# -*- coding: utf-8 -*-
"""
Figures of the chapter "Ön Bilgiler ve Taylor Teoremi"
(dersler/numerik-analiz/on-bilgiler-ve-taylor-teoremi.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box and never directly under a heading.
The figures are NOT produced at build time. Run

    python scripts/numerical_figures/onb.py
    python scripts/center_figures.py "numerical-onb-*.md"
    python scripts/check_figure_labels.py "scripts/_figures/numerical-onb-*.md"

and paste the markup of scripts/_figures/numerical-onb-<name>.md into the .qmd.
Captions are Turkish on purpose; aria labels are plain ASCII.

The 3-D error surface is a staircase seen from its low corner, so every top
face and every riser faces the viewer; the faces are painted back to front and
the wire net is drawn on top.
"""
import html
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, dot, hollow, TEXT, THEORY, PRACTICE, BASE, BG  # noqa: E402
from svg_plot3 import Camera, Space  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "numerical-onb-"

MINUS = "&#8722;"
APPROX = "&#8776;"


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


def text_w(s, size):
    """Rough advance width of a label (0.56 em per visible character)."""
    plain = html.unescape(re.sub(r"<[^>]+>", "", s)).replace("​", "")
    return len(plain) * 0.56 * size


def plate(p, x, y, s, dx=0, dy=0, size=11.5, anchor="start", opacity=0.9):
    """Page-coloured rounded plate under a label that has to sit on lines."""
    px, py = p.X(x) + dx, p.Y(y) + dy
    w = text_w(s, size)
    x0 = px - (w / 2 if anchor == "middle" else w if anchor == "end" else 0)
    p.add(f'<rect x="{x0 - 2.5:.1f}" y="{py - 0.8 * size - 1:.1f}" width="{w + 5:.1f}" '
          f'height="{size + 3:.1f}" rx="3" fill="{BG}" opacity="{opacity}"/>')


def plabel(p, x, y, s, dx=0, dy=0, color=TEXT, size=11.5, anchor="start", bold=False):
    plate(p, x, y, s, dx, dy, size, anchor)
    p.label(x, y, s, dx, dy, color, size, anchor, bold)


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


# ============================================================
# ustel-kokler: f(x) = 4x^2 - e^x on [-1, 5], three roots
# ============================================================
def f_exp(x):
    return 4 * x * x - math.exp(x)


XR, YR = (-1.25, 5.3), (-10.0, 18.0)
p = Plot(80, 40, 450, 300, XR, YR)
p.grid([-1, 1, 2, 3, 4, 5], [-10, -5, 5, 10, 15])
p.origin_axes(it("x"), it("y"), (-1, 1, 2, 3, 4, 5), (-10, -5, 5, 10, 15), dec, dec, opacity=0.75)
# the three bracketing intervals on the x axis (small gaps keep (-1, 0) and (0, 1) apart)
for a, b in ((-1, 0), (0, 1), (4, 5)):
    p.line([(a + 0.035, 0), (b - 0.035, 0)], PRACTICE, 7, None, 0.38)
for run in clip_polyline(sample(f_exp, -1, 5, 600), XR, YR):
    p.line(run, THEORY, 2.4)
# f(5) lies far below the window: arrow to the bottom edge
p.arrow((5, -6.2), (5, -10), PRACTICE, 1.6, 7.5)
p.label(5, -10, it("f") + "(5) " + APPROX + " " + MINUS + "48,41", 0, 17, PRACTICE, 11.5, "middle")
for (x, y), (dx, dy, anc) in (((-1, f_exp(-1)), (8, -6, "start")), ((0, f_exp(0)), (-6, 15, "end")),
                              ((1, f_exp(1)), (-7, -6, "end")), ((4, f_exp(4)), (8, 4, "start"))):
    dot(p, (x, y), THEORY, 3.8)
    p.label(x, y, dec(y), dx, dy, THEORY, 11.5, anc)
for r in (-0.407776709, 0.714805912, 4.306584728):
    hollow(p, (r, 0), PRACTICE, 4.2, 1.8)
save("ustel-kokler", figure(
    int(p.x0 + p.w + 50), int(p.y0 + p.h + 50), [p],
    "<em>y</em> = 4<em>x</em>² &#8722; <em>e</em><sup><em>x</em></sup> grafiği. İşaretli noktalar "
    "<em>f</em>(&#8722;1), <em>f</em>(0), <em>f</em>(1) ve <em>f</em>(4) değerleridir. Eğri "
    "<em>x</em> ekseninin altına iner ve <em>f</em>(5) &#8776; &#8722;48,41 olur. Boş daireler "
    "<em>x</em> &#8776; &#8722;0,4078; 0,7148; 4,3066 köklerini, kalın parçalar bu kökleri içeren "
    "(&#8722;1, 0), (0, 1) ve (4, 5) aralıklarını gösterir.",
    aria="Graph of y = 4x^2 - e^x for x from -1 to 5 with the values at -1, 0, 1 and 4 marked, "
         "three roots shown as open circles and the bracketing intervals (-1, 0), (0, 1), (4, 5) "
         "highlighted on the x axis"))

# ============================================================
# cos-taylor: cos x against P_2 and P_4 on [-4, 4]
# ============================================================
XR, YR = (-4.0, 4.0), (-2.0, 2.0)
p = Plot(50, 30, 480, 240, XR, YR)
p.grid([-4, -3, -2, -1, 1, 2, 3, 4], [-2, -1, 1, 2])
p.origin_axes(it("x"), it("y"), (), (), opacity=0.75)
# tick labels along the frame, away from the curves that cross the axes
for t in (-4, -3, -2, -1, 0, 1, 2, 3, 4):
    p.label(t, -2, dec(t), 0, 17, TEXT, 11, "middle")
for t in (-2, -1, 0, 1, 2):
    p.label(-4, t, dec(t), -8, 4, TEXT, 11, "end")
curves = (
    (lambda x: 1 - x * x / 2, PRACTICE, 2.1, "7 4"),
    (lambda x: 1 - x * x / 2 + x ** 4 / 24, BASE, 2.4, "0.1 4.2"),
    (math.cos, THEORY, 2.8, None),
)
for g, col, wd, da in curves:
    for run in clip_polyline(sample(g, -4, 4, 800), XR, YR):
        p.line(run, col, wd, da)
dot(p, (0, 1), TEXT, 4.0)
p.label(0, 1, "(0, 1)", 7, -9, TEXT, 11.5)
# legend under the panel
LY = p.y0 + p.h + 50
items = ((it("cos x"), THEORY, 2.8, None),
         (it("P") + sub("2") + "(" + it("x") + ")", PRACTICE, 2.1, "7 4"),
         (it("P") + sub("4") + "(" + it("x") + ")", BASE, 2.4, "0.1 4.2"))
x = p.x0 + p.w / 2 - 190
for s, col, wd, da in items:
    da_s = f' stroke-dasharray="{da}"' if da else ""
    p.add(f'<line x1="{x:.1f}" y1="{LY - 4:.1f}" x2="{x + 34:.1f}" y2="{LY - 4:.1f}" stroke="{col}" '
          f'stroke-width="{wd}"{da_s} stroke-linecap="round"/>')
    p.text_px(x + 42, LY, s, TEXT, 12)
    x += 130
save("cos-taylor", figure(
    int(p.x0 + p.w + 40), int(LY + 20), [p],
    "<em>y</em> = cos <em>x</em> ile <em>x</em><sub>0</sub> = 0 civarındaki Taylor polinomları "
    "<em>P</em><sub>2</sub>(<em>x</em>) = 1 &#8722; <em>x</em>²/2 ve "
    "<em>P</em><sub>4</sub>(<em>x</em>) = 1 &#8722; <em>x</em>²/2 + <em>x</em><sup>4</sup>/24. "
    "Üç eğri (0, 1) noktası civarında üst üste biner. Uzaklaştıkça önce <em>P</em><sub>2</sub>, "
    "daha geç <em>P</em><sub>4</sub> kosinüsten ayrılır: <em>x</em> = 2'de cos 2 &#8776; &#8722;0,4161, "
    "<em>P</em><sub>2</sub>(2) = &#8722;1, <em>P</em><sub>4</sub>(2) &#8776; &#8722;0,3333 olur.",
    aria="Graphs of cos x, the Taylor polynomial P2 = 1 - x^2/2 (dashed) and P4 = 1 - x^2/2 + x^4/24 "
         "(dotted) on the window x from -4 to 4, y from -2 to 2; all three agree near (0, 1)"))


# ============================================================
# cos-hata-yuzeyi: z = log10 |cos x - P_n(x)|, x in [0.1, 3], n = 0..8
# ============================================================
def remainder(x, n):
    """cos x - P_n(x) as the tail of the Maclaurin series (no cancellation)."""
    k0 = n // 2 + 1                       # first even power 2k with 2k > n
    s, term = 0.0, None
    for k in range(k0, k0 + 30):
        term = (-1) ** k * x ** (2 * k) / math.factorial(2 * k)
        s += term
    return s


ZMIN, ZMAX = -16.0, 1.0


def zval(x, n):
    return max(ZMIN, math.log10(abs(remainder(x, n))))


SX, SN, SZ = 1.25, 0.36, 0.12          # world units per x, per n and per decade


def W(x, n, z):
    """Data (x, n, log10 error) -> world point. n runs toward the viewer."""
    return (x * SX, -n * SN, (z - ZMIN) * SZ)


cam = Camera(azimuth=238.0, elevation=24.0)
X0, X1 = 0.1, 3.0
NX = 58
xs = [X0 + (X1 - X0) * k / NX for k in range(NX + 1)]
Z = {n: [zval(x, n) for x in xs] for n in range(9)}

box = [W(x, n, z) for x in (0, X1 + 0.35) for n in (-0.5, 8.5 + 0.9) for z in (ZMIN, ZMAX + 0.6)]
q = [cam.project(P)[:2] for P in box]
xr = (min(a for a, _ in q) - 0.15, max(a for a, _ in q) + 0.15)
yr = (min(b for _, b in q) - 0.15, max(b for _, b in q) + 0.15)
PPU = 92
pl = Plot(60, 30, (xr[1] - xr[0]) * PPU, (yr[1] - yr[0]) * PPU, xr, yr)
S = Space(pl, cam)

faces = []                                # (depth, [world points], fill, opacity)


def face(pts, fill, op):
    dep = sum(cam.project(P)[2] for P in pts) / len(pts)
    faces.append((dep, pts, fill, op))


for n in range(9):
    for i in range(NX):
        a, b = xs[i], xs[i + 1]
        za, zb = Z[n][i], Z[n][i + 1]
        face([W(a, n - 0.5, za), W(b, n - 0.5, zb), W(b, n + 0.5, zb), W(a, n + 0.5, za)], THEORY, 0.2)
        if n < 8 and n % 2 == 1:          # risers only where P_n changes (odd -> even)
            za2, zb2 = Z[n + 1][i], Z[n + 1][i + 1]
            face([W(a, n + 0.5, za), W(b, n + 0.5, zb), W(b, n + 0.5, zb2), W(a, n + 0.5, za2)],
                 PRACTICE, 0.16)
# front curtain at x = 0.1, from the staircase profile down to the floor
for n in range(9):
    face([W(X0, n - 0.5, ZMIN), W(X0, n + 0.5, ZMIN), W(X0, n + 0.5, Z[n][0]), W(X0, n - 0.5, Z[n][0])],
         THEORY, 0.07)
faces.sort(key=lambda t: t[0])

# floor frame and back edges (drawn first, they lie behind or under the staircase)
S.line([W(X0, -0.5, ZMIN), W(X1, -0.5, ZMIN), W(X1, 8.5, ZMIN)], TEXT, 0.8, "3 3", 0.35)
for n in (-0.5, 8.5):
    S.line([W(X1, n, ZMIN), W(X1, n, Z[max(0, min(8, round(n)))][-1])], TEXT, 0.8, "3 3", 0.35)

for _, pts, fill, op in faces:
    pp = " ".join(pl.P(*S.pt(P)) for P in pts)
    pl.add(f'<polygon points="{pp}" fill="{fill}" fill-opacity="{op:.3f}" stroke="{fill}" '
           f'stroke-width="0.3" stroke-opacity="0.08" stroke-linejoin="round"/>')

# wire net: strip edges along x and cross sections every 0.5 in x
for n in range(9):
    for e in (-0.5, 0.5):
        same = (n % 2 == 0 and e == 0.5 and n < 8) or (n % 2 == 1 and e == -0.5)
        S.line([W(x, n + e, Z[n][i]) for i, x in enumerate(xs)], THEORY,
               0.7 if same else 1.2, "3 3" if same else None, 0.55 if same else 0.85)
for i in range(0, NX + 1, 5):
    x = xs[i]
    path = []
    for n in range(9):
        path += [W(x, n - 0.5, Z[n][i]), W(x, n + 0.5, Z[n][i])]
    S.line(path, THEORY, 0.7, None, 0.55)
# front profile at x = 0.1 and the vertical edge of the curtain
front = []
for n in range(9):
    front += [W(X0, n - 0.5, Z[n][0]), W(X0, n + 0.5, Z[n][0])]
S.line(front, PRACTICE, 2.0)
S.line([W(X0, 8.5, Z[8][0]), W(X0, 8.5, ZMIN), W(X0, -0.5, ZMIN), W(X0, -0.5, Z[0][0])], TEXT, 0.8, None, 0.45)
S.line([W(X0, 8.5, ZMIN), W(X1, 8.5, ZMIN)], TEXT, 0.8, None, 0.45)
S.line([W(X0, 8.5, Z[8][0])] + [W(x, 8.5, Z[8][i]) for i, x in enumerate(xs)], THEORY, 1.2, None, 0.85)

# axes: x along the front floor edge, n along the left floor edge, z at the far left corner
NA = 8.5 + 0.55
S.arrow(W(0, NA, ZMIN), W(X1 + 0.3, NA, ZMIN), TEXT, 1.1, 7, None, 0.7)
S.label(W(X1 + 0.3, NA, ZMIN), it("x"), 9, 5, TEXT, 12.5)
for xv in (0.5, 1, 1.5, 2, 2.5, 3):
    S.line([W(xv, NA - 0.12, ZMIN), W(xv, NA + 0.12, ZMIN)], TEXT, 1.0, None, 0.7)
    S.label(W(xv, NA, ZMIN), dec(xv), 0, 17, TEXT, 10.5, "middle")
XA = -0.12
S.arrow(W(XA, -0.6, ZMIN), W(XA, NA + 0.35, ZMIN), TEXT, 1.1, 7, None, 0.7)
S.label(W(XA, NA + 0.35, ZMIN), it("n"), -6, 14, TEXT, 12.5, "middle")
for n in range(9):
    S.line([W(XA - 0.04, n, ZMIN), W(XA + 0.04, n, ZMIN)], TEXT, 1.0, None, 0.7)
    S.label(W(XA, n, ZMIN), str(n), -8, 9, TEXT, 10.5, "end")
ZX, ZN = XA, -0.6
S.arrow(W(ZX, ZN, ZMIN), W(ZX, ZN, ZMAX + 0.5), TEXT, 1.1, 7, None, 0.7)
for zv in (-16, -12, -8, -4, 0):
    S.line([W(ZX - 0.05, ZN, zv), W(ZX + 0.05, ZN, zv)], TEXT, 1.0, None, 0.7)
    S.label(W(ZX, ZN, zv), dec(zv), -8, 4, TEXT, 10.5, "end")
S.label(W(ZX, ZN, ZMAX + 0.5), "log" + sub("10") + " |cos " + it("x") + " " + MINUS + " " + it("P") + sub(it("n"))
        + "(" + it("x") + ")|", 0, -10, TEXT, 12, "middle")
# strip labels for the equal pairs
save("cos-hata-yuzeyi", figure(
    int(pl.x0 + pl.w + 40), int(pl.y0 + pl.h + 30), [pl],
    "<em>z</em> = log<sub>10</sub> |cos <em>x</em> &#8722; <em>P</em><sub><em>n</em></sub>(<em>x</em>)| "
    "yüzeyi (0,1 &#8804; <em>x</em> &#8804; 3, <em>n</em> = 0, 1, …, 8; <em>z</em> &#8805; &#8722;16 "
    "kırpılmıştır). Her <em>n</em> için <em>x</em> yönünde bir şerit vardır. Çift <em>n</em> ile ondan "
    "sonraki tek <em>n</em> şeridi aynı yüksekliktedir, çünkü <em>P</em><sub>2<em>k</em></sub> = "
    "<em>P</em><sub>2<em>k</em>+1</sub> olur; basamaklar yalnız çift <em>n</em>'lerde iner (yalnız <em>x</em> &gt; 2,78 için <em>n</em> = 2 şeridi <em>n</em> = 0 şeridinin biraz üstüne çıkar). Kalın eğri "
    "<em>x</em> = 0,1'deki profildir: <em>x</em> küçüldükçe ve <em>n</em> büyüdükçe hata hızla düşer.",
    aria="Staircase surface of log10 of the error of the Maclaurin polynomials of cos x, for x from 0.1 "
         "to 3 and n from 0 to 8; equal heights for each even n and the following odd n, steps down at "
         "every even n, lowest values for small x and large n"))


# ============================================================
# shared helpers of the concept figures (no numbers on the axes)
# ============================================================
PRIME = "&#8242;"


def concept_plot(xr=(-0.35, 5.4), yr=(-0.4, 3.6), w=440, h=290):
    """Panel with the origin near its lower left corner and arrowed axes."""
    p = Plot(110, 30, w, h, xr, yr)
    p.origin_axes(it("x"), it("y"), opacity=0.75)
    return p


def x_mark(p, x, y, s, color=TEXT, size=12.5):
    """Dashed drop line from (x, y) to the x axis, a tick and the name of x below the axis."""
    p.vline(x, 0, y, TEXT, "4 3", 0.45)
    p.add(f'<line x1="{p.X(x):.1f}" y1="{p.Y(0) - 3:.1f}" x2="{p.X(x):.1f}" y2="{p.Y(0) + 3:.1f}" '
          f'stroke="{TEXT}" stroke-width="1" opacity="0.75"/>')
    p.label(x, 0, s, 0, 18, color, size, "middle")


def y_mark(p, x, y, s, color=TEXT, size=12.5):
    """Dashed guide from the y axis to (x, y), a tick and the name of y left of the axis."""
    p.line([(0, y), (x, y)], TEXT, 1.0, "4 3", 0.45)
    p.add(f'<line x1="{p.X(0) - 3:.1f}" y1="{p.Y(y):.1f}" x2="{p.X(0) + 3:.1f}" y2="{p.Y(y):.1f}" '
          f'stroke="{TEXT}" stroke-width="1" opacity="0.75"/>')
    p.label(0, y, s, -8, 4.5, color, size, "end")


def bisect(g, lo, hi, n=80):
    """Root of g on [lo, hi] (g(lo) and g(hi) of opposite signs)."""
    glo = g(lo)
    for _ in range(n):
        mid = (lo + hi) / 2
        if (g(mid) > 0) == (glo > 0):
            lo, glo = mid, g(mid)
        else:
            hi = mid
    return (lo + hi) / 2


def legend(p, items, y, x=None, gap=40):
    """One-row legend: (label, color, width, dash) items, centred under the panel unless x is given."""
    widths = [42 + text_w(s, 12) for s, *_ in items]
    total = sum(widths) + gap * (len(items) - 1)
    x = p.x0 + p.w / 2 - total / 2 if x is None else x
    for (s, col, wd, da), wdt in zip(items, widths):
        da_s = f' stroke-dasharray="{da}"' if da else ""
        p.add(f'<line x1="{x:.1f}" y1="{y - 4:.1f}" x2="{x + 32:.1f}" y2="{y - 4:.1f}" stroke="{col}" '
              f'stroke-width="{wd}"{da_s} stroke-linecap="round"/>')
        p.text_px(x + 40, y, s, TEXT, 12)
        x += wdt + gap


FX = it("f")


def fof(s):
    """'f(s)' with an italic f."""
    return FX + "(" + s + ")"


# ============================================================
# rolle: f(a) = f(b) and a horizontal tangent at c
# ============================================================
A_R, B_R = 0.8, 4.6


def f_rolle(x):
    return 1.0 + 0.32 * (x - A_R) * (B_R - x) * (1 + 0.25 * (x - A_R))


C_R = bisect(lambda x: (f_rolle(x + 1e-6) - f_rolle(x - 1e-6)), A_R + 0.5, B_R - 0.5)
FA_R, FC_R = f_rolle(A_R), f_rolle(C_R)
p = concept_plot()
p.line([(0, FA_R), (B_R, FA_R)], TEXT, 1.0, "4 3", 0.45)
p.add(f'<line x1="{p.X(0) - 3:.1f}" y1="{p.Y(FA_R):.1f}" x2="{p.X(0) + 3:.1f}" y2="{p.Y(FA_R):.1f}" '
      f'stroke="{TEXT}" stroke-width="1" opacity="0.75"/>')
p.label(1.95, FA_R, fof(it("a")) + " = " + fof(it("b")), 0, -8, TEXT, 12.5, "middle")
x_mark(p, A_R, FA_R, it("a"))
x_mark(p, B_R, FA_R, it("b"))
x_mark(p, C_R, FC_R, it("c"), PRACTICE)
p.line(sample(f_rolle, A_R, B_R, 400), THEORY, 2.6)
p.line([(C_R - 0.95, FC_R), (C_R + 0.95, FC_R)], PRACTICE, 2.2)
dot(p, (A_R, FA_R), THEORY, 4.2)
dot(p, (B_R, FA_R), THEORY, 4.2)
dot(p, (C_R, FC_R), PRACTICE, 4.4)
p.label(C_R, FC_R, FX + PRIME + "(" + it("c") + ") = 0", 0, -12, PRACTICE, 12.5, "middle", True)
p.label(B_R, FA_R, it("y") + " = " + fof(it("x")), 10, -10, THEORY, 12.5, "start")
save("rolle", figure(
    int(p.x0 + p.w + 40), int(p.y0 + p.h + 40), [p],
    "Rolle teoremi: <em>f</em>(<em>a</em>) = <em>f</em>(<em>b</em>) olduğundan grafik iki uçta aynı "
    "yüksekliktedir. Arada bir <em>c</em> noktasında teğet yataydır, yani <em>f</em>&#8242;(<em>c</em>) = 0 olur.",
    aria="Graph of a differentiable function with equal values at a and b and a horizontal tangent at an "
         "interior point c where f'(c) = 0"))

# ============================================================
# ortalama-deger: the secant from (a, f(a)) to (b, f(b)) and the parallel tangent at c
# ============================================================
A_M, B_M = 0.7, 4.7


def f_mvt(x):
    t = x - A_M
    return 0.8 + 1.15 * t - 0.2 * t * t + 0.012 * t ** 3


def df_mvt(x):
    t = x - A_M
    return 1.15 - 0.4 * t + 0.036 * t * t


FA_M, FB_M = f_mvt(A_M), f_mvt(B_M)
SLOPE_M = (FB_M - FA_M) / (B_M - A_M)
C_M = bisect(lambda x: df_mvt(x) - SLOPE_M, A_M, B_M)
FC_M = f_mvt(C_M)
p = concept_plot(h=245)
y_mark(p, A_M, FA_M, fof(it("a")))
y_mark(p, B_M, FB_M, fof(it("b")))
x_mark(p, A_M, FA_M, it("a"))
x_mark(p, B_M, FB_M, it("b"))
x_mark(p, C_M, FC_M, it("c"), PRACTICE)
p.line([(A_M, FA_M), (B_M, FB_M)], BASE, 2.2)
p.line([(C_M - 1.45, FC_M - 1.45 * SLOPE_M), (C_M + 1.45, FC_M + 1.45 * SLOPE_M)], PRACTICE, 2.2)
p.line(sample(f_mvt, A_M, B_M, 400), THEORY, 2.6)
dot(p, (A_M, FA_M), THEORY, 4.2)
dot(p, (B_M, FB_M), THEORY, 4.2)
dot(p, (C_M, FC_M), PRACTICE, 4.4)
p.label(B_M, FB_M, it("y") + " = " + fof(it("x")), 10, 16, THEORY, 12.5, "start")
legend(p, (("kiriş", BASE, 2.2, None),
           ("teğet, eğimi " + FX + PRIME + "(" + it("c") + ")", PRACTICE, 2.2, None)), p.y0 + p.h + 52)
save("ortalama-deger", figure(
    int(p.x0 + p.w + 40), int(p.y0 + p.h + 66), [p],
    "Ortalama değer teoremi: (<em>a</em>, <em>f</em>(<em>a</em>)) ile (<em>b</em>, <em>f</em>(<em>b</em>)) "
    "noktalarını birleştiren kirişin eğimi (<em>f</em>(<em>b</em>) &#8722; <em>f</em>(<em>a</em>))/(<em>b</em> "
    "&#8722; <em>a</em>)'dır. Arada bir <em>c</em> noktasındaki teğet bu kirişe paraleldir.",
    aria="Graph of a differentiable function on a to b with the secant joining (a, f(a)) and (b, f(b)) and "
         "the parallel tangent line at an interior point c"))

# ============================================================
# ekstrem-deger: interior maximum f(c_2) with f'(c_2) = 0, minimum f(c_1) at the end point b
# ============================================================
A_E, B_E = 0.6, 4.8


def f_evt(x):
    t = (x - A_E) / (B_E - A_E)
    return 1.7 + 1.7 * (4.8 * t - 7.8 * t * t + 2.4 * t ** 3)


C2_E = bisect(lambda x: f_evt(x + 1e-6) - f_evt(x - 1e-6), A_E + 0.3, B_E - 0.5)
MAX_E, MIN_E = f_evt(C2_E), f_evt(B_E)
p = concept_plot()
p.polygon([(A_E, MIN_E), (B_E, MIN_E), (B_E, MAX_E), (A_E, MAX_E)], PRACTICE, 0.07)
y_mark(p, B_E, MAX_E, fof(it("c") + sub("2")), PRACTICE)
y_mark(p, B_E, MIN_E, fof(it("c") + sub("1")), PRACTICE)
x_mark(p, A_E, f_evt(A_E), it("a"))
x_mark(p, C2_E, MAX_E, it("c") + sub("2"), PRACTICE)
x_mark(p, B_E, MIN_E, it("b") + " = " + it("c") + sub("1"), PRACTICE)
p.line([(C2_E - 0.7, MAX_E), (C2_E + 0.7, MAX_E)], PRACTICE, 2.2)
p.line(sample(f_evt, A_E, B_E, 400), THEORY, 2.6)
dot(p, (A_E, f_evt(A_E)), THEORY, 4.2)
dot(p, (C2_E, MAX_E), PRACTICE, 4.6)
dot(p, (B_E, MIN_E), PRACTICE, 4.6)
p.label(C2_E, MAX_E, "maksimum", 0, -12, PRACTICE, 12.5, "middle", True)
p.label(B_E, MIN_E, "minimum", 10, 4.5, PRACTICE, 12.5, "start", True)
p.label(3.3, f_evt(3.3), it("y") + " = " + fof(it("x")), 8, -10, THEORY, 12.5, "start")
save("ekstrem-deger", figure(
    int(p.x0 + p.w + 40), int(p.y0 + p.h + 40), [p],
    "Ekstrem değer teoremi: [<em>a</em>, <em>b</em>] üzerinde sürekli <em>f</em> bütün değerlerini "
    "<em>f</em>(<em>c</em><sub>1</sub>) ile <em>f</em>(<em>c</em><sub>2</sub>) arasında (taralı bant) alır. "
    "Maksimum bir iç noktada alınmıştır ve orada teğet yataydır (<em>f</em>&#8242;(<em>c</em><sub>2</sub>) = 0); "
    "minimum ise <em>b</em> uç noktasında alınmıştır.",
    aria="Graph of a continuous function on a to b whose maximum f(c2) is attained at an interior point with a "
         "horizontal tangent and whose minimum f(c1) is attained at the end point b, the band between them shaded"))

# ============================================================
# ara-deger: the line y = K between f(a) and f(b) meets the graph
# ============================================================
A_I, B_I, K_I = 0.7, 4.7, 1.6


def f_ivt(x):
    t = (x - A_I) / (B_I - A_I)
    return 0.6 + 2.4 * t + 1.0 * math.sin(3 * math.pi * t)


FA_I, FB_I = f_ivt(A_I), f_ivt(B_I)
grid_x = [A_I + (B_I - A_I) * k / 4000 for k in range(4001)]
ROOTS_I = [bisect(lambda x: f_ivt(x) - K_I, u, v) for u, v in zip(grid_x, grid_x[1:])
           if (f_ivt(u) - K_I) * (f_ivt(v) - K_I) < 0]
assert len(ROOTS_I) == 3
p = concept_plot(yr=(-0.4, 4.0), h=295)
p.line([(0, FA_I), (0, FB_I)], PRACTICE, 7, None, 0.3)
y_mark(p, A_I, FA_I, fof(it("a")))
y_mark(p, B_I, FB_I, fof(it("b")))
p.add(f'<line x1="{p.X(0) - 3:.1f}" y1="{p.Y(K_I):.1f}" x2="{p.X(0) + 3:.1f}" y2="{p.Y(K_I):.1f}" '
      f'stroke="{TEXT}" stroke-width="1" opacity="0.75"/>')
p.label(0, K_I, it("K"), -8, 4.5, PRACTICE, 12.5, "end", True)
p.line([(0, K_I), (5.25, K_I)], PRACTICE, 1.8)
x_mark(p, A_I, FA_I, it("a"))
x_mark(p, B_I, FB_I, it("b"))
for k, r in enumerate(ROOTS_I, 1):
    x_mark(p, r, K_I, it("c") + sub(str(k)), PRACTICE)
p.line(sample(f_ivt, A_I, B_I, 500), THEORY, 2.6)
dot(p, (A_I, FA_I), THEORY, 4.2)
dot(p, (B_I, FB_I), THEORY, 4.2)
for r in ROOTS_I:
    dot(p, (r, K_I), PRACTICE, 4.4)
p.label(5.25, K_I, it("y") + " = " + it("K"), 0, -8, PRACTICE, 12.5, "end")
p.label(B_I, FB_I, it("y") + " = " + fof(it("x")), 10, 16, THEORY, 12.5, "start")
save("ara-deger", figure(
    int(p.x0 + p.w + 40), int(p.y0 + p.h + 40), [p],
    "Ara değer teoremi: <em>K</em>, <em>f</em>(<em>a</em>) ile <em>f</em>(<em>b</em>) arasında (eksendeki "
    "kalın parça) olduğundan <em>y</em> = <em>K</em> doğrusu grafiği en az bir noktada keser. Bu grafikte üç kesim "
    "noktası var; <em>c</em><sub>1</sub>, <em>c</em><sub>2</sub>, <em>c</em><sub>3</sub>'ün her biri için "
    "<em>f</em>(<em>c</em>) = <em>K</em> olur.",
    aria="Graph of a continuous function from (a, f(a)) up to (b, f(b)) crossed three times by the horizontal "
         "line y = K, the crossing points c1, c2, c3 marked on the x axis"))

# ============================================================
# taylor: f, P_n and the remainder R_n(x) as the vertical gap at x
# ============================================================
X0_T, XT = 1.3, 3.9


def f_tay(x):
    return 0.45 + 0.32 * math.exp(0.6 * x)


def p_tay(x):
    """Second-order Taylor polynomial of f_tay at X0_T."""
    e = 0.32 * math.exp(0.6 * X0_T)
    h = x - X0_T
    return 0.45 + e * (1 + 0.6 * h + 0.6 ** 2 * h * h / 2)


p = concept_plot(xr=(-0.35, 4.55), yr=(-0.4, 4.6), w=480, h=265)
FX0, FXT, PXT = f_tay(X0_T), f_tay(XT), p_tay(XT)
x_mark(p, X0_T, FX0, it("x") + sub("0"))
x_mark(p, XT, FXT, it("x"))
# the interval between x_0 and x where xi(x) lies
p.line([(X0_T, 0), (XT, 0)], PRACTICE, 7, None, 0.3)
p.label((X0_T + XT) / 2, 0, "ξ(" + it("x") + ") bu aralıkta", 0, -9, PRACTICE, 11.5, "middle")
p.line(sample(p_tay, -0.1, XT + 0.08, 300), PRACTICE, 2.2, "7 4")
p.line(sample(f_tay, -0.1, XT + 0.08, 300), THEORY, 2.6)
y_mark(p, XT, FXT, fof(it("x")), THEORY, 12)
y_mark(p, XT, PXT, it("P") + sub(it("n")) + "(" + it("x") + ")", PRACTICE, 12)
dot(p, (X0_T, FX0), TEXT, 4.2)
p.label(X0_T, FX0, "(" + it("x") + sub("0") + ", " + fof(it("x") + sub("0")) + ")", -8, -10, TEXT, 12, "end")
# the gap R_n(x)
p.add(f'<line x1="{p.X(XT) + 9:.1f}" y1="{p.Y(FXT):.1f}" x2="{p.X(XT) + 9:.1f}" y2="{p.Y(PXT):.1f}" '
      f'stroke="{TEXT}" stroke-width="1.4"/>')
for yv in (FXT, PXT):
    p.add(f'<line x1="{p.X(XT) + 5:.1f}" y1="{p.Y(yv):.1f}" x2="{p.X(XT) + 13:.1f}" y2="{p.Y(yv):.1f}" '
          f'stroke="{TEXT}" stroke-width="1.4"/>')
dot(p, (XT, FXT), THEORY, 4.2)
dot(p, (XT, PXT), PRACTICE, 4.2)
p.label(XT, (FXT + PXT) / 2, it("R") + sub(it("n")) + "(" + it("x") + ")", 18, 4.5, TEXT, 12.5, "start", True)
legend(p, ((it("y") + " = " + fof(it("x")), THEORY, 2.6, None),
           (it("y") + " = " + it("P") + sub(it("n")) + "(" + it("x") + ")", PRACTICE, 2.2, "7 4")), p.y0 + p.h + 52)
save("taylor", figure(
    int(p.x0 + p.w + 90), int(p.y0 + p.h + 66), [p],
    "Taylor teoremi: <em>P<sub>n</sub></em>, <em>f</em>'nin grafiğine (<em>x</em><sub>0</sub>, "
    "<em>f</em>(<em>x</em><sub>0</sub>)) noktasında yapışır. Bir <em>x</em> noktasında iki grafik arasındaki "
    "düşey fark kesme hatası <em>R<sub>n</sub></em>(<em>x</em>) = <em>f</em>(<em>x</em>) &#8722; "
    "<em>P<sub>n</sub></em>(<em>x</em>)'tir; formüldeki &#958;(<em>x</em>), <em>x</em><sub>0</sub> ile "
    "<em>x</em> arasındaki (eksende kalın çizilen) aralıktadır.",
    aria="Graph of a function f and its Taylor polynomial P_n about x0, touching at (x0, f(x0)); at a point x "
         "the vertical gap between the two graphs is marked as the remainder R_n(x), and the interval between "
         "x0 and x, where xi(x) lies, is highlighted on the x axis"))
