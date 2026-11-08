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

for label, (A, B) in [("PCB1", (8002, 9371)), ("PCB1_1", (9371, 11412))]:
    seg = [r for r in recs if A <= r[0] < B]
    layers = {}
    for i,t,h,d in seg:
        if t == "LAYER" and isinstance(d, dict):
            lid = json.loads(h["id"])[1] if isinstance(h.get("id"), str) and h["id"].startswith("[") else h.get("id")
            layers[str(lid)] = d.get("layerName")
    attrs = collections.defaultdict(dict)
    for i,t,h,d in seg:
        if t == "ATTR" and isinstance(d, dict):
            attrs[str(d.get("parentId"))][d.get("key")] = d.get("value")
    print(f"\n########## {label}: lines {A}..{B} ##########")
    print("--- board outline / shapes on layers 11,53,54,55,13,14 ---")
    for i,t,h,d in seg:
        if isinstance(d, dict) and str(d.get("layerId")) in ("11","53","54","55","13","14") and t in ("POLY","LINE","RECT","CIRCLE","ELLIPSE","REGION"):
            print(i, t, "layer", d.get("layerId"), json.dumps({k:v for k,v in d.items() if k in ("path","startX","startY","endX","endY","centerX","centerY","radius","polyType","regionType","name","width")}, ensure_ascii=False)[:300])
    print("--- components ---")
    for i,t,h,d in seg:
        if t == "COMPONENT" and isinstance(d, dict):
            a = attrs.get(str(h.get("id")), {})
            print(f"  {str(a.get('Designator','?')):6s} x={d.get('x'):>10} y={d.get('y'):>10} rot={d.get('rotation')} foot={a.get('Footprint','')}")
    print("--- images ---")
    for i,t,h,d in seg:
        if t == "IMAGE" and isinstance(d, dict):
            print(i, {k:v for k,v in d.items() if k in ("layerId","startX","startY","width","height","angle")})
    print("--- document-layer STRING ---")
    for i,t,h,d in seg:
        if t == "STRING" and isinstance(d, dict) and str(d.get("layerId")) in ("13","14","9","10"):
            print(i, repr(d.get("text"))[:120])
