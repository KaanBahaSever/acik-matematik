# -*- coding: utf-8 -*-
"""
Figures of the chapter "SymPy ile Sembolik Hesap"
(dersler/python-bilimsel/sympy-ile-sembolik-hesap.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution,
exercise or callout), never inside a definition box and never directly under
a heading; concept figures stay visible (not inside a collapsed .cozum
block). The figures are NOT produced at build time. The data come from SymPy
and NumPy, so run this script with the course environment:

    taslaklar/python-bilimsel/.venv/Scripts/python.exe \
        scripts/python_figures/sym.py
    python scripts/center_figures.py "python-sym-*.md"
    python scripts/check_figure_labels.py "scripts/_figures/python-sym-*.md"

(set OPENBLAS_NUM_THREADS=1 on this machine) and paste the markup of
scripts/_figures/python-sym-<name>.md into the .qmd. Every figure is drawn
from exactly the data the chapter's code computes: the same expressions,
SymPy calls (srepr, diff, solve, dsolve, series, lambdify) and NumPy grids.
Captions are Turkish on purpose; aria labels are plain ASCII.
"""
import math
import sys
from pathlib import Path

import numpy as np
import sympy as sp

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import (Plot, figure, hollow, TEXT, THEORY,  # noqa: E402
                      PRACTICE, BASE, REMARK)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "python-sym-"

MINUS = "&#8722;"
PI_S = "&#960;"
SUB = {str(k): chr(0x2080 + k) for k in range(10)}


def save(name, markup):
    (OUT_DIR / f"{PREFIX}{name}.md").write_text(markup, encoding="utf-8",
                                                newline="\n")
    print(f"{PREFIX}{name}.md")


def it(s):
    """Italic run inside an SVG <text>."""
    return f'<tspan font-style="italic">{s}</tspan>'


def sup(s, size=8.5):
    """Superscript inside an SVG <text>."""
    return (f'<tspan font-size="{size}" dy="-5">{s}</tspan>'
            f'<tspan dy="5">&#8203;</tspan>')


def tick(t):
    """Tick label with a true minus sign."""
    s = f"{t:g}"
    return s.replace(".", ",").replace("-", MINUS)


def pt(a, b):
    """Point label (a, b) with true minus signs."""
    return f"({tick(a)}, {tick(b)})"


def clip_y(xs, ys, lo, hi):
    """Split the polyline (xs, ys) into pieces that stay inside lo <= y <= hi.

    A piece entering or leaving the band is cut at the band edge by linear
    interpolation, so a steep curve does not poke out of its panel.
    """
    pieces, cur = [], []
    for k in range(len(xs)):
        x, y = float(xs[k]), float(ys[k])
        inside = lo <= y <= hi
        if k > 0:
            xp, yp = float(xs[k - 1]), float(ys[k - 1])
            was = lo <= yp <= hi
            if inside != was:
                edge = hi if (y > hi or yp > hi) else lo
                t = (edge - yp) / (y - yp)
                cut = (xp + t * (x - xp), edge)
                cur.append(cut)
                if was:
                    pieces.append(cur)
                    cur = []
                else:
                    cur = [cut]
        if inside:
            cur.append((x, y))
    if len(cur) > 1:
        pieces.append(cur)
    return [c for c in pieces if len(c) > 1]


x, y = sp.symbols("x y")


# ============================================================
# ifade-agaci: the expression tree of x**2 + 2*x*y + sin(x)
# ============================================================
expr = x**2 + 2*x*y + sp.sin(x)
assert sp.srepr(expr) == ("Add(Pow(Symbol('x'), Integer(2)), "
                          "Mul(Integer(2), Symbol('x'), Symbol('y')), "
                          "sin(Symbol('x')))")


def node_kind(e):
    """('op' | 'sym' | 'num', label) of one tree node."""
    if e.is_Symbol:
        return "sym", it(e.name)
    if e.is_Integer:
        return "num", str(e).replace("-", MINUS)
    return "op", e.func.__name__


# level 1: the three terms (srepr order), level 2: their arguments
terms = list(expr.args)
SUBEXPR = {
    "Pow": it("x") + "²",
    "Mul": "2" + it("x") + it("y"),
    "sin": "sin " + it("x"),
}
W_TREE = 540
LEAF_GAP, GROUP_GAP = 62, 104
leaf_x, parent_x, cursor = [], [], 0.0
for g, term in enumerate(terms):
    if g:
        cursor += GROUP_GAP - LEAF_GAP
    xs_g = []
    for _ in term.args:
        xs_g.append(cursor)
        cursor += LEAF_GAP
    leaf_x.append(xs_g)
cursor -= LEAF_GAP
shift = (W_TREE - cursor) / 2
leaf_x = [[v + shift for v in g] for g in leaf_x]
parent_x = [(g[0] + g[-1]) / 2 for g in leaf_x]
root_x = (parent_x[0] + parent_x[-1]) / 2
Y0, Y1, Y2 = 40, 120, 200
BOX_H = 28


def box_w(label_len):
    return 16 + 9.0 * label_len


p = Plot(0, 0, W_TREE, 240, (0, 1), (0, 1))


def edge(x1, y1, x2, y2):
    p.add(f'<line x1="{x1:.1f}" y1="{y1 + BOX_H / 2:.1f}" x2="{x2:.1f}" '
          f'y2="{y2 - BOX_H / 2:.1f}" stroke="{TEXT}" stroke-width="1.2" '
          f'opacity="0.5"/>')


def node(cx, cy, e):
    kind, label = node_kind(e)
    raw = e.func.__name__ if kind == "op" else str(e)
    w = box_w(len(raw))
    color = {"op": THEORY, "sym": BASE, "num": PRACTICE}[kind]
    rx = 6 if kind == "op" else BOX_H / 2
    p.add(f'<rect x="{cx - w / 2:.1f}" y="{cy - BOX_H / 2:.1f}" '
          f'width="{w:.1f}" height="{BOX_H}" rx="{rx}" fill="{color}" '
          f'fill-opacity="0.12" stroke="{color}" stroke-width="1.4"/>')
    p.text_px(cx, cy + 4.5, label, color, 13, "middle", bold=(kind == "op"))


for px_, term in zip(parent_x, terms):
    edge(root_x, Y0, px_, Y1)
for g, term in enumerate(terms):
    for lx, arg in zip(leaf_x[g], term.args):
        edge(parent_x[g], Y1, lx, Y2)
node(root_x, Y0, expr)
for g, term in enumerate(terms):
    node(parent_x[g], Y1, term)
    for lx, arg in zip(leaf_x[g], term.args):
        node(lx, Y2, arg)
# the subexpression each level-1 node stands for, right beside the node
for px_, term in zip(parent_x, terms):
    name = term.func.__name__
    w = box_w(len(name))
    p.text_px(px_ + w / 2 + 8, Y1 + 4.5, "= " + SUBEXPR[name], TEXT, 12.5)
p.text_px(root_x + box_w(3) / 2 + 8, Y0 + 4.5,
          "= " + it("x") + "² + 2" + it("x") + it("y") + " + sin "
          + it("x"), TEXT, 12.5)

save("ifade-agaci", figure(
    W_TREE, 240, [p],
    "<em>x</em>² + 2<em>xy</em> + sin <em>x</em> ifadesinin ağacı. Kökteki "
    "<code>Add</code> düğümünün üç alt ağacı vardır: <code>Pow</code>, "
    "<code>Mul</code> ve <code>sin</code>. Yapraklar semboller "
    "(<em>x</em>, <em>y</em>) ve tam sayılardır (2). Şekil, yukarıdaki "
    "<code>sp.srepr</code> çıktılarının çizimidir.",
    aria="Expression tree of x**2 + 2*x*y + sin(x): the root Add has three "
         "children Pow, Mul and sin; Pow has leaves x and 2, Mul has leaves "
         "2, x and y, sin has the leaf x"))


# ============================================================
# tek-yonlu: atan(1/x) near 0 with the two one-sided limits
# ============================================================
f_atan = sp.lambdify(x, sp.atan(1 / x), "numpy")
right = sp.limit(sp.atan(1 / x), x, 0, dir="+")
left = sp.limit(sp.atan(1 / x), x, 0, dir="-")
assert (right, left) == (sp.pi / 2, -sp.pi / 2)
R, L = float(right), float(left)

XR, YR = (-4.4, 4.4), (-2.05, 2.05)
p = Plot(40, 24, 440, 250, XR, YR)
p.origin_axes(it("x"), it("y"), [-4, -2, 2, 4], [], tick, tick)
for level in (R, L):
    p.line([(XR[0], level), (XR[1], level)], TEXT, 1.0, "5 4", 0.55)
xr = np.linspace(0.02, XR[1], 400)
xl = np.linspace(XR[0], -0.02, 400)
p.line(list(zip(xr, f_atan(xr))), THEORY, 2.1)
p.line(list(zip(xl, f_atan(xl))), THEORY, 2.1)
hollow(p, (0, R), PRACTICE, 4.2, 1.8)
hollow(p, (0, L), PRACTICE, 4.2, 1.8)
p.label(XR[0], R, PI_S + "/2", 2, -7, TEXT, 12)
p.label(XR[1], L, MINUS + PI_S + "/2", -2, 16, TEXT, 12, "end")
p.label(0, R, "sağ limit " + PI_S + "/2", 10, -9, PRACTICE, 12, bold=True)
p.label(0, L, "sol limit " + MINUS + PI_S + "/2", -10, 19, PRACTICE, 12,
        "end", bold=True)
# curve name in the empty band above the right branch
p.label(1.8, 1.0, it("y") + " = arctan(1/" + it("x") + ")", 0, 0, THEORY,
        12.5, bold=True)

save("tek-yonlu", figure(
    500, 300, [p],
    "<em>y</em> = arctan(1/<em>x</em>) fonksiyonunun grafiği. Sağdan "
    "yaklaşırken değerler &#960;/2'ye, soldan yaklaşırken &#8722;&#960;/2'ye "
    "gider; içi boş noktalar bu iki tek yönlü limiti gösterir. Sağ ve sol "
    "limit farklı olduğundan sıfırda iki yönlü limit yoktur.",
    aria="Graph of y = arctan(1/x) on [-4.4, 4.4]; the right branch tends to "
         "pi/2 and the left branch to -pi/2 as x approaches 0, marked by two "
         "hollow points on the y axis and dashed horizontal lines"))


# ============================================================
# teget: f(x) = x^3 - 2x, its tangent at x = 1 and the second intersection
# ============================================================
f_cub = x**3 - 2*x
a_t = 1
slope = sp.diff(f_cub, x).subs(x, a_t)
tangent = sp.expand(f_cub.subs(x, a_t) + slope * (x - a_t))
assert tangent == x - 2
assert sp.factor(f_cub - tangent) == (x - 1)**2 * (x + 2)
F = sp.lambdify(x, f_cub, "numpy")
TG = sp.lambdify(x, tangent, "numpy")

XR, YR = (-2.7, 2.6), (-6.2, 5.2)
p = Plot(40, 24, 420, 300, XR, YR)
p.origin_axes(it("x"), it("y"), [-2, -1, 1, 2], [-4, 2, 4], tick, tick)
xx = np.linspace(XR[0], XR[1], 500)
for piece in clip_y(xx, F(xx), YR[0], YR[1]):
    p.line(piece, THEORY, 2.1)
p.line([(XR[0], float(TG(XR[0]))), (XR[1], float(TG(XR[1])))], BASE, 1.9)
p.vline(-2, 0, -4, TEXT, "3 3", 0.55)
p.vline(1, 0, -1, TEXT, "3 3", 0.55)
p.points([(1, -1)], PRACTICE, 4.6)
p.points([(-2, -4)], REMARK, 4.6)
p.label(1, -1, pt(1, -1), 10, 16, PRACTICE, 12, bold=True)
p.label(-2, -4, pt(-2, -4), 10, 14, REMARK, 12, bold=True)
xc = 1.95
p.label(xc, float(F(xc)), it("y") + " = " + it("x") + sup("3") + " "
        + MINUS + " 2" + it("x"), -10, 0, THEORY, 12.5, "end", bold=True)
p.label(XR[1], float(TG(XR[1])), it("y") + " = " + it("x") + " " + MINUS
        + " 2", 6, 4, BASE, 12.5, bold=True)

save("teget", figure(
    560, 350, [p],
    "<em>y</em> = <em>x</em>³ &#8722; 2<em>x</em> eğrisi ve "
    "<em>x</em> = 1'deki teğeti <em>y</em> = <em>x</em> &#8722; 2. Teğet "
    "eğriye (1, &#8722;1) noktasında değer, farkın çift kökü "
    "<em>x</em> = 1 budur. Basit kök <em>x</em> = &#8722;2 ise teğetin "
    "eğriyi yeniden kestiği (&#8722;2, &#8722;4) noktasını verir.",
    aria="The cubic y = x^3 - 2x with its tangent line y = x - 2 at x = 1; "
         "the tangent touches the curve at (1, -1) and crosses it again at "
         "(-2, -4)"))


# ============================================================
# alan: the region between y = x^2 and y = x + 2 (exm-sym-alan)
# ============================================================
top, bottom = x + 2, x**2
a_i, b_i = sp.solve(sp.Eq(top, bottom), x)
assert (a_i, b_i) == (-1, 2)
assert sp.integrate(top - bottom, (x, a_i, b_i)) == sp.Rational(9, 2)
a_i, b_i = float(a_i), float(b_i)

XR, YR = (-2.6, 3.3), (-0.9, 6.3)
p = Plot(40, 24, 400, 300, XR, YR)
p.origin_axes(it("x"), it("y"), [-2, -1, 1, 2, 3], [1, 4, 6], tick, tick)
xs_in = np.linspace(a_i, b_i, 200)
region = ([(v, v + 2) for v in xs_in]
          + [(v, v * v) for v in xs_in[::-1]])
p.polygon(region, PRACTICE, 0.18)
xp = np.linspace(-math.sqrt(YR[1]), math.sqrt(YR[1]), 300)
p.line(list(zip(xp, xp**2)), THEORY, 2.1)
p.line([(-2.6, -0.6), (3.3, 5.3)], BASE, 2.0)
p.points([(a_i, a_i + 2), (b_i, b_i + 2)], PRACTICE, 4.4)
p.label(math.sqrt(YR[1]), YR[1], it("y") + " = " + it("x") + "²", 8, 6,
        THEORY, 12.5, bold=True)
p.label(3.3, 5.3, it("y") + " = " + it("x") + " + 2", 8, 6, BASE, 12.5,
        bold=True)

save("alan", figure(
    520, 350, [p],
    "<em>y</em> = <em>x</em>² parabolü ile <em>y</em> = <em>x</em> + 2 "
    "doğrusu arasında kalan sınırlı bölge (gölgeli). İki eğri bölgenin uç "
    "noktalarında kesişir.",
    aria="The parabola y = x^2 and the line y = x + 2; the bounded region "
         "between them is shaded and the two intersection points are "
         "marked"))


# ============================================================
# cember-dogru: the circle x^2 + y^2 = 5 and the line y = x + 1
# ============================================================
eqs = [sp.Eq(x**2 + y**2, 5), sp.Eq(y, x + 1)]
sols = sp.solve(eqs, [x, y], dict=True)
assert sols == [{x: -2, y: -1}, {x: 1, y: 2}]
r5 = math.sqrt(5)

XR, YR = (-3.3, 3.3), (-3.0, 3.4)
width = 360
p = Plot(40, 24, width, width * (YR[1] - YR[0]) / (XR[1] - XR[0]), XR, YR)
p.origin_axes(it("x"), it("y"), [-2, -1, 1, 2], [-2, -1, 1, 2], tick, tick)
p.circle(0, 0, r5, THEORY, 2.1)
p.line([(-3.3, -2.3), (2.4, 3.4)], BASE, 2.0)
for s in sols:
    p.points([(float(s[x]), float(s[y]))], PRACTICE, 4.6)
p.label(-2, -1, pt(-2, -1), -10, 4, PRACTICE, 12, "end", bold=True)
p.label(1, 2, pt(1, 2), 4, -18, PRACTICE, 12, "end", bold=True)
ang = -math.pi / 4
p.label(r5 * math.cos(ang), r5 * math.sin(ang),
        it("x") + "² + " + it("y") + "² = 5", 8, 14, THEORY, 12.5,
        bold=True)
p.label(2.4, 3.4, it("y") + " = " + it("x") + " + 1", 8, 6, BASE, 12.5,
        bold=True)

save("cember-dogru", figure(
    500, 400, [p],
    "<em>x</em>² + <em>y</em>² = 5 çemberi ile <em>y</em> = <em>x</em> + 1 "
    "doğrusu (&#8722;2, &#8722;1) ve (1, 2) noktalarında kesişir. Bu iki "
    "nokta, <code>sp.solve</code> fonksiyonunun bulduğu iki çözümdür.",
    aria="The circle x^2 + y^2 = 5 and the line y = x + 1 meeting at the "
         "points (-2, -1) and (1, 2)"))


# ============================================================
# yon-alani: direction field of y' = x - y and the solution family
# ============================================================
yf = sp.Function("y")
ode = sp.Eq(yf(x).diff(x) + yf(x), x)
general = sp.dsolve(ode, yf(x)).rhs
C1 = sp.Symbol("C1")
assert sp.simplify(general - (C1 * sp.exp(-x) + x - 1)) == 0
particular = sp.dsolve(ode, yf(x), ics={yf(0): 1}).rhs
assert sp.simplify(particular - (x - 1 + 2 * sp.exp(-x))) == 0

XR, YR = (-1.0, 4.0), (-2.0, 4.0)
PW, PH = 340, 310
p = Plot(60, 24, PW, PH, XR, YR)
p.origin_axes(it("x"), it("y"), [1, 2, 3], [-1, 1, 2, 3, 4], tick, tick)
# slope marks of y' = x - y on a grid, drawn in pixel space
sx = PW / (XR[1] - XR[0])
sy = PH / (YR[1] - YR[0])
HALF = 6.0
marks = []
for gx in np.arange(-0.75, 4.0, 0.5):
    for gy in np.arange(-1.75, 4.0, 0.5):
        slope_xy = gx - gy
        dx_px, dy_px = sx, slope_xy * sy
        norm = math.hypot(dx_px, dy_px)
        ux, uy = dx_px / norm * HALF, dy_px / norm * HALF
        cx, cy = p.X(gx), p.Y(gy)
        marks.append(f'<line x1="{cx - ux:.1f}" y1="{cy + uy:.1f}" '
                     f'x2="{cx + ux:.1f}" y2="{cy - uy:.1f}"/>')
p.add(f'<g stroke="{TEXT}" stroke-width="1.1" opacity="0.38" '
      f'stroke-linecap="round">' + "".join(marks) + "</g>")
xx = np.linspace(XR[0], XR[1], 600)
family = [-1, 0, 1, 3]
for c in family:
    curve = sp.lambdify(x, general.subs(C1, c), "numpy")
    yy = curve(xx) * np.ones_like(xx)
    pieces = clip_y(xx, yy, YR[0], YR[1])
    for piece in pieces:
        p.line(piece, THEORY, 1.5, opacity=0.8)
    x_in, y_in = pieces[0][0]
    lab = it("C") + "₁ = " + tick(c)
    if abs(x_in - XR[0]) < 1e-9:
        p.label(x_in, y_in, lab, -6, 4, THEORY, 11.5, "end")
    elif abs(y_in - YR[1]) < 1e-9:
        p.label(x_in, y_in, lab, 0, -7, THEORY, 11.5, "middle")
    else:
        p.label(x_in, y_in, lab, 0, 16, THEORY, 11.5, "middle")
part = sp.lambdify(x, particular, "numpy")
pieces = clip_y(xx, part(xx), YR[0], YR[1])
for piece in pieces:
    p.line(piece, PRACTICE, 2.6)
x_in, y_in = pieces[0][0]
p.label(x_in, y_in, it("C") + "₁ = 2", -6, 4, PRACTICE, 12, "end",
        bold=True)
p.points([(0, 1)], PRACTICE, 4.8)
p.label(0, 1, it("y") + "(0) = 1", -8, 17, PRACTICE, 12, "end", bold=True)

save("yon-alani", figure(
    470, 380, [p],
    "<em>y</em>&#8242; = <em>x</em> &#8722; <em>y</em> denkleminin yön "
    "alanı (kısa çizgiler her noktadaki eğimi gösterir) ve "
    "<em>y</em> = <em>C</em>₁<em>e</em><sup>&#8722;<em>x</em></sup> + "
    "<em>x</em> &#8722; 1 çözüm ailesinden <em>C</em>₁ = &#8722;1, 0, 1, "
    "2, 3 eğrileri. Kalın eğri, (0, 1) noktasından geçen "
    "<em>C</em>₁ = 2 çözümüdür. Bütün çözümler <em>C</em>₁ = 0 için elde "
    "edilen <em>y</em> = <em>x</em> &#8722; 1 doğrusuna yaklaşır.",
    aria="Direction field of y' = x - y on [-1, 4] x [-2, 4] with the "
         "solution curves y = C1 exp(-x) + x - 1 for C1 = -1, 0, 1, 2, 3; "
         "the curve for C1 = 2 through (0, 1) is highlighted and all "
         "curves approach the line y = x - 1"))


# ============================================================
# taylor: sin x and its Taylor polynomials T1, T3, T5, T7 (Matplotlib code)
# ============================================================
xs_t = np.linspace(-2 * np.pi, 2 * np.pi, 400)
XR, YR = (-2 * math.pi - 0.2, 2 * math.pi + 1.0), (-3.0, 3.0)
p = Plot(40, 30, 480, 270, XR, YR)
p.origin_axes(it("x"), it("y"),
              [-2 * math.pi, -math.pi, math.pi, 2 * math.pi], [-2, -1, 1, 2],
              lambda t: {-2: MINUS + "2" + PI_S, -1: MINUS + PI_S,
                         1: PI_S, 2: "2" + PI_S}[round(t / math.pi)],
              tick)
p.line(list(zip(xs_t, np.sin(xs_t))), TEXT, 2.6)
COLORS = {1: THEORY, 3: BASE, 5: PRACTICE, 7: REMARK}
for n in [1, 3, 5, 7]:
    T = sp.series(sp.sin(x), x, 0, n + 1).removeO()
    T_num = sp.lambdify(x, T, "numpy")
    pieces = clip_y(xs_t, T_num(xs_t), YR[0], YR[1])
    for piece in pieces:
        p.line(piece, COLORS[n], 1.9)
    # label where the right-hand branch leaves the window
    x_out, y_out = pieces[-1][-1] if len(pieces) > 1 else pieces[0][-1]
    lab = it("T") + SUB[str(n)]
    if y_out > 0:
        p.label(x_out, y_out, lab, 0, -7, COLORS[n], 13, "middle", bold=True)
    else:
        p.label(x_out, y_out, lab, 0, 17, COLORS[n], 13, "middle", bold=True)
p.label(2 * math.pi, 0.0, "sin " + it("x"), 4, -10, TEXT, 12.5,
        bold=True)

save("taylor", figure(
    580, 340, [p],
    "sin <em>x</em> (kalın) ve Taylor polinomları <em>T</em>₁, "
    "<em>T</em>₃, <em>T</em>₅, <em>T</em>₇; Matplotlib kodunun çizdiği "
    "grafiğin aynı verilerle (400 nokta, &#8722;3 &#8804; <em>y</em> "
    "&#8804; 3 penceresi) çizilmiş hâli. Derece arttıkça polinom sinüsü "
    "daha geniş bir aralıkta izler.",
    aria="sin x on [-2 pi, 2 pi] with its Taylor polynomials T1, T3, T5 and "
         "T7 clipped to the window y from -3 to 3; higher degrees follow the "
         "sine curve on wider intervals"))
