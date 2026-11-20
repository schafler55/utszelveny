#!/usr/bin/env python3
"""NAP szakaszadatok beépítése az ÚtSzelvény index.html-be.

Beolvassa a NAP WFS-ből letöltött GeoJSON-fájlokat, és a beágyazott `roaddata` JSON-ba írja:
  sav  – forgalmi sávok száma        [út, pálya, tól, ig, sávok]
  bur  – burkolat típusa, szélessége [út, pálya, tól, ig, szélesség dm-ben, típus-index] + burt (típusnevek); hiányzó adat: -1
  anf  – éves keresztmetszeti forgalom [út, pálya, tól, ig, állomás-index] + ksz (állomásonként asz, anf, oj, ongj2; hiányzó: -1) + anfEv
         asz = forgalomszámláló állomás száma, anf = évi átlagos napi keresztmetszeti forgalom (egységjármű/nap),
         oj = összes jármű forgalom (jármű/nap), ongj2 = nehéz motoros forgalom (jármű/nap)  – a NAP adatcsomag-leírás szerint
A geometriát nem használja (az alkalmazásban már megvan): az út száma (kszam), a pálya (pkod)
és a szelvény (kszelv / vszelv, km*10000+m) köti az utakhoz. Az egymáshoz érő, azonos értékű darabok összevonódnak.

Használat:  python3 tools/nap_szakaszadatok.py <mappa a .json fájlokkal> [index.html]
A fájlokat a nevük eleje alapján ismeri fel (Összes_gépjármű_forgalmi_sávok_száma…, Burkolat_típusa…, Éves_keresztmetszeti_forgalmi…).
"""
import json, re, sys, os, unicodedata

def norm(s):
    return unicodedata.normalize("NFC", s).lower()

def find(folder, prefix):
    for f in sorted(os.listdir(folder)):
        if norm(f).startswith(norm(prefix)) and f.endswith(".json"):
            return os.path.join(folder, f)
    sys.exit(f"Nem találom: {prefix}*.json a {folder} mappában")

CH = re.compile(r"\s*(\d+)\s*\+\s*(\d+)\s*$")
def cval(s):
    m = CH.match(str(s))
    if not m: raise ValueError(f"rossz szelvény: {s!r}")
    return int(m[1]) * 10000 + int(m[2])

def load(path):
    d = json.load(open(path, encoding="utf-8"))
    return [x["properties"] for x in d["features"]]

def ranges(props, RI, val):
    """[(r, pk, f, t, value)] sorted, touching pieces with the same value merged"""
    rows = []
    for p in props:
        r = RI.get(str(p["kszam"]).strip())
        if r is None: raise SystemExit(f"ismeretlen út: {p['kszam']!r}")
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
    # hiányzó szélesség / típus (néhány földút): -1
    bur = ranges(bp, RI, lambda p: (round(float(p["rbtsz"]) * 10) if p["rbtsz"] is not None else -1,
                                    burt.index(p["rbtip"]) if p["rbtip"] else -1))
    D["burt"] = burt
    D["bur"] = [v for x in bur for v in (x[0], x[1], x[2], x[3], x[4][0], x[4][1])]

    ap = load(find(folder, "Éves_keresztmetszeti_forgalmi"))
    num = lambda v: int(v) if v is not None else -1          # hiányzó érték: -1
    key = lambda p: (num(p["asz"]), num(p["anf"]), num(p["oj"]), num(p["ongj2"]))
    st = sorted({key(p) for p in ap})
    si = {k: n for n, k in enumerate(st)}
    anf = ranges(ap, RI, lambda p: si[key(p)])
    D["ksz"] = [v for x in st for v in x]
    D["anf"] = [v for x in anf for v in x]
    D["anfEv"] = sorted({int(p["ev"]) for p in ap})[-1]

    js = json.dumps(D, ensure_ascii=False, separators=(",", ":"))
    open(html, "w", encoding="utf-8", newline="").write(s[:i] + js + s[j:])
    print(f"sáv {len(sav)} szakasz · burkolat {len(bur)} szakasz, {len(burt)} típus · "
          f"forgalom {len(anf)} szakasz, {len(st)} állomás ({D['anfEv']}) · roaddata {len(js)/1e6:.2f} MB")

if __name__ == "__main__":
    main()
