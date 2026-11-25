#!/usr/bin/env python3
"""Makes tools/adat/osm/telepulesek.json, the settlement polygons for the town names on built-up sections.
Run by hand about once a year (OpenStreetMap boundaries change rarely); needs `pip install shapely`.

Geometry: geoBoundaries HUN ADM3 (OpenStreetMap, admin_level 8), whose names are broken (encoding), so each
polygon takes the name of the geoHungary settlement (OpenStreetMap too) it overlaps most (> 50 %).
  https://media.githubusercontent.com/media/wmgeolab/geoBoundaries/main/releaseData/gbOpen/HUN/ADM3/geoBoundaries-HUN-ADM3.geojson
  https://github.com/wuerdo/geoHungary  (settlements.geojson)
Usage: python3 telepulesek_keszit.py geoBoundaries-HUN-ADM3.geojson settlements.geojson telepulesek.json [date]
"""
import datetime, json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from shapely.geometry import shape
from shapely.strtree import STRtree
import geo


def eov_poly(rings):
    out = []
    for ring in rings:
        q = []
        for lon, lat in ring:
            e, n = geo.wgs_to_eov(lat, lon)
            p = (round(e), round(n))
            if not q or q[-1] != p:
                q.append(p)
        out.append(q)
    return out


def main():
    gb, hu, dst = sys.argv[1:4]
    date = sys.argv[4] if len(sys.argv) > 4 else datetime.date.today().isoformat()
    G = json.load(open(gb, encoding="utf-8"))["features"]
    H = json.load(open(hu, encoding="utf-8"))["features"]
    hs = [shape(f["geometry"]).buffer(0) for f in H]
    hn = [f["properties"]["NAME"] for f in H]
    tree = STRtree(hs)
    polys, names, lost = [], set(), 0
    for f in G:
        g = shape(f["geometry"]).buffer(0)
        best, ba = None, 0.0
        for k in tree.query(g):
            a = g.intersection(hs[k]).area
            if a > ba:
                best, ba = k, a
        if best is None or ba < 0.5 * g.area:
            lost += 1
            continue
        parts = list(g.geoms) if g.geom_type == "MultiPolygon" else [g]
        for p in parts:
            polys.append((hn[best], eov_poly([list(p.exterior.coords)] + [list(r.coords) for r in p.interiors])))
            names.add(hn[best])
    names = sorted(names)
    ix = {n: i for i, n in enumerate(names)}
    rows = sorted([[ix[n]] + [geo.encode(r) for r in rings] for n, rings in polys])
    out = {"source": "OpenStreetMap administrative boundaries (admin_level 8): geometry geoBoundaries HUN ADM3, "
                     "names geoHungary settlements.geojson",
           "license": "© OpenStreetMap contributors, ODbL 1.0", "downloaded": date,
           "crs": "EPSG:23700 (EOV metres, the app's formulas)", "names": names, "polys": rows}
    s = json.dumps(out, ensure_ascii=False, separators=(",", ":"))
    open(dst, "w", encoding="utf-8").write(s)
    print(f"{len(G)} polygons, {len(names)} names, {lost} without a name (> 50 % overlap), {len(s) / 1e6:.2f} MB")


if __name__ == "__main__":
    main()
