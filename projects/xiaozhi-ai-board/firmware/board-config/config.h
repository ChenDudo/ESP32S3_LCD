// 小智 AI 板 · 板级配置（参考取值，非独立编译单元）
// 目标位置：xiaozhi-esp32/main/boards/xiaozhi-ai-board/config.h
//
// 宏名以你拉取的上游版本为准（近版本改过 DISPLAY_* 的命名），
// 先对照 main/boards/esp-s3-devkitc-1/config.h，再抄本文件的“值”。

#pragma once

// ===== 主控 =====
// ESP32-S3-WROOM-1-N16R8：16 MB Flash + 8 MB Octal PSRAM
// menuconfig: Flash 16MB / PSRAM Octal(OPI) / 分区表 16MB v2

// ===== 显示屏：中景园 ZJY133T-IG01（1.3" IPS 240x240 ST7789V2）=====
#define DISPLAY_WIDTH            240
#define DISPLAY_HEIGHT           240
#define DISPLAY_OFFSET_X         0
#define DISPLAY_OFFSET_Y         0
#define DISPLAY_SWAP_XY          false
#define DISPLAY_MIRROR_X         false
#define DISPLAY_MIRROR_Y         false
#define DISPLAY_INVERT_COLOR     true     // IPS，对应初始化 0x21
#define DISPLAY_RGB_ORDER        LCD_RGB_ELEMENT_ORDER_RGB
#define DISPLAY_BACKLIGHT_PIN    GPIO_NUM_8
#define DISPLAY_BACKLIGHT_OUTPUT_INVERT false   // 低边 NMOS，高电平点亮
#define DISPLAY_BL_PWM_HZ        20000    // 20 kHz，避开音频与帧率拍频
#define DISPLAY_BL_PWM_BITS      10

// SPI（屏只写，无 MISO）
#define DISPLAY_SPI_HOST         SPI2_HOST
#define DISPLAY_SPI_SCLK_PIN     GPIO_NUM_12
#define DISPLAY_SPI_MOSI_PIN     GPIO_NUM_11
#define DISPLAY_SPI_DC_PIN       GPIO_NUM_13
#define DISPLAY_SPI_CS_PIN       GPIO_NUM_10
#define DISPLAY_SPI_RST_PIN      GPIO_NUM_9
#define DISPLAY_SPI_CLOCK_HZ     (40 * 1000 * 1000)

// ===== 音频：ES8311 + NS4150B（方案 A，单麦）=====
#define AUDIO_I2S_GPIO_MCLK      GPIO_NUM_14
#define AUDIO_I2S_GPIO_BCLK      GPIO_NUM_15
#define AUDIO_I2S_GPIO_WS        GPIO_NUM_16
#define AUDIO_I2S_GPIO_DIN       GPIO_NUM_17   // codec -> MCU
#define AUDIO_I2S_GPIO_DOUT      GPIO_NUM_18   // MCU -> codec
#define AUDIO_CODEC_I2C_SDA_PIN  GPIO_NUM_41
#define AUDIO_CODEC_I2C_SCL_PIN  GPIO_NUM_42
#define AUDIO_PA_EN_PIN          GPIO_NUM_7
#define AUDIO_SAMPLE_RATE        16000

// ===== 交互 =====
#define WHEEL_UP_PIN             GPIO_NUM_2    // 拨轮上拨
#define WHEEL_DOWN_PIN           GPIO_NUM_6    // 拨轮下拨
#define WHEEL_PRESS_PIN          GPIO_NUM_4    // 拨轮按压 = 对话/打断
#define LED_STRIP_GPIO           GPIO_NUM_48

// ===== TF 卡（microSD，SPI3 独立总线）=====
#define SDCARD_SPI_HOST          SPI3_HOST
#define SDCARD_CLK_PIN           GPIO_NUM_39
#define SDCARD_MOSI_PIN          GPIO_NUM_40
#define SDCARD_MISO_PIN          GPIO_NUM_38
#define SDCARD_CS_PIN            GPIO_NUM_47
#define SDCARD_CD_PIN            GPIO_NUM_21    // 卡插入 -> GND，10k 上拉
#define SDCARD_MOUNT_POINT       "/sdcard"
#define SDCARD_CLOCK_HZ          (20 * 1000 * 1000)

// ===== 系统 =====
#define BOOT_BUTTON_GPIO         GPIO_NUM_0
#define BAT_ADC_PIN              GPIO_NUM_5
#define VBUS_SENSE_PIN           GPIO_NUM_1    // 5V 分压检测，可选
