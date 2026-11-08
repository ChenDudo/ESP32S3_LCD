# -*- coding: utf-8 -*-
"""ESP32S3_LCD 全覆盖不透明外壳 Rev I —— 生成 STL / DXF / 报价 / 下单说明

结构：上盖（完整不透明顶板 + 四周侧壁 + 4 个四角连接柱，仅开显示区窗口 + Φ4 复位孔）
      底座（平板 + 4 定位销台 + 4 连接柱台 + 4 沉孔）
      Rev I：4 个连接柱移到 PCB 板框之外的外壳四角，M3 不再穿过 PCB；
      PCB 由底座 Φ3.8 定位销定位。四边所有对外开口统一开口带 Z 4.00~14.20，上下沿完全平齐；
      天线让位窗 27.00 与 I2C 合并宽窗同高；双 Type-C / 5V / XH-5P 均按
      带壳插头 + 线材外径留余量。顶板保持完整不镂空。
"""
import os, json, csv, math
import numpy as np
from shapely.geometry import box, Point
from shapely.ops import unary_union
import trimesh
from trimesh.creation import extrude_polygon
import ezdxf
import params_v2 as P

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "deliverables")
os.makedirs(OUT, exist_ok=True)
ARCH = os.path.join(HERE, "archive_v1")
os.makedirs(ARCH, exist_ok=True)

# 归档上一版开放式底座文件
OLD = ["ESP32S3_LCD_底座_3D打印.stl", "ESP32S3_LCD_底座_加工轮廓.dxf",
       "ESP32S3_LCD_底座_工程图.dxf", "ESP32S3_LCD_底座_工程图.pdf",
       "给商家的下单说明.txt", "外壳实物报价.csv"]
for f in OLD:
    src, dst = os.path.join(OUT, f), os.path.join(ARCH, f)
    if os.path.exists(src) and not os.path.exists(dst):
        os.replace(src, dst)


def rr(w, h, r, ox=0.0, oy=0.0, res=32):
    """圆角矩形 shapely 多边形"""
    return box(ox + r, oy + r, ox + w - r, oy + h - r).buffer(r, resolution=res, join_style=1)


def rr_at(cx, cy, w, h, r, res=24):
    return rr(w, h, r, cx - w / 2, cy - h / 2, res)


def rr_pts(w, h, r, ox=0.0, oy=0.0, res=10):
    def arc(cx, cy, a0, a1):
        return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / res)),
                 cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / res)))
                for i in range(res + 1)]
    return (arc(ox + w - r, oy + h - r, 0, 90) +
            arc(ox + r, oy + h - r, 90, 180) +
            arc(ox + r, oy + r, 180, 270) +
            arc(ox + w - r, oy + r, 270, 360))


def prism(poly, z0, z1):
    m = extrude_polygon(poly, z1 - z0)
    m.apply_translation([0, 0, z0 - m.bounds[0][2]])
    return m


def cyl(r, z0, z1, x, y, sections=32):
    c = trimesh.creation.cylinder(radius=r, height=z1 - z0, sections=sections)
    # trimesh cylinder 默认以原点居中，按实际 bounds 把底面对齐到 z0
    c.apply_translation([x, y, z0 - c.bounds[0][2]])
    return c


def bdiff(meshes):
    return trimesh.boolean.difference(meshes, engine="manifold")


def bunion(meshes):
    return trimesh.boolean.union(meshes, engine="manifold")


OUTER = rr(P.W, P.H, P.R_OUT)
INNER = rr(P.W - 2 * P.T_WALL, P.H - 2 * P.T_WALL, P.R_IN,
           P.T_WALL, P.T_WALL)
OUTER_PTS = rr_pts(P.W, P.H, P.R_OUT)


# ---------------- 上盖 ----------------
def build_top(win_w, win_h):
    outer = prism(OUTER, P.T_BASE, P.H_TOTAL)                 # 罩体 Z 2.4~16.0
    cavity = prism(INNER, P.T_BASE, P.Z_TOP_IN)               # 内腔 Z 2.4~14.2
    window = prism(rr_at(P.WIN_CX, P.WIN_CY, win_w, win_h, P.WIN_R),
                   P.Z_TOP_IN - 0.2, P.H_TOTAL + 0.5)          # 显示窗切穿顶板
    # Rev I：顶板完整无镂空；天线让位与所有接口窗统一 Z 开口带（止于顶板内表面）
    ant_slot = prism(box(P.ANT_X0, P.ANT_Y0, P.ANT_X1, P.H + 2.0),
                     P.ANT_SLOT_Z0, P.ANT_SLOT_Z1)
    reset = cyl(P.RESET_HOLE_D / 2, P.Z_TOP_IN - 0.2, P.H_TOTAL + 0.5,
                *P.RESET_POS)
    cut = [outer, cavity, window, ant_slot, reset]
    for name, (x0, y0, x1, y1), z0, z1, desc in P.SLOTS:
        cut.append(prism(box(x0, y0, x1, y1), z0, z1))
    shell = bdiff(cut)

    # 4 个四角连接柱（带自攻底孔，柱顶嵌进顶板 0.2）
    posts = []
    for x, y in P.SCREW_POS:
        post = bdiff([cyl(P.POST_D / 2, P.POST_Z0, P.POST_Z1, x, y),
                      cyl(P.POST_PILOT_D / 2, P.POST_Z0 - 0.2, P.POST_PILOT_Z1, x, y)])
        posts.append(post)
    # 顶板完整封闭，无需加强筋
    return bunion([shell] + posts)


# ---------------- 底座 ----------------
def build_base():
    body = prism(OUTER, 0, P.T_BASE)
    # 新四角连接柱台（带 M3 通孔 + 沉孔），位于 PCB 板框之外
    screw_boss = [cyl(P.POST_D / 2, P.T_BASE - 0.1, P.Z_PCB_BOT, x, y)
                  for x, y in P.SCREW_POS]
    # PCB 孔位：Φ7 支撑台 + Φ3.8 定位销（穿过 PCB 四角 φ4 孔）
    pcb_boss = [cyl(P.BASE_BOSS_D / 2, P.T_BASE - 0.1, P.Z_PCB_BOT, x, y)
                for x, y in P.HOLES]
    pins = [cyl(P.LOCATOR_D / 2, P.Z_PCB_BOT - 0.1, P.LOCATOR_Z1, x, y)
            for x, y in P.HOLES]
    solid = bunion([body] + screw_boss + pcb_boss + pins)
    cuts = []
    for x, y in P.SCREW_POS:
        cuts.append(cyl(P.SCREW_HOLE_D / 2, -1.0, P.Z_PCB_BOT + 0.2, x, y))
        cuts.append(cyl(P.SCREW_CS_D / 2, -1.0, P.SCREW_CS_DEPTH, x, y))
    return bdiff([solid] + cuts)


top = build_top(P.WIN_W, P.WIN_H)
base = build_base()

files = {}
for name, mesh in [("ESP32S3_LCD_全覆盖外壳_上盖_3D打印.stl", top),
                   ("ESP32S3_LCD_全覆盖外壳_底座_3D打印.stl", base)]:
    p = os.path.join(OUT, name)
    mesh.export(p)
    files[name] = dict(watertight=bool(mesh.is_watertight),
                       volume_cm3=round(mesh.volume / 1000, 2),
                       bounds=[[round(v, 2) for v in r] for r in mesh.bounds],
                       faces=int(len(mesh.faces)))
    print(f"STL {name}: watertight={mesh.is_watertight} "
          f"vol={mesh.volume/1000:.2f}cm3 faces={len(mesh.faces)}")

# ---------------- DXF 工具 ----------------
def new_doc(layers):
    d = ezdxf.new("R2010", setup=True)
    d.header["$INSUNITS"] = 4  # mm
    for n, c in layers:
        d.layers.new(n, dxfattribs={"color": c})
    return d


def T(m, s, x, y, h=2.5, layer="TEXT", rot=0):
    m.add_text(s, dxfattribs={"layer": layer, "height": h,
                              "insert": (x, y), "rotation": rot})


def LN(m, p1, p2, layer="OUTLINE"):
    m.add_line(p1, p2, dxfattribs={"layer": layer})


def RECT(m, x0, y0, x1, y1, layer="OUTLINE"):
    m.add_lwpolyline([(x0, y0), (x1, y0), (x1, y1), (x0, y1)],
                     close=True, dxfattribs={"layer": layer})


def DIMH(m, x1, x2, y, label, off=0):
    yd = y + off
    LN(m, (x1, yd), (x2, yd), "DIM")
    LN(m, (x1, y - 1.2), (x1, yd + 1.6), "DIM")
    LN(m, (x2, y - 1.2), (x2, yd + 1.6), "DIM")
    for xx, s in ((x1, 1), (x2, -1)):
        m.add_solid([(xx, yd), (xx + s * 1.5, yd + 0.4),
                     (xx + s * 1.5, yd - 0.4)], dxfattribs={"layer": "DIM"})
    T(m, label, (x1 + x2) / 2 - len(label) * 0.8, yd + 1.3, 2.6, "DIM")


def DIMV(m, y1, y2, x, label, off=0):
    xd = x + off
    LN(m, (xd, y1), (xd, y2), "DIM")
    LN(m, (x - 1.2, y1), (xd + 1.6, y1), "DIM")
    LN(m, (x - 1.2, y2), (xd + 1.6, y2), "DIM")
    for yy, s in ((y1, 1), (y2, -1)):
        m.add_solid([(xd, yy), (xd + 0.4, yy + s * 1.5),
                     (xd - 0.4, yy + s * 1.5)], dxfattribs={"layer": "DIM"})
    T(m, label, xd - 2.2, (y1 + y2) / 2 - len(label) * 0.8, 2.6, "DIM", 90)


LAYERS = [("OUTLINE", 7), ("WINDOW", 1), ("CUT", 1), ("HOLE", 1),
          ("PCB_REF", 8), ("DIM", 4), ("CENTER", 8), ("TEXT", 7),
          ("TABLE", 7), ("ANT", 2), ("SECTION", 5), ("NOTE", 6), ("SLOT", 3)]

WIN = (P.WIN_CX - P.WIN_W / 2, P.WIN_CY - P.WIN_H / 2,
       P.WIN_CX + P.WIN_W / 2, P.WIN_CY + P.WIN_H / 2)
LCD_AA = (P.WIN_CX - P.LCD_AA_X / 2, P.WIN_CY - P.LCD_AA_Y / 2,
          P.WIN_CX + P.LCD_AA_X / 2, P.WIN_CY + P.LCD_AA_Y / 2)

# ---- 1. 上盖 1:1 加工图（俯视 + 四边展开） ----
d = new_doc(LAYERS)
m = d.modelspace()
m.add_lwpolyline(OUTER_PTS, close=True, dxfattribs={"layer": "OUTLINE"})
m.add_lwpolyline(rr_pts(P.WIN_W, P.WIN_H, P.WIN_R, WIN[0], WIN[1]),
                 close=True, dxfattribs={"layer": "WINDOW"})
m.add_lwpolyline(rr_pts(P.PCB_PY, P.PCB_PX, P.PCB_R, P.OX, P.OY), close=True,
                 dxfattribs={"layer": "PCB_REF", "linetype": "DASHED"})
# 侧壁天线让位窗（俯视投影为靠上边窄条；顶板完整不开洞）
RECT(m, P.ANT_X0, P.ANT_Y0, P.ANT_X1, P.H, "ANT")
# 顶板复位键孔
m.add_circle(P.RESET_POS, P.RESET_HOLE_D / 2, dxfattribs={"layer": "HOLE"})
T(m, "复位孔 Φ4.0", P.RESET_POS[0] + 3, P.RESET_POS[1] + 1, 1.8, "NOTE")
for x, y in P.SCREW_POS:
    m.add_circle((x, y), P.POST_D / 2, dxfattribs={"layer": "CENTER", "linetype": "DASHED"})
    LN(m, (x - 4.5, y), (x + 4.5, y), "CENTER")
    LN(m, (x, y - 4.5), (x, y + 4.5), "CENTER")
# 关键器件标记
for name, (x, y) in P.PARTS.items():
    m.add_circle((x, y), 1.2, dxfattribs={"layer": "PCB_REF"})
    T(m, name, x + 1.8, y + 0.6, 1.8, "NOTE")
# 尺寸
DIMH(m, 0, P.W, 0, f"{P.W:.2f}", -11)
DIMV(m, 0, P.H, 0, f"{P.H:.2f}", -11)
DIMH(m, WIN[0], WIN[2], P.H, f"{P.WIN_W:.2f} 显示窗", 7)
DIMV(m, WIN[1], WIN[3], P.W, f"{P.WIN_H:.2f}", 9)
DIMH(m, P.ANT_X0, P.ANT_X1, P.H, f"{P.ANT_X1-P.ANT_X0:.2f} 侧壁让位窗(顶板不开)", 15)
DIMH(m, P.SCREW_POS[0][0], P.SCREW_POS[2][0], 0, "104.20 柱距", -20)
DIMV(m, P.SCREW_POS[0][1], P.SCREW_POS[1][1], 0, "66.00", -20)
T(m, f"上盖俯视 1:1  (单位 mm)  显示窗 {P.WIN_W:.2f} x {P.WIN_H:.2f}（按实测 A.A 放大让位）", 0, -30, 3.6)
T(m, f"实测 LCD A.A {P.LCD_AA_X:.2f} x {P.LCD_AA_Y:.2f}；窗口四周各让位 {P.WIN_CLEAR_X:.2f} / {P.WIN_CLEAR_Y:.2f}，请勿缩小", 0, -35, 2.8, "NOTE")
T(m, "顶板完整封闭、无镂空；仅显示窗 + Φ4 复位孔", 0, P.H + 22, 3.0, "ANT")
T(m, "四边统一开口带 Z 4.00~14.20：天线 27.00 与 I2C 宽窗平齐；双 Type-C 36.00；5V 18.00 / XH-5P 23.00",
  0, P.H + 27, 2.8, "ANT")
T(m, f"Rev I 偏心屏：显示窗中心 X={P.WIN_CX:.2f} / Y={P.WIN_CY:.2f}"
     f"（相对外壳中心左移 {-P.WIN_OFFSET_X:.2f}），窗口左缘 X={WIN[0]:.2f}；请勿居中",
  0, P.H + 32, 2.8, "ANT")
T(m, f"单版本：窗口 {P.WIN_W:.2f} x {P.WIN_H:.2f} 比实测 A.A {P.LCD_AA_X:.2f} x {P.LCD_AA_Y:.2f} 四周各放大 {P.WIN_CLEAR_X:.2f} / {P.WIN_CLEAR_Y:.2f}",
  0, P.H + 37, 2.8, "ANT")
# 四边侧壁展开图（放在右侧 x=125 起）
SX, SY = 125.0, 0.0
def side_view(title, length, segments, y):
    RECT(m, SX, y, SX + length, y + P.H_CAVITY, "OUTLINE")
    T(m, title, SX, y + P.H_CAVITY + 3.0, 2.6)
    for (a, b, z0, z1, label) in segments:
        RECT(m, SX + a, y + (z0 - P.T_BASE), SX + b, y + (z1 - P.T_BASE), "SLOT")
        T(m, label, SX + a, y - 3.5, 1.9, "NOTE")
    T(m, "0", SX - 3, y - 1, 2.0, "DIM")
    T(m, f"{length:.1f}", SX + length - 6, y - 1, 2.0, "DIM")

top_segs = [(b[0], b[2], z0, z1, n) for n, b, z0, z1, d in P.SLOTS
            if n.startswith("I2C")]
top_segs += [(P.ANT_X0, P.ANT_X1, P.ANT_SLOT_Z0, P.ANT_SLOT_Z1, "ANT 让位窗")]
bot_segs = [(b[0], b[2], z0, z1, n) for n, b, z0, z1, d in P.SLOTS if b[1] < 0]
rgt_segs = [(b[1], b[3], z0, z1, n) for n, b, z0, z1, d in P.SLOTS
            if b[0] > P.W - P.T_WALL - 1]
side_view("上边（天线侧）展开 1:1", P.W, top_segs, 8)
side_view("下边（双 Type-C）展开 1:1", P.W, bot_segs, 32)
side_view("右边（5V / XH5P）展开 1:1", P.H, rgt_segs, 56)
side_view("左边（封闭，无开口）展开 1:1", P.H, [], 80)
T(m, "侧壁展开：横轴 = 边长方向，纵轴 = 侧壁高 11.80 (Z 2.4~14.2)", SX, 100, 2.6, "NOTE")
T(m, "SLOT 层 = 需开通的窗口；其余为实壁", SX, 105, 2.6, "NOTE")
d.saveas(os.path.join(OUT, "ESP32S3_LCD_全覆盖外壳_上盖_加工图.dxf"))

# ---- 2. 底座 1:1 加工图 ----
d2 = new_doc(LAYERS)
m2 = d2.modelspace()
m2.add_lwpolyline(OUTER_PTS, close=True, dxfattribs={"layer": "OUTLINE"})
m2.add_lwpolyline(rr_pts(P.PCB_PY, P.PCB_PX, P.PCB_R, P.OX, P.OY), close=True,
                  dxfattribs={"layer": "PCB_REF", "linetype": "DASHED"})
for x, y in P.SCREW_POS:
    m2.add_circle((x, y), P.SCREW_HOLE_D / 2, dxfattribs={"layer": "HOLE"})
    m2.add_circle((x, y), P.SCREW_CS_D / 2, dxfattribs={"layer": "CENTER", "linetype": "DASHED"})
    LN(m2, (x - 5, y), (x + 5, y), "CENTER")
    LN(m2, (x, y - 5), (x, y + 5), "CENTER")
# PCB 四角孔位：底座定位销（不是螺丝孔）
for x, y in P.HOLES:
    m2.add_circle((x, y), P.LOCATOR_D / 2, dxfattribs={"layer": "PCB_REF"})
    m2.add_circle((x, y), P.BASE_BOSS_D / 2, dxfattribs={"layer": "PCB_REF", "linetype": "DASHED"})
DIMH(m2, 0, P.W, 0, f"{P.W:.2f}", -11)
DIMV(m2, 0, P.H, 0, f"{P.H:.2f}", -11)
DIMH(m2, P.SCREW_POS[0][0], P.SCREW_POS[2][0], 0, "104.20 柱距", -20)
DIMV(m2, P.SCREW_POS[0][1], P.SCREW_POS[1][1], 0, "66.00", -20)
T(m2, "底座俯视 1:1 (单位 mm)", 0, -30, 3.6)
T(m2, "四角 4x Φ3.4 通孔 + 底面 Φ6.5 深 1.6 沉孔（M3 沉头螺丝；不穿 PCB）", 0, P.H + 8, 2.8)
T(m2, "PCB 孔位：4x Φ7 支撑台 + Φ3.8x1.6 定位销（PCB 底面 Z=3.4）", 0, P.H + 13, 2.8)
T(m2, "四角 Φ6 连接柱在 PCB 板框之外；底板厚 2.40；总装配高 16.00", 0, P.H + 23, 2.8)
d2.saveas(os.path.join(OUT, "ESP32S3_LCD_全覆盖外壳_底座_加工图.dxf"))

# ---- 3. 装配工程图 DXF（剖面 + BOM + 技术说明 + 标题栏） ----
d3 = new_doc(LAYERS)
m3 = d3.modelspace()
# 上盖俯视（缩略，1:1）
m3.add_lwpolyline(OUTER_PTS, close=True, dxfattribs={"layer": "OUTLINE"})
m3.add_lwpolyline(rr_pts(P.WIN_W, P.WIN_H, P.WIN_R, WIN[0], WIN[1]),
                  close=True, dxfattribs={"layer": "WINDOW"})
RECT(m3, P.ANT_X0, P.ANT_Y0, P.ANT_X1, P.H, "ANT")
m3.add_circle(P.RESET_POS, P.RESET_HOLE_D / 2, dxfattribs={"layer": "HOLE"})
for x, y in P.SCREW_POS:
    m3.add_circle((x, y), P.POST_D / 2, dxfattribs={"layer": "HOLE"})
DIMH(m3, 0, P.W, 0, f"{P.W:.2f}", -11)
DIMV(m3, 0, P.H, 0, f"{P.H:.2f}", -11)
T(m3, "上盖俯视 1:1", 0, -18, 3.4)
LN(m3, (-5, P.WIN_CY), (0, P.WIN_CY), "SECTION")
LN(m3, (P.W, P.WIN_CY), (P.W + 5, P.WIN_CY), "SECTION")
T(m3, "A", -8, P.WIN_CY + 1.5, 3.2, "SECTION"); T(m3, "A", P.W + 6, P.WIN_CY + 1.5, 3.2, "SECTION")

# A-A 剖面 2:1
SX0, SZ, SC = 150.0, 20.0, 2.0
def PP(x, z): return (SX0 + x * SC, SZ + z * SC)
sec = [PP(0, P.T_BASE), PP(P.W, P.T_BASE), PP(P.W, P.H_TOTAL),
       PP(P.W - P.T_WALL, P.H_TOTAL), PP(P.W - P.T_WALL, P.Z_TOP_IN),
       PP(P.T_WALL, P.Z_TOP_IN), PP(P.T_WALL, P.H_TOTAL),
       PP(0, P.H_TOTAL)]
m3.add_lwpolyline(sec, close=True, dxfattribs={"layer": "SECTION"})
# 顶板窗口断口（剖面在 y=33.5 穿过窗口）
wa, wb = WIN[0] * SC, WIN[2] * SC
LN(m3, (SX0 + wa, SZ + P.Z_TOP_IN * SC), (SX0 + wa, SZ + P.H_TOTAL * SC), "SECTION")
LN(m3, (SX0 + wb, SZ + P.Z_TOP_IN * SC), (SX0 + wb, SZ + P.H_TOTAL * SC), "SECTION")
# 底座
m3.add_lwpolyline([PP(0, 0), PP(P.W, 0), PP(P.W, P.T_BASE), PP(0, P.T_BASE)],
                  close=True, dxfattribs={"layer": "SECTION"})
# 层叠
for z, label in [(P.Z_PCB_BOT, "PCB 底面"), (P.Z_PCB_TOP, "PCB t=1.6"),
                 (9.10, "ESP32 核心板顶面(直焊)"), (12.10, "3.5in LCD 模块顶面")]:
    LN(m3, PP(P.OX + 5, z), PP(P.W - P.OX - 5, z), "PCB_REF")
    T(m3, label, SX0 + 6 * SC, SZ + z * SC + 1.2, 2.0, "NOTE")
LN(m3, PP(0, P.Z_TOP_IN), PP(P.W, P.Z_TOP_IN), "CENTER")
T(m3, "顶板内表面 Z=14.2；LCD 顶面约 12.1，间隙约 2.1", SX0, SZ + 34 * SC, 2.4, "NOTE")
DIMV(m3, SZ, SZ + P.T_BASE * SC, SX0, "2.40", -10)
DIMV(m3, SZ + P.T_BASE * SC, SZ + P.H_TOTAL * SC, SX0, "16.00 总高", -24)
T(m3, "A-A 剖面 2:1（沿窗口中心横剖）", SX0, SZ + 40 * SC, 3.6)

# BOM
BX, BY, RH = 225.0, 150.0, 6.5
rows = [["序号", "名称", "规格 / 材料", "数量"],
        ["1", "上盖", "PLA/PETG 或光敏树脂，不透明、非导电", "1"],
        ["2", "底座", "同上", "1"],
        ["3", "M3 自攻螺丝", "M3x12 沉头 304 不锈钢", "4"],
        ["4", "硅胶脚垫", "Φ8x1.5 自粘（可选）", "4"]]
for xx in (BX, BX + 10, BX + 30, BX + 92, BX + 125):
    LN(m3, (xx, BY - len(rows) * RH), (xx, BY + RH), "TABLE")
for r in range(len(rows) + 1):
    LN(m3, (BX, BY + RH - r * RH), (BX + 125, BY + RH - r * RH), "TABLE")
for r, row in enumerate(rows):
    for c, val in enumerate(row):
        T(m3, val, BX + [0, 10, 30, 92][c] + 1.0,
          BY - r * RH + 1.6, 2.2, "TABLE")
T(m3, "明细表 BOM", BX, BY + 11, 3.2)

notes = [
    "技术说明 / Technical Notes",
    "1. 上盖为不透明全覆盖件，仅开显示区窗口；屏幕黑边（右侧宽于左侧）被顶板压住。",
    "2. 显示窗 74.40x50.00，按实测 LCD A.A 73.44x48.96 四周各放大 0.48/0.52 让位；",
    "   原 A/B 双版窗口均小于 A.A（会切掉亮区像素），已作废，本版只剩一个上盖。",
    "2b.【偏心屏对位】ATK-MD0350 显示区不居中：右侧黑边宽、左侧窄，上下对称。",
    "   窗口中心 X 由 52.60 左移至 49.85（WIN_OFFSET_X=-2.75），Y 保持 33.50；",
    "   除 <=0.5mm 装配让位外，四周黑边由完整不透明顶板压住。依据规格书 OUTLINE 84.69x55.26",
    "   / LCD A.A 73.44x48.96 长边尺寸链偏心 2.77 mm，实物图逐像素 2.52 mm，取 2.75。",
    "   打样前点亮屏幕实测：亮区左缘到模块左缘 L、右缘到模块右缘 R，(L-R)/2 即偏移量；",
    "   不符改 params_v2.py 的 WIN_OFFSET_X 一行并重跑全部脚本。",
    "3. 顶板完整封闭不镂空；四边开口统一 Z 4.00~14.20，天线让位窗与 I2C 窗上下沿平齐。",
    "4. 天线投影 20mm 内禁止金属件、覆铜；4 个连接柱距天线中心均 >45mm。",
    "5. 上边：2 段 I2C 合并宽窗（4 个 XH2.54-4P，座距 12.96）+ Φ4 复位孔 + 27.00 天线让位窗。",
    "   下边：ESP32 核心板（直焊）双 Type-C 共用 36.00 窗；右边：5V 18.00 + XH-5P 23.00。",
    "   所有窗口按带壳插头宽 14~16 / 线材 Φ3~5 留余量，非按母座贴边开孔。",
    "6. Rev I：4x M3x12 自底面沉孔穿入，直接拧进外壳四角 Φ6 柱（底孔 Φ2.6）；",
    "   不穿过 PCB。LCD 板 97.92 覆盖 PCB 四角 φ4 孔且左端无孔，旧穿板方案装不上。",
    "   PCB 由底座 4 个 Φ3.8x1.6 定位销 + Φ7 支撑台定位，φ4 孔空置不用螺丝。",
    "7. 材料必须绝缘非金属；不喷金属漆、不镀层、不用碳纤维/导电料；建议 PETG 或韧性树脂。",
    "8. 未注公差按 3D 打印常规工艺；本图不作 GB/ISO 符合性声明。",
]
for i, t in enumerate(notes):
    T(m3, t, 150.0, 5 - i * 5.2, 2.5, "NOTE" if i else "TEXT")

TX, TY = 225.0, 10.0
for xx in (TX, TX + 60, TX + 92, TX + 125):
    LN(m3, (xx, TY), (xx, TY + 25), "TABLE")
for yy in (TY, TY + 8, TY + 16, TY + 25):
    LN(m3, (TX, yy), (TX + 125, yy), "TABLE")
T(m3, "ESP32S3_LCD 全覆盖显示屏外壳", TX + 2, TY + 18.5, 3.0)
T(m3, "图号 ESP32S3-LCD-EN-I", TX + 2, TY + 10.5, 2.3)
T(m3, "Rev I", TX + 94, TY + 10.5, 2.3)
T(m3, "单位 mm  比例 1:1 / 2:1", TX + 2, TY + 2.5, 2.3)
T(m3, "2026-11-07", TX + 94, TY + 2.5, 2.3)
d3.saveas(os.path.join(OUT, "ESP32S3_LCD_全覆盖外壳_装配工程图.dxf"))
print("DXF x3 done")

# ---------------- 报价 CSV ----------------
vol_top = top.volume / 1000
vol_base = base.volume / 1000
vol_all = vol_top + vol_base
quote = [
    ["项目", "规格/工艺", "数量", "单价参考(¥)", "小计(¥)", "备注"],
    ["上盖 FDM 3D打印", f"PLA/PETG 不透明，约 {vol_top:.1f} cm3", "1件", "16~26", "16~26", "发 STL，推荐 PETG"],
    ["底座 FDM 3D打印", f"PLA/PETG，约 {vol_base:.1f} cm3", "1件", "14~24", "14~24", "与上盖同单打印更便宜"],
    ["整套 SLA 光敏树脂", f"约 {vol_all:.1f} cm3，精度高", "1套", "55~95", "55~95", "替代方案，表面更好"],
    ["整套 亚克力/CNC", "需改造为叠层结构", "1套", "120~220", "120~220", "不推荐，成本高"],
    ["M3 自攻螺丝", "M3x12 沉头 304 不锈钢", "4颗", "0.4~0.8", "1.6~3.2", "搜：M3*12 沉头螺丝"],
    ["硅胶脚垫", "Φ8x1.5 自粘（可选）", "4片", "0.3~0.6", "1~2", "遮住螺丝头"],
    ["运费", "普通快递", "1单", "8~12", "8~12", "部分商家满额包邮"],
    ["合计 · 经济 FDM", "上盖+底座+螺丝+运费", "1台", "", "40~65", "不含 PCB / LCD / ESP32"],
    ["合计 · 含脚垫", "再加脚垫", "1台", "", "41~67", ""],
    ["合计 · 推荐 SLA", "树脂整套+螺丝+运费", "1台", "", "65~110", "精度高、卡扣/柱更准"],
    ["小批量 5 套 FDM", "摊薄后单套", "5套", "22~34/套", "110~170", "开机费摊薄"],
]
with open(os.path.join(OUT, "外壳实物报价.csv"), "w", newline="", encoding="utf-8-sig") as f:
    csv.writer(f).writerows(quote)

# ---------------- 下单说明 ----------------
note = f"""ESP32-S3 LCD 全覆盖显示屏外壳 Rev I —— 淘宝打样下单说明
==========================================================
  【零、Rev I 结构修正：4 颗螺丝不再穿过 PCB】
  ★ ATK-MD0350 用户手册图 3.1：模块 PCB 底板 56.41 x 97.92 mm，
    两个安装孔只在 ALIENTEK 一端、孔距 48.64 mm；屏幕左侧没有过孔。
    PCB 同侧两孔距 48.695，与 48.64 仅差 0.055 → LCD 两孔对准 PCB 一端两孔。
    LCD 板 97.92 长 < PCB 100 长，故 LCD 板【完全覆盖 PCB 四角 φ4 孔】，
    左端为实心板。旧版「底部 4 颗 M3 穿过 PCB 四角孔 → 拧进上盖柱」装不上：
    螺杆在 Z 5.0~12.1 段被 LCD 板挡死，缩柱径 / 换 M2 / 不上 LCD 螺丝都无效。
  ★ 本版修法：外形每边 +3.00 mm → {P.W:.2f} x {P.H:.2f} x {P.H_TOTAL:.2f} mm，
    4 个连接柱移到外壳四角（PCB 板框之外，柱心 ({P.SCREW_C:.2f},{P.SCREW_C:.2f}) 等，Φ{P.POST_D:.1f}）。
    因 LCD 板完全在 PCB 板框内，柱子与屏幕绝无干涉；柱心到 PCB 圆角实体
    净距 3.80 mm > 柱半径 3.00，余量 0.80 mm。
  ★ PCB 四角 φ4 孔【不再穿螺丝】，改由底座 4 个 Φ{P.LOCATOR_D:.1f}x1.6 定位销
    （Z 3.40~5.00）水平定位，底座原 4 个 Φ{P.BASE_BOSS_D:.1f} 支撑台托住 PCB 底面。
    4 颗 M3x12 只连接上盖与底座的四角柱，不再经过 PCB / LCD。
  ★ 顶板内表面 Z=14.20 与 LCD 板顶（约 12.1）留约 2.1 mm；
    若装配后觉得 PCB/LCD 有轻微晃动，在顶板内侧贴 1~2 mm 自粘泡棉垫即可，
    不要擅自加高柱或缩小显示窗。
  ★ 若不接受外形变大：可改「右侧 2 颗加长 M3 穿过 LCD 安装孔 + 左侧 2 个卡扣」，
    外形可回到 105.20x67.00，但只剩 2 颗螺丝、卡扣对打印精度敏感。需整套重出。

  【显示窗：单版本 + 按实测 A.A 放大让位】
  ★ 已实测确认 LCD A.A（发光显示区）= 73.44 x 48.96 mm，本版据此定窗。
  ★ 原 A / B 双版本窗口（69.00x47.60 / 72.00x47.60）都小于 A.A，会切掉亮区
    边缘像素，已全部作废。本目录只剩一个上盖 STL。
  ★ 现窗口 {P.WIN_W:.2f} x {P.WIN_H:.2f} mm（四角 R{P.WIN_R:.1f}），
    四周各比 A.A 放大 {P.WIN_CLEAR_X:.2f} / {P.WIN_CLEAR_Y:.2f} mm。
    取舍：理想装配下四周会露出 <=0.5 mm 极窄黑边，但绝不遮挡显示内容。
    请转告商家：不要按旧版习惯把窗口缩小或移回居中。
  ★ 偏心量仍待实测：显示区左缘到模块左缘 = L，右缘到模块右缘 = R。
    当前 WIN_OFFSET_X = {P.WIN_OFFSET_X:.2f}（窗口中心 X={P.WIN_CX:.2f} / Y={P.WIN_CY:.2f}，
    外壳中心 X={P.W/2:.2f}），由规格书尺寸链 2.77 mm 与实物图像素 2.52 mm 推算，未实测。
    若实测 (L-R)/2 不同：改 params_v2.py 的 WIN_OFFSET_X 一行，
    重跑 build_v2.py / make_pdf_v2.py / make_views.py / build_step.py /
    make_preview.py / freecadcmd build_fcstd.py 即可同步全部交付物。

  【打样前必测：整机高度】把 LCD 屏和 ESP32 系统板装到 PCB 上后，
  量「PCB 顶面到整机最高点」的距离。本设计内腔从 PCB 顶面算起留 9.20 mm
  （顶板内表面 Z=14.2，PCB 顶面 Z=5.0；核心板直焊顶面约 9.1、LCD 顶面约 12.1 为最高）。
  若实测 >9.2 mm，请改 params_v2.py 的 Z_TOP_IN / H_TOTAL 后重出图，否则会顶到顶板。

  【孔径定案：PCB 四角 φ4 孔，不是 φ2】
  工程 .epru 里 4 个 FILL CIRCLE 第三个参数是【半径】78.7402 mil = 2.000 mm，
  孔径 = Φ4.000；用户导出的 PCB PDF 底层隔离圈实测 4.48 mm 也吻合。
  φ4 是 M3 的加大过孔（M3 标准过孔 φ3.2~3.4），不是 M4（M4 需 φ4.5 过孔）。
  本版 φ4 孔只用于底座定位销对准，不再过螺丝。

  【LCD 屏固定】按你确认：不用 M3 螺丝/螺母锁 LCD，屏幕靠 H1 插座插装、
  底座定位销把 PCB 定位、顶板压住黑边限位；LCD 那 2 个安装孔空置不用。
  4 颗 M3 全部用于上盖与底座的连接，互不干扰。

【一、文件与工艺】
  1) 3D 打印（推荐，一次成型）
     搜索：3D打印服务 代打 / 3D打印 光敏树脂 打样 / FDM 3D打印 PETG 定制 / 嘉立创3D打印
     发给商家（2 个 STL，一次下单）：
       ESP32S3_LCD_全覆盖外壳_上盖_3D打印.stl
       ESP32S3_LCD_全覆盖外壳_底座_3D打印.stl
       + ESP32S3_LCD_全覆盖外壳_工程图.pdf（给尺寸与要求）
     材料：不透明 PLA / PETG（便宜、绝缘）；要更精细选 SLA 光敏树脂/韧性树脂
     禁止：金属打印、碳纤维填充、导电料、金属漆、电镀
  2) 若想用亚克力激光切割：这套是闭合腔体，不能直接切平板叠层，
     请让商家按 PDF 剖面改为「顶板 + 4 条边框 + 底板」5 件粘接，或直接选 3D 打印。
  3) CNC：发 STL + PDF，材料 POM/ABS，别用铝（会屏蔽天线）。

【二、复制给商家的一段话】
  两件 3D 打印外壳，外形 {P.W:.2f} x {P.H:.2f} x {P.H_TOTAL:.2f} mm，整套约 {vol_all:.0f} cm3。
  上盖顶板厚 1.8、侧壁厚 1.6、总高 16.0；显示窗 {P.WIN_W:.2f} x {P.WIN_H:.2f} mm
  （四角 R1.5），窗口中心 X={P.WIN_CX:.2f} / Y={P.WIN_CY:.2f}（相对外壳中心左移
  {-P.WIN_OFFSET_X:.2f} mm，为对准偏心屏显示区），请勿擅自把窗口移回居中；
  顶板完整无镂空，仅显示窗 + Φ4 复位孔；四边侧壁统一开口带
  Z 4.00~14.20（天线让位窗 27.00 与 I2C 合并宽窗平齐），窗口已按带壳插头与线材留余量，
  窗口四周已按实测 A.A 放大让位以吸收装配偏差，请勿擅自缩小或移回居中；
  顶板天线区不要开洞、不要加支撑。
  外壳四角有 4 个 Φ{P.POST_D:.1f} 连接柱（在 PCB 板框之外，别误当成 PCB 安装孔）；
  底座另有 4 个 Φ{P.BASE_BOSS_D:.1f} 支撑台和 Φ{P.LOCATOR_D:.1f} 定位销，用来定位 PCB。
  不透明绝缘非金属，不喷金属漆；请按 STL 原尺寸 1:1 打印，不要缩放、不要加支撑在窗口内。
  建议顶板朝上平放打印，层高 0.2 mm 以下，窗口与四角连接柱精度优先。

【三、自己买的配件】
  M3x12 沉头自攻螺丝 x4     搜：M3*12 沉头 自攻螺丝 304
  硅胶脚垫 Φ8 x4（可选）     搜：硅胶脚垫 圆形 自粘 8mm
  1~2 mm 自粘泡棉垫（可选）  贴在顶板内侧，压住 LCD 板顶消除轻微晃动

【四、装配顺序】
  1. 底座朝上，PCB 放入：4 个 φ4 孔对准底座 4 个 Φ{P.BASE_BOSS_D:.1f} 支撑台上的
     Φ{P.LOCATOR_D:.1f} 定位销（PCB 底面 Z=3.4）。四角连接柱位在 PCB 板框之外，
     不要试图把螺丝穿进 PCB 孔。
  2. LCD 屏插 PCB 的 H1 排座；ESP32 系统板直焊在 PCB 上，天线端对准
     【上边侧壁让位窗】并穿出壳外（顶板完整盖住，不包住天线外露段）。
     LCD 不上 M3 螺丝/螺母，那 2 个安装孔空置。
  3. 扣上上盖：四边接口开窗对准 USB1 / CN3 / 4x I2C / 双 Type-C；顶板压住屏幕黑边，
     只露出显示区；上盖 4 个 Φ{P.POST_D:.1f} 柱正好对准底座四角的 Φ{P.POST_D:.1f} 台。
  4. 从底部 4 个沉孔拧入 M3x12 自攻螺丝，经底座 Φ3.4 通孔直接拧进上盖柱
     （底孔 Φ2.6）；螺丝【不穿过 PCB、不穿过 LCD】。塑料柱吃力即可，勿过度拧紧。
  5. 若顶板与 LCD 板之间约 2.1 mm 间隙导致轻微晃动，贴 1~2 mm 泡棉垫再扣合。

【五、接口开窗对应（PCB 左旋 90°、天线朝上的正视方位）】
  ★ 四边所有开口统一 Z 4.00~14.20（下沿留 1.60 实壁、上沿齐平顶板内表面），
    天线让位窗与 I2C 插座窗完全平齐；窗口按「带壳插头 + 线材外径 + 插拔空间」留余量。
  ★ Rev I 外形每边 +3.00 mm，以下坐标全部相对旧版 +3.00，但相对 PCB 的位置不变。
  上边：天线让位窗 27.00 宽（{P.ANT_X0:.2f}~{P.ANT_X1:.2f}）+ 2 段 I2C 合并宽窗
        （{P.I2C_GROUPS[0][0]:.2f}~{P.I2C_GROUPS[0][1]:.2f} /
         {P.I2C_GROUPS[1][0]:.2f}~{P.I2C_GROUPS[1][1]:.2f}，各覆盖 2 个 XH2.54-4P，
         座中心距仅 12.96 故不再各开 12mm 小窗；段间各留 2.00 加强筋）+ 顶板 Φ4 复位键孔
  下边：ESP32 核心板（直接焊在 PCB 上）自带 2 个 Type-C（UART / USB）
        共用 36.00 宽窗（{P.DUAL_USBC_X0:.2f}~{P.DUAL_USBC_X1:.2f}）
  右边：5V Type-C 18.00 宽窗（{P.RIGHT_5V_Y0:.2f}~{P.RIGHT_5V_Y1:.2f}）
        + XH2.54-5P 23.00 宽窗（{P.RIGHT_XH_Y0:.2f}~{P.RIGHT_XH_Y1:.2f}）
  左边：封闭，无外部接口
  底部：4 个 M3 螺丝沉孔（外壳四角，PCB 板框之外）
  【余量依据】XH2.54 带扣插头约 13~15 宽、线束出口需 8~10 高；Type-C 线端注塑壳
  约 12~16 宽 x 6~8 厚、线材 Φ3~5，折弯另需 3~5。开口带 10.20 高、各窗宽度
  均含上述余量；打样前建议拿实际线材比一下，若仍紧可改 params_v2.py 加宽。

【六、天线净空】
  顶板完整封闭、不镂空；天线及模组端部从上边侧壁让位窗穿出，外露段不被壳体包住。
  壳体是绝缘塑料不屏蔽；4 个连接柱在四角、距天线中心均 >45 mm，远超 2.4GHz 近场 20 mm。
  核心板为直接焊接（板间距约 2.5、板厚 1.6），天线铜层约 Z 8~9，顶板内表面
  Z 14.2 与天线之间约 5mm 塑料间隙，介电加载较弱；
  装好后对比悬空 / 吸铁板的 WiFi RSSI，若掉 >3dB 可把天线端再多伸出 5~10 mm，
  或把顶板天线区内表面减薄 0.8 mm（外表面仍平整无洞）。
  接线与安装时避免整块金属背板贴近天线端。

【七、文件清单】
  ESP32S3_LCD_全覆盖外壳_上盖_3D打印.stl        上盖（唯一版本，窗口 74.40x50.00）
  ESP32S3_LCD_全覆盖外壳_底座_3D打印.stl         底座（含 4 定位销 + 4 连接台）
  ESP32S3_LCD_全覆盖外壳_上盖_加工图.dxf        1:1 上盖俯视 + 四边侧壁展开
  ESP32S3_LCD_全覆盖外壳_底座_加工图.dxf        1:1 底座俯视
  ESP32S3_LCD_全覆盖外壳_装配工程图.dxf         尺寸/剖面/BOM/技术说明（可编辑）
  ESP32S3_LCD_全覆盖外壳_工程图.pdf             3 页 A4，可直接发给商家
  ESP32S3_LCD_全覆盖外壳_三视图.pdf             A3 三视图 + 辅助下视图（重点看这页）
  ESP32S3_LCD_全覆盖外壳_三视图.dxf             1:1 可编辑三视图
  ESP32S3_LCD_全覆盖外壳_上盖_可编辑.step          STEP 实体（同上盖 STL）
  ESP32S3_LCD_全覆盖外壳_底座_可编辑.step        STEP 实体（同底座 STL）
  ESP32S3_LCD_全覆盖外壳_装配体_含PCB参考.step   3 件装配，PCB 为参考件不打印
  外壳实物报价.csv                              实物制作费用
  params_v2.py / build_v2.py                     STL/DXF/PDF 参数化源
  build_step.py                                  STEP 参数化源
  build_fcstd.py                                 生成 .FCStd 的 FreeCADCmd 脚本
  ESP32S3_LCD_外壳工程.FCStd                     FreeCAD 工程文件（双击即开）
  FreeCAD_一键生成工程.FCMacro                   可选：补颜色/视图的着色版宏

  【STEP 实体文件说明】3 个 .step 是 AP214 BREP 解析实体（圆角是真圆弧、
    螺丝孔是真圆柱面），可在 FreeCAD / SolidWorks / 立创EDA / Fusion 里打开测量、
    改特征、做装配，不是 STL 那种三角网格；发给商家打印仍以 .stl 为准。
    装配体 STEP 内含 3 个独立实体：上盖 / 底座 / PCB 参考板，
    在 FreeCAD 里可用「Part → 拆分」逐件隐藏。PCB 参考板只是用来检查
    装配间隙的参考件，不是打印件，不要发给商家。
    改尺寸后按【零】里的脚本清单全部重跑一遍，
    否则 STL / STEP / FCStd / PDF 会互相不一致。

  【FreeCAD 工程文件】STEP 是中性交换格式，不是 FreeCAD 工程；原生工程是
    .FCStd（一个文档里装多个命名对象）。本目录已附现成的
    ESP32S3_LCD_外壳工程.FCStd，双击即可打开，内含上盖 / 底座 /
    PCB 参考板 3 个命名实体（本机 FreeCAD 1.1.4 命令行内核生成并回读验证）。
    只看整体也可打开「装配体_含PCB参考.step」一个文件（内含 3 个实体）。
    命令行内核不带 GuiDocument（颜色 / 相机）；想要着色 + 等轴测视图，
    在 FreeCAD 里执行 FreeCAD_一键生成工程.FCMacro（宏 → 宏... → 执行），
    会覆盖同名 .FCStd 补上外观，几何不变。
    重新生成： "C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" build_fcstd.py
"""
with open(os.path.join(OUT, "给商家的下单说明.txt"), "w", encoding="utf-8") as f:
    f.write(note)

# ---------------- 几何摘要（供 PDF 用） ----------------
geom = dict(
    W=P.W, H=P.H, R_OUT=P.R_OUT, T_WALL=P.T_WALL, T_BASE=P.T_BASE,
    H_TOTAL=P.H_TOTAL, H_CAVITY=P.H_CAVITY, Z_PCB_BOT=P.Z_PCB_BOT,
    Z_PCB_TOP=P.Z_PCB_TOP, Z_TOP_IN=P.Z_TOP_IN, T_TOP=P.T_TOP,
    OX=P.OX, OY=P.OY, PCB_PX=P.PCB_PX, PCB_PY=P.PCB_PY, PCB_R=P.PCB_R,
    WIN=list(WIN), LCD_AA=list(LCD_AA),
    WIN_W=P.WIN_W, WIN_H=P.WIN_H,
    LCD_AA_W=P.LCD_AA_X, LCD_AA_H=P.LCD_AA_Y,
    WIN_CLEAR_X=P.WIN_CLEAR_X, WIN_CLEAR_Y=P.WIN_CLEAR_Y,
    WIN_R=P.WIN_R,
    WIN_OFFSET_X=P.WIN_OFFSET_X, WIN_CX=P.WIN_CX, WIN_CY=P.WIN_CY,
    ANT=[P.ANT_X0, P.ANT_Y0, P.ANT_X1, P.H],
    ANT_SLOT_Z0=P.ANT_SLOT_Z0, ANT_SLOT_Z1=P.ANT_SLOT_Z1,
    RESET_POS=list(P.RESET_POS), RESET_HOLE_D=P.RESET_HOLE_D,
    REV="I",
    HOLES=P.HOLES, SCREW_POS=P.SCREW_POS, PARTS=P.PARTS,
    SLOTS=[[n, list(b), z0, z1, d] for n, b, z0, z1, d in P.SLOTS],
    I2C_X=P.I2C_X, I2C_SLOT_W=P.I2C_SLOT_W,
    OPEN_Z0=P.OPEN_Z0, OPEN_Z1=P.OPEN_Z1, RIB_W=P.RIB_W,
    I2C_GROUPS=[list(g) for g in P.I2C_GROUPS],
    DUAL_USBC=[P.DUAL_USBC_X0, P.DUAL_USBC_X1],
    RIGHT_SLOTS=[[P.RIGHT_5V_Y0, P.RIGHT_5V_Y1],
                 [P.RIGHT_XH_Y0, P.RIGHT_XH_Y1]],
    POST_D=P.POST_D, SCREW_HOLE_D=P.SCREW_HOLE_D, SCREW_CS_D=P.SCREW_CS_D,
    BASE_BOSS_D=P.BASE_BOSS_D, LOCATOR_D=P.LOCATOR_D,
    GAP=P.GAP, SHIFT=P.SHIFT,
    PCB_HOLE_D=P.PCB_HOLE_D, POST_PILOT_D=P.POST_PILOT_D,
    SCREW_CS_DEPTH=P.SCREW_CS_DEPTH,
    ANT_CENTER=list(P.ANT_CENTER),
    volumes=files,
)
with open(os.path.join(HERE, "geom_v2.json"), "w", encoding="utf-8") as f:
    json.dump(geom, f, ensure_ascii=False, indent=2)

print("CSV / TXT / geom.json done")
print("TOTAL volume:", round(vol_all, 2), "cm3")
