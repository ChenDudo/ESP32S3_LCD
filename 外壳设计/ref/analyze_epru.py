import json, collections, re, sys, os

p = os.path.join(os.path.dirname(__file__), "esp32s3_lcd", "ESP32S3_LCD.epru")
raw = open(p, "r", encoding="utf-8", errors="replace").read()
lines = raw.split("\n")
print("total bytes", len(raw), "lines", len(lines))

types = collections.Counter()
heads = []
for i, ln in enumerate(lines):
    if not ln.strip():
        continue
    parts = ln.split("||")
    try:
        h = json.loads(parts[0])
    except Exception:
        continue
    types[h.get("type", "?")] += 1
    heads.append((i, h.get("type"), len(parts), len(ln)))

print("\n=== types ===")
for t, c in types.most_common(60):
    print(f"{t:30s} {c}")

print("\n=== first 25 headers ===")
for i, t, np, l in heads[:25]:
    print(i, t, "parts", np, "len", l)

# layer / doc types
print("\n=== docType values ===")
dt = collections.Counter()
for ln in lines:
    for m in re.finditer(r'"docType"\s*:\s*"([^"]+)"', ln):
        dt[m.group(1)] += 1
print(dt)

print("\n=== layer-ish keys ===")
lay = collections.Counter()
for ln in lines:
    for m in re.finditer(r'"layer(?:Id|Name)?"\s*:\s*"?([^",}]+)', ln):
        lay[m.group(1)] += 1
print(lay.most_common(30))
