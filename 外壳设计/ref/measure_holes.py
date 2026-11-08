# -*- coding: utf-8 -*-
"""精确测量 PCB 安装孔直径：PDF 矢量 + 工程记录 三方交叉验证"""
import pymupdf, json, math

PDF = r'C:\Users\14210\Downloads\PCB_PCB1_1_2026-11-07.pdf'
EPRU = r'C:\Users\14210\WorkBuddy\2026-11-07-21-40-20\ref\esp32s3_lcd\ESP32S3_LCD.epru'
PT_PER_MM = 72 / 25.4

d = pymupdf.open(PDF)
for pi in [0, 1, 3, 4]:
    pg = d[pi]
    print(f'===== page {pi+1} =====')
    cand = []
    for pa in pg.get_drawings():
        r = pa['rect']
        w, h = r.width, r.height
        if 2.0 < w < 20 and abs(w - h) / max(w, h) < 0.12:
            cx, cy = (r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2
            items = [it[0] for it in pa['items']]
            cand.append((round(cx, 2), round(cy, 2), round(w, 3),
                         tuple(round(v, 2) for v in pa['color']) if pa.get('color') else None,
                         tuple(round(v, 2) for v in pa['fill']) if pa.get('fill') else None,
                         ','.join(items[:5])))
    # 按位置聚类：四角区域
    print('  near-square paths total:', len(cand))
    for c in sorted(cand, key=lambda x: (x[0], x[1])):
        cx, cy, w = c[0], c[1], c[2]
        corner = ''
        if cx < 60 and cy < 60: corner = 'TL'
        elif cx > 150 and cy < 60: corner = 'TR'
        elif cx < 60 and cy > 260: corner = 'BL'
        elif cx > 150 and cy > 260: corner = 'BR'
        if corner:
            print(f'   {corner} center=({cx},{cy}) d={w}pt = {w/PT_PER_MM:.3f}mm color={c[3]} fill={c[4]} items={c[5]}')

print()
print('===== 工程 FILL CIRCLE 记录 =====')
lines = open(EPRU, encoding='utf-8', errors='replace').read().split('\n')
def rec(i):
    ln = lines[i]
    if not ln.strip(): return None, None
    ps = ln.split('||')
    try: h = json.loads(ps[0])
    except: return None, None
    dd = None
    if len(ps) > 1:
        s = ps[1]; s = s[:-1] if s.endswith('|') else s
        try: dd = json.loads(s)
        except: dd = s
    return h, dd
for i in range(9371, 11412):
    h, dd = rec(i)
    if h and h.get('type') == 'FILL' and isinstance(dd, dict):
        path = dd.get('path')
        if path and path[0][0] == 'CIRCLE':
            _, cx, cy, v = path[0]
            print(f'  line{i}: layer={dd["layerId"]} center=({cx},{cy})mil param={v}mil'
                  f'  -> if RADIUS: d={2*v*0.0254:.3f}mm | if DIAMETER: d={v*0.0254:.3f}mm')

print()
print('===== 板框 OUTLINE 与板尺寸标定 =====')
for i in range(9371, 11412):
    h, dd = rec(i)
    if h and h.get('type') == 'POLY' and isinstance(dd, dict) and dd.get('polyType') == 'BOARD_OUTLINE':
        print(' ', dd['path'], '-> w,h(mm)=', round(dd['path'][3]*0.0254, 3), round(dd['path'][4]*0.0254, 3))
print()
print('===== VIA 孔径校准（验证 mil 单位与 diameter 语义）=====')
n = 0
for i in range(9371, 11412):
    h, dd = rec(i)
    if h and h.get('type') == 'VIA' and isinstance(dd, dict) and n < 3:
        print(f'  holeDiameter={dd["holeDiameter"]}mil = {dd["holeDiameter"]*0.0254:.4f}mm,'
              f' viaDiameter={dd["viaDiameter"]}mil = {dd["viaDiameter"]*0.0254:.4f}mm')
        n += 1
