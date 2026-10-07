# -*- coding: utf-8 -*-
"""
Figures of the chapter "Silindirik Koordinatlarda Üç Katlı İntegraller"
(dersler/integral-calculus/silindirik-koordinatlarda-uc-katli-integraller.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box and never directly under a heading.
Concept figures stay visible: under a definition box, in the statement part
of a theorem, or in the plain text next to the paragraph they illustrate.
The figures are NOT produced at build time. Run

    python scripts/calculus_figures/sil.py
    python scripts/center_figures.py "calculus-sil-*.md"
    python scripts/check_figure_labels.py "scripts/_figures/calculus-sil-*.md"

and paste the markup of scripts/_figures/calculus-sil-<name>.md into the .qmd.
Captions are Turkish on purpose; aria labels are plain ASCII.
"""
import html
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, panel_title, TEXT, THEORY, PRACTICE, BASE, REMARK, BG, WIDE  # noqa: E402
from svg_plot3 import Camera, Space  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "calculus-sil-"

MINUS = "&#8722;"
ZWSP = chr(0x200B)
DEG = math.pi / 180.0


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


def splabel(S, P, s, dx=0, dy=0, color=TEXT, size=11.5, anchor="start", bold=False):
    """Label at a space point on a page-coloured plate (for text over a meshed surface)."""
    p = S.p
    X, Y = S.pt(P)
    px, py = p.X(X) + dx, p.Y(Y) + dy
    w = text_w(s, size)
    x0 = px - (w / 2 if anchor == "middle" else w if anchor == "end" else 0)
    p.add(f'<rect x="{x0 - 2.5:.1f}" y="{py - 0.8 * size - 1:.1f}" width="{w + 5:.1f}" '
          f'height="{size + 3:.1f}" rx="3" fill="{BG}" opacity="0.85"/>')
    p.label(X, Y, s, dx, dy, color, size, anchor, bold)


def cyl(r, t, z):
    """Cylindrical -> rectangular."""
    return (r * math.cos(t), r * math.sin(t), z)


def floor_arc(S, r, t0, t1, z=0.0, color=TEXT, width=1.4, dash=None, opacity=1.0, head=None):
    """Arc of the circle of radius r about the z axis at height z, optionally with an arrowhead."""
    f = (lambda t: cyl(r, t, z))
    if head:
        S.segment_arrow(f, t0, t1, color, width, head, 80)
    else:
        S.curve(f, t0, t1, color, width, 80, dash, opacity)


R_EQ = it("r")
TH = it("&#952;")
SQRT_XY = "&#8730;(" + it("x") + sup("2") + " + " + it("y") + sup("2") + ")"

# ============================================================
# koordinatlar: the cylindrical coordinates (r, theta, z) of a point
# ============================================================
cam = Camera(azimuth=35.0, elevation=22.0)
R0, T0, Z0 = 2.6, 50 * DEG, 2.2
Pf = cyl(R0, T0, 0.0)
P = cyl(R0, T0, Z0)
pl, S = fit_space(cam, [(0, 0, 0), (3.1, 0, 0), (0, 3.5, 0), (0, 0, 3.2), Pf, P, cyl(R0, -0.35, 0),
                        cyl(R0, 1.95, Z0)], 40, 30, 92, 0.35)
S.axes(3.1, 3.5, 3.2)
# traces of the cylinder r = r0 through P
floor_arc(S, R0, -0.35, 1.95, 0.0, TEXT, 1.0, "4 3", 0.45)
floor_arc(S, R0, -0.35, 1.95, Z0, TEXT, 1.0, "4 3", 0.45)
S.guide([P, (0, 0, Z0)], TEXT, 0.55)
S.point((0, 0, Z0), TEXT, 2.6)
S.line([(0, 0, 0), Pf], PRACTICE, 2.8)
S.line([Pf, P], THEORY, 2.8)
floor_arc(S, 0.85, 0.0, T0, 0.0, REMARK, 1.8, head=7.0)
S.point(Pf, TEXT, 4.0)
S.point(P, THEORY, 4.8)
S.label((0, 0, 0), it("O"), -12, 2, TEXT, 12.5, "end")
S.label(cyl(1.05, T0 / 2, 0), TH, 0, 14, REMARK, 14, "middle", True)
S.label(cyl(R0 * 0.55, T0, 0), R_EQ, -10, 6, PRACTICE, 15, "end", True)
S.label(cyl(R0, T0, Z0 / 2), it("z"), 10, 5, THEORY, 15, "start", True)
S.label(P, it("P") + "(" + it("r") + ", " + TH + ", " + it("z") + ")", 8, -10, THEORY, 13, "start", True)
S.label(Pf, "(" + it("r") + ", " + TH + ", 0)", 10, 16, TEXT, 12.5)
S.label(cyl(R0 / 2, T0, Z0), it("r"), 0, -7, TEXT, 12, "middle")
save("koordinatlar", figure(
    int(pl.x0 + pl.w + 40), int(pl.y0 + pl.h + 30), [pl],
    "<em>P</em> noktasının silindirik koordinatları: (<em>r</em>, <em>&#952;</em>), <em>P</em>'nin "
    "<em>xy</em>-düzlemindeki izdüşümünün kutupsal koordinatları, <em>z</em> ise <em>P</em>'nin yüksekliğidir. "
    "<em>r</em> aynı zamanda <em>P</em>'nin <em>z</em> eksenine uzaklığıdır; kesikli yaylar <em>P</em>'den geçen "
    "<em>r</em> = sabit silindirinin izleridir.",
    aria="Point P above the xy plane with its projection (r, theta, 0), the segment of length r from the "
         "origin to the projection, the angle theta from the positive x axis, the vertical segment of length z "
         "and dashed arcs of the cylinder through P"))

# ============================================================
# yuzeyler: coordinate surfaces r = c, theta = c, z = c
# ============================================================
ZT = 2.2
AX_OFF = ((-5, 15), (12, 5), (-11, -4))   # axis-label offsets for the larger labels of the rows
AXES = [(0, 0, 0), (2.2, 0, 0), (0, 2.3, 0), (0, 0, 2.9)]
CYL_C, HP_C, HP_L, PL_C, PL_H = 1.2, 100 * DEG, 1.9, 1.4, 1.45
# each panel is as wide as its own drawing; the three share one vertical range
rows = fit_row(Camera(azimuth=35.0, elevation=22.0), [
    AXES + [cyl(CYL_C, 2 * math.pi * j / 24, z) for j in range(24) for z in (0.0, ZT)],
    AXES + [cyl(HP_L, HP_C, 0), cyl(HP_L, HP_C, ZT), (0, 0, ZT)],
    AXES + [(sx * PL_H, sy * PL_H, PL_C) for sx in (-1, 1) for sy in (-1, 1)],
], 20, 44, 62, 0.22, 22)
panels = []
for k, (pl, S) in enumerate(rows):
    panels.append(pl)
    if k == 0:
        c = CYL_C
        S.axes(2.2, 2.3, 2.9, size=14, offsets=AX_OFF)
        S.surface(lambda u, v: cyl(c, u, v), (0, 2 * math.pi), (0, ZT), nu=28, nv=3, fill=THEORY,
                  stroke=THEORY, opacity=(0.05, 0.22), stroke_width=0.4, stroke_opacity=0.35)
        floor_arc(S, c, 0, 2 * math.pi, 0.0, THEORY, 1.6)
        floor_arc(S, c, 0, 2 * math.pi, ZT, THEORY, 1.6)
        S.line([(0, 0, ZT), cyl(c, 80 * DEG, ZT)], PRACTICE, 2.0)
        S.label(cyl(c / 2, 80 * DEG, ZT), it("c"), -2, -7, PRACTICE, 15.5, "middle", True)
        panel_title(pl, it("r") + " = " + it("c") + ": silindir", TEXT, 16)
    elif k == 1:
        c = HP_C
        S.axes(2.2, 2.3, 2.9, size=14, offsets=AX_OFF)
        quad = [(0, 0, 0), cyl(HP_L, c, 0), cyl(HP_L, c, ZT), (0, 0, ZT)]
        S.polygon(quad, THEORY, 0.20, THEORY, 1.4)
        S.line([(0, 0, 0), cyl(HP_L, c, 0)], THEORY, 2.0)
        floor_arc(S, 0.55, 0.0, c, 0.0, REMARK, 1.7, head=6.5)
        S.label(cyl(0.72, c / 2, 0), it("c"), 0, 16, REMARK, 15.5, "middle", True)
        panel_title(pl, TH + " = " + it("c") + ": yarım düzlem", TEXT, 16)
    else:
        c = PL_C
        S.axes(2.2, 2.3, 2.9, size=14, offsets=AX_OFF)
        H = PL_H
        S.polygon([(-H, -H, c), (H, -H, c), (H, H, c), (-H, H, c)], THEORY, 0.20, THEORY, 1.4)
        S.point((0, 0, c), PRACTICE, 3.8)
        S.label((0, 0, c), it("c"), -9, -6, PRACTICE, 15.5, "end", True)
        panel_title(pl, it("z") + " = " + it("c") + ": yatay düzlem", TEXT, 16)
save("yuzeyler", figure(
    int(panels[-1].x0 + panels[-1].w + 20), int(max(p.y0 + p.h for p in panels) + 20), panels,
    "Silindirik koordinatlarda bir koordinatı sabitlemek: <em>r</em> = <em>c</em> ekseni <em>z</em> ekseni olan "
    "dairesel bir silindir, <em>&#952;</em> = <em>c</em> kenarı <em>z</em> ekseni olan düşey bir yarım düzlem, "
    "<em>z</em> = <em>c</em> yatay bir düzlemdir. Her yüzeyin yalnız bir parçası çizilmiştir.",
    css_class=WIDE,
    aria="Three panels: a circular cylinder r = c about the z axis, a vertical half plane theta = c bounded by "
         "the z axis, and a horizontal plane z = c"))

# ============================================================
# bolge: a type 1 solid over a region D given in polar coordinates
# ============================================================
AL, BE = 20 * DEG, 70 * DEG


def h1(t):
    s = (t - AL) / (BE - AL)
    return 1.1 + 0.25 * math.sin(math.pi * s)


def h2(t):
    s = (t - AL) / (BE - AL)
    return 2.7 - 0.2 * math.sin(math.pi * s)


def u1(x, y):
    return 0.8 + 0.12 * x + 0.08 * y


def u2(x, y):
    return 3.6 - 0.11 * (x * x + y * y)


def dpt(u, t):
    """Point of D: u in [0, 1] runs from r = h1 to r = h2."""
    r = h1(t) + u * (h2(t) - h1(t))
    return cyl(r, t, 0.0)


def lift(Q, g):
    return (Q[0], Q[1], g(Q[0], Q[1]))


cam = Camera(azimuth=35.0, elevation=22.0)
pl, S = fit_space(cam, [(0, 0, 0), (3.3, 0, 0), (0, 3.4, 0), (0, 0, 4.4), lift(dpt(1, BE), u2),
                        lift(dpt(1, AL), u2), dpt(1, AL), dpt(1, BE)], 40, 30, 88, 0.45)
S.axes(3.3, 3.4, 4.4)
# floor: the region D and its boundary
Dpts = ([dpt(0, AL + (BE - AL) * k / 40) for k in range(41)]
        + [dpt(1, BE - (BE - AL) * k / 40) for k in range(41)])
S.polygon(Dpts, BASE, 0.22)
S.line([(0, 0, 0), dpt(1, AL)], TEXT, 1.0, "4 3", 0.55)
S.line([(0, 0, 0), dpt(1, BE)], TEXT, 1.0, "4 3", 0.55)
S.curve(lambda t: dpt(0, t), AL, BE, BASE, 2.0)
S.curve(lambda t: dpt(1, t), AL, BE, BASE, 2.0)
S.line([dpt(0, AL), dpt(1, AL)], BASE, 2.0)
S.line([dpt(0, BE), dpt(1, BE)], BASE, 2.0)
# vertical edges of the solid
for u, t in ((0, AL), (1, AL), (0, BE), (1, BE)):
    Q = dpt(u, t)
    S.guide([Q, lift(Q, u1)], TEXT, 0.45)
    S.line([lift(Q, u1), lift(Q, u2)], THEORY, 1.0, None, 0.6)
# the outer wall r = h2 (front) is shaded lightly
S.surface(lambda t, z: (dpt(1, t)[0], dpt(1, t)[1], u1(*dpt(1, t)[:2]) + z * (u2(*dpt(1, t)[:2]) - u1(*dpt(1, t)[:2]))),
          (AL, BE), (0, 1), nu=12, nv=1, fill=THEORY, stroke="none", opacity=(0.04, 0.10))
# bottom and top surfaces
S.surface(lambda u, t: lift(dpt(u, t), u1), (0, 1), (AL, BE), nu=5, nv=10, fill=THEORY, stroke=THEORY,
          opacity=(0.08, 0.20), stroke_width=0.4, stroke_opacity=0.35)
S.surface(lambda u, t: lift(dpt(u, t), u2), (0, 1), (AL, BE), nu=5, nv=10, fill=THEORY, stroke=THEORY,
          opacity=(0.10, 0.30), stroke_width=0.4, stroke_opacity=0.35)
for g in (u1, u2):
    S.curve(lambda t, g=g: lift(dpt(0, t), g), AL, BE, THEORY, 1.6)
    S.curve(lambda t, g=g: lift(dpt(1, t), g), AL, BE, THEORY, 1.6)
    S.curve(lambda u, g=g: lift(dpt(u, AL), g), 0, 1, THEORY, 1.6)
    S.curve(lambda u, g=g: lift(dpt(u, BE), g), 0, 1, THEORY, 1.6)
TM = (AL + BE) / 2
S.label(dpt(0.5, TM), it("D"), 0, 5, BASE, 15, "middle", True)
S.label(dpt(1, AL), TH + " = " + it("&#945;"), -6, 16, TEXT, 12.5, "end")
S.label(dpt(1, BE), TH + " = " + it("&#946;"), 10, 6, TEXT, 12.5)
S.label(dpt(1, 0.62 * AL + 0.38 * BE), it("r") + " = " + it("h") + sub("2") + "(" + TH + ")", 10, 16, BASE, 12.5)
S.label(dpt(0, AL + 0.02), it("r") + " = " + it("h") + sub("1") + "(" + TH + ")", -16, -2, BASE, 12.5, "end")
splabel(S, lift(dpt(1, BE), u2), it("z") + " = " + it("u") + sub("2") + "(" + it("x") + ", " + it("y") + ")",
        12, -2, THEORY, 12.5)
splabel(S, lift(dpt(0, AL), u1), it("z") + " = " + it("u") + sub("1") + "(" + it("x") + ", " + it("y") + ")",
        -10, -4, THEORY, 12.5, "end")
S.label(lift(dpt(0.5, TM), lambda x, y: 0.5 * (u1(x, y) + u2(x, y))), it("E"), 0, 5, THEORY, 15, "middle", True)
save("bolge", figure(
    int(pl.x0 + pl.w + 40), int(pl.y0 + pl.h + 30), [pl],
    "<em>E</em> cismi, <em>xy</em>-düzlemindeki izdüşümü <em>D</em>'nin üstünde, <em>z</em> = "
    "<em>u</em><sub>1</sub>(<em>x</em>, <em>y</em>) ile <em>z</em> = <em>u</em><sub>2</sub>(<em>x</em>, <em>y</em>) "
    "yüzeyleri arasında kalır. <em>D</em> kutupsal koordinatlarda &#945; &#8804; <em>&#952;</em> &#8804; &#946;, "
    "<em>h</em><sub>1</sub>(<em>&#952;</em>) &#8804; <em>r</em> &#8804; <em>h</em><sub>2</sub>(<em>&#952;</em>) "
    "ile verilir.",
    aria="A solid E between a lower surface z = u1(x, y) and an upper surface z = u2(x, y) above a region D "
         "of the xy plane bounded by the rays theta = alpha, theta = beta and the curves r = h1(theta), "
         "r = h2(theta)"))

# ============================================================
# hacim-elemani: the cylindrical box with edges dr, r dtheta, dz
# ============================================================
RA, DR = 2.1, 0.8
TA, DT = 22 * DEG, 30 * DEG
ZA, DZ = 1.3, 1.0
RB, TB, ZB = RA + DR, TA + DT, ZA + DZ
cam = Camera(azimuth=35.0, elevation=22.0)
pl, S = fit_space(cam, [(0, 0, 0), (3.3, 0, 0), (0, 3.4, 0), (0, 0, 2.9), cyl(RB, TA, 0), cyl(RB, TB, ZB),
                        cyl(RB, TA, ZB)], 40, 30, 100, 0.4)
S.axes(3.3, 3.4, 2.9)
# floor: the polar rectangle under the box and the two rays
S.line([(0, 0, 0), cyl(RB, TA, 0)], TEXT, 1.0, "4 3", 0.55)
S.line([(0, 0, 0), cyl(RB, TB, 0)], TEXT, 1.0, "4 3", 0.55)
floor_poly = ([cyl(RA, TA + DT * k / 20, 0) for k in range(21)]
              + [cyl(RB, TB - DT * k / 20, 0) for k in range(21)])
S.polygon(floor_poly, BASE, 0.20, BASE, 1.2)
floor_arc(S, 0.75, TA, TB, 0.0, REMARK, 1.6)
S.label(cyl(0.95, TA + DT / 2, 0), "&#916;" + TH, 6, 14, REMARK, 13, "middle", True)
for r, t in ((RA, TA), (RB, TA), (RA, TB), (RB, TB)):
    S.guide([cyl(r, t, 0), cyl(r, t, ZA)], TEXT, 0.45)
# the box: back faces first, then the visible ones
S.surface(lambda t, z: cyl(RA, t, z), (TA, TB), (ZA, ZB), nu=8, nv=1, fill=THEORY, stroke="none",
          opacity=(0.06, 0.12))
for t in (TA, TB):
    S.polygon([cyl(RA, t, ZA), cyl(RB, t, ZA), cyl(RB, t, ZB), cyl(RA, t, ZB)], THEORY, 0.10)
S.polygon([cyl(RA, TA + DT * k / 20, ZA) for k in range(21)] + [cyl(RB, TB - DT * k / 20, ZA) for k in range(21)],
          THEORY, 0.08)
S.surface(lambda t, z: cyl(RB, t, z), (TA, TB), (ZA, ZB), nu=8, nv=1, fill=THEORY, stroke="none",
          opacity=(0.14, 0.26))
S.polygon([cyl(RA, TA + DT * k / 20, ZB) for k in range(21)] + [cyl(RB, TB - DT * k / 20, ZB) for k in range(21)],
          THEORY, 0.30)
for z in (ZA, ZB):
    for r in (RA, RB):
        floor_arc(S, r, TA, TB, z, THEORY, 1.5)
    for t in (TA, TB):
        S.line([cyl(RA, t, z), cyl(RB, t, z)], THEORY, 1.5)
for r, t in ((RA, TA), (RB, TA), (RA, TB), (RB, TB)):
    S.line([cyl(r, t, ZA), cyl(r, t, ZB)], THEORY, 1.5)
# highlighted edges
S.line([cyl(RA, TB, ZB), cyl(RB, TB, ZB)], PRACTICE, 2.6)
floor_arc(S, RB, TA, TB, ZB, PRACTICE, 2.6)
S.line([cyl(RB, TA, ZA), cyl(RB, TA, ZB)], PRACTICE, 2.6)
S.label(cyl(RA + DR / 2, TB, ZB), "&#916;" + it("r"), 8, -6, PRACTICE, 13.5, "start", True)
S.label(cyl(RB, TA + DT / 2, ZB), it("r") + "&#8201;&#916;" + TH, 0, -10, PRACTICE, 13.5, "middle", True)
S.label(cyl(RB, TA, ZA + DZ / 2), "&#916;" + it("z"), -10, 5, PRACTICE, 13.5, "end", True)
S.label(cyl(RB, TA + DT / 2, 0), "&#916;" + it("A"), 4, 18, BASE, 13, "middle", True)
save("hacim-elemani", figure(
    int(pl.x0 + pl.w + 40), int(pl.y0 + pl.h + 30), [pl],
    "Silindirik bir kutu: tabanı alanı &#916;<em>A</em> olan bir kutupsal dikdörtgen, yüksekliği &#916;<em>z</em>'dir. "
    "Kenarları yaklaşık &#916;<em>r</em>, <em>r</em>&#8201;&#916;<em>&#952;</em> ve &#916;<em>z</em> olduğundan "
    "hacmi yaklaşık <em>r</em>&#8201;&#916;<em>r</em>&#8201;&#916;<em>&#952;</em>&#8201;&#916;<em>z</em>'dir.",
    aria="A small cylindrical box between radii r and r + dr, angles theta and theta + dtheta and heights z and "
         "z + dz, with its edges dr, r dtheta and dz highlighted and its base, a polar rectangle, shaded on "
         "the xy plane"))

# ============================================================
# supurme: how the iterated integral of the paraboloid example sweeps the solid
# ============================================================


def para(r, t):
    return cyl(r, t, 4 - r * r)


TS = 0.8 * math.pi     # the fixed angle of panels 1 and 2 (the slice faces the viewer)
RS = 1.15              # the fixed radius of panel 1
BOX = ([(0, 0, 0), (2.9, 0, 0), (0, 2.9, 0), (0, 0, 4.9)]
       + [cyl(2.0, 2 * math.pi * j / 36, 0) for j in range(36)])
panels = []
titles = (it("z") + ": 0 &#8594; 4 " + MINUS + " " + it("r") + sup("2", 10.5),
          it("r") + ": 0 &#8594; 2",
          TH + ": 0 &#8594; 2&#960;")
# the third panel also holds the turning arrow of radius 2.3 on the floor
rows = fit_row(Camera(azimuth=35.0, elevation=22.0),
               [BOX, BOX, BOX + [cyl(2.3, 2 * math.pi * j / 36, 0) for j in range(36)]], 20, 48, 48, 0.3, 18)
for k, (pl, S) in enumerate(rows):
    panels.append(pl)
    S.axes(2.9, 2.9, 4.9, size=13.5, offsets=((-5, 15), (11, 5), (-11, -2)))
    floor_arc(S, 2.0, 0, 2 * math.pi, 0.0, TEXT, 1.0, "4 3", 0.5)
    S.surface(para, (0, 2), (0, 2 * math.pi), nu=5, nv=20, fill=THEORY, stroke=THEORY,
              opacity=(0.04, 0.16), stroke_width=0.4, stroke_opacity=0.3)
    floor_arc(S, 2.0, 0, 2 * math.pi, 0.0, THEORY, 1.2)
    if k == 0:
        Q = cyl(RS, TS, 0)
        S.point(Q, PRACTICE, 3.0)
        S.arrow(Q, para(RS, TS), PRACTICE, 2.4, 8.0)
        S.point(para(RS, TS), PRACTICE, 3.0)
    elif k == 1:
        sl = [(0, 0, 0), cyl(2, TS, 0)] + [para(2 - 2 * j / 30, TS) for j in range(31)]
        S.polygon(sl, PRACTICE, 0.30, PRACTICE, 1.4)
        for j in range(1, 5):
            r = 0.4 * j
            S.line([cyl(r, TS, 0), para(r, TS)], PRACTICE, 1.0, None, 0.6)
        S.arrow((0, 0, 0.0), cyl(2.0, TS, 0), PRACTICE, 2.4, 8.0)
    else:
        # the slice has turned from theta = 0 to theta = TS; the part swept so far is tinted
        S.surface(para, (0, 2), (0, TS), nu=5, nv=10, fill=PRACTICE, stroke="none", opacity=(0.10, 0.24))
        sl0 = [(0, 0, 0), cyl(2, 0.0, 0)] + [para(2 - 2 * j / 30, 0.0) for j in range(31)]
        S.polygon(sl0, PRACTICE, 0.10, PRACTICE, 1.0, "4 3")
        sl = [(0, 0, 0), cyl(2, TS, 0)] + [para(2 - 2 * j / 30, TS) for j in range(31)]
        S.polygon(sl, PRACTICE, 0.30, PRACTICE, 1.4)
        floor_arc(S, 2.3, 0.1, TS + 0.35, 0.0, PRACTICE, 2.2, head=8.0)
    panel_title(pl, titles[k], TEXT, 15.5)
save("supurme", figure(
    int(panels[-1].x0 + panels[-1].w + 20), int(max(p.y0 + p.h for p in panels) + 20), panels,
    "Ardışık integral cismi adım adım tarar. Solda <em>r</em> ve <em>&#952;</em> sabitken <em>z</em> tabandan "
    "paraboloide çıkar; ortada <em>&#952;</em> sabitken bu dik çizgiler <em>r</em> = 0'dan <em>r</em> = 2'ye "
    "kayarak düşey bir dilim oluşturur; sağda dilim <em>z</em> ekseni etrafında <em>&#952;</em> = 0'dan "
    "2&#960;'ye dönerek bütün cismi süpürür.",
    css_class=WIDE,
    aria="Three panels of the solid under the paraboloid z = 4 - r^2: a vertical segment for fixed r and theta, "
         "a vertical slice for fixed theta, and the slice rotating about the z axis"))

# ============================================================
# yarim-silindir: the solid of the mass example
# ============================================================
# a flatter, more side-on camera than the default makes the tall solid wider on the page;
# the three surface names sit in a column to the right of the solid, joined by leader lines
cam = Camera(azimuth=50.0, elevation=18.0)
pl, S = fit_space(cam, [(1.7, 0, 0), (-1.3, 0, 0), (0, 1.8, 0), (0, 0, 4.35), cyl(1, 0, 4), cyl(1, math.pi, 4),
                        cyl(1, math.pi / 2, 4)], 80, 30, 82, 0.5)
S.axes(1.7, 1.8, 4.35, -1.3, 0.0, 0.0, size=10.5, offsets=((-6, 12), (11, 5), (-10, -3)))
# flat back face in the xz plane: 1 - x^2 <= z <= 4
back = [(x / 20, 0, 4) for x in range(-20, 21)] + [(x / 20, 0, 1 - (x / 20) ** 2) for x in range(20, -21, -1)]
S.polygon(back, TEXT, 0.06, TEXT, 0.9)
# bottom: the paraboloid z = 1 - r^2 over the half disk
S.surface(lambda r, t: cyl(r, t, 1 - r * r), (0, 1), (0, math.pi), nu=5, nv=12, fill=BASE, stroke=BASE,
          opacity=(0.10, 0.28), stroke_width=0.4, stroke_opacity=0.4)
S.curve(lambda x: (x, 0, 1 - x * x), -1, 1, BASE, 1.8)
floor_arc(S, 1.0, 0, math.pi, 0.0, BASE, 1.8)
# curved wall r = 1 and the top half disk z = 4
S.surface(lambda t, z: cyl(1, t, z), (0, math.pi), (0, 4), nu=16, nv=4, fill=THEORY, stroke=THEORY,
          opacity=(0.06, 0.20), stroke_width=0.4, stroke_opacity=0.3)
S.polygon([cyl(1, math.pi * k / 40, 4) for k in range(41)], THEORY, 0.22, THEORY, 1.6)
S.line([cyl(1, 0, 0), cyl(1, 0, 4)], THEORY, 1.6)
S.line([cyl(1, math.pi, 0), cyl(1, math.pi, 4)], THEORY, 1.6)
S.guide([(0, 0, 1), (0, 0, 4)], TEXT, 0.6)
S.point((0, 0, 4), TEXT, 3.6)
S.point((0, 0, 1), BASE, 3.8)
S.point((1, 0, 0), TEXT, 3.6)
S.label((0, 0, 4), "(0, 0, 4)", -10, -6, TEXT, 10.5, "end")
splabel(S, (0, 0, 1), "(0, 0, 1)", -10, 4, BASE, 10.5, "end")
S.label((1, 0, 0), "(1, 0, 0)", -8, -9, TEXT, 10.5, "end")
# leader-line column: X just right of the wall's silhouette (the wall's widest point is X = 1)
XL = 1.0 + 0.45
for P, s_, col, size in ((cyl(0.75, 2.0, 4), it("z") + " = 4", THEORY, 11),
                         (cyl(1, 1.9, 2.4), it("r") + " = 1", THEORY, 11),
                         (cyl(0.75, 1.6, 1 - 0.75 ** 2), it("z") + " = 1 " + MINUS + " " + it("r") + sup("2", 8),
                          BASE, 11)):
    X, Y = S.pt(P)
    YL = Y + 0.18
    S.p.line([(X, Y), (XL, YL)], TEXT, 0.9, None, 0.7)
    S.p.add(f'<circle cx="{S.p.X(X):.1f}" cy="{S.p.Y(Y):.1f}" r="1.8" fill="{TEXT}" opacity="0.7"/>')
    S.p.label(XL, YL, s_, 4, 4, col, size, "start", True)
save("yarim-silindir", figure(
    int(pl.x0 + pl.w + 60), int(pl.y0 + pl.h + 30), [pl],
    "<em>x</em><sup>2</sup> + <em>y</em><sup>2</sup> = 1 silindirinin içinde, <em>y</em> &#8805; 0 tarafında, "
    "<em>z</em> = 1 &#8722; <em>x</em><sup>2</sup> &#8722; <em>y</em><sup>2</sup> paraboloidinin üstünde ve "
    "<em>z</em> = 4 düzleminin altında kalan cisim. Silindirik koordinatlarda 0 &#8804; <em>&#952;</em> &#8804; "
    "&#960;, 0 &#8804; <em>r</em> &#8804; 1, 1 &#8722; <em>r</em><sup>2</sup> &#8804; <em>z</em> &#8804; 4'tür.",
    aria="Half of a solid cylinder of radius 1 on the side y greater than or equal to 0, bounded below by the "
         "paraboloid z = 1 - r^2 and above by the plane z = 4"))

# ============================================================
# koni: the solid between the cone z = r and the plane z = 2
# ============================================================
cam = Camera(azimuth=35.0, elevation=22.0)
pl, S = fit_space(cam, [(2.9, 0, 0), (0, 3.0, 0), (0, 0, 3.0), cyl(2, 0.6, 2), cyl(2, 3.7, 2), cyl(2, 2.2, 0),
                        cyl(2, 5.3, 0)], 40, 30, 90, 0.4)
# floor disk D (the projection) and the hidden part of the axes
S.polygon([cyl(2, 2 * math.pi * k / 96, 0) for k in range(97)], BASE, 0.18, BASE, 1.4)
S.axes(2.9, 3.0, 3.0)
S.surface(lambda r, t: cyl(r, t, r), (0, 2), (0, 2 * math.pi), nu=5, nv=24, fill=THEORY, stroke=THEORY,
          opacity=(0.06, 0.24), stroke_width=0.4, stroke_opacity=0.35)
S.polygon([cyl(2, 2 * math.pi * k / 96, 2) for k in range(97)], THEORY, 0.18, THEORY, 1.6)
S.point((0, 0, 2), TEXT, 3.6)
S.point((2, 0, 0), TEXT, 3.2)
S.point((0, 2, 0), TEXT, 3.2)
S.label((0, 0, 2), "2", -9, -5, TEXT, 12, "end")
S.label((2, 0, 0), "2", -10, 10, TEXT, 12, "end")
S.label((0, 2, 0), "2", 4, 16, TEXT, 12)
S.label(cyl(2, 125 * DEG, 2), it("z") + " = 2", 10, 5, THEORY, 13, "start", True)
S.label(cyl(1.3, 125 * DEG, 1.3), it("z") + " = " + SQRT_XY, 12, 6, THEORY, 12.5, "start", True)
S.label(cyl(2, 5.6, 0), it("D"), 10, 14, BASE, 14, "start", True)
save("koni", figure(
    int(pl.x0 + pl.w + 60), int(pl.y0 + pl.h + 30), [pl],
    "Altta <em>z</em> = &#8730;(<em>x</em><sup>2</sup> + <em>y</em><sup>2</sup>) konisi, üstte <em>z</em> = 2 "
    "düzlemiyle sınırlanan cisim. <em>xy</em>-düzlemine izdüşümü <em>D</em>: <em>x</em><sup>2</sup> + "
    "<em>y</em><sup>2</sup> &#8804; 4 diskidir; silindirik koordinatlarda cisim 0 &#8804; <em>r</em> &#8804; 2, "
    "<em>r</em> &#8804; <em>z</em> &#8804; 2 ile verilir.",
    aria="Solid cone with vertex at the origin, bounded below by the cone z = sqrt(x^2 + y^2) and above by "
         "the plane z = 2, with its projection, the disk of radius 2, shaded in the xy plane"))

# ============================================================
# ceyrek-koni: 0 <= theta <= pi/2, r <= z <= 2 (exercise)
# ============================================================
cam = Camera(azimuth=35.0, elevation=22.0)
pl, S = fit_space(cam, [(2.9, 0, 0), (0, 2.9, 0), (0, 0, 3.0), (2, 0, 2), (0, 2, 2), cyl(2, math.pi / 4, 2)],
                  40, 30, 100, 0.45)
S.axes(2.9, 2.9, 3.0)
S.polygon([(0, 0, 0)] + [cyl(2, math.pi / 2 * k / 40, 0) for k in range(41)], TEXT, 0.06, TEXT, 1.0, "4 3")
# the two flat faces in the coordinate planes
S.polygon([(0, 0, 0), (2, 0, 2), (0, 0, 2)], THEORY, 0.12, THEORY, 1.4)
S.polygon([(0, 0, 0), (0, 2, 2), (0, 0, 2)], THEORY, 0.12, THEORY, 1.4)
for r, t in ((2, 0.0), (2, math.pi / 2)):
    S.guide([cyl(r, t, 0), cyl(r, t, 2)], TEXT, 0.45)
# curved face z = r and the top quarter disk z = 2
S.surface(lambda r, t: cyl(r, t, r), (0, 2), (0, math.pi / 2), nu=5, nv=10, fill=THEORY, stroke=THEORY,
          opacity=(0.08, 0.26), stroke_width=0.4, stroke_opacity=0.35)
S.polygon([(0, 0, 2)] + [cyl(2, math.pi / 2 * k / 40, 2) for k in range(41)], PRACTICE, 0.20, PRACTICE, 1.6)
S.point((0, 0, 2), TEXT, 3.4)
S.label((0, 0, 2), "2", -9, -4, TEXT, 12, "end")
S.label((2, 0, 0), "2", -8, 12, TEXT, 12, "end")
S.label((0, 2, 0), "2", 2, 16, TEXT, 12)
S.label(cyl(2, math.pi / 4, 2), it("z") + " = 2", 10, -10, PRACTICE, 13, "start", True)
splabel(S, cyl(1.3, 0.55, 1.3), it("z") + " = " + it("r"), 14, 10, THEORY, 13, "start", True)
save("ceyrek-koni", figure(
    int(pl.x0 + pl.w + 50), int(pl.y0 + pl.h + 30), [pl],
    "0 &#8804; <em>&#952;</em> &#8804; &#960;/2, <em>r</em> &#8804; <em>z</em> &#8804; 2 cismi: <em>z</em> = "
    "<em>r</em> konisinin üstünde, <em>z</em> = 2 düzleminin altında kalan dolu koninin <em>x</em> &#8805; 0, "
    "<em>y</em> &#8805; 0 tarafındaki çeyreği.",
    aria="Quarter of a solid cone in the first octant, bounded by the cone z = r, the plane z = 2 and the "
         "coordinate planes x = 0 and y = 0"))
