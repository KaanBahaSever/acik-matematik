# -*- coding: utf-8 -*-
"""
Figures of the chapter "Alt Diziler ve Cauchy Dizileri"
(dersler/analiz-4/alt-diziler-ve-cauchy-dizileri.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box: a figure that illustrates a
definition sits directly below that box. The figures are NOT produced at
build time. Run

    python scripts/analysis4_figures/alt.py
    python scripts/center_figures.py "analysis4-alt-*.md"
    python scripts/check_figure_labels.py "scripts/_figures/analysis4-alt-*.md"

and paste the markup of scripts/_figures/analysis4-alt-<name>.md into the
.qmd. Captions are Turkish on purpose (they are shown on the site); aria
labels are plain ASCII.

Conventions: a boundary that belongs to the set is a solid line, one that does
not is dashed; points of the set are filled, excluded points are hollow.
Every drawing that contains a circle uses equal x and y scales.
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, circle_pts, dot, hollow, TEXT, THEORY, PRACTICE  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "analysis4-alt-"

MINUS = "&#8722;"


def it(s):
    """Italic run inside an SVG <text>."""
    return f'<tspan font-style="italic">{s}</tspan>'


def sub(s, size=8.5):
    """Subscript inside an SVG <text>."""
    return f'<tspan font-size="{size}" dy="3.5">{s}</tspan><tspan dy="-3.5">&#8203;</tspan>'


def xk(k, name="x"):
    """The label x_k (or p_k)."""
    return it(name) + sub(str(k))


def x_kj(j):
    """The label x_{k_j}: a subscript with its own subscript."""
    return (it("x") + f'<tspan font-size="8.5" dy="3.5" font-style="italic">k</tspan>'
            f'<tspan font-size="7" dy="2">{j}</tspan><tspan dy="-5.5">&#8203;</tspan>')


def eq_plot(x0, y0, ppu, xr, yr):
    """Panel with the same number of pixels per unit on both axes."""
    return Plot(x0, y0, (xr[1] - xr[0]) * ppu, (yr[1] - yr[0]) * ppu, xr, yr)


def to_data(p, px, py):
    """Pixel position -> data coordinates of panel p."""
    return (p.xmin + (px - p.x0) / p.w * (p.xmax - p.xmin),
            p.ymin + (p.y0 + p.h - py) / p.h * (p.ymax - p.ymin))


def trimmed_arrow(p, a, b, color, width=1.3, head=7.0, cut0=0.0, cut1=0.0, dash=None, opacity=1.0):
    """Arrow from data point a to b, shortened by cut0 / cut1 pixels at its ends."""
    ax, ay, bx, by = p.X(a[0]), p.Y(a[1]), p.X(b[0]), p.Y(b[1])
    L = math.hypot(bx - ax, by - ay)
    ux, uy = (bx - ax) / L, (by - ay) / L
    s = to_data(p, ax + ux * cut0, ay + uy * cut0)
    e = to_data(p, bx - ux * cut1, by - uy * cut1)
    p.arrow(s, e, color, width, head, dash, opacity)


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


# ============================================================ iraksak-dizi
# x_k = ((-1)^k, 1/2^k): the even-indexed subsequence tends to (1, 0), the
# odd-indexed one to (-1, 0). Unequal scales on purpose: the heights halve.
K_MAX = 8
even = [(1.0, 0.5 ** k) for k in range(2, K_MAX + 1, 2)]
odd = [(-1.0, 0.5 ** k) for k in range(1, K_MAX + 1, 2)]
p = Plot(40, 34, 440, 232, (-1.5, 1.5), (-0.1, 0.6))
p.origin_axes("", "", opacity=0.45)
for v, s in ((0.25, "1/4"), (0.5, "1/2")):
    tick(p, 0, v, False)
    p.label(0, v, s, -7, 4, TEXT, 11, "end")
# limits of the two subsequences (not terms of the sequence)
hollow(p, (1, 0), THEORY, 5.0, 1.8)
hollow(p, (-1, 0), PRACTICE, 5.0, 1.8)
p.label(1, 0, "(1, 0)", 0, 21, THEORY, 12, "middle")
p.label(-1, 0, "(" + MINUS + "1, 0)", 0, 21, PRACTICE, 12, "middle")
p.points(even, THEORY, 3.8)
p.points(odd, PRACTICE, 3.8)
for k, pt in zip((2, 4), even):
    p.label(*pt, xk(k), 9, 4, THEORY, 12.5)
for k, pt in zip((1, 3), odd):
    p.label(*pt, xk(k), -9, 4, PRACTICE, 12.5, "end")
# one arrow per branch, pointing at the limit of that subsequence
AX, TOP, BOT = 0.8, 0.40, 0.06
p.arrow((AX, TOP), (AX, BOT), THEORY, 1.6, 8)
p.arrow((-AX, TOP), (-AX, BOT), PRACTICE, 1.6, 8)
p.label(AX, TOP, "(" + it("x") + sub("2" + it("j")) + ")", 0, -8, THEORY, 12.5, "middle")
p.label(-AX, TOP, "(" + it("x") + sub("2" + it("j") + " + 1") + ")", 0, -8, PRACTICE, 12.5, "middle")
save("iraksak-dizi", figure(
    520, 310, [p],
    "<em>x<sub>k</sub></em> = ((&#8722;1)<sup><em>k</em></sup>, 1/2<sup><em>k</em></sup>) dizisinin ilk 8 terimi iki kol "
    "hâlinde ilerler. Çift indisli alt dizi (<em>x</em><sub>2<em>j</em></sub>) (mavi) (1, 0) noktasına, tek indisli "
    "alt dizi (<em>x</em><sub>2<em>j</em>+1</sub>) (turuncu) (&#8722;1, 0) noktasına yaklaşır; yükseklik her "
    "adımda yarıya iner. İki alt dizinin limitleri farklı olduğundan dizi ıraksaktır.",
    aria="Two branches of a planar sequence: even terms descending to (1, 0), odd terms descending to (-1, 0)"))

# ============================================================ bw-yuvarlar
# Choosing k_1 < k_2 < k_3 with x_{k_j} in B(a, 1/j) \ {a}.
p = eq_plot(40, 30, 165, (-1.25, 1.35), (-1.32, 1.2))
RADII = ((1.0, "1"), (0.5, "1/2"), (1 / 3, "1/3"))
for r, _ in RADII:
    p.circle(0, 0, r, THEORY, 1.5, "5 3")
p.label(0, -1.0, it("B") + "(" + it("a") + ", 1)", 0, 17, THEORY, 12, "middle")
p.label(0, -0.5, it("B") + "(" + it("a") + ", 1/2)", 0, 16, THEORY, 12, "middle")
p.label(0, -1 / 3, it("B") + "(" + it("a") + ", 1/3)", 0, 13.5, THEORY, 11, "middle")
# terms of the sequence that are not chosen
others = [(-1.12, -0.3), (-0.62, 0.45), (0.3, -0.76), (1.15, 0.55), (-0.3, -0.26), (0.63, -0.2),
          (-0.46, -0.72), (0.13, 0.74), (0.21, -0.15), (-0.85, 0.95), (1.05, -0.9)]
for q in others:
    p.add(f'<circle cx="{p.X(q[0]):.1f}" cy="{p.Y(q[1]):.1f}" r="2.4" fill="{TEXT}" opacity="0.35"/>')
# the chosen terms
chosen = [(0.76 * math.cos(math.radians(32)), 0.76 * math.sin(math.radians(32))),
          (0.415 * math.cos(math.radians(58)), 0.415 * math.sin(math.radians(58))),
          (0.2 * math.cos(math.radians(150)), 0.2 * math.sin(math.radians(150)))]
assert 0.5 < math.hypot(*chosen[0]) < 1 and 1 / 3 < math.hypot(*chosen[1]) < 0.5 and 0 < math.hypot(*chosen[2]) < 1 / 3
path = chosen + [(0.0, 0.0)]
for a, b in zip(path, path[1:]):
    trimmed_arrow(p, a, b, PRACTICE, 1.2, 6.5, 6, 6, None, 0.85)
p.points(chosen, PRACTICE, 3.8)
dot(p, (0, 0), TEXT, 3.6)
p.label(0, 0, it("a"), 6, 13, TEXT, 13, "start", True)
p.label(*chosen[0], x_kj(1), 8, 4, PRACTICE, 13)
# x_{k_2} sits in the thin ring 1/3 < r < 1/2, so its name goes along the top of that ring
ang = math.radians(97)
p.label(0.4167 * math.cos(ang), 0.4167 * math.sin(ang), x_kj(2), 0, 3, PRACTICE, 13, "middle")
p.label(*chosen[2], x_kj(3), 0, 16, PRACTICE, 13, "middle")
save("bw-yuvarlar", figure(
    500, 460, [p],
    "İndislerin seçimi: <em>x</em><sub><em>k</em><sub>1</sub></sub> terimi <em>B</em>(<em>a</em>, 1) yuvarından, "
    "<em>x</em><sub><em>k</em><sub>2</sub></sub> (<em>k</em><sub>2</sub> &gt; <em>k</em><sub>1</sub>) "
    "<em>B</em>(<em>a</em>, 1/2) yuvarından, <em>x</em><sub><em>k</em><sub>3</sub></sub> "
    "(<em>k</em><sub>3</sub> &gt; <em>k</em><sub>2</sub>) <em>B</em>(<em>a</em>, 1/3) yuvarından alınır; hepsi "
    "<em>a</em>'dan farklıdır. Her yuvara dizinin sonsuz çoklukta terimi düştüğü için seçim hiç tıkanmaz. "
    "Gri noktalar dizinin seçilmeyen terimleridir.",
    aria="Three nested balls around a with radii 1, 1/2 and 1/3 and one chosen term in each, joined by arrows towards a"))

# ============================================================ kapali-degil
# F = [-1, 1) x [0, 1] and the sequence (1 - 1/k, 0) in F converging to (1, 0), not in F.
p = eq_plot(40, 30, 140, (-1.5, 1.5), (-0.42, 1.4))
p.origin_axes("", "", opacity=0.45)
p.polygon([(-1, 0), (1, 0), (1, 1), (-1, 1)], THEORY, 0.16)
p.line([(1, 0), (-1, 0), (-1, 1), (1, 1)], THEORY, 1.9)
p.line([(1, 0), (1, 1)], THEORY, 1.7, "5 3")
hollow(p, (1, 1), THEORY, 3.4)
tick(p, -1, 0, True)
p.label(-1, 0, MINUS + "1", 0, 17, TEXT, 11, "middle")
p.label(-0.5, 0.55, it("F"), 0, 0, THEORY, 16, "middle", True)
seq = [(1 - 1 / k, 0.0) for k in range(1, 7)]
trimmed_arrow(p, (0.42, 0.14), (0.97, 0.14), PRACTICE, 1.3, 7.0)
p.points(seq, PRACTICE, 3.4)
hollow(p, (1, 0), PRACTICE, 4.4, 1.8)
p.label(*seq[0], xk(1), 5, 17, PRACTICE, 12.5)
p.label(*seq[1], xk(2), 0, 17, PRACTICE, 12.5, "middle")
p.label(*seq[2], xk(3), 0, 17, PRACTICE, 12.5, "middle")
p.label(1, 0, "(1, 0)", 0, 19, PRACTICE, 12, "middle")
p.label(1, 0, it("F") + "'de değil", 0, 34, PRACTICE, 12, "middle")
save("kapali-degil", figure(
    520, 320, [p],
    "<em>F</em> = [&#8722;1, 1) &#215; [0, 1] kümesinin sağ kenarı (kesikli) kümeye ait değildir. "
    "<em>x<sub>k</sub></em> = (1 &#8722; 1/<em>k</em>, 0) terimlerinin hepsi <em>F</em>'dedir ve (1, 0) noktasına "
    "yakınsar; oysa (1, 0) &#8713; <em>F</em>. Bu yüzden <em>F</em> kapalı değildir.",
    aria="A rectangle whose right edge is missing, with points on the bottom edge converging to the missing corner"))

# ============================================================ hiperbol-bolge
# A = {xy >= 1} and {x^2 + y^2 < 5}: two lens-shaped pieces; p_k = (1, 2 - 1/k) -> (1, 2), not in A.
R5 = math.sqrt(5)
XA, XB = math.sqrt((5 - math.sqrt(21)) / 2), math.sqrt((5 + math.sqrt(21)) / 2)   # 0.4569, 2.1889
assert abs(XA ** 2 + 1 / XA ** 2 - 5) < 1e-12 and abs(XB ** 2 + 1 / XB ** 2 - 5) < 1e-12
L = 2.6
p = eq_plot(40, 30, 78, (-L, L), (-L, L))
p.origin_axes("x", "y", opacity=0.45)
for v in (1, 2):
    tick(p, v, 0, True)
    tick(p, 0, v, False)
    p.label(v, 0, str(v), 0, 15, TEXT, 11, "middle")
    p.label(0, v, str(v), -7, 4, TEXT, 11, "end")
# reference curves: the whole circle and the whole hyperbola, faint
p.circle(0, 0, R5, TEXT, 1.0, "5 3", "none", 0.45)
for s in (1, -1):
    xs = [1 / L + (L - 1 / L) * i / 200 for i in range(201)]
    p.line([(s * x, s / x) for x in xs], TEXT, 1.0, None, 0.45)
# the set A: lens between the hyperbola branch and the circle, and its mirror image
th_a, th_b = math.atan2(1 / XA, XA), math.atan2(1 / XB, XB)
hyp = [(XA + (XB - XA) * i / 160, 1 / (XA + (XB - XA) * i / 160)) for i in range(161)]
arc = circle_pts(0, 0, R5, th_b, th_a, 120)
for s in (1, -1):
    h = [(s * x, s * y) for x, y in hyp]
    c = [(s * x, s * y) for x, y in arc]
    p.polygon(h + c, THEORY, 0.2)
    p.line(h, THEORY, 2.1)
    p.line(c, THEORY, 1.9, "5 3")
    for q in ((s * XA, s / XA), (s * XB, s / XB)):
        hollow(p, q, THEORY, 3.3)
    p.label(s * 1.62, s * 1.2, it("A"), 0, 5, THEORY, 15, "middle", True)
p.label(-R5 / math.sqrt(2), R5 / math.sqrt(2), it("x") + "² + " + it("y") + "² = 5", -4, -4, TEXT, 11.5, "end")
p.label(L, 1 / L, it("xy") + " = 1", 6, 4, TEXT, 11.5)
# the sequence p_k = (1, 2 - 1/k) and its limit (1, 2)
pk = [(1.0, 2 - 1 / k) for k in range(1, 6)]
trimmed_arrow(p, (1.14, 1.25), (1.14, 1.84), PRACTICE, 1.3, 7.0)
p.points(pk, PRACTICE, 3.0)
hollow(p, (1, 2), PRACTICE, 4.2, 1.8)
p.label(*pk[0], xk(1, "p"), -7, 13, PRACTICE, 12.5, "end")
p.label(*pk[1], xk(2, "p"), -7, 1, PRACTICE, 12.5, "end")
p.label(1, 2, "(1, 2) " + it("A") + "'da değil", 8, -8, PRACTICE, 12)
save("hiperbol-bolge", figure(
    500, 480, [p],
    "<em>A</em> kümesi <em>xy</em> = 1 hiperbolü (düz, kümeye ait) ile <em>x</em><sup>2</sup> + <em>y</em><sup>2</sup> = 5 "
    "çemberi (kesikli, kümeye ait değil) arasındaki iki mercek biçimli parçadır; köşeler çemberin üstünde olduğundan "
    "kümeye ait değildir. <em>p<sub>k</sub></em> = (1, 2 &#8722; 1/<em>k</em>) terimleri <em>A</em>'dadır ve "
    "(1, 2) noktasına yakınsar; (1, 2) &#8713; <em>A</em>.",
    aria="Two lens shaped regions between the hyperbola xy equal 1 and the circle of radius root five, with points climbing to (1, 2) on the circle"))
