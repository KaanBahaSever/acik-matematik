# -*- coding: utf-8 -*-
"""
Generates the SVG figures used in the "Diferansiyel Geometri" chapters
(dersler/diferansiyel-geometri).

Same authoring flow as scripts/analysis_figures.py: the figures are NOT produced
at build time. Run this script, then

    python scripts/center_figures.py "diffgeo-*.md"

(which measures each drawing and centers it in its viewBox) and paste the
resulting markup into the .qmd files — inside the theorem/example/proof box the
figure explains, never inside a definition box. Building the books therefore
needs neither Python nor Jupyter; CI runs Quarto alone.

Three-dimensional drawings (points, tangent vectors, vector fields, surfaces
of R^3) go through scripts/svg_plot3.py: an orthographic camera projects
space points onto an equal-aspect panel.

The captions are Turkish on purpose — they are the text shown on the site.

Usage:   python scripts/diffgeo_figures.py && python scripts/center_figures.py "diffgeo-*.md"
Output:  scripts/_figures/diffgeo-<name>.md
"""
import io
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from svg_plot import *  # noqa: E402,F403 — Plot, figure, colors, WIDE, hollow, dot, ...
from svg_plot3 import *  # noqa: E402,F403 — Camera, Space, space_panel, vector helpers

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_figures")
os.makedirs(OUT_DIR, exist_ok=True)
OUT = {}

EPS, DELTA, ELL, INF, LEQ_S = "&#949;", "&#948;", "&#8467;", "&#8734;", "&#8804;"
PRIME, GEQ_S, NEQ_S, TIMES_S, MINUS_S = "&#8242;", "&#8805;", "&#8800;", "&#215;", "&#8722;"
INT_S, SUM_S, ARROW, PARTIAL, CDOT = "&#8747;", "&#8721;", "&#8594;", "&#8706;", "&#183;"


def subs(s, size=9):
    """Subscript inside an SVG <text>: 'x' + subs('0')."""
    return f'<tspan font-size="{size}" dy="4">{s}</tspan><tspan dy="-4">&#8203;</tspan>'


def sups(s, size=8.5):
    """Superscript inside an SVG <text>."""
    return f'<tspan font-size="{size}" dy="-5">{s}</tspan><tspan dy="5">&#8203;</tspan>'


def bold(s):
    """Bold run inside an SVG <text> — points and vector parts are set in bold."""
    return f'<tspan font-weight="700">{s}</tspan>'


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

# ============================================================ acik-yari-uzay
# -*- coding: utf-8 -*-
# acik-yari-uzay: the open half-space O = {x > 0}. The plane x = 0 is drawn as a grey,
# dashed-edged rectangle with corners (0, -3, -2), (0, 3, -2), (0, 3, 3), (0, -3, 3); the side
# x > 0 is tinted blue (a slab 0 < x < XB of it, with a floor grid at z = -2). Around
# p = (1, 2, 1) the ball of radius 1 and around s = (2, -1, 2) the ball of radius 2 are drawn as
# gridded spheres; each is tangent to the plane at the foot of its center, (0, 2, 1) and
# (0, -1, 2), and lies entirely inside O.
import math

XB = 3.2                        # depth of the drawn slab of O along x
p, s = (1.0, 2.0, 1.0), (2.0, -1.0, 2.0)
cp, cs = (0.0, 2.0, 1.0), (0.0, -1.0, 2.0)          # feet of p and s on the plane x = 0
wall = [(0, -3, -2), (0, 3, -2), (0, 3, 3), (0, -3, 3)]

P = space_panel(20, 14, 360, (-3.35, 2.55), (-2.75, 2.75))
S = Space(P, Camera(azimuth=35, elevation=25, scale=0.7))


def sphere(C, r):
    def f(u, v):
        return (C[0] + r * math.cos(u) * math.cos(v),
                C[1] + r * math.sin(u) * math.cos(v),
                C[2] + r * math.sin(v))
    return f


def hull2d(pts):
    """Convex hull (monotone chain) of 2-D points, counter-clockwise."""
    pts = sorted(set(pts))

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lower, upper = [], []
    for q in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], q) <= 0:
            lower.pop()
        lower.append(q)
    for q in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], q) <= 0:
            upper.pop()
        upper.append(q)
    return lower[:-1] + upper[:-1]


# --- the piece of the negative x axis behind the plane (painted first, so the wall covers it)
S.line([(-1.2, 0, 0), (0, 0, 0)], TEXT, 1.1, None, 0.3)

# --- the plane x = 0: grey, translucent, dashed edge (the boundary is not part of O) ---------
S.polygon(wall, TEXT, 0.10)
S.line(wall + [wall[0]], TEXT, 1.0, "5 4", 0.55)

# --- the half-space O: silhouette of the slab 0 < x < XB, tinted blue, plus a floor grid ------
box = [(x, y, z) for x in (0.0, XB) for y in (-3.0, 3.0) for z in (-2.0, 3.0)]
P.polygon(hull2d([S.pt(q) for q in box]), THEORY, 0.12)
for x in (0, 1, 2, 3):
    S.line([(x, -3, -2), (x, 3, -2)], THEORY, 0.7, None, 0.12)
for y in range(-3, 4):
    S.line([(0, y, -2), (XB, y, -2)], THEORY, 0.7, None, 0.12)

# --- the two balls: s (radius 2) is farther from the viewer, so it is painted first ----------
S.surface(sphere(s, 2.0), (0.0, 2 * math.pi), (-math.pi / 2, math.pi / 2), nu=16, nv=8,
          fill=BASE, stroke=BASE, opacity=(0.05, 0.24), stroke_width=0.55, stroke_opacity=0.38)
S.surface(sphere(p, 1.0), (0.0, 2 * math.pi), (-math.pi / 2, math.pi / 2), nu=16, nv=8,
          fill=PRACTICE, stroke=PRACTICE, opacity=(0.05, 0.24), stroke_width=0.55, stroke_opacity=0.38)

# --- axes and ticks: painted after the spheres so the numbers are not dimmed by the fills.
# The y ticks -3, 3 and the z tick -2 are omitted: they would sit on the dashed edges of the
# plane; the x tick 3 would cross the plane's lower edge in projection.
S.axes(4.1, 3.8, 3.7, ymin=-3.4, zmin=-2.4)
S.ticks("x", (1, 2), offset=(-9, 11))
S.ticks("y", (-2, -1, 1, 2))
S.ticks("z", (1, 2, 3), offset=(19, -4))
S.ticks("z", (-1,), offset=(19, 4))

# --- radii to the plane: the distance from each center to x = 0 is its first coordinate -----
S.line([s, cs], BASE, 1.3, "4 3", 0.9)
S.line([p, cp], PRACTICE, 1.3, "4 3", 0.9)
S.hollow(cs, BASE, 2.8, 1.4)
S.hollow(cp, PRACTICE, 2.8, 1.4)
S.point(s, BASE, 4.0)
S.point(p, PRACTICE, 4.0)

# --- labels ---------------------------------------------------------------------------------
S.label(p, bold("p") + ", " + EPS + " = 1", 0, -50, PRACTICE, 12, "middle")
S.label(s, bold("s") + ", " + EPS + " = 2", 0, -94, BASE, 12, "middle")
S.label((2.3, -0.9, -2.0), '<tspan font-style="italic">O</tspan>: <tspan font-style="italic">x</tspan> &gt; 0',
        0, 4, THEORY, 12.5, "middle")
S.label((0, 3, 3), '<tspan font-style="italic">x</tspan> = 0', 6, -3, TEXT, 11, "start")

OUT["acik-yari-uzay"] = figure(
    400, 360, [P],
    "<em>O</em> = {<strong>p</strong> : <em>p</em><sub>1</sub> &gt; 0} yarı uzayı, "
    "<em>x</em> = 0 düzleminin (gri, kesikli kenarlı; kümeye ait değil) önünde kalan mavi bölgedir. "
    "<strong>p</strong> = (1, 2, 1) etrafındaki 1 yarıçaplı top ile <strong>s</strong> = (2, &#8722;1, 2) "
    "etrafındaki 2 yarıçaplı top, düzleme sırasıyla (0, 2, 1) ve (0, &#8722;1, 2) noktalarında teğet olup "
    "tamamen <em>O</em>&#8217;nun içinde kalır: <em>O</em>&#8217;nun bir noktasından düzleme olan uzaklık "
    "o noktanın birinci koordinatı <em>p</em><sub>1</sub>&#8217;dir ve &#949; = <em>p</em><sub>1</sub> "
    "seçilince top <em>O</em>&#8217;dan taşmaz. Düzleme yaklaştıkça toplar küçülür ama yarıçap hiç "
    "sıfırlanmaz; <em>O</em> bu yüzden açıktır.",
    aria="The open half-space O = {x > 0}: the grey plane x = 0 with dashed edges, the blue region "
         "in front of it, the ball of radius 1 about p = (1, 2, 1) and the ball of radius 2 about "
         "s = (2, -1, 2), each tangent to the plane and contained in O")

# ============================================================ birebir-orten-dort-grafik
# -*- coding: utf-8 -*-
# Four small panels side by side: the horizontal-line test on x^3, e^x, x^3 + x^2 and sin x.
# Blue graph, dashed orange test lines, filled marks where a test line meets the graph.


def ital(s):
    """Italic run inside an SVG <text> — variable and function names."""
    return f'<tspan font-style="italic">{s}</tspan>'


def mfmt(v):
    """Tick label with a Turkish decimal comma and a real minus sign."""
    return tfmt(v).replace("-", MINUS_S)


PI_TICKS = {-2 * PI: MINUS_S + "2&#960;", -PI: MINUS_S + "&#960;", PI: "&#960;", 2 * PI: "2&#960;"}


def bisect(f, a, b, n=60):
    """Root of f on [a, b] (f changes sign there) by bisection."""
    fa = f(a)
    for _ in range(n):
        m = 0.5 * (a + b)
        fm = f(m)
        if (fa < 0) == (fm < 0):
            a, fa = m, fm
        else:
            b = m
    return 0.5 * (a + b)


X, Y = ital("x"), ital("y")
# PITCH leaves 44 px between panels so a panel's x-axis name never sits on the same
# baseline as its neighbour's leftmost label with only a word's width between them
PANEL_W, PANEL_H, PITCH, TOP = 140, 168, 184, 30
LINE_DASH = "5 3"


def tick_text(p, px, py, s, anchor="middle"):
    """A tick label in the same style origin_axes uses (11 pt, 0.7 opacity)."""
    p.add(f'<text x="{px:.1f}" y="{py:.1f}" fill="{TEXT}" font-size="11" opacity="0.7" '
          f'text-anchor="{anchor}">{s}</text>')


def tick_mark(p, axis, t):
    """Tick mark only (no label) on the x or y axis through the origin."""
    if axis == "x":
        p.add(f'<line x1="{p.X(t):.1f}" y1="{p.Y(0)-3:.1f}" x2="{p.X(t):.1f}" y2="{p.Y(0)+3:.1f}" '
              f'stroke="{TEXT}" stroke-width="1" opacity="0.7"/>')
    else:
        p.add(f'<line x1="{p.X(0)-3:.1f}" y1="{p.Y(t):.1f}" x2="{p.X(0)+3:.1f}" y2="{p.Y(t):.1f}" '
              f'stroke="{TEXT}" stroke-width="1" opacity="0.7"/>')


def x_axis_name(p):
    """The italic x just past the arrow tip, below the axis (same style as the y name)."""
    p.add(f'<text x="{p.x0+p.w+8:.1f}" y="{p.Y(0)+15:.1f}" fill="{TEXT}" font-size="11.5" '
          f'font-style="italic" opacity="0.85">x</text>')


def title(p, tag, formula):
    p.text_px(p.x0 + p.w / 2, p.y0 - 12, bold(tag) + "  " + formula, TEXT, 11.5, "middle")


def test_line(p, y, x0, x1):
    p.line([(x0, y), (x1, y)], PRACTICE, 1.5, LINE_DASH)


def hit(p, x, y):
    """Filled mark where a test line meets the graph, ringed so it reads over both lines."""
    dot(p, (x, y), BG, 4.6)
    dot(p, (x, y), TEXT, 3.1)


def panel(k, xrange, yrange):
    return Plot(26 + k * PITCH, TOP, PANEL_W, PANEL_H, xrange, yrange)


# ---- (a) y = x^3 -------------------------------------------------------------
pa = panel(0, (-2.5, 2.5), (-2.8, 2.8))
pa.origin_axes("", "y", xticks=(-2, -1, 1, 2), yticks=(-2, -1, 1, 2), xfmt=mfmt, yfmt=mfmt)
x_axis_name(pa)
title(pa, "(a)", Y + " = " + X + sups("3"))
test_line(pa, 0.5, -2.45, 2.45)
clipped(pa, lambda x: x ** 3, -2.0, 2.0, THEORY, 1.9)
hit(pa, 0.5 ** (1 / 3), 0.5)
pa.label(-2.42, 0.5, Y + " = 0,5", 0, -5, PRACTICE, 11)

# ---- (b) y = e^x -------------------------------------------------------------
pb = panel(1, (-2.5, 2.5), (-1.7, 4.2))
pb.origin_axes("", "y", xticks=(-2, -1, 1, 2), yticks=(1, 2, 3), xfmt=mfmt, yfmt=mfmt)
x_axis_name(pb)
title(pb, "(b)", Y + " = " + ital("e") + sups(X))
test_line(pb, 0.5, -2.45, 2.45)
test_line(pb, -1.0, -2.45, 2.45)
clipped(pb, math.exp, -2.0, 2.0, THEORY, 1.9)
hit(pb, math.log(0.5), 0.5)
pb.label(-2.42, 0.5, Y + " = 0,5", 0, -5, PRACTICE, 11)
pb.label(-2.42, -1.0, Y + " = " + MINUS_S + "1", 0, 13, PRACTICE, 11)

# ---- (c) y = x^3 + x^2 -------------------------------------------------------
cubic = lambda x: x ** 3 + x ** 2  # noqa: E731
pc = panel(2, (-1.8, 1.3), (-0.6, 0.6))
pc.origin_axes("", "y", xticks=(1,), yticks=(-0.5, 0.5), xfmt=mfmt, yfmt=mfmt)
x_axis_name(pc)
# the graph drops steeply to the left of x = -1, so that tick's label sits just right of it
tick_mark(pc, "x", -1)
tick_text(pc, pc.X(-1) + 2, pc.Y(0) + 15, MINUS_S + "1", "start")
title(pc, "(c)", Y + " = " + X + sups("3") + " + " + X + sups("2"))
test_line(pc, 0.1, -1.78, 1.28)
clipped(pc, cubic, -2.0, 2.0, THEORY, 1.9)
for a, b in ((-1.0, -0.7), (-0.6, -0.2), (0.1, 0.5)):
    hit(pc, bisect(lambda x: cubic(x) - 0.1, a, b), 0.1)
pc.label(-1.76, 0.1, Y + " = 0,1", 0, -7, PRACTICE, 11)

# ---- (d) y = sin x -----------------------------------------------------------
# y range stops at -1.7: the graph never goes below -1, so a deeper panel is empty space
pd = panel(3, (-8.2, 8.2), (-1.7, 2.6))
pd.origin_axes("", "y", yticks=(1,), yfmt=mfmt)
x_axis_name(pd)
# the graph cuts the axis steeply at its zeros and the labels are wider than the gaps
# between them, so each label goes just above the axis on the side where the graph is
# below it (the negative side) — that pocket is free of both the graph and the test line
for t, s in PI_TICKS.items():
    tick_mark(pd, "x", t)
    if math.cos(t) < 0:      # graph descends through the zero: negative side is the right
        tick_text(pd, pd.X(t) + 3, pd.Y(0) - 4, s, "start")
    else:                    # graph ascends: negative side is the left
        tick_text(pd, pd.X(t) - 3, pd.Y(0) - 4, s, "end")
tick_mark(pd, "y", -1)
tick_text(pd, pd.X(0) + 7, pd.Y(-1) + 4, MINUS_S + "1", "start")
title(pd, "(d)", Y + " = sin " + X)
test_line(pd, 0.5, -8.1, 8.1)
test_line(pd, 2.0, -8.1, 8.1)
# the graph ends on its extrema at ±5π/2, so the last marks are not followed by a stub
curve(pd, math.sin, -2.5 * PI, 2.5 * PI, THEORY, 1.9, 300)
for k in (-1, 0, 1):
    for x in (PI / 6 + 2 * k * PI, 5 * PI / 6 + 2 * k * PI):
        if -2.5 * PI <= x <= 2.5 * PI:
            hit(pd, x, 0.5)
# the graph fills the whole strip, so these two labels sit just outside the panel
pd.text_px(pd.x0 + pd.w + 8, pd.Y(0.5) + 4, Y + " = 0,5", PRACTICE, 11)
pd.text_px(pd.x0 + pd.w + 8, pd.Y(2.0) + 4, Y + " = 2", PRACTICE, 11)

OUT["birebir-orten-dort-grafik"] = figure(
    788, 225, [pa, pb, pc, pd],
    "Yatay doğru testi: her yatay doğru grafiği en çok bir kez kesiyorsa fonksiyon birebir, "
    "en az bir kez kesiyorsa örtendir. "
    "(a) <em>x</em><sup>3</sup> kesin artandır ve her yüksekliğe ulaşır; <em>y</em> = 0,5 doğrusu "
    "grafiği tam bir kez keser: hem birebir hem örten. "
    "(b) <em>e</em><sup><em>x</em></sup> de kesin artandır ama hep pozitiftir; <em>y</em> = 0,5 tek "
    "noktada kesilirken <em>y</em> = &#8722;1 doğrusu grafiğe hiç değmez: birebir ama örten değil. "
    "(c) <em>x</em><sup>3</sup> + <em>x</em><sup>2</sup> her yüksekliğe ulaşır ama <em>y</em> = 0,1 "
    "doğrusunu üç noktada keser (örten, birebir değil); (d) sin <em>x</em> ise <em>y</em> = 0,5 "
    "doğrusunu sonsuz kez keser ve <em>y</em> = 2 doğrusuna hiç ulaşamaz (ne birebir ne örten).",
    css_class=WIDE,
    aria="Dort panel: x^3, e^x, x^3+x^2 ve sin x grafikleri, kesikli yatay test dogrulari ve kesisim noktalari",
)

# ============================================================ dform-donen-alan
# -*- coding: utf-8 -*-
# dform-donen-alan — the rotating field V = -y U1 + x U2 on the integer lattice -2..2 and its curl.
# Arrows are drawn at 0.4 of their true length (stated in the caption). Colour encodes the length
# |V(a, b)| = sqrt(a^2 + b^2): every arrow is drawn in THEORY and the longer classes are pushed from
# blue towards purple with an sRGB hue-rotate filter, so no colour code is written and both themes work.
# Dashed grey circles of radius 1 and 2 carry counter-clockwise rotation arrows; the out-of-page symbol
# at the origin stands for rot V = 2 U3, and the free top-left / bottom-right corners hold the formulas.
import math

SHRINK = 0.4
XR, YR = (-3.05, 3.05), (-3.05, 3.05)
p = cplane(24, 30, 352, XR, YR)
PPU = p.w / (XR[1] - XR[0])                  # pixels per data unit
MAX_HUE = 58.0                               # hue rotation of the longest arrows, in degrees
L_MIN, L_MAX = 1.0, math.sqrt(8.0)
FID = "dform-donen-alan-hue"                 # filter ids must be unique on the page


def ital(s):
    return '<tspan font-style="italic">' + s + '</tspan>'


def hue_for(n2):
    """Hue rotation for the arrows whose squared length is n2."""
    return MAX_HUE * (math.sqrt(n2) - L_MIN) / (L_MAX - L_MIN)


def tip(a, b):
    """End point of the shortened arrow V(a, b) = (-b, a) starting at (a, b)."""
    return (a - SHRINK * b, b + SHRINK * a)


def boxed_text(x, y, s, width, dx=0, dy=0, color=TEXT, size=11.5, anchor="middle", pad=2.0):
    """Label on an opaque page-background box, so an axis behind it does not show through."""
    px, py = p.X(x) + dx, p.Y(y) + dy
    bx = px - width if anchor == "end" else (px - width / 2 if anchor == "middle" else px)
    top, bottom = py - 0.75 * size - pad, py + 0.3 * size + pad
    p.add(f'<rect x="{bx - pad:.1f}" y="{top:.1f}" width="{width + 2 * pad:.1f}" '
          f'height="{bottom - top:.1f}" fill="{BG}" stroke="none"/>')
    p.add(f'<text x="{px:.1f}" y="{py:.1f}" fill="{color}" font-size="{size}" '
          f'text-anchor="{anchor}">{s}</text>')


def num_label(x, y, s, dx, dy, anchor):
    """Coordinate number next to a lattice point on an axis."""
    p.add(f'<text x="{p.X(x) + dx:.1f}" y="{p.Y(y) + dy:.1f}" fill="{TEXT}" font-size="10.5" '
          f'text-anchor="{anchor}" opacity="0.75">{s}</text>')


def rotation_arrow(r, a_mid, span_deg, color=TEXT, width=1.4, head=7.0, opacity=0.7):
    """Counter-clockwise arc of radius r centred on angle a_mid (degrees), arrowhead at its end.
    Arc and head share one <g opacity>; the arc stops at the base of the head."""
    a1 = math.radians(a_mid + span_deg / 2)
    a0 = math.radians(a_mid - span_deg / 2)
    back = head / (r * PPU)                               # angle covered by the head
    n = 24
    arc_pts = [(r * math.cos(a0 + (a1 - back * 0.8 - a0) * k / n),
                r * math.sin(a0 + (a1 - back * 0.8 - a0) * k / n)) for k in range(n + 1)]
    d = " ".join(("M" if i == 0 else "L") + p.P(x, y) for i, (x, y) in enumerate(arc_pts))
    x1, y1 = p.X(r * math.cos(a1)), p.Y(r * math.sin(a1))
    xb, yb = p.X(r * math.cos(a1 - back)), p.Y(r * math.sin(a1 - back))
    L = math.hypot(x1 - xb, y1 - yb)
    ux, uy = (x1 - xb) / L, (y1 - yb) / L
    px_, py_, hw = -uy, ux, head * 0.42
    p.add(f'<g opacity="{opacity}">'
          f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round"/>'
          f'<polygon points="{x1:.1f},{y1:.1f} {x1 - ux * head + px_ * hw:.1f},{y1 - uy * head + py_ * hw:.1f} '
          f'{x1 - ux * head - px_ * hw:.1f},{y1 - uy * head - py_ * hw:.1f}" fill="{color}"/></g>')


# --- filters: one hue rotation per length class (n2 = a^2 + b^2) -----------------------------------
CLASSES = (1, 2, 4, 5, 8)
defs = ['<defs>']
for n2 in CLASSES[1:]:
    defs.append(f'<filter id="{FID}-{n2}" color-interpolation-filters="sRGB">'
                f'<feColorMatrix type="hueRotate" values="{hue_for(n2):.1f}"/></filter>')
defs.append('</defs>')
p.add("".join(defs))

# --- dashed level circles and the axes ------------------------------------------------------------
for r in (1.0, 2.0):
    p.circle(0, 0, r, TEXT, 1.1, "5 4", "none", 0.42)
p.origin_axes("x", "y")

for x, s, dx, dy, anc in ((1, "1", 4, 13, "start"), (2, "2", 4, 13, "start"),
                          (-1, MINUS_S + "1", -4, -5, "end"), (-2, MINUS_S + "2", -4, -5, "end")):
    num_label(x, 0, s, dx, dy, anc)
for y, s, dx, dy, anc in ((1, "1", 6, -5, "start"), (2, "2", 6, -5, "start"),
                          (-1, MINUS_S + "1", -6, 13, "end"), (-2, MINUS_S + "2", -6, 11, "end")):
    # -2 sits 2 px higher: the head of the arrow from (-1, -2) ends just below-left of it
    num_label(0, y, s, dx, dy, anc)

# --- counter-clockwise rotation arrows on both circles --------------------------------------------
# The inner arcs are 30 deg long and turned 5 deg forward: centred on 45 deg, their tails met the heads
# of the arrows at (1, 0), (0, 1), (-1, 0), (0, -1); now tail and head clear arrows and labels by ~14 px.
for r, span, shift in ((1.0, 30, 5), (2.0, 22, 0)):
    for a_mid in (45, 135, 225, 315):
        rotation_arrow(r, a_mid + shift, span, TEXT, 1.25, 6.5, 0.55)

# --- the field, grouped by length so each class gets its hue ---------------------------------------
for n2 in CLASSES:
    pts = [(a, b) for a in range(-2, 3) for b in range(-2, 3) if a * a + b * b == n2]
    p.add(f'<g filter="url(#{FID}-{n2})">' if n2 != 1 else '<g>')
    head = 7.0 if n2 <= 2 else 8.0
    for a, b in pts:
        p.arrow((a, b), tip(a, b), THEORY, 1.9, head=head)
    for a, b in pts:
        dot(p, (a, b), THEORY, 2.4)
    p.add('</g>')

# --- rot V = 2 U3: out-of-page symbol at the origin -----------------------------------------------
ox, oy = p.X(0), p.Y(0)
p.add(f'<circle cx="{ox:.1f}" cy="{oy:.1f}" r="7.5" fill="{BG}" stroke="{PRACTICE}" stroke-width="1.7"/>')
p.add(f'<circle cx="{ox:.1f}" cy="{oy:.1f}" r="2.4" fill="{PRACTICE}"/>')
boxed_text(0, 0, "rot " + ital("V") + " = 2" + ital("U") + subs("3"), 70, 0, 28, PRACTICE, 11.5, "middle")

# --- corner formulas ------------------------------------------------------------------------------
p.label(-3.0, 2.72, ital("V") + " = " + MINUS_S + ital("y") + ital("U") + subs("1") + " + "
        + ital("x") + ital("U") + subs("2"), 0, 0, THEORY, 11.5, "start")

# d(phi) = 2 dx ^ dy; the wedge is drawn as a path because the figure font has no U+2227.
# Proportions follow the wedge() of dform-jacobi-birim-kare so the chapter's wedges match; the runs on
# both sides are anchored on the side facing the wedge, so another font never moves it.
WX, WY, SIZE = p.X(2.62), p.Y(-2.78), 11.5
HALF, TALLW = 0.26 * SIZE, 0.58 * SIZE
GAP = HALF + 0.24 * SIZE
p.text_px(WX - GAP, WY, ital("d") + ital("&#966;") + " = 2 " + ital("d") + ital("x"), TEXT, SIZE, "end")
p.add(f'<path d="M{WX - HALF:.1f},{WY:.1f} L{WX:.1f},{WY - TALLW:.1f} L{WX + HALF:.1f},{WY:.1f}" '
      f'fill="none" stroke="{TEXT}" stroke-width="0.95" stroke-linejoin="miter" stroke-linecap="round"/>')
p.text_px(WX + GAP, WY, ital("d") + ital("y"), TEXT, SIZE, "start")

# The caption avoids the wedge entity as well (the site font has no U+2227): the product is named in words.
OUT["dform-donen-alan"] = figure(
    400, 412, [p],
    "<em>V</em> = &#8722;<em>y</em><em>U</em><sub>1</sub> + <em>x</em><em>U</em><sub>2</sub> alanının "
    "&#8722;2..2 tam sayı ızgarasındaki okları; okunaklılık için her ok gerçek boyunun 0,4 katıyla "
    "çizilmiş, boyu arttıkça maviden mora doğru renklendirilmiştir. Her ok, başlangıç noktası merkezli ve "
    "kendi noktasından geçen çembere teğettir, gerçek boyu da o çemberin yarıçapına eşittir; yarıçapı 1 ve 2 "
    "olan kesikli çemberlerdeki küçük oklar, alanın <em>z</em> ekseni çevresinde saat yönünün tersine "
    "döndüğünü gösterir. Okların boyu merkezden uzaklaştıkça artsa da dönmenin ölçüsü her yerde aynıdır: "
    "<em>dx</em> ile <em>dy</em>&#8217;nin kama çarpımının 2 katı olan <em>d</em>&#966;, ikinci eşleme "
    "altında sabit rot <em>V</em> = 2<em>U</em><sub>3</sub> alanına karşılık gelir. Başlangıç noktasındaki, "
    "ortasında nokta bulunan küçük daire bu vektörün sayfadan dışarıya, dönme ekseni doğrultusunda baktığını "
    "gösterir.",
    aria="Duzlemde V = -y U1 + x U2 alaninin -2..2 tam sayi izgarasindaki oklari, 0,4 katiyla kisaltilmis, "
         "uzunluga gore maviden mora renkli; yaricapi 1 ve 2 olan kesikli gri cemberler uzerinde saat "
         "yonunun tersine donus oklari; baslangic noktasinda sayfadan disari simgesi ve rot V = 2 U3 "
         "etiketi; kosede d phi = 2 dx wedge dy.")

# ============================================================ dform-isaretli-alan
# -*- coding: utf-8 -*-
# dform-isaretli-alan — the signed area A(v, w) = v1 w2 - v2 w1 in three panels (2D).
# Left:   v = (3, 1) blue, w = (1, 2) orange; the parallelogram (0, 0), (3, 1), (4, 3), (1, 2)
#         is shaded and hatched blue; a counter-clockwise turn from v to w; A(v, w) = 5.
# Middle: the same parallelogram shaded and hatched red (the practice colour, hatch slanted the
#         other way); w first, then v; a clockwise turn from w to v; A(w, v) = -5.
# Right:  v and its dashed copy from (3, 1) to (6, 2); the parallelogram (0, 0), (3, 1), (6, 2),
#         (3, 1) collapses onto the thick grey segment from (0, 0) to (6, 2); A(v, v) = 0.
# Every panel: x in [-1, 7], y in [-1, 4], equal scale, origin O = (0, 0).
import math

XR, YR = (-1.0, 7.0), (-1.0, 4.0)
PW, PITCH, LEFT, TOP = 228, 262, 24, 34     # panel width, panel pitch, first panel x, panel top

O = (0.0, 0.0)
v = (3.0, 1.0)
w = (1.0, 2.0)
vw = (4.0, 3.0)                              # v + w, far corner of the parallelogram
vv = (6.0, 2.0)                              # v + v, end of the collapsed parallelogram
PARA = [O, v, vw, w]

A_V = math.degrees(math.atan2(v[1], v[0]))  # direction of v, 18.43 deg
A_W = math.degrees(math.atan2(w[1], w[0]))  # direction of w, 63.43 deg
R_TURN, GAP = 1.6, 8.0                       # turn-arrow radius (data units), gap to the arrows (deg);
                                             # 8 deg at this radius leaves about 6 px to either vector


def ital(s):
    return f'<tspan font-style="italic">{s}</tspan>'


def halo(p, x, y, s, dx=0, dy=0, color=TEXT, size=11.5, anchor="start"):
    """Label at a data point with a page-coloured halo, so grid and hatch lines behind it break."""
    p.add(f'<text x="{p.X(x) + dx:.1f}" y="{p.Y(y) + dy:.1f}" fill="{color}" font-size="{size}" '
          f'text-anchor="{anchor}" stroke="{BG}" stroke-width="3.2" stroke-linejoin="round" '
          f'paint-order="stroke">{s}</text>')


def panel(k, title, color):
    """Equal-scale panel k with a light integer grid in the first quadrant, axes and a title."""
    p = cplane(LEFT + k * PITCH, TOP, PW, XR, YR)
    for gx in range(1, 7):
        p.line([(gx, 0), (gx, YR[1])], TEXT, 0.7, None, 0.13)
    for gy in (1, 2, 3):
        p.line([(0, gy), (XR[1], gy)], TEXT, 0.7, None, 0.13)
    p.origin_axes("x", "y", xticks=(1, 2, 3, 4, 5, 6), yticks=(1, 2, 3))
    p.text_px(p.x0 + p.w / 2, p.y0 - 14, title, color, 12.5, "middle")
    return p


def hatch(p, poly, angle_deg, color, step_px=6.0, width=0.9, opacity=0.55):
    """Parallel hatch lines at angle_deg, clipped to a convex polygon given in data coordinates."""
    a = math.radians(angle_deg)
    d = (math.cos(a), math.sin(a))
    n = (-d[1], d[0])
    step = step_px * (p.xmax - p.xmin) / p.w          # pixels -> data units (equal scale)
    proj = [n[0] * x + n[1] * y for x, y in poly]
    lo, hi = min(proj), max(proj)
    count = int((hi - lo) / step)
    c0 = lo + (hi - lo - (count - 1) * step) / 2       # centre the family inside the polygon
    parts = []
    for i in range(count):
        c = c0 + i * step
        hits = []
        for j in range(len(poly)):
            (x0, y0), (x1, y1) = poly[j], poly[(j + 1) % len(poly)]
            s0 = n[0] * x0 + n[1] * y0 - c
            s1 = n[0] * x1 + n[1] * y1 - c
            if (s0 < 0) != (s1 < 0):
                t = s0 / (s0 - s1)
                hits.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t))
        if len(hits) >= 2:
            hits.sort(key=lambda q: d[0] * q[0] + d[1] * q[1])
            parts.append(f"M{p.P(*hits[0])} L{p.P(*hits[-1])}")
    p.add(f'<path d="{" ".join(parts)}" fill="none" stroke="{color}" stroke-width="{width}" '
          f'opacity="{opacity}" stroke-linecap="butt"/>')


def turn_arrow(p, r, a0, a1, color=TEXT, width=1.5, head=6.5):
    """Small circular arc about O from angle a0 to a1 (degrees) with an arrowhead at a1.
    A page-coloured halo underneath breaks the hatch lines around it."""
    n = 60
    pts = [(p.X(r * math.cos(math.radians(a0 + (a1 - a0) * k / n))),
            p.Y(r * math.sin(math.radians(a0 + (a1 - a0) * k / n)))) for k in range(n + 1)]
    tx, ty = pts[-1]
    j = n
    while j > 0 and math.hypot(pts[j][0] - tx, pts[j][1] - ty) < head:
        j -= 1
    bx, by = pts[j]
    L = math.hypot(tx - bx, ty - by)
    ux, uy = (tx - bx) / L, (ty - by) / L             # chord direction into the tip
    px, py, hw = -uy, ux, head * 0.45
    k = n
    while k > 0 and math.hypot(pts[k][0] - tx, pts[k][1] - ty) < head * 0.75:
        k -= 1

    def path(q):
        return " ".join(("M" if i == 0 else "L") + f"{x:.1f},{y:.1f}" for i, (x, y) in enumerate(q))

    p.add(f'<path d="{path(pts)}" fill="none" stroke="{BG}" stroke-width="{width + 2.4}" '
          f'stroke-linecap="round" stroke-linejoin="round"/>')
    p.add(f'<path d="{path(pts[:k + 1])}" fill="none" stroke="{color}" stroke-width="{width}" '
          f'stroke-linecap="round" stroke-linejoin="round"/>')
    hx, hy = tx - ux * head, ty - uy * head
    p.add(f'<polygon points="{tx:.1f},{ty:.1f} {hx + px * hw:.1f},{hy + py * hw:.1f} '
          f'{hx - px * hw:.1f},{hy - py * hw:.1f}" fill="{color}"/>')


def dashed_arrow(p, p0, p1, color, width, head, dash):
    """Dashed arrow; the shaft is drawn from the head backwards so a full dash meets the head."""
    x0, y0, x1, y1 = p.X(p0[0]), p.Y(p0[1]), p.X(p1[0]), p.Y(p1[1])
    L = math.hypot(x1 - x0, y1 - y0)
    ux, uy = (x1 - x0) / L, (y1 - y0) / L
    px, py, hw = -uy, ux, head * 0.42
    sx, sy = x1 - ux * head * 0.85, y1 - uy * head * 0.85
    p.add(f'<line x1="{sx:.1f}" y1="{sy:.1f}" x2="{x0:.1f}" y2="{y0:.1f}" stroke="{color}" '
          f'stroke-width="{width}" stroke-dasharray="{dash}" stroke-linecap="butt"/>')
    p.add(f'<polygon points="{x1:.1f},{y1:.1f} {x1 - ux * head + px * hw:.1f},{y1 - uy * head + py * hw:.1f} '
          f'{x1 - ux * head - px * hw:.1f},{y1 - uy * head - py * hw:.1f}" fill="{color}"/>')


def origin_label(p):
    halo(p, 0, 0, bold("O"), -6, 14, TEXT, 11, "end")


# ---- left: A(v, w) = 5, counter-clockwise ------------------------------------------------------
p1 = panel(0, ital("A") + "(" + bold("v") + ", " + bold("w") + ") = 5", THEORY)
p1.polygon(PARA, THEORY, 0.10)
hatch(p1, PARA, 45, THEORY)
p1.line([v, vw, w], THEORY, 1.2, None, 0.75)
turn_arrow(p1, R_TURN, A_V + GAP, A_W - GAP)
p1.arrow(O, v, THEORY, 2.4, head=9)
p1.arrow(O, w, PRACTICE, 2.4, head=9)
dot(p1, O, TEXT, 2.6)
dot(p1, vw, TEXT, 2.4)
origin_label(p1)
halo(p1, *v, bold("v") + " = (3, 1)", 8, 4, THEORY, 11.5)
halo(p1, *w, bold("w") + " = (1, 2)", -17, -17, PRACTICE, 11.5)
halo(p1, *vw, "(4, 3)", 7, 4, TEXT, 11)

# ---- middle: A(w, v) = -5, clockwise -----------------------------------------------------------
p2 = panel(1, ital("A") + "(" + bold("w") + ", " + bold("v") + ") = " + MINUS_S + "5", PRACTICE)
p2.polygon(PARA, PRACTICE, 0.10)
hatch(p2, PARA, -45, PRACTICE)
p2.line([v, vw, w], PRACTICE, 1.2, None, 0.75)
turn_arrow(p2, R_TURN, A_W - GAP, A_V + GAP)
p2.arrow(O, w, PRACTICE, 2.4, head=9)       # first argument
p2.arrow(O, v, THEORY, 2.4, head=9)         # second argument
dot(p2, O, TEXT, 2.6)
dot(p2, vw, TEXT, 2.4)
origin_label(p2)
halo(p2, *w, bold("w"), 0, -9, PRACTICE, 12, "middle")
halo(p2, *v, bold("v"), 8, 4, THEORY, 12)

# ---- right: A(v, v) = 0, collapsed ---------------------------------------------------------------
p3 = panel(2, ital("A") + "(" + bold("v") + ", " + bold("v") + ") = 0", TEXT)
p3.line([O, vv], TEXT, 7.5, None, 0.25)     # the parallelogram squashed onto a segment
p3.arrow(O, v, THEORY, 2.4, head=9)
dashed_arrow(p3, v, vv, THEORY, 2.2, 9, "5 3.5")
dot(p3, O, TEXT, 2.6)
origin_label(p3)
halo(p3, 1.5, 0.5, bold("v"), -2, -12, THEORY, 12, "middle")
halo(p3, 4.5, 1.5, bold("v"), -2, -12, THEORY, 12, "middle")
halo(p3, *v, "(3, 1)", 6, 16, TEXT, 11)
halo(p3, *vv, "(6, 2)", 0, -11, TEXT, 11, "middle")

OUT["dform-isaretli-alan"] = figure(
    800, 200, [p1, p2, p3],
    "<strong>v</strong> = (3, 1) ve <strong>w</strong> = (1, 2) vektörlerinin belirlediği, köşeleri "
    "(0, 0), (3, 1), (4, 3), (1, 2) olan paralelkenarın alanı 5&#8217;tir. Soldaki panelde "
    "<strong>v</strong>&#8217;den <strong>w</strong>&#8217;ye saat yönünün tersine dönülür ve "
    "<em>A</em>(<strong>v</strong>, <strong>w</strong>) = 5 olur; ortadaki panelde paralelkenar aynıdır, "
    "ama sıra değiştiği için <strong>w</strong>&#8217;den <strong>v</strong>&#8217;ye saat yönünde dönülür "
    "ve <em>A</em>(<strong>w</strong>, <strong>v</strong>) = &#8722;5 olur. Sağdaki panelde "
    "<strong>v</strong> iki kez alınmıştır: paralelkenar (0, 0) ile (6, 2) arasındaki doğru parçasına "
    "çöker ve <em>A</em>(<strong>v</strong>, <strong>v</strong>) = 0 olur.",
    css_class=WIDE,
    aria="Uc panel. Solda v = (3, 1) mavi ve w = (1, 2) turuncu oklarin belirledigi, koseleri (0, 0), "
         "(3, 1), (4, 3), (1, 2) olan mavi tarali paralelkenar, v'den w'ye saat yonunun tersine donen ok, "
         "A(v, w) = 5. Ortada ayni paralelkenar turuncu tarali, w'den v'ye saat yonunde donen ok, "
         "A(w, v) = -5. Sagda v oku ve (3, 1)'den (6, 2)'ye kesikli kopyasi; paralelkenar (0, 0) ile "
         "(6, 2) arasindaki kalin gri dogru parcasina coker, A(v, v) = 0",
)

# ============================================================ dform-jacobi-birim-kare
# -*- coding: utf-8 -*-
# dform-jacobi-birim-kare: the unit square of the (x, y) plane and its images under
# (x, y) -> (f, g) = (2x + y, -x + y) and (x, y) -> (g, f) = (-x + y, 2x + y).
# All three panels share one scale (PPU pixels per unit), so both parallelograms visibly
# cover three times the area of the square.
# Colour convention for this figure: U1 and its images -> THEORY, U2 and its images -> PRACTICE.
# Fills: square TEXT (grey), orientation-preserving image THEORY, orientation-reversing image
# PRACTICE (the palette has no red token). Rotation symbols are TEXT.
# The wedge glyph is missing from the figure font, so every wedge is drawn as two strokes.
# Labels carry a page-coloured halo so the faint grid lines break behind them. The tick at 3 is
# left without a number in both image panels: there the number would touch a closing edge, and
# the vertex labels (3, 0) and (0, 3) carry the value instead.

PPU = 64            # pixels per data unit, the same in every panel
GAP = 46            # horizontal space between panels
TOP = 40            # top of the tallest panel
BAND = 4 * PPU      # height of the tallest panel (the right one); the others are centred on it
RING_R = 0.25       # radius of the rotation symbols, data units
LEFT_X0 = 16


def ital(s):
    return f'<tspan font-style="italic">{s}</tspan>'


def num(v):
    """Integer tick label with a real minus sign."""
    return (MINUS_S + str(-v)) if v < 0 else str(v)


def panel(x0, xr, yr):
    w, h = (xr[1] - xr[0]) * PPU, (yr[1] - yr[0]) * PPU
    return Plot(x0, TOP + (BAND - h) / 2, w, h, xr, yr)


pl = panel(LEFT_X0, (-0.5, 1.5), (-0.5, 1.5))
pm = panel(pl.x0 + pl.w + GAP, (-0.5, 3.5), (-1.5, 1.5))
pr = panel(pm.x0 + pm.w + GAP, (-1.5, 1.5), (-0.5, 3.5))


def halo_px(p, px, py, s, color=TEXT, size=11, anchor="start", fill_opacity=1.0, italic=False):
    """Text at a pixel position with a page-coloured halo that breaks the lines behind it."""
    fo = f' fill-opacity="{fill_opacity}"' if fill_opacity < 1.0 else ""
    it = ' font-style="italic"' if italic else ""
    p.add(f'<text x="{px:.1f}" y="{py:.1f}" fill="{color}"{fo} font-size="{size}" text-anchor="{anchor}"{it} '
          f'stroke="{BG}" stroke-width="3" stroke-linejoin="round" paint-order="stroke">{s}</text>')


def halo(p, x, y, s, dx=0, dy=0, color=TEXT, size=11, anchor="start"):
    halo_px(p, p.X(x) + dx, p.Y(y) + dy, s, color, size, anchor)


def title(p, s):
    p.text_px(p.x0 + p.w / 2, p.y0 - 18, s, TEXT, 11.5, "middle")


def grid(p, xs, ys):
    for gx in xs:
        p.line([(gx, p.ymin), (gx, p.ymax)], TEXT, 0.7, None, 0.13)
    for gy in ys:
        p.line([(p.xmin, gy), (p.xmax, gy)], TEXT, 0.7, None, 0.13)


def ticks(p, xs, ys, xlabeled, ylabeled):
    """Tick marks on the axes through the origin, numbers (with halo) only where asked."""
    ox, oy = p.X(0), p.Y(0)
    for t in xs:
        p.add(f'<line x1="{p.X(t):.1f}" y1="{oy - 3:.1f}" x2="{p.X(t):.1f}" y2="{oy + 3:.1f}" '
              f'stroke="{TEXT}" stroke-width="1" opacity="0.7"/>')
        if t in xlabeled:
            halo_px(p, p.X(t), oy + 15, num(t), TEXT, 11, "middle", 0.7)
    for t in ys:
        p.add(f'<line x1="{ox - 3:.1f}" y1="{p.Y(t):.1f}" x2="{ox + 3:.1f}" y2="{p.Y(t):.1f}" '
              f'stroke="{TEXT}" stroke-width="1" opacity="0.7"/>')
        if t in ylabeled:
            halo_px(p, ox - 7, p.Y(t) + 4, num(t), TEXT, 11, "end", 0.7)


def ring_points(c, a0, a1, n=64):
    return [(c[0] + RING_R * math.cos(a0 + (a1 - a0) * k / n),
             c[1] + RING_R * math.sin(a0 + (a1 - a0) * k / n)) for k in range(n + 1)]


RING_SWEEP = math.radians(290)


def ring_angles(sign):
    """Start and end angle of the rotation symbol; the gap is at the top in both senses."""
    a0 = math.radians(125 if sign > 0 else 55)
    return a0, a0 + sign * RING_SWEEP


def ring_halo(p, c, sign):
    """Page-coloured ring under the rotation symbol: it breaks the axis line where the symbol
    crosses it. Drawn before the translucent fill, so the fill tints the ring back."""
    p.line(ring_points(c, *ring_angles(sign)), BG, 5.0)


def ring(p, c, sign, head=7.0, width=1.5, opacity=0.8):
    """Circular arrow around c: sign = +1 counter-clockwise, -1 clockwise."""
    a0, a1 = ring_angles(sign)
    rp = RING_R * PPU
    ab = a1 - sign * (head * 0.85) / rp          # arrowhead base on the arc
    shaft = ring_points(c, a0, ab)
    d = " ".join(("M" if i == 0 else "L") + p.P(x, y) for i, (x, y) in enumerate(shaft))
    tx, ty = p.X(c[0] + RING_R * math.cos(a1)), p.Y(c[1] + RING_R * math.sin(a1))
    bx, by = p.X(c[0] + RING_R * math.cos(ab)), p.Y(c[1] + RING_R * math.sin(ab))
    L = math.hypot(tx - bx, ty - by)
    ux, uy = (tx - bx) / L, (ty - by) / L
    px, py, hw = -uy, ux, head * 0.45
    p.add(f'<g opacity="{opacity}">'
          f'<path d="{d}" fill="none" stroke="{TEXT}" stroke-width="{width}" stroke-linecap="butt"/>'
          f'<polygon points="{tx:.1f},{ty:.1f} {tx - ux * head + px * hw:.1f},{ty - uy * head + py * hw:.1f} '
          f'{tx - ux * head - px * hw:.1f},{ty - uy * head - py * hw:.1f}" fill="{TEXT}"/></g>')


# em widths used to lay out the two-form labels. Every run next to a wedge is anchored on the
# side facing it ("d<first>" end, "d<second>" start, "= [-]3 dx" end, "dy" start), so a font with
# other widths never moves a wedge. "=" and the coefficient are one run: the spaces around "="
# come from the font itself, so "=" and a minus sign cannot run together (they did in Segoe UI,
# Arial and DejaVu Sans when "=" was a separate glyph centred between estimated widths). The only
# estimated gap left is the one before "="; EQ_GAP keeps it open in the site fonts (Source Sans
# Pro, Lato) and their stand-ins. An italic f leans past its advance width, so a run ending in f
# gets F_OVERHANG of extra room on its right.
EM = {"d": 0.50, "f": 0.28, "g": 0.50, "x": 0.46, "y": 0.46, "3": 0.50, " ": 0.25,
      "=": 0.56, MINUS_S: 0.56}
F_OVERHANG = 0.14
EQ_GAP = 0.50      # visible gap before "=": ~5.5 px in serif, >= 2.3 px in Segoe UI and Arial


def em(runs):
    """Width in em of a sequence of glyphs given as a list (so MINUS_S counts as one glyph)."""
    return sum(EM[ch] for ch in runs)


def right_overhang(word):
    return F_OVERHANG if word.endswith("f") else 0.0


def wedge(p, cx, base, size):
    ww, hh = 0.52 * size, 0.58 * size
    p.add(f'<path d="M{cx - ww / 2:.1f},{base:.1f} L{cx:.1f},{base - hh:.1f} L{cx + ww / 2:.1f},{base:.1f}" '
          f'fill="none" stroke="{TEXT}" stroke-width="0.95" stroke-linejoin="miter" stroke-linecap="round"/>')


def form_label(p, base, first, second, negative, size=11.5):
    """'d<first> ^ d<second> = [-]3 dx ^ dy' centred under panel p on the baseline `base`."""
    s = size
    sp_w, wedge_w, gap_eq = 0.24 * s, 0.52 * s, EQ_GAP * s
    word1, word2 = "d" + first, "d" + second
    rhs = ["=", " "] + ([MINUS_S] if negative else []) + ["3", " ", "d", "x"]
    w1, w2 = em(word1) * s, em(word2) * s
    o1, o2 = right_overhang(word1) * s, right_overhang(word2) * s
    wr, w4 = em(rhs) * s, em("dy") * s
    total = (w1 + o1 + 2 * sp_w + wedge_w + w2 + o2 + gap_eq + wr
             + 2 * sp_w + wedge_w + w4)
    x = p.x0 + p.w / 2 - total / 2

    a_end = x + w1
    p.text_px(a_end, base, word1, TEXT, s, "end", False, True)
    wedge(p, a_end + o1 + sp_w + wedge_w / 2, base, s)
    b_start = a_end + o1 + 2 * sp_w + wedge_w
    p.text_px(b_start, base, word2, TEXT, s, "start", False, True)
    c_end = b_start + w2 + o2 + gap_eq + wr                     # right edge of "= [-]3 dx"
    p.text_px(c_end, base, "= " + (MINUS_S if negative else "") + "3 " + ital("dx"), TEXT, s, "end")
    wedge(p, c_end + sp_w + wedge_w / 2, base, s)
    p.text_px(c_end + 2 * sp_w + wedge_w, base, "dy", TEXT, s, "start", False, True)


def quad(p, O, A, C, B, fill, fill_op, edge, edge_op, center, sign):
    """Common drawing order: ring halo, fill, closing edges A-C-B, the arrows O-A (blue) and
    O-B (orange), rotation symbol."""
    ring_halo(p, center, sign)
    p.polygon([O, A, C, B], fill, fill_op, "none")
    p.line([A, C, B], edge, 1.1, None, edge_op)
    p.arrow(O, A, THEORY, 2.4, head=9)
    p.arrow(O, B, PRACTICE, 2.4, head=9)
    ring(p, center, sign)


O = (0.0, 0.0)

# ---- left: the unit square ------------------------------------------------------------------
title(pl, "(" + ital("x") + ", " + ital("y") + ") düzlemi")
pl.origin_axes("x", "y")
ticks(pl, (1,), (1,), (1,), (1,))
quad(pl, O, (1, 0), (1, 1), (0, 1), TEXT, 0.10, TEXT, 0.45, (0.5, 0.5), +1)
halo(pl, 0.5, 0, ital("U") + subs("1"), 0, 18, THEORY, 12, "middle")
halo(pl, 0, 0.5, ital("U") + subs("2"), -8, 4, PRACTICE, 12, "end")

# ---- middle: (f, g) = (2x + y, -x + y) ------------------------------------------------------
title(pm, "(" + ital("f") + ", " + ital("g") + ") = (2" + ital("x") + " + " + ital("y") + ", "
      + MINUS_S + ital("x") + " + " + ital("y") + ")")
grid(pm, (1, 2, 3), (-1, 1))
pm.origin_axes("f", "g")
ticks(pm, (1, 2, 3), (-1, 1), (1, 2), (-1, 1))
quad(pm, O, (2, -1), (3, 0), (1, 1), THEORY, 0.16, THEORY, 0.6, (1.5, 0.0), +1)
halo(pm, 2, -1, "(2, " + MINUS_S + "1)", 0, 16, THEORY, 11, "middle")
halo(pm, 1, 1, "(1, 1)", 0, -9, PRACTICE, 11, "middle")
halo(pm, 3, 0, "(3, 0)", 3, -8, TEXT, 11, "start")
form_label(pm, pm.y0 + pm.h + 26, "f", "g", False)

# ---- right: (g, f) = (-x + y, 2x + y) -------------------------------------------------------
# the ")" after the italic f is nudged 2 px right: the f's hook reached over it in every test font
title(pr, "(" + ital("g") + ", " + ital("f") + '<tspan dx="2">)</tspan> = (' + MINUS_S + ital("x") + " + "
      + ital("y") + ", 2" + ital("x") + " + " + ital("y") + ")")
grid(pr, (-1, 1), (1, 2, 3))
pr.origin_axes("g", "f")
ticks(pr, (-1, 1), (1, 2, 3), (-1, 1), (1, 2))
quad(pr, O, (-1, 2), (0, 3), (1, 1), PRACTICE, 0.16, PRACTICE, 0.6, (0.0, 1.5), -1)
halo(pr, -1, 2, "(" + MINUS_S + "1, 2)", -8, 4, THEORY, 11, "end")
halo(pr, 1, 1, "(1, 1)", 8, 4, PRACTICE, 11, "start")
halo(pr, 0, 3, "(0, 3)", -7, -7, TEXT, 11, "end")
form_label(pr, pr.y0 + pr.h + 26, "g", "f", True)

OUT["dform-jacobi-birim-kare"] = figure(
    int(pr.x0 + pr.w + 40), int(TOP + BAND + 46), [pl, pm, pr],
    "Solda birim kare, ortada ve sağda iki lineer dönüşüm altındaki görüntüleri; üç panel aynı "
    "ölçekle çizildiğinden iki paralelkenarın da karenin üç katı alan kapladığı görülür. Mavi oklar "
    "<em>U</em><sub>1</sub>&#8217;i ve görüntülerini, turuncu oklar <em>U</em><sub>2</sub>&#8217;yi ve "
    "görüntülerini gösterir. (<em>f</em>, <em>g</em>) = (2<em>x</em> + <em>y</em>, &#8722;<em>x</em> + "
    "<em>y</em>) altında maviden turuncuya dönüş karedeki gibi saat yönünün tersinedir ve katsayı 3 "
    "çıkar; koordinatların yeri değişince paralelkenar yansır, dönüş saat yönüne çevrilir ve katsayı "
    "&#8722;3 olur. İşaret alanın büyüklüğünü değil, yönünü kaydeder.",
    css_class=WIDE,
    aria="Uc panel ayni olcekte. Solda (x, y) duzleminde birim kare, U1 mavi ok (0,0)->(1,0), U2 turuncu "
         "ok (0,0)->(0,1), saat yonunun tersine donus. Ortada (f, g) = (2x + y, -x + y) altinda koseleri "
         "(0,0), (2,-1), (3,0), (1,1) olan acik mavi paralelkenar, saat yonunun tersine donus, "
         "df wedge dg = 3 dx wedge dy. Sagda (g, f) = (-x + y, 2x + y) altinda koseleri (0,0), (-1,2), "
         "(0,3), (1,1) olan paralelkenar, saat yonunde donus, dg wedge df = -3 dx wedge dy.",
)

# ============================================================ dform-paralelkenar-izdusumleri
# -*- coding: utf-8 -*-
# dform-paralelkenar-izdusumleri: the parallelogram spanned by v = (2, 0, 1) and w = (0, 3, 1),
# corners 0, v, v + w = (2, 3, 2), w, area 7, and its shadows on the three coordinate planes:
#   xy (z = 0): rectangle     0, (2, 0, 0), (2, 3, 0), (0, 3, 0)   signed area dx^dy = 6
#   xz (y = 0): parallelogram 0, (2, 0, 1), (2, 0, 2), (0, 0, 1)   signed area dx^dz = 2
#   yz (x = 0): parallelogram 0, (0, 0, 1), (0, 3, 2), (0, 3, 1)   signed area dy^dz = -3
# Colours: only the theme tokens exist. v lies in the wall y = 0 and w in the wall x = 0, so each
# wall shadow takes the colour of the vector lying in it (xz THEORY like v, yz PRACTICE like w);
# the floor shadow is BASE and the parallelogram itself is hatched TEXT grey.
# Camera: the normal v x w = (-3, -2, 6) leans away from the usual view. Up to elevation ~30 the
# parallelogram is seen edge-on and lies on top of both wall shadows (_dform_cam_sheet.py);
# above ~31 the two wall shadows fold away from it along v and w. Azimuth 50: the y axis and the
# guide (2, 3, 2) -> (2, 0, 2) are parallel on the page and pass on either side of the centre of
# the parallelogram; at azimuth 40 that strip is too narrow for the label "alan 7".
import math
import re

AZ, EL = 50.0, 48.0
AX = 3.5
cam = Camera(azimuth=AZ, elevation=EL, scale=1.0)

O = (0.0, 0.0, 0.0)
v = (2.0, 0.0, 1.0)
w = (0.0, 3.0, 1.0)
s = vadd(v, w)                                                   # (2, 3, 2)
PARA = [O, v, s, w]
SH_XY = [O, (2.0, 0.0, 0.0), (2.0, 3.0, 0.0), (0.0, 3.0, 0.0)]
SH_XZ = [O, (2.0, 0.0, 1.0), (2.0, 0.0, 2.0), (0.0, 0.0, 1.0)]
SH_YZ = [O, (0.0, 0.0, 1.0), (0.0, 3.0, 2.0), (0.0, 3.0, 1.0)]

# panel range from the projections of everything drawn, plus room for the labels
drawn = [O, (AX, 0, 0), (0, AX, 0), (0, 0, AX), (3, 0, 0), (0, 3, 0), (3, 3, 0)] + PARA + SH_XZ + SH_YZ
XY = [cam.project(Q)[:2] for Q in drawn]
X0, X1 = min(t[0] for t in XY) - 0.45, max(t[0] for t in XY) + 1.05
Y0, Y1 = min(t[1] for t in XY) - 0.25, max(t[1] for t in XY) + 0.3
P = space_panel(16, 14, 368, (X0, X1), (Y0, Y1))
S = Space(P, cam)


# ---------------------------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------------------------
def ital(t):
    return f'<tspan font-style="italic">{t}</tspan>'


def px(Q):
    X, Y = S.pt(Q)
    return P.X(X), P.Y(Y)


WIDTH = {" ": 0.25, "(": 0.33, ")": 0.33, ",": 0.25, ":": 0.28, "=": 0.56, "l": 0.28, "−": 0.56}


def est_width(t, size):
    plain = re.sub(r"<[^>]+>", "", t).replace("&#8722;", "−")
    return sum(WIDTH.get(ch, 0.5) for ch in plain) * size


BOXES = []    # pixel boxes of all labels; faint lines (floor grid, hatching) break around them
LABELS = []   # label drawing calls, run after everything else


def reserve(x0, y0, x1, y1, pad=3.0):
    BOXES.append((x0 - pad, y0 - pad, x1 + pad, y1 + pad))


def halo_text(x, y, t, color=TEXT, size=11.5, anchor="start"):
    """Text at pixel (x, y) with a page-coloured halo."""
    P.add(f'<text x="{x:.1f}" y="{y:.1f}" fill="{color}" font-size="{size}" text-anchor="{anchor}" '
          f'stroke="{BG}" stroke-width="3.2" stroke-linejoin="round" paint-order="stroke">{t}</text>')


def plan_text(Q, t, dx, dy, color=TEXT, size=11.5, anchor="start", halo=True):
    x, y = px(Q)
    x, y = x + dx, y + dy
    wid = est_width(t, size)
    x0 = x if anchor == "start" else (x - wid / 2 if anchor == "middle" else x - wid)
    reserve(x0, y - 0.72 * size, x0 + wid, y + 0.22 * size)
    if halo:
        LABELS.append(lambda: halo_text(x, y, t, color, size, anchor))
    else:
        LABELS.append(lambda: P.text_px(x, y, t, color, size, anchor))


def plan_form(Q, a, b, value, dx, dy, color, size=11.5):
    """Label 'da ^ db: value' whose wedge is centred at pixel offset (dx, dy) from Q, on the baseline.
    The wedge sign is missing from the figure font, so it is drawn as a thin chevron polygon."""
    qx, qy = px(Q)
    cx, base = qx + dx, qy + dy
    hw, top, th = 0.27 * size, 0.56 * size, 0.085 * size
    gap = hw + 0.24 * size
    left, right = ital("d" + a), ital("d" + b) + ": " + value
    reserve(cx - gap - est_width(left, size), base - 0.72 * size,
            cx + gap + est_width(right, size), base + 0.22 * size)

    def draw():
        halo_text(cx - gap, base, left, color, size, "end")
        halo_text(cx + gap, base, right, color, size, "start")
        L = math.hypot(hw, top)
        apex_in, foot_in = th * L / hw, th * L / top
        pts = [(cx - hw, base), (cx, base - top), (cx + hw, base), (cx + hw - foot_in, base),
               (cx, base - top + apex_in), (cx - hw + foot_in, base)]
        P.add('<polygon points="%s" fill="%s" fill-opacity="1" stroke="%s" stroke-width="2.4" '
              'stroke-linejoin="round" paint-order="stroke"/>'
              % (" ".join("%.1f,%.1f" % q for q in pts), color, BG))
    LABELS.append(draw)


def outside_box(A, B, box):
    """Pieces of the space segment A-B whose projection stays outside the pixel box (x0, y0, x1, y1)."""
    (ax, ay), (bx, by) = px(A), px(B)
    x0, y0, x1, y1 = box
    ddx, ddy = bx - ax, by - ay
    t0, t1 = 0.0, 1.0
    for p_, q_ in ((-ddx, ax - x0), (ddx, x1 - ax), (-ddy, ay - y0), (ddy, y1 - ay)):
        if p_ == 0:
            if q_ < 0:
                return [(A, B)]
            continue
        r = q_ / p_
        if p_ < 0:
            t0 = max(t0, r)
        else:
            t1 = min(t1, r)
    if t0 >= t1:
        return [(A, B)]
    at = lambda r: vadd(A, vscale(r, vsub(B, A)))          # noqa: E731
    return ([(A, at(t0))] if t0 > 0 else []) + ([(at(t1), B)] if t1 < 1 else [])


def gapped_line(A, B, color, width, opacity):
    pieces = [(A, B)]
    for box in BOXES:
        pieces = [q for a_, b_ in pieces for q in outside_box(a_, b_, box)]
    for a_, b_ in pieces:
        S.line([a_, b_], color, width, None, opacity)


def on_para(a, b):
    return vadd(vscale(a, v), vscale(b, w))


def tick_mark(Q, d):
    S.line([vadd(Q, vscale(-0.04, d)), vadd(Q, vscale(0.04, d))], TEXT, 1.0, None, 0.7)


# ---------------------------------------------------------------------------------------------
# label layout first, so that the faint lines can break around the labels
# ---------------------------------------------------------------------------------------------
# tick labels: the digits 1 on x and y would sit under the parallelogram and are left out
plan_text((2, 0, 0), "2", -9, -3, TEXT, 10, "middle", halo=False)
plan_text((3, 0, 0), "3", -9, -3, TEXT, 10, "middle", halo=False)
plan_text((0, 2, 0), "2", 3, 18, TEXT, 10, "middle", halo=False)
plan_text((0, 3, 0), "3", 9, -5, TEXT, 10, "middle", halo=False)
plan_text((0, 0, 1), "1", -8, -3, TEXT, 10, "end", halo=False)
plan_text((0, 0, 2), "2", -9, 4, TEXT, 10, "end", halo=False)
plan_text((0, 0, 3), "3", -9, 4, TEXT, 10, "end", halo=False)

plan_text(v, bold("v") + " = (2, 0, 1)", -10, 16, THEORY, 11.5, "end")
plan_text(w, bold("w") + " = (0, 3, 1)", 9, 4, PRACTICE, 11.5, "start")
plan_text(vscale(0.5, s), "alan 7", 0, 3, TEXT, 11.5, "middle")
plan_form((1.5, 1.5, 0.0), "x", "y", "6", -7, 4, BASE)       # left of the guide under (2, 3, 2)
plan_form((2.0, 0.0, 1.5), "x", "z", "2", -41, 4, THEORY)
plan_form((0.0, 1.5, 1.5), "y", "z", MINUS_S + "3", 20, -9, PRACTICE)

# ---------------------------------------------------------------------------------------------
# drawing, back to front
# ---------------------------------------------------------------------------------------------
# 1. floor grid and the three shadows
for k in range(4):
    gapped_line((k, 0, 0), (k, 3, 0), TEXT, 0.7, 0.12)
    gapped_line((0, k, 0), (3, k, 0), TEXT, 0.7, 0.12)
S.polygon(SH_XY, BASE, 0.20, BASE, 1.1)
S.polygon(SH_XZ, THEORY, 0.20, THEORY, 1.1)
S.polygon(SH_YZ, PRACTICE, 0.20, PRACTICE, 1.1)

# 2. axes and tick marks
S.axes(AX, AX, AX)
for k in (1, 2, 3):
    tick_mark((k, 0, 0), (0, 1, 0))
    tick_mark((0, k, 0), (1, 0, 0))
    tick_mark((0, 0, k), (1, 0, 0))

# 3. projection guides from the corners to the coordinate planes
for A, B in ((v, (2, 0, 0)), (s, (2, 3, 0)), (w, (0, 3, 0)),     # onto z = 0
             (s, (2, 0, 2)), (w, (0, 0, 1)),                     # onto y = 0
             (s, (0, 3, 2)), (v, (0, 0, 1))):                    # onto x = 0
    S.guide([A, B], TEXT, 0.5)

# 4. the parallelogram: translucent grey, hatched along v - w, outlined where no arrow runs
S.polygon(PARA, TEXT, 0.10)
N_HATCH = 9
for k in range(1, N_HATCH + 1):
    c = 2.0 * k / (N_HATCH + 1)
    a0, a1 = max(0.0, c - 1.0), min(1.0, c)
    gapped_line(on_para(a0, c - a0), on_para(a1, c - a1), TEXT, 0.8, 0.3)
S.line([v, s, w], TEXT, 1.3, None, 0.8)

# 5. vector parts from the origin
S.arrow(O, v, THEORY, 2.4, head=9)
S.arrow(O, w, PRACTICE, 2.4, head=9)
S.point(O, TEXT, 3.0)
S.point(s, TEXT, 2.6)

# 6. labels
for draw_label in LABELS:
    draw_label()

OUT["dform-paralelkenar-izdusumleri"] = figure(
    400, int(14 + P.h + 14), [P],
    "Mavi ve turuncu oklar <strong>v</strong> = (2, 0, 1) ve <strong>w</strong> = (0, 3, 1) vektör "
    "kısımlarıdır; gerdikleri gri taralı paralelkenarın alanı 7&#8217;dir. Kesikli kılavuzlar köşeleri "
    "koordinat düzlemlerine indirir: gölgelerin işaretli alanları <em>xy</em>-düzlemindeki yeşil "
    "dikdörtgende 6, <em>xz</em>-düzlemindeki mavi paralelkenarda 2, <em>yz</em>-düzlemindeki turuncu "
    "paralelkenarda &#8722;3&#8217;tür. Bir 2-formun üç katsayısı bu üç alanı tartar; "
    "6<sup>2</sup> + 2<sup>2</sup> + (&#8722;3)<sup>2</sup> = 7<sup>2</sup> eşitliği ise alanlar için bir "
    "Pitagoras bağıntısıdır.",
    aria="v = (2, 0, 1) ve w = (0, 3, 1) vektorlerinin gerdigi, koseleri (0, 0, 0), (2, 0, 1), (2, 3, 2), "
         "(0, 3, 1) olan alani 7 paralelkenar ve koordinat duzlemlerine izdusumleri: xy-duzleminde isaretli "
         "alani dx^dy = 6 olan dikdortgen, xz-duzleminde dx^dz = 2 ve yz-duzleminde dy^dz = -3 olan "
         "paralelkenarlar; koselerden duzlemlere kesikli kilavuzlar",
)

# ============================================================ dform-silindirik-hacim-parcasi
# -*- coding: utf-8 -*-
# dform-silindirik-hacim-parcasi: the piece 2 <= r <= 2.5, pi/6 <= theta <= pi/4, 0 <= z <= 0.6 of
# space in cylindrical coordinates (blue, hatched), bounded by two pieces of the coaxial cylinders
# r = 2 and r = 2.5 (grey tint), the half-planes theta = pi/6, pi/4 and the planes z = 0, 0.6.
# From its corner (r, theta, z) = (2, pi/6, 0) = (sqrt 3, 1, 0) leave the three edges
#   dr = 1/2 (radial, to (2.17, 1.25, 0)), r dtheta = 2 pi/12 (arc of r = 2, to (1.41, 1.41, 0)),
#   dz = 3/5 (vertical, to (1.73, 1, 0.6)).
# Camera: azimuth -105 makes that corner the vertex nearest to the viewer, so all three edges are
# visible and come out with similar lengths. At the usual azimuth 20-50 the corner is the farthest
# vertex and the radial edge points at the viewer (at 30 it projects onto the vertical edge).
# No red token exists in the site palette, so the radial edge uses TEXT (as in form-kritik-noktalar).
import math

AZ, EL = -105.0, 30.0
R0, R1 = 2.0, 2.5
T0, T1 = math.pi / 6, math.pi / 4
Z0, Z1 = 0.0, 0.6
TH = "&#977;"                        # vartheta, as in the text


def cyl(r, t, z):
    return (r * math.cos(t), r * math.sin(t), z)


def arc_pts(r, z, t0, t1, n=24):
    return [cyl(r, t0 + (t1 - t0) * k / n, z) for k in range(n + 1)]


def it(s):
    return '<tspan font-style="italic">' + s + '</tspan>'


P = space_panel(10, 10, 400, (-1.25, 3.7), (-0.35, 3.1))
S = Space(P, Camera(azimuth=AZ, elevation=EL, scale=1.0))


def px(Q):
    X, Y = S.pt(Q)
    return (P.X(X), P.Y(Y))


def halo(x, y, s, color=TEXT, size=11.5, anchor="start", weight=None, opacity=1.0):
    """Text at pixel (x, y) on a page-coloured halo, so faint grid and hatch lines break around it."""
    w = f' font-weight="{weight}"' if weight else ""
    op = f' opacity="{opacity}"' if opacity < 1.0 else ""
    P.add(f'<text x="{x:.1f}" y="{y:.1f}" fill="{color}" font-size="{size}" text-anchor="{anchor}"{w}{op} '
          f'stroke="{BG}" stroke-width="3.2" stroke-linejoin="round" paint-order="stroke">{s}</text>')


def at(Q, s, dx, dy, color=TEXT, size=11.5, anchor="start", weight=None, opacity=1.0):
    x, y = px(Q)
    halo(x + dx, y + dy, s, color, size, anchor, weight, opacity)


def hatch(polys, color, step=4.4, angle=62.0, width=0.75, opacity=0.5):
    """Parallel hatch lines (pixel space) clipped to the union of the given pixel polygons."""
    a = math.radians(angle)
    ux, uy = math.cos(a), -math.sin(a)          # along the lines (screen y grows downward)
    nx, ny = -uy, ux                            # across the lines
    cs = [x * nx + y * ny for poly in polys for x, y in poly]
    c = min(cs) + step / 2
    out = []
    while c < max(cs):
        bx, by = c * nx, c * ny
        spans = []
        for poly in polys:
            ts = []
            for (x0, y0), (x1, y1) in zip(poly, poly[1:] + poly[:1]):
                d0, d1 = x0 * nx + y0 * ny - c, x1 * nx + y1 * ny - c
                if (d0 >= 0) != (d1 >= 0):
                    s = d0 / (d0 - d1)
                    xi, yi = x0 + s * (x1 - x0), y0 + s * (y1 - y0)
                    ts.append((xi - bx) * ux + (yi - by) * uy)
            ts.sort()
            spans += [(ts[k], ts[k + 1]) for k in range(0, len(ts) - 1, 2)]
        spans.sort()
        merged = []
        for s0, s1 in spans:
            if merged and s0 <= merged[-1][1] + 0.2:
                merged[-1] = (merged[-1][0], max(merged[-1][1], s1))
            else:
                merged.append((s0, s1))
        for s0, s1 in merged:
            if s1 - s0 > 1.0:
                out.append(f'<line x1="{bx + s0 * ux:.1f}" y1="{by + s0 * uy:.1f}" '
                           f'x2="{bx + s1 * ux:.1f}" y2="{by + s1 * uy:.1f}"/>')
        c += step
    P.add(f'<g stroke="{color}" stroke-width="{width}" opacity="{opacity}">{"".join(out)}</g>')


# --- corners of the piece ---------------------------------------------------------------------
A = cyl(R0, T0, Z0)          # the corner (sqrt 3, 1, 0)
B = cyl(R1, T0, Z0)          # end of the radial edge
C = cyl(R0, T1, Z0)          # end of the arc edge
D = cyl(R0, T0, Z1)          # end of the vertical edge
E = cyl(R1, T1, Z0)          # far bottom corner (hidden)
F = cyl(R1, T0, Z1)
G = cyl(R0, T1, Z1)
H = cyl(R1, T1, Z1)

TOP = arc_pts(R0, Z1, T0, T1) + arc_pts(R1, Z1, T1, T0)
INNER = arc_pts(R0, Z0, T0, T1) + arc_pts(R0, Z1, T1, T0)
OUTER = arc_pts(R1, Z0, T0, T1) + arc_pts(R1, Z1, T1, T0)
SIDE0 = [A, B, F, D]          # theta = pi/6
FRONT = (TOP, INNER, SIDE0)   # the faces turned toward the viewer tile the outline of the piece

# --- floor grid, axes, ticks ------------------------------------------------------------------
S.floor_grid((0, 3), (0, 3), n=3, opacity=0.13)
S.axes(3.45, 3.45, 3.3, offsets=((10, 4), (-6, -5), (-9, -3)))
for v in (1, 2, 3):
    S.line([(v, -0.05, 0), (v, 0.05, 0)], TEXT, 1.0, None, 0.7)
    S.line([(-0.05, v, 0), (0.05, v, 0)], TEXT, 1.0, None, 0.7)
    S.line([(-0.05, 0, v), (0.05, 0, v)], TEXT, 1.0, None, 0.7)
    at((v, 0, 0), str(v), 0, 16, TEXT, 10, "middle", opacity=0.8)
    at((0, v, 0), str(v), -9, 5, TEXT, 10, "end", opacity=0.8)
    at((0, 0, v), str(v), -9, 4, TEXT, 10, "end", opacity=0.8)

# --- the dashed r line to the corner and the angle theta = pi/6 on the floor --------------------
S.line([(0, 0, 0), A], TEXT, 1.2, "5 3", 0.6)
ANG = [cyl(0.62, T0 * k / 30, 0) for k in range(31)]
S.line(ANG[:-2], TEXT, 1.2, None, 0.75)
S.arrow(ANG[-4], ANG[-1], TEXT, 1.2, 6.0, None, 0.75)

# --- the piece: back wall, hidden edges, blue body with hatching, front walls, visible edges ----
S.polygon(OUTER, TEXT, 0.07)
for run in (arc_pts(R1, Z0, T0, T1), [C, E], [E, H]):
    S.line(run, TEXT, 0.9, "3 2.5", 0.45)
S.polygon(SIDE0, THEORY, 0.20)
S.polygon(TOP, THEORY, 0.12)
S.polygon(INNER, THEORY, 0.10)
S.polygon(INNER, TEXT, 0.07)
hatch([[px(q) for q in face] for face in FRONT], THEORY)
for run in ([B, F], arc_pts(R1, Z1, T0, T1), [H, G], [G, C], [D, F], arc_pts(R0, Z1, T0, T1)):
    S.line(run, TEXT, 1.0, None, 0.65)

# --- the three edges from the corner, and the corner itself ----------------------------------
S.line([A, B], TEXT, 2.8)
S.line(arc_pts(R0, Z0, T0, T1), BASE, 2.8)
S.line([A, D], PRACTICE, 2.8)
S.point(A, TEXT, 3.4)

# --- labels ----------------------------------------------------------------------------------
at(vscale(0.33, A), it("r") + " = 2", -3, -6, TEXT, 11, "end")
at(cyl(1.2, math.radians(14), 0), it(TH) + " = " + PI_S + "/6", 0, 4, TEXT, 11, "middle")
at(cyl(2.25, T0, 0), it("dr") + " = 1/2", 4, 14, TEXT, 11.5, "start", 600)
at(cyl(R1, T0, 0.3), it("dz") + " = 3/5", 7, 4, PRACTICE, 11.5, "start", 600)
# the arc label sits a little above C: at C's own height its first line runs into the z = 1 tick
at(C, it("r") + " " + it("d" + TH) + " = 2 " + CDOT + " " + PI_S + "/12", -7, -7, BASE, 11, "end", 600)
at(C, APPROX + " 0,52", -7, 7, BASE, 11, "end", 600)

TX, TY = P.X(1.5), P.Y(2.28)
halo(TX, TY, it("r") + " " + it("dr") + " " + it("d" + TH) + " " + it("dz") + " = " + PI_S + "/20 "
     + APPROX + " 0,157", TEXT, 11.5, "middle")
halo(TX, TY + 18, "gerçek hacim 9" + PI_S + "/160 " + APPROX + " 0,177", THEORY, 11.5, "middle", 600)

OUT["dform-silindirik-hacim-parcasi"] = figure(
    420, 300, [P],
    "Mavi taralı küçük parça, <em>r</em> = 2 ve <em>r</em> = 2,5 silindirleri (gri), "
    "<em>&#977;</em> = &#960;/6 ve <em>&#977;</em> = &#960;/4 yarım düzlemleri ile <em>z</em> = 0 ve "
    "<em>z</em> = 0,6 düzlemleri arasında kalır; köşesi (<em>r</em>, <em>&#977;</em>, <em>z</em>) = "
    "(2, &#960;/6, 0) noktasıdır. Bu köşeden çıkan üç kenar parçayı yaklaşık bir kutu gibi ölçer: "
    "radyal kenar <em>dr</em> = 1/2, <em>r</em> = 2 çemberi üzerindeki yay <em>r</em> "
    "<em>d&#977;</em> = 2 &#183; &#960;/12 &#8776; 0,52 ve dikey kenar <em>dz</em> = 3/5. "
    "Yay kenarının boyu <em>d&#977;</em> değil <em>r</em> <em>d&#977;</em> olduğundan kutunun hacmi "
    "<em>r</em> <em>dr</em> <em>d&#977;</em> <em>dz</em> = &#960;/20 &#8776; 0,157 çıkar; parçanın "
    "gerçek hacmi ise 9&#960;/160 &#8776; 0,177'dir. Parça küçüldükçe iki değerin oranı 1'e yaklaşır.",
    aria="Silindirik koordinatlarda kucuk hacim parcasi, mavi tarali: r = 2 ile r = 2,5 silindirleri, "
         "theta = pi/6 ile theta = pi/4 yarim duzlemleri, z = 0 ile z = 0,6 duzlemleri arasi. "
         "Kose (r, theta, z) = (2, pi/6, 0), yani yaklasik (1,73; 1; 0). Koseden cikan kenarlar: "
         "dr = 1/2, r dtheta = 2 pi/12 yaklasik 0,52, dz = 3/5. Kesikli r dogrusu ve theta = pi/6 "
         "aci yayi. r dr dtheta dz = pi/20 yaklasik 0,157; gercek hacim 9 pi/160 yaklasik 0,177.",
)

# ============================================================ dform-yayilan-alan
# -*- coding: utf-8 -*-
# dform-yayilan-alan — the position field V = x U1 + y U2 + z U3 cut by the plane z = 0, i.e. the
# arrows x U1 + y U2 at the integer lattice -2..2, drawn at 0.4 of their true length. Colour encodes
# the length |V(a, b)| = sqrt(a^2 + b^2): every arrow is drawn in PRACTICE, longer classes are thicker
# and more opaque and are pushed from orange towards red with an sRGB hue-rotate filter (the device of
# dform-donen-alan), so no colour code is written and "orange -> red" holds in both themes. The origin,
# where V vanishes, is a red dot. A dashed blue square with corners (+-0.5, +-0.5) around the origin
# carries small outward flux arrows on its edges: the field leaves it through every side.
# Labels: "div V = 3" beside the square, "d eta = 3 dx wedge dy wedge dz" in the top-left corner.
# The wedge glyph is missing from the book font, so it is drawn as a small path between words that
# are each centred on their own estimated midpoint (width errors then do not accumulate).
import math

SHRINK = 0.4
XR, YR = (-3.1, 3.25), (-3.02, 3.55)
P = cplane(24, 22, 344, XR, YR)
PPU = 344 / (XR[1] - XR[0])                 # pixels per data unit
LMAX = 2 * math.sqrt(2)                     # longest field vector on the lattice, at (+-2, +-2)
MAX_HUE = -26.0                             # hue rotation of the longest arrows: orange -> red
FID = "dform-yayilan-alan-hue"              # filter ids must be unique on the page
CLASSES = (1, 2, 4, 5, 8)                   # squared lengths a^2 + b^2 met on the lattice


def ital(s):
    return '<tspan font-style="italic">' + s + '</tspan>'


def tip(a, b):
    """End point of the shortened arrow of V = (a, b) attached at (a, b)."""
    return (a + SHRINK * a, b + SHRINK * b)


# 1. faint integer grid over the lattice, then the axes with ticks
for k in range(-2, 3):
    P.line([(k, -2), (k, 2)], TEXT, 0.7, None, 0.13)
    P.line([(-2, k), (2, k)], TEXT, 0.7, None, 0.13)

tick_fmt = lambda v: (MINUS_S + str(-v)) if v < 0 else str(v)
P.origin_axes("x", "y", xticks=(-2, -1, 1, 2), yticks=(-2, -1, 1, 2), xfmt=tick_fmt, yfmt=tick_fmt)

# 2. the square with corners (+-0.5, +-0.5): light fill and dashed outline
H = 0.5
P.polygon([(-H, -H), (H, -H), (H, H), (-H, H)], THEORY, 0.08, "none")
P.line([(-H, -H), (H, -H), (H, H), (-H, H), (-H, -H)], THEORY, 1.6, "5 3.5", 1.0)

# 3. lattice arrows, grouped by length class: one hue rotation and one group opacity per class
def strength(n2):
    """0 for length 1, 1 for the longest length 2*sqrt(2)."""
    return (math.sqrt(n2) - 1) / (LMAX - 1)


defs = ['<defs>']
for n2 in CLASSES[1:]:
    defs.append(f'<filter id="{FID}-{n2}" color-interpolation-filters="sRGB">'
                f'<feColorMatrix type="hueRotate" values="{MAX_HUE * strength(n2):.1f}"/></filter>')
defs.append('</defs>')
P.add("".join(defs))

cells = [(a, b) for a in range(-2, 3) for b in range(-2, 3) if (a, b) != (0, 0)]
style = {n2: (1.35 + 1.05 * strength(n2), 7 + 2 * strength(n2), 0.55 + 0.45 * strength(n2))
         for n2 in CLASSES}                          # shaft width, head size, group opacity
# opaque page-coloured copies first: the tint then mixes with the page, not with the axis beneath
for a, b in cells:
    w, hd, _ = style[a * a + b * b]
    P.arrow((a, b), tip(a, b), BG, w + 0.6, head=hd)
for n2 in CLASSES:
    w, hd, op = style[n2]
    filt = f' filter="url(#{FID}-{n2})"' if n2 != 1 else ""
    # opacity on the group, not on shaft and head: they overlap and would darken where they meet
    P.add(f'<g{filt} opacity="{op:.2f}">')
    for a, b in cells:
        if a * a + b * b == n2:
            P.arrow((a, b), tip(a, b), PRACTICE, w, head=hd)
    P.add('</g>')
for a, b in cells:
    dot(P, (a, b), TEXT, 1.9)

# 4. outward flux arrows on the four edges (two per edge, clear of the axes)
FL = 0.25
for s in (-0.25, 0.25):
    P.arrow((H, s), (H + FL, s), THEORY, 1.5, head=6)
    P.arrow((-H, s), (-H - FL, s), THEORY, 1.5, head=6)
    P.arrow((s, H), (s, H + FL), THEORY, 1.5, head=6)
    P.arrow((s, -H), (s, -H - FL), THEORY, 1.5, head=6)

# 5. the origin, where V vanishes: a red dot (the reddest hue) on a page-coloured ring; the ring is
# drawn unfiltered so the filter region of the lone circle cannot clip it
P.add(f'<circle cx="{P.X(0):.1f}" cy="{P.Y(0):.1f}" r="4.8" fill="{BG}"/>')
P.add(f'<g filter="url(#{FID}-8)"><circle cx="{P.X(0):.1f}" cy="{P.Y(0):.1f}" r="4.0" '
      f'fill="{PRACTICE}"/></g>')


# 6. labels
def halo(px, py, s, color=TEXT, size=11.5, anchor="start"):
    P.add(f'<text x="{px:.1f}" y="{py:.1f}" fill="{color}" font-size="{size}" text-anchor="{anchor}" '
          f'stroke="{BG}" stroke-width="3.2" stroke-linejoin="round" paint-order="stroke">{s}</text>')


halo(P.X(0.92), P.Y(0.40), "div " + ital("V") + " = 3", THEORY, 11.5, "start")


def wedge_formula(px, py, size=11.5, color=TEXT):
    """d eta = 3 dx ^ dy ^ dz starting at pixel px on baseline py; the wedges are drawn paths."""
    em = size
    # widths sit between Source Sans Pro / Lato (the site) and the serif of the preview raster
    space, thin, op_gap = 0.30 * em, 0.22 * em, 0.25 * em
    wedge_w = 0.50 * em
    items = [("t", ital("d&#951;"), 1.05 * em), ("g", space), ("t", "=", 0.55 * em), ("g", space),
             ("t", "3", 0.52 * em), ("g", thin), ("t", ital("dx"), 1.00 * em), ("g", op_gap),
             ("w", wedge_w), ("g", op_gap), ("t", ital("dy"), 1.00 * em), ("g", op_gap),
             ("w", wedge_w), ("g", op_gap), ("t", ital("dz"), 0.95 * em)]
    x = px
    for it in items:
        if it[0] == "g":
            x += it[1]
        elif it[0] == "t":
            _, s, w = it
            P.add(f'<text x="{x + w / 2:.1f}" y="{py:.1f}" fill="{color}" font-size="{size}" '
                  f'text-anchor="middle">{s}</text>')
            x += w
        else:
            w = it[1]
            cx, hw, h = x + w / 2, 0.24 * em, 0.56 * em
            P.add(f'<path d="M{cx - hw:.1f},{py - 0.3:.1f} L{cx:.1f},{py - h:.1f} L{cx + hw:.1f},{py - 0.3:.1f}" '
                  f'fill="none" stroke="{color}" stroke-width="0.9" stroke-linejoin="round" '
                  f'stroke-linecap="round"/>')
            x += w
    return x


wedge_formula(P.X(-3.0), P.Y(3.12))

OUT["dform-yayilan-alan"] = figure(
    400, 380, [P],
    "Konum alanı <em>V</em> = <em>x</em> <em>U</em><sub>1</sub> + <em>y</em> <em>U</em><sub>2</sub> + "
    "<em>z</em> <em>U</em><sub>3</sub>&#8217;ün <em>z</em> = 0 düzlemindeki kesiti: &#8722;2..2 tam sayı "
    "ızgarasının her noktasındaki ok, o noktanın konum vektörünü okunaklılık için gerçek uzunluğunun "
    "0,4 katıyla gösterir. Oklar, alanın sıfır olduğu başlangıç noktasından (kırmızı nokta) uzaklaştıkça "
    "uzar ve turuncudan kırmızıya döner. Köşeleri (&#177;0,5; &#177;0,5) olan kesikli mavi karenin her "
    "kenarında alan dışarı doğru akar, içeri aktığı hiçbir yer yoktur; diverjansın ölçtüğü yayılma budur. "
    "Düzlemdeki oklar diverjansa 1 + 1 katkısını verir, üçüncü 1 düzleme dik <em>z</em> yönündeki "
    "yayılmadan gelir; böylece div <em>V</em> = 3 olur.",
    aria="Konum alani V = x U1 + y U2 + z U3 un z = 0 duzlemindeki kesiti: -2..2 tam sayi izgarasinda "
         "disari bakan oklar, 0,4 katiyla kisaltilmis, uzadikca turuncudan kirmiziya donuyor; baslangic "
         "noktasinda kirmizi nokta; baslangic noktasi merkezli, koseleri (+-0,5; +-0,5) olan kesikli mavi "
         "kare ve kenarlarinda disari akis oklari; etiketler div V = 3 ve d eta = 3 dx wedge dy wedge dz",
)

# ============================================================ donusum-cemberi-iki-kez-sarar
# -*- coding: utf-8 -*-
# donusum-cemberi-iki-kez-sarar — F(u, v) = (u^2 - v^2, 2uv) wraps the plane twice around itself (2D).
# Left panel, uv plane [-2.5, 2.5]^2: unit circle (thin grey) and the circle r = 2 (thick blue) that
#   alpha(t) = (2 cos t, 2 sin t) traverses once counter-clockwise; points at t = 0, pi/4, pi/2, pi, 3pi/2:
#   (2, 0), (1.41, 1.41), (0, 2), (-2, 0), (0, -2).
# Right panel, xy plane [-4.5, 4.5]^2: r^2 = 1 (thin grey) and r^2 = 4 (thick blue); beta(t) = (4 cos 2t,
#   4 sin 2t) goes round twice, the second turn is drawn as a thin concentric circle just inside.
#   Images: (4, 0) for t = 0 and t = pi, (-4, 0) for t = pi/2 and t = 3pi/2, (0, 4) for t = pi/4.
# The book palette has no five distinct point hues, so colour marks the antipodal pair p, -p (same
# image point): filled dot = t, ring = t + pi. On the right the two marks sit one inside the other,
# and each ring is wide enough to cover both turns where they pass through the point.
import math

R_A, R_B = 2.0, 4.0            # radius of alpha's circle and of its image circle
INNER = 3.72                   # radius at which beta's second turn is drawn (about 7 px inside)
LX, RX, TOP, PW = 24, 316, 26, 220
ARROW_Y = 104                  # height of the F arrow between the panels (pixels)

pa = cplane(LX, TOP, PW, (-2.5, 2.5), (-2.5, 2.5))    # 44 px per unit
pb = cplane(RX, TOP, PW, (-4.5, 4.5), (-4.5, 4.5))    # 24.4 px per unit

T_EQ = '<tspan font-style="italic">t</tspan> = '


def ital(s):
    return f'<tspan font-style="italic">{s}</tspan>'


def halo(p, x, y, s, dx=0, dy=0, color=TEXT, size=11, anchor="start"):
    """Label at a data point with a page-coloured halo."""
    p.add(f'<text x="{p.X(x) + dx:.1f}" y="{p.Y(y) + dy:.1f}" fill="{color}" font-size="{size}" '
          f'text-anchor="{anchor}" stroke="{BG}" stroke-width="3.2" stroke-linejoin="round" '
          f'paint-order="stroke">{s}</text>')


def round_path(p, r, color, width, opacity=1.0):
    """Circle about the origin as a polyline (so the text-hit checker sees its stroke)."""
    p.line(circle_pts(0, 0, r, samples=240), color, width, None, opacity)


def along(p, rho, deg, color, width, head, span=7.5):
    """Counter-clockwise arrowhead sitting on the circle of radius rho at angle deg."""
    p.arrow(polar(rho, math.radians(deg - span)), polar(rho, math.radians(deg)), color, width, head)


def filled(p, z, color):
    dot(p, z, BG, 5.4)
    dot(p, z, color, 3.6)


def ringed(p, z, color, r=6.4):
    p.add(f'<circle cx="{p.X(z[0]):.1f}" cy="{p.Y(z[1]):.1f}" r="{r}" fill="{BG}" '
          f'stroke="{color}" stroke-width="1.8"/>')


def doubled(p, z, color):
    """Ring (moment t + pi) with the filled dot (moment t) inside: two moments, one image point."""
    ringed(p, z, color, 6.4)
    dot(p, z, color, 3.2)


# ---- left: the uv plane ------------------------------------------------------------------------
pa.origin_axes("u", "v")
round_path(pa, 1.0, TEXT, 1.1, 0.45)
guide(pa, [(0, 0), polar(R_A, 5 * PI / 4)], TEXT, 0.45)
round_path(pa, R_A, THEORY, 2.4)
along(pa, R_A, 135, THEORY, 2.4, 10)
along(pa, R_A, 315, THEORY, 2.4, 10)

dot(pa, (0, 0), TEXT, 2.6)
filled(pa, (2, 0), PRACTICE)                                   # t = 0
filled(pa, (math.sqrt(2), math.sqrt(2)), TEXT)                 # t = pi/4
filled(pa, (0, 2), BASE)                                       # t = pi/2
ringed(pa, (-2, 0), PRACTICE)                                  # t = pi
ringed(pa, (0, -2), BASE)                                      # t = 3pi/2

halo(pa, 2, 0, T_EQ + "0", -10, -8, PRACTICE, 11, "end")
halo(pa, math.sqrt(2), math.sqrt(2), T_EQ + PI_S + "/4", 8, -7, TEXT, 11, "start")
halo(pa, 0, 2, T_EQ + PI_S + "/2", -8, -7, BASE, 11, "end")
halo(pa, -2, 0, T_EQ + PI_S, 11, -8, PRACTICE, 11, "start")
halo(pa, 0, -2, T_EQ + "3" + PI_S + "/2", 9, 17, BASE, 11, "start")
halo(pa, *polar(2.36, math.radians(150)), ital("&#945;"), 0, 4, THEORY, 13, "middle")
halo(pa, *polar(2.28, math.radians(225)), ital("r") + " = 2", -2, 10, THEORY, 11.5, "end")

# ---- the arrow F between the panels (pixel coordinates) ----------------------------------------
x0, x1, hd = LX + PW + 16, RX - 14, 8.5
pa.add(f'<line x1="{x0:.1f}" y1="{ARROW_Y}" x2="{x1 - hd * 0.8:.1f}" y2="{ARROW_Y}" stroke="{TEXT}" '
       f'stroke-width="1.6" stroke-linecap="round"/>')
pa.add(f'<polygon points="{x1:.1f},{ARROW_Y} {x1 - hd:.1f},{ARROW_Y - hd * 0.42:.1f} '
       f'{x1 - hd:.1f},{ARROW_Y + hd * 0.42:.1f}" fill="{TEXT}"/>')
pa.text_px((x0 + x1) / 2, ARROW_Y - 8, "F", TEXT, 13, "middle", False, True)

# ---- right: the xy plane -----------------------------------------------------------------------
pb.origin_axes("x", "y")
round_path(pb, 1.0, TEXT, 1.1, 0.45)
guide(pb, [(0, 0), polar(R_B, 5 * PI / 4)], TEXT, 0.45)
round_path(pb, R_B, THEORY, 2.4)       # first turn, 0 <= t <= pi
round_path(pb, INNER, THEORY, 1.3)     # second turn, pi <= t <= 2pi, drawn just inside
along(pb, R_B, 135, THEORY, 2.4, 10)
along(pb, R_B, 290, THEORY, 2.4, 10)
along(pb, INNER, 45, THEORY, 1.3, 8)
along(pb, INNER, 250, THEORY, 1.3, 8)

dot(pb, (0, 0), TEXT, 2.6)
doubled(pb, (4, 0), PRACTICE)                                  # t = 0 and t = pi
doubled(pb, (-4, 0), BASE)                                     # t = pi/2 and t = 3pi/2
filled(pb, (0, 4), TEXT)                                       # t = pi/4

halo(pb, 4, 0, T_EQ + "0", -15, -8, PRACTICE, 11, "end")
halo(pb, 4, 0, T_EQ + PI_S, -15, 18, PRACTICE, 11, "end")
halo(pb, -4, 0, T_EQ + PI_S + "/2", 15, -8, BASE, 11, "start")
halo(pb, -4, 0, T_EQ + "3" + PI_S + "/2", 15, 18, BASE, 11, "start")
halo(pb, 0, 4, T_EQ + PI_S + "/4", -14, -8, TEXT, 11, "end")   # clear of the y arrowhead
halo(pb, *polar(4.5, math.radians(150)), ital("&#946;"), 0, 4, THEORY, 13, "middle")
halo(pb, *polar(4.32, math.radians(225)), ital("r") + sups("2") + " = 4", -2, 10, THEORY, 11.5, "end")
halo(pb, 0, 0, ital("F") + "(0, 0) = (0, 0)", 6, 38, TEXT, 10.5, "start")

OUT["donusum-cemberi-iki-kez-sarar"] = figure(
    560, 272, [pa, pb],
    "Solda <em>r</em> = 2 yarıçaplı çemberi saat yönünün tersine bir kez dolaşan "
    "&#945;(<em>t</em>) = (2 cos <em>t</em>, 2 sin <em>t</em>) eğrisi, sağda onun "
    "<em>F</em>(<em>u</em>, <em>v</em>) = (<em>u</em><sup>2</sup> &#8722; <em>v</em><sup>2</sup>, 2<em>uv</em>) "
    "altındaki görüntüsü &#946;(<em>t</em>) = (4 cos 2<em>t</em>, 4 sin 2<em>t</em>) görülüyor. "
    "&#946; ise yarıçapı <em>r</em><sup>2</sup> = 4 olan çemberi iki kez dolaşır; ikinci tur, seçilebilsin "
    "diye kalın çemberin hemen içine ince çizgiyle çizilmiştir. "
    "Aynı renkteki dolu nokta <em>t</em>, halka <em>t</em> + &#960; anını gösterir: bu iki an birbirinin "
    "tam karşısındaki <strong>p</strong> ve &#8722;<strong>p</strong> noktalarını verir ve "
    "<em>F</em>(&#8722;<strong>p</strong>) = <em>F</em>(<strong>p</strong>) olduğundan sağda aynı noktaya düşer. "
    "Gri birim çember kendi üzerine gider, başlangıç noktası ise yerinde kalır.",
    css_class=WIDE,
    aria="Iki panel. Solda uv duzleminde merkezi baslangic noktasinda r = 1 gri ve r = 2 kalin mavi "
         "cemberleri; alpha bu cemberi saat yonunun tersine bir kez dolasir. Noktalar: t = 0 icin (2, 0), "
         "t = pi/4 icin (1,41; 1,41), t = pi/2 icin (0, 2), t = pi icin (-2, 0), t = 3pi/2 icin (0, -2); "
         "karsilikli noktalar ayni renkte. Aradaki ok F. Sagda xy duzleminde r^2 = 1 gri ve r^2 = 4 mavi "
         "cemberleri; beta cemberi iki kez dolasir, ikinci tur icte ince cizgi, dort yon oku. (4, 0) "
         "noktasinda t = 0 ve t = pi, (-4, 0) noktasinda t = pi/2 ve t = 3pi/2, (0, 4) noktasinda "
         "t = pi/4. F(0, 0) = (0, 0)",
)

# ============================================================ donusum-jacobi-sutunlari
# -*- coding: utf-8 -*-
# donusum-jacobi-sutunlari: F(u, v) = (u + v, uv) at p = (1, 2), J_F(p) = [[1, 1], [2, 1]].
# Left, the (u, v) plane: U1(p) = (1, 0)_p, U2(p) = (0, 1)_p and the square with corners
# (1, 2), (1.5, 2), (1.5, 2.5), (1, 2.5). Right, the (x, y) plane: F(p) = (3, 2), the images
# F_*(U1(p)) = (1, 2) and F_*(U2(p)) = (1, 1), the true image of the square (straight-edged
# quadrilateral (3, 2), (3.5, 3), (4, 3.75), (3.5, 2.5)) and the parallelogram spanned by the
# half arrows ((3, 2), (3.5, 3), (4, 3.5), (3.5, 2.5)); the 0.25 gap sits between the fourth corners.
# Colour convention for this figure: U1 and its image -> THEORY, U2 and its image -> BASE, the
# same colours mark the two columns of the matrix; the tangent-map parallelogram -> PRACTICE.
# The palette has no red token, so the points and the gap marker are TEXT.
# Both panels share one scale (PPU pixels per unit), so the two shaded regions compare directly.
import math

PPU = 80
TOP = 26
RIGHT_H = 3.0 * PPU                      # the right panel is the taller one
LEFT_X0 = 34
GAP = 150                                # left panel end -> right panel start

pl = Plot(LEFT_X0, TOP + (RIGHT_H - 1.7 * PPU) / 2, 1.7 * PPU, 1.7 * PPU, (0.5, 2.2), (1.5, 3.2))
pr = Plot(LEFT_X0 + 1.7 * PPU + GAP, TOP, 2.5 * PPU, RIGHT_H, (2.5, 5.0), (1.5, 4.5))


def ital(s):
    return f'<tspan font-style="italic">{s}</tspan>'


def halo(pl_, x, y, s, dx=0, dy=0, color=TEXT, size=11.5, anchor="start"):
    """Label at a data point with a page-coloured halo, so grid lines behind it break."""
    pl_.add(f'<text x="{pl_.X(x) + dx:.1f}" y="{pl_.Y(y) + dy:.1f}" fill="{color}" font-size="{size}" '
            f'text-anchor="{anchor}" stroke="{BG}" stroke-width="3.2" stroke-linejoin="round" '
            f'paint-order="stroke">{s}</text>')


def px_arrow(pl_, x0, y0, x1, y1, color, width, head):
    """Arrow between two pixel positions (used for the map F between the panels)."""
    L = math.hypot(x1 - x0, y1 - y0)
    ux, uy = (x1 - x0) / L, (y1 - y0) / L
    px, py, hw = -uy, ux, head * 0.42
    sx, sy = x1 - ux * head * 0.8, y1 - uy * head * 0.8
    pl_.add(f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{sx:.1f}" y2="{sy:.1f}" stroke="{color}" '
            f'stroke-width="{width}" stroke-linecap="round"/>')
    pl_.add(f'<polygon points="{x1:.1f},{y1:.1f} {x1 - ux * head + px * hw:.1f},{y1 - uy * head + py * hw:.1f} '
            f'{x1 - ux * head - px * hw:.1f},{y1 - uy * head - py * hw:.1f}" fill="{color}"/>')


def U(k):
    return ital("U") + subs(k)


def Fstar(k):
    return ital("F") + subs("*") + "(" + ital("U") + subs(k) + ")"


# ---- left: the (u, v) plane -----------------------------------------------------------------
p = (1.0, 2.0)
square = [(1.0, 2.0), (1.5, 2.0), (1.5, 2.5), (1.0, 2.5)]

pl.grid((1, 1.5, 2), (2, 2.5, 3))
pl.axes((1, 1.5, 2), (2, 2.5, 3), "u", "v", xfmt=tfmt, yfmt=tfmt)
pl.polygon(square, TEXT, 0.13, "none")
pl.line(square + square[:1], TEXT, 1.1, None, 0.5)
pl.arrow(p, (2.0, 2.0), THEORY, 2.4, head=9)
pl.arrow(p, (1.0, 3.0), BASE, 2.4, head=9)
dot(pl, p, TEXT, 3.6)

halo(pl, 1.72, 2.0, U("1"), 0, -8, THEORY, 12, "middle")
halo(pl, 1.0, 2.75, U("2"), -8, 4, BASE, 12, "end")
halo(pl, 1.0, 2.0, bold("p") + " = (1, 2)", -3, 17, TEXT, 11, "start")

# ---- right: the (x, y) plane ----------------------------------------------------------------
Fp = (3.0, 2.0)
image = [(3.0, 2.0), (3.5, 3.0), (4.0, 3.75), (3.5, 2.5)]       # F of the square's corners
approx = [(3.0, 2.0), (3.5, 3.0), (4.0, 3.5), (3.5, 2.5)]       # F(p) + half arrows

pr.grid((3, 3.5, 4, 4.5), (2, 2.5, 3, 3.5, 4))
pr.axes((3, 3.5, 4, 4.5), (2, 2.5, 3, 3.5, 4), "x", "y", xfmt=tfmt, yfmt=tfmt)
pr.polygon(image, TEXT, 0.13, "none")
pr.line(image + image[:1], TEXT, 1.1, None, 0.5)
pr.line(approx + approx[:1], PRACTICE, 1.7, "5 3", 0.95)
pr.arrow(Fp, (4.0, 4.0), THEORY, 2.4, head=9)
pr.arrow(Fp, (4.0, 3.0), BASE, 2.4, head=9)

# the gap between the fourth corners, with short caps
gx = pr.X(4.0)
for yy in (3.5, 3.75):
    pr.add(f'<line x1="{gx - 2.5:.1f}" y1="{pr.Y(yy):.1f}" x2="{gx + 3.0:.1f}" y2="{pr.Y(yy):.1f}" '
           f'stroke="{TEXT}" stroke-width="1.2"/>')
pr.line([(4.0, 3.5), (4.0, 3.75)], TEXT, 1.8)
dot(pr, Fp, TEXT, 3.6)

halo(pr, 4.0, 3.625, "0,25", 8, 4, TEXT, 10.5, "start")
halo(pr, 3.0, 2.0, ital("F") + "(" + bold("p") + ") = (3, 2)", -4, 17, TEXT, 11, "start")
halo(pr, 4.0, 4.0, Fstar("1") + " = (1, 2)", -14, 0, THEORY, 11, "end")
halo(pr, 3.675, 2.325, Fstar("2") + " = (1, 1)", 0, 0, BASE, 11, "start")

# ---- between the panels: the map F and its Jacobian matrix at p ------------------------------
left_end = pl.x0 + pl.w
gap_c = (left_end + 20 + pr.x0 - 26) / 2
ay = TOP + RIGHT_H / 2 - 8
px_arrow(pr, gap_c - 40, ay, gap_c + 40, ay, TEXT, 1.6, 9)
pr.text_px(gap_c, ay - 8, "F", TEXT, 13, "middle", False, True)

cy = ay + 30                               # vertical centre of the matrix block
r1, r2 = cy - 3.5, cy + 11.5               # row baselines
top, bot = r1 - 10, r2 + 4
mx0 = gap_c + 2                            # left parenthesis
c1, c2 = mx0 + 11, mx0 + 29                # column centres
# dx on the parenthesis: the italic subscript F otherwise leans into "("
pr.text_px(mx0 - 4, cy + 4, ital("J") + subs(ital("F")) + '<tspan dx="1.6">(</tspan>' + bold("p") + ") =",
           TEXT, 11.5, "end")
for x_, sgn in ((mx0 + 4, -1), (mx0 + 36, 1)):
    pr.add(f'<path d="M{x_:.1f},{top:.1f} Q{x_ + sgn * 6:.1f},{(top + bot) / 2:.1f} {x_:.1f},{bot:.1f}" '
           f'fill="none" stroke="{TEXT}" stroke-width="1.2"/>')
for (row, a, b) in ((r1, "1", "1"), (r2, "2", "1")):
    pr.text_px(c1, row, a, THEORY, 11.5, "middle")
    pr.text_px(c2, row, b, BASE, 11.5, "middle")

OUT["donusum-jacobi-sutunlari"] = figure(
    int(pr.x0 + pr.w + 36), int(TOP + RIGHT_H + 30), [pl, pr],
    "<em>F</em>(<em>u</em>, <em>v</em>) = (<em>u</em> + <em>v</em>, <em>uv</em>) altında "
    "<em>U</em><sub>1</sub>(<strong>p</strong>) ve <em>U</em><sub>2</sub>(<strong>p</strong>) oklarının "
    "görüntüleri, <strong>p</strong> = (1, 2)&#8217;deki Jacobi matrisinin sütunları olan (1, 2) ve "
    "(1, 1)&#8217;dir; aynı renk bir oku, görüntüsünü ve matristeki sütununu birbirine bağlar. "
    "Soldaki küçük karenin gerçek görüntüsü sağdaki gri dörtgendir; turuncu kesikli paralelkenar ise "
    "iki görüntü okunun yarısıyla kurulan, teğet dönüşümünün önerdiği şekildir. Üç köşe tam uyar; "
    "dördüncü köşedeki 0,25&#8217;lik fark, kenar uzunluklarının çarpımı 0,5 &#183; 0,5&#8217;tir, "
    "yani ikinci mertebeden bir hatadır.",
    css_class=WIDE,
    aria="Iki panel ayni olcekte. Solda uv duzleminde p = (1, 2), mavi U1 oku (1, 0), yesil U2 oku "
         "(0, 1) ve koseleri (1, 2), (1,5; 2), (1,5; 2,5), (1; 2,5) olan gri kare. Aradaki F oku ve "
         "J_F(p) = [[1, 1], [2, 1]]. Sagda xy duzleminde F(p) = (3, 2), mavi F*(U1) = (1, 2) ve yesil "
         "F*(U2) = (1, 1) oklari; karenin gercek goruntusu koseleri (3, 2), (3,5; 3), (4; 3,75), "
         "(3,5; 2,5) olan gri dortgen; oklarin yarisiyla kurulan, koseleri (3, 2), (3,5; 3), (4; 3,5), "
         "(3,5; 2,5) olan turuncu kesikli paralelkenar; (4; 3,5) ile (4; 3,75) arasinda 0,25 fark.",
)

# ============================================================ donusum-kup-ve-tersi
# -*- coding: utf-8 -*-
# donusum-kup-ve-tersi: F(x) = x^3 is one-to-one and onto, but its inverse cbrt is not differentiable
# at 0. Window [-2, 2] x [-2, 2] at equal scale: y = x^3 (THEORY, x in [-1.26, 1.26]), its mirror
# image y = cbrt(x) (PRACTICE, x in [-2, 2]) and the dashed grey mirror line y = x.
# At the origin the horizontal tangent of x^3 (slope 0, lies on the x axis) becomes the vertical
# tangent of cbrt(x) (lies on the y axis). The graphs meet at (0, 0), (1, 1) and (-1, -1); only the
# last two get dots, the origin is already marked by the two tangent pieces. The mirror pair
# A = (0.5, 0.125) on the cube and B = (0.125, 0.5) on the cube root, joined by a dashed segment
# that crosses y = x at right angles in (0.3125, 0.3125).
# The palette has no red token, so the cube-root graph is PRACTICE (orange).
# Both graphs come from one parameter list, (t, t^3) and (t^3, t), so they are exact mirror images.
# The second and fourth quadrants are empty: the two tangent notes sit there, mirrored in y = x.
# The figure font has no cube-root glyph (U+221B renders as a missing-glyph box), so the radical
# in the label is a path and the caption says "kup kok" in words.
import math

XR, YR = (-2.3, 2.85), (-2.3, 2.45)   # extra room on the right and on top for the curve-end labels
P = cplane(18, 22, 364, XR, YR)
X_CUBE = 2 ** (1 / 3)                  # 1.26: y = x^3 reaches the window edge y = 2 there
TAN = 0.75                             # half length of the two tangent pieces
A, B = (0.5, 0.125), (0.125, 0.5)      # mirror pair
M = (0.3125, 0.3125)                   # where segment AB meets y = x


def ital(s):
    return f'<tspan font-style="italic">{s}</tspan>'


def mfmt(v):
    """Tick label with a real minus sign."""
    return fmt(v).replace("-", MINUS_S)


def halo(x, y, s, dx=0, dy=0, color=TEXT, size=11.5, anchor="start"):
    """Label at a data point with a page-coloured halo, so dashed lines behind it break."""
    P.add(f'<text x="{P.X(x) + dx:.1f}" y="{P.Y(y) + dy:.1f}" fill="{color}" font-size="{size}" '
          f'text-anchor="{anchor}" stroke="{BG}" stroke-width="3.2" stroke-linejoin="round" '
          f'paint-order="stroke">{s}</text>')


def cube_root_label(x, y, dx, dy, color, size=12):
    """'y = cube root of x' built from pieces. 'y =' ends at a fixed pixel and the x is centred under
    the bar, so the radical lines up whatever the width of the font."""
    x0, yb = P.X(x) + dx, P.Y(y) + dy
    P.add(f'<text x="{x0 + 17:.1f}" y="{yb:.1f}" fill="{color}" font-size="{size}" '
          f'text-anchor="end">{ital("y")} =</text>')
    r, top = x0 + 21, yb - 10.5          # left end of the radical, height of its bar
    # the hook sits a little low and the index a little high, so the 3 does not touch the hook
    P.add(f'<path d="M{r:.1f},{yb - 3.6:.1f} L{r + 2.2:.1f},{yb - 5.0:.1f} L{r + 5:.1f},{yb + 0.8:.1f} '
          f'L{r + 9:.1f},{top:.1f} H{r + 18:.1f}" fill="none" stroke="{color}" stroke-width="1.1" '
          f'stroke-linejoin="round" stroke-linecap="round"/>')
    P.add(f'<text x="{r + 1.8:.1f}" y="{yb - 7.6:.1f}" fill="{color}" font-size="7.5" '
          f'text-anchor="middle">3</text>')
    P.add(f'<text x="{r + 13.5:.1f}" y="{yb:.1f}" fill="{color}" font-size="{size}" '
          f'text-anchor="middle" font-style="italic">x</text>')


# 1. mirror line y = x, then the axes
P.line([(-2.0, -2.0), (2.0, 2.0)], TEXT, 1.1, "5 4", 0.55)
P.origin_axes("x", "y", xticks=(-2, -1, 1, 2), yticks=(-2, -1, 1, 2), xfmt=mfmt, yfmt=mfmt)

# 2. the two graphs
N = 320
ts = [-X_CUBE + 2 * X_CUBE * k / N for k in range(N + 1)]
P.line([(t, t ** 3) for t in ts], THEORY, 2.3)
P.line([(t ** 3, t) for t in ts], PRACTICE, 2.3)

# 3. tangents at the origin: horizontal for the cube, vertical for the cube root
P.line([(-TAN, 0.0), (TAN, 0.0)], THEORY, 2.2, "5 3.5", 0.95)
P.line([(0.0, -TAN), (0.0, TAN)], PRACTICE, 2.2, "5 3.5", 0.95)

# 4. the mirror pair, the dashed segment between them and its right angle with y = x
P.line([A, B], TEXT, 1.1, "3 2.5", 0.8)
s = 0.075 / math.sqrt(2)
u, n = (s, s), (-s, s)                 # along y = x, and along AB towards B
P.line([(M[0] + u[0], M[1] + u[1]), (M[0] + u[0] + n[0], M[1] + u[1] + n[1]),
        (M[0] + n[0], M[1] + n[1])], TEXT, 0.9, None, 0.75)

# 5. points: common points black and ringed, the mirror pair small
for Q in ((1.0, 1.0), (-1.0, -1.0)):
    dot(P, Q, BG, 5.4)
    dot(P, Q, TEXT, 3.6)
for Q in (A, B):
    dot(P, Q, BG, 4.2)
    dot(P, Q, TEXT, 2.7)

# 6. labels
X_, Y_ = ital("x"), ital("y")
halo(X_CUBE, 2.0, Y_ + " = " + X_ + sups("3"), 0, -9, THEORY, 12, "middle")
cube_root_label(2.0, X_CUBE, 7, 4, PRACTICE)
halo(2.0, 2.0, Y_ + " = " + X_, 6, 2, TEXT, 11.5, "start")
halo(-0.4, 0.0, "eğim 0", 0, -10, THEORY, 10.5, "middle")
halo(0.0, -0.5, "dikey teğet", 8, 4, PRACTICE, 10.5, "start")
halo(1.0, 1.0, "(1, 1)", -9, -7, TEXT, 10.5, "end")
halo(-1.0, -1.0, "(" + MINUS_S + "1, " + MINUS_S + "1)", 4, 22, TEXT, 10.5, "start")

OUT["donusum-kup-ve-tersi"] = figure(
    400, 370, [P],
    "<em>y</em> = <em>x</em><sup>3</sup> grafiği (mavi) ile tersi olan küp kök grafiği (turuncu), "
    "kesikli <em>y</em> = <em>x</em> doğrusuna göre birbirinin yansımasıdır: mavi eğri üzerindeki "
    "(0,5; 0,125) noktası, bu doğruya dik kesikli parça boyunca turuncu eğri üzerindeki (0,125; 0,5) "
    "noktasına gider. İki grafik (1, 1), (&#8722;1, &#8722;1) ve başlangıç noktasında kesişir; orada "
    "<em>x</em><sup>3</sup>&#8217;ün teğeti yataydır (eğim 0), yansıma ise bu teğeti dikey bir teğete "
    "çevirir. Dikey teğetin eğimi tanımsız olduğundan küp kök fonksiyonu "
    "0&#8217;da türevlenemez; <em>x</em><sup>3</sup> birebir ve örten olduğu hâlde bir difeomorfizma "
    "değildir.",
    aria="y = x^3 grafigi mavi, y = kup kok x grafigi turuncu, ikisi kesikli gri y = x dogrusuna gore "
         "simetrik; pencere -2 ile 2 arasi, esit olcek. Baslangic noktasinda x^3'un yatay teget parcasi "
         "(egim 0) ve kup kokun dikey teget parcasi. Ortak noktalar (0, 0), (1, 1) ve (-1, -1); mavi egri "
         "uzerinde (0,5; 0,125), turuncu egri uzerinde (0,125; 0,5) ve aralarinda y = x'e dik kesikli parca.",
)

# ============================================================ donusum-lineer-birim-noktalar
# -*- coding: utf-8 -*-
# donusum-lineer-birim-noktalar: the linear map F = (x - y, x + y, 2z) on R^3.
# Thin grey arrows u1, u2, u3 span the dashed unit cube; thick arrows F(u1) = (1, 1, 0) (THEORY),
# F(u2) = (-1, 1, 0) (BASE), F(u3) = (0, 0, 2) (PRACTICE) span its image, a translucent box with
# square base (0,0,0), (1,1,0), (0,2,0), (-1,1,0) and height 2. Two dashed floor arcs of radius 0.4
# mark the 45-degree turns u1 -> F(u1) and u2 -> F(u2). The point p = (2, 1, -1) and its image
# F(p) = (1, 3, -2) are joined by a thin dashed arrow; dashed drops tie both to the floor grid.
# Colour: the site palette has no red token, so p and F(p) are TEXT points (filled / hollow), the
# course convention for points. Every box vertex is computed as F(cube vertex), never typed in.
# Camera az = 20, el = 30 came out of a scan (_scan_donusum_lineer.py): el = 30 gives the u2 -> F(u2)
# arc the longest projection, az = 20 keeps F(u1) well away from the vertical and leaves the most
# room between the back corner F(u2) and the front vertical edge of the box.
import math

AZ, EL = 20.0, 30.0
P = space_panel(10, 10, 460, (-1.4, 3.85), (-3.05, 2.6))
S = Space(P, Camera(azimuth=AZ, elevation=EL, scale=1.0))
PPU = 460 / 5.25


def F(q):
    return (q[0] - q[1], q[0] + q[1], 2 * q[2])


O = (0.0, 0.0, 0.0)
U1, U2, U3 = (1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)
FU1, FU2, FU3 = F(U1), F(U2), F(U3)
p = (2.0, 1.0, -1.0)
Fp = F(p)
assert (FU1, FU2, FU3, Fp) == ((1, 1, 0), (-1, 1, 0), (0, 0, 2), (1, 3, -2))


def ital(s):
    return f'<tspan font-style="italic">{s}</tspan>'


def num(v):
    return MINUS_S + fmt(-v) if v < 0 else fmt(v)


def coords(q):
    return "(" + ", ".join(num(c) for c in q) + ")"


def px(Q):
    X, Y = S.pt(Q)
    return P.X(X), P.Y(Y)


def tag(Q, s, dx=0, dy=0, color=TEXT, size=11, anchor="start"):
    """Label at a space point with a page-coloured halo, so grid and edge lines behind it break."""
    x, y = px(Q)
    P.add(f'<text x="{x + dx:.1f}" y="{y + dy:.1f}" fill="{color}" font-size="{size}" '
          f'text-anchor="{anchor}" stroke="{BG}" stroke-width="3.2" stroke-linejoin="round" '
          f'paint-order="stroke">{s}</text>')


def arrow_px(a, b, color, width, head, dash=None, opacity=1.0, outline=False, shaft=True):
    """Arrow between page points. Shaft and head share one <g opacity>; the shaft is drawn from the
    head backwards so a full dash meets the head. outline=True rims the head with the page colour."""
    (x0, y0), (x1, y1) = a, b
    L = math.hypot(x1 - x0, y1 - y0)
    ux, uy = (x1 - x0) / L, (y1 - y0) / L
    nx, ny, hw = -uy, ux, head * 0.42
    sx, sy = x1 - ux * head * 0.85, y1 - uy * head * 0.85
    out = []
    if shaft:
        da = f' stroke-dasharray="{dash}"' if dash else ""
        out.append(f'<line x1="{sx:.1f}" y1="{sy:.1f}" x2="{x0:.1f}" y2="{y0:.1f}" stroke="{color}" '
                   f'stroke-width="{width}"{da} stroke-linecap="butt"/>')
    rim = f' stroke="{BG}" stroke-width="1.6" stroke-linejoin="round" paint-order="stroke"' if outline else ""
    out.append(f'<polygon points="{x1:.1f},{y1:.1f} {x1 - ux * head + nx * hw:.1f},{y1 - uy * head + ny * hw:.1f} '
               f'{x1 - ux * head - nx * hw:.1f},{y1 - uy * head - ny * hw:.1f}" fill="{color}"{rim}/>')
    P.add(f'<g opacity="{opacity}">' + "".join(out) + '</g>')


def arrow3(A, B, color, width, head, **kw):
    arrow_px(px(A), px(B), color, width, head, **kw)


# ---- unit cube and its image box ---------------------------------------------------------------
def face(axis, val):
    a, b = [t for t in range(3) if t != axis]
    quad = []
    for s, t in ((0, 0), (1, 0), (1, 1), (0, 1)):
        v = [0.0, 0.0, 0.0]
        v[axis], v[a], v[b] = val, s, t
        quad.append(tuple(v))
    return quad


CUBE_FACES = [face(ax, v) for ax in range(3) for v in (0, 1)]
CUBE_EDGES = [(c, vadd(c, e)) for c in [(i, j, k) for i in (0, 1) for j in (0, 1) for k in (0, 1)]
              for e in (U1, U2, U3) if vadd(c, e)[0] <= 1 and vadd(c, e)[1] <= 1 and vadd(c, e)[2] <= 1]
BOX_CENTER = F((0.5, 0.5, 0.5))


def front(quad_img):
    """True when the outward normal of an image face points toward the viewer."""
    n = vcross(vsub(quad_img[1], quad_img[0]), vsub(quad_img[3], quad_img[0]))
    mid = vscale(0.25, vadd(vadd(quad_img[0], quad_img[1]), vadd(quad_img[2], quad_img[3])))
    if vdot(n, vsub(mid, BOX_CENTER)) < 0:
        n = vscale(-1, n)
    return vdot(n, S.cam.d) > 0


BOX_FACES = [[F(v) for v in q] for q in CUBE_FACES]
FACE_FRONT = [front(q) for q in BOX_FACES]


def edge_hidden(e):
    adj = [i for i, q in enumerate(CUBE_FACES) if e[0] in q and e[1] in q]
    return not any(FACE_FRONT[i] for i in adj)


def at_origin(e):
    return O in e


# ---- 1. floor grid, back of the box, drops below the floor ---------------------------------------
S.floor_grid((-1, 2), (0, 3), n=3, opacity=0.10)

for q, fr in zip(BOX_FACES, FACE_FRONT):
    if not fr:
        S.polygon(q, THEORY, 0.07)
for e in CUBE_EDGES:
    if edge_hidden(e) and not at_origin(e):
        S.line([F(e[0]), F(e[1])], THEORY, 0.9, "4 3", 0.45)

for Q in (p, Fp):
    S.guide([(Q[0], Q[1], 0.0), Q], TEXT, 0.45)
    S.point((Q[0], Q[1], 0.0), TEXT, 1.9)

# ---- 2. axes and ticks --------------------------------------------------------------------------
S.axes(2.6, 3.6, 2.6, opacity=0.45)
S.ticks("x", (2,), offset=(-11, 3))       # left of the axis: the default offset sits on the steep x axis
S.ticks("y", (2, 3))

# ---- 3. dashed unit cube (edges through the origin are the arrows u1, u2, u3) ---------------------
for e in CUBE_EDGES:
    if not at_origin(e):
        S.line(list(e), TEXT, 1.0, "4 3", 0.5)

# ---- 4. front of the box ------------------------------------------------------------------------
for q, fr in zip(BOX_FACES, FACE_FRONT):
    if fr:
        S.polygon(q, THEORY, 0.07)
for e in CUBE_EDGES:
    if not edge_hidden(e) and not at_origin(e):
        S.line([F(e[0]), F(e[1])], THEORY, 1.0, None, 0.55)

# ---- 5. 45-degree floor arcs of radius 0.4 --------------------------------------------------------
R_ARC = 0.4


def floor_arc(t0, t1, n=40):
    return [(R_ARC * math.cos(math.radians(t0 + (t1 - t0) * k / n)),
             R_ARC * math.sin(math.radians(t0 + (t1 - t0) * k / n)), 0.0) for k in range(n + 1)]


S.line(floor_arc(0, 45), TEXT, 1.0, "2.4 1.8", 0.85)
S.line(floor_arc(90, 135), TEXT, 1.0, "2.4 1.8", 0.85)

# ---- 6. arrows ----------------------------------------------------------------------------------
for U in (U1, U2, U3):
    arrow3(O, U, TEXT, 1.4, 7.5, opacity=0.68)
arrow3(O, FU2, BASE, 2.6, 10.5)
arrow3(O, FU1, THEORY, 2.6, 10.5)
arrow3(O, FU3, PRACTICE, 2.6, 10.5)
arrow3(O, U3, TEXT, 1.4, 7.5, opacity=0.85, outline=True, shaft=False)   # unit mark on the orange shaft

# p -> F(p): thin dashed arrow ending on the rim of the hollow circle
R_P, R_FP = 3.8, 4.2
(ax_, ay_), (bx_, by_) = px(p), px(Fp)
L = math.hypot(bx_ - ax_, by_ - ay_)
ux, uy = (bx_ - ax_) / L, (by_ - ay_) / L
arrow_px((ax_ + ux * (R_P + 3), ay_ + uy * (R_P + 3)), (bx_ - ux * (R_FP + 2), by_ - uy * (R_FP + 2)),
         TEXT, 1.1, 8, dash="5 3.5", opacity=0.75)
S.point(p, TEXT, R_P)
S.hollow(Fp, TEXT, R_FP, 1.7)

# ---- 7. labels ----------------------------------------------------------------------------------
def u_name(k):
    return bold("u") + subs(k)


def F_of(k):
    return ital("F") + "(" + u_name(k) + ")"


tag(U1, u_name("1"), -7, -5, TEXT, 11.5, "end")
tag(U2, u_name("2"), 6, 19, TEXT, 11.5, "middle")
tag(U3, u_name("3"), -8, 3, TEXT, 11.5, "end")

tag(FU1, F_of("1") + " = " + coords(FU1), 6, 21, THEORY, 11, "middle")
dCD = px((0, 2, 0))[0] - px(FU2)[0]                      # page gap from F(u2) to the front edge at (0, 2, 0)
tag(FU2, F_of("2") + " = " + coords(FU2), dCD + 6, 4, BASE, 11, "start")
tag(FU3, F_of("3") + " = " + coords(FU3), -8, 4, PRACTICE, 11, "end")

tag(p, bold("p") + " = " + coords(p), -9, 4, TEXT, 11, "end")
tag(Fp, ital("F") + "(" + bold("p") + ") = " + coords(Fp), 9, 4, TEXT, 11, "start")

# angle labels: the first on the bisector of its wedge; the second midway between the +y and F(u2)
# rays, at page X = 0.77, between the vertical box edge over (1, 1, 0) (X = 0.60) and the cube edge
# over u2 (X = 0.94), which both cross that narrow wedge
DEG = "45&#176;"
tag((0.72 * math.cos(math.radians(22.5)), 0.72 * math.sin(math.radians(22.5)), 0), DEG, 0, 4, TEXT, 10, "middle")
xy2, xf2 = S.pt(U2), S.pt(FU2)
X2 = 0.77
Y2 = 0.5 * (X2 * xy2[1] / xy2[0] + X2 * xf2[1] / xf2[0])
P.add(f'<text x="{P.X(X2):.1f}" y="{P.Y(Y2) + 3.5:.1f}" fill="{TEXT}" font-size="10" text-anchor="middle" '
      f'stroke="{BG}" stroke-width="3.2" stroke-linejoin="round" paint-order="stroke">{DEG}</text>')

OUT["donusum-lineer-birim-noktalar"] = figure(
    480, 520, [P],
    "<em>F</em> = (<em>x</em> &#8722; <em>y</em>, <em>x</em> + <em>y</em>, 2<em>z</em>) lineer dönüşümü, "
    "ince gri oklarla gösterilen <strong>u</strong><sub>1</sub>, <strong>u</strong><sub>2</sub>, "
    "<strong>u</strong><sub>3</sub> birim noktalarını sırasıyla (1, 1, 0), (&#8722;1, 1, 0) ve (0, 0, 2) "
    "noktalarına götürür. İki yatay ok <em>z</em> ekseni çevresinde 45 derece döner ve &#8730;2 katına uzar, "
    "düşey ok ise iki katına çıkar; bu yüzden kesikli birim küp, tabanı 45 derece dönmüş bir kare ve "
    "yüksekliği 2 olan mavi kutuya gider. "
    "Başka her noktanın görüntüsü bu üç değerden okunur: <strong>p</strong> = (2, 1, &#8722;1) için "
    "<em>F</em>(<strong>p</strong>) = 2<em>F</em>(<strong>u</strong><sub>1</sub>) + "
    "<em>F</em>(<strong>u</strong><sub>2</sub>) &#8722; <em>F</em>(<strong>u</strong><sub>3</sub>) = (1, 3, &#8722;2).",
    aria="Lineer donusum F = (x - y, x + y, 2z): ince gri u1, u2, u3 oklari ve kesikli birim kup; kalin "
         "F(u1) = (1, 1, 0) mavi, F(u2) = (-1, 1, 0) yesil, F(u3) = (0, 0, 2) turuncu oklar; zeminde 45 "
         "derecelik iki kesikli yay; tabani (0, 0, 0), (1, 1, 0), (0, 2, 0), (-1, 1, 0) karesi ve yuksekligi "
         "2 olan yari saydam mavi kutu; p = (2, 1, -1) dolu nokta, F(p) = (1, 3, -2) ici bos daire ve "
         "aralarinda kesikli ok")

# ============================================================ donusum-paraboller-birim-kare
# -*- coding: utf-8 -*-
# donusum-paraboller-birim-kare: F(u, v) = (u^2 - v^2, 2uv) carries the unit square onto an arch (2D).
# Left, the (u, v) plane on [-2.5, 2.5]^2: the line v = 1 (blue) with the points (t, 1), t = -2..2,
# the line u = 1 (green) with the points (1, t), and the hatched unit square [0, 1] x [0, 1].
# Right, the (x, y) plane on [-4, 4] x [-4.5, 4.5]: the images x = y^2/4 - 1 (blue, vertex (-1, 0))
# and x = 1 - y^2/4 (green, vertex (1, 0)) with the image points of the dots on the left; the two
# parabolas meet at (0, 2) and (0, -2), both ringed. The hatched region is
# R = { y >= 0, y^2/4 - 1 <= x <= 1 - y^2/4 }, the image of the square.
# Both panels use equal scale (46 px per unit on the left, 230/9 px per unit on the right), so the
# right angle at (0, 2) is drawn as a right angle.
# Colour convention: lines and parabolas THEORY / BASE as in the text; square and region PRACTICE;
# the bottom and left edges of the square and their image, the segment [-1, 1] of the x axis, are
# drawn as thick PRACTICE strokes. The palette has no red, purple or brown token, so a corner and its
# image share a marker SHAPE instead of a colour: (0, 0) circle, (1, 0) square, (1, 1) -> (0, 2)
# diamond, (0, 1) -> (-1, 0) triangle.
import math

PPU_L = 46                         # pixels per unit, left panel
BAND = 5 * PPU_L                   # common panel height
PPU_R = BAND / 9                   # pixels per unit, right panel
TOP, LEFT, GAP = 24, 22, 66

pl = Plot(LEFT, TOP, BAND, BAND, (-2.5, 2.5), (-2.5, 2.5))
pr = Plot(LEFT + BAND + GAP, TOP, 8 * PPU_R, BAND, (-4.0, 4.0), (-4.5, 4.5))

TS = (-2, -1, 0, 1, 2)
Y_END = math.sqrt(20.0)            # |y| where both parabolas reach x = +-4, the panel's side edges


def ital(s):
    return f'<tspan font-style="italic">{s}</tspan>'


def num(v):
    """Integer tick label with a real minus sign."""
    return (MINUS_S + str(-v)) if v < 0 else str(v)


def halo_px(p, px, py, s, color=TEXT, size=11, anchor="start", fill_opacity=1.0):
    """Text at a pixel position with a page-coloured halo that breaks the lines behind it."""
    fo = f' fill-opacity="{fill_opacity}"' if fill_opacity < 1.0 else ""
    p.add(f'<text x="{px:.1f}" y="{py:.1f}" fill="{color}"{fo} font-size="{size}" text-anchor="{anchor}" '
          f'stroke="{BG}" stroke-width="3.2" stroke-linejoin="round" paint-order="stroke">{s}</text>')


def halo(p, x, y, s, dx=0, dy=0, color=TEXT, size=11, anchor="start"):
    halo_px(p, p.X(x) + dx, p.Y(y) + dy, s, color, size, anchor)


def ticks(p, xs, ys, xnum, ynum):
    """Tick marks on the axes through the origin; numbers (with halo) only where asked."""
    ox, oy = p.X(0), p.Y(0)
    for t in xs:
        p.add(f'<line x1="{p.X(t):.1f}" y1="{oy - 3:.1f}" x2="{p.X(t):.1f}" y2="{oy + 3:.1f}" '
              f'stroke="{TEXT}" stroke-width="1" opacity="0.7"/>')
        if t in xnum:
            halo_px(p, p.X(t), oy + 15, num(t), TEXT, 10.5, "middle", 0.7)
    for t in ys:
        p.add(f'<line x1="{ox - 3:.1f}" y1="{p.Y(t):.1f}" x2="{ox + 3:.1f}" y2="{p.Y(t):.1f}" '
              f'stroke="{TEXT}" stroke-width="1" opacity="0.7"/>')
        if t in ynum:
            halo_px(p, ox - 7, p.Y(t) + 4, num(t), TEXT, 10.5, "end", 0.7)


def hatch(p, poly, angle_deg, color, step_px=5.5, width=0.8, opacity=0.5):
    """Parallel hatch lines at angle_deg, clipped to a convex polygon given in data coordinates."""
    a = math.radians(angle_deg)
    d = (math.cos(a), math.sin(a))
    n = (-d[1], d[0])
    step = step_px * (p.xmax - p.xmin) / p.w          # pixels -> data units (equal scale)
    proj = [n[0] * x + n[1] * y for x, y in poly]
    lo, hi = min(proj), max(proj)
    count = int((hi - lo) / step)
    c0 = lo + (hi - lo - (count - 1) * step) / 2
    parts = []
    for i in range(count):
        c = c0 + i * step
        hits = []
        for j in range(len(poly)):
            (x0, y0), (x1, y1) = poly[j], poly[(j + 1) % len(poly)]
            s0 = n[0] * x0 + n[1] * y0 - c
            s1 = n[0] * x1 + n[1] * y1 - c
            if (s0 < 0) != (s1 < 0):
                t = s0 / (s0 - s1)
                hits.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t))
        if len(hits) >= 2:
            hits.sort(key=lambda q: d[0] * q[0] + d[1] * q[1])
            parts.append(f"M{p.P(*hits[0])} L{p.P(*hits[-1])}")
    p.add(f'<path d="{" ".join(parts)}" fill="none" stroke="{color}" stroke-width="{width}" '
          f'opacity="{opacity}" stroke-linecap="butt"/>')


def shaded(p, poly):
    p.polygon(poly, PRACTICE, 0.13, "none")
    hatch(p, poly, 45, PRACTICE)


def bead(p, pt, color, r=2.8):
    """Small dot on a curve of the same colour; a thin page-coloured rim keeps it visible."""
    p.add(f'<circle cx="{p.X(pt[0]):.1f}" cy="{p.Y(pt[1]):.1f}" r="{r}" fill="{color}" '
          f'stroke="{BG}" stroke-width="1.2" paint-order="stroke"/>')


def ring(p, pt, r=8.0):
    p.add(f'<circle cx="{p.X(pt[0]):.1f}" cy="{p.Y(pt[1]):.1f}" r="{r}" fill="none" '
          f'stroke="{TEXT}" stroke-width="1.4" opacity="0.85"/>')


def marker(p, pt, shape, size=4.4):
    """Corner marker; a corner and its image share the shape."""
    X, Y = p.X(pt[0]), p.Y(pt[1])
    style = f'fill="{TEXT}" stroke="{BG}" stroke-width="1.6" stroke-linejoin="round" paint-order="stroke"'
    if shape == "circle":
        p.add(f'<circle cx="{X:.1f}" cy="{Y:.1f}" r="{size * 0.86:.1f}" {style}/>')
    elif shape == "square":
        s = size * 0.78
        p.add(f'<rect x="{X - s:.1f}" y="{Y - s:.1f}" width="{2 * s:.1f}" height="{2 * s:.1f}" {style}/>')
    elif shape == "diamond":
        s = size * 1.15
        p.add(f'<polygon points="{X:.1f},{Y - s:.1f} {X + s:.1f},{Y:.1f} {X:.1f},{Y + s:.1f} '
              f'{X - s:.1f},{Y:.1f}" {style}/>')
    else:                                               # triangle, apex up
        s = size * 1.2
        p.add(f'<polygon points="{X:.1f},{Y - s:.1f} {X + s * 0.866:.1f},{Y + s * 0.5:.1f} '
              f'{X - s * 0.866:.1f},{Y + s * 0.5:.1f}" {style}/>')


def F(pt):
    u, v = pt
    return (u * u - v * v, 2 * u * v)


# ---- left: the (u, v) plane ---------------------------------------------------------------------
SQUARE = [(0, 0), (1, 0), (1, 1), (0, 1)]
shaded(pl, SQUARE)
pl.origin_axes("u", "v")
ticks(pl, (-2, -1, 1, 2), (-2, -1, 1, 2), (-2, -1, 2), (-2, -1, 2))
pl.line([(0, 1), (0, 0), (1, 0)], PRACTICE, 2.4, None, 0.9)     # left and bottom edge of the square
pl.line([(-2.5, 1), (2.5, 1)], THEORY, 2.1)                      # v = 1
pl.line([(1, -2.5), (1, 2.5)], BASE, 2.1)                        # u = 1
for t in TS:
    bead(pl, (t, 1), THEORY)
    bead(pl, (1, t), BASE)

LEFT_CORNERS = ((0, 0), (1, 0), (1, 1), (0, 1))
SHAPES = ("circle", "square", "diamond", "triangle")
for c, s in zip(LEFT_CORNERS, SHAPES):
    marker(pl, c, s)

halo(pl, -1.5, 1, ital("v") + " = 1", 0, -8, THEORY, 11.5, "middle")
halo(pl, 1, -1.5, ital("u") + " = 1", 8, 4, BASE, 11.5, "start")

# ---- the arrow F between the panels ----------------------------------------------------------------
AY = pl.Y(0.5)
ax0, ax1 = pl.x0 + pl.w + 14, pr.x0 - 14
# shaft and head share one <g opacity>, so they do not darken where they overlap
pl.add(f'<g opacity="0.8">'
       f'<line x1="{ax0:.1f}" y1="{AY:.1f}" x2="{ax1 - 7:.1f}" y2="{AY:.1f}" stroke="{TEXT}" '
       f'stroke-width="1.6" stroke-linecap="butt"/>'
       f'<polygon points="{ax1:.1f},{AY:.1f} {ax1 - 9:.1f},{AY - 3.8:.1f} {ax1 - 9:.1f},{AY + 3.8:.1f}" '
       f'fill="{TEXT}"/></g>')
pl.text_px((ax0 + ax1) / 2, AY - 8, "F", TEXT, 13, "middle", False, True)     # 13 as in the sibling figures

# ---- right: the (x, y) plane ------------------------------------------------------------------------
N = 80
green_arc = [(1 - (2 * k / N) ** 2 / 4, 2 * k / N) for k in range(N + 1)]          # (1, 0) -> (0, 2)
blue_arc = [((2 - 2 * k / N) ** 2 / 4 - 1, 2 - 2 * k / N) for k in range(N + 1)]    # (0, 2) -> (-1, 0)
REGION = green_arc + blue_arc[1:]
shaded(pr, REGION)
pr.origin_axes("x", "y")
ticks(pr, (-3, -2, -1, 1, 2, 3), (-4, -3, -2, -1, 1, 2, 3, 4), (-3, -2, 2, 3), (-4, 4))
pr.line([(-1, 0), (1, 0)], PRACTICE, 2.4, None, 0.9)             # image of the two lower edges

ys = [-Y_END + 2 * Y_END * k / 240 for k in range(241)]
pr.line([(y * y / 4 - 1, y) for y in ys], THEORY, 2.1)            # image of v = 1
pr.line([(1 - y * y / 4, y) for y in ys], BASE, 2.1)              # image of u = 1
for t in TS:
    bead(pr, F((t, 1)), THEORY)       # (3, -4), (0, -2), (-1, 0), (0, 2), (3, 4)
    bead(pr, F((1, t)), BASE)         # (-3, -4), (0, -2), (1, 0), (0, 2), (-3, 4)

ring(pr, (0, 2))
ring(pr, (0, -2))
for c, s in zip(LEFT_CORNERS, SHAPES):
    marker(pr, F(c), s)               # (0, 0), (1, 0), (0, 2), (-1, 0)

# the label sits in the right-angle wedge that opens to the right of (0, 2); 15 px keeps it clear of
# the ring and of both parabolas (dx = 12 left only about 4 px)
halo(pr, 0, 2, ital("F") + "(1, 1) = (0, 2)", 15, 4, TEXT, 11, "start")
# baseline y = -2.25: the parabola is nearest the label at the label's inner bottom corner, and there
# a label up to 70 px wide (a wider page font) still keeps about 25 px from its curve
halo(pr, 3.9, -2.25, ital("x") + " = " + ital("y") + sups("2") + "/4 " + MINUS_S + " 1", 0, 0, THEORY, 11.5, "end")
halo(pr, -3.9, -2.25, ital("x") + " = 1 " + MINUS_S + " " + ital("y") + sups("2") + "/4", 0, 0, BASE, 11.5, "start")

OUT["donusum-paraboller-birim-kare"] = figure(
    int(pr.x0 + pr.w + 26), int(TOP + BAND + 28), [pl, pr],
    "Solda <em>v</em> = 1 yatay doğrusu (mavi), <em>u</em> = 1 dikey doğrusu (yeşil) ve taralı birim kare; "
    "sağda bunların <em>F</em>(<em>u</em>, <em>v</em>) = (<em>u</em><sup>2</sup> &#8722; <em>v</em><sup>2</sup>, "
    "2<em>uv</em>) altındaki görüntüleri: <em>x</em> = <em>y</em><sup>2</sup>/4 &#8722; 1 ve "
    "<em>x</em> = 1 &#8722; <em>y</em><sup>2</sup>/4 parabolleri ile tepesi (0, 2)&#8217;de olan kemer "
    "biçimli bölge. Karenin üst ve sağ kenarı iki parabol yayına, turuncu çizilen alt ve sol kenarı ise "
    "<em>x</em> ekseninin [&#8722;1, 1] parçasının iki yarısına gider. Aynı biçimli işaretler her köşeyi "
    "görüntüsüyle eşler: (1, 1)&#8217;deki dik açı (0, 2)&#8217;de dik kalır, (0, 0)&#8217;daki dik açı "
    "ise düz açıya açılır. Halkalı (0, &#8722;2) noktası iki farklı noktanın, (&#8722;1, 1) ile "
    "(1, &#8722;1)&#8217;in görüntüsüdür.",
    css_class=WIDE,
    aria="Iki panel, aralarinda F oku. Solda uv duzleminde v = 1 mavi yatay dogru, u = 1 yesil dikey dogru, "
         "uzerlerinde t = -2, -1, 0, 1, 2 noktalari; [0, 1] x [0, 1] birim karesi turuncu tarali, koseleri "
         "(0, 0) daire, (1, 0) kare, (1, 1) baklava, (0, 1) ucgen isaretli. Sagda xy duzleminde x = y^2/4 - 1 "
         "mavi ve x = 1 - y^2/4 yesil paraboller; mavi uzerinde (3, -4), (0, -2), (-1, 0), (0, 2), (3, 4), "
         "yesil uzerinde (-3, -4), (0, -2), (1, 0), (0, 2), (-3, 4); kesisim noktalari (0, 2) ve (0, -2) "
         "halkali. y >= 0, x ekseninin [-1, 1] parcasi ve iki parabol yayi arasindaki bolge tarali; kose "
         "goruntuleri (0, 0) daire, (1, 0) kare, (0, 2) baklava, (-1, 0) ucgen. F(1, 1) = (0, 2).",
)

# ============================================================ donusum-teget-donusumu-tanimi
# -*- coding: utf-8 -*-
# donusum-teget-donusumu-tanimi — the tangent map from its definition, F(u, v) = (u + v, uv).
# Left (uv plane): the line t -> p + tv = (1 + t, 2 + t), t in [-1, 1], through p = (1, 2), and the
# tangent vector v_p = (1, 1) at p (tip (2, 3)). Right (xy plane): the image curve
# beta(t) = F(p + tv) = (3 + 2t, 2 + 3t + t^2), t in [-1, 1], through F(p) = (3, 2), and its initial
# velocity F_*(v_p) = (2, 3) (tip (5, 5)) lying on the dashed tangent line of the parabola at (3, 2).
# Small blue dots mark t = -1, 0.5, 1 in both panels. There is no red in the palette, so p and F(p)
# are the larger TEXT dots. Both panels have equal aspect and their horizontal axes share a pixel row.
import math

KL, KR = 60, 32                                   # pixels per unit, left and right panel
L = cplane(40, 34, 3.5 * KL, (-0.5, 3.0), (0.0, 3.5))
R = cplane(350, 20, 6.0 * KR, (0.0, 6.0), (-0.5, 7.0))

TS = (-1.0, 0.5, 1.0)


def line_pt(t):
    return (1.0 + t, 2.0 + t)


def beta(t):
    return (3.0 + 2.0 * t, 2.0 + 3.0 * t + t * t)


def ital(s):
    return '<tspan font-style="italic">' + s + '</tspan>'


def halo(P, x, y, s, dx=0, dy=0, color=TEXT, size=11.5, anchor="start"):
    """Label at a data point with a page-coloured halo, so grid lines behind it break.
    The halo is a separate text layer underneath: with a single stroked <text>, the halo of a
    later tspan (the bold v in 'tv') paints over the crossbar of the italic t before it."""
    pos = f'x="{P.X(x) + dx:.1f}" y="{P.Y(y) + dy:.1f}" font-size="{size}" text-anchor="{anchor}"'
    P.add(f'<text {pos} fill="{BG}" stroke="{BG}" stroke-width="3.2" stroke-linejoin="round">{s}</text>')
    P.add(f'<text {pos} fill="{color}">{s}</text>')


def mark(P, pt, color, r):
    """Filled dot with a thin page-coloured ring, so it reads on top of lines and arrows."""
    P.add(f'<circle cx="{P.X(pt[0]):.1f}" cy="{P.Y(pt[1]):.1f}" r="{r + 1.3:.1f}" fill="{BG}"/>')
    dot(P, pt, color, r)


def unpx(P, px, py):
    """Pixel position -> data point of panel P."""
    return (P.xmin + (px - P.x0) / P.w * (P.xmax - P.xmin),
            P.ymin + (P.y0 + P.h - py) / P.h * (P.ymax - P.ymin))


def arrow_into_dot(P, p0, p1, gap, color, width, head):
    """Arrow from p0 towards p1 whose head stops `gap` pixels short, touching a dot drawn at p1."""
    x0, y0, x1, y1 = P.X(p0[0]), P.Y(p0[1]), P.X(p1[0]), P.Y(p1[1])
    n = math.hypot(x1 - x0, y1 - y0)
    tip = unpx(P, x1 - (x1 - x0) / n * gap, y1 - (y1 - y0) / n * gap)
    P.arrow(p0, tip, color, width, head)


F_S = ital("F")
V_P = bold("v") + subs(bold("p"))

# ---------------------------------------------------------------- left panel: uv plane
L.grid(xs=(1, 2), ys=(1, 2, 3))
L.origin_axes("u", "v", xticks=(1, 2), yticks=(1, 2, 3))

L.line([line_pt(-1.0), line_pt(1.0)], THEORY, 2.2)
L.arrow(line_pt(-0.72), line_pt(-0.42), THEORY, 2.2, head=9)       # direction of travel
arrow_into_dot(L, line_pt(0.0), line_pt(1.0), 4.3, PRACTICE, 2.8, 10.5)

for t in TS:
    mark(L, line_pt(t), THEORY, 2.8)
mark(L, line_pt(0.0), TEXT, 4.0)

halo(L, 1.0, 2.0, bold("p"), -9, -6, TEXT, 12.5, "end")
halo(L, 1.75, 2.75, V_P + " = (1, 1)", 12, 16, PRACTICE, 12, "start")
halo(L, 0.5, 1.5, bold("p") + " + " + ital("t") + bold("v"), 10, 16, THEORY, 12, "start")

# ---------------------------------------------------------------- the map F between the panels
AY = 140
L.add(f'<g opacity="0.8">'
      f'<line x1="270" y1="{AY}" x2="{320 - 8:.1f}" y2="{AY}" stroke="{TEXT}" stroke-width="1.4"/>'
      f'<polygon points="320,{AY} {320 - 9},{AY - 3.8} {320 - 9},{AY + 3.8}" fill="{TEXT}"/></g>')
L.text_px(295, AY - 8, F_S, TEXT, 13, "middle")

# ---------------------------------------------------------------- right panel: xy plane
R.grid(xs=(1, 2, 3, 4, 5), ys=(1, 2, 3, 4, 5, 6))
R.origin_axes("x", "y", xticks=(1, 2, 3, 4, 5), yticks=(1, 2, 3, 4, 5, 6))

# tangent line of the parabola at (3, 2): (3 + 2s, 2 + 3s)
R.line([(3.0 + 2.0 * s, 2.0 + 3.0 * s) for s in (-0.8, 1.5)], TEXT, 1.1, "5 4", 0.6)

N = 160
R.line([beta(-1.0 + 2.0 * k / N) for k in range(N + 1)], THEORY, 2.2)
# direction of travel: the head runs into the t = 1 dot; mid-curve it would crowd the orange head
arrow_into_dot(R, beta(0.86), beta(1.0), 4.3, THEORY, 2.2, 9)
# The t = 0.5 dot (4, 3.75) is only 4.4 px from the orange shaft's centre line, so its page-coloured
# ring would bite into the shaft: paint the rings before the arrow and the dot fills after it.
for t in TS:
    R.add(f'<circle cx="{R.X(beta(t)[0]):.1f}" cy="{R.Y(beta(t)[1]):.1f}" r="4.1" fill="{BG}"/>')
R.arrow((3.0, 2.0), (5.0, 5.0), PRACTICE, 2.8, head=10.5)

for t in TS:
    dot(R, beta(t), THEORY, 2.8)
mark(R, beta(0.0), TEXT, 4.0)

halo(R, 3.0, 2.0, F_S + "(" + bold("p") + ")", -9, -6, TEXT, 12, "end")
halo(R, 3.0, 2.0, F_S + subs("*") + "(" + V_P + ") = (2, 3)", 25, -12, PRACTICE, 12, "start")
halo(R, 4.4, 4.6, ital("&#946;") + "(" + ital("t") + ") = " + F_S + "(" + bold("p") + " + "
     + ital("t") + bold("v") + ")", -15, 0, THEORY, 12, "end")

OUT["donusum-teget-donusumu-tanimi"] = figure(
    580, 280, [L, R],
    "Solda <strong>p</strong> = (1, 2) noktasından <strong>v</strong> = (1, 1) hızıyla geçen "
    "<strong>p</strong> + <em>t</em><strong>v</strong> doğrusu ve <strong>v</strong><sub><strong>p</strong></sub> "
    "oku; sağda bu doğrunun <em>F</em>(<em>u</em>, <em>v</em>) = (<em>u</em> + <em>v</em>, <em>uv</em>) altındaki "
    "görüntüsü &#946;(<em>t</em>) = (3 + 2<em>t</em>, 2 + 3<em>t</em> + <em>t</em><sup>2</sup>) parabolü ve "
    "onun <em>F</em>(<strong>p</strong>) = (3, 2) noktasındaki başlangıç hızı "
    "<em>F</em><sub>*</sub>(<strong>v</strong><sub><strong>p</strong></sub>) = (2, 3). "
    "Küçük mavi noktalar iki panelde de <em>t</em> = &#8722;1, <em>t</em> = 0,5 ve <em>t</em> = 1 anlarıdır. "
    "Solda okun ucu <em>t</em> = 1 noktasına tam oturur; sağda ise ok parabolün kesikli teğet doğrusu "
    "üzerinde kalıp (5, 5)'te biter ve &#946;(1) = (5, 6) ile arasındaki fark <em>t</em><sup>2</sup> = 1 olur.",
    css_class=WIDE,
    aria="Iki panel. Solda uv duzleminde p = (1, 2), mavi p + tv = (1 + t, 2 + t) dogrusu (t -1 ile 1 arasi), "
         "p'de turuncu v_p = (1, 1) oku, ucu (2, 3); t = -1, 0.5, 1 noktalari (0, 1), (1.5, 2.5), (2, 3). "
         "Paneller arasinda F oku. Sagda xy duzleminde F(p) = (3, 2), mavi beta(t) = (3 + 2t, 2 + 3t + t^2) "
         "parabol parcasi, noktalari (1, 0), (4, 3.75), (5, 6); F(p)'de turuncu F_*(v_p) = (2, 3) oku, "
         "ucu (5, 5), parabolun (3, 2)'deki kesikli gri teget dogrusu uzerinde.",
)

# ============================================================ donusum-toplam-carpim-katlama
# -*- coding: utf-8 -*-
# donusum-toplam-carpim-katlama: F(u, v) = (u + v, uv) folds the plane along the diagonal (2D, two panels).
# Left, the (u, v) plane on [-1, 3] x [-1, 3], equal scale: the fold line u = v; the half-plane below it
# (v < u) is shaded and hatched blue, the half-plane above it (v > u) orange. The mirror points (1, 2)
# (orange) and (2, 1) (blue). The green segment t -> (1 + t, 1 - t), t in [-1, 1], runs from (0, 2) to
# (2, 0) across the diagonal; at (1, 1) its velocity (1, -1) is the thick green arrow.
# Right, the (x, y) plane on [-2, 6] x [-2, 5], equal scale: both halves land on the image y <= x^2/4,
# so both hatchings are laid over it; the diagonal lands on the boundary parabola y = x^2/4.
# F(1, 2) = F(2, 1) = (3, 2) is a dot split along the diagonal direction (orange upper-left, blue
# lower-right), echoing the two half-planes. The image (2, 1 - t^2) of the green segment climbs from
# (2, 0) to (2, 1) and comes back down; it is drawn as a hairpin. At (2, 1), on the parabola, the
# velocity is zero.
# The palette has no red or purple token: the fold line and the parabola are thick TEXT, and the doubly
# covered point is the orange/blue split dot.
# Point names follow the example text, which writes F(1, 2) = F(2, 1) = (3, 2) and reserves bold p for
# the diagonal point (a, a); so the two mirror points are labelled by their coordinates.
import math

L_W = 210                         # left panel: width = height, 4 x 4 units (52.5 px per unit)
R_W = 320                         # right panel: 8 x 7 units (40 px per unit), height 280
GAP = 58                          # space between the panels, holds the F arrow
LEFT, TOP = 22, 22

HATCH_BLUE, HATCH_ORANGE = 22.5, 112.5   # hatch angles on screen; neither runs along the diagonal (45),
                                          # the green segment (-45) or its vertical image (90)
FOLD_W = 2.4                      # width of the fold line and of the parabola
GREEN_W = 1.8
SQ20 = math.sqrt(20.0)            # where the parabola leaves the top edge y = 5

pr = cplane(LEFT + L_W + GAP, TOP, R_W, (-2.0, 6.0), (-2.0, 5.0))
# the left panel sits so that its u axis (v = 0) runs on the same line as the right panel's x axis
pl = Plot(LEFT, pr.Y(0) - L_W * 3 / 4, L_W, L_W, (-1.0, 3.0), (-1.0, 3.0))


def ital(s):
    return f'<tspan font-style="italic">{s}</tspan>'


def mfmt(v):
    return tfmt(v).replace("-", MINUS_S)


def halo_px(p, px, py, s, color=TEXT, size=11.5, anchor="start", opacity=1.0):
    """Text at a pixel position with a page-coloured halo, so hatch lines behind it break."""
    fo = f' fill-opacity="{opacity}"' if opacity < 1.0 else ""
    p.add(f'<text x="{px:.1f}" y="{py:.1f}" fill="{color}"{fo} font-size="{size}" text-anchor="{anchor}" '
          f'stroke="{BG}" stroke-width="3.2" stroke-linejoin="round" paint-order="stroke">{s}</text>')


def halo(p, x, y, s, dx=0, dy=0, color=TEXT, size=11.5, anchor="start", opacity=1.0):
    halo_px(p, p.X(x) + dx, p.Y(y) + dy, s, color, size, anchor, opacity)


def axes(p, xname, yname, xticks, yticks):
    """Axes through the origin with arrowheads; tick labels carry a halo because the panels are hatched."""
    ox, oy = p.X(0), p.Y(0)
    left, right = p.x0 - 4, p.x0 + p.w + 4
    top, bottom = p.y0 - 4, p.y0 + p.h + 4
    p.add(f'<g stroke="{TEXT}" stroke-width="1.1" opacity="0.6" fill="{TEXT}">'
          f'<line x1="{left:.1f}" y1="{oy:.1f}" x2="{right - 6:.1f}" y2="{oy:.1f}"/>'
          f'<line x1="{ox:.1f}" y1="{bottom:.1f}" x2="{ox:.1f}" y2="{top + 6:.1f}"/>'
          f'<polygon points="{right:.1f},{oy:.1f} {right - 8:.1f},{oy - 3.5:.1f} {right - 8:.1f},{oy + 3.5:.1f}" stroke="none"/>'
          f'<polygon points="{ox:.1f},{top:.1f} {ox - 3.5:.1f},{top + 8:.1f} {ox + 3.5:.1f},{top + 8:.1f}" stroke="none"/>'
          f'</g>')
    for t in xticks:
        p.add(f'<line x1="{p.X(t):.1f}" y1="{oy - 3:.1f}" x2="{p.X(t):.1f}" y2="{oy + 3:.1f}" '
              f'stroke="{TEXT}" stroke-width="1" opacity="0.7"/>')
        halo_px(p, p.X(t), oy + 15, mfmt(t), TEXT, 10.5, "middle", 0.75)
    for t in yticks:
        p.add(f'<line x1="{ox - 3:.1f}" y1="{p.Y(t):.1f}" x2="{ox + 3:.1f}" y2="{p.Y(t):.1f}" '
              f'stroke="{TEXT}" stroke-width="1" opacity="0.7"/>')
        halo_px(p, ox - 7, p.Y(t) + 4, mfmt(t), TEXT, 10.5, "end", 0.75)
    halo_px(p, right - 2, oy + 15, ital(xname), TEXT, 11.5, "end", 0.85)
    halo_px(p, ox + 7, top + 9, ital(yname), TEXT, 11.5, "start", 0.85)


def hatch(p, poly, angle_deg, color, step=6.0, width=0.8, opacity=0.5):
    """Parallel hatch lines at angle_deg (on screen, counter-clockwise from +x), clipped to a simple
    polygon given in data coordinates. Works in pixels, so the spacing is the same in every panel;
    the crossings of each line are paired even-odd, so non-convex polygons are fine."""
    q = [(p.X(x), p.Y(y)) for x, y in poly]
    a = math.radians(angle_deg)
    d = (math.cos(a), -math.sin(a))
    n = (-d[1], d[0])
    proj = [n[0] * x + n[1] * y for x, y in q]
    c = math.floor(min(proj) / step) * step + step / 2
    parts = []
    while c < max(proj):
        hits = []
        for j in range(len(q)):
            (x0, y0), (x1, y1) = q[j], q[(j + 1) % len(q)]
            s0 = n[0] * x0 + n[1] * y0 - c
            s1 = n[0] * x1 + n[1] * y1 - c
            if (s0 < 0) != (s1 < 0):
                t = s0 / (s0 - s1)
                hits.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t))
        hits.sort(key=lambda h: d[0] * h[0] + d[1] * h[1])
        for k in range(0, len(hits) - 1, 2):
            (ax, ay), (bx, by) = hits[k], hits[k + 1]
            parts.append(f"M{ax:.1f},{ay:.1f} L{bx:.1f},{by:.1f}")
        c += step
    p.add(f'<path d="{" ".join(parts)}" fill="none" stroke="{color}" stroke-width="{width}" '
          f'opacity="{opacity}" stroke-linecap="butt"/>')


def haloed_line(p, pts, color, width, extra=3.2):
    p.line(pts, BG, width + extra)
    p.line(pts, color, width)


def ringed_dot(p, pt, color, r=4.0, ring=1.4):
    dot(p, pt, BG, r + ring)
    dot(p, pt, color, r)


def split_dot(p, pt, r=3.8, ring=1.2):
    """Dot cut along the diagonal direction: upper-left half orange, lower-right half blue."""
    cx, cy = p.X(pt[0]), p.Y(pt[1])
    a = r / math.sqrt(2)
    x1, y1, x2, y2 = cx + a, cy - a, cx - a, cy + a
    p.add(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r + ring}" fill="{BG}"/>')
    p.add(f'<path d="M{x1:.2f},{y1:.2f} A{r},{r} 0 0 0 {x2:.2f},{y2:.2f} Z" fill="{PRACTICE}"/>')
    p.add(f'<path d="M{x1:.2f},{y1:.2f} A{r},{r} 0 0 1 {x2:.2f},{y2:.2f} Z" fill="{THEORY}"/>')


def head_px(p, tx, ty, ux, uy, color, head=7.0):
    """Filled arrowhead with its tip at pixel (tx, ty), pointing along the unit vector (ux, uy)."""
    px, py, hw = -uy, ux, head * 0.42
    p.add(f'<polygon points="{tx:.1f},{ty:.1f} {tx - ux * head + px * hw:.1f},{ty - uy * head + py * hw:.1f} '
          f'{tx - ux * head - px * hw:.1f},{ty - uy * head - py * hw:.1f}" fill="{color}"/>')


# ---- left: the (u, v) plane ----------------------------------------------------------------------
BELOW = [(-1.0, -1.0), (3.0, -1.0), (3.0, 3.0)]        # v < u
ABOVE = [(-1.0, -1.0), (3.0, 3.0), (-1.0, 3.0)]        # v > u
pl.polygon(BELOW, THEORY, 0.09)
pl.polygon(ABOVE, PRACTICE, 0.09)
hatch(pl, BELOW, HATCH_BLUE, THEORY)
hatch(pl, ABOVE, HATCH_ORANGE, PRACTICE)
axes(pl, "u", "v", (1, 2), (1, 2))

haloed_line(pl, [(-1.0, -1.0), (3.0, 3.0)], TEXT, FOLD_W)          # the fold line u = v
# t -> (1 + t, 1 - t), t in [-1, 1]: its second half lies under the velocity arrow, so the thin line
# stops at (1, 1) and the halo stops inside the arrowhead (a round halo cap at the tip nicks the u axis)
pl.line([(0.0, 2.0), (1.85, 0.15)], BG, GREEN_W + 3.2)
pl.line([(0.0, 2.0), (1.0, 1.0)], BASE, GREEN_W)
pl.arrow((1.0, 1.0), (2.0, 0.0), BASE, 2.8, head=10)              # velocity (1, -1) at t = 0

ringed_dot(pl, (1.0, 2.0), PRACTICE, 4.0)
ringed_dot(pl, (2.0, 1.0), THEORY, 4.0)
ringed_dot(pl, (1.0, 1.0), BASE, 3.4)

halo(pl, 1.0, 2.0, "(1, 2)", 0, -10, PRACTICE, 11.5, "middle")
halo(pl, 2.0, 1.0, "(2, 1)", 11, 4, THEORY, 11.5, "start")
halo(pl, 2.5, 2.78, ital("u") + " = " + ital("v"), 0, 0, TEXT, 11.5, "end")
halo(pl, 1.29, 0.3, "(1, " + MINUS_S + "1)", 0, 0, BASE, 11, "end")

# ---- right: the (x, y) plane ---------------------------------------------------------------------
N = 240
IMAGE = ([(-2.0, -2.0), (6.0, -2.0), (6.0, 5.0), (SQ20, 5.0)]
         + [(SQ20 + (-2.0 - SQ20) * k / N, (SQ20 + (-2.0 - SQ20) * k / N) ** 2 / 4) for k in range(N + 1)])
pr.polygon(IMAGE, THEORY, 0.09)
pr.polygon(IMAGE, PRACTICE, 0.09)
hatch(pr, IMAGE, HATCH_BLUE, THEORY)
hatch(pr, IMAGE, HATCH_ORANGE, PRACTICE)
axes(pr, "x", "y", (-1, 1, 2, 3, 4, 5), (-1, 1, 2, 3, 4))

PARABOLA = [(-2.0 + (SQ20 + 2.0) * k / N, (-2.0 + (SQ20 + 2.0) * k / N) ** 2 / 4) for k in range(N + 1)]
pr.line(PARABOLA, BG, FOLD_W + 3.2)
# (3, 2) is only 0.14 units from the parabola: its dot goes under the parabola's stroke, so the curve
# stays whole and the dot visibly sits below it
split_dot(pr, (3.0, 2.0))
pr.line(PARABOLA, TEXT, FOLD_W)

# image of the green segment, (2, 1 - t^2): up the left strand, round the top, down the right strand
GX, GY0, GY1, D, HAIR_W = pr.X(2.0), pr.Y(0.0), pr.Y(1.0), 4.6, 2.0
hp = (f"M{GX - D:.1f},{GY0:.1f} L{GX - D:.1f},{GY1 + D:.1f} "
      f"A{D},{D} 0 0 1 {GX + D:.1f},{GY1 + D:.1f} L{GX + D:.1f},{GY0:.1f}")
pr.add(f'<path d="{hp}" fill="none" stroke="{BG}" stroke-width="{HAIR_W + 3.2}" stroke-linejoin="round"/>')
pr.add(f'<path d="{hp}" fill="none" stroke="{BASE}" stroke-width="{HAIR_W}" stroke-linejoin="round"/>')
# the two heads sit at different heights (up near the top, down near the bottom), so they never touch
head_px(pr, GX - D, pr.Y(0.70), 0.0, -1.0, BASE, 9.0)     # going up
head_px(pr, GX + D, pr.Y(0.12), 0.0, 1.0, BASE, 9.0)      # coming back down
ringed_dot(pr, (2.0, 1.0), BASE, 3.4)

FXY = lambda a, b: ital("F") + f"({a}, {b})"            # noqa: E731
# the doubly covered point: its coordinates next to the dot, the equality and the note underneath, all in
# the dark region to the right, where the parabola is at least 0.5 units away
halo(pr, 3.0, 2.0, "(3, 2)", 10, 4, TEXT, 11.5, "start")
halo(pr, 3.0, 2.0, "= " + FXY(1, 2) + " = " + FXY(2, 1), 10, 20, TEXT, 11, "start")
halo(pr, 3.0, 2.0, "iki ters görüntü", 10, 35, TEXT, 10, "start", 0.78)
halo(pr, 2.0, 1.0, "(2, 1)", -9, -5, TEXT, 11, "end")
halo(pr, 2.0, 1.0, "hız sıfır", -9, -20, BASE, 10, "end")
halo(pr, 3.95, 4.3, ital("y") + " = " + ital("x") + sups("2") + "/4", 0, 0, TEXT, 11.5, "end")

# ---- the map between the panels --------------------------------------------------------------------
AY = pr.Y(2.5)
AX0, AX1 = pl.x0 + pl.w + 12, pr.x0 - 10
pr.add(f'<line x1="{AX0:.1f}" y1="{AY:.1f}" x2="{AX1 - 8:.1f}" y2="{AY:.1f}" stroke="{TEXT}" '
       f'stroke-width="1.6" stroke-linecap="round"/>')
head_px(pr, AX1, AY, 1.0, 0.0, TEXT, 10.0)
pr.text_px((AX0 + AX1) / 2, AY - 8, "F", TEXT, 13, "middle", False, True)

OUT["donusum-toplam-carpim-katlama"] = figure(
    int(pr.x0 + pr.w + 24), int(pr.y0 + pr.h + 14), [pl, pr],
    "<em>F</em>(<em>u</em>, <em>v</em>) = (<em>u</em> + <em>v</em>, <em>uv</em>) dönüşümü düzlemi "
    "<em>u</em> = <em>v</em> köşegeni boyunca katlar: köşegenin altındaki mavi ve üstündeki turuncu "
    "yarı düzlem aynı <em>y</em> &#8804; <em>x</em><sup>2</sup>/4 bölgesine gider, bu yüzden sağda iki "
    "tarama üst üste biner; köşegenin görüntüsü sınırdaki <em>y</em> = <em>x</em><sup>2</sup>/4 "
    "parabolüdür. Köşegene göre simetrik turuncu (1, 2) ve mavi (2, 1) noktalarının ikisi de iki renkli "
    "(3, 2) noktasına düşer. Köşegeni dik kesen yeşil (1 + <em>t</em>, 1 &#8722; <em>t</em>) doğru "
    "parçasının görüntüsü (2, 1 &#8722; <em>t</em><sup>2</sup>) eğrisidir: "
    "(2, 0)&#8217;dan (2, 1)&#8217;e çıkar, parabol üzerinde durur ve geri iner. (1, 1) noktasındaki "
    "(1, &#8722;1) hız vektörü sıfıra ezildiği için bu dönüş noktasında hız sıfırdır.",
    css_class=WIDE,
    aria="Iki panel. Solda uv duzlemi, [-1, 3] x [-1, 3]: u = v kosegeni kalin cizgi; altindaki yari duzlem "
         "mavi, ustundeki turuncu tarali; (1, 2) turuncu, (2, 1) mavi nokta; (0, 2) ile (2, 0) arasinda "
         "yesil (1 + t, 1 - t) dogru parcasi ve (1, 1) noktasinda (1, -1) yesil ok. Aradaki ok F. "
         "Sagda xy duzlemi, "
         "[-2, 6] x [-2, 5]: y = x^2/4 parabolu kalin cizgi; altindaki goruntu bolgesi iki taramayla koyu; "
         "(3, 2) iki renkli nokta, iki ters goruntu, F(1, 2) = F(2, 1) = (3, 2); x = 2 uzerinde (2, 0)'dan "
         "(2, 1)'e cikip geri inen yesil cizgi; (2, 1) parabol uzerinde, hiz sifir.",
)

# ============================================================ egri-helis-hiz-vektorleri
# -*- coding: utf-8 -*-
# egri-helis-hiz-vektorleri: the helix alpha(t) = (cos t, sin t, t/2) on the cylinder x^2 + y^2 = 1
# with its velocity vectors at t = 0, pi/2, pi, 3pi/2; their vector parts are (-sin t, cos t, 1/2).
# A dashed vertical piece of length 1/2 hangs from every arrow tip: the constant rise.
# Painter's order: the far half of the tube with everything behind its near wall, then the near
# wall, then everything in front of it; far pieces of the helix are drawn lighter.
# Camera az = 20, el = 18 came out of a clearance scan: lower elevations lay the t = 0 arrow along
# the x axis, higher ones run the near helix through the point t = 3pi/2.
import math

AZ, EL = 20.0, 18.0
Z0, Z1 = -0.3, 3.5                   # height range of the drawn cylinder
T0, T1 = -0.3, 2 * math.pi + 0.3     # parameter range of the helix
XMAX, YMAX, ZMAX = 2.2, 1.9, 4.15    # axis ends; x reaches 2.2 so its arrowhead clears the bottom rim
PHI = math.radians(AZ)               # cos(u - PHI) > 0 on the half of the tube facing the viewer
TS = (0.0, math.pi / 2, math.pi, 3 * math.pi / 2)
FAR = (PHI + math.pi / 2, PHI + 3 * math.pi / 2)
NEAR = (PHI - math.pi / 2, PHI + math.pi / 2)


def helix(t):
    return (math.cos(t), math.sin(t), t / 2)


def velocity(t):
    """Vector part of alpha'(t)."""
    return (-math.sin(t), math.cos(t), 0.5)


def tube(u, z):
    return (math.cos(u), math.sin(u), z)


def near(u):
    return math.cos(u - PHI) > 0


def rim_arc(z, u0, u1, dash=None, opacity=0.5, n=60):
    S.line([tube(u0 + (u1 - u0) * k / n, z) for k in range(n + 1)], TEXT, 0.9, dash, opacity)


def helix_runs(front, n=1200):
    """Maximal pieces of the helix on the near (front=True) or far half of the tube."""
    ts = [T0 + (T1 - T0) * k / n for k in range(n + 1)]
    out, cur = [], []
    for i, t in enumerate(ts):
        if near(t) == front:
            if not cur and i > 0:
                cur.append(helix(ts[i - 1]))
            cur.append(helix(t))
        elif cur:
            cur.append(helix(t))
            out.append(cur)
            cur = []
    if cur:
        out.append(cur)
    return out


def velocity_arrow(t):
    B, V = helix(t), velocity(t)
    tip = vadd(B, V)
    S.guide([tip, vsub(tip, (0, 0, 0.5))], TEXT, 0.75, 1.1)   # the rise 1/2, hanging from the tip
    S.arrow(B, tip, PRACTICE, 2.4, head=9)


def tick_mark(Q):
    """Short tick through an axis point: along y on the x axis, along x on the y and z axes."""
    d = (0, 1, 0) if Q[1] == 0 and Q[2] == 0 else (1, 0, 0)
    S.line([vadd(Q, vscale(-0.04, d)), vadd(Q, vscale(0.04, d))], TEXT, 1.0, None, 0.7)


P = space_panel(16, 14, 384, (-2.4, 2.4), (-1.0, 4.3))
S = Space(P, Camera(azimuth=AZ, elevation=EL, scale=1.0))
near_runs = helix_runs(True)

# --- far half of the tube and what lies behind the near wall ----------------------------------
S.surface(tube, FAR, (Z0, Z1), nu=24, nv=1, fill=TEXT, stroke="none", opacity=(0.015, 0.06))
rim_arc(Z0, *FAR, dash="3 3", opacity=0.35)
rim_arc(Z1, *FAR, opacity=0.45)
for run in helix_runs(False):
    S.line(run, THEORY, 2.2, None, 0.55)
for t in TS:
    if not near(t):
        velocity_arrow(t)

# axes inside the tube
S.line([(0, 0, 0), (1, 0, 0)], TEXT, 1.0, None, 0.35)
S.line([(0, 0, 0), (0, 1, 0)], TEXT, 1.0, None, 0.35)
S.line([(0, 0, 0), (0, 0, Z1)], TEXT, 1.0, None, 0.4)
# z ticks stop at 2: at this view the helix ends right where a tick at 3 would sit
for k in (1, 2):
    tick_mark((0, 0, k))

# --- near half of the tube -------------------------------------------------------------------
S.surface(tube, NEAR, (Z0, Z1), nu=24, nv=1, fill=TEXT, stroke="none", opacity=(0.015, 0.06))
rim_arc(Z0, *NEAR, opacity=0.5)
rim_arc(Z1, *NEAR, opacity=0.5)
for u in NEAR:
    S.line([tube(u, Z0), tube(u, Z1)], TEXT, 0.9, None, 0.45)

# axes outside the tube
S.arrow((1, 0, 0), (XMAX, 0, 0), TEXT, 1.1, 7, None, 0.55)
S.arrow((0, 1, 0), (0, YMAX, 0), TEXT, 1.1, 7, None, 0.55)
S.arrow((0, 0, Z1), (0, 0, ZMAX), TEXT, 1.1, 7, None, 0.55)
tick_mark((1, 0, 0))
tick_mark((0, 1, 0))

# --- near pieces of the helix, with the direction of travel at its upper end ------------------
for run in near_runs[:-1]:
    S.line(run, THEORY, 2.6)
last = near_runs[-1]
S.line(last[:-2], THEORY, 2.6)
S.arrow(last[-12], last[-1], THEORY, 2.6, head=10)

for t in TS:
    if near(t):
        velocity_arrow(t)
for t in TS:
    S.point(helix(t), TEXT, 3.2)

# --- labels ----------------------------------------------------------------------------------
S.label((XMAX, 0, 0), "x", -4, 13, TEXT, 11.5, "middle", False, True)
S.label((0, YMAX, 0), "y", 10, 4, TEXT, 11.5, "middle", False, True)
S.label((0, 0, ZMAX), "z", -10, -4, TEXT, 11.5, "middle", False, True)
S.label((1, 0, 0), "1", 9, 15, TEXT, 10, "middle")
S.label((0, 1, 0), "1", -6, 16, TEXT, 10, "middle")
S.label((0, 0, 1), "1", -9, 4, TEXT, 10, "end")
S.label((0, 0, 2), "2", -9, 7, TEXT, 10, "end")       # a little low: the far helix crosses just above

IT_T = '<tspan font-style="italic">t</tspan> = '
S.label(helix(0), IT_T + "0", -8, -7, TEXT, 11, "end")
S.label(helix(math.pi / 2), IT_T + PI_S + "/2", -9, 4, TEXT, 11, "end")
S.label(helix(math.pi), IT_T + PI_S, 8, -6, TEXT, 11, "start")
tip32 = vadd(helix(3 * math.pi / 2), velocity(3 * math.pi / 2))
S.label(vsub(tip32, (0, 0, 0.25)), IT_T + "3" + PI_S + "/2", -8, 4, TEXT, 11, "end")
half = vsub(vadd(helix(math.pi / 2), velocity(math.pi / 2)), (0, 0, 0.25))
S.label(half, "1/2", 6, 4, TEXT, 10.5, "start")
S.label(helix(0.62), '<tspan font-style="italic">&#945;</tspan>', -4, -10, THEORY, 12.5, "end")

OUT["egri-helis-hiz-vektorleri"] = figure(
    416, 452, [P],
    "<em>x</em><sup>2</sup> + <em>y</em><sup>2</sup> = 1 silindirine sarılan "
    "&#945;(<em>t</em>) = (cos <em>t</em>, sin <em>t</em>, <em>t</em>/2) helisi ve "
    "<em>t</em> = 0, &#960;/2, &#960;, 3&#960;/2 anlarındaki hız vektörleri (turuncu oklar). "
    "Okların yatay kısmı, nokta silindiri dolandıkça dönerek yön değiştirir; her okun ucundan inen "
    "kesikli düşey parça ise hep aynı boydadır, çünkü hız vektörünün <em>z</em> koordinatı her an "
    "1/2&#8217;dir. Helisin sabit hızla yükselmesi, hızın bu değişmeyen düşey kısmında görülür.",
    aria="Silindir x^2 + y^2 = 1 uzerinde alpha(t) = (cos t, sin t, t/2) helisi; t = 0, pi/2, pi, "
         "3pi/2 anlarinda turuncu hiz oklari, vektor kisimlari (0, 1, 1/2), (-1, 0, 1/2), "
         "(0, -1, 1/2), (1, 0, 1/2); her okun ucundan 1/2 boyunda kesikli dusey parca iner")

# ============================================================ egri-helis-teget-dogrusu
# -*- coding: utf-8 -*-
# egri-helis-teget-dogrusu: the helix alpha(t) = (2 cos t, 2 sin t, t), t in [-0.6, 2.4], on the
# translucent cylinder x^2 + y^2 = 4 (z in [-1.2, 2.5]); its tangent lines u -> alpha(t) + u alpha'(t),
# u in [-1, 1], at t = 0 and t = pi/4, and the velocity arrows (0, 2, 1) and (-sqrt2, sqrt2, 1)
# drawn from alpha(0) = (2, 0, 0) and alpha(pi/4) = (sqrt2, sqrt2, pi/4).
# The camera sits at azimuth 20, elevation 35: at lower elevations the x axis and the tangent line
# through alpha(0) (which lies on the x axis) project almost onto each other, and near elevation 28
# alpha(pi/4) projects onto the y axis. From this side the helix passes behind the cylinder for
# t > 110 degrees; that end is painted between the back and the front half of the cylinder.
import math

AZ, EL = 20.0, 35.0
R2 = math.sqrt(2.0)
Z0, Z1 = -1.2, 2.5                   # height range of the drawn cylinder
T0, T1 = -0.6, 2.4                   # parameter range of the helix
T_BACK = math.radians(AZ + 90.0)     # helix goes behind the cylinder's silhouette here
XMAX, YMAX, ZMAX = 4.0, 3.6, 4.25    # axis lengths; x = 4.0 keeps the x arrowhead off the bottom rim

P = space_panel(20, 14, 360, (-2.85, 3.85), (-2.35, 3.8))
S = Space(P, Camera(azimuth=AZ, elevation=EL, scale=1.0))


def helix(t):
    return (2.0 * math.cos(t), 2.0 * math.sin(t), t)


def cyl(u, v):
    return (2.0 * math.cos(u), 2.0 * math.sin(u), v)


def rim(z):
    return lambda u: (2.0 * math.cos(u), 2.0 * math.sin(u), z)


A0, A1 = helix(0.0), helix(math.pi / 4)
V0, V1 = (0.0, 2.0, 1.0), (-R2, R2, 1.0)
BACK = (math.radians(AZ + 90.0), math.radians(AZ + 270.0))
FRONT = (math.radians(AZ - 90.0), math.radians(AZ + 90.0))
O = (0.0, 0.0, 0.0)
AX_OP = 0.55

# --- back half of the cylinder, its rims, and the part of the helix behind the front face -------
S.surface(cyl, BACK, (Z0, Z1), nu=18, nv=1, fill=TEXT, stroke="none", opacity=(0.03, 0.09),
          stroke_width=0, stroke_opacity=0)
# The hidden bottom rim is left out: in this view it runs through the y tick labels 1 and 2
# and through the crossing of the y axis with the tangent line at pi/4.
S.curve(rim(Z1), BACK[0], BACK[1], TEXT, 1.0, 90, None, 0.35)      # seen through the open top
S.curve(helix, T_BACK, T1, THEORY, 2.4, 40, None, 0.42)

# --- axis pieces inside the cylinder -------------------------------------------------------------
S.line([O, (2.0, 0.0, 0.0)], TEXT, 1.1, None, AX_OP)
S.line([O, (0.0, 2.0, 0.0)], TEXT, 1.1, None, AX_OP)
S.arrow(O, (0.0, 0.0, ZMAX), TEXT, 1.1, 7.0, None, AX_OP)

# --- front half of the cylinder: faces, rims, silhouette rulings ---------------------------------
S.surface(cyl, FRONT, (Z0, Z1), nu=18, nv=1, fill=TEXT, stroke="none", opacity=(0.03, 0.09),
          stroke_width=0, stroke_opacity=0)
S.curve(rim(Z0), FRONT[0], FRONT[1], TEXT, 1.0, 90, None, 0.45)
S.curve(rim(Z1), FRONT[0], FRONT[1], TEXT, 1.0, 90, None, 0.45)
for u in FRONT:
    S.line([cyl(u, Z0), cyl(u, Z1)], TEXT, 1.0, None, 0.45)

# --- axis pieces outside the cylinder, labels, ticks ---------------------------------------------
S.arrow((2.0, 0.0, 0.0), (XMAX, 0.0, 0.0), TEXT, 1.1, 7.0, None, AX_OP)
S.arrow((0.0, 2.0, 0.0), (0.0, YMAX, 0.0), TEXT, 1.1, 7.0, None, AX_OP)
S.label((XMAX, 0.0, 0.0), "x", -9, 6, TEXT, 11.5, "middle", False, True)
S.label((0.0, YMAX, 0.0), "y", 10, 4, TEXT, 11.5, "middle", False, True)
S.label((0.0, 0.0, ZMAX), "z", 0, -7, TEXT, 11.5, "middle", False, True)
S.ticks("x", (1,))
S.ticks("y", (1,), offset=(0, -6))
S.ticks("y", (2,), offset=(-5, 13))     # nudged left, off the silhouette ruling at x-page = 2
S.ticks("y", (3,))
S.ticks("z", (1, 2, 3), offset=(-9, 7))

# --- tangent lines (u in [-1, 1]) under the helix, so the curve stays blue where they touch -------
for A, V in ((A0, V0), (A1, V1)):
    S.line([vadd(A, vscale(-1.0, V)), vadd(A, V)], PRACTICE, 1.7, None, 0.6)

# --- the helix in front, with a direction arrowhead ----------------------------------------------
S.curve(helix, T0, T_BACK, THEORY, 2.8, 160)
S.arrow(helix(1.38), helix(1.46), THEORY, 2.8, head=10)

# --- velocity arrows (u in [0, 1]) on top ----------------------------------------------------------
for A, V in ((A0, V0), (A1, V1)):
    S.arrow(A, vadd(A, V), PRACTICE, 2.6, head=9)
S.point(A0, TEXT, 3.8)
S.point(A1, TEXT, 3.8)

# --- labels -------------------------------------------------------------------------------------
IT_T = '<tspan font-style="italic">t</tspan>'
IT_A = '<tspan font-style="italic">&#945;</tspan>'
S.label(A0, IT_T + " = 0", -8, -7, TEXT, 11.5, "end")
S.label(A1, IT_T + " = &#960;/4", -9, 0, TEXT, 11.5, "end")
S.label(vadd(A0, vscale(0.75, V0)), IT_A + PRIME + "(0)", 0, 18, PRACTICE, 11.5, "middle")
S.label(vadd(A1, V1), IT_A + PRIME + "(&#960;/4)", 7, 5, PRACTICE, 11.5, "start")
S.label(helix(T_BACK), IT_A, 8, 4, THEORY, 12.5, "start")
S.label(cyl(FRONT[1], Z1), '<tspan font-style="italic">x</tspan>' + sups("2") + " + "
        + '<tspan font-style="italic">y</tspan>' + sups("2") + " = 4", 8, -6, TEXT, 11, "start")

OUT["egri-helis-teget-dogrusu"] = figure(
    400, 370, [P],
    "<em>x</em><sup>2</sup> + <em>y</em><sup>2</sup> = 4 silindiri üzerindeki "
    "<em>&#945;</em>(<em>t</em>) = (2 cos <em>t</em>, 2 sin <em>t</em>, <em>t</em>) helisi ve "
    "<em>t</em> = 0, <em>t</em> = &#960;/4 anlarındaki teğet doğruları "
    "(&#8722;1 &#8804; <em>u</em> &#8804; 1 için açık turuncu). Koyu turuncu oklar hız "
    "vektörleridir; vektör kısımları (0, 2, 1) ve (&#8722;&#8730;2, &#8730;2, 1) olup her biri kendi "
    "teğet doğrusunun 0 &#8804; <em>u</em> &#8804; 1 parçası üzerinde durur. Her doğru eğrinin "
    "noktasından eğriyle aynı hızla geçer ama silindire yalnızca o noktada dokunur: doğru boyunca "
    "<em>x</em><sup>2</sup> + <em>y</em><sup>2</sup> = 4 + 4<em>u</em><sup>2</sup> olduğundan "
    "<em>u</em> &#8800; 0 için silindirin dışında kalır. Helisin silindirin arkasına geçen ucu "
    "soluk çizilmiştir.",
    aria="x^2 + y^2 = 4 silindiri uzerinde alpha(t) = (2 cos t, 2 sin t, t) helisi; t = 0 ve "
         "t = pi/4 noktalarindaki teget dogrulari, u -1 ile 1 arasinda; hiz oklari (0, 2, 1) ve "
         "(-1,414; 1,414; 1). Dogrular silindire yalnizca bu noktalarda dokunur.")

# ============================================================ egri-hiperbol-uzerinde-yukselen
# -*- coding: utf-8 -*-
# egri-hiperbol-uzerinde-yukselen: the curve alpha(t) = (e^t, e^-t, sqrt(2) t) climbing the vertical
# wall that stands on the branch x > 0 of the hyperbola xy = 1. The branch is drawn dashed on the
# floor for x in [0.34, 2.95]; the wall is a very faint blue strip with z in [-1.6, 1.6]; the curve
# is drawn for t in [-1.08, 1.08] with direction arrows. The points at t = -1, 0, 1 are marked, each
# with a dashed vertical guide down (or up) to its shadow on the hyperbola.
import math

R2 = math.sqrt(2.0)
HX0, HX1 = 0.34, 2.95        # drawn piece of the hyperbola branch (range of x)
WZ0, WZ1 = -1.6, 1.6         # height range of the drawn wall
T0, T1 = -1.08, 1.08         # drawn parameter range of the curve
UA, UB = math.log(HX0), math.log(HX1)


def alpha(t):
    return (math.exp(t), math.exp(-t), R2 * t)


def branch(u, z=0.0):
    """Point of the wall over the branch, parametrised by u = log x (even spacing along the arc)."""
    return (math.exp(u), math.exp(-u), z)


def ital(s):
    return f'<tspan font-style="italic">{s}</tspan>'


def mfmt(v):
    return fmt(v).replace("-", MINUS_S)


P = space_panel(20, 14, 360, (-2.45, 3.55), (-2.95, 2.35))
S = Space(P, Camera(azimuth=30, elevation=27, scale=1.0))

# --- floor grid and axes (the axes lie behind the wall from this viewpoint) ------------------
S.floor_grid((0, 3), (0, 3), n=3, opacity=0.13)
S.axes(3.7, 3.7, 1.85, zmin=-2.0)
S.ticks("x", (1, 3), offset=(-12, 6))
S.ticks("x", (2,), offset=(-13, 5))
S.ticks("y", (1, 2, 3), offset=(0, -6))
S.ticks("z", (-1, 1), fmt_=mfmt)

# --- the wall over the branch: a very faint blue strip with thin edges -----------------------
US = [UA + (UB - UA) * k / 60 for k in range(61)]
S.polygon([branch(u, WZ0) for u in US] + [branch(u, WZ1) for u in reversed(US)], THEORY, 0.08)
S.line([branch(u, WZ1) for u in US], THEORY, 0.8, None, 0.35)
S.line([branch(u, WZ0) for u in US], THEORY, 0.8, None, 0.35)
S.line([branch(UA, WZ0), branch(UA, WZ1)], THEORY, 0.8, None, 0.35)
S.line([branch(UB, WZ0), branch(UB, WZ1)], THEORY, 0.8, None, 0.35)

# --- the hyperbola branch on the floor, dashed grey ------------------------------------------
S.line([branch(u) for u in US], TEXT, 1.4, "5 4", 0.65)

# --- vertical guides from the marked points to their shadows on the hyperbola ---------------
A, B, C = alpha(-1.0), alpha(0.0), alpha(1.0)
for Q in (A, C):
    S.guide([Q, (Q[0], Q[1], 0.0)], TEXT, 0.6, 1.0)
    S.point((Q[0], Q[1], 0.0), TEXT, 2.3)

# --- the curve and its direction arrows ------------------------------------------------------
S.curve(alpha, T0, T1, PRACTICE, 2.8, 160)
for t in (-0.5, 0.5):
    S.arrow(alpha(t - 0.02), alpha(t + 0.07), PRACTICE, 2.8, head=10)

S.point(A, TEXT, 3.6)
S.point(B, TEXT, 3.6)
S.point(C, TEXT, 3.6)

# --- labels ----------------------------------------------------------------------------------
T = ital("t")
S.label(C, T + " = 1", -2, -12, TEXT, 11.5, "end")
S.label(B, T + " = 0", 0, 26, TEXT, 11.5, "middle")
# below the wall's lower edge: to the right of A the end of the curve runs down-right
S.label(A, T + " = " + MINUS_S + "1", 0, 29, TEXT, 11.5, "middle")
# right of the branch's end, outside the wall and below the y axis (the floor near the other
# end is crowded by grid lines and the guide of t = 1)
S.label(branch(UA), ital("xy") + " = 1", 9, 20, TEXT, 11, "start")
S.label((0.6, 2.4, 1.6), ital("&#945;") + "(" + T + ") = (" + ital("e") + sups(T) + ", " + ital("e")
        + sups(MINUS_S + T) + ", &#8730;2 " + T + ")", 0, -18, PRACTICE, 11.5, "middle")

OUT["egri-hiperbol-uzerinde-yukselen"] = figure(
    400, 345, [P],
    "<em>&#945;</em>(<em>t</em>) = (<em>e</em><sup><em>t</em></sup>, <em>e</em><sup>&#8722;<em>t</em></sup>, "
    "&#8730;2 <em>t</em>) eğrisi, <em>xy</em> = 1 hiperbolünün <em>x</em> &gt; 0 kolu üzerine dikilen "
    "soluk mavi duvarda ilerler; kesikli dikey kılavuzlar, noktaların <em>xy</em> düzlemine "
    "izdüşümlerinin bu kolda olduğunu gösterir. <em>t</em> = &#8722;1, 0, 1 anlarında yükseklik "
    "&#8722;1,414; 0; 1,414 olur, yani her birim zamanda &#8730;2 kadar artar: eğri helis gibi sabit "
    "hızla yükselir, yalnızca altındaki eğri daire değil hiperboldür. Oklar hareket yönünü gösterir; "
    "<em>t</em> arttıkça izdüşüm kolun <em>y</em> eksenine yakın ucundan <em>x</em> eksenine yakın "
    "ucuna doğru kayar; eğri de kolun her noktasının üstünden tam bir kez geçer.",
    aria="Curve alpha(t) = (e^t, e^-t, sqrt(2) t) on the faint vertical wall over the branch x > 0 "
         "of the hyperbola xy = 1; the points at t = -1, 0, 1 with dashed vertical guides to the "
         "hyperbola, and arrows showing the direction of motion")

# ============================================================ egri-hiperbolun-iki-kolu
# -*- coding: utf-8 -*-
# egri-hiperbolun-iki-kolu — the level set C: x^2 - y^2 = 1 for y in [-2.5, 2.5]: the right
# branch C1 (x >= 1, thick blue) and the left branch C2 (x <= -1, thick orange), the dashed
# gray asymptotes y = x and y = -x, and the faintly shaded strip -1 < x < 1 that C never
# enters. On C1 the parametrization beta(t) = (cosh t, sinh t) is marked at t = -1, 0, 1
# together with its velocity vectors beta'(t) = (sinh t, cosh t), drawn at half scale.

import math

XR, YR = (-3.1, 3.3), (-2.8, 2.95)
p = cplane(18, 34, 364, XR, YR)
YEND = 2.5                      # the branches are drawn for |y| <= 2.5
ASY = 2.72                      # the asymptotes run a little past the branch ends
T_END = math.asinh(YEND)
HALF = 0.5                      # velocity vectors are drawn at half scale


def ital(s):
    return '<tspan font-style="italic">' + s + '</tspan>'


def halo_label(x, y, s, dx=0, dy=0, color=TEXT, size=11, anchor="start", opacity=1.0):
    """Label with a page-background halo, for spots where a faint line passes close by."""
    px, py = p.X(x) + dx, p.Y(y) + dy
    p.add(f'<text x="{px:.1f}" y="{py:.1f}" fill="{BG}" stroke="{BG}" stroke-width="4" '
          f'stroke-linejoin="round" font-size="{size}" text-anchor="{anchor}">{s}</text>')
    p.add(f'<text x="{px:.1f}" y="{py:.1f}" fill="{color}" font-size="{size}" '
          f'text-anchor="{anchor}" opacity="{opacity}">{s}</text>')


def beta(t):
    return (math.cosh(t), math.sinh(t))


def beta_prime(t):
    return (math.sinh(t), math.cosh(t))


def head_on_curve(t, color, size=11.0):
    """Filled arrowhead centred on beta(t), pointing along the direction of motion."""
    x, y = beta(t)
    vx, vy = beta_prime(t)
    n = math.hypot(vx, vy)
    ux, uy = vx / n, -vy / n                 # pixel direction (screen y grows downward)
    px, py = p.X(x), p.Y(y)
    tipx, tipy = px + ux * size * 0.55, py + uy * size * 0.55
    bx, by = px - ux * size * 0.45, py - uy * size * 0.45
    hw = size * 0.45
    p.add(f'<polygon points="{tipx:.1f},{tipy:.1f} {bx - uy * hw:.1f},{by + ux * hw:.1f} '
          f'{bx + uy * hw:.1f},{by - ux * hw:.1f}" fill="{color}"/>')


# the strip -1 < x < 1 that C never enters
rect(p, -1.0, 1.0, YR[0], YR[1], TEXT, 0.07)

# asymptotes
p.line([(-ASY, -ASY), (ASY, ASY)], TEXT, 1.1, "5 4", 0.55)
p.line([(-ASY, ASY), (ASY, -ASY)], TEXT, 1.1, "5 4", 0.55)

p.origin_axes("x", "y")

# ticks at x = -1 and x = 1; numbers sit inside the strip so the branches do not cross them
oy = p.Y(0)
for v in (-1, 1):
    X = p.X(v)
    p.add(f'<line x1="{X:.1f}" y1="{oy - 3:.1f}" x2="{X:.1f}" y2="{oy + 3:.1f}" '
          f'stroke="{TEXT}" stroke-width="1" opacity="0.7"/>')
p.text_px(p.X(-1) + 4, oy + 15, MINUS_S + "1", TEXT, 11, "start")
p.text_px(p.X(1) - 4, oy + 15, "1", TEXT, 11, "end")

# the two branches
N = 260
C1 = [beta(-T_END + 2 * T_END * k / N) for k in range(N + 1)]
C2 = [(-x, y) for x, y in C1]
p.line(C1, THEORY, 3.4, None, 0.62)
p.line(C2, PRACTICE, 3.4, None, 0.62)

# direction of motion on C1 (t increasing, upward)
head_on_curve(-1.47, THEORY, 11.0)

# marked instants t = -1, 0, 1 with half-scale velocity vectors
TS = (-1.0, 0.0, 1.0)
for t in TS:
    x, y = beta(t)
    p.add(f'<circle cx="{p.X(x):.1f}" cy="{p.Y(y):.1f}" r="5.6" fill="{BG}"/>')
for t in TS:
    b, v = beta(t), beta_prime(t)
    p.arrow(b, (b[0] + HALF * v[0], b[1] + HALF * v[1]), THEORY, 2.0, head=8)
for t in TS:
    dot(p, beta(t), TEXT, 3.4)

# point labels: t value, coordinates underneath
p.label(1.543, 1.175, ital("t") + " = 1", 11, 4, TEXT, 11.5, "start")
p.label(1.543, 1.175, "(1,543; 1,175)", 11, 17, TEXT, 10.5, "start")
p.label(1.0, 0.0, ital("t") + " = 0", 10, -6, TEXT, 11.5, "start")
p.label(1.0, 0.0, "(1, 0)", 10, 15, TEXT, 10.5, "start")
p.label(1.543, -1.175, ital("t") + " = " + MINUS_S + "1", 14, -5, TEXT, 11.5, "start")
p.label(1.543, -1.175, "(1,543; " + MINUS_S + "1,175)", 14, 8, TEXT, 10.5, "start")

# velocity labels
B1 = ital("&#946;") + PRIME
p.label(1.93, 1.65, B1 + "(1)", 12, 4, THEORY, 11.5, "start")
p.label(1.0, 0.28, B1 + "(0)", -6, 4, THEORY, 11.5, "end")
p.label(1.2, -0.62, B1 + "(" + MINUS_S + "1)", 14, 4, THEORY, 11.5, "start")

# branch names
p.label(math.sqrt(1 + 2.2 ** 2), 2.2, ital("C") + subs("1"), 10, 5, THEORY, 13, "start")
p.label(-math.sqrt(1 + 2.2 ** 2), 2.2, ital("C") + subs("2"), -10, 5, PRACTICE, 13, "end")

# asymptote names, above the upper ends
p.label(2.6, 2.72, ital("y") + " = " + ital("x"), 0, -3, TEXT, 11, "end")
p.label(-2.6, 2.72, ital("y") + " = " + MINUS_S + ital("x"), 0, -3, TEXT, 11, "start")

OUT["egri-hiperbolun-iki-kolu"] = figure(
    400, 372, [p],
    "<em>r</em> = 1 için <em>x</em><sup>2</sup> &#8722; <em>y</em><sup>2</sup> = 1 hiperbolü, kesikli "
    "çizilen <em>y</em> = <em>x</em> ve <em>y</em> = &#8722;<em>x</em> asimptotlarına yaklaşan iki "
    "koldan oluşur: sağdaki <em>C</em><sub>1</sub> (mavi) ve soldaki <em>C</em><sub>2</sub> (turuncu). "
    "&#8722;1 &lt; <em>x</em> &lt; 1 şeridine (gri) hiperbolün hiçbir noktası girmez; bu yüzden "
    "hiperbol üzerinde kalarak bir koldan ötekine geçilemez. "
    "<em>&#946;</em>(<em>t</em>) = (cosh <em>t</em>, sinh <em>t</em>) noktası <em>C</em><sub>1</sub>'i "
    "aşağıdan yukarı dolaşır; <em>t</em> = &#8722;1, 0, 1 anlarındaki hız vektörleri yarı ölçekte "
    "çizilmiştir. Hızın ikinci koordinatı cosh <em>t</em> &#8805; 1 olduğundan hız hiçbir anda "
    "sıfır olmaz.",
    aria="r = 1 icin x^2 - y^2 = 1 hiperbolu, y -2,5 ile 2,5 arasinda: sag kol C1 mavi, sol kol C2 turuncu, "
         "kesikli gri asimptotlar y = x ve y = -x, x = -1 ile x = 1 arasindaki dusey serit soluk gri "
         "tarali. C1 uzerinde "
         "beta(t) = (cosh t, sinh t) icin t = -1, 0, 1 noktalari (1,543; -1,175), (1, 0), "
         "(1,543; 1,175) ve bu noktalardaki yari olcekli hiz vektorleri (-1,175; 1,543), (0, 1), "
         "(1,175; 1,543); C1 uzerinde yukari yon oku.")

# ============================================================ egri-kesen-vektor-limiti
# -*- coding: utf-8 -*-
# Scaled secant vectors of alpha(t) = (t, t^2, 0) at t = 1 approaching the velocity alpha'(1).
#   secant chords:  (1,1) -> alpha(1 + dt) = (2,4), (3/2,9/4), (5/4,25/16)      (thin dashed grey)
#   scaled secants: (1/dt)(alpha(1+dt) - alpha(1)) = (1, 2 + dt)  -> tips (2,4), (2,7/2), (2,13/4)
#   velocity:       alpha'(1) = (1, 2) applied at (1,1)           -> tip (2,3), tangent y = 2x - 1


def ital(s):
    """Italic run inside an SVG <text> — variable names."""
    return f'<tspan font-style="italic">{s}</tspan>'


def group(p, opacity):
    """Open an opacity group so a shaft and its head fade as one shape (no double-dark overlap)."""
    p.add(f'<g opacity="{opacity}">')


def end_group(p):
    p.add('</g>')


ALPHA, CAP_DELTA = "&#945;", "&#916;"
X, Y, T = ital("x"), ital("y"), ital("t")
DT = CAP_DELTA + T

A1 = (1.0, 1.0)
# (dt label, chord end alpha(1 + dt), scaled-secant tip, arrow opacity, label opacity, label dy)
SECANTS = [
    ("1",   (2.0, 4.0),     (2.0, 4.0),  0.45, 0.80, 5),
    ("1/2", (1.5, 2.25),    (2.0, 3.5),  0.70, 0.90, 4),
    ("1/4", (1.25, 1.5625), (2.0, 3.25), 1.00, 1.00, 9),
]
V_TIP = (2.0, 3.0)

p = Plot(40, 18, 322, 262, (-0.22, 2.72), (-0.38, 5.02))
p.origin_axes(X, Y, xticks=(1, 2), yticks=(1, 2, 3, 4), xfmt=tfmt, yfmt=tfmt)

# all scaled secants have first component 1, so their tips sit on the line x = 2
guide(p, [(2.0, 0.0), (2.0, 2.9)], TEXT, 0.35)   # stops under the velocity arrowhead

# tangent line y = 2x - 1 (faint, dashed); beyond (1,1) it runs under the velocity arrow
p.line([(0.31, 2 * 0.31 - 1), V_TIP], PRACTICE, 1.3, "5 4", 0.55)

# the route: parabola y = x^2 on [0, 2.2]
curve(p, lambda x: x * x, 0.0, 2.2, TEXT, 1.8, opacity=0.78)

# scaled secant vectors, faint (dt = 1) to strong (dt = 1/4)
for _, _, tip, op, _, _ in SECANTS:
    group(p, op)
    p.arrow(A1, tip, THEORY, 1.8, head=7.5)
    end_group(p)

# the velocity vector alpha'(1) = (1, 2) at (1, 1)
p.arrow(A1, V_TIP, PRACTICE, 2.8, head=10)

# the secant chords themselves, drawn thin over the arrows they lie on
for _, end, _, _, _, _ in SECANTS:
    p.line([A1, end], TEXT, 0.85, "3 2.5", 0.6)

# chord end points alpha(3/2), alpha(5/4) on the parabola (alpha(2) is the tip of the dt = 1 arrow), then alpha(1)
for _, end, tip, _, _, _ in SECANTS:
    if end != tip:
        dot(p, end, TEXT, 2.5)
dot(p, A1, TEXT, 3.8)

# labels
p.label(*A1, ALPHA + "(1) = (1, 1)", -9, -7, TEXT, 11, "end")
p.label(2.0, 4.0, ALPHA + "(2) = (2, 4)", -9, -6, TEXT, 11, "end")
p.label(2.2, 2.2 ** 2, Y + " = " + X + sups("2"), 7, 4, TEXT, 11)

for name, _, tip, _, lop, dy in SECANTS:
    group(p, lop)
    p.label(tip[0], tip[1], DT + " = " + name, 8, dy, THEORY, 11)
    end_group(p)

p.label(1.62, 2 * 1.62 - 1, ALPHA + PRIME + "(1)", 9, 15, PRACTICE, 12, bold=True)
group(p, 0.8)
p.label(0.86, 0.3, Y + " = 2" + X + " " + MINUS_S + " 1", 0, 0, PRACTICE, 10.5)
end_group(p)

OUT["egri-kesen-vektor-limiti"] = figure(
    400, 300, [p],
    "<em>xy</em> düzlemindeki <em>y</em> = <em>x</em><sup>2</sup> rotası üzerinde, &#945;(1) = (1, 1) noktasından çıkan "
    "ve soluktan belirgine giden mavi oklar, &#916;<em>t</em> = 1, 1/2, 1/4 için ölçeklenmiş kesen vektörlerdir; "
    "vektör kısımları (1, 2 + &#916;<em>t</em>)'dir. "
    "Her ok, &#945;(1)'i parabol üzerindeki &#945;(1 + &#916;<em>t</em>) noktasına, yani (2, 4), (3/2, 9/4) ya da "
    "(5/4, 25/16) noktasına bağlayan kesikli gri kesen boyunca uzanır. "
    "&#916;<em>t</em> küçüldükçe kesenler kısalıp sıfıra gider, ama 1/&#916;<em>t</em> ile büyütülen okların uçları "
    "<em>x</em> = 2 doğrusu üzerinde (2, 4), (2, 7/2), (2, 13/4) diye inerek (2, 3)'e yaklaşır. "
    "Limit, vektör kısmı (1, 2) olan turuncu hız vektörü &#945;&#8242;(1)'dir; bu ok, parabolün (1, 1)'deki "
    "teğeti olan <em>y</em> = 2<em>x</em> &#8722; 1 doğrusu üzerinde yatar.",
    aria="y = x^2 parabolu ve (1,1) noktasi; bu noktadan cikan, uclari (2,4), (2,3.5) ve (2,3.25) olan uc mavi "
         "olceklenmis kesen vektor, (2,3) noktasinda biten turuncu hiz vektoru ve kesikli teget dogru y = 2x - 1",
)

# ============================================================ egri-silindir-kure-kesisimi
# -*- coding: utf-8 -*-
# egri-silindir-kure-kesisimi: the sphere Sigma: x^2 + y^2 + z^2 = 4 (grey), the cylinder
# C: (x - 1)^2 + y^2 = 1 for -2 <= z <= 2 (blue) and their intersection, the closed curve
# alpha(t) = (1 + cos t, sin t, 2 sin(t/2)), 0 <= t <= 4 pi (orange, with direction arrows).
# The sphere is drawn as its silhouette disk plus a latitude/longitude grid; grid lines and
# curve pieces on the far side of a surface are faded (the curve: far side of the sphere).
# A low elevation keeps the two loops of the figure eight equally open.

_AZ, _EL = 30.0, 16.0
_cam = Camera(azimuth=_AZ, elevation=_EL, scale=1.0)
_P = space_panel(10, 10, 427, (-3.2, 2.9), (-2.75, 3.05))
_S = Space(_P, _cam)
_D = _cam.d                    # unit vector toward the viewer
_TWO_PI = 2.0 * math.pi


def _alpha(t):
    return (1.0 + math.cos(t), math.sin(t), 2.0 * math.sin(t / 2.0))


def _runs(pts, front):
    """Cut a sampled polyline into maximal (is_front, points) runs; runs share end points."""
    runs = []
    for q in pts:
        f = front(q)
        if not runs or runs[-1][0] != f:
            runs.append((f, ([runs[-1][1][-1]] if runs else []) + [q]))
        else:
            runs[-1][1].append(q)
    return runs


def _sphere_front(q):
    return vdot(q, _D) >= 0.0


def _cyl_front(q):
    return (q[0] - 1.0) * _D[0] + q[1] * _D[1] >= 0.0


def _draw(pts, front, which, color, width, opacity, dash=None):
    """Draw only the front (which=True) or back (which=False) runs of a polyline."""
    for f, run in _runs(pts, front):
        if f == which and len(run) > 1:
            _S.line(run, color, width, dash, opacity)


def _sample(f, t0, t1, n):
    return [f(t0 + (t1 - t0) * k / n) for k in range(n + 1)]


def _txt(q, s, dx, dy, color=TEXT, size=11.0, anchor="start", italic=False, opacity=1.0):
    """Label at a space point with a thin page-coloured halo, so grid lines behind it break."""
    X, Y = _S.pt(q)
    st = ' font-style="italic"' if italic else ""
    op = f' opacity="{opacity}"' if opacity < 1.0 else ""
    _P.add(f'<text x="{_P.X(X) + dx:.1f}" y="{_P.Y(Y) + dy:.1f}" fill="{color}" font-size="{size}" '
           f'text-anchor="{anchor}"{st}{op} stroke="{BG}" stroke-width="3.2" stroke-linejoin="round" '
           f'paint-order="stroke">{s}</text>')


def _head(t, color=PRACTICE, size=10.0, opacity=1.0):
    """Arrowhead centred on alpha(t), pointing along the projected direction of travel."""
    a, b = _S.pt(_alpha(t - 0.03)), _S.pt(_alpha(t + 0.03))
    x0, y0, x1, y1 = _P.X(a[0]), _P.Y(a[1]), _P.X(b[0]), _P.Y(b[1])
    L = math.hypot(x1 - x0, y1 - y0)
    ux, uy = (x1 - x0) / L, (y1 - y0) / L
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    tx, ty = cx + ux * size * 0.5, cy + uy * size * 0.5
    px, py, hw = -uy, ux, size * 0.42
    pts = (f"{tx:.1f},{ty:.1f} {tx - ux * size + px * hw:.1f},{ty - uy * size + py * hw:.1f} "
           f"{tx - ux * size - px * hw:.1f},{ty - uy * size - py * hw:.1f}")
    _P.add(f'<polygon points="{pts}" fill="{color}" opacity="{opacity}"/>')


def _sph(u, v):
    return (2 * math.cos(v) * math.cos(u), 2 * math.cos(v) * math.sin(u), 2 * math.sin(v))


def _cyl(u, z):
    return (1 + math.cos(u), math.sin(u), z)


# --- sphere: silhouette disk and grid ------------------------------------------------------
_ox, _oy = _S.pt((0.0, 0.0, 0.0))
_P.add(f'<circle cx="{_P.X(_ox):.1f}" cy="{_P.Y(_oy):.1f}" r="{_P.R(2.0):.1f}" fill="{TEXT}" '
       f'fill-opacity="0.045" stroke="{TEXT}" stroke-width="1.0" stroke-opacity="0.5"/>')
_meridians = [_sample(lambda v, u=math.radians(a): _sph(u, v), -math.pi / 2, math.pi / 2, 48)
              for a in range(0, 360, 30)]
_parallels = [_sample(lambda u, v=math.radians(b): _sph(u, v), 0.0, _TWO_PI, 120)
              for b in (-60, -30, 0, 30, 60)]

# --- cylinder: rulings every 45 degrees and the two rims -----------------------------------
_rulings = [[_cyl(math.radians(a), -2.0), _cyl(math.radians(a), 2.0)] for a in range(0, 360, 45)]
_rims = [_sample(lambda u, z=z: _cyl(u, z), 0.0, _TWO_PI, 120) for z in (-2.0, 2.0)]

# back grid lines first
for m in _meridians + _parallels:
    _draw(m, _sphere_front, False, TEXT, 0.7, 0.13)
for r in _rulings:
    if not _cyl_front(r[0]):
        _S.line(r, THEORY, 0.7, None, 0.2)
for ring in _rims:
    _draw(ring, _cyl_front, False, THEORY, 1.0, 0.5)

# translucent cylinder wall (shaded, no edges)
_S.surface(_cyl, (0.0, _TWO_PI), (-2.0, 2.0), nu=48, nv=1,
           fill=THEORY, stroke=THEORY, opacity=(0.05, 0.13), stroke_width=0, stroke_opacity=0)

# silhouette rulings of the cylinder
for a in (_AZ + 90.0, _AZ - 90.0):
    _S.line([_cyl(math.radians(a), -2.0), _cyl(math.radians(a), 2.0)], THEORY, 1.0, None, 0.65)

# front grid lines
for m in _meridians + _parallels:
    _draw(m, _sphere_front, True, TEXT, 0.7, 0.26)
for r in _rulings:
    if _cyl_front(r[0]):
        _S.line(r, THEORY, 0.7, None, 0.38)
for ring in _rims:
    _draw(ring, _cyl_front, True, THEORY, 1.15, 0.8)

# --- axes and ticks ------------------------------------------------------------------------
_S.axes(4.2, 3.3, 2.95, zmin=-2.0, offsets=((-4, 14), (9, 4), (-9, -3)))
# y ticks drawn by hand so their labels get the halo: the meridian through (0, 2, 0)
# runs straight down through the label "2" otherwise
for _v in (1, 2, 3):
    _S.line([(0.04, _v, 0.0), (-0.04, _v, 0.0)], TEXT, 1.0, None, 0.7)
    _txt((0.0, _v, 0.0), str(_v), 1, 14, TEXT, 10, "middle")

# --- the curve: far side of the sphere dashed and faded, near side solid -------------------
_curve = _sample(_alpha, 0.0, 2 * _TWO_PI, 1200)
_draw(_curve, _sphere_front, False, PRACTICE, 2.0, 0.75, "5 3")
_draw(_curve, _sphere_front, True, PRACTICE, 2.7, 1.0)
for _t in (0.25 * math.pi, 1.78 * math.pi, 2.25 * math.pi, 3.78 * math.pi):
    _head(_t)

# --- marked points -------------------------------------------------------------------------
_R2 = math.sqrt(2.0)
_A, _B, _N = (2.0, 0.0, 0.0), (1.0, 1.0, _R2), (0.0, 0.0, 2.0)
_E, _SP = (1.0, -1.0, _R2), (0.0, 0.0, -2.0)
_ax, _ay = _S.pt(_A)
_P.add(f'<circle cx="{_P.X(_ax):.1f}" cy="{_P.Y(_ay):.1f}" r="7" fill="none" stroke="{TEXT}" '
       f'stroke-width="1.2" opacity="0.8"/>')
for q in (_A, _B, _N, _E, _SP):
    _S.point(q, TEXT, 3.5)

_ti = '<tspan font-style="italic">t</tspan> = '
_PI_S = "&#960;"
_SQ2 = "&#8730;2"

# (2, 0, 0): t = 0 and t = 2 pi, to the left, between the upper-left branch and the x axis
_txt(_A, "(2, 0, 0)", -23, -15, TEXT, 11, "end")
_txt(_A, _ti + "0 ve 2" + _PI_S, -23, -2, TEXT, 10.5, "end", opacity=0.8)
# (1, 1, sqrt 2): t = pi/2, to the right of the cylinder's right edge
_txt(_B, "(1, 1, " + _SQ2 + ")", 12, 5, TEXT, 11, "start")
_txt(_B, _ti + _PI_S + "/2", 12, 18, TEXT, 10.5, "start", opacity=0.8)
# (0, 0, 2): t = pi, above-right of the north pole
_txt(_N, "(0, 0, 2)", 8, -10, TEXT, 11, "start")
_txt(_N, _ti + _PI_S, 8, -23, TEXT, 10.5, "start", opacity=0.8)
# (1, -1, sqrt 2): t = 3 pi / 2, to the left
_txt(_E, "(1, " + MINUS_S + "1, " + _SQ2 + ")", -13, -2, TEXT, 11, "end")
_txt(_E, _ti + "3" + _PI_S + "/2", -13, 11, TEXT, 10.5, "end", opacity=0.8)
# (0, 0, -2): t = 3 pi, below-left of the south pole, inside the cylinder's bottom opening
_txt(_SP, "(0, 0, " + MINUS_S + "2)", -14, 12, TEXT, 11, "end")
_txt(_SP, _ti + "3" + _PI_S, -14, 24, TEXT, 10.5, "end", opacity=0.8)

# surface names: C at the lower-left end of the cylinder, Sigma beside the sphere's outline
_txt(_cyl(math.radians(_AZ - 90.0), -2.0), "C", -8, 5, THEORY, 12.5, "end", italic=True)
_sig = vadd(vscale(2.0 * math.cos(math.radians(35)), _cam.r), vscale(2.0 * math.sin(math.radians(35)), _cam.u))
_txt(_sig, "&#931;", 8, 2, TEXT, 12.5, "start")

OUT["egri-silindir-kure-kesisimi"] = figure(
    440, 420, [_P],
    "Merkezi orijin, yarıçapı 2 olan &#931; küresi (gri) ile (<em>x</em> &#8722; 1)<sup>2</sup> + "
    "<em>y</em><sup>2</sup> = 1 silindiri <em>C</em> (mavi) ve bu iki yüzeyin kesişimi olan turuncu "
    "<em>&#945;</em>(<em>t</em>) = (1 + cos <em>t</em>, sin <em>t</em>, 2 sin(<em>t</em>/2)) rotası. "
    "0 &#8804; <em>t</em> &#8804; 2&#960; iken nokta üst yarıda (1, 1, &#8730;2), (0, 0, 2) ve "
    "(1, &#8722;1, &#8730;2) üzerinden, 2&#960; &#8804; <em>t</em> &#8804; 4&#960; iken alt yarıda "
    "(0, 0, &#8722;2) üzerinden dolaşır; kesikli parça kürenin arka yüzündedir. Rota (2, 0, 0) "
    "noktasında kendini keser: nokta oraya <em>t</em> = 0 ve <em>t</em> = 2&#960; anlarında, "
    "okların gösterdiği gibi iki farklı yönde gelir.",
    aria="Sphere of radius 2 centred at the origin and the cylinder (x-1)^2 + y^2 = 1 for z from -2 to 2; "
         "their intersection curve alpha(t) = (1 + cos t, sin t, 2 sin(t/2)), t from 0 to 4 pi, with "
         "direction arrows; marked points (2,0,0) at t = 0 and 2 pi where the curve crosses itself, "
         "(1,1,sqrt2) at t = pi/2, (0,0,2) at t = pi, (1,-1,sqrt2) at t = 3pi/2, (0,0,-2) at t = 3pi")

# ============================================================ egri-yeniden-parametrelendirme
# -*- coding: utf-8 -*-
# egri-yeniden-parametrelendirme — one route, two clocks.
# Route: alpha(t) = (sqrt t, t sqrt t, 1 - t), 0 < t < 4, drawn as a soft gray band with a
# direction arrow. Blue discs: alpha at t = 1, 2, 3 (equal steps of its own clock).
# Orange squares: beta(s) = alpha(s^2) = (s, s^3, 1 - s^2) at s = 1/2, 1, 3/2.
# The shared point (1, 1, 0) carries both marks.
#
# Depth cue: the route's shadow on the floor z = 0, a faint curtain between route and shadow,
# and dashed ribs at the marks. The route touches the floor exactly at (1, 1, 0).
#
# Camera: the route starts on the z axis at (0, 0, 1), so every view puts its first stretch
# near that axis. Azimuth 30-38 makes the route pass through the projected origin (misleading);
# azimuth 42-46 puts (1, 1, 0) straight below the origin. Azimuth 54 keeps the route >= 0.3
# units off the origin. Only the positive half-axes are drawn: a negative z axis would run
# alongside the route and its tick labels would collide with the marks.

import math

AZ, EL = 54, 28
CAM = Camera(azimuth=AZ, elevation=EL, scale=1.0)


def alpha(t):
    return (math.sqrt(t), t * math.sqrt(t), 1.0 - t)


def shadow(t):
    return (math.sqrt(t), t * math.sqrt(t), 0.0)


def beta(s):
    return (s, s ** 3, 1.0 - s * s)


def proj(P):
    X, Y, _ = CAM.project(P)
    return X, Y


AX_END = (2.7, 9.3, 1.9)
route = [alpha(4.0 * k / 400) for k in range(401)]
bbox = [proj(P) for P in route] + [proj((AX_END[0], 0, 0)), proj((0, AX_END[1], 0)),
                                   proj((0, 0, AX_END[2]))]
X0, X1 = min(b[0] for b in bbox), max(b[0] for b in bbox)
Y0, Y1 = min(b[1] for b in bbox), max(b[1] for b in bbox)
PAD_L, PAD_R, PAD_B, PAD_T = 0.9, 1.4, 0.5, 0.6

PW = 440
SP = space_panel(20, 20, PW, (X0 - PAD_L, X1 + PAD_R), (Y0 - PAD_B, Y1 + PAD_T))
S = Space(SP, CAM)


def ital(s):
    return '<tspan font-style="italic">' + s + "</tspan>"


def colored(s, color):
    return f'<tspan fill="{color}">{s}</tspan>'


def px(P):
    X, Y = S.pt(P)
    return SP.X(X), SP.Y(Y)


def disc_px(cx, cy, color, r):
    SP.add(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r + 1.6:.1f}" fill="{BG}"/>')
    SP.add(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{color}"/>')


def square_px(cx, cy, color, half):
    h = half + 1.6
    SP.add(f'<rect x="{cx - h:.1f}" y="{cy - h:.1f}" width="{2 * h:.1f}" height="{2 * h:.1f}" fill="{BG}"/>')
    SP.add(f'<rect x="{cx - half:.1f}" y="{cy - half:.1f}" width="{2 * half:.1f}" height="{2 * half:.1f}" '
           f'fill="{color}"/>')


def disc(P, color, r):
    disc_px(*px(P), color, r)


def square(P, color, half):
    square_px(*px(P), color, half)


T_MARKS = (2.0, 3.0)
S_MARKS = (0.5, 1.5)
common = (1.0, 1.0, 0.0)

# depth cue: curtain between the route and its floor shadow, the shadow, and ribs at the marks
curtain = [alpha(4.0 * k / 200) for k in range(201)] + [shadow(4.0 * k / 200) for k in range(200, -1, -1)]
S.polygon(curtain, TEXT, 0.05)
S.curve(shadow, 0.0, 4.0, TEXT, 1.0, samples=200, dash="4 3", opacity=0.45)
# no rib at s = 1/2: in this view that rib projects straight along the route band and only
# doubles the line
for P in [alpha(t) for t in T_MARKS] + [beta(1.5)] + [alpha(4.0)]:
    S.guide([P, (P[0], P[1], 0.0)], TEXT, 0.45)

# positive half-axes, then the route, then the marks, then the text
S.axes(*AX_END, opacity=0.5, offsets=((-10, 6), (10, 4), (-10, -4)))
S.ticks("x", (1, 2), offset=(-3, -6))
S.ticks("y", (2, 4, 6, 8), offset=(3, -8))
S.ticks("z", (1,), offset=(16, 4))

# background halo under the route: between t = 0.15 and t = 1 the floor shadow runs within a few
# pixels of the route, and the route passes in front of the x axis; the halo keeps the band clean.
# It starts at t = 0.02 so its round cap stays clear of the z axis tick at (0, 0, 1).
S.curve(alpha, 0.02, 3.93, BG, 6.4, samples=300)

# the route: one group so the band and its arrowhead share a single opacity
SP.add('<g opacity="0.42">')
S.curve(alpha, 0.0, 3.93, TEXT, 3.2, samples=300)
S.arrow(alpha(3.86), alpha(4.0), TEXT, 3.2, head=11)
SP.add("</g>")

for t in T_MARKS:
    disc(alpha(t), THEORY, 4.3)
for s in S_MARKS:
    square(beta(s), PRACTICE, 3.9)
# the shared point: an orange square with a blue disc on it
square(common, PRACTICE, 6.2)
disc(common, THEORY, 3.2)

# labels, all on the empty side of the route (the curtain lies on the other side)
S.label(beta(0.5), ital("s") + " = 1/2", -11, 4, PRACTICE, 11, "end")
S.label(common, colored(ital("t") + " = 1", THEORY) + ", " + colored(ital("s") + " = 1", PRACTICE),
        -13, 20, TEXT, 11, "end")
S.label(alpha(2.0), ital("t") + " = 2", -10, 4, THEORY, 11, "end")
S.label(beta(1.5), ital("s") + " = 3/2", -10, 5, PRACTICE, 11, "end")
S.label(alpha(3.0), ital("t") + " = 3", -10, 4, THEORY, 11, "end")

# legend, top right
LX, LY = SP.X(X1 - 3.5), SP.Y(Y1 - 0.1)
disc_px(LX, LY - 4, THEORY, 4.3)
SP.text_px(LX + 11, LY, ital("α") + "'nın saati: " + "&#916;" + ital("t") + " = 1", TEXT, 11)
square_px(LX, LY + 15, PRACTICE, 3.9)
SP.text_px(LX + 11, LY + 19, ital("β") + "'nın saati: " + "&#916;" + ital("s") + " = 1/2", TEXT, 11)

# the two parametrizations, in the empty lower-left corner (left of the route's last stretch)
FX = SP.X(proj((AX_END[0], 0, 0))[0]) - 4
FY = SP.Y(proj(alpha(4.0))[1]) - 40
t_, s_ = ital("t"), ital("s")
SP.text_px(FX, FY, ital("α") + "(" + t_ + ") = (√" + t_ + ", " + t_ + "√" + t_ + ", 1 " + MINUS_S + " " + t_
           + "),  0 &lt; " + t_ + " &lt; 4", TEXT, 11)
SP.text_px(FX, FY + 18, ital("β") + "(" + s_ + ") = " + ital("α") + "(" + s_ + sups("2") + ") = (" + s_ + ", "
           + s_ + sups("3") + ", 1 " + MINUS_S + " " + s_ + sups("2") + "),  0 &lt; " + s_ + " &lt; 2",
           TEXT, 11)

OUT["egri-yeniden-parametrelendirme"] = figure(
    480, 480, [SP],
    "Gri çizgi, <em>α</em> ile onun yeniden parametrelendirmesi "
    "<em>β</em>(<em>s</em>) = <em>α</em>(<em>s</em><sup>2</sup>) = "
    "(<em>s</em>, <em>s</em><sup>3</sup>, 1 &#8722; <em>s</em><sup>2</sup>) eğrilerinin ortak rotasıdır; "
    "kesikli eğri bu rotanın <em>z</em> = 0 düzlemindeki izdüşümüdür. Mavi yuvarlaklar <em>α</em>'nın "
    "saatiyle eşit aralıklı <em>t</em> = 1, 2, 3 anlarını, turuncu kareler <em>β</em>'nın saatiyle eşit "
    "aralıklı <em>s</em> = 1/2, 1, 3/2 anlarını gösterir; iki saat (1, 1, 0) noktasında buluşur. "
    "Başlangıçtan bu noktaya kadarki kısa parçaya <em>β</em> toplam süresinin yarısını, <em>α</em> ise "
    "yalnızca çeyreğini ayırır; bu yüzden turuncu işaretler başta sık, sonda seyrektir: <em>β</em> "
    "yolculuğun başında yavaş, sonunda hızlıdır.",
    aria="Ayni rota uzerinde iki saat: gri egri alfa(t) = (kok t, t kok t, 1 - t), t 0 ile 4 arasinda, "
         "yon oklu ve z = 0 duzlemindeki izdusumu kesikli; mavi yuvarlaklar t = 1, 2, 3, "
         "turuncu kareler beta(s) = (s, s^3, 1 - s^2) icin s = 1/2, 1, 3/2; ortak nokta (1, 1, 0) "
         "t = 1, s = 1 etiketli.")

# ============================================================ form-alan-fonksiyona
# -*- coding: utf-8 -*-
# form-alan-fonksiyona — the constant field V = U1 + U2 on the grid {-1, 0, 1}^2 and the
# numbers phi(V)(p) = p1 - p2 for phi((v1, v2)_p) = -p2 v1 + p1 v2.
# Arrows are drawn at 0.35 of their true length (stated in the caption).

SHRINK = 0.35
XR, YR = (-1.6, 1.6), (-1.6, 1.6)
p = cplane(50, 64, 300, XR, YR)
PPU = 300 / (XR[1] - XR[0])          # pixels per data unit
u = 1.0 / PPU                        # one pixel in data units
PHI = "&#966;"


def ital(s):
    return '<tspan font-style="italic">' + s + '</tspan>'


def colored(s, color):
    return '<tspan fill="' + color + '">' + s + '</tspan>'


def dim(s, a=0.72):
    return '<tspan fill-opacity="' + str(a) + '">' + s + '</tspan>'


def mfmt(v):
    return fmt(v).replace("-", MINUS_S)


# --- light grid on the integer lines (0 is carried by the axes) ------------------------
p.grid(xs=(-1, 1), ys=(-1, 1))

# --- axes through the origin; tick numbers sit on the panel edges so that they never
#     touch the value labels next to the points ------------------------------------------
p.origin_axes("x", "y")
for t in (-1, 0, 1):
    p.text_px(p.X(t), p.y0 + p.h + 17, dim(mfmt(t), 0.7), TEXT, 10.5, "middle")
    p.text_px(p.x0 - 9, p.Y(t) + 4, dim(mfmt(t), 0.7), TEXT, 10.5, "end")

# --- the zero line y = x of phi(V) = x - y ----------------------------------------------
p.line([(XR[0], YR[0]), (XR[1], YR[1])], TEXT, 1.3, "5 4", 0.55)

# its label in the empty strip right of the line's lower end; a page-coloured patch cuts
# the grid line x = -1 under the text
LAB_X, LAB_Y = -1.33, -1.54
LAB_W = 70 * u                       # rendered text is about 65 px wide
rect(p, LAB_X - 3 * u, LAB_X + LAB_W, YR[0], LAB_Y + 12 * u, BG, 1.0)
p.label(LAB_X, LAB_Y,
        dim(ital("y") + " = " + ital("x") + ":", 0.8) + "&#160;"
        + colored(ital(PHI) + "(" + ital("V") + ") = 0", PRACTICE),
        0, 0, TEXT, 11, "start")

# --- the field V(p) = (1, 1)_p at the nine grid points ----------------------------------
PTS = [(a, b) for b in (1, 0, -1) for a in (-1, 0, 1)]
for a, b in PTS:
    p.arrow((a, b), (a + SHRINK, b + SHRINK), THEORY, 2.0, head=8)
for a, b in PTS:
    dot(p, (a, b), TEXT, 3.2)

# --- phi(V)(p) = p1 - p2, lower left of every point --------------------------------------
# (dx, dy) keeps the text left of the vertical line and below the horizontal line through
# the point, and clear of the dashed diagonal through (-1,-1), (0,0), (1,1)
for a, b in PTS:
    p.label(a, b, mfmt(a - b), -20, 13, PRACTICE, 12.5, "end", True)

# --- the formulas above the panel ---------------------------------------------------------
cx = p.x0 + p.w / 2
p.text_px(cx, p.y0 - 38,
          ital("V") + " = " + ital("U") + subs("1") + " + " + ital("U") + subs("2")
          + ",&#160;&#160;&#160;"
          + ital(PHI) + "((" + ital("v") + subs("1") + ", " + ital("v") + subs("2") + ")"
          + subs(bold("p")) + ") = " + MINUS_S + ital("p") + subs("2") + ital("v") + subs("1")
          + " + " + ital("p") + subs("1") + ital("v") + subs("2"),
          TEXT, 11.5, "middle")
p.text_px(cx, p.y0 - 19,
          "sayılar: " + ital(PHI) + "(" + ital("V") + ") = " + ital("x") + " " + MINUS_S + " " + ital("y"),
          PRACTICE, 11.5, "middle")

OUT["form-alan-fonksiyona"] = figure(
    400, 395, [p],
    "<em>V</em> = <em>U</em><sub>1</sub> + <em>U</em><sub>2</sub> alanı dokuz ızgara noktasının her "
    "birinde aynı (1, 1) okunu çizer (mavi; okunaklılık için her ok gerçek uzunluğunun 0,35 katıyla "
    "çizilmiştir). Turuncu sayılar, <em>&#966;</em>((<em>v</em><sub>1</sub>, <em>v</em><sub>2</sub>)"
    "<sub><strong>p</strong></sub>) = &#8722;<em>p</em><sub>2</sub><em>v</em><sub>1</sub> + "
    "<em>p</em><sub>1</sub><em>v</em><sub>2</sub> 1-formunun her noktadaki oka verdiği değerlerdir, yani "
    "<em>&#966;</em>(<em>V</em>) = <em>x</em> &#8722; <em>y</em>: ok hiç değişmediği hâlde "
    "<em>&#966;</em>'nin katsayıları noktayla değiştiği için sayılar değişir. Kesikli "
    "<em>y</em> = <em>x</em> doğrusu üzerinde ok, <em>&#966;</em>'nin o noktadaki sıfır doğrultusu "
    "boyunca durur ve değer 0 olur.",
    aria="Duzlemde x, y icin -1, 0, 1 izgarasindaki dokuz noktada V = U1 + U2 alaninin (1, 1) yonlu "
         "mavi oklari, 0,35 katiyla kisaltilmis. Her noktanin sol altinda turuncu phi(V) = x - y "
         "degeri: ust satir (y = 1) -2, -1, 0; orta satir (y = 0) -1, 0, 1; alt satir (y = -1) 0, 1, 2. "
         "Gri kesikli y = x dogrusu uzerinde deger 0.")

# ============================================================ form-dx-okuma
# -*- coding: utf-8 -*-
# form-dx-okuma: the 1-forms dx, dy, dz read the coordinates of the vector part of
# v_p = (2, 1, 3)_p at p = (1, 2, 1). Thick arrow p -> p + v = (3, 3, 4); axis-parallel
# staircase (1,2,1) -> (3,2,1) -> (3,3,1) -> (3,3,4) with pieces 2, 1, 3.
# Colors follow teget-ayrisim: 1st coordinate PRACTICE, 2nd BASE, 3rd THEORY, whole vector TEXT.


def ital(s):
    """Italic run inside an SVG <text> — function names such as dx."""
    return f'<tspan font-style="italic">{s}</tspan>'


# Camera chosen by search + previews (_search_form_dx.py): for v = (2, 1, 3) the usual azimuths
# 20-50 either put the z-step on top of the z axis (35-55) or make the arrow almost parallel to
# it (20-30); at azimuth ~12 the arrow and the x-step line up through p. At 66/34 the arrow
# leans ~43 deg off the z-step, p stays clear of the origin and every label has room.
cam = Camera(azimuth=66, elevation=34, scale=1.0)

p = (1.0, 2.0, 1.0)
v = (2.0, 1.0, 3.0)
q = vadd(p, v)                      # (3, 3, 4)
a = (3.0, 2.0, 1.0)                 # end of the x-step
b = (3.0, 3.0, 1.0)                 # end of the y-step

# panel range from the projections of everything drawn, plus room for the labels
drawn = [(0, 0, 0), (3.5, 0, 0), (0, 3.5, 0), (0, 0, 4.5), (3, 0, 0), (0, 3, 0), (3, 3, 0), p, q, a, b]
XY = [cam.project(Q)[:2] for Q in drawn]
X0, X1 = min(t[0] for t in XY) - 0.55, max(t[0] for t in XY) + 0.6
Y0, Y1 = min(t[1] for t in XY) - 0.45, max(t[1] for t in XY) + 0.4
P = space_panel(20, 16, 360, (X0, X1), (Y0, Y1))
S = Space(P, cam)


def meet(A, B, C, D):
    """Parameter t on C-D where the projections of A-B and C-D cross, or None."""
    (ax, ay), (bx, by), (cx, cy), (dx_, dy_) = S.pt(A), S.pt(B), S.pt(C), S.pt(D)
    den = (bx - ax) * (dy_ - cy) - (by - ay) * (dx_ - cx)
    if abs(den) < 1e-12:
        return None
    s = ((cx - ax) * (dy_ - cy) - (cy - ay) * (dx_ - cx)) / den
    t = ((cx - ax) * (by - ay) - (cy - ay) * (bx - ax)) / den
    return t if (0 < s < 1 and 0 < t < 1) else None


S.floor_grid((0, 3), (0, 3), n=3, opacity=0.13)
S.axes(3.5, 3.5, 4.5)
# at this camera the x axis is nearly horizontal and the y axis steep, so the default tick-label
# offsets put the digits on the axis lines; push them further below-left
S.ticks("x", (1, 2, 3), offset=(-6, 15))
S.ticks("y", (1, 2, 3), offset=(-5, 14))
S.ticks("z", (1, 2, 3, 4))
S.drop(p)

# the staircase: x-step, y-step, z-step
S.line([p, a], PRACTICE, 2.4)
S.line([a, b], BASE, 2.4)
t = meet(p, a, b, q)
if t is not None:                   # the z-step passes in front of the x-step: open a gap in it
    zc = b[2] + t * (q[2] - b[2])
    S.line([(3.0, 3.0, zc - 0.17), (3.0, 3.0, zc + 0.17)], BG, 8.0)
S.line([b, q], THEORY, 2.4)

S.arrow(p, q, TEXT, 3.2, head=11)
S.point(p, TEXT, 4.0)

vp = bold("v") + subs(bold("p"))
# p sits between the y axis and the arrow, so only its name fits there; the coordinates of
# both ends are in the caption
S.label(p, bold("p"), 8, 4, TEXT, 11.5, "start")
S.label(q, bold("p") + " + " + bold("v"), -9, -4, TEXT, 11.5, "end")
S.label(vadd(p, vscale(0.5, v)), vp, 8, -4, TEXT, 12.5, "start")
# the x- and y-step labels each sit inside the floor-grid cell under their piece, clear of the grid lines
S.label((2.0, 2.0, 1.0), ital("dx") + "(" + vp + ") = 2", 16, 30, PRACTICE, 11, "middle")
S.label(b, ital("dy") + "(" + vp + ") = 1", 16, 30, BASE, 11, "middle")
S.label((3.0, 3.0, 3.0), ital("dz") + "(" + vp + ") = 3", -9, 4, THEORY, 11, "end")

OUT["form-dx-okuma"] = figure(
    400, int(16 + P.h + 16), [P],
    "Kalın ok, <strong>p</strong> = (1, 2, 1) noktasındaki <strong>v</strong><sub><strong>p</strong></sub> = "
    "(2, 1, 3)<sub><strong>p</strong></sub> teğet vektörüdür ve (1, 2, 1)'den (3, 3, 4)'e gider. Okun başından "
    "sonuna eksenlere paralel basamaklarla gidildiğinde önce <em>x</em> yönünde 2 (turuncu), sonra <em>y</em> "
    "yönünde 1 (yeşil), en son <em>z</em> yönünde 3 (mavi) birim yürünür. Bu üç uzunluk sırasıyla "
    "<em>dx</em>(<strong>v</strong><sub><strong>p</strong></sub>), <em>dy</em>(<strong>v</strong><sub><strong>p</strong></sub>) "
    "ve <em>dz</em>(<strong>v</strong><sub><strong>p</strong></sub>) değerleridir: her biri vektör kısmının bir "
    "koordinatını okur ve uygulama noktası <strong>p</strong>'ye bağlı değildir.",
    aria="Tangent vector v_p from p = (1, 2, 1) to p + v = (3, 3, 4) beside the axis-parallel staircase "
         "whose pieces have lengths dx(v_p) = 2, dy(v_p) = 1, dz(v_p) = 3",
)

# ============================================================ form-kritik-noktalar
# -*- coding: utf-8 -*-
# form-kritik-noktalar — the plane x = 0 for f = (1 - x^2) y + (1 - y^2) z, where f = y + z - y^2 z.
# Level curves c = -2, -1, 0, 1, 2: away from y = +-1 they are z = (c - y) / (1 - y^2).
# c = 1 is the line y = 1 together with z = 1 / (1 + y); c = -1 is the line y = -1 together with
# z = 1 / (y - 1). The critical points (y, z) = (1, 1/2) and (-1, -1/2) are where the two pieces of
# the thick level sets cross. No red token exists in the site palette, so the critical points are
# TEXT dots on a page-background ring (the course convention for points).

import math

YR, ZR = (-2.5, 2.5), (-2.0, 2.0)
p = cplane(40, 34, 320, YR, ZR)            # equal scale: 64 px per unit, frame 320 x 256
X0, X1, Y0, Y1 = p.X(YR[0]), p.X(YR[1]), p.Y(ZR[1]), p.Y(ZR[0])


def ital(s):
    return '<tspan font-style="italic">' + s + '</tspan>'


def num(v):
    return (MINUS_S + fmt(-v)) if v < 0 else fmt(v)


# ---- sampling a branch z = g(y) on an open interval, clipped exactly to the frame -------------
def safe(g, y):
    try:
        return g(y)
    except ZeroDivisionError:
        return math.inf


def inside(z):
    return ZR[0] <= z <= ZR[1]


def edge(g, a, b):
    """a is inside, b is outside (or the reverse): bisect to the frame crossing, return the inside end."""
    ia = inside(safe(g, a))
    for _ in range(60):
        m = 0.5 * (a + b)
        if inside(safe(g, m)) == ia:
            a = m
        else:
            b = m
    y = a if ia else b
    return (y, min(max(g(y), ZR[0]), ZR[1]))


def rdp(pts, tol=0.25):
    """Douglas-Peucker in pixel space, keeps the markup small."""
    if len(pts) < 3:
        return pts
    P = [(p.X(y), p.Y(z)) for y, z in pts]
    keep = [False] * len(pts)
    keep[0] = keep[-1] = True
    stack = [(0, len(pts) - 1)]
    while stack:
        i, j = stack.pop()
        (ax, ay), (bx, by) = P[i], P[j]
        L = math.hypot(bx - ax, by - ay) or 1.0
        best, k = -1.0, None
        for m in range(i + 1, j):
            d = abs((bx - ax) * (ay - P[m][1]) - (ax - P[m][0]) * (by - ay)) / L
            if d > best:
                best, k = d, m
        if k is not None and best > tol:
            keep[k] = True
            stack += [(i, k), (k, j)]
    return [q for q, f in zip(pts, keep) if f]


def branch_runs(g, ya, yb, n=4000):
    eps = 1e-9
    ys = [ya + eps + (yb - ya - 2 * eps) * k / n for k in range(n + 1)]
    runs, cur, prev = [], None, None
    for y in ys:
        ok = inside(safe(g, y))
        if ok:
            if cur is None:
                cur = [edge(g, y, prev)] if prev is not None else []
            cur.append((y, g(y)))
        elif cur is not None:
            cur.append(edge(g, prev, y))
            runs.append(cur)
            cur = None
        prev = y
    if cur:
        runs.append(cur)
    return [rdp(r) for r in runs]


def level(c):
    if c == 1:
        return lambda y: 1.0 / (1.0 + y), [(-2.5, -1.0), (-1.0, 2.5)]
    if c == -1:
        return lambda y: 1.0 / (y - 1.0), [(-2.5, 1.0), (1.0, 2.5)]
    return (lambda y, c=c: (c - y) / (1.0 - y * y)), [(-2.5, -1.0), (-1.0, 1.0), (1.0, 2.5)]


STYLE = {2: (THEORY, 1.5, 0.9), 1: (THEORY, 2.9, 1.0), 0: (TEXT, 1.6, 0.45),
         -1: (PRACTICE, 2.9, 1.0), -2: (PRACTICE, 1.5, 0.9)}

# faint unit grid
p.grid(xs=(-2, -1, 0, 1, 2), ys=(-1, 0, 1))

# thin levels first, then the thick c = 1 and c = -1 sets on top
for c in (0, 2, -2, 1, -1):
    g, spans = level(c)
    color, width, op = STYLE[c]
    for ya, yb in spans:
        for run in branch_runs(g, ya, yb):
            p.line(run, color, width, None, op)
    if c in (1, -1):
        p.line([(c, ZR[0]), (c, ZR[1])], color, width, None, op)

# frame, tick marks and numbers
p.add(f'<rect x="{X0:.1f}" y="{Y0:.1f}" width="{X1 - X0:.1f}" height="{Y1 - Y0:.1f}" fill="none" '
      f'stroke="{TEXT}" stroke-width="1.1" opacity="0.45"/>')
for v in (-2, -1, 0, 1, 2):
    X = p.X(v)
    p.add(f'<line x1="{X:.1f}" y1="{Y1:.1f}" x2="{X:.1f}" y2="{Y1 + 4:.1f}" stroke="{TEXT}" '
          f'stroke-width="1" opacity="0.6"/>')
    p.text_px(X, Y1 + 16, num(v), TEXT, 10.5, "middle")
    Y = p.Y(v)
    p.add(f'<line x1="{X0 - 4:.1f}" y1="{Y:.1f}" x2="{X0:.1f}" y2="{Y:.1f}" stroke="{TEXT}" '
          f'stroke-width="1" opacity="0.6"/>')
    p.text_px(X0 - 7, Y + 3.8, num(v), TEXT, 10.5, "end")
p.text_px(X1 + 8, Y1 + 4, "y", TEXT, 12, "start", False, True)
p.text_px(X0 - 7, Y0 - 9, "z", TEXT, 12, "end", False, True)

# level values beside the right edge, where the five outer branches leave the frame evenly spaced
for c in (2, 1, 0, -1, -2):
    color, width, op = STYLE[c]
    zc = (c - 2.5) / (1 - 2.5 * 2.5)
    p.text_px(X1 + 5, p.Y(zc) + 3.6, num(c), color, 10, "start", c in (1, -1))
p.text_px(X1 + 5, p.Y((-2 - 2.5) / (1 - 6.25)) - 10, ital("c"), TEXT, 11, "start")

# critical points
for q in ((1.0, 0.5), (-1.0, -0.5)):
    p.add(f'<circle cx="{p.X(q[0]):.1f}" cy="{p.Y(q[1]):.1f}" r="7" fill="{BG}"/>')
    dot(p, q, TEXT, 4.3)

def halo_px(px, py, s, color, size, anchor, weight=None):
    """Text on a page-background halo, so the faint grid line behind it does not cut the glyphs."""
    w = f' font-weight="{weight}"' if weight else ""
    p.add(f'<text x="{px:.1f}" y="{py:.1f}" fill="{BG}" stroke="{BG}" stroke-width="4" '
          f'stroke-linejoin="round" font-size="{size}" text-anchor="{anchor}"{w}>{s}</text>')
    p.add(f'<text x="{px:.1f}" y="{py:.1f}" fill="{color}" font-size="{size}" '
          f'text-anchor="{anchor}"{w}>{s}</text>')


# labels in the two wedges between the thick line and the thick curve; the coordinates of the
# lower point are wider (two minus signs), so that block sits a little lower to clear the curve
qx, qy = p.X(1.0), p.Y(0.5)
halo_px(qx - 9, qy - 37, "(0, 1, 1/2)", TEXT, 11, "end")
halo_px(qx - 9, qy - 22, ital("f") + " = 1", THEORY, 11, "end", 600)
rx, ry = p.X(-1.0), p.Y(-0.5)
halo_px(rx + 9, ry + 39, ital("f") + " = " + MINUS_S + "1", PRACTICE, 11, "start", 600)
halo_px(rx + 9, ry + 54, "(0, " + MINUS_S + "1, " + MINUS_S + "1/2)", TEXT, 11, "start")

# formula line above the frame
p.text_px((X0 + X1) / 2, Y0 - 9,
          ital("x") + " = 0 düzleminde&#160; " + ital("f") + " = " + ital("y") + " + " + ital("z")
          + " " + MINUS_S + " " + ital("y") + sups("2") + ital("z")
          + ",&#160;&#160;seviye eğrileri " + ital("f") + " = " + ital("c"),
          TEXT, 11.5, "middle")

OUT["form-kritik-noktalar"] = figure(
    400, 330, [p],
    "<em>x</em> = 0 düzleminde <em>f</em> = <em>y</em> + <em>z</em> &#8722; <em>y</em><sup>2</sup><em>z</em> "
    "fonksiyonunun <em>c</em> = &#8722;2, &#8722;1, 0, 1, 2 seviye eğrileri: <em>c</em> &gt; 0 için eğriler mavi, "
    "<em>c</em> &lt; 0 için turuncu, <em>c</em> = 0 için gri; sağ kenardaki sayılar eğrilerin <em>c</em> değeridir. "
    "Kalın mavi <em>f</em> = 1 kümesi <em>y</em> = 1 doğrusu ile <em>z</em> = 1/(1 + <em>y</em>) eğrisinin "
    "birleşimidir ve ikisi kritik nokta (0, 1, 1/2)'de kesişir; kalın turuncu <em>f</em> = &#8722;1 kümesi "
    "<em>y</em> = &#8722;1 doğrusu ile <em>z</em> = 1/(<em>y</em> &#8722; 1) eğrisinden oluşur ve kesişim "
    "(0, &#8722;1, &#8722;1/2)'dir. Kesişen iki eğri noktanın çevresini dört bölgeye ayırır; "
    "<em>f</em> &#8722; 1 (ya da <em>f</em> + 1) bu bölgelerde sırayla işaret değiştirdiği için "
    "kritik noktalar ekstremum değildir.",
    aria="x = 0 duzleminde f = y + z - y^2 z fonksiyonunun c = -2, -1, 0, 1, 2 seviye egrileri; "
         "pozitif c mavi, negatif c turuncu, c = 0 gri. c = 1 kumesi y = 1 dogrusu ile z = 1/(1 + y) "
         "egrisidir ve ikisi (0, 1, 1/2) kritik noktasinda kesisir; c = -1 kumesi y = -1 dogrusu ile "
         "z = 1/(y - 1) egrisidir ve ikisi (0, -1, -1/2) kritik noktasinda kesisir.")

# ============================================================ form-lineer-yaklasim
# -*- coding: utf-8 -*-
# form-lineer-yaklasim — f = x^2 y / z along the line p + t v, p = (1, 1.5, 1), v = (-0.1, 0.1, 0.2):
#   f(p + t v) = (10 - t)^2 (15 + t) / (200 (5 + t)),   value 1.5 at t = 0 and 1.08 at t = 1.
# Its tangent at t = 0 is 1.5 - 0.5 t (slope df(v_p) = -0.5). At t = 1 two rails hang from the
# guide y = 1.5: the blue one down to 1.08 (true change -0.42), the orange one down to 1.0
# (linear change -0.5). A grey bracket marks the gap 0.08 between the two end points (the error).


def g_line(t):
    """f(p + t v) for f = x^2 y / z, p = (1, 1.5, 1), v = (-0.1, 0.1, 0.2)."""
    return (10 - t) ** 2 * (15 + t) / (200 * (5 + t))


def tangent(t):
    """Tangent line of the graph at t = 0."""
    return 1.5 - 0.5 * t


# the numbers written in the figure must be the numbers of the exercise
for t, val in ((-1, 2.1175), (-0.5, 1.7763), (0, 1.5), (0.5, 1.2717), (1, 1.08), (1.5, 0.9170)):
    assert abs(g_line(t) - val) < 6e-5, (t, g_line(t))
assert abs(tangent(1) - 1.0) < 1e-12


def mfmt(v):
    """Tick label with a Turkish decimal comma and a real minus sign."""
    return tfmt(v).replace("-", MINUS_S)


def ital(s):
    """Italic run inside an SVG <text> — function and variable names."""
    return f'<tspan font-style="italic">{s}</tspan>'


def halo_text(px, py, s, color=TEXT, size=11.5, anchor="start"):
    """Text with a page-background halo so thin guide lines never cut through it."""
    p.add(f'<text x="{px:.1f}" y="{py:.1f}" fill="{BG}" stroke="{BG}" stroke-width="4" '
          f'stroke-linejoin="round" font-size="{size}" text-anchor="{anchor}">{s}</text>')
    p.add(f'<text x="{px:.1f}" y="{py:.1f}" fill="{color}" font-size="{size}" '
          f'text-anchor="{anchor}">{s}</text>')


def seg_px(x1, y1, x2, y2, color, width, dash=None, opacity=1.0, cap="butt"):
    """Straight segment given in pixel coordinates."""
    da = f' stroke-dasharray="{dash}"' if dash else ""
    p.add(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" '
          f'stroke-width="{width}"{da} opacity="{opacity}" stroke-linecap="{cap}"/>')


XT, YT = (-1, -0.5, 0, 0.5, 1, 1.5), (1, 1.5, 2)
p = Plot(48, 26, 282, 226, (-1.0, 1.5), (0.6, 2.3))
p.axes(XT, YT, "t", "değer", xfmt=mfmt, yfmt=mfmt)
B, L = p.y0 + p.h, p.x0
for t in XT:
    seg_px(p.X(t), B, p.X(t), B + 4, TEXT, 1.0, opacity=0.45)
for y in YT:
    seg_px(L - 4, p.Y(y), L, p.Y(y), TEXT, 1.0, opacity=0.45)

# 1. guides: the level y = 1.5 across the panel, and the columns t = 0 and t = 1 down to the axis
guide(p, [(-1.0, 1.5), (1.5, 1.5)], TEXT, 0.45)
guide(p, [(0.0, 0.6), (0.0, 1.5)], TEXT, 0.25)
guide(p, [(1.0, 0.6), (1.0, 1.0)], TEXT, 0.25)

# 2. the error bracket left of t = 1, below the tangent, with dotted extensions to the two points
RX = p.X(1.0)
Y108, Y100 = p.Y(1.08), p.Y(1.0)
XB = RX - 30                      # the tangent meets y = 1.08 at t = 0.84, well right of the bracket
seg_px(XB + 4.5, Y108, RX - 5, Y108, TEXT, 1.0, "1.5 2", 0.55)
seg_px(XB + 4.5, Y100, RX - 5, Y100, TEXT, 1.0, "1.5 2", 0.55)
p.add(f'<path d="M{XB + 4.5:.1f},{Y108:.1f} L{XB:.1f},{Y108:.1f} L{XB:.1f},{Y100:.1f} '
      f'L{XB + 4.5:.1f},{Y100:.1f}" fill="none" stroke="{TEXT}" stroke-width="1.5" opacity="0.8" '
      f'stroke-linejoin="round"/>')

# 3. tangent line at t = 0 (dashed, PRACTICE) and the graph (THEORY)
p.line([(-1.0, tangent(-1.0)), (1.5, tangent(1.5))], PRACTICE, 1.7, "6 4")
curve(p, g_line, -1.0, 1.5, THEORY, 2.0)

# 4. the two drops at t = 1, side by side, both hanging from y = 1.5
Y150 = p.Y(1.5)
seg_px(RX - 2.4, Y150, RX - 2.4, Y108, THEORY, 2.2)
seg_px(RX + 2.4, Y150, RX + 2.4, Y100, PRACTICE, 2.2)

# 5. points
dot(p, (0.0, 1.5), TEXT, 3.8)
dot(p, (1.0, 1.08), THEORY, 3.6)
dot(p, (1.0, 1.0), PRACTICE, 3.6)

# 6. labels
halo_text(p.X(0.0) + 7, Y150 - 8, "(0; 1,5)", TEXT, 11)
halo_text(RX + 10, p.Y(1.40) + 4, "gerçek fark = " + MINUS_S + "0,42", THEORY, 11.5)
halo_text(RX + 10, p.Y(1.24) + 4,
          ital("df") + "(" + bold("v") + subs(bold("p")) + ") = " + MINUS_S + "0,5", PRACTICE, 11.5)
halo_text(XB - 5, (Y108 + Y100) / 2 + 4, "hata = 0,08", TEXT, 11, "end")

# 7. legend in the empty upper-right region
lx, ly = 118, 44
seg_px(lx, ly - 4, lx + 22, ly - 4, THEORY, 2.0, cap="round")
p.text_px(lx + 29, ly,
          ital("f") + "(" + bold("p") + " + " + ital("t") + bold("v") + ") = (10 " + MINUS_S + " "
          + ital("t") + ")" + sups("2") + "(15 + " + ital("t") + ") / [200(5 + " + ital("t") + ")]",
          THEORY, 11)
seg_px(lx, ly + 16, lx + 22, ly + 16, PRACTICE, 1.7, "6 4", cap="round")
p.text_px(lx + 29, ly + 20, "teğet: 1,5 " + MINUS_S + " 0,5" + ital("t"), PRACTICE, 11)

OUT["form-lineer-yaklasim"] = figure(
    400, 275, [p],
    "<strong>p</strong> = (1; 1,5; 1) noktasından <strong>v</strong> = (&#8722;0,1; 0,1; 0,2) yönünde "
    "giderken <em>f</em> = <em>x</em><sup>2</sup><em>y</em>/<em>z</em>'nin aldığı değerler mavi eğridir; "
    "turuncu kesikli doğru, eğrinin <em>t</em> = 0'daki teğeti 1,5 &#8722; 0,5<em>t</em>'dir. "
    "<em>t</em> = 1'de, yani <strong>p</strong> + <strong>v</strong> noktasında, eğri 1,5'ten 1,08'e iner "
    "ve gerçek fark &#8722;0,42 olur; teğet ise 1,0'a iner ve bu düşüş, teğetin eğimi olan "
    "<em>df</em>(<strong>v</strong><sub><strong>p</strong></sub>) = &#8722;0,5'tir. "
    "İki nokta arasındaki 0,08'lik aralık lineer yaklaşımın hatasıdır: eğri teğetten ancak bükülerek "
    "ayrıldığı için bu aralık, adım küçüldükçe adımın kendisinden çok daha hızlı küçülür.",
    aria="t eksenine gore f(p + tv) = (10 - t)^2 (15 + t) / (200 (5 + t)) egrisi ve t = 0'daki kesikli "
         "teget 1,5 - 0,5t; (0; 1,5) noktasi. t = 1'de egri 1,08'e iner (gercek fark -0,42), teget 1,0'a "
         "iner (df(v_p) = -0,5); iki nokta arasindaki hata 0,08.",
)

# ============================================================ form-seviye-dogrulari
# -*- coding: utf-8 -*-
# form-seviye-dogrulari — the 1-form phi(v_p) = 2 p1 v1 + p2 v2 at p = (1, 1), where it reads
# 2 v1 + v2. Six tangent arrows leave p with tips (2, 1), (1, 2), (2, 2), (0, 3), (0, 2), (1, -1)
# and values 2, 1, 3, 0, -1, -2. The tip of an arrow with value c lies on 2x + y = 3 + c; these
# level lines are drawn for c = -2 .. 3, each labelled at its top/left end on the frame.

XR, YR = (-0.5, 3.0), (-1.5, 3.5)
p = cplane(64, 62, 280, XR, YR)          # equal scale: 80 px per unit
L, R = p.X(XR[0]), p.X(XR[1])
T, B = p.Y(YR[1]), p.Y(YR[0])
P = (1.0, 1.0)


def ital(s):
    return '<tspan font-style="italic">' + s + '</tspan>'


def num(v):
    return (MINUS_S + str(-v)) if v < 0 else str(v)


def halo_text(px, py, s, color=TEXT, size=11, anchor="start", weight=None, opacity=1.0):
    """Text with a page-background halo so faint grid lines do not cut through it."""
    w = f' font-weight="{weight}"' if weight else ""
    p.add(f'<text x="{px:.1f}" y="{py:.1f}" fill="{BG}" stroke="{BG}" stroke-width="4" '
          f'stroke-linejoin="round" font-size="{size}" text-anchor="{anchor}"{w}>{s}</text>')
    p.add(f'<text x="{px:.1f}" y="{py:.1f}" fill="{color}" font-size="{size}" '
          f'text-anchor="{anchor}" opacity="{opacity}"{w}>{s}</text>')


# 1. faint unit grid; the lines x = 0 and y = 0 a little stronger
for x in (0, 1, 2):
    p.line([(x, YR[0]), (x, YR[1])], TEXT, 0.8 if x == 0 else 0.7, None, 0.30 if x == 0 else 0.11)
for y in (-1, 0, 1, 2, 3):
    p.line([(XR[0], y), (XR[1], y)], TEXT, 0.8 if y == 0 else 0.7, None, 0.30 if y == 0 else 0.11)

# 2. frame
p.add(f'<rect x="{L:.1f}" y="{T:.1f}" width="{R - L:.1f}" height="{B - T:.1f}" fill="none" '
      f'stroke="{TEXT}" stroke-width="1" opacity="0.4"/>')

# 3. level lines 2x + y = 3 + c, clipped to the frame
EPS_ = 1e-9


def ends(k):
    """The two points where 2x + y = k meets the frame, upper (top/left) end first."""
    pts = []
    for x in XR:
        y = k - 2 * x
        if YR[0] - EPS_ <= y <= YR[1] + EPS_:
            pts.append((x, y))
    for y in YR:
        x = (k - y) / 2
        if XR[0] - EPS_ <= x <= XR[1] + EPS_:
            pts.append((x, y))
    pts.sort(key=lambda q: -q[1])
    return pts[0], pts[-1]


LEVELS = (-2, -1, 0, 1, 2, 3)
for c in LEVELS:
    a, b = ends(3 + c)
    if c == 0:
        p.line([a, b], TEXT, 1.6, None, 0.75)
    else:
        p.line([a, b], TEXT, 1.1, None, 0.40)

# 4. ticks: x along the bottom, y along the right edge (the left and top edges carry the c labels)
for x in (0, 1, 2, 3):
    X = p.X(x)
    p.add(f'<line x1="{X:.1f}" y1="{B:.1f}" x2="{X:.1f}" y2="{B + 4:.1f}" stroke="{TEXT}" '
          f'stroke-width="1" opacity="0.5"/>')
    p.text_px(X, B + 16, num(x), TEXT, 10.5, "middle")
for y in (-1, 0, 1, 2, 3):
    Y = p.Y(y)
    p.add(f'<line x1="{R:.1f}" y1="{Y:.1f}" x2="{R + 4:.1f}" y2="{Y:.1f}" stroke="{TEXT}" '
          f'stroke-width="1" opacity="0.5"/>')
    p.text_px(R + 8, Y + 4, num(y), TEXT, 10.5, "start")
p.text_px(R + 20, B + 16, "x", TEXT, 11.5, "start", italic=True)
p.text_px(R + 10, T + 4, "y", TEXT, 11.5, "start", italic=True)

# 5. the six tangent arrows at p
TIPS = [((2, 1), 2), ((1, 2), 1), ((2, 2), 3), ((0, 3), 0), ((0, 2), -1), ((1, -1), -2)]
for tip, _ in TIPS:
    p.arrow(P, tip, THEORY, 2.0, head=8.5)

# 6. the point p
dot(p, P, TEXT, 4.2)

# 7. c labels at the upper end of every level line
for c in LEVELS:
    (x, y), _ = ends(3 + c)
    s = ital("c") + " = " + num(c)
    wt = "700" if c == 0 else None
    if abs(x - XR[0]) < EPS_:                      # left edge
        p.add(f'<text x="{L - 6:.1f}" y="{p.Y(y) + 4:.1f}" fill="{TEXT}" font-size="10.5" '
              f'text-anchor="end"{" font-weight=" + chr(34) + wt + chr(34) if wt else ""}>{s}</text>')
    else:                                          # top edge
        p.add(f'<text x="{p.X(x):.1f}" y="{T - 7:.1f}" fill="{TEXT}" font-size="10.5" '
              f'text-anchor="middle"{" font-weight=" + chr(34) + wt + chr(34) if wt else ""}>{s}</text>')

# 8. values at the arrow tips (pixel offsets chosen off the level line through each tip)
VALUE_POS = {
    (2, 1): (9, 4.5, "start"),
    (1, 2): (5, -7, "start"),
    (2, 2): (7, -5, "start"),
    (0, 3): (7, -6, "start"),
    (0, 2): (6, -7, "start"),
    (1, -1): (-5, 15, "end"),
}
for tip, val in TIPS:
    dx, dy, anchor = VALUE_POS[tip]
    halo_text(p.X(tip[0]) + dx, p.Y(tip[1]) + dy, num(val), PRACTICE, 12.5, anchor, "700")

# 9. name of the point
halo_text(p.X(P[0]) - 8, p.Y(P[1]) + 16, bold("p"), TEXT, 12.5, "end")

# 10. title: the rule at p
p.text_px((L + R) / 2, T - 30,
          bold("p") + " = (1, 1) noktasında&#160;&#160;" + ital("&#966;") + subs(bold("p")) + "(" + bold("v")
          + subs(bold("p")) + ") = 2" + ital("v") + subs("1") + " + " + ital("v") + subs("2"),
          TEXT, 12, "middle")

OUT["form-seviye-dogrulari"] = figure(
    420, 500, [p],
    "<strong>p</strong> = (1, 1) noktasında <em>&#966;</em><sub><strong>p</strong></sub>(<strong>v</strong><sub><strong>p</strong></sub>) "
    "= 2<em>v</em><sub>1</sub> + <em>v</em><sub>2</sub> kuralı: <strong>p</strong>'den çıkan altı okun "
    "ucundaki turuncu sayılar, <em>&#966;</em>'nin o oka verdiği değerlerdir. Değeri <em>c</em> olan "
    "her okun ucu 2<em>x</em> + <em>y</em> = 3 + <em>c</em> doğrusunun üzerine düşer; gri doğrular "
    "<em>c</em> = &#8722;2, &#8722;1, 0, 1, 2, 3 için bu seviye doğrularıdır ve daha kalın çizilen "
    "<em>c</em> = 0 doğrusu <strong>p</strong>'den geçer. Doğruların paralel ve eşit aralıklı olması, "
    "<em>&#966;</em><sub><strong>p</strong></sub>'nin lineer olmasının görüntüsüdür.",
    aria="p = (1, 1) noktasinda phi(v_p) = 2 v1 + v2 kurali. p'den uclari (2, 1), (1, 2), (2, 2), "
         "(0, 3), (0, 2), (1, -1) olan alti ok; degerleri sirasiyla 2, 1, 3, 0, -1, -2. "
         "2x + y = 3 + c seviye dogrulari c = -2, -1, 0, 1, 2, 3 icin paralel ve esit aralikli; "
         "her okun ucu kendi degerinin dogrusu uzerinde, c = 0 dogrusu p'den gecer.")

# ============================================================ form-yerel-ekstremum
# -*- coding: utf-8 -*-
# form-yerel-ekstremum — level curves of f = x^3 - 3x + y^2 on the square [-2.5, 2.5]^2
# (f does not depend on z, so this is the picture in every plane z = const).
# Levels c = -1.5, -1, 0, 1 (blue), c = 2 (thick, neutral) and c = 3 (orange).
# f + 2 = (x - 1)^2 (x + 2) + y^2: the blue ovals shrink to the local minimum (1, 0), f = -2.
# f - 2 = (x + 1)^2 (x - 2) + y^2: the c = 2 curve y^2 = (x + 1)^2 (2 - x) is a loop over
# -1 <= x <= 2 that crosses itself at (-1, 0), a critical point with no extremum.

import math

_XR = _YR = (-2.5, 2.5)
_PPU = 68.0                                  # pixels per unit, equal on both axes
_P = cplane(40, 40, 5 * _PPU, _XR, _YR)
_L, _R = _P.X(_XR[0]), _P.X(_XR[1])
_T, _B = _P.Y(_YR[1]), _P.Y(_YR[0])


def _g(x):
    return x ** 3 - 3 * x


def _f(x, y):
    return _g(x) + y * y


def _ital(s):
    return '<tspan font-style="italic">' + s + '</tspan>'


def _num(v):
    s = tfmt(abs(v))
    return (MINUS_S + s) if v < 0 else s


def _bisect(h, lo, hi, n=60):
    """Root of h on [lo, hi], assuming h(lo) and h(hi) have opposite signs."""
    s_lo = h(lo) < 0
    for _ in range(n):
        mid = 0.5 * (lo + hi)
        if (h(mid) < 0) == s_lo:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


# --- curve samplers ------------------------------------------------------------------------
def _left_branch(c, n=180):
    """c < 2: the open branch x <= -1 of f = c, as x(y) for |y| <= 2.5 (g increases there)."""
    pts = []
    for k in range(n + 1):
        y = _YR[0] + (_YR[1] - _YR[0]) * k / n
        pts.append((_bisect(lambda x: _g(x) - (c - y * y), -3.0, -1.0), y))
    return pts


def _oval(c, n=260):
    """c < 2: the closed part of f = c around (1, 0), found ray by ray from (1, 0)."""
    pts = []
    for k in range(n + 1):
        th = 2 * math.pi * k / n
        ct, st = math.cos(th), math.sin(th)
        h = lambda r: _f(1 + r * ct, r * st) - c
        r = 0.02
        while h(r) < 0:
            r += 0.02
        rr = _bisect(h, r - 0.02, r)
        pts.append((1 + rr * ct, rr * st))
    return pts


def _c2_branch(sign, n=420):
    """c = 2: y = sign (x + 1) sqrt(2 - x) from the frame (|y| = 2.5) through (-1, 0) to (2, 0)."""
    x_exit = _bisect(lambda x: (x + 1) ** 2 * (2 - x) - 6.25, -3.0, -1.0)
    pts = []
    for k in range(n + 1):
        u = k / n
        x = x_exit + (2 - x_exit) * (1 - (1 - u) ** 2)     # dense near the vertical tangent at x = 2
        pts.append((x, sign * (x + 1) * math.sqrt(max(0.0, 2 - x))))
    return pts


def _c3_curve(n=420):
    """c = 3: y^2 = 3 - g(x), from the top edge round the vertex (e, 0) to the bottom edge."""
    e = _bisect(lambda x: _g(x) - 3.0, 1.0, 3.0)
    x_exit = _bisect(lambda x: _g(x) - (3.0 - 6.25), -3.0, -1.0)
    pts = []
    for k in range(n + 1):
        u = -1 + 2 * k / n
        x = e - (e - x_exit) * u * u
        y = math.copysign(math.sqrt(max(0.0, 3.0 - _g(x))), u)
        pts.append((x, y))
    return pts


# --- 1. faint unit grid and frame -----------------------------------------------------------
for v in (-2, -1, 0, 1, 2):
    _P.line([(v, _YR[0]), (v, _YR[1])], TEXT, 0.7, None, 0.08)
    _P.line([(_XR[0], v), (_XR[1], v)], TEXT, 0.7, None, 0.08)
_P.add(f'<rect x="{_L:.1f}" y="{_T:.1f}" width="{_R - _L:.1f}" height="{_B - _T:.1f}" fill="none" '
       f'stroke="{TEXT}" stroke-width="1" opacity="0.38"/>')

# --- 2. level curves -------------------------------------------------------------------------
_BLUE = [(-1.5, 0.70), (-1.0, 0.80), (0.0, 0.90), (1.0, 1.0)]   # tone deepens towards c = 2
for c, op in _BLUE:
    _P.line(_left_branch(c), THEORY, 1.6, None, op)
    _P.line(_oval(c), THEORY, 1.6, None, op)
_P.line(_c3_curve(), PRACTICE, 1.7, None, 1.0)
_P.line(_c2_branch(1), TEXT, 2.7, None, 0.88)
_P.line(_c2_branch(-1), TEXT, 2.7, None, 0.88)


# --- 3. level values: a ladder under (1, 0), where every curve crosses x = 1 horizontally ----
def _tag(x, y, s, w, color, size=10, opacity=1.0, pad=1.8):
    """Value label centred on a curve, on a page-coloured box that cuts a gap into it."""
    px, py = _P.X(x), _P.Y(y) + 0.36 * size
    top, bot = py - 0.74 * size - pad, py + 0.12 * size + pad
    _P.add(f'<rect x="{px - w / 2 - pad:.1f}" y="{top:.1f}" width="{w + 2 * pad:.1f}" '
           f'height="{bot - top:.1f}" fill="{BG}" stroke="none"/>')
    _P.add(f'<text x="{px:.1f}" y="{py:.1f}" fill="{color}" font-size="{size}" text-anchor="middle" '
           f'font-weight="600" opacity="{opacity}">{s}</text>')


_tag(1, -math.sqrt(0.5), _num(-1.5), 19, THEORY, opacity=0.9)
_tag(1, -1.0, _num(-1), 12, THEORY, opacity=0.9)
_tag(1, -math.sqrt(2), _num(0), 6.5, THEORY)
_tag(1, -math.sqrt(3), _num(1), 6.5, THEORY)
_tag(1, -2.0, _ital("c") + " = 2", 24, TEXT)
_tag(1, -math.sqrt(5), _ital("c") + " = 3", 24, PRACTICE)

# --- 4. leaders from the labels above the frame down to the two critical points --------------
_LEAD_TOP = _T - 3.5                         # starts clear of the label's descenders


def _leader(x, color, opacity):
    X = _P.X(x)
    _P.add(f'<line x1="{X:.1f}" y1="{_LEAD_TOP:.1f}" x2="{X:.1f}" y2="{_P.Y(0) - 8.5:.1f}" '
           f'stroke="{color}" stroke-width="1" opacity="{opacity}"/>')


_leader(-1, TEXT, 0.6)
_leader(1, BASE, 0.85)


# --- 5. the critical points, ringed by the page colour --------------------------------------
def _marked(pt, color, r=4.4):
    _P.add(f'<circle cx="{_P.X(pt[0]):.1f}" cy="{_P.Y(pt[1]):.1f}" r="{r + 2.6:.1f}" fill="{BG}"/>')
    dot(_P, pt, color, r)


_marked((-1.0, 0.0), TEXT)
_marked((1.0, 0.0), BASE)

# --- 6. point labels above the frame ---------------------------------------------------------
_P.text_px(_P.X(-1) + 62, _T - 12, "kritik ama ekstremum değil, " + _ital("f") + " = 2",
           TEXT, 11, "end", bold=True)
_P.text_px(_P.X(1) - 28, _T - 12, "yerel minimum, " + _ital("f") + " = " + MINUS_S + "2",
           BASE, 11, "start", bold=True)

# --- 7. ticks and axis names -----------------------------------------------------------------
for v in (-2, -1, 0, 1, 2):
    X, Y = _P.X(v), _P.Y(v)
    _P.add(f'<line x1="{X:.1f}" y1="{_B:.1f}" x2="{X:.1f}" y2="{_B + 4:.1f}" stroke="{TEXT}" '
           f'stroke-width="1" opacity="0.5"/>')
    _P.add(f'<line x1="{_L - 4:.1f}" y1="{Y:.1f}" x2="{_L:.1f}" y2="{Y:.1f}" stroke="{TEXT}" '
           f'stroke-width="1" opacity="0.5"/>')
    _P.add(f'<text x="{X:.1f}" y="{_B + 16:.1f}" fill="{TEXT}" font-size="10.5" '
           f'text-anchor="middle" opacity="0.75">{_num(v)}</text>')
    _P.add(f'<text x="{_L - 7:.1f}" y="{Y + 3.8:.1f}" fill="{TEXT}" font-size="10.5" '
           f'text-anchor="end" opacity="0.75">{_num(v)}</text>')
_P.text_px((_L + _R) / 2, _B + 32, "x", TEXT, 11.5, "middle", italic=True)
_P.text_px(_L - 28, (_T + _B) / 2 + 4, "y", TEXT, 11.5, "middle", italic=True)

OUT["form-yerel-ekstremum"] = figure(
    400, 420, [_P],
    "<em>f</em> = <em>x</em><sup>3</sup> &#8722; 3<em>x</em> + <em>y</em><sup>2</sup> fonksiyonunun "
    "<em>xy</em>-düzlemindeki seviye eğrileri; <em>f</em>, <em>z</em>'ye bağlı olmadığından her "
    "<em>z</em> için aynı resim görülür. Mavi eğrilerin (<em>c</em> = &#8722;1,5; &#8722;1; 0; 1) "
    "ilmeğin içindeki kapalı parçaları (1, 0)'a doğru iç içe küçülür: orada <em>f</em>'nin yerel "
    "minimumu vardır ve değeri &#8722;2'dir. Kalın <em>c</em> = 2 eğrisi <em>y</em><sup>2</sup> = "
    "(<em>x</em> + 1)<sup>2</sup>(2 &#8722; <em>x</em>) ise (&#8722;1, 0)'da kendini keser; bu "
    "noktanın solunda ve sağında <em>f</em> &lt; 2 (mavi), altında ve üstünde <em>f</em> &gt; 2 "
    "(turuncu) olduğundan <em>df</em> orada sıfır olduğu hâlde ekstremum yoktur.",
    aria="xy-duzleminde f = x^3 - 3x + y^2 fonksiyonunun c = -1.5, -1, 0, 1, 2, 3 seviye egrileri; "
         "x ve y -2.5 ile 2.5 arasi, f z'ye bagli olmadigindan her z icin ayni resim. c &lt; 2 egrileri "
         "mavi: solda acik kollar ve (1, 0) etrafinda ic ice kapali egriler. c = 2 egrisi kalin: "
         "y^2 = (x + 1)^2 (2 - x), (-1, 0) noktasinda kendini kesen ve x = -1 ile x = 2 arasinda "
         "ilmek olusturan egri. c = 3 egrisi turuncu. (1, 0) yesil nokta, ilmegin icinde: yerel "
         "minimum, f = -2. (-1, 0) noktasi: kritik ama ekstremum degil, f = 2.")

# ============================================================ kapali-yari-duzlem-acik-degil
# -*- coding: utf-8 -*-
# kapali-yari-duzlem-acik-degil — the closed half-plane C: p1 >= 0 (shaded, boundary line
# included) is not open: around the boundary point p = (0, 1) the dashed ball of radius 0,5
# sticks out of C on the left, and q = (-0,25; 1) inside that ball is not in C. For contrast,
# the ball of radius 1 around the interior point s = (1,5; 1,5) stays entirely inside C.

XR, YR = (-2.15, 3.4), (-1.15, 3.15)
p = cplane(30, 22, 340, XR, YR)


def ital(s):
    return '<tspan font-style="italic">' + s + '</tspan>'


def mfmt(v):
    """Tick label with a real minus sign and the Turkish decimal comma."""
    return tfmt(v).replace("-", MINUS_S)


# the closed half-plane C (fill up to the panel edges), then a faint unit grid
rect(p, 0.0, XR[1], YR[0], YR[1], THEORY, 0.13)
for k in range(-2, 4):
    p.line([(k, -1), (k, 3)], TEXT, 0.7, None, 0.10)
for k in range(-1, 4):
    p.line([(-2, k), (3, k)], TEXT, 0.7, None, 0.10)

p.origin_axes("x", "y", xticks=(-2, -1, 1, 2, 3), yticks=(), xfmt=mfmt, yfmt=mfmt)

# the boundary line p1 = 0 belongs to C: thick solid line on top of the y axis
p.line([(0.0, -1.12), (0.0, 3.0)], THEORY, 3.2)

# y ticks drawn after the boundary line so that they stay visible (y = 1 is skipped:
# q sits right where its number would go)
ox = p.X(0.0)
for t in (-1, 2, 3):
    ty = p.Y(t)
    p.add(f'<line x1="{ox-5:.1f}" y1="{ty:.1f}" x2="{ox+5:.1f}" y2="{ty:.1f}" '
          f'stroke="{TEXT}" stroke-width="1" opacity="0.7"/>')
    p.text_px(ox - 8, ty + 4, mfmt(t), TEXT, 11, "end")

# interior point s and its ball of radius 1, entirely inside C
S = (1.5, 1.5)
p.circle(S[0], S[1], 1.0, BASE, 1.6, "5 4")
dot(p, S, BASE, 4.0)

# boundary point p, its ball of radius 0,5 (left half outside C) and q inside the ball
P, Q = (0.0, 1.0), (-0.25, 1.0)
p.circle(P[0], P[1], 0.5, PRACTICE, 1.6, "5 4")
dot(p, P, PRACTICE, 4.0)
hollow(p, Q, PRACTICE, 3.8, 1.7)

# labels
p.label(3.3, 2.88, ital("C") + ": " + ital("p") + subs("1") + " " + GEQ_S + " 0",
        0, 0, THEORY, 12.5, "end")
p.label(-0.14, 2.55, "sınır " + ital("C") + "'ye ait", 0, 0, THEORY, 11, "end")

p.label(-0.1, 1.62, bold("p") + " = (0, 1)", 0, 0, PRACTICE, 11.5, "end")
p.label(-0.62, 1.0, bold("q") + " = (" + MINUS_S + "0,25; 1)", 0, -2, PRACTICE, 11.5, "end")
p.label(-0.62, 1.0, ital("C") + "'de değil", 0, 11, PRACTICE, 11.5, "end")
p.label(-0.3, 0.5, EPS + " = 0,5", 0, 10, PRACTICE, 11.5, "end")

p.label(S[0], S[1], bold("s") + " = (1,5; 1,5)", 0, -9, BASE, 11.5, "middle")
p.label(S[0], S[1], EPS + " = 1", 0, 17, BASE, 11.5, "middle")
p.label(S[0], 0.5, "top " + ital("C") + "'nin içinde", 0, 14, BASE, 11, "middle")

OUT["kapali-yari-duzlem-acik-degil"] = figure(
    400, 320, [p],
    "<em>C</em>: <em>p</em><sub>1</sub> &#8805; 0 kapalı yarı düzlemi (mavi) sınır doğrusunu da "
    "içerir. Sınırdaki <strong>p</strong> = (0, 1) noktasının etrafına çizilen yarıçapı 0,5 olan "
    "dairenin sol yarısı kümeden taşar: içindeki <strong>q</strong> = (&#8722;0,25; 1) noktası "
    "<strong>p</strong>'ye 0,25 uzaklıktadır ama <em>C</em>'de değildir. Yarıçap ne kadar "
    "küçültülürse küçültülsün aynı şey olur; bu yüzden <em>C</em> açık değildir. Buna karşılık "
    "iç noktadaki <strong>s</strong> = (1,5; 1,5) etrafındaki yarıçapı 1 olan daire tamamen "
    "<em>C</em>'nin içinde kalır.",
    aria="x >= 0 kapali yari duzlemi C mavi tarali, x = 0 sinir dogrusu kalin cizgiyle C'ye "
         "dahil. Sinirdaki p = (0, 1) noktasi etrafindaki yaricapi 0,5 olan kesikli dairenin "
         "sol yarisi C'nin disina tasar; icindeki q = (-0,25; 1) noktasi C'de degildir. "
         "Karsilastirma icin s = (1,5; 1,5) etrafindaki yaricapi 1 olan kesikli daire tamamen "
         "C'nin icinde kalir.")

# ============================================================ kismi-turev-egim
# -*- coding: utf-8 -*-
# Partial derivatives as slopes: f = x^2 y restricted to the two coordinate lines through p = (1, 2).
#   t -> f(1 + t, 2) = 2(1 + t)^2   (blue parabola, tangent of slope df/dx(p) = 4 at t = 0)
#   t -> f(1, 2 + t) = 2 + t        (green dashed line, slope df/dy(p) = 1)


def g_x(t):
    """f along the x-direction line through p: f(1 + t, 2) = 2 (1 + t)^2."""
    return 2 * (1 + t) ** 2


def mfmt(v):
    """Tick label with a Turkish decimal comma and a real minus sign."""
    return tfmt(v).replace("-", MINUS_S)


def ital(s):
    """Italic run inside an SVG <text> — function and variable names."""
    return f'<tspan font-style="italic">{s}</tspan>'


def along(p, t0, h0, t1, h1, at_t, s, off=12.0, color=TEXT, size=11.0):
    """Text written parallel to the line through (t0,h0),(t1,h1), starting above the point at t = at_t
    and shifted `off` pixels to the lower-right side of the line."""
    ax, ay, bx, by = p.X(t0), p.Y(h0), p.X(t1), p.Y(h1)
    ang = math.degrees(math.atan2(by - ay, bx - ax))
    ux, uy = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    nx, ny = -uy, ux                      # unit normal pointing to the lower-right of an ascending line
    h = h0 + (h1 - h0) * (at_t - t0) / (t1 - t0)
    sx, sy = p.X(at_t) + nx * off, p.Y(h) + ny * off
    p.add(f'<text x="{sx:.1f}" y="{sy:.1f}" transform="rotate({ang:.1f} {sx:.1f} {sy:.1f})" '
          f'fill="{color}" font-size="{size}">{s}</text>')


F, T, X, Y = ital("f"), ital("t"), ital("x"), ital("y")

p = Plot(48, 26, 306, 206, (-1.5, 1.2), (-1.0, 8.0))
p.origin_axes("t", "değer", xticks=(-1.5, -1, 0.5, 1), yticks=(4, 6, 8), xfmt=mfmt, yfmt=mfmt)

# the y-direction line f(1, 2 + t) = 2 + t: thin, dashed, BASE
p.line([(-1.5, 0.5), (1.2, 3.2)], BASE, 1.3, "5 4")

# the x-direction parabola f(1 + t, 2) = 2(1 + t)^2 (leaves the panel through the top at t = 1)
clipped(p, g_x, -1.5, 1.2, THEORY, 2.0)

# tangent at t = 0 with slope 4: value 2 + 4t on [-0.6, 0.6]
p.line([(-0.6, 2 + 4 * -0.6), (0.6, 2 + 4 * 0.6)], PRACTICE, 2.0)

# the point (0, 2) = (0, f(p)) where the parabola, the line and the tangent meet
dot(p, (0.0, 2.0), TEXT, 3.8)
p.label(0.0, 2.0, "(0, 2)", -8, -6, TEXT, 11.5, "end")

# slope labels written along the lines, on their lower-right sides
along(p, -0.6, -0.4, 0.6, 4.4, 0.33,
      "eğim = " + PARTIAL + F + "/" + PARTIAL + X + "(" + bold("p") + ") = 4",
      off=12.0, color=PRACTICE, size=11.0)
along(p, -1.5, 0.5, 1.2, 3.2, 0.18,
      "eğim = " + PARTIAL + F + "/" + PARTIAL + Y + "(" + bold("p") + ") = 1",
      off=13.0, color=BASE, size=11.0)

# legend in the empty upper-left region: which curve is which
lx, ly = 54, 50
p.add(f'<line x1="{lx}" y1="{ly - 4}" x2="{lx + 20}" y2="{ly - 4}" stroke="{THEORY}" stroke-width="2.0" stroke-linecap="round"/>')
p.text_px(lx + 27, ly, F + "(1 + " + T + ", 2) = 2(1 + " + T + ")" + sups("2"), THEORY, 11.5)
p.add(f'<line x1="{lx}" y1="{ly + 16}" x2="{lx + 20}" y2="{ly + 16}" stroke="{BASE}" stroke-width="1.3" stroke-dasharray="5 4" stroke-linecap="round"/>')
p.text_px(lx + 27, ly + 20, F + "(1, 2 + " + T + ") = 2 + " + T, BASE, 11.5)

OUT["kismi-turev-egim"] = figure(
    400, 255, [p],
    "<em>f</em> = <em>x</em><sup>2</sup><em>y</em> fonksiyonunun <strong>p</strong> = (1, 2) noktasından "
    "geçen iki koordinat doğrusuna kısıtlanışı; yatay eksen <em>t</em>, düşey eksen görülen değer. "
    "Mavi eğri, birinci koordinatı değiştirince görülen <em>f</em>(1 + <em>t</em>, 2) = 2(1 + <em>t</em>)<sup>2</sup> "
    "parabolüdür; (0, 2) noktasındaki turuncu teğetinin eğimi &#8706;<em>f</em>/&#8706;<em>x</em>(<strong>p</strong>) = 4'tür. "
    "Yeşil kesikli doğru ikinci koordinat boyunca görülen <em>f</em>(1, 2 + <em>t</em>) = 2 + <em>t</em> değerleridir; "
    "eğimi &#8706;<em>f</em>/&#8706;<em>y</em>(<strong>p</strong>) = 1'dir. "
    "Kısmi türev, fonksiyonu bir koordinat doğrultusundaki doğruya kısıtlayıp alınan sıradan türevden başka bir şey değildir.",
    aria="t eksenine gore f(1+t,2) = 2(1+t)^2 parabolu, (0,2) noktasi, oradaki egimi 4 olan turuncu teget "
         "ve egimi 1 olan yesil kesikli f(1,2+t) = 2+t dogrusu",
)

# ============================================================ koordinat-fonksiyonu-x
# -*- coding: utf-8 -*-
# koordinat-fonksiyonu-x: the plane x = 2 carrying p = (2, 3, 1), q = (2, -1, 3), r = (2, 0, 0);
# the coordinate function x sends all three points to the same number 2 on the x axis.
#
# Camera note: with the default (azimuth 35, elevation 22) the point p projects exactly onto
# the y axis line (tan(el) = cos(az)/2), so a lower elevation is used here.
import math

P = space_panel(20, 14, 360, (-3.3, 4.65), (-2.1, 4.85))
S = Space(P, Camera(azimuth=30, elevation=15, scale=1.0))

p, q, r = (2.0, 3.0, 1.0), (2.0, -1.0, 3.0), (2.0, 0.0, 0.0)
corners = [(2.0, -2.0, -1.0), (2.0, 4.0, -1.0), (2.0, 4.0, 4.0), (2.0, -2.0, 4.0)]
AX_OP, AX_W = 0.55, 1.1

# --- axes behind the plane (y, z and the x axis up to x = 2) ----------------------------
S.line([(0, -2.5, 0), (0, 0, 0)], TEXT, AX_W, None, AX_OP)
S.arrow((0, 0, 0), (0, 4.8, 0), TEXT, AX_W, 7, None, AX_OP)
S.arrow((0, 0, 0), (0, 0, 4.6), TEXT, AX_W, 7, None, AX_OP)
S.line([(0, 0, 0), (2, 0, 0)], TEXT, AX_W, None, AX_OP)
S.label((0, 4.8, 0), "y", 10, 4, TEXT, 11.5, "middle", False, True)
S.label((0, 0, 4.6), "z", -10, -4, TEXT, 11.5, "middle", False, True)
S.ticks("y", (-2, -1, 1, 2, 3, 4))
S.ticks("z", (1, 2, 3, 4))

# --- the plane patch x = 2 -------------------------------------------------------------
S.polygon(corners, THEORY, 0.15, "none")
S.line(corners + [corners[0]], THEORY, 0.9, None, 0.6)

# --- front part of the x axis (x > 2 lies in front of the plane) -------------------------
S.arrow((2, 0, 0), (5.8, 0, 0), TEXT, AX_W, 7, None, AX_OP)
S.label((5.8, 0, 0), "x", -8, 12, TEXT, 11.5, "middle", False, True)
S.ticks("x", (2, 3, 4))

# --- value arrows: every point goes to the single label "x = 2" ----------------------------
M = S.pt(r)
L = (M[0] + 1.35, M[1] - 0.8)          # the label "x = 2", low inside the patch
LX, LY = P.X(L[0]), P.Y(L[1])


def value_arrow(src, end_px, color, gap0=6.0, width=1.1, head=6.5, opacity=0.85):
    """Thin dashed arrow from the 2-D data point src to the pixel position end_px, trimmed
    by gap0 px at the start. Shaft and head share one <g opacity> so the shaft end does not
    show through the translucent head."""
    x0, y0 = P.X(src[0]), P.Y(src[1])
    x1, y1 = end_px
    dx, dy = x1 - x0, y1 - y0
    n = math.hypot(dx, dy)
    ux, uy = dx / n, dy / n
    x0, y0 = x0 + ux * gap0, y0 + uy * gap0
    sx, sy = x1 - ux * head * 0.8, y1 - uy * head * 0.8
    px, py, hw = -uy, ux, head * 0.42
    P.add(f'<g opacity="{opacity}">'
          f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{sx:.1f}" y2="{sy:.1f}" stroke="{color}" '
          f'stroke-width="{width}" stroke-dasharray="4 3" stroke-linecap="butt"/>'
          f'<polygon points="{x1:.1f},{y1:.1f} {x1-ux*head+px*hw:.1f},{y1-uy*head+py*hw:.1f} '
          f'{x1-ux*head-px*hw:.1f},{y1-uy*head-py*hw:.1f}" fill="{color}"/></g>')


def halo_point(Q, color, rad=3.9):
    """Filled point with a thin background-coloured rim so it stays visible on lines."""
    X, Y = P.X(Q[0]), P.Y(Q[1])
    P.add(f'<circle cx="{X:.1f}" cy="{Y:.1f}" r="{rad}" fill="{color}" stroke="{BG}" stroke-width="1.4"/>')


# three arrival points spread around the label so the heads do not pile up
value_arrow(S.pt(p), (LX + 11, LY - 12), PRACTICE)
value_arrow(S.pt(q), (LX - 9, LY - 12), BASE)
value_arrow(M, (LX - 25, LY - 3), THEORY)

halo_point(S.pt(p), PRACTICE)
halo_point(S.pt(q), BASE)
halo_point(M, THEORY)

# --- labels ----------------------------------------------------------------------------
S.label(p, bold("p") + " = (2, 3, 1)", 7, -7, PRACTICE, 11, "start")
S.label(q, bold("q") + " = (2, " + MINUS_S + "1, 3)", 0, -10, BASE, 11, "middle")
S.label(r, bold("r") + " = (2, 0, 0)", -12, -3, THEORY, 11, "end")
P.label(L[0], L[1], '<tspan font-style="italic">x</tspan> = 2', 0, 4, TEXT, 12.5, "middle")

OUT["koordinat-fonksiyonu-x"] = figure(
    400, 350, [P],
    "Mavi taralı parça, <em>x</em> eksenini 2 noktasında dik kesen <em>x</em> = 2 düzleminin bir "
    "kesitidir; <strong>p</strong> = (2, 3, 1), <strong>q</strong> = (2, &#8722;1, 3) ve "
    "<strong>r</strong> = (2, 0, 0) noktalarının üçü de bu düzlem üzerindedir. Kesikli oklar "
    "<em>x</em> koordinat fonksiyonunun yaptığı işi gösterir: birbirinden farklı üç noktayı "
    "aynı 2 sayısına götürür. <em>x</em>(<strong>p</strong>) = 2 koşulunu sağlayan noktaların "
    "tamamı işte bu düzlemdir.",
    aria="The plane x = 2 in R^3 with the points p = (2, 3, 1), q = (2, -1, 3) and r = (2, 0, 0) on it; "
         "dashed arrows from all three points converge on the single value x = 2 at the mark 2 of the x axis",
)

# ============================================================ nokta-koordinat-kutusu
# -*- coding: utf-8 -*-
# Three points of R^3 read off the axes: p = (2, 3, 1) with its dashed coordinate box,
# q = (2, 3, -1) directly below p and below the floor, r = (3, 2, 1) with x and y swapped.
# Camera: azimuth 20 keeps p and r clear of the z axis and of each other's guides
# (azimuth 45 is degenerate here: r projects onto p's floor edge because r - (2,1,0) = (1,1,1)).

P = space_panel(20, 20, 380, (-1.95, 4.7), (-3.0, 2.15))
S = Space(P, Camera(azimuth=20, elevation=33, scale=1.0))

p = (2.0, 3.0, 1.0)
q = (2.0, 3.0, -1.0)
r = (3.0, 2.0, 1.0)
foot = (2.0, 3.0, 0.0)          # where the vertical through p and q pierces the floor


def mfmt(v):
    """Tick label with a real minus sign instead of a hyphen."""
    return fmt(v).replace("-", MINUS_S)


# floor grid on integer lines
S.floor_grid((0, 4), (0, 4), n=4, opacity=0.11)

# r: only a dashed drop to the floor, enough to place it in space
S.guide([r, (3, 2, 0)], BASE, 0.45)
S.point((3, 2, 0), BASE, 2.0)

# p: the full dashed coordinate box (floor L, riser, guide to the z axis)
S.coordinate_box(p, TEXT, 0.55)

# q: the same vertical continued below the floor
S.guide([foot, q], TEXT, 0.55)
S.point(foot, TEXT, 2.2)

S.axes(4.5, 4.5, 2.2, zmin=-1.8)
S.ticks("x", (1, 2, 3, 4), offset=(-9, 2))
S.ticks("y", (1, 2, 3, 4), offset=(6, -5))
S.ticks("z", (1, 2), offset=(-9, 4))
S.ticks("z", (-1,), fmt_=mfmt, offset=(-9, 0))

# the three coordinates of p marked on the axes, and the origin
S.point((2, 0, 0), TEXT, 2.4)
S.point((0, 3, 0), TEXT, 2.4)
S.point((0, 0, 1), TEXT, 2.4)
S.point((0, 0, 0), TEXT, 2.4)

S.point(p, PRACTICE, 4.2)
S.point(q, THEORY, 4.2)
S.point(r, BASE, 4.2)

# two-line labels: name over coordinates, tucked into the gaps between the guides
S.label(p, bold("p"), -10, 17, PRACTICE, 11.5, "end")
S.label(p, "(2, 3, 1)", -10, 31, PRACTICE, 11.5, "end")
S.label(r, bold("r"), -4, -24, BASE, 11.5, "middle")
S.label(r, "(3, 2, 1)", -4, -11, BASE, 11.5, "middle")
S.label(q, bold("q") + " = (2, 3, " + MINUS_S + "1)", 18, 24, THEORY, 11.5, "start")
S.label((0, 0, 0), bold("0"), -6, -5, TEXT, 11, "end")

OUT["nokta-koordinat-kutusu"] = figure(
    420, 330, [P],
    "Üç nokta ve koordinatları: <strong>p</strong> = (2, 3, 1) noktasına ulaşmak için "
    "başlangıç noktasından <em>x</em> ekseni boyunca 2, <em>y</em> ekseni boyunca 3, sonra "
    "yukarı 1 birim gidilir; kesikli koordinat kutusu bu üç adımı eksenlerden okutur. "
    "<strong>q</strong> = (2, 3, &#8722;1), <strong>p</strong>'nin tam altında ve zeminin 1 birim "
    "aşağısındadır; yalnızca üçüncü koordinat değişmiştir. <strong>r</strong> = (3, 2, 1) ise "
    "aynı sayıları farklı sırayla taşır ve bu yüzden bambaşka bir yerde durur.",
    aria="Points p = (2, 3, 1) with dashed coordinate box, q = (2, 3, -1) directly below p "
         "under the floor, and r = (3, 2, 1) in orthographic xyz axes")

# ============================================================ ozet-kavram-haritasi
# -*- coding: utf-8 -*-
# ozet-kavram-haritasi — concept map of the worked example "Bes Dilde Ayni Sayi" (2D).
# f = x^2 + yz, p = (1, 2, 3), v = (1, -1, 2): the five languages (directional derivative, curve,
# vector field, 1-form, mapping; blue boxes) all deliver the same number v_p[f] = 3 (orange node).
# Solid blue arrows: "this computation gives the number". Grey dashed arrows: relations between the
# languages (duality, special case, exterior derivative), not steps of the computation.
# The panel maps data coordinates one-to-one onto viewBox pixels (y grows downward), so boxes,
# arrows and text are laid out directly in pixels.
import math

W, H = 620, 440
p = Plot(0, 0, W, H, (0, W), (H, 0))

ALPHA, BETA = "&#945;", "&#946;"
NB = "&#160;"
# brackets after an italic letter: a 1.2 px nudge keeps V's and f's overhang off the bracket
LBR, RBR = '<tspan dx="1.2">[</tspan>', '<tspan dx="1.2">]</tspan>'
# the same nudge for round brackets touching the hook of an italic f: f(, df(, (df)
LPA, RPA = '<tspan dx="1.2">(</tspan>', '<tspan dx="1.2">)</tspan>'

BW, BH = 178, 60                  # blue boxes
NW, NH = 164, 72                  # orange centre node
GW, GH = 150, 40                  # small grey box
C = (310, 218)                    # centre node
XL, XR = 97, W - 97               # column centres
BOXES = {
    "yonlu": (310, 58),
    "egri": (XL, 122),
    "alan": (XR, 122),
    "donusum": (XL, 314),
    "form": (XR, 314),
}
G = (380, 398)                    # grey box, on the outer (bottom) edge, below-left of the 1-form box


def ital(s):
    return '<tspan font-style="italic">' + s + '</tspan>'


def vp(size=9):
    return bold("v") + subs(bold("p"), size)


def rounded_box(c, w, h, color, fill_opacity, stroke_width, stroke_opacity=1.0, rx=7):
    p.add(f'<rect x="{c[0] - w / 2:.1f}" y="{c[1] - h / 2:.1f}" width="{w:.1f}" height="{h:.1f}" '
          f'rx="{rx}" fill="{color}" fill-opacity="{fill_opacity}" stroke="{color}" '
          f'stroke-opacity="{stroke_opacity}" stroke-width="{stroke_width}"/>')


def rim(c, w, h, toward, gap=0.0):
    """Where the ray from the box centre c toward `toward` leaves the box grown by `gap` px."""
    dx, dy = toward[0] - c[0], toward[1] - c[1]
    tx = (w / 2 + gap) / abs(dx) if dx else math.inf
    ty = (h / 2 + gap) / abs(dy) if dy else math.inf
    t = min(tx, ty)
    return (c[0] + t * dx, c[1] + t * dy)


def relation(a, b, both=False, head=7.5, width=1.3, opacity=0.6, dash="5 4"):
    """Grey dashed arrow a -> b (double-headed if both). Shaft and heads share one <g opacity>."""
    x0, y0 = a
    x1, y1 = b
    L = math.hypot(x1 - x0, y1 - y0)
    ux, uy = (x1 - x0) / L, (y1 - y0) / L
    px, py, hw = -uy, ux, head * 0.42

    def tip(x, y, sx, sy):
        return (f'<polygon points="{x:.1f},{y:.1f} {x - sx * head + px * hw:.1f},{y - sy * head + py * hw:.1f} '
                f'{x - sx * head - px * hw:.1f},{y - sy * head - py * hw:.1f}" fill="{TEXT}"/>')

    s0 = (x0 + ux * head * 0.85, y0 + uy * head * 0.85) if both else a
    s1 = (x1 - ux * head * 0.85, y1 - uy * head * 0.85)
    g = [f'<g opacity="{opacity}">',
         f'<line x1="{s0[0]:.1f}" y1="{s0[1]:.1f}" x2="{s1[0]:.1f}" y2="{s1[1]:.1f}" stroke="{TEXT}" '
         f'stroke-width="{width}" stroke-dasharray="{dash}" stroke-linecap="butt"/>',
         tip(x1, y1, ux, uy)]
    if both:
        g.append(tip(x0, y0, -ux, -uy))
    g.append('</g>')
    p.add("".join(g))


def dim(s, a=0.8):
    return '<tspan fill-opacity="' + str(a) + '">' + s + '</tspan>'


t = ital("t")
CONTENT = {
    "yonlu": ("yönlü türev", [
        bold("p") + " + " + t + bold("v") + " = (1 + " + t + ", 2 " + MINUS_S + " " + t + ", 3 + 2" + t + ")",
        ital("f") + LPA + bold("p") + " + " + t + bold("v") + ") = 7 + 3" + t + " " + MINUS_S + " "
        + t + sups("2"),
    ]),
    "egri": ("eğri", [
        ital(ALPHA) + "(" + t + ") = (" + ital("e") + sups(ital("t")) + ", 2 " + MINUS_S + " sin " + t
        + ", 3 + 2" + t + ")",
        ital(ALPHA) + PRIME + "(0) = " + vp(),
    ]),
    "alan": ("vektör alanı", [
        ital("V") + " = " + ital("U") + subs("1") + " " + MINUS_S + " " + ital("U") + subs("2")
        + " + 2" + ital("U") + subs("3"),
        ital("V") + LBR + '<tspan dx="1.2" font-style="italic">f</tspan>' + RBR + " = 2" + ital("x") + " " + MINUS_S + " " + ital("z") + " + 2" + ital("y"),
    ]),
    "form": ("1-form", [
        ital("df") + " = 2" + ital("x") + " " + ital("dx") + " + " + ital("z") + " " + ital("dy") + " + "
        + ital("y") + " " + ital("dz"),
        ital("df") + LPA + vp() + ") = 2 " + MINUS_S + " 3 + 4",
    ]),
    "donusum": ("dönüşüm", [
        "Jacobi satırı (2" + NB * 2 + "3" + NB * 2 + "2)",
        ital("f") + subs("*") + "(" + vp() + ") = (3)" + subs("7"),
    ]),
}

# --- 1. box fills and frames ----------------------------------------------------------------
for key, c in BOXES.items():
    rounded_box(c, BW, BH, THEORY, 0.08, 1.4)
rounded_box(C, NW, NH, PRACTICE, 0.11, 2.0)
rounded_box(G, GW, GH, TEXT, 0.035, 1.1, 0.45)

# --- 2. every language delivers the number: solid blue arrows into the centre node ------------
for key, c in BOXES.items():
    p.arrow(rim(c, BW, BH, C, 3), rim(C, NW, NH, c, 4), THEORY, 1.8, head=8.5)

# --- 3. relations between the languages: grey dashed arrows ----------------------------------
LX, RX = XL - 20, XR + 20
relation((LX, BOXES["egri"][1] + BH / 2 + 4), (LX, BOXES["donusum"][1] - BH / 2 - 4))
relation((RX, BOXES["alan"][1] + BH / 2 + 4), (RX, BOXES["form"][1] - BH / 2 - 4), both=True)
D0, D1 = rim(BOXES["form"], BW, BH, G, 4), rim(G, GW, GH, BOXES["form"], 4)
relation(D0, D1)

# --- 4. text ---------------------------------------------------------------------------------
for key, c in BOXES.items():
    title, lines = CONTENT[key]
    top = c[1] - BH / 2
    p.text_px(c[0], top + 17, title, THEORY, 11, "middle", True)
    for k, s in enumerate(lines):
        p.text_px(c[0], top + 34 + 16 * k, s, TEXT, 11, "middle")

# the bold italic f's tail reaches under "[": push the f itself right
p.text_px(C[0], C[1] - 10, vp(11) + '[<tspan dx="1.8" font-style="italic">f</tspan>' + RBR + " = 3",
          PRACTICE, 16, "middle", True)
p.text_px(C[0], C[1] + 11, ital("f") + " = " + ital("x") + sups("2") + " + " + ital("yz"), TEXT, 10.5, "middle")
p.text_px(C[0], C[1] + 26, bold("p") + " = (1, 2, 3)," + NB * 2 + bold("v") + " = (1, " + MINUS_S + "1, 2)",
          TEXT, 10.5, "middle")

p.text_px(G[0], G[1] - 4, dim("diferansiyel formlar", 0.75), TEXT, 10.5, "middle", True)
p.text_px(G[0], G[1] + 12, ital("d") + "(" + ital("df") + RPA + " = 0", TEXT, 10.5, "middle")

# relation labels: inner side of the two column arrows, beside the short arrow to the grey box
MID = C[1]
p.text_px(LX + 8, MID - 3, dim("özel hâl,"), TEXT, 10.5, "start")
p.text_px(LX + 8, MID + 13, dim(ital(BETA) + PRIME + " = " + ital("F") + subs("*") + "(" + ital(ALPHA) + PRIME + ")"),
          TEXT, 10.5, "start")
p.text_px(RX - 8, MID + 5, dim(ital("dx") + subs(ital("i")) + "(" + ital("U") + subs(ital("j")) + ") = "
                            + ital(DELTA) + subs(ital("ij"))), TEXT, 10.5, "end")
p.text_px((D0[0] + D1[0]) / 2 + 12, (D0[1] + D1[1]) / 2 + 13, dim("dış türev " + ital("d")),
          TEXT, 10.5, "start")

OUT["ozet-kavram-haritasi"] = figure(
    W, H, [p],
    "<em>f</em> = <em>x</em><sup>2</sup> + <em>yz</em>, <strong>p</strong> = (1, 2, 3) ve "
    "<strong>v</strong> = (1, &#8722;1, 2) için yönlü türev, eğri, vektör alanı, 1-form ve dönüşüm "
    "dilleri (mavi kutular) aynı <strong>v</strong><sub><strong>p</strong></sub>[<em>f</em>] = 3 "
    "sayısına varır. Beş hesabın özü aynıdır: kısmi türevler 2, 3, 2 ile <strong>v</strong>'nin "
    "koordinatları 1, &#8722;1, 2 terim terim çarpılıp toplanır; 1-form kutusundaki 2 &#8722; 3 + 4 bu "
    "toplamdır. Gri kesikli oklar diller arasındaki bağları gösterir: <em>dx</em><sub><em>i</em></sub>"
    "(<em>U</em><sub><em>j</em></sub>) = <em>&#948;</em><sub><em>ij</em></sub> dualitesi vektör alanlarını "
    "1-formlara bağlar, eğri dili <em>&#946;</em>&#8242; = <em>F</em><sub>*</sub>(<em>&#945;</em>&#8242;) "
    "kuralıyla dönüşüm dilinin özel hâlidir, dış türev ise 1-formları <em>d</em>(<em>df</em>) = 0 "
    "kuralının geçtiği daha yüksek dereceli diferansiyel formlara taşır.",
    css_class=WIDE,
    aria="Kavram haritasi. Ortada turuncu dugum v_p[f] = 3; altinda f = x^2 + yz, p = (1, 2, 3), "
         "v = (1, -1, 2). Cevresinde bes mavi kutu, her birinden merkeze ok: yonlu turev, "
         "p + tv = (1 + t, 2 - t, 3 + 2t), f(p + tv) = 7 + 3t - t^2; egri, alpha(t) = (e^t, 2 - sin t, "
         "3 + 2t), alpha'(0) = v_p; vektor alani, V = U1 - U2 + 2U3, V[f] = 2x - z + 2y; 1-form, "
         "df = 2x dx + z dy + y dz, df(v_p) = 2 - 3 + 4; donusum, Jacobi satiri (2 3 2), "
         "f_*(v_p) = (3)_7. Gri kesikli oklar: vektor alani ile 1-form arasinda cift yonlu, "
         "dx_i(U_j) = delta_ij; egriden donusume, ozel hal, beta' = F_*(alpha'); 1-form kutusundan "
         "disaridaki diferansiyel formlar d(df) = 0 kutusuna, dis turev d.",
)

# ============================================================ seviye-egrileri-x2y
# -*- coding: utf-8 -*-
# seviye-egrileri-x2y — level curves x^2 y = c of f = x^2 y on the square [-2, 2] x [-2, 2]:
# c = 2, 1, 0.5 (blue, darker for larger c), c = -0.5, -1, -2 (orange, darker for larger |c|)
# and the c = 0 level set, the union of the two axes (thick gray). Each curve carries its
# value as a contour label; the point p = (1, 2) sits on the c = 2 curve since f(1, 2) = 2.

import math

XR, YR = (-2.4, 2.4), (-2.3, 2.55)
p = cplane(34, 26, 356, XR, YR)
YLO, YHI = -2.25, 2.5          # the curves stop a hair inside the panel
XMAX = 2.0                     # ... and at the edge of the square


def ital(s):
    return '<tspan font-style="italic">' + s + '</tspan>'


def halo_text(x, y, s, dx=0, dy=0, color=TEXT, size=11, anchor="middle", opacity=1.0, weight=None):
    """Label with a page-background halo so it can sit on a faint grid line."""
    px, py = p.X(x) + dx, p.Y(y) + dy
    w = f' font-weight="{weight}"' if weight else ""
    p.add(f'<text x="{px:.1f}" y="{py:.1f}" fill="{BG}" stroke="{BG}" stroke-width="4" '
          f'stroke-linejoin="round" font-size="{size}" text-anchor="{anchor}"{w}>{s}</text>')
    p.add(f'<text x="{px:.1f}" y="{py:.1f}" fill="{color}" font-size="{size}" '
          f'text-anchor="{anchor}" opacity="{opacity}"{w}>{s}</text>')


def boxed_text(x, y, s, width, dx=0, dy=0, color=TEXT, size=11, opacity=1.0, weight=600, pad=2.5):
    """Contour label: centred on a data point, on an opaque page-background box that cuts a
    clean gap into the curve (a glyph halo alone leaks the curve through '-' and '=')."""
    px, py = p.X(x) + dx, p.Y(y) + dy
    top, bottom = py - 0.72 * size - pad, py + 0.18 * size + pad
    p.add(f'<rect x="{px - width / 2 - pad:.1f}" y="{top:.1f}" width="{width + 2 * pad:.1f}" '
          f'height="{bottom - top:.1f}" fill="{BG}" stroke="none"/>')
    p.add(f'<text x="{px:.1f}" y="{py:.1f}" fill="{color}" font-size="{size}" '
          f'text-anchor="middle" opacity="{opacity}" font-weight="{weight}">{s}</text>')


# faint unit grid outlining the square [-2, 2] x [-2, 2]
for k in range(-2, 3):
    p.line([(k, -2), (k, 2)], TEXT, 0.7, None, 0.12)
    p.line([(-2, k), (2, k)], TEXT, 0.7, None, 0.12)

# c = 0 level set: the two coordinate axes, thick and gray
p.line([(-XMAX, 0), (XMAX, 0)], TEXT, 3.4, None, 0.30)
p.line([(0, YLO), (0, YHI)], TEXT, 3.4, None, 0.30)

# level curves y = c / x^2, two branches each; tone darkens with |c|
LEVELS = [(0.5, THEORY, 0.62), (1.0, THEORY, 0.80), (2.0, THEORY, 1.0),
          (-0.5, PRACTICE, 0.62), (-1.0, PRACTICE, 0.80), (-2.0, PRACTICE, 1.0)]


def branch(c, sign, color, op, n=260):
    bound = YHI if c > 0 else YLO
    x_in = math.sqrt(abs(c) / abs(bound))      # where the branch enters the panel
    pts = []
    for k in range(n + 1):
        t = (k / n) ** 1.7                      # denser sampling on the steep part
        x = x_in + (XMAX - x_in) * t
        pts.append((sign * x, c / (x * x)))
    p.line(pts, color, 2.0, None, op)


for c, color, op in LEVELS:
    branch(c, 1, color, op)
    branch(c, -1, color, op)

# thin axes with arrowheads on top of the gray band
p.origin_axes("x", "y")

# tick marks and numbers (haloed: the grid lines pass through them)
ox, oy = p.X(0), p.Y(0)
for v in (-2, -1, 1, 2):
    X = p.X(v)
    p.add(f'<line x1="{X:.1f}" y1="{oy-3:.1f}" x2="{X:.1f}" y2="{oy+3:.1f}" '
          f'stroke="{TEXT}" stroke-width="1" opacity="0.7"/>')
    Y = p.Y(v)
    p.add(f'<line x1="{ox-3:.1f}" y1="{Y:.1f}" x2="{ox+3:.1f}" y2="{Y:.1f}" '
          f'stroke="{TEXT}" stroke-width="1" opacity="0.7"/>')
    halo_text(0, v, (MINUS_S + str(-v)) if v < 0 else str(v), -7, 4, TEXT, 10.5, "end", 0.75)
for v in (-2, -1, 1, 2):
    halo_text(v, 0, (MINUS_S + str(-v)) if v < 0 else str(v), 0, 21, TEXT, 10.5, "middle", 0.75)

# contour labels: c > 0 on the right branches, c < 0 on the left branches, one row each
YL = 0.72
WIDTHS = {"0,5": 13.5, "1": 6.0, "2": 6.0}
for c, color, op in LEVELS:
    x = math.sqrt(abs(c) / YL)
    s = tfmt(abs(c))
    if c > 0:
        boxed_text(x, YL, s, WIDTHS[s], 0, 3.6, color, 10.5, op)
    else:
        boxed_text(-x, -YL, MINUS_S + s, WIDTHS[s] + 6.0, 0, 3.6, color, 10.5, op)
boxed_text(-1.5, 0, ital("c") + " = 0", 22.0, 0, 3.6, TEXT, 10.5, 0.7)

# the point p = (1, 2) on the c = 2 curve, ringed by the page background
P = (1.0, 2.0)
p.add(f'<circle cx="{p.X(P[0]):.1f}" cy="{p.Y(P[1]):.1f}" r="6.4" fill="{BG}"/>')
dot(p, P, PRACTICE, 4.0)
p.label(P[0], P[1], bold("p") + " = (1, 2)", 11, -5, PRACTICE, 11.5, "start")

# formula line above the panel
p.text_px(p.x0 + 2, p.y0 - 6,
          ital("f") + " = " + ital("x") + sups("2") + ital("y") + ",&#160;&#160; seviye eğrileri "
          + ital("x") + sups("2") + ital("y") + " = " + ital("c"),
          TEXT, 11.5, "start")

OUT["seviye-egrileri-x2y"] = figure(
    424, 412, [p],
    "<em>f</em> = <em>x</em><sup>2</sup><em>y</em> fonksiyonunun düzlemdeki seviye eğrileri "
    "<em>x</em><sup>2</sup><em>y</em> = <em>c</em>: <em>c</em> = 0,5; 1; 2 için maviler, "
    "<em>c</em> = &#8722;0,5; &#8722;1; &#8722;2 için turuncular; |<em>c</em>| büyüdükçe ton koyulaşır. "
    "<em>c</em> &#8800; 0 iken seviye kümesi iki dallı <em>y</em> = <em>c</em>/<em>x</em><sup>2</sup> "
    "eğrisidir; <em>c</em> = 0 seviye kümesi ise iki koordinat ekseninin birleşimidir (kalın gri). "
    "<strong>p</strong> = (1, 2) noktası <em>c</em> = 2 eğrisinin üzerindedir, çünkü "
    "<em>f</em>(1, 2) = 1<sup>2</sup> &#183; 2 = 2.",
    aria="Duzlemde f = x^2 y fonksiyonunun x^2 y = c seviye egrileri, c = -2, -1, -0.5, 0.5, 1, 2; "
         "pozitif c mavi, negatif c turuncu, her egri iki dalli y = c / x^2 egrisi; c = 0 seviye "
         "kumesi iki koordinat ekseninin birlesimi, kalin gri. p = (1, 2) noktasi c = 2 egrisinin "
         "uzerindedir.")

# ============================================================ teget-ayrisim
# -*- coding: utf-8 -*-
# teget-ayrisim: V(p) = 2U1(p) + 3U2(p) + 2U3(p) at p = (1, 2, 1) — the arrow from
# (1, 2, 1) to (3, 5, 3) as the diagonal of the 2x3x2 box spanned by its components.


def ital(s):
    """Italic run inside an SVG <text> — function/field names."""
    return f'<tspan font-style="italic">{s}</tspan>'


# azimuth 30 (not 25): at 25 the projected 2U1 arrow crossed the y axis exactly on the
# y = 1 tick; at 30 the crossing sits at y ~ 0.76, so the tick and its label stay clear
P = space_panel(20, 16, 498, (-2.2, 5.7), (-2.55, 3.85))
S = Space(P, Camera(azimuth=30, elevation=22, scale=1.0))

# floor grid with unit spacing
for i in range(0, 5):
    S.line([(i, 0, 0), (i, 6, 0)], TEXT, 0.7, None, 0.12)
for j in range(0, 7):
    S.line([(0, j, 0), (4, j, 0)], TEXT, 0.7, None, 0.12)

S.axes(3.9, 5.9, 3.9)
S.ticks("x", (1, 2, 3))
S.ticks("y", (1, 2, 3, 4, 5))
S.ticks("z", (1, 2, 3))

p = (1.0, 2.0, 1.0)
q = (3.0, 5.0, 3.0)
a, b, c = (3.0, 2.0, 1.0), (1.0, 5.0, 1.0), (1.0, 2.0, 3.0)      # p + 2U1, p + 3U2, p + 2U3
ab, bc, ca = (3.0, 5.0, 1.0), (1.0, 5.0, 3.0), (3.0, 2.0, 3.0)

# the 2x3x2 box: nine dashed edges (the other three are the component arrows);
# the back vertical edge a-ca is drawn in two pieces so the label of p sits in a gap
edges = [(a, ab), (b, ab), (c, ca), (b, bc), (c, bc), (ab, q), (bc, q), (ca, q),
         (a, (3.0, 2.0, 1.48)), ((3.0, 2.0, 2.06), ca)]
for e in edges:
    S.guide(list(e), TEXT, 0.42, 1.0, "5 4")
S.drop(p)

# component arrows and the field value
S.arrow(p, a, PRACTICE, 2.2, head=8)
S.arrow(p, b, BASE, 2.2, head=8)
S.arrow(p, c, THEORY, 2.2, head=8)
S.arrow(p, q, TEXT, 2.8, head=10)
S.point(p, TEXT, 3.8)

# labels — each one at the tip of its own arrow
bp = "(" + bold("p") + ")"


def comp(k, coef):
    return (ital("v") + subs(k) + bp + " " + ital("U") + subs(k) + bp
            + " = " + coef + ital("U") + subs(k) + bp)


S.label(p, bold("p") + " = (1, 2, 1)", -8, -2, TEXT, 11.5, "end")
S.label(q, ital("V") + bp + " = (2, 3, 2)" + subs(bold("p")), -6, -27, TEXT, 11.5, "end")
S.label(a, comp("1", "2"), 40, 36, PRACTICE, 11, "end")
S.label(b, comp("2", "3"), 8, 4, BASE, 11, "start")
S.label(c, comp("3", "2"), 8, -10, THEORY, 11, "start")

OUT["teget-ayrisim"] = figure(
    540, 430, [P],
    "Kalın ok, <strong>p</strong> = (1, 2, 1) noktasındaki <em>V</em>(<strong>p</strong>) = (2, 3, 2)<sub><strong>p</strong></sub> "
    "teğet vektörüdür: (1, 2, 1)'den (3, 5, 3)'e gider. Eksenlere paralel üç bileşen oku "
    "2<em>U</em><sub>1</sub>(<strong>p</strong>), 3<em>U</em><sub>2</sub>(<strong>p</strong>), 2<em>U</em><sub>3</sub>(<strong>p</strong>) "
    "toplandığında <em>V</em>(<strong>p</strong>)'yi verir; <em>V</em>(<strong>p</strong>), kenarları bu üç ok olan "
    "2&#215;3&#215;2 kutunun <strong>p</strong>'den çıkan köşegenidir. Koordinat fonksiyonlarının <strong>p</strong>'deki "
    "değerleri <em>v</em><sub>1</sub>(<strong>p</strong>) = 2, <em>v</em><sub>2</sub>(<strong>p</strong>) = 3, "
    "<em>v</em><sub>3</sub>(<strong>p</strong>) = 2 kutunun kenar uzunluklarıdır.",
    aria="Tangent vector V(p) = (2,3,2) at p = (1,2,1) drawn as the diagonal of the 2x3x2 box spanned by its three component arrows 2U1, 3U2, 2U3",
)

# ============================================================ teget-dogal-cati
# -*- coding: utf-8 -*-
# teget-dogal-cati: the natural frame U1, U2, U3 evaluated at p = (1, 2, 1) and q = (3, 0, 2).
# Colour convention for this figure: U1 -> PRACTICE, U2 -> BASE, U3 -> THEORY (same colour = same field).

P = space_panel(26, 18, 348, (-2.75, 3.05), (-2.05, 2.60))
S = Space(P, Camera(azimuth=35, elevation=28, scale=0.70))


def ital(s):
    return f'<tspan font-style="italic">{s}</tspan>'


def U(k, name):
    """Label 'U_k(name)' with an italic U and a bold point name."""
    return ital("U") + subs(k) + "(" + bold(name) + ")"


# floor grid and axes
S.floor_grid((0, 4), (0, 4), n=4, opacity=0.11)
S.axes(4.7, 4.7, 3.7)
S.ticks("x", (1, 2, 3, 4))
S.ticks("y", (1, 2, 3, 4))
S.ticks("z", (1, 2, 3))

p = (1.0, 2.0, 1.0)
q = (3.0, 0.0, 2.0)
E1, E2, E3 = (1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)

# dashed verticals so the heights z = 1 and z = 2 can be read off the floor
S.drop(p)
S.drop(q)

# the three frame arrows at each point: same vector parts, different points of application
for X in (p, q):
    S.arrow(X, vadd(X, E1), PRACTICE, 2.3, head=8)   # U1: (1, 0, 0)
    S.arrow(X, vadd(X, E2), BASE, 2.3, head=8)       # U2: (0, 1, 0)
    S.arrow(X, vadd(X, E3), THEORY, 2.3, head=8)     # U3: (0, 0, 1)

S.point(p, TEXT, 3.8)
S.point(q, TEXT, 3.8)

# point labels
S.label(p, bold("p") + " = (1, 2, 1)", 8, -9, TEXT, 11, "start")
S.label(q, bold("q") + " = (3, 0, 2)", -9, -7, TEXT, 11, "end")

# arrow labels at p
S.label(vadd(p, E1), U("1", "p"), -4, 12, PRACTICE, 11, "end")
S.label(vadd(p, E2), U("2", "p"), 6, 4, BASE, 11, "start")
S.label(vadd(p, E3), U("3", "p"), 6, -4, THEORY, 11, "start")

# arrow labels at q
S.label(vadd(q, E1), U("1", "q"), -4, 12, PRACTICE, 11, "end")
S.label(vadd(q, E2), U("2", "q"), 4, 13, BASE, 11, "start")
S.label(vadd(q, E3), U("3", "q"), 6, -4, THEORY, 11, "start")

OUT["teget-dogal-cati"] = figure(
    400, 300, [P],
    "Doğal çatı <em>U</em><sub>1</sub>, <em>U</em><sub>2</sub>, <em>U</em><sub>3</sub>'ün "
    "<strong>p</strong> = (1, 2, 1) ve <strong>q</strong> = (3, 0, 2) noktalarındaki değerleri. "
    "Her noktada eksenlere paralel üç birim ok vardır: <em>U</em><sub>1</sub> için (1, 0, 0), "
    "<em>U</em><sub>2</sub> için (0, 1, 0), <em>U</em><sub>3</sub> için (0, 0, 1); aynı renk aynı alanı gösterir. "
    "<em>U</em><sub>1</sub>(<strong>p</strong>) ile <em>U</em><sub>1</sub>(<strong>q</strong>) paraleldir ama "
    "uygulama noktaları farklı olduğundan eşit değildir.",
    aria="Natural frame U1, U2, U3 at the points p = (1, 2, 1) and q = (3, 0, 2): three unit arrows "
         "parallel to the axes at each point, same colour for the same field",
)

# ============================================================ teget-donen-alan
# -*- coding: utf-8 -*-
# teget-donen-alan — the rotating field V(p) = (-p2, p1)_p on the integer grid -2..2.
# Arrows are drawn at 0.4 of their true length (stated in the caption).

SHRINK = 0.4
XR, YR = (-3.15, 3.15), (-3.1, 3.15)
p = cplane(20, 30, 330, XR, YR)
PPU = 330 / (XR[1] - XR[0])          # pixels per data unit

# faint integer grid over the lattice only
for k in range(-2, 3):
    p.line([(k, -2), (k, 2)], TEXT, 0.7, None, 0.16)
    p.line([(-2, k), (2, k)], TEXT, 0.7, None, 0.16)

p.origin_axes("x", "y")

NAMED = [(1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (-1, 1), (2, 0)]   # arrows in the text
ORIGIN = (0, 0)


def tip(a, b):
    """End point of the shortened arrow starting at (a, b)."""
    return (a - SHRINK * b, b + SHRINK * a)


# light arrows: the rest of the lattice
for a in range(-2, 3):
    for b in range(-2, 3):
        if (a, b) == ORIGIN or (a, b) in NAMED:
            continue
        p.arrow((a, b), tip(a, b), THEORY, 1.3, head=6, opacity=0.38)
        p.circle(a, b, 2.0 / PPU, THEORY, 0, None, THEORY, 0.45)

# dark arrows: the eight points of the example
for a, b in NAMED:
    p.arrow((a, b), tip(a, b), THEORY, 2.0, head=7)
for a, b in NAMED:
    dot(p, (a, b), THEORY, 3.2)
dot(p, ORIGIN, THEORY, 3.6)


def coords(a, b):
    def s(v):
        return (MINUS_S + str(-v)) if v < 0 else str(v)
    return "(" + s(a) + ", " + s(b) + ")"


# label placement: (dx, dy, anchor) chosen so that no arrow crosses the text
LAB = {
    (1, 0): (5, 13, "start"),
    (2, 0): (6, -6, "start"),
    (0, 1): (6, 13, "start"),
    (1, 1): (6, 13, "start"),
    (-1, 1): (6, 13, "start"),
    (-1, 0): (6, 13, "start"),
    (0, -1): (6, 13, "start"),
    (0, 0): (-6, -6, "end"),
}
for (a, b), (dx, dy, anc) in LAB.items():
    p.label(a, b, coords(a, b), dx, dy, TEXT, 10, anc)

# the field's formula above the panel
def ital(s):
    return '<tspan font-style="italic">' + s + '</tspan>'


p.text_px(p.x0 + p.w / 2, p.y0 - 17,
          ital("V") + "(" + bold("p") + ") = (" + MINUS_S + ital("p") + subs("2") + ", " + ital("p") + subs("1") + ")"
          + subs(bold("p")),
          TEXT, 11.5, "middle")

OUT["teget-donen-alan"] = figure(
    400, 380, [p],
    "Düzlemde <em>V</em>(<strong>p</strong>) = (&#8722;<em>p</em><sub>2</sub>, <em>p</em><sub>1</sub>)"
    "<sub><strong>p</strong></sub> alanının &#8722;2..2 tam sayı ızgarasındaki okları; örnekteki sekiz "
    "nokta koyu, ızgaranın geri kalanı açık mavidir. Okunaklılık için her ok gerçek uzunluğunun "
    "0,4 katıyla çizilmiştir; yönler ve uzunluk oranları doğrudur. Oklar başlangıç noktasının "
    "etrafında saat yönünün tersine döner, <strong>0</strong>'dan uzaklaştıkça uzar ve "
    "<strong>0</strong>'da sıfır olduğundan orada yalnızca nokta görünür.",
    aria="Duzlemde V(p) = (-p2, p1) vektor alaninin -2..2 tam sayi izgarasindaki oklari, "
         "0,4 katiyla kisaltilmis; sekiz ornek nokta koyu mavi, digerleri acik mavi; "
         "baslangic noktasinda ok yok, yalnizca nokta var.")

# ============================================================ teget-dort-vektor
# -*- coding: utf-8 -*-
# teget-dort-vektor: four tangent vectors at p = (1, 1, 0) — v_p, w_p, -2 v_p and v_p + w_p —
# with the parallelogram spanned by v_p and w_p (exercise "Lineer Birleşim ve Çizim").

cam = Camera(azimuth=35, elevation=22, scale=1.0)

p = (1.0, 1.0, 0.0)
v = (-2.0, 1.0, -1.0)
w = (0.0, 1.0, 3.0)
A = vadd(p, v)                    # (-1, 2, -1)   end of v_p
B = vadd(p, w)                    # (1, 2, 3)     end of w_p
C = vadd(p, vscale(-2.0, v))      # (5, -1, 2)    end of -2 v_p
D = vadd(p, vadd(v, w))           # (-1, 3, 2)    end of v_p + w_p

P = space_panel(20, 20, 360, (-4.0, 4.1), (-2.4, 3.6))
S = Space(P, cam)

# 1. floor: unit grid on z = 0 covering x in [-1, 5], y in [-1, 3]
for i in range(-1, 6):
    S.line([(i, -1, 0), (i, 3, 0)], TEXT, 0.7, None, 0.12)
for j in range(-1, 4):
    S.line([(-1, j, 0), (5, j, 0)], TEXT, 0.7, None, 0.12)

# 2. dashed coordinate guides for the four end points (floor L + riser)
def coord_guides(Q, opacity=0.38, foot=True):
    x, y, z = Q
    S.guide([(x, 0, 0), (x, y, 0), (0, y, 0)], TEXT, opacity)
    S.guide([(x, y, 0), Q], TEXT, opacity)
    if foot:
        S.point((x, y, 0), TEXT, 1.8)

for Q in (A, C, D):
    coord_guides(Q)
coord_guides(B, foot=False)     # its foot (1, 2, 0) would sit on the v_p arrow

# 3. parallelogram spanned by v_p and w_p: the two missing sides, dashed
S.guide([A, D], TEXT, 0.6, 1.2, "5 3")
S.guide([B, D], TEXT, 0.6, 1.2, "5 3")

# 4. axes and ticks
S.axes(6.0, 3.6, 3.6, xmin=-1.6, ymin=-1.6, zmin=0.0)
mfmt = lambda t: fmt(t).replace("-", MINUS_S)
S.ticks("x", (1, 2, 3, 4, 5), fmt_=mfmt, offset=(-8, 12))
S.ticks("y", (-1, 1, 2, 3), fmt_=mfmt)
S.ticks("z", (1, 2, 3), fmt_=mfmt)

# 5. the four tangent vectors
S.arrow(p, C, THEORY, 2.4, head=9, opacity=0.6)     # -2 v_p (same hue as v_p, faded)
S.arrow(p, A, THEORY, 2.4, head=9)                  # v_p
S.arrow(p, B, BASE, 2.4, head=9)                    # w_p
S.arrow(p, D, PRACTICE, 2.4, head=9)                # v_p + w_p

# 6. the point of application
S.point(p, TEXT, 3.8)

# 7. labels
vp = bold("v") + subs(bold("p"))
wp = bold("w") + subs(bold("p"))
S.label(p, bold("p") + " = (1, 1, 0)", 6, 25, TEXT, 11, "end")
S.label(vadd(p, vscale(0.565, v)), vp, 0, 19, THEORY, 12.5, "middle", True)
S.label(vadd(p, vscale(0.5, w)), wp, -5, 5, BASE, 12.5, "end", True)
S.label(vadd(p, vscale(0.544, vadd(v, w))), vp + " + " + wp, 0, -29, PRACTICE, 12.5, "middle", True)
S.label(vadd(p, vscale(-1.3, v)), MINUS_S + "2" + vp, 0, 18, THEORY, 12.5, "middle", True)

S.label(A, "(" + MINUS_S + "1, 2, " + MINUS_S + "1)", 7, 8, TEXT, 11, "start")
S.label(B, "(1, 2, 3)", 0, -10, TEXT, 11, "middle")
S.label(C, "(5, " + MINUS_S + "1, 2)", 6, -8, TEXT, 11, "start")
S.label(D, "(" + MINUS_S + "1, 3, 2)", 8, -12, TEXT, 11, "middle")

OUT["teget-dort-vektor"] = figure(
    400, 306, [P],
    "<strong>p</strong> = (1, 1, 0) noktasından çıkan dört teğet vektör: "
    "<strong>v</strong><sub><strong>p</strong></sub> = (&#8722;2, 1, &#8722;1)<sub><strong>p</strong></sub>, "
    "<strong>w</strong><sub><strong>p</strong></sub> = (0, 1, 3)<sub><strong>p</strong></sub>, "
    "&#8722;2<strong>v</strong><sub><strong>p</strong></sub> ve "
    "<strong>v</strong><sub><strong>p</strong></sub> + <strong>w</strong><sub><strong>p</strong></sub>. "
    "Her okun ucu, <strong>p</strong>'ye vektör kısmının eklenmesiyle bulunur; kesikli kılavuzlar uç "
    "noktaların koordinatlarını okutur. &#8722;2<strong>v</strong><sub><strong>p</strong></sub>, "
    "<strong>v</strong><sub><strong>p</strong></sub> ile aynı doğru üzerinde ters yönde ve iki kat "
    "uzundur; <strong>v</strong><sub><strong>p</strong></sub> + <strong>w</strong><sub><strong>p</strong></sub> "
    "ise <strong>v</strong><sub><strong>p</strong></sub> ile <strong>w</strong><sub><strong>p</strong></sub>'nin "
    "gerdiği paralelkenarın köşegenidir.",
    aria="p = (1, 1, 0) noktasindan cikan dort teget vektor: v_p, w_p, -2 v_p ve v_p + w_p; "
         "v_p ile w_p'nin gerdigi paralelkenarin kosegeni v_p + w_p'dir",
)

# ============================================================ teget-ok-koordinat-kutusu
# -*- coding: utf-8 -*-
# Tangent vector v_p = (2, 3, 2)_(1, 1, 3): arrow from p = (1, 1, 3) to p + v = (3, 4, 5),
# both points read off the axes through dashed coordinate boxes.

P = space_panel(30, 20, 330, (-1.6, 4.1), (-1.95, 4.1))
S = Space(P, Camera(azimuth=24, elevation=25, scale=0.72))

p = (1.0, 1.0, 3.0)
v = (2.0, 3.0, 2.0)
q = vadd(p, v)          # (3, 4, 5)


def box(pt, opacity):
    """All nine dashed edges of the coordinate box spanned by the origin and pt."""
    x, y, z = pt
    S.guide([(x, 0, 0), (x, y, 0), (0, y, 0)], TEXT, opacity)           # floor L
    S.guide([(x, 0, 0), (x, 0, z)], TEXT, opacity)                      # three risers
    S.guide([(x, y, 0), (x, y, z)], TEXT, opacity)
    S.guide([(0, y, 0), (0, y, z)], TEXT, opacity)
    S.guide([(0, 0, z), (x, 0, z), (x, y, z), (0, y, z), (0, 0, z)], TEXT, opacity)  # top


# floor grid on integer lines
for i in range(0, 5):
    S.line([(i, 0, 0), (i, 5, 0)], TEXT, 0.7, None, 0.12)
for j in range(0, 6):
    S.line([(0, j, 0), (4, j, 0)], TEXT, 0.7, None, 0.12)

box(q, 0.34)
box(p, 0.48)

S.axes(4.8, 5.4, 5.9)
S.ticks("x", (1, 2, 3, 4), offset=(-9, -6))
S.ticks("y", (1, 2, 3, 4, 5))
S.ticks("z", (1, 2, 3, 4, 5), offset=(-8, -2))

S.arrow(p, q, PRACTICE, 2.4, head=9)
S.point(p, TEXT, 3.6)
S.point(q, TEXT, 3.6)
S.point((0, 0, 0), TEXT, 2.4)

# Labels sit in the gap between the (0,1,.) riser and the (3,4,.) riser (p) and to the
# left of the (0,4,.) riser (p + v); two lines each so no dashed edge cuts through them.
S.label(p, bold("p"), 23, 12, TEXT, 11, "start")
S.label(p, "(1, 1, 3)", 23, 26, TEXT, 11, "start")
S.label(q, bold("p") + " + " + bold("v"), 8, 4, TEXT, 11, "start")
S.label(q, "(3, 4, 5)", 8, 18, TEXT, 11, "start")
S.label(vadd(p, vscale(0.42, v)), bold("v") + subs(bold("p")), -1, -9, PRACTICE, 12.5, "middle")
S.label((0, 0, 0), bold("0"), 1, 13, TEXT, 11, "middle")

OUT["teget-ok-koordinat-kutusu"] = figure(
    400, 395, [P],
    "Teğet vektör <strong>v</strong><sub><strong>p</strong></sub> = (2, 3, 2)<sub>(1, 1, 3)</sub>: "
    "uygulama noktası <strong>p</strong> = (1, 1, 3), bitiş noktası ise "
    "<strong>p</strong> + <strong>v</strong> = (3, 4, 5). Kesikli koordinat kutuları her iki "
    "noktanın koordinatlarını eksenlerden okutur; ok, iki noktayı birleştiren yönlü doğru "
    "parçasıdır. Aynı vektör kısmı <strong>0</strong> noktasında uygulansaydı ok orijinden "
    "(2, 3, 2) noktasına giderdi.",
    aria="Tangent vector v_p from p = (1, 1, 3) to p + v = (3, 4, 5) with dashed coordinate boxes")

# ============================================================ teget-paralel-vektorler
# -*- coding: utf-8 -*-
# teget-paralel-vektorler — two parallel tangent vectors in the plane (2D)
# v = (2, 1) applied at p = (1, 1) and at q = (4, 3).

P = cplane(30, 20, 340, (-0.5, 7.0), (-0.5, 4.8))

# light guide grid confined to the first quadrant (keeps tick numbers clear), then axes
for gx in (1, 2, 3, 4, 5, 6):
    P.line([(gx, 0), (gx, 4.8)], TEXT, 0.7, None, 0.13)
for gy in (1, 2, 3, 4):
    P.line([(0, gy), (7.0, gy)], TEXT, 0.7, None, 0.13)
P.origin_axes("x", "y", xticks=(1, 2, 3, 4, 5, 6), yticks=(1, 2, 3, 4))

p, q, v = (1, 1), (4, 3), (2, 1)
p_tip = (p[0] + v[0], p[1] + v[1])   # (3, 2)
q_tip = (q[0] + v[0], q[1] + v[1])   # (6, 4)

# the two arrows: same vector part, different points of application
P.arrow(p, p_tip, PRACTICE, 2.4, head=9)
P.arrow(q, q_tip, PRACTICE, 2.4, head=9)

# points of application
dot(P, p, TEXT, 3.8)
dot(P, q, TEXT, 3.8)

# labels — point names bold, vector names bold with bold subscript
P.label(p[0], p[1], bold("p") + " = (1, 1)", 7, 16, TEXT, 12, "start")
P.label(q[0], q[1], bold("q") + " = (4, 3)", 7, 16, TEXT, 12, "start")
P.label(p_tip[0], p_tip[1], "(3, 2)", 0, -9, TEXT, 10.5, "middle")
P.label(q_tip[0], q_tip[1], "(6, 4)", 0, -9, TEXT, 10.5, "middle")
P.label((p[0] + p_tip[0]) / 2, (p[1] + p_tip[1]) / 2,
        bold("v") + subs(bold("p")), -6, -10, PRACTICE, 12.5, "middle")
P.label((q[0] + q_tip[0]) / 2, (q[1] + q_tip[1]) / 2,
        bold("v") + subs(bold("q")), -6, -10, PRACTICE, 12.5, "middle")

OUT["teget-paralel-vektorler"] = figure(
    400, 275, [P],
    "Aynı vektör kısmı <strong>v</strong> = (2, 1), iki farklı noktaya uygulanmıştır: "
    "<strong>v</strong><sub><strong>p</strong></sub> oku <strong>p</strong> = (1, 1)'den (3, 2)'ye, "
    "<strong>v</strong><sub><strong>q</strong></sub> oku <strong>q</strong> = (4, 3)'ten (6, 4)'e gider. "
    "İki ok aynı uzunlukta ve aynı yöndedir; yalnızca uygulama noktaları farklıdır. "
    "Bu yüzden paraleldirler, ama teğet vektör olarak birbirine eşit değildirler.",
    aria="Duzlemde p=(1,1) noktasindan (3,2) noktasina giden v_p oku ile q=(4,3) noktasindan "
         "(6,4) noktasina giden v_q oku; ayni uzunluk ve yon, farkli uygulama noktalari")

# ============================================================ teget-paralelkenar
# -*- coding: utf-8 -*-
# teget-paralelkenar: parallelogram rule and scalar multiples of tangent vectors at p = (1, 1).
P = cplane(30, 16, 340, (-1.5, 5.75), (-1.5, 3.5))
P.origin_axes("x", "y", xticks=(-1, 1, 2, 3, 4, 5))
# y ticks by hand: the (-3/2)u_p shaft passes exactly through (0, 2), so that one
# label is nudged down-left, away from the shaft
ox = P.X(0)
for t, ddx, ddy in ((-1, 0, 0), (1, 0, 0), (2, -2, 3), (3, 0, 0)):
    P.add(f'<line x1="{ox-3:.1f}" y1="{P.Y(t):.1f}" x2="{ox+3:.1f}" y2="{P.Y(t):.1f}" '
          f'stroke="{TEXT}" stroke-width="1" opacity="0.7"/>')
    P.add(f'<text x="{ox-7+ddx:.1f}" y="{P.Y(t)+4+ddy:.1f}" fill="{TEXT}" font-size="11" '
          f'opacity="0.7" text-anchor="end">{fmt(t)}</text>')

p = (1.0, 1.0)
v_end, w_end, s_end = (4.0, 1.0), (2.0, 3.0), (5.0, 3.0)
u_end, u2_end, u32_end = (2.0, 0.0), (3.0, -1.0), (-0.5, 2.5)

# parallelogram completed with dashed guides
guide(P, [v_end, s_end], TEXT, 0.55)
guide(P, [w_end, s_end], TEXT, 0.55)

# scalar multiples of u_p (green): 2u_p drawn first, wide and translucent, u_p on top of it.
# Shaft and head go into one <g opacity> so the two shapes stay fully opaque relative to
# each other: a plain arrow(..., opacity=0.5) darkens where the round shaft end overlaps
# the head and leaves a blot inside the arrowhead.
def translucent_arrow(pl, p0, p1, color, width, head, opacity):
    x0, y0, x1, y1 = pl.X(p0[0]), pl.Y(p0[1]), pl.X(p1[0]), pl.Y(p1[1])
    dx, dy = x1 - x0, y1 - y0
    length = math.hypot(dx, dy)
    ux, uy = dx / length, dy / length
    px, py, hw = -uy, ux, head * 0.42
    sx, sy = x1 - ux * head * 0.8, y1 - uy * head * 0.8   # flat shaft end, inside the head
    pl.add(f'<g opacity="{opacity}">'
           f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{sx:.1f}" y2="{sy:.1f}" '
           f'stroke="{color}" stroke-width="{width}" stroke-linecap="butt"/>'
           f'<polygon points="{x1:.1f},{y1:.1f} {x1-ux*head+px*hw:.1f},{y1-uy*head+py*hw:.1f} '
           f'{x1-ux*head-px*hw:.1f},{y1-uy*head-py*hw:.1f}" fill="{color}"/></g>')


translucent_arrow(P, p, u2_end, BASE, 3.4, head=10, opacity=0.5)
P.arrow(p, u_end, BASE, 2.0, head=8)
P.arrow(p, u32_end, BASE, 2.0, head=8)

# v_p, w_p (blue) and their sum (red)
P.arrow(p, v_end, THEORY, 2.0, head=8.5)
P.arrow(p, w_end, THEORY, 2.0, head=8.5)
P.arrow(p, s_end, PRACTICE, 2.2, head=9)

dot(P, p, TEXT, 3.8)

# labels
P.label(1, 1, bold("p"), -9, 13, TEXT, 12, "end", True)
P.label(2.5, 1, bold("v") + subs(bold("p")), 0, 16, THEORY, 12, "middle", True)
P.label(1.5, 2, bold("w") + subs(bold("p")), -7, 4, THEORY, 12, "end", True)
P.label(2.9, 2.5, bold("v") + subs(bold("p")) + " + " + bold("w") + subs(bold("p")),
        0, 4, PRACTICE, 12, "middle", True)
P.label(1.5, 0.5, bold("u") + subs(bold("p")), 6, -6, BASE, 12, "start", True)
P.label(2.5, -0.5, "2" + bold("u") + subs(bold("p")), -8, 12, BASE, 12, "end", True)
P.label(0, 2.75, "(" + MINUS_S + "3/2)" + bold("u") + subs(bold("p")), -5, 4, BASE, 12, "end", True)

OUT["teget-paralelkenar"] = figure(
    400, 290, [P],
    "<strong>p</strong> = (1, 1) noktasındaki teğet vektörler ok olarak çizilmiştir. "
    "<strong>v</strong><sub><strong>p</strong></sub> = (3, 0)<sub><strong>p</strong></sub> ve "
    "<strong>w</strong><sub><strong>p</strong></sub> = (1, 2)<sub><strong>p</strong></sub> bir paralelkenar gerer; "
    "kesikli kenarlarla tamamlanan bu paralelkenarın <strong>p</strong>&#8217;den çıkan köşegeni toplam "
    "<strong>v</strong><sub><strong>p</strong></sub> + <strong>w</strong><sub><strong>p</strong></sub> = (4, 2)<sub><strong>p</strong></sub>&#8217;dir. "
    "Yeşil oklar skaler katı gösterir: 2<strong>u</strong><sub><strong>p</strong></sub>, "
    "<strong>u</strong><sub><strong>p</strong></sub> = (1, &#8722;1)<sub><strong>p</strong></sub> ile aynı yönde ve iki kat uzun, "
    "&#8722;(3/2)<strong>u</strong><sub><strong>p</strong></sub> ise ters yönde ve bir buçuk kat uzundur.",
    aria="Tangent vectors at p = (1, 1): v_p and w_p span a parallelogram whose diagonal is v_p + w_p; "
         "the green arrows u_p, 2u_p and (-3/2)u_p show scalar multiples along one line",
)

# ============================================================ teget-uzayi-demet
# -*- coding: utf-8 -*-
# teget-uzayi-demet: the bundle of six tangent vectors at p = (2, 2),
# plus the stray (1, 2)_q at q = (0, 0) that does not belong to T_p.
P = cplane(10, 14, 380, (-1.35, 6.3), (-0.95, 4.75))
P.grid(xs=(1, 2, 3, 4, 5, 6), ys=(1, 2, 3, 4))
P.origin_axes("x", "y", xticks=(1, 2, 3, 4, 5), yticks=(1, 2, 3, 4))

p, q = (2.0, 2.0), (0.0, 0.0)
vecs = [(1, 2), (3, 1), (2, -1), (-2, -1), (-1, -2), (0, -2)]


def num(n):
    return (MINUS_S + str(-n)) if n < 0 else str(n)


def vlabel(v, sub):
    """'(a, b)' with a bold subscript naming the point of application."""
    return "(" + num(v[0]) + ", " + num(v[1]) + ")" + subs(bold(sub))


# the stray arrow at q first, so the bundle at p is painted over it
P.arrow(q, (1.0, 2.0), TEXT, 1.8, head=8, dash="5 4", opacity=0.55)

for v in vecs:
    P.arrow(p, (p[0] + v[0], p[1] + v[1]), PRACTICE, 2.2, head=8)

dot(P, p, TEXT, 3.8)
dot(P, q, TEXT, 3.8)

# point labels
P.label(2, 2, bold("p") + " = (2, 2)", 22, 5, TEXT, 12, "start")
P.label(0, 0, bold("q") + " = (0, 0)", -7, 15, TEXT, 12, "end")

# tangent-vector labels, each beside its own tip / shaft
P.label(3, 4, vlabel((1, 2), "p"), 8, 4, PRACTICE, 11)
P.label(5, 3, vlabel((3, 1), "p"), 8, 4, PRACTICE, 11)
P.label(4, 1, vlabel((2, -1), "p"), 8, 4, PRACTICE, 11)
P.label(0, 1, vlabel((-2, -1), "p"), -9, -12, PRACTICE, 11, "end")
P.label(1, 0, vlabel((-1, -2), "p"), 0, 31, PRACTICE, 11, "middle")
P.label(2, 0.5, vlabel((0, -2), "p"), 8, 4, PRACTICE, 11)

# the stray arrow's two-line note, above-left of its tip (1, 2)
P.add('<g opacity="0.65">')
P.label(0, 2, vlabel((1, 2), "q"), 12, -24, TEXT, 11)
P.label(0, 2, '<tspan font-style="italic">T</tspan>' + subs(bold("p")) + "&#8217;de değil", 12, -9, TEXT, 11)
P.add('</g>')

OUT["teget-uzayi-demet"] = figure(
    400, 313, [P],
    "<strong>p</strong> = (2, 2) noktasından çıkan altı ok, (1, 2)<sub><strong>p</strong></sub>, "
    "(3, 1)<sub><strong>p</strong></sub>, (2, &#8722;1)<sub><strong>p</strong></sub>, "
    "(&#8722;2, &#8722;1)<sub><strong>p</strong></sub>, (&#8722;1, &#8722;2)<sub><strong>p</strong></sub> ve "
    "(0, &#8722;2)<sub><strong>p</strong></sub> teğet vektörleridir; bitiş noktaları sırasıyla (3, 4), (5, 3), "
    "(4, 1), (0, 1), (1, 0) ve (2, 0)'dır. Teğet uzayı <em>T</em><sub><strong>p</strong></sub>(&#8477;<sup>2</sup>), "
    "bu okların ve <strong>p</strong>'den çıkan bütün diğer okların oluşturduğu demettir. "
    "Kesikli gri ok (1, 2)<sub><strong>q</strong></sub> ise <strong>q</strong> = (0, 0)'dan çıkar: vektör kısmı "
    "(1, 2)<sub><strong>p</strong></sub> ile aynı olduğu hâlde uygulama noktası farklı olduğundan "
    "<em>T</em><sub><strong>p</strong></sub>(&#8477;<sup>2</sup>)'ye ait değildir.",
    aria="Duzlemde p=(2,2) noktasindan cikan alti teget vektor oku: bitisleri (3,4), (5,3), (4,1), (0,1), (1,0), (2,0); ayrica q=(0,0) noktasindan (1,2) noktasina giden kesikli gri ok, T_p'ye ait degildir")

# ============================================================ teget-vektor-anatomisi
# -*- coding: utf-8 -*-
# teget-vektor-anatomisi — the two ingredients of a tangent vector in the plane (2D).
# Vector part v = (3, 1) drawn from the origin (grey, dashed); point of application p = (1, 2);
# tangent vector v_p drawn from p to p + v = (4, 3) (thick, orange). Dotted edges 0-p and
# (3, 1)-(4, 3) close the parallelogram: both arrows perform the same displacement.

P = cplane(30, 20, 340, (-0.6, 5.0), (-0.6, 3.8))

O = (0.0, 0.0)
p = (1.0, 2.0)
v = (3.0, 1.0)
a = v                                  # tip of the vector part drawn from 0
b = (p[0] + v[0], p[1] + v[1])         # p + v = (4, 3)


def halo(x, y, s, dx=0, dy=0, color=TEXT, size=11.5, anchor="start", fill_opacity=1.0):
    """Label at a data point with a page-coloured halo, so grid lines behind it break."""
    fo = f' fill-opacity="{fill_opacity}"' if fill_opacity < 1.0 else ""
    P.add(f'<text x="{P.X(x) + dx:.1f}" y="{P.Y(y) + dy:.1f}" fill="{color}"{fo} font-size="{size}" '
          f'text-anchor="{anchor}" stroke="{BG}" stroke-width="3.2" stroke-linejoin="round" '
          f'paint-order="stroke">{s}</text>')


def dashed_arrow(p0, p1, color, width, head, dash, opacity):
    """Translucent dashed arrow. Shaft and head share one <g opacity> so they do not darken
    where they overlap; the shaft is drawn from the head backwards so a full dash meets the head."""
    x0, y0, x1, y1 = P.X(p0[0]), P.Y(p0[1]), P.X(p1[0]), P.Y(p1[1])
    L = math.hypot(x1 - x0, y1 - y0)
    ux, uy = (x1 - x0) / L, (y1 - y0) / L
    px, py, hw = -uy, ux, head * 0.42
    sx, sy = x1 - ux * head * 0.85, y1 - uy * head * 0.85
    P.add(f'<g opacity="{opacity}">'
          f'<line x1="{sx:.1f}" y1="{sy:.1f}" x2="{x0:.1f}" y2="{y0:.1f}" stroke="{color}" '
          f'stroke-width="{width}" stroke-dasharray="{dash}" stroke-linecap="butt"/>'
          f'<polygon points="{x1:.1f},{y1:.1f} {x1 - ux * head + px * hw:.1f},{y1 - uy * head + py * hw:.1f} '
          f'{x1 - ux * head - px * hw:.1f},{y1 - uy * head - py * hw:.1f}" fill="{color}"/></g>')


# 1. light grid on the integer lines of the first quadrant, then axes
for gx in (1, 2, 3, 4):
    P.line([(gx, 0), (gx, 3.8)], TEXT, 0.7, None, 0.13)
for gy in (1, 2, 3):
    P.line([(0, gy), (5.0, gy)], TEXT, 0.7, None, 0.13)
P.origin_axes("x", "y", xticks=(1, 2, 3, 4), yticks=(1, 2, 3))

# 2. dotted edges closing the parallelogram 0, (3, 1), (4, 3), p
P.line([O, p], TEXT, 1.6, "0.1 3.8", 0.6)
P.line([a, b], TEXT, 1.6, "0.1 3.8", 0.6)

# 3. vector part (grey, dashed, translucent) and the tangent vector v_p (thick orange)
dashed_arrow(O, a, TEXT, 1.8, 9, "6 4", 0.55)
P.arrow(p, b, PRACTICE, 2.8, head=10.5)

# 4. points
dot(P, O, TEXT, 2.6)
dot(P, p, TEXT, 3.8)

# 5. labels (name and note 15 px apart in both groups)
halo(0, 0, bold("0"), -7, 14, TEXT, 11, "end")

# vector part: below the grey arrow, name first, note underneath
halo(2.35, 0, bold("v") + " = (3, 1)", 0, -30, TEXT, 11.5, "start")
halo(2.35, 0, "vektör kısmı", 0, -15, TEXT, 10, "start", 0.72)

# point of application: above-left of p, note on top, name next to the point
halo(0.8, 2, "uygulama noktası", 0, -32, TEXT, 10, "middle", 0.72)
halo(0.8, 2, bold("p") + " = (1, 2)", 0, -17, TEXT, 11.5, "middle")

# tangent vector and its tip
halo(2.5, 2.5, bold("v") + subs(bold("p")), -4, -15, PRACTICE, 12.5, "middle")
halo(4, 3, bold("p") + " + " + bold("v") + " = (4, 3)", -6, -13, TEXT, 11.5, "middle")

OUT["teget-vektor-anatomisi"] = figure(
    400, 300, [P],
    "Bir teğet vektör iki bilgiden oluşur: nereden çıktığını söyleyen uygulama noktası "
    "<strong>p</strong> = (1, 2) ve ne kadar yer değiştirdiğini söyleyen vektör kısmı "
    "<strong>v</strong> = (3, 1). Teğet vektör <strong>v</strong><sub><strong>p</strong></sub>, "
    "<strong>p</strong>'den <strong>p</strong> + <strong>v</strong> = (4, 3) noktasına giden ok olarak "
    "resmedilir; kesikli gri ok aynı yer değiştirmeyi <strong>0</strong> noktasından yapar. "
    "Noktalı kenarlar bu iki okun bir paralelkenarın karşılıklı kenarları olduğunu gösterir.",
    aria="Duzlemde teget vektor: 0'dan (3, 1)'e kesikli gri v oku (vektor kismi), uygulama noktasi "
         "p = (1, 2), p'den p + v = (4, 3)'e kalin turuncu v_p oku; noktali kenarlar paralelkenari tamamlar",
)

# ============================================================ teget-vektor-esitligi
# -*- coding: utf-8 -*-
# teget-vektor-esitligi: the equality rule for tangent vectors in R^3.
# v = (1, 2, 2) applied at p = (1, 1, 1) and at q = (3, 2, 1) gives two parallel orange arrows
# (same vector part, different points); w = (2, -1, 1) applied at p gives a green arrow
# (same point, different vector part).
# Camera az=20, el=27 (from _scan_esitlik2.py): the parallel arrows stay ~50 px apart and v_q
# crosses the projected y axis at y ~ 1.6, between two ticks.

P = space_panel(30, 20, 340, (-1.9, 4.8), (-2.5, 3.45))
S = Space(P, Camera(azimuth=20, elevation=27, scale=1.0))

p = (1.0, 1.0, 1.0)
q = (3.0, 2.0, 1.0)
v = (1.0, 2.0, 2.0)
w = (2.0, -1.0, 1.0)
vp_tip = vadd(p, v)     # (2, 3, 3)
vq_tip = vadd(q, v)     # (4, 4, 3)
wp_tip = vadd(p, w)     # (3, 0, 2)

# 1. floor grid, axes, ticks (x labels sit left of the steep x axis, y labels right of the grid lines)
S.floor_grid((0, 4), (0, 4), n=4, opacity=0.12)
S.axes(4.6, 4.7, 3.4)
S.ticks("x", (1, 2, 3, 4), offset=(-10, -2))
S.ticks("y", (1, 2, 3, 4), offset=(3, 13))
S.ticks("z", (1, 2, 3))

# 2. dashed verticals from the points of application down to the floor
S.drop(p)
S.drop(q)

# 3. the three tangent vectors
S.arrow(p, wp_tip, BASE, 2.4, head=9)
S.arrow(p, vp_tip, PRACTICE, 2.4, head=9)
S.arrow(q, vq_tip, PRACTICE, 2.4, head=9)

# 4. points of application
S.point(p, TEXT, 3.8)
S.point(q, TEXT, 3.8)

# 5. labels: point names bold, vector names bold with bold subscripts;
#    v_p and v_q sit at the same spot of their arrows to stress the equal vector parts
vp = bold("v") + subs(bold("p"))
vq = bold("v") + subs(bold("q"))
wp = bold("w") + subs(bold("p"))
S.label(p, bold("p"), -6, -10, TEXT, 12, "end")
S.label(q, bold("q"), 7, 14, TEXT, 12, "start")
S.label(vadd(p, vscale(0.6, v)), vp, -7, -8, PRACTICE, 12.5, "end")
S.label(vadd(q, vscale(0.6, v)), vq, -7, -8, PRACTICE, 12.5, "end")
S.label(vadd(p, vscale(0.72, w)), wp, 0, -9, BASE, 12.5, "middle")

OUT["teget-vektor-esitligi"] = figure(
    400, 340, [P],
    "<strong>v</strong><sub><strong>p</strong></sub> ile <strong>v</strong><sub><strong>q</strong></sub>'nun "
    "vektör kısmı aynı <strong>v</strong> = (1, 2, 2) olduğundan oklar paralel ve eşit uzunluktadır; "
    "ancak uygulama noktaları <strong>p</strong> = (1, 1, 1) ile <strong>q</strong> = (3, 2, 1) farklı "
    "olduğu için bunlar farklı teğet vektörlerdir. "
    "<strong>v</strong><sub><strong>p</strong></sub> ile <strong>w</strong><sub><strong>p</strong></sub> "
    "aynı <strong>p</strong> noktasında durur, fakat vektör kısımları <strong>v</strong> ile "
    "<strong>w</strong> = (2, &#8722;1, 1) farklı olduğundan onlar da farklıdır. "
    "İki teğet vektörün eşit olması için vektör kısımlarının ve uygulama noktalarının ikisinin "
    "birden aynı olması gerekir.",
    aria="R3'te teget vektor esitligi: p = (1, 1, 1) noktasindan (2, 3, 3) noktasina v_p ve "
         "q = (3, 2, 1) noktasindan (4, 4, 3) noktasina v_q turuncu, paralel ve esit uzunlukta oklar; "
         "p noktasindan (3, 0, 2) noktasina w_p yesil ok",
)

# ============================================================ toplam-paralelkenar
# -*- coding: utf-8 -*-
# toplam-paralelkenar: p = (1, 2, 0), q = (2, 0, 1) and the points p + q = (3, 2, 1),
# 2p = (2, 4, 0), (p + q)/2 = (3/2, 1, 1/2) from the example "Toplam ve Skaler Kat Hesabi".
# Colour convention: p -> THEORY, q -> BASE (second vector), p + q -> PRACTICE (the sum),
# 2p -> THEORY faded (same direction as p), midpoint -> hollow PRACTICE circle.

O = (0.0, 0.0, 0.0)
p = (1.0, 2.0, 0.0)
q = (2.0, 0.0, 1.0)
s = vadd(p, q)                 # (3, 2, 1)
d = vscale(2.0, p)             # (2, 4, 0)
m = vscale(0.5, s)             # (3/2, 1, 1/2)

P = space_panel(22, 18, 356, (-2.35, 3.05), (-2.0, 1.75))
S = Space(P, Camera(azimuth=42, elevation=28, scale=0.78))

# 1. floor grid on the integer lines, x in [0, 3], y in [0, 4]
for i in range(0, 4):
    S.line([(i, 0, 0), (i, 4, 0)], TEXT, 0.7, None, 0.12)
for j in range(0, 5):
    S.line([(0, j, 0), (3, j, 0)], TEXT, 0.7, None, 0.12)

# 2. dashed helpers: coordinate box of p + q, riser under q, parallelogram edges, p-q segment
S.coordinate_box(s, opacity=0.40)
S.guide([(2, 0, 0), q], TEXT, 0.40)                  # q sits above the x axis at x = 2
S.guide([p, s], TEXT, 0.60, 1.2, "5 3")              # p -> p + q (parallel to q)
S.guide([q, s], TEXT, 0.60, 1.2, "5 3")              # q -> p + q (parallel to p)
S.guide([p, q], TEXT, 0.50, 0.9, "3 3")              # segment whose midpoint is (p + q)/2

# 3. axes and ticks
S.axes(3.9, 4.9, 2.3)
S.ticks("x", (1, 2, 3))
S.ticks("y", (1, 2, 3, 4))
S.ticks("z", (1, 2))

# 4. arrows: 2p first (faded, wider), then p over it, then q and p + q
S.arrow(O, d, THEORY, 3.2, head=10, opacity=0.45)   # 2p = (2, 4, 0)
S.arrow(O, p, THEORY, 2.4, head=9)                  # p = (1, 2, 0)
S.arrow(O, q, BASE, 2.4, head=9)                    # q = (2, 0, 1)
S.arrow(O, s, PRACTICE, 2.4, head=9)                # p + q = (3, 2, 1)

# 5. points
S.point(O, TEXT, 2.6)
S.point((3, 2, 0), TEXT, 1.8)                        # foot of p + q on the floor
S.hollow(m, PRACTICE, 3.4, 1.6)                      # (p + q)/2

# 6. labels
S.label(O, bold("0"), 2, 13, TEXT, 11, "middle")
S.label(p, bold("p") + " = (1, 2, 0)", 8, 12, THEORY, 11.5, "start")
S.label(q, bold("q") + " = (2, 0, 1)", -8, -6, BASE, 11.5, "end")
S.label(s, bold("p") + " + " + bold("q") + " = (3, 2, 1)", -9, -8, PRACTICE, 11.5, "end")
S.label(d, "2" + bold("p") + " = (2, 4, 0)", 9, 5, THEORY, 11.5, "start")
S.label(m, "(" + bold("p") + " + " + bold("q") + ")/2 = (3/2, 1, 1/2)", 6, 15, TEXT, 10.5, "start")

OUT["toplam-paralelkenar"] = figure(
    400, 292, [P],
    "<strong>p</strong> = (1, 2, 0) ve <strong>q</strong> = (2, 0, 1) için toplam ve skaler kat. "
    "<strong>p</strong> + <strong>q</strong> = (3, 2, 1), başlangıç noktasından çıkan <strong>p</strong> "
    "ve <strong>q</strong> oklarının gerdiği paralelkenarın karşı köşesidir; kesikli kenarlar "
    "paralelkenarı tamamlar, kesikli koordinat kutusu ise (3, 2, 1) koordinatlarını eksenlerden okutur. "
    "2<strong>p</strong> = (2, 4, 0), <strong>p</strong> okunun aynı doğrultuda iki katına uzatılmışıdır. "
    "<strong>p</strong> ile <strong>q</strong>'yu birleştiren ince parçanın orta noktası "
    "(<strong>p</strong> + <strong>q</strong>)/2 = (3/2, 1, 1/2), toplam okunun tam ortasında durur.",
    aria="p = (1, 2, 0) ve q = (2, 0, 1) oklari, paralelkenarin karsi kosesi p + q = (3, 2, 1), "
         "uzatilmis ok 2p = (2, 4, 0) ve p ile q'yu birlestiren parcanin orta noktasi (p + q)/2 = (3/2, 1, 1/2)",
)

# ============================================================ yonlu-dogru-boyunca-grafik
# -*- coding: utf-8 -*-
# Graph of t -> f(p + tv) = -3t - 6t^2 - 3t^3 with its tangent line at t = 0 (slope -3).


def g_line(t):
    """f evaluated along the line p + tv, with f = x^2 y z, p = (1, 1, 0), v = (1, 0, -3)."""
    return -3 * t - 6 * t ** 2 - 3 * t ** 3


def mfmt(v):
    """Tick label with a Turkish decimal comma and a real minus sign."""
    return tfmt(v).replace("-", MINUS_S)


def ital(s):
    """Italic run inside an SVG <text> — function and variable names."""
    return f'<tspan font-style="italic">{s}</tspan>'


F, T = ital("f"), ital("t")

p = Plot(48, 26, 306, 206, (-1.5, 0.8), (-2.4, 1.7))
p.origin_axes("t", "f(" + bold("p") + " + t" + bold("v") + ")",
              xticks=(-1.5, -1, -0.5, 0.5), yticks=(-2, -1, 1), xfmt=mfmt, yfmt=mfmt)

# tangent line at t = 0: value -3t (dashed, PRACTICE)
p.line([(-0.55, 1.65), (0.75, -2.25)], PRACTICE, 1.7, "6 4")

# the graph itself (clipped where it leaves the panel at the bottom)
clipped(p, g_line, -1.5, 0.8, THEORY, 2.0)

# marked points (both lie on the graph, so both are filled): (0, 0) where the tangent
# touches, (-1, 0) where the value is 0 again
dot(p, (-1.0, 0.0), TEXT, 3.2)
dot(p, (0.0, 0.0), TEXT, 3.8)
p.label(0.0, 0.0, "(0, 0)", 7, -7, TEXT, 11.5)
p.label(-1.0, 0.0, "(" + MINUS_S + "1, 0)", 8, -20, TEXT, 11.5)

# slope label next to the upper-left part of the tangent
p.label(-0.55, 1.2, "eğim = " + bold("v") + subs(bold("p")) + "[" + F + "] = " + MINUS_S + "3",
        0, 0, PRACTICE, 11.5, "end")

# formula of the graph (legend for the blue curve), in the empty lower-left region
p.text_px(54, p.Y(-1.5),
          F + "(" + bold("p") + " + " + T + bold("v") + ") = " + MINUS_S + "3" + T + " "
          + MINUS_S + " 6" + T + sups("2") + " " + MINUS_S + " 3" + T + sups("3"),
          THEORY, 11.5)

OUT["yonlu-dogru-boyunca-grafik"] = figure(
    400, 255, [p],
    "<strong>p</strong> + <em>t</em><strong>v</strong> doğrusu boyunca <em>f</em>'nin değeri: "
    "yatay eksen <em>t</em>, düşey eksen <em>f</em>(<strong>p</strong> + <em>t</em><strong>v</strong>) "
    "= &#8722;3<em>t</em> &#8722; 6<em>t</em><sup>2</sup> &#8722; 3<em>t</em><sup>3</sup>. "
    "Grafik (0, 0) noktasından geçer ve oradaki teğetinin eğimi "
    "<strong>v</strong><sub><strong>p</strong></sub>[<em>f</em>] = &#8722;3'tür; "
    "<em>t</em> &gt; 0 olur olmaz eğri yatay eksenin altına iner, yani <strong>p</strong>'den "
    "<strong>v</strong> yönünde yola çıkınca <em>f</em> azalır. "
    "<em>t</em> = &#8722;1'de değer yine 0'dır: doğrunun o noktası (0, 1, 3)'tür ve "
    "birinci koordinatı sıfır olduğundan <em>f</em> orada sıfırlanır.",
    aria="t eksenine gore f(p+tv) = -3t - 6t^2 - 3t^3 grafigi, (0,0) noktasi ve egimi -3 olan kesikli teget dogru",
)

# ============================================================ yonlu-dogru-p-v
# -*- coding: utf-8 -*-
# yonlu-dogru-p-v: the line p + t v through p = (1, 1, 0) in the direction
# v = (1, 0, -3), with the points at t = -1, 0, 1 and the tangent vector v_p.

_P = space_panel(84, 18, 235, (-2.4, 2.6), (-4.0, 3.6))
_S = Space(_P, Camera(azimuth=33, elevation=20, scale=1.0))

_p = (1.0, 1.0, 0.0)
_v = (1.0, 0.0, -3.0)
_q = vadd(_p, _v)              # (2, 1, -3)
_m = vadd(_p, vscale(-1, _v))  # (0, 1, 3)


def _line(t):
    return (1.0 + t, 1.0, -3.0 * t)


def _mfmt(v):
    return fmt(v).replace("-", MINUS_S)


# floor and axes
_S.floor_grid((0, 2.5), (0, 2.5), n=5, opacity=0.10)
_S.axes(2.9, 2.9, 3.35, zmin=-3.3)
_S.ticks("x", (1, 2))
_S.ticks("y", (1, 2), offset=(3, 13))
_S.ticks("z", (1, 2, 3), offset=(-14, 4))

# dashed coordinate guides for p and p + v, and a faint drop for the t = -1 point
_S.guide([(1, 0, 0), (1, 1, 0), (0, 1, 0)], TEXT, 0.45)
_S.guide([(2, 0, 0), (2, 1, 0)], TEXT, 0.45)
_S.guide([(2, 1, 0), _q], TEXT, 0.45)
_S.guide([_q, (0, 0, -3)], TEXT, 0.45)
_S.guide([_m, (0, 1, 0)], TEXT, 0.28)

# the line p + t v, extended past t = -1 and t = 1
_S.curve(_line, -1.08, 1.08, THEORY, 1.3, samples=2, opacity=0.8)

# the tangent vector v_p from p to p + v
_S.arrow(_p, _q, PRACTICE, 2.4, head=9)

# marked points
_S.point(_m, TEXT, 3.2)
_S.point(_p, TEXT, 3.6)
_S.point(_q, TEXT, 3.2)

# negative z ticks, labelled left of the dashed riser from (2, 1, 0)
_S.ticks("z", (-1, -2, -3), fmt_=_mfmt, offset=(-14, 4))

# labels
_S.label(_m, "t = " + MINUS_S + "1", 9, -1, TEXT, 11.5)
_S.label(_m, "(0, 1, 3)", 9, 12, TEXT, 10.5)
_S.label(_p, "t = 0 (" + bold("p") + ")", 9, 14, TEXT, 11.5)
_S.label(_p, "(1, 1, 0)", 9, 26, TEXT, 10.5)
_S.label(_q, "t = 1 (" + bold("p") + " + " + bold("v") + ")", -12, -2, TEXT, 11.5, "end")
_S.label(_q, "(2, 1, " + MINUS_S + "3)", -12, 11, TEXT, 10.5, "end")
_S.label(_line(0.3), bold("v") + subs(bold("p")), 9, 4, PRACTICE, 12.5, "start", True)

OUT["yonlu-dogru-p-v"] = figure(
    400, 400, [_P],
    "<strong>p</strong> = (1, 1, 0) noktasından geçen ve <strong>v</strong> = (1, 0, &#8722;3) "
    "doğrultusundaki <em>t</em> &#8614; (1 + <em>t</em>, 1, &#8722;3<em>t</em>) doğrusu. "
    "<em>t</em> = &#8722;1, 0, 1 anlarında doğru (0, 1, 3), <strong>p</strong> ve "
    "<strong>p</strong> + <strong>v</strong> = (2, 1, &#8722;3) noktalarından geçer; "
    "<strong>v</strong><sub><strong>p</strong></sub> oku <strong>p</strong>'den "
    "<strong>p</strong> + <strong>v</strong>'ye uzanır. Yönlü türev "
    "<strong>v</strong><sub><strong>p</strong></sub>[<em>f</em>] yalnızca <em>f</em>'nin bu doğru "
    "üzerindeki değerlerine bağlıdır: <em>t</em> = 0 anındaki değişim hızıdır.",
    aria="p=(1,1,0) noktasindan gecen, v=(1,0,-3) dogrultusundaki dogru; t=-1, 0, 1 anlarindaki "
         "(0,1,3), (1,1,0), (2,1,-3) noktalari ve p'den p+v'ye v_p oku",
)

# ============================================================ yonlu-donen-alan-seviye
# -*- coding: utf-8 -*-
# yonlu-donen-alan-seviye — level circles f = x^2 + y^2 = 1, 2, 4 and the rotating
# field V = -y U1 + x U2 at ten points; every arrow is tangent to the circle it sits on,
# so V[f] = 0. At (1, 1) the gradient (2, 2) and V(1, 1) = (-1, 1) are perpendicular.
# Arrows are drawn at half their true length (stated in the caption).

import math

SHRINK = 0.5
XR, YR = (-2.45, 2.8), (-2.45, 2.55)
p = cplane(36, 34, 315, XR, YR)


def ital(s):
    return '<tspan font-style="italic">' + s + '</tspan>'


def halo_text(pl, x, y, s, dx=0, dy=0, color=TEXT, size=11, anchor="middle", opacity=1.0):
    """Label with a page-background halo so it can sit on a faint line."""
    px, py = pl.X(x) + dx, pl.Y(y) + dy
    pl.add(f'<text x="{px:.1f}" y="{py:.1f}" fill="{BG}" stroke="{BG}" stroke-width="4" '
           f'stroke-linejoin="round" font-size="{size}" text-anchor="{anchor}">{s}</text>')
    pl.add(f'<text x="{px:.1f}" y="{py:.1f}" fill="{color}" font-size="{size}" '
           f'text-anchor="{anchor}" opacity="{opacity}">{s}</text>')


def boxed_text(pl, x, y, s, width, dx=0, dy=0, color=TEXT, size=11, anchor="end", pad=2.0):
    """Label on an opaque page-background box: hides an axis line or an arc that would
    otherwise show through the thin glyphs (minus sign, equals sign) of a halo-only label."""
    px, py = pl.X(x) + dx, pl.Y(y) + dy
    if anchor == "end":
        bx = px - width
    elif anchor == "middle":
        bx = px - width / 2
    else:
        bx = px
    top, bottom = py - 0.75 * size - pad, py + 0.25 * size + pad
    pl.add(f'<rect x="{bx - pad:.1f}" y="{top:.1f}" width="{width + 2 * pad:.1f}" '
           f'height="{bottom - top:.1f}" fill="{BG}" stroke="none"/>')
    pl.add(f'<text x="{px:.1f}" y="{py:.1f}" fill="{color}" font-size="{size}" '
           f'text-anchor="{anchor}">{s}</text>')


def num_label(x, y, s, dx, dy, anchor):
    """Coordinate number next to a lattice point on an axis."""
    p.add(f'<text x="{p.X(x)+dx:.1f}" y="{p.Y(y)+dy:.1f}" fill="{TEXT}" font-size="10.5" '
          f'text-anchor="{anchor}" opacity="0.75">{s}</text>')


# level circles f = 1, 2, 4 (gray)
for r in (1.0, math.sqrt(2), 2.0):
    p.circle(0, 0, r, TEXT, 1.2, None, "none", 0.35)

p.origin_axes("x", "y")

# coordinate numbers, each placed on the side away from the arrow at that point
num_label(1, 0, "1", 4, 13, "start")
num_label(2, 0, "2", 4, 13, "start")
num_label(-1, 0, MINUS_S + "1", -4, -5, "end")
num_label(-2, 0, MINUS_S + "2", -4, 13, "end")
num_label(0, 1, "1", 6, 13, "start")
num_label(0, 2, "2", 6, -5, "start")
num_label(0, -1, MINUS_S + "1", -6, 13, "end")
num_label(0, -2, MINUS_S + "2", -6, 13, "end")

# level labels sitting on their circles
halo_text(p, 0.866, -0.5, ital("f") + " = 1", 0, 4, TEXT, 10.5, "middle", 0.75)
halo_text(p, 0.366, -1.366, ital("f") + " = 2", 0, 4, TEXT, 10.5, "middle", 0.75)
halo_text(p, 1.732, -1.0, ital("f") + " = 4", 0, 4, TEXT, 10.5, "middle", 0.75)

# the field V(a, b) = (-b, a) at the ten points of the example
PTS = [(1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (-1, 1), (-1, -1), (1, -1), (2, 0), (0, 2)]
for a, b in PTS:
    va, vb = -b, a
    tip = (a + SHRINK * va, b + SHRINK * vb)
    p.arrow((a, b), tip, THEORY, 1.9, head=7 if a * a + b * b < 1.5 else 8)

# gradient (2x, 2y) = (2, 2) at (1, 1), perpendicular to the level circle
P1 = (1.0, 1.0)
p.arrow(P1, (1 + SHRINK * 2, 1 + SHRINK * 2), PRACTICE, 2.2, head=8.5)

# right-angle mark between V(1, 1) and the gradient
s = 0.13
u = (-s / math.sqrt(2), s / math.sqrt(2))     # along V(1, 1)
w = (s / math.sqrt(2), s / math.sqrt(2))      # along the gradient
p.line([(P1[0] + u[0], P1[1] + u[1]), (P1[0] + u[0] + w[0], P1[1] + u[1] + w[1]),
        (P1[0] + w[0], P1[1] + w[1])], TEXT, 1.1, None, 0.8)

# points
for a, b in PTS:
    dot(p, (a, b), TEXT, 2.8)
dot(p, (0, 0), TEXT, 2.8)

# label at (1, 1): it straddles the y axis, so it gets an opaque background box (a glyph
# halo alone leaks the axis through "-" and "="); "V[f] = 0" lives in the formula line
# above the panel so that the top arc of the f = 2 circle stays visible
boxed_text(p, 0.5, 1.5, ital("V") + "(1, 1) = (" + MINUS_S + "1, 1)", 72, -6, -2, THEORY, 11, "end")
p.label(2, 2, "(2" + ital("x") + ", 2" + ital("y") + ") = (2, 2)", 0, -10, PRACTICE, 11, "middle")

# formula line above the panel (lifted a little so the y-axis arrowhead keeps clear of it)
p.text_px(p.x0 + p.w / 2, p.y0 - 14,
          ital("V") + " = " + MINUS_S + ital("y") + ital("U") + subs("1") + " + " + ital("x") + ital("U")
          + subs("2") + ",&#160;&#160;&#160;" + ital("f") + " = " + ital("x") + sups("2") + " + " + ital("y") + sups("2")
          + ",&#160;&#160;&#160;" + ital("V") + "[" + ital("f") + "] = 0",
          TEXT, 11.5, "middle")

OUT["yonlu-donen-alan-seviye"] = figure(
    400, 345, [p],
    "<em>f</em> = <em>x</em><sup>2</sup> + <em>y</em><sup>2</sup> fonksiyonunun <em>f</em> = 1, 2, 4 "
    "seviye çemberleri (gri) ve <em>V</em> = &#8722;<em>y</em><em>U</em><sub>1</sub> + "
    "<em>x</em><em>U</em><sub>2</sub> alanının on noktadaki okları (mavi); okunaklılık için her ok "
    "gerçek uzunluğunun yarısıyla çizilmiştir. Her ok bulunduğu seviye çemberine teğettir: çember "
    "boyunca ilerlerken <em>f</em> değişmez, bu yüzden <em>V</em>[<em>f</em>] = 0. (1, 1) noktasında "
    "(2<em>x</em>, 2<em>y</em>) = (2, 2) gradyanı (turuncu) çembere dik çıkar; <em>V</em>(1, 1) = "
    "(&#8722;1, 1) ise ona diktir, aradaki dik açı işareti bunu vurgular.",
    aria="Duzlemde f = x^2 + y^2 fonksiyonunun f = 1, 2, 4 seviye cemberleri ve V = -y U1 + x U2 "
         "alaninin on noktadaki oklari; her ok bulundugu cembere tegettir, V[f] = 0. (1, 1) "
         "noktasinda gradyan (2, 2) turuncu ve V(1, 1) = (-1, 1) mavi ok birbirine diktir.")

# ============================================================ yonlu-eyer-yonler
# -*- coding: utf-8 -*-
# yonlu-eyer-yonler: level curves of f = x^2 - y^2 (f = -3, 0, 3), the point
# p = (1, 1), the unit circle around p and the unit directions with the largest,
# smallest and zero directional derivative, plus the gradient (2, -2).

_XR, _YR = (-2.4, 3.9), (-2.15, 2.35)
_P = cplane(46, 22, 416, _XR, _YR)   # 416 px / 6.3 units: same scale as 442 / 6.7

_p = (1.0, 1.0)
_s = 1.0 / math.sqrt(2.0)          # 1/sqrt(2)
_u_zero = (1.0 + _s, 1.0 + _s)     # p + (1, 1)/sqrt2  -> derivative 0
_u_max = (1.0 + _s, 1.0 - _s)      # p + (1, -1)/sqrt2 -> derivative 2 sqrt2
_u_min = (1.0 - _s, 1.0 + _s)      # p + (-1, 1)/sqrt2 -> derivative -2 sqrt2
_grad = (3.0, -1.0)                # p + (2, -2)

_LEVEL_OP = 0.38                   # grey level curves: text colour, faded


def _mfmt(v):
    return fmt(v).replace("-", MINUS_S)


def _inside(pt):
    return _XR[0] <= pt[0] <= _XR[1] and _YR[0] <= pt[1] <= _YR[1]


def _clipped_line(pts, color=TEXT, width=1.4, opacity=_LEVEL_OP, dash=None):
    """Polyline restricted to the panel rectangle (runs outside are dropped)."""
    run = []
    for q in pts:
        if _inside(q):
            run.append(q)
        else:
            if len(run) > 1:
                _P.line(run, color, width, dash, opacity)
            run = []
    if len(run) > 1:
        _P.line(run, color, width, dash, opacity)


def _samples(f, t0, t1, n=240):
    return [f(t0 + (t1 - t0) * k / n) for k in range(n + 1)]


def _glabel(x, y, s, anchor="start", size=11.5):
    """Grey label for a level curve."""
    _P.add(f'<text x="{_P.X(x):.1f}" y="{_P.Y(y):.1f}" fill="{TEXT}" font-size="{size}" '
           f'text-anchor="{anchor}" opacity="0.66">{s}</text>')


def _haloed_head(p0, p1, color, head=8.0, halo=1.3):
    """Arrowhead at p1 with a thin page-coloured outline, so it stays visible on
    top of the wide translucent gradient arrow drawn beneath it."""
    x0, y0, x1, y1 = _P.X(p0[0]), _P.Y(p0[1]), _P.X(p1[0]), _P.Y(p1[1])
    dx, dy = x1 - x0, y1 - y0
    length = math.hypot(dx, dy)
    ux, uy = dx / length, dy / length
    px, py = -uy, ux
    hw = head * 0.42
    pts = (f"{x1:.1f},{y1:.1f} {x1-ux*head+px*hw:.1f},{y1-uy*head+py*hw:.1f} "
           f"{x1-ux*head-px*hw:.1f},{y1-uy*head-py*hw:.1f}")
    _P.add(f'<polygon points="{pts}" fill="{color}" stroke="{BG}" stroke-width="{halo}" '
           f'stroke-linejoin="round"/>')


def _nabla(px, py, color, size=8.0, width=1.15):
    """The nabla sign drawn as an inverted triangle (the text font lacks it)."""
    _P.add(f'<polygon points="{px:.1f},{py-size:.1f} {px+size:.1f},{py-size:.1f} '
           f'{px+size/2:.1f},{py:.1f}" fill="none" stroke="{color}" stroke-width="{width}" '
           f'stroke-linejoin="round"/>')


_fi = '<tspan font-style="italic">f</tspan>'

# --- level curves (grey) ---------------------------------------------------
# f = 3: x = +-sqrt(3 + y^2), parametrised by y
_clipped_line(_samples(lambda y: (math.sqrt(3.0 + y * y), y), _YR[0] - 0.1, _YR[1] + 0.1))
_clipped_line(_samples(lambda y: (-math.sqrt(3.0 + y * y), y), _YR[0] - 0.1, _YR[1] + 0.1))
# f = -3: y = +-sqrt(3 + x^2), parametrised by x
_clipped_line(_samples(lambda x: (x, math.sqrt(3.0 + x * x)), _XR[0] - 0.1, _XR[1] + 0.1))
_clipped_line(_samples(lambda x: (x, -math.sqrt(3.0 + x * x)), _XR[0] - 0.1, _XR[1] + 0.1))
# f = 0: the lines y = x and y = -x, sampled so the clipping keeps the part
# inside the panel (a two-point segment with both ends outside would vanish)
_clipped_line(_samples(lambda t: (t, t), -2.4, 2.4))
_clipped_line(_samples(lambda t: (t, -t), -2.4, 2.4))

# --- axes ------------------------------------------------------------------
_P.axes((-2, -1, 0, 1, 2, 3), (-2, -1, 0, 1, 2), "x", "y", xfmt=_mfmt, yfmt=_mfmt)

# --- unit circle around p ---------------------------------------------------
_P.circle(1.0, 1.0, 1.0, TEXT, 0.9, dash="3 3", opacity=0.55)

# --- gradient (thick, translucent, behind) and the unit directions ----------
_P.arrow(_p, _grad, PRACTICE, 3.8, head=12, opacity=0.5)
_P.arrow(_p, _u_max, PRACTICE, 2.2, head=8)
_haloed_head(_p, _u_max, PRACTICE, head=8)
_P.arrow(_p, _u_min, PRACTICE, 2.0, head=8, dash="5 3")
_P.arrow(_p, _u_zero, BASE, 2.2, head=8)
dot(_P, _p, TEXT, 3.6)

# --- labels ------------------------------------------------------------------
_glabel(2.95, 1.85, _fi + " = 3")
_glabel(-1.78, -0.95, _fi + " = 3")
_glabel(-0.9, 2.24, _fi + " = " + MINUS_S + "3")
_glabel(0.0, -2.03, _fi + " = " + MINUS_S + "3", "middle")
_glabel(-1.35, -1.72, _fi + " = 0")
_glabel(1.35, -1.78, _fi + " = 0", "end")

_P.label(1.0, 0.2, bold("p") + " = (1, 1)", 0, 0, TEXT, 11.5, "middle")
_P.label(1.45, 1.6, "türev 0", 0, 0, BASE, 12, "end")
_P.label(2.05, 0.3, "türev 2&#8730;2, en büyük", 0, 0, PRACTICE, 12)
_P.label(-0.2, 1.45, "türev " + MINUS_S + "2&#8730;2", 0, 0, PRACTICE, 12, "end")
_P.label(-0.2, 1.22, "en küçük", 0, 0, PRACTICE, 12, "end")
# gradient label: drawn nabla + "f(p) = (2, -2)"
_gx, _gy = _P.X(2.45), _P.Y(-1.42)
_nabla(_gx, _gy, PRACTICE)
_P.text_px(_gx + 11, _gy, _fi + "(" + bold("p") + ") = (2, " + MINUS_S + "2)", PRACTICE, 12)

OUT["yonlu-eyer-yonler"] = figure(
    520, 352, [_P],
    "<em>f</em> = <em>x</em><sup>2</sup> &#8722; <em>y</em><sup>2</sup> fonksiyonunun "
    "<em>f</em> = &#8722;3, 0, 3 seviye eğrileri ve <strong>p</strong> = (1, 1) noktası "
    "çevresindeki birim çember. Yönlü türev, gradyan &#8711;<em>f</em>(<strong>p</strong>) = (2, &#8722;2) "
    "yönündeki (1, &#8722;1)/&#8730;2 birim vektörü için en büyük değeri 2&#8730;2'yi, ters yön "
    "(&#8722;1, 1)/&#8730;2 için en küçük değeri &#8722;2&#8730;2'yi alır. <strong>p</strong>'den geçen "
    "<em>f</em> = 0 seviye eğrisine (<em>y</em> = <em>x</em> doğrusuna) teğet olan (1, 1)/&#8730;2 "
    "yönünde türev sıfırdır; gradyan bu seviye eğrisine diktir.",
    aria="f = x^2 - y^2 fonksiyonunun f = -3, 0, 3 seviye egrileri, p = (1, 1) noktasi ve cevresindeki "
         "birim cember; (1,-1)/sqrt2 yonunde turev 2 sqrt2 (en buyuk), (-1,1)/sqrt2 yonunde -2 sqrt2 "
         "(en kucuk), (1,1)/sqrt2 yonunde 0; gradyan (2,-2) oku",
)

# ============================================================ yonlu-gradyan-seviye
# -*- coding: utf-8 -*-
# yonlu-gradyan-seviye — level circles of f = x^2 + y^2 (f = 1, 5, 9), the point p = (1, 2)
# on the f = 5 circle, and the arrows v = (3, -1), u = (2, -1), n = (1, 2) at p together with
# the gradient (2, 4). n lies on top of the (wider, translucent) gradient arrow.

XR, YR = (-3.45, 5.3), (-3.6, 6.6)
p = cplane(30, 24, 340, XR, YR)


def ital(s):
    return '<tspan font-style="italic">' + s + '</tspan>'


# level circles x^2 + y^2 = 1, 5, 9
R5 = 5 ** 0.5
for r in (1.0, R5, 3.0):
    p.circle(0, 0, r, TEXT, 1.5, None, "none", 0.5)

p.origin_axes("x", "y")

P = (1.0, 2.0)
GRAD = (2.0, 4.0)
V, U, N = (3.0, -1.0), (2.0, -1.0), (1.0, 2.0)


def tip(w):
    return (P[0] + w[0], P[1] + w[1])


# gradient: wide, translucent, drawn first so n lands on top of it
p.add('<g opacity="0.32">')
p.arrow(P, tip(GRAD), PRACTICE, 9.0, head=16)
p.add('</g>')

p.arrow(P, tip(V), THEORY, 2.2, head=8)
p.arrow(P, tip(U), BASE, 2.2, head=8)
p.arrow(P, tip(N), PRACTICE, 2.2, head=8)
dot(p, P, TEXT, 3.6)

# labels of the level circles: just below the lowest point of each circle
for r, s in ((1.0, "1"), (R5, "5"), (3.0, "9")):
    p.label(0, -r, ital("f") + " = " + s, 6, 13, TEXT, 11)

# the point
p.label(1.5, 1.2, bold("p") + " = (1, 2)", 0, 0, TEXT, 11.5, "end")

# the arrows. The nabla glyph (U+2207) is missing from the font, so it is drawn as a small
# outlined inverted triangle in front of the gradient label (base at cap height, apex on
# the baseline).
p.line([(2.86, 5.12), (3.06, 5.12), (2.96, 4.90), (2.86, 5.12)], PRACTICE, 1.3)
p.label(2.5, 5.0, ital("f") + "(" + bold("p") + ") = (2, 4)", 25, 4, PRACTICE, 11.5)
p.label(1.5, 3.0, bold("n") + ", " + bold("n") + subs(bold("p")) + "[" + ital("f") + "] = 10",
        12, 4, PRACTICE, 11.5)
p.label(2.7, 1.85, bold("v") + ", " + bold("v") + subs(bold("p")) + "[" + ital("f") + "] = 2",
        0, 4, THEORY, 11.5)
p.label(3.22, 0.55, bold("u") + ", " + bold("u") + subs(bold("p")) + "[" + ital("f") + "] = 0",
        0, 4, BASE, 11.5)

OUT["yonlu-gradyan-seviye"] = figure(
    400, 445, [p],
    "<em>f</em> = <em>x</em><sup>2</sup> + <em>y</em><sup>2</sup> fonksiyonunun <em>f</em> = 1, 5, 9 "
    "seviye çemberleri ve <em>f</em> = 5 çemberi üzerindeki <strong>p</strong> = (1, 2) noktası. "
    "<strong>u</strong> = (2, &#8722;1) çembere teğettir ve <strong>u</strong><sub><strong>p</strong></sub>[<em>f</em>] = 0; "
    "<strong>n</strong> = (1, 2) gradyan (2, 4) ile aynı doğrultudadır, çembere diktir, <em>f</em>'nin "
    "en hızlı arttığı yönü gösterir ve türevi üçü arasında en büyük olan 10'dur. "
    "<strong>v</strong> = (3, &#8722;1) ikisinin arasında kalır: "
    "türevi 2, gradyanla iç çarpımıdır. Kalın yarı saydam ok gradyandır; "
    "<strong>n</strong> onun yarısı uzunluğunda olduğundan üstüne düşer.",
    aria="f = x^2 + y^2 fonksiyonunun f = 1, 5, 9 seviye cemberleri; f = 5 cemberi uzerindeki "
         "p = (1, 2) noktasindan cikan v = (3, -1), u = (2, -1), n = (1, 2) oklari ve kalin yari "
         "saydam gradyan oku (2, 4); u cembere teget (turev 0), n gradyanla ayni yonde (turev 10), "
         "v icin turev 2.")

# ============================================================ yonlu-her-noktada-sayi
# -*- coding: utf-8 -*-
# yonlu-her-noktada-sayi — W = xU1 + yU2 on eight points, with the value W[f] = 2(x^2 + y^2)
# written at the tip of every arrow; level circles of f = x^2 + y^2 in the background.
# Arrows are drawn at 0.7 of their true length (stated in the caption).

SHRINK = 0.7
XR, YR = (-2.35, 3.85), (-2.3, 3.95)
p = cplane(32, 34, 336, XR, YR)
PPU = 336 / (XR[1] - XR[0])          # pixels per data unit
u = 1.0 / PPU                        # one pixel in data units


def ital(s):
    return '<tspan font-style="italic">' + s + '</tspan>'


def colored(s, color):
    return '<tspan fill="' + color + '">' + s + '</tspan>'


def dim(s):
    return '<tspan fill-opacity="0.7">' + s + '</tspan>'


def mfmt(v):
    return fmt(v).replace("-", MINUS_S)


# --- background: level circles of f = x^2 + y^2 (f = 1, 2, 4) -----------------------
for r in (1.0, math.sqrt(2.0), 2.0):
    p.circle(0, 0, r, TEXT, 1.0, None, "none", 0.28)

# level labels sit on the circles in the empty lower-right quadrant; a page-coloured
# patch under each one cuts the circle so the text is not crossed by it
LEVELS = [(1.0, -50, "1"), (math.sqrt(2.0), -28, "2"), (2.0, -18, "4")]
for r, ang, val in LEVELS:
    a = math.radians(ang)
    cx, cy = r * math.cos(a), r * math.sin(a)
    rect(p, cx - 15 * u, cx + 15 * u, cy - 6.5 * u, cy + 6.5 * u, BG, 1.0)
    p.label(cx, cy, dim(ital("f") + " = " + val), 0, 3.5, TEXT, 10, "middle")

# --- axes -------------------------------------------------------------------------
p.origin_axes("x", "y", xticks=(-2, -1, 1, 2, 3), yticks=(-2, -1, 1, 2, 3), xfmt=mfmt, yfmt=mfmt)

# --- the field W(p) = p at the eight points of the example ---------------------------
PTS = [(1, 0), (0, 1), (1, 1), (2, 0), (-1, 1), (0, 0), (-1, -1), (0, 2)]
VALUES = {(1, 0): "2", (0, 1): "2", (1, 1): "4", (2, 0): "8",
          (-1, 1): "4", (0, 0): "0", (-1, -1): "4", (0, 2): "8"}


def tip(a, b):
    """End point of the shortened arrow W(a, b) = (a, b) drawn from (a, b)."""
    return (a + SHRINK * a, b + SHRINK * b)


for a, b in PTS:
    if (a, b) == (0, 0):
        continue
    p.arrow((a, b), tip(a, b), THEORY, 2.0, head=8)
for a, b in PTS:
    dot(p, (a, b), TEXT, 3.2)
dot(p, (0, 0), TEXT, 3.6)

# value labels W[f](p) at the tips: (dx, dy, anchor) chosen so nothing crosses the text
LAB = {
    (1, 0): (2, -9, "middle"),
    (0, 1): (9, 4, "start"),
    (1, 1): (9, -3, "start"),
    (2, 0): (6, -8, "start"),
    (-1, 1): (-9, -3, "end"),
    (0, 0): (-8, 14, "end"),
    (-1, -1): (-9, 9, "end"),
    (0, 2): (9, 4, "start"),
}
for (a, b), (dx, dy, anc) in LAB.items():
    x, y = (a, b) if (a, b) == (0, 0) else tip(a, b)
    p.label(x, y, VALUES[(a, b)], dx, dy, PRACTICE, 12.5, anc, True)

# --- the formulas above the panel ---------------------------------------------------
p.text_px(p.x0 + p.w / 2, p.y0 - 12,
          ital("W") + " = " + ital("x") + ital("U") + subs("1") + " + " + ital("y") + ital("U") + subs("2")
          + ",&#160;&#160;&#160;" + ital("f") + " = " + ital("x") + sups("2") + " + " + ital("y") + sups("2") + ",&#160;&#160;&#160;"
          + colored(ital("W") + "[" + ital("f") + "] = 2(" + ital("x") + sups("2") + " + " + ital("y") + sups("2") + ")",
                    PRACTICE),
          TEXT, 11.5, "middle")

OUT["yonlu-her-noktada-sayi"] = figure(
    400, 385, [p],
    "Düzlemde <em>W</em> = <em>x</em><em>U</em><sub>1</sub> + <em>y</em><em>U</em><sub>2</sub> alanının "
    "örnekteki sekiz noktadaki okları (mavi) ve her okun ucunda o noktadaki "
    "<em>W</em>[<em>f</em>] = 2(<em>x</em><sup>2</sup> + <em>y</em><sup>2</sup>) değeri (turuncu); "
    "gri çemberler <em>f</em> = <em>x</em><sup>2</sup> + <em>y</em><sup>2</sup> fonksiyonunun "
    "<em>f</em> = 1, 2, 4 seviye çemberleridir (yarıçapları 1, &#8730;2, 2). Okunaklılık için her ok "
    "gerçek uzunluğunun 0,7 katıyla çizilmiştir. Her ok kendi seviye çemberine dik ve dışarı doğrudur; "
    "başlangıç noktasından uzaklaştıkça ok uzar ve yanındaki sayı büyür, başlangıç noktasında ise "
    "<em>W</em>(<strong>0</strong>) sıfır vektörü olduğundan yalnızca nokta ve 0 değeri görünür. "
    "Böylece <em>W</em>[<em>f</em>], her noktaya bir sayı veren bir fonksiyondur.",
    aria="Duzlemde W = xU1 + yU2 alaninin sekiz noktadaki mavi oklari; her okun ucunda W[f] = 2(x^2 + y^2) "
         "degeri turuncu yazili: (1,0) ve (0,1)'de 2, (1,1), (-1,1), (-1,-1)'de 4, (2,0) ve (0,2)'de 8, "
         "baslangic noktasinda 0 ve ok yok. Arka planda f = 1, 2, 4 seviye cemberleri, gri.")

# ============================================================ yonlu-yuzey-kesit
# -*- coding: utf-8 -*-
# yonlu-yuzey-kesit: the graph z = x^2 + y^2 over -1..4 x -1..3, cut by the vertical plane that
# stands on the line p + t v (p = (1, 2), v = (3, -1)); the section curve
# t -> (1 + 3t, 2 - t, 5 + 2t + 10t^2) and its tangent at (1, 2, 5), whose slope in t is 2.
# The viewer stands at the low (-, -) corner so the bowl's high far wall does not hide the
# section. The z axis is compressed by KZ (ticks carry the true values) so that z up to 25 fits.

KZ = 0.2                      # drawn z = KZ * true z
ZTOP = 11.0                   # true height of the drawn piece of the vertical plane (curve tops at 9.8)
T0, T1 = -0.5, 0.6            # parameter range of the section curve


def S3(x, y, z):
    """Space point with the compressed z coordinate."""
    return (x, y, KZ * z)


def f(x, y):
    return x * x + y * y


def surf(u, v):
    return S3(u, v, f(u, v))


def floor_pt(t):
    return S3(1 + 3 * t, 2 - t, 0.0)


def sec(t):
    """Section curve, a hair above the surface so it is not swallowed by the faces."""
    return S3(1 + 3 * t, 2 - t, 5 + 2 * t + 10 * t * t + 0.03)


def top_pt(t):
    return S3(1 + 3 * t, 2 - t, ZTOP)


P = space_panel(20, 14, 360, (-2.7, 2.9), (-0.7, 4.3))
S = Space(P, Camera(azimuth=225, elevation=28, scale=0.62))

# --- floor: integer grid on the xy plane over the surface's domain ---------------------
for x in range(-1, 5):
    S.line([S3(x, -1, 0), S3(x, 3, 0)], TEXT, 0.7, None, 0.12)
for y in range(-1, 4):
    S.line([S3(-1, y, 0), S3(4, y, 0)], TEXT, 0.7, None, 0.12)

# the line p + t v in the xy plane: from the plane's left edge to a little past the tip of v
# (further left it would run into the tick label 3 of the y axis)
S.line([floor_pt(T0), floor_pt(1.2)], TEXT, 1.0, None, 0.7)

# --- the vertical plane over the line: lower part (below the section, under the surface) --
TS = [T0 + (T1 - T0) * k / 60 for k in range(61)]
lower = [floor_pt(t) for t in TS] + [sec(t) for t in reversed(TS)]
S.polygon(lower, TEXT, 0.07)

# --- the surface z = x^2 + y^2 -------------------------------------------------------------
S.surface(surf, (-1.0, 4.0), (-1.0, 3.0), nu=10, nv=8, fill=THEORY, stroke=THEORY,
          opacity=(0.05, 0.24))

# --- upper part of the vertical plane (inside the bowl, in front of the far wall) ---------
upper = [sec(t) for t in TS] + [top_pt(t) for t in reversed(TS)]
S.polygon(upper, TEXT, 0.07)
S.line([floor_pt(T0), top_pt(T0), top_pt(T1), floor_pt(T1)], TEXT, 0.8, "4 3", 0.4)

# --- axes and ticks (z ticks show the true heights) ---------------------------------------
S.axes(4.9, 3.7, 5.6, xmin=-1.3, ymin=-1.3, offsets=((9, 4), (-9, 4), (0, -6)))
S.ticks("x", (1, 2, 3, 4), offset=(2, 12))
S.ticks("y", (1, 2, 3), offset=(-11, 13))   # shifted left, away from the plane's dashed edge
# z ticks by hand: the labels go to the right of the axis, where the arrows leave room
for k in (1, 2, 3, 4, 5):
    S.line([(-0.04, 0, k), (0.04, 0, k)], TEXT, 1.0, None, 0.7)
    S.label((0, 0, k), str(int(round(k / KZ))), 7, 4, TEXT, 10, "start")

# --- coordinates of the marked point, the section curve and the two arrows ---------------
p0, p5, q0, q7 = S3(1, 2, 0), S3(1, 2, 5), S3(4, 1, 0), S3(4, 1, 7)
S.coordinate_box(p5, opacity=0.4)
S.curve(sec, T0, T1, THEORY, 2.6, 120)
S.arrow(p0, q0, PRACTICE, 2.2, head=9)          # v = (3, -1) in the xy plane
S.arrow(p5, q7, PRACTICE, 2.4, head=9)          # tangent to the section, direction (3, -1, 2)
S.point(p0, TEXT, 3.2)
S.point(p5, TEXT, 3.8)

# --- labels -------------------------------------------------------------------------------
S.label(p0, bold("p") + " = (1, 2)", -8, -5, TEXT, 11, "end", True)
S.label(q0, bold("v") + " = (3, " + MINUS_S + "1)", 6, -10, PRACTICE, 11.5, "start", True)
S.label(p5, "(1, 2, 5)", -8, -6, TEXT, 11, "end")
S.label(sec(T1), '<tspan font-style="italic">t</tspan>&#8217;ye göre eğim = 2',
        10, 2, PRACTICE, 11, "start")
S.label(sec(T0), "kesit eğrisi", -6, 4, THEORY, 11, "end")
S.label(S3(2.5, 3, f(2.5, 3)), "z = x" + sups("2") + " + y" + sups("2"), -8, 4, THEORY, 11.5, "end",
        False, True)
S.label(top_pt(0.1), "düşey düzlem", -6, -8, TEXT, 10.5, "end")

OUT["yonlu-yuzey-kesit"] = figure(
    400, 360, [P],
    "<em>z</em> = <em>x</em><sup>2</sup> + <em>y</em><sup>2</sup> yüzeyi, düzlemde "
    "<strong>p</strong> = (1, 2)&#8217;den geçen <strong>v</strong> = (3, &#8722;1) doğrultusundaki "
    "doğru ve bu doğru üzerinde yükselen düşey düzlem. Düzlem yüzeyi kesit eğrisi "
    "<em>t</em> &#8614; (1 + 3<em>t</em>, 2 &#8722; <em>t</em>, 5 + 2<em>t</em> + 10<em>t</em><sup>2</sup>) "
    "boyunca keser; (1, 2, 5) noktasındaki turuncu ok bu eğrinin teğetidir: yatay bileşeni "
    "<strong>v</strong>, düşey bileşeni 2&#8217;dir, yani <em>t</em> bir birim artarken teğet 2 birim "
    "yükselir ve <strong>v</strong><sub><strong>p</strong></sub>[<em>f</em>] = 2 olur. Eğim yatay "
    "uzaklığa göre değil <em>t</em>&#8217;ye göre ölçülür; <em>z</em> ekseni okunaklılık için "
    "1/5 ölçekte çizilmiştir.",
    aria="Surface z = x^2 + y^2 over -1..4 x -1..3, the line through p = (1, 2) in direction "
         "v = (3, -1), the vertical plane over it, the section curve on the surface and the tangent "
         "arrow at (1, 2, 5) in direction (3, -1, 2); the slope in t is 2")


# ---------------------------------------------------------------------------
for name, content in OUT.items():
    path = os.path.join(OUT_DIR, "diffgeo-%s.md" % name)
    io.open(path, "w", encoding="utf-8", newline="\n").write(content)
    print("yazildi:", path)
