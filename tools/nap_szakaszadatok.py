#!/usr/bin/env python3
"""Imports NAP section data into ÚtSzelvény's index.html.

Reads the GeoJSON files downloaded from the NAP WFS and writes into the embedded `roaddata` JSON:
  sav  – number of traffic lanes         [road, carriageway, from, to, lanes]
  bur  – pavement type and width         [road, carriageway, from, to, width in dm, type index] + burt (type names); missing: -1
  anf  – annual cross-section traffic    [road, carriageway, from, to, station index] + ksz (per station asz, anf, oj, ongj2; missing: -1) + anfEv
         asz = traffic counting station number, anf = annual average daily cross-section traffic (PCU/day),
         oj = all vehicles (vehicles/day), ongj2 = heavy motor vehicles (vehicles/day)  – as in the NAP data package description
The geometry is not used (the app already has it): the road number (kszam), the carriageway (pkod, 0 undivided /
1 jobb / 2 bal) and the chainage (kszelv / vszelv, km*10000+m) join the records to the roads. Touching pieces with the
same value are merged.

Usage:  python3 tools/nap_szakaszadatok.py <folder with the .json files> [index.html]
The files are recognised by the start of their names (Összes_gépjármű_forgalmi_sávok_száma…, Burkolat_típusa…,
Éves_keresztmetszeti_forgalmi…).
"""
import json, re, sys, os, unicodedata

def norm(s):
    return unicodedata.normalize("NFC", s).lower()

def find(folder, prefix):
    for f in sorted(os.listdir(folder)):
        if norm(f).startswith(norm(prefix)) and f.endswith(".json"):
            return os.path.join(folder, f)
    sys.exit(f"Not found: {prefix}*.json in {folder}")

CH = re.compile(r"\s*(\d+)\s*\+\s*(\d+)\s*$")
def cval(s):
    m = CH.match(str(s))
    if not m: raise ValueError(f"bad chainage: {s!r}")
    return int(m[1]) * 10000 + int(m[2])

def load(path):
    d = json.load(open(path, encoding="utf-8"))
    return [x["properties"] for x in d["features"]]

def ranges(props, RI, val):
    """[(r, pk, f, t, value)] sorted, touching pieces with the same value merged"""
    rows = []
    for p in props:
        r = RI.get(str(p["kszam"]).strip())
        if r is None: raise SystemExit(f"unknown road: {p['kszam']!r}")
        f, t = cval(p["kszelv"]), cval(p["vszelv"])
        rows.append((r, int(p["pkod"]), min(f, t), max(f, t), val(p)))
    rows.sort()
    out = []
    for x in rows:
        if out:
            y = out[-1]
            if y[0] == x[0] and y[1] == x[1] and y[4] == x[4] and x[2] <= y[3] + 1:
                out[-1] = (y[0], y[1], y[2], max(y[3], x[3]), y[4]); continue
        out.append(x)
    return out

def main():
    folder = sys.argv[1]
    html = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(__file__), "..", "index.html")
    s = open(html, encoding="utf-8", newline="").read()
    tag = '<script type="application/json" id="roaddata">'
    i = s.index(tag) + len(tag); j = s.index("</script>", i)
    D = json.loads(s[i:j])
    RI = {r.split("|")[0]: k for k, r in enumerate(D["roads"])}

    sav = ranges(load(find(folder, "Összes_gépjármű_forgalmi_sávok_száma")), RI, lambda p: int(p["savossz"]))
    D["sav"] = [v for x in sav for v in x]

    bp = load(find(folder, "Burkolat_típusa"))
    burt = sorted({p["rbtip"] for p in bp if p["rbtip"]})
    # missing width / type (a few dirt roads): -1
    bur = ranges(bp, RI, lambda p: (round(float(p["rbtsz"]) * 10) if p["rbtsz"] is not None else -1,
                                    burt.index(p["rbtip"]) if p["rbtip"] else -1))
    D["burt"] = burt
    D["bur"] = [v for x in bur for v in (x[0], x[1], x[2], x[3], x[4][0], x[4][1])]

    ap = load(find(folder, "Éves_keresztmetszeti_forgalmi"))
    num = lambda v: int(v) if v is not None else -1          # missing value: -1
    key = lambda p: (num(p["asz"]), num(p["anf"]), num(p["oj"]), num(p["ongj2"]))
    st = sorted({key(p) for p in ap})
    si = {k: n for n, k in enumerate(st)}
    anf = ranges(ap, RI, lambda p: si[key(p)])
    D["ksz"] = [v for x in st for v in x]
    D["anf"] = [v for x in anf for v in x]
    D["anfEv"] = sorted({int(p["ev"]) for p in ap})[-1]

    js = json.dumps(D, ensure_ascii=False, separators=(",", ":"))
    open(html, "w", encoding="utf-8", newline="").write(s[:i] + js + s[j:])
    print(f"lanes {len(sav)} ranges · pavement {len(bur)} ranges, {len(burt)} types · "
          f"traffic {len(anf)} ranges, {len(st)} stations ({D['anfEv']}) · roaddata {len(js)/1e6:.2f} MB")

if __name__ == "__main__":
    main()
