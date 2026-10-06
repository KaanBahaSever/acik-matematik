# -*- coding: utf-8 -*-
"""
Figures of the chapter "Bölünmüş Farklar"
(dersler/numerik-analiz/bolunmus-farklar.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution,
exercise or callout), never inside a definition box and never directly under a
heading. The figures are NOT produced at build time. Run

    python scripts/numerical_figures/bfk.py
    python scripts/center_figures.py "numerical-bfk-*.md"
    python scripts/check_figure_labels.py "scripts/_figures/numerical-bfk-*.md"

and paste the markup of scripts/_figures/numerical-bfk-<name>.md into the .qmd.
Captions are Turkish on purpose; aria labels are plain ASCII.

The polynomials are rebuilt here from the data of the chapter (Newton form for
the cubic, the Lagrange form for P_4), so every drawn value matches the text.
"""
import html
import re
import sys
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, dot, hollow, TEXT, THEORY, PRACTICE, BASE, REMARK, BG  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "numerical-bfk-"

MINUS = "&#8722;"
APPROX = "&#8776;"


def save(name, markup):
    (OUT_DIR / f"{PREFIX}{name}.md").write_text(markup, encoding="utf-8", newline="\n")
    print(f"{PREFIX}{name}.md")


def it(s):
    """Italic run inside an SVG <text>."""
    return f'<tspan font-style="italic">{s}</tspan>'


def sub(s, size=9):
    """Subscript inside an SVG <text>; the zero-width space resets the baseline."""
    return f'<tspan font-size="{size}" dy="3.5">{s}</tspan><tspan dy="-3.5">&#8203;</tspan>'


def sup(s, size=9):
    """Superscript inside an SVG <text>."""
    return f'<tspan font-size="{size}" dy="-5">{s}</tspan><tspan dy="5">&#8203;</tspan>'


def xi(k):
    return it("x") + sub(str(k))


def fbr(*idx):
    """The divided difference f[x_i, ..., x_j] with real subscripts."""
    return it("f") + "[" + ", ".join(xi(k) for k in idx) + "]"


def pk(k):
    return it("P") + sub(str(k))


def dec(v, digits=2):
    """Decimal comma and a true minus sign: -0.5 -> '−0,5'."""
    s = f"{v:.{digits}f}".rstrip("0").rstrip(".")
    if s in ("-0", ""):
        s = "0"
    return s.replace(".", ",").replace("-", MINUS)


def text_w(s, size):
    """Rough advance width of a label: 0.56 em per character, tspans at their own size."""
    w = 0.0
    for a, inner in re.findall(r"<tspan\b([^>]*)>(.*?)</tspan>", s):
        m = re.search(r'font-size="([\d.]+)"', a)
        w += len(html.unescape(inner).replace("​", "")) * 0.56 * (float(m.group(1)) if m else size)
    rest = re.sub(r"<tspan\b[^>]*>.*?</tspan>", "", s)
    w += len(html.unescape(re.sub(r"<[^>]+>", "", rest)).replace("​", "")) * 0.56 * size
    return w


def plate(p, x, y, s, dx=0, dy=0, size=11.5, anchor="start", opacity=0.9):
    """Page-coloured rounded plate under a label that has to sit on lines."""
    px, py = p.X(x) + dx, p.Y(y) + dy
    w = text_w(s, size)
    x0 = px - (w / 2 if anchor == "middle" else w if anchor == "end" else 0)
    p.add(f'<rect x="{x0 - 2.5:.1f}" y="{py - 0.8 * size - 1:.1f}" width="{w + 5:.1f}" '
          f'height="{size + 3:.1f}" rx="3" fill="{BG}" opacity="{opacity}"/>')


def plabel(p, x, y, s, dx=0, dy=0, color=TEXT, size=11.5, anchor="start", bold=False):
    plate(p, x, y, s, dx, dy, size, anchor)
    p.label(x, y, s, dx, dy, color, size, anchor, bold)


def graph_runs(f, x0, x1, ylo, yhi, n=400):
    """Samples of y = f(x) on [x0, x1], cut into the runs that stay in [ylo, yhi]."""
    runs, cur = [], []
    for k in range(n + 1):
        x = x0 + (x1 - x0) * k / n
        y = f(x)
        if ylo <= y <= yhi:
            cur.append((x, y))
        elif cur:
            runs.append(cur)
            cur = []
    if cur:
        runs.append(cur)
    return [r for r in runs if len(r) > 1]


def lagrange(xs, ys):
    """The interpolating polynomial as a callable (exact rational nodes, float evaluation)."""
    def f(x):
        total = 0.0
        for i, (xi_, yi) in enumerate(zip(xs, ys)):
            term = float(yi)
            for j, xj in enumerate(xs):
                if j != i:
                    term *= (x - float(xj)) / float(xi_ - xj)
            total += term
        return total
    return f


# ============================================================
# ucgen-sema: the triangular scheme of the divided difference table, four nodes
# ============================================================
# Pixel coordinates: the panel maps data units one-to-one onto pixels, y downward.
W0, H0 = 640, 330
sc = Plot(0, 0, W0, H0, (0, W0), (H0, 0))
FS = 13.5                      # font size inside the boxes
BOX_H = 28
ROW = 34                       # vertical distance of two half rows
TOP = 52                       # centre of half row 0
COL_X = [20, 120, 250, 420]    # left edges of the four columns
COL_W = [70, 100, 136, 172]    # box widths


def row_y(r):
    return TOP + r * ROW


cells = {}
for c in range(4):
    for i in range(4 - c):
        cells[(c, i)] = (COL_X[c], row_y(2 * i + c), tuple(range(i, i + c + 1)))

# arrows first, so the boxes sit on top of their ends
for (c, i), (bx, by, idx) in cells.items():
    if c == 0:
        continue
    for src in ((c - 1, i), (c - 1, i + 1)):
        sx, sy, _ = cells[src]
        sgn = 1 if src[1] == i + 1 else -1          # +1: the source lies below the target
        x0, y0 = sx + COL_W[c - 1] + 3, sy - sgn * 4
        x1, y1 = bx - 3, by + sgn * 6
        sc.arrow((x0, y0), (x1, y1), REMARK, 1.3, 7.0, None, 0.85)

for (c, i), (bx, by, idx) in cells.items():
    top = i == 0
    color = PRACTICE if top else TEXT
    sc.add(f'<rect x="{bx}" y="{by - BOX_H / 2:.1f}" width="{COL_W[c]}" height="{BOX_H}" rx="5" '
           f'fill="{PRACTICE if top else BG}" fill-opacity="{0.16 if top else 1}" '
           f'stroke="{color}" stroke-width="{1.5 if top else 1.1}" stroke-opacity="{1 if top else 0.6}"/>')
    s = fbr(*idx)
    cx = bx + COL_W[c] / 2
    sc.text_px(cx, by + 4.5, s, color, FS, "middle", top)
    if top:
        w = 0.82 * text_w(s, FS)       # the estimate runs wide; 0.82 matches the rendered width
        sc.add(f'<line x1="{cx - w / 2:.1f}" y1="{by + 12:.1f}" x2="{cx + w / 2:.1f}" y2="{by + 12:.1f}" '
               f'stroke="{PRACTICE}" stroke-width="1.3"/>')

# the label of the Newton coefficients, in the empty corner above the top edge
sc.text_px(COL_X[2] + COL_W[2] / 2 + 40, row_y(0) + 4, "Newton katsayıları", PRACTICE, 13, "middle", True)

# how f[x1, x2, x3] is computed, under its own box
bx, by, _ = cells[(2, 1)]
rule = ("(" + fbr(2, 3) + " " + MINUS + " " + fbr(1, 2) + ") / (" + xi(3) + " " + MINUS + " " + xi(1) + ")")
sc.add(f'<line x1="{bx + COL_W[2] / 2:.1f}" y1="{by + BOX_H / 2 + 2:.1f}" x2="{bx + COL_W[2] / 2:.1f}" '
       f'y2="{by + BOX_H / 2 + 16:.1f}" stroke="{THEORY}" stroke-width="1" stroke-dasharray="3 2"/>')
sc.text_px(bx + COL_W[2] / 2 - 30, by + BOX_H / 2 + 30, "= " + rule, THEORY, 12)

save("ucgen-sema", figure(
    W0, H0, [sc],
    "Dört noktalı bölünmüş fark tablosunun hesap şeması. Her kutu, solundaki üst ve alt komşusundan "
    "hesaplanır: alttaki eksi üstteki, bölü kapsanan ilk ve son noktanın farkı. Örneğin "
    "<em>f</em>[<em>x</em><sub>1</sub>, <em>x</em><sub>2</sub>, <em>x</em><sub>3</sub>] = "
    "(<em>f</em>[<em>x</em><sub>2</sub>, <em>x</em><sub>3</sub>] &#8722; "
    "<em>f</em>[<em>x</em><sub>1</sub>, <em>x</em><sub>2</sub>]) / "
    "(<em>x</em><sub>3</sub> &#8722; <em>x</em><sub>1</sub>). Üst kenardaki altı çizili kutular "
    "Newton katsayılarıdır.",
    aria="Triangular scheme of the divided difference table for four nodes: the values f[x_i] in the "
         "first column, each further box computed from its upper and lower left neighbours (twelve arrows), "
         "and the top edge f[x_0], f[x_0, x_1], f[x_0, x_1, x_2], f[x_0, x_1, x_2, x_3] highlighted as the "
         "Newton coefficients"))

# ============================================================
# newton-terimleri: the partial sums P_0, ..., P_3 through (0, 2), (1, 3), (2, 12), (5, 147)
# ============================================================
NODES = [(0, 2), (1, 3), (2, 12), (5, 147)]
# divided differences, recomputed: coefficients 2, 1, 4, 1
xs = [Fraction(a) for a, _ in NODES]
table = [[Fraction(b) for _, b in NODES]]
for k in range(1, 4):
    prev = table[-1]
    table.append([(prev[i + 1] - prev[i]) / (xs[i + k] - xs[i]) for i in range(len(prev) - 1)])
COEF = [float(col[0]) for col in table]
assert COEF == [2.0, 1.0, 4.0, 1.0]


def partial(n):
    def f(x):
        total, prod = 0.0, 1.0
        for k in range(n + 1):
            total += COEF[k] * prod
            prod *= x - float(xs[k])
        return total
    return f


P = [partial(n) for n in range(4)]
assert abs(P[3](3) - 35) < 1e-12 and abs(P[2](5) - 87) < 1e-12

XR, YR = (-0.5, 5.4), (-10.0, 160.0)
p = Plot(55, 30, 400, 290, XR, YR)
p.grid((0, 1, 2, 3, 4, 5), (0, 40, 80, 120, 160))
p.axes((0, 1, 2, 3, 4, 5), (0, 40, 80, 120, 160), "", it("y"), dec, dec)
# the x label goes to the tick row, so that the label of P_0 has the corner to itself
p.label(XR[1], YR[0], it("x"), 2, 16, TEXT, 11, "start", italic=False)
p.line([(XR[0], 0), (XR[1], 0)], TEXT, 1.0, None, 0.45)
STYLE = [(REMARK, 1.8), (BASE, 1.8), (THEORY, 2.0), (PRACTICE, 3.0)]
for n in range(4):
    for run in graph_runs(P[n], XR[0], XR[1], YR[0], YR[1]):
        p.line(run, STYLE[n][0], STYLE[n][1])

# the last term at x = 5: from P_2(5) = 87 up to P_3(5) = 147
p.line([(5, 87), (5, 147)], TEXT, 1.1, "4 3", 0.75)
hollow(p, (5, 87), THEORY, 3.4, 1.5)
# a framed note right of the gap; the frame is as wide as the label checker's width estimate
NOTE = ["son terim:", it("x") + "(" + it("x") + " " + MINUS + " 1)(" + it("x") + " " + MINUS + " 2)"]
note_w = max(text_w(s_, 11.5) for s_ in NOTE) + 6
nx, ny = p.X(5) + 9, p.Y(124)
p.add(f'<rect x="{nx:.1f}" y="{ny - 19:.1f}" width="{note_w:.1f}" height="38" rx="4" fill="{BG}" '
      f'stroke="{TEXT}" stroke-width="0.8" stroke-opacity="0.35"/>')
p.text_px(nx + note_w / 2, ny - 4, NOTE[0], TEXT, 11.5, "middle")
p.text_px(nx + note_w / 2, ny + 12, NOTE[1], TEXT, 11.5, "middle")

for z in NODES:
    dot(p, z, TEXT, 4.0)
hollow(p, (3, 35), PRACTICE, 4.2, 1.8)
p.label(3, 35, pk(3) + "(3) = 35", -8, -8, PRACTICE, 12, "end", True)

X = it("x")
lab = [
    pk(0) + "(" + X + ") = 2",
    pk(1) + "(" + X + ") = " + X + " + 2",
    pk(2) + "(" + X + ") = 4" + X + sup("2") + " " + MINUS + " 3" + X + " + 2",
    pk(3) + "(" + X + ") = " + X + sup("3") + " + " + X + sup("2") + " " + MINUS + " " + X + " + 2",
]
# short names at the right ends of the curves, the formulas in a key in the empty upper left corner
p.label(XR[1], P[0](XR[1]), pk(0), 6, 12, REMARK, 12)
p.label(XR[1], P[1](XR[1]), pk(1), 6, -2, BASE, 12)
p.label(XR[1], P[2](XR[1]), pk(2), 6, 4, THEORY, 12)
# P_3 leaves the panel at the top; its name sits right of that exit
x_top = 5.0
while P[3](x_top) < YR[1]:
    x_top += 0.001
p.label(x_top, YR[1], pk(3), 7, 6, PRACTICE, 12.5, "start", True)
KEY_X, KEY_Y, KEY_DY = -0.3, 150.0, 13.5
p.add(f'<rect x="{p.X(KEY_X) - 8:.1f}" y="{p.Y(KEY_Y) - 13:.1f}" width="190" height="{4 * KEY_DY * p.h / 170 + 6:.1f}" '
      f'rx="4" fill="{BG}" stroke="{TEXT}" stroke-width="0.8" stroke-opacity="0.35"/>')
for n in (3, 2, 1, 0):
    yk = KEY_Y - (3 - n) * KEY_DY
    p.line([(KEY_X, yk + 1.5), (KEY_X + 0.35, yk + 1.5)], STYLE[n][0], STYLE[n][1] + 0.4)
    p.label(KEY_X + 0.45, yk, lab[n], 0, 4, STYLE[n][0], 11.5, "start", n == 3)

save("newton-terimleri", figure(
    p.x0 + p.w + 175, p.y0 + p.h + 35, [p],
    "Newton biçiminin kısmi toplamları. <em>P</em><sub>0</sub> yalnız (0; 2) noktasından, "
    "<em>P</em><sub>1</sub> ilk iki noktadan, <em>P</em><sub>2</sub> ilk üç noktadan geçer. "
    "<em>P</em><sub>2</sub>(5) = 87 olduğundan (5; 147) noktasına ancak son terim "
    "<em>x</em>(<em>x</em> &#8722; 1)(<em>x</em> &#8722; 2) eklenince ulaşılır. "
    "İçi boş daire <em>P</em><sub>3</sub>(3) = 35 değeridir.",
    aria="Partial sums of the Newton form through the points (0, 2), (1, 3), (2, 12), (5, 147): "
         "P_0 = 2, P_1 = x + 2, P_2 = 4x^2 - 3x + 2 and the thick cubic P_3 = x^3 + x^2 - x + 2, "
         "with P_3(3) = 35 and the dashed gap from P_2(5) = 87 to 147 filled by the last term"))

# ============================================================
# p4-ileri-geri: one P_4 through five equally spaced nodes, read from either end of the table
# ============================================================
NX = [Fraction(10, 10), Fraction(13, 10), Fraction(16, 10), Fraction(19, 10), Fraction(22, 10)]
NY = [Fraction("0.7651977"), Fraction("0.6200860"), Fraction("0.4554022"), Fraction("0.2818186"),
      Fraction("0.1103623")]
P4 = lagrange(NX, NY)
V11, V2 = P4(1.1), P4(2.0)
assert f"{V11:.7f}" == "0.7196460" and f"{V2:.7f}" == "0.2238754"

XR, YR = (0.9, 2.3), (0.0, 0.85)
q = Plot(60, 25, 420, 290, XR, YR)
XT = (1.0, 1.3, 1.6, 1.9, 2.2)
YT = (0.0, 0.2, 0.4, 0.6, 0.8)
q.grid(XT, YT)
q.axes(XT, YT, it("x"), it("y"), lambda v: f"{v:.1f}".replace(".", ","), lambda v: dec(v, 1))
# the two ends of the table as bands on the x axis
band = 7 * (YR[1] - YR[0]) / q.h
q.polygon([(1.0, 0), (1.3, 0), (1.3, band), (1.0, band)], THEORY, 0.35, THEORY, 1.0)
q.polygon([(1.9, 0), (2.2, 0), (2.2, band), (1.9, band)], PRACTICE, 0.35, PRACTICE, 1.0)
q.label(1.15, 0, "tablonun başı: ileri fark", 0, 34, THEORY, 11.5, "middle", True)
q.label(2.05, 0, "tablonun sonu: geri fark", 0, 34, PRACTICE, 11.5, "middle", True)

q.line([(0.95 + 1.3 * k / 300, P4(0.95 + 1.3 * k / 300)) for k in range(301)], TEXT, 2.2)
q.label(1.5, P4(1.5), pk(4) + "(" + it("x") + ")", 8, -8, TEXT, 12.5)

q.vline(1.1, 0, V11, THEORY, "4 3", 0.8)
q.vline(2.0, 0, V2, PRACTICE, "4 3", 0.8)
for a, b in zip(NX, NY):
    dot(q, (float(a), float(b)), TEXT, 4.0)
hollow(q, (1.1, V11), THEORY, 4.6, 1.9)
hollow(q, (2.0, V2), PRACTICE, 4.6, 1.9)
plabel(q, 1.1, V11, pk(4) + "(1,1) " + APPROX + " 0,7196460", 9, -10, THEORY, 12, "start", True)
plabel(q, 2.0, V2, pk(4) + "(2) " + APPROX + " 0,2238754", 9, -11, PRACTICE, 12, "start", True)

save("p4-ileri-geri", figure(
    q.x0 + q.w + 70, q.y0 + q.h + 50, [q],
    "(1,0; 0,7651977), …, (2,2; 0,1103623) beş noktasından geçen tek bir <em>P</em><sub>4</sub> polinomu. "
    "<em>x</em> = 1,1 tablonun başında olduğundan ileri fark formülüyle, <em>x</em> = 2 tablonun sonunda "
    "olduğundan geri fark formülüyle hesaplanır; iki değer de aynı eğrinin üzerindedir.",
    aria="The degree four interpolating polynomial through five equally spaced nodes from 1.0 to 2.2, "
         "with the start of the table marked for the forward difference value P_4(1.1) = 0.7196460 and "
         "the end of the table marked for the backward difference value P_4(2) = 0.2238754"))
