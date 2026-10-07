# -*- coding: utf-8 -*-
"""
Figures of the chapter "Yüzey Alanı"
(dersler/integral-calculus/yuzey-alani.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box and never directly under a heading.
Concept figures stay visible: bolme below the definition of surface area,
paralelkenar in the statement of the surface area theorem (before the proof),
egim in the prose on the geometric meaning of the integrand. The example and
exercise figures sit under the question text of their box.
The figures are NOT produced at build time. Run

    python scripts/calculus_figures/yal.py
    python scripts/center_figures.py "calculus-yal-*.md"
    python scripts/check_figure_labels.py "scripts/_figures/calculus-yal-*.md"

and paste the markup of scripts/_figures/calculus-yal-<name>.md into the .qmd.
Captions are Turkish on purpose; aria labels are plain ASCII.
"""
import html
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, dot, panel_title, TEXT, THEORY, PRACTICE, BASE, BG, WIDE  # noqa: E402
from svg_plot3 import Camera, Space, vadd, vsub, vscale, vcross, vdot, vunit  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "calculus-yal-"

MINUS = "&#8722;"
DELTA = "&#916;"
GAMMA = "&#947;"
ZWSP = chr(0x200B)          # the zero-width space the sub/sup helpers leave behind


def save(name, markup):
    (OUT_DIR / f"{PREFIX}{name}.md").write_text(markup, encoding="utf-8", newline="\n")
    print(f"{PREFIX}{name}.md")


def it(s):
    """Italic run inside an SVG <text>."""
    return f'<tspan font-style="italic">{s}</tspan>'


def bf(s):
    """Bold upright run (vectors) inside an SVG <text>."""
    return f'<tspan font-weight="700">{s}</tspan>'


def sub(s, size=9.5):
    """Subscript inside an SVG <text>."""
    return f'<tspan font-size="{size}" dy="3.5">{s}</tspan><tspan dy="-3.5">&#8203;</tspan>'


def sup(s, size=9):
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


def text_w(s, size):
    """Rough advance width of a label (0.5 em per visible character, tspans at their own size)."""
    def count(t):
        return len(html.unescape(re.sub(r"<[^>]+>", "", t)).replace(ZWSP, ""))
    width = 0.0
    for m in re.finditer(r'<tspan font-size="([\d.]+)"[^>]*>(.*?)</tspan>', s):
        width += count(m.group(2)) * 0.5 * float(m.group(1))
    rest = re.sub(r'<tspan font-size="[\d.]+"[^>]*>.*?</tspan>', "", s)
    return width + count(rest) * 0.5 * size


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


def faces_of(f, urange, vrange, nu, nv, fill):
    """Quads of a parametric surface, tagged with their fill colour (for multi_surface)."""
    u0, u1 = urange
    v0, v1 = vrange
    grid = [[f(u0 + (u1 - u0) * i / nu, v0 + (v1 - v0) * j / nv) for j in range(nv + 1)]
            for i in range(nu + 1)]
    out = []
    for i in range(nu):
        for j in range(nv):
            out.append(((grid[i][j], grid[i + 1][j], grid[i + 1][j + 1], grid[i][j + 1]), fill))
    return out


def multi_surface(S, faces, opacity=(0.08, 0.34), stroke_width=0.5, stroke_opacity=0.45,
                  light=(-0.35, -0.55, 0.76)):
    """Several surfaces painted back to front together (Space.surface sorts only its own faces)."""
    L = vunit(light)
    items = []
    for quad, fill in faces:
        a, b, c, d = quad
        n = vcross(vsub(c, a), vsub(d, b))
        n = vunit(n) if any(abs(t) > 1e-12 for t in n) else (0.0, 0.0, 1.0)
        shade = 0.5 * (1.0 + abs(vdot(n, L)))
        dep = sum(S.depth(q) for q in quad) / 4.0
        items.append((dep, quad, fill, shade))
    items.sort(key=lambda t: t[0])
    lo, hi = opacity
    for _, quad, fill, shade in items:
        op = lo + (hi - lo) * shade
        pts = " ".join(S.p.P(*S.pt(q)) for q in quad)
        S.p.add(f'<polygon points="{pts}" fill="{fill}" fill-opacity="{op:.3f}" stroke="{fill}" '
                f'stroke-width="{stroke_width}" stroke-opacity="{stroke_opacity}" stroke-linejoin="round"/>')


RIJ = it("R") + sub(it("ij"))
PIJ = it("P") + sub(it("ij"))
TIJ = DELTA + it("T") + sub(it("ij"))
SIJ = DELTA + it("S") + sub(it("ij"))
DX = DELTA + it("x")
DY = DELTA + it("y")

# ============================================================
# bolme: grid on D, one cell R_ij, the patch Delta S_ij and the tangent piece Delta T_ij
# ============================================================
XM, YM = 3.0, 3.2
NX, NY = 4, 4
HX, HY = XM / NX, YM / NY          # 0.75, 0.8
CI, CJ = 2, 2                      # highlighted cell


def fb(x, y):
    return 3.6 - 0.2 * x * x - 0.15 * y * y


def fbx(x, y):
    return -0.4 * x


def fby(x, y):
    return -0.3 * y


cam = Camera(azimuth=32.0, elevation=24.0)
pl, S = fit_space(cam, [(0, 0, 0), (4.0, 0, 0), (0, 4.2, 0), (0, 0, 4.6), (XM, YM, 0), (XM, 0, 0),
                        (0, YM, fb(0, YM)), (0, 0, fb(0, 0))], 40, 30, 64, 0.3)
S.axes(4.0, 4.2, 4.6)
# the floor: D with its grid and the cell R_ij
S.polygon([(0, 0, 0), (XM, 0, 0), (XM, YM, 0), (0, YM, 0)], BASE, 0.10, BASE, 1.2)
for k in range(1, NX):
    S.line([(k * HX, 0, 0), (k * HX, YM, 0)], BASE, 0.8, None, 0.55)
for k in range(1, NY):
    S.line([(0, k * HY, 0), (XM, k * HY, 0)], BASE, 0.8, None, 0.55)
x0c, y0c = CI * HX, CJ * HY
cell = [(x0c, y0c, 0), (x0c + HX, y0c, 0), (x0c + HX, y0c + HY, 0), (x0c, y0c + HY, 0)]
S.polygon(cell, PRACTICE, 0.30, PRACTICE, 1.4)
# vertical guides from the corners of the cell
for (cx, cy, _) in cell:
    S.guide([(cx, cy, 0), (cx, cy, fb(cx, cy))], TEXT, 0.55, 1.0, "4 3")
# the surface S and its grid lines
S.surface(lambda u, v: (u, v, fb(u, v)), (0, XM), (0, YM), nu=12, nv=12, fill=THEORY, stroke=THEORY,
          opacity=(0.05, 0.20), stroke_width=0.4, stroke_opacity=0.0)
for k in range(NX + 1):
    S.curve(lambda t, k=k: (k * HX, t, fb(k * HX, t)), 0, YM, THEORY, 0.8, 40, None, 0.6)
for k in range(NY + 1):
    S.curve(lambda t, k=k: (t, k * HY, fb(t, k * HY)), 0, XM, THEORY, 0.8, 40, None, 0.6)
# the patch Delta S_ij on the surface
ns = 12
edge = ([(x0c + HX * k / ns, y0c) for k in range(ns + 1)] +
        [(x0c + HX, y0c + HY * k / ns) for k in range(1, ns + 1)] +
        [(x0c + HX - HX * k / ns, y0c + HY) for k in range(1, ns + 1)] +
        [(x0c, y0c + HY - HY * k / ns) for k in range(1, ns)])
S.polygon([(a, b, fb(a, b)) for a, b in edge], THEORY, 0.40, THEORY, 1.4)
# the tangent parallelogram Delta T_ij at P_ij
P0 = (x0c, y0c, fb(x0c, y0c))
av = (HX, 0.0, fbx(x0c, y0c) * HX)
bv = (0.0, HY, fby(x0c, y0c) * HY)
para = [P0, vadd(P0, av), vadd(vadd(P0, av), bv), vadd(P0, bv)]
S.polygon(para, PRACTICE, 0.26, PRACTICE, 1.8)
S.point(P0, PRACTICE, 4.0)
S.point((x0c, y0c, 0), TEXT, 3.2)
# labels
splabel(S, P0, PIJ, -10, -6, PRACTICE, 12.5, "end", True)
# right of the dashed guide that drops from the corner P_ij + b
splabel(S, vadd(P0, bv), TIJ, 9, 24, PRACTICE, 12.5, "start", True)
S.label(vadd(P0, av), SIJ, -14, 22, THEORY, 12.5, "end", True)
splabel(S, (x0c, y0c, 0), "(" + it("x") + sub(it("i")) + ", " + it("y") + sub(it("j")) + ")", -9, -7, TEXT,
        11.5, "end")
S.label((x0c + HX, y0c + HY / 2, 0), RIJ, 12, 12, PRACTICE, 12.5, "start", True)
S.label((XM, 0.35, 0), it("D"), -2, 16, BASE, 13, "end", True)
splabel(S, (0, YM, fb(0, YM)), it("S"), 10, -14, THEORY, 13, "start", True)
# Delta x and Delta y on the far edges of D
S.line([(x0c, YM + 0.25, 0), (x0c + HX, YM + 0.25, 0)], TEXT, 1.0, None, 0.7)
for xx in (x0c, x0c + HX):
    S.line([(xx, YM + 0.15, 0), (xx, YM + 0.35, 0)], TEXT, 1.0, None, 0.7)
S.label((x0c + HX / 2, YM + 0.25, 0), DX, 6, 14, TEXT, 11.5)
S.line([(XM + 0.25, y0c, 0), (XM + 0.25, y0c + HY, 0)], TEXT, 1.0, None, 0.7)
for yy in (y0c, y0c + HY):
    S.line([(XM + 0.15, yy, 0), (XM + 0.35, yy, 0)], TEXT, 1.0, None, 0.7)
S.label((XM + 0.25, y0c + HY / 2, 0), DY, 0, 17, TEXT, 11.5, "middle")
save("bolme", figure(
    int(pl.x0 + pl.w + 40), int(pl.y0 + pl.h + 30), [pl],
    "<em>D</em> dikdörtgeni <em>&#916;x</em> &#215; <em>&#916;y</em> boyutlu alt dikdörtgenlere bölünür. "
    "<em>R<sub>ij</sub></em>'nin sol alt köşesi (<em>x<sub>i</sub></em>, <em>y<sub>j</sub></em>)'nin "
    "üstündeki <em>P<sub>ij</sub></em> noktasında <em>S</em>'ye teğet olan düzlemin <em>R<sub>ij</sub></em> "
    "üstündeki parçası bir paralelkenardır (turuncu). Alanı <em>&#916;T<sub>ij</sub></em>, yüzeyin "
    "<em>R<sub>ij</sub></em> üstündeki parçasının (mavi) alanı <em>&#916;S<sub>ij</sub></em>'ye yakındır.",
    aria="Surface S over a rectangle D divided into a 4 by 4 grid; one cell R_ij is shaded, the patch of "
         "the surface above it is drawn darker and the tangent parallelogram at the point P_ij above the "
         "corner (x_i, y_j) is drawn on top of it"))

# ============================================================
# paralelkenar: the tangent parallelogram spanned by a and b over R_ij
# ============================================================
X0P, Y0P, ZP = 0.6, 0.7, 1.7
DXP, DYP = 1.6, 2.0
FXP, FYP = -0.35, 0.60
P = (X0P, Y0P, ZP)
A = (DXP, 0.0, FXP * DXP)
B = (0.0, DYP, FYP * DYP)
cam = Camera(azimuth=35.0, elevation=22.0)
corners = [P, vadd(P, A), vadd(vadd(P, A), B), vadd(P, B)]
floor = [(c[0], c[1], 0.0) for c in corners]
N = vunit(vcross(A, B))
C = vscale(0.25, vadd(vadd(corners[0], corners[1]), vadd(corners[2], corners[3])))
NTIP = vadd(C, vscale(1.25, N))
pl, S = fit_space(cam, [(0, 0, 0), (2.9, 0, 0), (0, 3.3, 0), (0, 0, 3.6), NTIP] + corners + floor,
                  40, 30, 80, 0.3)
S.axes(2.9, 3.3, 3.6)
S.polygon(floor, BASE, 0.16, BASE, 1.4)
for c in corners:
    S.guide([(c[0], c[1], 0.0), c], TEXT, 0.55, 1.0, "4 3")
S.polygon(corners, PRACTICE, 0.22, PRACTICE, 1.3)
S.arrow(P, vadd(P, A), PRACTICE, 2.4, 9.0)
S.arrow(P, vadd(P, B), PRACTICE, 2.4, 9.0)
S.arrow(C, NTIP, THEORY, 2.2, 9.0)
S.point(P, PRACTICE, 4.0)
S.label(P, PIJ, -2, -12, PRACTICE, 12.5, "end", True)
S.label(vadd(P, vscale(0.5, A)), bf("a"), -10, -2, PRACTICE, 13.5, "end")
S.label(vadd(P, vscale(0.5, B)), bf("b"), 0, -10, PRACTICE, 13.5, "middle")
S.label(NTIP, bf("a") + " &#215; " + bf("b"), 8, -2, THEORY, 12.5, "start")
S.label(vadd(vadd(P, vscale(0.55, A)), vscale(0.7, B)), TIJ, 0, 4, PRACTICE, 12.5, "middle", True)
S.label(vscale(0.5, vadd(floor[0], floor[2])), RIJ, 0, 5, BASE, 12.5, "middle", True)
# Delta x beside the back-left edge, Delta y below the front edge of the floor rectangle
S.label(vscale(0.5, vadd(floor[0], floor[1])), DX, -8, -6, TEXT, 11.5, "end")
S.label(vscale(0.5, vadd(floor[1], floor[2])), DY, 0, 18, TEXT, 11.5, "middle")
save("paralelkenar", figure(
    int(pl.x0 + pl.w + 40), int(pl.y0 + pl.h + 30), [pl],
    "Teğet düzlemin <em>R<sub>ij</sub></em> üstündeki parçası, <em>P<sub>ij</sub></em> köşesinden çıkan "
    "<b>a</b> = <em>&#916;x</em> <b>i</b> + <em>f<sub>x</sub></em> <em>&#916;x</em> <b>k</b> ve "
    "<b>b</b> = <em>&#916;y</em> <b>j</b> + <em>f<sub>y</sub></em> <em>&#916;y</em> <b>k</b> vektörlerinin "
    "gerdiği paralelkenardır. <b>a</b> ve <b>b</b>'nin <em>xy</em>-düzlemine izdüşümleri "
    "<em>R<sub>ij</sub></em>'nin kenarlarıdır; <b>a</b> &#215; <b>b</b> paralelkenara diktir ve "
    "uzunluğu alanını verir.",
    aria="Rectangle R_ij on the floor with side lengths dx and dy, the tangent parallelogram above it "
         "with corner P_ij and edge vectors a and b, and the normal vector a x b at its centre"))

# ============================================================
# egim: section along the steepest direction, stretch factor 1/cos(gamma)
# ============================================================
G = math.radians(34.0)
L0 = 3.0
XA, ZA = 1.0, 1.4
XB, ZB = XA + L0, ZA + L0 * math.tan(G)
p = eq_plot(30, 20, 80, (-0.2, 5.4), (-0.6, 4.5))
p.line([(-0.1, 0), (5.2, 0)], TEXT, 1.2, None, 0.6)
p.line([(XA, 0), (XB, 0)], BASE, 3.2)
p.line([(XA - 0.6, ZA - 0.6 * math.tan(G)), (XB + 0.6, ZB + 0.6 * math.tan(G))], PRACTICE, 1.0, "5 4", 0.6)
p.line([(XA, ZA), (XB, ZB)], PRACTICE, 3.2)
p.line([(XA, 0), (XA, ZA)], TEXT, 1.0, "4 3", 0.6)
p.line([(XB, 0), (XB, ZB)], TEXT, 1.0, "4 3", 0.6)
p.line([(XA, ZA), (XB, ZA)], TEXT, 0.9, "2 3", 0.5)
p.arc(XA, ZA, 0.9, 0.0, G, TEXT, 1.2)
p.label(XA + 0.9 * math.cos(G / 2), ZA + 0.9 * math.sin(G / 2), it(GAMMA), 8, 4, TEXT, 13)
# normal n and vertical k at the midpoint of the tilted segment
XMID, ZMID = (XA + XB) / 2, (ZA + ZB) / 2
NL = 1.5
NV = (-math.sin(G) * NL, math.cos(G) * NL)
p.arrow((XMID, ZMID), (XMID + NV[0], ZMID + NV[1]), THEORY, 2.2, 9.0)
p.arrow((XMID, ZMID), (XMID, ZMID + NL), TEXT, 1.8, 8.0, None, 0.8)
p.arc(XMID, ZMID, 0.75, math.pi / 2, math.pi / 2 + G, TEXT, 1.2)
p.label(XMID - 0.75 * math.sin(G / 2), ZMID + 0.75 * math.cos(G / 2), it(GAMMA), -2, -6, TEXT, 13, "middle")
p.label(XMID + NV[0], ZMID + NV[1], bf("n"), -6, -4, THEORY, 14, "end")
p.label(XMID, ZMID + NL, bf("k"), 7, 4, TEXT, 14)
p.label((XA + XB) / 2, 0, it("&#8467;"), 0, 20, BASE, 14, "middle", True)
p.label(XB, ZB, it("&#8467;") + " / cos " + it(GAMMA), 10, 12, PRACTICE, 13, "start", True)
p.label(5.2, 0, it("xy") + "-düzlemi", 0, 16, TEXT, 11.5, "end")
p.label(XB + 0.6, ZB + 0.6 * math.tan(G), "teğet düzlem", -4, -10, PRACTICE, 11.5, "end")
save("egim", figure(
    480, 420, [p],
    "Teğet düzlemi en dik doğrultusu boyunca kesen düşey düzlem. Düzlem <em>xy</em>-düzlemiyle "
    "<em>&#947;</em> açısı yapar; bu, <b>n</b> normali ile <b>k</b> arasındaki açıdır. Bu doğrultudaki "
    "<em>&#8467;</em> uzunluğundaki bir gölge düzlemde <em>&#8467;</em>/cos <em>&#947;</em> uzunluğuna "
    "karşılık gelir; buna dik (yatay) doğrultudaki uzunluklar değişmez.",
    aria="Side view: a horizontal segment of length l and above it a tilted segment making the angle "
         "gamma with the horizontal, of length l over cos gamma; at the middle of the tilted segment its "
         "normal n and the vertical k make the same angle gamma"))

# ============================================================
# duzlem: the plane -x + 2y + 2z = 6 inside the cylinder x^2 + y^2 = 4
# ============================================================
RD = 2.0


def zpl(x, y):
    return 3.0 + x / 2.0 - y


def rim(t):
    x, y = RD * math.cos(t), RD * math.sin(t)
    return (x, y, zpl(x, y))


cam = Camera(azimuth=35.0, elevation=22.0)
ring = [rim(2 * math.pi * k / 96) for k in range(96)]
# the z axis stops a little above the top of the ellipse (z = 3 + sqrt 5) and is labelled beside its tip
pl, S = fit_space(cam, [(-2.2, -2.2, 0), (2.2, 2.2, 0), (3.2, 0, 0), (0, 3.2, 0), (0, 0, 5.7), (-2.2, 2.2, 0),
                        (2.2, -2.2, 0)] + ring, 40, 30, 68, 0.3)
S.axes(3.2, 3.2, 5.7, -2.4, -2.4, 0.0, offsets=((-4, 13), (10, 4), (10, 6)))
S.polygon([(RD * math.cos(2 * math.pi * k / 96), RD * math.sin(2 * math.pi * k / 96), 0) for k in range(96)],
          BASE, 0.16, BASE, 1.4)
# silhouette lines of the cylinder and a few vertical guides
az = math.radians(35.0)
for sgn in (1, -1):
    t = az + sgn * math.pi / 2
    x, y = RD * math.cos(t), RD * math.sin(t)
    S.line([(x, y, 0), (x, y, zpl(x, y))], TEXT, 1.1, "5 4", 0.6)
for k in range(8):
    t = 2 * math.pi * k / 8 + 0.2
    x, y = RD * math.cos(t), RD * math.sin(t)
    S.guide([(x, y, 0), (x, y, zpl(x, y))], TEXT, 0.35, 0.9, "3 3")
S.polygon(ring, THEORY, 0.28, THEORY, 1.8)
S.point((0, 0, 3.0), THEORY, 3.2)
S.label((0, 0, 3.0), "(0, 0, 3)", -8, -6, THEORY, 11.5, "end")
S.label((RD * math.cos(0.6), RD * math.sin(0.6), 0), it("D"), 6, 14, BASE, 13, "start", True)
splabel(S, rim(math.radians(150)), it("S"), 14, 22, THEORY, 13, "start", True)
S.label((0, 0, 5.0), MINUS + it("x") + " + 2" + it("y") + " + 2" + it("z") + " = 6", 24, 0, THEORY, 11.5)
S.label((RD * math.cos(-0.9), RD * math.sin(-0.9), 0), it("x") + "² + " + it("y") + "² = 4", 10, 14, TEXT, 11.5)
save("duzlem", figure(
    int(pl.x0 + pl.w + 40), int(pl.y0 + pl.h + 30), [pl],
    "&#8722;<em>x</em> + 2<em>y</em> + 2<em>z</em> = 6 düzleminin <em>x</em>² + <em>y</em>² = 4 silindiri içinde "
    "kalan parçası <em>S</em> bir elipstir; gölgesi <em>D</em> ise 2 yarıçaplı dairedir. Eğik düzlem "
    "gölgesinden büyüktür: alanı <em>D</em>'nin alanının 3/2 katıdır.",
    aria="Disk D of radius 2 in the xy-plane, the dashed vertical cylinder over its boundary and the "
         "tilted elliptic piece S of the plane -x + 2y + 2z = 6 cut out by the cylinder"))

# ============================================================
# ucgen: Example 1, the triangle T and the surface z = x^2 + 2y + 2 over it
# ============================================================
p = eq_plot(40, 46, 160, (-0.25, 1.45), (-0.22, 1.32))
p.arrow((-0.2, 0), (1.42, 0), TEXT, 1.2, 8.0, None, 0.6)
p.arrow((0, -0.2), (0, 1.3), TEXT, 1.2, 8.0, None, 0.6)
p.label(1.42, 0, it("x"), -2, 17, TEXT, 12.5, "end")
p.label(0, 1.3, it("y"), 9, 5, TEXT, 12.5)
p.polygon([(0, 0), (1, 0), (1, 1)], BASE, 0.18, BASE, 1.8)
p.points([(0, 0), (1, 0), (1, 1)], TEXT, 3.4)
p.label(0, 0, "(0, 0)", -6, 17, TEXT, 11.5, "end")
p.label(1, 0, "(1, 0)", 6, 17, TEXT, 11.5)
p.label(1, 1, "(1, 1)", 8, -4, TEXT, 11.5)
p.label(0.45, 0.45, it("y") + " = " + it("x"), -10, -8, BASE, 12, "end")
p.label(0.72, 0.28, it("T"), 0, 5, BASE, 15, "middle", True)
panel_title(p, it("xy") + "-düzleminde " + it("T"))

ZS = 0.4                     # vertical scale of the 3-D panel


def zs(P):
    return (P[0], P[1], ZS * P[2])


def fu(x, y):
    return x * x + 2 * y + 2


# looked at from the -y side: the surface rises with y, so this is the side its upper face turns to
cam = Camera(azimuth=-55.0, elevation=26.0)
left = p.x0 + p.w + 70
# the z axis ends a little above the highest point z = 5; a small pad keeps the panel title close to it
pts = [zs(q) for q in [(0, 0, 0), (1.5, 0, 0), (0, 1.5, 0), (0, 0, 5.4), (1, 1, 5), (1, 0, 3), (0, 1, 4),
                       (1.3, 1.3, 0)]]
pl3, S = fit_space(cam, pts, left, 46, 190, 0.12)
S.axes(1.5, 1.5, ZS * 5.4, offsets=((6, 14), (8, -6), (-10, -4)))
S.polygon([(0, 0, 0), (1, 0, 0), (1, 1, 0)], BASE, 0.18, BASE, 1.6)
for v in [(0, 0), (1, 0), (1, 1)]:
    S.guide([(v[0], v[1], 0), zs((v[0], v[1], fu(*v)))], TEXT, 0.5, 1.0, "4 3")
S.surface(lambda u, v: zs((u, v, fu(u, v))), (0, 1), (0, 1), nu=8, nv=8, fill=THEORY, stroke=THEORY,
          opacity=(0.03, 0.10), stroke_width=0.4, stroke_opacity=0.25)
S.surface(lambda u, v: zs((u, u * v, fu(u, u * v))), (0, 1), (0, 1), nu=8, nv=8, fill=THEORY, stroke=THEORY,
          opacity=(0.18, 0.42), stroke_width=0.5, stroke_opacity=0.5)
edge = ([(t, 0.0) for t in [k / 16 for k in range(17)]] + [(1.0, t) for t in [k / 16 for k in range(1, 17)]] +
        [(1 - t, 1 - t) for t in [k / 16 for k in range(1, 16)]])
S.line([zs((a, b, fu(a, b))) for a, b in edge] + [zs((0, 0, 2))], THEORY, 1.8)
for (a, b), (dx, dy, anc) in (((0, 0), (8, -8, "start")), ((1, 0), (-10, 4, "end")), ((1, 1), (-10, -6, "end"))):
    Q = zs((a, b, fu(a, b)))
    S.point(Q, THEORY, 3.4)
    splabel(S, Q, f"({a}, {b}, {fu(a, b)})", dx, dy, THEORY, 11.5, anc)
S.label((0.68, 0.22, 0), it("T"), 0, 5, BASE, 14, "middle", True)
splabel(S, zs((0.0, 1.0, fu(0, 1))), it("z") + " = " + it("x") + "² + 2" + it("y") + " + 2", 8, -8, THEORY, 11.5)
panel_title(pl3, it("T") + "'nin üstündeki yüzey parçası")
save("ucgen", figure(
    int(pl3.x0 + pl3.w + 30), int(max(p.y0 + p.h, pl3.y0 + pl3.h) + 30), [p, pl3],
    "Solda (0, 0), (1, 0), (1, 1) köşeli <em>T</em> üçgeni: 0 &#8804; <em>x</em> &#8804; 1, "
    "0 &#8804; <em>y</em> &#8804; <em>x</em>. Sağda <em>z</em> = <em>x</em>² + 2<em>y</em> + 2 yüzeyinin "
    "<em>T</em> üstündeki parçası (koyu) ve birim kare üstündeki devamı (açık). Sağ panelde düşey "
    "ölçek küçültülmüştür.",
    css_class=WIDE,
    aria="Left: the triangle T with vertices (0, 0), (1, 0), (1, 1) under the line y = x. Right: the "
         "surface z = x^2 + 2y + 2 over the unit square with its piece above T drawn darker"))

# ============================================================
# paraboloit: Example 2, z = x^2 + y^2 under z = 9, over the disk of radius 3
# ============================================================
cam = Camera(azimuth=35.0, elevation=16.0)
# the z axis ends just above the rim z = 9 and is labelled beside its tip; the label of the surface sits
# outside its left silhouette, so the tall paraboloid does not make a narrow, tall figure
pl, S = fit_space(cam, [(-3.2, -3.2, 0), (3.2, 3.2, 0), (4.0, 0, 0), (0, 4.0, 0), (0, 0, 10.1),
                        (-3, 3, 9), (3, -3, 9), (-3.2, 3.2, 0), (3.2, -3.2, 0)], 40, 30, 40, 0.4)
S.axes(4.0, 4.0, 10.1, offsets=((-4, 13), (10, 4), (10, 6)))
S.polygon([(3 * math.cos(2 * math.pi * k / 96), 3 * math.sin(2 * math.pi * k / 96), 0) for k in range(96)],
          BASE, 0.18, BASE, 1.4)
th0 = math.radians(-30)
S.line([(0, 0, 0), (3 * math.cos(th0), 3 * math.sin(th0), 0)], BASE, 1.4, "4 3")
S.label((1.5 * math.cos(th0), 1.5 * math.sin(th0), 0), "3", 0, 15, BASE, 12, "middle", True)
S.surface(lambda r, t: (r * math.cos(t), r * math.sin(t), r * r), (0, 3), (0, 2 * math.pi), nu=9, nv=28,
          fill=THEORY, stroke=THEORY, opacity=(0.05, 0.24), stroke_width=0.45, stroke_opacity=0.4)
S.circle((0, 0, 9), (1, 0, 0), (0, 1, 0), 3, THEORY, 2.0)
S.label((3 * math.cos(math.radians(125)), 3 * math.sin(math.radians(125)), 9), it("z") + " = 9", 10, 5, THEORY,
        12, "start", True)
# start-anchored at its estimated width, so the leftmost ink of the figure is the start of the label
SURF = it("z") + " = " + it("x") + "² + " + it("y") + "²"
S.label((math.sqrt(6.0) * math.cos(math.radians(-55)), math.sqrt(6.0) * math.sin(math.radians(-55)), 6.0),
        SURF, -4 - text_w(SURF, 11.5), 4, THEORY, 11.5, "start")
S.label((3 * math.cos(math.radians(120)), 3 * math.sin(math.radians(120)), 0), it("D"), -10, 10, BASE, 13,
        "end", True)
save("paraboloit", figure(
    int(pl.x0 + pl.w + 40), int(pl.y0 + pl.h + 30), [pl],
    "<em>z</em> = <em>x</em>² + <em>y</em>² paraboloidinin <em>z</em> = 9 düzleminin altında kalan parçası. "
    "Paraboloit bu düzlemi <em>x</em>² + <em>y</em>² = 9 çemberi boyunca keser; bu yüzden parçanın "
    "<em>xy</em>-düzlemine izdüşümü 3 yarıçaplı <em>D</em> dairesidir.",
    aria="Paraboloid z = x^2 + y^2 up to the circle x^2 + y^2 = 9 at height z = 9, above the disk D of "
         "radius 3 in the xy-plane"))

# ============================================================
# iki-silindir: the boundary of the solid y^2 + z^2 <= 1, x^2 + z^2 <= 1
# ============================================================
cam = Camera(azimuth=28.0, elevation=26.0)
pl, S = fit_space(cam, [(-1.1, -1.1, -1.1), (1.1, 1.1, 1.1), (1.9, 0, 0), (0, 1.9, 0), (0, 0, 1.8),
                        (-1.1, 1.1, -1.1), (1.1, -1.1, 1.1), (1.1, -1.1, -1.1), (-1.1, 1.1, 1.1)],
                  40, 30, 130, 0.25)


def c1(phi, s):
    """Cylinder x^2 + z^2 = 1, the part with |y| <= |x|."""
    return (math.cos(phi), s * abs(math.cos(phi)), math.sin(phi))


def c2(phi, s):
    """Cylinder y^2 + z^2 = 1, the part with |x| <= |y|."""
    return (s * abs(math.cos(phi)), math.cos(phi), math.sin(phi))


VIEW = cam.d                       # unit vector toward the viewer


def center(quad):
    return vscale(0.25, vadd(vadd(quad[0], quad[1]), vadd(quad[2], quad[3])))


front, back = [], []
for quad, fill in (faces_of(c1, (0, 2 * math.pi), (-1, 1), 40, 6, THEORY) +
                   faces_of(c2, (0, 2 * math.pi), (-1, 1), 40, 6, PRACTICE)):
    c = center(quad)
    out = (c[0], 0.0, c[2]) if fill == THEORY else (0.0, c[1], c[2])   # outward normal of the cylinder
    (front if vdot(out, VIEW) > 0 else back).append((quad, fill))
# the solid is convex: the hidden half is only hinted, the visible half is shaded
multi_surface(S, back, opacity=(0.02, 0.05), stroke_width=0.4, stroke_opacity=0.12)
multi_surface(S, front, opacity=(0.14, 0.42), stroke_width=0.45, stroke_opacity=0.4)
# the two seam ellipses in the planes y = x and y = -x: solid where visible, dashed where hidden
NS = 160
for sgn in (1, -1):
    seg, vis = [], None
    for k in range(NS + 1):
        t = 2 * math.pi * k / NS
        Q = (math.cos(t), sgn * math.cos(t), math.sin(t))
        v = vdot((Q[0], Q[1], 2 * Q[2]), VIEW) > 0      # sum of the two outward normals
        if vis is None or v == vis:
            seg.append(Q)
        else:
            seg.append(Q)
            S.line(seg, TEXT, 1.5 if vis else 0.9, None if vis else "4 3", 0.8 if vis else 0.4)
            seg = [Q]
        vis = v
    S.line(seg, TEXT, 1.5 if vis else 0.9, None if vis else "4 3", 0.8 if vis else 0.4)
# only the parts of the axes outside the solid; they leave it at (1, 0, 0), (0, 1, 0), (0, 0, 1)
for k, (end, name, off) in enumerate((((1.9, 0, 0), "x", (-4, 14)), ((0, 1.9, 0), "y", (10, 4)),
                                      ((0, 0, 1.8), "z", (-10, -4)))):
    S.arrow(vscale(1.0 / end[k], end), end, TEXT, 1.1, 7.0, None, 0.55)
    S.label(end, name, off[0], off[1], TEXT, 11.5, "middle", False, True)
splabel(S, c1(math.radians(-25), 0.3), it("x") + "² + " + it("z") + "² = 1", -12, 22, THEORY, 12, "end", True)
splabel(S, c2(math.radians(-25), -0.2), it("y") + "² + " + it("z") + "² = 1", 14, 22, PRACTICE, 12, "start", True)
save("iki-silindir", figure(
    int(pl.x0 + pl.w + 40), int(pl.y0 + pl.h + 30), [pl],
    "<em>y</em>² + <em>z</em>² &#8804; 1 ve <em>x</em>² + <em>z</em>² &#8804; 1 eşitsizliklerini birlikte "
    "sağlayan cismin yüzeyi. Mavi parçalar <em>x</em>² + <em>z</em>² = 1 silindirinden (|<em>y</em>| "
    "&#8804; |<em>x</em>|), turuncu parçalar <em>y</em>² + <em>z</em>² = 1 silindirinden (|<em>x</em>| "
    "&#8804; |<em>y</em>|) gelir; iki silindir <em>y</em> = &#177;<em>x</em> düzlemlerindeki elipsler "
    "boyunca birleşir.",
    aria="The solid common to two perpendicular unit cylinders: its surface consists of four pieces of "
         "the cylinder x^2 + z^2 = 1 and four pieces of the cylinder y^2 + z^2 = 1 meeting along two "
         "ellipses in the planes y = x and y = -x"))
