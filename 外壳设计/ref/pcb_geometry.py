import json, collections, os, math

p = os.path.join(os.path.dirname(__file__), "esp32s3_lcd", "ESP32S3_LCD.epru")
lines = open(p, "r", encoding="utf-8", errors="replace").read().split("\n")

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

# doc segments
starts = [(i, (d if isinstance(d, dict) else {}).get("docType"))
          for i, t, h, d in recs if t == "DOCHEAD"]
print("=== docs ===")
for k, (i, dt) in enumerate(starts):
    end = starts[k+1][0] if k+1 < len(starts) else recs[-1][0]+1
    print(k, i, end, dt, "records", sum(1 for r in recs if i <= r[0] < end))

# choose latest PCB doc
pcb_starts = [(i, dt) for i, dt in starts if dt == "PCB"]
A, B = pcb_starts[-1][0], (starts[[j for j,(s,dt) in enumerate(starts) if s==pcb_starts[-1][0]][0]+1][0]
                           if [j for j,(s,dt) in enumerate(starts) if s==pcb_starts[-1][0]][0]+1 < len(starts)
                           else recs[-1][0]+1)
seg = [r for r in recs if A <= r[0] < B]
print(f"\n=== latest PCB doc lines {A}..{B}, {len(seg)} records ===")

# layers
layers = {}
for i, t, h, d in seg:
    if t == "LAYER" and isinstance(d, dict):
        lid = json.loads(h["id"])[1] if isinstance(h.get("id"), str) and h["id"].startswith("[") else h.get("id")
        layers[str(lid)] = d.get("layerName") or d.get("layerType")
print("\n=== layers in PCB doc ===")
for k, v in layers.items():
    print(k, v)

# geometry per layer
print("\n=== geometry counts by layerId ===")
cnt = collections.Counter()
for i, t, h, d in seg:
    if t in ("LINE", "POLY", "RECT", "CIRCLE", "ELLIPSE", "ARC", "PAD", "VIA", "REGION", "FILL", "STRING", "IMAGE", "WIRE") and isinstance(d, dict):
        cnt[(str(d.get("layerId")), t)] += 1
for (lid, t), c in sorted(cnt.items(), key=lambda x: (int(x[0][0]) if x[0][0].isdigit() else 999, x[0][1])):
    print(f"layer {lid:>3} {layers.get(lid,'?'):28s} {t:9s} {c}")

# outline layer
outline_ids = [k for k, v in layers.items() if v and "Outline" in str(v)]
print("\n=== outline layer ids ===", outline_ids)

def coords(d):
    out = []
    if isinstance(d.get("path"), list):
        for v in d["path"]:
            if isinstance(v, (int, float)):
                out.append(v)
    for key in ("startX", "startY", "endX", "endY", "x", "y", "centerX", "centerY", "dotX1", "dotY1", "dotX2", "dotY2"):
        if isinstance(d.get(key), (int, float)):
            out.append(d[key])
    return out

for ol in outline_ids:
    print(f"\n=== outline geometries layer {ol} ===")
    for i, t, h, d in seg:
        if isinstance(d, dict) and str(d.get("layerId")) == ol and t in ("LINE","POLY","RECT","CIRCLE","ELLIPSE","ARC","REGION"):
            print(i, t, json.dumps(d, ensure_ascii=False)[:400])

# all regions
print("\n=== regions ===")
for i, t, h, d in seg:
    if t == "REGION" and isinstance(d, dict):
        print(i, json.dumps(d, ensure_ascii=False)[:500])

# components
comps = [(i, h, d) for i, t, h, d in seg if t == "COMPONENT" and isinstance(d, dict)]
print(f"\n=== components: {len(comps)} ===")
attrs = collections.defaultdict(dict)
for i, t, h, d in seg:
    if t == "ATTR" and isinstance(d, dict):
        owner = str(d.get("ownerId") or d.get("parentId") or d.get("id") or "")
        attrs[owner][d.get("key") or d.get("name") or "?"] = d.get("value")
print("ATTR sample:", json.dumps(seg and [d for i,t,h,d in seg if t=="ATTR"][:2], ensure_ascii=False)[:600])

# bounding box of all pads / outline
def bbox(recs_):
    xs, ys = [], []
    for i,t,h,d in recs_:
        if not isinstance(d, dict): continue
        c = coords(d)
        if t in ("LINE",):
            xs += [d.get("startX",0), d.get("endX",0)]; ys += [d.get("startY",0), d.get("endY",0)]
    return (min(xs), max(xs), min(ys), max(ys)) if xs else None

# mounting holes: PAD with big hole on multilayer
print("\n=== large-hole pads (mounting holes) ===")
for i,t,h,d in seg:
    if t == "PAD" and isinstance(d, dict):
        hole = d.get("hole") or {}
        w = hole.get("width", 0)
        if isinstance(w,(int,float)) and w >= 60:
            print(i, "x",d.get("centerX"),"y",d.get("centerY"),"layer",d.get("layerId"),"hole",w,"pad",d.get("defaultPad",{}).get("width"))
