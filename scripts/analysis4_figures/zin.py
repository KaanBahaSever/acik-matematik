# -*- coding: utf-8 -*-
"""
Figures of the chapter "Jacobi Matrisi ve Zincir Kuralı"
(dersler/analiz-4/jacobi-matrisi-ve-zincir-kurali.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box and never directly under a heading.
The figures are NOT produced at build time. Run

    python scripts/analysis4_figures/zin.py
    python scripts/center_figures.py "analysis4-zin-*.md"
    python scripts/check_figure_labels.py "scripts/_figures/analysis4-zin-*.md"

and paste the markup of scripts/_figures/analysis4-zin-<name>.md into the .qmd.
The captions are Turkish on purpose; the aria labels are plain ASCII.

The composition ring and the nabla are not in the renderer's fallback font:
the ring is written as U+25E6 (white bullet), which is.
"""
import html
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, blob, closed_curve, dot, TEXT, THEORY, PRACTICE, BASE, BG, WIDE  # noqa: E402
from svg_plot3 import Camera, Space  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "analysis4-zin-"

MINUS, TIMES, RING, PARTIAL, BB_R = "&#8722;", "&#215;", "&#9702;", "&#8706;", "&#8477;"
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


def eq_plot(x0, y0, ppu, xr, yr):
    """Panel with the same number of pixels per unit on both axes."""
    return Plot(x0, y0, (xr[1] - xr[0]) * ppu, (yr[1] - yr[0]) * ppu, xr, yr)


def pixel_plot(W, H):
    """A panel whose data coordinates are the canvas pixels (y grows downward)."""
    return Plot(0, 0, W, H, (0, W), (H, 0))


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


def bezier(P0, C, P1, n=60):
    return [((1 - t) ** 2 * P0[0] + 2 * t * (1 - t) * C[0] + t * t * P1[0],
             (1 - t) ** 2 * P0[1] + 2 * t * (1 - t) * C[1] + t * t * P1[1])
            for t in (k / n for k in range(n + 1))]


def curved_arrow(p, P0, C, P1, color, width=1.7, head=8.0, cut0=0.0, cut1=0.0):
    """Quadratic Bezier arrow from P0 to P1 (control point C), trimmed by cut0 / cut1 pixels."""
    pts = bezier(P0, C, P1, 120)
    def trim(pts, cut):
        acc, i = 0.0, 0
        while i + 1 < len(pts) and acc < cut:
            acc += math.hypot(p.X(pts[i + 1][0]) - p.X(pts[i][0]), p.Y(pts[i + 1][1]) - p.Y(pts[i][1]))
            i += 1
        return pts[i:]
    pts = trim(pts, cut0)
    pts = trim(pts[::-1], cut1)[::-1]
    p.line(pts[:-4], color, width)
    p.arrow(pts[-5], pts[-1], color, width, head)


def ring_of(f, g):
    return f + " " + RING + " " + g


FG = ring_of(it("f"), it("g"))

# ============================================================
# paraboloit-afin: the tangent planes z = 0 and z = 2x + 2y - 2 of z = x^2 + y^2
# ============================================================
RB = 2.0                                          # radius of the drawn bowl


def bowl(r, phi):
    return (r * math.cos(phi), r * math.sin(phi), r * r)


def tplane(x, y):
    return 2 * x + 2 * y - 2


# Viewed from azimuth -20 deg (x toward the viewer, y to the right): the plane z = 2x + 2y - 2 is seen
# at a grazing angle, so its patch meets the side of the bowl at (1, 1, 2) as a visible tangency.
AZ = -20.0
cam = Camera(azimuth=AZ, elevation=22.0)
# the patch of z = 2x + 2y - 2 is a rectangle spanned by the level direction (1, -1, 0) and the
# steepest direction (1, 1, 4) of the plane: an xy-square would project to a thin diamond
E1 = (1 / math.sqrt(2), -1 / math.sqrt(2), 0.0)
E2 = (1 / math.sqrt(18), 1 / math.sqrt(18), 4 / math.sqrt(18))
T3 = [(1 + a * E1[0] + b * E2[0], 1 + a * E1[1] + b * E2[1], 2 + a * E1[2] + b * E2[2])
      for a, b in ((-0.85, -1.1), (0.85, -1.1), (0.85, 1.1), (-0.85, 1.1))]
assert all(abs(z - tplane(x, y)) < 1e-12 for x, y, z in T3)
B3 = [(-0.7, -0.7, 0.0), (0.7, -0.7, 0.0), (0.7, 0.7, 0.0), (-0.7, 0.7, 0.0)]
rim = [bowl(RB, 2 * math.pi * k / 48) for k in range(48)]
pl, S = fit_space(cam, rim + T3 + B3 + [(2.9, 0, 0), (0, 2.9, 0), (0, 0, 5.2)], 110, 40, 78, 0.35)
S.axes(2.9, 2.9, 5.2, labels=("x", "y", "z"))
a0 = math.radians(AZ)
BACK = (a0 + math.pi / 2, a0 + 3 * math.pi / 2)
FRONT = (a0 - math.pi / 2, a0 + math.pi / 2)
S.surface(bowl, (0.0, RB), BACK, nu=8, nv=14, fill=THEORY, stroke=THEORY, opacity=(0.05, 0.16),
          stroke_width=0.5, stroke_opacity=0.3)
S.curve(lambda t: bowl(RB, t), BACK[0], BACK[1], THEORY, 1.1, 80, None, 0.6)
# the tangent plane z = 0 at the vertex
S.polygon(B3, BASE, 0.22)
S.line(B3 + [B3[0]], BASE, 1.4, None, 0.9)
S.surface(bowl, (0.0, RB), FRONT, nu=8, nv=14, fill=THEORY, stroke=THEORY, opacity=(0.05, 0.18),
          stroke_width=0.5, stroke_opacity=0.35)
S.curve(lambda t: bowl(RB, t), FRONT[0], FRONT[1], THEORY, 1.5, 80, None, 0.85)
# the tangent plane at (1, 1, 2): it lies outside the bowl, in front of it
S.polygon(T3, PRACTICE, 0.2)
S.line(T3 + [T3[0]], PRACTICE, 1.4, None, 0.9)
S.point((0.0, 0.0, 0.0), BASE, 4.0)
S.point((1.0, 1.0, 2.0), PRACTICE, 4.2)
splabel(S, (0.0, 0.0, 0.0), it("f") + "(0, 0)", -9, 4, BASE, 12, "end")
splabel(S, (1.0, 1.0, 2.0), it("f") + "(1, 1)", 9, -6, PRACTICE, 12)
splabel(S, B3[1], it("z") + " = 0", 6, 10, BASE, 12)
splabel(S, T3[0], it("z") + " = 2" + it("x") + " + 2" + it("y") + " " + MINUS + " 2", 8, 12, PRACTICE, 12)
splabel(S, bowl(RB, math.radians(AZ + 90)), it("z") + " = " + it("x") + "² + " + it("y") + "²", 8, 4, THEORY, 12)
save("paraboloit-afin", figure(
    int(pl.x0 + pl.w + 130), int(pl.y0 + pl.h + 30), [pl],
    "<em>z</em> = <em>x</em>² + <em>y</em>² paraboloidi (<em>x</em>² + <em>y</em>² &#8804; 4 kısmı) ve "
    "afin yaklaşımların görüntü kümeleri. Tepedeki <em>f</em>(0, 0) = (0, 0, 0) noktasında teğet düzlem "
    "<em>z</em> = 0'dır (yeşil); <em>f</em>(1, 1) = (1, 1, 2) noktasında ise <em>z</em> = 2<em>x</em> + "
    "2<em>y</em> &#8722; 2 düzlemidir (turuncu). İki düzlem yüzeye yalnız bu noktalarda değer ve yüzeyin "
    "altında kalır.",
    aria="Paraboloid z = x^2 + y^2 over the disc of radius 2 with a small patch of the plane z = 0 at the "
         "vertex and a patch of the plane z = 2x + 2y - 2 touching it at (1, 1, 2)"))

# ============================================================
# zincir-diyagrami: g then f, and the derivatives composed in the same order
# ============================================================
W, H = 640, 420
p = pixel_plot(W, H)
BOX_Y0, BOX_Y1 = 70, 190
CX = (110, 320, 530)
BOX_W = 170


def space_box(cx, name):
    x0 = cx - BOX_W / 2
    p.add(f'<rect x="{x0:.1f}" y="{BOX_Y0}" width="{BOX_W}" height="{BOX_Y1 - BOX_Y0}" rx="10" '
          f'fill="{TEXT}" fill-opacity="0.035" stroke="{TEXT}" stroke-opacity="0.45" stroke-width="1.1"/>')
    p.label(cx, BOX_Y1, name, 0, 20, TEXT, 13.5, "middle")


RN, RM, RP = (BB_R + sup(it(s), 9.5) for s in ("n", "m", "p"))
for cx, name in zip(CX, (RN, RM, RP)):
    space_box(cx, name)
A_PT, B_PT, C_PT = (98.0, 140.0), (318.0, 140.0), (536.0, 140.0)
closed_curve(p, blob(112, 132, 44, [(5, 2, 0.6), (3, 3, 2.0)]), THEORY, 1.4, "5 3", THEORY, 0.14)
closed_curve(p, blob(322, 132, 46, [(5, 2, 2.1), (3, 3, 0.4)]), BASE, 1.4, "5 3", BASE, 0.14)
p.label(112, 168, it("U"), 0, 0, THEORY, 14, "middle", True)
p.label(300, 104, it("V"), 0, 0, BASE, 14, "middle", True)
dot(p, A_PT, TEXT, 3.8)
dot(p, B_PT, TEXT, 3.8)
dot(p, C_PT, TEXT, 3.8)
p.label(*A_PT, it("a"), -8, -6, TEXT, 13, "end")
p.label(*B_PT, it("b") + " = " + it("g") + "(" + it("a") + ")", 0, 20, TEXT, 12, "middle")
p.label(*C_PT, "(" + FG + ")(" + it("a") + ")", 0, 20, TEXT, 12, "middle")
curved_arrow(p, A_PT, (208, 78), B_PT, THEORY, 1.8, 8.0, 7, 7)
curved_arrow(p, B_PT, (427, 78), C_PT, BASE, 1.8, 8.0, 7, 7)
curved_arrow(p, A_PT, (317, -58), C_PT, PRACTICE, 1.8, 8.0, 7, 7)
p.label(208, 99, it("g"), 0, 0, THEORY, 14, "middle")
p.label(427, 99, it("f"), 0, 0, BASE, 14, "middle")
p.label(317, 41, FG, 0, -9, PRACTICE, 14, "middle")
# the derivatives: three small coordinate frames and the linear maps between them
AY = 285


def frame(cx):
    ox, oy = cx - 26, AY + 20
    p.arrow((ox, oy), (ox + 56, oy), TEXT, 1.1, 6.5, None, 0.55)
    p.arrow((ox, oy), (ox, oy - 48), TEXT, 1.1, 6.5, None, 0.55)
    p.arrow((ox, oy), (ox + 24, oy - 30), TEXT, 1.1, 6.5, None, 0.55)


for cx, name in zip(CX, (RN, RM, RP)):
    frame(cx)
    p.label(cx, AY + 20, name, 0, 22, TEXT, 13.5, "middle")
DGA = it("D") + it("g") + "(" + it("a") + ")"
DFB = it("D") + it("f") + "(" + it("g") + "(" + it("a") + "))"
for (x0, x1), name, dims, col in (((CX[0] + 52, CX[1] - 48), DGA, it("m") + " " + TIMES + " " + it("n"), THEORY),
                                  ((CX[1] + 52, CX[2] - 48), DFB, it("p") + " " + TIMES + " " + it("m"), BASE)):
    p.arrow((x0, AY), (x1, AY), col, 1.8, 8.0)
    p.label((x0 + x1) / 2, AY, name, 0, -9, col, 12, "middle")
    p.label((x0 + x1) / 2, AY, dims, 0, 17, col, 11.5, "middle")
LY = 360
p.arrow((CX[0], LY), (CX[2], LY), PRACTICE, 1.8, 8.0)
p.line([(CX[0], LY - 5), (CX[0], LY + 5)], PRACTICE, 1.8)
p.label(CX[1], LY, it("D") + "(" + FG + ")(" + it("a") + ") = " + DFB + " " + RING + " " + DGA, 0, 20,
        PRACTICE, 12.5, "middle")
p.label(CX[1], LY, it("p") + " " + TIMES + " " + it("n"), 0, 37, PRACTICE, 11.5, "middle")
save("zincir-diyagrami", figure(
    W, H, [p],
    "Zincir kuralının şeması. Üstte <em>g</em>, <em>a</em> noktasını <em>b</em> = <em>g</em>(<em>a</em>) "
    "noktasına, <em>f</em> de <em>b</em>'yi (<em>f</em> &#8728; <em>g</em>)(<em>a</em>) noktasına götürür. "
    "Altta türevler aynı sırayla bileşir: <em>m</em> &#215; <em>n</em> tipindeki <em>Dg</em>(<em>a</em>) "
    "ile <em>p</em> &#215; <em>m</em> tipindeki <em>Df</em>(<em>g</em>(<em>a</em>)) matrislerinin çarpımı "
    "<em>p</em> &#215; <em>n</em> tipindeki <em>D</em>(<em>f</em> &#8728; <em>g</em>)(<em>a</em>) matrisidir.",
    css_class=WIDE,
    aria="Top row: the point a in U in R^n, g maps it to b = g(a) in V in R^m, f maps b to (f o g)(a) in R^p, "
         "and a long arrow f o g. Bottom row: coordinate frames R^n, R^m, R^p joined by the arrows Dg(a) "
         "of type m x n and Df(g(a)) of type p x m, and the long arrow D(f o g)(a) of type p x n"))

# ============================================================
# trees: the dependence diagrams of the chain rule
# ============================================================
NODE_R = 13.0


def node(p, P, name, color=TEXT, hi=False):
    p.add(f'<circle cx="{P[0]:.1f}" cy="{P[1]:.1f}" r="{NODE_R}" fill="{BG}" stroke="{color}" '
          f'stroke-width="{1.8 if hi else 1.1}" stroke-opacity="{1.0 if hi else 0.6}"/>')
    p.label(P[0], P[1], it(name), 0, 5, color, 14.5, "middle")


def edge(p, A, B, label, frac, hi, size=12.0):
    L = math.hypot(B[0] - A[0], B[1] - A[1])
    ux, uy = (B[0] - A[0]) / L, (B[1] - A[1]) / L
    s = (A[0] + ux * NODE_R, A[1] + uy * NODE_R)
    e = (B[0] - ux * NODE_R, B[1] - uy * NODE_R)
    if hi:
        p.line([s, e], PRACTICE, 2.6)
    else:
        p.line([s, e], TEXT, 1.1, None, 0.45)
    m = (A[0] + (B[0] - A[0]) * frac, A[1] + (B[1] - A[1]) * frac)
    plabel(p, m[0], m[1], label, 0, 0.3 * size, PRACTICE if hi else TEXT, size, "middle", opacity=1.0)


def dfrac(num, den):
    return PARTIAL + it(num) + "/" + PARTIAL + it(den)


def chain_tree(W, top, mids, leaves, spread, target, fracs, H=270):
    """u on top, the intermediate variables below it, the independent variables as leaves."""
    p = pixel_plot(W, H)
    U_P = (W / 2, 32.0)
    MY, LY = 136.0, 250.0
    mid_x = [W / 2 + (k - (len(mids) - 1) / 2) * top for k in range(len(mids))]
    for mx, m in zip(mid_x, mids):
        edge(p, U_P, (mx, MY), dfrac("u", m), 0.5, True)
        for j, leaf in enumerate(leaves):
            lx = mx + (j - (len(leaves) - 1) / 2) * spread
            edge(p, (mx, MY), (lx, LY), dfrac(m, leaf), fracs[j], leaf == target, 11.5)
    node(p, U_P, "u", PRACTICE, True)
    for mx, m in zip(mid_x, mids):
        node(p, (mx, MY), m, PRACTICE, True)
        for j, leaf in enumerate(leaves):
            lx = mx + (j - (len(leaves) - 1) / 2) * spread
            hi = leaf == target
            node(p, (lx, LY), leaf, PRACTICE if hi else TEXT, hi)
    return p


p = chain_tree(660, 160, ("x", "y", "z", "w"), ("s", "t"), 88, "s", (0.52, 0.52))
save("dort-ara-agac", figure(
    660, 270, [p],
    "<em>u</em> = <em>f</em>(<em>x</em>, <em>y</em>, <em>z</em>, <em>w</em>) için ağaç diyagramı: her dalın "
    "üzerinde ilgili kısmi türev yazılıdır. <em>u</em>'dan <em>s</em> yapraklarına inen dört yol (renkli) "
    "&#8706;<em>u</em>/&#8706;<em>s</em> toplamının dört terimini verir; <em>t</em> yaprakları da "
    "&#8706;<em>u</em>/&#8706;<em>t</em> için aynı işi görür.",
    css_class=WIDE,
    aria="Tree diagram: u on top, x, y, z, w in the middle, and the leaves s and t under each of them; "
         "the four paths from u down to the s leaves are highlighted"))

p = chain_tree(680, 210, ("x", "y", "z"), ("r", "s", "t"), 66, "s", (0.44, 0.64, 0.44))
save("rst-agac", figure(
    680, 270, [p],
    "<em>u</em>'nun <em>x</em>, <em>y</em>, <em>z</em> ara değişkenlerine, bunların da <em>r</em>, <em>s</em>, "
    "<em>t</em> bağımsız değişkenlerine bağlılığını gösteren ağaç. &#8706;<em>u</em>/&#8706;<em>s</em> için "
    "<em>u</em> &#8594; <em>x</em> &#8594; <em>s</em>, <em>u</em> &#8594; <em>y</em> &#8594; <em>s</em> ve "
    "<em>u</em> &#8594; <em>z</em> &#8594; <em>s</em> yolları (renkli) izlenir.",
    css_class=WIDE,
    aria="Tree diagram: u on top, x, y, z in the middle, and the leaves r, s, t under each of them; "
         "the three paths from u down to the s leaves are highlighted"))
