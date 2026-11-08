# -*- coding: utf-8 -*-
"""ESP32S3_LCD 全覆盖不透明外壳 Rev G —— 生成 STL / DXF / 报价 / 下单说明

结构：上盖（完整不透明顶板 + 四周侧壁 + 4 螺丝柱，仅开显示区窗口 + Φ4 复位孔）
      底座（平板 + 4 支撑台 + 4 沉孔）
      Rev G：四边所有对外开口统一开口带 Z 4.00~14.20，上下沿完全平齐；
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
    # Rev G：顶板完整无镂空；天线让位与所有接口窗统一 Z 开口带（止于顶板内表面）
    ant_slot = prism(box(P.ANT_X0, P.ANT_Y0, P.ANT_X1, P.H + 2.0),
                     P.ANT_SLOT_Z0, P.ANT_SLOT_Z1)
    reset = cyl(P.RESET_HOLE_D / 2, P.Z_TOP_IN - 0.2, P.H_TOTAL + 0.5,
                *P.RESET_POS)
    cut = [outer, cavity, window, ant_slot, reset]
    for name, (x0, y0, x1, y1), z0, z1, desc in P.SLOTS:
        cut.append(prism(box(x0, y0, x1, y1), z0, z1))
    shell = bdiff(cut)

    # 4 个螺丝柱（带自攻底孔，柱顶嵌进顶板 0.2）
    posts = []
    for x, y in P.HOLES:
        post = bdiff([cyl(P.POST_D / 2, P.POST_Z0, P.POST_Z1, x, y),
                      cyl(P.POST_PILOT_D / 2, P.POST_Z0 - 0.2, P.POST_PILOT_Z1, x, y)])
        posts.append(post)
    # 顶板完整封闭，无需加强筋
    return bunion([shell] + posts)


# ---------------- 底座 ----------------
def build_base():
    body = prism(OUTER, 0, P.T_BASE)
    bosses = [cyl(P.POST_D / 2, P.T_BASE - 0.1, P.Z_PCB_BOT, x, y) for x, y in P.HOLES]
    solid = bunion([body] + bosses)
    cuts = []
    for x, y in P.HOLES:
        cuts.append(cyl(P.SCREW_HOLE_D / 2, -1.0, P.Z_PCB_BOT + 0.2, x, y))
        cuts.append(cyl(P.SCREW_CS_D / 2, -1.0, P.SCREW_CS_DEPTH, x, y))
    return bdiff([solid] + cuts)


top_a = build_top(P.WIN_A_W, P.WIN_A_H)
top_b = build_top(P.WIN_B_W, P.WIN_B_H)
base = build_base()

files = {}
for name, mesh in [("ESP32S3_LCD_全覆盖外壳_上盖_A版_3D打印.stl", top_a),
                   ("ESP32S3_LCD_全覆盖外壳_上盖_B版_3D打印.stl", top_b),
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

WIN_A = (P.WIN_CX - P.WIN_A_W / 2, P.WIN_CY - P.WIN_A_H / 2,
         P.WIN_CX + P.WIN_A_W / 2, P.WIN_CY + P.WIN_A_H / 2)

# ---- 1. 上盖 1:1 加工图（俯视 + 四边展开） ----
d = new_doc(LAYERS)
m = d.modelspace()
m.add_lwpolyline(OUTER_PTS, close=True, dxfattribs={"layer": "OUTLINE"})
m.add_lwpolyline(rr_pts(P.WIN_A_W, P.WIN_A_H, P.WIN_R, WIN_A[0], WIN_A[1]),
                 close=True, dxfattribs={"layer": "WINDOW"})
m.add_lwpolyline(rr_pts(P.PCB_PY, P.PCB_PX, P.PCB_R, P.OX, P.OY), close=True,
                 dxfattribs={"layer": "PCB_REF", "linetype": "DASHED"})
# 侧壁天线让位窗（俯视投影为靠上边窄条；顶板完整不开洞）
RECT(m, P.ANT_X0, P.ANT_Y0, P.ANT_X1, P.H, "ANT")
# 顶板复位键孔
m.add_circle(P.RESET_POS, P.RESET_HOLE_D / 2, dxfattribs={"layer": "HOLE"})
T(m, "复位孔 Φ4.0", P.RESET_POS[0] + 3, P.RESET_POS[1] + 1, 1.8, "NOTE")
for x, y in P.HOLES:
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
DIMH(m, WIN_A[0], WIN_A[2], P.H, f"{P.WIN_A_W:.2f} (A版)", 7)
DIMV(m, WIN_A[1], WIN_A[3], P.W, f"{P.WIN_A_H:.2f}", 9)
DIMH(m, P.ANT_X0, P.ANT_X1, P.H, f"{P.ANT_X1-P.ANT_X0:.2f} 侧壁让位窗(顶板不开)", 15)
DIMH(m, P.HOLES[0][0], P.HOLES[1][0], 0, "91.34", -20)
DIMV(m, P.HOLES[0][1], P.HOLES[2][1], 0, "48.70", -20)
T(m, f"上盖俯视 1:1  (单位 mm)  窗口按 A 版 {P.WIN_A_W:.2f} x {P.WIN_A_H:.2f}", 0, -30, 3.6)
T(m, f"B 版窗口 {P.WIN_B_W:.2f} x {P.WIN_B_H:.2f}（其余相同），见 B 版 STL", 0, -35, 2.8, "NOTE")
T(m, "顶板完整封闭、无镂空；仅显示窗 + Φ4 复位孔", 0, P.H + 22, 3.0, "ANT")
T(m, "四边统一开口带 Z 4.00~14.20：天线 27.00 与 I2C 宽窗平齐；双 Type-C 36.00；5V 18.00 / XH-5P 23.00",
  0, P.H + 27, 2.8, "ANT")
T(m, f"Rev G 偏心屏：显示窗中心 X={P.WIN_CX:.2f} / Y={P.WIN_CY:.2f}"
     f"（相对外壳中心左移 {-P.WIN_OFFSET_X:.2f}），窗口左缘 X={WIN_A[0]:.2f}；请勿居中",
  0, P.H + 32, 2.8, "ANT")
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
for x, y in P.HOLES:
    m2.add_circle((x, y), P.SCREW_HOLE_D / 2, dxfattribs={"layer": "HOLE"})
    m2.add_circle((x, y), P.POST_D / 2, dxfattribs={"layer": "CENTER", "linetype": "DASHED"})
    LN(m2, (x - 5, y), (x + 5, y), "CENTER")
    LN(m2, (x, y - 5), (x, y + 5), "CENTER")
DIMH(m2, 0, P.W, 0, "105.20", -11)
DIMV(m2, 0, P.H, 0, "67.00", -11)
DIMH(m2, P.HOLES[0][0], P.HOLES[1][0], 0, "91.34", -20)
DIMV(m2, P.HOLES[0][1], P.HOLES[2][1], 0, "48.70", -20)
T(m2, "底座俯视 1:1 (单位 mm)", 0, -30, 3.6)
T(m2, "4x Φ3.4 通孔 + 底面 Φ6.5 深 1.6 沉孔（M3 沉头螺丝）", 0, P.H + 8, 2.8)
T(m2, "4x Φ7 支撑台 高 1.0（PCB 底面 Z=3.4）", 0, P.H + 13, 2.8)
T(m2, "底板厚 2.40；总装配高 16.00", 0, P.H + 23, 2.8)
d2.saveas(os.path.join(OUT, "ESP32S3_LCD_全覆盖外壳_底座_加工图.dxf"))

# ---- 3. 装配工程图 DXF（剖面 + BOM + 技术说明 + 标题栏） ----
d3 = new_doc(LAYERS)
m3 = d3.modelspace()
# 上盖俯视（缩略，1:1）
m3.add_lwpolyline(OUTER_PTS, close=True, dxfattribs={"layer": "OUTLINE"})
m3.add_lwpolyline(rr_pts(P.WIN_A_W, P.WIN_A_H, P.WIN_R, WIN_A[0], WIN_A[1]),
                  close=True, dxfattribs={"layer": "WINDOW"})
RECT(m3, P.ANT_X0, P.ANT_Y0, P.ANT_X1, P.H, "ANT")
m3.add_circle(P.RESET_POS, P.RESET_HOLE_D / 2, dxfattribs={"layer": "HOLE"})
for x, y in P.HOLES:
    m3.add_circle((x, y), P.POST_D / 2, dxfattribs={"layer": "HOLE"})
DIMH(m3, 0, P.W, 0, "105.20", -11)
DIMV(m3, 0, P.H, 0, "67.00", -11)
T(m3, "上盖俯视 1:1", 0, -18, 3.4)
LN(m3, (-5, 33.5), (0, 33.5), "SECTION")
LN(m3, (P.W, 33.5), (P.W + 5, 33.5), "SECTION")
T(m3, "A", -8, 35, 3.2, "SECTION"); T(m3, "A", P.W + 6, 35, 3.2, "SECTION")

# A-A 剖面 2:1
SX0, SZ, SC = 150.0, 20.0, 2.0
def PP(x, z): return (SX0 + x * SC, SZ + z * SC)
sec = [PP(0, P.T_BASE), PP(P.W, P.T_BASE), PP(P.W, P.H_TOTAL),
       PP(P.W - P.T_WALL, P.H_TOTAL), PP(P.W - P.T_WALL, P.Z_TOP_IN),
       PP(P.T_WALL, P.Z_TOP_IN), PP(P.T_WALL, P.H_TOTAL),
       PP(0, P.H_TOTAL)]
m3.add_lwpolyline(sec, close=True, dxfattribs={"layer": "SECTION"})
# 顶板窗口断口（剖面在 y=33.5 穿过窗口）
wa, wb = WIN_A[0] * SC, WIN_A[2] * SC
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
    "2. 窗口 A 版 69.00x47.60（保守压边）；B 版 72.00x47.60（贴 AA 73.44x48.96）。",
    "2b.【Rev G 偏心屏对位】ATK-MD0350 显示区不居中：右侧黑边宽、左侧窄，上下对称。",
    "   窗口中心 X 由 52.60 左移至 49.85（WIN_OFFSET_X=-2.75），Y 保持 33.50；",
    "   只露显示区，四周黑边由完整不透明顶板压住。依据 LCM 规格书 OUTLINE 84.69x55.26",
    "   / LCD A.A 73.44x48.96 长边尺寸链偏心 2.77 mm，实物图逐像素 2.52 mm，取 2.75。",
    "   打样前点亮屏幕实测：亮区左缘到模块左缘 L、右缘到模块右缘 R，(L-R)/2 即偏移量；",
    "   不符改 params_v2.py 的 WIN_OFFSET_X 一行并重跑全部脚本。",
    "3. 顶板完整封闭不镂空；四边开口统一 Z 4.00~14.20，天线让位窗与 I2C 窗上下沿平齐。",
    "4. 天线投影 20mm 内禁止金属件、覆铜；4 个螺丝柱距天线中心均 >45mm。",
    "5. 上边：2 段 I2C 合并宽窗（4 个 XH2.54-4P，座距 12.96）+ Φ4 复位孔 + 27.00 天线让位窗。",
    "   下边：ESP32 核心板（直焊）双 Type-C 共用 36.00 窗；右边：5V 18.00 + XH-5P 23.00。",
    "   所有窗口按带壳插头宽 14~16 / 线材 Φ3~5 留余量，非按母座贴边开孔。",
    "6. 4x M3x12 自攻螺丝自底面沉孔穿入，经 PCB 4x φ4 孔拧入上盖 Φ7 柱（底孔 Φ2.6）。",
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
T(m3, "图号 ESP32S3-LCD-EN-D", TX + 2, TY + 10.5, 2.3)
T(m3, "Rev G", TX + 94, TY + 10.5, 2.3)
T(m3, "单位 mm  比例 1:1 / 2:1", TX + 2, TY + 2.5, 2.3)
T(m3, "2026-11-07", TX + 94, TY + 2.5, 2.3)
d3.saveas(os.path.join(OUT, "ESP32S3_LCD_全覆盖外壳_装配工程图.dxf"))
print("DXF x3 done")

# ---------------- 报价 CSV ----------------
vol_top = top_a.volume / 1000
vol_base = base.volume / 1000
vol_all = vol_top + vol_base
quote = [
    ["项目", "规格/工艺", "数量", "单价参考(¥)", "小计(¥)", "备注"],
    ["上盖 FDM 3D打印", f"PLA/PETG 不透明，约 {vol_top:.1f} cm3", "1件", "16~26", "16~26", "发 STL，推荐 PETG"],
    ["底座 FDM 3D打印", f"PLA/PETG，约 {vol_base:.1f} cm3", "1件", "14~24", "14~24", "与上盖同单打印更便宜"],
    ["整套 SLA 光敏树脂", f"约 {vol_all:.1f} cm3，精度高", "1套", "55~95", "55~95", "替代方案，表面更好"],
    ["整套 亚克力/CNC", "需改造为叠层结构", "1套", "120~220", "120~220", "不推荐，成本高"],
    ["M3 自攻螺丝", "M3x12 沉头 304 不锈钢", "4颗", "0.4~0.8", "1.6~3.2", "搜：M3*12 沉头螺丝"],
    ["φ4→φ3 尼龙衬套", "M3 定位垫圈（可选）", "4片", "0.3~0.8", "1~3", "吃掉 φ4 孔约 1mm 松量"],
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
note = f"""ESP32-S3 LCD 全覆盖显示屏外壳 Rev G —— 淘宝打样下单说明
==========================================================
  【零、打样前必测两项：亮区尺寸 + 偏心量】
  1) 点亮屏幕，用游标卡尺量「发光显示区」的宽 x 高：
    - 约 70.46 x 49.07 mm 或更小 → 发【上盖_A版】STL（窗口 69.00 x 47.60，黑边全包住）
    - 约 73.44 x 48.96 mm        → 发【上盖_B版】STL（窗口 72.00 x 47.60）
  2) 量偏心：显示区左缘到模块左缘 = L，显示区右缘到模块右缘 = R。
     ★ Rev G 已按 (L-R)/2 = -2.75 mm（显示区偏左、右侧黑边宽）把窗口中心
       从外壳中心 X=52.60 左移到 X=49.85，Y=33.50 不变；上下黑边对称故不调 Y。
       依据：LCM 规格书 OUTLINE 84.69x55.26 / LCD A.A 73.44x48.96 长边尺寸链
       偏心 2.77 mm；你发的实物商品图逐像素换算 2.52 mm，取 2.75。
       窗口仍只露显示区，四周黑边由完整不透明顶板压住（已确认）。
     若实测偏移不同：改 params_v2.py 的 WIN_OFFSET_X 一行，
     重跑 build_v2.py / make_pdf_v2.py / make_views.py / build_step.py /
     make_preview.py / freecadcmd build_fcstd.py 即可同步全部交付物。
  两版只有窗口长度不同，其余完全一致。底座两版通用。

  【必测第二项：高度】把 LCD 屏和 ESP32 系统板装到 PCB 上后，
  量「PCB 顶面到整机最高点」的距离。本设计内腔从 PCB 顶面算起留 9.20 mm
  （顶板内表面 Z=14.2，PCB 顶面 Z=5.0；核心板直焊顶面约 9.1、LCD 顶面约 12.1 为最高）。
  若实测 >9.2 mm，请改 params_v2.py 的 Z_TOP_IN / H_TOTAL 后重出图，否则会顶到顶板。

  【孔径与螺丝已定案：φ4 孔 + M3 螺丝，不是 M4】
  Rev C 写的「φ2 孔 + M2 螺丝」是错的，已纠正。三条证据：
    1) 工程 .epru 里 4 个 FILL CIRCLE（Multi-Layer = NPTH 孔）第三个参数是【半径】
       78.7402 mil = 2.000 mm，所以孔径 = 2×2.000 = φ4.000 mm。
       之前把「半径 2mm」读成了「直径 2mm」；板框那个 2.0 是圆角 R2，不是孔。
    2) PCB_PCB1_1_2026-11-07.pdf 底层铜皮四角白色无铜圆实测 4.48 mm
       = φ4.0 孔 + 0.24 mm 隔离环；PDF 四角那个 2.000 mm 圆是板框圆角弧包围盒。
    3) 你实测 M3 螺丝（光杆 φ3.0）能穿过并固定 LCD 屏 → 孔必然 ≥φ3，与 φ2 矛盾。
  为什么不是 M4：φ4.0 恰好是 M4 螺杆的名义直径，塞进 φ4.0 孔几乎零间隙，
    板厂钻孔公差 ±0.1 加四孔位累积公差至少有一颗会卡死（M4 需 φ4.5 过孔）；
    M4 沉头 φ8 / 螺丝柱 Φ9 距板边只有 5.7 mm，塑料件还容易崩边。
    φ4.0 实际是【M3 的加大过孔】（M3 标准过孔 φ3.2~3.4），你手上的 M3 正好能用。
  本版配置：M3×12 沉头自攻 ×4；底座通孔 Φ3.4、底面沉孔 Φ6.5 深 1.6、
    上盖 Φ7 螺丝柱、柱内 Φ2.6 自攻底孔（盲孔深至 Z=13.8）。
  φ4 孔配 M3 有约 1 mm 径向松量：PCB 被底座 4 个 Φ7 支撑台与上盖柱夹紧，
    装配时目视居中后拧紧即可；想更精准可加 4 片 φ4→φ3 尼龙衬套或 M3 大平垫（外径 Φ7）。
  仍建议卡尺复量一次四角孔径；若实测确实是 φ2（与 M3 实测矛盾，可能性很低），
    告诉我，我把螺丝改回 M2 或用 φ3.2 钻头轻扩四孔。

  【LCD 屏固定：两种方案，本版按 A 出图】
  方案 A（推荐，本版）：屏幕靠 H1 插座 + 顶板压住黑边定位，不另配螺丝；
    外壳 4 颗 M3 螺丝独占 PCB 四角孔，装配最简单、顶板最完整。
  方案 B（若你坚持用 M3 螺丝+螺母把 LCD 屏锁在 PCB 上）：那 2 颗螺丝会占用
    PCB 四角孔中的 2 个，与上盖柱冲突。需我把那 2 处改成「长 M3 螺丝一穿到底 +
    顶板开 Φ7 让位孔」，或改为 2 螺丝 + 2 卡扣。告诉我 LCD 屏安装孔对应哪两个角即可重出图。

【一、文件与工艺】
  1) 3D 打印（推荐，一次成型）
     搜索：3D打印服务 代打 / 3D打印 光敏树脂 打样 / FDM 3D打印 PETG 定制 / 嘉立创3D打印
     发给商家（2 个 STL，一次下单）：
       ESP32S3_LCD_全覆盖外壳_上盖_A版_3D打印.stl   （或 B 版，二选一）
       ESP32S3_LCD_全覆盖外壳_底座_3D打印.stl
       + ESP32S3_LCD_全覆盖外壳_工程图.pdf（给尺寸与要求）
     材料：不透明 PLA / PETG（便宜、绝缘）；要更精细选 SLA 光敏树脂/韧性树脂
     禁止：金属打印、碳纤维填充、导电料、金属漆、电镀
  2) 若想用亚克力激光切割：这套是闭合腔体，不能直接切平板叠层，
     请让商家按 PDF 剖面改为「顶板 + 4 条边框 + 底板」5 件粘接，或直接选 3D 打印。
  3) CNC：发 STL + PDF，材料 POM/ABS，别用铝（会屏蔽天线）。

【二、复制给商家的一段话】
  两件 3D 打印外壳，外形 105.20 x 67.00 x 16.00 mm，整套约 {vol_all:.0f} cm3。
  上盖顶板厚 1.8、侧壁厚 1.6、总高 16.0；显示窗 {P.WIN_A_W:.2f} x {P.WIN_A_H:.2f} mm
  （四角 R1.5），窗口中心 X={P.WIN_CX:.2f} / Y={P.WIN_CY:.2f}（相对外壳中心左移
  {-P.WIN_OFFSET_X:.2f} mm，为对准偏心屏显示区），请勿擅自把窗口移回居中；
  顶板完整无镂空，仅显示窗 + Φ4 复位孔；四边侧壁统一开口带
  Z 4.00~14.20（天线让位窗 27.00 与 I2C 合并宽窗平齐），窗口已按带壳插头与线材留余量，
  请勿擅自缩小窗口；顶板天线区不要开洞、不要加支撑。
  不透明绝缘非金属，不喷金属漆；请按 STL 原尺寸 1:1 打印，不要缩放、不要加支撑在窗口内。
  建议顶板朝上平放打印，层高 0.2 mm 以下，窗口与螺丝柱精度优先。

【三、自己买的配件】
  M3x12 沉头自攻螺丝 x4     搜：M3*12 沉头 自攻螺丝 304
  φ4→φ3 尼龙衬套 x4（可选）  搜：尼龙 衬套 M3 定位垫圈
  硅胶脚垫 Φ8 x4（可选）     搜：硅胶脚垫 圆形 自粘 8mm

【四、装配顺序】
  1. 底座朝上，PCB 放入：4 个 φ4 安装孔对准底座 4 个 Φ7 支撑台（PCB 底面 Z=3.4）。
  2. LCD 屏插 PCB 排座；ESP32 系统板焊/插在 PCB 上，天线端对准【上边侧壁让位窗】
     并穿出壳外（顶板完整盖住，不包住天线外露段）。
  3. 扣上上盖：四边接口开窗对准 USB1 / CN3 / 4x I2C / 双 Type-C；顶板压住屏幕黑边，
     只露出显示区；4 个 Φ7 螺丝柱正好压在 PCB 4 个孔上。
  4. 从底部 4 个沉孔拧入 M3x12 自攻螺丝，穿过 PCB φ4 孔，拧进上盖柱（底孔 Φ2.6）；
     PCB 目视居中后拧紧，勿过度用力（φ4 孔比 M3 杆大约 1mm）。
     不要过度拧紧，塑料柱吃力即可。

【五、接口开窗对应（PCB 左旋 90°、天线朝上的正视方位）】
  ★ 四边所有开口统一 Z 4.00~14.20（下沿留 1.60 实壁、上沿齐平顶板内表面），
    天线让位窗与 I2C 插座窗完全平齐；窗口按「带壳插头 + 线材外径 + 插拔空间」留余量。
  上边：天线让位窗 27.00 宽（39.10~66.10）+ 2 段 I2C 合并宽窗
        （12.00~37.10 / 68.10~93.00，各覆盖 2 个 XH2.54-4P，座中心距仅 12.96
         故不再各开 12mm 小窗；段间各留 2.00 加强筋）+ 顶板 Φ4 复位键孔
  下边：ESP32 核心板（直接焊在 PCB 上）自带 2 个 Type-C（UART / USB）
        共用 36.00 宽窗（34.00~70.00，原 26.00 太窄）
  右边：5V Type-C 18.00 宽窗（11.00~29.00，原 10.00）
        + XH2.54-5P 23.00 宽窗（32.00~55.00，原 16.50，兼容 H2 3P / H3 2P）
  左边：封闭，无外部接口
  底部：4 个 M3 螺丝沉孔
  【余量依据】XH2.54 带扣插头约 13~15 宽、线束出口需 8~10 高；Type-C 线端注塑壳
  约 12~16 宽 x 6~8 厚、线材 Φ3~5，折弯另需 3~5。开口带 10.20 高、各窗宽度
  均含上述余量；打样前建议拿实际线材比一下，若仍紧可改 params_v2.py 加宽。

【六、天线净空】
  顶板完整封闭、不镂空；天线及模组端部从上边侧壁让位窗穿出，外露段不被壳体包住。
  壳体是绝缘塑料不屏蔽；4 个螺丝柱距天线中心均 >45 mm，远超 2.4GHz 近场 20 mm。
  核心板为直接焊接（板间距约 2.5、板厚 1.6），天线铜层约 Z 8~9，顶板内表面
  Z 14.2 与天线之间约 5mm 塑料间隙，介电加载比排母插装版本更弱；
  装好后对比悬空 / 吸铁板的 WiFi RSSI，若掉 >3dB 可把天线端再多伸出 5~10 mm，
  或把顶板天线区内表面减薄 0.8 mm（外表面仍平整无洞）。
  接线与安装时避免整块金属背板贴近天线端，建议天线端朝外或悬出安装面边缘。

【七、文件清单】
  ESP32S3_LCD_全覆盖外壳_上盖_A版_3D打印.stl   A 版上盖（保守窗口）
  ESP32S3_LCD_全覆盖外壳_上盖_B版_3D打印.stl   B 版上盖（标准 AA 窗口）
  ESP32S3_LCD_全覆盖外壳_底座_3D打印.stl       底座（两版通用）
  ESP32S3_LCD_全覆盖外壳_上盖_加工图.dxf        1:1 上盖俯视 + 四边侧壁展开
  ESP32S3_LCD_全覆盖外壳_底座_加工图.dxf        1:1 底座俯视
  ESP32S3_LCD_全覆盖外壳_装配工程图.dxf         尺寸/剖面/BOM/技术说明（可编辑）
  ESP32S3_LCD_全覆盖外壳_工程图.pdf             3 页 A4，可直接发给商家
  ESP32S3_LCD_全覆盖外壳_三视图.pdf             A3 三视图 + 辅助下视图（重点看这页）
  ESP32S3_LCD_全覆盖外壳_三视图.dxf             1:1 可编辑三视图
  ESP32S3_LCD_全覆盖外壳_上盖_A版_可编辑.step    STEP 实体（同 A 版 STL）
  ESP32S3_LCD_全覆盖外壳_上盖_B版_可编辑.step    STEP 实体（同 B 版 STL）
  ESP32S3_LCD_全覆盖外壳_底座_可编辑.step        STEP 实体（同底座 STL）
  ESP32S3_LCD_全覆盖外壳_装配体_含PCB参考.step   3 件装配，PCB 为参考件不打印
  外壳实物报价.csv                              实物制作费用
  params_v2.py / build_v2.py                     STL/DXF/PDF 参数化源
  build_step.py                                  STEP 参数化源
  build_fcstd.py                                 生成 .FCStd 的 FreeCADCmd 脚本
  ESP32S3_LCD_外壳工程.FCStd                     FreeCAD 工程文件（双击即开）
  FreeCAD_一键生成工程.FCMacro                   可选：补颜色/视图的着色版宏

  【STEP 实体文件说明】4 个 .step 是 AP214 BREP 解析实体（圆角是真圆弧、
    螺丝孔是真圆柱面；上盖仅 74 个面、底座仅 30 个面），可在 FreeCAD /
    SolidWorks / 立创EDA / Fusion 里打开测量、改特征、做装配，不是 STL 那种
    三角网格；发给商家打印仍以 .stl 为准。
    装配体 STEP 内含 3 个独立实体：上盖 A 版 / 底座 / PCB 参考板，
    在 FreeCAD 里可用「Part → 拆分」逐件隐藏。PCB 参考板只是用来检查
    装配间隙的参考件，不是打印件，不要发给商家。
    改尺寸后按【零】里的脚本清单全部重跑一遍，
    否则 STL / STEP / FCStd / PDF 会互相不一致。

  【FreeCAD 工程文件】STEP 是中性交换格式，不是 FreeCAD 工程；原生工程是
    .FCStd（一个文档里装多个命名对象）。本目录已附现成的
    ESP32S3_LCD_外壳工程.FCStd，双击即可打开，内含上盖 A 版 / 底座 /
    PCB 参考板 3 个命名实体（本机 FreeCAD 1.1.4 命令行内核生成并回读验证）。
    只看整体也可打开「装配体_含PCB参考.step」一个文件（内含 3 个实体）。
    命令行内核不带 GuiDocument（颜色 / 相机）；想要着色 + 等轴测视图，
    在 FreeCAD 里执行 FreeCAD_一键生成工程.FCMacro（宏 → 宏... → 执行），
    会覆盖同名 .FCStd 补上外观，几何不变；改宏里 TOP_FILE 一行可换 B 版。
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
    WIN_A=list(WIN_A), WIN_B=[P.WIN_CX - P.WIN_B_W/2, P.WIN_CY - P.WIN_B_H/2,
                              P.WIN_CX + P.WIN_B_W/2, P.WIN_CY + P.WIN_B_H/2],
    WIN_A_W=P.WIN_A_W, WIN_A_H=P.WIN_A_H, WIN_B_W=P.WIN_B_W, WIN_B_H=P.WIN_B_H,
    WIN_R=P.WIN_R,
    WIN_OFFSET_X=P.WIN_OFFSET_X, WIN_CX=P.WIN_CX, WIN_CY=P.WIN_CY,
    ANT=[P.ANT_X0, P.ANT_Y0, P.ANT_X1, P.H],
    ANT_SLOT_Z0=P.ANT_SLOT_Z0, ANT_SLOT_Z1=P.ANT_SLOT_Z1,
    RESET_POS=list(P.RESET_POS), RESET_HOLE_D=P.RESET_HOLE_D,
    REV="G",
    HOLES=P.HOLES, PARTS=P.PARTS,
    SLOTS=[[n, list(b), z0, z1, d] for n, b, z0, z1, d in P.SLOTS],
    I2C_X=P.I2C_X, I2C_SLOT_W=P.I2C_SLOT_W,
    OPEN_Z0=P.OPEN_Z0, OPEN_Z1=P.OPEN_Z1, RIB_W=P.RIB_W,
    I2C_GROUPS=[list(g) for g in P.I2C_GROUPS],
    DUAL_USBC=[P.DUAL_USBC_X0, P.DUAL_USBC_X1],
    RIGHT_SLOTS=[[P.RIGHT_5V_Y0, P.RIGHT_5V_Y1],
                 [P.RIGHT_XH_Y0, P.RIGHT_XH_Y1]],
    POST_D=P.POST_D, SCREW_HOLE_D=P.SCREW_HOLE_D, SCREW_CS_D=P.SCREW_CS_D,
    PCB_HOLE_D=P.PCB_HOLE_D, POST_PILOT_D=P.POST_PILOT_D,
    SCREW_CS_DEPTH=P.SCREW_CS_DEPTH,
    ANT_CENTER=list(P.ANT_CENTER),
    volumes=files,
)
with open(os.path.join(HERE, "geom_v2.json"), "w", encoding="utf-8") as f:
    json.dump(geom, f, ensure_ascii=False, indent=2)

print("CSV / TXT / geom.json done")
print("TOTAL volume:", round(vol_all, 2), "cm3")
