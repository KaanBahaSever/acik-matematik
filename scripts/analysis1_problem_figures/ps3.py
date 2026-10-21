# -*- coding: utf-8 -*-
"""
Figures of the chapter "Reel Sayılar, Mutlak Değer ve Supremum Üzerine Problemler"
(dersler/analiz-1/problemler-reel-sayilar.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box and never directly under a heading.
The figures are NOT produced at build time. Run

    python scripts/analysis1_problem_figures/ps3.py
    python scripts/center_figures.py "analysis1-ps3-*.md"
    python scripts/check_figure_labels.py "scripts/_figures/analysis1-ps3-*.md"

and paste the markup of scripts/_figures/analysis1-ps3-<name>.md into the .qmd.
The captions are Turkish on purpose; the aria labels are plain ASCII.

Conventions: a point that belongs to a set is filled, one that does not is
hollow; solution sets are drawn as thick bars on the x axis.
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, hollow, fmt, TEXT, THEORY, PRACTICE, BASE, REMARK  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "analysis1-ps3-"

MINUS, INF, LEQ, GEQ = "&#8722;", "&#8734;", "&#8804;", "&#8805;"


def save(name, svg):
    (OUT_DIR / f"{PREFIX}{name}.md").write_text(svg, encoding="utf-8", newline="\n")
    print(f"{PREFIX}{name}.md")


def it(s):
    """Italic math letter inside an SVG <text>."""
    return f'<tspan font-style="italic">{s}</tspan>'


def sups(s, size=9):
    """Superscript inside an SVG <text>."""
    return f'<tspan font-size="{size}" dy="-5">{s}</tspan><tspan dy="5">&#8203;</tspan>'


def num(v):
    """Tick label with a decimal comma and a true minus sign."""
    s = fmt(v).replace(".", ",")
    return s.replace("-", MINUS)


def curve(p, f, x0, x1, color=THEORY, width=1.9, samples=240, dash=None, opacity=1.0):
    """Polyline of y = f(x) on [x0, x1]."""
    pts = [(x0 + (x1 - x0) * k / samples, f(x0 + (x1 - x0) * k / samples)) for k in range(samples + 1)]
    p.line(pts, color, width, dash, opacity)


def axis_bar(p, a, b, color=PRACTICE, left=True, right=True, y=0.0, width=5.0, opacity=0.55, r=4.0):
    """A solution interval drawn on the x axis; None as an end means the bar runs off the panel."""
    xa = p.xmin if a is None else a
    xb = p.xmax if b is None else b
    p.line([(xa, y), (xb, y)], color, width, opacity=opacity)
    for x, closed, real in ((a, left, a is not None), (b, right, b is not None)):
        if not real:
            continue
        if closed:
            p.points([(x, y)], color, r)
        else:
            hollow(p, (x, y), color, r, 1.6)


# ============================================================
# dort-mutlak: f(x) = |x| - |x-1| + 3|x-2| - 2|x-3| against y = x + 1
# ============================================================
def f_dort(x):
    return abs(x) - abs(x - 1) + 3 * abs(x - 2) - 2 * abs(x - 3)


p = Plot(40, 24, 400, 270, (-3.5, 5.6), (-3.0, 7.0))
p.origin_axes("x", "y", xticks=(-3, -2, -1, 1, 2, 3, 4, 5), yticks=(-2, 2, 4, 6), xfmt=num, yfmt=num)
p.line([(3, 4), (5.6, 6.6)], PRACTICE, 7, opacity=0.35)
curve(p, lambda x: x + 1, -3.5, 5.6, BASE, 1.5, samples=2, dash="6 4")
p.line([(-3.5, f_dort(-3.5)), (0, -1), (1, 0), (2, -1), (3, 4), (5.6, f_dort(5.6))], THEORY, 2.0)
p.points([(-1, 0)], PRACTICE, 4.6)
axis_bar(p, 3, None, PRACTICE, left=True, y=0.0, width=4.0, opacity=0.6)
p.label(-3.3, 2.3, "y = f(x)", 0, -10, THEORY, 12, "start", italic=True)
p.label(-3.4, -2.8, "y = x + 1", 0, 0, BASE, 12, "start", italic=True)
p.label(-0.25, -1.45, "x = " + MINUS + "1", 0, 0, PRACTICE, 11.5, "end", bold=True)
p.label(4.3, 5.3, "f(x) = x + 1", -8, -12, PRACTICE, 11.5, "end", bold=True)
save("dort-mutlak", figure(
    480, 330, [p],
    "Sol yan <em>f</em>(<em>x</em>) = |<em>x</em>| &#8722; |<em>x</em> &#8722; 1| + 3|<em>x</em> &#8722; 2| "
    "&#8722; 2|<em>x</em> &#8722; 3| her parçada doğrusaldır. Grafiği <em>y</em> = <em>x</em> + 1 doğrusunu "
    "<em>x</em> = &#8722;1'de keser, <em>x</em> &#8805; 3 için ise onunla çakışır (kalın şerit); "
    "çözüm kümesi {&#8722;1} &#8746; [3, &#8734;).",
    aria="Piecewise linear graph of the left side and the line y = x + 1: they meet at x = -1 "
         "and coincide for every x at least 3"))

# ============================================================
# ikinci-derece: |x^2 - 4x - 1| >= 4
# ============================================================
p = Plot(40, 24, 400, 260, (-2.3, 6.3), (0.0, 14.0))
p.origin_axes("x", "y", xticks=(-2, -1, 1, 2, 3, 4, 5, 6), yticks=(8, 12), xfmt=num, yfmt=num)
p.line([(-2.3, 4), (6.3, 4)], REMARK, 1.3, dash="6 4")
curve(p, lambda x: abs(x * x - 4 * x - 1), -2.3, 6.3, THEORY, 2.0, samples=400)
for x in (-1, 1, 3, 5):
    p.vline(x, 0, 4, TEXT, "3 3", 0.45)
p.points([(-1, 4), (1, 4), (3, 4), (5, 4)], THEORY, 3.4)
axis_bar(p, None, -1, PRACTICE, right=True)
axis_bar(p, 1, 3, PRACTICE)
axis_bar(p, 5, None, PRACTICE, left=True)
p.label(6.3, 4, "y = 4", -2, -7, REMARK, 11.5, "end", italic=True)
p.label(5.55, 10.0, "y = |x" + sups("2") + " " + MINUS + " 4x " + MINUS + " 1|", -8, 0, THEORY, 12, "end", italic=True)
save("ikinci-derece", figure(
    480, 320, [p],
    "<em>y</em> = |<em>x</em><sup>2</sup> &#8722; 4<em>x</em> &#8722; 1| grafiği <em>y</em> = 4 doğrusunun "
    "üstünde ya da üzerinde olduğu yerlerde eşitsizlik sağlanır. Bu <em>x</em>'ler eksende kalın çizilmiştir: "
    "(&#8722;&#8734;, &#8722;1] &#8746; [1, 3] &#8746; [5, &#8734;). Ortadaki tepe, ifadenin negatif olduğu "
    "bölgede mutlak değerin grafiği yukarı katlamasından doğar.",
    aria="Graph of the absolute value of x squared minus 4x minus 1 with the line y = 4; the solution set "
         "is x at most -1, x between 1 and 3, and x at least 5"))

# ============================================================
# iki-uzaklik: |x - 1| + |x - 2| > 1
# ============================================================
p = Plot(40, 24, 400, 240, (-1.2, 4.2), (0.0, 5.6))
p.origin_axes("x", "y", xticks=(-1, 1, 2, 3, 4), yticks=(2, 3, 4, 5), xfmt=num, yfmt=num)
p.line([(-1.2, 1), (4.2, 1)], REMARK, 1.3, dash="6 4")
p.line([(-1.2, 5.4), (1, 1), (2, 1), (4.2, 5.4)], THEORY, 2.0)
p.points([(1, 1), (2, 1)], THEORY, 3.4)
axis_bar(p, None, 1, PRACTICE, right=False)
axis_bar(p, 2, None, PRACTICE, left=False)
p.label(4.2, 1, "y = 1", -2, -7, REMARK, 11.5, "end", italic=True)
p.label(3.15, 3.3, "y = |x " + MINUS + " 1| + |x " + MINUS + " 2|", -10, 0, THEORY, 12, "end", italic=True)
save("iki-uzaklik", figure(
    480, 300, [p],
    "<em>y</em> = |<em>x</em> &#8722; 1| + |<em>x</em> &#8722; 2| grafiği [1, 2] üzerinde tam 1 yüksekliğinde "
    "düzdür; [1, 2]'nin dışında bu aralıktan uzaklaştıkça doğrusal olarak artar (eğim solda &#8722;2, sağda 2). "
    "Eşitsizliğin çözümleri eksende kalın çizilen "
    "(&#8722;&#8734;, 1) &#8746; (2, &#8734;) kümesidir; 1 ve 2 çözüm değildir.",
    aria="Graph of |x-1| + |x-2| with a flat bottom of height 1 on [1, 2] and the line y = 1; "
         "the solution set is x below 1 or above 2"))

# ============================================================
# sinus: s_n = sin(n pi / 2) - 1/n for n = 1..24
# ============================================================
N = 24
vals = [[0, 1, 0, -1][k % 4] - 1 / k for k in range(1, N + 1)]
p = Plot(48, 24, 400, 270, (0, N + 1), (-1.75, 1.3))
p.axes(xticks=(1, 4, 8, 12, 16, 20, 24), yticks=(-1, 0, 1), xlabel="n", xfmt=num, yfmt=num)
p.line([(0, 0), (N + 1, 0)], TEXT, 0.9, opacity=0.35)
p.line([(0, 1), (N + 1, 1)], THEORY, 1.3, dash="6 4")
p.line([(0, -4 / 3), (N + 1, -4 / 3)], BASE, 1.1, dash="3 3", opacity=0.8)
p.points([(k, v) for k, v in zip(range(1, N + 1), vals)], PRACTICE, 3.4)
p.points([(3, -4 / 3)], BASE, 5.0)
p.label(N + 1, 1, "sup S = 1", -2, -7, THEORY, 11.5, "end", bold=True)
p.label(3, -4 / 3, "min S = " + MINUS + "4/3", 10, 19, BASE, 11.5, "start", bold=True)
save("sinus", figure(
    500, 320, [p],
    "<em>s<sub>n</sub></em> = sin(<em>n</em>&#960;/2) &#8722; 1/<em>n</em> terimleri (<em>n</em> = 1, &#8230;, 24). "
    "Üç kol vardır: 4<em>k</em> + 1 sıralı terimler 1'e alttan yaklaşır, çift sıralı terimler 0'a alttan, "
    "4<em>k</em> + 3 sıralı terimler &#8722;1'e alttan. Supremum 1 hiçbir terimde alınmaz; en küçük terim "
    "<em>s</em><sub>3</sub> = &#8722;4/3'tür.",
    aria="Dot plot of sin(n pi/2) - 1/n for n = 1 to 24 with three branches approaching 1, 0 and -1; "
         "the dashed line y = 1 is the supremum and the point n = 3 at -4/3 is the minimum"))

# ============================================================
# ustel: e^{-x^2}, values (0, 1]
# ============================================================
p = Plot(40, 24, 400, 220, (-3.0, 3.0), (0.0, 1.18))
p.origin_axes("x", "y", xticks=(-2, -1, 1, 2), yticks=(0.5,), xfmt=num, yfmt=num)
p.line([(0, 0), (0, 1)], PRACTICE, 6, opacity=0.4)
hollow(p, (0, 0), PRACTICE, 4.2, 1.8)
curve(p, lambda x: math.exp(-x * x), -3.0, 3.0, THEORY, 2.0, samples=300)
p.points([(0, 1)], PRACTICE, 4.6)
p.label(0, 1, "maks C = 1", 10, -4, PRACTICE, 11.5, "start", bold=True)
p.label(1.55, math.exp(-1.55 ** 2), "y = e" + sups("&#8722;x&#178;", 10), 8, -10, THEORY, 12, "start", italic=True)
save("ustel", figure(
    480, 290, [p],
    "<em>y</em> = <em>e</em><sup>&#8722;<em>x</em><sup>2</sup></sup> grafiği. En büyük değer 1, "
    "<em>x</em> = 0'da alınır. Değerler <em>x</em> büyüdükçe 0'a istenildiği kadar yaklaşır ama 0'a hiç "
    "ulaşmaz; değerler düşey eksende kalın çizilen (0, 1] aralığında kalır.",
    aria="Bell shaped graph of e to the minus x squared with maximum 1 at x = 0 and values "
         "approaching 0; the set of values (0, 1] is marked on the y axis"))

# ============================================================
# aralik-birlesimi: D = [2,3] u [4,5] u [6,7] u [8,9] u {10}
# ============================================================
p = Plot(30, 30, 440, 80, (-0.6, 11.9), (-1.0, 1.0))
p.arrow((-0.6, 0), (11.9, 0), TEXT, 1.1, head=7.0, opacity=0.55)
for t in range(0, 12):
    X, Y = p.X(t), p.Y(0)
    p.add(f'<line x1="{X:.1f}" y1="{Y-4:.1f}" x2="{X:.1f}" y2="{Y+4:.1f}" stroke="{TEXT}" stroke-width="1" opacity="0.55"/>')
    p.text_px(X, Y + 18, num(t), TEXT, 11, "middle")
p.polygon([(0, -0.28), (10, -0.28), (10, 0.28), (0, 0.28)], BASE, 0.10, stroke=BASE, width=1.0, dash="4 3")
for a in (2, 4, 6, 8):
    axis_bar(p, a, a + 1, THEORY, width=5.0, opacity=0.6)
p.line([(10, 0), (11, 0)], REMARK, 4.0, dash="4 3", opacity=0.6)
hollow(p, (11, 0), REMARK, 4.0, 1.6)
p.points([(10, 0)], PRACTICE, 4.8)
p.points([(2, 0)], PRACTICE, 4.8)
p.label(2, 0, "min D = 2", 0, -26, PRACTICE, 11.5, "middle", bold=True)
p.label(10, 0, "maks D = 10", 0, -26, PRACTICE, 11.5, "middle", bold=True)
p.label(5, 0.28, "[0, 10]", 0, -8, BASE, 11, "middle", italic=True)
save("aralik-birlesimi", figure(
    500, 150, [p],
    "<em>D</em> = [2, 3] &#8746; [4, 5] &#8746; [6, 7] &#8746; [8, 9] &#8746; {10}. Kesikli çerçeve [0, 10] "
    "penceresidir; [10, 11] aralığından pencerede yalnızca 10 noktası kalır. En küçük eleman 2, en büyük "
    "eleman 10'dur.",
    aria="Number line with the closed intervals 2 to 3, 4 to 5, 6 to 7, 8 to 9 and the single point 10 "
         "inside the window from 0 to 10"))

# ============================================================
# fonksiyon-toplam: f(x) = x, g(x) = 1 - x, f + g = 1 on [0, 1]
# ============================================================
p = Plot(48, 30, 360, 230, (0.0, 1.0), (0.0, 1.25))
p.axes(xticks=(0, 0.5, 1), yticks=(0, 0.5, 1), xlabel="x", xfmt=num, yfmt=num)
p.line([(0, 1), (1, 1)], PRACTICE, 4.0, opacity=0.75)
p.line([(0, 0), (1, 1)], THEORY, 2.0)
p.line([(0, 1), (1, 0)], BASE, 2.0, dash="7 4")
p.points([(1, 1)], THEORY, 4.6)
p.points([(0, 1)], BASE, 4.6)
p.label(0.5, 1, "f(x) + g(x) = 1", 0, -10, PRACTICE, 12, "middle", italic=True)
p.label(0.78, 0.78, "f(x) = x", 10, 12, THEORY, 12, "start", italic=True)
p.label(0.22, 0.78, "g(x) = 1 " + MINUS + " x", -10, 12, BASE, 12, "end", italic=True)
save("fonksiyon-toplam", figure(
    460, 310, [p],
    "<em>f</em>(<em>x</em>) = <em>x</em> en büyük değeri 1'i <em>x</em> = 1'de, <em>g</em>(<em>x</em>) = 1 &#8722; "
    "<em>x</em> ise <em>x</em> = 0'da alır. Aynı noktadaki değerler toplanınca her yerde 1 elde edilir; "
    "bu yüzden sup <em>C</em> = 1 iken sup <em>A</em> + sup <em>B</em> = 2'dir.",
    aria="Graphs of f(x) = x and g(x) = 1 - x on [0, 1] together with their sum, the constant 1; "
         "f peaks at x = 1 and g peaks at x = 0"))
