# -*- coding: utf-8 -*-
"""
Figures of the chapter "ℝⁿ Uzayı, İç Çarpım ve Norm"
(dersler/analiz-4/rn-uzayi-ic-carpim-ve-norm.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box and never directly under a heading.
The figures are NOT produced at build time. Run

    python scripts/analysis4_figures/nrm.py
    python scripts/center_figures.py "analysis4-nrm-*.md"
    python scripts/check_figure_labels.py "scripts/_figures/analysis4-nrm-*.md"

and paste the markup of scripts/_figures/analysis4-nrm-<name>.md into the .qmd.
The captions are Turkish on purpose; the aria labels are plain ASCII.
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, TEXT, THEORY, PRACTICE, BASE, REMARK  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "analysis4-nrm-"

MINUS, SQRT, NORM, THETA_S, PI_S = "&#8722;", "&#8730;", "&#8214;", "&#952;", "&#960;"
INF = "&#8734;"


def save(name, svg):
    (OUT_DIR / f"{PREFIX}{name}.md").write_text(svg, encoding="utf-8", newline="\n")
    print(f"{PREFIX}{name}.md")


def it(s):
    """Italic math letter inside an SVG <text>."""
    return f'<tspan font-style="italic">{s}</tspan>'


def subs(s, size=9):
    """Subscript inside an SVG <text>."""
    return f'<tspan font-size="{size}" dy="4">{s}</tspan><tspan dy="-4">&#8203;</tspan>'


def num(v):
    """Tick label with a real minus sign."""
    s = f"{v:g}"
    return s.replace("-", MINUS)


def equal_panel(x0, y0, ppu, xrange, yrange):
    """A panel with the same pixels per unit on both axes."""
    return Plot(x0, y0, ppu * (xrange[1] - xrange[0]), ppu * (yrange[1] - yrange[0]), xrange, yrange)


def plain_axes(p, xticks=(), yticks=(), opacity=0.45):
    """Unlabelled axes through the origin with small ticks; the vectors of these
    figures are called x and y, so the axes carry no letters."""
    p.origin_axes("", "", xticks, yticks, num, num, opacity)


# ============================================================
# toplama: a + b and a - b as the two diagonals of the parallelogram
# ============================================================
A, B = (3.0, 1.0), (1.0, 2.0)
p = equal_panel(40, 20, 56, (-1.0, 5.0), (-2.0, 4.0))
p.grid(xs=range(-1, 6), ys=range(-2, 5))
plain_axes(p, (1, 2, 3, 4), (-1, 1, 2, 3))
# the two missing sides of the parallelogram
p.line([A, (4.0, 3.0)], TEXT, 1.3, "5 4", 0.6)
p.line([B, (4.0, 3.0)], TEXT, 1.3, "5 4", 0.6)
# a - b twice: from the tip of b to the tip of a, and moved to the origin
p.arrow(B, A, BASE, 1.4, 7.0, "5 3")
p.arrow((0, 0), (2.0, -1.0), BASE, 2.0)
p.arrow((0, 0), A, THEORY, 2.0)
p.arrow((0, 0), B, PRACTICE, 2.0)
p.arrow((0, 0), (4.0, 3.0), TEXT, 2.6, 9.0)
p.label(3.0, 1.0, it("a") + " = (3, 1)", 8, 13, THEORY, 12)
# b's label sits above its tip: to the left it would hit the tick "2", to the right the dashed side
p.label(1.0, 2.0, it("b") + " = (1, 2)", -12, -12, PRACTICE, 12, "middle")
p.label(4.0, 3.0, it("a") + " + " + it("b") + " = (4, 3)", 0, -11, TEXT, 12, "middle", True)
p.label(2.0, -1.0, it("a") + " " + MINUS + " " + it("b") + " = (2, " + MINUS + "1)", 8, 12, BASE, 12)
# in the free triangle between the dashed diagonal, the sum and the dashed side at (3, 1)
p.label(2.78, 1.33, it("a") + " " + MINUS + " " + it("b"), 0, 0, BASE, 11.5, "middle")
save("toplama", figure(
    420, 380, [p],
    "<em>a</em> = (3, 1) ve <em>b</em> = (1, 2) için <em>a</em> + <em>b</em> = (4, 3), kenarları "
    "<em>a</em> ile <em>b</em> olan paralelkenarın orijinden çıkan köşegenidir. <em>b</em>'nin ucundan "
    "<em>a</em>'nın ucuna giden kesikli ok öbür köşegendir; orijine taşındığında "
    "<em>a</em> &#8722; <em>b</em> = (2, &#8722;1) vektörü olur.",
    aria="Vectors a and b in the plane, their sum as the diagonal of the parallelogram and their "
         "difference drawn from the tip of b and from the origin"))

# ============================================================
# aci: the angle between x = (3, 1) and y = (1, 2) is pi/4
# ============================================================
X, Y = (3.0, 1.0), (1.0, 2.0)
p = equal_panel(30, 20, 92, (-0.5, 3.5), (-0.5, 2.5))
plain_axes(p, (1, 2, 3), (1, 2))
t0, t1 = math.atan2(X[1], X[0]), math.atan2(Y[1], Y[0])
p.arc(0, 0, 0.55, t0, t1, TEXT, 1.4, None, 0.85)
p.line([Y, X], TEXT, 1.3, "5 4", 0.75)
p.arrow((0, 0), X, THEORY, 2.2)
p.arrow((0, 0), Y, PRACTICE, 2.2)
tm = (t0 + t1) / 2
p.label(0.78 * math.cos(tm), 0.78 * math.sin(tm), it(THETA_S) + " = " + PI_S + "/4", 0, 4, TEXT, 12, "middle")
p.label(3.0, 1.0, it("x") + " = (3, 1)", -2, 20, THEORY, 12, "middle")
p.label(1.0, 2.0, it("y") + " = (1, 2)", -8, -6, PRACTICE, 12, "end")
p.label(2.0, 1.5, it("x") + " " + MINUS + " " + it("y"), 7, -7, TEXT, 12)
save("aci", figure(
    420, 340, [p],
    "<em>x</em> = (3, 1) ile <em>y</em> = (1, 2) arasındaki açı "
    "<em>&#952;</em> = &#960;/4'tür. Kesikli kenar, kosinüs teoreminin kullandığı üçgenin "
    "üçüncü kenarıdır; uzunluğu &#8214;<em>x</em> &#8722; <em>y</em>&#8214; = &#8730;5'tir.",
    aria="Vectors x = (3, 1) and y = (1, 2) from the origin with the angle pi/4 between them "
         "and the dashed third side x minus y of the triangle"))

# ============================================================
# birim-egriler: the unit curves of the 1-norm, the Euclidean norm and the max norm
# ============================================================
R2 = math.sqrt(2.0)
p = equal_panel(40, 24, 110, (-1.6, 1.6), (-1.6, 1.6))
p.origin_axes("", "", (), (), num, num, 0.4)
# ticks placed by hand: the square and the circles pass through the usual spots
for v, anchor, dx, dy in ((1, "start", 5, 14), (-1, "end", -5, 14)):
    p.line([(v, -0.035), (v, 0.035)], TEXT, 1.0, None, 0.6)
    p.label(v, 0, num(v), dx, dy, TEXT, 11, anchor)
for v, dy in ((1, -6), (-1, 15)):
    p.line([(-0.035, v), (0.035, v)], TEXT, 1.0, None, 0.6)
    p.label(0, v, num(v), -6, dy, TEXT, 11, "end")
circ = [(math.cos(2 * math.pi * k / 200), math.sin(2 * math.pi * k / 200)) for k in range(201)]
p.line([(R2 * c, R2 * s) for c, s in circ], REMARK, 1.4, "6 4", 0.9)
p.line([(1, 1), (-1, 1), (-1, -1), (1, -1), (1, 1)], PRACTICE, 2.1)
p.line(circ, THEORY, 2.1)
p.line([(1, 0), (0, 1), (-1, 0), (0, -1), (1, 0)], BASE, 2.1)
p.points([(1, 0), (0, 1), (-1, 0), (0, -1)], TEXT, 3.6)
# legend to the right of the drawing
LX, LY = 1.75, 1.25
rows = ((BASE, None, NORM + it("x") + NORM + subs("1") + " = 1"),
        (THEORY, None, NORM + it("x") + NORM + " = 1"),
        (PRACTICE, None, NORM + it("x") + NORM + subs(INF) + " = 1"),
        (REMARK, "6 4", NORM + it("x") + NORM + " = " + SQRT + "2"))
for k, (col, dash, txt) in enumerate(rows):
    yy = LY - 0.3 * k
    p.line([(LX, yy), (LX + 0.3, yy)], col, 2.1 if dash is None else 1.4, dash)
    p.label(LX + 0.3, yy, txt, 8, 4, col, 12)
save("birim-egriler", figure(
    560, 400, [p],
    "En içte &#8214;<em>x</em>&#8214;<sub>1</sub> = 1 karesi, ortada &#8214;<em>x</em>&#8214; = 1 birim "
    "çemberi, en dışta &#8214;<em>x</em>&#8214;<sub>&#8734;</sub> = 1 karesi vardır; üçü (&#177;1, 0) ve "
    "(0, &#177;1) noktalarında birbirine değer. Kesikli &#8214;<em>x</em>&#8214; = &#8730;2 çemberi "
    "dış karenin köşelerinden geçer.",
    aria="Unit curves of the 1-norm, the Euclidean norm and the maximum norm nested inside each other, "
         "touching at the four points on the axes, and the dashed circle of radius square root of 2"))

# ============================================================
# paralelkenar: the parallelogram law for x = (1, 2), y = (3, -1)
# ============================================================
X, Y, S = (1.0, 2.0), (3.0, -1.0), (4.0, 1.0)
p = equal_panel(40, 20, 64, (-1.0, 4.8), (-1.6, 2.7))
plain_axes(p, (), ())
p.line([X, S, Y], TEXT, 1.5)
p.arrow((0, 0), S, BASE, 2.8, 10.0)
p.arrow(Y, X, REMARK, 2.8, 10.0)
p.arrow((0, 0), X, THEORY, 2.2)
p.arrow((0, 0), Y, PRACTICE, 2.2)
p.points([(0, 0)], TEXT, 3.0)
p.label(0, 0, it("O"), -7, 15, TEXT, 12, "end")
p.label(1.0, 2.0, it("x"), -9, -3, THEORY, 13, "end", True)
p.label(3.0, -1.0, it("y"), 6, 15, PRACTICE, 13, "start", True)
p.label(4.0, 1.0, it("x") + " + " + it("y"), 9, 5, BASE, 12.5, "start", True)
p.label(1.7, 0.95, it("x") + " " + MINUS + " " + it("y"), 9, 4, REMARK, 12.5, "start", True)
# side lengths, pushed outward from the middle of each side
p.label(0.5, 1.0, SQRT + "5", -9, 4, TEXT, 12, "end")
p.label(3.59, 0.18, SQRT + "5", 8, 0, TEXT, 12, "start")
p.label(1.5, -0.5, SQRT + "10", -4, 17, TEXT, 12, "middle")
p.label(2.5, 1.5, SQRT + "10", 5, -9, TEXT, 12, "middle")
# diagonal lengths
p.label(3.0, 0.75, SQRT + "17", 0, -8, BASE, 12, "middle")
p.label(2.5, -0.25, SQRT + "13", -8, 10, REMARK, 12, "end")
save("paralelkenar", figure(
    440, 330, [p],
    "<em>x</em> = (1, 2) ve <em>y</em> = (3, &#8722;1) üzerine kurulan paralelkenar. Kenar uzunlukları "
    "&#8730;5 ve &#8730;10, köşegenler <em>x</em> + <em>y</em> (&#8730;17) ve <em>x</em> &#8722; <em>y</em> "
    "(&#8730;13) uzunluğundadır: 17 + 13 = 2(5 + 10).",
    aria="Parallelogram spanned by x = (1, 2) and y = (3, -1) with its diagonals x + y and x - y "
         "and the side and diagonal lengths"))
