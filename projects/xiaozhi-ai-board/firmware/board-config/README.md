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
