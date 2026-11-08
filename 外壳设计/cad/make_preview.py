# -*- coding: utf-8 -*-
"""Rev G 预览图：上盖俯视（标出偏心窗口位置）+ 等距 3D。

窗口中心由外壳中心 52.60 左移到 49.85 后，俯视图里能直观看到
窗口相对外壳居中线偏左，右侧留出的顶板压边更宽。
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
STL = os.path.join(OUT, "ESP32S3_LCD_全覆盖外壳_上盖_A版_3D打印.stl")

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

WIN = (P.WIN_CX - P.WIN_A_W / 2, P.WIN_CY - P.WIN_A_H / 2,
       P.WIN_A_W, P.WIN_A_H)


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
    # Rev F 旧窗口（居中）作对比，直观看出左移量
    old_wx = P.W / 2 - P.WIN_A_W / 2
    ax.add_patch(FancyBboxPatch(
        (old_wx, wy), ww, wh,
        boxstyle=f"round,pad=0,rounding_size={P.WIN_R}",
        fill=False, ec="#94a1ad", ls="--", lw=1.3))
    ax.add_patch(FancyBboxPatch(
        (wx, wy), ww, wh,
        boxstyle=f"round,pad=0,rounding_size={P.WIN_R}",
        fc="#93aed0", ec="#c0392b", lw=2.4))
    ax.add_patch(Circle(P.RESET_POS, P.RESET_HOLE_D / 2,
                        fc="white", ec="#243447", lw=1.2))
    for x, y in P.HOLES:
        ax.add_patch(Circle((x, y), P.POST_D / 2, fill=False,
                            ec="#5a6d7d", ls="--", lw=1.0))

    # 外壳中心线 vs 窗口中心线
    ax.plot([P.W / 2, P.W / 2], [-4, P.H + 4], color="#8a97a3",
            ls=":", lw=1.2)
    ax.plot([P.WIN_CX, P.WIN_CX], [wy - 3, wy + wh + 3],
            color="#c0392b", ls="--", lw=1.2)
    y0 = wy - 2.0
    ax.annotate("", xy=(P.W / 2, y0), xytext=(P.WIN_CX, y0),
                arrowprops=dict(arrowstyle="<->", color="#c0392b", lw=1.6))
    ax.text((P.W / 2 + P.WIN_CX) / 2, y0 - 2.0,
            f"左移 {-P.WIN_OFFSET_X:.2f} mm", color="#c0392b",
            ha="center", fontsize=10.5)

    ax.text(P.W / 2, -10.5, f"外壳中心 X={P.W/2:.2f}",
            ha="center", color="#5a6d7d", fontsize=10)
    ax.text(0, -14.5,
            "灰色虚线框 = Rev F 居中旧窗口；红色实线框 = Rev G 偏心新窗口",
            color="#5a6d7d", fontsize=9.5)
    ax.text(wx + ww / 2, wy + wh / 2,
            f"显示窗 {ww:.2f}×{wh:.2f}\n中心 X={P.WIN_CX:.2f}",
            ha="center", va="center", color="#1b2a3a", fontsize=11,
            bbox=dict(facecolor="white", alpha=0.72, edgecolor="none", pad=3))
    ax.text(0, P.H + 8,
            f"Rev G 上盖俯视 · 显示窗已左移对准偏心屏 · 顶板完整无镂空 · 单位 mm",
            fontsize=12, color="#1b2a3a")
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
    ax.set_title("Rev G 上盖等距视图 · 窗口偏心对位 · 顶板完整",
                 fontsize=12, color="#1b2a3a", pad=-6)
    p = os.path.join(OUT, "上盖_顶板完整_等距预览.png")
    fig.savefig(p, dpi=130, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return p


if __name__ == "__main__":
    print(top_view())
    print(iso_view())
