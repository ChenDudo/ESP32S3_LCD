#include "sensors.h"

#define LGFX_USE_V1
#include <LovyanGFX.hpp>

#include "board_pins.h"
#include "app_config.h"

namespace sensors {
namespace {

constexpr uint32_t I2C_FREQ = APP_I2C_FREQ;
constexpr int I2C_PORT = 0;  // 与 GT911 触摸同一个端口

HardwareSerial gpsSerial(1);

GpsFix sFix;

bool gBusReady = false;

bool busReady() {
  if (!gBusReady) {
    gBusReady = lgfx::i2c::init(I2C_PORT, board_pins::I2C_SDA, board_pins::I2C_SCL).has_value();
  }
  return gBusReady;
}

bool i2cWrite(uint8_t addr, const uint8_t *data, size_t len) {
  return busReady() &&
         lgfx::i2c::transactionWrite(I2C_PORT, addr, data, (uint8_t)len, I2C_FREQ).has_value();
}

bool i2cRead(uint8_t addr, uint8_t *data, size_t len) {
  return busReady() &&
         lgfx::i2c::transactionRead(I2C_PORT, addr, data, (uint8_t)len, I2C_FREQ).has_value();
}

bool i2cWriteRead(uint8_t addr, const uint8_t *w, uint8_t wlen, uint8_t *r, size_t rlen) {
  return busReady() &&
         lgfx::i2c::transactionWriteRead(I2C_PORT, addr, w, wlen, r, rlen, I2C_FREQ).has_value();
}

bool readReg(uint8_t addr, uint8_t reg, uint8_t *data, size_t len) {
  return i2cWriteRead(addr, &reg, 1, data, len);
}

// ---------------- AHT20 ----------------

bool aht20Probed = false;
bool aht20Present = false;

bool aht20Init() {
  const uint8_t cmd[3] = {0xBE, 0x08, 0x00};  // 标定/初始化命令
  if (!i2cWrite(AHT20_ADDR, cmd, 3)) return false;
  delay(10);
  uint8_t status = 0;
  if (!i2cRead(AHT20_ADDR, &status, 1)) return false;
  return (status & 0x08) != 0;  // bit3 = 已标定
}

bool aht20Read(float &temperature, float &humidity) {
  const uint8_t cmd[3] = {0xAC, 0x33, 0x00};  // 触发测量
  if (!i2cWrite(AHT20_ADDR, cmd, 3)) return false;
  delay(80);

  uint8_t b[6];
  if (!i2cRead(AHT20_ADDR, b, 6)) return false;
  if (b[0] & 0x80) return false;  // 忙

  const uint32_t rawH = ((uint32_t)b[1] << 12) | ((uint32_t)b[2] << 4) | (b[3] >> 4);
  const uint32_t rawT = (((uint32_t)b[3] & 0x0F) << 16) | ((uint32_t)b[4] << 8) | b[5];

  humidity = rawH * 100.0f / 1048576.0f;
  temperature = rawT * 200.0f / 1048576.0f - 50.0f;
  return true;
}

// ---------------- BMP280 ----------------

struct BmpCalib {
  uint16_t T1;
  int16_t T2, T3;
  uint16_t P1;
  int16_t P2, P3, P4, P5, P6, P7, P8, P9;
};

BmpCalib cal;
bool bmpProbed = false;
bool bmpPresent = false;

int16_t le16s(const uint8_t *p) { return (int16_t)((uint16_t)p[0] | ((uint16_t)p[1] << 8)); }
uint16_t le16u(const uint8_t *p) { return (uint16_t)((uint16_t)p[0] | ((uint16_t)p[1] << 8)); }

bool bmp280Init() {
  uint8_t id = 0;
  if (!readReg(BMP280_ADDR, 0xD0, &id, 1) || id != 0x58) return false;

  uint8_t c[24];
  if (!readReg(BMP280_ADDR, 0x88, c, 24)) return false;

  cal.T1 = le16u(c + 0);
  cal.T2 = le16s(c + 2);
  cal.T3 = le16s(c + 4);
  cal.P1 = le16u(c + 6);
  cal.P2 = le16s(c + 8);
  cal.P3 = le16s(c + 10);
  cal.P4 = le16s(c + 12);
  cal.P5 = le16s(c + 14);
  cal.P6 = le16s(c + 16);
  cal.P7 = le16s(c + 18);
  cal.P8 = le16s(c + 20);
  cal.P9 = le16s(c + 22);

  // 0xF5: t_sb=500ms, filter=x16；0xF4: osrs_t=x2, osrs_p=x16, normal mode
  const uint8_t cfg[2] = {0xF5, 0x90};
  if (!i2cWrite(BMP280_ADDR, cfg, 2)) return false;
  const uint8_t ctrl[2] = {0xF4, 0x57};
  if (!i2cWrite(BMP280_ADDR, ctrl, 2)) return false;
  delay(50);
  return true;
}

float bmpCompensateTemp(int32_t adcT, int32_t &tFine) {
  const float v1 = ((float)adcT / 16384.0f - (float)cal.T1 / 1024.0f) * (float)cal.T2;
  float v2 = (float)adcT / 131072.0f - (float)cal.T1 / 8192.0f;
  v2 = v2 * v2 * (float)cal.T3;
  tFine = (int32_t)(v1 + v2);
  return (v1 + v2) / 5120.0f;
}

float bmpCompensatePress(int32_t adcP, int32_t tFine) {
  float v1 = (float)tFine / 2.0f - 64000.0f;
  float v2 = v1 * v1 * (float)cal.P6 / 32768.0f;
  v2 = v2 + v1 * (float)cal.P5 * 2.0f;
  v2 = v2 / 4.0f + (float)cal.P4 * 65536.0f;
  v1 = ((float)cal.P3 * v1 * v1 / 524288.0f + (float)cal.P2 * v1) / 524288.0f;
  v1 = (1.0f + v1 / 32768.0f) * (float)cal.P1;
  if (v1 == 0.0f) return 0.0f;

  float p = 1048576.0f - (float)adcP;
  p = (p - v2 / 4096.0f) * 6250.0f / v1;
  v1 = (float)cal.P9 * p * p / 2147483648.0f;
  v2 = p * (float)cal.P8 / 32768.0f;
  return p + (v1 + v2 + (float)cal.P7) / 16.0f;  // Pa
}

bool bmp280Read(float &temperature, float &pressureHpa) {
  uint8_t d[6];
  if (!readReg(BMP280_ADDR, 0xF7, d, 6)) return false;

  const int32_t adcP = ((int32_t)d[0] << 12) | ((int32_t)d[1] << 4) | (d[2] >> 4);
  const int32_t adcT = ((int32_t)d[3] << 12) | ((int32_t)d[4] << 4) | (d[5] >> 4);

  int32_t tFine = 0;
  temperature = bmpCompensateTemp(adcT, tFine);
  pressureHpa = bmpCompensatePress(adcP, tFine) / 100.0f;
  return true;
}

// ---------------- ATGM336H (NMEA 0183) ----------------

char line[100];
uint8_t lineLen = 0;

int splitFields(char *s, char **out, int maxOut) {
  int n = 0;
  out[n++] = s;
  for (char *p = s; *p && n < maxOut; ++p) {
    if (*p == ',') {
      *p = '\0';
      out[n++] = p + 1;
    }
  }
  return n;
}

bool parseCoord(const char *value, const char *hemi, double &deg) {
  if (!value || !*value) return false;
  const double raw = atof(value);
  const int d = (int)(raw / 100.0);
  const double minutes = raw - d * 100.0;
  deg = d + minutes / 60.0;
  if (hemi && (*hemi == 'S' || hemi[0] == 'W')) deg = -deg;
  return true;
}

void parseSentence(char *sentence) {
  if (sentence[0] != '$') return;

  char *f[24];
  const int n = splitFields(sentence, f, 24);
  if (n < 3) return;

  const char *type = f[0] + 3;  // 跳过 "$GN" / "$GP"

  if (strncmp(type, "RMC", 3) == 0 && n > 9) {
    const bool active = (f[2][0] == 'A');
    if (active) {
      parseCoord(f[3], f[4], sFix.latitude);
      parseCoord(f[5], f[6], sFix.longitude);
      sFix.locationValid = true;
    } else {
      sFix.locationValid = false;
    }
    if (*f[7]) sFix.speedKph = (float)atof(f[7]) * 1.852f;

    // hhmmss.ss
    if (strlen(f[1]) >= 6) {
      sFix.hour = (f[1][0] - '0') * 10 + (f[1][1] - '0');
      sFix.minute = (f[1][2] - '0') * 10 + (f[1][3] - '0');
      sFix.second = (f[1][4] - '0') * 10 + (f[1][5] - '0');
      sFix.timeValid = true;
    }
    // ddmmyy
    if (strlen(f[9]) >= 6) {
      sFix.day = (f[9][0] - '0') * 10 + (f[9][1] - '0');
      sFix.month = (f[9][2] - '0') * 10 + (f[9][3] - '0');
      sFix.year = 2000 + (f[9][4] - '0') * 10 + (f[9][5] - '0');
    }
    sFix.sentenceCount++;
    sFix.lastSentenceMs = millis();
  } else if (strncmp(type, "GGA", 3) == 0 && n > 9) {
    sFix.satellites = (uint8_t)atoi(f[7]);
    if (*f[9]) sFix.altitude = (float)atof(f[9]);
    if (*f[6] && f[6][0] != '0') {
      parseCoord(f[2], f[3], sFix.latitude);
      parseCoord(f[4], f[5], sFix.longitude);
      sFix.locationValid = true;
    }
    sFix.sentenceCount++;
    sFix.lastSentenceMs = millis();
  }
}

}  // namespace

void begin() { busReady(); }

void gpsBegin() {
  gpsSerial.begin(9600, SERIAL_8N1, board_pins::GPS_RX, board_pins::GPS_TX);
  lineLen = 0;
}

bool readEnvironment(Environment &env) {
  if (!aht20Probed) {
    aht20Probed = true;
    aht20Present = aht20Init();
  }
  if (aht20Present) {
    float t = 0.0f, h = 0.0f;
    if (aht20Read(t, h)) {
      env.temperature = t;
      env.humidity = h;
      env.aht20Ok = true;
    }
  }

  if (!bmpProbed) {
    bmpProbed = true;
    bmpPresent = bmp280Init();
  }
  if (bmpPresent) {
    float t = 0.0f, p = 0.0f;
    if (bmp280Read(t, p)) {
      env.bmpTemperature = t;
      env.pressure = p;
      env.bmp280Ok = true;
    }
  }

  return env.aht20Ok || env.bmp280Ok;
}

bool gpsPoll(GpsFix &fix) {
  bool updated = false;
  while (gpsSerial.available() > 0) {
    const char c = (char)gpsSerial.read();
    if (c == '\n') {
      line[lineLen] = '\0';
      if (lineLen > 6) {
        parseSentence(line);
        updated = true;
      }
      lineLen = 0;
    } else if (c != '\r') {
      if (lineLen < sizeof(line) - 1) {
        line[lineLen++] = c;
      } else {
        lineLen = 0;  // 超长，丢弃这一行
      }
    }
  }
  if (updated) fix = sFix;
  return updated;
}

}  // namespace sensors
