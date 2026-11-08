# -*- coding: utf-8 -*-
"""Rev I —— A3 横向三视图（正视图 / 上视图 / 右视图 + 辅助下视图）

输出：
  deliverables/ESP32S3_LCD_全覆盖外壳_三视图.pdf   A3 420x297，1 页
  deliverables/ESP32S3_LCD_全覆盖外壳_三视图.dxf   1:1、单位 mm、可编辑
"""
import os, json
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import ezdxf

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "deliverables")
G = json.load(open(os.path.join(HERE, "geom_v2.json"), encoding="utf-8"))

pdfmetrics.registerFont(TTFont("SimHei", r"C:\Windows\Fonts\simhei.ttf"))
INK = HexColor("#1b2430")
DIMC = HexColor("#2f6db3")
REDC = HexColor("#c0392b")
GRAY = HexColor("#7b8794")
BLUE = HexColor("#1f4e79")
GREEN = HexColor("#2e7d52")
PALE = HexColor("#f7fafc")
LIGHT = HexColor("#eef3f8")
SIDE = HexColor("#c9d6e3")
WINF = HexColor("#ffffff")
ANTF = HexColor("#e6eff9")
GRNF = HexColor("#e4f3ea")

W, H = G["W"], G["H"]
HT = G["H_TOTAL"]
TB, TTI, ZTI = G["T_BASE"], G["T_TOP"], G["Z_TOP_IN"]
WIN = G["WIN"]
AX0, AY0, AX1, AY1 = G["ANT"]
AZ0, AZ1 = G["ANT_SLOT_Z0"], G["ANT_SLOT_Z1"]
RST = G["RESET_POS"]
RSTD = G["RESET_HOLE_D"]
HOLES = [tuple(h) for h in G["HOLES"]]
SCREW_POS = [tuple(p) for p in G["SCREW_POS"]]
SLOTS = G["SLOTS"]
TOP_SLOTS = [(b[0], b[2], z0, z1, n) for n, b, z0, z1, d in SLOTS
             if b[1] >= H - G["T_WALL"] - 0.5]
BOT_SLOTS = [(b[0], b[2], z0, z1, n) for n, b, z0, z1, d in SLOTS if b[1] < 0]
RGT_SLOTS = [(b[1], b[3], z0, z1, n) for n, b, z0, z1, d in SLOTS
             if b[0] >= W - G["T_WALL"] - 0.5]

S = 1.6  # 图示放大比例（尺寸数字均为实际 mm）
PW, PH = 420.0, 297.0
PDF = os.path.join(OUT, "ESP32S3_LCD_全覆盖外壳_三视图.pdf")
c = canvas.Canvas(PDF, pagesize=(PW * mm, PH * mm))
c.setTitle("ESP32S3_LCD 全覆盖外壳 三视图 Rev I")
c.setAuthor("WorkBuddy")


def TW(s, size):
    return pdfmetrics.stringWidth(str(s), "SimHei", size) / 72.0 * 25.4


def T(s, x, y, size=7, color=INK, font="SimHei"):
    c.setFont(font, size); c.setFillColor(color)
    c.drawString(x * mm, y * mm, str(s))


def TC(s, cx, y, size=7, color=INK):
    T(s, cx - TW(s, size) / 2, y, size, color)


def TR(s, x, y, size=7, color=INK):
    c.setFont("SimHei", size); c.setFillColor(color)
    c.drawRightString(x * mm, y * mm, str(s))


def LN(x1, y1, x2, y2, color=INK, w=0.3, dash=None):
    c.setStrokeColor(color); c.setLineWidth(w)
    if dash: c.setDash(dash)
    c.line(x1 * mm, y1 * mm, x2 * mm, y2 * mm)
    if dash: c.setDash()


def RECT(x, y, w, h, color=INK, lw=0.35, fill=None, dash=None):
    if fill:
        c.setFillColor(fill); c.rect(x * mm, y * mm, w * mm, h * mm, stroke=0, fill=1)
    c.setStrokeColor(color); c.setLineWidth(lw)
    if dash: c.setDash(dash)
    c.rect(x * mm, y * mm, w * mm, h * mm, stroke=1, fill=0)
    if dash: c.setDash()


def RR(x, y, w, h, r, color=INK, lw=0.45, fill=None, dash=None):
    if fill:
        c.setFillColor(fill); c.roundRect(x * mm, y * mm, w * mm, h * mm, r * mm, stroke=0, fill=1)
    c.setStrokeColor(color); c.setLineWidth(lw)
    if dash: c.setDash(dash)
    c.roundRect(x * mm, y * mm, w * mm, h * mm, r * mm, stroke=1, fill=0)
    if dash: c.setDash()


def CIRCLE(x, y, r, color=INK, lw=0.35, fill=None, dash=None):
    if fill:
        c.setFillColor(fill); c.circle(x * mm, y * mm, r * mm, stroke=0, fill=1)
    c.setStrokeColor(color); c.setLineWidth(lw)
    if dash: c.setDash(dash)
    c.circle(x * mm, y * mm, r * mm, stroke=1, fill=0)
    if dash: c.setDash()


def MARKS(xoff, yoff, sc, color=INK):
    """顶板一体成型凸字（geom_v2.json 字形轮廓，even-odd 填充挖空内孔）。"""
    c.setFillColor(color)
    for item in G.get("TEXT_MARKS", []):
        for poly in item["polys"]:
            p = c.beginPath()
            for ring in [poly["outer"]] + poly["holes"]:
                if len(ring) < 3:
                    continue
                p.moveTo((xoff + ring[0][0] * sc) * mm,
                         (yoff + ring[0][1] * sc) * mm)
                for x, y in ring[1:]:
                    p.lineTo((xoff + x * sc) * mm, (yoff + y * sc) * mm)
                p.close()
            c.drawPath(p, stroke=0, fill=1, fillMode=1)


def DIMH(x1, x2, y, label, color=DIMC, size=6.2, above=True):
    LN(x1, y, x2, y, color, 0.25)
    for xx, s in ((x1, 1), (x2, -1)):
        LN(xx, y, xx + s * 1.6, y + 0.7, color, 0.25)
        LN(xx, y, xx + s * 1.6, y - 0.7, color, 0.25)
    TC(label, (x1 + x2) / 2, y + (1.6 if above else -size * 0.42 - 2.4), size, color)
    LN(x1, y - 2.2, x1, y + 2.2, color, 0.2)
    LN(x2, y - 2.2, x2, y + 2.2, color, 0.2)


def DIMV(y1, y2, x, label, color=DIMC, size=6.2, left=True):
    LN(x, y1, x, y2, color, 0.25)
    for yy, s in ((y1, 1), (y2, -1)):
        LN(x, yy, x + 0.7, yy + s * 1.6, color, 0.25)
        LN(x, yy, x - 0.7, yy + s * 1.6, color, 0.25)
    lx = x - 2.0 if left else x + 2.0
    if left:
        TR(label, lx, (y1 + y2) / 2 - size * 0.35, size, color)
    else:
        T(label, lx, (y1 + y2) / 2 - size * 0.35, size, color)


# ==================== 页眉 / 标题栏 ====================
RECT(6, 6, PW - 12, PH - 12, GRAY, 0.4)
LN(6, 274, PW - 6, 274, BLUE, 0.7)
T("ESP32-S3 LCD 全覆盖显示屏外壳  ·  三视图", 12, 282, 15, BLUE)
TR("Rev I   /   A3 横向   /   单位 mm   /   图示比例 1.6 : 1   /   2026-11-08",
   PW - 12, 283, 8, GRAY)
T("顶板完整封闭、不透明，无 U 形镂空；天线让位仅在上边侧壁。尺寸数字为实物 mm，与图示比例无关。",
   12, 266, 7.4, INK)

# 标题栏
LN(6, 20, PW - 6, 20, INK, 0.5)
for xx in (170, 250, 320, 375):
    LN(xx, 6, xx, 20, GRAY, 0.3)
T("图名：全覆盖外壳 三视图（正 / 上 / 右 + 辅助下视图）", 10, 12.5, 7.5, INK)
T("图号：ESP32S3-LCD-EN-I-VIEW", 174, 12.5, 7, INK)
T("版本：Rev I", 254, 12.5, 7, INK)
T("材料：绝缘非金属", 324, 12.5, 7, INK)
T("第 1 / 1 页", 379, 12.5, 7, GRAY)


# ==================== 1. 正视图（屏幕正面 / 从 +Z 看） ====================
FX, FY = 28.0, 148.0
FW, FH = W * S, H * S
T("① 正视图（屏幕正面 / 从 +Z 看）  1.6 : 1", FX, 260, 9, BLUE)
RR(FX, FY, FW, FH, G["R_OUT"] * S, INK, 0.65, fill=PALE)
# PCB 参考
RR(FX + G["OX"] * S, FY + G["OY"] * S, G["PCB_PY"] * S, G["PCB_PX"] * S,
   G["PCB_R"] * S, GRAY, 0.3, dash=(2, 1.5))
# 显示窗
wx, wy, ww, wh = WIN[0], WIN[1], G["WIN_W"], G["WIN_H"]
RR(FX + wx * S, FY + wy * S, ww * S, wh * S, G["WIN_R"] * S,
   REDC, 0.75, fill=WINF)
TC("显示区窗口 AA", FX + (wx + ww / 2) * S, FY + (wy + wh / 2) * S + 3, 8, REDC)
TC(f"{ww:.2f} × {wh:.2f}（A.A + 让位）", FX + (wx + ww / 2) * S,
   FY + (wy + wh / 2) * S - 3, 7, REDC)
TC("四周各放大 0.5，不切亮区", FX + (wx + ww / 2) * S,
   FY + (wy + wh / 2) * S - 10, 6.5, GRAY)
# 侧壁让位窗投影（靠上边窄条）
RECT(FX + AX0 * S, FY + AY0 * S, (AX1 - AX0) * S, (AY1 - AY0) * S,
     BLUE, 0.55, fill=ANTF, dash=(2, 1.2))
TC("侧壁让位窗", FX + (AX0 + AX1) / 2 * S, FY + AY0 * S + 0.4, 4.6, BLUE)
# 2 段 I2C 合并宽窗投影（4 个座，段间 2.00 加强筋）
for a, b in G["I2C_GROUPS"]:
    RECT(FX + a * S, FY + (H - 1.6) * S, (b - a) * S, 1.6 * S,
         GREEN, 0.45, fill=GRNF)
# 复位孔 + 顶板一体成型接口凸字
CIRCLE(FX + RST[0] * S, FY + RST[1] * S, RSTD / 2 * S,
       REDC, 0.6, fill=WINF)
MARKS(FX, FY, S)
# 孔标注移到左侧，避免与凸字 "RST" 叠字
T("Φ4 孔", FX + (RST[0] - 14) * S, FY + (RST[1] - 1.5) * S - 2, 5.6, REDC)
# 4 个四角连接柱（隐藏线）
for x, y in SCREW_POS:
    CIRCLE(FX + x * S, FY + y * S, G["POST_D"] / 2 * S, BLUE, 0.4, dash=(1.5, 1))
    CIRCLE(FX + x * S, FY + y * S, 1.3 * S, BLUE, 0.4)
    px, py = FX + x * S, FY + y * S
    LN(px - 5, py, px + 5, py, GRAY, 0.2)
    LN(px, py - 5, px, py + 5, GRAY, 0.2)
# 剖切标记 A-A
LN(FX - 7, FY + H / 2 * S, FX, FY + H / 2 * S, BLUE, 0.5)
LN(FX + FW, FY + H / 2 * S, FX + FW + 7, FY + H / 2 * S, BLUE, 0.5)
T("A", FX - 10, FY + H / 2 * S + 1, 8, BLUE)
T("A", FX + FW + 8, FY + H / 2 * S + 1, 8, BLUE)
# 尺寸
DIMH(FX, FX + FW, FY - 10, f"{W:.2f}")
DIMV(FY, FY + FH, FX - 11, f"{H:.2f}")
# 窗口尺寸 69.00 × 47.60 已标在窗内，避免与主视图标题挤在同一行
DIMV(FY + wy * S, FY + (wy + wh) * S, FX + FW + 9, f"{wh:.2f}", left=False)
# 四角柱距 104.20 × 66.00 见右侧关键尺寸表；此处不再画竖向标注，
# 右对齐的中文标签会越出 A3 左边界被裁切（与外形 73.00 标注也会挤在同一行）。
# 虚线含义见右下「图例」，此处不重复（会被后绘制的上视图盖住）


# ==================== 2. 上视图（从天线侧 / +Yo 看） ====================
TX, TY = 28.0, 100.0
TH = HT * S
T("② 上视图（从天线侧 / +Yo 看，沿 -Yo）", TX, 131, 9, BLUE)
RECT(TX, TY, FW, TH, INK, 0.65, fill=PALE)
# 分层：底座 / 侧壁 / 顶板
RECT(TX, TY, FW, TB * S, INK, 0.4, fill=SIDE)
RECT(TX, TY + ZTI * S, FW, TTI * S, INK, 0.4, fill=SIDE)
LN(TX, TY + ZTI * S, TX + FW, TY + ZTI * S, INK, 0.4)
LN(TX, TY + TB * S, TX + FW, TY + TB * S, INK, 0.3)
# 顶板连续完整（再描一条强调线）
LN(TX, TY + HT * S + 1.2, TX + FW, TY + HT * S + 1.2, GREEN, 0.9)
TC("顶板连续完整 · 无镂空", TX + FW / 2,
   TY + ZTI * S + TTI * S / 2 - 1.0, 5.2, GREEN)
# I2C 窗
for x0, x1, z0, z1, n in TOP_SLOTS:
    RECT(TX + x0 * S, TY + z0 * S, (x1 - x0) * S, (z1 - z0) * S,
         GREEN, 0.45, fill=GRNF)
# 天线让位窗
RECT(TX + AX0 * S, TY + AZ0 * S, (AX1 - AX0) * S, (AZ1 - AZ0) * S,
     BLUE, 0.6, fill=ANTF)
TC("27.00 天线让位窗", TX + (AX0 + AX1) / 2 * S,
   TY + (AZ0 + AZ1) / 2 * S - 1.8, 6, BLUE)
T(f"统一开口带 Z {AZ0:.2f}~{AZ1:.2f}", TX + AX0 * S + 1,
  TY + AZ1 * S - 4.5, 5.5, BLUE)
T("2 段 I2C 合并宽窗（4 座）", TX + 13, TY + TB * S + 2, 5.8, GREEN)
# 尺寸
# 外形 111.20 已在正视图标注，此处不重复
DIMV(TY, TY + TH, TX - 11, f"{HT:.2f} 总高")
# 27.00 已标在让位窗内与右侧关键尺寸表，避免与上视图标题同行
DIMV(TY + ZTI * S, TY + HT * S, TX + FW + 8, f"{TTI:.2f} 顶板", left=False)
# 该说明已并入右下「三视图读图说明」，此处不再重复以免与辅助视图标题相挤


# ==================== 3. 辅助下视图（接口侧 / -Yo 看） ====================
BX, BY = 28.0, 60.0
T("③ 辅助下视图（接口侧 / -Yo 看）  —— 补充第 2 视图看不到的双 Type-C", BX, 91, 8.2, BLUE)
RECT(BX, BY, FW, TH, INK, 0.65, fill=PALE)
RECT(BX, BY, FW, TB * S, INK, 0.4, fill=SIDE)
RECT(BX, BY + ZTI * S, FW, TTI * S, INK, 0.4, fill=SIDE)
LN(BX, BY + ZTI * S, BX + FW, BY + ZTI * S, INK, 0.4)
LN(BX, BY + TB * S, BX + FW, BY + TB * S, INK, 0.3)
for x0, x1, z0, z1, n in BOT_SLOTS:
    RECT(BX + x0 * S, BY + z0 * S, (x1 - x0) * S, (z1 - z0) * S,
         GREEN, 0.45, fill=GRNF)
    TC(f"双 Type-C 窗 {x1-x0:.2f}", BX + (x0 + x1) / 2 * S,
       BY + (z0 + z1) / 2 * S - 1.8, 6, GREEN)
DIMH(BX, BX + FW, BY - 9, f"{W:.2f}")
T("顶板同样连续完整；横轴 Xo：左 = Xo 小端，右 = Xo 大端。",
  BX, BY - 18, 6.3, GRAY)


# ==================== 4. 右视图（从 +Xo 看） ====================
RX, RY = 225.0, 148.0
RW = H * S
T("④ 右视图（从 +Xo 看，沿 -Xo）", RX, 180, 9, BLUE)
RECT(RX, RY, RW, TH, INK, 0.65, fill=PALE)
RECT(RX, RY, RW, TB * S, INK, 0.4, fill=SIDE)
RECT(RX, RY + ZTI * S, RW, TTI * S, INK, 0.4, fill=SIDE)
LN(RX, RY + ZTI * S, RX + RW, RY + ZTI * S, INK, 0.4)
LN(RX, RY + TB * S, RX + RW, RY + TB * S, INK, 0.3)
for y0, y1, z0, z1, n in RGT_SLOTS:
    RECT(RX + y0 * S, RY + z0 * S, (y1 - y0) * S, (z1 - z0) * S,
         GREEN, 0.45, fill=GRNF)
    TC(f"{y1-y0:.2f}", RX + (y0 + y1) / 2 * S,
       RY + (z0 + z1) / 2 * S - 1.8, 5.6, GREEN)
T("5V Type-C", RX + G["RIGHT_SLOTS"][0][0] * S + 1, RY + TH + 3, 5.6, GREEN)
T("XH2.54-5P", RX + G["RIGHT_SLOTS"][1][0] * S + 1, RY + TH + 3, 5.6, GREEN)
DIMH(RX, RX + RW, RY - 9, f"{H:.2f}")
DIMV(RY, RY + TH, RX - 10, f"{HT:.2f}")
# 横轴方向说明已并入右下读图说明第 5~6 行


# ==================== 右上：方位示意 + 关键尺寸表 ====================
IX1, IX2 = 225.0, 337.0
T("视图方位示意（PCB 左旋 90°、天线朝上）", IX1, 262, 9, BLUE)
# 小壳体示意：四边标注 + 观察方向两行（不与页眉/标题同行）
SX, SY, SW, SH = IX1 + 6, 212, 92, 36
RR(SX, SY, SW, SH, 4, INK, 0.5, fill=PALE)
RR(SX + 8, SY + 6, SW - 16, SH - 12, 2, REDC, 0.5, fill=WINF)
TC("显示窗", SX + SW / 2, SY + SH / 2 - 1, 7, REDC)
RECT(SX + 32, SY + SH - 4, 28, 4, BLUE, 0.5, fill=ANTF)
T("上：天线让位窗 + I2C×4", SX + 2, SY + SH + 4, 5.8, BLUE)
T("下：双 Type-C", SX + 2, SY - 6, 5.8, INK)
T("右：5V / XH-5P", SX + 52, SY - 6, 5.8, INK)
T("左：封闭", SX - 17, SY + SH / 2, 5.8, GRAY)
T("① 从 +Z（屏幕正面）   ② 从 +Yo（天线侧）", IX1, 202, 5.8, GRAY)
T("④ 从 +Xo（右侧）   ③ 从 -Yo（接口侧，辅助）", IX1, 196, 5.8, GRAY)

T("关键尺寸 / 结构", IX2, 262, 9, BLUE)
specs = [
    (f"外形  {W:.2f} × {H:.2f} × {HT:.2f}   R{G['R_OUT']:.1f}", INK),
    (f"顶板 {TTI:.2f} / 侧壁 {G['T_WALL']:.2f} / 底板 {TB:.2f} / 内腔 {G['H_CAVITY']:.2f}", INK),
    (f"显示窗 {G['WIN_W']:.2f}×{G['WIN_H']:.2f} R{G['WIN_R']:.1f}（唯一版本）", REDC),
    (f"实测 A.A {G['LCD_AA_W']:.2f}×{G['LCD_AA_H']:.2f}，四周让位 {G['WIN_CLEAR_X']:.2f}/{G['WIN_CLEAR_Y']:.2f}", REDC),
    (f"窗口中心 X={G['WIN_CX']:.2f}/Y={G['WIN_CY']:.2f}，偏心屏左移 {-G['WIN_OFFSET_X']:.2f}", REDC),
    (f"顶板无镂空：仅显示窗 + Φ{RSTD:.1f} 复位孔；宁露黑边不切亮区", GREEN),
    (f"统一开口带 Z {AZ0:.2f}~{AZ1:.2f}（四边平齐）", BLUE),
    (f"上边：天线 {AX1-AX0:.2f} + I2C 合并宽窗 25.10/24.90", BLUE),
    (f"下边双 Type-C {G['DUAL_USBC'][1]-G['DUAL_USBC'][0]:.2f}；右边 18.00/23.00", GREEN),
    (f"PCB 四角 φ{G['PCB_HOLE_D']:.1f} 孔距 91.34 × 48.70（2 个对角有销）", INK),
    (f"四角柱距 {G['SCREW_POS'][2][0]-G['SCREW_POS'][0][0]:.2f} × "
     f"{G['SCREW_POS'][1][1]-G['SCREW_POS'][0][1]:.2f}；M3×12 ×4 不穿板", INK),
    (f"四角 Φ{G['POST_D']:.1f} 连接柱在 PCB 板框外；M3 不穿板", REDC),
    (f"PCB 由 2 个对角销定位（圆 Φ{G['LOCATOR_D']:.1f} + 菱形 {G['DIAMOND_W']:.2f}）", INK),
    ("另 2 个 φ4 孔空置；菱形销沿对角削扁吸收 0.31 mm 收缩", INK),
    (f"顶板凸字：USB / COM / Power / 5P / RST，高 {G['TEXT_SIZE']:.2f} 凸 {G['TEXT_RAISE']:.2f}", GREEN),
    ("凸字在显示窗外边框带，勿打磨/喷砂；不影响天线", INK),
    ("材料：PETG / 韧性树脂，绝缘非金属", INK),
]
for i, (s, col) in enumerate(specs):
    T("· " + s, IX2, 253 - i * 6.3, 6.4, col)


# ==================== 右下：读图说明 / 天线净空 / 图例 ====================
JX, JY = 225.0, 132.0
T("三视图读图说明", JX, JY, 9, BLUE)
notes = [
    "① 正视图 = 屏幕正面：只见显示窗 + Φ4 复位孔，顶板完整不透明；",
    "   窗口按实测 A.A 四周放大 0.5，宁露极窄黑边也不切亮区；已左移 2.75。",
    "② 上视图 = 从天线侧看：顶板整段连续；天线让位窗与 2 段",
    "   I2C 合并宽窗上下沿完全平齐（统一 Z 4.00~14.20）。",
    "④ 右视图 = 从右侧看：5V Type-C（18.00）与 XH2.54-5P（23.00）；",
    "   ③ 辅助下视图补双 Type-C 共用 36.00 窗；均含插线余量。",
    "各视图 1.6:1，尺寸数字为实物 mm；深灰实心字 = 顶板一体成型凸字。",
]
for i, s in enumerate(notes):
    T(s, JX, JY - 7 - i * 5.9, 6.3, INK)

T("天线净空 / 射频提示", JX, 82, 9, BLUE)
T("· 天线及 ESP32 模组端部经侧壁让位窗伸出壳外，不被壳体包住。", JX, 74, 6.3, INK)
T("· 核心板直焊，天线铜层约 Z 8~9，顶板内表面 Z 14.2，塑料间隙", JX, 68, 6.3, REDC)
T("  约 5 mm，介电加载更弱；装好后对比悬空 / 吸铁板 RSSI。", JX, 62, 6.3, REDC)
T("· 若 RSSI 掉 >3 dB：把天线端再多伸出 5~10 mm，或把顶板", JX, 56, 6.3, INK)
T("  天线区内表面减薄 0.8 mm（外表面仍平整、无洞）。", JX, 50, 6.3, INK)
T("· 4 连接柱距天线中心 >45 mm；近场 20 mm 内禁金属/覆铜。", JX, 44, 6.3, INK)

T("图例", JX, 35, 8.5, BLUE)
RECT(JX, 27, 7, 3.5, REDC, 0.4, fill=WINF); T("显示窗 / 复位孔", JX + 10, 28, 6.2, INK)
RECT(JX + 70, 27, 7, 3.5, GREEN, 0.4, fill=GRNF); T("接口开窗", JX + 80, 28, 6.2, INK)
RECT(JX + 130, 27, 7, 3.5, BLUE, 0.4, fill=ANTF); T("天线让位窗（仅侧壁）", JX + 140, 28, 6.2, INK)
LN(JX, 24, JX + 7, 24, GRAY, 0.35, dash=(2, 1.2)); T("虚线 = PCB 参考 / 四角连接柱隐藏线", JX + 10, 23.5, 6.2, INK)
T("深灰字 = 顶板凸字，勿打磨", JX + 70, 23.5, 6.2, INK)
RECT(JX + 130, 22.5, 7, 3.5, INK, 0.4, fill=SIDE); T("浅蓝 = 顶板 / 底板实体", JX + 140, 23.5, 6.2, INK)

c.save()
print("PDF:", PDF)


# ==================== DXF：1:1 三视图 ====================
d = ezdxf.new("R2010", setup=True)
d.header["$INSUNITS"] = 4
LAY = [("OUTLINE", 7), ("WINDOW", 1), ("HOLE", 1), ("PCB_REF", 8),
       ("DIM", 4), ("CENTER", 8), ("TEXT", 7), ("SLOT", 3), ("ANT", 5),
       ("SECTION", 5), ("TOPPLATE", 5), ("MARK", 6)]
for n, col in LAY:
    d.layers.new(n, dxfattribs={"color": col})
m = d.modelspace()


def dt(s, x, y, h=3.0, layer="TEXT"):
    m.add_text(s, dxfattribs={"layer": layer, "height": h, "insert": (x, y)})


def dl(p1, p2, layer="OUTLINE"):
    m.add_line(p1, p2, dxfattribs={"layer": layer})


def dr(x0, y0, x1, y1, layer="OUTLINE"):
    m.add_lwpolyline([(x0, y0), (x1, y0), (x1, y1), (x0, y1)],
                     close=True, dxfattribs={"layer": layer})


def dc(x, y, r, layer="CENTER"):
    m.add_circle((x, y), r, dxfattribs={"layer": layer})


def dh(x1, x2, y, label, off=0):
    yd = y + off
    dl((x1, yd), (x2, yd), "DIM"); dl((x1, y - 1.2), (x1, yd + 1.6), "DIM")
    dl((x2, y - 1.2), (x2, yd + 1.6), "DIM")
    dt(label, (x1 + x2) / 2 - len(label) * 0.9, yd + 1.5, 2.6, "DIM")


def dv(y1, y2, x, label, off=0):
    xd = x + off
    dl((xd, y1), (xd, y2), "DIM"); dl((x - 1.2, y1), (xd + 1.6, y1), "DIM")
    dl((x - 1.2, y2), (xd + 1.6, y2), "DIM")
    dt(label, xd - 2.2, (y1 + y2) / 2 - len(label) * 0.9, 2.6, "DIM")


def rr_dxf(x, y, w, h, r, layer="OUTLINE"):
    # 用多段线 + 圆弧近似圆角矩形（1:1）
    pts = [(x + r, y), (x + w - r, y), (x + w, y + r), (x + w, y + h - r),
           (x + w - r, y + h), (x + r, y + h), (x, y + h - r), (x, y + r)]
    m.add_lwpolyline(pts, close=True, dxfattribs={"layer": layer})
    for cx, cy, a0, a1 in [(x + r, y + r, 270, 360), (x + w - r, y + r, 0, 90),
                           (x + w - r, y + h - r, 90, 180), (x + r, y + h - r, 180, 270)]:
        m.add_arc((cx, cy), r, a0, a1, dxfattribs={"layer": layer})


# 正视图 1:1
rr_dxf(0, 0, W, H, G["R_OUT"])
rr_dxf(G["OX"], G["OY"], G["PCB_PY"], G["PCB_PX"], G["PCB_R"], "PCB_REF")
rr_dxf(wx, wy, ww, wh, G["WIN_R"], "WINDOW")
dr(AX0, AY0, AX1, AY1, "ANT")
dc(RST[0], RST[1], RSTD / 2, "HOLE")
# 顶板一体成型接口凸字（MARK 层，1:1 轮廓）
for item in G.get("TEXT_MARKS", []):
    for poly in item["polys"]:
        for ring in [poly["outer"]] + poly["holes"]:
            m.add_lwpolyline([(float(x), float(y)) for x, y in ring],
                             close=True, dxfattribs={"layer": "MARK"})
for x, y in SCREW_POS:
    dc(x, y, G["POST_D"] / 2, "CENTER")
    dl((x - 4.5, y), (x + 4.5, y), "CENTER"); dl((x, y - 4.5), (x, y + 4.5), "CENTER")
for a, b in G["I2C_GROUPS"]:
    dr(a, H - 1.6, b, H, "SLOT")
dh(0, W, 0, f"{W:.2f}", -10); dv(0, H, 0, f"{H:.2f}", -10)
dh(wx, wx + ww, H, f"{ww:.2f}", 8); dh(SCREW_POS[0][0], SCREW_POS[2][0], 0, "104.20 柱距", -19)
dt("① 正视图（屏幕正面 / +Z）  1:1   顶板完整无镂空", 0, H + 18, 3.4)
dt("蓝色 = 侧壁让位窗投影（顶板不开）；红色 = 显示窗；紫色 = 顶板凸字；Φ4 复位孔", 0, -27, 2.8)

# 上视图 1:1（放在 y=-45 起，z 映射到 y+（-45+z））
SY0 = -45.0
dr(0, SY0, W, SY0 + HT)
dr(0, SY0, W, SY0 + TB, "TOPPLATE")
dr(0, SY0 + ZTI, W, SY0 + HT, "TOPPLATE")
dl((0, SY0 + ZTI), (W, SY0 + ZTI), "TOPPLATE")
for x0, x1, z0, z1, n in TOP_SLOTS:
    dr(x0, SY0 + z0, x1, SY0 + z1, "SLOT")
dr(AX0, SY0 + AZ0, AX1, SY0 + AZ1, "ANT")
dh(0, W, SY0, f"{W:.2f}", -9); dv(SY0, SY0 + HT, 0, f"{HT:.2f}", -10)
dh(AX0, AX1, SY0 + HT, "27.00 让位窗", 8)
dt("② 上视图（天线侧 / +Yo）  1:1   顶板连续完整", 0, SY0 + HT + 18, 3.4)
dt(f"四边统一开口带 Z {AZ0:.2f}~{AZ1:.2f}；天线与 I2C 窗平齐；顶板 Z 14.2~16.0 不切断", 0, SY0 - 18, 2.8)

# 辅助下视图 1:1
BY0 = -90.0
dr(0, BY0, W, BY0 + HT)
dr(0, BY0, W, BY0 + TB, "TOPPLATE")
dr(0, BY0 + ZTI, W, BY0 + HT, "TOPPLATE")
dl((0, BY0 + ZTI), (W, BY0 + ZTI), "TOPPLATE")
for x0, x1, z0, z1, n in BOT_SLOTS:
    dr(x0, BY0 + z0, x1, BY0 + z1, "SLOT")
dh(0, W, BY0, f"{W:.2f}", -9)
dt("③ 辅助下视图（接口侧 / -Yo）  1:1   双 Type-C 共用窗 36.00", 0, BY0 + HT + 18, 3.4)

# 右视图 1:1（放在 x=130 起，横轴 Yo、纵轴 z）
RX0 = 130.0
dr(RX0, 0, RX0 + H, HT)
dr(RX0, 0, RX0 + H, TB, "TOPPLATE")
dr(RX0, ZTI, RX0 + H, HT, "TOPPLATE")
dl((RX0, ZTI), (RX0 + H, ZTI), "TOPPLATE")
for y0, y1, z0, z1, n in RGT_SLOTS:
    dr(RX0 + y0, z0, RX0 + y1, z1, "SLOT")
dh(RX0, RX0 + H, 0, f"{H:.2f}", -9); dv(0, HT, RX0, f"{HT:.2f}", -10)
dt("④ 右视图（+Xo）  1:1   横轴 Yo：左=下边，右=上边（天线侧）", RX0, HT + 18, 3.4)

dt("ESP32S3-LCD-EN-I-VIEW  Rev I  |  单位 mm  1:1  |  柱在板框外 / M3 不穿板 / 顶板凸字 / 2 对角定位销",
   0, -112, 3.6)
DXF = os.path.join(OUT, "ESP32S3_LCD_全覆盖外壳_三视图.dxf")
d.saveas(DXF)
print("DXF:", DXF)
