//////////////////////////////////////////////////////////////////////////////////	 
//本程序只供学习使用，未经作者许可，不得用于其它任何用途
//中景园电子
//店铺地址：http://shop73023976.taobao.com
//
//  文 件 名   : main.c
//  版 本 号   : v2.0
//  作    者   : HuangKai
//  生成日期   : 2018-10-31
//  最近修改   : 
//  功能描述   : LCD 8位并口接口演示例程(51系列)
//              说明: 
//      ----------------------------------------------------------------
//                 GND   接地
//                 VCC   3.3v
//      ------------控制引脚--------------------------------------------
//                 RST   P00
//                 CS    P01
//                 DC    P02
//                 SDC   P03(原理图的WR引脚)
//                 RD    P04 
//     -------------数据引脚---------------------------------------------
//                 P20-7
//     ------------------------------------------------------------------
//              ----------------------------------------------------------------
// 修改历史   :
// 日    期   : 
// 作    者   : HuangKai
// 修改内容   : 创建文件
//版权所有，盗版必究。
//Copyright(C) 中景园电子2018-10-31
//All rights reserved
//******************************************************************************/

#include "REG51.h"
#include "spi.h"
int main(void)
 {	
	 u8 i,m;
	 float t=0;
	 Lcd_Init();			     //初始化OLED  
	 LCD_Clear(WHITE);
	 BACK_COLOR=WHITE;
	 while(1)
	 {
		 	LCD_ShowChinese(10,0,0,32,RED);   //中
			LCD_ShowChinese(45,0,1,32,RED);   //景
			LCD_ShowChinese(80,0,2,32,RED);   //园
			LCD_ShowChinese(115,0,3,32,RED);  //电
			LCD_ShowChinese(150,0,4,32,RED);  //子
		 
		 	LCD_ShowChinese(10,75,0,16,RED);  //中
			LCD_ShowChinese(45,75,1,16,RED);  //景
			LCD_ShowChinese(80,75,2,16,RED);  //园
			LCD_ShowChinese(115,75,3,16,RED); //电
			LCD_ShowChinese(150,75,4,16,RED); //子
			LCD_ShowString(10,35,"2.4 TFT SPI 240*320",RED);
			LCD_ShowString(10,55,"LCD_W:",RED);	LCD_ShowNum(70,55,LCD_W,3,RED);
			LCD_ShowString(110,55,"LCD_H:",RED);LCD_ShowNum(160,55,LCD_H,3,RED);
		 
		  for(i=0;i<5;i++)
		  {
				for(m=0;m<6;m++)
				{
				  LCD_ShowPicture(m*40,120+i*40,39+m*40,159+i*40);
				}
		  }
			while(1)
			{
				LCD_ShowNum1(80,95,t,5,RED);
		    t+=0.01;
      }
   }
}