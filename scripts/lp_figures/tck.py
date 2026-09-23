# -*- coding: utf-8 -*-
"""
Figures of the chapter "Temel Çözümler ve Konveks Kümeler"
(dersler/lineer-programlama/temel-cozumler-ve-konveks-kumeler.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution,
exercise or callout), never inside a definition box: a figure that
illustrates a definition sits directly below that box. The figures are NOT
produced at build time. Run

    python scripts/lp_figures/tck.py
    python scripts/center_figures.py "lp-tck-*.md" --keep-width
    python scripts/check_figure_labels.py "scripts/_figures/lp-tck-*.md"

and paste the markup of scripts/_figures/lp-tck-<name>.md into the .qmd.
The captions are Turkish on purpose (they are shown on the site); the aria
labels are plain ASCII.
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, panel_title, WIDE, TEXT, THEORY, PRACTICE, BASE, REMARK  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "lp-tck-"

MINUS = "&#8722;"
SUB = {"1": "&#8321;", "2": "&#8322;", "3": "&#8323;", "4": "&#8324;", "5": "&#8325;", "6": "&#8326;"}


def x(i):
    """x with a Unicode subscript digit."""
    return "x" + SUB[str(i)]


def X(i):
    """Point name X with a Unicode subscript digit."""
    return "X" + SUB[str(i)]


def save(name, markup):
    path = OUT_DIR / f"{PREFIX}{name}.md"
    path.write_text(markup, encoding="utf-8", newline="\n")
    print("wrote", path.name)


def ellipse_pts(cx, cy, rx, ry, samples=120):
    return [(cx + rx * math.cos(2 * math.pi * k / samples), cy + ry * math.sin(2 * math.pi * k / samples))
            for k in range(samples + 1)]


def is_convex(poly):
    """True when the polygon (counter-clockwise) turns left at every vertex."""
    n = len(poly)
    for i in range(n):
        (ax, ay), (bx, by), (cx, cy) = poly[i], poly[(i + 1) % n], poly[(i + 2) % n]
        if (bx - ax) * (cy - by) - (by - ay) * (cx - bx) <= 0:
            return False
    return True


# ============================================================
# ek-ornek: x1 + x2 <= 4, x1 + 3x2 <= 6; six basic solutions
# ============================================================
def extra_example():
    W, H = 560, 440
    p = Plot(58, 30, 440, 340, (0, 6.8), (0, 4.6))
    p.grid(xs=(1, 2, 3, 4, 5, 6), ys=(1, 2, 3, 4))
    p.axes((0, 1, 2, 3, 4, 5, 6), (1, 2, 3, 4), x(1), x(2))
    p.polygon([(0, 0), (4, 0), (3, 1), (0, 2)], THEORY, 0.16)
    p.line([(0, 4), (4, 0)], BASE, 2.0)          # x1 + x2 = 4
    p.line([(0, 2), (6, 0)], PRACTICE, 2.0)      # x1 + 3x2 = 6
    # level line of z = 2x1 + 3x2 through the optimum
    p.line([(0, 3), (4.5, 0)], REMARK, 1.5, dash="6 5")
    p.arrow((3, 1), (3.45, 1.675), REMARK, 1.6, 8)
    # line labels
    p.label(1.15, 2.85, x(1) + " + " + x(2) + " = 4  (" + x(3) + " = 0)", 8, -4, BASE, 13)
    p.label(4.7, 0.43, x(1) + " + 3" + x(2) + " = 6  (" + x(4) + " = 0)", 6, -10, PRACTICE, 13)
    p.label(0.62, 2.62, "z = 9", -2, 14, REMARK, 12.5, "end")
    # feasible basic solutions (vertices)
    p.points([(0, 0), (4, 0), (3, 1), (0, 2)], PRACTICE, 4.8)
    p.label(0, 0, "O", 7, -8, TEXT, 13.5)
    p.label(4, 0, "A", 4, -9, TEXT, 13.5)
    p.label(3, 1, "B", 6, -9, TEXT, 13.5, bold=True)
    p.label(0, 2, "C", 8, 16, TEXT, 13.5)
    # infeasible basic solutions
    p.hollow_points([(0, 4), (6, 0)], REMARK, 5.0)
    p.label(0, 4, "D", 9, 5, REMARK, 13.5)
    p.label(6, 0, "E", 0, -11, REMARK, 13.5, "middle")

    cap = ("Uygun bölge boyalı dörtgendir. Her kısıt doğrusu üzerinde bir değişken sıfırdır "
           "(eksenlerde x₁ = 0 ya da x₂ = 0); iki doğrunun her kesişimi, o iki değişken sıfırlanarak "
           "bulunan bir temel çözümdür. Dolu noktalar O, A, B, C uygun temel çözümlerdir ve bölgenin "
           "köşeleridir; boş noktalar D(0, 4) ve E(6, 0) uygun olmayan temel çözümlerdir ve bölgenin "
           "dışında kalır. Kesikli z = 9 doğrusu bölgeye yalnız B(3, 1) köşesinde değer.")
    aria = ("Feasible quadrilateral O(0,0), A(4,0), B(3,1), C(0,2) bounded by x1 + x2 = 4 and x1 + 3x2 = 6; "
            "infeasible basic solutions D(0,4) and E(6,0) outside; dashed level line z = 9 touches at B.")
    save("ek-ornek", figure(W, H, [p], cap, aria=aria))


# ============================================================
# konveks: convex and non-convex sets
# ============================================================
def convex_sets():
    W, H = 720, 260
    PW, PH = 200, 190
    xr = (0, 4)
    yr = (0, 4 * PH / PW)
    ps = [Plot(20 + k * 240, 44, PW, PH, xr, yr) for k in range(3)]

    # (a) convex polygon
    a = ps[0]
    poly = [(0.4, 0.5), (3.1, 0.3), (3.7, 1.9), (2.4, 3.4), (0.6, 2.9)]
    assert is_convex(poly)
    a.polygon(poly, THEORY, 0.16, stroke=THEORY, width=2.0)
    a.line([(1.0, 1.0), (3.0, 2.4)], PRACTICE, 2.0)
    a.points([(1.0, 1.0), (3.0, 2.4)], PRACTICE, 4.2)
    a.label(1.0, 1.0, "U", -8, 4, PRACTICE, 13, "end")
    a.label(3.0, 2.4, "V", 8, -4, PRACTICE, 13)
    panel_title(a, "konveks", TEXT, 13)

    # (b) ellipse
    b = ps[1]
    ell = ellipse_pts(2.0, 1.9, 1.8, 1.2)
    b.polygon(ell, THEORY, 0.16, stroke=THEORY, width=2.0)
    b.line([(0.9, 1.3), (3.0, 2.6)], PRACTICE, 2.0)
    b.points([(0.9, 1.3), (3.0, 2.6)], PRACTICE, 4.2)
    b.label(0.9, 1.3, "U", -8, 4, PRACTICE, 13, "end")
    b.label(3.0, 2.6, "V", 8, -4, PRACTICE, 13)
    panel_title(b, "konveks", TEXT, 13)

    # (c) non-convex: a crescent-like region (L shape)
    c = ps[2]
    lsh = [(0.4, 0.3), (3.6, 0.3), (3.6, 1.3), (1.5, 1.3), (1.5, 3.4), (0.4, 3.4)]
    c.polygon(lsh, THEORY, 0.16, stroke=THEORY, width=2.0)
    u, v = (0.95, 3.0), (3.2, 0.8)
    c.line([u, v], PRACTICE, 2.0, dash="6 4")
    c.points([u, v], PRACTICE, 4.2)
    c.label(*u, "U", 8, -4, PRACTICE, 13)
    c.label(*v, "V", 0, -10, PRACTICE, 13, "middle")
    c.label(2.55, 2.3, "kümenin dışı", 0, 0, REMARK, 12.5, "middle")
    panel_title(c, "konveks değil", TEXT, 13)

    cap = ("Soldaki çokgen ve ortadaki elips konvekstir: içlerinden hangi iki nokta alınırsa alınsın, "
           "UV doğru parçası kümenin içinde kalır. Sağdaki L biçimli küme konveks değildir: U ve V "
           "kümededir ama UV doğru parçasının bir kısmı kümenin dışından geçer.")
    aria = ("Three panels: a convex polygon and an ellipse, each containing the segment UV; "
            "an L-shaped non-convex set whose segment UV leaves the set.")
    save("konveks", figure(W, H, ps, cap, WIDE, aria=aria))


# ============================================================
# kesisim: intersection of two discs is convex, union is not
# ============================================================
def lens(c1, c2, r, samples=60):
    """Boundary of the intersection of two equal discs with centers on the x axis."""
    d = (c2 - c1) / 2
    h = math.sqrt(r * r - d * d)
    th = math.atan2(h, d)
    right = [(c1 + r * math.cos(-th + 2 * th * k / samples), r * math.sin(-th + 2 * th * k / samples))
             for k in range(samples + 1)]
    left = [(c2 + r * math.cos(math.pi - th + 2 * th * k / samples),
             r * math.sin(math.pi - th + 2 * th * k / samples)) for k in range(samples + 1)]
    return right + left


def union_boundary(c1, c2, r, samples=90):
    d = (c2 - c1) / 2
    h = math.sqrt(r * r - d * d)
    th = math.atan2(h, d)
    # outer arc of disc 2 (from its upper intersection point clockwise around the right side)
    a2 = [(c2 + r * math.cos(math.pi - th - (2 * math.pi - 2 * th) * k / samples),
           r * math.sin(math.pi - th - (2 * math.pi - 2 * th) * k / samples)) for k in range(samples + 1)]
    a1 = [(c1 + r * math.cos(-th - (2 * math.pi - 2 * th) * k / samples),
           r * math.sin(-th - (2 * math.pi - 2 * th) * k / samples)) for k in range(samples + 1)]
    return a2 + a1


def intersection_union():
    W, H = 720, 280
    PW, PH = 300, 200
    xr = (-2.7, 2.7)
    yr = (-2.7 * PH / PW, 2.7 * PH / PW)
    left = Plot(30, 50, PW, PH, xr, yr)
    right = Plot(390, 50, PW, PH, xr, yr)
    c1, c2, r = -0.9, 0.9, 1.4

    for p in (left, right):
        p.circle(c1, 0, r, THEORY, 1.6)
        p.circle(c2, 0, r, BASE, 1.6)
        p.label(c1 - 1.1, -1.08, "C" + SUB["1"], -6, 6, THEORY, 13, "end")
        p.label(c2 + 1.1, -1.08, "C" + SUB["2"], 6, 6, BASE, 13)

    left.polygon(lens(c1, c2, r), PRACTICE, 0.30)
    left.label(0, -0.15, "C" + SUB["1"] + " ∩ C" + SUB["2"], 0, 0, PRACTICE, 12.5, "middle")
    panel_title(left, "kesişim konveks", TEXT, 13)

    right.polygon(union_boundary(c1, c2, r), PRACTICE, 0.16)
    u, v = (-0.9, 1.2), (0.9, 1.2)
    right.line([u, v], REMARK, 2.0, dash="6 4")
    right.points([u, v], REMARK, 4.2)
    right.label(*u, "U", 0, 20, REMARK, 13, "middle")
    right.label(*v, "V", 0, 20, REMARK, 13, "middle")
    panel_title(right, "birleşim konveks değil", TEXT, 13)

    cap = ("İki dairesel bölge konvekstir. Solda kesişimleri (koyu boyalı mercek) yine konvekstir. "
           "Sağda birleşimleri konveks değildir: U birinci, V ikinci bölgededir, ama UV doğru "
           "parçasının ortası iki bölgenin de dışında kalır.")
    aria = ("Two overlapping discs C1 and C2. Left: their intersection, a convex lens. "
            "Right: their union with a segment UV whose middle lies outside the union.")
    save("kesisim", figure(W, H, [left, right], cap, WIDE, aria=aria))


# ============================================================
# uc-nokta: extreme points of a polygon and of an ellipse
# ============================================================
def extreme_points():
    W, H = 720, 280
    PW, PH = 300, 210
    xr = (0, 4.4)
    yr = (0, 4.4 * PH / PW)
    left = Plot(30, 46, PW, PH, xr, yr)
    right = Plot(390, 46, PW, PH, xr, yr)

    poly = [(0.5, 0.4), (3.5, 0.4), (4.0, 1.9), (2.2, 2.9), (0.3, 2.1)]
    assert is_convex(poly)
    left.polygon(poly, THEORY, 0.14, stroke=THEORY, width=2.0)
    left.points(poly, PRACTICE, 5.0)
    # a non-extreme point on an edge
    e0, e1 = (3.5, 0.4), (4.0, 1.9)
    pe = (3.75, 1.15)
    left.line([(3.61, 0.73), (3.89, 1.57)], REMARK, 3.2)
    left.hollow_points([pe], REMARK, 4.6)
    left.label(*pe, "P", -8, 5, REMARK, 13, "end")
    # a non-extreme interior point
    q = (1.8, 1.5)
    left.line([(1.2, 1.1), (2.4, 1.9)], REMARK, 2.2)
    left.hollow_points([q], REMARK, 4.6)
    left.label(*q, "Q", 0, 18, REMARK, 13, "middle")
    left.label(0.5, 0.4, "uç nokta", 0, 20, PRACTICE, 12.5, "middle")
    panel_title(left, "çokgen: 5 uç nokta", TEXT, 13)

    ell = ellipse_pts(2.2, 1.5, 1.8, 1.05)
    right.polygon(ell, THEORY, 0.14, stroke="none")
    right.line(ell, PRACTICE, 3.2)
    right.hollow_points([(2.2, 1.5)], REMARK, 4.6)
    right.line([(1.6, 1.5), (2.8, 1.5)], REMARK, 2.2)
    right.label(2.2, 1.5, "Q", 0, 18, REMARK, 13, "middle")
    right.label(2.2, 2.55, "sınırın her noktası uç nokta", 0, -12, PRACTICE, 12.5, "middle")
    panel_title(right, "elips: sonsuz sayıda uç nokta", TEXT, 13)

    cap = ("Solda çokgenin uç noktaları beş köşesidir. Bir kenarın ortasındaki P noktası uç nokta "
           "değildir: o kenar üzerinde P'nin iki yanındaki iki noktanın konveks kombinasyonudur. "
           "İçteki Q noktası da kendisinden geçen kısa bir doğru parçasının ortasıdır. Sağda elipsin "
           "sınırındaki her nokta uç noktadır; içteki noktalar değildir.")
    aria = ("Left: convex pentagon with its five vertices marked as extreme points, an edge point P and "
            "an interior point Q that are midpoints of short segments. Right: ellipse whose whole boundary "
            "consists of extreme points.")
    save("uc-nokta", figure(W, H, [left, right], cap, WIDE, aria=aria))


# ============================================================
# uc-kombinasyon: a point of a convex polygon as a convex
# combination of vertices (boundary point, interior point)
# ============================================================
def vertex_combination():
    W, H = 720, 300
    PW, PH = 300, 230
    xr = (-0.5, 4.9)
    yr = (-0.3, -0.3 + 5.4 * PH / PW)
    left = Plot(30, 40, PW, PH, xr, yr)
    right = Plot(390, 40, PW, PH, xr, yr)
    V = [(1.0, 0.0), (4.0, 0.3), (4.4, 2.2), (3.0, 3.6), (0.9, 3.2), (0.0, 1.6)]
    assert is_convex(V)
    offs = [(-4, 18, "end"), (6, 16, "start"), (9, 4, "start"), (4, -10, "start"),
            (-6, -10, "end"), (-9, 4, "end")]
    for p in (left, right):
        p.polygon(V, THEORY, 0.14, stroke=THEORY, width=2.0)
        p.points(V, PRACTICE, 4.4)
        for i, ((vx, vy), (dx, dy, anc)) in enumerate(zip(V, offs)):
            p.label(vx, vy, X(i + 1), dx, dy, PRACTICE, 13, anc)

    # boundary point on X6X1
    a = (0.5 * V[5][0] + 0.5 * V[0][0], 0.5 * V[5][1] + 0.5 * V[0][1])
    left.line([V[5], V[0]], REMARK, 3.0)
    left.points([a], TEXT, 4.4)
    left.label(*a, "A", 10, 4, TEXT, 13.5)
    panel_title(left, "sınırdaki nokta", TEXT, 13)

    # interior point on X6B, B on X2X3
    b = (0.5 * V[1][0] + 0.5 * V[2][0], 0.5 * V[1][1] + 0.5 * V[2][1])
    lam = 0.45
    a2 = (lam * V[5][0] + (1 - lam) * b[0], lam * V[5][1] + (1 - lam) * b[1])
    right.line([V[1], V[2]], REMARK, 3.0)
    right.line([V[5], b], TEXT, 1.6, dash="6 4")
    right.points([a2, b], TEXT, 4.4)
    right.label(*a2, "A", 0, -10, TEXT, 13.5, "middle")
    right.label(*b, "B", 10, 5, TEXT, 13.5)
    panel_title(right, "içteki nokta", TEXT, 13)

    cap = ("Konveks çokgenin bir noktasını uç noktaların konveks kombinasyonu olarak yazmak. Solda A "
           "sınırdadır ve X₆X₁ kenarı üzerinde olduğu için X₆ ile X₁'in konveks kombinasyonudur. Sağda "
           "A içtedir: X₆'dan A'ya giden ışın sınırı X₂X₃ kenarındaki B noktasında keser; A, X₆ ile B'nin, "
           "B de X₂ ile X₃'ün konveks kombinasyonudur.")
    aria = ("Two copies of a convex hexagon X1 to X6. Left: point A on the edge X6X1. Right: interior point A "
            "on the dashed segment from X6 to B, where B lies on the edge X2X3.")
    save("uc-kombinasyon", figure(W, H, [left, right], cap, WIDE, aria=aria))


# ============================================================
# kaynak-geometri: feasible set of x1 + 2x2 + 3x3 + 4x4 = 7,
# 2x1 + x2 + x3 + 2x4 = 3 drawn in the (x3, x4) plane
# ============================================================
def source_geometry():
    W, H = 560, 440
    p = Plot(58, 30, 440, 340, (0, 2.75), (0, 2.12))
    p.grid(xs=(0.5, 1, 1.5, 2, 2.5), ys=(0.5, 1, 1.5, 2))
    p.axes((0, 0.5, 1, 1.5, 2, 2.5), (0.5, 1, 1.5, 2), x(3), x(4),
           xfmt=lambda v: f"{v:g}".replace(".", ","), yfmt=lambda v: f"{v:g}".replace(".", ","))
    tri = [(1, 0), (2.2, 0), (1, 1)]
    p.polygon(tri, THEORY, 0.18)
    p.line([(1, 0), (1, 2.06)], BASE, 2.0)                  # x1 = 0  <=>  x3 = 1
    p.line([(0, 11 / 6), (2.2, 0)], PRACTICE, 2.0)          # x2 = 0  <=>  5x3 + 6x4 = 11
    p.line([(0, 0), (0, 2.06)], REMARK, 2.6)                # x3 = 0
    p.line([(0, 0), (2.7, 0)], REMARK, 2.6)                 # x4 = 0
    p.label(1, 2.0, x(1) + " = 0", 7, 4, BASE, 13)
    p.label(1.62, 0.485, x(2) + " = 0", 8, -6, PRACTICE, 13)
    p.label(0, 1.2, x(3) + " = 0", 7, 0, REMARK, 13)
    p.label(2.6, 0, x(4) + " = 0", 0, -9, REMARK, 13, "middle")
    # feasible basic solutions
    p.points([(2.2, 0), (1, 0), (1, 1)], PRACTICE, 5.0)
    p.label(2.2, 0, X(2), 6, -9, PRACTICE, 13.5)
    p.label(1, 0, X(4), -7, -9, PRACTICE, 13.5, "end")
    p.label(1, 1, X(5), 9, -7, PRACTICE, 13.5)
    # infeasible basic solutions
    p.hollow_points([(0, 0), (0, 11 / 6)], REMARK, 5.2)
    p.label(0, 0, X(1), 9, -9, REMARK, 13.5)
    p.label(0, 11 / 6, X(3), 10, -6, REMARK, 13.5)
    # the feasible point (1/3, 1/3, 2, 0)
    p.points([(2, 0)], TEXT, 3.8)
    p.label(2, 0, "P", -2, -10, TEXT, 13, "end")

    cap = ("Örneğin uygun çözümleri x₃x₄ düzleminde: x₁ = (x₃ − 1)/3 ve x₂ = (11 − 5x₃ − 6x₄)/3 "
           "olduğundan x₁ ≥ 0 koşulu x₃ ≥ 1, x₂ ≥ 0 koşulu 5x₃ + 6x₄ ≤ 11 demektir. Uygun bölge boyalı "
           "üçgendir ve köşeleri üç uygun temel çözüm X₂, X₄, X₅'tir. Uygun olmayan X₁ ve X₃ üçgenin "
           "dışındadır. x₁ = 0 ile x₃ = 0 doğruları paraleldir; bu yüzden x₁ ve x₃ birlikte sıfırlanınca "
           "temel çözüm çıkmaz. P noktası (1/3, 1/3, 2, 0) uygun çözümüdür.")
    aria = ("Feasible set of the example in the x3-x4 plane: the triangle with vertices X4(1,0), X2(2.2,0), "
            "X5(1,1); infeasible basic solutions X1 at the origin and X3 at (0, 11/6); the lines x1 = 0 "
            "(x3 = 1) and x3 = 0 are parallel.")
    save("kaynak-geometri", figure(W, H, [p], cap, aria=aria))


# ============================================================
# sinirsiz: an unbounded feasible region
# ============================================================
def unbounded():
    W, H = 560, 420
    p = Plot(58, 30, 440, 320, (0, 6.2), (0, 4.5))
    p.grid(xs=(1, 2, 3, 4, 5, 6), ys=(1, 2, 3, 4))
    p.axes((0, 1, 2, 3, 4, 5, 6), (1, 2, 3, 4), x(1), x(2))
    p.polygon([(2, 0), (6.2, 0), (6.2, 4.5), (3.5, 4.5), (0.5, 1.5)], THEORY, 0.16)
    p.line([(0, 2), (2, 0)], BASE, 2.0)             # x1 + x2 = 2
    p.line([(0, 1), (3.5, 4.5)], PRACTICE, 2.0)     # -x1 + x2 = 1
    p.label(0.15, 0.3, x(1) + " + " + x(2) + " = 2", 0, 0, BASE, 13)
    p.label(2.6, 3.6, MINUS + x(1) + " + " + x(2) + " = 1", -10, -2, PRACTICE, 13, "end")
    p.points([(2, 0), (0.5, 1.5)], PRACTICE, 4.8)
    p.label(2, 0, "(2, 0)", 6, -9, TEXT, 13)
    p.label(0.5, 1.5, "(1/2, 3/2)", 10, 8, TEXT, 13)
    p.arrow((4.2, 1.6), (5.8, 1.6), REMARK, 2.0, 10)
    p.arrow((4.2, 1.6), (5.4, 2.8), REMARK, 2.0, 10)
    p.label(4.2, 1.6, "sınırsız", -8, 5, REMARK, 13, "end")

    cap = ("x₁ + x₂ ≥ 2, −x₁ + x₂ ≤ 1, x₁, x₂ ≥ 0 kısıtlarının uygun bölgesi. Bölge iki doğru ve x₁ "
           "ekseniyle sınırlanır ama sağa ve sağ yukarı doğru sonsuza uzanır; sınırsız bir konveks "
           "bölgedir. Yalnız iki köşesi vardır: (2, 0) ve (1/2, 3/2).")
    aria = ("Unbounded feasible region above x1 + x2 = 2, below -x1 + x2 = 1 and above the x1 axis, "
            "with vertices (2,0) and (1/2,3/2); arrows show that it extends without bound.")
    save("sinirsiz", figure(W, H, [p], cap, aria=aria))


# ============================================================
# dejenere: three constraint lines through one vertex
# ============================================================
def degenerate():
    W, H = 560, 440
    p = Plot(58, 30, 400, 340, (0, 2.35), (0, 2.35 * 340 / 400))
    p.grid(xs=(0.5, 1, 1.5, 2), ys=(0.5, 1, 1.5))
    p.axes((0, 0.5, 1, 1.5, 2), (0.5, 1, 1.5), x(1), x(2),
           xfmt=lambda v: f"{v:g}".replace(".", ","), yfmt=lambda v: f"{v:g}".replace(".", ","))
    p.polygon([(0, 0), (1, 0), (1, 1), (0, 1)], THEORY, 0.18)
    p.line([(0, 1.9975), (1.9975, 0)], BASE, 2.0)           # x1 + x2 = 2
    p.line([(1, 0), (1, 1.95)], PRACTICE, 2.0)              # x1 = 1
    p.line([(0, 1), (2.3, 1)], REMARK, 2.0)                 # x2 = 1
    p.label(1.55, 0.45, x(1) + " + " + x(2) + " = 2  (" + x(3) + " = 0)", 8, 0, BASE, 13)
    p.label(1, 1.8, x(1) + " = 1  (" + x(4) + " = 0)", 8, 0, PRACTICE, 13)
    p.label(2.3, 1, x(2) + " = 1  (" + x(5) + " = 0)", 0, -9, REMARK, 13, "end")
    p.points([(1, 1)], TEXT, 5.2)
    p.label(1, 1, "(1, 1)", -9, -9, TEXT, 13.5, "end")

    cap = ("x₁ + x₂ ≤ 2, x₁ ≤ 1, x₂ ≤ 1 kısıtlarının uygun bölgesi birim karedir. (1, 1) köşesinden "
           "üç kısıt doğrusu birden geçer: bu noktada x₃, x₄, x₅ aylak değişkenlerinin üçü de sıfırdır. "
           "Temel çözümde yalnız iki değişken sıfırlandığı için üçüncü sıfır bir temel değişkendir; "
           "köşe dejenere bir uygun temel çözümdür.")
    aria = ("Unit square feasible region; the three lines x1 + x2 = 2, x1 = 1 and x2 = 1 pass through "
            "the corner (1,1), a degenerate basic feasible solution.")
    save("dejenere", figure(W, H, [p], cap, aria=aria))


if __name__ == "__main__":
    extra_example()
    convex_sets()
    intersection_union()
    extreme_points()
    vertex_combination()
    source_geometry()
    unbounded()
    degenerate()
