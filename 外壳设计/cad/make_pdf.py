# -*- coding: utf-8 -*-
"""生成 2 页 A4 可打印工程图 PDF"""
import os, math
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, Color
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "deliverables")
PDF = os.path.join(OUT, "ESP32S3_LCD_底座_工程图.pdf")
pdfmetrics.registerFont(TTFont("SimHei", r"C:\Windows\Fonts\simhei.ttf"))

W, L, R = 65.6, 103.8, 3.5
TW, TB, HW, HT = 1.6, 2.4, 4.2, 6.6
PCB_W, PCB_L = 61.8, 100.0
PX, PY = 1.9, 1.9
M3 = [(7.615, 97.58), (56.31, 97.58), (7.615, 6.24), (56.31, 6.24)]
MAG = [(18.0, 22.0), (47.6, 22.0), (18.0, 36.0), (47.6, 36.0)]

INK = HexColor("#1b2430")
DIMC = HexColor("#2f6db3")
REDC = HexColor("#c0392b")
GRAY = HexColor("#7b8794")
LIGHT = HexColor("#eef3f8")

c = canvas.Canvas(PDF, pagesize=(297 * mm, 210 * mm))
c.setTitle("ESP32S3_LCD 显示屏外壳 底座 工程图")
c.setAuthor("WorkBuddy")

def T(s, x, y, size=8, color=INK, font="SimHei"):
    c.setFont(font, size); c.setFillColor(color); c.drawString(x * mm, y * mm, s)

def TR(s, x, y, size=8, color=INK):
    c.setFont("SimHei", size); c.setFillColor(color); c.drawRightString(x * mm, y * mm, s)

def LN(x1, y1, x2, y2, color=INK, w=0.35, dash=None):
    c.setStrokeColor(color); c.setLineWidth(w)
    if dash: c.setDash(dash)
    c.line(x1 * mm, y1 * mm, x2 * mm, y2 * mm)
    if dash: c.setDash()

def RECT(x, y, w, h, color=INK, lw=0.35, fill=None, dash=None):
    if fill: c.setFillColor(fill); c.rect(x * mm, y * mm, w * mm, h * mm, stroke=0, fill=1)
    c.setStrokeColor(color); c.setLineWidth(lw)
    if dash: c.setDash(dash)
    c.rect(x * mm, y * mm, w * mm, h * mm, stroke=1, fill=0)
    if dash: c.setDash()

def RR(x, y, w, h, r, color=INK, lw=0.45, fill=None, dash=None):
    if fill: c.setFillColor(fill); c.roundRect(x * mm, y * mm, w * mm, h * mm, r * mm, stroke=0, fill=1)
    c.setStrokeColor(color); c.setLineWidth(lw)
    if dash: c.setDash(dash)
    c.roundRect(x * mm, y * mm, w * mm, h * mm, r * mm, stroke=1, fill=0)
    if dash: c.setDash()

def CIRCLE(x, y, r, color=INK, lw=0.35, dash=None):
    c.setStrokeColor(color); c.setLineWidth(lw)
    if dash: c.setDash(dash)
    c.circle(x * mm, y * mm, r * mm, stroke=1, fill=0)
    if dash: c.setDash()

def DIMH(x1, x2, y, label, off=0, color=DIMC, ext_from=None):
    yd = y + off
    ey = ext_from if ext_from is not None else y - 1.5
    LN(x1, yd, x2, yd, color, 0.3)
    LN(x1, ey, x1, yd + 2, color, 0.25)
    LN(x2, ey, x2, yd + 2, color, 0.25)
    for xx, s in ((x1, 1), (x2, -1)):
        c.setFillColor(color)
        p = c.beginPath(); p.moveTo(xx * mm, yd * mm)
        p.lineTo((xx + s * 1.8) * mm, (yd + 0.5) * mm)
        p.lineTo((xx + s * 1.8) * mm, (yd - 0.5) * mm); p.close()
        c.drawPath(p, stroke=0, fill=1)
    c.setFont("SimHei", 7.5); c.setFillColor(color)
    c.drawCentredString((x1 + x2) / 2 * mm, (yd + 2.2) * mm, label)

def DIMV(y1, y2, x, label, off=0, color=DIMC):
    xd = x + off
    LN(xd, y1, xd, y2, color, 0.3)
    LN(x - 1.5, y1, xd + 2, y1, color, 0.25)
    LN(x - 1.5, y2, xd + 2, y2, color, 0.25)
    for yy, s in ((y1, 1), (y2, -1)):
        c.setFillColor(color)
        p = c.beginPath(); p.moveTo(xd * mm, yy * mm)
        p.lineTo((xd + 0.5) * mm, (yy + s * 1.8) * mm)
        p.lineTo((xd - 0.5) * mm, (yy + s * 1.8) * mm); p.close()
        c.drawPath(p, stroke=0, fill=1)
    c.saveState(); c.translate((xd - 2.0) * mm, (y1 + y2) / 2 * mm)
    c.rotate(90); c.setFont("SimHei", 7.5); c.setFillColor(color)
    c.drawCentredString(0, 0, label); c.restoreState()

def TITLE(x, y, w=115):
    RECT(x, y, w, 26)
    LN(x, y + 8, x + w, y + 8, GRAY, 0.25)
    LN(x, y + 17, x + w, y + 17, GRAY, 0.25)
    LN(x + 78, y, x + 78, y + 17, GRAY, 0.25)
    T("ESP32S3_LCD 显示屏外壳 / 底座", x + 2, y + 20, 9)
    T("图号 ESP32S3-LCD-EN-A", x + 2, y + 11, 7)
    T("材料：绝缘非金属（PLA/PETG/树脂/亚克力）", x + 2, y + 3.5, 6.5)
    T("Rev A", x + 80, y + 11, 7)
    T("2026-11-07", x + 80, y + 3.5, 7)

# ==================== 第 1 页：俯视图 ====================
OX, OY = 52.0, 42.0
T("ESP32-S3 + 3.5\" TFTLCD 显示屏  底座外壳工程图", 12, 199, 12)
LN(12, 196.5, 285, 196.5, GRAY, 0.4)
T("第 1 页 / 共 2 页   底座俯视图 1:1", 12, 190, 8, GRAY)

RR(OX, OY, W, L, R, INK, 0.6)
# 侧壁内侧线（短边整段敞开，故不画闭合内腔框）
LN(OX + TW, OY, OX + TW, OY + L, INK, 0.5)
LN(OX + W - TW, OY, OX + W - TW, OY + L, INK, 0.5)
# PCB 参考
RR(OX + PX, OY + PY, PCB_W, PCB_L, 2.0, HexColor("#5a6b7b"), 0.45, dash=(2.5, 1.5))
for x, y in M3:
    CIRCLE(OX + x, OY + y, 1.6, REDC, 0.45)
    LN(OX + x - 2.6, OY + y, OX + x + 2.6, OY + y, GRAY, 0.2, dash=(1.5, 1))
    LN(OX + x, OY + y - 2.6, OX + x, OY + y + 2.6, GRAY, 0.2, dash=(1.5, 1))
for x, y in MAG:
    CIRCLE(OX + x, OY + y, 4.1, REDC, 0.45)
    LN(OX + x - 5.5, OY + y, OX + x + 5.5, OY + y, GRAY, 0.2, dash=(1.5, 1))
    LN(OX + x, OY + y - 5.5, OX + x, OY + y + 5.5, GRAY, 0.2, dash=(1.5, 1))
# 天线净空区
RECT(OX, OY + L, W, 20, REDC, 0.4, fill=HexColor("#fdf1ef"), dash=(2, 1.5))
T("ANT 天线净空区 ≥20 mm", OX + 2, OY + L + 14, 9, REDC)
T("外壳不覆盖、不延伸；禁止金属 / 磁体 / 覆铜", OX + 2, OY + L + 7, 7, REDC)
# 剖切 A-A
YSEC = 55.0
LN(OX - 7, OY + YSEC, OX, OY + YSEC, REDC, 0.5)
LN(OX + W, OY + YSEC, OX + W + 7, OY + YSEC, REDC, 0.5)
T("A", OX - 10, OY + YSEC + 1, 9, REDC); T("A", OX + W + 8, OY + YSEC + 1, 9, REDC)
# 尺寸
DIMH(OX, OX + W, OY, "65.60", -12)
DIMV(OY, OY + L, OX, "103.80", -12)
DIMH(OX + M3[0][0], OX + M3[1][0], OY + L, "48.70", 26, ext_from=OY + L + 21)
DIMV(OY + M3[2][1], OY + M3[0][1], OX + W, "91.34", 14)
DIMH(OX, OX + TW, OY, "1.60", -20)

# 右侧：图例 / BOM / 标题栏
BX = 168.0
T("图例与要求", BX, 185, 9.5)
LN(BX, 183, 285, 183, GRAY, 0.3)
CIRCLE(BX + 4, 177, 1.6, REDC); T("4×Φ3.2 通孔（M3），与 PCB 4×Φ4 孔同轴", BX + 10, 175, 7)
CIRCLE(BX + 4, 169, 3.0, REDC); T("4×Φ8.2 通孔，嵌 Φ8×2 钕铁硼磁铁", BX + 10, 167, 7)
LN(BX, 160, BX + 6, 160, GRAY, 0.3, dash=(2, 1.5)); T("PCB 参考轮廓 61.80×100.00 R2（虚线）", BX + 10, 158, 7)
T("外轮廓 65.60×103.80 R3.5 | 内腔宽 62.40 | 圆角 R2.5", BX, 150, 7)
T("底厚 2.40 | 侧壁 1.60 宽 × 4.20 高 | 总高 6.60", BX, 144, 7)
T("磁铁中心 (18,22) (47.6,22) (18,36) (47.6,36)", BX, 138, 7)
T("距天线端 ≥67 mm，全部位于非天线侧", BX, 132, 7, REDC)

T("明细表 BOM", BX, 122, 9.5)
rows = [["序号", "名称", "规格 / 材料", "数量"],
        ["1", "底座外壳", "PLA/PETG 或光敏树脂", "1"],
        ["2", "钕铁硼磁铁", "Φ8×2 mm N35", "4"],
        ["3", "M3 紧固件", "M3×8 螺丝 + 螺母", "4"],
        ["4", "硅胶脚垫", "Φ8×1.5 自粘（可选）", "4"]]
cols = [BX, BX + 9, BX + 27, BX + 88, BX + 117]
for i in range(len(rows) + 1):
    LN(BX, 119 - i * 6.5, BX + 117, 119 - i * 6.5, GRAY, 0.25)
for xx in cols:
    LN(xx, 119 - len(rows) * 6.5, xx, 119, GRAY, 0.25)
for i, row in enumerate(rows):
    for j, val in enumerate(row):
        T(val, cols[j] + 1.2, 119 - (i + 1) * 6.5 + 2.0, 6.8)
T("短边 A（天线侧）：整段敞开、无侧壁", BX, 78, 7.5, REDC)
T("短边 B（接口侧）：整段敞开，USB-C / Type-C 凸出不遮挡", BX, 72, 7.5, REDC)
TITLE(BX, 12, 117)
T("单位 mm   比例 1:1 / 2:1   未注公差按常规工艺", 12, 12, 7, GRAY)
c.showPage()

# ==================== 第 2 页：剖面与装配 ====================
T("ESP32-S3 + 3.5\" TFTLCD 显示屏  底座外壳工程图", 12, 199, 12)
LN(12, 196.5, 285, 196.5, GRAY, 0.4)
T("第 2 页 / 共 2 页   A-A 剖面 2:1 / 装配层叠示意 / 技术说明", 12, 190, 8, GRAY)

SX, SZ, SC = 28.0, 118.0, 2.0
def P(x, z): return (SX + x * SC, SZ + z * SC)
# U 形截面
pts = [(0, 0), (W, 0), (W, HT), (W - TW, HT), (W - TW, TB), (TW, TB), (TW, HT), (0, HT)]
c.setFillColor(LIGHT); c.setStrokeColor(INK); c.setLineWidth(0.6)
pth = c.beginPath(); pth.moveTo(*(v * mm for v in P(*pts[0])))
for q in pts[1:]: pth.lineTo(*(v * mm for v in P(*q)))
pth.close(); c.drawPath(pth, stroke=1, fill=1)
# 剖面线
c.setStrokeColor(GRAY); c.setLineWidth(0.2)
for x in range(0, int(W * SC), 5):
    xx = SX + x
    c.line(xx * mm, SZ * mm, min(xx + 3.5, SX + W * SC) * mm, (SZ + min(3.5, (W * SC - x)) * 0.7) * mm)
# PCB 截面
z0 = TB + 0.4
RECT(SX + PX * SC, SZ + z0 * SC, PCB_W * SC, 1.6 * SC, INK, 0.4, fill=HexColor("#d7e6d0"))
T("PCB t=1.6", SX + 30 * SC, SZ + (z0 + 0.4) * SC, 6.5)
# 尺寸
DIMV(SZ, SZ + TB * SC, SX, "2.40", -9)
DIMV(SZ + TB * SC, SZ + HT * SC, SX, "4.20", -9)
DIMV(SZ, SZ + HT * SC, SX, "6.60", -19)
DIMH(SX + TW * SC, SX + (W - TW) * SC, SZ, "62.40", -9)
DIMH(SX, SX + W * SC, SZ, "65.60", -18)
T("A-A 剖面 2:1（剖面线仅示意外壳本体）", SX, SZ + 10 * SC, 8.5)

# 装配层叠示意
AX, AY, ASC = 28.0, 48.0, 2.0
def Q(x, z): return (AX + x * ASC, AY + z * ASC)
RECT(Q(0, 0)[0], Q(0, 0)[1], W * ASC, TB * ASC, INK, 0.4, fill=LIGHT)
RECT(Q(0, TB)[0], Q(0, TB)[1], TW * ASC, HW * ASC, INK, 0.4, fill=LIGHT)
RECT(Q(W - TW, TB)[0], Q(W - TW, TB)[1], TW * ASC, HW * ASC, INK, 0.4, fill=LIGHT)
T("底壳 6.6", Q(3, 0.8)[0], Q(3, 0.8)[1], 6)
zpcb = TB + 0.4
RECT(Q(PX, zpcb)[0], Q(PX, zpcb)[1], PCB_W * ASC, 1.6 * ASC, INK, 0.4, fill=HexColor("#d7e6d0"))
T("PCB 61.8×100", Q(20, zpcb + 0.3)[0], Q(20, zpcb + 0.3)[1], 6)
zesp = zpcb + 4.5
RECT(Q(PX + 6, zesp)[0], Q(PX + 6, zesp)[1], (PCB_W - 12) * ASC, 2.0 * ASC, INK, 0.4, fill=HexColor("#f6dfc8"))
T("ESP32 系统板", Q(20, zesp + 0.5)[0], Q(20, zesp + 0.5)[1], 6)
# 天线外伸
RECT(Q(-7, zesp)[0], Q(-7, zesp)[1], 7 * ASC, 2.0 * ASC, REDC, 0.5, fill=HexColor("#fbe9e7"), dash=(1.5, 1))
T("天线外伸", AX - 14, Q(0, zesp + 0.4)[1], 6, REDC)
zlcd = zesp + 6.0
RECT(Q(PX + 2, zlcd)[0], Q(PX + 2, zlcd)[1], (PCB_W - 4) * ASC, 3.0 * ASC, INK, 0.4, fill=HexColor("#d9e6f5"))
T("3.5\" LCD 模块（插装于 PCB）", Q(20, zlcd + 0.8)[0], Q(20, zlcd + 0.8)[1], 6)
T("装配层叠示意 2:1（仅外壳本体为剖面，其余为外形示意）", AX, AY + 22 * ASC, 8.5)

# 技术说明
NX = 178.0
T("技术说明", NX, 185, 10)
LN(NX, 183, 285, 183, GRAY, 0.3)
notes = [
    "1. 外壳仅包覆 PCB 本体；LCD 屏与 ESP32 系统板",
    "   均位于壳体之外，不做上盖。",
    "2. 两条短边整段敞开、不设侧壁：一端为天线",
    "   敞口，另一端为 USB-C / Type-C 接口敞口。",
    "   天线实际在另一端时，将本图上下镜像使用。",
    "3. 天线投影 20 mm 范围内禁止金属件、磁铁、",
    "   覆铜及任何遮挡物；PCB 该区域应做净空。",
    "4. 4 片磁铁仅布置于非天线端，距天线 ≥67 mm；",
    "   若吸在铁质表面，天线宜朝外或悬出边缘。",
    "5. 壳体必须为绝缘非金属材料（PLA / PETG /",
    "   光敏树脂 / 亚克力），禁止金属漆与镀层。",
    "6. 4×Φ3.2 通孔配 M3 螺丝固定 PCB；4×Φ8.2",
    "   通孔嵌 Φ8×2 磁铁，点胶固定后贴脚垫遮蔽。",
    "7. 未注尺寸公差按 3D 打印 / 激光切割常规工艺；",
    "   本图为项目设计图，不作 GB/ISO 符合性声明。",
]
for i, s in enumerate(notes):
    T(s, NX, 176 - i * 5.6, 7, REDC if i in (2, 3, 6, 7, 8) else INK)
T("加工提示", NX, 88, 9.5)
LN(NX, 86, 285, 86, GRAY, 0.3)
for i, s in enumerate([
    "3D 打印：发 STL，PLA/PETG 或光敏树脂，",
    "实体体积约 17 cm³，底面平放无支撑。",
    "激光切割：发 DXF（1:1，单位 mm），3 mm",
    "亚克力底板 + 两条长边条粘接，短边不加框。",
    "CNC：发 STL + PDF，材料选 POM/ABS，勿用铝。",
]):
    T(s, NX, 80 - i * 6.2, 7)
TITLE(NX, 12, 107)
T("单位 mm   比例 1:1 / 2:1   2026-11-07", 28, 12, 7, GRAY)
c.save()
print("PDF:", PDF)
