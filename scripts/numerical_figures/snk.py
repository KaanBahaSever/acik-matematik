# -*- coding: utf-8 -*-
"""
Figures of the chapter "Sabit Nokta İterasyonu"
(dersler/numerik-analiz/sabit-nokta-iterasyonu.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box and never directly under a heading.
The figures are NOT produced at build time. Run

    python scripts/numerical_figures/snk.py
    python scripts/center_figures.py "numerical-snk-*.md"
    python scripts/check_figure_labels.py "scripts/_figures/numerical-snk-*.md"

and paste the markup of scripts/_figures/numerical-snk-<name>.md into the .qmd.
Captions are Turkish on purpose; aria labels are plain ASCII.
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, dot, hollow, TEXT, THEORY, PRACTICE, BASE, BG, WIDE  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "numerical-snk-"

MINUS = "&#8722;"


def save(name, markup):
    (OUT_DIR / f"{PREFIX}{name}.md").write_text(markup, encoding="utf-8", newline="\n")
    print(f"{PREFIX}{name}.md")


def it(s):
    """Italic run inside an SVG <text>."""
    return f'<tspan font-style="italic">{s}</tspan>'


def sup(s, size=8.5):
    """Superscript inside an SVG <text>."""
    return f'<tspan font-size="{size}" dy="-5">{s}</tspan><tspan dy="5">&#8203;</tspan>'


def sub(s, size=8.5):
    """Subscript inside an SVG <text>."""
    return f'<tspan font-size="{size}" dy="3">{s}</tspan><tspan dy="-3">&#8203;</tspan>'


def dec(v, digits=2):
    """Decimal comma and a true minus sign: -0.5 -> '−0,5'."""
    s = f"{v:.{digits}f}".rstrip("0").rstrip(".")
    return s.replace(".", ",").replace("-", MINUS)


def eq_plot(x0, y0, ppu, xr, yr):
    """Panel with the same number of pixels per unit on both axes."""
    return Plot(x0, y0, (xr[1] - xr[0]) * ppu, (yr[1] - yr[0]) * ppu, xr, yr)


def sample(f, a, b, n=240):
    return [(a + (b - a) * k / n, f(a + (b - a) * k / n)) for k in range(n + 1)]


def clip_y(pts, lo, hi):
    """Keep the samples of a graph whose ordinate lies in [lo, hi] (one run, the graph is monotone there)."""
    return [(x, y) for x, y in pts if lo <= y <= hi]


def frame(p):
    p.polygon([(p.xmin, p.ymin), (p.xmax, p.ymin), (p.xmax, p.ymax), (p.xmin, p.ymax)], TEXT, 0.0, TEXT, 0.8)


def ytick(p, v, s):
    p.add(f'<line x1="{p.x0 - 4:.1f}" y1="{p.Y(v):.1f}" x2="{p.x0:.1f}" y2="{p.Y(v):.1f}" stroke="{TEXT}" '
          f'opacity="0.6"/>')
    p.text_px(p.x0 - 7, p.Y(v) + 4, s, TEXT, 11, "end")


def xtick(p, v, s, color=TEXT, size=11):
    p.add(f'<line x1="{p.X(v):.1f}" y1="{p.y0 + p.h:.1f}" x2="{p.X(v):.1f}" y2="{p.y0 + p.h + 4:.1f}" '
          f'stroke="{TEXT}" opacity="0.6"/>')
    p.text_px(p.X(v), p.y0 + p.h + 17, s, color, size, "middle")


# ============================================================
# kesisim: y = x^2 - 2 meets y = x at (-1, -1) and (2, 2)
# ============================================================
p = eq_plot(40, 30, 62, (-2.5, 3.0), (-2.5, 4.0))
p.grid([-2, -1, 1, 2, 3], [-2, -1, 1, 2, 3, 4])
p.origin_axes(it("x"), it("y"), (-2, 1), (-2, -1, 1, 2, 3), dec, dec, opacity=0.5)
p.line([(-2.5, -2.5), (3.0, 3.0)], BASE, 2.0)
p.line(clip_y(sample(lambda x: x * x - 2, -2.5, 3.0, 400), -2.5, 4.0), THEORY, 2.4)
for x in (-1.0, 2.0):
    p.line([(x, x), (x, 0)], TEXT, 1.0, "4 3", 0.7)
    dot(p, (x, x), PRACTICE, 4.6)
p.label(-1, 0, it("p") + " = " + MINUS + "1", 0, -8, PRACTICE, 12, "middle", True)
p.label(2, 0, it("p") + " = 2", 0, 17, PRACTICE, 12, "middle", True)
p.label(2.36, 3.5696, it("y") + " = " + it("x") + "² " + MINUS + " 2", 10, 4, THEORY, 12.5, "start", True)
p.label(2.6, 2.6, it("y") + " = " + it("x"), 8, 16, BASE, 12.5, "start", True)
save("kesisim", figure(
    int(p.x0 + p.w + 30), int(p.y0 + p.h + 25), [p],
    "<em>y</em> = <em>x</em>² &#8722; 2 parabolü <em>y</em> = <em>x</em> doğrusunu (&#8722;1, &#8722;1) ve "
    "(2, 2) noktalarında keser. Bu noktaların apsisleri <em>g</em>(<em>x</em>) = <em>x</em>² &#8722; 2 "
    "fonksiyonunun sabit noktalarıdır.",
    aria="The parabola y = x^2 - 2 and the line y = x crossing at (-1, -1) and (2, 2); dashed drops mark "
         "the fixed points p = -1 and p = 2 on the x axis"))

# ============================================================
# sin-kare: g(x) = 1.4 sin x maps [1, pi/2] into itself
# ============================================================
HP = math.pi / 2
G1, G2 = 1.4 * math.sin(1.0), 1.4             # g(1) = 1.1781, g(pi/2) = 1.4
PFIX = 1.0
for _ in range(200):
    PFIX = 1.4 * math.sin(PFIX)
assert abs(G1 - 1.1781) < 5e-5 and abs(PFIX - 1.37259) < 5e-6
R = (0.95, 1.62)
p = eq_plot(80, 30, 520, R, R)
p.add(f'<g stroke="{TEXT}" stroke-width="1.1" opacity="0.5">'
      f'<line x1="{p.x0:.1f}" y1="{p.y0 + p.h:.1f}" x2="{p.x0 + p.w + 8:.1f}" y2="{p.y0 + p.h:.1f}"/>'
      f'<line x1="{p.x0:.1f}" y1="{p.y0 - 8:.1f}" x2="{p.x0:.1f}" y2="{p.y0 + p.h:.1f}"/></g>')
p.text_px(p.x0 + p.w + 14, p.y0 + p.h + 4, it("x"), TEXT, 12.5)
p.text_px(p.x0, p.y0 - 14, it("y"), TEXT, 12.5, "middle")
SQ = [(1.0, 1.0), (HP, 1.0), (HP, HP), (1.0, HP)]
p.polygon(SQ, THEORY, 0.06, THEORY, 1.2, "6 4")
# the range g([1, pi/2]) as a band on the y axis, with guides from the end points
for v in (G1, G2):
    p.line([(R[0], v), (HP if v == G2 else 1.0, v)], TEXT, 0.9, "3 3", 0.55)
p.add(f'<line x1="{p.x0:.1f}" y1="{p.Y(G1):.1f}" x2="{p.x0:.1f}" y2="{p.Y(G2):.1f}" stroke="{PRACTICE}" '
      f'stroke-width="6" opacity="0.75" stroke-linecap="butt"/>')
p.line([(R[0], R[0]), (R[1], R[1])], BASE, 1.8)
p.line(sample(lambda x: 1.4 * math.sin(x), 1.0, HP), PRACTICE, 2.6)
for pt in ((1.0, G1), (HP, G2)):
    dot(p, pt, PRACTICE, 4.2)
dot(p, (PFIX, PFIX), TEXT, 4.8)
p.line([(PFIX, PFIX), (PFIX, R[0])], TEXT, 0.9, "3 3", 0.5)
for v, s in ((1.0, "1"), (G1, "1,1781"), (G2, "1,4"), (HP, "π/2")):
    ytick(p, v, s)
for v, s in ((1.0, "1"), (PFIX, it("p") + " &#8776; 1,37259"), (HP, "π/2")):
    xtick(p, v, s)
p.label(R[0], (G1 + G2) / 2, it("g") + "([1, π/2])", 12, 4, PRACTICE, 12, "start", True)
# below the curve, right of the diagonal
p.label(1.565, 1.335, it("y") + " = 1,4 sin " + it("x"), 0, 0, PRACTICE, 12.5, "end", True)
p.label(1.6, 1.6, it("y") + " = " + it("x"), -10, -4, BASE, 12.5, "end", True)
save("sin-kare", figure(
    int(p.x0 + p.w + 40), int(p.y0 + p.h + 30), [p],
    "<em>g</em>(<em>x</em>) = 1,4 sin <em>x</em> fonksiyonu [1, π/2] aralığında artandır ve değerleri "
    "[1,1781; 1,4] aralığında kalır; bu aralık kesikli karenin içindedir. Eğri <em>y</em> = <em>x</em> "
    "doğrusunu karenin içinde tek bir <em>p</em> &#8776; 1,37259 noktasında keser.",
    aria="The curve y = 1.4 sin x over 1 to pi/2 inside the dashed square [1, pi/2] x [1, pi/2]; its range "
         "1.1781 to 1.4 is marked on the y axis and it meets the line y = x at p = 1.37259"))

# ============================================================
# orumcek-agi: cobweb diagrams, convergent and divergent
# ============================================================
# left: g(x) = 0.3 e^(-x), p_0 = 0.2, iterates rounded to five decimals as in the table of the text
SEQ = [0.2]
for _ in range(5):
    SEQ.append(round(0.3 * math.exp(-SEQ[-1]), 5))
assert SEQ == [0.2, 0.24562, 0.23467, 0.23725, 0.23664, 0.23678]
QFIX = 0.2
for _ in range(200):
    QFIX = 0.3 * math.exp(-QFIX)
assert abs(QFIX - 0.23676) < 5e-6
L = (0.19, 0.26)
PW = 232
p1 = eq_plot(56, 60, PW / (L[1] - L[0]), L, L)
# right: g(x) = x^2 - 2, p_0 = 2.1
RQ = [2.1, 2.41, 3.8081]
assert abs(RQ[0] ** 2 - 2 - RQ[1]) < 1e-12 and abs(RQ[1] ** 2 - 2 - RQ[2]) < 1e-12
P3 = RQ[2] ** 2 - 2                       # 12.50162561
Rr = (1.8, 4.2)
p2 = eq_plot(56 + PW + 92, 60, PW / (Rr[1] - Rr[0]), Rr, Rr)


def panel(p, title, xlab_y=True):
    frame(p)
    p.text_px(p.x0 + p.w / 2, p.y0 - 30, title, TEXT, 12.5, "middle", True)
    p.text_px(p.x0 + p.w + 8, p.y0 + p.h + 4, it("x"), TEXT, 12.5)
    p.text_px(p.x0, p.y0 - 9, it("y"), TEXT, 12.5, "middle")


def cobweb(p, seq, start_y, color=PRACTICE, arrows=3):
    """Vertical to the curve, horizontal to the diagonal; returns the list of drawn corners."""
    pts = [(seq[0], start_y)]
    for a, b in zip(seq, seq[1:]):
        pts += [(a, b), (b, b)]
    for k, (u, v) in enumerate(zip(pts, pts[1:])):
        if k < arrows:
            p.arrow(u, v, color, 1.5, 7.0)
        else:
            p.line([u, v], color, 1.5)
    return pts


# left panel
panel(p1, "Yakınsak: |" + it("g") + "′(" + it("p") + ")| &#8776; 0,24 &lt; 1")
p1.grid([0.20, 0.22, 0.24], [0.20, 0.22, 0.24])
for v in (0.20, 0.22, 0.24, 0.26):
    ytick(p1, v, f"{v:.2f}".replace(".", ","))
p1.line([(L[0], L[0]), (L[1], L[1])], BASE, 1.8)
p1.line(sample(lambda x: 0.3 * math.exp(-x), L[0], L[1]), THEORY, 2.4)
for a in SEQ[1:3]:
    p1.line([(a, a), (a, L[0])], TEXT, 0.9, "3 3", 0.5)
cobweb(p1, SEQ, L[0])
dot(p1, (QFIX, QFIX), TEXT, 4.2)
for k, a in enumerate(SEQ[:3]):
    xtick(p1, a, it("p") + sub(str(k)), PRACTICE, 12)
# fixed point label in the free lower right corner, with a leader
p1.line([(QFIX + 0.0012, QFIX - 0.0012), (0.2475, 0.2215)], TEXT, 0.9, None, 0.7)
p1.label(0.2475, 0.2215, it("p") + " &#8776; 0,23676", -14, 14, TEXT, 12, "start")
p1.label(0.192, 0.3 * math.exp(-0.192), it("y") + " = 0,3" + it("e") + sup(MINUS + it("x")), 4, -10, THEORY,
         12.5, "start", True)
p1.label(0.2535, 0.2535, it("y") + " = " + it("x"), -8, 0, BASE, 12.5, "end", True)

# right panel
panel(p2, "Iraksak: |" + it("g") + "′(2)| = 4 &gt; 1")
p2.grid([2, 3, 4], [2, 3, 4])
for v in (2, 3, 4):
    ytick(p2, v, dec(v))
p2.line([(Rr[0], Rr[0]), (Rr[1], Rr[1])], BASE, 1.8)
p2.line(clip_y(sample(lambda x: x * x - 2, Rr[0], Rr[1], 600), Rr[0], Rr[1]), THEORY, 2.4)
for a in RQ[1:]:
    p2.line([(a, a), (a, Rr[0])], TEXT, 0.9, "3 3", 0.5)
cobweb(p2, RQ, Rr[0], arrows=4)
# p_3 = 12.5 is far above the frame: the last vertical leaves through the top edge
p2.line([(RQ[2], RQ[2]), (RQ[2], Rr[1] - 0.06)], PRACTICE, 1.5)
p2.arrow((RQ[2], Rr[1] - 0.1), (RQ[2], Rr[1] + 0.12), PRACTICE, 1.5, 7.0)
# above the frame, left of the arrowhead
p2.label(RQ[2], Rr[1], it("p") + sub("3") + " &#8776; 12,5", -8, -4, PRACTICE, 12, "end", True)
dot(p2, (2.0, 2.0), TEXT, 4.2)
# left of the steep parabola, joined to the point by a leader
p2.line([(1.985, 2.04), (1.9, 2.6)], TEXT, 0.9, None, 0.7)
p2.label(1.82, 2.68, it("p") + " = 2", 0, 0, TEXT, 12, "start")
for k, a in enumerate(RQ):
    xtick(p2, a, it("p") + sub(str(k)), PRACTICE, 12)
p2.label(2.46, 4.0, it("y") + " = " + it("x") + "² " + MINUS + " 2", 8, 4, THEORY, 12.5, "start", True)
p2.label(3.2, 3.2, it("y") + " = " + it("x"), 8, 16, BASE, 12.5, "start", True)
save("orumcek-agi", figure(
    int(p2.x0 + p2.w + 30), int(p1.y0 + p1.h + 30), [p1, p2],
    "Örümcek ağı diyagramları. Solda <em>g</em>(<em>x</em>) = 0,3<em>e</em><sup>&#8722;<em>x</em></sup> ve "
    "<em>p</em><sub>0</sub> = 0,2: eğriye dikey, <em>y</em> = <em>x</em> doğrusuna yatay adımlar kökün iki "
    "yanında dolanarak <em>p</em> &#8776; 0,23676 noktasına daralır. Sağda <em>g</em>(<em>x</em>) = "
    "<em>x</em>² &#8722; 2 ve <em>p</em><sub>0</sub> = 2,1: adımlar 2,41 ve 3,8081 üzerinden "
    "<em>p</em> = 2 kökünden uzaklaşır, <em>p</em><sub>3</sub> &#8776; 12,5 çerçevenin dışındadır.",
    css_class=WIDE,
    aria="Two cobweb diagrams. Left: g(x) = 0.3 exp(-x) from p0 = 0.2, a square spiral closing in on the "
         "fixed point 0.23676. Right: g(x) = x^2 - 2 from p0 = 2.1, a staircase moving away from the fixed "
         "point 2 through 2.41 and 3.8081 and leaving the frame toward p3 = 12.5"))


def axes_from_origin(p, xmax, ymax):
    """Plain x and y axes through the data origin with arrowheads and italic names."""
    ox, oy = p.X(0), p.Y(0)
    xe, ye = p.X(xmax), p.Y(ymax)
    p.add(f'<g stroke="{TEXT}" stroke-width="1.1" opacity="0.6" fill="{TEXT}">'
          f'<line x1="{ox - 4:.1f}" y1="{oy:.1f}" x2="{xe:.1f}" y2="{oy:.1f}"/>'
          f'<line x1="{ox:.1f}" y1="{oy + 4:.1f}" x2="{ox:.1f}" y2="{ye:.1f}"/>'
          f'<polygon points="{xe:.1f},{oy:.1f} {xe - 8:.1f},{oy - 3.5:.1f} {xe - 8:.1f},{oy + 3.5:.1f}" stroke="none"/>'
          f'<polygon points="{ox:.1f},{ye:.1f} {ox - 3.5:.1f},{ye + 8:.1f} {ox + 3.5:.1f},{ye + 8:.1f}" stroke="none"/>'
          f'</g>')
    p.text_px(xe - 2, oy + 17, it("x"), TEXT, 12.5, "end")
    p.text_px(ox + 9, ye + 6, it("y"), TEXT, 12.5)


def tick_x(p, v, s, color=TEXT, size=12, bold=False):
    p.add(f'<line x1="{p.X(v):.1f}" y1="{p.Y(0) - 3:.1f}" x2="{p.X(v):.1f}" y2="{p.Y(0) + 3:.1f}" '
          f'stroke="{TEXT}" opacity="0.7"/>')
    p.label(v, 0, s, 0, 18, color, size, "middle", bold)


def tick_y(p, v, s, color=TEXT, size=12, bold=False):
    p.add(f'<line x1="{p.X(0) - 3:.1f}" y1="{p.Y(v):.1f}" x2="{p.X(0) + 3:.1f}" y2="{p.Y(v):.1f}" '
          f'stroke="{TEXT}" opacity="0.7"/>')
    p.label(0, v, s, -8, 4, color, size, "end", bold)


# ============================================================
# varlik: g maps [a, b] into itself, so its graph stays in the square and meets y = x
# ============================================================
def g_gen(x):
    """A generic continuous g on [a, b] = [1, 4] with values in [1.72, 3.10] and |g'| < 1."""
    t = (x - 1) / 3
    return 1 + 3 * (0.52 + 0.2 * math.sin(4.2 * t + 0.4) - 0.08 * t)


GA, GB = 1.0, 4.0
lo, hi = GA, GB
for _ in range(80):
    m = (lo + hi) / 2
    lo, hi = (m, hi) if g_gen(m) > m else (lo, m)
PG = lo                                    # about 2.6657
assert GA < g_gen(GA) and g_gen(GB) < GB
assert all(GA <= g_gen(GA + 3 * k / 600) <= GB for k in range(601))
W0 = (-0.25, 4.75)
p = eq_plot(50, 30, 80, W0, W0)
axes_from_origin(p, 4.75, 4.75)
for v in (GA, GB):
    p.line([(v, 0), (v, GA)], TEXT, 0.9, "3 3", 0.5)
    p.line([(0, v), (GA, v)], TEXT, 0.9, "3 3", 0.5)
p.polygon([(GA, GA), (GB, GA), (GB, GB), (GA, GB)], THEORY, 0.06, TEXT, 1.2, "6 4")
p.line([(0, 0), (4.6, 4.6)], BASE, 1.9)
p.line(sample(g_gen, GA, GB), THEORY, 2.6)
for x in (GA, GB):
    dot(p, (x, g_gen(x)), THEORY, 4.0)
p.line([(PG, PG), (PG, 0)], TEXT, 1.0, "3 3", 0.7)
dot(p, (PG, PG), PRACTICE, 4.8)
for v, s in ((GA, it("a")), (GB, it("b"))):
    tick_x(p, v, s)
    tick_y(p, v, s)
tick_x(p, PG, it("p"), PRACTICE, 12.5, True)
p.label(4.6, 4.6, it("y") + " = " + it("x"), -4, -9, BASE, 12.5, "end", True)
p.label(GB, g_gen(GB), it("y") + " = " + it("g") + "(" + it("x") + ")", -8, 22, THEORY, 12.5, "end", True)
save("varlik", figure(
    int(p.x0 + p.w + 30), int(p.y0 + p.h + 30), [p],
    "<em>g</em>, [<em>a</em>, <em>b</em>] aralığını kendi içine gönderdiğinden grafiği kesikli karenin "
    "içinde kalır. Grafik karenin sol kenarında <em>y</em> = <em>x</em> doğrusunun üstünde, sağ kenarında "
    "altındadır; bu yüzden doğruyu bir (<em>p</em>, <em>p</em>) noktasında keser ve <em>p</em> bir sabit "
    "noktadır.",
    aria="The dashed square [a, b] x [a, b], the diagonal y = x and a continuous curve y = g(x) that stays "
         "inside the square, starting above the diagonal at x = a and ending below it at x = b, so that it "
         "meets the diagonal at the fixed point (p, p)"))


# ============================================================
# iterasyon: the cobweb p_{n+1} = g(p_n) for a decreasing g, generic labels
# ============================================================
def g_dec(x):
    """A generic decreasing g; only the shape matters."""
    return 3.2 * math.exp(-0.35 * x)


IT = [3.4]
for _ in range(4):
    IT.append(g_dec(IT[-1]))
PD = 1.0
for _ in range(300):
    PD = g_dec(PD)
assert IT[1] < IT[3] < PD < IT[2] < IT[0]
p = eq_plot(120, 30, 96, (-0.15, 4.25), (-0.15, 2.8))
axes_from_origin(p, 4.25, 2.8)
p.line([(0, 0), (2.7, 2.7)], BASE, 1.9)
p.line(sample(g_dec, 0.72, 4.0), THEORY, 2.6)
hollow(p, (PD, PD), TEXT, 4.2, 1.6)
# guides: drops from the diagonal to the x axis, and from the y axis to where each horizontal step starts
for v in IT[1:4]:
    p.line([(v, v), (v, 0)], TEXT, 0.9, "3 3", 0.55)
p.line([(0, IT[1]), (IT[1], IT[1])], TEXT, 0.9, "3 3", 0.55)
p.line([(0, IT[2]), (IT[1], IT[2])], TEXT, 0.9, "3 3", 0.55)
p.line([(0, IT[3]), (IT[3], IT[3])], TEXT, 0.9, "3 3", 0.55)
# the staircase: up to the graph, across to the diagonal, ...
path = [(IT[0], 0)]
for a, b in zip(IT[:3], IT[1:4]):
    path += [(a, b), (b, b)]
for u, v in zip(path, path[1:]):
    # stop short of the corner dot so the arrowhead stays visible
    d = math.hypot(v[0] - u[0], v[1] - u[1])
    cut = 5.5 / p.R(1)
    p.arrow(u, (v[0] - (v[0] - u[0]) * cut / d, v[1] - (v[1] - u[1]) * cut / d), PRACTICE, 1.6, 7.5)
for pt in path[1:]:
    dot(p, pt, PRACTICE if abs(pt[0] - pt[1]) > 1e-9 else TEXT, 3.6)
for k, v in enumerate(IT[:4]):
    tick_x(p, v, it("p") + sub(str(k)), PRACTICE, 12.5, True)
for k in (1, 2, 3):
    tick_y(p, IT[k], it("p") + sub(str(k)) + " = " + it("g") + "(" + it("p") + sub(str(k - 1)) + ")", TEXT, 12)
# point labels
pair = lambda i, j: "(" + it("p") + sub(str(i)) + ", " + it("p") + sub(str(j)) + ")"
p.label(IT[0], IT[1], pair(0, 1), 7, -9, TEXT, 11.5, "start")
p.label(IT[1], IT[1], pair(1, 1), -7, -8, TEXT, 11.5, "end")
p.label(IT[1], IT[2], pair(1, 2), 7, -9, TEXT, 11.5, "start")
p.label(IT[2], IT[2], pair(2, 2), 9, 4, TEXT, 11.5, "start")
p.label(2.7, 2.7, it("y") + " = " + it("x"), -4, -9, BASE, 12.5, "end", True)
p.label(4.0, g_dec(4.0), it("y") + " = " + it("g") + "(" + it("x") + ")", 0, 20, THEORY, 12.5, "end", True)
save("iterasyon", figure(
    int(p.x0 + p.w + 30), int(p.y0 + p.h + 30), [p],
    "Sabit nokta iterasyonunun geometrik yorumu. <em>p</em><sub>0</sub>'dan dikey olarak "
    "<em>y</em> = <em>g</em>(<em>x</em>) grafiğine çıkılır ve <em>p</em><sub>1</sub> = "
    "<em>g</em>(<em>p</em><sub>0</sub>) okunur. Yatay olarak <em>y</em> = <em>x</em> doğrusuna gidilince "
    "<em>p</em><sub>1</sub> yatay eksene taşınır ve adım tekrarlanır. Azalan <em>g</em> için terimler "
    "sabit noktanın (içi boş nokta) iki yanında dolanarak ona yaklaşır.",
    aria="Cobweb diagram of p_(n+1) = g(p_n) for a decreasing g: from p0 up to the curve at (p0, p1), across "
         "to the diagonal at (p1, p1), up to (p1, p2), across to (p2, p2), down to (p2, p3) and across to "
         "(p3, p3); p0 to p3 on the x axis and p1 = g(p0), p2 = g(p1), p3 = g(p2) on the y axis"))
