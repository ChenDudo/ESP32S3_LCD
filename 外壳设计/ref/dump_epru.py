import json, collections, os

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
        try:
            d = json.loads(parts[1])
        except Exception:
            d = parts[1][:200]
    recs.append((i, h.get("type"), h, d))

def show(t, n=3, maxlen=900):
    print(f"\n===== {t} samples =====")
    c = 0
    for i, typ, h, d in recs:
        if typ == t:
            print(i, json.dumps(h, ensure_ascii=False)[:250])
            print("   DATA:", json.dumps(d, ensure_ascii=False)[:maxlen] if not isinstance(d, str) else d[:maxlen])
            c += 1
            if c >= n:
                break

for t in ["DOCHEAD", "LAYER", "CANVAS", "PCB", "BOARD", "COMPONENT", "PRIMITIVE", "LINE", "RECT", "CIRCLE", "ELLIPSE", "POLY", "PAD", "STRING", "IMAGE", "REGION", "META"]:
    show(t, 2, 700)

# document boundaries
print("\n===== doc segmentation =====")
for i, typ, h, d in recs:
    if typ == "DOCHEAD":
        print(i, json.dumps(d, ensure_ascii=False)[:300])
