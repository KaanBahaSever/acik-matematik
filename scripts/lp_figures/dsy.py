# -*- coding: utf-8 -*-
"""
Figures of the chapter "Tam Sayılı Programlama ve Dal-Sınır Yöntemi"
(dersler/lineer-programlama/dal-sinir-yontemi.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution,
exercise or callout), never inside a definition box: a figure that
illustrates a definition sits directly below that box. The figures are NOT
produced at build time. Run

    python scripts/lp_figures/dsy.py
    python scripts/center_figures.py "lp-dsy-*.md" --keep-width
    python scripts/check_figure_labels.py "scripts/_figures/lp-dsy-*.md"

and paste the markup of scripts/_figures/lp-dsy-<name>.md into the .qmd.
Captions are Turkish (they are shown on the site); aria labels are ASCII.

Region figures use the same scale on both axes. Integer lattice points are
drawn as small dots: filled when they satisfy the constraints of the
relaxed problem, faint otherwise. A strip that a branching step cuts away
is shaded with the remark colour and outlined with a dashed border.
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, TEXT, THEORY, PRACTICE, BASE, REMARK, WIDE  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "lp-dsy-"

SUB = {"1": "&#8321;", "2": "&#8322;"}
X1, X2 = "x" + SUB["1"], "x" + SUB["2"]
LEQ, GEQ = "≤", "≥"


def save(name, markup):
    path = OUT_DIR / f"{PREFIX}{name}.md"
    path.write_text(markup, encoding="utf-8", newline="\n")
    print("wrote", path.name)


# ------------------------------------------------------------------------
# geometry helpers
# ------------------------------------------------------------------------
def clip_halfplane(poly, a1, a2, b):
    """Sutherland-Hodgman step: the part of a polygon with a1*x + a2*y <= b."""
    out = []
    n = len(poly)
    for i in range(n):
        p, q = poly[i - 1], poly[i]
        fp = a1 * p[0] + a2 * p[1] - b
        fq = a1 * q[0] + a2 * q[1] - b
        if fq <= 1e-12:
            if fp > 1e-12:
                t = fp / (fp - fq)
                out.append((p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1])))
            out.append(q)
        elif fp <= 1e-12:
            t = fp / (fp - fq)
            out.append((p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1])))
    return out


def region(p, halfplanes):
    """Region cut to the panel; halfplanes are (a1, a2, b): a1*x + a2*y <= b."""
    poly = [(p.xmin, p.ymin), (p.xmax, p.ymin), (p.xmax, p.ymax), (p.xmin, p.ymax)]
    for a1, a2, b in halfplanes:
        poly = clip_halfplane(poly, a1, a2, b)
        if not poly:
            break
    return poly


def line_in_panel(p, a1, a2, b):
    """The part of the line a1*x + a2*y = b inside the panel, or None."""
    pts = []
    eps = 1e-9
    if abs(a2) > eps:
        for x in (p.xmin, p.xmax):
            y = (b - a1 * x) / a2
            if p.ymin - eps <= y <= p.ymax + eps:
                pts.append((x, y))
    if abs(a1) > eps:
        for y in (p.ymin, p.ymax):
            x = (b - a2 * y) / a1
            if p.xmin - eps <= x <= p.xmax + eps:
                pts.append((x, y))
    uniq = []
    for q in pts:
        if all(abs(q[0] - r[0]) > 1e-7 or abs(q[1] - r[1]) > 1e-7 for r in uniq):
            uniq.append(q)
    if len(uniq) < 2:
        return None
    uniq.sort()
    return uniq[0], uniq[-1]


def panel(x0, y0, s, xr, yr):
    """Panel with the same scale s (pixels per unit) on both axes."""
    return Plot(x0, y0, s * (xr[1] - xr[0]), s * (yr[1] - yr[0]), xr, yr)


def draw_line(p, a1, a2, b, color, width=2.0, dash=None, opacity=1.0):
    seg = line_in_panel(p, a1, a2, b)
    if seg:
        p.line(list(seg), color, width, dash=dash, opacity=opacity)


def base(p, xticks, yticks):
    p.grid(xs=[t for t in xticks if t], ys=[t for t in yticks if t])
    p.axes(xticks, yticks, X1, X2)


def lattice(p, halfplanes, r_in=3.2, r_out=2.0):
    """Integer points of the panel; filled if they satisfy every halfplane."""
    inside, outside = [], []
    for x in range(math.ceil(p.xmin), math.floor(p.xmax) + 1):
        for y in range(math.ceil(p.ymin), math.floor(p.ymax) + 1):
            ok = all(a1 * x + a2 * y <= b + 1e-9 for a1, a2, b in halfplanes)
            (inside if ok else outside).append((x, y))
    for x, y in outside:
        p.add(f'<circle cx="{p.X(x):.1f}" cy="{p.Y(y):.1f}" r="{r_out}" fill="{TEXT}" opacity="0.28"/>')
    p.points(inside, TEXT, r_in)


def strip(p, halfplanes):
    """A cut-away strip: remark colour, dashed border."""
    p.polygon(region(p, halfplanes), REMARK, 0.22, stroke=REMARK, width=1.2, dash="5 4")


def canvas(p, pad_r=40, pad_b=44):
    return int(p.x0 + p.w + pad_r), int(p.y0 + p.h + pad_b)


NONNEG = [(-1, 0, 0), (0, -1, 0)]


# ============================================================
# yuvarlama: 7x1 + 4x2 <= 13, max z = 21x1 + 11x2; rounding fails
# ============================================================
def rounding():
    hp = [(7, 4, 13)] + NONNEG
    p = panel(70, 30, 92, (0, 3.2), (0, 3.9))
    base(p, (0, 1, 2, 3), (1, 2, 3))
    p.polygon(region(p, hp), THEORY, 0.15, stroke=THEORY, width=1.2)
    draw_line(p, 7, 4, 13, BASE, 2.0)
    p.label(0.95, 1.6, "7" + X1 + " + 4" + X2 + " = 13", 14, -18, BASE, 13)
    lattice(p, hp)
    # LP optimum, rounded point, integer optimum
    p.points([(13 / 7, 0)], THEORY, 5.4)
    p.label(13 / 7, 0, "(13/7, 0): z = 39", 14, -12, THEORY, 13)
    p.hollow_points([(2, 0)], REMARK, 6.5)
    p.label(2, 0, "(2, 0) uygun değil", 10, -34, REMARK, 13)
    p.hollow_points([(1, 0)], TEXT, 6.5)
    p.label(1, 0, "(1, 0): z = 21", -6, -12, TEXT, 12.5, "end")
    p.points([(0, 3)], PRACTICE, 5.6)
    p.label(0, 3, "(0, 3): z = 33", 12, -8, PRACTICE, 13.5, bold=True)
    p.label(1, 1, "(1, 1): z = 32", 10, -8, TEXT, 12.5)
    W, H = canvas(p, 60)
    cap = ("7x₁ + 4x₂ ≤ 13 bölgesi ve tam sayılı noktaları (koyu noktalar). Rahatlatılmış problemin optimumu "
           "(13/7, 0) noktasıdır. Yukarı yuvarlanan (2, 0) bölgenin dışında kalır, aşağı yuvarlanan (1, 0) ise "
           "z = 21 verir; tam sayılı optimum (0, 3) noktasında z = 33'tür ve LP optimumundan uzaktadır.")
    aria = ("Triangle 7x1 + 4x2 at most 13 with its integer points; LP optimum (13/7, 0), rounded point (2, 0) "
            "outside the region, truncated point (1, 0), integer optimum (0, 3).")
    save("yuvarlama", figure(W, H, [p], cap, aria=aria))


# ============================================================
# dallanma: the same triangle split at x1 = 13/7 into x1 <= 1 and x1 >= 2
# ============================================================
def branching_small():
    hp = [(7, 4, 13)] + NONNEG
    p = panel(70, 30, 92, (0, 3.2), (0, 3.9))
    base(p, (0, 1, 2, 3), (1, 2, 3))
    # the part x1 <= 1 is Alt Problem 2, the strip 1 < x1 < 2 is cut away
    p.polygon(region(p, hp + [(1, 0, 1)]), THEORY, 0.18, stroke=THEORY, width=1.3)
    strip(p, hp + [(-1, 0, -1), (1, 0, 2)])
    draw_line(p, 7, 4, 13, BASE, 2.0)
    p.line([(1, 0), (1, 3.9)], TEXT, 1.3, dash="6 4", opacity=0.75)
    p.line([(2, 0), (2, 3.9)], TEXT, 1.3, dash="6 4", opacity=0.75)
    p.label(1, 3.9, X1 + " " + LEQ + " 1", -6, 14, TEXT, 13, "end")
    p.label(2, 3.9, X1 + " " + GEQ + " 2", 6, 14, TEXT, 13)
    lattice(p, hp)
    p.label(0.5, 0.7, "Alt Problem 2", 0, 0, THEORY, 13, "middle")
    p.label(1.5, 0.2, "atılan", 0, 0, REMARK, 12, "middle")
    p.label(1.5, 0.2, "şerit", 0, 14, REMARK, 12, "middle")
    p.points([(13 / 7, 0)], TEXT, 4.0)
    p.label(13 / 7, 0, "(13/7, 0)", 12, -14, TEXT, 12.5)
    p.points([(1, 1.5)], PRACTICE, 5.4)
    p.label(1, 1.5, "(1, 3/2): z = 75/2", 10, -10, PRACTICE, 13, bold=True)
    p.label(2.55, 2.55, "Alt Problem 3:", 0, 0, REMARK, 12.5, "middle")
    p.label(2.55, 2.55, "uygun çözüm yok", 0, 16, REMARK, 12.5, "middle")
    W, H = canvas(p, 60)
    cap = ("x₁ = 13/7 değişkeninden dallanma. x₁ ≤ 1 dalı (Alt Problem 2) bölgenin sol parçasını alır; "
           "1 < x₁ < 2 şeridi atılır ve içinde tam sayılı nokta yoktur. x₁ ≥ 2 dalı (Alt Problem 3) "
           "bölgeyle kesişmez. Altı tam sayılı noktanın hepsi Alt Problem 2'de kalır.")
    aria = ("The triangle 7x1 + 4x2 at most 13 cut by the lines x1 = 1 and x1 = 2; the part x1 at most 1 is "
            "subproblem 2 with optimum (1, 3/2), the strip between is cut away, x1 at least 2 is empty.")
    save("dallanma", figure(W, H, [p], cap, aria=aria))


# ============================================================
# source example: x1 + x2 <= 6, 9x1 + 5x2 <= 45, max z = 8x1 + 5x2
# ============================================================
SRC = [(1, 1, 6), (9, 5, 45)] + NONNEG


def source_panel():
    p = panel(64, 30, 56, (0, 7), (0, 7))
    base(p, range(0, 8), range(1, 8))
    return p


def source_lines(p, labels=True):
    draw_line(p, 1, 1, 6, BASE, 1.8)
    draw_line(p, 9, 5, 45, PRACTICE, 1.8)
    if labels:
        p.label(4.9, 1.45, X1 + " + " + X2 + " = 6", 12, 4, BASE, 13)
        p.label(1.33, 6.6, "9" + X1 + " + 5" + X2 + " = 45", 10, 4, PRACTICE, 13)


def src_ap1():
    p = source_panel()
    p.polygon(region(p, SRC), THEORY, 0.15, stroke=THEORY, width=1.2)
    source_lines(p)
    lattice(p, SRC)
    p.points([(15 / 4, 9 / 4)], PRACTICE, 5.6)
    p.label(15 / 4, 9 / 4, "(15/4, 9/4)", 12, -10, PRACTICE, 13.5, bold=True)
    p.label(1.6, 1.25, "Alt Problem 1", 0, 0, THEORY, 13.5, "middle")
    W, H = canvas(p, 70)
    cap = ("Alt Problem 1, yani rahatlatılmış problem. Uygun bölge (0, 0), (5, 0), (15/4, 9/4), (0, 6) köşeli "
           "dörtgendir; koyu noktalar tam sayılı uygun noktalardır. Rahatlatılmış problemin optimumu "
           "(15/4, 9/4) köşesidir ve tam sayılı değildir.")
    aria = ("Feasible quadrilateral of x1 + x2 at most 6 and 9x1 + 5x2 at most 45 with its integer points; "
            "optimum (15/4, 9/4) of the relaxed problem.")
    save("ap1", figure(W, H, [p], cap, aria=aria))


def src_ap2_ap3():
    p = source_panel()
    p.polygon(region(p, SRC), TEXT, 0.0, stroke=TEXT, width=1.0, dash="4 4")
    p.polygon(region(p, SRC + [(1, 0, 3)]), THEORY, 0.18, stroke=THEORY, width=1.3)
    p.polygon(region(p, SRC + [(-1, 0, -4)]), PRACTICE, 0.22, stroke=PRACTICE, width=1.3)
    strip(p, SRC + [(-1, 0, -3), (1, 0, 4)])
    source_lines(p, labels=False)
    lattice(p, SRC)
    p.label(1.5, 1.2, "Alt Problem 3", 0, 0, THEORY, 13.5, "middle")
    p.label(1.5, 1.2, X1 + " " + LEQ + " 3", 0, 17, THEORY, 13, "middle")
    p.label(4.45, 0.2, "atılan", -10, -32, REMARK, 12, "end")
    p.label(4.45, 0.2, "şerit", -10, -18, REMARK, 12, "end")
    p.points([(3, 3)], THEORY, 5.4)
    p.label(3, 3, "(3, 3): z = 39", 10, -10, THEORY, 13, bold=True)
    p.points([(4, 9 / 5)], PRACTICE, 5.4)
    p.line([(4.08, 1.86), (4.92, 2.42)], PRACTICE, 1.0, opacity=0.8)
    p.label(5.0, 2.5, "(4, 9/5): z = 41", 0, 4, PRACTICE, 13, bold=True)
    p.label(5.3, 1.45, "Alt Problem 2", 0, 0, PRACTICE, 13.5)
    p.label(5.3, 1.45, X1 + " " + GEQ + " 4", 0, 15, PRACTICE, 13)
    W, H = canvas(p, 90)
    cap = ("x₁ = 15/4 değişkeninden dallanma. Alt Problem 3 (x₁ ≤ 3) bölgenin sol parçası, Alt Problem 2 "
           "(x₁ ≥ 4) sağdaki küçük üçgendir; 3 < x₁ < 4 şeridi atılır ve içinde tam sayılı nokta yoktur. "
           "Kalın noktalar iki alt problemin optimumlarıdır.")
    aria = ("The region of subproblem 1 split by x1 = 3 and x1 = 4: subproblem 3 on the left with optimum (3, 3), "
            "subproblem 2 the small triangle on the right with optimum (4, 9/5), the strip between cut away.")
    save("ap2-ap3", figure(W, H, [p], cap, aria=aria))


def src_ap4_ap5():
    ap2 = SRC + [(-1, 0, -4)]
    p = panel(64, 30, 150, (3, 5.8), (0, 2.8))
    base(p, (3, 4, 5), (1, 2))
    p.polygon(region(p, ap2), TEXT, 0.0, stroke=TEXT, width=1.0, dash="4 4")
    p.polygon(region(p, ap2 + [(0, 1, 1)]), PRACTICE, 0.22, stroke=PRACTICE, width=1.3)
    strip(p, ap2 + [(0, -1, -1), (0, 1, 2)])
    draw_line(p, 9, 5, 45, PRACTICE, 1.6, opacity=0.8)
    p.line([(3, 1), (5.8, 1)], TEXT, 1.2, dash="6 4", opacity=0.7)
    p.line([(3, 2), (5.8, 2)], TEXT, 1.2, dash="6 4", opacity=0.7)
    p.label(5.8, 1, X2 + " " + LEQ + " 1", -4, 16, TEXT, 13, "end")
    p.label(5.8, 2, X2 + " " + GEQ + " 2", -4, -8, TEXT, 13, "end")
    lattice(p, SRC)
    p.points([(4, 9 / 5)], TEXT, 4.2)
    p.label(4, 9 / 5, "(4, 9/5)", -10, -6, TEXT, 12.5, "end")
    p.points([(40 / 9, 1)], PRACTICE, 5.4)
    p.label(40 / 9, 1, "(40/9, 1): z = 365/9", 12, -10, PRACTICE, 13, bold=True)
    p.label(4.28, 0.3, "Alt Problem 5", 0, 0, PRACTICE, 13, "middle")
    p.label(4.1, 2.5, "Alt Problem 4 (" + X2 + " " + GEQ + " 2):", 0, 0, REMARK, 12.5)
    p.label(4.1, 2.5, "Alt Problem 2 ile kesişimi boş", 0, 16, REMARK, 12.5)
    p.label(4.0, 1.4, "atılan şerit", -10, 4, REMARK, 12, "end")
    W, H = canvas(p, 40)
    cap = ("Alt Problem 2'nin bölgesi (kesikli üçgen) x₂ = 9/5 değişkeninden bölünür. x₂ ≤ 1 dalı Alt Problem 5'in "
           "dörtgenini verir; 1 < x₂ < 2 şeridi atılır. Üçgenin en yüksek noktası x₂ = 9/5 olduğundan x₂ ≥ 2 "
           "dalı (Alt Problem 4) boştur.")
    aria = ("Close-up of the triangle of subproblem 2 cut by the lines x2 = 1 and x2 = 2: subproblem 5 below with "
            "optimum (40/9, 1), subproblem 4 above is empty.")
    save("ap4-ap5", figure(W, H, [p], cap, aria=aria))


def src_ap6_ap7():
    ap5 = SRC + [(-1, 0, -4), (0, 1, 1)]
    p = panel(64, 30, 150, (3, 5.8), (0, 2.1))
    base(p, (3, 4, 5), (1, 2))
    p.polygon(region(p, ap5), TEXT, 0.0, stroke=TEXT, width=1.0, dash="4 4")
    strip(p, ap5 + [(-1, 0, -4), (1, 0, 5)])
    draw_line(p, 9, 5, 45, PRACTICE, 1.6, opacity=0.8)
    p.line([(4, 0), (4, 1)], THEORY, 4.0)
    lattice(p, SRC)
    p.points([(40 / 9, 1)], TEXT, 4.2)
    p.label(40 / 9, 1, "(40/9, 1)", 8, -10, TEXT, 12.5)
    p.points([(4, 1)], THEORY, 5.4)
    p.label(4, 1, "(4, 1): z = 37", -12, -10, THEORY, 13, "end", bold=True)
    p.label(4, 0.5, "Alt Problem 7", -12, 4, THEORY, 13, "end")
    p.points([(5, 0)], PRACTICE, 5.6)
    p.label(5, 0, "(5, 0): z = 40", 12, -10, PRACTICE, 13, bold=True)
    p.label(5, 0, "Alt Problem 6", 12, -30, PRACTICE, 13)
    p.label(4.5, 1.45, "atılan şerit: 4 &lt; " + X1 + " &lt; 5", 0, 0, REMARK, 12.5, "middle")
    W, H = canvas(p, 40)
    cap = ("Alt Problem 5'in bölgesi (kesikli dörtgen) x₁ = 40/9 değişkeninden bölünür. x₁ ≤ 4 dalı (Alt Problem 7) "
           "x₁ = 4 üzerindeki kalın doğru parçasıdır, x₁ ≥ 5 dalı (Alt Problem 6) yalnız (5, 0) noktasıdır; "
           "aradaki 4 < x₁ < 5 şeridi atılır.")
    aria = ("Close-up of the quadrilateral of subproblem 5: subproblem 7 is the segment x1 = 4, x2 from 0 to 1 "
            "with optimum (4, 1); subproblem 6 is the single point (5, 0).")
    save("ap6-ap7", figure(W, H, [p], cap, aria=aria))


# ============================================================
# branch-and-bound trees
# ============================================================
BOX_W, BOX_H = 162, 80


def tree(nodes, edges):
    """nodes: {id: (cx, top, [lines], colour)}; edges: [(parent, child, text, side)]."""
    W = int(max(cx for cx, *_ in nodes.values()) + BOX_W / 2 + 16)
    H = int(max(top for _, top, *_ in nodes.values()) + BOX_H + 16)
    p = Plot(0, 0, W, H, (0, W), (H, 0))     # data y grows downward = pixels
    for a, b, text, side in edges:
        ax, atop = nodes[a][0], nodes[a][1]
        bx, btop = nodes[b][0], nodes[b][1]
        x0, y0 = ax + (-0.28 if bx < ax else 0.28) * BOX_W, atop + BOX_H
        x1, y1 = bx, btop
        p.arrow((x0, y0 + 2), (x1, y1 - 2), TEXT, 1.4, 8, opacity=0.7)
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        if side == "left":
            p.text_px(mx - 8, my + 4, text, TEXT, 13, "end")
        else:
            p.text_px(mx + 8, my + 4, text, TEXT, 13, "start")
    for cx, top, lines, col in nodes.values():
        x0 = cx - BOX_W / 2
        p.add(f'<rect x="{x0:.1f}" y="{top:.1f}" width="{BOX_W}" height="{BOX_H}" rx="8" '
              f'fill="{col}" fill-opacity="0.10" stroke="{col}" stroke-width="1.6"/>')
        for i, s in enumerate(lines):
            bold = i == 0
            colour = col if i in (0, len(lines) - 1) else TEXT
            p.text_px(cx, top + 19 + 18.5 * i, s, colour, 13 if i else 13.5, "middle", bold=bold)
    return p, W, H


def src_tree():
    L = [14, 136, 258, 380]
    nodes = {
        1: (330, L[0], ["Alt Problem 1", X1 + " = 15/4, " + X2 + " = 9/4", "z = 165/4 = Ü.S", "dallan: " + X1], THEORY),
        2: (200, L[1], ["Alt Problem 2", X1 + " = 4, " + X2 + " = 9/5", "z = 41", "dallan: " + X2], THEORY),
        3: (470, L[1], ["Alt Problem 3", X1 + " = 3, " + X2 + " = 3", "z = 39", "aday, A.S = 39"], BASE),
        4: (95, L[2], ["Alt Problem 4", "uygun çözüm yok", "", "budanır (D2)"], REMARK),
        5: (310, L[2], ["Alt Problem 5", X1 + " = 40/9, " + X2 + " = 1", "z = 365/9", "dallan: " + X1], THEORY),
        6: (205, L[3], ["Alt Problem 6", X1 + " = 5, " + X2 + " = 0", "z = 40", "aday, optimal *"], PRACTICE),
        7: (420, L[3], ["Alt Problem 7", X1 + " = 4, " + X2 + " = 1", "z = 37", "aday, 37 &lt; 39"], REMARK),
    }
    edges = [(1, 2, X1 + " " + GEQ + " 4", "left"), (1, 3, X1 + " " + LEQ + " 3", "right"),
             (2, 4, X2 + " " + GEQ + " 2", "left"), (2, 5, X2 + " " + LEQ + " 1", "right"),
             (5, 6, X1 + " " + GEQ + " 5", "left"), (5, 7, X1 + " " + LEQ + " 4", "right")]
    p, W, H = tree(nodes, edges)
    cap = ("Örneğin dal-sınır ağacı. Her kutuda alt problemin rahatlatılmış optimumu, z değeri ve verilen karar "
           "yazılıdır; oklarda eklenen kısıt durur. Alt Problem 4 uygun olmadığı, Alt Problem 3, 6 ve 7 tam sayılı "
           "çözüm verdiği için dallanmaz. En iyi aday Alt Problem 6'dır: x₁ = 5, x₂ = 0, z = 40.")
    aria = ("Branch and bound tree of the example with seven subproblems; subproblem 1 branches on x1 into 2 and 3, "
            "2 branches on x2 into 4 (infeasible) and 5, 5 branches on x1 into 6 (optimal, z = 40) and 7 (z = 37).")
    save("agac", figure(W, H, [p], cap, css_class=WIDE, aria=aria))


# ============================================================
# extra example: 2x1 + 3x2 <= 6, 2x1 + x2 <= 5, max z = 3x1 + 2x2
# ============================================================
EK = [(2, 3, 6), (2, 1, 5)] + NONNEG


def ek_panel():
    p = panel(64, 30, 120, (0, 3.4), (0, 2.6))
    base(p, (0, 1, 2, 3), (1, 2))
    return p


def ek_first():
    p = ek_panel()
    p.polygon(region(p, EK), TEXT, 0.0, stroke=TEXT, width=1.0, dash="4 4")
    p.polygon(region(p, EK + [(1, 0, 2)]), THEORY, 0.18, stroke=THEORY, width=1.3)
    strip(p, EK + [(-1, 0, -2), (1, 0, 3)])
    draw_line(p, 2, 3, 6, BASE, 1.8)
    draw_line(p, 2, 1, 5, PRACTICE, 1.8)
    p.label(0.15, 2.0, "2" + X1 + " + 3" + X2 + " = 6", 12, -8, BASE, 13)
    p.label(2.62, 0, "2" + X1 + " + " + X2 + " = 5", 6, -30, PRACTICE, 13)
    p.line([(2, 0), (2, 2.6)], TEXT, 1.2, dash="6 4", opacity=0.7)
    p.line([(3, 0), (3, 2.6)], TEXT, 1.2, dash="6 4", opacity=0.7)
    p.label(2, 2.6, X1 + " " + LEQ + " 2", -6, 14, TEXT, 13, "end")
    p.label(3, 2.6, X1 + " " + GEQ + " 3", 6, 14, TEXT, 13)
    lattice(p, EK)
    p.points([(9 / 4, 1 / 2)], TEXT, 4.4)
    p.label(9 / 4, 1 / 2, "(9/4, 1/2)", 12, -2, TEXT, 12.5)
    p.points([(2, 2 / 3)], THEORY, 5.4)
    p.label(2, 2 / 3, "(2, 2/3): z = 22/3", -10, 20, THEORY, 13, "end", bold=True)
    p.label(0.75, 0.2, "Alt Problem 2", 0, 0, THEORY, 13, "middle")
    p.label(3, 1.6, "Alt Problem 3:", -8, 0, REMARK, 12.5, "end")
    p.label(3, 1.6, "boş", -8, 16, REMARK, 12.5, "end")
    W, H = canvas(p, 110)
    cap = ("Ek örnekte Alt Problem 1'in bölgesi (kesikli) ve x₁ = 9/4 değişkeninden dallanma. x₁ ≤ 2 dalı "
           "Alt Problem 2'dir; 2 < x₁ < 3 şeridi atılır; bölgede x₁ en fazla 5/2 olduğundan x₁ ≥ 3 dalı "
           "(Alt Problem 3) boştur.")
    aria = ("Region of 2x1 + 3x2 at most 6 and 2x1 + x2 at most 5 with its integer points, LP optimum (9/4, 1/2); "
            "subproblem 2 is the part x1 at most 2 with optimum (2, 2/3); x1 at least 3 is empty.")
    save("ek-ilk", figure(W, H, [p], cap, aria=aria))


def ek_second():
    ap2 = EK + [(1, 0, 2)]
    p = ek_panel()
    p.polygon(region(p, ap2), TEXT, 0.0, stroke=TEXT, width=1.0, dash="4 4")
    strip(p, ap2 + [(0, -1, 0), (0, 1, 1)])
    ap5 = ap2 + [(0, -1, -1)]
    p.polygon(region(p, ap5 + [(1, 0, 1)]), THEORY, 0.20, stroke=THEORY, width=1.3)
    strip(p, ap5 + [(-1, 0, -1), (1, 0, 2)])
    p.line([(0, 0), (2, 0)], PRACTICE, 4.2)
    draw_line(p, 2, 3, 6, BASE, 1.6, opacity=0.8)
    p.line([(1, 1), (1, 2.6)], TEXT, 1.2, dash="6 4", opacity=0.7)
    p.label(1, 2.6, X1 + " " + LEQ + " 1", -6, 14, TEXT, 13, "end")
    lattice(p, EK)
    p.points([(3 / 2, 1)], TEXT, 4.4)
    p.label(3 / 2, 1, "(3/2, 1): z = 13/2", 12, -8, TEXT, 12.5)
    p.points([(1, 4 / 3)], THEORY, 5.4)
    p.label(1, 4 / 3, "(1, 4/3): z = 17/3", 10, -10, THEORY, 13, bold=True)
    p.label(0.45, 1.3, "Alt Problem 6", 0, 4, THEORY, 13, "middle")
    p.points([(2, 0)], PRACTICE, 5.6)
    p.label(2, 0, "(2, 0): z = 6", 12, -10, PRACTICE, 13, bold=True)
    p.label(1.0, 0, "Alt Problem 4", 0, -12, PRACTICE, 13, "middle")
    p.label(1.0, 0.45, "atılan şerit", 0, 4, REMARK, 12.5, "middle")
    W, H = canvas(p, 110)
    cap = ("Ek örneğin sonraki adımları. Alt Problem 2'nin bölgesi (kesikli) x₂ = 2/3 değişkeninden bölünür: "
           "x₂ ≤ 0 dalı x₁ ekseni üzerindeki kalın doğru parçasıdır (Alt Problem 4), x₂ ≥ 1 dalı Alt Problem 5'tir. "
           "Alt Problem 5 de x₁ = 3/2 değişkeninden bölünür; x₁ ≤ 1 dalı Alt Problem 6'nın dörtgenidir, "
           "x₁ ≥ 2 dalı (Alt Problem 7) boştur. Gri şeritler (0 < x₂ < 1 ve 1 < x₁ < 2) atılan parçalardır.")
    aria = ("Region of subproblem 2 split by x2: subproblem 4 is the segment from (0,0) to (2,0) with optimum (2,0), "
            "subproblem 5 is the part x2 at least 1 with optimum (3/2, 1); its part x1 at most 1 is subproblem 6 "
            "with optimum (1, 4/3).")
    save("ek-ikinci", figure(W, H, [p], cap, aria=aria))


def ek_tree():
    L = [14, 136, 258, 380]
    nodes = {
        1: (330, L[0], ["Alt Problem 1", X1 + " = 9/4, " + X2 + " = 1/2", "z = 31/4 = Ü.S", "dallan: " + X1], THEORY),
        2: (200, L[1], ["Alt Problem 2", X1 + " = 2, " + X2 + " = 2/3", "z = 22/3", "dallan: " + X2], THEORY),
        3: (470, L[1], ["Alt Problem 3", "uygun çözüm yok", "", "budanır (D2)"], REMARK),
        4: (95, L[2], ["Alt Problem 4", X1 + " = 2, " + X2 + " = 0", "z = 6", "aday, optimal *"], PRACTICE),
        5: (310, L[2], ["Alt Problem 5", X1 + " = 3/2, " + X2 + " = 1", "z = 13/2", "dallan: " + X1], THEORY),
        6: (205, L[3], ["Alt Problem 6", X1 + " = 1, " + X2 + " = 4/3", "z = 17/3", "budanır (D1)"], REMARK),
        7: (420, L[3], ["Alt Problem 7", "uygun çözüm yok", "", "budanır (D2)"], REMARK),
    }
    edges = [(1, 2, X1 + " " + LEQ + " 2", "left"), (1, 3, X1 + " " + GEQ + " 3", "right"),
             (2, 4, X2 + " " + LEQ + " 0", "left"), (2, 5, X2 + " " + GEQ + " 1", "right"),
             (5, 6, X1 + " " + LEQ + " 1", "left"), (5, 7, X1 + " " + GEQ + " 2", "right")]
    p, W, H = tree(nodes, edges)
    cap = ("Ek örneğin dal-sınır ağacı. Alt Problem 3 ve 7 uygun olmadığı için, Alt Problem 6 da z = 17/3 değeri "
           "mevcut aday değeri 6'yı geçemediği için budanır. Tek aday Alt Problem 4'tür: x₁ = 2, x₂ = 0, z = 6.")
    aria = ("Branch and bound tree of the extra example with seven subproblems; subproblem 4 gives the optimum "
            "(2, 0) with z = 6, subproblems 3 and 7 are infeasible, subproblem 6 is pruned by its bound 17/3.")
    save("ek-agac", figure(W, H, [p], cap, css_class=WIDE, aria=aria))


if __name__ == "__main__":
    rounding()
    branching_small()
    src_ap1()
    src_ap2_ap3()
    src_ap4_ap5()
    src_ap6_ap7()
    src_tree()
    ek_first()
    ek_second()
    ek_tree()
