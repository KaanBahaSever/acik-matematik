# -*- coding: utf-8 -*-
"""
Figures of the chapter "Aksiyomlar, Eşitsizlikler ve Tamlık Üzerine Problemler"
(dersler/analiz-1/problemler-aksiyomlar-ve-tamlik.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box and never directly under a heading.
The figures are NOT produced at build time. Run

    python scripts/analysis1_problem_figures/ps5a.py
    python scripts/center_figures.py "analysis1-ps5a-*.md"
    python scripts/check_figure_labels.py "scripts/_figures/analysis1-ps5a-*.md"

and paste the markup of scripts/_figures/analysis1-ps5a-<name>.md into the .qmd.
The captions are Turkish on purpose; the aria labels are plain ASCII.

Conventions: a point of the solution set is filled, a point outside it is
hollow; the solution set itself is a thick band on the x axis.
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, hollow, TEXT, THEORY, PRACTICE, BASE, REMARK  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "analysis1-ps5a-"

MINUS, INFTY, SQRT = "&#8722;", "&#8734;", "&#8730;"


def save(name, svg):
    (OUT_DIR / f"{PREFIX}{name}.md").write_text(svg, encoding="utf-8", newline="\n")
    print(f"{PREFIX}{name}.md")


def it(s):
    """Italic math letter inside an SVG <text>."""
    return f'<tspan font-style="italic">{s}</tspan>'


def num(v):
    """Tick label with a Turkish decimal comma and a true minus sign."""
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    s = s.replace(".", ",")
    return s.replace("-", MINUS) if s not in ("-0", "") else "0"


def curve(p, f, a, b, ymin, ymax, color, width=2.0, samples=400, dash=None, opacity=1.0):
    """Graph of f on [a, b], cut into pieces where it leaves [ymin, ymax]."""
    seg = []
    for k in range(samples + 1):
        t = a + (b - a) * k / samples
        y = f(t)
        if ymin <= y <= ymax:
            seg.append((t, y))
        else:
            if len(seg) > 1:
                p.line(seg, color, width, dash, opacity)
            seg = []
    if len(seg) > 1:
        p.line(seg, color, width, dash, opacity)


def band(p, x0, x1, color=BASE, width=5, opacity=0.6):
    """Thick band on the x axis marking a piece of the solution set."""
    p.line([(x0, 0), (x1, 0)], color, width, None, opacity)


def hline(p, y, x0, x1, color=REMARK, dash="5 4", width=1.2, opacity=0.85):
    p.line([(x0, y), (x1, y)], color, width, dash, opacity)


# ============================================================
# mutlak-b: |3x + 2| > 4|x - 1| holds exactly on (2/7, 6)
# ============================================================
p = Plot(40, 24, 380, 230, (-1.2, 7.6), (-2.0, 26.0))
p.origin_axes("x", "y", xticks=[1, 2, 3, 4, 5, 6, 7], yticks=[5, 10, 15, 20], xfmt=num, yfmt=num)
curve(p, lambda t: abs(3 * t + 2), -1.2, 7.3, -2, 26, THEORY, 2.1)
curve(p, lambda t: 4 * abs(t - 1), -1.2, 7.3, -2, 26, PRACTICE, 2.1)
band(p, 2 / 7, 6)
hollow(p, (2 / 7, 0), BASE, 4.0, 1.6)
hollow(p, (6, 0), BASE, 4.0, 1.6)
p.vline(2 / 7, 0, 20 / 7, TEXT, "3 3", 0.55)
p.vline(6, 0, 20, TEXT, "3 3", 0.55)
p.points([(2 / 7, 20 / 7), (6, 20)], TEXT, 3.4)
p.label(2 / 7, 0, "2/7", 3, 17, BASE, 11, "start", bold=True)
p.label(0.6, 12.0, it("y") + " = |3" + it("x") + " + 2|", 0, 0, THEORY, 12, "start")
p.label(7.3, 4 * abs(7.3 - 1), it("y") + " = 4|" + it("x") + " " + MINUS + " 1|", -10, -2, PRACTICE, 12, "end")
p.label(3.1, 0, "çözüm: (2/7, 6)", 0, -10, BASE, 11.5, "middle", bold=True)
save("mutlak-b", figure(
    470, 300, [p],
    "<em>y</em> = |3<em>x</em> + 2| (mavi) ile <em>y</em> = 4|<em>x</em> &#8722; 1| (turuncu) grafikleri "
    "<em>x</em> = 2/7 ve <em>x</em> = 6 noktalarında kesişir. Mavi grafik yalnızca bu iki nokta arasında "
    "üstte kalır; çözüm kümesi (2/7, 6) açık aralığıdır.",
    aria="Graphs of y = |3x + 2| and y = 4|x - 1| crossing at x = 2/7 and x = 6; the first lies above "
         "the second exactly between the crossings"))

# ============================================================
# mutlak-d: |x| - |x-1| + 3|x-2| - 2|x-3| = x + 1 on {-1} and [3, oo)
# ============================================================


def f_d(t):
    return abs(t) - abs(t - 1) + 3 * abs(t - 2) - 2 * abs(t - 3)


p = Plot(40, 24, 380, 260, (-3.4, 6.4), (-3.2, 8.0))
p.origin_axes("x", "y", xticks=[-3, -2, -1, 1, 2, 3, 4, 5, 6], yticks=[-2, 2, 4, 6], xfmt=num, yfmt=num)
curve(p, lambda t: t + 1, -3.4, 6.3, -3.2, 8, PRACTICE, 1.6, dash="6 4")
curve(p, f_d, -3.4, 6.3, -3.2, 8, THEORY, 2.1, samples=980)
band(p, 3, 6.15)
p.arrow((6.0, 0), (6.4, 0), BASE, 4, head=9, opacity=0.6)
p.points([(-1, 0), (3, 0)], BASE, 4.0)
p.points([(-1, 0)], TEXT, 3.2)
p.vline(3, 0, 4, TEXT, "3 3", 0.55)
p.points([(3, 4)], TEXT, 3.4)
p.label(-1, 0, MINUS + "1", -4, -10, BASE, 11.5, "end", bold=True)
p.label(-3.0, f_d(-3.0), it("y") + " = " + it("f") + "(" + it("x") + ")", 8, -6, THEORY, 12, "start")
p.label(1.5, 3.1, it("y") + " = " + it("x") + " + 1", 0, 0, PRACTICE, 12, "end")
p.label(4.6, 5.6, "çakışırlar", -10, 0, BASE, 11.5, "end", bold=True)
p.label(4.7, 0, "[3, " + INFTY + ")", 0, -10, BASE, 11.5, "middle", bold=True)
save("mutlak-d", figure(
    470, 320, [p],
    "<em>f</em>(<em>x</em>) = |<em>x</em>| &#8722; |<em>x</em> &#8722; 1| + 3|<em>x</em> &#8722; 2| &#8722; "
    "2|<em>x</em> &#8722; 3| fonksiyonunun grafiği (mavi) ve <em>y</em> = <em>x</em> + 1 doğrusu (kesikli). "
    "İki grafik <em>x</em> = &#8722;1'de kesişir ve <em>x</em> &#8805; 3 için üst üste biner; "
    "çözüm kümesi {&#8722;1} &#8746; [3, &#8734;)'dur.",
    aria="Graph of the piecewise linear function |x| - |x-1| + 3|x-2| - 2|x-3| and the line y = x + 1; "
         "they meet at x = -1 and coincide for x at least 3"))

# ============================================================
# mutlak-f: |1 - |x - 1|| < 1 on (-1, 1) and (1, 3)
# ============================================================
p = Plot(40, 24, 380, 170, (-2.3, 4.3), (-0.4, 2.3))
p.origin_axes("x", "y", xticks=[-2, -1, 1, 2, 3, 4], yticks=[1, 2], xfmt=num, yfmt=num)
hline(p, 1, -2.3, 4.2)
curve(p, lambda t: abs(1 - abs(t - 1)), -2.2, 4.2, -1, 3, THEORY, 2.1, samples=1320)
band(p, -1, 1)
band(p, 1, 3)
for xx in (-1, 1, 3):
    hollow(p, (xx, 0), BASE, 4.0, 1.6)
hollow(p, (1, 1), THEORY, 4.0, 1.6)
p.points([(-1, 1), (3, 1)], TEXT, 3.2)
p.label(4.2, 1, it("y") + " = 1", 0, -7, REMARK, 11.5, "end")
p.label(1.15, 1.55, it("y") + " = |1 " + MINUS + " |" + it("x") + " " + MINUS + " 1||", 0, 0, THEORY, 12, "middle")
save("mutlak-f", figure(
    470, 240, [p],
    "<em>y</em> = |1 &#8722; |<em>x</em> &#8722; 1|| grafiği <em>y</em> = 1 doğrusunun altında yalnızca "
    "(&#8722;1, 1) ve (1, 3) aralıklarında kalır. <em>x</em> = 1'de değer tam 1'dir, bu nokta çözüme girmez.",
    aria="W shaped graph of y = |1 - |x - 1|| below the line y = 1 on (-1, 1) and (1, 3); at x = 1 "
         "the graph touches the line"))

# ============================================================
# mutlak-g: ||x + 1| - |x - 1|| < 1 on (-1/2, 1/2)
# ============================================================
p = Plot(40, 24, 380, 170, (-3.2, 3.2), (-0.4, 2.6))
p.origin_axes("x", "y", xticks=[-3, -2, -1, 1, 2, 3], yticks=[1, 2], xfmt=num, yfmt=num)
hline(p, 1, -3.2, 3.1)
curve(p, lambda t: abs(abs(t + 1) - abs(t - 1)), -3.1, 3.1, -1, 3, THEORY, 2.1, samples=1240)
band(p, -0.5, 0.5)
hollow(p, (-0.5, 0), BASE, 4.0, 1.6)
hollow(p, (0.5, 0), BASE, 4.0, 1.6)
p.vline(-0.5, 0, 1, TEXT, "3 3", 0.55)
p.vline(0.5, 0, 1, TEXT, "3 3", 0.55)
p.points([(-0.5, 1), (0.5, 1)], TEXT, 3.2)
p.label(-0.5, 0, MINUS + "1/2", -5, -8, BASE, 11, "end", bold=True)
p.label(0.5, 0, "1/2", 5, -8, BASE, 11, "start", bold=True)
p.label(3.1, 1, it("y") + " = 1", 0, -7, REMARK, 11.5, "end")
p.label(-3.0, 2, it("y") + " = ||" + it("x") + " + 1| " + MINUS + " |" + it("x") + " " + MINUS + " 1||", 0, -9, THEORY, 12, "start")
save("mutlak-g", figure(
    470, 240, [p],
    "<em>y</em> = ||<em>x</em> + 1| &#8722; |<em>x</em> &#8722; 1|| grafiği: |<em>x</em>| &#8805; 1 iken "
    "sabit 2, &#8722;1 &lt; <em>x</em> &lt; 1 iken 2|<em>x</em>|. Grafik <em>y</em> = 1 doğrusunun altına "
    "yalnızca (&#8722;1/2, 1/2) aralığında iner.",
    aria="Graph of y = ||x + 1| - |x - 1||, equal to 2 outside (-1, 1) and to 2|x| inside; it lies below "
         "y = 1 exactly on (-1/2, 1/2)"))

# ============================================================
# sup-inf-b: the values of sqrt(x + 1)/x for x >= 2 fill (0, sqrt3/2]
# ============================================================
TOP = math.sqrt(3) / 2
p = Plot(56, 24, 360, 200, (0, 15.0), (0, 1.0))
p.origin_axes("x", "y", xticks=[2, 4, 6, 8, 10, 12, 14], yticks=[0.5], xfmt=num, yfmt=num)
hline(p, TOP, 0, 14.6, THEORY, "5 4", 1.1, 0.8)
curve(p, lambda t: math.sqrt(t + 1) / t, 2, 14.6, 0, 1, BASE, 2.1)
p.line([(0, 0), (0, TOP)], PRACTICE, 5, None, 0.45)
p.points([(0, TOP), (2, TOP)], PRACTICE, 4.0)
hollow(p, (0, 0), PRACTICE, 4.0, 1.8)
p.vline(2, 0, TOP, TEXT, "3 3", 0.55)
p.label(14.6, TOP, "sup = max = " + SQRT + "3/2", 0, -8, THEORY, 11.5, "end", bold=True)
p.label(8.5, math.sqrt(9.5) / 8.5, it("y") + " = " + SQRT + "(" + it("x") + " + 1)/" + it("x"), 0, -12, BASE, 12, "start")
p.label(0, 0.33, "değerler", 9, 0, PRACTICE, 11, "start", bold=True)
p.label(14.6, 0, "inf = 0", 0, -9, PRACTICE, 11.5, "end", bold=True)
save("sup-inf-b", figure(
    470, 270, [p],
    "<em>x</em> &#8805; 2 için <em>y</em> = &#8730;(<em>x</em> + 1)/<em>x</em> grafiği. En büyük değer "
    "<em>x</em> = 2'de alınan &#8730;3/2'dir; <em>x</em> büyüdükçe değerler 0'a istenildiği kadar yaklaşır "
    "ama 0 olmaz. Düşey eksendeki kalın parça değerler kümesini gösterir.",
    aria="Decreasing graph of sqrt(x + 1)/x for x at least 2, maximum sqrt(3)/2 at x = 2, values tending "
         "to 0; the value set is marked on the y axis"))

# ============================================================
# sup-inf-f: x^3 - 4x < 0 exactly on (-oo, -2) and (0, 2)
# ============================================================
p = Plot(40, 24, 380, 230, (-3.3, 3.3), (-6.5, 6.5))
p.origin_axes("x", "y", xticks=[-3, -1, 1, 3], yticks=[-4, 4], xfmt=num, yfmt=num)
curve(p, lambda t: t ** 3 - 4 * t, -3.2, 3.2, -6.5, 6.5, THEORY, 2.1)
band(p, -3.0, -2)
p.arrow((-2.9, 0), (-3.35, 0), BASE, 4, head=9, opacity=0.6)
band(p, 0, 2)
for xx in (-2, 0, 2):
    hollow(p, (xx, 0), BASE, 4.0, 1.6)
p.label(1.9, 5.0, it("y") + " = " + it("x") + "&#179; " + MINUS + " 4" + it("x"), 0, 0, THEORY, 12, "end")
p.label(-2, 0, MINUS + "2", 6, 16, TEXT, 11, "start")
p.label(2, 0, "2", 6, 16, TEXT, 11, "start")
p.label(1, 0, "sup = 2", 0, 30, BASE, 11.5, "middle", bold=True)
p.label(-2.85, 0, "alttan sınırsız", 0, -12, BASE, 11.5, "middle", bold=True)
save("sup-inf-f", figure(
    470, 300, [p],
    "<em>y</em> = <em>x</em>&#179; &#8722; 4<em>x</em> = <em>x</em>(<em>x</em> &#8722; 2)(<em>x</em> + 2) "
    "grafiği <em>x</em> eksenini &#8722;2, 0 ve 2'de keser. Grafik eksenin altında, yani ifade negatif, "
    "tam olarak (&#8722;&#8734;, &#8722;2) ve (0, 2) aralıklarında kalır.",
    aria="Cubic y = x^3 - 4x crossing the x axis at -2, 0, 2; negative on (-infinity, -2) and on (0, 2)"))
