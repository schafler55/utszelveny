#!/usr/bin/env python3
"""Check the texts block of index.html (id="texts"): valid JSON, every key the app asks for exists.

Usage: python3 tools/szovegek.py [web/index.html]
Exit code 1 (and a GitHub Actions error line) when the block is broken or a key is missing;
unused texts are only listed as warnings.
"""
import json
import re
import sys

path = sys.argv[1] if len(sys.argv) > 1 else "web/index.html"
html = open(path, encoding="utf-8").read()
m = re.search(r'<script type="application/json" id="texts">(.*?)</script>', html, re.S)
if not m:
    print(f"::error file={path}::no texts block (<script type=\"application/json\" id=\"texts\">)")
    sys.exit(1)
line0 = html.count("\n", 0, m.start(1)) + 1
try:
    texts = json.loads(m.group(1))
except json.JSONDecodeError as e:
    print(f"::error file={path},line={line0 + e.lineno - 1}::texts block is not valid JSON: {e.msg} (line {line0 + e.lineno - 1}, column {e.colno})")
    sys.exit(1)

errors, have = [], set()
for g, items in texts.items():
    if not isinstance(items, dict):
        errors.append(f'group "{g}" must be an object {{"key": "text", ...}}')
        continue
    for k, v in items.items():
        have.add(f"{g}.{k}")
        ok = isinstance(v, str) or (isinstance(v, list) and all(isinstance(x, str) for x in v))
        if not ok:
            errors.append(f"{g}.{k}: must be a text or a list of texts")

rest = html[:m.start()] + html[m.end():]
# keys asked for directly (markup data-tx attributes, TX("group.key"...) calls) must exist;
# any other "group.key" string that names a text counts as used (keys chosen with ?: in the code)
asked = set(re.findall(r'data-tx(?:-[a-z-]+)?="([a-z_]+\.[a-z0-9_]+)"', rest)) | set(re.findall(r'TX\(\s*"([a-z_]+\.[a-z0-9_]+)"', rest))
used = asked | (set(re.findall(r'["\']([a-z_]+\.[a-z0-9_]+)["\']', rest)) & have)
groups = set(re.findall(r'TXA?\(\s*"([a-z_]+)"', rest))
# a group whose keys the code picks at run time, TX("group." + code) (e.g. the codes of the Android side): all used
groups |= set(re.findall(r'TXA?\(\s*"([a-z_]+)\."\s*\+', rest))
for k in sorted(asked):
    if k not in have:
        errors.append(f"{k}: used by the app but missing from the texts block")
for g in sorted(groups):
    if g not in texts:
        errors.append(f'{g}: lookup group used by the app but missing from the texts block')

unused = sorted(k for k in have if k not in used and k.split(".")[0] not in groups)
for k in unused:
    print(f"::warning file={path}::text {k} is not used by the app")
for e in errors:
    print(f"::error file={path}::{e}")
n = len(have)
print(f"texts block: {n} texts in {len(texts)} groups, {len(errors)} errors, {len(unused)} unused")
sys.exit(1 if errors else 0)
