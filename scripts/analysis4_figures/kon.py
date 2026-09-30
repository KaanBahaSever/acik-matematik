# -*- coding: utf-8 -*-
"""
Figures of the chapter "Metrik, Doğrular ve Konveks Kümeler"
(dersler/analiz-4/metrik-dogrular-ve-konveks-kumeler.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box and never directly under a heading.
The figures are NOT produced at build time. Run

    python scripts/analysis4_figures/kon.py
    python scripts/center_figures.py "analysis4-kon-*.md"
    python scripts/check_figure_labels.py "scripts/_figures/analysis4-kon-*.md"

and paste the markup of scripts/_figures/analysis4-kon-<name>.md into the .qmd.
The captions are Turkish on purpose; the aria labels are plain ASCII.

Conventions: a boundary that belongs to the set is solid, one that does not is
dashed; a point of the set is filled, a point outside it is hollow.
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import (Plot, figure, hollow, disk_fill, annulus_fill, panel_title,  # noqa: E402
                      WIDE, TEXT, THEORY, PRACTICE)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "analysis4-kon-"

MINUS, INF = "&#8722;", "&#8734;"


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


def plain_axes(p, opacity=0.4):
    """Axes through the origin without letters or ticks."""
    p.origin_axes("", "", (), (), num, num, opacity)


def tick(p, axis, v, label, dx, dy, anchor):
    """A short tick on an axis through the origin with a hand-placed label."""
    h = 0.045 * (p.xmax - p.xmin) / 3.0
    if axis == "x":
        p.line([(v, -h), (v, h)], TEXT, 1.0, None, 0.6)
        p.label(v, 0, label, dx, dy, TEXT, 11, anchor)
    else:
        p.line([(-h, v), (h, v)], TEXT, 1.0, None, 0.6)
        p.label(0, v, label, dx, dy, TEXT, 11, anchor)


# ============================================================
# dogru-parcasi: L(a; b) for a = (4, 1), b = (0, 3) is the piece 0 <= x <= 4 of x + 2y = 6
# ============================================================
A, B = (4.0, 1.0), (0.0, 3.0)
p = equal_panel(30, 24, 68, (-1.0, 5.0), (-1.0, 4.0))
# no tick label 3 on the y axis: b = (0, 3) sits there and carries its own coordinates
p.origin_axes(it("x"), it("y"), (1, 2, 3, 4), (1, 2), num, num, 0.45)
p.line([(-1.0, 3.5), (5.0, 0.5)], TEXT, 1.2, "5 4", 0.55)
p.line([B, A], THEORY, 3.0)
p.points([(1.0, 2.5), (2.0, 2.0)], PRACTICE, 3.4)
p.points([A, B], TEXT, 4.2)
p.label(B[0], B[1], it("b") + " = (0, 3)", 9, -25, TEXT, 12)
p.label(B[0], B[1], it("t") + " = 0", 9, -10, TEXT, 12)
p.label(A[0], A[1], it("a") + " = (4, 1)", -8, 19, TEXT, 12, "end")
p.label(A[0], A[1], it("t") + " = 1", -8, 34, TEXT, 12, "end")
p.label(1.0, 2.5, it("t") + " = 1/4", 6, -9, PRACTICE, 12)
p.label(2.0, 2.0, it("t") + " = 1/2 (orta nokta)", 6, -9, PRACTICE, 12)
save("dogru-parcasi", figure(
    470, 380, [p],
    "<em>a</em> = (4, 1) ile <em>b</em> = (0, 3) arasındaki <em>L</em>(<em>a</em>; <em>b</em>) doğru parçası "
    "(kalın), <em>x</em> + 2<em>y</em> = 6 doğrusunun (kesikli) 0 &#8804; <em>x</em> &#8804; 4 olan kısmıdır. "
    "<em>t</em> = 0 için <em>b</em>, <em>t</em> = 1/4 için (1, 5/2), <em>t</em> = 1/2 için orta nokta (2, 2), "
    "<em>t</em> = 1 için <em>a</em> elde edilir.",
    aria="Line x + 2y = 6 dashed, the segment from b = (0, 3) to a = (4, 1) solid, with the points for "
         "t = 0, 1/4, 1/2 and 1 marked"))

# ============================================================
# halka: the disc x^2 + y^2 <= 4 is convex, the ring 1 <= x^2 + y^2 <= 4 is not
# ============================================================
PQ = ((-1.5, 0.0), (1.5, 0.0))
PPU, GAP = 52, 56
W1 = 5.0 * PPU
left = equal_panel(24, 34, PPU, (-2.5, 2.5), (-2.5, 2.5))
right = equal_panel(24 + W1 + GAP, 34, PPU, (-2.5, 2.5), (-2.5, 2.5))
# left: the closed disc
disk_fill(left, 0, 0, 2, THEORY, 0.18)
plain_axes(left)
left.circle(0, 0, 2, THEORY, 2.1)
left.line(list(PQ), TEXT, 2.2)
left.points(list(PQ), TEXT, 4.0)
left.label(-1.5, 0, it("p"), 0, 18, TEXT, 12.5, "middle")
left.label(1.5, 0, it("q"), 0, 18, TEXT, 12.5, "middle")
panel_title(left, "konveks", TEXT, 12.5)
# right: the closed ring
annulus_fill(right, 0, 0, 1, 2, THEORY, 0.18)
# the vertical axis stops at the hole, which holds the label of the midpoint
AX = f'stroke="{TEXT}" stroke-width="1.1" opacity="0.4"'
right.add(f'<line x1="{right.X(-2.5) - 4:.1f}" y1="{right.Y(0):.1f}" x2="{right.X(2.5) + 4:.1f}" y2="{right.Y(0):.1f}" {AX}/>')
right.add(f'<polygon points="{right.X(2.5) + 4:.1f},{right.Y(0):.1f} {right.X(2.5) - 4:.1f},{right.Y(0) - 3.5:.1f} '
          f'{right.X(2.5) - 4:.1f},{right.Y(0) + 3.5:.1f}" fill="{TEXT}" opacity="0.4"/>')
right.add(f'<line x1="{right.X(0):.1f}" y1="{right.Y(-2.5) + 4:.1f}" x2="{right.X(0):.1f}" y2="{right.Y(-1):.1f}" {AX}/>')
right.add(f'<line x1="{right.X(0):.1f}" y1="{right.Y(1):.1f}" x2="{right.X(0):.1f}" y2="{right.Y(2.5) - 4:.1f}" {AX}/>')
right.add(f'<polygon points="{right.X(0):.1f},{right.Y(2.5) - 4:.1f} {right.X(0) - 3.5:.1f},{right.Y(2.5) + 4:.1f} '
          f'{right.X(0) + 3.5:.1f},{right.Y(2.5) + 4:.1f}" fill="{TEXT}" opacity="0.4"/>')
right.circle(0, 0, 1, THEORY, 2.1)
right.circle(0, 0, 2, THEORY, 2.1)
right.line([PQ[0], (-1.0, 0.0)], TEXT, 2.2)
right.line([(1.0, 0.0), PQ[1]], TEXT, 2.2)
right.line([(-1.0, 0.0), (1.0, 0.0)], PRACTICE, 2.8)
right.points(list(PQ), TEXT, 4.0)
hollow(right, (0, 0), PRACTICE, 4.0, 1.8)
right.label(-1.5, 0, it("p"), 0, 18, TEXT, 12.5, "middle")
right.label(1.5, 0, it("q"), 0, 18, TEXT, 12.5, "middle")
right.label(0, 0, "(" + it("p") + " + " + it("q") + ")/2", 0, -10, PRACTICE, 11.5, "middle")
right.label(0, 0, "<tspan font-style=\"italic\">C</tspan>'de değil", 0, 21, PRACTICE, 11, "middle")
right.label(-1.06, -1.06, it("C"), 0, 5, THEORY, 14, "middle", True)
panel_title(right, "konveks değil", TEXT, 12.5)
save("halka", figure(
    24 + 2 * W1 + GAP + 24, 34 + W1 + 16, [left, right],
    "Solda <em>x</em><sup>2</sup> + <em>y</em><sup>2</sup> &#8804; 4 dairesi: iki noktasını birleştiren parça "
    "dairenin içinde kalır. Sağda <em>C</em> = {1 &#8804; <em>x</em><sup>2</sup> + <em>y</em><sup>2</sup> &#8804; 4} "
    "halkası: <em>p</em> = (&#8722;3/2, 0) ile <em>q</em> = (3/2, 0) arasındaki parçanın &#8722;1 &lt; <em>x</em> &lt; 1 "
    "kısmı (turuncu) delikten geçer; orta nokta (<em>p</em> + <em>q</em>)/2 = (0, 0) <em>C</em>'ye ait değildir.",
    css_class=WIDE,
    aria="Left: a closed disc of radius 2 containing the segment between (-3/2, 0) and (3/2, 0). "
         "Right: the closed ring between radii 1 and 2, the same segment crossing the hole, midpoint (0, 0) hollow"))

# ============================================================
# birim-yuvarlar: the open unit balls of the 1-norm, the Euclidean norm and the max norm
# ============================================================
PPU, GAP = 62, 40
W1 = 3.0 * PPU
panels = [equal_panel(28 + k * (W1 + GAP), 34, PPU, (-1.5, 1.5), (-1.5, 1.5)) for k in range(3)]
DIAMOND = [(1, 0), (0, 1), (-1, 0), (0, -1)]
SQUARE = [(1, 1), (-1, 1), (-1, -1), (1, -1)]
titles = (it("B") + subs("1") + "(0, 1)", it("B") + "(0, 1)", it("B") + subs(INF) + "(0, 1)")
for k, p in enumerate(panels):
    if k == 0:
        p.polygon(DIAMOND, THEORY, 0.2)
    elif k == 1:
        disk_fill(p, 0, 0, 1, THEORY, 0.2)
    else:
        p.polygon(SQUARE, THEORY, 0.2)
    plain_axes(p)
    tick(p, "x", 1, "1", 4, 15, "start")
    tick(p, "x", -1, num(-1), -4, 15, "end")
    tick(p, "y", 1, "1", -5, -5, "end")
    tick(p, "y", -1, num(-1), -5, 15, "end")
    if k == 0:
        p.line(DIAMOND + [DIAMOND[0]], THEORY, 2.0, "6 4")
        for q in DIAMOND:
            hollow(p, q, THEORY, 3.3, 1.6)
    elif k == 1:
        p.circle(0, 0, 1, THEORY, 2.0, "6 4")
    else:
        p.line(SQUARE + [SQUARE[0]], THEORY, 2.0, "6 4")
        for q in SQUARE:
            hollow(p, q, THEORY, 3.3, 1.6)
    panel_title(p, titles[k], THEORY, 13)
save("birim-yuvarlar", figure(
    28 + 3 * W1 + 2 * GAP + 28, 34 + W1 + 14, panels,
    "&#8477;<sup>2</sup>'de üç açık birim yuvar. Solda 1-normuna göre <em>B</em><sub>1</sub>(0, 1) = "
    "{|<em>x</em>| + |<em>y</em>| &lt; 1}, ortada Öklid normuna göre <em>B</em>(0, 1) = "
    "{<em>x</em><sup>2</sup> + <em>y</em><sup>2</sup> &lt; 1}, sağda maksimum normuna göre "
    "<em>B</em><sub>&#8734;</sub>(0, 1) = (&#8722;1, 1) &#215; (&#8722;1, 1). Kesikli kenarlar ve içi boş "
    "köşeler yuvarlara ait değildir.",
    css_class=WIDE,
    aria="Three panels: the open unit ball of the 1-norm (a square with corners on the axes), of the Euclidean "
         "norm (a disc) and of the maximum norm (a square with sides parallel to the axes), all with dashed "
         "boundaries"))

# ============================================================
# yuvar-iki-iki: B_1((2, 2), 1) is the square with corners (1, 2), (2, 1), (3, 2), (2, 3)
# ============================================================
p = equal_panel(46, 30, 80, (0.0, 4.5), (0.0, 4.5))
p.axes((1, 2, 3), (1, 2, 3), it("x"), it("y"))
# the lines x = 2 and y = 2 separate the four cases
p.line([(2, 0), (2, 4.5)], TEXT, 0.8, "4 4", 0.35)
p.line([(0, 2), (4.5, 2)], TEXT, 0.8, "4 4", 0.35)
CORNERS = [(3.0, 2.0), (2.0, 3.0), (1.0, 2.0), (2.0, 1.0)]
p.polygon(CORNERS, THEORY, 0.2)
DOT = "2 3"
p.line([(0.5, 4.5), (4.5, 0.5)], TEXT, 1.1, DOT, 0.75)     # x + y = 5
p.line([(0.0, 3.0), (3.0, 0.0)], TEXT, 1.1, DOT, 0.75)     # x + y = 3
p.line([(0.0, 1.0), (3.5, 4.5)], TEXT, 1.1, DOT, 0.75)     # y - x = 1
p.line([(1.0, 0.0), (4.5, 3.5)], TEXT, 1.1, DOT, 0.75)     # x - y = 1
p.line(CORNERS + [CORNERS[0]], THEORY, 2.0, "6 4")
for q in CORNERS:
    hollow(p, q, THEORY, 3.4, 1.6)
p.points([(2.0, 2.0)], TEXT, 3.8)
p.label(2.0, 2.0, "(2, 2)", 6, -7, TEXT, 11.5)
# each corner label sits in the wedge left free by the two dotted lines and the grey guide
p.label(1.0, 2.0, "(1, 2)", 0, -22, TEXT, 11.5, "middle")
p.label(3.0, 2.0, "(3, 2)", 0, -22, TEXT, 11.5, "middle")
p.label(2.0, 3.0, "(2, 3)", 11, 4, TEXT, 11.5)
p.label(2.0, 1.0, "(2, 1)", 11, 4, TEXT, 11.5)
# the names of the dotted lines at their ends
p.label(4.5, 0.5, it("x") + " + " + it("y") + " = 5", 6, 4, TEXT, 11.5)
p.label(4.5, 3.5, it("x") + " " + MINUS + " " + it("y") + " = 1", 6, 4, TEXT, 11.5)
p.label(3.5, 4.5, it("y") + " " + MINUS + " " + it("x") + " = 1", 0, -8, TEXT, 11.5, "middle")
p.label(0.0, 3.0, it("x") + " + " + it("y") + " = 3", 7, -6, TEXT, 11.5)
save("yuvar-iki-iki", figure(
    520, 430, [p],
    "<em>B</em><sub>1</sub>((2, 2), 1) yuvarı: <em>x</em> + <em>y</em> = 5, <em>x</em> + <em>y</em> = 3, "
    "<em>y</em> &#8722; <em>x</em> = 1 ve <em>x</em> &#8722; <em>y</em> = 1 doğrularının sınırladığı, köşeleri "
    "(1, 2), (2, 1), (3, 2) ve (2, 3) olan karenin içi. Soluk kesikli <em>x</em> = 2 ve <em>y</em> = 2 doğruları "
    "dört durumu ayırır; karenin kenarları ve köşeleri yuvara ait değildir.",
    aria="The open 1-norm ball of radius 1 about (2, 2): a tilted square with corners (1, 2), (2, 1), (3, 2), "
         "(2, 3) cut out by four dotted lines, with the guide lines x = 2 and y = 2"))
