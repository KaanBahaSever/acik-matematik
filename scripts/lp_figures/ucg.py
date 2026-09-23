# -*- coding: utf-8 -*-
"""
Figures of the chapter "Uç Noktalar ve Grafik Yöntem"
(dersler/lineer-programlama/uc-noktalar-ve-grafik-yontem.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution,
exercise or callout), never inside a definition box: a figure that
illustrates a definition sits directly below that box. The figures are NOT
produced at build time. Run

    python scripts/lp_figures/ucg.py
    python scripts/center_figures.py "lp-ucg-*.md" --keep-width
    python scripts/check_figure_labels.py "scripts/_figures/lp-ucg-*.md"

and paste the markup of scripts/_figures/lp-ucg-<name>.md into the .qmd.
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
PREFIX = "lp-ucg-"

MINUS = "&#8722;"
SUB = {"1": "&#8321;", "2": "&#8322;", "3": "&#8323;", "4": "&#8324;",
       "5": "&#8325;", "6": "&#8326;"}
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
# kose-tarama: vertices of x1 + 2x2 <= 8, 3x1 + 2x2 <= 12 with z = x1 + x2
# ============================================================
def vertex_scan():
    p = panel(130, 30, 54, (0, 9), (0, 7))
    base(p, (0, 2, 4, 6, 8), (2, 6))
    p.polygon(region(p, [(1, 2, 8), (3, 2, 12), (-1, 0, 0), (0, -1, 0)]), THEORY, 0.14)
    draw_line(p, 1, 2, 8, BASE)
    draw_line(p, 3, 2, 12, PRACTICE)
    p.label(7.0, 0.5, X1 + " + 2" + X2 + " = 8", 6, -16, BASE, 13)
    p.label(1.3, 4.05, "3" + X1 + " + 2" + X2 + " = 12", 10, -30, PRACTICE, 13)
    pts = [((0, 0), "O(0, 0): z = 0", 8, -8, "start"),
           ((4, 0), "A(4, 0): z = 4", 9, -9, "start"),
           ((2, 3), "B(2, 3): z = 5", 10, 2, "start"),
           ((0, 4), "C(0, 4)", -9, -2, "end")]
    p.points([q for q, *_ in pts], TEXT, 4.2)
    p.points([(2, 3)], PRACTICE, 5.5)
    for (x, y), s, dx, dy, anc in pts:
        col = PRACTICE if (x, y) == (2, 3) else TEXT
        p.label(x, y, s, dx, dy, col, 13.5, anc, bold=(x, y) == (2, 3))
    p.label(0, 4, "z = 4", -9, 14, TEXT, 13.5, "end")
    W, H = canvas(p)
    cap = ("x₁ + 2x₂ ≤ 8, 3x₁ + 2x₂ ≤ 12, x₁, x₂ ≥ 0 kısıtlarının uygun bölgesi OABC dörtgenidir. "
           "z = x₁ + x₂ amaç fonksiyonu dört uç noktada 0, 4, 5, 4 değerlerini alır; "
           "en büyük değer B(2, 3) noktasındadır.")
    aria = ("Feasible quadrilateral OABC of x1 + 2x2 at most 8 and 3x1 + 2x2 at most 12, "
            "vertices labelled with the values of z = x1 + x2; the largest value 5 is at B(2,3).")
    save("kose-tarama", figure(W, H, [p], cap, aria=aria))


# ============================================================
# coklu-optimum: z = 3x1 + 2x2 is maximal on the whole edge AB
# ============================================================
def multiple_optima():
    p = panel(64, 30, 54, (0, 9), (0, 7))
    base(p, (0, 2, 4, 6, 8), (2, 4, 6))
    p.polygon(region(p, [(1, 2, 8), (3, 2, 12), (-1, 0, 0), (0, -1, 0)]), THEORY, 0.14)
    draw_line(p, 1, 2, 8, BASE)
    draw_line(p, 3, 2, 12, PRACTICE, 1.4, dash="7 5", opacity=0.9)
    draw_line(p, 3, 2, 6, TEXT, 1.3, dash="7 5", opacity=0.7)
    p.line([(4, 0), (2, 3)], PRACTICE, 4.2)
    p.label(7.0, 0.5, X1 + " + 2" + X2 + " = 8", 6, -16, BASE, 13)
    p.label(0.4, 5.4, "z = 12", 10, -4, PRACTICE, 13)
    p.label(0.2, 2.7, "z = 6", 8, -6, TEXT, 13)
    # gradient c = (3, 2), drawn from a point of the edge, perpendicular to it
    p.arrow((3, 1.5), (3 + 0.45 * 3, 1.5 + 0.45 * 2), TEXT, 1.8, 10)
    p.label(3 + 0.45 * 3, 1.5 + 0.45 * 2, "c = (3, 2)", 8, 4, TEXT, 13)
    p.points([(4, 0), (2, 3)], PRACTICE, 5.2)
    p.points([(0, 0), (0, 4)], TEXT, 4.0)
    p.label(4, 0, "A(4, 0)", 10, -8, PRACTICE, 13.5)
    p.label(2, 3, "B(2, 3)", 8, -10, PRACTICE, 13.5)
    p.label(0, 4, "C", 9, -6, TEXT, 13.5)
    p.label(0, 0, "O", 8, -8, TEXT, 13.5)
    W, H = canvas(p)
    cap = ("Aynı bölgede z = 3x₁ + 2x₂. En büyük değer z = 12, A ve B uç noktalarında alınır; "
           "z = 12 seviye doğrusu AB kenarının üzerine oturduğu için kalın çizilen kenarın her noktası optimaldir. "
           "Ok gradyan yönünü, yani z'nin arttığı yönü gösterir.")
    aria = ("Same quadrilateral with objective 3x1 + 2x2; dashed level lines z = 6 and z = 12, "
            "the line z = 12 contains the edge AB, which is drawn thick; gradient arrow (3,2).")
    save("coklu-optimum", figure(W, H, [p], cap, aria=aria))


# ============================================================
# kaydirma: a non-extreme point P = (3, 3/2) and the points P +- t y
# ============================================================
def shifting():
    p = panel(64, 30, 54, (0, 9), (0, 7))
    base(p, (0, 2, 4, 6, 8), (2, 4, 6))
    p.polygon(region(p, [(1, 2, 8), (3, 2, 12), (-1, 0, 0), (0, -1, 0)]), THEORY, 0.14)
    draw_line(p, 1, 2, 8, BASE)
    draw_line(p, 3, 2, 12, PRACTICE)
    p.label(7.0, 0.5, X1 + " + 2" + X2 + " = 8", 6, -16, BASE, 13)
    p.label(0.4, 5.4, "3" + X1 + " + 2" + X2 + " = 12", 10, -4, PRACTICE, 13)
    p.line([(4, 0), (2, 3)], THEORY, 3.2, opacity=0.8)
    p.points([(0, 0), (4, 0), (2, 3), (0, 4)], TEXT, 4.0)
    p.label(4, 0, "A", 9, -7, TEXT, 13.5)
    p.label(2, 3, "B", 7, -9, TEXT, 13.5)
    p.label(0, 4, "C", 9, -6, TEXT, 13.5)
    p.label(0, 0, "O", 8, -8, TEXT, 13.5)
    p.points([(3.5, 0.75), (2.5, 2.25)], THEORY, 4.6)
    p.points([(3, 1.5)], PRACTICE, 5.2)
    p.label(3, 1.5, "P", 10, 5, PRACTICE, 14, bold=True)
    p.label(3.5, 0.75, "X" + SUB["1"], 10, 5, THEORY, 13.5)
    p.label(2.5, 2.25, "X" + SUB["2"], 10, 5, THEORY, 13.5)
    W, H = canvas(p)
    cap = ("P(3, 3/2) noktası AB kenarının ortasındadır ve uç nokta değildir. İspattaki kaydırma, t = 1/4 için "
           "P'yi X₁(7/2, 3/4) ile X₂(5/2, 9/4) noktalarının orta noktası olarak yazar; "
           "t = 1/2 alınınca X₁ ve X₂ tam A ve B uç noktalarına ulaşır.")
    aria = ("The point P(3, 1.5) in the middle of edge AB and the two feasible points X1(3.5, 0.75) "
            "and X2(2.5, 2.25) on the same edge whose midpoint is P.")
    save("kaydirma", figure(W, H, [p], cap, aria=aria))


# ============================================================
# temel-cozumler: all six basic solutions of the standard form
# ============================================================
def basic_solutions():
    p = panel(110, 30, 50, (0, 9.2), (0, 7))
    base(p, (0, 2, 4, 6, 8), (2, 6))
    p.polygon(region(p, [(1, 2, 8), (3, 2, 12), (-1, 0, 0), (0, -1, 0)]), THEORY, 0.14)
    draw_line(p, 1, 2, 8, BASE)
    draw_line(p, 3, 2, 12, PRACTICE)
    p.label(6.3, 0.85, "x" + SUB["3"] + " = 0", 4, -12, BASE, 13)
    p.label(0.6, 5.1, "x" + SUB["4"] + " = 0", 10, -4, PRACTICE, 13)
    feas = [((0, 0), "{x₃, x₄}", 8, -8, "start"),
            ((4, 0), "{x₁, x₃}", 9, -9, "start"),
            ((2, 3), "{x₁, x₂}", 9, -7, "start"),
            ((0, 4), "{x₂, x₄}", -9, 5, "end")]
    infeas = [((8, 0), "{x₁, x₄}", 0, -12, "middle"),
              ((0, 6), "{x₂, x₃}", 10, -4, "start")]
    p.points([q for q, *_ in feas], PRACTICE, 5.0)
    p.hollow_points([q for q, *_ in infeas], TEXT, 5.0)
    for (x, y), s, dx, dy, anc in feas:
        p.label(x, y, s, dx, dy, PRACTICE, 13, anc)
    for (x, y), s, dx, dy, anc in infeas:
        p.label(x, y, s, dx, dy, TEXT, 13, anc)
    W, H = canvas(p)
    cap = ("Standart formun altı baz adayı. Dolu noktalar uygun temel çözümlerdir ve tam olarak bölgenin "
           "dört köşesidir; içi boş noktalar (8, 0) ile (0, 6) uygun olmayan temel çözümlerdir. "
           "Her noktanın yanında baz değişkenleri yazılıdır; bir kısıt doğrusu üzerinde o kısıtın aylak değişkeni sıfırdır.")
    aria = ("The six basic solutions of the standard form drawn in the x1 x2 plane: four feasible ones at the "
            "vertices of the region (filled) and two infeasible ones at (8,0) and (0,6) (hollow), each labelled "
            "with its basic variables.")
    save("temel-cozumler", figure(W, H, [p], cap, aria=aria))


# ============================================================
# kaynak: the example with vertices A B C D E, max z = x1 + 2x2
# ============================================================
def source_example():
    p = panel(120, 30, 28, (0, 13), (0, 16))
    base(p, (0, 2, 6, 8, 10, 12), (2, 4, 6, 8, 12, 14, 16))
    hp = [(-1, -4, -4), (1, -1, 4), (1, 0, 6), (-1, 2, 20), (-1, 0, 0), (0, -1, 0)]
    p.polygon(region(p, hp), THEORY, 0.16)
    draw_line(p, 1, 4, 4, BASE)          # x1 + 4x2 = 4
    draw_line(p, -1, 1, -4, PRACTICE)    # -x1 + x2 = -4
    draw_line(p, 1, 0, 6, REMARK)        # x1 = 6
    draw_line(p, 1, -2, -20, THEORY)     # x1 - 2x2 = -20
    p.label(0, 0.55, X1 + " + 4" + X2 + " = 4", -10, 0, BASE, 12, "end")
    p.label(11.4, 8.3, MINUS + X1 + " + " + X2 + " = " + MINUS + "4", 0, 0, PRACTICE, 12.5, "end")
    p.label(6, 15.6, X1 + " = 6", 7, 4, REMARK, 12.5)
    p.label(12.5, 13.2, X1 + " " + MINUS + " 2" + X2 + " = " + MINUS + "20", 0, 0, THEORY, 12.5, "end")
    # level lines z = 20 (through B) and z = 32 (through A)
    draw_line(p, 1, 2, 20, TEXT, 1.3, dash="7 5", opacity=0.75)
    draw_line(p, 1, 2, 32, PRACTICE, 1.4, dash="7 5", opacity=0.95)
    p.label(12.9, 3.55, "z = 20", 0, 16, TEXT, 12.5, "end")
    p.label(8.2, 10.6, "z = 32", 0, 0, PRACTICE, 12.5)
    # gradient c = (1, 2)
    p.arrow((1.5, 4.25), (1.5 + 1.6, 4.25 + 3.2), TEXT, 1.8, 10)
    p.label(1.5 + 1.6, 4.25 + 3.2, "c = (1, 2)", 7, 12, TEXT, 12.5)
    verts = [((6, 13), "A(6, 13)", 28, 6, "start"),
             ((0, 10), "B(0, 10)", -9, 5, "end"),
             ((0, 1), "C(0, 1)", 9, -8, "start"),
             ((4, 0), "D(4, 0)", 0, 17, "middle"),
             ((6, 2), "E(6, 2)", 9, 17, "start")]
    p.points([q for q, *_ in verts], TEXT, 4.0)
    p.points([(6, 13)], PRACTICE, 5.6)
    for (x, y), s, dx, dy, anc in verts:
        opt = (x, y) == (6, 13)
        p.label(x, y, s, dx, dy, PRACTICE if opt else TEXT, 13.5, anc, bold=opt)
    W, H = canvas(p, 40, 44)
    cap = ("Uygun bölge ABCDE beşgenidir. Kesikli doğrular z = x₁ + 2x₂ amaç fonksiyonunun z = 20 ve z = 32 "
           "seviye doğrularıdır; ok gradyan yönünü gösterir. Seviye doğrusu gradyan yönünde kaydırıldığında "
           "bölgeden en son A(6, 13) köşesinde ayrılır: max z = 32.")
    aria = ("Feasible pentagon ABCDE bounded by x1 + 4x2 = 4, -x1 + x2 = -4, x1 = 6, x1 - 2x2 = -20 and the axes; "
            "dashed level lines of z = x1 + 2x2 for z = 20 and z = 32, gradient arrow (1,2), optimal vertex A(6,13).")
    save("kaynak", figure(W, H, [p], cap, aria=aria))


# ============================================================
# uretim: production example, max z = 30x1 + 20x2
# ============================================================
def production():
    p = panel(110, 30, 4.3, (0, 100), (0, 108))
    base(p, (0, 20, 40, 60, 80), (20, 40, 60, 100))
    hp = [(2, 1, 100), (1, 1, 80), (1, 0, 40), (-1, 0, 0), (0, -1, 0)]
    p.polygon(region(p, hp), THEORY, 0.14)
    draw_line(p, 2, 1, 100, BASE)
    draw_line(p, 1, 1, 80, PRACTICE)
    draw_line(p, 1, 0, 40, REMARK)
    p.label(4, 92, "2" + X1 + " + " + X2 + " = 100", 10, -2, BASE, 12.5)
    p.label(63, 19, X1 + " + " + X2 + " = 80", 0, 0, PRACTICE, 12.5)
    p.label(40, 104, X1 + " = 40", 7, 4, REMARK, 12.5)
    draw_line(p, 30, 20, 1200, TEXT, 1.3, dash="7 5", opacity=0.75)
    draw_line(p, 30, 20, 1800, PRACTICE, 1.4, dash="7 5", opacity=0.95)
    p.label(28, 18, "z = 1200", -6, 6, TEXT, 12.5, "end")
    p.label(60, 0, "z = 1800", 6, -8, PRACTICE, 12.5)
    p.arrow((55, 55), (55 + 0.55 * 30, 55 + 0.55 * 20), TEXT, 1.8, 10)
    p.label(55 + 0.55 * 30, 55 + 0.55 * 20, "c = (30, 20)", 8, 4, TEXT, 12.5)
    verts = [((0, 0), "O", 8, -8, "start"),
             ((40, 0), "A(40, 0)", 8, -8, "start"),
             ((40, 20), "B(40, 20)", 9, 4, "start"),
             ((20, 60), "C(20, 60)", 9, -4, "start"),
             ((0, 80), "D(0, 80)", -9, 5, "end")]
    p.points([q for q, *_ in verts], TEXT, 4.0)
    p.points([(20, 60)], PRACTICE, 5.6)
    for (x, y), s, dx, dy, anc in verts:
        opt = (x, y) == (20, 60)
        p.label(x, y, s, dx, dy, PRACTICE if opt else TEXT, 13.5, anc, bold=opt)
    W, H = canvas(p)
    cap = ("Üretim modelinin uygun bölgesi OABCD. z = 30x₁ + 20x₂ seviye doğruları gradyan yönünde "
           "kaydırıldığında bölgeden en son C(20, 60) köşesinde ayrılır: 20 masa ve 60 sandalye ile max z = 1800 TL.")
    aria = ("Feasible pentagon OABCD of the production model with constraint lines 2x1 + x2 = 100, x1 + x2 = 80, "
            "x1 = 40; dashed level lines z = 1200 and z = 1800, gradient arrow (30,20), optimal vertex C(20,60).")
    save("uretim", figure(W, H, [p], cap, aria=aria))


# ============================================================
# diyet: min z = 2x1 + 3x2 on an unbounded region
# ============================================================
def diet_min():
    p = panel(64, 30, 50, (0, 9), (0, 7))
    base(p, (0, 2, 4, 8), (2, 4, 6))
    hp = [(-1, -1, -4), (-1, -3, -6), (-1, 0, 0), (0, -1, 0)]
    p.polygon(region(p, hp), THEORY, 0.14)
    draw_line(p, 1, 1, 4, BASE)
    draw_line(p, 1, 3, 6, PRACTICE)
    p.label(1.25, 3.05, X1 + " + " + X2 + " = 4", 0, 0, BASE, 12.5)
    p.label(4.3, 0.75, X1 + " + 3" + X2 + " = 6", 0, 0, PRACTICE, 12.5)
    draw_line(p, 2, 3, 9, PRACTICE, 1.4, dash="7 5", opacity=0.95)
    draw_line(p, 2, 3, 18, TEXT, 1.3, dash="7 5", opacity=0.75)
    p.label(0.15, 3.1, "z = 9", 0, 0, PRACTICE, 12.5)
    p.label(8.4, 0.4, "z = 18", 0, -30, TEXT, 12.5, "middle")
    # improvement direction for a minimum: -c = -(2, 3)
    p.arrow((6.6, 3.4), (6.6 - 0.5 * 2, 3.4 - 0.5 * 3), TEXT, 1.8, 10)
    p.label(6.6, 3.4, MINUS + "c = (" + MINUS + "2, " + MINUS + "3)", 6, -4, TEXT, 12.5)
    verts = [((0, 4), "A(0, 4): z = 12", 9, -6, "start"),
             ((3, 1), "B(3, 1): z = 9", -8, 16, "end"),
             ((6, 0), "C(6, 0): z = 12", 0, 17, "middle")]
    p.points([q for q, *_ in verts], TEXT, 4.0)
    p.points([(3, 1)], PRACTICE, 5.6)
    for (x, y), s, dx, dy, anc in verts:
        opt = (x, y) == (3, 1)
        p.label(x, y, s, dx, dy, PRACTICE if opt else TEXT, 13.5, anc, bold=opt)
    W, H = canvas(p)
    cap = ("Uygun bölge sağa ve yukarı doğru sınırsızdır. Minimum problemi olduğu için z = 2x₁ + 3x₂ seviye "
           "doğrusu gradyanın tersi yönünde kaydırılır; bölgeye son dokunduğu nokta B(3, 1) köşesidir: min z = 9.")
    aria = ("Unbounded feasible region above the lines x1 + x2 = 4 and x1 + 3x2 = 6 with vertices A(0,4), B(3,1), "
            "C(6,0); dashed level lines z = 18 and z = 9 of z = 2x1 + 3x2, arrow of the negative gradient, "
            "optimal vertex B(3,1).")
    save("diyet", figure(W, H, [p], cap, aria=aria))


# ============================================================
# karisim: the feasible set is a segment on x1 + x2 = 100
# ============================================================
def mixture():
    p = panel(64, 30, 3.9, (0, 110), (0, 110))
    base(p, (0, 20, 40, 60, 80, 100), (20, 40, 60, 80, 100))
    # half-planes x1 + 5x2 >= 300 and x1 + 3x2 <= 250, lightly shaded
    both = region(p, [(-1, -5, -300), (1, 3, 250), (-1, 0, 0), (0, -1, 0)])
    p.polygon(both, THEORY, 0.10)
    draw_line(p, 1, 1, 100, BASE)
    draw_line(p, 1, 5, 300, PRACTICE)
    draw_line(p, 1, 3, 250, REMARK)
    p.label(96, 4, X1 + " + " + X2 + " = 100", -4, -14, BASE, 12.5, "end")
    p.label(3, 51, X1 + " + 5" + X2 + " = 300", 0, 0, PRACTICE, 12.5)
    p.label(108, 44.5, X1 + " + 3" + X2 + " = 250", 0, 0, REMARK, 12.5, "end")
    p.line([(25, 75), (50, 50)], THEORY, 5.0)
    draw_line(p, 4, 10, 700, PRACTICE, 1.4, dash="7 5", opacity=0.95)
    draw_line(p, 4, 10, 1000, TEXT, 1.3, dash="7 5", opacity=0.75)
    p.label(2, 71.2, "z = 700", 0, 0, PRACTICE, 12.5)
    p.label(108, 63.5, "z = 1000", 0, 0, TEXT, 12.5, "end")
    p.arrow((92, 96), (92 - 0.9 * 4, 96 - 0.9 * 10), TEXT, 1.8, 10)
    p.label(92, 96, MINUS + "c", 8, 4, TEXT, 12.5)
    p.points([(25, 75)], TEXT, 4.2)
    p.points([(50, 50)], PRACTICE, 5.6)
    p.label(25, 75, "P(25, 75)", 10, -8, TEXT, 13.5)
    p.label(50, 50, "Q(50, 50)", -10, 16, PRACTICE, 13.5, "end", bold=True)
    W, H = canvas(p)
    cap = ("Karışım probleminde eşitlik kısıtı yüzünden uygun çözümler x₁ + x₂ = 100 doğrusunun kalın çizilen "
           "PQ parçasıdır; açık boyalı bant iki eşitsizliğin ortak bölgesidir. Uç noktalar P ve Q'dur. "
           "z = 4x₁ + 10x₂ seviye doğrusu gradyanın tersi yönünde kaydırıldığında parçadan en son Q(50, 50) "
           "noktasında ayrılır: min z = 700.")
    aria = ("Mixture problem: the feasible set is the segment PQ on the line x1 + x2 = 100 between P(25,75) "
            "and Q(50,50), cut out by x1 + 5x2 at least 300 and x1 + 3x2 at most 250; dashed level lines "
            "z = 1000 and z = 700, optimal endpoint Q.")
    save("karisim", figure(W, H, [p], cap, aria=aria))


# ============================================================
# bos: no feasible solution
# ============================================================
def infeasible():
    p = panel(64, 30, 50, (0, 8), (0, 7))
    base(p, (0, 2, 4, 6), (2, 4, 6))
    p.polygon(region(p, [(1, 1, 2), (-1, 0, 0), (0, -1, 0)]), BASE, 0.16)
    p.polygon(region(p, [(-1, -2, -6), (-1, 0, 0), (0, -1, 0)]), PRACTICE, 0.13)
    draw_line(p, 1, 1, 2, BASE)
    draw_line(p, 1, 2, 6, PRACTICE)
    p.label(4.4, 5.2, X1 + " + 2" + X2 + " " + GEQ + " 6", 0, 0, PRACTICE, 12.5)
    p.label(2.35, 0.3, X1 + " + " + X2 + " " + LEQ + " 2", 0, 0, BASE, 12.5)
    p.arrow((2.25, 0.42), (0.95, 0.45), BASE, 1.3, 8, opacity=0.85)
    W, H = canvas(p)
    cap = ("x₁ + x₂ ≤ 2 kısıtının bölgesi (alttaki üçgen) ile x₁ + 2x₂ ≥ 6 kısıtının bölgesi birinci bölgede ortak "
           "nokta içermez. Uygun çözüm yoktur; bu yüzden optimal çözüm de yoktur.")
    aria = ("Triangle x1 + x2 at most 2 in the first quadrant and the region above x1 + 2x2 = 6; "
            "the two shaded regions do not meet, so there is no feasible solution.")
    save("bos", figure(W, H, [p], cap, aria=aria))


# ============================================================
# sinirsiz: unbounded objective
# ============================================================
def unbounded():
    p = panel(64, 30, 46, (0, 10), (0, 7.5))
    base(p, (0, 4, 6, 8), (2, 4, 6))
    hp = [(-1, 1, 1), (1, -2, 2), (-1, 0, 0), (0, -1, 0)]
    p.polygon(region(p, hp), THEORY, 0.14)
    draw_line(p, -1, 1, 1, BASE)
    draw_line(p, 1, -2, 2, PRACTICE)
    p.label(5.2, 6.2, MINUS + X1 + " + " + X2 + " = 1", -8, -4, BASE, 12.5, "end")
    p.label(5.1, 0.85, X1 + " " + MINUS + " 2" + X2 + " = 2", 0, 0, PRACTICE, 12.5)
    for k in (4, 8, 12):
        draw_line(p, 1, 1, k, TEXT, 1.3, dash="7 5", opacity=0.75)
    p.label(4, 0, "z = 4", 6, -8, TEXT, 12.5)
    p.label(8, 0, "z = 8", 6, -8, TEXT, 12.5)
    p.label(10, 2, "z = 12", 6, 4, TEXT, 12.5)
    p.arrow((5.5, 2.3), (5.5 + 1.2, 2.3 + 1.2), TEXT, 1.8, 10)
    p.label(6.7, 3.5, "c = (1, 1)", 8, 4, TEXT, 12.5)
    p.points([(0, 0), (0, 1), (2, 0)], TEXT, 4.0)
    p.label(0, 1, "(0, 1)", -9, 5, TEXT, 13, "end")
    p.label(2, 0, "(2, 0)", 0, 18, TEXT, 13, "middle")
    W, H = canvas(p)
    cap = ("Uygun bölge sağ yukarı doğru sınırsızdır ve z = x₁ + x₂ seviye doğruları gradyan yönünde ne kadar "
           "kaydırılırsa kaydırılsın bölgeyi kesmeye devam eder. z istenildiği kadar büyür; maksimum yoktur.")
    aria = ("Unbounded feasible region between the lines -x1 + x2 = 1 and x1 - 2x2 = 2 in the first quadrant; "
            "dashed level lines z = 4, 8, 12 of z = x1 + x2 all meet the region.")
    save("sinirsiz", figure(W, H, [p], cap, aria=aria))


# ============================================================
# alternatif: infinitely many optimal solutions
# ============================================================
def alternative():
    p = panel(64, 30, 46, (0, 11), (0, 7))
    base(p, (0, 2, 4, 6, 8, 10), (2, 4, 6))
    hp = [(1, 2, 10), (1, 0, 6), (-1, 0, 0), (0, -1, 0)]
    p.polygon(region(p, hp), THEORY, 0.14)
    draw_line(p, 1, 2, 10, BASE)
    draw_line(p, 1, 0, 6, REMARK)
    p.line([(6, 2), (0, 5)], PRACTICE, 4.4)
    draw_line(p, 1, 2, 6, TEXT, 1.3, dash="7 5", opacity=0.75)
    p.label(9.2, 0.4, X1 + " + 2" + X2 + " = 10", 4, -14, BASE, 12.5)
    p.label(6, 6.8, X1 + " = 6", 7, 4, REMARK, 12.5)
    p.label(0, 3, "z = 6", -9, 5, TEXT, 12.5, "end")
    p.label(3, 3.5, "z = 10", 0, -12, PRACTICE, 12.5, "middle")
    p.arrow((2.6, 1.7), (2.6 + 0.8, 1.7 + 1.6), TEXT, 1.8, 10)
    p.label(3.1, 2.5, "c = (1, 2)", 8, 4, TEXT, 12.5)
    p.points([(0, 0), (6, 0)], TEXT, 4.0)
    p.points([(6, 2), (0, 5)], PRACTICE, 5.4)
    p.label(6, 2, "B(6, 2)", 9, 5, PRACTICE, 13.5, bold=True)
    p.label(0, 5, "C(0, 5)", 9, -8, PRACTICE, 13.5, bold=True)
    p.label(6, 0, "A(6, 0)", 8, -8, TEXT, 13.5)
    W, H = canvas(p)
    cap = ("Amaç doğrusu z = x₁ + 2x₂, x₁ + 2x₂ = 10 kısıtına paraleldir. Seviye doğrusu kaydırıldığında "
           "bölgeden bir köşede değil, BC kenarının tamamı boyunca ayrılır; BC üzerindeki her nokta max z = 10 veren "
           "bir optimal çözümdür.")
    aria = ("Feasible quadrilateral with vertices O, A(6,0), B(6,2), C(0,5); the objective x1 + 2x2 is parallel "
            "to the edge BC, which is drawn thick; dashed level line z = 6 and gradient arrow (1,2).")
    save("alternatif", figure(W, H, [p], cap, aria=aria))


if __name__ == "__main__":
    vertex_scan()
    multiple_optima()
    shifting()
    basic_solutions()
    source_example()
    production()
    diet_min()
    mixture()
    infeasible()
    unbounded()
    alternative()
