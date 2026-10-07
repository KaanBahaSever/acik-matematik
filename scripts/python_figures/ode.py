# -*- coding: utf-8 -*-
"""
Figures of the chapter "Diferansiyel Denklemlerin Sayısal Çözümü"
(dersler/python-bilimsel/diferansiyel-denklemlerin-sayisal-cozumu.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution,
exercise or callout), never inside a definition box and never directly under
a heading; concept figures stay visible (not inside a collapsed .cozum
block). The figures are NOT produced at build time. The data come from NumPy
and SciPy, so run this script with the course environment:

    taslaklar/python-bilimsel/.venv/Scripts/python.exe \
        scripts/python_figures/ode.py
    python scripts/center_figures.py "python-ode-*.md"
    python scripts/check_figure_labels.py "scripts/_figures/python-ode-*.md"

(set OPENBLAS_NUM_THREADS=1 on this machine) and paste the markup of
scripts/_figures/python-ode-<name>.md into the .qmd. Every figure is drawn
from exactly the data the chapter's code computes: the same equations, step
sizes, tolerances and initial values. Captions are Turkish on purpose; aria
labels are plain ASCII.
"""
import math
import sys
from pathlib import Path

import numpy as np
from scipy.integrate import solve_ivp

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import (Plot, figure, WIDE, TEXT, THEORY, PRACTICE,  # noqa: E402
                      BASE, REMARK, BG)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "python-ode-"

MINUS = "&#8722;"
SUB = {str(k): chr(0x2080 + k) for k in range(10)}
TIGHT = dict(rtol=1e-10, atol=1e-12)


def save(name, markup):
    (OUT_DIR / f"{PREFIX}{name}.md").write_text(markup, encoding="utf-8",
                                                newline="\n")
    print(f"{PREFIX}{name}.md")


def it(s):
    """Italic run inside an SVG <text>."""
    return f'<tspan font-style="italic">{s}</tspan>'


def sup(s, size=10.5):
    """Superscript inside an SVG <text>."""
    return (f'<tspan font-size="{size}" dy="-5">{s}</tspan>'
            f'<tspan dy="5">&#8203;</tspan>')


def sub(name, k):
    """Italic letter with a subscript digit: k_1."""
    return it(name) + "".join(SUB[c] for c in str(k))


def dec(v, digits=3):
    """Decimal comma and a true minus sign: -1.8794 -> '−1,879'."""
    s = f"{v:.{digits}f}"
    if float(s) == 0:
        s = s.lstrip("-")
    return s.replace(".", ",").replace("-", MINUS)


def tick(t):
    """Tick label with a decimal comma and a true minus sign."""
    s = f"{t:g}"
    return s.replace(".", ",").replace("-", MINUS)


def clip_y(xs, ys, lo, hi):
    """Split the polyline (xs, ys) into pieces inside lo <= y <= hi."""
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


def legend_line(p, px, py, color, label, dash=None, dot=False, size=12,
                width=1.9):
    """A short line sample with an optional marker and a label (pixels)."""
    da = f' stroke-dasharray="{dash}"' if dash else ""
    p.add(f'<line x1="{px:.1f}" y1="{py:.1f}" x2="{px + 24:.1f}" '
          f'y2="{py:.1f}" stroke="{color}" stroke-width="{width}"{da}/>')
    if dot:
        p.add(f'<circle cx="{px + 12:.1f}" cy="{py:.1f}" r="3.2" '
              f'fill="{color}"/>')
    p.text_px(px + 31, py + 4, label, TEXT, size)


def slope_mark(p, x, y, s, length, color, width=2.4, opacity=1.0):
    """A short segment of slope s centred at the data point (x, y).

    The length is given in pixels, so the mark has the same size wherever
    it sits and its direction is the slope as seen on the page.
    """
    sx = p.w / (p.xmax - p.xmin)
    sy = p.h / (p.ymax - p.ymin)
    vx, vy = sx, -sy * s
    norm = math.hypot(vx, vy)
    dx, dy = vx / norm * length / 2, vy / norm * length / 2
    X, Y = p.X(x), p.Y(y)
    p.add(f'<line x1="{X - dx:.1f}" y1="{Y - dy:.1f}" x2="{X + dx:.1f}" '
          f'y2="{Y + dy:.1f}" stroke="{color}" stroke-width="{width}" '
          f'opacity="{opacity}" stroke-linecap="round"/>')


def euler(f, t0, y0, h, n):
    """Same algorithm as the chapter's euler (odetools.py)."""
    t = t0 + h * np.arange(n + 1)
    y = np.zeros((n + 1,) + np.shape(y0))
    y[0] = y0
    for k in range(n):
        y[k + 1] = y[k] + h * f(t[k], y[k])
    return t, y


def rk4(f, t0, y0, h, n):
    """Same algorithm as the chapter's rk4 (odetools.py)."""
    t = t0 + h * np.arange(n + 1)
    y = np.zeros((n + 1,) + np.shape(y0))
    y[0] = y0
    for k in range(n):
        k1 = f(t[k], y[k])
        k2 = f(t[k] + h / 2, y[k] + h / 2 * k1)
        k3 = f(t[k] + h / 2, y[k] + h / 2 * k2)
        k4 = f(t[k] + h, y[k] + h * k3)
        y[k + 1] = y[k] + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
    return t, y


# ============================================================
# yon-alani: direction field of y' = t - y^2 with solution curves
# ============================================================
def f_riccati(t, y):
    return t - y**2


TR, YR = (0.0, 3.0), (-1.6, 2.2)
p = Plot(58, 30, 450, 290, TR, YR)
p.axes([0, 0.5, 1, 1.5, 2, 2.5, 3], [-1.5, -1, -0.5, 0, 0.5, 1, 1.5, 2],
       it("t"), it("y"), tick, tick)
p.line([(0, 0), (3, 0)], TEXT, 0.8, opacity=0.35)
for tg in np.arange(0.125, 3.0, 0.25):
    for yg in np.arange(-1.5, 2.01, 0.25):
        slope_mark(p, tg, yg, f_riccati(tg, yg), 12, TEXT, 1.2, 0.55)
# the isocline t = y^2 (slope 0)
yy = np.linspace(-math.sqrt(3), math.sqrt(3), 121)
p.line(list(zip(yy**2, yy)), REMARK, 1.4, "6 4")
p.label(2.3, -1.12, it("t") + " = " + it("y") + sup("2"), 0, 0, REMARK,
        12.5, "start", bold=True)


def below(t, y):
    return y[0] - YR[0]


below.terminal = True
for y0 in [-1.0, -0.8, -0.6, 0.8, 1.6, 2.2]:
    s = solve_ivp(f_riccati, TR, [y0], events=below, dense_output=True,
                  **TIGHT)
    tt = np.linspace(0, s.t[-1], 300)
    for piece in clip_y(tt, s.sol(tt)[0], *YR):
        p.line(piece, BASE, 1.5, opacity=0.9)
s0 = solve_ivp(f_riccati, TR, [0.0], dense_output=True, **TIGHT)
tt = np.linspace(0, 3, 300)
p.line(list(zip(tt, s0.sol(tt)[0])), THEORY, 2.6)
y2 = float(s0.sol(2.0)[0])
assert abs(y2 - 1.1935759753) < 1e-9
p.points([(0.0, 0.0), (2.0, y2)], THEORY, 4.6)
p.line([(2.0, y2), (2.28, 0.62)], THEORY, 1.0, opacity=0.8)
p.label(2.28, 0.62, it("y") + "(2) &#8776; " + dec(y2, 4), -4, 16, THEORY,
        12.5, "start", bold=True)
save("yon-alani", figure(
    640, 380, [p],
    "<em>y</em>&#8242; = <em>t</em> &#8722; <em>y</em>² denkleminin yön "
    "alanı: her kısa çizgi, bulunduğu noktadaki eğimi gösterir. Kalın eğri "
    "<em>y</em>(0) = 0 koşulunu sağlayan çözümdür; ince eğriler başka "
    "başlangıç değerlerinden çıkan çözümlerdir. Kesikli <em>t</em> = "
    "<em>y</em>² parabolü üzerinde eğim sıfırdır: parabolün içinde "
    "çözümler artar, dışında azalır.",
    aria="Direction field of y' = t - y^2 on [0, 3] x [-1.6, 2.2] with the "
         "dashed isocline t = y^2, the bold solution through (0, 0) that "
         "reaches (2, 1.1936), and thinner solutions from other initial "
         "values; those starting at -0.8 or lower fall out of the window"))


# ============================================================
# euler-poligon: Euler's method for y' = y, h = 0.25
# ============================================================
t_e, y_e = euler(lambda t, y: y, 0.0, 1.0, 0.25, 4)
assert abs(y_e[-1] - 2.44140625) < 1e-15

p = Plot(58, 24, 450, 270, (0.0, 1.14), (0.8, 2.95))
p.axes([0, 0.25, 0.5, 0.75, 1], [1, 1.5, 2, 2.5], it("t"), it("y"),
       tick, tick)
for tk, yk in zip(t_e[1:], y_e[1:]):
    tt = np.linspace(tk, 1.08, 60)
    p.line(list(zip(tt, yk * np.exp(tt - tk))), REMARK, 1.2, "4 3", 0.9)
tt = np.linspace(0, 1.08, 200)
p.line(list(zip(tt, np.exp(tt))), THEORY, 2.4)
p.line(list(zip(t_e, y_e)), PRACTICE, 2.2)
p.points(list(zip(t_e, y_e)), PRACTICE, 4.4)
p.points([(1.0, math.e)], THEORY, 4.4)
# the error at t = 1
X1 = p.X(1.0) + 14
p.add(f'<line x1="{X1:.1f}" y1="{p.Y(math.e):.1f}" x2="{X1:.1f}" '
      f'y2="{p.Y(y_e[-1]):.1f}" stroke="{TEXT}" stroke-width="1.2"/>')
for yv in (math.e, y_e[-1]):
    p.add(f'<line x1="{X1 - 4:.1f}" y1="{p.Y(yv):.1f}" x2="{X1 + 4:.1f}" '
          f'y2="{p.Y(yv):.1f}" stroke="{TEXT}" stroke-width="1.2"/>')
p.text_px(X1 + 7, (p.Y(math.e) + p.Y(y_e[-1])) / 2 + 4,
          "hata " + dec(math.e - y_e[-1], 3), TEXT, 12)
p.label(0.62, math.exp(0.62), it("y") + " = " + it("e") + sup(it("t")),
        -8, -10, THEORY, 13, "end", bold=True)
p.label(0.78, 1.42, "Euler, " + it("h") + " = 0,25", 0, 0, PRACTICE,
        12.5, "start", bold=True)
for k in (1, 2, 3, 4):
    p.label(t_e[k], y_e[k], sub("y", k), 4, 18, PRACTICE, 12, "start")
p.label(0.0, 1.0, sub("y", 0), 6, 18, PRACTICE, 12, "start")
save("euler-poligon", figure(
    640, 340, [p],
    "<em>y</em>&#8242; = <em>y</em>, <em>y</em>(0) = 1 problemine "
    "<em>h</em> = 0,25 ile dört Euler adımı. Her adım, bulunduğu noktadan "
    "geçen çözümün teğeti boyunca ilerler; kesikli eğriler bu çözümlerdir "
    "(<em>y</em> = <em>y<sub>i</sub></em><em>e</em><sup><em>t</em> &#8722; "
    "<em>t<sub>i</sub></em></sup>). Yöntem her adımda bir alttaki çözüme "
    "atlar ve hatalar birikir: <em>t</em> = 1'de 2,4414 değeri "
    "<em>e</em> &#8776; 2,7183'ün 0,277 altında kalır.",
    aria="Euler polygon for y' = y with h = 0.25 from (0, 1) through "
         "1.25, 1.5625, 1.9531 to 2.4414 at t = 1, below the curve e^t "
         "which reaches 2.7183; dashed curves are the solutions through each "
         "Euler point and the error 0.277 at t = 1 is marked"))


# ============================================================
# rk4-egimler: the four slopes of one RK4 step, y' = y, h = 1
# ============================================================
h = 1.0
k1 = 1.0
k2 = 1.0 + h / 2 * k1
k3 = 1.0 + h / 2 * k2
k4 = 1.0 + h * k3
y1 = 1.0 + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
assert (k1, k2, k3, k4) == (1.0, 1.5, 1.75, 2.75)
assert abs(y1 - rk4(lambda t, y: y, 0.0, 1.0, 1.0, 1)[1][-1]) < 1e-15
assert abs(y1 - 2.708333333333333) < 1e-12

p = Plot(58, 24, 450, 290, (0.0, 1.5), (0.8, 3.05))
p.axes([0, 0.5, 1], [1, 1.5, 2, 2.5, 3], it("t"), it("y"), tick, tick)
tt = np.linspace(0, 1.1, 200)
p.line(list(zip(tt, np.exp(tt))), THEORY, 2.0, opacity=0.8)
p.vline(0.5, 0.8, 1.75)
p.vline(1.0, 0.8, 2.75)
# the predictor lines that produce the sample points
p.line([(0, 1), (0.5, 1 + 0.5 * k1)], TEXT, 1.1, "4 3", 0.7)
p.line([(0, 1), (0.5, 1 + 0.5 * k2)], TEXT, 1.1, "4 3", 0.7)
p.line([(0, 1), (1.0, 1 + k3)], TEXT, 1.1, "4 3", 0.7)
# the final step with the weighted slope, and Euler's step for comparison
p.line([(0, 1), (1.0, 2.0)], PRACTICE, 1.6, "7 4")
p.line([(0, 1), (1.0, y1)], BASE, 2.4)
samples = [(0.0, 1.0, k1), (0.5, 1.5, k2), (0.5, 1.75, k3), (1.0, 2.75, k4)]
for x, y, s in samples:
    slope_mark(p, x, y, s, 28 if x > 0 else 22, REMARK, 3.0)
    p.points([(x, y)], REMARK, 3.6)
p.label(0.0, 1.0, sub("k", 1) + " = 1", 4, 22, REMARK, 12.5, "start",
        bold=True)
p.label(0.5, 1.5, sub("k", 2) + " = 1,5", 10, 17, REMARK, 12.5, "start",
        bold=True)
p.label(0.5, 1.75, sub("k", 3) + " = 1,75", -10, -9, REMARK, 12.5, "end",
        bold=True)
p.label(1.0, 2.75, sub("k", 4) + " = 2,75", -10, -11, REMARK, 12.5, "end",
        bold=True)
p.points([(1.0, y1)], BASE, 4.6)
p.points([(1.0, 2.0)], PRACTICE, 4.4)
p.label(1.0, y1, "RK4: " + dec(y1, 4), 12, 16, BASE, 12.5, "start",
        bold=True)
p.label(1.0, math.e, it("e") + " &#8776; " + dec(math.e, 4), 12, -4, THEORY,
        12.5, "start", bold=True)
p.label(1.0, 2.0, "Euler: 2", 10, 4, PRACTICE, 12.5, "start", bold=True)
p.label(1.1, math.exp(1.1), it("y") + " = " + it("e") + sup(it("t")), 6, 8,
        THEORY, 12.5, "start", bold=True)
save("rk4-egimler", figure(
    660, 360, [p],
    "<em>y</em>&#8242; = <em>y</em>, <em>y</em>(0) = 1 için tek bir RK4 "
    "adımı (<em>h</em> = 1). Eğim dört noktada ölçülür: başta "
    "(<em>k</em>₁ = 1), ortada iki kez (<em>k</em>₂ = 1,5 ve "
    "<em>k</em>₃ = 1,75) ve sonda (<em>k</em>₄ = 2,75); kesikli doğrular bu "
    "noktaların nasıl bulunduğunu gösterir. Ağırlıklı ortalama eğimle atılan "
    "adım 2,7083'e varır ve <em>e</em> &#8776; 2,7183'e çok yaklaşır; aynı "
    "adımı Euler yöntemi 2'de bitirir.",
    aria="One RK4 step of size 1 for y' = y from (0, 1): slope marks at "
         "(0, 1) with k1 = 1, at (0.5, 1.5) with k2 = 1.5, at (0.5, 1.75) "
         "with k3 = 1.75 and at (1, 2.75) with k4 = 2.75; the RK4 step ends "
         "at 2.7083 next to e = 2.7183, Euler's step ends at 2"))


# ============================================================
# hata-adim: global error at t = 4 vs h, logistic equation (log-log)
# ============================================================
def f_log(t, y):
    return y * (1 - y)


def exact_log(t):
    return 1 / (1 + 9 * np.exp(-t))


T = 4.0
ns = 2 ** np.arange(3, 11)
hs = T / ns
err_e = np.array([abs(euler(f_log, 0, 0.1, T / n, n)[1][-1] - exact_log(T))
                  for n in ns])
err_r = np.array([abs(rk4(f_log, 0, 0.1, T / n, n)[1][-1] - exact_log(T))
                  for n in ns])
p_e = np.polyfit(np.log(hs), np.log(err_e), 1)[0]
p_r = np.polyfit(np.log(hs), np.log(err_r), 1)[0]
assert f"{p_e:.3f}" == "1.067" and f"{p_r:.3f}" == "3.990"
assert f"{err_e[0]:.3e}" == "1.349e-02" and f"{err_r[-1]:.3e}" == "2.286e-13"


def xlog(v):
    return "10" + sup(MINUS + str(int(-v))) if v < 0 else "1"


lh = np.log10(hs)
p = Plot(78, 24, 440, 270, (-2.55, -0.15), (-13.2, -1.2))
p.grid([-2, -1], [-12, -9, -6, -3])
p.axes([-2, -1], [-12, -9, -6, -3], it("h"), "hata", xlog, xlog)
p.line(list(zip(lh, np.log10(0.05 * hs))), TEXT, 1.0, "6 4", 0.75)
p.line(list(zip(lh, np.log10(0.002 * hs**4))), TEXT, 1.0, "2 3", 0.85)
p.line(list(zip(lh, np.log10(err_e))), PRACTICE, 2.0)
p.points(list(zip(lh, np.log10(err_e))), PRACTICE, 3.8)
p.line(list(zip(lh, np.log10(err_r))), BASE, 2.0)
for x, y in zip(lh, np.log10(err_r)):
    p.add(f'<rect x="{p.X(x) - 3.5:.1f}" y="{p.Y(y) - 3.5:.1f}" width="7" '
          f'height="7" fill="{BASE}"/>')
p.label(lh[3], math.log10(err_e[3]), "Euler", 0, 20, PRACTICE, 13,
        "middle", bold=True)
p.label(lh[4], math.log10(err_r[4]), "RK4", 12, 16, BASE, 13, "start",
        bold=True)
p.label(lh[6], math.log10(0.05 * hs[6]), "eğim 1", 0, -9, TEXT, 12,
        "middle")
p.label(lh[6], math.log10(0.002 * hs[6] ** 4), "eğim 4", 10, 12, TEXT, 12,
        "start")
save("hata-adim", figure(
    600, 340, [p],
    "<em>y</em>&#8242; = <em>y</em>(1 &#8722; <em>y</em>), <em>y</em>(0) = "
    "0,1 probleminde <em>t</em> = 4'teki hatanın adım uzunluğuna göre "
    "değişimi; Matplotlib kodunun çizdiği log-log grafiğin aynı verilerle "
    "çizilmiş hâli (<em>h</em> = 4/<em>n</em>, <em>n</em> = 8, 16, …, 1024). "
    "Euler'in noktaları eğimi 1, RK4'ünkiler eğimi 4 olan kesikli ve "
    "noktalı doğrulara paraleldir: adımı yarıya indirmek Euler'in hatasını "
    "yarıya, RK4'ün hatasını on altıda bire indirir.",
    aria="Log-log plot of the error at t = 4 against the step size h from "
         "0.0039 to 0.5 for the logistic equation: Euler's errors fall from "
         "1.3e-2 to 7.1e-5 parallel to a reference line of slope 1, RK4's "
         "from 5.8e-5 to 2.3e-13 parallel to a line of slope 4"))


# ============================================================
# uyarlamali-adim: the steps RK45 takes for y' = 1 + y^2 (rtol = 1e-6)
# ============================================================
def f_tan(t, y):
    return 1 + y**2


sol = solve_ivp(f_tan, (0, 1.5), [0.0], rtol=1e-6, atol=1e-12)
assert sol.t.size - 1 == 24 and sol.nfev == 248
steps = np.diff(sol.t)
p1 = Plot(56, 34, 250, 230, (0, 1.6), (0, 15))
p1.axes([0, 0.5, 1, 1.5], [0, 5, 10, 15], it("t"), it("y"), tick, tick)
tt = np.linspace(0, 1.5, 300)
p1.line(list(zip(tt, np.tan(tt))), THEORY, 2.0)
p1.points(list(zip(sol.t, sol.y[0])), PRACTICE, 3.4)
p1.label(1.15, math.tan(1.15), it("y") + " = tan " + it("t"), -10, -2,
         THEORY, 12.5, "end", bold=True)
p1.text_px(p1.x0 + p1.w / 2, p1.y0 - 16, "çözüm ve adım noktaları", TEXT,
           12.5, "middle", bold=True)
p2 = Plot(56 + 250 + 70, 34, 250, 230, (0, 1.6), (0, 0.24))
p2.axes([0, 0.5, 1, 1.5], [0, 0.05, 0.1, 0.15, 0.2], it("t"), "",
        tick, tick)
for a, hk in zip(sol.t[:-1], steps):
    # the tiny probing steps and the last step would get a negative width
    # (invalid SVG) after the 0.8 px gap, so keep a thin visible sliver
    bar_w = max(p2.X(a + hk) - p2.X(a) - 0.8, 0.6)
    p2.add(f'<rect x="{p2.X(a):.1f}" y="{p2.Y(hk):.1f}" '
           f'width="{bar_w:.1f}" '
           f'height="{p2.Y(0) - p2.Y(hk):.1f}" fill="{BASE}" '
           f'fill-opacity="0.45" stroke="{BASE}" stroke-width="0.8"/>')
p2.text_px(p2.x0 + p2.w / 2, p2.y0 - 16, "adım uzunlukları", TEXT, 12.5,
           "middle", bold=True)
save("uyarlamali-adim", figure(
    680, 310, [p1, p2],
    "<code>solve_ivp</code>'nin <em>y</em>&#8242; = 1 + <em>y</em>², "
    "<em>y</em>(0) = 0 problemini <code>rtol=1e-6</code> ile çözerken attığı "
    "24 adım. Solda adım noktaları <em>y</em> = tan <em>t</em> eğrisi "
    "üzerinde, sağda her adımın uzunluğu (sütunun genişliği adımın "
    "kapladığı aralık, yüksekliği adım uzunluğu). İlk dört adım, yöntemin "
    "ölçeği yoklarken attığı 0,0001, 0,001, 0,01 ve 0,1 uzunluğundaki "
    "adımlardır; sonra adımlar en fazla 0,21'e çıkar ve çözüm dikleştikçe "
    "küçülür.",
    css_class=WIDE,
    aria="Left: y = tan t on [0, 1.5] with the 25 points of the RK45 "
         "solution at rtol 1e-6, crowding near t = 1.5. Right: bars of the "
         "24 step sizes, tiny at the start, up to 0.21 near t = 0.2 and "
         "shrinking to about 0.01 as t approaches 1.5"))


# ============================================================
# salinici: harmonic oscillator, Euler spiral vs RK4 circle (n = 40)
# ============================================================
def osc(t, u):
    return np.array([u[1], -u[0]])


n_osc = 40
h_osc = 2 * np.pi / n_osc
_, u_e = euler(osc, 0.0, np.array([1.0, 0.0]), h_osc, n_osc)
_, u_r = rk4(osc, 0.0, np.array([1.0, 0.0]), h_osc, n_osc)
r_e = math.hypot(*u_e[-1])
assert f"{r_e:.6f}" == "1.628225" and f"{u_r[-1, 0]:.6f}" == "0.999996"

LIM = 1.85
p = Plot(50, 26, 360, 360, (-LIM, LIM), (-LIM, LIM))
p.axes([-1.5, -1, -0.5, 0, 0.5, 1, 1.5], [-1.5, -1, -0.5, 0, 0.5, 1, 1.5],
       it("y"), it("y") + "&#8242;", tick, tick)
p.line([(-LIM, 0), (LIM, 0)], TEXT, 0.8, opacity=0.35)
p.line([(0, -LIM), (0, LIM)], TEXT, 0.8, opacity=0.35)
p.circle(0, 0, 1.0, THEORY, 2.0, dash="6 4")
p.line([tuple(v) for v in u_e], PRACTICE, 1.8)
p.points([tuple(v) for v in u_e], PRACTICE, 2.6)
p.points([tuple(v) for v in u_r], BASE, 3.2)
p.arrow(tuple(u_e[5]), tuple(u_e[6]), PRACTICE, 1.8, 9)
p.points([(1.0, 0.0)], TEXT, 4.2)
p.label(1.0, 1.62, "Euler: " + it("r") + " = " + dec(r_e, 3), 0, 0,
        PRACTICE, 12.5, "middle", bold=True)
p.label(-0.62, 0.62, "RK4", 12, 16, BASE, 12.5, "start", bold=True)
p.label(1.0, 0.0, "başlangıç", -9, 17, TEXT, 12, "end")
save("salinici", figure(
    460, 430, [p],
    "<em>y</em>&#8242;&#8242; + <em>y</em> = 0 sisteminin faz düzleminde "
    "<em>h</em> = 2&#960;/40 ile bir tam tur. Tam çözüm kesikli birim "
    "çemberi saat yönünde dolaşır. RK4'ün 41 noktası çemberin üzerinde "
    "kalır; Euler'in noktaları her adımda orijinden "
    "&#8730;(1 + <em>h</em>²) kat uzaklaşır ve tur sonunda yarıçap "
    "1,628 olur.",
    aria="Phase plane (y, y') of the harmonic oscillator over one period "
         "with h = 2 pi / 40: the exact solution is the dashed unit circle, "
         "the 41 RK4 points lie on it, and the Euler points spiral "
         "outward clockwise from (1, 0) to radius 1.628"))


# ============================================================
# lotka-volterra: time series (x0 = 6) and closed orbits
# ============================================================
LV = (1.0, 0.5, 0.75, 0.25)


def lotka(t, z, a, b, c, d):
    x, y = z
    return [a * x - b * x * y, -c * y + d * x * y]


def prey_down(t, z, a, b, c, d):
    return z[0] - c / d


prey_down.direction = -1
main = solve_ivp(lotka, (0, 30), [6.0, 2.0], args=LV, events=prey_down,
                 dense_output=True, **TIGHT)
assert f"{np.diff(main.t_events[0])[0]:.6f}" == "7.583374"
t = np.linspace(0, 30, 601)
x, y = main.sol(t)

p1 = Plot(52, 34, 300, 220, (0, 30), (0, 8.6))
p1.axes([0, 10, 20, 30], [0, 2, 4, 6, 8], it("t"), "", tick, tick)
p1.line(list(zip(t, x)), THEORY, 2.0)
p1.line(list(zip(t, y)), PRACTICE, 2.0)
legend_line(p1, p1.x0 + 150, p1.y0 - 18, THEORY, "av " + it("x"))
legend_line(p1, p1.x0 + 228, p1.y0 - 18, PRACTICE, "avcı " + it("y"))
p2 = Plot(52 + 300 + 66, 34, 260, 220, (0, 10.5), (0, 5.4))
p2.axes([0, 3, 6, 9], [0, 2, 4], "av " + it("x"), "avcı " + it("y"),
        tick, tick)
periods = []
for x0 in [3.5, 4.5, 6.0, 8.0]:
    s = solve_ivp(lotka, (0, 30), [x0, 2.0], args=LV, events=prey_down,
                  dense_output=True, **TIGHT)
    T = s.t_events[0][1] - s.t_events[0][0]
    periods.append(T)
    tt = np.linspace(0, T, 400)
    xs, ys = s.sol(tt)
    p2.line(list(zip(xs, ys)), THEORY if x0 == 6.0 else BASE,
            2.2 if x0 == 6.0 else 1.5)
    p2.points([(x0, 2.0)], THEORY if x0 == 6.0 else BASE, 3.2)
assert [f"{T:.4f}" for T in periods] == ["7.2684", "7.3556", "7.5834",
                                         "7.9976"]
p2.points([(3.0, 2.0)], TEXT, 4.0)
p2.arrow(tuple(main.sol(1.0)), tuple(main.sol(1.15)), THEORY, 2.0, 9)
save("lotka-volterra", figure(
    700, 300, [p1, p2],
    "Lotka–Volterra modeli, <em>a</em> = 1, <em>b</em> = 0,5, <em>c</em> = "
    "0,75, <em>d</em> = 0,25; Matplotlib kodunun çizdiği iki grafiğin aynı "
    "verilerle çizilmiş hâli. Solda (6; 2) başlangıcından çıkan çözümün "
    "zamana göre değişimi: avcı sayısının tepeleri av sayısınınkinden sonra "
    "gelir. Sağda <em>x</em>(0) = 3,5; 4,5; 6; 8 ve <em>y</em>(0) = 2 "
    "başlangıçlarından çıkan kapalı yörüngeler; hepsi (3; 2) denge "
    "noktasının çevresinde saat yönünün tersine dolanır.",
    css_class=WIDE,
    aria="Left: prey x(t) and predator y(t) for t from 0 to 30 starting at "
         "(6, 2), oscillating with period 7.58, the predator peaks lagging "
         "the prey peaks. Right: four closed orbits around the equilibrium "
         "(3, 2) through (3.5, 2), (4.5, 2), (6, 2) and (8, 2), traversed "
         "counterclockwise"))


# ============================================================
# sarkac-faz: phase portrait of the pendulum theta'' = -sin(theta)
# ============================================================
def pendulum(t, z):
    return [z[1], -np.sin(z[0])]


def at_right(t, z):
    return z[0] - np.pi


at_right.terminal = True
PI = math.pi
p = Plot(58, 24, 470, 300, (-PI - 0.25, PI + 0.25), (-2.85, 2.85))


def pi_tick(v):
    k = round(v / (PI / 2))
    return {-2: MINUS + "&#960;", -1: MINUS + "&#960;/2", 0: "0",
            1: "&#960;/2", 2: "&#960;"}[k]


p.axes([-PI, -PI / 2, 0, PI / 2, PI], [-2, -1, 0, 1, 2], "&#952;",
       "&#969;", pi_tick, tick)
p.line([(-PI - 0.25, 0), (PI + 0.25, 0)], TEXT, 0.8, opacity=0.35)
p.line([(0, -2.85), (0, 2.85)], TEXT, 0.8, opacity=0.35)
th = np.linspace(-PI, PI, 400)
p.line(list(zip(th, 2 * np.cos(th / 2))), TEXT, 1.5, "6 4", 0.9)
p.line(list(zip(th, -2 * np.cos(th / 2))), TEXT, 1.5, "6 4", 0.9)
for th0 in [0.5, 1.0, 1.5, 2.0, 2.5]:
    s = solve_ivp(pendulum, (0, 17), [th0, 0.0], dense_output=True, **TIGHT)
    tt = np.linspace(0, 17, 1600)
    a, w = s.sol(tt)
    p.line(list(zip(a, w)), BASE, 1.6)
    p.arrow((a[24], w[24]), (a[30], w[30]), BASE, 1.6, 8)
for om0 in [0.8, 1.6]:
    s = solve_ivp(pendulum, (0, 20), [-PI, om0], events=at_right,
                  dense_output=True, **TIGHT)
    tt = np.linspace(0, s.t[-1], 400)
    a, w = s.sol(tt)
    p.line(list(zip(a, w)), PRACTICE, 1.8)
    p.line(list(zip(-a, -w)), PRACTICE, 1.8)
    p.arrow((a[150], w[150]), (a[160], w[160]), PRACTICE, 1.8, 8)
    p.arrow((-a[150], -w[150]), (-a[160], -w[160]), PRACTICE, 1.8, 8)
p.points([(0.0, 0.0)], TEXT, 4.0)
for xe in (-PI, PI):
    p.add(f'<circle cx="{p.X(xe):.1f}" cy="{p.Y(0):.1f}" r="4.2" '
          f'fill="{BG}" stroke="{TEXT}" stroke-width="1.6"/>')
p.label(2.25, 2.3, "dönme", 0, 0, PRACTICE, 12.5, "middle", bold=True)
p.label(0.0, 0.48, "salınım", 0, -6, BASE, 12.5, "middle", bold=True)
save("sarkac-faz", figure(
    560, 370, [p],
    "Sarkacın faz portresi; Matplotlib kodunun çizdiği grafiğin aynı "
    "verilerle çizilmiş hâli. Kapalı eğriler &#952;₀ = 0,5; 1; 1,5; 2; 2,5 "
    "genlikli salınımlardır; dalgalı eğriler, sarkacın tepeden aşarak "
    "döndüğü hareketlerdir. Kesikli ayırıcı eğri (<em>E</em> = 1) iki tür "
    "hareketi ayırır. Dolu nokta kararlı denge (0; 0), içi boş noktalar "
    "tepedeki kararsız denge (±&#960;; 0).",
    aria="Phase portrait of the pendulum on theta from -pi to pi: closed "
         "orbits around (0, 0) for amplitudes 0.5 to 2.5, dashed separatrix "
         "omega = +-2 cos(theta/2) through the unstable equilibria (+-pi, 0) "
         "and rotating trajectories above and below it, all traversed "
         "clockwise"))
