#!/usr/bin/env python3
"""App-level check of a road data build (gate 6–7 of the data pipeline), in headless Chrome.

Opens two index.html files (old = main, new = the build), and asks the real app code the same questions:
  * golden points (tools/adat/golden.json): fixed places with the road + km+m they must give (± 5 m);
  * a regression sample: N random places along the old network (fixed seed) – road, carriageway, km+m (± 2 m),
    speed limit, built-up / town name, operator, county directorate + mérnökség, lanes, pavement, traffic, one-way,
    bridges and truck limits nearby.
Prints a Markdown report; exit code 1 when the new page does not load or a golden point fails.

Usage:  python3 tools/adat/apptest.py <old index.html> <new index.html> [--n 5000] [--seed 1] [--chrome PATH]
        python3 tools/adat/apptest.py --make-golden <index.html>   (writes golden.json from that build)
Needs: pip install playwright (and Google Chrome or `playwright install chromium`).
"""
import argparse, json, os, pathlib, sys

HERE = os.path.dirname(os.path.abspath(__file__))
GOLDEN = os.path.join(HERE, "golden.json")

# the app's own functions, called inside the page
PROBE = r"""
(args) => {
  const [pts, withAttrs] = args;
  const out = [];
  for (const [E, N] of pts) {
    lastMatch = null; forcedRoad = null;
    const res = match(E, N, {acc: 5});
    if (res.off) { out.push(null); continue; }
    const s = res.best.s, r = segRoad[s], pk = segPk[s], v = cval(res.ch);
    const o = {road: ROADS[r].num, pk, ch: fmtCh(res.ch), v, d: Math.round(res.best.d * 10) / 10};
    if (withAttrs) {
      const sp = speedAt(r, pk, segKut[s], v, 0);
      o.spd = [sp.lim, sp.own, sp.bu, (sp.cond || []).map(x => x.lim + " " + x.kieg).join(";")];
      o.tel = telAt(r, pk, v);
      o.kez = KEZ[segKez[s]];
      o.mrn = typeof mernoksegOf === "function" ? [igazgatosagOf(s), ...mernoksegOf(s)] : null;   // null: a page from before V1.3.2.0
      o.cty = segCty[s];
      o.sav = lanesAt(r, pk, v);
      o.bur = pavementAt(r, pk, v);
      o.anf = trafficAt(r, pk, v);
      o.egy = onewayAt(r, pk, v);
      o.br = bridgesNear(r, pk, v, 0).filter(x => Math.abs(x.raw) <= 50).map(x => x.b.name + "|" + x.b.rs.join(",")).sort();
      o.tr = trucksNear(r, pk, v, 0).filter(x => x.active).map(x => x.x.sig).sort();
    }
    out.push(o);
  }
  return out;
}
"""

SAMPLE = r"""
([n, seed]) => {
  // places along the network: a random segment (weighted by length), a random point on it, 3 m to the side
  let x = seed >>> 0;
  const rnd = () => { x ^= x << 13; x >>>= 0; x ^= x >>> 17; x ^= x << 5; x >>>= 0; return x / 4294967296; };
  const len = [], acc = [];
  let tot = 0;
  for (let s = 0; s < NSEG; s++) { const L = segLen(s); tot += L; acc.push(tot); }
  const pts = [];
  while (pts.length < n) {
    const t = rnd() * tot;
    let lo = 0, hi = NSEG - 1;
    while (lo < hi) { const m = (lo + hi) >> 1; if (acc[m] < t) lo = m + 1; else hi = m; }
    const s = lo, L = segLen(s);
    if (L < 20) continue;
    const a = 5 + rnd() * (L - 10), p = pointAt(s, a), q = pointAt(s, Math.min(L, a + 1));
    const dx = q.E - p.E, dy = q.N - p.N, l = Math.hypot(dx, dy) || 1, side = rnd() < 0.5 ? 3 : -3;
    pts.push([Math.round((p.E - dy / l * side) * 10) / 10, Math.round((p.N + dx / l * side) * 10) / 10]);
  }
  return pts;
}
"""


def open_page(browser, path):
    pg = browser.new_page(bypass_csp=True)      # the page's CSP has no 'unsafe-eval', which wait_for_function needs
    errors = []
    pg.on("pageerror", lambda e: errors.append(str(e)))
    pg.goto(pathlib.Path(path).resolve().as_uri())
    pg.wait_for_function("typeof NSEG !== 'undefined' && NSEG > 0", timeout=60000)
    pg.wait_for_timeout(3500)          # bridge crossings are worked out 2.5 s after the start
    return pg, errors


def same_ch(a, b, tol):
    if a is None or b is None:
        return a is b
    return a["road"] == b["road"] and a["pk"] == b["pk"] and abs(vd(a["v"], b["v"])) <= tol


def vd(a, b):
    return (b // 10000 - a // 10000) * 1000 + (b % 10000 - a % 10000)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("old", nargs="?")
    ap.add_argument("new", nargs="?")
    ap.add_argument("--n", type=int, default=5000)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--chrome", default="/usr/bin/google-chrome" if os.path.exists("/usr/bin/google-chrome") else None)
    ap.add_argument("--make-golden")
    a = ap.parse_args()
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=a.chrome) if a.chrome else p.chromium.launch()
        if a.make_golden:
            G = json.load(open(GOLDEN, encoding="utf-8"))
            pg, err = open_page(browser, a.make_golden)
            res = pg.evaluate(PROBE, [[g["eov"] for g in G["points"]], False])
            for g, r in zip(G["points"], res):
                g["expect"] = None if r is None else {k: r[k] for k in ("road", "pk", "ch")}
            json.dump(G, open(GOLDEN, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
            print(f"golden.json: {len(G['points'])} points written from {a.make_golden}")
            return
        old, eo = open_page(browser, a.old)
        new, en = open_page(browser, a.new)
        rep, fail = [], False
        if en:
            rep.append("**The new page has JavaScript errors:** " + "; ".join(en[:5]))
            fail = True
        G = json.load(open(GOLDEN, encoding="utf-8"))["points"]
        res = new.evaluate(PROBE, [[g["eov"] for g in G], False])
        rep += ["### Golden points", "| Place | Expected | New build | |", "|---|---|---|---|"]
        for g, r in zip(G, res):
            e = g.get("expect")
            ok = same_ch(r, dict(e, v=int(e["ch"].split("+")[0]) * 10000 + int(e["ch"].split("+")[1])) if e else None, 5)
            fail |= not ok
            show = lambda x: "off the network" if x is None else f"{x['road']} {x['ch']}" + (f" ({'JOBB' if x['pk'] == 1 else 'BAL'})" if x["pk"] else "")
            rep.append(f"| {g['name']} | {show(e)} | {show(r)} | {'✓' if ok else '✗'} |")
        pts = old.evaluate(SAMPLE, [a.n, a.seed])
        ro = old.evaluate(PROBE, [pts, True])
        rn = new.evaluate(PROBE, [pts, True])
        cnt = {k: 0 for k in ("place", "spd", "tel", "kez", "mrn", "cty", "sav", "bur", "anf", "egy", "br", "tr")}
        no_mrn = 0
        ex = {k: [] for k in cnt}
        for P, x, y in zip(pts, ro, rn):
            if not same_ch(x, y, 2):
                cnt["place"] += 1
                if len(ex["place"]) < 8:
                    ex["place"].append(f"EOV {P[0]:.0f} {P[1]:.0f}: {x and (x['road'], x['pk'], x['ch'])} → {y and (y['road'], y['pk'], y['ch'])}")
                continue
            if x is None:
                continue
            for k in cnt:
                if k == "mrn" and (x[k] is None or y[k] is None):      # one of the pages has no such data: nothing to compare
                    no_mrn += 1
                    continue
                if k != "place" and json.dumps(x[k], sort_keys=True, ensure_ascii=False) != json.dumps(y[k], sort_keys=True, ensure_ascii=False):
                    cnt[k] += 1
                    if len(ex[k]) < 5:
                        ex[k].append(f"{x['road']} {x['ch']}: `{json.dumps(x[k], ensure_ascii=False)}` → `{json.dumps(y[k], ensure_ascii=False)}`")
        rep += ["", f"### Regression sample: {len(pts):,} places along the network (seed {a.seed})".replace(",", "."),
                "| Check | Different |", "|---|---:|"]
        names = {"place": "road / carriageway / km+m (± 2 m)", "spd": "speed limit", "tel": "town name", "kez": "operator",
                 "mrn": "county directorate / mérnökség", "cty": "county", "sav": "lanes", "bur": "pavement",
                 "anf": "traffic", "egy": "one-way", "br": "bridges within 50 m", "tr": "truck limits in force"}
        for k, n in cnt.items():
            rep.append(f"| {names[k]} | {'not in the old page' if k == 'mrn' and no_mrn else n} |")
        for k, L in ex.items():
            if L:
                rep.append(f"- {names[k]}: " + "; ".join(L))
        browser.close()
    print("\n".join(rep))
    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()
