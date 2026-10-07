# -*- coding: utf-8 -*-
"""
Figures of the chapter "Stokes Teoremi"
(dersler/integral-calculus/stokes-teoremi.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box and never directly under a heading.
The figures are NOT produced at build time. Run

    python scripts/calculus_figures/sto.py
    python scripts/center_figures.py "calculus-sto-*.md"
    python scripts/check_figure_labels.py "scripts/_figures/calculus-sto-*.md"

and paste the markup of scripts/_figures/calculus-sto-<name>.md into the .qmd.
Captions are Turkish on purpose; aria labels are plain ASCII.

Colour roles: surfaces THEORY, boundary curves and normals PRACTICE, plane
regions on the floor BASE.
"""
import html
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, panel_title, TEXT, THEORY, PRACTICE, BASE, BG, WIDE  # noqa: E402
from svg_plot3 import Camera, Space, vadd, vsub, vscale, vdot, vcross, vunit, vnorm  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "calculus-sto-"

MINUS = "&#8722;"
PI = "&#960;"
ZWSP = chr(0x200B)
D2R = math.pi / 180.0
TAU = 2 * math.pi


def save(name, markup):
    (OUT_DIR / f"{PREFIX}{name}.md").write_text(markup, encoding="utf-8", newline="\n")
    print(f"{PREFIX}{name}.md")


def it(s):
    """Italic run inside an SVG <text>."""
    return f'<tspan font-style="italic">{s}</tspan>'


def bf(s):
    """Bold upright run (vectors) inside an SVG <text>."""
    return f'<tspan font-weight="700" font-style="normal">{s}</tspan>'


def sub(s, size=8.5):
    """Subscript inside an SVG <text>."""
    return f'<tspan font-size="{size}" dy="3.5">{s}</tspan><tspan dy="-3.5">&#8203;</tspan>'


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


def vis_curve(S, f, t0, t1, visible, color=THEORY, width=1.6, samples=160, hidden_opacity=0.45,
              hidden_dash="4 3", opacity=1.0):
    """Curve drawn solid where visible(t) is true and dashed elsewhere."""
    pts = [(f(t0 + (t1 - t0) * k / samples), visible(t0 + (t1 - t0) * k / samples)) for k in range(samples + 1)]
    run, state = [pts[0][0]], pts[0][1]
    for P, v in pts[1:]:
        run.append(P)
        if v != state:
            S.line(run, color, width, None if state else hidden_dash, opacity if state else hidden_opacity)
            run, state = [P], v
    S.line(run, color, width, None if state else hidden_dash, opacity if state else hidden_opacity)


def arrow_on(S, f, t, dt=0.06, color=PRACTICE, width=2.2, head=9.0):
    """Arrowhead on the space curve f at parameter t, pointing toward increasing t."""
    S.arrow(f(t - dt), f(t + dt), color, width, head)


def leader(S, P, Q2, s, dx=0, dy=4, color=TEXT, size=11.5, anchor="start"):
    """Thin leader line from the space point P to the screen point Q2 = (X, Y) with a label there."""
    X, Y = S.pt(P)
    S.p.line([(X, Y), Q2], TEXT, 0.9, None, 0.7)
    S.p.label(Q2[0], Q2[1], s, dx, dy, color, size, anchor)


def square_to_disk(u, v):
    """Smooth map of the square [-1, 1]^2 onto the unit disk (no pole in the middle of the grid)."""
    return (u * math.sqrt(1 - v * v / 2), v * math.sqrt(1 - u * u / 2))


def leader_end(S, P, Xend, Y, s, color=TEXT, size=11.5):
    """Leader from the space point P to a label whose right edge is at the screen x Xend (data units).

    Anchoring at the right edge keeps the label inside the extent of the rest of the drawing, so the
    canvas does not have to grow to the right for it."""
    w = (text_w(s, size) + 6) / (S.p.w / (S.p.xmax - S.p.xmin))
    X, Yp = S.pt(P)
    S.p.line([(X, Yp), (Xend - w, Y)], TEXT, 0.9, None, 0.7)
    S.p.label(Xend, Y, s, 0, 4, color, size, "end")


CAM = Camera(azimuth=35.0, elevation=22.0)
O = (0.0, 0.0, 0.0)
K = (0.0, 0.0, 1.0)
VEC_N = bf("n")
VEC_V = bf("v")
CURL_V = "curl " + VEC_V


# ============================================================
# pozitif-yon: an oriented surface, its unit normals and the induced orientation of the boundary
# ============================================================
cam1 = Camera(azimuth=35.0, elevation=30.0)
C1c = (0.4, 2.4, 0.0)


def rad1(th):
    return 1.55 + 0.17 * math.cos(3 * th + 0.5) + 0.10 * math.sin(2 * th)


def zb1(th):
    return 1.75 + 0.25 * math.sin(2 * th + 0.3)


Z1, H1 = 1.75, 0.5


def surf1(rho, th):
    R = rad1(th)
    return (C1c[0] + rho * R * math.cos(th), C1c[1] + 1.15 * rho * R * math.sin(th),
            Z1 + H1 * (1 - rho ** 2) + rho ** 2 * (zb1(th) - Z1))


def surf1_sq(u, v):
    a, b = square_to_disk(u, v)
    return surf1(math.hypot(a, b), math.atan2(b, a))


def normal1(rho, th, h=1e-4):
    a = vsub(surf1(rho + h, th), surf1(rho - h, th))
    b = vsub(surf1(rho, th + h), surf1(rho, th - h))
    n = vunit(vcross(a, b))
    return n if n[2] > 0 else vscale(-1, n)


def rim1(th):
    return surf1(1.0, th)


pl, S = fit_space(cam1, [O, (2.4, 0, 0), (0, 4.6, 0), (0, 0, 3.6), rim1(0), rim1(math.pi / 2), rim1(math.pi),
                         rim1(3 * math.pi / 2), vadd(surf1(0.1, 1.0), (0, 0, 1.1))], 40, 30, 92, 0.3)
S.axes(2.4, 4.6, 3.6)
S.surface(surf1_sq, (-1, 1), (-1, 1), nu=14, nv=14, fill=THEORY, stroke=THEORY, opacity=(0.08, 0.30),
          stroke_width=0.35, stroke_opacity=0.25)
S.curve(rim1, 0, TAU, PRACTICE, 2.3, 240)
for th in (1.1, 4.3):
    arrow_on(S, rim1, th, 0.07)
for rho, th in ((0.08, 1.0), (0.78, 2.6), (0.72, 5.6)):
    P = surf1(rho, th)
    n = normal1(rho, th)
    S.arrow(P, vadd(P, vscale(0.95, n)), PRACTICE, 2.0, 8.5)
    S.point(P, PRACTICE, 2.6)
    S.label(vadd(P, vscale(0.95, n)), VEC_N, 8, 2, PRACTICE, 13.5, "start", True)
splabel(S, surf1(0.45, 4.9), it("S"), 0, 4, THEORY, 14, "middle", True)
S.label(rim1(0.1), it("C"), -2, 22, PRACTICE, 14, "middle", True)
S.label(O, "0", -8, 12, TEXT, 11.5, "end")
save("pozitif-yon", figure(
    int(pl.x0 + pl.w + 40), int(pl.y0 + pl.h + 30), [pl],
    "Birim normali <strong>n</strong> olan yönlendirilmiş <em>S</em> yüzeyi ve sınır eğrisi <em>C</em>'nin "
    "pozitif yönü. Başı <strong>n</strong> yönünde olan biri <em>C</em> üzerinde oklar yönünde yürürse "
    "yüzey hep solunda kalır. Burada <strong>n</strong> yukarı baktığından bu yön, yukarıdan bakınca saat "
    "yönünün tersidir.",
    aria="A curved surface S floating above the xy-plane, three upward unit normal vectors n on it and its "
         "boundary curve C with arrowheads that run counterclockwise when seen from above"))


# ============================================================
# grafik: S is the graph z = g(x, y) over D; the boundary C sits above the boundary C1 of D
# ============================================================
cx2, cy2, ax2, ay2 = 1.5, 2.1, 1.05, 1.35


def sq(t, e=0.5):
    return math.copysign(abs(t) ** e, t)


def dom2(rho, th):
    return (cx2 + rho * ax2 * sq(math.cos(th)), cy2 + rho * ay2 * sq(math.sin(th)))


def g2(x, y):
    return 1.75 + 0.32 * math.sin(2.1 * (y - cy2) + 0.4) - 0.22 * (x - cx2)


def surf2(rho, th):
    x, y = dom2(rho, th)
    return (x, y, g2(x, y))


def surf2_sq(u, v):
    a, b = square_to_disk(u, v)
    return surf2(math.hypot(a, b), math.atan2(b, a))


def floor2(rho, th):
    x, y = dom2(rho, th)
    return (x, y, 0.0)


pl, S = fit_space(CAM, [O, (3.2, 0, 0), (0, 4.4, 0), (0, 0, 3.0), surf2(1, 0), surf2(1, math.pi / 2),
                        surf2(1, math.pi), surf2(1, 1.5 * math.pi), floor2(1, 0), floor2(1, math.pi)],
                  40, 30, 74, 0.3)
S.axes(3.2, 4.4, 3.0)
S.polygon([floor2(1, TAU * k / 120) for k in range(120)], BASE, 0.14)
S.curve(lambda t: floor2(1, t), 0, TAU, BASE, 1.9, 240)
arrow_on(S, lambda t: floor2(1, t), 4.0, 0.07, BASE, 1.9, 8.5)
arrow_on(S, lambda t: floor2(1, t), 1.3, 0.07, BASE, 1.9, 8.5)
for th in (math.pi / 4, 3 * math.pi / 4, 5 * math.pi / 4, 7 * math.pi / 4):
    S.guide([floor2(1, th), surf2(1, th)], TEXT, 0.5)
S.surface(surf2_sq, (-1, 1), (-1, 1), nu=14, nv=14, fill=THEORY, stroke=THEORY, opacity=(0.10, 0.32),
          stroke_width=0.35, stroke_opacity=0.25)
S.curve(lambda t: surf2(1, t), 0, TAU, PRACTICE, 2.3, 240)
arrow_on(S, lambda t: surf2(1, t), 4.0, 0.07)
arrow_on(S, lambda t: surf2(1, t), 1.3, 0.07)
Pn = surf2(0.3, 2.3)
h = 1e-4
gx = (g2(Pn[0] + h, Pn[1]) - g2(Pn[0] - h, Pn[1])) / (2 * h)
gy = (g2(Pn[0], Pn[1] + h) - g2(Pn[0], Pn[1] - h)) / (2 * h)
nn = vunit((-gx, -gy, 1.0))
S.arrow(Pn, vadd(Pn, vscale(1.0, nn)), PRACTICE, 2.0, 8.5)
S.point(Pn, PRACTICE, 2.6)
S.label(vadd(Pn, vscale(1.0, nn)), VEC_N, 8, 2, PRACTICE, 13.5, "start", True)
splabel(S, surf2(0.45, 5.3), it("S"), 0, 4, THEORY, 14, "middle", True)
S.label(surf2(1, 5.6), it("C"), -12, 4, PRACTICE, 14, "end", True)
splabel(S, floor2(0.25, 4.9), it("D"), 0, 4, BASE, 14, "middle", True)
S.label(floor2(1, 4.6), it("C") + sub("1", 10.5), -6, 16, BASE, 14, "end", True)
S.label(surf2(1, 2.0), it("z") + " = " + it("g") + "(" + it("x") + ", " + it("y") + ")", 10, -8, THEORY, 12.5)
S.label(O, "0", -8, 12, TEXT, 11.5, "end")
save("grafik", figure(
    int(pl.x0 + pl.w + 80), int(pl.y0 + pl.h + 30), [pl],
    "<em>S</em> yüzeyi <em>z</em> = <em>g</em>(<em>x</em>, <em>y</em>) grafiği olduğunda gölgesi "
    "<em>D</em> bölgesidir ve <em>S</em>'nin sınırı <em>C</em>, <em>D</em>'nin sınırı <em>C</em>&#8321;'in "
    "tam üstünde durur. <em>S</em> yukarı yönlendirilmişse <em>C</em>'nin pozitif yönü, <em>C</em>&#8321;'in "
    "pozitif yönünün (saat yönünün tersinin) üstündeki yöndür.",
    aria="A wavy surface S, the graph of z = g(x, y), above a rounded region D of the xy-plane; dashed "
         "verticals join the boundary curve C of S to the boundary curve C1 of D, both oriented "
         "counterclockwise as seen from above, and an upward normal n on S"))


# ============================================================
# elips: example 1, the plane y + z = 2 cut by the cylinder x^2 + y^2 = 1
# ============================================================
def wall3(th, s):
    return (math.cos(th), math.sin(th), s * (2 - math.sin(th)))


def plane3(rho, th):
    return (rho * math.cos(th), rho * math.sin(th), 2 - rho * math.sin(th))


def rim3(th):
    return plane3(1.0, th)


def plane3_sq(u, v):
    a, b = square_to_disk(u, v)
    return (a, b, 2 - b)


def front3(th):
    """Outward normal of the cylinder faces the camera."""
    return math.cos(th) * CAM.d[0] + math.sin(th) * CAM.d[1] >= 0


pl, S = fit_space(CAM, [O, (2.0, 0, 0), (0, 2.4, 0), (0, 0, 3.7), rim3(0), rim3(math.pi / 2),
                        rim3(-math.pi / 2), (1, 0, 0), (-1, 0, 0)], 40, 30, 110, 0.3)
S.axes(2.0, 2.4, 3.7, xmin=0, ymin=0)
# floor disk D
S.surface(lambda rho, th: (rho * math.cos(th), rho * math.sin(th), 0.0), (0, 1), (0, TAU), nu=2, nv=40,
          fill=BASE, stroke=BASE, opacity=(0.12, 0.16), stroke_width=0.0, stroke_opacity=0.0)
vis_curve(S, lambda t: (math.cos(t), math.sin(t), 0.0), 0, TAU, front3, BASE, 1.5)
# cylinder wall up to the plane
S.surface(wall3, (0, TAU), (0, 1), nu=40, nv=4, fill=THEORY, stroke=THEORY, opacity=(0.03, 0.12),
          stroke_width=0.0, stroke_opacity=0.0)
for th in (35 * D2R + math.pi / 2, 35 * D2R - math.pi / 2):
    S.line([wall3(th, 0), wall3(th, 1)], THEORY, 1.3, None, 0.8)
# the elliptic region S in the plane
S.surface(plane3_sq, (-1, 1), (-1, 1), nu=12, nv=12, fill=THEORY, stroke=THEORY, opacity=(0.14, 0.34),
          stroke_width=0.3, stroke_opacity=0.22)
S.curve(rim3, 0, TAU, PRACTICE, 2.3, 240)
arrow_on(S, rim3, 5.0, 0.07)
arrow_on(S, rim3, 1.9, 0.07)
splabel(S, plane3(0.35, 3.6), it("S"), 0, 4, THEORY, 14, "middle", True)
S.label(rim3(5.45), it("C"), -7, 2, PRACTICE, 14, "end", True)
S.label((0.55, -0.35, 0), it("D"), 0, 4, BASE, 14, "middle", True)
XT = S.pt((0, 2.4, 0))[0]
Xp, Yp = S.pt(plane3(0.8, 1.3))
leader_end(S, plane3(0.8, 1.3), XT, Yp + 0.35, it("y") + " + " + it("z") + " = 2", THEORY, 12.5)
Xw, Yw = S.pt(wall3(1.95, 0.35))
leader_end(S, wall3(1.95, 0.35), XT, Yw - 0.1, it("x") + "² + " + it("y") + "² = 1", THEORY, 12.5)
S.label(O, "0", -8, 12, TEXT, 11.5, "end")
save("elips", figure(
    int(pl.x0 + pl.w + 60), int(pl.y0 + pl.h + 30), [pl],
    "<em>y</em> + <em>z</em> = 2 düzlemi <em>x</em>² + <em>y</em>² = 1 silindirini <em>C</em> elipsinde "
    "keser. <em>S</em>, düzlemin <em>C</em> içinde kalan parçasıdır; gölgesi birim daire <em>D</em>'dir. "
    "<em>C</em> yukarıdan bakınca saat yönünün tersine dolanır, bu yüzden <em>S</em> yukarı yönlendirilir.",
    aria="A vertical cylinder of radius 1 standing on the unit disk D and cut off above by the tilted plane "
         "y + z = 2; the elliptic piece S of the plane and its boundary ellipse C, oriented counterclockwise "
         "when seen from above"))


# ============================================================
# ayni-sinir: a disk, a hemisphere and a paraboloid with the same boundary circle
# ============================================================
R4 = 2.0
box4 = [O, (2.9, 0, 0), (0, 3.0, 0), (0, 0, 4.6), (-2, 0, 0), (0, -2, 0), (2, 0, 0), (0, 2, 0),
        (2 * math.cos(-55 * D2R), 2 * math.sin(-55 * D2R), 0)]


def front_circle(th):
    return math.cos(th) * CAM.d[0] + math.sin(th) * CAM.d[1] >= 0


panels = []
left = 20
titles = ("disk " + it("D"), "yarım küre " + it("H"), "paraboloit " + it("P"))
for k in range(3):
    pl, S = fit_space(CAM, box4, left, 40, 40, 0.25)
    left += pl.w + 18
    S.axes(2.9, 3.0, 4.6, offsets=((-4, 13), (10, 4), (-10, -4)))
    # the label sits a little high so that it clears the apex of the paraboloid in the third panel
    S.ticks("z", [4], offset=(-11, 1))
    rim = (lambda t: (R4 * math.cos(t), R4 * math.sin(t), 0.0))
    if k == 0:
        S.surface(lambda rho, th: (rho * math.cos(th), rho * math.sin(th), 0.0), (0, R4), (0, TAU), nu=3, nv=40,
                  fill=THEORY, stroke=THEORY, opacity=(0.14, 0.22), stroke_width=0.3, stroke_opacity=0.25)
        S.curve(rim, 0, TAU, PRACTICE, 2.1, 200)
        top = (1.2 * math.cos(1.9), 1.2 * math.sin(1.9), 0.0)
        ntop = K
    elif k == 1:
        vis_curve(S, rim, 0, TAU, front_circle, PRACTICE, 2.1, 200, 0.6, "4 3")
        S.surface(lambda ph, th: (R4 * math.sin(ph) * math.cos(th), R4 * math.sin(ph) * math.sin(th),
                                  R4 * math.cos(ph)), (0, math.pi / 2), (0, TAU), nu=7, nv=28, fill=THEORY,
                  stroke=THEORY, opacity=(0.06, 0.26), stroke_width=0.3, stroke_opacity=0.25)
        ph_, th_ = 50 * D2R, 1.9
        ntop = (math.sin(ph_) * math.cos(th_), math.sin(ph_) * math.sin(th_), math.cos(ph_))
        top = vscale(R4, ntop)
    else:
        vis_curve(S, rim, 0, TAU, front_circle, PRACTICE, 2.1, 200, 0.6, "4 3")
        S.surface(lambda rho, th: (rho * math.cos(th), rho * math.sin(th), 4 - rho ** 2), (0, R4), (0, TAU),
                  nu=8, nv=28, fill=THEORY, stroke=THEORY, opacity=(0.06, 0.26), stroke_width=0.3,
                  stroke_opacity=0.25)
        rr_, th_ = 1.25, 1.9
        top = (rr_ * math.cos(th_), rr_ * math.sin(th_), 4 - rr_ ** 2)
        ntop = vunit((2 * top[0], 2 * top[1], 1.0))
    if k != 0:
        # redraw the visible front half of the rim on top of the surface
        vis_curve(S, rim, 0, TAU, front_circle, PRACTICE, 2.1, 200, 0.0, None)
    arrow_on(S, rim, 0.75, 0.06, PRACTICE, 2.1, 8.5)
    S.point(top, PRACTICE, 2.4)
    S.arrow(top, vadd(top, vscale(1.0, ntop)), PRACTICE, 1.9, 8.0)
    S.label(vadd(top, vscale(1.0, ntop)), VEC_N, 7, 4, PRACTICE, 13, "start", True)
    S.label(rim(5.55), it("C"), -8, 14, PRACTICE, 13, "end", True)
    panel_title(pl, titles[k])
    panels.append(pl)
save("ayni-sinir", figure(
    int(left), int(max(q.y0 + q.h for q in panels) + 20), panels,
    "Sınırı aynı <em>C</em> çemberi (<em>x</em>² + <em>y</em>² = 4, <em>z</em> = 0) olan üç yüzey: "
    "<em>x</em>² + <em>y</em>² &#8804; 4 diski, <em>x</em>² + <em>y</em>² + <em>z</em>² = 4 küresinin üst "
    "yarısı ve <em>z</em> = 4 &#8722; <em>x</em>² &#8722; <em>y</em>² paraboloitinin <em>xy</em>-düzleminin "
    "üstündeki parçası. Üçü de yukarı yönlendirildiğinde <em>C</em>'ye aynı pozitif yönü verir.",
    css_class=WIDE,
    aria="Three panels: the disk of radius 2 in the xy-plane, the upper hemisphere of radius 2 and the "
         "paraboloid z = 4 - x^2 - y^2 above the xy-plane; all three share the boundary circle C of radius 2, "
         "drawn with the same counterclockwise arrow, and carry an upward normal n"))


# ============================================================
# kure-silindir: example 2, the cap of the sphere of radius 2 inside the cylinder of radius 1, and the disk
# ============================================================
R5, Z5 = 2.0, math.sqrt(3.0)
cam5 = Camera(azimuth=35.0, elevation=18.0)
box5 = [O, (2.6, 0, 0), (0, 2.8, 0), (0, 0, 2.9), (-2, 0, 0), (0, -2, 0), (2, 0, 0), (0, 2, 0)]


def front5(th):
    return math.cos(th) * cam5.d[0] + math.sin(th) * cam5.d[1] >= 0


panels = []
left = 20
for k in range(2):
    pl, S = fit_space(cam5, box5, left, 40, 80, 0.2)
    left += pl.w + 24
    X5, Y5 = S.pt(O)
    # silhouette of the upper hemisphere: the upper half of the sphere's screen circle
    S.p.line([(X5 + R5 * math.cos(math.pi * j / 80), Y5 + R5 * math.sin(math.pi * j / 80)) for j in range(81)],
             TEXT, 1.1, None, 0.55)
    vis_curve(S, lambda t: (R5 * math.cos(t), R5 * math.sin(t), 0.0), 0, TAU, front5, TEXT, 1.1, 160, 0.35,
              "4 3", 0.55)
    S.axes(2.6, 2.8, 2.9, offsets=((-4, 13), (10, 4), (-10, -4)))
    # the cylinder x^2 + y^2 = 1 between z = 0 and z = sqrt(3)
    vis_curve(S, lambda t: (math.cos(t), math.sin(t), 0.0), 0, TAU, front5, TEXT, 1.0, 120, 0.35, "4 3", 0.6)
    for th in (35 * D2R + math.pi / 2, 35 * D2R - math.pi / 2):
        S.line([(math.cos(th), math.sin(th), 0), (math.cos(th), math.sin(th), Z5)], TEXT, 1.0, None, 0.6)
    if k == 0:
        S.surface(lambda ph, th: (R5 * math.sin(ph) * math.cos(th), R5 * math.sin(ph) * math.sin(th),
                                  R5 * math.cos(ph)), (0, math.pi / 6), (0, TAU), nu=4, nv=32, fill=THEORY,
                  stroke=THEORY, opacity=(0.18, 0.40), stroke_width=0.3, stroke_opacity=0.3)
        Xc, Yc = S.pt((0.0, -0.45, 1.93))
        leader(S, (0.0, -0.45, 1.93), (Xc - 0.75, Yc + 0.55), it("S"), -4, 4, THEORY, 14, "end")
        S.arrow((0, 0, R5), (0, 0, R5 + 0.7), PRACTICE, 1.9, 8.0)
        S.label((0, 0, R5 + 0.7), VEC_N, 8, 4, PRACTICE, 13, "start", True)
        panel_title(pl, it("S") + ": küre parçası")
    else:
        S.surface(lambda rho, th: (rho * math.cos(th), rho * math.sin(th), Z5), (0, 1), (0, TAU), nu=3, nv=32,
                  fill=BASE, stroke=BASE, opacity=(0.20, 0.32), stroke_width=0.3, stroke_opacity=0.3)
        splabel(S, (0.0, -0.3, Z5), it("S") + sub("1", 9.5), 0, 4, BASE, 14, "middle", True)
        S.arrow((0, 0, Z5), (0, 0, Z5 + 0.75), PRACTICE, 1.9, 8.0)
        S.label((0, 0, Z5 + 0.75), bf("k"), 8, 4, PRACTICE, 13, "start", True)
        panel_title(pl, it("S") + sub("1", 9.5) + ": disk")
    S.curve(lambda t: (math.cos(t), math.sin(t), Z5), 0, TAU, PRACTICE, 2.1, 160)
    arrow_on(S, lambda t: (math.cos(t), math.sin(t), Z5), 0.75, 0.08, PRACTICE, 2.1, 8.5)
    S.label((math.cos(-0.95), math.sin(-0.95), Z5), it("C"), -9, 6, PRACTICE, 13, "end", True)
    if k == 0:
        Xs, Ys = S.pt((R5 * math.cos(70 * D2R) * math.sin(55 * D2R), R5 * math.sin(70 * D2R) * math.sin(55 * D2R),
                       R5 * math.cos(55 * D2R)))
        leader(S, (R5 * math.sin(55 * D2R) * math.cos(70 * D2R), R5 * math.sin(55 * D2R) * math.sin(70 * D2R),
                   R5 * math.cos(55 * D2R)), (Xs + 0.55, Ys + 0.75),
               it("x") + "² + " + it("y") + "² + " + it("z") + "² = 4", 2, -2, TEXT, 11.5)
    else:
        th_r = 35 * D2R + math.pi / 2
        Xo, Yo = S.pt(O)
        leader_end(S, (math.cos(th_r), math.sin(th_r), 1.0), S.pt((0, 2.8, 0))[0], Yo + 1.85,
                   it("x") + "² + " + it("y") + "² = 1", TEXT, 11.5)
    panels.append(pl)
save("kure-silindir", figure(
    int(left + 10), int(max(q.y0 + q.h for q in panels) + 20), panels,
    "Solda <em>x</em>² + <em>y</em>² + <em>z</em>² = 4 küresinin <em>x</em>² + <em>y</em>² = 1 silindiri "
    "içinde kalan üst parçası <em>S</em>, sağda <em>z</em> = &#8730;3 düzlemindeki birim disk "
    "<em>S</em>&#8321;. İkisinin sınırı aynı <em>C</em> çemberidir (<em>x</em>² + <em>y</em>² = 1, "
    "<em>z</em> = &#8730;3) ve yukarı yönlendirildiklerinde <em>C</em>'ye aynı yönü verirler.",
    css_class=WIDE,
    aria="Two panels with the upper hemisphere of radius 2 and the cylinder of radius 1 drawn thin. Left: "
         "the spherical cap S above the circle C at height sqrt(3) with an upward normal n. Right: the flat "
         "disk S1 at height sqrt(3) with the same boundary circle C and normal k"))


# ============================================================
# dolanim: circulation of a planar velocity field around two closed curves
# ============================================================
V1, V2, SIG = (-2.3, -0.7), (2.1, 0.8), 1.7


def vel(x, y):
    """Two vortices: counterclockwise around V1, clockwise around V2, plus a weak drift."""
    vx = vy = 0.0
    for (a, b), s in ((V1, 1.0), (V2, -1.0)):
        w = s * math.exp(-((x - a) ** 2 + (y - b) ** 2) / SIG ** 2)
        vx += -w * (y - b)
        vy += w * (x - a)
    return vx + 0.12, vy


def curve6(c, base, wob):
    def f(t):
        r = base + sum(a * math.cos(k * t + ph) for a, k, ph in wob)
        return (c[0] + 1.1 * r * math.cos(t), c[1] + r * math.sin(t))
    return f


C1f = curve6(V1, 1.25, [(0.18, 2, 0.4), (0.10, 3, 1.2)])
C2f = curve6(V2, 1.15, [(0.20, 2, 2.0), (0.08, 3, 0.3)])


def circulation(f, n=2000):
    tot = 0.0
    for k in range(n):
        t0, t1 = TAU * k / n, TAU * (k + 1) / n
        p0, p1 = f(t0), f(t1)
        vm = vel((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2)
        tot += vm[0] * (p1[0] - p0[0]) + vm[1] * (p1[1] - p0[1])
    return tot


assert circulation(C1f) > 0 and circulation(C2f) < 0
XR6, YR6 = (-4.8, 4.8), (-2.9, 2.9)
p = eq_plot(30, 20, 62, XR6, YR6)
p.origin_axes("x", "y", opacity=0.45)
for i in range(-6, 7):
    for j in range(-3, 4):
        x, y = 0.75 * i, 0.75 * j
        if abs(x) > 4.6 or abs(y) > 2.6:
            continue
        vx, vy = vel(x, y)
        L = math.hypot(vx, vy)
        sc = 0.55 * min(1.0, L / 0.9) / max(L, 1e-9)
        if L < 0.05:
            continue
        p.arrow((x - 0.5 * sc * vx, y - 0.5 * sc * vy), (x + 0.5 * sc * vx, y + 0.5 * sc * vy), BASE, 1.2, 5.5,
                None, 0.75)
for f, tmark, name, off in ((C1f, 5.4, "C" + "", (-1.6, -1.55)), (C2f, 1.9, "C", (2.9, 2.05))):
    pts = [f(TAU * k / 240) for k in range(241)]
    p.line(pts, THEORY, 2.0)
    for ta in (tmark, tmark + math.pi):
        p.arrow(f(ta - 0.05), f(ta + 0.05), THEORY, 2.0, 9.0)
p.label(-2.3 - 1.75, -0.7 - 1.25, it("C") + sub("1", 9.5), -2, 4, THEORY, 14, "end", True)
p.label(2.1 + 1.45, 0.8 + 1.15, it("C") + sub("2", 9.5), 4, 0, THEORY, 14, "start", True)
for f, tq, side in ((C1f, 0.35, 1), (C2f, 3.6, -1)):
    P = f(tq)
    d = (f(tq + 1e-4)[0] - f(tq - 1e-4)[0], f(tq + 1e-4)[1] - f(tq - 1e-4)[1])
    Ld = math.hypot(*d)
    T = (d[0] / Ld, d[1] / Ld)
    vv = vel(*P)
    Lv = math.hypot(*vv)
    vv = (vv[0] / Lv * 0.85, vv[1] / Lv * 0.85)
    p.arrow(P, (P[0] + 0.9 * T[0], P[1] + 0.9 * T[1]), PRACTICE, 2.0, 8.5)
    p.arrow(P, (P[0] + vv[0], P[1] + vv[1]), TEXT, 2.0, 8.5)
    p.points([P], PRACTICE, 3.0)
    p.label(P[0] + 0.9 * T[0], P[1] + 0.9 * T[1], bf("T"), -8 if side > 0 else 8, 4 if side > 0 else 6,
            PRACTICE, 13, "end" if side > 0 else "start")
    p.label(P[0] + vv[0], P[1] + vv[1], bf("v"), 7 if side > 0 else -7, 4, TEXT, 13,
            "start" if side > 0 else "end")
save("dolanim", figure(
    int(p.x0 + p.w + 40), int(p.y0 + p.h + 30), [p],
    "Bir akışkanın hız alanı <strong>v</strong> (oklar) ve iki kapalı eğri. <em>C</em>&#8321; boyunca "
    "<strong>v</strong> çoğunlukla eğrinin <strong>T</strong> teğetiyle aynı yöne akar, <strong>v</strong> "
    "&#183; <strong>T</strong> &gt; 0 olur ve dolanım pozitiftir. <em>C</em>&#8322; boyunca akış eğrinin "
    "yönüne karşıdır, dolanım negatiftir.",
    aria="A planar velocity field drawn as arrows with a counterclockwise whirl on the left and a clockwise "
         "whirl on the right; the closed curve C1 around the left whirl and C2 around the right whirl are both "
         "traversed counterclockwise; at one point of each the unit tangent T and the velocity v are drawn, "
         "nearly parallel on C1 and nearly opposite on C2"))


# ============================================================
# kucuk-disk: a small disk S_a about P0 with normal n, its boundary C_a and the vector curl v(P0)
# ============================================================
cam7 = Camera(azimuth=30.0, elevation=24.0)
P0 = (0.0, 0.0, 0.0)
n7 = vunit((0.25, -0.15, 1.0))
e1 = vunit(vcross(n7, (0.0, 1.0, 0.0)))
e1 = vscale(-1, e1) if e1[0] < 0 else e1
e2 = vcross(n7, e1)
a7 = 1.0
cv = vunit(vadd(vscale(math.cos(38 * D2R), n7), vscale(math.sin(38 * D2R), vunit((-0.2, 1.0, 0.2)))))
cv = vscale(2.0, cv)


def disk7(rho, th):
    return vadd(P0, vadd(vscale(rho * a7 * math.cos(th), e1), vscale(rho * a7 * math.sin(th), e2)))


def rim7(th):
    return disk7(1.0, th)


pl, S = fit_space(cam7, [rim7(k * TAU / 16) for k in range(16)] + [vscale(1.6, n7), cv,
                                                                  vadd(rim7(0), (0, 0, -0.3))],
                  40, 30, 190, 0.35)
S.surface(disk7, (0, 1), (0, TAU), nu=3, nv=24, fill=THEORY, stroke=THEORY, opacity=(0.14, 0.28),
          stroke_width=0.3, stroke_opacity=0.18)
S.curve(rim7, 0, TAU, PRACTICE, 2.3, 200)
arrow_on(S, rim7, 4.9, 0.06)
arrow_on(S, rim7, 1.8, 0.06)
# the radius a
S.line([P0, rim7(5.75)], TEXT, 1.1, None, 0.8)
S.label(disk7(0.55, 5.75), it("a"), 2, 14, TEXT, 13, "middle")
# the normal n(P0), the vector curl v(P0) and its projection onto n
S.arrow(P0, vscale(1.1, n7), PRACTICE, 2.1, 9.0)
S.label(vscale(1.1, n7), VEC_N + "(" + it("P") + sub("0", 10) + ")", -8, 4, PRACTICE, 13, "end")
foot = vscale(vdot(cv, n7), n7)
S.guide([vscale(1.12, n7), foot], PRACTICE, 0.6)
S.guide([cv, foot], TEXT, 0.6)
S.arrow(P0, cv, THEORY, 2.3, 9.5)
S.label(cv, CURL_V + "(" + it("P") + sub("0", 10) + ")", -6, -6, THEORY, 13, "end")
S.point(P0, TEXT, 3.2)
S.label(P0, it("P") + sub("0", 10), 6, 16, TEXT, 13, "start")
splabel(S, disk7(0.62, 3.6), it("S") + sub(it("a"), 10), 0, 4, THEORY, 13.5, "middle", True)
S.label(rim7(2.6), it("C") + sub(it("a"), 10), -8, 8, PRACTICE, 13.5, "end", True)
save("kucuk-disk", figure(
    int(pl.x0 + pl.w + 60), int(pl.y0 + pl.h + 30), [pl],
    "<em>P</em>&#8320; merkezli, <em>a</em> yarıçaplı ve birim normali <strong>n</strong> olan küçük "
    "<em>S<sub>a</sub></em> diski ile sınırı <em>C<sub>a</sub></em>. <em>C<sub>a</sub></em> etrafındaki "
    "dolanım yaklaşık olarak (curl <strong>v</strong>(<em>P</em>&#8320;) &#183; <strong>n</strong>) "
    "<em>&#960;a</em>²'dir; çarpandaki iç çarpım, curl <strong>v</strong>'nin <strong>n</strong> doğrultusundaki "
    "bileşenidir (kesikli izdüşüm).",
    aria="A small tilted disk S_a of radius a centred at P0, its boundary circle C_a with arrows, the unit "
         "normal n(P0) and the vector curl v(P0) at an angle to it, with a dashed drop from the tip of curl v "
         "to the normal line"))


# ============================================================
# kup: exercise, the cube with vertices (+-1, +-1, +-1) without its bottom face
# ============================================================
cam8 = Camera(azimuth=35.0, elevation=24.0)
V = {(sx, sy, sz): (float(sx), float(sy), float(sz)) for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1)}
pl, S = fit_space(cam8, list(V.values()) + [(0, 0, 1.9), (0.4, 1.9, 0.3)], 40, 30, 105, 0.3)
faces = {
    "top": [V[(-1, -1, 1)], V[(1, -1, 1)], V[(1, 1, 1)], V[(-1, 1, 1)]],
    "x+": [V[(1, -1, -1)], V[(1, 1, -1)], V[(1, 1, 1)], V[(1, -1, 1)]],
    "x-": [V[(-1, -1, -1)], V[(-1, 1, -1)], V[(-1, 1, 1)], V[(-1, -1, 1)]],
    "y+": [V[(-1, 1, -1)], V[(1, 1, -1)], V[(1, 1, 1)], V[(-1, 1, 1)]],
    "y-": [V[(-1, -1, -1)], V[(1, -1, -1)], V[(1, -1, 1)], V[(-1, -1, 1)]],
}
for name in sorted(faces, key=lambda nm: sum(S.depth(q) for q in faces[nm])):
    S.polygon(faces[name], THEORY, 0.13 if name in ("x-", "y-") else 0.20, "none")
hidden = V[(-1, -1, -1)]
edges = set()
for a in V:
    for b in V:
        if a < b and sum(1 for i in range(3) if a[i] != b[i]) == 1:
            edges.add((a, b))
for a, b in edges:
    if a[2] == -1 and b[2] == -1:
        continue      # the bottom square is the boundary curve, drawn below
    dashed = hidden in (V[a], V[b])
    S.line([V[a], V[b]], THEORY, 1.3, "4 3" if dashed else None, 0.55 if dashed else 0.9)
sq8 = [V[(1, -1, -1)], V[(1, 1, -1)], V[(-1, 1, -1)], V[(-1, -1, -1)], V[(1, -1, -1)]]
for i in range(4):
    A, B = sq8[i], sq8[i + 1]
    dashed = hidden in (A, B)
    S.line([A, B], PRACTICE, 2.2, "5 4" if dashed else None, 0.6 if dashed else 1.0)
    if not dashed:
        M = vscale(0.5, vadd(A, B))
        S.arrow(vadd(M, vscale(-0.08, vsub(B, A))), vadd(M, vscale(0.08, vsub(B, A))), PRACTICE, 2.2, 9.0)
S.arrow((0, 0, 1), (0, 0, 1.75), PRACTICE, 1.9, 8.0)
S.label((0, 0, 1.75), VEC_N, 8, 4, PRACTICE, 13, "start", True)
S.point((0.3, 1, 0.3), PRACTICE, 2.4)
S.arrow((0.3, 1, 0.3), (0.3, 1.75, 0.3), PRACTICE, 1.9, 8.0)
S.label((0.3, 1.75, 0.3), VEC_N, 2, -9, PRACTICE, 13, "middle", True)
S.point((0, 0, 1), PRACTICE, 2.4)
S.label(V[(1, 1, -1)], it("C"), 8, 12, PRACTICE, 14, "start", True)
splabel(S, (1.0, -0.35, 0.25), it("S"), 0, 4, THEORY, 14, "middle", True)
splabel(S, V[(1, 1, 1)], "(1, 1, 1)", 8, 18, TEXT, 11.5, "start")
S.label(V[(1, -1, -1)], "(1, " + MINUS + "1, " + MINUS + "1)", -4, 18, TEXT, 11.5, "middle")
save("kup", figure(
    int(pl.x0 + pl.w + 60), int(pl.y0 + pl.h + 30), [pl],
    "Köşeleri (&#177;1, &#177;1, &#177;1) olan küpün tabanı çıkarılmış yüzeyi <em>S</em>: üst yüz ve dört "
    "yan yüz, normaller dışa doğru. Sınırı, <em>z</em> = &#8722;1 düzlemindeki kare <em>C</em>'dir ve "
    "yukarıdan bakınca saat yönünün tersine dolanır.",
    aria="Open box: the cube with vertices (+-1, +-1, +-1) without its bottom face, outward normals on the top "
         "and on the right face, and the bottom square C at z = -1 with arrows running counterclockwise when "
         "seen from above"))
