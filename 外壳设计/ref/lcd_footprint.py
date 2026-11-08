# -*- coding: utf-8 -*-
"""定位 ESP32S3_LCD.epru 里 TFT3.5'_C / LCD 封装的可视框图元与坐标。"""
import json, os, collections

P = os.path.join(os.path.dirname(__file__), "esp32s3_lcd", "ESP32S3_LCD.epru")
lines = open(P, "r", encoding="utf-8", errors="replace").read().split("\n")
recs = []
for i, ln in enumerate(lines):
    if not ln.strip():
        continue
    parts = ln.split("||")
    try:
        h = json.loads(parts[0])
    except Exception:
        continue
    d = None
    if len(parts) > 1:
        s = parts[1]
        if s.endswith("|"):
            s = s[:-1]
        try:
            d = json.loads(s)
        except Exception:
            d = s
    recs.append((i, h.get("type"), h, d))

print("total records", len(recs))
print("=== META docs ===")
for i, t, h, d in recs:
    if t == "META":
        title = d.get("title") if isinstance(d, dict) else ""
        print(f"line={i:6d} ticket={h.get('ticket')} first={h.get('firstTicket')} "
              f"id={h.get('id')} docType={d.get('docType') if isinstance(d, dict) else ''} title={title}")

print("\n=== type counts ===")
print(collections.Counter(t for _, t, _, _ in recs))

# 所有含几何坐标的图元，按层统计包围盒
print("\n=== geometry bbox per layer (records with x/y) ===")
layers = collections.defaultdict(lambda: [1e18, -1e18, 1e18, -1e18, 0])
for i, t, h, d in recs:
    if not isinstance(d, dict):
        continue
    pts = []
    for k1, k2 in (("startX", "startY"), ("endX", "endY"), ("x", "y"), ("cx", "cy")):
        if k1 in d and k2 in d and isinstance(d[k1], (int, float)):
            pts.append((d[k1], d[k2]))
    for key in ("points", "polygon", "vertices"):
        v = d.get(key)
        if isinstance(v, list):
            for q in v:
                if isinstance(q, (list, tuple)) and len(q) >= 2:
                    pts.append((q[0], q[1]))
                elif isinstance(q, dict) and "x" in q and "y" in q:
                    pts.append((q["x"], q["y"]))
    if not pts:
        continue
    lay = d.get("layerId", d.get("layer", "?"))
    b = layers[str(lay)]
    for x, y in pts:
        b[0] = min(b[0], x); b[1] = max(b[1], x)
        b[2] = min(b[2], y); b[3] = max(b[3], y)
        b[4] += 1
for lay, b in sorted(layers.items(), key=lambda kv: -kv[1][4])[:20]:
    print(f"  layer={lay:>6s} pts={b[4]:6d}  X {b[0]:.1f}~{b[1]:.1f} mil "
          f"({(b[1]-b[0])*0.0254:.2f} mm)  Y {b[2]:.1f}~{b[3]:.1f} "
          f"mil ({(b[3]-b[2])*0.0254:.2f} mm)")
