# -*- coding: utf-8 -*-
"""
Figures of the chapter "Kök Bulma ve Optimizasyon"
(dersler/python-bilimsel/kok-bulma-ve-optimizasyon.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution,
exercise or callout), never inside a definition box and never directly under
a heading; concept figures stay visible (not inside a collapsed .cozum
block). The figures are NOT produced at build time. The data come from NumPy
and SciPy, so run this script with the course environment:

    taslaklar/python-bilimsel/.venv/Scripts/python.exe \
        scripts/python_figures/kok.py
    python scripts/center_figures.py "python-kok-*.md"
    python scripts/check_figure_labels.py "scripts/_figures/python-kok-*.md"

(set OPENBLAS_NUM_THREADS=1 on this machine) and paste the markup of
scripts/_figures/python-kok-<name>.md into the .qmd. Every figure is drawn
from exactly the data the chapter's code computes: the same functions,
grids, starting points and SciPy calls. Captions are Turkish on purpose;
aria labels are plain ASCII.
"""
import math
import sys
from pathlib import Path

import contourpy
import numpy as np
from scipy.optimize import minimize, newton

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import (Plot, figure, WIDE, TEXT, THEORY, PRACTICE,  # noqa: E402
                      BASE, REMARK, BG)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "python-kok-"

MINUS = "&#8722;"
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


def sub(name, k):
    """Italic letter with a subscript digit: x_0."""
    return it(name) + "".join(SUB[c] for c in str(k))


def dec(v, digits=3):
    """Decimal comma and a true minus sign: -1.8794 -> '−1,879'."""
    s = f"{v:.{digits}f}"
    if float(s) == 0:
        s = s.lstrip("-")
    return s.replace(".", ",").replace("-", MINUS)


def tick(t):
    """Tick label with a true minus sign."""
    s = f"{t:g}"
    return s.replace(".", ",").replace("-", MINUS)


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


def legend_line(p, px, py, color, label, dash=None, dot=True, size=11.5):
    """A short line sample with an optional marker and a label (pixels)."""
    da = f' stroke-dasharray="{dash}"' if dash else ""
    p.add(f'<line x1="{px:.1f}" y1="{py:.1f}" x2="{px + 26:.1f}" '
          f'y2="{py:.1f}" stroke="{color}" stroke-width="1.9"{da}/>')
    if dot:
        p.add(f'<circle cx="{px + 13:.1f}" cy="{py:.1f}" r="3.2" '
              f'fill="{color}"/>')
    p.text_px(px + 34, py + 4, label, TEXT, size)


def swatch(p, px, py, color, label, size=11.5):
    """A small filled square with a label (pixels)."""
    p.add(f'<rect x="{px:.1f}" y="{py - 6:.1f}" width="12" height="12" '
          f'rx="2" fill="{color}" fill-opacity="0.75"/>')
    p.text_px(px + 18, py + 4.5, label, TEXT, size)


def f_cubic(x):
    return x**3 - 3*x + 1


def df_cubic(x):
    return 3*x**2 - 3


# ============================================================
# isaret-tarama: the grid scan of f(x) = x^3 - 3x + 1 (Matplotlib code)
# ============================================================
x_grid = np.linspace(-2.5, 2.5, 11)
y_grid = f_cubic(x_grid)
idx = np.nonzero(y_grid[:-1] * y_grid[1:] < 0)[0]
brackets = list(zip(x_grid[idx], x_grid[idx + 1]))
assert brackets == [(-2.0, -1.5), (0.0, 0.5), (1.5, 2.0)]

p = Plot(62, 46, 430, 250, (-2.6, 2.6), (-8, 10))
for a, b in brackets:
    p.polygon([(a, -8), (b, -8), (b, 10), (a, 10)], BASE, 0.14)
    p.label((a + b) / 2, 10, f"[{tick(a)}; {tick(b)}]", 0, -8, BASE, 11.5,
            "middle", bold=True)
p.axes([-2, -1, 0, 1, 2], [-5, 0, 5, 10], it("x"), "", tick, tick)
p.line([(-2.6, 0), (2.6, 0)], TEXT, 0.9, opacity=0.55)
xx = np.linspace(-2.5, 2.5, 401)
p.line(list(zip(xx, f_cubic(xx))), THEORY, 2.0)
p.points(list(zip(x_grid, y_grid)), PRACTICE, 3.8)
p.label(-1.0, 3.0, it("f") + "(" + it("x") + ") = " + it("x") + sup("3")
        + " " + MINUS + " 3" + it("x") + " + 1", 0, -12, THEORY, 12.5,
        "middle", bold=True)
save("isaret-tarama", figure(
    530, 330, [p],
    "<em>f</em>(<em>x</em>) = <em>x</em>³ &#8722; 3<em>x</em> + 1 "
    "fonksiyonunun grafiği ve adımı 0,5 olan ızgaranın 11 noktası; Matplotlib "
    "kodunun çizdiği grafiğin aynısı. Komşu iki ızgara noktasında işaretin "
    "değiştiği üç aralık gölgelidir: her birinde bir kök vardır.",
    aria="Graph of f(x) = x^3 - 3x + 1 on [-2.5, 2.5] with the 11 grid "
         "points of step 0.5; the three sign-change intervals [-2, -1.5], "
         "[0, 0.5] and [1.5, 2] are shaded"))


# ============================================================
# newton-dongu: Newton's method cycling for f(x) = x^3 - 2x + 2 from x0 = 0
# ============================================================
def f_cyc(x):
    return x**3 - 2*x + 2


def df_cyc(x):
    return 3*x**2 - 2


it_cyc = [0.0]
for _ in range(4):
    x = it_cyc[-1]
    it_cyc.append(x - f_cyc(x) / df_cyc(x))
assert it_cyc == [0.0, 1.0, 0.0, 1.0, 0.0]
root_cyc = -1.7692923542386314

p = Plot(52, 26, 480, 250, (-2.2, 1.8), (-2.5, 4.0))
p.origin_axes(it("x"), it("y"), [-2, -1, 1], [-2, 2, 4], tick, tick)
xx = np.linspace(-2.2, 1.8, 401)
for piece in clip_y(xx, f_cyc(xx), -2.5, 4.0):
    p.line(piece, THEORY, 2.0)
# the arrows run along the two tangents (at x = 0 slope -2, at x = 1 slope
# 1); the dashed piece extends the second one beyond its point of contact
p.line([(1.0, 1.0), (1.6, 1.6)], REMARK, 1.3, "5 3")
p.arrow((0.0, 2.0), (0.96, 0.08), PRACTICE, 1.8, 8)
p.arrow((1.0, 0.0), (1.0, 0.92), PRACTICE, 1.6, 7, dash="3 3")
p.arrow((1.0, 1.0), (0.05, 0.05), PRACTICE, 1.8, 8)
p.arrow((0.0, 0.0), (0.0, 1.92), PRACTICE, 1.6, 7, dash="3 3")
p.points([(0.0, 2.0), (1.0, 1.0)], THEORY, 4.0)
p.points([(0.0, 0.0), (1.0, 0.0)], PRACTICE, 4.2)
p.points([(root_cyc, 0.0)], BASE, 4.6)
p.label(0.0, 0.0, sub("x", 0) + " = 0", -8, 17, PRACTICE, 12, "end",
        bold=True)
p.label(1.0, 0.0, sub("x", 1) + " = 1", 6, 17, PRACTICE, 12, "start",
        bold=True)
p.label(root_cyc, 0.0, "kök " + dec(root_cyc), -9, -9, BASE, 12, "end",
        bold=True)
p.label(1.55, f_cyc(1.55), it("y") + " = " + it("x") + sup("3") + " "
        + MINUS + " 2" + it("x") + " + 2", -8, 0, THEORY, 12, "end",
        bold=True)
save("newton-dongu", figure(
    560, 310, [p],
    "<em>f</em>(<em>x</em>) = <em>x</em>³ &#8722; 2<em>x</em> + 2 için "
    "Newton yöntemi <em>x</em>₀ = 0'dan başlayınca: 0'daki teğet ekseni "
    "1'de, 1'deki teğet ekseni yeniden 0'da keser. İterasyon 0 ile 1 "
    "arasında döner ve &#8722;1,769 civarındaki köke hiç yaklaşmaz.",
    aria="Graph of y = x^3 - 2x + 2 with the tangent at x = 0 hitting the "
         "axis at 1 and the tangent at x = 1 hitting the axis at 0, so "
         "Newton's iterates cycle between 0 and 1; the real root near "
         "-1.769 is marked"))


# ============================================================
# newton-havza: which root Newton reaches from each starting point x0
# ============================================================
roots = np.sort(2 * np.cos(2 * np.pi * np.array([1, 2, 4]) / 9))
root_colors = [THEORY, BASE, PRACTICE]

fine = np.linspace(-3, 3, 1201)
fine = fine[np.abs(df_cubic(fine)) > 1e-9]       # skip f'(x0) = 0 exactly
reached = newton(f_cubic, fine, fprime=df_cubic, maxiter=100)
label = np.argmin(np.abs(reached[:, None] - roots[None, :]), axis=1)
assert np.all(np.abs(reached - roots[label]) < 1e-8)

x0_code = np.linspace(-3, 3, 12)                 # the chapter's 12 points
r_code = newton(f_cubic, x0_code, fprime=df_cubic)
lab_code = np.argmin(np.abs(r_code[:, None] - roots[None, :]), axis=1)

p = Plot(52, 30, 530, 200, (-3.1, 3.1), (-6, 8))
p.origin_axes(it("x"), it("y"), [-3, -2, -1, 1, 2], [-4, 4], tick, tick)
xx = np.linspace(-3, 3, 601)
for piece in clip_y(xx, f_cubic(xx), -6, 8):
    p.line(piece, TEXT, 1.9, opacity=0.8)
STRIP_Y, STRIP_H = 278, 24
for xc in (-1.0, 1.0):
    p.add(f'<line x1="{p.X(xc):.1f}" y1="{p.y0:.1f}" x2="{p.X(xc):.1f}" '
          f'y2="{STRIP_Y + STRIP_H + 4:.1f}" stroke="{TEXT}" '
          f'stroke-width="1" stroke-dasharray="4 3" opacity="0.5"/>')
p.label(1.0, 8, it("f") + "&#8242;(" + it("x") + ") = 0", 6, 8, TEXT, 11.5)
for k, r in enumerate(roots):
    p.points([(r, 0.0)], root_colors[k], 5.0)
# the strip: one coloured cell per starting point of the fine grid
h = 0.005
start = 0
for k in range(1, len(fine) + 1):
    if k == len(fine) or label[k] != label[start] \
            or fine[k] - fine[k - 1] > 1.5 * h:
        xa, xb = fine[start] - h / 2, fine[k - 1] + h / 2
        p.add(f'<rect x="{p.X(xa):.1f}" y="{STRIP_Y}" '
              f'width="{p.X(xb) - p.X(xa):.2f}" height="{STRIP_H}" '
              f'fill="{root_colors[label[start]]}" fill-opacity="0.75"/>')
        start = k
p.add(f'<rect x="{p.X(-3 - h / 2):.1f}" y="{STRIP_Y}" '
      f'width="{p.X(3 + h / 2) - p.X(-3 - h / 2):.1f}" height="{STRIP_H}" '
      f'fill="none" stroke="{TEXT}" stroke-width="0.8" stroke-opacity="0.5"/>')
for a, k in zip(x0_code, lab_code):
    p.add(f'<circle cx="{p.X(a):.1f}" cy="{STRIP_Y + STRIP_H + 11:.1f}" '
          f'r="3.6" fill="{root_colors[k]}"/>')
p.text_px(p.X(3.1) + 4, STRIP_Y + STRIP_H / 2 + 5, sub("x", 0), TEXT, 13,
          "start", italic=False)
p.text_px(p.X(-3) - 2, STRIP_Y - 9, "başlangıç noktası " + sub("x", 0)
          + ", Newton'un vardığı kökün rengiyle", TEXT, 11.5)
LEG_Y = STRIP_Y + STRIP_H + 36
p.text_px(p.X(-3) - 2, LEG_Y + 4.5, "kökler:", TEXT, 11.5)
for k, r in enumerate(roots):
    swatch(p, p.X(-3) + 52 + 86 * k, LEG_Y, root_colors[k], dec(r), 12)
save("newton-havza", figure(
    620, 380, [p],
    "Üstte <em>f</em>(<em>x</em>) = <em>x</em>³ &#8722; 3<em>x</em> + 1 ve "
    "üç kökü. Alttaki şeritte [&#8722;3; 3] aralığındaki her <em>x</em>₀ "
    "başlangıç noktası, <code>newton</code> fonksiyonunun oradan vardığı "
    "kökün rengine boyanmıştır (1201 noktalık ızgara); şeridin altındaki "
    "12 nokta, metindeki kodun başlangıç noktalarıdır. Türevin sıfır olduğu "
    "<em>x</em> = ±1 yakınında renkler birbirine karışır.",
    aria="Graph of f(x) = x^3 - 3x + 1 with its roots -1.879, 0.347 and "
         "1.532, and below it a strip over [-3, 3] coloured by the root "
         "Newton's method reaches from each starting point; the colours mix "
         "near x = -1 and x = 1 where f' vanishes"))


# ============================================================
# yakinsama-hizi: errors of bisection, secant and Newton (semilog)
# ============================================================
p_true = 2 * math.cos(2 * math.pi / 9)
bis, a, b = [], 1.5, 2.0
for _ in range(6):
    m = (a + b) / 2
    bis.append(m)
    if f_cubic(a) * f_cubic(m) < 0:
        b = m
    else:
        a = m
sec = [2.0, 1.9]
for _ in range(6):
    u, v = sec[-2], sec[-1]
    sec.append(v - f_cubic(v) * (v - u) / (f_cubic(v) - f_cubic(u)))
nwt = [2.0]
for _ in range(6):
    x = nwt[-1]
    nwt.append(x - f_cubic(x) / df_cubic(x))

# row n = error after n steps; the n-th secant step produces x_(n+1)
ns = range(1, 7)
e_bis = [abs(bis[n - 1] - p_true) for n in ns]
e_sec = [abs(sec[n + 1] - p_true) for n in ns]
e_nwt = [abs(nwt[n] - p_true) for n in ns]
assert e_nwt[-1] == 0.0          # the last Newton step is exact: not drawn


def log_pts(errs):
    return [(n, math.log10(e)) for n, e in zip(ns, errs) if e > 0]


def ylog(t):
    return "1" if t == 0 else "10" + sup(MINUS + str(int(-t)))


p = Plot(70, 24, 400, 270, (0.7, 6.3), (-16, 0))
p.grid(ys=[-4, -8, -12])
p.axes(list(ns), [0, -4, -8, -12, -16], it("n"), "hata", tick, ylog)
bound = [(n, math.log10(0.5 / 2**n)) for n in ns]
p.line(bound, TEXT, 1.3, "5 4", opacity=0.75)
for errs, color in [(e_bis, THEORY), (e_sec, BASE), (e_nwt, PRACTICE)]:
    pts = log_pts(errs)
    p.line(pts, color, 2.0)
    p.points(pts, color, 3.8)
LX, LY = p.X(1.0), p.Y(-9.2)
legend_line(p, LX, LY, THEORY, "ikiye bölme")
legend_line(p, LX, LY + 22, BASE, "sekant")
legend_line(p, LX, LY + 44, PRACTICE, "Newton")
legend_line(p, LX, LY + 66, TEXT, "sınır (" + it("b") + " " + MINUS + " "
            + it("a") + ")/2" + sup(it("n")), dash="5 4", dot=False)
save("yakinsama-hizi", figure(
    500, 340, [p],
    "Aynı kök (<em>x</em>³ &#8722; 3<em>x</em> + 1 = 0'ın 1,532 civarındaki "
    "kökü) için üç yöntemin <em>n</em> adım sonraki hatası, logaritmik "
    "ölçekte; tablodaki sayıların aynısı. İkiye bölmenin hatası sınırın "
    "altında kalır ama inişi yavaştır; sekantın ve Newton'un eğrisi giderek "
    "dikleşir. Newton'un hatası 0 olan 6. adımı çizilmedi.",
    aria="Semilog plot of the error after n = 1..6 steps for "
         "bisection, secant and Newton on the root 1.532 of x^3 - 3x + 1, "
         "with the dashed bisection bound (b - a)/2^n; the secant reaches "
         "8e-11 and Newton 1e-14 after 6 and 5 steps"))


# ============================================================
# sistem: x^2 + y^2 = 4 and e^x + y = 1, Newton paths from two starts
# ============================================================
def F_sys(v):
    x, y = v
    return np.array([x**2 + y**2 - 4, np.exp(x) + y - 1])


def J_sys(v):
    x, y = v
    return np.array([[2*x, 2*y], [np.exp(x), 1.0]])


def newton_path(start, steps=6):
    v = np.array(start, dtype=float)
    pts = [v]
    for _ in range(steps):
        v = v + np.linalg.solve(J_sys(v), -F_sys(v))
        pts.append(v)
    return np.array(pts)


path_a = newton_path([1.0, -1.0])
path_b = newton_path([-1.0, 1.0])
sol_a, sol_b = path_a[-1], path_b[-1]

p = Plot(40, 24, 396, 360, (-3.6, 3), (-3, 3))
p.origin_axes(it("x"), it("y"), [-3, -1, 1], [-1, 1], tick,
              tick)
p.circle(0, 0, 2, THEORY, 2.0)
xe = np.linspace(-3.6, math.log(4), 300)
p.line(list(zip(xe, 1 - np.exp(xe))), BASE, 2.0)
for path in (path_a, path_b):
    # the first Newton step as an arrow, the next two iterates as dots
    p.arrow(tuple(path[0]), tuple(path[1]), PRACTICE, 1.4, 7, dash="4 3",
            opacity=0.9)
    p.line([tuple(q) for q in path[1:4]], PRACTICE, 1.2, "3 3", 0.9)
    p.points([tuple(q) for q in path[1:3]], PRACTICE, 2.6)
p.hollow_points([tuple(path_a[0]), tuple(path_b[0])], TEXT, 4.2)
p.points([tuple(sol_a), tuple(sol_b)], PRACTICE, 5.0)
p.label(*path_a[0], "(1; " + MINUS + "1)", -8, 4, TEXT, 11.5, "end")
p.label(*path_b[0], "(" + MINUS + "1; 1)", 4, -9, TEXT, 11.5, "start")
p.label(*sol_a, f"({dec(sol_a[0])}; {dec(sol_a[1])})", 14, 14, PRACTICE,
        12, "start", True)
p.label(-2.75, 1.3, f"({dec(sol_b[0])}; {dec(sol_b[1])})", 0, 0, PRACTICE,
        12, "middle", True)
p.line([(-2.45, 1.2), (sol_b[0] - 0.08, sol_b[1] + 0.06)], TEXT, 0.9,
       opacity=0.6)
p.label(1.414, 1.414, it("x") + sup("2") + " + " + it("y") + sup("2")
        + " = 4", 6, -6, THEORY, 12.5, "start", True)
p.label(1.25, 1 - math.exp(1.25), it("e") + sup(it("x")) + " + " + it("y")
        + " = 1", 10, 4, BASE, 12.5, "start", True)
save("sistem", figure(
    470, 420, [p],
    "<em>x</em>² + <em>y</em>² = 4 çemberi ile <em>e</em><sup><em>x</em>"
    "</sup> + <em>y</em> = 1 eğrisinin iki kesişim noktası. Kesikli oklar "
    "Newton yönteminin (1; &#8722;1) ve (&#8722;1; 1) başlangıç noktalarından "
    "attığı ilk adımlardır; her başlangıç kendisine yakın olan çözüme gider.",
    aria="The circle x^2 + y^2 = 4 and the curve y = 1 - e^x meeting at "
         "(1.004, -1.730) and (-1.816, 0.837); dashed arrows show the first "
         "Newton steps from the starting points (1, -1) and (-1, 1)"))


# ============================================================
# iki-minimum: f(x) = x^4 - 4x^2 + x and what minimize_scalar finds
# ============================================================
def g4(x):
    return x**4 - 4*x**2 + x


crit = np.sort(np.real(np.roots([4, 0, -8, 1])))
x_glob, x_max, x_loc = crit
p = Plot(56, 30, 510, 270, (-2.4, 2.4), (-7.6, 6))
p.origin_axes(it("x"), it("y"), [-2, -1, 1, 2], [-4, -2, 2, 4], tick, tick)
xx = np.linspace(-2.4, 2.4, 481)
for piece in clip_y(xx, g4(xx), -7.6, 6):
    p.line(piece, THEORY, 2.0)
p.add(f'<line x1="{p.X(0):.1f}" y1="{p.Y(-7.6) + 30:.1f}" '
      f'x2="{p.X(2.4):.1f}" y2="{p.Y(-7.6) + 30:.1f}" stroke="{BASE}" '
      f'stroke-width="5" stroke-opacity="0.45" stroke-linecap="round"/>')
p.text_px(p.X(1.2), p.Y(-7.6) + 22, "bounds=(0, 3)", BASE, 11.5, "middle")
p.points([(x_glob, g4(x_glob))], PRACTICE, 5.0)
p.points([(x_loc, g4(x_loc))], BASE, 5.0)
p.points([(x_max, g4(x_max))], TEXT, 3.6)
p.label(x_glob, g4(x_glob), "mutlak minimum", 0, 22, PRACTICE, 12,
        "middle", True)
p.label(x_glob, g4(x_glob), f"({dec(x_glob)}; {dec(g4(x_glob))})", 0, 37,
        PRACTICE, 11.5, "middle")
p.label(x_loc, g4(x_loc), "yerel minimum", 0, 22, BASE, 12, "middle",
        True)
p.label(x_loc, g4(x_loc), f"({dec(x_loc)}; {dec(g4(x_loc))})", 0, 37,
        BASE, 11.5, "middle")
p.label(x_max, g4(x_max), "yerel maksimum", 8, -10, TEXT, 11.5, "start")
p.label(-1.9, 4.2, it("f") + "(" + it("x") + ") = " + it("x")
        + sup("4") + " " + MINUS + " 4" + it("x") + sup("2") + " + "
        + it("x"), 0, 0, THEORY, 12.5, "start", True)
save("iki-minimum", figure(
    600, 370, [p],
    "<em>f</em>(<em>x</em>) = <em>x</em><sup>4</sup> &#8722; 4<em>x</em>² + "
    "<em>x</em> fonksiyonunun iki yerel minimumu. <code>bracket=(-3, -2)</code>"
    " ile yapılan arama soldaki mutlak minimumu, varsayılan arama ve "
    "<code>bounds=(0, 3)</code> ile yapılan arama sağdaki yerel minimumu "
    "bulur.",
    aria="Graph of f(x) = x^4 - 4x^2 + x with the absolute minimum near "
         "(-1.473, -5.444), the local maximum near (0.126, 0.063) and the "
         "local minimum near (1.347, -2.619); the interval (0, 3) used as "
         "bounds is marked under the axis"))


# ============================================================
# rosenbrock-yollari: Nelder-Mead and BFGS paths on Rosenbrock's valley
# ============================================================
def rosen(v):
    x, y = v
    return (1 - x)**2 + 100 * (y - x**2)**2


def rosen_grad(v):
    x, y = v
    return np.array([-2 * (1 - x) - 400 * x * (y - x**2),
                     200 * (y - x**2)])


x0_r = np.array([-1.2, 1.0])
paths = {}
for method, jac in [("Nelder-Mead", None), ("BFGS", rosen_grad)]:
    path = [x0_r]
    minimize(rosen, x0_r, method=method, jac=jac,
             callback=lambda xk: path.append(xk.copy()))
    paths[method] = np.array(path)
assert len(paths["Nelder-Mead"]) == 85 and len(paths["BFGS"]) == 33

XR, YR = (-1.5, 1.5), (-0.5, 1.5)
gx = np.linspace(*XR, 301)
gy = np.linspace(*YR, 201)
GX, GY = np.meshgrid(gx, gy)
GZ = (1 - GX)**2 + 100 * (GY - GX**2)**2
gen = contourpy.contour_generator(GX, GY, GZ)
levels = [1, 4, 16, 64, 256]

panels = []
for k, (method, color, title) in enumerate([
        ("Nelder-Mead", BASE, "Nelder–Mead: 85 nokta"),
        ("BFGS", PRACTICE, "BFGS, gradyanlı: 33 nokta")]):
    q = Plot(40 + k * 330, 40, 285, 190, XR, YR)
    q.axes([-1, 0, 1], [0, 1], it("x"), it("y"), tick, tick)
    for lev in levels:
        for line in gen.lines(lev):
            q.line([tuple(pt) for pt in line], TEXT, 0.9, opacity=0.35)
    xv = np.linspace(-1.2, 1.2, 121)
    q.line(list(zip(xv, xv**2)), TEXT, 0.9, "2 3", opacity=0.6)
    P = paths[method]
    q.line([tuple(pt) for pt in P], color, 1.7)
    q.points([tuple(pt) for pt in P[1:-1]], color, 2.0)
    q.hollow_points([tuple(P[0])], TEXT, 4.4)
    q.points([(1.0, 1.0)], TEXT, 4.4)
    q.label(1.0, 1.0, "(1; 1)", 10, 4, TEXT, 11.5, "start")
    q.text_px(q.x0 + q.w / 2, q.y0 - 18, title, color, 12.5, "middle", True)
    panels.append(q)
save("rosenbrock-yollari", figure(
    680, 280, panels,
    "Rosenbrock fonksiyonunun eş yükselti eğrileri (<em>f</em> = 1, 4, 16, "
    "64, 256) ve kesikli <em>y</em> = <em>x</em>² vadisi. Solda Nelder–Mead "
    "yönteminin, sağda gradyanı verilen BFGS yönteminin callback ile "
    "kaydedilen noktaları; ikisi de içi boş daireyle gösterilen "
    "(&#8722;1,2; 1) noktasından başlayıp muz biçimli vadiyi izleyerek "
    "(1; 1) minimumuna varır.",
    css_class=WIDE,
    aria="Two panels with the contour lines of the Rosenbrock function and "
         "the valley y = x^2: left the 85 points of Nelder-Mead, right the "
         "33 points of BFGS with gradient, both going from (-1.2, 1) along "
         "the curved valley to the minimum (1, 1)"))


# ============================================================
# kisitli: (x-2)^2 + (y-1)^2 on the triangle x + y <= 2, x, y >= 0
# ============================================================
opt = np.array([1.5, 0.5])
p = Plot(40, 24, 340, 340, (-0.5, 3.0), (-0.5, 3.0))
p.origin_axes(it("x"), it("y"), [1, 2], [1, 2], tick, tick)
p.polygon([(0, 0), (2, 0), (0, 2)], THEORY, 0.16, THEORY, 1.4)
p.line([(-0.4, 2.4), (2.4, -0.4)], THEORY, 1.2, "5 4", opacity=0.8)
for rad in (0.3, 1.0, 1.4):
    p.circle(2, 1, rad, TEXT, 1.0, "4 3", opacity=0.55)
p.circle(2, 1, math.sqrt(0.5), PRACTICE, 1.8)
p.hollow_points([(2.0, 1.0)], TEXT, 4.2)
p.arrow(tuple(opt), (2.0, 1.0), BASE, 1.8, 8)
p.points([tuple(opt)], PRACTICE, 5.0)
p.label(2.0, 1.0, "(2; 1)", 8, -8, TEXT, 11.5, "start")
p.label(*opt, "(1,5; 0,5)", -10, 16, PRACTICE, 12, "end", True)
p.label(1.75, 0.75, MINUS + "&#8711;" + it("f"), 9, 14, BASE, 12.5,
        "start", True)
p.label(0.45, 0.6, "uygun", 0, 0, THEORY, 12, "middle", True)
p.label(0.45, 0.6, "bölge", 0, 15, THEORY, 12, "middle", True)
p.label(-0.2, 2.2, it("x") + " + " + it("y") + " = 2", 10, -6, THEORY,
        12, "start", True)
save("kisitli", figure(
    410, 400, [p],
    "Uygun bölge <em>x</em> + <em>y</em> &#8804; 2, <em>x</em>, <em>y</em> "
    "&#8805; 0 üçgenidir. Kesikli çemberler (2; 1) merkezli eş yükselti "
    "eğrileridir; minimum, üçgene değen en küçük çemberin değme noktası "
    "(1,5; 0,5)'tir. Orada &#8722;&#8711;<em>f</em> = (1; 1) vektörü "
    "<em>x</em> + <em>y</em> = 2 doğrusuna diktir.",
    aria="The feasible triangle with x + y at most 2 and x, y nonnegative, "
         "dashed level "
         "circles of (x-2)^2 + (y-1)^2 around (2, 1), and the solid circle "
         "of radius sqrt(0.5) touching the triangle at the optimum "
         "(1.5, 0.5), where -grad f points to (2, 1) perpendicular to the "
         "line x + y = 2"))
