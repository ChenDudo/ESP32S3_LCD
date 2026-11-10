#include <Arduino.h>

#include "lcd_panel.h"
#include "sensors.h"
#include "rgb_led.h"
#include "app_config.h"

#if !APP_DISPLAY_TEST

// 正点原子 ATK-MD0350 3.5" 480x320 电容触摸屏（V2.4，旧资料）
//   显示：ST7796U / NT35310，Intel 8080 16 位并口 → ESP32-S3 LCD_CAM i80
//   触摸：GT9 系列电容触摸，I2C（不是 SPI）
//
// 底板扩展（未接外设时可用 display_test 环境单独点屏）：
//   AHT20 温湿度（I2C 0x38）与 GY-BMP280 气压（I2C 0x76）挂在触摸同一条 I2C 上（J4）
//   ATGM336H-5N31 GNSS 走 UART1（IO44 收 / IO43 发），即原 J3 调试口

Lcd lcd;


sensors::Environment env;
sensors::GpsFix gps;

// ---------------- 配色 ----------------
constexpr uint16_t C_BG = 0x0000;
static inline uint16_t cardBg() { return lcd.color565(24, 30, 42); }
static inline uint16_t cardEdge() { return lcd.color565(58, 70, 90); }
static inline uint16_t labelColor() { return lcd.color565(132, 148, 174); }
static inline uint16_t valueColor() { return lcd.color565(236, 242, 255); }
static inline uint16_t accent() { return lcd.color565(64, 196, 160); }
static inline uint16_t warnColor() { return lcd.color565(230, 120, 90); }

// ---------------- 布局 ----------------
constexpr int HEADER_H = 48;
constexpr int CARD_Y = 56;
constexpr int CARD_H = 108;
constexpr int CARD_W = 148;
constexpr int CARD_X[3] = {10, 166, 322};
constexpr int GPS_Y = 172;
constexpr int GPS_H = 110;
constexpr int GPS_X = 10;
constexpr int GPS_W = 460;
constexpr int STATUS_Y = 300;

void drawCardFrame(int x, int y, int w, int h, const char *title) {
  lcd.fillRoundRect(x, y, w, h, 10, cardBg());
  lcd.drawRoundRect(x, y, w, h, 10, cardEdge());
  lcd.setTextDatum(top_left);
  lcd.setTextSize(1);
  lcd.setTextColor(labelColor());
  lcd.drawString(title, x + 12, y + 10, &fonts::Font2);
}

void drawEnvValues() {
  char t[12], h[12], p[12];
  if (env.aht20Ok) {
    snprintf(t, sizeof(t), "%.1f", env.temperature);
    snprintf(h, sizeof(h), "%.1f", env.humidity);
  } else {
    snprintf(t, sizeof(t), "--");
    snprintf(h, sizeof(h), "--");
  }
  if (env.bmp280Ok) {
    snprintf(p, sizeof(p), "%.1f", env.pressure);
  } else {
    snprintf(p, sizeof(p), "--");
  }

  const char *values[3] = {t, h, p};
  const char *units[3] = {"C", "%RH", "hPa"};
  const bool ok[3] = {env.aht20Ok, env.aht20Ok, env.bmp280Ok};

  for (int i = 0; i < 3; ++i) {
    const int x = CARD_X[i];
    // 只清数值区域，避免整屏重绘导致闪烁
    lcd.fillRect(x + 2, CARD_Y + 32, CARD_W - 4, CARD_H - 36, cardBg());

    lcd.setTextDatum(top_left);
    lcd.setTextSize(2);
    lcd.setTextColor(ok[i] ? valueColor() : warnColor());
    lcd.drawString(values[i], x + 12, CARD_Y + 38, &fonts::Font4);

    lcd.setTextSize(1);
    lcd.setTextColor(labelColor());
    lcd.drawString(units[i], x + 14, CARD_Y + 76, &fonts::Font2);
  }
}

void drawGpsValues() {
  const int x = GPS_X + 12;
  lcd.fillRect(GPS_X + 2, GPS_Y + 28, GPS_W - 4, GPS_H - 32, cardBg());
  lcd.setTextDatum(top_left);
  lcd.setTextSize(1);

  char line1[56];
  char line2[56];
  char line3[56];

  if (gps.sentenceCount == 0) {
    snprintf(line1, sizeof(line1), "Waiting for NMEA data ...");
    snprintf(line2, sizeof(line2), "Check J3 wiring, 9600 8N1");
    line3[0] = '\0';
  } else if (gps.locationValid) {
    snprintf(line1, sizeof(line1), "FIX  sats:%02u  alt:%.0fm  spd:%.1fkm/h",
             gps.satellites, gps.altitude, gps.speedKph);
    snprintf(line2, sizeof(line2), "LAT %.6f", gps.latitude);
    snprintf(line3, sizeof(line3), "LON %.6f", gps.longitude);
  } else {
    snprintf(line1, sizeof(line1), "No fix yet   sats:%02u", gps.satellites);
    snprintf(line2, sizeof(line2), "Cold start needs 30~40s outdoors");
    line3[0] = '\0';
  }

  lcd.setTextColor(gps.locationValid ? accent() : warnColor());
  lcd.drawString(line1, x, GPS_Y + 30, &fonts::Font2);
  lcd.setTextColor(valueColor());
  lcd.drawString(line2, x, GPS_Y + 54, &fonts::Font2);
  if (line3[0]) lcd.drawString(line3, x, GPS_Y + 78, &fonts::Font2);

  // 右上角 UTC 时间
  char clock[16] = "--:--:--";
  if (gps.timeValid) {
    snprintf(clock, sizeof(clock), "%02u:%02u:%02u", gps.hour, gps.minute, gps.second);
  }
  lcd.setTextDatum(top_right);
  lcd.setTextColor(valueColor());
  lcd.drawString(clock, GPS_X + GPS_W - 12, GPS_Y + 10, &fonts::Font2);
  lcd.setTextDatum(top_left);
}

void drawStatusLine(const char *text, uint16_t color) {
  lcd.fillRect(0, STATUS_Y, lcd.width(), lcd.height() - STATUS_Y,
               lcd.color565(28, 28, 28));
  lcd.setTextDatum(top_left);
  lcd.setTextColor(color);
  lcd.setTextSize(1);
  lcd.drawString(text, 8, STATUS_Y + 6, &fonts::Font0);
}

void drawStaticScreen() {
  lcd.fillScreen(C_BG);

  lcd.fillRect(0, 0, lcd.width(), HEADER_H, lcd.color565(22, 58, 105));
  lcd.setTextDatum(top_left);
  lcd.setTextColor(TFT_WHITE);
  lcd.setTextSize(2);
  lcd.drawString("ESP32-S3 N16R8", 12, 10, &fonts::Font2);

  lcd.setTextDatum(top_right);
  lcd.setTextSize(1);
  lcd.setTextColor(lcd.color565(170, 205, 245));
  lcd.drawString("ATK-MD0350 3.5in 480x320", lcd.width() - 12, 16, &fonts::Font2);
  lcd.setTextDatum(top_left);

  drawCardFrame(CARD_X[0], CARD_Y, CARD_W, CARD_H, "TEMP");
  drawCardFrame(CARD_X[1], CARD_Y, CARD_W, CARD_H, "HUMI");
  drawCardFrame(CARD_X[2], CARD_Y, CARD_W, CARD_H, "PRES");
  drawCardFrame(GPS_X, GPS_Y, GPS_W, GPS_H, "GNSS  ATGM336H");

  drawStatusLine("touch: waiting", TFT_LIGHTGREY);
}

void setup() {
  Serial.begin(115200);
  delay(300);
  Serial.println();
  Serial.println("ESP32-S3 N16R8 + ATK-MD0350 3.5in (ST7796 + GT1151Q) + AHT20/BMP280/GPS");

  rgbLedOff();  // 关掉核心板板载 WS2812

  pinMode(board_pins::LCD_RD, OUTPUT);
  digitalWrite(board_pins::LCD_RD, HIGH);

  pinMode(board_pins::LCD_BL, OUTPUT);
  digitalWrite(board_pins::LCD_BL, LOW);  // 先关，避免初始化时闪白屏

  lcd.init();
  lcd.setRotation(1);  // 320x480 竖屏 → 480x320 横屏
  digitalWrite(board_pins::LCD_BL, HIGH);

  sensors::begin();
  sensors::gpsBegin();

  drawStaticScreen();

  Serial.printf("LCD size: %d x %d\n", lcd.width(), lcd.height());
  Serial.printf("Flash: %u KB, PSRAM: %u KB\n", ESP.getFlashChipSize() / 1024,
                ESP.getPsramSize() / 1024);
  Serial.println("Demo ready.");
}

void loop() {
  static uint32_t lastEnvMs = 0;
  static uint32_t lastGpsDrawMs = 0;
  static bool gpsDirty = false;
  static uint16_t lastX = 0xFFFF;
  static uint16_t lastY = 0xFFFF;

  // GNSS：持续排空串口缓冲
  if (sensors::gpsPoll(gps)) {
    gpsDirty = true;
  }

  if (gpsDirty && millis() - lastGpsDrawMs > 500) {
    gpsDirty = false;
    lastGpsDrawMs = millis();
    drawGpsValues();
  }

  // 温湿度 / 气压：1 秒一次（AHT20 单次测量需要 80ms）
  if (millis() - lastEnvMs > 1000) {
    lastEnvMs = millis();
    sensors::readEnvironment(env);
    drawEnvValues();
    Serial.printf("T=%.1fC RH=%.1f%% P=%.1fhPa (aht:%d bmp:%d) gps:fix=%d sats=%u\n",
                  env.temperature, env.humidity, env.pressure, env.aht20Ok,
                  env.bmp280Ok, gps.locationValid, gps.satellites);
  }

  // 触摸
  uint16_t x = 0;
  uint16_t y = 0;
  if (!lcd.getTouch(&x, &y)) return;
  if (x == lastX && y == lastY) return;
  lastX = x;
  lastY = y;

  lcd.fillCircle(x, y, 4, TFT_ORANGE);

  char text[48];
  snprintf(text, sizeof(text), "touch: X=%u Y=%u", x, y);
  drawStatusLine(text, TFT_ORANGE);
}

#endif  // !APP_DISPLAY_TEST
