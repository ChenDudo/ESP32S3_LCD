# -*- coding: utf-8 -*-
"""三视图第二轮排版：拉开视图间距，去掉重复/被覆盖的标注。"""
import io, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, "make_views.py")
s = io.open(p, encoding="utf-8").read()

pairs = [
    # 主视图：删掉重复的孔距尺寸线（右侧尺寸表已有 91.34×48.70）
    ('''DIMH(FX + HOLES[0][0] * S, FX + HOLES[1][0] * S, FY - 19, "91.34 孔距")''',
     '''# 91.34 × 48.70 孔距见右侧关键尺寸表，避免与上视图标题挤在同一行'''),

    # 主视图：这行说明会被后绘制的上视图图形盖住，图例中已有同样内容
    ('''T("虚线 = PCB 参考 61.80×100.00 R2   蓝色虚线圆 = Φ7 螺丝柱位", FX, FY - 29, 6.3, GRAY)''',
     '''# 虚线含义见右下「图例」，此处不重复（会被后绘制的上视图盖住）'''),

    # 上视图整体下移、标题上移，与主视图尺寸线拉开
    ('''TX, TY = 28.0, 108.0
TH = HT * S
T("② 上视图（从天线侧 / +Yo 看，沿 -Yo）", TX, 141, 9, BLUE)''',
     '''TX, TY = 28.0, 100.0
TH = HT * S
T("② 上视图（从天线侧 / +Yo 看，沿 -Yo）", TX, 131, 9, BLUE)'''),

    # 顶板说明移进顶板条内，不再压在上视图标题行
    ('''LN(TX, TY + HT * S + 1.2, TX + FW, TY + HT * S + 1.2, GREEN, 0.9)
T("顶板连续完整 · 无镂空", TX + FW - 62, TY + HT * S + 3, 6.2, GREEN)''',
     '''LN(TX, TY + HT * S + 1.2, TX + FW, TY + HT * S + 1.2, GREEN, 0.9)
TC("顶板连续完整 · 无镂空", TX + FW / 2,
   TY + ZTI * S + TTI * S / 2 - 1.0, 5.2, GREEN)'''),

    # 上视图外形 105.20 与主视图重复，删掉以便辅助视图标题独立成行
    ('''DIMH(TX, TX + FW, TY - 9, f"{W:.2f}")''',
     '''# 外形 105.20 已在正视图标注，此处不重复'''),
]

for i, (old, new) in enumerate(pairs, 1):
    n = s.count(old)
    if n != 1:
        print(f"!! pair#{i}: hit {n} :: {old[:70]!r}")
        sys.exit(1)
    s = s.replace(old, new)
io.open(p, "w", encoding="utf-8").write(s)
print("OK: make_views.py 第二轮修正", len(pairs), "处")
