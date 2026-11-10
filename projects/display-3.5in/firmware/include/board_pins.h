#pragma once

// 引脚定义：ESP32-S3-WROOM-1-N16R8 + 正点原子 ATK-MD0350 3.5" 480x320 电容触摸屏
// 屏模块 V2.4（旧资料）：显示走 8080 16 位并口，触摸走 I2C（GT9 系列），34P 2x17 排针 2.54mm。
//
// 排针与 GPIO 的对应关系见 硬件设计/引脚分配表-电容版.csv
// 注意：34P 排针的丝印名沿用了电阻屏时代的命名——30/34 脚实际是 I2C，33 脚实际是触摸复位。

namespace board_pins {

// ---- 16 位数据总线：排针 6~21 脚（DB0~DB15）----
constexpr int LCD_D0  = 1;
constexpr int LCD_D1  = 2;
constexpr int LCD_D2  = 3;
constexpr int LCD_D3  = 4;
constexpr int LCD_D4  = 5;
constexpr int LCD_D5  = 6;
constexpr int LCD_D6  = 7;
constexpr int LCD_D7  = 8;
constexpr int LCD_D8  = 9;
constexpr int LCD_D9  = 10;
constexpr int LCD_D10 = 11;
constexpr int LCD_D11 = 12;
constexpr int LCD_D12 = 13;
constexpr int LCD_D13 = 14;
constexpr int LCD_D14 = 15;
constexpr int LCD_D15 = 16;

// ---- LCD 控制信号 ----
constexpr int LCD_WR  = 17;
constexpr int LCD_CS  = 18;
constexpr int LCD_RS  = 21;  // 排针 2 脚，命令/数据选择（DC）
constexpr int LCD_RST = 38;  // 排针 5 脚
constexpr int LCD_RD  = 39;  // 排针 4 脚；底板 10K 上拉到 3V3，驱动按只写运行
constexpr int LCD_BL  = 40;  // 排针 23 脚，高电平点亮背光

// ---- 电容触摸（I2C + 中断 + 复位）----
constexpr int TP_SCL = 41;  // 排针 34 脚（丝印 CLK），I2C_SCL
constexpr int TP_SDA = 42;  // 排针 30 脚（丝印 MOSI），I2C_SDA
constexpr int TP_INT = 46;  // 排针 31 脚（丝印 PEN），输入专用脚

// 触摸复位脚：
//   自制底板用 IO48（干净、无复用）。
//   但很多 ESP32-S3 开发板（DevKitC-1 等）把 GPIO48 接着板载 RGB WS2812，
//   用它做复位会出现灯乱闪、个别板子还把电平拉偏，所以开发板调试时改用空闲的 IO47。
//   —— 此时 GPS_PPS 不可用（PPS 本来就是可选项）。
#define BOARD_TP_RST_ON_IO47 1

#if BOARD_TP_RST_ON_IO47
constexpr int TP_RST = 47;   // 排针 33 脚（丝印 CS），实为触摸复位
constexpr int GPS_PPS = -1;  // 被 TP_RST 占用，不接
#else
constexpr int TP_RST = 48;
constexpr int GPS_PPS = 47;
#endif

// 核心板板载 WS2812：GPIO48 经 0Ω 接 U1(XL-5050RGBC) 的 DI。
// 开发板模式下 IO48 空闲，固件会主动把它熄灭；自制底板把 48 用作 TP_RST，没有这颗灯。
#if BOARD_TP_RST_ON_IO47
constexpr int RGB_LED = 48;
#else
constexpr int RGB_LED = -1;
#endif

// 排针 29 脚（MISO）与 32 脚（BUSY）在电容版上是 NC，不接任何 GPIO。

// ---- 扩展外设 ----
// 温湿度 AHT20(0x38) 与气压 GY-BMP280(0x76) 挂在触摸同一条 I2C 上（J4 排针）
constexpr int I2C_SCL   = TP_SCL;  // 排针 J4-3 / 屏 34 脚
constexpr int I2C_SDA   = TP_SDA;  // 排针 J4-2 / 屏 30 脚

// GNSS ATGM336H-5N31 走 UART1，占用原 J3 调试口（硬件串口日志让位给 USB-CDC）
constexpr int GPS_TX    = 43;  // ESP32 发送 → GPS 模块 RXD（J3-2）
constexpr int GPS_RX    = 44;  // ESP32 接收 ← GPS 模块 TXD（J3-3）
// GPS_PPS 见上方定义：开发板模式下为 -1（IO47 让给 TP_RST）

}  // namespace board_pins
