# -*- coding: utf-8 -*-
"""
Figures of the chapter "Sınır, Kapanış ve İç"
(dersler/analiz-4/sinir-kapanis-ve-ic.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box and never directly under a heading.
The figures are NOT produced at build time. Run

    python scripts/analysis4_figures/snr.py
    python scripts/center_figures.py "analysis4-snr-*.md"
    python scripts/check_figure_labels.py "scripts/_figures/analysis4-snr-*.md"

and paste the markup of scripts/_figures/analysis4-snr-<name>.md into the .qmd.
The captions are Turkish on purpose; the aria labels are plain ASCII.

Conventions: a boundary that belongs to the set is solid, one that does not is
dashed; a point of the set is filled, a point outside it is hollow.
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, hollow, annulus_fill, TEXT, THEORY, PRACTICE  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "analysis4-snr-"

MINUS = "&#8722;"


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
    return f"{v:g}".replace("-", MINUS)


def equal_panel(x0, y0, ppu, xrange, yrange):
    """A panel with the same pixels per unit on both axes."""
    return Plot(x0, y0, ppu * (xrange[1] - xrange[0]), ppu * (yrange[1] - yrange[0]), xrange, yrange)


def arc_pts(cx, cy, r, a0, a1, n=96):
    return [(cx + r * math.cos(a0 + (a1 - a0) * k / n), cy + r * math.sin(a0 + (a1 - a0) * k / n))
            for k in range(n + 1)]


def graph_pts(f, x0, x1, n=160):
    return [(x0 + (x1 - x0) * k / n, f(x0 + (x1 - x0) * k / n)) for k in range(n + 1)]


def neg(pts):
    return [(-x, -y) for x, y in pts]


def tick(p, axis, v, label, dx, dy, anchor):
    """A short tick on an axis through the origin with a hand-placed label."""
    h = 0.04 * (p.xmax - p.xmin) / 3.0
    if axis == "x":
        p.line([(v, -h), (v, h)], TEXT, 1.0, None, 0.6)
        p.label(v, 0, label, dx, dy, TEXT, 11, anchor)
    else:
        p.line([(-h, v), (h, v)], TEXT, 1.0, None, 0.6)
        p.label(0, v, label, dx, dy, TEXT, 11, anchor)


# ============================================================
# e-kumesi: E = {x^2 + y^2 <= 4, xy > 1}, the circle arcs belong to E, the hyperbola arcs do not
# ============================================================
A = math.sqrt(2 + math.sqrt(3))              # 1.9319
B = math.sqrt(2 - math.sqrt(3))              # 0.5176
TA, TB = math.atan2(B, A), math.atan2(A, B)  # 15 and 75 degrees
p = equal_panel(30, 20, 84, (-2.5, 2.5), (-2.5, 2.5))
lens = graph_pts(lambda x: 1 / x, B, A) + arc_pts(0, 0, 2, TA, TB)
p.polygon(lens, THEORY, 0.2)
p.polygon(neg(lens), THEORY, 0.2)
p.origin_axes(it("x"), it("y"), (), (), num, num, 0.45)
# the rest of the circle and of the hyperbola: thin grey guides
for a0, a1 in ((TB, TA + math.pi), (TB + math.pi, TA + 2 * math.pi)):
    p.line(arc_pts(0, 0, 2, a0, a1, 160), TEXT, 1.0, None, 0.45)
for x0, x1 in ((0.4, B), (A, 2.5)):
    branch = graph_pts(lambda x: 1 / x, x0, x1, 80)
    p.line(branch, TEXT, 1.0, None, 0.45)
    p.line(neg(branch), TEXT, 1.0, None, 0.45)
# the boundary of E
for s in (1, -1):
    arc = arc_pts(0, 0, 2, TA, TB)
    hyp = graph_pts(lambda x: 1 / x, B, A)
    p.line(arc if s == 1 else neg(arc), THEORY, 2.5)
    p.line(hyp if s == 1 else neg(hyp), THEORY, 2.3, "6 4")
for q in ((A, B), (B, A), (-A, -B), (-B, -A)):
    hollow(p, q, THEORY, 3.8, 1.7)
p.label(A, B, "(" + it("a") + ", " + it("b") + ")", 7, -7, TEXT, 12)
p.label(B, A, "(" + it("b") + ", " + it("a") + ")", 7, -7, TEXT, 12)
p.label(1.28, 1.2, it("E"), 0, 0, THEORY, 14, "middle", True)
p.label(-1.25, -1.33, it("E"), 0, 0, THEORY, 14, "middle", True)
p.label(2.0 * math.cos(math.radians(120)), 2.0 * math.sin(math.radians(120)),
        it("x") + sups("2") + " + " + it("y") + sups("2") + " = 4", -6, -6, TEXT, 11.5, "end")
# under the right end of the branch, between the hyperbola, the circle and the x axis
p.label(2.55, 0.4, it("xy") + " = 1", 0, 16, TEXT, 11.5, "end")
save("e-kumesi", figure(
    500, 480, [p],
    "<em>E</em> = {<em>x</em><sup>2</sup> + <em>y</em><sup>2</sup> &#8804; 4, <em>xy</em> &gt; 1} kümesinin "
    "iki parçası. Sınırın düz çizilen çember yayları <em>E</em>'ye aittir, kesikli hiperbol yayları ait "
    "değildir; <em>a</em> &#8776; 1,93 ve <em>b</em> &#8776; 0,52 olmak üzere dört köşe noktası da "
    "<em>E</em>'nin dışındadır.",
    aria="The set E between the circle of radius 2 and the hyperbola xy = 1 in the first and third quadrants, "
         "circle arcs solid, hyperbola arcs dashed, four corner points hollow"))

# ============================================================
# papyon: A = {|y| < |x| <= 1}; the diagonals and the origin are missing
# ============================================================
p = equal_panel(30, 20, 115, (-1.5, 1.5), (-1.5, 1.5))
right = [(0, 0), (1, -1), (1, 1)]
left = [(0, 0), (-1, 1), (-1, -1)]
p.polygon(right, THEORY, 0.22)
p.polygon(left, THEORY, 0.22)
p.origin_axes(it("x"), it("y"), (), (), num, num, 0.45)
tick(p, "x", 1, "1", 5, 15, "start")
tick(p, "x", -1, num(-1), -5, 15, "end")
tick(p, "y", 1, "1", -7, 4, "end")
tick(p, "y", -1, num(-1), -7, 4, "end")
p.line([(-1, -1), (1, 1)], THEORY, 1.9, "6 4")
p.line([(-1, 1), (1, -1)], THEORY, 1.9, "6 4")
p.line([(1, -1), (1, 1)], THEORY, 2.6)
p.line([(-1, -1), (-1, 1)], THEORY, 2.6)
for q in ((1, 1), (1, -1), (-1, 1), (-1, -1), (0, 0)):
    hollow(p, q, THEORY, 3.8, 1.7)
p.label(0.68, 0.28, it("A"), 0, 0, THEORY, 14, "middle", True)
save("papyon", figure(
    420, 400, [p],
    "<em>A</em> = {|<em>y</em>| &lt; |<em>x</em>| &#8804; 1} papyonu. <em>x</em> = &#177;1 kenarları "
    "<em>A</em>'ya aittir (düz); köşegen parçaları, dört köşe ve başlangıç noktası ait değildir. "
    "Kapanış bu kesikli parçaları ve boş noktaları da içerir.",
    aria="Bow tie region between the lines y = x and y = -x for 0 less than |x| at most 1, "
         "vertical sides solid, diagonals dashed, corners and origin hollow"))

# ============================================================
# uc-parca: interior point, boundary point and exterior point of a set S
# ============================================================
RB = 0.36                                    # radius of the small balls


def bean(t):
    """Kidney-bean outline: the cos 2t term dents the top edge and fattens the bottom."""
    return (2.0 * math.cos(t), 1.0 * math.sin(t) + 0.45 * math.cos(2 * t) + 0.3)


p = equal_panel(20, 20, 72, (-3.0, 3.0), (-2.0, 2.0))
N = 240
outline = [bean(2 * math.pi * k / N) for k in range(N)]
p.polygon(outline, THEORY, 0.2)
upper = [bean(math.pi * k / 120) for k in range(121)]
lower = [bean(math.pi + math.pi * k / 120) for k in range(121)]
p.line(upper, THEORY, 2.3)
p.line(lower, THEORY, 2.1, "6 4")
PP = (-0.2, -0.45)
QQ = bean(math.pi / 6)
ZZ = (2.25, -1.25)
for c in (PP, QQ, ZZ):
    p.circle(c[0], c[1], RB, PRACTICE, 1.3, "4 3")
p.points([PP, QQ], TEXT, 3.6)
hollow(p, ZZ, TEXT, 3.6, 1.6)
p.label(PP[0], PP[1], it("p"), 6, -5, TEXT, 12.5)
p.label(QQ[0], QQ[1], it("q"), -8, -6, TEXT, 12.5, "end")
p.label(ZZ[0], ZZ[1], it("z"), 6, -5, TEXT, 12.5)
p.label(PP[0], PP[1] - RB, "iç nokta", 0, 16, TEXT, 12, "middle")
p.label(QQ[0], QQ[1] + RB, "sınır noktası", 0, -8, TEXT, 12, "middle")
p.label(ZZ[0], ZZ[1] - RB, it("S") + sups("c") + "'nin iç noktası", -10, 17, TEXT, 12, "middle")
p.label(-1.25, 0.05, it("S"), 0, 0, THEORY, 15, "middle", True)
p.label(-2.4, 1.45, it("S") + sups("c"), 0, 0, TEXT, 15, "middle", True)
save("uc-parca", figure(
    470, 330, [p],
    "<em>S</em> kümesi ve üç tür nokta: <em>p</em>'nin çevresindeki küçük yuvar tamamen <em>S</em>'de "
    "(iç nokta), <em>q</em>'nun çevresindeki her yuvar hem <em>S</em>'ye hem <em>S</em><sup>c</sup>'ye "
    "taşar (sınır noktası), <em>z</em>'nin çevresindeki yuvar tamamen <em>S</em><sup>c</sup>'de. "
    "Sınırın düz kısmı <em>S</em>'ye aittir, kesikli kısmı ait değildir.",
    aria="A bean shaped set S with an interior point p, a boundary point q and an exterior point z, "
         "each with a small ball around it"))

# ============================================================
# yari-acik-halka: X = {2 <= |x - x0| < 3} with x0 = 0
# ============================================================
RS = 0.45
# a little extra room above and to the right keeps the axis tips clear of the ball about (0, 3)
p = equal_panel(20, 20, 58, (-3.5, 3.9), (-3.5, 4.1))
annulus_fill(p, 0, 0, 2, 3, THEORY, 0.2)
p.origin_axes(it("x"), it("y"), (), (), num, num, 0.45)
# 3 on the x axis, 2 on the y axis: the sample point (2, 0) sits where the tick 2 would go
tick(p, "x", 3, "3", 4, 15, "start")
tick(p, "y", 2, "2", -6, -5, "end")
p.circle(0, 0, 2, THEORY, 2.5)
p.circle(0, 0, 3, THEORY, 2.1, "6 4")
for c in ((2, 0), (0, 3)):
    p.circle(c[0], c[1], RS, PRACTICE, 1.2, "4 3")
p.points([(0, 0)], TEXT, 3.6)
p.points([(2, 0)], THEORY, 3.8)
hollow(p, (0, 3), THEORY, 3.8, 1.7)
p.label(0, 0, it("x") + subs("0"), 7, -7, TEXT, 12.5)
p.label(-1.77, -1.77, it("X"), 0, 5, THEORY, 15, "middle", True)
save("yari-acik-halka", figure(
    480, 490, [p],
    "<em>X</em> = {2 &#8804; &#8214;<em>x</em> &#8722; <em>x</em><sub>0</sub>&#8214; &lt; 3} halkası "
    "(<em>x</em><sub>0</sub> = (0, 0)). İç çember <em>X</em>'e aittir (düz), dış çember ait değildir "
    "(kesikli). (2, 0) ve (0, 3) sınır noktalarının çevresindeki her yuvar hem <em>X</em>'e hem "
    "tümleyenine taşar.",
    aria="Annulus between the circles of radius 2 and 3 about the origin, inner circle solid, outer circle "
         "dashed, with small balls around the boundary points (2, 0) and (0, 3)"))
