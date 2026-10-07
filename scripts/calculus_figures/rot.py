# -*- coding: utf-8 -*-
"""
Figures of the chapter "Rotasyonel ve Diverjans"
(dersler/integral-calculus/rotasyonel-ve-diverjans.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box and never directly under a heading.
Concept figures stay visible: donme and akis-rot in the prose on the physical
meaning of the curl, akis-div in the prose on the physical meaning of the
divergence, normal in the statement of the normal form of Green's theorem.
yol shows a step of a proof and sits inside that proof; the exercise figures
(alan, cisim) sit under the question text of their box.
The figures are NOT produced at build time. Run

    python scripts/calculus_figures/rot.py
    python scripts/center_figures.py "calculus-rot-*.md"
    python scripts/check_figure_labels.py "scripts/_figures/calculus-rot-*.md"

and paste the markup of scripts/_figures/calculus-rot-<name>.md into the .qmd.
Captions are Turkish on purpose; aria labels are plain ASCII.

Vector fields are drawn with arrows that start at their base point and whose
lengths are proportional to |F| (one common scale per panel).
"""
import html
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, TEXT, THEORY, PRACTICE, BASE, BG, WIDE  # noqa: E402
from svg_plot3 import Camera, Space, vadd, vsub, vscale, vcross, vunit  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "calculus-rot-"

MINUS = "&#8722;"
PI_S = "&#960;"
THETA = "&#952;"
OMEGA = "&#969;"
ZWSP = chr(0x200B)          # the zero-width space the sub/sup helpers leave behind


def html_caption(s):
    """Turn the SVG tspan markup of it()/bf()/sub()/sup() into HTML for the <figcaption>."""
    s = re.sub(r'<tspan font-size="[\d.]+" dy="3.5">(.*?)</tspan><tspan dy="-3.5">&#8203;</tspan>',
               r"<sub>\1</sub>", s)
    s = re.sub(r'<tspan font-size="[\d.]+" dy="-5">(.*?)</tspan><tspan dy="5">&#8203;</tspan>',
               r"<sup>\1</sup>", s)
    s = re.sub(r'<tspan font-style="italic">(.*?)</tspan>', r"<em>\1</em>", s)
    s = re.sub(r'<tspan font-weight="700">(.*?)</tspan>', r"<b>\1</b>", s)
    return s


def save(name, markup):
    markup = re.sub(r"<figcaption>(.*?)</figcaption>",
                    lambda m: "<figcaption>" + html_caption(m.group(1)) + "</figcaption>", markup, flags=re.S)
    assert "tspan" not in markup.split("<figcaption>")[1], name
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
    """Label on a page-coloured plate, for text that must sit on arrows or a meshed surface."""
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


def arrow_px(p, a, b, color=THEORY, width=1.4, opacity=1.0, minpx=2.5, head_max=7.0):
    """Arrow from data point a to b whose head shrinks with short shafts; a dot if almost zero."""
    X0, Y0, X1, Y1 = p.X(a[0]), p.Y(a[1]), p.X(b[0]), p.Y(b[1])
    L = math.hypot(X1 - X0, Y1 - Y0)
    if L < minpx:
        p.add(f'<circle cx="{X0:.1f}" cy="{Y0:.1f}" r="1.2" fill="{color}" opacity="{opacity}"/>')
        return
    head = min(head_max, 0.35 * L + 2.5)
    ux, uy = (X1 - X0) / L, (Y1 - Y0) / L
    sx, sy = X1 - ux * head * 0.8, Y1 - uy * head * 0.8
    hw = head * 0.42
    p.add(f'<line x1="{X0:.1f}" y1="{Y0:.1f}" x2="{sx:.1f}" y2="{sy:.1f}" stroke="{color}" '
          f'stroke-width="{width}" opacity="{opacity}" stroke-linecap="round"/>')
    p.add(f'<polygon points="{X1:.1f},{Y1:.1f} {X1 - ux * head - uy * hw:.1f},{Y1 - uy * head + ux * hw:.1f} '
          f'{X1 - ux * head + uy * hw:.1f},{Y1 - uy * head - ux * hw:.1f}" fill="{color}" opacity="{opacity}"/>')


def field(p, F, xs, ys, scale, color=THEORY, width=1.4, opacity=0.9):
    """Arrow plot of the plane field F on the grid xs x ys; arrows start at the grid points."""
    for x in xs:
        for y in ys:
            vx, vy = F(x, y)
            arrow_px(p, (x, y), (x + scale * vx, y + scale * vy), color, width, opacity)


def frange(a, b, h):
    n = int(round((b - a) / h))
    return [a + k * h for k in range(n + 1)]


def axes2(p, xl="x", yl="y", opacity=0.55):
    """Axes through the data origin with arrowheads, clipped to the panel."""
    ox, oy = p.X(0), p.Y(0)
    left, right = p.x0 - 4, p.x0 + p.w + 10
    top, bottom = p.y0 - 10, p.y0 + p.h + 4
    p.add(f'<g stroke="{TEXT}" stroke-width="1.1" opacity="{opacity}" fill="{TEXT}">'
          f'<line x1="{left:.1f}" y1="{oy:.1f}" x2="{right:.1f}" y2="{oy:.1f}"/>'
          f'<line x1="{ox:.1f}" y1="{bottom:.1f}" x2="{ox:.1f}" y2="{top:.1f}"/>'
          f'<polygon points="{right:.1f},{oy:.1f} {right - 8:.1f},{oy - 3.5:.1f} {right - 8:.1f},{oy + 3.5:.1f}" stroke="none"/>'
          f'<polygon points="{ox:.1f},{top:.1f} {ox - 3.5:.1f},{top + 8:.1f} {ox + 3.5:.1f},{top + 8:.1f}" stroke="none"/>'
          f'</g>')
    p.text_px(right - 2, oy + 16, it(xl), TEXT, 12, "end")
    p.text_px(ox + 8, top + 10, it(yl), TEXT, 12, "start")


def spin(p, c, r_px, a0, a1, color, width=1.6):
    """Circular arc of r_px pixels about the data point c, angles in degrees (counter-clockwise
    on the page when a1 > a0), with an arrowhead at a1."""
    cx, cy = p.X(c[0]), p.Y(c[1])
    n = 40
    pts = []
    for k in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * k / n)
        pts.append((cx + r_px * math.cos(a), cy - r_px * math.sin(a)))
    d = " ".join(("M" if k == 0 else "L") + f"{X:.1f},{Y:.1f}" for k, (X, Y) in enumerate(pts[:-3]))
    p.add(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round"/>')
    (Xa, Ya), (Xb, Yb) = pts[-4], pts[-1]
    L = math.hypot(Xb - Xa, Yb - Ya) or 1.0
    ux, uy = (Xb - Xa) / L, (Yb - Ya) / L
    head, hw = 7.5, 3.2
    p.add(f'<polygon points="{Xb + ux * 2:.1f},{Yb + uy * 2:.1f} {Xb - ux * head - uy * hw:.1f},{Yb - uy * head + ux * hw:.1f} '
          f'{Xb - ux * head + uy * hw:.1f},{Yb - uy * head - ux * hw:.1f}" fill="{color}"/>')


def wheel(p, c, color=PRACTICE, r_px=8.0):
    """A small paddle wheel: four paddles tilted by 20 degrees around a hub, on a page-coloured disk."""
    cx, cy = p.X(c[0]), p.Y(c[1])
    p.add(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r_px + 2.5:.1f}" fill="{BG}" opacity="0.9"/>')
    d = ""
    for k in range(4):
        a = math.radians(20 + 90 * k)
        d += f"M{cx:.1f},{cy:.1f} L{cx + r_px * math.cos(a):.1f},{cy - r_px * math.sin(a):.1f} "
    p.add(f'<path d="{d.strip()}" stroke="{color}" stroke-width="2.6" stroke-linecap="round"/>')
    p.add(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="2.6" fill="{color}"/>')


def under(p, lines, size=12.5, gap=19, first=26):
    """Centred lines of text under a panel (panel titles of a two-panel figure)."""
    for k, s in enumerate(lines):
        p.text_px(p.x0 + p.w / 2, p.y0 + p.h + first + k * gap, s, TEXT, size, "middle")


F_B, I_B, J_B, K_B, R_B, N_B, T_B = bf("F"), bf("i"), bf("j"), bf("k"), bf("r"), bf("n"), bf("T")
CURLF = "curl " + F_B
DIVF = "div " + F_B
P1, P2 = it("A") + sub("1"), it("A") + sub("2")

# ============================================================
# donme: the curl vector is the axis of the local rotation (right-hand rule)
# ============================================================
cam = Camera(azimuth=35.0, elevation=22.0)
NRM = vunit((-0.1, 0.25, 1.0))
E1 = vunit(vcross((0.0, 0.0, 1.0), NRM))
E2 = vcross(NRM, E1)
RAD = 1.25
O3 = (0.0, 0.0, 0.0)


def ring(t, r=RAD):
    return vadd(vscale(r * math.cos(t), E1), vscale(r * math.sin(t), E2))


TIP = vscale(2.15, NRM)
pts = [ring(k * math.pi / 8) for k in range(16)] + [TIP, vscale(-0.3, NRM)]
pl, S = fit_space(cam, pts, 60, 30, 170, 0.35)
# disk with four paddles, painted below the axis
S.polygon([ring(k * 2 * math.pi / 72) for k in range(72)], THEORY, 0.12)
for k in range(4):
    a = math.pi / 4 + k * math.pi / 2
    S.line([O3, ring(a, RAD * 0.92)], TEXT, 1.0, None, 0.45)
# the rim, travelled counter-clockwise as seen from the tip of curl F: three arcs with heads
for k in range(3):
    t0 = 2 * math.pi * k / 3 + 0.25
    S.segment_arrow(lambda t: ring(t), t0, t0 + 2 * math.pi / 3 - 0.5, THEORY, 2.0, 9.0, 60)
# the axis: the curl vector
S.arrow(O3, TIP, PRACTICE, 2.4, 10.0)
S.point(O3, PRACTICE, 4.0)
S.label(TIP, CURLF + "(" + it("x") + ", " + it("y") + ", " + it("z") + ")", -12, 6, PRACTICE, 13, "end", True)
splabel(S, O3, "(" + it("x") + ", " + it("y") + ", " + it("z") + ")", 8, 18, TEXT, 12.5)
save("donme", figure(
    int(pl.x0 + pl.w + 190), int(pl.y0 + pl.h + 30), [pl],
    "Hız alanı " + F_B + " olan bir akışkanda (" + it("x") + ", " + it("y") + ", " + it("z") + ") noktasının "
    "yakınındaki parçacıklar, curl " + F_B + "(" + it("x") + ", " + it("y") + ", " + it("z") + ") "
    "doğrultusundaki eksen etrafında döner. Vektörün ucundan bakıldığında dönme saatin tersi yönündedir "
    "(sağ el kuralı); vektörün uzunluğu dönmenin hızını ölçer.",
    aria="A small translucent disk with four spokes around a point, its rim drawn with arrows "
         "turning counterclockwise when seen from the tip of the curl vector, which stands "
         "perpendicular to the disk at the point"))

# ============================================================
# akis-rot: (a) sin y i + cos x j with curl = -(sin x + cos y) k, (b) 2xy i + (x^2 + y) j, curl 0
# ============================================================
# (a) on [-3.2, 3.2] with grid step pi/4, so that A1 and A2 sit at the centres of grid cells;
# (b) on [-1.6, 1.6] with grid step 0.4; both panels are 320 px wide, one arrow scale per panel
LA, LB = 3.2, 1.6
pa = eq_plot(50, 30, 50.0, (-LA, LA), (-LA, LA))
pb = eq_plot(50 + pa.w + 70, 30, 100.0, (-LB, LB), (-LB, LB))
for p, L in ((pa, LA), (pb, LB)):
    p.polygon([(-L, -L), (L, -L), (L, L), (-L, L)], TEXT, 0.03, TEXT, 0.8)
    axes2(p)
HA = math.pi / 4
GA = [(k + 0.5) * HA for k in range(-4, 4)]
field(pa, lambda x, y: (math.sin(y), math.cos(x)), GA, GA, 0.75 * HA / math.sqrt(2), THEORY, 1.4, 0.85)
HB = 0.4
GB = [(k + 0.5) * HB for k in range(-4, 4)]
MAXB = math.hypot(2 * 1.4 * 1.4, 1.4 * 1.4 + 1.4)      # longest arrow of panel (b)
field(pb, lambda x, y: (2 * x * y, x * x + y), GB, GB, 0.85 * HB / MAXB, THEORY, 1.4, 0.85)
A1 = (-math.pi / 2, math.pi / 2)
A2 = (math.pi / 2, math.pi / 2)
spin(pa, A1, 14, -60, 220, PRACTICE, 1.8)
spin(pa, A2, 14, 240, -40, PRACTICE, 1.8)
wheel(pa, A1, PRACTICE, 7.0)
wheel(pa, A2, PRACTICE, 7.0)
plabel(pa, *A1, P1, -21, 5, PRACTICE, 13, "end", True)
plabel(pa, *A2, P2, -21, 5, PRACTICE, 13, "end", True)
BP = (-0.8, 1.2)
wheel(pb, BP, PRACTICE, 7.0)
plabel(pb, *BP, it("A"), -14, -14, PRACTICE, 13, "end", True)
under(pa, ["(a) " + F_B + " = sin " + it("y") + " " + I_B + " + cos " + it("x") + " " + J_B,
           CURLF + " = " + MINUS + "(sin " + it("x") + " + cos " + it("y") + ") " + K_B])
under(pb, ["(b) " + F_B + " = 2" + it("xy") + " " + I_B + " + (" + it("x") + sup("2") + " + " + it("y") + ") " + J_B,
           CURLF + " = " + bf("0")])
save("akis-rot", figure(
    int(pb.x0 + pb.w + 30), int(pa.y0 + pa.h + 70), [pa, pb],
    "İki düzlem akışı (alanlar " + it("z") + "'den bağımsızdır, " + it("z") + "-bileşenleri 0'dır). "
    "(a) " + P1 + " = (" + MINUS + PI_S + "/2, " + PI_S + "/2) noktasında curl " + F_B + " = " + K_B +
    " olduğundan buraya konan küçük çark saatin tersi yönünde, " + P2 + " = (" + PI_S + "/2, " + PI_S +
    "/2) noktasında curl " + F_B + " = " + MINUS + K_B + " olduğundan saat yönünde döner. "
    "(b) Her yerde curl " + F_B + " = " + bf("0") + " olduğundan " + it("A") + " noktasındaki çark akışla "
    "birlikte sürüklenir ama kendi ekseni etrafında dönmez.",
    css_class=WIDE,
    aria="Two arrow plots. Left: the field sin y i + cos x j with paddle "
         "wheels at A1 turning counterclockwise and at A2 turning clockwise. Right: the field "
         "2xy i + (x^2 + y) j with a paddle wheel at A that does not turn"))

# ============================================================
# akis-div: (a) (1 + x^2) i + y j with div = 2x + 1, (b) -x i + y j with div 0
# ============================================================
PPU = 70.0
L = 2.2
pa = eq_plot(50, 30, PPU, (-L, L), (-L, L))
pb = eq_plot(50 + pa.w + 70, 30, PPU, (-L, L), (-L, L))
for p in (pa, pb):
    p.polygon([(-L, -L), (L, -L), (L, L), (-L, L)], TEXT, 0.03, TEXT, 0.8)
    axes2(p)
GRID = frange(-1.75, 1.75, 0.5)
MAXA = math.hypot(1 + 1.75 ** 2, 1.75)          # longest arrow of panel (a)
field(pa, lambda x, y: (1 + x * x, y), GRID, GRID, 0.46 / MAXA, THEORY, 1.4, 0.85)
field(pb, lambda x, y: (-x, y), GRID, GRID, 0.46 / MAXA, THEORY, 1.4, 0.85)
C1, C2 = (-1.5, 1.0), (1.0, 1.0)
for p, c in ((pa, C1), (pa, C2), (pb, C2)):
    p.circle(c[0], c[1], 0.3, PRACTICE, 1.3, "4 3")
    p.points([c], PRACTICE, 4.0)
plabel(pa, *C1, P1, -24, -14, PRACTICE, 13, "end", True)
plabel(pa, *C2, P2, -24, -14, PRACTICE, 13, "end", True)
plabel(pb, *C2, it("A"), -24, -14, PRACTICE, 13, "end", True)
under(pa, ["(a) " + F_B + " = (1 + " + it("x") + sup("2") + ") " + I_B + " + " + it("y") + " " + J_B,
           DIVF + " = 2" + it("x") + " + 1"])
under(pb, ["(b) " + F_B + " = " + MINUS + it("x") + " " + I_B + " + " + it("y") + " " + J_B,
           DIVF + " = 0"])
save("akis-div", figure(
    int(pb.x0 + pb.w + 30), int(pa.y0 + pa.h + 70), [pa, pb],
    "(a) " + P1 + " = (" + MINUS + "1,5; 1) noktasında div " + F_B + " = " + MINUS + "2 &lt; 0: kesikli "
    "çemberin içine giren oklar çıkanlardan uzundur, net akış içeri doğrudur. " + P2 + " = (1, 1) "
    "noktasında div " + F_B + " = 3 &gt; 0: çıkan oklar daha uzundur, net akış dışarı doğrudur. "
    "(b) div " + F_B + " = 0 her yerde; " + it("A") + " = (1, 1) çevresine giren ve çıkan akış dengededir.",
    css_class=WIDE,
    aria="Two arrow plots on the square from -2.2 to 2.2. Left: the field (1 + x^2) i + y j with dashed "
         "circles around A1 = (-1.5, 1) and A2 = (1, 1). Right: the field -x i + y j with a dashed "
         "circle around A = (1, 1)"))


# ============================================================
# normal: the unit tangent T and the outward unit normal n on a positively oriented boundary
# ============================================================
def rho(t):
    return 1.0 + 0.18 * math.cos(2 * t - 0.6) + 0.10 * math.sin(3 * t + 0.4)


CX, CY = 2.1, 1.75


def bnd(t):
    return (CX + 1.45 * rho(t) * math.cos(t), CY + 1.05 * rho(t) * math.sin(t))


def dbnd(t, h=1e-5):
    a, b = bnd(t - h), bnd(t + h)
    return ((b[0] - a[0]) / (2 * h), (b[1] - a[1]) / (2 * h))


p = eq_plot(40, 20, 95, (-0.3, 4.3), (-0.3, 3.5))
axes2(p)
p.text_px(p.X(0) - 6, p.Y(0) + 15, "0", TEXT, 11.5, "end")
curve = [bnd(2 * math.pi * k / 240) for k in range(240)]
p.polygon(curve, BASE, 0.14)
p.line(curve + [curve[0]], BASE, 2.0)
# direction of travel: arrowheads at two places
for t0 in (2.2, 4.9):
    a, b = bnd(t0 - 0.06), bnd(t0 + 0.06)
    p.arrow(a, b, BASE, 2.0, 10.0)
T0 = 0.55
Q0 = bnd(T0)
dx_, dy_ = dbnd(T0)
nrm = math.hypot(dx_, dy_)
TV = (dx_ / nrm, dy_ / nrm)
NV = (dy_ / nrm, -dx_ / nrm)
SC = 0.95
p.arrow(Q0, (Q0[0] + SC * TV[0], Q0[1] + SC * TV[1]), THEORY, 2.2, 10.0)
p.arrow(Q0, (Q0[0] + SC * NV[0], Q0[1] + SC * NV[1]), PRACTICE, 2.2, 10.0)
# right-angle mark between T and n
s = 0.16
c1 = (Q0[0] + s * TV[0], Q0[1] + s * TV[1])
c2 = (Q0[0] + s * (TV[0] + NV[0]), Q0[1] + s * (TV[1] + NV[1]))
c3 = (Q0[0] + s * NV[0], Q0[1] + s * NV[1])
p.line([c1, c2, c3], TEXT, 1.0, None, 0.7)
p.points([Q0], TEXT, 3.8)
p.label(*Q0, R_B + "(" + it("t") + ")", -8, 22, TEXT, 13, "end")
p.label(Q0[0] + SC * TV[0], Q0[1] + SC * TV[1], T_B + "(" + it("t") + ")", -4, -10, THEORY, 13, "end", True)
p.label(Q0[0] + SC * NV[0], Q0[1] + SC * NV[1], N_B + "(" + it("t") + ")", 8, 6, PRACTICE, 13, "start", True)
p.label(CX - 0.35, CY - 0.1, it("D"), 0, 0, BASE, 15, "middle", True)
p.label(*bnd(4.2), it("C"), -10, 16, BASE, 15, "end", True)
save("normal", figure(
    int(p.x0 + p.w + 30), int(p.y0 + p.h + 30), [p],
    it("C") + " pozitif yönde (" + it("D") + " solda kalacak biçimde) dolaşılır. " + T_B + "(" + it("t") +
    ") birim teğet vektördür; " + N_B + "(" + it("t") + "), " + T_B + "(" + it("t") + ")'nin saat yönünde 90° "
    "döndürülmesiyle elde edilir ve " + it("D") + "'nin dışını gösterir.",
    aria="A smooth closed curve C bounding a shaded region D in the first quadrant, travelled "
         "counterclockwise; at a point r(t) of C the unit tangent T(t) and the outward unit normal n(t) "
         "are drawn with a right-angle mark between them"))

# ============================================================
# yol: the potential of the proof, built along three segments parallel to the axes
# ============================================================
cam = Camera(azimuth=35.0, elevation=22.0)
XQ, YQ, ZQ = 2.2, 2.7, 1.9
A_, B_, Q_ = (XQ, 0.0, 0.0), (XQ, YQ, 0.0), (XQ, YQ, ZQ)
pl, S = fit_space(cam, [O3, (3.2, 0, 0), (0, 3.8, 0), (0, 0, 2.8), Q_, B_], 50, 30, 95, 0.4)
S.axes(3.2, 3.8, 2.8)
S.polygon([O3, A_, B_, (0, YQ, 0)], BASE, 0.07)
S.guide([B_, (0, YQ, 0)], TEXT, 0.4)
S.guide([Q_, (0, 0, ZQ)], TEXT, 0.4)
S.arrow(O3, A_, THEORY, 2.6, 10.0)
S.arrow(A_, B_, BASE, 2.6, 10.0)
S.arrow(B_, Q_, PRACTICE, 2.6, 10.0)
for P in (O3, A_, B_):
    S.point(P, TEXT, 3.4)
S.point(Q_, PRACTICE, 4.2)
S.label(O3, "O", -10, -6, TEXT, 12.5, "end")
S.label(A_, "(" + it("x") + ", 0, 0)", -10, 12, TEXT, 12.5, "end")
S.label(B_, "(" + it("x") + ", " + it("y") + ", 0)", 10, 14, TEXT, 12.5, "start")
S.label(Q_, "(" + it("x") + ", " + it("y") + ", " + it("z") + ")", 10, -6, PRACTICE, 12.5, "start", True)
S.label(vscale(0.5, vadd(O3, A_)), it("C") + sub("1"), 10, 14, THEORY, 13.5, "start", True)
S.label(vscale(0.5, vadd(A_, B_)), it("C") + sub("2"), 0, 20, BASE, 13.5, "middle", True)
S.label(vscale(0.5, vadd(B_, Q_)), it("C") + sub("3"), 10, 4, PRACTICE, 13.5, "start", True)
save("yol", figure(
    int(pl.x0 + pl.w + 40), int(pl.y0 + pl.h + 30), [pl],
    "Potansiyel, orijinden (O) (" + it("x") + ", " + it("y") + ", " + it("z") + ") noktasına eksenlere paralel üç "
    "doğru parçası boyunca toplanır: " + it("C") + sub("1") + " üzerinde yalnız " + it("x") + ", " +
    it("C") + sub("2") + " üzerinde yalnız " + it("y") + ", " + it("C") + sub("3") + " üzerinde yalnız " +
    it("z") + " değişir; bu yüzden sırasıyla yalnız " + it("P") + ", " + it("Q") + " ve " + it("R") +
    " katkı verir.",
    aria="Coordinate axes and a path from the origin O to (x, 0, 0), then to (x, y, 0), then up to (x, y, z), "
         "the three segments C1, C2, C3 parallel to the axes drawn as arrows"))

# ============================================================
# alan: exercise field i + (y/2) j in the first quadrant (div > 0, curl = 0)
# ============================================================
p = eq_plot(40, 20, 95, (-0.35, 4.2), (-0.35, 4.0))
axes2(p)
p.text_px(p.X(0) - 6, p.Y(0) + 15, "0", TEXT, 11.5, "end")
XS = [0.5, 1.3, 2.1, 2.9, 3.7]
YS = [0.3, 1.1, 1.9, 2.7]
field(p, lambda x, y: (1.0, y / 2.0), XS[:-1], YS, 0.48, THEORY, 1.6, 0.9)
PQ = (2.05, 2.3)
p.points([PQ], PRACTICE, 4.2)
plabel(p, *PQ, it("A"), -8, -9, PRACTICE, 13, "end", True)
save("alan", figure(
    int(p.x0 + p.w + 30), int(p.y0 + p.h + 30), [p],
    "Alanın " + it("xy") + "-düzlemindeki kısmı. Alan " + it("z") + "'den bağımsızdır ve " + it("z") +
    "-bileşeni 0'dır.",
    aria="Arrow plot in the first quadrant: every arrow has the same horizontal component, the vertical "
         "component grows with y and is almost zero on the bottom row; a marked point A sits among the arrows"))

# ============================================================
# cisim: a rigid body turning about the z axis, w = omega k, v = w x r
# ============================================================
cam = Camera(azimuth=28.0, elevation=20.0)
RB, Z0, Z1 = 1.7, 1.7, 2.1
PHI = math.radians(5.0)
DP = 1.05
PB = (DP * math.cos(PHI), DP * math.sin(PHI), Z1)
pts = [(RB * math.cos(a), RB * math.sin(a), z) for a in [k * math.pi / 8 for k in range(16)] for z in (Z0, Z1)]
pts += [O3, (2.6, 0, 0), (0, 2.6, 0), (0, 0, 4.0)]
pl, S = fit_space(cam, pts, 50, 30, 105, 0.35)
S.axes(2.6, 2.6, 4.0, offsets=((-4, 13), (10, 4), (-10, -4)))
# side of the slab, then its top face
S.surface(lambda a, z: (RB * math.cos(a), RB * math.sin(a), z), (0, 2 * math.pi), (Z0, Z1), nu=48, nv=1,
          fill=THEORY, stroke=THEORY, opacity=(0.10, 0.22), stroke_width=0.0, stroke_opacity=0.0)
top = [(RB * math.cos(2 * math.pi * k / 96), RB * math.sin(2 * math.pi * k / 96), Z1) for k in range(96)]
S.polygon(top, THEORY, 0.16)
S.line(top + [top[0]], THEORY, 1.4, None, 0.8)
S.curve(lambda a: (RB * math.cos(a), RB * math.sin(a), Z0), -math.pi / 2 + 0.49, math.pi / 2 + 0.49,
        THEORY, 1.2, 60, None, 0.7)
# the axis above the slab: w = omega k and the sense of rotation
S.arrow((0, 0, Z1), (0, 0, 3.55), PRACTICE, 2.4, 10.0)
S.label((0, 0, 3.55), bf("w"), -10, 2, PRACTICE, 14, "end", True)
S.segment_arrow(lambda a: (0.38 * math.cos(a), 0.38 * math.sin(a), 3.05), -2.4, 2.4, TEXT, 1.4, 7.5, 60)
# rim arrows: speeds proportional to the distance from the axis
for a in (-1.15, 1.25, 2.3):
    Pr = (RB * math.cos(a), RB * math.sin(a), Z1)
    S.arrow(Pr, vadd(Pr, vscale(0.45, (-math.sin(a), math.cos(a), 0))), THEORY, 1.8, 8.0)
# position vector r, the angle theta and the distance d
S.line([O3, PB], BASE, 1.8, "5 3")
S.arrow(vscale(0.82, PB), PB, BASE, 1.8, 8.0)
S.line([(0, 0, Z1), PB], TEXT, 1.6)
S.curve(lambda u: vscale(0.55, vunit(vadd(vscale(1 - u, (0, 0, 1.0)), vscale(u, vunit(PB))))), 0, 1,
        TEXT, 1.2, 30)
# velocity of P
VP = vscale(0.75, (-math.sin(PHI), math.cos(PHI), 0))
S.arrow(PB, vadd(PB, VP), PRACTICE, 2.4, 9.0)
S.point(PB, PRACTICE, 4.0)
S.point(O3, TEXT, 3.0)
splabel(S, PB, it("P"), 4, 18, PRACTICE, 13.5, "start", True)
splabel(S, vadd(PB, VP), bf("v"), 4, -8, PRACTICE, 14, "start", True)
splabel(S, vscale(0.5, vadd((0, 0, Z1), PB)), it("d"), 0, -8, TEXT, 13, "middle")
S.label(vscale(0.62, vunit(vadd((0, 0, 1.0), vunit(PB)))), THETA, 8, 4, TEXT, 13, "start")
S.label(vscale(0.5, PB), R_B, 9, 8, BASE, 14, "start", True)
splabel(S, (1.25 * math.cos(-1.25), 1.25 * math.sin(-1.25), Z1), it("B"), 0, 5, THEORY, 14, "middle", True)
S.label(O3, "0", -8, 12, TEXT, 12, "end")
save("cisim", figure(
    int(pl.x0 + pl.w + 30), int(pl.y0 + pl.h + 30), [pl],
    it("B") + " cismi " + it("z") + " ekseni etrafında " + OMEGA + " açısal hızıyla döner; " + bf("w") +
    " = " + OMEGA + K_B + ". " + it("P") + " noktasının eksene uzaklığı " + it("d") + " = |" + R_B +
    "| sin " + THETA + ", hızı ise eksene ve " + R_B + "'ye dik, büyüklüğü " + OMEGA + it("d") + " olan " +
    bf("v") + " vektörüdür.",
    aria="A disk-shaped body B turning about the z axis with the angular velocity vector w on the axis; "
         "a point P of the body, its position vector r from the origin making the angle theta with the "
         "z axis, its distance d to the axis and its velocity v tangent to the circle it travels"))
