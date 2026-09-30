# -*- coding: utf-8 -*-
"""
Figures of the chapter "Mutlak ve Bağlı Ekstremumlar"
(dersler/analiz-4/mutlak-ve-bagli-ekstremumlar.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box and never directly under a heading.
The figures are NOT produced at build time. Run

    python scripts/analysis4_figures/lag.py
    python scripts/center_figures.py "analysis4-lag-*.md"
    python scripts/check_figure_labels.py "scripts/_figures/analysis4-lag-*.md"

and paste the markup of scripts/_figures/analysis4-lag-<name>.md into the .qmd.
Captions are Turkish on purpose; aria labels are plain ASCII.

Conventions: a boundary that belongs to the set is solid, one that does not is
dashed. Constraint curves are drawn in BASE, level curves of the objective in
THEORY or grey, extremum points in PRACTICE. Every drawing with a circle has
equal x and y scales.
"""
import html
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, TEXT, THEORY, PRACTICE, BASE, REMARK, BG  # noqa: E402
from svg_plot3 import Camera, Space  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "analysis4-lag-"

MINUS, INF = "&#8722;", "&#8734;"
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


def dec(v):
    """Decimal comma: 0.5 -> '0,5', negative sign as a true minus."""
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return s.replace(".", ",").replace("-", MINUS)


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
    """Label on a page-coloured plate, for text that must sit on other lines.

    (A stroke halo with paint-order is painted per tspan and would erase the
    previous glyphs, so a rounded rectangle is laid under the text instead.)
    """
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


def nabla_px(p, px, py, size, color):
    """A nabla drawn as a path (the SVG font has no U+2207); left foot at pixel px, baseline py."""
    w, h = 0.62 * size, 0.66 * size
    p.add(f'<path d="M{px + 0.02 * size:.1f},{py - h:.1f} L{px + w:.1f},{py - h:.1f} L{px + w / 2 + 0.01 * size:.1f},'
          f'{py:.1f} Z" fill="none" stroke="{color}" stroke-width="{0.085 * size:.2f}" stroke-linejoin="round"/>')


def grad_label(p, x, y, parts, dx=0, dy=0, color=TEXT, size=12, anchor="start", plate=False):
    """Label made of text pieces and nablas (None stands for a nabla)."""
    widths = [0.72 * size if s is None else text_w(s, size) + 0.08 * size for s in parts]
    total = sum(widths)
    px = p.X(x) + dx - (total / 2 if anchor == "middle" else total if anchor == "end" else 0)
    py = p.Y(y) + dy
    if plate:
        p.add(f'<rect x="{px - 2.5:.1f}" y="{py - 0.8 * size - 1:.1f}" width="{total + 5:.1f}" '
              f'height="{size + 3:.1f}" rx="3" fill="{BG}" opacity="0.85"/>')
    for s, w in zip(parts, widths):
        if s is None:
            nabla_px(p, px, py, size, color)
        else:
            p.text_px(px, py, s, color, size)
        px += w


def cbrt(v):
    return math.copysign(abs(v) ** (1 / 3), v)


# ============================================================
# dikdortgen: f = x^2 - 2xy + 2y on D = [0, 3] x [0, 2]
# ============================================================
p = eq_plot(60, 30, 115, (-0.5, 3.6), (-0.5, 2.6))
D = [(0, 0), (3, 0), (3, 2), (0, 2)]
p.polygon(D, THEORY, 0.10)
p.arrow((-0.4, 0), (3.6, 0), TEXT, 1.0, 7.0, None, 0.55)
p.arrow((0, -0.4), (0, 2.6), TEXT, 1.0, 7.0, None, 0.55)
p.label(3.6, 0, it("x"), 0, 17, TEXT, 12.5, "middle")
p.label(0, 2.6, it("y"), 10, 5, TEXT, 12.5)


def inside_d(q):
    return -1e-9 <= q[0] <= 3 + 1e-9 and -1e-9 <= q[1] <= 2 + 1e-9


def level_runs(c, n=600):
    """The level set x^2 - 2xy + 2y = c inside D, as y = (c - x^2) / (2 - 2x) for x != 1."""
    runs, cur = [], []
    for k in range(n + 1):
        x = 3 * k / n
        if abs(x - 1) < 1e-9:
            if cur:
                runs.append(cur)
            cur = []
            continue
        q = (x, (c - x * x) / (2 - 2 * x))
        if inside_d(q):
            cur.append(q)
        elif cur:
            runs.append(cur)
            cur = []
    if cur:
        runs.append(cur)
    return [r for r in runs if len(r) > 1]


def clip_to_edge(run):
    """Extend a sampled run to the rectangle boundary by bisection on both ends."""
    out = list(run)
    for end, step in ((0, -1), (-1, 1)):
        x_in = run[end][0]
        x_out = x_in + step * 3 / 600
        c = run[end][0] ** 2 - 2 * run[end][0] * run[end][1] + 2 * run[end][1]
        if not (0 <= x_out <= 3) or abs(x_out - 1) < 1e-6:     # left D, or stopped at the pole x = 1
            continue
        for _ in range(50):
            xm = (x_in + x_out) / 2
            if inside_d((xm, (c - xm * xm) / (2 - 2 * xm))):
                x_in = xm
            else:
                x_out = xm
        q = (x_in, (c - x_in * x_in) / (2 - 2 * x_in))
        if end == 0:
            out.insert(0, q)
        else:
            out.append(q)
    return out


LEVELS = (0.5, 1.0, 2.0, 4.0, 6.0, 8.0)
for c in LEVELS:
    for run in level_runs(c):
        p.line(clip_to_edge(run), REMARK, 1.1, None, 0.85)
p.line([(1, 0), (1, 2)], REMARK, 1.1, None, 0.85)          # f(1, y) = 1: the other half of the level c = 1
p.line(D + [D[0]], THEORY, 1.9)
# small value labels on the level curves
for c, x in ((0.5, 0.36), (0.5, 1.71), (1.0, 2.35), (2.0, 2.05), (4.0, 2.55), (6.0, 2.8)):
    y = (c - x * x) / (2 - 2 * x)
    plabel(p, x, y, dec(c), 0, 4, REMARK, 10, "middle")
# edges
p.label(1.5, 0, it("L") + sub("1"), 0, 18, THEORY, 13, "middle", True)
p.label(3, 1.0, it("L") + sub("2"), 9, 5, THEORY, 13, "start", True)
p.label(0.75, 2, it("L") + sub("3"), 0, -8, THEORY, 13, "middle", True)
p.label(0, 1.5, it("L") + sub("4"), -9, 5, THEORY, 13, "end", True)
# the candidates
p.points([(1, 1), (0, 2), (3, 2)], TEXT, 4.0)
p.points([(0, 0), (2, 2)], THEORY, 4.4)
p.points([(3, 0)], PRACTICE, 4.6)
plabel(p, 1, 1, "kritik nokta, " + it("f") + " = 1", -8, -7, TEXT, 11.5, "end")
p.label(3, 0, "maks: " + it("f") + " = 9", 0, 18, PRACTICE, 12, "middle", True)
p.label(0, 0, "min: " + it("f") + " = 0", -7, 18, THEORY, 12, "end", True)
p.label(2, 2, "min: " + it("f") + " = 0", 0, -8, THEORY, 12, "middle", True)
p.label(0, 2, it("f") + " = 4", -7, -7, TEXT, 12, "end")
p.label(3, 2, it("f") + " = 1", 7, -7, TEXT, 12)
save("dikdortgen", figure(
    560, 420, [p],
    "<em>D</em> = [0, 3] &#215; [0, 2] dikdörtgeni, kenarları <em>L</em><sub>1</sub>–<em>L</em><sub>4</sub> ve "
    "<em>f</em>(<em>x</em>, <em>y</em>) = <em>x</em>² &#8722; 2<em>xy</em> + 2<em>y</em> fonksiyonunun "
    "<em>f</em> = 0,5; 1; 2; 4; 6; 8 seviye eğrileri. <em>f</em> = 1 seviyesi (1, 1) eyer noktasında kesişen iki "
    "doğrudur. En büyük değer (3, 0) köşesinde, en küçük değer (0, 0) ve (2, 2) sınır noktalarında alınır.",
    aria="Rectangle [0, 3] x [0, 2] with edges L1 to L4, grey level curves of f = x^2 - 2xy + 2y, the saddle "
         "point (1, 1), the maximum 9 at (3, 0) and the minimum 0 at (0, 0) and (2, 2)"))

# ============================================================
# cember-seviye: f = x^2 + 2y^2 on the unit circle
# ============================================================
p = eq_plot(40, 30, 118, (-1.9, 1.9), (-1.5, 1.95))
p.arrow((-1.9, 0), (1.9, 0), TEXT, 1.0, 7.0, None, 0.5)
p.arrow((0, -1.5), (0, 1.95), TEXT, 1.0, 7.0, None, 0.5)
p.label(1.9, 0, it("x"), 0, 17, TEXT, 12.5, "middle")
p.label(0, 1.95, it("y"), -10, 5, TEXT, 12.5, "end")


def ellipse(c, n=160):
    a, b = math.sqrt(c), math.sqrt(c / 2)
    return [(a * math.cos(2 * math.pi * k / n), b * math.sin(2 * math.pi * k / n)) for k in range(n + 1)]


for c in (0.5, 1.5, 3.0):
    p.line(ellipse(c), THEORY, 1.0, None, 0.7)
p.line(ellipse(1.0), THEORY, 2.0)
p.line(ellipse(2.0), THEORY, 2.0)
p.line([(math.cos(2 * math.pi * k / 160), math.sin(2 * math.pi * k / 160)) for k in range(161)], BASE, 2.6)
# gradients, all scaled by 1/5
SC = 0.2
p.arrow((1, 0), (1 + 2 * SC, 0), THEORY, 3.4, 11.0)
p.arrow((1, 0), (1 + 2 * SC, 0), BASE, 1.5, 7.0)
p.arrow((0, 1), (0, 1 + 4 * SC), THEORY, 2.2, 10.0)
p.arrow((0, 1), (0, 1 + 2 * SC), BASE, 2.6, 9.0)
grad_label(p, 1 + SC, 0, [None, it("f") + " =", None, it("g")], 4, -9, TEXT, 12.5, "middle", True)
grad_label(p, 0, 1 + 4 * SC, [None, it("f")], -8, 4, THEORY, 13, "end")
grad_label(p, 0, 1 + 2 * SC, [None, it("g")], -8, 4, BASE, 13, "end")
# the four candidates
p.points([(1, 0), (-1, 0)], PRACTICE, 4.2)
p.points([(0, 1), (0, -1)], PRACTICE, 4.2)
p.label(1, 0, "min", -8, -7, PRACTICE, 12, "end", True)
p.label(-1, 0, "min", 8, -7, PRACTICE, 12, "start", True)
p.label(0, 1, "maks", 8, -5, PRACTICE, 12, "start", True)
p.label(0, -1, "maks", 0, 18, PRACTICE, 12, "middle", True)
# names of the curves
a = math.radians(-38)
p.label(math.sqrt(2) * math.cos(a), math.sin(a), it("f") + " = 2", 6, 12, THEORY, 12)
p.label(0.62, math.sqrt(0.5 - 0.62 ** 2 / 2), it("f") + " = 1", 0, -4, THEORY, 12, "middle")
a = math.radians(140)
p.label(math.cos(a), math.sin(a), it("g") + " = 0", -8, -6, BASE, 12.5, "end", True)
save("cember-seviye", figure(
    500, 480, [p],
    "Birim çember <em>g</em> = 0 ve <em>f</em> = <em>x</em>² + 2<em>y</em>² fonksiyonunun <em>f</em> = 0,5; 1; "
    "1,5; 2; 3 seviye elipsleri. <em>f</em> = 1 elipsi çembere (&#177;1, 0) noktalarında içten, <em>f</em> = 2 "
    "elipsi (0, &#177;1) noktalarında dıştan teğettir; bu noktalarda &#8711;<em>f</em> ile &#8711;<em>g</em> "
    "paraleldir. Oklar 1/5 ölçekle çizilmiştir: (1, 0)'da &#8711;<em>f</em> = &#8711;<em>g</em> = (2, 0), "
    "(0, 1)'de &#8711;<em>f</em> = (0, 4) ve &#8711;<em>g</em> = (0, 2).",
    aria="Unit circle with the level ellipses x^2 + 2y^2 = c, the ellipse c = 1 touching the circle at (1, 0) "
         "and (-1, 0), the ellipse c = 2 touching it at (0, 1) and (0, -1), and parallel gradient arrows"))

# ============================================================
# kubik: e^(xy) on the curve x^3 + y^3 = 16
# ============================================================
p = eq_plot(50, 30, 46, (-4, 5), (-4, 5))
p.arrow((-4.1, 0), (5.35, 0), TEXT, 1.1, 7.0, None, 0.5)
p.arrow((0, -4.1), (0, 5.35), TEXT, 1.1, 7.0, None, 0.5)
p.label(5.35, 0, it("x"), -2, -8, TEXT, 12.5, "end")
p.label(0, 5.35, it("y"), 9, 5, TEXT, 12.5)
for t in (-2, 2, 4):
    p.line([(t, -0.08), (t, 0.08)], TEXT, 1.0, None, 0.6)
    p.line([(-0.08, t), (0.08, t)], TEXT, 1.0, None, 0.6)
    p.label(t, 0, dec(t), 0, 16, TEXT, 11, "middle")
    p.label(0, t, dec(t), -7, 4, TEXT, 11, "end")
p.line([(-4, 4), (4, -4)], TEXT, 1.1, "6 4", 0.6)
# level curves xy = const of f = e^(xy)
for c, xs in ((4.0, [(0.8, 5.0)]), (-2.0, [(-4.0, -0.4), (0.5, 5.0)]), (-6.0, [(-4.0, -1.2), (1.5, 5.0)])):
    for x0, x1 in xs:
        pts = [(x0 + (x1 - x0) * k / 120, c / (x0 + (x1 - x0) * k / 120)) for k in range(121)]
        p.line(pts, REMARK, 1.8 if c == 4.0 else 1.2, None, 0.9)
XE = cbrt(80.0)                                      # the curve leaves the window at y = -4, x = 80^(1/3)
curve = [(x, cbrt(16 - x ** 3)) for x in [-4 + (XE + 4) * k / 400 for k in range(401)]]
p.line(curve, BASE, 2.6)
p.points([(2, 2)], PRACTICE, 4.6)
p.label(2, 2, "maks: " + it("e") + sup("4"), 8, -8, PRACTICE, 12.5, "start", True)
p.label(5, 0.8, it("xy") + " = 4", 5, 4, REMARK, 12)
p.label(5, -0.4, it("xy") + " = " + MINUS + "2", 5, 4, REMARK, 12)
p.label(5, -1.2, it("xy") + " = " + MINUS + "6", 5, 4, REMARK, 12)
p.label(-4, 4, it("y") + " = " + MINUS + it("x"), -7, 8, TEXT, 11.5, "end")
p.label(-4, cbrt(80.0), it("xy") + " → " + MINUS + INF, 8, -2, BASE, 12)
p.label(XE, -4, it("xy") + " → " + MINUS + INF, -4, 16, BASE, 12, "end")
p.label(3.55, -2.35, it("x") + "³ + " + it("y") + "³ = 16", 0, 0, BASE, 12.5, "start", True)
save("kubik", figure(
    560, 490, [p],
    "<em>x</em>³ + <em>y</em>³ = 16 eğrisi ve <em>f</em> = <em>e</em><sup><em>xy</em></sup> fonksiyonunun "
    "<em>xy</em> = 4, &#8722;2, &#8722;6 seviye eğrileri. <em>xy</em> = 4 hiperbolü eğriye (2, 2)'de teğettir; "
    "eğrinin öbür bütün noktalarında <em>xy</em> &lt; 4'tür. Eğri <em>y</em> = &#8722;<em>x</em> asimptotuna yaklaşırken "
    "<em>xy</em> &#8594; &#8722;&#8734;, yani <em>f</em> &#8594; 0 olur; minimum yoktur.",
    aria="Curve x^3 + y^3 = 16 with the dashed asymptote y = -x, the hyperbola xy = 4 touching it at (2, 2) "
         "and the hyperbolas xy = -2 and xy = -6 crossing it"))

# ============================================================
# silindir-duzlem: the ellipse cut from the cylinder x^2 + y^2 = 1 by x + y + z = 1
# ============================================================
R2 = math.sqrt(2)
AZ = -15.0
cam = Camera(azimuth=AZ, elevation=20.0)
ZB, ZT = -1.0, 3.0
box = [(math.cos(u), math.sin(u), z) for u in [2 * math.pi * k / 24 for k in range(24)] for z in (ZB, ZT)] + \
      [(1.7, 0, 0), (0, 1.7, 0), (0, 0, 3.5)]
pl, S = fit_space(cam, box, 40, 30, 105, 0.3)
d = cam.d
PHI = math.atan2(d[1], d[0])                        # the outer normal (cos u, sin u, 0) faces the viewer near u = PHI
BACK = (PHI + math.pi / 2, PHI + 3 * math.pi / 2)
FRONT = (PHI - math.pi / 2, PHI + math.pi / 2)


def cyl(u, v):
    return (math.cos(u), math.sin(u), v)


def ell(t):
    return (math.cos(t), math.sin(t), 1 - math.cos(t) - math.sin(t))


O3 = (0.0, 0.0, 0.0)
A3, B3 = (1.0, 0.0, 0.0), (0.0, 1.0, 0.0)
C3 = (1 / R2, 1 / R2, 1 - R2)
D3 = (-1 / R2, -1 / R2, 1 + R2)
# back half of the cylinder and what lies inside it
S.surface(cyl, BACK, (ZB, ZT), nu=12, nv=4, fill=TEXT, stroke=TEXT, opacity=(0.04, 0.09),
          stroke_width=0.5, stroke_opacity=0.25)
S.line([O3, (1.7, 0, 0)], TEXT, 1.1, None, 0.55)
S.line([O3, (0, 1.7, 0)], TEXT, 1.1, None, 0.55)
S.line([O3, (0, 0, 3.5)], TEXT, 1.1, None, 0.55)
# the plane x + y + z = 1 over the disc of radius 1.35
RP = 1.35
disc = [(RP * math.cos(t), RP * math.sin(t), 1 - RP * (math.cos(t) + math.sin(t)))
        for t in [2 * math.pi * k / 96 for k in range(96)]]
S.polygon(disc, BASE, 0.16)
S.line(disc + [disc[0]], BASE, 0.9, None, 0.6)
S.curve(ell, 0, 2 * math.pi, THEORY, 2.6, 160)
S.guide([O3, A3], TEXT, 0.75, 1.2, "4 3")
S.guide([O3, D3], TEXT, 0.75, 1.2, "4 3")
# front half of the cylinder, then the front arc of the ellipse again on top
S.surface(cyl, FRONT, (ZB, ZT), nu=12, nv=4, fill=TEXT, stroke=TEXT, opacity=(0.04, 0.10),
          stroke_width=0.5, stroke_opacity=0.3)
for z in (ZB, ZT):
    S.curve(lambda u, z=z: cyl(u, z), 0, 2 * math.pi, TEXT, 1.0, 96, None, 0.5)
for u in FRONT:
    S.line([cyl(u, ZB), cyl(u, ZT)], TEXT, 1.0, None, 0.5)
S.curve(ell, FRONT[0], FRONT[1], THEORY, 2.6, 100)
# axes tips outside the cylinder
S.arrow((1.0, 0, 0), (1.7, 0, 0), TEXT, 1.1, 7.0, None, 0.55)
S.arrow((0, 1.0, 0), (0, 1.7, 0), TEXT, 1.1, 7.0, None, 0.55)
S.arrow((0, 0, 3.0), (0, 0, 3.5), TEXT, 1.1, 7.0, None, 0.55)
S.label((1.7, 0, 0), it("x"), -6, 14, TEXT, 12.5, "end")
S.label((0, 1.7, 0), it("y"), 8, 12, TEXT, 12.5)
S.label((0, 0, 3.5), it("z"), -8, 2, TEXT, 12.5, "end")
# points
S.point(O3, TEXT, 3.6)
S.point(A3, PRACTICE, 4.4)
S.point(B3, PRACTICE, 4.4)
S.point(D3, PRACTICE, 4.4)
S.point(C3, TEXT, 4.2)
splabel(S, O3, it("O"), -8, -6, TEXT, 12.5, "end")
splabel(S, A3, it("A"), -9, 14, PRACTICE, 13, "end", True)
splabel(S, B3, it("B"), 9, 14, PRACTICE, 13, "start", True)
splabel(S, C3, it("C") + ": yerel maks", 10, 14, TEXT, 12)
splabel(S, D3, it("D") + ": en uzak", -10, -8, PRACTICE, 12, "end", True)
splabel(S, (0, 1.7, 0), it("A") + ", " + it("B") + ": en yakın, uzaklık 1", 4, -14, PRACTICE, 12, "end", True)
save("silindir-duzlem", figure(
    int(pl.x0 + pl.w + 60), int(pl.y0 + pl.h + 60), [pl],
    "<em>x</em>² + <em>y</em>² = 1 silindiri ile <em>x</em> + <em>y</em> + <em>z</em> = 1 düzleminin kesişimi "
    "bir elipstir. Orijine en yakın noktalar <em>A</em> = (1, 0, 0) ve <em>B</em> = (0, 1, 0) (uzaklık 1), en "
    "uzak nokta <em>D</em> = (&#8722;1/&#8730;2, &#8722;1/&#8730;2, 1 + &#8730;2)'dir. <em>C</em> = "
    "(1/&#8730;2, 1/&#8730;2, 1 &#8722; &#8730;2) noktası <em>A</em> ile <em>B</em> arasındaki yayda bir yerel "
    "maksimumdur.",
    aria="Cylinder x^2 + y^2 = 1 cut by the plane x + y + z = 1 along an ellipse, with the nearest points "
         "A = (1, 0, 0) and B = (0, 1, 0), the local maximum C and the farthest point D, and dashed segments "
         "from the origin to A and D"))
