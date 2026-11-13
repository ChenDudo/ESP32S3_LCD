# -*- coding: utf-8 -*-
"""ESP32S3_LCD 全覆盖外壳 Rev I —— 3 页 A4 横向工程图 PDF"""
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
c.setTitle("ESP32S3_LCD 全覆盖显示屏外壳 工程图 Rev I")
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


def POLY(pts, xoff, yoff, sc, color=INK, lw=0.35, fill=None, dash=None):
    """按点列画多边形（菱形定位销轮廓用）。"""
    p = c.beginPath()
    p.moveTo((xoff + pts[0][0] * sc) * mm, (yoff + pts[0][1] * sc) * mm)
    for x, y in pts[1:]:
        p.lineTo((xoff + x * sc) * mm, (yoff + y * sc) * mm)
    p.close()
    if dash: c.setDash(dash)
    if fill:
        c.setFillColor(fill)
        c.drawPath(p, stroke=0, fill=1)
    c.setStrokeColor(color); c.setLineWidth(lw)
    c.drawPath(p, stroke=1, fill=0)
    if dash: c.setDash()


def MARKS(xoff, yoff, sc, color=HexColor("#243447")):
    """顶板一体成型凸字：用 geom_v2.json 的字形轮廓，even-odd 填充挖空内孔。
    先铺与顶板同色的底衬，遮住穿过字的 PCB 参考虚线 / 器件参考点（制图文字避让）。"""
    for item in G.get("TEXT_MARKS", []):
        bx0, by0, bx1, by1 = item["bbox"]
        c.setFillColor(HexColor("#ffffff"))
        c.rect((xoff + (bx0 - 0.15) * sc) * mm,
               (yoff + (by0 - 0.15) * sc) * mm,
               (bx1 - bx0 + 0.30) * sc * mm,
               (by1 - by0 + 0.30) * sc * mm, stroke=0, fill=1)
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


def DIMH(x1, x2, y, label, color=DIMC, size=7):
    LN(x1, y, x2, y, color, 0.3)
    LN(x1, y - 1.5, x1, y + 1.5, color, 0.25)
    LN(x2, y - 1.5, x2, y + 1.5, color, 0.25)
    T(label, (x1 + x2) / 2 - len(label) * size * 0.27, y + 2.2, size, color)


def DIMV(y1, y2, x, label, color=DIMC, size=7, label_on="right", label_dy=0.0):
    LN(x, y1, x, y2, color, 0.3)
    LN(x - 1.5, y1, x + 1.5, y1, color, 0.25)
    LN(x - 1.5, y2, x + 1.5, y2, color, 0.25)
    yy = (y1 + y2) / 2 - size * 0.35 + label_dy
    if label_on == "left":
        TR(label, x - 2.2, yy, size, color)
    else:
        T(label, x + 2.2, yy, size, color)


def HEADER(title, page):
    c.setFillColor(BLUE); c.rect(0, 196 * mm, 297 * mm, 14 * mm, stroke=0, fill=1)
    T(title, 8, 200.5, 11, HexColor("#ffffff"))
    TR(f"Rev I   {page}/3   2026-11-08   单位 mm", 289, 200.5, 8, HexColor("#dce8f5"))


def FOOTER(note):
    LN(8, 8.5, 289, 8.5, GRAY, 0.3)
    T(note, 8, 4.5, 6.5, GRAY)
    TR("图号 ESP32S3-LCD-EN-I", 289, 4.5, 6.5, GRAY)


W, H = G["W"], G["H"]
WIN = G["WIN"]
ANT = G["ANT"]
HOLES = [tuple(h) for h in G["HOLES"]]
SCREW_POS = [tuple(p) for p in G["SCREW_POS"]]


# ================= 页 1：上盖俯视 =================
HEADER("页 1  上盖俯视图  ·  顶板完整无镂空 / 仅开显示区窗口", 1)
OX, OY, SC = 30.0, 92.0, 1.0

def P(x, y): return (OX + x * SC, OY + y * SC)

RR(OX, OY, W, H, G["R_OUT"], INK, 0.6, fill=PALE)
# PCB 参考
RR(P(G["OX"], G["OY"])[0], P(G["OX"], G["OY"])[1], G["PCB_PY"], G["PCB_PX"],
   G["PCB_R"], GRAY, 0.3, dash=(2, 1.5))
# 显示窗
wx, wy, ww, wh = WIN[0], WIN[1], G["WIN_W"], G["WIN_H"]
RR(P(wx, wy)[0], P(wx, wy)[1], ww, wh, G["WIN_R"], REDC, 0.7, fill=HexColor("#ffffff"))
T("显示窗 = A.A + 让位", P(wx + 3, wy + wh / 2)[0], P(wx + 3, wy + wh / 2)[1], 7, REDC)
T("四周各放大 0.5，不切亮区", P(wx + 3, wy + wh / 2 - 5)[0],
  P(wx + 3, wy + wh / 2 - 5)[1], 6, GRAY)
# 侧壁天线让位窗（俯视投影为靠上边窄条；顶板完整不开洞）
ax0, ay0, ax1, ay1 = ANT
RECT(P(ax0, ay0)[0], P(ax0, ay0)[1], ax1 - ax0, ay1 - ay0,
     BLUE, 0.5, fill=HexColor("#e6eff9"), dash=(2, 1.2))
# 该窄条由上方 27.00 尺寸线与右侧图例说明，视图内不再加文字以免与复位孔标注相叠
# 顶板复位键孔
CIRCLE(*P(*G["RESET_POS"]), G["RESET_HOLE_D"] / 2, REDC, 0.6,
       fill=HexColor("#ffffff"))
# 顶板外表面一体成型接口凸字（与 STL / STEP 同一字形轮廓）
MARKS(OX, OY, SC)
# 复位孔标注：上边 I2C 凸字已上移到 Y≈69.80，故改放窗口上缘与 I2C 之间的空白带，
# 并加一条短引线指向圆孔，避免与 I2C2 / RST 凸字重叠
_hx, _hy = P(G["RESET_POS"][0], G["RESET_POS"][1])
T("Φ4 孔", P(25.0, 61.7)[0], P(25.0, 61.7)[1], 4.8, REDC)
LN(P(37.5, 63.0)[0], P(37.5, 63.0)[1],
   _hx - G["RESET_HOLE_D"] / 2 - 0.6, _hy - 1.8, REDC, 0.3)
# 4 个四角连接柱（PCB 板框之外）
for x, y in SCREW_POS:
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
# 剖切线（沿窗口中心，非外壳几何中心）
_sy = P(0, G["WIN_CY"])[1]
LN(OX - 6, _sy, OX, _sy, BLUE, 0.5)
LN(OX + W, _sy, OX + W + 6, _sy, BLUE, 0.5)
T("A", OX - 8, _sy + 1, 8, BLUE)
T("A", OX + W + 6.5, _sy + 1, 8, BLUE)
# 尺寸
DIMH(OX, OX + W, OY - 8, f"{W:.2f}")
DIMV(OY, OY + H, OX - 9, f"{H:.2f}")
DIMH(P(wx, 0)[0], P(wx + ww, 0)[0], OY + H + 6, f"{G['WIN_W']:.2f} 显示窗")
DIMV(P(0, wy)[1], P(0, wy + wh)[1], OX + W + 8, f"{G['WIN_H']:.2f}")
DIMH(P(ax0, 0)[0], P(ax1, 0)[0], OY + H + 14,
     f"{ax1-ax0:.2f} 侧壁让位窗（顶板不开）", BLUE)
DIMH(P(SCREW_POS[0][0], 0)[0], P(SCREW_POS[2][0], 0)[0], OY - 15, "104.20 柱距")
DIMV(P(0, SCREW_POS[0][1])[1], P(0, SCREW_POS[1][1])[1], OX - 22,
     "66.00 柱距", label_dy=-12)
T("上盖俯视 1:1（单版本显示窗 · A.A 放大让位）", OX, OY - 22, 9, INK)
T("虚线 = PCB 参考轮廓 61.80×100.00 R2 / 蓝色虚线圆 = 四角 Φ6 连接柱（板框外）", OX, 10.5, 6.5, GRAY)

# 右侧信息区
IX = 158.0
T("显示窗 vs 实测 LCD A.A", IX, 184, 9, BLUE)
rows = [["项目", "宽 X", "高 Y", "说明"],
        ["A.A", "73.44", "48.96", "实测发光区"],
        ["窗口", "74.40", "50.00", "四周 +0.5"],
        ["让位", "0.48", "0.52", "不切亮区"]]
colx = [IX, IX + 34, IX + 68, IX + 100]
for r, row in enumerate(rows):
    y = 176 - r * 6
    RECT(IX, y - 2, 132, 6, GRAY, 0.25, fill=(LIGHT if r == 0 else None))
    for j, v in enumerate(row):
        T(v, colx[j] + 1, y, 6.3 if r else 6.8, INK if r else BLUE)
T("窗口比 A.A 大：宁露极窄黑边，不切亮区。", IX, 148, 6.6, REDC)
T(f"窗口 X 左移 {-G['WIN_OFFSET_X']:.2f}（推算待实测）、Y 下移 {-G.get('WIN_OFFSET_Y', 0):.2f}（EDA 实测）。",
  IX, 142.5, 6.6, REDC)

T("四边接口开窗（PCB 左旋 90°、天线朝上的正视图）", IX, 137, 8.5, BLUE)
info = [
    ("上边", f"A 组 Z {G['OPEN_Z0']:.2f}~{G['OPEN_Z1']:.2f}：天线 27.00 与 I2C 宽窗平齐", REDC),
    ("下边", f"B 组 Z {G['DUAL_Z0']:.2f}~{G['DUAL_Z1']:.2f}：核心板双 Type-C 36.00 宽窗", BLUE),
    ("右边", f"A 组 Z {G['OPEN_Z0']:.2f}~{G['OPEN_Z1']:.2f}：5V 18.00 + XH-5P 23.00", INK),
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
    f"窗口 {G['WIN_W']:.2f}×{G['WIN_H']:.2f} R{G['WIN_R']:.1f}；中心 X={G['WIN_CX']:.2f} / Y={G['WIN_CY']:.2f}",
    f"实测 A.A {G['LCD_AA_W']:.2f}×{G['LCD_AA_H']:.2f}，四周让位 {G['WIN_CLEAR_X']:.2f}/{G['WIN_CLEAR_Y']:.2f}",
    f"偏心屏：X 左移 {-G['WIN_OFFSET_X']:.2f}、Y 下移 {-G.get('WIN_OFFSET_Y', 0):.2f} 对准显示区",
    f"顶板完整无镂空；开口 A {G['OPEN_Z0']:.2f}~{G['OPEN_Z1']:.2f} / B {G['DUAL_Z0']:.2f}~{G['DUAL_Z1']:.2f}",
    "插线余量：窗口按带壳插头 + 线材 Φ3~5 留，不按母座贴边",
    "4×Φ6 连接柱在 PCB 板框外；M3 不穿板、φ4 孔空置",
    "PCB 由 2 个对角定位销（圆销 + 菱形销）定位；内缘距 PCB 4.00",
]
for i, s in enumerate(specs):
    # 9 行：行距压到 5.9，末行 y=35.8，与 y=30 的「图例」标题留足间距
    T("· " + s, IX, 83 - i * 5.9, 6.4, INK)

T("图例", IX, 30, 8, BLUE)
CIRCLE(IX + 3, 24, 2, BLUE, 0.4, dash=(1.5, 1)); T("四角 Φ6 连接柱（板框外）", IX + 8, 22.5, 6.4, INK)
RECT(IX, 16, 6, 3, GREEN, 0.4, fill=HexColor("#e4f3ea")); T("I2C 侧壁开窗", IX + 8, 17, 6.4, INK)
RECT(IX + 55, 16, 6, 3, BLUE, 0.4, fill=HexColor("#e6eff9")); T("侧壁让位窗", IX + 63, 17, 6.4, INK)
T(f"顶板 9 组凸字（字高 {G['TEXT_SIZE']:.2f}）：右侧字头朝左 / 上边 I2C 字头朝上 / RST 横排，均贴近接口",
  IX, 11, 5.8, INK)
FOOTER("注：Rev I 四角连接柱移出 PCB 板框，M3 不穿板；窗口 X 左移 2.75 / Y 下移 0.90 对准偏心屏；顶板 9 组凸字一体成型，勿打磨掉。")


# ================= 页 2：底座 + 剖面 =================
c.showPage()
HEADER("页 2  底座俯视图 / A-A 剖面 / 装配层叠", 2)
BX, BY = 30.0, 105.0
RR(BX, BY, W, H, G["R_OUT"], INK, 0.6, fill=PALE)
RR(BX + G["OX"], BY + G["OY"], G["PCB_PY"], G["PCB_PX"], G["PCB_R"],
   GRAY, 0.3, dash=(2, 1.5))
for x, y in SCREW_POS:
    CIRCLE(BX + x, BY + y, G["SCREW_HOLE_D"] / 2, REDC, 0.6)
    CIRCLE(BX + x, BY + y, G["SCREW_CS_D"] / 2, BLUE, 0.4, dash=(1.5, 1))
    CIRCLE(BX + x, BY + y, G["POST_D"] / 2, GRAY, 0.3, dash=(1, 1))
    LN(BX + x - 5, BY + y, BX + x + 5, BY + y, GRAY, 0.2)
    LN(BX + x, BY + y - 5, BX + x, BY + y + 5, GRAY, 0.2)
# PCB 四角孔位：4 个 Φ7 支撑台 + A 方案 2 个对角定位销（圆销 / 菱形销）
for x, y in HOLES:
    CIRCLE(BX + x, BY + y, G["BASE_BOSS_D"] / 2, GRAY, 0.3, dash=(1, 1))
CIRCLE(BX + G["LOCATOR_ROUND"][0], BY + G["LOCATOR_ROUND"][1],
       G["LOCATOR_D"] / 2, GREEN, 0.5)
POLY(G["DIAMOND_PTS"], BX, BY, 1.0, GREEN, 0.5, fill=HexColor("#e4f3ea"))
T("圆销 Φ3.8", BX + G["LOCATOR_ROUND"][0] + 4.5,
  BY + G["LOCATOR_ROUND"][1] - 1.2, 5.4, GREEN)
T("菱形销 3.20", BX + G["LOCATOR_DIAMOND"][0] - 20,
  BY + G["LOCATOR_DIAMOND"][1] + 4.5, 5.4, GREEN)
DIMH(BX, BX + W, BY - 8, f"{W:.2f}")
DIMV(BY, BY + H, BX - 9, f"{H:.2f}")
DIMH(BX + SCREW_POS[0][0], BX + SCREW_POS[2][0], BY - 15, "104.20 柱距")
DIMV(BY + SCREW_POS[0][1], BY + SCREW_POS[1][1], BX - 22,
     "66.00 柱距", label_dy=-12)
T("底座俯视 1:1", BX, BY - 22, 9, INK)
T(f"四角：红 Φ3.4 通孔 / 蓝 Φ6.5 沉孔；PCB 孔位：绿 1 圆销 Φ{G['LOCATOR_D']:.1f}"
  f" + 1 菱形销 {G['DIAMOND_W']:.2f} / 灰 4x Φ7 台（另 2 孔空置）",
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
T("底面 Φ6.5 沉孔 → Φ3.4 通孔 → 四角连接柱", IX, 121, 6.6, INK)
T("→ 上盖 Φ6 柱内 Φ2.6 自攻底孔（盲孔 Z=13.8）", IX, 115, 6.6, INK)
T("M3×12 沉头螺丝【不穿 PCB / LCD】，勿过紧", IX, 109, 6.6, INK)
T("PCB 靠 2 个对角定位销定位（圆销主定位 + 菱形销沿对角削扁）；另 2 个 φ4 孔空置",
  IX, 100, 6.3, GREEN)
T("菱形销连线向留 0.40 单边间隙，吸收 SLA 收缩约 0.31 mm，避免顶销", IX, 94, 6.3, GREEN)

# A-A 剖面 2:1
SX, SZ, SCL = 30.0, 20.0, 1.30
def SP(x, z): return (SX + x * SCL, SZ + z * SCL)
T("A-A 剖面 1.3:1（沿显示窗中心横剖，见页 1）", SX, 70, 9, BLUE)
T(f"装配层叠 Z（mm）：PCB 底 {G['Z_PCB_BOT']:.2f} → 顶 {G['Z_PCB_TOP']:.2f} → 核心板顶 {G['CORE_TOP_Z']:.2f}（直焊）"
  f" → 双 Type-C 插口中心 {G['CORE_PORT_Z']:.2f}",
  SX, 64, 6.6, INK)
T(f"→ 线头壳顶 {G['CABLE_SHELL_TOP_Z']:.2f}（故 B 组开口 {G['DUAL_Z0']:.2f}~{G['DUAL_Z1']:.2f}）；"
  f"排母/排针合高 {G['STACK_BOARD_GAP']:.2f} → LCD 顶面 {G['LCD_TOP_Z']:.2f} → 顶板内表面 {G['Z_TOP_IN']:.2f}（留 {G['STACK_CLEAR']:.2f}）",
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
               (G["CORE_TOP_Z"], BLUE), (G["CORE_PORT_Z"], BLUE),
               (G["CABLE_SHELL_TOP_Z"], GREEN),
               (G["LCD_TOP_Z"], GREEN), (G["Z_TOP_IN"], REDC)]:
    LN(*SP(G["OX"] + 5, z), *SP(W - G["OX"] - 5, z), col, 0.3, dash=(3, 1.5))
# 底板厚 2.40 已在右下「底板 Z 0~2.4」文字中给出，此处不再重复画短尺寸线，
# 避免与大尺寸线 / 剖面轮廓互相压叠。
DIMV(SZ, SZ + G["H_TOTAL"] * SCL, SX - 8, f"{G['H_TOTAL']:.2f} 总高", label_on="left")
DIMV(SZ + G["Z_TOP_IN"] * SCL, SZ + G["H_TOTAL"] * SCL, SX + W * SCL + 5,
     f"{G['T_TOP']:.2f} 顶板")
DIMH(SX, SX + W * SCL, SZ - 7, f"{W:.2f}")
T("红色虚线 = PCB 孔位 / 定位销中心（仅 2 个对角有销）", 208, 30, 6.2, INK)
T(f"底板 Z 0~{G['T_BASE']:.1f} / 侧壁 {G['T_BASE']:.1f}~{G['Z_TOP_IN']:.1f} / 顶板 {G['Z_TOP_IN']:.1f}~{G['H_TOTAL']:.1f}（凸字顶 {G['H_TOTAL'] + G['TEXT_RAISE']:.2f}）",
  208, 23, 6.2, GRAY)
FOOTER("注：Rev I 四角 Φ6 柱在 PCB 板框外，M3 不穿 PCB / LCD；PCB 由 2 个对角定位销（圆 + 菱形）定位；顶板凸字勿打磨。")


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

OZ0, OZ1 = G["OPEN_Z0"], G["OPEN_Z1"]
DZ0, DZ1 = G["DUAL_Z0"], G["DUAL_Z1"]
GL, GR = G["I2C_GROUPS"]
DU = G["DUAL_USBC"]
R5V, RXV = G["RIGHT_SLOTS"]
top_segs = [(GL[0], GL[1], OZ0, OZ1, "I2C 合并窗 25.10", GREEN),
            (ANT[0], ANT[2], OZ0, OZ1, "ANT 让位窗 27.00", REDC),
            (GR[0], GR[1], OZ0, OZ1, "I2C 合并窗 24.90", GREEN)]
side(158, f"上边（天线侧）展开 1:1  —  A 组开口带 Z {OZ0:.2f}~{OZ1:.2f}（高 {OZ1-OZ0:.2f}，上留 {G['OPEN_Z_TOP_WALL']:.2f} 实壁）", W, top_segs,
     "4 个 XH2.54-4P 座中心距仅 12.96，单开 12 窗放不下带壳插头 → 左右各 2 座合并宽窗；"
     "天线让位窗与 I2C 窗上下沿完全平齐，段间各留 2.00 加强筋。")
side(116, f"下边（双 Type-C）展开 1:1  —  B 组开口带 Z {DZ0:.2f}~{DZ1:.2f}（高 {DZ1-DZ0:.2f}，上留 {G['DUAL_Z_TOP_WALL']:.2f} 实壁）", W,
     [(DU[0], DU[1], DZ0, DZ1, "B 组 2× Type-C 36.00", GREEN)],
     f"核心板直焊：插口中心 Z {G['CORE_PORT_Z']:.2f}、线头壳顶 {G['CABLE_SHELL_TOP_Z']:.2f}；"
     f"旧上沿 {OZ1:.2f} 会顶住 → B 组抬到 {DZ1:.2f}（完整 Z 链见下单说明）")
side(74, f"右边（5V / XH5P）展开 1:1  —  A 组 Z {OZ0:.2f}~{OZ1:.2f}", H,
     [(R5V[0], R5V[1], OZ0, OZ1, "5V Type-C 18.00", GREEN),
      (RXV[0], RXV[1], OZ0, OZ1, "XH2.54-5P 23.00", GREEN)],
     "5V Type-C 输出口 (USB1) 由 10.00 加宽到 18.00；XH2.54-5P (CN3) 由 16.50 加宽到 23.00，"
     "两窗之间留 3.00 实壁；均兼容 H2 3P / H3 2P 端子。")
side(32, "左边（封闭）展开 1:1", H, [],
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
T("4 个四角连接柱距天线中心 >45mm", IX, 144, 6.2, INK)
T("顶板完整；天线端经侧壁让位窗伸出壳外", IX, 137, 6.4, REDC)

T("装配顺序", IX, 123, 9, BLUE)
steps = [
    "1. 底座朝上，2 个对角 φ4 孔对准圆销 Φ3.8 / 菱形销 3.20（底面 Z=3.4）",
    "2. LCD 插 PCB 排座；ESP32 核心板直焊，天线端朝上边让位窗",
    "3. 扣上盖：四边开窗对准接口；顶板压住屏幕黑边",
    "4. 从底部 4 沉孔拧入 M3×12，直接拧进四角连接柱（不穿 PCB / LCD）",
]
for i, s in enumerate(steps):
    T(s, IX, 116 - i * 6.2, 6.3, INK)

T("加工提示", IX, 82, 9, BLUE)
tips = [
    "· 推荐 FDM PETG 或 SLA 韧性树脂；不透明、绝缘",
    "· 禁止金属打印 / 碳纤维 / 导电料 / 金属漆 / 电镀",
    "· 顶板朝上平放打印；层高 ≤0.2mm，窗口与柱精度优先",
    "· 顶板完整无镂空；开口 A/B 两组不同高，均已留线材余量，勿缩小",
    "· 顶板 9 组凸字勿打磨/喷砂；按 STL 1:1 打印，窗口内不加支撑",
    f"· 装好 LCD/ESP32 实测最高点：距 PCB 顶面 >{G['Z_TOP_IN'] - G['Z_PCB_TOP'] - G['STACK_CLEAR']:.2f}mm 需再加高",
]
for i, s in enumerate(tips):
    T(s, IX, 75 - i * 6.2, 6.3, INK if i < 3 else GRAY)

T("设计依据", IX, 36, 8.5, BLUE)
T("依据：ESP32S3_LCD 工程 + PCB_PCB1_1_2026-11-07.pdf 装配层", IX, 29, 6.1, GRAY)
T("板框 61.80×100.00 R2；4×φ4 孔距 91.34×48.70（CIRCLE 半径 2mm×2）", IX, 23.5, 6.1, GRAY)
T(f"ESP32-S3-Metric.pdf：系统板 63.39×27.94 直焊；双 Type-C 口中心 Z {G['CORE_PORT_Z']:.2f} → B 组 {DZ0:.2f}~{DZ1:.2f}", IX, 18, 6.1, GRAY)
T("ATK-MD0350 图3.1：模块板 56.41×97.92、仅一端 2 孔距 48.64；板覆盖 PCB 四角孔", IX, 12.5, 6.1, GRAY)
FOOTER(f"注：开口 A {OZ0:.2f}~{OZ1:.2f} / B {DZ0:.2f}~{DZ1:.2f}；四角柱在板框外、M3 不穿板；顶板完整带 9 组凸字；★ 底座四角无凸台，与上盖 Z=2.40 平面贴合（旧件削平 1mm）。")

c.save()
print("PDF:", PDF)
