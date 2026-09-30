# -*- coding: utf-8 -*-
"""
Figures of the chapter "Yönlü Türev ve Ortalama Değer Teoremi"
(dersler/analiz-4/yonlu-turev-ve-ortalama-deger-teoremi.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box and never directly under a heading.
The figures are NOT produced at build time. Run

    python scripts/analysis4_figures/yon.py
    python scripts/center_figures.py "analysis4-yon-*.md"
    python scripts/check_figure_labels.py "scripts/_figures/analysis4-yon-*.md"

and paste the markup of scripts/_figures/analysis4-yon-<name>.md into the .qmd.
The captions are Turkish on purpose; the aria labels are plain ASCII.

Conventions: a boundary that belongs to the set is solid, one that does not is
dashed; a point of the set is filled, a point outside it is hollow. The nabla
sign is missing from the renderer's fallback font, so it is drawn as a small
triangle path in front of the text (nabla_label).
"""
import html
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, closed_curve, dot, hollow, TEXT, THEORY, PRACTICE, BASE, BG  # noqa: E402
from svg_plot3 import Camera, Space  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "analysis4-yon-"

MINUS, THETA = "&#8722;", "&#952;"
ZWSP = "​"


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


def num(v):
    return f"{v:g}".replace("-", MINUS).replace(".", ",")


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


def plabel(p, x, y, s, dx=0, dy=0, color=TEXT, size=11.5, anchor="start", bold=False, opacity=0.88):
    """Label on a page-coloured plate, for text that sits on lines or on a meshed surface."""
    px, py = p.X(x) + dx, p.Y(y) + dy
    w = text_w(s, size)
    x0 = px - (w / 2 if anchor == "middle" else w if anchor == "end" else 0)
    p.add(f'<rect x="{x0 - 2.5:.1f}" y="{py - 0.8 * size - 1:.1f}" width="{w + 5:.1f}" '
          f'height="{size + 3:.1f}" rx="3" fill="{BG}" opacity="{opacity}"/>')
    p.label(x, y, s, dx, dy, color, size, anchor, bold)


def splabel(S, P, s, dx=0, dy=0, color=TEXT, size=11.5, anchor="start", bold=False):
    """plabel() at a space point."""
    X, Y = S.pt(P)
    plabel(S.p, X, Y, s, dx, dy, color, size, anchor, bold)


def nabla_label(p, x, y, rest, dx=0, dy=0, color=TEXT, size=12.5):
    """'nabla' + rest, left-aligned at data point (x, y) nudged by (dx, dy) pixels; the
    nabla is a drawn triangle as tall as a capital letter."""
    px, py = p.X(x) + dx, p.Y(y) + dy
    h, w = 0.68 * size, 0.62 * size
    p.add(f'<path d="M{px:.1f},{py - h:.1f} L{px + w:.1f},{py - h:.1f} L{px + w / 2:.1f},{py:.1f} Z" '
          f'fill="none" stroke="{color}" stroke-width="{0.085 * size:.2f}" stroke-linejoin="miter"/>')
    p.text_px(px + w + 0.12 * size, py, rest, color, size)


DU = it("D") + sub(it("u"))

# ============================================================
# kesit-egrisi: the vertical plane through (1, 1) along u = (-3/5, -4/5) cuts the paraboloid
# ============================================================


def fp(x, y):
    return 4 - x * x - 2 * y * y


def para(r, phi):
    """Elliptic polar coordinates: the base ellipse x^2 + 2y^2 = 4 is r = 1."""
    x, y = 2 * r * math.cos(phi), math.sqrt(2) * r * math.sin(phi)
    return (x, y, fp(x, y))


U = (-3 / 5, -4 / 5)


def on_line(t, z):
    return (1 + U[0] * t, 1 + U[1] * t, z)


def phi_(t):
    return 1 + 22 * t / 5 - 41 * t * t / 25


# the section runs from one rim of the z >= 0 part to the other: phi(t) = 0
DISC = math.sqrt(22 * 22 / 25 + 4 * 41 / 25)
T_LO, T_HI = (22 / 5 - DISC) / (2 * 41 / 25), (22 / 5 + DISC) / (2 * 41 / 25)   # -0.211, 2.894
PP = (1.0, 1.0, 1.0)
P0 = (1.0, 1.0, 0.0)
# azimuth 15 instead of 35: x still comes toward the viewer (down-left), but the plane along u is
# seen less obliquely, so the section parabola is not squeezed into a sliver
cam = Camera(azimuth=15.0, elevation=22.0)
TP0, TP1, ZTOP = -0.45, 3.1, 4.3
quad = [on_line(TP0, 0), on_line(TP1, 0), on_line(TP1, ZTOP), on_line(TP0, ZTOP)]
box = [(-2, -1.6, 0), (2, -1.6, 0), (-2, 1.6, 0), (2, 1.6, 0), (0, 0, 4.7), (2.6, 0, 0), (0, 2.2, 0)] + quad
pl, S = fit_space(cam, box, 60, 40, 84, 0.3)
S.axes(2.6, 2.2, 4.7, -2.0, -1.6, 0.0, offsets=((-4, 13), (10, 4), (0, -8)))
S.surface(para, (0, 1), (0, 2 * math.pi), nu=6, nv=24, fill=THEORY, stroke=THEORY,
          opacity=(0.05, 0.22), stroke_width=0.5, stroke_opacity=0.4)
S.polygon(quad, TEXT, 0.07)
S.line(quad + [quad[0]], TEXT, 0.8, None, 0.4)
S.curve(lambda t: on_line(t, phi_(t)), T_LO, T_HI, THEORY, 2.8, 120)
TAN = [on_line(t, 1 + 22 * t / 5) for t in (-0.2, 0.6)]
S.line(TAN, PRACTICE, 2.2)
S.arrow(P0, on_line(1.0, 0.0), THEORY, 2.0, 8.0)
S.drop(PP)
S.point(PP, PRACTICE, 4.2)
S.point(P0, TEXT, 3.2)
splabel(S, PP, it("P"), 9, 5, PRACTICE, 13)
splabel(S, P0, "(1, 1)", 9, 12, TEXT, 11.5)
splabel(S, on_line(0.55, 0.0), it("u"), 0, 17, THEORY, 13, "middle")
splabel(S, on_line(T_HI, 0.0), it("C"), -9, -2, THEORY, 13.5, "end", True)
splabel(S, TAN[1], "eğim = " + DU + '<tspan dx="4" font-style="italic">f</tspan>' + "(1, 1) = 22/5", 8, -2, PRACTICE, 12)
splabel(S, (0, 0, 4), it("z") + " = 4 " + MINUS + " " + it("x") + "² " + MINUS + " 2" + it("y") + "²",
        -12, -6, THEORY, 11.5, "end")
save("kesit-egrisi", figure(
    int(pl.x0 + pl.w + 60), int(pl.y0 + pl.h + 30), [pl],
    "<em>z</em> = 4 &#8722; <em>x</em>² &#8722; 2<em>y</em>² paraboloidinin <em>z</em> &#8805; 0 kısmı ve "
    "(1, 1) noktasından <em>u</em> = (&#8722;3/5, &#8722;4/5) yönünde geçen düşey düzlem (gri). Düzlem "
    "yüzeyi <em>C</em>: <em>z</em> = 1 + 22<em>t</em>/5 &#8722; 41<em>t</em>²/25 parabolü boyunca keser; "
    "<em>P</em> = (1, 1, 1) noktasındaki teğetin (turuncu) eğimi <em>D<sub>u</sub>f</em>(1, 1) = 22/5'tir.",
    aria="Paraboloid z = 4 - x^2 - 2y^2 with the vertical plane through (1, 1) along u = (-3/5, -4/5), "
         "the section parabola C, the point P = (1, 1, 1) and the tangent line of C at P"))

# ============================================================
# en-hizli-artis: level curves of x e^y, the gradient and u at P = (2, 0)
# ============================================================
p = eq_plot(40, 30, 118, (0.0, 3.5), (-1.0, 2.5))
p.origin_axes(it("x"), it("y"), (1, 3), (-1, 1, 2), num, num, 0.45)


def level(k, n=160):
    """y = ln(k/x) inside the panel."""
    x0 = max(k * math.exp(-2.5), 0.02)
    x1 = min(3.5, k * math.exp(1.0))
    return [(x0 + (x1 - x0) * i / n, math.log(k / (x0 + (x1 - x0) * i / n))) for i in range(n + 1)]


for k in (0.5, 1.0, 3.0, 4.0):
    p.line(level(k), TEXT, 1.0, None, 0.4)
p.line(level(2.0), TEXT, 1.7, None, 0.85)
PT, QT = (2.0, 0.0), (0.5, 2.0)
GR = (3.0, 2.0)                                   # P + grad f(2, 0) = P + (1, 2)
UT = (2.0 - 0.6, 0.8)                             # P + u
TD = (2 / math.sqrt(5), -1 / math.sqrt(5))
p.line([(PT[0] - TD[0], PT[1] - TD[1]), (PT[0] + TD[0], PT[1] + TD[1])], TEXT, 1.4, "5 4", 0.8)
p.line([PT, QT], TEXT, 1.0, "4 3", 0.7)
ga, ua = math.atan2(2, 1), math.atan2(0.8, -0.6)
p.arc(PT[0], PT[1], 0.33, ga, ua, TEXT, 1.1, None, 0.8)
p.label(PT[0] + 0.19 * math.cos((ga + ua) / 2), PT[1] + 0.19 * math.sin((ga + ua) / 2), it(THETA),
        0, 4, TEXT, 12, "middle")
p.arrow(PT, GR, PRACTICE, 2.3, 9.0)
p.arrow(PT, UT, THEORY, 2.3, 9.0)
dot(p, PT, TEXT, 4.0)
dot(p, QT, TEXT, 4.0)
p.label(*PT, it("P"), -8, 17, TEXT, 13, "end")
p.label(*QT, it("Q"), -8, 4, TEXT, 13, "end")
nabla_label(p, *GR, it("f") + "(2, 0)", 7, 4, PRACTICE, 12.5)
p.label(UT[0] - 0.8 * 0.14, UT[1] - 0.6 * 0.14, it("u"), 0, 4, THEORY, 13.5, "end")
plabel(p, PT[0] - TD[0], PT[1] - TD[1], "değişim hızı 0", -5, 4, TEXT, 11.5, "end")
p.label(3.5, math.log(2 / 3.5), it("x") + it("e") + sup(it("y")) + " = 2", 0, 19, TEXT, 12, "end")
save("en-hizli-artis", figure(
    500, 480, [p],
    "<em>f</em>(<em>x</em>, <em>y</em>) = <em>xe<sup>y</sup></em> fonksiyonunun <em>xe<sup>y</sup></em> = 0,5; 1; "
    "2; 3; 4 seviye eğrileri. <em>P</em> = (2, 0) noktasında gradyan &#8711;<em>f</em>(2, 0) = (1, 2) "
    "(turuncu) <em>P</em>'den geçen seviye eğrisine diktir; o eğrinin teğet doğrultusunda (kesikli) değişim "
    "hızı 0'dır. <em>Q</em>'ya bakan <em>u</em> = (&#8722;3/5, 4/5) birim vektörü (mavi) gradyanla "
    "cos <em>&#952;</em> = 1/&#8730;5 olan bir <em>&#952;</em> açısı yapar.",
    aria="Level curves of x e^y in the first quadrant, the gradient (1, 2) drawn from P = (2, 0), the unit "
         "vector u toward Q = (0.5, 2), the angle theta between them and the dashed tangent of the level "
         "curve through P"))

# ============================================================
# sureksiz: f = x y^2/(x^2 + y^4) is 1/2 on x = y^2 and -1/2 on x = -y^2
# ============================================================
p = eq_plot(40, 30, 170, (-1.3, 1.3), (-1.2, 1.2))
p.origin_axes(it("x"), it("y"), (), (), num, num, 0.45)
for a, b in (((-1.2, -1.2), (1.2, 1.2)), ((-1.3, 0.65), (1.3, -0.65))):
    p.line([a, b], TEXT, 1.0, None, 0.45)
YS = [-1.1 + 2.2 * k / 200 for k in range(201)]
p.line([(y * y, y) for y in YS], PRACTICE, 2.4)
p.line([(-y * y, y) for y in YS], THEORY, 2.4)
p.points([(1 / k ** 2, 1 / k) for k in range(1, 6)], TEXT, 3.0)
hollow(p, (0, 0), TEXT, 4.2, 1.7)
p.label(1.21, 1.1, it("f") + " = 1/2", 7, 4, PRACTICE, 12.5)
p.label(-1.21, 1.1, it("f") + " = " + MINUS + "1/2", -7, 4, THEORY, 12.5, "end")
p.label(1.0, 1.0, "(1/" + it("k") + "², 1/" + it("k") + ")", 8, 12, TEXT, 11.5)
p.label(-1.3, 0.65, "doğrular boyunca " + it("f") + " → 0", 2, -8, TEXT, 11.5)
p.label(0, 0, it("f") + "(0, 0) = 0", -12, 13, TEXT, 12, "end")
save("sureksiz", figure(
    520, 460, [p],
    "<em>f</em>(<em>x</em>, <em>y</em>) = <em>xy</em>²/(<em>x</em>² + <em>y</em><sup>4</sup>) için "
    "<em>x</em> = <em>y</em>² parabolünde (turuncu) <em>f</em> = 1/2, <em>x</em> = &#8722;<em>y</em>² "
    "parabolünde (mavi) <em>f</em> = &#8722;1/2'dir; orijin iki parabolden de çıkarılmıştır. Orijinden geçen "
    "her doğru boyunca <em>f</em> &#8594; 0 olur, ama parabol üzerindeki (1/<em>k</em>², 1/<em>k</em>) "
    "noktaları orijine yaklaşırken <em>f</em> hep 1/2'dir.",
    aria="The parabolas x = y^2 and x = -y^2 through the hollow origin, four lines through the origin, and "
         "the points (1/k^2, 1/k) for k = 1 to 5 on the right parabola approaching the origin"))

# ============================================================
# odt: the mean value theorem needs only the segment L(a; b) inside A
# ============================================================
R1, R2 = 1.0, 2.2                                  # the open set A is a thick arc of this annulus
TH0, TH1 = math.radians(200), math.radians(340)
RM, RC = (R1 + R2) / 2, (R2 - R1) / 2


def pol(r, t):
    return (r * math.cos(t), r * math.sin(t))


def arc(r, t0, t1, n=90):
    return [pol(r, t0 + (t1 - t0) * k / n) for k in range(n + 1)]


def cap(t, s0, s1, n=40):
    c = pol(RM, t)
    return [(c[0] + RC * math.cos(s0 + (s1 - s0) * k / n), c[1] + RC * math.sin(s0 + (s1 - s0) * k / n))
            for k in range(n + 1)]


banana = (arc(R2, TH0, TH1) + cap(TH1, TH1, TH1 + math.pi)[1:] + arc(R1, TH1, TH0)[1:]
          + cap(TH0, TH0 + math.pi, TH0 + 2 * math.pi)[1:-1])
p = eq_plot(40, 30, 88, (-2.75, 2.75), (-2.5, 0.3))
closed_curve(p, banana, THEORY, 1.6, "6 4", THEORY, 0.15)
A_ = pol(1.72, math.radians(243))
B_ = pol(1.72, math.radians(297))
C_ = (A_[0] + 0.55 * (B_[0] - A_[0]), A_[1] + 0.55 * (B_[1] - A_[1]))
P_ = pol(1.6, math.radians(213))
Q_ = pol(1.6, math.radians(327))
assert 1.72 * math.cos(math.radians(27)) > R1 and 1.6 * math.cos(math.radians(57)) < R1
p.line([P_, Q_], TEXT, 1.1, "5 4", 0.6)
p.line([A_, B_], TEXT, 2.6)
G_ = (C_[0] + 0.49, C_[1] + 0.38)
p.arrow(C_, G_, PRACTICE, 2.0, 8.0)
dot(p, A_, TEXT, 4.0)
dot(p, B_, TEXT, 4.0)
dot(p, C_, PRACTICE, 4.0)
dot(p, P_, TEXT, 3.4)
dot(p, Q_, TEXT, 3.4)
p.label(*A_, it("a"), -9, 5, TEXT, 13.5, "end")
p.label(*B_, it("b"), 9, 5, TEXT, 13.5)
p.label(*C_, it("c") + " = (1 " + MINUS + " " + it("t") + sub("0") + ")" + it("a") + " + " + it("t") + sub("0")
        + it("b"), 0, 20, PRACTICE, 12, "middle")
nabla_label(p, *G_, it("f") + "(" + it("c") + ")", 6, 6, PRACTICE, 12.5)
p.label(*P_, it("p"), -9, 4, TEXT, 13, "end")
p.label(*Q_, it("q"), 9, 4, TEXT, 13)
p.label(*pol(R2, math.radians(228)), it("A"), -10, 12, THEORY, 15, "end", True)
save("odt", figure(
    560, 330, [p],
    "Konveks olmayan açık bir <em>A</em> kümesi. <em>a</em> ile <em>b</em>'yi birleştiren <em>L</em>(<em>a</em>; "
    "<em>b</em>) doğru parçası <em>A</em>'nın içinde kaldığından teorem bu ikiliye uygulanır ve parça üzerinde "
    "<em>f</em>(<em>b</em>) &#8722; <em>f</em>(<em>a</em>) = &#10216;&#8711;<em>f</em>(<em>c</em>), <em>b</em> "
    "&#8722; <em>a</em>&#10217; eşitliğini sağlayan bir <em>c</em> noktası vardır. <em>p</em> ile <em>q</em>'yu "
    "birleştiren parça ise <em>A</em>'dan taşar; teorem bu ikili için bir şey söylemez.",
    aria="A non-convex open region shaped like a thick arc with a dashed boundary, the segment from a to b "
         "inside it with the point c and an arrow grad f(c), and a dashed segment from p to q that leaves "
         "the region"))
