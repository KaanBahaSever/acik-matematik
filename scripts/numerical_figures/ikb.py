# -*- coding: utf-8 -*-
"""
Figures of the chapter "İkiye Bölme Metodu"
(dersler/numerik-analiz/ikiye-bolme-metodu.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box and never directly under a heading.
The figures are NOT produced at build time. Run

    python scripts/numerical_figures/ikb.py
    python scripts/center_figures.py "numerical-ikb-*.md"
    python scripts/check_figure_labels.py "scripts/_figures/numerical-ikb-*.md"

and paste the markup of scripts/_figures/numerical-ikb-<name>.md into the .qmd.
Captions are Turkish on purpose; aria labels are plain ASCII.

The step-count surface n = floor(log2(L / eps)) + 1 is drawn exactly: every
terrace is the region between two curves L = 2^k eps, one flat polygon per
level, and the risers follow those curves. The staircase is seen from its low
corner, so every terrace and riser faces the viewer.
"""
import html
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, dot, hollow, TEXT, THEORY, PRACTICE, BASE, REMARK, BG, WIDE  # noqa: E402
from svg_plot3 import Camera, Space  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "numerical-ikb-"

MINUS = "&#8722;"


def save(name, markup):
    (OUT_DIR / f"{PREFIX}{name}.md").write_text(markup, encoding="utf-8", newline="\n")
    print(f"{PREFIX}{name}.md")


def it(s):
    """Italic run inside an SVG <text>."""
    return f'<tspan font-style="italic">{s}</tspan>'


def sup(s, size=8.5):
    """Superscript inside an SVG <text>."""
    return f'<tspan font-size="{size}" dy="-5">{s}</tspan><tspan dy="5">&#8203;</tspan>'


def sub(s, size=8.5):
    """Subscript inside an SVG <text>."""
    return f'<tspan font-size="{size}" dy="3.5">{s}</tspan><tspan dy="-3.5">&#8203;</tspan>'


def dec(v, nd=4):
    """Decimal comma and a true minus sign: -0.5 -> '−0,5'."""
    s = f"{v:.{nd}f}".rstrip("0").rstrip(".")
    return s.replace(".", ",").replace("-", MINUS)


def pow10(k):
    """10^k as SVG text."""
    return "10" + sup(dec(k))


def text_w(s, size):
    """Rough advance width of a label (0.56 em per visible character)."""
    plain = html.unescape(re.sub(r"<[^>]+>", "", s)).replace("​", "")
    return len(plain) * 0.56 * size


def plate_px(p, px, py, s, size=11.5, anchor="start", opacity=0.9):
    """Page-coloured rounded plate under a label at pixel position (px, py)."""
    w = text_w(s, size)
    x0 = px - (w / 2 if anchor == "middle" else w if anchor == "end" else 0)
    p.add(f'<rect x="{x0 - 2.5:.1f}" y="{py - 0.8 * size - 1:.1f}" width="{w + 5:.1f}" '
          f'height="{size + 3:.1f}" rx="3" fill="{BG}" opacity="{opacity}"/>')


def clip_polyline(pts, xr, yr):
    """Cut a polyline to the rectangle xr x yr; returns the list of inside runs."""
    (x0, x1), (y0, y1) = xr, yr

    def inside(q):
        return x0 <= q[0] <= x1 and y0 <= q[1] <= y1

    def cut(a, b):
        """Liang-Barsky: the part of segment ab inside the box, or None."""
        t0, t1 = 0.0, 1.0
        dx, dy = b[0] - a[0], b[1] - a[1]
        for pk, qk in ((-dx, a[0] - x0), (dx, x1 - a[0]), (-dy, a[1] - y0), (dy, y1 - a[1])):
            if pk == 0:
                if qk < 0:
                    return None
                continue
            r = qk / pk
            if pk < 0:
                t0 = max(t0, r)
            else:
                t1 = min(t1, r)
            if t0 > t1:
                return None
        return ((a[0] + t0 * dx, a[1] + t0 * dy), (a[0] + t1 * dx, a[1] + t1 * dy))

    runs, cur = [], []
    for a, b in zip(pts, pts[1:]):
        seg = cut(a, b)
        if seg is None:
            if cur:
                runs.append(cur)
                cur = []
            continue
        if not cur:
            cur = [seg[0]]
        cur.append(seg[1])
        if not inside(b):
            runs.append(cur)
            cur = []
    if cur:
        runs.append(cur)
    return [r for r in runs if len(r) > 1]


def sample(f, a, b, n=400):
    return [(a + (b - a) * k / n, f(a + (b - a) * k / n)) for k in range(n + 1)]


def double_arrow(p, x0, x1, y, color=TEXT, width=1.3, head=7.0):
    """Horizontal arrow with heads at both ends."""
    xm = (x0 + x1) / 2
    p.arrow((xm, y), (x0, y), color, width, head)
    p.arrow((xm, y), (x1, y), color, width, head)


# ============================================================
# yatik-fonksiyon: f(x) = (x - 1)^9, small values far from the root
# ============================================================
def flat(x):
    return (x - 1) ** 9


XR, YR = (0.0, 2.0), (-0.02, 0.02)
EPS = 1e-3
R = 10 ** (-1 / 3)                        # |x - 1| < R  <=>  |f(x)| < 10^-3
p = Plot(80, 30, 460, 280, XR, YR)
p.grid([0.5, 1, 1.5, 2], [-0.02, -0.01, 0.01, 0.02])
p.polygon([(0, -EPS), (2, -EPS), (2, EPS), (0, EPS)], BASE, 0.22)
p.origin_axes("", it("y"), (2,), (-0.02, -0.01, 0.01, 0.02), dec, dec, opacity=0.75)
p.label(2, 0, it("x"), 0, -9, TEXT, 12.5, "end")
p.line([(1 - R, 0), (1 + R, 0)], BASE, 6, None, 0.55)
for run in clip_polyline(sample(flat, 0, 2, 800), XR, YR):
    p.line(run, THEORY, 2.4)
p.label(0, EPS, "|" + it("f") + "(" + it("x") + ")| &lt; " + pow10(-3), 8, -7, BASE, 11.5, "start", True)
p.label(1 - R, 0, dec(1 - R), 2, 24, BASE, 11, "start")
p.label(1 + R, 0, dec(1 + R), 2, 24, BASE, 11, "start")
# p and p*, with the distance 0.4 between them
YA = -0.0065
for xv in (1.0, 1.4):
    p.vline(xv, 0, YA, TEXT, "3 3", 0.55)
double_arrow(p, 1.0, 1.4, YA, TEXT, 1.2, 7)
p.label(1.2, YA, "0,4", 0, 16, TEXT, 12, "middle", True)
dot(p, (1.0, 0.0), TEXT, 4.0)
p.label(1.0, 0, it("p") + " = 1", 0, -11, TEXT, 12, "middle")
hollow(p, (1.4, flat(1.4)), PRACTICE, 4.4, 2.0)
p.label(1.4, 0, it("p") + "* = 1,4", 6, -11, PRACTICE, 12, "end", True)
save("yatik-fonksiyon", figure(
    int(p.x0 + p.w + 40), int(p.y0 + p.h + 40), [p],
    "<em>f</em>(<em>x</em>) = (<em>x</em> &#8722; 1)<sup>9</sup> grafiği. Taralı şerit "
    "|<em>f</em>(<em>x</em>)| &lt; 10<sup>&#8722;3</sup> bölgesidir. Grafik bu şeridin içinde "
    "(0,5358; 1,4642) aralığı boyunca kalır, kalın parça bu aralıktır. "
    "<em>p</em>* = 1,4 noktasında <em>f</em>(1,4) &#8776; 0,000262 olduğundan nokta eksenin hemen "
    "üstündedir, ama kökten uzaklığı 0,4'tür.",
    aria="Graph of f(x) = (x - 1)^9 on the window x from 0 to 2, y from -0.02 to 0.02, with the thin band "
         "where the absolute value of f is below 0.001, the interval (0.5358, 1.4642) where the graph stays "
         "in the band, the root p = 1 and the point p* = 1.4 at distance 0.4 from it"))


# ============================================================
# ic-ice-araliklar: f(x) = x^3 + 4x^2 - 10 and the nested intervals
# ============================================================
def cubic(x):
    return x ** 3 + 4 * x ** 2 - 10


ROOT = 1.3652300134
XR = (0.9, 2.1)
p1 = Plot(190, 30, 480, 230, XR, (-6.0, 15.0))
p1.grid([1, 1.25, 1.5, 1.75, 2], [-5, 5, 10, 15])
p1.axes((1, 1.25, 1.5, 1.75, 2), (-5, 0, 5, 10, 15), "", "", dec, dec)
p1.text_px(p1.x0 - 4, p1.y0 - 14, it("y"), TEXT, 12, "middle")
p1.line([(XR[0], 0), (XR[1], 0)], TEXT, 1.2, None, 0.7)
p1.label(XR[1], 0, it("x"), 8, 4, TEXT, 12.5)
for run in clip_polyline(sample(cubic, 0.9, 2.1, 400), XR, (-6.0, 15.0)):
    p1.line(run, THEORY, 2.4)
# the midpoints p_1, ..., p_5 with their function values
mids = []
a, b = 1.0, 2.0
for k in range(5):
    m = (a + b) / 2
    mids.append((a, b, m, cubic(m)))
    if cubic(m) * cubic(a) > 0:
        a = m
    else:
        b = m
for k, (_, _, m, fm) in enumerate(mids):
    p1.vline(m, 0, fm, PRACTICE, "3 2", 0.9)
    p1.points([(m, fm)], PRACTICE, 2.8)
p1.label(1.5, cubic(1.5), it("p") + sub("1"), 0, -8, PRACTICE, 12, "middle")
p1.label(1.25, cubic(1.25), it("p") + sub("2"), 0, 16, PRACTICE, 12, "middle")
for (x, y), (dx, dy, anc) in (((1, -5), (8, 4, "start")), ((2, 14), (-9, 4, "end"))):
    dot(p1, (x, y), THEORY, 4.0)
    p1.label(x, y, "(" + dec(x) + ", " + dec(y) + ")", dx, dy, THEORY, 11.5, anc)
hollow(p1, (ROOT, 0), TEXT, 3.6, 1.6)
p1.label(ROOT, 0, it("p"), 2, -9, TEXT, 12.5, "middle", True)

# bars: row n sits at y = 6 - n
p2 = Plot(190, 305, 480, 190, XR, (0.5, 5.5))
TOP = p1.Y(0)
p2.add(f'<line x1="{p2.X(ROOT):.1f}" y1="{TOP:.1f}" x2="{p2.X(ROOT):.1f}" y2="{p2.y0 + p2.h:.1f}" '
       f'stroke="{TEXT}" stroke-width="1" stroke-dasharray="4 3" opacity="0.6"/>')
for n, (a, b, m, fm) in enumerate(mids, start=1):
    y = 6 - n
    ya, yb = p2.Y(y) - 4.5, 9
    p2.add(f'<rect x="{p2.X(a):.1f}" y="{ya:.1f}" width="{p2.X(b) - p2.X(a):.1f}" height="{yb}" '
           f'fill="{BASE}" fill-opacity="0.45" stroke="{BASE}" stroke-width="1.1"/>')
    hollow(p2, (m, y), PRACTICE, 3.4, 1.6)
    p2.label(m, y, "+" if fm > 0 else MINUS, 0, -9, PRACTICE, 13, "middle", True)
    p2.text_px(p2.x0 - 14, p2.Y(y) + 4, "[" + dec(a) + "; " + dec(b) + "]", TEXT, 11.5, "end")
    p2.text_px(p2.x0 - 128, p2.Y(y) + 4, str(n), TEXT, 11.5, "middle")
# column headers of the little table left of the bars
p2.text_px(p2.x0 - 128, p2.y0 - 2, it("n"), TEXT, 12, "middle", True)
p2.text_px(p2.x0 - 14, p2.y0 - 2, "[" + it("a") + sub(it("n")) + ", " + it("b") + sub(it("n")) + "]",
           TEXT, 12, "end", True)
save("ic-ice-araliklar", figure(
    int(p1.x0 + p1.w + 40), int(p2.y0 + p2.h + 20), [p1, p2],
    "Üstte <em>f</em>(<em>x</em>) = <em>x</em>³ + 4<em>x</em>² &#8722; 10 grafiği; kesikli dikey "
    "parçalar <em>p</em><sub>1</sub> = 1,5, <em>p</em><sub>2</sub> = 1,25, <em>p</em><sub>3</sub> = 1,375, "
    "<em>p</em><sub>4</sub> = 1,3125, <em>p</em><sub>5</sub> = 1,34375 orta noktalarındaki fonksiyon "
    "değerleridir. Altta aynı ölçekte ilk beş [<em>a</em><sub><em>n</em></sub>, "
    "<em>b</em><sub><em>n</em></sub>] aralığı, orta noktaları ve <em>f</em>(<em>p</em><sub><em>n</em></sub>) "
    "değerinin işareti. Her aralık bir öncekinin yarısıdır ve hepsi <em>p</em> &#8776; 1,3652 kökünü "
    "(kesikli çizgi) içerir.",
    css_class=WIDE,
    aria="Top: graph of x^3 + 4x^2 - 10 between 0.9 and 2.1 with the endpoints (1, -5), (2, 14), the root "
         "p near 1.3652 and dashed segments at the midpoints 1.5, 1.25, 1.375, 1.3125, 1.34375. Bottom: the "
         "nested intervals [1, 2], [1, 1.5], [1.25, 1.5], [1.25, 1.375], [1.3125, 1.375] with their "
         "midpoints and the sign of f there"))


# ============================================================
# adim-sayisi-yuzey: n(L, eps) = floor(log2(L / eps)) + 1
# ============================================================
L0, L1 = 0.25, 8.0                        # L = b - a
U0, U1 = 1.0, 6.0                         # u = -log10(eps)
LOG2_10 = math.log2(10)
SL, SU, SZ = 0.42, 0.62, 0.084            # world units per unit of L, per decade of eps, per step


def steps(L, u):
    return math.floor(math.log2(L) + u * LOG2_10) + 1


def W(L, u, n):
    return (L * SL, (u - U0) * SU, n * SZ)


def L_at(c, u):
    """The curve log2(L / eps) = c, i.e. L = 2^c 10^(-u)."""
    return 2.0 ** c * 10.0 ** (-u)


def u_at(c, L):
    return (c - math.log2(L)) / LOG2_10


def curve_pts(c, k=48):
    """Samples (L, u) of the curve L = 2^c 10^-u inside the rectangle, or []."""
    ua = max(U0, u_at(c, L1))
    ub = min(U1, u_at(c, L0))
    if ua >= ub:
        return []
    return [(L_at(c, ua + (ub - ua) * i / k), ua + (ub - ua) * i / k) for i in range(k + 1)]


def terrace(m, k=48):
    """Boundary (L, u) of the region where n = m, as one closed polygon."""
    # region: m - 1 <= log2 L + u log2 10 < m inside the rectangle; walk the boundary
    lo, hi = m - 1, m
    pts = []
    # bottom edge u = U0 from left to right, then right edge, top edge, left edge;
    # the two level curves cut the rectangle; build by sampling the rectangle edge and the curves
    us = [U0 + (U1 - U0) * i / (4 * k) for i in range(4 * k + 1)]
    left, right = [], []
    for u in us:
        a = max(L0, L_at(lo, u))
        b = min(L1, L_at(hi, u))
        if a < b:
            left.append((a, u))
            right.append((b, u))
    # add exact kinks so the polygon corners are sharp
    for c, edge in ((lo, L0), (hi, L1), (lo, L1), (hi, L0)):
        u = u_at(c, edge)
        if U0 < u < U1:
            a, b = max(L0, L_at(lo, u)), min(L1, L_at(hi, u))
            if a <= b:
                left.append((a, u))
                right.append((b, u))
    left.sort(key=lambda t: t[1])
    right.sort(key=lambda t: t[1])
    pts = right + left[::-1]
    return pts


cam = Camera(azimuth=222.0, elevation=24.0)
NMIN, NMAX = steps(L0, U0), steps(L1, U1)
box = [W(L, u, n) for L in (0, L1 + 0.6) for u in (U0 - 0.4, U1 + 0.3) for n in (0, 25.5)]
q = [cam.project(P)[:2] for P in box]
xr = (min(a for a, _ in q) - 0.1, max(a for a, _ in q) + 0.1)
yr = (min(b for _, b in q) - 0.1, max(b for _, b in q) + 0.1)
PPU = 104
pl = Plot(60, 30, (xr[1] - xr[0]) * PPU, (yr[1] - yr[0]) * PPU, xr, yr)
S = Space(pl, cam)

faces = []


def face(pts, fill, op, stroke_op=0.0):
    dep = sum(cam.project(P)[2] for P in pts) / len(pts)
    faces.append((dep, pts, fill, op, stroke_op))


for m in range(NMIN, NMAX + 1):
    poly = terrace(m)
    if len(poly) < 3:
        continue
    t = (m - NMIN) / (NMAX - NMIN)
    P3 = [W(L, u, m) for L, u in poly]
    dep = max(cam.project(P)[2] for P in P3)
    # colour by height: a BASE layer fading out under a PRACTICE layer fading in
    faces.append((dep, P3, BASE, 0.34 * (1 - t) + 0.04, 0.0))
    faces.append((dep + 1e-6, P3, PRACTICE, 0.30 * t + 0.02, 0.0))
    # riser along log2(L / eps) = m between level m and m + 1
    if m < NMAX:
        cp = curve_pts(m)
        for (La, ua), (Lb, ub) in zip(cp, cp[1:]):
            face([W(La, ua, m), W(Lb, ub, m), W(Lb, ub, m + 1), W(La, ua, m + 1)], THEORY, 0.14)
# front curtains (u = U0 and L = L0) from the staircase down to the floor
for edge in ("u", "L"):
    k = 160
    for i in range(k):
        if edge == "u":
            La, Lb = L0 + (L1 - L0) * i / k, L0 + (L1 - L0) * (i + 1) / k
            A, B = (La, U0), (Lb, U0)
        else:
            ua, ub = U0 + (U1 - U0) * i / k, U0 + (U1 - U0) * (i + 1) / k
            A, B = (L0, ua), (L0, ub)
        nmid = steps((A[0] + B[0]) / 2, (A[1] + B[1]) / 2)
        face([W(*A, 0), W(*B, 0), W(*B, nmid), W(*A, nmid)], THEORY, 0.05)
faces.sort(key=lambda t: t[0])

# back floor edges, faint (they lie behind the staircase)
S.line([W(L0, U1, 0), W(L1, U1, 0), W(L1, U0, 0)], TEXT, 0.8, "3 3", 0.35)
S.line([W(L1, U1, 0), W(L1, U1, NMAX)], TEXT, 0.8, "3 3", 0.35)

for _, pts, fill, op, sop in faces:
    pp = " ".join(pl.P(*S.pt(P)) for P in pts)
    pl.add(f'<polygon points="{pp}" fill="{fill}" fill-opacity="{op:.3f}" stroke="none"/>')

# terrace edges: the top and bottom of every riser
for m in range(NMIN, NMAX):
    cp = curve_pts(m)
    if cp:
        S.line([W(L, u, m + 1) for L, u in cp], THEORY, 0.9, None, 0.75)
        S.line([W(L, u, m) for L, u in cp], THEORY, 0.5, None, 0.45)


def profile(edge):
    """Step profile of the staircase along a front edge, at full height."""
    pts = []
    k = 600
    prev = None
    for i in range(k + 1):
        if edge == "u":
            P = (L0 + (L1 - L0) * i / k, U0)
        else:
            P = (L0, U0 + (U1 - U0) * i / k)
        n = steps(*P)
        if prev is not None and n != prev:
            pts.append(W(*P, prev))
        pts.append(W(*P, n))
        prev = n
    return pts


S.line(profile("u"), THEORY, 1.3, None, 0.9)
S.line(profile("L"), THEORY, 1.3, None, 0.9)
S.line([W(L0, U1, 0), W(L0, U0, 0), W(L1, U0, 0)], TEXT, 0.8, None, 0.5)
S.line([W(L0, U0, 0), W(L0, U0, NMIN)], TEXT, 0.8, None, 0.5)
S.line([W(L1, U0, 0), W(L1, U0, steps(L1, U0))], TEXT, 0.8, None, 0.5)
S.line([W(L0, U1, 0), W(L0, U1, steps(L0, U1))], TEXT, 0.8, None, 0.5)

# axes: L along the front floor edge, eps along the left floor edge, n at the left corner
UA = U0 - 0.3
S.arrow(W(0, UA, 0), W(L1 + 0.6, UA, 0), TEXT, 1.1, 7, None, 0.7)
S.label(W(L1 + 0.6, UA, 0), it("b") + " " + MINUS + " " + it("a"), 10, 12, TEXT, 12.5)
for Lv in (1, 2, 3, 4, 5, 6, 7, 8):
    S.line([W(Lv, UA - 0.08, 0), W(Lv, UA + 0.08, 0)], TEXT, 1.0, None, 0.7)
    S.label(W(Lv, UA, 0), str(Lv), 0, 16, TEXT, 10.5, "middle")
LA = L0 - 0.45
S.arrow(W(LA, U0 - 0.3, 0), W(LA, U1 + 0.55, 0), TEXT, 1.1, 7, None, 0.7)
S.label(W(LA, U1 + 0.55, 0), "&#949;", -6, 2, TEXT, 13, "end", False, True)
for k in range(1, 7):
    S.line([W(LA - 0.1, k, 0), W(LA + 0.1, k, 0)], TEXT, 1.0, None, 0.7)
    S.label(W(LA, k, 0), pow10(-k), -8, 12, TEXT, 10.5, "end")
NZ = (LA, U1)
S.arrow(W(*NZ, 0), W(*NZ, 25.5), TEXT, 1.1, 7, None, 0.7)
S.label(W(*NZ, 25.5), it("n"), 0, -9, TEXT, 12.5, "middle")
for nv in (5, 10, 15, 20, 25):
    S.line([W(NZ[0] - 0.12, NZ[1], nv), W(NZ[0] + 0.12, NZ[1], nv)], TEXT, 1.0, None, 0.7)
    S.label(W(*NZ, nv), str(nv), -9, 4, TEXT, 10.5, "end")

# the five marked points
POINTS = ((1, 1e-3), (5, 0.005), (0.25, 0.01), (3, 1e-3), (1, 1e-2))
LABELS = {
    (1, 1e-3): ("1; " + pow10(-3), (-10, -8, "end")),
    (5, 0.005): ("5; 0,005", (10, 6, "start")),
    (0.25, 0.01): ("0,25; " + pow10(-2), (-10, 2, "end")),
    (3, 1e-3): ("3; " + pow10(-3), (-4, -12, "middle")),
    (1, 1e-2): ("1; " + pow10(-2), (-10, 10, "end")),
}
for L, e in POINTS:
    u = -math.log10(e)
    n = steps(L, u)
    P = W(L, u, n)
    S.point(P, PRACTICE, 4.2)
    s, (dx, dy, anc) = LABELS[(L, e)]
    s = "(" + s + "): " + it("n") + " = " + str(n)
    X, Y = S.pt(P)
    plate_px(pl, pl.X(X) + dx, pl.Y(Y) + dy, s, 11.5, anc)
    S.label(P, s, dx, dy, PRACTICE, 11.5, anc, True)
save("adim-sayisi-yuzey", figure(
    int(pl.x0 + pl.w + 40), int(pl.y0 + pl.h + 30), [pl],
    "<em>n</em> = &#8970;log<sub>2</sub>((<em>b</em> &#8722; <em>a</em>)/&#949;)&#8971; + 1 adım sayısı: "
    "<em>b</em> &#8722; <em>a</em> &#8712; [0,25; 8] ve &#949; &#8712; [10<sup>&#8722;6</sup>, "
    "10<sup>&#8722;1</sup>] (logaritmik eksen) üzerinde tam sayı değerli teraslardan oluşan bir merdiven. "
    "Renk <em>n</em> büyüdükçe değişir. Etiketlerde (<em>b</em> &#8722; <em>a</em>; &#949;) çifti ve adım "
    "sayısı yazılıdır. (1; 10<sup>&#8722;3</sup>) ile (5; 0,005) aynı terastadır, çünkü ikisinde de "
    "(<em>b</em> &#8722; <em>a</em>)/&#949; = 1000'dir.",
    aria="Staircase surface of the bisection step count n = floor(log2(L / eps)) + 1 over L = b - a from "
         "0.25 to 8 and eps from 1e-6 to 1e-1 on a logarithmic axis, with five marked points: "
         "(1, 1e-3) n = 10, (5, 0.005) n = 10, (0.25, 0.01) n = 5, (3, 1e-3) n = 12, (1, 1e-2) n = 7"))
