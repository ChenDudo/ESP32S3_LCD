import pymupdf, math, os, collections
P = r"C:\Users\14210\Downloads\PCB_PCB1_1_2026-11-07.pdf"
d = pymupdf.open(P)

def circles_from_page(pg):
    out = []
    for path in pg.get_drawings():
        for item in path["items"]:
            if item[0] == "c":  # bezier curve (circle made of 4 arcs)
                out.append(path)
                break
    return out

# bounding rect of all drawn items on page2 (bottom copper) to find board outline extents
for pi in [1, 0]:
    pg = d[pi]
    dr = pg.get_drawings()
    print(f"\n===== page {pi+1} rect={pg.rect} drawings={len(dr)} =====")
    xs, ys = [], []
    for path in dr:
        r = path["rect"]
        xs += [r.x0, r.x1]; ys += [r.y0, r.y1]
    print("all drawing bbox", min(xs), max(xs), min(ys), max(ys))
    # look for filled/stroked circles: paths whose items are all curves and whose rect is near-square
    circs = []
    for path in dr:
        items = path["items"]
        if not items: continue
        if all(it[0] == "c" for it in items) and len(items) >= 4:
            r = path["rect"]
            w, h = r.width, r.height
            if w > 0.5 and abs(w - h) / max(w, h) < 0.12:
                circs.append((round((r.x0+r.x1)/2, 2), round((r.y0+r.y1)/2, 2), round(w/2, 3),
                               path.get("fill"), path.get("color"), path.get("width")))
    print("near-square curve paths =", len(circs))
    sizes = collections.Counter(round(c[2], 2) for c in circs)
    print("radius histogram(top):", sizes.most_common(20))
    # print largest circles
    big = sorted(circs, key=lambda c: -c[2])[:20]
    print("largest circles (cx, cy, r, fill, stroke, width):")
    for c in big: print("   ", c)
