# -*- coding: utf-8 -*-
"""ESP32S3_LCD 全覆盖外壳 Rev I —— 导出可编辑的 STEP (AP214 BREP) 实体

与 build_v2.py 的 STL 用同一套 params_v2.py 参数，但用 OpenCascade 解析几何
重新建模：圆角是真正的圆柱面，螺丝孔是真正的圆柱面，窗口是平面多边形，
因此在 FreeCAD / SolidWorks / 立创EDA / Fusion 里可以测量、布尔、改特征，
而不是 STL 那种三角网格。

差异仅一处：STL 版的圆角由 shapely.buffer 生成（每象限 32 段折线逼近），
STEP 版用解析圆弧，两者轮廓差 <0.01 mm，外形尺寸 / 孔径 / 开窗完全一致。

输出（cad/deliverables/）：
  ESP32S3_LCD_全覆盖外壳_上盖_可编辑.step
  ESP32S3_LCD_全覆盖外壳_底座_可编辑.step
  ESP32S3_LCD_全覆盖外壳_装配体_含PCB参考.step
"""
import os
import cadquery as cq
from shapely.geometry import Polygon
import params_v2 as P
import text_geom as TG

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "deliverables")
os.makedirs(OUT, exist_ok=True)


def rr_prism(w, h, r, cx, cy, z0, z1):
    """精确圆弧圆角矩形柱；中心 (cx,cy)，Z 从 z0 到 z1"""
    wp = cq.Workplane("XY").workplane(offset=z0).rect(w, h).extrude(z1 - z0)
    if r and r > 0:
        wp = wp.edges("|Z").fillet(r)
    return wp.translate((cx, cy, 0)).val()


def box_prism(x0, y0, x1, y1, z0, z1):
    """直角矩形柱（窗口 / 让位窗切除体）"""
    return rr_prism(x1 - x0, y1 - y0, 0,
                    (x0 + x1) / 2, (y0 + y1) / 2, z0, z1)


def cylinder(r, z0, z1, cx, cy):
    return (cq.Workplane("XY").workplane(offset=z0).circle(r)
            .extrude(z1 - z0).translate((cx, cy, 0)).val())


def poly_prism(poly, z0, z1):
    """把 shapely 多边形（可带内孔）挤成 BREP 实体，与 STL 版共用同一轮廓。"""
    outer = [tuple(p) for p in list(poly.exterior.coords)[:-1]]
    w = (cq.Workplane("XY").workplane(offset=z0)
         .polyline(outer).close().extrude(z1 - z0))
    for h in poly.interiors:
        pts = [tuple(p) for p in list(h.coords)[:-1]]
        cutter = (cq.Workplane("XY").workplane(offset=z0 - 0.1)
                  .polyline(pts).close().extrude(z1 - z0 + 0.2))
        w = w.cut(cq.Workplane(obj=cutter.val()))
    return w.val()


def build_top(win_w, win_h):
    outer = rr_prism(P.W, P.H, P.R_OUT, P.W / 2, P.H / 2,
                     P.T_BASE, P.H_TOTAL)
    # 内腔略低于罩体底面，避免共面布尔；罩体底部本来就是敞开的
    cavity = rr_prism(P.W - 2 * P.T_WALL, P.H - 2 * P.T_WALL, P.R_IN,
                      P.W / 2, P.H / 2, P.T_BASE - 0.5, P.Z_TOP_IN)
    window = rr_prism(win_w, win_h, P.WIN_R, P.WIN_CX, P.WIN_CY,
                      P.Z_TOP_IN - 0.2, P.H_TOTAL + 0.5)
    ant_slot = box_prism(P.ANT_X0, P.ANT_Y0, P.ANT_X1, P.H + 2.0,
                         P.ANT_SLOT_Z0, P.ANT_SLOT_Z1)
    reset = cylinder(P.RESET_HOLE_D / 2, P.Z_TOP_IN - 0.2,
                     P.H_TOTAL + 0.5, *P.RESET_POS)
    cuts = [cavity, window, ant_slot, reset]
    for name, (x0, y0, x1, y1), z0, z1, desc in P.SLOTS:
        cuts.append(box_prism(x0, y0, x1, y1, z0, z1))
    shell = outer.cut(*cuts)

    posts = []
    for x, y in P.SCREW_POS:
        post = cylinder(P.POST_D / 2, P.POST_Z0, P.POST_Z1, x, y)
        pilot = cylinder(P.POST_PILOT_D / 2, P.POST_Z0 - 0.2,
                         P.POST_PILOT_Z1, x, y)
        posts.append(post.cut(pilot))
    # 顶板外表面一体成型接口凸字（与 STL 共用 text_geom.py 的字形轮廓）
    marks = [poly_prism(p, TG.mark_z0(), TG.mark_z1())
             for _, _, _, _, polys, _ in TG.all_marks() for p in polys]
    return shell.fuse(*(posts + marks)).clean()


def build_base():
    body = rr_prism(P.W, P.H, P.R_OUT, P.W / 2, P.H / 2, 0, P.T_BASE)
    screw_boss = [cylinder(P.POST_D / 2, P.T_BASE - 0.1, P.Z_PCB_BOT, x, y)
                  for x, y in P.SCREW_POS]
    pcb_boss = [cylinder(P.BASE_BOSS_D / 2, P.T_BASE - 0.1, P.Z_PCB_BOT, x, y)
                for x, y in P.HOLES]
    # A 方案：4 个 Φ7 支撑台保留，定位销只留 2 个对角（圆销 + 菱形销）
    pins = [
        cylinder(P.LOCATOR_D / 2, P.LOCATOR_Z0 - 0.1, P.LOCATOR_Z1,
                 *P.LOCATOR_ROUND),
        poly_prism(Polygon(TG.diamond_pin_points(
            P.LOCATOR_DIAMOND, P.LOCATOR_ROUND)),
            P.LOCATOR_Z0 - 0.1, P.LOCATOR_Z1),
    ]
    solid = body.fuse(*(screw_boss + pcb_boss + pins))
    cuts = []
    for x, y in P.SCREW_POS:
        cuts.append(cylinder(P.SCREW_HOLE_D / 2, -0.5, P.Z_PCB_BOT + 0.2, x, y))
        cuts.append(cylinder(P.SCREW_CS_D / 2, -0.5, P.SCREW_CS_DEPTH, x, y))
    return solid.cut(*cuts)


def build_pcb_reference():
    """PCB 参考件：仅用于在 CAD 里检查装配间隙，不是打印件"""
    board = rr_prism(P.PCB_PY, P.PCB_PX, P.PCB_R,
                     P.OX + P.PCB_PY / 2, P.OY + P.PCB_PX / 2,
                     P.Z_PCB_BOT, P.Z_PCB_TOP)
    holes = [cylinder(P.PCB_HOLE_D / 2, P.Z_PCB_BOT - 0.5,
                      P.Z_PCB_TOP + 0.5, x, y) for x, y in P.HOLES]
    return board.cut(*holes)


def save(shape, filename):
    path = os.path.join(OUT, filename)
    shape.exportStep(path)
    return path


def check(path, expect_vol_cm3):
    """回读 STEP，确认是有效 BREP 实体且体积与 STL 一致"""
    imported = cq.importers.importStep(path)
    solids = imported.solids().vals()
    vol = sum(s.Volume() for s in solids) / 1000.0
    bb = cq.Compound.makeCompound(solids).BoundingBox()
    ok = len(solids) >= 1 and bb.xlen > 0 and bb.zlen > 0
    print(f"  {os.path.basename(path)}")
    print(f"    solids={len(solids)}  volume={vol:.2f} cm3 "
          f"(STL {expect_vol_cm3:.2f})  "
          f"bbox={bb.xlen:.2f} x {bb.ylen:.2f} x {bb.zlen:.2f} mm")
    if expect_vol_cm3:
        d = abs(vol - expect_vol_cm3) / expect_vol_cm3 * 100
        print(f"    delta vs STL = {d:.2f}%")
        if d > 1.5:
            print("    !! 体积偏差偏大，请检查圆角/窗口")
            ok = False
    return ok


def main():
    import json
    geom_path = os.path.join(HERE, "geom_v2.json")
    ref = {}
    if os.path.exists(geom_path):
        with open(geom_path, encoding="utf-8") as f:
            ref = json.load(f).get("volumes", {})

    top = build_top(P.WIN_W, P.WIN_H)
    base = build_base()
    pcb = build_pcb_reference()

    parts = [
        (top, "ESP32S3_LCD_全覆盖外壳_上盖_可编辑.step",
         "ESP32S3_LCD_全覆盖外壳_上盖_3D打印.stl"),
        (base, "ESP32S3_LCD_全覆盖外壳_底座_可编辑.step",
         "ESP32S3_LCD_全覆盖外壳_底座_3D打印.stl"),
    ]
    print("STEP 导出 + 回读校验")
    all_ok = True
    for shape, fname, stl_key in parts:
        p = save(shape, fname)
        expect = ref.get(stl_key, {}).get("volume_cm3", 0)
        all_ok &= check(p, expect)

    # 装配体：3 个独立 BREP 实体合在一个 STEP 里。
    # 不用 cq.Assembly.save —— 该路径在 cadquery 2.8 / Python 3.13 上会导出空文件。
    assy_path = os.path.join(OUT, "ESP32S3_LCD_全覆盖外壳_装配体_含PCB参考.step")
    cq.Compound.makeCompound([top, base, pcb]).exportStep(assy_path)
    print(f"  {os.path.basename(assy_path)}  (3 solids: top / base / PCB ref)")
    expect_assy = (ref.get(parts[0][2], {}).get("volume_cm3", 0)
                   + ref.get(parts[1][2], {}).get("volume_cm3", 0)
                   + pcb.Volume() / 1000.0)
    all_ok &= check(assy_path, expect_assy)

    print("ALL CHECKS PASSED" if all_ok else "SOME CHECKS FAILED")
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
