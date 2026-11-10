#pragma once

#include <Arduino.h>

#include "board_pins.h"

// 熄灭核心板板载 WS2812（GPIO48 → 0Ω → U1 XL-5050RGBC 的 DI）。
//
// 为什么不能只 digitalWrite(LOW)：WS2812 是锁存型器件，数据脚一直被拉低只会让它
// 停在 reset 状态，**不会清掉已经点亮的颜色**（PWM 保持上一次锁存的值）。
// 要真正熄灭，必须给它发一帧 24 位全 0 的数据。
// neopixelWrite() 用 RMT 产生精确时序，正好干这件事；之后把脚拉低，防止悬空被干扰。
inline void rgbLedOff() {
  if (board_pins::RGB_LED < 0) return;  // 自制底板：IO48 是触摸复位，没有这颗灯
  neopixelWrite(static_cast<uint8_t>(board_pins::RGB_LED), 0, 0, 0);
  pinMode(board_pins::RGB_LED, OUTPUT);
  digitalWrite(board_pins::RGB_LED, LOW);
}
