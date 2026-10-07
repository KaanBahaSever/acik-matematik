# -*- coding: utf-8 -*-
"""
Figures of the chapter "Çok Katlı İntegrallerde Değişken Değiştirme"
(dersler/integral-calculus/cok-katli-integrallerde-degisken-degistirme.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box and never directly under a heading.
Concept figures stay visible: donusum and kucuk-dikdortgen in the prose,
izgara and kuresel-kutu in the statements of the two theorems (before the
proof blocks), kutupsal under the question of the polar example. The figures
kare-parabol, yamuk and hiperbol show solution steps and sit in .cozum.

The figures are NOT produced at build time. Run

    python scripts/calculus_figures/ddg.py
    python scripts/center_figures.py "calculus-ddg-*.md"
    python scripts/check_figure_labels.py "scripts/_figures/calculus-ddg-*.md"

and paste the markup of scripts/_figures/calculus-ddg-<name>.md into the .qmd.
Captions are Turkish on purpose; aria labels are plain ASCII.

Conventions of the chapter: the uv-plane (region S) is drawn on the left in
the BASE color, the xy-plane (region R = T(S)) on the right in THEORY, and the
map T points from left to right.
"""
import html
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, dot, blob, TEXT, THEORY, PRACTICE, BASE, REMARK, BG, WIDE  # noqa: E402
from svg_plot3 import Camera, Space, vdot  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "calculus-ddg-"

MINUS = "&#8722;"
APPROX = "&#8776;"
DELTA = "&#916;"


def save(name, markup):
    (OUT_DIR / f"{PREFIX}{name}.md").write_text(markup, encoding="utf-8", newline="\n")
    print(f"{PREFIX}{name}.md")


def it(s):
    """Italic run inside an SVG <text>."""
    return f'<tspan font-style="italic">{s}</tspan>'


def bf(s):
    """Bold upright run (vectors)."""
    return f'<tspan font-weight="700">{s}</tspan>'


def sub(s, size=10):
    """Subscript inside an SVG <text>."""
    return f'<tspan font-size="{size}" dy="3.5">{s}</tspan><tspan dy="-3.5">&#8203;</tspan>'


def sup(s, size=10):
    """Superscript inside an SVG <text>."""
    return f'<tspan font-size="{size}" dy="-5">{s}</tspan><tspan dy="5">&#8203;</tspan>'


def eq_plot(x0, y0, ppu, xr, yr):
    """Panel with the same number of pixels per unit on both axes."""
    return Plot(x0, y0, (xr[1] - xr[0]) * ppu, (yr[1] - yr[0]) * ppu, xr, yr)


def pixel_plot(W, H):
    """A panel whose data coordinates are the canvas pixels (y down)."""
    return Plot(0, 0, W, H, (0, W), (H, 0))


def connector(W, H, x0, x1, y, labels=((None, 1),)):
    """Horizontal arrows between two panels: ('T', 1) points right, ('T^-1', -1) left."""
    q = pixel_plot(W, H)
    n = len(labels)
    for k, (s, direction) in enumerate(labels):
        s = s or it("T")
        yy = y + (k - (n - 1) / 2) * 34
        a, b = (x0, x1) if direction > 0 else (x1, x0)
        q.arrow((a, yy), (b, yy), TEXT, 1.6, 8.0, None, 0.85)
        q.text_px((x0 + x1) / 2, yy - 7, s, TEXT, 13, "middle")
    return q


def T_sq(u, v):
    """The running example x = u^2 - v^2, y = 2uv."""
    return (u * u - v * v, 2 * u * v)


def seg(f, t0, t1, n=60):
    return [f(t0 + (t1 - t0) * k / n) for k in range(n + 1)]


def mid_arrow(p, pts, color, width=2.0, head=9.0):
    """Arrowhead in the middle of a polyline, pointing along it."""
    k = len(pts) // 2
    p.arrow(pts[k - 1], pts[k + 1], color, width, head)


def frame_axes(p, xl, yl):
    p.origin_axes(it(xl), it(yl), opacity=0.5)


def text_w(s, size):
    """Rough advance width of a label (0.5 em per visible character, tspans at their own size)."""
    def count(t):
        return len(html.unescape(re.sub(r"<[^>]+>", "", t)).replace(chr(0x200B), ""))
    width = 0.0
    for m in re.finditer(r'<tspan font-size="([\d.]+)"[^>]*>(.*?)</tspan>', s):
        width += count(m.group(2)) * 0.5 * float(m.group(1))
    rest = re.sub(r'<tspan font-size="[\d.]+"[^>]*>.*?</tspan>', "", s)
    return width + count(rest) * 0.5 * size


def plabel(p, x, y, s, dx=0, dy=0, color=TEXT, size=11.5, anchor="start", bold=False):
    """Label on a page-coloured plate, for text that must sit on grid lines or shading."""
    px, py = p.X(x) + dx, p.Y(y) + dy
    w = text_w(s, size)
    x0 = px - (w / 2 if anchor == "middle" else w if anchor == "end" else 0)
    p.add(f'<rect x="{x0 - 2.5:.1f}" y="{py - 0.8 * size - 1:.1f}" width="{w + 5:.1f}" '
          f'height="{size + 4:.1f}" rx="3" fill="{BG}" opacity="0.85"/>')
    p.label(x, y, s, dx, dy, color, size, anchor, bold)


U0, V0 = it("u") + sub("0"), it("v") + sub("0")
X0, Y0 = it("x") + sub("0"), it("y") + sub("0")
T_INV = it("T") + sup(MINUS + "1")

# ============================================================
# donusum: a region S and its image R = T(S)
# ============================================================
pl = eq_plot(40, 60, 120, (-0.25, 1.75), (-0.25, 1.15))
pr = eq_plot(370, 30, 92, (-0.3, 2.15), (-0.25, 2.05))
frame_axes(pl, "u", "v")
frame_axes(pr, "x", "y")
S_pts = blob(1.1, 0.55, 0.31, [(0.045, 2, 0.6), (0.03, 3, 1.9)], samples=160)
pl.polygon(S_pts, BASE, 0.14)
pl.line(S_pts + [S_pts[0]], BASE, 2.0)
R_pts = [T_sq(a, b) for a, b in S_pts]
pr.polygon(R_pts, THEORY, 0.14)
pr.line(R_pts + [R_pts[0]], THEORY, 2.0)
P1 = (1.2, 0.46)
Q1 = T_sq(*P1)
dot(pl, P1, TEXT, 3.8)
dot(pr, Q1, TEXT, 3.8)
pl.line([P1, (1.5, 0.22)], TEXT, 0.9, None, 0.7)
pl.label(1.5, 0.22, "(" + it("u") + sub("1") + ", " + it("v") + sub("1") + ")", 3, 12, TEXT, 11.5, "start")
pr.label(*Q1, "(" + it("x") + sub("1") + ", " + it("y") + sub("1") + ")", 0, 18, TEXT, 11.5, "middle")
pl.label(0.98, 0.65, it("S"), 0, 0, BASE, 15, "middle", True)
pr.label(0.75, 1.5, it("R") + " = " + it("T") + "(" + it("S") + ")", 0, 0, THEORY, 13.5, "middle", True)
W, H = 610, 270
mid_y = pl.Y(0.55)
q = connector(W, H, pl.x0 + pl.w + 18, pr.x0 - 6, mid_y, ((it("T"), 1), (T_INV, -1)))
save("donusum", figure(
    W, H, [pl, pr, q],
    "<em>T</em> dönüşümü <em>uv</em>-düzlemindeki <em>S</em> bölgesini <em>xy</em>-düzlemindeki "
    "<em>R</em> = <em>T</em>(<em>S</em>) bölgesine, her (<em>u</em><sub>1</sub>, <em>v</em><sub>1</sub>) "
    "noktasını da görüntüsü (<em>x</em><sub>1</sub>, <em>y</em><sub>1</sub>) noktasına götürür. "
    "<em>T</em> bire bir ise <em>T</em><sup>&#8722;1</sup> geri dönüşü sağlar. Burada <em>T</em>(<em>u</em>, "
    "<em>v</em>) = (<em>u</em>² &#8722; <em>v</em>², 2<em>uv</em>) alınmıştır.",
    WIDE,
    aria="Left: a rounded region S in the uv-plane with a marked point (u1, v1). Right: its image "
         "R = T(S) in the xy-plane with the image point (x1, y1). Arrows T and T inverse between the panels"))

# ============================================================
# kare-parabol: Example 1, the unit square under x = u^2 - v^2, y = 2uv
# ============================================================
SIDE_COL = (BASE, THEORY, PRACTICE, REMARK)
pl = eq_plot(40, 60, 125, (-0.3, 1.45), (-0.3, 1.4))
pr = eq_plot(380, 30, 96, (-1.5, 1.55), (-0.35, 2.4))
frame_axes(pl, "u", "v")
frame_axes(pr, "x", "y")
sq = [(0, 0), (1, 0), (1, 1), (0, 1)]
pl.polygon(sq, BASE, 0.13)
sides_uv = [seg(lambda t: (t, 0.0), 0, 1), seg(lambda t: (1.0, t), 0, 1),
            seg(lambda t: (1 - t, 1.0), 0, 1), seg(lambda t: (0.0, 1 - t), 0, 1)]
for pts, col in zip(sides_uv, SIDE_COL):
    pl.line(pts, col, 2.6)
    mid_arrow(pl, pts, col)
for (a, b), s, dx, dy, anc in (((1, 0), "(1, 0)", 6, 16, "start"), ((1, 1), "(1, 1)", 6, -7, "start"),
                               ((0, 1), "(0, 1)", -7, -7, "end")):
    dot(pl, (a, b), TEXT, 3.2)
    pl.label(a, b, s, dx, dy, TEXT, 11.5, anc)
pl.label(0.5, 0, it("S") + sub("1"), 0, 18, BASE, 13, "middle", True)
pl.label(1, 0.5, it("S") + sub("2"), 9, 5, THEORY, 13, "start", True)
pl.label(0.5, 1, it("S") + sub("3"), 0, -9, PRACTICE, 13, "middle", True)
pl.label(0, 0.5, it("S") + sub("4"), -9, 5, REMARK, 13, "end", True)
pl.label(0.5, 0.5, it("S"), 0, 5, BASE, 15, "middle", True)
sides_xy = [[T_sq(*P) for P in pts] for pts in sides_uv]
boundary = [P for pts in sides_xy for P in pts]
pr.polygon(boundary, THEORY, 0.13)
for pts, col in zip(sides_xy, SIDE_COL):
    pr.line(pts, col, 2.6)
    mid_arrow(pr, pts, col)
for (a, b), s, dx, dy, anc in (((1, 0), "(1, 0)", 6, 16, "start"), ((-1, 0), "(" + MINUS + "1, 0)", -6, 16, "end"),
                               ((0, 2), "(0, 2)", 8, -6, "start")):
    dot(pr, (a, b), TEXT, 3.2)
    pr.label(a, b, s, dx, dy, TEXT, 11.5, anc)
pr.label(0.5, 0, it("T") + "(" + it("S") + sub("1") + ")", 0, 18, BASE, 12, "middle", True)
pr.label(-0.5, 0, it("T") + "(" + it("S") + sub("4") + ")", 0, 18, REMARK, 12, "middle", True)
pr.label(0.5, 1.72, it("x") + " = 1 " + MINUS + " " + it("y") + "²/4", 0, 0, THEORY, 12, "start", True)
pr.label(-0.5, 1.72, it("x") + " = " + it("y") + "²/4 " + MINUS + " 1", 0, 0, PRACTICE, 12, "end", True)
pr.label(0, 0.7, it("R"), 0, 5, THEORY, 15, "middle", True)
W, H = 700, 330
q = connector(W, H, pl.x0 + pl.w + 12, pr.x0 - 4, pl.Y(0.5))
save("kare-parabol", figure(
    W, H, [pl, pr, q],
    "<em>x</em> = <em>u</em>² &#8722; <em>v</em>², <em>y</em> = 2<em>uv</em> dönüşümü birim karenin "
    "<em>S</em><sub>1</sub>, <em>S</em><sub>2</sub>, <em>S</em><sub>3</sub>, <em>S</em><sub>4</sub> "
    "kenarlarını aynı renkteki sınır parçalarına götürür. Kare saat yönünün tersine dolaşılınca "
    "<em>R</em>'nin sınırı da saat yönünün tersine dolaşılır.",
    WIDE,
    aria="Left: the unit square in the uv-plane with sides S1 to S4 drawn counterclockwise in four colors. "
         "Right: the region R bounded by the x axis and the parabolas x = 1 - y^2/4 and x = y^2/4 - 1, "
         "with vertices (-1, 0), (1, 0) and (0, 2) and the image sides in matching colors"))

# ============================================================
# kucuk-dikdortgen: a small rectangle and the parallelogram that approximates its image
# ============================================================
UA, UB, VA, VB = 1.0, 1.5, 0.4, 0.8
DU, DV = UB - UA, VB - VA
pl = eq_plot(40, 110, 135, (-0.2, 1.8), (-0.2, 1.0))
pr = eq_plot(400, 30, 100, (-0.15, 2.45), (-0.15, 2.65))
frame_axes(pl, "u", "v")
frame_axes(pr, "x", "y")
rect = [(UA, VA), (UB, VA), (UB, VB), (UA, VB)]
pl.polygon(rect, BASE, 0.16, BASE, 2.0)
dot(pl, (UA, VA), TEXT, 3.6)
pl.label(UA, VA, "(" + U0 + ", " + V0 + ")", -6, 17, TEXT, 11.5, "end")
pl.label((UA + UB) / 2, VA, DELTA + it("u"), 0, 17, TEXT, 12, "middle")
pl.label(UA, (VA + VB) / 2, DELTA + it("v"), -7, 5, TEXT, 12, "end")
pl.label((UA + UB) / 2, (VA + VB) / 2, it("S"), 0, 5, BASE, 15, "middle", True)
bottom = seg(lambda t: T_sq(t, VA), UA, UB)
right = seg(lambda t: T_sq(UB, t), VA, VB)
top = seg(lambda t: T_sq(t, VB), UB, UA)
left = seg(lambda t: T_sq(UA, t), VB, VA)
pr.polygon(bottom + right + top + left, THEORY, 0.15)
pr.line(right, THEORY, 1.6)
pr.line(top, THEORY, 1.6)
pr.line(bottom, THEORY, 2.4)
pr.line(left, THEORY, 2.4)
P = T_sq(UA, VA)                                 # (0.84, 0.8)
ru = (2 * UA * DU, 2 * VA * DU)                  # du * r_u = (1, 0.4)
rv = (-2 * VA * DV, 2 * UA * DV)                 # dv * r_v = (-0.32, 0.8)
A = (P[0] + ru[0], P[1] + ru[1])
B = (P[0] + rv[0], P[1] + rv[1])
C = (A[0] + rv[0], A[1] + rv[1])
pr.polygon([P, A, C, B], PRACTICE, 0.10, PRACTICE, 1.2, "5 3")
pr.arrow(P, A, PRACTICE, 2.2, 9)
pr.arrow(P, B, PRACTICE, 2.2, 9)
dot(pr, P, TEXT, 3.6)
pr.label(*P, "(" + X0 + ", " + Y0 + ")", -8, 6, TEXT, 11.5, "end")
mid_a = (P[0] + ru[0] / 2, P[1] + ru[1] / 2)
mid_b = (P[0] + rv[0] / 2, P[1] + rv[1] / 2)
pr.label(*mid_a, DELTA + it("u") + " " + bf("r") + sub(it("u")), 6, 30, PRACTICE, 12.5, "start", True)
plabel(pr, *mid_b, DELTA + it("v") + " " + bf("r") + sub(it("v")), 9, 4, PRACTICE, 12.5, "start", True)
end_b = bottom[-1]
pr.label(*end_b, bf("r") + "(" + it("u") + ", " + V0 + ")", 6, 18, THEORY, 12, "start")
top_l = left[0]
pr.label(*top_l, bf("r") + "(" + U0 + ", " + it("v") + ")", -6, -4, THEORY, 12, "end")
pr.label(1.84, 1.6, it("R"), 0, 5, THEORY, 15, "middle", True)
W, H = 680, 330
q = connector(W, H, pl.x0 + pl.w + 12, pr.x0 - 4, pl.Y(0.6))
save("kucuk-dikdortgen", figure(
    W, H, [pl, pr, q],
    "Kenarları &#916;<em>u</em> ve &#916;<em>v</em> olan küçük <em>S</em> dikdörtgeninin görüntüsü eğri "
    "kenarlı bir <em>R</em> bölgesidir. <em>R</em>, (<em>x</em><sub>0</sub>, <em>y</em><sub>0</sub>) "
    "köşesindeki &#916;<em>u</em> <b>r</b><sub><em>u</em></sub> ve &#916;<em>v</em> "
    "<b>r</b><sub><em>v</em></sub> teğet vektörlerinin gerdiği paralelkenara (kesikli) yakındır. Burada "
    "<em>T</em>(<em>u</em>, <em>v</em>) = (<em>u</em>² &#8722; <em>v</em>², 2<em>uv</em>), <em>S</em> = "
    "[1; 1,5] &#215; [0,4; 0,8] alınmıştır.",
    WIDE,
    aria="Left: a small rectangle S with lower left corner (u0, v0) and sides du, dv. Right: its curved "
         "image R with corner (x0, y0), the image curves r(u, v0) and r(u0, v), and the dashed "
         "parallelogram spanned by the tangent vectors du r_u and dv r_v"))

# ============================================================
# izgara: Riemann sum over a grid of S and the curved grid of images
# ============================================================
UL, UR, VL, VR = 0.7, 1.5, 0.2, 0.9
NU, NV = 6, 5
du, dv = (UR - UL) / NU, (VR - VL) / NV
pl = eq_plot(40, 100, 210, (-0.12, 1.65), (-0.12, 1.02))
pr = eq_plot(470, 30, 92, (-0.6, 2.4), (-0.15, 2.85))
frame_axes(pl, "u", "v")
frame_axes(pr, "x", "y")
CU, CV, EA, EB = 1.1, 0.55, 0.37, 0.31
ell = [(CU + EA * math.cos(2 * math.pi * k / 160), CV + EB * math.sin(2 * math.pi * k / 160)) for k in range(161)]
pl.polygon(ell, BASE, 0.12)
pr.polygon([T_sq(*P) for P in ell], THEORY, 0.12)
for i in range(NU + 1):
    uu = UL + i * du
    pl.line([(uu, VL), (uu, VR)], TEXT, 0.8, None, 0.45)
    pr.line(seg(lambda t: T_sq(uu, t), VL, VR), TEXT, 0.8, None, 0.45)
for j in range(NV + 1):
    vv = VL + j * dv
    pl.line([(UL, vv), (UR, vv)], TEXT, 0.8, None, 0.45)
    pr.line(seg(lambda t: T_sq(t, vv), UL, UR), TEXT, 0.8, None, 0.45)
pl.line(ell, BASE, 2.2)
pr.line([T_sq(*P) for P in ell], THEORY, 2.2)
I, J = 3, 3
ui, vj = UL + I * du, VL + J * dv
cell = [(ui, vj), (ui + du, vj), (ui + du, vj + dv), (ui, vj + dv)]
pl.polygon(cell, BASE, 0.45, BASE, 1.4)
img = (seg(lambda t: T_sq(t, vj), ui, ui + du, 12) + seg(lambda t: T_sq(ui + du, t), vj, vj + dv, 12)
       + seg(lambda t: T_sq(t, vj + dv), ui + du, ui, 12) + seg(lambda t: T_sq(ui, t), vj + dv, vj, 12))
pr.polygon(img, THEORY, 0.45, THEORY, 1.4)
dot(pl, (ui, vj), TEXT, 3.4)
dot(pr, T_sq(ui, vj), TEXT, 3.4)
# leaders from the labels to the highlighted cells
lab_l = (1.55, 1.0)
pl.line([(ui + du * 0.7, vj + dv * 0.7), (lab_l[0] - 0.04, lab_l[1] - 0.03)], TEXT, 0.9, None, 0.7)
pl.label(*lab_l, it("S") + sub(it("ij")), 0, 0, BASE, 13, "start", True)
Rc = T_sq(ui + du * 0.6, vj + dv * 0.6)
lab_r = (1.95, 2.45)
pr.line([Rc, (lab_r[0] - 0.05, lab_r[1] - 0.06)], TEXT, 0.9, None, 0.7)
pr.label(*lab_r, it("R") + sub(it("ij")), 0, 0, THEORY, 13, "start", True)
plabel(pl, ui, vj, "(" + it("u") + sub(it("i")) + ", " + it("v") + sub(it("j")) + ")", -6, 17, TEXT, 11, "end")
xi, yj = T_sq(ui, vj)
plabel(pr, xi, yj, "(" + it("x") + sub(it("i")) + ", " + it("y") + sub(it("j")) + ")", 8, 15, TEXT, 11, "start")
pl.label(UL, CV, it("S"), -10, 5, BASE, 15, "end", True)
pr.label(*T_sq(UL, 0.9), it("R"), -8, 0, THEORY, 15, "end", True)
pl.label(ui + du / 2, VL, DELTA + it("u"), 0, 15, TEXT, 11, "middle")
W, H = 790, 340
q = connector(W, H, pl.x0 + pl.w + 14, pr.x0 - 10, pl.Y(0.55))
save("izgara", figure(
    W, H, [pl, pr, q],
    "<em>S</em> bölgesi &#916;<em>u</em> &#215; &#916;<em>v</em> boyutlu <em>S<sub>ij</sub></em> "
    "dikdörtgenlerine bölünür; <em>T</em> bu ızgarayı <em>R</em> üzerinde eğri bir ızgaraya götürür. "
    "Her <em>R<sub>ij</sub></em> parçasının alanı yaklaşık |&#8706;(<em>x</em>, <em>y</em>)/&#8706;(<em>u</em>, "
    "<em>v</em>)| &#916;<em>u</em> &#916;<em>v</em> olur (burada <em>T</em>(<em>u</em>, <em>v</em>) = "
    "(<em>u</em>² &#8722; <em>v</em>², 2<em>uv</em>)).",
    WIDE,
    aria="Left: an elliptical region S in the uv-plane covered by a rectangular grid, one cell S_ij "
         "highlighted with corner (u_i, v_j). Right: the image region R with the curved image grid "
         "and the highlighted image cell R_ij with corner (x_i, y_j)"))

# ============================================================
# kutupsal: the polar map sends a rectangle to a polar rectangle
# ============================================================
RA, RB, AL, BE = 1.0, 2.0, 0.4, 1.1
pl = eq_plot(40, 80, 105, (-0.2, 2.55), (-0.15, 1.45))
pr = eq_plot(400, 30, 98, (-0.2, 2.25), (-0.2, 2.2))
frame_axes(pl, "r", "&#952;")
frame_axes(pr, "x", "y")
box = [(RA, AL), (RB, AL), (RB, BE), (RA, BE)]
pl.polygon(box, BASE, 0.15, BASE, 2.0)
for xx in (RA, RB):
    pl.line([(xx, 0), (xx, AL)], TEXT, 0.9, "4 3", 0.55)
for yy in (AL, BE):
    pl.line([(0, yy), (RA, yy)], TEXT, 0.9, "4 3", 0.55)
pl.label(RA, 0, it("a"), 0, 16, TEXT, 12, "middle")
pl.label(RB, 0, it("b"), 0, 16, TEXT, 12, "middle")
pl.label(0, AL, "&#945;", -7, 5, TEXT, 12.5, "end")
pl.label(0, BE, "&#946;", -7, 5, TEXT, 12.5, "end")
pl.label(RA, (AL + BE) / 2, it("r") + " = " + it("a"), 7, 5, BASE, 12, "start")
pl.label(RB, (AL + BE) / 2, it("r") + " = " + it("b"), 7, 5, BASE, 12, "start")
pl.label((RA + RB) / 2, AL, "&#952; = &#945;", 0, 16, BASE, 12, "middle")
pl.label((RA + RB) / 2, BE, "&#952; = &#946;", 0, -8, BASE, 12, "middle")
pl.label((RA + RB) / 2, (AL + BE) / 2, it("S"), 0, 5, BASE, 15, "middle", True)


def pol(r, t):
    return (r * math.cos(t), r * math.sin(t))


region = seg(lambda t: pol(RB, t), AL, BE) + seg(lambda t: pol(RA, t), BE, AL)
pr.polygon(region, THEORY, 0.15)
pr.line(seg(lambda t: pol(RA, t), AL, BE), THEORY, 2.0)
pr.line(seg(lambda t: pol(RB, t), AL, BE), THEORY, 2.0)
for t in (AL, BE):
    pr.line([(0, 0), pol(RA, t)], TEXT, 0.9, "4 3", 0.55)
    pr.line([pol(RA, t), pol(RB, t)], THEORY, 2.0)
pr.line(seg(lambda t: pol(0.42, t), 0, AL, 20), TEXT, 1.0, None, 0.7)
pr.line(seg(lambda t: pol(0.62, t), 0, BE, 30), TEXT, 1.0, None, 0.7)
pr.label(*pol(0.42, AL / 2), "&#945;", 6, 5, TEXT, 12, "start")
pr.label(*pol(0.62, 0.85), "&#946;", 4, -2, TEXT, 12, "start")
pr.label(*pol(1.08, 0.9), it("r") + " = " + it("a"), 0, 4, THEORY, 12, "start")
pr.label(*pol(RB, (AL + BE) / 2), it("r") + " = " + it("b"), 8, 0, THEORY, 12, "start")
pr.label(*pol((RA + RB) / 2, AL), "&#952; = &#945;", 8, 14, THEORY, 12, "start")
pr.label(*pol((RA + RB) / 2, BE), "&#952; = &#946;", -10, -2, THEORY, 12, "end")
pr.label(*pol(1.62, 0.6), it("R"), 0, 5, THEORY, 15, "middle", True)
W, H = 650, 300
q = connector(W, H, pl.x0 + pl.w + 14, pr.x0 - 6, pl.Y(0.75))
save("kutupsal", figure(
    W, H, [pl, pr, q],
    "<em>x</em> = <em>r</em> cos &#952;, <em>y</em> = <em>r</em> sin &#952; dönüşümü <em>r</em>&#952;-düzlemindeki "
    "[<em>a</em>, <em>b</em>] &#215; [&#945;, &#946;] dikdörtgenini <em>xy</em>-düzlemindeki kutupsal "
    "dikdörtgene götürür: <em>r</em> = sabit doğruları çember yaylarına, &#952; = sabit doğruları "
    "orijinden çıkan ışınlara gider.",
    WIDE,
    aria="Left: the rectangle a to b in r times alpha to beta in theta in the r theta plane. Right: the "
         "polar rectangle between the arcs r = a and r = b and the rays theta = alpha and theta = beta"))

# ============================================================
# yamuk: Example 3, the trapezoid R and the trapezoid S under u = x + y, v = x - y
# ============================================================
COL = {"uv": BASE, "v2": THEORY, "umv": REMARK, "v1": PRACTICE}
pl = eq_plot(40, 40, 64, (-2.6, 2.75), (-0.35, 2.55))
pr = eq_plot(470, 30, 78, (-0.55, 2.6), (-2.5, 0.55))
frame_axes(pl, "u", "v")
frame_axes(pr, "x", "y")
Sv = [(1, 1), (2, 2), (-2, 2), (-1, 1)]
pl.polygon(Sv, BASE, 0.13)
pl.line([(1, 1), (2, 2)], COL["uv"], 2.6)
pl.line([(2, 2), (-2, 2)], COL["v2"], 2.6)
pl.line([(-2, 2), (-1, 1)], COL["umv"], 2.6)
pl.line([(-1, 1), (1, 1)], COL["v1"], 2.6)
for P, s, dx, dy, anc in (((1, 1), "(1, 1)", 7, 15, "start"), ((2, 2), "(2, 2)", 4, -8, "start"),
                          ((-2, 2), "(" + MINUS + "2, 2)", -4, -8, "end"),
                          ((-1, 1), "(" + MINUS + "1, 1)", -7, 15, "end")):
    dot(pl, P, TEXT, 3.2)
    pl.label(*P, s, dx, dy, TEXT, 11.5, anc)
pl.label(1.5, 1.5, it("u") + " = " + it("v"), 9, 5, COL["uv"], 12, "start", True)
pl.label(0, 2, it("v") + " = 2", 0, -8, COL["v2"], 12, "middle", True)
pl.label(-1.5, 1.5, it("u") + " = " + MINUS + it("v"), -9, 5, COL["umv"], 12, "end", True)
pl.label(0, 1, it("v") + " = 1", 0, 17, COL["v1"], 12, "middle", True)
pl.label(0, 1.5, it("S"), 0, 5, BASE, 15, "middle", True)
Rv = [(1, 0), (2, 0), (0, -2), (0, -1)]
pr.polygon(Rv, THEORY, 0.13)
pr.line([(1, 0), (2, 0)], COL["uv"], 2.6)
pr.line([(2, 0), (0, -2)], COL["v2"], 2.6)
pr.line([(0, -2), (0, -1)], COL["umv"], 2.6)
pr.line([(0, -1), (1, 0)], COL["v1"], 2.6)
for P, s, dx, dy, anc in (((1, 0), "(1, 0)", -4, -8, "end"), ((2, 0), "(2, 0)", 4, -8, "start"),
                          ((0, -2), "(0, " + MINUS + "2)", -7, 5, "end"),
                          ((0, -1), "(0, " + MINUS + "1)", -7, 5, "end")):
    dot(pr, P, TEXT, 3.2)
    pr.label(*P, s, dx, dy, TEXT, 11.5, anc)
pr.label(1.5, 0, it("y") + " = 0", 0, 17, COL["uv"], 12, "middle", True)
pr.label(1.0, -1.0, it("x") + " " + MINUS + " " + it("y") + " = 2", 9, 8, COL["v2"], 12, "start", True)
pr.label(0, -1.5, it("x") + " = 0", -7, 5, COL["umv"], 12, "end", True)
pr.label(0.5, -0.5, it("x") + " " + MINUS + " " + it("y") + " = 1", -7, -6, COL["v1"], 12, "end", True)
pr.label(0.75, -0.75, it("R"), 0, 5, THEORY, 15, "middle", True)
W, H = 740, 260
q = connector(W, H, pl.x0 + pl.w + 12, pr.x0 - 8, pl.Y(1.3), ((it("T"), 1), (T_INV, -1)))
save("yamuk", figure(
    W, H, [pl, pr, q],
    "<em>u</em> = <em>x</em> + <em>y</em>, <em>v</em> = <em>x</em> &#8722; <em>y</em> ile <em>R</em> yamuğunun "
    "her kenarı <em>S</em> yamuğunun aynı renkteki kenarına gider. <em>T</em> ise <em>x</em> = "
    "(<em>u</em> + <em>v</em>)/2, <em>y</em> = (<em>u</em> &#8722; <em>v</em>)/2 ile <em>S</em>'yi <em>R</em>'ye "
    "geri götürür.",
    WIDE,
    aria="Left: the trapezoid S in the uv-plane with vertices (1, 1), (2, 2), (-2, 2), (-1, 1) and sides "
         "u = v, v = 2, u = -v, v = 1. Right: the trapezoid R in the xy-plane with vertices (1, 0), (2, 0), "
         "(0, -2), (0, -1) and sides y = 0, x - y = 2, x = 0, x - y = 1 in matching colors"))

# ============================================================
# hiperbol: u = x^2 - y^2, v = xy turns a curved region into a rectangle
# ============================================================


def inv_h(uu, vv):
    """The first-quadrant point with x^2 - y^2 = uu, xy = vv."""
    s = math.sqrt(uu * uu + 4 * vv * vv)
    return (math.sqrt((s + uu) / 2), math.sqrt((s - uu) / 2))


pl = Plot(70, 60, 260, 150, (-0.6, 10.0), (-0.4, 4.8))
pl.origin_axes(it("u"), it("v"), (1, 9), (2, 4), opacity=0.5)
pl.polygon([(1, 2), (9, 2), (9, 4), (1, 4)], BASE, 0.15, BASE, 2.0)
pl.label(5, 3, it("S"), 0, 5, BASE, 15, "middle", True)
pr = eq_plot(440, 30, 92, (-0.2, 3.65), (-0.2, 2.45))
frame_axes(pr, "x", "y")
# full curves, clipped to the panel by their parameter ranges
pr.line(seg(lambda t: (math.sqrt(1 + t * t), t), 0, 2.4), PRACTICE, 1.2, "5 3", 0.7)
pr.line(seg(lambda t: (math.sqrt(9 + t * t), t), 0, math.sqrt(3.65**2 - 9)), PRACTICE, 1.2, "5 3", 0.7)
XE = 3.4
pr.line(seg(lambda t: (t, 2 / t), 2 / 2.45, XE), REMARK, 1.2, "5 3", 0.8)
pr.line(seg(lambda t: (t, 4 / t), 4 / 2.45, XE), REMARK, 1.2, "5 3", 0.8)
bd = (seg(lambda t: inv_h(t, 2), 1, 9) + seg(lambda t: inv_h(9, t), 2, 4)
      + seg(lambda t: inv_h(t, 4), 9, 1) + seg(lambda t: inv_h(1, t), 4, 2))
pr.polygon(bd, THEORY, 0.18, THEORY, 2.0)
pr.label(math.sqrt(1 + 2.3**2), 2.3, it("x") + "² " + MINUS + " " + it("y") + "² = 1", -6, 4, PRACTICE, 11.5, "end")
pr.label(3.6, math.sqrt(3.6**2 - 9), it("x") + "² " + MINUS + " " + it("y") + "² = 9", -4, -9, PRACTICE, 11.5, "end")
pr.label(XE, 2 / XE, it("xy") + " = 2", 6, 4, REMARK, 11.5, "start")
pr.label(XE, 4 / XE, it("xy") + " = 4", 6, 4, REMARK, 11.5, "start")
pr.label(2.45, 1.25, it("R"), 0, 5, THEORY, 15, "middle", True)
W, H = 860, 270
q = connector(W, H, pl.x0 + pl.w + 22, pr.x0 - 10, pl.Y(3.0), ((it("T"), 1), (T_INV, -1)))
save("hiperbol", figure(
    W, H, [pl, pr, q],
    "<em>u</em> = <em>x</em>² &#8722; <em>y</em>², <em>v</em> = <em>xy</em> değişkenleri birinci bölgedeki "
    "dört hiperbolün sınırladığı <em>R</em> bölgesini [1, 9] &#215; [2, 4] dikdörtgenine çevirir.",
    WIDE,
    aria="Left: the rectangle S = [1, 9] x [2, 4] in the uv-plane. Right: the curved region R in the first "
         "quadrant between the hyperbolas x^2 - y^2 = 1, x^2 - y^2 = 9, xy = 2 and xy = 4"))

# ============================================================
# kuresel-kutu: a box in (rho, theta, phi) space and the spherical wedge it maps to
# ============================================================
R1, R2, TH1, TH2, PH1, PH2 = 1.3, 2.0, 0.85, 1.45, 0.55, 1.05


def sph(r, t, f):
    return (r * math.sin(f) * math.cos(t), r * math.sin(f) * math.sin(t), r * math.cos(f))


cam = Camera(azimuth=35.0, elevation=22.0)


def fit(pts, x0, y0, ppu, pad=0.15):
    qq = [cam.project(P)[:2] for P in pts]
    xr = (min(a for a, _ in qq) - pad, max(a for a, _ in qq) + pad)
    yr = (min(b for _, b in qq) - pad, max(b for _, b in qq) + pad)
    p = eq_plot(x0, y0, ppu, xr, yr)
    return p, Space(p, cam)


corners = {(i, j, k): ((R1, R2)[i], (TH1, TH2)[j], (PH1, PH2)[k]) for i in (0, 1) for j in (0, 1) for k in (0, 1)}
# the 12 edges: pairs of corner indices that differ in one place
edges = [(a, b) for a in corners for b in corners if a < b and sum(x != y for x, y in zip(a, b)) == 1]
# a face is (axis, side); an edge lies on the two faces fixed by its constant indices


def edge_faces(a, b):
    return [(ax, a[ax]) for ax in range(3) if a[ax] == b[ax]]


def box_normal(face):
    ax, side = face
    n = [0.0, 0.0, 0.0]
    n[ax] = 1.0 if side else -1.0
    return tuple(n)


def wedge_normal(face):
    """Outward normal of a face of the spherical wedge, at the face center."""
    ax, side = face
    r, t, f = (R1 + R2) / 2, (TH1 + TH2) / 2, (PH1 + PH2) / 2
    sign = 1.0 if side else -1.0
    if ax == 0:
        v = (math.sin(f) * math.cos(t), math.sin(f) * math.sin(t), math.cos(f))
    elif ax == 1:
        t = (TH1, TH2)[side]
        v = (-math.sin(t), math.cos(t), 0.0)
    else:
        f = (PH1, PH2)[side]
        v = (math.cos(f) * math.cos(t), math.cos(f) * math.sin(t), -math.sin(f))
    return tuple(sign * c for c in v)


def visible(face, normal):
    return vdot(normal(face), cam.d) > 0


# left: the coordinate box, with rho, theta, phi drawn along the three axes
LX, LY, LZ = 2.5, 1.9, 1.45
pl, SL = fit([(0, 0, 0), (LX, 0, 0), (0, LY, 0), (0, 0, LZ)] + list(corners.values()), 30, 40, 100, 0.25)
SL.axes(LX, LY, LZ, labels=("&#961;", "&#952;", "&#966;"))
for ax in range(3):
    for side in (0, 1):
        quad = [c for c in corners if c[ax] == side]
        quad = [quad[0], quad[1], quad[3], quad[2]]
        SL.polygon([corners[c] for c in quad], BASE, 0.11 if visible((ax, side), box_normal) else 0.05)
for a, b in edges:
    front = any(visible(fc, box_normal) for fc in edge_faces(a, b))
    SL.line([corners[a], corners[b]], BASE, 1.9 if front else 1.1, None if front else "4 3", 1.0 if front else 0.7)
SL.label(((R1 + R2) / 2, TH1, PH2), DELTA + "&#961;", -8, -6, TEXT, 12, "end")
SL.label((R2, (TH1 + TH2) / 2, PH1), DELTA + "&#952;", 0, 18, TEXT, 12, "middle")
SL.label((R1, TH2, (PH1 + PH2) / 2), DELTA + "&#966;", 9, 4, TEXT, 12, "start")
SL.label((R2, TH1, (PH1 + PH2) / 2), it("S"), -10, 5, BASE, 15, "end", True)

# right: the spherical wedge
pts = [(0, 0, 0), (2.3, 0, 0), (0, 2.3, 0), (0, 0, 2.3)] + [sph(*corners[c]) for c in corners]
pr, SR = fit(pts, 420, 30, 105, 0.25)
SR.axes(2.3, 2.3, 2.3)
for c in ((0, 0, 0), (0, 1, 0), (0, 0, 1), (0, 1, 1)):
    SR.guide([(0, 0, 0), sph(*corners[c])], TEXT, 0.35)
FACE_SURF = {
    (0, 0): (lambda t, f: sph(R1, t, f), (TH1, TH2), (PH1, PH2)),
    (0, 1): (lambda t, f: sph(R2, t, f), (TH1, TH2), (PH1, PH2)),
    (1, 0): (lambda r, f: sph(r, TH1, f), (R1, R2), (PH1, PH2)),
    (1, 1): (lambda r, f: sph(r, TH2, f), (R1, R2), (PH1, PH2)),
    (2, 0): (lambda r, t: sph(r, t, PH1), (R1, R2), (TH1, TH2)),
    (2, 1): (lambda r, t: sph(r, t, PH2), (R1, R2), (TH1, TH2)),
}
# hidden faces first, then the visible ones
for want in (False, True):
    for face, (fn, ur, vr) in FACE_SURF.items():
        if visible(face, wedge_normal) == want:
            op = (0.06, 0.20) if want else (0.03, 0.08)
            SR.surface(fn, ur, vr, 3, 3, THEORY, THEORY, op, 0.4, 0.18 if want else 0.08)
for a, b in edges:
    A, B = corners[a], corners[b]
    front = any(visible(fc, wedge_normal) for fc in edge_faces(a, b))
    SR.curve(lambda s, A=A, B=B: sph(*[A[i] + s * (B[i] - A[i]) for i in range(3)]), 0, 1, THEORY,
             1.9 if front else 1.1, 40, None if front else "4 3", 1.0 if front else 0.7)
SR.label(sph((R1 + R2) / 2, TH1, PH2), DELTA + "&#961;", -8, 14, TEXT, 12, "end")
SR.label(sph(R2, (TH1 + TH2) / 2, PH2), it("&#961;") + " sin &#966; " + DELTA + "&#952;", 6, 20, TEXT, 12, "start")
SR.label(sph(R2, TH2, (PH1 + PH2) / 2), it("&#961;") + " " + DELTA + "&#966;", 9, 4, TEXT, 12, "start")
SR.label(sph(R2, (TH1 + TH2) / 2, (PH1 + PH2) / 2), it("R"), 0, 5, THEORY, 15, "middle", True)
W = int(pr.x0 + pr.w + 60)
H = int(max(pl.y0 + pl.h, pr.y0 + pr.h) + 30)
q = connector(W, H, pl.x0 + pl.w + 8, pr.x0 + 10, (pl.y0 + pl.h / 2))
save("kuresel-kutu", figure(
    W, H, [pl, pr, q],
    "Küresel koordinat dönüşümü (&#961;, &#952;, &#966;)-uzayındaki küçük <em>S</em> kutusunu bir küresel kama "
    "<em>R</em>'ye götürür. Kamanın kenarları yaklaşık &#916;&#961;, &#961; sin &#966; &#916;&#952; ve "
    "&#961; &#916;&#966; olduğundan hacmi yaklaşık &#961;² sin &#966; &#916;&#961; &#916;&#952; &#916;&#966;'dir; "
    "bu çarpan Jacobi determinantının mutlak değeridir.",
    WIDE,
    aria="Left: a box in rho theta phi space with edges d rho, d theta, d phi. Right: the spherical wedge "
         "it maps to in xyz-space, bounded by two spheres, two half planes and two cones, with edge lengths "
         "d rho, rho sin phi d theta and rho d phi"))
