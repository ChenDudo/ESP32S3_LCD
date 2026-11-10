// 中景园 ZJY133T-IG01（ST7789V2）厂家初始化序列
// 来源：硬件资料/中景园1.3寸240X240 TFT LCD技术资料/瀚彩玻璃/
//       1.30IPS焊接12pin-…-ZJY133T-IG01/03-程序源码/11-…/HARDWARE/LCD/lcd_init.c
//
// 用法：在板型类里创建 esp_lcd panel_io 之后、创建 panel 之前调用
//       zjy133t_panel_init(panel_io)，然后跳过驱动自带的初始化。
// 注意：ESP-IDF 自带 ST7789 通用初始化的 VCOM/gamma 与这块屏不匹配，
//       直接用会发灰；本文件是替代它的最小实现。

#include "esp_err.h"
#include "esp_lcd_panel_io.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

typedef struct {
    uint8_t cmd;
    uint8_t len;
    const uint8_t *data;
    uint16_t delay_ms;
} zjy_init_cmd_t;

static const uint8_t D_36[] = {0x00};                     // MADCTL：竖屏正向
static const uint8_t D_3A[] = {0x05};                     // 16 bit RGB565
static const uint8_t D_B2[] = {0x1F, 0x1F, 0x00, 0x33, 0x33};
static const uint8_t D_B7[] = {0x00};
static const uint8_t D_BB[] = {0x3F};
static const uint8_t D_C0[] = {0x2C};
static const uint8_t D_C2[] = {0x01};
static const uint8_t D_C3[] = {0x0F};
static const uint8_t D_C4[] = {0x20};
static const uint8_t D_C6[] = {0x13};
static const uint8_t D_D0[] = {0xA4, 0xA1};
static const uint8_t D_D6[] = {0xA1};
static const uint8_t D_E0[] = {0xF0, 0x06, 0x0D, 0x0B, 0x0A, 0x07, 0x2E,
                               0x43, 0x45, 0x38, 0x14, 0x13, 0x25, 0x29};
static const uint8_t D_E1[] = {0xF0, 0x07, 0x0A, 0x08, 0x07, 0x23, 0x2E,
                               0x33, 0x44, 0x3A, 0x16, 0x17, 0x26, 0x2C};
static const uint8_t D_E4[] = {0x1D, 0x00, 0x00};          // 240 gate 线

static const zjy_init_cmd_t ZJY133T_INIT[] = {
    {0x11, 0, NULL,  120},   // Sleep out
    {0x36, 1, D_36,    0},
    {0x3A, 1, D_3A,    0},
    {0xB2, 5, D_B2,    0},
    {0xB7, 1, D_B7,    0},   // VGH 12.2V / VGL -7.16V
    {0xBB, 1, D_BB,    0},   // VCOM
    {0xC0, 1, D_C0,    0},
    {0xC2, 1, D_C2,    0},
    {0xC3, 1, D_C3,    0},   // VRH 4.3V
    {0xC4, 1, D_C4,    0},
    {0xC6, 1, D_C6,    0},
    {0xD0, 2, D_D0,    0},
    {0xD6, 1, D_D6,    0},
    {0xE0, 14, D_E0,   0},
    {0xE1, 14, D_E1,   0},
    {0xE4, 3, D_E4,    0},
    {0x21, 0, NULL,    0},   // INVON：IPS 必须反显
    {0x11, 0, NULL,  120},   // 厂家原序列有第二次，保留
    {0x29, 0, NULL,   20},   // Display on
};

esp_err_t zjy133t_panel_init(esp_lcd_panel_io_handle_t io)
{
    for (size_t i = 0; i < sizeof(ZJY133T_INIT) / sizeof(ZJY133T_INIT[0]); i++) {
        const zjy_init_cmd_t *c = &ZJY133T_INIT[i];
        esp_err_t err = esp_lcd_panel_io_tx_param(io, c->cmd, c->data, c->len);
        if (err != ESP_OK) {
            return err;
        }
        if (c->delay_ms) {
            vTaskDelay(pdMS_TO_TICKS(c->delay_ms));
        }
    }
    return ESP_OK;
}
