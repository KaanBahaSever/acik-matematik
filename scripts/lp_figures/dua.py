# -*- coding: utf-8 -*-
"""
Figures of the chapter "Dualite"
(dersler/lineer-programlama/dualite.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution,
exercise or callout), never inside a definition box: a figure that
illustrates a definition sits directly below that box. The figures are NOT
produced at build time. Run

    python scripts/lp_figures/dua.py
    python scripts/center_figures.py "lp-dua-*.md" --keep-width
    python scripts/check_figure_labels.py "scripts/_figures/lp-dua-*.md"

and paste the markup of scripts/_figures/lp-dua-<name>.md into the .qmd.
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
PREFIX = "lp-dua-"

MINUS = "&#8722;"
SUB = {"1": "&#8321;", "2": "&#8322;", "3": "&#8323;", "4": "&#8324;",
       "5": "&#8325;", "6": "&#8326;"}
X1, X2 = "x" + SUB["1"], "x" + SUB["2"]
Y1, Y2 = "y" + SUB["1"], "y" + SUB["2"]


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


def base(p, xticks, yticks, xl=X1, yl=X2):
    p.grid(xs=[t for t in xticks if t], ys=[t for t in yticks if t])
    p.axes(xticks, yticks, xl, yl)


def canvas(p, pad_r=40, pad_b=44):
    return int(p.x0 + p.w + pad_r), int(p.y0 + p.h + pad_b)


# ============================================================
# ornek5-yol: the simplex path of the primal of Example 5
# ============================================================
def example5_path():
    p = panel(70, 30, 7.4, (0, 66), (0, 52))
    base(p, (0, 10, 20, 30, 40, 50, 60), (10, 20, 30, 40, 50))
    hp = [(1, 1, 50), (2, 1, 110), (1, 2, 80), (1, 5, 185), (5, 6, 300), (-1, 0, 0), (0, -1, 0)]
    p.polygon(region(p, hp), THEORY, 0.14)
    draw_line(p, 1, 1, 50, BASE)
    draw_line(p, 1, 2, 80, REMARK)
    draw_line(p, 1, 5, 185, THEORY)
    p.label(44, 6, X1 + " + " + X2 + " = 50", -8, 0, BASE, 12, "end")
    p.label(66, 7, X1 + " + 2" + X2 + " = 80", 0, -52, REMARK, 12, "end")
    p.label(66, 23.8, X1 + " + 5" + X2 + " = 185", 0, -24, THEORY, 12, "end")
    # level line z = 650 through the optimum
    draw_line(p, 10, 15, 650, PRACTICE, 1.4, dash="7 5", opacity=0.95)
    p.label(46, 12.6, "z = 650", 8, 6, PRACTICE, 12.5)
    # simplex path X0 -> X1 -> X2 -> X3
    path = [(0, 0), (0, 37), (10, 35), (20, 30)]
    for a, b in zip(path, path[1:]):
        p.arrow(a, b, PRACTICE, 2.6, 10)
    p.points(path[:3], TEXT, 4.2)
    p.points([path[3]], PRACTICE, 5.6)
    p.label(0, 0, "X₀", 9, -8, TEXT, 13)
    p.label(0, 37, "X₁", 8, 18, TEXT, 13)
    p.label(10, 35, "X₂", -6, 20, TEXT, 13, "end")
    p.label(20, 30, "X₃(20, 30)", -8, 22, PRACTICE, 13.5, "end", bold=True)
    W, H = canvas(p)
    cap = ("Beş kısıtlı maksimum probleminin uygun bölgesi. Simpleks yöntem X₀(0, 0) köşesinden (z = 0) başlar; "
           "x₂ baza girince X₁(0, 37) köşesine (z = 555), x₁ baza girince X₂(10, 35) köşesine (z = 625), "
           "x₆ baza girince X₃(20, 30) köşesine (z = 650) geçer. Kesikli doğru z = 650 seviye doğrusudur. "
           "Şekilde yalnız bölgeyi sınırlayan kısıt doğruları çizildi: 2x₁ + x₂ ≤ 110 ve 5x₁ + 6x₂ ≤ 300 "
           "kısıtları bölgenin her noktasında kendiliğinden sağlanır; optimal çözümde aylak değişkenleri x₄ = 40 ve x₇ = 20'dir.")
    aria = ("Feasible pentagon of the five-constraint maximum problem with vertices (0,0), (50,0), (20,30), (10,35), (0,37) "
            "bounded by x1 + x2 = 50, x1 + 2x2 = 80, x1 + 5x2 = 185; arrows show the simplex path (0,0) to (0,37) "
            "to (10,35) to (20,30); dashed level line z = 650.")
    save("ornek5-yol", figure(W, H, [p], cap, aria=aria))


# ============================================================
# diyet-primal: min z = 2x1 + 3x2, x1 + x2 >= 4, x1 + 3x2 >= 6
# ============================================================
def diet_primal():
    p = panel(64, 30, 50, (0, 9), (0, 6.6))
    base(p, (0, 2, 4, 6, 8), (2, 4, 6))
    hp = [(-1, -1, -4), (-1, -3, -6), (-1, 0, 0), (0, -1, 0)]
    p.polygon(region(p, hp), THEORY, 0.14)
    draw_line(p, 1, 1, 4, BASE)
    draw_line(p, 1, 3, 6, PRACTICE)
    p.label(2.15, 2.0, X1 + " + " + X2 + " = 4", 0, 0, BASE, 12.5)
    p.label(3.9, 0.82, X1 + " + 3" + X2 + " = 6", 0, 0, PRACTICE, 12.5)
    draw_line(p, 2, 3, 9, PRACTICE, 1.4, dash="7 5", opacity=0.95)
    draw_line(p, 2, 3, 15, TEXT, 1.3, dash="7 5", opacity=0.75)
    p.label(0.15, 3.1, "z = 9", 0, 0, PRACTICE, 12.5)
    p.label(0.1, 5.0, "z = 15", 8, -4, TEXT, 12.5)
    p.arrow((6.6, 3.4), (6.6 - 0.5 * 2, 3.4 - 0.5 * 3), TEXT, 1.8, 10)
    p.label(6.6, 3.4, MINUS + "c = (" + MINUS + "2, " + MINUS + "3)", 6, -4, TEXT, 12.5)
    verts = [((0, 4), "A(0, 4)", 9, -6, "start"),
             ((3, 1), "B(3, 1): z = 9", -8, 16, "end"),
             ((6, 0), "C(6, 0)", 9, -9, "start")]
    p.points([q for q, *_ in verts], TEXT, 4.0)
    p.points([(3, 1)], PRACTICE, 5.6)
    for (x, y), s, dx, dy, anc in verts:
        opt = (x, y) == (3, 1)
        p.label(x, y, s, dx, dy, PRACTICE if opt else TEXT, 13.5, anc, bold=opt)
    W, H = canvas(p)
    cap = ("Primal problem: min z = 2x₁ + 3x₂, x₁ + x₂ ≥ 4, x₁ + 3x₂ ≥ 6. Uygun bölge sınırsızdır; "
           "kesikli doğrular z = 15 ve z = 9 seviye doğrularıdır. Seviye doğrusu gradyanın tersi yönünde kaydırılınca "
           "bölgeye son olarak B(3, 1) köşesinde dokunur: min z = 9.")
    aria = ("Unbounded feasible region above x1 + x2 = 4 and x1 + 3x2 = 6 with vertices A(0,4), B(3,1), C(6,0); "
            "dashed level lines z = 15 and z = 9 through B; arrow of the negative gradient.")
    save("diyet-primal", figure(W, H, [p], cap, aria=aria))


# ============================================================
# diyet-dual: max g = 4y1 + 6y2, y1 + y2 <= 2, y1 + 3y2 <= 3
# ============================================================
def diet_dual():
    p = panel(64, 30, 150, (0, 3.3), (0, 2.25))
    base(p, (0, 0.5, 1, 1.5, 2, 2.5, 3), (0.5, 1, 1.5, 2), Y1, Y2)
    hp = [(1, 1, 2), (1, 3, 3), (-1, 0, 0), (0, -1, 0)]
    p.polygon(region(p, hp), THEORY, 0.14)
    draw_line(p, 1, 1, 2, BASE)
    draw_line(p, 1, 3, 3, PRACTICE)
    p.label(0.12, 2.05, Y1 + " + " + Y2 + " = 2", 8, 4, BASE, 12.5)
    p.label(3.25, 0.12, Y1 + " + 3" + Y2 + " = 3", 0, -12, PRACTICE, 12.5, "end")
    draw_line(p, 4, 6, 6, TEXT, 1.3, dash="7 5", opacity=0.75)
    draw_line(p, 4, 6, 9, PRACTICE, 1.4, dash="7 5", opacity=0.95)
    p.label(0.3, 0.8, "g = 6", -8, 16, TEXT, 12.5, "end")
    p.label(0.15, 1.4, "g = 9", 8, -4, PRACTICE, 12.5)
    p.arrow((2.2, 1.0), (2.2 + 0.1 * 4, 1.0 + 0.1 * 6), TEXT, 1.8, 10)
    p.label(2.6, 1.6, "c = (4, 6)", 8, 2, TEXT, 12.5)
    verts = [((0, 0), "O", 8, -8, "start"),
             ((1.5, 0.5), "D(3/2, 1/2): g = 9", 10, -8, "start")]
    p.points([(0, 0), (2, 0), (0, 1)], TEXT, 4.0)
    p.points([(1.5, 0.5)], PRACTICE, 5.6)
    for (x, y), s, dx, dy, anc in verts:
        opt = (x, y) == (1.5, 0.5)
        p.label(x, y, s, dx, dy, PRACTICE if opt else TEXT, 13.5, anc, bold=opt)
    W, H = canvas(p)
    cap = ("Dual problem: max g = 4y₁ + 6y₂, y₁ + y₂ ≤ 2, y₁ + 3y₂ ≤ 3. Uygun bölge köşeleri O(0, 0), (2, 0), "
           "D(3/2, 1/2), (0, 1) olan dörtgendir; köşelerde g sırasıyla 0, 8, 9, 6 değerini alır. Seviye doğrusu gradyan yönünde kaydırılınca bölgeden en son "
           "D(3/2, 1/2) köşesinde ayrılır: max g = 9, primalin minimum değerine eşit.")
    aria = ("Feasible quadrilateral of the dual with vertices O, (2,0), D(1.5,0.5), (0,1) bounded by y1 + y2 = 2 and "
            "y1 + 3y2 = 3; dashed level lines g = 6 and g = 9, gradient arrow (4,6), optimal vertex D.")
    save("diyet-dual", figure(W, H, [p], cap, aria=aria))


if __name__ == "__main__":
    example5_path()
    diet_primal()
    diet_dual()
