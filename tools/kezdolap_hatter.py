#!/usr/bin/env python3
"""Draws the road-network background of the landing page (site/hatter.svg).

A made-up piece of road network in the app's map style, as a tile that repeats
downwards without a seam: main roads with km markers (dot + short line to the
side, with the km number) and road number signs, a motorway, secondary and
minor roads, a railway, bridges where one road goes over another (deck +
parapet lines with flared ends, like the app's map bridge symbol) and
at-grade crossings. Solid colours blended to the page background (#E5EBE4),
so overlapping roads don't get darker.

    python3 tools/kezdolap_hatter.py            # writes site/hatter.svg
"""
import math, os, sys

W, H = 1440, 3200          # tile size; the page repeats it downwards
BG = "#E5EBE4"             # page background (light theme --bg)
ROAD = "#D2DED3"           # main road body
ROAD2 = "#D9E3D9"          # secondary / minor road body
LANE = "#EEF2ED"           # centre line
MARK = "#AFC4B2"           # km markers, bridge parapets, sign fill
LABEL = "#9FB6A3"          # km numbers
RAIL = "#C6D4C8"

def catmull(pts, step=4.0):
    """Catmull-Rom spline through pts (the first and last only steer the ends) -> dense polyline."""
    out = []
    for i in range(1, len(pts) - 2):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[i + 1], pts[i + 2]
        seg = math.dist(p1, p2)
        n = max(2, int(seg / step))
        for k in range(n):
            t = k / n
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t
                                    + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in (0, 1)))
    out.append(tuple(pts[-2]))
    return out

def d_attr(poly):
    return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in poly)

def at(poly, s):
    """Point and unit tangent at arc length s."""
    acc = 0.0
    for a, b in zip(poly, poly[1:]):
        l = math.dist(a, b)
        if acc + l >= s and l > 0:
            t = (s - acc) / l
            return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t), ((b[0] - a[0]) / l, (b[1] - a[1]) / l)
        acc += l
    a, b = poly[-2], poly[-1]
    l = math.dist(a, b)
    return b, ((b[0] - a[0]) / l, (b[1] - a[1]) / l)

def length(poly):
    return sum(math.dist(a, b) for a, b in zip(poly, poly[1:]))

def crossings(pa, pb):
    """Points where two polylines cross, with the arc length along pa."""
    res, sa = [], 0.0
    for a1, a2 in zip(pa, pa[1:]):
        la = math.dist(a1, a2)
        for b1, b2 in zip(pb, pb[1:]):
            dx1, dy1 = a2[0] - a1[0], a2[1] - a1[1]
            dx2, dy2 = b2[0] - b1[0], b2[1] - b1[1]
            den = dx1 * dy2 - dy1 * dx2
            if abs(den) < 1e-9:
                continue
            t = ((b1[0] - a1[0]) * dy2 - (b1[1] - a1[1]) * dx2) / den
            u = ((b1[0] - a1[0]) * dy1 - (b1[1] - a1[1]) * dx1) / den
            if 0 <= t < 1 and 0 <= u < 1:
                res.append(sa + t * la)
        sa += la
    return res

def vertical(x, ys_xs):
    """Control points for a road that leaves the tile at the bottom where it entered at the top (seamless)."""
    return [(x, -300), (x, -150), (x, 0), (x, 150)] + ys_xs + [(x, H - 150), (x, H), (x, H + 150), (x, H + 300)]

# ---- the network --------------------------------------------------------------------------------------------
# kind: main (with km markers), motorway, secondary, minor, rail
ROADS = {
    "A": dict(kind="main", w=20, num="42", km0=12, side=1, pts=vertical(400, [
        (470, 420), (720, 760), (690, 1150), (470, 1520), (430, 1900), (640, 2300), (560, 2700)])),
    "B": dict(kind="main", w=20, num="4", km0=164, side=-1, pts=vertical(1060, [
        (980, 520), (1150, 900), (1230, 1300), (1020, 1700), (960, 2100), (1180, 2520), (1120, 2860)])),
    "M": dict(kind="motorway", w=30, num="M0", km0=27, side=-1, pts=[
        (-300, 1580), (-100, 1580), (0, 1580), (380, 1650), (800, 1480), (1200, 1580), (1540, 1520), (1740, 1520)]),
    "C": dict(kind="secondary", w=13, num="4801", pts=[
        (-300, 640), (-100, 640), (0, 640), (300, 580), (640, 700), (900, 630), (1300, 700), (1540, 660), (1740, 660)]),
    "E": dict(kind="secondary", w=13, num="3401", pts=[
        (-300, 2400), (-100, 2400), (0, 2400), (350, 2460), (720, 2320), (1100, 2440), (1540, 2380), (1740, 2380)]),
    "R": dict(kind="rail", w=8, pts=[
        (-300, 1000), (-100, 1010), (0, 1020), (420, 1110), (900, 1280), (1540, 1230), (1740, 1220)]),
    "m1": dict(kind="minor", w=8, pts=[(640, 600), (720, 760), (930, 860), (1150, 900), (1300, 960)]),
    "m2": dict(kind="minor", w=8, pts=[(520, 1800), (430, 1900), (200, 2050), (-100, 2110), (-300, 2120)]),
    "m3": dict(kind="minor", w=8, pts=[(900, 2150), (960, 2100), (1250, 1990), (1540, 2040), (1740, 2040)]),
    "m4": dict(kind="minor", w=8, pts=[(560, 2200), (640, 2300), (820, 2640), (1120, 2860), (1300, 2960)]),
    "m5": dict(kind="minor", w=8, pts=[(1100, 600), (980, 520), (780, 360), (560, 300), (405, 200), (380, 150)]),
    "m6": dict(kind="minor", w=8, pts=[(180, 1720), (200, 1615), (150, 1300), (240, 1050), (180, 820), (300, 580), (330, 480)]),
}

def street(a, b):
    """A short straight street (settlements)."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    return dict(kind="street", w=5, pts=[(a[0] - dx * .1, a[1] - dy * .1), a, b, (b[0] + dx * .1, b[1] + dy * .1)])

# two villages: a few streets around a crossing
for i, (a, b) in enumerate([
        # around the 42 / 4801 crossing
        ((560, 560), (600, 760)), ((470, 590), (500, 780)), ((470, 700), (640, 668)),
        ((500, 780), (660, 745)), ((780, 580), (820, 780)), ((760, 790), (880, 900)),
        # around the 4 / 3401 crossing
        ((1240, 2300), (1290, 2520)), ((1330, 2290), (1360, 2470)), ((1180, 2330), (1420, 2300)),
        ((1200, 2520), (1420, 2480)), ((1000, 2330), (1080, 2560))]):
    ROADS[f"s{i}"] = street(a, b)
# (upper, lower): the upper road crosses the lower one on a bridge; every other crossing is at grade
BRIDGES = [("A", "C"), ("M", "A"), ("M", "B"), ("E", "A"), ("A", "R"), ("B", "R"), ("m6", "R")]

for r in ROADS.values():
    r["poly"] = catmull(r["pts"])

out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">']
out.append(f'<g fill="none" stroke-linecap="round" stroke-linejoin="round">')

def road(r, deck=None):
    """deck = (s0, s1): only that stretch (a bridge deck)."""
    poly = r["poly"] if deck is None else [at(r["poly"], s)[0] for s in frange(*deck, 2)]
    d = d_attr(poly)
    k, w = r["kind"], r["w"]
    if k == "rail":
        out.append(f'<path d="{d}" stroke="{RAIL}" stroke-width="2.5"/>')
        out.append(f'<path d="{d}" stroke="{RAIL}" stroke-width="{w}" stroke-dasharray="2 9" stroke-linecap="butt"/>')
        return
    body = ROAD if k in ("main", "motorway") else ROAD2
    if deck is not None:
        out.append(f'<path d="{d}" stroke="{BG}" stroke-width="{w + 14}" stroke-linecap="butt"/>')
    out.append(f'<path d="{d}" stroke="{body}" stroke-width="{w}"' + (' stroke-linecap="butt"' if deck else "") + '/>')
    if k == "motorway":   # two carriageways: a solid divider
        out.append(f'<path d="{d}" stroke="{LANE}" stroke-width="2.5"' + (' stroke-linecap="butt"' if deck else "") + '/>')
    elif k in ("main", "secondary"):
        out.append(f'<path d="{d}" stroke="{LANE}" stroke-width="1.8" stroke-dasharray="14 12" stroke-linecap="butt"/>')

def frange(a, b, step):
    n = max(1, int((b - a) / step))
    return [a + (b - a) * i / n for i in range(n + 1)]

# draw order: rail, minor, secondary, main, motorway; then the bridge decks on top
for kind in ("rail", "street", "minor", "secondary", "main", "motorway"):
    for r in ROADS.values():
        if r["kind"] == kind:
            road(r)

for up, lo in BRIDGES:
    U, L = ROADS[up], ROADS[lo]
    for s in crossings(U["poly"], L["poly"]):
        (px, py), (tx, ty) = at(U["poly"], s)
        # the deck spans the lower road plus a margin, wider when the roads cross at a sharp angle
        (_, _), (lx, ly) = at(L["poly"], [x for x in crossings(L["poly"], U["poly"]) if math.dist(at(L["poly"], x)[0], (px, py)) < 6][0])
        sin = abs(tx * ly - ty * lx) or 0.3
        half = (L["w"] / 2 + 12) / max(sin, 0.35)
        road(U, (s - half, s + half))
        nx, ny = -ty, tx
        off = U["w"] / 2 + 5
        for sg in (1, -1):
            a = (px - tx * half + nx * off * sg, py - ty * half + ny * off * sg)
            b = (px + tx * half + nx * off * sg, py + ty * half + ny * off * sg)
            fa = (a[0] - tx * 6 + nx * 6 * sg, a[1] - ty * 6 + ny * 6 * sg)
            fb = (b[0] + tx * 6 + nx * 6 * sg, b[1] + ty * 6 + ny * 6 * sg)
            out.append(f'<path d="M{fa[0]:.1f} {fa[1]:.1f} L{a[0]:.1f} {a[1]:.1f} L{b[0]:.1f} {b[1]:.1f} L{fb[0]:.1f} {fb[1]:.1f}" stroke="{MARK}" stroke-width="2.4"/>')
out.append('</g>')

# km markers: a dot and a short line to the side, with the km number (main roads and the motorway)
out.append(f'<g font-family="Roboto, Arial, sans-serif" font-weight="700" font-size="13" fill="{LABEL}">')
for r in ROADS.values():
    if "km0" not in r:
        continue
    poly, L = r["poly"], length(r["poly"])
    every = 190
    s, km = 90.0, r["km0"]
    while s < L - 40:
        (px, py), (tx, ty) = at(poly, s)
        if -10 < px < W + 10 and 30 < py < H - 30:
            nx, ny = -ty * r["side"], tx * r["side"]
            a = r["w"] / 2 + 3
            b = a + 11
            out.append(f'<path d="M{px + nx * a:.1f} {py + ny * a:.1f} L{px + nx * b:.1f} {py + ny * b:.1f}" stroke="{MARK}" stroke-width="2" fill="none"/>')
            out.append(f'<circle cx="{px + nx * b:.1f}" cy="{py + ny * b:.1f}" r="3.2" fill="{MARK}"/>')
            lx, ly = px + nx * (b + 9), py + ny * (b + 9) + 4.5
            anchor = "start" if nx > 0.3 else "end" if nx < -0.3 else "middle"
            if anchor == "middle":
                ly += 6 if ny > 0 else -4
            out.append(f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="{anchor}">{km}</text>')
        s += every
        km += 1
out.append('</g>')

# road number signs on the roads: shield for main roads / motorway, plate for secondary roads
out.append('<g font-family="Roboto, Arial, sans-serif" font-weight="700" text-anchor="middle">')
for r in ROADS.values():
    if "num" not in r:
        continue
    poly, L = r["poly"], length(r["poly"])
    for s in frange(L * 0.22, L * 0.78, L * 0.28):
        (px, py), _ = at(poly, s)
        if not (40 < px < W - 40 and 60 < py < H - 60):
            continue
        if r["kind"] == "secondary":
            w = 12 + 8 * len(r["num"])
            out.append(f'<rect x="{px - w / 2:.1f}" y="{py - 10:.1f}" width="{w}" height="20" rx="4" fill="{BG}" stroke="{MARK}" stroke-width="2"/>')
            out.append(f'<text x="{px:.1f}" y="{py + 4.5:.1f}" font-size="13" fill="{LABEL}">{r["num"]}</text>')
        else:
            w = 30 if len(r["num"]) < 3 else 38
            h = 26
            x0, y0 = px - w / 2, py - h / 2
            out.append(f'<path d="M{x0:.1f} {y0:.1f} h{w} v{h * 0.62:.1f} l{-w / 2:.1f} {h * 0.38:.1f} l{-w / 2:.1f} {-h * 0.38:.1f} z" fill="{MARK}" stroke="{BG}" stroke-width="2.5" stroke-linejoin="round"/>')
            out.append(f'<text x="{px:.1f}" y="{py + 2:.1f}" font-size="14" fill="{BG}">{r["num"]}</text>')
out.append('</g></svg>')

dst = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "site", "hatter.svg")
if len(sys.argv) > 1:
    dst = sys.argv[1]
os.makedirs(os.path.dirname(dst), exist_ok=True)
with open(dst, "w") as f:
    f.write("\n".join(out) + "\n")
print(f"{dst}: {os.path.getsize(dst) // 1024} KB")
