# -*- coding: utf-8 -*-
"""
Figures of the chapter "Green Teoremi"
(dersler/integral-calculus/green-teoremi.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box and never directly under a heading.
Concept figures stay visible: `pozitif-yon` sits directly below the definition
box of the positive orientation, `birlesim` and `delikli` in the statements of
their theorem and corollary (before the proofs); `ucgen`, `yarim-halka` and
`parabol-yon` sit under the question text of their example or exercise.
`basit-bolge` belongs to the proof of Green's theorem and `orijin` to the
solution of the example with the field (-y i + x j)/(x^2 + y^2).
The figures are NOT produced at build time. Run

    python scripts/calculus_figures/grn.py
    python scripts/center_figures.py "calculus-grn-*.md"
    python scripts/check_figure_labels.py "scripts/_figures/calculus-grn-*.md"

and paste the markup of scripts/_figures/calculus-grn-<name>.md into the .qmd.
Captions are Turkish on purpose; aria labels are plain ASCII.
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, dot, panel_title, TEXT, THEORY, PRACTICE, BASE, BG, WIDE  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "calculus-grn-"

MINUS = "&#8722;"
PRIME = "&#8242;"
DPRIME = "&#8243;"
PI = math.pi


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


def head(p, P, d, color, size=10.0):
    """Filled arrowhead centred at data point P, pointing along data direction d."""
    sx = p.w / (p.xmax - p.xmin)
    sy = p.h / (p.ymax - p.ymin)
    dx, dy = d[0] * sx, -d[1] * sy
    n = math.hypot(dx, dy) or 1.0
    ux, uy = dx / n, dy / n
    X, Y = p.X(P[0]), p.Y(P[1])
    tx, ty = X + ux * size * 0.55, Y + uy * size * 0.55
    bx, by = X - ux * size * 0.45, Y - uy * size * 0.45
    hw = size * 0.42
    p.add(f'<polygon points="{tx:.1f},{ty:.1f} {bx - uy * hw:.1f},{by + ux * hw:.1f} '
          f'{bx + uy * hw:.1f},{by - ux * hw:.1f}" fill="{color}"/>')


def path_heads(p, pts, fracs, color, size=10.0):
    """Arrowheads at the given fractions of the arc length of a polyline."""
    seg = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    total = sum(seg)
    for f in fracs:
        target, acc = f * total, 0.0
        for i, s in enumerate(seg):
            if acc + s >= target:
                lam = (target - acc) / s if s else 0.0
                P = (pts[i][0] + lam * (pts[i + 1][0] - pts[i][0]), pts[i][1] + lam * (pts[i + 1][1] - pts[i][1]))
                head(p, P, (pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]), color, size)
                break
            acc += s


def path_d(p, pts, close=True):
    d = "M" + " L".join(p.P(x, y) for x, y in pts)
    return d + (" Z" if close else "")


def ring_fill(p, outer, inner, color=THEORY, opacity=0.14):
    """Shade the region between two closed polylines (even-odd rule)."""
    p.add(f'<path d="{path_d(p, outer)} {path_d(p, inner)}" fill="{color}" fill-opacity="{opacity}" '
          f'fill-rule="evenodd" stroke="none"/>')


def polar_blob(cx, cy, rfun, n=240):
    """Closed counter-clockwise curve r = rfun(theta) around (cx, cy)."""
    return [(cx + rfun(2 * PI * k / n) * math.cos(2 * PI * k / n),
             cy + rfun(2 * PI * k / n) * math.sin(2 * PI * k / n)) for k in range(n + 1)]


def ellipse_arc(cx, cy, rx, ry, a0, a1, n=40):
    return [(cx + rx * math.cos(a0 + (a1 - a0) * k / n), cy + ry * math.sin(a0 + (a1 - a0) * k / n))
            for k in range(n + 1)]


def tick_x(p, x, s, color=TEXT, size=11.5):
    p.add(f'<line x1="{p.X(x):.1f}" y1="{p.Y(0) - 3:.1f}" x2="{p.X(x):.1f}" y2="{p.Y(0) + 3:.1f}" '
          f'stroke="{TEXT}" stroke-width="1" opacity="0.7"/>')
    p.label(x, 0, s, 0, 16, color, size, "middle")


def tick_y(p, y, s, color=TEXT, size=11.5):
    p.add(f'<line x1="{p.X(0) - 3:.1f}" y1="{p.Y(y):.1f}" x2="{p.X(0) + 3:.1f}" y2="{p.Y(y):.1f}" '
          f'stroke="{TEXT}" stroke-width="1" opacity="0.7"/>')
    p.label(0, y, s, -8, 4, color, size, "end")


C1, C2, C3, C4 = (it("C") + sub(k) for k in "1234")


# ============================================================
# pozitif-yon: positive and negative orientation of a simple closed curve
# ============================================================
def r_a(t):
    return 1.55 + 0.38 * math.cos(2 * t - 0.9) + 0.22 * math.cos(3 * t + 1.6)


def r_b(t):
    return 1.5 + 0.3 * math.cos(2 * t + 0.7) + 0.26 * math.sin(3 * t - 0.4)


panels = []
left = 30
for k, (rf, positive, title) in enumerate(((r_a, True, "(a) Pozitif yön"), (r_b, False, "(b) Negatif yön"))):
    p = eq_plot(left, 40, 46, (-0.5, 5.4), (-0.5, 4.6))
    left += p.w + 50
    p.origin_axes(it("x"), it("y"))
    p.label(0, 0, "0", -7, 14, TEXT, 11, "end")
    pts = polar_blob(2.7, 2.15, rf)
    p.polygon(pts, THEORY, 0.13)
    p.line(pts, THEORY, 2.0)
    run = pts if positive else pts[::-1]
    path_heads(p, run, (0.06, 0.31, 0.56, 0.81), THEORY, 11)
    p.label(2.7, 2.15, it("D"), 0, 5, TEXT, 14, "middle", True)
    # label C outside the curve, on the upper right
    ang = 0.75
    rr = rf(ang)
    p.label(2.7 + rr * math.cos(ang), 2.15 + rr * math.sin(ang), it("C"), 8, -6, THEORY, 14, "start", True)
    panel_title(p, title)
    panels.append(p)
save("pozitif-yon", figure(
    int(left - 20), 300, panels,
    "(a) Pozitif yönlü <em>C</em> eğrisi saat yönünün tersine bir kez dolaşılır; eğri boyunca ilerleyen "
    "biri <em>D</em> bölgesini hep solunda görür. (b) Ters yönde dolaşılan eğri negatif yönlüdür: "
    "<em>D</em> bu kez hep sağda kalır.",
    css_class=WIDE,
    aria="Two plane regions D bounded by closed curves C. Left: arrows run counterclockwise, region on the "
         "left. Right: arrows run clockwise, region on the right"))

# ============================================================
# basit-bolge: the simple region seen as type I (left) and type II (right)
# ============================================================
OX, OY = 1.0, 0.8          # shift of the region
W, H = 5.0, 3.6
LL = (OX + 1.8, OY + 1.4, 1.8, 1.4)      # corner arcs: centre and radii
LR = (OX + 3.8, OY + 0.9, 1.2, 0.9)
UR = (OX + 3.5, OY + 2.4, 1.5, 1.2)
UL = (OX + 1.4, OY + 2.6, 1.4, 1.0)


def arc(c, a0, a1):
    return ellipse_arc(c[0], c[1], c[2], c[3], a0, a1)


arc_ll = arc(LL, PI, 1.5 * PI)            # (OX, ..) -> bottom
arc_lr = arc(LR, 1.5 * PI, 2 * PI)        # bottom -> right side
arc_ur = arc(UR, 0, 0.5 * PI)             # right side -> top
arc_ul = arc(UL, 0.5 * PI, PI)            # top -> left side
bottom = [arc_ll[-1], arc_lr[0]]
right = [arc_lr[-1], arc_ur[0]]
top = [arc_ur[-1], arc_ul[0]]
leftseg = [arc_ul[-1], arc_ll[0]]
outline = arc_ll + arc_lr + arc_ur + arc_ul
A_, B_ = OX, OX + W
C_, D_ = OY, OY + H

SB = 10.0                                  # sub size: the figure is shown at a reduced scale
BC1, BC2, BC3, BC4 = (it("C") + sub(k, SB) for k in "1234")
panels = []
left = 30
for k in range(2):
    p = eq_plot(left, 40, 42, (-0.5, 6.9), (-0.5, 5.4))
    left += p.w + 46
    p.origin_axes(it("x"), it("y"))
    p.label(0, 0, "0", -7, 14, TEXT, 12, "end")
    p.polygon(outline, THEORY, 0.12)
    p.label(OX + 2.5, OY + 1.8, it("D"), 0, 5, TEXT, 14.5, "middle", True)
    if k == 0:
        lower = arc_ll + arc_lr[1:]
        upper = arc_ur + arc_ul[1:]
        p.line(lower, THEORY, 2.2)
        p.line(upper, BASE, 2.2)
        p.line(right, PRACTICE, 2.2)
        p.line(leftseg, PRACTICE, 2.2)
        path_heads(p, lower, (0.5,), THEORY, 11)
        path_heads(p, upper, (0.5,), BASE, 11)
        path_heads(p, right, (0.55,), PRACTICE, 11)
        path_heads(p, leftseg, (0.55,), PRACTICE, 11)
        for xv in (A_, B_):
            p.vline(xv, 0, OY + 1.4 if xv == A_ else OY + 0.9)
        tick_x(p, A_, it("a"), size=12.5)
        tick_x(p, B_, it("b"), size=12.5)
        p.label(OX + 2.8, OY, BC1, 0, 19, THEORY, 13.5, "middle", True)
        p.label(B_, OY + 1.65, BC2, 8, 5, PRACTICE, 13.5, "start", True)
        p.label(OX + 2.45, OY + H, BC3, 0, -12, BASE, 13.5, "middle", True)
        p.label(A_, OY + 1.95, BC4, -8, 5, PRACTICE, 13.5, "end", True)
        p.label(OX + 3.6, OY - 0.05, it("y") + " = " + it("g") + sub("1", SB) + "(" + it("x") + ")",
                0, 19, THEORY, 12.5, "start")
        p.label(OX + 4.9, OY + 3.25, it("y") + " = " + it("g") + sub("2", SB) + "(" + it("x") + ")",
                6, -8, BASE, 12.5, "start")
        panel_title(p, "I. tip: " + it("P") + " " + it("dx") + " integrali", size=12.5)
    else:
        rightc = arc_lr + right[1:] + arc_ur[1:]
        leftc = arc_ul + leftseg[1:] + arc_ll[1:]
        p.line(rightc, THEORY, 2.2)
        p.line(leftc, BASE, 2.2)
        p.line(top, PRACTICE, 2.2)
        p.line(bottom, PRACTICE, 2.2)
        path_heads(p, rightc, (0.5,), THEORY, 11)
        path_heads(p, leftc, (0.5,), BASE, 11)
        path_heads(p, top, (0.5,), PRACTICE, 11)
        path_heads(p, bottom, (0.5,), PRACTICE, 11)
        p.add(f'<line x1="{p.X(0):.1f}" y1="{p.Y(C_):.1f}" x2="{p.X(OX + 1.8):.1f}" y2="{p.Y(C_):.1f}" '
              f'stroke="{TEXT}" stroke-width="1" stroke-dasharray="4 3" opacity="0.5"/>')
        p.add(f'<line x1="{p.X(0):.1f}" y1="{p.Y(D_):.1f}" x2="{p.X(OX + 1.4):.1f}" y2="{p.Y(D_):.1f}" '
              f'stroke="{TEXT}" stroke-width="1" stroke-dasharray="4 3" opacity="0.5"/>')
        tick_y(p, C_, it("c"), size=12.5)
        tick_y(p, D_, it("d"), size=12.5)
        G = "&#915;"
        p.label(B_, OY + 1.65, G + sub("1", SB), 8, 5, THEORY, 13.5, "start", True)
        p.label(OX + 2.45, OY + H, G + sub("2", SB), 0, -12, PRACTICE, 13.5, "middle", True)
        p.label(A_, OY + 1.95, G + sub("3", SB), -8, 5, BASE, 13.5, "end", True)
        p.label(OX + 2.8, OY, G + sub("4", SB), 0, 19, PRACTICE, 13.5, "middle", True)
        p.label(OX + 4.6, OY + 3.45, it("x") + " = " + it("h") + sub("2", SB) + "(" + it("y") + ")",
                12, -6, THEORY, 12.5, "start")
        p.label(OX + 0.3, OY + 2.85, it("x") + " = " + it("h") + sub("1", SB) + "(" + it("y") + ")",
                0, 4, BASE, 12.5, "start")
        panel_title(p, "II. tip: " + it("Q") + " " + it("dy") + " integrali", size=12.5)
    panels.append(p)
save("basit-bolge", figure(
    int(left - 16), 365, panels,
    "Aynı basit bölge iki biçimde. Solda I. tip betim: alt eğri <em>C</em><sub>1</sub> (<em>y</em> = "
    "<em>g</em><sub>1</sub>(<em>x</em>)), üst eğri <em>C</em><sub>3</sub> (<em>y</em> = <em>g</em><sub>2</sub>(<em>x</em>)) "
    "ve üzerlerinde <em>dx</em> = 0 olan düşey parçalar <em>C</em><sub>2</sub>, <em>C</em><sub>4</sub>. "
    "Sağda II. tip betim: sağ eğri &#915;<sub>1</sub> (<em>x</em> = <em>h</em><sub>2</sub>(<em>y</em>)), "
    "sol eğri &#915;<sub>3</sub> (<em>x</em> = <em>h</em><sub>1</sub>(<em>y</em>)) ve üzerlerinde "
    "<em>dy</em> = 0 olan yatay parçalar &#915;<sub>2</sub>, &#915;<sub>4</sub>.",
    css_class=WIDE,
    aria="The same convex region D twice. Left: boundary split into lower curve C1, right vertical segment C2, "
         "upper curve C3, left vertical segment C4 between x = a and x = b. Right: boundary split into right "
         "curve Gamma1, top segment Gamma2, left curve Gamma3, bottom segment Gamma4 between y = c and y = d"))

# ============================================================
# ucgen: Example 1, the triangle (0,0) -> (1,0) -> (0,1) -> (0,0)
# ============================================================
p = eq_plot(40, 30, 230, (-0.3, 1.35), (-0.25, 1.3))
p.origin_axes(it("x"), it("y"))
tri = [(0, 0), (1, 0), (0, 1)]
p.polygon(tri, THEORY, 0.14)
p.line(tri + [(0, 0)], THEORY, 2.2)
path_heads(p, [(0, 0), (1, 0)], (0.5,), THEORY, 11)
path_heads(p, [(1, 0), (0, 1)], (0.5,), THEORY, 11)
path_heads(p, [(0, 1), (0, 0)], (0.5,), THEORY, 11)
dot(p, (0, 0), TEXT, 3.6)
dot(p, (1, 0), TEXT, 3.6)
dot(p, (0, 1), TEXT, 3.6)
p.label(0, 0, "(0, 0)", -8, 18, TEXT, 11.5, "end")
p.label(1, 0, "(1, 0)", 0, 20, TEXT, 11.5, "middle")
p.label(0, 1, "(0, 1)", -9, 4, TEXT, 11.5, "end")
p.label(0.3, 0.3, it("D"), 0, 5, TEXT, 14, "middle", True)
p.label(0.6, 0.4, it("C"), 10, -8, THEORY, 14, "start", True)
p.label(0.72, 0.62, it("y") + " = 1 " + MINUS + " " + it("x"), 0, 0, THEORY, 12.5, "start")
save("ucgen", figure(
    int(p.x0 + p.w + 30), int(p.y0 + p.h + 30), [p],
    "Üçgen <em>C</em> eğrisi (0, 0) &#8594; (1, 0) &#8594; (0, 1) &#8594; (0, 0) sırasıyla, yani saat "
    "yönünün tersine dolaşılır; sınırladığı <em>D</em> bölgesi 0 &#8804; <em>x</em> &#8804; 1, "
    "0 &#8804; <em>y</em> &#8804; 1 &#8722; <em>x</em> ile verilir.",
    aria="Triangle with vertices (0,0), (1,0), (0,1), shaded region D, arrows counterclockwise along the "
         "sides, hypotenuse y = 1 - x"))

# ============================================================
# birlesim: D = D1 u D2 with the common cut C3
# ============================================================


def r_k(t):
    """A kidney-shaped curve with a dent on top (at theta = pi/2)."""
    return 2.0 - 0.95 * math.exp(-((t - PI / 2) / 0.42) ** 2) + 0.18 * math.cos(2 * t)


p = eq_plot(40, 30, 62, (-2.9, 2.9), (-2.4, 1.9))
kid = polar_blob(0, 0, r_k, 360)
top_y = r_k(PI / 2)
bot_y = -r_k(1.5 * PI)
p.polygon(kid, THEORY, 0.13)
p.line(kid, PRACTICE, 2.2)
# the cut along x = 0
p.line([(0, bot_y), (0, top_y)], BASE, 2.2)
# boundary of D1 (left half): outer arc from the top over the left down to the bottom
n = len(kid) - 1
left_arc = kid[n // 4: 3 * n // 4 + 1]            # theta from pi/2 to 3pi/2
right_arc = kid[3 * n // 4:] + kid[1: n // 4 + 1]  # theta from 3pi/2 to 5pi/2
path_heads(p, left_arc, (0.32, 0.7), PRACTICE, 11)
path_heads(p, right_arc, (0.3, 0.68), PRACTICE, 11)
# C3 upward (left side of the cut) and -C3 downward (right side)
p.arrow((-0.18, -0.55), (-0.18, 0.15), BASE, 1.6, 8)
p.arrow((0.18, 0.15), (0.18, -0.55), BASE, 1.6, 8)
p.label(-0.18, -0.25, C3, -7, 4, BASE, 13, "end", True)
p.label(0.18, -0.25, MINUS + C3, 7, 4, BASE, 13, "start", True)
p.label(-1.15, 0.45, it("D") + sub("1"), 0, 5, TEXT, 14, "middle", True)
p.label(1.15, 0.45, it("D") + sub("2"), 0, 5, TEXT, 14, "middle", True)
ang = 2.55
p.label(r_k(ang) * math.cos(ang), r_k(ang) * math.sin(ang), C1, -8, -4, PRACTICE, 13.5, "end", True)
ang = 0.55
p.label(r_k(ang) * math.cos(ang), r_k(ang) * math.sin(ang), C2, 8, -4, PRACTICE, 13.5, "start", True)
save("birlesim", figure(
    int(p.x0 + p.w + 30), int(p.y0 + p.h + 30), [p],
    "<em>D</em> = <em>D</em><sub>1</sub> &#8746; <em>D</em><sub>2</sub>: ortak kenar <em>C</em><sub>3</sub>, "
    "<em>D</em><sub>1</sub>'in sınırında yukarı, <em>D</em><sub>2</sub>'nin sınırında aşağı doğru "
    "(&#8722;<em>C</em><sub>3</sub>) dolaşılır. Bu iki katkı birbirini götürür ve geriye <em>D</em>'nin "
    "dış sınırı <em>C</em><sub>1</sub> &#8746; <em>C</em><sub>2</sub> kalır.",
    aria="A kidney shaped region split by a vertical segment into a left part D1 and a right part D2; the "
         "segment carries an upward arrow C3 on the left and a downward arrow -C3 on the right, the outer "
         "boundary C1 and C2 runs counterclockwise"))

# ============================================================
# yarim-halka: Example 4, the upper half of the ring 1 <= r <= 2
# ============================================================
p = eq_plot(40, 40, 78, (-2.7, 2.9), (-0.55, 2.55))
p.origin_axes(it("x"), it("y"))
outer = [(2 * math.cos(PI * k / 80), 2 * math.sin(PI * k / 80)) for k in range(81)]
inner = [(math.cos(PI - PI * k / 80), math.sin(PI - PI * k / 80)) for k in range(81)]   # from (-1,0) to (1,0)
region = outer + inner
p.polygon(region, THEORY, 0.14)
p.line(outer, THEORY, 2.2)
p.line(inner, THEORY, 2.2)
p.line([(-2, 0), (-1, 0)], THEORY, 2.2)
p.line([(1, 0), (2, 0)], THEORY, 2.2)
path_heads(p, outer, (0.2, 0.8), THEORY, 11)
path_heads(p, inner, (0.25, 0.75), THEORY, 11)
path_heads(p, [(-2, 0), (-1, 0)], (0.5,), THEORY, 11)
path_heads(p, [(1, 0), (2, 0)], (0.5,), THEORY, 11)
# the y-axis splits D into two simple regions
p.line([(0, 1), (0, 2)], BASE, 1.6, "5 4")
for xv, s in ((-2, MINUS + "2"), (-1, MINUS + "1"), (1, "1"), (2, "2")):
    tick_x(p, xv, s)
p.label(-1.25, 1.0, it("D"), 0, 5, TEXT, 14, "middle", True)
ang = 2.45
p.label(2 * math.cos(ang), 2 * math.sin(ang), it("C"), -9, -4, THEORY, 14, "end", True)
# leader lines to the two circles
P_out = (2 * math.cos(1.25), 2 * math.sin(1.25))
p.line([P_out, (1.2, 2.35)], TEXT, 0.9, None, 0.6)
p.label(1.2, 2.35, it("x") + sup("2") + " + " + it("y") + sup("2") + " = 4", 4, -2, TEXT, 12, "start")
lab = it("x") + sup("2") + " + " + it("y") + sup("2") + " = 1"
p.add(f'<rect x="{p.X(0) - 33:.1f}" y="{p.Y(0.5) - 11:.1f}" width="66" height="16" rx="3" fill="{BG}"/>')
p.label(0, 0.5, lab, 0, 0, TEXT, 12, "middle")
save("yarim-halka", figure(
    int(p.x0 + p.w + 40), int(p.y0 + p.h + 30), [p],
    "Üst yarı düzlemde <em>x</em>² + <em>y</em>² = 1 ile <em>x</em>² + <em>y</em>² = 4 çemberleri arasındaki "
    "<em>D</em> bölgesi ve pozitif yönlü sınırı <em>C</em>: dış yay saat yönünün tersine, iç yay saat yönünde "
    "dolaşılır. Kesikli <em>y</em> ekseni parçası <em>D</em>'yi iki basit bölgeye ayırır.",
    aria="Upper half ring between the circles of radius 1 and 2, outer arc oriented counterclockwise, inner "
         "arc clockwise, the two segments on the x axis oriented outward-to-inward accordingly; a dashed "
         "piece of the y axis splits the region in two"))

# ============================================================
# delikli: region with a hole; orientation (left) and the two cuts (right)
# ============================================================


def r_o(t):
    return 2.15 + 0.32 * math.cos(2 * t - 0.5) + 0.2 * math.cos(3 * t + 1.0)


HX, HY, HA, HB = -0.15, 0.1, 0.78, 0.48      # the hole: an ellipse


def hole(k, n=120):
    t = 2 * PI * k / n
    return (HX + HA * math.cos(t), HY + HB * math.sin(t))


outer = polar_blob(0, 0, r_o, 300)
inner_ccw = [hole(k) for k in range(121)]
inner_cw = inner_ccw[::-1]
panels = []
left = 30
for k in range(2):
    p = eq_plot(left, 40, 58, (-2.75, 2.75), (-2.65, 2.65))
    left += p.w + 46
    ring_fill(p, outer, inner_ccw, THEORY, 0.13)
    if k == 0:
        p.line(outer, THEORY, 2.2)
        p.line(inner_ccw, PRACTICE, 2.2)
        path_heads(p, outer, (0.1, 0.35, 0.6, 0.85), THEORY, 11)
        path_heads(p, inner_cw, (0.2, 0.7), PRACTICE, 10)
        ang = 2.3
        p.label(r_o(ang) * math.cos(ang), r_o(ang) * math.sin(ang), C1, -8, -6, THEORY, 13.5, "end", True)
        p.label(HX, HY, C2, 0, 5, PRACTICE, 13, "middle", True)
        p.label(0.95, -0.85, it("D"), 0, 5, TEXT, 14, "middle", True)
        panel_title(p, "(a) Pozitif yönlü sınır")
    else:
        # cut along y = HY from the hole to the outer curve, on both sides
        def outer_x(sign):
            lo, hi = 0.0, 4.0
            for _ in range(60):
                mid = (lo + hi) / 2
                ang = math.atan2(HY, sign * mid)
                if math.hypot(sign * mid, HY) < r_o(ang):
                    lo = mid
                else:
                    hi = mid
            return sign * lo
        xl, xr = outer_x(-1), outer_x(1)
        p.line(outer, THEORY, 2.2)
        p.line(inner_ccw, PRACTICE, 2.2)
        p.line([(xl, HY), (HX - HA, HY)], BASE, 2.0)
        p.line([(HX + HA, HY), (xr, HY)], BASE, 2.0)
        # paired opposite arrows along each cut
        for (xa, xb) in ((xl, HX - HA), (HX + HA, xr)):
            xm = (xa + xb) / 2
            p.arrow((xm - 0.32, HY + 0.17), (xm + 0.32, HY + 0.17), BASE, 1.4, 7)
            p.arrow((xm + 0.32, HY - 0.17), (xm - 0.32, HY - 0.17), BASE, 1.4, 7)
        upper_outer = [q for q in outer if q[1] >= HY]
        path_heads(p, outer, (0.15, 0.35, 0.62, 0.85), THEORY, 11)
        path_heads(p, inner_cw, (0.25, 0.75), PRACTICE, 10)
        p.label(0.2, 1.45, it("D") + PRIME, 0, 5, TEXT, 14, "middle", True)
        p.label(0.2, -1.35, it("D") + DPRIME, 0, 5, TEXT, 14, "middle", True)
        panel_title(p, "(b) İki kesikle ikiye bölme")
    panels.append(p)
save("delikli", figure(
    int(left - 16), int(panels[0].y0 + panels[0].h + 30), panels,
    "(a) Delikli <em>D</em> bölgesinin pozitif yönlü sınırı: dış eğri <em>C</em><sub>1</sub> saat yönünün "
    "tersine, iç eğri <em>C</em><sub>2</sub> saat yönünde dolaşılır; iki durumda da <em>D</em> solda kalır. "
    "(b) İki kesik <em>D</em>'yi <em>D</em>&#8242; ve <em>D</em>&#8243; parçalarına ayırır. Her kesik iki "
    "parçanın sınırında zıt yönlerde dolaşıldığından kesikler üzerindeki integraller birbirini götürür.",
    css_class=WIDE,
    aria="Left: a region with an elliptic hole, outer boundary C1 with counterclockwise arrows, inner "
         "boundary C2 with clockwise arrows. Right: the same region cut along a horizontal line through the "
         "hole into an upper part D' and a lower part D'', each cut carrying two opposite arrows"))

# ============================================================
# orijin: Example 5, a curve C around the origin and the small circle C'
# ============================================================


def r_c(t):
    return 2.1 + 0.45 * math.cos(2 * t - 0.4) + 0.3 * math.sin(3 * t + 0.3)


CXc, CYc = 0.45, 0.25
p = eq_plot(40, 30, 62, (-2.6, 3.4), (-2.4, 2.9))
p.origin_axes(it("x"), it("y"))
cur = polar_blob(CXc, CYc, r_c, 300)
AR = 0.55
circ = [(AR * math.cos(2 * PI * k / 120), AR * math.sin(2 * PI * k / 120)) for k in range(121)]
ring_fill(p, cur, circ, THEORY, 0.13)
p.line(cur, THEORY, 2.2)
p.line(circ, PRACTICE, 2.0)
path_heads(p, cur, (0.08, 0.33, 0.58, 0.83), THEORY, 11)
path_heads(p, circ, (0.2, 0.7), PRACTICE, 10)
ang = 0.5
p.label(CXc + r_c(ang) * math.cos(ang), CYc + r_c(ang) * math.sin(ang), it("C"), 9, -4, THEORY, 14, "start", True)
p.label(AR * math.cos(2.3), AR * math.sin(2.3), it("C") + PRIME, -6, -6, PRACTICE, 13.5, "end", True)
p.label(1.45, 0.75, it("D"), 0, 5, TEXT, 14, "middle", True)
p.line([(0, 0), (AR * math.cos(-0.7), AR * math.sin(-0.7))], TEXT, 1.0, None, 0.7)
p.label(AR * math.cos(-0.7) * 0.5, AR * math.sin(-0.7) * 0.5, it("a"), -3, 14, TEXT, 12, "end")
save("orijin", figure(
    int(p.x0 + p.w + 30), int(p.y0 + p.h + 30), [p],
    "Orijini çevreleyen <em>C</em> eğrisi ve <em>C</em>'nin içinde kalan, <em>a</em> yarıçaplı <em>C</em>&#8242; "
    "çemberi. Aradaki <em>D</em> bölgesi orijini içermez; pozitif yönlü sınırı <em>C</em> ile ters yönde "
    "dolaşılan <em>C</em>&#8242; çemberinden, yani <em>C</em> &#8746; (&#8722;<em>C</em>&#8242;) eğrisinden oluşur.",
    aria="A closed curve C around the origin with counterclockwise arrows and a small circle C' of radius a "
         "centred at the origin with counterclockwise arrows; the region D between them is shaded"))

# ============================================================
# parabol-yon: exercise, the clockwise boundary under x = y^2
# ============================================================
p = eq_plot(40, 30, 72, (-0.6, 5.0), (-0.6, 2.75))
p.origin_axes(it("x"), it("y"))
par = [(s * s, s) for s in [2 * k / 80 for k in range(81)]]
reg = par + [(4, 0), (0, 0)]
p.polygon(reg, THEORY, 0.14)
p.line(par, THEORY, 2.2)
p.line([(4, 2), (4, 0)], THEORY, 2.2)
p.line([(4, 0), (0, 0)], THEORY, 2.2)
path_heads(p, par, (0.55,), THEORY, 11)
path_heads(p, [(4, 2), (4, 0)], (0.5,), THEORY, 11)
path_heads(p, [(4, 0), (0, 0)], (0.5,), THEORY, 11)
dot(p, (4, 2), TEXT, 3.6)
dot(p, (4, 0), TEXT, 3.6)
p.label(4, 2, "(4, 2)", 0, -10, TEXT, 11.5, "middle")
p.label(4, 0, "(4, 0)", 8, 17, TEXT, 11.5, "start")
p.label(0, 0, "0", -7, 14, TEXT, 11, "end")
p.label(1.2, 1.45, it("x") + " = " + it("y") + sup("2"), 0, 0, THEORY, 12.5, "end")
p.label(4, 1.0, it("C"), 9, 5, THEORY, 14, "start", True)
p.label(2.7, 0.6, it("D"), 0, 5, TEXT, 14, "middle", True)
save("parabol-yon", figure(
    int(p.x0 + p.w + 30), int(p.y0 + p.h + 30), [p],
    "<em>C</em> eğrisi önce <em>x</em> = <em>y</em>² parabolü boyunca (0, 0)'dan (4, 2)'ye, sonra düşey "
    "doğru parçasıyla (4, 0)'a, oradan da <em>x</em> ekseni boyunca orijine döner. Bu dolaşımda <em>D</em> "
    "bölgesi sağda kalır: <em>C</em> saat yönünde, yani negatif yönlüdür.",
    aria="Region under the parabola x = y^2 between x = 0 and x = 4 above the x axis; arrows go up along the "
         "parabola to (4,2), down the segment x = 4 to (4,0) and left along the x axis back to the origin"))
