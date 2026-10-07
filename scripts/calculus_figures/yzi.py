# -*- coding: utf-8 -*-
"""
Figures of the chapter "Yüzey İntegralleri"
(dersler/integral-calculus/yuzey-integralleri.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box and never directly under a heading.
Concept figures stay visible: bolme below the definition of the surface
integral, mobius in the prose on non-orientable surfaces, iki-yon below the
definition of an orientation, kure-yon below the definition of the positive
orientation of a closed surface, aki-prizma in the prose that motivates the
flux. The example figures (kapali-silindir, paraboloit-kapak) sit under the
question text of their example box.
The figures are NOT produced at build time. Run

    python scripts/calculus_figures/yzi.py
    python scripts/center_figures.py "calculus-yzi-*.md"
    python scripts/check_figure_labels.py "scripts/_figures/calculus-yzi-*.md"

and paste the markup of scripts/_figures/calculus-yzi-<name>.md into the .qmd.
Captions are Turkish on purpose; aria labels are plain ASCII.
"""
import html
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, panel_title, TEXT, THEORY, PRACTICE, BASE, BG, WIDE  # noqa: E402
from svg_plot3 import Camera, Space, vadd, vsub, vscale, vcross, vdot, vunit, vnorm  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "calculus-yzi-"

MINUS = "&#8722;"
DELTA = "&#916;"
THETA = "&#952;"
PI = "&#960;"
ZWSP = chr(0x200B)          # the zero-width space the sub/sup helpers leave behind
D2R = math.pi / 180.0
O = (0.0, 0.0, 0.0)


def save(name, markup):
    (OUT_DIR / f"{PREFIX}{name}.md").write_text(markup, encoding="utf-8", newline="\n")
    print(f"{PREFIX}{name}.md")


def it(s):
    """Italic run inside an SVG <text>."""
    return f'<tspan font-style="italic">{s}</tspan>'


def bf(s):
    """Bold upright run (vectors) inside an SVG <text>."""
    return f'<tspan font-weight="700">{s}</tspan>'


def sub(s, size=9):
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
    """Label on a page-coloured plate, for text that must sit on a shaded surface."""
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


def leader(S, P, s, dx, dy, color=TEXT, size=12.5, anchor="start", bold=True, gap=5.0):
    """Label at a pixel offset from a space point, joined to the point by a thin leader line."""
    X, Y = S.pt(P)
    px, py = S.p.X(X), S.p.Y(Y)
    ex, ey = px + dx, py + dy - 0.35 * size
    if anchor == "start":
        ex -= 3
    elif anchor == "end":
        ex += 3
    L = math.hypot(ex - px, ey - py) or 1.0
    sx, sy = px + (ex - px) * gap / L, py + (ey - py) * gap / L
    S.p.add(f'<line x1="{sx:.1f}" y1="{sy:.1f}" x2="{ex:.1f}" y2="{ey:.1f}" stroke="{color}" '
            f'stroke-width="0.9" opacity="0.8"/>')
    S.p.label(X, Y, s, dx, dy, color, size, anchor, bold)


def vis_curve(S, f, t0, t1, normal, color=THEORY, width=1.6, samples=120, hidden_opacity=0.45,
              hidden_dash="4 3", opacity=1.0):
    """Curve drawn solid where its outward normal faces the viewer and dashed behind."""
    d = S.cam.d
    pts = [(f(t0 + (t1 - t0) * k / samples), vdot(normal(t0 + (t1 - t0) * k / samples), d) >= 0)
           for k in range(samples + 1)]
    run, state = [pts[0][0]], pts[0][1]
    for P, v in pts[1:]:
        run.append(P)
        if v != state:
            S.line(run, color, width, None if state else hidden_dash, opacity if state else hidden_opacity)
            run, state = [P], v
    S.line(run, color, width, None if state else hidden_dash, opacity if state else hidden_opacity)


def sphere_outline(S, C, R, color=THEORY, fill_opacity=0.10, width=1.5):
    """Screen-space disk: the silhouette of a sphere (equal-aspect panel)."""
    X, Y = S.pt(C)
    p = S.p
    p.add(f'<circle cx="{p.X(X):.1f}" cy="{p.Y(Y):.1f}" r="{p.R(R):.1f}" fill="{color}" '
          f'fill-opacity="{fill_opacity}" stroke="{color}" stroke-width="{width}"/>')


def quads(f, urange, vrange, nu, nv):
    """Quads of a parametric surface (u, v) -> f(u, v)."""
    u0, u1 = urange
    v0, v1 = vrange
    grid = [[f(u0 + (u1 - u0) * i / nu, v0 + (v1 - v0) * j / nv) for j in range(nv + 1)]
            for i in range(nu + 1)]
    return [(grid[i][j], grid[i + 1][j], grid[i + 1][j + 1], grid[i][j + 1])
            for i in range(nu) for j in range(nv)]


def face_markup(S, quad, fill, opacity=(0.06, 0.26), stroke_width=0.4, stroke_opacity=0.35,
                light=(-0.35, -0.55, 0.76)):
    """One shaded quad (same shading rule as Space.surface)."""
    a, b, c, d = quad
    n = vcross(vsub(c, a), vsub(d, b))
    n = vunit(n) if vnorm(n) > 1e-12 else (0.0, 0.0, 1.0)
    shade = 0.5 * (1.0 + abs(vdot(n, vunit(light))))
    op = opacity[0] + (opacity[1] - opacity[0]) * shade
    pts = " ".join(S.p.P(*S.pt(q)) for q in quad)
    return (f'<polygon points="{pts}" fill="{fill}" fill-opacity="{op:.3f}" stroke="{fill}" '
            f'stroke-width="{stroke_width}" stroke-opacity="{stroke_opacity}" stroke-linejoin="round"/>')


class Painter:
    """Collect faces and arrows with a depth and emit them back to front."""

    def __init__(self, S):
        self.S = S
        self.items = []

    def face(self, quad, fill, **kw):
        dep = sum(self.S.depth(q) for q in quad) / 4.0
        self.items.append((dep, ("face", quad, fill, kw)))

    def arrow(self, P0, P1, color, width=1.8, head=8.0, bias=0.0):
        dep = self.S.depth(P0) + bias
        self.items.append((dep, ("arrow", P0, P1, color, width, head)))

    def emit(self):
        for _, item in sorted(self.items, key=lambda t: t[0]):
            if item[0] == "face":
                _, quad, fill, kw = item
                self.S.p.add(face_markup(self.S, quad, fill, **kw))
            else:
                _, P0, P1, color, width, head = item
                self.S.arrow(P0, P1, color, width, head)


PIJ = it("P") + sub(it("ij")) + sup("*")
SIJ = it("S") + sub(it("ij"))
RIJ = it("R") + sub(it("ij"))

# ============================================================
# bolme: the grid on the parameter domain D and the patches S_ij of the surface
# ============================================================
U0, U1, V0, V1 = 0.5, 3.5, 0.5, 2.5
NU, NV = 6, 4
DU, DV = (U1 - U0) / NU, (V1 - V0) / NV
CI, CJ = 3, 2                                    # highlighted cell [2, 2.5] x [1.5, 2]
CU0, CV0 = U0 + CI * DU, V0 + CJ * DV
US, VS = CU0 + 0.55 * DU, CV0 + 0.45 * DV        # sample point (u*, v*) in R_ij


def rmap(uu, vv):
    s, w = uu - U0, vv - V0
    return (2.3 - 1.05 * w, 0.25 + 1.0 * s, 1.35 + 0.5 * math.sin(1.45 * s - 0.2) + 0.2 * w)


# left panel: the uv-plane
p = eq_plot(40, 40, 62, (-0.35, 4.0), (-0.35, 3.05))
p.origin_axes("u", "v", opacity=0.55)
p.polygon([(U0, V0), (U1, V0), (U1, V1), (U0, V1)], BASE, 0.10, BASE, 1.3)
for k in range(1, NU):
    p.line([(U0 + k * DU, V0), (U0 + k * DU, V1)], BASE, 0.8, None, 0.6)
for k in range(1, NV):
    p.line([(U0, V0 + k * DV), (U1, V0 + k * DV)], BASE, 0.8, None, 0.6)
p.polygon([(CU0, CV0), (CU0 + DU, CV0), (CU0 + DU, CV0 + DV), (CU0, CV0 + DV)], PRACTICE, 0.32, PRACTICE, 1.5)
p.points([(US, VS)], PRACTICE, 3.4)
p.label(U0 + 0.5 * DU, V0 + 0.5 * DV, it("D"), 0, 5, BASE, 14, "middle", True)
p.label(CU0 + DU, CV0 + DV, RIJ, 4, -6, PRACTICE, 12.5, "start", True)
# Delta u under the bottom edge, Delta v right of the grid at the same row
p.line([(CU0, V0 - 0.16), (CU0 + DU, V0 - 0.16)], TEXT, 1.0, None, 0.7)
for uu in (CU0, CU0 + DU):
    p.line([(uu, V0 - 0.08), (uu, V0 - 0.24)], TEXT, 1.0, None, 0.7)
p.label(CU0 + DU / 2, V0 - 0.16, DELTA + it("u"), 0, 15, TEXT, 11.5, "middle")
p.line([(U1 + 0.16, CV0), (U1 + 0.16, CV0 + DV)], TEXT, 1.0, None, 0.7)
for vv in (CV0, CV0 + DV):
    p.line([(U1 + 0.08, vv), (U1 + 0.24, vv)], TEXT, 1.0, None, 0.7)
p.label(U1 + 0.16, CV0 + DV / 2, DELTA + it("v"), 8, 4, TEXT, 11.5, "start")
left = p

# right panel: the surface
cam = Camera(azimuth=35.0, elevation=24.0)
corners = [rmap(a, b) for a in (U0, U1) for b in (V0, V1)]
right, S = fit_space(cam, [O, (3.0, 0, 0), (0, 3.9, 0), (0, 0, 2.7)] + corners, left.x0 + left.w + 95, 22,
                     62, 0.25)
S.axes(3.0, 3.9, 2.7)
S.surface(lambda a, b: rmap(a, b), (U0, U1), (V0, V1), nu=24, nv=16, fill=THEORY, stroke=THEORY,
          opacity=(0.05, 0.22), stroke_width=0.3, stroke_opacity=0.0)
for k in range(NU + 1):
    S.curve(lambda t, k=k: rmap(U0 + k * DU, t), V0, V1, THEORY, 0.9, 40, None, 0.75)
for k in range(NV + 1):
    S.curve(lambda t, k=k: rmap(t, V0 + k * DV), U0, U1, THEORY, 0.9, 60, None, 0.75)
ns = 10
edge = ([(CU0 + DU * k / ns, CV0) for k in range(ns + 1)] +
        [(CU0 + DU, CV0 + DV * k / ns) for k in range(1, ns + 1)] +
        [(CU0 + DU - DU * k / ns, CV0 + DV) for k in range(1, ns + 1)] +
        [(CU0, CV0 + DV - DV * k / ns) for k in range(1, ns)])
S.polygon([rmap(a, b) for a, b in edge], PRACTICE, 0.40, PRACTICE, 1.5)
PS = rmap(US, VS)
S.point(PS, PRACTICE, 3.4)
leader(S, PS, PIJ, 34, -40, PRACTICE)
leader(S, rmap(CU0 + 0.8 * DU, CV0 + 0.1 * DV), SIJ, 36, 34, PRACTICE)
splabel(S, rmap(U0, V1), it("S"), -8, -12, THEORY, 14, "end", True)
# the map r between the panels
mid_y = left.y0 + left.h * 0.45
gap = Plot(left.x0 + left.w + 12, mid_y - 10, 70, 20, (0, 1), (0, 1))
gap.arrow((0.05, 0.5), (0.95, 0.5), TEXT, 1.6, 9.0, None, 0.85)
gap.label(0.5, 0.5, bf("r"), 0, -9, TEXT, 14, "middle")
save("bolme", figure(
    int(right.x0 + right.w + 30), int(max(left.y0 + left.h, right.y0 + right.h) + 30), [left, gap, right],
    "<b>r</b>, <em>uv</em>-düzlemindeki <em>D</em> dikdörtgenini <em>S</em> yüzeyine götürür. "
    "<em>D</em>'nin <em>&#916;u</em> &#215; <em>&#916;v</em> boyutlu her <em>R<sub>ij</sub></em> alt "
    "dikdörtgeni, yüzeyde bir <em>S<sub>ij</sub></em> yamasına karşılık gelir. Riemann toplamında "
    "<em>f</em>, yamadan seçilen bir <em>P<sub>ij</sub></em>* noktasında hesaplanır ve yamanın alanıyla "
    "çarpılır.",
    css_class=WIDE,
    aria="Left: the rectangle D in the uv-plane divided into a 6 by 4 grid with one cell R_ij of size du by "
         "dv shaded. Right: its image, a curved surface S divided into patches; the patch S_ij that "
         "corresponds to R_ij is shaded and contains the sample point P_ij*"))

# ============================================================
# kapali-silindir: the solid inside x^2 + y^2 = 1 between z = 0 and z = 1 + x
# ============================================================
cam2 = Camera(azimuth=258.0, elevation=16.0)
pl, S = fit_space(cam2, [O, (1.75, 0, 0), (0, 1.8, 0), (0, 0, 2.75), (1, 0, 2), (-1, 0, 0), (0, -1, 1),
                         (0, 1, 1), (0.94, -0.34, 0), (-0.94, 0.34, 0)], 40, 30, 110, 0.25)
d2 = cam2.d
# axes first: the solid is translucent and covers what lies behind or inside it
S.line([O, (1.0, 0, 0)], TEXT, 1.0, "4 3", 0.45)
S.arrow((0, 0, 0), (0, 1.8, 0), TEXT, 1.1, 7.0, None, 0.55)
S.line([O, (0, 0, 1.0)], TEXT, 1.0, "4 3", 0.45)
S.label((0, 1.8, 0), it("y"), -8, 2, TEXT, 11.5, "end")
# bottom disk S_2 (z = 0)
S.polygon([(math.cos(t), math.sin(t), 0.0) for t in [2 * math.pi * k / 96 for k in range(96)]],
          BASE, 0.14, "none")
vis_curve(S, lambda t: (math.cos(t), math.sin(t), 0.0), 0, 2 * math.pi,
          lambda t: (math.cos(t), math.sin(t), 0.0), BASE, 1.5, 192, 0.55)
# lateral surface S_1
S.surface(lambda t, s: (math.cos(t), math.sin(t), s * (1 + math.cos(t))), (0, 2 * math.pi), (0, 1),
          nu=72, nv=6, fill=THEORY, stroke=THEORY, opacity=(0.05, 0.24), stroke_width=0.3, stroke_opacity=0.0)
# silhouette generators of the cylinder
for t in (math.atan2(-d2[0], d2[1]), math.atan2(d2[0], -d2[1])):
    S.line([(math.cos(t), math.sin(t), 0), (math.cos(t), math.sin(t), 1 + math.cos(t))], THEORY, 1.5)
# top S_3 on the plane z = 1 + x
top = [(math.cos(t), math.sin(t), 1 + math.cos(t)) for t in [2 * math.pi * k / 96 for k in range(96)]]
S.polygon(top, PRACTICE, 0.18, PRACTICE, 1.6)
# visible parts of the axes
S.arrow((1.0, 0, 0), (1.75, 0, 0), TEXT, 1.1, 7.0, None, 0.55)
S.arrow((0, 0, 1.0), (0, 0, 2.75), TEXT, 1.1, 7.0, None, 0.55)
S.label((1.75, 0, 0), it("x"), 8, 4, TEXT, 11.5, "start")
S.label((0, 0, 2.75), it("z"), -9, 2, TEXT, 11.5, "end")
# labels
S.label((math.cos(-1.35), math.sin(-1.35), 0.45), it("S") + sub("1"), 0, 0, THEORY, 13.5, "middle", True)
leader(S, (math.cos(-0.25), math.sin(-0.25), 0.7), it("x") + sup("2") + " + " + it("y") + sup("2") + " = 1",
       40, 30, THEORY, 12, "start", False)
leader(S, (0.45, 0.35, 1.45), it("S") + sub("3") + ": " + it("z") + " = 1 + " + it("x"), -70, -62, PRACTICE,
       12.5, "end", True)
leader(S, (-0.35, 0.55, 0.0), it("S") + sub("2") + ": " + it("z") + " = 0", -60, 52, BASE, 12.5, "end", True)
save("kapali-silindir", figure(
    int(pl.x0 + pl.w + 60), int(pl.y0 + pl.h + 40), [pl],
    "<em>S</em> yüzeyi üç parçadan oluşur: <em>x</em>² + <em>y</em>² = 1 silindirinin yan yüzü "
    "<em>S</em><sub>1</sub>, <em>z</em> = 0 düzlemindeki birim daire <em>S</em><sub>2</sub> ve "
    "<em>z</em> = 1 + <em>x</em> düzleminin bu dairenin üstündeki parçası <em>S</em><sub>3</sub>. "
    "Tavan, <em>x</em> = 1'de 2 yüksekliğine çıkar ve (&#8722;1, 0, 0) noktasında tabana değer.",
    aria="Solid bounded by the cylinder x^2 + y^2 = 1, the plane z = 0 and the plane z = 1 + x: the side S1 "
         "is part of the cylinder, the bottom S2 is the unit disk and the tilted elliptic top S3 lies in the "
         "plane z = 1 + x"))

# ============================================================
# mobius: the normal carried once around the centre line comes back reversed
# ============================================================


def mob(uu, w):
    q = 1.0 + 0.5 * w * math.cos(uu / 2)
    return (q * math.cos(uu), q * math.sin(uu), 0.5 * w * math.sin(uu / 2))


def mob_n(uu):
    """Unit normal r_w x r_u on the centre circle (it equals -(r_u x r_w))."""
    return (-math.sin(uu / 2) * math.cos(uu), -math.sin(uu / 2) * math.sin(uu), math.cos(uu / 2))


cam3 = Camera(azimuth=-60.0, elevation=32.0)
pl, S = fit_space(cam3, [mob(2 * math.pi * k / 60, w) for k in range(60) for w in (-1, 1)] +
                  [(1, 0, 0.75), (1, 0, -0.75)], 40, 40, 140, 0.3)
pt = Painter(S)
for q in quads(mob, (0, 2 * math.pi), (-1, 1), 72, 6):
    pt.face(q, THEORY, opacity=(0.06, 0.26), stroke_width=0.3, stroke_opacity=0.0)
NL = 0.62
NK = 12
for k in range(1, NK):
    uu = 2 * math.pi * k / NK
    P0 = mob(uu, 0)
    pt.arrow(P0, vadd(P0, vscale(NL, mob_n(uu))), THEORY, 1.5, 7.0, 0.05)
pt.emit()
# centre line with a travel arrow, the two rims
S.curve(lambda t: mob(t, 0), 0.08, 2 * math.pi - 0.08, TEXT, 1.0, 240, "4 3", 0.6)
S.curve(lambda t: mob(t, 1), 0, 4 * math.pi, THEORY, 1.3, 400, None, 0.85)
S.segment_arrow(lambda t: mob(t, 0), 3.75, 4.05, TEXT, 1.4, 8.0, 20)
# start and end at the same point P
P = mob(0, 0)
S.arrow(P, vadd(P, vscale(NL + 0.1, mob_n(0))), PRACTICE, 2.3, 9.0)
S.arrow(P, vadd(P, vscale(NL + 0.1, mob_n(2 * math.pi))), BASE, 2.3, 9.0)
S.point(P, TEXT, 3.6)
S.label(P, it("P"), 10, 4, TEXT, 13, "start", True)
S.label(vadd(P, vscale(NL + 0.1, mob_n(0))), bf("n"), 8, 4, PRACTICE, 14, "start")
S.label(vadd(P, vscale(NL + 0.1, mob_n(2 * math.pi))), MINUS + bf("n"), 8, 6, BASE, 14, "start")
save("mobius", figure(
    int(pl.x0 + pl.w + 40), int(pl.y0 + pl.h + 30), [pl],
    "Möbius şeridi. <em>P</em> noktasında seçilen <b>n</b> normali orta çember (kesikli) boyunca sürekli "
    "olarak taşınırsa, bir tur sonra aynı <em>P</em> noktasına &#8722;<b>n</b> olarak döner. Bu yüzden "
    "şeridin her noktasında sürekli değişen bir birim normal seçilemez.",
    aria="Moebius strip with unit normals drawn along its centre circle; the normal n chosen at the point P "
         "turns over gradually and after one full turn arrives at P again as -n"))

# ============================================================
# iki-yon: the two orientations n and -n of a surface patch
# ============================================================


def gq(xx, yy):
    return 1.45 + 0.35 * math.sin(1.3 * xx + 0.4) - 0.18 * (yy - 1.1) ** 2


def gq_n(xx, yy):
    gx = 0.35 * 1.3 * math.cos(1.3 * xx + 0.4)
    gy = -0.36 * (yy - 1.1)
    return vunit((-gx, -gy, 1.0))


cam4 = Camera(azimuth=35.0, elevation=22.0)
box = [O, (2.6, 0, 0), (0, 2.9, 0), (0, 0, 2.7), (2.0, 2.2, gq(2.0, 2.2)), (2.0, 0, gq(2.0, 0)),
       (0, 2.2, gq(0, 2.2)), (2.0, 2.2, 0.4)]
panels = []
for idx, sgn in enumerate((1, -1)):
    pl, S = fit_space(cam4, box, 30 + idx * 360, 40, 88, 0.25)
    S.axes(2.6, 2.9, 2.7)
    feet = [(a, b) for a in (0.45, 1.0, 1.55) for b in (0.55, 1.1, 1.65)]
    if sgn < 0:
        for a, b in feet:
            P0 = (a, b, gq(a, b))
            S.arrow(P0, vadd(P0, vscale(-0.75, gq_n(a, b))), PRACTICE, 1.6, 7.5)
    S.surface(lambda a, b: (a, b, gq(a, b)), (0, 2.0), (0, 2.2), nu=14, nv=14, fill=THEORY, stroke=THEORY,
              opacity=(0.08, 0.30), stroke_width=0.3, stroke_opacity=0.0)
    S.curve(lambda t: (t, 0, gq(t, 0)), 0, 2.0, THEORY, 1.3)
    S.curve(lambda t: (2.0, t, gq(2.0, t)), 0, 2.2, THEORY, 1.3)
    S.curve(lambda t: (t, 2.2, gq(t, 2.2)), 0, 2.0, THEORY, 1.3)
    S.curve(lambda t: (0, t, gq(0, t)), 0, 2.2, THEORY, 1.3)
    for a, b in feet:
        P0 = (a, b, gq(a, b))
        S.point(P0, PRACTICE, 2.8)
        if sgn > 0:
            S.arrow(P0, vadd(P0, vscale(0.75, gq_n(a, b))), PRACTICE, 1.6, 7.5)
    a, b = 0.45, 1.65
    tip = vadd((a, b, gq(a, b)), vscale(0.75 * sgn, gq_n(a, b)))
    S.label(tip, bf("n") if sgn > 0 else MINUS + bf("n"), 8, 4 if sgn > 0 else 12, PRACTICE, 14, "start")
    panel_title(pl, "normal " + (bf("n") if sgn > 0 else MINUS + bf("n")))
    panels.append(pl)
save("iki-yon", figure(
    int(panels[-1].x0 + panels[-1].w + 30), int(max(q.y0 + q.h for q in panels) + 30), panels,
    "Yönlendirilebilir bir yüzeyin iki yönlendirmesi. Solda her noktada <b>n</b>, sağda &#8722;<b>n</b> "
    "seçilmiştir; iki seçimde de normal yüzey boyunca sürekli değişir. Bu yüzey bir fonksiyon grafiği "
    "olduğundan soldaki yukarı, sağdaki aşağı yönlendirmedir.",
    css_class=WIDE,
    aria="Two copies of the same surface patch, the graph of a function: on the left the unit normals n "
         "point upward at nine points, on the right the opposite normals -n point downward"))

# ============================================================
# kure-yon: outward (positive) and inward (negative) orientation of a sphere
# ============================================================


def sph(rho, theta, phi):
    return (rho * math.sin(phi) * math.cos(theta), rho * math.sin(phi) * math.sin(theta), rho * math.cos(phi))


cam5 = Camera(azimuth=35.0, elevation=20.0)
box5 = [(1.9, 0, 0), (0, 1.9, 0), (0, 0, 1.9), (0, 0, -1.6), (-1.6, -1.6, 0), (1.6, 1.6, 0), (1.6, -1.6, 0),
        (-1.6, 1.6, 0)]
feet5 = [(35 * D2R + t * D2R, f * D2R) for t, f in ((-80, 50), (80, 50), (-88, 95), (88, 95), (-55, 140),
                                                      (55, 140), (0, 160))]
panels = []
for idx, sgn in enumerate((1, -1)):
    pl, S = fit_space(cam5, box5, 30 + idx * 330, 40, 80, 0.2)
    for e in ((1.0, 0, 0), (0, 1.0, 0), (0, 0, 1.0)):
        S.line([O, e], TEXT, 1.0, "4 3", 0.45)
        S.arrow(e, vscale(1.9, e), TEXT, 1.1, 7.0, None, 0.55)
    S.label((1.9, 0, 0), it("x"), -4, 13, TEXT, 11.5, "middle")
    S.label((0, 1.9, 0), it("y"), 10, 4, TEXT, 11.5, "middle")
    S.label((0, 0, 1.9), it("z"), -10, -4, TEXT, 11.5, "middle")
    sphere_outline(S, O, 1.0, THEORY, 0.12, 1.5)
    vis_curve(S, lambda t: (math.cos(t), math.sin(t), 0), 0, 2 * math.pi,
              lambda t: (math.cos(t), math.sin(t), 0), THEORY, 1.1, 120, 0.4)
    if sgn < 0:
        S.point(O, TEXT, 2.4)
    for t, f in feet5:
        P0 = sph(1.0, t, f)
        if sgn > 0:
            S.arrow(P0, sph(1.6, t, f), PRACTICE, 1.6, 7.5)
        else:
            S.arrow(P0, sph(0.5, t, f), PRACTICE, 1.4, 7.0)
        S.point(P0, PRACTICE, 2.6)
    panel_title(pl, "pozitif: dışa doğru" if sgn > 0 else "negatif: içe doğru")
    panels.append(pl)
save("kure-yon", figure(
    int(panels[-1].x0 + panels[-1].w + 30), int(max(q.y0 + q.h for q in panels) + 30), panels,
    "Kapalı bir yüzey olan kürenin iki yönlendirmesi. Solda normaller kürenin içindeki bölgeden dışa "
    "doğru bakar (pozitif yönlendirme), sağda içe doğru bakar (negatif yönlendirme).",
    css_class=WIDE,
    aria="Two unit spheres: on the left the unit normals point outward, on the right they point inward "
         "toward the centre"))

# ============================================================
# aki-prizma: the fluid that crosses a small patch in time dt fills a slanted prism
# ============================================================
cam6 = Camera(azimuth=35.0, elevation=22.0)
rgt, upv, tow = cam6.r, cam6.u, cam6.d


def scr(a, b, c):
    """World vector with screen components a (right), b (up), c (toward the viewer)."""
    return vadd(vadd(vscale(a, rgt), vscale(b, upv)), vscale(c, tow))


C6 = O
N6 = vunit(scr(0.78, 0.0, 0.62))                     # unit normal: to the right and toward the viewer
E1 = scr(0.0, 1.5, 0.0)                              # patch edges, both perpendicular to N6
E2 = vscale(1.35, vunit(scr(-0.62, 0.0, 0.78)))
V6 = vadd(vscale(1.45, N6), scr(0.0, 0.62, -0.25))   # v dt, slanted against the normal
H6 = vdot(V6, N6)
base = [vadd(C6, vadd(vscale(sa, E1), vscale(sb, E2))) for sa, sb in ((-0.5, -0.5), (-0.5, 0.5), (0.5, 0.5),
                                                                         (0.5, -0.5))]
topf = [vadd(q, V6) for q in base]
pl, S = fit_space(cam6, base + topf + [vadd(C6, vscale(1.0, N6))], 40, 40, 190, 0.45)
for q in base:
    S.line([q, vadd(q, V6)], TEXT, 1.0, "4 3", 0.55)
S.polygon(topf, THEORY, 0.07, THEORY, 1.0, "4 3")
S.polygon(base, THEORY, 0.30, THEORY, 1.6)
Cn = vadd(C6, vscale(H6, N6))                         # foot of the height on the top face
S.line([vadd(C6, vscale(0.85, N6)), Cn], BASE, 1.4, "2 3", 0.95)
S.arrow(C6, vadd(C6, vscale(0.85, N6)), BASE, 2.2, 9.0)
S.point(Cn, BASE, 2.6)
S.arrow(base[0], vadd(base[0], V6), PRACTICE, 2.2, 9.0)
S.point(C6, BASE, 3.0)
S.label(vadd(C6, vscale(0.85, N6)), bf("n"), 0, -10, BASE, 14, "middle")
leader(S, vadd(C6, vscale(0.5 * (H6 + 0.85), N6)), "(" + bf("v") + " &#183; " + bf("n") + ") " + DELTA + it("t"),
       30, 46, BASE, 12.5, "start", True)
S.label(vadd(base[0], vscale(0.5, V6)), bf("v") + " " + DELTA + it("t"), 6, 18, PRACTICE, 13, "start", True)
splabel(S, vadd(C6, vadd(vscale(0.28, E1), vscale(-0.12, E2))), DELTA + it("S"), 0, 5, THEORY, 13, "middle", True)
save("aki-prizma", figure(
    int(pl.x0 + pl.w + 40), int(pl.y0 + pl.h + 30), [pl],
    "Alanı <em>&#916;S</em> olan küçük, düz bir yamadan <em>&#916;t</em> sürede geçen akışkan, tabanı bu yama "
    "ve yan kenarları <b>v</b> <em>&#916;t</em> olan eğik bir prizmayı doldurur. Prizmanın yüksekliği "
    "<b>v</b> <em>&#916;t</em>'nin <b>n</b> doğrultusundaki bileşeni (<b>v</b> &#183; <b>n</b>) "
    "<em>&#916;t</em>, hacmi (<b>v</b> &#183; <b>n</b>) <em>&#916;S</em> <em>&#916;t</em>'dir.",
    aria="A small flat patch of area dS with unit normal n; the fluid crossing it in time dt fills a slanted "
         "prism whose side edges are the vector v dt; the height of the prism along n is (v . n) dt"))

# ============================================================
# paraboloit-kapak: the boundary of the solid under z = 1 - x^2 - y^2 with outward normals
# ============================================================
cam7 = Camera(azimuth=35.0, elevation=20.0)
pl, S = fit_space(cam7, [O, (1.85, 0, 0), (0, 1.9, 0), (0, 0, 1.85), (0, 0, -0.75), (1, 0, 0), (-1, 0, 0),
                         (0, 1, 0), (0, -1, 0), (0.7, 0.7, -0.6)], 40, 40, 140, 0.25)
# downward normals of the bottom disk S_2, drawn first so the solid covers their upper ends
foot2 = [(0.45, 35 * D2R + 0.4), (0.75, 35 * D2R - 0.9), (0.7, 35 * D2R + 1.5), (0.0, 0.0)]
for rr, tt in foot2:
    P0 = (rr * math.cos(tt), rr * math.sin(tt), 0.0)
    S.arrow(P0, vadd(P0, (0, 0, -0.62)), PRACTICE, 1.6, 7.5)
S.polygon([(math.cos(t), math.sin(t), 0.0) for t in [2 * math.pi * k / 96 for k in range(96)]], BASE, 0.16, "none")
S.line([O, (1.0, 0, 0)], TEXT, 1.0, "4 3", 0.45)
S.line([O, (0, 1.0, 0)], TEXT, 1.0, "4 3", 0.45)
S.line([O, (0, 0, 1.0)], TEXT, 1.0, "4 3", 0.45)
vis_curve(S, lambda t: (math.cos(t), math.sin(t), 0.0), 0, 2 * math.pi,
          lambda t: (math.cos(t), math.sin(t), -0.3), BASE, 1.4, 192, 0.55)
S.surface(lambda rr, tt: (rr * math.cos(tt), rr * math.sin(tt), 1 - rr * rr), (0, 1), (0, 2 * math.pi),
          nu=10, nv=40, fill=THEORY, stroke=THEORY, opacity=(0.05, 0.24), stroke_width=0.3, stroke_opacity=0.0)
# outline of the paraboloid as seen by the camera: points where the normal is perpendicular to d
d7 = cam7.d
sil = []
for k in range(721):
    tt = 2 * math.pi * k / 720
    c = 2 * (d7[0] * math.cos(tt) + d7[1] * math.sin(tt))
    if c < -1e-9:
        rr = -d7[2] / c
        if rr <= 1.0:
            sil.append((tt, (rr * math.cos(tt), rr * math.sin(tt), 1 - rr * rr)))
sil.sort(key=lambda q: (q[0] - math.atan2(d7[1], d7[0])) % (2 * math.pi))
S.line([q for _, q in sil], THEORY, 1.5)
S.arrow((1.0, 0, 0), (1.85, 0, 0), TEXT, 1.1, 7.0, None, 0.55)
S.arrow((0, 1.0, 0), (0, 1.9, 0), TEXT, 1.1, 7.0, None, 0.55)
S.arrow((0, 0, 1.0), (0, 0, 1.85), TEXT, 1.1, 7.0, None, 0.55)
S.label((1.85, 0, 0), it("x"), -4, 14, TEXT, 11.5, "middle")
S.label((0, 1.9, 0), it("y"), 10, 4, TEXT, 11.5, "middle")
S.label((0, 0, 1.85), it("z"), -10, -2, TEXT, 11.5, "middle")
# outward normals of S_1: (2x, 2y, 1) normalised
foot1 = [(0.0, 0.0), (0.55, 35 * D2R), (0.6, 35 * D2R + 1.5), (0.6, 35 * D2R - 1.5), (0.85, 35 * D2R + 0.75),
         (0.85, 35 * D2R - 0.75)]
for rr, tt in foot1:
    xx, yy = rr * math.cos(tt), rr * math.sin(tt)
    P0 = (xx, yy, 1 - rr * rr)
    S.arrow(P0, vadd(P0, vscale(0.62, vunit((2 * xx, 2 * yy, 1.0)))), PRACTICE, 1.6, 7.5)
    S.point(P0, PRACTICE, 2.6)
splabel(S, (0.35 * math.cos(35 * D2R - 1.0), 0.35 * math.sin(35 * D2R - 1.0), 1 - 0.35 ** 2), it("S") + sub("1"),
        -8, 12, THEORY, 13.5, "end", True)
leader(S, (0.55 * math.cos(35 * D2R - 1.2), 0.55 * math.sin(35 * D2R - 1.2), 0.0), it("S") + sub("2"), -70, 40, BASE,
       13.5, "end", True)
save("paraboloit-kapak", figure(
    int(pl.x0 + pl.w + 40), int(pl.y0 + pl.h + 30), [pl],
    "<em>E</em> cisminin sınırı iki parçadır: <em>z</em> = 1 &#8722; <em>x</em>² &#8722; <em>y</em>² "
    "paraboloidinin <em>z</em> &#8805; 0 kısmı <em>S</em><sub>1</sub> ve <em>z</em> = 0 düzlemindeki birim "
    "daire <em>S</em><sub>2</sub>. Dışa doğru yönlendirmede <em>S</em><sub>1</sub>'in normalleri yukarı, "
    "<em>S</em><sub>2</sub>'ninkiler aşağı bakar.",
    aria="Solid under the paraboloid z = 1 - x^2 - y^2 and above the plane z = 0; the outward unit normals on "
         "the curved top S1 point up and away, those on the flat bottom disk S2 point straight down"))
