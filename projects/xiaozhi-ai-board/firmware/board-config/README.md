# 板级配置参考

这里不是可编译工程，而是**要抄进上游 xiaozhi-esp32 的取值**：

```
xiaozhi-esp32/main/boards/xiaozhi-ai-board/
├── config.h              ← 抄 config.h 里的宏
├── xiaozhi_ai_board.cc   ← 板型类，照抄 bread-compact-wifi
└── (可选) st7789_vendor_init.c
```

| 文件 | 内容 |
|---|---|
| `config.h` | 引脚、屏分辨率/方向、背光、采样率等全部宏 |
| `st7789_vendor_init.c` | 中景园厂家初始化序列（含 IPS 的 0x21 与 VCOM/gamma），替换 esp_lcd 的通用 ST7789 初始化 |

## 三条注意

1. **宏名会随上游版本变**。`DISPLAY_MIRROR_X` 这类宏在近几个版本里改过名，抄之前先看 `main/boards/esp-s3-devkitc-1/config.h` 的当前写法，以它为准。
2. **屏的初始化必须用厂家序列**。ESP-IDF 自带的 ST7789 驱动初始化里 VCOM/gamma 不是这块屏的，直接用会发灰、对比度差。
3. **PSRAM 是八线（OPI）**。N16R8 在 menuconfig 里选 Octal，否则 `MALLOC_CAP_SPIRAM` 拿不到内存，LVGL 缓冲会退回内部 RAM。

## 显示参数一览（与硬件文档一致）

| 项 | 值 |
|---|---|
| 分辨率 | 240 × 240，RGB565 |
| SPI | SPI2_HOST，mode 0，40 MHz（实测稳后可 60 MHz） |
| SCLK / MOSI | GPIO12 / GPIO11 |
| DC / CS / RST | GPIO13 / GPIO10 / GPIO9 |
| BL | GPIO8，LEDC 20 kHz，10 bit，正逻辑 |
| 反显 | 开（IPS，初始化里的 0x21） |
| 镜像 / 交换 | 全关（竖屏正向）；装反了改这三个宏，不要改走线 |

## 环境温湿度（AHT20，rev 1.8 换型）

`config.h` 末尾的 `TEMP_SENSOR_*` 是抄进上游板型的取值：固定地址 `0x38`、初始化 `0xE1`、触发 `0xAC 0x33 0x00`、约 80 ms 测量、3 s 周期。
**AHT20 数据帧没有 CRC**，别套用旧 SHT30 的 CRC8 流程；靠状态位 busy/CAL、连续两次读数一致与量程检查（RH 0–100、T −40~85 °C）兜底。
**不要为它新建 I2C 总线**——与 ES8311 共用 GPIO41/42 和同一个 `i2c_master` handle，总线只有一组 4.7 kΩ 上拉。
器件缺失只记日志，不阻塞开机；读数用于室温上报，PCB 热隔离与左壁通风孔见硬件/结构文档。
**本项目确定不加触摸**：0x38 与常见触摸 IC 默认地址相同，且 AHT20 无 ADDR 脚、地址不可改。

## 内置喇叭与音量上限（rev 1.9）

`config.h` 音频段的 `AUDIO_SPEAKER_*` / `AUDIO_OUTPUT_VOLUME_MAX_DB` 是抄进上游板型的取值：喇叭内置 GSPK151035PN（8 Ω / 0.5 W，15×10×3.5），1.25T 端子接 J2。
**8 Ω 下 NS4150B 可输出约 1.5 W，是额定功率的 3 倍**，所以 `SetOutputVolume()`、开机提示音与所有播放路径都必须钳在 **−8 dB（相对满幅）** 以内并加软限幅，否则会烧音圈。
喇叭本体是 BTL 两线，**不占 GPIO、不需要驱动**；功放使能仍走 `AUDIO_PA_EN_PIN`（GPIO7，RC 延时消 POP）。
音腔、出音孔与限幅的硬件依据见硬件说明 rev 1.9 §03 与结构 rev 2.0。
