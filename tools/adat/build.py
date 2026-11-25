#!/usr/bin/env python3
"""Builds ÚtSzelvény's whole road data (the `roaddata` JSON inside web/index.html) from the NAP WFS downloads.

Usage:
  python3 tools/adat/build.py <folder with the 13 NAP .json files> [web/index.html] [--date YYYY-MM-DD]

* Every table is rebuilt from scratch in one go – all tables point to roads by their position in `roads`, so a
  partial update after a network change would attach data to the wrong roads.
* Deterministic: the same files give a byte-identical index.html (the WFS returns features in a different
  order on every download, so everything is sorted here).
* Only the `roaddata` block of index.html is replaced; nothing else in the file changes.
* Any unexpected input (missing file or field, unknown code, unknown road number, incomplete download) stops
  the build with an error and leaves index.html untouched.
* The files are recognised by the WFS layer name in their feature ids (see layers.json); file names don't matter.

The town names on built-up (átkelési) sections come from tools/adat/osm/telepulesek.json (OpenStreetMap, ODbL).
"""
import argparse, collections, datetime, json, math, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from geo import (cval, plen, simplify, project, point_at, encode, decode, chainage, along_at, in_ring)  # noqa: E402
from napdata import DataError, manifest, find_layers, load_layer  # noqa: E402
from check import check  # noqa: E402

TAG = '<script type="application/json" id="roaddata">'
KUT = {"1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9, "K": 10, "P": 11}
SIMPLIFY_M = 1.0        # geometry simplification tolerance (Douglas–Peucker, metres)
POST_MAX_D = 50         # a km post further than this from the road is not used
MIN_KM_SPACING = 800    # a missing km post is interpolated only where the known km points are at least this far apart per km;
                        # closer than that the chainage skips km numbers there (e.g. road 24141 km 0 → 3 in 2.3 km)
TEL_STEP = 10           # town-name sampling step along built-up sections (m)
TEL_MIN = 30            # shorter town pieces go to the neighbouring name (m)
TEL_END_MIN = 100       # same for the first / last piece of a section (NAP sections run a little past the town line)


def road_key(num):
    m = re.fullmatch(r"([A-Za-z]*)(\d+)(.*)", num)
    if not m:
        return (2, num, 0, "")
    return (0 if m.group(1).upper() == "M" else 1, m.group(1), int(m.group(2)), m.group(3))


class Strings:
    """shared text list `str` (index 0 = empty text)"""
    def __init__(self):
        self.a, self.i = [""], {"": 0}

    def __call__(self, s):
        s = "" if s is None else str(s)
        if s not in self.i:
            self.i[s] = len(self.a)
            self.a.append(s)
        return self.i[s]


def flat_pts(geom):
    return [(c[0], c[1]) for part in geom["coordinates"] for c in part]


# ---------------------------------------------------------------------------------------------------------------
# km anchors: [along, km, m] triples; chainage grows along every segment's geometry
# ---------------------------------------------------------------------------------------------------------------
def build_anchors(s, posts):
    """[along, km, m] triples of one segment (dict with a, b = chainage values, pts, L, scale); posts =
    {km: [(x, y)]} of its road + carriageway from Szelvényjelek.
    Whole-km anchors: the km post projected on the segment (within POST_MAX_D). A km without a post is placed
    evenly between the nearest known km points of the segment – its posts, and the segment start's km measured
    back from the start with the segment's scale – if they are at least MIN_KM_SPACING apart per km; otherwise
    it is measured from the segment start with the scale. Interpolated anchors that would break the order of
    the posts are left out (e.g. km numbers skipped by the chainage)."""
    ka, ma = divmod(s["a"], 10000)
    kb, mb = divmod(s["b"], 10000)
    L, sc = s["L"], s["scale"]
    want = [K for K in range(ka + 1, kb + 1) if not (K == kb and mb == 0)]
    known = {}
    for K in want:
        best = None
        for x, y in posts.get(K, ()):
            dd, al = project(s["pts"], x, y)
            if dd < POST_MAX_D and 0 < al < L and (best is None or dd < best[0]):
                best = (dd, al)
        if best:
            known[K] = best[1]
    ref = dict(known)
    ref[ka] = -ma / sc
    ks = sorted(ref)
    an = [(0.0, ka, ma, 2)]
    for K in want:
        if K in known:
            an.append((round(known[K], 1), K, 0, 1))
            continue
        lo = [k for k in ks if k < K]
        hi = [k for k in ks if k > K]
        if lo and hi:
            k1, k2 = lo[-1], hi[0]
            if (ref[k2] - ref[k1]) / (k2 - k1) < MIN_KM_SPACING:
                continue        # km sections far too short: the chainage skips km numbers here
            al = ref[k1] + (K - k1) / (k2 - k1) * (ref[k2] - ref[k1])
        else:
            dm = (K - ka) * 1000 - ma
            al = dm / sc if dm > 0 else L - ((kb - K) * 1000 + mb) / sc
        if 0 < al < L:
            an.append((round(al, 1), K, 0, 0))
    an.append((round(L, 1), kb, mb, 2))
    fixed = [x for x in an if x[3]]
    out = []
    for x in an:
        if not x[3]:
            v = x[1] * 10000 + x[2]
            prev = max([y[0] for y in fixed if y[1] * 10000 + y[2] < v] + [-1])
            nxt = min([y[0] for y in fixed if y[1] * 10000 + y[2] > v] + [1e18])
            if not prev < x[0] < nxt:
                continue
        out.append(x)
    return [v for t in out for v in t[:3]]


# ---------------------------------------------------------------------------------------------------------------
class Net:
    """the built segments, for chainage look-ups by the other tables"""
    def __init__(self, segs):
        self.segs = segs
        self.by = collections.defaultdict(list)
        self.road = collections.defaultdict(list)
        for s in segs:
            self.by[(s["r"], s["pk"])].append(s)
            self.road[s["r"]].append(s)

    def locate(self, r, pk, x, y):
        """nearest point on road r (carriageway pk, None = any) -> (distance, chainage value, pk)"""
        best = None
        for s in (self.road[r] if pk is None else self.by[(r, pk)]):
            dd, al = project(s["pts"], x, y)
            if best is None or dd < best[0]:
                best = (dd, chainage(s["an"], s["scale"], al), s["pk"])
        return best


def ranges(rows):
    """sorted [(r, pk, from, to, value)], touching pieces with the same value merged"""
    rows.sort()
    out = []
    for x in rows:
        if out:
            y = out[-1]
            if y[0] == x[0] and y[1] == x[1] and y[4] == x[4] and x[2] <= y[3]:
                out[-1] = (y[0], y[1], y[2], max(y[3], x[3]), y[4])
                continue
        out.append(x)
    return out


def ranges1(rows):
    """like ranges() but also merges pieces 1 m apart (as the section-data importer did)"""
    rows.sort()
    out = []
    for x in rows:
        if out:
            y = out[-1]
            if y[0] == x[0] and y[1] == x[1] and y[4] == x[4] and x[2] <= y[3] + 1:
                out[-1] = (y[0], y[1], y[2], max(y[3], x[3]), y[4])
                continue
        out.append(x)
    return out


# ---------------------------------------------------------------------------------------------------------------
def build(folder, osm_path, date=None):
    M = manifest()["layers"]
    paths = find_layers(folder)
    F, INFO = {}, {}
    for k in M:
        F[k], INFO[k] = load_layer(k, paths[k])
    P = {k: [x["properties"] for x in v] for k, v in F.items()}
    warn = []

    def code_check(k, field, allowed):
        bad = sorted({str(p.get(field)) for p in P[k] if p.get(field) not in allowed})
        if bad:
            raise DataError(f"{M[k]['name']}: unknown {field} value(s): {', '.join(bad[:10])}")
    for k, spec in M.items():
        for field, allowed in (spec.get("codes") or {}).items():
            if field in ("hkorlt", "sulyk_kod"):      # checked where they are used
                continue
            code_check(k, field, list(allowed))

    D = {}
    # ---------------- roads ----------------
    names = collections.defaultdict(collections.Counter)
    for p in P["kutka"]:
        names[str(p["kszam"]).strip()][(p["utnev"] or "").strip()] += 1
    nums = sorted({str(p["kszam"]).strip() for p in P["halozat"]}, key=road_key)
    for n in nums:
        if n not in names:
            warn.append(f"road {n}: no name in {M['kutka']['name']}")
        elif len(names[n]) > 1:
            warn.append(f"road {n}: {len(names[n])} different names, the most common is used")
    only_k = sorted(set(names) - set(nums), key=road_key)
    if only_k:
        warn.append(f"{len(only_k)} road number(s) only in {M['kutka']['name']}: {', '.join(only_k[:10])}")
    D["roads"] = [n + "|" + (sorted(names[n].items(), key=lambda x: (-x[1], x[0]))[0][0] if n in names else "")
                  for n in nums]
    RI = {n: i for i, n in enumerate(nums)}

    def road(k, p):
        r = RI.get(str(p["kszam"]).strip())
        if r is None:
            raise DataError(f"{M[k]['name']}: unknown road number {p['kszam']!r}")
        return r

    # ---------------- operators (kezelő) per network segment ----------------
    net_ids = [p["id"] for p in P["halozat"]]
    kut_by_id = {p["id"]: p for p in P["kutka"]}
    if set(kut_by_id) == set(net_ids):
        kez_of = {i: (kut_by_id[i]["kezelo"] or "") for i in net_ids}
    else:
        raise DataError(f"{M['kutka']['name']}: its ids no longer match the network – the range join for the "
                        f"extended package (Mérnökség) has to be added to build.py")

    # ---------------- segments ----------------
    raw = []
    for f in F["halozat"]:
        p = f["properties"]
        pts = [(round(x), round(y)) for x, y in simplify(flat_pts(f["geometry"]), SIMPLIFY_M)]
        if len(pts) < 2:
            raise DataError(f"segment {p['id']} ({p['kszam']}): fewer than 2 points")
        raw.append(dict(id=p["id"], p=p, road=str(p["kszam"]).strip(), r=road("halozat", p), pk=int(p["pkod"]),
                        a=cval(p["kszelv"]), b=cval(p["vszelv"]), pts=pts))
    raw.sort(key=lambda s: (s["r"], s["pk"], s["a"], s["b"], s["id"]))
    for i, s in enumerate(raw):
        s["i"] = i
        s["L"] = plen(s["pts"])
        # metres of chainage per metre of geometry: NAP segment length / drawn length (a few NAP lengths are
        # placeholders like 1 m on a 200 m segment – those use 1)
        r = (s["p"]["szho"] or 0) / s["L"] if s["L"] > 0 else 0
        s["scale"] = r if 0.25 <= r <= 4 else 1.0
    posts = collections.defaultdict(lambda: collections.defaultdict(list))
    for f in F["kmjel"]:
        p = f["properties"]
        x, y = f["geometry"]["coordinates"][:2]
        posts[(str(p["kszam"]).strip(), int(p["pkod"]))][int(p["kmjel"])].append((x, y))
    kez, kezi, lab, labi = [], {}, [""], {"": 0}
    segs = []
    for s in raw:
        p = s["p"]
        kz = kez_of[s["id"]]
        if kz not in kezi:
            kezi[kz] = len(kez)
            kez.append(kz)
        lb = (p["szak_label"] or "") if p["szak_tipus"] == 2 else ""
        if lb not in labi:
            labi[lb] = len(lab)
            lab.append(lb)
        cty = 0
        for code in (p["kkod"] or "", p["vkod"] or ""):
            if code[1:3].isdigit() and int(code[1:3]):
                cty = int(code[1:3])
                break
        s["an"] = build_anchors(s, posts.get((s["road"], s["pk"]), {}))
        s["scale4"] = round(s["scale"], 4)
        segs.append([s["r"], s["pk"], KUT[p["kutka"]], cty, kezi[kz], labi[lb], s["scale4"], s["an"],
                     len(s["pts"]), encode(s["pts"])])
    D["kez"], D["lab"], D["segs"] = kez, lab, segs
    for s in raw:            # look-ups use the stored (rounded) scale, like the app
        s["scale"] = s["scale4"]
    NET = Net(raw)

    STR = Strings()
    # ---------------- speed limits ----------------
    SEBKIR = {"teljes keresztmetszetre": 0, None: 0, "szelvényezéssel azonos": 1, "szelvényezéssel ellentétes": 2}
    rows = []
    for p in P["sebkorl"]:
        a, b = cval(p["kszelv"]), cval(p["vszelv"])
        rows.append((road("sebkorl", p), int(p["pkod"]), min(a, b), max(a, b), int(p["sebkorl"]),
                     SEBKIR[p["sebkir"]], (p["sebkieg"] or "").strip()))
    rows.sort()
    D["spd"] = [v for x in rows for v in (*x[:6], STR(x[6]))]

    # ---------------- built-up sections ----------------
    BU = {"külsőségi": 0, "átkelési": 1}
    szk = ranges([(road("szakjel", p), int(p["pkod"]), *sorted((cval(p["kszelv"]), cval(p["vszelv"]))),
                   BU[p["szakjel"]]) for p in P["szakjel"]])
    D["szk"] = [v for x in szk for v in x]

    # ---------------- bridges ----------------
    HK = M["hid"]["codes"]["hkorlt"]
    UNDER = (4, 5, 9)            # limits for the road under the bridge (height, rigid gate, width)
    br, der = [], []
    numre = re.compile(r"\d+")
    for f in F["hid"]:
        p = f["properties"]
        lim = []
        for i in range(1, 7):
            t = p.get(f"hkorlt{i}")
            if t is None:
                continue
            if t not in HK:
                raise DataError(f"{M['hid']['name']}: unknown limit type {t!r}")
            if HK[t]:
                v = p.get(f"hkorle{i}")
                lim.append((HK[t], -1 if v is None else v))
        r, pk, v = road("hid", p), int(p["pkod"]), cval(p["kszelv"])
        over = 1 if p["hhely"] == "közút feletti híd" else 0
        name = (p["hnev"] or "").strip()
        own = [x for x in lim if x[0] not in UNDER]
        under = [x for x in lim if x[0] in UNDER]
        rec = dict(r=r, pk=pk, v=v, name=name, hnem=p["hnem"] or "", over=over, tb=p["huzemtb"] or "",
                   rs=[w for x in own for w in x])
        br.append(rec)
        x, y = f["geometry"]["coordinates"][:2]
        if over and pk in (1, 2) and NET.by[(r, 3 - pk)]:
            # a structure over a divided road: the record is on one carriageway only – copy it to the other
            hit = NET.locate(r, 3 - pk, x, y)
            if hit[0] < 100:
                br.append(dict(rec, pk=3 - pk, v=hit[1]))
            else:
                warn.append(f"bridge {name!r} on {p['kszam']}: other carriageway {hit[0]:.0f} m away, not copied")
        if under:
            # limits under the bridge belong to the road below: a record on it when the name names that road
            for n in numre.findall(name):
                if n == str(p["kszam"]) or n not in RI:
                    continue
                hit = NET.locate(RI[n], None, x, y)
                if hit and hit[0] < 50:
                    der.append((hit[0], dict(r=RI[n], pk=hit[2], v=hit[1], name=name, hnem=p["hnem"] or "", over=1,
                                             tb=p["huzemtb"] or "", rs=[w for x in under for w in x],
                                             der=1, upper=str(p["kszam"]))))
    seen = set()
    for dd, rec in sorted(der, key=lambda x: (x[0], x[1]["r"], x[1]["name"])):
        k = (rec["r"], rec["name"])
        if k not in seen:
            seen.add(k)
            br.append(rec)
    br.sort(key=lambda b: (b["r"], b["pk"], b["v"], b["name"], b["over"], json.dumps(b["rs"]), b.get("der", 0)))
    D["br"] = []
    for b in br:
        row = [b["r"], b["pk"], b["v"], b["name"], STR(b["hnem"]), b["over"], STR(b["tb"]), b["rs"]]
        if b.get("der"):
            row += [1, b["upper"]]
        D["br"].append(row)

    # ---------------- truck restrictions ----------------
    TK = M["teher"]["codes"]["sulyk_kod"]
    tr = []
    for p in P["teher"]:
        if p["sulyk_kod"] is None:
            continue
        for c in ("sulyk_kod", "sulyk2_kod"):
            if p[c] is not None and str(p[c]) not in TK:
                raise DataError(f"{M['teher']['name']}: unknown restriction code {p[c]!r}")
        a, b = cval(p["kszelv"]), cval(p["vszelv"])
        row = [road("teher", p), int(p["pkod"]), min(a, b), max(a, b), TK[str(p["sulyk_kod"])],
               -1 if p["sulykorl"] is None else p["sulykorl"],
               (p["sulykieg"] or "").strip()]
        if p["sulyk2_kod"] is not None:
            row += [TK[str(p["sulyk2_kod"])], -1 if p["sulykorl2"] is None else p["sulykorl2"], (p["sulykieg2"] or "").strip()]
        tr.append(row)
    tr.sort(key=lambda x: json.dumps(x, ensure_ascii=False))
    tr.sort(key=lambda x: (x[0], x[1], x[2], x[3]))
    for row in tr:
        row[6] = STR(row[6])
        if len(row) > 7:
            row[9] = STR(row[9])
    D["tr"] = tr
    D["str"] = STR.a

    # ---------------- town names on built-up sections (OpenStreetMap) ----------------
    D["tnev"], D["tel"] = town_names(szk, NET, osm_path, warn)

    # ---------------- section data: lanes, pavement, traffic ----------------
    sav = ranges1([(road("sav", p), int(p["pkod"]), *sorted((cval(p["kszelv"]), cval(p["vszelv"]))),
                    int(p["savossz"])) for p in P["sav"]])
    D["sav"] = [v for x in sav for v in x]
    burt = sorted({p["rbtip"] for p in P["burkolat"] if p["rbtip"]})
    bur = ranges1([(road("burkolat", p), int(p["pkod"]), *sorted((cval(p["kszelv"]), cval(p["vszelv"]))),
                    (round(float(p["rbtsz"]) * 10) if p["rbtsz"] is not None else -1,
                     burt.index(p["rbtip"]) if p["rbtip"] else -1)) for p in P["burkolat"]])
    D["burt"] = burt
    D["bur"] = [v for x in bur for v in (x[0], x[1], x[2], x[3], x[4][0], x[4][1])]
    num = lambda v: int(v) if v is not None else -1
    key = lambda p: (num(p["asz"]), num(p["anf"]), num(p["oj"]), num(p["ongj2"]))
    st = sorted({key(p) for p in P["forgalom"]})
    sti = {k: n for n, k in enumerate(st)}
    anf = ranges1([(road("forgalom", p), int(p["pkod"]), *sorted((cval(p["kszelv"]), cval(p["vszelv"]))),
                    sti[key(p)]) for p in P["forgalom"]])
    D["ksz"] = [v for x in st for v in x]
    D["anf"] = [v for x in anf for v in x]
    D["anfEv"] = max(int(p["ev"]) for p in P["forgalom"] if p["ev"] is not None)

    # ---------------- road identification points (közúti azonosítópontok) ----------------
    codes, flat = [], []
    for f in sorted(F["csp"], key=lambda f: f["properties"]["kod"]):
        p = f["properties"]
        g = f["geometry"]
        pts = g["coordinates"] if g["type"] == "MultiPoint" else [g["coordinates"]]
        uniq = []
        for c in pts:
            e, n = round(c[0]), round(c[1])
            if not any(abs(e - a) <= 1 and abs(n - b) <= 1 for a, b in uniq):
                uniq.append((e, n))
        rr = []
        for x in str(p["kszamok"] or "").split(","):
            x = x.strip()
            if not x:
                continue
            if x not in RI:
                raise DataError(f"{M['csp']['name']}: unknown road number {x!r} ({p['kod']})")
            if RI[x] not in rr:
                rr.append(RI[x])
        codes.append(p["kod"])
        flat.append(len(uniq))
        for e, n in uniq:
            flat += [e, n]
        flat.append(len(rr))
        flat += rr
    D["cspk"], D["csp"] = codes, flat

    # ---------------- one-way carriageways ----------------
    rows = []
    for p in P["irany"]:
        t = p["irany"]
        d_ = 1 if "egyező" in t else 2
        a, b = cval(p["kszelv"]), cval(p["vszelv"])
        rows.append((road("irany", p), int(p["pkod"]), min(a, b), max(a, b), d_))
    egy = ranges1(rows)
    D["egy"] = [v for x in egy for v in x]

    # ---------------- bus stops ----------------
    SIDES = {"jobboldali": 0, "baloldali": 1, "útközepén": 2}
    bnames = sorted({(p["mnev"] or "").strip() for p in P["megallo"] if (p["mnev"] or "").strip()})
    kinds = sorted({p["mkiep"] for p in P["megallo"] if p["mkiep"]})
    ni = {n: k for k, n in enumerate(bnames)}
    stops = []
    for f in F["megallo"]:
        p = f["properties"]
        e, n = f["geometry"]["coordinates"][:2]
        nm = (p["mnev"] or "").strip()
        stops.append((road("megallo", p), int(p["pkod"]), cval(p["kszelv"]), round(e), round(n),
                      ni[nm] if nm else -1, SIDES[p["mold"]], kinds.index(p["mkiep"]) if p["mkiep"] else -1))
    stops.sort()
    bm, pe, pn = [], 0, 0
    for x in stops:
        bm += [x[0], x[1], x[2], x[3] - pe, x[4] - pn, x[5], x[6], x[7]]
        pe, pn = x[3], x[4]
    D["bm"], D["bmn"], D["bmt"] = bm, bnames, kinds

    # ---------------- what this data was built from ----------------
    ts = sorted(i["timeStamp"] for i in INFO.values() if i.get("timeStamp"))
    D["meta"] = {
        "date": date or (ts[-1][:10] if ts else datetime.date.today().isoformat()),
        "layers": {k: {"n": INFO[k]["features"], "sha": INFO[k]["sha"]} for k in M},
        "osm": json.load(open(osm_path, encoding="utf-8")).get("downloaded", ""),
    }
    for k in M:
        if INFO[k]["new_fields"]:
            warn.append(f"{M[k]['name']}: new field(s) not used yet: {', '.join(INFO[k]['new_fields'])}")
    return D, INFO, warn


# ---------------------------------------------------------------------------------------------------------------
def town_names(szk, NET, osm_path, warn):
    """[(r, pk, from, to, name index)] for the built-up (átkelési) sections: the settlement polygon the road runs
    in, sampled every TEL_STEP m; short pieces (< 30 m) and end pieces (< 100 m, where the NAP section runs a little
    past the town line) go to the neighbouring name."""
    O = json.load(open(osm_path, encoding="utf-8"))
    names = O["names"]
    polys = []
    for row in O["polys"]:
        rings = [decode(r) for r in row[1:]]
        xs = [x for x, _ in rings[0]]
        ys = [y for _, y in rings[0]]
        polys.append((row[0], rings, (min(xs), min(ys), max(xs), max(ys))))
    C = 5000
    grid = collections.defaultdict(list)
    for k, (_, _, bb) in enumerate(polys):
        for gx in range(int(bb[0] // C), int(bb[2] // C) + 1):
            for gy in range(int(bb[1] // C), int(bb[3] // C) + 1):
                grid[(gx, gy)].append(k)

    def name_at(x, y):
        for k in grid.get((int(x // C), int(y // C)), ()):
            ni, rings, bb = polys[k]
            if bb[0] <= x <= bb[2] and bb[1] <= y <= bb[3] and in_ring(x, y, rings[0]) and \
                    not any(in_ring(x, y, h) for h in rings[1:]):
                return ni
        return None

    out = []
    for r, pk, f, t, bu in szk:
        if bu != 1:
            continue
        segs = NET.by[(r, pk)] or NET.road[r]
        samples = []                             # (chainage, name, segment, along)
        for s in segs:
            c0, c1 = chainage(s["an"], s["scale"], 0), chainage(s["an"], s["scale"], s["L"])
            if c1 < f or c0 > t:
                continue
            a0 = along_at(s["an"], s["scale"], s["L"], max(f, c0))
            a1 = along_at(s["an"], s["scale"], s["L"], min(t, c1))
            al = a0
            while True:
                x, y = point_at(s["pts"], al)
                samples.append((chainage(s["an"], s["scale"], al), name_at(x, y), s["i"], al))
                if al >= a1:
                    break
                al = min(a1, al + TEL_STEP)
        samples.sort(key=lambda x: x[0])
        runs = []                                # [name, from, to, metres along the road]
        last = None
        for v, n, si, al in samples:
            step = (al - last[3] if last and last[2] == si else TEL_STEP) if last else 0
            if n is None:
                last = (v, n, si, al)
                continue
            if runs and runs[-1][0] == n:
                runs[-1][2] = v
                runs[-1][3] += step
            else:
                b = v
                if runs and last and last[2] == si and last[1] == runs[-1][0]:
                    s = NET.segs[si]                 # town line between two samples: find it to ~0.5 m
                    lo, hi = last[3], al
                    while hi - lo > 0.5:
                        mid = (lo + hi) / 2
                        if name_at(*point_at(s["pts"], mid)) == runs[-1][0]:
                            lo = mid
                        else:
                            hi = mid
                    b = chainage(s["an"], s["scale"], lo)
                    runs[-1][3] += lo - last[3]
                    step = al - lo
                if runs:
                    runs[-1][2] = b
                runs.append([n, b + 1, v, step])
            last = (v, n, si, al)
        if not runs:
            continue
        runs[0][1], runs[-1][2] = f, t
        changed = True
        while changed and len(runs) > 1:
            changed = False
            for i, x in enumerate(runs):
                end = i == 0 or i == len(runs) - 1
                if x[3] < TEL_MIN or (end and x[3] < TEL_END_MIN):
                    j = i - 1 if i > 0 else i + 1
                    y = runs[j]
                    y[1], y[2], y[3] = min(y[1], x[1]), max(y[2], x[2]), y[3] + x[3]
                    del runs[i]
                    changed = True
                    break
            merged = [runs[0]]
            for x in runs[1:]:
                if x[0] == merged[-1][0]:
                    merged[-1][2] = x[2]
                    merged[-1][3] += x[3]
                else:
                    merged.append(x)
            runs = merged
        for n, a, b, _ in runs:
            out.append((r, pk, a, b, n))
    out = ranges1(out)
    used = sorted({x[4] for x in out}, key=lambda i: names[i])
    tnev = [names[i] for i in used]
    ix = {i: k for k, i in enumerate(used)}
    return tnev, [v for x in out for v in (x[0], x[1], x[2], x[3], ix[x[4]])]


# ---------------------------------------------------------------------------------------------------------------
def read_roaddata(html):
    s = open(html, encoding="utf-8", newline="").read()
    i = s.index(TAG) + len(TAG)
    j = s.index("</script>", i)
    return s, i, j


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("folder")
    ap.add_argument("html", nargs="?", default=os.path.join(HERE, "..", "..", "web", "index.html"))
    ap.add_argument("--date", help="data date for Névjegy (default: newest download time of the files)")
    ap.add_argument("--osm", default=os.path.join(HERE, "osm", "telepulesek.json"))
    ap.add_argument("--json", help="also write the roaddata JSON to this file")
    ap.add_argument("--force", action="store_true", help="write index.html even when a check fails")
    a = ap.parse_args()
    try:
        D, INFO, warn = build(a.folder, a.osm, a.date)
    except DataError as e:
        sys.exit(f"STOP: {e}")
    s, i, j = read_roaddata(a.html)
    try:
        old = json.loads(s[i:j])
    except ValueError:
        old = None
    err, w2, nums = check(D, old)
    warn += w2
    for w in warn:
        print("warning:", w)
    if err and not a.force:
        sys.exit("STOP: " + "; ".join(err) + " (index.html not changed; --force writes it anyway)")
    js = json.dumps(D, ensure_ascii=False, separators=(",", ":"))
    open(a.html, "w", encoding="utf-8", newline="").write(s[:i] + js + s[j:])
    if a.json:
        open(a.json, "w", encoding="utf-8").write(js)
    print(f"roads {len(D['roads'])} · segments {len(D['segs'])} · bridges {len(D['br'])} · "
          f"{nums['length_km']:,.0f} km · roaddata {len(js.encode()) / 1e6:.2f} MB · "
          f"index.html {os.path.getsize(a.html) / 1e6:.2f} MB".replace(",", "."))


if __name__ == "__main__":
    main()
