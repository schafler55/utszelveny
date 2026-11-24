#!/usr/bin/env python3
"""Imports the NAP one-way carriageways (egyirányú útpályák) and bus stops (autóbusz megállóhelyek) into
ÚtSzelvény's index.html.

Reads the two GeoJSON files downloaded from the NAP WFS (nap_eu_irany, nap_b26_megallo; EOV, EPSG:23700) and
writes into the embedded `roaddata` JSON:
  egy – one-way ranges        [road, carriageway, from, to, direction]
        direction 1 = one-way in the direction of the chainage, 2 = against it (irany); touching pieces merged.
        A place on an undivided road that has no range here is two-way.
  bm  – bus stops, one after the other: [road, carriageway, chainage, E, N, name, side, kind]
        chainage km*10000+m (kszelv); E, N: EOV in metres (the stop itself, beside the road), stored as the
        difference from the previous stop's E, N (the first one from 0) – the list is sorted by road and chainage;
        name: index into bmn (-1 = no name); side: 0 right / 1 left / 2 in the middle of the road (mold);
        kind: index into bmt (-1 = no data) – how the stop is built (mkiep)
  bmn – the stop names (mnev), bmt – the kinds of stop
The road number (kszam), the carriageway (pkod, 0 undivided / 1 jobb / 2 bal) and the chainage join the records
to the roads, as in tools/nap_szakaszadatok.py.

Usage:  python3 tools/nap_egyiranyu_megallok.py <folder with the .json files> [web/index.html]
The files are recognised by the start of their names (Egyirányú_útpályák… / Egyir_ny___tp_ly_k… and
Autóbusz_megállóhelyek… / Aut_busz_meg_ll_helyek…).
"""
import json, re, sys, os, unicodedata

def norm(s):
    return unicodedata.normalize("NFC", s).lower()

def find(folder, keys):
    for f in sorted(os.listdir(folder)):
        n = norm(f)
        if f.endswith(".json") and any(k in n for k in keys):
            return os.path.join(folder, f)
    sys.exit(f"Not found: {keys[0]}*.json in {folder}")

CH = re.compile(r"\s*(\d+)\s*\+\s*(\d+)\s*$")
def cval(s):
    m = CH.match(str(s))
    if not m: raise ValueError(f"bad chainage: {s!r}")
    return int(m[1]) * 10000 + int(m[2])

def feats(path):
    d = json.load(open(path, encoding="utf-8"))
    crs = (d.get("crs") or {}).get("properties", {}).get("name", "")
    if crs and not crs.endswith("23700"):
        sys.exit(f"not EOV coordinates: {crs} ({path})")
    return d["features"]

SIDES = {"jobboldali": 0, "baloldali": 1, "útközepén": 2}

def main():
    folder = sys.argv[1]
    html = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(__file__), "..", "web", "index.html")
    s = open(html, encoding="utf-8", newline="").read()
    tag = '<script type="application/json" id="roaddata">'
    i = s.index(tag) + len(tag); j = s.index("</script>", i)
    D = json.loads(s[i:j])
    RI = {r.split("|")[0]: k for k, r in enumerate(D["roads"])}
    def road(p):
        r = RI.get(str(p["kszam"]).strip())
        if r is None: raise SystemExit(f"unknown road: {p['kszam']!r}")
        return r

    # one-way carriageways
    rows = []
    for f in feats(find(folder, ["egyirányú_útpályák", "egyir_ny___tp_ly_k"])):
        p = f["properties"]
        t = norm(p["irany"] or "")
        d = 1 if "egyező" in t else 2 if "ellentétes" in t else 0
        if not d: raise SystemExit(f"unknown direction: {p['irany']!r}")
        a, b = cval(p["kszelv"]), cval(p["vszelv"])
        rows.append((road(p), int(p["pkod"]), min(a, b), max(a, b), d))
    rows.sort()
    egy = []
    for x in rows:
        if egy:
            y = egy[-1]
            if y[0] == x[0] and y[1] == x[1] and y[4] == x[4] and x[2] <= y[3] + 1:
                egy[-1] = (y[0], y[1], y[2], max(y[3], x[3]), y[4]); continue
        egy.append(x)
    D["egy"] = [v for x in egy for v in x]

    # bus stops
    bp = feats(find(folder, ["autóbusz_megállóhelyek", "aut_busz_meg_ll_helyek"]))
    names = sorted({f["properties"]["mnev"].strip() for f in bp if (f["properties"]["mnev"] or "").strip()})
    kinds = sorted({f["properties"]["mkiep"] for f in bp if f["properties"]["mkiep"]})
    ni = {n: k for k, n in enumerate(names)}
    stops = []
    for f in bp:
        p = f["properties"]
        e, n = f["geometry"]["coordinates"][:2]
        nm = (p["mnev"] or "").strip()
        side = SIDES.get(norm(p["mold"] or ""), -1)
        if side < 0: raise SystemExit(f"unknown side: {p['mold']!r}")
        stops.append((road(p), int(p["pkod"]), cval(p["kszelv"]), round(e), round(n),
                      ni[nm] if nm else -1, side, kinds.index(p["mkiep"]) if p["mkiep"] else -1))
    stops.sort()
    bm, pe, pn = [], 0, 0
    for x in stops:
        bm += [x[0], x[1], x[2], x[3] - pe, x[4] - pn, x[5], x[6], x[7]]
        pe, pn = x[3], x[4]
    D["bm"] = bm
    D["bmn"] = names
    D["bmt"] = kinds

    js = json.dumps(D, ensure_ascii=False, separators=(",", ":"))
    open(html, "w", encoding="utf-8", newline="").write(s[:i] + js + s[j:])
    add = sum(len(json.dumps(D[k], ensure_ascii=False, separators=(",", ":"))) for k in ("egy", "bm", "bmn", "bmt"))
    print(f"one-way {len(rows)} records → {len(egy)} ranges · bus stops {len(stops)} ({len(names)} names, "
          f"{len(kinds)} kinds) · +{add/1e6:.2f} MB · roaddata {len(js)/1e6:.2f} MB")

if __name__ == "__main__":
    main()
