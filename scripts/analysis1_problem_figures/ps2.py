# -*- coding: utf-8 -*-
"""
Figures of the chapter "Kümeler, Bağıntılar ve Fonksiyonlar Üzerine Problemler"
(dersler/analiz-1/problemler-kumeler-bagintilar-fonksiyonlar.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box and never directly under a heading.
The figures are NOT produced at build time. Run

    python scripts/analysis1_problem_figures/ps2.py
    python scripts/center_figures.py "analysis1-ps2-*.md"
    python scripts/check_figure_labels.py "scripts/_figures/analysis1-ps2-*.md"

and paste the markup of scripts/_figures/analysis1-ps2-<name>.md into the .qmd.
The captions are Turkish on purpose; the aria labels are plain ASCII.

Conventions: an endpoint that belongs to a set is a filled dot, one that does
not is a hollow dot; a missing pair of a relation is a dashed arrow with a cross.
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, hollow, cross, BASE, BG, PRACTICE, TEXT, THEORY, WIDE  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "analysis1-ps2-"

MINUS, SQRT, INF = "&#8722;", "&#8730;", "&#8734;"


def save(name, svg):
    (OUT_DIR / f"{PREFIX}{name}.md").write_text(svg, encoding="utf-8", newline="\n")
    print(f"{PREFIX}{name}.md")


def it(s):
    """Italic math letter inside an SVG <text>."""
    return f'<tspan font-style="italic">{s}</tspan>'


def num(v):
    """A tick label with a typographic minus sign."""
    s = f"{v:g}"
    return s.replace("-", MINUS)


def arrow_px(p, x0, y0, x1, y1, color=THEORY, width=1.6, head=7.0, dash=None, opacity=1.0):
    """Straight arrow between two pixel positions with a filled head."""
    dx, dy = x1 - x0, y1 - y0
    length = math.hypot(dx, dy) or 1.0
    ux, uy = dx / length, dy / length
    sx, sy = x1 - ux * head * 0.8, y1 - uy * head * 0.8
    da = f' stroke-dasharray="{dash}"' if dash else ""
    p.add(f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{sx:.1f}" y2="{sy:.1f}" stroke="{color}" '
          f'stroke-width="{width}"{da} opacity="{opacity}" stroke-linecap="round"/>')
    head_px(p, x1, y1, ux, uy, color, head, opacity)


def head_px(p, x1, y1, ux, uy, color, head=7.0, opacity=1.0):
    px, py = -uy, ux
    hw = head * 0.42
    p.add(f'<polygon points="{x1:.1f},{y1:.1f} {x1-ux*head+px*hw:.1f},{y1-uy*head+py*hw:.1f} '
          f'{x1-ux*head-px*hw:.1f},{y1-uy*head-py*hw:.1f}" fill="{color}" opacity="{opacity}"/>')


def arrow_between_px(p, a, b, color=THEORY, width=1.6, gap=8.0, head=7.0, dash=None, opacity=1.0):
    """Arrow from pixel point a to pixel point b, both ends pulled back by `gap` pixels."""
    length = math.hypot(b[0] - a[0], b[1] - a[1]) or 1.0
    ux, uy = (b[0] - a[0]) / length, (b[1] - a[1]) / length
    arrow_px(p, a[0] + ux * gap, a[1] + uy * gap, b[0] - ux * gap, b[1] - uy * gap,
             color, width, head, dash, opacity)


def ellipse_px(p, cx, cy, rx, ry, color=TEXT, width=1.1, opacity=0.45):
    p.add(f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="none" '
          f'stroke="{color}" stroke-width="{width}" opacity="{opacity}"/>')


def number_axes(p, xticks, yticks, xlabels=None, ylabels=None, xname="x", yname="y"):
    """Axes through the origin with arrowheads, ticks and labels (pixels computed from data)."""
    ox, oy = p.X(0), p.Y(0)
    left, right = p.x0 - 4, p.x0 + p.w + 6
    top, bottom = p.y0 - 6, p.y0 + p.h + 4
    p.add(f'<g stroke="{TEXT}" stroke-width="1.1" opacity="0.5" fill="{TEXT}">'
          f'<line x1="{left:.1f}" y1="{oy:.1f}" x2="{right:.1f}" y2="{oy:.1f}"/>'
          f'<line x1="{ox:.1f}" y1="{bottom:.1f}" x2="{ox:.1f}" y2="{top:.1f}"/>'
          f'<polygon points="{right:.1f},{oy:.1f} {right-8:.1f},{oy-3.5:.1f} {right-8:.1f},{oy+3.5:.1f}" stroke="none"/>'
          f'<polygon points="{ox:.1f},{top:.1f} {ox-3.5:.1f},{top+8:.1f} {ox+3.5:.1f},{top+8:.1f}" stroke="none"/>'
          '</g>')
    for i, t in enumerate(xticks):
        lab = xlabels[i] if xlabels else num(t)
        p.add(f'<line x1="{p.X(t):.1f}" y1="{oy-3:.1f}" x2="{p.X(t):.1f}" y2="{oy+3:.1f}" stroke="{TEXT}" '
              f'stroke-width="1" opacity="0.6"/>')
        p.text_px(p.X(t), oy + 16, lab, TEXT, 11, "middle")
    for i, t in enumerate(yticks):
        lab = ylabels[i] if ylabels else num(t)
        p.add(f'<line x1="{ox-3:.1f}" y1="{p.Y(t):.1f}" x2="{ox+3:.1f}" y2="{p.Y(t):.1f}" stroke="{TEXT}" '
              f'stroke-width="1" opacity="0.6"/>')
        p.text_px(ox - 7, p.Y(t) + 4, lab, TEXT, 11, "end")
    p.text_px(right - 2, oy - 8, xname, TEXT, 12, "end", italic=True)
    p.text_px(ox + 8, top + 10, yname, TEXT, 12, "start", italic=True)


def curve(p, f, x0, x1, color=THEORY, width=2.2, samples=160, dash=None, opacity=1.0):
    pts = [(x0 + (x1 - x0) * k / samples, f(x0 + (x1 - x0) * k / samples)) for k in range(samples + 1)]
    p.line(pts, color, width, dash, opacity)


def hband(p, lo, hi, color=PRACTICE, opacity=0.10):
    p.polygon([(p.xmin, lo), (p.xmax, lo), (p.xmax, hi), (p.xmin, hi)], color, opacity)


# ============================================================
# venn-abc: A = {2,4,6,8}, B = {3,4,5,6}, C = {4,5} with the elements placed
# ============================================================
p = Plot(20, 20, 330, 220, (-3.5, 3.5), (-2.33, 2.33))       # 330/7 = 47.1 px per unit on both axes
CIRCLES = (("A", (-1.15, 0.0), 2.0, THEORY), ("B", (1.15, 0.0), 2.0, BASE), ("C", (0.95, -0.62), 0.95, PRACTICE))
for name, (cx, cy), r, col in CIRCLES:
    p.add(f'<circle cx="{p.X(cx):.1f}" cy="{p.Y(cy):.1f}" r="{p.R(r):.1f}" fill="{col}" fill-opacity="0.08" stroke="none"/>')
for name, (cx, cy), r, col in CIRCLES:
    p.circle(cx, cy, r, col, 1.6)
p.label(-2.75, 1.75, it("A"), 0, 0, THEORY, 13, "middle", True)
p.label(2.75, 1.75, it("B"), 0, 0, BASE, 13, "middle", True)
p.label(1.95, -1.55, it("C"), 0, 0, PRACTICE, 13, "middle", True)
for v, (ex, ey) in ((2, (-2.0, 0.55)), (8, (-1.75, -0.85)), (6, (0.0, 0.95)), (4, (0.3, -0.75)),
                    (5, (1.35, -0.85)), (3, (2.3, 0.65))):
    p.label(ex, ey, str(v), 0, 5, TEXT, 13, "middle", True)
save("venn-abc", figure(
    370, 260, [p],
    "<em>A</em> = {2, 4, 6, 8}, <em>B</em> = {3, 4, 5, 6} ve <em>C</em> = {4, 5} kümelerinin Venn şeması. "
    "<em>C</em> tamamen <em>B</em>'nin içindedir; <em>A</em> ile <em>B</em>'nin ortak elemanları 4 ve 6'dır, "
    "bunlardan yalnız 4, <em>C</em>'ye de aittir.",
    aria="Venn diagram of A = {2,4,6,8}, B = {3,4,5,6} and C = {4,5} with every element placed in its region"))


# ============================================================
# relation digraphs on {1, 2, 3}
# ============================================================
NODE_R = 13


def node(p, x, y, label):
    p.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{NODE_R}" fill="{BG}" stroke="{TEXT}" stroke-width="1.4"/>')
    p.text_px(x, y + 4.5, label, TEXT, 13, "middle", True)


def loop(p, x, y, color=THEORY):
    """A loop above a node: a teardrop curve from the upper left to the upper right of the circle."""
    a0, a1 = math.radians(235), math.radians(305)          # SVG angles measured with y downward
    sx, sy = x + NODE_R * math.cos(a0), y + NODE_R * math.sin(a0)
    ex, ey = x + NODE_R * math.cos(a1), y + NODE_R * math.sin(a1)
    c1 = (x - 26, y - 46)
    c2 = (x + 26, y - 46)
    p.add(f'<path d="M{sx:.1f},{sy:.1f} C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {ex+1.5:.1f},{ey-3:.1f}" '
          f'fill="none" stroke="{color}" stroke-width="1.6" stroke-linecap="round"/>')
    ux, uy = ex - c2[0], ey - c2[1]
    n = math.hypot(ux, uy)
    head_px(p, ex, ey, ux / n, uy / n, color, 7.0)


def straight(p, a, b, offset=0.0, color=THEORY, dash=None, opacity=1.0):
    """Arrow between two nodes, shifted `offset` pixels perpendicular to the segment (for a pair of opposite arrows)."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    n = math.hypot(dx, dy)
    nx, ny = -dy / n * offset, dx / n * offset
    arrow_between_px(p, (a[0] + nx, a[1] + ny), (b[0] + nx, b[1] + ny), color, 1.6, NODE_R + 3, 7.0, dash, opacity)


def arch(p, a, b, depth, color=PRACTICE, dash="5 4"):
    """A dashed arched arrow below the row of nodes from a to b, marking a pair that is NOT in the relation."""
    cx, cy = (a[0] + b[0]) / 2, a[1] + 2 * depth
    s = (a[0] + 6, a[1] + NODE_R - 1)
    e = (b[0] - 6, b[1] + NODE_R - 1)
    p.add(f'<path d="M{s[0]:.1f},{s[1]:.1f} Q{cx:.1f},{cy:.1f} {e[0]:.1f},{e[1]:.1f}" fill="none" stroke="{color}" '
          f'stroke-width="1.5" stroke-dasharray="{dash}" stroke-linecap="round"/>')
    ux, uy = e[0] - cx, e[1] - cy
    n = math.hypot(ux, uy)
    head_px(p, e[0], e[1], ux / n, uy / n, color, 7.0, 0.9)
    mx, my = 0.25 * s[0] + 0.5 * cx + 0.25 * e[0], 0.25 * s[1] + 0.5 * cy + 0.25 * e[1]
    return mx, my


def cross_px(p, x, y, color=PRACTICE, size=5.0):
    p.add(f'<path d="M{x-size:.1f},{y-size:.1f} L{x+size:.1f},{y+size:.1f} M{x-size:.1f},{y+size:.1f} '
          f'L{x+size:.1f},{y-size:.1f}" stroke="{color}" stroke-width="2" stroke-linecap="round"/>')


ROW = {1: (60.0, 80.0), 2: (180.0, 80.0), 3: (300.0, 80.0)}

# baginti-a: reflexive and symmetric, not transitive
p = Plot(0, 0, 360, 170, (0, 1), (0, 1))
for k in (1, 2, 3):
    loop(p, *ROW[k])
for a, b in ((1, 2), (2, 3)):
    straight(p, ROW[a], ROW[b], -5)
    straight(p, ROW[b], ROW[a], -5)
mx, my = arch(p, ROW[1], ROW[3], 34)
cross_px(p, mx, my)
p.text_px(mx, my + 22, "(1, 3) yok", PRACTICE, 11.5, "middle")
for k in (1, 2, 3):
    node(p, *ROW[k], str(k))
save("baginti-a", figure(
    360, 170, [p],
    "{1, 2, 3} üzerindeki bağıntı: her elemanda bir döngü (yansımalı), her okun karşı yönlüsü de var (simetrik). "
    "1'den 2'ye ve 2'den 3'e ok olduğu hâlde 1'den 3'e ok yok; geçişlilik bozulur.",
    aria="Directed graph on 1, 2, 3 with loops, arrows both ways between 1 and 2 and between 2 and 3, "
         "and a dashed missing arrow from 1 to 3"))

# baginti-e: reflexive, neither symmetric nor transitive
p = Plot(0, 0, 360, 170, (0, 1), (0, 1))
for k in (1, 2, 3):
    loop(p, *ROW[k])
for a, b in ((1, 2), (2, 3)):
    straight(p, ROW[a], ROW[b], 0)
mx, my = arch(p, ROW[1], ROW[3], 34)
cross_px(p, mx, my)
p.text_px(mx, my + 22, "(1, 3) yok", PRACTICE, 11.5, "middle")
for k in (1, 2, 3):
    node(p, *ROW[k], str(k))
save("baginti-e", figure(
    360, 170, [p],
    "{1, 2, 3} üzerindeki bağıntı: her elemanda bir döngü var (yansımalı). 1'den 2'ye ok var ama 2'den 1'e yok "
    "(simetrik değil); 1'den 2'ye ve 2'den 3'e ok olduğu hâlde 1'den 3'e ok yok (geçişli değil).",
    aria="Directed graph on 1, 2, 3 with loops, one-way arrows from 1 to 2 and from 2 to 3, "
         "and a dashed missing arrow from 1 to 3"))


# ============================================================
# mutlak-grafik: f(x) = |x - 3| - 2 on (-5, 3] has image [-2, 6)
# ============================================================
p = Plot(40, 30, 300, 250, (-6.2, 5.0), (-3.2, 7.2))
number_axes(p, (-5, 3), (-2, 6))
curve(p, lambda t: abs(t - 3) - 2, -6.0, 4.8, THEORY, 1.3, dash="5 4", opacity=0.45)
curve(p, lambda t: abs(t - 3) - 2, -5.0, 3.0, THEORY, 2.6)
p.line([(-5, 6), (0, 6)], TEXT, 1.0, "3 3", 0.5)
p.line([(3, -2), (0, -2)], TEXT, 1.0, "3 3", 0.5)
p.line([(-5, 0), (-5, 6)], TEXT, 1.0, "3 3", 0.5)
p.line([(3, 0), (3, -2)], TEXT, 1.0, "3 3", 0.5)
hollow(p, (-5, 6), THEORY, 4.2, 1.8)
p.points([(3, -2)], THEORY, 4.2)
# domain on the x axis and image on the y axis
p.line([(-5, 0), (3, 0)], BASE, 5.0, opacity=0.55)
hollow(p, (-5, 0), BASE, 4.2, 1.8)
p.points([(3, 0)], BASE, 4.2)
p.line([(0, -2), (0, 6)], PRACTICE, 5.0, opacity=0.55)
p.points([(0, -2)], PRACTICE, 4.2)
hollow(p, (0, 6), PRACTICE, 4.2, 1.8)
p.label(-2.3, 1.6, it("y") + " = 1 " + MINUS + " " + it("x"), 0, 0, THEORY, 12, "end")
p.label(-2.5, 0, "tanım kümesi (" + MINUS + "5, 3]", 0, 34, BASE, 11.5, "middle")
p.label(0, 2.0, "görüntü [" + MINUS + "2, 6)", 10, 0, PRACTICE, 11.5, "start")
save("mutlak-grafik", figure(
    380, 310, [p],
    "<em>f</em>(<em>x</em>) = |<em>x</em> &#8722; 3| &#8722; 2 fonksiyonu (&#8722;5, 3] üzerinde <em>y</em> = 1 &#8722; "
    "<em>x</em> doğru parçasıdır. Tanım kümesi <em>x</em> ekseninde, görüntüsü [&#8722;2, 6) ise <em>y</em> ekseninde "
    "gösterilmiştir: &#8722;5 tanım kümesinde olmadığı için 6 değeri de alınmaz (boş daireler).",
    aria="Graph of |x - 3| - 2 restricted to the half open interval from -5 to 3, a line segment of slope -1, "
         "with the domain on the x axis and the image from -2 to 6 on the y axis"))


# ============================================================
# delikli-dogru: (x^2 - 4)/(x - 2) = x + 2 for x != 2
# ============================================================
p = Plot(40, 30, 300, 240, (-4.5, 5.0), (-2.2, 7.6))
number_axes(p, (-2, 2), (2, 4))
curve(p, lambda t: t + 2, -4.2, 4.8, THEORY, 2.4)
p.line([(0, 4), (2, 4)], PRACTICE, 1.1, "4 3", 0.85)
p.line([(2, 0), (2, 4)], PRACTICE, 1.1, "4 3", 0.85)
hollow(p, (2, 4), PRACTICE, 4.6, 1.9)
p.label(2, 4, "(2, 4) yok", 10, 18, PRACTICE, 11.5, "start")
p.label(-3.0, 0.4, it("y") + " = " + it("x") + " + 2", 0, -14, THEORY, 12, "middle")
save("delikli-dogru", figure(
    380, 300, [p],
    "<em>f</em>(<em>x</em>) = (<em>x</em>&#178; &#8722; 4)/(<em>x</em> &#8722; 2) fonksiyonunun grafiği, "
    "<em>y</em> = <em>x</em> + 2 doğrusundan (2, 4) noktası çıkarılarak elde edilir. Bu yüzden hiçbir <em>x</em> "
    "için <em>f</em>(<em>x</em>) = 4 olmaz.",
    aria="Graph of (x squared minus 4) over (x minus 2): the line y = x + 2 with a hole at the point (2, 4)"))


# ============================================================
# ters-goruntu: f(x) = x^2 - 3, preimage of (-1, 6) is (-3, -sqrt 2) u (sqrt 2, 3)
# ============================================================
S2 = math.sqrt(2)
p = Plot(40, 30, 320, 260, (-3.9, 3.9), (-4.0, 8.0))
number_axes(p, (-3, 3), (-3, -1, 6))
for xv, dx, anchor, lab in ((-S2, 6, "start", MINUS + SQRT + "2"), (S2, -6, "end", SQRT + "2")):
    p.add(f'<line x1="{p.X(xv):.1f}" y1="{p.Y(0)-3:.1f}" x2="{p.X(xv):.1f}" y2="{p.Y(0)+3:.1f}" stroke="{TEXT}" '
          f'stroke-width="1" opacity="0.6"/>')
    p.label(xv, 0, lab, dx, -8, TEXT, 11, anchor)
hband(p, -1, 6, PRACTICE, 0.10)
p.line([(p.xmin, -1), (p.xmax, -1)], PRACTICE, 1.0, "4 3", 0.7)
p.line([(p.xmin, 6), (p.xmax, 6)], PRACTICE, 1.0, "4 3", 0.7)
curve(p, lambda t: t * t - 3, -3.35, 3.35, THEORY, 1.3, opacity=0.45)
curve(p, lambda t: t * t - 3, -3.0, -S2, THEORY, 2.6)
curve(p, lambda t: t * t - 3, S2, 3.0, THEORY, 2.6)
for xv in (-3, -S2, S2, 3):
    p.line([(xv, 0), (xv, xv * xv - 3)], BASE, 1.0, "3 3", 0.7)
    hollow(p, (xv, xv * xv - 3), THEORY, 3.8, 1.6)
p.line([(-3, 0), (-S2, 0)], BASE, 5.0, opacity=0.6)
p.line([(S2, 0), (3, 0)], BASE, 5.0, opacity=0.6)
for xv in (-3, -S2, S2, 3):
    hollow(p, (xv, 0), BASE, 4.0, 1.8)
p.label(1.6, 6.0, it("B") + " = (" + MINUS + "1, 6)", 0, -8, PRACTICE, 11.5, "middle")
p.label(1.2, -3.0, it("y") + " = " + it("x") + "&#178; " + MINUS + " 3", 8, 4, THEORY, 12, "start")
save("ters-goruntu", figure(
    400, 320, [p],
    "<em>f</em>(<em>x</em>) = <em>x</em>&#178; &#8722; 3 grafiğinin &#8722;1 &lt; <em>y</em> &lt; 6 şeridine düşen "
    "iki parçası koyu çizilmiştir. Bu parçaların <em>x</em> eksenine izdüşümü ters görüntüyü verir: "
    "(&#8722;3, &#8722;&#8730;2) ve (&#8730;2, 3) aralıkları; uç noktalar şeridin sınırına düştüğü için dahil değildir.",
    aria="Parabola y = x squared minus 3 with the horizontal band between -1 and 6 shaded and the two open intervals "
         "of x values whose images fall in the band marked on the x axis"))


# ============================================================
# parcali: f(x) = -1 for x < 0, x for x >= 0
# ============================================================
p = Plot(40, 30, 300, 220, (-3.4, 3.4), (-2.0, 3.2))
number_axes(p, (-1, 1, 2), (1, 2))
p.add(f'<line x1="{p.X(0)-3:.1f}" y1="{p.Y(-1):.1f}" x2="{p.X(0)+3:.1f}" y2="{p.Y(-1):.1f}" stroke="{TEXT}" '
      f'stroke-width="1" opacity="0.6"/>')
p.label(0, -1, MINUS + "1", 9, 4, TEXT, 11, "start")
p.line([(-3.3, -1), (0, -1)], THEORY, 2.6)
hollow(p, (0, -1), THEORY, 4.2, 1.8)
p.line([(0, 0), (3.1, 3.1)], THEORY, 2.6)
p.points([(0, 0)], THEORY, 4.2)
p.label(-1.8, -1, it("y") + " = " + MINUS + "1", 0, -10, THEORY, 12, "middle")
p.label(2.2, 2.2, it("y") + " = " + it("x"), 10, 8, THEORY, 12, "start")
save("parcali", figure(
    380, 280, [p],
    "<em>x</em> &lt; 0 için &#8722;1, <em>x</em> &#8805; 0 için <em>x</em> değerini alan fonksiyonun grafiği. "
    "Sol parça (0, &#8722;1) noktasını içermez (boş daire); 0'daki değer <em>f</em>(0) = 0'dır (dolu nokta).",
    aria="Graph of the piecewise function equal to -1 for negative x and to x for nonnegative x, "
         "with an open dot at (0, -1) and a filled dot at the origin"))


# ============================================================
# ok-semasi: f(n) = n + 1 from A = {1..5} to B = {2..7}, g from B to C = {a..e}
# ============================================================
p = Plot(0, 0, 520, 260, (0, 1), (0, 1))
COLS = {"A": 70.0, "B": 260.0, "C": 450.0}
TOP, STEP = 52.0, 30.0
A_EL = [1, 2, 3, 4, 5]
B_EL = [2, 3, 4, 5, 6, 7]
C_EL = ["a", "b", "c", "d", "e"]


def ypos(i, n):
    """Vertical position of the i-th of n elements, centered on the column."""
    mid = TOP + STEP * 2.5
    return mid + (i - (n - 1) / 2) * STEP


for name, n in (("A", 5), ("B", 6), ("C", 5)):
    ellipse_px(p, COLS[name], TOP + STEP * 2.5, 34, STEP * n / 2 + 16)
    p.text_px(COLS[name], TOP + STEP * 2.5 - STEP * n / 2 - 24, it(name), TEXT, 13, "middle", True)
F_MAP = {1: 2, 2: 3, 3: 4, 4: 5, 5: 6}
G_MAP = {2: "a", 3: "b", 4: "c", 5: "d", 6: "e", 7: "e"}
for a, b in F_MAP.items():
    arrow_between_px(p, (COLS["A"], ypos(A_EL.index(a), 5)), (COLS["B"], ypos(B_EL.index(b), 6)), THEORY, 1.5, 12)
for b, c in G_MAP.items():
    col = PRACTICE if b in (6, 7) else BASE
    arrow_between_px(p, (COLS["B"], ypos(B_EL.index(b), 6)), (COLS["C"], ypos(C_EL.index(c), 5)), col, 1.5, 12)
for i, v in enumerate(A_EL):
    p.text_px(COLS["A"], ypos(i, 5) + 4.5, str(v), TEXT, 12.5, "middle")
for i, v in enumerate(B_EL):
    p.text_px(COLS["B"], ypos(i, 6) + 4.5, str(v), PRACTICE if v == 7 else TEXT, 12.5, "middle", v == 7)
for i, v in enumerate(C_EL):
    p.text_px(COLS["C"], ypos(i, 5) + 4.5, it(v), TEXT, 12.5, "middle")
p.text_px((COLS["A"] + COLS["B"]) / 2, 30, it("f"), THEORY, 13, "middle", True)
p.text_px((COLS["B"] + COLS["C"]) / 2, 30, it("g"), BASE, 13, "middle", True)
save("ok-semasi", figure(
    520, 260, [p],
    "<em>f</em>(<em>n</em>) = <em>n</em> + 1 ile <em>A</em>'dan <em>B</em>'ye, sonra <em>g</em> ile <em>B</em>'den "
    "<em>C</em>'ye. <em>f</em>, 7'ye hiçbir ok göndermez; <em>g</em>'nin 6 ve 7'yi aynı <em>e</em>'ye götürmesi "
    "(vurgulu oklar) bu yüzden bileşkede hiç görünmez ve <em>g</em> &#8728; <em>f</em> birebir kalır.",
    css_class=WIDE,
    aria="Arrow diagram: f sends 1..5 to 2..6 in B, g sends 2..7 to a..e with both 6 and 7 going to e"))
