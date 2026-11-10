# 固件设计

目标：在自制板上跑通 `xiaozhi-esp32`，并注册为一块自定义板型。

状态：**待建工程**。下面是开工前就定好的部分，避免画完板才发现引脚对不上。

## 技术选型

| 项 | 选择 | 原因 |
|---|---|---|
| 框架 | ESP-IDF **v6.1**（当前最新稳定） | 小智主线已迁到 v6.0+；v5.2 已于 2026-08 EOL |
| 板型 | 自定义板型，照抄 `main/boards/bread-compact-wifi` 改造 | 目录：`main/boards/xiaozhi-ai-board/` |
| 分区表 | 16MB 方案（`partitions/v2`） | 其中 8MB 是 assets 分区，存唤醒词模型/字体/音效，**Flash 小于 16MB 放不下** |
| 拨轮 | 6 脚贴片三向开关（上/下/按压） | 3 个普通按键；上/下音量 ±5%，按压对话；不是编码器，不用 PCNT |
| 显示 | ESP-IDF `esp_lcd` + ST7789V2 面板驱动 | **必须用厂家初始化序列**（VCOM/gamma/0x21 反显），见 `board-config/` |
| 编译路径 | **必须纯 ASCII** | ESP-IDF 对中文路径的报错极难排查 |

## 引脚分配（板级 config.h）

| 功能 | GPIO | 备注 |
|---|---|---|
| I2S_MCLK | 14 | codec 主时钟 |
| I2S_BCLK | 15 | |
| I2S_WS / LRCK | 16 | |
| I2S_DIN（收） | 17 | ES8311/ES7210 SDOUT → 主控 |
| I2S_DOUT（发） | 18 | 主控 → ES8311 SDIN |
| I2C_SDA / SCL | 41 / 42 | codec 寄存器 + AHT20（固定 0x38）；本项目不加触摸，全总线一组 4.7 kΩ 上拉 |
| PA_EN | 7 | 功放使能，串 RC 延时消 POP 声 |
| WHEEL_UP / WHEEL_DOWN | 2 / 6 | 拨轮上/下拨 |
| WHEEL_PRESS | 4 | 拨轮按压＝对话/打断键 |
| LED_DIN | 48 | WS2812 |
| LCD_SCLK / MOSI | 12 / 11 | |
| LCD_DC / CS / RST / BL | 13 / 10 / 9 / 8 | |
| BAT_ADC | 5 | VBAT 100k/100k 分压 |
| BOOT | 0 | strapping，仅上电瞬间采样 |

**不要碰的脚**：GPIO19/20（USB D−/D+）、GPIO0/3/45/46 不做对外输出；26–37 被 Flash/八线 PSRAM 占用。
**可用 GPIO 已排满**：新增外设一律先评审。本次 AHT20 复用 I2C 41/42，没有占用新脚；以后必须加单总线/ADC 器件时，先砍 VBUS_SENSE（GPIO1）这类可选项。**不加触摸是硬约束**：AHT20 固定占 0x38 且地址不可改。

## 显示屏（ZJY133T-IG01）

| 项 | 值 |
|---|---|
| 分辨率 / 颜色 | 240 × 240，RGB565（16 bit） |
| SPI | `SPI2_HOST`，mode 0，40 MHz（实测稳后可 60 MHz），**无 MISO** |
| 引脚 | SCLK 12 / MOSI 11 / DC 13 / CS 10 / RST 9 / BL 8 |
| 背光 | LEDC 20 kHz、10 bit，正逻辑（低边 2N7002） |
| 反显 | `invert_color = true`（IPS，初始化 0x21） |
| 镜像 / 交换 | 全关（竖屏正向） |

**不要用 ST7789 的通用初始化**：这块屏的 VCOM（0xBB=0x3F）、gamma、gate 数（0xE4）都与默认值不同，用错会发灰、对比度差。
厂家序列已整理成 `board-config/st7789_vendor_init.c`，可直接调 `zjy133t_panel_init(panel_io)`。
引脚与显示宏见 `board-config/config.h`。硬件依据见 `../硬件设计/显示屏接口设计-ZJY133T-IG01.html`。

## TF 卡（microSD）

| 项 | 值 |
|---|---|
| 总线 | `SPI3_HOST` 独立总线（**不跟屏共用 SPI2**），20 MHz |
| 引脚 | CLK 39 / MOSI 40 / MISO 38 / CS 47 / CD 21 |
| 文件系统 | FAT32，挂载点 `/sdcard` |
| 容量 | ≤32 GB（SDHC，出厂格式化成 FAT32） |

挂载用 `esp_vfs_fat_sdspi_mount()`：`slot_config.host_id = SPI3_HOST`，引脚填上表，`format_if_mount_failed = false`。
CD 脚（GPIO21）10k 上拉、卡插入为低，可以先读 CD 再决定是否挂载，没卡不影响启动。
卡座 CS 有 10k 上拉，启动时不会被卡抢总线。

## 温湿度传感器（AHT20，rev 1.8 换型）

**它不是新引脚，是 codec 那条 I2C 总线上的第二个设备**：ES8311（0x18 段）与 AHT20（固定 0x38）共用 GPIO41/42、共用同一个 `i2c_master` bus/handle，总线只贴一组 4.7 kΩ 上拉。可用 GPIO 已排满，后续加器件也照这个思路走。
**本项目确定不做触摸**：AHT20 地址固定且无 ADDR 脚，与常见电容触摸 IC（FT6x36 等）默认地址 0x38 相同；以后若加触摸，必须换传感器或加 I2C mux。

| 项 | 值 |
|---|---|
| 器件 / 地址 | AHT20（奥松），固定 `0x38`（写 `0x70` / 读 `0x71`），**无地址选择脚** |
| 总线 | 与 ES8311 共用 SDA 41 / SCL 42，400 kHz，**不要另建 bus** |
| 启动 | 上电 ≥40 ms 后读状态字；CAL(bit3) 未置位则发 `0xE1` 初始化（必要时 `0xBA` 软复位重来） |
| 测量 | `0xAC 0x33 0x00` 触发，约 75–80 ms；轮询状态字 busy(bit7) 或等超时 |
| 数据 | 7 字节：1 状态 + 5 数据（20 bit RH + 20 bit T）；**AHT20 无 CRC** |
| 换算 | `RH = 100·raw20/2^20` %；`T = 200·raw20/2^20 − 50` °C |
| 校验兜底 | 状态位 busy/CAL + 连续两次读数一致 + 量程检查（RH 0–100、T −40~85 °C）；异常丢弃本次，不要用旧 SHT30 的 CRC8 流程 |
| 周期 | **3 s 单次采样**（测量窗口 80 ms，比 SHT30 长，压低自热占空比；别用连续模式） |
| 失败处理 | 器件缺失 / 读数异常只记日志，**不阻塞开机** |

读数用于对话里回答室温/湿度与设备状态上报（走板型类暴露的状态或 MCP 工具，**别在音频任务里同步等 80 ms**）。
器件贴 PCB 左边缘 (5, 26)，靠左壁通风孔；PCB 热隔离槽与外壳通风要求见 `../硬件设计/小智AI自制板-硬件设计说明.html` §04 与结构 rev 2.0（温湿度换型的机械数值未变；内置喇叭位与出音孔见结构 §02）。
**读数偏高先查布局与通风，不要用软件偏移硬补。**

## 烧录与串口（USB-C 一根线）

板子用 ESP32-S3 自带的 **USB-Serial/JTAG**（GPIO19/20 直连 USB-C），**没有 CH340**。插上 USB-C 就是串口：

- Windows：设备管理器出现 `USB JTAG/serial debug unit (COMx)`
- macOS / Linux：`/dev/tty.usbmodem*` / `/dev/ttyACM0`

```bash
idf.py -p COMx flash monitor
```

esptool 会通过 USB 控制线自动复位进下载模式，正常不用按按键。**固件跑飞或电脑不认口**时：用针捅住左壁的
**BOOT** 针孔，再捅一下 **RST**，松开 BOOT，出现下载口后再烧。

menuconfig 把控制台指到 USB：
`Component config → ESP System Settings → Channel for console output → USB Serial/JTAG Controller`。
UART0（GPIO43/44）只留测试点，作为最后救砖。

注意：要用**数据线**，纯充电线不行；CC 的 5.1 kΩ 不能漏，否则 C-to-C 线不供电。

## 要写的代码

1. **板型定义** `main/boards/xiaozhi-ai-board/config.h`
   - 上表全部宏 + `WHEEL_UP_PIN` / `WHEEL_DOWN_PIN` / `WHEEL_PRESS_PIN`
   - 音频输出走 ES8311，输入按最终方案（单麦直连 / ES7210 双麦）二选一
2. **板型类** 继承 `WifiBoard`，实现 `GetAudioCodec()`、`GetDisplay()`、初始化按键与旋钮
3. **拨轮回调** 注册三个按键：上/下 → `SetOutputVolume()` 每次 ±5%，按住 300ms 后每 100ms 连发；按压 → 对话/打断。
   **不要用 `iot_knob`**：这颗开关没有 A/B 相，是三个独立轻触。
4. **按压逻辑** 短按＝对话/打断，长按＝重新配网
5. **温湿度** 复用 codec 的 I2C handle 读 AHT20（0x38），3 s 一次、状态位 + 双读数一致性校验（无 CRC）；独立低优先级任务，读失败不阻塞开机
6. **音量限幅（内置喇叭硬约束）** `SetOutputVolume()` 与所有提示音统一钳在 **−8 dB（相对满幅）** 以内并加峰值/软限幅：8 Ω 下 NS4150B 可输出约 1.5 W，是内置 0.5 W 喇叭额定的 3 倍。拨轮每次 ±5% 不得越过上限；开机默认音量取低值，上板先用示波器实测不过功率

## menuconfig 关键项

- `Component config → XiaoZhi → Board Type`：选到自己的板型
- `ESP PSRAM`：模式必须与模组一致（N16R8 是 **Octal / OPI**），否则 `heap_caps_malloc(MALLOC_CAP_SPIRAM)` 返回 NULL
- `Flash size`：16MB，Flash mode 与模组一致（DIO/QIO 写错会起不来）
- `Partition Table`：自定义 16MB 方案

## 上板调试顺序

电源 → 串口识别 → 屏点亮 → 喇叭出声（限幅后低音量）→ 麦克风录音 → I2C 扫描（codec + 0x38）→ 温湿度读数 → 唤醒词 → 完整对话。
每一段用示例工程单独验证，不要一上来跑完整固件。

## 待办

- [ ] 建 PlatformIO / ESP-IDF 工程骨架
- [ ] 把 `board-config/` 的宏与厂家初始化序列并入上游板型
- [ ] 写板型 `config.h` 与板型类
- [ ] 单测：LCD 点亮 / I2S 出声 / 拨轮三向按键 / I2C 扫描与 AHT20 读数
- [ ] 输出音量上限 −8 dB + 软限幅；示波器复核功放输出不过功率、AEC 分压不削顶
- [ ] AHT20 读数接入板型状态/MCP，室温与湿度可对话查询
- [ ] 接入小智主流程，验证唤醒与打断
