# -*- coding: utf-8 -*-
"""
Figures of the chapter "Çok Değişkenli Fonksiyonlar ve Limit"
(dersler/analiz-4/cok-degiskenli-fonksiyonlar-ve-limit.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box and never directly under a heading.
The figures are NOT produced at build time. Run

    python scripts/analysis4_figures/lim.py
    python scripts/center_figures.py "analysis4-lim-*.md"
    python scripts/check_figure_labels.py "scripts/_figures/analysis4-lim-*.md"

and paste the markup of scripts/_figures/analysis4-lim-<name>.md into the .qmd.
The captions are Turkish on purpose; the aria labels are plain ASCII.

Conventions: a boundary that belongs to the set is solid, one that does not is
dashed; a point of the set is filled, a point outside it is hollow. Thin grey
curves are guides (the rest of a circle or a line that bounds no part of the set).
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, hollow, blob, WIDE, TEXT, THEORY, PRACTICE  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "analysis4-lim-"

MINUS, DELTA, EPS = "&#8722;", "&#948;", "&#949;"


def save(name, svg):
    (OUT_DIR / f"{PREFIX}{name}.md").write_text(svg, encoding="utf-8", newline="\n")
    print(f"{PREFIX}{name}.md")


def it(s):
    """Italic math letter inside an SVG <text>."""
    return f'<tspan font-style="italic">{s}</tspan>'


def subs(s, size=9):
    """Subscript inside an SVG <text>."""
    return f'<tspan font-size="{size}" dy="4">{s}</tspan><tspan dy="-4">&#8203;</tspan>'


def sups(s, size=9):
    """Superscript inside an SVG <text>."""
    return f'<tspan font-size="{size}" dy="-5">{s}</tspan><tspan dy="5">&#8203;</tspan>'


def num(v):
    """Tick label with a real minus sign."""
    return f"{v:g}".replace("-", MINUS)


def equal_panel(x0, y0, ppu, xrange, yrange):
    """A panel with the same pixels per unit on both axes."""
    return Plot(x0, y0, ppu * (xrange[1] - xrange[0]), ppu * (yrange[1] - yrange[0]), xrange, yrange)


def arc_pts(cx, cy, r, a0, a1, n=96):
    return [(cx + r * math.cos(a0 + (a1 - a0) * k / n), cy + r * math.sin(a0 + (a1 - a0) * k / n))
            for k in range(n + 1)]


def graph_pts(f, x0, x1, n=160):
    return [(x0 + (x1 - x0) * k / n, f(x0 + (x1 - x0) * k / n)) for k in range(n + 1)]


def tick(p, axis, v, label, dx, dy, anchor):
    """A short tick on an axis through the origin with a hand-placed label."""
    h = 0.045 * (p.xmax - p.xmin) / 3.0
    if axis == "x":
        p.line([(v, -h), (v, h)], TEXT, 1.0, None, 0.6)
        p.label(v, 0, label, dx, dy, TEXT, 11, anchor)
    else:
        p.line([(-h, v), (h, v)], TEXT, 1.0, None, 0.6)
        p.label(0, v, label, dx, dy, TEXT, 11, anchor)


def clip_convex(subject, clip):
    """Sutherland-Hodgman: the part of polygon `subject` inside the convex,
    counter-clockwise polygon `clip`."""
    def inside(q, a, b):
        return (b[0] - a[0]) * (q[1] - a[1]) - (b[1] - a[1]) * (q[0] - a[0]) >= 0

    def cut(p1, p2, a, b):
        x1, y1 = p1
        x2, y2 = p2
        dxs, dys = x2 - x1, y2 - y1
        dxc, dyc = b[0] - a[0], b[1] - a[1]
        t = (dxc * (y1 - a[1]) - dyc * (x1 - a[0])) / (dyc * dxs - dxc * dys)
        return (x1 + t * dxs, y1 + t * dys)

    out = list(subject)
    for i in range(len(clip)):
        a, b = clip[i - 1], clip[i]
        pts, out = out, []
        for j in range(len(pts)):
            cur, prev = pts[j], pts[j - 1]
            if inside(cur, a, b):
                if not inside(prev, a, b):
                    out.append(cut(prev, cur, a, b))
                out.append(cur)
            elif inside(prev, a, b):
                out.append(cut(prev, cur, a, b))
    return out


# ============================================================
# log-kok: dom f = {(x - 1)(y + 2) > 0, x^2 + y^2 <= 9}
# ============================================================
R = 3.0
S8, S5 = math.sqrt(8.0), math.sqrt(5.0)
TOP = math.atan2(S8, 1.0)                    # (1, sqrt 8)
RIGHT = math.atan2(-2.0, S5)                 # (sqrt 5, -2)
LEFT = math.atan2(-2.0, -S5) + 2 * math.pi   # (-sqrt 5, -2)
BOTTOM = math.atan2(-S8, 1.0) + 2 * math.pi  # (1, -sqrt 8)
p = equal_panel(40, 30, 50, (-4.0, 4.0), (-4.0, 4.0))
upper = [(1.0, -2.0)] + arc_pts(0, 0, R, RIGHT, TOP)
lower = [(1.0, -2.0)] + arc_pts(0, 0, R, LEFT, BOTTOM)
p.polygon(upper, THEORY, 0.2)
p.polygon(lower, THEORY, 0.2)
p.origin_axes(it("x"), it("y"), (), (), num, num, 0.45)
tick(p, "x", 3, "3", 5, 15, "start")
tick(p, "y", 3, "3", -5, -9, "end")
# guides: the rest of the circle and the two lines outside the pieces
p.line(arc_pts(0, 0, R, TOP, LEFT, 160), TEXT, 1.0, None, 0.45)
p.line(arc_pts(0, 0, R, BOTTOM, RIGHT + 2 * math.pi, 40), TEXT, 1.0, None, 0.45)
p.line([(1.0, S8), (1.0, 4.0)], TEXT, 1.0, "5 4", 0.5)
p.line([(1.0, -S8), (1.0, -4.0)], TEXT, 1.0, "5 4", 0.5)
p.line([(-4.0, -2.0), (-S5, -2.0)], TEXT, 1.0, "5 4", 0.5)
p.line([(S5, -2.0), (4.0, -2.0)], TEXT, 1.0, "5 4", 0.5)
# the boundary of dom f: circle arcs belong to it, the pieces of the two lines do not
p.line(arc_pts(0, 0, R, RIGHT, TOP), THEORY, 2.5)
p.line(arc_pts(0, 0, R, LEFT, BOTTOM), THEORY, 2.5)
p.line([(1.0, -2.0), (1.0, S8)], THEORY, 2.1, "6 4")
p.line([(1.0, -2.0), (S5, -2.0)], THEORY, 2.1, "6 4")
p.line([(1.0, -2.0), (-S5, -2.0)], THEORY, 2.1, "6 4")
p.line([(1.0, -2.0), (1.0, -S8)], THEORY, 2.1, "6 4")
for q in ((1.0, -2.0), (1.0, S8), (S5, -2.0), (-S5, -2.0), (1.0, -S8)):
    hollow(p, q, THEORY, 3.6, 1.6)
p.label(1.0, 4.0, it("x") + " = 1", 0, -7, TEXT, 11.5, "middle")
p.label(4.0, -2.0, it("y") + " = " + MINUS + "2", 7, 4, TEXT, 11.5)
p.label(3.0 * math.cos(math.radians(128)), 3.0 * math.sin(math.radians(128)),
        it("x") + sups("2") + " + " + it("y") + sups("2") + " = 9", -6, -6, TEXT, 11.5, "end")
save("log-kok", figure(
    480, 460, [p],
    "dom <em>f</em>: kapalı <em>x</em><sup>2</sup> + <em>y</em><sup>2</sup> &#8804; 9 yuvarının <em>x</em> = 1 ve "
    "<em>y</em> = &#8722;2 doğrularıyla ayrılan parçalarından <em>x</em> &gt; 1, <em>y</em> &gt; &#8722;2 olan "
    "sağ üstteki ile <em>x</em> &lt; 1, <em>y</em> &lt; &#8722;2 olan sol alttaki. Çember yayları kümeye aittir "
    "(düz), doğru parçaları ve (1, &#8722;2) noktası ait değildir (kesikli, içi boş).",
    aria="Disc of radius 3 cut by the dashed lines x = 1 and y = -2; the upper right piece and the lower left "
         "piece are shaded, their circle arcs solid, the point (1, -2) hollow"))

# ============================================================
# disk-parabol: dom f = {(x - 1)^2 + y^2 < 1, y > x^2 - 1}
# ============================================================


def meet(x):
    """(x - 1)^2 (x^2 + 2x + 2) - 1: zero where the parabola crosses the circle."""
    return (x - 1) ** 2 * (x * x + 2 * x + 2) - 1


def bisect(f, a, b):
    for _ in range(80):
        m = (a + b) / 2
        if f(a) * f(m) <= 0:
            b = m
        else:
            a = m
    return (a + b) / 2


X1, X2 = bisect(meet, 0.2, 0.7), bisect(meet, 1.2, 1.6)          # 0.4258..., 1.3865...
P1, P2 = (X1, X1 * X1 - 1), (X2, X2 * X2 - 1)
A1 = math.atan2(P1[1], P1[0] - 1) + 2 * math.pi                   # angle of P1 about (1, 0)
A2 = math.atan2(P2[1], P2[0] - 1)                                 # angle of P2 about (1, 0)
par = lambda x: x * x - 1                                         # noqa: E731
p = equal_panel(40, 26, 110, (-1.2, 2.6), (-1.4, 1.6))
region = arc_pts(1.0, 0.0, 1.0, A2, A1, 160) + graph_pts(par, X1, X2, 100)
p.polygon(region, THEORY, 0.2)
p.origin_axes(it("x"), it("y"), (), (), num, num, 0.45)
tick(p, "x", 1, "1", 5, 15, "start")
tick(p, "x", 2, "2", 5, 15, "start")
tick(p, "y", 1, "1", -6, 4, "end")
# guides: the lower right arc of the circle and the parabola outside the circle
p.line(arc_pts(1.0, 0.0, 1.0, A1 - 2 * math.pi, A2, 60), TEXT, 1.0, None, 0.45)
p.line(graph_pts(par, -1.1, X1, 120), TEXT, 1.0, None, 0.45)
p.line(graph_pts(par, X2, 1.6, 60), TEXT, 1.0, None, 0.45)
# the boundary of dom f: neither the arc nor the parabola belongs to it
p.line(arc_pts(1.0, 0.0, 1.0, A2, A1, 160), THEORY, 2.1, "6 4")
p.line(graph_pts(par, X1, X2, 100), THEORY, 2.1, "6 4")
hollow(p, (1.0, 0.0), TEXT, 3.4, 1.5)
hollow(p, P1, THEORY, 3.6, 1.6)
hollow(p, P2, THEORY, 3.6, 1.6)
p.label(1.0 + math.cos(-0.75), math.sin(-0.75), "(" + it("x") + " " + MINUS + " 1)" + sups("2") + " + "
        + it("y") + sups("2") + " = 1", 8, 8, TEXT, 11.5)
p.label(1.6, par(1.6), it("y") + " = " + it("x") + sups("2") + " " + MINUS + " 1", 7, 6, TEXT, 11.5)
save("disk-parabol", figure(
    520, 400, [p],
    "dom <em>f</em>: (1, 0) merkezli açık birim yuvarın <em>y</em> = <em>x</em><sup>2</sup> &#8722; 1 parabolünün "
    "üstünde kalan kısmı. Parabol yuvarın merkezinden geçer ve çemberi yaklaşık (0,43; &#8722;0,82) ile "
    "(1,39; 0,92) noktalarında keser; çember yayı da parabol yayı da kümeye ait değildir (kesikli).",
    aria="Open disc of radius 1 about (1, 0) and the parabola y = x^2 - 1 through its center; the part of the "
         "disc above the parabola is shaded, both boundary curves dashed, the two crossing points hollow"))

# ============================================================
# komsuluk: f maps D inside B(x0, delta) minus x0 into B(L, eps)
# ============================================================
PPU = 62
p = Plot(24, 40, PPU * 10.4, PPU * 3.8, (0.0, 10.4), (0.0, 3.8))
FRAMES = ((0.1, 4.3), (6.1, 10.3))
for a, b in FRAMES:
    p.line([(a, 0.05), (b, 0.05), (b, 3.75), (a, 3.75), (a, 0.05)], TEXT, 1.0, None, 0.3)
p.label(2.2, 3.75, "&#8477;" + sups(it("n")), 0, -9, TEXT, 13, "middle", True)
p.label(8.2, 3.75, "&#8477;" + sups(it("m")), 0, -9, TEXT, 13, "middle", True)
# the set D and the accumulation point x0 on its edge
D = blob(1.95, 1.85, 1.3, [(0.16, 2, 0.6), (0.09, 3, 2.1)], 240)
T0 = 0.12
X0 = (1.95 + (1.3 + 0.16 * math.cos(2 * T0 + 0.6) + 0.09 * math.cos(3 * T0 + 2.1)) * math.cos(T0),
      1.85 + (1.3 + 0.16 * math.cos(2 * T0 + 0.6) + 0.09 * math.cos(3 * T0 + 2.1)) * math.sin(T0))
DL = 0.72
disc = arc_pts(X0[0], X0[1], DL, 0.0, 2 * math.pi, 180)[:-1]
near = clip_convex(D, disc)
p.polygon(D, THEORY, 0.14)
p.polygon(near, PRACTICE, 0.32)
p.line(D + [D[0]], THEORY, 1.4, "5 4")
p.circle(X0[0], X0[1], DL, PRACTICE, 1.6, "5 3")
XP = (2.85, 1.72)                           # inside the dark part, well away from its edges
p.points([XP], TEXT, 3.6)
hollow(p, X0, TEXT, 3.8, 1.6)
p.label(X0[0], X0[1], it("x") + subs("0"), 8, 5, TEXT, 12.5)
p.label(XP[0], XP[1], it("x"), 6, -5, TEXT, 12.5)
p.label(1.05, 2.1, it("D"), 0, 0, THEORY, 14, "middle", True)
p.label(X0[0] + DL * math.cos(1.0), X0[1] + DL * math.sin(1.0),
        it("B") + "(" + it("x") + subs("0") + ", " + it(DELTA) + ")", 3, -6, PRACTICE, 12)
# the arrow f between the two spaces
p.arrow((4.5, 1.85), (5.9, 1.85), TEXT, 1.6, 8.0)
p.label(5.2, 1.85, it("f"), 0, -8, TEXT, 13.5, "middle")
# the ball B(L, eps) and the image of the dark part near L
L = (8.1, 1.8)
EP = 1.15
p.circle(L[0], L[1], EP, PRACTICE, 1.6, "5 3")
IMG = blob(L[0] - 0.36, L[1] + 0.3, 0.3, [(0.07, 2, 0.4), (0.04, 3, 1.0)], 120)
p.polygon(IMG, PRACTICE, 0.32)
FX = (L[0] - 0.42, L[1] + 0.34)
p.points([L, FX], TEXT, 3.6)
p.label(L[0], L[1], it("L"), 7, 13, TEXT, 12.5)
p.label(FX[0], FX[1], it("f") + "(" + it("x") + ")", -9, -8, TEXT, 12.5, "end")
p.label(L[0] + EP * math.cos(0.75), L[1] + EP * math.sin(0.75),
        it("B") + "(" + it("L") + ", " + it(EPS) + ")", 4, -6, PRACTICE, 12)
save("komsuluk", figure(
    24 + PPU * 10.4 + 24, 40 + PPU * 3.8 + 12, [p],
    "Solda <em>D</em> kümesi ve kenarındaki <em>x</em><sub>0</sub> yığılma noktası. <em>D</em>'nin "
    "<em>B</em>(<em>x</em><sub>0</sub>, <em>&#948;</em>) yuvarına düşen, <em>x</em><sub>0</sub> dışındaki "
    "parçası (turuncu) <em>f</em> altında sağdaki <em>B</em>(<em>L</em>, <em>&#949;</em>) yuvarının içine gider: "
    "bu parçadaki her <em>x</em> için <em>f</em>(<em>x</em>) de o yuvardadır.",
    css_class=WIDE,
    aria="Left: a region D with the point x0 on its edge, a dashed ball about x0 and the part of D inside it. "
         "Right: a dashed ball about L containing the image of that part and the point f(x)"))

# ============================================================
# parabol-diziler: x_k = (1/k, 1/k^2) on the parabola, y_k = (1/k, 0) off it
# ============================================================
p = equal_panel(40, 26, 330, (-0.15, 1.15), (-0.25, 1.15))
p.origin_axes(it("x"), it("y"), (), (), num, num, 0.45)
p.line(graph_pts(lambda x: x * x, -0.15, 1.05, 160), THEORY, 2.6)
XS = [(1 / k, 1 / k ** 2) for k in range(1, 7)]
YS = [(1 / k, 0.0) for k in range(1, 7)]
p.points(XS, THEORY, 3.6)
p.points(YS, PRACTICE, 3.6)
hollow(p, (0, 0), TEXT, 3.8, 1.6)
p.label(1.05, 1.05 ** 2, it("f") + " = 0", 7, 5, THEORY, 12.5)
p.label(0.06, 0.9, "parabolün dışında " + it("f") + " = 1", 0, 0, TEXT, 12)
p.label(1.0, 1.0, it("x") + subs("1"), -10, -2, THEORY, 12.5, "end")
p.label(0.5, 0.25, it("x") + subs("2"), -9, -5, THEORY, 12.5, "end")
p.label(1 / 3, 1 / 9, it("x") + subs("3"), -8, -7, THEORY, 12.5, "end")
for k in (1, 2, 3):
    p.label(1 / k, 0, it("y") + subs(str(k)), 0, 19, PRACTICE, 12.5, "middle")
save("parabol-diziler", figure(
    520, 520, [p],
    "<em>x<sub>k</sub></em> = (1/<em>k</em>, 1/<em>k</em><sup>2</sup>) noktaları <em>y</em> = <em>x</em><sup>2</sup> "
    "parabolü üzerindedir ve orada <em>f</em> = 0'dır; <em>y<sub>k</sub></em> = (1/<em>k</em>, 0) noktaları "
    "parabolün dışındadır ve orada <em>f</em> = 1'dir. İki dizi de (0, 0)'a yakınsar, görüntüleri ise 0'a ve "
    "1'e gider.",
    aria="Parabola y = x^2 with the points (1/k, 1/k^2) on it and the points (1/k, 0) on the x axis, "
         "k = 1 to 6, both sequences approaching the origin"))
