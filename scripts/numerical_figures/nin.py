# -*- coding: utf-8 -*-
"""
Figures of the chapter "Nümerik İntegrasyon"
(dersler/numerik-analiz/numerik-integrasyon.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box and never directly under a heading.
The node diagram of the closed and open Newton-Cotes formulas sits directly
below the definition box of the open formula.
The figures are NOT produced at build time. Run

    python scripts/numerical_figures/nin.py
    python scripts/center_figures.py "numerical-nin-*.md"
    python scripts/check_figure_labels.py "scripts/_figures/numerical-nin-*.md"

and paste the markup of scripts/_figures/numerical-nin-<name>.md into the .qmd.
Captions are Turkish on purpose; aria labels are plain ASCII.
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, TEXT, THEORY, PRACTICE, REMARK, BG  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "numerical-nin-"

MINUS = "&#8722;"
APPROX = "&#8776;"


def save(name, markup):
    (OUT_DIR / f"{PREFIX}{name}.md").write_text(markup, encoding="utf-8", newline="\n")
    print(f"{PREFIX}{name}.md")


def it(s):
    """Italic run inside an SVG <text>."""
    return f'<tspan font-style="italic">{s}</tspan>'


def sup(s, size=10):
    """Superscript inside an SVG <text>."""
    return f'<tspan font-size="{size}" dy="-5">{s}</tspan><tspan dy="5">&#8203;</tspan>'


def sub(s, size=10):
    """Subscript inside an SVG <text>."""
    return f'<tspan font-size="{size}" dy="3">{s}</tspan><tspan dy="-3">&#8203;</tspan>'


def xs(k):
    """x_k with an italic x."""
    return it("x") + sub(k)


def f(x):
    return 4.0 / (1.0 + x * x)


def p2(x):
    """Quadratic through (0, 4), (0.5, 3.2), (1, 2)."""
    return 4.0 - 1.2 * x - 0.8 * x * x


def samples(g, a, b, n=200):
    return [(a + (b - a) * k / n, g(a + (b - a) * k / n)) for k in range(n + 1)]


def leader(p, a, b, color=TEXT, opacity=0.75):
    """Thin pointer line from data point a to data point b."""
    p.line([a, b], color, 0.9, None, opacity)


def xaxis_marks(p, marks):
    """Tick marks with labels below the x axis: marks = [(x, label), ...]."""
    oy = p.Y(0)
    for x, s in marks:
        p.add(f'<line x1="{p.X(x):.1f}" y1="{oy - 3:.1f}" x2="{p.X(x):.1f}" y2="{oy + 3:.1f}" '
              f'stroke="{TEXT}" stroke-width="1" opacity="0.7"/>')
        p.label(x, 0, s, 0, 17, TEXT, 11.5, "middle")


XR, YR = (-0.1, 1.15), (0.0, 4.4)
PW, PH = 420, 330


def frame():
    p = Plot(60, 30, PW, PH, XR, YR)
    p.origin_axes(it("x"), it("y"), (), (1, 2, 3, 4), opacity=0.5)
    return p


# ============================================================
# yamuk: trapezoidal rule for 4/(1 + x^2) on [0, 1]
# ============================================================
p = frame()
curve = samples(f, 0, 1)
# trapezoid under the chord from (0, 4) to (1, 2)
p.polygon([(0, 0), (1, 0), (1, 2), (0, 4)], THEORY, 0.16, THEORY, 1.4)
# the sliver between the curve and the chord: the error of the rule
p.polygon(curve + [(0, 4)], PRACTICE, 0.55)
p.line(curve, THEORY, 2.4)
p.line(samples(f, -0.1, 0, 10), THEORY, 2.4, None, 0.4)
p.line(samples(f, 1, 1.15, 20), THEORY, 2.4, None, 0.4)
p.points([(0, 4), (1, 2)], THEORY, 3.8)
xaxis_marks(p, [(0, xs("0") + " = 0"), (0.5, "0,5"), (1, xs("1") + " = 1")])
p.label(0.5, 1.2, "Yamuk alanı = 3", 0, 4, THEORY, 13, "middle", True)
p.label(0, 2.1, it("f") + "(" + xs("0") + ") = 4", 7, 4, THEORY, 12)
p.label(1, 1.0, it("f") + "(" + xs("1") + ") = 2", 8, 4, THEORY, 12)
p.label(0.72, f(0.72), it("y") + " = 4/(1 + " + it("x") + sup("2") + ")", 10, -14, THEORY, 12.5, "start", True)
# error label in the free upper right corner, with a pointer into the sliver
leader(p, (0.42, 3.36), (0.6, 3.92), PRACTICE)
p.label(0.6, 3.92, "hata " + APPROX + " 0,141592654", 4, -2, PRACTICE, 12.5, "start", True)
save("yamuk", figure(
    PW + 140, PH + 80, [p],
    "<em>f</em>(<em>x</em>) = 4/(1 + <em>x</em>²) eğrisi ve Yamuk Kuralının kullandığı yamuk. Yamuğun alanı "
    "3'tür. Eğri (0, 4) ile (1, 2) noktalarını birleştiren kirişin üstünde kaldığından yamuk integrali eksik "
    "ölçer; turuncu ince bölgenin alanı gerçek hata olan &#960; &#8722; 3 &#8776; 0,141592654'tür.",
    aria="Graph of 4/(1 + x^2) on 0 to 1 with the trapezoid of area 3 under the chord from (0, 4) to (1, 2) "
         "and the thin region between the curve and the chord, the error 0.141592654, shaded"))

# ============================================================
# simpson: Simpson's rule for 4/(1 + x^2) on [0, 1]
# ============================================================
p = frame()
curve = samples(f, 0, 1)
para = samples(p2, 0, 1)
# area under the parabola
p.polygon([(0, 0)] + para + [(1, 0)], PRACTICE, 0.12)
p.line([(1, 0), (1, 2)], PRACTICE, 1.0, "4 3", 0.7)
# the two regions between f and P2: f above on (0, 0.5), below on (0.5, 1)
left_f, left_p = samples(f, 0, 0.5, 100), samples(p2, 0, 0.5, 100)
right_f, right_p = samples(f, 0.5, 1, 100), samples(p2, 0.5, 1, 100)
p.polygon(left_f + left_p[::-1], THEORY, 0.6)
p.polygon(right_f + right_p[::-1], REMARK, 0.6)
p.line(curve, THEORY, 2.2)
p.line(samples(f, -0.1, 0, 10), THEORY, 2.2, None, 0.4)
p.line(samples(f, 1, 1.15, 20), THEORY, 2.2, None, 0.4)
p.line(para, PRACTICE, 2.2, "6 4")
p.points([(0, 4), (0.5, 3.2), (1, 2)], TEXT, 4.0)
xaxis_marks(p, [(0, xs("0") + " = 0"), (0.5, xs("1") + " = 0,5"), (1, xs("2") + " = 1")])
p.label(0.5, 1.2, "Simpson yaklaşımı " + APPROX + " 3,133333333", 0, 4, PRACTICE, 12.5, "middle", True)
# legend in the free upper right corner
LX, LY = 0.6, 4.3
p.line([(LX, LY), (LX + 0.09, LY)], THEORY, 2.2)
p.label(LX + 0.09, LY, it("y") + " = 4/(1 + " + it("x") + sup("2") + ")", 7, 4, THEORY, 12)
p.line([(LX, LY - 0.3), (LX + 0.09, LY - 0.3)], PRACTICE, 2.2, "6 4")
p.label(LX + 0.09, LY - 0.3, it("y") + " = " + it("P") + sub("2") + "(" + it("x") + ")", 7, 4, PRACTICE, 12)
# region labels with pointers
leader(p, (0.26, 3.72), (0.5, 3.62), THEORY)
p.label(0.5, 3.62, it("f") + " &gt; " + it("P") + sub("2"), 4, 4, THEORY, 12, "start", True)
leader(p, (0.76, 2.62), (0.9, 3.0), REMARK)
p.label(0.9, 3.0, it("f") + " &lt; " + it("P") + sub("2"), 4, 0, REMARK, 12, "start", True)
p.text_px(p.X(0.5), p.Y(0) + 42,
          "iki bölgenin işaretli toplamı = &#960; " + MINUS + " 3,133333333 " + APPROX + " 0,008259",
          TEXT, 12, "middle")
save("simpson", figure(
    PW + 140, PH + 100, [p],
    "<em>f</em>(<em>x</em>) = 4/(1 + <em>x</em>²) eğrisi ve (0, 4), (0,5; 3,2), (1, 2) düğümlerinden geçen "
    "<em>P</em><sub>2</sub>(<em>x</em>) = 4 &#8722; 1,2<em>x</em> &#8722; 0,8<em>x</em>² parabolü (kesikli). "
    "Parabolün altındaki alan Simpson yaklaşımıdır. (0; 0,5) aralığında <em>f</em> parabolün üstünde, "
    "(0,5; 1) aralığında altındadır; iki ince bölgenin işaretli toplamı gerçek hata olan "
    "&#960; &#8722; 3,133333333 &#8776; 0,008259'dur.",
    aria="Graph of 4/(1 + x^2) on 0 to 1 with the dashed parabola P2 through (0, 4), (0.5, 3.2), (1, 2), the "
         "area under the parabola, the Simpson approximation 3.133333333, shaded, and the two thin regions "
         "between the curves, f above P2 on the left half and below on the right half"))

# ============================================================
# dugumler: node layout of the closed (n = 3) and open (n = 2) formulas
# ============================================================
W, H = 520, 250
XA, XB = 70, 450


def pixel_plot(W, H):
    """A panel whose data coordinates are the SVG pixels themselves (y grows downward)."""
    return Plot(0, 0, W, H, (0, W), (H, 0))


def brace_up(p, x1, x2, y, depth=7, color=TEXT, width=1.1, opacity=0.75):
    """Curly brace over the span x1..x2 at height y (pixels), tip pointing up."""
    r = min(6.0, (x2 - x1) / 4)
    xm, h = (x1 + x2) / 2, depth / 2
    d = (f"M{x1:.1f},{y:.1f} Q{x1:.1f},{y - h:.1f} {x1 + r:.1f},{y - h:.1f} "
         f"L{xm - r:.1f},{y - h:.1f} Q{xm:.1f},{y - h:.1f} {xm:.1f},{y - depth:.1f} "
         f"Q{xm:.1f},{y - h:.1f} {xm + r:.1f},{y - h:.1f} "
         f"L{x2 - r:.1f},{y - h:.1f} Q{x2:.1f},{y - h:.1f} {x2:.1f},{y:.1f}")
    p.add(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}" opacity="{opacity}"/>')


def row(p, y, title, nodes, used, color):
    """One [a, b] segment at pixel height y; nodes = list of labels, equally spaced."""
    p.text_px((XA + XB) / 2, y - 42, title, TEXT, 13, "middle", True)
    p.add(f'<line x1="{XA}" y1="{y}" x2="{XB}" y2="{y}" stroke="{TEXT}" stroke-width="1.6" opacity="0.7"/>')
    m = len(nodes) - 1
    xs_ = [XA + (XB - XA) * k / m for k in range(m + 1)]
    for x1, x2 in zip(xs_, xs_[1:]):
        brace_up(p, x1 + 6, x2 - 6, y - 8)
        p.text_px((x1 + x2) / 2, y - 19, it("h"), TEXT, 12.5, "middle")
    for x, s, u in zip(xs_, nodes, used):
        if u:
            p.add(f'<circle cx="{x:.1f}" cy="{y}" r="5.2" fill="{color}"/>')
            p.text_px(x, y + 21, s, color, 12.5, "middle")
        else:
            p.add(f'<circle cx="{x:.1f}" cy="{y}" r="5.2" fill="{BG}" stroke="{TEXT}" '
                  f'stroke-width="1.6" stroke-opacity="0.55"/>')
            p.text_px(x, y + 21, s, TEXT, 12.5, "middle")
            p.text_px(x, y + 37, "kullanılmaz", TEXT, 11, "middle", False, True)


p = pixel_plot(W, H)
A_, B_ = it("a"), it("b")
row(p, 75, "Kapalı, " + it("n") + " = 3: " + it("h") + " = (" + B_ + " " + MINUS + " " + A_ + ")/3",
    [A_ + " = " + xs("0"), xs("1"), xs("2"), xs("3") + " = " + B_], [True] * 4, THEORY)
row(p, 190, "Açık, " + it("n") + " = 2: " + it("h") + " = (" + B_ + " " + MINUS + " " + A_ + ")/4",
    [A_ + " = " + xs(MINUS + "1"), xs("0"), xs("1"), xs("2"), xs("3") + " = " + B_],
    [False, True, True, True, False], PRACTICE)
save("dugumler", figure(
    W, H, [p],
    "Kapalı formülde (<em>n</em> = 3) [<em>a</em>, <em>b</em>] üç eşit parçaya bölünür ve uç noktalar dahil "
    "dört nokta düğümdür. Açık formülde (<em>n</em> = 2) aralık dört eşit parçaya bölünür; uç noktalar "
    "<em>x</em><sub>&#8722;1</sub> = <em>a</em> ve <em>x</em><sub>3</sub> = <em>b</em> kullanılmaz, düğümler "
    "yalnız üç iç noktadır.",
    aria="Two segments from a to b: the closed formula with n = 3 uses the four equally spaced points a = x0, "
         "x1, x2, x3 = b; the open formula with n = 2 splits the interval into four parts and uses only the "
         "interior points x0, x1, x2, leaving the end points unused"))
