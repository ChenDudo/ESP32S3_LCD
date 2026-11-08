# -*- coding: utf-8 -*-
"""ESP32S3_LCD 开放式底座外壳：生成可加工交付文件（STL / DXF / PDF / 报价）"""
import os, math, csv
import numpy as np
from shapely.geometry import box, Point
from shapely.ops import unary_union
import trimesh
from trimesh.creation import extrude_polygon
import ezdxf

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "deliverables")
os.makedirs(OUT, exist_ok=True)

# ---------------- 设计参数 (mm) ----------------
W, L, R_OUT = 65.6, 103.8, 3.5        # 外壳外轮廓
T_WALL      = 1.6                     # 长边侧壁厚
T_BASE      = 2.4                     # 底板厚
H_WALL      = 4.2                     # 侧壁高（自底板顶面起）
H_TOTAL     = T_BASE + H_WALL         # 6.6 总高
PCB_W, PCB_L, PCB_R = 61.8, 100.0, 2.0
PCB_X0 = T_WALL + 0.3                 # 1.9 PCB 左下角 x
PCB_Y0 = (L - PCB_L) / 2              # 1.9 PCB 左下角 y

M3_D, MAG_D = 3.2, 8.2
# PCB 安装孔（工程解析值，相对 PCB 左上角，y 向下）
PCB_HOLES = [(5.715, 4.32), (54.41, 4.32), (5.715, 95.66), (54.41, 95.66)]
M3 = [(PCB_X0 + x, PCB_Y0 + PCB_L - y) for x, y in PCB_HOLES]  # 转为外壳左下角原点
MAG = [(18.0, 22.0), (47.6, 22.0), (18.0, 36.0), (47.6, 36.0)]

def rounded_rect(w, h, r, res=24):
    return box(r, r, w - r, h - r).buffer(r, resolution=res, join_style=1)

def arc_pts(cx, cy, r, a0, a1, n=8):
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]

def rr_points(w, h, r, ox=0.0, oy=0.0, res=10):
    """圆角矩形轮廓点（逆时针，闭合）"""
    p = []
    p += arc_pts(ox + w - r, oy + h - r, r, 0, 90, res)      # 右上
    p += arc_pts(ox + r, oy + h - r, r, 90, 180, res)        # 左上
    p += arc_pts(ox + r, oy + r, r, 180, 270, res)           # 左下
    p += arc_pts(ox + w - r, oy + r, r, 270, 360, res)       # 右下
    return p

OUTER_PTS = rr_points(W, L, R_OUT)

# ---------------- 1. STL 3D 实体 ----------------
outer_poly = rounded_rect(W, L, R_OUT, 32)
all_holes = unary_union(
    [Point(x, y).buffer(M3_D / 2, resolution=32) for x, y in M3] +
    [Point(x, y).buffer(MAG_D / 2, resolution=32) for x, y in MAG]
)
base_poly = outer_poly.difference(all_holes)
base = extrude_polygon(base_poly, T_BASE)

wall_L = extrude_polygon(outer_poly.intersection(box(0, 0, T_WALL, L)), H_WALL)
wall_R = extrude_polygon(outer_poly.intersection(box(W - T_WALL, 0, W, L)), H_WALL)
wall_L.apply_translation([0, 0, T_BASE])
wall_R.apply_translation([0, 0, T_BASE])

shell = base.union(wall_L).union(wall_R)
stl_path = os.path.join(OUT, "ESP32S3_LCD_底座_3D打印.stl")
shell.export(stl_path)
print("STL:", stl_path, "watertight=", shell.is_watertight,
      "volume_cm3=", round(shell.volume / 1000, 2), "bounds=", shell.bounds.tolist())

# ---------------- 2. DXF 加工轮廓（1:1，按图层分发） ----------------
doc = ezdxf.new("R2010", setup=True)
doc.header["$INSUNITS"] = 4  # mm
for name, color in [("CUT_BASE", 7), ("CUT_HOLE", 1), ("CUT_FRAME", 3),
                    ("WALL_INNER", 5), ("PCB_REF", 8), ("ANT_ZONE", 2),
                    ("NOTE", 6)]:
    doc.layers.new(name, dxfattribs={"color": color})
msp = doc.modelspace()

msp.add_lwpolyline(OUTER_PTS, close=True, dxfattribs={"layer": "CUT_BASE"})
for x, y in M3:
    msp.add_circle((x, y), M3_D / 2, dxfattribs={"layer": "CUT_HOLE"})
for x, y in MAG:
    msp.add_circle((x, y), MAG_D / 2, dxfattribs={"layer": "CUT_HOLE"})
# 侧壁内侧线（短边整段敞开，故内腔在 y 向贯通）
msp.add_line((T_WALL, 0), (T_WALL, L), dxfattribs={"layer": "WALL_INNER"})
msp.add_line((W - T_WALL, 0), (W - T_WALL, L), dxfattribs={"layer": "WALL_INNER"})
# PCB 参考轮廓（虚线，不参与切割）
msp.add_lwpolyline(rr_points(PCB_W, PCB_L, PCB_R, PCB_X0, PCB_Y0), close=True,
                   dxfattribs={"layer": "PCB_REF", "linetype": "DASHED"})
# 天线净空区（不加工，仅示意）
msp.add_lwpolyline([(0, L), (W, L), (W, L + 20), (0, L + 20)], close=True,
                   dxfattribs={"layer": "ANT_ZONE", "linetype": "DASHED"})
for i, t in enumerate([
    "ESP32S3_LCD 底座 加工轮廓 1:1 单位 mm",
    "CUT_BASE=底板外轮廓  CUT_HOLE=4xM3 Φ3.2 + 4x磁铁 Φ8.2 通孔",
    "WALL_INNER=长边侧壁内侧线；两条短边整段敞开无侧壁",
    "PCB_REF=PCB 参考轮廓(虚线,不切割)  ANT_ZONE=天线净空(不加工)",
    "外形 65.6 x 103.8 R3.5 / 底厚 2.4 / 侧壁 1.6 x 4.2 / 总高 6.6",
]):
    msp.add_text(t, dxfattribs={"layer": "NOTE", "height": 2.2,
                                "insert": (0, L + 26 + i * 4)})
cut_path = os.path.join(OUT, "ESP32S3_LCD_底座_加工轮廓.dxf")
doc.saveas(cut_path)
print("DXF cut:", cut_path)

# ---------------- 3. 完整工程图 DXF（尺寸/剖面/BOM/标题栏） ----------------
d2 = ezdxf.new("R2010", setup=True)
d2.header["$INSUNITS"] = 4
for name, color in [("OUTLINE", 7), ("HOLE", 1), ("PCB_REF", 8), ("DIM", 4),
                    ("CENTER", 8), ("HATCH", 8), ("TEXT", 7), ("TABLE", 7),
                    ("ANT", 2), ("SECTION", 5)]:
    d2.layers.new(name, dxfattribs={"color": color})
m = d2.modelspace()

def txt(s, x, y, h=2.5, layer="TEXT", rot=0):
    m.add_text(s, dxfattribs={"layer": layer, "height": h,
                              "insert": (x, y), "rotation": rot})

def line(p1, p2, layer="OUTLINE"):
    m.add_line(p1, p2, dxfattribs={"layer": layer})

def dim_h(x1, x2, y, label, off=0):
    """水平尺寸线（自绘，全可编辑）"""
    yd = y + off
    line((x1, yd), (x2, yd), "DIM")
    line((x1, y - 1), (x1, yd + 1.5), "DIM")
    line((x2, y - 1), (x2, yd + 1.5), "DIM")
    for xx, s in ((x1, 1), (x2, -1)):
        m.add_solid([(xx, yd), (xx + s * 1.6, yd + 0.45), (xx + s * 1.6, yd - 0.45)],
                    dxfattribs={"layer": "DIM"})
    txt(label, (x1 + x2) / 2 - len(label) * 0.85, yd + 1.2, 2.6, "DIM")

def dim_v(y1, y2, x, label, off=0):
    xd = x + off
    line((xd, y1), (xd, y2), "DIM")
    line((x - 1, y1), (xd + 1.5, y1), "DIM")
    line((x - 1, y2), (xd + 1.5, y2), "DIM")
    for yy, s in ((y1, 1), (y2, -1)):
        m.add_solid([(xd, yy), (xd + 0.45, yy + s * 1.6), (xd - 0.45, yy + s * 1.6)],
                    dxfattribs={"layer": "DIM"})
    txt(label, xd - 2.0, (y1 + y2) / 2, 2.6, "DIM", 90)

# --- 俯视图 ---
m.add_lwpolyline(OUTER_PTS, close=True, dxfattribs={"layer": "OUTLINE"})
line((T_WALL, 0), (T_WALL, L), "OUTLINE")
line((W - T_WALL, 0), (W - T_WALL, L), "OUTLINE")
m.add_lwpolyline(rr_points(PCB_W, PCB_L, PCB_R, PCB_X0, PCB_Y0), close=True,
                 dxfattribs={"layer": "PCB_REF", "linetype": "DASHED"})
for x, y in M3:
    m.add_circle((x, y), M3_D / 2, dxfattribs={"layer": "HOLE"})
    line((x - 2.6, y), (x + 2.6, y), "CENTER")
    line((x, y - 2.6), (x, y + 2.6), "CENTER")
for x, y in MAG:
    m.add_circle((x, y), MAG_D / 2, dxfattribs={"layer": "HOLE"})
    line((x - 5.5, y), (x + 5.5, y), "CENTER")
    line((x, y - 5.5), (x, y + 5.5), "CENTER")
# 天线净空虚框 + 标注
m.add_lwpolyline([(0, L), (W, L), (W, L + 20), (0, L + 20)], close=True,
                 dxfattribs={"layer": "ANT", "linetype": "DASHED"})
txt("ANT 天线净空区 ≥20mm：外壳不覆盖、不延伸，禁止金属/磁体/覆铜", 0, L + 23, 3.0, "ANT")
txt("天线侧（短边）：整段敞开、无侧壁", 0, -9, 3.0, "ANT")
txt("接口侧（短边）：整段敞开，USB-C / Type-C 凸出不遮挡", 0, -14, 3.0, "ANT")
# 剖切 A-A（横向，y=55）
YSEC = 55.0
line((-6, YSEC), (0, YSEC), "SECTION")
line((W, YSEC), (W + 6, YSEC), "SECTION")
txt("A", -8, YSEC + 1, 3.5, "SECTION"); txt("A", W + 6, YSEC + 1, 3.5, "SECTION")
# 尺寸
dim_h(0, W, 0, "65.60", -12)
dim_v(0, L, 0, "103.80", -12)
dim_h(M3[0][0], M3[1][0], L, "48.70", 6)
dim_v(M3[2][1], M3[0][1], W, "91.34", 8)
dim_h(0, T_WALL, 0, "1.60", -20)
txt("4×Φ3.2 通孔 (M3) 与 PCB 4×Φ4 孔同轴", W + 16, 90, 2.6)
txt("4×Φ8.2 通孔：Φ8×2 钕铁硼磁铁，用胶固定", W + 16, 85, 2.6)
txt("磁铁距天线端 ≥67mm，位于非天线侧", W + 16, 80, 2.6, "ANT")
txt("PCB 参考轮廓 61.80×100.00 R2 (虚线)", W + 16, 74, 2.6)
txt("内腔 62.40 宽 / 短边贯通 103.80", W + 16, 69, 2.6)
txt("外轮廓圆角 R3.5，内腔圆角 R2.5", W + 16, 64, 2.6)
txt("底座俯视图 1:1", 0, -26, 4.0)

# --- 剖面 A-A（放在 x=140 起，放大 2:1） ---
SX, SZ, SC = 150.0, 20.0, 2.0
def P(x, z): return (SX + x * SC, SZ + z * SC)
# 外壳截面 U 形（沿 x 方向）
sec = [P(0, 0), P(W, 0), P(W, H_TOTAL), P(W - T_WALL, H_TOTAL),
       P(W - T_WALL, T_BASE), P(T_WALL, T_BASE), P(T_WALL, H_TOTAL),
       P(0, H_TOTAL), P(0, 0)]
m.add_lwpolyline(sec, close=True, dxfattribs={"layer": "SECTION"})
# 剖面线（简化为 45° 斜线）
for i in range(0, int(W * SC), 6):
    x0 = SX + i
    line((x0, SZ), (x0 + 5 * SC, SZ + 5 * SC * 0.42), "HATCH")
# PCB / ESP32 / LCD 层叠示意（不按材质剖面线）
zpcb = T_BASE + 0.4
line(P(PCB_X0, zpcb), P(PCB_X0 + PCB_W, zpcb), "PCB_REF")
line(P(PCB_X0, zpcb + 1.6), P(PCB_X0 + PCB_W, zpcb + 1.6), "PCB_REF")
txt("PCB t=1.6", SX + 62 * SC, SZ + (zpcb + 0.8) * SC, 2.2)
line(P(PCB_X0 + 8, zpcb + 6.0), P(PCB_X0 + PCB_W - 8, zpcb + 6.0), "ANT")
txt("ESP32 系统板（天线端伸出板外，不入壳）", SX + 12 * SC, SZ + (zpcb + 7.5) * SC, 2.4, "ANT")
line(P(PCB_X0 + 3, zpcb + 16.0), P(PCB_X0 + PCB_W - 3, zpcb + 16.0), "PCB_REF")
txt("3.5\" LCD 模块（插装于 PCB，不入壳）", SX + 12 * SC, SZ + (zpcb + 17.5) * SC, 2.4)
dim_v(SZ, SZ + T_BASE * SC, SX, "2.40", -10)
dim_v(SZ + T_BASE * SC, SZ + H_TOTAL * SC, SX, "4.20", -10)
dim_v(SZ, SZ + H_TOTAL * SC, SX, "6.60", -20)
dim_h(SX + T_WALL * SC, SX + (W - T_WALL) * SC, SZ, "62.40", -8)
txt("A-A 剖面 2:1", SX, SZ + 30 * SC, 4.0)

# --- BOM 表 ---
BX, BY, CW, RH = 225.0, 145.0, 62.0, 6.5
rows = [["序号", "名称", "规格 / 材料", "数量"],
        ["1", "底座外壳", "PLA/PETG 或光敏树脂，非导电", "1"],
        ["2", "钕铁硼磁铁", "Φ8×2 mm N35", "4"],
        ["3", "M3 螺丝", "M3×8 不锈钢 + 螺母", "4"],
        ["4", "硅胶脚垫", "Φ8×1.5 自粘（可选）", "4"]]
for r, row in enumerate(rows):
    y = BY - r * RH
    for c, val in enumerate(row):
        x = BX + [0, 10, 28, 84][c] if c < 4 else BX
    line((BX, y), (BX + 120, y), "TABLE")
line((BX, BY + RH), (BX + 120, BY + RH), "TABLE")
for xx in (BX, BX + 10, BX + 28, BX + 84, BX + 120):
    line((xx, BY - len(rows) * RH + RH), (xx, BY + RH), "TABLE")
for r, row in enumerate(rows):
    y = BY - r * RH - RH + 1.8
    for c, val in enumerate(row):
        txt(val, BX + [0, 10, 28, 84][c] + 1.0, y, 2.4, "TABLE")
txt("明细表 BOM", BX, BY + 10, 3.4)

# --- 技术说明 + 标题栏 ---
notes = [
    "技术说明：",
    "1. 外壳仅包覆 PCB 本体；LCD 屏与 ESP32 系统板均位于壳体之外。",
    "2. 两条短边整段敞开、不设侧壁；天线侧按实际装配方向选用，可上下镜像。",
    "3. 天线投影 20mm 范围内禁止金属件、磁铁、覆铜及遮挡物。",
    "4. 磁铁仅布置于非天线端；吸在铁质表面时天线宜朝外/悬出边缘。",
    "5. 壳体为绝缘非金属材料（PLA/PETG/光敏树脂/亚克力）。",
    "6. 未注尺寸公差按 3D 打印/激光切割常规工艺，不作 GB/ISO 符合性声明。",
]
for i, t in enumerate(notes):
    txt(t, 150, 5 - i * 5, 2.8)
TX, TY = 225.0, 10.0
for xx in (TX, TX + 60, TX + 90, TX + 120):
    line((xx, TY), (xx, TY + 25), "TABLE")
for yy in (TY, TY + 8, TY + 16, TY + 25):
    line((TX, yy), (TX + 120, yy), "TABLE")
txt("ESP32S3_LCD 显示屏外壳 / 底座", TX + 2, TY + 19, 3.2)
txt("图号 ESP32S3-LCD-EN-A", TX + 2, TY + 10.5, 2.4)
txt("Rev A", TX + 92, TY + 10.5, 2.4)
txt("单位 mm  比例 1:1 / 2:1", TX + 2, TY + 2.5, 2.4)
txt("2026-11-07", TX + 92, TY + 2.5, 2.4)

eng_path = os.path.join(OUT, "ESP32S3_LCD_底座_工程图.dxf")
d2.saveas(eng_path)
print("DXF eng:", eng_path)

# ---------------- 4. 报价 CSV（只算外壳实物） ----------------
quote = [
    ["项目", "规格/工艺", "数量", "单价参考(¥)", "小计(¥)", "备注"],
    ["外壳 3D打印 FDM", "PLA/PETG，约17cm³/约19g", "1件", "18~28", "18~28", "最省事，发 STL 即可"],
    ["外壳 3D打印 SLA", "光敏树脂，约17cm³", "1件", "30~50", "30~50", "精度高、表面好"],
    ["外壳 亚克力激光切割", "3mm 亚克力叠层（底板+边框）", "1件", "20~35", "20~35", "需发 DXF，需自行粘接"],
    ["外壳 CNC", "POM/ABS，需 STEP/图纸", "1件", "120~200", "120~200", "金属件会影响天线，不推荐"],
    ["钕铁硼磁铁", "Φ8×2 mm N35 镀镍", "4片", "0.5~1.0", "2~4", "嵌入 Φ8.2 通孔，胶固定"],
    ["M3 紧固件", "M3×8 螺丝 + 螺母", "4套", "0.4~0.8", "2~3", "与 PCB 4×Φ4 孔同轴"],
    ["硅胶脚垫", "Φ8×1.5 自粘（可选）", "4片", "0.3~0.6", "1~2", "防滑兼遮蔽磁铁孔"],
    ["运费", "普通快递", "1单", "8~12", "8~12", "多家 Printing 常包邮"],
    ["合计（经济方案 FDM）", "外壳+磁铁+螺丝+脚垫+运费", "1台", "", "31~49", "不含 PCB / LCD / ESP32"],
    ["合计（推荐方案 SLA）", "外壳+磁铁+螺丝+脚垫+运费", "1台", "", "43~71", "不含 PCB / LCD / ESP32"],
    ["小批量 5 件（FDM）", "摊薄后单件", "5件", "10~16/件", "50~80", "外壳单件约 10~16"],
]
with open(os.path.join(OUT, "外壳实物报价.csv"), "w", newline="", encoding="utf-8-sig") as f:
    csv.writer(f).writerows(quote)
print("CSV quote done")

# ---------------- 5. 给商家的下单说明 ----------------
note = """ESP32-S3 LCD 显示屏底座外壳 —— 淘宝打样下单说明
================================================
【一、先选工艺，再决定发哪个文件】
1) 3D 打印（最推荐，一次成型、最省事）
   搜索关键词：3D打印服务 代打 / 3D打印 光敏树脂 打样 / FDM 3D打印 PLA PETG 定制 / 嘉立创3D打印
   下单发：ESP32S3_LCD_底座_3D打印.stl （+ PDF 工程图给尺寸）
   材料建议：PLA 或 PETG（便宜、绝缘、不影响天线）；要更好表面选 SLA 光敏树脂
   不要选：金属打印、碳纤维填充、导电材料
2) 亚克力激光切割（叠层粘接）
   搜索关键词：亚克力激光切割 定制 打样 / 亚克力 DIY 外壳 加工 / 激光切割 DXF 代切
   下单发：ESP32S3_LCD_底座_加工轮廓.dxf（1:1，单位 mm）
   说明：3mm 亚克力，CUT_BASE 层为底板外轮廓+孔，两条长边侧壁另切 3mm 宽长条后粘接；
        短边不要加边框（天线与接口要敞开）
3) CNC 加工
   搜索关键词：CNC 手板 打样 POM / ABS 外壳 CNC 加工 / 塑料 CNC 小批量
   下单发：STL + PDF 工程图（商家会自行转 STEP）；材料选 POM/ABS/亚克力，不要用铝

【二、给商家的关键参数（复制粘贴即可）】
外形尺寸 65.6 × 103.8 × 6.6 mm，四角 R3.5
底板厚 2.4 mm；两条长边侧壁厚 1.6 mm、高 4.2 mm；两条短边整段敞开、无侧壁
孔：4×Φ3.2 通孔（M3）、4×Φ8.2 通孔（嵌 Φ8×2 磁铁）
实体体积约 17 cm³（PLA 约 19 g），无悬空、易打印，建议底面朝下/朝上平放打印
材料必须绝缘非金属；表面无需喷漆，不要喷金属漆、不要镀层

【三、自己买的配件】
钕铁硼磁铁 Φ8×2 mm ×4（搜：圆形强力磁铁 8*2 钕铁硼）
M3×8 不锈钢螺丝 + 螺母 ×4（搜：M3*8 螺丝 304 不锈钢）
自粘硅胶脚垫 Φ8 ×4（可选，搜：硅胶脚垫 圆形 自粘 8mm）

【四、装配顺序】
磁铁从底面塞入 Φ8.2 孔 → 点胶固定 → 贴脚垫遮蔽
PCB 放入内腔，4 个 Φ4 孔对准底座 Φ3.2 孔 → M3 螺丝穿入固定
LCD 屏插 PCB 排座；ESP32 系统板焊在 PCB 上，天线端朝敞开的短边、伸到壳外
注意：天线 20mm 内不要有磁铁、螺丝、金属面；吸在铁板上时让天线端悬出边缘

【五、文件清单】
ESP32S3_LCD_底座_3D打印.stl        3D 打印用实体模型
ESP32S3_LCD_底座_加工轮廓.dxf      1:1 闭合轮廓，按图层分发，可导入立创EDA/激光切割
ESP32S3_LCD_底座_工程图.dxf        完整工程图（尺寸/剖面/BOM/标题栏，可编辑）
ESP32S3_LCD_底座_工程图.pdf        2 页 A4，可直接打印给商家
外壳实物报价.csv                   实物制作费用表
"""
with open(os.path.join(OUT, "给商家的下单说明.txt"), "w", encoding="utf-8") as f:
    f.write(note)
print("TXT note done")
print("M3 holes:", M3)
print("MAG holes:", MAG)
