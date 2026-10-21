# -*- coding: utf-8 -*-
"""
Figures of the chapter "Reel Sayıların Özellikleri, Mutlak Değer ve Sınırlı Kümeler Üzerine Problemler"
(dersler/analiz-1/problemler-mutlak-deger-ve-sinirli-kumeler.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box and never directly under a heading.
The figures are NOT produced at build time. Run

    python scripts/analysis1_problem_figures/ps4b.py
    python scripts/center_figures.py "analysis1-ps4b-*.md"
    python scripts/check_figure_labels.py "scripts/_figures/analysis1-ps4b-*.md"

and paste the markup of scripts/_figures/analysis1-ps4b-<name>.md into the .qmd.
The captions are Turkish on purpose; the aria labels are plain ASCII.

Conventions: a point or boundary that belongs to the set is filled or solid,
one that does not is hollow or dashed; solution sets of one-variable
inequalities are drawn as thick bars on the x axis; plane sets are shaded.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, hollow, fmt, TEXT, THEORY, PRACTICE, BASE, REMARK  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "analysis1-ps4b-"

MINUS = "&#8722;"


def save(name, svg):
    (OUT_DIR / f"{PREFIX}{name}.md").write_text(svg, encoding="utf-8", newline="\n")
    print(f"{PREFIX}{name}.md")


def num(v):
    """Tick label: simple halves as fractions, otherwise a decimal comma; true minus sign."""
    halves = {0.5: "1/2", 1.5: "3/2", 2.5: "5/2"}
    a = abs(v)
    if a in halves:
        s = halves[a]
        return (MINUS if v < 0 else "") + s
    return fmt(v).replace(".", ",").replace("-", MINUS)


def curve(p, f, x0, x1, color=THEORY, width=1.9, samples=240, dash=None, opacity=1.0):
    """Polyline of y = f(x) on [x0, x1]."""
    pts = [(x0 + (x1 - x0) * k / samples, f(x0 + (x1 - x0) * k / samples)) for k in range(samples + 1)]
    p.line(pts, color, width, dash, opacity)


def axis_bar(p, a, b, color=PRACTICE, left=True, right=True, y=0.0, width=5.0, opacity=0.55, r=4.0):
    """A solution interval on the x axis; None as an end means the bar runs off the panel."""
    xa = p.xmin if a is None else a
    xb = p.xmax if b is None else b
    p.line([(xa, y), (xb, y)], color, width, opacity=opacity)
    for x, closed in ((a, left), (b, right)):
        if x is None:
            continue
        if closed:
            p.points([(x, y)], color, r)
        else:
            hollow(p, (x, y), color, r, 1.6)


def plane(lim=3.6, size=300, ticks=(-3, -2, -1, 1, 2, 3)):
    """A square panel [-lim, lim]^2 with equal scales and axes through the origin."""
    p = Plot(30, 22, size, size, (-lim, lim), (-lim, lim))
    p.origin_axes("x", "y", xticks=ticks, yticks=ticks, xfmt=num, yfmt=num)
    return p


def plane_figure(name, p, caption, aria):
    save(name, figure(360, 350, [p], caption, aria=aria))


# ============================================================
# mutlak-dogru-a: |x - 2| <= x + 1, solutions [1/2, oo)
# ============================================================
p = Plot(40, 24, 400, 270, (-1.6, 5.6), (-0.9, 6.6))
p.origin_axes("x", "y", xticks=(-1, 0.5, 2, 3, 4, 5), yticks=(1.5, 3, 5), xfmt=num, yfmt=num)
p.line([(-1.6, 3.6), (2, 0), (5.6, 3.6)], THEORY, 2.0)
curve(p, lambda x: x + 1, -1.6, 5.6, BASE, 1.6, samples=2, dash="6 4")
p.vline(0.5, 0, 1.5, TEXT, "3 3", 0.5)
p.points([(0.5, 1.5)], PRACTICE, 4.4)
axis_bar(p, 0.5, None, PRACTICE, left=True)
p.label(3.45, 0.62, "y = |x " + MINUS + " 2|", 0, 0, THEORY, 12, "start", italic=True)
p.label(4.4, 5.4, "y = x + 1", -8, -6, BASE, 12, "end", italic=True)
save("mutlak-dogru-a", figure(
    480, 330, [p],
    "<em>y</em> = |<em>x</em> &#8722; 2| (düz çizgi) ve <em>y</em> = <em>x</em> + 1 (kesikli). Doğru, "
    "<em>x</em> = 1/2'de V'yi keser ve bu noktanın sağında hep V'nin üstünde kalır; V'nin sağ kolu doğruya "
    "paraleldir. Çözüm kümesi [1/2, &#8734;) eksende kalın çizilmiştir.",
    aria="Graph of the V shaped y = |x - 2| and the line y = x + 1 meeting at x = 1/2; "
         "the solution set from 1/2 to infinity is marked on the x axis"))

# ============================================================
# mutlak-dogru-b: 3|x| <= 2 - x, solutions [-1, 1/2]
# ============================================================
p = Plot(40, 24, 400, 270, (-2.4, 2.4), (-0.8, 5.6))
p.origin_axes("x", "y", xticks=(-2, -1, 0.5, 1, 2), yticks=(1.5, 3, 4.5), xfmt=num, yfmt=num)
p.line([(-5.6 / 3, 5.6), (0, 0), (5.6 / 3, 5.6)], THEORY, 2.0)
curve(p, lambda x: 2 - x, -2.4, 2.4, BASE, 1.6, samples=2, dash="6 4")
p.vline(-1, 0, 3, TEXT, "3 3", 0.5)
p.vline(0.5, 0, 1.5, TEXT, "3 3", 0.5)
p.points([(-1, 3), (0.5, 1.5)], PRACTICE, 4.4)
axis_bar(p, -1, 0.5, PRACTICE)
p.label(1.55, 4.65, "y = 3|x|", 10, 4, THEORY, 12, "start", italic=True)
p.label(-2.3, 2.5, "y = 2 " + MINUS + " x", 0, 0, BASE, 12, "start", italic=True)
save("mutlak-dogru-b", figure(
    480, 330, [p],
    "<em>y</em> = 3|<em>x</em>| (düz çizgi) ve <em>y</em> = 2 &#8722; <em>x</em> (kesikli). İki grafik "
    "(&#8722;1, 3) ve (1/2, 3/2) noktalarında kesişir; doğru, bu iki nokta arasında V'nin üstündedir. "
    "Çözüm kümesi [&#8722;1, 1/2] eksende kalın çizilmiştir.",
    aria="Graph of y = 3|x| and the line y = 2 - x meeting at (-1, 3) and (1/2, 3/2); "
         "the solution interval from -1 to 1/2 is marked on the x axis"))

# ============================================================
# fark-grafigi: y = |x| - |x - 1|
# ============================================================
p = Plot(40, 24, 400, 220, (-2.6, 3.6), (-1.7, 1.7))
p.origin_axes("x", "y", xticks=(-2, -1, 1, 2, 3), yticks=(), xfmt=num, yfmt=num)
p.line([(-2.6, 1), (3.6, 1)], REMARK, 1.0, dash="4 4", opacity=0.7)
p.line([(-2.6, -1), (3.6, -1)], REMARK, 1.0, dash="4 4", opacity=0.7)
p.line([(-2.6, -1), (0, -1), (1, 1), (3.6, 1)], THEORY, 2.2)
p.points([(0, -1), (1, 1)], PRACTICE, 4.2)
p.label(1.9, 1, "y = |x| " + MINUS + " |x " + MINUS + " 1|", 0, -10, THEORY, 12, "middle", italic=True)
p.label(0, -1, "(0, " + MINUS + "1)", 8, 18, PRACTICE, 11.5, "start")
p.label(1, 1, "(1, 1)", 8, 18, PRACTICE, 11.5, "start")
save("fark-grafigi", figure(
    480, 280, [p],
    "<em>y</em> = |<em>x</em>| &#8722; |<em>x</em> &#8722; 1| grafiği: <em>x</em> &lt; 0 için sabit "
    "&#8722;1, [0, 1] üzerinde eğimi 2 olan <em>y</em> = 2<em>x</em> &#8722; 1 doğru parçası, "
    "<em>x</em> &#8805; 1 için sabit 1. Grafik kesikli çizilen <em>y</em> = &#177;1 doğruları arasında kalır.",
    aria="Graph of y = |x| - |x - 1|: constant -1 for negative x, a segment of slope 2 from (0, -1) "
         "to (1, 1), and constant 1 for x at least 1"))

# ============================================================
# toplam-seridi: 4 < |x + 2| + |x - 1| < 5
# ============================================================
p = Plot(40, 24, 400, 270, (-4.3, 3.3), (0.0, 7.9))
p.origin_axes("x", "y", xticks=(-4, -3, -2, -1, 1, 2, 3), yticks=(1, 2, 6, 7), xfmt=num, yfmt=num)
p.polygon([(-4.3, 4), (3.3, 4), (3.3, 5), (-4.3, 5)], REMARK, 0.13)
p.line([(-4.3, 4), (3.3, 4)], REMARK, 1.2, dash="6 4")
p.line([(-4.3, 5), (3.3, 5)], REMARK, 1.2, dash="6 4")
p.line([(-4.3, 7.6), (-2, 3), (1, 3), (3.3, 7.6)], THEORY, 2.1)
for x in (-3, -2.5, 1.5, 2):
    p.vline(x, 0, 5 if x in (-3, 2) else 4, TEXT, "3 3", 0.45)
axis_bar(p, -3, -2.5, PRACTICE, left=False, right=False)
axis_bar(p, 1.5, 2, PRACTICE, left=False, right=False)
p.label(-1.5, 3, "y = |x + 2| + |x " + MINUS + " 1|", 0, 20, THEORY, 12, "start", italic=True)
p.points([(-2, 3), (1, 3)], THEORY, 3.6)
p.label(-2, 3, "(" + MINUS + "2, 3)", -6, 16, THEORY, 11, "end")
p.label(1, 3, "(1, 3)", 6, 16, THEORY, 11, "start")
p.label(3.3, 5, "y = 5", -2, -7, REMARK, 11.5, "end", italic=True)
p.label(3.3, 4, "y = 4", -2, 15, REMARK, 11.5, "end", italic=True)
save("toplam-seridi", figure(
    480, 330, [p],
    "<em>f</em>(<em>x</em>) = |<em>x</em> + 2| + |<em>x</em> &#8722; 1| grafiği [&#8722;2, 1] üzerinde 3 "
    "yüksekliğinde düzdür, dışında eğimi &#177;2 olan doğrulardır. Grafiğin 4 &lt; <em>y</em> &lt; 5 şeridinde "
    "kaldığı <em>x</em>'ler eksende kalın çizilmiştir: (&#8722;3, &#8722;5/2) &#8746; (3/2, 2).",
    aria="Graph of |x + 2| + |x - 1| with the band between the lines y = 4 and y = 5; "
         "the solution intervals (-3, -5/2) and (3/2, 2) are marked on the x axis"))

# ============================================================
# duzlem-esitlik-a: |x| = |y|
# ============================================================
p = plane()
p.line([(-3.4, -3.4), (3.4, 3.4)], THEORY, 2.1)
p.line([(-3.4, 3.4), (3.4, -3.4)], THEORY, 2.1)
p.label(2.3, 2.3, "y = x", 10, 4, THEORY, 12, "start", italic=True)
p.label(2.3, -2.3, "y = " + MINUS + "x", 10, 4, THEORY, 12, "start", italic=True)
plane_figure(
    "duzlem-esitlik-a", p,
    "|<em>x</em>| = |<em>y</em>| koşulunu sağlayan noktalar, orijinde dik kesişen <em>y</em> = <em>x</em> ve "
    "<em>y</em> = &#8722;<em>x</em> doğrularıdır.",
    "The set |x| = |y|: the two diagonal lines y = x and y = -x through the origin")

# ============================================================
# duzlem-esitlik-b: |x| + |y| = 1
# ============================================================
p = plane(2.0, ticks=(-1, 1))
sq = [(1, 0), (0, 1), (-1, 0), (0, -1)]
p.line(sq + [sq[0]], THEORY, 2.1)
p.points(sq, THEORY, 3.6)
p.label(0.5, 0.5, "x + y = 1", 8, -6, THEORY, 11.5, "start", italic=True)
plane_figure(
    "duzlem-esitlik-b", p,
    "|<em>x</em>| + |<em>y</em>| = 1 koşulunu sağlayan noktalar, köşeleri (&#177;1, 0) ve (0, &#177;1) olan "
    "karenin kenarlarıdır. Birinci bölgedeki kenar <em>x</em> + <em>y</em> = 1 doğrusunun parçasıdır; ötekiler "
    "simetriyle elde edilir.",
    "The set |x| + |y| = 1: the boundary of the square with corners (1, 0), (0, 1), (-1, 0), (0, -1)")

# ============================================================
# duzlem-esitlik-c: |xy| = 2
# ============================================================
L = 4.9
p = plane(L, ticks=(-2, 2))
E = L - 0.5
x0 = 2 / E
branch = [(x0 + (E - x0) * k / 200, 2 / (x0 + (E - x0) * k / 200)) for k in range(201)]
for sx in (1, -1):
    for sy in (1, -1):
        p.line([(sx * x, sy * y) for x, y in branch], THEORY, 2.0)
p.points([(1, 2), (2, 1), (-1, 2), (-2, -1)], PRACTICE, 3.6)
p.label(2.2, 0.91, "y = 2/x", 6, -12, THEORY, 12, "start", italic=True)
p.label(2.2, -0.91, "y = " + MINUS + "2/x", 6, 20, THEORY, 12, "start", italic=True)
plane_figure(
    "duzlem-esitlik-c", p,
    "|<em>xy</em>| = 2 koşulunu sağlayan noktalar dört kollu bir eğridir: birinci ve üçüncü bölgede "
    "<em>y</em> = 2/<em>x</em>, ikinci ve dördüncü bölgede <em>y</em> = &#8722;2/<em>x</em> hiperbolünün kolları. "
    "İşaretli noktalar (1, 2), (2, 1), (&#8722;1, 2) ve (&#8722;2, &#8722;1)'dir.",
    "The set |xy| = 2: the four branches of the hyperbolas y = 2/x and y = -2/x")

# ============================================================
# duzlem-esitlik-d: |x| - |y| = 2
# ============================================================
L = 4.6
p = plane(L, ticks=(-4, -2, 2, 4))
E = L - 0.2
for s in (1, -1):
    p.line([(s * 2, 0), (s * E, E - 2)], THEORY, 2.1)
    p.line([(s * 2, 0), (s * E, -(E - 2))], THEORY, 2.1)
p.points([(2, 0), (-2, 0)], PRACTICE, 4.0)
p.label(3.5, 1.5, "y = x " + MINUS + " 2", -6, -8, THEORY, 11.5, "end", italic=True)
p.label(-3.5, 1.5, "y = " + MINUS + "x " + MINUS + " 2", 6, -8, THEORY, 11.5, "start", italic=True)
plane_figure(
    "duzlem-esitlik-d", p,
    "|<em>x</em>| &#8722; |<em>y</em>| = 2 koşulunu sağlayan noktalar dört ışındır: (2, 0)'dan sağa açılan "
    "<em>y</em> = &#177;(<em>x</em> &#8722; 2) ışınları ve (&#8722;2, 0)'dan sola açılan simetrikleri. "
    "&#8722;2 &lt; <em>x</em> &lt; 2 şeridinde kümenin noktası yoktur.",
    "The set |x| - |y| = 2: two rays starting at (2, 0) opening to the right and their mirror images "
    "starting at (-2, 0)")

# ============================================================
# duzlem-bolge-a: |x| <= |y|
# ============================================================
L = 3.6
p = plane(L)
E = L - 0.1
p.polygon([(0, 0), (E, E), (-E, E)], THEORY, 0.18)
p.polygon([(0, 0), (E, -E), (-E, -E)], THEORY, 0.18)
p.line([(-E, -E), (E, E)], THEORY, 1.9)
p.line([(-E, E), (E, -E)], THEORY, 1.9)
p.points([(1, 2)], PRACTICE, 3.8)
hollow(p, (2, 1), PRACTICE, 3.8, 1.6)
p.label(1, 2, "(1, 2)", -8, 4, PRACTICE, 11, "end")
p.label(2, 1, "(2, 1)", 8, 4, PRACTICE, 11, "start")
plane_figure(
    "duzlem-bolge-a", p,
    "|<em>x</em>| &#8804; |<em>y</em>| bölgesi (taralı): <em>y</em> = &#177;<em>x</em> doğrularının ayırdığı "
    "dört açısal bölgeden <em>y</em> eksenini içeren ikisi, sınır doğrularıyla birlikte. Dolu nokta bölgededir, "
    "içi boş nokta değildir.",
    "The region |x| at most |y|: the upper and lower wedges between the lines y = x and y = -x, "
    "including the lines")

# ============================================================
# duzlem-bolge-b: |x| + |y| <= 1
# ============================================================
p = plane(2.0, ticks=(-1, 1))
sq = [(1, 0), (0, 1), (-1, 0), (0, -1)]
p.polygon(sq, THEORY, 0.22)
p.line(sq + [sq[0]], THEORY, 2.0)
p.points([(0.5, 0.5)], PRACTICE, 3.6)
hollow(p, (1, 1), PRACTICE, 3.6, 1.6)
p.label(1, 1, "(1, 1)", 8, 4, PRACTICE, 11, "start")
p.label(0.5, 0.5, "(1/2, 1/2)", 8, -6, PRACTICE, 11, "start")
plane_figure(
    "duzlem-bolge-b", p,
    "|<em>x</em>| + |<em>y</em>| &#8804; 1 bölgesi: köşeleri (&#177;1, 0) ve (0, &#177;1) olan dolu kare. "
    "Kenarlar bölgeye aittir; (1/2, 1/2) bölgededir, (1, 1) değildir.",
    "The region |x| + |y| at most 1: the filled square with corners (1, 0), (0, 1), (-1, 0), (0, -1)")

# ============================================================
# duzlem-bolge-c: |xy| <= 2
# ============================================================
L = 4.9
p = plane(L, ticks=(-2, 2))
E = L - 0.5
xa = 2 / E
arc = [(xa + (E - xa) * k / 120, 2 / (xa + (E - xa) * k / 120)) for k in range(121)]
for sx in (1, -1):
    for sy in (1, -1):
        pts = [(0, 0), (0, sy * E)] + [(sx * x, sy * y) for x, y in arc] + [(sx * E, 0)]
        p.polygon(pts, THEORY, 0.18)
        p.line([(sx * x, sy * y) for x, y in arc], THEORY, 1.9)
p.points([(1, 1)], PRACTICE, 3.8)
hollow(p, (2, 2), PRACTICE, 3.8, 1.6)
p.label(1, 1, "(1, 1)", 7, 14, PRACTICE, 11, "start")
p.label(2, 2, "(2, 2)", 7, -6, PRACTICE, 11, "start")
plane_figure(
    "duzlem-bolge-c", p,
    "|<em>xy</em>| &#8804; 2 bölgesi (taralı): iki ekseni içeren ve <em>y</em> = &#177;2/<em>x</em> "
    "hiperbollerinin dört koluyla sınırlanan bölge; kollar da bölgeye aittir. Bölge eksenler boyunca "
    "sonsuza uzanır; (1, 1) bölgededir, (2, 2) değildir.",
    "The region |xy| at most 2: the star shaped region containing both axes, bounded by the four "
    "branches of y = 2/x and y = -2/x")

# ============================================================
# duzlem-bolge-d: |x| - |y| >= 2
# ============================================================
L = 4.6
p = plane(L, ticks=(-4, -2, 2, 4))
E = L - 0.15
for s in (1, -1):
    p.polygon([(s * 2, 0), (s * E, E - 2), (s * E, -(E - 2))], THEORY, 0.2)
    p.line([(s * E, E - 2), (s * 2, 0), (s * E, -(E - 2))], THEORY, 2.0)
p.points([(3, 0)], PRACTICE, 3.8)
hollow(p, (3, 2), PRACTICE, 3.8, 1.6)
p.label(3, 0, "(3, 0)", 0, 18, PRACTICE, 11, "middle")
p.label(3, 2, "(3, 2)", -8, -4, PRACTICE, 11, "end")
plane_figure(
    "duzlem-bolge-d", p,
    "|<em>x</em>| &#8722; |<em>y</em>| &#8805; 2 bölgesi (taralı): köşesi (2, 0)'da olan ve sağa açılan "
    "açısal bölge ile köşesi (&#8722;2, 0)'da olan ve sola açılan simetriği; sınır ışınları dahildir. "
    "(3, 0) bölgededir, (3, 2) değildir.",
    "The region |x| - |y| at least 2: a wedge with vertex (2, 0) opening to the right and its mirror "
    "image with vertex (-2, 0)")
