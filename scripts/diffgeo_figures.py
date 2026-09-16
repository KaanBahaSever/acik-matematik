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

# ============================================================ cati-donme-alani
# -*- coding: utf-8 -*-
# cati-donme-alani: the rotation field V = -y U1 + x U2 seen from above on the circle r = 5, at the
# three points of the box's table: (3, 4), (-4, 3), (0, -5). At each point the cylindrical frame is
# drawn at TRUE length: E1 (orange) along the radius, E2 (green) tangent, and V (blue) lying on top
# of E2 but five times as long, which is the statement V = r E2 with r = 5.
# So the factor can be counted rather than believed, the blue shaft carries background-coloured cuts
# at t = 2, 3, 4; with the green arrowhead marking t = 1 the shaft reads as five equal units.
# The draft asks for a red E1; this palette has no red, so E1 takes PRACTICE (orange), the book's
# colour for arrows, while E2 keeps BASE (green) and V THEORY (blue) exactly as the draft asks.
# The y axis passes through (0, -5) and E1 there points straight down along it, so the E1 shafts are
# drawn over a background halo that lifts them off the axis line.
import math

XR, YR = (-9.2, 6.6), (-7.2, 8.3)
p = cplane(20, 30, 370, XR, YR)
PPU = 370.0 / (XR[1] - XR[0])          # pixels per data unit (equal on both axes)
R = 5.0
DBAR = "&#8214;"                        # double bar for the norm

A = dict(q=(3.0, 4.0), V=(-4.0, 3.0), E1=(0.6, 0.8), E2=(-0.8, 0.6))
B = dict(q=(-4.0, 3.0), V=(-3.0, -4.0), E1=(-0.8, 0.6), E2=(-0.6, -0.8))
C = dict(q=(0.0, -5.0), V=(5.0, 0.0), E1=(0.0, -1.0), E2=(1.0, 0.0))

# --- the numbers of the box, checked instead of trusted -----------------------------------------
for d in (A, B, C):
    x, y = d["q"]
    assert math.isclose(math.hypot(x, y), R)                       # the point sits on r = 5
    assert d["E1"] == (x / R, y / R)                               # E1 is radial and a unit vector
    assert d["E2"] == (-y / R, x / R)                              # E2 is tangent and a unit vector
    assert math.isclose(d["E1"][0] * d["E2"][0] + d["E1"][1] * d["E2"][1], 0.0, abs_tol=1e-12)
    assert d["V"] == (-y, x)                                       # V = -y U1 + x U2
    assert d["V"] == (R * d["E2"][0], R * d["E2"][1])              # V = r E2, the point of the box


def ital(s):
    return '<tspan font-style="italic">' + s + '</tspan>'


def col(s, c):
    return f'<tspan fill="{c}">{s}</tspan>'


IT_V = ital("V")
IT_E1 = ital("E") + subs("1")
IT_E2 = ital("E") + subs("2")


def tip(q, v, t=1.0):
    return (q[0] + t * v[0], q[1] + t * v[1])


def px_dir(v):
    """Unit pixel direction of the data vector v (the panel's y axis points up)."""
    dx, dy = v[0] * PPU, -v[1] * PPU
    n = math.hypot(dx, dy) or 1.0
    return dx / n, dy / n


def unit_marks(d, ts=(2.0, 3.0, 4.0)):
    """Ruler marks along the V shaft at whole multiples of E2: a hairline notch in the shaft and a
    short grey tick beside it, on the E1 side. A wider notch would turn V into a dashed arrow, and
    a dashed arrow means 'auxiliary line' everywhere else in this book. The mark at t = 1 is the
    green arrowhead itself; a grey tick there would sit on the dashed radius and read as part of
    it."""
    q, u, s = d["q"], d["E2"], d["E1"]
    ux, uy = px_dir(u)
    nx, ny = -uy, ux
    sx, sy = px_dir(s)
    for t in ts:
        cx, cy = p.X(q[0] + u[0] * t), p.Y(q[1] + u[1] * t)
        if t > 1.0:                      # at t = 1 the green arrowhead is the mark
            p.add(f'<line x1="{cx - nx * 3.4:.1f}" y1="{cy - ny * 3.4:.1f}" '
                  f'x2="{cx + nx * 3.4:.1f}" y2="{cy + ny * 3.4:.1f}" stroke="{BG}" '
                  f'stroke-width="1.4" stroke-linecap="butt"/>')
        p.add(f'<line x1="{cx + sx * 3.4:.1f}" y1="{cy + sy * 3.4:.1f}" '
              f'x2="{cx + sx * 8.6:.1f}" y2="{cy + sy * 8.6:.1f}" stroke="{TEXT}" '
              f'stroke-width="1.1" opacity="0.5" stroke-linecap="butt"/>')


def haloed_arrow(q, v, color, width=2.4, head=7.0, halo=4.6):
    """Arrow drawn over a background halo, so the axis line beneath it does not show through."""
    x0, y0, x1, y1 = p.X(q[0]), p.Y(q[1]), p.X(q[0] + v[0]), p.Y(q[1] + v[1])
    p.add(f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" stroke="{BG}" '
          f'stroke-width="{halo:.1f}" stroke-linecap="round"/>')
    p.arrow(q, (q[0] + v[0], q[1] + v[1]), color, width, head)


def tick(x, y, horizontal=True, s=3.5):
    if horizontal:
        p.add(f'<line x1="{p.X(x):.1f}" y1="{p.Y(y) - s:.1f}" x2="{p.X(x):.1f}" '
              f'y2="{p.Y(y) + s:.1f}" stroke="{TEXT}" stroke-width="1" opacity="0.65"/>')
    else:
        p.add(f'<line x1="{p.X(x) - s:.1f}" y1="{p.Y(y):.1f}" x2="{p.X(x) + s:.1f}" '
              f'y2="{p.Y(y):.1f}" stroke="{TEXT}" stroke-width="1" opacity="0.65"/>')


# --- 1. the circle r = 5, the radii that carry E1, the axes --------------------------------------
p.circle(0, 0, R, TEXT, 1.2, None, "none", 0.45)
guide(p, [(0.0, 0.0), A["q"]], TEXT, 0.34)
guide(p, [(0.0, 0.0), B["q"]], TEXT, 0.34)     # the radius to (0, -5) is the y axis itself
p.origin_axes("x", "y")
tick(5, 0); tick(-5, 0); tick(0, 5, False)

# --- 2. V (blue, true length 5), its unit cuts, E2 (green) on its first unit, E1 (orange) --------
for d in (A, B, C):
    p.arrow(d["q"], tip(d["q"], d["V"]), THEORY, 2.6, head=10)
for d in (A, B, C):
    unit_marks(d)
for d in (A, B, C):
    haloed_arrow(d["q"], d["E2"], BASE, 2.6, 8.0, 5.0)   # the halo sets E2 off from the blue shaft
for d in (A, B, C):
    haloed_arrow(d["q"], d["E1"], PRACTICE, 2.4, 7.0)
for d in (A, B, C):
    dot(p, d["q"], TEXT, 3.4)
dot(p, (0.0, 0.0), TEXT, 2.4)

# --- 3. labels -----------------------------------------------------------------------------------
# tick numbers, kept off the circle they sit on
p.label(5, 0, "5", 5, 15, TEXT, 10.5, "start")
p.label(-5, 0, MINUS_S + "5", -5, 15, TEXT, 10.5, "end")
p.label(0, 5, "5", -7, -5, TEXT, 10.5, "end")
p.label(1.5, 2.0, ital("r") + " = 5", 11, 8, TEXT, 11, "start")

# (3, 4): coordinates to the right, E1 past its tip, E2 under the green head,
# the two-line block above-left of the blue tip
p.label(*A["q"], "(3, 4)", 13, 4, TEXT, 11, "start")
p.label(*tip(A["q"], A["E1"]), IT_E1, 5, -5, PRACTICE, 11.5, "start")
p.label(*tip(A["q"], A["E2"], 0.5), IT_E2, -8, 11, BASE, 11.5, "end")
p.label(*tip(A["q"], A["V"]), IT_V + " = (" + MINUS_S + "4, 3)", -10, -10, THEORY, 11.5, "end")
p.label(*tip(A["q"], A["V"]), IT_E2 + " = (" + MINUS_S + "4/5, 3/5)", -10, 7, BASE, 11.5, "end")

# (-4, 3)
p.label(*B["q"], "(" + MINUS_S + "4, 3)", 11, -6, TEXT, 11, "start")
p.label(*tip(B["q"], B["E1"]), IT_E1, -6, -5, PRACTICE, 11.5, "end")
p.label(*tip(B["q"], B["E2"], 0.8), IT_E2, 9, 10, BASE, 11.5, "start")
p.label(*tip(B["q"], B["V"]), IT_V + " = (" + MINUS_S + "3, " + MINUS_S + "4)", 0, 16,
        THEORY, 11.5, "middle")
p.label(*tip(B["q"], B["V"]), IT_E2 + " = (" + MINUS_S + "3/5, " + MINUS_S + "4/5)", 0, 32,
        BASE, 11.5, "middle")

# (0, -5): everything goes below the horizontal arrow, where the page is empty
p.label(*C["q"], "(0, " + MINUS_S + "5)", -9, 15, TEXT, 11, "end")
p.label(*tip(C["q"], C["E1"]), IT_E1, 7, 0, PRACTICE, 11.5, "start")
p.label(*tip(C["q"], C["E2"], 0.5), IT_E2, 0, -9, BASE, 11.5, "middle")
p.label(*tip(C["q"], C["V"]), IT_V + " = (5, 0)", 26, 20, THEORY, 11.5, "end")
p.label(*tip(C["q"], C["V"]), IT_E2 + " = (1, 0)", 26, 36, BASE, 11.5, "end")

# the two statements of the box, in the corners the drawing leaves empty
p.label(1.35, 7.55,
        col(IT_V, THEORY) + " = " + MINUS_S + ital("y") + " " + ital("U") + subs("1") + " + "
        + ital("x") + " " + ital("U") + subs("2"), 0, 0, TEXT, 12, "start")
p.label(1.35, 6.85,
        col(IT_V, THEORY) + " = " + ital("r") + " " + col(IT_E2, BASE), 0, 0, TEXT, 12, "start")
p.label(-9.0, -4.6, DBAR + IT_V + DBAR + " = " + ital("r") + " = 5", 0, 0, TEXT, 11.5, "start")

OUT["cati-donme-alani"] = figure(
    400, 400, [p],
    "<em>z</em> = 0 düzlemine, yani <em>xy</em> düzlemine üstten bakıyoruz: <em>r</em> = 5 çemberi "
    "üzerindeki üç noktada <em>V</em> = &#8722;<em>y</em> <em>U</em><sub>1</sub> + <em>x</em> "
    "<em>U</em><sub>2</sub> dönme alanının oku (mavi) ile silindirik çatının birim vektörleri "
    "<em>E</em><sub>1</sub> (turuncu, yarıçap yönünde) ve <em>E</em><sub>2</sub> (yeşil, çembere "
    "teğet) gerçek uzunluklarıyla çizilmiştir. Mavi ok her noktada yeşil okla aynı doğrultudadır "
    "ve tam beş katı uzundur; yanındaki gri çentikler, yeşil okun ucuyla birlikte, onu beş eşit "
    "birime böler. Görülen şey <em>V</em> = <em>r</em> <em>E</em><sub>2</sub> eşitliğidir: alanın "
    "<em>E</em><sub>1</sub> yönünde hiç bileşeni yoktur ve boyu yalnızca <em>z</em> eksenine "
    "uzaklığa, yani <em>r</em> = 5&#8217;e eşittir.",
    aria="xy duzlemine ustten gorunus: r = 5 cemberi ve uzerindeki (3, 4), (-4, 3), (0, -5) "
         "noktalari. Her noktada turuncu birim E1 oku yaricap boyunca disa, yesil birim E2 oku "
         "cembere teget, mavi V oku ise E2 ile ayni yonde ama tam bes kat uzundur; V sirasiyla "
         "(-4, 3), (-3, -4) ve (5, 0), E2 ise (-4/5, 3/5), (-3/5, -4/5) ve (1, 0) vektorleridir. "
         "Mavi ok, yanindaki gri centiklerle bes esit birime bolunmustur: V = r E2 ve r = 5.")

# ============================================================ cati-gram-schmidt
# -*- coding: utf-8 -*-
# cati-gram-schmidt: the worked case of the exercise, drawn at p = origin. V = 2U1 + 2U2 + U3 and
# W = U1 (grey) are the data; E1 = V/||V|| (orange, unit), the projection (W . E1)E1 = (4/9, 4/9,
# 2/9) sits on the E1 shaft as a faint dashed sleeve, the rest W~ = (5/9, -4/9, -2/9) is drawn as
# the dashed green arrow from the foot of the perpendicular to the tip of W — the same vector as
# E2 up to length, so the green unit arrow E2 at p is visibly parallel to it. E3 = E1 x E2 (blue).
# The draft asks for a red E1; this palette has no red, so the frame keeps the book's colours
# (cati-kuresel-cati, cati-donme-alani): E1 -> PRACTICE, E2 -> BASE, E3 -> THEORY, and W~, being
# E2 before normalisation, takes E2's green instead of the draft's orange, which E1 already holds.
# Camera: E1 = (2, 2, 1)/3 points almost exactly along the API's default view direction (dot 0.985),
# so V would be seen end on. A scan over azimuth and elevation, maximising the smallest page angle
# between E1, W, E2, E3 while keeping the three unit arrows near the same apparent length, picked
# azimuth 196, elevation 30: there the frame opens into a 120-degree fan (E1 up-left, E2 right,
# E3 down-left), the three unit arrows project to 0.84, 0.78, 0.83 of their true length, and no two
# bold arrows come closer than 58 degrees on the page. The viewer therefore sits over the (-x, -y)
# quadrant: x runs up-right, y to the left, z up, all three axes labelled.
import math

AZ, EL = 196.0, 30.0
AXX, AXY, AXZ, AXZ0 = 1.95, 1.2, 1.3, -0.95

O = (0.0, 0.0, 0.0)
V = (2.0, 2.0, 1.0)                 # vector part of V = 2U1 + 2U2 + U3
Wv = (1.0, 0.0, 0.0)                # vector part of W = U1
E1 = vscale(1.0 / vnorm(V), V)      # (2, 2, 1)/3
c1 = vdot(Wv, E1)                   # W . E1 = 2/3
PRJ = vscale(c1, E1)                # (4/9, 4/9, 2/9)
WT = vsub(Wv, PRJ)                  # (5/9, -4/9, -2/9)
nWT = vnorm(WT)                     # sqrt(5)/3
E2 = vscale(1.0 / nWT, WT)          # (5, -4, -2)/(3 sqrt 5)
E3 = vcross(E1, E2)                 # (0, 1, -2)/sqrt 5

# --- the numbers of the box, checked instead of trusted ------------------------------------------
TOL = 1e-12
assert math.isclose(vnorm(V), 3.0, abs_tol=TOL)
assert all(math.isclose(a, b, abs_tol=TOL) for a, b in zip(E1, (2 / 3, 2 / 3, 1 / 3)))
assert math.isclose(c1, 2 / 3, abs_tol=TOL)
assert all(math.isclose(a, b, abs_tol=TOL) for a, b in zip(PRJ, (4 / 9, 4 / 9, 2 / 9)))
assert all(math.isclose(a, b, abs_tol=TOL) for a, b in zip(WT, (5 / 9, -4 / 9, -2 / 9)))
assert math.isclose(nWT, math.sqrt(5) / 3, abs_tol=TOL)
assert all(math.isclose(a, b, abs_tol=TOL)
           for a, b in zip(E2, vscale(1 / (3 * math.sqrt(5)), (5.0, -4.0, -2.0))))
assert all(math.isclose(a, b, abs_tol=TOL)
           for a, b in zip(E3, vscale(1 / math.sqrt(5), (0.0, 1.0, -2.0))))
assert all(math.isclose(a, b, abs_tol=TOL)             # E3 from the cross product of the box
           for a, b in zip(vcross(V, (5.0, -4.0, -2.0)), (0.0, 9.0, -18.0)))
for a, b in ((E1, E2), (E1, E3), (E2, E3)):
    assert math.isclose(vdot(a, b), 0.0, abs_tol=1e-12)
for e in (E1, E2, E3):
    assert math.isclose(vnorm(e), 1.0, abs_tol=1e-12)
assert math.isclose(vdot(WT, E1), 0.0, abs_tol=1e-12)  # the right angle drawn at the foot

P = space_panel(16, 14, 400, (-2.42, 1.95), (-1.52, 2.45))
S = Space(P, Camera(azimuth=AZ, elevation=EL, scale=1.0))
PPU = P.w / (P.xmax - P.xmin)       # pixels per page unit (equal on both axes)

SQ, DBAR = "&#8730;", "&#8214;"     # square root, double bar for the norm


def ital(s):
    return f'<tspan font-style="italic">{s}</tspan>'


def EN(k):
    return ital("E") + subs(str(k))


IT_V, IT_W = ital("V"), ital("W")


def wtilde(size=12.0):
    """Italic W with a tilde over it. The combining accent U+0303 is not in the book's font — it
    comes out as a dotted circle next to the letter — so the tilde is set as a raised tspan pulled
    back over the W, and the advance it eats is handed back to whatever follows."""
    ts = 0.92 * size
    wW, wT = 0.76 * size, 0.50 * ts          # advances of the italic W and of the tilde
    dx = -(wW + wT) / 2 + 0.09 * size        # the last term centres the ink, measured in the PNG
    return (ital("W")
            + f'<tspan dx="{dx:.2f}" dy="{-0.50 * size:.2f}" font-size="{ts:.1f}">~</tspan>'
            + f'<tspan dx="{-wT - dx:.2f}" dy="{0.50 * size:.2f}">&#8203;</tspan>')


def halo(px_, py_, s, color=TEXT, size=11.5, anchor="start"):
    """Text at a pixel position with a page-coloured halo, so faint lines break under it."""
    P.add(f'<text x="{px_:.1f}" y="{py_:.1f}" fill="{color}" font-size="{size}" '
          f'text-anchor="{anchor}" stroke="{BG}" stroke-width="3.4" stroke-linejoin="round" '
          f'paint-order="stroke">{s}</text>')


def at(X, Y, s, color=TEXT, size=11.5, anchor="start"):
    """Halo text at a page (panel data) position."""
    halo(P.X(X), P.Y(Y), s, color, size, anchor)


def tag(Q, s, dx=0, dy=0, color=TEXT, size=11.5, anchor="start"):
    """Halo text hung on a space point."""
    X, Y = S.pt(Q)
    halo(P.X(X) + dx, P.Y(Y) + dy, s, color, size, anchor)


def px_dir(Q):
    """Unit page direction (in pixels, y down) of the space vector Q."""
    X, Y = S.pt(Q)
    dx, dy = X * PPU, -Y * PPU
    n = math.hypot(dx, dy) or 1.0
    return dx / n, dy / n


def cut(t, half=4.6, width=3.0):
    """Background-coloured cut across the V shaft at t units along E1: the unit marks of ||V|| = 3."""
    X, Y = S.pt(vscale(t, E1))
    ux, uy = px_dir(E1)
    x, y = P.X(X), P.Y(Y)
    P.add(f'<line x1="{x + uy * half:.1f}" y1="{y - ux * half:.1f}" '
          f'x2="{x - uy * half:.1f}" y2="{y + ux * half:.1f}" stroke="{BG}" '
          f'stroke-width="{width}" stroke-linecap="butt"/>')


def right_angle(Q, a, b, s=0.18, color=TEXT, width=1.2):
    """Right-angle mark at Q, a true square in the plane of a and b; drawn over a background
    halo so the faint axis that runs through the E1-E3 wedge breaks behind it."""
    pts = [vadd(Q, vscale(s, vunit(a))),
           vadd(Q, vadd(vscale(s, vunit(a)), vscale(s, vunit(b)))),
           vadd(Q, vscale(s, vunit(b)))]
    S.line(pts, BG, width + 2.6)
    S.line(pts, color, width, None, 0.95)


# ---------------------------------------------------------------- 1. axes
S.axes(AXX, AXY, AXZ, zmin=AXZ0, offsets=((11, -4), (-12, -1), (0, -10)))
S.ticks("y", (1,), offset=(1, 14))
S.ticks("z", (1,), offset=(-9, 4))

# ---------------------------------------------------------------- 2. the data: V and W
S.arrow(O, V, TEXT, 2.3, head=10, opacity=0.72)
cut(2.0)                                       # E1's head marks 1, this cut 2, the tip 3
S.arrow(O, Wv, TEXT, 2.6, head=9.0, opacity=0.72)

# ---------------------------------------------------------------- 3. the projection and W~
S.line([O, PRJ], PRACTICE, 7.0, "5 5", 0.50)   # (W . E1)E1 as a sleeve along the E1 shaft
S.arrow(PRJ, Wv, BASE, 1.9, 8.0, "5 4", 0.95)  # W~ = W - (W . E1)E1, carried to the foot
right_angle(PRJ, vscale(-1.0, E1), E2, 0.15, TEXT)

# ---------------------------------------------------------------- 4. the frame
right_angle(O, E1, E3, 0.18, PRACTICE)
right_angle(O, E2, E3, 0.18, BASE)
S.arrow(O, E1, PRACTICE, 2.6, head=9)
S.arrow(O, E2, BASE, 2.6, head=9)
S.arrow(O, E3, THEORY, 2.6, head=9)

S.point(O, TEXT, 3.6)
S.point(V, TEXT, 3.0)
S.point(Wv, TEXT, 3.0)
S.point(PRJ, PRACTICE, 3.2)

# ---------------------------------------------------------------- 5. labels
tag(O, bold("p"), 19, 20, TEXT, 12)
tag(V, IT_V + " = (2, 2, 1)", 14, -6, TEXT, 12)
tag(vscale(2.4, E1), DBAR + IT_V + DBAR + " = 3", 12, 4, TEXT, 11.5)
tag(E1, EN(1) + " = (2, 2, 1)/3", -12, -5, PRACTICE, 12, "end")
tag(PRJ, "(" + IT_W + " " + CDOT + " " + EN(1) + ")" + EN(1) + " = (4/9, 4/9, 2/9)",
    -13, 11, PRACTICE, 11.5, "end")

at(0.50, 0.62, IT_W + " = (1, 0, 0)", TEXT, 12)
at(0.50, 0.36, wtilde(12) + " = (5/9, " + MINUS_S + "4/9, " + MINUS_S + "2/9)", BASE, 12)
at(0.50, 0.16, DBAR + wtilde(11.5) + DBAR + " = " + SQ + "5/3", BASE, 11.5)
at(0.45, -0.30, EN(2) + " = (5, " + MINUS_S + "4, " + MINUS_S + "2)/(3" + SQ + "5)", BASE, 12)

tag(E3, EN(3) + " = " + EN(1) + " " + TIMES_S + " " + EN(2) + " = (0, 1, " + MINUS_S + "2)/"
    + SQ + "5", -8, 15, THEORY, 12, "end")

at(0.05, -1.10, EN(1) + " " + CDOT + " " + EN(2) + " = " + EN(1) + " " + CDOT + " " + EN(3)
   + " = " + EN(2) + " " + CDOT + " " + EN(3) + " = 0", TEXT, 11, "middle")
at(0.05, -1.33, DBAR + EN(1) + DBAR + " = " + DBAR + EN(2) + DBAR + " = " + DBAR + EN(3) + DBAR
   + " = 1", TEXT, 11, "middle")

OUT["cati-gram-schmidt"] = figure(
    432, 424, [P],
    "Uygulama noktası <strong>p</strong> orijinde alınmıştır; gri oklar orada verilen "
    "<em>V</em> = 2<em>U</em><sub>1</sub> + 2<em>U</em><sub>2</sub> + <em>U</em><sub>3</sub> ile "
    "<em>W</em> = <em>U</em><sub>1</sub> alanlarının vektör kısımlarıdır. Birinci adım "
    "<em>E</em><sub>1</sub> = <em>V</em>/&#8214;<em>V</em>&#8214; (turuncu): aynı doğrultuda, "
    "&#8214;<em>V</em>&#8214; = 3 olduğu için üçte bir uzunlukta; turuncu ok ucu ile gri okun "
    "üzerindeki çentik, <em>V</em>&#8217;yi üç eşit birime böler. İkinci adımda "
    "<em>W</em>&#8217;den <em>E</em><sub>1</sub> yönündeki bileşen (<em>W</em> &#183; "
    "<em>E</em><sub>1</sub>)<em>E</em><sub>1</sub> = (4/9, 4/9, 2/9) &#8212; turuncu okun "
    "üzerindeki soluk şerit &#8212; çıkarılır; dik ayaktan <em>W</em>&#8217;nin ucuna giden "
    "kesikli yeşil ok geriye kalan (5/9, &#8722;4/9, &#8722;2/9) vektörüdür ve dik açı işaretinin "
    "söylediği gibi <em>E</em><sub>1</sub>&#8217;e diktir; birim uzunluğa getirilince "
    "<em>p</em>&#8217;deki yeşil ok <em>E</em><sub>2</sub> olur. Üçüncü adım "
    "<em>E</em><sub>3</sub> = <em>E</em><sub>1</sub> &#215; <em>E</em><sub>2</sub> (mavi), öteki "
    "iki dik açı işaretinin gösterdiği gibi hem <em>E</em><sub>1</sub>&#8217;e hem "
    "<em>E</em><sub>2</sub>&#8217;ye diktir; üç ok birlikte, altı koşulu da sağlayan bir çatıdır.",
    aria="p noktasinda gri oklar V = (2, 2, 1) ve W = (1, 0, 0); turuncu birim ok E1 = (2, 2, 1)/3 "
         "V ile ayni dogrultudadir ve V nin ucte biri kadardir; W nin E1 uzerine izdusumu "
         "(4/9, 4/9, 2/9) turuncu okun ilk parcasi olarak soluk kesikli bir seritle gosterilir; "
         "dik ayaktan W nin "
         "ucuna giden kesikli yesil ok W tilde = (5/9, -4/9, -2/9) olup E1 e diktir; ona paralel "
         "yesil birim ok E2 = (5, -4, -2) bolu 3 karekok 5; mavi birim ok E3 = (0, 1, -2) bolu "
         "karekok 5 hem E1 e hem E2 ye diktir; uc dik aci isareti dikligi gosterir",
)

# ============================================================ cati-kuresel-cati
# -*- coding: utf-8 -*-
# cati-kuresel-cati: the spherical frame field F1, F2, F3 at p = (3, 0, 4) and q = (0, 4, 3),
# both on the sphere of radius rho = 5. Colours follow teget-dogal-cati: F1 -> PRACTICE,
# F2 -> BASE, F3 -> THEORY, so the same field keeps the same colour at both points.
# The sphere itself is drawn in TEXT (like the cylinder of egri-helis-hiz-vektorleri) to leave
# the three accent colours free for the frame.
# Camera: the awkward pair is F1(q) = (0, 4/5, 3/5) and F2(q) = (-1, 0, 0) — at the API's default
# view they project onto almost the same page direction (2 degrees apart). A scan over azimuth and
# elevation maximising the smallest tip-to-other-arrow distance picked azimuth 57, elevation 19:
# there the six arrows stay at least 0.25 units (about 12 px) clear of each other, and the floor
# is still open enough for the vartheta = pi/2 arc.
import math

AZ, EL = 57.0, 19.0
RHO = 5.0
AXX, AXY, AXZ = 5.8, 6.0, 5.6

p = (3.0, 0.0, 4.0)
q = (0.0, 4.0, 3.0)
FP = ((0.6, 0.0, 0.8), (0.0, 1.0, 0.0), (-0.8, 0.0, 0.6))      # F1, F2, F3 at p
FQ = ((0.0, 0.8, 0.6), (-1.0, 0.0, 0.0), (0.0, -0.6, 0.8))     # F1, F2, F3 at q
COL = (PRACTICE, BASE, THEORY)
PHI_P = math.atan2(4.0, 3.0)        # cos = 3/5, sin = 4/5
PHI_Q = math.atan2(3.0, 4.0)        # cos = 4/5, sin = 3/5

RHO_S, PHI_S, TH_S = "&#961;", "&#966;", "&#977;"

P = space_panel(22, 20, 446, (-5.55, 4.05), (-2.15, 6.0))
S = Space(P, Camera(azimuth=AZ, elevation=EL, scale=1.0))


def ital(s):
    return f'<tspan font-style="italic">{s}</tspan>'


def FN(k):
    """Name of the k-th frame field, italic F with a subscript."""
    return ital("F") + subs(str(k))


def halo_px(px, py, s, color=TEXT, size=11.5, anchor="start"):
    """Text at a pixel position with a page-coloured halo, so the wire frame breaks under it."""
    P.add(f'<text x="{px:.1f}" y="{py:.1f}" fill="{color}" font-size="{size}" '
          f'text-anchor="{anchor}" stroke="{BG}" stroke-width="3.2" stroke-linejoin="round" '
          f'paint-order="stroke">{s}</text>')


def tag(Q, s, dx=0, dy=0, color=TEXT, size=11.5, anchor="start"):
    """Halo text hung on a space point."""
    X, Y = S.pt(Q)
    halo_px(P.X(X) + dx, P.Y(Y) + dy, s, color, size, anchor)


def sph(th, ph, r=RHO):
    return (r * math.cos(ph) * math.cos(th), r * math.cos(ph) * math.sin(th), r * math.sin(ph))


def block(x, y, rows, dy=0.35, size=10.5):
    """A small stack of coloured lines placed at panel coordinates (x, y)."""
    for k, (s, c) in enumerate(rows):
        halo_px(P.X(x), P.Y(y - k * dy), s, c, size, "start")


def sweep(f, t0, t1, head=6.0, width=1.05, opacity=0.8, n=64):
    """Angle arc with an arrowhead at its end, a shade lighter than the frame arrows."""
    pts = [f(t0 + (t1 - t0) * k / n) for k in range(n + 1)]
    S.line(pts[:-2], TEXT, width, None, opacity)
    S.arrow(pts[-3], pts[-1], TEXT, width, head, None, opacity)


# ---------------------------------------------------------------- 1. floor and the sphere octant
# the grid stops at 4: the corner (5, 5, 0) projects below everything else and would leave a
# band of empty page under the figure
S.floor_grid((0, 4), (0, 4), n=4, opacity=0.09)
S.surface(sph, (0.0, math.pi / 2), (0.0, math.pi / 2), nu=12, nv=9, fill=TEXT, stroke=TEXT,
          opacity=(0.03, 0.10), stroke_width=0.55, stroke_opacity=0.22)

# the two coordinate curves through p: the meridian vartheta = 0 and the parallel through p,
# lifted a hair off the sphere so they read above the wire frame
S.curve(lambda t: sph(0.0, t, RHO + 0.03), 0.0, math.pi / 2, TEXT, 1.2, 96, None, 0.5)
S.curve(lambda t: sph(t, PHI_P, RHO + 0.03), 0.0, math.pi / 2, TEXT, 1.2, 96, None, 0.5)

# ---------------------------------------------------------------- 2. axes
S.axes(AXX, AXY, AXZ, offsets=((-6, 14), (11, 5), (-11, -4)))
S.ticks("x", (3, 5), length=0.16)
S.ticks("y", (4, 5), length=0.16)
S.ticks("z", (5,), length=0.16, offset=(-10, -6))

# ---------------------------------------------------------------- 3. radii, drops, angle arcs
for X in (p, q):
    S.guide([(0.0, 0.0, 0.0), X], TEXT, 0.55, 1.1)
    S.drop(X)

R_TH, R_PP, R_PQ = 2.35, 1.55, 1.45
sweep(lambda t: (R_TH * math.cos(t), R_TH * math.sin(t), 0.0),
      0.0, math.pi / 2, 6.5)                                               # vartheta, in the floor
sweep(lambda t: (R_PP * math.cos(t), 0.0, R_PP * math.sin(t)), 0.0, PHI_P)  # phi at p, in y = 0
sweep(lambda t: (0.0, R_PQ * math.cos(t), R_PQ * math.sin(t)), 0.0, PHI_Q)  # phi at q, in x = 0

# ---------------------------------------------------------------- 4. the two frames
for X, F in ((p, FP), (q, FQ)):
    for v, c in zip(F, COL):
        S.arrow(X, vadd(X, v), c, 2.4, head=7.5)
S.point(p, TEXT, 3.6)
S.point(q, TEXT, 3.6)

# ---------------------------------------------------------------- 5. labels
tag(p, bold("p"), -10, 6, TEXT, 12, "end")
tag(q, bold("q"), 10, 9, TEXT, 12, "start")

tag(vadd(p, FP[0]), FN(1), -5, -5, PRACTICE, 11.5, "end")
tag(vadd(p, FP[1]), FN(2), 6, 12, BASE, 11.5, "start")
tag(vadd(p, FP[2]), FN(3), 0, -9, THEORY, 11.5, "middle")
tag(vadd(q, FQ[0]), FN(1), 0, -9, PRACTICE, 11.5, "middle")
tag(vadd(q, FQ[1]), FN(2), 7, 4, BASE, 11.5, "start")
tag(vadd(q, FQ[2]), FN(3), -5, 11, THEORY, 11.5, "end")   # below the tip: the parallel through p


# rho on each dashed radius, the two phi arcs, vartheta in the floor and on the meridian
halo_px(P.X(-1.42), P.Y(1.50), ital(RHO_S) + " = 5", TEXT, 11.5, "end")
halo_px(P.X(1.22), P.Y(0.72), ital(RHO_S) + " = 5", TEXT, 11.5, "start")
tag(sph(0.0, PHI_P / 2, 1.05), ital(PHI_S), 0, 4, TEXT, 12, "middle")
tag(sph(math.pi / 2, PHI_Q / 2, 1.15), ital(PHI_S), 0, 4, TEXT, 12, "middle")
halo_px(P.X(-0.49), P.Y(-1.02), ital(TH_S) + " = " + PI_S + "/2", TEXT, 11.5, "middle")
tag(sph(0.0, math.radians(25.0)), ital(TH_S) + " = 0", -5, 4, TEXT, 11.5, "end")

# the numbers, next to their point
block(-5.30, 3.05, [(bold("p") + " = (3, 0, 4)", TEXT),
                    (FN(1) + " = (3/5, 0, 4/5)", PRACTICE),
                    (FN(2) + " = (0, 1, 0)", BASE),
                    (FN(3) + " = (" + MINUS_S + "4/5, 0, 3/5)", THEORY)])
block(1.60, 4.65, [(bold("q") + " = (0, 4, 3)", TEXT),
                   (FN(1) + " = (0, 4/5, 3/5)", PRACTICE),
                   (FN(2) + " = (" + MINUS_S + "1, 0, 0)", BASE),
                   (FN(3) + " = (0, " + MINUS_S + "3/5, 4/5)", THEORY)])

OUT["cati-kuresel-cati"] = figure(
    490, 420, [P],
    "Yarıçapı 5 olan kürenin <em>x</em>, <em>y</em>, <em>z</em> &#8805; 0 parçası üzerinde "
    "küresel çatı alanının iki noktadaki değerleri: <strong>p</strong> = (3, 0, 4) ve "
    "<strong>q</strong> = (0, 4, 3). Her iki noktada da <em>F</em><sub>1</sub> (turuncu) "
    "başlangıç noktasından dışa, yani küreye dik bakar; <em>F</em><sub>2</sub> (yeşil) paralel "
    "çember boyunca doğuya, <em>F</em><sub>3</sub> (mavi) meridyen boyunca kuzeye bakar ve ikisi "
    "de küreye teğettir. Kesikli çizgiler <em>&#961;</em> = 5 yarıçapını, yaylar "
    "<em>&#977;</em> ile <em>&#966;</em> açılarını okutur: ilk noktada <em>&#977;</em> = 0, "
    "ikincide <em>&#977;</em> = &#960;/2&#8217;dir. <em>F</em><sub>1</sub>&#8217;in vektör kısmı "
    "her seferinde noktanın koordinatlarının 5&#8217;e bölümüdür.",
    aria="Yaricapi 5 olan kurenin x, y ve z koordinatlari negatif olmayan sekizde birlik "
         "parcasi uzerinde kuresel cati alani. "
         "p = (3, 0, 4) noktasinda F1 = (3/5, 0, 4/5), F2 = (0, 1, 0), F3 = (-4/5, 0, 3/5); "
         "q = (0, 4, 3) noktasinda F1 = (0, 4/5, 3/5), F2 = (-1, 0, 0), F3 = (0, -3/5, 4/5). "
         "Kesikli yaricaplar rho = 5, yaylar vartheta ve phi acilarini gosterir; F1 kureye dik, "
         "F2 ile F3 kureye tegettir.",
)

# ============================================================ cati-kuresel-duzlem
# -*- coding: utf-8 -*-
# cati-kuresel-duzlem: the half plane vartheta = 0 (horizontal axis r, vertical axis z) with the
# point p = (3, 0, 4) of the worked example: r = 3, z = 4, rho = 5, cos phi = 3/5, sin phi = 4/5.
# Four unit arrows sit at p: the cylindrical frame E1 = (1, 0) and E3 = (0, 1) in grey, and the
# spherical frame F1 = (3/5, 4/5) (orange, the outward direction O -> p) and F3 = (-4/5, 3/5)
# (blue, ninety degrees ahead of F1, pointing north). Three arcs carry the same angle phi: at the
# origin between the r axis and the ray Op, at p between E1 and F1, and at p between E3 and F3 --
# that is the whole content of F1 = cos phi E1 + sin phi E3, F3 = -sin phi E1 + cos phi E3.
# The thin grey segment O->p and the orange arrow are deliberately collinear: F1 is the
# continuation of the radius, which is why its vector part is p/rho.
# Layout: the empty lower right quadrant takes the two identities, the empty top left takes the
# name of the plane; equal aspect (cplane) is required, every angle in the picture is read off.
import math

PHI = math.atan2(4.0, 3.0)          # 53.13 degrees; cos = 3/5, sin = 4/5 exactly
COSP, SINP = 0.6, 0.8

PHI_S = "&#966;"                    # varphi, as in the text
TH_S = "&#977;"                     # vartheta
RHO_S = "&#961;"                    # rho


def ital(s):
    return f'<tspan font-style="italic">{s}</tspan>'


def tint(s, color):
    return f'<tspan fill="{color}">{s}</tspan>'


def EE(k):
    return ital("E") + subs(k)


def FF(k):
    return ital("F") + subs(k)


pl = cplane(32, 18, 340, (-0.70, 6.35), (-0.80, 5.80))

O = (0.0, 0.0)
PT = (3.0, 4.0)
FOOT = (3.0, 0.0)
E1 = (4.0, 4.0)                      # PT + (1, 0)
E3 = (3.0, 5.0)                      # PT + (0, 1)
F1 = (3.6, 4.8)                      # PT + (3/5, 4/5)
F3 = (2.2, 4.6)                      # PT + (-4/5, 3/5)
RMAX, ZMAX = 6.10, 5.55
GREY = 0.66                          # the cylindrical frame is drawn in the text colour, faded

# ---------------------------------------------------------------- 1. axes of the half plane
pl.arrow(O, (RMAX, 0.0), TEXT, 1.1, 7, None, 0.55)
pl.arrow((0.0, -0.55), (0.0, ZMAX), TEXT, 1.1, 7, None, 0.55)

# ---------------------------------------------------------------- 2. how p is read off
guide(pl, [FOOT, PT], TEXT, 0.55)                     # the height z = 4
pl.line([O, PT], TEXT, 1.3, None, 0.55)               # the radius rho = 5, continued by F1

# ---------------------------------------------------------------- 3. the three angle arcs
pl.arc(0.0, 0.0, 0.80, 0.0, PHI, TEXT, 1.2, None, 0.80)
pl.arc(PT[0], PT[1], 0.45, 0.0, PHI, TEXT, 1.2, None, 0.80)
pl.arc(PT[0], PT[1], 0.45, math.pi / 2, math.pi / 2 + PHI, TEXT, 1.2, None, 0.80)

# ---------------------------------------------------------------- 4. the four unit arrows
pl.arrow(PT, E1, TEXT, 2.0, 8.5, None, GREY)
pl.arrow(PT, E3, TEXT, 2.0, 8.5, None, GREY)
pl.arrow(PT, F1, PRACTICE, 2.5, 9.5)
pl.arrow(PT, F3, THEORY, 2.5, 9.5)

dot(pl, O, TEXT, 3.2)
dot(pl, FOOT, TEXT, 2.8)
dot(pl, PT, TEXT, 3.6)

# ---------------------------------------------------------------- 5. labels
pl.label(RMAX, 0.0, "r", -2, 17, TEXT, 11.5, "middle", False, True)
pl.label(0.0, ZMAX, "z", 8, -1, TEXT, 11.5, "start", False, True)
pl.label(0.0, 0.0, "O", -7, 15, TEXT, 11.5, "end")
pl.label(PT[0], PT[1], bold("p") + " = (3, 0, 4)", 9, 17, TEXT, 11.5, "start")

pl.label(1.5, 2.0, ital(RHO_S) + " = 5", -9, -2, TEXT, 11.5, "end")
pl.label(1.5, 0.0, ital("r") + " = 3", 0, 17, TEXT, 11.5, "middle")
pl.label(3.0, 3.10, ital("z") + " = 4", 8, 4, TEXT, 11.5, "start")

# the same phi three times: at the origin and in the two wedges at p
pl.label(1.02 * math.cos(PHI / 2), 1.02 * math.sin(PHI / 2), ital(PHI_S), 0, 4, TEXT, 12.5, "middle")
pl.label(PT[0] + 0.70 * math.cos(PHI / 2), PT[1] + 0.70 * math.sin(PHI / 2),
         ital(PHI_S), 0, 4, TEXT, 11.5, "middle")
pl.label(PT[0] - 0.70 * math.sin(PHI / 2), PT[1] + 0.70 * math.cos(PHI / 2),
         ital(PHI_S), 0, 4, TEXT, 11.5, "middle")

pl.label(E1[0], E1[1], EE("1"), 9, -5, TEXT, 11.5, "start")
pl.label(E3[0], E3[1], EE("3"), 0, -9, TEXT, 11.5, "middle")
pl.label(F1[0], F1[1], FF("1") + " (dışa)", 7, -4, PRACTICE, 12, "start")
pl.label(F3[0], F3[1], FF("3") + " (kuzeye)", -7, -4, THEORY, 12, "end")

# the name of the plane, in the empty top left corner
pl.label(0.55, 5.40, ital(TH_S) + " = 0 yarım düzlemi", 0, 0, TEXT, 11.5, "start")

# the two identities, in the empty lower right quadrant
BX, BY = pl.X(3.15), pl.Y(1.80)
pl.text_px(BX, BY, tint(FF("1"), PRACTICE) + " = cos " + ital(PHI_S) + " " + EE("1")
           + " + sin " + ital(PHI_S) + " " + EE("3"), TEXT, 11.5)
pl.text_px(BX, BY + 21, tint(FF("3"), THEORY) + " = " + MINUS_S + "sin " + ital(PHI_S) + " "
           + EE("1") + " + cos " + ital(PHI_S) + " " + EE("3"), TEXT, 11.5)
pl.text_px(BX, BY + 50, "cos " + ital(PHI_S) + " = 3/5,&#160;&#160;&#160;sin " + ital(PHI_S)
           + " = 4/5", TEXT, 11)

OUT["cati-kuresel-duzlem"] = figure(
    400, 360, [pl],
    "<em>&#977;</em> = 0 yarım düzleminde çizilen <strong>p</strong> = (3, 0, 4) noktasının yatay "
    "uzaklığı <em>r</em> = 3, yüksekliği <em>z</em> = 4, başlangıç noktası O&#8217;ya uzaklığı "
    "<em>&#961;</em> = 5&#8217;tir. "
    "Silindirik çatının <em>E</em><sub>1</sub> (yatay) ve <em>E</em><sub>3</sub> (düşey) okları "
    "gri çizilmiştir; küresel çatının <em>F</em><sub>1</sub> oku (turuncu) O&#8217;dan "
    "<strong>p</strong>&#8217;ye bakan doğrultunun devamıdır, <em>F</em><sub>3</sub> oku (mavi) ondan "
    "90&#176; ileride kuzeye bakar. Üç yay da aynı <em>&#966;</em> açısını işaretler: "
    "<em>F</em><sub>1</sub>, <em>F</em><sub>3</sub> ikilisi <em>E</em><sub>1</sub>, "
    "<em>E</em><sub>3</sub> ikilisinin <em>&#966;</em> kadar döndürülmüşüdür. Burada "
    "cos <em>&#966;</em> = 3/5 ve sin <em>&#966;</em> = 4/5 olduğundan <em>F</em><sub>1</sub>&#8217;in "
    "vektör kısmı (3/5, 0, 4/5), <em>F</em><sub>3</sub>&#8217;ün vektör kısmı ise "
    "(&#8722;4/5, 0, 3/5) çıkar.",
    aria="Dikey yarim duzlem, yatay eksen r ve dusey eksen z; p = (3, 0, 4) noktasi r = 3, z = 4 "
         "konumunda; O dan p ye cizilen dogru parcasi rho = 5 uzunlugunda ve yatay eksenle phi "
         "acisi yapar; p de dort birim ok: gri E1 yatay, gri E3 dusey, turuncu F1 O p "
         "dogrultusunda vektor kismi (3/5, 0, 4/5), mavi F3 ondan 90 derece ileride vektor kismi "
         "(-4/5, 0, 3/5); E1 ile F1 arasindaki ve E3 ile F3 arasindaki yaylar ayni phi acisini "
         "gosterir",
)

# ============================================================ cati-silindirik-cati
# -*- coding: utf-8 -*-
# cati-silindirik-cati: the cylindrical frame field E1, E2, E3 of the example, evaluated at
# p = (3, 4, 2), q = (-4, 3, 0) and s = (0, -5, 1). All three lie on the cylinder r = 5, drawn
# as a translucent grey tube. The vector parts come out of the formula E1 = (x/r, y/r, 0),
# E2 = (-y/r, x/r, 0), E3 = (0, 0, 1) and are asserted against the table in the box.
# Colours follow teget-dogal-cati: E1 -> PRACTICE, E2 -> BASE, E3 -> THEORY (the palette has no
# red token, so the radial field takes the orange one).
# Camera: azimuth 20 is the largest-clearance choice inside the API's 20-50 band — the three
# points sit at the polar angles 53.13, 143.13 and 270 degrees, and at az = 20 none of the six
# horizontal arrows points at the viewer (the shortest, E2 at s, still projects to 0.56 of a unit).
# Elevation 28 opens the rim ellipses and lifts that shortest projection.
# The far half of the bottom rim is left out (it is hidden behind the body of the tube); that also
# keeps the neighbourhoods of q and s, which both sit on the far wall, free of guide lines.
# What is left running through them is the front lip of the mouth, which the E3 arrows of q and s
# cross — correctly, the near wall is in front of them. The labels are the ones kept off it: every
# one of them sits wholly above or wholly below that arc.
import math

AZ, EL = 20.0, 28.0
R = 5.0                              # radius of the cylinder every point stands on
ZB, ZT = -0.7, 3.45                  # drawn height range of the tube
AXX, AXY, AXZ = 4.8, 6.2, 4.25       # axis ends: x stops inside the tube, y pierces it at (0, 5, 0)
PHI = math.radians(AZ)               # cos(u - PHI) > 0 on the half of the tube facing the viewer
NEAR = (PHI - math.pi / 2, PHI + math.pi / 2)
FAR = (PHI + math.pi / 2, PHI + 3 * math.pi / 2)

P = space_panel(18, 16, 440, (-6.6, 6.7), (-3.9, 5.7))
S = Space(P, Camera(azimuth=AZ, elevation=EL, scale=1.0))

TH = "&#977;"                        # vartheta, as in the text


def ital(s):
    return '<tspan font-style="italic">' + s + '</tspan>'


def ename(k):
    """The field name E_k, italic with a subscript."""
    return ital("E") + subs(k)


def halo(x, y, s, color=TEXT, size=11, anchor="start"):
    """Text at a pixel position on a page-coloured halo, so faint lines break around it."""
    P.add(f'<text x="{x:.1f}" y="{y:.1f}" fill="{color}" font-size="{size}" text-anchor="{anchor}" '
          f'stroke="{BG}" stroke-width="3.2" stroke-linejoin="round" paint-order="stroke">{s}</text>')


def at(Q, s, dx=0, dy=0, color=TEXT, size=11, anchor="start"):
    """Halo text hung on a space point."""
    X, Y = S.pt(Q)
    halo(P.X(X) + dx, P.Y(Y) + dy, s, color, size, anchor)


def tube(u, z):
    return (R * math.cos(u), R * math.sin(u), z)


def rim(z, u0, u1, opacity=0.45, dash=None, n=64):
    S.line([tube(u0 + (u1 - u0) * k / n, z) for k in range(n + 1)], TEXT, 0.9, dash, opacity)


def frame_at(Q):
    """The cylindrical frame at Q: E1 = (cos t, sin t, 0), E2 = (-sin t, cos t, 0), E3 = U3."""
    x, y, _ = Q
    r = math.hypot(x, y)
    c, s = x / r, y / r
    return ((c, s, 0.0), (-s, c, 0.0), (0.0, 0.0, 1.0))


def draw_frame(Q):
    e1, e2, e3 = frame_at(Q)
    S.arrow(Q, vadd(Q, e1), PRACTICE, 2.2, head=7)
    S.arrow(Q, vadd(Q, e2), BASE, 2.2, head=7)
    S.arrow(Q, vadd(Q, e3), THEORY, 2.2, head=7)
    S.point(Q, TEXT, 3.4)


def tip(Q, k):
    return vadd(Q, frame_at(Q)[k])


p = (3.0, 4.0, 2.0)
q = (-4.0, 3.0, 0.0)
s = (0.0, -5.0, 1.0)
foot = (3.0, 4.0, 0.0)               # the projection of p on the xy plane

# --- the numbers of the box, checked before anything is drawn ----------------------------------
TABLE = {p: ((0.6, 0.8, 0.0), (-0.8, 0.6, 0.0)),
         q: ((-0.8, 0.6, 0.0), (-0.6, -0.8, 0.0)),
         s: ((0.0, -1.0, 0.0), (1.0, 0.0, 0.0))}
for Q, (t1, t2) in TABLE.items():
    e1, e2, e3 = frame_at(Q)
    assert vnorm(vsub(e1, t1)) < 1e-12 and vnorm(vsub(e2, t2)) < 1e-12, Q
    assert abs(vnorm(e1) - 1) < 1e-12 and abs(vnorm(e2) - 1) < 1e-12 and abs(vnorm(e3) - 1) < 1e-12
    assert abs(vdot(e1, e2)) < 1e-12 and abs(vdot(e1, e3)) < 1e-12 and abs(vdot(e2, e3)) < 1e-12
    # E1 points straight out from the z axis, E2 turns counter-clockwise about it
    assert vnorm(vsub(e1, vunit((Q[0], Q[1], 0.0)))) < 1e-12
    assert vnorm(vsub(e2, vcross((0.0, 0.0, 1.0), e1))) < 1e-12
    assert abs(math.hypot(Q[0], Q[1]) - R) < 1e-12
    print("%-18s E1 = %-18s E2 = %-18s sayfada |E1| = %.2f, |E2| = %.2f, nokta = (%.2f, %.2f)" %
          (Q, t1, t2, math.dist(S.pt(vadd(Q, e1)), S.pt(Q)), math.dist(S.pt(vadd(Q, e2)), S.pt(Q)),
           S.pt(Q)[0], S.pt(Q)[1]))

# --- floor, far wall of the tube ---------------------------------------------------------------
S.floor_grid((-3.5, 3.5), (-3.5, 3.5), n=4, opacity=0.09)
S.surface(tube, FAR, (ZB, ZT), nu=22, nv=1, fill=TEXT, stroke="none", opacity=(0.02, 0.075))
rim(ZT, *FAR, opacity=0.30)          # the far lip of the mouth; the far bottom arc stays hidden

# --- axes and ticks (they run inside the tube) --------------------------------------------------
S.axes(AXX, AXY, AXZ, offsets=((-4, 13), (10, 4), (-10, -4)))
S.ticks("y", (5,), length=0.3)
S.ticks("z", (1, 2, 3), length=0.3, offset=(-9, -2))   # a touch high: the front lip of the mouth
                                                      # runs just under the 1

# --- the cylindrical coordinates of p, read off on the floor and along the riser -----------------
S.guide([(0, 0, 0), foot], TEXT, 0.6, 1.1, "5 3")            # r = 5
S.guide([foot, p], TEXT, 0.6, 1.1, "5 3")                    # z = 2
ANG = [(2.4 * math.cos(t), 2.4 * math.sin(t), 0.0)
       for t in [math.atan2(4, 3) * k / 40 for k in range(41)]]
S.line(ANG[:-2], TEXT, 1.1, None, 0.7)
S.arrow(ANG[-4], ANG[-1], TEXT, 1.1, 6.0, None, 0.7)

# --- the two points on the far wall -------------------------------------------------------------
draw_frame(q)
draw_frame(s)

# --- near wall of the tube ----------------------------------------------------------------------
S.surface(tube, NEAR, (ZB, ZT), nu=22, nv=1, fill=TEXT, stroke="none", opacity=(0.02, 0.075))
rim(ZT, *NEAR, opacity=0.5)
rim(ZB, *NEAR, opacity=0.45)
for u in NEAR:
    # light: E2 at s ends right on the left edge of the tube, and a darker line would swallow
    # the arrowhead; the shading of the wall already marks the silhouette
    S.line([tube(u, ZB), tube(u, ZT)], TEXT, 0.9, None, 0.32)

# --- p, on the near wall ------------------------------------------------------------------------
S.point(foot, TEXT, 2.4)
draw_frame(p)

# --- labels -------------------------------------------------------------------------------------
at(p, bold("p") + " = (3, 4, 2)", -10, -9, TEXT, 11, "end")
at(q, bold("q") + " = (" + MINUS_S + "4, 3, 0)", -13, -26, TEXT, 11, "end")
at(s, bold("s") + " = (0, " + MINUS_S + "5, 1)", 9, -16, TEXT, 11, "start")   # above the front lip

at(tip(p, 0), ename("1"), 6, 21, PRACTICE, 11, "start")   # well clear of the y axis below it
at(tip(p, 1), ename("2"), 7, -3, BASE, 11, "start")
at(tip(p, 2), ename("3"), 7, 4, THEORY, 11, "start")      # beside, not above: the lip runs there
at(tip(q, 0), ename("1"), 7, -2, PRACTICE, 11, "start")
at(tip(q, 1), ename("2"), -15, 6, BASE, 11, "end")
at(tip(q, 2), ename("3"), 0, -8, THEORY, 11, "middle")
at(tip(s, 0), ename("1"), 0, -8, PRACTICE, 11, "middle")
at(tip(s, 1), ename("2"), -3, 12, BASE, 11, "end")
at(tip(s, 2), ename("3"), 0, -8, THEORY, 11, "middle")

at((2.1, 2.8, 0.0), ital("r") + " = 5", -16, 18, TEXT, 11, "middle")     # 70% along the r guide
at((3.0, 4.0, 1.24), ital("z") + " = 2", -7, 4, TEXT, 11, "end")          # 62% up the riser
at((1.6 * math.cos(math.atan2(4, 3) / 2), 1.6 * math.sin(math.atan2(4, 3) / 2), 0.0),
   ital(TH), 0, 4, TEXT, 12, "middle")

OUT["cati-silindirik-cati"] = figure(
    476, 350, [P],
    "Silindirik çatı alanının üç noktadaki değerleri: <strong>p</strong> = (3, 4, 2), "
    "<strong>q</strong> = (&#8722;4, 3, 0) ve <strong>s</strong> = (0, &#8722;5, 1); üçü de "
    "<em>r</em> = 5 silindirinin üzerindedir. Her noktada <em>E</em><sub>1</sub> (turuncu) "
    "<em>z</em> ekseninden dışa, <em>E</em><sub>2</sub> (yeşil) silindirin çevresi boyunca dönme "
    "yönüne, <em>E</em><sub>3</sub> (mavi) yukarı bakar. Nokta <em>z</em> ekseninin çevresinde "
    "döndükçe <em>E</em><sub>1</sub> ile <em>E</em><sub>2</sub> birlikte döner, "
    "<em>E</em><sub>3</sub> ise hiç değişmez. Kesikli çizgiler <strong>p</strong>&#8217;nin "
    "silindirik koordinatlarını okur: taban uzaklığı <em>r</em> = 5, taban açısı "
    "<em>&#977;</em> ve yükseklik <em>z</em> = 2.",
    aria="Yari saydam r = 5 silindiri uzerinde uc nokta: p = (3, 4, 2), q = (-4, 3, 0), "
         "s = (0, -5, 1). Her noktada silindirik cati alaninin uc birim oku: E1 turuncu, z "
         "ekseninden disa; E2 yesil, cember boyunca donme yonunde; E3 mavi, yukari. p icin kesikli "
         "kilavuzlar taban uzakligi r = 5, taban acisi theta ve yukseklik z = 2 degerlerini okutur.",
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

# ============================================================ frenet-cember-merkez-egrisi
# -*- coding: utf-8 -*-
# frenet-cember-merkez-egrisi: the lemma "constant kappa, zero torsion => a circle of radius
# 1/kappa", drawn on the concrete curve of the box, beta(s) = (2cos(s/2), 2sin(s/2), 0), whose
# plane is z = 0 — so the panel is that plane and its points are written as pairs.
# kappa = 1/2, so the radius is 1/kappa = 2 and N = (-cos(s/2), -sin(s/2)) has length 1: every N
# arrow stops exactly halfway to the centre and the dashed rest of the radius carries 1/kappa = 2.
# Marked points, straight from the box: s = 0 -> (2, 0), s = pi/2 -> (1,414; 1,414), s = pi -> (0, 2).
# Checked by hand at each of them: T . (radial direction) = 0 (T is tangent) and T . N = 0, with
# N = -(radial direction) (N looks at the centre); see TANGENT_CHECK below, which asserts it.
# Colours follow API.md rather than the wording of the draft note: the curve is THEORY, the unit
# tangent T is PRACTICE ("teget vektorler ve oklar PRACTICE"), the second vector N is BASE.
# Layout notes, after three rounds of looking at the raster:
#  * At s = 0 both N and the radius lie along the x axis, so 1/kappa = 2 is written above the
#    segment and N below it, in the gap between the tick labels 1 and 2.
#  * At s = pi/2 the label 1/kappa = 2 had to move past the arrowhead of N, which lands at
#    (0,707; 0,707): it now lies along the arrow on its lower-right side, twice as far from the
#    x axis as from its own ray, so it cannot be read as belonging to the radius at s = 0.
#  * The radius at s = pi is named at y = 0,60, below the y tick 1 — at 0,78 the two collided.
#  * y ticks other than 1 are dropped: 2 would sit on the shaft of the T arrow leaving (0, 2), and
#    below the axis the room is taken by the centre annotation.
#  * The dashed radii are drawn at opacity 0.7 (the axes are at 0.45) so that the two that run
#    along an axis still read as separate segments.
import math

R = 2.0                      # 1/kappa
XR, YR = (-3.3, 3.3), (-1.75, 3.0)
p = cplane(34, 26, 336, XR, YR)
PPU = 336 / (XR[1] - XR[0])  # pixels per data unit


def beta(s):
    return (R * math.cos(s / 2), R * math.sin(s / 2))


def T_of(s):
    return (-math.sin(s / 2), math.cos(s / 2))


def N_of(s):
    return (-math.cos(s / 2), -math.sin(s / 2))


# --- the facts the figure claims, verified before anything is drawn ---------------------------
def TANGENT_CHECK():
    for s in (0.0, math.pi / 2, math.pi):
        b, t, n = beta(s), T_of(s), N_of(s)
        radial = (b[0] / R, b[1] / R)                       # unit vector from the centre to beta
        assert abs(t[0] * radial[0] + t[1] * radial[1]) < 1e-12      # T is tangent to the circle
        assert abs(t[0] * n[0] + t[1] * n[1]) < 1e-12                # N is perpendicular to T
        assert math.hypot(n[0] + radial[0], n[1] + radial[1]) < 1e-12  # N points at the centre
        assert abs(math.hypot(*n) - 1.0) < 1e-12                     # N is a unit vector
        assert abs(math.hypot(*t) - 1.0) < 1e-12                     # T is a unit vector
        # beta + (1/kappa) N = the centre, for every s
        assert math.hypot(b[0] + R * n[0], b[1] + R * n[1]) < 1e-12


TANGENT_CHECK()


def it(s):
    return '<tspan font-style="italic">' + s + '</tspan>'


BETA, GAMMA, KAPPA, TAU = it("&#946;"), it("&#947;"), it("&#954;"), it("&#964;")
T_S, N_S, C_S, S_S = bold("T"), bold("N"), bold("c"), it("s")
RADIUS_TXT = "1/" + KAPPA + " = 2"

# --- 1. axes, the three radii of length 1/kappa = 2, then the arc beta runs along --------------
p.origin_axes("x", "y", xticks=(-3, -2, -1, 1, 2, 3), yticks=(1,), opacity=0.45)

MARKS = (0.0, math.pi / 2, math.pi)
for s in MARKS:
    guide(p, [beta(s), (0, 0)], TEXT, 0.7, 1.15)
p.arc(0, 0, R, 0, math.pi, THEORY, 2.6)

# --- 2. the Frenet vectors: T tangent (orange), N of length 1 towards the centre (green) -------
for s in MARKS:
    b, t = beta(s), T_of(s)
    p.arrow(b, (b[0] + t[0], b[1] + t[1]), PRACTICE, 2.1, head=8)
for s in MARKS:
    b, n = beta(s), N_of(s)
    p.arrow(b, (b[0] + n[0], b[1] + n[1]), BASE, 2.1, head=8)
for s in MARKS:
    dot(p, beta(s), TEXT, 3.4)
dot(p, (0, 0), TEXT, 4.4)                                          # the centre c = gamma

# --- 3. labels at the three points -------------------------------------------------------------
# s = 0 at (2, 0): the point labels go to the right, above the x axis (the tick labels are below
# it); N and the radius run along the axis, so they are named above and below the same segment.
p.label(2, 0, S_S + " = 0", 10, -22, TEXT, 10.5, "start")
p.label(2, 0, "(2, 0)", 10, -8, TEXT, 11, "start")
p.label(2, 1, T_S, 8, 1, PRACTICE, 12, "start")
p.label(1.52, 0, N_S, 0, 13, BASE, 12, "middle")
p.label(0.78, 0, RADIUS_TXT, 0, -9, TEXT, 10.5, "middle")

# s = pi/2 at (1,414; 1,414): both arrows leave to the left, so the point labels go outward to the
# upper right; N is named close to its tail, the radius length across the ray on the other side.
b2, t2, n2 = beta(math.pi / 2), T_of(math.pi / 2), N_of(math.pi / 2)
p.label(b2[0], b2[1], S_S + " = " + PI_S + "/2", 12, -20, TEXT, 10.5, "start")
p.label(b2[0], b2[1], APPROX + " (1,414; 1,414)", 12, -6, TEXT, 11, "start")
p.label(b2[0] + t2[0], b2[1] + t2[1], T_S, -8, -4, PRACTICE, 12, "end")
p.label(1.36, 1.04, N_S, 0, 0, BASE, 12, "middle")
p.label(1.336, 0.682, RADIUS_TXT, 0, 0, TEXT, 10.5, "middle")

# s = pi at (0, 2): T leaves to the left, N straight down the y axis; the point labels are stacked
# above the T arrow, N and the radius length on the left of the axis.
p.label(0, 2, S_S + " = " + PI_S, -10, -28, TEXT, 10.5, "end")
p.label(0, 2, "(0, 2)", -10, -14, TEXT, 11, "end")
p.label(-1, 2, T_S, -8, -5, PRACTICE, 12, "end")
p.label(0, 1.45, N_S, -8, 0, BASE, 12, "end")
p.label(0, 0.60, RADIUS_TXT, -8, 0, TEXT, 10.5, "end")

# --- 4. the curve with its invariants, the centre, the parametrisation -------------------------
p.label(-R * math.cos(math.radians(30)), R * math.sin(math.radians(30)), BETA,
        -9, -3, THEORY, 12.5, "end")
p.label(-3.2, 2.78, KAPPA + " = 1/2 (sabit)", 0, 0, THEORY, 11, "start")
p.label(-3.2, 2.48, TAU + " = 0", 0, 0, THEORY, 11, "start")

p.label(0, 0, GAMMA + " = " + BETA + " + (1/" + KAPPA + ") " + N_S + " = " + C_S,
        -12, 31, TEXT, 11, "end")
p.label(0, 0, "= (0, 0) sabit", -12, 46, TEXT, 11, "end")

p.label(3.2, -1.45,
        BETA + "(" + S_S + ") = (2cos(" + S_S + "/2), 2sin(" + S_S + "/2))",
        0, 0, TEXT, 10, "end")

OUT["frenet-cember-merkez-egrisi"] = figure(
    400, 300, [p],
    "Eğriliği <em>&#954;</em> = 1/2 sabit, burulması sıfır olan <em>&#946;</em> eğrisi "
    "1/<em>&#954;</em> = 2 yarıçaplı bir çemberin parçasıdır; şekildeki düzlem, eğrinin içinde "
    "kaldığı <em>z</em> = 0 düzlemidir ve noktalar orada (<em>x</em>, <em>y</em>) çiftiyle "
    "yazılmıştır. İşaretli üç noktada birim teğet <strong>T</strong> "
    "(turuncu) çembere teğettir; asli normal <strong>N</strong> (yeşil) ona diktir, birim "
    "uzunluktadır ve merkeze bakar. Her noktadan <strong>N</strong> yönünde 1/<em>&#954;</em> = 2 "
    "kadar ilerlenince (kesikli gri parçalar) hep aynı yere varılır: <em>&#947;</em> = "
    "<em>&#946;</em> + (1/<em>&#954;</em>)<strong>N</strong> sabittir ve değeri çemberin merkezi "
    "<strong>c</strong> = (0, 0)&#8217;dır. Eğrinin her noktası bu sabit noktadan tam "
    "1/<em>&#954;</em> = 2 uzaklıktadır.",
    aria="xy duzleminde merkezi (0, 0) olan 2 yaricapli cemberin ust yarisi kalin mavi cizilmis; "
         "uzerinde s = 0 icin (2, 0), s = pi/2 icin yaklasik (1,414; 1,414) ve s = pi icin (0, 2) "
         "noktalari isaretli. Her noktada cembere teget turuncu T oku ve ona dik, merkeze bakan "
         "1 boyunda yesil N oku var; her noktadan merkeze giden kesikli gri parca 1/kappa = 2 "
         "uzunlugundadir. Merkezdeki buyuk nokta gamma = beta + (1/kappa) N sabitidir, degeri "
         "c = (0, 0). Egri beta(s) = (2cos(s/2), 2sin(s/2)) olup kappa = 1/2 sabit, tau = 0",
)

# ============================================================ frenet-duzlem-egriligi
# -*- coding: utf-8 -*-
# frenet-duzlem-egriligi: the slope angle of the parabola y = x^2/2 and its derivative.
# Left panel (equal scale): the parabola in orange, and at x = -1, 0, 1.5 the unit tangent T (blue)
# with the unit normal N = T turned 90 degrees to the left (green). A thin grey ray parallel to the
# x axis leaves every point; the shaded wedge between that ray and T carries the slope angle
#   phi = arctan(x):  -45 at x = -1, 0 at x = 0, 56.31 at x = 1.5   (the numbers of the box).
# Right panel: phi against arc length s(x) = (x sqrt(1+x^2) + asinh x)/2, with the tangent of the
# graph at s = 0 in grey; its slope is the plane curvature.
# Drawing notes. At x = -1 the parabola runs *inside* its own angle wedge (it leaves the point along
# T and bends up towards the grey ray), so the wedge is shaded and its outline is drawn before the
# curve: the curve crosses it cleanly instead of swallowing the arc's end. At x = 0 the tangent lies
# along the grey ray itself — that is what phi = 0 means — so the ray is drawn past the arrowhead and
# the 0 degree label hangs under its free end. The wedge is only 0.77 r wide, so the angle labels
# are bare numbers; the letter phi is fixed by T = (cos phi, sin phi), written inside the cup.
import math

KAPPA, PHI_S, DEG = "&#954;", "&#966;", "&#176;"
XS = (-1.0, 0.0, 1.5)
GUIDE_LEN = {-1.0: 0.90, 0.0: 1.35, 1.5: 0.85}
WEDGE_R = {-1.0: 0.50, 0.0: 0.0, 1.5: 0.50}


def par(x):
    return (x, x * x / 2)


def tangent(x):
    n = math.hypot(1.0, x)
    return (1.0 / n, x / n)


def normal(x):
    t = tangent(x)
    return (-t[1], t[0])            # T turned 90 degrees to the left: N = (-y', x')


def arclen(x):
    return (x * math.sqrt(1 + x * x) + math.asinh(x)) / 2


def ital(s):
    return f'<tspan font-style="italic">{s}</tspan>'


def ktilde(size=11.0):
    """Kappa with a tilde over it. The combining accent U+0303 is not in the book's font, so the
    tilde is a raised tspan pulled back over the letter; the advance it eats is handed back."""
    ts = 0.92 * size
    wK, wT = 0.52 * size, 0.50 * ts          # advances of kappa and of the tilde
    dx = -(wK + wT) / 2 + 0.10 * size        # the last term centres the ink, measured in the PNG
    return (KAPPA
            + f'<tspan dx="{dx:.2f}" dy="{-0.46 * size:.2f}" font-size="{ts:.1f}">~</tspan>'
            + f'<tspan dx="{-wT - dx:.2f}" dy="{0.46 * size:.2f}">&#8203;</tspan>')


# ===================================================================== left panel: the parabola
A = cplane(22, 16, 350, (-2.40, 2.70), (-0.60, 2.70))     # 68.6 px per unit, equal scale

A.axes((-2, -1, 0, 1, 1.5, 2), (0, 1, 2), "x", "y", xfmt=tfmt)

# dashed drop from each marked point to the x axis, so the tick reads off the point
for x in XS:
    guide(A, [par(x), (x, A.ymin)], TEXT, 0.30)

# rays parallel to the x axis and the shaded angle wedges — under the curve
for x in XS:
    p = par(x)
    A.line([p, (p[0] + GUIDE_LEN[x], p[1])], TEXT, 1.0, None, 0.45)
    if WEDGE_R[x]:
        A.sector(p[0], p[1], WEDGE_R[x], 0.0, math.atan(x), TEXT, 0.13)
        A.arc(p[0], p[1], WEDGE_R[x], 0.0, math.atan(x), TEXT, 1.2, None, 0.8)

curve(A, lambda t: t * t / 2, -2.0, 2.2, PRACTICE, 2.6, 300)
A.label(-1.95, 2.36, ital("y") + " = " + ital("x") + sups("2") + "/2", 0, 0, PRACTICE, 12)

for x in XS:
    p, T, N = par(x), tangent(x), normal(x)
    A.arrow(p, (p[0] + T[0], p[1] + T[1]), THEORY, 2.4, 9)
    A.arrow(p, (p[0] + N[0], p[1] + N[1]), BASE, 2.4, 9)
    dot(A, p, TEXT, 3.4)

# vector names, each pushed to the free side of its own arrowhead
# T at x = -1 hangs below-left of its head: to the right it would touch the dashed drop at x = 0
A.label(-0.2929, -0.2071, bold("T"), -7, 14, THEORY, 12.5, "end")
A.label(-0.2929, 1.2071, bold("N"), -12, -5, BASE, 12.5, "end")
A.label(1.0, 0.0, bold("T"), 3, -9, THEORY, 12.5)
A.label(0.0, 1.0, bold("N"), 8, -2, BASE, 12.5)
A.label(2.0547, 1.9571, bold("T"), 9, 10, THEORY, 12.5)
A.label(0.6679, 1.6797, bold("N"), -8, -4, BASE, 12.5, "end")

# the three slope angles, just outside their wedges (x = 0 has none: there the angle is zero)
A.label(-0.26, 0.22, MINUS_S + "45" + DEG, 0, 0, TEXT, 11, "middle")
A.label(1.15, -0.26, "0" + DEG, 0, 0, TEXT, 11, "middle")
A.label(2.26, 1.40, "56,3" + DEG, 0, 0, TEXT, 11, "middle")

# the two Frenet ingredients, written in the free cup of the parabola
A.label(0.35, 2.42, bold("T") + " = (cos " + PHI_S + ", sin " + PHI_S + ")", 0, 0, THEORY, 12,
        "middle")
A.label(0.35, 2.06, bold("N") + " = (" + MINUS_S + "sin " + PHI_S + ", cos " + PHI_S + ")", 0, 0,
        BASE, 12, "middle")

panel_title(A, "Birim teğet " + bold("T") + ", birim normal " + bold("N") + " ve eğim açısı "
            + PHI_S, TEXT, 11.5)

# ===================================================================== right panel: phi(s)
B = Plot(396, 68, 198, 174, (-2.35, 2.95), (-80, 88))
DEG_PER_UNIT = math.degrees(1.0)          # slope of the tangent at s = 0, where the curvature is 1

B.origin_axes(ital("s"), PHI_S)
B.line([(arclen(-1.35 + 3.15 * k / 240), math.degrees(math.atan(-1.35 + 3.15 * k / 240)))
        for k in range(241)], THEORY, 2.2)
B.line([(-0.85, -0.85 * DEG_PER_UNIT), (0.95, 0.95 * DEG_PER_UNIT)], TEXT, 1.5, None, 0.9)
for x in XS:
    dot(B, (arclen(x), math.degrees(math.atan(x))), TEXT, 3.2)

B.label(arclen(-1.0), -45.0, MINUS_S + "45" + DEG, -9, -6, TEXT, 11, "end")
B.label(arclen(1.5), 56.31, "56,3" + DEG, 2, 18, TEXT, 11)
B.label(1.0, 68.0, "eğim = " + ktilde(11), 0, 0, TEXT, 11)
B.label(0.45, -42.0, PHI_S + " hep artar,", 0, 0, TEXT, 11)
B.label(0.45, -58.0, "yani " + ktilde(11) + " &gt; 0.", 0, 0, TEXT, 11)

# the title is lifted clear of the phi axis arrowhead, which sits right under the panel's midline
B.text_px(495, 50, "Eğim açısının grafiği", TEXT, 11.5, "middle", True)
B.text_px(495, 26, ktilde(13.5) + " = " + PHI_S + PRIME, TEXT, 13.5, "middle")

OUT["frenet-duzlem-egriligi"] = figure(
    620, 280, [A, B],
    "Birim hızlı bir düzlem eğrisinde eğim açısı " + PHI_S + ", birim teğet <strong>T</strong>"
    "&#8217;nin <em>x</em> ekseniyle yaptığı açıdır. Solda <em>y</em> = <em>x</em><sup>2</sup>/2 "
    "parabolü üzerinde üç nokta alınmıştır: <em>x</em> = &#8722;1&#8217;de " + PHI_S + " = "
    "&#8722;45&#176;, <em>x</em> = 0&#8217;da " + PHI_S + " = 0&#176;, <em>x</em> = 1,5&#8217;te "
    + PHI_S + " &#8776; 56,3&#176;; her noktada mavi <strong>T</strong> oku eğriye teğettir, "
    "yeşil <strong>N</strong> oku ise <strong>T</strong>&#8217;nin 90&#176; sola döndürülmüşüdür, "
    "yani ona diktir. Sağdaki küçük panelde aynı açı yay uzunluğunun fonksiyonu olarak çizilmiştir: "
    + PHI_S + " durmadan arttığı için grafiğin her noktadaki eğimi pozitiftir. İşte bu eğim, yani "
    "eğim açısının yay uzunluğuna göre türevi, eğrinin düzlem eğriliğidir.",
    css_class=WIDE,
    aria="Solda y = x^2/2 parabolu turuncu cizilmis; x = -1, x = 0 ve x = 1,5 noktalarinda mavi "
         "birim teget ok T ve yesil birim normal ok N vardir, N her noktada T nin 90 derece sola "
         "dondurulmusudur. Her noktadan x eksenine paralel ince gri bir isin cikar; isin ile T "
         "arasindaki aci taranmis bir dilimle isaretlenmis ve sirasiyla -45 derece, 0 derece, "
         "56,3 derece yazilmistir. Sagdaki kucuk panelde yatay eksen yay uzunlugu s, dusey eksen "
         "egim acisidir; mavi egri artandir ve s = 0 noktasinda cizilen gri teget dogrunun egimi "
         "kappa tilde olarak etiketlenmistir",
)

# ============================================================ frenet-egrilik-vektoru
# -*- coding: utf-8 -*-
# frenet-egrilik-vektoru: the two unit-speed circles of the worked example, drawn in the xy plane.
#   beta1(s) = (sin s, 1 - cos s)            centre (0, 1), radius a = 1  (blue)
#   beta3(s) = (3 sin s/3, 3 - 3 cos s/3)    centre (0, 3), radius a = 3  (orange)
# Both pass through the origin with the same unit tangent T = (1, 0), so the x axis is their common
# tangent line there; the curvature vectors T1'(0) = (0, 1) and T3'(0) = (0, 1/3) stand perpendicular
# to it, on the y axis, each pointing at its own centre.
# Left panel: the whole picture — the two circles, the grey T arrow on the common tangent line.
# Right panel: a zoom on the first unit of arc length. The two curvature arrows live here, not on the
# left: at 135 px per unit the short one is 45 px long and both labels fit beside the y axis, whereas
# on the left panel every spot next to the 21 px orange arrow is crossed by the blue circle.
# The arrows are collinear, so the orange one is drawn over the blue: the shared shaft is orange up
# to 1/3 and blue above it, which is exactly the "one is three times the other" reading.
# At s = 1 the points are (0,841; 0,460) and (0,982; 0,165); the dashed drops measure their distance
# from the tangent line. Panel sizes are chosen so both come out 184.8 px tall.
import math

# ---------------------------------------------------------------- the two curves
def b1(s):
    return (math.sin(s), 1.0 - math.cos(s))


def b3(s):
    return (3.0 * math.sin(s / 3.0), 3.0 - 3.0 * math.cos(s / 3.0))


S1 = b1(1.0)                      # (0.84147, 0.45970)
S3 = b3(1.0)                      # (0.98159, 0.16512)
K1, K3 = 1.0, 1.0 / 3.0           # the two curvatures

p1 = cplane(16, 40, 240, (-1.35, 2.35), (-0.55, 2.30))    # 64.86 px per unit
p2 = cplane(316, 40, 210, (-0.22, 1.33), (-0.22, 1.144))  # 135.48 px per unit

KAPPA = "&#954;"
BETA = "&#946;"


def ital(s):
    return f'<tspan font-style="italic">{s}</tspan>'


def halo(p, px, py, s, color=TEXT, size=11.5, anchor="start"):
    """Text at a pixel position with a page-coloured halo, so a line behind it breaks."""
    p.add(f'<text x="{px:.1f}" y="{py:.1f}" fill="{color}" font-size="{size}" '
          f'text-anchor="{anchor}" stroke="{BG}" stroke-width="3.4" stroke-linejoin="round" '
          f'paint-order="stroke">{s}</text>')


def clip_runs(p, f, t0, t1, n=1800):
    """Maximal runs of the parametric curve f that stay inside the panel's data rectangle."""
    runs, cur = [], []
    for k in range(n + 1):
        x, y = f(t0 + (t1 - t0) * k / n)
        if p.xmin <= x <= p.xmax and p.ymin <= y <= p.ymax:
            cur.append((x, y))
        else:
            if len(cur) > 1:
                runs.append(cur)
            cur = []
    if len(cur) > 1:
        runs.append(cur)
    return runs


def draw_curve(p, f, t0, t1, color, width=2.2):
    for run in clip_runs(p, f, t0, t1):
        p.line(run, color, width)


# ================================================================ LEFT: the two circles
panel_title(p1, "İki çember, orijinde ortak teğet")

draw_curve(p1, b3, -2.2, 2.2, PRACTICE)
p1.circle(0, 1, 1.0, THEORY, 2.2)                    # the a = 1 circle fits whole
p1.origin_axes("x", "y", xticks=(1, 2), yticks=(2,))

p1.arrow((0, 0), (1, 0), TEXT, 2.6, head=8.5)        # the common unit tangent, on the tangent line
guide(p1, [(0, 1), (1, 1)], THEORY, 0.75, 1.2)       # a radius, drawn sideways so it misses the y axis
hollow(p1, (0, 1), THEORY, 3.2, 1.6)                 # centre of the small circle
dot(p1, (0, 0), TEXT, 3.4)

halo(p1, p1.X(0.5), p1.Y(1) - 6, ital("a") + " = 1", THEORY, 11, "middle")
halo(p1, p1.X(0) + 9, p1.Y(1) + 14, "(0, 1)", THEORY, 11, "start")
halo(p1, 30, 56, ital(BETA) + subs("1"), THEORY, 12.5, "start")
halo(p1, 239, 150, ital(BETA) + subs("3"), PRACTICE, 12.5, "middle")
halo(p1, 235, 164, ital("a") + " = 3", PRACTICE, 11, "middle")

p1.text_px(p1.X(0.55), p1.Y(0) + 15, ital("T"), TEXT, 12.5, "middle")
p1.text_px(p1.x0 + 3, p1.Y(0) + 15, "teğet doğrusu", TEXT, 10.5, "start")

# ================================================================ RIGHT: curvature vectors, s = 1
panel_title(p2, "Eğrilik vektörleri ve " + ital("s") + " = 1")

draw_curve(p2, b3, -1.0, 2.2, PRACTICE)
draw_curve(p2, b1, -1.0, 2.2, THEORY)
p2.origin_axes("x", "y", xticks=(0.5,), yticks=(0.5,), xfmt=tfmt, yfmt=tfmt)

# the two curvature vectors at the origin; they are collinear, so the short orange one is drawn
# last and covers the lower third of the blue shaft
p2.arrow((0, 0), (0, K1), THEORY, 2.6, head=9)
p2.arrow((0, 0), (0, K3), PRACTICE, 2.6, head=8.5)
p2.line([(0.08, 0), (0.08, 0.08), (0, 0.08)], TEXT, 1.1, None, 0.85)   # right angle with the tangent

guide(p2, [S1, (S1[0], 0.0)], THEORY, 0.85, 1.2)
guide(p2, [S3, (S3[0], 0.0)], PRACTICE, 0.85, 1.2)
dot(p2, S1, THEORY, 3.6)
dot(p2, S3, PRACTICE, 3.6)
dot(p2, (0, 0), TEXT, 3.2)

halo(p2, p2.X(0) + 9, p2.Y(K1) + 4, KAPPA + subs("1") + " = 1", THEORY, 12, "start")
halo(p2, p2.X(0) + 9, p2.Y(K3) + 4, KAPPA + subs("3") + " = 1/3", PRACTICE, 12, "start")
halo(p2, p2.X(S1[0]) + 6, p2.Y(S1[1]) + 4, "0,460", THEORY, 11.5, "start")
halo(p2, p2.X(S3[0]) + 6, p2.Y(S3[1] / 2) + 4, "0,165", PRACTICE, 11.5, "start")
halo(p2, 466, 105, ital(BETA) + subs("1"), THEORY, 12, "end")
# beta3 sits in the free wedge above its own curve: right of it the curve leaves the panel, below it
# the "0,165" label already fills the strip between the curve and the axis
halo(p2, 515, 145, ital(BETA) + subs("3"), PRACTICE, 12, "middle")

# the three notes under the axis: which s the origin is, what the x axis is, and the axis name
p2.text_px(p2.X(0) - 8, p2.Y(0) + 15, ital("s") + " = 0", TEXT, 11, "end")
p2.text_px(505, p2.Y(0) + 15, "teğet doğrusu", TEXT, 10.5, "end")

OUT["frenet-egrilik-vektoru"] = figure(
    560, 240, [p1, p2],
    "Solda orijinden geçen ve orada aynı birim teğet vektöre sahip iki çember: yarıçapı "
    "<em>a</em> = 1 olan &#946;<sub>1</sub> (mavi) ile yarıçapı <em>a</em> = 3 olan "
    "&#946;<sub>3</sub> (turuncu); gri ok ikisinin ortak teğeti <em>T</em>(0) = (1, 0)&#8217;dır ve "
    "<em>x</em> ekseni ortak teğet doğrusudur. Sağdaki yakın planda aynı noktadan dikey çıkan iki "
    "eğrilik vektörü görülüyor: mavi okun boyu &#954;<sub>1</sub> = 1, turuncu okunki "
    "&#954;<sub>3</sub> = 1/3&#8217;tür; ikisi de teğet doğrusuna diktir ve kendi çemberinin "
    "merkezine bakar. <em>s</em> = 1 anında eğriler teğet doğrusundan 0,460 ile 0,165 kadar "
    "uzaklaşmıştır: oranları yaklaşık 2,78&#8217;dir, yani eğriliği büyük olan eğri teğet "
    "doğrusundan üç katına yakın hızla ayrılır.",
    css_class=WIDE,
    aria="Iki panel. Solda xy duzleminde orijinden gecen iki cember: merkezi (0, 1) ve yaricapi 1 "
         "olan mavi beta1 ile merkezi (0, 3) ve yaricapi 3 olan turuncu beta3; orijindeki ortak "
         "teget dogrusu x eksenidir ve uzerinde gri T oku (1, 0) durur. Sagda yakin plan: "
         "orijinden yukari cikan mavi ok (0, 1) uzunlugu 1 ve kappa1 = 1, turuncu ok (0, 1/3) "
         "uzunlugu 1/3 ve kappa3 = 1/3; kucuk kare isareti bu oklarin teget dogrusuna dik "
         "oldugunu gosterir. s = 1 icin mavi nokta (0,841; 0,460), turuncu nokta (0,982; 0,165); "
         "her birinden x eksenine kesikli dik iniyor, uzunluklari 0,460 ve 0,165.")

# ============================================================ frenet-helis-cati
# -*- coding: utf-8 -*-
# frenet-helis-cati: the helix beta(s) = (3cos(s/5), 3sin(s/5), 4s/5) on the cylinder
# x^2 + y^2 = 9 with its Frenet frame at s = 5pi/2, where beta = (0, 3, 2pi),
# T = (-3/5, 0, 4/5), N = (0, -1, 0), B = (4/5, 0, 3/5), kappa = 3/25 and tau = 4/25.
#
# Drawn arc.  One full turn of this helix rises 2*pi*b = 8pi = 25.1 units over a tube of
# radius 3, an 8 : 1 box that leaves the frame a few pixels wide on any readable page.  The
# figure therefore shows the half turn s in [0, 5pi] (z from 0 to 4pi), which is exactly the
# piece centred on the marked point: u = s/5 runs 0 to pi and the frame sits at u = pi/2, in
# the middle of both the sweep and the rise.  The two end labels s = 0 and s = 5pi say so.
#
# Colours follow the book's Frenet convention (keyfi-kubik-aparat, keyfi-kubik-cati-t2):
# curve blue, T orange, N green, B dark, osculating patch hatched in the tangent's colour.
#
# Camera.  The two readings the figure has to carry pull against each other, because
# B = (4/5, 0, 3/5) lies in the xz plane and N = (0, -1, 0) along -y:
#   * seen from a large azimuth B opens out nicely but N turns into the screen, and the whole
#     point that N aims straight at the cylinder axis is lost to foreshortening;
#   * seen from a small azimuth N lies across the page and points at the axis at almost full
#     length, but B leans toward the viewer and comes out short.
# _probe_frenet_helis.py scans both angles; the widest spread of the three page directions in
# the whole band is at az about 27-30 with a low elevation.  At az = 28, el = 12 the page
# angles are T 73, B 130, N 174 degrees (T-N 101, N-B 44, T-B 57), the projected lengths are
# 0.94, 0.89, 0.58 and the osculating plane still keeps 0.82 of its area.
#
# Because B projects into the sector between T and N, the 2 x 2 osculating patch is hung on
# the T and -N edges, away from B: a patch on the +N side would have the B arrow lying inside
# it and would say the opposite of what the figure teaches.  The curve bends toward +N, so it
# leaves the patch clear as well and only hugs the T arrow, which is what tangency looks like.
import math

AZ, EL = 28.0, 12.0
PPU = 30.0                               # pixels per space unit
A, B_, C = 3.0, 4.0, 5.0                 # a = 3, b = 4, c = 5
S0, S1 = 0.0, 5 * math.pi                # the drawn arc: half a turn
SP = 5 * math.pi / 2                     # the marked point
Z0, Z1 = -1.0, 13.2                      # the drawn piece of the cylinder
ZAX = 14.0                               # top of the z axis
LEN = 2.0                                # the unit vectors are drawn twice as long
PHI = math.radians(AZ)                   # cos(u - PHI) > 0 on the half of the tube facing us
NEAR = (PHI - math.pi / 2, PHI + math.pi / 2)
FAR = (PHI + math.pi / 2, PHI + 3 * math.pi / 2)

PT = (0.0, 3.0, 2 * math.pi)             # beta(5pi/2)
TV = (-0.6, 0.0, 0.8)
NV = (0.0, -1.0, 0.0)
BV = (0.8, 0.0, 0.6)
AXIS_PT = (0.0, 0.0, 2 * math.pi)        # where N points: the axis at the same height

SQ = "&#8730;"
KAPPA, TAU, BETA = "&#954;", "&#964;", "&#946;"


def beta(s):
    u = s / C
    return (A * math.cos(u), A * math.sin(u), B_ * s / C)


def velocity(s):
    """beta'(s) — already a unit vector."""
    u = s / C
    return (-(A / C) * math.sin(u), (A / C) * math.cos(u), B_ / C)


def accel(s):
    """beta''(s) = T'(s); its length is the curvature."""
    u = s / C
    return (-(A / C / C) * math.cos(u), -(A / C / C) * math.sin(u), 0.0)


def tube(u, z):
    return (A * math.cos(u), A * math.sin(u), z)


def is_near(u):
    return math.cos(u - PHI) > 0


# ---------------------------------------------------------------- self-checks on the numbers
assert abs(beta(SP)[0]) < 1e-12 and abs(beta(SP)[1] - 3.0) < 1e-12
assert abs(beta(SP)[2] - 2 * math.pi) < 1e-12                     # beta(5pi/2) = (0, 3, 2pi)
assert vnorm(vsub(velocity(SP), TV)) < 1e-12                      # T = (-3/5, 0, 4/5)
assert abs(vnorm(accel(SP)) - 3.0 / 25.0) < 1e-12                 # kappa = 3/25
assert vnorm(vsub(vscale(25.0 / 3.0, accel(SP)), NV)) < 1e-12     # N = T'/kappa = (0, -1, 0)
assert vnorm(vsub(vcross(TV, NV), BV)) < 1e-12                    # B = T x N = (4/5, 0, 3/5)
for _v in (TV, NV, BV):
    assert abs(vnorm(_v) - 1.0) < 1e-12
assert abs(vdot(TV, NV)) + abs(vdot(TV, BV)) + abs(vdot(NV, BV)) < 1e-12
# B'(s) = (b/c^2)(cos u, sin u, 0) = -tau N with tau = 4/25
_h = 1e-6
_Bp = vscale(1 / (2 * _h), vsub(vcross(velocity(SP + _h), vscale(25.0 / 3.0, accel(SP + _h))),
                                vcross(velocity(SP - _h), vscale(25.0 / 3.0, accel(SP - _h)))))
assert vnorm(vsub(_Bp, vscale(-4.0 / 25.0, NV))) < 1e-6           # tau = 4/25
# N really points at the cylinder axis
assert vnorm(vsub(vadd(PT, vscale(3.0, NV)), AXIS_PT)) < 1e-12

P = space_panel(18, 14, PPU * 9.5, (-4.1, 5.4), (-3.9, 14.1))
S = Space(P, Camera(azimuth=AZ, elevation=EL, scale=1.0))

# ---------------------------------------------------------------- page-space report
_dirs = {}
for _k, _v in (("T", TV), ("N", NV), ("B", BV)):
    _X, _Y = S.pt(_v)
    _dirs[_k] = (math.degrees(math.atan2(_Y, _X)) % 360.0, math.hypot(_X, _Y))
    print("%s: page angle %6.1f deg, projected length %.2f" % (_k, _dirs[_k][0], _dirs[_k][1]))
_c0, _c1 = S.pt(beta(SP - 0.02)), S.pt(beta(SP + 0.02))
_tan = math.degrees(math.atan2(_c1[1] - _c0[1], _c1[0] - _c0[0])) % 360.0
print("curve tangent on the page: %.1f deg (T reads %.1f) — difference %.2f"
      % (_tan, _dirs["T"][0], abs(_tan - _dirs["T"][0])))
print("T to N on the page: %.1f deg (90 in space)"
      % abs(_dirs["T"][0] - _dirs["N"][0]))
_pp, _ap = S.pt(PT), S.pt(AXIS_PT)
print("N on the page points at %.1f deg, the axis point lies at %.1f deg from beta(5pi/2)"
      % (_dirs["N"][0], math.degrees(math.atan2(_ap[1] - _pp[1], _ap[0] - _pp[0])) % 360.0))


def halo(px_, py_, s, color=TEXT, size=11.5, anchor="start", pad=3.8):
    """Text with a page-coloured outline behind it, drawn as two <text> runs: rsvg drops the
    ascender of an italic letter that a raised tspan follows when one run is stroked.

    `pad` widens the outline where a wall ruling would otherwise show through the gap between
    two glyphs and read as a stray tick."""
    common = f'x="{px_:.1f}" y="{py_:.1f}" font-size="{size}" text-anchor="{anchor}"'
    P.add(f'<text {common} fill="none" stroke="{BG}" stroke-width="{pad}" '
          f'stroke-linejoin="round">{s}</text>')
    P.add(f'<text {common} fill="{color}">{s}</text>')


def at(X, Y, s, color=TEXT, size=11.5, anchor="start", pad=3.8):
    """Halo text at a point of the panel's data plane (that is, of the projected page)."""
    halo(P.X(X), P.Y(Y), s, color, size, anchor, pad)


def tag(Q, s, dx=0, dy=0, color=TEXT, size=11.5, anchor="start", pad=3.8):
    """Halo text hung on a space point."""
    X, Y = S.pt(Q)
    halo(P.X(X) + dx, P.Y(Y) + dy, s, color, size, anchor, pad)


def hatch(poly, angle_deg, color=TEXT, step_px=7.5, width=0.8, opacity=0.38):
    """Parallel hatch lines at angle_deg (page), clipped to a convex polygon in data units."""
    a = math.radians(angle_deg)
    d = (math.cos(a), math.sin(a))
    nrm = (-d[1], d[0])
    step = step_px * (P.xmax - P.xmin) / P.w
    proj = [nrm[0] * x + nrm[1] * y for x, y in poly]
    lo, hi = min(proj), max(proj)
    count = max(1, int((hi - lo) / step))
    c0 = lo + (hi - lo - (count - 1) * step) / 2.0
    parts = []
    for i in range(count):
        c = c0 + i * step
        hits = []
        for j in range(len(poly)):
            (x0, y0), (x1, y1) = poly[j], poly[(j + 1) % len(poly)]
            s0 = nrm[0] * x0 + nrm[1] * y0 - c
            s1 = nrm[0] * x1 + nrm[1] * y1 - c
            if (s0 < 0) != (s1 < 0):
                t = s0 / (s0 - s1)
                hits.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t))
        if len(hits) >= 2:
            hits.sort(key=lambda q: d[0] * q[0] + d[1] * q[1])
            parts.append(f"M{P.P(*hits[0])} L{P.P(*hits[-1])}")
    P.add(f'<path d="{" ".join(parts)}" fill="none" stroke="{color}" stroke-width="{width}" '
          f'opacity="{opacity}" stroke-linecap="butt"/>')


def rim(z, u0, u1, dash=None, opacity=0.45, n=64):
    S.line([tube(u0 + (u1 - u0) * k / n, z) for k in range(n + 1)], TEXT, 0.9, dash, opacity)


def runs(front, n=900):
    """Maximal pieces of the drawn arc on the near (front=True) or far half of the tube."""
    ss = [S0 + (S1 - S0) * k / n for k in range(n + 1)]
    out, cur = [], []
    for i, s in enumerate(ss):
        if is_near(s / C) == front:
            if not cur and i > 0:
                cur.append(beta(ss[i - 1]))
            cur.append(beta(s))
        elif cur:
            cur.append(beta(s))
            out.append(cur)
            cur = []
    if cur:
        out.append(cur)
    return out


def wall(urange):
    """Half of the tube, with its grid.  nu = 7 puts no ruling at u = PHI, which would project
    onto the z axis itself; nv = 3 keeps the horizontal circle at z = 8.47 well clear of the
    frame at z = 2pi = 6.28, and four circles read as a tube where eight read as a cage."""
    S.surface(tube, urange, (Z0, Z1), nu=7, nv=3, fill=TEXT, stroke=TEXT,
              opacity=(0.012, 0.05), stroke_width=0.6, stroke_opacity=0.13)


# ---------------------------------------------------------------- 1. far half of the tube
wall(FAR)
rim(Z0, *FAR, dash="3 3", opacity=0.30)
rim(Z1, *FAR, opacity=0.40)

# ---------------------------------------------------------------- 2. what the near wall hides
S.line([(0, 0, 0), (A, 0, 0)], TEXT, 1.1, None, 0.40)          # x axis inside the tube
S.line([(0, 0, 0), (0, A, 0)], TEXT, 1.1, None, 0.40)          # y axis inside the tube
S.line([(0, 0, Z0), (0, 0, 13.4)], TEXT, 1.1, "5 4", 0.55)     # the z axis, hidden in the tube
for run in runs(False):
    S.line(run, THEORY, 2.0, None, 0.42)

# ---------------------------------------------------------------- 3. near half of the tube
wall(NEAR)
rim(Z0, *NEAR, opacity=0.50)
rim(Z1, *NEAR, opacity=0.50)
for u in NEAR:
    S.line([tube(u, Z0), tube(u, Z1)], TEXT, 0.9, None, 0.40)

# ---------------------------------------------------------------- 4. the helix in front
for run in runs(True):
    S.line(run, THEORY, 2.6)
S.arrow(beta(2.45), beta(2.95), THEORY, 2.6, 9.5)              # direction of travel
S.point(beta(S0), TEXT, 3.0)

# ---------------------------------------------------------------- 5. axes outside the tube
S.arrow((A, 0, 0), (4.3, 0, 0), TEXT, 1.1, 7, None, 0.55)
S.arrow((0, A, 0), (0, 4.3, 0), TEXT, 1.1, 7, None, 0.55)
S.arrow((0, 0, 13.4), (0, 0, ZAX), TEXT, 1.1, 7, None, 0.55)
S.ticks("y", (3,), offset=(13, 11))       # no x tick: the curve starts at that very point

# ---------------------------------------------------------------- 6. the osculating patch
CORNER = vadd(PT, vsub(vscale(LEN, TV), vscale(LEN, NV)))
PATCH = [PT, vadd(PT, vscale(LEN, TV)), CORNER, vsub(PT, vscale(LEN, NV))]
POLY = S.pts(PATCH)
P.polygon(POLY, PRACTICE, 0.08, "none")   # 0.10 came out as a solid brown block on dark
hatch(POLY, 33.0, PRACTICE)                                    # midway between the two edges,
#                                       which run at 72.5 and -6.3 degrees on the page
S.guide([PATCH[1], CORNER, PATCH[3], PT], PRACTICE, 0.55, 1.1)  # every edge but the T arrow

# ---------------------------------------------------------------- 7. the frame at s = 5pi/2
S.drop(PT)                                                     # down to (0, 3, 0) on the y axis
S.guide([PT, AXIS_PT], TEXT, 0.55, 1.1)                        # N aims here: (0, 0, 2pi)
for _v in (TV, NV, BV):                                        # halos: three shafts, one origin
    S.line([PT, vadd(PT, vscale(LEN, _v))], BG, 5.6)
S.arrow(PT, vadd(PT, vscale(LEN, TV)), PRACTICE, 2.5, head=9)
S.arrow(PT, vadd(PT, vscale(LEN, NV)), BASE, 2.5, head=9)
S.arrow(PT, vadd(PT, vscale(LEN, BV)), TEXT, 2.5, head=9)
S.point(PT, TEXT, 3.8)
S.point(AXIS_PT, TEXT, 2.6)

# ---------------------------------------------------------------- 8. labels
IT_S = '<tspan font-style="italic">s</tspan>'
IT_B = f'<tspan font-style="italic">{BETA}</tspan>'

tag((4.3, 0, 0), '<tspan font-style="italic">x</tspan>', -7, 14, TEXT, 11.5, "middle")
tag((0, 4.3, 0), '<tspan font-style="italic">y</tspan>', 9, 6, TEXT, 11.5, "start")
tag((0, 0, ZAX), '<tspan font-style="italic">z</tspan>', -10, -3, TEXT, 11.5, "end")
tag(AXIS_PT, "2" + PI_S, -9, 4, TEXT, 10, "end", pad=5.4)   # a ruling runs between 2 and pi

tag(vadd(PT, vscale(LEN, TV)), bold("T"), 6, -8, PRACTICE, 12.5, "start")   # above the patch,
#                                            whose top edge leaves the arrow tip to the right
tag(vadd(PT, vscale(LEN, NV)), bold("N"), -2, -10, BASE, 12.5, "middle")
tag(vadd(PT, vscale(LEN, BV)), bold("B"), -9, -3, TEXT, 12.5, "end")

at(0.75, 6.95, IT_B + "(5" + PI_S + "/2) = (0, 3, 2" + PI_S + ")", TEXT, 11.5, "end")
tag(beta(S0), IT_S + " = 0", 6, 15, TEXT, 11, "start")
tag(beta(S1), IT_S + " = 5" + PI_S, 9, 3, TEXT, 11, "start")

# the legend goes in the empty upper left of the tube, above the curve; its last line clears
# the horizontal circle at z = 8.47, whose far branch runs at 8.90 on the page
at(-2.9, 10.3, bold("T") + " = (" + MINUS_S + "3/5, 0, 4/5)", PRACTICE, 11.5)
at(-2.9, 9.65, bold("N") + " = (0, " + MINUS_S + "1, 0)", BASE, 11.5)
at(-2.9, 9.0, bold("B") + " = (4/5, 0, 3/5)", TEXT, 11.5)

at(0.6, -2.0, '<tspan font-style="italic">x</tspan>' + sups("2") + " + "
   + '<tspan font-style="italic">y</tspan>' + sups("2") + " = 9", TEXT, 11.5)
at(0.35, -2.8, IT_B + "(" + IT_S + ") = (3 cos(" + IT_S + "/5), 3 sin(" + IT_S + "/5), 4"
   + IT_S + "/5)", THEORY, 11.5, "middle")
at(0.35, -3.55, KAPPA + " = 3/25,    " + TAU + " = 4/25", TEXT, 11.5, "middle")

OUT["frenet-helis-cati"] = figure(
    round(18 + P.w + 18), round(14 + P.h + 14), [P],
    "Helis <em>&#946;</em>(<em>s</em>) = (3cos(<em>s</em>/5), 3sin(<em>s</em>/5), "
    "4<em>s</em>/5) <em>x</em><sup>2</sup> + <em>y</em><sup>2</sup> = 9 silindirinin duvarında "
    "yükselir; çizilen yay yarım turdur, <em>s</em> = 0&#8217;dan <em>s</em> = 5&#960;&#8217;ye. "
    "Ortadaki <em>&#946;</em>(5&#960;/2) = (0, 3, 2&#960;) noktasında turuncu <strong>T</strong> "
    "eğriye teğettir, yeşil <strong>N</strong> ona diktir ve kesikli çizginin gösterdiği gibi "
    "silindirin ekseni üzerindeki (0, 0, 2&#960;) noktasına dosdoğru bakar, koyu "
    "<strong>B</strong> = <strong>T</strong> &#215; <strong>N</strong> ise ilk ikisinin gerdiği "
    "taralı oskülatör düzleme diktir ve okura doğru çıkar. Üçü de birim uzunluktadır; "
    "görünürlük için iki kat uzun çizilmişlerdir, sayfada farklı boyda görünmeleri izdüşümün "
    "kısaltmasındandır. Bu heliste eğrilik ile burulma her noktada sabittir: "
    "&#954; = 3/25, &#964; = 4/25.",
    aria="x^2 + y^2 = 9 silindirinin duvarinda yukselen beta(s) = (3cos(s/5), 3sin(s/5), 4s/5) "
         "helisinin s = 0 ile s = 5pi arasindaki yarim turu; beta(5pi/2) = (0, 3, 2pi) "
         "noktasinda turuncu T = (-3/5, 0, 4/5) egriye teget, yesil N = (0, -1, 0) silindir "
         "ekseni uzerindeki (0, 0, 2pi) noktasina dogru, koyu B = (4/5, 0, 3/5) ise T ve N nin "
         "gerdigi taranmis oskulator duzleme diktir; kappa = 3/25 ve tau = 4/25",
)

# ============================================================ frenet-oskulator-cember
# -*- coding: utf-8 -*-
# frenet-oskulator-cember: the osculating circle of the exercise, drawn in the osculating plane
# with kappa_0 = 1. The second-order picture of beta is the parabola y = x^2/2 (orange, thick,
# -2 <= x <= 2); its curvature at the origin is y''/(1+y'^2)^(3/2) = 1 = kappa_0, so
#   T_0 = (1, 0)  (horizontal: y'(0) = 0, tangent to the parabola at its vertex),
#   N_0 = (0, 1)  (T_0 . N_0 = 0, pointing to the concave side),
#   c   = beta(0) + (1/kappa_0) N_0 = (0, 1),   r = 1/kappa_0 = 1.
# So the green N_0 arrow IS the radius drawn from beta(0) to c: its tip lands exactly on the
# centre. A separate dashed segment from c to the origin would be drawn on top of that arrow, so
# the segment is the arrow and both readings are labelled on its two sides: N_0 = (0, 1) on the
# left, r = 1/kappa_0 = 1 on the right.
# The circle (thin blue) lies inside the cup: at x = 0.5 it is at y = 0.134 while the parabola is
# at 0.125. At height y = 0,5 the parabola is at (1; 0,5) and the circle at (0,866; 0,5) — the
# two dots are 9.5 px apart, which is the "small difference" the box talks about.
# Axes are L-shaped at the panel edges on purpose: the centre of the panel is the only place wide
# enough for "egrilik merkezi", and an axis through the origin would run straight through it.
# The line y = 0 is redrawn faintly across the panel because it is the common tangent line at
# beta(0), and the T_0 arrow lies along it.

XR, YR = (-2.35, 2.35), (-0.5, 2.45)
p = cplane(46, 26, 334, XR, YR)          # 71.06 px per unit, equal scale

KAPPA, BETA, GAMMA = "&#954;", "&#946;", "&#947;"


def ital(s):
    return f'<tspan font-style="italic">{s}</tspan>'


def nfmt(v):
    return fmt(v).replace("-", MINUS_S)


def par(x):
    return x * x / 2.0


K0 = ital(KAPPA) + subs("0")
T0, N0 = bold("T") + subs("0"), bold("N") + subs("0")
C = (0.0, 1.0)                            # centre of curvature
Q = (0.866, 0.5)                          # circle point at height y = 0,5
R = (1.0, 0.5)                            # parabola point at height y = 0,5

# --- 1. frame: L-shaped axes, then the tangent line y = 0 -------------------------------------
p.axes((-2, -1, 0, 1, 2), (0, 1, 2), "x", "y", xfmt=nfmt, yfmt=nfmt)
p.line([(XR[0], 0.0), (XR[1], 0.0)], TEXT, 1.0, None, 0.22)

# --- 2. the osculating circle (thin blue) and the parabola (thick orange) ----------------------
p.circle(C[0], C[1], 1.0, THEORY, 1.6)
curve(p, par, -2.0, 2.0, PRACTICE, 2.6, 240)

# --- 3. the comparison at height y = 0,5 ------------------------------------------------------
guide(p, [(0.72, 0.5), (1.12, 0.5)], TEXT, 0.55)      # the common height
guide(p, [(1.0, 0.1), (1.0, 0.5)], TEXT, 0.55)        # x = 1, up from the tip of T_0

# --- 4. the Frenet arrows at beta(0) ----------------------------------------------------------
p.arrow((0.0, 0.0), (1.0, 0.0), THEORY, 2.6, 9)       # T_0 = (1, 0), along the parabola's tangent
p.arrow((0.0, 0.0), (0.0, 1.0), BASE, 2.6, 9)         # N_0 = (0, 1), perpendicular to T_0

# --- 5. points --------------------------------------------------------------------------------
dot(p, Q, THEORY, 3.4)
dot(p, R, PRACTICE, 3.4)
dot(p, (0.0, 0.0), TEXT, 3.8)
dot(p, C, TEXT, 4.6)

# --- 6. labels --------------------------------------------------------------------------------
# the circle, named above its highest point; the centre block inside it, centred on x = 0 where
# nothing else runs
p.label(0, 2, ital(GAMMA) + ": oskülatör çember", 0, -11, THEORY, 11, "middle")
p.label(0, 1, "eğrilik merkezi", 0, -29, TEXT, 10.5, "middle")
p.label(0, 1, bold("c") + " = (0, 1)", 0, -12, TEXT, 11.5, "middle")

# the two readings of the same segment: the unit normal on its left, the radius on its right
p.label(0, 0.62, N0 + " = (0, 1)", -8, 4, BASE, 11, "end")
p.label(0, 0.80, ital("r") + " = 1/" + K0 + " = 1", 9, 4, TEXT, 10.5, "start")

# the point and the tangent, below the line y = 0
p.label(0, 0, ital(BETA) + "(0) = (0, 0)", -8, 16, TEXT, 11, "end")
p.label(0.53, 0, T0 + " = (1, 0)", 0, 16, THEORY, 11, "middle")

# the parabola, named outside the cup under its left arm
p.label(-1.21, par(-1.21), ital(BETA) + ": " + ital("y") + " = " + ital("x") + sups("2") + "/2",
        0, 24, PRACTICE, 11, "end")
p.label(-1.21, par(-1.21), K0 + " = 1", 0, 41, TEXT, 11, "end")

# the two points of the comparison, outside the cup under the right arm
p.label(1.22, par(1.22), ital(BETA) + ": (1; 0,5)", 12, 26, PRACTICE, 11, "start")
p.label(1.22, par(1.22), ital(GAMMA) + ": (0,866; 0,5)", 12, 44, THEORY, 11, "start")

OUT["frenet-oskulator-cember"] = figure(
    400, 262, [p],
    "&#954;<sub>0</sub> = 1 alındığında &#946;&#8217;nın oskülatör düzlemdeki ikinci mertebeden "
    "görüntüsü <em>y</em> = <em>x</em><sup>2</sup>/2 parabolü (turuncu), oskülatör çemberi &#947; "
    "ise (0, 1) merkezli ve <em>r</em> = 1/&#954;<sub>0</sub> = 1 yarıçaplı çemberdir (mavi). "
    "Eğrilik merkezi <strong>c</strong>, &#946;(0) noktasından <strong>N</strong><sub>0</sub> "
    "yönünde 1/&#954;<sub>0</sub> kadar ilerleyerek bulunur: yeşil ok tam <strong>c</strong>&#8217;de "
    "biter, yani bu ok aynı zamanda yarıçaptır. Çember orijinde parabole içten teğettir; iki "
    "eğrinin ortak teğet yönü <strong>T</strong><sub>0</sub> = (1, 0), ona dik olan normal yön ise "
    "<strong>N</strong><sub>0</sub> = (0, 1)&#8217;dir. İkisi orijin yakınında öyle yakındır ki "
    "<em>y</em> = 0,5 yüksekliğinde parabol (1; 0,5) noktasındayken çember (0,866; 0,5) "
    "noktasındadır.",
    aria="xy duzleminde kalin turuncu y = x^2/2 parabolu, x = -2 ile 2 arasinda, ve orijinde ona "
         "icten teget, merkezi c = (0, 1) ve yaricapi r = 1 olan ince mavi oskulator cember. "
         "Orijindeki beta(0) = (0, 0) noktasinda yatay mavi T0 = (1, 0) oku ve dusey yesil "
         "N0 = (0, 1) oku; yesil okun ucu tam c noktasinda biter ve yaricapi gosterir. "
         "y = 0,5 yuksekliginde parabolun noktasi (1; 0,5) turuncu, cemberin noktasi "
         "(0,866; 0,5) mavi isaretli; aradaki kucuk fark gorunur.",
)

# ============================================================ frenet-uc-duzlem
# -*- coding: utf-8 -*-
# frenet-uc-duzlem: the Frenet frame at a single point beta(0) and the three planes it fixes.
#
# The picture is intrinsic — there is no x, y, z to show — so the frame itself is used as the
# world basis: T0 = (1,0,0), N0 = (0,1,0), B0 = T0 x N0 = (0,0,1). That keeps the drawn frame
# right-handed, which the chapter's B = T x N demands. (The draft sketch asked for T0 to the
# right, N0 toward the viewer and B0 up; with B = T x N that triple is left-handed — right of B
# up is B x T = "away from the viewer" — so T0 and N0 swap their page directions here.)
#
# Camera. The three squares are mutually perpendicular, so their foreshortenings |n . d| obey
# f_osc^2 + f_rect^2 + f_norm^2 = 1: no view opens all three. az = 45 makes the picture
# left-right symmetric (T0 down-left, N0 down-right, B0 straight up, 114-123 degrees apart on
# the page); el = 40 is above the API's 15-30 band on purpose, because f_osc = sin(el) and below
# ~32 degrees the osculating square is squashed onto its own long diagonal and the unit arrows
# T0, N0 come within a few pixels of its rim. At (45, 40) the three squares open to 0.64, 0.54
# and 0.54 of their true area.
#
# The approximation beta(s) - beta(0) = s T0 + (s^2/2) N0 + (s^3/6) B0 (kappa0 = tau0 = 1, the
# box's simplest case) is drawn on -1.5 <= s <= 1.5, after the patches and before the arrows, so
# the T0 arrow covers the piece of curve that runs along it: the curve then visibly leaves the
# arrow, which is what "tangent" means here.
import math

AZ, EL = 45.0, 40.0
SCALE = 1.2
HALF = 1.2                 # half side: every patch is a 2.4 x 2.4 square centred at beta(0)
SMIN, SMAX = -1.5, 1.5     # the s range the box names

O = (0.0, 0.0, 0.0)        # beta(0)
T0 = (1.0, 0.0, 0.0)
N0 = (0.0, 1.0, 0.0)
B0 = vcross(T0, N0)        # (0, 0, 1) — B is T x N by definition, never the other way round

BETA_S, KAPPA_S, TAU_S = "&#946;", "&#954;", "&#964;"
APPROX_S, RSQUO = "&#8776;", "&#8217;"
TT = bold("T") + subs("0")
NN = bold("N") + subs("0")
BB = bold("B") + subs("0")


def beta(s):
    """Frenet approximation with kappa0 = tau0 = 1, measured from beta(0) at the origin."""
    return vadd(vscale(s, T0), vadd(vscale(0.5 * s * s, N0), vscale(s ** 3 / 6.0, B0)))


P = space_panel(16, 14, 432, (-3.75, 2.95), (-2.55, 2.05))
S = Space(P, Camera(azimuth=AZ, elevation=EL, scale=SCALE))


def it(s):
    return f'<tspan font-style="italic">{s}</tspan>'


def halo(px_, py_, s, color=TEXT, size=11.5, anchor="start"):
    """Text with a page-coloured halo underneath, so a faint rim behind it breaks.

    Two elements rather than paint-order="stroke": with one element the halo of a subscript
    eats the letter in front of it."""
    common = f'x="{px_:.1f}" y="{py_:.1f}" font-size="{size}" text-anchor="{anchor}"'
    P.add(f'<text {common} fill="none" stroke="{BG}" stroke-width="3.6" '
          f'stroke-linejoin="round">{s}</text>')
    P.add(f'<text {common} fill="{color}">{s}</text>')


def tag(Q, s, dx=0, dy=0, color=TEXT, size=11.5, anchor="start"):
    """Haloed text hung on a space point."""
    X, Y = S.pt(Q)
    halo(P.X(X) + dx, P.Y(Y) + dy, s, color, size, anchor)


def plane_tag(Q, name, perp, dx=0, dy=0, color=TEXT, anchor="start"):
    """Two-line patch label: the name, and under it the vector the patch is perpendicular to."""
    X, Y = S.pt(Q)
    halo(P.X(X) + dx, P.Y(Y) + dy, name, color, 12, anchor)
    halo(P.X(X) + dx, P.Y(Y) + dy + 14.5, perp + RSQUO + "a dik", color, 10.5, anchor)


def patch(e1, e2, color, fill_op=0.065):
    """A 2.4 x 2.4 square of the plane spanned by e1, e2, centred at beta(0)."""
    corners = [vadd(vscale(a * HALF, e1), vscale(b * HALF, e2))
               for a, b in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    S.polygon(corners, color, fill_op, "none")
    return corners


def rim(corners, color):
    S.polygon(corners, "none", 0.0, color, 1.1, "5 3")


def right_angle(a, b, size, color=TEXT, width=1.25, opacity=0.85):
    """The two outer edges of a small square in the plane of the unit vectors a, b, at beta(0).
    In one grey and one size the three marks closed up into a hexagon — a little cube corner
    sitting on the point. Each therefore takes the colour of the patch whose plane it lies in and
    its own size, and the three read as three separate right angles."""
    ea, eb = vscale(size, a), vscale(size, b)
    S.line([ea, vadd(ea, eb), eb], color, width, None, opacity)


# ---------------------------------------------------------------- 1. the three plane patches
OSC = patch(T0, N0, PRACTICE, 0.07)    # spanned by T0 and N0, perpendicular to B0
RECT = patch(T0, B0, BASE, 0.045)      # spanned by T0 and B0, perpendicular to N0
NORM = patch(N0, B0, THEORY, 0.045)    # spanned by N0 and B0, perpendicular to T0

# where the patches cut one another: the half-lines opposite the three arrows. They start well
# outside the right-angle marks, or they turn the middle of the picture into a cube corner.
for e in (T0, N0, B0):
    S.line([vscale(-0.45, e), vscale(-HALF, e)], TEXT, 1.0, "3 3", 0.30)

rim(OSC, PRACTICE)
rim(RECT, BASE)
rim(NORM, THEORY)

# ---------------------------------------------------------------- 2. the three right angles
# The curve is tangent to the T0 line, so on the page its s > 0 branch runs inside the (T0, N0)
# wedge and its s < 0 branch inside the (N0, B0) wedge — no size keeps those two marks clear of
# it. They are kept small and drawn first, so the curve passes over them close to the point,
# where the arrows and the dot carry the eye anyway.
right_angle(T0, N0, 0.28, PRACTICE)    # the corner inside the osculating square
right_angle(N0, B0, 0.25, THEORY)      # inside the normal square
right_angle(B0, T0, 0.30, BASE)        # inside the rectifying square, the wedge the curve misses

# ---------------------------------------------------------------- 3. the Frenet approximation
S.curve(beta, SMIN, SMAX, PRACTICE, 2.0, 260)
S.point(beta(SMIN), PRACTICE, 2.6)
S.point(beta(SMAX), PRACTICE, 2.6)

S.arrow(O, T0, THEORY, 2.5, 9.5)
S.arrow(O, N0, BASE, 2.5, 9.5)
S.arrow(O, B0, TEXT, 2.5, 9.5)
S.point(O, TEXT, 3.8)

# ---------------------------------------------------------------- 4. labels
tag(O, it(BETA_S) + "(0)", -34, -8, TEXT, 12, "end")

# the frame names sit beside the middle of their own arrow, pushed off it sideways
tag(vscale(0.60, T0), TT, -10, -5, THEORY, 12.5, "end")
tag(vscale(0.60, N0), NN, 10, -5, BASE, 12.5, "start")
tag(vscale(0.60, B0), BB, 10, 4, TEXT, 12.5, "start")

# each patch is named at the corner that no other patch reaches
plane_tag(vadd(vscale(HALF, T0), vscale(-HALF, N0)), "oskülatör düzlem", BB,
          -12, -2, PRACTICE, "end")                     # left tip of the flat diamond
plane_tag(vadd(vscale(-HALF, T0), vscale(HALF, B0)), "rektifiyan düzlem", NN,
          12, -4, BASE, "start")                        # top corner, to the right
plane_tag(vadd(vscale(-HALF, N0), vscale(HALF, B0)), "normal düzlem", TT,
          -12, -4, THEORY, "end")                       # top corner, to the left

tag(beta(SMIN), "Frenet yaklaşımı", -14, 26, PRACTICE, 11.5, "middle")

LX, LY = P.X(-3.62), P.Y(-2.08)
halo(LX, LY, KAPPA_S + subs("0") + " = " + TAU_S + subs("0") + " = 1,"
     + "&#160;&#160;&#160;" + MINUS_S + "1,5 " + LEQ_S + " " + it("s") + " " + LEQ_S + " 1,5",
     TEXT, 11.5)
halo(LX, LY + 19, it(BETA_S) + "(" + it("s") + ") " + MINUS_S + " " + it(BETA_S) + "(0) "
     + APPROX_S + " " + it("s") + " " + TT + " + (" + it("s") + sups("2") + "/2) " + NN
     + " + (" + it("s") + sups("3") + "/6) " + BB, PRACTICE, 11.5)

# ---------------------------------------------------------------- 5. what the eye should check
d = (math.cos(math.radians(EL)) * math.cos(math.radians(AZ)),
     math.cos(math.radians(EL)) * math.sin(math.radians(AZ)), math.sin(math.radians(EL)))
print("  |T0|, |N0|, |B0| =", [round(vnorm(v), 12) for v in (T0, N0, B0)])
print("  T.N, N.B, B.T    =", [round(vdot(a, b), 12) for a, b in ((T0, N0), (N0, B0), (B0, T0))])
print("  T x N - B        =", [round(c, 12) for c in vsub(vcross(T0, N0), B0)])

h = 1e-5
tangent = vunit(vsub(beta(h), beta(-h)))
print("  egri tegeti(0) - T0 =", [round(c, 9) for c in vsub(tangent, T0)])
acc = vscale(1.0 / (h * h), vsub(vadd(beta(h), beta(-h)), vscale(2.0, beta(0.0))))
print("  egri ivmesi(0) = kappa0 N0 ?", [round(c, 6) for c in acc], " ivme . T0 =",
      round(vdot(acc, T0), 9))

for nm, v in (("T0", T0), ("N0", N0), ("B0", B0)):
    X, Y = S.pt(v)
    print(f"  {nm}: sayfa boyu {math.hypot(X, Y) * P.w / (P.xmax - P.xmin):.1f} px, "
          f"yon {math.degrees(math.atan2(Y, X)) % 360:.1f} derece")
XT, YT = S.pt(T0)
XC, YC = S.pt(beta(0.02))
print(f"  egrinin s=0 sayfa yonu {math.degrees(math.atan2(YC, XC)) % 360:.1f} derece "
      f"(T0 ile fark {abs(math.degrees(math.atan2(YC, XC) - math.atan2(YT, XT))):.2f} derece)")
XN, YN = S.pt(N0)
print(f"  sayfada T0-N0 acisi {math.degrees(math.acos((XT * XN + YT * YN) / (math.hypot(XT, YT) * math.hypot(XN, YN)))):.1f} "
      f"derece (uzayda 90)")
print("  duzlem acikligi |n.d|: oskulator %.2f, rektifiyan %.2f, normal %.2f"
      % (abs(vdot(B0, d)), abs(vdot(N0, d)), abs(vdot(T0, d))))

pts = [S.pt(beta(SMIN + (SMAX - SMIN) * k / 400.0)) for k in range(401)]
pts += [S.pt(q) for q in OSC + RECT + NORM + [T0, N0, B0]]
xs, ys = [q[0] for q in pts], [q[1] for q in pts]
print(f"  cizim X [{min(xs):.2f}, {max(xs):.2f}] Y [{min(ys):.2f}, {max(ys):.2f}]  "
      f"panel X [{P.xmin}, {P.xmax}] Y [{P.ymin}, {P.ymax}]")
print(f"  piksel/birim {P.w / (P.xmax - P.xmin):.1f}")

OUT["frenet-uc-duzlem"] = figure(
    464, 326, [P],
    "<em>&#946;</em>(0) noktasında Frenet çatısının üç birim vektörü &#8212; teğet "
    "<strong>T</strong><sub>0</sub> (mavi), asli normal <strong>N</strong><sub>0</sub> (yeşil) ve "
    "binormal <strong>B</strong><sub>0</sub> (koyu) &#8212; her biri bir düzlemi dik olarak deler: "
    "turuncu kare <strong>B</strong><sub>0</sub>&#8217;a dik oskülatör düzlem, yeşil kare "
    "<strong>N</strong><sub>0</sub>&#8217;a dik rektifiyan düzlem, mavi kare "
    "<strong>T</strong><sub>0</sub>&#8217;a dik normal düzlemdir; üç dik açı işareti çatının "
    "ikişer ikişer dikliğini gösterir. İnce turuncu yay, &#954;<sub>0</sub> = "
    "&#964;<sub>0</sub> = 1 alınarak yazılan <em>&#946;</em>(<em>s</em>) &#8722; "
    "<em>&#946;</em>(0) &#8776; <em>s</em> <strong>T</strong><sub>0</sub> + "
    "(<em>s</em><sup>2</sup>/2) <strong>N</strong><sub>0</sub> + (<em>s</em><sup>3</sup>/6) "
    "<strong>B</strong><sub>0</sub> Frenet yaklaşımıdır. Yay <em>s</em> = 0&#8217;da "
    "<strong>T</strong><sub>0</sub> okuna teğettir, ikinci terim onu oskülatör düzlem içinde "
    "<strong>N</strong><sub>0</sub> yönünde büker, en küçük olan üçüncü terim ise onu bu "
    "düzlemden <strong>B</strong><sub>0</sub> yönünde ayırır.",
    aria="beta(0) noktasinda Frenet catisinin uc birim oku: teget T0 mavi, asli normal N0 yesil, "
         "binormal B0 koyu, ikiser ikiser dik. Uc yari saydam kare duzlem parcasi: T0 ile N0'in "
         "gerdigi turuncu oskulator duzlem B0'a dik, T0 ile B0'in gerdigi yesil rektifiyan duzlem "
         "N0'a dik, N0 ile B0'in gerdigi mavi normal duzlem T0'a dik. Ince turuncu yay, "
         "kappa0 = tau0 = 1 icin beta(s) - beta(0) = s T0 + (s^2/2) N0 + (s^3/6) B0 Frenet "
         "yaklasimidir; s degeri -1,5 ile 1,5 arasinda cizilmistir ve yay s = 0 noktasinda "
         "T0 okuna tegettir")

# ============================================================ frenet-yaklasim-izdusumleri
# -*- coding: utf-8 -*-
# frenet-yaklasim-izdusumleri: the three projections of the Frenet approximation
#   beta^(s) - beta(0) = s T0 + (k0 s^2 / 2) N0 + (k0 t0 s^3 / 6) B0,  with k0 = t0 = 1, |s| <= 1.5,
# written in the frame coordinates p = s, q = s^2/2, w = s^3/6 exactly as the solution does:
#   osculating (T0, N0): q = p^2/2     parabola;  d(p, q)/ds = (1, s) -> (1, 0) at s = 0, so the
#                                      blue arrow along T0 really is the tangent there, and N0,
#                                      drawn as the vertical axis, is perpendicular to it on the page
#   rectifying (T0, B0): w = p^3/6     cubic; w'' = p changes sign at 0 -> inflection at the origin
#   normal     (N0, B0): w^2 = 2q^3/9  semicubical parabola; d(q, w)/ds = (s, s^2/2) ~ s(1, s/2),
#                                      so both branches leave the origin tangent to the N0 axis:
#                                      the cusp. q = s^2/2 >= 0, so only the right half plane is used.
# Scale: N0 and B0 get 160/1.7 = 94.1 px per unit in every panel, so the third panel — the only one
# whose shape depends on the aspect ratio, since the cusp is a tangency — is drawn with equal scale.
# T0 is compressed to 200/3.5 = 57.1 px per unit to keep the three panels on one line; an
# axis-parallel scaling leaves a horizontal tangent horizontal, so nothing above is disturbed.
# Labels sit in the empty parts: inside the cup of the parabola, in the two quadrants the cubic
# leaves free, and outside the horn of the semicubic. Leaders are slanted so that they are never
# read as a second copy of the vertical axis.

TOP, LEFT, GAP = 40, 30, 44
PW, PH, P3W = 200, 160, 198
S0, S1, NS = -1.5, 1.5, 400

p1 = Plot(LEFT, TOP, PW, PH, (-1.75, 1.75), (-0.35, 1.35))
p2 = Plot(LEFT + PW + GAP, TOP, PW, PH, (-1.75, 1.75), (-0.85, 0.85))
p3 = Plot(LEFT + 2 * (PW + GAP), TOP, P3W, PH, (-0.45, 1.65), (-0.85, 0.85))

SS = [S0 + (S1 - S0) * k / NS for k in range(NS + 1)]
KAPPA, TAU, BETA = "&#954;", "&#964;", "&#946;"


def ital(s):
    return f'<tspan font-style="italic">{s}</tspan>'


def sub0(s):
    """Frame name with the index 0: T0, N0, B0."""
    return s + subs("0")


def halo(p, x, y, s, dx=0, dy=0, color=TEXT, size=11.5, anchor="start", strong=False):
    """Text hung on a data point with a page-coloured halo, so a faint line behind it breaks."""
    st = ' font-weight="700"' if strong else ''
    p.add(f'<text x="{p.X(x) + dx:.1f}" y="{p.Y(y) + dy:.1f}" fill="{color}" font-size="{size}" '
          f'text-anchor="{anchor}"{st} stroke="{BG}" stroke-width="3.2" stroke-linejoin="round" '
          f'paint-order="stroke">{s}</text>')


def title(p, s):
    """Panel title, 15 px above the panel: the vertical axis arrowhead reaches y0 - 4."""
    p.text_px(p.x0 + p.w / 2, p.y0 - 15, s, TEXT, 11.5, "middle", True)


def axis_names(p, xname, yname):
    """Frame names at the two arrow tips: the x name under the right tip, the y name left of the
    top tip (on the right it would sit on the equation labels)."""
    p.text_px(p.x0 + p.w + 2, p.Y(0) + 16, xname, TEXT, 12, "end", True)
    p.text_px(p.X(0) - 8, p.y0 + 7, yname, TEXT, 12, "end", True)


def leader(p, a, b, opacity=0.6):
    """Thin line from a label to the point it names."""
    p.add(f'<line x1="{p.X(a[0]):.1f}" y1="{p.Y(a[1]):.1f}" x2="{p.X(b[0]):.1f}" y2="{p.Y(b[1]):.1f}" '
          f'stroke="{TEXT}" stroke-width="0.9" opacity="{opacity}"/>')


def bead(p, pt, color=PRACTICE, r=2.8):
    """Dot on a curve, rimmed with the page colour so it stays visible on the stroke."""
    p.add(f'<circle cx="{p.X(pt[0]):.1f}" cy="{p.Y(pt[1]):.1f}" r="{r}" fill="{color}" '
          f'stroke="{BG}" stroke-width="1.2" paint-order="stroke"/>')


def origin_dot(p):
    p.points([(0, 0)], TEXT, 3.4)


# ---------------------------------------------------------------------------------------------
# 1. osculating plane (T0, N0): the parabola q = p^2/2 and the tangent T0 at beta(0)
# ---------------------------------------------------------------------------------------------
title(p1, "Oskülatör düzlem (" + sub0("T") + sub0("N") + ")")
p1.origin_axes("", "")
p1.line([(s, s * s / 2) for s in SS], PRACTICE, 2.2)
p1.arrow((0, 0), (0.8, 0), THEORY, 2.4, head=8)
origin_dot(p1)
axis_names(p1, sub0("T"), sub0("N"))

# both labels sit inside the cup of the parabola, centred on the N0 axis; at q = 0,9 the arms are
# 76 px from the axis and at q = 0,55 they are 60 px, so a 56 px label clears them either side
halo(p1, 0, 0.90, ital("q") + " = " + ital("p") + sups("2") + "/2", 0, 0, PRACTICE, 12, "middle")
halo(p1, 0, 0.55, KAPPA + subs("0") + " = " + TAU + subs("0") + " = 1", 0, 0, TEXT, 11.5, "middle")
halo(p1, 0, 0, BETA + "(0)", -8, 15, TEXT, 11.5, "end")
halo(p1, 0.5, 0, "teğet", 0, 18, THEORY, 11.5, "middle")

# ---------------------------------------------------------------------------------------------
# 2. rectifying plane (T0, B0): the cubic w = p^3/6 with its inflection at beta(0)
# ---------------------------------------------------------------------------------------------
title(p2, "Rektifiyan düzlem (" + sub0("T") + sub0("B") + ")")
p2.origin_axes("", "")
p2.line([(s, s ** 3 / 6) for s in SS], PRACTICE, 2.2)
origin_dot(p2)
axis_names(p2, sub0("T"), sub0("B"))

# the cubic leaves the upper left and lower right quadrants free; the two sign labels sit in the
# wedges the curve leaves next to itself and say what the inflection does: w changes sign at s = 0
halo(p2, -1.62, 0.58, ital("w") + " = " + ital("p") + sups("3") + "/6", 0, 0, PRACTICE, 12, "start")
halo(p2, 0.60, 0.55, ital("w") + " &gt; 0", 0, 0, TEXT, 11, "start")
halo(p2, -0.45, -0.60, ital("w") + " &lt; 0", 0, 0, TEXT, 11, "end")
halo(p2, 0, 0, BETA + "(0)", -8, -9, TEXT, 11.5, "end")
leader(p2, (0.316, -0.33), (0.07, -0.095))
halo(p2, 1.62, -0.45, "dönüm noktası", 0, 0, TEXT, 11.5, "end")

# ---------------------------------------------------------------------------------------------
# 3. normal plane (N0, B0): the semicubical parabola w^2 = 2q^3/9, cusp at beta(0), q >= 0
# ---------------------------------------------------------------------------------------------
title(p3, "Normal düzlem (" + sub0("N") + sub0("B") + ")")
p3.origin_axes("", "")
p3.line([(s * s / 2, s ** 3 / 6) for s in SS], PRACTICE, 2.2)
bead(p3, (S1 * S1 / 2, S1 ** 3 / 6))
bead(p3, (S0 * S0 / 2, S0 ** 3 / 6))
origin_dot(p3)
axis_names(p3, sub0("N"), sub0("B"))

halo(p3, 0.12, 0.60, ital("w") + sups("2") + " = 2" + ital("q") + sups("3") + "/9", 0, 0,
     PRACTICE, 12, "start")
halo(p3, 0, 0, BETA + "(0)", -8, 15, TEXT, 11.5, "end")
leader(p3, (0.33, -0.60), (0.06, -0.07))
halo(p3, 0.35, -0.72, "sivri uç", 0, 0, TEXT, 11.5, "start")
halo(p3, S1 * S1 / 2, S1 ** 3 / 6, ital("s") + " = 1,5", 7, 4, TEXT, 11, "start")
halo(p3, S0 * S0 / 2, S0 ** 3 / 6, ital("s") + " = " + MINUS_S + "1,5", 7, 4, TEXT, 11, "start")

OUT["frenet-yaklasim-izdusumleri"] = figure(
    734, 220, [p1, p2, p3],
    "Frenet yaklaşımının &#954;<sub>0</sub> = 1, &#964;<sub>0</sub> = 1 ve "
    "&#8722;1,5 &#8804; <em>s</em> &#8804; 1,5 için üç çatı düzlemine dik izdüşümleri; her panelde "
    "orijin <strong>&#946;</strong>(0) noktasıdır ve çatı koordinatları "
    "<em>p</em> = <em>s</em>, <em>q</em> = <em>s</em><sup>2</sup>/2, "
    "<em>w</em> = <em>s</em><sup>3</sup>/6&#8217;dır. Oskülatör düzlemde <em>q</em> = "
    "<em>p</em><sup>2</sup>/2 parabolü görülür: eğri <strong>&#946;</strong>(0) noktasında "
    "<strong>T</strong><sub>0</sub>&#8217;a teğettir (mavi ok) ve "
    "<strong>N</strong><sub>0</sub> yönüne kıvrılır. Rektifiyan düzlemdeki "
    "<em>w</em> = <em>p</em><sup>3</sup>/6 kübiğinin orijinde dönüm noktası vardır; eğri burada "
    "<strong>B</strong><sub>0</sub> bileşeninin işaretini değiştirir. Normal düzlemde ise "
    "<em>w</em><sup>2</sup> = 2<em>q</em><sup>3</sup>/9 yarı kübik parabolü yalnızca "
    "<em>q</em> &#8805; 0 yarı düzleminde kalır ve orijinde sivri uç yapar: eğriye "
    "<strong>T</strong><sub>0</sub> doğrultusunda bakan gözlemci onu gelip geri dönüyormuş gibi "
    "görür.",
    css_class=WIDE,
    aria="Yan yana uc panel. Birincide oskulator duzlem T0 N0: turuncu parabol q = p kare bolu 2, "
         "orijindeki siyah nokta beta(0) ve oradan T0 yonunde cikan kisa mavi teget oku. "
         "Ikincide rektifiyan duzlem T0 B0: turuncu kubik w = p kup bolu 6, orijinde donum "
         "noktasi. Ucuncude normal duzlem N0 B0: turuncu yari kubik parabol w kare = 2 q kup "
         "bolu 9, yalnizca q nun negatif olmadigi yari duzlemde, orijinde sivri uc; iki ucu "
         "s = 1,5 ve s = eksi 1,5 olarak isaretli. Her panelde kappa0 = 1 ve tau0 = 1.",
)

# ============================================================ iccarpim-aci-kosinus
# -*- coding: utf-8 -*-
# iccarpim-aci-kosinus: the angle between two vectors and the "shadow" reading of the dot product.
# In the xy plane, from a common origin: w = (3, 0) (orange, along the x axis) and v = (2, 2) (blue).
# The angle between them is vartheta = pi/4, marked by a small arc. A dashed perpendicular drops from
# the tip of v to the x axis, its foot at (2, 0); the segment from the origin to the foot is drawn as a
# thick translucent blue band beneath w: it is the shadow of v on w, of length ||v|| cos vartheta = 2.
# The note in the empty upper-right region records v . w = 6 = 2 . 3 = (||v|| cos vartheta) . ||w||.
import math

DBAR = "&#8214;"                                        # double vertical bar for the norm
TH = '<tspan font-style="italic">&#977;</tspan>'        # vartheta, as in the text
V, W = bold("v"), bold("w")
NORM_V = DBAR + V + DBAR
NORM_W = DBAR + W + DBAR

p = cplane(30, 18, 340, (-0.55, 3.75), (-0.55, 3.3))

O = (0.0, 0.0)
v_tip = (2.0, 2.0)
w_tip = (3.0, 0.0)
foot = (2.0, 0.0)

# 1. axes through the origin, scaled 0..3 on both
p.origin_axes("x", "y", xticks=(1, 2, 3), yticks=(1, 2, 3))

# 2. the shadow of v on w: thick translucent band from the origin to the foot, drawn beneath w
p.line([O, foot], THEORY, 7.0, None, 0.35)

# 3. angle arc between w (angle 0) and v (angle pi/4)
p.arc(0, 0, 0.6, 0.0, math.pi / 4, TEXT, 1.2, None, 0.85)

# 4. dashed perpendicular from the tip of v to the x axis, with a right-angle mark at the foot
guide(p, [v_tip, foot], TEXT, 0.6)
s = 0.13
p.line([(2.0 - s, 0.0), (2.0 - s, s), (2.0, s)], TEXT, 1.0, None, 0.7)

# 5. the two vectors
p.arrow(O, w_tip, PRACTICE, 2.4, head=9)
p.arrow(O, v_tip, THEORY, 2.4, head=9)

# 6. points: origin and the foot of the perpendicular
dot(p, O, TEXT, 3.2)
dot(p, foot, TEXT, 3.2)

# 7. labels
p.label(1.0, 1.0, V + " = (2, 2)", -9, -3, THEORY, 12, "end")
p.label(2.5, 0.0, W + " = (3, 0)", 0, 31, PRACTICE, 12, "middle")
p.label(0.73, 0.27, TH + " = " + PI_S + "/4", 0, 4, TEXT, 12, "start")
p.label(2.0, 0.0, "(2, 0)", 8, -7, TEXT, 11.5, "start")
p.label(1.0, 0.0, NORM_V + " cos " + TH + " = 2", 0, 31, THEORY, 12, "middle")

# note in the free upper region: the product and what each factor is
p.label(2.2, 2.98, V + " " + CDOT + " " + W + " = 6 = 2 " + CDOT + " 3", 0, 0, TEXT, 12.5, "middle")
p.label(2.2, 2.72, "2 = " + NORM_V + " cos " + TH + ",&#160;&#160;&#160;3 = " + NORM_W, 0, 0, TEXT, 11.5, "middle")

OUT["iccarpim-aci-kosinus"] = figure(
    400, 330, [p],
    "<em>xy</em> düzleminde ortak başlangıçtan çıkan iki ok: <strong>w</strong> = (3, 0) (turuncu) "
    "<em>x</em> ekseni üzerindedir, <strong>v</strong> = (2, 2) (mavi) köşegen doğrultusundadır ve "
    "aralarındaki açı <em>&#977;</em> = &#960;/4&#8217;tür. <strong>v</strong>&#8217;nin ucundan "
    "<strong>w</strong>&#8217;nin doğrusuna inen kesikli dikmenin ayağı (2, 0) noktasıdır; başlangıçtan "
    "bu ayağa kadar uzanan kalın parça <strong>v</strong>&#8217;nin <strong>w</strong> doğrultusundaki "
    "gölgesidir ve boyu &#8214;<strong>v</strong>&#8214; cos <em>&#977;</em> = 2&#8217;dir. "
    "İç çarpım bu gölge boyunun &#8214;<strong>w</strong>&#8214; = 3 ile çarpımıdır: "
    "<strong>v</strong> &#183; <strong>w</strong> = 2 &#183; 3 = 6.",
    aria="xy duzleminde ortak baslangictan cikan iki ok: w = (3, 0) turuncu, x ekseni uzerinde; "
         "v = (2, 2) mavi; aralarindaki aci theta = pi/4 kucuk bir yayla isaretli; v'nin ucundan "
         "x eksenine inen kesikli dikmenin ayagi (2, 0); baslangictan (2, 0)'a kadar kalin parca "
         "||v|| cos theta = 2; not: v . w = 6 = 2 . 3",
)

# ============================================================ iccarpim-acik-yuvar
# -*- coding: utf-8 -*-
# iccarpim-acik-yuvar: the z = 0 section of the open unit ball O = {||p|| < 1}.
# The unit circle (centre origin, radius 1) is dashed because it does not belong to O; the disk
# inside it is tinted grey. At p = (1/2, 0, 0) the gap to the unit sphere is eps = 1 - ||p|| = 1/2,
# and the blue ball N_eps(p) of that radius touches the unit circle from inside at (1, 0, 0)
# without sticking out. The radius from p to (1, 0, 0) carries eps = 1 - ||p|| = 1/2.
# Point names keep the three coordinates of the box text; the note "z = 0 kesiti" in the empty
# lower-left part of the disk says which plane we are looking at.
# Tick labels are placed by hand: origin_axes() would print 1 and -1 exactly on the dashed circle,
# which passes through (+-1, 0) and (0, +-1).

DBAR = "&#8214;"                                   # double vertical bar for the norm
P_B = bold("p")
NORM_P = DBAR + P_B + DBAR
EPS_LABEL = EPS + " = 1 " + MINUS_S + " " + NORM_P + " = 1/2"


def ital(s):
    return '<tspan font-style="italic">' + s + '</tspan>'


XR, YR = (-1.42, 1.50), (-1.22, 1.22)
p = cplane(26, 20, 340, XR, YR)
ox, oy = p.X(0.0), p.Y(0.0)

P = (0.5, 0.0)          # the point p, drawn in the z = 0 plane
T = (1.0, 0.0)          # where N_eps(p) touches the unit circle
EPSILON = 0.5           # 1 - ||p||


def tick_mark(t, along_x):
    if along_x:
        X = p.X(t)
        p.add(f'<line x1="{X:.1f}" y1="{oy-3:.1f}" x2="{X:.1f}" y2="{oy+3:.1f}" '
              f'stroke="{TEXT}" stroke-width="1" opacity="0.7"/>')
    else:
        Y = p.Y(t)
        p.add(f'<line x1="{ox-3:.1f}" y1="{Y:.1f}" x2="{ox+3:.1f}" y2="{Y:.1f}" '
              f'stroke="{TEXT}" stroke-width="1" opacity="0.7"/>')


def tick_label(px, py, s, anchor):
    p.add(f'<text x="{px:.1f}" y="{py:.1f}" fill="{TEXT}" font-size="11" text-anchor="{anchor}" '
          f'opacity="0.7">{s}</text>')


# 1. the open unit disk O: light grey fill, dashed boundary (the unit circle is not part of O)
disk_fill(p, 0.0, 0.0, 1.0, TEXT, 0.10)

# 2. axes through the origin; ticks by hand (see the note at the top)
p.origin_axes("x", "y")
tick_mark(-1.0, True)
tick_mark(1.0, False)
tick_mark(-1.0, False)
tick_label(p.X(-1.0) - 6, oy + 15, MINUS_S + "1", "end")      # left of the circle's leftmost point
tick_label(ox - 8, p.Y(1.0) - 5, "1", "end")                  # above the circle's top
tick_label(ox - 8, p.Y(-1.0) + 14, MINUS_S + "1", "end")      # below the circle's bottom

# 3. the dashed unit circle
p.circle(0.0, 0.0, 1.0, TEXT, 1.4, "5 4", "none", 0.7)

# 4. the ball N_eps(p): blue tint and blue rim, tangent to the unit circle at (1, 0, 0)
disk_fill(p, P[0], P[1], EPSILON, THEORY, 0.20)
p.circle(P[0], P[1], EPSILON, THEORY, 1.7)

# 5. the radius from p to the point of tangency: the gap eps = 1 - ||p||
p.line([P, T], THEORY, 2.4)

# 6. points: p (filled) and (1, 0, 0) (hollow: it lies on the unit sphere, so it is not in O)
dot(p, P, TEXT, 4.0)
hollow(p, T, TEXT, 3.6, 1.6)

# 7. labels — the two inside the ball sit above and below its horizontal radius
p.label(P[0], P[1], P_B + " = (1/2, 0, 0)", 0, 19, TEXT, 11.5, "middle")
p.label(0.90, 0.0, EPS_LABEL, 0, -11, THEORY, 11, "end")
p.label(P[0], 0.26, ital("N") + subs(EPS) + "(" + P_B + ")", 0, 0, THEORY, 12, "middle")
p.label(T[0], T[1], "(1, 0, 0)", 7, -7, TEXT, 11, "start")
p.label(-0.5, 0.38, "açık yuvar " + ital("O"), 0, 0, TEXT, 11.5, "middle")
p.label(-0.52, 1.03, "birim çember", 0, 0, TEXT, 10.5, "end")
p.label(-0.52, 0.915, "(" + ital("O") + "'ya ait değil)", 0, 0, TEXT, 10.5, "end")
p.label(-0.48, -0.52, "(" + ital("z") + " = 0 kesiti)", 0, 0, TEXT, 11, "middle")

OUT["iccarpim-acik-yuvar"] = figure(
    400, 330, [p],
    "Şekil, &#8214;<strong>p</strong>&#8214; &lt; 1 açık birim yuvarının <em>z</em> = 0 düzlemiyle "
    "kesitidir: gri disk <em>O</em>&#8217;nun noktalarıdır, kesikli çizilen birim çember ise kümeye "
    "ait değildir. <strong>p</strong> = (1/2, 0, 0) noktasının çembere olan boşluğu "
    "&#949; = 1 &#8722; &#8214;<strong>p</strong>&#8214; = 1/2&#8217;dir; bu yarıçapla çizilen mavi "
    "<em>N</em><sub>&#949;</sub>(<strong>p</strong>) yuvarı birim çembere (1, 0, 0) noktasında içten "
    "dokunur ama dışına taşmaz, yani tamamen <em>O</em>&#8217;nun içinde kalır. Çembere yaklaşan "
    "noktalarda &#949; küçülür, fakat &#8214;<strong>p</strong>&#8214; &lt; 1 olduğu sürece sıfır "
    "olmaz; <em>O</em> bu yüzden açıktır.",
    aria="z = 0 kesiti: merkezi orijin, yaricapi 1 olan kesikli birim cember ve icini dolduran gri "
         "disk O; p = (1/2, 0, 0) noktasi isaretli; merkezi p, yaricapi epsilon = 1/2 olan mavi "
         "cember birim cembere (1, 0, 0) noktasinda icten dokunuyor; p'den (1, 0, 0)'a giden parca "
         "epsilon = 1 - ||p|| = 1/2 etiketli; eksenler -1 ile 1 arasinda olcekli",
)

# ============================================================ iccarpim-kure-acik-degil
# -*- coding: utf-8 -*-
# iccarpim-kure-acik-degil: the z = 0 section of the unit sphere S = {||p|| = 1}, which is not open.
# S itself is only the surface, so the section is drawn as a thick solid circle (no tint inside).
# At p = (1, 0, 0) the neighbourhood N_eps(p) of radius eps = 1/2 (blue, dashed rim, light tint)
# spills both inside and outside the circle; q = (5/4, 0, 0) lies in that neighbourhood, at distance
# eps/2 = 1/4 from p, but ||q|| = 5/4 is not 1, so q is not in S.
# Point names keep the three coordinates of the box text, as in iccarpim-acik-yuvar; the note
# "(z = 0 kesiti)" in the empty inside of the circle says which plane we are looking at.
# Labels near the two circles are drawn with a background halo (paint-order) so the lines break
# behind them instead of running through the text.
import math

DBAR = "&#8214;"                                   # double vertical bar for the norm
P_B, Q_B = bold("p"), bold("q")
NORM_P = DBAR + P_B + DBAR
NORM_Q = DBAR + Q_B + DBAR

XR, YR = (-1.5, 2.15), (-1.3, 1.35)
p = cplane(28, 22, 344, XR, YR)
ox, oy = p.X(0.0), p.Y(0.0)

P = (1.0, 0.0)                                     # the point of S we test
Q = (1.25, 0.0)                                    # 1 + eps/2, inside N_eps(p) but outside S
EPSILON = 0.5
RIM = (1.0 + EPSILON * math.cos(math.pi / 4), EPSILON * math.sin(math.pi / 4))   # end of the eps radius


def ital(s):
    return '<tspan font-style="italic">' + s + '</tspan>'


def txt(x, y, s, dx=0, dy=0, color=TEXT, size=11.5, anchor="middle", opacity=1.0):
    """Label at a data point with a page-coloured halo, so lines behind it break."""
    op = f' opacity="{opacity}"' if opacity < 1.0 else ""
    p.add(f'<text x="{p.X(x) + dx:.1f}" y="{p.Y(y) + dy:.1f}" fill="{color}" font-size="{size}" '
          f'text-anchor="{anchor}"{op} stroke="{BG}" stroke-width="3.0" stroke-linejoin="round" '
          f'paint-order="stroke">{s}</text>')


def tick_mark(t, along_x):
    if along_x:
        X = p.X(t)
        p.add(f'<line x1="{X:.1f}" y1="{oy-3:.1f}" x2="{X:.1f}" y2="{oy+3:.1f}" '
              f'stroke="{TEXT}" stroke-width="1" opacity="0.7"/>')
    else:
        Y = p.Y(t)
        p.add(f'<line x1="{ox-3:.1f}" y1="{Y:.1f}" x2="{ox+3:.1f}" y2="{Y:.1f}" '
              f'stroke="{TEXT}" stroke-width="1" opacity="0.7"/>')


# 1. the neighbourhood N_eps(p): light blue tint (drawn first, everything else sits on top)
disk_fill(p, P[0], P[1], EPSILON, THEORY, 0.16)

# 2. axes through the origin; ticks by hand, so that no tick number lands on a circle
p.origin_axes("x", "y")
tick_mark(-1.0, True)
tick_mark(1.0, False)
tick_mark(-1.0, False)
txt(-1.0, 0.0, MINUS_S + "1", -7, 15, TEXT, 11, "end", 0.7)
txt(0.0, 1.0, "1", -8, -5, TEXT, 11, "end", 0.7)
txt(0.0, -1.0, MINUS_S + "1", -8, 14, TEXT, 11, "end", 0.7)

# 3. S itself: the unit circle, thick and solid — the set is exactly this curve
p.circle(0.0, 0.0, 1.0, TEXT, 2.8)

# 4. the rim of N_eps(p): dashed blue, crossing S at two points
p.circle(P[0], P[1], EPSILON, THEORY, 1.7, "5 4")

# 5. the radius of the neighbourhood, into the free space above and right of p
p.line([P, RIM], THEORY, 2.2)

# 6. leader from q down to its label block
p.line([(1.28, -0.07), (1.45, -0.52)], PRACTICE, 0.9, None, 0.8)

# 7. points: p belongs to S (filled), q does not (hollow).
# p sits on the thick circle and would melt into it, so a thin background ring separates the two.
p.add(f'<circle cx="{p.X(P[0]):.1f}" cy="{p.Y(P[1]):.1f}" r="5.8" fill="{BG}" stroke="none"/>')
dot(p, P, TEXT, 4.2)
hollow(p, Q, PRACTICE, 4.0, 1.8)

# 8. labels
txt(-0.98, 1.14, ital("S") + ": " + NORM_P + " = 1", 0, 0, TEXT, 12.5)
txt(-0.98, 0.99, "birim küre", 0, 0, TEXT, 11)
# p's name sits clear of the thick circle, so that its halo does not bite into S
txt(P[0], P[1], P_B + " = (1, 0, 0)", -15, 23, TEXT, 12, "end")
txt(1.25, 0.62, ital("N") + subs(EPS) + "(" + P_B + ")", 0, 0, THEORY, 12)
# the radius is labelled past its far end, so the segment does not run through the text
txt(RIM[0], RIM[1], EPS + " = 1/2", 6, -4, THEORY, 11.5, "start")

txt(1.45, -0.64, Q_B + " = (5/4, 0, 0)", 0, 0, PRACTICE, 12)
txt(1.45, -0.80, NORM_Q + " = 5/4 " + NEQ_S + " 1", 0, 0, PRACTICE, 11.5)
txt(1.45, -0.96, ital("S") + "'de değil", 0, 0, PRACTICE, 11.5)

txt(1.30, 0.98, ital("d") + "(" + P_B + ", " + Q_B + ") = " + EPS + "/2 = 1/4 &lt; " + EPS,
    0, 0, TEXT, 11.5)
txt(-0.45, -0.45, "(" + ital("z") + " = 0 kesiti)", 0, 0, TEXT, 11, "middle", 0.8)

OUT["iccarpim-kure-acik-degil"] = figure(
    400, 296, [p],
    "<em>S</em>: &#8214;<strong>p</strong>&#8214; = 1 birim küresinin <em>z</em> = 0 kesiti kalın "
    "çemberdir; küme yalnızca yüzeydir, çemberin içi <em>S</em>&#8217;ye ait değildir. "
    "<strong>p</strong> = (1, 0, 0) noktası <em>S</em>&#8217;nin üzerindedir, ama yarıçapı "
    "&#949; = 1/2 olan <em>N</em><sub>&#949;</sub>(<strong>p</strong>) komşuluğu çemberin hem içine "
    "hem dışına taşar. Komşuluktaki <strong>q</strong> = (5/4, 0, 0) noktası <strong>p</strong>&#8217;ye "
    "yalnızca &#949;/2 = 1/4 uzaklıktadır, fakat &#8214;<strong>q</strong>&#8214; = 5/4 &#8800; 1 "
    "olduğundan <em>S</em>&#8217;de değildir. &#949; ne kadar küçültülürse küçültülsün aynı şey olur: "
    "bir yüzeyin kalınlığı yoktur, hiçbir yuvar onun içine sığmaz, bu yüzden <em>S</em> açık değildir.",
    aria="z = 0 kesiti: merkezi orijin, yaricapi 1 olan kalin birim cember S ve uzerindeki "
         "p = (1, 0, 0) noktasi; merkezi p, yaricapi epsilon = 1/2 olan mavi kesikli komsuluk cemberi "
         "birim cemberin hem icine hem disina tasar; komsulugun icindeki q = (5/4, 0, 0) noktasi "
         "birim cemberin disindadir, normu 5/4, yani S'de degildir; p ile q arasindaki uzaklik "
         "epsilon bolu 2 = 1/4",
)

# ============================================================ iccarpim-ortonormal-acilim
# -*- coding: utf-8 -*-
# iccarpim-ortonormal-acilim: the orthonormal expansion of v = (3, 1, 2) at p = (1, 1, 0)
# in the rotated frame e1 = (1,1,0)/sqrt2, e2 = (-1,1,0)/sqrt2, e3 = (0,0,1).
#   (v.e1) e1 = 2 sqrt2 e1 = (2, 2, 0),  (v.e2) e2 = -sqrt2 e2 = (1, -1, 0),  (v.e3) e3 = 2 e3.
# The three components are the edges of a box with sides 2 sqrt2, sqrt2, 2 whose main diagonal
# is v; the second edge runs against e2 because its coefficient is negative.
# Camera az=34, el=18 comes from _scan_ortonormal.py: it keeps the four rays leaving p
# (three bold edges and v) at least 41 degrees apart in projection and no face of the box
# degenerate, while v still projects 1.28 units long.
# Tick labels are drawn by hand with a halo: near x = 1, 2 the x axis runs inside the narrow
# wedge above the (v.e2)e2 edge, and the y axis runs ~16 px above the e2 arrow, so the
# y labels are placed on the upper side of their axis.

AZ, EL = 34.0, 18.0
P = space_panel(26, 16, 452, (-3.05, 3.15), (-1.75, 2.90))
S = Space(P, Camera(azimuth=AZ, elevation=EL, scale=1.0))

R2 = math.sqrt(2.0)
SQ2 = "&#8730;2"

p = (1.0, 1.0, 0.0)
E1 = (2.0, 2.0, 0.0)          # (v . e1) e1 = 2 sqrt2 e1
E2 = (1.0, -1.0, 0.0)         # (v . e2) e2 = -sqrt2 e2   (opposite to e2)
E3 = (0.0, 0.0, 2.0)          # (v . e3) e3 = 2 e3
e1 = (1.0 / R2, 1.0 / R2, 0.0)
e2 = (-1.0 / R2, 1.0 / R2, 0.0)
e3 = (0.0, 0.0, 1.0)

A = vadd(p, E1)               # (3, 3, 0)
B = vadd(p, E2)               # (2, 0, 0)
C = vadd(p, E3)               # (1, 1, 2)
AB = vadd(A, E2)              # (4, 2, 0)
AC = vadd(A, E3)              # (3, 3, 2)
BC = vadd(B, E3)              # (2, 0, 2)
TIP = vadd(p, (3.0, 1.0, 2.0))  # (4, 2, 2) — the far corner, tip of v


def ital(s):
    """Italic run inside an SVG <text> — the frame names e1, e2, e3 are italic."""
    return f'<tspan font-style="italic">{s}</tspan>'


def txt(q, s, dx=0, dy=0, color=TEXT, size=11.0, anchor="start", opacity=1.0):
    """Label at a space point, haloed with the page colour so dashed edges break behind it."""
    X, Y = S.pt(q)
    px(P.X(X) + dx, P.Y(Y) + dy, s, color, size, anchor, opacity)


def px(x, y, s, color=TEXT, size=11.0, anchor="start", opacity=1.0):
    """Haloed label at a pixel position."""
    op = f' opacity="{opacity}"' if opacity < 1.0 else ""
    P.add(f'<text x="{x:.1f}" y="{y:.1f}" fill="{color}" font-size="{size}" '
          f'text-anchor="{anchor}"{op} stroke="{BG}" stroke-width="3.4" stroke-linejoin="round" '
          f'paint-order="stroke">{s}</text>')


def tick(axis, value, dx, dy, anchor="middle"):
    """Tick mark on a coordinate axis with a haloed label."""
    k = "xyz".index(axis)
    tdir = {"x": (0, 1, 0), "y": (1, 0, 0), "z": (1, 0, 0)}[axis]
    q = [0.0, 0.0, 0.0]
    q[k] = value
    q = tuple(q)
    S.line([vadd(q, vscale(-0.04, tdir)), vadd(q, vscale(0.04, tdir))], TEXT, 1.0, None, 0.7)
    txt(q, fmt(value), dx, dy, TEXT, 10, anchor, 0.75)


V = bold("v")
EE = [ital("e") + subs(str(k)) for k in (1, 2, 3)]


def comp_label(k, coef):
    return "(" + V + " " + CDOT + " " + EE[k] + ") " + EE[k] + " = " + coef + " " + EE[k]


# 1. floor: the footprint of the box, then the grid and the axes ----------------------------
S.polygon([p, A, AB, B], TEXT, 0.06)
S.floor_grid((0, 4), (0, 3), n=4, opacity=0.10)
S.line([(0, 3, 0), (4, 3, 0)], TEXT, 0.7, None, 0.10)
S.axes(4.5, 3.5, 2.7)
for _v in (1, 2, 3, 4):
    tick("x", _v, -10, 11)
tick("y", 1, 7, -7, "start")            # above the axis: the e2 arrow runs just below it
tick("y", 2, 4, -7, "start")
tick("y", 3, 4, -7, "start")
tick("z", 1, -9, 4, "end")
tick("z", 2, -9, 4, "end")

# 2. the box: the nine edges that do not start at p, dashed ---------------------------------
for a, b in ((A, AB), (A, AC), (B, AB), (B, BC), (C, AC), (C, BC),
             (AB, TIP), (AC, TIP), (BC, TIP)):
    S.guide([a, b], TEXT, 0.42, 1.0, "5 4")

# 3. the three components as thick edges leaving p ------------------------------------------
for q in (A, B, C):
    S.line([p, q], PRACTICE, 3.2, None, 0.9)

# 4. the frame: unit arrows at p (e2 runs against its own component) -------------------------
for e in (e1, e2, e3):
    S.arrow(p, vadd(p, e), BASE, 2.0, head=7)

# 5. v itself: the main diagonal of the box --------------------------------------------------
S.arrow(p, TIP, THEORY, 2.6, head=10)

S.point(p, TEXT, 3.8)
S.point(TIP, TEXT, 3.0)

# 6. labels ---------------------------------------------------------------------------------
txt(p, bold("p") + " = (1, 1, 0)", -6, 22, TEXT, 11.5, "end")
txt(vadd(p, vscale(0.55, (3.0, 1.0, 2.0))), V + " = (3, 1, 2)", -14, -1, THEORY, 12.5, "end")

txt(vadd(p, e1), EE[0], 10, 5, BASE, 12, "start")
txt(vadd(p, e2), EE[1], 2, 14, BASE, 12, "middle")
txt(vadd(p, e3), EE[2], 9, 4, BASE, 12, "start")

txt(A, comp_label(0, "2" + SQ2), 10, 6, PRACTICE, 11, "start")
txt(B, comp_label(1, MINUS_S + SQ2), -4, -13, PRACTICE, 11, "end")
txt(C, comp_label(2, "2"), 9, -7, PRACTICE, 11, "start")

# the result, in the free upper-left corner
px(120, 72, "Ortonormal açılım", TEXT, 10.5, "middle", 0.75)
px(120, 92, V + " = 2" + SQ2 + " " + EE[0] + " " + MINUS_S + " " + SQ2 + " " + EE[1]
   + " + 2 " + EE[2], TEXT, 12.5, "middle")

OUT["iccarpim-ortonormal-acilim"] = figure(
    504, 375, [P],
    "<strong>p</strong> = (1, 1, 0) noktasındaki <em>e</em><sub>1</sub>, <em>e</em><sub>2</sub>, "
    "<em>e</em><sub>3</sub> çatısı yeşil birim oklarla, <strong>v</strong> = (3, 1, 2) teğet vektörü "
    "mavi okla çizilmiştir. Turuncu üç kenar <strong>v</strong>&#8217;nin çatı doğrultularındaki "
    "bileşenleridir: (<strong>v</strong> &#183; <em>e</em><sub>1</sub>)<em>e</em><sub>1</sub> = "
    "2&#8730;2 <em>e</em><sub>1</sub>, (<strong>v</strong> &#183; <em>e</em><sub>2</sub>)"
    "<em>e</em><sub>2</sub> = &#8722;&#8730;2 <em>e</em><sub>2</sub> ve (<strong>v</strong> &#183; "
    "<em>e</em><sub>3</sub>)<em>e</em><sub>3</sub> = 2<em>e</em><sub>3</sub>; ikinci katsayı "
    "negatif olduğu için o kenar <em>e</em><sub>2</sub> okunun tersi yönde gider. "
    "Üç bileşen, kenarları 2&#8730;2, &#8730;2 ve 2 olan kesikli kutuyu belirler ve "
    "<strong>v</strong> bu kutunun <strong>p</strong>&#8217;den çıkan köşegenidir: ortonormal "
    "açılımın katsayıları, <strong>v</strong>&#8217;nin çatı doğrultularındaki işaretli gölge "
    "uzunluklarıdır.",
    aria="Tangent vector v = (3, 1, 2) at p = (1, 1, 0) drawn as the diagonal of the box whose edges "
         "are its components in the frame e1 = (1,1,0)/sqrt2, e2 = (-1,1,0)/sqrt2, e3 = (0,0,1): "
         "(v.e1)e1 = 2 sqrt2 e1, (v.e2)e2 = -sqrt2 e2 running opposite to the e2 arrow, and "
         "(v.e3)e3 = 2 e3; a note gives v = 2 sqrt2 e1 - sqrt2 e2 + 2 e3",
)

# ============================================================ iccarpim-paralelyuz-hacmi
# -*- coding: utf-8 -*-
# iccarpim-paralelyuz-hacmi: the parallelepiped spanned by u = (1, 2, 3) (blue), v = (2, 0, 0) and
# w = (1, 3, 0) (orange) at the origin. Its base is the hatched parallelogram (0,0,0), (2,0,0),
# (3,3,0), (1,3,0) in the xy plane, of area ||v x w|| = 6; the unit normal e = (0, 0, 1) (green)
# sits on the dashed perpendicular that falls from the tip of u to the base, whose length is
# u . e = 3. Volume = 6 . 3 = 18.
# Camera azimuth 40 (rather than the usual 35) keeps the vertex u + v clear of the z axis;
# elevation 24 opens the base enough to read the hatching. The origin is the hidden far vertex of
# the box, which is exactly right here: the three edges that meet there are the three vectors, and
# they are drawn last, opaque, over the glassy faces.
import math

DBAR = "&#8214;"                       # double bar, for the norm

P = space_panel(14, 14, 404, (-2.45, 3.64), (-2.05, 3.24))
S = Space(P, Camera(azimuth=40.0, elevation=24.0, scale=1.0))

O = (0.0, 0.0, 0.0)
u = (1.0, 2.0, 3.0)
v = (2.0, 0.0, 0.0)
w = (1.0, 3.0, 0.0)
e = (0.0, 0.0, 1.0)
uv, uw, vw = vadd(u, v), vadd(u, w), vadd(v, w)
uvw = vadd(u, vw)
F = (1.0, 2.0, 0.0)                    # foot of the perpendicular from the tip of u

U, V, W, E = bold("u"), bold("v"), bold("w"), bold("e")


def halo(x, y, s, color=TEXT, size=11.5, anchor="start", italic=False):
    """Text on a page-coloured halo, so faint grid, hatch and edge lines break around it."""
    st = ' font-style="italic"' if italic else ""
    P.add(f'<text x="{x:.1f}" y="{y:.1f}" fill="{color}" font-size="{size}" text-anchor="{anchor}"{st} '
          f'stroke="{BG}" stroke-width="3.4" stroke-linejoin="round" paint-order="stroke">{s}</text>')


def at(Q, s, dx=0, dy=0, color=TEXT, size=11.5, anchor="start", italic=False):
    """halo() at a space point, nudged by (dx, dy) pixels."""
    X, Y = S.pt(Q)
    halo(P.X(X) + dx, P.Y(Y) + dy, s, color, size, anchor, italic)


def tick(axis, val, dx, dy, anchor="middle", length=0.045):
    """One tick mark on a coordinate axis, its number written with a halo."""
    k = "xyz".index(axis)
    tdir = {"x": (0.0, 1.0, 0.0), "y": (1.0, 0.0, 0.0), "z": (1.0, 0.0, 0.0)}[axis]
    Q = [0.0, 0.0, 0.0]
    Q[k] = float(val)
    Q = tuple(Q)
    S.line([vadd(Q, vscale(-length, tdir)), vadd(Q, vscale(length, tdir))], TEXT, 1.0, None, 0.7)
    at(Q, fmt(val), dx, dy, TEXT, 10, anchor)


# 1. floor grid under the base ---------------------------------------------------------------
S.floor_grid((0, 3), (0, 3), n=3, opacity=0.11)

# 2. the six faces, painted back to front; the base carries its own hatching -------------------
BASE_FACE = (O, v, vw, w)
FACES = [BASE_FACE,
         (u, uv, uvw, uw),
         (O, v, uv, u),
         (w, vw, uvw, uw),
         (O, w, uw, u),
         (v, vw, uvw, uv)]
for face in sorted(FACES, key=lambda f: sum(S.depth(q) for q in f)):
    if face is BASE_FACE:
        S.polygon(face, PRACTICE, 0.13)
        for k in range(1, 8):                       # hatch parallel to w, spaced along v
            t = k / 8.0
            S.line([vscale(t, v), vadd(vscale(t, v), w)], PRACTICE, 0.75, None, 0.45)
    else:
        S.polygon(face, TEXT, 0.05)

# 3. edges: the nine that are not one of the three vectors --------------------------------------
for a, b in ((u, uv), (u, uw), (uv, uvw), (uw, uvw), (v, uv), (w, uw), (vw, uvw)):
    S.line([a, b], TEXT, 0.9, None, 0.42)
for a, b in ((v, vw), (vw, w)):                     # the two base edges opposite v and w
    S.line([a, b], PRACTICE, 1.4, None, 0.8)

# 4. axes and ticks ------------------------------------------------------------------------------
S.axes(3.3, 4.4, 3.3, offsets=((-4, 14), (10, 4), (-10, -4)))
# v runs along the x axis, so the x numbers go to the other side of it, into the base
for t in (1, 2, 3):
    tick("x", t, 6, 13)
tick("y", 1, -5, -7, "end")                         # clear of the green arrow at (1, 2, 0)
for t in (2, 3, 4):
    tick("y", t, 0, -8)
for t in (1, 2, 3):
    tick("z", t, -11, 4, "end")

# 5. the height: dashed perpendicular from the tip of u down to the base ------------------------
S.guide([u, F], TEXT, 0.6, 1.1)
S.point(F, TEXT, 2.6)

# 6. the three vectors, then the unit normal (which stands in front of the edge w) ---------------
S.arrow(O, v, PRACTICE, 2.4, head=9)
S.arrow(O, w, PRACTICE, 2.4, head=9)
S.arrow(O, u, THEORY, 2.4, head=9)
S.arrow(F, vadd(F, e), BASE, 2.3, head=7)
S.point(O, TEXT, 3.6)
S.point(u, TEXT, 2.8)

# 7. labels ---------------------------------------------------------------------------------------
at(u, U + " = (1, 2, 3)", 10, -13, THEORY, 12, "middle")
at(v, V + " = (2, 0, 0)", -10, -6, PRACTICE, 12, "end")
at(w, W + " = (1, 3, 0)", 9, 7, PRACTICE, 12, "start")
at(vadd(F, e), E + " = (0, 0, 1)", 9, 5, BASE, 12, "start")
at((1.0, 2.0, 2.0), U + " " + CDOT + " " + E + " = 3", 9, 4, TEXT, 12, "start")

# area of the base, written in its own colour just under the near edge of the hatching
halo(P.X(-0.45), P.Y(-1.92), "alan = " + DBAR + V + " " + TIMES_S + " " + W + DBAR + " = 6",
     PRACTICE, 11.5, "middle")

# the reading of the volume, in the free upper-left corner
halo(P.X(-2.38), P.Y(3.05), "hacim = alan " + CDOT + " yükseklik", TEXT, 12)
halo(P.X(-2.38), P.Y(2.74), "= 6 " + CDOT + " 3 = 18", TEXT, 12)

OUT["iccarpim-paralelyuz-hacmi"] = figure(
    432, 379, [P],
    "Kenarları <strong>u</strong> = (1, 2, 3), <strong>v</strong> = (2, 0, 0) ve "
    "<strong>w</strong> = (1, 3, 0) olan paralelyüzün tabanı, <em>xy</em> düzleminde duran taralı "
    "paralelkenardır; alanı &#8214;<strong>v</strong> &#215; <strong>w</strong>&#8214; = 6&#8217;dır. "
    "Taban düzlemine dik birim vektör <strong>e</strong> = (0, 0, 1) yeşil okla gösterilmiştir ve "
    "<strong>u</strong>&#8217;nun ucundan tabana inen kesikli dikme, yüksekliğin "
    "<strong>u</strong> &#183; <strong>e</strong> = 3 olduğunu okutur. Hacim taban alanı ile "
    "yüksekliğin çarpımıdır: 6 &#183; 3 = 18 = <strong>u</strong> &#183; <strong>v</strong> "
    "&#215; <strong>w</strong>.",
    aria="Parallelepiped at the origin with edges u = (1, 2, 3) in blue, v = (2, 0, 0) and "
         "w = (1, 3, 0) in orange; its base is the hatched parallelogram with corners (0,0,0), "
         "(2,0,0), (3,3,0), (1,3,0) in the xy plane, of area ||v x w|| = 6; a green unit normal "
         "e = (0, 0, 1) stands on the dashed perpendicular dropped from the tip of u to the base, "
         "whose length is u . e = 3; volume = 6 . 3 = 18",
)

# ============================================================ iccarpim-uzaklik-kutusu
# -*- coding: utf-8 -*-
# iccarpim-uzaklik-kutusu: the distance d(p, q) = 13 between p = (1, 2, 0) and q = (4, 6, 12)
# read off the axis-parallel box whose opposite corners are p and q.
# Dashed box (edges 3, 4, 12), orange dashed base diagonal (5) and thick blue space diagonal (13);
# the two Pythagoras triangles p-a-c (floor) and p-c-q (standing) are tinted and their right
# angles marked at a = (4, 2, 0) and c = (4, 6, 0).
# Camera: elevation 30 opens the floor rectangle enough to keep the labels 3, 4 and 5 clear of
# its edges; azimuth 35 pushes the box's left vertical edge away from the z axis (at azimuth 30
# the two run 8 px apart and read as one double line).
import math

P = space_panel(25, 20, 300, (-3.45, 6.55), (-3.6, 11.3))
S = Space(P, Camera(azimuth=35, elevation=30, scale=1.0))

p = (1.0, 2.0, 0.0)
q = (4.0, 6.0, 12.0)
a = (4.0, 2.0, 0.0)          # p + (3, 0, 0)
c = (4.0, 6.0, 0.0)          # a + (0, 4, 0): the foot of q
b = (1.0, 6.0, 0.0)
pz = (1.0, 2.0, 12.0)        # p + (0, 0, 12)
qa = (4.0, 2.0, 12.0)
qb = (1.0, 6.0, 12.0)

mid_pa = (2.5, 2.0, 0.0)
mid_ac = (4.0, 4.0, 0.0)
mid_cq = (4.0, 6.0, 6.0)
mid_pc = (2.5, 4.0, 0.0)
on_pq = (3.25, 5.0, 9.0)     # 75 % of the way from p to q, where the box is widest


def txt(Q, s, dx=0.0, dy=0.0, color=TEXT, size=11.5, anchor="middle"):
    """Label at a space point with a page-coloured halo, so grid lines behind it break."""
    X, Y = S.pt(Q)
    P.add(f'<text x="{P.X(X) + dx:.1f}" y="{P.Y(Y) + dy:.1f}" fill="{color}" font-size="{size}" '
          f'text-anchor="{anchor}" stroke="{BG}" stroke-width="2.4" stroke-linejoin="round" '
          f'paint-order="stroke">{s}</text>')


def right_angle(C, u, v, L=0.52):
    """Corner mark at C along the directions u and v, both legs L units long *on the page*."""
    def leg(d):
        d = vunit(d)
        (X0, Y0), (X1, Y1) = S.pt(C), S.pt(vadd(C, d))
        return vscale(L / math.hypot(X1 - X0, Y1 - Y0), d)
    u, v = leg(u), leg(v)
    S.line([vadd(C, u), vadd(C, vadd(u, v)), vadd(C, v)], TEXT, 1.0, None, 0.75)


# 1. floor grid on the integer lines under the box
for i in range(5):
    S.line([(i, 0.0, 0.0), (i, 6.0, 0.0)], TEXT, 0.7, None, 0.10)
for j in range(7):
    S.line([(0.0, j, 0.0), (4.0, j, 0.0)], TEXT, 0.7, None, 0.10)

# 2. the two right triangles of the calculation: 3-4-5 on the floor, 5-12-13 standing up
S.polygon([p, a, c], PRACTICE, 0.14)
S.polygon([p, c, q], THEORY, 0.10)

# 3. axes and ticks (y labels to the right of the axis: p sits right next to y = 2)
S.axes(5.0, 7.2, 12.6)
S.ticks("x", (1, 2, 3, 4))
S.ticks("y", (2, 4, 6), offset=(10, 4))
S.ticks("z", (4, 8, 12))

# 4. the box: all twelve edges dashed, the three measured ones a shade stronger
for edge in ([p, a, c, b, p], [pz, qa, q, qb, pz], [p, pz], [a, qa], [b, qb]):
    S.guide(edge, TEXT, 0.38)
S.guide([p, a], TEXT, 0.8, 1.3)
S.guide([a, c], TEXT, 0.8, 1.3)
S.guide([c, q], TEXT, 0.8, 1.3)

# only the floor right angle is marked: at c the two legs meet at 33 degrees on the page and the
# corner mark degenerates into a zigzag, while the vertical edge already reads as perpendicular
right_angle(a, vsub(p, a), vsub(c, a))

# 5. the two diagonals
S.line([p, c], PRACTICE, 2.0, "6 4")
S.line([p, q], THEORY, 2.8)

# 6. corners
S.point(a, TEXT, 2.4)
S.point(c, TEXT, 2.4)
S.point(p, TEXT, 4.2)
S.point(q, TEXT, 4.2)

# 7. edge and diagonal lengths, each beside its own segment
txt(mid_pa, "3", -7, -9, TEXT, 12)
txt(mid_ac, "4", -5, 14, TEXT, 12)
txt(mid_cq, "12", 9, 4, TEXT, 12, "start")
txt(mid_pc, "5", -11, 7, PRACTICE, 12.5)      # inside the 3-4-5 triangle, on its hypotenuse
txt(on_pq, "13", -7, 4, THEORY, 12.5, "end")

# 8. the two points: q's coordinates fit inside the top face, p's go in the left margin
txt(p, bold("p"), -8, -2, TEXT, 12.5, "end")
txt(q, bold("q") + " = (4, 6, 12)", -18, -26, TEXT, 11.5)
P.label(-0.95, 0.8, bold("p") + " = (1, 2, 0)", 0, 0, TEXT, 11.5, "end")

# 9. the two Pythagoras steps, in the empty column left of the z axis
P.label(-0.95, 5.6, "3" + sups("2") + " + 4" + sups("2") + " = 5" + sups("2"),
        0, 0, PRACTICE, 11, "end")
P.label(-0.95, 4.65, "5" + sups("2") + " + 12" + sups("2") + " = 13" + sups("2"),
        0, 0, THEORY, 11, "end")

OUT["iccarpim-uzaklik-kutusu"] = figure(
    350, 487, [P],
    "<strong>p</strong> = (1, 2, 0) ile <strong>q</strong> = (4, 6, 12), kenarları koordinat "
    "eksenlerine paralel olan kesikli kutunun karşılıklı iki köşesidir; kenar uzunlukları "
    "koordinat farkları 3, 4 ve 12&#8217;dir. Tabandaki turuncu köşegen Pisagor&#8217;la "
    "3<sup>2</sup> + 4<sup>2</sup> = 5<sup>2</sup> hesabından 5 çıkar; bu 5 ile 12 yüksekliği "
    "yeni bir dik üçgen kurduğundan kutunun mavi köşegeni 5<sup>2</sup> + 12<sup>2</sup> = "
    "13<sup>2</sup> hesabından 13 olur. Uzaklık formülü bu iki Pisagor adımını tek karekökte "
    "birleştirir: <em>d</em>(<strong>p</strong>, <strong>q</strong>) = 13.",
    aria="Rectangular box with axis-parallel edges whose opposite corners are p = (1, 2, 0) and "
         "q = (4, 6, 12); dashed edges of lengths 3, 4 and 12, an orange dashed base diagonal of "
         "length 5 and a thick blue space diagonal of length 13; the right triangles 3-4-5 on the "
         "floor and 5-12-13 standing on it are tinted",
)

# ============================================================ iccarpim-vektorel-carpim
# -*- coding: utf-8 -*-
# iccarpim-vektorel-carpim: the cross product of the example, drawn at the origin.
# v = (2, 1, 0) (blue, lies in the floor z = 0) and w = (0, 3, 1) (orange, one unit above the
# floor) span the hatched parallelogram 0, v, v + w = (2, 4, 1), w, of area sqrt(41); the normal
# v x w = (1, -2, 6) (green, thick) carries the same length sqrt(41). Two right-angle marks at the
# origin show v . (v x w) = 0 and w . (v x w) = 0, each in the colour of its own vector; the small
# curved arrow turns v into w, the right-hand rule that fixes the direction of the green arrow.
# The y ticks 1 and 2 are dropped: the projected y axis runs through the patch and their labels
# would land on the hatching next to 'alan'.
# Camera: azimuth 45 keeps v clear of the projected x axis (30 deg) and n clear of the z axis
# (22 deg); elevation 38 is above the API's 15-30 band on purpose — below ~32 the parallelogram is
# seen almost edge on (foreshortening 0.34) and neither the hatching nor the area label fits in it,
# while at 38 the patch opens to 0.49 of its true area and v is still 1.5 units long on the page.
import math

AZ, EL = 45.0, 38.0
AXX, AXY, AXZ = 3.0, 4.4, 6.6

O = (0.0, 0.0, 0.0)
v = (2.0, 1.0, 0.0)
w = (0.0, 3.0, 1.0)
n = vcross(v, w)                     # (1, -2, 6)
vw = vadd(v, w)                      # (2, 4, 1)
PARA = [O, v, vw, w]

P = space_panel(16, 14, 372, (-3.45, 4.05), (-2.75, 5.65))
S = Space(P, Camera(azimuth=AZ, elevation=EL, scale=1.0))

SQ = "&#8730;"                       # square root
DBAR = "&#8214;"                     # double bar for the norm
V, W = bold("v"), bold("w")
N = V + " " + TIMES_S + " " + W


def halo(px_, py_, s, color=TEXT, size=11.5, anchor="start"):
    """Text at a pixel position with a page-coloured halo, so faint lines behind it break."""
    P.add(f'<text x="{px_:.1f}" y="{py_:.1f}" fill="{color}" font-size="{size}" '
          f'text-anchor="{anchor}" stroke="{BG}" stroke-width="3.4" stroke-linejoin="round" '
          f'paint-order="stroke">{s}</text>')


def tag(Q, s, dx=0, dy=0, color=TEXT, size=11.5, anchor="start"):
    """Halo text hung on a space point."""
    X, Y = S.pt(Q)
    halo(P.X(X) + dx, P.Y(Y) + dy, s, color, size, anchor)


def hatch(poly, angle_deg, color=TEXT, step_px=7.5, width=0.8, opacity=0.38):
    """Parallel hatch lines at angle_deg (page), clipped to a convex polygon in panel data units."""
    a = math.radians(angle_deg)
    d = (math.cos(a), math.sin(a))
    nrm = (-d[1], d[0])
    step = step_px * (P.xmax - P.xmin) / P.w
    proj = [nrm[0] * x + nrm[1] * y for x, y in poly]
    lo, hi = min(proj), max(proj)
    count = max(1, int((hi - lo) / step))
    c0 = lo + (hi - lo - (count - 1) * step) / 2.0
    parts = []
    for i in range(count):
        c = c0 + i * step
        hits = []
        for j in range(len(poly)):
            (x0, y0), (x1, y1) = poly[j], poly[(j + 1) % len(poly)]
            s0 = nrm[0] * x0 + nrm[1] * y0 - c
            s1 = nrm[0] * x1 + nrm[1] * y1 - c
            if (s0 < 0) != (s1 < 0):
                t = s0 / (s0 - s1)
                hits.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t))
        if len(hits) >= 2:
            hits.sort(key=lambda q: d[0] * q[0] + d[1] * q[1])
            parts.append(f"M{P.P(*hits[0])} L{P.P(*hits[-1])}")
    P.add(f'<path d="{" ".join(parts)}" fill="none" stroke="{color}" stroke-width="{width}" '
          f'opacity="{opacity}" stroke-linecap="butt"/>')


def right_angle(a, b, s=0.32, color=TEXT, width=1.1, opacity=0.9):
    """Right-angle mark at the origin, a true square in the plane of a and b (both drawn from the
    origin). The two marks share their edge along b = v x w, so in one grey they closed up into a
    hexagonal collar around the green arrow; each therefore takes the colour of its own vector."""
    ea, eb = vscale(s, vunit(a)), vscale(s, vunit(b))
    S.line([ea, vadd(ea, eb), eb], color, width, None, opacity)


# ---------------------------------------------------------------- 1. floor and axes
for gx in range(0, 4):
    S.line([(gx, 0, 0), (gx, 3, 0)], TEXT, 0.7, None, 0.09)
for gy in range(0, 4):
    S.line([(0, gy, 0), (3, gy, 0)], TEXT, 0.7, None, 0.09)

S.axes(AXX, AXY, AXZ, offsets=((-7, -8), (11, 5), (-10, -4)))
S.ticks("x", (1, 2))
S.ticks("y", (3, 4))          # 1 and 2 would fall inside the parallelogram
S.ticks("z", (2, 4, 6))

# ---------------------------------------------------------------- 2. the parallelogram
POLY = S.pts(PARA)
P.polygon(POLY, TEXT, 0.07, "none")
hatch(POLY, 25.0)
S.guide([v, vw, w], TEXT, 0.55, 1.1)          # the two far edges, the near ones are the arrows
S.drop(w)                                      # w stands one unit above the floor

# ---------------------------------------------------------------- 3. right angles and the turn
right_angle(v, n, color=THEORY)
right_angle(w, n, 0.28, color=PRACTICE)

e1 = vunit(v)
e2 = vunit(vsub(w, vscale(vdot(w, e1), e1)))
TH = math.acos(vdot(v, w) / (vnorm(v) * vnorm(w)))
R = 1.15
T0, T1 = 0.10 * TH, 0.90 * TH                  # short of both arrows, so nothing touches


def turn(t):
    return vadd(vscale(R * math.cos(t), e1), vscale(R * math.sin(t), e2))


S.curve(turn, T0, T1, BG, 3.0, 48)             # halo, so the hatching breaks under the arc
S.segment_arrow(turn, T0, T1, BASE, 1.5, 7.0, 48)

# ---------------------------------------------------------------- 4. the three vectors
S.arrow(O, v, THEORY, 2.4, head=9)
S.arrow(O, w, PRACTICE, 2.4, head=9)
S.arrow(O, n, BASE, 2.8, head=10)
S.point(O, TEXT, 3.4)

# ---------------------------------------------------------------- 5. labels
tag(O, bold("p"), -24, 3, TEXT, 12, "end")
tag(v, V + " = (2, 1, 0)", -8, 24, THEORY, 12, "end")
tag(w, W + " = (0, 3, 1)", 9, 5, PRACTICE, 12, "start")
tag(vw, V + " + " + W + " = (2, 4, 1)", 0, 16, TEXT, 11.5, "middle")

tag(n, N + " = (1, " + MINUS_S + "2, 6)", 0, -13, BASE, 12, "middle")
tag(vscale(0.45, n), DBAR + N + DBAR + " = " + SQ + "41", -8, 4, BASE, 11.5, "end")

# labels placed by hand in the free parts of the page: the area inside the hatched patch,
# the right-hand rule just above the w edge next to the turn, the two orthogonality checks
# in the open region to the right of the z axis
halo(P.X(0.96), P.Y(-0.97), "alan = " + SQ + "41", TEXT, 11.5, "middle")
halo(P.X(0.95), P.Y(0.33), "sağ el kuralı", BASE, 11.5, "middle")
halo(P.X(0.25), P.Y(2.95), V + " " + CDOT + " (" + N + ") = 2 " + MINUS_S + " 2 + 0 = 0", TEXT, 11.5)
halo(P.X(0.25), P.Y(2.55), W + " " + CDOT + " (" + N + ") = 0 " + MINUS_S + " 6 + 6 = 0", TEXT, 11.5)

OUT["iccarpim-vektorel-carpim"] = figure(
    400, 470, [P],
    "Uygulama noktası <strong>p</strong> orijinde alınmıştır; oradan çıkan "
    "<strong>v</strong> = (2, 1, 0) (mavi) ile <strong>w</strong> = (0, 3, 1) (turuncu) taralı "
    "paralelkenarı gerer. Vektörel çarpım <strong>v</strong> &#215; <strong>w</strong> = "
    "(1, &#8722;2, 6) (yeşil) bu paralelkenarın düzlemine diktir: iki dik açı işareti, "
    "<strong>v</strong> &#183; (<strong>v</strong> &#215; <strong>w</strong>) = 0 ve "
    "<strong>w</strong> &#183; (<strong>v</strong> &#215; <strong>w</strong>) = 0 hesaplarının "
    "geometrik karşılığıdır. Okun yönünü sağ el kuralı belirler: <strong>v</strong>&#8217;den "
    "<strong>w</strong>&#8217;ye dönülürken başparmak <strong>v</strong> &#215; "
    "<strong>w</strong> yönünü gösterir. Okun uzunluğu &#8214;<strong>v</strong> &#215; "
    "<strong>w</strong>&#8214; = &#8730;41, paralelkenarın alanına eşittir.",
    aria="Uzayda orijinden cikan mavi v = (2, 1, 0) ve turuncu w = (0, 3, 1) oklari taranmis bir "
         "paralelkenar gerer; paralelkenara dik yesil ok v x w = (1, -2, 6) olup uzunlugu "
         "karekok 41'dir; orijindeki iki dik aci isareti v ve w ile bu okun dikligini, kavisli "
         "ok ise v den w ye donusu, yani sag el kuralini gosterir",
)

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

# ============================================================ keyfi-koni-egrisi
# -*- coding: utf-8 -*-
# keyfi-koni-egrisi — the curve alpha(t) = (t cos t, t sin t, t) on the double cone x^2 + y^2 = z^2,
# with the Frenet frame at the vertex alpha(0) = (0, 0, 0).
#
# From the exercise box: alpha'(0) = (1, 0, 1), alpha''(0) = (0, 2, 0), alpha'''(0) = (-3, 0, 0),
# so v(0) = sqrt2, alpha' x alpha'' = (-2, 0, 2), kappa(0) = 1, tau(0) = 3/4 and
#   T(0) = (1, 0, 1)/sqrt2,  N(0) = (0, 1, 0),  B(0) = (-1, 0, 1)/sqrt2.
# Checks done by hand for this drawing: T . N = 0, B = T x N, and T is the direction the curve
# leaves the vertex in (alpha'(0) = sqrt2 T). T lies along the cone generator u = 0 and B along
# u = pi; N is horizontal, so it is the only one of the three that leaves the cone at once.
# The three unit vectors are drawn 2 units long (said in the caption) — at this scale, where the
# cone is 2pi = 6.28 units wide, a unit arrow would be 30 px and its head would swallow the shaft.
#
# Depth: the cone's near face is |u - az| < acos(tan el) on the upper nappe and |u - az| <
# acos(-tan el) on the lower one, so the curve is cut into near/far runs; the far runs go in
# before the surface and stay pale, the near runs after it, each with a page-coloured halo that
# breaks the grid beneath. B points away from the viewer (it is a generator of the back of the
# cone) so it is drawn before the near curve and the curve crosses over it; T and N come toward
# the viewer and are drawn last.
# Camera az = 40, el = 20: the upper end alpha(2pi) = (2pi, 0, 2pi) then lands on the near face and
# the free wedges left and right of the two nappes (nothing of the cone projects into a band of
# +-41 deg about the horizon) carry the axes and all the text.
import math

AZ, EL = 40.0, 20.0
PHI = math.radians(AZ)
TAN_EL = math.tan(math.radians(EL))
TWO_PI = 2.0 * math.pi
SQ2 = math.sqrt(2.0)
CAM = Camera(azimuth=AZ, elevation=EL, scale=1.0)
AXX, AXY, AXZ = 7.0, 7.0, 7.2          # axis ends (z is drawn both ways)
VLEN = 2.0                             # drawn length of T, N, B

SQRT_S, KAPPA_S, TAU_S = "&#8730;", "&#954;", "&#964;"


def alpha(t):
    return (t * math.cos(t), t * math.sin(t), t)


def cone(u, w):
    """The double cone x^2 + y^2 = z^2: radius |w| at height w."""
    r = abs(w)
    return (r * math.cos(u), r * math.sin(u), w)


def faces_viewer(t):
    """True when alpha(t) sits on the half of the cone that faces the camera."""
    x, y, z = alpha(t)
    if x == 0.0 and y == 0.0:
        return True
    c = math.cos(math.atan2(y, x) - PHI)
    return c > TAN_EL if z > 0 else c > -TAN_EL


def spans(front, n=1600):
    """Parameter intervals on which the curve stays on the near (front=True) or far half."""
    ts = [-TWO_PI + 2 * TWO_PI * k / n for k in range(n + 1)]
    out, start = [], None
    for i, t in enumerate(ts):
        if faces_viewer(t) == front:
            if start is None:
                start = ts[i - 1] if i else t
        elif start is not None:
            out.append((start, t))
            start = None
    if start is not None:
        out.append((start, ts[-1]))
    return out


def poly(t0, t1, n=240):
    return [alpha(t0 + (t1 - t0) * k / n) for k in range(n + 1)]


def proj(P):
    X, Y, _ = CAM.project(P)
    return X, Y


# --- panel: the projected bounding box of cone, curve and axes ---------------------------------
box = [proj(cone(TWO_PI * k / 120, w)) for k in range(121) for w in (TWO_PI, -TWO_PI)]
box += [proj(alpha(-TWO_PI + 2 * TWO_PI * k / 240)) for k in range(241)]
box += [proj((AXX, 0, 0)), proj((0, AXY, 0)), proj((0, 0, AXZ)), proj((0, 0, -AXZ))]
X0, X1 = min(b[0] for b in box), max(b[0] for b in box)
Y0, Y1 = min(b[1] for b in box), max(b[1] for b in box)
PAD_L, PAD_R, PAD_B, PAD_T = 0.30, 0.30, 1.30, 1.00
PW = 470
SP = space_panel(30, 30, PW, (X0 - PAD_L, X1 + PAD_R), (Y0 - PAD_B, Y1 + PAD_T))
S = Space(SP, CAM)


def ital(s):
    return '<tspan font-style="italic">' + s + "</tspan>"


def halo_px(x, y, s, color=TEXT, size=11.0, anchor="start", opacity=1.0, halo=True):
    """Text at a pixel position, with a page-coloured outline so faint lines break behind it."""
    op = f' opacity="{opacity}"' if opacity < 1.0 else ""
    h = (f' stroke="{BG}" stroke-width="3.4" stroke-linejoin="round" paint-order="stroke"'
         if halo else "")
    SP.add(f'<text x="{x:.1f}" y="{y:.1f}" fill="{color}" font-size="{size}" '
           f'text-anchor="{anchor}"{op}{h}>{s}</text>')


def at(X, Y, s, color=TEXT, size=11.0, anchor="start", opacity=1.0, halo=True):
    """Halo text at a point of the projected plane (the panel's own coordinates)."""
    halo_px(SP.X(X), SP.Y(Y), s, color, size, anchor, opacity, halo)


def tag(P, s, dx=0, dy=0, color=TEXT, size=11.0, anchor="start"):
    """Halo text hung on a space point."""
    X, Y = S.pt(P)
    halo_px(SP.X(X) + dx, SP.Y(Y) + dy, s, color, size, anchor)


def haloed_arrow(P0, P1, color, width=2.6, head=9.5, halo=3.4):
    """A space arrow on a cleared strip, so the cone's grid does not run through it."""
    S.line([P0, P1], BG, width + halo)
    S.arrow(P0, P1, color, width, head)


PPU = PW / (SP.xmax - SP.xmin)          # pixels per projected unit


def trimmed(pts, px=3.6):
    """The polyline shortened by px at both ends — used for the curve's halo, so the white
    strip stops short of the joins with the far runs instead of biting into them."""
    def cut(seq):
        x0, y0 = S.pt(seq[0])
        i = 0
        while i < len(seq) - 2:
            x, y = S.pt(seq[i])
            if math.hypot(x - x0, y - y0) * PPU >= px:
                break
            i += 1
        return seq[i:]
    return list(reversed(cut(list(reversed(cut(pts))))))


# --- 1. the parts of the curve that run behind the cone ---------------------------------------
# far runs reach a little past their ends, so the near runs' halos cover the join
FAR = [poly(max(-TWO_PI, a - 0.07), min(TWO_PI, b + 0.07)) for a, b in spans(False)]
NEAR = [poly(a, b) for a, b in spans(True)]
for r in FAR:
    S.line(r, THEORY, 2.0, None, 0.42)

# --- 2. the cone, its two rims, then the axes -------------------------------------------------
# u starts at 7.5 deg so that no grid generator falls on u = 0 or u = pi, where T and B lie
S.surface(cone, (math.pi / 24, TWO_PI + math.pi / 24), (-TWO_PI, TWO_PI), nu=24, nv=12,
          fill=TEXT, stroke=TEXT, opacity=(0.012, 0.055), stroke_width=0.55, stroke_opacity=0.20)
for w in (TWO_PI, -TWO_PI):
    S.circle((0, 0, w), (1, 0, 0), (0, 1, 0), abs(w), TEXT, 0.9, None, 96, 0.45)

S.axes(AXX, AXY, AXZ, zmin=-AXZ, offsets=((-5, 14), (11, 5), (-11, -4)))
S.ticks("x", (2, 4, 6), offset=(-6, 16))   # the x axis runs down-left; keep its numbers off it

# --- 3. the binormal: it points into the back of the cone, so the curve passes in front of it --
B0 = vscale(VLEN / SQ2, (-1.0, 0.0, 1.0))
haloed_arrow((0, 0, 0), B0, TEXT)

# --- 4. the near parts of the curve, the direction of travel, the starting point ---------------
for r in NEAR:
    S.line(trimmed(r), BG, 5.4)
for r in NEAR:
    S.line(r, THEORY, 2.4)
S.arrow(alpha(TWO_PI - 0.20), alpha(TWO_PI), THEORY, 2.4, head=10)   # travel direction at t = 2pi
S.arrow(alpha(-2.25), alpha(-1.95), THEORY, 2.4, head=9.5)
S.point(alpha(-TWO_PI), THEORY, 3.4)

# --- 5. tangent and normal: both point toward the viewer, so they go on top --------------------
T0 = vscale(VLEN / SQ2, (1.0, 0.0, 1.0))
N0 = (0.0, VLEN, 0.0)
haloed_arrow((0, 0, 0), N0, BASE)
# T gets only a hairline halo: the curve leaves the vertex along T, and a wide cleared strip
# would rub out exactly the piece of curve that shows the tangency
haloed_arrow((0, 0, 0), T0, PRACTICE, halo=1.0)
S.point((0, 0, 0), TEXT, 3.0)

# --- 6. labels --------------------------------------------------------------------------------
tag(T0, bold("T"), -6, -5, PRACTICE, 12.5)
tag(N0, bold("N"), 7, -7, BASE, 12.5)
tag(B0, bold("B"), 5, -6, TEXT, 12.5)
# the vertex's name goes into the open wedge between the x axis and T, far enough out that
# neither line reaches it
tag((0, 0, 0), ital("&#945;") + "(0)", -26, 4, TEXT, 11, "end")

# the two ends of the curve
tag(alpha(TWO_PI), ital("&#945;") + "(2" + PI_S + ") = (2" + PI_S + ", 0, 2" + PI_S + ")",
    -7, 20, TEXT, 11, "middle")
at(3.78, -5.22, ital("&#945;") + "(" + MINUS_S + "2" + PI_S + ") = ("
   + MINUS_S + "2" + PI_S + ", 0, " + MINUS_S + "2" + PI_S + ")", TEXT, 11, "middle")
SP.add(f'<path d="M{SP.X(3.95):.1f},{SP.Y(-4.45):.1f} L{SP.X(3.83):.1f},{SP.Y(-4.95):.1f}" '
       f'fill="none" stroke="{TEXT}" stroke-width="0.9" opacity="0.5"/>')

# the curve's name, on the free side of its far stretch across the top
tag(alpha(4.2), ital("&#945;"), 0, 15, THEORY, 12.5, "middle")

# the apparatus at t = 0, in the open wedge left of the two nappes
LX = X0 - PAD_L + 0.25
at(LX, 2.45, ital("&#945;") + "(0) = (0, 0, 0)", TEXT, 11.5, halo=False)
at(LX, 1.83, bold("T") + "(0) = (1, 0, 1)/" + SQRT_S + "2", PRACTICE, 11.5, halo=False)
at(LX, 1.21, bold("N") + "(0) = (0, 1, 0)", BASE, 11.5, halo=False)
at(LX, 0.59, bold("B") + "(0) = (" + MINUS_S + "1, 0, 1)/" + SQRT_S + "2", TEXT, 11.5, halo=False)
at(LX, -0.20, ital("t") + " = 0: " + KAPPA_S + " = 1, " + TAU_S + " = 3/4", TEXT, 11.5, halo=False)

# titles in the free band above the cone
at(LX, Y1 + 0.55, ital("x") + sups("2") + " + " + ital("y") + sups("2") + " = " + ital("z")
   + sups("2"), TEXT, 11.5, opacity=0.85, halo=False)
at(X1 + 0.25, Y1 + 0.55, ital("&#945;") + "(" + ital("t") + ") = (" + ital("t") + " cos "
   + ital("t") + ", " + ital("t") + " sin " + ital("t") + ", " + ital("t") + ")",
   THEORY, 11.5, "end", halo=False)

OUT["keyfi-koni-egrisi"] = figure(
    int(PW + 60), int(SP.h + 60), [SP],
    "<em>x</em><sup>2</sup> + <em>y</em><sup>2</sup> = <em>z</em><sup>2</sup> çift konisi (gri "
    "ızgara) ve üzerinde kalan <em>&#945;</em>(<em>t</em>) = (<em>t</em> cos <em>t</em>, "
    "<em>t</em> sin <em>t</em>, <em>t</em>) eğrisi, &#8722;2&#960; &#8804; <em>t</em> &#8804; "
    "2&#960; (mavi; koninin arkasından geçen parçalar soluk çizilmiştir). Eğri alt koniden "
    "gelip tepeden geçer ve üst koniye çıkar; tepe koni için bir tekillik olsa da eğri orada "
    "düzgündür, çünkü <em>&#945;</em>&#8242;(0) = (1, 0, 1) &#8800; <strong>0</strong>. "
    "Tepeden çıkan üç ok <em>t</em> = 0 anındaki Frenet çatısıdır: <strong>T</strong> (turuncu) "
    "eğriye teğettir, <strong>N</strong> (yeşil) eğrinin döndüğü yana bakar, <strong>B</strong> "
    "= <strong>T</strong> &#215; <strong>N</strong> (koyu) ikisine de diktir. Üçü de birim "
    "vektördür, görünürlük için 2 birim uzunlukta çizilmiştir; eğrilik orada &#954; = 1 olduğu "
    "için eğri, tepeden ayrılır ayrılmaz <strong>T</strong> doğrultusundan sapıp "
    "<strong>N</strong> yönüne döner.",
    aria="Cift koni x^2 + y^2 = z^2 ve uzerindeki alpha(t) = (t cos t, t sin t, t) egrisi, t "
         "-2pi ile 2pi arasinda; egri alt koniden gelip tepeden gecer ve ust koniye cikar, uclari "
         "alpha(-2pi) = (-2pi, 0, -2pi) ve alpha(2pi) = (2pi, 0, 2pi); tepeden, yani "
         "alpha(0) = (0, 0, 0) noktasindan cikan uc ok t = 0 anindaki Frenet catisidir: turuncu "
         "T(0) = (1, 0, 1)/karekok 2, yesil N(0) = (0, 1, 0), koyu B(0) = (-1, 0, 1)/karekok 2; "
         "o anda kappa = 1 ve tau = 3/4")

# ============================================================ keyfi-kubik-aparat
# -*- coding: utf-8 -*-
# keyfi-kubik-aparat: alpha(t) = (3t - t^3, 3t^2, 3t + t^3) on [-1.5, 1.5] with the Frenet
# apparatus of the worked example at t = 1: alpha(1) = (2, 3, 4), T = (0, 1, 1)/sqrt2 (orange,
# tangent), N = (-1, 0, 0) (green), B = (0, -1, 1)/sqrt2 (dark), each drawn 2 units long, and
# the 2 x 2 osculating patch spanned by T and N hatched in the tangent's colour.
#
# Camera.  Three things fight here, and only a narrow band of views survives all of them
# (the search is in _probe_keyfi_kubik_aparat*.py):
#   * every unit tangent of this curve has T_z = 1/sqrt2, so all of them lie on the 45 degree
#     cone about the z axis and an elevation near 45 projects a piece of the curve onto a cusp;
#   * the osculating plane is seen edge on from low down, and with it the right angle between
#     T and N collapses — at the elevations the API recommends (15-30) the projected T and N
#     are less than 25 degrees apart, which would make the drawing say the opposite of the text;
#   * B(1) points from alpha(1) back across the origin, so in most views the B arrow and the
#     y axis fall on the same page line.
# At az = 40, el = 72 the page angles are T-N 70, N-B 81, T-B 151 degrees, the patch keeps 0.53
# of its area, the worst foreshortening along the curve is 0.45, the y axis clears every arrow
# as far as y = 1.4, and the drawing comes out square.  The curve leaves the origin along
# (1, 0, 1), which from this height is only 15 degrees off the x axis, so the two run together
# for the first few pixels; the curve is painted over the axis there.
#
# Depth.  For t < 0 the curve hangs below the floor z = 0 and is drawn lighter.  It crosses the
# patch, the N arrow and the rising branch, so the rising branch and the three frame arrows are
# laid on a background-coloured halo and read as being in front — which is what they are.
import math

AZ, EL = 40.0, 72.0
R2 = math.sqrt(2.0)
T0, T1 = -1.5, 1.5
AXX, AXY, AXZ = 2.8, 1.4, 6.0            # the y axis stops at 1.4: any longer and it runs into
                                         # the N arrow and then into the osculating patch

A1 = (2.0, 3.0, 4.0)                     # alpha(1)
TV = (0.0, 1 / R2, 1 / R2)               # T(1)
NV = (-1.0, 0.0, 0.0)                    # N(1)
BV = (0.0, -1 / R2, 1 / R2)              # B(1) = T(1) x N(1)
LEN = 2.0                                # the unit vectors are drawn twice as long

SQ = "&#8730;"
KAPPA, TAU = "&#954;", "&#964;"
IT_A = '<tspan font-style="italic">&#945;</tspan>'
IT_T = '<tspan font-style="italic">t</tspan>'


def alpha(t):
    return (3 * t - t ** 3, 3 * t * t, 3 * t + t ** 3)


P = space_panel(20, 18, 360, (-2.2, 6.3), (-6.1, 2.4))
S = Space(P, Camera(azimuth=AZ, elevation=EL, scale=1.0))

TIP = {k: vadd(A1, vscale(LEN, v)) for k, v in (("T", TV), ("N", NV), ("B", BV))}
CORNER = vadd(A1, vadd(vscale(LEN, TV), vscale(LEN, NV)))


def halo(px, py, s, color=TEXT, size=11.5, anchor="start", ring=True):
    """Text at a pixel position, by default with a page-coloured halo so lines behind it break.

    The halo is dropped where the text carries a superscript: rsvg loses the ascender of an
    italic letter that a raised tspan follows once the run is stroked."""
    stroke = (f'stroke="{BG}" stroke-width="3.4" stroke-linejoin="round" paint-order="stroke" '
              if ring else "")
    P.add(f'<text x="{px:.1f}" y="{py:.1f}" fill="{color}" font-size="{size}" '
          f'text-anchor="{anchor}" {stroke}>{s}</text>')


def tag(Q, s, dx=0, dy=0, color=TEXT, size=11.5, anchor="start"):
    """Halo text hung on a space point."""
    X, Y = S.pt(Q)
    halo(P.X(X) + dx, P.Y(Y) + dy, s, color, size, anchor)


def at(x, y, s, color=TEXT, size=11.5, anchor="start", ring=True):
    """Text at a panel position (page coordinates of the projection)."""
    halo(P.X(x), P.Y(y), s, color, size, anchor, ring)


def italic(s):
    return f'<tspan font-style="italic">{s}</tspan>'


def hatch(poly, angle_deg, color=TEXT, step_px=8.0, width=0.8, opacity=0.36):
    """Parallel hatch lines at angle_deg (page), clipped to a convex polygon in panel units."""
    a = math.radians(angle_deg)
    d = (math.cos(a), math.sin(a))
    nrm = (-d[1], d[0])
    step = step_px * (P.xmax - P.xmin) / P.w
    proj = [nrm[0] * x + nrm[1] * y for x, y in poly]
    lo, hi = min(proj), max(proj)
    count = max(1, int((hi - lo) / step))
    c0 = lo + (hi - lo - (count - 1) * step) / 2.0
    parts = []
    for i in range(count):
        c = c0 + i * step
        hits = []
        for j in range(len(poly)):
            (x0, y0), (x1, y1) = poly[j], poly[(j + 1) % len(poly)]
            s0 = nrm[0] * x0 + nrm[1] * y0 - c
            s1 = nrm[0] * x1 + nrm[1] * y1 - c
            if (s0 < 0) != (s1 < 0):
                t = s0 / (s0 - s1)
                hits.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t))
        if len(hits) >= 2:
            hits.sort(key=lambda q: d[0] * q[0] + d[1] * q[1])
            parts.append(f"M{P.P(*hits[0])} L{P.P(*hits[-1])}")
    P.add(f'<path d="{" ".join(parts)}" fill="none" stroke="{color}" stroke-width="{width}" '
          f'opacity="{opacity}" stroke-linecap="butt"/>')


# ---------------------------------------------------------------- 1. the floor
S.floor_grid((-1, 2), (0, 3), n=3, opacity=0.10)

# ---------------------------------------------------------------- 2. the curve below the floor
S.curve(alpha, T0, 0.0, THEORY, 2.2, 240, None, 0.45)

# ---------------------------------------------------------------- 3. the osculating patch
POLY = S.pts([A1, TIP["T"], CORNER, TIP["N"]])
P.polygon(POLY, PRACTICE, 0.10, "none")
hatch(POLY, 105.0, PRACTICE)
S.guide([TIP["T"], CORNER, TIP["N"]], PRACTICE, 0.5, 1.1)

# ---------------------------------------------------------------- 4. the curve above the floor
S.curve(alpha, 0.0, T1, BG, 5.6, 240)                  # halo: the lower branch passes behind
S.curve(alpha, 0.0, T1, THEORY, 2.6, 240)
S.arrow(alpha(1.26), alpha(1.38), THEORY, 2.6, 10.0)   # direction of travel, kept off the
#                                                        self-crossing that sits at the far end

# the axes go on top of the curve: alpha(0) is the origin itself, and near it the curve runs
# within a few pixels of the x axis, so underneath they would leave the axes looking cut off
S.axes(AXX, AXY, AXZ, labels=("", "", ""))

# ---------------------------------------------------------------- 5. the frame at t = 1
S.drop(A1)
for k in ("T", "N", "B"):                      # halos first: the three shafts share a start point
    S.line([A1, TIP[k]], BG, 5.8)
S.arrow(A1, TIP["T"], PRACTICE, 2.5, head=9)
S.arrow(A1, TIP["N"], BASE, 2.5, head=9)
S.arrow(A1, TIP["B"], TEXT, 2.5, head=9)
S.point(A1, TEXT, 3.8)

# ---------------------------------------------------------------- 6. labels
tag((AXX, 0, 0), italic("x"), -4, 14, TEXT, 11.5, "middle")
tag((0, AXY, 0), italic("y"), 6, -8, TEXT, 11.5, "middle")
tag((0, 0, AXZ), italic("z"), -11, -3, TEXT, 11.5, "end")

tag(A1, IT_A + "(1) = (2, 3, 4)", -11, 16, TEXT, 11.5, "end")
tag(TIP["T"], bold("T"), 7, 15, PRACTICE, 12.5)
tag(vadd(A1, vscale(0.8 * LEN, NV)), bold("N"), -12, -8, BASE, 12.5, "middle")
tag(vadd(A1, vscale(0.7 * LEN, BV)), bold("B"), 11, -9, TEXT, 12.5, "middle")
tag(alpha(1.5), IT_A, 7, -7, THEORY, 13)

at(1.70, 1.75, bold("T") + "(1) = (0, 1/" + SQ + "2, 1/" + SQ + "2)", PRACTICE, 11.5)
at(1.70, 1.30, bold("N") + "(1) = (" + MINUS_S + "1, 0, 0)", BASE, 11.5)
at(1.70, 0.85, bold("B") + "(1) = (0, " + MINUS_S + "1/" + SQ + "2, 1/" + SQ + "2)", TEXT, 11.5)

at(0.35, -4.25, IT_A + "(" + IT_T + ") = (3" + IT_T + " " + MINUS_S + " " + IT_T + sups("3")
   + ", 3" + IT_T + sups("2") + ", 3" + IT_T + " + " + IT_T + sups("3") + ")", THEORY, 11.5,
   "start", False)
at(0.35, -4.85, KAPPA + "(1) = " + TAU + "(1) = 1/12", TEXT, 11.5)

OUT["keyfi-kubik-aparat"] = figure(
    400, 400, [P],
    "&#945;(<em>t</em>) = (3<em>t</em> &#8722; <em>t</em><sup>3</sup>, 3<em>t</em><sup>2</sup>, "
    "3<em>t</em> + <em>t</em><sup>3</sup>) eğrisi &#8722;1,5 &#8804; <em>t</em> &#8804; 1,5 "
    "aralığında çizilmiştir; ok, <em>t</em>&#8217;nin arttığı yönü gösterir, soluk kısım "
    "<em>z</em> = 0 düzleminin altında kalır. &#945;(1) = (2, 3, 4) noktasında turuncu "
    "<strong>T</strong>(1) eğriye teğettir, yeşil <strong>N</strong>(1) = (&#8722;1, 0, 0) ona "
    "diktir ve eğrinin büküldüğü yana bakar, koyu <strong>B</strong>(1) = <strong>T</strong>(1) "
    "&#215; <strong>N</strong>(1) ise ilk ikisinin gerdiği taralı oskülatör düzleme diktir. "
    "Üç vektör de birim uzunluktadır; görünürlük için iki kat uzun çizilmişlerdir, sayfada "
    "farklı boyda görünmeleri izdüşümün kısaltmasındandır. Bu noktada eğrilik ile burulma "
    "eşittir: "
    "&#954;(1) = &#964;(1) = 1/12.",
    aria="Uzayda alpha(t) = (3t - t^3, 3t^2, 3t + t^3) egrisi ve t = 1 anindaki Frenet catisi; "
         "alpha(1) = (2, 3, 4) noktasindan cikan turuncu T = (0, 1/karekok2, 1/karekok2) egriye "
         "tegettir, yesil N = (-1, 0, 0) ile taranmis oskulator duzlem karesini gerer, koyu "
         "B = (0, -1/karekok2, 1/karekok2) bu kareye diktir; egrilik ve burulma 1/12")

# ============================================================ keyfi-kubik-cati-t2
# -*- coding: utf-8 -*-
# keyfi-kubik-cati-t2: the cubic alpha(t) = (2t, t^2, t^3/3) on -4 <= t <= 4 with the Frenet frame
# at t = 2. alpha(2) = (4, 4, 8/3); T = (1,2,2)/3, N = (-2,-1,2)/3, B = (2,-2,1)/3, each drawn 4
# units long, and the hatched piece of the osculating plane they span.
#
# Camera. The whole exercise is a fight between three things: T = (1,2,2)/3 must not point at the
# viewer (it would collapse to a stub), the osculating plane must not be seen edge on (|B.d| small),
# and the drawing must not be absurdly tall (z sweeps 42.7 units while x and y sweep 16). A scan
# over az in [14, 30], el in [14, 26] (see _scan_kubik.py) settles on az = 21, el = 18, where the
# three unit vectors project to 2.76, 3.47 and 3.51 of their 4 units, |B.d| = 0.48 opens the patch,
# and the page directions 43 / 95 / 167 degrees fan the arrows apart.
#
# Depth. depth(t) = d . alpha(t) = 1.776 t + 0.341 t^2 + 0.103 t^3 is strictly increasing, so the
# whole t < 0 half lies behind the t > 0 half: it is drawn thinner and paler, and the near half
# carries a background-coloured halo that breaks it where they cross (t = 1.67 over t = -0.90).
# That crossing and the far branch pass about one unit (15 px) under alpha(2) — the only tight
# spot in the picture, and the reason the labels at alpha(2) all go up and to the right.
import math

AZ, EL = 21.0, 18.0
L = 4.0                                  # drawn length of each frame vector
T2 = (1 / 3.0, 2 / 3.0, 2 / 3.0)
N2 = (-2 / 3.0, -1 / 3.0, 2 / 3.0)
B2 = (2 / 3.0, -2 / 3.0, 1 / 3.0)


def alpha(t):
    return (2 * t, t * t, t ** 3 / 3.0)


A2 = alpha(2.0)                          # (4, 4, 8/3)

P = space_panel(20, 16, 376, (-5.0, 19.6), (-21.4, 17.5))
S = Space(P, Camera(azimuth=AZ, elevation=EL, scale=1.0))

ALPHA_S, KAPPA_S, TAU_S = "&#945;", "&#954;", "&#964;"


def it(s):
    return f'<tspan font-style="italic">{s}</tspan>'


def mfmt(v):
    """Tick label with a typographic minus."""
    return fmt(v).replace("-", MINUS_S)


def halo(px_, py_, s, color=TEXT, size=11.5, anchor="start"):
    """Text with a page-coloured halo, so the faint grid behind it breaks.

    The halo is a separate stroke-only copy underneath rather than paint-order="stroke" on one
    element: with one element the renderer strokes and fills each tspan in turn, and the halo of a
    superscript then eats the crossbar of the italic letter in front of it.
    """
    common = (f'x="{px_:.1f}" y="{py_:.1f}" font-size="{size}" text-anchor="{anchor}"')
    P.add(f'<text {common} fill="none" stroke="{BG}" stroke-width="3.6" '
          f'stroke-linejoin="round">{s}</text>')
    P.add(f'<text {common} fill="{color}">{s}</text>')


def tag(Q, s, dx=0, dy=0, color=TEXT, size=11.5, anchor="start"):
    """Halo text hung on a space point."""
    X, Y = S.pt(Q)
    halo(P.X(X) + dx, P.Y(Y) + dy, s, color, size, anchor)


def hatch(poly, angle_deg, color=TEXT, step_px=8.0, width=0.8, opacity=0.34):
    """Parallel hatch lines at angle_deg (page), clipped to a convex polygon in panel units."""
    a = math.radians(angle_deg)
    d = (math.cos(a), math.sin(a))
    nrm = (-d[1], d[0])
    step = step_px * (P.xmax - P.xmin) / P.w
    proj = [nrm[0] * x + nrm[1] * y for x, y in poly]
    lo, hi = min(proj), max(proj)
    count = max(1, int((hi - lo) / step))
    c0 = lo + (hi - lo - (count - 1) * step) / 2.0
    parts = []
    for i in range(count):
        c = c0 + i * step
        hits = []
        for j in range(len(poly)):
            (x0, y0), (x1, y1) = poly[j], poly[(j + 1) % len(poly)]
            s0 = nrm[0] * x0 + nrm[1] * y0 - c
            s1 = nrm[0] * x1 + nrm[1] * y1 - c
            if (s0 < 0) != (s1 < 0):
                t = s0 / (s0 - s1)
                hits.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t))
        if len(hits) >= 2:
            hits.sort(key=lambda q: d[0] * q[0] + d[1] * q[1])
            parts.append(f"M{P.P(*hits[0])} L{P.P(*hits[-1])}")
    P.add(f'<path d="{" ".join(parts)}" fill="none" stroke="{color}" stroke-width="{width}" '
          f'opacity="{opacity}" stroke-linecap="butt"/>')


def right_angle(Q, a, b, s=0.75, color=TEXT, width=1.1, opacity=0.85):
    """Right-angle mark at Q, a true square in the plane of a and b, on a halo so that the grid
    line running behind it does not turn the corner into a crossroads."""
    ea, eb = vscale(s, vunit(a)), vscale(s, vunit(b))
    pts = [vadd(Q, ea), vadd(Q, vadd(ea, eb)), vadd(Q, eb)]
    S.line(pts, BG, width + 2.6)
    S.line(pts, color, width, None, opacity)


# ---------------------------------------------------------------- 1. the wall y = 0 and the axes
for gx in (-8, -4, 4, 8):
    S.line([(gx, 0, -12), (gx, 0, 12)], TEXT, 0.7, None, 0.10)
for gz in (-12, -8, -4, 4, 8, 12):
    S.line([(-8, 0, gz), (8, 0, gz)], TEXT, 0.7, None, 0.10)

S.axes(9.0, 18.0, 14.0, xmin=-9.0, zmin=-14.0, labels=("x", "y", "z"),
       offsets=((-5, 15), (11, 5), (-11, -5)))


def ticks(axis, values, dx, dy, anchor="middle"):
    """Ticks with haloed numbers — S.ticks() writes plain text, which the wall grid crosses."""
    k = "xyz".index(axis)
    tdir = {"x": (0, 1, 0), "y": (1, 0, 0), "z": (1, 0, 0)}[axis]
    for v in values:
        Q = [0.0, 0.0, 0.0]
        Q[k] = float(v)
        Q = tuple(Q)
        S.line([vadd(Q, vscale(-0.28, tdir)), vadd(Q, vscale(0.28, tdir))], TEXT, 1.0, None, 0.7)
        tag(Q, mfmt(v), dx, dy, TEXT, 10, anchor)


ticks("x", (4, 8), 11, 8)
ticks("y", (8, 12, 16), 0, 14)          # a tick at 4 would land on the far branch of the curve
ticks("z", (-10, -5, 5, 10), -10, 4, "end")

# ---------------------------------------------------------------- 2. the far half t <= 0
S.curve(alpha, -4.0, 0.0, THEORY, 2.0, 320, None, 0.5)

# ---------------------------------------------------------------- 3. the osculating patch
# The negative margins are wide enough that the rim of the patch does not run along the N and T
# arrows: -0.30 L back along T is 11 px to the left of N, -0.22 L back along N is 14 px under T.
CORNERS = [vadd(A2, vadd(vscale(a, vscale(L, T2)), vscale(b, vscale(L, N2))))
           for a, b in ((-0.30, -0.22), (1.20, -0.22), (1.20, 1.18), (-0.30, 1.18))]
POLY = S.pts(CORNERS)
P.polygon(POLY, PRACTICE, 0.09, "none")
hatch(POLY, 28.0, PRACTICE, 8.0, 0.8, 0.36)
P.polygon(POLY, "none", 0.0, PRACTICE, 1.0, "4 3")

# ---------------------------------------------------------------- 4. the near half t >= 0
NEAR = [alpha(4.0 * k / 320.0) for k in range(321)]
S.line(NEAR, BG, 4.6)                      # halo: breaks the far branch where they cross
S.line(NEAR[:-3], THEORY, 2.5)
S.arrow(NEAR[-4], NEAR[-1], THEORY, 2.5, 9.5)

# ---------------------------------------------------------------- 5. the frame at t = 2
right_angle(A2, T2, N2, 0.72, TEXT, 1.3, 0.95)
S.arrow(A2, vadd(A2, vscale(L, T2)), PRACTICE, 2.6, 9.5)
S.arrow(A2, vadd(A2, vscale(L, N2)), BASE, 2.6, 9.5)
S.arrow(A2, vadd(A2, vscale(L, B2)), TEXT, 2.6, 9.5)

for Q in (alpha(-4.0), (0.0, 0.0, 0.0), A2, alpha(4.0)):
    S.point(Q, TEXT, 3.4)

# ---------------------------------------------------------------- 6. labels
tag(vadd(A2, vscale(L, T2)), bold("T"), 10, 15, PRACTICE, 12.5)
tag(vadd(A2, vscale(L, N2)), bold("N"), -12, -6, BASE, 12.5, "end")   # clear of the patch's rim
tag(vadd(A2, vscale(L, B2)), bold("B"), -8, 2, TEXT, 12.5, "end")
tag(A2, it(ALPHA_S) + "(2) = (4, 4, 8/3)", 15, 13, TEXT, 11.5)   # between the patch rim and y
tag((0.0, 0.0, 0.0), it(ALPHA_S) + "(0) = (0, 0, 0)", -9, -7, TEXT, 11.5, "end")
tag(alpha(4.0), it(ALPHA_S) + "(4) = (8, 16, 64/3)", -12, 1, TEXT, 11.5, "end")
tag(alpha(-4.0), it(ALPHA_S) + "(" + MINUS_S + "4) = (" + MINUS_S + "8, 16, " + MINUS_S + "64/3)",
    -9, 15, TEXT, 11.5, "end")
halo(P.X(8.0), P.Y(11.0), it(ALPHA_S) + "(" + it("t") + ") = (2" + it("t") + ", " + it("t")
     + sups("2") + ", " + it("t") + sups("3") + "/3)", THEORY, 12.5, "end")

LEG = (P.X(-4.6), (P.Y(-15.2), P.Y(-16.8), P.Y(-18.4), P.Y(-20.0)))
halo(LEG[0], LEG[1][0], it("t") + " = 2:  " + KAPPA_S + " = " + TAU_S + " = 1/18", TEXT, 12)
halo(LEG[0], LEG[1][1], bold("T") + " = (1/3, 2/3, 2/3)", PRACTICE, 11.5)
halo(LEG[0], LEG[1][2], bold("N") + " = (" + MINUS_S + "2/3, " + MINUS_S + "1/3, 2/3)", BASE, 11.5)
halo(LEG[0], LEG[1][3], bold("B") + " = (2/3, " + MINUS_S + "2/3, 1/3)", TEXT, 11.5)

# ---------------------------------------------------------------- 7. what the eye should check
d = (math.cos(math.radians(EL)) * math.cos(math.radians(AZ)),
     math.cos(math.radians(EL)) * math.sin(math.radians(AZ)), math.sin(math.radians(EL)))
print("  |T|, |N|, |B| =", [round(vnorm(v), 12) for v in (T2, N2, B2)])
print("  T.N, N.B, T.B =", [round(vdot(a, b), 12) for a, b in ((T2, N2), (N2, B2), (T2, B2))])
print("  T x N - B =", [round(c, 12) for c in vsub(vcross(T2, N2), B2)])
tang = vunit(vsub(alpha(2.0001), alpha(1.9999)))
print("  egri tegeti - T =", [round(c, 6) for c in vsub(tang, T2)])
for nm, v in (("T", T2), ("N", N2), ("B", B2)):
    X, Y = S.pt(v)
    print(f"  {nm}: sayfa boyu {L * math.hypot(X, Y):.2f}/4 birim, "
          f"yon {math.degrees(math.atan2(Y, X)) % 360:.0f} derece")
print(f"  patch |B.d| = {abs(vdot(B2, d)):.2f}")
P2 = S.pt(A2)
worst = min(((math.dist(S.pt(alpha(-4 + 8 * k / 2000.0)), P2), -4 + 8 * k / 2000.0)
             for k in range(2001) if abs(-4 + 8 * k / 2000.0 - 2) > 0.8))
print(f"  alpha(2)'ye en yakin oteki egri noktasi: t = {worst[1]:.2f}, {worst[0]:.2f} birim "
      f"({worst[0] * P.w / (P.xmax - P.xmin):.0f} px), derinlik {vdot(alpha(worst[1]), d):.1f} "
      f"({vdot(A2, d):.1f})")
xs, ys = [], []
for k in range(801):
    X, Y = S.pt(alpha(-4 + 8 * k / 800.0))
    xs.append(X)
    ys.append(Y)
print(f"  egri X [{min(xs):.1f}, {max(xs):.1f}]  Y [{min(ys):.1f}, {max(ys):.1f}]  "
      f"panel X [{P.xmin}, {P.xmax}] Y [{P.ymin}, {P.ymax}]")

OUT["keyfi-kubik-cati-t2"] = figure(
    416, 628, [P],
    "<em>&#945;</em>(<em>t</em>) = (2<em>t</em>, <em>t</em><sup>2</sup>, <em>t</em><sup>3</sup>/3) "
    "kübik eğrisi &#8722;4 &#8804; <em>t</em> &#8804; 4 aralığında çizilmiştir; uçtaki ok "
    "<em>t</em>&#8217;nin artış yönünü, soluk parça ise eğrinin arkada kalan "
    "<em>t</em> &#8804; 0 yarısını gösterir. <em>t</em> = 2 noktasında, yani "
    "<em>&#945;</em>(2) = (4, 4, 8/3)&#8217;te, Frenet çatısının üç birim vektörü dörder "
    "birim uzunluğunda çizilmiştir: teğet <strong>T</strong> (turuncu), asli normal "
    "<strong>N</strong> (yeşil) ve binormal <strong>B</strong>. <strong>T</strong> ile "
    "<strong>N</strong>&#8217;nin gerdiği taralı parça oskülatör düzlemdir; <strong>T</strong> "
    "eğriye teğet olduğu için eğriyle birlikte gider, dik açı işareti de "
    "<strong>T</strong> &#183; <strong>N</strong> = 0 olduğunu hatırlatır. Üç okun sayfada farklı "
    "boylarda görünmesi izdüşümdendir; üçü de birim vektördür ve bu noktada "
    "&#954; = &#964; = 1/18&#8217;dir.",
    aria="Uzayda alpha(t) = (2t, t kare, t kup bolu 3) kubik egrisi t = -4 ile t = 4 arasinda; "
         "isaretli noktalar alpha(-4) = (-8, 16, -64/3), alpha(0) = (0, 0, 0), "
         "alpha(2) = (4, 4, 8/3) ve alpha(4) = (8, 16, 64/3). alpha(2) noktasindan dorder birim "
         "uzunlugunda uc ok cikar: turuncu T = (1/3, 2/3, 2/3) egriye tegettir, yesil "
         "N = (-2/3, -1/3, 2/3) ve koyu B = (2/3, -2/3, 1/3). T ile N taranmis oskulator duzlem "
         "parcasini gerer; o noktada kappa = tau = 1/18",
)

# ============================================================ keyfi-silindirik-helis
# -*- coding: utf-8 -*-
# keyfi-silindirik-helis: alpha(t) = (3t - t^3, 3t^2, 3t + t^3) on the vertical cylinder erected
# over its floor projection gamma(t) = (3t - t^3, 3t^2, 0). The axis of the cylindrical helix is
# u = (0, 0, 1) (the z axis), and the unit tangent meets every ruling of the wall at vartheta = pi/4.
# The ruling through t = 0 IS the z axis (gamma(0) = origin), so the angle at alpha(0) is read off
# the axis itself; the angle at alpha(1) = (2, 3, 4) is read off the ruling through
# gamma(1) = (2, 3, 0). Both verticals are already on the page — no extra dashed line is needed.
# The wall covers the whole height the curve occupies, -7.9 <= z <= 7.9, so that the curve really
# lies in it; a wall stopping at z = 0 would leave the branch t < 0 hanging in the air.
# u is drawn one unit long, its true length: three units would contradict the label u = (0, 0, 1).
# Camera: azimuth 32 is a compromise. Smaller azimuths open the floor curve and keep the figure
# wide, but they also lay T(0) = (1, 0, 1)/sqrt2 along the line of sight (at az = 22 that arrow
# shrinks to 28 px while T(1) stays 58); at az = 32 the two tangents come out 35 and 53 px long.
# Elevation 30 keeps the drawn angles honest: the two pi/4 angles read 46 and 53 degrees on the
# page, while at elevation 45 the first one would flatten to about 80.
import math

AZ, EL = 32.0, 30.0
T0, T1 = -1.5, 1.5                    # parameter range of the curve
Z1 = 3 * T1 + T1 ** 3                 # 7.875 — the height the curve reaches
Z0 = -Z1
RULINGS = (-1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5)
AXX, AXY, AXZ = 3.3, 7.9, 8.8
PPU = 36.0                            # pixels per space unit
UP = (0.0, 0.0, 1.0)                  # the axis vector u, a unit vector
ARROWS = (0.0, 1.0)                   # where the tangent vectors are drawn
TLEN = 2.0                            # drawn length of the tangent vectors


def alpha(t):
    return (3 * t - t ** 3, 3 * t * t, 3 * t + t ** 3)


def gam(t):
    return (3 * t - t ** 3, 3 * t * t, 0.0)


def wall(u, v):
    return (3 * u - u ** 3, 3 * u * u, v)


def tangent(t):
    """Unit tangent, straight from alpha'(t) = (3 - 3t^2, 6t, 3 + 3t^2)."""
    return vunit((3 - 3 * t * t, 6 * t, 3 + 3 * t * t))


def tip(t):
    return vadd(alpha(t), vscale(TLEN, tangent(t)))


# ---- self-check: unit tangents, each at pi/4 to u, and the two points of the text --------------
SQ2 = math.sqrt(2.0)
assert vnorm(vsub(tangent(0.0), (1 / SQ2, 0.0, 1 / SQ2))) < 1e-12     # T(0) = (1, 0, 1)/sqrt 2
assert vnorm(vsub(tangent(1.0), (0.0, 1 / SQ2, 1 / SQ2))) < 1e-12     # T(1) = (0, 1, 1)/sqrt 2
for _t in ARROWS:
    assert abs(math.acos(vdot(tangent(_t), UP)) - math.pi / 4) < 1e-12
assert alpha(0.0) == (0.0, 0.0, 0.0) and alpha(1.0) == (2.0, 3.0, 4.0) and gam(1.0) == (2, 3, 0)

# ---- panel sized from the projected content ----------------------------------------------------
CAM = Camera(azimuth=AZ, elevation=EL, scale=1.0)
CLOUD = [alpha(T0 + (T1 - T0) * k / 120) for k in range(121)]
CLOUD += [wall(T0 + (T1 - T0) * k / 120, z) for k in range(121) for z in (Z0, Z1)]
CLOUD += [(AXX, 0, 0), (0, AXY, 0), (0, 0, AXZ)] + [tip(t) for t in ARROWS]
XS = [CAM.project(q)[0] for q in CLOUD]
YS = [CAM.project(q)[1] for q in CLOUD]
PAD = 0.45
XR = (min(XS) - PAD, max(XS) + PAD)
YR = (min(YS) - PAD, max(YS) + PAD)
X0, Y0 = 26.0, 18.0
P = space_panel(X0, Y0, PPU * (XR[1] - XR[0]), XR, YR)
S = Space(P, CAM)

# ---- page-space report, so the arrows and angles can be checked without guessing ----------------
for _t in ARROWS:
    _a, _b = S.pt(alpha(_t)), S.pt(tip(_t))
    _dx, _dy = P.X(_b[0]) - P.X(_a[0]), P.Y(_b[1]) - P.Y(_a[1])
    print("t = %.0f: T arrow %.0f px, %.1f deg from the page vertical (true 45)"
          % (_t, math.hypot(_dx, _dy), math.degrees(math.atan2(abs(_dx), -_dy))))


def halo(px_, py_, s, color=TEXT, size=11.5, anchor="start"):
    """Text with a page-coloured outline behind it, so the faint wall lines break under it.

    Two separate <text> elements, not paint-order="stroke": rsvg strokes each tspan run in turn,
    so a superscript's halo was painted over the crossbar of the italic t just before it and
    '3t^2' came out as '3iota^2'.
    """
    common = (f'x="{px_:.1f}" y="{py_:.1f}" font-size="{size}" text-anchor="{anchor}"')
    P.add(f'<text {common} fill="none" stroke="{BG}" stroke-width="3.4" '
          f'stroke-linejoin="round">{s}</text>')
    P.add(f'<text {common} fill="{color}">{s}</text>')


def tag(Q, s, dx=0, dy=0, color=TEXT, size=11.5, anchor="start"):
    X, Y = S.pt(Q)
    halo(P.X(X) + dx, P.Y(Y) + dy, s, color, size, anchor)


def angle_mark(t, R, dx, dy, anchor):
    """Arc from the vertical ruling to the tangent at alpha(t), plus the vartheta label."""
    p, Tv = alpha(t), tangent(t)
    e = vunit(vsub(Tv, vscale(vdot(Tv, UP), UP)))      # in-plane direction, perpendicular to u
    ang = math.acos(vdot(Tv, UP))

    def at(r, th):
        return vadd(p, vadd(vscale(r * math.cos(th), UP), vscale(r * math.sin(th), e)))

    arc = [at(R, ang * k / 48) for k in range(49)]
    S.line(arc, BG, 2.4)                               # halo: at t = 0 the curve runs through the
    S.line(arc, TEXT, 1.3, None, 0.9)                  # wedge, and the arc has to stay readable
    tag(at(R, 0.0), TH + " = " + PI_S + "/4", dx, dy, TEXT, 11.5, anchor)


TH = "&#977;"                          # vartheta, as in the text
IT = '<tspan font-style="italic">%s</tspan>'
AL, GA, IT_T = IT % "&#945;", IT % "&#947;", IT % "t"
MIN = " " + MINUS_S + " "
CUBIC = ("(3" + IT_T + MIN + IT_T + sups("3") + ", 3" + IT_T + sups("2") + ", ")

# ---- 1. the wall over gamma, its rulings and rims -----------------------------------------------
S.surface(wall, (T0, T1), (Z0, Z1), nu=28, nv=1, fill=TEXT, stroke="none", opacity=(0.030, 0.085))
for u in RULINGS:
    S.line([wall(u, Z0), wall(u, Z1)], TEXT, 0.9, None, 0.30)
for z in (Z0, Z1):
    S.curve(lambda t, z=z: wall(t, z), T0, T1, TEXT, 1.0, 160, None, 0.40)
S.curve(gam, T0, T1, TEXT, 2.0, 200, None, 0.60)      # the cross-section curve, on the floor

# ---- 2. axes and the axis vector u ---------------------------------------------------------------
S.axes(AXX, AXY, AXZ, offsets=((-2, 14), (11, 4), (-11, -4)))
S.arrow((0, 0, 0), UP, TEXT, 2.6, head=9)

# ---- 3. the curve, its tangents and the two angles -----------------------------------------------
S.segment_arrow(alpha, T0, T1, THEORY, 2.5, 10.0, 300)
for t in ARROWS:
    S.arrow(alpha(t), tip(t), PRACTICE, 2.4, head=8.5)
angle_mark(0.0, 1.3, -5, -14, "end")
angle_mark(1.0, 1.1, 0, -11, "middle")

S.point(gam(1.0), TEXT, 2.6)
for t in ARROWS:
    S.point(alpha(t), TEXT, 3.4)

# ---- 4. labels -----------------------------------------------------------------------------------
tag(tip(0.0), bold("T"), -4, 16, PRACTICE, 12.5, "end")
tag(tip(1.0), bold("T"), 8, 14, PRACTICE, 12.5, "start")
tag(UP, bold("u") + " = (0, 0, 1)", -18, 2, TEXT, 12, "end")

tag(alpha(0.0), AL + "(0) = (0, 0, 0)", -30, 13, TEXT, 11.5, "end")
tag(alpha(1.0), AL + "(1) = (2, 3, 4)", 13, 17, TEXT, 11.5, "start")
tag(alpha(1.5), AL + "(" + IT_T + ") = " + CUBIC + "3" + IT_T + " + " + IT_T + sups("3") + ")",
    10, 26, THEORY, 11.5, "start")
tag(gam(1.5), GA + "(" + IT_T + ") = " + CUBIC + "0)", 10, 20, TEXT, 11.5, "start")

OUT["keyfi-silindirik-helis"] = figure(
    round(X0 + P.w + 24), round(Y0 + P.h + 18), [P],
    "&#945;(<em>t</em>) = (3<em>t</em> &#8722; <em>t</em><sup>3</sup>, 3<em>t</em><sup>2</sup>, "
    "3<em>t</em> + <em>t</em><sup>3</sup>) eğrisi, düzlemdeki izdüşümü "
    "&#947;(<em>t</em>) = (3<em>t</em> &#8722; <em>t</em><sup>3</sup>, 3<em>t</em><sup>2</sup>, 0) "
    "üstüne dikilen düşey silindirin duvarında yükselir. Silindirin doğrultmanları düşey olduğundan "
    "eksen vektörü <strong>u</strong> = (0, 0, 1)&#8217;dir. Birim teğet <strong>T</strong> "
    "(turuncu) her noktada bu düşey doğrultuyla aynı &#977; = &#960;/4 açısını yapar: "
    "&#945;(0) = (0, 0, 0) ile &#945;(1) = (2, 3, 4) noktalarındaki iki yay eşittir. Kesit eğrisi "
    "&#947; bir çember olmadığından &#945; dairesel bir helis değil, genel bir silindirik helistir.",
    aria="alpha(t) = (3t - t^3, 3t^2, 3t + t^3) egrisi, xy duzlemindeki izdusumu gamma(t) = "
         "(3t - t^3, 3t^2, 0) uzerine dikilen dusey silindirin duvarinda ilerler; orijinden cikan "
         "kalin ok eksen vektoru u = (0, 0, 1), turuncu oklar alpha(0) = (0, 0, 0) ve "
         "alpha(1) = (2, 3, 4) noktalarindaki birim tegetler T olup her ikisi de dusey "
         "dogrultmanla pi/4 acisi yapar")

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

# ============================================================ kovaryant-cember-uzerinde-ivme
# -*- coding: utf-8 -*-
# kovaryant-cember-uzerinde-ivme: the rotation field W = -y U1 + x U2 on the unit circle and its
# self-derivative nabla_W W = -x U1 - y U2. At t = 0, pi/2, pi, 3pi/2 the W arrows (blue) are
# tangent to the circle, vector parts (0, 1), (-1, 0), (0, -1), (1, 0); the nabla_W W arrows
# (orange) point to the centre, vector parts (-1, 0), (0, -1), (1, 0), (0, 1), and — having
# length 1 — end exactly at the origin. Short light-grey arrows at (+-1.4, 0), (0, +-1.4)
# hint at W away from the circle; they are drawn shortened (stated in the caption).
# The nabla glyph (U+2207) is missing from the site font, so it is drawn as an outlined
# inverted triangle in front of its label.
import math

XR = YR = (-1.6, 1.6)
p = cplane(35, 40, 330, XR, YR)
PPU = 330 / (XR[1] - XR[0])          # pixels per data unit
OUT_SHRINK = 0.35                    # the grey hint arrows: 0.35 of their true length

TS = (0.0, math.pi / 2, math.pi, 3 * math.pi / 2)
ON_CIRCLE = [(1, 0), (0, 1), (-1, 0), (0, -1)]
OUTSIDE = [(1.4, 0), (0, 1.4), (-1.4, 0), (0, -1.4)]


def W(a, b):
    """Vector part of W at (a, b)."""
    return (-b, a)


def acc(a, b):
    """Vector part of nabla_W W at (a, b)."""
    return (-a, -b)


def ital(s):
    return '<tspan font-style="italic">' + s + '</tspan>'


def num(v):
    v = int(round(v))
    return (MINUS_S + str(-v)) if v < 0 else str(v)


def nabla(px, py, color, size=8.0, width=1.0):
    """The nabla sign as an inverted triangle: base at cap height, apex on the baseline."""
    p.add(f'<polygon points="{px:.1f},{py - size:.1f} {px + size:.1f},{py - size:.1f} '
          f'{px + size / 2:.1f},{py:.1f}" fill="none" stroke="{color}" stroke-width="{width}" '
          f'stroke-linejoin="round"/>')


def turn_arc(a0, a1, r=1.0, color=TEXT, width=1.5, opacity=0.85, head=7.0, n=40):
    """Small arc along the circle from angle a0 to a1 with an arrowhead: the sense of rotation."""
    pts = [polar(r, a0 + (a1 - a0) * k / n) for k in range(n + 1)]
    p.line(pts[:-2], color, width, None, opacity)
    p.arrow(pts[-4], pts[-1], color, width, head, None, opacity)


# --- the circle r = 1 (grey) and the field away from it (short light-grey arrows) -----------
p.circle(0, 0, 1.0, TEXT, 1.3, None, "none", 0.4)
for a, b in OUTSIDE:
    wa, wb = W(a, b)
    p.arrow((a, b), (a + OUT_SHRINK * wa, b + OUT_SHRINK * wb), TEXT, 1.4, head=6.5, opacity=0.4)
    p.circle(a, b, 2.0 / PPU, TEXT, 0, None, TEXT, 0.4)

p.origin_axes("x", "y")

# counter-clockwise sense of the motion, on the circle between t = 0 and t = pi/2
turn_arc(math.radians(28), math.radians(62))

# --- W (blue, tangent) and nabla_W W (orange, to the centre) at the four points -------------
for a, b in ON_CIRCLE:
    wa, wb = W(a, b)
    p.arrow((a, b), (a + wa, b + wb), THEORY, 2.1, head=8)
for a, b in ON_CIRCLE:
    ca, cb = acc(a, b)
    p.arrow((a, b), (a + ca, b + cb), PRACTICE, 2.1, head=8)
for a, b in ON_CIRCLE:
    dot(p, (a, b), TEXT, 3.2)

# --- labels ----------------------------------------------------------------------------------
T_EQ = ital("t") + " = "
# (coordinates, t-label, dx, dy of the first line, anchor); the second line sits 13 px further
# from the point. Each pair is placed on the side of the point that neither arrow crosses.
POINT_LABELS = [
    ((1, 0), T_EQ + "0", 7, 14, "start", +13),
    ((0, 1), T_EQ + PI_S + "/2", 8, -6, "start", -13),
    ((-1, 0), T_EQ + PI_S, -7, -6, "end", -13),
    ((0, -1), T_EQ + "3" + PI_S + "/2", -8, 14, "end", +13),
]
for (a, b), ts, dx, dy, anc, step in POINT_LABELS:
    p.label(a, b, "(" + num(a) + ", " + num(b) + ")", dx, dy, TEXT, 11, anc)
    p.add(f'<text x="{p.X(a) + dx:.1f}" y="{p.Y(b) + dy + step:.1f}" fill="{TEXT}" font-size="10.5" '
          f'text-anchor="{anc}" opacity="0.8">{ts}</text>')

# W beside the blue arrow at (1, 0); nabla_W W above the orange arrow from (1, 0) to the origin
p.label(1, 0.5, ital("W"), 8, 4, THEORY, 12.5, "start")
gx, gy = p.X(0.5) - 15, p.Y(0) - 9
nabla(gx, gy, PRACTICE)
p.text_px(gx + 10, gy, subs(ital("W")) + " " + ital("W"), PRACTICE, 12.5, "start")

# formula line above the panel: W = -yU1 + xU2,  nabla_W W = -xU1 - yU2
fy = p.y0 - 18
p.text_px(184, fy,
          ital("W") + " = " + MINUS_S + ital("y") + ital("U") + subs("1") + " + " + ital("x") + ital("U")
          + subs("2") + ",", TEXT, 11.5, "end")
nabla(192, fy, TEXT)
p.text_px(202, fy,
          subs(ital("W")) + " " + ital("W") + " = " + MINUS_S + ital("x") + ital("U") + subs("1") + " "
          + MINUS_S + " " + ital("y") + ital("U") + subs("2"), TEXT, 11.5, "start")

OUT["kovaryant-cember-uzerinde-ivme"] = figure(
    400, 388, [p],
    "Birim çember (gri) üzerinde <em>t</em> = 0, &#960;/2, &#960;, 3&#960;/2 noktalarında "
    "<em>W</em> = &#8722;<em>y</em><em>U</em><sub>1</sub> + <em>x</em><em>U</em><sub>2</sub> dönme "
    "alanının okları (mavi) ve &#8711;<sub><em>W</em></sub><em>W</em> = &#8722;<em>x</em><em>U</em><sub>1</sub> "
    "&#8722; <em>y</em><em>U</em><sub>2</sub> alanının okları (turuncu). Mavi oklar çembere teğettir: "
    "saat yönünün tersine dönen noktanın hızıdır. Turuncu oklar merkeze bakar, uzunlukları yarıçap "
    "kadardır ve tam orijinde biter: bu, birim açısal hızla dönen noktanın merkezcil ivmesidir. "
    "Çember dışındaki açık gri oklar <em>W</em>&#8217;nin oradaki yönünü gösterir; yer kazanmak için "
    "kısaltılmıştır.",
    aria="Birim cember uzerinde t = 0, pi/2, pi, 3pi/2 noktalari (1, 0), (0, 1), (-1, 0), (0, -1); "
         "her birinde W = -y U1 + x U2 alaninin cembere teget mavi oku, vektor kisimlari (0, 1), "
         "(-1, 0), (0, -1), (1, 0), ve merkeze bakan turuncu nabla_W W oku, vektor kisimlari "
         "(-1, 0), (0, -1), (1, 0), (0, 1), hepsi orijinde biter; cember disinda (1.4, 0), (0, 1.4), "
         "(-1.4, 0), (0, -1.4) noktalarinda W'nin kisaltilmis acik gri oklari; saat yonunun tersine "
         "donusu gosteren kucuk yay oku")

# ============================================================ kovaryant-dogru-boyunca-alan
# -*- coding: utf-8 -*-
# kovaryant-dogru-boyunca-alan: the line alpha(t) = (2 - t, 1, 2t) of the example, drawn for
# -1/2 <= t <= 1, with the field W = x^2 U1 + yz U3 on it. At t = -1/2, 0, 1/2, 1 the points are
# (5/2, 1, -1), (2, 1, 0), (3/2, 1, 1), (1, 1, 2) and the vector parts of W are (25/4, 0, -1),
# (4, 0, 0), (9/4, 0, 1), (1, 0, 2) — blue arrows, all at 1/4 of their true length (said in the
# title). From p = (2, 1, 0) the green arrow is v = (-1, 0, 2); since p + v is the point at t = 1,
# it runs along the line and covers its 0 <= t <= 1 piece. The orange arrow is the covariant
# derivative nabla_v W = (-4, 0, 2), drawn at the same 1/4 scale.
# Everything lies in the plane y = 1 (the grid), so the three axes at y = 0 are seen through it:
# every arrow and the line itself are drawn over a background-coloured casing, which is the
# correct occlusion — the sheet y = 1 is in front of the axes — and keeps the crossings clean.
# Camera: azimuth 50 is at the top of the API band on purpose. Below ~48 the projected z axis
# cuts the drawn line (at az 35 it crosses at t = 0.57) and the short W arrow at t = 1/2 shrinks
# to about 25 px; at 50 the line stays left of the z axis and that arrow is 38 px long.
# Elevation 30 puts the projected x axis, which is parallel to the z = const grid lines, at the
# level z = tan(el)/sin(az) = 0.75 — midway between the nabla tip (z = 1/2) and the point at
# t = 1/2 (z = 1), the only free gap there is.
import math

AZ, EL = 50.0, 30.0
SHRINK = 0.25                              # every W arrow and the nabla arrow at 1/4
TS = (-0.5, 0.0, 0.5, 1.0)
GX, GZ = (0.0, 4.4), (-1.5, 2.85)          # extent of the grid drawn in the plane y = 1
AXX, AXY, AXZ = 1.4, 1.85, 2.7

p_pt = (2.0, 1.0, 0.0)
v_vec = (-1.0, 0.0, 2.0)
nabla_vec = (-4.0, 0.0, 2.0)


def alpha(t):
    return (2.0 - t, 1.0, 2.0 * t)


def field(q):
    """W = x^2 U1 + yz U3 at the point q."""
    return (q[0] * q[0], 0.0, q[1] * q[2])


def tip(q, w):
    """Tip of the arrow that carries the vector part w, shortened to 1/4."""
    return vadd(q, vscale(SHRINK, w))


P = space_panel(16, 14, 372, (-2.80, 1.42), (-3.18, 2.50))
S = Space(P, Camera(azimuth=AZ, elevation=EL, scale=1.0))

IT_T = None                                # set below, once bold()/subs() are in scope


def ital(s):
    return '<tspan font-style="italic">' + s + '</tspan>'


def halo(px, py, s, color=TEXT, size=11, anchor="start"):
    """Text with a page-coloured outline, so the faint grid and axes break under it."""
    P.add(f'<text x="{px:.1f}" y="{py:.1f}" fill="{color}" font-size="{size}" '
          f'text-anchor="{anchor}" stroke="{BG}" stroke-width="3.4" stroke-linejoin="round" '
          f'paint-order="stroke">{s}</text>')


def at(X, Y, s, color=TEXT, size=11, anchor="start"):
    """Halo text at a point of the panel's (projected) data plane."""
    halo(P.X(X), P.Y(Y), s, color, size, anchor)


def tag(Q, s, dx=0, dy=0, color=TEXT, size=11, anchor="start"):
    """Halo text hung on a space point, nudged by pixels."""
    X, Y = S.pt(Q)
    halo(P.X(X) + dx, P.Y(Y) + dy, s, color, size, anchor)


def cased_arrow(A, B, color, width, head):
    """Arrow over a background-coloured casing: it sits in front of the axes and the grid."""
    S.arrow(A, B, BG, width + 2.2, head + 2.2)
    S.arrow(A, B, color, width, head)


def marked(Q, r=3.4):
    S.point(Q, BG, r + 1.4)
    S.point(Q, TEXT, r)


def nabla_text(px, py, rest, color, size=11.5):
    """'nabla' as a small triangle path, then the rest of the label: the font has no U+2207."""
    w, h = 0.62 * size, 0.70 * size
    P.add(f'<path d="M{px:.1f},{py - h:.1f} L{px + w:.1f},{py - h:.1f} L{px + w / 2:.1f},{py:.1f} Z" '
          f'fill="none" stroke="{color}" stroke-width="1.15" stroke-linejoin="miter" '
          f'stroke-opacity="1"/>')
    halo(px + w + 1.5, py, rest, color, size, "start")


# --- 1. the plane y = 1: a pale sheet with a grid ------------------------------------------------
CORNERS = [(GX[0], 1, GZ[0]), (GX[1], 1, GZ[0]), (GX[1], 1, GZ[1]), (GX[0], 1, GZ[1])]
P.polygon(S.pts(CORNERS), TEXT, 0.05, "none")
for gx in (1, 2, 3, 4):
    S.line([(gx, 1, GZ[0]), (gx, 1, GZ[1])], TEXT, 0.7, None, 0.13)
for gz in (-1, 0, 1, 2):
    S.line([(GX[0], 1, gz), (GX[1], 1, gz)], TEXT, 0.7, None, 0.13)
S.line(CORNERS + [CORNERS[0]], TEXT, 0.9, None, 0.22)

# --- 2. axes (behind the sheet, so they stay faint) ----------------------------------------------
S.axes(AXX, AXY, AXZ, color=TEXT, opacity=0.45, offsets=((-5, 14), (11, 5), (-9, -5)))
for Q, s, dx, dy, anchor in (((1, 0, 0), "1", -3, 15, "middle"),
                             ((0, 1, 0), "1", 7, 14, "start"),
                             ((0, 0, 1), "1", 8, 4, "start"),
                             ((0, 0, 2), "2", 8, 4, "start")):
    d = (0, 0.07, 0) if Q[0] else (0.07, 0, 0)
    S.line([vsub(Q, d), vadd(Q, d)], TEXT, 1.0, None, 0.55)
    tag(Q, s, dx, dy, TEXT, 10, anchor)

# --- 3. the line, the field on it, v and the covariant derivative ---------------------------------
S.arrow(alpha(-0.5), alpha(1.0), BG, 3.6, 0.1)              # casing for the line
S.line([alpha(-0.5), alpha(1.0)], TEXT, 1.3, None, 0.55)

HEADS = {-0.5: 9.5, 0.0: 8.5, 0.5: 7.5, 1.0: 7.5}
for t in TS:
    q = alpha(t)
    cased_arrow(q, tip(q, field(q)), THEORY, 2.2, HEADS[t])

cased_arrow(p_pt, vadd(p_pt, v_vec), BASE, 2.4, 9.5)
cased_arrow(p_pt, tip(p_pt, nabla_vec), PRACTICE, 2.6, 10.0)

for t in TS:
    marked(alpha(t), 3.6 if t == 0.0 else 3.2)

# --- 4. labels ------------------------------------------------------------------------------------
IT_T = ital("t") + " = "
U1 = ital("U") + subs("1")
U3 = ital("U") + subs("3")

# the points, read off the line: to its right below t = 1/2, to its left at t = 1
tag(alpha(-0.5), IT_T + MINUS_S + "1/2", 13, -3, TEXT, 11)
tag(alpha(-0.5), "(5/2, 1, " + MINUS_S + "1)", 13, 12, TEXT, 11)
tag(p_pt, bold("p") + " = (2, 1, 0)", 14, 12, TEXT, 11)
tag(p_pt, IT_T + "0", 14, 26, TEXT, 11)
tag(alpha(0.5), IT_T + "1/2", -14, -32, TEXT, 11, "end")
tag(alpha(0.5), "(3/2, 1, 1)", -14, -18, TEXT, 11, "end")
tag(alpha(1.0), IT_T + "1", -13, -4, TEXT, 11, "end")
tag(alpha(1.0), "(1, 1, 2)", -13, 11, TEXT, 11, "end")

# the vector parts of the blue arrows, each beside its own arrow
at(-2.00, -2.20, "(25/4, 0, " + MINUS_S + "1)", THEORY, 10.5, "middle")
at(-1.00, -1.55, ital("W") + "(" + bold("p") + ") = (4, 0, 0)", THEORY, 10.5, "end")
at(-1.15, -0.17, "(9/4, 0, 1)", THEORY, 10.5, "middle")
at(-0.40, 1.50, "(1, 0, 2)", THEORY, 10.5, "end")

# v, in the narrow wedge between the line and the projected z axis
at(-0.38, 0.12, bold("v"), BASE, 12.5)
# the covariant derivative, in the open pocket below the origin
nabla_text(P.X(-0.42), P.Y(-0.85), subs(bold("v")) + ital("W") + " = (" + MINUS_S + "4, 0, 2)",
           PRACTICE, 11.5)

at(-0.90, -1.80, ital("&#945;"), TEXT, 12.5)          # the line, on the free side of its grey piece
at(0.60, -1.46, ital("y") + " = 1 düzlemi", TEXT, 10.5, "end")
# the field and the scale of the arrows, in the open corner above the sheet
at(-2.74, 2.26, ital("W") + " = " + ital("x") + sups("2") + U1 + " + " + ital("yz") + " " + U3,
   TEXT, 11.5)
at(-2.74, 2.04, "mavi ve turuncu oklar 1/4 ölçeğinde", TEXT, 11.5)

OUT["kovaryant-dogru-boyunca-alan"] = figure(
    404, 528, [P],
    "<strong>p</strong> = (2, 1, 0) noktasından <strong>v</strong> = (&#8722;1, 0, 2) yönünde "
    "giden &#945;(<em>t</em>) = (2 &#8722; <em>t</em>, 1, 2<em>t</em>) doğrusu, tümüyle "
    "<em>y</em> = 1 düzleminde kalır; doğru üzerindeki dört noktada mavi oklar "
    "<em>W</em> = <em>x</em><sup>2</sup><em>U</em><sub>1</sub> + <em>yzU</em><sub>3</sub> "
    "alanının değerleridir ve vektör kısımları <em>t</em> = &#8722;1/2, 0, 1/2, 1 için sırasıyla "
    "(25/4, 0, &#8722;1), (4, 0, 0), (9/4, 0, 1), (1, 0, 2)&#8217;dir. Yeşil ok "
    "<strong>v</strong>, doğrunun <em>t</em> = 0 ile <em>t</em> = 1 arasındaki parçasının "
    "kendisidir; sığmaları için bütün mavi oklar ve turuncu ok gerçek boylarının "
    "1/4&#8217;ü ile çizilmiştir. <em>t</em> büyürken ok "
    "önce kısalır, sonra yukarı doğru döner; turuncu ok "
    "&#8711;<sub><strong>v</strong></sub><em>W</em> = (&#8722;4, 0, 2) bu iki değişimi tek bir "
    "teğet vektörde toplar ve <em>W</em>(<strong>p</strong>) ile aynı noktada uygulanmıştır.",
    aria="Uzayda y = 1 duzleminde alpha(t) = (2 - t, 1, 2t) dogrusu; t = -1/2, 0, 1/2, 1 "
         "noktalari (5/2, 1, -1), (2, 1, 0), (3/2, 1, 1), (1, 1, 2) isaretli ve her birinde "
         "W = x^2 U1 + yz U3 alaninin mavi oku var, vektor kisimlari sirasiyla (25/4, 0, -1), "
         "(4, 0, 0), (9/4, 0, 1), (1, 0, 2), hepsi 1/4 olceginde. p = (2, 1, 0) noktasindan cikan "
         "yesil ok v = (-1, 0, 2) dogru boyunca uzanir; ayni noktadan cikan turuncu ok, ayni "
         "olcekteki kovaryant turev nabla_v W = (-4, 0, 2)",
)

# ============================================================ kovaryant-duzlemde-donme-alani
# -*- coding: utf-8 -*-
# kovaryant-duzlemde-donme-alani: the rotation field W = -y U1 + x U2 in the xy plane and its
# covariant derivative along v = (0, 1) at p = (1, 0). The dashed line x = 1 is p + t v; on it the
# points t = -1/2, 0, 1/2, 1, i.e. (1, -1/2), (1, 0), (1, 1/2), (1, 1), carry the W arrows (blue) with
# vector parts (1/2, 1), (0, 1), (-1/2, 1), (-1, 1). At p the green v = (0, 1) and the blue
# W(p) = (0, 1) are the same vector, so v is drawn underneath as a border around the blue arrow;
# nabla_v W = (-1, 0) is the orange arrow along the x axis. Light-grey arrows on the lattice
# {-1, 0, 1, 2} x {-1, 0, 1} show the field around. Every arrow is drawn at SHRINK of its true
# length (stated in the caption); at 1/2 or 1 the tip of W(p) would land on the next marked point.
# The nabla glyph (U+2207) is missing from the site font, so it is drawn as an outlined inverted
# triangle in front of its label, as in kovaryant-cember-uzerinde-ivme.

SHRINK = 0.4
XR, YR = (-1.6, 2.5), (-1.6, 1.9)
p = cplane(25, 34, 350, XR, YR)
PPU = 350 / (XR[1] - XR[0])          # pixels per data unit

P0 = (1.0, 0.0)                      # p
V = (0.0, 1.0)                       # v
DW = (-1.0, 0.0)                     # nabla_v W at p
TS = (-0.5, 0.0, 0.5, 1.0)           # t values of the marked points on the line
LATTICE = [(a, b) for a in (-1, 0, 1, 2) for b in (-1, 0, 1)
           if (a, b) not in ((0, 0), (1, 0), (1, 1))]   # grey field arrows; (0, 0) has W = 0


def W(a, b):
    """Vector part of W at (a, b)."""
    return (-b, a)


def tip(q, w):
    """End point of the shortened arrow with vector part w starting at q."""
    return (q[0] + SHRINK * w[0], q[1] + SHRINK * w[1])


def ital(s):
    return '<tspan font-style="italic">' + s + '</tspan>'


def nabla(px, py, color, size=8.0, width=1.15):
    """The nabla sign as an inverted triangle: base at cap height, apex on the baseline."""
    p.add(f'<polygon points="{px:.1f},{py - size:.1f} {px + size:.1f},{py - size:.1f} '
          f'{px + size / 2:.1f},{py:.1f}" fill="none" stroke="{color}" stroke-width="{width}" '
          f'stroke-linejoin="round"/>')


def stacked_arrows(p0, p1, under, over, width=2.2, head=8.0, border=2.2):
    """Two equal vectors drawn on top of each other: the `under` arrow shows as a uniform border
    of `border` px around the `over` arrow (shaft and head alike)."""
    x0, y0, x1, y1 = p.X(p0[0]), p.Y(p0[1]), p.X(p1[0]), p.Y(p1[1])
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy)
    ux, uy = dx / L, dy / L
    sx, sy = x1 - ux * head * 0.8, y1 - uy * head * 0.8
    px_, py_, hw = -uy, ux, head * 0.42
    pts = (f"{x1:.1f},{y1:.1f} {x1 - ux * head + px_ * hw:.1f},{y1 - uy * head + py_ * hw:.1f} "
           f"{x1 - ux * head - px_ * hw:.1f},{y1 - uy * head - py_ * hw:.1f}")
    p.add(f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{sx:.1f}" y2="{sy:.1f}" stroke="{under}" '
          f'stroke-width="{width + 2 * border:.1f}" stroke-linecap="round"/>')
    p.add(f'<polygon points="{pts}" fill="{under}" stroke="{under}" stroke-width="{2 * border:.1f}" '
          f'stroke-linejoin="round"/>')
    p.arrow(p0, p1, over, width, head)


def num_label(x, y, s, dx, dy, anchor):
    """Coordinate number next to a lattice point on an axis."""
    p.add(f'<text x="{p.X(x) + dx:.1f}" y="{p.Y(y) + dy:.1f}" fill="{TEXT}" font-size="10.5" '
          f'text-anchor="{anchor}" opacity="0.75">{s}</text>')


def tick(x, y, horizontal):
    """Short tick through an axis point."""
    if horizontal:
        p.add(f'<line x1="{p.X(x):.1f}" y1="{p.Y(y) - 3:.1f}" x2="{p.X(x):.1f}" y2="{p.Y(y) + 3:.1f}" '
              f'stroke="{TEXT}" stroke-width="1" opacity="0.7"/>')
    else:
        p.add(f'<line x1="{p.X(x) - 3:.1f}" y1="{p.Y(y):.1f}" x2="{p.X(x) + 3:.1f}" y2="{p.Y(y):.1f}" '
              f'stroke="{TEXT}" stroke-width="1" opacity="0.7"/>')


# --- the line p + t v = (1, t), the axes and the ticks ------------------------------------------
guide(p, [(1.0, YR[0] + 0.06), (1.0, YR[1] - 0.06)], TEXT, 0.5)
# the x label goes above the axis: below it, the arrow from (2, -1) ends at (2.4, -0.2)
p.origin_axes("", "y")
p.add(f'<text x="{p.x0 + p.w + 2:.1f}" y="{p.Y(0) - 7:.1f}" fill="{TEXT}" font-size="11.5" '
      f'font-style="italic" text-anchor="end" opacity="0.85">x</text>')
# tick numbers on the side of the axis that the arrow at that point does not cross
tick(-1, 0, True);  num_label(-1, 0, MINUS_S + "1", 0, -6, "middle")
tick(2, 0, True);   num_label(2, 0, "2", 0, 14, "middle")
tick(0, 1, False);  num_label(0, 1, "1", 6, 4, "start")
tick(0, -1, False); num_label(0, -1, MINUS_S + "1", -6, 4, "end")

# --- the field around: short light-grey arrows on the lattice -----------------------------------
for a, b in LATTICE:
    p.arrow((a, b), tip((a, b), W(a, b)), TEXT, 1.4, head=6.5, opacity=0.42)
for a, b in LATTICE + [(0, 0)]:
    p.circle(a, b, 2.0 / PPU, TEXT, 0, None, TEXT, 0.45)

# --- W along the line (blue), v under W(p) (green), nabla_v W (orange) --------------------------
for t in TS:
    q = (1.0, t)
    if t != 0.0:
        p.arrow(q, tip(q, W(*q)), THEORY, 2.1, head=7.5)
stacked_arrows(P0, tip(P0, V), BASE, THEORY, 2.6, 8.5, 1.9)      # v = W(p) = (0, 1)
p.arrow(P0, tip(P0, DW), PRACTICE, 2.2, head=8)
for t in TS:
    dot(p, (1.0, t), TEXT, 3.3)

# --- labels --------------------------------------------------------------------------------------
T_EQ = ital("t") + " = "
PX, PY = p.X(P0[0]), p.Y(P0[1])
# t values: to the right of the points, except t = -1/2 whose right side holds the arrow from (1, -1)
p.label(1.0, -0.5, T_EQ + MINUS_S + "1/2", -9, 4, TEXT, 10.5, "end")
p.label(1.0, 0.0, T_EQ + "0", 9, 3, TEXT, 10.5, "start")
p.label(1.0, 0.5, T_EQ + "1/2", 9, 4, TEXT, 10.5, "start")
p.label(1.0, 1.0, T_EQ + "1", 9, 4, TEXT, 10.5, "start")

p.text_px(PX - 6, PY + 15, bold("p") + " = (1, 0)", TEXT, 11.5, "end")
p.text_px(PX - 9, PY - 28, ital("W") + "(" + bold("p") + ")", THEORY, 12, "end")
p.text_px(PX + 9, PY - 24, bold("v"), BASE, 12.5, "start")
gx, gy = PX - 34, PY - 9
nabla(gx, gy, PRACTICE)
p.text_px(gx + 10, gy, subs(bold("v")) + " " + ital("W"), PRACTICE, 12.5, "start")

# formula line above the panel
p.text_px(p.x0 + p.w / 2, p.y0 - 16,
          ital("W") + " = " + MINUS_S + ital("y") + ital("U") + subs("1") + " + " + ital("x") + ital("U")
          + subs("2"), TEXT, 11.5, "middle")

OUT["kovaryant-duzlemde-donme-alani"] = figure(
    400, 348, [p],
    "<em>W</em> = &#8722;<em>y</em><em>U</em><sub>1</sub> + <em>x</em><em>U</em><sub>2</sub> dönme "
    "alanının <em>x</em> = 1 doğrusu üzerindeki <em>t</em> = &#8722;1/2, 0, 1/2, 1 noktalarında okları "
    "(mavi) ve çevredeki tam sayı noktalarında okları (gri); okunaklılık için her ok gerçek boyunun "
    "0,4 katıyla çizilmiştir. <strong>p</strong> = (1, 0) noktasındaki yeşil <strong>v</strong> = (0, 1) "
    "oku, oradaki <em>W</em>(<strong>p</strong>) = (0, 1) mavi okuyla aynı vektör olduğu için onun "
    "altında yalnızca kenarlarıyla görünür. Doğru boyunca yukarı çıkıldıkça okun <em>y</em> bileşeni 1 "
    "kalır, <em>x</em> bileşeni &#8722;<em>y</em> olur: sağa yatık ok <strong>p</strong>&#8217;de "
    "dikleşir, sonra sola yatar. Bu dönüşün <strong>p</strong>&#8217;deki hızı turuncu okla gösterilen "
    "&#8711;<sub><strong>v</strong></sub><em>W</em> = (&#8722;1, 0) vektörüdür; ilk anda okun yalnızca "
    "doğrultusu değişir, boyu değişmez.",
    aria="Duzlemde W = -y U1 + x U2 alani; x = 1 kesikli dogrusu uzerinde t = -1/2, 0, 1/2, 1 "
         "anlarindaki (1, -1/2), (1, 0), (1, 1/2), (1, 1) noktalarinda W'nin mavi oklari, vektor "
         "kisimlari (1/2, 1), (0, 1), (-1/2, 1), (-1, 1); p = (1, 0) noktasindan cikan yesil v = (0, 1) "
         "oku mavi W(p) okunun altinda kenar olarak gorunur; ayni noktadan cikan turuncu "
         "nabla_v W = (-1, 0) oku; -1..2 x -1..1 tam sayi izgarasinda acik gri W oklari; butun oklar "
         "gercek boyunun 0,4 katiyla cizilmis")

# ============================================================ kovaryant-konum-alani
# -*- coding: utf-8 -*-
# kovaryant-konum-alani: the position field X = x U1 + y U2 in the xy plane. Its arrow at (a, b)
# has vector part (a, b); every X arrow is drawn at 1/2 of its true length (stated in the title
# and the caption). Grey arrows at the lattice points (1,1), (1,2), (2,2), (3,1), (1,3); blue arrows
# at the points p + t v, t = 0, 1/2, 1, of the dashed line through p = (2, 1) with v = (1, 2),
# i.e. at (2, 1), (5/2, 2), (3, 3) with vector parts (2, 1), (5/2, 2), (3, 3).
# The tangent vector v (green) and the covariant derivative nabla_v X = (1, 2) = v (orange, the
# course colour for derivative arrows) are drawn at TRUE length; the orange arrow runs parallel to v,
# shifted 0.25 units to its right so the two do not coincide.
# The nabla is drawn as a small triangle path: the site font has no U+2207.
import math

SHRINK = 0.5                                   # X arrows are shortened to 1/2
XR, YR = (-0.35, 5.15), (-0.35, 4.85)
p = cplane(30, 34, 340, XR, YR)
PPU = p.w / (XR[1] - XR[0])                    # pixels per data unit

P0 = (2.0, 1.0)                                # p
V = (1.0, 2.0)                                 # v
LATTICE = [(1, 1), (1, 2), (2, 2), (3, 1), (1, 3)]
NPERP = (2.0 / math.sqrt(5.0), -1.0 / math.sqrt(5.0))   # unit normal to v, pointing to its right
OFF = 0.25                                      # shift of the nabla arrow, in data units


def ital(s):
    return '<tspan font-style="italic">' + s + '</tspan>'


def on_line(t):
    return (P0[0] + t * V[0], P0[1] + t * V[1])


def x_tip(q):
    """Tip of the shortened X arrow at q: q + (1/2) q."""
    return (q[0] * (1.0 + SHRINK), q[1] * (1.0 + SHRINK))


def shifted(q):
    return (q[0] + OFF * NPERP[0], q[1] + OFF * NPERP[1])


def nabla_label(px, py, rest, color, size=11.5):
    """'nabla' as a triangle path, followed by the text `rest` (subscript first)."""
    w, h = 0.62 * size, 0.70 * size
    p.add(f'<path d="M{px:.1f},{py - h:.1f} L{px + w:.1f},{py - h:.1f} L{px + w / 2:.1f},{py:.1f} Z" '
          f'fill="none" stroke="{color}" stroke-width="1.1" stroke-linejoin="miter"/>')
    p.text_px(px + w + 1.5, py, rest, color, size, "start")


# --- axes ---------------------------------------------------------------------------------------
p.origin_axes("x", "y", xticks=(1, 2, 3, 4), yticks=(1, 2, 3, 4))

# --- the field on the lattice: grey, at 1/2 scale ----------------------------------------------
for q in LATTICE:
    p.arrow(q, x_tip(q), TEXT, 1.5, head=6.5, opacity=0.5)
for q in LATTICE:
    dot(p, q, TEXT, 2.4)

# --- the line p + t v, dashed, and the three X arrows on it (blue) ------------------------------
guide(p, [on_line(-0.42), on_line(1.28)], TEXT, 0.55)
for t in (0.0, 0.5, 1.0):
    p.arrow(on_line(t), x_tip(on_line(t)), THEORY, 2.0, head=7.5)

# --- v (green) and nabla_v X = v (orange), true length -----------------------------------------
p.arrow(P0, on_line(1.0), BASE, 2.4, head=9)
p.arrow(shifted(P0), shifted(on_line(1.0)), PRACTICE, 2.2, head=8.5)

for t in (0.0, 0.5, 1.0):
    dot(p, on_line(t), TEXT, 3.4)

# --- labels -------------------------------------------------------------------------------------
IT_T = ital("t") + " = "
# p, below-right (the dashed line runs down-left, the orange arrow starts just above the text)
p.label(*P0, bold("p") + " = (2, 1)", 16, 22, TEXT, 11.5, "start")
p.label(*P0, IT_T + "0", 16, 35, TEXT, 10.5, "start")
# t = 1/2, below-left of the dot, clear of the dashed line and of the grey arrow base (2, 2)
p.label(*on_line(0.5), IT_T + "1/2", -16, 16, TEXT, 10.5, "end")
# p + v = (3, 3), upper-left: the dashed line leaves to the upper right, the arrows arrive from below
p.label(*on_line(1.0), bold("p") + " + " + bold("v") + " = (3, 3)", -10, -4, TEXT, 11.5, "end")
p.label(*on_line(1.0), IT_T + "1", -10, -17, TEXT, 10.5, "end")
# vector parts of the blue arrows, at their tips
p.label(*x_tip(on_line(0.0)), "(2, 1)", 8, 4, THEORY, 10.5, "start")
p.label(*x_tip(on_line(0.5)), "(5/2, 2)", 8, 4, THEORY, 10.5, "start")
p.label(*x_tip(on_line(1.0)), "(3, 3)", 8, 4, THEORY, 10.5, "start")
# v, left of the green arrow at t = 1/4
p.label(*on_line(0.25), bold("v"), -9, 4, BASE, 12.5, "end")
# nabla_v X = v, right of the orange arrow at its middle
mx, my = shifted(on_line(0.5))
nabla_label(p.X(mx) + 9, p.Y(my) + 4,
            subs(bold("v")) + ital("X") + " = " + bold("v"), PRACTICE, 11.5)

# title: the field and the scale of its arrows
p.text_px(p.x0 + p.w / 2, p.y0 - 12,
          ital("X") + " = " + ital("x") + ital("U") + subs("1") + " + " + ital("y") + ital("U") + subs("2")
          + " okları 1/2 ölçeğinde", TEXT, 11.5, "middle")

OUT["kovaryant-konum-alani"] = figure(
    400, 392, [p],
    "Düzlemde <em>X</em> = <em>xU</em><sub>1</sub> + <em>yU</em><sub>2</sub> konum alanı: her noktadaki "
    "okun vektör kısmı noktanın kendisidir, okunaklılık için bütün <em>X</em> okları gerçek boyunun "
    "yarısıyla çizilmiştir. <strong>p</strong> = (2, 1) noktasından <strong>v</strong> = (1, 2) yönünde "
    "(yeşil ok, gerçek boyda) ilerlerken <strong>p</strong> + <em>t</em><strong>v</strong> "
    "noktalarındaki mavi okların vektör kısımları <em>t</em> = 0, 1/2, 1 için (2, 1), (5/2, 2), (3, 3), "
    "yani noktanın kendisidir; ok, nokta kadar değişir. Bu değişimin <em>t</em>&#8217;ye göre türevi "
    "olan turuncu ok &#8711;<sub><strong>v</strong></sub><em>X</em> = (1, 2), yeşil "
    "<strong>v</strong> okunun yanında ona paralel ve eşit boydadır: konum alanının türevi yönün "
    "kendisidir.",
    aria="xy duzleminde X = x U1 + y U2 konum alani: (1,1), (1,2), (2,2), (3,1), (1,3) noktalarinda "
         "gri oklar, vektor kisimlari noktanin koordinatlari, 1/2 olceginde; p = (2,1) noktasindan "
         "v = (1,2) yesil oku ve kesikli p + t v dogrusu; dogru uzerinde t = 0, 1/2, 1 noktalari "
         "(2,1), (5/2,2), (3,3) ve oradaki mavi X oklari (2,1), (5/2,2), (3,3); p'de v'ye paralel "
         "turuncu ok nabla_v X = (1,2) = v")

# ============================================================ kovaryant-sabit-uzunluk-diklik
# -*- coding: utf-8 -*-
# kovaryant-sabit-uzunluk-diklik: the plane of vector parts (first component to the right, second
# upward) with the unit circle. W = cos x U1 + sin x U2 has unit length everywhere. Along the line
# p + t V(p) through p = (pi/3, 1, 0) with V(p) = (-1, 0, pi/3) the first coordinate is x = pi/3 - t,
# so the arrow of W makes the angle pi/3 - t. Three unit arrows from the origin:
#   t = -pi/6 -> angle pi/2, (0, 1), light blue
#   t = 0     -> angle pi/3, W(p) = (1/2, sqrt3/2), dark blue
#   t = pi/6  -> angle pi/6, (sqrt3/2, 1/2), light blue
# From the tip of W(p) the derivative nabla_V W(p) = (sqrt3/2, -1/2) (orange) is tangent to the
# circle and perpendicular to W(p): a right-angle mark sits between them. A small clockwise arc arrow
# outside the circle shows how the tip travels as t grows. The whole circle is drawn; the otherwise
# empty lower-right corner holds the formulas of W, V and p.
import math

S3 = math.sqrt(3.0)
XR, YR = (-1.2, 2.35), (-1.2, 1.36)
p = cplane(28, 20, 384, XR, YR)

O = (0.0, 0.0)
W_MINUS = (0.0, 1.0)                    # t = -pi/6, angle pi/2
W_P = (0.5, S3 / 2)                     # t = 0, angle pi/3
W_PLUS = (S3 / 2, 0.5)                  # t = pi/6, angle pi/6
D = (S3 / 2, -0.5)                      # nabla_V W(p): the clockwise unit tangent at W(p)
TIP = (W_P[0] + D[0], W_P[1] + D[1])    # (1.366, 0.366)
LIGHT = 0.45                            # opacity of the two neighbouring arrows
R_ARC = 1.16                            # radius of the "t grows" arc arrow


def ital(s):
    return f'<tspan font-style="italic">{s}</tspan>'


def nabla(px, py, color, size=8.0, width=1.15):
    """The nabla sign drawn as an inverted triangle (the text font lacks the glyph):
    base at cap height, apex on the baseline."""
    p.add(f'<polygon points="{px:.1f},{py - size:.1f} {px + size:.1f},{py - size:.1f} '
          f'{px + size / 2:.1f},{py:.1f}" fill="none" stroke="{color}" stroke-width="{width}" '
          f'stroke-linejoin="round"/>')


def arc_arrow(r, a0_deg, a1_deg, color, width=1.3, head=7.0, opacity=0.8, n=60):
    """Circular arc about the origin from a0 to a1 (degrees) with an arrowhead at a1."""
    a0, a1 = math.radians(a0_deg), math.radians(a1_deg)
    pts = [(r * math.cos(a0 + (a1 - a0) * k / n), r * math.sin(a0 + (a1 - a0) * k / n))
           for k in range(n + 1)]
    p.line(pts[:-2], color, width, None, opacity)
    p.arrow(pts[-4], pts[-1], color, width, head, None, opacity)


# --- unit circle and axes ----------------------------------------------------------------------
p.circle(0, 0, 1, TEXT, 0.9, None, "none", 0.45)
p.origin_axes("1. bileşen", "2. bileşen", xticks=(1,), yticks=(1,))

# --- the three unit arrows: neighbours faded, W(p) full ------------------------------------------
p.arrow(O, W_MINUS, THEORY, 2.2, 9, None, LIGHT)
p.arrow(O, W_PLUS, THEORY, 2.2, 9, None, LIGHT)
p.arrow(O, W_P, THEORY, 2.6, 9)

# --- the derivative, tangent to the circle at the tip of W(p) -----------------------------------
p.arrow(W_P, TIP, PRACTICE, 2.4, 9)

# right-angle mark between W(p) (looking back toward the origin) and the derivative
s = 0.12
a = (W_P[0] * (1 - s), W_P[1] * (1 - s))
c = (W_P[0] + s * D[0], W_P[1] + s * D[1])
b = (a[0] + s * D[0], a[1] + s * D[1])
p.line([a, b, c], TEXT, 1.1, None, 0.8)

# clockwise arc arrow outside the circle: the tip travels this way as t grows
arc_arrow(R_ARC, 84, 45, TEXT, 1.3, 7, 0.75)

# --- points --------------------------------------------------------------------------------------
dot(p, O, TEXT, 2.6)
for q in (W_MINUS, W_P, W_PLUS):
    dot(p, q, TEXT, 2.6)

# --- labels --------------------------------------------------------------------------------------
IT_T = ital("t") + " = "
p.label(0, 0.5, IT_T + MINUS_S + PI_S + "/6", -9, 4, TEXT, 11, "end")
p.label(W_PLUS[0] / 2, W_PLUS[1] / 2, IT_T + PI_S + "/6", 2, 13, TEXT, 11, "start")
# W(p): left of the shaft at height 0.8, in the pocket between the y axis and the arrow
# (the circle is still 7 px above the text there)
p.label(0.8 / S3, 0.8, ital("W") + "(" + bold("p") + ")", -8, 4, THEORY, 12, "end")
p.label(1.26 * math.cos(math.radians(57)), 1.26 * math.sin(math.radians(57)),
        ital("t") + " artar", 4, 0, TEXT, 11, "start")

# derivative label above the orange arrow: drawn nabla, subscript V, then the rest as text
q = (W_P[0] + 0.55 * D[0], W_P[1] + 0.55 * D[1])
gx, gy = p.X(q[0]) + 10, p.Y(q[1]) - 8
nabla(gx, gy, PRACTICE)
p.text_px(gx + 8.5, gy,
          subs(ital("V")) + ital("W") + "(" + bold("p") + ") = (&#8730;3/2, " + MINUS_S + "1/2)",
          PRACTICE, 11.5)

# formulas in the empty lower-right corner
U = ital("U")
LX = 1.12
p.label(LX, -0.45, ital("W") + " = cos " + ital("x") + " " + U + subs("1") + " + sin " + ital("x") + " "
        + U + subs("2"), 0, 0, TEXT, 11.5)
p.label(LX, -0.65, ital("V") + " = " + MINUS_S + ital("y") + U + subs("1") + " + " + ital("x") + U + subs("3"),
        0, 0, TEXT, 11.5)
p.label(LX, -0.85, bold("p") + " = (" + PI_S + "/3, 1, 0)", 0, 0, TEXT, 11.5)

OUT["kovaryant-sabit-uzunluk-diklik"] = figure(
    440, 320, [p],
    "<em>W</em> = cos <em>x</em> <em>U</em><sub>1</sub> + sin <em>x</em> <em>U</em><sub>2</sub> alanının "
    "her oku birim uzunluktadır; vektör kısımları birinci ve ikinci bileşen düzlemine çizilince uçları "
    "birim çember üzerinde kalır. <strong>p</strong> = (&#960;/3, 1, 0) noktasından "
    "<em>V</em>(<strong>p</strong>) = (&#8722;1, 0, &#960;/3) yönünde ilerlerken <em>x</em> = &#960;/3 &#8722; <em>t</em> "
    "olur; <em>t</em> = &#8722;&#960;/6, 0, &#960;/6 anlarındaki oklar &#960;/2, &#960;/3, &#960;/6 açılarındadır "
    "ve <em>W</em>(<strong>p</strong>) = (1/2, &#8730;3/2) okunun ucu <em>t</em> arttıkça çember üzerinde saat "
    "yönünde dolaşır. Ucun hızı olan &#8711;<sub><em>V</em></sub><em>W</em>(<strong>p</strong>) = "
    "(&#8730;3/2, &#8722;1/2) (turuncu) çembere teğettir, dolayısıyla yarıçap doğrultusundaki "
    "<em>W</em>(<strong>p</strong>)&#8217;ye diktir; aradaki dik açı işareti bunu gösterir.",
    aria="Vektor kisimlari duzleminde birim cember ve orijinden cikan uc birim ok: t = -pi/6 icin (0, 1), "
         "t = 0 icin W(p) = (1/2, sqrt3/2), t = pi/6 icin (sqrt3/2, 1/2). W(p) okunun ucundan cikan turuncu "
         "ok nabla_V W(p) = (sqrt3/2, -1/2) cembere teget ve W(p)'ye dik, aralarinda dik aci isareti; "
         "cemberin disindaki kucuk yay oku ucun t arttikca saat yonunde dolastigini gosterir")

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

# ============================================================ yay-dogru-en-kisa-yol
# -*- coding: utf-8 -*-
# yay-dogru-en-kisa-yol: the straight segment is the shortest path (2D, xy plane).
# p = (0, 0), q = (2, 0); the segment p-q is thick green (d(p, q) = 2); the wavy path
# alpha(t) = (t, sin pi t), 0 <= t <= 2, is orange (L(alpha) ~ 4.61). At alpha(1/4) = (0.25, 0.71)
# the blue velocity arrow has vector part (1, pi cos(pi/4)) = (1, 2.22); its projection onto
# u = (1, 0) is the short grey arrow (1, 0) = 1 * u, with a dashed drop from the blue tip to the
# grey tip and a right-angle mark at the foot. u itself sits at p as a small arrow on top of
# the segment. Labels carry the inequality ||alpha'|| >= alpha' . u.
import math

XR, YR = (-0.9, 2.85), (-1.55, 3.3)
PW = 330                                    # panel width in px -> 88 px per unit
p = cplane(35, 22, PW, XR, YR)
PPU = PW / (XR[1] - XR[0])

P0 = (0.0, 0.0)                             # p
Q0 = (2.0, 0.0)                             # q
U = (1.0, 0.0)                              # unit vector u
T0 = 0.25
A = (T0, math.sin(math.pi * T0))            # alpha(1/4) = (0.25, 0.7071)
V = (1.0, math.pi * math.cos(math.pi * T0))  # alpha'(1/4) = (1, 2.2214)
TIP = (A[0] + V[0], A[1] + V[1])            # (1.25, 2.9285)
FOOT = (A[0] + U[0], A[1] + U[1])           # tip of the projection (alpha'.u) u = u: (1.25, 0.7071)


def ital(s):
    return f'<tspan font-style="italic">{s}</tspan>'


def mfmt(v):
    """Tick label with a Turkish decimal comma and a real minus sign."""
    return tfmt(v).replace("-", MINUS_S)


def wave(t):
    return math.sin(math.pi * t)


ALPHA = ital("&#945;")
T = ital("t")
DBAR = "&#8214;"
AP = ALPHA + PRIME                          # alpha'

# 1. axes through the origin; the segment p-q lies on the x axis. No x ticks: the curve passes
#    through (1, 0) and (2, 0) steeply, so tick labels there would sit on it; p, q, 0,25 read the x axis
p.origin_axes("x", "y", yticks=(-1, 1, 2, 3), xfmt=mfmt, yfmt=mfmt)

# 2. dashed guides reading the coordinates of alpha(1/4) off the axes
guide(p, [(0.0, A[1]), A], TEXT, 0.5)
guide(p, [(A[0], 0.0), A], TEXT, 0.5)

# 3. the straight segment (green, thick) and the wavy path (orange)
p.line([P0, Q0], BASE, 4.5)
curve(p, wave, 0.0, 2.0, PRACTICE, 2.4, samples=240)

# 4. u at p, drawn on top of the segment at full TEXT opacity: a translucent stroke would blend
#    into the green and lose the arrowhead
p.arrow(P0, U, TEXT, 1.7, head=7)

# 5. dashed drop from the velocity tip to the foot of the projection, right-angle mark at the foot
guide(p, [TIP, FOOT], TEXT, 0.55)
s = 9.0 / PPU
p.line([(FOOT[0] - s, FOOT[1]), (FOOT[0] - s, FOOT[1] + s), (FOOT[0], FOOT[1] + s)], TEXT, 1.0, None, 0.7)

# 6. the projection and the velocity (blue). The projection is TEXT at reduced opacity so it reads as
#    the "gri ok" of the caption in both themes (the axes are the only other grey arrows)
p.arrow(A, FOOT, TEXT, 2.0, head=7.5, opacity=0.62)
p.arrow(A, TIP, THEORY, 2.4, head=9)

# 7. points
dot(p, P0, TEXT, 3.6)
dot(p, Q0, TEXT, 3.6)
dot(p, A, TEXT, 3.4)

# 8. labels
p.label(*P0, bold("p") + " = (0, 0)", -8, 15, TEXT, 11.5, "end")
p.label(*Q0, bold("q") + " = (2, 0)", 8, -8, TEXT, 11.5, "start")
p.label(0.62, 0.0, bold("u"), 0, 15, TEXT, 12, "middle")
p.label(A[0], 0.0, "0,25", 0, 15, TEXT, 10.5, "middle")
# the point is named where its horizontal guide meets the y axis, on the free left side
p.label(0.0, A[1], ALPHA + "(1/4) =", -8, -3, TEXT, 11.5, "end")
p.label(0.0, A[1], "(0,25; 0,71)", -8, 11, TEXT, 11.5, "end")
p.label(*TIP, AP + "(1/4) = (1; 2,22)", 0, -9, THEORY, 11.5, "middle")
p.label(*FOOT, AP + " " + CDOT + " " + bold("u") + " = 1", 11, 4, TEXT, 11.5, "start")
p.label(FOOT[0], 1.9, DBAR + AP + DBAR + " " + GEQ_S + " " + AP + " " + CDOT + " " + bold("u"),
        12, 0, TEXT, 12.5, "start")
p.label(1.5, 0.0, ital("d") + "(" + bold("p") + ", " + bold("q") + ") = 2", 0, -8, BASE, 11.5, "middle")
p.label(1.5, -1.0, ALPHA + "(" + T + ") = (" + T + ", sin " + PI_S + T + ")", 0, 17, PRACTICE, 11.5, "middle")
p.label(1.5, -1.0, ital("L") + "(" + ALPHA + ") " + APPROX + " 4,61", 0, 31, PRACTICE, 11.5, "middle")

OUT["yay-dogru-en-kisa-yol"] = figure(
    400, int(22 + p.h + 22), [p],
    "<strong>p</strong> = (0, 0) ile <strong>q</strong> = (2, 0) arasındaki yeşil doğru parçasının uzunluğu "
    "<em>d</em>(<strong>p</strong>, <strong>q</strong>) = 2, turuncu dalgalı yol "
    "&#945;(<em>t</em>) = (<em>t</em>, sin &#960;<em>t</em>), 0 &#8804; <em>t</em> &#8804; 2, ise "
    "<em>L</em>(&#945;) &#8776; 4,61 uzunluğundadır. &#945;(1/4) = (0,25; 0,71) noktasındaki mavi hız oku "
    "&#945;&#8242;(1/4) = (1; 2,22)&#8217;nin <strong>u</strong> = (1, 0) birim vektörü üzerine izdüşümü gri "
    "ok (1, 0)&#8217;dır: uzunluğu &#945;&#8242; &#183; <strong>u</strong> = 1 olup hızın boyunu aşamaz. "
    "Her anda geçerli olan &#8214;&#945;&#8242;&#8214; &#8805; &#945;&#8242; &#183; <strong>u</strong> "
    "eşitsizliği integral alınınca <em>L</em>(&#945;) &#8805; <em>d</em>(<strong>p</strong>, <strong>q</strong>) verir.",
    aria="xy duzleminde p = (0, 0) ile q = (2, 0) arasinda kalin yesil dogru parcasi (uzunluk 2) ve "
         "turuncu dalgali yol alpha(t) = (t, sin pi t), t 0'dan 2'ye (uzunluk yaklasik 4,61). "
         "alpha(1/4) = (0,25; 0,71) noktasindan cikan mavi hiz oku (1; 2,22), onun u = (1, 0) uzerine "
         "izdusumu olan kisa gri ok (1, 0), ucundan inen kesikli dikme ve dik aci isareti; p'de kucuk "
         "u oku; etiket: ||alpha'|| >= alpha' . u",
)

# ============================================================ yay-helis-paralel-alan
# -*- coding: utf-8 -*-
# yay-helis-paralel-alan: two vector fields on the helix alpha(t) = (cos t, sin t, t), 0 <= t <= 2pi.
# V = U3 (green): at t = 0, pi/2, pi, 3pi/2, 2pi the same vector part (0, 0, 1) — a parallel field.
# Y = cos t U1 + sin t U2 (orange): vector parts (1, 0, 0), (0, 1, 0), (-1, 0, 0), (0, -1, 0), (1, 0, 0)
# — the arrow turns with the helix, so Y is not parallel.
# Camera az = 56, el = 12 (from _scan_paralel_alan.py): near the textbook view (az ~ 45, el ~ 22) the
# green tip at t = 3pi/2 lands on the point t = 2pi and the helix runs along two green arrows;
# a lower, more side-on camera keeps every arrow clear of the curve and of the other markers.
import math

AZ, EL = 56.0, 12.0
PHI = math.radians(AZ)
TS = (0.0, math.pi / 2, math.pi, 3 * math.pi / 2, 2 * math.pi)
E3 = (0.0, 0.0, 1.0)
XMAX, YMAX, ZMAX = 2.7, 2.7, 7.6


def helix(t):
    return (math.cos(t), math.sin(t), t)


def radial(t):
    """Vector part of Y(t) = cos t U1 + sin t U2."""
    return (math.cos(t), math.sin(t), 0.0)


def it(s):
    return f'<tspan font-style="italic">{s}</tspan>'


def helix_piece(t0, t1, opacity):
    S.curve(helix, t0, t1, TEXT, 1.7, samples=160, opacity=opacity)


P = space_panel(14, 12, 312, (-3.0, 3.0), (-0.9, 7.7))
S = Space(P, Camera(azimuth=AZ, elevation=EL, scale=1.0))

# 1. floor: faint grid and the dashed unit circle the helix winds over
S.floor_grid((-2, 2), (-2, 2), n=4, opacity=0.10)
S.circle((0, 0, 0), (1, 0, 0), (0, 1, 0), 1.0, TEXT, 0.9, dash="4 3", opacity=0.45)

# 2. the half of the helix that lies behind the z axis (cos(t - AZ) < 0), drawn lighter
helix_piece(PHI + math.pi / 2, PHI + 3 * math.pi / 2, 0.32)

# 3. axes and ticks
S.axes(XMAX, YMAX, ZMAX)
S.ticks("x", (2,), offset=(-12, 12))          # the tick at 1 would sit under the point t = 0
S.ticks("y", (1, 2), offset=(2, 13))
S.ticks("z", (1, 2, 3, 4, 5, 6))

# 4. the near half of the helix (gray: the curve is the stage, the fields are the subject)
helix_piece(0.0, PHI + math.pi / 2, 0.5)
helix_piece(PHI + 3 * math.pi / 2, 2 * math.pi, 0.5)

# 5. the two fields at the five sample points: Y (orange, radial) and V = U3 (green, vertical)
for t in TS:
    B = helix(t)
    S.arrow(B, vadd(B, radial(t)), PRACTICE, 2.4, head=8)
    S.arrow(B, vadd(B, E3), BASE, 2.4, head=8)
for t in TS:
    S.point(helix(t), TEXT, 3.4)

# 6. labels ---------------------------------------------------------------------------------
IT_T = it("t") + " = "
p0, p1, p2, p3, p4 = (helix(t) for t in TS)
# t = 0 sits on the dashed unit circle, so its label goes beside the green shaft, not the point
S.label(vadd(p0, vscale(0.3, E3)), IT_T + "0", -8, 4, TEXT, 11, "end")
S.label(p1, IT_T + PI_S + "/2", 6, 21, TEXT, 11, "start")
S.label(p2, IT_T + PI_S, -8, 12, TEXT, 11, "end")
S.label(p3, IT_T + "3" + PI_S + "/2", -8, 14, TEXT, 11, "end")
S.label(p4, IT_T + "2" + PI_S, 8, -3, TEXT, 11, "start")

# vector parts of Y at the orange tips — they change with t
o_tips = [vadd(helix(t), radial(t)) for t in TS]
# at t = 0 the arrow lies on the x axis: its label hangs under the shaft
S.label(o_tips[0], "(1, 0, 0)", 5, 17, PRACTICE, 10.5, "start")
S.label(o_tips[1], "(0, 1, 0)", 7, -2, PRACTICE, 10.5, "start")
S.label(o_tips[2], "(" + MINUS_S + "1, 0, 0)", 7, 4, PRACTICE, 10.5, "start")
S.label(o_tips[3], "(0, " + MINUS_S + "1, 0)", -7, 4, PRACTICE, 10.5, "end")
S.label(o_tips[4], "(1, 0, 0)", -7, 4, PRACTICE, 10.5, "end")

# vector part of V at the green tips — the same (0, 0, 1) everywhere; at t = pi/2 and 3pi/2 the helix
# runs right past the tip, so those two stay unlabelled
g_tips = [vadd(helix(t), E3) for t in TS]
S.label(g_tips[0], "(0, 0, 1)", -7, 3, BASE, 10.5, "end")
S.label(g_tips[2], "(0, 0, 1)", 7, 0, BASE, 10.5, "start")
S.label(g_tips[4], "(0, 0, 1)", -7, 3, BASE, 10.5, "end")

# field names
S.label(vadd(p4, vscale(0.55, E3)), it("V") + " = " + it("U") + subs("3"), 8, 4, BASE, 12, "start")
S.label(vadd(p2, vscale(0.5, radial(math.pi))), it("Y"), 0, -8, PRACTICE, 12.5, "middle")
S.label(helix(2.3), it("&#945;"), 11, 3, TEXT, 12.5, "start")

OUT["yay-helis-paralel-alan"] = figure(
    340, 472, [P],
    "&#945;(<em>t</em>) = (cos <em>t</em>, sin <em>t</em>, <em>t</em>) helisi üzerinde iki vektör alanı, "
    "<em>t</em> = 0, &#960;/2, &#960;, 3&#960;/2, 2&#960; noktalarında. Yeşil oklar <em>V</em> = <em>U</em><sub>3</sub> "
    "alanının değerleridir: her birinin vektör kısmı (0, 0, 1)'dir, oklar birbirinin ötelenmiş kopyasıdır; "
    "<em>V</em> paraleldir. Turuncu oklar <em>Y</em> = cos <em>t</em> <em>U</em><sub>1</sub> + sin <em>t</em> <em>U</em><sub>2</sub> "
    "alanının değerleridir: vektör kısımları (1, 0, 0), (0, 1, 0), (&#8722;1, 0, 0), (0, &#8722;1, 0), (1, 0, 0) "
    "diye helisle birlikte döner; uzunluk hep 1 olsa da yön değiştiği için <em>Y</em> paralel değildir.",
    aria="Helis alpha(t) = (cos t, sin t, t), t 0 ile 2pi arasinda, gri; t = 0, pi/2, pi, 3pi/2, 2pi noktalarinda "
         "yesil dusey oklar, hepsinin vektor kismi (0, 0, 1): paralel alan V = U_3; ayni noktalarda turuncu "
         "radyal oklar (1, 0, 0), (0, 1, 0), (-1, 0, 0), (0, -1, 0), (1, 0, 0): paralel olmayan alan Y",
)

# ============================================================ yay-helis-surat-yay-uzunlugu
# -*- coding: utf-8 -*-
# yay-helis-surat-yay-uzunlugu: the helix alpha(t) = (3 cos t, 3 sin t, 4t), one full turn on the
# cylinder x^2 + y^2 = 9 (thin grey), with the quarter turn t in [0, pi/2] in thick orange
# (length 5pi/2 = 7.85), the velocity vectors (0, 3, 4) at alpha(0) = (3, 0, 0) and (-3, 0, 4) at
# alpha(pi/2) = (0, 3, 2pi) in blue (both of length 5), and the dashed chord between the two
# points (length 7.58).
# Camera az = -12, el = 28 (from _scan_yay_helis.py): the chord and the start velocity leave
# alpha(0) at 20 degrees on the page and the arrow tip clears the arc by 0.87 units; the usual
# az = 20..35 views look along the arc's bulge, which lays the blue arrow on top of the orange arc.
# Painter's order as in egri-helis-hiz-vektorleri: far wall, far pieces, inner axes, near wall,
# near pieces, then the highlighted quarter turn, arrows, points and text.
import math

AZ, EL = -12.0, 28.0
A, B = 3.0, 4.0                       # radius and pitch constant
TQ = math.pi / 2                      # end of the quarter turn
TEND = 2 * math.pi                    # one full turn
Z0, Z1 = 0.0, 8 * math.pi + 0.4       # height range of the drawn cylinder
ZTIP = Z1 + 2.6                       # z axis arrow tip; shorter and the head sits on the top rim's back edge
XMAX, YMAX = 4.8, 4.4                 # x and y axis arrow tips (x is foreshortened: a longer stub)
PHI = math.radians(AZ)                # cos(u - PHI) > 0 on the half of the tube facing the viewer
FAR = (PHI + math.pi / 2, PHI + 3 * math.pi / 2)
NEAR = (PHI - math.pi / 2, PHI + math.pi / 2)
IT_A = '<tspan font-style="italic">&#945;</tspan>'


def helix(t):
    return (A * math.cos(t), A * math.sin(t), B * t)


def velocity(t):
    """Vector part of alpha'(t)."""
    return (-A * math.sin(t), A * math.cos(t), B)


def tube(u, z):
    return (A * math.cos(u), A * math.sin(u), z)


def near(u):
    return math.cos(u - PHI) > 0


def rim_arc(z, u0, u1, dash=None, opacity=0.5, n=60):
    S.line([tube(u0 + (u1 - u0) * k / n, z) for k in range(n + 1)], TEXT, 0.9, dash, opacity)


def helix_runs(front, t0, t1, n=900):
    """Maximal pieces of the helix on the near (front=True) or far half of the tube."""
    ts = [t0 + (t1 - t0) * k / n for k in range(n + 1)]
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


def tick_mark(Q, d, half=0.15):
    """Short tick through an axis point Q along direction d."""
    S.line([vadd(Q, vscale(-half, d)), vadd(Q, vscale(half, d))], TEXT, 1.0, None, 0.7)


P = space_panel(16, 14, 376, (-9.6, 9.2), (-3.3, 25.4))   # 20 px per unit
S = Space(P, Camera(azimuth=AZ, elevation=EL, scale=1.0))

A0, AQ = helix(0), helix(TQ)                    # (3, 0, 0) and (0, 3, 2pi)
V0, VQ = velocity(0), velocity(TQ)              # (0, 3, 4) and (-3, 0, 4)
TIP0, TIPQ = vadd(A0, V0), vadd(AQ, VQ)         # (3, 3, 4) and (-3, 3, 4 + 2pi)
ZTICKS = (2 * math.pi, 4 * math.pi, 6 * math.pi, 8 * math.pi)

# --- far half of the tube and what lies behind the near wall ----------------------------------
S.surface(tube, FAR, (Z0, Z1), nu=24, nv=1, fill=TEXT, stroke="none", opacity=(0.015, 0.06))
rim_arc(Z0, *FAR, dash="3 3", opacity=0.35)
rim_arc(Z1, *FAR, opacity=0.4)
for run in helix_runs(False, TQ, TEND):
    S.line(run, TEXT, 1.3, None, 0.4)

# axes inside the tube
S.line([(0, 0, 0), (A, 0, 0)], TEXT, 1.0, None, 0.35)
S.line([(0, 0, 0), (0, A, 0)], TEXT, 1.0, None, 0.35)
S.line([(0, 0, 0), (0, 0, Z1)], TEXT, 1.0, None, 0.4)
for z in ZTICKS:
    tick_mark((0, 0, z), (1, 0, 0))

# the velocity at alpha(pi/2) starts on the far side of the tube and stays behind the near wall
S.arrow(AQ, TIPQ, THEORY, 2.4, head=9)

# --- near half of the tube -------------------------------------------------------------------
S.surface(tube, NEAR, (Z0, Z1), nu=24, nv=1, fill=TEXT, stroke="none", opacity=(0.015, 0.06))
rim_arc(Z0, *NEAR, opacity=0.5)
rim_arc(Z1, *NEAR, opacity=0.5)
for u in NEAR:
    S.line([tube(u, Z0), tube(u, Z1)], TEXT, 0.9, None, 0.45)
for run in helix_runs(True, TQ, TEND):
    S.line(run, TEXT, 1.3, None, 0.7)
S.hollow(helix(TEND), TEXT, 2.8, 1.2)           # end of the full turn, right above alpha(0)

# axes outside the tube
S.arrow((A, 0, 0), (XMAX, 0, 0), TEXT, 1.1, 7, None, 0.55)
S.arrow((0, A, 0), (0, YMAX, 0), TEXT, 1.1, 7, None, 0.55)
S.arrow((0, 0, Z1), (0, 0, ZTIP), TEXT, 1.1, 7, None, 0.55)
tick_mark((0, A, 0), (1, 0, 0))

# --- the quarter turn, its chord, the velocity at alpha(0), the two points -------------------
S.guide([A0, AQ], TEXT, 0.6, 1.1, "5 3")
S.curve(helix, 0.0, TQ, PRACTICE, 2.8, samples=120)
S.arrow(A0, TIP0, THEORY, 2.4, head=9)
S.point(A0, TEXT, 3.6)
S.point(AQ, TEXT, 3.6)

# --- labels ----------------------------------------------------------------------------------
S.label((XMAX, 0, 0), "x", -4, 13, TEXT, 11.5, "middle", False, True)
S.label((0, YMAX, 0), "y", 10, 4, TEXT, 11.5, "middle", False, True)
S.label((0, 0, ZTIP), "z", -10, -4, TEXT, 11.5, "middle", False, True)
S.label((0, A, 0), "3", 9, 15, TEXT, 10, "middle")   # outside the tube's edge, under the y axis
for k, z in enumerate(ZTICKS, start=1):
    S.label((0, 0, z), "%d" % (2 * k) + PI_S, -8, 4, TEXT, 10, "end")

S.label(A0, IT_A + "(0) = (3, 0, 0)", -9, 19, TEXT, 11, "end")
S.label(AQ, IT_A + "(" + PI_S + "/2) = (0, 3, 2" + PI_S + ")", 11, 4, TEXT, 11, "start")

S.label(TIP0, IT_A + PRIME + "(0) = (0, 3, 4)", 12, 1, THEORY, 11, "start")
S.label(TIP0, "uzunluk 5", 12, 15, THEORY, 10.5, "start")
mid_q = vadd(AQ, vscale(0.65, VQ))
S.label(mid_q, IT_A + PRIME + "(" + PI_S + "/2) = (" + MINUS_S + "3, 0, 4)", 12, -2, THEORY, 11, "start")
S.label(mid_q, "uzunluk 5", 12, 12, THEORY, 10.5, "start")

S.label(helix(math.radians(74)), "5" + PI_S + "/2 " + APPROX + " 7,85", 12, 4, PRACTICE, 11, "start")
S.label(vadd(A0, vscale(0.88, vsub(AQ, A0))), APPROX + " 7,58", -9, 4, TEXT, 10, "end")

S.label(helix(3 * math.pi / 2), IT_A, -10, 4, TEXT, 12.5, "end")
S.label(helix(3 * math.pi / 2), "bir tam tur: 10" + PI_S + " " + APPROX + " 31,4", -10, 19, TEXT, 10.5, "end")

OUT["yay-helis-surat-yay-uzunlugu"] = figure(
    400, 600, [P],
    "<em>a</em> = 3, <em>b</em> = 4 için &#945;(<em>t</em>) = (3cos <em>t</em>, 3sin <em>t</em>, 4<em>t</em>) "
    "helisinin <em>x</em><sup>2</sup> + <em>y</em><sup>2</sup> = 9 silindirine sarılan bir tam turu (ince gri) "
    "ve <em>t</em> = 0&#8217;dan <em>t</em> = &#960;/2&#8217;ye çeyrek turu (kalın turuncu). "
    "Mavi oklar &#945;(0) = (3, 0, 0) ve &#945;(&#960;/2) = (0, 3, 2&#960;) noktalarındaki hız vektörleridir; "
    "vektör kısımları (0, 3, 4) ve (&#8722;3, 0, 4) farklı olsa da ikisinin de uzunluğu 5&#8217;tir, "
    "çünkü helisin sürati sabittir. Sürat sabit olduğundan çeyrek turun uzunluğu "
    "5 &#183; &#960;/2 = 5&#960;/2 &#8776; 7,85&#8217;tir; aynı iki noktayı birleştiren kesikli doğru parçası ise "
    "yalnızca &#8776; 7,58 uzunluğundadır: eğri üzerinden gidilen yol kestirmeden uzundur.",
    aria="Silindir x^2 + y^2 = 9 uzerinde alpha(t) = (3cos t, 3sin t, 4t) helisinin bir tam turu ince gri; "
         "t = 0'dan pi/2'ye ceyrek tur kalin turuncu, uzunlugu 5pi/2 = 7,85; alpha(0) = (3, 0, 0) ve "
         "alpha(pi/2) = (0, 3, 2pi) noktalarinda mavi hiz vektorleri (0, 3, 4) ve (-3, 0, 4), ikisi de 5 "
         "uzunlugunda; iki nokta arasindaki kesikli dogru parcasi 7,58 uzunlugunda",
)

# ============================================================ yay-helis-teget-olmayan-alan
# -*- coding: utf-8 -*-
# yay-helis-teget-olmayan-alan: the helix alpha(t) = (cos t, sin t, t), t in [0, 2pi], drawn grey,
# with two vector fields on it at t = 0, pi/2, pi, 3pi/2, 2pi:
#   Y(t)      vector part (cos t, sin t, 0)   — orange, horizontal, pointing away from the axis
#   alpha'(t) vector part (-sin t, cos t, 1)  — blue, tangent to the helix
# The axis of the helix (the z axis) is dashed. Painter's order: far arrows (t = pi, 3pi/2, which
# lie on the side away from the viewer), far pieces of the helix, the z axis, near pieces of the
# helix, near arrows, points, labels.
# Camera az = 35, el = 18: the tip of Y(2pi) (which points toward the viewer) and the head of
# alpha'(3pi/2) approach each other for az near 45, while for az below 30 the last quarter turn of
# the helix runs through the tip of Y(2pi); a lower elevation keeps Y(2pi) well above alpha(3pi/2).
import math

AZ, EL = 35.0, 18.0
PHI = math.radians(AZ)
TWO_PI = 2.0 * math.pi
TS = (0.0, math.pi / 2, math.pi, 3 * math.pi / 2, TWO_PI)
XMAX, YMAX, ZMAX = 2.7, 2.7, TWO_PI + 1.5
O = (0.0, 0.0, 0.0)


def helix(t):
    return (math.cos(t), math.sin(t), t)


def radial(t):
    """Vector part of Y(t)."""
    return (math.cos(t), math.sin(t), 0.0)


def velocity(t):
    """Vector part of alpha'(t)."""
    return (-math.sin(t), math.cos(t), 1.0)


def near(t):
    """True on the half of the helix facing the viewer."""
    return math.cos(t - PHI) > 0


def helix_runs(front, n=1400, trim=7):
    """Maximal pieces of the helix on the near (front=True) or far half.

    A far piece is cut `trim` samples (about 2.7 px) short at each seam with a near piece: the
    two runs are translucent, and the round cap of the near run drawn over the far run would
    otherwise leave a dark bead at the seam.
    """
    ts = [TWO_PI * k / n for k in range(n + 1)]
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
    if not front:
        out = [run[(trim if run[0] != helix(0.0) else 0):
                   (len(run) - trim if run[-1] != helix(TWO_PI) else len(run))] for run in out]
    return out


def field_arrows(t):
    B = helix(t)
    S.arrow(B, vadd(B, radial(t)), PRACTICE, 2.4, head=8.5)
    S.arrow(B, vadd(B, velocity(t)), THEORY, 2.4, head=8.5)


def tick_mark(Q, along):
    S.line([vadd(Q, vscale(-0.05, along)), vadd(Q, vscale(0.05, along))], TEXT, 1.0, None, 0.7)


P = space_panel(16, 14, 400, (-3.0, 3.0), (-1.5, 8.6))
S = Space(P, Camera(azimuth=AZ, elevation=EL, scale=1.0))

# --- floor reference: the unit circle under the helix ---------------------------------------
S.circle(O, (1, 0, 0), (0, 1, 0), 1.0, TEXT, 0.9, "3 3", 96, 0.35)

# --- x and y axes (no x tick: the point alpha(0) sits at x = 1 and the tip of Y(0) at x = 2) -----
S.arrow(O, (XMAX, 0, 0), TEXT, 1.1, 7, None, 0.55)
S.arrow(O, (0, YMAX, 0), TEXT, 1.1, 7, None, 0.55)
tick_mark((0, 1, 0), (1, 0, 0))
tick_mark((0, 2, 0), (1, 0, 0))

# --- far side: arrows at t = pi, 3pi/2 and the far pieces of the helix ------------------------
for t in TS:
    if not near(t):
        field_arrows(t)
for run in helix_runs(False):
    S.line(run, TEXT, 2.2, None, 0.4)

# --- the axis of the helix, dashed, with ticks on its left -------------------------------------
S.arrow(O, (0, 0, ZMAX), TEXT, 1.1, 7, "5 4", 0.6)
for k in (2, 4, 6):
    tick_mark((0, 0, k), (1, 0, 0))

# --- near side ------------------------------------------------------------------------------------
for run in helix_runs(True):
    S.line(run, TEXT, 2.4, None, 0.65)
for t in TS:
    if near(t):
        field_arrows(t)
for t in TS:
    S.point(helix(t), TEXT, 3.2)

# --- labels ---------------------------------------------------------------------------------------
IT = '<tspan font-style="italic">%s</tspan>'
IT_T = IT % "t" + " = "
IT_Y = IT % "Y"
IT_A = IT % "&#945;"
S.label((XMAX, 0, 0), "x", -4, 13, TEXT, 11.5, "middle", False, True)
S.label((0, YMAX, 0), "y", 10, 4, TEXT, 11.5, "middle", False, True)
S.label((0, 0, ZMAX), "z", -10, -4, TEXT, 11.5, "middle", False, True)
S.label((0, 1, 0), "1", 0, 14, TEXT, 10, "middle")
S.label((0, 2, 0), "2", 0, 14, TEXT, 10, "middle")
for k in (2, 4, 6):
    S.label((0, 0, k), str(k), -9, 4, TEXT, 10, "end")

# t labels: each in the free wedge around its point (between the two arrows and the curve)
S.label(helix(0), IT_T + "0", -14, -3, TEXT, 11, "end")                     # between circle and Y(0)
S.label(helix(math.pi / 2), IT_T + PI_S + "/2", -9, 4, TEXT, 11, "end")     # left, curve arrives from below-left
S.label(helix(math.pi), IT_T + PI_S, -7, 14, TEXT, 11, "end")               # below-left, clear of the z axis
S.label(helix(3 * math.pi / 2), IT_T + "3" + PI_S + "/2", -9, 13, TEXT, 11, "end")   # below-left, under Y(3pi/2)
S.label(helix(TWO_PI), IT_T + "2" + PI_S, -8, -8, TEXT, 11, "end")          # up-left: blue leaves up-right, curve arrives from below-left

# field labels at t = 0, pi/2 and 2pi
S.label(vadd(helix(0), radial(0)), IT_Y + "(0)", 6, 12, PRACTICE, 11.5, "start")
S.label(vadd(helix(0), velocity(0)), IT_A + PRIME + "(0)", 6, 7, THEORY, 11.5, "start")   # under the curve, above the unit circle
S.label(vadd(helix(math.pi / 2), radial(math.pi / 2)), IT_Y + "(" + PI_S + "/2)", 6, 4, PRACTICE, 11.5, "start")
S.label(vadd(helix(math.pi / 2), velocity(math.pi / 2)), IT_A + PRIME + "(" + PI_S + "/2)", 7, 0, THEORY, 11.5, "start")
S.label(vadd(helix(TWO_PI), radial(TWO_PI)), IT_Y + "(2" + PI_S + ")", -6, 0, PRACTICE, 11.5, "end")   # left of the tip, above the head of alpha'(3pi/2)
S.label(vadd(helix(TWO_PI), velocity(TWO_PI)), IT_A + PRIME + "(2" + PI_S + ")", 7, 4, THEORY, 11.5, "start")
S.label(helix(4.1), IT_A, -8, 2, TEXT, 12.5, "end")

OUT["yay-helis-teget-olmayan-alan"] = figure(
    432, 620, [P],
    "Gri eğri <em>&#945;</em>(<em>t</em>) = (cos <em>t</em>, sin <em>t</em>, <em>t</em>) helisidir; "
    "<em>t</em> = 0, &#960;/2, &#960;, 3&#960;/2, 2&#960; anlarında iki vektör alanı çizilmiştir. "
    "Turuncu oklar <em>Y</em>(<em>t</em>)&#8217;dir: vektör kısmı (cos <em>t</em>, sin <em>t</em>, 0) "
    "olduğundan her ok yataydır ve helisin ekseninden (kesikli <em>z</em> ekseni) dışarıya bakar. "
    "Mavi oklar hız vektörleri <em>&#945;</em>&#8242;(<em>t</em>)&#8217;dir; vektör kısmı "
    "(&#8722;sin <em>t</em>, cos <em>t</em>, 1) hep 1 birim yükselir ve eğriye teğettir. "
    "Aynı noktada duran turuncu ve mavi oklar birbirine diktir; <em>Y</em> eğri üzerinde bir vektör "
    "alanıdır, ama hiçbir anda eğriye teğet değildir.",
    aria="Helis alpha(t) = (cos t, sin t, t), t 0 ile 2pi arasinda, gri egri; t = 0, pi/2, pi, "
         "3pi/2, 2pi noktalarinda turuncu Y oklari (vektor kisimlari (1, 0, 0), (0, 1, 0), "
         "(-1, 0, 0), (0, -1, 0), (1, 0, 0), yatay ve eksenden disa) ve mavi hiz oklari "
         "(0, 1, 1), (-1, 0, 1), (0, -1, 1), (1, 0, 1), (0, 1, 1); z ekseni kesikli",
)

# ============================================================ yay-iki-egri-parcasi
# -*- coding: utf-8 -*-
# yay-iki-egri-parcasi: two curve segments from the origin to (0, pi^2, 0) on 0 <= t <= pi,
#   alpha(t) = (sin t, -t^2 cos t, sin 2t)          orange, L ~ 12.92
#   beta(t)  = (t^2 sin t, t^2, t^2 (1 + cos t))    blue,   L ~ 14.46
# The chord joining the end points is the y-axis piece from 0 to pi^2 (length pi^2 ~ 9.87), so the
# y axis is drawn as that dashed grey chord plus a solid arrow beyond the far end point.
# Dots mark t = pi/4, pi/2, 3pi/4 on both curves.  Camera az = 30, el = 16 (from _scan_yay2.py):
# a low elevation keeps alpha (below the floor) and beta (above it) apart on their final approach.
import math

PI = math.pi
PI2 = PI * PI                       # 9.8696
AZ, EL = 30.0, 16.0
XMAX, YMAX, ZMIN, ZMAX = 4.6, 11.0, -1.35, 2.9
TS = (PI / 4, PI / 2, 3 * PI / 4)


def alpha(t):
    return (math.sin(t), -t * t * math.cos(t), math.sin(2 * t))


def beta(t):
    return (t * t * math.sin(t), t * t, t * t * (1 + math.cos(t)))


def ital(s):
    return f'<tspan font-style="italic">{s}</tspan>'


P = space_panel(16, 14, 550, (-2.7, 9.8), (-2.0, 3.1))
S = Space(P, Camera(azimuth=AZ, elevation=EL, scale=1.0))

# 1. floor grid z = 0 over 0 <= x <= 4, 0 <= y <= 10 (unit cells)
for k in range(5):
    S.line([(k, 0, 0), (k, 10, 0)], TEXT, 0.7, None, 0.10)
for k in range(11):
    S.line([(0, k, 0), (4, k, 0)], TEXT, 0.7, None, 0.10)

# 2. axes: x and z as arrows; the y axis is the dashed chord 0..pi^2 and an arrow past the end
S.arrow((0, 0, 0), (XMAX, 0, 0), TEXT, 1.1, 7, None, 0.55)
S.line([(0, 0, ZMIN), (0, 0, 0)], TEXT, 1.1, None, 0.55)
S.arrow((0, 0, 0), (0, 0, ZMAX), TEXT, 1.1, 7, None, 0.55)
S.line([(0, 0, 0), (0, PI2, 0)], TEXT, 1.3, "5 4", 0.6)          # chord = segment of the y axis
S.arrow((0, PI2, 0), (0, YMAX, 0), TEXT, 1.1, 7, None, 0.55)
S.label((XMAX, 0, 0), "x", -4, 13, TEXT, 11.5, "middle", False, True)
S.label((0, YMAX, 0), "y", 10, 4, TEXT, 11.5, "middle", False, True)
S.label((0, 0, ZMAX), "z", -10, -4, TEXT, 11.5, "middle", False, True)

# 3. ticks: no x tick at 1 — alpha(pi/2) = (1, 0, 0) sits there and is labelled itself;
#    no y ticks — every candidate label lands on beta (t = 3pi/4 sits at y ~ 3, beta crosses the
#    chord at y ~ 4, and runs 13 px under it from y ~ 6 on); the unit grid and the chord label
#    give the y scale instead
S.ticks("x", (2, 3, 4), offset=(-2, 14))
S.ticks("z", (-1, 1, 2), fmt_=lambda v: fmt(v).replace("-", MINUS_S))

# 4. the two curves (beta is nearer the viewer: drawn last)
S.curve(alpha, 0, PI, PRACTICE, 2.3, samples=400)
S.curve(beta, 0, PI, THEORY, 2.3, samples=400)

# 5. points: end points, and t = pi/4, pi/2, 3pi/4 on each curve
S.point((0, 0, 0), TEXT, 3.6)
S.point((0, PI2, 0), TEXT, 3.6)
for t in TS:
    S.point(alpha(t), TEXT, 2.7)
    S.point(beta(t), TEXT, 2.7)

# 6. labels
S.label((0, 0, 0), bold("0"), 3, 15, TEXT, 11.5, "middle")
S.label((0, PI2, 0), "(0, " + PI_S + sups("2") + ", 0)", 10, -11, TEXT, 10.5, "middle")
S.label((0, 6.6, 0), PI_S + sups("2") + " &#8776; 9,87", 0, -10, TEXT, 10.5, "middle")

S.label(alpha(2.55), ital("L") + "(" + ital("&#945;") + ") &#8776; 12,92", 0, 17, PRACTICE, 11.5, "middle")
S.label(beta(1.6), ital("L") + "(" + ital("&#946;") + ") &#8776; 14,46", 8, -8, THEORY, 11.5, "start")

S.label(alpha(TS[0]), PI_S + "/4", -7, -3, PRACTICE, 10, "end")
S.label(alpha(TS[1]), PI_S + "/2", -9, 3, PRACTICE, 10, "end")
S.label(alpha(TS[2]), "3" + PI_S + "/4", -4, 14, PRACTICE, 10, "end")
S.label(beta(TS[0]), PI_S + "/4", 8, 8, THEORY, 10, "start")
S.label(beta(TS[1]), PI_S + "/2", -6, -6, THEORY, 10, "end")
S.label(beta(TS[2]), "3" + PI_S + "/4", 6, -6, THEORY, 10, "start")

OUT["yay-iki-egri-parcasi"] = figure(
    582, 250, [P],
    "Orijinden (0, &#960;<sup>2</sup>, 0) &#8776; (0, 9,87, 0) noktasına giden iki eğri parçası: "
    "turuncu &#945;(<em>t</em>) = (sin <em>t</em>, &#8722;<em>t</em><sup>2</sup> cos <em>t</em>, sin 2<em>t</em>) "
    "ve mavi &#946;(<em>t</em>) = (<em>t</em><sup>2</sup> sin <em>t</em>, <em>t</em><sup>2</sup>, "
    "<em>t</em><sup>2</sup>(1 + cos <em>t</em>)), 0 &#8804; <em>t</em> &#8804; &#960;; noktalar "
    "<em>t</em> = &#960;/4, &#960;/2, 3&#960;/4 anlarını gösterir. Uç noktaları birleştiren kesikli gri "
    "doğru parçası <em>y</em> ekseni üzerindedir ve uzunluğu &#960;<sup>2</sup> &#8776; 9,87'dir; "
    "Simpson kuralıyla bulunan <em>L</em>(&#945;) &#8776; 12,92 ve <em>L</em>(&#946;) &#8776; 14,46 "
    "bundan büyüktür; &#945; parçası yaklaşık 1,5 birim daha kısadır. &#946; orijinde durur, sonra "
    "<em>z</em> yönünde yükselerek geniş bir kavis çizer; &#945; ise önce yükselip <em>t</em> = &#960;/2'de "
    "<em>x</em> ekseni üzerindeki (1, 0, 0) noktasından geçer, ardından <em>xy</em> düzleminin altına "
    "iner ve uç noktaya alttan yaklaşır.",
    css_class=WIDE,
    aria="Orijinden (0, pi^2, 0) noktasina giden iki egri parcasi: turuncu alpha(t) = (sin t, -t^2 cos t, "
         "sin 2t), uzunlugu yaklasik 12,92, ve mavi beta(t) = (t^2 sin t, t^2, t^2 (1 + cos t)), uzunlugu "
         "yaklasik 14,46; uc noktalar arasindaki kesikli gri dogru parcasi y ekseni uzerinde, uzunlugu "
         "pi^2 yaklasik 9,87; t = pi/4, pi/2, 3pi/4 noktalari isaretli",
)

# ============================================================ yay-koni-spirali-ayni-rota
# -*- coding: utf-8 -*-
# yay-koni-spirali-ayni-rota — one route on the cone, two clocks.
# Cone z^2 = x^2 + y^2, upper half up to z = 8, as a translucent grey grid. On it the orange spiral
# alpha(t) = (e^t cos t, e^t sin t, e^t), 0 <= t <= 2. Hollow orange rings: alpha at equal time
# steps t = 0, 0.5, 1, 1.5, 2 (the arcs between them grow: 1.12, 1.85, 3.05, 5.04). Filled blue
# squares: the unit-speed copy beta(s) = alpha(t(s)), t(s) = log(1 + s/sqrt 3), at equal path
# steps s = 0, 2, 4, 6, 8, 10 (every arc between squares has length 2). beta(0) = alpha(0) and
# beta(6) ~ alpha(1.5) (t(6) = 1.4961), so those two marks carry both symbols.
#
# Camera az = 43, el = 17 (from a scan): the spiral sweeps the polar angles 0..114.6 deg, the
# silhouette generators of the cone sit at az +- acos(tan el) = 43 +- 72 deg, so the whole route
# stays on the near face; lower azimuths spread the crowded start a little more but push the end
# of the route round the back of the cone.
import math

AZ, EL = 43.0, 17.0
PHI = math.radians(AZ)
SIL = math.acos(math.tan(math.radians(EL)))         # half-angle of the near face (radians)
ZTOP = 8.0
SQ3 = math.sqrt(3.0)
CAM = Camera(azimuth=AZ, elevation=EL, scale=1.0)


def alpha(t):
    e = math.exp(t)
    return (e * math.cos(t), e * math.sin(t), e)


def beta(s):
    w = 1.0 + s / SQ3
    th = math.log(w)
    return (w * math.cos(th), w * math.sin(th), w)


def cone(u, z):
    return (z * math.cos(u), z * math.sin(u), z)


def proj(P):
    X, Y, _ = CAM.project(P)
    return X, Y


T_MARKS = (0.0, 0.5, 1.0, 1.5, 2.0)
S_MARKS = (0.0, 2.0, 4.0, 6.0, 8.0, 10.0)
X_END, Y_END, Z_END = 7.0, 9.0, 10.8
NEAR = (PHI - SIL, PHI + SIL)
FAR = (PHI + SIL, PHI + 2 * math.pi - SIL)

# --- panel from the projected bounding box ----------------------------------------------------
rim = [cone(2 * math.pi * k / 120, ZTOP) for k in range(121)]
bbox = [proj(P) for P in rim] + [proj((X_END, 0, 0)), proj((0, Y_END, 0)), proj((0, 0, Z_END))]
X0, X1 = min(b[0] for b in bbox), max(b[0] for b in bbox)
Y0, Y1 = min(b[1] for b in bbox), max(b[1] for b in bbox)
PAD_L, PAD_R, PAD_B, PAD_T = 0.5, 0.6, 0.7, 0.6
PW = 500
SP = space_panel(16, 16, PW, (X0 - PAD_L, X1 + PAD_R), (Y0 - PAD_B, Y1 + PAD_T))
S = Space(SP, CAM)


def ital(s):
    return '<tspan font-style="italic">' + s + "</tspan>"


def px(P):
    X, Y = S.pt(P)
    return SP.X(X), SP.Y(Y)


def txt_px(x, y, s, color=TEXT, size=11.0, anchor="start", italic=False, opacity=1.0, halo=True):
    """Text with a thin page-coloured halo so the cone's grid breaks behind it."""
    st = ' font-style="italic"' if italic else ""
    op = f' opacity="{opacity}"' if opacity < 1.0 else ""
    h = f' stroke="{BG}" stroke-width="3.4" stroke-linejoin="round" paint-order="stroke"' if halo else ""
    SP.add(f'<text x="{x:.1f}" y="{y:.1f}" fill="{color}" font-size="{size}" text-anchor="{anchor}"'
           f'{st}{op}{h}>{s}</text>')


def txt(P, s, dx, dy, color=TEXT, size=11.0, anchor="start", italic=False, opacity=1.0):
    x, y = px(P)
    txt_px(x + dx, y + dy, s, color, size, anchor, italic, opacity)


def ring_px(cx, cy, color, r, fill=BG):
    SP.add(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" stroke="{color}" stroke-width="1.9"/>')


def square_px(cx, cy, color, half):
    h = half + 1.5
    SP.add(f'<rect x="{cx - h:.1f}" y="{cy - h:.1f}" width="{2 * h:.1f}" height="{2 * h:.1f}" fill="{BG}"/>')
    SP.add(f'<rect x="{cx - half:.1f}" y="{cy - half:.1f}" width="{2 * half:.1f}" height="{2 * half:.1f}" '
           f'fill="{color}"/>')


RING_R, SQ_HALF = 5.2, 3.5

# --- the cone: far face first (fainter), then the axis inside it, then the near face -----------
S.surface(cone, FAR, (0.0, ZTOP), nu=18, nv=8, fill=TEXT, stroke=TEXT,
          opacity=(0.01, 0.04), stroke_width=0.55, stroke_opacity=0.16)
S.line([(0, 0, 0), (0, 0, ZTOP)], TEXT, 1.0, None, 0.45)
S.surface(cone, NEAR, (0.0, ZTOP), nu=12, nv=8, fill=TEXT, stroke=TEXT,
          opacity=(0.02, 0.075), stroke_width=0.6, stroke_opacity=0.32)
# outline: the two silhouette generators and the near half of the rim
for u in NEAR:
    S.line([(0, 0, 0), cone(u, ZTOP)], TEXT, 0.9, None, 0.45)
S.curve(lambda u: cone(u, ZTOP), NEAR[0], NEAR[1], TEXT, 0.9, samples=90, opacity=0.45)

# --- axes: x toward the viewer, y to the right, z out of the top opening ---------------------
S.arrow((0, 0, 0), (X_END, 0, 0), TEXT, 1.1, 7, None, 0.55)
S.arrow((0, 0, 0), (0, Y_END, 0), TEXT, 1.1, 7, None, 0.55)
S.arrow((0, 0, ZTOP), (0, 0, Z_END), TEXT, 1.1, 7, None, 0.55)
txt((X_END, 0, 0), "x", -4, 13, TEXT, 11.5, "middle", italic=True)
txt((0, Y_END, 0), "y", 10, 4, TEXT, 11.5, "middle", italic=True)
txt((0, 0, Z_END), "z", -10, -3, TEXT, 11.5, "middle", italic=True)
S.ticks("x", (2, 4, 6), offset=(-10, 0))
S.ticks("y", (2, 4, 6, 8), offset=(0, 13))
# no tick at z = 2: the route's start (t = 0.5 and t = 1) passes right beside the axis there
for v in (4, 6, 8):
    S.line([(-0.06, 0, v), (0.06, 0, v)], TEXT, 1.0, None, 0.7)
    txt((0, 0, v), str(v), -8, 4, TEXT, 10, "end", opacity=0.85)

# --- the route --------------------------------------------------------------------------------
S.curve(alpha, 0.0, 2.0, PRACTICE, 2.3, samples=400)

# --- marks: squares (beta, equal path steps) under the rings (alpha, equal time steps) ---------
for s in S_MARKS:
    square_px(*px(beta(s)), THEORY, SQ_HALF)
for t in T_MARKS:
    shared = t in (0.0, 1.5)          # beta(0) = alpha(0), beta(6) ~ alpha(1.5)
    ring_px(*px(alpha(t)), PRACTICE, RING_R, fill="none" if shared else BG)

# --- labels: t on the upper-left side of the route, s on the lower-right side -----------------
# The z axis runs through the crowded start (beta(2) sits on it, alpha(1) 20 px to its right), so
# the shared start point gets one two-coloured label on the left and "t = 1" goes above its ring,
# entirely to the right of the axis.
t_, s_ = ital("t"), ital("s")


def colored(s, color):
    return f'<tspan fill="{color}">{s}</tspan>'


txt(alpha(0.0), colored(t_ + " = 0", PRACTICE) + ", " + colored(s_ + " = 0", THEORY), -9, 5, TEXT, 11, "end")
txt(alpha(0.5), t_ + " = 0,5", -9, -4, PRACTICE, 11, "end")
txt(alpha(1.0), t_ + " = 1", -4, -11, PRACTICE, 11, "middle")
txt(alpha(1.5), t_ + " = 1,5", -9, 2, PRACTICE, 11, "end")
txt(alpha(2.0), t_ + " = 2", -9, 0, PRACTICE, 11, "end")

txt(beta(2.0), s_ + " = 2", 9, 9, THEORY, 11, "start")
txt(beta(4.0), s_ + " = 4", 9, 8, THEORY, 11, "start")
txt(beta(6.0), s_ + " = 6", 9, 8, THEORY, 11, "start")
txt(beta(8.0), s_ + " = 8", 9, 8, THEORY, 11, "start")
txt(beta(10.0), s_ + " = 10", 9, 8, THEORY, 11, "start")

# the curve's name on the upper-left side of its last stretch (the t labels' side, between
# t = 1,5 and t = 2); the cone's equation in the free top-left corner above the rim
txt(alpha(1.8), ital("&#945;"), -7, -6, PRACTICE, 12.5, "end")
txt_px(SP.X(X0 - PAD_L + 0.3), SP.Y(Y1 + PAD_T - 0.45),
       ital("z") + sups("2") + " = " + ital("x") + sups("2") + " + " + ital("y") + sups("2"),
       TEXT, 11, halo=False, opacity=0.85)

# --- legend in the empty wedge left of the cone, above the x axis ----------------------------
LX, LY = SP.X(X0 - PAD_L + 0.3), SP.Y(1.9)
ring_px(LX + 5, LY - 4, PRACTICE, RING_R, fill=BG)
txt_px(LX + 16, LY, ital("&#945;") + ": eşit zaman adımları, &#916;" + t_ + " = 0,5", TEXT, 11, halo=False)
square_px(LX + 5, LY + 15, THEORY, SQ_HALF)
txt_px(LX + 16, LY + 19, ital("&#946;") + ": eşit yol adımları, &#916;" + s_ + " = 2", TEXT, 11, halo=False)

# --- the two parametrizations in the empty wedge right of the cone, above the y axis ----------
E_T = ital("e") + sups(ital("t"))
FX = SP.X(2.6)
txt_px(FX, SP.Y(1.2), ital("&#945;") + "(" + t_ + ") = (" + E_T + " cos " + t_ + ", " + E_T + " sin " + t_
       + ", " + E_T + "),  0 " + LEQ_S + " " + t_ + " " + LEQ_S + " 2", TEXT, 11, halo=False)
txt_px(FX, SP.Y(0.65), ital("&#946;") + "(" + s_ + ") = " + ital("&#945;") + "(log(1 + " + s_ + "/&#8730;3))",
       TEXT, 11, halo=False)

OUT["yay-koni-spirali-ayni-rota"] = figure(
    532, 440, [SP],
    "<em>z</em><sup>2</sup> = <em>x</em><sup>2</sup> + <em>y</em><sup>2</sup> konisinin üst yarısı (gri "
    "ızgara) ve üzerindeki <em>&#945;</em>(<em>t</em>) = (e<sup><em>t</em></sup> cos <em>t</em>, "
    "e<sup><em>t</em></sup> sin <em>t</em>, e<sup><em>t</em></sup>) spirali, 0 &#8804; <em>t</em> &#8804; 2 "
    "(turuncu). İçi boş turuncu daireler <em>&#945;</em>'nın eşit zaman adımlarındaki "
    "<em>t</em> = 0; 0,5; 1; 1,5; 2 noktalarıdır: aralarındaki yaylar 1,12; 1,85; 3,05; 5,04 diye uzar, "
    "çünkü sürat &#8730;3&#8201;e<sup><em>t</em></sup> gittikçe büyür. Dolu mavi kareler birim hızlı kopya "
    "<em>&#946;</em>'nın eşit yol adımlarındaki <em>s</em> = 0, 2, 4, 6, 8, 10 noktalarıdır; ardışık iki "
    "kare arasındaki yay uzunluğu hep 2'dir. İki eğri aynı rotayı dolaşır; farklı olan yalnızca saatleridir.",
    aria="Koni z^2 = x^2 + y^2 uzerinde alpha(t) = (e^t cos t, e^t sin t, e^t) spirali, t 0 ile 2 arasinda, "
         "turuncu; ici bos turuncu daireler t = 0; 0,5; 1; 1,5; 2 noktalari (1; 0; 1), (1,45; 0,79; 1,65), "
         "(1,47; 2,29; 2,72), (0,32; 4,47; 4,48), (-3,08; 6,72; 7,39) ve aralari giderek uzar; dolu mavi "
         "kareler birim hizli beta icin s = 0, 2, 4, 6, 8, 10 noktalari (1; 0; 1), (1,55; 1,50; 2,15), "
         "(1,21; 3,08; 3,31), (0,33; 4,45; 4,46), (-0,87; 5,55; 5,62), (-2,27; 6,38; 6,77); ardisik kareler "
         "arasi yay uzunlugu hep 2")

# ============================================================ yay-parabol-hiz-ivme
# -*- coding: utf-8 -*-
# yay-parabol-hiz-ivme: the parabola alpha(t) = (t, t^2, 0) drawn in the xy plane (y = x^2 on
# [-1.6, 1.6], grey) with velocity (blue) and acceleration (orange) at t = -1, 0, 1.
#   alpha(-1) = (-1, 1): alpha' = (1, -2), alpha'' = (0, 2)
#   alpha(0)  = (0, 0):  alpha' = (1, 0),  alpha'' = (0, 2)
#   alpha(1)  = (1, 1):  alpha' = (1, 2),  alpha'' = (0, 2)
# The two arrows at the origin lie on the coordinate axes (that is what the numbers say), so the
# axes carry tick numbers only; the unit grid supplies the tick marks. The acceleration arrow at
# the origin is boxed in by the y axis and the two other acceleration arrows, so its label is set
# on two rows inside the cup of the parabola.

XR, YR = (-2.65, 2.9), (-1.35, 3.45)
p = cplane(32, 22, 336, XR, YR)        # about 60 px per unit, equal scale


def ital(s):
    return f'<tspan font-style="italic">{s}</tspan>'


ALPHA = ital("&#945;")
DPRIME = "&#8243;"                     # double prime for the second derivative
A, O, B = (-1.0, 1.0), (0.0, 0.0), (1.0, 1.0)
VEL = {A: (1.0, -2.0), O: (1.0, 0.0), B: (1.0, 2.0)}
ACC = (0.0, 2.0)

# 1. unit grid (skipping the axes) and the axes through the origin
p.grid([x for x in range(-2, 4) if x], [y for y in range(-1, 4) if y])
p.origin_axes("x", "y")
for x in (-2, -1, 1, 2):
    p.label(x, 0, fmt(x).replace("-", MINUS_S), 0, 15, TEXT, 11, "middle")
for y in (1, 2, 3):
    p.label(0, y, fmt(y).replace("-", MINUS_S), -7, 4, TEXT, 11, "end")
p.label(0, -1, MINUS_S + "1", -11, 7, TEXT, 11, "end")   # clear of the arrowhead landing at (0, -1)

# 2. the parabola, grey
curve(p, lambda x: x * x, -1.6, 1.6, TEXT, 2.2, 240, None, 0.5)

# 3. acceleration arrows (orange, all (0, 2)), then velocity arrows (blue, tangent to the curve)
for q in (A, O, B):
    p.arrow(q, (q[0] + ACC[0], q[1] + ACC[1]), PRACTICE, 2.4, 9)
for q, v in VEL.items():
    p.arrow(q, (q[0] + v[0], q[1] + v[1]), THEORY, 2.4, 9)

# 4. the three points
for q in (A, O, B):
    dot(p, q, TEXT, 3.6)

# 5. labels — points in the text colour, velocity in blue, acceleration in orange
m = MINUS_S
# alpha(-1) sits below-left of its point (mirroring alpha(1) below-right): on the point's own
# height the y = 1 grid line would strike through the text
p.label(*A, ALPHA + f"({m}1) = ({m}1, 1)", -9, 16, TEXT, 11, "end")
p.label(*O, ALPHA + "(0) = (0, 0)", 7, 32, TEXT, 11, "start")
p.label(*B, ALPHA + "(1) = (1, 1)", 8, 16, TEXT, 11, "start")

p.label(-0.25, -0.5, ALPHA + PRIME + f"({m}1) = (1, {m}2)", -14, 4, THEORY, 11, "end")
p.label(1.0, 0.0, ALPHA + PRIME + "(0) = (1, 0)", 10, -8, THEORY, 11, "start")
p.label(1.5, 2.0, ALPHA + PRIME + "(1) = (1, 2)", 16, 4, THEORY, 11, "start")

p.label(-1.0, 3.0, ALPHA + DPRIME + f"({m}1) = (0, 2)", 0, -9, PRACTICE, 11, "middle")
p.label(0.0, 1.6, ALPHA + DPRIME + "(0) =", 8, 4, PRACTICE, 11, "start")
p.label(0.0, 1.3, "(0, 2)", 8, 4, PRACTICE, 11, "start")
p.label(1.0, 3.0, ALPHA + DPRIME + "(1) = (0, 2)", -28, -10, PRACTICE, 11, "start")

OUT["yay-parabol-hiz-ivme"] = figure(
    400, 340, [p],
    "<em>xy</em> düzleminde <em>y</em> = <em>x</em><sup>2</sup> parabolünü çizen "
    "&#945;(<em>t</em>) = (<em>t</em>, <em>t</em><sup>2</sup>, 0) eğrisinin <em>t</em> = &#8722;1, 0, 1 "
    "anlarındaki hız vektörleri (mavi) ve ivme vektörleri (turuncu). "
    "Hız okları eğriye teğettir ve vektör kısımları (1, &#8722;2), (1, 0), (1, 2) olarak noktadan "
    "noktaya değişir; ivme oklarının üçü de aynı (0, 2) vektör kısmını taşır, hep yukarı bakar ve "
    "hiçbir anda hıza paralel değildir. "
    "<em>t</em> = &#8722;1&#8217;de ivme hızla geniş açı yapar (nokta yavaşlar), <em>t</em> = 0&#8217;da "
    "ona diktir, <em>t</em> = 1&#8217;de dar açı yapar (nokta hızlanır).",
    aria="xy duzleminde y = x^2 parabolu (gri, x -1,6 ile 1,6 arasinda) ve alpha(-1) = (-1, 1), "
         "alpha(0) = (0, 0), alpha(1) = (1, 1) noktalari. Her noktadan mavi hiz oku, vektor kisimlari "
         "sirasiyla (1, -2), (1, 0), (1, 2), egriye teget; turuncu ivme oku ucunde de (0, 2), hep dusey. "
         "Eksenler ve birim izgara",
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
