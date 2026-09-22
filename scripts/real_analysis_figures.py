# -*- coding: utf-8 -*-
"""
Generates the SVG figures used in the "Reel Analiz" chapters (dersler/reel-analiz).

Same authoring flow as scripts/analysis2_figures.py: the figures are NOT produced
at build time. Run this script, then

    python scripts/center_figures.py "real-*.md"

(which measures each drawing and centers it in its viewBox) and paste the
resulting markup into the .qmd files. Figures go INSIDE the box they explain
(theorem, proof, example or solution), never inside a definition box: a figure
that illustrates a definition sits directly below that box. Building the books
therefore needs neither Python nor Jupyter; CI runs Quarto alone.

The captions are Turkish on purpose — they are the text shown on the site.
The aria labels are plain ASCII.

Usage:   python scripts/real_analysis_figures.py && python scripts/center_figures.py "real-*.md"
Output:  scripts/_figures/real-<name>.md
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

EPS, DELTA, ELL, INF = "&#949;", "&#948;", "&#8467;", "&#8734;"
MINUS_S, INT_S, ARROW, PHI, PSI = "&#8722;", "&#8747;", "&#8594;", "&#966;", "&#968;"


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def subs(s, size=9):
    """Subscript inside an SVG <text>: 'C' + subs('1')."""
    return f'<tspan font-size="{size}" dy="4">{s}</tspan><tspan dy="-4">&#8203;</tspan>'


def sups(s, size=8.5):
    """Superscript inside an SVG <text>."""
    return f'<tspan font-size="{size}" dy="-5">{s}</tspan><tspan dy="5">&#8203;</tspan>'


def mstar():
    """The outer-measure symbol m*."""
    return "m" + sups("*", 10)


def curve(p, f, x0, x1, color=THEORY, width=1.9, samples=240, dash=None, opacity=1.0):
    """Polyline of y = f(x) on [x0, x1]."""
    pts = [(x0 + (x1 - x0) * k / samples, f(x0 + (x1 - x0) * k / samples)) for k in range(samples + 1)]
    p.line(pts, color, width, dash, opacity)


def rect(p, x0, x1, y0, y1, color=THEORY, opacity=0.16, stroke=None, width=1.0, dash=None):
    """Axis-aligned rectangle in data coordinates."""
    p.polygon([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], color, opacity,
              stroke if stroke else "none", width, dash)


def bar(p, a, b, y, color=THEORY, h=8.0, opacity=1.0):
    """A number-line piece [a, b] drawn as a bar of h pixels centered on data height y."""
    X0, X1, Y = p.X(a), p.X(b), p.Y(y)
    p.add(f'<rect x="{X0:.1f}" y="{Y - h / 2:.1f}" width="{max(X1 - X0, 0.8):.1f}" height="{h:.1f}" '
          f'fill="{color}" opacity="{opacity}"/>')


def hline_px(p, x0, x1, y, color=TEXT, width=1.1, opacity=0.45, dash=None):
    """Horizontal thin line in data coordinates (a number line)."""
    da = f' stroke-dasharray="{dash}"' if dash else ""
    p.add(f'<line x1="{p.X(x0):.1f}" y1="{p.Y(y):.1f}" x2="{p.X(x1):.1f}" y2="{p.Y(y):.1f}" '
          f'stroke="{color}" stroke-width="{width}" opacity="{opacity}"{da}/>')


def tick(p, x, y, s, color=TEXT, size=10.5, dy=16, opacity=0.75):
    """A small tick on the horizontal line at height y with a label below it."""
    X, Y = p.X(x), p.Y(y)
    p.add(f'<line x1="{X:.1f}" y1="{Y - 3:.1f}" x2="{X:.1f}" y2="{Y + 3:.1f}" stroke="{color}" '
          f'stroke-width="1" opacity="{opacity}"/>')
    p.add(f'<text x="{X:.1f}" y="{Y + dy:.1f}" fill="{color}" font-size="{size}" '
          f'text-anchor="middle" opacity="{opacity}">{s}</text>')


def ytick(p, y, s, size=10.5, opacity=0.75):
    """A y-axis tick label left of the panel."""
    p.add(f'<text x="{p.x0 - 7:.1f}" y="{p.Y(y) + 4:.1f}" fill="{TEXT}" font-size="{size}" '
          f'text-anchor="end" opacity="{opacity}">{s}</text>')


def hatch(p, x0, x1, y0, y1, color, step=5.0, width=0.85, opacity=0.6):
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


def band(p, lo, hi, x0, x1, color, opacity, samples=300):
    """Fill between y = lo(x) and y = hi(x) on [x0, x1]."""
    xs = [x0 + (x1 - x0) * k / samples for k in range(samples + 1)]
    pts = [(x, hi(x)) for x in xs] + [(x, lo(x)) for x in reversed(xs)]
    p.polygon(pts, color, opacity)


def runs(xs, flags):
    """Maximal runs [x_i, x_j] of consecutive sample points where flags is True."""
    out, start = [], None
    for x, fl in zip(xs, flags):
        if fl and start is None:
            start = x
        if not fl and start is not None:
            out.append((start, prev))
            start = None
        prev = x
    if start is not None:
        out.append((start, prev))
    return out


def root(f, a, b, it=60):
    """Bisection root of f on [a, b] (f(a), f(b) of opposite signs)."""
    fa = f(a)
    for _ in range(it):
        m = (a + b) / 2
        if fa * f(m) <= 0:
            b = m
        else:
            a, fa = m, f(m)
    return (a + b) / 2


def swatch(p, px, py, color, label, kind="fill", opacity=0.35, dash=None):
    """Legend entry at pixel (px, py): a small fill box or line sample, then the label."""
    if kind == "fill":
        p.add(f'<rect x="{px:.1f}" y="{py - 8:.1f}" width="14" height="9" fill="{color}" '
              f'fill-opacity="{opacity}" stroke="{color}" stroke-width="0.8"/>')
    elif kind == "hatch":
        p.add(f'<rect x="{px:.1f}" y="{py - 8:.1f}" width="14" height="9" fill="none" '
              f'stroke="{color}" stroke-width="0.8"/>')
        p.add(f'<path d="M{px + 1:.1f},{py:.1f} L{px + 9:.1f},{py - 8:.1f} M{px + 6:.1f},{py:.1f} '
              f'L{px + 14:.1f},{py - 8:.1f}" stroke="{color}" stroke-width="0.8" opacity="0.8"/>')
    else:
        da = f' stroke-dasharray="{dash}"' if dash else ""
        w = 3.0 if kind == "bold" else 1.8
        p.add(f'<line x1="{px:.1f}" y1="{py - 3.5:.1f}" x2="{px + 16:.1f}" y2="{py - 3.5:.1f}" '
              f'stroke="{color}" stroke-width="{w}"{da}/>')
    p.text_px(px + 20, py, label, TEXT, 10.5)


def round_rect(p, x, y, w, h, color, opacity=0.08, r=14, width=1.4, dash=None):
    """Rounded rectangle in pixel coordinates."""
    da = f' stroke-dasharray="{dash}"' if dash else ""
    p.add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{r}" '
          f'fill="{color}" fill-opacity="{opacity}" stroke="{color}" stroke-width="{width}"{da}/>')


def cantor_intervals(k):
    """The 2^k closed intervals of the k-th Cantor stage C_k."""
    ints = [(0.0, 1.0)]
    for _ in range(k):
        new = []
        for a, b in ints:
            t = (b - a) / 3
            new += [(a, a + t), (b - t, b)]
        ints = new
    return ints


def cantor_fn(x, depth=40):
    """The Cantor-Lebesgue function via the ternary expansion of x."""
    if x >= 1:
        return 1.0
    r, scale = 0.0, 0.5
    for _ in range(depth):
        x *= 3
        d = int(x)
        x -= d
        if d == 1:
            return r + scale
        if d == 2:
            r += scale
        scale /= 2
    return r


# ============================================================ cantor-insasi
# The first four stages of the Cantor construction.
p = Plot(70, 22, 400, 150, (0, 1), (-0.5, 4.5))
for x, k0 in ((1 / 3, 1), (2 / 3, 1), (1 / 9, 2), (2 / 9, 2), (7 / 9, 2), (8 / 9, 2)):
    p.vline(x, 4.3 - k0, -0.75, TEXT, "3 3", 0.28)
for k in range(5):
    y = 4 - k
    for a, b in cantor_intervals(k):
        bar(p, a, b, y, THEORY, 8)
    p.label(0, y, "C" + subs(str(k)), -14, 4, TEXT, 12, "end", True, True)
    p.label(1, y, ("1", "2/3", "4/9", "8/27", "16/81")[k], 16, 4, BASE, 10.5, "start")
p.label(1, 4.5, "toplam uzunluk", 16, 2, BASE, 10, "start", False, True)
hline_px(p, 0, 1, -0.75, TEXT, 1.0, 0.4)
for x, s in ((0, "0"), (1 / 9, "1/9"), (2 / 9, "2/9"), (1 / 3, "1/3"), (2 / 3, "2/3"),
             (7 / 9, "7/9"), (8 / 9, "8/9"), (1, "1")):
    tick(p, x, -0.75, s)
OUT["cantor-insasi"] = figure(
    560, 215, [p],
    "Cantor kümesinin ilk aşamaları. Her adımda kalan kapalı aralıkların açık orta üçte biri atılır; "
    "<em>C<sub>k</sub></em>, uzunluğu 3<sup>&#8722;<em>k</em></sup> olan 2<sup><em>k</em></sup> kapalı "
    "aralıktan oluşur ve toplam uzunluğu (2/3)<sup><em>k</em></sup> sıfıra gider.",
    aria="Cantor construction: stages C0 to C4 of the unit interval with the open middle thirds removed")

# ============================================================ cantor-lebesgue-grafigi
# The devil's staircase; the seven plateaus of O_3 highlighted.
p = Plot(56, 24, 300, 270, (0, 1), (0, 1))
p.axes((), (), "x", "")
for x, s in ((1 / 9, "1/9"), (2 / 9, "2/9"), (1 / 3, "1/3"), (2 / 3, "2/3"), (7 / 9, "7/9"),
             (8 / 9, "8/9"), (1, "1")):
    p.label(x, 0, s, 0, 16, TEXT, 10, "middle")
p.label(0, 0, "0", 0, 16, TEXT, 10, "middle")
for y, s in ((0.25, "1/4"), (0.5, "1/2"), (0.75, "3/4"), (1, "1")):
    ytick(p, y, s, 10.5)
p.line([(0, 0.5), (1 / 3, 0.5)], TEXT, 1.0, "4 3", 0.45)
p.vline(1 / 3, 0, 0.5, TEXT, "4 3", 0.45)
p.vline(2 / 3, 0, 0.5, TEXT, "4 3", 0.45)
N = 2400
p.line([(k / N, cantor_fn(k / N)) for k in range(N + 1)], THEORY, 1.1, None, 0.85)
plateaus = [((1, 27), (2, 27), 1), ((1, 9), (2, 9), 2), ((7, 27), (8, 27), 3), ((1, 3), (2, 3), 4),
            ((19, 27), (20, 27), 5), ((7, 9), (8, 9), 6), ((25, 27), (26, 27), 7)]
for (a0, a1), (b0, b1), j in plateaus:
    p.line([(a0 / a1, j / 8), (b0 / b1, j / 8)], PRACTICE, 3.2)
p.label(0.5, 0.5, "1/2", 0, -8, PRACTICE, 10.5, "middle")
p.label(1 / 6, 0.25, "1/4", 0, -8, PRACTICE, 10.5, "middle")
p.label(5 / 6, 0.75, "3/4", 0, -8, PRACTICE, 10.5, "middle")
p.label(0.08, 0.84, PHI, 0, 0, THEORY, 14, "start", True, True)
OUT["cantor-lebesgue-grafigi"] = figure(
    400, 330, [p],
    "Cantor–Lebesgue fonksiyonunun grafiği. Kalın basamaklar <em>&#119978;</em><sub>3</sub>'ün yedi "
    "aralığıdır; <em>&#966;</em> bunlarda soldan sağa 1/8, 2/8, &#8230;, 7/8 değerlerini alır. "
    "Sonraki aşamalar aradaki boşluklara giderek daha kısa basamaklar ekler; <em>&#966;</em> "
    "sürekli ve artandır ama bütün yükselişi sıfır ölçülü Cantor kümesi üzerinde gerçekleşir.",
    aria="Graph of the Cantor-Lebesgue function with the seven plateaus of the third stage highlighted")

# ============================================================ basamak-yumusatma
# Smoothing the jumps of a step function by linear ramps of half-width delta.
XS = [0.0, 2.0, 4.0, 6.0]
CS = [1.0, 2.6, 1.6]
DL = 0.4


def s_step(x):
    for j in range(3):
        if x < XS[j + 1] or j == 2:
            return CS[j]


def g_smooth(x):
    for j in (1, 2):
        if abs(x - XS[j]) <= DL:
            t = (x - (XS[j] - DL)) / (2 * DL)
            return CS[j - 1] + t * (CS[j] - CS[j - 1])
    return s_step(x)


p = Plot(50, 30, 400, 190, (0, 6.3), (0, 3.1))
p.axes((), (), "x", "")
for j in (1, 2):
    a, b = XS[j] - DL, XS[j] + DL
    lo, hi = min(CS[j - 1], CS[j]), max(CS[j - 1], CS[j])
    # the two triangles where s and g differ
    p.polygon([(a, CS[j - 1]), (XS[j], CS[j - 1]), (XS[j], CS[j - 1] + (CS[j] - CS[j - 1]) / 2)],
              PRACTICE, 0.35)
    p.polygon([(XS[j], CS[j]), (b, CS[j]), (XS[j], CS[j - 1] + (CS[j] - CS[j - 1]) / 2)],
              PRACTICE, 0.35)
    p.vline(a, 0, hi, TEXT, "2 3", 0.35)
    p.vline(b, 0, hi, TEXT, "2 3", 0.35)
    # bracket for J_j under the axis
    Y = p.Y(0) + 26
    p.add(f'<path d="M{p.X(a):.1f},{Y - 4:.1f} V{Y:.1f} H{p.X(b):.1f} V{Y - 4:.1f}" fill="none" '
          f'stroke="{PRACTICE}" stroke-width="1.2"/>')
    p.text_px(p.X(XS[j]), Y + 14, "J" + subs(str(j)), PRACTICE, 11.5, "middle", False, True)
for j in range(3):
    p.line([(XS[j], CS[j]), (XS[j + 1], CS[j])], TEXT, 1.6, "5 4", 0.75)
curve(p, g_smooth, 0, 6, THEORY, 2.2, 600)
for x, s in ((0, "a"), (2, "x" + subs("1")), (4, "x" + subs("2")), (6, "b")):
    p.label(x, 0, s, 0, 15, TEXT, 11.5, "middle", False, True)
p.label(1.0, CS[0], "c" + subs("1"), 0, -8, TEXT, 11, "middle", False, True)
p.label(3.0, CS[1], "c" + subs("2"), 0, -8, TEXT, 11, "middle", False, True)
p.label(5.0, CS[2], "c" + subs("3"), 0, -8, TEXT, 11, "middle", False, True)
swatch(p, p.X(0) + 10, p.Y(3.1) - 8, TEXT, "s (basamak)", "line", dash="5 4")
swatch(p, p.X(0) + 130, p.Y(3.1) - 8, THEORY, "g (sürekli)", "line")
swatch(p, p.X(0) + 250, p.Y(3.1) - 8, PRACTICE, "s &#8800; g", "fill")
OUT["basamak-yumusatma"] = figure(
    470, 270, [p],
    "Üç basamaklı <em>s</em> fonksiyonu (kesikli) ve onu yumuşatan sürekli <em>g</em>. Her sıçrama "
    "noktası <em>x<sub>j</sub></em> çevresindeki <em>J<sub>j</sub></em> = [<em>x<sub>j</sub></em> &#8722; "
    "<em>&#948;</em>, <em>x<sub>j</sub></em> + <em>&#948;</em>] aralığında <em>g</em> doğrusaldır; iki "
    "fonksiyon yalnız taralı dar bölgelerde ayrılır ve bu bölgelerde |<em>s</em> &#8722; <em>g</em>| "
    "&#8804; 2<em>M</em> olur.",
    aria="A three step function and a continuous function joining the steps by linear ramps near each jump")

# ============================================================ dis-olcu-ortu
# A set with three pieces and a cover by overlapping open intervals.
A_PIECES = [(1.0, 2.0), (3.2, 3.6), (4.5, 6.0)]
COVER = [((0.7, 1.8), 1), ((1.5, 2.3), 2), ((3.0, 3.8), 2), ((4.3, 5.4), 1), ((5.1, 6.3), 2)]
p = Plot(40, 20, 440, 120, (0.3, 6.7), (0, 3.2))
hline_px(p, 0.3, 6.7, 0.5, TEXT, 1.1, 0.5)
for a, b in A_PIECES:
    bar(p, a, b, 0.5, THEORY, 7)
for i, ((a, b), row) in enumerate(COVER):
    y = 0.5 + 0.95 * row
    bar(p, a, b, y, BASE, 16, 0.22)
    p.label(a, y, "(", -2, 5, BASE, 15, "middle")
    p.label(b, y, ")", 2, 5, BASE, 15, "middle")
    p.label((a + b) / 2, y, "I" + subs(str(i + 1)), 0, 4, BASE, 11.5, "middle", True, True)
    p.vline(a, 0.5, y - 0.2, BASE, "2 3", 0.45)
    p.vline(b, 0.5, y - 0.2, BASE, "2 3", 0.45)
for a, b in A_PIECES:
    p.label((a + b) / 2, 0.5, "A", 0, 20, THEORY, 12, "middle", True, True)
p.label(6.7, 0.5, "&#8477;", 4, 4, TEXT, 11, "start", False, True)
OUT["dis-olcu-ortu"] = figure(
    500, 175, [p],
    "Üç parçalı bir <em>A</em> kümesi (kalın) ve onu örten beş açık aralık. Parçaların toplam uzunluğu "
    "1 + 0,4 + 1,5 = 2,9, örtünün toplamı ise 1,1 + 0,8 + 0,8 + 1,1 + 1,2 = 5'tir; fazlalık, aralıkların "
    "birbirine ve <em>A</em>'nın dışına taşmasından gelir. Dış ölçü, bütün örtüler üzerinden bu "
    "toplamların infimumudur.",
    aria="A set with three pieces on the real line covered by five overlapping open intervals")

# ============================================================ caratheodory-bolme
# A test set A cut by E into A n E and A minus E.
def e_left(y):
    return 2.3 + 0.28 * math.sin(1.4 * y + 0.4)


def e_right(y):
    return 4.1 + 0.32 * math.sin(1.2 * y + 2.0)


p = Plot(30, 20, 420, 280, (0, 6.5), (0, 4.33))
YS = [k * 4.2 / 120 + 0.05 for k in range(121)]
p.polygon([(e_left(y), y) for y in YS] + [(e_right(y), y) for y in reversed(YS)], THEORY, 0.10,
          THEORY, 1.4)
A0, A1, AX0, AX1 = 1.55, 2.75, 0.4, 6.1
AY = [A0 + (A1 - A0) * k / 60 for k in range(61)]
p.polygon([(e_left(y), y) for y in AY] + [(e_right(y), y) for y in reversed(AY)], THEORY, 0.42)
p.polygon([(AX0, A0), (AX0, A1)] + [(e_left(y), y) for y in reversed(AY)], PRACTICE, 0.30)
p.polygon([(AX1, A0), (AX1, A1)] + [(e_right(y), y) for y in reversed(AY)], PRACTICE, 0.30)
rect(p, AX0, AX1, A0, A1, PRACTICE, 0.0, PRACTICE, 1.6)
p.label(3.2, 3.7, "E", 0, 0, THEORY, 15, "middle", True, True)
p.label(AX0, A1, "A", 4, -8, PRACTICE, 15, "start", True, True)
p.label(3.2, (A0 + A1) / 2, "A &#8745; E", 0, 5, TEXT, 12.5, "middle", True, True)
p.label(1.2, (A0 + A1) / 2, "A \\ E", 0, 5, PRACTICE, 12.5, "middle", True, True)
p.label(5.2, (A0 + A1) / 2, "A \\ E", 0, 5, PRACTICE, 12.5, "middle", True, True)
p.label(3.2, 0.0, mstar() + "(A) = " + mstar() + "(A &#8745; E) + " + mstar() + "(A \\ E)",
        0, 22, TEXT, 12.5, "middle", False, True)
OUT["caratheodory-bolme"] = figure(
    480, 345, [p],
    "Carathéodory koşulunun şeması. <em>E</em> herhangi bir <em>A</em> test kümesini iki parçaya "
    "ayırır: <em>E</em>'nin içinde kalan <em>A</em> &#8745; <em>E</em> ve dışında kalan "
    "<em>A</em> &#8726; <em>E</em>. <em>E</em> ölçülebilirse, <em>A</em> nasıl seçilirse seçilsin bu "
    "iki parçanın dış ölçüleri toplanarak <em>m</em><sup>*</sup>(<em>A</em>)'yı verir.",
    aria="A horizontal test set A cut by a vertical set E into the parts A intersect E and A minus E")

# ============================================================ gli-kacan-tepe
# f_n = n chi_(0,1/n] for n = 1, 2, 4; the corners lie on y = 1/x.
p = Plot(50, 24, 320, 240, (0, 1.08), (0, 4.6))
p.axes((), (1, 2, 4), "x", "y")
for x, s in ((0.25, "1/4"), (0.5, "1/2"), (1, "1")):
    p.label(x, 0, s, 0, 16, TEXT, 10.5, "middle")
p.label(0, 0, "0", 0, 16, TEXT, 10.5, "middle")
curve(p, lambda x: 1 / x, 1 / 4.5, 1.05, TEXT, 1.3, 200, "5 4", 0.7)
for n, col in ((1, THEORY), (2, BASE), (4, PRACTICE)):
    rect(p, 0, 1 / n, 0, n, col, 0.14, col, 1.8)
    dot(p, (1 / n, n), col, 3.6)
    p.label(1 / n, n, "f" + subs(str(n)), 6, -6, col, 12, "start", True, True)
p.label(0.62, 1 / 0.62, "y = 1/x", 8, -6, TEXT, 11.5, "start", False, True)
OUT["gli-kacan-tepe"] = figure(
    420, 300, [p],
    "<em>n</em> = 1, 2, 4 için <em>f<sub>n</sub></em> = <em>n</em>&#967;<sub>(0, 1/<em>n</em>]</sub>. "
    "Dikdörtgenler daralıp yükselir, alanları hep 1'dir; köşeleri <em>y</em> = 1/<em>x</em> eğrisi "
    "üzerindedir. Bütün <em>f<sub>n</sub></em>'leri baskılayan bir fonksiyon bu merdiveni aşmak zorunda "
    "kalır ve integrali sonsuz olur.",
    aria="Rectangles of height n over the interval from 0 to 1 over n for n equal 1, 2, 4 with the curve y equal 1 over x")

# ============================================================ yak-sikistirma
# Closed F inside E inside open O, on the line.
E_P = [(1.0, 2.5), (3.4, 4.2), (5.0, 6.5)]
F_P = [(1.15, 2.3), (3.55, 4.05), (5.2, 6.35)]
O_P = [(0.8, 2.75), (3.2, 4.45), (4.8, 6.7)]
p = Plot(40, 24, 440, 110, (0.4, 7.1), (0, 3))
hline_px(p, 0.4, 7.1, 2.2, TEXT, 1.1, 0.5)
for a, b in O_P:
    bar(p, a, b, 2.2, PRACTICE, 14, 0.40)
for a, b in E_P:
    bar(p, a, b, 2.2, BG, 14, 1.0)
    bar(p, a, b, 2.2, BASE, 14, 0.55)
for a, b in F_P:
    bar(p, a, b, 2.2, THEORY, 14, 1.0)
# component rows
for rows_y, pieces, col, name, lb, rb in ((1.2, F_P, THEORY, "F", "[", "]"),
                                          (0.6, E_P, BASE, "E", "", ""),
                                          (0.0, O_P, PRACTICE, "O", "(", ")")):
    for a, b in pieces:
        bar(p, a, b, rows_y, col, 3.5, 0.9)
        if lb:
            p.label(a, rows_y, lb, -1, 4.5, col, 12, "middle")
            p.label(b, rows_y, rb, 1, 4.5, col, 12, "middle")
    p.label(0.4, rows_y, name, -6, 4, col, 12, "end", True, True)
# callouts above the composite bar
p.line([(0.9, 2.45), (0.9, 2.85)], PRACTICE, 1.0, None, 0.8)
p.label(0.9, 2.85, "O \\ E", 0, -4, PRACTICE, 11.5, "middle", True, True)
p.line([(2.4, 2.45), (2.4, 2.85)], BASE, 1.0, None, 0.9)
p.label(2.4, 2.85, "E \\ F", 0, -4, BASE, 11.5, "middle", True, True)
p.label(1.72, 2.2, "F", 0, 4.5, BG, 11.5, "middle", True, True)
OUT["yak-sikistirma"] = figure(
    500, 175, [p],
    "Ölçülebilir <em>E</em> kümesi, içindeki kapalı <em>F</em> ile dışındaki açık "
    "<em>&#119978;</em> arasında sıkıştırılır (alt satırlar üç kümeyi ayrı ayrı gösterir). Üstteki "
    "şeritte <em>F</em>'nin iki yanındaki ince parçalar <em>E</em> &#8726; <em>F</em>, en dıştakiler "
    "<em>&#119978;</em> &#8726; <em>E</em> kümesidir; teorem, ikisinin de ölçüsünün "
    "<em>&#949;</em>'dan küçük seçilebileceğini söyler.",
    aria="A set E on the line squeezed between a closed set F inside it and an open set O containing it")

# ============================================================ yak-aralik-yaklasimi
# A ragged set E and a finite union U of disjoint open intervals.
E_R = [(0.5, 1.3), (1.45, 1.6), (1.7, 2.6), (3.5, 3.62), (4.2, 5.8), (5.95, 6.05), (7.1, 7.2)]
U_R = [(0.4, 2.7), (4.1, 5.9)]
p = Plot(60, 20, 420, 110, (0.2, 7.5), (0, 2.6))
for y in (2.2, 1.2, 0.2):
    hline_px(p, 0.2, 7.5, y, TEXT, 1.0, 0.35)
for a, b in E_R:
    bar(p, a, b, 2.2, THEORY, 8)
for a, b in U_R:
    bar(p, a, b, 1.2, BASE, 8, 0.75)
    p.label(a, 1.2, "(", -2, 5, BASE, 14, "middle")
    p.label(b, 1.2, ")", 2, 5, BASE, 14, "middle")


def in_any(x, pieces):
    return any(a <= x <= b for a, b in pieces)


diff_u_e = [(0.4, 0.5), (1.3, 1.45), (1.6, 1.7), (2.6, 2.7), (4.1, 4.2), (5.8, 5.9)]
diff_e_u = [(3.5, 3.62), (5.95, 6.05), (7.1, 7.2)]
for a, b in diff_u_e:
    bar(p, a, b, 0.2, BASE, 12, 0.9)
for a, b in diff_e_u:
    bar(p, a, b, 0.2, THEORY, 12, 0.9)
p.label(0.2, 2.2, "E", -8, 4, THEORY, 12.5, "end", True, True)
p.label(0.2, 1.2, "U", -8, 4, BASE, 12.5, "end", True, True)
p.label(0.2, 0.2, "fark", -8, 4, TEXT, 11.5, "end", False, True)
p.label(1.55, 1.2, "I" + subs("1"), 0, -9, BASE, 11, "middle", False, True)
p.label(5.0, 1.2, "I" + subs("2"), 0, -9, BASE, 11, "middle", False, True)
p.label(2.3, 0.2, "U \\ E", 0, 22, BASE, 11, "middle", True, True)
p.label(6.4, 0.2, "E \\ U", 0, 22, THEORY, 11, "middle", True, True)
OUT["yak-aralik-yaklasimi"] = figure(
    520, 170, [p],
    "Düzensiz parçalardan oluşan <em>E</em> ve iki ayrık açık aralığın birleşimi <em>&#119984;</em>. "
    "Alt satırda simetrik farkın iki parçası görülür: <em>&#119984;</em> &#8726; <em>E</em> (yeşil) "
    "aralıkların içinde kalan küçük boşluklar, <em>E</em> &#8726; <em>&#119984;</em> (mavi) aralıkların "
    "dışında kalan küçük parçalardır. Teorem, bu farkın ölçüsünün istenildiği kadar küçük "
    "yapılabileceğini söyler.",
    aria="A ragged set E, a union U of two open intervals, and the two parts of their symmetric difference")

# ============================================================ seritlere-ayrisma
# 1/x^2 on [1, 6] split into the strips [k, k+1).
p = Plot(50, 30, 380, 220, (0.8, 6.45), (0, 1.08))
p.axes((1, 2, 3, 4, 5, 6), (0.5, 1), "x", "y", yfmt=lambda v: fmt(v).replace(".", ","))
for k in range(1, 6):
    col = THEORY if k % 2 else BASE
    xs = [k + j / 60 for j in range(61)]
    p.polygon([(k, 0)] + [(x, 1 / x ** 2) for x in xs] + [(k + 1, 0)], col, 0.28)
    p.vline(k, 0, 1 / k ** 2, TEXT, "3 3", 0.35)
    p.label(k + 0.5, 0, "E" + subs(str(k)), 0, 30, col, 11, "middle", True, True)
xs = [6 + j / 40 * 0.4 for j in range(41)]
p.polygon([(6, 0)] + [(x, 1 / x ** 2) for x in xs] + [(6.4, 0)], REMARK, 0.15)
curve(p, lambda x: 1 / x ** 2, 1, 6.4, THEORY, 2.0)
for k, s in ((1, "1/2"), (2, "1/6"), (3, "1/12"), (4, "1/20"), (5, "1/30")):
    yl = 0.2 if k == 1 else 1 / (k + 0.5) ** 2 + 0.06
    p.label(k + 0.5, yl, s, 0, 0, TEXT, 11, "middle", True)
p.label(1.35, 1 / 1.35 ** 2, "y = 1/x" + sups("2"), 10, -2, THEORY, 12, "start", False, True)
p.label(3.2, 0.62, "şerit alanı: 1/k " + MINUS_S + " 1/(k + 1)", 0, 0, TEXT, 11, "start", False, True)
OUT["seritlere-ayrisma"] = figure(
    470, 300, [p],
    "<em>y</em> = 1/<em>x</em><sup>2</sup> altındaki bölge <em>E<sub>k</sub></em> = [<em>k</em>, "
    "<em>k</em> + 1) şeritlerine ayrılır. Şeritlerin alanları 1/2, 1/6, 1/12, 1/20, 1/30, &#8230; "
    "iç içe sadeleşen bir seri oluşturur ve toplamları 1'dir.",
    aria="Area under y equal 1 over x squared split into unit strips with areas one half, one sixth and so on")

# ============================================================ leg-kuvvet-dizisi
# x^n on [0, 1]; for epsilon = 0.2 the set F = [0, 0.9] carries uniform convergence.
CUT = 0.9
p = Plot(50, 30, 320, 240, (0, 1.02), (0, 1.05))
p.axes((), (0.5, 1), "x", "y", yfmt=lambda v: fmt(v).replace(".", ","))
rect(p, 0, CUT, 0, 1, BASE, 0.10)
rect(p, CUT, 1, 0, 1, PRACTICE, 0.20)
p.vline(CUT, 0, 1.0, TEXT, "5 4", 0.7)
for n in (1, 2, 4, 8, 16):
    curve(p, lambda x, n=n: x ** n, 0, 1, THEORY, 1.7, 300)
    dot(p, (CUT, CUT ** n), PRACTICE, 3.0)
p.label(0, 0, "0", 0, 16, TEXT, 10.5, "middle")
p.label(1, 0, "1", 0, 16, TEXT, 10.5, "middle")
p.label(CUT, 0, "1 " + MINUS_S + " " + EPS + "/2", 3, 16, TEXT, 10.5, "end")
p.label(0.46, 0.46, "n = 1", -6, -6, THEORY, 11, "end", False, True)
p.label(0.04, 0.93, "F = [0, 1 " + MINUS_S + " " + EPS + "/2]", 0, 0, BASE, 11.5, "start", True, True)
p.label(1.0, 1.0, "atılan küme", 2, -12, PRACTICE, 11, "end", True, True)
OUT["leg-kuvvet-dizisi"] = figure(
    420, 305, [p],
    "<em>n</em> = 1, 2, 4, 8, 16 için <em>x<sup>n</sup></em> grafikleri (yukarıdan aşağıya; <em>&#949;</em> = 0,2). "
    "<em>F</em> = [0, 1 &#8722; <em>&#949;</em>/2] üzerinde fark en çok (1 &#8722; "
    "<em>&#949;</em>/2)<sup><em>n</em></sup> olur (işaretli noktalar) ve sıfıra gider; düzgünlüğü bozan "
    "davranış, atılan dar (1 &#8722; <em>&#949;</em>/2, 1] şeridinde toplanmıştır.",
    aria="Graphs of x to the n on the unit interval with the part left of 1 minus epsilon over 2 shaded")

# ============================================================ leg-surekli-genisleme
# f on F = [0,1] u [2,3] and its continuous extension.
p = Plot(50, 20, 400, 150, (-1.3, 4.3), (-0.25, 1.3))
p.axes((-1, 0, 1, 2, 3, 4), (0, 1), "x", "y")
p.line([(-1.3, 0), (0, 0)], PRACTICE, 2.0, "6 4")
p.line([(1, 0), (2, 1)], PRACTICE, 2.0, "6 4")
p.line([(3, 1), (4.3, 1)], PRACTICE, 2.0, "6 4")
p.line([(0, 0), (1, 0)], THEORY, 3.4)
p.line([(2, 1), (3, 1)], THEORY, 3.4)
p.points([(0, 0), (1, 0), (2, 1), (3, 1)], THEORY, 3.6)
p.label(0.5, 0, "f = 0", 0, -9, THEORY, 11.5, "middle", True, True)
p.label(2.5, 1, "f = 1", 0, -9, THEORY, 11.5, "middle", True, True)
p.label(-0.7, 0, "g = 0", 0, -9, PRACTICE, 11, "middle", False, True)
p.label(3.7, 1, "g = 1", 0, -9, PRACTICE, 11, "middle", False, True)
p.label(1.5, 0.5, "g(x) = x " + MINUS_S + " 1", 8, 12, PRACTICE, 11, "start", False, True)
OUT["leg-surekli-genisleme"] = figure(
    480, 205, [p],
    "<em>F</em> = [0, 1] &#8746; [2, 3] üzerinde tanımlı <em>f</em> (kalın) ve sürekli genişlemesi "
    "<em>g</em> (kesikli). Sınırsız boşluklarda <em>g</em> en yakın uçtaki değerde sabit kalır; "
    "(1, 2) boşluğunda uç değerleri birleştiren doğru parçasıdır.",
    aria="A function equal to 0 on 0 to 1 and 1 on 2 to 3, extended continuously by constants and a line segment")

# ============================================================ min-ayrisimi
# ell <= f + g split as h = min{f, ell} plus k = ell - h, and k <= g.
def f_m(x):
    return 1.3 + 0.55 * math.sin(0.75 * x + 0.3)


def g_m(x):
    return 0.85 + 0.35 * math.cos(0.6 * x + 1.0)


def s_m(x):
    return f_m(x) + g_m(x)


def l_m(x):
    return (0.70 + 0.26 * math.sin(1.05 * x - 0.4)) * s_m(x)


L0, L1 = 1.0, 9.0
p = Plot(50, 58, 420, 230, (0, 10), (0, 3.4))
p.axes((), (1, 2, 3), "x", "", yfmt=fmt)
band(p, f_m, s_m, 0, 10, BASE, 0.13)
xs = [L0 + (L1 - L0) * k / 800 for k in range(801)]
for a, b in runs(xs, [l_m(x) > f_m(x) for x in xs]):
    band(p, f_m, l_m, a, b, PRACTICE, 0.40, 120)
curve(p, s_m, 0, 10, TEXT, 1.4, 200, "6 4", 0.8)
curve(p, f_m, 0, 10, TEXT, 1.4, 200, None, 0.8)
curve(p, l_m, L0, L1, PRACTICE, 1.6, 400)
p.vline(L0, 0, l_m(L0), PRACTICE, "2 3", 0.7)
p.vline(L1, 0, l_m(L1), PRACTICE, "2 3", 0.7)
curve(p, lambda x: min(f_m(x), l_m(x)), L0, L1, THEORY, 3.0, 800)
p.label(9.9, s_m(9.9), "f + g", 4, -4, TEXT, 11, "start", False, True)
p.label(9.9, f_m(9.9), "f", 4, 4, TEXT, 11, "start", False, True)
top = p.Y(3.4) - 34
swatch(p, p.x0, top, THEORY, "h = min{f, " + ELL + "}", "bold")
swatch(p, p.x0 + 140, top, PRACTICE, ELL, "line")
swatch(p, p.x0 + 210, top, PRACTICE, "k = " + ELL + " " + MINUS_S + " h", "fill", 0.40)
swatch(p, p.x0, top + 18, BASE, "f ile f + g arası (yüksekliği g)", "fill", 0.18)
swatch(p, p.x0 + 210, top + 18, TEXT, "f + g", "line", dash="6 4")
OUT["min-ayrisimi"] = figure(
    500, 330, [p],
    "<em>&#8467;</em> &#8804; <em>f</em> + <em>g</em> fonksiyonunun ayrışımı. <em>h</em> = min{<em>f</em>, "
    "<em>&#8467;</em>} kalın çizgidir; <em>k</em> = <em>&#8467;</em> &#8722; <em>h</em> yalnız "
    "<em>&#8467;</em>'nin <em>f</em>'yi aştığı yerlerde sıfırdan farklıdır (turuncu). Turuncu bölge, "
    "yüksekliği <em>g</em> olan yeşil şeridin içinde kalır; yani <em>k</em> &#8804; <em>g</em>.",
    aria="Graphs of f, f plus g and ell; h is the minimum of f and ell and k is the part of ell above f")

# ============================================================ fatou-kutle-kaybi
# Two ways mass escapes: into a point and off to infinity.
p1 = Plot(44, 34, 210, 190, (0, 1.08), (0, 4.6))
p1.axes((), (1, 2, 4), "x", "")
panel_title(p1, "Noktaya sıkışan kütle")
for x, s in ((0.25, "1/4"), (0.5, "1/2"), (1, "1")):
    p1.label(x, 0, s, 0, 16, TEXT, 10.5, "middle")
p1.label(0, 0, "0", 0, 16, TEXT, 10.5, "middle")
for n, col in ((1, THEORY), (2, BASE), (4, PRACTICE)):
    rect(p1, 0, 1 / n, 0, n, col, 0.14, col, 1.8)
    p1.label(1 / n, n, "f" + subs(str(n)), 5, -5, col, 12, "start", True, True)
p2 = Plot(320, 34, 240, 190, (0, 6.4), (0, 1.9))
p2.axes((1, 2, 3, 4, 5), (1,), "x", "")
panel_title(p2, "Sonsuza kaçan kütle")
for n in (1, 2, 3, 4):
    rect(p2, n, n + 1, 0, 1, THEORY, 0.12, THEORY, 1.6)
    p2.label(n + 0.5, 1, "f" + subs(str(n)), 0, -7, THEORY, 12, "middle", True, True)
p2.arrow((5.15, 0.5), (6.2, 0.5), PRACTICE, 1.8)
p2.label(5.65, 0.5, INF, 0, -8, PRACTICE, 13, "middle")
OUT["fatou-kutle-kaybi"] = figure(
    580, 260, [p1, p2],
    "Fatou lemmasında kesin eşitsizliğe yol açan iki durum. Solda <em>n</em>&#967;<sub>(0, 1/<em>n</em>]</sub> "
    "dikdörtgenleri daralıp yükselir, sağda &#967;<sub>[<em>n</em>, <em>n</em>+1]</sub> birim kareleri "
    "sağa kayar. Her <em>f<sub>n</sub></em>'nin integrali 1'dir; ama iki dizinin de noktasal limiti "
    "sıfırdır, kütle limitte kaybolur.",
    css_class=WIDE,
    aria="Left: rectangles n times indicator of 0 to 1 over n. Right: unit squares sliding to infinity")

# ============================================================ nl-kuvvet-dizisi
# x^n and its discontinuous pointwise limit; the points x_n = 2^(-1/n).
p = Plot(50, 24, 320, 240, (0, 1.04), (0, 1.08))
p.axes((), (), "x", "y")
p.label(0, 0, "0", 0, 16, TEXT, 10.5, "middle")
p.label(1, 0, "1", 0, 16, TEXT, 10.5, "middle")
ytick(p, 0.5, "1/2")
ytick(p, 1, "1")
p.line([(0, 0.5), (1, 0.5)], TEXT, 1.0, "4 3", 0.4)
for n in (1, 2, 5, 20):
    curve(p, lambda x, n=n: x ** n, 0, 1, THEORY, 1.7, 400)
    dot(p, (2 ** (-1 / n), 0.5), TEXT, 2.8)
p.line([(0, 0), (1, 0)], PRACTICE, 3.2)
hollow(p, (1, 0), PRACTICE, 4.0)
dot(p, (1, 1), PRACTICE, 4.4)
p.label(0.3, 0.3, "x", -6, -4, THEORY, 11.5, "end", False, True)
p.label(0.55, 0.55 ** 2, "x" + sups("2"), -3, -6, THEORY, 11.5, "end", False, True)
p.label(0.75, 0.75 ** 5, "x" + sups("5"), -3, -6, THEORY, 11.5, "end", False, True)
p.label(0.9, 0.9 ** 20, "x" + sups("20"), -3, -8, THEORY, 11.5, "end", False, True)
p.label(0.5, 0, "limit f", 0, 18, PRACTICE, 11.5, "middle", True, True)
OUT["nl-kuvvet-dizisi"] = figure(
    420, 300, [p],
    "<em>x</em>, <em>x</em><sup>2</sup>, <em>x</em><sup>5</sup>, <em>x</em><sup>20</sup> grafikleri ve "
    "noktasal limit <em>f</em> (turuncu): [0, 1) üzerinde 0, <em>x</em> = 1'de 1. İşaretli noktalar "
    "<em>x<sub>n</sub></em> = 2<sup>&#8722;1/<em>n</em></sup> değerleridir; her <em>f<sub>n</sub></em> "
    "orada 1/2 değerini alır ve bu noktalar 1'e kayar. Bu yüzden sup |<em>f</em> &#8722; "
    "<em>f<sub>n</sub></em>| hiçbir zaman 1/2'nin altına inmez.",
    aria="Graphs of x, x squared, x to the 5 and x to the 20 with the discontinuous pointwise limit")

# ============================================================ nl-basit-yaklasim-merdiven
# Splitting the range: phi_eps below f, psi_eps above f, and the sets E_k.
def f_s(x):
    return 2.1 + 1.2 * math.sin(0.9 * x) + 0.45 * math.sin(2.3 * x + 0.5)


p = Plot(70, 20, 400, 220, (0, 10), (0, 4.3))
p.axes((), (), "x", "")
for k in range(5):
    p.line([(0, k), (10, k)], TEXT, 0.8, "3 3", 0.3)
    ytick(p, k, "y" + subs(str(k)), 11)
xs = [10 * j / 2000 for j in range(2001)]
lv = [int(math.floor(f_s(x))) + 1 for x in xs]
segs = []
for lvl in range(1, 5):
    for a, b in runs(xs, [v == lvl for v in lv]):
        segs.append((a, b, lvl))
segs.sort()
for i, (a, b, lvl) in enumerate(segs):
    p.line([(a, lvl - 1), (b, lvl - 1)], BASE, 2.4)
    p.line([(a, lvl), (b, lvl)], PRACTICE, 2.4)
    if i > 0:
        pa, pb, pl = segs[i - 1]
        p.line([(a, min(pl, lvl) - 1), (a, max(pl, lvl))], TEXT, 0.8, "2 3", 0.35)
curve(p, f_s, 0, 10, THEORY, 2.0, 600)
for lvl in range(1, 5):
    yrow = p.Y(0) + 20 + 17 * (lvl - 1)
    p.text_px(p.x0 - 8, yrow + 4, "E" + subs(str(lvl)), TEXT, 11, "end", False, True)
    for a, b, l2 in segs:
        if l2 == lvl:
            p.add(f'<rect x="{p.X(a):.1f}" y="{yrow - 3:.1f}" width="{p.X(b) - p.X(a):.1f}" height="6" '
                  f'fill="{THEORY}" opacity="0.75"/>')
p.label(10, f_s(10), "f", 8, 4, THEORY, 13, "start", True, True)
top = p.Y(4.3) - 10
swatch(p, p.x0 + 20, top, PRACTICE, PSI + subs(EPS), "bold")
swatch(p, p.x0 + 110, top, BASE, PHI + subs(EPS), "bold")
OUT["nl-basit-yaklasim-merdiven"] = figure(
    500, 330, [p],
    "Değer aralığı <em>y</em><sub>0</sub> &lt; <em>y</em><sub>1</sub> &lt; &#8230; &lt; "
    "<em>y</em><sub>4</sub> noktalarıyla bölünür. <em>E<sub>k</sub></em> = {<em>y</em><sub><em>k</em>&#8722;1</sub> "
    "&#8804; <em>f</em> &lt; <em>y<sub>k</sub></em>} kümeleri alttaki satırlarda görülür; birkaç "
    "aralıktan oluşabilirler. <em>&#966;<sub>&#949;</sub></em> her <em>E<sub>k</sub></em> üzerinde "
    "<em>y</em><sub><em>k</em>&#8722;1</sub>, <em>&#968;<sub>&#949;</sub></em> ise <em>y<sub>k</sub></em> "
    "değerini alır; ikisi <em>f</em>'yi alttan ve üstten bir şerit genişliği içinde sıkıştırır.",
    aria="A function sandwiched between two simple functions built from a partition of its range; the level sets E1 to E4 shown below")

# ============================================================ alt-seviye-kumesi
# The sublevel set {f < c}.
def f_a(x):
    return 2.0 + 1.1 * math.sin(0.9 * x) + 0.6 * math.sin(2.1 * x + 1.0)


CL = 2.3
p = Plot(50, 20, 400, 200, (0, 10), (0, 4))
p.axes((), (), "x", "y")
ytick(p, CL, "c", 11.5)
xs = [10 * j / 4000 for j in range(4001)]
below = runs(xs, [f_a(x) < CL for x in xs])
curve(p, f_a, 0, 10, THEORY, 2.0, 600)
p.line([(0, CL), (10, CL)], PRACTICE, 1.4, "6 4")
for a, b in below:
    p.line([(x, f_a(x)) for x in xs if a <= x <= b], PRACTICE, 2.8)
    p.line([(a, 0), (b, 0)], PRACTICE, 4.0)
    for e in (a, b):
        if 0 < e < 10:
            p.vline(e, 0, CL, TEXT, "2 3", 0.4)
            hollow(p, (e, 0), PRACTICE, 3.6)
        else:
            dot(p, (e, 0), PRACTICE, 3.6)
mid = max(below, key=lambda ab: ab[1] - ab[0])
p.label((mid[0] + mid[1]) / 2, 0, "{f &lt; c}", 0, 18, PRACTICE, 12, "middle", True, True)
p.label(10, CL, "y = c", 8, 4, PRACTICE, 11.5, "start", False, True)
p.label(0.2, 3.85, "y = f(x)", 0, 0, THEORY, 11.5, "start", False, True)
OUT["alt-seviye-kumesi"] = figure(
    480, 270, [p],
    "Bir <em>f</em> grafiği ve <em>y</em> = <em>c</em> doğrusu. Grafiğin doğrunun altında kaldığı "
    "noktalar <em>x</em> ekseninde kalın parçalar olarak işaretlidir; bunların birleşimi "
    "{<em>f</em> &lt; <em>c</em>} kümesidir. <em>f</em>'nin ölçülebilir olması, her <em>c</em> için "
    "bu kümenin ölçülebilir olmasıdır.",
    aria="Graph of a function and a horizontal line y equal c; the set where the graph lies below the line is marked on the x axis")

# ============================================================ vitali-otelemeleri
# Disjoint rational translates of C_n, all trapped inside [-n, n+1] (n = 1).
CX = [-0.97, -0.78, -0.72, -0.51, 0.61, 0.68, 0.77, 0.83]
QS = [(0, "0"), (1 / 3, "1/3"), (2 / 3, "2/3"), (1, "1")]
COLS = [THEORY, BASE, PRACTICE, REMARK]
allpts = sorted(x + q for q, _ in QS for x in CX)
assert min(b - a for a, b in zip(allpts, allpts[1:])) > 0.03, "translates too close to read"
p = Plot(110, 34, 380, 190, (-1.3, 2.3), (0, 6))
rect(p, -1, 2, 0.3, 5.7, REMARK, 0.07, REMARK, 1.0, "4 3")
p.label(0.5, 5.7, "[" + MINUS_S + "n, n + 1]", 0, -8, REMARK, 11.5, "middle", True, True)
for i, ((q, qs), col) in enumerate(zip(QS, COLS)):
    y = 5 - i
    hline_px(p, -1.3, 2.3, y, TEXT, 0.8, 0.3)
    p.points([(x + q, y) for x in CX], col, 3.4)
    p.label(-1.3, y, "C" + subs("n") + " + " + qs, -8, 4, col, 11.5, "end", False, True)
y = 0.9
hline_px(p, -1.3, 2.3, y, TEXT, 0.8, 0.3)
for (q, _), col in zip(QS, COLS):
    p.points([(x + q, y) for x in CX], col, 3.4)
p.label(-1.3, y, "birleşim", -8, 4, TEXT, 11.5, "end", False, True)
hline_px(p, -1.3, 2.3, 0.0, TEXT, 1.0, 0.5)
for x, s in ((-1, MINUS_S + "n"), (0, "0"), (1, "n"), (2, "n + 1")):
    tick(p, x, 0.0, s, TEXT, 10.5, 16)
OUT["vitali-otelemeleri"] = figure(
    520, 265, [p],
    "<em>C<sub>n</sub></em> &#8838; [&#8722;<em>n</em>, <em>n</em>] kümesinin [0, 1]'deki birkaç "
    "rasyonel sayı kadar ötelemeleri (şematik). Ötelemeler ikişer ikişer ayrıktır ve hepsi "
    "[&#8722;<em>n</em>, <em>n</em> + 1] aralığında kalır. Sonsuz sayıda ayrık kopyanın ölçüleri toplamı "
    "2<em>n</em> + 1'i aşamayacağından <em>m</em>(<em>C<sub>n</sub></em>) = 0 olmak zorundadır.",
    aria="Rational translates of a bounded set drawn as dots in rows; all are disjoint and lie in a bounded interval")

# ============================================================ rl-basamak-yaklasim
# Lower and upper step functions of a partition; the gap is U(f,P) - L(f,P).
def f_r(x):
    return 1.6 + 0.7 * math.sin(1.3 * x + 0.2) + 0.35 * math.sin(3.1 * x)


PX = [0.0, 0.9, 2.1, 3.0, 4.2, 5.0]
p = Plot(50, 50, 420, 220, (0, 5.2), (0, 3.0))
p.axes((), (1, 2), "x", "y")
for i in range(5):
    a, b = PX[i], PX[i + 1]
    vals = [f_r(a + (b - a) * k / 300) for k in range(301)]
    mi, Mi = min(vals), max(vals)
    rect(p, a, b, 0, mi, THEORY, 0.16, THEORY, 1.0)
    hatch(p, a, b, mi, Mi, PRACTICE, 5.0, 0.85, 0.65)
    rect(p, a, b, mi, Mi, PRACTICE, 0.0, PRACTICE, 1.2)
    if i == 2:
        p.label((a + b) / 2, mi, "m" + subs("3"), 0, 15, THEORY, 11.5, "middle", False, True)
        p.label((a + b) / 2, Mi, "M" + subs("3"), 0, -6, PRACTICE, 11.5, "middle", False, True)
curve(p, f_r, 0, 5, THEORY, 2.2, 400)
for i, x in enumerate(PX):
    s = "a" if i == 0 else ("b" if i == 5 else "x" + subs(str(i)))
    p.label(x, 0, s, 0, 16, TEXT, 11.5, "middle", False, True)
top = p.Y(3.0) - 22
swatch(p, p.x0, top, THEORY, "alt basamak (m" + subs("i") + ")", "fill", 0.25)
swatch(p, p.x0 + 150, top, PRACTICE, "üst basamak (M" + subs("i") + ")", "line")
swatch(p, p.x0 + 300, top, PRACTICE, "U(f, P) " + MINUS_S + " L(f, P)", "hatch")
OUT["rl-basamak-yaklasim"] = figure(
    500, 320, [p],
    "Beş alt aralıklı bir <em>P</em> bölüntüsü için alt basamak fonksiyonu (dolgulu, "
    "<em>m<sub>i</sub></em> yüksekliğinde) ve üst basamak fonksiyonu (<em>M<sub>i</sub></em> "
    "yüksekliğinde). Birincinin integrali <em>L</em>(<em>f</em>, <em>P</em>), ikincininki "
    "<em>U</em>(<em>f</em>, <em>P</em>)'dir; taralı şeritlerin toplam alanı aradaki farktır.",
    aria="A continuous function between lower and upper step functions of a partition with five subintervals")

# ============================================================ borel-olculebilir-kapsamalar
# Nested families of subsets of R, with an example in each layer.
W, H = 560, 380
p = Plot(0, 0, W, H, (0, W), (H, 0))           # pixel coordinates, y downward
round_rect(p, 10, 10, 540, 360, REMARK, 0.05, 18)
round_rect(p, 30, 44, 500, 300, THEORY, 0.06, 16)
round_rect(p, 50, 78, 300, 252, BASE, 0.07, 14)
round_rect(p, 68, 112, 264, 186, PRACTICE, 0.06, 12)
round_rect(p, 86, 146, 110, 64, THEORY, 0.10, 10, 1.2)
round_rect(p, 206, 146, 110, 64, THEORY, 0.10, 10, 1.2)
p.add(f'<ellipse cx="410" cy="205" rx="92" ry="66" fill="{PRACTICE}" fill-opacity="0.07" '
      f'stroke="{PRACTICE}" stroke-width="1.3" stroke-dasharray="5 4"/>')
T = p.text_px
T(24, 32, "Bütün alt kümeler", REMARK, 12, "start", True)
T(44, 66, "M: ölçülebilir kümeler", THEORY, 12, "start", True)
T(64, 100, "B: Borel kümeleri", BASE, 12, "start", True)
T(82, 134, "F" + subs("&#963;") + " ve G" + subs("&#948;") + " kümeleri", PRACTICE, 11.5, "start", True)
T(141, 168, "açık", THEORY, 11.5, "middle", True)
T(261, 168, "kapalı", THEORY, 11.5, "middle", True)
T(141, 192, "(0, 1)", TEXT, 12, "middle", False, True)
T(261, 192, "{0}", TEXT, 12, "middle", False, True)
T(200, 242, "rasyonel sayılar (bir F" + subs("&#963;") + " kümesi)", TEXT, 11.5, "middle", False, True)
T(200, 318, "G" + subs("&#948;&#963;") + ", F" + subs("&#963;&#948;") + ", &#8230;", TEXT, 11.5,
  "middle", False, True)
T(410, 166, "dış ölçüsü 0", PRACTICE, 11.5, "middle", True)
T(430, 200, "Cantor kümesinin", TEXT, 11, "middle", False, True)
T(430, 215, "Borel olmayan", TEXT, 11, "middle", False, True)
T(430, 230, "bir alt kümesi", TEXT, 11, "middle", False, True)
T(280, 361, "Vitali kümesi", TEXT, 12, "middle", False, True)
OUT["borel-olculebilir-kapsamalar"] = figure(
    W, H, [p],
    "Alt küme ailelerinin kapsama şeması. Açık ve kapalı kümeler hem <em>F<sub>&#963;</sub></em> hem "
    "<em>G<sub>&#948;</sub></em> kümeleridir; bunlar Borel σ-cebiri <em>&#8492;</em>'nin içindedir. "
    "<em>&#8499;</em> ise <em>&#8492;</em>'yi ve dış ölçüsü sıfır olan bütün kümeleri (kesikli bölge) "
    "içerir. Her katmanda birer örnek: (0, 1), {0}, &#8474;, Cantor kümesinin Borel olmayan bir alt "
    "kümesi ve ölçülemeyen Vitali kümesi.",
    aria="Nested families: open and closed sets, F sigma and G delta sets, Borel sets, measurable sets, all subsets, with examples")

# ============================================================ sivrilen-tepeler
# f_n = 2n chi_[1/(2n), 1/n], n = 1..4: area 1, sliding into 0.
p = Plot(50, 24, 340, 250, (0, 1.05), (0, 8.7))
p.axes((), (2, 4, 6, 8), "x", "y")
for x, s in ((1 / 8, "1/8"), (0.25, "1/4"), (0.5, "1/2"), (1, "1")):
    p.label(x, 0, s, 0, 16, TEXT, 10.5, "middle")
p.label(0, 0, "0", 0, 16, TEXT, 10.5, "middle")
for n, col in ((1, THEORY), (2, BASE), (3, PRACTICE), (4, REMARK)):
    rect(p, 1 / (2 * n), 1 / n, 0, 2 * n, col, 0.16, col, 1.8)
    p.label(1 / n, 2 * n, "f" + subs(str(n)), 4, -5, col, 12, "start", True, True)
OUT["sivrilen-tepeler"] = figure(
    420, 310, [p],
    "<em>n</em> = 1, 2, 3, 4 için <em>f<sub>n</sub></em> = 2<em>n</em>&#967;<sub><em>I<sub>n</sub></em></sub>, "
    "<em>I<sub>n</sub></em> = [1/(2<em>n</em>), 1/<em>n</em>]. Her tepenin alanı 1'dir; tepeler "
    "daralıp yükselerek sıfıra doğru kayar ve her sabit <em>x</em> &gt; 0 noktasını bir süre sonra "
    "terk eder.",
    aria="Four rectangles of height 2n over the interval from 1 over 2n to 1 over n, each of area one")

# ============================================================ artan-halkalar
# A_1 in A_2 in A_3 and the rings C_k = A_k minus A_{k-1}.
p = Plot(20, 20, 330, 264, (-2.5, 2.5), (-2.0, 2.0))
WOB = ((0.10, 2, 0.6), (0.06, 3, 1.9))


def blob_k(r, cx=0.0, cy=0.0):
    return blob(cx, cy, r, [(a * r, k, ph) for a, k, ph in WOB])


def path_of(pts):
    return "M" + " L".join(p.P(x, y) for x, y in pts) + " Z"


RS = [(0.62, 0.10, 0.0), (1.20, 0.04, -0.03), (1.80, 0.0, 0.0)]
shapes = [blob_k(r, cx, cy) for r, cx, cy in RS]
fills = [(THEORY, 0.40), (BASE, 0.28), (PRACTICE, 0.22)]
for i in (2, 1):
    col, op = fills[i]
    p.add(f'<path d="{path_of(shapes[i])} {path_of(shapes[i - 1])}" fill="{col}" fill-opacity="{op}" '
          f'fill-rule="evenodd" stroke="none"/>')
p.add(f'<path d="{path_of(shapes[0])}" fill="{THEORY}" fill-opacity="0.40" stroke="none"/>')
for i, s in enumerate(shapes):
    closed_curve(p, s, (THEORY, BASE, PRACTICE)[i], 1.6)
p.label(0.10, 0.0, "C" + subs("1") + " = A" + subs("1"), 0, 4, TEXT, 12, "middle", True, True)
p.label(0.0, 0.93, "C" + subs("2"), 0, 4, TEXT, 12, "middle", True, True)
p.label(0.0, 1.55, "C" + subs("3"), 0, 4, TEXT, 12, "middle", True, True)
for i, (r, cx, cy) in enumerate(RS):
    a = -0.62
    rr = r * (1 + 0.10 * math.cos(2 * a + 0.6) + 0.06 * math.cos(3 * a + 1.9))
    x, y = cx + rr * math.cos(a), cy + rr * math.sin(a)
    p.label(x, y, "A" + subs(str(i + 1)), 5, 12, (THEORY, BASE, PRACTICE)[i], 12, "start", True, True)
OUT["artan-halkalar"] = figure(
    370, 300, [p],
    "Artan <em>A</em><sub>1</sub> &#8838; <em>A</em><sub>2</sub> &#8838; <em>A</em><sub>3</sub> kümeleri ve "
    "aralarındaki halkalar <em>C<sub>k</sub></em> = <em>A<sub>k</sub></em> &#8726; "
    "<em>A</em><sub><em>k</em>&#8722;1</sub>. Halkalar ayrıktır ve ilk <em>n</em> tanesinin birleşimi "
    "<em>A<sub>n</sub></em>'dir; bu yüzden birleşimin ölçüsü halkaların ölçüleri toplamıdır.",
    aria="Three nested sets A1, A2, A3 with the rings between them shaded in different tones")


# ---------------------------------------------------------------------------
for name, content in OUT.items():
    with io.open(os.path.join(OUT_DIR, "real-%s.md" % name), "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
print("generated:", ", ".join(OUT))
