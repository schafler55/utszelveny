#!/usr/bin/env python3
"""Version number of ÚtSzelvény: check that every place agrees, or set a new version everywhere at once.

    python3 tools/verzio.py              # check (CI runs this on every push)
    python3 tools/verzio.py --tag V1.4.0 # check, and that the release tag is the same version (CI, stable releases)
    python3 tools/verzio.py 1.3.0.1      # set 1.3.0.1 everywhere (versionCode 1030001), then check

Places: web/index.html (page title, header label, Névjegy line with the versionCode, APP_VER used by the update
check and the photo EXIF), web/sw.js (cache name, read by the web app's update check),
android/app/build.gradle (versionName, versionCode) and the version line of README.md. The Android user agent
takes the app's own versionName.
versionCode: two digits per version part, four parts (1.3.0.1 → 1030001, 1.4.0 → 1040000), so every part must
stay below 100. Up to V1.3.0 it was one digit per part (1.3.0 → 1300); the new codes are all higher.

The owner's rule (2026-11-26), see also CHANGELOG.md:
  - every change gets its own version, so every downloaded app can be identified: the fourth part goes up
    (1.3.0.1, 1.3.0.2 …);
  - the third part goes up only when the owner says so (1.3.1.0, then 1.3.1.1 …);
  - a stable release raises the second part and has three parts (1.4.0, then 1.4.0.1 …).
"""
import os
import re
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
VER = r"(\d+(?:\.\d+){1,3})"
# file, label, pattern with one group for the version (versionCode: the code)
PLACES = [
    ("web/index.html", "page title", r"<title>ÚtSzelvény V" + VER + r"</title>"),
    ("web/index.html", "header label", r'id="verTag">V' + VER + r"<"),
    ("web/index.html", "Névjegy line", r'class="about-t">ÚtSzelvény V' + VER + r" \(\d+\)<"),
    ("web/index.html", "Névjegy versionCode", r'class="about-t">ÚtSzelvény V[\d.]+ \((\d+)\)<'),
    ("web/index.html", "APP_VER", r'const APP_VER="UtSzelveny V' + VER + r'";'),
    ("web/sw.js", "service worker cache", r'const C="utszelveny-v' + VER + r'";'),
    ("android/app/build.gradle", "versionName", r'versionName "' + VER + r'"'),
    ("android/app/build.gradle", "versionCode", r"versionCode (\d+)"),
    ("README.md", "README version line", r"\*\*Verzió:\*\* V" + VER + r" "),
]
GH = os.environ.get("GITHUB_ACTIONS") == "true"


def read(path):
    return open(os.path.join(ROOT, path), encoding="utf-8", newline="").read()


def code_of(v):
    """1.3.0.1 → 1030001: two digits per part, four parts."""
    parts = [int(x) for x in v.split(".")]
    return int("".join(f"{x:02d}" for x in (parts + [0, 0, 0])[:4]))


def find_all():
    found = []
    for path, label, pat in PLACES:
        m = re.findall(pat, read(path))
        found.append((path, label, m[0] if len(m) == 1 else None, len(m)))
    return found


def check(tag=None):
    errors, warnings = [], []
    found = find_all()
    for path, label, val, n in found:
        if n != 1:
            errors.append(f"{path}: {label} found {n} times (expected once)")
    vers = {val for path, label, val, n in found if val and "versionCode" not in label}
    codes = {val for path, label, val, n in found if val and "versionCode" in label}
    if len(vers) > 1:
        errors.append("the version differs: " + ", ".join(f"{label} {val}" for path, label, val, n in found
                                                          if val and "versionCode" not in label))
    v = sorted(vers)[0] if vers else None
    if v:
        parts = [int(x) for x in v.split(".")]
        if any(x > 99 for x in parts):
            errors.append(f"version {v}: every part must stay below 100 (versionCode is two digits per part)")
        elif any(x >= 90 for x in parts):
            warnings.append(f"version {v}: a part is approaching 100, where the two-digits-per-part versionCode breaks")
        want = str(code_of(v))
        for c in codes:
            if c != want:
                errors.append(f"versionCode {c} does not match version {v} (should be {want})")
        if tag is not None and tag.lstrip("vV") != v:
            errors.append(f"the release tag {tag} is not the app's version V{v}: set it with tools/verzio.py first")
    for w in warnings:
        print(f"::warning::{w}" if GH else f"warning: {w}")
    for e in errors:
        print(f"::error::{e}" if GH else f"error: {e}")
    print(f"version {v or '?'} (versionCode {', '.join(sorted(codes)) or '?'}) – {len(errors)} error(s)")
    return not errors


def set_version(v):
    if not re.fullmatch(r"\d{1,2}(\.\d{1,2}){2,3}", v):
        sys.exit(f"{v}: use four parts (1.3.0.1), or three for a stable release (1.4.0); every part 0–99")
    code = str(code_of(v))
    files = {}
    for path, label, pat in PLACES:
        s = files.get(path) or read(path)
        new = code if "versionCode" in label else v
        s, n = re.subn(pat, lambda m: m.group(0)[:m.start(1) - m.start(0)] + new + m.group(0)[m.end(1) - m.start(0):], s)
        if n != 1:
            sys.exit(f"{path}: {label} found {n} times – nothing written")
        files[path] = s
    for path, s in files.items():
        open(os.path.join(ROOT, path), "w", encoding="utf-8", newline="").write(s)
        print("written:", path)


def main():
    a = sys.argv[1:]
    tag = None
    if a and a[0] == "--tag":
        tag = a[1] if len(a) > 1 else ""
        a = a[2:]
    if a:
        set_version(a[0].lstrip("vV"))
    sys.exit(0 if check(tag) else 1)


if __name__ == "__main__":
    main()
