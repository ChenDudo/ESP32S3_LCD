#pragma once

#include <Arduino.h>

// 板载扩展外设驱动（全部自带实现，不引第三方库）
//   AHT20      温湿度   I2C 0x38
//   BMP280     气压+温度 I2C 0x76（GY-BMP280 模块）
//   ATGM336H   定位      UART1 9600 8N1
// 两个 I2C 器件与 GT911 触摸共用一条总线（I2C_NUM_0 / IO41 / IO42）。

namespace sensors {

constexpr uint8_t AHT20_ADDR = 0x38;
constexpr uint8_t BMP280_ADDR = 0x76;  // GY-BMP280 默认 0x76；SDO 拉高则 0x77
constexpr uint8_t TMP117_ADDR = 0x48;  // ADD0 接 GND；外接探头，与上面两个不冲突

struct Environment {
  bool aht20Ok = false;
  bool bmp280Ok = false;
  bool tmp117Ok = false;
  float temperature = 0.0f;  // ℃，优先取外接 TMP117，其次 AHT20
  float humidity = 0.0f;     // %RH
  float pressure = 0.0f;     // hPa
  float bmpTemperature = 0.0f;
  float tmp117Temperature = 0.0f;
};

struct GpsFix {
  bool timeValid = false;
  bool locationValid = false;  // 已定位
  uint8_t satellites = 0;
  double latitude = 0.0;
  double longitude = 0.0;
  float altitude = 0.0f;     // m
  float speedKph = 0.0f;
  uint8_t hour = 0, minute = 0, second = 0;
  uint8_t day = 0, month = 0;
  uint16_t year = 0;
  uint32_t lastSentenceMs = 0;  // 最近一次收到有效句子的时刻
  uint32_t sentenceCount = 0;
};

// 初始化 I2C 总线（与触摸共用）与 GPS 串口；可重复调用
void begin();
void gpsBegin();

bool readEnvironment(Environment &env);

// 排空串口缓冲并解析 NMEA；返回 true 表示本次有新数据更新
bool gpsPoll(GpsFix &fix);

}  // namespace sensors
