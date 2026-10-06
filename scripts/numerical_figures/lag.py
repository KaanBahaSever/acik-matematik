# -*- coding: utf-8 -*-
"""
Figures of the chapter "Lagrange İnterpolasyonu"
(dersler/numerik-analiz/lagrange-interpolasyonu.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box and never directly under a heading.
The figures are NOT produced at build time. Run

    python scripts/numerical_figures/lag.py
    python scripts/center_figures.py "numerical-lag-*.md"
    python scripts/check_figure_labels.py "scripts/_figures/numerical-lag-*.md"

and paste the markup of scripts/_figures/numerical-lag-<name>.md into the .qmd.
Captions are Turkish on purpose; aria labels are plain ASCII.

The 3-D figure shows one vertical ribbon per n: the curve z(x, n) over [0, 1]
with a translucent curtain down to the floor. The curtain is cut into bands of
z and each band gets a stronger fill the higher it reaches, so the colour
follows z. Ribbons are painted back to front (the camera looks from the side
of large n), so nearer curtains softly veil the curves behind them.
"""
import html
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, dot, TEXT, THEORY, PRACTICE, BASE, REMARK, BG  # noqa: E402
from svg_plot3 import Camera, Space  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "numerical-lag-"

MINUS = "&#8722;"
APPROX = "&#8776;"
PI = "&#960;"


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
    return f'<tspan font-size="{size}" dy="3.5">{s}</tspan><tspan dy="-3.5">&#8203;</tspan>'


def dec(v, digits=2):
    """Decimal comma and a true minus sign: -0.5 -> '−0,5'."""
    s = f"{v:.{digits}f}".rstrip("0").rstrip(".")
    return s.replace(".", ",").replace("-", MINUS)


def text_w(s, size):
    """Rough advance width of a label (0.56 em per visible character)."""
    plain = html.unescape(re.sub(r"<[^>]+>", "", s)).replace("​", "")
    return len(plain) * 0.56 * size


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


def sample(f, a, b, n=240):
    return [(a + (b - a) * k / n, f(a + (b - a) * k / n)) for k in range(n + 1)]


def argmax(f, a, b, iters=200):
    """Maximiser of a unimodal function on [a, b] (golden-section search)."""
    g = (math.sqrt(5) - 1) / 2
    c, d = b - g * (b - a), a + g * (b - a)
    for _ in range(iters):
        if f(c) > f(d):
            b = d
        else:
            a = c
        c, d = b - g * (b - a), a + g * (b - a)
    return (a + b) / 2


# ============================================================
# taylor-ustel: e^x and its Taylor polynomials P_0 ... P_3 about x_0 = 0
# ============================================================
def taylor(k):
    return lambda x: sum(x ** j / math.factorial(j) for j in range(k + 1))


p = Plot(60, 30, 380, 300, (-2, 2), (-1, 7.5))
p.grid([-1, 0, 1], [0, 2, 4, 6])
p.axes((-2, -1, 0, 1, 2), (0, 2, 4, 6), it("x"), it("y"), dec, dec)
for pts in (((-2, 0), (2, 0)), ((0, -1), (0, 7.5))):
    p.line(pts, TEXT, 1.0, None, 0.4)
COLORS = (REMARK, BASE, PRACTICE, THEORY)
for k in range(4):
    p.line(sample(taylor(k), -2, 2), COLORS[k], 1.7)
p.line(sample(math.exp, -2, 2), TEXT, 3.0)
E2, P32 = math.exp(2), taylor(3)(2)
# the error at x = 2, between P_3(2) and e^2
p.line([(2, P32), (2, E2)], TEXT, 1.4, "4 3", 0.9)
for yv in (P32, E2):
    p.add(f'<line x1="{p.X(2) - 4:.1f}" y1="{p.Y(yv):.1f}" x2="{p.X(2) + 4:.1f}" y2="{p.Y(yv):.1f}" '
          f'stroke="{TEXT}" stroke-width="1.2" opacity="0.9"/>')
# right-hand column of labels at x = 2
p.label(2, E2, it("e") + sup(it("x")), 9, 5, TEXT, 12.5, bold=True)
p.label(2, (E2 + P32) / 2, "hata " + APPROX + " " + dec(E2 - P32, 3), 9, 4, TEXT, 11.5)
for k in range(4):
    p.label(2, taylor(k)(2), it("P") + sub(str(k)), 9, 5, COLORS[k], 12.5, bold=True)
dot(p, (0, 1), TEXT, 4.2)
plabel(p, 0, 1, it("x") + sub("0") + " = 0", 7, 18, TEXT, 11.5)
save("taylor-ustel", figure(
    500, 370, [p],
    "<em>e</em><sup><em>x</em></sup> (kalın) ve <em>x</em><sub>0</sub> = 0 civarındaki "
    "<em>P</em><sub>0</sub>, <em>P</em><sub>1</sub>, <em>P</em><sub>2</sub>, <em>P</em><sub>3</sub> Taylor "
    "polinomları. Eğriler (0, 1) noktasında birbirine değer ve 0 civarında üst üste biner, uçlara doğru "
    "açılarak ayrılır. <em>x</em> = 2'de <em>e</em><sup>2</sup> &#8776; 7,389 ile "
    "<em>P</em><sub>3</sub>(2) &#8776; 6,333 arasındaki fark yaklaşık 1,056'dır.",
    aria="The exponential function together with its Taylor polynomials P0 to P3 about x0 = 0 on the "
         "interval from -2 to 2; all curves touch at (0, 1) and spread apart toward the ends, with the "
         "error of about 1.056 between e^2 and P3(2) marked at x = 2"))

# ============================================================
# katsayi-polinomlari: L_0, L_1, L_2 for the nodes 2, 2.75, 4
# ============================================================
NODES = (2.0, 2.75, 4.0)


def L0(x):
    return 2 / 3 * (x - 2.75) * (x - 4)


def L1(x):
    return -16 / 15 * (x - 2) * (x - 4)


def L2(x):
    return 2 / 5 * (x - 2) * (x - 2.75)


p = Plot(60, 30, 400, 300, (1.8, 4.2), (-0.6, 1.4))
p.axes((), (-0.5, 0, 0.5, 1), "", it("y"), yfmt=dec)
for yv in (0, 1):
    p.line([(1.8, yv), (4.2, yv)], TEXT, 0.9, None, 0.35)
for k, xv in enumerate(NODES):
    p.vline(xv, -0.6, 1.4, TEXT, "4 3", 0.45)
    p.label(xv, -0.6, it("x") + sub(str(k)) + " = " + dec(xv), 0, 18, TEXT, 11.5, "middle")
LS = ((L0, THEORY), (L1, PRACTICE), (L2, BASE))
for f, c in LS:
    p.line(sample(f, 1.8, 4.2), c, 2.2)
# node values: two curves vanish at every node, drawn as a ring with a dot inside
for k, xv in enumerate(NODES):
    zeros = [c for j, (f, c) in enumerate(LS) if j != k]
    dot(p, (xv, 1), LS[k][1], 4.4)
    dot(p, (xv, 0), zeros[0], 5.0)
    dot(p, (xv, 0), BG, 3.0)
    dot(p, (xv, 0), zeros[1], 2.2)
plabel(p, 2.17, L0(2.17), it("L") + sub("0"), 9, 0, THEORY, 13, bold=True)
plabel(p, 3.0, L1(3.0), it("L") + sub("1"), 0, -10, PRACTICE, 13, "middle", bold=True)
plabel(p, 3.83, L2(3.83), it("L") + sub("2"), -9, 0, BASE, 13, "end", bold=True)
save("katsayi-polinomlari", figure(
    500, 380, [p],
    "<em>x</em><sub>0</sub> = 2, <em>x</em><sub>1</sub> = 2,75, <em>x</em><sub>2</sub> = 4 düğümleri için "
    "<em>L</em><sub>0</sub>, <em>L</em><sub>1</sub>, <em>L</em><sub>2</sub> Lagrange katsayı polinomları. "
    "Her <em>L</em><sub><em>k</em></sub> kendi düğümünde 1, öteki iki düğümde 0 değerini alır.",
    aria="The three Lagrange basis polynomials L0, L1, L2 for the nodes 2, 2.75 and 4; each equals 1 at "
         "its own node and 0 at the other two nodes"))

# ============================================================
# sinus-hata: the true error |sin(pi x / 2) - x| against the bound (pi^3/48)|x^3 - x|
# ============================================================
def err(x):
    return abs(math.sin(math.pi * x / 2) - x)


def bound(x):
    return math.pi ** 3 / 48 * abs(x ** 3 - x)


p = Plot(60, 34, 420, 300, (-1, 1), (0, 0.27))
p.grid([-0.5, 0.5], [0.05, 0.1, 0.15, 0.2, 0.25])
p.axes((-1, -0.5, 0, 0.5, 1), (0, 0.05, 0.1, 0.15, 0.2, 0.25), it("x"), "", dec, dec)
BMAX = math.pi ** 3 * math.sqrt(3) / 216
p.line([(-1, BMAX), (1, BMAX)], TEXT, 1.0, None, 0.55)
p.line(sample(bound, -1, 1, 400), PRACTICE, 2.0, "7 4")
p.line(sample(err, -1, 1, 400), THEORY, 3.0)
p.text_px(p.x0 + p.w / 2, p.Y(BMAX) - 8,
          PI + sup("3") + "&#8730;3/216 " + APPROX + " " + dec(BMAX, 5), TEXT, 11.5, "middle")
XB = 1 / math.sqrt(3)
XE = argmax(err, 0.2, 0.9)
for s in (-1, 1):
    dot(p, (s * XB, BMAX), PRACTICE, 3.8)
    dot(p, (s * XE, err(XE)), THEORY, 3.8)
# value labels: inside the humps, on dotted leaders from the maxima
LEAD = 0.058
p.line([(XB, BMAX - 0.004), (XB, LEAD + 0.012)], PRACTICE, 1.0, "2 3", 0.9)
p.label(XB, LEAD, it("x") + " = 1/&#8730;3 " + APPROX + " " + dec(XB, 5), 0, 0, PRACTICE, 11.5, "middle")
p.label(-XE, err(XE), dec(err(XE), 5), 0, 22, THEORY, 11.5, "middle")
p.line([(-XE, err(XE) - 0.03), (-XE, LEAD + 0.012)], THEORY, 1.0, "2 3", 0.9)
p.label(-XE, LEAD, it("x") + " " + APPROX + " " + MINUS + dec(XE, 5), 0, 0, THEORY, 11.5, "middle")
for k, xv in enumerate((-1, 0, 1)):
    dot(p, (xv, 0), TEXT, 4.2)
    p.label(xv, 0, it("x") + sub(str(k)) + " = " + dec(xv), 0, 34, TEXT, 11.5, "middle")
# legend in the free wedge between the humps
LX, LY = p.X(0) - 52, p.Y(0.222)
p.add(f'<line x1="{LX:.1f}" y1="{LY:.1f}" x2="{LX + 26:.1f}" y2="{LY:.1f}" stroke="{THEORY}" stroke-width="3"/>')
p.text_px(LX + 32, LY + 4, "gerçek hata", THEORY, 11.5)
p.add(f'<line x1="{LX:.1f}" y1="{LY + 18:.1f}" x2="{LX + 26:.1f}" y2="{LY + 18:.1f}" stroke="{PRACTICE}" '
      f'stroke-width="2" stroke-dasharray="7 4"/>')
p.text_px(LX + 32, LY + 22, "hata sınırı", PRACTICE, 11.5)
save("sinus-hata", figure(
    540, 400, [p],
    "Kalın eğri gerçek hata |sin(&#960;<em>x</em>/2) &#8722; <em>x</em>|, kesikli eğri teoremden gelen "
    "(&#960;<sup>3</sup>/48)|<em>x</em><sup>3</sup> &#8722; <em>x</em>| sınırıdır. Sınırın tepeleri "
    "<em>x</em> = &#177;1/&#8730;3 noktalarında &#960;<sup>3</sup>&#8730;3/216 &#8776; 0,24863, gerçek "
    "hatanın tepeleri <em>x</em> &#8776; &#177;0,56066 noktalarında 0,21051'dir. Üç düğümde ikisi de "
    "sıfırdır ve sınır her yerde gerçek hatanın üstünde kalır.",
    aria="The true error of the approximation of sin(pi x / 2) by x on the interval from -1 to 1 together "
         "with the bound (pi^3/48)|x^3 - x|; the bound peaks at 0.24863 for x = 1/sqrt(3), the true error "
         "peaks at 0.21051 near x = 0.56066, and both vanish at the nodes -1, 0, 1"))

# ============================================================
# carpim-yuzeyi: z(x, n) = |prod (x - i/n)| / (h^(n+1) n!/4) on [0, 1], n = 1..10
# ============================================================
NMAX = 10
LXW, SY, HZ = 1.7, 0.16, 1.0          # world length of [0, 1], spacing of the ribbons, height of z = 1


def ratio(x, n):
    h = 1 / n
    prod = 1.0
    for i in range(n + 1):
        prod *= x - i * h
    return abs(prod) / (h ** (n + 1) * math.factorial(n) / 4)


def W(x, n, z):
    """(x, n, z) -> world point; n grows toward the viewer."""
    return (LXW * x, -SY * n, HZ * z)


cam = Camera(azimuth=-64.0, elevation=24.0)
N0, N1 = 0.4, NMAX + 0.6
box = [W(x, n, z) for x in (0, 1.18) for n in (N0, N1 + 1.3) for z in (0, 1.2)]
q = [cam.project(P)[:2] for P in box]
PPU = 210
xr = (min(a for a, _ in q) - 0.1, max(a for a, _ in q) + 0.1)
yr = (min(b for _, b in q) - 0.1, max(b for _, b in q) + 0.1)
pl = Plot(70, 30, (xr[1] - xr[0]) * PPU, (yr[1] - yr[0]) * PPU, xr, yr)
S = Space(pl, cam)

# floor frame and the plane z = 1 (painted first: everything else must stay crisp)
floor = [W(0, N0, 0), W(1, N0, 0), W(1, N1, 0), W(0, N1, 0)]
S.polygon(floor, TEXT, 0.03, TEXT, 0.8)
roof = [W(0, N0, 1), W(1, N0, 1), W(1, N1, 1), W(0, N1, 1)]
S.polygon(roof, BASE, 0.08, BASE, 1.1, "6 4")
for c in (roof[0], roof[1], roof[2], roof[3]):
    S.guide([c, (c[0], c[1], 0.0)], TEXT, 0.22, 0.8, "3 3")

# the z axis on the back left corner
ZA0 = W(0, N0, 0)
S.arrow(ZA0, W(0, N0, 1.2), TEXT, 1.1, 7.0, None, 0.6)
for zv in (0.5, 1.0):
    P = W(0, N0, zv)
    S.line([P, (P[0] - 0.05, P[1], P[2])], TEXT, 1.0, None, 0.7)
    S.label(P, dec(zv), -9, 4, TEXT, 10.5, "end")
S.label(W(0, N0, 1.2), "oran", 0, -8, TEXT, 12, "middle", italic=True)

# the x axis along the front edge
XA = W(0, N1 + 1.3, 0)
S.arrow(XA, W(1.18, N1 + 1.3, 0), TEXT, 1.1, 7.0, None, 0.6)
for xv in (0, 0.5, 1):
    P = W(xv, N1 + 1.3, 0)
    S.line([P, (P[0], P[1] - 0.05, P[2])], TEXT, 1.0, None, 0.7)
    S.label(P, dec(xv), 0, 15, TEXT, 10.5, "middle")
S.label(W(1.18, N1 + 1.3, 0), it("x"), 8, 12, TEXT, 12.5, "middle")

# colour by height: the curtain is filled once, then every level t adds a layer over
# the part of the curtain above height t, so the fill darkens as z grows
LAYERS = ((0.0, 0.07), (0.15, 0.07), (0.3, 0.08), (0.45, 0.09), (0.6, 0.1), (0.8, 0.1))


def fix3(v):
    """Three decimals with a decimal comma: 0.77 -> '0,770'."""
    return f"{v:.3f}".replace(".", ",")


def layer_runs(pts, t):
    """Pieces of the region t <= height <= z(x) under a sampled curve, as (x, z) polygons."""
    runs, cur = [], []
    for (xa, za), (xb, zb) in zip(pts, pts[1:]):
        if (za > t) != (zb > t):
            xc = xa + (t - za) * (xb - xa) / (zb - za)
            if za > t:
                cur.append((xa, za))
                cur.append((xc, t))
                runs.append(cur)
                cur = []
            else:
                cur = [(xc, t)]
        elif za > t:
            cur.append((xa, za))
    if cur:
        cur.append(pts[-1])
        runs.append(cur)
    out = []
    for run in runs:
        if len(run) < 2:
            continue
        out.append(run + [(run[-1][0], t), (run[0][0], t)])
    return out


PEAKS = {}
for n in range(1, NMAX + 1):
    m = max(60, 18 * n)
    xs = [k / m for k in range(m + 1)]
    pts = [(x, ratio(x, n)) for x in xs]
    for t, op in LAYERS:
        for poly in layer_runs(pts, t):
            S.polygon([W(x, n, z) for x, z in poly], THEORY, op)
    S.line([W(0, n, 0), W(1, n, 0)], TEXT, 0.7, None, 0.35)
    S.line([W(x, n, z) for x, z in pts], THEORY, 1.5)
    for i in range(n + 1):
        S.point(W(i / n, n, 0), TEXT, 1.7)
    # strip number at the right-hand end
    S.label(W(1, n, 0), (it("n") + " = 1") if n == 1 else str(n), 9, 4, TEXT, 10.5 if n > 1 else 11.5)
    # peaks of the end and middle subintervals
    j_mid = (n - 1) // 2
    xe = argmax(lambda t: ratio(t, n), 0, 1 / n)
    xm = argmax(lambda t: ratio(t, n), j_mid / n, (j_mid + 1) / n)
    PEAKS[n] = ((xe, ratio(xe, n)), (xm, ratio(xm, n)))

# marked peaks
for n in (1, 2, 5, 10):
    (xe, ze), _ = PEAKS[n]
    S.point(W(xe, n, ze), PRACTICE, 3.6)
for n in (4, 10):
    _, (xm, zm) = PEAKS[n]
    S.point(W(xm, n, zm), BASE, 3.6)
(xe, ze), _ = PEAKS[1]
X, Y = S.pt(W(xe, 1, ze))
plabel(pl, X, Y, "1", 0, -9, PRACTICE, 11.5, "middle", True)
for n in (2, 5, 10):
    (xe, ze), _ = PEAKS[n]
    X, Y = S.pt(W(xe, n, ze))
    plabel(pl, X, Y, fix3(ze), -7, -3, PRACTICE, 11.5, "end", True)
_, (xm, zm) = PEAKS[4]
X, Y = S.pt(W(xm, 4, zm))
plabel(pl, X, Y, fix3(zm), 0, -11, BASE, 11.5, "middle", True)
_, (xm, zm) = PEAKS[10]
X, Y = S.pt(W(xm, 10, zm))
plabel(pl, X, Y, fix3(zm), 0, 19, BASE, 11.5, "middle", True)
X, Y = S.pt(W(1, N0, 1))
plabel(pl, X, Y, "oran = 1", 8, 4, BASE, 11.5)
save("carpim-yuzeyi", figure(
    int(pl.x0 + pl.w + 40), int(pl.y0 + pl.h + 30), [pl],
    "[0, 1] aralığında <em>h</em> = 1/<em>n</em> adımlı <em>n</em> + 1 eşit aralıklı düğüm için "
    "|(<em>x</em> &#8722; <em>x</em><sub>0</sub>)&#8230;(<em>x</em> &#8722; <em>x</em><sub><em>n</em></sub>)| "
    "çarpımının <em>h</em><sup><em>n</em>+1</sup><em>n</em>!/4 sınırına oranı, <em>n</em> = 1, 2, &#8230;, 10. "
    "Her şerit bir <em>n</em> değerine aittir; dolgu, oran büyüdükçe koyulaşır. Bütün şeritler "
    "oran = 1 düzleminin altında kalır. Uç alt aralıklardaki tepeler (<em>n</em> = 1, 2, 5, 10 için 1; "
    "0,770; 0,563; 0,459) yüksektir; orta alt aralıktaki tepe <em>n</em> = 4'te 0,236, <em>n</em> = 10'da "
    "0,005'tir.",
    aria="Ribbons over the interval from 0 to 1 for n = 1 to 10 showing the ratio of the node product to "
         "the bound h^(n+1) n!/4; every ribbon stays below the plane at height 1, the peaks near x = 0 and "
         "x = 1 stay high while the middle peaks shrink toward 0 as n grows"))

EPS = "&#949;"


def axis_tick(p, x, s):
    """Tick mark on the bottom axis with a label below it."""
    Y = p.y0 + p.h
    p.add(f'<line x1="{p.X(x):.1f}" y1="{Y - 4:.1f}" x2="{p.X(x):.1f}" y2="{Y + 4:.1f}" '
          f'stroke="{TEXT}" stroke-width="1.1" opacity="0.7"/>')
    p.text_px(p.X(x), Y + 19, s, TEXT, 12.5, "middle")


def poly_through(xs, ys):
    """The interpolating polynomial through (xs, ys) in Lagrange form, as a callable."""
    def f(x):
        total = 0.0
        for i, (xi_, yi) in enumerate(zip(xs, ys)):
            term = yi
            for j, xj in enumerate(xs):
                if j != i:
                    term *= (x - xj) / (xi_ - xj)
            total += term
        return total
    return f


# ============================================================
# weierstrass-serit: a polynomial y = P(x) inside the band f(x) - eps < y < f(x) + eps on [a, b]
# ============================================================
WA, WB, WEPS = 0.7, 4.5, 0.62


def wf(x):
    return 1.9 + 0.55 * x + 0.9 * math.tanh(1.6 * (x - 1.6)) - 0.52 * math.tanh(1.3 * (x - 3.2))


# P is a genuine polynomial: it interpolates f plus a gentle wave at 12 Chebyshev nodes of [a, b]
CH = [(WA + WB) / 2 + (WB - WA) / 2 * math.cos((2 * k + 1) * math.pi / 24) for k in range(12)]
WP = poly_through(CH, [wf(t) + 0.62 * WEPS * math.sin(2.6 * (t - WA) + 0.5) for t in CH])
WGAP = max(abs(wf(WA + (WB - WA) * k / 2000) - WP(WA + (WB - WA) * k / 2000)) for k in range(2001))
assert WGAP < 0.85 * WEPS, WGAP

p = Plot(50, 30, 380, 240, (0, 5), (0.6, 5.2))
p.axes((), (), it("x"), it("y"))
band_lo = sample(lambda x: wf(x) - WEPS, WA, WB)
band_hi = sample(lambda x: wf(x) + WEPS, WA, WB)
p.polygon(band_lo + band_hi[::-1], PRACTICE, 0.10)
for xv in (WA, WB):
    p.vline(xv, 0.6, wf(xv) + WEPS, TEXT, "4 3", 0.4)
    axis_tick(p, xv, it("a" if xv == WA else "b"))
p.line(band_hi, PRACTICE, 1.6, "7 4")
p.line(band_lo, PRACTICE, 1.6, "7 4")
p.line(sample(wf, WA, WB), TEXT, 2.6)
p.line(sample(WP, WA, WB), THEORY, 2.2)
# the half width eps of the band, as a double arrow below the graph of f (P runs above f there)
XE = 1.05
p.arrow((XE, wf(XE) - WEPS / 2), (XE, wf(XE) - WEPS), TEXT, 1.1, 6.0, None, 0.85)
p.arrow((XE, wf(XE) - WEPS / 2), (XE, wf(XE)), TEXT, 1.1, 6.0, None, 0.85)
p.label(XE, wf(XE) - WEPS / 2, it(EPS), 6, 5, TEXT, 13, "start")
# right-hand column of names
ends = [(wf(WB) + WEPS, it("f") + "(" + it("x") + ") + " + it(EPS), PRACTICE, False),
        (WP(WB), it("P") + "(" + it("x") + ")", THEORY, True),
        (wf(WB), it("f") + "(" + it("x") + ")", TEXT, True),
        (wf(WB) - WEPS, it("f") + "(" + it("x") + ") " + MINUS + " " + it(EPS), PRACTICE, False)]
for yv, s, c, b in ends:
    p.label(WB, yv, s, 8, 4, c, 12, "start", b)
save("weierstrass-serit", figure(
    560, 340, [p],
    "<em>f</em> grafiğinin çevresinde, <em>y</em> = <em>f</em>(<em>x</em>) &#8722; &#949; ile "
    "<em>y</em> = <em>f</em>(<em>x</em>) + &#949; kesikli eğrileri arasındaki şerit. Teorem, [<em>a</em>, <em>b</em>] "
    "aralığının tamamında bu şeridin içinde kalan bir <em>P</em> polinomu bulunduğunu söyler.",
    aria="A continuous function y = f(x) on the interval from a to b, the dashed curves f(x) + eps and "
         "f(x) - eps bounding a shaded band, and a polynomial y = P(x) that wiggles but stays inside the band"))

# ============================================================
# lineer-interpolasyon: the line y = P(x) through (x_0, f(x_0)) and (x_1, f(x_1))
# ============================================================
LX0, LX1 = 1.2, 3.6


def lf(x):
    return 0.6 + 2.2 * math.log(x + 0.25) - 0.08 * (x - 2) ** 2


LSLOPE = (lf(LX1) - lf(LX0)) / (LX1 - LX0)


def lp(x):
    return lf(LX0) + LSLOPE * (x - LX0)


p = Plot(50, 30, 380, 260, (0, 5), (0, 4.6))
p.axes((), (), it("x"), it("y"))
for k, xv in enumerate((LX0, LX1)):
    p.vline(xv, 0, lf(xv), TEXT, "4 3", 0.45)
    axis_tick(p, xv, it("x") + sub(str(k)))
p.line(sample(lf, 0.7, 4.75), TEXT, 2.6)
p.line([(0.55, lp(0.55)), (4.55, lp(4.55))], THEORY, 2.2)
for xv in (LX0, LX1):
    dot(p, (xv, lf(xv)), TEXT, 4.4)
plabel(p, LX0, lf(LX0), "(" + it("x") + sub("0") + ", " + it("f") + "(" + it("x") + sub("0") + "))", 8, 18, TEXT, 12)
plabel(p, LX1, lf(LX1), "(" + it("x") + sub("1") + ", " + it("f") + "(" + it("x") + sub("1") + "))", -6, -12, TEXT, 12,
       "end")
p.label(4.75, lf(4.75), it("y") + " = " + it("f") + "(" + it("x") + ")", 8, 4, TEXT, 12.5, "start", True)
p.label(4.55, lp(4.55), it("y") + " = " + it("P") + "(" + it("x") + ")", 8, 4, THEORY, 12.5, "start", True)
save("lineer-interpolasyon", figure(
    540, 330, [p],
    "<em>y</em> = <em>f</em>(<em>x</em>) eğrisi ve (<em>x</em><sub>0</sub>, <em>f</em>(<em>x</em><sub>0</sub>)), "
    "(<em>x</em><sub>1</sub>, <em>f</em>(<em>x</em><sub>1</sub>)) noktalarından geçen <em>y</em> = <em>P</em>(<em>x</em>) "
    "doğrusu. <em>P</em>, iki düğümde <em>f</em> ile aynı değeri alır; düğümlerin arasında ve dışında "
    "<em>f</em>'den ayrılır.",
    aria="A curve y = f(x) and the straight line y = P(x) through the two points with abscissae x0 and x1; the "
         "line meets the curve exactly at the two nodes and departs from it elsewhere"))

# ============================================================
# taylor-genis: e^x and P_0 ... P_5 about x_0 = 0 on [-1, 3]
# ============================================================
p = Plot(55, 30, 380, 300, (-1, 3), (-1, 21))
p.grid([0, 1, 2, 3], [5, 10, 15, 20])
p.axes((-1, 0, 1, 2, 3), (0, 5, 10, 15, 20), it("x"), it("y"), dec, dec)
p.line([(-1, 0), (3, 0)], TEXT, 1.0, None, 0.4)
p.line([(0, -1), (0, 21)], TEXT, 1.0, None, 0.4)
TCOL = ((REMARK, None), (BASE, "6 4"), (PRACTICE, None), (THEORY, "6 4"), (REMARK, "2 3"), (BASE, None))
for k in range(6):
    p.line(sample(taylor(k), -1, 3), TCOL[k][0], 1.8, TCOL[k][1])
p.line(sample(math.exp, -1, 3), TEXT, 3.0)
E3 = math.exp(3)
p.label(3, E3, it("y") + " = " + it("e") + sup(it("x")), 9, 5, TEXT, 12.5, bold=True)
for k in range(6):
    p.label(3, taylor(k)(3), it("y") + " = " + it("P") + sub(str(k)) + "(" + it("x") + ")", 9, 5,
            TCOL[k][0], 12, bold=True)
assert abs(taylor(5)(3) - 18.4) < 1e-12
save("taylor-genis", figure(
    560, 370, [p],
    "<em>e</em><sup><em>x</em></sup> (kalın) ve <em>x</em><sub>0</sub> = 0 civarındaki <em>P</em><sub>0</sub>, "
    "<em>P</em><sub>1</sub>, &#8230;, <em>P</em><sub>5</sub> Taylor polinomları, [&#8722;1, 3] aralığında. "
    "0 civarında bütün eğriler <em>e</em><sup><em>x</em></sup> ile neredeyse çakışır; <em>x</em> = 3'te ise "
    "<em>P</em><sub>5</sub>(3) = 18,4 bile <em>e</em><sup>3</sup> &#8776; 20,086 değerinden belirgin biçimde "
    "uzaktır.",
    aria="The exponential function on the interval from -1 to 3 together with its Taylor polynomials P0 to P5 "
         "about x0 = 0; near 0 all curves agree, while at x = 3 even P5(3) = 18.4 stays well below e^3 = 20.086"))
