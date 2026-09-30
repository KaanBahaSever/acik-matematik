# -*- coding: utf-8 -*-
"""
Figures of the chapter "ℝⁿ'de Diziler ve Yakınsaklık"
(dersler/analiz-4/rn-de-diziler-ve-yakinsaklik.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box: a figure that illustrates a
definition sits directly below that box. The figures are NOT produced at
build time. Run

    python scripts/analysis4_figures/diz.py
    python scripts/center_figures.py "analysis4-diz-*.md"
    python scripts/check_figure_labels.py "scripts/_figures/analysis4-diz-*.md"

and paste the markup of scripts/_figures/analysis4-diz-<name>.md into the
.qmd. Captions are Turkish on purpose (they are shown on the site); aria
labels are plain ASCII.

Conventions: a boundary that belongs to the set is a solid line, one that does
not is dashed (every region drawn here is open, so all boundaries are dashed);
points of the set are filled, excluded points are hollow. Every drawing that
contains a circle uses equal x and y scales.
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, disk_fill, dot, hollow, WIDE, TEXT, THEORY, PRACTICE, BASE  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "analysis4-diz-"

MINUS, EPS, SQRT = "&#8722;", "&#949;", "&#8730;"


def it(s):
    """Italic run inside an SVG <text>."""
    return f'<tspan font-style="italic">{s}</tspan>'


def sub(s, size=8.5):
    """Subscript inside an SVG <text>."""
    return f'<tspan font-size="{size}" dy="3.5">{s}</tspan><tspan dy="-3.5">&#8203;</tspan>'


def xk(k):
    """The label x_k."""
    return it("x") + sub(str(k))


def eq_plot(x0, y0, ppu, xr, yr):
    """Panel with the same number of pixels per unit on both axes."""
    return Plot(x0, y0, (xr[1] - xr[0]) * ppu, (yr[1] - yr[0]) * ppu, xr, yr)


def tick(p, x, y, horizontal):
    """Short tick mark across an axis at data point (x, y)."""
    X, Y = p.X(x), p.Y(y)
    if horizontal:
        p.add(f'<line x1="{X:.1f}" y1="{Y - 3:.1f}" x2="{X:.1f}" y2="{Y + 3:.1f}" stroke="{TEXT}" stroke-width="1" opacity="0.6"/>')
    else:
        p.add(f'<line x1="{X - 3:.1f}" y1="{Y:.1f}" x2="{X + 3:.1f}" y2="{Y:.1f}" stroke="{TEXT}" stroke-width="1" opacity="0.6"/>')


def save(name, markup):
    (OUT_DIR / f"{PREFIX}{name}.md").write_text(markup, encoding="utf-8", newline="\n")
    print(f"{PREFIX}{name}.md")


# ============================================================ yakinsak-yuvar
# x_k = (1/k, 1 + (-1)^k / k) -> (0, 1); with eps = 0.3 the terms from k = 5 on
# lie in B((0, 1), 0.3) because ||x_k - (0, 1)|| = sqrt(2)/k.
EPS_V, K_MAX = 0.3, 12
terms = [(1 / k, 1 + (-1) ** k / k) for k in range(1, K_MAX + 1)]
assert all((math.sqrt(2) / k < EPS_V) == (k >= 5) for k in range(1, K_MAX + 1))
p = eq_plot(40, 30, 205, (-0.62, 1.2), (-0.16, 1.68))
p.origin_axes("", "", opacity=0.45)
for v, s in ((0.5, "1/2"), (1.0, "1")):
    tick(p, v, 0, True)
    p.label(v, 0, s, 0, 16, TEXT, 11, "middle")
for v, s in ((0.5, "1/2"), (1.5, "3/2")):
    tick(p, 0, v, False)
    p.label(0, v, s, -7, 4, TEXT, 11, "end")
# the ball B((0, 1), 0.3)
disk_fill(p, 0, 1, EPS_V, BASE, 0.13)
p.circle(0, 1, EPS_V, BASE, 1.6, "5 3")
ang = math.radians(135)
end = (EPS_V * math.cos(ang), 1 + EPS_V * math.sin(ang))
p.line([(0, 1), end], BASE, 1.2)
p.label(end[0], end[1], EPS + " = 0,3", -3, -6, BASE, 12, "end")
# consecutive terms joined by a faint polyline
p.line(terms, TEXT, 0.9, None, 0.35)
p.points(terms[:4], PRACTICE, 3.8)
p.points(terms[4:], THEORY, 3.0)
dot(p, (0, 1), BASE, 4.2)
p.label(0, 1, "(0, 1)", -8, 4, BASE, 12, "end")
# names of the first four terms
p.label(*terms[0], xk(1), 7, -7, PRACTICE, 12.5)
p.label(*terms[1], xk(2), 7, -6, PRACTICE, 12.5)
p.label(*terms[2], xk(3), 8, 5, PRACTICE, 12.5)
p.label(*terms[3], xk(4), 8, 2, PRACTICE, 12.5)
save("yakinsak-yuvar", figure(
    420, 420, [p],
    "<em>x<sub>k</sub></em> = (1/<em>k</em>, 1 + (&#8722;1)<sup><em>k</em></sup>/<em>k</em>) dizisinin ilk 12 terimi; "
    "ardışık terimler ince çizgiyle birleştirildi. İkinci bileşen 1'in bir altına bir üstüne sıçrar. "
    "&#949; = 0,3 için <em>x</em><sub>1</sub>, &#8230;, <em>x</em><sub>4</sub> (turuncu) "
    "<em>B</em>((0, 1), 0,3) yuvarının dışında, <em>x</em><sub>5</sub> ve sonraki terimler (mavi) içindedir.",
    aria="Terms of a planar sequence zigzagging towards the point (0, 1); the first four lie outside the ball of radius 0.3, the rest inside"))

# ============================================================ iraksak-iki-kume
# x_k = ((-1)^k, 1/2^k) is divergent: for the candidate a = (0.3, 0) the ball
# B(a, 1) misses every odd term, since ||x_k - a|| >= |-1 - 0.3| = 1.3.
A_C, E0, K_MAX = (0.3, 0.0), 1.0, 10
odd = [(-1.0, 0.5 ** k) for k in range(1, K_MAX + 1, 2)]
even = [(1.0, 0.5 ** k) for k in range(2, K_MAX + 1, 2)]
assert all(math.hypot(x - A_C[0], y - A_C[1]) >= 1.3 for x, y in odd)
assert all(math.hypot(x - A_C[0], y - A_C[1]) < E0 for x, y in even)
p = eq_plot(40, 30, 132, (-1.6, 1.6), (-1.12, 1.12))
p.origin_axes("", "", opacity=0.45)
# the candidate a and the ball B(a, eps0)
disk_fill(p, A_C[0], A_C[1], E0, THEORY, 0.12)
p.circle(A_C[0], A_C[1], E0, THEORY, 1.7, "6 4")
p.line([A_C, (A_C[0], A_C[1] - E0)], THEORY, 1.3)
p.label(A_C[0], -E0 / 2, EPS + sub("0") + " = 1", 6, 4, THEORY, 12.5)
dot(p, A_C, THEORY, 3.8)
p.label(*A_C, it("a"), 0, -9, THEORY, 13, "middle", True)
# the two clusters (-1, 0) and (1, 0), which are not terms of the sequence
hollow(p, (-1, 0), TEXT, 4.6)
hollow(p, (1, 0), TEXT, 4.6)
p.label(-1, 0, "(" + MINUS + "1, 0)", 0, 19, TEXT, 11.5, "middle")
p.label(1, 0, "(1, 0)", 0, 19, TEXT, 11.5, "middle")
# odd terms (all outside the ball) and even terms (inside)
p.points(odd, PRACTICE, 3.4)
p.points(even, BASE, 3.4)
p.label(*odd[0], xk(1), -8, 4, PRACTICE, 12.5, "end")
p.label(*even[0], xk(2), -8, 4, BASE, 12.5, "end")
p.label(-1, 0.5, "tek " + it("k"), 0, -14, PRACTICE, 11.5, "middle")
p.label(1, 0.25, "çift " + it("k"), 0, -14, BASE, 11.5, "middle")
save("iraksak-iki-kume", figure(
    480, 360, [p],
    "<em>x<sub>k</sub></em> = ((&#8722;1)<sup><em>k</em></sup>, 1/2<sup><em>k</em></sup>) dizisinin ilk 10 terimi. "
    "Aday nokta <em>a</em> = (0,3; 0) için &#949;<sub>0</sub> = 1 yarıçaplı yuvar tek indisli terimlerin hiçbirini "
    "içermez: bu terimlerin <em>a</em>'ya uzaklığı en az 1,3'tür. <em>a</em> nereye konursa konsun, "
    "(&#8722;1, 0) ile (1, 0) arasındaki uzaklık 2 olduğundan iki terim grubundan biri bu yuvarın dışında kalır.",
    aria="Odd terms near (-1, 0) and even terms near (1, 0); a ball of radius one around a candidate limit a misses all odd terms"))

# ============================================================ kare-yuvar
# Norm versus components around a: the square of half side eps/sqrt(2) lies in
# B(a, eps), which lies in the square of half side eps (eps = 1 in the drawing).
S = 1 / math.sqrt(2)
p = eq_plot(40, 30, 118, (-1.3, 1.3), (-1.3, 1.3))
# faint coordinate cross through a
p.line([(-1.25, 0), (1.25, 0)], TEXT, 0.9, "2 3", 0.4)
p.line([(0, -1.25), (0, 1.25)], TEXT, 0.9, "2 3", 0.4)
outer = [(-1, -1), (1, -1), (1, 1), (-1, 1), (-1, -1)]
inner = [(-S, -S), (S, -S), (S, S), (-S, S), (-S, -S)]
p.line(outer, TEXT, 1.3, "7 4", 0.75)
disk_fill(p, 0, 0, 1, THEORY, 0.13)
p.circle(0, 0, 1, THEORY, 1.8, "5 3")
p.polygon(inner[:-1], PRACTICE, 0.2)
p.line(inner, PRACTICE, 1.6, "3 3")
# radius eps (horizontal) and half side eps/sqrt(2) (vertical)
p.line([(0, 0), (1, 0)], THEORY, 1.4)
p.label(0.5, 0, EPS, 0, -6, THEORY, 13, "middle")
p.line([(0, 0), (0, -S)], PRACTICE, 1.4)
p.label(0, -S / 2, EPS + "/" + SQRT + "2", 5, 5, PRACTICE, 12)
dot(p, (0, 0), TEXT, 3.6)
p.label(0, 0, it("a"), -6, -7, TEXT, 13, "end", True)
# legend on the right, in a faint frame (the frame also keeps the canvas wide
# enough for the label checker's generous text-width estimate)
LX, LY0, DY = 1.62, 0.34, 0.34
fx0, fx1 = p.X(LX - 0.14), p.X(LX + 0.3) + 8 + 188
fy0, fy1 = p.Y(LY0 + 0.24), p.Y(LY0 - 2 * DY - 0.2)
p.add(f'<rect x="{fx0:.1f}" y="{fy0:.1f}" width="{fx1 - fx0:.1f}" height="{fy1 - fy0:.1f}" rx="6" '
      f'fill="none" stroke="{TEXT}" stroke-width="0.9" opacity="0.3"/>')
p.line([(LX, LY0), (LX + 0.3, LY0)], TEXT, 1.3, "7 4", 0.75)
p.label(LX + 0.3, LY0, "her " + it("i") + " için |" + it("z") + sub(it("i")) + " " + MINUS + " "
        + it("a") + sub(it("i")) + "| &lt; " + EPS, 8, 4, TEXT, 12)
p.line([(LX, LY0 - DY), (LX + 0.3, LY0 - DY)], THEORY, 1.8, "5 3")
p.label(LX + 0.3, LY0 - DY, it("B") + "(" + it("a") + ", " + EPS + ")", 8, 4, THEORY, 12)
p.line([(LX, LY0 - 2 * DY), (LX + 0.3, LY0 - 2 * DY)], PRACTICE, 1.6, "3 3")
p.label(LX + 0.3, LY0 - 2 * DY, "her " + it("i") + " için |" + it("z") + sub(it("i")) + " " + MINUS + " "
        + it("a") + sub(it("i")) + "| &lt; " + EPS + "/" + SQRT + "2", 8, 4, PRACTICE, 12)
save("kare-yuvar", figure(
    660, 380, [p],
    "<em>a</em> merkezli üç bölge (üçü de açık). Turuncu karenin her noktasında bileşen farkları &#949;/&#8730;2'den "
    "küçüktür ve bu kare <em>B</em>(<em>a</em>, &#949;) yuvarının içindedir: bileşen farkları "
    "&#949;/&#8730;2'den küçükse nokta yuvardadır. Yuvar da kesikli gri karenin içindedir: nokta yuvardaysa "
    "her bileşen farkı &#949;'dan küçüktür.",
    css_class=WIDE, aria="A small square inside a disc inside a larger square, all centred at a, with the radius eps and the half side eps over root two"))
