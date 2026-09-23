# -*- coding: utf-8 -*-
"""
Figures of the chapter "Tahmin Edicilerin Özellikleri"
(dersler/matematiksel-istatistik/tahmin-edicilerin-ozellikleri.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box: a figure that illustrates a
definition sits directly below that box. The figures are NOT produced at
build time. Run

    python scripts/statistics_figures/tep.py
    python scripts/center_figures.py "statistics-tep-*.md" --keep-width
    python scripts/check_figure_labels.py "scripts/_figures/statistics-tep-*.md"

and paste the markup of scripts/_figures/statistics-tep-<name>.md into the
.qmd. Captions are Turkish on purpose (they are shown on the site); aria
labels are plain ASCII.
"""
import math
import sys
from pathlib import Path

import mpmath as mp

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, WIDE, TEXT, THEORY, PRACTICE, BASE, REMARK  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "statistics-tep-"
OUT = {}

MINUS, APPROX, PM = "&#8722;", "&#8776;", "&#177;"
SIGMA, MU, THETA, LAMBDA, PI_, SQRT, EPS = "&#963;", "&#956;", "&#952;", "&#955;", "&#960;", "&#8730;", "&#949;"
SQ, SUB1, SUB2 = "&#178;", "&#8321;", "&#8322;"
LABEL = 13     # names of curves and marks
TICK = 11      # axis numbers
SAMPLES = 400


def num(v, digits=None):
    """Decimal comma and a real minus sign: -1.52 -> '&#8722;1,52'."""
    if digits is None:
        s = f"{v:.4f}".rstrip("0").rstrip(".")
    else:
        s = f"{v:.{digits}f}"
    if s in ("-0", ""):
        s = "0"
    return s.replace("-", MINUS).replace(".", ",")


def it(s):
    return f'<tspan font-style="italic">{s}</tspan>'


XBAR = '<tspan font-style="italic">X&#773;</tspan>'
SHAT = SIGMA + "&#770;" + SQ          # sigma hat squared
S2 = it("S") + SQ


def T(k):
    return it("T") + (SUB1 if k == 1 else SUB2 if k == 2 else "&#8323;")


# ---------------------------------------------------------------------------
# densities
# ---------------------------------------------------------------------------
def normal_pdf(x, mu, s):
    return math.exp(-0.5 * ((x - mu) / s) ** 2) / (s * math.sqrt(2 * math.pi))


def gamma2_pdf(x, rate):
    """Gamma(2, rate) density: rate^2 x e^(-rate x)."""
    return rate * rate * x * math.exp(-rate * x) if x > 0 else 0.0


def sqrt_product_pdf(t, lam=1.0):
    """Density of sqrt(X1 X2) for two independent Exp(lam): 4 lam^2 t K0(2 lam t)."""
    if t <= 0:
        return 0.0
    return float(4 * lam * lam * t * mp.besselk(0, 2 * lam * t))


# ---------------------------------------------------------------------------
# drawing helpers
# ---------------------------------------------------------------------------
def sample(f, a, b, n=SAMPLES):
    return [(a + (b - a) * k / n, f(a + (b - a) * k / n)) for k in range(n + 1)]


def curve(p, f, a, b, color=THEORY, width=2.0, dash=None, n=SAMPLES):
    pts = sample(f, a, b, n)
    run = []
    for x, y in pts:
        if y <= p.ymax:
            run.append((x, y))
        else:
            if len(run) > 1:
                p.line(run, color, width, dash)
            run = []
    if len(run) > 1:
        p.line(run, color, width, dash)


def shade(p, f, a, b, color=PRACTICE, opacity=0.25, n=240):
    pts = [(a, 0)] + [(x, min(y, p.ymax)) for x, y in sample(f, a, b, n)] + [(b, 0)]
    p.polygon(pts, color, opacity)


def x_axis(p, ticks, name=""):
    Y = p.Y(0)
    left, right = p.x0 - 4, p.x0 + p.w + 10
    p.add(f'<g stroke="{TEXT}" stroke-width="1.1" opacity="0.5" fill="{TEXT}">'
          f'<line x1="{left:.1f}" y1="{Y:.1f}" x2="{right:.1f}" y2="{Y:.1f}"/>'
          f'<polygon points="{right:.1f},{Y:.1f} {right-8:.1f},{Y-3.5:.1f} {right-8:.1f},{Y+3.5:.1f}" stroke="none"/></g>')
    for v, lab in ticks:
        X = p.X(v)
        p.add(f'<line x1="{X:.1f}" y1="{Y-3:.1f}" x2="{X:.1f}" y2="{Y+3:.1f}" stroke="{TEXT}" stroke-width="1" opacity="0.7"/>')
        if lab:
            p.add(f'<text x="{X:.1f}" y="{Y+16:.1f}" fill="{TEXT}" font-size="{TICK}" text-anchor="middle" opacity="0.8">{lab}</text>')
    if name:
        p.add(f'<text x="{right+4:.1f}" y="{Y+4:.1f}" fill="{TEXT}" font-size="12" font-style="italic" opacity="0.85">{name}</text>')


def y_axis(p, ticks, name="", x=None):
    X = p.X(p.xmin if x is None else x)
    top, bottom = p.y0 - 10, p.Y(0)
    p.add(f'<g stroke="{TEXT}" stroke-width="1.1" opacity="0.5" fill="{TEXT}">'
          f'<line x1="{X:.1f}" y1="{bottom:.1f}" x2="{X:.1f}" y2="{top:.1f}"/>'
          f'<polygon points="{X:.1f},{top:.1f} {X-3.5:.1f},{top+8:.1f} {X+3.5:.1f},{top+8:.1f}" stroke="none"/></g>')
    for v, lab in ticks:
        Y = p.Y(v)
        p.add(f'<line x1="{X-3:.1f}" y1="{Y:.1f}" x2="{X+3:.1f}" y2="{Y:.1f}" stroke="{TEXT}" stroke-width="1" opacity="0.7"/>')
        p.add(f'<text x="{X-7:.1f}" y="{Y+4:.1f}" fill="{TEXT}" font-size="{TICK}" text-anchor="end" opacity="0.8">{lab}</text>')
    if name:
        p.add(f'<text x="{X+8:.1f}" y="{top+6:.1f}" fill="{TEXT}" font-size="12" font-style="italic" opacity="0.85">{name}</text>')


def ticks(vals, digits=None):
    return [(v, num(v, digits)) for v in vals]


def legend(p, px, py, entries, size=12.5, row=20):
    """Legend at pixel (px, py) = top-left; entries are (color, dash, text)."""
    for k, (color, dash, s) in enumerate(entries):
        y = py + k * row
        da = f' stroke-dasharray="{dash}"' if dash else ""
        p.add(f'<line x1="{px:.1f}" y1="{y:.1f}" x2="{px+24:.1f}" y2="{y:.1f}" stroke="{color}" stroke-width="2.4"{da} stroke-linecap="round"/>')
        p.text_px(px + 31, y + 4.5, s, TEXT, size)


def hbar(p, y, x0, x1, color, height, opacity=0.8):
    p.add(f'<rect x="{p.X(x0):.1f}" y="{p.Y(y) - height / 2:.1f}" width="{max(p.X(x1) - p.X(x0), 0.8):.1f}" '
          f'height="{height}" fill="{color}" opacity="{opacity}" rx="1.5"/>')


def emit(name, W, H, panels, caption, css_class="ders-grafik", aria=""):
    OUT[name] = figure(W, H, panels, caption, css_class, aria)


# ============================================================
# bolen: sampling densities of S^2 and sigma-hat^2, normal population, n = 5
# ============================================================
def fig_divisor():
    p = Plot(62, 44, 450, 210, (0, 3.2), (0, 1.1))
    p.grid([0.5, 1, 1.5, 2, 2.5, 3], [0.25, 0.5, 0.75, 1.0])
    f_s2 = lambda s: gamma2_pdf(s, 2.0)        # S^2 = chi2_4 / 4
    f_hat = lambda v: gamma2_pdf(v, 2.5)       # sigma-hat^2 = chi2_4 / 5
    curve(p, f_s2, 0, 3.2, THEORY, 2.3)
    curve(p, f_hat, 0, 3.2, PRACTICE, 2.3, "7 4")
    p.vline(1.0, 0, 1.0, THEORY, "4 3", 0.9)
    p.vline(0.8, 0, 1.0, PRACTICE, "4 3", 0.9)
    p.label(1.0, 1.0, "E(" + S2 + ") = " + SIGMA + SQ + " = 1", 6, 2, THEORY, LABEL)
    p.label(0.8, 1.0, "E(" + SHAT + ") = 0,8", -6, 2, PRACTICE, LABEL, "end")
    x_axis(p, ticks([0, 0.5, 1, 1.5, 2, 2.5, 3]), "")
    y_axis(p, ticks([0.25, 0.5, 0.75, 1.0]), "yoğunluk")
    legend(p, p.X(1.75), p.Y(0.78), [(THEORY, None, S2 + ": " + it("n") + " " + MINUS + " 1'e bölünür"),
                                     (PRACTICE, "7 4", SHAT + ": " + it("n") + "'ye bölünür")])
    emit("bolen", 560, 300, [p],
         "Varyansı σ² = 1 olan normal bir kitleden alınan n = 5 birimlik örneklemlerde iki varyans "
         "tahmin edicisinin dağılımı. n − 1'e bölünen S²'nin ortalaması tam σ² = 1'dir; n'ye bölünen "
         "σ̂² ise sola kaymıştır ve ortalaması (n − 1)/n · σ² = 0,8 olur.",
         aria="Densities of the sample variance with divisor n minus 1 and with divisor n for n 5; means 1 and 0.8")


# ============================================================
# asimptotik: E(sigma-hat^2)/sigma^2 = (n-1)/n against n
# ============================================================
def fig_asymptotic():
    p = Plot(70, 40, 440, 210, (0, 31), (0, 1.1))
    p.grid([5, 10, 15, 20, 25, 30], [0.25, 0.5, 0.75, 1.0])
    p.line([(0, 1), (30.5, 1)], BASE, 1.6, "6 4")
    pts = [(n, (n - 1) / n) for n in range(2, 31)]
    p.line(pts, PRACTICE, 1.2, None, 0.5)
    p.points(pts, PRACTICE, 3.4)
    p.label(30.5, 1, "hedef: " + SIGMA + SQ, -2, -9, BASE, LABEL, "end")
    p.label(2, 0.5, it("n") + " = 2: 0,5 " + SIGMA + SQ, 10, 5, PRACTICE, LABEL)
    p.label(10, 0.9, it("n") + " = 10: 0,9 " + SIGMA + SQ, 4, 22, PRACTICE, LABEL)
    x_axis(p, ticks([0, 5, 10, 15, 20, 25, 30]), it("n"))
    y_axis(p, ticks([0.25, 0.5, 0.75, 1.0], 2), "E(" + SHAT + ") / " + SIGMA + SQ)
    emit("asimptotik", 560, 290, [p],
         "n'ye bölünen varyans tahmin edicisi σ̂²'nin beklenen değeri σ²'nin (n − 1)/n katıdır. "
         "Her n için hedefin altında kalır (yanlıdır), ama n büyüdükçe oran 1'e yaklaşır: "
         "σ̂² asimptotik olarak yansızdır.",
         aria="Points (n minus 1) over n for n from 2 to 30 approaching the dashed line at 1")


# ============================================================
# yan-varyans: bias and spread of an estimator
# ============================================================
def fig_bias_variance():
    p = Plot(40, 40, 480, 200, (0, 10), (0, 0.4))
    m, s, th = 6.0, 1.2, 3.6
    f = lambda x: normal_pdf(x, m, s)
    shade(p, f, 0.2, 9.8, THEORY, 0.12)
    curve(p, f, 0.2, 9.8, THEORY, 2.3)
    p.vline(th, 0, 0.36, PRACTICE, "5 3", 1.0)
    p.vline(m, 0, f(m), THEORY, "4 3", 0.9)
    x_axis(p, [(th, ""), (m, "")])
    p.label(th, 0, THETA, 0, 18, PRACTICE, 14, "middle", True, True)
    p.label(m, 0, "E(" + it("T") + ")", 0, 18, THEORY, 13, "middle", True)
    # bias arrow
    p.arrow((th, 0.36), (m, 0.36), PRACTICE, 1.8, 8)
    p.label((th + m) / 2, 0.36, "yanlılık = E(" + it("T") + ") " + MINUS + " " + THETA, 0, -9, PRACTICE, LABEL, "middle")
    # spread: +- one standard deviation at the inflection height
    h = f(m + s)
    p.arrow((m, h), (m + s, h), TEXT, 1.4, 7)
    p.arrow((m, h), (m - s, h), TEXT, 1.4, 7)
    p.label(m + s, h, "yayılım: " + SQRT + "Var(" + it("T") + ")", 10, 4, TEXT, LABEL)
    p.label(1.9, 0.12, "dağılımı", 0, 0, THEORY, LABEL, "middle")
    p.label(1.9, 0.12, it("T") + "'nin", 0, -16, THEORY, LABEL, "middle")
    emit("yan-varyans", 560, 280, [p],
         "Bir T tahmin edicisinin dağılımı. Hata kareler ortalaması iki parçadan oluşur: dağılımın merkezi "
         "E(T)'nin hedef θ'dan uzaklığı (yanlılık) ve dağılımın kendi merkezi çevresindeki yayılımı (varyans).",
         aria="Bell shaped density of an estimator centred at E of T, an arrow from theta to E of T marks the bias, a double arrow marks the spread")


# ============================================================
# ustel-yogunluk: densities of T1 = (X1+X2)/2 and T2 = sqrt(X1 X2), lambda = 1
# ============================================================
def fig_exp_densities():
    p = Plot(62, 44, 450, 230, (0, 3.6), (0, 1.2))
    p.grid([0.5, 1, 1.5, 2, 2.5, 3, 3.5], [0.25, 0.5, 0.75, 1.0])
    f1 = lambda t: gamma2_pdf(t, 2.0)
    curve(p, f1, 0, 3.6, THEORY, 2.3)
    curve(p, sqrt_product_pdf, 1e-6, 3.6, PRACTICE, 2.3, "7 4")
    p.vline(1.0, 0, 1.1, THEORY, "4 3", 0.9)
    p.vline(math.pi / 4, 0, 1.1, PRACTICE, "4 3", 0.9)
    p.label(1.0, 1.1, "E(" + T(1) + ") = 1/" + LAMBDA + " = 1", 6, 2, THEORY, LABEL)
    p.label(math.pi / 4, 1.1, "E(" + T(2) + ") = " + PI_ + "/4 " + APPROX + " 0,79", -6, 2, PRACTICE, LABEL, "end")
    x_axis(p, ticks([0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5]), it("t"))
    y_axis(p, ticks([0.25, 0.5, 0.75, 1.0], 2), "yoğunluk")
    legend(p, p.X(1.75), p.Y(0.8), [(THEORY, None, T(1) + " = (" + it("X") + SUB1 + " + " + it("X") + SUB2 + ")/2"),
                                     (PRACTICE, "7 4", T(2) + " = " + SQRT + "(" + it("X") + SUB1 + it("X") + SUB2 + ")")])
    emit("ustel-yogunluk", 560, 300, [p],
         "λ = 1 iken iki tahmin edicinin dağılımı. T₁'in ortalaması hedef 1/λ = 1'dir; T₂'nin ortalaması "
         "π/4 ≈ 0,79 ile hedefin solunda kalır, ama T₂ ortalaması çevresinde daha dar toplanır.",
         aria="Densities of the mean and of the geometric mean of two exponential observations with rate 1")


# ============================================================
# ustel-hko: MSE = variance + bias^2 for T1, T2, T3 (lambda = 1)
# ============================================================
def fig_exp_mse():
    p = Plot(190, 30, 330, 170, (0, 0.72), (0, 3.6))
    p.grid([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7], [])
    v1, v2, v3 = 0.5, (16 - math.pi ** 2) / 16, (16 - math.pi ** 2) / math.pi ** 2
    b2 = (math.pi / 4 - 1) ** 2
    rows = [(3, T(1) + " = (" + it("X") + SUB1 + " + " + it("X") + SUB2 + ")/2", v1, 0.0),
            (2, T(2) + " = " + SQRT + "(" + it("X") + SUB1 + it("X") + SUB2 + ")", v2, b2),
            (1, T(3) + " = (4/" + PI_ + ")" + SQRT + "(" + it("X") + SUB1 + it("X") + SUB2 + ")", v3, 0.0)]
    for y, name, v, bb in rows:
        hbar(p, y, 0, v, THEORY, 26, 0.75)
        if bb > 0:
            hbar(p, y, v, v + bb, PRACTICE, 26, 0.9)
        p.label(0, y, name, -12, 4.5, TEXT, LABEL, "end")
        p.label(v + bb, y, num(v + bb, 3), 7, 4.5, TEXT, LABEL, "start", True)
    x_axis(p, ticks([0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7], 1), "")
    p.text_px(p.X(0.36), p.Y(0) + 36, "hata kareler ortalaması (" + LAMBDA + " = 1)", TEXT, 12, "middle")
    # legend below
    lx, ly = p.X(0.02), p.Y(0) + 60
    p.add(f'<rect x="{lx:.1f}" y="{ly - 9:.1f}" width="14" height="11" fill="{THEORY}" opacity="0.75" rx="1.5"/>')
    p.text_px(lx + 20, ly + 1, "varyans", TEXT, 12.5)
    p.add(f'<rect x="{lx + 110:.1f}" y="{ly - 9:.1f}" width="14" height="11" fill="{PRACTICE}" opacity="0.9" rx="1.5"/>')
    p.text_px(lx + 130, ly + 1, "yanlılığın karesi", TEXT, 12.5)
    emit("ustel-hko", 600, 300, [p],
         "λ = 1 iken üç tahmin edicinin hata kareler ortalaması, varyans ve yanlılığın karesi olarak parçalanmış. "
         "T₁ ile T₃ yansızdır; yanlı olan T₂'nin küçük bir yanlılık karşılığında kazandığı varyans, "
         "onu en küçük hata kareler ortalamasına taşır.",
         aria="Horizontal stacked bars of variance and squared bias for three estimators: 0.5, 0.429 and 0.621")


# ============================================================
# etkinlik: X1 against Xbar (n = 4), normal population
# ============================================================
def fig_efficiency():
    p = Plot(40, 44, 480, 200, (-3.6, 3.6), (0, 0.85))
    f1 = lambda x: normal_pdf(x, 0, 1)
    f4 = lambda x: normal_pdf(x, 0, 0.5)
    shade(p, f1, -1, 1, THEORY, 0.10)
    shade(p, f4, -1, 1, PRACTICE, 0.18)
    curve(p, f1, -3.6, 3.6, THEORY, 2.3, "7 4")
    curve(p, f4, -3.6, 3.6, PRACTICE, 2.3)
    p.vline(0, 0, 0.82, TEXT, "4 3", 0.6)
    labs = {-3: MU + " " + MINUS + " 3" + SIGMA, -2: MU + " " + MINUS + " 2" + SIGMA, -1: MU + " " + MINUS + " " + SIGMA,
            0: MU, 1: MU + " + " + SIGMA, 2: MU + " + 2" + SIGMA, 3: MU + " + 3" + SIGMA}
    x_axis(p, [(k, labs[k]) for k in range(-3, 4)])
    legend(p, p.X(-3.5), p.Y(0.8), [(THEORY, "7 4", it("X") + SUB1 + ": varyans " + SIGMA + SQ),
                                    (PRACTICE, None, XBAR + " (" + it("n") + " = 4): varyans " + SIGMA + SQ + "/4")])
    p.label(3.6, 0.66, "P(|" + XBAR + " " + MINUS + " " + MU + "| " + "&lt; " + SIGMA + ") " + APPROX + " 0,95", 0, 0, PRACTICE, 12.5, "end")
    p.label(3.6, 0.66, "P(|" + it("X") + SUB1 + " " + MINUS + " " + MU + "| " + "&lt; " + SIGMA + ") " + APPROX + " 0,68", 0, 20, THEORY, 12.5, "end")
    emit("etkinlik", 560, 290, [p],
         "Normal bir kitlede μ'nün iki yansız tahmin edicisi. İkisi de μ çevresinde toplanır, ama n = 4 iken "
         "X̄'in varyansı X₁'inkinin dörtte biridir: μ'ye σ'dan yakın düşme olasılığı X₁ için yaklaşık 0,68, "
         "X̄ için yaklaşık 0,95'tir.",
         aria="Two normal densities centred at mu, a wide one for a single observation and a narrow one for the mean of four")


# ============================================================
# tutarlilik: densities of Xbar for n = 1, 4, 16, 64 and the band mu +- eps
# ============================================================
def fig_consistency():
    p = Plot(56, 40, 470, 230, (-3.2, 3.2), (0, 3.4))
    eps = 0.5
    p.polygon([(-eps, 0), (eps, 0), (eps, 3.3), (-eps, 3.3)], BASE, 0.10)
    p.vline(-eps, 0, 3.3, BASE, "4 3", 0.8)
    p.vline(eps, 0, 3.3, BASE, "4 3", 0.8)
    styles = [(1, BASE, "2 4"), (4, REMARK, "7 4"), (16, THEORY, None), (64, PRACTICE, None)]
    entries = []
    for n, c, d in styles:
        s = 1 / math.sqrt(n)
        curve(p, lambda x, s=s: normal_pdf(x, 0, s), -3.2, 3.2, c, 2.2, d, 600)
        out = 2 * (1 - float(mp.ncdf(eps * math.sqrt(n))))
        entries.append((c, d, it("n") + " = " + str(n) + ":  " + num(out, 4)))
    x_axis(p, [(-3, MU + " " + MINUS + " 3"), (-eps, ""), (0, MU), (eps, ""), (3, MU + " + 3")])
    p.label(-eps, 0, MU + " " + MINUS + " " + EPS, 0, 30, BASE, 12, "middle")
    p.label(eps, 0, MU + " + " + EPS, 0, 30, BASE, 12, "middle")
    p.label(1.0, 3.25, "P(|" + XBAR + " " + MINUS + " " + MU + "| " + "&#8805; " + EPS + ")", 0, 0, TEXT, 12.5)
    legend(p, p.X(1.0), p.Y(3.25) + 22, entries, 12.5, 21)
    emit("tutarlilik", 600, 320, [p],
         "σ = 1 olan normal bir kitlede X̄'in dağılımı n = 1, 4, 16, 64 için; taralı şerit μ ± ε, ε = 0,5. "
         "n büyüdükçe dağılım μ'nün çevresine sıkışır ve şeridin dışına düşme olasılığı sıfıra gider: "
         "X̄, μ'nün tutarlı bir tahmin edicisidir.",
         aria="Normal densities of the sample mean for n 1, 4, 16, 64 becoming narrower around mu; a band of half width 0.5 is shaded")


# ============================================================
# duzgun-hko: MSE / theta^2 of 2 Xbar, max X_i and (n+1)/n max X_i for U(0, theta)
# ============================================================
def fig_uniform_mse():
    p = Plot(70, 40, 440, 220, (0, 20.8), (0, 0.36))
    p.grid([5, 10, 15, 20], [0.1, 0.2, 0.3])
    series = [(lambda n: 1 / (3 * n), BASE, "7 4", "2" + XBAR + " (yansız)"),
              (lambda n: 2 / ((n + 1) * (n + 2)), PRACTICE, None, "max " + it("X") + "<tspan font-size=\"10\" dy=\"4\">i</tspan><tspan dy=\"-4\">&#8203;</tspan> (yanlı)"),
              (lambda n: 1 / (n * (n + 2)), THEORY, None, "(" + it("n") + " + 1)/" + it("n") + " · max " + it("X") + "<tspan font-size=\"10\" dy=\"4\">i</tspan><tspan dy=\"-4\">&#8203;</tspan> (yansız)")]
    for f, c, d, _ in series:
        pts = [(n, f(n)) for n in range(1, 21)]
        p.line(pts, c, 1.8, d, 0.9)
        p.points(pts, c, 3.0)
    x_axis(p, ticks([0, 5, 10, 15, 20]), it("n"))
    y_axis(p, ticks([0.1, 0.2, 0.3], 1), "HKO / " + THETA + SQ)
    legend(p, p.X(7.5), p.Y(0.33), [(c, d, s) for _, c, d, s in series], 12.5, 21)
    p.label(1, 1 / 3, it("n") + " = 1: üçü de 1/3", 9, -2, TEXT, 12)
    emit("duzgun-hko", 560, 310, [p],
         "U(0, θ) kitlesinde üç tahmin edicinin hata kareler ortalaması (θ² birimiyle) örneklem hacmine göre. "
         "n = 1'de üçü aynıdır; n büyüdükçe en büyük gözleme dayanan iki tahmin edicinin HKO'su "
         "2X̄'inkinden çok daha hızlı küçülür.",
         aria="Mean squared errors of three estimators of theta for the uniform distribution against n from 1 to 20")


def main():
    fig_divisor()
    fig_asymptotic()
    fig_bias_variance()
    fig_exp_densities()
    fig_exp_mse()
    fig_uniform_mse()
    fig_efficiency()
    fig_consistency()
    for name, md in OUT.items():
        path = OUT_DIR / f"{PREFIX}{name}.md"
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(md)
        print("wrote", path.name)


if __name__ == "__main__":
    main()
