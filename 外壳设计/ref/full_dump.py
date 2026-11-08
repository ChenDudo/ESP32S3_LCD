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

starts = [i for i,t,h,d in recs if t == "DOCHEAD"]
print("=== DOC SEGMENTS ===")
for k, s in enumerate(starts):
    e = starts[k+1] if k+1 < len(starts) else recs[-1][0]+1
    dh = recs[s][3] if isinstance(recs[s][3], dict) else {}
    meta = {}
    for i,t,h,d in recs[s:e]:
        if t == "META" and isinstance(d, dict): meta.update(d)
    print(k, s, e, "docType=", dh.get("docType"), "title=", meta.get("title"), "uuid=", dh.get("uuid") or meta.get("uuid"), "head=", json.dumps({k:v for k,v in dh.items() if k in ('uuid','docType','id','name')},ensure_ascii=False)[:200])

print("\n=== DOCHEAD / META raw samples ===")
for i,t,h,d in recs[:40]:
    if t in ("DOCHEAD","META"):
        print(i, t, json.dumps(h,ensure_ascii=False)[:250], json.dumps(d,ensure_ascii=False)[:400])

# PCB docs
pcb_starts = [i for i,t,h,d in recs if t=="DOCHEAD" and isinstance(d,dict) and d.get("docType")=="PCB"]
print("\nPCB docs at", pcb_starts)
for pi,s in enumerate(pcb_starts):
    idx = starts.index(s)
    e = starts[idx+1] if idx+1 < len(starts) else recs[-1][0]+1
    seg = [r for r in recs if s <= r[0] < e]
    print(f"\n########## PCB#{pi} lines {s}..{e} recs={len(seg)} ##########")
    layers={}
    for i,t,h,d in seg:
        if t=="LAYER" and isinstance(d,dict):
            lid = str(h.get("id"))
            layers[lid] = d.get("layerName") or d.get("layerType")
    print("LAYERS:", layers)
    cnt=collections.Counter()
    for i,t,h,d in seg:
        if isinstance(d,dict): cnt[(str(d.get("layerId")),t)]+=1
    print("GEOM:", sorted(cnt.items(), key=lambda x:(int(x[0][0]) if x[0][0].isdigit() else 999,x[0][1]))[:60])
    # outline
    ol=[k for k,v in layers.items() if v and "Outline" in str(v)]
    print("OUTLINE LAYERS",ol)
    for i,t,h,d in seg:
        if isinstance(d,dict) and str(d.get("layerId")) in ol and t in ("LINE","POLY","RECT","CIRCLE","ARC","REGION"):
            print(" O",i,t,json.dumps(d,ensure_ascii=False)[:300])
    # big hole pads
    print("BIG PADS:")
    for i,t,h,d in seg:
        if t=="PAD" and isinstance(d,dict):
            hole=d.get("hole") or {}
            w=hole.get("width",0) if isinstance(hole,dict) else 0
            if isinstance(w,(int,float)) and w>=60:
                print("  P",i,"x",d.get("centerX"),"y",d.get("centerY"),"hole",w)
    # components + attrs
    attrs=collections.defaultdict(dict)
    for i,t,h,d in seg:
        if t=="ATTR" and isinstance(d,dict):
            attrs[str(d.get("parentId") or d.get("ownerId"))][d.get("key")]=d.get("value")
    print("COMPONENTS:")
    for i,t,h,d in seg:
        if t=="COMPONENT" and isinstance(d,dict):
            a=attrs.get(str(h.get("id")),{})
            print("  C",str(a.get("Designator","?")).ljust(6), "x",round(d.get("x",0),1),"y",round(d.get("y",0),1),"dev",str(a.get("Device",""))[:30],"fp",str(a.get("Footprint",""))[:24],"name",str(a.get("Name",""))[:24])
    print("STRINGS:")
    for i,t,h,d in seg:
        if t=="STRING" and isinstance(d,dict):
            print("  S",round(d.get("x",0),1),round(d.get("y",0),1),"L",d.get("layerId"),repr(d.get("text"))[:80])
