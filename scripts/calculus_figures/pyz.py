# -*- coding: utf-8 -*-
"""
Figures of the chapter "Parametrik Yüzeyler ve Alanları"
(dersler/integral-calculus/parametrik-yuzeyler-ve-alanlari.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box and never directly under a heading.
Concept figures stay visible: parametrik-yuzey under the definition of grid
curves, ceyrek-silindir and kure in the prose after their examples, donel in
the statement of the proposition on surfaces of revolution (before the proof),
teget-duzlem under the definition of the tangent plane, yama in the prose that
motivates the surface area definition. spiral-tup sits under the question
text of its example, sinus-donel inside its solution.
The figures are NOT produced at build time. Run

    python scripts/calculus_figures/pyz.py
    python scripts/center_figures.py "calculus-pyz-*.md"
    python scripts/check_figure_labels.py "scripts/_figures/calculus-pyz-*.md"

and paste the markup of scripts/_figures/calculus-pyz-<name>.md into the .qmd.
Captions are Turkish on purpose; aria labels are plain ASCII.
"""
import html
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, dot, blob, TEXT, THEORY, PRACTICE, BASE, BG, WIDE  # noqa: E402
from svg_plot3 import Camera, Space, vadd, vsub, vscale, vcross, vdot, vunit, vnorm  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "calculus-pyz-"

MINUS = "&#8722;"
DELTA = "&#916;"
PHI = "&#966;"
THETA = "&#952;"
PI = "&#960;"
TIMES = "&#215;"
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


def pixel_plot(W, H):
    """A panel whose data coordinates are the canvas pixels (y down)."""
    return Plot(0, 0, W, H, (0, W), (H, 0))


def connector(W, H, x0, x1, y, label):
    """Horizontal mapping arrow between two panels with a label above it."""
    q = pixel_plot(W, H)
    q.arrow((x0, y), (x1, y), TEXT, 1.6, 8.0, None, 0.85)
    q.text_px((x0 + x1) / 2, y - 8, label, TEXT, 14, "middle")
    return q


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
          f'height="{size + 4:.1f}" rx="3" fill="{BG}" opacity="0.85"/>')
    p.label(x, y, s, dx, dy, color, size, anchor, bold)


def splabel(S, P, s, dx=0, dy=0, color=TEXT, size=11.5, anchor="start", bold=False):
    """plabel() at a space point."""
    X, Y = S.pt(P)
    plabel(S.p, X, Y, s, dx, dy, color, size, anchor, bold)


def vis_curve(S, f, t0, t1, front, color, width=1.8, n=160, back_dash="4 3", back_opacity=0.55):
    """Space curve drawn solid where front(P) holds and dashed elsewhere."""
    pts = [f(t0 + (t1 - t0) * k / n) for k in range(n + 1)]
    run, state = [pts[0]], front(pts[0])
    for P in pts[1:]:
        s = front(P)
        if s != state:
            run.append(P)
            if state:
                S.line(run, color, width)
            else:
                S.line(run, color, width * 0.8, back_dash, back_opacity)
            run, state = [P], s
        else:
            run.append(P)
    if state:
        S.line(run, color, width)
    else:
        S.line(run, color, width * 0.8, back_dash, back_opacity)


def inside(poly, x, y):
    """Even-odd point-in-polygon test."""
    c = False
    n = len(poly)
    for i in range(n):
        (x1, y1), (x2, y2) = poly[i], poly[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
            c = not c
    return c


def chord(poly, fixed, value, lo, hi, n=400):
    """Interval of the line (u = value if fixed == 'u' else v = value) inside poly."""
    ts = [lo + (hi - lo) * k / n for k in range(n + 1)]
    ins = [t for t in ts if (inside(poly, value, t) if fixed == "u" else inside(poly, t, value))]
    return (min(ins), max(ins)) if ins else None


def deriv(F, u, v, h=1e-5):
    """Numerical partial derivatives r_u, r_v of a space map F(u, v)."""
    ru = vscale(1 / (2 * h), vsub(F(u + h, v), F(u - h, v)))
    rv = vscale(1 / (2 * h), vsub(F(u, v + h), F(u, v - h)))
    return ru, rv


U0, V0 = it("u") + sub("0"), it("v") + sub("0")
R_B = bf("r")
RU, RV = bf("r") + sub(it("u")), bf("r") + sub(it("v"))
C1, C2 = it("C") + sub("1"), it("C") + sub("2")


# The running surface of the general figures: a bent shell over the uv-rectangle [0, 3] x [0, 2].
def shell(u, v):
    ph = 0.25 + 0.55 * v
    return (0.6 + 1.6 * math.cos(ph), 0.5 + 1.05 * u, 1.0 + 1.6 * math.sin(ph) + 0.25 * math.sin(1.3 * u))


# ============================================================
# parametrik-yuzey: D in the uv-plane -> S in space, with the grid curves through (u0, v0)
# ============================================================
BC = (1.5, 1.0)


def blob_pt(t, s=1.0):
    rho = 1.0 + 0.08 * math.cos(2 * t + 0.6) + 0.06 * math.cos(3 * t + 1.9)
    return (BC[0] + s * 1.25 * rho * math.cos(t), BC[1] + s * 0.8 * rho * math.sin(t))


DPOLY = [blob_pt(2 * math.pi * k / 200) for k in range(200)]
UA, VA = 1.75, 1.15
pl = eq_plot(80, 36, 76, (-0.25, 3.35), (-0.25, 2.25))
pl.origin_axes(it("u"), it("v"), opacity=0.5)
pl.label(0, 0, "0", -7, 14, TEXT, 11, "end")
pl.polygon(DPOLY, TEXT, 0.07)
pl.line(DPOLY + [DPOLY[0]], TEXT, 1.6, None, 0.75)
cu = chord(DPOLY, "u", UA, -0.2, 2.2)
cv = chord(DPOLY, "v", VA, -0.2, 3.3)
pl.line([(UA, cu[0]), (UA, cu[1])], PRACTICE, 2.2)
pl.line([(cv[0], VA), (cv[1], VA)], BASE, 2.2)
dot(pl, (UA, VA), TEXT, 3.8)
plabel(pl, UA, VA, "(" + U0 + ", " + V0 + ")", 6, -8, TEXT, 11.5)
pl.label(UA, cu[0], it("u") + " = " + U0, 0, 18, PRACTICE, 12, "middle", True)
pl.label(cv[0], VA, it("v") + " = " + V0, -7, 4, BASE, 12, "end", True)
pl.label(0.75, 0.55, it("D"), 0, 0, TEXT, 15, "middle", True)

cam = Camera(azimuth=35.0, elevation=22.0)
P0 = shell(UA, VA)
grid_pts = [shell(*blob_pt(t, s)) for t in [k * 0.3 for k in range(21)] for s in (0.0, 1.0)]
pr, S = fit_space(cam, [(0, 0, 0), (2.9, 0, 0), (0, 4.2, 0), (0, 0, 3.4)] + grid_pts, 390, 30, 72, 0.25)
S.axes(2.9, 4.2, 3.4)
S.label((0, 0, 0), "0", -8, 4, TEXT, 11, "end")
# the patch: blob in polar form mapped by the shell
S.surface(lambda s, t: shell(*blob_pt(t, s)), (0.0, 1.0), (0.0, 2 * math.pi), nu=8, nv=48,
          fill=THEORY, stroke=THEORY, opacity=(0.08, 0.26), stroke_width=0.3, stroke_opacity=0.0)
# faint grid curves of the patch
for uu in [0.5 + 0.25 * k for k in range(9)]:
    c = chord(DPOLY, "u", uu, -0.2, 2.2)
    if c:
        S.curve(lambda t, uu=uu: shell(uu, t), c[0], c[1], THEORY, 0.7, 40, None, 0.45)
for vv in [0.4 + 0.2 * k for k in range(7)]:
    c = chord(DPOLY, "v", vv, -0.2, 3.3)
    if c:
        S.curve(lambda t, vv=vv: shell(t, vv), c[0], c[1], THEORY, 0.7, 40, None, 0.45)
S.line([shell(*q) for q in DPOLY] + [shell(*DPOLY[0])], THEORY, 1.8)
S.curve(lambda t: shell(UA, t), cu[0], cu[1], PRACTICE, 2.4, 60)
S.curve(lambda t: shell(t, VA), cv[0], cv[1], BASE, 2.4, 60)
S.arrow((0, 0, 0), P0, TEXT, 1.5, 8.0, "5 3", 0.85)
S.point(P0, TEXT, 3.8)
splabel(S, vscale(0.5, P0), R_B + "(" + U0 + ", " + V0 + ")", 8, 16, TEXT, 11.5)
S.label(shell(UA, cu[1]), C1, -2, -8, PRACTICE, 13, "middle", True)
S.label(shell(cv[1], VA), C2, 10, 4, BASE, 13, "start", True)
S.label(shell(*blob_pt(2.6)), it("S"), -8, -6, THEORY, 15, "end", True)
W, H = int(pr.x0 + pr.w + 30), int(max(pl.y0 + pl.h, pr.y0 + pr.h) + 24)
q = connector(W, H, pl.x0 + pl.w + 8, pr.x0 + 62, pl.Y(1.0), R_B)
save("parametrik-yuzey", figure(
    W, H, [pl, pr, q],
    "<b>r</b>, <em>uv</em>-düzlemindeki <em>D</em> bölgesini uzaydaki <em>S</em> yüzeyine gönderir: "
    "(<em>u</em><sub>0</sub>, <em>v</em><sub>0</sub>) noktası, konum vektörü "
    "<b>r</b>(<em>u</em><sub>0</sub>, <em>v</em><sub>0</sub>) olan noktaya gider. <em>D</em>'deki "
    "<em>u</em> = <em>u</em><sub>0</sub> düşey doğrusunun görüntüsü <em>C</em><sub>1</sub>, "
    "<em>v</em> = <em>v</em><sub>0</sub> yatay doğrusunun görüntüsü <em>C</em><sub>2</sub> koordinat "
    "eğrisidir.",
    WIDE,
    aria="Left: a rounded region D in the uv-plane with the vertical line u = u0 and the horizontal line "
         "v = v0 through the point (u0, v0). Right: its image, a curved surface S in space, with the "
         "position vector r(u0, v0) and the grid curves C1 and C2 through its tip"))

# ============================================================
# ceyrek-silindir: the cylinder x^2 + z^2 = 4 and the quarter cylinder 0 <= u <= pi/2, 0 <= v <= 3
# ============================================================
RC = 2.0
cam = Camera(azimuth=35.0, elevation=22.0)


def cyl(u, y):
    return (RC * math.cos(u), y, RC * math.sin(u))


def cyl_front(P):
    n = (P[0], 0.0, P[2])
    return vdot(n, cam.d) > 0


YL0, YL1 = -1.2, 4.2
pts = [cyl(2 * math.pi * k / 24, y) for k in range(24) for y in (YL0, YL1)]
pl, S = fit_space(cam, pts + [(3.3, 0, 0), (0, 5.4, 0), (0, 0, 3.0)], 40, 30, 56, 0.3)
# the x label is drawn last on a plate: its axis tip lies over the translucent cylinder
S.axes(3.3, 5.4, 3.0, labels=("", "y", "z"))
S.label((0, 0, 0), "0", 8, 13, TEXT, 11)
S.surface(lambda u, y: cyl(u, y), (0.0, 2 * math.pi), (YL0, YL1), nu=36, nv=6, fill=THEORY,
          stroke=THEORY, opacity=(0.03, 0.12), stroke_width=0.4, stroke_opacity=0.25)
for yy in (YL0, YL1):
    vis_curve(S, lambda t, yy=yy: cyl(t, yy), 0.0, 2 * math.pi, cyl_front, THEORY, 1.2)
S.surface(lambda u, y: cyl(u, y), (0.0, math.pi / 2), (0.0, 3.0), nu=8, nv=6, fill=PRACTICE,
          stroke=PRACTICE, opacity=(0.18, 0.40), stroke_width=0.5, stroke_opacity=0.5)
S.line([cyl(0, 0), cyl(0, 3)], PRACTICE, 1.8)
S.line([cyl(math.pi / 2, 0), cyl(math.pi / 2, 3)], PRACTICE, 1.8)
S.curve(lambda t: cyl(t, 3.0), 0.0, math.pi / 2, PRACTICE, 1.8, 40)
# the circle v = 0 (y = 0) through (2, 0, 0) and (0, 0, 2)
vis_curve(S, lambda t: cyl(t, 0.0), 0.0, 2 * math.pi, cyl_front, TEXT, 1.6)
for P, s, dx, dy, anc in (((2, 0, 0), "(2, 0, 0)", -10, 16, "end"),
                          ((0, 0, 2), "(0, 0, 2)", -10, -8, "end"),
                          ((0, 3, 2), "(0, 3, 2)", 6, -10, "start")):
    S.point(P, TEXT, 3.6)
    splabel(S, P, s, dx, dy, TEXT, 11.5, anc)
S.label(cyl(0.2, YL1), it("x") + "² + " + it("z") + "² = 4", 8, 14, THEORY, 12, "start", True)
splabel(S, (3.3, 0, 0), it("x"), -4, 13, TEXT, 11.5, "middle")
save("ceyrek-silindir", figure(
    int(pl.x0 + pl.w + 40), int(pl.y0 + pl.h + 30), [pl],
    "<em>x</em>² + <em>z</em>² = 4 silindirinin bir parçası (açık) ve 0 &#8804; <em>u</em> &#8804; "
    "&#960;/2, 0 &#8804; <em>v</em> &#8804; 3 parametre bölgesinin görüntüsü olan çeyrek silindir (koyu). "
    "Siyah çember, <em>v</em> = 0 koordinat eğrisidir; (2, 0, 0) ve (0, 0, 2) noktalarından geçer.",
    aria="A horizontal circular cylinder of radius 2 around the y axis drawn lightly, the quarter of it "
         "with x and z nonnegative and 0 to 3 in y shaded darker, and the circle y = 0 through (2, 0, 0) "
         "and (0, 0, 2); the corner (0, 3, 2) is marked"))

# ============================================================
# spiral-tup: r(u, v) = <(2 + sin v) cos u, (2 + sin v) sin u, u + cos v>, 0 <= u, v <= 2 pi
# ============================================================
# a slightly higher camera than usual keeps the tall coil within the page height
cam = Camera(azimuth=35.0, elevation=28.0)


def tube(u, v):
    R = 2 + math.sin(v)
    return (R * math.cos(u), R * math.sin(u), u + math.cos(v))


pts = [tube(2 * math.pi * i / 40, 2 * math.pi * j / 12) for i in range(41) for j in range(13)]
pl, S = fit_space(cam, pts + [(0, 0, 7.6), (3.6, 0, 0), (0, 3.8, 0)], 40, 30, 52, 0.3)
S.axes(3.6, 3.8, 7.6, labels=("x", "y", "z"))
S.surface(tube, (0.0, 2 * math.pi), (0.0, 2 * math.pi), nu=60, nv=18, fill=THEORY, stroke=THEORY,
          opacity=(0.05, 0.26), stroke_width=0.4, stroke_opacity=0.35)
UC = 4.75
VC = 0.0
S.curve(lambda t: tube(UC, t), 0.0, 2 * math.pi, PRACTICE, 2.6, 80)
S.curve(lambda t: tube(t, VC), 0.0, 2 * math.pi, BASE, 2.6, 160)
save("spiral-tup", figure(
    int(pl.x0 + pl.w + 40), int(pl.y0 + pl.h + 30), [pl],
    "Yüzeyin 0 &#8804; <em>u</em> &#8804; 2&#960;, 0 &#8804; <em>v</em> &#8804; 2&#960; parçası "
    "bir tam tur atan bir tüptür. Kalın çizilen iki koordinat eğrisinden biri küçük bir çember, öbürü "
    "bir sarmaldır.",
    aria="A tube of radius 1 wound once around the z axis like a spring, rising from z = -1 to about "
         "z = 7.3, drawn with its grid; one small circle around the tube and one spiral along it are "
         "drawn thick"))

# ============================================================
# kure: the rectangle [0, pi] x [0, 2 pi] in the phi-theta plane -> the sphere, phi = c and theta = k
# ============================================================
CPH, KTH = math.pi / 3, 1.82 * math.pi
pl = eq_plot(52, 40, 46, (-0.35, 3.75), (-0.35, 6.9))
pl.origin_axes(it(PHI), it(THETA), opacity=0.5)
pl.polygon([(0, 0), (math.pi, 0), (math.pi, 2 * math.pi), (0, 2 * math.pi)], TEXT, 0.07, TEXT, 1.2)
pl.line([(CPH, 0), (CPH, 2 * math.pi)], PRACTICE, 2.2)
pl.line([(0, KTH), (math.pi, KTH)], BASE, 2.2)
for x, s in ((CPH, it("c")), (math.pi, PI)):
    pl.label(x, 0, s, 0, 16, TEXT, 11.5, "middle")
for y, s in ((KTH, it("k")), (2 * math.pi, "2" + PI)):
    pl.label(0, y, s, -7, 4, TEXT, 11.5, "end")
pl.label(0, 0, "0", -7, 15, TEXT, 11, "end")
pl.label(2.3, 2.4, it("D"), 0, 0, TEXT, 15, "middle", True)
plabel(pl, CPH, 3.4, it(PHI) + " = " + it("c"), 6, 4, PRACTICE, 12, "start", True)
plabel(pl, 2.2, KTH, it(THETA) + " = " + it("k"), 0, 17, BASE, 12, "middle", True)

cam = Camera(azimuth=35.0, elevation=22.0)


def sph(ph, th):
    return (math.sin(ph) * math.cos(th), math.sin(ph) * math.sin(th), math.cos(ph))


def sph_front(P):
    return vdot(P, cam.d) > 0


pr, S = fit_space(cam, [sph(math.pi * i / 12, 2 * math.pi * j / 24) for i in range(13) for j in range(24)]
                  + [(1.6, 0, 0), (0, 1.65, 0), (0, 0, 1.55)], 330, 40, 118, 0.2)
# the hidden parts of the axes first, then the translucent sphere
S.axes(1.6, 1.65, 1.55)
S.surface(sph, (0.0, math.pi), (0.0, 2 * math.pi), nu=12, nv=24, fill=THEORY, stroke=THEORY,
          opacity=(0.04, 0.18), stroke_width=0.35, stroke_opacity=0.25)
vis_curve(S, lambda t: sph(math.pi / 2, t), 0.0, 2 * math.pi, sph_front, TEXT, 1.1)
vis_curve(S, lambda t: sph(CPH, t), 0.0, 2 * math.pi, sph_front, PRACTICE, 2.4)
vis_curve(S, lambda t: sph(t, KTH), 0.0, math.pi, sph_front, BASE, 2.4)
S.point((0, 0, 1), TEXT, 3.2)
S.point((0, 0, -1), TEXT, 3.2)
splabel(S, sph(CPH, 0.45 * math.pi), it(PHI) + " = " + it("c"), 6, -8, PRACTICE, 12, "start", True)
splabel(S, sph(0.45 * math.pi, KTH), it(THETA) + " = " + it("k"), -12, 4, BASE, 12, "end", True)
W, H = 640, int(max(pl.y0 + pl.h, pr.y0 + pr.h) + 30)
q = connector(W, H, pl.x0 + pl.w + 14, pr.x0 + 4, pl.Y(math.pi), R_B)
save("kure", figure(
    W, H, [pl, pr, q],
    "Küre parametrelemesi <b>r</b>(<em>&#966;</em>, <em>&#952;</em>), "
    "[0, &#960;] &#215; [0, 2&#960;] dikdörtgenini küreye gönderir. Düşey <em>&#966;</em> = <em>c</em> "
    "doğrusu bir enlem çemberine, yatay <em>&#952;</em> = <em>k</em> doğrusu kutupları birleştiren bir "
    "meridyene gider.",
    WIDE,
    aria="Left: the rectangle 0 to pi by 0 to 2 pi in the phi theta plane with the vertical line phi = c "
         "and the horizontal line theta = k. Right: a sphere with the latitude circle phi = c and the "
         "meridian theta = k joining the poles"))

# ============================================================
# donel: rotating y = f(x) about the x axis; the point (x, f(x) cos t, f(x) sin t)
# ============================================================
cam = Camera(azimuth=35.0, elevation=22.0)
XA_, XB_ = 0.4, 3.8


def fprof(x):
    return 1.0 + 0.45 * math.sin(1.3 * x + 0.2)


def rev(x, t):
    r = fprof(x)
    return (x, r * math.cos(t), r * math.sin(t))


def rev_front(P):
    n = (0.0, P[1], P[2])
    return vdot(n, cam.d) > 0


pts = [rev(XA_ + (XB_ - XA_) * i / 20, 2 * math.pi * j / 24) for i in range(21) for j in range(24)]
pl, S = fit_space(cam, pts + [(4.8, 0, 0), (0, 2.4, 0), (0, 0, 2.2)], 40, 30, 92, 0.3)
S.axes(4.8, 2.4, 2.2)
S.surface(rev, (XA_, XB_), (0.0, 2 * math.pi), nu=24, nv=32, fill=THEORY, stroke=THEORY,
          opacity=(0.03, 0.16), stroke_width=0.3, stroke_opacity=0.22)
# the generating curve y = f(x) in the xy-plane (theta = 0)
S.curve(lambda x: rev(x, 0.0), XA_, XB_, PRACTICE, 2.6, 80)
X0_ = 2.75
T0 = math.radians(65.0)
CEN = (X0_, 0.0, 0.0)
Q = rev(X0_, T0)
vis_curve(S, lambda t: rev(X0_, t), 0.0, 2 * math.pi, rev_front, TEXT, 1.8)
S.line([CEN, rev(X0_, 0.0)], PRACTICE, 1.4, "4 3", 0.9)
S.line([CEN, Q], PRACTICE, 2.2)
# angle marker theta from the y direction toward z
S.curve(lambda t: (X0_, 0.38 * math.cos(t), 0.38 * math.sin(t)), 0.0, T0, TEXT, 1.3, 30)
S.point(CEN, TEXT, 3.2)
S.point(Q, PRACTICE, 4.2)
S.point(rev(X0_, 0.0), PRACTICE, 3.2)
splabel(S, (X0_, 0.56 * math.cos(T0 / 2), 0.56 * math.sin(T0 / 2)), it(THETA), 2, 5, TEXT, 13, "middle")
splabel(S, vscale(0.5, vadd(CEN, Q)), it("f") + "(" + it("x") + ")", -8, 0, PRACTICE, 12, "end", True)
splabel(S, Q, "(" + it("x") + ", " + it("y") + ", " + it("z") + ")", 8, -8, TEXT, 11.5, "start")
splabel(S, rev(1.0, 0.0), it("y") + " = " + it("f") + "(" + it("x") + ")", 10, -8, PRACTICE, 12, "start",
        True)
splabel(S, CEN, it("x"), -10, 12, TEXT, 12, "end")
save("donel", figure(
    int(pl.x0 + pl.w + 40), int(pl.y0 + pl.h + 30), [pl],
    "<em>y</em> = <em>f</em>(<em>x</em>) eğrisi <em>x</em> ekseni çevresinde dönerken eğrinin her noktası, "
    "<em>x</em> eksenine dik düzlemde <em>f</em>(<em>x</em>) yarıçaplı bir çember çizer. <em>y</em> ekseninin "
    "yönünden <em>&#952;</em> kadar dönmüş nokta (<em>x</em>, <em>f</em>(<em>x</em>) cos <em>&#952;</em>, "
    "<em>f</em>(<em>x</em>) sin <em>&#952;</em>) olur.",
    aria="A surface of revolution about the x axis with its generating curve y = f(x) in the xy plane; "
         "one circle of radius f(x) at a fixed x, the angle theta measured from the y direction and the "
         "rotated point (x, y, z)"))

# ============================================================
# sinus-donel: y = sin x, 0 <= x <= 2 pi, rotated about the x axis
# ============================================================
cam = Camera(azimuth=-62.0, elevation=20.0)


def srev(x, t):
    r = math.sin(x)
    return (x, r * math.cos(t), r * math.sin(t))


pts = [srev(2 * math.pi * i / 40, 2 * math.pi * j / 24) for i in range(41) for j in range(24)]
pl, S = fit_space(cam, pts + [(7.3, 0, 0), (0, 1.5, 0), (0, 0, 1.5)], 40, 30, 64, 0.3)
S.axes(7.3, 1.5, 1.5, xmin=0.0, labels=("x", "", "z"), offsets=((10, 4), (8, -4), (-10, -4)))
splabel(S, (0, 1.5, 0), it("y"), 10, -2, TEXT, 11.5, "start")
S.surface(srev, (0.0, 2 * math.pi), (0.0, 2 * math.pi), nu=48, nv=28, fill=THEORY, stroke=THEORY,
          opacity=(0.05, 0.24), stroke_width=0.35, stroke_opacity=0.3)
S.curve(lambda x: (x, math.sin(x), 0.0), 0.0, 2 * math.pi, PRACTICE, 2.2, 120)
for xv, s in ((math.pi, PI), (2 * math.pi, "2" + PI)):
    S.point((xv, 0, 0), TEXT, 3.0)
    S.label((xv, 0, 0), s, 4, 17, TEXT, 11.5, "middle")
S.label((0, 0, 0), "0", -4, 16, TEXT, 11, "middle")
splabel(S, (math.pi / 2, 1.0, 0.0), it("y") + " = sin " + it("x"), 4, 18, PRACTICE, 12, "start", True)
save("sinus-donel", figure(
    int(pl.x0 + pl.w + 40), int(pl.y0 + pl.h + 30), [pl],
    "<em>y</em> = sin <em>x</em>, 0 &#8804; <em>x</em> &#8804; 2&#960; eğrisinin <em>x</em> ekseni "
    "çevresinde döndürülmesiyle oluşan yüzey: <em>x</em> = 0, &#960; ve 2&#960; noktalarında eksene "
    "değen iki iğ.",
    aria="Surface obtained by rotating y = sin x for x from 0 to 2 pi about the x axis: two spindles "
         "touching the axis at 0, pi and 2 pi; the curve y = sin x is drawn on it"))

# ============================================================
# teget-duzlem: grid curves C1, C2 through P0, tangent vectors r_u, r_v, tangent plane and normal
# ============================================================
UT, VT = 1.6, 1.0
P0 = shell(UT, VT)
ru, rv = deriv(shell, UT, VT)
ru_s, rv_s = vscale(0.9, ru), vscale(0.9, rv)
N = vcross(ru, rv)
NT = vadd(P0, vscale(1.15, vunit(N)))
cam = Camera(azimuth=35.0, elevation=22.0)
corners = [vadd(P0, vadd(vscale(a, ru_s), vscale(b, rv_s))) for a, b in ((-1.3, -1.3), (1.3, -1.3),
                                                                          (1.3, 1.3), (-1.3, 1.3))]
sheet = [shell(3.0 * i / 8, 2.0 * j / 6) for i in range(9) for j in range(7)]
pl, S = fit_space(cam, sheet + corners + [NT, (0, 0, 0), (2.6, 0, 0), (0, 4.0, 0), (0, 0, 3.5)],
                  40, 30, 72, 0.25)
S.axes(2.6, 4.0, 3.5)
S.surface(shell, (0.0, 3.0), (0.0, 2.0), nu=12, nv=8, fill=THEORY, stroke=THEORY,
          opacity=(0.06, 0.24), stroke_width=0.4, stroke_opacity=0.35)
S.curve(lambda t: shell(UT, t), 0.0, 2.0, PRACTICE, 1.8, 60, None, 0.8)
S.curve(lambda t: shell(t, VT), 0.0, 3.0, BASE, 1.8, 80, None, 0.8)
S.polygon(corners, TEXT, 0.10, TEXT, 1.0)
S.arrow(P0, vadd(P0, ru_s), BASE, 3.0, 10.0)
S.arrow(P0, vadd(P0, rv_s), PRACTICE, 3.0, 10.0)
S.arrow(P0, NT, TEXT, 2.0, 9.0)
S.point(P0, TEXT, 4.0)
splabel(S, P0, it("P") + sub("0"), -10, 16, TEXT, 12.5, "end", True)
splabel(S, vadd(P0, ru_s), RU, 6, 14, BASE, 13, "start", True)
splabel(S, vadd(P0, rv_s), RV, -8, -6, PRACTICE, 13, "end", True)
splabel(S, NT, RU + " " + TIMES + " " + RV, 8, -2, TEXT, 12.5, "start", True)
splabel(S, shell(UT, 0.0), C1, -7, 1, PRACTICE, 13, "end", True)
S.label(shell(3.0, VT), C2, 8, 4, BASE, 13, "start", True)
S.label(shell(0.0, 1.6), it("S"), -8, 0, THEORY, 14, "end", True)
save("teget-duzlem", figure(
    int(pl.x0 + pl.w + 40), int(pl.y0 + pl.h + 30), [pl],
    "<em>P</em><sub>0</sub>'dan geçen <em>C</em><sub>1</sub> (<em>u</em> = <em>u</em><sub>0</sub>) ve "
    "<em>C</em><sub>2</sub> (<em>v</em> = <em>v</em><sub>0</sub>) koordinat eğrilerinin teğet vektörleri "
    "<b>r</b><sub><em>v</em></sub> ve <b>r</b><sub><em>u</em></sub>'dur. Bu iki vektörü içeren düzlem "
    "teğet düzlemdir (gri); <b>r</b><sub><em>u</em></sub> &#215; <b>r</b><sub><em>v</em></sub> ona diktir.",
    aria="A curved surface S with the grid curves C1 and C2 through the point P0, the tangent vectors "
         "r_u along C2 and r_v along C1, the grey tangent plane spanned by them and the normal vector "
         "r_u x r_v"))

# ============================================================
# yama: grid on the rectangle D, cell R_ij -> patch S_ij, parallelogram of du r_u*, dv r_v*
# ============================================================
NU, NV = 4, 3
DU, DV = 3.0 / NU, 2.0 / NV
IC, JC = 2, 1
ui, vj = IC * DU, JC * DV
pl = eq_plot(50, 46, 74, (-0.25, 3.4), (-0.25, 2.35))
pl.origin_axes(it("u"), it("v"), opacity=0.5)
pl.label(0, 0, "0", -7, 14, TEXT, 11, "end")
pl.polygon([(0, 0), (3, 0), (3, 2), (0, 2)], TEXT, 0.07, TEXT, 1.2)
for k in range(1, NU):
    pl.line([(k * DU, 0), (k * DU, 2)], TEXT, 0.8, None, 0.45)
for k in range(1, NV):
    pl.line([(0, k * DV), (3, k * DV)], TEXT, 0.8, None, 0.45)
pl.polygon([(ui, vj), (ui + DU, vj), (ui + DU, vj + DV), (ui, vj + DV)], PRACTICE, 0.28, PRACTICE, 1.6)
dot(pl, (ui, vj), TEXT, 3.6)
pl.label(ui + DU / 2, vj + DV / 2, it("R") + sub(it("ij")), 0, 5, PRACTICE, 12.5, "middle", True)
plabel(pl, ui, vj, "(" + it("u") + sub(it("i")) + sup("*") + ", " + it("v") + sub(it("j")) + sup("*") + ")",
       -4, 18, TEXT, 11, "end")
pl.label(ui + DU / 2, 2.0, DELTA + it("u"), 0, -8, TEXT, 11.5, "middle")
pl.line([(ui, 2.0), (ui, 2.12)], TEXT, 1.0, None, 0.7)
pl.line([(ui + DU, 2.0), (ui + DU, 2.12)], TEXT, 1.0, None, 0.7)
pl.label(3.0, vj + DV / 2, DELTA + it("v"), 8, 4, TEXT, 11.5, "start")
pl.label(0.35, 1.75, it("D"), 0, 0, TEXT, 15, "middle", True)

cam = Camera(azimuth=35.0, elevation=22.0)
PIJ = shell(ui, vj)
ru, rv = deriv(shell, ui, vj)
A_ = vscale(DU, ru)
B_ = vscale(DV, rv)
para = [PIJ, vadd(PIJ, A_), vadd(vadd(PIJ, A_), B_), vadd(PIJ, B_)]
pr, S = fit_space(cam, sheet + para + [(0, 0, 0), (2.6, 0, 0), (0, 4.0, 0), (0, 0, 3.4)], 360, 30, 74, 0.25)
S.axes(2.6, 4.0, 3.4)
S.label((0, 0, 0), "0", -8, 4, TEXT, 11, "end")
S.surface(shell, (0.0, 3.0), (0.0, 2.0), nu=12, nv=8, fill=THEORY, stroke=THEORY,
          opacity=(0.06, 0.22), stroke_width=0.3, stroke_opacity=0.0)
for k in range(NU + 1):
    S.curve(lambda t, k=k: shell(k * DU, t), 0.0, 2.0, THEORY, 0.8, 40, None, 0.6)
for k in range(NV + 1):
    S.curve(lambda t, k=k: shell(t, k * DV), 0.0, 3.0, THEORY, 0.8, 60, None, 0.6)
ns = 16
edge = ([(ui + DU * k / ns, vj) for k in range(ns + 1)] + [(ui + DU, vj + DV * k / ns) for k in range(1, ns + 1)]
        + [(ui + DU - DU * k / ns, vj + DV) for k in range(1, ns + 1)] + [(ui, vj + DV - DV * k / ns)
                                                                           for k in range(1, ns)])
S.polygon([shell(a, b) for a, b in edge], THEORY, 0.38, THEORY, 1.5)
S.polygon(para, PRACTICE, 0.22, PRACTICE, 1.2)
S.arrow(PIJ, vadd(PIJ, A_), PRACTICE, 2.2, 8.5)
S.arrow(PIJ, vadd(PIJ, B_), PRACTICE, 2.2, 8.5)
S.point(PIJ, TEXT, 3.8)
splabel(S, PIJ, it("P") + sub(it("ij")), -8, 16, TEXT, 12, "end", True)
splabel(S, vadd(PIJ, A_), DELTA + it("u") + " " + RU + sup("*"), 4, 18, PRACTICE, 12, "start", True)
splabel(S, vadd(PIJ, B_), DELTA + it("v") + " " + RV + sup("*"), -8, -8, PRACTICE, 12, "end", True)
S.label(shell(ui + DU, vj + DV), it("S") + sub(it("ij")), 8, -6, THEORY, 12.5, "start", True)
S.label(shell(3.0, 0.0), it("S"), 10, 6, THEORY, 15, "start", True)
W, H = int(pr.x0 + pr.w + 30), int(max(pl.y0 + pl.h, pr.y0 + pr.h) + 24)
q = connector(W, H, pl.x0 + pl.w + 22, pr.x0 + 80, pl.Y(1.0), R_B)
save("yama", figure(
    W, H, [pl, pr, q],
    "<em>D</em> dikdörtgeni <em>&#916;u</em> &#215; <em>&#916;v</em> boyutlu alt dikdörtgenlere bölünür. "
    "<em>R<sub>ij</sub></em>'nin görüntüsü <em>S<sub>ij</sub></em> yamasıdır (koyu). Yama, "
    "<em>P<sub>ij</sub></em> köşesinden çıkan <em>&#916;u</em> <b>r</b><sub><em>u</em></sub><sup>*</sup> "
    "ve <em>&#916;v</em> <b>r</b><sub><em>v</em></sub><sup>*</sup> vektörlerinin gerdiği paralelkenarla "
    "(turuncu) yaklaşık olarak aynı alana sahiptir.",
    WIDE,
    aria="Left: the rectangle D in the uv-plane divided into a 4 by 3 grid with one cell R_ij shaded and "
         "its lower left corner marked. Right: the surface S with the image grid, the patch S_ij and the "
         "parallelogram spanned by du r_u star and dv r_v star at its corner P_ij"))
