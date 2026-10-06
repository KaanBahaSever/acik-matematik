# -*- coding: utf-8 -*-
"""
Figures of the chapter "En Küçük Kareler Yöntemi"
(dersler/numerik-analiz/en-kucuk-kareler-yontemi.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution,
exercise or callout), never inside a definition box and never directly under a
heading. The figures are NOT produced at build time. Run

    python scripts/numerical_figures/ekk.py
    python scripts/center_figures.py "numerical-ekk-*.md"
    python scripts/check_figure_labels.py "scripts/_figures/numerical-ekk-*.md"

and paste the markup of scripts/_figures/numerical-ekk-<name>.md into the .qmd.
Captions are Turkish on purpose; aria labels are plain ASCII.

The regression coefficients are recomputed here from the normal equations with
exact fractions, so the drawn lines are the ones derived in the chapter.

The 3-D graph of E(a, b) is a translucent surface with a sparse wire net. The
wires and the axis are split into the parts the viewer sees and the parts
hidden by the surface (a ray is cast from each sample toward the camera):
hidden parts are painted faintly before the surface, visible parts after it.
The level curves on the floor are exact ellipses: with u = a - 2, v = b - 1 the
quadratic part is 25u^2 + 10uv + 5v^2 = 25(u + v/5)^2 + 4v^2.
"""
import html
import math
import re
import sys
from fractions import Fraction as F
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, dot, hollow, TEXT, THEORY, PRACTICE, BASE, REMARK, BG  # noqa: E402
from svg_plot3 import Camera, Space  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "numerical-ekk-"

MINUS = "&#8722;"
SUBS = {"1": "&#8321;", "2": "&#8322;", "3": "&#8323;", "4": "&#8324;"}
YHAT = "ŷ"


def save(name, markup):
    (OUT_DIR / f"{PREFIX}{name}.md").write_text(markup, encoding="utf-8", newline="\n")
    print(f"{PREFIX}{name}.md")


def it(s):
    """Italic run inside an SVG <text>."""
    return f'<tspan font-style="italic">{s}</tspan>'


def dec(v, digits=2):
    """Decimal comma and a true minus sign: -0.5 -> '−0,5'."""
    s = f"{v:.{digits}f}".rstrip("0").rstrip(".")
    if s in ("-0", ""):
        s = "0"
    return s.replace(".", ",").replace("-", MINUS)


def fixed(v, digits):
    """Fixed number of decimals with a decimal comma: 0.0451 -> '0,0451'."""
    return f"{v:.{digits}f}".replace(".", ",").replace("-", MINUS)


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


def regression(xs, ys):
    """Slope and intercept from the normal equations, in exact fractions."""
    n = len(xs)
    sx, sy = sum(xs), sum(ys)
    sxx = sum(x * x for x in xs)
    sxy = sum(x * y for x, y in zip(xs, ys))
    det = sxx * n - sx * sx
    return (n * sxy - sx * sy) / det, (sxx * sy - sx * sxy) / det


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


# ============================================================
# artiklar: the four points, the regression line and the residuals
# ============================================================
XS = [F(-1), F(-1, 10), F(2, 10), F(1)]
YS = [F(1), F(1099, 1000), F(808, 1000), F(1)]
A1, B1 = regression(XS, YS)
assert A1 == F(-613, 27300)


def line1(x):
    return float(A1) * x + float(B1)


XR1, YR1 = (-1.2, 1.2), (0.75, 1.15)
p = Plot(60, 30, 430, 280, XR1, YR1)
xt = (-1, -0.5, 0, 0.5, 1)
yt = (0.8, 0.9, 1.0, 1.1)
p.axes(xt, yt, it("x"), it("y"), dec, dec)
p.grid(xt, yt)
p.line([(XR1[0], line1(XR1[0])), (XR1[1], line1(XR1[1]))], THEORY, 2.0)
# residual labels: (dx, dy, anchor) chosen per point so they keep clear of the line and the points
PLACES = ((10, -6, "start"), (-9, 4, "end"), (9, 4, "start"), (-9, -10, "end"))
for k, (x, y) in enumerate(zip(XS, YS)):
    x, y = float(x), float(y)
    yh = line1(x)
    q = y - yh
    p.line([(x, y), (x, yh)], PRACTICE, 1.8, "5 3")
    hollow(p, (x, yh), THEORY, 3.4, 1.4)
    dot(p, (x, y), TEXT, 4.2)
    dx, dy, anc = PLACES[k]
    s = it("q") + SUBS[str(k + 1)] + " ≈ " + fixed(q, 4)
    plabel(p, x, (y + yh) / 2, s, dx, dy, PRACTICE, 12, anc)
plabel(p, -1.12, 0.925, YHAT + " = " + MINUS + "0,0225" + it("x") + " + 0,9773", 0, 0, THEORY, 12.5,
       "start", True)
E1 = sum((float(y) - line1(float(x))) ** 2 for x, y in zip(XS, YS))
assert abs(E1 - 0.0435) < 5e-5
save("artiklar", figure(
    int(p.x0 + p.w + 40), int(p.y0 + p.h + 40), [p],
    "Dört veri noktası (dolu daireler) ve regresyon doğrusu <em>ŷ</em> = &#8722;0,0225<em>x</em> + 0,9773. "
    "Doğru üzerindeki içi boş daireler <em>ŷ</em><sub><em>i</em></sub> tahmini değerleridir. Kesikli "
    "parçalar <em>q</em><sub><em>i</em></sub> = <em>y</em><sub><em>i</em></sub> &#8722; "
    "<em>ŷ</em><sub><em>i</em></sub> artıklarıdır: her nokta ile doğru arasındaki dikey uzaklık. "
    "<em>E</em>, bu dört parçanın uzunluklarının karelerinin toplamıdır: <em>E</em> &#8776; 0,0435.",
    aria="Four data points with the regression line y = -0.0225x + 0.9773 and dashed vertical residual "
         "segments from each point to the line, labelled q1 to q4"))

# ============================================================
# e-yuzeyi: E(a, b) = 25a^2 + 10ab + 5b^2 - 110a - 30b + 125 over [0, 4] x [-3, 5]
# ============================================================
AR, BR = (0.0, 4.0), (-3.0, 5.0)
ZS = 1 / 50          # one unit of height per 50 units of E


def E(a, b):
    return 25 * a * a + 10 * a * b + 5 * b * b - 110 * a - 30 * b + 125


assert [E(*q) for q in ((0, -3), (4, 5), (0, 5), (4, -3), (2, 1), (0, 0), (3, 1), (2, 3))] == \
    [260, 260, 100, 100, 0, 125, 25, 20]


def h(a, b):
    return E(a, b) * ZS


def in_rect(a, b):
    return AR[0] <= a <= AR[1] and BR[0] <= b <= BR[1]


def level_ellipse(c, n=360):
    """E(a, b) = c: 25(u + v/5)^2 + 4v^2 = c with u = a - 2, v = b - 1."""
    pts = []
    for k in range(n + 1):
        t = 2 * math.pi * k / n
        v = math.sqrt(c) / 2 * math.sin(t)
        u = math.sqrt(c) / 5 * math.cos(t) - v / 5
        pts.append((2 + u, 1 + v))
    return pts


class GraphScene:
    """Collects strokes, sorts them into hidden (painted before the surface)
    and visible parts (painted after it)."""

    def __init__(self, S, height, inside, reach=12.0):
        self.S = S
        self.h = height
        self.inside = inside
        self.reach = reach
        self.back, self.front = [], []

    def hidden(self, P, eps=0.01, n=600):
        """Does the surface lie between P and the viewer?"""
        d = self.S.cam.d
        prev = None
        for k in range(n + 1):
            t = eps + (self.reach - eps) * k / n
            x, y, z = P[0] + t * d[0], P[1] + t * d[1], P[2] + t * d[2]
            if not self.inside(x, y):
                prev = None
                continue
            g = z - self.h(x, y)
            if prev is not None and g * prev < 0:
                return True
            prev = g
        return False

    def polyline(self, pts, color, width, opacity=1.0, hidden_opacity=0.3, dash=None):
        """Split a sampled space curve at the changes of visibility."""
        flags = [self.hidden(tuple((a + b) / 2 for a, b in zip(P, Q))) for P, Q in zip(pts, pts[1:])]
        start = 0
        for k in range(1, len(flags) + 1):
            if k == len(flags) or flags[k] != flags[start]:
                run = pts[start:k + 1]
                if flags[start]:
                    self.back.append(lambda run=run: self.S.line(run, color, width, dash,
                                                                 opacity * hidden_opacity))
                else:
                    self.front.append(lambda run=run: self.S.line(run, color, width, dash, opacity))
                start = k

    def curve(self, f, t0, t1, color, width, samples=160, **kw):
        self.polyline([f(t0 + (t1 - t0) * k / samples) for k in range(samples + 1)], color, width, **kw)

    def render(self, draw_surface):
        for f in self.back:
            f()
        draw_surface()
        for f in self.front:
            f()


cam = Camera(azimuth=-58.0, elevation=27.0)
ZTOP = 300 * ZS
corners = [(a, b) for a in AR for b in BR]
box = [(a, b, 0.0) for a, b in corners] + [(a, b, h(a, b)) for a, b in corners] + [(0, -3, ZTOP + 0.3)]
q = [cam.project(P)[:2] for P in box]
PAD = 0.35
xr = (min(x for x, _ in q) - PAD, max(x for x, _ in q) + PAD)
yr = (min(y for _, y in q) - PAD, max(y for _, y in q) + PAD)
PPU = 58
pe = Plot(40, 20, (xr[1] - xr[0]) * PPU, (yr[1] - yr[0]) * PPU, xr, yr)
S = Space(pe, cam)
G = GraphScene(S, h, in_rect)

# floor: outline of the domain and the exact level ellipses E = 5, 20, 50, 100, 200 (cut to the domain)
LEVELS = (5, 20, 50, 100, 200)
S.line([(0, -3, 0), (4, -3, 0), (4, 5, 0), (0, 5, 0), (0, -3, 0)], TEXT, 1.0, None, 0.5)
for c in LEVELS:
    for run in clip_polyline(level_ellipse(c), AR, BR):
        S.line([(a, b, 0.0) for a, b in run], BASE, 1.5, None, 0.95)

# vertical E axis at the corner (0, -3) and its ticks
G.polyline([(0, -3, z * ZTOP / 60) for z in range(61)], TEXT, 1.1, 0.7, 0.45)
G.front.append(lambda: S.arrow((0, -3, ZTOP - 0.2), (0, -3, ZTOP + 0.3), TEXT, 1.1, 7.0, None, 0.7))
for v in (100, 200):
    S.line([(0, -3, v * ZS), (0, -3.15, v * ZS)], TEXT, 1.0, None, 0.7)
    S.label((0, -3.15, v * ZS), str(v), -5, 4, TEXT, 10.5, "end")
S.label((0, -3, ZTOP + 0.3), it("E"), 0, -8, TEXT, 13, "middle")
# ticks on the floor edges b = -3 (for a) and a = 4 (for b)
for v in range(5):
    S.line([(v, -3, 0), (v, -3.15, 0)], TEXT, 1.0, None, 0.7)
    S.label((v, -3.15, 0), str(v), -6, 12, TEXT, 10.5, "middle")
for v in (-3, -1, 1, 3, 5):
    S.line([(4, v, 0), (4.15, v, 0)], TEXT, 1.0, None, 0.7)
    S.label((4.15, v, 0), dec(v), 8, 10, TEXT, 10.5, "middle")
S.label((2, -3.6, 0), it("a"), -8, 16, TEXT, 13, "middle")
S.label((4.6, 1, 0), it("b"), 12, 14, TEXT, 13, "middle")

# sparse wire net on the surface
for k in range(9):
    a = k / 2
    G.curve(lambda t, a=a: (a, t, h(a, t)), BR[0], BR[1], THEORY, 0.7, 80, opacity=0.6, hidden_opacity=0.3)
for k in range(9):
    b = -3 + k
    G.curve(lambda t, b=b: (t, b, h(t, b)), AR[0], AR[1], THEORY, 0.7, 60, opacity=0.6, hidden_opacity=0.3)
# the rim of the surface, a little heavier
for pts in ([(t / 40 * 4, -3) for t in range(41)], [(4, -3 + t / 40 * 8) for t in range(41)],
            [(4 - t / 40 * 4, 5) for t in range(41)], [(0, 5 - t / 40 * 8) for t in range(41)]):
    G.polyline([(a, b, h(a, b)) for a, b in pts], THEORY, 1.3, 0.9, 0.4)


def draw_bowl():
    S.surface(lambda u, v: (u, v, h(u, v)), AR, BR, nu=16, nv=32, fill=THEORY, stroke=THEORY,
              opacity=(0.05, 0.2), stroke_width=0.3, stroke_opacity=0.06)


G.render(draw_bowl)

# level labels on the floor, along the ray from (2, 1) toward the corner (4, 5)
for c in LEVELS:
    s = math.sqrt(c / E(4, 5))          # E(2 + 2s, 1 + 4s) = 260 s^2 along this ray
    P = (2 + 2 * s, 1 + 4 * s, 0.0)
    X, Y = S.pt(P)
    plabel(pe, X, Y, str(c), 0, 4, BASE, 10.5, "middle", True)
# the minimum, with a leader to a free spot below the floor
S.point((2, 1, 0), PRACTICE, 4.6)
MX, MY = S.pt((2, 1, 0))
pe.line([(MX, MY + 0.08), (MX - 0.25, MY + 0.75)], PRACTICE, 1.0, None, 0.9)
plabel(pe, MX - 0.25, MY + 0.75, "minimum: " + it("E") + "(2, 1) = 0", 0, -5, PRACTICE, 12.5, "middle", True)

save("e-yuzeyi", figure(
    int(pe.x0 + pe.w + 40), int(pe.y0 + pe.h + 30), [pe],
    "<em>E</em>(<em>a</em>, <em>b</em>) = 25<em>a</em>² + 10<em>ab</em> + 5<em>b</em>² &#8722; 110<em>a</em> "
    "&#8722; 30<em>b</em> + 125 yüzeyinin 0 &#8804; <em>a</em> &#8804; 4, &#8722;3 &#8804; <em>b</em> &#8804; 5 "
    "üzerindeki parçası. Köşelerde <em>E</em> 100 ile 260 arasındadır. Tabandaki eğik elipsler <em>E</em> = 5; "
    "20; 50; 100; 200 seviye eğrileridir ve hepsi (2, 1) noktasını çevreler. Yüzeyin tek bir çukuru vardır; "
    "normal denklemlerin çözümü olan (2, 1) bu çukurun dibidir ve orada <em>E</em> = 0 olur. Yüzeyin arkasında "
    "kalan çizgiler soluk çizilmiştir.",
    aria="Elliptic paraboloid E(a, b) over a from 0 to 4 and b from -3 to 5 with level ellipses E = 5, 20, 50, "
         "100, 200 on the floor around (2, 1) and the minimum E(2, 1) = 0 marked"))

# ============================================================
# not-tahmini: the grade data, the regression line and the prediction at x = 60
# ============================================================
GX = [75, 80, 93, 65, 87, 71, 98, 68, 84, 77]
GY = [82, 78, 86, 72, 91, 80, 95, 72, 89, 74]
A2, B2 = regression([F(v) for v in GX], [F(v) for v in GY])
assert (A2, B2) == (F(41, 62), F(903, 31))


def line2(x):
    return float(A2) * x + float(B2)


Y60 = line2(60)
XR2, YR2 = (55, 100), (60, 100)
g = Plot(60, 30, 430, 300, XR2, YR2)
g.axes((55, 60, 70, 80, 90, 100), (60, 70, 80, 90, 100), "", "", dec, dec)
g.grid((60, 70, 80, 90, 100), (70, 80, 90, 100))
g.label(100, 60, "Matematik (" + it("x") + ")", 0, 34, TEXT, 12, "end")
g.text_px(g.x0 - 4, g.y0 - 14, "Fizik (" + it("y") + ")", TEXT, 12, "start")
g.line([(55, line2(55)), (100, line2(100))], THEORY, 2.0)
g.line([(55, Y60), (60, Y60), (60, 60)], PRACTICE, 1.1, "4 3", 0.85)
for x, y in zip(GX, GY):
    dot(g, (x, y), TEXT, 4.0)
dot(g, (60, Y60), PRACTICE, 5.0)
plabel(g, 60, Y60, it("x") + " = 60 için " + it("y") + " ≈ 68,81", 9, 17, PRACTICE, 12.5, "start", True)
plabel(g, 57, 84, it("y") + " = 0,6613" + it("x") + " + 29,1290", 0, 0, THEORY, 12.5, "start", True)

save("not-tahmini", figure(
    int(g.x0 + g.w + 40), int(g.y0 + g.h + 50), [g],
    "On öğrencinin (Matematik, Fizik) notları ve regresyon doğrusu <em>y</em> = 0,6613<em>x</em> + 29,1290. "
    "Matematik notu 60 olan öğrencinin Fizik notu tahmini doğru üzerindeki noktadan okunur: "
    "<em>y</em> &#8776; 68,81, yani yaklaşık 69.",
    aria="Scatter plot of ten math and physics grades with the regression line y = 0.6613x + 29.1290 and the "
         "predicted point at x = 60, y about 68.81, with dashed guides to both axes"))

# ============================================================
# genel-artiklar: generic picture of the method, points (x_i, y_i), the line y^ = ax + b, y^_i and q_i
# ============================================================
def sb(s_, size=9):
    """Subscript inside an SVG <text>; the zero-width space resets the baseline."""
    return f'<tspan font-size="{size}" dy="3.5">{s_}</tspan><tspan dy="-3.5">&#8203;</tspan>'


GXS = [F(1), F(17, 10), F(29, 10), F(375, 100), F(46, 10)]
GYS = [F(1), F(23, 10), F(2), F(37, 10), F(31, 10)]
GA, GB = regression(GXS, GYS)
GQ = [y - GA * x - GB for x, y in zip(GXS, GYS)]
assert sum(GQ) == 0 and min(abs(float(q)) for q in GQ) > 0.3


def gline(x):
    return float(GA) * x + float(GB)


IDX = ["1", "2", "3", None, it("n")]       # the fourth point stands for the ones between x_3 and x_n
p = Plot(50, 30, 420, 280, (0, 5.4), (0, 4.6))
p.axes((), (), it("x"), it("y"))
p.line([(0.3, gline(0.3)), (5.1, gline(5.1))], THEORY, 2.2)
p.label(5.1, gline(5.1), YHAT + " = " + it("a") + it("x") + " + " + it("b"), 6, -8, THEORY, 12.5, "end", True)
for k, (x, y) in enumerate(zip(GXS, GYS)):
    x, y = float(x), float(y)
    yh = gline(x)
    up = y > yh
    Y = p.y0 + p.h
    p.add(f'<line x1="{p.X(x):.1f}" y1="{Y - 4:.1f}" x2="{p.X(x):.1f}" y2="{Y + 4:.1f}" stroke="{TEXT}" '
          f'stroke-width="1.1" opacity="0.7"/>')
    p.line([(x, y), (x, yh)], PRACTICE, 2.0)
    hollow(p, (x, yh), THEORY, 3.6, 1.6)
    dot(p, (x, y), TEXT, 4.4)
    i = IDX[k]
    if i is None:
        p.text_px(p.X(x), Y + 19, "&#8230;", TEXT, 12.5, "middle")
        continue
    p.text_px(p.X(x), Y + 19, it("x") + sb(i), TEXT, 12.5, "middle")
    # the residual beside its segment on the side away from the rising line, the data point beyond its end
    if up:
        p.label(x, (y + yh) / 2, it("q") + sb(i), -7, 5, PRACTICE, 12.5, "end", True)
    else:
        p.label(x, (y + yh) / 2, it("q") + sb(i), 7, 5, PRACTICE, 12.5, "start", True)
    p.label(x, y, "(" + it("x") + sb(i) + ", " + it("y") + sb(i) + ")", 0, -11 if up else 21, TEXT, 12, "middle")
    # y^_i away from the rising line: below right if the point is above, above left otherwise
    if up:
        p.label(x, yh, YHAT + sb(i), 8, 17, THEORY, 12.5, "start")
    else:
        p.label(x, yh, YHAT + sb(i), -8, -9, THEORY, 12.5, "end")
save("genel-artiklar", figure(
    int(p.x0 + p.w + 40), int(p.y0 + p.h + 40), [p],
    "Veri noktaları (<em>x</em><sub><em>i</em></sub>, <em>y</em><sub><em>i</em></sub>) (dolu daireler), "
    "<em>ŷ</em> = <em>ax</em> + <em>b</em> doğrusu ve doğru üzerindeki <em>ŷ</em><sub><em>i</em></sub> = "
    "<em>ax</em><sub><em>i</em></sub> + <em>b</em> tahmini değerleri (içi boş daireler). Dikey parçalar "
    "<em>q</em><sub><em>i</em></sub> = <em>y</em><sub><em>i</em></sub> &#8722; <em>ŷ</em><sub><em>i</em></sub> "
    "farklarıdır; en küçük kareler yöntemi bu parçaların uzunluklarının karelerinin toplamı <em>E</em>'yi "
    "en küçük yapan doğruyu seçer.",
    aria="Data points (x_i, y_i) scattered around the line y = ax + b, the fitted values on the line marked as "
         "hollow circles and the vertical deviations q_1, q_2, q_3, ..., q_n between each point and the line"))
