# -*- coding: utf-8 -*-
"""ESP32S3_LCD 全覆盖外壳 Rev E —— 3 页 A4 横向工程图 PDF"""
import os, json, math
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

HERE = os.path.dirname(os.path.abspath(__file__))
G = json.load(open(os.path.join(HERE, "geom_v2.json"), encoding="utf-8"))
PDF = os.path.join(HERE, "deliverables", "ESP32S3_LCD_全覆盖外壳_工程图.pdf")
pdfmetrics.registerFont(TTFont("SimHei", r"C:\Windows\Fonts\simhei.ttf"))

INK = HexColor("#1b2430")
DIMC = HexColor("#2f6db3")
REDC = HexColor("#c0392b")
GRAY = HexColor("#7b8794")
LIGHT = HexColor("#eef3f8")
BLUE = HexColor("#1f4e79")
GREEN = HexColor("#2e7d52")
PALE = HexColor("#f7fafc")

c = canvas.Canvas(PDF, pagesize=(297 * mm, 210 * mm))
c.setTitle("ESP32S3_LCD 全覆盖显示屏外壳 工程图 Rev E")
c.setAuthor("WorkBuddy")


def T(s, x, y, size=8, color=INK, font="SimHei"):
    c.setFont(font, size); c.setFillColor(color); c.drawString(x * mm, y * mm, str(s))


def TR(s, x, y, size=8, color=INK):
    c.setFont("SimHei", size); c.setFillColor(color); c.drawRightString(x * mm, y * mm, str(s))


def LN(x1, y1, x2, y2, color=INK, w=0.35, dash=None):
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


def CIRCLE(x, y, r, color=INK, lw=0.35, dash=None, fill=None):
    if fill:
        c.setFillColor(fill); c.circle(x * mm, y * mm, r * mm, stroke=0, fill=1)
    c.setStrokeColor(color); c.setLineWidth(lw)
    if dash: c.setDash(dash)
    c.circle(x * mm, y * mm, r * mm, stroke=1, fill=0)
    if dash: c.setDash()


def DIMH(x1, x2, y, label, color=DIMC, size=7):
    LN(x1, y, x2, y, color, 0.3)
    LN(x1, y - 1.5, x1, y + 1.5, color, 0.25)
    LN(x2, y - 1.5, x2, y + 1.5, color, 0.25)
    T(label, (x1 + x2) / 2 - len(label) * size * 0.27, y + 2.2, size, color)


def DIMV(y1, y2, x, label, color=DIMC, size=7, label_on="right"):
    LN(x, y1, x, y2, color, 0.3)
    LN(x - 1.5, y1, x + 1.5, y1, color, 0.25)
    LN(x - 1.5, y2, x + 1.5, y2, color, 0.25)
    yy = (y1 + y2) / 2 - size * 0.35
    if label_on == "left":
        TR(label, x - 2.2, yy, size, color)
    else:
        T(label, x + 2.2, yy, size, color)


def HEADER(title, page):
    c.setFillColor(BLUE); c.rect(0, 196 * mm, 297 * mm, 14 * mm, stroke=0, fill=1)
    T(title, 8, 200.5, 11, HexColor("#ffffff"))
    TR(f"Rev E   {page}/3   2026-11-08   单位 mm", 289, 200.5, 8, HexColor("#dce8f5"))


def FOOTER(note):
    LN(8, 8.5, 289, 8.5, GRAY, 0.3)
    T(note, 8, 4.5, 6.5, GRAY)
    TR("图号 ESP32S3-LCD-EN-E", 289, 4.5, 6.5, GRAY)


W, H = G["W"], G["H"]
WIN = G["WIN_A"]
ANT = G["ANT"]
HOLES = [tuple(h) for h in G["HOLES"]]


# ================= 页 1：上盖俯视 =================
HEADER("页 1  上盖俯视图  ·  顶板完整无镂空 / 仅开显示区窗口", 1)
OX, OY, SC = 30.0, 92.0, 1.0

def P(x, y): return (OX + x * SC, OY + y * SC)

RR(OX, OY, W, H, G["R_OUT"], INK, 0.6, fill=PALE)
# PCB 参考
RR(P(G["OX"], G["OY"])[0], P(G["OX"], G["OY"])[1], G["PCB_PY"], G["PCB_PX"],
   G["PCB_R"], GRAY, 0.3, dash=(2, 1.5))
# 显示窗
wx, wy, ww, wh = WIN[0], WIN[1], G["WIN_A_W"], G["WIN_A_H"]
RR(P(wx, wy)[0], P(wx, wy)[1], ww, wh, G["WIN_R"], REDC, 0.7, fill=HexColor("#ffffff"))
T("显示区窗口 AA", P(wx + 3, wy + wh / 2)[0], P(wx + 3, wy + wh / 2)[1], 7, REDC)
T("屏幕黑边被顶板压住", P(wx + 3, wy + wh / 2 - 5)[0],
  P(wx + 3, wy + wh / 2 - 5)[1], 6, GRAY)
# 侧壁天线让位窗（俯视投影为靠上边窄条；顶板完整不开洞）
ax0, ay0, ax1, ay1 = ANT
RECT(P(ax0, ay0)[0], P(ax0, ay0)[1], ax1 - ax0, ay1 - ay0,
     BLUE, 0.5, fill=HexColor("#e6eff9"), dash=(2, 1.2))
# 该窄条由上方 27.00 尺寸线与右侧图例说明，视图内不再加文字以免与复位孔标注相叠
# 顶板复位键孔
CIRCLE(*P(*G["RESET_POS"]), G["RESET_HOLE_D"] / 2, REDC, 0.6,
       fill=HexColor("#ffffff"))
T("Φ4 复位孔", P(G["RESET_POS"][0] + 3, G["RESET_POS"][1] - 2.2)[0],
  P(G["RESET_POS"][0] + 3, G["RESET_POS"][1] - 2.2)[1], 5.6, REDC)
# 4 螺丝柱
for x, y in HOLES:
    CIRCLE(*P(x, y), G["POST_D"] / 2, BLUE, 0.4, dash=(1.5, 1))
    CIRCLE(*P(x, y), 1.3, BLUE, 0.4)
    px, py = P(x, y)
    LN(px - 4.5, py, px + 4.5, py, GRAY, 0.2)
    LN(px, py - 4.5, px, py + 4.5, GRAY, 0.2)
# 关键器件
for name, (x, y) in G["PARTS"].items():
    px, py = P(x, y)
    CIRCLE(px, py, 0.9, GRAY, 0.3, fill=HexColor("#cfd8e3"))
# 4 个 I2C 开口标记
for i, cx in enumerate(G["I2C_X"], 1):
    RECT(P(cx - G["I2C_SLOT_W"] / 2, H - 1.6)[0], P(cx - G["I2C_SLOT_W"] / 2, H - 1.6)[1],
         G["I2C_SLOT_W"], 1.6, GREEN, 0.5, fill=HexColor("#e4f3ea"))
# 剖切线
LN(OX - 6, P(0, G["H"] / 2)[1], OX, P(0, G["H"] / 2)[1], BLUE, 0.5)
LN(OX + W, P(0, G["H"] / 2)[1], OX + W + 6, P(0, G["H"] / 2)[1], BLUE, 0.5)
T("A", OX - 8, P(0, G["H"] / 2)[1] + 1, 8, BLUE)
T("A", OX + W + 6.5, P(0, G["H"] / 2)[1] + 1, 8, BLUE)
# 尺寸
DIMH(OX, OX + W, OY - 8, f"{W:.2f}")
DIMV(OY, OY + H, OX - 9, f"{H:.2f}")
DIMH(P(wx, 0)[0], P(wx + ww, 0)[0], OY + H + 6, f"{G['WIN_A_W']:.2f} (A版窗口)")
DIMV(P(0, wy)[1], P(0, wy + wh)[1], OX + W + 8, f"{G['WIN_A_H']:.2f}")
DIMH(P(ax0, 0)[0], P(ax1, 0)[0], OY + H + 14,
     f"{ax1-ax0:.2f} 侧壁让位窗（顶板不开）", BLUE)
DIMH(P(HOLES[0][0], 0)[0], P(HOLES[1][0], 0)[0], OY - 15, "91.34 孔距")
DIMV(P(0, HOLES[0][1])[1], P(0, HOLES[2][1])[1], OX - 16, "48.70")
T("上盖俯视 1:1（窗口按 A 版）", OX, OY - 22, 9, INK)
T("虚线 = PCB 参考轮廓 61.80×100.00 R2 / 蓝色虚线圆 = Φ7 螺丝柱位", OX, 10.5, 6.5, GRAY)

# 右侧信息区
IX = 158.0
T("A / B 版窗口对照", IX, 184, 9, BLUE)
rows = [["版本", "窗口尺寸", "依据", "适用"],
        ["A", "69.00 × 47.60", "EDA封装可视框 70.46×49.07", "≤70.46"],
        ["B", "72.00 × 47.60", "通用 AA 73.44×48.96", "≈73.44"]]
colx = [IX, IX + 14, IX + 42, IX + 110]
for r, row in enumerate(rows):
    y = 176 - r * 7
    RECT(IX, y - 2, 132, 7, GRAY, 0.25, fill=(LIGHT if r == 0 else None))
    for j, v in enumerate(row):
        T(v, colx[j] + 1, y, 6.3 if r else 6.8, INK if r else BLUE)
T("打样前先点亮屏幕、量「发光区」宽高，再选 A 或 B 版 STL。", IX, 152, 6.8, REDC)
T("其余几何两版完全相同；底座通用。", IX, 146.5, 6.8, INK)

T("四边接口开窗（PCB 左旋 90°、天线朝上的正视图）", IX, 137, 8.5, BLUE)
info = [
    ("上边", "侧壁让位窗 27.00（Z 8.0~14.2）+ Φ4 复位孔 + 4× I2C", REDC),
    ("下边", "ESP32 系统板双 Type-C 共用 26.00 长窗", INK),
    ("右边", "5V Type-C 输出 + XH2.54-5P（兼容 2P/3P）", INK),
    ("左边", "封闭，无外部接口", GRAY),
    ("底部", "4× M3 沉孔，从底面拧紧", INK),
]
for i, (k, v, col) in enumerate(info):
    y = 129 - i * 7.2
    T(k, IX, y, 7, BLUE)
    T(v, IX + 13, y, 6.5, col)

T("关键尺寸 / 结构", IX, 88, 8.5, BLUE)
specs = [
    f"外形 {W:.2f} × {H:.2f} × {G['H_TOTAL']:.2f}，外圆角 R{G['R_OUT']:.1f}",
    f"顶板厚 {G['T_TOP']:.2f} / 侧壁厚 {G['T_WALL']:.2f} / 内腔净高 {G['H_CAVITY']:.2f}",
    f"窗口 {G['WIN_A_W']:.2f}×{G['WIN_A_H']:.2f} R{G['WIN_R']:.1f}；黑边左右约 4.96、上下约 3.73",
    "顶板完整无镂空：仅显示窗 + Φ4 复位孔；侧壁留 27.00 让位窗",
    "4× Φ7 螺丝柱，内底孔 Φ2.6（M3 自攻，盲孔）",
    "PCB 4× φ4 安装孔距 91.34 × 48.70，与柱同轴",
    "壳体内缘距 PCB 1.00 间隙；材料绝缘非金属",
]
for i, s in enumerate(specs):
    T("· " + s, IX, 81 - i * 6.6, 6.6, INK)

T("图例", IX, 30, 8, BLUE)
CIRCLE(IX + 3, 24, 2, BLUE, 0.4, dash=(1.5, 1)); T("螺丝柱位 Φ7", IX + 8, 22.5, 6.4, INK)
RECT(IX, 16, 6, 3, GREEN, 0.4, fill=HexColor("#e4f3ea")); T("I2C 侧壁开窗", IX + 8, 17, 6.4, INK)
RECT(IX + 55, 16, 6, 3, BLUE, 0.4, fill=HexColor("#e6eff9")); T("侧壁让位窗", IX + 63, 17, 6.4, INK)
FOOTER("注：本页窗口按 A 版绘制；B 版仅窗口长度 72.00 不同。屏幕可视区尺寸请以实物实测为准。")


# ================= 页 2：底座 + 剖面 =================
c.showPage()
HEADER("页 2  底座俯视图 / A-A 剖面 / 装配层叠", 2)
BX, BY = 30.0, 105.0
RR(BX, BY, W, H, G["R_OUT"], INK, 0.6, fill=PALE)
RR(BX + G["OX"], BY + G["OY"], G["PCB_PY"], G["PCB_PX"], G["PCB_R"],
   GRAY, 0.3, dash=(2, 1.5))
for x, y in HOLES:
    CIRCLE(BX + x, BY + y, G["SCREW_HOLE_D"] / 2, REDC, 0.6)
    CIRCLE(BX + x, BY + y, G["SCREW_CS_D"] / 2, BLUE, 0.4, dash=(1.5, 1))
    CIRCLE(BX + x, BY + y, G["POST_D"] / 2, GRAY, 0.3, dash=(1, 1))
    LN(BX + x - 5, BY + y, BX + x + 5, BY + y, GRAY, 0.2)
    LN(BX + x, BY + y - 5, BX + x, BY + y + 5, GRAY, 0.2)
DIMH(BX, BX + W, BY - 8, "105.20")
DIMV(BY, BY + H, BX - 9, "67.00")
DIMH(BX + HOLES[0][0], BX + HOLES[1][0], BY - 15, "91.34 孔距")
DIMV(BY + HOLES[0][1], BY + HOLES[2][1], BX - 16, "48.70")
T("底座俯视 1:1", BX, BY - 22, 9, INK)
T("红实线 Φ3.4 通孔 / 蓝虚线 Φ6.5 沉孔 / 灰虚线 Φ7 支撑台",
  BX, BY - 28, 6.3, GRAY)

# 右侧 BOM
IX = 158.0
T("明细表 BOM", IX, 184, 9, BLUE)
bom = [["序", "名称", "规格 / 材料", "数量"],
       ["1", "上盖", "PLA/PETG 或光敏树脂，不透明绝缘", "1"],
       ["2", "底座", "同上", "1"],
       ["3", "M3 自攻螺丝", "M3×12 沉头 304 不锈钢", "4"],
       ["4", "硅胶脚垫", "Φ8×1.5 自粘（可选）", "4"]]
cx = [IX, IX + 10, IX + 28, IX + 108]
for r, row in enumerate(bom):
    y = 176 - r * 7.5
    RECT(IX, y - 2, 126, 7.5, GRAY, 0.25, fill=(LIGHT if r == 0 else None))
    for j, v in enumerate(row):
        T(v, cx[j] + 1, y, 6.3 if r else 6.8, INK if r else BLUE)
T("紧固件路径（自下而上）", IX, 128, 8.5, BLUE)
T("底面 Φ6.5 深 1.6 沉孔 → Φ3.4 通孔 → PCB φ4 孔", IX, 121, 6.6, INK)
T("→ 上盖 Φ7 柱内 Φ2.6 自攻底孔（盲孔深至 Z=13.8）", IX, 115, 6.6, INK)
T("M3×12 沉头螺丝，拧入塑料柱约 7mm，勿过紧", IX, 109, 6.6, INK)
T("靠 4 颗 M3 螺丝固定；φ4 为 M3 加大过孔，非 M4", IX, 100, 6.6, GREEN)

# A-A 剖面 2:1
SX, SZ, SCL = 30.0, 20.0, 1.5
def SP(x, z): return (SX + x * SCL, SZ + z * SCL)
T("A-A 剖面 1.5:1（沿显示窗中心横剖，见页 1）", SX, 70, 9, BLUE)
T(f"装配层叠 Z（自外壳底面算起，mm）：PCB 底面 {G['Z_PCB_BOT']:.2f} → PCB 顶面 {G['Z_PCB_TOP']:.2f} → LCD 顶面 12.10",
  SX, 64, 6.6, INK)
T(f"→ ESP32 顶面 13.10 → 顶板内表面 {G['Z_TOP_IN']:.2f}；内腔净高 {G['H_CAVITY']:.2f}，顶部留 1.10 间隙",
  SX, 58.5, 6.6, INK)


def poly_path(pts, fillc):
    c.setFillColor(fillc); c.setStrokeColor(INK); c.setLineWidth(0.5)
    p = c.beginPath()
    p.moveTo(pts[0][0] * mm, pts[0][1] * mm)
    for q in pts[1:]:
        p.lineTo(q[0] * mm, q[1] * mm)
    p.close(); c.drawPath(p, stroke=1, fill=1)


# 上盖剖面：窗口处断开，形成左 / 右两块 U 形截面
poly_path([SP(0, G["T_BASE"]), SP(G["T_WALL"], G["T_BASE"]),
           SP(G["T_WALL"], G["Z_TOP_IN"]), SP(WIN[0], G["Z_TOP_IN"]),
           SP(WIN[0], G["H_TOTAL"]), SP(0, G["H_TOTAL"])], HexColor("#dce6f0"))
poly_path([SP(WIN[2], G["H_TOTAL"]), SP(WIN[2], G["Z_TOP_IN"]),
           SP(W - G["T_WALL"], G["Z_TOP_IN"]), SP(W - G["T_WALL"], G["T_BASE"]),
           SP(W, G["T_BASE"]), SP(W, G["H_TOTAL"])], HexColor("#dce6f0"))
# 显示窗断口标注
T("显示窗", SP(WIN[0], G["H_TOTAL"])[0] + 3, SP(WIN[0], G["H_TOTAL"])[1] + 2.5, 6, REDC)
# 底座
RECT(SX, SZ, W * SCL, G["T_BASE"] * SCL, INK, 0.5, fill=HexColor("#c9d6e3"))
# 螺丝中心线
LN(*SP(HOLES[0][0], 0), *SP(HOLES[0][0], G["H_TOTAL"]), REDC, 0.3, dash=(2, 1.5))
LN(*SP(HOLES[1][0], 0), *SP(HOLES[1][0], G["H_TOTAL"]), REDC, 0.3, dash=(2, 1.5))
# 层叠参考线（仅画线，Z 值见上方文字说明）
for z, col in [(G["Z_PCB_BOT"], GRAY), (G["Z_PCB_TOP"], INK),
               (12.10, GREEN), (13.10, BLUE), (G["Z_TOP_IN"], REDC)]:
    LN(*SP(G["OX"] + 5, z), *SP(W - G["OX"] - 5, z), col, 0.3, dash=(3, 1.5))
# 底板厚 2.40 已在右下「底板 Z 0~2.4」文字中给出，此处不再重复画短尺寸线，
# 避免与大尺寸线 / 剖面轮廓互相压叠。
DIMV(SZ, SZ + G["H_TOTAL"] * SCL, SX - 8, f"{G['H_TOTAL']:.2f} 总高", label_on="left")
DIMV(SZ + G["Z_TOP_IN"] * SCL, SZ + G["H_TOTAL"] * SCL, SX + W * SCL + 5,
     f"{G['T_TOP']:.2f} 顶板")
DIMH(SX, SX + W * SCL, SZ - 7, f"{W:.2f}")
T("红色虚线 = M3 螺丝中心；剖面仅示意外壳本体", 195, 24, 6.2, INK)
T(f"底板 Z 0~{G['T_BASE']:.1f} / 侧壁 {G['T_BASE']:.1f}~{G['Z_TOP_IN']:.1f} / 顶板 {G['Z_TOP_IN']:.1f}~{G['H_TOTAL']:.1f}",
  195, 18, 6.2, GRAY)
FOOTER("注：4 个螺丝柱与 PCB 4×φ4 孔同轴；靠 4 颗 M3 螺丝从底部固定（φ4 是 M3 加大过孔，M4 需 φ4.5 孔）。")


# ================= 页 3：侧壁展开 + 说明 =================
c.showPage()
HEADER("页 3  四边侧壁展开图 / 天线净空 / 装配与加工说明", 3)
SX, SCL = 25.0, 1.0
Z0 = G["T_BASE"]
HC = G["H_CAVITY"]

def side(y, title, length, segs, note):
    T(title, SX, y + HC + 4, 8, BLUE)
    RECT(SX, y, length * SCL, HC, INK, 0.5, fill=PALE)
    for (a, b, z0, z1, lab, col) in segs:
        RECT(SX + a * SCL, y + (z0 - Z0), (b - a) * SCL, z1 - z0,
             col, 0.5, fill=(HexColor("#fdeceb") if col == REDC else HexColor("#e4f3ea")))
        T(lab, SX + a * SCL + 0.6, y + (z0 - Z0) + 1.2, 5.4, col)
    T(f"0", SX - 3, y - 3, 5.5, DIMC)
    T(f"{length:.2f}", SX + length - 8, y - 3, 5.5, DIMC)
    T(note, SX, y - 7.5, 6.2, GRAY)

top_segs = []
for i, cx in enumerate(G["I2C_X"], 1):
    top_segs.append((cx - G["I2C_SLOT_W"] / 2, cx + G["I2C_SLOT_W"] / 2,
                     4.6, 12.8, f"I2C{i}", GREEN))
top_segs.append((ANT[0], ANT[2], G["ANT_SLOT_Z0"], G["ANT_SLOT_Z1"],
                 "ANT 侧壁让位窗", REDC))
side(158, "上边（天线侧）展开 1:1  —  4× I2C / 复位 / 天线", W, top_segs,
     "4 个 12.00 宽 I2C 窗（Z 4.6~12.8）；天线让位窗 27.00 宽仅开 Z 8.0~14.2，顶板与下段侧壁完整。")
side(126, "下边（双 Type-C）展开 1:1", W,
     [(40.0, 66.0, 7.6, 12.8, "2× Type-C 共用长窗 26.00", GREEN)],
     "对应 ESP32-S3-DevKitC 自带 UART / USB 两个 Type-C（中心约 46.5 / 58.5）；长窗兼容位置偏差。")
side(94, "右边（5V / XH5P）展开 1:1", H,
     [(15.3, 25.3, 4.6, 8.8, "5V Type-C", GREEN),
      (35.0, 51.5, 4.6, 12.8, "XH2.54-5P", GREEN)],
     "5V Type-C 输出口 (USB1)；XH2.54-5P (CN3) 长窗同时兼容 H2 3P / H3 2P 端子。")
side(62, "左边（封闭）展开 1:1", H, [],
     "无外部接口，整段实壁；如需检修口可自行在此边开窗。")

# 右侧说明
IX = 158.0
T("天线净空", IX, 184, 9, BLUE)
T("近场 20mm 内禁金属 / 覆铜", IX, 176, 6.6, REDC)
RX, RY = IX + 4, 150
RR(RX, RY, 55, 22, 2, INK, 0.4, fill=PALE)
# 天线（在上边）与 20mm 净空区
RECT(RX + 11, RY + 8, 34, 14, REDC, 0.4, dash=(2, 1.4))
RECT(RX + 18, RY + 17, 20, 4, REDC, 0.5, fill=HexColor("#fdeceb"))
T("天线", RX + 21, RY + 18.2, 6, REDC)
T("20mm 净空", RX + 12, RY + 9.5, 5.5, REDC)
for x, y in [(RX + 6, RY + 4), (RX + 49, RY + 4), (RX + 6, RY + 12), (RX + 49, RY + 12)]:
    CIRCLE(x, y, 1.6, BLUE, 0.4, fill=HexColor("#c9dcf0"))
T("4 个螺丝柱距天线中心 >45mm", IX, 144, 6.2, INK)
T("顶板完整；天线端经侧壁让位窗伸出壳外", IX, 137, 6.4, REDC)

T("装配顺序", IX, 123, 9, BLUE)
steps = [
    "1. 底座朝上，PCB 放上 4 个 Φ7 支撑台（底面 Z=3.4）",
    "2. LCD 插 PCB 排座；ESP32 天线端朝上边让位窗穿出",
    "3. 扣上盖：四边开窗对准接口；顶板压住屏幕黑边",
    "4. 从底部 4 沉孔拧入 M3×12，穿 PCB φ4 孔拧进上盖柱",
]
for i, s in enumerate(steps):
    T(s, IX, 116 - i * 6.2, 6.3, INK)

T("加工提示", IX, 82, 9, BLUE)
tips = [
    "· 推荐 FDM PETG 或 SLA 韧性树脂；不透明、绝缘",
    "· 禁止金属打印 / 碳纤维 / 导电料 / 金属漆 / 电镀",
    "· 顶板朝上平放打印；层高 ≤0.2mm，窗口与柱精度优先",
    "· 顶板完整无镂空；天线内段上方留 1.1mm，RSSI 偏低可再外移",
    "· 按 STL 原尺寸 1:1 打印，不要缩放、窗口内不加支撑",
    "· 装好 LCD/ESP32 实测最高点：距 PCB 顶面 >9.2mm 需加高壳体",
]
for i, s in enumerate(tips):
    T(s, IX, 75 - i * 6.2, 6.3, INK if i < 3 else GRAY)

T("设计依据", IX, 36, 8.5, BLUE)
T("依据：ESP32S3_LCD 工程 + PCB_PCB1_1_2026-11-07.pdf 装配层", IX, 29, 6.1, GRAY)
T("板框 61.80×100.00 R2；4×φ4 孔距 91.34×48.70（CIRCLE 半径 2mm×2）", IX, 23.5, 6.1, GRAY)
T("ESP32-S3-Metric.pdf：系统板 63.39×27.94，插 U1/U2，天线端经让位窗外露", IX, 18, 6.1, GRAY)
T("ATK-MD0350：LCD 经 H1 插入仅 2 安装孔；φ4 是 M3 加大过孔，不用 M4", IX, 12.5, 6.1, GRAY)
FOOTER("注：Rev E 顶板完整无镂空，天线让位仅在上边侧壁；展开图横轴为边长、纵轴为侧壁高 11.80。")

c.save()
print("PDF:", PDF)
