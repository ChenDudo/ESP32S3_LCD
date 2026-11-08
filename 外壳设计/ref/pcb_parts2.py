import json, collections, os

p = os.path.join(os.path.dirname(__file__), "esp32s3_lcd", "ESP32S3_LCD.epru")
lines = open(p, "r", encoding="utf-8", errors="replace").read().split("\n")
recs, metas = [], {}
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
    if h.get("type") == "DOCHEAD" and isinstance(d, dict):
        pass

# meta title per doc segment
starts = [i for i,t,h,d in recs if t == "DOCHEAD"]
for k, s in enumerate(starts):
    e = starts[k+1] if k+1 < len(starts) else recs[-1][0]+1
    for i,t,h,d in recs[s:e]:
        if t == "META" and isinstance(d, dict) and d.get("title"):
            metas[s] = d["title"]
            break

seg = [r for r in recs if 9371 <= r[0] < 11412]
attrs = collections.defaultdict(dict)
for i,t,h,d in seg:
    if t == "ATTR" and isinstance(d, dict):
        attrs[str(d.get("parentId"))][d.get("key")] = d.get("value")

# map footprint uuid -> title
fpname = {}
for s, title in metas.items():
    fpname[s] = title

print("=== COMPONENTS ===")
for i,t,h,d in seg:
    if t == "COMPONENT" and isinstance(d, dict):
        a = attrs.get(str(h.get("id")), {})
        print(f"id={str(h.get('id'))[:10]} x={d.get('x'):>10} y={d.get('y'):>10} Des={str(a.get('Designator','?')):6s} Foot={a.get('Footprint','')} part={str(d.get('partId'))[:20]}")

print("\n=== ATTR keys ===")
keys = collections.Counter()
for v in attrs.values():
    for k in v: keys[k] += 1
print(keys.most_common(20))

print("\n=== STRING texts ===")
for i,t,h,d in seg:
    if t == "STRING" and isinstance(d, dict):
        print(i, "L", d.get("layerId"), "x", round(d.get("x",0),1), "y", round(d.get("y",0),1), repr(d.get("text"))[:90])

print("\n=== IMAGE summary ===")
for i,t,h,d in seg:
    if t == "IMAGE" and isinstance(d, dict):
        print({k:v for k,v in d.items() if k in ("layerId","startX","startY","width","height","angle","name","src","uuid")})

print("\n=== doc meta titles (footprints used) ===")
for s, title in sorted(metas.items()):
    print(s, title)
