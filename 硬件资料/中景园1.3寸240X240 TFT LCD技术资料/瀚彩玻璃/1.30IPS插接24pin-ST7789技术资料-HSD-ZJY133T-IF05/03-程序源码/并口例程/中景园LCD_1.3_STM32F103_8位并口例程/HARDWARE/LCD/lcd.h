#ifndef __LCD_H
#define __LCD_H			  	 
#include "sys.h"
#include "stdlib.h"	   

#define USE_HORIZONTAL 0  //设置横屏或者竖屏显示 0或1为竖屏 2或3为横屏


#if USE_HORIZONTAL==0||USE_HORIZONTAL==1
#define LCD_W 240
#define LCD_H 240

#else
#define LCD_W 240
#define LCD_H 240
#endif

#define	u8 unsigned char
#define	u16 unsigned int
#define	u32 unsigned long

   						  
//-----------------测试LED端口定义---------------- 

#define LED_ON GPIO_ResetBits(GPIOA,GPIO_Pin_15)
#define LED_OFF GPIO_SetBits(GPIOA,GPIO_Pin_15)

//-----------------OLED端口定义---------------- 

#define DATAOUT(x) GPIOA->ODR=x; //数据输出
#define DATAIN     GPIOA->IDR;   //数据输入

#define	LCD_RST_SET	GPIOB->BSRR=1<<3    //复位			  PB3
#define	LCD_CS_SET  GPIOB->BSRR=1<<4    //片选端口  	PB4
#define	LCD_DC_SET	GPIOB->BSRR=1<<5    //数据/命令   PB5
#define	LCD_WR_SET	GPIOB->BSRR=1<<6    //写数据	    PB6
#define	LCD_RD_SET	GPIOB->BSRR=1<<7    //读数据		  PB7

#define	LCD_RST_CLR	GPIOB->BRR=1<<3     //复位
#define	LCD_CS_CLR  GPIOB->BRR=1<<4     //片选端口    PB3
#define	LCD_DC_CLR	GPIOB->BRR=1<<5     //数据/命令   PB4
#define	LCD_WR_CLR	GPIOB->BRR=1<<6     //写数据	    PB5
#define	LCD_RD_CLR	GPIOB->BRR=1<<7     //读数据	    PB6

#define OLED_CMD  0	//写命令
#define OLED_DATA 1	//写数据

extern  u16 BACK_COLOR;   //背景色

void LCD_Writ_Bus(u8 dat);
void LCD_WR_DATA8(u8 dat);
void LCD_WR_DATA(u16 dat);
void LCD_WR_REG(u8 dat);
void LCD_Address_Set(u16 x1,u16 y1,u16 x2,u16 y2);
void Lcd_Init(void); 
void LCD_Clear(u16 Color);
void LCD_ShowChinese(u16 x,u16 y,u8 index,u8 size,u16 color);
void LCD_DrawPoint(u16 x,u16 y,u16 color);
void LCD_DrawPoint_big(u16 x,u16 y,u16 colory);
void LCD_Fill(u16 xsta,u16 ysta,u16 xend,u16 yend,u16 color);
void LCD_DrawLine(u16 x1,u16 y1,u16 x2,u16 y2,u16 color);
void LCD_DrawRectangle(u16 x1, u16 y1, u16 x2, u16 y2,u16 color);
void Draw_Circle(u16 x0,u16 y0,u8 r,u16 color);
void LCD_ShowChar(u16 x,u16 y,u8 num,u8 mode,u16 color);
void LCD_ShowString(u16 x,u16 y,const u8 *p,u16 color);
u32 mypow(u8 m,u8 n);
void LCD_ShowNum(u16 x,u16 y,u16 num,u8 len,u16 color);
void LCD_ShowNum1(u16 x,u16 y,float num,u8 len,u16 color);
void LCD_ShowPicture(u16 x1,u16 y1,u16 x2,u16 y2);


//画笔颜色
#define WHITE         	 0xFFFF
#define BLACK         	 0x0000	  
#define BLUE           	 0x001F  
#define BRED             0XF81F
#define GRED 			       0XFFE0
#define GBLUE			       0X07FF
#define RED           	 0xF800
#define MAGENTA       	 0xF81F
#define GREEN         	 0x07E0
#define CYAN          	 0x7FFF
#define YELLOW        	 0xFFE0
#define BROWN 			     0XBC40 //棕色
#define BRRED 			     0XFC07 //棕红色
#define GRAY  			     0X8430 //灰色
//GUI颜色

#define DARKBLUE      	 0X01CF	//深蓝色
#define LIGHTBLUE      	 0X7D7C	//浅蓝色  
#define GRAYBLUE       	 0X5458 //灰蓝色
//以上三色为PANEL的颜色 
 
#define LIGHTGREEN     	 0X841F //浅绿色
#define LGRAY 			     0XC618 //浅灰色(PANNEL),窗体背景色

#define LGRAYBLUE        0XA651 //浅灰蓝色(中间层颜色)
#define LBBLUE           0X2B12 //浅棕蓝色(选择条目的反色)


					  		 
#endif  
	 
	 



