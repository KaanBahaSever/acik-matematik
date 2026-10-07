# -*- coding: utf-8 -*-
"""
Figures of the chapter "Dikdörtgen Bölgelerde İki Katlı İntegraller"
(dersler/integral-calculus/dikdortgen-bolgelerde-iki-katli-integraller.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box and never directly under a heading.
Concept figures stay visible: under a definition box, in the statement part of
a theorem or example, or in plain text. The figures are NOT produced at build
time. Run

    python scripts/calculus_figures/dkt.py
    python scripts/center_figures.py "calculus-dkt-*.md"
    python scripts/check_figure_labels.py "scripts/_figures/calculus-dkt-*.md"

and paste the markup of scripts/_figures/calculus-dkt-<name>.md into the .qmd.
Captions are Turkish on purpose; aria labels are plain ASCII.

All solids are drawn with translucent faces so that what lies behind them
stays readable; faces are painted back to front.
"""
import html
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, dot, TEXT, THEORY, PRACTICE, BASE, BG  # noqa: E402
from svg_plot3 import Camera, Space, vsub, vcross, vunit, vdot  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "calculus-dkt-"

MINUS = "&#8722;"
ZWSP = chr(0x200B)          # the zero-width space the sub/sup helpers leave behind


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


def fit_space(cam, pts, x0, y0, ppu, pad=0.12):
    """Equal-aspect panel just large enough for the projections of pts."""
    q = [cam.project(P)[:2] for P in pts]
    xr = (min(a for a, _ in q) - pad, max(a for a, _ in q) + pad)
    yr = (min(b for _, b in q) - pad, max(b for _, b in q) + pad)
    plot = eq_plot(x0, y0, ppu, xr, yr)
    return plot, Space(plot, cam)


def dec(v, digits=2):
    """Decimal comma: 0.5 -> '0,5'."""
    s = f"{v:.{digits}f}".rstrip("0").rstrip(".")
    return s.replace(".", ",").replace("-", MINUS)


def text_w(s, size):
    """Rough advance width of a label (0.43 em per visible character, tspans at their own size)."""
    def count(t):
        return len(html.unescape(re.sub(r"<[^>]+>", "", t)).replace(ZWSP, ""))
    width = 0.0
    for m in re.finditer(r'<tspan font-size="([\d.]+)"[^>]*>(.*?)</tspan>', s):
        width += count(m.group(2)) * 0.43 * float(m.group(1))
    rest = re.sub(r'<tspan font-size="[\d.]+"[^>]*>.*?</tspan>', "", s)
    return width + count(rest) * 0.43 * size


def plabel(p, x, y, s, dx=0, dy=0, color=TEXT, size=11.5, anchor="start", bold=False):
    """Label on a page-coloured plate, for text that must sit on a meshed surface."""
    px, py = p.X(x) + dx, p.Y(y) + dy
    w = text_w(s, size)
    x0 = px - (w / 2 if anchor == "middle" else w if anchor == "end" else 0)
    p.add(f'<rect x="{x0 - 2.5:.1f}" y="{py - 0.8 * size - 1:.1f}" width="{w + 5:.1f}" '
          f'height="{size + 3:.1f}" rx="3" fill="{BG}" opacity="0.85"/>')
    p.label(x, y, s, dx, dy, color, size, anchor, bold)


def splabel(S, P, s, dx=0, dy=0, color=TEXT, size=11.5, anchor="start", bold=False):
    """plabel() at a space point."""
    X, Y = S.pt(P)
    plabel(S.p, X, Y, s, dx, dy, color, size, anchor, bold)


def face(S, pts, fill, opacity, stroke=None, width=1.0, stroke_opacity=0.9, opaque=False):
    """One tinted planar face with its own outline; an opaque face hides what lies behind it."""
    if opaque:
        S.polygon(pts, BG, 1.0)
    S.polygon(pts, fill, opacity)
    if stroke:
        S.line(list(pts) + [pts[0]], stroke, width, None, stroke_opacity)


def column(S, x0, x1, y0, y1, h, fill=PRACTICE, op=(0.30, 0.20, 0.38), stroke=PRACTICE, width=1.1,
           opaque=False):
    """The three faces of the box [x0, x1] x [y0, y1] x [0, h] that the default
    camera (azimuth between 0 and 90 degrees) sees: front x = x1, right y = y1, top."""
    face(S, [(x1, y0, 0), (x1, y1, 0), (x1, y1, h), (x1, y0, h)], fill, op[0], stroke, width, opaque=opaque)
    face(S, [(x0, y1, 0), (x1, y1, 0), (x1, y1, h), (x0, y1, h)], fill, op[1], stroke, width, opaque=opaque)
    face(S, [(x0, y0, h), (x1, y0, h), (x1, y1, h), (x0, y1, h)], fill, op[2], stroke, width, opaque=opaque)


def mesh_faces(S, f, urange, vrange, nu, nv):
    """Quads of a parametric surface with depth, mean height and normal, unsorted."""
    u0, u1 = urange
    v0, v1 = vrange
    grid = [[f(u0 + (u1 - u0) * i / nu, v0 + (v1 - v0) * j / nv) for j in range(nv + 1)]
            for i in range(nu + 1)]
    out = []
    for i in range(nu):
        for j in range(nv):
            q = (grid[i][j], grid[i + 1][j], grid[i + 1][j + 1], grid[i][j + 1])
            n = vunit(vcross(vsub(q[2], q[0]), vsub(q[3], q[1])))
            dep = sum(S.depth(P) for P in q) / 4.0
            zm = sum(P[2] for P in q) / 4.0
            out.append((dep, zm, q, n))
    return out


def paint_faces(S, faces, fill, opacity=(0.06, 0.26), stroke_width=0.5, stroke_opacity=0.4,
                light=(-0.35, -0.55, 0.76)):
    """Paint mesh quads back to front with the same soft shading as Space.surface."""
    L = vunit(light)
    lo, hi = opacity
    for dep, _, q, n in sorted(faces, key=lambda t: t[0]):
        shade = 0.5 * (1.0 + abs(vdot(n, L)))
        op = lo + (hi - lo) * shade
        pts = " ".join(S.p.P(*S.pt(P)) for P in q)
        S.p.add(f'<polygon points="{pts}" fill="{fill}" fill-opacity="{op:.3f}" stroke="{fill}" '
                f'stroke-width="{stroke_width}" stroke-opacity="{stroke_opacity}" stroke-linejoin="round"/>')


def tick3(S, P, s, direction, dx, dy, size=11.5, color=TEXT, anchor="middle"):
    """Short tick at the space point P across `direction`, with a label."""
    a = tuple(P[k] - 0.06 * direction[k] for k in range(3))
    b = tuple(P[k] + 0.06 * direction[k] for k in range(3))
    S.line([a, b], color, 1.1, None, 0.7)
    S.label(P, s, dx, dy, color, size, anchor)


cam = Camera(azimuth=35.0, elevation=22.0)

# star-and-index labels
IJ = it("ij")
XS = it("x") + sup("*") + sub(IJ)
YS = it("y") + sup("*") + sub(IJ)


# ============================================================
# bolunus: the rectangle R divided into m x n subrectangles
# ============================================================
A_, B_, C_, D_ = 2.0, 9.2, 1.4, 5.4
M_, N_ = 6, 4
DX, DY = (B_ - A_) / M_, (D_ - C_) / N_
IH, JH = 4, 3                                     # the highlighted R_ij
p = eq_plot(60, 30, 52, (-0.4, 10.6), (-0.6, 6.6))
# R and its subrectangles
p.polygon([(A_, C_), (B_, C_), (B_, D_), (A_, D_)], THEORY, 0.07)
xi0, xi1 = A_ + (IH - 1) * DX, A_ + IH * DX
yj0, yj1 = C_ + (JH - 1) * DY, C_ + JH * DY
p.polygon([(xi0, yj0), (xi1, yj0), (xi1, yj1), (xi0, yj1)], PRACTICE, 0.22)
for i in range(M_ + 1):
    x = A_ + i * DX
    p.line([(x, C_), (x, D_)], THEORY, 1.6 if i in (0, M_) else 1.0, None, 0.9)
for j in range(N_ + 1):
    y = C_ + j * DY
    p.line([(A_, y), (B_, y)], THEORY, 1.6 if j in (0, N_) else 1.0, None, 0.9)
# sample points: a fixed scatter inside every cell
FRAC = [(0.30, 0.62), (0.72, 0.35), (0.48, 0.78), (0.22, 0.28), (0.66, 0.70), (0.40, 0.45),
        (0.78, 0.58), (0.55, 0.22), (0.28, 0.50), (0.60, 0.40), (0.36, 0.70), (0.70, 0.25)]
k = 0
for i in range(1, M_ + 1):
    for j in range(1, N_ + 1):
        fx, fy = FRAC[k % len(FRAC)]
        k += 1
        px, py = A_ + (i - 1 + fx) * DX, C_ + (j - 1 + fy) * DY
        if (i, j) == (IH, JH):
            px, py = xi0 + 0.62 * DX, yj0 + 0.55 * DY
            SP = (px, py)
            continue
        p.points([(px, py)], TEXT, 2.4)
dot(p, SP, PRACTICE, 3.8)
# axes
p.arrow((-0.3, 0), (10.5, 0), TEXT, 1.1, 8.0, None, 0.6)
p.arrow((0, -0.3), (0, 6.5), TEXT, 1.1, 8.0, None, 0.6)
p.label(10.5, 0, it("x"), 0, 17, TEXT, 12.5, "middle")
p.label(0, 6.5, it("y"), -10, 6, TEXT, 12.5, "middle")
p.label(0, 0, "0", -8, 14, TEXT, 11, "middle")
# guides to the axes
for x in (A_, xi0, xi1, B_):
    p.line([(x, 0), (x, C_)], TEXT, 0.9, "3 3", 0.45)
for y in (C_, yj0, yj1, D_):
    p.line([(0, y), (A_, y)], TEXT, 0.9, "3 3", 0.45)
for x, s in ((A_, it("a")), (xi0, it("x") + sub(it("i") + MINUS + "1")), (xi1, it("x") + sub(it("i"))),
             (B_, it("b"))):
    p.line([(x, -0.08), (x, 0.08)], TEXT, 1.0, None, 0.7)
    p.label(x, 0, s, 0, 17, TEXT, 12, "middle")
for y, s in ((C_, it("c")), (yj0, it("y") + sub(it("j") + MINUS + "1")), (yj1, it("y") + sub(it("j"))),
             (D_, it("d"))):
    p.line([(-0.08, y), (0.08, y)], TEXT, 1.0, None, 0.7)
    p.label(0, y, s, -8, 4, TEXT, 12, "end")
# dimension marks above and to the right of the highlighted cell
YT = D_ + 0.42
p.line([(xi0, yj1), (xi0, YT + 0.12)], PRACTICE, 0.9, "2 3", 0.7)
p.line([(xi1, yj1), (xi1, YT + 0.12)], PRACTICE, 0.9, "2 3", 0.7)
p.arrow((xi0 + DX / 2, YT), (xi0, YT), PRACTICE, 1.2, 6.0)
p.arrow((xi0 + DX / 2, YT), (xi1, YT), PRACTICE, 1.2, 6.0)
p.label(xi0 + DX / 2, YT, "&#916;" + it("x"), 0, -7, PRACTICE, 12, "middle")
XT = B_ + 0.42
p.line([(xi1, yj0), (XT + 0.12, yj0)], PRACTICE, 0.9, "2 3", 0.7)
p.line([(xi1, yj1), (XT + 0.12, yj1)], PRACTICE, 0.9, "2 3", 0.7)
p.arrow((XT, yj0 + DY / 2), (XT, yj0), PRACTICE, 1.2, 6.0)
p.arrow((XT, yj0 + DY / 2), (XT, yj1), PRACTICE, 1.2, 6.0)
p.label(XT, yj0 + DY / 2, "&#916;" + it("y"), 8, 4, PRACTICE, 12)
# names
p.label(xi0 + 0.1, yj0 + 0.12, it("R") + sub(IJ), 0, 0, PRACTICE, 12.5, "start", True)
p.line([SP, (B_ + 0.25, D_ - 0.15)], PRACTICE, 0.9, None, 0.8)
p.label(B_ + 0.25, D_ - 0.15, "(" + XS + ", " + YS + ")", 4, -2, PRACTICE, 12)
p.label(A_, D_, it("R"), -2, -9, THEORY, 14, "end", True)
save("bolunus", figure(
    680, 440, [p],
    "<em>R</em> = [<em>a</em>, <em>b</em>] &#215; [<em>c</em>, <em>d</em>] dikdörtgeni <em>m</em> = 6, "
    "<em>n</em> = 4 için 24 alt dikdörtgene bölünmüştür. Turuncu <em>R<sub>ij</sub></em> alt dikdörtgeninin "
    "kenarları &#916;<em>x</em> ve &#916;<em>y</em>, alanı &#916;<em>A</em> = &#916;<em>x</em>&#160;&#916;<em>y</em>'dir; "
    "her alt dikdörtgenden bir örnek noktası (nokta) seçilir.",
    aria="The rectangle R from a to b and from c to d divided into a 6 by 4 grid of subrectangles, a dot in "
         "every cell, one cell R_ij highlighted with its sides Delta x and Delta y and its sample point"))


# ============================================================
# shared surface for 'sutun' and 'kesit'
# ============================================================
RA, RB, RC, RD = 1.0, 4.0, 1.0, 4.6


def fs(x, y):
    return 2.0 + 0.09 * y * y + 0.12 * (x - 2.5) ** 2


def solid_frame(S, back=True):
    """Vertical corner edges of the solid over R and the boundary curves of its top."""
    corners = [(RA, RC), (RA, RD), (RB, RC), (RB, RD)]
    for (x, y) in corners:
        if back == ((x, y) in ((RA, RC), (RA, RD), (RB, RC))):
            S.line([(x, y, 0), (x, y, fs(x, y))], TEXT, 1.0, None, 0.55)


def floor_guides(S, a_off=(-6, 14)):
    S.guide([(RA, 0, 0), (RA, RC, 0)], TEXT, 0.45)
    S.guide([(RB, 0, 0), (RB, RC, 0)], TEXT, 0.45)
    S.guide([(0, RC, 0), (RA, RC, 0)], TEXT, 0.45)
    S.guide([(0, RD, 0), (RA, RD, 0)], TEXT, 0.45)
    tick3(S, (RA, 0, 0), it("a"), (0, 1, 0), *a_off)
    tick3(S, (RB, 0, 0), it("b"), (0, 1, 0), -6, 14)
    tick3(S, (0, RC, 0), it("c"), (1, 0, 0), 2, -8)
    tick3(S, (0, RD, 0), it("d"), (1, 0, 0), 2, -8)


# ============================================================
# sutun: one column of the Riemann sum under the surface
# ============================================================
MG, NG = 6, 7
XS9 = it("x") + sup("*", 9.5) + sub(IJ, 9.5)     # larger indices: this drawing is shown at about 0.9 scale
YS9 = it("y") + sup("*", 9.5) + sub(IJ, 9.5)
GX, GY = (RB - RA) / MG, (RD - RC) / NG
CI, CJ = 5, 3
cx0, cx1 = RA + (CI - 1) * GX, RA + CI * GX
cy0, cy1 = RC + (CJ - 1) * GY, RC + CJ * GY
SX, SY = cx0 + 0.6 * GX, cy0 + 0.45 * GY
HS = fs(SX, SY)
pts = [(0, 0, 0), (5.0, 0, 0), (0, 5.6, 0), (0, 0, 4.6), (RB, RD, 0), (RB, RC, 0), (RA, RD, fs(RA, RD)),
       (RB, RD, fs(RB, RD))]
pl, S = fit_space(cam, pts, 30, 20, 50, 0.3)
S.axes(5.0, 5.6, 4.6)
floor_guides(S)
# R with its grid
S.polygon([(RA, RC, 0), (RB, RC, 0), (RB, RD, 0), (RA, RD, 0)], BASE, 0.10)
for i in range(MG + 1):
    x = RA + i * GX
    S.line([(x, RC, 0), (x, RD, 0)], BASE, 1.3 if i in (0, MG) else 0.8, None, 0.8)
for j in range(NG + 1):
    y = RC + j * GY
    S.line([(RA, y, 0), (RB, y, 0)], BASE, 1.3 if j in (0, NG) else 0.8, None, 0.8)
S.polygon([(cx0, cy0, 0), (cx1, cy0, 0), (cx1, cy1, 0), (cx0, cy1, 0)], PRACTICE, 0.35)
solid_frame(S, back=True)
column(S, cx0, cx1, cy0, cy1, HS)
S.line([(SX, SY, 0), (SX, SY, HS)], PRACTICE, 1.0, "3 3", 0.9)
S.point((SX, SY, 0), PRACTICE, 2.8)
# the surface over R
S.surface(lambda u, v: (u, v, fs(u, v)), (RA, RB), (RC, RD), nu=12, nv=14, fill=THEORY, stroke=THEORY,
          opacity=(0.05, 0.22), stroke_width=0.45, stroke_opacity=0.35)
for (x0_, y0_, x1_, y1_) in ((RA, RC, RB, RC), (RB, RC, RB, RD), (RA, RD, RB, RD), (RA, RC, RA, RD)):
    S.curve(lambda t, a=(x0_, y0_), b=(x1_, y1_): (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t,
                                                     fs(a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)),
            0, 1, THEORY, 1.4, 40, None, 0.9)
solid_frame(S, back=False)
S.point((SX, SY, HS), PRACTICE, 3.6)
# labels
splabel(S, (RA, RD, fs(RA, RD)), it("z") + " = " + it("f") + "(" + it("x") + ", " + it("y") + ")", 10, -8,
        THEORY, 12.5)
S.p.line([S.pt((cx1, cy0, HS * 0.6)), S.pt((cx1 + 0.8, cy0 - 0.6, HS * 0.6))], PRACTICE, 0.9, None, 0.8)
splabel(S, (cx1 + 0.8, cy0 - 0.6, HS * 0.6), it("f") + "(" + XS9 + ", " + YS9 + ")", -4, 4, PRACTICE, 12, "end")
S.p.line([S.pt((cx1, (cy0 + cy1) / 2, 0)), S.pt((cx1 + 0.9, (cy0 + cy1) / 2 + 0.2, 0))],
         PRACTICE, 0.9, None, 0.8)
splabel(S, (cx1 + 0.9, (cy0 + cy1) / 2 + 0.2, 0), it("R") + sub(IJ, 9.5), 0, 16, PRACTICE, 12.5, "middle",
        True)
save("sutun", figure(
    int(pl.x0 + pl.w + 40), int(pl.y0 + pl.h + 20), [pl],
    "Tabanı <em>R<sub>ij</sub></em>, yüksekliği <em>f</em>(<em>x</em><sub><em>ij</em></sub><sup>*</sup>, "
    "<em>y</em><sub><em>ij</em></sub><sup>*</sup>) olan kutu (turuncu), cismin <em>R<sub>ij</sub></em> üzerindeki "
    "ince parçasının yerini tutar; hacmi <em>f</em>(<em>x</em><sub><em>ij</em></sub><sup>*</sup>, "
    "<em>y</em><sub><em>ij</em></sub><sup>*</sup>)&#160;&#916;<em>A</em>'dır. Bütün alt dikdörtgenlerdeki "
    "kutuların hacimleri toplamı iki katlı Riemann toplamıdır.",
    aria="A surface z = f(x, y) over a rectangle R on the floor divided into a grid; over one subrectangle "
         "R_ij stands a column whose top touches the surface at the sample point"))


# ============================================================
# kutular: Example 1, four boxes under z = 16 - x^2 - 2y^2
# ============================================================
ZS = 0.18                                         # the z axis is drawn at a reduced scale


def fp(x, y):
    return 16 - x * x - 2 * y * y


def P3(x, y, z):
    return (x, y, z * ZS)


pts = [(0, 0, 0), (2.9, 0, 0), (0, 2.9, 0), (0, 0, 18.5 * ZS), (2, 2, 0)]
pl, S = fit_space(cam, pts, 30, 20, 92, 0.3)
S.axes(2.9, 2.9, 18.5 * ZS)
for v in (1, 2):
    tick3(S, (v, 0, 0), str(v), (0, 1, 0), -7, 14)
    tick3(S, (0, v, 0), str(v), (1, 0, 0), 3, 15)
tick3(S, P3(0, 0, 16), "16", (1, -1, 0), -13, 4, anchor="end")
S.polygon([(0, 0, 0), (2, 0, 0), (2, 2, 0), (0, 2, 0)], BASE, 0.12)
S.line([(0, 0, 0), (2, 0, 0), (2, 2, 0), (0, 2, 0), (0, 0, 0)], BASE, 1.2, None, 0.8)
S.line([(1, 0, 0), (1, 2, 0)], BASE, 1.0, None, 0.8)
S.line([(0, 1, 0), (2, 1, 0)], BASE, 1.0, None, 0.8)
# back edges of the solid
S.line([P3(0, 0, 0), P3(0, 0, 16)], THEORY, 1.0, "4 3", 0.6)
S.curve(lambda t: P3(0, t, fp(0, t)), 0, 2, THEORY, 1.2, 40, "4 3", 0.7)
S.curve(lambda t: P3(t, 0, fp(t, 0)), 0, 2, THEORY, 1.2, 40, "4 3", 0.7)
# boxes, far to near; heights at the upper right corners
BOXES = [(0, 0), (0, 1), (1, 0), (1, 1)]
for (i, j) in sorted(BOXES, key=lambda b: S.depth((b[0] + 0.5, b[1] + 0.5, 0))):
    h = fp(i + 1, j + 1)
    column(S, i, i + 1, j, j + 1, h * ZS, PRACTICE, (0.30, 0.16, 0.42), PRACTICE, 1.2, opaque=True)
    S.point(P3(i + 1, j + 1, h), PRACTICE, 3.2)
# the paraboloid patch on top, translucent
S.surface(lambda u, v: P3(u, v, fp(u, v)), (0, 2), (0, 2), nu=8, nv=8, fill=THEORY, stroke=THEORY,
          opacity=(0.03, 0.13), stroke_width=0.4, stroke_opacity=0.25)
S.curve(lambda t: P3(2, t, fp(2, t)), 0, 2, THEORY, 1.6, 40)
S.curve(lambda t: P3(t, 2, fp(t, 2)), 0, 2, THEORY, 1.6, 40)
S.line([P3(2, 0, 0), P3(2, 0, 12)], THEORY, 1.0, None, 0.6)
S.line([P3(0, 2, 0), P3(0, 2, 8)], THEORY, 1.0, None, 0.6)
S.line([P3(2, 2, 0), P3(2, 2, 4)], THEORY, 1.0, None, 0.6)
# heights on the tops of the boxes
for (i, j) in BOXES:
    h = fp(i + 1, j + 1)
    splabel(S, P3(i + 0.5, j + 0.5, h), str(int(h)), 0, 5, PRACTICE, 12, "middle", True)
splabel(S, P3(0, 0.15, 16), it("z") + " = 16 " + MINUS + " " + it("x") + "² " + MINUS + " 2" + it("y") + "²",
        14, -6, THEORY, 12)
save("kutular", figure(
    int(pl.x0 + pl.w + 40), int(pl.y0 + pl.h + 20), [pl],
    "<em>z</em> = 16 &#8722; <em>x</em>² &#8722; 2<em>y</em>² paraboloidinin altına dikilen dört kutu "
    "(düşey eksen küçültülmüş ölçekte). Yükseklikler karelerin sağ üst köşelerindeki değerlerdir: "
    "13, 7, 10 ve 4. Kutuların toplam hacmi 34'tür.",
    aria="The patch of the paraboloid z = 16 - x^2 - 2y^2 over the square [0, 2] x [0, 2] with four boxes "
         "under it of heights 13, 7, 10 and 4 standing on the four unit squares"))


# ============================================================
# yarim-silindir: Example 2, the half cylinder x^2 + z^2 = 1, z >= 0
# ============================================================
pts = [(0, 0, 0), (1.9, 0, 0), (0, 2.9, 0), (0, -2.6, 0), (0, 0, 1.8), (1, 2, 0), (-1, -2, 0),
       (-1, 2, 0), (0, 2, 1), (0, -2, 1)]
pl, S = fit_space(cam, pts, 30, 20, 95, 0.3)
# the hidden halves of the axes first
S.line([(0, -2.6, 0), (0, 0, 0)], TEXT, 1.0, None, 0.4)
S.line([(-1.4, 0, 0), (0, 0, 0)], TEXT, 1.0, None, 0.4)
S.polygon([(-1, -2, 0), (1, -2, 0), (1, 2, 0), (-1, 2, 0)], BASE, 0.14)
S.line([(-1, -2, 0), (1, -2, 0), (1, 2, 0), (-1, 2, 0), (-1, -2, 0)], BASE, 1.2, None, 0.8)
# far end cap (y = -2)
cap = [(math.cos(t), -2, math.sin(t)) for t in [k * math.pi / 40 for k in range(41)]]
S.polygon(cap, THEORY, 0.10)
S.line(cap, THEORY, 1.0, "4 3", 0.6)
S.line([(0, 0, 0), (0, 0, 1)], TEXT, 1.0, "3 3", 0.5)
S.surface(lambda t, y: (math.cos(t), y, math.sin(t)), (0, math.pi), (-2, 2), nu=16, nv=8, fill=THEORY,
          stroke=THEORY, opacity=(0.05, 0.24), stroke_width=0.45, stroke_opacity=0.35)
cap = [(math.cos(t), 2, math.sin(t)) for t in [k * math.pi / 40 for k in range(41)]]
S.polygon(cap, THEORY, 0.16)
S.line(cap + [cap[0]], THEORY, 1.6)
S.line([(-1, -2, 0), (-1, 2, 0)], THEORY, 1.4)
S.line([(1, -2, 0), (1, 2, 0)], THEORY, 1.4)
S.curve(lambda t: (math.cos(t), -2, math.sin(t)), 0, math.pi, THEORY, 1.2, 40)
# the visible halves of the axes
S.arrow((1, 0, 0), (1.9, 0, 0), TEXT, 1.1, 7.0, None, 0.6)
S.arrow((0, 2, 0), (0, 2.9, 0), TEXT, 1.1, 7.0, None, 0.6)
S.arrow((0, 0, 1), (0, 0, 1.8), TEXT, 1.1, 7.0, None, 0.6)
S.label((1.9, 0, 0), "x", -4, 13, TEXT, 11.5, "middle", False, True)
S.label((0, 2.9, 0), "y", 10, 4, TEXT, 11.5, "middle", False, True)
S.label((0, 0, 1.8), "z", -10, -2, TEXT, 11.5, "middle", False, True)
S.point((1, 0, 0), TEXT, 3.0)
S.point((0, 2, 0), TEXT, 3.0)
S.point((0, 0, 1), TEXT, 3.0)
splabel(S, (1, 0, 0), "(1, 0, 0)", -6, 16, TEXT, 11.5, "end")
splabel(S, (0, 2, 0), "(0, 2, 0)", 8, 15, TEXT, 11.5)
splabel(S, (0, 0, 1), "(0, 0, 1)", -8, -8, TEXT, 11.5, "end")
splabel(S, (0.0, 2.0, 1.0), it("x") + "² + " + it("z") + "² = 1", 14, -8, THEORY, 12)
splabel(S, (0.4, 1.3, 0), it("R"), 0, 0, BASE, 13, "middle", True)
save("yarim-silindir", figure(
    int(pl.x0 + pl.w + 40), int(pl.y0 + pl.h + 20), [pl],
    "<em>z</em> = &#8730;(1 &#8722; <em>x</em>²) yüzeyi, ekseni <em>y</em> ekseni ve yarıçapı 1 olan "
    "silindirin üst yarısıdır. <em>R</em> = [&#8722;1, 1] &#215; [&#8722;2, 2] üzerindeki cismin her kesiti "
    "alanı <em>&#960;</em>/2 olan bir yarım dairedir ve cismin uzunluğu 4'tür.",
    aria="Upper half of the circular cylinder x^2 + z^2 = 1 lying along the y axis from y = -2 to y = 2 over "
         "the rectangle R, with the points (1, 0, 0), (0, 2, 0) and (0, 0, 1) marked"))


# ============================================================
# kesit: the cross-section A(x) behind Fubini's theorem
# ============================================================
X0S = 2.55
pts = [(0, 0, 0), (5.0, 0, 0), (0, 5.6, 0), (0, 0, 4.6), (RB, RD, 0), (RB, RC, 0), (RA, RD, fs(RA, RD)),
       (RB, RD, fs(RB, RD))]
pl, S = fit_space(cam, pts, 30, 20, 50, 0.3)
S.axes(5.0, 5.6, 4.6)
floor_guides(S, a_off=(-13, 12))
S.polygon([(RA, RC, 0), (RB, RC, 0), (RB, RD, 0), (RA, RD, 0)], BASE, 0.10)
S.line([(RA, RC, 0), (RB, RC, 0), (RB, RD, 0), (RA, RD, 0), (RA, RC, 0)], BASE, 1.2, None, 0.8)
solid_frame(S, back=True)
# the part of the surface behind the slice, then the slice, then the part in front
faces = mesh_faces(S, lambda u, v: (u, v, fs(u, v)), (RA, RB), (RC, RD), 12, 14)
behind = [fc for fc in faces if sum(P[0] for P in fc[2]) / 4 < X0S]
front = [fc for fc in faces if sum(P[0] for P in fc[2]) / 4 >= X0S]
paint_faces(S, behind, THEORY, (0.05, 0.22), 0.45, 0.35)
ys = [RC + (RD - RC) * k / 60 for k in range(61)]
slab = [(X0S, y, 0) for y in ys] + [(X0S, y, fs(X0S, y)) for y in reversed(ys)]
S.polygon(slab, PRACTICE, 0.30)
S.line([(X0S, RC, 0), (X0S, RD, 0)], PRACTICE, 1.4)
S.line([(X0S, RC, 0), (X0S, RC, fs(X0S, RC))], PRACTICE, 1.4)
S.line([(X0S, RD, 0), (X0S, RD, fs(X0S, RD))], PRACTICE, 1.4)
S.curve(lambda y: (X0S, y, fs(X0S, y)), RC, RD, PRACTICE, 2.6, 60)
paint_faces(S, front, THEORY, (0.04, 0.16), 0.45, 0.3)
for (x0_, y0_, x1_, y1_) in ((RA, RC, RB, RC), (RB, RC, RB, RD), (RA, RD, RB, RD), (RA, RC, RA, RD)):
    S.curve(lambda t, a=(x0_, y0_), b=(x1_, y1_): (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t,
                                                     fs(a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)),
            0, 1, THEORY, 1.4, 40, None, 0.9)
solid_frame(S, back=False)
S.guide([(X0S, 0, 0), (X0S, RC, 0)], PRACTICE, 0.7)
tick3(S, (X0S, 0, 0), it("x"), (0, 1, 0), -6, 14, color=PRACTICE)
splabel(S, (X0S, RC + 0.5 * (RD - RC), 0.7 * fs(X0S, RC + 0.5 * (RD - RC))), it("A") + "(" + it("x") + ")", 0, 5,
        PRACTICE, 13, "middle", True)
splabel(S, (X0S, RD, fs(X0S, RD)), it("C"), 8, 2, PRACTICE, 13, "start", True)
splabel(S, (RA, RD, fs(RA, RD)), it("z") + " = " + it("f") + "(" + it("x") + ", " + it("y") + ")", 10, -8,
        THEORY, 12.5)
save("kesit", figure(
    int(pl.x0 + pl.w + 40), int(pl.y0 + pl.h + 20), [pl],
    "Cismin <em>x</em> noktasından geçen ve <em>x</em> eksenine dik düzlemle kesiti (turuncu), "
    "<em>c</em> &#8804; <em>y</em> &#8804; <em>d</em> aralığında <em>C</em>: <em>z</em> = <em>f</em>(<em>x</em>, "
    "<em>y</em>) eğrisinin altında kalan bölgedir. Alanı <em>A</em>(<em>x</em>) = &#8747;<sub><em>c</em></sub>"
    "<sup><em>d</em></sup> <em>f</em>(<em>x</em>, <em>y</em>)&#160;<em>dy</em> olduğundan hacim "
    "&#8747;<sub><em>a</em></sub><sup><em>b</em></sup> <em>A</em>(<em>x</em>)&#160;<em>dx</em> ardışık "
    "integraline eşittir.",
    aria="The solid under a surface over a rectangle R, cut by the vertical plane through x perpendicular to "
         "the x axis; the cross-section under the curve C is shaded and labelled A(x)"))


# ============================================================
# negatif: Example 5, z = x - 3y^2 lies below R = [0, 2] x [1, 2]
# ============================================================
ZN = 0.15


def fn(x, y):
    return x - 3 * y * y


def N3(x, y, z):
    return (x, y, z * ZN)


camn = Camera(azimuth=35.0, elevation=18.0)
pts = [(0, 0, 0), (2.8, 0, 0), (0, 2.9, 0), (0, 0, 1.0), (0, 0, -13 * ZN), (2, 2, -12 * ZN), (2, 1, 0),
       (0, 2, -12 * ZN)]
pl, S = fit_space(camn, pts, 30, 20, 92, 0.3)
S.line([(0, 0, -13 * ZN), (0, 0, 0)], TEXT, 1.0, None, 0.5)
S.axes(2.8, 2.9, 1.0)
for v in (1, 2):
    tick3(S, (0, v, 0), str(v), (1, 0, 0), 2, -8)
tick3(S, (2, 0, 0), "2", (0, 1, 0), -7, 14)
tick3(S, N3(0, 0, -12), MINUS + "12", (1, -1, 0), -12, 4, anchor="end")
S.guide([(2, 0, 0), (2, 1, 0)], TEXT, 0.45)
S.guide([(0, 1, 0), (2, 1, 0)], TEXT, 0.35)
S.guide([N3(0, 0, -12), N3(0, 2, -12)], TEXT, 0.4)
# back vertical edges
S.line([N3(0, 1, 0), N3(0, 1, fn(0, 1))], TEXT, 1.0, "4 3", 0.55)
S.line([N3(0, 2, 0), N3(0, 2, fn(0, 2))], TEXT, 1.0, None, 0.55)
S.surface(lambda u, v: N3(u, v, fn(u, v)), (0, 2), (1, 2), nu=10, nv=8, fill=THEORY, stroke=THEORY,
          opacity=(0.08, 0.30), stroke_width=0.45, stroke_opacity=0.4)
for (x0_, y0_, x1_, y1_) in ((0, 1, 2, 1), (2, 1, 2, 2), (0, 2, 2, 2), (0, 1, 0, 2)):
    S.curve(lambda t, a=(x0_, y0_), b=(x1_, y1_): N3(a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t,
                                                     fn(a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)),
            0, 1, THEORY, 1.4, 40, None, 0.9)
S.line([N3(2, 1, 0), N3(2, 1, fn(2, 1))], TEXT, 1.0, None, 0.55)
S.line([N3(2, 2, 0), N3(2, 2, fn(2, 2))], TEXT, 1.0, None, 0.55)
# R on the xy-plane above the surface
S.polygon([(0, 1, 0), (2, 1, 0), (2, 2, 0), (0, 2, 0)], BASE, 0.22)
S.line([(0, 1, 0), (2, 1, 0), (2, 2, 0), (0, 2, 0), (0, 1, 0)], BASE, 1.5)
splabel(S, (1.0, 1.5, 0), it("R"), 0, 5, BASE, 13, "middle", True)
splabel(S, N3(2, 2, fn(2, 2)), it("z") + " = " + it("x") + " " + MINUS + " 3" + it("y") + "²", 10, 12, THEORY,
        12.5)
save("negatif", figure(
    int(pl.x0 + pl.w + 40), int(pl.y0 + pl.h + 20), [pl],
    "<em>R</em> = [0, 2] &#215; [1, 2] üzerinde <em>z</em> = <em>x</em> &#8722; 3<em>y</em>² yüzeyi "
    "<em>xy</em>-düzleminin tümüyle altındadır (düşey eksen küçültülmüş ölçekte). <em>R</em> ile yüzey "
    "arasındaki cismin hacmi 12'dir; integral bunun ters işaretlisi olan &#8722;12'dir.",
    aria="The rectangle R = [0, 2] x [1, 2] on the xy-plane and below it the surface z = x - 3y^2, joined "
         "by vertical edges; the solid between them lies under the plane"))


# ============================================================
# ortalama: a hilly surface cut by the plane z = f_avg
# ============================================================
FA = 1.5


def fo(x, y):
    return FA + 0.8 * math.sin(math.pi * x / 2) * math.sin(math.pi * y / 2)


pts = [(0, 0, 0), (5.0, 0, 0), (0, 5.2, 0), (0, 0, 3.0), (4, 4, 0), (4, 0, 0), (0, 4, 2.4), (4, 4, 2.4)]
pl, S = fit_space(cam, pts, 30, 20, 78, 0.3)
S.axes(5.0, 5.2, 3.0)
S.polygon([(0, 0, 0), (4, 0, 0), (4, 4, 0), (0, 4, 0)], BASE, 0.10)
S.line([(0, 0, 0), (4, 0, 0), (4, 4, 0), (0, 4, 0), (0, 0, 0)], BASE, 1.2, None, 0.8)
for (x, y) in ((0, 0), (0, 4), (4, 0)):
    S.line([(x, y, 0), (x, y, FA)], PRACTICE, 1.0, "4 3", 0.7)
faces = mesh_faces(S, lambda u, v: (u, v, fo(u, v)), (0, 4), (0, 4), 20, 20)
low = [fc for fc in faces if fc[1] < FA]
high = [fc for fc in faces if fc[1] >= FA]
paint_faces(S, low, THEORY, (0.06, 0.26), 0.4, 0.35)
S.polygon([(0, 0, FA), (4, 0, FA), (4, 4, FA), (0, 4, FA)], PRACTICE, 0.26)
S.line([(0, 0, FA), (4, 0, FA), (4, 4, FA), (0, 4, FA), (0, 0, FA)], PRACTICE, 1.5)
paint_faces(S, high, THEORY, (0.08, 0.32), 0.4, 0.4)
S.line([(4, 4, 0), (4, 4, FA)], PRACTICE, 1.0, "4 3", 0.7)
splabel(S, (4, 0, 0), it("R"), -4, 18, BASE, 13, "middle", True)
splabel(S, (3, 3, fo(3, 3)), "tepe", 0, -12, THEORY, 11.5, "middle")
splabel(S, (3, 1, fo(3, 1)), "vadi", 4, 16, THEORY, 11.5, "middle")
splabel(S, (4, 4, FA), it("z") + " = " + it("f") + sub("ort"), 10, 6, PRACTICE, 12.5)
save("ortalama", figure(
    int(pl.x0 + pl.w + 40), int(pl.y0 + pl.h + 20), [pl],
    "Engebeli bir <em>z</em> = <em>f</em>(<em>x</em>, <em>y</em>) yüzeyi ve <em>z</em> = <em>f</em><sub>ort</sub> "
    "düzlemi (turuncu). Düzlemin üstünde kalan tepeler kesilip altında kalan vadilere doldurulursa yüzey "
    "tümüyle düzleşir; tabanı <em>R</em>, yüksekliği <em>f</em><sub>ort</sub> olan kutunun hacmi yüzeyin "
    "altındaki hacme eşittir.",
    aria="A wavy surface with two hills and two valleys over a square R, cut by a horizontal plane at the "
         "height of the average value; the hills rise above the plane and the valleys dip below it"))


# ============================================================
# kar: Example 9, midpoint values of the snow depth on a 4 x 4 grid
# ============================================================
WX, WY = 388.0, 276.0
VALS = [[0, 15, 8, 7], [2, 25, 18.5, 11], [4.5, 28, 17, 13.5], [12, 15, 17.5, 13]]   # rows bottom to top
p = eq_plot(60, 30, 1.0, (-14, WX + 54), (-14, WY + 26))
for j in range(4):
    for i in range(4):
        v = VALS[j][i]
        x0_, y0_ = i * WX / 4, j * WY / 4
        p.polygon([(x0_, y0_), (x0_ + WX / 4, y0_), (x0_ + WX / 4, y0_ + WY / 4), (x0_, y0_ + WY / 4)],
                  THEORY, 0.03 + 0.30 * v / 28)
for i in range(5):
    p.line([(i * WX / 4, 0), (i * WX / 4, WY)], THEORY, 1.4 if i in (0, 4) else 0.9, None, 0.85)
for j in range(5):
    p.line([(0, j * WY / 4), (WX, j * WY / 4)], THEORY, 1.4 if j in (0, 4) else 0.9, None, 0.85)
for j in range(4):
    for i in range(4):
        cx, cy = (i + 0.5) * WX / 4, (j + 0.5) * WY / 4
        dot(p, (cx, cy), PRACTICE, 3.0)
        p.label(cx, cy, dec(VALS[j][i], 1), 0, -8, TEXT, 12.5, "middle", True)
p.arrow((-10, 0), (WX + 50, 0), TEXT, 1.1, 8.0, None, 0.6)
p.arrow((0, -10), (0, WY + 22), TEXT, 1.1, 8.0, None, 0.6)
p.label(WX + 50, 0, it("x") + " (km)", -2, -8, TEXT, 12, "end")
p.label(0, WY + 22, it("y") + " (km)", 8, 6, TEXT, 12)
p.label(0, 0, "0", -7, 15, TEXT, 11, "middle")
p.label(WX, 0, "388", 0, 15, TEXT, 11, "middle")
p.label(0, WY, "276", -7, 4, TEXT, 11, "end")
save("kar", figure(
    600, 420, [p],
    "Bölge 4 &#215; 4 = 16 eş dikdörtgene bölünmüştür; noktalar alt dikdörtgenlerin merkezleri, sayılar "
    "bu merkezlerde ölçülen kar kalınlığıdır (cm). Koyu renkli hücrelerde kar daha kalındır.",
    aria="A rectangle 388 by 276 km divided into a 4 by 4 grid, each cell shaded by the snow depth and "
         "carrying the value measured at its centre"))
