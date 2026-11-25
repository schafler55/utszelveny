"""Checks of a built road data set (gate 4–5 of the data pipeline): geometry sanity, and plausibility against the
data it replaces. build.py runs them before writing index.html; an error stops the build."""
import math
from geo import decode

EOV_BOX = (380000, 30000, 960000, 380000)    # Hungary in EOV metres, with a margin
MAX_DROP = 0.10                              # a table losing more records than this: probably a partial NAP export
MAX_NET_DROP = 0.01                          # the network losing more length than this


def net_length(D):
    tot = 0.0
    for s in D["segs"]:
        p = decode(s[9])
        tot += sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(p, p[1:]))
    return tot


def counts(D):
    n = lambda k, w: len(D.get(k, [])) // w
    return {"roads": len(D["roads"]), "segments": len(D["segs"]), "speed limits": n("spd", 7),
            "built-up sections": n("szk", 5), "bridges": len(D["br"]), "truck restrictions": len(D["tr"]),
            "lanes": n("sav", 5), "pavement": n("bur", 6), "traffic": n("anf", 5), "one-way": n("egy", 5),
            "identification points": len(D.get("cspk", [])), "bus stops": n("bm", 8), "town names": n("tel", 5)}


def check(D, old=None):
    """-> (errors, warnings, numbers for the report)"""
    err, warn = [], []
    bad_box = bad_an = bad_scale = 0
    for s in D["segs"]:
        pts = decode(s[9])
        if len(pts) < 2 or len(pts) != s[8]:
            err.append(f"segment of road {D['roads'][s[0]].split('|')[0]}: wrong point count")
        if any(not (EOV_BOX[0] <= e <= EOV_BOX[2] and EOV_BOX[1] <= n <= EOV_BOX[3]) for e, n in pts):
            bad_box += 1
        an = s[7]
        al = an[0::3]
        ch = [an[i + 1] * 10000 + an[i + 2] for i in range(0, len(an), 3)]
        if any(b <= a for a, b in zip(al, al[1:])) or any(b < a for a, b in zip(ch, ch[1:])):
            bad_an += 1
        if not 0.25 <= s[6] <= 4:
            bad_scale += 1
    if bad_box:
        err.append(f"{bad_box} segments have points outside Hungary")
    if bad_an:
        err.append(f"{bad_an} segments have km anchors out of order")
    if bad_scale:
        warn.append(f"{bad_scale} segments have an unusual chainage / length ratio")
    roads_with = {s[0] for s in D["segs"]}
    if len(roads_with) != len(D["roads"]):
        err.append(f"{len(D['roads']) - len(roads_with)} roads have no segment")
    if any("|" not in r or not r.split("|", 1)[1] for r in D["roads"]):
        warn.append(f"{sum(1 for r in D['roads'] if not r.split('|', 1)[1])} roads have no name")
    new_c = counts(D)
    nums = {"counts": new_c, "length_km": round(net_length(D) / 1000, 1)}
    if old:
        old_c = counts(old)
        nums["old_counts"] = old_c
        for k, v in new_c.items():
            o = old_c.get(k, 0)
            if o and v < o * (1 - MAX_DROP):
                err.append(f"{k}: {o} → {v} records (−{(o - v) / o:.0%}) – probably an incomplete NAP export")
        ol = net_length(old) / 1000
        nums["old_length_km"] = round(ol, 1)
        if nums["length_km"] < ol * (1 - MAX_NET_DROP):
            err.append(f"network length {ol:.0f} → {nums['length_km']:.0f} km – probably an incomplete NAP export")
    return err, warn, nums
