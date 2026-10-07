# -*- coding: utf-8 -*-
"""
Figures of the chapter "Küresel Koordinatlarda Üç Katlı İntegraller"
(dersler/integral-calculus/kuresel-koordinatlarda-uc-katli-integraller.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box and never directly under a heading.
The figures are NOT produced at build time. Run

    python scripts/calculus_figures/kur.py
    python scripts/center_figures.py "calculus-kur-*.md"
    python scripts/check_figure_labels.py "scripts/_figures/calculus-kur-*.md"

and paste the markup of scripts/_figures/calculus-kur-<name>.md into the .qmd.
Captions are Turkish on purpose; aria labels are plain ASCII.

Spherical coordinates follow the chapter: rho is the distance to the origin,
theta the polar angle of the projection to the xy-plane and phi the angle
measured from the positive z axis.
"""
import html
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, panel_title, TEXT, THEORY, PRACTICE, BASE, BG, WIDE  # noqa: E402
from svg_plot3 import Camera, Space, vadd, vsub, vscale, vdot, vunit  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "calculus-kur-"

MINUS = "&#8722;"
RHO, THETA, PHI, PI = "&#961;", "&#952;", "&#966;", "&#960;"
DELTA = "&#916;"
ZWSP = chr(0x200B)          # the zero-width space the sub/sup helpers leave behind
D2R = math.pi / 180.0


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


R_, T_, P_ = it(RHO), it(THETA), it(PHI)


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


def fit_row(cam, pts_list, x0, y0, ppu, pad=0.12, gap=20):
    """A row of equal-aspect panels: each panel is just wide enough for its own points,
    all panels share one vertical range so that their origins and titles line up."""
    qs = [[cam.project(P)[:2] for P in pts] for pts in pts_list]
    yr = (min(b for q in qs for _, b in q) - pad, max(b for q in qs for _, b in q) + pad)
    out, left = [], x0
    for q in qs:
        xr = (min(a for a, _ in q) - pad, max(a for a, _ in q) + pad)
        plot = eq_plot(left, y0, ppu, xr, yr)
        out.append((plot, Space(plot, cam)))
        left += plot.w + gap
    return out


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


def sph(rho, theta, phi):
    """Spherical -> rectangular coordinates (angles in radians)."""
    return (rho * math.sin(phi) * math.cos(theta), rho * math.sin(phi) * math.sin(theta), rho * math.cos(phi))


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


def disk(p, X, Y, R, color=THEORY, opacity=0.10, stroke=None, width=1.4, sopacity=1.0, dash=None):
    """Screen-space disk (data units of an equal-aspect panel): the silhouette of a sphere."""
    st = (f' stroke="{stroke}" stroke-width="{width}" stroke-opacity="{sopacity}"'
          + (f' stroke-dasharray="{dash}"' if dash else "")) if stroke else ' stroke="none"'
    p.add(f'<circle cx="{p.X(X):.1f}" cy="{p.Y(Y):.1f}" r="{p.R(R):.1f}" fill="{color}" '
          f'fill-opacity="{opacity}"{st}/>')


def sphere_outline(S, C, R, color=THEORY, fill_opacity=0.10, width=1.5, dash=None, sopacity=1.0):
    X, Y = S.pt(C)
    disk(S.p, X, Y, R, color, fill_opacity, color, width, sopacity, dash)


def angle_arc3(S, C, e1, e2, r, a0, a1, color=TEXT, width=1.2, samples=40, opacity=0.9):
    """Arc of radius r about C in the plane of the orthonormal pair e1, e2, from angle a0 to a1."""
    S.curve(lambda t: vadd(C, vadd(vscale(r * math.cos(t), e1), vscale(r * math.sin(t), e2))),
            a0, a1, color, width, samples, None, opacity)


def right_angle(S, V, u1, u2, s=0.16, color=TEXT, opacity=0.6):
    """Small right-angle mark at V between the unit directions u1, u2."""
    A = vadd(V, vscale(s, u1))
    B = vadd(A, vscale(s, u2))
    Cc = vadd(V, vscale(s, u2))
    S.line([A, B, Cc], color, 0.9, None, opacity)


CAM = Camera(azimuth=35.0, elevation=22.0)
K = (0.0, 0.0, 1.0)
O = (0.0, 0.0, 0.0)

# ============================================================
# nokta: a point with its spherical coordinates and the two right triangles
# ============================================================
rho0, th0, ph0 = 3.0, 50 * D2R, 42 * D2R
P0 = sph(rho0, th0, ph0)
Pf = (P0[0], P0[1], 0.0)
Q0 = (0.0, 0.0, P0[2])
hdir = (math.cos(th0), math.sin(th0), 0.0)
pl, S = fit_space(CAM, [O, (3.3, 0, 0), (0, 3.4, 0), (0, 0, 3.4), P0, Pf], 40, 30, 92, 0.35)
S.axes(3.3, 3.4, 3.4)
# the right triangles OQP (at Q) and OP'P (at P')
S.polygon([O, Pf, P0], PRACTICE, 0.07)
S.guide([P0, Pf], TEXT, 0.6)
S.guide([P0, Q0], TEXT, 0.6)
S.line([O, Pf], BASE, 1.8)
S.line([O, Q0], BASE, 3.0, None, 0.85)
right_angle(S, Pf, vunit(vsub(O, Pf)), K, 0.17)
right_angle(S, Q0, vunit(vsub(O, Q0)), hdir, 0.17)
S.line([O, P0], PRACTICE, 2.6)
# angle phi between the z axis and OP, angle theta in the floor
angle_arc3(S, O, K, hdir, 0.85, 0.0, ph0, PRACTICE, 1.4)
angle_arc3(S, O, (1, 0, 0), (0, 1, 0), 0.95, 0.0, th0, THEORY, 1.4)
S.point(P0, PRACTICE, 4.2)
S.point(Pf, TEXT, 3.0)
S.point(Q0, TEXT, 3.0)
S.label(sph(1.0, th0, ph0 / 2), P_, 4, -2, PRACTICE, 13, "start", True)
S.label((1.15 * math.cos(th0 / 2), 1.15 * math.sin(th0 / 2), 0), T_, 2, 12, THEORY, 13, "middle", True)
S.label(sph(2.0, th0, ph0), R_, 9, 8, PRACTICE, 13.5, "start", True)
S.label(vscale(0.55, Pf), it("r"), 10, 4, BASE, 13, "start", True)
S.label((0, 0, P0[2] * 0.5), it("z"), -8, 4, BASE, 13, "end", True)
S.label(P0, it("P") + "(" + R_ + ", " + T_ + ", " + P_ + ")", 9, -6, PRACTICE, 12.5)
S.label(P0, "= (" + it("x") + ", " + it("y") + ", " + it("z") + ")", 9, 11, PRACTICE, 12.5)
S.label(Pf, it("P") + "&#8242;(" + it("x") + ", " + it("y") + ", 0)", 8, 15, TEXT, 12)
S.label(Q0, it("Q"), -9, 4, TEXT, 12.5, "end")
S.label(O, it("O"), -8, 12, TEXT, 12.5, "end")
save("nokta", figure(
    int(pl.x0 + pl.w + 60), int(pl.y0 + pl.h + 30), [pl],
    "<em>P</em> noktasının küresel koordinatları: <em>&#961;</em> = |<em>OP</em>| orijine uzaklık, "
    "<em>&#966;</em> pozitif <em>z</em> ekseniyle <em>OP</em> arasındaki açı, <em>&#952;</em> ise "
    "<em>P</em>&#8242; izdüşümünün kutupsal açısıdır. <em>OQP</em> ve <em>OP</em>&#8242;<em>P</em> dik "
    "üçgenlerinden <em>z</em> = <em>&#961;</em> cos <em>&#966;</em> ve <em>r</em> = |<em>OP</em>&#8242;| = "
    "<em>&#961;</em> sin <em>&#966;</em> okunur.",
    aria="Point P in space joined to the origin O by a segment of length rho; the angle phi between the "
         "positive z axis and OP, the projection P' on the xy-plane with polar angle theta, the distance r "
         "from O to P' and the height z, forming the right triangles OQP and OP'P"))

# ============================================================
# yuzeyler: the coordinate surfaces rho = c, theta = c and phi = c (two cases)
# ============================================================
# one row of four panels; each is as wide as its own drawing, all share one vertical range
AXL = (2.3, 2.2, 2.3)                       # axis lengths x, y, z
AXO = ((-5, 16), (12, 5), (-11, -4))        # axis-label offsets for the larger labels of the row
R1 = 1.3                                    # sphere
C2, LH2, Z02, Z12 = 55 * D2R, 2.0, -1.3, 2.0  # half-plane
CONES = ((32 * D2R, 2.0), (135 * D2R, 1.9))   # (c, generator length) of the two half-cones
AX_PTS = [O, (AXL[0], 0, 0), (0, AXL[1], 0), (0, 0, AXL[2])]


def ring(z, r, n=36):
    return [(r * math.cos(2 * math.pi * j / n), r * math.sin(2 * math.pi * j / n), z) for j in range(n)]


u2 = (math.cos(C2), math.sin(C2), 0.0)
rows = fit_row(CAM, [
    AX_PTS + [sph(R1, 2 * math.pi * j / 36, math.pi * i / 6) for j in range(36) for i in range(7)],
    AX_PTS + [(0, 0, Z02), vadd((0, 0, Z02), vscale(LH2, u2)), vadd((0, 0, Z12), vscale(LH2, u2)), (0, 0, Z12)],
    AX_PTS + ring(CONES[0][1] * math.cos(CONES[0][0]), CONES[0][1] * math.sin(CONES[0][0])),
    AX_PTS + ring(CONES[1][1] * math.cos(CONES[1][0]), CONES[1][1] * math.sin(CONES[1][0])),
], 20, 46, 62, 0.22, 16)
panels = []
for idx, (pl, S) in enumerate(rows):
    if idx == 0:
        # the sphere's screen silhouette is a circle of radius R1 about the projected centre
        sphere_outline(S, O, R1, THEORY, 0.10, 1.6)
        vis_curve(S, lambda t: (R1 * math.cos(t), R1 * math.sin(t), 0), 0, 2 * math.pi,
                  lambda t: (math.cos(t), math.sin(t), 0), THEORY, 1.4)
        vis_curve(S, lambda t: (R1 * math.sin(t) * math.cos(1.1), R1 * math.sin(t) * math.sin(1.1),
                                R1 * math.cos(t)), 0, 2 * math.pi,
                  lambda t: (math.sin(t) * math.cos(1.1), math.sin(t) * math.sin(1.1), math.cos(t)), THEORY, 1.2)
        S.axes(*AXL, size=15, offsets=AXO)
        S.guide([O, sph(R1, -0.6, math.pi / 2 - 0.55)], PRACTICE, 0.9, 1.4, None)
        splabel(S, sph(R1 * 0.55, -0.6, math.pi / 2 - 0.55), it("c"), 2, -8, PRACTICE, 16.5, "start", True)
        panel_title(pl, R_ + " = " + it("c") + ": küre", TEXT, 16.5)
    elif idx == 1:
        quad = [(0, 0, Z02), vadd((0, 0, Z02), vscale(LH2, u2)), vadd((0, 0, Z12), vscale(LH2, u2)), (0, 0, Z12)]
        S.polygon(quad, THEORY, 0.16, THEORY, 1.3)
        S.axes(*AXL, size=15, offsets=AXO)
        S.line([O, vscale(LH2, u2)], THEORY, 1.8)
        angle_arc3(S, O, (1, 0, 0), (0, 1, 0), 0.7, 0, C2, PRACTICE, 1.5)
        S.label((0.85 * math.cos(C2 / 2), 0.85 * math.sin(C2 / 2), 0), it("c"), 0, 15, PRACTICE, 16.5, "middle",
                True)
        panel_title(pl, T_ + " = " + it("c") + ": yarı düzlem", TEXT, 16.5)
    else:
        c, Lg = CONES[idx - 2]
        S.axes(*AXL, size=15, offsets=AXO)
        S.surface(lambda s, v: sph(s, v, c), (0, Lg), (0, 2 * math.pi), nu=6, nv=24, fill=THEORY, stroke=THEORY,
                  opacity=(0.04, 0.16), stroke_width=0.4, stroke_opacity=0.35)
        S.circle((0, 0, Lg * math.cos(c)), (1, 0, 0), (0, 1, 0), Lg * math.sin(c), THEORY, 1.6)
        g = -0.9   # azimuth of the marked generator
        S.line([O, sph(Lg, g, c)], THEORY, 1.6)
        angle_arc3(S, O, K, (math.cos(g), math.sin(g), 0), 0.55, 0, c, PRACTICE, 1.5)
        S.label(sph(0.75, g, c / 2), it("c"), 4, 3, PRACTICE, 16.5, "start", True)
        if idx == 2:
            panel_title(pl, P_ + " = " + it("c") + ", 0 &lt; " + it("c") + " &lt; " + PI + "/2", TEXT, 16.5)
        else:
            panel_title(pl, P_ + " = " + it("c") + ", " + PI + "/2 &lt; " + it("c") + " &lt; " + PI, TEXT, 16.5)
    panels.append(pl)
save("yuzeyler", figure(
    int(panels[-1].x0 + panels[-1].w + 20), int(max(q.y0 + q.h for q in panels) + 20), panels,
    "Küresel koordinatlarda bir koordinatı sabitleyen yüzeyler. <em>&#961;</em> = <em>c</em> merkezi orijinde "
    "olan bir küre, <em>&#952;</em> = <em>c</em> kenarı <em>z</em> ekseni olan düşey bir yarı düzlem, "
    "<em>&#966;</em> = <em>c</em> ise ekseni <em>z</em> ekseni olan bir yarı konidir: <em>c</em> &lt; "
    "<em>&#960;</em>/2 iken yukarı, <em>c</em> &gt; <em>&#960;</em>/2 iken aşağı açılır.",
    css_class=WIDE,
    aria="Four panels: the sphere rho = c, the vertical half-plane theta = c through the z axis, the upward "
         "half-cone phi = c with c below pi/2 and the downward half-cone phi = c with c above pi/2"))

# ============================================================
# ornek-nokta: the point (2, pi/4, pi/3) of the first worked example
# ============================================================
rho1, th1, ph1 = 2.0, math.pi / 4, math.pi / 3
P1 = sph(rho1, th1, ph1)
P1f = (P1[0], P1[1], 0.0)
h1 = (math.cos(th1), math.sin(th1), 0.0)
pl, S = fit_space(CAM, [O, (2.2, 0, 0), (0, 2.3, 0), (0, 0, 2.2), P1, P1f], 40, 30, 120, 0.3)
S.axes(2.2, 2.3, 2.2)
S.guide([(P1[0], 0, 0), P1f, (0, P1[1], 0)], TEXT, 0.45)
S.guide([P1, P1f], TEXT, 0.55)
S.guide([P1, (0, 0, P1[2])], TEXT, 0.45)
S.guide([O, P1f], TEXT, 0.55)
S.line([O, P1], PRACTICE, 2.6)
angle_arc3(S, O, K, h1, 0.55, 0.0, ph1, PRACTICE, 1.4)
angle_arc3(S, O, (1, 0, 0), (0, 1, 0), 0.6, 0.0, th1, THEORY, 1.4)
S.point(P1, PRACTICE, 4.2)
S.point(P1f, TEXT, 2.6)
S.label(sph(0.75, th1, ph1 / 2), PI + "/3", 4, -2, PRACTICE, 12, "start", True)
S.label((0.78 * math.cos(th1 / 2), 0.78 * math.sin(th1 / 2), 0), PI + "/4", 6, 12, THEORY, 12, "middle", True)
S.label(sph(1.0, th1, ph1), "2", 3, 18, PRACTICE, 13, "start", True)
S.label((0, 0, P1[2]), "1", -9, 4, TEXT, 11.5, "end")
S.label(P1, "(2, " + PI + "/4, " + PI + "/3)", 9, -6, PRACTICE, 12.5)
S.label(P1, "= (&#8730;(3/2), &#8730;(3/2), 1)", 9, 11, PRACTICE, 12)
save("ornek-nokta", figure(
    int(pl.x0 + pl.w + 60), int(pl.y0 + pl.h + 30), [pl],
    "Küresel koordinatları (2, <em>&#960;</em>/4, <em>&#960;</em>/3) olan nokta: orijinden 2 birim uzakta, "
    "<em>z</em> ekseniyle <em>&#960;</em>/3 açı yapan ve izdüşümü <em>x</em> ekseniyle <em>&#960;</em>/4 açı "
    "yapan doğrultuda. Dik koordinatları (&#8730;(3/2), &#8730;(3/2), 1)'dir.",
    aria="The point with spherical coordinates (2, pi/4, pi/3): a segment of length 2 from the origin making "
         "the angle pi/3 with the z axis, whose projection makes the angle pi/4 with the x axis; height 1"))


# ============================================================
# kama: a spherical wedge and its three edge lengths
# ============================================================
ra, rb = 2.0, 3.0
ta, tb = 70 * D2R, 110 * D2R
pa, pb = 35 * D2R, 62 * D2R
pl, S = fit_space(CAM, [O, (2.6, 0, 0), (0, 3.4, 0), (0, 0, 3.3), sph(rb, ta, pa), sph(rb, tb, pb),
                        sph(rb, ta, pb), sph(rb, tb, pa)], 40, 30, 100, 0.35)
S.axes(2.6, 3.4, 3.3)
# floor sector between the traces of the two half-planes
RF = 1.25
S.polygon([O] + [(RF * math.cos(ta + (tb - ta) * k / 30), RF * math.sin(ta + (tb - ta) * k / 30), 0)
                 for k in range(31)], BASE, 0.12)
for tt in (ta, tb):
    S.guide([O, (RF * math.cos(tt), RF * math.sin(tt), 0)], BASE, 0.7, 0.9)
# guide rays from the origin to the inner corners
for tt in (ta, tb):
    for pp in (pa, pb):
        S.guide([O, sph(ra, tt, pp)], TEXT, 0.4, 0.9)
# the six faces of the wedge, back to front
faces = [
    lambda u, v: sph(ra, ta + (tb - ta) * u, pa + (pb - pa) * v),
    lambda u, v: sph(ra + (rb - ra) * u, ta, pa + (pb - pa) * v),
    lambda u, v: sph(ra + (rb - ra) * u, ta + (tb - ta) * v, pa),
    lambda u, v: sph(ra + (rb - ra) * u, ta + (tb - ta) * v, pb),
    lambda u, v: sph(ra + (rb - ra) * u, tb, pa + (pb - pa) * v),
    lambda u, v: sph(rb, ta + (tb - ta) * u, pa + (pb - pa) * v),
]
for _, f in sorted(((S.depth(f(0.5, 0.5)), f) for f in faces), key=lambda t: t[0]):
    S.surface(f, (0, 1), (0, 1), nu=3, nv=3, fill=THEORY, stroke=THEORY, opacity=(0.08, 0.20),
              stroke_width=0.3, stroke_opacity=0.18)
# the twelve edges
for rr in (ra, rb):
    for tt in (ta, tb):
        S.curve(lambda t, rr=rr, tt=tt: sph(rr, tt, t), pa, pb, THEORY, 1.4, 30)
    for pp in (pa, pb):
        S.curve(lambda t, rr=rr, pp=pp: sph(rr, t, pp), ta, tb, THEORY, 1.4, 30)
for tt in (ta, tb):
    for pp in (pa, pb):
        S.line([sph(ra, tt, pp), sph(rb, tt, pp)], THEORY, 1.4)
# the three highlighted edges at the front corner (rb, ta, pb)
S.line([sph(ra, ta, pb), sph(rb, ta, pb)], PRACTICE, 3.2)
S.curve(lambda t: sph(rb, ta, t), pa, pb, BASE, 3.2, 30)
S.curve(lambda t: sph(rb, t, pb), ta, tb, PRACTICE, 3.2, 30)
# the horizontal radius r = rho sin phi of the circle that carries the theta-edge
zc = rb * math.cos(pb)
S.guide([(0, 0, zc), sph(rb, ta, pb)], TEXT, 0.55)
# angle phi (to the lower cone) and delta-phi in the half-plane theta = ta
mdir = (math.cos(ta), math.sin(ta), 0.0)
angle_arc3(S, O, K, mdir, 0.7, 0, pa, TEXT, 1.2)
angle_arc3(S, O, K, mdir, 1.05, pa, pb, BASE, 1.5)
S.label(sph(0.72, ta, pa / 2), P_, 4, -2, TEXT, 12.5, "start", True)
S.label(sph(1.05, ta, (pa + pb) / 2), DELTA + P_, -7, 6, BASE, 12, "end", True)
S.label((0.95 * math.cos((ta + tb) / 2), 0.95 * math.sin((ta + tb) / 2), 0), DELTA + T_, 0, 16, BASE, 12,
        "middle", True)
S.label(sph((ra + rb) / 2, ta, pb), DELTA + R_, -2, 18, PRACTICE, 12.5, "middle", True)
splabel(S, sph(rb, ta, (pa + pb) / 2), R_ + " " + DELTA + P_, -12, 2, BASE, 12.5, "end", True)
S.label(sph(rb, (ta + tb) / 2, pb), R_ + " sin " + P_ + " " + DELTA + T_, 16, 16, PRACTICE, 12.5, "start", True)
S.label((0, 0, zc), it("r") + " = " + R_ + " sin " + P_, -8, -6, TEXT, 11.5, "end")
S.label(O, it("O"), -8, 12, TEXT, 12.5, "end")
save("kama", figure(
    int(pl.x0 + pl.w + 60), int(pl.y0 + pl.h + 30), [pl],
    "İnce bir küresel kama yaklaşık bir kutudur. Kenarları: <em>&#961;</em> yönünde &#916;<em>&#961;</em>; "
    "<em>&#961;</em> yarıçaplı çemberin &#916;<em>&#966;</em> açılık yayı <em>&#961;</em> &#916;<em>&#966;</em>; "
    "<em>z</em> eksenine uzaklığı <em>r</em> = <em>&#961;</em> sin <em>&#966;</em> olan yatay çemberin "
    "&#916;<em>&#952;</em> açılık yayı <em>&#961;</em> sin <em>&#966;</em> &#916;<em>&#952;</em>. Bu yüzden "
    "hacmi yaklaşık <em>&#961;</em>² sin <em>&#966;</em> &#916;<em>&#961;</em> &#916;<em>&#952;</em> "
    "&#916;<em>&#966;</em>'dir.",
    aria="A spherical wedge between two spheres, two half-planes and two half-cones, with dashed rays to the "
         "origin; its radial edge delta rho, its meridian edge rho delta phi and its horizontal edge "
         "rho sin phi delta theta are highlighted"))


# ============================================================
# dondurma: the solid above the cone z = sqrt(x^2 + y^2) and below the sphere x^2 + y^2 + z^2 = z
# ============================================================
C4 = (0.0, 0.0, 0.5)
R4 = 0.5
EL4 = 18.0
cam4 = Camera(azimuth=35.0, elevation=EL4)
SIL = math.acos(math.tan(EL4 * D2R))     # cone generators on the silhouette: cos(v - az) = tan(el)
GEN_L = 35 * D2R + SIL                     # the left silhouette generator
BOX4 = [O, (0.85, 0, 0), (0, 0.9, 0), (0, 0, 1.25), (0.5, 0.5, 0.5), (-0.5, -0.5, 0.5), (0.0, -0.75, 0.5)]


def ice_cream(S, shade=True, dashed_sphere=True, width=1.6, color=THEORY):
    """Outline (and optionally shading) of the solid rho <= cos(phi), phi <= pi/4."""
    X4, Y4 = S.pt(C4)
    if dashed_sphere:
        S.p.add(f'<circle cx="{S.p.X(X4):.1f}" cy="{S.p.Y(Y4):.1f}" r="{S.p.R(R4):.1f}" fill="none" '
                f'stroke="{TEXT}" stroke-width="1.0" stroke-dasharray="4 3" stroke-opacity="0.45"/>')
    if shade:
        S.surface(lambda s, v: (s * math.cos(v), s * math.sin(v), s), (0, 0.5), (0, 2 * math.pi), nu=3, nv=16,
                  fill=color, stroke=color, opacity=(0.05, 0.20), stroke_width=0.35, stroke_opacity=0.25)
        S.surface(lambda a, v: (R4 * math.sin(a) * math.cos(v), R4 * math.sin(a) * math.sin(v),
                                0.5 + R4 * math.cos(a)),
                  (0, math.pi / 2), (0, 2 * math.pi), nu=5, nv=16, fill=color, stroke=color,
                  opacity=(0.05, 0.20), stroke_width=0.35, stroke_opacity=0.25)
    # the cap silhouette is the upper half of the sphere's screen circle
    S.p.line([(X4 + R4 * math.cos(math.pi * k / 60), Y4 + R4 * math.sin(math.pi * k / 60)) for k in range(61)],
             color, width)
    vis_curve(S, lambda t: (0.5 * math.cos(t), 0.5 * math.sin(t), 0.5), 0, 2 * math.pi,
              lambda t: (math.cos(t), math.sin(t), 0.0), color, width - 0.1, 120, 0.5)
    for v in (35 * D2R + SIL, 35 * D2R - SIL):
        S.line([O, (0.5 * math.cos(v), 0.5 * math.sin(v), 0.5)], color, width)


pl, S = fit_space(cam4, BOX4, 40, 30, 300, 0.12)
S.axes(0.85, 0.9, 1.25, offsets=((-4, 13), (10, 4), (-10, -4)))
ice_cream(S)
S.guide([O, (0, 0, 1.0)], TEXT, 0.5)
g4 = (math.cos(GEN_L), math.sin(GEN_L), 0.0)
angle_arc3(S, O, K, g4, 0.2, 0, math.pi / 4, PRACTICE, 1.4)
S.label(vadd(vscale(0.25 * math.cos(math.pi / 8), K), vscale(0.25 * math.sin(math.pi / 8), g4)), PI + "/4",
        -4, 4, PRACTICE, 12, "end", True)
S.point((0, 0, 1.0), PRACTICE, 3.6)
S.label((0, 0, 1.0), "(0, 0, 1)", 8, -7, PRACTICE, 11.5)
S.label(O, it("O"), -8, 12, TEXT, 12, "end")
# leader lines from the two equations to their surfaces
XC, YC = S.pt(C4)
SP = (R4 * math.sin(0.9) * math.cos(110 * D2R), R4 * math.sin(0.9) * math.sin(110 * D2R), 0.5 + R4 * math.cos(0.9))
# the labels stay inside the span of the axis tips so that the canvas does not grow
XT, YT = S.pt((0.85, 0, 0))[0], S.pt((0, 0.9, 0))[0]
X, Y = S.pt(SP)
S.p.line([(X, Y), (YT - 0.29, YC + 0.42)], TEXT, 0.9, None, 0.7)
S.p.label(YT, YC + 0.42, it("x") + "² + " + it("y") + "² + " + it("z") + "² = " + it("z"), 0, 4, THEORY, 12, "end")
GEN_R = 35 * D2R - SIL
CP = (0.25 * math.cos(GEN_R), 0.25 * math.sin(GEN_R), 0.25)
X, Y = S.pt(CP)
S.p.line([(X, Y), (XT + 0.31, Y - 0.06)], TEXT, 0.9, None, 0.7)
S.p.label(XT, Y - 0.06, it("z") + " = &#8730;(" + it("x") + "² + " + it("y") + "²)", 0, 4, THEORY, 12)
S.label((0.0, 0.0, 0.62), it("E"), 10, 4, THEORY, 14, "start", True)
save("dondurma", figure(
    int(pl.x0 + pl.w + 60), int(pl.y0 + pl.h + 30), [pl],
    "<em>z</em> = &#8730;(<em>x</em>² + <em>y</em>²) konisinin üstünde ve <em>x</em>² + <em>y</em>² + "
    "<em>z</em>² = <em>z</em> küresinin altında kalan <em>E</em> cismi. Küre orijinden geçer, merkezi "
    "(0, 0, 1/2), yarıçapı 1/2'dir; kesikli çizgi kürenin cisme girmeyen alt kısmıdır. Koni ile <em>z</em> "
    "ekseni arasındaki açı <em>&#960;</em>/4'tür.",
    aria="Ice-cream-cone shaped solid: the cone z = sqrt(x^2 + y^2) up to height 1/2 capped by the upper half "
         "of the sphere x^2 + y^2 + z^2 = z of radius 1/2 centred at (0, 0, 1/2); the lower half of the sphere "
         "is dashed and the half-angle of the cone is pi/4"))

# ============================================================
# tarama: how the iterated integral d rho d phi d theta sweeps out the solid
# ============================================================
TH5 = 125 * D2R            # the half-plane seen face-on by the camera
e5 = (math.cos(TH5), math.sin(TH5), 0.0)
PH5 = 22 * D2R
panels = []
# each panel is as wide as its own drawing (the third one also holds the turning arrow)
CAP4 = [(R4 * math.sin(a) * math.cos(v), R4 * math.sin(a) * math.sin(v), 0.5 + R4 * math.cos(a))
        for a in (k * math.pi / 8 for k in range(9)) for v in (j * math.pi / 12 for j in range(24))]
AX4 = [O, (0.75, 0, 0), (0, 0.78, 0), (0, 0, 1.25)]
TURN4 = [(0.62 * math.cos(v), 0.62 * math.sin(v), 0.95) for v in (j * math.pi / 18 for j in range(36))]
rows = fit_row(cam4, [AX4 + CAP4, AX4 + CAP4, AX4 + CAP4 + TURN4], 20, 44, 205, 0.1, 18)
for k, (pl, S) in enumerate(rows):
    S.axes(0.75, 0.78, 1.25, size=14, offsets=((-5, 15), (12, 5), (-11, -4)))
    ice_cream(S, shade=(k == 2), dashed_sphere=False, width=1.2, color=THEORY)
    if k == 0:
        end = vadd(vscale(math.cos(PH5) * math.sin(PH5), e5), vscale(math.cos(PH5) ** 2, K))
        S.arrow(O, end, PRACTICE, 2.4, 9.0)
        S.point(end, PRACTICE, 3.2)
        angle_arc3(S, O, K, e5, 0.22, 0, PH5, TEXT, 1.1)
        S.label(vadd(vscale(0.3 * math.cos(PH5 / 2), K), vscale(0.3 * math.sin(PH5 / 2), e5)), P_, 0, 3, TEXT,
                15, "middle", True)
        S.label(end, R_ + " = cos " + P_, 7, -5, PRACTICE, 15)
        panel_title(pl, "önce " + R_ + ": 0 → cos " + P_, TEXT, 16)
    elif k == 1:
        sl = [O] + [vadd(vscale(math.cos(t) * math.sin(t), e5), vscale(math.cos(t) ** 2, K))
                    for t in (math.pi / 4 * j / 40 for j in range(41))]
        S.polygon(sl, PRACTICE, 0.22, PRACTICE, 1.4)
        for t in (PH5, 2 * PH5 * 0.85):
            end = vadd(vscale(math.cos(t) * math.sin(t), e5), vscale(math.cos(t) ** 2, K))
            S.line([O, end], PRACTICE, 1.0, None, 0.7)
        # sweep arrow for phi
        S.segment_arrow(lambda t: vadd(vscale(0.62 * math.sin(t) * math.cos(t) / math.cos(t), e5),
                                       vscale(0.62 * math.cos(t), K)), 0.1, math.pi / 4 - 0.04, PRACTICE, 1.5,
                        7.0, 40)
        S.label(vadd(vscale(0.5 * math.cos(math.pi / 4), e5), vscale(0.5 * math.cos(math.pi / 4), K)),
                P_ + " = " + PI + "/4", 6, 17, PRACTICE, 15)
        panel_title(pl, "sonra " + P_ + ": 0 → " + PI + "/4", TEXT, 16)
    else:
        # the same slice, and the rotation about the z axis
        sl = [O] + [vadd(vscale(math.cos(t) * math.sin(t), e5), vscale(math.cos(t) ** 2, K))
                    for t in (math.pi / 4 * j / 40 for j in range(41))]
        S.polygon(sl, PRACTICE, 0.18, PRACTICE, 1.0)
        S.segment_arrow(lambda t: (0.62 * math.cos(t), 0.62 * math.sin(t), 0.95), 0.2 * math.pi, 1.75 * math.pi,
                        PRACTICE, 1.6, 8.0, 80)
        panel_title(pl, "en son " + T_ + ": 0 → 2" + PI, TEXT, 16)
    panels.append(pl)
save("tarama", figure(
    int(panels[-1].x0 + panels[-1].w + 20), int(max(q.y0 + q.h for q in panels) + 20), panels,
    "Ardışık integralin cismi taraması. Önce <em>&#966;</em> ve <em>&#952;</em> sabitken <em>&#961;</em>, "
    "0'dan küre üzerindeki cos <em>&#966;</em> değerine gider ve bir doğru parçası çizer. Sonra <em>&#952;</em> "
    "sabitken <em>&#966;</em>, 0'dan <em>&#960;</em>/4'e gider ve bu parçalar bir yarı düzlem dilimini doldurur. "
    "En son <em>&#952;</em>, 0'dan 2<em>&#960;</em>'ye gider ve dilim <em>z</em> ekseni etrafında dönerek cismin "
    "tamamını tarar.",
    css_class=WIDE,
    aria="Three panels: a segment from the origin to the sphere along a ray with fixed phi and theta; the planar "
         "slice 0 le phi le pi/4 in a half-plane theta = const; the slice rotated about the z axis to fill the "
         "whole solid"))

# ============================================================
# top-silindir: the solid rho le 2, rho le csc(phi) = ball of radius 2 inside the cylinder r le 1
# ============================================================
R6, Z6 = 2.0, math.sqrt(3.0)
EL6 = 18.0
cam6 = Camera(azimuth=35.0, elevation=EL6)
pl, S = fit_space(cam6, [(0, 0, 2.5), (0, 0, -2.2), (2.4, 0, 0), (0, 2.6, 0), (-2, -2, 0), (2, 2, 0),
                         (2, -2, 0), (-2, 2, 0)], 40, 30, 95, 0.15)
X6, Y6 = S.pt(O)
# the ball of radius 2: dashed silhouette and equator
S.p.add(f'<circle cx="{S.p.X(X6):.1f}" cy="{S.p.Y(Y6):.1f}" r="{S.p.R(R6):.1f}" fill="none" stroke="{TEXT}" '
        f'stroke-width="1.0" stroke-dasharray="4 3" stroke-opacity="0.45"/>')
vis_curve(S, lambda t: (R6 * math.cos(t), R6 * math.sin(t), 0.0), 0, 2 * math.pi,
          lambda t: (math.cos(t), math.sin(t), 0.0), TEXT, 1.0, 120, 0.3, "4 3", 0.45)
S.axes(2.4, 2.6, 2.6, zmin=-2.3, offsets=((-4, 13), (10, 4), (-10, -4)))
# the solid: cylinder wall and the two spherical caps
S.surface(lambda z, v: (math.cos(v), math.sin(v), z), (-Z6, Z6), (0, 2 * math.pi), nu=4, nv=20, fill=THEORY,
          stroke=THEORY, opacity=(0.05, 0.18), stroke_width=0.3, stroke_opacity=0.25)
for lo, hi in ((0.0, math.pi / 6), (5 * math.pi / 6, math.pi)):
    S.surface(lambda a, v: sph(R6, v, a), (lo, hi), (0, 2 * math.pi), nu=3, nv=20, fill=THEORY, stroke=THEORY,
              opacity=(0.05, 0.18), stroke_width=0.3, stroke_opacity=0.25)
for zz in (Z6, -Z6):
    vis_curve(S, lambda t, zz=zz: (math.cos(t), math.sin(t), zz), 0, 2 * math.pi,
              lambda t: (math.cos(t), math.sin(t), 0.0), THEORY, 1.6, 120, 0.5)
for v in (35 * D2R + math.pi / 2, 35 * D2R - math.pi / 2):
    S.line([(math.cos(v), math.sin(v), -Z6), (math.cos(v), math.sin(v), Z6)], THEORY, 1.6)
# apparent outline of the caps: the arcs of the sphere's contour circle with |z| >= sqrt(3)
u6, r6 = cam6.u, cam6.r
for sgn, t0 in ((1, -math.pi), (-1, 0.0)):
    pts = []
    for k in range(721):
        t = t0 + 2 * math.pi * k / 720
        P = vadd(vscale(R6 * math.cos(t), u6), vscale(R6 * math.sin(t), r6))
        if sgn * P[2] >= Z6:
            pts.append((t, P))
    if pts:
        S.line([P for _, P in pts], THEORY, 1.6)
# the angle pi/6 between the z axis and the top rim, seen in the face-on half-plane
e6 = (math.cos(125 * D2R), math.sin(125 * D2R), 0.0)
rim6 = vadd(e6, (0, 0, Z6))
S.guide([O, rim6], PRACTICE, 0.8, 1.1)
angle_arc3(S, O, K, e6, 0.8, 0, math.pi / 6, PRACTICE, 1.4)
S.label(vadd(vscale(0.95 * math.cos(math.pi / 12), K), vscale(0.95 * math.sin(math.pi / 12), e6)), PI + "/6",
        -2, 6, PRACTICE, 11.5, "end", True)
S.label((0, 0, 2.0), R_ + " = 2", 10, -10, THEORY, 12, "start", True)
side = (math.cos(35 * D2R + math.pi / 2), math.sin(35 * D2R + math.pi / 2), -0.9)
S.label(side, R_ + " sin " + P_ + " = 1", 10, 4, THEORY, 12, "start", True)
S.label(vadd((math.cos(35 * D2R - math.pi / 2), math.sin(35 * D2R - math.pi / 2), 0), (0, 0, Z6)),
        it("z") + " = &#8730;3", -10, 4, TEXT, 11.5, "end")
S.label(vadd((math.cos(35 * D2R - math.pi / 2), math.sin(35 * D2R - math.pi / 2), 0), (0, 0, -Z6)),
        it("z") + " = " + MINUS + "&#8730;3", -10, 4, TEXT, 11.5, "end")
save("top-silindir", figure(
    int(pl.x0 + pl.w + 80), int(pl.y0 + pl.h + 30), [pl],
    "<em>&#961;</em> &#8804; 2, <em>&#961;</em> &#8804; csc <em>&#966;</em> cismi: 2 yarıçaplı topun "
    "(kesikli) <em>x</em>² + <em>y</em>² &#8804; 1 silindiri içinde kalan kısmı. Yan yüzey "
    "<em>&#961;</em> sin <em>&#966;</em> = 1 silindiri, alt ve üst kapaklar <em>&#961;</em> = 2 küresinin "
    "parçalarıdır; ikisi <em>z</em> = &#177;&#8730;3 çemberlerinde, yani <em>&#966;</em> = <em>&#960;</em>/6 "
    "ve <em>&#966;</em> = 5<em>&#960;</em>/6'da birleşir.",
    aria="Solid cylinder of radius 1 about the z axis between z = -sqrt(3) and z = sqrt(3), capped above and "
         "below by pieces of the sphere of radius 2, drawn dashed; the top rim makes the angle pi/6 with the "
         "z axis"))
