# -*- coding: utf-8 -*-
"""
Figures of the chapter "Polinomlar, İnterpolasyon ve Eğri Uydurma"
(dersler/python-bilimsel/interpolasyon-ve-egri-uydurma.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution,
exercise or callout), never inside a definition box and never directly under
a heading; concept figures stay visible (not inside a collapsed .cozum
block). The figures are NOT produced at build time. The data come from
NumPy and SciPy, so run this script with a Python that has the course packages
(Python 3.12 with NumPy 2.5, SciPy 1.18, SymPy 1.14):

    python \
        scripts/python_figures/egr.py
    python scripts/center_figures.py "python-egr-*.md"
    python scripts/check_figure_labels.py "scripts/_figures/python-egr-*.md"

(set OPENBLAS_NUM_THREADS=1 on this machine) and paste the markup of
scripts/_figures/python-egr-<name>.md into the .qmd. Every figure is drawn
from exactly the data the chapter's code computes: the same polynomials,
nodes, grids and seeds; the numbers the code prints are asserted here.
Captions are Turkish on purpose; aria labels are plain ASCII.
"""
import math
import os
import sys
from pathlib import Path

os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
import numpy as np  # noqa: E402
from numpy.polynomial import Polynomial  # noqa: E402
from scipy.interpolate import BarycentricInterpolator, CubicSpline  # noqa
from scipy.optimize import curve_fit  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import (Plot, figure, WIDE, TEXT, THEORY,  # noqa: E402
                      PRACTICE, BASE, REMARK)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "python-egr-"

MINUS = "&#8722;"
SUBS = {str(k): chr(0x2080 + k) for k in range(10)}


def save(name, markup):
    (OUT_DIR / f"{PREFIX}{name}.md").write_text(markup, encoding="utf-8",
                                                newline="\n")
    print(f"{PREFIX}{name}.md")


def it(s):
    """Italic run inside an SVG <text>."""
    return f'<tspan font-style="italic">{s}</tspan>'


def sup(s, size=9):
    """Superscript inside an SVG <text>."""
    return (f'<tspan font-size="{size}" dy="-5">{s}</tspan>'
            f'<tspan dy="5">&#8203;</tspan>')


def sub(s):
    """Subscript digits as Unicode subscript characters."""
    return "".join(SUBS.get(ch, ch) for ch in s)


def subt(s, size=9):
    """Subscript inside an SVG <text>."""
    return (f'<tspan font-size="{size}" dy="3">{s}</tspan>'
            f'<tspan dy="-3">&#8203;</tspan>')


def tick(t):
    """Tick label with a decimal comma and a true minus sign."""
    s = f"{t:g}"
    return s.replace(".", ",").replace("-", MINUS)


def pow10(e):
    """Tick label 10^e for a log axis."""
    return "10" + sup(str(e).replace("-", MINUS))


def legend_line(p, px, py, color, label, dash=None, dot=False, hollow=False,
                size=12):
    """A short line sample with an optional marker and a label (pixels)."""
    if dash != "none":
        da = f' stroke-dasharray="{dash}"' if dash else ""
        p.add(f'<line x1="{px:.1f}" y1="{py:.1f}" x2="{px + 24:.1f}" '
              f'y2="{py:.1f}" stroke="{color}" stroke-width="2"{da}/>')
    if dot:
        p.add(f'<circle cx="{px + 12:.1f}" cy="{py:.1f}" r="3.6" '
              f'fill="{color}"/>')
    if hollow:
        p.add(f'<circle cx="{px + 12:.1f}" cy="{py:.1f}" r="3.8" '
              f'fill="none" stroke="{color}" stroke-width="1.6"/>')
    p.text_px(px + 32, py + 4.5, label, TEXT, size)


def frame(p, opacity=0.5):
    """Full box around a panel, as Matplotlib draws its spines."""
    p.add(f'<rect x="{p.x0:.1f}" y="{p.y0:.1f}" width="{p.w:.1f}" '
          f'height="{p.h:.1f}" fill="none" stroke="{TEXT}" '
          f'stroke-width="1" opacity="{opacity}"/>')


def ticks(p, xs, ys, xfmt=tick, yfmt=tick, size=11):
    """Tick marks and labels on the bottom and left edges of a frame."""
    a = [f'<g stroke="{TEXT}" stroke-width="1" opacity="0.6">']
    for v in xs:
        X = p.X(v)
        a.append(f'<line x1="{X:.1f}" y1="{p.y0 + p.h:.1f}" x2="{X:.1f}" '
                 f'y2="{p.y0 + p.h + 4:.1f}"/>')
    for v in ys:
        Y = p.Y(v)
        a.append(f'<line x1="{p.x0 - 4:.1f}" y1="{Y:.1f}" x2="{p.x0:.1f}" '
                 f'y2="{Y:.1f}"/>')
    a.append('</g>')
    p.add("".join(a))
    for v in xs:
        p.text_px(p.X(v), p.y0 + p.h + 16, xfmt(v), TEXT, size, "middle")
    for v in ys:
        p.text_px(p.x0 - 7, p.Y(v) + 4, yfmt(v), TEXT, size, "end")


def title(p, s, size=12.5):
    p.text_px(p.x0 + p.w / 2, p.y0 - 9, s, TEXT, size, "middle", bold=True)


def runge(x):
    return 1 / (1 + 25 * x**2)


def cheb_nodes(n):
    k = np.arange(n + 1)
    return np.cos((2 * k + 1) * np.pi / (2 * n + 2))


# ============================================================
# wilkinson: roots of w with the x^19 coefficient changed by 2^-23
# ============================================================
w = Polynomial.fromroots(np.arange(1, 21))
c = w.coef.copy()
c[19] -= 2.0**-23
r = Polynomial(c).roots()
r = r[np.argsort(r.real)]
assert np.sum(r.imag != 0) == 10
top = r[r.imag > 0]
far = top[np.argmax(top.imag)]
assert f"{far.real:.4f} {far.imag:+.4f}" == "16.7310 +2.8127"

XR, YR = (-0.6, 22.4), (-3.5, 3.5)
p = Plot(30, 52, 500, 250, XR, YR)
p.origin_axes("Re", "Im", [5, 10, 15, 20], [-3, -2, -1, 1, 2, 3],
              tick, tick)
p.hollow_points([(k, 0) for k in range(1, 21)], BASE, 4.2)
p.points([(z.real, z.imag) for z in r], PRACTICE, 3.6)
p.label(far.real, far.imag, "16,73 + 2,81" + it("i"), 8, -8, PRACTICE, 12,
        bold=True)
p.label(far.real, -far.imag, "16,73 " + MINUS + " 2,81" + it("i"), 8, 16,
        PRACTICE, 12, bold=True)
legend_line(p, 40, 14, BASE, "gerçek kökler 1, 2, ..., 20",
            dash="none", hollow=True)
legend_line(p, 40, 34, PRACTICE, it("x") + sup("19") + " katsayısı 2"
            + sup(MINUS + "23") + " azalınca", dash="none", dot=True)

save("wilkinson", figure(
    560, 320, [p],
    "Wilkinson polinomu <em>w</em>(<em>x</em>) = (<em>x</em> &#8722; 1)"
    "(<em>x</em> &#8722; 2)&#183;&#183;&#183;(<em>x</em> &#8722; 20) için "
    "<em>x</em><sup>19</sup> katsayısı &#8722;210'dan &#8722;210 &#8722; "
    "2<sup>&#8722;23</sup>'e değiştirilince bulunan kökler (dolu "
    "noktalar) ve <em>w</em>'nin gerçek kökleri (içi boş). Yaklaşık "
    "10<sup>&#8722;7</sup>'lik bir değişiklik on kökü karmaşık düzleme "
    "taşır.",
    aria="Complex plane with the roots 1 to 20 of the Wilkinson polynomial "
         "as hollow circles on the real axis and the roots after the x^19 "
         "coefficient is decreased by 2^-23 as filled dots: ten of them "
         "form five complex conjugate pairs, the farthest 16.73 +- 2.81i"))


# ============================================================
# lagrange-taban: basis polynomials L0..L3 for nodes 0, 1, 2, 3 and p
# ============================================================
xn = np.array([0.0, 1.0, 2.0, 3.0])
yn = np.array([1.0, 3.0, 2.0, 5.0])


def lagrange_basis(xn, k, x):
    others = np.delete(xn, k)
    return np.prod((x[:, None] - others) / (xn[k] - others), axis=1)


xx = np.linspace(0, 3, 400)
basis = [lagrange_basis(xn, k, xx) for k in range(4)]
pp = sum(yn[k] * basis[k] for k in range(4))
p_vand = Polynomial(np.linalg.solve(np.vander(xn, increasing=True), yn))
assert np.allclose(pp, p_vand(xx))
COLORS = [THEORY, BASE, PRACTICE, REMARK]

XR = (-0.22, 3.3)
p1 = Plot(48, 40, 290, 240, XR, (-0.62, 1.42))
p1.origin_axes(it("x"), "", [1, 2, 3], [-0.5, 0.5, 1], tick, tick)
for xk in xn[1:]:
    p1.vline(xk, -0.62, 1.42, TEXT, "2 4", 0.35)
for k in range(4):
    p1.line(list(zip(xx, basis[k])), COLORS[k], 2.0)
    p1.points([(xn[k], 1.0)], COLORS[k], 4.0)
# labels of the basis polynomials next to their peak at the own node
LAB_POS = {0: (0.0, 1.0, 8, -8, "start"), 1: (1.0, 1.0, 0, -10, "middle"),
           2: (2.0, 1.0, 0, -10, "middle"), 3: (3.0, 1.0, 10, -8, "start")}
for k, (lx, ly, dx, dy, anchor) in LAB_POS.items():
    p1.label(lx, ly, it("L") + sub(str(k)), dx, dy, COLORS[k], 13, anchor,
             bold=True)
title(p1, "Lagrange taban polinomları")

p2 = Plot(420, 40, 290, 240, XR, (-0.6, 6.6))
p2.origin_axes(it("x"), it("y"), [1, 2, 3], [1, 2, 3, 4, 5, 6], tick, tick)
p2.line(list(zip(xx, pp)), THEORY, 2.2)
p2.points(list(zip(xn, yn)), PRACTICE, 4.4)
PT_POS = {0: (9, -8, "start"), 1: (6, -10, "start"), 2: (0, 21, "middle"),
          3: (-9, -8, "end")}
for k, (xk, yk) in enumerate(zip(xn, yn)):
    dx, dy, anchor = PT_POS[k]
    p2.label(xk, yk, f"({tick(xk)}, {tick(yk)})", dx, dy, PRACTICE, 11.5,
             anchor)
p2.label(2.55, float(p_vand(2.55)), it("p"), 10, 8, THEORY, 13, bold=True)
title(p2, it("p") + " = 1" + it("L") + sub("0") + " + 3" + it("L")
      + sub("1") + " + 2" + it("L") + sub("2") + " + 5" + it("L") + sub("3"))

save("lagrange-taban", figure(
    740, 310, [p1, p2],
    "Sol: 0, 1, 2, 3 düğümlerinin Lagrange taban polinomları. Her "
    "<em>L</em><sub><em>k</em></sub> kendi düğümünde 1, öteki düğümlerde 0 "
    "değerini alır (noktalı çizgiler düğümleri gösterir). Sağ: bu "
    "polinomların veriyle ağırlıklı toplamı olan interpolasyon polinomu "
    "<em>p</em>(<em>x</em>) = 1 + 35<em>x</em>/6 &#8722; 5<em>x</em>² + "
    "7<em>x</em>³/6 dört noktanın hepsinden geçer.",
    css_class=WIDE,
    aria="Left: the four Lagrange basis polynomials of the nodes 0, 1, 2, 3, "
         "each equal to 1 at its own node and 0 at the others. Right: the "
         "interpolating polynomial through (0, 1), (1, 3), (2, 2), (3, 5)"))


# ============================================================
# runge: P10 at equispaced and at Chebyshev nodes (Matplotlib code)
# ============================================================
n = 10
nodes = [("eşit aralıklı düğümler", np.linspace(-1, 1, n + 1)),
         ("Çebişev düğümleri", cheb_nodes(n))]
xx = np.linspace(-1, 1, 401)
panels = []
errors = []
for j, (name, nd) in enumerate(nodes):
    P10 = BarycentricInterpolator(nd, runge(nd))
    yy = P10(xx)
    errors.append(np.max(np.abs(yy - runge(xx))))
    p = Plot(60 + j * 345, 40, 285, 230, (-1.1, 1.1), (-0.6, 2.1))
    frame(p)
    ticks(p, [-1, -0.5, 0, 0.5, 1], [-0.5, 0, 0.5, 1, 1.5, 2] if j == 0
          else [])
    p.add(f'<line x1="{p.x0:.1f}" y1="{p.Y(0):.1f}" x2="{p.x0 + p.w:.1f}" '
          f'y2="{p.Y(0):.1f}" stroke="{TEXT}" stroke-width="0.8" '
          f'opacity="0.3"/>')
    p.line(list(zip(xx, runge(xx))), TEXT, 2.3)
    p.line(list(zip(xx, yy)), THEORY, 1.9)
    p.points(list(zip(nd, runge(nd))), PRACTICE, 3.6)
    legend_line(p, p.x0 + p.w - 92, p.y0 + 18, TEXT, it("f"))
    legend_line(p, p.x0 + p.w - 92, p.y0 + 38, THEORY,
                it("P") + sub("10"))
    title(p, name)
    panels.append(p)
assert [f"{e:.4f}" for e in errors] == ["1.9156", "0.1092"]

save("runge", figure(
    700, 300, panels,
    "<em>f</em>(<em>x</em>) = 1/(1 + 25<em>x</em>²) ve 11 düğümden geçen "
    "onuncu dereceden interpolasyon polinomu <em>P</em><sub>10</sub>; "
    "yukarıdaki Matplotlib kodunun çizdiği grafiğin aynı verilerle "
    "çizilmiş hâli. Eşit aralıklı düğümlerde polinom uçlara yakın büyük "
    "salınımlar yapar (en büyük hata 1,92); uçlarda sıklaşan Çebişev "
    "düğümlerinde salınım kaybolur (en büyük hata 0,11).",
    css_class=WIDE,
    aria="Two panels: the Runge function 1/(1 + 25 x^2) and its degree 10 "
         "interpolating polynomial; with equispaced nodes the polynomial "
         "oscillates near the ends up to 1.9, with Chebyshev nodes it stays "
         "close to the function"))


# ============================================================
# omega: the node polynomial for n = 10, equispaced and Chebyshev
# ============================================================
def omega(nd, x):
    return np.prod(x[:, None] - nd, axis=1)


xx = np.linspace(-1, 1, 2001)
om_eq = omega(np.linspace(-1, 1, 11), xx)
om_ch = omega(cheb_nodes(10), xx)
assert f"{np.max(np.abs(om_eq)):9.3e}" == "8.532e-03"
assert f"{np.max(np.abs(om_ch)):9.3e}" == "9.766e-04"

p = Plot(76, 34, 430, 270, (-1.06, 1.06), (-0.0096, 0.0096))
frame(p)
ticks(p, [-1, -0.5, 0, 0.5, 1], [-0.008, -0.004, 0, 0.004, 0.008])
p.add(f'<line x1="{p.x0:.1f}" y1="{p.Y(0):.1f}" x2="{p.x0 + p.w:.1f}" '
      f'y2="{p.Y(0):.1f}" stroke="{TEXT}" stroke-width="0.8" '
      f'opacity="0.35"/>')
band = 2.0**-10
p.line([(-1.06, band), (1.06, band)], TEXT, 1.0, "5 4", 0.65)
p.line([(-1.06, -band), (1.06, -band)], TEXT, 1.0, "5 4", 0.65)
p.line(list(zip(xx, om_eq)), BASE, 2.0)
p.line(list(zip(xx, om_ch)), THEORY, 2.2)
p.text_px(p.x0, p.y0 - 10, it("ω") + "(" + it("x") + ")", TEXT, 12.5,
          "middle")
p.text_px(p.x0 + p.w / 2, p.y0 + p.h + 34, it("x"), TEXT, 12.5, "middle")
i_peak = np.argmax(om_eq)
p.label(xx[i_peak], om_eq[i_peak], "eşit aralıklı düğümler", 12, 6, BASE,
        12.5, bold=True)
p.label(-0.25, -band, "Çebişev düğümleri", 0, 19, THEORY, 12.5, "middle",
        bold=True)
p.label(0.25, band, "+2" + sup(MINUS + "10"), 0, -7, TEXT, 11.5, "middle")
p.label(0.25, -band, MINUS + "2" + sup(MINUS + "10"), 0, 17, TEXT, 11.5,
        "middle")

save("omega", figure(
    540, 340, [p],
    "11 düğüm (<em>n</em> = 10) için <em>&#969;</em>(<em>x</em>) = "
    "(<em>x</em> &#8722; <em>x</em><sub>0</sub>)&#183;&#183;&#183;"
    "(<em>x</em> &#8722; <em>x</em><sub>10</sub>) çarpımı. Eşit aralıklı "
    "düğümlerde çarpım uçlara yakın 8,5&#183;10<sup>&#8722;3</sup>'e çıkar; Çebişev düğümlerinde aralığın "
    "her yerinde aynı yükseklikte salınır ve hiçbir zaman "
    "2<sup>&#8722;10</sup> &#8776; 9,8&#183;10<sup>&#8722;4</sup> "
    "sınırını (kesikli çizgiler) aşmaz.",
    aria="The node polynomial omega(x) for 11 equispaced nodes, large near "
         "the ends of [-1, 1], and for 11 Chebyshev nodes, oscillating "
         "with equal height 2^-10 between dashed lines"))


# ============================================================
# spline: the not-a-knot cubic spline through 11 Runge nodes
# ============================================================
xn = np.linspace(-1, 1, 11)
Sp = CubicSpline(xn, runge(xn))
xx = np.linspace(-1, 1, 2001)
assert f"{np.max(np.abs(Sp(xx) - runge(xx))):.4f}" == "0.0220"

p = Plot(50, 30, 460, 250, (-1.08, 1.08), (-0.08, 1.12))
p.origin_axes(it("x"), it("y"), [-1, -0.5, 0.5, 1], [0.5, 1], tick, tick)
p.line(list(zip(xx, runge(xx))), TEXT, 1.4, "5 4", 0.8)
for i in range(len(xn) - 1):
    xs = np.linspace(xn[i], xn[i + 1], 40)
    p.line(list(zip(xs, Sp(xs))), THEORY if i % 2 == 0 else BASE, 2.4)
p.points(list(zip(xn, runge(xn))), PRACTICE, 3.8)
legend_line(p, 330, 50, TEXT, it("f"), dash="5 4")
legend_line(p, 330, 72, THEORY, "spline (tek parçalar)")
legend_line(p, 330, 94, BASE, "spline (çift parçalar)")

save("spline", figure(
    560, 320, [p],
    "<em>f</em>(<em>x</em>) = 1/(1 + 25<em>x</em>²) (kesikli) ve onun 11 "
    "eşit aralıklı düğümdeki değerlerinden <code>CubicSpline</code> ile "
    "kurulan kübik spline. Renkler on kübik parçayı birbirinden ayırır; "
    "parçalar düğümlerde birinci ve ikinci türevleriyle birlikte "
    "birleşir. En büyük hata 0,022'dir; aynı düğümlerdeki "
    "<em>P</em><sub>10</sub> polinomunun hatası 1,92'ydi.",
    aria="The Runge function dashed and the cubic spline through its "
         "values at 11 equispaced nodes, the ten cubic pieces drawn in "
         "alternating colours; the spline follows the function closely"))


# ============================================================
# spline-hata: errors of np.interp and CubicSpline against n (log-log)
# ============================================================
xx = np.linspace(-1, 1, 20001)
ns = [10, 20, 40, 80, 160, 320]
e_lin, e_spl = [], []
for n in ns:
    xn = np.linspace(-1, 1, n + 1)
    e_lin.append(np.max(np.abs(np.interp(xx, xn, runge(xn)) - runge(xx))))
    e_spl.append(np.max(np.abs(CubicSpline(xn, runge(xn))(xx)
                               - runge(xx))))
assert [f"{e:8.2e}" for e in e_lin][-1] == "2.44e-04"
assert [f"{e:8.2e}" for e in e_spl][-1] == "5.98e-08"

lx = [math.log10(v) for v in ns]
p = Plot(70, 24, 400, 290, (0.9, 2.62), (-8.4, -0.6))
frame(p)
ticks(p, lx, [-1, -2, -3, -4, -5, -6, -7, -8],
      lambda v: str(round(10**v)), pow10)
p.grid(lx, [-2, -4, -6, -8])
p.text_px(p.x0 + p.w / 2, p.y0 + p.h + 34, "alt aralık sayısı " + it("n"),
          TEXT, 12, "middle")
p.text_px(p.x0, p.y0 - 10, "en büyük hata", TEXT, 12, "middle")
# reference slopes through the last points, shifted down by a factor 4
for errs, slope, color, lab in ((e_lin, 2, BASE, "eğim " + MINUS + "2"),
                                (e_spl, 4, THEORY, "eğim " + MINUS + "4")):
    x1, y1 = lx[-1], math.log10(errs[-1]) - 0.6
    x0 = lx[2]
    y0 = y1 + slope * (x1 - x0)
    p.line([(x0, y0), (x1, y1)], TEXT, 1.2, "5 4", 0.7)
    p.label((x0 + x1) / 2, (y0 + y1) / 2, lab, -6, 14, TEXT, 11.5, "end")
for errs, color in ((e_lin, BASE), (e_spl, THEORY)):
    pts = [(a, math.log10(e)) for a, e in zip(lx, errs)]
    p.line(pts, color, 2.1)
    p.points(pts, color, 3.8)
p.label(lx[4], math.log10(e_lin[4]), "parçalı doğrusal", 0, -20, BASE,
        12.5, "middle", bold=True)
p.label(lx[1], math.log10(e_spl[1]), "kübik spline", -8, 20, THEORY, 12.5,
        "middle", bold=True)

save("spline-hata", figure(
    520, 370, [p],
    "<em>f</em>(<em>x</em>) = 1/(1 + 25<em>x</em>²) için parçalı doğrusal "
    "interpolasyonun (<code>np.interp</code>) ve kübik spline'ın "
    "(<code>CubicSpline</code>) en büyük hatası, iki ekseni de logaritmik "
    "ölçekte; tablodaki sayıların aynısı. <em>n</em> = 40'tan sonra alt "
    "aralık sayısı iki katına çıkınca hatalar yaklaşık 4 ve 16 kat "
    "küçülür; daha küçük <em>n</em>'de iki eğri de daha yavaş iner. Kesikli "
    "çizgiler bu hızlara karşılık gelen &#8722;2 ve &#8722;4 eğimlerini "
    "gösterir.",
    aria="Log-log plot of the maximum error against the number of "
         "subintervals n = 10 to 320 for piecewise linear interpolation, "
         "slope -2, and for the cubic spline, slope -4, with dashed "
         "reference lines"))


# ============================================================
# artiklar: fits of degree 1 and 2 to the height data of a body thrown
# upward and their residuals
# ============================================================
rng = np.random.default_rng(16)
t = np.linspace(0, 2, 21)
h = 25 + 3 * t - 4.905 * t**2 + rng.normal(0, 0.05, t.size)
tt = np.linspace(0, 2, 201)
fits = {deg: Polynomial.fit(t, h, deg) for deg in (1, 2)}
res = {deg: h - fits[deg](t) for deg in (1, 2)}
assert f"{np.max(np.abs(res[1])):.3f}" == "3.161"
assert f"{np.max(np.abs(res[2])):.3f}" == "0.078"
FIT_COL = {1: BASE, 2: THEORY}

p0 = Plot(52, 40, 200, 210, (-0.1, 2.1), (9.0, 29.5))
frame(p0)
ticks(p0, [0, 1, 2], [10, 15, 20, 25])
p0.points(list(zip(t, h)), TEXT, 3.0)
for deg in (1, 2):
    p0.line(list(zip(tt, fits[deg](tt))), FIT_COL[deg], 2.0)
p0.text_px(p0.x0 + p0.w / 2, p0.y0 + p0.h + 33, it("t") + " (s)", TEXT, 12,
           "middle")
p0.text_px(p0.x0 - 8, p0.y0 - 10, it("h") + " (m)", TEXT, 12, "middle")
legend_line(p0, p0.x0 + 10, p0.Y(13.4), TEXT, "ölçüm", dash="none",
            dot=True, size=11.5)
legend_line(p0, p0.x0 + 10, p0.Y(13.4) + 19, BASE, "derece 1", size=11.5)
legend_line(p0, p0.x0 + 10, p0.Y(13.4) + 38, THEORY, "derece 2", size=11.5)

panels = [p0]
for deg, x0_, yr, yt in ((1, 312, (-3.5, 3.5), [-3, -2, -1, 0, 1, 2, 3]),
                         (2, 552, (-0.1, 0.1), [-0.1, -0.05, 0, 0.05, 0.1])):
    q = Plot(x0_, 40, 175, 210, (-0.1, 2.1), yr)
    frame(q)
    ticks(q, [0, 1, 2], yt)
    q.add(f'<line x1="{q.x0:.1f}" y1="{q.Y(0):.1f}" x2="{q.x0 + q.w:.1f}" '
          f'y2="{q.Y(0):.1f}" stroke="{TEXT}" stroke-width="1" '
          f'opacity="0.45"/>')
    q.points(list(zip(t, res[deg])), FIT_COL[deg], 3.2)
    q.text_px(q.x0 + q.w / 2, q.y0 + q.h + 33, it("t") + " (s)", TEXT, 12,
              "middle")
    title(q, f"derece {deg}: artıklar")
    panels.append(q)
title(p0, "veri ve uyan polinomlar")

save("artiklar", figure(
    750, 300, panels,
    "Yukarı atılan cismin 21 yükseklik ölçümüne birinci ve ikinci dereceden "
    "polinom uydurulması (sol) ve iki modelin artıkları; yukarıdaki "
    "Matplotlib kodunun çizdiği grafiğin aynı verilerle çizilmiş hâli. "
    "Doğrunun artıkları belirgin bir kemer çizer: model, verideki eğriliği "
    "yakalayamamıştır. Parabolün artıkları ise sıfırın iki yanına "
    "düzensizce dağılır ve 0,08 m'yi aşmaz (eksen ölçeklerinin farkına "
    "dikkat).",
    css_class=WIDE,
    aria="Left: 21 noisy height measurements of a body thrown upward with the "
         "fitted line and parabola. Middle: the residuals of the line form "
         "an arch between -3.2 and 1.8. Right: the residuals of the parabola "
         "scatter randomly within 0.08"))


# ============================================================
# sogutma: Newton's law of cooling fitted with curve_fit
# ============================================================
def cooling(t, Ta, T0, k):
    return Ta + (T0 - Ta) * np.exp(-k * t)


rng = np.random.default_rng(5)
t = np.arange(0, 31, 2.0)
T = cooling(t, 22, 90, 0.12) + rng.normal(0, 0.5, t.size)
popt, pcov = curve_fit(cooling, t, T, p0=(20, 80, 0.1))
assert [f"{v:.4f}" for v in popt] == ["21.6914", "89.3752", "0.1173"]
Ta, T0, k = popt

tt = np.linspace(0, 30, 300)
p = Plot(60, 30, 430, 260, (-1, 31.5), (12, 96))
frame(p)
ticks(p, [0, 5, 10, 15, 20, 25, 30], [20, 40, 60, 80])
p.line([(-1, Ta), (31.5, Ta)], TEXT, 1.1, "5 4", 0.7)
p.line(list(zip(tt, cooling(tt, *popt))), THEORY, 2.2)
p.points(list(zip(t, T)), PRACTICE, 3.8)
p.text_px(p.x0 + p.w / 2, p.y0 + p.h + 34, it("t") + " (dakika)", TEXT, 12,
          "middle")
p.text_px(p.x0, p.y0 - 10, it("T") + " (°C)", TEXT, 12, "middle")
p.label(1.5, Ta, it("T") + subt("a") + " ≈ 21,7 °C", 0, -8, TEXT, 12)
p.label(9, float(cooling(9, *popt)), it("T") + "(" + it("t") + ") = 21,7 + "
        "67,7 " + it("e") + sup(MINUS + "0,117" + it("t")), 12, -6, THEORY,
        12.5, bold=True)
legend_line(p, p.x0 + p.w - 150, p.y0 + 18, PRACTICE, "ölçüm", dash="none",
            dot=True)
legend_line(p, p.x0 + p.w - 150, p.y0 + 38, THEORY, "uyan eğri")

save("sogutma", figure(
    540, 340, [p],
    "Soğuyan bir sıvının iki dakikada bir ölçülen sıcaklıkları ve "
    "<code>curve_fit</code> ile uydurulan Newton soğuma eğrisi. Kesikli "
    "çizgi, tahmin edilen ortam sıcaklığıdır; eğri zamanla ona yaklaşır.",
    aria="Sixteen temperature readings of a cooling liquid every two "
         "minutes with the fitted curve T(t) = 21.7 + 67.7 exp(-0.117 t) "
         "approaching the dashed line T = 21.7"))
