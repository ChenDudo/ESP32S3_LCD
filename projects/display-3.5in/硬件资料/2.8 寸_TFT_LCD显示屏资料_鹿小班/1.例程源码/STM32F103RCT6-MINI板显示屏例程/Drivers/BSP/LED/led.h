 

#ifndef __LED_H
#define __LED_H

#include "./SYSTEM/sys/sys.h"

/******************************************************************************************/
/* 引脚 定义 */

#define LED0_GPIO_PORT                  GPIOA
#define LED0_GPIO_PIN                   SYS_GPIO_PIN8
#define LED0_GPIO_CLK_ENABLE()          do{ RCC->APB2ENR |= 1 << 2; }while(0)   /* PA口时钟使能 */

#define LED1_GPIO_PORT                  GPIOD
#define LED1_GPIO_PIN                   SYS_GPIO_PIN2
#define LED1_GPIO_CLK_ENABLE()          do{ RCC->APB2ENR |= 1 << 5; }while(0)   /* PD口时钟使能 */

/******************************************************************************************/



/* LED端口定义 */
#define LED0(x)         sys_gpio_pin_set(LED0_GPIO_PORT, LED0_GPIO_PIN, x)      /* LED0 */
#define LED1(x)         sys_gpio_pin_set(LED1_GPIO_PORT, LED1_GPIO_PIN, x)      /* LED1 */

/* LED取反定义 */
#define LED0_TOGGLE()   do{ LED0_GPIO_PORT->ODR ^= LED0_GPIO_PIN; }while(0)      /* LED0 = !LED0 */
#define LED1_TOGGLE()   do{ LED1_GPIO_PORT->ODR ^= LED1_GPIO_PIN; }while(0)      /* LED1 = !LED1 */


void led_init(void);    /* 初始化 */

#endif

















