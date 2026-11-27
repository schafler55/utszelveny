# Road data build (`tools/adat/`)

Builds the whole embedded road data of the app – the `<script type="application/json" id="roaddata">` block of
`web/index.html` – from the NAP (Nemzeti Adathozzáférési Pont) WFS downloads, in one step. Nothing else in
`index.html` changes.

```
python3 tools/adat/build.py <folder with the 13 NAP .json files> [web/index.html]   # build + checks
python3 tools/adat/compare.py <old index.html> <new index.html>                    # change report (Markdown)
python3 tools/adat/apptest.py <old index.html> <new index.html>                    # app-level test in headless Chrome
```

`build.py`, `compare.py` and `check.py` need only the Python 3 standard library. `apptest.py` needs
`pip install playwright` and Chrome. `osm/telepulesek_keszit.py` needs `pip install shapely`.

## Rules

* **All tables are rebuilt together.** Every table points to roads by their position in `roads`; a partial
  update after the network changed would attach data to the wrong roads. (This is why the three old importers –
  `nap_szakaszadatok.py`, `nap_azonositopontok.py`, `nap_egyiranyu_megallok.py` – were folded in here.)
* **Deterministic.** The WFS returns features in a different order on every download, so everything is sorted;
  the same data gives a byte-identical `index.html` (checked: the files uploaded on 2026-11-24 and a fresh
  download of the same day give the same file).
* **Fail closed.** A missing layer or field, an unknown code or road number, an incomplete download
  (`numberMatched` ≠ features), points outside Hungary, km anchors out of order, or a table losing more than 10 %
  of its records (the network more than 1 % of its length) compared with the data in `index.html` stops the
  build and leaves `index.html` unchanged (`--force` overrides the comparison checks).
* **Files are recognised by content.** Each feature id starts with `wfs_<number>.<layer>.`; `layers.json`
  maps the layer names to the tables, so the file names don't matter.
* **What the data was built from** goes into `roaddata.meta`: the download date (newest WFS `timeStamp`, or
  `--date`), and per layer the feature count and a content hash (properties + geometry rounded to 1 cm; the
  feature ids and `timeStamp` that change on every download are left out). Névjegy shows the date
  (`about.data_source`, `{date}`).

## Layers → tables

| NAP layer (`layers.json` key) | Tables |
|---|---|
| Országos közúthálózat (`halozat`) | `roads` (numbers), `segs`, `lab` |
| Szelvényjelek (`kmjel`) | km anchors in `segs` |
| Közút neve, kategóriája és kezelője (`kutka`) | road names in `roads`, `kez`, `mrn` |
| Lakott területi szakaszok (`szakjel`) | `szk`; with `osm/telepulesek.json` → `tel`, `tnev` |
| Sebességkorlátozás (`sebkorl`) | `spd`, `str` |
| Hídhasználati feltételek (`hid`) | `br`, `str` |
| Tehergépjárművekre vonatkozó korlátozások (`teher`) | `tr`, `str` |
| Összes gépjármű forgalmi sávok száma (`sav`) | `sav` |
| Burkolat típusa, szélessége (`burkolat`) | `bur`, `burt` |
| Éves keresztmetszeti forgalmi adatok (`forgalom`) | `anf`, `ksz`, `anfEv` |
| Közúti azonosító pontok (`csp`) | `csp`, `cspk` |
| Egyirányú útpályák (`irany`) | `egy` |
| Autóbusz megállóhelyek (`megallo`) | `bm`, `bmn`, `bmt` |

## How the tables are made

* **roads:** every road number of the network, sorted (M roads first, then by number); the name from `kutka`.
* **segs** – one per network feature, sorted by road, carriageway, chainage:
  `[road, pk, kut, county, kezelő, label, scale, anchors, points, polyline, mrn]`.
  Geometry: Douglas–Peucker 1 m (distance to the segment, as GEOS), rounded to EOV metres, polyline-encoded.
  County: digits 2–3 of `kkod` (of `vkod` when `kkod` has 00). Label: `szak_label` where `szak_tipus` = 2.
  Scale: NAP length (`szho`) / drawn length (1 when the ratio is outside 0.25–4: placeholder lengths).
  Anchors `[along, km, m]`: segment start and end, and every whole km in between – the km post projected on
  the segment (≤ 50 m away); a missing post is interpolated evenly between the nearest known km points of the
  segment (its posts and the segment start's km, measured back with the scale) when they are ≥ 800 m apart per
  km – closer than that the chainage skips km numbers there and no anchor is made; with no known point after
  it, measured from the start with the scale.
* **kez, mrn** – the operator and its units, from `kutka` (since 2026-11 with `pkod`, `kszelv`, `vszelv`, `zkod`,
  `uzemm`, `mernokseg`). The layer lists the network's segments again: joined by `id`; the build stops when the
  ids, or a row's road / carriageway / chainage, differ from the network (a join by chainage would be needed then).
  `mrn` rows are `[county code of the county directorate, mérnökség name, …]`, row 0 = nothing known; a segment
  points to its row. `zkod` 020–200 are Magyar Közút's county directorates (megyei igazgatóság) – the value in
  `layers.json` is the KSH county code, the app writes the name from it (`common.directorate_name`); the
  concession companies' codes (010, 220, 240, 250, 260) give 0 = no directorate. An unknown `zkod` stops the
  build. A segment shared by two mérnökségek is listed twice in the layer, once with each (9 segments in
  2026-11; the data does not say where the line between them is): its row has both names. A segment listed with
  two operators or two directorates stops the build.
* **spd, szk, sav, bur, anf, egy:** ranges per road and carriageway; touching pieces with the same value merged.
* **br:** one record per NAP bridge; limits for the road *under* the bridge (height, rigid gate, width – codes
  4, 5, 9) are taken off the bridge; when the bridge name names that road and it passes within 50 m, a record
  is made on it (`der`, `upper`). A structure over a divided road is recorded on one carriageway in the NAP
  data – it is copied to the other one (projected chainage).
* **tr:** the NAP restriction codes 21–28 become the app's 1–8; records without a code are skipped.
* **tel, tnev:** each built-up (átkelési) section is sampled every 10 m against the settlement polygons;
  town lines are found to ~0.5 m; pieces shorter than 30 m (100 m at the ends of a section, where the NAP
  section runs a little past the town line) go to the neighbouring name.

## Settlement polygons (`osm/`)

`osm/telepulesek.json` (OpenStreetMap, ODbL – credited in Névjegy) is kept in the repo and refreshed by hand
about once a year with `osm/telepulesek_keszit.py` (geometry: geoBoundaries HUN ADM3, names: geoHungary; see
the script's header for the download links).

## Baseline (2026-11-24)

The first build was compared with the data on main 7abf89f, which had been made by hand in chat sessions:
roads, speed limits, built-up sections, lanes, pavement, traffic, one-way, truck limits, identification points
and bus stops are identical; of 22,341 segments 15 have one different vertex (and so a slightly different
scale) and 26 have km anchors moved – mostly bike path 95001 without km posts, up to 43 m (the old rule for
missing posts could not be fully reconstructed); 14 copied over-bridges are 1 m off; town names agree on
99.86 % of the length (8,231 → 8,266 ranges; a few town lines move by metres). In the app (`apptest.py`): 5,000 places – no difference; 20,000
places – 2 km+m differences (9 m and 3 m) and 1 town name. Golden points (`golden.json`) were refreshed from
this build; the one that moved is the 95001 bike path (103+100 → 103+084).
