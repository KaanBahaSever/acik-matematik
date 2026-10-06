# -*- coding: utf-8 -*-
"""
Figures of the chapter "Secant ve Regula Falsi Metodları"
(dersler/numerik-analiz/secant-ve-regula-falsi.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box and never directly under a heading.
The figures are NOT produced at build time. Run

    python scripts/numerical_figures/sec.py
    python scripts/center_figures.py "numerical-sec-*.md"
    python scripts/check_figure_labels.py "scripts/_figures/numerical-sec-*.md"

and paste the markup of scripts/_figures/numerical-sec-<name>.md into the .qmd.
Captions are Turkish on purpose; aria labels are plain ASCII.
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, dot, hollow, TEXT, THEORY, PRACTICE, BASE, REMARK, BG  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "numerical-sec-"

MINUS = "&#8722;"


def save(name, markup):
    (OUT_DIR / f"{PREFIX}{name}.md").write_text(markup, encoding="utf-8", newline="\n")
    print(f"{PREFIX}{name}.md")


def it(s):
    """Italic run inside an SVG <text>."""
    return f'<tspan font-style="italic">{s}</tspan>'


def sub(s, size=8.5):
    """Subscript inside an SVG <text>."""
    return f'<tspan font-size="{size}" dy="3">{s}</tspan><tspan dy="-3">&#8203;</tspan>'


def sup(s, size=8.5):
    """Superscript inside an SVG <text>."""
    return f'<tspan font-size="{size}" dy="-5">{s}</tspan><tspan dy="5">&#8203;</tspan>'


def pn(k):
    """The label p_k."""
    return it("p") + sub(k)


def dec(v, digits=2):
    """Decimal comma and a true minus sign: -0.5 -> '−0,5'."""
    s = f"{v:.{digits}f}".rstrip("0").rstrip(".")
    if s in ("-0", ""):
        s = "0"
    return s.replace(".", ",").replace("-", MINUS)


def x_axis(p, label="x"):
    """The line y = 0 across the panel with an arrowhead and the axis name."""
    over = 10 / p.w * (p.xmax - p.xmin)
    p.arrow((p.xmin, 0), (p.xmax + over, 0), TEXT, 1.1, 7.0, None, 0.6)
    p.label(p.xmax + over, 0, it(label), 4, 4, TEXT, 12.5)


def sample(f, a, b, n=240):
    return [(a + (b - a) * k / n, f(a + (b - a) * k / n)) for k in range(n + 1)]


def chord_root(a, fa, b, fb):
    return b - fb * (b - a) / (fb - fa)


# ============================================================
# shared frame of the two method pictures (secant-yontem, regula-falsi-yontem)
# ============================================================
# A generic convex increasing curve y = e^(0.6 x) - 8 with p0 = 1 and p1 = 5.6.
# Both methods start with the same two points, so the first two chords agree;
# the third step shows the difference.
def f_gen(x):
    return math.exp(0.6 * x) - 8


G0, G1 = 1.0, 5.6
GEN_ROOT = math.log(8) / 0.6                  # 3.4657
XG, YG = (-0.45, 6.35), (-8.6, 23.5)
G_TOP = math.log(8 + 22.8) / 0.6              # the curve stops just under the top edge


def secant_iterates(f, a, b, n):
    ps = [a, b]
    for _ in range(n):
        ps.append(chord_root(ps[-2], f(ps[-2]), ps[-1], f(ps[-1])))
    return ps


def regula_falsi_iterates(f, a, b, n):
    """Iterates and, for every new one, the index k of the other end of its chord."""
    ps, ends, k = [a, b], [], 0
    for _ in range(n):
        last = len(ps) - 1
        ends.append(k)
        new = chord_root(ps[k], f(ps[k]), ps[last], f(ps[last]))
        if f(new) * f(ps[last]) < 0:
            k = last
        ps.append(new)
    return ps, ends


def generic_frame():
    g = Plot(30, 30, 452, 300, XG, YG)
    g.origin_axes(it("x"), it("y"))
    g.line(sample(f_gen, XG[0], G_TOP), THEORY, 2.0)
    # curve name in the gap between the curve and the guide at p1
    x_name = math.log(8 + 6) / 0.6
    g.label(x_name, f_gen(x_name), it("y") + " = " + it("f") + "(" + it("x") + ")", 10, 4, THEORY, 12.5)
    return g


def point_label(k):
    return "(" + pn(str(k)) + ", " + it("f") + "(" + pn(str(k)) + "))"


def mark_iterates(g, ps):
    """Dashed guides from the axis to the curve, the points on the curve and the axis ticks."""
    for x in ps:
        g.vline(x, 0, f_gen(x), TEXT, "3 3", 0.6)
    for k, x in enumerate(ps):
        dot(g, (x, f_gen(x)), PRACTICE, 4.2 if k < 2 else 3.2)
    hollow(g, (GEN_ROOT, 0), TEXT, 3.6)
    g.label(G0, f_gen(G0), point_label(0), 0, 20, TEXT, 12, "middle")
    g.label(G1, f_gen(G1), point_label(1), -12, 0, TEXT, 12, "end")
    g.label(G0, 0, pn("0"), 0, -8, TEXT, 12.5, "middle")
    g.label(G1, 0, pn("1"), 0, 17, TEXT, 12.5, "middle")


CHORD_SHADE = (0.45, 0.7, 1.0)

# ============================================================
# secant-yontem: the secant method on the generic curve
# ============================================================
gs = secant_iterates(f_gen, G0, G1, 3)        # 1, 5.6, 2.0538, 2.6930, 3.8766
g = generic_frame()
g.line([(gs[0], f_gen(gs[0])), (gs[1], f_gen(gs[1]))], PRACTICE, 1.8, None, CHORD_SHADE[0])
g.line([(gs[2], f_gen(gs[2])), (gs[1], f_gen(gs[1]))], PRACTICE, 1.8, None, CHORD_SHADE[1])
# the third secant runs from (p2, f(p2)) through (p3, f(p3)) on to the axis at p4
m3 = (f_gen(gs[3]) - f_gen(gs[2])) / (gs[3] - gs[2])
x_end = gs[4] + 0.25
g.line([(gs[2], f_gen(gs[2])), (x_end, f_gen(gs[2]) + m3 * (x_end - gs[2]))], PRACTICE, 1.8, None,
       CHORD_SHADE[2])
mark_iterates(g, gs[:4])
g.vline(gs[4], 0, f_gen(gs[4]), TEXT, "3 3", 0.6)
dot(g, (gs[4], f_gen(gs[4])), PRACTICE, 3.2)
g.label(gs[2], 0, pn("2"), -4, -8, TEXT, 12.5, "end")
g.label(gs[3], 0, pn("3"), -4, -8, TEXT, 12.5, "end")
g.label(GEN_ROOT, 0, it("p"), -5, -8, TEXT, 12.5, "end")
g.label(gs[4], 0, pn("4"), 4, 17, TEXT, 12.5)
save("secant-yontem", figure(
    520, 370, [g],
    "Secant metodu. (<em>p</em><sub>0</sub>, <em>f</em>(<em>p</em><sub>0</sub>)) ile (<em>p</em><sub>1</sub>, "
    "<em>f</em>(<em>p</em><sub>1</sub>)) noktalarından geçen kiriş <em>x</em> eksenini <em>p</em><sub>2</sub>'de "
    "keser. Sonraki her kiriş son iki noktadan geçer: (<em>p</em><sub>1</sub>, <em>f</em>(<em>p</em><sub>1</sub>)) "
    "ile (<em>p</em><sub>2</sub>, <em>f</em>(<em>p</em><sub>2</sub>)) kirişi <em>p</em><sub>3</sub>'ü, "
    "(<em>p</em><sub>2</sub>, <em>f</em>(<em>p</em><sub>2</sub>)) ile (<em>p</em><sub>3</sub>, "
    "<em>f</em>(<em>p</em><sub>3</sub>)) kirişi <em>p</em><sub>4</sub>'ü verir. <em>p</em><sub>4</sub>, "
    "<em>p</em> kökünün öbür yanına düşer.",
    aria="Secant method on a convex increasing curve y = f(x): the line through (p0, f(p0)) and (p1, f(p1)) "
         "meets the x axis at p2, the line through the points over p1 and p2 gives p3, and the line through "
         "the points over p2 and p3 gives p4, which lies right of the root p"))

# ============================================================
# regula-falsi-yontem: regula falsi on the same curve and scale
# ============================================================
gr, gends = regula_falsi_iterates(f_gen, G0, G1, 3)   # 1, 5.6, 2.0538, 2.6930, 3.0562; ends 0, 1, 1
g = generic_frame()
for n in range(2, 5):
    # the chord for p_n joins p_(n-1) with the kept end p_k of the other sign
    a, b = gr[n - 1], gr[gends[n - 2]]
    g.line([(a, f_gen(a)), (b, f_gen(b))], PRACTICE, 1.8, None, CHORD_SHADE[n - 2])
mark_iterates(g, gr)
dot(g, (G1, f_gen(G1)), PRACTICE, 5.2)
g.label(gr[2], 0, pn("2"), -4, -8, TEXT, 12.5, "end")
g.label(gr[3], 0, pn("3"), -4, -8, TEXT, 12.5, "end")
# p4 is boxed in by the chords above the axis and the curve below it: carry its guide on under the curve
P4_LOW = -4.6
g.vline(gr[4], f_gen(gr[4]), P4_LOW, TEXT, "2 2", 0.6)
g.label(gr[4], P4_LOW, pn("4"), 0, 15, TEXT, 12.5, "middle")
g.label(GEN_ROOT, 0, it("p"), 5, 17, TEXT, 12.5)
save("regula-falsi-yontem", figure(
    520, 370, [g],
    "Secant metodunun şeklindeki eğri ve başlangıç noktalarıyla Regula Falsi metodu. Yeni yaklaşımlarda "
    "<em>f</em> hep negatif kaldığından her kiriş, <em>f</em>'nin pozitif olduğu (<em>p</em><sub>1</sub>, "
    "<em>f</em>(<em>p</em><sub>1</sub>)) ucuna bağlı kalır ve <em>x</em> eksenini <em>p</em><sub>2</sub>, "
    "<em>p</em><sub>3</sub>, <em>p</em><sub>4</sub>'te keser. İlk iki kiriş Secant metodundakilerle aynıdır; "
    "ama <em>p</em><sub>4</sub> kökün öbür yanına geçmez. Yaklaşımlar <em>p</em>'ye hep soldan yaklaşır ve kök "
    "her adımda kirişin iki ucu arasında kalır.",
    aria="Regula falsi on the same convex curve: all chords pass through the fixed end (p1, f(p1)) and meet the "
         "x axis at p2, p3 and p4, which approach the root p from the left"))

# ============================================================
# kiris: the first two secant steps for cos x - x
# ============================================================
def f_cos(x):
    return math.cos(x) - x


P0, P1 = 0.5, math.pi / 4
F0, F1 = f_cos(P0), f_cos(P1)
P2 = chord_root(P0, F0, P1, F1)            # 0.736384139
F2 = f_cos(P2)                             # 0.004517719
P3 = chord_root(P1, F1, P2, F2)            # 0.739058139
ROOT = 0.7390851332151607

p = Plot(60, 30, 400, 280, (0.45, 0.85), (-0.12, 0.42))
p.grid([0.5, 0.6, 0.7, 0.8], [-0.1, 0.1, 0.2, 0.3, 0.4])
p.axes([0.5, 0.6, 0.7, 0.8], [-0.1, 0, 0.1, 0.2, 0.3, 0.4], "", it("y"), dec, dec)
x_axis(p)
x_top = 0.45                               # the curve leaves the panel at the top near x = 0.468
while f_cos(x_top) > 0.42:
    x_top += 0.0005
p.line(sample(f_cos, x_top, 0.85), THEORY, 2.0)
p.label(0.47, 0.06, it("y") + " = cos " + it("x") + " " + MINUS + " " + it("x"), 0, 0, THEORY, 12.5)
# guides from the two starting points to the axis
p.vline(P0, F0, 0, TEXT, "3 3", 0.55)
p.vline(P1, F1, 0, TEXT, "3 3", 0.55)
# the second chord (dashed) and the first chord
p.line([(P1, F1), (P2, F2)], PRACTICE, 1.6, "5 3", 0.85)
p.line([(P0, F0), (P1, F1)], PRACTICE, 2.2)
dot(p, (P0, F0), PRACTICE, 4.2)
dot(p, (P1, F1), PRACTICE, 4.2)
p.label(P0, 0, pn("0"), 0, 17, TEXT, 12.5, "middle")
p.label(P1, 0, pn("1"), 0, -8, TEXT, 12.5, "middle")

# zoom window around the crossings near the root
ZX, ZY = (0.7345, 0.7415), (-0.005, 0.007)
p.polygon([(ZX[0], ZY[0]), (ZX[1], ZY[0]), (ZX[1], ZY[1]), (ZX[0], ZY[1])], "none", 0, TEXT, 0.9)
q = Plot(290, 42, 160, 100, ZX, ZY)
IX0, IY0, IX1, IY1 = q.x0 - 5, q.y0 - 5, q.x0 + q.w + 5, q.y0 + q.h + 5
for cx in (IX0, IX1):
    p.add(f'<line x1="{p.X((ZX[0] + ZX[1]) / 2):.1f}" y1="{p.Y(ZY[1]):.1f}" x2="{cx:.1f}" y2="{IY1:.1f}" '
          f'stroke="{TEXT}" stroke-width="0.8" opacity="0.35"/>')
q.add(f'<rect x="{IX0:.1f}" y="{IY0:.1f}" width="{IX1 - IX0:.1f}" height="{IY1 - IY0:.1f}" rx="3" '
      f'fill="{BG}" stroke="{TEXT}" stroke-width="0.9" stroke-opacity="0.5"/>')
q.line([(ZX[0], 0), (ZX[1], 0)], TEXT, 1.0, None, 0.55)
q.line(sample(f_cos, ZX[0], ZX[1], 40), THEORY, 2.0)


def chord_y(a, fa, b, fb, x):
    return fa + (fb - fa) * (x - a) / (b - a)


# the chords cut to the zoom window
c1 = [(x, chord_y(P0, F0, P1, F1, x)) for x in (ZX[0], ZX[1])]
q.line(c1, PRACTICE, 2.2)
x_c2 = ZX[1]
c2 = [(P2, F2), (x_c2, chord_y(P1, F1, P2, F2, x_c2))]
q.line(c2, PRACTICE, 1.6, "5 3", 0.95)
dot(q, (P2, F2), PRACTICE, 3.2)
dot(q, (P2, 0), PRACTICE, 3.0)
hollow(q, (ROOT, 0), TEXT, 3.6)
q.label(P2, 0, pn("2"), -5, 15, TEXT, 12, "end")
q.label(ROOT, 0, it("p"), 6, -6, TEXT, 12)
save("kiris", figure(
    500, 335, [p, q],
    "<em>y</em> = cos <em>x</em> &#8722; <em>x</em> eğrisi ve Secant metodunun ilk iki kirişi. "
    "(<em>p</em><sub>0</sub>, <em>f</em>(<em>p</em><sub>0</sub>)) ile (<em>p</em><sub>1</sub>, "
    "<em>f</em>(<em>p</em><sub>1</sub>)) noktalarından geçen kiriş <em>x</em> eksenini "
    "<em>p</em><sub>2</sub> = 0,736384139'da keser. Büyütülmüş pencerede kesikli çizilen ikinci kiriş "
    "eğriyle neredeyse çakışır ve ekseni <em>p</em><sub>3</sub> = 0,739058139'da, "
    "<em>p</em> = 0,739085133 kökünün hemen yanında keser.",
    aria="Graph of y = cos x - x with the secant through (p0, f(p0)) and (p1, f(p1)) crossing the x axis "
         "at p2 = 0.7364; a zoom window shows p2, the dashed second secant and the root p = 0.7391"))

# ============================================================
# regula-falsi-kirisler: x^3 - 3 on [1, 2], the right end stays at 2
# ============================================================
def f_cube(x):
    return x ** 3 - 3


A, B = 1.0, 2.0
FB = f_cube(B)
lefts = [A]
for _ in range(3):
    a = lefts[-1]
    lefts.append(chord_root(a, f_cube(a), B, FB))
# lefts = [1, 1.285714286, 1.392059553, 1.426733629]
CUBE_ROOT = 3 ** (1 / 3)

p = Plot(60, 30, 420, 300, (0.9, 2.1), (-2.5, 5.5))
p.grid([1.0, 1.2, 1.4, 1.6, 1.8, 2.0], [-2, 2, 4])
p.axes([1.0, 1.2, 1.4, 1.6, 1.8, 2.0], [-2, 0, 2, 4], "", it("y"), dec, dec)
x_axis(p)
p.line(sample(f_cube, 0.9, 8.5 ** (1 / 3)), THEORY, 2.0)    # up to the top edge y = 5.5
p.label(1.72, 0.8, it("y") + " = " + it("x") + "³ " + MINUS + " 3", 0, 0, THEORY, 12.5)
# the right end x = 2 down to the interval strip
STRIP_TOP = p.y0 + p.h + 34
STEP = 15
# (interrupted at the tick label "2")
for ya, yb in ((p.Y(FB), p.y0 + p.h), (p.y0 + p.h + 22, STRIP_TOP + 3 * STEP + 4)):
    p.add(f'<line x1="{p.X(B):.1f}" y1="{ya:.1f}" x2="{p.X(B):.1f}" y2="{yb:.1f}" '
          f'stroke="{PRACTICE}" stroke-width="1" stroke-dasharray="3 3" opacity="0.6"/>')
SHADE = (0.45, 0.7, 1.0)
for k in range(3):
    a = lefts[k]
    p.line([(a, f_cube(a)), (B, FB)], PRACTICE, 1.7, None, SHADE[k])
for k in range(3):
    dot(p, (lefts[k], f_cube(lefts[k])), PRACTICE, 3.0)
dot(p, (B, FB), PRACTICE, 5.0)
p.label(B, FB, pn("1") + " = 2", -9, -6, PRACTICE, 12.5, "end", True)
p.label(A, f_cube(A), pn("0") + " = 1", 6, 16, TEXT, 12)
# axis crossings
for k in (1, 2, 3):
    dot(p, (lefts[k], 0), PRACTICE, 2.6)
hollow(p, (CUBE_ROOT, 0), TEXT, 3.6)
p.label(lefts[1], 0, pn("2"), -5, -7, TEXT, 12.5, "end")
# leaders to the lower right for the crowded crossings p3, p4 and p
for x0, (lx, ly), s in ((lefts[2], (1.535, -1.7), pn("3")),
                        (lefts[3], (1.575, -1.1), pn("4")),
                        (CUBE_ROOT, (1.615, -0.5), it("p"))):
    p.line([(x0 + 0.004, -0.06), (lx, ly)], TEXT, 0.8, None, 0.55)
    p.label(lx, ly, s, 3, 9, TEXT, 12.5)
# the bracketing intervals, one row per step
names = ["[1, 2]", "[" + pn("2") + ", 2]", "[" + pn("3") + ", 2]", "[" + pn("4") + ", 2]"]
for k in range(4):
    y = STRIP_TOP + k * STEP
    x0, x1 = p.X(lefts[k]), p.X(B)
    p.add(f'<rect x="{x0:.1f}" y="{y - 2.5:.1f}" width="{x1 - x0:.1f}" height="5" rx="2.5" '
          f'fill="{BASE}" opacity="{0.45 + 0.18 * k:.2f}"/>')
    p.text_px(x0 - 7, y + 4, names[k], TEXT, 11.5, "end")
save("regula-falsi-kirisler", figure(
    520, int(STRIP_TOP + 3 * STEP + 20), [p],
    "<em>y</em> = <em>x</em>³ &#8722; 3 için Regula Falsi metodunun ilk üç kirişi. Bütün kirişler sağ uçtaki "
    "(2, 5) noktasından çıkar ve <em>x</em> eksenini sırasıyla <em>p</em><sub>2</sub> = 1,285714286, "
    "<em>p</em><sub>3</sub> = 1,392059553, <em>p</em><sub>4</sub> = 1,426733629'da keser; "
    "kök <em>p</em> = 1,442249570'tir. Alttaki çubuklar kökü içeren aralıklardır: sol uç köke yaklaşırken "
    "sağ uç hep 2'de kalır.",
    aria="Graph of y = x^3 - 3 with three regula falsi chords from the fixed point (2, 5) crossing the x axis "
         "at p2 = 1.2857, p3 = 1.3921 and p4 = 1.4267 near the root 1.4422, and bars for the intervals "
         "[1, 2], [p2, 2], [p3, 2], [p4, 2] whose right end stays at 2"))

# ============================================================
# hata-karsilastirma: |p_n - p| on a log scale for the four methods
# ============================================================
# |p_n - p| with p = 0.7390851332151607, recomputed at 60 digits
SERIES = [
    ("Sabit Nokta", REMARK, "circle", None,
     [4.63e-2, 3.20e-2, 2.12e-2, 1.44e-2, 9.63e-3, 6.52e-3, 4.38e-3, 2.96e-3]),
    ("Newton-Raphson", THEORY, "square", None,
     [4.63e-2, 4.51e-4, 4.49e-8, 4.45e-16]),
    ("Secant", PRACTICE, "triangle", None,
     [2.39e-1, 4.63e-2, 2.70e-3, 2.70e-5, 1.61e-8, 9.61e-14]),
    ("Regula Falsi", BASE, "diamond", "6 4",
     [2.39e-1, 4.63e-2, 2.70e-3, 2.70e-5, 2.69e-7, 2.69e-9]),
]
# the next errors fall below the axis: (series, next value, label)
OFF_AXIS = {"Newton-Raphson": 4.37e-32, "Secant": 3.42e-22}


def marker(px, py, kind, color, r=4.2, filled=True):
    fill = color if filled else BG
    attrs = f'fill="{fill}" stroke="{color}" stroke-width="1.6"'
    if kind == "circle":
        return f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{r:.1f}" {attrs}/>'
    if kind == "square":
        s = r * 0.85
        return f'<rect x="{px - s:.1f}" y="{py - s:.1f}" width="{2 * s:.1f}" height="{2 * s:.1f}" {attrs}/>'
    if kind == "triangle":
        s = r * 1.15
        pts = [(px, py - s), (px + s * 0.95, py + s * 0.62), (px - s * 0.95, py + s * 0.62)]
    else:
        s = r * 1.35
        pts = [(px, py - s), (px + s, py), (px, py + s), (px - s, py)]
    return f'<polygon points="{" ".join(f"{a:.1f},{b:.1f}" for a, b in pts)}" {attrs}/>'


def pow10(k):
    return "1" if k == 0 else "10" + sup(MINUS + str(-k))


YMIN = -17.0
p = Plot(80, 30, 420, 340, (-0.4, 7.4), (YMIN, 0.4))
p.grid(range(8), range(-16, 1))
p.axes(range(8), range(-16, 1, 2), "", "|" + it("p") + sub(it("n")) + " " + MINUS + " " + it("p") + "|",
       lambda v: str(int(v)), lambda v: pow10(int(round(v))))
p.label(7.4, YMIN, it("n"), 16, 4, TEXT, 12.5)
for name, color, kind, dash, errs in SERIES:
    pts = [(n, math.log10(e)) for n, e in enumerate(errs)]
    p.line(pts, color, 1.8, dash, 0.9)
    if name in OFF_AXIS:
        n0, y0 = pts[-1]
        y1 = math.log10(OFF_AXIS[name])
        stop = YMIN + 0.35
        t = (stop - y0) / (y1 - y0)
        p.arrow((n0, y0), (n0 + t, stop), color, 1.4, 7.0, "3 2", 0.9)
    filled = name != "Regula Falsi"
    r = 5.4 if name == "Regula Falsi" else 4.0
    for x, y in pts:
        p.add(marker(p.X(x), p.Y(y), kind, color, r, filled))
# the values below the axis next to the arrow tips
p.label(3, YMIN + 0.35, "4,4 &#183; 10" + sup(MINUS + "32"), -8, -2, THEORY, 11, "end")
nx = 5 + (YMIN + 0.35 + 13.0173) / (math.log10(3.42e-22) + 13.0173)
p.label(nx, YMIN + 0.35, "3,4 &#183; 10" + sup(MINUS + "22"), 8, -2, PRACTICE, 11)
# legend, two columns under the axis
LX = (p.x0 + 20, p.x0 + 220)
LY = p.y0 + p.h + 40
for k, (name, color, kind, dash, _) in enumerate(SERIES):
    lx, ly = LX[k % 2], LY + 18 * (k // 2)
    da = f' stroke-dasharray="{dash}"' if dash else ""
    p.add(f'<line x1="{lx:.1f}" y1="{ly:.1f}" x2="{lx + 30:.1f}" y2="{ly:.1f}" stroke="{color}" '
          f'stroke-width="1.8"{da} opacity="0.9"/>')
    p.add(marker(lx + 15, ly, kind, color, 5.4 if name == "Regula Falsi" else 4.0, name != "Regula Falsi"))
    p.text_px(lx + 40, ly + 4, name, TEXT, 12)
save("hata-karsilastirma", figure(
    540, int(LY + 18 + 16), [p],
    "cos <em>x</em> &#8722; <em>x</em> = 0 denkleminde dört yöntemin |<em>p</em><sub><em>n</em></sub> &#8722; "
    "<em>p</em>| hataları, logaritmik dikey eksende (<em>p</em> = 0,7390851332). Sabit Nokta İterasyonunun "
    "hatası her adımda aynı oranda azalır ve noktalar bir doğru boyunca iner. Newton-Raphson ve Secant'ın "
    "eğrileri giderek dikleşir; aşağı oklar, eksenin altında kalan sonraki hataları gösterir. Secant ile "
    "Regula Falsi <em>n</em> = 3'e kadar çakışır, sonra Regula Falsi yavaşlar.",
    aria="Log scale plot of the errors |p_n - p| against n for fixed point iteration, Newton-Raphson, secant "
         "and regula falsi on cos x - x = 0; Newton and secant drop fastest, secant and regula falsi coincide "
         "up to n = 3"))
