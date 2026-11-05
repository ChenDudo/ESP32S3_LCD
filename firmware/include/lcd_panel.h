#pragma once

#define LGFX_USE_V1
#include <LovyanGFX.hpp>

#include "board_pins.h"
#include "app_config.h"
#include "touch_gt1151.h"

// ATK-MD0350 3.5" 480x320 电容屏的 LGFX 设备定义（显示 + 触摸）
// 说明：
//   显示  ST7796U / NT35310，8080 16 位并口 → ESP32-S3 LCD_CAM i80
//   触摸  GT9 系列电容触摸，I2C（不是 SPI）
//   若屏实际是 NT35310 且 ST7796 不显示，把 PanelType 换成 lgfx::Panel_ILI9488

using PanelType = lgfx::Panel_ST7796;

class Lcd : public lgfx::LGFX_Device {
 public:
  Lcd() {
    {
      auto cfg = bus_.config();
      cfg.freq_write = 20000000;  // 20MHz 起步；PCB 走线短可试 40000000
      cfg.freq_read = 16000000;
      cfg.pin_wr = board_pins::LCD_WR;
      cfg.pin_rd = -1;  // 底板已把 RD 10K 上拉，只写模式
      cfg.pin_rs = board_pins::LCD_RS;
      cfg.pin_d0 = board_pins::LCD_D0;
      cfg.pin_d1 = board_pins::LCD_D1;
      cfg.pin_d2 = board_pins::LCD_D2;
      cfg.pin_d3 = board_pins::LCD_D3;
      cfg.pin_d4 = board_pins::LCD_D4;
      cfg.pin_d5 = board_pins::LCD_D5;
      cfg.pin_d6 = board_pins::LCD_D6;
      cfg.pin_d7 = board_pins::LCD_D7;
      cfg.pin_d8 = board_pins::LCD_D8;
      cfg.pin_d9 = board_pins::LCD_D9;
      cfg.pin_d10 = board_pins::LCD_D10;
      cfg.pin_d11 = board_pins::LCD_D11;
      cfg.pin_d12 = board_pins::LCD_D12;
      cfg.pin_d13 = board_pins::LCD_D13;
      cfg.pin_d14 = board_pins::LCD_D14;
      cfg.pin_d15 = board_pins::LCD_D15;
      bus_.config(cfg);
      panel_.setBus(&bus_);
    }

    {
      auto cfg = panel_.config();
      cfg.pin_cs = board_pins::LCD_CS;
      cfg.pin_rst = board_pins::LCD_RST;
      cfg.pin_busy = -1;
      cfg.memory_width = 320;
      cfg.memory_height = 480;
      cfg.panel_width = 320;
      cfg.panel_height = 480;
      cfg.offset_x = 0;
      cfg.offset_y = 0;
      cfg.offset_rotation = 0;
      cfg.readable = false;
      cfg.invert = LCD_INVERT;        // 实测这块 IPS 屏需要 INVON，否则白黑互换
      cfg.rgb_order = LCD_RGB_ORDER;  // 红蓝互换开关（见 app_config.h 的说明）
      cfg.dlen_16bit = true;
      cfg.bus_shared = false;
      panel_.config(cfg);
    }

    {
      auto cfg = touch_.config();
      cfg.i2c_port = 0;  // I2C_NUM_0，与 AHT20 / BMP280 共用
      cfg.pin_sda = board_pins::TP_SDA;
      cfg.pin_scl = board_pins::TP_SCL;
      cfg.i2c_addr = 0x14;  // 实测本屏 GT1151Q 在 0x14（INT 上拉时）；驱动会再试 0x5D
      // INT 只用来在复位时选地址 + 上拉，读坐标靠轮询（见 touch_gt1151.h 的说明）。
      // 注意 IO46 是 ESP32-S3 的输入专用脚，只能开内部上拉（约 45k），
      // 建议底板按设计手册补一颗 10K 外部上拉到 3V3。
      cfg.pin_int = board_pins::TP_INT;
      cfg.pin_rst = board_pins::TP_RST;
      cfg.freq = APP_I2C_FREQ;
      cfg.x_min = 0;
      cfg.x_max = 319;
      cfg.y_min = 0;
      cfg.y_max = 479;
      cfg.offset_rotation = 0;  // 面板坐标即竖屏 320x480，旋转交给 convertRawXY
      cfg.bus_shared = false;
      touch_.config(cfg);
      panel_.setTouch(&touch_);
    }

    setPanel(&panel_);
  }

 private:
  lgfx::Bus_Parallel16 bus_;
  PanelType panel_;
  Touch_GT1151 touch_;
};
