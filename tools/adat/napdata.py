"""Reading and checking the downloaded NAP WFS GeoJSON files (gate 1–3 of the data pipeline)."""
import hashlib, json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
FID = re.compile(r'"id"\s*:\s*"wfs_(\d+)\.([A-Za-z0-9_]+)\.fid')


class DataError(Exception):
    """A check failed: the data must not be used."""


def manifest():
    with open(os.path.join(HERE, "layers.json"), encoding="utf-8") as f:
        return json.load(f)


def identify(path):
    """(wfs number, layer name) from the first feature id of a downloaded WFS GeoJSON file"""
    with open(path, encoding="utf-8", errors="replace") as f:
        head = f.read(65536)
    m = FID.search(head)
    return (m.group(1), m.group(2)) if m else (None, None)


def find_layers(folder):
    """{key: path} for every layer of layers.json found in the folder (any file names)"""
    M = manifest()["layers"]
    by_layer = {v["layer"]: k for k, v in M.items()}
    found = {}
    for fn in sorted(os.listdir(folder)):
        if not fn.lower().endswith((".json", ".geojson")):
            continue
        p = os.path.join(folder, fn)
        n, layer = identify(p)
        k = by_layer.get(layer)
        if k:
            if k in found:
                raise DataError(f"{M[k]['name']}: two files in {folder} ({os.path.basename(found[k])}, {fn})")
            found[k] = p
    missing = [M[k]["name"] for k in M if k not in found]
    if missing:
        raise DataError("missing NAP files: " + ", ".join(missing))
    return found


def _rnd(c):
    return [_rnd(x) for x in c] if isinstance(c, list) else round(c, 2)


def fingerprint(feats):
    """content hash that ignores what changes on every download (feature id strings, timeStamp):
    properties + geometry rounded to 1 cm, features sorted"""
    rows = sorted(json.dumps([f.get("properties"), (f.get("geometry") or {}).get("type"),
                              _rnd((f.get("geometry") or {}).get("coordinates") or [])],
                             sort_keys=True, ensure_ascii=False, separators=(",", ":")) for f in feats)
    return hashlib.sha256("\n".join(rows).encode("utf-8")).hexdigest()[:16]


def load_layer(key, path):
    """features of one layer after the file checks (gate 1–2); returns (features, info)"""
    spec = manifest()["layers"][key]
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    if d.get("type") != "FeatureCollection" or not isinstance(d.get("features"), list):
        raise DataError(f"{spec['name']}: not a GeoJSON FeatureCollection")
    feats = d["features"]
    n = len(feats)
    for fld in ("numberMatched", "numberReturned", "totalFeatures"):
        v = d.get(fld)
        if isinstance(v, int) and v != n:
            raise DataError(f"{spec['name']}: incomplete download – {fld} {v}, features {n}")
    if n == 0:
        raise DataError(f"{spec['name']}: no features")
    crs = ((d.get("crs") or {}).get("properties") or {}).get("name", "")
    if crs and not crs.endswith("23700"):
        raise DataError(f"{spec['name']}: not EOV coordinates ({crs})")
    fields = set()
    for x in feats:
        fields.update((x.get("properties") or {}).keys())
    miss = [f for f in spec["fields"] if f not in fields]
    if miss:
        raise DataError(f"{spec['name']}: missing field(s) {', '.join(miss)}")
    known = set(spec["fields"]) | set(spec.get("optional", [])) | {"id"}
    extra = sorted(f for f in fields if f not in known)
    g = spec["geom"]
    bad = sum(1 for x in feats if (x.get("geometry") or {}).get("type") not in (g, None))
    if bad:
        raise DataError(f"{spec['name']}: {bad} features are not {g}")
    m = re.match(r"wfs_(\d+)\.", str(feats[0].get("id", "")))
    info = {"name": spec["name"], "features": n, "fields": sorted(fields), "new_fields": extra,
            "wfs": m.group(1) if m else None, "sha": fingerprint(feats), "timeStamp": d.get("timeStamp")}
    return feats, info
