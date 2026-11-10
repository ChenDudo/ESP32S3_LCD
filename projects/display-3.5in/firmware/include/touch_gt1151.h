#pragma once

#include <LovyanGFX.hpp>

// GT1151Q 电容触摸驱动（为正点原子 ATK-MD0350 3.5" 电容屏编写，实测产品 ID "1158"）
//
// 为什么不直接用 lgfx::Touch_GT911 —— 三个硬性差异，任何一个都会导致读不到或读错：
//
//   1) 寄存器布局不同。GT1151Q 每个触点 8 字节，从 0x8150 起依次是
//      x_low, x_high, y_low, y_high, sizeW, sizeH, reserved, track_id
//      而 GT911 驱动把 0x8150 当成 track_id、从 0x8151 取 x，坐标会整体错开一个字节。
//
//   2) INT 依赖不同。GT911 驱动的 getTouchRaw 只在 INT 为低时才去读寄存器；
//      本屏 INT 接在 IO46（ESP32-S3 的输入专用脚），没焊外部上拉时永远读不到。
//      这里改成纯轮询，INT 只用于上电时的地址选择。
//
//   3) 状态位清除不同。0x814E 的 bit7 置位后必须无条件写 0，否则芯片认为主机没读完，
//      不会再有下一次上报。GT911 驱动只在有触点时才写 0。
//
// 坐标：getTouchRaw 返回触摸面板的原始坐标（竖屏 320x480），
//       旋转与镜像由 Panel_Device::convertRawXY 依据 setRotation() 自动完成。

struct GtDiag {
  char product_id[8];
  uint8_t addr;
  bool ok;
};

// C++11 兼容的“全局单例”：inline 函数内的 static 变量在所有 TU 中共用一份
inline GtDiag &gtDiag(void) {
  static GtDiag d = {{0}, 0, false};
  return d;
}

class Touch_GT1151 : public lgfx::ITouch {
 public:
  bool init(void) override {
    if (_inited) return true;
    if (isSPI()) return false;  // 本屏触摸是 I2C

    // 先给 INT 上拉：GT1151Q 手册要求 INT 必须上拉，且复位释放瞬间 INT 的电平
    // 决定 I2C 地址（上拉 → 0x14，拉低 → 0x5D）。
    if (_cfg.pin_int >= 0) {
      lgfx::pinMode(_cfg.pin_int, lgfx::pin_mode_t::input_pullup);
    }

    // 硬复位：手册 4.2 节，RST 低 5~20ms，释放后再等足够时间让固件完成自校准
    if (_cfg.pin_rst >= 0) {
      lgfx::pinMode(_cfg.pin_rst, lgfx::pin_mode_t::output);
      lgfx::gpio_hi(_cfg.pin_rst);
      lgfx::delay(5);
      lgfx::gpio_lo(_cfg.pin_rst);
      lgfx::delay(15);
      lgfx::gpio_hi(_cfg.pin_rst);
      lgfx::delay(120);
    }

    if (!lgfx::i2c::init(_cfg.i2c_port, _cfg.pin_sda, _cfg.pin_scl).has_value()) {
      gtDiag().ok = false;
      return false;
    }

    // 探测地址：0x14（INT 上拉）优先，再试 0x5D（INT 被拉低时）。
    // 必须用产品 ID 校验，否则总线上偶发的假 ACK 会被误认成芯片。
    static constexpr uint8_t cand[2] = {0x14, 0x5D};
    for (uint8_t a : cand) {
      char id[8] = {0};
      if (!readProductId(a, id)) continue;

      _cfg.i2c_addr = a;
      writeReg(a, 0x814E, 0x00);  // 清掉复位后可能残留的状态位

      GtDiag &d = gtDiag();
      d.addr = a;
      d.ok = true;
      for (int i = 0; i < 7; ++i) d.product_id[i] = id[i];
      d.product_id[7] = '\0';

      _inited = true;
      return true;
    }

    gtDiag().ok = false;
    return false;
  }

  void wakeup(void) override {
    if (_inited) writeReg(_cfg.i2c_addr, 0x8040, 0x00);  // Command：Normal
  }

  void sleep(void) override {
    if (_inited) writeReg(_cfg.i2c_addr, 0x8040, 0x05);  // Command：Sleep
  }

  uint_fast8_t getTouchRaw(lgfx::touch_point_t *tp, uint_fast8_t count) override {
    if (!_inited || count == 0) return 0;
    if (count > 5) count = 5;

    uint8_t status = 0;
    if (!readReg(_cfg.i2c_addr, 0x814E, &status, 1)) return 0;
    if (!(status & 0x80)) return 0;  // bit7 未置位 = 没有新数据

    uint_fast8_t points = status & 0x0F;
    if (points > count) points = count;

    uint8_t buf[8 * 5] = {0};
    bool ok = true;
    if (points) ok = readReg(_cfg.i2c_addr, 0x8150, buf, points * 8);

    // 无论有没有触点都要清，否则芯片不再产生新的上报
    writeReg(_cfg.i2c_addr, 0x814E, 0x00);

    if (!ok) return 0;

    for (uint_fast8_t i = 0; i < points; ++i) {
      const uint8_t *p = &buf[i * 8];
      tp[i].x = static_cast<int16_t>(p[0] | (p[1] << 8));
      tp[i].y = static_cast<int16_t>(p[2] | (p[3] << 8));
      tp[i].size = static_cast<uint16_t>(p[4] + p[5]);
      tp[i].id = static_cast<uint16_t>(i);
    }
    return points;
  }

 private:
  bool readReg(uint8_t addr, uint16_t reg, uint8_t *buf, size_t len) {
    const uint8_t a[2] = {static_cast<uint8_t>(reg >> 8), static_cast<uint8_t>(reg & 0xFF)};
    return lgfx::i2c::transactionWriteRead(_cfg.i2c_port, addr, a, 2, buf, len, _cfg.freq)
        .has_value();
  }

  bool writeReg(uint8_t addr, uint16_t reg, uint8_t value) {
    const uint8_t a[3] = {static_cast<uint8_t>(reg >> 8), static_cast<uint8_t>(reg & 0xFF),
                          value};
    return lgfx::i2c::transactionWrite(_cfg.i2c_port, addr, a, 3, _cfg.freq).has_value();
  }

  // 产品 ID 在 0x8140，4 字节 ASCII（本屏是 "1158"）。非可打印字符一律判为探测失败。
  bool readProductId(uint8_t addr, char *out) {
    uint8_t buf[4] = {0};
    if (!readReg(addr, 0x8140, buf, 4)) return false;
    for (int i = 0; i < 4; ++i) {
      if (buf[i] < 0x20 || buf[i] > 0x7E) return false;
      out[i] = static_cast<char>(buf[i]);
    }
    out[4] = '\0';
    return true;
  }
};
