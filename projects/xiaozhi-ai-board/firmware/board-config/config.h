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

// ===== 内置喇叭：GSPK151035PN（8 Ω / 0.5 W，硬件说明 rev 1.9）=====
// 8 Ω 下 NS4150B 约 1.5 W（4 Ω 3 W 减半），是喇叭额定的 3 倍，必须限幅
// 提示音、拨轮调节与网络下发的音量都受此上限约束，并加峰值软限幅
#define AUDIO_SPEAKER_OHM            8
#define AUDIO_SPEAKER_RATED_MW       500
#define AUDIO_OUTPUT_VOLUME_MAX_DB   (-8)

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

// ===== 环境温湿度：AHT20（rev 1.8 换型，复用 codec 的 I2C，零新增 GPIO）=====
// 不要另建一条 I2C 总线：与 ES8311 共用同一个 i2c_master bus / device handle，
// 端口宏与 handle 获取方式以所用上游版本的 i2c_master API 为准，值照抄下面。
#define TEMP_SENSOR_I2C_SDA_PIN      GPIO_NUM_41   // == AUDIO_CODEC_I2C_SDA_PIN
#define TEMP_SENSOR_I2C_SCL_PIN      GPIO_NUM_42   // == AUDIO_CODEC_I2C_SCL_PIN
#define TEMP_SENSOR_I2C_ADDR         0x38          // AHT20 固定 7-bit 地址；写 0x70 / 读 0x71，无 ADDR 脚
#define TEMP_SENSOR_I2C_CLK_HZ       400000
#define TEMP_SENSOR_CMD_INIT         0xE1          // 初始化/校准，参数按 datasheet
#define TEMP_SENSOR_CMD_MEASURE      0xAC          // 触发单次测量，后跟 0x33 0x00
#define TEMP_SENSOR_CMD_SOFT_RESET   0xBA
#define TEMP_SENSOR_MEAS_TIMEOUT_MS  100           // 测量约 75–80ms，轮询 busy 位并留余量
#define TEMP_SENSOR_POLL_MS          3000          // 3s 单次采样：测量窗口较长，压低自热占空比
// 读数 7 字节：1 状态字节 + 5 数据字节（20bit RH + 20bit T）；AHT20 无 CRC，
// 靠状态位 busy(bit7)/CAL(bit3) + 连续两次读数一致 + 量程范围检查兜底
// RH(%) = 100*raw20/1048576；T(°C) = 200*raw20/1048576 - 50
// 读不到器件只记日志，不阻塞开机
// 注意：0x38 与常见电容触摸 IC 默认地址相同且不可改；本项目确定不加触摸，
// 以后若加触摸需换传感器或加 I2C mux
