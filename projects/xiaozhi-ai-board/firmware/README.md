# 固件设计

目标：在自制板上跑通 `xiaozhi-esp32`，并注册为一块自定义板型。

状态：**待建工程**。下面是开工前就定好的部分，避免画完板才发现引脚对不上。

## 技术选型

| 项 | 选择 | 原因 |
|---|---|---|
| 框架 | ESP-IDF **v6.1**（当前最新稳定） | 小智主线已迁到 v6.0+；v5.2 已于 2026-08 EOL |
| 板型 | 自定义板型，照抄 `main/boards/bread-compact-wifi` 改造 | 目录：`main/boards/xiaozhi-ai-board/` |
| 分区表 | 16MB 方案（`partitions/v2`） | 其中 8MB 是 assets 分区，存唤醒词模型/字体/音效，**Flash 小于 16MB 放不下** |
| 旋钮 | `iot_knob` 组件（小智已内置抽象） | 10ms 软件轮询，手拧场景足够；S3 虽带硬件 PCNT，暂不必用 |
| 编译路径 | **必须纯 ASCII** | ESP-IDF 对中文路径的报错极难排查 |

## 引脚分配（板级 config.h）

| 功能 | GPIO | 备注 |
|---|---|---|
| I2S_MCLK | 14 | codec 主时钟 |
| I2S_BCLK | 15 | |
| I2S_WS / LRCK | 16 | |
| I2S_DIN（收） | 17 | ES8311/ES7210 SDOUT → 主控 |
| I2S_DOUT（发） | 18 | 主控 → ES8311 SDIN |
| I2C_SDA / SCL | 41 / 42 | codec 寄存器；屏触摸可共用 |
| PA_EN | 7 | 功放使能，串 RC 延时消 POP 声 |
| KNOB_A / KNOB_B | 2 / 6 | 编码器 A/B 相 |
| KNOB_SW | 4 | 波轮按压＝对话/打断键（**独立功能键已取消**） |
| LED_DIN | 48 | WS2812 |
| LCD_SCLK / MOSI | 12 / 11 | |
| LCD_DC / CS / RST / BL | 13 / 10 / 9 / 8 | |
| BAT_ADC | 5 | VBAT 100k/100k 分压 |
| BOOT | 0 | strapping，仅上电瞬间采样 |

**不要碰的脚**：GPIO19/20（USB D−/D+）、GPIO0/3/45/46 不做对外输出。

## 要写的代码

1. **板型定义** `main/boards/xiaozhi-ai-board/config.h`
   - 上表全部宏 + `KNOB_PIN_A` / `KNOB_PIN_B`
   - 音频输出走 ES8311，输入按最终方案（单麦直连 / ES7210 双麦）二选一
2. **板型类** 继承 `WifiBoard`，实现 `GetAudioCodec()`、`GetDisplay()`、初始化按键与旋钮
3. **旋钮回调** 注册 `KNOB_LEFT` / `KNOB_RIGHT` → `SetOutputVolume()`，每格 5%（EC11 18 段正好一档一步）
4. **按压逻辑** 短按＝对话/打断，长按＝重新配网

## menuconfig 关键项

- `Component config → XiaoZhi → Board Type`：选到自己的板型
- `ESP PSRAM`：模式必须与模组一致（N16R8 是 **Octal / OPI**），否则 `heap_caps_malloc(MALLOC_CAP_SPIRAM)` 返回 NULL
- `Flash size`：16MB，Flash mode 与模组一致（DIO/QIO 写错会起不来）
- `Partition Table`：自定义 16MB 方案

## 上板调试顺序

电源 → 串口识别 → 屏点亮 → 喇叭出声 → 麦克风录音 → 唤醒词 → 完整对话。
每一段用示例工程单独验证，不要一上来跑完整固件。

## 待办

- [ ] 建 PlatformIO / ESP-IDF 工程骨架
- [ ] 写板型 `config.h` 与板型类
- [ ] 单测：LCD 点亮 / I2S 出声 / 编码器计数
- [ ] 接入小智主流程，验证唤醒与打断
