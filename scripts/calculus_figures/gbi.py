# -*- coding: utf-8 -*-
"""
Figures of the chapter "Genel Bölgelerde İki Katlı İntegraller"
(dersler/integral-calculus/genel-bolgelerde-iki-katli-integraller.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box and never directly under a heading.
The figures are NOT produced at build time. Run

    python scripts/calculus_figures/gbi.py
    python scripts/center_figures.py "calculus-gbi-*.md"
    python scripts/check_figure_labels.py "scripts/_figures/calculus-gbi-*.md"

and paste the markup of scripts/_figures/calculus-gbi-<name>.md into the .qmd.
Captions are Turkish on purpose; aria labels are plain ASCII.
"""
import html
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, dot, panel_title, TEXT, THEORY, PRACTICE, BASE, BG, WIDE  # noqa: E402
from svg_plot3 import Camera, Space  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "calculus-gbi-"

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


def plane_axes(p, xr, yr, xl="x", yl="y", opacity=0.6):
    """Coordinate axes with arrowheads through the origin of a 2-D panel."""
    p.arrow((xr[0], 0), (xr[1], 0), TEXT, 1.1, 7.0, None, opacity)
    p.arrow((0, yr[0]), (0, yr[1]), TEXT, 1.1, 7.0, None, opacity)
    p.label(xr[1], 0, it(xl), -2, 16, TEXT, 12.5, "end")
    p.label(0, yr[1], it(yl), 8, 6, TEXT, 12.5)


def tick(p, x, y, s, axis="x", color=TEXT, size=11):
    """Small tick with its label on one of the axes."""
    if axis == "x":
        p.add(f'<line x1="{p.X(x):.1f}" y1="{p.Y(0) - 3:.1f}" x2="{p.X(x):.1f}" y2="{p.Y(0) + 3:.1f}" '
              f'stroke="{TEXT}" stroke-width="1" opacity="0.7"/>')
        p.label(x, 0, s, 0, 16, color, size, "middle")
    else:
        p.add(f'<line x1="{p.X(0) - 3:.1f}" y1="{p.Y(y):.1f}" x2="{p.X(0) + 3:.1f}" y2="{p.Y(y):.1f}" '
              f'stroke="{TEXT}" stroke-width="1" opacity="0.7"/>')
        p.label(0, y, s, -7, 4, color, size, "end")


def graph(f, a, b, n=120):
    return [(a + (b - a) * k / n, f(a + (b - a) * k / n)) for k in range(n + 1)]


def graph_y(h, c, d, n=120):
    """Points of the curve x = h(y), c <= y <= d."""
    return [(h(c + (d - c) * k / n), c + (d - c) * k / n) for k in range(n + 1)]


G1, G2 = it("g") + sub("1"), it("g") + sub("2")
H1, H2 = it("h") + sub("1"), it("h") + sub("2")
D1, D2 = it("D") + sub("1"), it("D") + sub("2")

# ============================================================
# uzanti: the graph of f over D and the graph of its zero extension F over R
# ============================================================
CX, CY = 1.7, 2.3


def rho(v):
    return 0.95 + 0.20 * math.cos(2 * v + 0.6) + 0.10 * math.sin(3 * v)


def fz(x, y):
    return 2.1 + 0.8 * math.exp(-((x - CX) ** 2 + (y - CY) ** 2) / 0.5) + 0.35 * math.sin(1.6 * y - 0.5)


def d_pt(u, v):
    r = u * rho(v)
    return (CX + r * math.cos(v), CY + r * math.sin(v))


RX, RY = (0.35, 3.05), (0.85, 3.75)
cam = Camera(azimuth=35.0, elevation=22.0)
box = [(0, 0, 0), (3.6, 0, 0), (0, 4.4, 0), (0, 0, 3.9), (RX[1], RY[1], 0), (RX[1], RY[0], 0), (0.5, 3.7, 3.4)]
panels = []
left = 20
for k in (0, 1):
    pl, S = fit_space(cam, box, left, 40, 50, 0.25)
    left += pl.w + 30
    S.axes(3.6, 4.4, 3.9)
    edge = [d_pt(1.0, 2 * math.pi * j / 96) for j in range(97)]
    if k == 1:
        rect = [(RX[0], RY[0], 0), (RX[1], RY[0], 0), (RX[1], RY[1], 0), (RX[0], RY[1], 0)]
        S.polygon(rect, THEORY, 0.20, THEORY, 1.3)
        S.label((RX[1], RY[1], 0), it("R"), 6, 14, THEORY, 13, "start", True)
        S.label((2.55, 1.3, 0), it("F") + " = 0", 0, 4, THEORY, 12, "middle", True)
    S.polygon([(x, y, 0) for x, y in edge], BASE, 0.28, BASE, 1.5)
    S.label((CX, CY, 0), it("D"), -4, 6, BASE, 13, "middle", True)
    for v in (0.35, 2.0, 3.4, 4.6):
        x, y = d_pt(1.0, v)
        S.guide([(x, y, 0), (x, y, fz(x, y))], TEXT, 0.45)
    S.surface(lambda u, v: (*d_pt(u, v), fz(*d_pt(u, v))), (0, 1), (0, 2 * math.pi), nu=5, nv=24,
              fill=THEORY, stroke=THEORY, opacity=(0.10, 0.34), stroke_width=0.5, stroke_opacity=0.45)
    S.line([(x, y, fz(x, y)) for x, y in edge], THEORY, 1.6)
    # the graph's name sits just right of the rightmost point of its rim, off the mesh
    xt, yt = max(((x, y) for x, y in edge), key=lambda q: S.pt((*q, fz(*q)))[0])
    if k == 0:
        S.label((xt, yt, fz(xt, yt)), it("f") + "'nin grafiği", 8, 4, THEORY, 12, "start", True)
        panel_title(pl, it("z") + " = " + it("f") + "(" + it("x") + ", " + it("y") + "), " + it("D") + " üzerinde")
    else:
        S.label((xt, yt, fz(xt, yt)), it("F") + "'nin grafiği", 8, 4, THEORY, 12, "start", True)
        panel_title(pl, it("z") + " = " + it("F") + "(" + it("x") + ", " + it("y") + "), " + it("R") + " üzerinde")
    panels.append(pl)
save("uzanti", figure(
    int(left), int(max(q.y0 + q.h for q in panels) + 20), panels,
    "Solda <em>f</em>'nin <em>D</em> üzerindeki grafiği. Sağda <em>D</em>'yi içeren <em>R</em> dikdörtgeni "
    "ve <em>F</em>'nin grafiği: <em>D</em> üzerinde <em>f</em> ile aynı yüzey, <em>R</em>'nin geri kalanında "
    "taban düzlemi (<em>F</em> = 0). İki grafiğin altında kalan hacim aynıdır.",
    css_class=WIDE,
    aria="Two 3D views: left, a curved surface z = f(x, y) above a region D on the floor; right, the same "
         "surface together with a rectangle R containing D, on which the zero extension F is 0 outside D"))

# ============================================================
# tipler: a type I and a type II region with the arrow that reads the inner limits
# ============================================================


def g1(x):
    return 1.0 + 0.35 * math.sin(1.7 * (x - 1.0))


def g2(x):
    return 3.1 + 0.45 * math.sin(1.4 * x + 0.3)


A_, B_ = 1.0, 4.0
p = eq_plot(40, 30, 62, (-0.4, 5.0), (-0.4, 4.4))
top = graph(g2, A_, B_)
bot = graph(g1, A_, B_)
p.polygon(bot + top[::-1], BASE, 0.20)
p.line(top, BASE, 2.0)
p.line(bot, BASE, 2.0)
p.line([(A_, g1(A_)), (A_, g2(A_))], BASE, 2.0)
p.line([(B_, g1(B_)), (B_, g2(B_))], BASE, 2.0)
p.line([(A_, 0), (A_, g1(A_))], TEXT, 1.0, "4 3", 0.5)
p.line([(B_, 0), (B_, g1(B_))], TEXT, 1.0, "4 3", 0.5)
plane_axes(p, (-0.4, 4.9), (-0.4, 4.35))
tick(p, A_, 0, it("a"))
tick(p, B_, 0, it("b"))
X0 = 2.75
p.line([(X0, 0), (X0, g1(X0))], TEXT, 1.0, "4 3", 0.5)
tick(p, X0, 0, it("x"))
p.arrow((X0, g1(X0)), (X0, g2(X0)), PRACTICE, 2.2, 9.0)
dot(p, (X0, g1(X0)), PRACTICE, 3.2)
p.label(1.75, 2.15, it("D"), 0, 0, BASE, 14, "middle", True)
p.label(2.4, 3.85, it("y") + " = " + G2 + "(" + it("x") + ")", 0, 0, BASE, 12.5, "middle", True)
p.label(1.9, 0.42, it("y") + " = " + G1 + "(" + it("x") + ")", 0, 0, BASE, 12.5, "middle", True)
panel_title(p, "Birinci tip (I. tip) bölge")
p1 = p


def h1(y):
    return 1.0 + 0.4 * math.sin(1.9 * y + 0.4)


def h2(y):
    return 3.4 + 0.35 * math.sin(1.6 * y + 1.2)


C_, D_ = 1.0, 3.6
p = eq_plot(p1.x0 + p1.w + 50, 30, 62, (-0.4, 5.0), (-0.4, 4.4))
lft = graph_y(h1, C_, D_)
rgt = graph_y(h2, C_, D_)
p.polygon(lft + rgt[::-1], BASE, 0.20)
p.line(lft, BASE, 2.0)
p.line(rgt, BASE, 2.0)
p.line([(h1(C_), C_), (h2(C_), C_)], BASE, 2.0)
p.line([(h1(D_), D_), (h2(D_), D_)], BASE, 2.0)
p.line([(0, C_), (h1(C_), C_)], TEXT, 1.0, "4 3", 0.5)
p.line([(0, D_), (h1(D_), D_)], TEXT, 1.0, "4 3", 0.5)
plane_axes(p, (-0.4, 4.9), (-0.4, 4.35))
tick(p, 0, C_, it("c"), "y")
tick(p, 0, D_, it("d"), "y")
Y0 = 2.25
p.line([(0, Y0), (h1(Y0), Y0)], TEXT, 1.0, "4 3", 0.5)
tick(p, 0, Y0, it("y"), "y")
p.arrow((h1(Y0), Y0), (h2(Y0), Y0), PRACTICE, 2.2, 9.0)
dot(p, (h1(Y0), Y0), PRACTICE, 3.2)
p.label(2.3, 3.0, it("D"), 0, 0, BASE, 14, "middle", True)
p.label(h1(1.5), 1.5, it("x") + " = " + H1 + "(" + it("y") + ")", -8, 4, BASE, 12.5, "end", True)
p.label(h2(1.5), 1.5, it("x") + " = " + H2 + "(" + it("y") + ")", 8, 4, BASE, 12.5, "start", True)
panel_title(p, "İkinci tip (II. tip) bölge")
save("tipler", figure(
    int(p.x0 + p.w + 40), int(p.y0 + p.h + 30), [p1, p],
    "Solda I. tip bir bölge: alt ve üst kenarı <em>x</em>'in fonksiyonlarının grafikleridir. Düşey ok "
    "<em>y</em> = <em>g</em><sub>1</sub>(<em>x</em>) eğrisinden girip <em>y</em> = <em>g</em><sub>2</sub>(<em>x</em>) "
    "eğrisinden çıkar ve iç integralin sınırlarını verir. Sağda II. tip bir bölge: sol ve sağ kenarı "
    "<em>y</em>'nin fonksiyonlarıdır; yatay ok <em>x</em> = <em>h</em><sub>1</sub>(<em>y</em>) eğrisinden "
    "<em>x</em> = <em>h</em><sub>2</sub>(<em>y</em>) eğrisine gider.",
    css_class=WIDE,
    aria="Left: a region between the graphs y = g1(x) below and y = g2(x) above for x between a and b, "
         "with a vertical arrow from the lower to the upper curve. Right: a region between the curves "
         "x = h1(y) and x = h2(y) for y between c and d, with a horizontal arrow from left to right"))

# ============================================================
# parabol: Example 1, the region between y = 2x^2 and y = 1 + x^2
# ============================================================
p = eq_plot(40, 30, 120, (-1.55, 1.6), (-0.35, 3.2))
reg = graph(lambda x: 2 * x * x, -1, 1)[::-1] + graph(lambda x: 1 + x * x, -1, 1)
p.polygon(reg, BASE, 0.20)
plane_axes(p, (-1.5, 1.55), (-0.3, 3.15))
XL = math.sqrt(3.05 / 2)
p.line(graph(lambda x: 2 * x * x, -XL, XL), BASE, 2.0)
XU = math.sqrt(3.05 - 1)
p.line(graph(lambda x: 1 + x * x, -1.42, 1.42), THEORY, 2.0)
dot(p, (-1, 2), TEXT, 3.6)
dot(p, (1, 2), TEXT, 3.6)
p.label(-1, 2, "(" + MINUS + "1, 2)", -10, 4, TEXT, 12, "end")
p.label(1, 2, "(1, 2)", 10, 4, TEXT, 12)
tick(p, -1, 0, MINUS + "1")
tick(p, 1, 0, "1")
X0 = 0.45
p.arrow((X0, 2 * X0 * X0), (X0, 1 + X0 * X0), PRACTICE, 2.2, 9.0)
dot(p, (X0, 2 * X0 * X0), PRACTICE, 3.0)
p.label(-0.45, 1.0, it("D"), 0, 0, BASE, 14, "middle", True)
p.label(1.42, 1 + 1.42 ** 2, it("y") + " = 1 + " + it("x") + "²", 6, 8, THEORY, 12.5, "start", True)
p.label(0.85, 2 * 0.85 ** 2, it("y") + " = 2" + it("x") + "²", 12, 6, BASE, 12.5, "start", True)
save("parabol", figure(
    int(p.x0 + p.w + 90), int(p.y0 + p.h + 30), [p],
    "<em>y</em> = 2<em>x</em>² ve <em>y</em> = 1 + <em>x</em>² parabolleri (&#8722;1, 2) ve (1, 2) noktalarında "
    "kesişir. Aradaki <em>D</em> bölgesi I. tiptir: her düşey ok alttaki <em>y</em> = 2<em>x</em>² parabolünden "
    "girer, üstteki <em>y</em> = 1 + <em>x</em>² parabolünden çıkar.",
    aria="The parabolas y = 2x^2 and y = 1 + x^2 meeting at (-1, 2) and (1, 2), the region D between them "
         "shaded and a vertical arrow from the lower to the upper parabola"))

# ============================================================
# paraboloit: Example 2, the solid under z = x^2 + y^2 above D: x^2 <= y <= 2x
# ============================================================
ZS = 0.15                       # the z axis is drawn at 3/20 of the scale of the x and y axes


def zf(x, y):
    return ZS * (x * x + y * y)


def top_pt(s, t):
    x = 2 * s
    y = x * x + t * (2 * x - x * x)
    return (x, y, zf(x, y))


cam = Camera(azimuth=40.0, elevation=34.0)
box = [(0, 0, 0), (2.9, 0, 0), (0, 4.9, 0), (0, 0, 1.7), (2, 4, 3.0), (2, 4, 0), (2.4, 0.2, 0)]
pl, S = fit_space(cam, box, 30, 30, 80, 0.3)
S.axes(2.9, 4.9, 1.7)
for v in (1, 2):
    S.line([(v, -0.06, 0), (v, 0.06, 0)], TEXT, 1.0, None, 0.7)
    S.label((v, 0, 0), str(v), -9, 8, TEXT, 10.5, "end")
for v in (2, 4):
    S.line([(-0.06, v, 0), (0.06, v, 0)], TEXT, 1.0, None, 0.7)
    S.label((0, v, 0), str(v), 0, -7, TEXT, 10.5, "middle")
# the region D on the floor; its two boundary curves are drawn a little beyond (2, 4)
floor = [(x, x * x, 0) for x in [2 * k / 60 for k in range(61)]] +         [(x, 2 * x, 0) for x in [2 - 2 * k / 60 for k in range(61)]]
S.polygon(floor, BASE, 0.30)
S.curve(lambda u: (u, u * u, 0), 0.0, 2.0, BASE, 1.8, 80)
S.curve(lambda u: (u, 2 * u, 0), 0.0, 2.0, PRACTICE, 1.8, 40)
# back wall on the plane y = 2x, top surface, front wall on the parabolic cylinder y = x^2
S.surface(lambda s, w: (2 * s, 4 * s, w * zf(2 * s, 4 * s)), (0, 1), (0, 1), nu=24, nv=1,
          fill=PRACTICE, stroke="none", opacity=(0.10, 0.10), stroke_width=0, stroke_opacity=0)
S.surface(top_pt, (0, 1), (0, 1), nu=14, nv=5, fill=THEORY, stroke=THEORY,
          opacity=(0.18, 0.36), stroke_width=0.5, stroke_opacity=0.45)
S.surface(lambda s, w: (2 * s, 4 * s * s, w * zf(2 * s, 4 * s * s)), (0, 1), (0, 1), nu=24, nv=1,
          fill=BASE, stroke="none", opacity=(0.14, 0.14), stroke_width=0, stroke_opacity=0)
S.line([top_pt(k / 60, 0) for k in range(61)], THEORY, 1.7)
S.line([top_pt(k / 60, 1) for k in range(61)], THEORY, 1.7)
S.line([(2, 4, 0), (2, 4, zf(2, 4))], TEXT, 1.2, None, 0.7)
S.point((2, 4, zf(2, 4)), TEXT, 3.4)
S.label((2, 4, zf(2, 4)), "(2, 4, 20)", 10, 4, TEXT, 11.5)
S.point((2, 4, 0), TEXT, 3.0)
S.label((2, 4, 0), "(2, 4, 0)", 10, 8, TEXT, 11.5)
S.label((1.1, 1.65, 0), it("D"), 0, 5, BASE, 13, "middle", True)
S.label((1.5, 2.25, 0), it("y") + " = " + it("x") + "²", -8, 14, BASE, 12, "end", True)
splabel(S, (1.6, 3.2, 0), it("y") + " = 2" + it("x"), 12, 2, PRACTICE, 12, "start", True)
# the paraboloid's name floats in the empty space above the rim of the top surface
pl.label(0.75, -0.07, it("z") + " = " + it("x") + "² + " + it("y") + "²", 0, 0, THEORY, 12, "middle", True)
save("paraboloit", figure(
    int(pl.x0 + pl.w + 60), int(pl.y0 + pl.h + 20), [pl],
    "Örnekteki cisim: tabanı <em>xy</em>-düzlemindeki <em>D</em> bölgesi, tavanı <em>z</em> = <em>x</em>² + "
    "<em>y</em>² paraboloidi, yan yüzleri <em>y</em> = 2<em>x</em> düzlemi ile <em>y</em> = <em>x</em>² parabolik "
    "silindiridir. En yüksek noktası (2, 4, 20)'dir; şekil sığsın diye <em>z</em> ekseni kısaltılarak "
    "çizilmiştir.",
    aria="A solid above the region D between y = x^2 and y = 2x in the xy plane, capped by the paraboloid "
         "z = x^2 + y^2 and walled by the plane y = 2x and the parabolic cylinder y = x^2; the highest point "
         "is (2, 4, 20) and the z axis is drawn shortened"))

# ============================================================
# ornek3: Example 3, D between y = x - 1 and y^2 = 2x + 6, as type I and as type II
# ============================================================


def par_x(y):
    return y * y / 2 - 3


XR, YR = (-3.9, 6.4), (-3.3, 5.3)
panels = []
for k in (0, 1):
    x0 = 30 if k == 0 else panels[0].x0 + panels[0].w + 40
    p = eq_plot(x0, 40, 29, XR, YR)
    reg = graph_y(par_x, -2, 4) + [(y + 1, y) for y in (4, -2)]
    p.polygon(reg, BASE, 0.20)
    plane_axes(p, (XR[0] + 0.1, XR[1] - 0.1), (YR[0] + 0.1, YR[1] - 0.1))
    p.line(graph_y(par_x, -3.0, 4.6), BASE, 2.0)
    p.line([(-2.3, -3.3), (6.1, 5.1)], THEORY, 2.0)
    dot(p, (5, 4), TEXT, 3.6)
    dot(p, (-1, -2), TEXT, 3.6)
    p.label(5, 4, "(5, 4)", -8, -8, TEXT, 11.5, "end")
    p.label(-1, -2, "(" + MINUS + "1, " + MINUS + "2)", -14, 4, TEXT, 11.5, "end")
    p.label(1.6, 2.2, it("D"), 0, 0, BASE, 14, "middle", True)
    if k == 0:
        p.label(-3, 0, MINUS + "3", -6, -6, TEXT, 11, "end")
        p.line([(-1, -2), (-1, 2)], TEXT, 1.1, "4 3", 0.7)
        for xa in (-2.2, 2.4):
            lo = -math.sqrt(2 * xa + 6) if xa < -1 else xa - 1
            hi = math.sqrt(2 * xa + 6)
            p.arrow((xa, lo), (xa, hi), PRACTICE, 2.2, 9.0)
            dot(p, (xa, lo), PRACTICE, 3.0)
        p.label(-0.6, 3.0, it("y") + " = √(2" + it("x") + " + 6)", -10, -12, BASE, 12, "end", True)
        p.label(1.5, -3.0, it("y") + " = " + MINUS + "√(2" + it("x") + " + 6)", 8, 6, BASE, 12, "start", True)
        p.label(3.9, 2.9, it("y") + " = " + it("x") + " " + MINUS + " 1", 12, 6, THEORY, 12, "start", True)
        panel_title(p, "I. tip olarak: alt sınır iki parçalı")
    else:
        Y0 = 1.0
        p.arrow((par_x(Y0), Y0), (Y0 + 1, Y0), PRACTICE, 2.2, 9.0)
        dot(p, (par_x(Y0), Y0), PRACTICE, 3.0)
        p.label(-0.6, 3.0, it("x") + " = " + it("y") + "²/2 " + MINUS + " 3", -10, -12, BASE, 12, "end", True)
        p.label(3.9, 2.9, it("x") + " = " + it("y") + " + 1", 12, 6, THEORY, 12, "start", True)
        panel_title(p, "II. tip olarak: tek parça")
    panels.append(p)
save("ornek3", figure(
    int(panels[1].x0 + panels[1].w + 30), int(panels[1].y0 + panels[1].h + 20), panels,
    "<em>y</em> = <em>x</em> &#8722; 1 doğrusu ile <em>y</em>² = 2<em>x</em> + 6 parabolü arasındaki <em>D</em> "
    "bölgesi. Solda düşey oklar: <em>x</em> = &#8722;1'in solunda alt sınır parabolün alt kolu, sağında doğrudur; "
    "bu yüzden I. tip yazım iki integral ister. Sağda yatay oklar hep paraboldan girip doğrudan çıkar: II. tip "
    "yazım tek integraldir.",
    css_class=WIDE,
    aria="Two copies of the region between the line y = x - 1 and the parabola y^2 = 2x + 6, meeting at "
         "(-1, -2) and (5, 4): left with vertical arrows and a dashed line at x = -1 where the lower boundary "
         "changes, right with a horizontal arrow from the parabola to the line"))

# ============================================================
# dortyuzlu: Example 4, the tetrahedron T and its shadow D on the xy plane
# ============================================================
O3, A3, B3, C3 = (0, 0, 0), (0, 0, 2), (0, 1, 0), (1, 0.5, 0)
cam = Camera(azimuth=35.0, elevation=22.0)
box = [O3, (1.7, 0, 0), (0, 1.7, 0), (0, 0, 2.5), C3]
pl, S = fit_space(cam, box, 30, 40, 120, 0.25)
S.axes(1.7, 1.7, 2.5)
S.polygon([O3, A3, B3], BASE, 0.10)
S.polygon([O3, A3, C3], PRACTICE, 0.14)
S.polygon([O3, B3, C3], BASE, 0.30)
S.polygon([A3, B3, C3], THEORY, 0.22)
S.line([A3, B3, C3, A3], THEORY, 1.8)
S.line([A3, O3], THEORY, 1.4, "4 3", 0.8)
S.line([O3, C3], THEORY, 1.4, "4 3", 0.8)
for P in (A3, B3, C3):
    S.point(P, TEXT, 3.4)
S.label(A3, "(0, 0, 2)", 10, 2, TEXT, 11.5)
S.label(B3, "(0, 1, 0)", 8, -8, TEXT, 11.5)
S.label(C3, "(1, 1/2, 0)", 8, 14, TEXT, 11.5)
S.label((0.5, 0.25, 0), it("D"), 8, 10, BASE, 12.5, "middle", True)
S.label((0.33, 0.45, 0.62), it("T"), 0, 0, THEORY, 14, "middle", True)
S.label((0.2, 0.6, 1.25), it("x") + " + 2" + it("y") + " + " + it("z") + " = 2", 18, -10, THEORY, 12, "start", True)
S.label((0.5, 0.25, 0.7), it("x") + " = 2" + it("y"), -14, 4, PRACTICE, 12, "end", True)
panel_title(pl, "Dörtyüzlü " + it("T"))
q = eq_plot(pl.x0 + pl.w + 60, 60, 190, (-0.2, 1.35), (-0.2, 1.25))
tri = [(0, 0), (1, 0.5), (0, 1)]
q.polygon(tri, BASE, 0.22)
plane_axes(q, (-0.15, 1.3), (-0.15, 1.2))
q.line([(-0.1, -0.05), (1.25, 0.625)], BASE, 2.0)
q.line([(-0.1, 1.05), (1.25, 0.375)], THEORY, 2.0)
X0 = 0.4
q.arrow((X0, X0 / 2), (X0, 1 - X0 / 2), PRACTICE, 2.2, 9.0)
dot(q, (X0, X0 / 2), PRACTICE, 3.0)
dot(q, (1, 0.5), TEXT, 3.4)
q.label(1, 0.5, "(1, 1/2)", 8, -12, TEXT, 11.5)
tick(q, 1, 0, "1")
tick(q, 0, 1, "1", "y")
q.label(0.2, 0.55, it("D"), 0, 0, BASE, 14, "middle", True)
q.label(0.75, 0.375, it("y") + " = " + it("x") + "/2", 6, 20, BASE, 12, "middle", True)
q.label(0.7, 0.65, it("y") + " = 1 " + MINUS + " " + it("x") + "/2", 10, -10, THEORY, 12, "start", True)
panel_title(q, "Taban bölgesi " + it("D"))
save("dortyuzlu", figure(
    int(q.x0 + q.w + 40), int(max(pl.y0 + pl.h, q.y0 + q.h) + 20), [pl, q],
    "Solda <em>x</em> = 0, <em>z</em> = 0, <em>x</em> = 2<em>y</em> ve <em>x</em> + 2<em>y</em> + <em>z</em> = 2 "
    "düzlemlerinin sınırladığı <em>T</em> dörtyüzlüsü. Sağda tabanı olan <em>D</em> üçgeni: <em>x</em> + "
    "2<em>y</em> + <em>z</em> = 2 düzlemi <em>xy</em>-düzlemini <em>y</em> = 1 &#8722; <em>x</em>/2 doğrusu "
    "boyunca keser.",
    css_class=WIDE,
    aria="Left: a tetrahedron T with vertices at the origin, (0, 0, 2), (0, 1, 0) and (1, 1/2, 0). Right: "
         "its base triangle D in the xy plane between the lines y = x/2 and y = 1 - x/2 for x from 0 to 1, "
         "with a vertical arrow"))

# ============================================================
# sira: Example 5, the triangle 0 <= x <= y <= 1 read in both orders
# ============================================================
panels = []
for k in (0, 1):
    x0 = 30 if k == 0 else panels[0].x0 + panels[0].w + 60
    p = eq_plot(x0, 40, 190, (-0.2, 1.35), (-0.2, 1.3))
    tri = [(0, 0), (1, 1), (0, 1)]
    p.polygon(tri, BASE, 0.22)
    plane_axes(p, (-0.15, 1.3), (-0.15, 1.25))
    p.line([(-0.1, -0.1), (1.2, 1.2)], BASE, 2.0)
    p.line([(0, 1), (1.2, 1)], THEORY, 2.0)
    p.line([(0, 0), (0, 1)], THEORY, 2.0)
    tick(p, 1, 0, "1")
    tick(p, 0, 1, "1", "y")
    p.line([(1, 0), (1, 1)], TEXT, 1.0, "4 3", 0.5)
    dot(p, (1, 1), TEXT, 3.4)
    p.label(1, 1, "(1, 1)", 8, 16, TEXT, 11.5)
    if k == 0:
        X0 = 0.4
        p.arrow((X0, X0), (X0, 1), PRACTICE, 2.2, 9.0)
        dot(p, (X0, X0), PRACTICE, 3.0)
        p.label(0.15, 0.62, it("D"), 0, 0, BASE, 14, "middle", True)
        p.label(1.2, 1.2, it("y") + " = " + it("x"), 6, 14, BASE, 12.5, "start", True)
        p.label(0.55, 1, it("y") + " = 1", 0, -9, THEORY, 12.5, "middle", True)
        panel_title(p, "I. tip: 0 ≤ " + it("x") + " ≤ 1, " + it("x") + " ≤ " + it("y") + " ≤ 1")
    else:
        Y0 = 0.6
        p.arrow((0, Y0), (Y0, Y0), PRACTICE, 2.2, 9.0)
        dot(p, (0, Y0), PRACTICE, 3.0)
        p.label(0.2, 0.82, it("D"), 0, 0, BASE, 14, "middle", True)
        p.label(1.2, 1.2, it("x") + " = " + it("y"), 6, 14, BASE, 12.5, "start", True)
        p.label(0, 0.3, it("x") + " = 0", -8, 4, THEORY, 12.5, "end", True)
        panel_title(p, "II. tip: 0 ≤ " + it("y") + " ≤ 1, 0 ≤ " + it("x") + " ≤ " + it("y"))
    panels.append(p)
save("sira", figure(
    int(panels[1].x0 + panels[1].w + 40), int(panels[1].y0 + panels[1].h + 20), panels,
    "Aynı <em>D</em> üçgeni iki biçimde okunur. Solda düşey ok <em>y</em> = <em>x</em> doğrusundan "
    "<em>y</em> = 1 doğrusuna gider; sağda yatay ok <em>x</em> = 0 ekseninden <em>x</em> = <em>y</em> "
    "doğrusuna gider. İkinci okuma, iç integrali <em>x</em>'e göre almayı sağlar.",
    css_class=WIDE,
    aria="Two copies of the triangle with vertices (0, 0), (1, 1) and (0, 1): left with a vertical arrow "
         "from y = x up to y = 1, right with a horizontal arrow from x = 0 to x = y"))

# ============================================================
# bolme: a region that is neither type I nor type II, split into D1 (type I) and D2 (type II)
# ============================================================
SPLIT = 2.5


def tcurve(x):
    """Upper edge: a valley around x = 1.8, falling to the right of x = 2.5."""
    v = 3.1 - 1.0 * math.exp(-((x - 1.8) / 0.28) ** 2)
    if x > SPLIT:
        v -= 0.3 * ((x - SPLIT) / 0.6) ** 2
    return v


def rcurve(y):
    """Right edge x = R(y): a dent around y = 1.6."""
    return 3.1 - 0.55 * math.exp(-((y - 1.6) / 0.3) ** 2)


Y_TOP = tcurve(3.1)                               # where the upper and the right edge meet
outline = [(1.0, 0.5)] + [(rcurve(y), y) for y in [0.5 + (Y_TOP - 0.5) * k / 80 for k in range(81)]] + \
          [(x, tcurve(x)) for x in [3.1 - 2.1 * k / 120 for k in range(121)]] + [(1.0, 0.5)]
panels = []
for k in (0, 1):
    x0 = 30 if k == 0 else panels[0].x0 + panels[0].w + 50
    p = eq_plot(x0, 40, 78, (-0.3, 3.7), (-0.3, 3.7))
    plane_axes(p, (-0.25, 3.65), (-0.25, 3.65))
    if k == 0:
        p.polygon(outline, BASE, 0.20)
        p.line(outline, BASE, 2.0)
        p.label(1.5, 1.3, it("D"), 0, 0, BASE, 14, "middle", True)
        p.line([(-0.1, 2.55), (3.6, 2.55)], TEXT, 1.0, "4 3", 0.6)
        p.line([(2.8, -0.1), (2.8, 3.6)], TEXT, 1.0, "4 3", 0.6)
        panel_title(p, "Ne I. ne II. tip")
    else:
        left_part = [(1.0, 0.5), (SPLIT, 0.5)] + [(x, tcurve(x)) for x in
                                                  [SPLIT - (SPLIT - 1.0) * j / 100 for j in range(101)]]
        right_part = [(SPLIT, 0.5)] + [(rcurve(y), y) for y in [0.5 + (Y_TOP - 0.5) * j / 80 for j in range(81)]] + \
                     [(x, tcurve(x)) for x in [3.1 - (3.1 - SPLIT) * j / 40 for j in range(41)]]
        p.polygon(left_part, BASE, 0.20)
        p.polygon(right_part, PRACTICE, 0.16)
        p.line(outline, BASE, 2.0)
        p.line([(SPLIT, 0.5), (SPLIT, tcurve(SPLIT))], PRACTICE, 2.0)
        p.label(1.5, 1.3, D1, 0, 0, BASE, 14, "middle", True)
        p.label(2.78, 2.35, D2, 0, 0, PRACTICE, 14, "middle", True)
        panel_title(p, D1 + " I. tip, " + D2 + " II. tip")
    panels.append(p)
save("bolme", figure(
    int(panels[1].x0 + panels[1].w + 30), int(panels[1].y0 + panels[1].h + 20), panels,
    "Solda ne I. ne II. tip olan bir <em>D</em> bölgesi: kesikli düşey doğru sınırı dört kez, kesikli yatay "
    "doğru da dört kez keser. Sağda <em>D</em> bir düşey doğru parçasıyla iki parçaya ayrılmıştır: "
    "<em>D</em><sub>1</sub> I. tip, <em>D</em><sub>2</sub> II. tip bir bölgedir ve iki parça yalnız bu doğru "
    "parçası boyunca ortaktır.",
    css_class=WIDE,
    aria="Left: a region D with a dip in its upper edge and a dent in its right edge, so that a dashed "
         "vertical line and a dashed horizontal line each cross its boundary four times. Right: the same "
         "region cut by a vertical segment into a left part D1 of type I and a right part D2 of type II"))
