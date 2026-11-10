#include <Arduino.h>
#include <math.h>

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
//   上滑 → 调亮背光    下滑 → 调暗背光（按滑动距离连续调，右上角显示百分比）
//   长按屏幕中心 0.8 秒 → 进入高速刷屏 + 帧率统计，再长按一次退出
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

// 当前整屏底色。浮层每次重画 / 擦除都必须先用真实底色擦净，
// 否则透明背景字体叠加会留下上一次的数字（见 drawBrightnessOverlay 的注释）。
static uint16_t screenBg = TFT_BLACK;

// ---------- 背光 PWM 调光 ----------
// 模块 V2.4 的 BL_CTR 只是 Q1(S8050) 的基极开关（R21 1K），没有恒流芯片，
// 所以占空比 ≈ 平均亮度，IO40 用 LEDC 输出即可，底板不用改。
//
// 8kHz：1kHz 时人眼扫视有频闪重影(phantom array)、相机有滚动条纹，且
//       1000/60Hz 非整数倍会让每帧亮度缓慢漂移；8kHz 每帧约 133 个周期，
//       这些现象已基本消失。
//
// 【2026-11-06 实测回退】曾提到 20kHz，结果低亮度段几乎全黑。原因不是占空比
// 太小，而是 S8050 跟不上：基极只有 R21 1K、无加速电容，饱和后的关断存储
// 时间约 1~2us；20kHz/8bit 的 LSB 只有 0.2us、duty=12 也才 2.3us 高电平，
// 窄脉冲大部分被拖尾吃掉，实际光输出远低于理论值。低频开关管调光必须
// 留足「绝对高电平时间」，不能只盯着频率。
//
// 8kHz + 8bit => LSB 0.49us；kBlMinDuty 14 => 6.9us 高电平（约 5.5%），
// 既能可靠点亮，又是一个「看得清但确实很暗」的最低档；0% 仍是完全灭。
// 若低亮度仍偏暗 / 闪烁，把 kBlFreq 降到 4000（LSB 0.98us，14 => 13.7us）。
static constexpr uint8_t  kBlChannel = 0;
static constexpr uint8_t  kBlBits    = 8;
static constexpr uint32_t kBlFreq    = 8000;
static constexpr uint8_t  kBlMinDuty = 14;     // ≈5.5%，8kHz 下 6.9us 高电平
static uint8_t  brightness = 100;              // 0..100 %
static uint32_t blDuty     = 255;              // 当前实际写入的占空比，供日志查看
static bool     blVisible  = false;
static uint32_t blUntil    = 0;

void setBrightness(uint8_t percent) {
  brightness = static_cast<uint8_t>(constrain(static_cast<int>(percent), 0, 100));
  if (brightness == 0) {
    blDuty = 0;
  } else {
    const float g = powf(brightness / 100.0f, 2.2f);  // gamma 校正，视觉上才线性
    blDuty = kBlMinDuty + static_cast<uint32_t>(g * (255 - kBlMinDuty));
  }
  ledcWrite(kBlChannel, blDuty);
}

void blBegin(uint8_t percent) {
  ledcSetup(kBlChannel, kBlFreq, kBlBits);
  ledcAttachPin(board_pins::LCD_BL, kBlChannel);
  setBrightness(percent);
}

// 亮度提示：右上角浮字，1.5 秒后自动擦掉，不占条带、不留黑块。
//
// 重影根因：LovyanGFX 的 setTextColor(color) 单参数会把 fore/back 设成同色，
// 字体渲染据此判定 fillbg = false（透明背景，只画字形像素）。连续调亮度时
// "BL 100%" → "BL   9%" 的前导空格不画任何像素，旧数字笔画就留在原处，
// 叠几次便是重影；原先那层 1px 黑色偏移描边还会再叠一层。
// 修法：每次先按真实底色擦净整块区域，再用双参数 setTextColor(fg, bg)
// 不透明绘制（字符框整块填底色），并去掉偏移描边。
//
// 低亮度可读性（2026-11-06 补充）：背光调暗后页面底色本身已经很暗，
// 黑字 / 白字都会和背景糊在一起。这里给浮字固定「黑底 + 亮绿字」的高对比
// OSD 配色：绿光在低照度下人眼最敏感，且不受页面底色影响；黑底由不透明
// 背景自动生成、紧贴字宽，不留整块黑条。擦除时统一用 screenBg 恢复页面。
static constexpr int kBlBoxW = 130;
static constexpr int kBlBoxH = 26;

void drawBrightnessOverlay() {
  lcd.fillRect(lcd.width() - kBlBoxW, 0, kBlBoxW, kBlBoxH, screenBg);

  char text[16];
  snprintf(text, sizeof(text), "BL %3d%%", brightness);
  lcd.setTextDatum(top_right);
  lcd.setTextSize(1);
  lcd.setTextColor(TFT_GREEN, TFT_BLACK);  // 不透明：紧贴字宽的黑底 + 亮绿字
  lcd.drawString(text, lcd.width() - 8, 5, &fonts::Font2);
  lcd.setTextDatum(top_left);
  blVisible = true;
  blUntil = millis() + 1500;
}

void eraseBrightnessOverlay() {
  if (!blVisible) return;
  lcd.fillRect(lcd.width() - kBlBoxW, 0, kBlBoxW, kBlBoxH, screenBg);
  blVisible = false;
}

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
  lcd.fillScreen(p.color);   // 整屏铺满，四边不留边框（顺带擦掉亮度浮字）
  blVisible = false;
  screenBg = p.color;
  drawLabel();
  logf("page %d/%d: %s\n", pageIndex + 1, kPageCount, p.name);
}

// ---------- 高速刷屏 + 帧率统计 ----------
// 整屏按帧全量重绘一组动态图形，用来测 8080 并口的真实吞吐。
// FPS 以半透明感的浮层文字直接叠在画面上，不占专门的条带。
// 扫描线自上而下扫过，便于观察撕裂（tearing）和帧同步。

static bool fpsMode = false;
static uint32_t fpsFrames = 0;      // 本统计窗口内的帧数
static uint32_t fpsWindowMs = 0;    // 窗口起点
static float fpsValue = 0.0f;
static uint16_t stressStep = 0;

// 中心判定：长按必须从屏幕中心附近开始，避免和翻页手势冲突
bool atCenter(uint16_t x, uint16_t y) {
  const int cx = lcd.width() / 2;
  const int cy = lcd.height() / 2;
  return abs(static_cast<int>(x) - cx) <= 70 && abs(static_cast<int>(y) - cy) <= 55;
}

// FPS 浮层：不画背景块，只在画面上叠字。
// 每帧都会被下面的重绘覆盖，所以必须在每帧末尾重新绘制（见 drawStressFrame）。
void drawFpsOverlay() {
  char text[40];
  if (fpsValue > 0.0f) {
    snprintf(text, sizeof(text), "FPS %4.1f   %.1f ms", fpsValue, 1000.0f / fpsValue);
  } else {
    snprintf(text, sizeof(text), "FPS --.-   measuring");
  }

  lcd.setTextDatum(top_left);
  lcd.setTextSize(1);
  // 先画一层黑色偏移字做描边，亮背景上也读得清
  lcd.setTextColor(TFT_BLACK);
  lcd.drawString(text, 9, 7, &fonts::Font2);
  lcd.setTextColor(TFT_GREEN);
  lcd.drawString(text, 8, 6, &fonts::Font2);
}

void enterFpsMode() {
  fpsMode = true;
  fpsFrames = 0;
  fpsValue = 0.0f;
  fpsWindowMs = millis();
  stressStep = 0;
  blVisible = false;
  lcd.fillScreen(TFT_BLACK);
  screenBg = TFT_BLACK;
  logf(">>> FPS mode: hold screen centre again to exit\n");
}

void exitFpsMode() {
  fpsMode = false;
  logf("<<< FPS mode off (%.1f fps last window)\n", fpsValue);
  showPage(pageIndex);  // 回到原来的颜色页
}

// 一帧：旋转辐条 + 扩散圆环 + 轨道光点 + 中心脉冲 + 扫描线
// 全部用图元直接画到屏上，不做缓冲——正好压满 8080 并口的带宽。
static constexpr float kPi = 3.14159265f;

void drawStressFrame() {
  const int y0 = 0;
  const int w = lcd.width();
  const int h = lcd.height();
  const int cx = w / 2;
  const int cy = h / 2;

  // 用时间而不是帧号驱动动画：帧率高时不会转得更快，视觉速度始终一致。
  // 取低 20 位，避免长时间运行后 float 精度下降（约 17 分钟回绕一次）。
  const uint32_t t = millis() & 0xFFFFF;

  // 背景：深蓝底，蓝色分量缓慢呼吸
  const uint8_t breath = static_cast<uint8_t>(t >> 7);
  screenBg = lcd.color565(0, 4 + (breath >> 5), 16 + (breath >> 2));
  lcd.fillRect(0, y0, w, h, screenBg);

  lcd.startWrite();

  // 1) 旋转辐条：12 根，约 0.55 圈/秒，间隔长短交替
  const float spin = t * 0.0035f;
  for (int i = 0; i < 12; ++i) {
    const float a = spin + i * (kPi / 6.0f);
    const float ca = cosf(a);
    const float sa = sinf(a);
    const int r1 = 26;
    const int r2 = 150 + ((i & 1) ? 40 : 0);
    const uint16_t c = lcd.color565(0, 130 + i * 8, 255 - i * 6);
    lcd.drawLine(cx + ca * r1, cy + sa * r1, cx + ca * r2, cy + sa * r2, c);
  }

  // 2) 扩散圆环：4 圈向外推，越外越暗
  for (int i = 0; i < 4; ++i) {
    const int r = static_cast<int>((t / 8 + i * 55) % 220);
    const uint8_t v = static_cast<uint8_t>(240 - r);
    lcd.drawCircle(cx, cy, r, lcd.color565(v, v >> 2, 255 - v));
    lcd.drawCircle(cx, cy, r + 1, lcd.color565(v >> 1, v >> 3, 128 - (v >> 1)));
  }

  // 3) 轨道光点：6 颗绕半径 110 转，各带一小段拖尾
  for (int i = 0; i < 6; ++i) {
    const float a = t * 0.003f + i * (kPi / 3.0f);
    const int px = cx + cosf(a) * 110;
    const int py = cy + sinf(a) * 110;
    lcd.fillCircle(px, py, 7, lcd.color565(255, 190, 40));
    lcd.drawCircle(px, py, 10, lcd.color565(120, 70, 10));
    const int tx = cx + cosf(a - 0.35f) * 110;
    const int ty = cy + sinf(a - 0.35f) * 110;
    lcd.fillCircle(tx, ty, 3, lcd.color565(110, 80, 20));
  }

  // 4) 中心脉冲：半径 10~70 往复，约 1.6 秒一个周期
  const int pr = 10 + static_cast<int>((t / 12) % 60);
  lcd.fillCircle(cx, cy, pr, lcd.color565(255, 50, 110));
  lcd.drawCircle(cx, cy, pr + 5, TFT_WHITE);

  // 5) 扫描线：自上而下，用来看撕裂和帧同步
  const int sy = y0 + static_cast<int>((t / 5) % h);
  lcd.drawFastHLine(0, sy, w, lcd.color565(0, 255, 190));

  lcd.endWrite();

  drawFpsOverlay();          // 浮在最上层，每帧重画（背景刚被抹掉）
  drawBrightnessOverlay();   // 亮度也每帧重画，刷屏时仍能实时看到调光结果

  ++stressStep;
  ++fpsFrames;
}

void setup() {
  Serial.begin(115200);   // 原生 USB
  Serial0.begin(115200);  // UART0 → 板载 USB-UART
  delay(400);

  logf("\n=== ATK-MD0350 3.5in colour uniformity test ===\n");

  rgbLedOff();  // 关掉核心板板载 WS2812

  pinMode(board_pins::LCD_RD, OUTPUT);
  digitalWrite(board_pins::LCD_RD, HIGH);

  blBegin(0);  // LEDC 接管 IO40，先给 0% —— 初始化期间背光灭，不会闪白屏

  logf("lcd.init() ...\n");
  lcd.init();          // 顺带完成触摸初始化（INT 上拉 + 硬复位 + 地址探测）
  lcd.setRotation(1);  // 320x480 竖屏 → 480x320 横屏

  setBrightness(100);
  logf("LCD size: %d x %d   invert=%d rgb_order=%d\n",
       lcd.width(), lcd.height(), LCD_INVERT, LCD_RGB_ORDER);
  // 回读实际频率与最小脉宽：分频器设不上时 ledcSetup 会返回 0，
  // 低亮度会直接不亮；S8050 需要 >=3us 的高电平才可靠导通。
  const uint32_t actualHz = ledcReadFreq(kBlChannel);
  const double lsbUs =
      actualHz ? 1e6 / (static_cast<double>(actualHz) * (1 << kBlBits)) : 0.0;
  logf("backlight: ch%d req %luHz/%dbit, actual %luHz, LSB %.2fus, "
       "min duty %d = %.1fus, start 100%% (duty %lu/255)\n",
       kBlChannel, static_cast<unsigned long>(kBlFreq), kBlBits,
       static_cast<unsigned long>(actualHz), lsbUs, kBlMinDuty,
       kBlMinDuty * lsbUs, static_cast<unsigned long>(blDuty));

  if (gtDiag().ok) {
    logf("GT1151Q ready at 0x%02X, product id \"%s\"\n", gtDiag().addr,
         gtDiag().product_id);
  } else {
    logf("GT1151Q NOT FOUND - 只能看颜色，不能翻页\n");
    logf("  -> 检查 J2-6(SDA/IO42) J2-7(SCL/IO41) J2-17(INT/IO46) J2-16(RST/IO47)\n");
  }

  logf("LEFT/RIGHT = colour, UP/DOWN = brightness, tap = label, hold centre = FPS.\n");

  showPage(0);
}

void loop() {
  static uint32_t lastPoll = 0;
  static bool touching = false;
  static bool longFired = false;
  static uint16_t startX = 0, startY = 0, lastX = 0, lastY = 0;
  static uint32_t startMs = 0;
  static uint8_t brightnessAtStart = 100;  // 按下瞬间的亮度，滑动按它做基准加减

  const uint32_t now = millis();

  // 刷屏模式下每轮都渲染，不受触摸轮询节流影响
  if (fpsMode) {
    drawStressFrame();
    if (now - fpsWindowMs >= 1000) {  // 每 1 秒结算一次帧率
      fpsValue = fpsFrames * 1000.0f / static_cast<float>(now - fpsWindowMs);
      fpsFrames = 0;
      fpsWindowMs = now;
      logf("fps %.1f  (%.2f ms/frame)\n", fpsValue, 1000.0f / fpsValue);
    }
  } else {
    if (labelVisible && now > labelUntil) eraseLabel();
    if (blVisible && now > blUntil) eraseBrightnessOverlay();
  }

  // 触摸轮询：翻页模式 15ms 一次；刷屏模式 30ms 一次，把带宽留给填充
  const uint32_t interval = fpsMode ? 30 : 15;
  if (now - lastPoll < interval) {
    if (!fpsMode) delay(1);
    return;
  }
  lastPoll = now;

  uint16_t x = 0;
  uint16_t y = 0;
  const bool pressed = lcd.getTouch(&x, &y);

  if (pressed) {
    if (!touching) {  // 按下瞬间
      touching = true;
      longFired = false;
      startX = lastX = x;
      startY = lastY = y;
      startMs = now;
      brightnessAtStart = brightness;
    } else {
      lastX = x;
      lastY = y;
      // 长按判定：必须从中心区域按下，按住 800ms 触发，一次按压只触发一次
      if (!longFired && (now - startMs) >= 800 && atCenter(startX, startY)) {
        longFired = true;
        if (fpsMode) {
          exitFpsMode();
        } else {
          enterFpsMode();
        }
      }
    }
    return;
  }

  if (!touching) return;

  // 松开：判定滑动 / 轻点
  touching = false;

  const int dx = static_cast<int>(lastX) - static_cast<int>(startX);
  const int dy = static_cast<int>(lastY) - static_cast<int>(startY);
  const uint32_t held = now - startMs;

  if (longFired) return;  // 长按已经处理过，别再当滑动/轻点

  if (held >= 800) return;  // 长按了但不在中心：忽略

  if (!fpsMode && abs(dx) >= 60 && abs(dx) > abs(dy) * 3 / 2) {
    if (dx < 0) {
      showPage(pageIndex + 1);  // 左滑 → 下一色
    } else {
      showPage(pageIndex - 1);  // 右滑 → 上一色
    }
    return;
  }

  // 上滑调亮 / 下滑调暗：按滑动距离连续调，3px ≈ 1%。
  // 两种模式都允许，这样刷屏时也能实时观察 PWM 对画面和帧率的影响。
  if (abs(dy) >= 50 && abs(dy) > abs(dx) * 3 / 2) {
    const int delta = (static_cast<int>(startY) - static_cast<int>(lastY)) / 3;
    setBrightness(static_cast<uint8_t>(
        constrain(brightnessAtStart + delta, 0, 100)));
    drawBrightnessOverlay();
    logf("brightness %3d%%  duty %lu/255  (swipe dy=%d)\n", brightness,
         static_cast<unsigned long>(blDuty), dy);
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
