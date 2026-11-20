#!/usr/bin/env python3
"""NAP közúti azonosítópontok beépítése az ÚtSzelvény index.html-be.

Beolvassa a NAP WFS-ből letöltött „Közti azonosító pontok” GeoJSON-t (nap_b5_csp), és a beágyazott
`roaddata` JSON-ba írja:
  cspk – az azonosítópontok kódjai (kod), pl. "C020001"
  csp  – pontonként egymás után: [pontok száma, E, N, E, N, …, utak száma, útindex, útindex, …]
         E, N: EOV (EPSG:23700) méterre kerekítve; útindex: a roaddata `roads` listájának indexe
         (kszamok = az azonosítópontba csatlakozó utak útszáma, a NAP adatcsomag-leírás szerint)
A MultiPoint egy azonosítópontnál több helyen is lehet (pl. az osztott pálya két oldalán); az 1 m-en belüli
ismétlődő pontok összevonódnak.

Használat:  python3 tools/nap_azonositopontok.py <mappa a .json fájllal> [index.html]
A fájlt a neve eleje alapján ismeri fel (Közti_azonosító_pontok… vagy K_z_ti_azonos_t_pontok…).
"""
import json, sys, os, unicodedata

def norm(s):
    return unicodedata.normalize("NFC", s).lower()

def find(folder):
    for f in sorted(os.listdir(folder)):
        n = norm(f)
        if f.endswith(".json") and ("közti_azonosító_pontok" in n or "k_z_ti_azonos_t_pontok" in n):
            return os.path.join(folder, f)
    sys.exit(f"Nem találom a Közti azonosító pontok .json fájlt a {folder} mappában")

def main():
    folder = sys.argv[1]
    html = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(__file__), "..", "index.html")
    s = open(html, encoding="utf-8", newline="").read()
    tag = '<script type="application/json" id="roaddata">'
    i = s.index(tag) + len(tag); j = s.index("</script>", i)
    D = json.loads(s[i:j])
    RI = {r.split("|")[0]: k for k, r in enumerate(D["roads"])}

    src = json.load(open(find(folder), encoding="utf-8"))
    crs = (src.get("crs") or {}).get("properties", {}).get("name", "")
    if crs and not crs.endswith("23700"):
        sys.exit(f"nem EOV koordináták: {crs}")
    feats = sorted(src["features"], key=lambda f: f["properties"]["kod"])
    codes, flat, npt = [], [], 0
    for f in feats:
        p = f["properties"]
        g = f["geometry"]
        pts = g["coordinates"] if g["type"] == "MultiPoint" else [g["coordinates"]]
        uniq = []
        for e, n in pts:
            e, n = round(e), round(n)
            if not any(abs(e - a) <= 1 and abs(n - b) <= 1 for a, b in uniq):
                uniq.append((e, n))
        roads = []
        for r in str(p["kszamok"] or "").split(","):
            r = r.strip()
            if not r: continue
            if r not in RI: raise SystemExit(f"ismeretlen út: {r!r} ({p['kod']})")
            if RI[r] not in roads: roads.append(RI[r])
        codes.append(p["kod"])
        flat.append(len(uniq)); npt += len(uniq)
        for e, n in uniq: flat += [e, n]
        flat.append(len(roads)); flat += roads
    D["cspk"] = codes
    D["csp"] = flat

    js = json.dumps(D, ensure_ascii=False, separators=(",", ":"))
    open(html, "w", encoding="utf-8", newline="").write(s[:i] + js + s[j:])
    add = len(json.dumps(codes, separators=(",", ":"))) + len(json.dumps(flat, separators=(",", ":")))
    print(f"azonosítópontok: {len(codes)} kód, {npt} pont · +{add/1e6:.2f} MB · roaddata {len(js)/1e6:.2f} MB")

if __name__ == "__main__":
    main()
