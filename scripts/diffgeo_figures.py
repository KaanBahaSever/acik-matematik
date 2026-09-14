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
