import json, os
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

seg = [r for r in recs if 9371 <= r[0] < 11412]
print("=== records with hole / big circle / radius ===")
for i,t,h,d in seg:
    if isinstance(d, dict) and (t in ("PAD","FILL","CIRCLE","ELLIPSE","VIA") or "hole" in json.dumps(d)[:400]):
        s = json.dumps(d, ensure_ascii=False)
        if t in ("FILL","CIRCLE","ELLIPSE") or '"hole"' in s:
            print(i, t, s[:400])

print("\n=== FILL records ===")
for i,t,h,d in seg:
    if t == "FILL" and isinstance(d, dict):
        print(i, json.dumps(d, ensure_ascii=False)[:500])

print("\n=== PAD records count/sample ===")
pads = [(i,d) for i,t,h,d in seg if t == "PAD"]
print("count", len(pads))
for i,d in pads[:5]:
    print(i, json.dumps(d, ensure_ascii=False)[:400])
