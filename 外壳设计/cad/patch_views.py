# -*- coding: utf-8 -*-
"""按 A3 首版渲染结果修正三视图排版：标题与尺寸线分行、图例离标题栏。"""
import io, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "make_views.py")
s = io.open(p, encoding="utf-8").read()

pairs = [
    # 主视图：窗口尺寸已写在窗内，删掉与标题同行的外部尺寸线；让位窗标签移入窄条
    ('''DIMH(FX + wx * S, FX + (wx + ww) * S, FY + FH + 7,
     f"{ww:.2f} (A 版窗口)")''',
     '''# 窗口尺寸 69.00 × 47.60 已标在窗内，避免与主视图标题挤在同一行'''),

    ('''T("侧壁让位窗（顶板完整）", FX + AX0 * S + 2, FY + AY0 * S - 5.5, 6, BLUE)''',
     '''TC("侧壁让位窗", FX + (AX0 + AX1) / 2 * S, FY + AY0 * S + 0.4, 4.6, BLUE)'''),

    # 上视图：删掉与标题同行的让位窗外部尺寸线（窗内与右侧尺寸表已有 27.00）
    ('''DIMH(TX + AX0 * S, TX + AX1 * S, TY + TH + 8, "27.00 侧壁让位窗", color=BLUE)''',
     '''# 27.00 已标在让位窗内与右侧关键尺寸表，避免与上视图标题同行'''),

    ('''T("说明：顶板整段连续，天线让位窗只开在侧壁 Z 8.0~14.2，下段侧壁保留。",
  TX, TY - 19, 6.3, GRAY)''',
     '''# 该说明已并入右下「三视图读图说明」，此处不再重复以免与辅助视图标题相挤'''),

    # 辅助下视图：整体下移，标题与上方 105.20 尺寸线分开
    ('''BX, BY = 28.0, 66.0
T("③ 辅助下视图（接口侧 / -Yo 看）  —— 补充第 2 视图看不到的双 Type-C", BX, 99, 8.2, BLUE)''',
     '''BX, BY = 28.0, 60.0
T("③ 辅助下视图（接口侧 / -Yo 看）  —— 补充第 2 视图看不到的双 Type-C", BX, 91, 8.2, BLUE)'''),

    # 右视图：删掉与「三视图读图说明」标题相挤的行
    ('''T("横轴 Yo：左 = 下边（接口侧），右 = 上边（天线侧）。顶板完整连续。",
  RX, RY - 18, 6.3, GRAY)''',
     '''# 横轴方向说明已并入右下读图说明第 5~6 行'''),

    # 方位示意：改成四边标注 + 两行观察方向，不再让箭头文字压到页眉与标题
    ('''# 小壳体示意
SX, SY, SW, SH = IX1 + 6, 218, 92, 38
RR(SX, SY, SW, SH, 4, INK, 0.5, fill=PALE)
RR(SX + 8, SY + 6, SW - 16, SH - 12, 2, REDC, 0.5, fill=WINF)
TC("显示窗", SX + SW / 2, SY + SH / 2 - 1, 7, REDC)
RECT(SX + 32, SY + SH - 4, 28, 4, BLUE, 0.5, fill=ANTF)
TC("天线侧（上）", SX + SW / 2, SY + SH + 3, 6, BLUE)
T("下：双 Type-C", SX + 2, SY - 7, 6, INK)
T("右：5V / XH-5P", SX + 52, SY - 7, 6, INK)
# 三个观察箭头
LN(SX + SW / 2, SY + SH / 2, SX + SW / 2 + 16, SY + SH + 12, GRAY, 0.35)
T("① 从屏幕正面 (+Z)", SX + SW / 2 + 10, SY + SH + 14, 5.8, GRAY)
LN(SX + SW / 2, SY + SH, SX + SW / 2 - 20, SY + SH + 12, GRAY, 0.35)
T("② 从天线侧 (+Yo)", SX - 22, SY + SH + 14, 5.8, GRAY)
LN(SX + SW, SY + SH / 2, SX + SW + 14, SY + SH / 2 + 10, GRAY, 0.35)
T("④ 从右侧 (+Xo)", SX + SW + 2, SY + SH / 2 + 13, 5.8, GRAY)''',
     '''# 小壳体示意：四边标注 + 观察方向两行（不与页眉/标题同行）
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
T("④ 从 +Xo（右侧）   ③ 从 -Yo（接口侧，辅助）", IX1, 196, 5.8, GRAY)'''),

    # 图例第二行上移，与标题栏 y=20 的线分开
    ('''LN(JX, 22, JX + 7, 22, GRAY, 0.35, dash=(2, 1.2)); T("虚线 = PCB 参考 / 螺丝柱隐藏线", JX + 10, 20.5, 6.2, INK)
RECT(JX + 130, 20.5, 7, 3.5, INK, 0.4, fill=SIDE); T("浅蓝 = 顶板 / 底板实体", JX + 140, 21.5, 6.2, INK)''',
     '''LN(JX, 24, JX + 7, 24, GRAY, 0.35, dash=(2, 1.2)); T("虚线 = PCB 参考 / 螺丝柱隐藏线", JX + 10, 23.5, 6.2, INK)
RECT(JX + 130, 22.5, 7, 3.5, INK, 0.4, fill=SIDE); T("浅蓝 = 顶板 / 底板实体", JX + 140, 23.5, 6.2, INK)'''),
]

for i, (old, new) in enumerate(pairs, 1):
    n = s.count(old)
    if n != 1:
        print(f"!! pair#{i}: hit {n} :: {old[:70]!r}")
        sys.exit(1)
    s = s.replace(old, new)
io.open(p, "w", encoding="utf-8").write(s)
print("OK: make_views.py 排版修正", len(pairs), "处")
