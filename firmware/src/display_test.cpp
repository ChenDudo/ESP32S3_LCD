#include <Arduino.h>

#include "lcd_panel.h"
#include "app_config.h"
#include "rgb_led.h"

#if APP_DISPLAY_TEST

// 整屏色偏检查固件
//   全屏铺满单色，用来判断：
//     - 有没有色偏（尤其白 / 灰页，肉眼最容易看出偏红、偏蓝、偏绿）
//     - 有没有坏点、坏线、暗角、亮度不均
//     - 边缘是否压边（纯色页没有边框，四边直接顶到玻璃边）
//
// 操作：
//   左滑 → 下一色      右滑 → 上一色      轻点 → 显示/隐藏当前页名称
//
// 日志同时输出两个串口：
//   Serial  = 原生 USB（IO19/20）
//   Serial0 = UART0（IO43/44，板载 USB-UART 桥，即常见的 COM 口）

Lcd lcd;

struct ColorPage {
  uint16_t color;
  const char *name;
  bool dark;  // true = 深色底，标签用白字
};

// 顺序按检查习惯排：先三原色，再白/灰（看色偏），最后混合色（看串色）
static const ColorPage kPages[] = {
    {TFT_RED, "RED", false},
    {TFT_GREEN, "GREEN", false},
    {TFT_BLUE, "BLUE", true},      // 蓝底黑字看不清，用白字
    {TFT_WHITE, "WHITE", false},   // 白底必须黑字，否则标签等于隐身
    {TFT_BLACK, "BLACK", true},
    {0x8410, "GRAY 50%", false},   // 128,128,128
    {0x4208, "GRAY 25%", true},    // 64,64,64
    {TFT_CYAN, "CYAN", false},
    {TFT_MAGENTA, "MAGENTA", false},
    {TFT_YELLOW, "YELLOW", false},
};
static constexpr int kPageCount = sizeof(kPages) / sizeof(kPages[0]);

static int pageIndex = 0;
static bool labelVisible = false;
static uint32_t labelUntil = 0;

// ---- 日志 ----
void logf(const char *fmt, ...) {
  char buf[160];
  va_list ap;
  va_start(ap, fmt);
  vsnprintf(buf, sizeof(buf), fmt, ap);
  va_end(ap);
  Serial.print(buf);
  Serial0.print(buf);
}

// ---- 页码标签（只占左下角一小块，1.5 秒后自动擦掉，不干扰看色） ----
static constexpr int kLabelH = 26;

void drawLabel() {
  const ColorPage &p = kPages[pageIndex];
  const uint16_t fg = p.dark ? TFT_WHITE : TFT_BLACK;

  char text[28];
  snprintf(text, sizeof(text), "%s  %d/%d", p.name, pageIndex + 1, kPageCount);

  lcd.setTextDatum(bottom_left);
  lcd.setTextColor(fg, p.color);
  lcd.setTextSize(1);
  lcd.drawString(text, 8, lcd.height() - 6, &fonts::Font2);
  lcd.setTextDatum(top_left);
  labelVisible = true;
  labelUntil = millis() + 1500;
}

void eraseLabel() {
  const ColorPage &p = kPages[pageIndex];
  lcd.fillRect(0, lcd.height() - kLabelH, lcd.width(), kLabelH, p.color);
  labelVisible = false;
}

void showPage(int index) {
  pageIndex = (index % kPageCount + kPageCount) % kPageCount;
  const ColorPage &p = kPages[pageIndex];
  lcd.fillScreen(p.color);   // 整屏铺满，四边不留边框
  drawLabel();
  logf("page %d/%d: %s\n", pageIndex + 1, kPageCount, p.name);
}

void setup() {
  Serial.begin(115200);   // 原生 USB
  Serial0.begin(115200);  // UART0 → 板载 USB-UART
  delay(400);

  logf("\n=== ATK-MD0350 3.5in colour uniformity test ===\n");

  rgbLedOff();  // 关掉核心板板载 WS2812

  pinMode(board_pins::LCD_RD, OUTPUT);
  digitalWrite(board_pins::LCD_RD, HIGH);

  pinMode(board_pins::LCD_BL, OUTPUT);
  digitalWrite(board_pins::LCD_BL, LOW);

  logf("lcd.init() ...\n");
  lcd.init();          // 顺带完成触摸初始化（INT 上拉 + 硬复位 + 地址探测）
  lcd.setRotation(1);  // 320x480 竖屏 → 480x320 横屏

  digitalWrite(board_pins::LCD_BL, HIGH);
  logf("LCD size: %d x %d   invert=%d rgb_order=%d\n",
       lcd.width(), lcd.height(), LCD_INVERT, LCD_RGB_ORDER);

  if (gtDiag().ok) {
    logf("GT1151Q ready at 0x%02X, product id \"%s\"\n", gtDiag().addr,
         gtDiag().product_id);
  } else {
    logf("GT1151Q NOT FOUND - 只能看颜色，不能翻页\n");
    logf("  -> 检查 J2-6(SDA/IO42) J2-7(SCL/IO41) J2-17(INT/IO46) J2-16(RST/IO47)\n");
  }

  logf("Swipe LEFT/RIGHT to change colour, tap to toggle the label.\n");

  showPage(0);
}

void loop() {
  static uint32_t lastPoll = 0;
  static bool touching = false;
  static uint16_t startX = 0, startY = 0, lastX = 0, lastY = 0;
  static uint32_t startMs = 0;

  if (labelVisible && millis() > labelUntil) {
    eraseLabel();
  }

  if (millis() - lastPoll < 15) {
    delay(1);
    return;
  }
  lastPoll = millis();

  uint16_t x = 0;
  uint16_t y = 0;
  const bool pressed = lcd.getTouch(&x, &y);

  if (pressed) {
    if (!touching) {  // 按下瞬间
      touching = true;
      startX = lastX = x;
      startY = lastY = y;
      startMs = millis();
    } else {
      lastX = x;
      lastY = y;
    }
    return;
  }

  if (!touching) return;  // 一直没按过

  // 松开：判定是滑动还是轻点
  touching = false;

  const int dx = static_cast<int>(lastX) - static_cast<int>(startX);
  const int dy = static_cast<int>(lastY) - static_cast<int>(startY);
  const uint32_t held = millis() - startMs;

  if (abs(dx) >= 60 && abs(dx) > abs(dy) * 3 / 2) {
    if (dx < 0) {
      showPage(pageIndex + 1);  // 左滑 → 下一色
    } else {
      showPage(pageIndex - 1);  // 右滑 → 上一色
    }
    return;
  }

  if (held < 400 && abs(dx) < 15 && abs(dy) < 15) {  // 轻点：显示/隐藏标签
    if (labelVisible) {
      eraseLabel();
    } else {
      drawLabel();
      labelUntil = millis() + 3000;
    }
  }
}

#endif  // APP_DISPLAY_TEST
