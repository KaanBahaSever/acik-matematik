# -*- coding: utf-8 -*-
"""
Figures of the chapter "Eğrisel İntegraller"
(dersler/integral-calculus/egrisel-integraller.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box and never directly under a heading.
Concept figures stay visible: `bolunus` sits in the prose before the
definition of the line integral with respect to arc length, `cit` in the
prose on the fence interpretation, `yol-farki` in the prose after the two
paths of the same endpoints and `is` in the prose before the definition of
work; `helis`, `ceyrek` and `kubik` sit under the question text of their
examples, and `isaret` under the question text of its exercise.
The figures are NOT produced at build time. Run

    python scripts/calculus_figures/egi.py
    python scripts/center_figures.py "calculus-egi-*.md"
    python scripts/check_figure_labels.py "scripts/_figures/calculus-egi-*.md"

and paste the markup of scripts/_figures/calculus-egi-<name>.md into the .qmd.
Captions are Turkish on purpose; aria labels are plain ASCII.
"""
import html
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, dot, TEXT, THEORY, PRACTICE, BASE, BG  # noqa: E402
from svg_plot3 import Camera, Space, vadd, vsub, vscale, vdot  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "calculus-egi-"

MINUS = "&#8722;"
ZWSP = chr(0x200B)
PI = math.pi


def save(name, markup):
    (OUT_DIR / f"{PREFIX}{name}.md").write_text(markup, encoding="utf-8", newline="\n")
    print(f"{PREFIX}{name}.md")


def it(s):
    """Italic run inside an SVG <text>."""
    return f'<tspan font-style="italic">{s}</tspan>'


def bf(s):
    """Bold upright run (vectors) inside an SVG <text>."""
    return f'<tspan font-weight="700">{s}</tspan>'


def sub(s, size=8.5):
    """Subscript inside an SVG <text>."""
    return f'<tspan font-size="{size}" dy="3.5">{s}</tspan><tspan dy="-3.5">&#8203;</tspan>'


def sup(s, size=8.5):
    """Superscript inside an SVG <text>."""
    return f'<tspan font-size="{size}" dy="-5">{s}</tspan><tspan dy="5">&#8203;</tspan>'


def subsup(base, lo, hi, size=8.5):
    """base with a subscript and a superscript stacked at the same x (P_i^*)."""
    return (f'{base}<tspan font-size="{size}" dy="-5">{hi}</tspan>'
            f'<tspan font-size="{size}" dx="-4" dy="8.5">{lo}</tspan><tspan dy="-3.5">&#8203;</tspan>')


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
    """Rough advance width of a label (0.43 em per visible character)."""
    def count(t):
        return len(html.unescape(re.sub(r"<[^>]+>", "", t)).replace(ZWSP, ""))
    width = 0.0
    for m in re.finditer(r'<tspan font-size="([\d.]+)"[^>]*>(.*?)</tspan>', s):
        width += count(m.group(2)) * 0.43 * float(m.group(1))
    rest = re.sub(r'<tspan font-size="[\d.]+"[^>]*>.*?</tspan>', "", s)
    return width + count(rest) * 0.43 * size


def plabel(p, x, y, s, dx=0, dy=0, color=TEXT, size=11.5, anchor="start", bold=False):
    """Label on a page-coloured plate, for text that must sit on a filled region."""
    px, py = p.X(x) + dx, p.Y(y) + dy
    w = text_w(s, size)
    x0 = px - (w / 2 if anchor == "middle" else w if anchor == "end" else 0)
    p.add(f'<rect x="{x0 - 2.5:.1f}" y="{py - 0.8 * size - 1:.1f}" width="{w + 5:.1f}" '
          f'height="{size + 3:.1f}" rx="3" fill="{BG}" opacity="0.85"/>')
    p.label(x, y, s, dx, dy, color, size, anchor, bold)


def splabel(S, P, s, dx=0, dy=0, color=TEXT, size=11.5, anchor="start", bold=False):
    X, Y = S.pt(P)
    plabel(S.p, X, Y, s, dx, dy, color, size, anchor, bold)


def catmull(knots, u):
    """Uniform Catmull-Rom spline through the knots; u runs from 0 to len(knots) - 1."""
    n = len(knots) - 1
    u = min(max(u, 0.0), n)
    i = min(int(u), n - 1)
    s = u - i
    p0 = knots[max(i - 1, 0)]
    p1, p2 = knots[i], knots[i + 1]
    p3 = knots[min(i + 2, n)]
    out = []
    for c in range(2):
        a0 = p1[c]
        a1 = 0.5 * (p2[c] - p0[c])
        a2 = 0.5 * (2 * p0[c] - 5 * p1[c] + 4 * p2[c] - p3[c])
        a3 = 0.5 * (-p0[c] + 3 * p1[c] - 3 * p2[c] + p3[c])
        out.append(a0 + a1 * s + a2 * s * s + a3 * s * s * s)
    return tuple(out)


def samples(f, t0, t1, n=200):
    return [f(t0 + (t1 - t0) * k / n) for k in range(n + 1)]


def arrow_on(p, f, t, dt, color, width=2.0, head=9.0):
    """Arrowhead on the plane curve f at parameter t, pointing in the direction of travel."""
    p.arrow(f(t - dt), f(t + dt), color, width, head)


def unit2(v):
    n = math.hypot(*v)
    return (v[0] / n, v[1] / n)


def axes2d(p, xr, yr, xl="x", yl="y", opacity=0.5):
    """Coordinate axes through the origin, drawn only over xr and yr (not the whole panel)."""
    p.arrow((xr[0], 0), (xr[1], 0), TEXT, 1.1, 8.0, None, opacity)
    p.arrow((0, yr[0]), (0, yr[1]), TEXT, 1.1, 8.0, None, opacity)
    p.label(xr[1], 0, it(xl), -2, 16, TEXT, 12.5, "end")
    p.label(0, yr[1], it(yl), 8, 8, TEXT, 12.5)


def mfmt(v):
    """Tick label with a real minus sign."""
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return s.replace("-", MINUS)


TI = it("t")
SUBI = it("i")
SUBIM = it("i") + MINUS + "1"
SB = 10.0                             # sub/superscript size of the figures shown at reduced scale

# ============================================================
# bolunus: the parameter interval and the n subarcs of C
# ============================================================
KN = [(1.0, 1.35), (0.75, 2.65), (1.6, 3.55), (3.0, 3.95), (4.3, 3.6), (4.75, 2.7), (4.1, 1.95),
      (4.6, 1.3), (5.8, 1.55), (6.55, 2.4)]
NK = len(KN) - 1                      # 9 subarcs
IH = 4                                # the highlighted subarc runs from knot IH-1 to knot IH
US = IH - 0.55                        # parameter of the sample point
TA, TB, TY = 1.0, 6.55, -1.15         # the parameter axis


def rb(u):
    return catmull(KN, u)


def tpos(u):
    return (TA + (TB - TA) * u / NK, TY)


p = eq_plot(40, 30, 54, (-0.45, 7.35), (-2.1, 4.55))
axes2d(p, (-0.45, 7.35), (-0.4, 4.55))
p.label(0, 0, "0", -6, 14, TEXT, 12, "end")
# the curve and the highlighted subarc
p.line(samples(rb, 0, NK, 360), THEORY, 2.0)
p.line(samples(rb, IH - 1, IH, 60), PRACTICE, 3.6)
arrow_on(p, rb, 8.45, 0.06, THEORY)
for k in range(NK + 1):
    dot(p, rb(k), THEORY, 3.4)
Ps = rb(US)
dot(p, Ps, PRACTICE, 4.4)
p.label(*rb(0), it("P") + sub("0", SB), 9, 6, THEORY, 12.5)
p.label(*rb(1), it("P") + sub("1", SB), -9, 4, THEORY, 12.5, "end")
p.label(*rb(2), it("P") + sub("2", SB), -8, -6, THEORY, 12.5, "end")
p.label(*rb(IH - 1), it("P") + sub(SUBIM, SB), -6, -10, THEORY, 12.5, "end")
p.label(*rb(IH), it("P") + sub(SUBI, SB), 9, -6, THEORY, 12.5)
p.label(*rb(NK), it("P") + sub(it("n"), SB), 8, -4, THEORY, 12.5)
p.label(*Ps, subsup(it("P"), SUBI, "*", SB), 0, -12, PRACTICE, 13, "middle", True)
p.label(*rb(IH - 0.5), "Δ" + it("s") + sub(SUBI, SB), 1, 24, PRACTICE, 13, "start", True)
p.label(*rb(6.6), it("C"), -12, 6, THEORY, 14.5, "end", True)
# the parameter interval [a, b]
p.line([(TA, TY), (TB, TY)], TEXT, 1.3, None, 0.7)
for k in range(NK + 1):
    dot(p, tpos(k), TEXT, 2.6)
p.arrow((TB, TY), (TB + 0.55, TY), TEXT, 1.1, 7.0, None, 0.6)
p.label(TB + 0.55, TY, TI, 0, 16, TEXT, 12.5, "end")
p.label(TA, TY, it("a"), 0, 18, TEXT, 12.5, "middle")
p.label(TB, TY, it("b"), 0, 18, TEXT, 12.5, "middle")
p.label(*tpos(IH - 1), it("t") + sub(SUBIM, SB), -4, 19, TEXT, 12.5, "middle")
p.label(*tpos(IH), it("t") + sub(SUBI, SB), 4, 19, TEXT, 12.5, "middle")
dot(p, tpos(US), PRACTICE, 3.6)
p.label(*tpos(US), subsup(it("t"), SUBI, "*", SB), 0, -9, PRACTICE, 12.5, "middle", True)
# the map t -> r(t) for the three marked parameters
for u, col, op, lift in ((IH - 1, TEXT, 0.45, 0.12), (IH, TEXT, 0.45, 0.12), (US, PRACTICE, 0.9, 0.62)):
    a0 = tpos(u)
    a1 = rb(u)
    d = unit2((a1[0] - a0[0], a1[1] - a0[1]))
    a1 = (a1[0] - 0.13 * d[0], a1[1] - 0.13 * d[1])
    p.arrow((a0[0], a0[1] + lift), a1, col, 1.1, 7.0, "4 3", op)
save("bolunus", figure(
    int(p.x0 + p.w + 30), int(p.y0 + p.h + 30), [p],
    "[<em>a</em>, <em>b</em>] parametre aralığı <em>n</em> eşit parçaya bölününce <em>C</em> eğrisi de "
    "<em>P</em><sub>0</sub>, <em>P</em><sub>1</sub>, …, <em>P<sub>n</sub></em> noktalarıyla <em>n</em> alt yaya "
    "bölünür; <em>P<sub>i</sub></em> = <b>r</b>(<em>t<sub>i</sub></em>) olur. <em>i</em>-inci alt yayın uzunluğu "
    "Δ<em>s<sub>i</sub></em>, üzerinden seçilen nokta <em>P<sub>i</sub></em>* = <b>r</b>(<em>t<sub>i</sub></em>*) "
    "noktasıdır.",
    aria="A plane curve C divided into subarcs by points P0, P1, ..., Pn; the subarc from P(i-1) to Pi "
         "is highlighted with its length delta s_i and a sample point Pi*; below, the parameter interval "
         "[a, b] with t(i-1), ti* and ti, and dashed arrows from these parameters to their points on C"))

# ============================================================
# cit: the line integral of f >= 0 as the area of a fence
# ============================================================


def cb(s):
    """Base curve C in the xy-plane."""
    return (1.6 + 0.9 * math.sin(1.8 * PI * s), 0.4 + 3.2 * s)


def fh(x, y):
    return 1.3 + 0.6 * math.sin(1.4 * y) + 0.2 * x


cam = Camera(azimuth=32.0, elevation=24.0)
box = [(0, 0, 0), (3.0, 0, 0), (0, 4.4, 0), (0, 0, 3.0), (2.6, 0.4, 0), (2.6, 3.6, 0), (2.6, 0.4, 2.6),
       (0.7, 3.6, 2.4)]
pl, S = fit_space(cam, box, 40, 30, 70, 0.3)
S.axes(3.0, 4.4, 3.0, size=12.5)
S.label((0, 0, 0), "0", -8, 4, TEXT, 12, "end")
NS = 120
pts = [cb(k / NS) for k in range(NS + 1)]
quads = []
for k in range(NS):
    (x0, y0), (x1, y1) = pts[k], pts[k + 1]
    q = [(x0, y0, 0.0), (x1, y1, 0.0), (x1, y1, fh(x1, y1)), (x0, y0, fh(x0, y0))]
    quads.append((sum(S.depth(P) for P in q) / 4, q))
quads.sort(key=lambda z: z[0])
for _, q in quads:
    S.polygon(q, THEORY, 0.16)
for k in range(0, NS + 1, 5):
    x, y = pts[k]
    S.line([(x, y, 0), (x, y, fh(x, y))], THEORY, 0.8, None, 0.45)
S.curve(lambda s: (*cb(s), fh(*cb(s))), 0, 1, THEORY, 1.8, 200)
S.curve(lambda s: (*cb(s), 0.0), 0, 1, BASE, 2.6, 200)
# one Riemann strip: base subarc of length delta s_i, flat top at f(P_i*)
S0, S1 = 0.50, 0.565
SM = (S0 + S1) / 2
xs, ys = cb(SM)
hs = fh(xs, ys)
strip = [(*cb(S0 + (S1 - S0) * j / 8), 0.0) for j in range(9)]
top = [(P[0], P[1], hs) for P in strip]
S.polygon(strip + top[::-1], PRACTICE, 0.42)
S.line(top, PRACTICE, 2.0)
S.line([strip[0], top[0]], PRACTICE, 1.4)
S.line([strip[-1], top[-1]], PRACTICE, 1.4)
S.line(strip, PRACTICE, 3.2)
S.point((xs, ys, 0), PRACTICE, 3.6)
splabel(S, (xs, ys, 0), subsup(it("P"), it("i"), "*", SB), 12, 14, PRACTICE, 12.5, "start", True)
splabel(S, top[-1], it("f") + "(" + subsup(it("P"), it("i"), "*", SB) + ")", 8, 2, PRACTICE, 12.5, "start", True)
splabel(S, strip[0], "Δ" + it("s") + sub(it("i"), SB), -10, 14, PRACTICE, 12.5, "end", True)
splabel(S, (*cb(0.97), 0.0), it("C"), 4, 18, BASE, 14.5, "start", True)
splabel(S, (*cb(0.14), fh(*cb(0.14))), it("z") + " = " + it("f") + "(" + it("x") + ", " + it("y") + ")",
        -6, -10, THEORY, 12.5, "end")
save("cit", figure(
    int(pl.x0 + pl.w + 40), int(pl.y0 + pl.h + 30), [pl],
    "<em>f</em> &#8805; 0 iken ∫<sub><em>C</em></sub> <em>f</em> <em>ds</em>, tabanı <em>xy</em>-düzlemindeki "
    "<em>C</em> eğrisi ve (<em>x</em>, <em>y</em>) noktasındaki yüksekliği <em>f</em>(<em>x</em>, <em>y</em>) olan "
    "perdenin bir yüzünün alanıdır. Turuncu şeridin alanı <em>f</em>(<em>P<sub>i</sub></em>*)&#8201;Δ<em>s<sub>i</sub></em> "
    "çarpımıdır; bu şeritlerin toplamı Riemann toplamını verir.",
    aria="A curve C in the xy-plane and the vertical fence over it whose height at (x, y) is f(x, y); "
         "one thin strip over a subarc of length delta s_i is highlighted with flat top at height f(Pi*)"))

# ============================================================
# yol-farki: two paths from (-5, -3) to (0, 2)
# ============================================================
p = eq_plot(40, 30, 44, (-6.4, 5.4), (-4.2, 3.3))
p.origin_axes(it("x"), it("y"), xticks=(-5,), yticks=(-3,), xfmt=mfmt, yfmt=mfmt)
p.label(0, 0, "0", -6, 14, TEXT, 11, "end")


def c1(t):
    return (5 * t - 5, 5 * t - 3)


def c2(y):
    return (4 - y * y, y)


p.line(samples(c1, 0, 1, 20), PRACTICE, 2.4)
p.line(samples(c2, -3, 2, 200), THEORY, 2.4)
arrow_on(p, c1, 0.42, 0.03, PRACTICE, 2.4)
arrow_on(p, c2, -1.3, 0.05, THEORY, 2.4)
arrow_on(p, c2, 1.35, 0.05, THEORY, 2.4)
dot(p, (-5, -3), TEXT, 4.2)
dot(p, (0, 2), TEXT, 4.2)
p.label(-5, -3, "(" + MINUS + "5, " + MINUS + "3)", -4, 18, TEXT, 12, "middle")
p.label(0, 2, "(0, 2)", -8, -8, TEXT, 12, "end")
p.label(*c1(0.62), it("C") + sub("1"), -12, -6, PRACTICE, 14, "end", True)
p.label(*c2(1.0), it("C") + sub("2"), 8, -10, THEORY, 14, "start", True)
p.label(*c2(-1.9), it("x") + " = 4 " + MINUS + " " + it("y") + "²", 12, 10, THEORY, 12.5)
dot(p, (4, 0), THEORY, 3.0)
p.label(4, 0, "(4, 0)", 8, 16, THEORY, 11.5)
save("yol-farki", figure(
    int(p.x0 + p.w + 30), int(p.y0 + p.h + 30), [p],
    "(" + MINUS + "5, " + MINUS + "3) noktasından (0, 2) noktasına giden iki yol: <em>C</em><sub>1</sub> doğru parçası "
    "ve <em>C</em><sub>2</sub>: <em>x</em> = 4 " + MINUS + " <em>y</em>² parabol yayı. Uç noktalar aynı olduğu hâlde "
    "∫ <em>y</em>² <em>dx</em> + <em>x</em> <em>dy</em> integrali <em>C</em><sub>1</sub> boyunca " + MINUS + "5/6, "
    "<em>C</em><sub>2</sub> boyunca 245/6 olur.",
    aria="The line segment C1 and the parabolic arc C2: x = 4 - y^2, both running from (-5, -3) to (0, 2), "
         "with arrows showing the direction of travel"))

# ============================================================
# helis: the circular helix x = cos t, y = sin t, z = t
# ============================================================
cam = Camera(azimuth=28.0, elevation=18.0)
ZT = 2 * PI
# the z axis is drawn at KZ times the scale of x and y (stated in the caption), otherwise one turn
# of radius 1 rising by 2 pi makes a drawing two and a half times as tall as it is wide
KZ = 0.36
ZD = KZ * ZT
box = [(1.0, 1.0, 0), (-1.0, -1.0, 0), (1, -1, 0), (-1, 1, 0), (0, 0, ZD + 0.75), (1.8, 0, 0), (0, 1.8, 0),
       (1, 1, ZD), (-1, -1, ZD)]
pl, S = fit_space(cam, box, 40, 30, 125, 0.4)


def hx(t):
    return (math.cos(t), math.sin(t), KZ * t)


# faint cylinder x^2 + y^2 = 1: bottom and top circles and the two silhouette lines
d = S.cam.d
for z in (0.0, ZD):
    S.circle((0, 0, z), (1, 0, 0), (0, 1, 0), 1.0, TEXT, 0.9, "4 3", 96, 0.4)
sil = math.atan2(d[1], d[0]) + PI / 2
for a in (sil, sil + PI):
    S.line([(math.cos(a), math.sin(a), 0), (math.cos(a), math.sin(a), ZD)], TEXT, 0.9, "4 3", 0.4)
S.axes(1.8, 1.8, ZD + 0.75, labels=("x", "y", "z"))
S.ticks("z", (KZ * 2, KZ * 4), fmt_=lambda v: mfmt(v / KZ))
# the helix: the half turned away from the viewer is drawn lighter
N = 480
seg, cur_front = [], None
for k in range(N + 1):
    t = ZT * k / N
    P = hx(t)
    front = vdot((P[0], P[1], 0.0), d) >= 0
    if cur_front is None or front == cur_front:
        seg.append(P)
    else:
        seg.append(P)
        S.line(seg, PRACTICE, 2.4 if cur_front else 1.6, None, 1.0 if cur_front else 0.45)
        seg = [P]
    cur_front = front
S.line(seg, PRACTICE, 2.4 if cur_front else 1.6, None, 1.0 if cur_front else 0.45)
for t0 in (1.2, 4.7):
    S.arrow(hx(t0 - 0.05), hx(t0 + 0.05), PRACTICE, 2.4, 9.0)
S.point(hx(0), PRACTICE, 4.0)
S.point(hx(ZT), PRACTICE, 4.0)
splabel(S, hx(0), "(1, 0, 0)", 12, 14, PRACTICE, 12, "start")
splabel(S, hx(ZT), "(1, 0, 2" + it("π") + ")", 10, -8, PRACTICE, 12, "start")
splabel(S, hx(1.0), it("C"), -12, -10, PRACTICE, 13.5, "end", True)
save("helis", figure(
    int(pl.x0 + pl.w + 40), int(pl.y0 + pl.h + 30), [pl],
    "<em>x</em> = cos <em>t</em>, <em>y</em> = sin <em>t</em>, <em>z</em> = <em>t</em> (0 &#8804; <em>t</em> &#8804; "
    "2<em>π</em>) dairesel helisi <em>x</em>² + <em>y</em>² = 1 silindirinin üzerinde bir tam tur atarak (1, 0, 0) "
    "noktasından (1, 0, 2<em>π</em>) noktasına çıkar. Silindirin arka yüzündeki kısmı soluk çizilmiştir; "
    "şekil fazla uzamasın diye <em>z</em> ekseni kısaltılmış ölçekle çizilmiştir.",
    aria="Circular helix x = cos t, y = sin t, z = t for t from 0 to 2 pi on the dashed cylinder of radius 1, "
         "rising from (1, 0, 0) to (1, 0, 2 pi) with arrows in the direction of increasing t"))

# ============================================================
# is: work element F . T delta s on a subarc
# ============================================================
# a valley-shaped curve: near the sample point it lies above its tangent line,
# so the measure of F . T fits below the tangent line in empty space
KW = [(0.2, 3.0), (1.1, 1.75), (2.4, 0.95), (3.9, 0.95), (5.2, 1.75), (6.2, 3.0)]
UA, UB, UM = 2.42, 3.06, 2.74


def rw(u):
    return catmull(KW, u)


p = eq_plot(40, 30, 76, (-0.2, 6.6), (-0.6, 4.6))
p.line(samples(rw, 0, len(KW) - 1, 300), THEORY, 2.0)
p.line(samples(rw, UA, UB, 60), PRACTICE, 3.6)
arrow_on(p, rw, 4.35, 0.05, THEORY)
P0, P1, PM = rw(UA), rw(UB), rw(UM)
h = 1e-4
T = unit2((rw(UM + h)[0] - rw(UM - h)[0], rw(UM + h)[1] - rw(UM - h)[1]))
NRM = (-T[1], T[0])                     # left normal (upward here)
ANG = math.radians(55)
FL = 2.4
Fv = (FL * (math.cos(ANG) * T[0] - math.sin(ANG) * T[1]), FL * (math.sin(ANG) * T[0] + math.cos(ANG) * T[1]))
FT = Fv[0] * T[0] + Fv[1] * T[1]        # tangential component
tip = (PM[0] + Fv[0], PM[1] + Fv[1])
foot = (PM[0] + FT * T[0], PM[1] + FT * T[1])
# tangent line, the drop from the tip of F with its right-angle mark
p.line([(PM[0] - 1.2 * T[0], PM[1] - 1.2 * T[1]), (PM[0] + 2.1 * T[0], PM[1] + 2.1 * T[1])], TEXT, 1.0, "4 3", 0.55)
p.line([tip, foot], TEXT, 1.0, "4 3", 0.7)
sq = 0.12
p.line([(foot[0] - sq * T[0], foot[1] - sq * T[1]),
        (foot[0] - sq * T[0] + sq * NRM[0], foot[1] - sq * T[1] + sq * NRM[1]),
        (foot[0] + sq * NRM[0], foot[1] + sq * NRM[1])], TEXT, 0.9, None, 0.7)
# the length F . T, measured below the tangent line
off = -0.34
m0 = (PM[0] + off * NRM[0], PM[1] + off * NRM[1])
m1 = (foot[0] + off * NRM[0], foot[1] + off * NRM[1])
p.line([m0, m1], PRACTICE, 1.6)
for m in (m0, m1):
    p.line([(m[0] - 0.09 * NRM[0], m[1] - 0.09 * NRM[1]), (m[0] + 0.09 * NRM[0], m[1] + 0.09 * NRM[1])],
           PRACTICE, 1.6)
for m, q in ((m0, PM), (m1, foot)):
    p.line([q, m], PRACTICE, 0.8, "2 3", 0.6)
mid = ((m0[0] + m1[0]) / 2, (m0[1] + m1[1]) / 2)
p.label(*mid, bf("F") + " · " + bf("T"), 6, 20, PRACTICE, 12.5, "middle", True)
# vectors
p.arrow(PM, tip, THEORY, 2.4, 10.0)
p.arrow(PM, (PM[0] + T[0], PM[1] + T[1]), BASE, 2.8, 10.0)
# angle between T and F
th0 = math.atan2(T[1], T[0])
p.arc(PM[0], PM[1], 0.5, th0, th0 + ANG, TEXT, 1.1, None, 0.8)
p.label(PM[0] + 0.68 * math.cos(th0 + ANG / 2), PM[1] + 0.68 * math.sin(th0 + ANG / 2), it("θ"),
        0, 5, TEXT, 12.5, "middle")
dot(p, PM, PRACTICE, 4.4)
p.label(*P0, "Δ" + it("s") + sub(SUBI), -10, -8, PRACTICE, 12.5, "end", True)
p.label(*PM, subsup(it("P"), SUBI, "*"), -10, 20, PRACTICE, 12.5, "end", True)
p.label(*tip, bf("F") + "(" + subsup(it("P"), SUBI, "*") + ")", 8, 2, THEORY, 12.5, "start", True)
TT = (PM[0] + T[0], PM[1] + T[1])
p.label(*TT, bf("T"), -2, -12, BASE, 13, "middle", True)
p.label(*rw(4.75), it("C"), 10, 4, THEORY, 14, "start", True)
save("is", figure(
    int(p.x0 + p.w + 30), int(p.y0 + p.h + 30), [p],
    "Parçacık turuncu alt yayı geçerken yaklaşık <b>T</b> birim teğet vektörü yönünde Δ<em>s<sub>i</sub></em> "
    "kadar ilerler. <b>F</b>'nin bu yöndeki bileşeni <b>F</b> · <b>T</b> = |<b>F</b>| cos <em>θ</em>, yani "
    "<b>F</b>'nin teğet doğrusu üzerindeki dik izdüşümünün uzunluğudur; bu parçada yapılan iş yaklaşık "
    "(<b>F</b> · <b>T</b>)&#8201;Δ<em>s<sub>i</sub></em> olur.",
    aria="A curve C with a short highlighted subarc of length delta s_i; at the sample point Pi* the force "
         "vector F and the unit tangent T make the angle theta, and the perpendicular projection of F onto "
         "the tangent line is measured below the line as F dot T"))

# ============================================================
# ceyrek: F = x^2 i - x y j along the quarter circle
# ============================================================
p = eq_plot(40, 30, 270, (-0.16, 1.4), (-0.16, 1.4))
p.origin_axes(it("x"), it("y"), xticks=(1,), yticks=(1,))
p.label(0, 0, "0", -6, 14, TEXT, 11, "end")
SC = 0.085
g = [0.1 + 0.2 * k for k in range(7)]
for x in g:
    for y in g:
        Fx, Fy = x * x, -x * y
        L = math.hypot(Fx, Fy) * SC
        if L < 0.012:
            dot(p, (x, y), THEORY, 1.4)
            continue
        p.arrow((x, y), (x + SC * Fx, y + SC * Fy), THEORY, 1.4, min(7.0, 0.45 * L * 270 + 2), None, 0.85)


def qc(t):
    return (math.cos(t), math.sin(t))


p.line(samples(qc, 0, PI / 2, 120), PRACTICE, 2.8)
arrow_on(p, qc, 0.55, 0.03, PRACTICE, 2.8, 11.0)
arrow_on(p, qc, 1.25, 0.03, PRACTICE, 2.8, 11.0)
dot(p, (1, 0), PRACTICE, 4.2)
dot(p, (0, 1), PRACTICE, 4.2)
plabel(p, *qc(0.95), it("C"), -12, 4, PRACTICE, 14, "end", True)
save("ceyrek", figure(
    int(p.x0 + p.w + 30), int(p.y0 + p.h + 30), [p],
    "<b>F</b>(<em>x</em>, <em>y</em>) = <em>x</em>² <b>i</b> &#8722; <em>xy</em> <b>j</b> kuvvet alanı ve (1, 0) "
    "noktasından (0, 1) noktasına giden çeyrek çember <em>C</em>. Oklar eğri boyunca hareketle geniş açı yapar, "
    "yani alan hareketi engeller; bu yüzden yapılan iş negatiftir.",
    aria="Arrows of the vector field F = x^2 i - x y j on a grid in the first quadrant, pointing right and "
         "down, and the quarter circle from (1, 0) to (0, 1) traversed counterclockwise"))

# ============================================================
# kubik: the twisted cubic and F(r(t)) at t = 1/2, 3/4, 1
# ============================================================
cam = Camera(azimuth=-30.0, elevation=20.0)
box = [(0, 0, 0), (1.6, 0, 0), (0, 2.3, 0), (0, 0, 2.3), (2, 2, 2), (1, 1, 0), (1.2, 0, 1.2)]
pl, S = fit_space(cam, box, 40, 30, 118, 0.25)
S.axes(1.6, 2.3, 2.3)
S.label((0, 0, 0), "0", -8, 4, TEXT, 11, "end")
S.ticks("x", (1,), size=11)
S.ticks("y", (1, 2), size=11)
S.ticks("z", (1, 2), size=11)
# the unit cube as a reference frame
for a_, b_ in (((1, 0, 0), (1, 1, 0)), ((0, 1, 0), (1, 1, 0)), ((1, 1, 0), (1, 1, 1)), ((0, 0, 1), (1, 0, 1)),
               ((0, 0, 1), (0, 1, 1)), ((1, 0, 1), (1, 1, 1)), ((0, 1, 1), (1, 1, 1)), ((1, 0, 0), (1, 0, 1)),
               ((0, 1, 0), (0, 1, 1))):
    S.line([a_, b_], TEXT, 0.8, "4 3", 0.4)
S.curve(lambda t: (t, t * t, t ** 3), 0, 1, PRACTICE, 2.6, 200)
S.arrow((0.36, 0.36 ** 2, 0.36 ** 3), (0.40, 0.16, 0.064), PRACTICE, 2.6, 9.0)
for tv, lab, dx, dy, anc in ((0.5, "1/2", 6, 22, "start"), (0.75, "3/4", -16, -6, "end"), (1.0, "1", 8, 2, "start")):
    P = (tv, tv * tv, tv ** 3)
    Fv3 = (P[0] * P[1], P[1] * P[2], P[2] * P[0])
    S.arrow(P, vadd(P, Fv3), THEORY, 2.2, 9.0)
    S.point(P, PRACTICE, 3.6)
    splabel(S, vadd(P, Fv3), bf("F") + "(" + bf("r") + "(" + lab + "))", dx, dy, THEORY, 12.5, anc)
splabel(S, (1, 1, 1), "(1, 1, 1)", 10, 14, PRACTICE, 12)
splabel(S, (0.75, 0.75 ** 2, 0.75 ** 3), it("C"), -14, 0, PRACTICE, 14, "end", True)
save("kubik", figure(
    int(pl.x0 + pl.w + 40), int(pl.y0 + pl.h + 30), [pl],
    "<em>x</em> = <em>t</em>, <em>y</em> = <em>t</em>², <em>z</em> = <em>t</em>³ (0 &#8804; <em>t</em> &#8804; 1) "
    "kübik eğrisi ve <em>t</em> = 1/2, 3/4, 1 noktalarında <b>F</b> = <em>xy</em> <b>i</b> + <em>yz</em> <b>j</b> + "
    "<em>zx</em> <b>k</b> vektörleri (gerçek uzunluklarıyla). Kesikli çizgiler birim küpün kenarlarıdır.",
    aria="The twisted cubic r(t) = (t, t^2, t^3) from the origin to (1, 1, 1) inside the dashed unit cube, "
         "with the vectors F(r(t)) drawn at t = 1/2, 3/4 and 1"))

# ============================================================
# isaret: F = (x - y) i + x y j on three quarters of the circle of radius 2
# ============================================================
p = eq_plot(40, 30, 72, (-3.0, 3.0), (-3.0, 3.0))
p.origin_axes(it("x"), it("y"))
p.label(0, 0, "0", -6, 14, TEXT, 11, "end")
G = [-2.5 + 0.5 * k for k in range(11)]
FMAX = math.hypot(5.0, 6.25)
for x in G:
    for y in G:
        Fx, Fy = x - y, x * y
        m = math.hypot(Fx, Fy)
        if m < 1e-9:
            dot(p, (x, y), THEORY, 1.4)
            continue
        L = 0.43 * math.sqrt(m / FMAX)
        p.arrow((x, y), (x + L * Fx / m, y + L * Fy / m), THEORY, 1.2, min(6.5, 0.45 * L * 72 + 2), None, 0.75)


def c29(t):
    return (2 * math.cos(t), 2 * math.sin(t))


p.line(samples(c29, 1.5 * PI, 2 * PI, 60), TEXT, 1.0, "4 3", 0.45)
p.line(samples(c29, 0, 1.5 * PI, 240), PRACTICE, 2.8)
for t0 in (0.75, 2.35, 3.95):
    arrow_on(p, c29, t0, 0.02, PRACTICE, 2.8, 11.0)
dot(p, (2, 0), PRACTICE, 4.4)
dot(p, (0, -2), PRACTICE, 4.4)
plabel(p, 2, 0, "(2, 0)", 8, -8, PRACTICE, 12)
plabel(p, 0, -2, "(0, " + MINUS + "2)", 8, 18, PRACTICE, 12)
plabel(p, *c29(2.0), it("C"), -10, -6, PRACTICE, 14, "end", True)
save("isaret", figure(
    int(p.x0 + p.w + 30), int(p.y0 + p.h + 30), [p],
    "<b>F</b>(<em>x</em>, <em>y</em>) = (<em>x</em> &#8722; <em>y</em>) <b>i</b> + <em>xy</em> <b>j</b> alanı ve "
    "<em>x</em>² + <em>y</em>² = 4 çemberinin (2, 0) noktasından saat yönünün tersine (0, &#8722;2) noktasına "
    "giden <em>C</em> yayı. Okların yönü <b>F</b>'nin yönüdür; uzunlukları |<b>F</b>| ile artar ama okunaklı "
    "kalsın diye orantılı çizilmemiştir.",
    aria="Arrows of the vector field F = (x - y) i + x y j on a grid, and three quarters of the circle of "
         "radius 2 traversed counterclockwise from (2, 0) through (0, 2) and (-2, 0) to (0, -2); the "
         "remaining quarter is dashed"))
