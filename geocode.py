#!/usr/bin/env python3
"""
Geocode businesses in js/data.js that don't have lat/lng yet.

Uses the U.S. Census Bureau batch geocoder (free, no key, public-domain data).
Every result is validated before it's written:
  * must land inside the Lindsey Street area of Norman (bounding box), and
  * must keep the input's street direction (W Lindsey must not come back as
    E Lindsey — the Census matcher sometimes "fixes" W into E).
Addresses that fail are interpolated by house number between the nearest
validated neighbors on the same street and side (odd/even). Anything that
can't be placed either way is left without coordinates, and the map falls
back to its approximate placement for it.

Usage:  python3 geocode.py          # fill in missing coordinates
        python3 geocode.py --all    # re-geocode everything
Then run python3 build.py.
"""
import csv, io, json, re, sys, uuid, urllib.request

ROOT = __file__.rsplit("/", 1)[0] if "/" in __file__ else "."
DATA = f"{ROOT}/js/data.js"
CENSUS = "https://geocoding.geo.census.gov/geocoder/locations/addressbatch"
BBOX = (35.17, 35.24, -97.50, -97.43)  # lat_min, lat_max, lng_min, lng_max

def norm_street(address):
    st = address.split(",")[0].strip()
    st = re.sub(r"\s+(#\S+|[A-D]\d{3})$", "", st)      # unit: #B, #100, D180, C248
    st = re.sub(r"\bW Lindsey$", "W Lindsey St", st)
    st = re.sub(r"\bMcGee$", "McGee Dr", st)
    st = re.sub(r"\bS Berry$", "S Berry Rd", st)
    return st

def census_batch(streets):
    buf = io.StringIO(); w = csv.writer(buf)
    for i, st in enumerate(streets): w.writerow([i, st, "Norman", "OK", ""])
    boundary = uuid.uuid4().hex
    body = (f"--{boundary}\r\nContent-Disposition: form-data; name=\"benchmark\"\r\n\r\nPublic_AR_Current\r\n"
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"addressFile\"; filename=\"in.csv\"\r\n"
            f"Content-Type: text/csv\r\n\r\n{buf.getvalue()}\r\n--{boundary}--\r\n").encode()
    req = urllib.request.Request(CENSUS, data=body, headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
    out = urllib.request.urlopen(req, timeout=180).read().decode()
    res = {}
    for r in csv.reader(io.StringIO(out)):
        if len(r) >= 6 and r[2] == "Match":
            lon, lat = map(float, r[5].split(","))
            res[streets[int(r[0])]] = (lat, lon, r[4])
    return res

def valid(street, lat, lon, matched):
    if not (BBOX[0] < lat < BBOX[1] and BBOX[2] < lon < BBOX[3]): return False
    m = re.match(r"\d+\s+([NSEW])\s", street)           # input direction must survive
    return not m or f" {m.group(1)} " in f" {matched.split(',')[0]} "

def interpolate(street, placed):
    m = re.match(r"(\d+)\s+(.*)", street)
    if not m: return None
    n, name = int(m.group(1)), m.group(2)
    pts = sorted((int(re.match(r"\d+", s).group()), ll) for s, ll in placed.items()
                 if s.endswith(" " + name) and int(re.match(r"\d+", s).group()) % 2 == n % 2)
    lo = [p for p in pts if p[0] < n]; hi = [p for p in pts if p[0] > n]
    if not lo or not hi: return None
    (n0, (a0, b0)), (n1, (a1, b1)) = lo[-1], hi[0]
    t = (n - n0) / (n1 - n0)
    return (a0 + t * (a1 - a0), b0 + t * (b1 - b0))

def main():
    redo = "--all" in sys.argv
    src = open(DATA).read()
    m = re.search(r"const BUSINESSES = \[\n(.*?)\n\];", src, re.S)
    lines = m.group(1).split("\n")
    objs = [json.loads(l.strip().rstrip(",")) for l in lines]
    todo = [o for o in objs if redo or not isinstance(o.get("lat"), (int, float))]
    if not todo:
        print("[geocode] every business already has coordinates."); return
    streets = sorted({norm_street(o["address"]) for o in todo})
    print(f"[geocode] {len(todo)} businesses -> {len(streets)} unique street addresses; querying Census…")
    res = census_batch(streets)
    placed = {s: (la, lo) for s, (la, lo, mt) in res.items() if valid(s, la, lo, mt)}
    rejected = [s for s in streets if s in res and s not in placed]
    unmatched = [s for s in streets if s not in res]
    interp = {}
    for s in rejected + unmatched:
        ll = interpolate(s, placed)
        if ll: interp[s] = ll
    final = {**placed, **interp}
    for o in todo:
        ll = final.get(norm_street(o["address"]))
        if ll: o["lat"], o["lng"] = round(ll[0], 6), round(ll[1], 6)
    out = [("  " + json.dumps(o, ensure_ascii=False)) for o in objs]
    open(DATA, "w").write(src[:m.start(1)] + ",\n".join(out) + src[m.end(1):])
    print(f"[geocode] exact/validated: {len(placed)} · interpolated: {sorted(interp)} · "
          f"left approximate: {sorted(set(rejected + unmatched) - set(interp))}")
    if rejected: print(f"[geocode] rejected Census matches (outside area or wrong direction): {rejected}")

if __name__ == "__main__":
    main()
