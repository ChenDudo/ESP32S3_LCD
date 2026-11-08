import json, collections, os

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

A, B = 9371, 11412
seg = [r for r in recs if A <= r[0] < B]

# attrs by parentId
attrs = collections.defaultdict(dict)
for i,t,h,d in seg:
    if t == "ATTR" and isinstance(d, dict):
        attrs[str(d.get("parentId"))][d.get("key")] = d.get("value")

print("=== COMPONENTS (56) ===")
for i,t,h,d in seg:
    if t == "COMPONENT" and isinstance(d, dict):
        cid = h.get("id")
        a = attrs.get(str(cid), {})
        print(f"{i:6d} id={cid} part={str(d.get('partId'))[:28]:28s} x={d.get('x'):>10} y={d.get('y'):>10} rot={d.get('rotation')}  "
              f"Des={a.get('Designator','?'):8s} Name={str(a.get('Name') or a.get('Value') or '')[:34]:34s} Foot={a.get('Footprint','')}")

print("\n=== all ATTR keys ===")
keys = collections.Counter()
for v in attrs.values():
    for k in v: keys[k] += 1
print(keys)

print("\n=== ELE_PLACEHOLDER / PAD / PAD_NET samples ===")
for t in ("ELE_PLACEHOLDER", "PAD", "PAD_NET", "VIA", "FILL"):
    print(f"--- {t}")
    c = 0
    for i,tt,h,d in seg:
        if tt == t:
            print(i, json.dumps(d, ensure_ascii=False)[:330]); c += 1
            if c >= 3: break

print("\n=== STRING texts (silkscreen/notes) ===")
for i,t,h,d in seg:
    if t == "STRING" and isinstance(d, dict):
        print(i, "layer", d.get("layerId"), "x", d.get("x"), "y", d.get("y"), repr(d.get("text"))[:100])

print("\n=== IMAGE records ===")
for i,t,h,d in seg:
    if t == "IMAGE" and isinstance(d, dict):
        print(i, {k:v for k,v in d.items() if k in ("layerId","startX","startY","width","height","angle","mirror","file","path","name","src")})

print("\n=== LINE geometry overall bbox (all copper/silk) ===")
xs, ys = [], []
for i,t,h,d in seg:
    if t == "LINE" and isinstance(d, dict):
        xs += [d.get("startX",0), d.get("endX",0)]
        ys += [d.get("startY",0), d.get("endY",0)]
print("mil bbox", min(xs), max(xs), min(ys), max(ys), "=> mm", (max(xs)-min(xs))*0.0254, (max(ys)-min(ys))*0.0254)
