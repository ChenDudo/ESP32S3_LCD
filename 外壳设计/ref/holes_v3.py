import json, os, collections
p = os.path.join(os.path.dirname(__file__), "esp32s3_lcd", "ESP32S3_LCD.epru")
lines = open(p, "r", encoding="utf-8", errors="replace").read().split("\n")
recs = []
for i, ln in enumerate(lines):
    if not ln.strip(): continue
    parts = ln.split("||")
    try: h = json.loads(parts[0])
    except Exception: continue
    d = None
    if len(parts) > 1:
        s = parts[1]
        if s.endswith("|"): s = s[:-1]
        try: d = json.loads(s)
        except Exception: d = s
    recs.append((i, h.get("type"), h, d))

# locate PCB document segments
segs = []
for i, t, h, d in recs:
    if isinstance(d, dict) and d.get("docType") == "PCB":
        segs.append(i)
print("=== PCB doc segment starts ===", segs)

# find end boundaries: next docType record of any kind
starts = []
for i, t, h, d in recs:
    if isinstance(d, dict) and "docType" in d:
        starts.append(i)
print("=== all doc starts ===", starts)

MIL = 0.0254
for si, s in enumerate(segs):
    e = next((x for x in starts if x > s), len(lines))
    print(f"\n########## PCB doc {si} lines {s}..{e} ##########")
    seg = [r for r in recs if s <= r[0] < e]
    types = collections.Counter(r[1] for r in seg)
    print("types:", dict(types))
    # HOLE records
    print("\n--- HOLE / VIA / CIRCLE / ARC records ---")
    for i, t, h, d in seg:
        if t in ("HOLE", "VIA", "CIRCLE", "ARC", "ELLIPSE") and isinstance(d, dict):
            print(i, t, json.dumps(d, ensure_ascii=False)[:350])
    # PAD: collect all shape/size info
    pads = [(i, d) for i, t, h, d in seg if t == "PAD" and isinstance(d, dict)]
    print(f"\n--- PAD count = {len(pads)} ---")
    keys = collections.Counter()
    for i, d in pads:
        for k in d: keys[k] += 1
    print("pad keys freq:", dict(keys))
    for i, d in pads[:4]:
        print(i, json.dumps(d, ensure_ascii=False)[:500])
    # look for hole/drill/radius fields
    print("\n--- PADs with hole/drill >= 1.0mm (or radius) ---")
    for i, d in pads:
        s = json.dumps(d, ensure_ascii=False)
        if any(k in s.lower() for k in ("hole", "drill", "radius", "r ")):
            print(i, s[:400])
    print("\n--- distinct PAD shape/size combos ---")
    combo = collections.Counter()
    for i, d in pads:
        cand = {k: d.get(k) for k in ("shape", "size", "width", "height", "hole", "holeR", "drill", "r", "radius", "net", "layer", "x", "y") if k in d}
        combo[json.dumps(cand, sort_keys=True, ensure_ascii=False)] += 1
    for k, v in combo.most_common(30):
        print(v, k[:280])
