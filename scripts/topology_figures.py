# -*- coding: utf-8 -*-
"""
Generates the SVG figures used in the "Topoloji" chapters (dersler/olasilik-teorisi).

Same authoring flow as scripts/analysis_figures.py: the figures are NOT produced
at build time. Run this script, then

    python scripts/center_figures.py "topology-*.md"

(which measures each drawing and centers it in its viewBox) and paste the
resulting markup into the .qmd files — inside the theorem/example/proof box the
figure explains, never inside a definition box. Building the books therefore
needs neither Python nor Jupyter; CI runs Quarto alone.

The captions are Turkish on purpose — they are the text shown on the site.

Usage:   python scripts/topology_figures.py && python scripts/center_figures.py "topology-*.md"
Output:  scripts/_figures/topology-<name>.md
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

# ============================================================ altuzay-uyusmayan-ornek
# Y = [0,1) u {2} inside R: the singleton {2} is open in the subspace topology (caught by the
# interval (3/2, 5/2)) but not in the order topology, whose basis elements around 2 are
# (c, 2] = (c, 1) u {2}.  Data y = pixel y (identity map).
W_F, H_F = 400, 236
p = Plot(16, 0, 368, H_F, (-0.55, 2.75), (H_F, 0))
Y_TOP, Y_LINE, Y_BOT = 54, 122, 178     # the three rows (pixel y)
C = 0.45                                 # the point c of the basis element (c, 2]


def cup(px, py, color=TEXT):
    """Hand-drawn union sign (the render font lacks U+222A); centred at (px, py)."""
    p.add('<path d="M%.1f %.1f L%.1f %.1f A2.8 2.8 0 0 0 %.1f %.1f L%.1f %.1f" fill="none" '
          'stroke="%s" stroke-width="1.1" stroke-linecap="round"/>'
          % (px - 2.8, py - 8, px - 2.8, py - 3, px + 2.8, py - 3, px + 2.8, py - 8, color))


def union_label(x, py, left, right, color=TEXT, size=11, bold=False):
    """'left  u  right' centred (in x) at data x, baseline py."""
    cx = p.X(x)
    p.text_px(cx - 6, py, left, color, size, "end", bold)
    cup(cx, py, color)
    p.text_px(cx + 6, py, right, color, size, "start", bold)


# ---- the number line carrying Y = [0, 1) u {2} --------------------------------
p.arrow((-0.5, Y_LINE), (2.73, Y_LINE), TEXT, 1.2, 7.0, opacity=0.6)
p.label(2.73, Y_LINE, "&#8477;", 0, -8, TEXT, 11.5, "end", True, False)
for x, s, col in ((0, "0", TEXT), (1, "1", TEXT), (1.5, "3/2", THEORY), (2, "2", TEXT),
                  (2.5, "5/2", THEORY), (C, "c", PRACTICE)):
    p.line([(x, Y_LINE - 4), (x, Y_LINE + 4)], TEXT, 1.2)
    p.label(x, Y_LINE, s, 0, 18, col, 11, "middle", col is not TEXT, col is PRACTICE)
p.line([(0, Y_LINE), (1, Y_LINE)], BASE, 3.4)
dot(p, (0, Y_LINE), BASE, 4.2)
hollow(p, (1, Y_LINE), BASE, 3.8, 1.7)
dot(p, (2, Y_LINE), BASE, 4.6)
union_label(0.5, Y_LINE - 12, "Y = [0, 1)", "{2}", BASE, 11, True)

# the point 2 seen from both rows
guide(p, [(2, Y_TOP), (2, Y_BOT)], TEXT, 0.4)
guide(p, [(C, Y_LINE), (C, Y_BOT)], PRACTICE, 0.5)

# ---- top row: (3/2, 5/2) is open in R and meets Y only at 2 ---------------------
rect(p, 1.5, 2.5, Y_TOP - 7, Y_LINE, THEORY, 0.08)
p.line([(1.5, Y_TOP), (2.5, Y_TOP)], THEORY, 2.4)
hollow(p, (1.5, Y_TOP), THEORY, 3.6, 1.6)
hollow(p, (2.5, Y_TOP), THEORY, 3.6, 1.6)
dot(p, (2, Y_TOP), THEORY, 4.6)
p.label(1.5, Y_TOP, "(3/2, 5/2) &#8745; Y = {2}", -14, -2, TEXT, 11, "end", False, False)
p.label(1.5, Y_TOP, "{2} alt uzay topolojisinde açık", -14, 13, THEORY, 10.5, "end", True, True)

# ---- bottom row: the basis element (c, 2] of the order topology ---------------
rect(p, C, 1, Y_LINE, Y_BOT + 7, PRACTICE, 0.08)
p.line([(C, Y_BOT), (1, Y_BOT)], PRACTICE, 2.4)
hollow(p, (C, Y_BOT), PRACTICE, 3.6, 1.6)
hollow(p, (1, Y_BOT), PRACTICE, 3.6, 1.6)
dot(p, (2, Y_BOT), PRACTICE, 4.6)
union_label(1.5, Y_BOT + 26, "(c, 2] = (c, 1)", "{2}", TEXT, 11)
p.text_px(p.X(1.5), Y_BOT + 42, "{2} sıra topolojisinde açık değil", PRACTICE, 10.5, "middle", True, True)
p.label(C, Y_BOT, "2'yi içeren", -14, -2, PRACTICE, 10.5, "end", False, True)
p.label(C, Y_BOT, "her baz elemanı", -14, 12, PRACTICE, 10.5, "end", False, True)

OUT["altuzay-uyusmayan-ornek"] = figure(
    W_F, H_F, [p],
    "<em>Y</em> = [0, 1) &#8746; {2} üzerinde alt uzay topolojisi ile sıra topolojisi çakışmaz. "
    "Üstte &#8477;'nin (3/2, 5/2) açık aralığı <em>Y</em>'yi yalnızca 2 noktasında keser; bu yüzden {2} alt "
    "uzay topolojisinde açıktır. Altta sıra topolojisinde 2'yi içeren bir baz elemanı, "
    "<em>c</em> &#8712; [0, 1) için (<em>c</em>, 2] = (<em>c</em>, 1) &#8746; {2}, görülüyor: her böyle küme "
    "[0, 1)'den bir parça da taşır, dolayısıyla {2} sıra topolojisinde açık değildir.",
    aria="Sayi dogrusunda Y = [0,1) birlesim {2}: sifirda dolu, birde bos uclu kalin aralik ve 2'de tek nokta; "
         "ustte (3/2, 5/2) acik araligi yalnizca 2'yi yakaliyor, altta (c, 2] = (c, 1) birlesim {2} baz elemani")

# ============================================================ altuzay-yde-acik
# Y = [0,1] as a subspace of R: the set U = [0, 1/2) is open in Y (it is Y meets (-1, 1/2))
# but not open in R.  Three rows over one number line; data y = pixel y (identity).
W_F, H_F = 400, 228
p = Plot(16, 0, 368, H_F, (-1.45, 1.45), (H_F, 0))
Y_TOP, Y_MID, Y_U, Y_LINE = 40, 86, 132, 172   # the rows and the number line (pixel y)
HALF = "1/2"

# the strip [0, 1/2) that survives the intersection, running through every row
rect(p, 0, 0.5, Y_TOP - 8, Y_U + 8, PRACTICE, 0.09)
guide(p, [(0, Y_TOP - 8), (0, Y_LINE)], PRACTICE, 0.5)
guide(p, [(0.5, Y_TOP - 8), (0.5, Y_LINE)], PRACTICE, 0.5)

# the number line with its ticks
p.arrow((-1.4, Y_LINE), (1.43, Y_LINE), TEXT, 1.2, 7.0, opacity=0.6)
p.label(1.43, Y_LINE, "&#8477;", 0, -8, TEXT, 11.5, "end", True, False)
for x, s in ((-1, MINUS_S + "1"), (0, "0"), (0.5, HALF), (1, "1")):
    p.line([(x, Y_LINE - 4), (x, Y_LINE + 4)], TEXT, 1.2)
    p.label(x, Y_LINE, s, 0, 18, TEXT, 11, "middle", False, False)

# top row: the open interval (-1, 1/2), open in R
p.line([(-1, Y_TOP), (0.5, Y_TOP)], THEORY, 2.4)
hollow(p, (-1, Y_TOP), THEORY, 3.6, 1.6)
hollow(p, (0.5, Y_TOP), THEORY, 3.6, 1.6)
p.label(0.5, Y_TOP, "(" + MINUS_S + "1, " + HALF + ")", 14, -3, TEXT, 11, "start", False, False)
p.label(0.5, Y_TOP, "&#8477;'de açık", 14, 12, THEORY, 10.5, "start", False, True)

# middle row: the subspace Y = [0, 1], closed ends
p.line([(0, Y_MID), (1, Y_MID)], BASE, 3.2)
dot(p, (0, Y_MID), BASE, 4.0)
dot(p, (1, Y_MID), BASE, 4.0)
p.label(0, Y_MID, "Y = [0, 1]", -14, 4, TEXT, 11, "end", False, False)
p.label(1, Y_MID, "alt uzay", 14, 4, BASE, 10.5, "start", False, True)

# bottom row: U = Y n (-1, 1/2) = [0, 1/2): closed at 0, open at 1/2
p.line([(0, Y_U), (0.5, Y_U)], PRACTICE, 2.8)
dot(p, (0, Y_U), PRACTICE, 4.2)
hollow(p, (0.5, Y_U), PRACTICE, 3.6, 1.6)
p.label(0.5, Y_U, "U = [0, " + HALF + ")", 14, 4, PRACTICE, 11, "start", True, False)
p.label(0, Y_U, "Y &#8745; (" + MINUS_S + "1, " + HALF + ")", -14, 4, TEXT, 10.5, "end", False, False)

# the verdict
p.text_px(200, 214, "U, Y'de açık ama &#8477;'de açık değil", PRACTICE, 11.5, "middle", True, False)

OUT["altuzay-yde-acik"] = figure(
    W_F, H_F, [p],
    "<em>Y</em> = [0, 1] alt uzayında <em>U</em> = [0, 1/2) kümesi. Üstteki (&#8722;1, 1/2) aralığı "
    "&#8477;'de açıktır; <em>Y</em> ile kesişimi taranmış şerit, yani 0'ı içeren ama 1/2'yi içermeyen "
    "<em>U</em> = [0, 1/2) kümesidir. Bu kesişim tanım gereği <em>Y</em>'de açıktır; ancak 0'ı içeren her "
    "açık aralık 0'ın soluna, dolayısıyla <em>U</em>'nun dışına taştığından <em>U</em>, &#8477;'de açık değildir.",
    aria="Sayi dogrusu uzerinde uc satir: ustte (-1, 1/2) acik araligi, ortada Y = [0, 1] kapali araligi, "
         "altta kesisimleri U = [0, 1/2); U sifirda dolu, 1/2'de bos uclu")

# ============================================================ atama-kurali-oklar
# Two arrow diagrams between C = {1, 2, 3} and D = {a, b}: r_1 is an assignment rule, r_2 is not
# because 1 is sent to both a and b.  Pixel drawing on an identity plot, so the ovals keep their shape.
W_F, H_F = 560, 226
p = Plot(0, 0, W_F, H_F, (0, W_F), (H_F, 0))     # identity map: data = pixels

C_PTS = {"1": 78, "2": 118, "3": 158}    # element -> pixel y
D_PTS = {"a": 98, "b": 138}
CX_OFF, DX_OFF = 0, 118                  # oval centres relative to the diagram's left edge
RX, RY_C, RY_D = 30, 60, 44
OVAL_Y = 118


def oval(cx, cy, rx, ry):
    p.add('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s" fill-opacity="0.06" '
          'stroke="%s" stroke-width="1.2"/>' % (cx, cy, rx, ry, THEORY, TEXT))


def diagram(left, title, pairs, bad_from, verdict, verdict_color):
    cx, dx = left + CX_OFF, left + DX_OFF
    p.text_px((cx + dx) / 2, 22, title, TEXT, 12, "middle", True)
    oval(cx, OVAL_Y, RX, RY_C)
    oval(dx, OVAL_Y, RX, RY_D)
    p.text_px(cx, OVAL_Y - RY_C - 8, "C", TEXT, 12, "middle", True, True)
    p.text_px(dx, OVAL_Y - RY_D - 8, "D", TEXT, 12, "middle", True, True)
    # the arrows first, so the dots sit on top of the shafts
    for c, d in pairs:
        hot = c == bad_from
        p.arrow((cx + 9, C_PTS[c]), (dx - 9, D_PTS[d]),
                PRACTICE if hot else THEORY, 2.4 if hot else 1.7, 8.5 if hot else 7.5)
    for c, y in C_PTS.items():
        hot = c == bad_from
        dot(p, (cx, y), PRACTICE if hot else TEXT, 3.6 if hot else 3.2)
        p.text_px(cx - 10, y + 4, c, PRACTICE if hot else TEXT, 11.5, "end", hot)
    for d, y in D_PTS.items():
        dot(p, (dx, y), TEXT, 3.2)
        p.text_px(dx + 10, y + 4, d, TEXT, 11.5, "start", False, True)
    p.text_px((cx + dx) / 2, OVAL_Y + RY_C + 30, verdict, verdict_color, 11.5, "middle", True)


diagram(88, "r" + subs("1") + " = {(1, a), (2, a), (3, b)}",
        [("1", "a"), ("2", "a"), ("3", "b")], None, "atama kuralı", BASE)
diagram(358, "r" + subs("2") + " = {(1, a), (1, b), (2, a)}",
        [("1", "a"), ("1", "b"), ("2", "a")], "1", "atama kuralı değil: 1 hem a'ya hem b'ye", PRACTICE)

OUT["atama-kurali-oklar"] = figure(
    W_F, H_F, [p],
    "<em>C</em> = {1, 2, 3} ile <em>D</em> = {<em>a</em>, <em>b</em>} arasında iki ok şeması. Solda "
    "<em>r</em><sub>1</sub> bir atama kuralıdır: her elemandan en fazla bir ok çıkar; <em>a</em>'ya iki "
    "okun gelmesi koşulu bozmaz. Sağda <em>r</em><sub>2</sub> atama kuralı değildir, çünkü 1 elemanından "
    "hem <em>a</em>'ya hem <em>b</em>'ye ok çıkar; koşul yalnızca birinci bileşenleri kısıtlar.",
    css_class=WIDE,
    aria="Iki ok semasi: solda C kumesinden D kumesine her elemandan tek ok cikan r1; sagda 1 elemanindan "
         "iki ok cikan ve atama kurali olmayan r2, iki ok vurgulu")

# ============================================================ baz-alt-limit-ince
# The standard topology is coarser than the lower limit topology: for x in (a, b) the
# half-open basis element [x, b) contains x and sits inside (a, b).
# Data y is measured in pixels from the bottom of the panel, so rows are placed directly.
p = Plot(16, 14, 368, 132, (0, 10), (0, 132))
Y_LINE = 22                     # the number line
Y_OPEN, Y_HALF = 104, 62        # the rows for (a, b) and [x, b)
A, X, B = 3.6, 5.4, 8.6

# light shading under each interval, down to the line
rect(p, A, B, Y_LINE, Y_OPEN, THEORY, 0.07)
rect(p, X, B, Y_LINE, Y_HALF, PRACTICE, 0.10)
# the number line
p.arrow((0.15, Y_LINE), (9.95, Y_LINE), TEXT, 1.2, 7.0, opacity=0.6)
p.label(9.9, Y_LINE, "&#8477;", 0, -9, TEXT, 11.5, "end", True, False)
for v, s, col in ((A, "a", TEXT), (X, "x", PRACTICE), (B, "b", TEXT)):
    p.line([(v, Y_LINE - 4), (v, Y_LINE + 4)], col, 1.3)
    p.label(v, Y_LINE, s, 0, 19, col, 12, "middle", v == X, True)
# dashed guides from the endpoints down to the line
guide(p, [(A, Y_LINE + 4), (A, Y_OPEN)], TEXT, 0.4)
guide(p, [(B, Y_LINE + 4), (B, Y_OPEN)], TEXT, 0.4)
guide(p, [(X, Y_LINE + 4), (X, Y_HALF)], PRACTICE, 0.5)
# (a, b): both ends open
p.line([(A, Y_OPEN), (B, Y_OPEN)], THEORY, 2.6)
hollow(p, (A, Y_OPEN), THEORY, 3.6, 1.6)
hollow(p, (B, Y_OPEN), THEORY, 3.6, 1.6)
p.text_px(p.X(A) - 12, p.Y(Y_OPEN) + 4, "(a, b)", THEORY, 11.5, "end", True, True)
# [x, b): closed at x, open at b
p.line([(X, Y_HALF), (B, Y_HALF)], PRACTICE, 2.6)
dot(p, (X, Y_HALF), PRACTICE, 3.8)
hollow(p, (B, Y_HALF), PRACTICE, 3.6, 1.6)
p.text_px(p.X(X) - 12, p.Y(Y_HALF) + 4, "[x, b)", PRACTICE, 11.5, "end", True, True)
# the point x on the line
dot(p, (X, Y_LINE), PRACTICE, 4.0)
# the inclusion, stated once above the rows
p.text_px(p.X((A + B) / 2), p.Y(Y_OPEN) - 14,
          "[x, b) içindeki her z için a &lt; x " + LEQ_S + " z &lt; b",
          TEXT, 10.5, "middle", False, True)

OUT["baz-alt-limit-ince"] = figure(
    400, 176, [p],
    "Standart topoloji alt limit topolojisinden daha kabadır. <em>x</em> noktası (<em>a</em>, <em>b</em>) açık "
    "aralığında verildiğinde, alt limit bazının [<em>x</em>, <em>b</em>) elemanı hem <em>x</em>'i içerir hem de "
    "(<em>a</em>, <em>b</em>)'nin içine sığar: <em>z</em> &#8712; [<em>x</em>, <em>b</em>) ise "
    "<em>a</em> &lt; <em>x</em> &#8804; <em>z</em> &lt; <em>b</em>. İnce olma ölçütünün (ii) koşulu böylece sağlanır ve "
    "her standart açık küme &#8477;<sub>&#8467;</sub>'de de açıktır.",
    aria="Sayi dogrusunda uclari acik (a, b) araligi, icinde x noktasi ve hemen altinda sol ucu kapali sag ucu acik [x, b) araligi")

# ============================================================ baz-daireler
# Condition (B2) for the basis of open discs in the plane: x lies in B1 n B2, and the disc
# B3 = B(x, s) with s = min{s1, s2} (distances from x to the two boundary circles) fits
# inside the lens-shaped intersection.  Equal px-per-unit on both axes.
PW, PH = 384.0, 239.0
XR = 3.2
YR = XR * PH / PW
p = Plot(8, 8, PW, PH, (-XR, XR), (-YR, YR))

C1, R1 = (-0.95, 0.05), 1.75
C2, R2 = (1.05, -0.30), 1.60
X = (0.05, 0.0)


def dist(u, v):
    return math.hypot(u[0] - v[0], u[1] - v[1])


def circ(c, r, n=120):
    return [(c[0] + r * math.cos(2 * math.pi * k / n), c[1] + r * math.sin(2 * math.pi * k / n))
            for k in range(n)]


def lens(ca, ra, cb, rb):
    """Intersection of two discs as a polygon (points of circle A inside B, then of B inside A)."""
    pa = [q for q in circ(ca, ra, 360) if dist(q, cb) < rb]
    pb = [q for q in circ(cb, rb, 360) if dist(q, ca) < ra]
    # order each arc by angle around the midpoint of the lens so the polygon closes cleanly
    m = ((ca[0] + cb[0]) / 2, (ca[1] + cb[1]) / 2)
    return sorted(pa + pb, key=lambda q: math.atan2(q[1] - m[1], q[0] - m[0]))


S1 = R1 - dist(X, C1)
S2 = R2 - dist(X, C2)
S = min(S1, S2)
# where the rays c1 -> x and c2 -> x reach their own boundary circles
P1 = (C1[0] + R1 * (X[0] - C1[0]) / dist(X, C1), C1[1] + R1 * (X[1] - C1[1]) / dist(X, C1))
P2 = (C2[0] + R2 * (X[0] - C2[0]) / dist(X, C2), C2[1] + R2 * (X[1] - C2[1]) / dist(X, C2))

# the two open discs and their intersection
p.polygon(circ(C1, R1), THEORY, 0.10)
p.polygon(circ(C2, R2), THEORY, 0.10)
p.polygon(lens(C1, R1, C2, R2), THEORY, 0.22)
p.circle(C1[0], C1[1], R1, THEORY, 1.6)
p.circle(C2[0], C2[1], R2, THEORY, 1.6)
# radii from the centres through x, continued to the boundary: the pieces beyond x are s1, s2
guide(p, [C1, X], TEXT, 0.55)
guide(p, [C2, X], TEXT, 0.55)
p.line([X, P1], PRACTICE, 1.5)
p.line([X, P2], PRACTICE, 1.5)
# the small disc B3 = B(x, s) centred at x
p.polygon(circ(X, S), PRACTICE, 0.22)
p.circle(X[0], X[1], S, PRACTICE, 1.7)
# centres and the point x
dot(p, C1, TEXT, 3.0)
dot(p, C2, TEXT, 3.0)
dot(p, X, PRACTICE, 4.2)
# labels
# one radius of each disc, drawn away from the crowded middle
E1 = (C1[0] + R1 * math.cos(math.radians(210)), C1[1] + R1 * math.sin(math.radians(210)))
E2 = (C2[0] + R2 * math.cos(math.radians(60)), C2[1] + R2 * math.sin(math.radians(60)))
guide(p, [C1, E1], THEORY, 0.6)
guide(p, [C2, E2], THEORY, 0.6)
p.label((C1[0] + E1[0]) / 2, (C1[1] + E1[1]) / 2, "r" + subs("1"), -4, 14, THEORY, 10.5, "middle", False, True)
p.label((C2[0] + E2[0]) / 2, (C2[1] + E2[1]) / 2, "r" + subs("2"), 12, 3, THEORY, 10.5, "middle", False, True)
p.label(-1.90, 1.15, "B" + subs("1"), 0, 0, THEORY, 12, "middle", True, True)
p.label(2.05, -1.20, "B" + subs("2"), 0, 0, THEORY, 12, "middle", True, True)
p.label(C1[0], C1[1], "c" + subs("1"), -2, 16, TEXT, 11, "middle", False, True)
p.label(C2[0], C2[1], "c" + subs("2"), 8, 15, TEXT, 11, "middle", False, True)
p.label(X[0], X[1], "x", -9, -9, PRACTICE, 12, "middle", True, True)
p.label(0.40, 0.14, "s" + subs("1"), 0, 0, PRACTICE, 10.5, "middle", False, True)
p.label(-0.20, -0.10, "s" + subs("2"), 0, 4, PRACTICE, 10.5, "middle", False, True)
p.label(0.12, -0.72, "B" + subs("3") + " = B(x, s)", 0, 0, PRACTICE, 11, "middle", True, True)
p.text_px(p.x0 + 6, p.y0 + PH - 8, "s = min{s" + subs("1") + ", s" + subs("2") + "}", TEXT, 10.5, "start", False, True)

OUT["baz-daireler"] = figure(
    400, 255, [p],
    "Düzlemde açık daireler bazı için (B2) koşulu. <em>x</em> noktası <em>B</em><sub>1</sub> &#8745; <em>B</em><sub>2</sub> "
    "kesişimindedir; <em>x</em>'in birinci dairenin sınırına uzaklığı <em>s</em><sub>1</sub> = <em>r</em><sub>1</sub> &#8722; "
    "<em>d</em>(<em>x</em>, <em>c</em><sub>1</sub>), ikincisine uzaklığı <em>s</em><sub>2</sub> = <em>r</em><sub>2</sub> &#8722; "
    "<em>d</em>(<em>x</em>, <em>c</em><sub>2</sub>)'dir. Bu ikisinin küçüğünü yarıçap alan <em>B</em><sub>3</sub> = "
    "<em>B</em>(<em>x</em>, <em>s</em>) dairesi <em>x</em>'i içerir ve kesişimin tamamen içinde kalır.",
    aria="Kesisen iki acik daire, kesisimde x noktasi ve x merkezli, kesisime sigan kucuk ucuncu daire")

# ============================================================ carpim-dikdortgen-kesisim
# Two open rectangles U1 x V1 and U2 x V2 in the plane X x Y; their intersection is
# again a rectangle, (U1 n U2) x (V1 n V2).  The factor intervals sit on the axes.
p = Plot(86, 20, 292, 186, (0, 9.8), (0, 6.6))
p.axes((), (), "X", "Y")

U1, V1 = (0.8, 6.9), (0.6, 4.7)      # THEORY rectangle
U2, V2 = (3.0, 9.4), (2.2, 6.3)      # PRACTICE rectangle
UI = (max(U1[0], U2[0]), min(U1[1], U2[1]))
VI = (max(V1[0], V2[0]), min(V1[1], V2[1]))
DASH = "5 3"
CAP = "&#8745;"


def box(u, v):
    return [(u[0], v[0]), (u[1], v[0]), (u[1], v[1]), (u[0], v[1])]


# faint projections of the rectangle sides onto the axes
for u, v, col in ((U1, V1, THEORY), (U2, V2, PRACTICE)):
    for x in u:
        guide(p, [(x, 0), (x, v[0])], col, 0.4)
    for y in v:
        guide(p, [(0, y), (u[0], y)], col, 0.4)

# the two open rectangles (dashed boundary = boundary not included)
p.polygon(box(U1, V1), THEORY, 0.14, THEORY, 1.5, DASH)
p.polygon(box(U2, V2), PRACTICE, 0.14, PRACTICE, 1.5, DASH)
# their intersection, itself an open rectangle
p.polygon(box(UI, VI), BASE, 0.42)
p.label(U1[0], V1[1], "U" + subs("1") + " " + TIMES_S + " V" + subs("1"), 6, 15, THEORY, 11.5, "start", True, True)
p.label(U2[1], V2[1], "U" + subs("2") + " " + TIMES_S + " V" + subs("2"), -6, 15, PRACTICE, 11.5, "end", True, True)
p.label((UI[0] + UI[1]) / 2, (VI[0] + VI[1]) / 2,
        "(U" + subs("1") + CAP + "U" + subs("2") + ")" + TIMES_S + "(V" + subs("1") + CAP + "V" + subs("2") + ")",
        0, 4, BASE, 10, "middle", True, False)

# factor intervals on the axes: two rows below the x-axis, two columns left of the y-axis
def x_interval(u, py, col, name, at):
    p.add('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="2.4" stroke-linecap="round"/>'
          % (p.X(u[0]) + 4, py, p.X(u[1]) - 4, py, col))
    for x in u:
        p.add('<circle cx="%.1f" cy="%.1f" r="3" fill="%s" stroke="%s" stroke-width="1.4"/>' % (p.X(x), py, BG, col))
    p.text_px(p.X(at), py + 15, name, col, 11, "middle", True, True)


def y_interval(v, px, col, name, at):
    p.add('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="2.4" stroke-linecap="round"/>'
          % (px, p.Y(v[0]) - 4, px, p.Y(v[1]) + 4, col))
    for y in v:
        p.add('<circle cx="%.1f" cy="%.1f" r="3" fill="%s" stroke="%s" stroke-width="1.4"/>' % (px, p.Y(y), BG, col))
    p.text_px(px - 8, p.Y(at) + 4, name, col, 11, "end", True, True)


AX_Y = p.y0 + p.h
x_interval(U1, AX_Y + 9, THEORY, "U" + subs("1"), 1.9)
x_interval(U2, AX_Y + 18, PRACTICE, "U" + subs("2"), 8.3)
x_interval(UI, AX_Y + 27, BASE, "U" + subs("1") + CAP + "U" + subs("2"), (UI[0] + UI[1]) / 2)
y_interval(V1, p.x0 - 9, THEORY, "V" + subs("1"), 1.4)
y_interval(V2, p.x0 - 18, PRACTICE, "V" + subs("2"), 5.6)
y_interval(VI, p.x0 - 27, BASE, "V" + subs("1") + CAP + "V" + subs("2"), (VI[0] + VI[1]) / 2)

OUT["carpim-dikdortgen-kesisim"] = figure(
    420, 268, [p],
    "İki açık dikdörtgenin kesişimi yine bir açık dikdörtgendir. <em>U</em><sub>1</sub> &#215; <em>V</em><sub>1</sub> "
    "ve <em>U</em><sub>2</sub> &#215; <em>V</em><sub>2</sub> dikdörtgenlerinin ortak bölgesi, yatay eksendeki "
    "<em>U</em><sub>1</sub> &#8745; <em>U</em><sub>2</sub> ile dikey eksendeki <em>V</em><sub>1</sub> &#8745; <em>V</em><sub>2</sub> "
    "aralıklarının çarpımıdır. Bir nokta iki dikdörtgende de bulunuyorsa birinci bileşeni iki <em>U</em>'da, ikinci "
    "bileşeni iki <em>V</em>'de birden yer alır; baz koşulu (B2) tam olarak bu gözleme dayanır.",
    aria="Duzlemde ust uste binen iki acik dikdortgen; kesisim bolgesi taranmis ve eksenlerde U1, U2, V1, V2 "
         "araliklari ile kesisimleri isaretli")

# ============================================================ gerektirme-kume-semasi
# p => q as set inclusion: the integers divisible by 6 (p) sit inside the integers
# divisible by 3 (q).  Pixel drawing, no axes.
W_F, H_F = 400, 255
p = Plot(0, 0, W_F, H_F, (0, W_F), (H_F, 0))     # identity map: data = pixels

ITAL_P = '<tspan font-style="italic">p</tspan>'
ITAL_Q = '<tspan font-style="italic">q</tspan>'

# ---- the universe: the integers -----------------------------------------------
RX0, RX1, RY0, RY1 = 20, 380, 4, 186
rect(p, RX0, RX1, RY0, RY1, TEXT, 0.0, TEXT, 1.2)
p.text_px(RX1 - 6, RY0 + 15, "tam sayılar", TEXT, 10.5, "end", False, True)

# ---- the two nested regions (q outside, p inside) ------------------------------
QX, QY, QR = 200, 95, 84
PX, PY, PR = 200, 118, 49
disk_fill(p, QX, QY, QR, THEORY, 0.11)
p.circle(QX, QY, QR, THEORY, 1.6)
disk_fill(p, PX, PY, PR, THEORY, 0.18)
p.circle(PX, PY, PR, THEORY, 1.6)

# region labels
p.text_px(QX, 33, "3'e bölünenler", THEORY, 11, "middle", True)
p.text_px(QX, 47, "(" + ITAL_Q + " doğru)", TEXT, 10, "middle")
p.text_px(PX, 108, "6'ya bölünenler", THEORY, 10.5, "middle", True)
p.text_px(PX, 122, "(" + ITAL_P + " doğru)", TEXT, 10, "middle")

# sample integers: inside p, in the ring q \ p, and outside q
for x, s in ((176, "6"), (200, "12"), (224, "18")):
    p.text_px(x, 146, s, TEXT, 11.5, "middle", True)
p.text_px(134, 129, "3", TEXT, 11.5, "middle", True)
p.text_px(266, 129, "15", TEXT, 11.5, "middle", True)
p.text_px(200, 64, "9", PRACTICE, 12, "middle", True)      # the counter-example to q => p
p.text_px(70, 52, "4", TEXT, 11.5, "middle", True)
p.text_px(330, 152, "7", TEXT, 11.5, "middle", True)

# ---- the note under the diagram ------------------------------------------------
p.text_px(W_F / 2, 211,
          ITAL_P + " " + ARROW + " " + ITAL_Q + " doğru: " + ITAL_P + " bölgesi " + ITAL_Q + " bölgesinin içinde.",
          TEXT, 11, "middle")
p.text_px(W_F / 2, 231,
          ITAL_Q + " " + ARROW + " " + ITAL_P + " yanlış: " +
          '<tspan fill="%s" font-weight="600">9</tspan>' % PRACTICE +
          " sayısı " + ITAL_Q + " bölgesinde ama " + ITAL_P + " bölgesinde değil.",
          TEXT, 11, "middle")

OUT["gerektirme-kume-semasi"] = figure(
    W_F, H_F, [p],
    "Gerektirmenin küme diliyle görünüşü. Dıştaki bölge <em>q</em>'nun doğru olduğu tam sayıları "
    "(3'e bölünenler), içteki bölge <em>p</em>'nin doğru olduğu tam sayıları (6'ya bölünenler) toplar. "
    "<em>p</em> &#8658; <em>q</em> doğrudur, çünkü <em>p</em> bölgesi <em>q</em> bölgesinin içinde kalır; "
    "6'ya bölünen her sayı 3'e de bölünür. Karşıt yön <em>q</em> &#8658; <em>p</em> ise yanlıştır: "
    "9 sayısı 3'e bölünür ama 6'ya bölünmez, yani <em>q</em> bölgesinde olup <em>p</em> bölgesinin dışındadır.",
    aria="Tam sayilari gosteren dikdortgen icinde ic ice iki daire: distaki 3'e bolunenler, icteki 6'ya bolunenler; "
         "9 sayisi iki daire arasindaki halkada, 4 ve 7 dairelerin disinda")

# ============================================================ ic-ice-araliklar
# Two indexed families on the number line: A_n = [-n, n] growing (union R, intersection [-1, 1])
# and B_n = (-1/n, 1/n) shrinking (union (-1, 1), intersection {0}).  Data y is measured in
# pixels from the bottom of each panel, so the rows sit at fixed heights.
PH = 150
Y_LINE = 20                       # the number line
ROWS = [(1, 122), (2, 88), (3, 54)]   # (n, data y): n grows downward toward the line
REAL = "&#8477;"


def number_line(p, xa, xb, ticks, tick_fmt):
    p.arrow((xa, Y_LINE), (xb, Y_LINE), TEXT, 1.1, 6.5, opacity=0.65)
    p.arrow((xb, Y_LINE), (xa, Y_LINE), TEXT, 1.1, 6.5, opacity=0.65)
    for t in ticks:
        p.line([(t, Y_LINE - 3.5), (t, Y_LINE + 3.5)], TEXT, 1.0, None, 0.8)
        p.label(t, Y_LINE, tick_fmt(t), 0, 16, TEXT, 10, "middle")


def row_label(p, y, s):
    p.text_px(p.X(0), p.Y(y) - 8, s, TEXT, 10.5, "middle", False, True)


def summary(p, union, inter):
    py = p.y0 + p.h + 34
    p.text_px(p.x0 + 2, py, "birleşim = " + union, BASE, 11, "start", True)
    p.text_px(p.x0 + p.w - 2, py, "kesişim = " + inter, PRACTICE, 11, "end", True)


# ---- (a) A_n = [-n, n]: the rows widen, every row covers [-1, 1] -------------------------
pa = Plot(22, 34, 250, PH, (-3.75, 3.75), (0, PH))
panel_title(pa, "(a)  A" + subs("n") + " = [" + MINUS_S + "n, n]")
# the intersection: the band that every row still covers
rect(pa, -1, 1, Y_LINE, 142, PRACTICE, 0.12)
number_line(pa, -3.65, 3.65, range(-3, 4), lambda t: (MINUS_S + str(-t)) if t < 0 else str(t))
# the union: the whole line
pa.line([(-3.55, Y_LINE), (3.55, Y_LINE)], BASE, 3.2, None, 0.75)
for n, y in ROWS:
    pa.line([(-n, y), (n, y)], THEORY, 2.4)
    dot(pa, (-n, y), THEORY, 3.2)
    dot(pa, (n, y), THEORY, 3.2)
    row_label(pa, y, "A" + subs(str(n)) + " = [" + MINUS_S + str(n) + ", " + str(n) + "]")
summary(pa, REAL, "[" + MINUS_S + "1, 1]")

# ---- (b) B_n = (-1/n, 1/n): the rows shrink, only 0 survives ----------------------------
pb = Plot(300, 34, 250, PH, (-1.3, 1.3), (0, PH))
panel_title(pb, "(b)  B" + subs("n") + " = (" + MINUS_S + "1/n, 1/n)")
# the intersection: the single point 0, common to every row
# drawn in pieces so the dashes pass behind the row labels
for ya, yb in ((Y_LINE, 57), (73, 91), (107, 125)):
    guide(pb, [(0, ya), (0, yb)], PRACTICE, 0.6)
number_line(pb, -1.27, 1.27, (-1, 1), lambda t: (MINUS_S + str(-t)) if t < 0 else str(t))
# the union: (-1, 1), the widest row, laid on the line
pb.line([(-1, Y_LINE), (1, Y_LINE)], BASE, 3.2, None, 0.75)
hollow(pb, (-1, Y_LINE), BASE, 3.2, 1.5)
hollow(pb, (1, Y_LINE), BASE, 3.2, 1.5)
FRAC = {1: "1", 2: "1/2", 3: "1/3"}
for n, y in ROWS:
    pb.line([(-1 / n, y), (1 / n, y)], THEORY, 2.4)
    hollow(pb, (-1 / n, y), THEORY, 3.2, 1.5)
    hollow(pb, (1 / n, y), THEORY, 3.2, 1.5)
    row_label(pb, y, "B" + subs(str(n)) + " = (" + MINUS_S + FRAC[n] + ", " + FRAC[n] + ")")
dot(pb, (0, Y_LINE), PRACTICE, 4.0)
pb.label(0, Y_LINE, "0", 0, 16, PRACTICE, 10.5, "middle", True)
summary(pb, "(" + MINUS_S + "1, 1)", "{0}")

OUT["ic-ice-araliklar"] = figure(
    560, 226, [pa, pb],
    "İki iç içe aralık ailesi. Solda <em>A<sub>n</sub></em> = [&#8722;<em>n</em>, <em>n</em>] aralıkları "
    "<em>n</em> büyüdükçe genişler: her gerçel sayı yeterince büyük bir <em>n</em> için bir "
    "<em>A<sub>n</sub></em>'ye düşer, bu yüzden birleşim &#8477;'dir; her aralığın ortak parçası ise "
    "en dar olan <em>A</em><sub>1</sub> = [&#8722;1, 1]'dir. Sağda "
    "<em>B<sub>n</sub></em> = (&#8722;1/<em>n</em>, 1/<em>n</em>) aralıkları daralır: birleşim en geniş "
    "olan (&#8722;1, 1), kesişim ise yalnızca 0 noktasıdır; sıfırdan farklı her sayı yeterince büyük "
    "<em>n</em> için dışarıda kalır.",
    css_class=WIDE,
    aria="Iki sayi dogrusu: solda genisleyen kapali araliklar A1, A2, A3 ve birlesim R, kesisim [-1,1]; "
         "sagda daralan acik araliklar B1, B2, B3 ve birlesim (-1,1), kesisim tek nokta 0")

# ============================================================ ic-ice-goruntu
# f(x) = 3x^2 + 2 : the image of A0 = [0, 1] is [2, 5]; the preimage of [2, 5] is the
# larger set [-1, 1].  Two vertical number lines (A on the left, B on the right), pixel drawing.
W_F, H_F = 400, 255
p = Plot(0, 0, W_F, H_F, (0, W_F), (H_F, 0))     # identity map: data = pixels
LX, RX = 155, 285                                  # the two number lines
REALS = "&#8477;"


def LY(v):
    """Value on A (left line) -> pixel y; scale 54 px per unit."""
    return 138 - 54 * v


def RY(v):
    """Value on B (right line) -> pixel y; scale 30 px per unit."""
    return 216 - (v - 0.6) * 30


# ---- the mapping band A0 -> f(A0) ---------------------------------------------
p.polygon([(LX, LY(1)), (RX, RY(5)), (RX, RY(2)), (LX, LY(0))], THEORY, 0.11)
# two points of A0's mirror image share one value: f(-1/2) = f(1/2)
for x in (-0.5, 0.5):
    p.line([(LX, LY(x)), (RX, RY(2.75))], PRACTICE, 1.1, "4 3", 0.85)
    dot(p, (LX, LY(x)), PRACTICE, 3.0)
dot(p, (RX, RY(2.75)), PRACTICE, 3.0)

# ---- the number lines -------------------------------------------------------------
for x in (LX, RX):
    p.line([(x, 232), (x, 60)], TEXT, 1.2, None, 0.6)
    p.arrow((x, 70), (x, 52), TEXT, 1.2, 7.0, None, 0.6)
p.text_px(LX, 44, "A = " + REALS, TEXT, 11.5, "middle", True, False)
p.text_px(RX, 44, "B = " + REALS, TEXT, 11.5, "middle", True, False)
p.arrow((LX + 34, 38), (RX - 34, 38), TEXT, 1.4, 8.0)
p.text_px((LX + RX) / 2, 31, "f", TEXT, 12, "middle", True, True)

# ---- the marked intervals ---------------------------------------------------------
# preimage f^-1(f(A0)) = [-1, 1]: wide, light
p.line([(LX, LY(-1)), (LX, LY(1))], PRACTICE, 10, None, 0.35)
# A0 = [0, 1] and its image [2, 5]: dark
p.line([(LX, LY(0)), (LX, LY(1))], THEORY, 4.5)
p.line([(RX, RY(2)), (RX, RY(5))], THEORY, 4.5)
for x, y in ((LX, LY(0)), (LX, LY(1)), (RX, RY(2)), (RX, RY(5))):
    dot(p, (x, y), THEORY, 3.4)
for y in (LY(-1), LY(1)):
    dot(p, (LX, y), PRACTICE, 3.4)
dot(p, (LX, LY(1)), THEORY, 3.4)      # 1 belongs to A0 too; keep it dark on top

# ---- tick labels ----------------------------------------------------------------
for v, s in ((1, "1"), (0.5, "1/2"), (0, "0"), (-0.5, MINUS_S + "1/2"), (-1, MINUS_S + "1")):
    p.text_px(LX - 8, LY(v) + 4, s, TEXT, 10, "end")
for v, s in ((2, "2"), (5, "5")):
    p.text_px(RX + 8, RY(v) + 4, s, TEXT, 10, "start")

# ---- set labels -------------------------------------------------------------------
p.text_px(LX - 34, LY(0.5) + 4, "A" + subs("0") + " = [0, 1]", THEORY, 11, "end", True, True)
p.text_px(LX - 34, LY(-1.45) + 4,
          "f" + sups(MINUS_S + "1") + "(f(A" + subs("0") + ")) = [" + MINUS_S + "1, 1]",
          PRACTICE, 11, "end", True, True)
p.line([(LX - 30, LY(-1.45)), (LX - 12, LY(-1.05))], PRACTICE, 0.9, None, 0.7)
p.text_px(RX + 22, RY(3.5) + 4, "f(A" + subs("0") + ") = [2, 5]", THEORY, 11, "start", True, True)
p.text_px(RX + 8, RY(2.75) + 4, "f(" + MINUS_S + "1/2) = f(1/2)", PRACTICE, 9.5, "start", False, True)

OUT["ic-ice-goruntu"] = figure(
    W_F, H_F, [p],
    "<em>f</em>(<em>x</em>) = 3<em>x</em><sup>2</sup> + 2 için görüntü ile ters görüntünün art arda "
    "uygulanması. <em>A</em><sub>0</sub> = [0, 1] kümesinin görüntüsü <em>f</em>(<em>A</em><sub>0</sub>) = [2, 5]'tir; "
    "bu aralığın ters görüntüsü ise [&#8722;1, 1], yani <em>A</em><sub>0</sub>'dan daha büyük bir kümedir. "
    "Sebep <em>f</em>'nin birebir olmamasıdır: &#8722;1/2 &#8713; <em>A</em><sub>0</sub> olduğu hâlde "
    "<em>f</em>(&#8722;1/2) = <em>f</em>(1/2) &#8712; <em>f</em>(<em>A</em><sub>0</sub>) olduğundan &#8722;1/2 ters "
    "görüntüye girer. Genel olarak yalnızca <em>A</em><sub>0</sub> &#8838; "
    "<em>f</em><sup>&#8722;1</sup>(<em>f</em>(<em>A</em><sub>0</sub>)) kapsaması geçerlidir.",
    aria="Iki dikey sayi dogrusu: solda A uzerinde [0,1] koyu ve [-1,1] acik isaretli, sagda B uzerinde "
         "goruntu [2,5] koyu isaretli; -1/2 ve 1/2 noktalari ayni degere gidiyor")

# ============================================================ sira-araliklar-sayi-dogrusu
# The four intervals with end points 1 and 3 on the real line, one per row:
# (1,3), [1,3), (1,3], [1,3].  Data y is measured in pixels from the panel bottom.
p = Plot(134, 18, 244, 166, (0.4, 4.25), (0, 166))
Y_LINE = 12                                        # the number line
ROWS = [("(1, 3)", False, False, 146, "açık"),
        ("[1, 3)", True, False, 110, "yarı açık"),
        ("(1, 3]", False, True, 74, "yarı açık"),
        ("[1, 3]", True, True, 36, "kapalı")]      # (name, left closed, right closed, data y, kind)

# faint guides at the two end points, so every row lines up with 1 and 3 on the line
for x in (1, 3):
    guide(p, [(x, Y_LINE), (x, 158)], TEXT, 0.3)

# the number line with ticks 1, 2, 3
p.arrow((0.45, Y_LINE), (4.2, Y_LINE), TEXT, 1.2, 7.0, opacity=0.7)
p.label(4.18, Y_LINE, "&#8477;", 0, -8, TEXT, 11.5, "end", True, False)
for x in (1, 2, 3):
    p.line([(x, Y_LINE - 4), (x, Y_LINE + 4)], TEXT, 1.2)
    p.label(x, Y_LINE, str(x), 0, 18, TEXT, 11, "middle", False, False)

# one interval per row: a solid dot for an included end point, a hollow one for an excluded one
for name, lc, rc, y, kind in ROWS:
    p.line([(1, y), (3, y)], THEORY, 2.6)
    for x, closed in ((1, lc), (3, rc)):
        if closed:
            dot(p, (x, y), THEORY, 4.2)
        else:
            hollow(p, (x, y), THEORY, 4.2, 1.6)
    p.text_px(122, p.Y(y) + 4, name, TEXT, 12, "end", True, False)
    p.label(3, y, kind, 16, 4, TEXT, 10, "start", False, True)

OUT["sira-araliklar-sayi-dogrusu"] = figure(
    400, 220, [p],
    "Gerçel sayılarda uç noktaları 1 ve 3 olan dört aralık. Dolu nokta uç noktanın kümeye dahil "
    "olduğunu, içi boş nokta dahil olmadığını gösterir: (1, 3) iki ucu da almaz, [1, 3) yalnızca 1'i, "
    "(1, 3] yalnızca 3'ü, [1, 3] ise ikisini de alır. Uçlar dışında dört küme aynıdır; fark yalnızca "
    "köşeli ve yuvarlak parantezin gösterdiği iki noktadadır.",
    aria="Sayi dogrusu uzerinde 1 ve 3 uclu dort aralik alt alta: acik, iki yari acik ve kapali; "
         "dahil uclar dolu, haric uclar ici bos nokta")

# ============================================================ sonlu-tumleyen-sayi-dogrusu
# Two number lines under the finite-complement topology on R:
#   top    A = R \ {1, 2, ..., n}  — thick line with the n points punched out (open, not closed)
#   bottom N = {0, 1, 2, ...}       — isolated dots on a thin line (neither open nor closed)
# Data x is the real line; data y is measured in pixels from the top (identity map).
W_F, H_F = 400, 232
p = Plot(30, 0, 342, H_F, (-2.6, 7.4), (H_F, 0))
REALS, NATS, ELLIP = "&#8477;", "&#8469;", "&#8230;"
XL, XR = -2.45, 7.3          # visible extent of each line
Y_TOP, Y_BOT = 60, 170       # the two lines (pixel rows)


def number_line(y, width, opacity):
    """Left tail, right arrow and the R label for a line at pixel row y."""
    p.line([(XL, y), (XR - 0.25, y)], TEXT, width, None, opacity)
    p.arrow((XR - 0.3, y), (XR, y), TEXT, width, 7.0, opacity=opacity)
    p.label(XR, y, REALS, 2, -8, TEXT, 11, "end", True, False)


def tick_label(x, y, s, color=TEXT, bold=False):
    p.label(x, y, s, 0, 18, color, 10.5, "middle", bold, True)


# ---- top line: A = R \ {1, 2, ..., n} ---------------------------------------
p.text_px(30, 22, "A = " + REALS + " \\ {1, 2, " + ELLIP + ", n}", THEORY, 12, "start", True)
p.text_px(372, 22, "açık, kapalı değil", BASE, 10.5, "end", True)
# the whole line belongs to A (thick, coloured) except the punched-out points
p.line([(XL, Y_TOP), (XR - 0.25, Y_TOP)], THEORY, 3.0)
p.arrow((XR - 0.3, Y_TOP), (XR, Y_TOP), THEORY, 3.0, 8.0)
p.label(XR, Y_TOP, REALS, 2, -9, TEXT, 11, "end", True, False)
# a faint tick at 0 for orientation
p.line([(0, Y_TOP - 4), (0, Y_TOP + 4)], TEXT, 1.0, None, 0.5)
tick_label(0, Y_TOP, "0")
for x, s in ((1, "1"), (2, "2"), (3, "3"), (5, "n")):
    hollow(p, (x, Y_TOP), THEORY, 3.6, 1.6)
    tick_label(x, Y_TOP, s, THEORY, True)
p.label(4, Y_TOP, ELLIP, 0, 4, THEORY, 12, "middle", True)
p.text_px(30, 101,
          "tümleyen " + REALS + " \\ A = {1, 2, " + ELLIP + ", n} sonlu  " + ARROW + "  A açık",
          TEXT, 10.5, "start")
p.text_px(30, 117,
          "A sonsuz ve A " + NEQ_S + " " + REALS + "  " + ARROW + "  A kapalı değil",
          TEXT, 10.5, "start")

# ---- bottom line: N = {0, 1, 2, ...} ------------------------------------------
p.text_px(30, 146, NATS + " = {0, 1, 2, 3, " + ELLIP + "}", THEORY, 12, "start", True)
p.text_px(372, 146, "ne açık ne kapalı", PRACTICE, 10.5, "end", True)
number_line(Y_BOT, 1.1, 0.55)
for k in range(7):
    dot(p, (k, Y_BOT), THEORY, 3.6)
    tick_label(k, Y_BOT, str(k), THEORY, True)
p.label(6.6, Y_BOT, ELLIP, 0, 4, THEORY, 12, "middle", True)
p.text_px(30, 211,
          "tümleyen " + REALS + " \\ " + NATS + " sonsuz  " + ARROW + "  " + NATS + " açık değil;   "
          + NATS + " sonsuz ve " + NATS + " " + NEQ_S + " " + REALS + "  " + ARROW + "  kapalı değil",
          TEXT, 10.5, "start")

OUT["sonlu-tumleyen-sayi-dogrusu"] = figure(
    W_F, H_F, [p],
    "&#8477; üzerinde sonlu tümleyen topolojisinde iki küme. Üstte <em>A</em> = &#8477; &#8726; {1, 2, &#8230;, "
    "<em>n</em>}: doğrunun tamamı alınmış, yalnızca <em>n</em> tane nokta çıkarılmıştır; tümleyeni sonlu olduğundan "
    "<em>A</em> açıktır, ama sonsuz ve &#8477;'den farklı olduğundan kapalı değildir. Altta &#8469;: sayılabilir "
    "sonsuz nokta işaretlidir; tümleyeni sonsuz olduğundan açık değil, kendisi sonsuz ve &#8477;'den farklı "
    "olduğundan kapalı da değildir. Bu topolojide açıklık, dışarıda kalan noktaların <em>sonlu</em> olmasına bağlıdır.",
    aria="Iki sayi dogrusu: ustte kalin cizgide 1, 2, 3 ve n noktalari ici bos halkalarla cikarilmis kume A; "
         "altta ince cizgide 0, 1, 2 gibi dogal sayilar dolu noktalarla isaretli kume N")

# ============================================================ topoloji-zinciri
# The chain {O, X} c tau_sonlu c tau_say c P(X) as four boxes joined by subset arrows;
# under each arrow the set that separates the two topologies when X = R.
# Pixel drawing, no axes.
W_F, H_F = 560, 206
p = Plot(0, 0, W_F, H_F, (0, W_F), (H_F, 0))     # identity map: data = pixels
REALS, NATS, TAU, EMPTY = "&#8477;", "&#8469;", "&#964;", "&#216;"

BW, BH, GAP = 100, 62, 44                         # box size and the gap between boxes
X_FIRST = (W_F - (4 * BW + 3 * GAP)) / 2
BY = 44                                           # top edge of the boxes
CY = BY + BH / 2                                  # vertical centre of the boxes

BOXES = [("en kaba", "", "{" + EMPTY + ", X}"),
         ("sonlu", "tümleyen", TAU + subs("sonlu")),
         ("sayılabilir", "tümleyen", TAU + subs("say")),
         ("ayrık", "", "<tspan font-style=\"italic\">P</tspan>(X)")]
SEPARATORS = [REALS + " \\ {0}", REALS + " \\ " + NATS, "{0}"]


def subset_sign(cx, cy, s=4.6, color=THEORY, width=1.3):
    """A hand-drawn 'subset or equal' sign: the render font lacks U+2286."""
    p.add('<path d="M%.1f,%.1f L%.1f,%.1f A%.1f,%.1f 0 0,0 %.1f,%.1f L%.1f,%.1f" '
          'fill="none" stroke="%s" stroke-width="%.1f" stroke-linecap="round"/>'
          % (cx + s, cy - s, cx, cy - s, s, s, cx, cy + s, cx + s, cy + s, color, width))
    p.add('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="%.1f" stroke-linecap="round"/>'
          % (cx - s, cy + s + 3.6, cx + s, cy + s + 3.6, color, width))


# ---- the four boxes ----------------------------------------------------------
box_x = []
for i, (name1, name2, sym) in enumerate(BOXES):
    x = X_FIRST + i * (BW + GAP)
    box_x.append(x)
    rect(p, x, x + BW, BY, BY + BH, THEORY, 0.10, THEORY, 1.3)
    cx = x + BW / 2
    if name2:
        p.text_px(cx, BY + 16, name1, TEXT, 10.5, "middle")
        p.text_px(cx, BY + 29, name2, TEXT, 10.5, "middle")
    else:
        p.text_px(cx, BY + 22, name1, TEXT, 10.5, "middle")
    p.text_px(cx, BY + BH - 12, sym, THEORY, 12.5, "middle", True)

# ---- subset arrows between the boxes, with the separating set below ------------
for i in range(3):
    xa, xb = box_x[i] + BW, box_x[i + 1]
    gx = (xa + xb) / 2
    p.arrow((xa + 4, CY), (xb - 4, CY), THEORY, 1.6, 7.5)
    subset_sign(gx, CY - 15)
    # the separating set: open in the right-hand topology, not in the left-hand one
    guide(p, [(gx, BY + BH + 4), (gx, BY + BH + 26)], PRACTICE, 0.6)
    p.text_px(gx, BY + BH + 40, SEPARATORS[i], PRACTICE, 11.5, "middle", True)
p.text_px(W_F / 2, BY + BH + 58,
          "X = " + REALS + " için ayırıcı kümeler: sağdaki topolojide açık, soldakinde açık değil",
          TEXT, 10.5, "middle", False, True)

# ---- finer / coarser direction arrows -------------------------------------------
x_left, x_right = box_x[0] + 6, box_x[3] + BW - 6
p.arrow((x_left, 26), (x_right, 26), TEXT, 1.2, 7.5, opacity=0.7)
p.text_px(W_F / 2, 18, "daha ince (daha çok açık küme)", TEXT, 10.5, "middle")
p.arrow((x_right, H_F - 22), (x_left, H_F - 22), TEXT, 1.2, 7.5, opacity=0.7)
p.text_px(W_F / 2, H_F - 8, "daha kaba (daha az açık küme)", TEXT, 10.5, "middle")

OUT["topoloji-zinciri"] = figure(
    W_F, H_F, [p],
    "Bir <em>X</em> kümesi üzerindeki dört topolojinin zinciri: {&#8709;, <em>X</em>} &#8838; "
    "&#964;<sub>sonlu</sub> &#8838; &#964;<sub>say</sub> &#8838; &#119979;(<em>X</em>). Soldan sağa gidildikçe "
    "açık küme sayısı artar, yani topoloji incelir. <em>X</em> = &#8477; için her ok üzerindeki küme, "
    "sağdaki topolojide açık olup soldakinde açık olmadığından dört topoloji birbirinden farklıdır: "
    "&#8477; &#8726; {0} sonlu tümleyende, &#8477; &#8726; &#8469; sayılabilir tümleyende, {0} ise yalnız "
    "ayrık topolojide açıktır.",
    css_class=WIDE,
    aria="Soldan saga dort kutu: en kaba topoloji, sonlu tumleyen, sayilabilir tumleyen, ayrik topoloji; "
         "kutular altkume oklariyla bagli, her okun altinda X = R icin ayirici kume; ustte daha ince, "
         "altta daha kaba yonunu gosteren oklar")

# ============================================================ uc-elemanli-topolojiler
# Two Hasse-like diagrams on X = {a, b, c}: tau_1 = {0, X, {a}} is a topology;
# tau_7 = {0, X, {a}, {b}} is not, because {a} u {b} = {a, b} is missing (T3 fails).
W_F, H_F = 560, 245
p = Plot(0, 0, W_F, H_F, (0, W_F), (H_F, 0))     # identity map: data = pixels
TAU, EMPTY = "&#964;", "&#216;"
BOX_H = 24


def box(cx, cy, w, s, color=THEORY, dash=None, h=BOX_H, size=11):
    """Rounded node box centred at (cx, cy) with its label."""
    da = ' stroke-dasharray="%s"' % dash if dash else ""
    p.add('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="4" fill="%s" fill-opacity="0.13" '
          'stroke="%s" stroke-width="1.3"%s/>' % (cx - w / 2, cy - h / 2, w, h, color, color, da))
    p.text_px(cx, cy + 4, s, TEXT, size, "middle", True, False)


def edge(x0, y0, x1, y1, color=TEXT, dash=None, opacity=0.75):
    """Inclusion arrow from the top of one box to the bottom of another."""
    p.arrow((x0, y0), (x1, y1), color, 1.4, 7.5, dash, opacity)


Y_TOP, Y_MID, Y_BOT = 62, 142, 222      # rows of the left diagram
TOP_W, ONE_W, EMPTY_W = 92, 40, 34

# ---- left: tau_1 is a topology --------------------------------------------------------
LC = 140
p.text_px(LC, 16, TAU + subs("1") + " topolojidir", THEORY, 12, "middle", True)
p.text_px(LC, 33, TAU + subs("1") + " = {" + EMPTY + ", X, {a}}", TEXT, 10.5, "middle", False, True)
box(LC, Y_TOP, TOP_W, "X = {a, b, c}")
box(LC, Y_MID, ONE_W, "{a}")
box(LC, Y_BOT, EMPTY_W, EMPTY)
edge(LC, Y_BOT - BOX_H / 2 - 2, LC, Y_MID + BOX_H / 2 + 2)
edge(LC, Y_MID - BOX_H / 2 - 2, LC, Y_TOP + BOX_H / 2 + 2)
# what the axioms ask for, and where it lands
p.text_px(LC + 30, (Y_MID + Y_BOT) / 2 + 4, EMPTY + " &#8745; {a} = " + EMPTY, TEXT, 9.5, "start", False, True)
p.text_px(LC + 30, (Y_TOP + Y_MID) / 2 + 4, "{a} &#8745; X = {a}", TEXT, 9.5, "start", False, True)
p.text_px(LC - 30, (Y_MID + Y_BOT) / 2 + 4, "birleşim: {a}", TEXT, 9.5, "end", False, True)
p.text_px(LC - 30, (Y_TOP + Y_MID) / 2 + 4, "birleşim: X", TEXT, 9.5, "end", False, True)

# ---- right: tau_7 is not a topology -------------------------------------------------
RC, XA, XB = 425, 345, 505           # centre, and the {a} / {b} columns
Y_MISS = 108                          # the missing union {a, b}
Y_ROW = 165                           # the {a}, {b} row
p.text_px(RC, 16, TAU + subs("7") + " topoloji değildir: (T3) bozulur", PRACTICE, 12, "middle", True)
p.text_px(RC, 33, TAU + subs("7") + " = {" + EMPTY + ", X, {a}, {b}}", TEXT, 10.5, "middle", False, True)
box(RC, Y_TOP, TOP_W, "X = {a, b, c}")
box(XA, Y_ROW, ONE_W, "{a}")
box(XB, Y_ROW, ONE_W, "{b}")
box(RC, Y_BOT, EMPTY_W, EMPTY)
# solid inclusions that do hold inside tau_7
edge(RC - 12, Y_BOT - BOX_H / 2 - 2, XA + 14, Y_ROW + BOX_H / 2 + 2)
edge(RC + 12, Y_BOT - BOX_H / 2 - 2, XB - 14, Y_ROW + BOX_H / 2 + 2)
edge(XA, Y_ROW - BOX_H / 2 - 2, RC - 36, Y_TOP + BOX_H / 2 + 2)
edge(XB, Y_ROW - BOX_H / 2 - 2, RC + 36, Y_TOP + BOX_H / 2 + 2)
# the union the family owes but does not contain
MISS_W, MISS_H = 74, 34
box(RC, Y_MISS, MISS_W, "", PRACTICE, "4 3", MISS_H)
p.text_px(RC, Y_MISS - 1, "{a, b}", TEXT, 11, "middle", True, False)
p.line([(RC - 21, Y_MISS - 3.5), (RC + 21, Y_MISS - 3.5)], PRACTICE, 1.7)
p.text_px(RC, Y_MISS + 12, TAU + subs("7", 8) + "'de yok", PRACTICE, 9.5, "middle", False, True)
edge(XA + 10, Y_ROW - BOX_H / 2 - 2, RC - MISS_W / 2 + 6, Y_MISS + MISS_H / 2 + 2, PRACTICE, "4 3", 0.95)
edge(XB - 10, Y_ROW - BOX_H / 2 - 2, RC + MISS_W / 2 - 6, Y_MISS + MISS_H / 2 + 2, PRACTICE, "4 3", 0.95)
p.text_px(RC, Y_ROW + 4, "{a} ile {b} birleşimi", PRACTICE, 9.5, "middle", False, True)

OUT["uc-elemanli-topolojiler"] = figure(
    W_F, H_F, [p],
    "<em>X</em> = {<em>a</em>, <em>b</em>, <em>c</em>} üzerinde iki aile. Solda &#964;<sub>1</sub> = {&#8709;, "
    "<em>X</em>, {<em>a</em>}}: üyelerin ikişer ikişer kesişimleri ve birleşimleri yine ailede kalır, bu yüzden "
    "&#964;<sub>1</sub> bir topolojidir. Sağda &#964;<sub>7</sub> = {&#8709;, <em>X</em>, {<em>a</em>}, {<em>b</em>}}: "
    "kesişimler sorunsuzdur, ama {<em>a</em>} &#8746; {<em>b</em>} = {<em>a</em>, <em>b</em>} ailede yoktur; "
    "(T3) bozulur ve &#964;<sub>7</sub> topoloji değildir. Aileyi topoloji olmaktan çıkarmaya tek bir eksik "
    "birleşim yeter.",
    css_class=WIDE,
    aria="Iki Hasse semasi: solda bos kume, {a} ve X kutulari kapsama oklariyla; sagda {a} ve {b} yan yana, "
         "ikisinden cikan kesikli oklar ustu cizili {a,b} kutusunda birlesiyor")

# ============================================================ venn-de-morgan
# De Morgan's laws for two sets: the complement of A u B (left) and of A n B (right)
# shaded inside the universe X.
R_V, D_V = 0.95, 1.1          # circle radius and centre distance (they overlap)
PW_V, PH_V, XR_V = 226.0, 150.0, 2.15
YR_V = XR_V * PH_V / PW_V      # equal px-per-unit on both axes: circles stay circles
BOX = [(-2.05, -1.32), (2.05, -1.32), (2.05, 1.32), (-2.05, 1.32)]
SHADE = 0.30


def _arc(cx, cy, a0, a1, n=48):
    return [(cx + R_V * math.cos(a0 + (a1 - a0) * k / n), cy + R_V * math.sin(a0 + (a1 - a0) * k / n))
            for k in range(n + 1)]


def lens(xa, xb, y):
    """A n B as a polygon (arc of A inside B, then arc of B inside A)."""
    th = math.acos((D_V / 2) / R_V)
    return _arc(xa, y, -th, th) + _arc(xb, y, math.pi - th, math.pi + th)


def cup(q, px, py):
    """The union sign drawn by hand (the raster font lacks U+222A); baseline at py."""
    q.add('<path d="M%.1f,%.1f V%.1f A3.1,3.1 0 0 0 %.1f,%.1f V%.1f" fill="none" stroke="%s" '
          'stroke-width="1.05" stroke-linecap="round"/>'
          % (px - 3.1, py - 7.4, py - 3.1, px + 3.1, py - 3.1, py - 7.4, TEXT))


SUP_C = sups("c")


def venn_panel(px, mode):
    q = Plot(px, 34, PW_V, PH_V, (-XR_V, XR_V), (-YR_V, YR_V))
    xa, xb, y = -D_V / 2, D_V / 2, 0.0
    # shade the whole universe, then cut the unshaded part out with the page colour
    q.polygon(BOX, THEORY, SHADE)
    if mode == "birlesim":
        q.polygon(_arc(xa, y, 0, 2 * math.pi), BG, 1.0)
        q.polygon(_arc(xb, y, 0, 2 * math.pi), BG, 1.0)
    else:
        q.polygon(lens(xa, xb, y), BG, 1.0)
    q.polygon(BOX, TEXT, 0.0, TEXT, 1.1)
    q.circle(xa, y, R_V, TEXT, 1.4)
    q.circle(xb, y, R_V, TEXT, 1.4)
    q.label(xa - 0.42, 0.5, "A", 0, 0, TEXT, 12, "middle", True, True)
    q.label(xb + 0.42, 0.5, "B", 0, 0, TEXT, 12, "middle", True, True)
    q.text_px(q.X(2.05) - 6, q.Y(1.32) + 15, "X", TEXT, 11.5, "end", False, True)
    # formula above the panel, split around the hand-drawn union sign
    cx, ty = q.x0 + q.w / 2, q.y0 - 12
    if mode == "birlesim":
        q.text_px(cx - 36, ty, "(A", TEXT, 12, "end", False, True)
        cup(q, cx - 29, ty)
        q.text_px(cx - 22, ty, "B)" + SUP_C + " = A" + SUP_C + " &#8745; B" + SUP_C, TEXT, 12, "start", False, True)
        note = "A veya B'de bulunmayan noktalar"
    else:
        q.text_px(cx + 22, ty, "(A &#8745; B)" + SUP_C + " = A" + SUP_C, TEXT, 12, "end", False, True)
        cup(q, cx + 29, ty)
        q.text_px(cx + 36, ty, "B" + SUP_C, TEXT, 12, "start", False, True)
        note = "A ile B'nin ortak kısmında bulunmayan noktalar"
    q.text_px(cx, q.y0 + q.h + 20, note, THEORY, 11, "middle", True)
    return q


panels = [venn_panel(30, "birlesim"), venn_panel(304, "kesisim")]
OUT["venn-de-morgan"] = figure(
    560, 220, panels,
    "İki küme için De Morgan kuralları. Dikdörtgen evrensel küme <em>X</em>'i, daireler <em>A</em> ve <em>B</em>'yi "
    "gösterir; taralı bölge tümleyendir. Solda (<em>A</em> &#8746; <em>B</em>)<sup>c</sup>: iki dairenin de dışında "
    "kalan noktalar, yani hem <em>A</em><sup>c</sup> hem <em>B</em><sup>c</sup>'de olanlar, <em>A</em><sup>c</sup> &#8745; "
    "<em>B</em><sup>c</sup>. Sağda (<em>A</em> &#8745; <em>B</em>)<sup>c</sup>: yalnızca mercek bölgesi taralı değildir; "
    "geriye <em>A</em>'nın ya da <em>B</em>'nin dışında olan noktalar, yani <em>A</em><sup>c</sup> &#8746; "
    "<em>B</em><sup>c</sup> kalır.",
    css_class=WIDE,
    aria="Iki Venn semasi: solda iki dairenin disinda kalan bolge, sagda iki dairenin ortak mercegi disindaki her yer taranmis")


# ---------------------------------------------------------------------------
for name, content in OUT.items():
    with io.open(os.path.join(OUT_DIR, "topology-%s.md" % name), "w", encoding="utf-8") as f:
        f.write(content)
print("generated:", ", ".join(OUT))
