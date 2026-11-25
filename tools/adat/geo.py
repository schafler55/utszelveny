"""Geometry helpers for the ÚtSzelvény data build (EOV metres, pure Python)."""
import math

# ---------- chainage values ----------
def cval(s):
    """NAP chainage text "12 + 345" -> km*10000 + m (m may be >= 1000 in the NAP data)"""
    a, b = str(s).split("+")
    return int(a) * 10000 + int(b)

def vdist(a, b):
    """≈ metres from chainage value a to b (same formula as the app)"""
    return (b // 10000 - a // 10000) * 1000 + (b % 10000 - a % 10000)

# ---------- polylines ----------
def plen(pts):
    return sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:]))

def _segd(px, py, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy
    if L2 == 0:
        return math.hypot(px - ax, py - ay)
    t = ((px - ax) * dx + (py - ay) * dy) / L2
    if t <= 0:
        return math.hypot(px - ax, py - ay)
    if t >= 1:
        return math.hypot(px - bx, py - by)
    return abs(dx * (py - ay) - dy * (px - ax)) / math.sqrt(L2)

def simplify(pts, tol):
    """Douglas–Peucker with distance to the segment (same result as GEOS / shapely simplify, preserve_topology=False)"""
    n = len(pts)
    if n < 3:
        return pts[:]
    keep = [False] * n
    keep[0] = keep[-1] = True
    st = [(0, n - 1)]
    while st:
        a, b = st.pop()
        if b <= a + 1:
            continue
        ax, ay = pts[a]
        bx, by = pts[b]
        best, bi = -1.0, a
        for i in range(a + 1, b):
            d = _segd(pts[i][0], pts[i][1], ax, ay, bx, by)
            if d > best:
                best, bi = d, i
        if best <= tol:
            continue
        keep[bi] = True
        st.append((bi, b))
        st.append((a, bi))
    return [p for p, k in zip(pts, keep) if k]

def project(pts, x, y):
    """nearest point of the polyline -> (distance, along)"""
    best = (1e18, 0.0)
    acc = 0.0
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        dx, dy = bx - ax, by - ay
        L2 = dx * dx + dy * dy
        L = math.sqrt(L2)
        t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((x - ax) * dx + (y - ay) * dy) / L2))
        d = math.hypot(x - (ax + t * dx), y - (ay + t * dy))
        if d < best[0]:
            best = (d, acc + t * L)
        acc += L
    return best

def point_at(pts, along):
    acc = 0.0
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        L = math.hypot(bx - ax, by - ay)
        if L > 0 and acc + L >= along:
            t = (along - acc) / L
            return (ax + t * (bx - ax), ay + t * (by - ay))
        acc += L
    return pts[-1]

# ---------- polyline text encoding (as decoded by the app's loadData) ----------
def encode(pts):
    o = []
    pe = pn = 0
    for e, n in pts:
        for v in (e - pe, n - pn):
            v = ~(v << 1) if v < 0 else v << 1
            while v >= 0x20:
                o.append(chr((0x20 | (v & 0x1F)) + 63))
                v >>= 5
            o.append(chr(v + 63))
        pe, pn = e, n
    return "".join(o)

def decode(s):
    out = []
    p = e = n = 0
    L = len(s)
    while p < L:
        vals = []
        for _ in range(2):
            r = sh = 0
            while True:
                b = ord(s[p]) - 63
                p += 1
                r |= (b & 31) << sh
                sh += 5
                if b < 32:
                    break
            vals.append(~(r >> 1) if r & 1 else r >> 1)
        e += vals[0]
        n += vals[1]
        out.append((e, n))
    return out

# ---------- chainage along a segment (same as the app's chainage()) ----------
def chainage(an, scale, along):
    n = len(an) // 3
    i = 0
    while i < n - 2 and along >= an[(i + 1) * 3] - 0.3:
        i += 1
    sA, kA, mA, sB, kB, mB = an[i * 3:i * 3 + 6]
    if kB == kA:
        m = mA + (along - sA) / (sB - sA) * (mB - mA) if sB > sA else mA
    else:
        m = mA + (along - sA) * scale
    return kA * 10000 + max(0, int(math.floor(m + 0.5)))

def along_at(an, scale, L, v):
    """position along a segment where the chainage reaches v (bisection, like the app's alongAt)"""
    if v <= chainage(an, scale, 0):
        return 0.0
    if v >= chainage(an, scale, L):
        return L
    a, b = 0.0, L
    for _ in range(40):
        m = (a + b) / 2
        if chainage(an, scale, m) < v:
            a = m
        else:
            b = m
    return b

# ---------- WGS84 -> EOV (EPSG:23700), same formulas as the app (HD72 3-parameter shift) ----------
_rad = math.pi / 180
_aW, _fW = 6378137.0, 1 / 298.257223563
_e2W = 2 * _fW - _fW * _fW
_a, _f = 6378160.0, 1 / 298.247167427
_e2 = 2 * _f - _f * _f
_e = math.sqrt(_e2)
_T = (52.17, -71.82, -14.9)
_lat0 = (47 + 8 / 60 + 39.8174 / 3600) * _rad
_lon0 = (19 + 2 / 60 + 54.8584 / 3600) * _rad
_k0, _x0, _y0 = 0.99993, 650000.0, 200000.0
_sin0 = math.sin(_lat0)
_R = _k0 * _a * math.sqrt(1 - _e2) / (1 - _e2 * _sin0 * _sin0)
_alpha = math.sqrt(1 + _e2 / (1 - _e2) * math.cos(_lat0) ** 4)
_b0 = math.asin(_sin0 / _alpha)
_K = (math.log(math.tan(math.pi / 4 + _b0 / 2)) - _alpha * math.log(math.tan(math.pi / 4 + _lat0 / 2))
      + _alpha * _e / 2 * math.log((1 + _e * _sin0) / (1 - _e * _sin0)))

def _toxyz(lat, lon, A, E2):
    N = A / math.sqrt(1 - E2 * math.sin(lat) ** 2)
    return (N * math.cos(lat) * math.cos(lon), N * math.cos(lat) * math.sin(lon), N * (1 - E2) * math.sin(lat))

def _fromxyz(X, Y, Z, A, E2):
    p = math.hypot(X, Y)
    lat = math.atan2(Z, p * (1 - E2))
    for _ in range(6):
        N = A / math.sqrt(1 - E2 * math.sin(lat) ** 2)
        lat = math.atan2(Z + E2 * N * math.sin(lat), p)
    return lat, math.atan2(Y, X)

def wgs_to_eov(lat_deg, lon_deg):
    w = _toxyz(lat_deg * _rad, lon_deg * _rad, _aW, _e2W)
    phi, lam = _fromxyz(w[0] - _T[0], w[1] - _T[1], w[2] - _T[2], _a, _e2)
    S = -_alpha * (math.log(math.tan(math.pi / 4 - phi / 2))
                   + _e / 2 * math.log((1 + _e * math.sin(phi)) / (1 - _e * math.sin(phi)))) + _K
    b = 2 * (math.atan(math.exp(S)) - math.pi / 4)
    I = _alpha * (lam - _lon0)
    rotI = math.atan(math.sin(I) / (math.sin(_b0) * math.tan(b) + math.cos(_b0) * math.cos(I)))
    rotB = math.asin(math.cos(_b0) * math.sin(b) - math.sin(_b0) * math.cos(b) * math.cos(I))
    return (_R * rotI + _x0, _R / 2 * math.log((1 + math.sin(rotB)) / (1 - math.sin(rotB))) + _y0)

# ---------- point in polygon ----------
def in_ring(x, y, ring):
    inside = False
    j = len(ring) - 1
    for i in range(len(ring)):
        xi, yi = ring[i]
        xj, yj = ring[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
            inside = not inside
        j = i
    return inside
