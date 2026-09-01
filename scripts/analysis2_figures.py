# -*- coding: utf-8 -*-
"""
Generates the SVG figures used in the "Analiz 2" chapters (dersler/analiz/2).

Same authoring flow as scripts/analysis_figures.py: the figures are NOT produced
at build time. Run this script, then

    python scripts/center_figures.py "analysis2-*.md"

(which measures each drawing and centers it in its viewBox) and paste the
resulting markup into the .qmd files — inside the theorem/example/proof box the
figure explains, never inside a definition box. Building the books therefore
needs neither Python nor Jupyter; CI runs Quarto alone.

The captions are Turkish on purpose — they are the text shown on the site.

Usage:   python scripts/analysis2_figures.py && python scripts/center_figures.py "analysis2-*.md"
Output:  scripts/_figures/analysis2-<name>.md
"""
import io
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from svg_plot import *  # noqa: E402,F403 — Plot, figure, colors, WIDE, hollow, dot, ...

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_figures")
os.makedirs(OUT_DIR, exist_ok=True)
OUT = {}

EPS, DELTA, ELL, INF, LEQ_S = "&#949;", "&#948;", "&#8467;", "&#8734;", "&#8804;"
PRIME, GEQ_S, NEQ_S, TIMES_S, MINUS_S = "&#8242;", "&#8805;", "&#8800;", "&#215;", "&#8722;"
INT_S, SUM_S, ARROW = "&#8747;", "&#8721;", "&#8594;"


def subs(s, size=9):
    """Subscript inside an SVG <text>: 'x' + subs('0')."""
    return f'<tspan font-size="{size}" dy="4">{s}</tspan><tspan dy="-4">&#8203;</tspan>'


def sups(s, size=8.5):
    """Superscript inside an SVG <text>."""
    return f'<tspan font-size="{size}" dy="-5">{s}</tspan><tspan dy="5">&#8203;</tspan>'


def curve(p, f, x0, x1, color=THEORY, width=1.9, samples=200, dash=None, opacity=1.0):
    """Polyline of y = f(x) on [x0, x1]."""
    pts = [(x0 + (x1 - x0) * k / samples, f(x0 + (x1 - x0) * k / samples)) for k in range(samples + 1)]
    p.line(pts, color, width, dash, opacity)


def guide(p, pts, color=TEXT, opacity=0.5, width=1.0):
    """Thin dashed guide line through the given data points."""
    p.line(pts, color, width, "4 3", opacity)


def tfmt(v):
    """Tick label with the Turkish decimal comma: 0.5 -> '0,5'."""
    return fmt(v).replace(".", ",")


def rect(p, x0, x1, y0, y1, color=THEORY, opacity=0.16, stroke=None, width=1.0):
    """Axis-aligned rectangle in data coordinates."""
    p.polygon([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], color, opacity,
              stroke if stroke else "none", width)


def through(f, x0, slope, x):
    """The line through (x0, f(x0)) with the given slope, evaluated at x."""
    return f(x0) + slope * (x - x0)

def clipped(p, f, x0, x1, color=THEORY, width=1.9, samples=400, opacity=1.0):
    """Like curve(), but drops the pieces that fall outside the panel's y-range."""
    run = []
    for k in range(samples + 1):
        x = x0 + (x1 - x0) * k / samples
        try:
            y = f(x)
        except (ValueError, ZeroDivisionError, OverflowError):
            y = None
        if y is None or not (p.ymin <= y <= p.ymax):
            if len(run) > 1:
                p.line(run, color, width, None, opacity)
            run = []
        else:
            run.append((x, y))
    if len(run) > 1:
        p.line(run, color, width, None, opacity)



# ============================================================ teget-kesen
# The derivative as the limit of secant slopes.
def f_sec(x):
    return 0.55 * x * x - 0.9 * x + 1.9


X0S = 1.15
DER = 2 * 0.55 * X0S - 0.9
p = Plot(48, 26, 300, 214, (-0.15, 3.2), (0.2, 4.35))
p.axes((1, 2, 3), (1, 2, 3, 4), "x", "y")
for xs, op in ((2.75, 0.30), (2.35, 0.45), (1.95, 0.62)):
    m = (f_sec(xs) - f_sec(X0S)) / (xs - X0S)
    p.line([(0.30, through(f_sec, X0S, m, 0.30)), (3.10, through(f_sec, X0S, m, 3.10))],
           PRACTICE, 1.3, None, op)
    dot(p, (xs, f_sec(xs)), PRACTICE, 3.2)
p.line([(0.30, through(f_sec, X0S, DER, 0.30)), (3.10, through(f_sec, X0S, DER, 3.10))],
       BASE, 2.0)
curve(p, f_sec, 0.15, 2.90, THEORY, 2.1)
dot(p, (X0S, f_sec(X0S)), TEXT, 4.2)
guide(p, [(X0S, 0.2), (X0S, f_sec(X0S))], TEXT, 0.4)
p.label(X0S, 0.2, "x" + subs("0"), 0, 15, TEXT, 11.5, "middle", True, True)
p.label(1.95, f_sec(1.95), "x", -6, 15, PRACTICE, 11, "end", False, True)
p.label(2.75, f_sec(2.75), "kesenler", 6, 2, PRACTICE, 10.5, "start", False, True)
p.label(0.62, through(f_sec, X0S, DER, 0.62), "teğet: eğim f" + PRIME + "(x" + subs("0") + ")",
        0, 18, BASE, 11, "middle", True, True)
p.label(2.35, f_sec(2.35), "y = f(x)", -10, -8, THEORY, 12, "end", True, True)
OUT["teget-kesen"] = figure(
    400, 258, [p],
    "Fark oranı, (<em>x</em><sub>0</sub>, <em>f</em>(<em>x</em><sub>0</sub>)) ile (<em>x</em>, <em>f</em>(<em>x</em>)) "
    "noktalarından geçen kesenin eğimidir. <em>x</em> &#8594; <em>x</em><sub>0</sub> giderken kesenler "
    "<em>x</em><sub>0</sub> noktasındaki teğete yaklaşır; teğetin eğimi tam olarak "
    "<em>f</em>&#8242;(<em>x</em><sub>0</sub>)'dır.",
    aria="Kesen dogrularin egimi limitte teget dogrusunun egimine yaklasiyor")

# ============================================================ turevsizlik
# Two ways a derivative fails to exist: a corner and a vertical tangent.
p1 = Plot(44, 28, 222, 190, (-1.7, 1.7), (-0.35, 1.75))
p1.origin_axes("x", "y")
panel_title(p1, "Köşe: f(x) = |x|")
curve(p1, lambda x: -x, -1.42, 0, THEORY, 2.1, 20)
curve(p1, lambda x: x, 0, 1.42, PRACTICE, 2.1, 20)
p1.line([(-1.0, 1.0), (0.55, -0.55)], THEORY, 1.2, "4 3", 0.55)
p1.line([(-0.55, -0.55), (1.0, 1.0)], PRACTICE, 1.2, "4 3", 0.55)
dot(p1, (0, 0), TEXT, 4.2)
p1.label(-1.1, 1.6, "f" + PRIME + sups("&#8722;") + "(0) = " + MINUS_S + "1", 0, 0, THEORY, 10.5, "middle", False, True)
p1.label(1.1, 1.6, "f" + PRIME + sups("+") + "(0) = 1", 0, 0, PRACTICE, 10.5, "middle", False, True)

p2 = Plot(322, 28, 222, 190, (-1.5, 1.5), (-1.35, 1.35))
p2.origin_axes("x", "y")
panel_title(p2, "Düşey teğet: f(x) = x" + sups("1/3"))
curve(p2, lambda x: (abs(x) ** (1.0 / 3.0)) * (1 if x >= 0 else -1), -1.4, 1.4, THEORY, 2.1, 300)
p2.line([(0, -1.25), (0, 1.25)], PRACTICE, 1.4, "4 3", 0.7)
dot(p2, (0, 0), TEXT, 4.2)
p2.label(-1.4, 1.0, "teğet düşey:", 0, 0, PRACTICE, 10.5, "start", False, True)
p2.label(-1.4, 0.76, "fark oranı +" + INF, 0, 0, PRACTICE, 10.5, "start", False, True)
OUT["turevsizlik"] = figure(
    560, 240, [p1, p2],
    "Türevin var olmadığı iki tipik durum. Solda <em>f</em>(<em>x</em>) = |<em>x</em>|: sağ ve sol türev vardır "
    "(1 ve &#8722;1) ama eşit değildir, grafikte köşe oluşur. Sağda <em>f</em>(<em>x</em>) = "
    "<em>x</em><sup>1/3</sup>: fark oranı +&#8734;'a ıraksar, teğet düşeydir; her iki fonksiyon da "
    "0 noktasında süreklidir.",
    aria="Solda mutlak deger fonksiyonunda kose, sagda kup kok fonksiyonunda dusey teget")

# ============================================================ rolle
def f_rolle(x):
    return 0.62 * math.sin(1.9 * (x - 0.35)) + 0.18 * math.sin(3.9 * (x - 0.35)) + 0.95


AR, BR = 0.35, 0.35 + 2 * math.pi / 1.9
# f(a) = f(b) by construction; find the interior critical points numerically
def d_rolle(x):
    return 0.62 * 1.9 * math.cos(1.9 * (x - 0.35)) + 0.18 * 3.9 * math.cos(3.9 * (x - 0.35))


crit = []
N = 4000
for k in range(N):
    u = AR + (BR - AR) * k / N
    v = AR + (BR - AR) * (k + 1) / N
    if d_rolle(u) * d_rolle(v) < 0:
        lo, hi = u, v
        for _ in range(60):
            mid = (lo + hi) / 2
            if d_rolle(lo) * d_rolle(mid) <= 0:
                hi = mid
            else:
                lo = mid
        crit.append((lo + hi) / 2)

p = Plot(48, 26, 306, 206, (-0.15, 3.9), (0.0, 2.05))
p.origin_axes("x", "y")
guide(p, [(0, f_rolle(AR)), (BR, f_rolle(AR))], TEXT, 0.45)
guide(p, [(AR, 0.0), (AR, f_rolle(AR))], TEXT, 0.4)
guide(p, [(BR, 0.0), (BR, f_rolle(BR))], TEXT, 0.4)
for c in crit:
    p.line([(c - 0.42, f_rolle(c)), (c + 0.42, f_rolle(c))], PRACTICE, 1.8)
    guide(p, [(c, 0.0), (c, f_rolle(c))], PRACTICE, 0.4)
curve(p, f_rolle, AR, BR, THEORY, 2.1)
dot(p, (AR, f_rolle(AR)), TEXT, 4.0)
dot(p, (BR, f_rolle(BR)), TEXT, 4.0)
for c in crit:
    dot(p, (c, f_rolle(c)), PRACTICE, 4.0)
p.label(AR, 0.0, "a", 0, 15, TEXT, 11.5, "middle", True, True)
p.label(BR, 0.0, "b", 0, 15, TEXT, 11.5, "middle", True, True)
for i, c in enumerate(crit):
    p.label(c, 0.0, "c" + subs(str(i + 1)), 0, 15, PRACTICE, 11, "middle", True, True)
p.label(0, f_rolle(AR), "f(a) = f(b)", -7, 4, TEXT, 10.5, "end", False, True)
p.label(crit[0], f_rolle(crit[0]), "f" + PRIME + "(c) = 0", 0, -10, PRACTICE, 10.5, "middle", False, True)
p.label(2.15, f_rolle(2.15), "y = f(x)", 6, -12, THEORY, 12, "start", True, True)
OUT["rolle"] = figure(
    400, 252, [p],
    "Rolle teoremi: uçlarda aynı değeri alan türevlenebilir bir eğrinin, aralığın içinde en az bir yerde "
    "yatay teğeti vardır. Weierstrass teoremi bir maksimum ve bir minimum noktası verir; uç değerler eşit "
    "olduğundan bunlardan biri iç noktadadır ve orada Fermat teoremi gereği türev sıfırdır.",
    aria="Rolle teoremi: f(a)=f(b) olan egride yatay tegetli ic noktalar")

# ============================================================ ortalama-deger
def f_mvt(x):
    return 0.28 * x ** 3 - 1.25 * x ** 2 + 1.55 * x


AM, BM = 0.35, 3.2
SL = (f_mvt(BM) - f_mvt(AM)) / (BM - AM)


def d_mvt(x):
    return 0.84 * x * x - 2.5 * x + 1.55


roots = []
disc = 2.5 ** 2 - 4 * 0.84 * (1.55 - SL)
for sgn in (-1, 1):
    r = (2.5 + sgn * math.sqrt(disc)) / (2 * 0.84)
    if AM < r < BM:
        roots.append(r)
roots.sort()

p = Plot(48, 26, 306, 208, (-0.15, 3.6), (0.0, 1.62))
p.origin_axes("x", "y")
p.line([(AM, f_mvt(AM)), (BM, f_mvt(BM))], PRACTICE, 1.8)
guide(p, [(AM, 0.0), (AM, f_mvt(AM))], TEXT, 0.4)
guide(p, [(BM, 0.0), (BM, f_mvt(BM))], TEXT, 0.4)
for c in roots:
    p.line([(c - 0.6, through(f_mvt, c, SL, c - 0.6)), (c + 0.6, through(f_mvt, c, SL, c + 0.6))],
           BASE, 1.8)
    guide(p, [(c, 0.0), (c, f_mvt(c))], BASE, 0.4)
curve(p, f_mvt, AM, BM, THEORY, 2.1)
dot(p, (AM, f_mvt(AM)), TEXT, 4.0)
dot(p, (BM, f_mvt(BM)), TEXT, 4.0)
for c in roots:
    dot(p, (c, f_mvt(c)), BASE, 4.0)
p.label(AM, 0.0, "a", 0, 15, TEXT, 11.5, "middle", True, True)
p.label(BM, 0.0, "b", 0, 15, TEXT, 11.5, "middle", True, True)
for i, c in enumerate(roots):
    p.label(c, 0.0, "c" + subs(str(i + 1)), 0, 15, BASE, 11, "middle", True, True)
p.label(1.75, f_mvt(AM) + SL * (1.75 - AM), "kiriş: eğim (f(b)" + MINUS_S + "f(a))/(b" + MINUS_S + "a)",
        0, -9, PRACTICE, 10.5, "middle", False, True)
p.label(roots[0], f_mvt(roots[0]), "teğet, kirişe paralel", -2, -11, BASE, 10.5, "middle", False, True)
p.label(1.5, f_mvt(1.5), "y = f(x)", 0, 22, THEORY, 12, "middle", True, True)
OUT["ortalama-deger"] = figure(
    400, 254, [p],
    "Ortalama değer teoremi: uç noktaları birleştiren kirişe <em>paralel</em> bir teğetin çizilebildiği en az "
    "bir <em>c</em> noktası vardır. İspat, eğri ile kiriş arasındaki düşey farkı ölçen yardımcı fonksiyona "
    "Rolle teoremini uygulamaktan ibarettir.",
    aria="Ortalama deger teoremi: kirise paralel teget noktalari")

# ============================================================ konvekslik
def f_cvx(x):
    return 0.30 * x * x - 0.55 * x + 1.50


X1C, X2C = 0.55, 3.25
ALP = 0.62
XA = ALP * X1C + (1 - ALP) * X2C
p1 = Plot(44, 30, 226, 194, (-0.1, 3.9), (0.0, 3.55))
p1.origin_axes("x", "y")
panel_title(p1, "Konveks: yay kirişin altında")
p1.polygon([(X1C, f_cvx(X1C)), (X2C, f_cvx(X2C))]
           + [(X2C - (X2C - X1C) * k / 40, f_cvx(X2C - (X2C - X1C) * k / 40)) for k in range(41)],
           THEORY, 0.10)
p1.line([(X1C, f_cvx(X1C)), (X2C, f_cvx(X2C))], PRACTICE, 1.8)
curve(p1, f_cvx, 0.25, 3.6, THEORY, 2.1)
sec_y = f_cvx(X1C) + (f_cvx(X2C) - f_cvx(X1C)) * (XA - X1C) / (X2C - X1C)
guide(p1, [(XA, f_cvx(XA)), (XA, sec_y)], BASE, 0.75, 1.4)
dot(p1, (X1C, f_cvx(X1C)), TEXT, 3.8)
dot(p1, (X2C, f_cvx(X2C)), TEXT, 3.8)
dot(p1, (XA, sec_y), PRACTICE, 3.8)
dot(p1, (XA, f_cvx(XA)), THEORY, 3.8)
guide(p1, [(X1C, 0.0), (X1C, f_cvx(X1C))], TEXT, 0.35)
guide(p1, [(X2C, 0.0), (X2C, f_cvx(X2C))], TEXT, 0.35)
guide(p1, [(XA, 0.0), (XA, f_cvx(XA))], BASE, 0.35)
p1.label(X1C, 0.0, "x" + subs("1"), 0, 15, TEXT, 11, "middle", True, True)
p1.label(X2C, 0.0, "x" + subs("2"), 0, 15, TEXT, 11, "middle", True, True)
p1.label(XA, 0.0, "&#945;x" + subs("1") + "+(1" + MINUS_S + "&#945;)x" + subs("2"), 0, 15, BASE, 9.5, "middle", False, True)
p1.label(XA, sec_y, "&#945;f(x" + subs("1") + ")+(1" + MINUS_S + "&#945;)f(x" + subs("2") + ")", 12, -13, PRACTICE, 9.5, "start", False, True)
p1.label(XA, f_cvx(XA), "f(&#945;x" + subs("1") + "+(1" + MINUS_S + "&#945;)x" + subs("2") + ")", 0, 22, THEORY, 9.5, "middle", False, True)

p2 = Plot(322, 30, 226, 194, (-0.1, 3.9), (0.0, 3.55))
p2.origin_axes("x", "y")
panel_title(p2, "Teğetin üstünde kalır")
XT = 1.35
for xt, col in ((0.85, BASE), (XT, PRACTICE), (2.95, BASE)):
    m = 0.60 * xt - 0.55
    p2.line([(max(0.1, xt - 1.15), through(f_cvx, xt, m, max(0.1, xt - 1.15))),
             (min(3.7, xt + 1.15), through(f_cvx, xt, m, min(3.7, xt + 1.15)))],
            col, 1.5, None, 1.0 if col == PRACTICE else 0.55)
    dot(p2, (xt, f_cvx(xt)), col, 3.6)
curve(p2, f_cvx, 0.25, 3.6, THEORY, 2.1)
p2.label(XT, f_cvx(XT), "f(x) " + GEQ_S + " f(x" + subs("0") + ")+f" + PRIME + "(x" + subs("0") + ")(x" + MINUS_S + "x" + subs("0") + ")",
         0, 30, PRACTICE, 10, "middle", False, True)
p2.label(2.95, f_cvx(2.95), "teğet eğimleri artar", 6, -18, BASE, 10, "end", False, True)
OUT["konvekslik"] = figure(
    560, 244, [p1, p2],
    "Solda konveksliğin tanımı: [<em>x</em><sub>1</sub>, <em>x</em><sub>2</sub>] üzerindeki her ara noktada "
    "eğrinin değeri, kirişin değerinden küçük ya da ona eşittir. Sağda iki eşdeğer görünüm: konveks bir "
    "fonksiyonun grafiği her teğetinin üstünde kalır ve teğet eğimleri, yani <em>f</em>&#8242;, artar.",
    aria="Konveks fonksiyon: yay kirisin altinda, grafik tegetin ustunde, teget egimleri artiyor")

# ============================================================ donum-noktasi
def f_inf(x):
    return 0.34 * x ** 3 - 1.5 * x ** 2 + 1.9 * x + 0.05


XI = 1.5 / (3 * 0.34)                     # f''(x) = 0
p = Plot(48, 26, 300, 206, (-0.15, 3.6), (0.0, 2.1))
p.origin_axes("x", "y")
guide(p, [(XI, 0.0), (XI, f_inf(XI))], PRACTICE, 0.5)
curve(p, f_inf, 0.1, XI, THEORY, 2.2)
curve(p, f_inf, XI, 3.2, BASE, 2.2)
m_inf = 3 * 0.34 * XI * XI - 3 * XI + 1.9
p.line([(XI - 1.25, through(f_inf, XI, m_inf, XI - 1.25)), (XI + 1.25, through(f_inf, XI, m_inf, XI + 1.25))],
       PRACTICE, 1.4, "4 3", 0.8)
dot(p, (XI, f_inf(XI)), PRACTICE, 4.4)
p.label(XI, 0.0, "x" + subs("0"), 0, 15, PRACTICE, 11.5, "middle", True, True)
p.label(0.72, f_inf(0.72), "konkav (f" + PRIME + PRIME + " &lt; 0)", 0, 20, THEORY, 10.5, "middle", False, True)
p.label(2.95, f_inf(2.95), "konveks (f" + PRIME + PRIME + " &gt; 0)", -10, -12, BASE, 10.5, "end", False, True)
p.label(XI, f_inf(XI), "dönüm noktası", 8, -14, PRACTICE, 10.5, "start", True, True)
OUT["donum-noktasi"] = figure(
    400, 252, [p],
    "Dönüm noktasında eğrilik yön değiştirir: solda konkav (<em>f</em>&#8242;&#8242; &lt; 0), sağda konveks "
    "(<em>f</em>&#8242;&#8242; &gt; 0). Teğet, dönüm noktasında eğriyi <em>keser</em> — bir tarafta üstünde, "
    "öbür tarafta altında kalır.",
    aria="Donum noktasinda konkavlik konveksllige donuyor, teget egriyi kesiyor")

# ============================================================ darboux-toplamlari
def f_dar(x):
    return 1.05 + 0.62 * math.sin(1.35 * x) + 0.17 * x


AD, BD, ND = 0.35, 3.45, 6
CUT = [AD + (BD - AD) * k / ND for k in range(ND + 1)]


def ext_on(f, u, v, want_max):
    vals = [f(u + (v - u) * k / 60) for k in range(61)]
    return max(vals) if want_max else min(vals)


panels = []
for want_max, ttl, col in ((False, "Alt toplam L(P, f)", THEORY), (True, "Üst toplam U(P, f)", PRACTICE)):
    q = Plot(44 if not want_max else 322, 30, 226, 192, (-0.1, 3.85), (0.0, 2.35))
    q.origin_axes("x", "y")
    panel_title(q, ttl, col)
    for k in range(ND):
        u, v = CUT[k], CUT[k + 1]
        h = ext_on(f_dar, u, v, want_max)
        rect(q, u, v, 0, h, col, 0.20, col, 0.9)
    curve(q, f_dar, AD, BD, TEXT, 2.0)
    for x in CUT:
        q.line([(x, 0), (x, -0.05)], TEXT, 1.0, None, 0.6)
    q.label(AD, 0, "a", 0, 15, TEXT, 11, "middle", True, True)
    q.label(BD, 0, "b", 0, 15, TEXT, 11, "middle", True, True)
    q.label(CUT[3], 0, "x" + subs("k"), 0, 15, TEXT, 10.5, "middle", False, True)
    q.label(2.05, 2.12, ("M" if want_max else "m") + subs("k") + " = "
            + ("sup" if want_max else "inf") + " f", 0, 0, col, 10.5, "middle", False, True)
    panels.append(q)
OUT["darboux-toplamlari"] = figure(
    560, 244, panels,
    "Aynı bölünüş için alt ve üst Darboux toplamları. Solda her dikdörtgenin yüksekliği o alt aralıktaki "
    "<em>infimum</em>, sağda <em>supremum</em>'dur; eğrinin altındaki alan her zaman ikisinin arasındadır. "
    "Bölünüş inceldikçe iki toplam birbirine yaklaşır — Riemann ölçütü tam bunu ister.",
    aria="Alt Darboux toplami egrinin altinda, ust Darboux toplami egrinin ustunde kalan dikdortgenler")

# ============================================================ riemann-toplami
p = Plot(48, 28, 306, 200, (-0.1, 3.85), (0.0, 2.35))
p.origin_axes("x", "y")
SAMP = (0.14, 0.72, 0.35, 0.9, 0.5, 0.28)
for k in range(ND):
    u, v = CUT[k], CUT[k + 1]
    t = u + (v - u) * SAMP[k]
    rect(p, u, v, 0, f_dar(t), BASE, 0.18, BASE, 0.9)
    dot(p, (t, 0), PRACTICE, 3.0)
    dot(p, (t, f_dar(t)), PRACTICE, 3.2)
    guide(p, [(t, 0), (t, f_dar(t))], PRACTICE, 0.45)
curve(p, f_dar, AD, BD, TEXT, 2.0)
p.label(AD, 0, "a", 0, 15, TEXT, 11, "middle", True, True)
p.label(BD, 0, "b", 0, 15, TEXT, 11, "middle", True, True)
p.label(CUT[1] + (CUT[2] - CUT[1]) * SAMP[1], 0, "t" + subs("k"), 0, 26, PRACTICE, 10.5, "middle", False, True)
p.label(1.95, 2.15, "S(P, f, T) = " + SUM_S + " f(t" + subs("k") + ")&#916;x" + subs("k"),
        0, 0, BASE, 11, "middle", False, True)
OUT["riemann-toplami"] = figure(
    400, 254, [p],
    "Riemann toplamı: her alt aralıkta <em>herhangi</em> bir <em>t</em><sub><em>k</em></sub> örnek noktası "
    "seçilir ve dikdörtgenin yüksekliği <em>f</em>(<em>t</em><sub><em>k</em></sub>) alınır. Bu toplam her zaman "
    "alt ve üst Darboux toplamlarının arasında kaldığından, bölünüşün normu sıfıra giderken sıkıştırma "
    "teoremiyle integrale yakınsar.",
    aria="Riemann toplami: her alt aralikta secilen ornek noktasinin yuksekligindeki dikdortgenler")

# ============================================================ integral-ortalama-deger
def f_avg(x):
    return 0.55 + 0.9 * math.sin(0.98 * x) + 0.1 * x


AA, BA = 0.3, 3.3
area = sum(f_avg(AA + (BA - AA) * (k + 0.5) / 2000) * (BA - AA) / 2000 for k in range(2000))
MEAN = area / (BA - AA)
lo, hi = AA, 1.9
for _ in range(80):
    mid = (lo + hi) / 2
    if f_avg(mid) < MEAN:
        lo = mid
    else:
        hi = mid
X0A = (lo + hi) / 2
p = Plot(48, 26, 306, 202, (-0.1, 3.75), (0.0, 1.95))
p.origin_axes("x", "y")
p.polygon([(AA, 0)] + [(AA + (BA - AA) * k / 120, f_avg(AA + (BA - AA) * k / 120)) for k in range(121)]
          + [(BA, 0)], THEORY, 0.14)
rect(p, AA, BA, 0, MEAN, PRACTICE, 0.0, PRACTICE, 1.7)
guide(p, [(0, MEAN), (BA, MEAN)], PRACTICE, 0.5)
curve(p, f_avg, AA, BA, THEORY, 2.1)
dot(p, (X0A, MEAN), PRACTICE, 4.2)
guide(p, [(X0A, 0), (X0A, MEAN)], PRACTICE, 0.45)
p.label(AA, 0, "a", 0, 15, TEXT, 11, "middle", True, True)
p.label(BA, 0, "b", 0, 15, TEXT, 11, "middle", True, True)
p.label(X0A, 0, "x" + subs("0"), 0, 15, PRACTICE, 11, "middle", True, True)
p.label(0, MEAN, "f(x" + subs("0") + ")", -7, 4, PRACTICE, 10.5, "end", False, True)
p.label(2.55, MEAN, "aynı alan", 0, -8, PRACTICE, 10.5, "middle", False, True)
p.label(1.35, f_avg(1.35), "y = f(x)", 0, -12, THEORY, 12, "middle", True, True)
OUT["integral-ortalama-deger"] = figure(
    400, 254, [p],
    "İntegral için ortalama değer teoremi: sürekli bir <em>f</em> için, eğrinin altındaki alanla <em>tam olarak "
    "aynı</em> alana sahip bir dikdörtgen vardır. Dikdörtgenin yüksekliği <em>f</em>(<em>x</em><sub>0</sub>), "
    "fonksiyonun [<em>a</em>, <em>b</em>] üzerindeki ortalama değeridir ve süreklilik sayesinde gerçekten "
    "alınan bir değerdir.",
    aria="Egrinin altindaki alana esit alanli dikdortgen; yuksekligi fonksiyonun ortalama degeri")

# ============================================================ iki-egri-arasi-alan
def f_top(x):
    return 2.35 - 0.42 * (x - 1.55) ** 2


def f_bot(x):
    return 0.55 + 0.28 * x


ROOTS = []
# 2.35 - 0.42 (x-1.55)^2 = 0.55 + 0.28 x  ->  0.42 x^2 - 1.302 x - 0.7908 + 0.28x... solved numerically
def gap(x):
    return f_top(x) - f_bot(x)


lo, hi = -1.0, 1.55
for _ in range(80):
    mid = (lo + hi) / 2
    if gap(mid) < 0:
        lo = mid
    else:
        hi = mid
XL = (lo + hi) / 2
lo, hi = 1.55, 4.5
for _ in range(80):
    mid = (lo + hi) / 2
    if gap(mid) > 0:
        lo = mid
    else:
        hi = mid
XR = (lo + hi) / 2
p = Plot(48, 26, 306, 202, (-0.35, 3.95), (0.0, 2.75))
p.origin_axes("x", "y")
p.polygon([(XL + (XR - XL) * k / 120, f_top(XL + (XR - XL) * k / 120)) for k in range(121)]
          + [(XR - (XR - XL) * k / 120, f_bot(XR - (XR - XL) * k / 120)) for k in range(121)],
          BASE, 0.16)
XV = XL + 0.62 * (XR - XL)
p.line([(XV, f_bot(XV)), (XV, f_top(XV))], PRACTICE, 1.8)
curve(p, f_top, XL - 0.35, XR + 0.35, THEORY, 2.1)
curve(p, f_bot, XL - 0.35, XR + 0.35, PRACTICE, 2.1)
dot(p, (XL, f_top(XL)), TEXT, 3.8)
dot(p, (XR, f_top(XR)), TEXT, 3.8)
guide(p, [(XL, 0), (XL, f_top(XL))], TEXT, 0.4)
guide(p, [(XR, 0), (XR, f_top(XR))], TEXT, 0.4)
p.label(XL, 0, "a", 0, 15, TEXT, 11, "middle", True, True)
p.label(XR, 0, "b", 0, 15, TEXT, 11, "middle", True, True)
p.label(XV, (f_top(XV) + f_bot(XV)) / 2, "f(x) " + MINUS_S + " g(x)", 8, 4, PRACTICE, 10.5, "start", False, True)
p.label(XL + 0.3 * (XR - XL), f_top(XL + 0.3 * (XR - XL)), "y = f(x)", 0, -10, THEORY, 11.5, "middle", True, True)
p.label(XL + 0.22 * (XR - XL), f_bot(XL + 0.22 * (XR - XL)), "y = g(x)", 0, 16, PRACTICE, 11.5, "middle", True, True)
OUT["iki-egri-arasi-alan"] = figure(
    400, 254, [p],
    "İki eğri arasındaki alan: her <em>x</em> için düşey kesitin uzunluğu <em>f</em>(<em>x</em>) &#8722; "
    "<em>g</em>(<em>x</em>)'tir; bu uzunlukların <em>a</em>'dan <em>b</em>'ye integrali aradaki bölgenin "
    "alanını verir. Sınırlar, iki eğrinin kesim noktalarıdır.",
    aria="Iki egri arasindaki bolge ve dusey kesit uzunlugu f(x) eksi g(x)")

# ============================================================ donel-hacim
def f_rev(x):
    return 0.42 + 0.52 * math.sin(0.85 * x) + 0.12 * x


AV, BV = 0.3, 3.4
p = Plot(48, 22, 306, 206, (-0.2, 3.9), (-1.35, 1.35))
p.origin_axes("x", "y")
p.polygon([(AV + (BV - AV) * k / 140, f_rev(AV + (BV - AV) * k / 140)) for k in range(141)]
          + [(BV - (BV - AV) * k / 140, -f_rev(BV - (BV - AV) * k / 140)) for k in range(141)],
          THEORY, 0.12)
curve(p, f_rev, AV, BV, THEORY, 2.0)
curve(p, lambda x: -f_rev(x), AV, BV, THEORY, 1.4, 200, None, 0.45)
for xc in (1.05, 2.25):
    r = f_rev(xc)
    p.add('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s" fill-opacity="0.16" stroke="%s" stroke-width="1.3"/>'
          % (p.X(xc), p.Y(0), 7.5, abs(p.Y(r) - p.Y(0)), PRACTICE, PRACTICE))
    p.line([(xc, 0), (xc, r)], PRACTICE, 1.4)
    p.label(xc, r / 2, "f(x)", 5, 4, PRACTICE, 10, "start", False, True)
p.add('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="none" stroke="%s" stroke-width="1.2" opacity="0.6"/>'
      % (p.X(BV), p.Y(0), 7.5, abs(p.Y(f_rev(BV)) - p.Y(0)), THEORY))
guide(p, [(AV, -f_rev(AV)), (AV, f_rev(AV))], TEXT, 0.4)
p.label(AV, 0, "a", 0, 16, TEXT, 11, "middle", True, True)
p.label(BV, 0, "b", 4, 16, TEXT, 11, "middle", True, True)
p.label(0.95, -1.05, "V = &#960; " + INT_S + " f " + sups("2") + "(x) dx", 0, 0, PRACTICE, 11.5, "middle", False, True)
OUT["donel-hacim"] = figure(
    400, 258, [p],
    "Dönel cisim: <em>y</em> = <em>f</em>(<em>x</em>) eğrisinin [<em>a</em>, <em>b</em>] parçası <em>x</em> "
    "ekseni çevresinde döndürülür. <em>x</em> noktasındaki dik kesit, yarıçapı <em>f</em>(<em>x</em>) olan bir "
    "dairedir; alanı &#960;<em>f</em><sup>2</sup>(<em>x</em>)'tir. Bu alanların integrali hacmi verir.",
    aria="Egrinin x ekseni cevresinde donmesiyle olusan cisim ve yaricapi f(x) olan dairesel kesitler")

# ============================================================ yay-uzunlugu
def f_arc(x):
    return 0.50 + 0.95 * math.sin(1.15 * x) + 0.06 * x * x


AL, BL = 0.2, 3.4
p1 = Plot(44, 28, 226, 192, (-0.2, 3.75), (0.0, 1.95))
p1.origin_axes("x", "y")
panel_title(p1, "Kırık çizgiyle yaklaşım")
NODES = [AL + (BL - AL) * k / 4 for k in range(5)]
p1.line([(x, f_arc(x)) for x in NODES], PRACTICE, 1.9)
curve(p1, f_arc, AL, BL, THEORY, 2.0)
for x in NODES:
    dot(p1, (x, f_arc(x)), PRACTICE, 3.2)
p1.label(2.9, f_arc(2.9), "y = f(x)", 8, 6, THEORY, 11.5, "start", True, True)

p2 = Plot(322, 28, 226, 192, (-0.2, 3.75), (0.0, 1.95))
p2.origin_axes("x", "y")
panel_title(p2, "Bir parçanın uzunluğu")
U, V = NODES[2], NODES[3]  # the chord whose length is analysed
curve(p2, f_arc, AL, BL, THEORY, 2.0, 200, None, 0.35)
curve(p2, f_arc, U, V, THEORY, 2.2)
p2.line([(U, f_arc(U)), (V, f_arc(V))], PRACTICE, 2.0)
p2.line([(U, f_arc(U)), (V, f_arc(U))], BASE, 1.5, "4 3")
p2.line([(V, f_arc(U)), (V, f_arc(V))], BASE, 1.5, "4 3")
dot(p2, (U, f_arc(U)), PRACTICE, 3.4)
dot(p2, (V, f_arc(V)), PRACTICE, 3.4)
p2.label((U + V) / 2, f_arc(U), "&#916;x", 0, -7, BASE, 10.5, "middle", False, True)
p2.label(V, (f_arc(U) + f_arc(V)) / 2, "&#916;y", 7, 4, BASE, 10.5, "start", False, True)
p2.label((U + V) / 2, (f_arc(U) + f_arc(V)) / 2, "&#8730;(&#916;x)" + sups("2") + "+(&#916;y)" + sups("2"),
         -6, 17, PRACTICE, 10, "end", False, True)
OUT["yay-uzunlugu"] = figure(
    560, 244, [p1, p2],
    "Yay uzunluğu, eğriye içten çizilen kırık çizgilerin uzunluklarının limitidir. Bir parçanın uzunluğu "
    "Pisagor'dan &#8730;((&#916;<em>x</em>)<sup>2</sup>+(&#916;<em>y</em>)<sup>2</sup>) = "
    "&#8730;(1+(&#916;<em>y</em>/&#916;<em>x</em>)<sup>2</sup>)&#183;&#916;<em>x</em> olarak yazılır; ortalama "
    "değer teoremiyle &#916;<em>y</em>/&#916;<em>x</em> = <em>f</em>&#8242;(<em>c</em>) alınır ve toplam bir "
    "Riemann toplamına dönüşür.",
    aria="Egriye ictean cizilen kirik cizgi ve bir parcanin Pisagor ile hesaplanan uzunlugu")

# ============================================================ kismi-toplamlar
S_INF = math.pi ** 2 / 6.0
part = []
acc = 0.0
for k in range(1, 15):
    acc += 1.0 / (k * k)
    part.append(acc)
p1 = Plot(46, 30, 224, 192, (0, 15), (0.8, 1.85))
p1.axes((1, 5, 10, 14), (1.0, 1.4, 1.8), "n", "s" + subs("n"), yfmt=tfmt)
panel_title(p1, SUM_S + " 1/k" + sups("2") + " yakınsar", THEORY)
guide(p1, [(0, S_INF), (15, S_INF)], PRACTICE, 0.7)
p1.points([(k + 1, v) for k, v in enumerate(part)], THEORY, 3.2)
p1.label(14.4, S_INF, "s = &#960;" + sups("2") + "/6", -4, -8, PRACTICE, 10.5, "end", False, True)

harm = []
acc = 0.0
for k in range(1, 15):
    acc += 1.0 / k
    harm.append(acc)
p2 = Plot(324, 30, 224, 192, (0, 15), (0.8, 3.6))
p2.axes((1, 5, 10, 14), (1, 2, 3), "n", "s" + subs("n"))
panel_title(p2, SUM_S + " 1/k ıraksar", PRACTICE)
p2.points([(k + 1, v) for k, v in enumerate(harm)], PRACTICE, 3.2)
p2.label(8.2, 2.35, "s" + subs("n") + " " + ARROW + " +" + INF, 0, 0, PRACTICE, 10.5, "middle", False, True)
p2.label(8.2, 2.02, "(çok yavaş)", 0, 0, PRACTICE, 10, "middle", False, True)
OUT["kismi-toplamlar"] = figure(
    560, 244, [p1, p2],
    "Bir serinin yakınsaklığı, kısmi toplamlar dizisinin yakınsaklığıdır. Solda &#8721;1/<em>k</em><sup>2</sup>: "
    "kısmi toplamlar artan ve üstten sınırlı olduğundan &#960;<sup>2</sup>/6'ya yakınsar. Sağda harmonik seri: "
    "genel terim sıfıra gitse de kısmi toplamlar sınırsızdır. Genel terimin sıfıra gitmesi <em>gerek</em> "
    "koşuldur, <em>yeter</em> değil.",
    aria="Solda yakinsak serinin kismi toplamlari bir limite yaklasiyor, sagda harmonik serininkiler sinirsiz")

# ============================================================ alterne-seri
alt = []
acc = 0.0
for k in range(1, 13):
    acc += (-1.0) ** (k + 1) / k
    alt.append(acc)
LN2 = math.log(2.0)
p = Plot(48, 28, 306, 198, (0, 13), (0.35, 1.08))
p.axes((1, 3, 5, 7, 9, 11), (0.5, 0.7, 0.9), "n", "s" + subs("n"), yfmt=tfmt)
guide(p, [(0, LN2), (13, LN2)], BASE, 0.75)
p.line([(k + 1, v) for k, v in enumerate(alt)], TEXT, 1.1, "3 3", 0.45)
p.points([(k + 1, v) for k, v in enumerate(alt) if k % 2 == 0], PRACTICE, 3.4)
p.points([(k + 1, v) for k, v in enumerate(alt) if k % 2 == 1], THEORY, 3.4)
p.label(12.6, LN2, "s = ln 2", -4, -8, BASE, 10.5, "end", False, True)
p.label(1, alt[0], "tek indisli: azalan", 8, 2, PRACTICE, 10.5, "start", False, True)
p.label(2, alt[1], "çift indisli: artan", 8, 12, THEORY, 10.5, "start", False, True)
OUT["alterne-seri"] = figure(
    400, 250, [p],
    "Alterne harmonik seri &#8721;(&#8722;1)<sup><em>k</em>+1</sup>/<em>k</em>. Tek indisli kısmi toplamlar "
    "azalarak, çift indisliler artarak ilerler; her adımda aradaki uzaklık <em>a</em><sub><em>n</em></sub>'e "
    "eşittir. İç içe aralıklar limiti sıkıştırır: seri ln 2'ye yakınsar ve <em>n</em>. adımdaki hata "
    "<em>a</em><sub><em>n</em>+1</sub>'i geçmez.",
    aria="Alterne serinin tek ve cift indisli kismi toplamlari limiti ic ice sikistiriyor")

# ============================================================ taylor-yaklasimi
def T(n, x):
    t, term = 0.0, x
    k = 1
    while k <= n:
        if k % 2 == 1:
            t += term
        term = -term * x * x / ((k + 1) * (k + 2))
        k += 2
    return t


XT_MAX = 6.6
p = Plot(48, 26, 306, 202, (-0.45, XT_MAX + 0.35), (-2.4, 2.4))
p.origin_axes("x", "y", xticks=(math.pi, 2 * math.pi), yticks=(-2, -1, 1, 2),
              xfmt=lambda v: "&#960;" if v > 3 and v < 4 else "2&#960;")
for n, col, op in ((1, PRACTICE, 0.5), (3, PRACTICE, 0.85), (5, THEORY, 0.9), (7, BASE, 1.0)):
    xs = [-0.35 + (XT_MAX + 0.6) * k / 300 for k in range(301)]
    pts = [(x, T(n, x)) for x in xs if -2.32 < T(n, x) < 2.32]
    p.line(pts, col, 1.6, None, op)
    # label the curve just before it leaves the band
    xl, yl = pts[-1]
    p.label(xl, yl, "T" + subs(str(n)), -6, -6 if yl > 0 else 14, col, 10.5, "end", False, True)
curve(p, math.sin, -0.35, XT_MAX + 0.25, TEXT, 2.3, 300)
p.label(4.75, math.sin(4.75), "y = sin x", 0, 18, TEXT, 11.5, "middle", True, True)
OUT["taylor-yaklasimi"] = figure(
    400, 254, [p],
    "sin <em>x</em>'in sıfır merkezli Taylor polinomları. Derece büyüdükçe yaklaşım orijinden daha uzağa kadar "
    "iyi kalır; her <em>T</em><sub><em>n</em></sub> sonlu bir polinom olduğundan yeterince uzakta eninde "
    "sonunda eğriyi terk eder. Lagrange kalanı, sabit bir aralıkta hatanın nasıl küçüldüğünü sayısal olarak "
    "kestirmeyi sağlar.",
    aria="Sinus fonksiyonu ve derecesi artan Taylor polinomlari")

# ============================================================ yakinsaklik-araligi
p = Plot(40, 60, 320, 92, (-1.35, 1.35), (-1, 1))
p.arrow((-1.3, 0), (1.32, 0), TEXT, 1.1, 7.0, opacity=0.55)
p.polygon([(-1, -0.34), (1, -0.34), (1, 0.34), (-1, 0.34)], THEORY, 0.14)
p.line([(-1, 0), (1, 0)], THEORY, 4.5, None, 0.55)
for x in (-1, 1):
    hollow(p, (x, 0), THEORY, 4.6, 1.8)
dot(p, (0, 0), PRACTICE, 4.4)
p.label(0, 0, "x" + subs("0"), 0, 18, PRACTICE, 11.5, "middle", True, True)
p.label(-1, 0, "x" + subs("0") + MINUS_S + "R", 0, 18, THEORY, 11, "middle", False, True)
p.label(1, 0, "x" + subs("0") + "+R", 0, 18, THEORY, 11, "middle", False, True)
p.label(0, 0, "mutlak yakınsar", 0, -14, THEORY, 11, "middle", False, True)
p.label(-1.18, 0, "ıraksar", 0, -14, PRACTICE, 11, "middle", False, True)
p.label(1.18, 0, "ıraksar", 0, -14, PRACTICE, 11, "middle", False, True)
p.label(-1, 0, "?", 0, 34, TEXT, 12, "middle", True)
p.label(1, 0, "?", 0, 34, TEXT, 12, "middle", True)
p.text_px(200, 178, "uç noktalar tek tek incelenir", TEXT, 10.5, "middle", False, True)
OUT["yakinsaklik-araligi"] = figure(
    400, 196, [p],
    "Bir kuvvet serisinin yakınsaklık kümesi her zaman bu resme benzer: merkezden <em>R</em> uzaklığa kadar "
    "mutlak yakınsaklık, dışında ıraksaklık. Yarıçapı Cauchy&#8211;Hadamard formülü verir; iki uç noktada ne "
    "olduğu ise formülden okunamaz, her biri ayrı ayrı incelenmelidir.",
    aria="Sayi dogrusu uzerinde yakinsaklik yaricapi: icte mutlak yakinsaklik, disda iraksaklik, uclarda soru isareti")

# ============================================================ karsilastirma-testi
p = Plot(46, 28, 308, 198, (0, 11), (0, 1.15))
p.axes((1, 3, 5, 7, 9), (0.25, 0.5, 0.75, 1.0), "k", "", yfmt=tfmt)
for k in range(1, 11):
    bk = 1.05 / (k ** 1.35)
    ak = bk * (0.42 + 0.24 * math.sin(1.7 * k))
    p.add('<rect x="%.1f" y="%.1f" width="9" height="%.1f" fill="%s" fill-opacity="0.22" stroke="%s" stroke-width="0.9"/>'
          % (p.X(k) - 4.5, p.Y(bk), abs(p.Y(0) - p.Y(bk)), PRACTICE, PRACTICE))
    p.add('<rect x="%.1f" y="%.1f" width="9" height="%.1f" fill="%s" fill-opacity="0.55" stroke="%s" stroke-width="0.9"/>'
          % (p.X(k) - 4.5, p.Y(ak), abs(p.Y(0) - p.Y(ak)), THEORY, THEORY))
p.label(7.2, 0.95, "b" + subs("k") + " (yakınsak)", 0, 0, PRACTICE, 11, "middle", False, True)
p.label(7.2, 0.78, "a" + subs("k") + " " + LEQ_S + " b" + subs("k"), 0, 0, THEORY, 11, "middle", False, True)
OUT["karsilastirma-testi"] = figure(
    400, 250, [p],
    "Karşılaştırma testi: terimleri 0 &#8804; <em>a</em><sub><em>k</em></sub> &#8804; "
    "<em>b</em><sub><em>k</em></sub> ile sıkıştırılmış bir seri, üstteki seri yakınsıyorsa yakınsar. Koyu "
    "sütunlar açık sütunların içinde kaldığından &#8721;<em>a</em><sub><em>k</em></sub>'nın kısmi toplamları "
    "&#8721;<em>b</em><sub><em>k</em></sub>'nınkileri aşamaz; artan ve üstten sınırlı dizi yakınsaktır.",
    aria="Her k icin a_k sutunu b_k sutununun icinde kaliyor")

# ============================================================ birinci-turev-testi-isaret-degisimi
# ============================================================ birinci-turev-testi-isaret-degisimi
# The first-derivative test read off a sign strip: f' turns + -> - at a strict
# local maximum and - -> + at a strict local minimum, while a critical point
# where the sign does not change is no extremum at all.

X1_FT, X2_FT, X3_FT = 1.30, 2.90, 4.40      # local max, flat point, local min
XA_FT, XB_FT = 0.30, 5.40                   # the piece of the curve that is drawn


def fp_ft(x):
    """f'(x): simple zeros at X1 and X3, a double zero at X2, bounded shape."""
    d = (x - X2_FT) ** 2
    return (x - X1_FT) * (x - X3_FT) * d / (d + 0.6)


N_FT = 900
H_FT = (XB_FT - XA_FT) / N_FT
CUM_FT = [0.0]
for _k in range(N_FT):
    _a = XA_FT + _k * H_FT
    _b = _a + H_FT
    CUM_FT.append(CUM_FT[-1] + (fp_ft(_a) + 4 * fp_ft(0.5 * (_a + _b)) + fp_ft(_b)) * H_FT / 6)
LO_FT, HI_FT = min(CUM_FT), max(CUM_FT)


def f_ft(x):
    """The antiderivative of fp_ft, rescaled into a comfortable band of the panel."""
    t = (min(max(x, XA_FT), XB_FT) - XA_FT) / H_FT
    k = min(int(t), N_FT - 1)
    u = t - k
    v = CUM_FT[k] + (CUM_FT[k + 1] - CUM_FT[k]) * u
    return 0.13 + 0.84 * (v - LO_FT) / (HI_FT - LO_FT)


XR_FT = (0.10, 5.80)
FI_FT = '<tspan font-style="italic">f</tspan>' + PRIME        # italic f with a prime
POS_FT = FI_FT + " &gt; 0"
NEG_FT = FI_FT + " &lt; 0"

# bands of constant sign: (left, right, colour, is f' positive)
BANDS_FT = [(XA_FT, X1_FT, BASE, True),
            (X1_FT, X2_FT, PRACTICE, False),
            (X2_FT, X3_FT, PRACTICE, False),
            (X3_FT, XB_FT, BASE, True)]

STRIP_TOP, STRIP_BOT = 212.5, 249.5          # pixel edges of the sign ribbon
ZERO_CY = 231.0                              # centre of the "0" markers
LINK_END = 256.0                             # where the dashed links stop

p = Plot(54, 24, 340, 170, XR_FT, (-0.07, 1.12))
q = Plot(54, 210, 340, 42, XR_FT, (0.0, 1.0))

# ---- upper panel: the graph of f -----------------------------------------
for xa, xb, col, _pos in BANDS_FT:
    rect(p, xa, xb, -0.07, 1.12, col, 0.09)

p.arrow((0.10, 0), (5.76, 0), TEXT, 1.1, 7.5, None, 0.5)
p.label(5.76, 0, "x", 7, 4, TEXT, 11.5, "start", False, True)
for xc in (X1_FT, X2_FT, X3_FT):
    p.add(f'<line x1="{p.X(xc):.1f}" y1="{p.Y(0) - 3.5:.1f}" x2="{p.X(xc):.1f}" y2="{p.Y(0) + 3.5:.1f}" '
          f'stroke="{TEXT}" stroke-width="1.1" opacity="0.6"/>')

curve(p, f_ft, XA_FT, XB_FT, THEORY, 2.3, 320)
for xc in (X1_FT, X2_FT, X3_FT):
    yc = f_ft(xc)
    p.line([(xc - 0.36, yc), (xc + 0.36, yc)], TEXT, 1.7, None, 0.8)
    dot(p, (xc, yc), TEXT, 4.0)

p.label(XB_FT, f_ft(XB_FT), "y = f(x)", -8, -9, THEORY, 11.5, "end", True, True)

# the case that fails: horizontal tangent, but no change of sign
p.text_px(p.X(X2_FT), 46, "yatay teğet var,", TEXT, 10, "middle")
p.text_px(p.X(X2_FT), 60, "ama işaret değişmiyor", TEXT, 10, "middle")
p.add(f'<line x1="{p.X(X2_FT):.1f}" y1="68" x2="{p.X(X2_FT):.1f}" y2="99" stroke="{TEXT}" '
      f'stroke-width="1.2" opacity="0.7"/>')
p.add(f'<polygon points="{p.X(X2_FT):.1f},105 {p.X(X2_FT) - 3.3:.1f},97 {p.X(X2_FT) + 3.3:.1f},97" '
      f'fill="{TEXT}" opacity="0.7"/>')

# ---- lower panel: the sign ribbon of f' -----------------------------------
for xa, xb, col, _pos in BANDS_FT:
    rect(q, xa, xb, 0.06, 0.94, col, 0.20)
q.add(f'<line x1="{q.X(XA_FT):.1f}" y1="{STRIP_TOP:.1f}" x2="{q.X(XB_FT):.1f}" y2="{STRIP_TOP:.1f}" '
      f'stroke="{TEXT}" stroke-width="0.9" opacity="0.3"/>')
q.add(f'<line x1="{q.X(XA_FT):.1f}" y1="{STRIP_BOT:.1f}" x2="{q.X(XB_FT):.1f}" y2="{STRIP_BOT:.1f}" '
      f'stroke="{TEXT}" stroke-width="0.9" opacity="0.3"/>')

for xc in (X1_FT, X2_FT, X3_FT):                       # links between the two panels
    q.add(f'<line x1="{q.X(xc):.1f}" y1="{p.Y(f_ft(xc)):.1f}" x2="{q.X(xc):.1f}" y2="{LINK_END:.1f}" '
          f'stroke="{TEXT}" stroke-width="1" stroke-dasharray="4 3" opacity="0.5"/>')

for i, (xa, xb, col, pos) in enumerate(BANDS_FT):
    xc = 0.5 * (xa + xb)
    q.text_px(q.X(xc), 226, POS_FT if pos else NEG_FT, col, 10, "middle", True)
    lo, hi = (0.16, 0.36) if pos else (0.36, 0.16)
    q.arrow((xc - 0.17, lo), (xc + 0.17, hi), col, 1.8, 6.5)

for xc in (X1_FT, X2_FT, X3_FT):                       # f' = 0 at the critical points
    q.add(f'<circle cx="{q.X(xc):.1f}" cy="{ZERO_CY:.1f}" r="9.5" fill="{BG}" stroke="{TEXT}" stroke-width="1.1"/>')
    q.text_px(q.X(xc), ZERO_CY + 4.2, "0", TEXT, 11.5, "middle", True)

for xc, tag in ((X1_FT, "1"), (X2_FT, "2"), (X3_FT, "3")):
    q.text_px(q.X(xc) + 6, 200, "x" + subs(tag), TEXT, 11, "start", False, True)

for xc, l1, l2 in ((X1_FT, "yerel", "maksimum"),
                   (X2_FT, "ekstremum", "değil"),
                   (X3_FT, "yerel", "minimum")):
    q.text_px(q.X(xc), 269, l1, TEXT, 10, "middle", True)
    q.text_px(q.X(xc), 282, l2, TEXT, 10, "middle", True)

OUT["birinci-turev-testi-isaret-degisimi"] = figure(
    424, 292, [p, q],
    "Üstte <em>f</em>'nin grafiği, altta aynı <em>x</em> ekseni üzerinde hizalanmış "
    "<em>f</em>&#8242; işaret şeridi vardır: şeridin <em>f</em>&#8242; &gt; 0 yazan aralıklarında ok "
    "yukarı bakar ve <em>f</em> kesin artar, <em>f</em>&#8242; &lt; 0 yazan aralıklarında ok aşağı bakar "
    "ve <em>f</em> kesin azalır. <em>x</em><sub>1</sub>'de işaret + iken &#8722; olur, bu yüzden orada "
    "kesin yerel maksimum; <em>x</em><sub>3</sub>'te &#8722; iken + olur, bu yüzden kesin yerel minimum "
    "vardır. <em>x</em><sub>2</sub>'de teğet yataydır, yani <em>f</em>&#8242;(<em>x</em><sub>2</sub>) = 0 "
    "olur; ama <em>f</em>&#8242; bu noktanın iki yanında da negatif kaldığından işaret değişmez ve "
    "<em>f</em>, <em>x</em><sub>2</sub>'nin bir komşuluğunda kesin azalmayı sürdürür. Testin okuduğu "
    "şey kritik noktanın kendisi değil, çevresindeki işaret değişimidir.",
    aria="f nin grafigi ve altinda f turevinin isaret seridi; iki isaret degisimli kritik nokta ve bir degisimsiz kritik nokta")

# ============================================================ buyume-hizlari-karsilastirma
# ============================================================ buyume-hizlari-karsilastirma
# Four growth rates on one pair of axes: ln x, x, x^2, 2^x.
LN = lambda x: math.log(x)
SQ = lambda x: x * x
EX = lambda x: 2.0 ** x

p = Plot(48, 26, 306, 206, (-0.3, 6.4), (0, 30))
p.origin_axes("x", "y", (1, 2, 3, 4, 5, 6), (5, 10, 15, 20, 25, 30))

# the last crossing of any two of the curves: 2^4 = 4^2 = 16
guide(p, [(4, 0), (4, 16)], TEXT, 0.38)

clipped(p, LN, 0.0, 6.35, TEXT, 2.0)
clipped(p, lambda x: x, 0.0, 6.35, BASE, 2.0)
clipped(p, SQ, 0.0, 6.35, THEORY, 2.0)
clipped(p, EX, 0.0, 6.35, PRACTICE, 2.4)

dot(p, (4, 16), PRACTICE, 4.2)
p.label(4, 16, "son kesişim", -13, -9, PRACTICE, 10.5, "end", False, True)

p.label(6.35, LN(6.35), "y = ln x", 0, -8, TEXT, 11, "end", True, True)
p.label(6.35, 6.35, "y = x", 0, -9, BASE, 11, "end", True, True)
p.label(4.472, 20, "y = x" + sups("2"), 15, 4, THEORY, 11, "start", True, True)
p.label(4.755, 27, "y = 2" + sups("x"), -10, 4, PRACTICE, 11, "end", True, True)

CHAIN = ('<tspan fill="%s">ln x</tspan> &lt; <tspan fill="%s">x</tspan> &lt; '
         '<tspan fill="%s">x%s</tspan> &lt; <tspan fill="%s">2%s</tspan>'
         % (TEXT, BASE, THEORY, sups("2"), PRACTICE, sups("x")))
p.label(0.35, 27.0, "x &gt; 4 için", 0, 0, TEXT, 11, "start", False, True)
p.label(0.35, 24.2, CHAIN, 0, 0, TEXT, 11.5, "start", False, True)

OUT["buyume-hizlari-karsilastirma"] = figure(
    400, 260, [p],
    "Aynı eksende dört büyüme hızı: ln <em>x</em> neredeyse yatay kalırken <em>x</em>, "
    "<em>x</em><sup>2</sup> ve 2<sup><em>x</em></sup> sırayla dikleşir; son kesişim <em>x</em> = 4'te olur ve "
    "ondan sonra 2<sup><em>x</em></sup> hepsini geride bırakır. L'Hôpital kuralının en sık uygulaması bu "
    "sıralamayı ispatlamaktır: ln <em>x</em> &#8810; <em>x</em><sup><em>a</em></sup> &#8810; "
    "<em>b</em><sup><em>x</em></sup> (<em>a</em> &gt; 0, <em>b</em> &gt; 1); her oranın limiti sıfırdır.",
    aria="ln x, x, x kare ve 2 uzeri x egrileri ayni eksende; 2 uzeri x, x=4 sonrasi hepsinin ustunde")

# ============================================================ carpim-kurali-alan
# -*- coding: utf-8 -*-
# The product rule read off an area picture: a rectangle with sides f and g
# grows by Df horizontally and Dg vertically; the new area splits into three
# pieces, the corner one being of second order.

F0, DF = 0.78, 0.22
G0, DG = 0.62, 0.20
F1, G1 = F0 + DF, G0 + DG

DIM_Y = -0.10          # horizontal dimension line, below the rectangle
DIM_X = -0.10          # vertical dimension line, left of the rectangle
MID = "&#183;"

p = Plot(62, 22, 288, 236, (-0.40, 1.14), (-0.30, 1.16))

# ---- the four pieces ------------------------------------------------------
rect(p, 0, F0, 0, G0, TEXT, 0.08)                       # starting area, faint
rect(p, F0, F1, 0, G0, THEORY, 0.20)                    # g(x0)*Df
rect(p, 0, F0, G0, G1, BASE, 0.20)                      # f(x0)*Dg
rect(p, F0, F1, G0, G1, PRACTICE, 0.40)                 # Df*Dg

# ---- outlines -------------------------------------------------------------
p.line([(0, 0), (F0, 0), (F0, G0), (0, G0), (0, 0)], TEXT, 1.5, None, 0.70)
guide(p, [(F0, G0), (F0, G1)], TEXT, 0.45)
guide(p, [(F0, G0), (F1, G0)], TEXT, 0.45)
p.line([(0, 0), (F1, 0), (F1, G1), (0, G1), (0, 0)], TEXT, 1.7, None, 0.85)
p.line([(F0, G0), (F1, G0), (F1, G1), (F0, G1), (F0, G0)], PRACTICE, 1.6)

# ---- dimension lines ------------------------------------------------------
def dim_h(a, b, s, size=11):
    p.arrow((a, DIM_Y), (b, DIM_Y), TEXT, 1.1, 6.0, None, 0.8)
    p.arrow((b, DIM_Y), (a, DIM_Y), TEXT, 1.1, 6.0, None, 0.8)
    p.label((a + b) / 2, DIM_Y, s, 0, 15, TEXT, size, "middle", False, True)


def dim_v(a, b, s, size=11):
    p.arrow((DIM_X, a), (DIM_X, b), TEXT, 1.1, 6.0, None, 0.8)
    p.arrow((DIM_X, b), (DIM_X, a), TEXT, 1.1, 6.0, None, 0.8)
    p.label(DIM_X, (a + b) / 2, s, -8, 4, TEXT, size, "end", False, True)


for x in (0, F0, F1):
    guide(p, [(x, 0), (x, DIM_Y - 0.045)], TEXT, 0.35)
for y in (0, G0, G1):
    guide(p, [(0, y), (DIM_X - 0.045, y)], TEXT, 0.35)
dim_h(0, F0, "f(x" + subs("0") + ")")
dim_h(F0, F1, "&#916;f")
dim_v(0, G0, "g(x" + subs("0") + ")")
dim_v(G0, G1, "&#916;g")

# ---- what each piece is ---------------------------------------------------
p.label(F0 / 2, 0.35, "f(x" + subs("0") + ")" + MID + "g(x" + subs("0") + ")",
        0, 0, TEXT, 12, "middle", False, True)
p.label(F0 / 2, 0.26, "başlangıç alanı", 0, 0, TEXT, 9.5, "middle", False, True)
p.label(F0 / 2, (G0 + G1) / 2, "f(x" + subs("0") + ")" + MID + "&#916;g",
        0, 4, BASE, 10.5, "middle", False, True)
cx, cy = p.X((F0 + F1) / 2), p.Y(G0 / 2) + 4
p.add(f'<text x="{cx:.1f}" y="{cy:.1f}" fill="{THEORY}" font-size="10.5" text-anchor="middle" '
      f'font-style="italic" transform="rotate(-90 {cx:.1f} {cy:.1f})">'
      f'g(x{subs("0")}){MID}&#916;f</text>')
p.label((F0 + F1) / 2, (G0 + G1) / 2, "&#916;f" + MID + "&#916;g", 0, 4, TEXT, 10, "middle", False, True)
p.arrow(((F0 + F1) / 2, 0.985), ((F0 + F1) / 2, G1 + 0.025), PRACTICE, 1.3, 6.5)
p.label((F0 + F1) / 2, 1.02, "ikinci mertebeden", 0, 0, PRACTICE, 9.5, "middle", True, True)
p.label(0, 0.88, "büyük dikdörtgen: (fg)(x" + subs("0") + "+h)", 0, 0, TEXT, 10.5, "start", False, True)

OUT["carpim-kurali-alan"] = figure(
    400, 258, [p],
    "Çarpım, kenarları <em>f</em> ve <em>g</em> olan dikdörtgenin alanıdır. <em>x</em><sub>0</sub>'dan "
    "<em>x</em><sub>0</sub>+<em>h</em>'ye geçerken yatay kenar &#916;<em>f</em>, düşey kenar &#916;<em>g</em> "
    "kadar uzar; (<em>fg</em>)(<em>x</em><sub>0</sub>+<em>h</em>) &#8722; (<em>fg</em>)(<em>x</em><sub>0</sub>) "
    "farkı, eklenen üç parçanın toplamıdır: <em>g</em>(<em>x</em><sub>0</sub>)&#916;<em>f</em>, "
    "<em>f</em>(<em>x</em><sub>0</sub>)&#916;<em>g</em> ve köşedeki &#916;<em>f</em>&#916;<em>g</em>. "
    "<em>h</em>'ye bölünüp limit alındığında köşedeki küçük parça sıfıra gider ve geriye "
    "<em>f</em>&#8242;(<em>x</em><sub>0</sub>)<em>g</em>(<em>x</em><sub>0</sub>) + "
    "<em>f</em>(<em>x</em><sub>0</sub>)<em>g</em>&#8242;(<em>x</em><sub>0</sub>) kalır.",
    aria="Carpim kuralinin alan yorumu: kenarlari f ve g olan dikdortgen buyurken eklenen uc parca")

# ============================================================ cauchy-schwarz-parabol
# -*- coding: utf-8 -*-
# Cauchy-Schwarz through the discriminant of phi(t) = int (f + t g)^2.
# One upward parabola that never dips below the t axis, its tangent twin
# (the equality case) and the impossible one that cuts the axis twice.

PHI = "&#966;"          # phi
DELTA_CAP = "&#916;"    # capital delta
CDOT = "&#183;"

A_CS = 0.42             # leading coefficient A = int g^2 > 0
TSTAR = -1.1            # t* = -B/(2A)
H_POS = 0.85            # vertex height C - B^2/(4A) > 0
H_NEG = -0.80           # vertex height of the impossible parabola
T0, T1 = -3.15, 0.95    # drawn range, symmetric about t*
ROOT = math.sqrt(-H_NEG / A_CS)


def para(h):
    return lambda t: A_CS * (t - TSTAR) ** 2 + h


p = Plot(48, 48, 250, 190, (-3.5, 1.4), (-1.2, 3.1))
panel_title(p, PHI + "(t) = " + INT_S + "(f + t g)" + sups("2")
            + " = At" + sups("2") + " + Bt + C", TEXT, 11)
p.origin_axes("t", PHI + "(t)")

# the part of the impossible parabola that lies below the axis
lens = [(TSTAR - ROOT + 2 * ROOT * k / 60, para(H_NEG)(TSTAR - ROOT + 2 * ROOT * k / 60))
        for k in range(61)]
p.polygon(lens, PRACTICE, 0.15, "none")

# three vertical translates: only the height of the vertex changes
curve(p, para(H_NEG), T0, T1, PRACTICE, 1.7, 200, "5 4", 0.85)
curve(p, para(0.0), T0, T1, BASE, 1.9)
curve(p, para(H_POS), T0, T1, THEORY, 2.2)

guide(p, [(TSTAR, 0.0), (TSTAR, 1.58)], TEXT, 0.45)
dot(p, (TSTAR - ROOT, 0.0), PRACTICE, 3.4)
dot(p, (TSTAR + ROOT, 0.0), PRACTICE, 3.4)
dot(p, (TSTAR, 0.0), BASE, 4.2)
dot(p, (TSTAR, H_POS), THEORY, 4.4)

p.label(TSTAR, 2.05, "t* = " + MINUS_S + "B/(2A)", 0, 0, THEORY, 10.5, "middle", True, True)
p.label(TSTAR, 1.70, PHI + "(t*) = C " + MINUS_S + " B" + sups("2") + "/(4A) " + GEQ_S + " 0",
        0, 0, THEORY, 10, "middle", False, True)
p.label(TSTAR, 0.0, "t*", -8, -8, TEXT, 11, "end", True, True)
p.label(TSTAR, -0.42, PHI + " &lt; 0", 0, 0, PRACTICE, 10, "middle", False, True)

# ---- annotation column ----------------------------------------------------
q = Plot(312, 48, 236, 190, (0, 1), (0, 1))
q.add(f'<rect x="316" y="48" width="230" height="44" rx="6" fill="{BASE}" '
      f'fill-opacity="0.09" stroke="{BASE}" stroke-opacity="0.6" stroke-width="1.2"/>')
q.text_px(431, 67, DELTA_CAP + " = B" + sups("2") + " " + MINUS_S + " 4AC " + LEQ_S + " 0",
          BASE, 12, "middle", True)
q.text_px(431, 84, "(" + INT_S + " f g)" + sups("2") + " " + LEQ_S + " ("
          + INT_S + " f" + sups("2") + ")(" + INT_S + " g" + sups("2") + ")",
          TEXT, 10.5, "middle")

ROWS = ((118, THEORY, None,
         DELTA_CAP + " &lt; 0: parabol ekseni kesmez",
         ("en alçak değeri bile pozitif",)),
        (162, BASE, None,
         DELTA_CAP + " = 0: parabol eksene teğet",
         (PHI + "(t*) = 0, yani f + t* g = 0", "f ile g doğrusal bağımlı: eşitlik")),
        (221, PRACTICE, "5 4",
         DELTA_CAP + " &gt; 0: iki kök, arada " + PHI + " &lt; 0",
         ("olanaksız, çünkü " + PHI + "(t) " + GEQ_S + " 0",)))

for y, col, dash, head, tail in ROWS:
    da = f' stroke-dasharray="{dash}"' if dash else ""
    q.add(f'<line x1="316" y1="{y - 4}" x2="340" y2="{y - 4}" stroke="{col}" '
          f'stroke-width="2.4" stroke-linecap="round"{da}/>')
    q.text_px(348, y, head, col, 10.5, "start", True)
    for i, s in enumerate(tail):
        q.text_px(348, y + 15 + 15 * i, s, TEXT, 9.8, "start")

OUT["cauchy-schwarz-parabol"] = figure(
    560, 252, [p, q],
    "İkinci ispatın tamamı bu resimde durur. <em>&#966;</em>(<em>t</em>) = "
    "&#8747;<sub><em>a</em></sub><sup><em>b</em></sup>(<em>f</em> + <em>t</em><em>g</em>)<sup>2</sup> "
    "integrali <em>t</em>'nin ikinci dereceden bir polinomudur; <em>A</em> = &#8747;<em>g</em><sup>2</sup> "
    "&gt; 0 olduğundan yukarı açılan bir paraboldür ve integrali alınan fonksiyon negatif olmadığından "
    "hiçbir <em>t</em> için negatif değer alamaz. Bu yüzden parabolün <em>t</em> eksenine yapabileceği en "
    "fazla şey teğet olmaktır: ekseni iki noktada kesen soluk parabol (&#916; &gt; 0) olanaksızdır, yani "
    "&#916; = <em>B</em><sup>2</sup> &#8722; 4<em>AC</em> &#8804; 0 olmak zorundadır &#8212; bu da tam "
    "olarak (&#8747;<em>fg</em>)<sup>2</sup> &#8804; &#8747;<em>f</em><sup>2</sup>&#183;"
    "&#8747;<em>g</em><sup>2</sup> demektir. Teğetlik hâli (&#916; = 0) eşitlik hâline karşılık gelir: "
    "<em>f</em> + <em>t</em>*<em>g</em> özdeş sıfırdır, yani <em>f</em> ile <em>g</em> doğrusal bağımlıdır.",
    css_class=WIDE,
    aria="Yukari acilan parabol t ekseninin ustunde, tegetlik esitlik hali, ekseni kesen parabol olanaksiz")

# ============================================================ darboux-incelme
# -*- coding: utf-8 -*-
# Refinement: inserting one point x* into [x_{i-1}, x_i] replaces a single
# rectangle by two.  For the infima the two new heights cannot drop below m_i,
# so the lower sum can only grow; for the suprema they cannot rise above M_i,
# so the upper sum can only shrink.  The hatched strip is the change.

def f_ref(x):
    return 2.6 * (x ** 3 / 3.0 - 1.2 * x * x + 0.95 * x) + 0.95


XL, XS, XR = 0.0, 1.3, 2.4          # x_{i-1},  x*,  x_i


def ext_ref(u, v, want_max):
    vals = [f_ref(u + (v - u) * k / 400.0) for k in range(401)]
    return max(vals) if want_max else min(vals)


M_LO = ext_ref(XL, XR, False)        # m_i
M_HI = ext_ref(XL, XR, True)         # M_i
T1_LO, T2_LO = ext_ref(XL, XS, False), ext_ref(XS, XR, False)   # t1, t2
T1_HI, T2_HI = ext_ref(XL, XS, True), ext_ref(XS, XR, True)     # T1, T2


def hatch(q, xa, xb, ya, yb, color=BASE, step=8.0, width=0.85, opacity=0.55):
    """Diagonal hatching clipped to the data rectangle [xa,xb] x [ya,yb]."""
    px0, px1 = q.X(xa), q.X(xb)
    ptop, pbot = q.Y(yb), q.Y(ya)
    segs = []
    c, cmax = px0 - pbot, px1 - ptop
    while c <= cmax:
        lo, hi = max(ptop, px0 - c), min(pbot, px1 - c)
        if hi - lo > 1.5:
            segs.append("M%.1f,%.1f L%.1f,%.1f" % (lo + c, lo, hi + c, hi))
        c += step
    if segs:
        q.add('<path d="%s" fill="none" stroke="%s" stroke-width="%s" opacity="%s"/>'
              % (" ".join(segs), color, width, opacity))


def badge(q, x, y, lines, color, size=9.5):
    """Short caption on an opaque plate, so it stays readable over the hatching."""
    w = 0.56 * size * max(len(t) for t in lines) + 11
    lh = size * 1.3
    h = lh * len(lines) + 6
    cx, cy = q.X(x), q.Y(y)
    q.add('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="3.5" fill="%s" opacity="0.88"/>'
          % (cx - w / 2, cy - h / 2, w, h, BG))
    for i, t in enumerate(lines):
        q.text_px(cx, cy - (len(lines) - 1) * lh / 2 + i * lh + size * 0.35,
                  t, color, size, "middle", True)


STAR = "x" + sups("*")
SUB_I1 = "x" + subs("i" + MINUS_S + "1")
SUB_I = "x" + subs("i")

panels = []
for want_max in (False, True):
    col = PRACTICE if want_max else THEORY
    base_h = M_HI if want_max else M_LO                  # the height P uses
    h1 = T1_HI if want_max else T1_LO                    # left piece under Q
    h2 = T2_HI if want_max else T2_LO                    # right piece under Q
    q = Plot(342 if want_max else 56, 32, 206, 186, (-0.45, 2.75), (0.0, 1.82))
    q.axes((), ())
    panel_title(q, "Üst toplam azalır" if want_max else "Alt toplam artar", col)

    # the two rectangles of Q
    rect(q, XL, XS, 0, h1, col, 0.17, col, 1.3)
    rect(q, XS, XR, 0, h2, col, 0.17, col, 1.3)

    # the strip by which Q differs from P
    if want_max:
        sx0, sx1, sy0, sy1 = XS, XR, h2, base_h
    else:
        sx0, sx1, sy0, sy1 = XL, XS, base_h, h1
    rect(q, sx0, sx1, sy0, sy1, BASE, 0.16)
    hatch(q, sx0, sx1, sy0, sy1, BASE)

    # the level P works with: dashed wherever no rectangle edge already draws it
    guide(q, [(-0.42, base_h), (XL if want_max else XS, base_h)], TEXT, 0.6)
    if want_max:
        guide(q, [(XS, base_h), (XR, base_h)], TEXT, 0.6)

    # the newly inserted cut
    q.line([(XS, 0), (XS, max(h1, h2))], BASE, 1.8)

    curve(q, f_ref, XL, XR, TEXT, 2.0)
    dot(q, (XS if not want_max else 0.5, h1), col, 3.0)
    dot(q, (1.9 if not want_max else XR, h2), col, 3.0)

    # axis ticks
    for x in (XL, XS, XR):
        q.line([(x, 0), (x, -0.045)], TEXT, 1.0, None, 0.6)
    q.label(XL, 0, SUB_I1, 0, 17, TEXT, 10.5, "middle", False, True)
    q.label(XS, 0, STAR, 0, 17, BASE, 11.5, "middle", True, True)
    q.label(XR, 0, SUB_I, 0, 17, TEXT, 10.5, "middle", False, True)

    # heights
    q.label(-0.45, base_h, ("M" if want_max else "m") + subs("i"),
            -7, 4, TEXT, 11, "end", False, True)
    if want_max:
        q.label(0.62, 0.40, "T" + subs("1") + " = M" + subs("i"), 0, 0, col, 10.5, "middle", False, True)
        q.label(1.42, h2, "T" + subs("2"), 0, 15, col, 11, "start", False, True)
    else:
        q.label(0.10, h1, "t" + subs("1"), 0, -7, col, 11, "start", False, True)
        q.label(1.85, 0.13, "t" + subs("2") + " = m" + subs("i"), 0, 0, col, 10.5, "middle", False, True)

    badge(q, (sx0 + sx1) / 2, (sy0 + sy1) / 2,
          ["kaybedilen" if want_max else "kazanılan", "alan"], BASE)
    q.label(0.95, 1.72, "y = f(x)", 0, 0, TEXT, 11, "middle", False, True)
    q.text_px(q.x0 + q.w / 2, q.y0 + q.h + 40,
              ("U(P, f) " + MINUS_S + " U(Q, f) " + GEQ_S + " 0") if want_max
              else ("L(Q, f) " + MINUS_S + " L(P, f) " + GEQ_S + " 0"),
              BASE, 11.5, "middle", True)
    panels.append(q)

OUT["darboux-incelme"] = figure(
    560, 270, panels,
    "Bir bölünüşe tek bir <em>x</em>* noktası eklendiğinde yalnızca o noktanın içine düştüğü "
    "[<em>x</em><sub><em>i</em>&#8722;1</sub>, <em>x</em><sub><em>i</em></sub>] alt aralığının terimi değişir; "
    "öteki bütün terimler aynı kalır. Solda infimumlar alınır: <em>t</em><sub>1</sub> ve <em>t</em><sub>2</sub> "
    "sayıları daha küçük kümelerin en büyük alt sınırları olduğundan <em>m</em><sub><em>i</em></sub>'nin altına "
    "inemez, bu yüzden alt toplam yalnızca artabilir. Sağda supremumlar alınır: <em>T</em><sub>1</sub> ve "
    "<em>T</em><sub>2</sub> sayıları <em>M</em><sub><em>i</em></sub>'yi aşamaz, bu yüzden üst toplam yalnızca "
    "azalabilir. Taralı şeritler tam olarak kazanılan ve kaybedilen alanlardır: bölünüş inceldikçe "
    "<em>L</em> yükselir, <em>U</em> alçalır ve iki toplam birbirine yaklaşır.",
    css_class=WIDE,
    aria="Bir alt aralik ikiye bolununce alt toplam artar, ust toplam azalir; degisen alanlar taranmis seritlerle gosterilir")

# ============================================================ darboux-x-kare-sin-turev
# -*- coding: utf-8 -*-
# f(x) = x^2 sin(1/x), f(0) = 0 -> f'(x) = 2x sin(1/x) - cos(1/x):
# a derivative that exists everywhere but is discontinuous at 0.
def fp(x):
    return 2.0 * x * math.sin(1.0 / x) - math.cos(1.0 / x)


def seg(p, x_far, x_near, n, width, opacity):
    """Draw the graph on [x_near, x_far] and on its mirror image.

    Sampling is uniform in u = 1/x, so every oscillation gets the same number
    of points however close to 0 it sits; f' is even, hence the two mirrored
    polylines. Thinner, paler strokes near 0 keep the crowded oscillations
    from merging into one solid block.
    """
    u0, u1 = 1.0 / x_far, 1.0 / x_near
    xs = [1.0 / (u0 + (u1 - u0) * k / n) for k in range(n + 1)]
    for sign in (1, -1):
        p.line([(sign * x, fp(x)) for x in xs], THEORY, width, None, opacity)


p = Plot(48, 24, 306, 212, (-0.46, 0.46), (-1.45, 1.45))
p.axes((-0.4, -0.2, 0, 0.2, 0.4), (-1, 0, 1), "x", "y", xfmt=tfmt, yfmt=tfmt)
p.line([(-0.46, 0.0), (0.46, 0.0)], TEXT, 1.0, None, 0.22)

# the two levels the oscillation keeps returning to: limsup = 1, liminf = -1
guide(p, [(-0.46, 1.0), (0.46, 1.0)], PRACTICE, 0.75)
guide(p, [(-0.46, -1.0), (0.46, -1.0)], PRACTICE, 0.75)

seg(p, 0.45, 0.120, 340, 1.8, 1.00)
seg(p, 0.120, 0.060, 180, 1.35, 0.95)
seg(p, 0.060, 0.035, 180, 1.00, 0.80)
seg(p, 0.035, 0.024, 180, 0.75, 0.60)

# f'(0) = 0 exists — the leader runs in the clean strip the drawing leaves at x = 0
guide(p, [(0.0, -1.36), (0.0, -0.10)], BASE, 0.65)
p.add('<circle cx="%.1f" cy="%.1f" r="6.4" fill="%s"/>' % (p.X(0), p.Y(0), BG))
dot(p, (0.0, 0.0), BASE, 4.4)
p.label(0.0, -1.30, "f" + PRIME + "(0) = 0", -8, 0, BASE, 11, "end", True, True)

p.label(0.0, 1.21, "0'da ne sağ ne sol limit var", 0, 0, PRACTICE, 11, "middle", False, False)
panel_title(p, "f" + PRIME + "(x) = 2x sin(1/x) " + MINUS_S + " cos(1/x)", TEXT, 11.5)

OUT["darboux-x-kare-sin-turev"] = figure(
    400, 262, [p],
    "<em>f</em>(<em>x</em>) = <em>x</em><sup>2</sup> sin(1/<em>x</em>), <em>f</em>(0) = 0 fonksiyonu her "
    "noktada türevlidir ve <em>f</em>&#8242;(0) = 0'dır; ama sıfıra yaklaşırken <em>f</em>&#8242; kesikli "
    "çizilen 1 ile &#8722;1 düzeyleri arasında sonsuz kez salınır, dolayısıyla 0'da ne sağ ne sol limiti "
    "vardır. Demek ki bir türev sürekli olmak zorunda değildir. Yine de Darboux teoremi gereği "
    "<em>f</em>&#8242; ara değer özelliğini taşır: bu yüzden bir türevin süreksizliği ancak ikinci tür "
    "olabilir, sıçrama asla.",
    aria="Turevi sifir yakininda arti bir ile eksi bir arasinda sonsuz kez salinan fonksiyonun grafigi")

# ============================================================ donusum-ucgenleri
# -*- coding: utf-8 -*-
# The three auxiliary right triangles that carry a trigonometric substitution
# back from t to x. The same right triangle is drawn three times; only the
# roles of the sides rotate, so the radical side (blue) moves from the
# adjacent leg to the hypotenuse to the opposite leg.

# Panel geometry: data units are pixels (xrange = 0..PW, yrange = 0..PH), so
# the aspect is equal and the right angle really is a right angle.
PW_TR, PH_TR = 179.0, 170.0
TW_TR, TH_TR = 96.0, 82.0                 # legs of every triangle, in pixels
AX_TR, AY_TR = 12.0, 78.0                 # vertex carrying the acute angle t
BX_TR = AX_TR + TW_TR                     # right-angle vertex
CY_TR = AY_TR + TH_TR                     # apex
T_TR = math.atan2(TH_TR, TW_TR)           # the drawn angle t (about 40.5 degrees)


def sq_tr(s):
    return s + sups("2")


A_LBL = "a"
BX_LBL = "bx"
RAD_SIN = "&#8730;(" + sq_tr("a") + MINUS_S + sq_tr("b") + sq_tr("x") + ")"
RAD_TAN = "&#8730;(" + sq_tr("a") + "+" + sq_tr("b") + sq_tr("x") + ")"
RAD_SEC = "&#8730;(" + sq_tr("b") + sq_tr("x") + MINUS_S + sq_tr("a") + ")"

# title, adjacent leg, opposite leg, hypotenuse, which side is the radical,
# which side is bx, the ratio the substitution fixes, the radical it kills
SPECS_TR = [
    ("x = (a/b) sin t", RAD_SIN, BX_LBL, A_LBL, "adj", "opp",
     "sin t = bx/a", RAD_SIN + " = a cos t"),
    ("x = (a/b) tan t", A_LBL, BX_LBL, RAD_TAN, "hyp", "opp",
     "tan t = bx/a", RAD_TAN + " = a sec t"),
    ("x = (a/b) sec t", A_LBL, RAD_SEC, BX_LBL, "opp", "hyp",
     "sec t = bx/a", RAD_SEC + " = a tan t"),
]


def rot_label_tr(p, x, y, s, deg, color, size):
    """Side label turned to lie along the hypotenuse."""
    px, py = p.X(x), p.Y(y) + 3.6
    p.add('<text x="%.1f" y="%.1f" fill="%s" font-size="%s" text-anchor="middle" '
          'font-style="italic" transform="rotate(%.2f %.1f %.1f)">%s</text>'
          % (px, py, color, size, deg, px, py, s))


def triangle_panel_tr(x0, spec):
    title, adj, opp, hyp, root, bxs, line1, line2 = spec
    p = Plot(x0, 34, PW_TR, PH_TR, (0, PW_TR), (0, PH_TR))

    def color_of(side):
        if side == root:
            return THEORY
        if side == bxs:
            return BASE
        return TEXT

    A, B, C = (AX_TR, AY_TR), (BX_TR, AY_TR), (BX_TR, CY_TR)

    # the three sides, each in the colour of the role it plays here
    p.line([A, B], color_of("adj"), 2.6 if root == "adj" else 2.0)
    p.line([B, C], color_of("opp"), 2.6 if root == "opp" else 2.0)
    p.line([C, A], color_of("hyp"), 2.6 if root == "hyp" else 2.0)

    # right-angle square at B, drawn inside the triangle
    p.line([(BX_TR - 10, AY_TR), (BX_TR - 10, AY_TR + 10), (BX_TR, AY_TR + 10)],
           TEXT, 1.2, None, 0.55)

    # the acute angle t — same corner, same colour in all three panels
    p.sector(AX_TR, AY_TR, 28, 0, T_TR, PRACTICE, 0.14)
    p.arc(AX_TR, AY_TR, 28, 0, T_TR, PRACTICE, 1.7)
    p.label(AX_TR + 38 * math.cos(T_TR / 2), AY_TR + 38 * math.sin(T_TR / 2),
            "t", 0, 4, PRACTICE, 12.5, "middle", True, True)

    # side labels
    p.label((AX_TR + BX_TR) / 2, AY_TR, adj, 0, 17, color_of("adj"),
            10.5, "middle", False, True)
    p.label(BX_TR, (AY_TR + CY_TR) / 2, opp, 8, 4, color_of("opp"),
            10.5, "start", False, True)
    rot_label_tr(p, (AX_TR + BX_TR) / 2 - 12.4, (AY_TR + CY_TR) / 2 + 14.5,
                 hyp, -math.degrees(T_TR), color_of("hyp"), 10.5)

    # what the picture is for
    panel_title(p, title, TEXT, 12)
    p.label(PW_TR / 2, AY_TR, line1, 0, 40, TEXT, 11, "middle", False, False)
    p.label(PW_TR / 2, AY_TR, line2, 0, 58, THEORY, 11, "middle", False, False)
    return p


PANELS_TR = [triangle_panel_tr(x0, s) for x0, s in zip((10, 195, 380), SPECS_TR)]

OUT["donusum-ucgenleri"] = figure(
    570, 216, PANELS_TR,
    "Yardımcı üçgen, hesabın sonunda <em>t</em>'den <em>x</em>'e dönmenin en hızlı yoludur: dar açısı "
    "<em>t</em> olan bir dik üçgende dönüşümün verdiği oran kurulur, üçüncü kenar Pisagor teoremiyle "
    "bulunur ve aranan bütün trigonometrik oranlar doğrudan okunur. Üç dönüşümde de üçgen aynıdır, "
    "yalnızca kenarların rolleri yer değiştirir: <em>bx</em> kenarı (yeşil) sırasıyla karşı, karşı ve "
    "hipotenüs; kökü taşıyan kenar (mavi) ise komşu, hipotenüs ve karşı kenar olur. Alttaki eşitlikler "
    "her dönüşümün hangi kökü sadeleştirdiğini gösterir; sonuncusu <em>t</em>'nin dar açı olduğu "
    "0 &#8804; <em>t</em> &lt; &#960;/2 dalında geçerlidir, öteki dalda işaretin elle denetlenmesi gerekir.",
    css_class=WIDE,
    aria="Sinus, tanjant ve sekant donusumlerine karsilik gelen uc yardimci dik ucgen ve kenar etiketleri")

# ============================================================ duzenleme-riemann-zikzak
# -*- coding: utf-8 -*-
# Riemann's construction: the partial sums zigzag around the target alpha with
# a shrinking amplitude, because the overshoot is bounded by the last term used.

ALPHA = "&#945;"
AL = 1.0                       # the target level, drawn as a dashed line

# One step per term: positive terms climb, negative terms descend. Each block
# stops the FIRST time the target is crossed, so the overshoot never exceeds
# the last term added; the terms shrink, hence so does the amplitude.
STEPS = [0.40, 0.32, 0.26, 0.22,          # x-block 1  -> 1.20   (overshoot 0.20 <= 0.22)
         -0.19, -0.17,                    # y-block 1  -> 0.84   (undershoot 0.16 < 0.17)
         0.155, 0.14,                     # x-block 2  -> 1.135
         -0.125, -0.115,                  # y-block 2  -> 0.895
         0.10, 0.093,                     # x-block 3  -> 1.088
         -0.082, -0.075,                  # y-block 3  -> 0.931
         0.068, 0.062,                    # x-block 4  -> 1.061
         -0.056, -0.051,                  # y-block 4  -> 0.954
         0.045, 0.041,                    # x-block 5  -> 1.040
         -0.037, -0.034]                  # y-block 5  -> 0.969

T = [0.0]
for s in STEPS:
    T.append(T[-1] + s)
N = len(T) - 1                             # 22 terms

TURNS = [k for k in range(1, N + 1)
         if k == N or (STEPS[k - 1] > 0) != (STEPS[k] > 0)]   # ends of the blocks

P1, V1 = 4, T[4]                           # first peak   S1+
Q1, W1 = 6, T[6]                           # first trough S1-

p = Plot(48, 28, 306, 196, (-0.9, 24.6), (-0.06, 1.38))
p.axes((0, 5, 10, 15, 20), (0,), "n", "t" + subs("n"))

# the target level
p.line([(-0.9, AL), (24.6, AL)], BASE, 1.4, "6 4", 0.85)
p.text_px(p.x0 - 7, p.Y(AL) + 4, ALPHA, BASE, 12.5, "end", True, True)

# the zigzag, drawn one monotone block at a time so each block keeps its colour
start = 0
for end in TURNS:
    col = THEORY if STEPS[start] > 0 else PRACTICE
    p.line([(k, T[k]) for k in range(start, end + 1)], col, 2.0)
    start = end

# every term is a vertex; the turning points are the emphasised ones
dot(p, (0, T[0]), TEXT, 2.6)
for k in range(1, N + 1):
    col = THEORY if STEPS[k - 1] > 0 else PRACTICE
    dot(p, (k, T[k]), col, 3.4 if k in TURNS else 2.1)

# how far the first block overshoots, and how far the second one undershoots
p.arrow((P1, AL), (P1, V1), TEXT, 1.2, 6.0, None, 0.85)
p.arrow((P1, V1), (P1, AL), TEXT, 1.2, 6.0, None, 0.85)
p.arrow((Q1, AL), (Q1, W1), TEXT, 1.2, 6.0, None, 0.85)
p.arrow((Q1, W1), (Q1, AL), TEXT, 1.2, 6.0, None, 0.85)
p.label(P1, V1, LEQ_S + " x" + subs("m&#8321;"), 0, -10, TEXT, 11, "middle", False, True)
p.label(Q1, W1, "&lt; |y" + subs("n&#8321;") + "|", 0, 15, TEXT, 11, "middle", False, True)

# the rule that generates the zigzag — this is also the colour key
p.arrow((2.3, 0.38), (2.3, 0.53), THEORY, 2.0, 6.5)
p.label(2.9, 0.42, ALPHA + "'nın altındayken: pozitif terimler", 0, 0, THEORY, 10.5, "start", False, False)
p.arrow((2.3, 0.28), (2.3, 0.13), PRACTICE, 2.0, 6.5)
p.label(2.9, 0.18, ALPHA + "'nın üstündeyken: negatif terimler", 0, 0, PRACTICE, 10.5, "start", False, False)

# the punchline, sitting above the tail that has already collapsed onto alpha
p.label(24.2, 1.12, "t" + subs("n") + " " + ARROW + " " + ALPHA, 0, 0, BASE, 11.5, "end", True, True)

OUT["duzenleme-riemann-zikzak"] = figure(
    400, 254, [p],
    "Riemann kurgusunun kısmi toplamları. Pozitif terimlerin toplamı +&#8734; olduğundan toplam her "
    "seferinde &#945;'nın üstüne çıkarılabilir, negatif terimlerinki &#8722;&#8734; olduğundan da her "
    "seferinde altına indirilebilir. Her dönüşte hedef <em>ilk kez</em> aşıldığı için aşma miktarı son "
    "eklenen terimin büyüklüğünü geçmez: tepe noktasındaki fazlalık <em>x</em><sub><em>m</em><sub>1</sub></sub>'i, "
    "dip noktasındaki eksiklik |<em>y</em><sub><em>n</em><sub>1</sub></sub>|'i aşmaz. Terimler sıfıra "
    "gittiğinden bu sapmalar da sıfıra iner; zikzağın genliği daralır ve kısmi toplamlar &#945;'ya yakınsar.",
    aria="Kismi toplamlarin zikzagi alfa duzeyi etrafinda genligi daralarak salinip yakinsiyor")

# ============================================================ fermat-yatay-teget
# -*- coding: utf-8 -*-
# Fermat: at an interior local extremum the tangent is horizontal.

def f_fer(x):
    return 0.4 * x ** 3 - 2.1 * x ** 2 + 2.808 * x + 0.20


AF, BF = 0.25, 3.5          # the open interval I = (a, b)
XF1, XF2 = 0.9, 2.6         # f'(x) = 1.2 (x - 0.9)(x - 2.6)

p = Plot(48, 30, 306, 200, (-0.12, 3.90), (0.0, 1.70))
p.origin_axes("x", "y")

# the open interval on the x axis
p.line([(AF, 0.0), (BF, 0.0)], BASE, 2.8, None, 0.9)

# horizontal tangents, tied to the axis by thin dashed drops
for xc in (XF1, XF2):
    guide(p, [(xc, 0.0), (xc, f_fer(xc))], PRACTICE, 0.45)
    p.line([(xc - 0.6, f_fer(xc)), (xc + 0.6, f_fer(xc))], PRACTICE, 1.9)

curve(p, f_fer, AF, BF, THEORY, 2.1, 260)
dot(p, (XF1, f_fer(XF1)), PRACTICE, 4.2)
dot(p, (XF2, f_fer(XF2)), PRACTICE, 4.2)

# the endpoints belong to neither the interval nor the graph
hollow(p, (AF, f_fer(AF)), THEORY, 3.8, 1.7)
hollow(p, (BF, f_fer(BF)), THEORY, 3.8, 1.7)
hollow(p, (AF, 0.0), BASE, 3.2, 1.6)
hollow(p, (BF, 0.0), BASE, 3.2, 1.6)

p.label(1.05, f_fer(XF1), "yerel maksimum: f" + PRIME + "(x" + subs("1") + ") = 0", 0, -11, PRACTICE, 10.5, "middle", False, True)
p.label(XF2 - 0.6, f_fer(XF2), "yerel minimum: f" + PRIME + "(x" + subs("2") + ") = 0", -8, 4, PRACTICE, 10.5, "end", False, True)
p.label(3.45, f_fer(3.45), "y = f(x)", -10, -10, THEORY, 12, "end", True, True)
p.label(1.62, 0.0, "I", 0, -7, BASE, 11.5, "middle", True, True)
p.label(AF, 0.0, "a", 0, 16, BASE, 11, "middle", True, True)
p.label(BF, 0.0, "b", 0, 16, BASE, 11, "middle", True, True)
p.label(XF1, 0.0, "x" + subs("1"), 0, 16, PRACTICE, 11, "middle", True, True)
p.label(XF2, 0.0, "x" + subs("2"), 0, 16, PRACTICE, 11, "middle", True, True)

OUT["fermat-yatay-teget"] = figure(
    400, 258, [p],
    "Fermat teoremi: açık bir <em>I</em> aralığının <em>iç</em> noktasında yerel bir ekstremum varsa ve türev "
    "orada mevcutsa, teğet yataydır — <em>x</em><sub>1</sub>'de yerel maksimum, <em>x</em><sub>2</sub>'de yerel "
    "minimum ve her ikisinde de <em>f</em>&#8242; = 0. Nedeni fark oranının işaretidir: sağdan yaklaşınca oran "
    "&#8804; 0, soldan yaklaşınca &#8805; 0 çıkar, dolayısıyla limit hem &#8804; 0 hem &#8805; 0, yani sıfırdır. "
    "Aralık açık olduğu için <em>a</em> ve <em>b</em> uçları dışarıda kalır; orada yalnızca tek yanlı fark oranı "
    "vardır ve bu argüman yürümez.",
    aria="Yerel maksimum ve yerel minimum noktalarinda egriye cizilen tegetler yatay")

# ============================================================ grafik-kesirli-birinci
# -*- coding: utf-8 -*-
# The worked example f(x) = (x+1)^2 / (1+x^2): both extrema, the three points of
# inflection and the two-sided horizontal asymptote y = 1 on one picture.

R3 = math.sqrt(3)


def f_kb(x):
    return (x + 1) ** 2 / (1 + x * x)


XMIN_KB, XMAX_KB = -5.3, 5.3
MIN_KB = (-1.0, 0.0)
MAX_KB = (1.0, 2.0)
INF_KB = [(-R3, f_kb(-R3)), (0.0, 1.0), (R3, f_kb(R3))]     # 0,134 / 1 / 1,866

p = Plot(46, 26, 350, 204, (XMIN_KB, XMAX_KB), (-0.56, 2.62))
p.origin_axes("x", "y", xticks=(-4, -3, -1, 1, 3, 4))

# ---- the horizontal asymptote y = 1 ---------------------------------------
p.line([(XMIN_KB + 0.05, 1.0), (XMAX_KB - 0.05, 1.0)], BASE, 1.6, "6 4", 0.95)
p.label(XMIN_KB + 0.1, 1.0, "y = 1  (yatay asimptot)", 0, -8, BASE, 10.5, "start", False, True)

# ---- the abscissas of the two outer inflection points ---------------------
for t in (-R3, R3):
    guide(p, [(t, 0.0), (t, f_kb(t))], PRACTICE, 0.40)
    p.line([(t, -0.045), (t, 0.045)], PRACTICE, 1.3)
p.label(-R3, 0.0, MINUS_S + "&#8730;3", 0, 15, PRACTICE, 10.5, "middle", False, True)
p.label(R3, 0.0, "&#8730;3", 0, 15, PRACTICE, 10.5, "middle", False, True)

# ---- the graph itself ------------------------------------------------------
curve(p, f_kb, XMIN_KB, XMAX_KB, THEORY, 2.3, 500)
p.label(XMIN_KB + 0.1, 2.42, "y = (x+1)" + sups("2") + " / (1+x" + sups("2") + ")",
        0, 0, THEORY, 11.5, "start", False, True)

# ---- the marked points -----------------------------------------------------
for z in INF_KB:
    hollow(p, z, PRACTICE, 3.4, 1.7)
dot(p, MIN_KB, PRACTICE, 4.4)
dot(p, MAX_KB, PRACTICE, 4.4)

p.label(MAX_KB[0], MAX_KB[1], "(1, 2)", 0, -12, PRACTICE, 11, "middle", True, True)
p.label(0.0, 1.0, "(0, 1)", -9, 15, PRACTICE, 10.5, "end", False, True)
p.label(-1.35, 0.0, "x eksenine teğet", 0, 32, PRACTICE, 9.5, "middle", False, True)

# ---- what a filled and what a hollow dot means -----------------------------
dot(p, (2.62, 0.62), PRACTICE, 4.4)
p.label(2.62, 0.62, "yerel ekstremum", 12, 4, TEXT, 9.5, "start", False, False)
hollow(p, (2.62, 0.24), PRACTICE, 3.4, 1.7)
p.label(2.62, 0.24, "dönüm noktası", 12, 4, TEXT, 9.5, "start", False, False)

OUT["grafik-kesirli-birinci"] = figure(
    412, 242, [p],
    "<em>f</em>(<em>x</em>) = (<em>x</em>+1)<sup>2</sup>/(1+<em>x</em><sup>2</sup>) fonksiyonunun beş adımlık "
    "incelemeden çıkan grafiği. Dolu noktalar yerel &#8212; burada aynı zamanda mutlak &#8212; ekstremumlardır: "
    "(&#8722;1, 0) minimumunda grafik <em>x</em> eksenine teğettir, (1, 2) maksimumunda tepe yapar. İçi boş "
    "noktalar üç dönüm noktasıdır; apsisleri &#8722;&#8730;3, 0 ve &#8730;3, ordinatları sırasıyla "
    "1&#8722;&#8730;3/2 &#8776; 0,134, 1 ve 1+&#8730;3/2 &#8776; 1,866'dır. Kesikli <em>y</em> = 1 doğrusu iki "
    "yönlü yatay asimptottur: grafik &#8722;&#8734; tarafında altından, +&#8734; tarafında üstünden yaklaşır ve "
    "asimptotu tam olarak dönüm noktası (0, 1)'de keser.",
    aria="f(x) = (x+1)^2/(1+x^2) grafigi: yerel minimum, yerel maksimum, uc donum noktasi ve y = 1 yatay asimptotu")

# ============================================================ hiperbolik-fonksiyonlar
# ============================================================ hiperbolik-fonksiyonlar
# Left: sinh and cosh squeezed between the halved exponentials.
# Right: tanh with its two horizontal asymptotes.
def f_sinh(x):
    return math.sinh(x)


def f_cosh(x):
    return math.cosh(x)


def e_pos(x):
    return math.exp(x) / 2.0


def e_neg(x):
    return math.exp(-x) / 2.0


XR1 = 2.35                       # half-width of the left panel
X_EP = math.log(9.2)             # e^x/2 leaves through the top edge here
X_EN = -math.log(8.0)            # -e^{-x}/2 leaves through the bottom edge here

p1 = Plot(44, 28, 226, 192, (-XR1, XR1), (-4.0, 4.6))
p1.origin_axes("x", "y", xticks=(-2, -1, 1, 2), yticks=(-2, 2, 4))
panel_title(p1, "Üstelin çift ve tek kısmı")
curve(p1, e_pos, -XR1, X_EP, BASE, 1.3, 200, "5 4", 0.75)
curve(p1, e_neg, -X_EP, XR1, BASE, 1.3, 200, "5 4", 0.75)
curve(p1, lambda x: -e_neg(x), X_EN, XR1, BASE, 1.3, 200, "5 4", 0.75)
clipped(p1, f_cosh, -XR1, XR1, PRACTICE, 2.1)
clipped(p1, f_sinh, -XR1, XR1, THEORY, 2.1)
dot(p1, (0, 1), PRACTICE, 3.8)
p1.label(0, 1, "(0, 1)", 5, -15, PRACTICE, 10, "start", False, True)
p1.label(-1.2, 4.15, "y = cosh x", 0, 0, PRACTICE, 11.5, "middle", True, True)
p1.label(1.2, 4.15, "y = sinh x", 0, 0, THEORY, 11.5, "middle", True, True)
p1.label(-1.5, 0, "e" + sups("x") + "/2", 0, -8, BASE, 10, "middle", False, True)
p1.label(1.25, 0, "e" + sups(MINUS_S + "x") + "/2", 0, -8, BASE, 10, "middle", False, True)
p1.label(1.65, 0, MINUS_S + "e" + sups(MINUS_S + "x") + "/2", 0, 30, BASE, 10, "middle", False, True)
p1.label(1.25, -2.75, "cosh" + sups("2") + "x " + MINUS_S + " sinh" + sups("2") + "x = 1",
         0, 0, TEXT, 10.5, "middle", False, True)

XR2 = 3.5                        # half-width of the right panel
p2 = Plot(322, 28, 226, 192, (-XR2, XR2), (-1.45, 1.45))
p2.origin_axes("x", "y", xticks=(-3, -2, -1, 1, 2, 3))
panel_title(p2, "y = tanh x", THEORY)
guide(p2, [(-XR2 + 0.05, 1.0), (XR2 - 0.05, 1.0)], PRACTICE, 0.75)
guide(p2, [(-XR2 + 0.05, -1.0), (XR2 - 0.05, -1.0)], PRACTICE, 0.75)
curve(p2, math.tanh, -XR2, XR2, THEORY, 2.1, 300)
p2.label(XR2 - 0.05, 1.0, "y = 1", 0, -7, PRACTICE, 10.5, "end", False, True)
p2.label(XR2 - 0.05, -1.0, "y = " + MINUS_S + "1", 0, 15, PRACTICE, 10.5, "end", False, True)
p2.label(-1.9, 1.2, "tanh = sinh / cosh", 0, 0, THEORY, 10, "middle", False, True)
p2.label(-1.85, -1.27, "tanh" + PRIME + " x = 1/cosh" + sups("2") + "x", 0, 0, TEXT, 10, "middle", False, True)

OUT["hiperbolik-fonksiyonlar"] = figure(
    560, 244, [p1, p2],
    "Hiperbolik fonksiyonlar üstel fonksiyonun çift ve tek kısımlarıdır: cosh <em>x</em> = "
    "(e<sup>x</sup> + e<sup>&#8722;x</sup>)/2, sinh <em>x</em> = (e<sup>x</sup> &#8722; "
    "e<sup>&#8722;x</sup>)/2. Solda <em>x</em> büyürken iki eğri de e<sup>x</sup>/2 kesiklisine "
    "yapışır; <em>x</em> küçülürken cosh e<sup>&#8722;x</sup>/2'ye, sinh ise &#8722;e<sup>&#8722;x</sup>/2'ye "
    "yaklaşır. Sağda tanh <em>x</em> = sinh <em>x</em>/cosh <em>x</em> her yerde artar ve &#8722;1 ile 1 "
    "doğrularının arasında kalır. cosh<sup>2</sup><em>x</em> &#8722; sinh<sup>2</sup><em>x</em> = 1 özdeşliği "
    "de, (sinh)&#8242; = cosh ve (cosh)&#8242; = sinh türev kuralları da doğrudan bu tanımdan çıkar.",
    css_class=WIDE,
    aria="Solda sinh ve cosh egrileri ile kesikli ustel egriler, sagda tanh egrisi ve arti eksi bir asimptotlari")

# ============================================================ ilkel-ailesi-x-kup
# ============================================================ ilkel-ailesi-x-kup
# The general antiderivative of 3x^2 is the family y = x^3 + C: one curve moved
# up and down. A vertical translation does not change any slope, so the tangents
# drawn at x = 1 on the four members are parallel, all of slope f(1) = 3.

X0_IA = 1.0                # the abscissa where the tangents are compared
SLOPE_IA = 3.0             # f(1) = 3 * 1^2
HALF_IA = 0.42             # half-length (in x) of a tangent segment
XMAX_IA = 1.75             # right end of the plotted range — where the C labels sit

# (C, colour); the constants 5 and -8 are the two antiderivatives of the example
FAM_IA = ((5, PRACTICE), (0, THEORY), (-4, BASE), (-8, TEXT))


def cube_ia(c):
    return lambda x: x ** 3 + c


p = Plot(48, 26, 230, 250, (-1.65, XMAX_IA), (-9.8, 11.4))
p.origin_axes("x", "y", yticks=(-6, -2, 2))

# the line x = 1, along which the four slopes are read off
guide(p, [(X0_IA, -9.75), (X0_IA, 7.7)], TEXT, 0.55)

for c, col in FAM_IA:
    f = cube_ia(c)
    op = 0.8 if col == TEXT else 1.0
    clipped(p, f, -1.65, XMAX_IA, col, 2.0, 400, op)
    # the tangent at x = 1: same slope on every member of the family
    p.line([(X0_IA - HALF_IA, through(f, X0_IA, SLOPE_IA, X0_IA - HALF_IA)),
            (X0_IA + HALF_IA, through(f, X0_IA, SLOPE_IA, X0_IA + HALF_IA))],
           col, 1.7, "6 4", op)
    dot(p, (X0_IA, f(X0_IA)), col, 3.4)
    tag = "C = " + (MINUS_S + str(-c) if c < 0 else str(c))
    p.label(XMAX_IA, f(XMAX_IA), tag, 8, 4, col, 11, "start", False, True)

# title, the slope note in the empty upper-left corner, and the name of the line
p.text_px(p.x0 + p.w / 2, 18, "y = x" + sups("3") + " + C", TEXT, 12.5, "middle", True, True)
p.label(-0.22, 10.0, "teğetler paralel", 0, 0, TEXT, 10.5, "end", False, True)
p.label(-0.22, 8.7, "F" + PRIME + "(1) = f(1) = 3", 0, 0, TEXT, 10.5, "end", False, True)
p.text_px(p.X(X0_IA), p.y0 + p.h + 15, "x = 1", TEXT, 11, "middle", False, True)

OUT["ilkel-ailesi-x-kup"] = figure(
    344, 302, [p],
    "<em>f</em>(<em>x</em>) = 3<em>x</em><sup>2</sup>'nin ilkelleri <em>y</em> = <em>x</em><sup>3</sup> + "
    "<em>C</em> eğrileridir; hepsi tek bir eğrinin düşey ötelenmişidir. Düşey öteleme hiçbir eğimi "
    "değiştirmediğinden <em>x</em> = 1 apsisinde dört eğriye çizilen teğetlerin eğimi de aynıdır: "
    "<em>F</em>&#8242;(1) = <em>f</em>(1) = 3, yani teğetler paraleldir. Demek ki ilkel tek bir eğri "
    "değil bir eğri ailesidir ve iki üye yalnızca bir sabitle ayrılır &#8212; örneğin <em>C</em> = 5 ile "
    "<em>C</em> = &#8722;8 üyeleri arasındaki fark her <em>x</em>'te 13'tür.",
    aria="Ayni eksende dort otelenmis kubik egri ve x esittir 1 dogrusu uzerinde dort paralel teget")

# ============================================================ integral-testi-dikdortgenler
# -*- coding: utf-8 -*-
# Integral test: left-endpoint rectangles circumscribe the area, right-endpoint
# rectangles are inscribed in it, so the partial sums trap the integral.


def f_it(x):
    return 1.0 / x


XA_IT, XB_IT = 1.0, 5.0
KS_IT = (1, 2, 3, 4)

INTEG_S_IT = INT_S + subs("1") + sups("5") + " f"                 # short form, used on the panels
INTEG_L_IT = INT_S + subs("1") + sups("5") + " f(x) dx"           # long form, used once at the bottom
NB = "&#160;"


def area_pts_it():
    """Boundary of the region under the graph on [1, 5]."""
    n = 90
    pts = [(XA_IT, 0.0)]
    pts += [(XA_IT + (XB_IT - XA_IT) * k / n, f_it(XA_IT + (XB_IT - XA_IT) * k / n))
            for k in range(n + 1)]
    pts.append((XB_IT, 0.0))
    return pts


def panel_it(x0, shift, col, title, sum_txt, rel):
    """One panel: rectangles of height f(k + shift) over each [k, k+1]."""
    p = Plot(x0, 34, 212, 176, (0.70, 5.40), (0.0, 1.18))
    p.axes((1, 2, 3, 4, 5), (0.5, 1.0), "x", "y", yfmt=tfmt)
    panel_title(p, title, TEXT, 11.5)

    for k in KS_IT:
        rect(p, k, k + 1, 0.0, f_it(k + shift), col, 0.17, col, 1.3)
    p.polygon(area_pts_it(), THEORY, 0.17, "none")
    curve(p, f_it, XA_IT, 5.28, THEORY, 2.3)
    for k in KS_IT:                       # the corner that rides on the graph
        dot(p, (k + shift, f_it(k + shift)), col, 3.6)

    p.label(1.55, 0.115, INTEG_S_IT, 0, 0, THEORY, 11, "middle", True, True)
    p.label(4.62, 0.46, "y = f(x)", 0, 0, THEORY, 11.5, "middle", True, True)

    xr = p.X(5.35)
    p.text_px(xr, p.y0 + 22, "dikdörtgenlerin alanı", TEXT, 10, "end", False, True)
    p.text_px(xr, p.y0 + 39, sum_txt, col, 11.5, "end", True, True)
    p.text_px(xr, p.y0 + 56, rel + NB + '<tspan fill="' + THEORY + '">' + INTEG_S_IT + "</tspan>",
              TEXT, 11.5, "end", False, True)
    return p


p1 = panel_it(46, 0, PRACTICE, "Yükseklik f(k): eğrinin üstünde",
              "f(1)+f(2)+f(3)+f(4)", GEQ_S)
p2 = panel_it(320, 1, BASE, "Yükseklik f(k+1): eğrinin altında",
              "f(2)+f(3)+f(4)+f(5)", LEQ_S)

p2.text_px(289, 250,
           '<tspan fill="' + BASE + '">' + SUM_S + subs("k=2") + sups("5") + " f(k)</tspan>"
           + NB + LEQ_S + NB
           + '<tspan fill="' + THEORY + '">' + INTEG_L_IT + "</tspan>"
           + NB + LEQ_S + NB
           + '<tspan fill="' + PRACTICE + '">' + SUM_S + subs("k=1") + sups("4") + " f(k)</tspan>",
           TEXT, 12.5, "middle", True, True)

OUT["integral-testi-dikdortgenler"] = figure(
    560, 264, [p1, p2],
    "Azalan pozitif bir <em>f</em> için her [<em>k</em>, <em>k</em>+1] aralığında "
    "<em>f</em>(<em>k</em>+1) &#8804; <em>f</em>(<em>x</em>) &#8804; <em>f</em>(<em>k</em>) olur: "
    "yüksekliği sol uç değeri <em>f</em>(<em>k</em>) olan dikdörtgenler eğrinin üstünde (solda), "
    "yüksekliği sağ uç değeri <em>f</em>(<em>k</em>+1) olanlar ise eğrinin altında (sağda) kalır. "
    "Tabanlar 1 birim olduğundan her dikdörtgenin alanı doğrudan serinin bir terimidir; alanları "
    "eğrinin altındaki alanla karşılaştırmak "
    "<em>f</em>(2)+<em>f</em>(3)+<em>f</em>(4)+<em>f</em>(5) &#8804; "
    "&#8747;<sub>1</sub><sup>5</sup> <em>f</em> &#8804; "
    "<em>f</em>(1)+<em>f</em>(2)+<em>f</em>(3)+<em>f</em>(4) eşitsizliğini verir. "
    "Aynı kestirim her <em>n</em> için geçerli olduğundan kısmi toplamlarla integraller birbirini "
    "sınırlar; bu yüzden seri ile genelleştirilmiş integral bir arada sonlu ya da bir arada sonsuzdur.",
    css_class=WIDE,
    aria="Iki panel: azalan egrinin ustunde kalan dikdortgenler ve altinda kalan dikdortgenler egri altindaki alani iki yandan kestiriyor")

# ============================================================ kokoran-esitsizlik-zinciri
# ============================================================ kokoran-esitsizlik-zinciri
# The four quantities of the chain inequality on one schematic number line:
# the root interval always sits inside the ratio interval, so 1 can fall in
# the gap — where the ratio test is silent but the root test still decides.

RATIO_S = "a" + subs("n+1") + "/a" + subs("n")
NROOT_S = sups("n") + "&#8730;a" + subs("n")
DOTS_S = "&#8230;"   # horizontal ellipsis; the midline dots glyph is missing from the export font

XLR, XLK, XUK, XUR = 1.05, 3.95, 5.75, 9.00   # liminf/limsup of ratios and of roots
XONE = 7.30                                    # where the number 1 falls
MIDS = (0.5 * (XLR + XLK), 0.5 * (XLK + XUK), 0.5 * (XUK + XUR))

p = Plot(20, 18, 400, 230, (0.0, 10.0), (0.0, 5.75))   # Y(y) = 248 - 40y


def yy(py):
    """Pixel row -> data y, so the whole layout can be planned in pixels."""
    return (248.0 - py) / 40.0


Y_ONE, Y_HEAD = yy(22), yy(42)
Y_ROW1, Y_NOTE = yy(80), yy(133)
Y_ROW2_TITLE, Y_ROW2 = yy(155), yy(199)
Y_ZONE1, Y_ZONE2 = yy(225), yy(238)


def numline(y):
    """A schematic number line carrying the two nested intervals."""
    p.polygon([(XLR, y - 0.20), (XUR, y - 0.20), (XUR, y + 0.20), (XLR, y + 0.20)],
              PRACTICE, 0.15, PRACTICE, 1.1)
    p.polygon([(XLK, y - 0.115), (XUK, y - 0.115), (XUK, y + 0.115), (XLK, y + 0.115)],
              THEORY, 0.26, THEORY, 1.3)
    p.arrow((0.30, y), (9.90, y), TEXT, 1.2, 7.5, None, 0.5)
    p.line([(XONE, y - 0.17), (XONE, y + 0.17)], TEXT, 1.7, None, 0.9)
    for x, col in ((XLR, PRACTICE), (XLK, THEORY), (XUK, THEORY), (XUR, PRACTICE)):
        dot(p, (x, y), col, 4.0)


# the gap that carries 1: root test decides there, ratio test does not
p.polygon([(XUK, 0.90), (XUR, 0.90), (XUR, 4.85), (XUK, 4.85)],
          BASE, 0.12, BASE, 1.2, "5 4")

# the threshold 1, running through both number lines
p.line([(XONE, 0.85), (XONE, 5.40)], TEXT, 1.3, "5 4", 0.65)
p.label(XONE, Y_ONE, "1", 0, 0, TEXT, 12.5, "middle", True)
p.label(XONE, Y_HEAD, "yakınsaklık", -8, 0, TEXT, 10.5, "end")
p.label(XONE, Y_HEAD, "ıraksaklık", 8, 0, TEXT, 10.5, "start")

# ---------------------------------------------------------------- general chain
p.label(0.35, Y_HEAD, "Terimleri pozitif her dizide:", 0, 0, TEXT, 10.5, "start", False, True)
numline(Y_ROW1)
p.label(MIDS[0], Y_ROW1, "oran aralığı", 0, -13, PRACTICE, 10, "middle", True)
p.label(MIDS[1], Y_ROW1, "kök aralığı", 0, -13, THEORY, 10, "middle", True)
for x, head, tail, col in ((XLR, "liminf", RATIO_S, PRACTICE),
                           (XLK, "liminf", NROOT_S, THEORY),
                           (XUK, "limsup", NROOT_S, THEORY),
                           (XUR, "limsup", RATIO_S, PRACTICE)):
    p.label(x, Y_ROW1, head, 0, 16, col, 10.5, "middle")
    p.label(x, Y_ROW1, tail, 0, 29, col, 10.5, "middle")
for x in MIDS:
    p.label(x, Y_ROW1, LEQ_S, 0, 22, TEXT, 12, "middle")

p.label(4.80, Y_NOTE, "Kök aralığı her zaman oran aralığının içinde kalır.",
        0, 0, TEXT, 10.5, "middle", False, True)

# ---------------------------------------------------------------- the example
p.label(0.35, Y_ROW2_TITLE,
        "Örnek: 1/2 + 1/3 + 1/2" + sups("2") + " + 1/3" + sups("2") + " + " + DOTS_S,
        0, 0, TEXT, 10.5, "start", False, True)
numline(Y_ROW2)
p.label(XLR, Y_ROW2, "0", 0, -21, PRACTICE, 11, "middle", True)
p.label(XUR, Y_ROW2, "+" + INF, 0, -21, PRACTICE, 11, "middle", True)
for x, head, tail in ((XLK, "1/&#8730;3", "&#8776; 0,577"),
                      (XUK, "1/&#8730;2", "&#8776; 0,707")):
    p.label(x, Y_ROW2, head, 0, -28, THEORY, 10.5, "middle", True)
    p.label(x, Y_ROW2, tail, 0, -15, THEORY, 9.5, "middle")
for x in MIDS:
    p.label(x, Y_ROW2, LEQ_S, 0, -21, TEXT, 12, "middle")

p.label(7.05, Y_ZONE1, "1 bu boşlukta kalır: oran testi susar,", 0, 0, BASE, 10, "middle")
p.label(7.05, Y_ZONE2, "kök testi yakınsaklığa karar verir.", 0, 0, BASE, 10, "middle")

OUT["kokoran-esitsizlik-zinciri"] = figure(
    440, 246, [p],
    "Dört büyüklük bir sayı doğrusunda her zaman bu sırayla dizilir: köklerin alt ve üst limitleri, "
    "oranların alt ve üst limitlerinin arasına sıkışır. Kök aralığı oran aralığından geniş olamaz; "
    "bu yüzden oran testinin karar verdiği her seride kök testi de aynı kararı verir. Alttaki örnekte "
    "1 sayısı oran aralığının (0 ile +&#8734; arası) içine düştüğünden oran testi susar, ama kök "
    "aralığının sağında kaldığından &#8722; yani limsup <sup>n</sup>&#8730;<em>a<sub>n</sub></em> = "
    "1/&#8730;2 &#8776; 0,707 &lt; 1 olduğundan &#8722; kök testi yakınsaklığa karar verir.",
    aria="Sayi dogrusunda oran araliginin icinde kalan dar kok araligi ve 1 sayisinin yeri")

# ============================================================ monoton-sicrama-delik
# -*- coding: utf-8 -*-
# monoton-sicrama-delik — an increasing function with a jump; the image misses an interval.

A, X0, B = 0.30, 1.85, 3.55
FA, L, FX0, C, R, FB = 0.55, 1.50, 2.05, 2.55, 3.05, 4.05


def f_left(x):
    u = (x - A) / (X0 - A)
    return FA + (L - FA) * (0.55 * u + 0.45 * u * u)


def f_right(x):
    v = (x - X0) / (B - X0)
    return R + (FB - R) * (0.65 * v + 0.35 * v * v)


p = Plot(66, 26, 288, 206, (-0.30, 4.15), (0.0, 4.4))
p.origin_axes("x", "y")

# ticks on the x axis for a, x0, b
for t in (A, X0, B):
    p.add('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1" opacity="0.55"/>'
          % (p.X(t), p.Y(0) - 3, p.X(t), p.Y(0) + 3, TEXT))

# guides: the jump levels back to the y axis, and x0 down to the x axis
guide(p, [(X0, 0.0), (X0, R)], TEXT, 0.40)
for y in (L, FX0, R):
    guide(p, [(0.09, y), (X0, y)], TEXT, 0.42)

# the value c, which the function never takes
p.line([(0.09, C), (4.05, C)], PRACTICE, 1.5, "6 4", 0.95)
hollow(p, (0, C), PRACTICE, 3.4, 1.7)

# the image of f: two shaded pieces on the y axis, plus the single point f(x0)
rect(p, -0.055, 0.055, FA, L, BASE, 0.80)
rect(p, -0.055, 0.055, R, FB, BASE, 0.80)
dot(p, (0, FA), BASE, 3.0)
dot(p, (0, FB), BASE, 3.0)
hollow(p, (0, L), BASE, 3.4, 1.7)
hollow(p, (0, R), BASE, 3.4, 1.7)
dot(p, (0, FX0), BASE, 3.6)

# the graph
curve(p, f_left, A, X0, THEORY, 2.1)
curve(p, f_right, X0, B, THEORY, 2.1)
dot(p, (A, FA), THEORY, 3.4)
dot(p, (B, FB), THEORY, 3.4)
hollow(p, (X0, L), THEORY, 3.8, 1.8)
hollow(p, (X0, R), THEORY, 3.8, 1.8)
dot(p, (X0, FX0), THEORY, 4.2)

# labels on the axes
p.label(A, 0, "a", 0, 16, TEXT, 11, "middle", True, True)
p.label(X0, 0, "x" + subs("0"), 0, 16, TEXT, 11, "middle", True, True)
p.label(B, 0, "b", 0, 16, TEXT, 11, "middle", True, True)
p.label(0, L, "f(x" + subs("0") + sups(MINUS_S) + ")", -10, 4, TEXT, 10.5, "end", False, True)
p.label(0, FX0, "f(x" + subs("0") + ")", -10, 4, TEXT, 10.5, "end", False, True)
p.label(0, R, "f(x" + subs("0") + sups("+") + ")", -10, 4, TEXT, 10.5, "end", False, True)
p.label(0, C, "c", -10, 4, PRACTICE, 11, "end", True, True)

# annotations
p.label(0.16, 3.62, "görüntü kümesi:", 0, 0, BASE, 11, "start", True, False)
p.label(0.16, 3.30, "iki ayrık parça", 0, 0, BASE, 11, "start", True, False)
p.label(3.30, f_right(3.30), "y = f(x)", -8, -6, THEORY, 11.5, "end", True, True)
p.label(2.98, 1.95, "f(x" + subs("0") + sups(MINUS_S) + ") &lt; c &lt; f(x" + subs("0") + sups("+") + ") ama",
        0, 0, PRACTICE, 10.5, "middle", False, True)
p.label(2.98, 1.63, "hiçbir x için f(x) = c", 0, 0, PRACTICE, 10.5, "middle", False, True)

OUT["monoton-sicrama-delik"] = figure(
    400, 256, [p],
    "Artan bir <em>f</em>'nin <em>x</em><sub>0</sub>'daki sıçraması: sol limit "
    "<em>f</em>(<em>x</em><sub>0</sub><sup>&#8722;</sup>) ile sağ limit "
    "<em>f</em>(<em>x</em><sub>0</sub><sup>+</sup>) vardır ama eşit değildir. Aradaki değerler "
    "&#8212; yalnız <em>f</em>(<em>x</em><sub>0</sub>) dışında &#8212; hiç alınmaz; örneğin "
    "<em>c</em> seviyesindeki yatay doğru grafiği hiç kesmez. Böylece sıçrama görüntü kümesinde "
    "bir delik açar: monoton bir fonksiyonun görüntüsünün aralık olması, sürekliliğe denktir.",
    aria="Artan bir fonksiyonun x0 noktasindaki sicramasi ve goruntu kumesinde acilan delik")

# ============================================================ mutlak-pozitif-negatif-kisim
# -*- coding: utf-8 -*-
# Splitting a sign-changing sequence into its positive and negative parts.
# Example sequence: a_k = (-1)^(k+1)/k, k = 1..10 — the one worked out in the text.

KMAX = 10
A_PN = [(-1.0) ** (k + 1) / k for k in range(1, KMAX + 1)]
AP_PN = [max(v, 0.0) for v in A_PN]      # a_k^+
AM_PN = [max(-v, 0.0) for v in A_PN]     # a_k^-

BW_PN = 8.6                               # bar width in pixels
XR_PN = (0, 11)
YR_PN = (-0.62, 1.12)                     # the same scale in all three panels


def ymm(v):
    """Tick label with a Turkish comma and a real minus sign."""
    return tfmt(v).replace("-", MINUS_S)


def bar_pn(p, k, v, color, opacity=0.6):
    """One column of a bar chart; a zero term becomes a zero-height bar on the axis."""
    x, y0 = p.X(k), p.Y(0)
    if abs(v) < 1e-12:
        p.add('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="3.2" '
              'stroke-linecap="round" opacity="0.5"/>'
              % (x - BW_PN / 2, y0, x + BW_PN / 2, y0, color))
        return
    top, bot = min(y0, p.Y(v)), max(y0, p.Y(v))
    p.add('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="1.6" fill="%s" fill-opacity="%.2f" '
          'stroke="%s" stroke-width="1.1"/>'
          % (x - BW_PN / 2, top, BW_PN, bot - top, color, opacity, color))


def tinted(s, c):
    """A coloured run inside a <text>."""
    return '<tspan fill="%s">%s</tspan>' % (c, s)


AK_PN = "a" + subs("k")
AP_S = tinted("a" + subs("k") + sups("+"), THEORY)
AM_S = tinted("a" + subs("k") + sups(MINUS_S), PRACTICE)

# ---------------------------------------------------------------- panel 1: a_k
p1 = Plot(46, 48, 156, 140, XR_PN, YR_PN)
p1.grid(ys=(-0.5, 0.5, 1.0))
p1.origin_axes("k", "", xticks=(1, 5, 9), yticks=(-0.5, 0.5, 1.0), yfmt=ymm)
panel_title(p1, AK_PN + " = (" + MINUS_S + "1)" + sups("k+1") + "/k", TEXT, 11)
for k, v in enumerate(A_PN, start=1):
    bar_pn(p1, k, v, THEORY if v > 0 else PRACTICE)
p1.label(10.6, 0.92, AK_PN + " &gt; 0", 0, 0, THEORY, 10, "end", False, True)
p1.label(10.6, -0.42, AK_PN + " &lt; 0", 0, 0, PRACTICE, 10, "end", False, True)

# ---------------------------------------------------------------- panel 2: a_k^+
p2 = Plot(244, 48, 156, 140, XR_PN, YR_PN)
p2.grid(ys=(0.5, 1.0))
p2.origin_axes("k", "", xticks=(1, 5, 9), yticks=(0.5, 1.0), yfmt=ymm)
panel_title(p2, "a" + subs("k") + sups("+") + " = max(" + AK_PN + ", 0)", THEORY, 11)
for k, v in enumerate(AP_PN, start=1):
    bar_pn(p2, k, v, THEORY)
p2.text_px(322, 167, "k tek " + ARROW + " a" + subs("k") + sups("+") + " = 1/k", THEORY, 10, "middle", False, True)
p2.text_px(322, 181, "k çift " + ARROW + " a" + subs("k") + sups("+") + " = 0", THEORY, 10, "middle", False, True)

# ---------------------------------------------------------------- panel 3: a_k^-
p3 = Plot(442, 48, 156, 140, XR_PN, YR_PN)
p3.grid(ys=(0.5, 1.0))
p3.origin_axes("k", "", xticks=(1, 5, 9), yticks=(0.5, 1.0), yfmt=ymm)
panel_title(p3, "a" + subs("k") + sups(MINUS_S) + " = max(" + MINUS_S + AK_PN + ", 0)", PRACTICE, 11)
for k, v in enumerate(AM_PN, start=1):
    bar_pn(p3, k, v, PRACTICE)
p3.text_px(520, 167, "k tek " + ARROW + " a" + subs("k") + sups(MINUS_S) + " = 0", PRACTICE, 10, "middle", False, True)
p3.text_px(520, 181, "k çift " + ARROW + " a" + subs("k") + sups(MINUS_S) + " = 1/k", PRACTICE, 10, "middle", False, True)

# ---------------------------------------------------------------- footer band
p1.add('<rect x="46" y="198" width="552" height="46" rx="6" fill="%s" fill-opacity="0.09" '
       'stroke="%s" stroke-width="1.1" stroke-opacity="0.45"/>' % (BASE, BASE))
p1.text_px(210, 220, AK_PN + " = " + AP_S + " " + MINUS_S + " " + AM_S, TEXT, 12, "middle", True, True)
p1.text_px(434, 220, "|" + AK_PN + "| = " + AP_S + " + " + AM_S, TEXT, 12, "middle", True, True)
p1.text_px(322, 238,
           "Şartlı yakınsak bir seride " + SUM_S + AP_S + " = " + SUM_S + AM_S + " = +" + INF
           + "'dur; mutlak yakınsakta ikisi de sonludur.",
           TEXT, 10.5, "middle", False, True)

OUT["mutlak-pozitif-negatif-kisim"] = figure(
    620, 258, [p1, p2, p3],
    "Örnek dizi <em>a</em><sub><em>k</em></sub> = (&#8722;1)<sup><em>k</em>+1</sup>/<em>k</em>. Her terim iki "
    "negatif olmayan parçaya ayrılır: <em>a</em><sub><em>k</em></sub><sup>+</sup> yalnızca yukarı yönlü "
    "çubukları, <em>a</em><sub><em>k</em></sub><sup>&#8722;</sup> ise aşağı yönlü çubukların boyunu tutar; "
    "kalan yerlerde ikisi de sıfırdır. Soldaki grafik ortadakinden sağdaki çıkarılarak, mutlak değerlerin "
    "grafiği ise ikisi toplanarak elde edilir. Mutlak yakınsaklık iki parça serisinin de yakınsaması "
    "demektir; şartlı yakınsaklıkta ise ikisi birden +&#8734;'a ıraksar ve sonlu toplam yalnızca bu iki "
    "sonsuzluğun birbirini yeme biçiminden doğar.",
    css_class=WIDE,
    aria="Uc sutun grafigi: isaret degistiren a k dizisi, pozitif kismi ve negatif kismi")

# ============================================================ olcut-ust-alt-fark
# -*- coding: utf-8 -*-
# The geometric reading of the Riemann criterion: U(P,f) - L(P,f) is the total
# area of the vertical strips between the lower and the upper staircase, each
# strip being omega_k wide-by-tall. Refining the partition thins every strip.

OMEGA_S = "&#969;"
APPROX_S = "&#8776;"
DELTA_X = "&#916;x"


def f_ol(x):
    return 0.9 + 0.85 * math.sin(1.5 * x) + 0.14 * x


A_OL, B_OL = 0.25, 3.40
KSTAR = 2                       # the subinterval carrying the omega_k annotation


def ext_ol(u, v, want_max):
    vals = [f_ol(u + (v - u) * k / 90) for k in range(91)]
    return max(vals) if want_max else min(vals)


def hatch_ol(p, x0, x1, y0, y1, color, step=5.0, width=0.85, opacity=0.55):
    """Diagonal hatching of an axis-aligned data rectangle, clipped in pixel space."""
    X0, X1 = p.X(x0), p.X(x1)
    Ytop, Ybot = p.Y(y1), p.Y(y0)
    if X1 - X0 < 1.0 or Ybot - Ytop < 1.0:
        return
    segs = []
    c = X0 + Ytop + step
    while c < X1 + Ybot:
        ax = max(X0, c - Ybot)
        bx = min(X1, c - Ytop)
        if bx - ax > 0.6:
            segs.append(f"M{ax:.1f},{c - ax:.1f} L{bx:.1f},{c - bx:.1f}")
        c += step
    if segs:
        p.add(f'<path d="{" ".join(segs)}" fill="none" stroke="{color}" '
              f'stroke-width="{width}" opacity="{opacity}"/>')


def num_ol(v):
    return ("%.2f" % v).replace(".", ",")


def olcut_panel(px, n, title):
    q = Plot(px, 34, 224, 188, (-0.15, 3.95), (0.0, 2.4))
    q.origin_axes("x", "y")
    panel_title(q, title, TEXT, 11.5)
    cuts = [A_OL + (B_OL - A_OL) * k / n for k in range(n + 1)]
    lo = [ext_ol(cuts[k], cuts[k + 1], False) for k in range(n)]
    hi = [ext_ol(cuts[k], cuts[k + 1], True) for k in range(n)]
    for k in range(n):
        u, v = cuts[k], cuts[k + 1]
        rect(q, u, v, 0, lo[k], THEORY, 0.15, THEORY, 0.9)          # lower rectangle
        rect(q, u, v, lo[k], hi[k], PRACTICE, 0.18, PRACTICE, 1.0)  # oscillation strip
        hatch_ol(q, u, v, lo[k], hi[k], PRACTICE)
    curve(q, f_ol, A_OL, B_OL, TEXT, 2.0)
    for x in cuts:
        q.line([(x, 0), (x, -0.055)], TEXT, 1.0, None, 0.6)
    q.label(A_OL, 0, "a", 0, 15, TEXT, 11, "middle", True, True)
    q.label(B_OL, 0, "b", 0, 15, TEXT, 11, "middle", True, True)
    diff = sum((hi[k] - lo[k]) * (cuts[k + 1] - cuts[k]) for k in range(n))
    q.label(2.85, 2.18, "U " + MINUS_S + " L " + APPROX_S + " " + num_ol(diff),
            0, 0, PRACTICE, 11, "middle", True, False)
    return q, cuts, lo, hi


# ---- left: a coarse partition, fully annotated ----------------------------
pL, cutsL, loL, hiL = olcut_panel(46, 5, "Kaba bölünüş P")
u, v = cutsL[KSTAR], cutsL[KSTAR + 1]
mk, Mk = loL[KSTAR], hiL[KSTAR]

# the oscillation of the k-th strip, measured just outside its right edge
XD = v + 0.05
pL.arrow((XD, (mk + Mk) / 2), (XD, Mk), TEXT, 1.1, 6.0, None, 0.85)
pL.arrow((XD, (mk + Mk) / 2), (XD, mk), TEXT, 1.1, 6.0, None, 0.85)
for y in (mk, Mk):
    pL.line([(XD - 0.06, y), (XD + 0.06, y)], TEXT, 1.0, None, 0.7)
pL.label(XD + 0.09, (mk + Mk) / 2, OMEGA_S + subs("k") + " = M" + subs("k") + " "
         + MINUS_S + " m" + subs("k"), 0, 4, TEXT, 10.5, "start", False, True)

# the width of the same subinterval, measured below the axis
YD = -0.30
guide(pL, [(u, 0), (u, YD - 0.05)], TEXT, 0.35)
guide(pL, [(v, 0), (v, YD - 0.05)], TEXT, 0.35)
pL.arrow(((u + v) / 2, YD), (u, YD), TEXT, 1.1, 6.0, None, 0.85)
pL.arrow(((u + v) / 2, YD), (v, YD), TEXT, 1.1, 6.0, None, 0.85)
pL.label((u + v) / 2, YD, DELTA_X + subs("k"), 0, 14, TEXT, 10.5, "middle", False, True)

# the blue staircase is the lower sum
pL.label(3.32, 0.98, "L(P, f)", 0, 0, THEORY, 10.5, "middle", False, True)
pL.arrow((3.28, 0.86), (3.08, 0.40), THEORY, 1.2, 6.5, None, 0.9)

# ---- right: the same curve, a finer partition -----------------------------
pR, cutsR, loR, hiR = olcut_panel(310, 10, "İnce bölünüş P" + PRIME)

# ---- the identity the picture proves --------------------------------------
pR.text_px(280, 279, "U(P, f) " + MINUS_S + " L(P, f) = " + SUM_S + " " + OMEGA_S
           + subs("k") + " " + DELTA_X + subs("k") + "  =  taralı şeritlerin toplam alanı",
           PRACTICE, 12, "middle", False, False)

OUT["olcut-ust-alt-fark"] = figure(
    560, 294, [pL, pR],
    "Ölçütün geometrik okunuşu. Her alt aralıkta alt dikdörtgenle onu örten üst dikdörtgen arasında "
    "kalan taralı şeridin yüksekliği <em>f</em>'nin o aralıktaki salınımı "
    "<em>&#969;</em><sub><em>k</em></sub> = <em>M</em><sub><em>k</em></sub> &#8722; "
    "<em>m</em><sub><em>k</em></sub>, genişliği &#916;<em>x</em><sub><em>k</em></sub>'dır; "
    "bu şeritlerin toplam alanı tam olarak <em>U</em>(<em>P</em>, <em>f</em>) &#8722; "
    "<em>L</em>(<em>P</em>, <em>f</em>)'dir. Solda kaba bir bölünüşte şeritler geniştir, sağda aynı eğri "
    "daha ince bir bölünüşle bölündüğünde hepsi birden incelir ve toplam alan yarıya iner. Riemann ölçütü "
    "işte bunu ister: verilen her <em>&#949;</em> &gt; 0 için taralı alanı <em>&#949;</em>'nin altına "
    "indiren bir bölünüş bulunabilmesi.",
    css_class=WIDE,
    aria="Ayni egri iki bolunusle: alt ve ust dikdortgenler arasindaki tarali salinim seritleri, "
         "bolunus inceldikce incelir")

# ============================================================ simetri-cift-tek-integral
# ============================================================ simetri-cift-tek-integral
# Left: an even integrand — the two halves carry the same area.
# Right: an odd integrand — the two halves carry opposite signed areas.
def f_even(x):
    return 1.2 - 0.5 * x * x + 0.15 * x ** 4


def f_odd(x):
    return 0.9 * x - 0.25 * x ** 3


A_EV = 2.0                     # half-width of the symmetric interval, left panel
A_OD = 1.6                     # ... and right panel
XM_OD = math.sqrt(0.9 / 0.75)  # where the odd function peaks


def area(p, f, x0, x1, color, opacity=0.18, n=90):
    """Shade the region between y = f(x) and the x axis over [x0, x1]."""
    pts = ([(x0, 0)]
           + [(x0 + (x1 - x0) * k / n, f(x0 + (x1 - x0) * k / n)) for k in range(n + 1)]
           + [(x1, 0)])
    p.polygon(pts, color, opacity, "none")


def intg(lo, hi):
    """An integral sign carrying its two limits."""
    return INT_S + subs(lo) + sups(hi)


# ---------------------------------------------------------------- even function
p1 = Plot(44, 26, 226, 186, (-2.48, 2.48), (-0.36, 2.05))
panel_title(p1, "Çift fonksiyon:  f(" + MINUS_S + "x) = f(x)")

# the x axis by hand, so the y axis can be drawn dashed as the mirror line
p1.arrow((-2.42, 0), (2.42, 0), TEXT, 1.1, 8.0, None, 0.5)
p1.label(2.42, 0, "x", -3, 16, TEXT, 11.5, "end", False, True)
p1.arrow((0, -0.06), (0, 2.00), TEXT, 1.15, 8.0, "5 4", 0.55)
p1.label(0, 2.00, "y", 7, 9, TEXT, 11.5, "start", False, True)

# the two halves, shaded in the same colour because they have the same area
area(p1, f_even, -A_EV, 0.0, THEORY, 0.17)
area(p1, f_even, 0.0, A_EV, THEORY, 0.17)
for s in (-1, 1):
    p1.line([(s * A_EV, 0), (s * A_EV, f_even(A_EV))], THEORY, 1.3, None, 0.55)
    p1.line([(s * A_EV, -0.07), (s * A_EV, 0.07)], TEXT, 1.4, None, 0.7)

# a mirror pair of points on the graph
XP_EV = 1.45
guide(p1, [(-XP_EV, f_even(XP_EV)), (XP_EV, f_even(XP_EV))], TEXT, 0.42)
dot(p1, (-XP_EV, f_even(XP_EV)), THEORY, 3.2)
dot(p1, (XP_EV, f_even(XP_EV)), THEORY, 3.2)

curve(p1, f_even, -A_EV, A_EV, THEORY, 2.2)
dot(p1, (-A_EV, f_even(A_EV)), THEORY, 3.6)
dot(p1, (A_EV, f_even(A_EV)), THEORY, 3.6)

p1.label(-1.05, 0.40, "A", 0, 0, THEORY, 13, "middle", True, True)
p1.label(1.05, 0.40, "A", 0, 0, THEORY, 13, "middle", True, True)
p1.label(-1.05, 1.80, "y = f(x)", 0, 0, THEORY, 11.5, "middle", True, True)
p1.label(-A_EV, 0, MINUS_S + "a", 0, 16, TEXT, 11, "middle", True, True)
p1.label(A_EV, 0, "a", 0, 16, TEXT, 11, "middle", True, True)
p1.label(0, 0, "eşit alanlar", 0, 17, THEORY, 10.5, "middle", False, False)

# ---------------------------------------------------------------- odd function
p2 = Plot(322, 26, 226, 186, (-1.98, 1.98), (-0.78, 0.78))
panel_title(p2, "Tek fonksiyon:  f(" + MINUS_S + "x) = " + MINUS_S + "f(x)")

p2.arrow((-1.92, 0), (1.92, 0), TEXT, 1.1, 8.0, None, 0.5)
p2.label(1.92, 0, "x", -3, -8, TEXT, 11.5, "end", False, True)
p2.arrow((0, -0.74), (0, 0.74), TEXT, 1.1, 8.0, None, 0.5)
p2.label(0, 0.74, "y", 7, 9, TEXT, 11.5, "start", False, True)

# opposite signs, opposite colours
area(p2, f_odd, -A_OD, 0.0, PRACTICE, 0.20)
area(p2, f_odd, 0.0, A_OD, BASE, 0.20)
p2.line([(-A_OD, 0), (-A_OD, f_odd(-A_OD))], PRACTICE, 1.3, None, 0.6)
p2.line([(A_OD, 0), (A_OD, f_odd(A_OD))], BASE, 1.3, None, 0.6)
for s in (-1, 1):
    p2.line([(s * A_OD, -0.03), (s * A_OD, 0.03)], TEXT, 1.4, None, 0.7)

# a point and its image under the half turn about the origin
guide(p2, [(-XM_OD, -f_odd(XM_OD)), (XM_OD, f_odd(XM_OD))], TEXT, 0.42)
dot(p2, (-XM_OD, -f_odd(XM_OD)), THEORY, 3.2)
dot(p2, (XM_OD, f_odd(XM_OD)), THEORY, 3.2)

curve(p2, f_odd, -A_OD, A_OD, THEORY, 2.2)
dot(p2, (-A_OD, f_odd(-A_OD)), THEORY, 3.6)
dot(p2, (A_OD, f_odd(A_OD)), THEORY, 3.6)
dot(p2, (0, 0), TEXT, 3.6)

p2.label(0.85, 0.24, "+A", 0, 0, BASE, 13, "middle", True, True)
p2.label(-0.85, -0.24, MINUS_S + "A", 0, 0, PRACTICE, 13, "middle", True, True)
p2.label(-1.02, 0.60, "y = f(x)", 0, 0, THEORY, 11.5, "middle", True, True)
p2.label(-A_OD, 0, MINUS_S + "a", 0, -9, TEXT, 11, "middle", True, True)
p2.label(A_OD, 0, "a", 0, 17, TEXT, 11, "middle", True, True)
p2.label(0, 0, "simetri merkezi", -8, -9, TEXT, 10, "end", False, False)

# ---------------------------------------------------------------- the two verdicts
p1.text_px(p1.x0 + p1.w / 2, 228,
           intg(MINUS_S + "a", "a") + " f = A + A = 2 " + intg("0", "a") + " f",
           TEXT, 12, "middle", False, True)
p2.text_px(p2.x0 + p2.w / 2, 228,
           intg(MINUS_S + "a", "a") + " f = (" + MINUS_S + "A) + A = 0",
           TEXT, 12, "middle", False, True)

OUT["simetri-cift-tek-integral"] = figure(
    560, 240, [p1, p2],
    "Simetri teoreminin resmi. Solda <em>f</em> çifttir: grafiği <em>y</em> eksenine göre "
    "simetrik olduğundan [&#8722;<em>a</em>, 0] ile [0, <em>a</em>] üzerindeki alanlar birbirinin "
    "aynısıdır ve integral yarım aralıktaki hesabın iki katına iner. Sağda <em>f</em> tektir: "
    "grafiği orijine göre simetrik olduğundan sol yarıdaki bölge eksenin altında, onun eşi olan sağ "
    "yarıdaki bölge ise üstünde kalır; iki katkı aynı büyüklükte ama zıt işaretlidir, dolayısıyla "
    "toplamları sıfırdır. Her iki durumda da işi bitiren şey <em>x</em> &#8614; &#8722;<em>x</em> "
    "değişken değiştirmesidir: sol yarıyı sağ yarıya taşır, çift fonksiyonda işareti korur, tek "
    "fonksiyonda ters çevirir.",
    css_class=WIDE,
    aria="Solda cift fonksiyonun y eksenine gore esit iki alani, sagda tek fonksiyonun zit isaretli iki alani")

# ============================================================ siralama-alan-karsilastirma
# ============================================================ siralama-alan-karsilastirma
# Monotonicity of the integral: f <= g on [a, b], so the signed area under f
# cannot exceed the signed area under g. Both curves dip below the axis so the
# "signed" part of the statement is visible.
A_SI, B_SI = 0.35, 3.15


def f_si(x):
    return 1.15 * math.sin(1.25 * (x - 0.9)) - 0.30


def gap_si(x):
    """g - f: strictly positive on [a, b]."""
    return 0.50 + 0.34 * math.sin(1.05 * x - 0.20)


def g_si(x):
    return f_si(x) + gap_si(x)


NS_SI = 180
FPTS = [(A_SI + (B_SI - A_SI) * k / NS_SI, f_si(A_SI + (B_SI - A_SI) * k / NS_SI))
        for k in range(NS_SI + 1)]
GPTS = [(B_SI - (B_SI - A_SI) * k / NS_SI, g_si(B_SI - (B_SI - A_SI) * k / NS_SI))
        for k in range(NS_SI + 1)]

p = Plot(48, 24, 306, 206, (-0.32, 3.92), (-1.75, 2.00))
p.origin_axes("x", "y")

# ---- the two regions ------------------------------------------------------
# signed area under f: the polygon self-intersects at f's zero, so the piece
# below the axis and the piece above it are both filled (nonzero fill rule)
p.polygon([(A_SI, 0)] + FPTS + [(B_SI, 0)], THEORY, 0.16)
# the band between the graphs — the integral of g - f
p.polygon(FPTS + GPTS, BASE, 0.09)
for k in range(17):
    xh = A_SI + (B_SI - A_SI) * k / 16
    p.line([(xh, f_si(xh)), (xh, g_si(xh))], BASE, 1.0, None, 0.40)

# one strip singled out: its height is g(x) - f(x) >= 0
XM_SI = 1.45
p.arrow((XM_SI, f_si(XM_SI)), (XM_SI, g_si(XM_SI)), BASE, 1.6, 7.0)
p.arrow((XM_SI, g_si(XM_SI)), (XM_SI, f_si(XM_SI)), BASE, 1.6, 7.0)

# ---- the graphs -----------------------------------------------------------
curve(p, f_si, A_SI, B_SI, THEORY, 2.1)
curve(p, g_si, A_SI, B_SI, PRACTICE, 2.1)
dot(p, (A_SI, f_si(A_SI)), THEORY, 3.4)
dot(p, (B_SI, f_si(B_SI)), THEORY, 3.4)
dot(p, (A_SI, g_si(A_SI)), PRACTICE, 3.4)
dot(p, (B_SI, g_si(B_SI)), PRACTICE, 3.4)

# ---- the interval ---------------------------------------------------------
guide(p, [(A_SI, -1.42), (A_SI, g_si(A_SI))], TEXT, 0.40)
guide(p, [(B_SI, -1.42), (B_SI, g_si(B_SI))], TEXT, 0.40)
p.label(A_SI, -1.45, "a", 0, 14, TEXT, 11.5, "middle", True, True)
p.label(B_SI, -1.45, "b", 0, 14, TEXT, 11.5, "middle", True, True)

# ---- labels ---------------------------------------------------------------
p.label(1.25, -0.85, "y = f(x)", 0, 0, THEORY, 12, "middle", True, True)
guide(p, [(1.05, 1.30), (1.05, g_si(1.05) + 0.07)], PRACTICE, 0.55)
p.label(1.05, 1.42, "y = g(x)", 0, 0, PRACTICE, 12, "middle", True, True)

rect(p, 1.52, 2.30, 0.94, 1.23, BG, 1.0)
p.label(1.56, 1.02, "g " + MINUS_S + " f " + GEQ_S + " 0", 0, 0, BASE, 10, "start", False, True)

# the sign of each piece of the blue region
p.label(2.20, 0.36, "+", 0, 0, THEORY, 16, "middle", True, False)
p.label(0.60, -0.42, MINUS_S, 0, 0, THEORY, 16, "middle", True, False)

p.label(3.02, 1.55,
        '<tspan fill="' + THEORY + '">' + INT_S + " f</tspan> " + LEQ_S
        + ' <tspan fill="' + PRACTICE + '">' + INT_S + " g</tspan>",
        0, 0, TEXT, 13, "middle", True, False)

OUT["siralama-alan-karsilastirma"] = figure(
    400, 256, [p],
    "[<em>a</em>, <em>b</em>] üzerinde <em>f</em> &#8804; <em>g</em> ise, <em>f</em>'nin grafiğiyle "
    "<em>x</em> ekseni arasında kalan işaretli alan (mavi bölge) <em>g</em> için hesaplanan alandan "
    "büyük olamaz; aradaki fark, her yerde negatif olmayan <em>g</em> &#8722; <em>f</em> fonksiyonunun "
    "taralı bölgesidir. Alan işaretlidir: eksenin altında kalan parça eksi sayılır, bu yüzden solda "
    "<em>f</em>'nin negatif katkısı <em>g</em>'ninkinden daha büyüktür. Darboux toplamlarıyla söylenirse "
    "her alt aralıkta <em>M</em><sub>k</sub>(<em>f</em>) &#8804; <em>M</em><sub>k</sub>(<em>g</em>) "
    "olduğundan <em>U</em>(<em>P</em>, <em>f</em>) &#8804; <em>U</em>(<em>P</em>, <em>g</em>) olur; "
    "infimum alındığında eşitsizlik integrallere geçer.",
    aria="Iki egri: f her yerde g nin altinda; aradaki taranmis bolge integraller farkini gosterir")

# ============================================================ taylorseri-ustel-kismi-toplamlar
# -*- coding: utf-8 -*-
# Partial sums of the Maclaurin series of e^x: the fit widens on both sides.

CDOTS = "&#8943;"     # midline ellipsis
APX = "&#8776;"       # approximately equal


def texp(n, x):
    """T_n(x) = 1 + x + x^2/2! + ... + x^n/n!."""
    s, term = 1.0, 1.0
    for k in range(1, n + 1):
        term *= x / k
        s += term
    return s


XA, XB = -2.6, 1.8
p = Plot(50, 28, 300, 200, (XA, XB), (-1.2, 6.6))
p.axes((-2, -1, 0, 1), (0, 2, 4, 6), "x", "y")

# the level y = 0, so the sign changes on the left are readable
guide(p, [(XA, 0), (XB, 0)], TEXT, 0.28)

# the centre of the expansion
guide(p, [(0, -1.2), (0, 5.05)], TEXT, 0.3)
p.label(0, 5.05, "merkez x" + subs("0") + " = 0", 6, -4, TEXT, 10, "start", False, True)

# the exponential itself, drawn first so the polynomials lie on top of it
clipped(p, math.exp, XA, XB, TEXT, 2.6, 420, 0.9)
p.label(XB, math.exp(XB), "y = e" + sups("x"), -2, -13, TEXT, 11.5, "end", True, True)

# the partial sums; degree grows -> the fit widens to the left and to the right
ROWS = ((1, PRACTICE, 1.6, 0.55),
        (2, PRACTICE, 1.7, 0.9),
        (3, THEORY, 1.7, 0.95),
        (5, BASE, 1.9, 1.0))
for n, col, wd, op in ROWS:
    clipped(p, lambda x, n=n: texp(n, x), XA, XB, col, wd, 420, op)
    yb = texp(n, XB)
    dot(p, (XB, yb), col, 2.6)
    p.label(XB, yb, "T" + subs(str(n)), 7, 4, col, 11, "start", False, True)

# what the picture is about
p.text_px(60, 54, "T" + subs("n") + "(x) = 1 + x + x" + sups("2") + "/2! + " + CDOTS
          + " + x" + sups("n") + "/n!", TEXT, 10.5, "start", False, True)
p.text_px(60, 72, "yakınsaklık yarıçapı R = " + INF, TEXT, 10.5, "start", False, True)
p.text_px(60, 90, "x = 1'de: T" + subs("1") + " = 2, T" + subs("2") + " = 2,5, T" + subs("3")
          + " " + APX + " 2,667, T" + subs("5") + " " + APX + " 2,717, e " + APX + " 2,71828",
          TEXT, 10, "start", False, True)

OUT["taylorseri-ustel-kismi-toplamlar"] = figure(
    400, 252, [p],
    "<em>e</em><sup><em>x</em></sup>'in Maclaurin serisinin kısmi toplamları: "
    "<em>T</em><sub>1</sub>(<em>x</em>) = 1 + <em>x</em>, <em>T</em><sub>2</sub>, "
    "<em>T</em><sub>3</sub> ve <em>T</em><sub>5</sub>. Her kısmi toplam merkezde eğriye yapışır; "
    "derece büyüdükçe yapışma bölgesi hem sağa hem sola genişler. Yakınsaklık yarıçapı "
    "&#8734; olduğundan önceden seçilen herhangi bir [&#8722;<em>R</em>, <em>R</em>] aralığında "
    "yeterince büyük <em>n</em> için hata gözle ayırt edilemez hâle gelir: <em>T</em><sub>5</sub> "
    "şeklin büyük bölümünde eğrinin altında kaybolmuştur. Yine de her <em>T</em><sub><em>n</em></sub> "
    "bir polinomdur; üstel büyümeye yetişemediğinden yeterince uzakta eğriyi terk eder.",
    aria="e ussu x egrisi ve Maclaurin kismi toplamlari T1, T2, T3, T5; derece arttikca yaklasim genisliyor")

# ============================================================ temel-teorem-teleskopik
# -*- coding: utf-8 -*-
# Proof of the first fundamental theorem: on every subinterval the mean value
# theorem turns the rise of F into the area f(t_k)*dx_k, and the rises telescope.
DL = "&#916;"                       # capital delta

def f_ftt(x):
    return 0.12 * x * x - 0.55 * x + 1.1


def F_ftt(x):
    return 0.04 * x ** 3 - 0.275 * x * x + 1.1 * x + 0.45     # F' = f


CUT_T = [0.0, 1.0, 1.7, 2.6, 4.0]                 # a = x0 < x1 < x2 < x3 < x4 = b
A_T, B_T = CUT_T[0], CUT_T[-1]
LV = [F_ftt(x) for x in CUT_T]                    # the levels F(x_k)


def mvt_point(u, v):
    """The t in (u, v) the mean value theorem gives for F on [u, v]: f(t) = slope."""
    s = (F_ftt(v) - F_ftt(u)) / (v - u)
    d = math.sqrt(0.55 ** 2 - 4 * 0.12 * (1.1 - s))
    r1, r2 = (0.55 - d) / 0.24, (0.55 + d) / 0.24
    return r1 if u < r1 < v else r2


TS = [mvt_point(CUT_T[k], CUT_T[k + 1]) for k in range(4)]
KS, KM = subs("k"), subs("k" + MINUS_S + "1")
XLAB = ["a", "x" + subs("1"), "x" + subs("2"), "x" + subs("3"), "b"]

# --- left panel: the Riemann sum ------------------------------------------
pf = Plot(44, 36, 210, 184, (-0.35, 4.50), (0.0, 1.40))
pf.origin_axes("x", "y")
panel_title(pf, "Riemann toplamı: " + SUM_S + " f(t" + KS + ")" + DL + "x" + KS, PRACTICE, 11)
for k in range(4):
    u, v, t = CUT_T[k], CUT_T[k + 1], TS[k]
    rect(pf, u, v, 0, f_ftt(t), PRACTICE, 0.18, PRACTICE, 1.0)
    guide(pf, [(t, 0), (t, f_ftt(t))], BASE, 0.5)
    dot(pf, (t, 0), BASE, 3.0)
    dot(pf, (t, f_ftt(t)), BASE, 3.2)
curve(pf, f_ftt, A_T, B_T, THEORY, 2.1)
for x, s in zip(CUT_T, XLAB):
    pf.line([(x, 0), (x, -0.035)], TEXT, 1.0, None, 0.6)
    pf.label(x, 0, s, 0, 15, TEXT, 11, "middle", True, True)
# one rectangle height read off the y axis
guide(pf, [(0, f_ftt(TS[2])), (TS[2], f_ftt(TS[2]))], BASE, 0.45)
pf.label(0, f_ftt(TS[2]), "f(t" + subs("3") + ")", -7, 4, BASE, 10.5, "end", False, True)
pf.label(TS[2], 0, "t" + subs("3"), 0, 28, BASE, 10.5, "middle", False, True)
pf.label(1.62, 1.20, "y = f(x)", 0, 0, THEORY, 11.5, "middle", True, True)

# --- right panel: the telescoping staircase --------------------------------
pF = Plot(300, 36, 250, 184, (-0.35, 5.40), (0.0, 3.95))
pF.origin_axes("x", "y")
panel_title(pF, "Teleskopik toplam: " + SUM_S + " [F(x" + KS + ") " + MINUS_S + " F(x" + KM + ")]",
            PRACTICE, 11)
for k in range(5):
    guide(pF, [(CUT_T[k], LV[k]), (4.90, LV[k])], TEXT, 0.35)
for k in range(4):
    pF.line([(CUT_T[k + 1], LV[k]), (CUT_T[k + 1], LV[k + 1])], PRACTICE, 3.0)
curve(pF, F_ftt, A_T, B_T, THEORY, 2.1)
for k in range(5):
    dot(pF, (CUT_T[k], LV[k]), THEORY, 3.2)
for x, s in zip(CUT_T, XLAB):
    pF.line([(x, 0), (x, -0.09)], TEXT, 1.0, None, 0.6)
    pF.label(x, 0, s, 0, 15, TEXT, 11, "middle", True, True)
# the four rises stacked on top of each other, and the total they add up to
for k in range(4):
    pF.line([(4.70, LV[k] + 0.035), (4.70, LV[k + 1] - 0.035)], PRACTICE, 5.0)
pF.line([(5.10, LV[0]), (5.10, LV[4])], PRACTICE, 1.5)
pF.arrow((5.10, LV[0] + 0.45), (5.10, LV[0]), PRACTICE, 1.5, 7.5)
pF.arrow((5.10, LV[4] - 0.45), (5.10, LV[4]), PRACTICE, 1.5, 7.5)
pF.label(4.70, 0, "basamaklar", 0, -8, PRACTICE, 9.5, "middle")
pF.text_px(548, 64, "F(b) " + MINUS_S + " F(a)", PRACTICE, 11, "end", True, True)
pF.label(0, LV[0], "F(a)", -7, 4, THEORY, 10.5, "end", False, True)
pF.label(0, LV[4], "F(b)", -7, 4, THEORY, 10.5, "end", False, True)
pF.label(0.85, 2.55, "y = F(x)", 0, 0, THEORY, 11.5, "middle", True, True)

pF.text_px(285, 268,
           "F(x" + KS + ") " + MINUS_S + " F(x" + KM + ") = f(t" + KS + ")" + DL + "x" + KS
           + "   (ortalama değer teoremi)", TEXT, 11.5, "middle", True, True)

OUT["temel-teorem-teleskopik"] = figure(
    570, 284, [pf, pF],
    "Birinci temel teoremin ispatı bu resimdedir. Solda [<em>a</em>, <em>b</em>]'nin bir bölünüşü ve her "
    "alt aralıkta yüksekliği <em>f</em>(<em>t</em><sub><em>k</em></sub>) olan dikdörtgenler duruyor; sağda "
    "aynı bölünüş üzerinde <em>F</em>'nin grafiği ve her alt aralıkta <em>F</em>'nin yükselişini gösteren "
    "basamaklar var. Ortalama değer teoremi bir basamağın yüksekliğini karşısındaki dikdörtgenin alanına "
    "eşitler: <em>F</em>(<em>x</em><sub><em>k</em></sub>) &#8722; "
    "<em>F</em>(<em>x</em><sub><em>k</em>&#8722;1</sub>) = "
    "<em>f</em>(<em>t</em><sub><em>k</em></sub>)&#916;<em>x</em><sub><em>k</em></sub>. Basamaklar üst üste "
    "konduğunda ara yükseklikler birbirini götürür ve geriye yalnızca <em>F</em>(<em>b</em>) &#8722; "
    "<em>F</em>(<em>a</em>) kalır; yani bu sayı, <em>f</em>'nin o bölünüşe karşılık gelen bir Riemann "
    "toplamına eşittir.",
    css_class=WIDE,
    aria="Solda f nin Riemann dikdortgenleri, sagda F nin merdiven basamaklari; basamaklar ust uste "
         "eklenince F(b) eksi F(a) cikiyor")

# ============================================================ ters-fonksiyon-yansima
# ============================================================ ters-fonksiyon-yansima
# The graph of f^{-1} is the mirror image of the graph of f in the line y = x.
def f_ti(x):
    return 0.5 * x * x - 0.25 * x + 0.25


A_TI, B_TI = 0.5, 2.0                      # domain [a, b]
FA_TI, FB_TI = f_ti(A_TI), f_ti(B_TI)      # range [A, B] = [f(a), f(b)]


def g_ti(y):
    """f^{-1}(y) by bisection on [a, b] — f is strictly increasing there."""
    lo, hi = A_TI, B_TI
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if f_ti(mid) < y:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


X0_TI = 1.25
Y0_TI = f_ti(X0_TI)
M_TI = 0.5 * (X0_TI + Y0_TI)               # foot of the reflection on y = x
D_TI = 0.08                                # half-size of the right-angle mark

# equal aspect: same data span on both axes, square panel
p = Plot(52, 20, 220, 220, (-0.28, 2.32), (-0.28, 2.32))
p.origin_axes("x", "y")

# the mirror line, stopped short so its name can sit at the tip
p.line([(-0.27, -0.27), (2.02, 2.02)], TEXT, 1.1, "5 4", 0.5)

# the two intervals, marked with thick strokes on the axes
p.line([(A_TI, 0), (B_TI, 0)], THEORY, 4.5, None, 0.5)
p.line([(0, FA_TI), (0, FB_TI)], PRACTICE, 4.5, None, 0.5)
for t in (A_TI, B_TI):
    p.line([(t, -0.06), (t, 0.06)], THEORY, 1.7)
for t in (FA_TI, FB_TI):
    p.line([(-0.06, t), (0.06, t)], PRACTICE, 1.7)

# the endpoints of the graphs tied to the axis marks
guide(p, [(A_TI, 0), (A_TI, FA_TI)], THEORY, 0.3)
guide(p, [(0, FA_TI), (A_TI, FA_TI)], PRACTICE, 0.3)
guide(p, [(B_TI, 0), (B_TI, FB_TI)], THEORY, 0.3)
guide(p, [(0, FB_TI), (B_TI, FB_TI)], PRACTICE, 0.3)

# the two graphs
curve(p, f_ti, A_TI, B_TI, THEORY, 2.2)
curve(p, g_ti, FA_TI, FB_TI, PRACTICE, 2.2)
dot(p, (A_TI, FA_TI), THEORY, 3.4)
dot(p, (B_TI, FB_TI), THEORY, 3.4)
dot(p, (FA_TI, A_TI), PRACTICE, 3.4)
dot(p, (FB_TI, B_TI), PRACTICE, 3.4)

# a point and its mirror image, joined perpendicularly to y = x
guide(p, [(X0_TI, Y0_TI), (Y0_TI, X0_TI)], TEXT, 0.6)
p.line([(M_TI + D_TI, M_TI + D_TI), (M_TI, M_TI + 2 * D_TI), (M_TI - D_TI, M_TI + D_TI)],
       TEXT, 1.0, None, 0.45)
dot(p, (X0_TI, Y0_TI), THEORY, 4.2)
dot(p, (Y0_TI, X0_TI), PRACTICE, 4.2)

# labels
p.label(A_TI, 0, "a", 0, 17, THEORY, 11.5, "middle", True, True)
p.label(B_TI, 0, "b", 0, 17, THEORY, 11.5, "middle", True, True)
p.label(0, FA_TI, "A = f(a)", -9, 4, PRACTICE, 10.5, "end", False, True)
p.label(0, FB_TI, "B = f(b)", -9, 4, PRACTICE, 10.5, "end", False, True)
p.label(X0_TI, Y0_TI, "(x" + subs("0") + ", y" + subs("0") + ")", 10, 17, THEORY, 11, "start", False, True)
p.label(Y0_TI, X0_TI, "(y" + subs("0") + ", x" + subs("0") + ")", -10, -12, PRACTICE, 11, "end", False, True)
p.label(1.56, 0.25, "y = f(x)", 0, 0, THEORY, 11.5, "middle", True, True)
p.label(0.50, 1.88, "y = f" + sups("&#8722;1") + "(x)", 0, 0, PRACTICE, 11.5, "middle", True, True)
p.label(2.20, 2.16, "y = x", 0, 0, TEXT, 11, "middle", False, True)

OUT["ters-fonksiyon-yansima"] = figure(
    300, 250, [p],
    "Kesin artan sürekli bir <em>f</em>'nin grafiği ile <em>f</em><sup>&#8722;1</sup>'in grafiği "
    "<em>y</em> = <em>x</em> doğrusuna göre birbirinin yansımasıdır: <em>f</em>'nin grafiğindeki her "
    "(<em>x</em><sub>0</sub>, <em>y</em><sub>0</sub>) noktasına ters fonksiyonun grafiğindeki "
    "(<em>y</em><sub>0</sub>, <em>x</em><sub>0</sub>) noktası karşılık gelir; iki noktayı birleştiren "
    "doğru parçası köşegene diktir ve köşegen tarafından ortalanır. Yansıma büyüklük sıralamasını "
    "bozmadığından <em>f</em><sup>&#8722;1</sup> de kesin artandır, bir noktanın komşuluğunu yine bir "
    "komşuluğa taşıdığından süreklilik de korunur. Tanım kümesi [<em>a</em>, <em>b</em>] ile değer kümesi "
    "[<em>A</em>, <em>B</em>] = [<em>f</em>(<em>a</em>), <em>f</em>(<em>b</em>)] yalnızca yer değiştirir.",
    aria="Artan bir fonksiyonun grafigi ve y esittir x dogrusuna gore yansimasi olan ters fonksiyonun grafigi")

# ============================================================ test-hiyerarsisi
# -*- coding: utf-8 -*-
# The four tests as nested regions: each one is a choice of c_k in Kummer's test.

W_TH, H_TH = 420, 282
NBSP = "&#160;"
DOT_TH = NBSP + NBSP + "&#183;" + NBSP + NBSP
CK = "c" + subs("k")

# a pixel canvas: text_px and raw <rect> markup both work in these coordinates
p = Plot(0, 0, W_TH, H_TH, (0, W_TH), (0, H_TH))


def box_th(x0, y0, x1, y1, color, fill_op, width=1.7, dash=None, stroke_op=0.85, r=13):
    """Rounded rectangle in pixel coordinates."""
    da = ' stroke-dasharray="%s"' % dash if dash else ""
    p.add('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="%d" '
          'fill="%s" fill-opacity="%.3f" stroke="%s" stroke-width="%.2f" '
          'stroke-opacity="%.2f"%s/>' % (x0, y0, x1 - x0, y1 - y0, r,
                                         color, fill_op, color, width, stroke_op, da))


# outermost dashed frame: series no rung of the ladder settles
box_th(8, 25, 412, 262, TEXT, 0.0, 1.2, "6 4", 0.45, 15)

# name, c_k badge, colour, left, top, right, bottom, fill opacity
LEVELS_TH = (("Kummer testi", CK + " serbest (örn. k ln k ln(ln k))",
              TEXT, 20, 39, 400, 244, 0.045),
             ("Bertrand testi", CK + " = k ln k", BASE, 38, 59, 382, 222, 0.075),
             ("Raabe testi", CK + " = k", PRACTICE, 56, 79, 364, 200, 0.075),
             ("Oran testi", CK + " = 1", THEORY, 74, 99, 346, 178, 0.085))

for name, badge, col, x0, y0, x1, y1, op in LEVELS_TH:
    box_th(x0, y0, x1, y1, col, op)
    p.text_px(x0 + 12, y0 + 15, name, col, 11, "start", True)
    p.text_px(x1 - 12, y0 + 15, badge, col, 10, "end", False, True)

# innermost region: what the cheapest test already settles
p.text_px(210, 136, "L " + NEQ_S + " 1 olan her seri", THEORY, 10.5, "middle")
p.text_px(210, 156, "örn. " + SUM_S + " 1/2" + sups("k") + " (L = 1/2)" + DOT_TH
          + SUM_S + " 1/k! (L = 0)", THEORY, 10, "middle")

# each ring: the series that silences the inner test but not the outer one
RINGS_TH = ((194, PRACTICE, SUM_S + " 1/k" + sups("2") + DOT_TH
             + "L = 1: oran susar" + DOT_TH + "R = 2: Raabe çözer"),
            (216, BASE, SUM_S + " 1/(k ln" + sups("2") + " k)" + DOT_TH
             + "R = 1: Raabe susar" + DOT_TH + "B = 2: Bertrand çözer"),
            (238, TEXT, SUM_S + " 1/(k ln k ln" + sups("2") + "(ln k))" + DOT_TH
             + "B = 1: Bertrand susar"))

for py, col, s in RINGS_TH:
    p.text_px(210, py, s, col, 10, "middle")

p.text_px(210, 256, "her ölçek kendi sınır durumunu yaratır: merdivenin sonu yoktur",
          TEXT, 10, "middle", False, True)

p.text_px(210, 16, "Her test bir öncekini kapsar", TEXT, 11.5, "middle", True)

OUT["test-hiyerarsisi"] = figure(
    W_TH, H_TH, [p],
    "Dört test iç içe geçmiş bir güç sıralaması oluşturur: her biri Kummer testinin bir "
    "<em>c<sub>k</sub></em> seçimidir ve bir alt basamağın karar verdiği her durumda aynı kararı "
    "verir. Halkalara yazılan seriler kapsamaların <strong>kesin</strong> olduğunu gösterir: "
    "&#931;1/<em>k</em><sup>2</sup> serisinde oran testi susar (<em>L</em> = 1) ama Raabe karar "
    "verir (<em>R</em> = 2); &#931;1/(<em>k</em> ln<sup>2</sup><em>k</em>) serisinde Raabe susar "
    "(<em>R</em> = 1) ama Bertrand karar verir (<em>B</em> = 2); "
    "&#931;1/(<em>k</em> ln <em>k</em> ln<sup>2</sup>(ln <em>k</em>)) serisinde Bertrand da susar "
    "(<em>B</em> = 1) ve daha ince bir ölçek gerekir. En dıştaki kesikli çerçeve, her yeni "
    "basamağın kendi sınır durumunu yarattığını hatırlatır.",
    aria="Ic ice gecmis dort kutu: oran, Raabe, Bertrand ve Kummer testlerinin guc siralamasi")

# ============================================================ ustel-esitsizlik
# The exponential curve stays above its tangent at the origin: e^x >= 1 + x.
XL, XR = -2.2, 1.35
XA1, XA2 = -1.7, 1.3          # where the vertical gap is measured


def line_y(x):
    return 1.0 + x


p = Plot(48, 26, 306, 206, (-2.45, 1.6), (-1.45, 4.15))
p.origin_axes("x", "y", xticks=(-2, 1), yticks=(2, 3))

# the region between the two graphs — never empty except at the touching point
band = [(XL + (XR - XL) * k / 140, math.exp(XL + (XR - XL) * k / 140)) for k in range(141)]
p.polygon(band + [(XR, line_y(XR)), (XL, line_y(XL))], BASE, 0.10)

p.line([(XL, line_y(XL)), (XR, line_y(XR))], PRACTICE, 2.0)
curve(p, math.exp, XL, XR, THEORY, 2.2, 240)

# double-headed arrows measuring e^x - (1 + x) on both sides of 0
for xa in (XA1, XA2):
    p.arrow((xa, line_y(xa)), (xa, math.exp(xa)), BASE, 1.6, 7.0)
    p.arrow((xa, math.exp(xa)), (xa, line_y(xa)), BASE, 1.6, 7.0)

dot(p, (0, 1), TEXT, 4.4)
p.label(0, 1, "(0, 1)", -12, -21, TEXT, 10.5, "end", True, True)
p.label(0, 1, "eşitlik yalnız x = 0", -12, -7, TEXT, 10.5, "end", False, True)

p.label(-2.15, 3.35, "y = 1 + x doğrusu,", 0, 0, PRACTICE, 10.5, "start", False, True)
p.label(-2.15, 3.35, "eğrinin orijindeki teğeti", 0, 14, PRACTICE, 10.5, "start", False, True)

p.label(1.0, math.exp(1.0), "y = e" + sups("x"), -14, 2, THEORY, 12, "end", True, True)
p.label(0.75, 1.75, "y = 1 + x", 8, 21, PRACTICE, 12, "start", True, True)
p.label(-1.62, -1.3, "e" + sups("x") + " " + MINUS_S + " (1 + x) &gt; 0", 0, 0, BASE, 11, "start", False, True)

OUT["ustel-esitsizlik"] = figure(
    400, 258, [p],
    "<em>e</em><sup>x</sup> &#8805; 1 + <em>x</em> eşitsizliği ortalama değer teoreminin en kısa "
    "uygulamalarından biridir: 0 ile <em>x</em> arasında bir <em>c</em> için "
    "<em>e</em><sup>x</sup> &#8722; 1 = <em>e</em><sup>c</sup><em>x</em> yazılır ve iki tarafın işareti "
    "karşılaştırılır. Geometrik anlamı, üstel eğrinin orijindeki teğetinin üstünde kalmasıdır; iki grafik "
    "yalnızca <em>x</em> = 0 noktasında temas eder, başka her yerde aradaki düşey fark kesin olarak pozitiftir.",
    aria="Ustel egri her yerde y = 1 + x dogrusunun ustunde kaliyor, yalniz (0,1) noktasinda temas ediyor")

# ============================================================ x-kare-sin-bir-bolu-x
# ============================================================ x-kare-sin-bir-bolu-x
# f(x) = x^2 sin(1/x) squeezed between the parabolas y = +-x^2.
XL, XC = 0.33, 0.012          # drawn range, and the radius left blank at the origin


def f_osc(x):
    return x * x * math.sin(1.0 / x)


def osc_branch(x_hi, x_lo):
    """Points sampled uniformly in 1/x, so every oscillation gets the same
    number of samples however fast it wiggles (a uniform x grid would alias)."""
    pts, x = [], x_hi
    while x > x_lo:
        pts.append((x, f_osc(x)))
        x -= min(0.0030, 2 * math.pi * x * x / 24)
    pts.append((x_lo, f_osc(x_lo)))
    return pts


right = osc_branch(XL, XC)
left = [(-x, -y) for x, y in right]        # f is odd

p = Plot(48, 24, 306, 210, (-0.35, 0.35), (-0.115, 0.115))
p.axes((-0.3, -0.2, -0.1, 0, 0.1, 0.2, 0.3), (-0.1, -0.05, 0, 0.05, 0.1), "x", "y",
       xfmt=tfmt, yfmt=tfmt)
panel_title(p, "f(x) = x" + sups("2") + " sin(1/x),  f(0) = 0", THEORY)
curve(p, lambda x: x * x, -XL, XL, PRACTICE, 1.6, 160, "6 4", 0.95)
curve(p, lambda x: -x * x, -XL, XL, PRACTICE, 1.6, 160, "6 4", 0.95)
p.line([(-XL, 0.0), (XL, 0.0)], BASE, 1.45, "5 4", 1.0)
p.line(right, THEORY, 1.8)
p.line(left, THEORY, 1.8)
dot(p, (0.0, 0.0), TEXT, 4.2)

p.label(0.30, 0.09, "y = x" + sups("2"), -3, -7, PRACTICE, 11.5, "end", False, True)
p.label(0.30, -0.09, "y = " + MINUS_S + "x" + sups("2"), -3, 16, PRACTICE, 11.5, "end", False, True)
p.label(-0.31, 0.0, "teğet: y = 0", 3, 15, BASE, 10.5, "start", False, True)
p.label(0.0, 0.0, "f" + PRIME + "(0) = 0", 0, 34, BASE, 11, "middle", True, True)
p.label(-0.085, 0.062, "salınım sıklaşır", 0, 0, THEORY, 10, "middle", False, False)
p.arrow((-0.075, 0.050), (-0.052, 0.010), THEORY, 1.2, 6.5, None, 0.65)

OUT["x-kare-sin-bir-bolu-x"] = figure(
    400, 262, [p],
    "<em>f</em>(<em>x</em>) = <em>x</em><sup>2</sup> sin(1/<em>x</em>) grafiği, <em>y</em> = "
    "<em>x</em><sup>2</sup> ile <em>y</em> = &#8722;<em>x</em><sup>2</sup> zarfları arasında sıkışır; "
    "0'a yaklaşırken salınım sonsuz kez tekrarlanır ama genlik <em>x</em><sup>2</sup> hızıyla erir. "
    "|<em>f</em>(<em>x</em>) &#8722; <em>f</em>(0)| / |<em>x</em>| &#8804; |<em>x</em>| olduğundan fark oranı "
    "0'a gider: <em>f</em> sıfırda türevlenebilirdir, <em>f</em>&#8242;(0) = 0 ve teğet yataydır. "
    "Buna karşın <em>x</em> &#8800; 0 için <em>f</em>&#8242;(<em>x</em>) = 2<em>x</em> sin(1/<em>x</em>) "
    "&#8722; cos(1/<em>x</em>) olup <em>x</em> &#8594; 0 iken limiti yoktur; yani türev 0 noktasında "
    "sürekli değildir.",
    aria="x kare sin bir bolu x egrisi arti eksi x kare zarflari arasinda sikisiyor, orijinde yatay teget")

# ============================================================ yuksek-turev-testi
# ============================================================ yuksek-turev-testi
# The higher-order derivative test: with f'(0) = f''(0) = 0 the second-derivative
# test is silent, and the first non-vanishing derivative decides. Taylor writes
# f(x) - f(0) = x^n (c + eps(x)); the sign is carried by the factor x^n, which
# keeps its sign on both sides when n is even and flips when n is odd.

Y_TOP = 1.45                     # how high the curve is allowed to climb
Y_STRIP = -0.52                  # the empty strip that carries the tangent label
XA4 = Y_TOP ** 0.25              # x^4 = Y_TOP
XA3 = Y_TOP ** (1.0 / 3.0)       # x^3 = Y_TOP
XT = 1.15                        # half-length of the drawn tangent segment
XS = 0.95                        # where the sign glyphs sit
NEQ = "&#8800;"


def _lin(a, b, n=110):
    return [a + (b - a) * k / n for k in range(n + 1)]


def _panel(x0, ymin, ymax, title):
    p = Plot(x0, 40, 150, 146, (-1.25, 1.25), (ymin, ymax))
    p.origin_axes("", "", opacity=0.38)
    panel_title(p, title)
    return p


def _tangent(p, dy):
    """The common hypothesis: the tangent at the origin is horizontal."""
    p.line([(-XT, 0), (XT, 0)], PRACTICE, 1.8, "6 4", 0.95)
    p.label(-1.22, 0, "f" + PRIME + "(0) = 0", 0, dy, PRACTICE, 9.5, "start", False, True)


def _note(p, line1, line2):
    cx = p.x0 + p.w / 2
    p.text_px(cx, 204, line1, TEXT, 10, "middle")
    p.text_px(cx, 220, line2, BASE, 10.5, "middle", True)


# ---- n = 4, c > 0: the curve stays above its tangent -----------------------
p1 = _panel(23, Y_STRIP, Y_TOP, "f(x) = x" + sups("4"))
p1.polygon([(x, x ** 4) for x in _lin(-XA4, XA4)] + [(XA4, 0), (-XA4, 0)], BASE, 0.18)
_tangent(p1, 15)
clipped(p1, lambda x: x ** 4, -1.25, 1.25, THEORY, 2.2)
dot(p1, (0, 0), PRACTICE, 4.0)
for s in (-XS, XS):
    p1.label(s, 0.36, "+", 0, 5, BASE, 15, "middle", True)
_note(p1, "n = 4 çift, f" + sups("(4)") + "(0) = 24 &gt; 0", "f(x) &gt; f(0): yerel minimum")

# ---- n = 4, c < 0: the curve stays below its tangent -----------------------
p2 = _panel(205, -Y_TOP, -Y_STRIP, "f(x) = " + MINUS_S + "x" + sups("4"))
p2.polygon([(x, -x ** 4) for x in _lin(-XA4, XA4)] + [(XA4, 0), (-XA4, 0)], BASE, 0.18)
_tangent(p2, -7)
clipped(p2, lambda x: -x ** 4, -1.25, 1.25, THEORY, 2.2)
dot(p2, (0, 0), PRACTICE, 4.0)
for s in (-XS, XS):
    p2.label(s, -0.36, MINUS_S, 0, 5, BASE, 15, "middle", True)
_note(p2, "n = 4 çift, f" + sups("(4)") + "(0) = " + MINUS_S + "24 &lt; 0",
      "f(x) &lt; f(0): yerel maksimum")

# ---- n = 3: the factor x^n changes sign at the origin ----------------------
p3 = _panel(387, -Y_TOP, Y_TOP, "f(x) = x" + sups("3"))
p3.polygon([(x, x ** 3) for x in _lin(-XA3, 0)] + [(0, 0), (-XA3, 0)], BASE, 0.18)
p3.polygon([(x, x ** 3) for x in _lin(0, XA3)] + [(XA3, 0)], BASE, 0.18)
_tangent(p3, -7)
clipped(p3, lambda x: x ** 3, -1.25, 1.25, THEORY, 2.2)
dot(p3, (0, 0), PRACTICE, 4.0)
p3.label(-XS, -0.38, MINUS_S, 0, 5, BASE, 15, "middle", True)
p3.label(XS, 0.38, "+", 0, 5, BASE, 15, "middle", True)
_note(p3, "n = 3 tek, f" + PRIME + PRIME + PRIME + "(0) = 6 " + NEQ + " 0",
      "işaret değişir: ekstremum yok")

# ---- the common reading of Taylor's formula --------------------------------
p1.text_px(280, 244, "f(x) " + MINUS_S + " f(0) = x" + sups("n") + " (c + " + EPS + "(x)),"
           "&#160;&#160; c = f" + sups("(n)") + "(0) / n! " + NEQ + " 0",
           TEXT, 11, "middle", False, True)

OUT["yuksek-turev-testi"] = figure(
    560, 254, [p1, p2, p3],
    "Üç fonksiyonun da orijinde birinci ve ikinci türevi sıfırdır; teğet üçünde de yataydır, bu yüzden "
    "ikinci türev testi hiçbirini ayırt edemez. Ayrımı sıfırdan farklı olan ilk türevin mertebesi yapar: "
    "Taylor formülü <em>f</em>(<em>x</em>) &#8722; <em>f</em>(0) farkını <em>x</em><sup>n</sup>(<em>c</em> + "
    "&#949;(<em>x</em>)) biçiminde yazar ve orijine yeterince yakın noktalarda işareti "
    "<em>x</em><sup>n</sup> çarpanı belirler. <em>n</em> çift olduğunda bu çarpan iki yanda da pozitiftir, "
    "fark <em>c</em>'nin işaretini korur: <em>c</em> &gt; 0 ise kesin yerel minimum (solda), <em>c</em> &lt; 0 "
    "ise kesin yerel maksimum (ortada). <em>n</em> tek olduğunda çarpan orijinin iki yanında zıt işaretlidir; "
    "fark da işaret değiştirdiğinden orijin ekstremum noktası olamaz (sağda).",
    css_class=WIDE,
    aria="Uc panel: x ussu dort egrisinde yerel minimum, eksi x ussu dort egrisinde yerel maksimum, "
         "x ussu uc egrisinde ekstremum yok")

# ============================================================ zincir-kurali-katmanlar
# -*- coding: utf-8 -*-
# Chain rule as two magnifications applied one after the other.

DL = "&#916;"        # capital delta
APX = "&#8776;"      # approximately equal
CDOT = "&#183;"      # centred dot

A = 0.46                              # common left endpoint of the three intervals
DXV, DUV, DYV = 0.30, 0.60, 0.90      # f'(x0) = 2, g'(u0) = 1.5 -> lengths are to scale
L0, L1 = 0.28, 1.44                   # extent of each number line

p = Plot(40, 26, 320, 198, (0.0, 2.30), (0.15, 3.45))
panel_title(p, "Zincir kuralı: iki büyütme oranı ard arda", TEXT, 11.5)

# level, interval length, colour, left label, right label, length label, right-label offset
ROWS = ((3.0, DXV, BASE,
         "x" + subs("0"),
         "x" + subs("0") + "+" + DL + "x",
         DL + "x", (14, -12)),
        (2.0, DUV, THEORY,
         "u" + subs("0") + " = f(x" + subs("0") + ")",
         "u" + subs("0") + "+" + DL + "u",
         DL + "u", (14, -12)),
        (1.0, DYV, PRACTICE,
         "y" + subs("0") + " = g(u" + subs("0") + ")",
         "y" + subs("0") + "+" + DL + "y",
         DL + "y", (16, -15)))

for lev, d, col, lab0, lab1, dlab, (ox, oy) in ROWS:
    p.arrow((L0, lev), (L1, lev), TEXT, 1.2, 7.0, None, 0.5)
    for t in (A, A + d):
        p.line([(t, lev - 0.09), (t, lev + 0.09)], TEXT, 1.1, None, 0.65)
    p.line([(A, lev), (A + d, lev)], col, 4.4)
    dot(p, (A, lev), col, 3.4)
    dot(p, (A + d, lev), col, 3.4)
    p.label(A, lev, lab0, -15, -11, TEXT, 10.5, "end", False, True)
    p.label(A + d, lev, lab1, ox, oy, TEXT, 10.5, "start", False, True)
    p.label(A + d / 2, lev, dlab, 0, -9, col, 11.5, "middle", True, True)

# f carries the first interval onto the second one, g the second onto the third
p.arrow((A, 2.87), (A, 2.13), THEORY, 1.7, 7.5)
p.arrow((A + DXV, 2.87), (A + DUV, 2.13), THEORY, 1.7, 7.5)
p.arrow((A, 1.87), (A, 1.13), PRACTICE, 1.7, 7.5)
p.arrow((A + DUV, 1.87), (A + DYV, 1.13), PRACTICE, 1.7, 7.5)

p.text_px(305, 70, "f: uzunluğu yaklaşık", THEORY, 10, "middle", False, True)
p.text_px(305, 84, "f" + PRIME + "(x" + subs("0") + ") = 2 katına çeker", THEORY, 10, "middle", False, True)
p.text_px(305, 130, "g: uzunluğu yaklaşık", PRACTICE, 10, "middle", False, True)
p.text_px(305, 144, "g" + PRIME + "(u" + subs("0") + ") = 1,5 katına çeker", PRACTICE, 10, "middle", False, True)

rect(p, 0.216, 2.084, 0.25, 0.72, BASE, 0.12, BASE, 1.2)
p.text_px(200, 208,
          DL + "y/" + DL + "x " + APX + " g" + PRIME + "(u" + subs("0") + ") " + CDOT
          + " f" + PRIME + "(x" + subs("0") + ") = 1,5 " + CDOT + " 2 = 3",
          TEXT, 11, "middle", True, True)

OUT["zincir-kurali-katmanlar"] = figure(
    400, 252, [p],
    "Zincir kuralının sezgisi budur. <em>f</em>, <em>x</em><sub>0</sub> çevresindeki küçük bir "
    "&#916;<em>x</em> aralığını yaklaşık <em>f</em>&#8242;(<em>x</em><sub>0</sub>) katına gerer; "
    "<em>g</em> de elde edilen &#916;<em>u</em> aralığını yaklaşık "
    "<em>g</em>&#8242;(<em>u</em><sub>0</sub>) katına gerer. İki büyütme oranı ard arda uygulandığından "
    "çarpılırlar: &#916;<em>y</em>/&#916;<em>x</em> &#8776; "
    "<em>g</em>&#8242;(<em>u</em><sub>0</sub>)&#183;<em>f</em>&#8242;(<em>x</em><sub>0</sub>).",
    aria="Uc sayi dogrusu: f araligi iki katina, g bir bucuk katina buyutuyor, oranlar carpiliyor")

# ============================================================ grafik-kesirli-ikinci
# -*- coding: utf-8 -*-
# The second worked example f(x) = x^2/(x-1): two branches separated by the
# vertical asymptote x = 1, the oblique asymptote y = x + 1, and the two
# extrema whose horizontal tangents are drawn as short orange segments.


def f_ki(x):
    return x * x / (x - 1.0)


XMIN_KI, XMAX_KI = -4.0, 6.0
YMIN_KI, YMAX_KI = -4.6, 9.4
MAX_KI = (0.0, 0.0)          # local maximum, graph tangent to the x axis
MIN_KI = (2.0, 4.0)          # local minimum

p = Plot(16, 26, 388, 224, (XMIN_KI, XMAX_KI), (YMIN_KI, YMAX_KI))
p.origin_axes("x", "y")
OX_KI, OY_KI = p.X(0.0), p.Y(0.0)

# ---- ticks drawn by hand: the negative x labels sit ABOVE the axis, because
#      the left branch runs just below it there ------------------------------
tk = ['<g fill="%s" font-size="11" opacity="0.72">' % TEXT]
for t in (-3, -2, 2, 3, 4, 5):
    tk.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1"/>'
              % (p.X(t), OY_KI - 3, p.X(t), OY_KI + 3, TEXT))
for t in (-3, -2):
    tk.append('<text x="%.1f" y="%.1f" text-anchor="middle">%s%d</text>'
              % (p.X(t), OY_KI - 8, MINUS_S, -t))
for t in (2, 3, 4, 5):
    tk.append('<text x="%.1f" y="%.1f" text-anchor="middle">%d</text>'
              % (p.X(t), OY_KI + 16, t))
for t in (-4, -2, 2, 4, 6):
    tk.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1"/>'
              % (OX_KI - 3, p.Y(t), OX_KI + 3, p.Y(t), TEXT))
    tk.append('<text x="%.1f" y="%.1f" text-anchor="end">%s</text>'
              % (OX_KI - 7, p.Y(t) + 4, (MINUS_S + str(-t)) if t < 0 else str(t)))
tk.append('</g>')
p.add("\n  ".join(tk))

# ---- the two asymptotes ----------------------------------------------------
p.line([(1.0, YMIN_KI + 0.05), (1.0, YMAX_KI - 0.05)], BASE, 1.6, "6 4", 0.95)
p.line([(XMIN_KI + 0.05, XMIN_KI + 1.05), (XMAX_KI - 0.05, XMAX_KI + 0.95)],
       BASE, 1.6, "6 4", 0.95)

# ---- the horizontal tangents, drawn under the curve ------------------------
p.line([(-0.62, 0.0), (0.62, 0.0)], PRACTICE, 2.2)
p.line([(1.38, 4.0), (2.62, 4.0)], PRACTICE, 2.2)

# ---- the two branches ------------------------------------------------------
clipped(p, f_ki, XMIN_KI, 0.9999, THEORY, 2.3, 900)
clipped(p, f_ki, 1.0001, XMAX_KI, THEORY, 2.3, 900)

# ---- the marked points -----------------------------------------------------
dot(p, MAX_KI, PRACTICE, 4.4)
dot(p, MIN_KI, PRACTICE, 4.4)
p.label(MAX_KI[0], MAX_KI[1], "(0, 0)", -8, 20, PRACTICE, 11, "end", True, True)
p.label(MIN_KI[0], 4.85, "(2, 4)", 0, 0, PRACTICE, 11, "middle", True, True)

# ---- what the picture says -------------------------------------------------
p.label(XMIN_KI + 0.15, 8.9, "y = x" + sups("2") + " / (x " + MINUS_S + " 1)",
        0, 0, THEORY, 12, "start", False, True)
p.label(0.85, 7.5, "x = 1  (düşey asimptot)", 0, 0, BASE, 10.5, "end", False, True)
p.label(XMAX_KI - 0.05, 2.7, "y = x + 1  (eğik asimptot)", 0, 0, BASE, 10.5, "end", False, True)

p.label(-3.9, -4.05, "sol kol: konkav", 0, 0, THEORY, 9.5, "start", False, False)
p.label(2.6, 6.6, "sağ kol: konveks", 0, 0, THEORY, 9.5, "middle", False, False)

p.label(1.55, -2.2,
        "f(x) = " + '<tspan fill="%s">x + 1</tspan>' % BASE + " + 1/(x " + MINUS_S + " 1)",
        0, 0, TEXT, 11, "start", False, True)
p.line([(1.5, -3.5), (2.0, -3.5)], PRACTICE, 2.2)
dot(p, (1.75, -3.5), PRACTICE, 4.4)
p.label(2.0, -3.5, "yerel ekstremum (yatay teğet)", 10, 4, TEXT, 9.5, "start", False, False)

OUT["grafik-kesirli-ikinci"] = figure(
    414, 258, [p],
    "<em>f</em>(<em>x</em>) = <em>x</em><sup>2</sup>/(<em>x</em>&#8722;1) fonksiyonunun iki koldan oluşan "
    "grafiği. Kesikli <em>x</em> = 1 doğrusu düşey, kesikli <em>y</em> = <em>x</em>+1 doğrusu eğik "
    "asimptottur; bölünmüş biçim <em>f</em>(<em>x</em>) = <em>x</em>+1+1/(<em>x</em>&#8722;1) ikisini de bir "
    "bakışta verir. Dolu noktalar yerel ekstremumlardır: (0, 0) yerel maksimumunda grafik <em>x</em> eksenine "
    "teğettir, (2, 4) yerel minimumunda çukur yapar; kısa turuncu parçalar bu iki noktadaki yatay teğetlerdir. "
    "Sol kol eğik asimptotun altında ve konkav, sağ kol üstünde ve konvekstir; grafik asimptotu hiç kesmez ve "
    "yerel maksimum değeri yerel minimum değerinden küçük olduğundan (0, 4) aralığındaki hiçbir değeri almaz.",
    aria="f(x) = x^2/(x-1) grafigi: x = 1 dusey asimptotu, y = x + 1 egik asimptotu, "
         "yerel maksimum (0,0) ve yerel minimum (2,4)")

# ============================================================ taylorseri-analitik-olmayan
IDENT, APPROX_S, TIMES_S = "&#8801;", "&#8776;", "&#215;"


# C^infty but not analytic: every derivative vanishes at the origin, so the
# Taylor series is identically zero while the function is positive off 0.
def f_flat(x):
    if x == 0.0:
        return 0.0
    t = 1.0 / (x * x)
    if t > 700.0:                      # e^-700 underflows to 0 anyway
        return 0.0
    return math.exp(-t)


def milli(v):
    """Tick label with three decimals and the Turkish comma: 0.005 -> '0,005'."""
    return ("%.3f" % v).replace(".", ",")


p1 = Plot(48, 34, 224, 186, (-2.35, 2.35), (-0.13, 1.14))
p1.origin_axes("x", "y", xticks=(-2, -1, 1, 2), yticks=(0.5, 1))
panel_title(p1, "f(x) = e" + sups(MINUS_S + "1/x" + sups("2", 7)), THEORY)
p1.line([(-2.3, 0), (2.3, 0)], PRACTICE, 2.4, "5 4", 0.95)
curve(p1, f_flat, -2.3, 2.3, THEORY, 2.2, 600)
dot(p1, (0, 0), TEXT, 4.4)
p1.label(-2.25, 0, "Taylor serisi " + IDENT + " 0", 0, -9, PRACTICE, 10.5, "start", False, True)
p1.label(1.6, f_flat(1.6), "y = f(x)", 6, 14, THEORY, 11.5, "start", True, True)
p1.label(0, 0, "f(0) = 0", 0, -13, TEXT, 10.5, "middle", False, True)

# right panel: the same graph magnified near the origin — still glued to the axis
p2 = Plot(322, 34, 224, 186, (-0.58, 0.58), (-0.0026, 0.0238))
p2.origin_axes("x", "y", xticks=(-0.5, -0.25, 0.25, 0.5), yticks=(0.005, 0.010, 0.015, 0.020),
               xfmt=tfmt, yfmt=milli)
panel_title(p2, "Orijin çevresinde büyütme", PRACTICE)
p2.line([(-0.56, 0), (0.56, 0)], PRACTICE, 2.2, "5 4", 0.95)
clipped(p2, f_flat, -0.56, 0.56, THEORY, 2.2, 600)
dot(p2, (0, 0), TEXT, 4.0)
for xv in (0.5, 0.3, 0.2):
    dot(p2, (xv, f_flat(xv)), BASE, 3.0)
p2.label(0.035, 0.0212, "f(0,5) " + APPROX_S + " 1,8" + TIMES_S + "10" + sups(MINUS_S + "2"),
         0, 0, BASE, 10, "start", False, True)
p2.label(0.035, 0.0182, "f(0,3) " + APPROX_S + " 1,5" + TIMES_S + "10" + sups(MINUS_S + "5"),
         0, 0, BASE, 10, "start", False, True)
p2.label(0.035, 0.0152, "f(0,2) " + APPROX_S + " 1,4" + TIMES_S + "10" + sups(MINUS_S + "11"),
         0, 0, BASE, 10, "start", False, True)
p2.label(0.035, 0.0112, "f" + sups("(n)") + "(0) = 0,  her n", 0, 0, TEXT, 10.5, "start", False, True)

OUT["taylorseri-analitik-olmayan"] = figure(
    560, 254, [p1, p2],
    "<em>f</em>(<em>x</em>) = e<sup>&#8722;1/<em>x</em><sup>2</sup></sup> (ve <em>f</em>(0) = 0) "
    "fonksiyonu her mertebeden türevlenebilirdir ve orijinde bütün türevleri sıfırdır; dolayısıyla "
    "Taylor serisi özdeş olarak sıfırdır (kesikli doğru). Oysa <em>x</em> &#8800; 0 için "
    "<em>f</em>(<em>x</em>) &gt; 0'dır: seri her yerde yakınsar ama fonksiyona yalnızca "
    "<em>x</em> = 0'da eşittir. Sağdaki büyütme, orijin çevresinde grafiğin eksene ne kadar hızlı "
    "yapıştığını gösterir &#8212; sonsuz türevlenebilir olmak analitik olmak demek değildir.",
    css_class=WIDE,
    aria="e ussu eksi bir bolu x kare fonksiyonu ve ozdes sifir olan Taylor serisi; orijin cevresinde buyutme")

# ============================================================ weierstrass-birim-cember
# -*- coding: utf-8 -*-
# The Weierstrass half-angle substitution as one picture: the chord drawn from
# B(-1, 0) to P = (cos x, sin x) makes the inscribed angle x/2 with the axis,
# so its slope is tan(x/2) = u. Since the horizontal run from B to the y axis
# is exactly 1, the chord meets the y axis at the height u itself.

X_WB = 1.0                                  # the central angle drawn (about 57 degrees)
U_WB = math.tan(X_WB / 2)                   # 0.5463 — the half-angle tangent
PX_WB, PY_WB = math.cos(X_WB), math.sin(X_WB)

SQ_WB = sups("2")
FR1_WB = "(1 " + MINUS_S + " u" + SQ_WB + ")/(1 + u" + SQ_WB + ")"
FR2_WB = "2u/(1 + u" + SQ_WB + ")"

# Equal aspect: 3.20 data units over 240 px and 2.70 over 202.5 px are both 75 px/unit.
p = Plot(28, 16, 240, 202.5, (-1.45, 1.75), (-1.20, 1.50))
p.origin_axes("", "", opacity=0.45)

# ---- the unit circle and its two horizontal ends --------------------------
p.circle(0, 0, 1, BASE, 1.7)
dot(p, (0.0, 0.0), TEXT, 3.0)
dot(p, (1.0, 0.0), TEXT, 3.4)
dot(p, (-1.0, 0.0), TEXT, 3.4)
p.label(0.0, 0.0, "O", -8, 13, TEXT, 11, "end", False, True)
p.label(1.0, 0.0, "A(1, 0)", -14, 30, TEXT, 10.5, "end", False, True)
p.label(-1.0, 0.0, "B(" + MINUS_S + "1, 0)", 12, 30, TEXT, 10.5, "start", False, True)

# ---- the central angle x and the radius OP --------------------------------
p.sector(0, 0, 0.30, 0, X_WB, THEORY, 0.18)
p.arc(0, 0, 0.30, 0, X_WB, THEORY, 1.6)
p.line([(0, 0), (PX_WB, PY_WB)], THEORY, 2.1)
p.label(0.42 * math.cos(X_WB / 2), 0.42 * math.sin(X_WB / 2), "x", 0, 4,
        THEORY, 12.5, "middle", True, True)
dot(p, (PX_WB, PY_WB), THEORY, 4.4)
p.label(PX_WB, PY_WB, "P", 7, -7, THEORY, 12.5, "start", True, True)

# ---- the chord from B, its inscribed angle x/2 and the height u -----------
p.line([(-1.0, 0.0), (PX_WB, PY_WB)], PRACTICE, 2.2)
p.sector(-1, 0, 0.50, 0, X_WB / 2, PRACTICE, 0.18)
p.arc(-1, 0, 0.50, 0, X_WB / 2, PRACTICE, 1.6)
p.label(-1 + 0.72 * math.cos(X_WB / 4), 0.72 * math.sin(X_WB / 4), "x/2", 0, 4,
        PRACTICE, 11.5, "middle", True, True)
p.label(-0.5, 0.0, "1", 0, 13, TEXT, 10.5, "middle", False, True)

p.line([(0.0, 0.0), (0.0, U_WB)], PRACTICE, 2.8)
dot(p, (0.0, U_WB), PRACTICE, 4.2)
p.label(0.0, U_WB, "u", -8, -9, PRACTICE, 12.5, "end", True, True)
# right angle of the triangle B, O, (0, u): the run is 1, the rise is u
p.line([(-0.10, 0.0), (-0.10, 0.10), (0.0, 0.10)], TEXT, 1.1, None, 0.55)

# ---- what the picture is worth, read off on the right --------------------
p.text_px(282, 56, "P = (cos x, sin x)", THEORY, 11.5, "start", False, True)
p.text_px(294, 74, "= (" + FR1_WB + ", " + FR2_WB + ")", THEORY, 10.5, "start", False, True)
p.add('<line x1="282" y1="92" x2="450" y2="92" stroke="%s" stroke-width="1" opacity="0.22"/>' % TEXT)
p.text_px(282, 112, "u = tan(x/2)", PRACTICE, 12.5, "start", True, True)
p.text_px(282, 140, "sin x = " + FR2_WB, TEXT, 11.5, "start", False, True)
p.text_px(282, 162, "cos x = " + FR1_WB, TEXT, 11.5, "start", False, True)
p.text_px(282, 184, "dx = 2 du/(1 + u" + SQ_WB + ")", TEXT, 11.5, "start", False, True)

OUT["weierstrass-birim-cember"] = figure(
    460, 224, [p],
    "Weierstrass değişiminin resmi. Merkezdeki <em>x</em> açısı <em>AP</em> yayını gördüğünden, aynı yayı "
    "gören <em>B</em>(&#8722;1, 0) köşesindeki çevre açı onun yarısı, <em>x</em>/2'dir; dolayısıyla "
    "<em>B</em>'den <em>P</em>'ye çizilen kirişin eğimi tan(<em>x</em>/2)'dir. <em>B</em> ile <em>y</em> "
    "ekseni arasındaki yatay uzaklık tam olarak 1 olduğu için bu eğim, kirişin <em>y</em> eksenini kestiği "
    "yüksekliğe eşittir: turuncu parçanın boyu <em>u</em> = tan(<em>x</em>/2)'dir. <em>x</em>, "
    "(&#8722;&#960;, &#960;) aralığında dolaşırken <em>u</em> bütün gerçel sayıları tarar ve "
    "<em>P</em> = (cos <em>x</em>, sin <em>x</em>) noktasının koordinatları <em>u</em>'nun rasyonel "
    "ifadeleri olarak okunur; sağdaki üç eşitlik de buradan çıkar.",
    aria="Birim cember uzerinde P noktasi, merkezdeki x acisi, (-1,0) noktasindan P'ye kiris, "
         "cevre aci x/2 ve kirisin y eksenini kestigi u = tan(x/2) yuksekligi")

# ============================================================ kuvvet-arctan-kismi-toplamlar
# Term-by-term integration of the geometric series gives arctan; its partial
# sums track the curve inside |x| < 1 and bolt away from it outside.
def s_arctan(n, x):
    """Partial sum of sum (-1)^k x^(2k+1)/(2k+1) up to k = n."""
    t = 0.0
    for k in range(n + 1):
        t += (-1.0) ** k * x ** (2 * k + 1) / (2 * k + 1)
    return t


PI4 = math.pi / 4.0
p = Plot(50, 26, 302, 208, (-1.62, 1.62), (-1.92, 1.92))
p.origin_axes("x", "y", xticks=(-1, 1), yticks=(-1, 1))

for xv in (-1.0, 1.0):
    p.line([(xv, -1.86), (xv, 1.86)], BASE, 1.3, "4 3", 0.75)

SERIES = ((0, PRACTICE, 0.45), (1, PRACTICE, 0.8), (2, THEORY, 0.85), (3, BASE, 1.0))
for n, col, op in SERIES:
    clipped(p, lambda x, n=n: s_arctan(n, x), -1.58, 1.58, col, 1.6, 500, op)
curve(p, math.atan, -1.58, 1.58, TEXT, 2.4, 400)

dot(p, (1, PI4), TEXT, 4.2)
guide(p, [(0, PI4), (1, PI4)], TEXT, 0.45)
p.label(0.58, PI4, "(1, &#960;/4)", 0, -8, TEXT, 10.5, "middle", True, True)

# legend in the empty lower-right corner: one row per curve
LX0, LX1, LTX = -0.88, -0.62, -0.54
rows = [(-1.12, TEXT, 2.4, 1.0, "y = arctan x")]
for i, (n, col, op) in enumerate(SERIES):
    rows.append((-1.285 - 0.165 * i, col, 1.6, op, "S" + subs(str(n))))
for ly, col, w, op, txt in rows:
    p.line([(LX0, ly), (LX1, ly)], col, w, None, op)
    p.label(LTX, ly, txt, 0, 4, col, 10.5, "start", txt.startswith("y"), True)

p.label(-1.0, -1.86, "R = 1", 0, 16, BASE, 10.5, "middle", False, True)
p.label(1.0, -1.86, "R = 1", 0, 16, BASE, 10.5, "middle", False, True)
p.label(0.28, 1.74, "|x| &lt; 1: yakınsar", 0, 0, THEORY, 10.5, "start", False, True)
p.label(-1.30, 1.74, "ıraksar", 0, 0, PRACTICE, 10.5, "middle", False, True)
p.label(1.34, 1.74, "ıraksar", 0, 0, PRACTICE, 10.5, "middle", False, True)

OUT["kuvvet-arctan-kismi-toplamlar"] = figure(
    400, 258, [p],
    "arctan <em>x</em> ile kuvvet serisi &#8721;(&#8722;1)<sup><em>n</em></sup><em>x</em><sup>2<em>n</em>+1</sup>/(2<em>n</em>+1) "
    "açılımının ilk dört kısmi toplamı. Derece büyüdükçe yaklaşım yakınsaklık aralığının içinde "
    "eğriye yapışır; |<em>x</em>| &gt; 1 olduğunda ise kısmi toplamlar eğriyi hızla terk eder. "
    "Uç nokta <em>x</em> = 1'de seri hâlâ yakınsar ve Abel limit teoremi toplamının "
    "arctan 1 = &#960;/4 olduğunu söyler &#8212; Leibniz formülü buradan gelir.",
    aria="Arktanjant egrisi ve kuvvet serisinin kismi toplamlari; yakinsaklik yaricapi bir")


# ---------------------------------------------------------------------------
for name, content in OUT.items():
    with io.open(os.path.join(OUT_DIR, "analysis2-%s.md" % name), "w", encoding="utf-8") as f:
        f.write(content)
print("generated:", ", ".join(OUT))
