# -*- coding: utf-8 -*-
"""
Figures of the chapter "Sayısal Türev ve İntegral"
(dersler/python-bilimsel/sayisal-turev-ve-integral.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution,
exercise or callout), never inside a definition box and never directly under
a heading; concept figures stay visible (not inside a collapsed .cozum
block). The figures are NOT produced at build time. The data come from NumPy
and SciPy, so run this script with a Python that has the course packages
(Python 3.12 with NumPy 2.5, SciPy 1.18, SymPy 1.14):

    python \
        scripts/python_figures/int.py
    python scripts/center_figures.py "python-int-*.md"
    python scripts/check_figure_labels.py "scripts/_figures/python-int-*.md"

(set OPENBLAS_NUM_THREADS=1 on this machine) and paste the markup of
scripts/_figures/python-int-<name>.md into the .qmd. Every figure is drawn
from exactly the data the chapter's code computes: the same functions,
grids, step sizes and SciPy calls. Captions are Turkish on purpose; aria
labels are plain ASCII.
"""
import math
import sys
from pathlib import Path

import numpy as np
from scipy.integrate import cumulative_trapezoid, quad

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import (Plot, figure, WIDE, TEXT, THEORY, PRACTICE,  # noqa: E402
                      BASE, REMARK, BG, panel_title)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "python-int-"

MINUS = "&#8722;"
PI = "&#960;"
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
    """Italic letter with a subscript digit: T_4."""
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


def pow10(t, size=8.5):
    """Tick label of a log10 axis: -3 -> 10^-3, 0 -> 1."""
    t = int(round(t))
    if t == 0:
        return "1"
    return "10" + sup((MINUS if t < 0 else "") + str(abs(t)), size)


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


def legend_line(p, px, py, color, label, dash=None, dot=True, size=11.5,
                hollow=False):
    """A short line sample with an optional marker and a label (pixels)."""
    if dash is not False:
        da = f' stroke-dasharray="{dash}"' if dash else ""
        p.add(f'<line x1="{px:.1f}" y1="{py:.1f}" x2="{px + 26:.1f}" '
              f'y2="{py:.1f}" stroke="{color}" stroke-width="1.9"{da}/>')
    if dot:
        if hollow:
            p.add(f'<circle cx="{px + 13:.1f}" cy="{py:.1f}" r="3.6" '
                  f'fill="{BG}" stroke="{color}" stroke-width="1.8"/>')
        else:
            p.add(f'<circle cx="{px + 13:.1f}" cy="{py:.1f}" r="3.4" '
                  f'fill="{color}"/>')
    p.text_px(px + 34, py + 4, label, TEXT, size)


# ============================================================
# adim-hata: error of the forward and central differences of e^x at x = 1
# against h = 10^-k (the table of b02), with the bounds of the theorem
# ============================================================
EPS = 2.0**-52
x0 = 1.0
exact = math.exp(x0)
ks = list(range(1, 16))
e_fwd, e_cen = [], []
for k in ks:
    h = 10.0**-k
    fwd = (math.exp(x0 + h) - math.exp(x0)) / h
    cen = (math.exp(x0 + h) - math.exp(x0 - h)) / (2 * h)
    e_fwd.append(abs(fwd - exact))
    e_cen.append(abs(cen - exact))
assert f"{e_fwd[7]:.3e}" == "6.603e-09" and f"{e_cen[4]:.3e}" == "5.859e-11"

delta = EPS * exact
M = exact
h_fwd = 2 * math.sqrt(delta / M)
b_fwd = M * h_fwd / 2 + 2 * delta / h_fwd
h_cen = (3 * delta / M) ** (1 / 3)
b_cen = M * h_cen**2 / 6 + delta / h_cen
assert f"{h_fwd:.2e}" == "2.98e-08" and f"{b_cen:.2e}" == "1.04e-10"

lg = math.log10
p = Plot(70, 26, 420, 280, (-15.6, -0.4), (-11.0, 0.4))
p.grid([-15, -12, -9, -6, -3], [-10, -8, -6, -4, -2, 0])
p.axes([-15, -12, -9, -6, -3], [0, -2, -4, -6, -8, -10], it("h"), "hata",
       pow10, pow10)
hh = np.logspace(-15.6, -0.4, 400)
model_fwd = M * hh / 2 + 2 * delta / hh
model_cen = M * hh**2 / 6 + delta / hh
for model, color in [(model_fwd, PRACTICE), (model_cen, THEORY)]:
    for piece in clip_y(np.log10(hh), np.log10(model), -11.0, 0.4):
        p.line(piece, color, 1.3, "5 4", opacity=0.75)
for errs, color in [(e_fwd, PRACTICE), (e_cen, THEORY)]:
    pts = [(-k, lg(e)) for k, e in zip(ks, errs)]
    p.line(pts, color, 2.0)
    p.points(pts, color, 3.6)
p.hollow_points([(lg(h_fwd), lg(b_fwd))], PRACTICE, 5.0)
p.hollow_points([(lg(h_cen), lg(b_cen))], THEORY, 5.0)
p.label(-4.0, -2.6, "eğim 1", 0, 0, PRACTICE, 12, "end", True)
p.label(-2.6, -7.4, "eğim 2", 0, 0, THEORY, 12, "start", True)
p.label(-15.2, -4.6, "eğim " + MINUS + "1", 0, 0, TEXT, 12, "start", True)
p.label(-15.2, -5.9, "yuvarlama", 0, 0, TEXT, 11.5, "start")
p.label(-15.2, -5.9, "hatası baskın", 0, 15, TEXT, 11.5, "start")
p.label(-4.6, -0.9, "kesme hatası baskın", 0, 0, TEXT, 11.5, "middle")
LX, LY = p.X(-15.3), p.Y(-8.6)
legend_line(p, LX, LY, PRACTICE, "ileri fark")
legend_line(p, LX, LY + 21, THEORY, "merkezi fark")
legend_line(p, LX, LY + 42, TEXT, "teoremdeki sınır", dash="5 4", dot=False)
save("adim-hata", figure(
    520, 350, [p],
    "<em>e</em><sup><em>x</em></sup> fonksiyonunun <em>x</em> = 1'deki "
    "türevi için ileri ve merkezi farkın hatası, iki eksen de logaritmik; "
    "adım taraması kodunun tablosundaki sayıların aynısı. Sağda kesme hatası "
    "baskındır ve doğrular 1 ile 2 eğimiyle iner. Solda yuvarlama hatası "
    "baskındır ve hata 1/<em>h</em> gibi büyür. Kesikli eğriler teoremdeki "
    "sınırlardır; içi boş halkalar sınırın en küçük olduğu adımları, "
    "yaklaşık 3&#183;10<sup>&#8722;8</sup> ve 9&#183;10<sup>&#8722;6</sup> "
    "değerlerini gösterir.",
    aria="Log-log plot of the error of the forward and central difference "
         "for the derivative of exp at x = 1 against h = 10^-1 ... 10^-15. "
         "Both curves are V shaped: the forward error is smallest near "
         "h = 1e-8, the central error near h = 1e-5; dashed theoretical "
         "bounds follow the same shape"))


# ============================================================
# gradient: np.gradient of cos x on 9 points of [0, pi], edge orders
# ============================================================
xg = np.linspace(0, np.pi, 9)
yg = np.cos(xg)
g1 = np.gradient(yg, xg)
g2 = np.gradient(yg, xg, edge_order=2)
assert round(abs(g1[0]), 4) == 0.1938 and round(abs(g2[0]), 4) == 0.0148

p = Plot(64, 24, 410, 250, (-0.12, math.pi + 0.12), (-1.1, 0.08))
p.grid([], [-1, -0.5, 0])
p.axes([], [-1, -0.5, 0], it("x"), "", tick, tick)
for t, lab in [(0, "0"), (math.pi / 4, PI + "/4"), (math.pi / 2, PI + "/2"),
               (3 * math.pi / 4, "3" + PI + "/4"), (math.pi, PI)]:
    p.text_px(p.X(t), p.y0 + p.h + 16, lab, TEXT, 11, "middle")
xx = np.linspace(0, math.pi, 300)
p.line(list(zip(xx, -np.sin(xx))), THEORY, 2.0)
p.points(list(zip(xg[1:-1], g1[1:-1])), PRACTICE, 3.8)
for k in (0, -1):
    p.vline(xg[k], g1[k], 0, TEXT, "3 3", 0.6)
    p.hollow_points([(xg[k], g1[k])], PRACTICE, 4.2)
    p.add(f'<rect x="{p.X(xg[k]) - 3.6:.1f}" y="{p.Y(g2[k]) - 3.6:.1f}" '
          f'width="7.2" height="7.2" fill="{BASE}" '
          f'transform="rotate(45 {p.X(xg[k]):.1f} {p.Y(g2[k]):.1f})"/>')
p.label(0.55, -0.75, MINUS + "sin " + it("x"), 0, 0, THEORY, 12.5, "end",
        True)
LX, LY = p.X(0.9), p.Y(-0.18)
legend_line(p, LX, LY, PRACTICE, "iç noktalar", dash=False)
legend_line(p, LX, LY + 21, PRACTICE, "uçlar, varsayılan", dash=False,
            hollow=True)
p.add(f'<rect x="{LX + 13 - 3.6:.1f}" y="{LY + 42 - 3.6:.1f}" width="7.2" '
      f'height="7.2" fill="{BASE}" '
      f'transform="rotate(45 {LX + 13:.1f} {LY + 42:.1f})"/>')
p.text_px(LX + 34, LY + 46, "uçlar, edge_order=2", TEXT, 11.5)
save("gradient", figure(
    520, 320, [p],
    "<code>np.gradient</code> kodunun dokuz noktada bulduğu türevler ve "
    "kesin türev &#8722;sin <em>x</em>. İç noktalardaki merkezi farklar "
    "eğriye çok yakındır. Uçlardaki tek yönlü fark ise varsayılan hâlde "
    "0,19 kadar sapar (içi boş halkalar); <code>edge_order=2</code> ile bu "
    "sapma 0,015'e iner (yeşil karolar).",
    aria="The curve -sin x on [0, pi] with the nine values of np.gradient "
         "of cos x: interior points lie on the curve, the default end "
         "values -0.19 lie well below 0, the edge_order=2 end values -0.015 "
         "lie close to 0"))


# ============================================================
# yamuk-simpson: T_4 and S_4 for exp(-x^2) on [0, 2]
# ============================================================
def gauss(x):
    return np.exp(-x**2)


xs4 = np.linspace(0, 2, 5)
ys4 = gauss(xs4)
T4 = 0.5 * (ys4[0] / 2 + ys4[1:-1].sum() + ys4[-1] / 2)
S4 = 0.5 / 3 * (ys4[0] + 4 * ys4[1:-1:2].sum() + 2 * ys4[2:-1:2].sum()
                + ys4[-1])
assert f"{T4:.10f}" == "0.8806186341" and f"{S4:.10f}" == "0.8818124253"


def parabola(xa, ya, u):
    """Lagrange parabola through three points, evaluated at u."""
    (x0_, x1_, x2_), (y0_, y1_, y2_) = xa, ya
    return (y0_ * (u - x1_) * (u - x2_) / ((x0_ - x1_) * (x0_ - x2_))
            + y1_ * (u - x0_) * (u - x2_) / ((x1_ - x0_) * (x1_ - x2_))
            + y2_ * (u - x0_) * (u - x1_) / ((x2_ - x0_) * (x2_ - x1_)))


panels = []
xx = np.linspace(0, 2.1, 300)
for j, title in enumerate(["Yamuk kuralı: " + sub("T", 4) + " = "
                           + dec(T4, 4),
                           "Simpson kuralı: " + sub("S", 4) + " = "
                           + dec(S4, 4)]):
    p = Plot(50 + j * 330, 34, 270, 200, (-0.08, 2.2), (-0.03, 1.12))
    p.axes([0, 0.5, 1, 1.5, 2], [0, 0.5, 1], it("x"), "", tick, tick)
    if j == 0:
        for k in range(4):
            p.polygon([(xs4[k], 0), (xs4[k], ys4[k]), (xs4[k + 1], ys4[k + 1]),
                       (xs4[k + 1], 0)], BASE, 0.18, BASE, 1.3)
    else:
        for k in (0, 2):
            u = np.linspace(xs4[k], xs4[k + 2], 80)
            v = parabola(xs4[k:k + 3], ys4[k:k + 3], u)
            pts = [(xs4[k], 0)] + list(zip(u, v)) + [(xs4[k + 2], 0)]
            p.polygon(pts, BASE, 0.18, BASE, 1.3)
        p.vline(xs4[1], 0, ys4[1], BASE, "3 3", 0.7)
        p.vline(xs4[3], 0, ys4[3], BASE, "3 3", 0.7)
    p.line(list(zip(xx, gauss(xx))), THEORY, 2.0)
    p.points(list(zip(xs4, ys4)), PRACTICE, 3.6)
    p.label(0.62, gauss(0.62), it("e") + sup(MINUS + it("x") + "²"),
            8, -6, THEORY, 12.5, "start", True)
    panel_title(p, title, TEXT, 12)
    panels.append(p)
save("yamuk-simpson", figure(
    680, 270, panels,
    "<em>e</em><sup>&#8722;<em>x</em>²</sup> fonksiyonunun [0, 2] "
    "aralığındaki integrali, <em>n</em> = 4 alt aralıkla; kuralları kendimiz "
    "yazdığımız kodun ilk iki sonucu. Solda her alt aralıktaki yamuk, sağda ikişer "
    "alt aralığı kaplayan iki parabol. Kesin değer 0,8821'dir: parabollerin "
    "altındaki alan yamukların alanından daha yakındır.",
    css_class=WIDE,
    aria="Two panels with the curve exp(-x^2) on [0, 2] and five nodes. "
         "Left: four shaded trapezoids, T4 = 0.8806. Right: two shaded "
         "parabolic strips through three nodes each, S4 = 0.8818"))


# ============================================================
# yakinsama: error of T_n and S_n against n (the table of b06)
# ============================================================
I_EXACT = math.sqrt(math.pi) / 2 * math.erf(2)
ns = [4, 8, 16, 32, 64, 128, 256]
err_t, err_s = [], []
for n in ns:
    x = np.linspace(0, 2, n + 1)
    y = gauss(x)
    h = 2 / n
    err_t.append(abs(h * (y[0] / 2 + y[1:-1].sum() + y[-1] / 2) - I_EXACT))
    err_s.append(abs(h / 3 * (y[0] + 4 * y[1:-1:2].sum()
                              + 2 * y[2:-1:2].sum() + y[-1]) - I_EXACT))
assert f"{err_t[-1]:.3e}" == "3.726e-07" and f"{err_s[-1]:.3e}" == "1.516e-11"


def nlab(t):
    return str(int(round(10**t)))


p = Plot(70, 24, 370, 250, (lg(3.4), lg(300)), (-11.3, -1.7))
tx = [lg(n) for n in ns]
p.grid(tx, [-10, -8, -6, -4, -2])
p.axes(tx, [-2, -4, -6, -8, -10], it("n"), "hata", nlab,
       lambda t: pow10(t, 9.5))
pts_t = [(lg(n), lg(e)) for n, e in zip(ns, err_t)]
pts_s = [(lg(n), lg(e)) for n, e in zip(ns, err_s)]
p.line(pts_t, BASE, 2.0)
p.points(pts_t, BASE, 3.6)
p.line(pts_s, PRACTICE, 2.0)
p.points(pts_s, PRACTICE, 3.6)
p.label(lg(45), lg(1.2e-5), "yamuk: eğim " + MINUS + "2", 6, -8, BASE, 12,
        "start", True)
p.label(lg(4.7), -8.6, "Simpson: eğim " + MINUS + "4", 0, 0,
        PRACTICE, 12, "start", True)
save("yakinsama", figure(
    470, 320, [p],
    "Kuralları kendimiz yazdığımız kodun tablosu, iki eksen de logaritmik. "
    "<em>n</em> her ikiye katlandığında yamuk kuralının hatası 4'e, "
    "Simpson kuralınınki 16'ya bölünür: doğruların eğimleri &#8722;2 ve "
    "&#8722;4'tür, yani hatalar <em>h</em>² ve <em>h</em>⁴ ile orantılıdır.",
    aria="Log-log plot of the error of the composite trapezoid and Simpson "
         "rules for the integral of exp(-x^2) on [0, 2] against n = 4 ... "
         "256: two straight lines with slopes -2 and -4"))


# ============================================================
# si: the sine integral from cumulative_trapezoid (code b08)
# ============================================================
t = np.linspace(0, 20, 401)
y = np.sinc(t / np.pi)
Si = cumulative_trapezoid(y, t, initial=0)
kmax = Si.argmax()
assert abs(t[kmax] - 3.15) < 1e-12

p = Plot(58, 24, 430, 250, (-0.4, 20.6), (-0.35, 2.05))
p.grid([5, 10, 15, 20], [0.5, 1, 1.5, 2])
p.axes([0, 5, 10, 15, 20], [0, 0.5, 1, 1.5, 2], it("x"), "", tick, tick)
p.line([(0, 0), (20.4, 0)], TEXT, 0.9, opacity=0.5)
p.line([(0, math.pi / 2), (20.4, math.pi / 2)], TEXT, 1.2, "5 4", 0.75)
p.label(20.4, math.pi / 2, PI + "/2", 0, -7, TEXT, 12, "end")
p.line(list(zip(t, y)), REMARK, 1.4, opacity=0.85)
p.line(list(zip(t, Si)), THEORY, 2.1)
p.points([(t[kmax], Si[kmax])], PRACTICE, 4.0)
p.label(t[kmax], Si[kmax], "(" + dec(t[kmax], 2) + "; " + dec(Si[kmax], 4)
        + ")", 8, -8, PRACTICE, 12, "start", True)
p.label(8.0, 1.62, "Si(" + it("x") + ")", 0, -10, THEORY, 12.5, "middle",
        True)
p.label(2.0, 0.62, "sin " + it("t") + "/" + it("t"), 0, 0, REMARK, 12,
        "start", True)
save("si", figure(
    520, 320, [p],
    "<code>cumulative_trapezoid</code> kodunun 401 noktada hesapladığı "
    "Si(<em>x</em>) değerleri (mavi) ve integrali alınan sin <em>t</em>/"
    "<em>t</em> fonksiyonu (gri). Si(<em>x</em>), sin <em>t</em>/<em>t</em> "
    "pozitifken artar, negatifken azalır; en büyük değerine "
    "<em>x</em> = &#960; civarında ulaşır ve &#960;/2 doğrusu etrafında "
    "sönen salınımlarla ona yaklaşır.",
    aria="The sine integral Si(x) on [0, 20] computed with "
         "cumulative_trapezoid, rising to its maximum 1.8519 at x = 3.15 "
         "and oscillating around the dashed line pi/2; the integrand "
         "sin(t)/t is drawn in grey"))


# ============================================================
# quad-tepe: where quad looks for the peak 1/((x - 0.3)^2 + 1e-4)
# ============================================================
calls = []


def peak(x):
    calls.append(x)
    return 1 / ((x - 0.3)**2 + 1e-4)


val, err, info = quad(peak, 0, 1, full_output=1)
ends = np.sort(np.r_[info["alist"][:info["last"]], 1.0])
assert len(calls) == 315 and info["last"] == 8
xcalls = np.array(calls, dtype=float)

p = Plot(70, 24, 420, 240, (-0.02, 1.02), (-900, 10600))
p.grid([0.25, 0.5, 0.75, 1], [2500, 5000, 7500, 10000])
p.axes([0, 0.25, 0.5, 0.75, 1], [0, 5000, 10000], it("x"), "", tick,
       lambda v: f"{int(v):,}".replace(",", "."))
# dense sampling only near the peak keeps the markup small
xx = np.unique(np.r_[np.linspace(0, 1, 201), np.linspace(0.26, 0.34, 241)])
p.line(list(zip(xx, 1 / ((xx - 0.3)**2 + 1e-4))), THEORY, 1.8)
for e in ends:
    p.vline(e, -900, 10600, BASE, "4 3", 0.75)
# the rug of evaluation points as one path (315 short ticks)
rug = " ".join(f"M{p.X(xc):.1f},{p.Y(0) + 4:.1f}V{p.Y(-900):.1f}"
               for xc in xcalls)
p.add(f'<path d="{rug}" stroke="{PRACTICE}" stroke-width="0.8" '
      f'opacity="0.8" fill="none"/>')
p.label(0.33, 9000, it("f") + "(" + it("x") + ") = 1/((" + it("x") + " "
        + MINUS + " 0,3)² + 10" + sup(MINUS + "4") + ")", 8, 0, THEORY,
        12, "start", True)
p.label(0.75, 4200, "8 alt aralık", 0, 0, BASE, 12, "middle", True)
p.label(0.75, 4200, "315 çağrı", 0, 17, PRACTICE, 12, "middle", True)
save("quad-tepe", figure(
    520, 320, [p],
    "<code>quad</code>'ın <em>x</em> = 0,3'teki dar tepeyi nasıl "
    "çözdüğü: tepe fonksiyonu kodunun kaydettiği veriler. Kesikli çizgiler "
    "<code>quad</code>'ın böldüğü 8 alt aralığın uçları, eksenin altındaki "
    "kısa çizgiler fonksiyonun hesaplandığı 315 nokta. Alt aralıklar tepenin "
    "yanında ikiye bölüne bölüne daralır; fonksiyonun düz olduğu yerde tek "
    "geniş aralık yeter.",
    aria="The sharp peak 1/((x - 0.3)^2 + 1e-4) on [0, 1] with the end "
         "points of the 8 subintervals chosen by quad, which shrink near "
         "x = 0.3, and a rug of the 315 evaluation points under the axis"))


# ============================================================
# iki-parabol: the region of the dblquad example and its arguments
# ============================================================
p = Plot(56, 30, 340, 300, (-1.35, 1.35), (-0.3, 2.45))
p.origin_axes(it("x"), it("y"), [], [1, 2], tick, tick)
xx = np.linspace(-1, 1, 200)
region = list(zip(xx, 2 * xx**2)) + list(zip(xx[::-1], 1 + xx[::-1]**2))
p.polygon(region, BASE, 0.16)
xw = np.linspace(-1.3, 1.3, 260)
p.line(list(zip(xw, 1 + xw**2)), THEORY, 2.0)
xw2 = np.linspace(-1.1, 1.1, 220)
p.line(list(zip(xw2, 2 * xw2**2)), PRACTICE, 2.0)
xa = 0.45
p.arrow((xa, 2 * xa**2), (xa, 1 + xa**2), TEXT, 1.6, 8)
p.points([(xa, 2 * xa**2)], TEXT, 3.0)
p.vline(-1, 0, 2, TEXT, "3 3", 0.6)
p.vline(1, 0, 2, TEXT, "3 3", 0.6)
p.points([(-1, 2), (1, 2)], TEXT, 3.4)
p.label(-1, 0, it("a") + " = " + MINUS + "1", 0, 16, TEXT, 12, "middle")
p.label(1, 0, it("b") + " = 1", 0, 16, TEXT, 12, "middle")
p.label(xa, 0, it("x"), 0, 16, TEXT, 12, "middle")
p.vline(xa, 0, 2 * xa**2, TEXT, "2 3", 0.6)
p.label(-0.4, 1.75, "hfun: 1 + " + it("x") + "²", 0, 0, THEORY,
        12, "middle", True)
p.label(0.62, 2 * 0.62**2, "gfun: 2" + it("x") + "²", 10, 8, PRACTICE, 12,
        "start", True)
p.label(-0.45, 0.85, it("D"), 0, 0, BASE, 13, "middle", True)
save("iki-parabol", figure(
    440, 380, [p],
    "<code>dblquad</code> örneğindeki <em>D</em> bölgesi. Dış integral "
    "<em>x</em>'i <em>a</em> = &#8722;1'den <em>b</em> = 1'e götürür; her "
    "<em>x</em> için iç integral <em>y</em>'yi alttaki "
    "<code>gfun(x)</code> = 2<em>x</em>² parabolünden üstteki "
    "<code>hfun(x)</code> = 1 + <em>x</em>² parabolüne kadar tarar (ok).",
    aria="The region D between the parabolas y = 2x^2 (lower, gfun) and "
         "y = 1 + x^2 (upper, hfun) for x from a = -1 to b = 1, with a "
         "vertical arrow from the lower to the upper parabola"))
