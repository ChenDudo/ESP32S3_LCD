# -*- coding: utf-8 -*-
"""Rev I 预览图：上盖俯视（实测 A.A 虚线 + 放大让位窗口实线）+ 等距 3D。

灰色虚线 = 实测 LCD A.A 73.44×48.96；红色实线 = 唯一显示窗 74.40×50.00，
四周各放大 0.48/0.52 mm 让位。窗口中心 X 左移 2.75、Y 下移 0.90 对准偏心屏
（Y 方向并非几何居中）。顶板 9 组凸字：右侧字头朝左、上边 I2C 字头朝下、RST 横排。
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import trimesh
import params_v2 as P

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "deliverables")
STL = os.path.join(OUT, "ESP32S3_LCD_全覆盖外壳_上盖_3D打印.stl")

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

WIN = (P.WIN_CX - P.WIN_W / 2, P.WIN_CY - P.WIN_H / 2,
       P.WIN_W, P.WIN_H)


def top_view():
    fig, ax = plt.subplots(figsize=(11, 7.4))
    ax.add_patch(FancyBboxPatch(
        (0, 0), P.W, P.H,
        boxstyle=f"round,pad=0,rounding_size={P.R_OUT}",
        fc="#dde6ef", ec="#243447", lw=2.2))
    ax.add_patch(FancyBboxPatch(
        (P.T_WALL, P.T_WALL), P.W - 2 * P.T_WALL, P.H - 2 * P.T_WALL,
        boxstyle=f"round,pad=0,rounding_size={P.R_IN}",
        fill=False, ec="#7d8c99", ls="--", lw=1.0))
    ax.add_patch(FancyBboxPatch(
        (P.OX, P.OY), P.PCB_PY, P.PCB_PX,
        boxstyle=f"round,pad=0,rounding_size={P.PCB_R}",
        fill=False, ec="#4f8f6d", ls=":", lw=1.2))

    wx, wy, ww, wh = WIN
    # 先画显示窗（带填充），否则填充会把下面的 A.A 参考线盖住
    ax.add_patch(FancyBboxPatch(
        (wx, wy), ww, wh,
        boxstyle=f"round,pad=0,rounding_size={P.WIN_R}",
        fc="#93aed0", ec="#c0392b", lw=2.4))
    # 实测 LCD A.A 参考矩形：画在窗口之上，才能看出四周 0.48 / 0.52 让位
    aax = P.WIN_CX - P.LCD_AA_X / 2
    aay = P.WIN_CY - P.LCD_AA_Y / 2
    ax.add_patch(FancyBboxPatch(
        (aax, aay), P.LCD_AA_X, P.LCD_AA_Y,
        boxstyle=f"round,pad=0,rounding_size={P.WIN_R}",
        fill=False, ec="#2f7d55", ls=(0, (5, 3)), lw=2.0, zorder=6))
    ax.add_patch(Circle(P.RESET_POS, P.RESET_HOLE_D / 2,
                        fc="white", ec="#243447", lw=1.2))
    for x, y in P.SCREW_POS:
        ax.add_patch(Circle((x, y), P.POST_D / 2, fill=False,
                            ec="#5a6d7d", ls="--", lw=1.0))

    # 顶板外表面一体成型接口凸字（与 STL / STEP 同一字形轮廓）
    import text_geom as TG
    from matplotlib.patches import Polygon as MplPolygon
    for _, _, _, _, polys, _ in TG.all_marks():
        for poly in polys:
            ax.add_patch(MplPolygon(list(poly.exterior.coords), closed=True,
                                    fc="#2b3a4a", ec="none", zorder=7))
            for hole in poly.interiors:
                ax.add_patch(MplPolygon(list(hole.coords), closed=True,
                                        fc="#dde6ef", ec="none", zorder=8))

    # 外壳中心线 vs 窗口中心线
    ax.plot([P.W / 2, P.W / 2], [-4, P.H + 4], color="#8a97a3",
            ls=":", lw=1.2)
    ax.plot([P.WIN_CX, P.WIN_CX], [wy - 1.5, wy + wh + 1],
            color="#c0392b", ls="--", lw=1.2)
    # 偏心量标注移进窗口下缘并加白底：下边框带现在被 USB / COM 凸字占用
    y0 = wy + 5.0
    ax.annotate("", xy=(P.W / 2, y0), xytext=(P.WIN_CX, y0),
                arrowprops=dict(arrowstyle="<->", color="#c0392b", lw=1.6))
    ax.text((P.W / 2 + P.WIN_CX) / 2, y0 - 3.6,
            f"左移 {-P.WIN_OFFSET_X:.2f} mm", color="#c0392b",
            ha="center", fontsize=10,
            bbox=dict(facecolor="white", alpha=0.85, edgecolor="none", pad=2))
    # 外壳 Y 中心线 vs 窗口 Y 中心线：突出显示「窗口不是 Y 轴居中」
    ax.plot([-4, P.W + 4], [P.H / 2, P.H / 2], color="#8a97a3",
            ls=":", lw=1.2)
    ax.plot([wx - 1.5, wx + ww + 1.5], [P.WIN_CY, P.WIN_CY],
            color="#c0392b", ls="--", lw=1.0, alpha=0.65)
    x0 = wx - 4.5
    ax.annotate("", xy=(x0, P.H / 2), xytext=(x0, P.WIN_CY),
                arrowprops=dict(arrowstyle="<->", color="#c0392b", lw=1.6))
    ax.text(x0 - 1.0, (P.H / 2 + P.WIN_CY) / 2,
            f"下移 {-P.WIN_OFFSET_Y:.2f} mm", color="#c0392b",
            ha="center", va="center", fontsize=9, rotation=90,
            bbox=dict(facecolor="white", alpha=0.85, edgecolor="none", pad=2))

    ax.text(P.W / 2, -10.5, f"外壳中心 X={P.W/2:.2f} / Y={P.H/2:.2f}",
            ha="center", color="#5a6d7d", fontsize=10)
    ax.text(0, -14.5,
            "绿色虚线框 = 实测 LCD A.A 73.44×48.96；红色实线框 = 显示窗 74.40×50.00（四周各放大 0.48/0.52 让位）",
            color="#5a6d7d", fontsize=9.5)
    ax.text(wx + ww / 2, wy + wh / 2,
            f"显示窗 {ww:.2f}×{wh:.2f}\n中心 X={P.WIN_CX:.2f} / Y={P.WIN_CY:.2f}",
            ha="center", va="center", color="#1b2a3a", fontsize=11,
            bbox=dict(facecolor="white", alpha=0.72, edgecolor="none", pad=3))
    ax.text(0, P.H + 8,
            "Rev I 上盖俯视 · 窗口 X 左移 2.75 / Y 下移 0.90 对准偏心屏（非 Y 居中）"
            f" · 顶板 9 组凸字（字高 {P.TEXT_SIZE:.2f}，右侧字头朝左、上边 I2C 字头朝下）· 单位 mm",
            fontsize=11, color="#1b2a3a")
    ax.set_xlim(-8, P.W + 8)
    ax.set_ylim(-17, P.H + 12)
    ax.set_aspect("equal")
    ax.axis("off")
    p = os.path.join(OUT, "上盖_顶板完整_俯视预览.png")
    fig.savefig(p, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return p


def iso_view():
    mesh = trimesh.load(STL)
    tris = mesh.vertices[mesh.faces]
    fig = plt.figure(figsize=(10, 7.5))
    ax = fig.add_subplot(111, projection="3d")
    poly = Poly3DCollection(tris, facecolor="#aebfd2",
                            edgecolor="#5d7085", linewidths=0.06)
    ax.add_collection3d(poly)
    ax.set_xlim(0, P.W)
    ax.set_ylim(0, P.H)
    ax.set_zlim(0, P.H_TOTAL + 6)
    ax.set_box_aspect((P.W, P.H, P.H_TOTAL * 1.5))
    ax.view_init(elev=28, azim=-62)
    ax.set_axis_off()
    ax.set_title("Rev I 上盖等距视图 · 窗口按 A.A 放大让位 · 顶板完整 + 接口凸字",
                 fontsize=12, color="#1b2a3a", pad=-6)
    p = os.path.join(OUT, "上盖_顶板完整_等距预览.png")
    fig.savefig(p, dpi=130, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return p


if __name__ == "__main__":
    print(top_view())
    print(iso_view())
