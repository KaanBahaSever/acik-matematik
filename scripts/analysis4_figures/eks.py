# -*- coding: utf-8 -*-
"""
Figures of the chapter "Yerel Ekstremumlar"
(dersler/analiz-4/yerel-ekstremumlar.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box and never directly under a heading.
The figures are NOT produced at build time. Run

    python scripts/analysis4_figures/eks.py
    python scripts/center_figures.py "analysis4-eks-*.md"
    python scripts/check_figure_labels.py "scripts/_figures/analysis4-eks-*.md"

and paste the markup of scripts/_figures/analysis4-eks-<name>.md into the .qmd.
Captions are Turkish on purpose; aria labels are plain ASCII.

The 3-D graphs are translucent surfaces with a sparse wire net. Curves, axes
and wires are split into the parts the viewer sees and the parts hidden by the
surface (a ray is cast from each sample toward the camera): hidden parts are
painted faintly before the surface, visible parts after it. Level curves are
exact: each one is solved in polar coordinates, r^2 being a root of a
quadratic, and never traced from a grid.
"""
import html
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, dot, TEXT, THEORY, PRACTICE, BASE, BG, WIDE  # noqa: E402
from svg_plot3 import Camera, Space  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "analysis4-eks-"

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


def eq_plot(x0, y0, ppu, xr, yr):
    """Panel with the same number of pixels per unit on both axes."""
    return Plot(x0, y0, (xr[1] - xr[0]) * ppu, (yr[1] - yr[0]) * ppu, xr, yr)


def fit_space(cam, pts, x0, y0, ppu, pad=0.12):
    """Equal-aspect panel just large enough for the projections of pts."""
    q = [cam.project(P)[:2] for P in pts]
    xr = (min(a for a, _ in q) - pad, max(a for a, _ in q) + pad)
    yr = (min(b for _, b in q) - pad, max(b for _, b in q) + pad)
    plot = eq_plot(x0, y0, ppu, xr, yr)
    return plot, Space(plot, cam)


def dec(v):
    """Decimal comma and a true minus sign: -0.5 -> '−0,5'."""
    s = f"{v:.2f}".rstrip("0").rstrip(".")
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


# ---------------------------------------------------------------------------
# hidden-line handling for the graph z = h(x, y) of a function on a convex domain
# ---------------------------------------------------------------------------
class GraphScene:
    """Collects strokes, sorts them into hidden (painted before the surface)
    and visible parts (painted after it)."""

    def __init__(self, S, height, inside, reach=8.0):
        self.S = S
        self.h = height
        self.inside = inside
        self.reach = reach
        self.back, self.front = [], []

    def hidden(self, P, eps=0.01, n=500):
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

    def axis(self, a, b, label, off, color=TEXT, width=1.1, opacity=0.6):
        """Axis from a to b (arrowhead at b), drawn in pieces by visibility."""
        L = math.dist(a, b)
        n = max(8, int(L * 60))
        head = 0.1 * L if L > 0 else 0
        stop = tuple(b[i] - (b[i] - a[i]) * head / L for i in range(3))
        self.polyline([tuple(a[i] + (stop[i] - a[i]) * k / n for i in range(3)) for k in range(n + 1)],
                      color, width, opacity, hidden_opacity=0.45)
        target = self.back if self.hidden(b) else self.front
        target.append(lambda: self.S.arrow(stop, b, color, width, 7.0, None, opacity))
        if label:
            target.append(lambda: self.S.label(b, it(label), off[0], off[1], color, 12.5, "middle"))

    def render(self, draw_surface):
        for f in self.back:
            f()
        draw_surface()
        for f in self.front:
            f()


# ============================================================
# eyer-yuzeyi: z = y^2 - x^2 over [-1, 1]^2
# ============================================================
def saddle(x, y):
    return y * y - x * x


def in_square(x, y, a=1.0):
    return -a <= x <= a and -a <= y <= a


cam = Camera(azimuth=35.0, elevation=24.0)
AX = 1.65
box = [(sx, sy, saddle(sx, sy)) for sx in (-1, 1) for sy in (-1, 1)]
box += [(1, 0, -1), (-1, 0, -1), (0, 1, 1), (0, -1, 1), (AX, 0, 0), (0, AX, 0), (0, 0, 1.55),
        (-1.25, 0, 0), (0, -1.25, 0), (0, 0, -1.2)]
pl, S = fit_space(cam, box, 30, 30, 150, 0.2)
G = GraphScene(S, saddle, in_square)
# sparse wire net: every 0.25 in x and y
for k in range(9):
    c = -1 + k / 4
    G.curve(lambda t, c=c: (c, t, saddle(c, t)), -1, 1, THEORY, 0.7, 60, opacity=0.55, hidden_opacity=0.35)
    G.curve(lambda t, c=c: (t, c, saddle(t, c)), -1, 1, THEORY, 0.7, 60, opacity=0.55, hidden_opacity=0.35)
# the coordinate axes
G.axis((-1.25, 0, 0), (AX, 0, 0), "x", (-6, 14))
G.axis((0, -1.25, 0), (0, AX, 0), "y", (10, 4))
G.axis((0, 0, -1.2), (0, 0, 1.55), "z", (-9, -3))
# the two parabolas through the saddle point
G.curve(lambda t: (t, 0.0, -t * t), -1, 1, PRACTICE, 2.8, 120, hidden_opacity=0.4)
G.curve(lambda t: (0.0, t, t * t), -1, 1, BASE, 2.8, 120, hidden_opacity=0.4)


def draw_saddle():
    S.surface(lambda u, v: (u, v, saddle(u, v)), (-1, 1), (-1, 1), nu=24, nv=24, fill=THEORY, stroke=THEORY,
              opacity=(0.05, 0.2), stroke_width=0.3, stroke_opacity=0.06)


G.render(draw_saddle)
S.point((0, 0, 0), TEXT, 4.2)
X_, Y_, Z_ = it("x"), it("y"), it("z")
S.label((1, 0, -1), Z_ + " = " + MINUS + X_ + sup("2"), -10, 8, PRACTICE, 12.5, "end", True)
S.label((0, 1, 1), Z_ + " = " + Y_ + sup("2"), 10, 4, BASE, 12.5, "start", True)
X, Y = S.pt((0, 0, 0))
plabel(pl, X, Y, "eyer noktası", 0, -12, TEXT, 12, "middle")
save("eyer-yuzeyi", figure(
    int(pl.x0 + pl.w + 40), int(pl.y0 + pl.h + 25), [pl],
    "<em>z</em> = <em>y</em>² &#8722; <em>x</em>² yüzeyi (&#8722;1 &#8804; <em>x</em>, <em>y</em> &#8804; 1). "
    "<em>x</em> ekseni üzerindeki <em>z</em> = &#8722;<em>x</em>² parabolü aşağı, <em>y</em> ekseni üzerindeki "
    "<em>z</em> = <em>y</em>² parabolü yukarı açılır. Orijin, ilk parabolün en yüksek, ikincisinin en alçak "
    "noktasıdır. "
    "Yüzeyin arkasında kalan çizgiler soluk çizilmiştir.",
    aria="Saddle surface z = y^2 - x^2 over the square from -1 to 1, with the downward parabola z = -x^2 "
         "along the x axis, the upward parabola z = y^2 along the y axis and the saddle point at the origin"))

# ============================================================
# paraboloid: z = x^2 + y^2 over the disc of radius 1.5
# ============================================================
RD = 1.5


def bowl(x, y):
    return x * x + y * y


def in_disc(x, y):
    return x * x + y * y <= RD * RD


def polar_bowl(r, phi):
    return (r * math.cos(phi), r * math.sin(phi), r * r)


cam = Camera(azimuth=35.0, elevation=22.0)
ZA = 3.0
box = [polar_bowl(RD, k * math.pi / 18) for k in range(36)]
box += [(2.1, 0, 0), (0, 2.2, 0), (0, 0, ZA), (-1.9, 0, 0), (0, -1.9, 0)]
pl, S = fit_space(cam, box, 90, 30, 112, 0.2)
G = GraphScene(S, bowl, in_disc)
# sparse wire net: level circles z = 0.5, 1, 1.5, 2 and the rim z = 2.25, meridians every 30 degrees
LEVELS = (0.5, 1.0, 1.5, 2.0)
for c in LEVELS:
    rc = math.sqrt(c)
    G.curve(lambda t, rc=rc: polar_bowl(rc, t), 0, 2 * math.pi, THEORY, 0.9, 144, opacity=0.8,
            hidden_opacity=0.4)
G.curve(lambda t: polar_bowl(RD, t), 0, 2 * math.pi, THEORY, 1.3, 144, opacity=0.9, hidden_opacity=0.5)
for k in range(12):
    phi = k * math.pi / 6
    G.curve(lambda r, phi=phi: polar_bowl(r, phi), 0, RD, THEORY, 0.6, 40, opacity=0.4, hidden_opacity=0.35)
G.axis((-1.9, 0, 0), (2.1, 0, 0), "x", (-6, 14))
G.axis((0, -1.9, 0), (0, 2.2, 0), "y", (10, 4))
G.axis((0, 0, 0), (0, 0, ZA), "z", (-9, -3))


def draw_bowl():
    S.surface(polar_bowl, (0, RD), (0, 2 * math.pi), nu=12, nv=48, fill=THEORY, stroke=THEORY,
              opacity=(0.05, 0.2), stroke_width=0.3, stroke_opacity=0.06)


G.render(draw_bowl)
S.point((0, 0, 0), PRACTICE, 4.4)
for c in (1.0, 2.0):
    rc = math.sqrt(c)
    S.label(polar_bowl(rc, math.radians(115)), Z_ + " = " + dec(c), 8, 4, THEORY, 11.5)
# the label sits left of the origin, in the free wedge between the -y and the +x axis
OX, OY = S.pt((0, 0, 0))
pl.line([(OX - 44 / pl.w * (pl.xmax - pl.xmin), OY - 8 / pl.h * (pl.ymax - pl.ymin)),
         (OX - 7 / pl.w * (pl.xmax - pl.xmin), OY - 2 / pl.h * (pl.ymax - pl.ymin))], PRACTICE, 0.9, None, 0.8)
S.label((0, 0, 0), "kesin yerel (mutlak) minimum", -48, 13, PRACTICE, 12, "end", True)
save("paraboloid", figure(
    int(pl.x0 + pl.w + 40), int(pl.y0 + pl.h + 30), [pl],
    "<em>z</em> = <em>x</em>² + <em>y</em>² dönel paraboloidinin <em>x</em>² + <em>y</em>² &#8804; 2,25 "
    "diski üzerindeki parçası. İnce çemberler <em>z</em> = 0,5; 1; 1,5; 2 seviyelerindedir. Yüzeyin en alt "
    "noktası orijindir: <em>f</em>(0, 0) = 0 kesin ve mutlak minimum değeridir.",
    aria="Paraboloid z = x^2 + y^2 over the disc of radius 1.5 with horizontal level circles and the lowest "
         "point, the strict absolute minimum, marked at the origin"))

# ============================================================
# dort-kuvvet: level curves of f = x^4 + y^4 - 4xy + 1
# ============================================================
# In polar coordinates f = A s^2 - B s + 1 with s = r^2, A = cos^4 + sin^4, B = 2 sin(2 theta);
# the level f = c is a root of A s^2 - B s + (1 - c) = 0.
W4 = 1.8


def quartic(x, y):
    return x ** 4 + y ** 4 - 4 * x * y + 1


def level_roots(c, th):
    ct, st = math.cos(th), math.sin(th)
    A, B = ct ** 4 + st ** 4, 2 * math.sin(2 * th)
    disc = B * B - 4 * A * (1 - c)
    if disc < 0:
        return None
    q = math.sqrt(disc)
    return ((B - q) / (2 * A), (B + q) / (2 * A))


def polar_pt(s, th):
    r = math.sqrt(max(s, 0.0))
    return (r * math.cos(th), r * math.sin(th))


def theta_window(c, lo, hi):
    """The theta interval inside (lo, hi) where disc >= 0 (bisection on both ends)."""
    mid = (lo + hi) / 2

    def ok(t):
        return level_roots(c, t) is not None

    def edge(a, b):                       # ok(a) is False, ok(b) is True
        for _ in range(80):
            m = (a + b) / 2
            if ok(m):
                b = m
            else:
                a = m
        return b
    return edge(lo, mid), edge(hi, mid)


def level_curves(c, n=720):
    """Closed polylines of the level set f = c (c > -1)."""
    curves = []
    if c > 1:                             # one star-shaped curve around the origin
        pts = []
        for k in range(n + 1):
            th = 2 * math.pi * k / n
            pts.append(polar_pt(level_roots(c, th)[1], th))
        curves.append(pts)
    elif c == 1:                          # the figure eight s = B / A (two lobes)
        for base in (0.0, math.pi):
            pts = []
            for k in range(n + 1):
                th = base + (math.pi / 2) * k / n
                ct, st = math.cos(th), math.sin(th)
                pts.append(polar_pt(2 * math.sin(2 * th) / (ct ** 4 + st ** 4), th))
            curves.append(pts)
    else:                                 # two ovals, one in the first and one in the third quadrant
        for base in (0.0, math.pi):
            t0, t1 = theta_window(c, base, base + math.pi / 2)
            # cosine spacing clusters samples where the two roots meet
            ths = [t0 + (t1 - t0) * (1 - math.cos(math.pi * k / n)) / 2 for k in range(n + 1)]
            inner = [polar_pt(level_roots(c, t)[0], t) for t in ths]
            outer = [polar_pt(level_roots(c, t)[1], t) for t in ths]
            curves.append(inner + outer[::-1] + [inner[0]])
    return curves


p = eq_plot(50, 70, 112, (-W4, W4), (-W4, W4))
p.polygon([(-W4, -W4), (W4, -W4), (W4, W4), (-W4, W4)], TEXT, 0.0, TEXT, 0.8)
p.origin_axes(it("x"), it("y"), (-1, 1), (-1, 1), dec, dec, opacity=0.45)
p.line([(-W4, -W4), (W4, W4)], TEXT, 1.0, "5 4", 0.6)
for c in (-0.5, 0.0, 0.5, 2.0, 4.0, 8.0):
    for curve in level_curves(c):
        for run in clip_polyline(curve, (-W4, W4), (-W4, W4)):
            p.line(run, THEORY, 1.3, None, 0.9)
for curve in level_curves(1.0):
    p.line(curve, PRACTICE, 2.6)
# inline level labels: 2, 4, 8 on the diagonal y = -x, the ovals and the figure eight in the third quadrant
for c in (2.0, 4.0, 8.0):
    th = 0.75 * math.pi
    x, y = polar_pt(level_roots(c, th)[1], th)
    plabel(p, x, y, dec(c), 0, 4, THEORY, 11, "middle")
for c in (-0.5, 0.0, 0.5):
    th = 1.25 * math.pi + 0.05
    x, y = polar_pt(level_roots(c, th)[0], th)
    plabel(p, x, y, dec(c), 0, 4, THEORY, 11, "middle")
th = math.radians(200)
x, y = polar_pt(2 * math.sin(2 * th) / (math.cos(th) ** 4 + math.sin(th) ** 4), th)
plabel(p, x, y, "1", 0, 4, PRACTICE, 11.5, "middle", True)
# critical points, with leaders to labels outside the frame
for (cx, cy), sgn in (((1, 1), 1), ((-1, -1), -1)):
    edge = sgn * (W4 + 0.12)
    p.line([(cx, cy + sgn * 0.06), (cx, edge)], TEXT, 0.9, None, 0.65)
    dot(p, (cx, cy), TEXT, 4.2)
    dy = -8 if sgn > 0 else 17
    p.label(cx, edge, "yerel minimum, " + it("f") + " = " + MINUS + "1", 0, dy, TEXT, 12, "middle")
dot(p, (0, 0), TEXT, 4.2)
p.label(0, 0, "eyer noktası,", 9, 22, TEXT, 12)
p.label(0, 0, it("f") + " = 1", 9, 37, TEXT, 12)
save("dort-kuvvet", figure(
    int(p.x0 + p.w + 50), int(p.y0 + p.h + 60), [p],
    "<em>f</em>(<em>x</em>, <em>y</em>) = <em>x</em><sup>4</sup> + <em>y</em><sup>4</sup> &#8722; 4<em>xy</em> + 1 "
    "fonksiyonunun &#8722;0,5; 0; 0,5; 1; 2; 4; 8 seviye eğrileri. Kalın sekiz biçimli eğri <em>f</em> = 1 "
    "seviyesidir ve eyer noktası olan orijinden geçer. Bu seviyenin altındaki eğriler (1, 1) ve "
    "(&#8722;1, &#8722;1) minimumlarını ayrı ayrı çevreler, üstündekiler ise üç kritik noktayı birlikte "
    "çevreler. Kesikli doğru <em>y</em> = <em>x</em>'tir.",
    aria="Level curves of x^4 + y^4 - 4xy + 1: small ovals around the minima (1, 1) and (-1, -1), the thick "
         "figure eight f = 1 through the saddle point at the origin and larger curves around all three"))

# ============================================================
# kup-kare: x^4 + y^2 (strict minimum) against x^3 + y^2 (saddle)
# ============================================================
PPU = 118
p1 = eq_plot(40, 50, PPU, (-1, 1), (-1, 1))
p2 = eq_plot(40 + 2 * PPU + 70, 50, PPU, (-1, 1), (-1, 1))


def quartic_level(c, n=480):
    """x^4 + y^2 = c in polar form: cos^4 s^2 + sin^2 s - c = 0, s = r^2 (stable root)."""
    pts = []
    for k in range(n + 1):
        th = 2 * math.pi * k / n
        a, b = math.cos(th) ** 4, math.sin(th) ** 2
        s = 2 * c / (b + math.sqrt(b * b + 4 * a * c))
        pts.append(polar_pt(s, th))
    return pts


def frame(p, title):
    p.polygon([(-1, -1), (1, -1), (1, 1), (-1, 1)], TEXT, 0.0, TEXT, 0.8)
    p.line([(0, -1), (0, 1)], TEXT, 1.0, None, 0.45)
    # the x axis, where the second order test is blind, drawn heavy
    p.line([(-1, 0), (1, 0)], TEXT, 2.4, None, 0.8)
    p.label(1, 0, it("x"), 8, 4, TEXT, 12.5)
    p.label(0, 1, it("y"), 0, -6, TEXT, 12.5, "middle")
    for v in (-1, 1):
        p.label(v, -1, dec(v), 0, 15, TEXT, 11, "middle")
        p.label(-1, v, dec(v), -6, 4, TEXT, 11, "end")
    p.text_px(p.x0 + p.w / 2, p.y0 - 24, title, TEXT, 13, "middle", True)


frame(p1, it("x") + sup("4") + " + " + it("y") + sup("2"))
for c in (0.02, 0.1, 0.3, 0.6):
    p1.line(quartic_level(c), THEORY, 1.5)
    plabel(p1, 0.0, math.sqrt(c), dec(c), 0, 4, THEORY, 10.5, "middle")
dot(p1, (0, 0), PRACTICE, 4.2)
p1.line([(0.03, -0.04), (0.42, -0.86)], PRACTICE, 0.9, None, 0.8)
p1.label(0.42, -0.86, "kesin minimum", 4, 12, PRACTICE, 12, "middle", True)

frame(p2, it("x") + sup("3") + " + " + it("y") + sup("2"))
cusp_lo = [(-abs(t) ** (2 / 3), t) for t in [-1 + k / 200 for k in range(201)]]    # y from -1 to 0
cusp_hi = [(-abs(t) ** (2 / 3), t) for t in [k / 200 for k in range(201)]]          # y from 0 to 1
p2.polygon(cusp_lo + cusp_hi, PRACTICE, 0.18)
p2.line(cusp_lo + cusp_hi[1:], PRACTICE, 2.6)
dot(p2, (0, 0), TEXT, 4.2)
p2.label(-0.62, -0.2, it("f") + " &lt; 0", 0, 4, PRACTICE, 12.5, "middle", True)
p2.label(0.5, 0.55, it("f") + " &gt; 0", 0, 4, TEXT, 12.5, "middle", True)
p2.label(-0.62, 0.72, it("f") + " = 0", 0, 0, PRACTICE, 12, "middle")
p2.label(0, 0, "eyer noktası", 8, -9, TEXT, 12)
save("kup-kare", figure(
    int(p2.x0 + p2.w + 40), int(p1.y0 + p1.h + 30), [p1, p2],
    "Solda <em>x</em><sup>4</sup> + <em>y</em>² fonksiyonunun 0,02; 0,1; 0,3; 0,6 seviye eğrileri orijini "
    "çevreler ve orijinde kesin minimum vardır. Sağda <em>x</em><sup>3</sup> + <em>y</em>² = 0 eğrisi "
    "(<em>x</em> = &#8722;|<em>y</em>|<sup>2/3</sup>) orijinde sivri bir uç yapar; taralı bölgede "
    "<em>f</em> &lt; 0, geri kalanında <em>f</em> &gt; 0 olur. İki fonksiyonun Hessian matrisi orijinde "
    "aynıdır; fark, kalın çizilen <em>x</em> ekseni boyunca ortaya çıkar.",
    css_class=WIDE,
    aria="Two panels: left, closed level curves of x^4 + y^2 around the strict minimum at the origin; right, "
         "the cusp curve x^3 + y^2 = 0 with the region f less than 0 shaded and the saddle point at the origin"))
