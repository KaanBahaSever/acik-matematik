# -*- coding: utf-8 -*-
"""
Figures of the chapter "Kompakt ve Bağlantılı Kümeler"
(dersler/analiz-4/kompakt-ve-baglantili-kumeler.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box: a figure that illustrates a
definition sits directly below that box. The figures are NOT produced at
build time. Run

    python scripts/analysis4_figures/kmp.py
    python scripts/center_figures.py "analysis4-kmp-*.md"
    python scripts/check_figure_labels.py "scripts/_figures/analysis4-kmp-*.md"

and paste the markup of scripts/_figures/analysis4-kmp-<name>.md into the
.qmd. Captions are Turkish on purpose (they are shown on the site); aria
labels are plain ASCII.

Conventions: a boundary that belongs to the set is a solid line, one that does
not is dashed; points of the set are filled, excluded points are hollow.
Every drawing that contains a circle uses equal x and y scales.
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import (Plot, figure, blob, closed_curve, circle_pts, disk_fill, dot, hollow,  # noqa: E402
                      TEXT, THEORY, PRACTICE, BASE, REMARK)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "analysis4-kmp-"

MINUS, EPS, ALPHA, BB_R = "&#8722;", "&#949;", "&#945;", "&#8477;"


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


def to_data(p, px, py):
    """Pixel position -> data coordinates of panel p."""
    return (p.xmin + (px - p.x0) / p.w * (p.xmax - p.xmin),
            p.ymin + (p.y0 + p.h - py) / p.h * (p.ymax - p.ymin))


def trimmed_arrow(p, a, b, color, width=1.3, head=7.0, cut0=0.0, cut1=0.0, dash=None, opacity=1.0):
    """Arrow from data point a to b, shortened by cut0 / cut1 pixels at its ends."""
    ax, ay, bx, by = p.X(a[0]), p.Y(a[1]), p.X(b[0]), p.Y(b[1])
    L = math.hypot(bx - ax, by - ay)
    ux, uy = (bx - ax) / L, (by - ay) / L
    s = to_data(p, ax + ux * cut0, ay + uy * cut0)
    e = to_data(p, bx - ux * cut1, by - uy * cut1)
    p.arrow(s, e, color, width, head, dash, opacity)


def save(name, markup):
    (OUT_DIR / f"{PREFIX}{name}.md").write_text(markup, encoding="utf-8", newline="\n")
    print(f"{PREFIX}{name}.md")


# ============================================================ kapali
# Proof that a compact K is closed: the small closed ball B[x, r*] misses K,
# a larger ball B[x, r] still meets it.
XP, R_STAR, R_BIG = (1.8, 0.0), 1.1, 2.35
p = eq_plot(40, 40, 52, (-2.8, 4.5), (-2.6, 3.3))
p.origin_axes("", "", opacity=0.35)
# the compact set K: a bean whose right-most point lies just left of x = 0
k_pts = blob(0.0, 0.0, 1.12, [(0.13, 2, 0.5), (0.07, 3, 2.2), (-0.06, 1, 1.9)])
shift = -0.05 - max(x for x, _ in k_pts)
k_pts = [(x + shift, 0.95 * y) for x, y in k_pts]
closed_curve(p, k_pts, THEORY, 1.8, fill=THEORY, opacity=0.2)
kx = sum(x for x, _ in k_pts) / len(k_pts)
p.label(kx - 0.15, 0.42, "K", 0, 5, THEORY, 15, "middle", True, True)
# the larger closed ball B[x, r]: still meets K (secondary, thin)
p.circle(XP[0], XP[1], R_BIG, REMARK, 1.2, None, "none", 0.9)
ang = math.radians(-58)
p.label(XP[0] + R_BIG * math.cos(ang), R_BIG * math.sin(ang),
        it("B") + "[" + it("x") + ", " + it("r") + "]", 7, 9, REMARK, 12)
# the small closed ball B[x, r*]: disjoint from K
disk_fill(p, XP[0], XP[1], R_STAR, PRACTICE, 0.15)
p.circle(XP[0], XP[1], R_STAR, PRACTICE, 1.9)
p.line([XP, (XP[0], R_STAR)], PRACTICE, 1.2)
p.label(XP[0], R_STAR / 2, it("r") + sup("*"), 5, 4, PRACTICE, 12)
dot(p, XP, PRACTICE, 3.6)
p.label(XP[0], 0, it("x"), -6, 15, PRACTICE, 13, "end")
p.label(XP[0], -R_STAR, it("B") + "[" + it("x") + ", " + it("r") + sup("*") + "]", 0, 17, PRACTICE, 12, "middle")
# G_{r*}: everything outside the small ball
p.label(4.5, 3.05, it("G") + sub(it("r") + "*") + " = " + BB_R + sup(it("n")) + " \\ " + it("B") + "["
        + it("x") + ", " + it("r") + sup("*") + "]", 0, 0, TEXT, 12, "end")
p.label(4.5, 3.05, it("K") + " bu kümenin içinde", 0, 17, TEXT, 11.5, "end")
save("kapali", figure(
    480, 400, [p],
    "Kompakt <em>K</em> kümesi ve <em>K</em>'nin dışındaki <em>x</em> noktası. Sonlu alt örtünün en küçük yarıçapı "
    "<em>r</em>* ile çizilen <em>B</em>[<em>x</em>, <em>r</em>*] kapalı yuvarı <em>K</em>'ye değmez; yani "
    "<em>K</em> &#8838; <em>G</em><sub><em>r</em>*</sub> = &#8477;<sup><em>n</em></sup> &#8726; <em>B</em>[<em>x</em>, <em>r</em>*] "
    "ve <em>B</em>(<em>x</em>, <em>r</em>*) yuvarı <em>K</em>'nin tümleyeninde kalır. Daha büyük bir <em>r</em> için "
    "<em>B</em>[<em>x</em>, <em>r</em>] yuvarı <em>K</em>'yi kesebilir.",
    aria="A compact set K, a point x outside it, a small closed ball around x missing K and a larger ball meeting K"))

# ============================================================ hucre-bolme
# Bisection of the closed square I_1 = [-2, 2]^2 into nested bad cells.
p = eq_plot(40, 30, 82, (-2.3, 2.3), (-2.3, 2.3))
cells = [(-2.0, 2.0), (0.0, 2.0), (0.0, 1.0), (0.5, 1.0)]   # I_1 ... I_4 as [lo, hi]^2
fills = [0.0, 0.12, 0.16, 0.24]


def square(lo, hi):
    return [(lo, lo), (hi, lo), (hi, hi), (lo, hi)]


for (lo, hi), op in zip(cells, fills):
    if op:
        p.polygon(square(lo, hi), THEORY, op)
# halving lines of I_1, I_2, I_3
for (lo, hi), col, op in zip(cells[:3], (TEXT, THEORY, THEORY), (0.45, 0.7, 0.7)):
    m = (lo + hi) / 2
    p.line([(m, lo), (m, hi)], col, 0.9, None, op)
    p.line([(lo, m), (hi, m)], col, 0.9, None, op)
# frames: I_1 thin, the chosen cells heavier
p.line(square(-2.0, 2.0) + [(-2.0, -2.0)], TEXT, 1.3, None, 0.8)
p.line(square(0.0, 2.0) + [(0.0, 0.0)], THEORY, 2.3)
p.line(square(0.0, 1.0) + [(0.0, 0.0)], THEORY, 1.9)
p.line(square(0.5, 1.0) + [(0.5, 0.5)], THEORY, 1.7)
# the common point x and the ball B(x, eps) inside G_alpha0
XC, EB = (0.75, 0.75), 0.62
p.circle(XC[0], XC[1], EB, PRACTICE, 1.6, "5 3")
dot(p, XC, PRACTICE, 3.4)
p.label(XC[0], XC[1], it("x"), -5, 13, PRACTICE, 12.5, "end")
ang = math.radians(45)
p.label(XC[0] + EB * math.cos(ang), XC[1] + EB * math.sin(ang),
        it("B") + "(" + it("x") + ", " + EPS + ")", 5, -4, PRACTICE, 12)
# cell names
p.label(-2.0, -2.0, it("I") + sub("1"), 7, -8, TEXT, 13)
p.label(2.0, 2.0, it("I") + sub("2"), -7, 17, THEORY, 13, "end")
p.label(0.0, 0.0, it("I") + sub("3"), 5, -6, THEORY, 12.5)
p.label(1.0, 1.0, it("I") + sub("4"), -3, 13, THEORY, 11.5, "end")
save("hucre-bolme", figure(
    460, 440, [p],
    "İkiye bölme yöntemi: <em>I</em><sub>1</sub> = [&#8722;2, 2] &#215; [&#8722;2, 2] karesi dört eş parçaya "
    "bölünür ve kötü bir parça <em>I</em><sub>2</sub> seçilir; <em>I</em><sub>3</sub> ve <em>I</em><sub>4</sub> aynı "
    "biçimde elde edilir. Hücreler ortak <em>x</em> noktasına büzülür ve bir adımdan sonra "
    "<em>B</em>(<em>x</em>, &#949;) &#8838; <em>G</em><sub>&#945;<sub>0</sub></sub> yuvarının içine girer.",
    aria="A square divided into four, one quarter divided again, down to a small cell inside a ball around x"))

# ============================================================ kelebek
# Two triangles touching at the origin, separated by the half planes x < 0 and x > 0.
L = 1.55
p = eq_plot(40, 30, 112, (-L, L), (-L, L))
p.polygon([(-L, -L), (0, -L), (0, L), (-L, L)], THEORY, 0.12)
p.polygon([(0, -L), (L, -L), (L, L), (0, L)], PRACTICE, 0.12)
# axes: thin x axis, dashed y axis = the common boundary of U and V
p.line([(-L, 0), (L, 0)], TEXT, 1.0, None, 0.5)
p.line([(0, -L), (0, L)], TEXT, 1.5, "6 4", 0.75)
for s in (-1, 1):
    p.line([(s, -0.03), (s, 0.03)], TEXT, 1.0, None, 0.6)
    p.line([(-0.03, s), (0.03, s)], TEXT, 1.0, None, 0.6)
p.label(1, 0, "1", 5, 14, TEXT, 11)
p.label(-1, 0, MINUS + "1", -5, 14, TEXT, 11, "end")
p.label(0, 1, "1", -6, 4, TEXT, 11, "end")
p.label(0, -1, MINUS + "1", -6, 4, TEXT, 11, "end")
# the set A: the diagonal edges are dashed, the vertical edges solid
for s in (-1, 1):
    p.polygon([(0, 0), (s, 1), (s, -1)], BASE, 0.25)
    p.line([(0, 0), (s, 1)], BASE, 1.6, "5 3")
    p.line([(0, 0), (s, -1)], BASE, 1.6, "5 3")
    p.line([(s, -1), (s, 1)], BASE, 1.9)
    hollow(p, (s, 1), BASE, 3.2)
    hollow(p, (s, -1), BASE, 3.2)
    p.label(0.72 * s, 0.33, it("A"), 0, 0, BASE, 13, "middle", True)
hollow(p, (0, 0), TEXT, 3.8)
p.line([(0.02, -0.08), (0.2, -1.17)], TEXT, 0.9, None, 0.6)
p.label(0.2, -1.17, "(0, 0) " + it("A") + "'da değil", -8, 15, TEXT, 11.5)
# the points (-1/2, 0) and (1/2, 0)
dot(p, (-0.5, 0), THEORY, 3.6)
dot(p, (0.5, 0), PRACTICE, 3.6)
p.label(-0.5, 0, "(" + MINUS + "1/2, 0)", 0, 17, THEORY, 11, "middle")
p.label(0.5, 0, "(1/2, 0)", 0, 17, PRACTICE, 11, "middle")
p.label(-L, L, it("U"), 12, 22, THEORY, 15, "start", True)
p.label(L, L, it("V"), -12, 22, PRACTICE, 15, "end", True)
save("kelebek", figure(
    440, 420, [p],
    "<em>A</em> kümesi orijinde birbirine değen iki üçgendir; eğik kenarlar ve orijin kümeye ait değildir, "
    "<em>x</em> = &#177;1 üzerindeki dikey kenarlar (uçları hariç) kümeye aittir. Sol yarı düzlem <em>U</em> "
    "ile sağ yarı düzlem <em>V</em> açık ve ayrık kümelerdir; <em>A</em>'yı iki parçaya ayırırlar.",
    aria="Two triangles meeting at the origin, which is excluded, separated by the left and right half planes"))

# ============================================================ konveks
# Convex C, the segment p(t) = t x + (1 - t) y and its pull-back to [0, 1].
XP, YP = (1.2, 0.5), (-1.2, -0.5)
A_E, B_E = 2.5, 1.5
p = eq_plot(40, 30, 76, (-2.75, 2.75), (-2.85, 1.7))
ell = circle_pts(0, 0, 1, 0, 2 * math.pi, 160)
ell = [(A_E * x, B_E * y) for x, y in ell[:-1]]
closed_curve(p, ell, BASE, 1.6, fill=BASE, opacity=0.12)
p.label(-1.55, 0.8, it("C"), 0, 0, BASE, 15, "middle", True)
# open sets U (around x) and V (around y): wobbly discs with dashed boundaries;
# V sits a little up-left of y so that the label of y fits inside it
U_C, U_R, U_W = XP, 0.66, [(0.07, 2, 0.4), (0.04, 3, 1.3)]
V_C, V_R, V_W = (-1.4, -0.38), 0.72, [(0.06, 2, 2.2), (0.04, 3, 0.2)]
closed_curve(p, blob(U_C[0], U_C[1], U_R, U_W), THEORY, 1.5, "5 3", THEORY, 0.16)
closed_curve(p, blob(V_C[0], V_C[1], V_R, V_W), PRACTICE, 1.5, "5 3", PRACTICE, 0.16)


def inside(c, base, wobble, q):
    """Is q inside the blob r(theta) = base + sum(a cos(k theta + phase)) centred at c?"""
    th = math.atan2(q[1] - c[1], q[0] - c[0])
    return math.hypot(q[0] - c[0], q[1] - c[1]) < base + sum(a * math.cos(k * th + ph) for a, k, ph in wobble)


def seg(t):
    return (t * XP[0] + (1 - t) * YP[0], t * XP[1] + (1 - t) * YP[1])


def crossing(c, base, wobble, t_in, t_out):
    """Parameter where the segment leaves the blob (bisection between an inner and an outer t)."""
    for _ in range(60):
        tm = (t_in + t_out) / 2
        if inside(c, base, wobble, seg(tm)):
            t_in = tm
        else:
            t_out = tm
    return (t_in + t_out) / 2


T_U = crossing(U_C, U_R, U_W, 1.0, 0.5)                    # p(t) in U  <=>  t > T_U
T_V = crossing(V_C, V_R, V_W, 0.0, 0.5)                    # p(t) in V  <=>  t < T_V
p.line([YP, XP], TEXT, 2.2)
dot(p, XP, THEORY, 3.8)
dot(p, YP, PRACTICE, 3.8)
dot(p, (0, 0), TEXT, 3.0)
p.label(XP[0], XP[1], it("x") + " = " + it("p") + "(1)", 0, -9, THEORY, 12, "middle")
p.label(YP[0], YP[1], it("y") + " = " + it("p") + "(0)", -3, -8, PRACTICE, 12, "end")
p.label(0, 0, it("p") + "(1/2)", -6, -8, TEXT, 11.5, "end")
p.label(XP[0] + U_R * 1.02, XP[1] - 0.24, it("U"), 6, 4, THEORY, 14, "start", True)
ang = math.radians(-40)
p.label(V_C[0] + V_R * math.cos(ang), V_C[1] + V_R * math.sin(ang), it("V"), 8, 15, PRACTICE, 14, "start", True)
# the number line [0, 1] drawn under the segment: t -> -1.5 + 3t
LY = -2.45


def tx(t):
    return -1.5 + 3 * t


p.line([(tx(0), LY), (tx(1), LY)], TEXT, 1.2, None, 0.6)
p.line([(tx(0), LY), (tx(T_V), LY)], PRACTICE, 3.2)
p.line([(tx(T_U), LY), (tx(1), LY)], THEORY, 3.2)
dot(p, (tx(0), LY), PRACTICE, 3.6)
dot(p, (tx(1), LY), THEORY, 3.6)
hollow(p, (tx(T_V), LY), PRACTICE, 3.4)
hollow(p, (tx(T_U), LY), THEORY, 3.4)
p.line([(tx(0.5), LY - 0.05), (tx(0.5), LY + 0.05)], TEXT, 1.1, None, 0.7)
p.label(tx(0), LY, "0", 0, 18, TEXT, 11.5, "middle")
p.label(tx(0.5), LY, "1/2", 0, 18, TEXT, 11.5, "middle")
p.label(tx(1), LY, "1", 0, 18, TEXT, 11.5, "middle")
p.label(tx(T_V / 2), LY, it("J"), 0, -9, PRACTICE, 13, "middle", True)
p.label(tx((1 + T_U) / 2), LY, it("I"), 0, -9, THEORY, 13, "middle", True)
trimmed_arrow(p, (tx(0), LY), YP, PRACTICE, 1.1, 7.0, 7, 6, "4 3", 0.85)
trimmed_arrow(p, (tx(1), LY), XP, THEORY, 1.1, 7.0, 7, 6, "4 3", 0.85)
p.label(0, -1.98, it("p") + "(" + it("t") + ") = " + it("t") + it("x") + " + (1 " + MINUS + " " + it("t") + ")"
        + it("y"), 0, 0, TEXT, 12, "middle")
save("konveks", figure(
    500, 420, [p],
    "Konveks <em>C</em> kümesinde <em>x</em> ile <em>y</em>'yi birleştiren doğru parçası "
    "<em>p</em>(<em>t</em>) = <em>tx</em> + (1 &#8722; <em>t</em>)<em>y</em>, <em>t</em> &#8712; [0, 1] ile taranır. "
    "Parçanın <em>U</em>'ya düşen noktaları <em>I</em> kümesine (mavi), <em>V</em>'ye düşen noktaları <em>J</em> "
    "kümesine (turuncu) karşılık gelir. <em>C</em> bağlantısız olsaydı bu iki küme [0, 1] aralığını da ayırırdı.",
    aria="A convex ellipse with a segment from y to x, open blobs U and V around the endpoints and the interval 0 to 1 mapped onto the segment"))
