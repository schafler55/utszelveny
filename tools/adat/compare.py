#!/usr/bin/env python3
"""Compares two ÚtSzelvény road data builds (the `roaddata` JSON of two index.html files) by content, not by
position: roads by number, segments by road + carriageway + end points, every table as a set of records with
road numbers and texts filled in. Prints a Markdown report – the change report of a data update.

Usage:  python3 tools/adat/compare.py <old index.html or .json> <new index.html or .json> [--max 30]
"""
import argparse, collections, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from geo import decode  # noqa: E402

TAG = '<script type="application/json" id="roaddata">'


def load(path):
    s = open(path, encoding="utf-8").read()
    if path.endswith(".json"):
        return json.loads(s)
    i = s.index(TAG) + len(TAG)
    return json.loads(s[i:s.index("</script>", i)])


def fmt(v):
    return f"{v // 10000}+{v % 10000:03d}"


def tables(D):
    """every table as {name: set of records} with road numbers / texts instead of indexes"""
    R = [r.split("|")[0] for r in D["roads"]]
    S = D.get("str", [""])
    T = {}
    T["roads"] = {tuple(r.split("|", 1)) for r in D["roads"]}
    seg = {}
    mrn = D.get("mrn")          # [directorate's county code, mérnökség name(s)…] rows; not in data built before V1.3.2.0
    for s in D["segs"]:
        pts = decode(s[9])
        k = (R[s[0]], s[1], pts[0], pts[-1])
        seg[k] = dict(kut=s[2], cty=s[3], kez=D["kez"][s[4]], lab=D["lab"][s[5]], scale=s[6], an=s[7], pts=pts,
                      mrn=tuple(mrn[s[10]]) if mrn and len(s) > 10 else None)
    T["segs"] = seg
    T["mrn"] = {n for x in mrn or [] for n in x[1:]}

    def flat(key, n, f):
        a = D.get(key, [])
        return {f(a[i:i + n]) for i in range(0, len(a), n)}
    T["spd"] = flat("spd", 7, lambda x: (R[x[0]], x[1], x[2], x[3], x[4], x[5], S[x[6]]))
    T["szk"] = flat("szk", 5, lambda x: (R[x[0]], *x[1:]))
    tn = D.get("tnev", [])
    T["tel"] = flat("tel", 5, lambda x: (R[x[0]], x[1], x[2], x[3], tn[x[4]]))
    T["sav"] = flat("sav", 5, lambda x: (R[x[0]], *x[1:]))
    bt = D.get("burt", [])
    T["bur"] = flat("bur", 6, lambda x: (R[x[0]], x[1], x[2], x[3], x[4], bt[x[5]] if x[5] >= 0 else None))
    ks = D.get("ksz", [])
    st = [tuple(ks[i:i + 4]) for i in range(0, len(ks), 4)]
    T["anf"] = flat("anf", 5, lambda x: (R[x[0]], x[1], x[2], x[3], st[x[4]]))
    T["egy"] = flat("egy", 5, lambda x: (R[x[0]], *x[1:]))
    T["br"] = {(R[b[0]], b[1], b[2], b[3], S[b[4]], b[5], S[b[6]], tuple(b[7]), *(b[8:])) for b in D["br"]}
    T["tr"] = {(R[a[0]], a[1], a[2], a[3], a[4], a[5], S[a[6]], *((a[7], a[8], S[a[9]]) if len(a) > 7 else ()))
               for a in D["tr"]}
    csp, a, i, k = set(), D.get("csp", []), 0, 0
    while i < len(a):
        n = a[i]
        pos = tuple(sorted(tuple(a[i + 1 + 2 * j:i + 3 + 2 * j]) for j in range(n)))
        i += 1 + 2 * n
        m = a[i]
        rr = tuple(R[x] for x in a[i + 1:i + 1 + m])
        i += 1 + m
        csp.add((D["cspk"][k], pos, rr))
        k += 1
    T["csp"] = csp
    bm, a, pe, pn = set(), D.get("bm", []), 0, 0
    bn, bk = D.get("bmn", []), D.get("bmt", [])
    for i in range(0, len(a), 8):
        pe += a[i + 3]
        pn += a[i + 4]
        bm.add((R[a[i]], a[i + 1], a[i + 2], pe, pn, bn[a[i + 5]] if a[i + 5] >= 0 else None, a[i + 6],
                bk[a[i + 7]] if a[i + 7] >= 0 else None))
    T["bm"] = bm
    T["anfEv"] = {D.get("anfEv")}
    return T


def compare(A, B, mx=30):
    TA, TB = tables(A), tables(B)
    out, summary = [], {}
    # roads
    ra, rb = dict(TA["roads"]), dict(TB["roads"])
    add = sorted(set(rb) - set(ra))
    rem = sorted(set(ra) - set(rb))
    ren = sorted(k for k in set(ra) & set(rb) if ra[k] != rb[k])
    summary["roads"] = (len(ra), len(rb), len(add) + len(rem) + len(ren))
    if add or rem or ren:
        out.append("### Roads")
        out += [f"- new: **{k}** {rb[k]}" for k in add[:mx]]
        out += [f"- removed: **{k}** {ra[k]}" for k in rem[:mx]]
        out += [f"- renamed: **{k}** {ra[k]} → {rb[k]}" for k in ren[:mx]]
    # segments
    sa, sb = TA["segs"], TB["segs"]
    only_a = set(sa) - set(sb)
    only_b = set(sb) - set(sa)
    diffs = collections.Counter()
    anc = []
    mrn_ch = collections.Counter()
    for k in set(sa) & set(sb):
        x, y = sa[k], sb[k]
        for f in ("kut", "cty", "kez", "lab"):
            if x[f] != y[f]:
                diffs[f] += 1
        if x["mrn"] != y["mrn"] and x["mrn"] is not None and y["mrn"] is not None:
            diffs["igazgatóság / mérnökség"] += 1
            mrn_ch[(x["mrn"], y["mrn"])] += 1
        if abs(x["scale"] - y["scale"]) > 0.00011:
            diffs["scale"] += 1
        if x["pts"] != y["pts"]:
            diffs["geometry (same ends)"] += 1
        if x["an"] != y["an"]:
            xa, ya = x["an"], y["an"]
            if len(xa) != len(ya) or [v for i, v in enumerate(xa) if i % 3] != [v for i, v in enumerate(ya) if i % 3]:
                diffs["km anchors (other km set)"] += 1
                anc.append((1e9, k))
            else:
                d = max(abs(p - q) for p, q in zip(xa[0::3], ya[0::3]))
                if d > 0.05:
                    diffs["km anchors (moved)"] += 1
                    anc.append((d, k))
    summary["segs"] = (len(sa), len(sb), len(only_a) + len(only_b) + sum(diffs.values()))
    if only_a or only_b or diffs:
        out.append("### Segments")
        if only_a or only_b:
            per = collections.Counter(k[0] for k in only_a) + collections.Counter(k[0] for k in only_b)
            out.append(f"- {len(only_a)} segments only in the old data, {len(only_b)} only in the new "
                       f"(roads: {', '.join(f'{r} ({n})' for r, n in per.most_common(mx))})")
        for f, n in diffs.most_common():
            out.append(f"- {f}: {n}")
        if anc:
            anc.sort(reverse=True)
            out.append("- largest km anchor changes: " + ", ".join(
                f"{k[0]}/{k[1]} " + ("other km set" if d >= 1e9 else f"{d:.1f} m") for d, k in anc[:mx]))
        show = lambda m: (" + ".join(m[1:]) or "–") + (f" (igazgatóság {m[0]})" if m[0] else "")
        for (x, y), n in mrn_ch.most_common(mx):
            out.append(f"- mérnökség: {show(x)} → {show(y)} ({n} segments)")
    # igazgatóság + mérnökség (per segment; the data built before V1.3.2.0 has none)
    ma, mb = TA["mrn"], TB["mrn"]
    have = lambda S: sum(1 for x in S.values() if x["mrn"] and len(x["mrn"]) > 1)
    summary["mrn (segments)"] = (have(sa), have(sb), diffs["igazgatóság / mérnökség"] if ma else have(sb))
    if ma != mb:
        out.append(f"### Mérnökség names: −{len(ma - mb)} / +{len(mb - ma)}")
        if ma - mb:
            out.append("- − " + ", ".join(sorted(ma - mb)[:mx * 4]))
        if mb - ma:
            out.append("- + " + ", ".join(sorted(mb - ma)[:mx * 4]))
    # record tables
    names = {"spd": "Speed limits", "szk": "Built-up sections", "tel": "Town names (OSM)", "sav": "Lanes",
             "bur": "Pavement", "anf": "Traffic", "egy": "One-way", "br": "Bridges", "tr": "Truck restrictions",
             "csp": "Identification points", "bm": "Bus stops", "anfEv": "Traffic year"}
    for t, title in names.items():
        a, b = TA[t], TB[t]
        ra_, rb_ = a - b, b - a
        summary[t] = (len(a), len(b), len(ra_) + len(rb_))
        if ra_ or rb_:
            out.append(f"### {title}: −{len(ra_)} / +{len(rb_)}")
            per = collections.Counter(x[0] for x in ra_ | rb_ if isinstance(x, tuple))
            if per:
                out.append("- roads: " + ", ".join(f"{r} ({n})" for r, n in per.most_common(mx)))
            for x in sorted(ra_, key=str)[:min(mx, 10)]:
                out.append(f"- − `{x}`")
            for x in sorted(rb_, key=str)[:min(mx, 10)]:
                out.append(f"- + `{x}`")
    head = ["| Table | Old | New | Changed records |", "|---|---:|---:|---:|"]
    head += [f"| {k} | {a:,} | {b:,} | {c:,} |".replace(",", ".") for k, (a, b, c) in summary.items()]
    return "\n".join(head + [""] + out), summary


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("old")
    ap.add_argument("new")
    ap.add_argument("--max", type=int, default=30)
    a = ap.parse_args()
    rep, _ = compare(load(a.old), load(a.new), a.max)
    print(rep)


if __name__ == "__main__":
    main()
