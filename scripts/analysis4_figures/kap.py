# -*- coding: utf-8 -*-
"""
Figures of the chapter "Ters ve Kapalı Fonksiyon Teoremleri"
(dersler/analiz-4/ters-ve-kapali-fonksiyon-teoremleri.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box and never directly under a heading.
The figures are NOT produced at build time. Run

    python scripts/analysis4_figures/kap.py
    python scripts/center_figures.py "analysis4-kap-*.md"
    python scripts/check_figure_labels.py "scripts/_figures/analysis4-kap-*.md"

and paste the markup of scripts/_figures/analysis4-kap-<name>.md into the .qmd.
Captions are Turkish on purpose; aria labels are plain ASCII.

Conventions: a boundary that belongs to the set is solid, one that does not is
dashed (the rectangles R of the implicit function theorem are open); a point of
the set is filled, a point outside it is hollow. Every drawing that contains a
circle uses equal x and y scales.
"""
import html
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, dot, hollow, TEXT, THEORY, PRACTICE, BASE, BG, WIDE  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "analysis4-kap-"

MINUS, PI_S, PHI, DELTA, ETA = "&#8722;", "&#960;", "&#966;", "&#948;", "&#951;"


def save(name, markup):
    (OUT_DIR / f"{PREFIX}{name}.md").write_text(markup, encoding="utf-8", newline="\n")
    print(f"{PREFIX}{name}.md")


def it(s):
    """Italic run inside an SVG <text>."""
    return f'<tspan font-style="italic">{s}</tspan>'


def sub(s, size=8.5):
    """Subscript inside an SVG <text>."""
    return f'<tspan font-size="{size}" dy="3.5">{s}</tspan><tspan dy="-3.5">&#8203;</tspan>'


def sup(s, size=8.5):
    """Superscript inside an SVG <text>."""
    return f'<tspan font-size="{size}" dy="-5">{s}</tspan><tspan dy="5">&#8203;</tspan>'


def eq_plot(x0, y0, ppu, xr, yr):
    """Panel with the same number of pixels per unit on both axes."""
    return Plot(x0, y0, (xr[1] - xr[0]) * ppu, (yr[1] - yr[0]) * ppu, xr, yr)


def dec(v):
    """Decimal comma and a true minus sign: -0.5 -> '−0,5'."""
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return s.replace(".", ",").replace("-", MINUS)


def text_w(s, size):
    """Rough advance width of a label (0.56 em per visible character)."""
    plain = html.unescape(re.sub(r"<[^>]+>", "", s)).replace("​", "")
    return len(plain) * 0.56 * size


def plabel(p, x, y, s, dx=0, dy=0, color=TEXT, size=11.5, anchor="start", bold=False):
    """Label on a page-coloured plate, for text that has to sit on lines."""
    px, py = p.X(x) + dx, p.Y(y) + dy
    w = text_w(s, size)
    x0 = px - (w / 2 if anchor == "middle" else w if anchor == "end" else 0)
    p.add(f'<rect x="{x0 - 2.5:.1f}" y="{py - 0.8 * size - 1:.1f}" width="{w + 5:.1f}" '
          f'height="{size + 3:.1f}" rx="3" fill="{BG}" opacity="0.9"/>')
    p.label(x, y, s, dx, dy, color, size, anchor, bold)


def tick(p, x, y, horizontal, length=4.0, opacity=0.6):
    """Short tick mark (pixels) across a horizontal or vertical axis line."""
    X, Y = p.X(x), p.Y(y)
    if horizontal:
        p.add(f'<line x1="{X:.1f}" y1="{Y - length:.1f}" x2="{X:.1f}" y2="{Y + length:.1f}" '
              f'stroke="{TEXT}" stroke-width="1" opacity="{opacity}"/>')
    else:
        p.add(f'<line x1="{X - length:.1f}" y1="{Y:.1f}" x2="{X + length:.1f}" y2="{Y:.1f}" '
              f'stroke="{TEXT}" stroke-width="1" opacity="{opacity}"/>')


def clip_polyline(pts, xr, yr):
    """Cut a polyline to the rectangle xr x yr; returns the list of inside runs."""
    (x0, x1), (y0, y1) = xr, yr

    def inside(q):
        return x0 <= q[0] <= x1 and y0 <= q[1] <= y1

    def cut(a, b):
        """Liang-Barsky: the part of segment ab inside the box, or None."""
        t0, t1 = 0.0, 1.0
        dx, dy = b[0] - a[0], b[1] - a[1]
        for pk, qk in ((-dx, a[0] - x0), (dx, x1 - a[0]), (-dy, a[1] - y0), (dy, y1 - a[1])):
            if pk == 0:
                if qk < 0:
                    return None
                continue
            r = qk / pk
            if pk < 0:
                t0 = max(t0, r)
            else:
                t1 = min(t1, r)
            if t0 > t1:
                return None
        return ((a[0] + t0 * dx, a[1] + t0 * dy), (a[0] + t1 * dx, a[1] + t1 * dy))

    runs, cur = [], []
    for a, b in zip(pts, pts[1:]):
        seg = cut(a, b)
        if seg is None:
            if cur:
                runs.append(cur)
                cur = []
            continue
        if not cur:
            cur = [seg[0]]
        cur.append(seg[1])
        if not inside(b):
            runs.append(cur)
            cur = []
    if cur:
        runs.append(cur)
    return [r for r in runs if len(r) > 1]


def rect_pts(x0, x1, y0, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


# ============================================================
# ustel-sarma: F(x, y) = (e^x cos y, e^x sin y) wraps the plane around the origin
# ============================================================
XR, YR = (-1.5, 1.0), (-4.0, 8.0)
pa = Plot(64, 40, 150, 336, XR, YR)                   # no circles on the left: unequal scales are fine
PPU = 72
pb = eq_plot(pa.x0 + pa.w + 110, pa.y0 + (pa.h - 4 * PPU) / 2, PPU, (-2, 2), (-2, 2))
PI = math.pi
VERT = (-1.0, 0.0, 0.5)
HORZ = (-PI / 2, 0.0, PI / 2)

# left panel: the strip V0 = R x (-pi, pi), its dashed boundary lines, the grid lines
pa.polygon(rect_pts(XR[0], XR[1], -PI, PI), BASE, 0.16)
for yb in (-PI, PI):
    pa.line([(XR[0], yb), (XR[1], yb)], BASE, 1.6, "6 4")
pa.axes((-1, 0, 0.5), (-PI, -PI / 2, 0, PI / 2, PI, 2 * PI), it("x"), it("y"), dec,
        lambda v: {-PI: MINUS + PI_S, -PI / 2: MINUS + PI_S + "/2", 0: "0", PI / 2: PI_S + "/2",
                   PI: PI_S, 2 * PI: "2" + PI_S}[v])
for yh in HORZ:
    pa.line([(XR[0], yh), (XR[1], yh)], PRACTICE, 1.8)
for xv in VERT:
    pa.line([(xv, YR[0]), (xv, YR[1])], THEORY, 1.8)
A, B = (0.0, 0.0), (0.0, 2 * PI)
dot(pa, A, TEXT, 4.0)
dot(pa, B, TEXT, 4.0)
pa.label(0, 0, it("A"), -6, -7, TEXT, 13, "end", True)
pa.label(0, 2 * PI, it("B"), 7, -6, TEXT, 13, "start", True)
pa.label(0.75, 2.35, it("V") + sub("0"), 0, 4, BASE, 13.5, "middle", True)

# the arrow F between the panels
ymid = pb.y0 + pb.h / 2
xa0, xa1 = pa.x0 + pa.w + 28, pb.x0 - 14
pa.add(f'<line x1="{xa0:.1f}" y1="{ymid:.1f}" x2="{xa1 - 8:.1f}" y2="{ymid:.1f}" stroke="{TEXT}" '
       f'stroke-width="1.6" opacity="0.8"/>')
pa.add(f'<polygon points="{xa1:.1f},{ymid:.1f} {xa1 - 10:.1f},{ymid - 4.5:.1f} {xa1 - 10:.1f},{ymid + 4.5:.1f}" '
       f'fill="{TEXT}" opacity="0.8"/>')
pa.text_px((xa0 + xa1) / 2, ymid - 9, it("F"), TEXT, 14, "middle", True)

# right panel: F(V0) is the plane without the closed half line u <= 0, v = 0
pb.polygon(rect_pts(-2, 2, -2, 2), BASE, 0.10)
pb.origin_axes(it("u"), it("v"), opacity=0.45)
for xv in VERT:
    pb.circle(0, 0, math.exp(xv), THEORY, 1.8)
for yh in HORZ:
    pb.line([(0, 0), (2 * math.cos(yh), 2 * math.sin(yh))], PRACTICE, 1.8)
pb.line([(-2, 0), (0, 0)], BASE, 2.0, "6 4")
hollow(pb, (0, 0), TEXT, 3.8)
dot(pb, (1, 0), TEXT, 4.0)
plabel(pb, 1, 0, it("F") + "(" + it("A") + ") = " + it("F") + "(" + it("B") + ")", 6, -9, TEXT, 12)
for xv, s in ((-1.0, it("e") + sup(MINUS + "1")), (0.0, "1"), (0.5, it("e") + sup("0,5"))):
    r = math.exp(xv)
    a = math.radians(135)
    pb.label(r * math.cos(a), r * math.sin(a), s, -4, -5, THEORY, 11.5, "end")
pb.label(-2, 2, it("F") + "(" + it("V") + sub("0") + ")", 6, 16, BASE, 13, "start", True)
save("ustel-sarma", figure(
    int(pb.x0 + pb.w + 30), int(pa.y0 + pa.h + 40), [pa, pb],
    "<em>F</em>(<em>x</em>, <em>y</em>) = (<em>e<sup>x</sup></em> cos <em>y</em>, <em>e<sup>x</sup></em> sin <em>y</em>) "
    "dönüşümü. Soldaki <em>x</em> = &#8722;1; 0; 0,5 düşey doğruları sağda merkezi orijin olan ve yarıçapı "
    "<em>e</em><sup>&#8722;1</sup> &#8776; 0,37; 1; <em>e</em><sup>0,5</sup> &#8776; 1,65 olan çemberlere, "
    "<em>y</em> = &#8722;<em>&#960;</em>/2; 0; <em>&#960;</em>/2 yatay doğruları orijinden çıkan ışınlara gider. "
    "&#8722;<em>&#960;</em> &lt; <em>y</em> &lt; <em>&#960;</em> şeridi <em>V</em><sub>0</sub>, orijin ve kesikli "
    "negatif <em>u</em> yarı ekseni dışındaki bütün düzlemi bir kez örter. "
    "<em>A</em> = (0, 0) ile <em>B</em> = (0, 2<em>&#960;</em>) aynı (1, 0) noktasına gider.",
    css_class=WIDE,
    aria="Left: the strip -pi less than y less than pi with three vertical and three horizontal lines and the "
         "points A = (0, 0) and B = (0, 2 pi). Right: their images, three circles about the origin and three "
         "rays, the negative u axis dashed and the origin hollow, and the common image point (1, 0)"))

# ============================================================
# kapali-ispat: every vertical of R meets the zero set exactly once
# ============================================================
DL, ET = 1.5, 1.0
XS = 0.9


def phi(x):
    return 0.4 * math.sin(1.2 * x) + 0.15 * x


p = eq_plot(80, 30, 115, (-1.95, 1.85), (-1.42, 1.3))
AXY, AXX = -1.25, -1.8                                  # the L-shaped axes sit outside R
# R: open rectangle, all four sides dashed; bottom side red (F < 0), top side blue (F > 0)
p.polygon(rect_pts(-DL, DL, -ET, ET), TEXT, 0.05)
for xs in (-DL, DL):
    p.line([(xs, -ET), (xs, ET)], TEXT, 1.2, "5 4", 0.7)
p.line([(-DL, -ET), (DL, -ET)], PRACTICE, 2.2, "7 4")
p.line([(-DL, ET), (DL, ET)], THEORY, 2.2, "7 4")
p.label(-0.75, -ET, it("F") + " &lt; 0", 0, -8, PRACTICE, 12.5, "middle", True)
p.label(-0.75, ET, it("F") + " &gt; 0", 0, 18, THEORY, 12.5, "middle", True)
p.label(-DL, ET, it("R"), 9, 19, TEXT, 14, "start", True)
# the axes with the symbolic ticks
p.arrow((AXX, AXY), (1.8, AXY), TEXT, 1.1, 7.0, None, 0.55)
p.arrow((AXX, AXY), (AXX, 1.25), TEXT, 1.1, 7.0, None, 0.55)
X0 = it("x") + sub("0")
Y0 = it("y") + sub("0")
for xv, s in ((-DL, X0 + " " + MINUS + " " + it(DELTA)), (0.0, X0), (XS, it("x")), (DL, X0 + " + " + it(DELTA))):
    tick(p, xv, AXY, True)
    p.label(xv, AXY, s, 0, 17, TEXT, 11.5, "middle")
for yv, s in ((-ET, Y0 + " " + MINUS + " " + it(ETA)), (0.0, Y0), (ET, Y0 + " + " + it(ETA))):
    tick(p, AXX, yv, False)
    p.label(AXX, yv, s, -7, 4, TEXT, 11.5, "end")
# the vertical through x: F increases from the red side to the blue side
p.line([(XS, -ET), (XS, ET)], TEXT, 1.1, "4 3", 0.75)
p.arrow((XS, -0.78), (XS, -0.3), TEXT, 1.6, 7.5, None, 0.9)
p.label(XS, -0.56, it("F") + " artar", 7, 4, TEXT, 11.5)
# the zero set y = phi(x) inside R
p.line([(-DL + 2 * DL * k / 240, phi(-DL + 2 * DL * k / 240)) for k in range(241)], BASE, 2.8)
dot(p, (0, 0), TEXT, 4.0)
p.label(0, 0, "(" + X0 + ", " + Y0 + ")", 6, 17, TEXT, 11.5)
dot(p, (XS, phi(XS)), BASE, 4.2)
p.label(XS, phi(XS), "(" + it("x") + ", " + it(PHI) + "(" + it("x") + "))", -8, -8, BASE, 12, "end")
p.label(-DL, phi(-DL), it("y") + " = " + it(PHI) + "(" + it("x") + ")", 8, 17, BASE, 12)
save("kapali-ispat", figure(
    int(p.x0 + p.w + 30), int(p.y0 + p.h + 20), [p],
    "<em>R</em> = (<em>x</em><sub>0</sub> &#8722; <em>&#948;</em>, <em>x</em><sub>0</sub> + <em>&#948;</em>) &#215; "
    "(<em>y</em><sub>0</sub> &#8722; <em>&#951;</em>, <em>y</em><sub>0</sub> + <em>&#951;</em>) dikdörtgeni. "
    "Alt kenarda <em>F</em> &lt; 0, üst kenarda <em>F</em> &gt; 0'dır ve her düşey kesitte <em>F</em>, <em>y</em>'ye "
    "göre kesin artandır. Bu yüzden her <em>x</em> için düşey doğru <em>F</em> = 0 kümesini tam bir kez, "
    "(<em>x</em>, <em>&#966;</em>(<em>x</em>)) noktasında keser.",
    aria="Open rectangle R around (x0, y0) with F negative on the bottom side and positive on the top side, "
         "the curve y = phi(x) crossing it from left to right, and a dashed vertical line at x with an upward "
         "arrow meeting the curve exactly once"))

# ============================================================
# cember: where the unit circle is a graph y = phi(x) and where it is not
# ============================================================
# The window around (1, 0) is only 0.4 wide, so it is repeated three times larger in an inset on the right.
p = eq_plot(40, 40, 120, (-1.5, 1.5), (-1.5, 1.5))
W2 = (0.8, 1.2, -0.35, 0.35)
ZPPU = 360
q = eq_plot(p.x0 + p.w + 62, p.Y(W2[3]) - (ZPPU - 120) * W2[3], ZPPU, W2[:2], W2[2:])
p.origin_axes(it("x"), it("y"), opacity=0.45)
for (x, y), dx, dy in (((-1, 0), -5, 15), ((0, 1), -5, -5), ((0, -1), -5, 15)):
    p.label(x, y, dec(x + y), dx, dy, TEXT, 11, "end")
p.circle(0, 0, 1, THEORY, 1.8)
# the good point (0.6, 0.8) and the window [0.35, 0.85] x [0.6, 1.0]
W1 = (0.35, 0.85, 0.6, 1.0)
p.polygon(rect_pts(*W1), BASE, 0.12)
p.line(rect_pts(*W1) + [(W1[0], W1[2])], BASE, 1.2, "5 3")
xa = W1[0]
xb = math.sqrt(1 - W1[2] ** 2)                          # 0.8: the arc leaves through the bottom side
p.line([(xa + (xb - xa) * k / 60, math.sqrt(1 - (xa + (xb - xa) * k / 60) ** 2)) for k in range(61)], BASE, 3.0)
p.line([(0.05, (5 - 3 * 0.05) / 4), (1.1, (5 - 3 * 1.1) / 4)], TEXT, 1.1, None, 0.75)
dot(p, (0.6, 0.8), TEXT, 4.0)
p.label(W1[1], 0.93, it("y") + " = " + it(PHI) + "(" + it("x") + ")", 6, 4, BASE, 12)
p.label(0.05, (5 - 3 * 0.05) / 4, "3" + it("x") + " + 4" + it("y") + " = 5", -5, 4, TEXT, 11.5, "end")
p.label(0.62, W1[2], "(0,6; 0,8)", 0, 15, TEXT, 11.5, "middle")
# the bad point (1, 0), the window [0.8, 1.2] x [-0.35, 0.35] and the vertical tangent x = 1
ya = W2[3]
ARC = [(math.sqrt(1 - (-ya + 2 * ya * k / 80) ** 2), -ya + 2 * ya * k / 80) for k in range(81)]
p.polygon(rect_pts(*W2), PRACTICE, 0.10)
p.line(rect_pts(*W2) + [(W2[0], W2[2])], PRACTICE, 1.2, "5 3")
p.line(ARC, PRACTICE, 3.0)
p.line([(1, -1.05), (1, 0.75)], TEXT, 1.1, "7 4", 0.7)
p.label(1, -1.05, it("x") + " = 1", 0, 15, TEXT, 11.5, "middle")
dot(p, (1, 0), TEXT, 3.6)
# zoom guides from the small window to the inset
for yc in (W2[2], W2[3]):
    p.add(f'<line x1="{p.X(W2[1]):.1f}" y1="{p.Y(yc):.1f}" x2="{q.X(W2[0]):.1f}" y2="{q.Y(yc):.1f}" '
          f'stroke="{PRACTICE}" stroke-width="0.9" stroke-dasharray="3 3" opacity="0.6"/>')
# the inset
XC = 0.95
YC = math.sqrt(1 - XC * XC)
q.polygon(rect_pts(*W2), PRACTICE, 0.10)
q.line(rect_pts(*W2) + [(W2[0], W2[2])], PRACTICE, 1.2, "5 3")
q.line([(W2[0], 0), (W2[1], 0)], TEXT, 1.0, None, 0.45)
q.line(ARC, PRACTICE, 3.0)
q.line([(1, W2[2]), (1, W2[3])], TEXT, 1.1, "7 4", 0.7)
q.line([(XC, W2[2]), (XC, W2[3])], TEXT, 1.3, "3 2", 0.9)
dot(q, (XC, YC), PRACTICE, 3.8)
dot(q, (XC, -YC), PRACTICE, 3.8)
dot(q, (1, 0), TEXT, 4.0)
q.label(1, 0, "(1, 0)", 7, -7, TEXT, 11.5)
q.label(XC, W2[3], it("x") + " = 0,95", 0, -7, TEXT, 11.5, "end")
q.label(1, W2[3], it("x") + " = 1", 0, -7, TEXT, 11.5, "start")
for xv in (0.8, 1.0, 1.2):
    q.label(xv, W2[2], dec(xv), 0, 15, TEXT, 11, "middle")
save("cember", figure(
    int(q.x0 + q.w + 40), int(p.y0 + p.h + 30), [p, q],
    "Birim çember. (0,6; 0,8) noktasının çevresindeki [0,35; 0,85] &#215; [0,6; 1] penceresinde çember tek bir "
    "<em>y</em> = <em>&#966;</em>(<em>x</em>) grafiğidir; teğeti 3<em>x</em> + 4<em>y</em> = 5 doğrusudur. "
    "(1, 0) noktasında teğet düşeydir (<em>x</em> = 1). Sağda üç kat büyütülen [0,8; 1,2] &#215; "
    "[&#8722;0,35; 0,35] penceresinde <em>x</em> = 0,95 doğrusu çemberi iki kez keser; 1'den büyük "
    "<em>x</em>'ler için ise kesişim yoktur.",
    css_class=WIDE,
    aria="Unit circle with a small window around (0.6, 0.8), where the arc is one graph y = phi(x) with tangent "
         "3x + 4y = 5, and a small window around (1, 0) with the vertical tangent x = 1, magnified on the right "
         "where the line x = 0.95 meets the circle twice"))

# ============================================================
# yaprak: the folium of Descartes x^3 + y^3 = 6xy
# ============================================================
# With t = y/x = tan(theta) the curve is x = 6 sin cos^2 / (cos^3 + sin^3), y = 6 sin^2 cos / (...),
# theta in (-pi/4, 3pi/4); theta = 0 and theta = pi/2 both give the origin.
LO, HI = -3.0, 4.5


def folium(th):
    c, s = math.cos(th), math.sin(th)
    d = c ** 3 + s ** 3
    return (6 * s * c * c / d, 6 * s * s * c / d)


p = eq_plot(40, 30, 60, (LO, HI), (LO, HI))
p.origin_axes(it("x"), it("y"), (2, 4), (2, 4), dec, dec, opacity=0.45)
p.line([(LO, -2 - LO), (-2 - LO, LO)], TEXT, 1.1, "6 4", 0.7)
p.label(-2.95, -0.62, it("x") + " + " + it("y") + " = " + MINUS + "2", 0, 0, TEXT, 11.5)
n = 4000
eps = 0.004
ths = [-PI / 4 + eps + (PI - 2 * eps) * k / n for k in range(n + 1)]
for run in clip_polyline([folium(t) for t in ths], (LO, HI), (LO, HI)):
    p.line(run, THEORY, 2.2)
# (3, 3) and its tangent x + y = 6
p.line([(2.2, 3.8), (3.8, 2.2)], PRACTICE, 1.4)
dot(p, (3, 3), PRACTICE, 4.0)
p.label(3, 3, "(3, 3)", 9, -7, PRACTICE, 11.5)
p.label(2.2, 3.8, it("x") + " + " + it("y") + " = 6", -4, -4, PRACTICE, 11.5, "end")
# the point with a vertical tangent
XV, YV = 2 ** (5 / 3), 2 ** (4 / 3)
p.line([(XV, YV - 0.65), (XV, YV + 0.4)], TEXT, 1.3, "4 3", 0.85)
dot(p, (XV, YV), TEXT, 4.0)
p.label(XV, YV, "(2" + sup("5/3") + ", 2" + sup("4/3") + ")", -9, 5, TEXT, 11.5, "end")
# the double point
dot(p, (0, 0), TEXT, 4.0)
p.label(0, 0, "kendini keser", -7, 16, TEXT, 11.5, "end")
save("yaprak", figure(
    int(p.x0 + p.w + 40), int(p.y0 + p.h + 30), [p],
    "Descartes yaprağı <em>x</em><sup>3</sup> + <em>y</em><sup>3</sup> = 6<em>xy</em> ve kesikli "
    "<em>x</em> + <em>y</em> = &#8722;2 asimptotu. (3, 3) noktasındaki teğet <em>x</em> + <em>y</em> = 6 doğrusudur; "
    "(2<sup>5/3</sup>, 2<sup>4/3</sup>) &#8776; (3,17; 2,52) noktasında teğet düşeydir. Eğri orijinden iki kez "
    "geçer ve orada kendini keser.",
    aria="Folium of Descartes x^3 + y^3 = 6xy with the dashed asymptote x + y = -2, the tangent x + y = 6 at "
         "(3, 3), a short vertical tangent at (2^(5/3), 2^(4/3)) and the self-intersection at the origin"))
