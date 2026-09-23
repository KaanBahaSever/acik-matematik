# -*- coding: utf-8 -*-
"""
Figures of the chapter "Alıştırmalar"
(dersler/lineer-programlama/alistirmalar.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution,
exercise or callout), never inside a definition box: a figure that
illustrates a definition sits directly below that box. The figures are NOT
produced at build time. Run

    python scripts/lp_figures/als.py
    python scripts/center_figures.py "lp-als-*.md" --keep-width
    python scripts/check_figure_labels.py "scripts/_figures/lp-als-*.md"

and paste the markup of scripts/_figures/lp-als-<name>.md into the .qmd.
The captions are Turkish on purpose (they are shown on the site); the aria
labels are plain ASCII.

Every two-variable figure uses the same scale on both axes, so the gradient
arrow is drawn perpendicular to the dashed objective (level) lines.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, TEXT, THEORY, PRACTICE, BASE, REMARK  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "lp-als-"

MINUS = "&#8722;"
SUB = {"1": "&#8321;", "2": "&#8322;", "3": "&#8323;", "4": "&#8324;"}
X1, X2 = "x" + SUB["1"], "x" + SUB["2"]


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
    """Feasible region cut to the panel; halfplanes are (a1, a2, b): a1*x + a2*y <= b."""
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


def canvas(p, pad_r=40, pad_b=44):
    return int(p.x0 + p.w + pad_r), int(p.y0 + p.h + pad_b)


# ============================================================
# grafik: max z = 180x1 + 120x2, optimal vertex B(1/2, 3)
# ============================================================
def graphic():
    p = panel(70, 30, 80, (0, 4.6), (0, 4.6))
    base(p, (0, 1, 2, 3, 4), (1, 2, 3, 4))
    hp = [(1, 1, 4), (20, 10, 40), (1, 0, 2), (0, 1, 3), (-1, 0, 0), (0, -1, 0)]
    p.polygon(region(p, hp), THEORY, 0.16)
    draw_line(p, 1, 1, 4, BASE, 1.6)
    draw_line(p, 20, 10, 40, PRACTICE)
    draw_line(p, 1, 0, 2, REMARK, 1.6)
    draw_line(p, 0, 1, 3, THEORY, 1.8)
    p.label(3.55, 0.45, X1 + " + " + X2 + " = 4", 8, 0, BASE, 12.5)
    p.label(0.08, 4.3, "20" + X1 + " + 10" + X2 + " = 40", 0, 0, PRACTICE, 12.5)
    p.label(2, 4.45, X1 + " = 2", 7, 4, REMARK, 12.5)
    p.label(3.1, 3, X2 + " = 3", 0, -8, THEORY, 12.5)
    # level lines 3x1 + 2x2 = 6 (z = 360) and 3x1 + 2x2 = 7.5 (z = 450)
    draw_line(p, 3, 2, 6, TEXT, 1.3, dash="7 5", opacity=0.75)
    draw_line(p, 3, 2, 7.5, PRACTICE, 1.4, dash="7 5", opacity=0.95)
    p.label(1.0, 1.2, "z = 360", -8, 0, TEXT, 12.5, "end")
    p.label(2.3, 0.3, "z = 450", 10, 0, PRACTICE, 12.5)
    # gradient c = (180, 120), drawn along (3, 2)
    p.arrow((2.9, 2.2), (2.9 + 0.2 * 3, 2.2 + 0.2 * 2), TEXT, 1.8, 10)
    p.label(2.9 + 0.2 * 3, 2.2 + 0.2 * 2, "c = (180, 120)", -20, -10, TEXT, 12.5)
    verts = [((0, 0), "O", 8, -8, "start"),
             ((2, 0), "A(2, 0)", 8, 17, "start"),
             ((0.5, 3), "B(1/2, 3)", 8, -10, "start"),
             ((0, 3), "C(0, 3)", 8, 18, "start")]
    p.points([q for q, *_ in verts], TEXT, 4.0)
    p.points([(0.5, 3)], PRACTICE, 5.6)
    for (x, y), s, dx, dy, anc in verts:
        opt = (x, y) == (0.5, 3)
        p.label(x, y, s, dx, dy, PRACTICE if opt else TEXT, 13.5, anc, bold=opt)
    W, H = canvas(p)
    cap = ("Uygun bölge OABC dörtgenidir; x₁ + x₂ ≤ 4 kısıtı bölgeye hiç değmez, x₁ = 2 doğrusu bölgeye yalnız A "
           "köşesinde değer. Kesikli doğrular z = 180x₁ + 120x₂ amaç fonksiyonunun z = 360 (A ve C'den geçer) ve "
           "z = 450 seviye doğrularıdır. Seviye doğrusu gradyan yönünde kaydırıldığında bölgeden en son "
           "B(1/2, 3) köşesinde ayrılır: max z = 450.")
    aria = ("Feasible quadrilateral OABC with O(0,0), A(2,0), B(1/2,3), C(0,3) bounded by 20x1 + 10x2 = 40 and x2 = 3; "
            "the lines x1 + x2 = 4 and x1 = 2 are also drawn; dashed level lines z = 360 through A and C and "
            "z = 450 through B, gradient arrow, optimal vertex B.")
    save("grafik", figure(W, H, [p], cap, aria=aria))


# ============================================================
# dya-bolge: max z = 11x1 + 4x2, 7x1 + 6x2 <= 84, 4x1 + 2x2 >= 32
# ============================================================
def sensitivity_region():
    p = panel(70, 30, 25, (0, 15), (0, 17))
    base(p, (0, 4, 8, 12), (4, 8, 12, 16))
    hp = [(7, 6, 84), (-4, -2, -32), (-1, 0, 0), (0, -1, 0)]
    p.polygon(region(p, hp), THEORY, 0.18)
    draw_line(p, 7, 6, 84, BASE)
    draw_line(p, 4, 2, 32, PRACTICE)
    p.label(0.9, 14.3, "7" + X1 + " + 6" + X2 + " = 84", 0, 0, BASE, 12.5)
    p.label(1.2, 16.1, "4" + X1 + " + 2" + X2 + " = 32", 0, 0, PRACTICE, 12.5)
    # level lines 11x1 + 4x2 = 88 and = 132, drawn up to x2 = 13
    p.line([(8, 0), (36 / 11, 13)], TEXT, 1.3, dash="7 5", opacity=0.75)
    p.line([(12, 0), (80 / 11, 13)], REMARK, 1.4, dash="7 5", opacity=0.95)
    p.label(36 / 11, 13, "z = 88", 0, -7, TEXT, 12.5, "middle")
    p.label(80 / 11, 13, "z = 132", 0, -7, REMARK, 12.5, "middle")
    # simplex path X0 (infeasible) -> X1 -> X2
    p.line([(0, 0), (7.7, 0)], PRACTICE, 2.6)
    p.arrow((7.0, 0), (8, 0), PRACTICE, 2.6, 11)
    p.line([(8, 0), (11.7, 0)], PRACTICE, 2.6)
    p.arrow((11.0, 0), (12, 0), PRACTICE, 2.6, 11)
    p.hollow_points([(0, 0)], PRACTICE, 5.0)
    p.points([(8, 0), (12, 0)], PRACTICE, 4.8)
    p.points([(12 / 5, 56 / 5)], TEXT, 4.0)
    p.label(0, 0, "X₀", 8, -9, TEXT, 13)
    p.label(8, 0, "X₁ = (8, 0)", 0, 32, TEXT, 13, "middle")
    p.label(12, 0, "X₂ = (12, 0)", 0, 32, PRACTICE, 13, "middle", bold=True)
    p.label(12 / 5, 56 / 5, "(12/5, 56/5)", 9, -2, TEXT, 13)
    W, H = canvas(p, 60)
    cap = ("Uygun bölge (8, 0), (12, 0) ve (12/5, 56/5) köşeli üçgendir. Büyük M yöntemi uygun bölgenin dışındaki "
           "X₀ = (0, 0) noktasından başlar, X₁ = (8, 0) köşesine ve oradan optimal X₂ = (12, 0) köşesine gider. "
           "Kesikli doğrular z = 11x₁ + 4x₂ amaç fonksiyonunun z = 88 ve z = 132 seviye doğrularıdır.")
    aria = ("Feasible triangle with vertices (8,0), (12,0), (12/5,56/5) between 7x1 + 6x2 = 84 and 4x1 + 2x2 = 32; "
            "the Big M path goes from the infeasible origin to (8,0) and then to (12,0); dashed level lines "
            "z = 88 and z = 132.")
    save("dya-bolge", figure(W, H, [p], cap, aria=aria))


# ============================================================
# dua-nokta: the primal feasible set is the single point (3, 0)
# ============================================================
def dual_point():
    p = panel(70, 30, 58, (0, 6), (0, 6.6))
    base(p, (0, 1, 2, 3, 4, 5), (1, 2, 3, 4, 5, 6))
    # the half-planes 2x1 + x2 >= 6 and x1 + 2x2 <= 5, lightly shaded
    p.polygon(region(p, [(-2, -1, -6), (1, 2, 5), (-1, 0, 0), (0, -1, 0)]), THEORY, 0.14)
    draw_line(p, 2, 1, 6, BASE)
    draw_line(p, 1, 1, 3, PRACTICE, 2.2)
    draw_line(p, 1, 2, 5, REMARK)
    p.label(0.35, 6.2, "2" + X1 + " + " + X2 + " = 6", 10, 0, BASE, 12.5)
    p.label(0.3, 2.7, X1 + " + " + X2 + " = 3", -2, -10, PRACTICE, 12.5)
    p.label(5.2, 0.4, X1 + " + 2" + X2 + " = 5", -6, -8, REMARK, 12.5, "end")
    p.points([(3, 0)], PRACTICE, 5.8)
    p.label(3, 0, "(3, 0)", 10, -10, PRACTICE, 13.5, "start", bold=True)
    W, H = canvas(p)
    cap = ("Açık boyalı bölge 2x₁ + x₂ ≥ 6 ve x₁ + 2x₂ ≤ 5 eşitsizliklerinin ortak bölgesidir. "
           "Eşitlik kısıtı yüzünden uygun çözümler x₁ + x₂ = 3 doğrusu üzerinde olmalıdır ve bu doğru bölgeye "
           "yalnız (3, 0) noktasında değer: esas problemin tek uygun çözümü (3, 0)'dır.")
    aria = ("The lines 2x1 + x2 = 6, x1 + x2 = 3 and x1 + 2x2 = 5; the shaded region of the two inequalities meets "
            "the line x1 + x2 = 3 only at the point (3,0), the unique feasible point.")
    save("dua-nokta", figure(W, H, [p], cap, aria=aria))


# ============================================================
# dsy-bolge: LP relaxation (sub-problem 1) and the strips of 2 and 3
# ============================================================
def bb_region():
    p = panel(70, 30, 70, (0, 4.4), (0, 5))
    base(p, (0, 1, 2, 3, 4), (1, 2, 3, 4, 5))
    lp = [(6, 2, 19), (2, 3, 13), (-1, 0, 0), (0, -1, 0)]
    p.polygon(region(p, lp), THEORY, 0.10)
    p.polygon(region(p, lp + [(1, 0, 2)]), PRACTICE, 0.20)
    p.polygon(region(p, lp + [(-1, 0, -3)]), REMARK, 0.30)
    draw_line(p, 6, 2, 19, BASE)
    draw_line(p, 2, 3, 13, THEORY)
    draw_line(p, 1, 0, 2, PRACTICE, 1.4, dash="5 4", opacity=0.9)
    draw_line(p, 1, 0, 3, REMARK, 1.4, dash="5 4", opacity=0.9)
    p.label(1.5, 5, "6" + X1 + " + 2" + X2 + " = 19", 0, -8, BASE, 12.5, "middle")
    p.label(3.3, 2.1, "2" + X1 + " + 3" + X2 + " = 13", 14, 0, THEORY, 12.5)
    p.label(2, 4.7, X1 + " = 2", 6, 4, PRACTICE, 12.5)
    p.label(3, 4.1, X1 + " = 3", 7, 4, REMARK, 12.5)
    p.label(0.9, 1.3, "Alt Problem 2", 0, 0, PRACTICE, 12.5, "middle")
    p.label(3.25, 0.25, "Alt Problem 3", 8, 0, REMARK, 12.5)
    # integer points of the LP region
    ints = [(i, j) for i in range(5) for j in range(6) if 6 * i + 2 * j <= 19 and 2 * i + 3 * j <= 13]
    p.points(ints, TEXT, 2.6)
    p.hollow_points([(31 / 14, 20 / 7)], TEXT, 5.0)
    p.label(31 / 14, 20 / 7, "(31/14, 20/7)", 10, -8, TEXT, 13)
    p.points([(2, 3)], PRACTICE, 5.6)
    p.label(2, 3, "(2, 3)", -9, 18, PRACTICE, 13.5, "end", bold=True)
    p.points([(3, 0.5)], REMARK, 5.0)
    p.label(3, 0.5, "(3, 1/2)", -9, -6, REMARK, 13, "end")
    W, H = canvas(p, 70)
    cap = ("Alt Problem 1'in (tam sayı koşulsuz problemin) uygun bölgesi dörtgendir ve LP optimumu "
           "(31/14, 20/7) noktasındadır. x₁ ≤ 2 ve x₁ ≥ 3 dalları bölgenin iki şeridini ayırır; aradaki "
           "2 < x₁ < 3 şeridinde hiç tam sayılı nokta yoktur. Alt Problem 2'nin optimumu (2, 3), "
           "Alt Problem 3'ünkü (3, 1/2) noktasıdır. Küçük noktalar bölgedeki tam sayılı noktalardır.")
    aria = ("LP region of 6x1 + 2x2 at most 19 and 2x1 + 3x2 at most 13 with the LP optimum (31/14, 20/7); "
            "the strip x1 at most 2 (sub-problem 2, optimum (2,3)) and the small triangle x1 at least 3 "
            "(sub-problem 3, optimum (3,1/2)) are shaded; integer points are marked.")
    save("dsy-bolge", figure(W, H, [p], cap, aria=aria))


# ============================================================
# dsy-ap3: zoom on sub-problem 3 and its branches 4 to 7
# ============================================================
def bb_zoom():
    p = panel(70, 30, 300, (2.8, 4.2), (0, 1.2))
    p.grid(xs=(3, 3.5, 4), ys=(0.5, 1))
    p.axes((3, 3.5, 4), (0, 0.5, 1), X1, X2, xfmt=lambda v: f"{v:g}".replace(".", ","),
           yfmt=lambda v: f"{v:g}".replace(".", ","))
    lp3 = [(6, 2, 19), (2, 3, 13), (-1, 0, -3), (0, -1, 0)]
    p.polygon(region(p, lp3), REMARK, 0.22)
    draw_line(p, 6, 2, 19, BASE)
    draw_line(p, 1, 0, 3, REMARK, 1.4, dash="5 4", opacity=0.9)
    draw_line(p, 1, 0, 4, TEXT, 1.4, dash="5 4", opacity=0.7)
    draw_line(p, 0, 1, 1, TEXT, 1.4, dash="5 4", opacity=0.7)
    p.label(3.05, 0.8, "6" + X1 + " + 2" + X2 + " = 19", 6, 0, BASE, 12.5)
    p.label(3, 1.12, X1 + " = 3", 6, 4, REMARK, 12.5)
    p.label(4, 1.12, X1 + " = 4", -7, 4, TEXT, 12.5, "end")
    p.label(3.7, 1, X2 + " = 1", 0, -8, TEXT, 12.5)
    # sub-problem 4: the segment from (3, 0) to (19/6, 0)
    p.line([(3, 0), (19 / 6, 0)], PRACTICE, 5.0)
    p.points([(3, 0.5)], REMARK, 5.0)
    p.label(3, 0.5, "(3, 1/2)", 10, -6, REMARK, 13)
    p.points([(19 / 6, 0)], PRACTICE, 5.0)
    p.label(19 / 6, 0, "(19/6, 0)", 8, -10, PRACTICE, 13)
    p.points([(3, 0)], TEXT, 5.4)
    p.label(3, 0, "(3, 0)", -8, -10, TEXT, 13.5, "end", bold=True)
    p.label(3.12, 0.25, "Alt Problem 3", 14, 0, REMARK, 12.5)
    W, H = canvas(p, 50)
    cap = ("Alt Problem 3'ün uygun bölgesi (3, 0), (19/6, 0), (3, 1/2) köşeli küçük üçgendir. x₂ ≥ 1 yarı düzlemi "
           "bu üçgene değmez (Alt Problem 5 uygun değildir); x₂ ≤ 0 ile kesişimi kalın çizilen doğru parçasıdır "
           "(Alt Problem 4). Bu parçanın x₁ ≤ 3 ile kesişimi yalnız (3, 0) noktasıdır (Alt Problem 6), "
           "x₁ ≥ 4 ile kesişimi boştur (Alt Problem 7).")
    aria = ("Zoom on the small triangle of sub-problem 3 with vertices (3,0), (19/6,0), (3,1/2); the dashed lines "
            "x2 = 1 and x1 = 4 miss it; the thick segment from (3,0) to (19/6,0) is sub-problem 4 and the point "
            "(3,0) is sub-problem 6.")
    save("dsy-ap3", figure(W, H, [p], cap, aria=aria))


# ============================================================
# dsy-agac: branch and bound tree
# ============================================================
def bb_tree():
    W, H = 690, 470
    p = Plot(0, 0, W, H, (0, W), (H, 0))   # data y grows downward = pixels
    bw, bh = 176, 64
    nodes = {
        1: (345, 14, THEORY, ["Alt Problem 1", "(31/14, 20/7)", "z = 22,5  (üst sınır)"]),
        2: (120, 148, PRACTICE, ["Alt Problem 2", "(2, 3), z = 22", "aday (D3), A.S = 22, optimal"]),
        3: (470, 148, THEORY, ["Alt Problem 3", "(3, 1/2), z = 17", "D1 ile budanabilir"]),
        4: (345, 282, THEORY, ["Alt Problem 4", "(19/6, 0), z = 95/6", "D1 ile budanabilir"]),
        5: (585, 282, REMARK, ["Alt Problem 5", "uygun çözüm yok", "budanır (D2)"]),
        6: (220, 400, TEXT, ["Alt Problem 6", "(3, 0), z = 15", "aday (D3)"]),
        7: (470, 400, REMARK, ["Alt Problem 7", "uygun çözüm yok", "budanır (D2)"]),
    }
    edges = [(1, 2, X1 + " ≤ 2"), (1, 3, X1 + " ≥ 3"), (3, 4, X2 + " ≤ 0"), (3, 5, X2 + " ≥ 1"),
             (4, 6, X1 + " ≤ 3"), (4, 7, X1 + " ≥ 4")]
    for a, b, lab in edges:
        xa, ya = nodes[a][0], nodes[a][1] + bh
        xb, yb = nodes[b][0], nodes[b][1]
        p.arrow((xa, ya + 2), (xb, yb - 3), TEXT, 1.5, 9, opacity=0.7)
        mx, my = (xa + xb) / 2, (ya + yb) / 2
        left = xb < xa
        p.text_px(mx + (-6 if left else 6), my - 6, lab, TEXT, 12.5, "end" if left else "start")
    for k, (cx, top, col, lines) in nodes.items():
        p.add(f'<rect x="{cx - bw / 2:.1f}" y="{top}" width="{bw}" height="{bh}" rx="8" '
              f'fill="{col}" fill-opacity="0.10" stroke="{col}" stroke-width="{2.4 if k == 2 else 1.5}"/>')
        p.text_px(cx, top + 19, lines[0], col, 13, "middle", bold=True)
        p.text_px(cx, top + 37, lines[1], TEXT, 12.5, "middle")
        p.text_px(cx, top + 55, lines[2], TEXT, 11.5, "middle")
    cap = ("Dal-sınır ağacı. Her kutuda alt problemin LP optimumu, amaç değeri ve budama kuralı yazılıdır; oklar "
           "eklenen dal kısıtını gösterir. Alt Problem 3 ve 4, değerleri A.S = 22'yi aşmadığı için D1 ile budanabilirdi; "
           "yöntemin adımlarını göstermek için dallandırıldılar. Aday çözümler Alt Problem 2 (z = 22) ve "
           "Alt Problem 6 (z = 15)'dır; en büyüğü Alt Problem 2'nin (2, 3) çözümüdür.")
    aria = ("Branch and bound tree: sub-problem 1 branches on x1 into sub-problems 2 (integer, z = 22) and 3; "
            "3 branches on x2 into 4 and 5 (infeasible); 4 branches on x1 into 6 (integer, z = 15) and 7 (infeasible).")
    save("dsy-agac", figure(W, H, [p], cap, aria=aria))


if __name__ == "__main__":
    graphic()
    sensitivity_region()
    dual_point()
    bb_region()
    bb_zoom()
    bb_tree()
