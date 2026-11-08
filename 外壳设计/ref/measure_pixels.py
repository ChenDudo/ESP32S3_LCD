# -*- coding: utf-8 -*-
"""用像素法测量 PCB 四角安装孔直径，并用板框 61.8x100mm 标定"""
from PIL import Image, ImageDraw
import numpy as np

# p4 品红板框 bbox (4x 渲染): x 75..778 px, y 73..1209 px
BX0, BX1, BY0, BY1 = 75, 778, 73, 1209
PX_PER_MM_X = (BX1 - BX0) / 61.8 / 4 * 4 / 4  # px/mm, 渲染 4x
PX_PER_MM = (BX1 - BX0) / 61.8
PY_PER_MM = (BY1 - BY0) / 100.0
print(f'标定: {PX_PER_MM:.3f} px/mm (X), {PY_PER_MM:.3f} px/mm (Y)')

MIL = 0.0254
holes = {
    'TL': (225, -169.949),
    'TR': (2142.0079, -169.9411),
    'BL': (225, -3766),
    'BR': (2142.0079, -3765.9921),
}
centers = {}
for k, (mx, my) in holes.items():
    px = BX0 + mx * MIL * PX_PER_MM
    py = BY0 + abs(my) * MIL * PY_PER_MM
    centers[k] = (int(round(px)), int(round(py)))
    print(f'  {k} -> pixel ({px:.1f}, {py:.1f})')

for name in ['p1', 'p2', 'p4', 'p5']:
    im = np.array(Image.open(f'pcbpdf/{name}.png').convert('RGB'))
    print(f'===== {name} =====')
    tiles = []
    for k, (cx, cy) in centers.items():
        R = 45
        a = im[cy - R:cy + R, cx - R:cx + R]
        r, g, b = a[:, :, 0].astype(int), a[:, :, 1].astype(int), a[:, :, 2].astype(int)
        white = (r > 235) & (g > 235) & (b > 235)
        dark = (r < 90) & (g < 90) & (b < 90)
        # 中心行/列连续段
        def run_at(mask):
            row = mask[R]
            col = mask[:, R]
            def longest(v):
                best = cur = 0
                for q in v:
                    cur = cur + 1 if q else 0
                    best = max(best, cur)
                return best
            return longest(row), longest(col)
        rw, cw = run_at(white)
        rd, cd = run_at(dark)
        # 白色连通域近似：中心附近白像素 bbox
        sub = white[R - 30:R + 30, R - 30:R + 30]
        ys, xs = np.where(sub)
        wb = (xs.max() - xs.min() + 1, ys.max() - ys.min() + 1) if len(xs) else (0, 0)
        print(f'  {k}: white row/col run = {rw}/{cw}px -> {rw/PX_PER_MM:.2f}/{cw/PY_PER_MM:.2f}mm |'
              f' dark = {rd}/{cd}px | white bbox {wb[0]/PX_PER_MM:.2f}x{wb[1]/PY_PER_MM:.2f}mm')
        # 放大拼图
        tile = Image.fromarray(a).resize((a.shape[1] * 4, a.shape[0] * 4), Image.LANCZOS)
        dr = ImageDraw.Draw(tile)
        dr.text((6, 6), f'{name} {k}', fill=(255, 0, 0))
        tiles.append(tile)
    W = sum(t.width for t in tiles[::2][:1]) * 2
    H = tiles[0].height * 2
    sheet = Image.new('RGB', (tiles[0].width * 2, H), 'white')
    for i, t in enumerate(tiles):
        sheet.paste(t, ((i % 2) * t.width, (i // 2) * t.height))
    sheet.save(f'pcbpdf/holes_{name}.png')
    print('  saved', f'pcbpdf/holes_{name}.png')
