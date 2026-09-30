# -*- coding: utf-8 -*-
"""
Figures of the chapter "Açık ve Kapalı Kümeler"
(dersler/analiz-4/acik-ve-kapali-kumeler.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box and never directly under a heading.
The figures are NOT produced at build time. Run

    python scripts/analysis4_figures/ack.py
    python scripts/center_figures.py "analysis4-ack-*.md"
    python scripts/check_figure_labels.py "scripts/_figures/analysis4-ack-*.md"

and paste the markup of scripts/_figures/analysis4-ack-<name>.md into the .qmd.
The captions are Turkish on purpose; the aria labels are plain ASCII.

Conventions: a boundary that belongs to the set is solid, one that does not is
dashed; a point of the set is filled, a point outside it is hollow.
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, hollow, cross, disk_fill, TEXT, THEORY, PRACTICE  # noqa: E402
from svg_plot3 import Camera, Space, space_panel, vadd  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "analysis4-ack-"

MINUS, NORM, EPS = "&#8722;", "&#8214;", "&#949;"


def save(name, svg):
    (OUT_DIR / f"{PREFIX}{name}.md").write_text(svg, encoding="utf-8", newline="\n")
    print(f"{PREFIX}{name}.md")


def it(s):
    """Italic math letter inside an SVG <text>."""
    return f'<tspan font-style="italic">{s}</tspan>'


def subs(s, size=9):
    """Subscript inside an SVG <text>."""
    return f'<tspan font-size="{size}" dy="4">{s}</tspan><tspan dy="-4">&#8203;</tspan>'


def sups(s, size=9):
    """Superscript inside an SVG <text>."""
    return f'<tspan font-size="{size}" dy="-5">{s}</tspan><tspan dy="5">&#8203;</tspan>'


def equal_panel(x0, y0, ppu, xrange, yrange):
    """A panel with the same pixels per unit on both axes."""
    return Plot(x0, y0, ppu * (xrange[1] - xrange[0]), ppu * (yrange[1] - yrange[0]), xrange, yrange)


def arc_pts(cx, cy, r, a0, a1, n=96):
    return [(cx + r * math.cos(a0 + (a1 - a0) * k / n), cy + r * math.sin(a0 + (a1 - a0) * k / n))
            for k in range(n + 1)]


X0_S = it("x") + subs("0")

# ============================================================
# acik-yuvar: B(x, eps) with eps = r - |x - x0| stays inside B(x0, r)
# ============================================================
R = 2.0
XP = (1.1, 0.6)
DX = math.hypot(*XP)
E = R - DX                                   # 0.7473...
U = (XP[0] / DX, XP[1] / DX)
T = (R * U[0], R * U[1])                     # the point where the two spheres touch
p = equal_panel(20, 20, 72, (-2.5, 2.5), (-2.5, 2.5))
disk_fill(p, 0, 0, R, THEORY, 0.12)
disk_fill(p, XP[0], XP[1], E, PRACTICE, 0.2)
p.circle(0, 0, R, THEORY, 1.8, "6 4")
p.circle(XP[0], XP[1], E, PRACTICE, 1.6, "5 3")
RA = math.radians(250)
RE = (R * math.cos(RA), R * math.sin(RA))
p.line([(0, 0), RE], THEORY, 1.5)
p.line([(0, 0), XP], TEXT, 1.5)
p.line([XP, T], PRACTICE, 1.9)
p.points([(0, 0), XP], TEXT, 3.6)
hollow(p, T, PRACTICE, 3.2, 1.5)
p.label(0, 0, X0_S, -8, 4, TEXT, 12.5, "end")
p.label(XP[0], XP[1], it("x"), 5, 15, TEXT, 12.5)
p.label(0.33, -0.2, NORM + it("x") + " " + MINUS + " " + X0_S + NORM, 0, 0, TEXT, 12, "middle")
tm = (XP[0] + T[0]) / 2, (XP[1] + T[1]) / 2
p.label(tm[0], tm[1], it(EPS), -7, -7, PRACTICE, 13, "end")
p.label(RE[0] / 2, RE[1] / 2, it("r"), 8, 4, THEORY, 13)
p.label(-1.45, 1.5, it("B") + "(" + X0_S + ", " + it("r") + ")", 0, 0, THEORY, 12.5, "end")
p.label(XP[0], XP[1] - E, it("B") + "(" + it("x") + ", " + it(EPS) + ")", 0, 17, PRACTICE, 12.5, "middle")
save("acik-yuvar", figure(
    400, 400, [p],
    "<em>x</em><sub>0</sub> = (0, 0) merkezli, <em>r</em> = 2 yarıçaplı açık yuvar ve içindeki "
    "<em>x</em> = (1,1; 0,6) noktası. <em>&#949;</em> = <em>r</em> &#8722; &#8214;<em>x</em> &#8722; "
    "<em>x</em><sub>0</sub>&#8214; &#8776; 0,747 yarıçaplı <em>B</em>(<em>x</em>, <em>&#949;</em>) yuvarı "
    "büyük yuvara içten teğettir ve tamamen onun içinde kalır. Kesikli çemberler yuvarlara ait değildir.",
    aria="Open ball of radius 2 about the origin with a smaller open ball about x = (1.1, 0.6) "
         "whose radius is r minus the distance from x to the center, touching the big sphere from inside"))

# ============================================================
# silindir: the half cylinder x2^2 + x3^2 = 1, x1 > 0 contains no ball
# ============================================================
EP = 0.4                                     # the radius drawn for B(a, eps)
AZ, EL = -55.0, 22.0                         # x1 runs to the right along the page
A3 = (1.0, 0.0, 1.0)
P3 = (1.0, 0.0, 1.0 + EP / 2)
L1 = 3.0
pl = space_panel(20, 20, 470, (-1.05, 3.65), (-1.75, 1.75))
S = Space(pl, Camera(azimuth=AZ, elevation=EL, scale=1.0))
d = S.cam.d
PHI = math.atan2(d[2], d[1])                 # normal (0, cos u, sin u) faces the viewer for |u - PHI| < 90 deg
BACK = (PHI + math.pi / 2, PHI + 3 * math.pi / 2)
FRONT = (PHI - math.pi / 2, PHI + math.pi / 2)


def cyl(u, v):
    return (v, math.cos(u), math.sin(u))


def rim(x1):
    return lambda u: (x1, math.cos(u), math.sin(u))


def ball(C, r):
    def f(u, v):
        return (C[0] + r * math.cos(u) * math.cos(v), C[1] + r * math.sin(u) * math.cos(v),
                C[2] + r * math.sin(v))
    return f


O3 = (0.0, 0.0, 0.0)
# back half of the tube and the axis pieces inside it
S.surface(cyl, BACK, (0.0, L1), nu=14, nv=6, fill=THEORY, stroke=THEORY, opacity=(0.05, 0.12),
          stroke_width=0.5, stroke_opacity=0.25)
S.line([O3, (L1, 0.0, 0.0)], TEXT, 1.1, None, 0.5)
S.line([O3, (0.0, 1.0, 0.0)], TEXT, 1.1, None, 0.5)
S.line([O3, (0.0, 0.0, 1.0)], TEXT, 1.1, None, 0.5)
S.curve(rim(L1), BACK[0], BACK[1], THEORY, 1.1, 60, None, 0.55)
# front half of the tube
S.surface(cyl, FRONT, (0.0, L1), nu=14, nv=6, fill=THEORY, stroke=THEORY, opacity=(0.05, 0.14),
          stroke_width=0.5, stroke_opacity=0.3)
S.curve(rim(L1), FRONT[0], FRONT[1], THEORY, 1.3, 60, None, 0.8)
for u in FRONT:
    S.line([cyl(u, 0.0), cyl(u, L1)], THEORY, 1.3, None, 0.8)
# the end circle x1 = 0 is not part of S
S.curve(rim(0.0), 0.0, 2 * math.pi, THEORY, 1.6, 120, "5 4", 0.95)
# axes outside the tube; the x2 axis runs behind the ball, which is painted over it
X2MAX = 2.35
S.arrow((L1, 0.0, 0.0), (4.1, 0.0, 0.0), TEXT, 1.1, 7.0, None, 0.55)
S.arrow((0.0, 1.0, 0.0), (0.0, X2MAX, 0.0), TEXT, 1.1, 7.0, None, 0.55)
S.arrow((0.0, 0.0, 1.0), (0.0, 0.0, 1.65), TEXT, 1.1, 7.0, None, 0.55)
S.label((4.1, 0.0, 0.0), it("x") + subs("1"), 6, 14, TEXT, 12, "middle")
S.label((0.0, X2MAX, 0.0), it("x") + subs("2"), 9, 3, TEXT, 12, "start")
S.label((0.0, 0.0, 1.65), it("x") + subs("3"), -8, -3, TEXT, 12, "end")
# the ball B(a, eps)
S.surface(ball(A3, EP), (0.0, 2 * math.pi), (-math.pi / 2, math.pi / 2), nu=18, nv=9,
          fill=PRACTICE, stroke=PRACTICE, opacity=(0.08, 0.24), stroke_width=0.45, stroke_opacity=0.3)
# points and labels
S.point(A3, TEXT, 3.6)
S.hollow(P3, PRACTICE, 3.4, 1.6)
S.label(A3, it("a"), -8, 13, TEXT, 13, "end")
S.label(P3, it("p") + " = (1, 0, 1 + " + it(EPS) + "/2)", 30, -26, PRACTICE, 12)
S.label(vadd(A3, (0.0, 0.0, -EP)), it("B") + "(" + it("a") + ", " + it(EPS) + ")", 26, 14, PRACTICE, 12)
S.label((2.3, 0.0, -1.0), it("S"), 0, 22, THEORY, 13.5, "middle", True)
save("silindir", figure(
    520, 390, [pl],
    "<em>S</em> yarım silindirinin <em>x</em><sub>1</sub> &#8804; 3 kısmı; kesikli <em>x</em><sub>1</sub> = 0 "
    "çemberi <em>S</em>'ye ait değildir. <em>a</em> = (1, 0, 1) merkezli <em>B</em>(<em>a</em>, "
    "<em>&#949;</em>) yuvarı yüzeyden taşar: <em>p</em> = (1, 0, 1 + <em>&#949;</em>/2) yuvarın içindedir "
    "ama <em>S</em>'de değildir.",
    aria="Half cylinder along the x1 axis with the point a = (1, 0, 1) on it, a small ball about a "
         "and the point p above a that lies in the ball but not on the cylinder"))

# ============================================================
# serit: 0 < x <= 1 is not open at a = (1, 0)
# ============================================================
EP = 0.5
AS = (1.0, 0.0)
PS = (1.0 + EP / 2, 0.0)
YT, YB = 1.5, -1.5
p = equal_panel(20, 30, 110, (-0.8, 2.0), (YB, YT))
p.polygon([(0, YB), (1, YB), (1, YT), (0, YT)], THEORY, 0.15)
p.polygon(arc_pts(1.0, 0.0, EP, -math.pi / 2, math.pi / 2), PRACTICE, 0.25)
p.arrow((-0.8, 0), (2.0, 0), TEXT, 1.1, 7.0, None, 0.5)
p.label(2.0, 0, it("x"), -2, 16, TEXT, 12, "end")
p.line([(0, YB), (0, YT)], THEORY, 1.9, "6 4")
p.line([(1, YB), (1, YT)], THEORY, 2.3)
p.circle(AS[0], AS[1], EP, PRACTICE, 1.5, "5 3")
p.points([AS], TEXT, 3.8)
hollow(p, PS, PRACTICE, 3.6, 1.6)
p.label(0, YT, it("x") + " = 0", 0, -8, THEORY, 12, "middle")
p.label(1, YT, it("x") + " = 1", 0, -8, THEORY, 12, "middle")
p.label(AS[0], AS[1], it("a"), -7, 16, TEXT, 13, "end")
p.label(PS[0], PS[1], it("p"), 0, -9, PRACTICE, 13, "middle")
p.label(1.0 + EP * math.cos(0.8), EP * math.sin(0.8), it("B") + "(" + it("a") + ", " + it(EPS) + ")",
        5, -4, PRACTICE, 12.5)
p.label(0.5, 0.95, it("U"), 0, 0, THEORY, 14, "middle", True)
save("serit", figure(
    360, 400, [p],
    "<em>U</em> = {0 &lt; <em>x</em> &#8804; 1} şeridi: <em>x</em> = 0 doğrusu kümeye ait değil (kesikli), "
    "<em>x</em> = 1 doğrusu ait (düz). <em>a</em> = (1, 0) merkezli, <em>&#949;</em> = 0,5 yarıçaplı yuvarın "
    "sağ yarısı şeridin dışındadır; <em>p</em> = (1,25; 0) bu yarıdadır.",
    aria="Vertical strip 0 less than x at most 1 with the dashed line x = 0 and the solid line x = 1, "
         "a ball about a = (1, 0) whose right half leaves the strip, and the point p = (1.25, 0)"))

# ============================================================
# bolzano-weierstrass: halving the square I_1 = [-2, 2]^2 three times
# ============================================================
RR = 2.0
XS = (0.75, 0.75)
p = equal_panel(40, 20, 92, (-2.3, 2.3), (-2.3, 2.3))
p.axes((-RR, RR), (-RR, RR), it("x"), it("y"),
       lambda v: (MINUS + it("r")) if v < 0 else it("r"),
       lambda v: (MINUS + it("r")) if v < 0 else it("r"))


def square(x0, y0, s):
    return [(x0, y0), (x0 + s, y0), (x0 + s, y0 + s), (x0, y0 + s)]


# the chosen squares, each shaded a little more
p.polygon(square(0, 0, 2), THEORY, 0.12)
p.polygon(square(0, 0, 1), THEORY, 0.16)
p.polygon(square(0.5, 0.5, 0.5), THEORY, 0.22)
# halving lines (dashed), then the outlines of the chosen closed squares (solid)
for (a, b) in (((0, -2), (0, 2)), ((-2, 0), (2, 0)), ((1, 0), (1, 2)), ((0, 1), (2, 1)),
               ((0.5, 0), (0.5, 1)), ((0, 0.5), (1, 0.5))):
    p.line([a, b], TEXT, 1.0, "4 3", 0.55)
p.line(square(-2, -2, 4) + [(-2, -2)], TEXT, 1.6)
for x0, y0, s, w in ((0, 0, 2, 1.4), (0, 0, 1, 1.4), (0.5, 0.5, 0.5, 1.6)):
    p.line(square(x0, y0, s) + [(x0, y0)], THEORY, w)
# the set S: a few points everywhere, more and more of them in the chosen squares
spread = [(-1.5, 1.2), (-0.7, 1.55), (-1.2, 0.4), (-0.35, 0.8),
          (-1.6, -0.6), (-0.9, -1.3), (-0.4, -0.45), (-1.3, -1.7),
          (0.6, -1.5), (1.4, -0.8), (0.3, -0.7), (1.7, -1.6),
          (1.3, 1.4), (1.8, 1.15), (1.15, 1.8), (0.3, 1.6), (0.75, 1.3),
          (1.5, 0.35), (1.25, 0.8), (1.8, 0.6),
          (0.3, 0.35), (0.15, 0.7), (0.35, 0.88), (0.62, 0.25), (0.88, 0.38), (0.4, 0.15), (0.78, 0.12)]
angles = (20, 200, 50, 230, 75, 255, 35, 215, 60, 240, 10, 190, 45)
cluster = [(XS[0] + 0.21 * 0.8 ** k * math.cos(math.radians(t)),
            XS[1] + 0.21 * 0.8 ** k * math.sin(math.radians(t))) for k, t in enumerate(angles)]
p.points(spread + cluster, TEXT, 2.1)
cross(p, XS, PRACTICE, 4.5, 2.0)
p.label(-2, 2, it("I") + subs("1"), 6, 16, TEXT, 12.5)
p.label(2, 2, it("I") + subs("2"), -6, 16, THEORY, 12.5, "end")
p.label(0, 0, it("I") + subs("3"), 5, -5, THEORY, 12.5)
p.label(0.5, 1.0, it("I") + subs("4"), 3, 12, THEORY, 11.5)
p.label(XS[0], XS[1], it("x") + sups("*"), 7, 17, PRACTICE, 12.5)
save("bolzano-weierstrass", figure(
    500, 480, [p],
    "<em>I</em><sub>1</sub> = [&#8722;2, 2]<sup>2</sup> karesi (<em>r</em> = 2) dört eş kareye bölünür ve "
    "<em>S</em>'nin sonsuz çoklukta noktasını içeren parça <em>I</em><sub>2</sub> = [0, 2]<sup>2</sup> seçilir; "
    "aynı işlemle <em>I</em><sub>3</sub> = [0, 1]<sup>2</sup> ve <em>I</em><sub>4</sub> = [0,5; 1]<sup>2</sup> "
    "bulunur. Noktalar bütün <em>I<sub>m</sub></em>'lerde bulunan <em>x</em>* = (0,75; 0,75) çevresinde birikir.",
    aria="Square I1 = [-2, 2]^2 halved into four squares three times, the nested squares I2, I3, I4 shaded, "
         "points of S accumulating at x* = (0.75, 0.75)"))
