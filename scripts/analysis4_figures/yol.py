# -*- coding: utf-8 -*-
"""
Figures of the chapter "Yollar Boyunca Limit ve Ardışık Limitler"
(dersler/analiz-4/yollar-boyunca-limit-ve-ardisik-limitler.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box and never directly under a heading.
The figures are NOT produced at build time. Run

    python scripts/analysis4_figures/yol.py
    python scripts/center_figures.py "analysis4-yol-*.md"
    python scripts/check_figure_labels.py "scripts/_figures/analysis4-yol-*.md"

and paste the markup of scripts/_figures/analysis4-yol-<name>.md into the .qmd.
The captions are Turkish on purpose; the aria labels are plain ASCII.

Values of a function on the plane are shown by a few labelled level curves,
not by a colour scale, so that the figures read the same in both themes.
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, hollow, WIDE, TEXT, THEORY, PRACTICE, BASE, REMARK  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "analysis4-yol-"

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
    """Tick label with a real minus sign."""
    return f"{v:g}".replace("-", MINUS)


def frac(s):
    """A value such as '-2/5' with a real minus sign."""
    return s.replace("-", MINUS)


def equal_panel(x0, y0, ppu, xrange, yrange):
    """A panel with the same pixels per unit on both axes."""
    return Plot(x0, y0, ppu * (xrange[1] - xrange[0]), ppu * (yrange[1] - yrange[0]), xrange, yrange)


def graph_pts(f, x0, x1, n=160):
    return [(x0 + (x1 - x0) * k / n, f(x0 + (x1 - x0) * k / n)) for k in range(n + 1)]


def head_along(p, path, i, color, width=1.8, head=8.0):
    """Arrowhead on a sampled path, pointing from path[i - 2] to path[i]."""
    a, b = path[i - 2], path[i]
    X0, Y0, X1, Y1 = p.X(a[0]), p.Y(a[1]), p.X(b[0]), p.Y(b[1])
    L = math.hypot(X1 - X0, Y1 - Y0) or 1.0
    ux, uy = (X1 - X0) / L, (Y1 - Y0) / L
    hw = head * 0.42
    p.add(f'<polygon points="{X1:.1f},{Y1:.1f} {X1 - ux * head - uy * hw:.1f},{Y1 - uy * head + ux * hw:.1f} '
          f'{X1 - ux * head + uy * hw:.1f},{Y1 - uy * head - ux * hw:.1f}" fill="{color}"/>')


def to_origin(f, x_far, n=120):
    """Samples of the graph y = f(x) from x_far towards 0 (the direction of travel)."""
    return [(x_far * (1 - k / n), f(x_far * (1 - k / n))) for k in range(n + 1)]


# ============================================================
# yollar: a line, a parabola, the y axis, a spiral and a sequence, all going to (0, 0)
# ============================================================
p = equal_panel(40, 24, 165, (-1.25, 1.25), (-1.25, 1.25))
p.origin_axes("", "", (), (), num, num, 0.3)
W = 2.0
# the line y = x/2, from both ends
for xf in (1.2, -1.2):
    path = to_origin(lambda x: x / 2, xf)
    p.line(path, THEORY, W)
    head_along(p, path, 70, THEORY)
# the parabola y = x^2, from both branches
for xf in (1.0, -1.0):
    path = to_origin(lambda x: x * x, xf)
    p.line(path, PRACTICE, W)
    head_along(p, path, 62, PRACTICE)
# the y axis
for yf in (1.2, -1.2):
    path = [(0.0, yf * (1 - k / 120)) for k in range(121)]
    p.line(path, BASE, W)
    head_along(p, path, 70, BASE)
# the logarithmic spiral (e^-t cos t, e^-t sin t), 0 <= t <= 12
spiral = [(math.exp(-t) * math.cos(t), math.exp(-t) * math.sin(t)) for t in (12 * k / 900 for k in range(901))]
p.line(spiral, REMARK, 1.8)
head_along(p, spiral, 60, REMARK)
head_along(p, spiral, 150, REMARK, 1.8, 7.0)
# the sequence x_k = (1/k, -1/k)
p.points([(1 / k, -1 / k) for k in range(1, 9)], TEXT, 3.0)
hollow(p, (0, 0), TEXT, 4.2, 1.7)
p.label(0, 0, it("x") + subs("0"), -12, 19, TEXT, 13, "end")
p.label(1.2, 0.6, "doğru", -2, -10, THEORY, 12.5, "end")
p.label(-1.0, 1.0, "parabol", -7, 4, PRACTICE, 12.5, "end")
p.label(0.0, 1.2, "eksen", 7, 4, BASE, 12.5)
p.label(1.0, 0.0, "sarmal", 6, 18, REMARK, 12.5)
p.label(1.0, -1.0, "dizi", 8, 4, TEXT, 12.5)
save("yollar", figure(
    500, 470, [p],
    "(0, 0) noktasına giden yollar: <em>y</em> = <em>x</em>/2 doğrusu, <em>y</em> = <em>x</em><sup>2</sup> "
    "parabolü, <em>y</em> ekseni, (<em>e</em><sup>&#8722;<em>t</em></sup> cos <em>t</em>, "
    "<em>e</em><sup>&#8722;<em>t</em></sup> sin <em>t</em>) sarmalı ve <em>x<sub>k</sub></em> = "
    "(1/<em>k</em>, &#8722;1/<em>k</em>) dizisi. Hiçbiri <em>x</em><sub>0</sub> = (0, 0) noktasının kendisinden "
    "geçmez; limit varsa her biri boyunca aynı değeri verir.",
    aria="Five ways to approach the origin: the line y = x/2 from both sides, both branches of the parabola "
         "y = x^2, the y axis from above and below, a logarithmic spiral and the sequence (1/k, -1/k)"))

# ============================================================
# dogrular: f = xy/(x^2 + y^2) is constant m/(1 + m^2) on every line y = mx
# ============================================================
p = equal_panel(56, 34, 150, (-1.0, 1.0), (-1.0, 1.0))
# a light tint for the sign of f: positive in the first and third quadrants
p.polygon([(0, 0), (1, 0), (1, 1), (0, 1)], PRACTICE, 0.09)
p.polygon([(0, 0), (-1, 0), (-1, -1), (0, -1)], PRACTICE, 0.09)
p.polygon([(0, 0), (-1, 0), (-1, 1), (0, 1)], THEORY, 0.09)
p.polygon([(0, 0), (1, 0), (1, -1), (0, -1)], THEORY, 0.09)
p.line([(-1, -1), (1, -1), (1, 1), (-1, 1), (-1, -1)], TEXT, 1.0, None, 0.45)
# (end point, value) for each line through the origin; the other end is the mirror image
LINES = (((1.0, 0.0), "0"), ((1.0, 0.5), "2/5"), ((1.0, 1.0), "1/2"), ((0.5, 1.0), "2/5"),
         ((0.0, 1.0), "0"), ((-0.5, 1.0), "-2/5"), ((-1.0, 1.0), "-1/2"), ((-1.0, 0.5), "-2/5"))


def value_color(v):
    return TEXT if v == "0" else (THEORY if v.startswith("-") else PRACTICE)


def end_label(p, e, s, color):
    """Value written just outside the square, beyond the end point e."""
    x, y = e
    if abs(x) == 1.0 and abs(y) < 1.0:            # left or right edge
        p.label(x, y, s, 8 if x > 0 else -8, 4, color, 12, "start" if x > 0 else "end")
    elif abs(y) == 1.0 and abs(x) < 1.0:          # top or bottom edge
        p.label(x, y, s, 0, -8 if y > 0 else 17, color, 12, "middle")
    else:                                         # a corner
        p.label(x, y, s, 6 if x > 0 else -6, -6 if y > 0 else 15, color, 12, "start" if x > 0 else "end")


for e, v in LINES:
    col = value_color(v)
    p.line([(-e[0], -e[1]), e], col, 1.8, None, 0.9 if col != TEXT else 0.6)
for e, v in LINES:
    col = value_color(v)
    end_label(p, e, frac(v), col)
    end_label(p, (-e[0], -e[1]), frac(v), col)
hollow(p, (0, 0), TEXT, 4.2, 1.7)
save("dogrular", figure(
    420, 400, [p],
    "<em>f</em>(<em>x</em>, <em>y</em>) = <em>xy</em>/(<em>x</em><sup>2</sup> + <em>y</em><sup>2</sup>) "
    "fonksiyonu orijinden geçen her <em>y</em> = <em>mx</em> doğrusu üzerinde <em>m</em>/(1 + <em>m</em><sup>2</sup>) "
    "değerini alır; doğruların uçlarındaki sayılar bu değerlerdir (<em>m</em> = 0, &#177;1/2, &#177;1, &#177;2 ve "
    "<em>x</em> = 0). Hafif tonlar <em>f</em>'nin işaretini gösterir: birinci ve üçüncü bölgede pozitif, "
    "ikinci ve dördüncüde negatif. Orijinin her komşuluğunda <em>f</em>, [&#8722;1/2, 1/2] aralığındaki bütün "
    "değerleri alır.",
    aria="The square from -1 to 1 with the lines y = mx for m = 0, 1/2, 1, 2, -1/2, -1, -2 and the y axis "
         "through the hollow origin, each line labelled with the constant value m/(1 + m^2) of xy/(x^2 + y^2)"))

# ============================================================
# parabol: f = x^2 y/(x^4 + y^2) goes to 0 along lines but equals 1/2 on y = x^2
# ============================================================
PPU = 130
left = equal_panel(64, 30, PPU, (-1.0, 1.0), (-1.0, 1.0))
GAP = 96
# a little room beyond x = 1 keeps the tick label 1 clear of the arrow tip and the axis letter
right = Plot(64 + 2 * PPU + GAP, 30, 2.3 * PPU, 2 * PPU, (-1.15, 1.15), (-0.6, 0.6))
left.origin_axes("", "", (), (), num, num, 0.3)
left.line([(-1, -1), (1, -1), (1, 1), (-1, 1), (-1, -1)], TEXT, 1.0, None, 0.4)
# level curves y = k x^2 and the values k/(1 + k^2) at their right ends
LEVELS = ((4.0, "4/17"), (2.0, "2/5"), (1.0, "1/2"), (0.5, "2/5"))
for k, v in LEVELS:
    for s in (1, -1):
        xe = min(1.0, 1.0 / math.sqrt(k))
        if k == 1.0 and s == 1:
            continue
        left.line(graph_pts(lambda x: s * k * x * x, -xe, xe, 120), TEXT, 1.0, None, 0.45)
        if xe < 1.0:
            # with a minus sign the two bottom labels need a little more room between them
            nudge = 0 if s > 0 else (-3 if k == 4.0 else 3)
            left.label(xe, s, frac(("-" if s < 0 else "") + v), nudge, -7 if s > 0 else 16, TEXT, 11, "middle")
        else:
            ye = s * k
            dy = 4 if abs(ye) < 1.0 else (-5 if s > 0 else 14)
            left.label(1.0, ye, frac(("-" if s < 0 else "") + v), 7, dy, TEXT, 11)
# the two lines and the parabola y = x^2
left.line([(-1, -1), (1, 1)], THEORY, 2.0)
left.line([(-0.5, -1), (0.5, 1)], THEORY, 2.0, "6 4")
left.line(graph_pts(lambda x: x * x, -1.0, 1.0, 160), PRACTICE, 2.8)
hollow(left, (0, 0), TEXT, 4.0, 1.7)
left.label(1.0, 1.0, "1/2", 7, -5, PRACTICE, 11)
left.label(-1.0, -1.0, it("y") + " = " + it("x"), -7, 4, THEORY, 12, "end")
left.label(-0.5, -1.0, it("y") + " = 2" + it("x"), 0, 17, THEORY, 12, "middle")
left.label(-1.0, 1.0, it("y") + " = " + it("x") + sups("2"), -7, 4, PRACTICE, 12, "end")
# right panel: f along the three paths
right.origin_axes(it("x"), it("f"), (), (), num, num, 0.45)
for v, s in ((-1.0, MINUS + "1"), (1.0, "1")):
    right.line([(v, -0.02), (v, 0.02)], TEXT, 1.0, None, 0.6)
    right.label(v, 0, s, 0, 15, TEXT, 11, "middle")
for v, s in ((0.5, "1/2"), (-0.5, MINUS + "1/2")):
    right.line([(-0.017, v), (0.017, v)], TEXT, 1.0, None, 0.6)
right.label(0, 0.5, "1/2", -6, -5, TEXT, 11, "end")
right.label(0, -0.5, MINUS + "1/2", -6, 4, TEXT, 11, "end")
g1 = graph_pts(lambda x: x / (x * x + 1), -1.0, 1.0, 200)
g2 = graph_pts(lambda x: 2 * x / (x * x + 4), -1.0, 1.0, 200)
right.line(g2, THEORY, 2.0, "6 4")
right.line(g1, THEORY, 2.0)
right.line([(-1.0, 0.5), (1.0, 0.5)], PRACTICE, 2.8)
hollow(right, (0, 0), THEORY, 4.0, 1.7)
hollow(right, (0, 0.5), PRACTICE, 4.0, 1.7)
right.label(-1.0, -0.5, it("f") + "(" + it("x") + ", " + it("x") + ")", -7, 4, THEORY, 12, "end")
right.label(-1.0, -0.4, it("f") + "(" + it("x") + ", 2" + it("x") + ")", -7, -1, THEORY, 12, "end")
right.label(0.62, 0.5, it("f") + "(" + it("x") + ", " + it("x") + sups("2") + ") = 1/2", 0, -9, PRACTICE, 12,
            "middle")
save("parabol", figure(
    64 + 4.3 * PPU + GAP + 30, 30 + 2 * PPU + 28, [left, right],
    "Solda <em>f</em>(<em>x</em>, <em>y</em>) = <em>x</em><sup>2</sup><em>y</em>/(<em>x</em><sup>4</sup> + "
    "<em>y</em><sup>2</sup>) fonksiyonunun <em>y</em> = <em>kx</em><sup>2</sup> düzey eğrileri (<em>k</em> = "
    "&#177;1/2, &#177;1, &#177;2, &#177;4) ve uçlarında <em>k</em>/(1 + <em>k</em><sup>2</sup>) değerleri; "
    "<em>y</em> = <em>x</em> ve <em>y</em> = 2<em>x</em> doğruları orijine yaklaştıkça bu eğrilerden gittikçe "
    "dikleşenlerini keser. Sağda <em>f</em>'nin üç yol boyunca aldığı değerler: <em>f</em>(<em>x</em>, <em>x</em>) "
    "= <em>x</em>/(<em>x</em><sup>2</sup> + 1) ve <em>f</em>(<em>x</em>, 2<em>x</em>) = 2<em>x</em>/(<em>x</em><sup>2</sup> "
    "+ 4) sıfıra gider, <em>f</em>(<em>x</em>, <em>x</em><sup>2</sup>) ise sabit 1/2'dir.",
    css_class=WIDE,
    aria="Left: level curves y = k x^2 of x^2 y/(x^4 + y^2) with their values, the lines y = x and y = 2x and "
         "the parabola y = x^2. Right: f along y = x and y = 2x tends to 0, along y = x^2 it stays 1/2"))
