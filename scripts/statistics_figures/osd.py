# -*- coding: utf-8 -*-
"""
Figures of the chapter "Önemli Sürekli Dağılımlar"
(dersler/matematiksel-istatistik/onemli-surekli-dagilimlar.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box: a figure that illustrates a
definition sits directly below that box. The figures are NOT produced at
build time. Run

    python scripts/statistics_figures/osd.py
    python scripts/center_figures.py "statistics-osd-*.md" --keep-width
    python scripts/check_figure_labels.py "scripts/_figures/statistics-osd-*.md"

and paste the markup of scripts/_figures/statistics-osd-<name>.md into the
.qmd. Captions are Turkish on purpose (they are shown on the site); aria
labels are plain ASCII.
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, WIDE, TEXT, THEORY, PRACTICE, BASE, REMARK  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "statistics-osd-"
OUT = {}

MINUS, APPROX = "&#8722;", "&#8776;"
ALPHA, BETA, GAMMA_, SIGMA, MU, THETA = "&#945;", "&#946;", "&#915;", "&#963;", "&#956;", "&#952;"
GAMMA_SMALL, PI_, SQRT, LT = "&#947;", "&#960;", "&#8730;", "&lt;"
LABEL = 13     # names of curves and areas
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


# ---------------------------------------------------------------------------
# densities
# ---------------------------------------------------------------------------
def gamma_pdf(x, r, a):
    if x <= 0:
        return 0.0
    return a / math.gamma(r) * (a * x) ** (r - 1) * math.exp(-a * x)


def beta_pdf(x, a, b):
    if x <= 0 or x >= 1:
        return 0.0
    B = math.gamma(a) * math.gamma(b) / math.gamma(a + b)
    return x ** (a - 1) * (1 - x) ** (b - 1) / B


def weibull_pdf(y, a, g):
    if y <= 0:
        return 0.0
    return g * a * y ** (g - 1) * math.exp(-a * y ** g)


def cauchy_pdf(x, c, th):
    return c / (math.pi * (c * c + (x - th) ** 2))


def normal_pdf(x, mu, s):
    return math.exp(-0.5 * ((x - mu) / s) ** 2) / (s * math.sqrt(2 * math.pi))


def lognormal_pdf(x, mu, s):
    if x <= 0:
        return 0.0
    return math.exp(-(math.log(x) - mu) ** 2 / (2 * s * s)) / (x * s * math.sqrt(2 * math.pi))


# ---------------------------------------------------------------------------
# drawing helpers
# ---------------------------------------------------------------------------
def sample(f, a, b, n=SAMPLES):
    return [(a + (b - a) * k / n, f(a + (b - a) * k / n)) for k in range(n + 1)]


def curve(p, f, a, b, color=THEORY, width=2.0, dash=None, n=SAMPLES):
    """Plot f on [a, b]; pieces above the panel top are dropped (clipping)."""
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


def shade(p, f, a, b, color=PRACTICE, opacity=0.30, n=240):
    pts = [(a, 0)] + [(x, min(y, p.ymax)) for x, y in sample(f, a, b, n)] + [(b, 0)]
    p.polygon(pts, color, opacity)


def x_axis(p, ticks, name=""):
    """Horizontal axis at y = 0 with an arrow head; ticks are (value, label) pairs."""
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
    """Vertical axis with an arrow head; ticks are (value, label) pairs."""
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


def legend(p, px, py, entries, size=12.5, row=19):
    """Legend box at pixel (px, py) = top-left; entries are (color, dash, text)."""
    for k, (color, dash, s) in enumerate(entries):
        y = py + k * row
        da = f' stroke-dasharray="{dash}"' if dash else ""
        p.add(f'<line x1="{px:.1f}" y1="{y:.1f}" x2="{px+24:.1f}" y2="{y:.1f}" stroke="{color}" stroke-width="2.4"{da} stroke-linecap="round"/>')
        p.text_px(px + 31, y + 4.5, s, TEXT, size)


def title(p, s, size=12.5):
    p.text_px(p.x0 + p.w / 2, p.y0 - 16, s, TEXT, size, "middle", True)


def emit(name, W, H, panels, caption, css_class="ders-grafik", aria=""):
    OUT[name] = figure(W, H, panels, caption, css_class, aria)


# ============================================================
# duzgun-olasilik: U(2, 8) density, P(3 < X < 6) shaded
# ============================================================
def fig_uniform():
    p = Plot(62, 40, 450, 210, (0, 10), (0, 0.25))
    h = 1 / 6
    p.polygon([(3, 0), (3, h), (6, h), (6, 0)], PRACTICE, 0.30)
    p.line([(0, 0), (2, 0)], THEORY, 2.2)
    p.line([(2, h), (8, h)], THEORY, 2.2)
    p.line([(8, 0), (9.6, 0)], THEORY, 2.2)
    p.vline(2, 0, h, THEORY, "4 3", 0.8)
    p.vline(8, 0, h, THEORY, "4 3", 0.8)
    x_axis(p, [(v, num(v)) for v in (0, 2, 3, 4, 5, 6, 7, 8, 10)], it("x"))
    y_axis(p, [(h, "1/6")], it("f") + "(" + it("x") + ")")
    p.label(4.5, h / 2, "P(3 " + LT + " " + it("X") + " " + LT + " 6) = 1/2", 0, 5, TEXT, LABEL, "middle")
    p.label(5, h, it("f") + "(" + it("x") + ") = 1/6", 0, -10, THEORY, LABEL, "middle")
    emit("duzgun-olasilik", 560, 290, [p],
         "U(2, 8) yoğunluğu 2 ile 8 arasında 1/6 yüksekliğinde bir dikdörtgendir. "
         "3 ile 6 arasındaki taralı dikdörtgenin alanı 3 · 1/6 = 1/2 olasılığını verir.",
         aria="Uniform density on 2 to 8 with height one sixth; the strip between 3 and 6 is shaded")


# ============================================================
# gamma-fonksiyonu: graph of the gamma function on (0, 4.4]
# ============================================================
def fig_gamma_function():
    p = Plot(62, 40, 450, 230, (0, 4.6), (0, 8))
    p.grid([1, 2, 3, 4], [2, 4, 6])
    curve(p, math.gamma, 0.05, 4.45, THEORY, 2.2, n=600)
    pts = [(0.5, math.sqrt(math.pi)), (1, 1), (2, 1), (3, 2), (4, 6)]
    p.points(pts, PRACTICE, 4.2)
    p.label(0.5, math.sqrt(math.pi), GAMMA_ + "(1/2) = " + SQRT + PI_, 10, -8, TEXT, LABEL)
    p.label(1, 1, GAMMA_ + "(1) = 1", -9, 17, TEXT, LABEL, "end")
    p.label(2, 1, GAMMA_ + "(2) = 1", 6, 19, TEXT, LABEL)
    p.label(3, 2, GAMMA_ + "(3) = 2", 8, 18, TEXT, LABEL)
    p.label(4, 6, GAMMA_ + "(4) = 6", 10, 16, TEXT, LABEL)
    x_axis(p, ticks([0, 1, 2, 3, 4]), it("p"))
    y_axis(p, ticks([2, 4, 6, 8]), GAMMA_ + "(" + it("p") + ")")
    emit("gamma-fonksiyonu", 560, 310, [p],
         "Gamma fonksiyonunun grafiği. Tam sayılarda faktöriyel değerlerinden geçer: "
         "Γ(n) = (n − 1)!. Γ(1/2) = √π ≈ 1,77 olur; p → 0 iken Γ(p) sınırsız büyür.",
         aria="Graph of the gamma function with the points at one half, 1, 2, 3 and 4 marked")


# ============================================================
# gamma-aileleri: Gamma(r, alpha) densities, two panels
# ============================================================
def fig_gamma_families():
    p1 = Plot(52, 44, 270, 210, (0, 12), (0, 1.0))
    styles = [(THEORY, None), (PRACTICE, None), (REMARK, "7 4"), (BASE, "2 4")]
    for (r, (c, d)) in zip([1, 2, 3, 5], styles):
        curve(p1, lambda x, r=r: gamma_pdf(x, r, 1.0), 1e-4, 12, c, 2.1, d)
    x_axis(p1, ticks([0, 2, 4, 6, 8, 10, 12]), it("x"))
    y_axis(p1, ticks([0.5, 1.0], 1), it("f") + "(" + it("x") + ")")
    title(p1, ALPHA + " = 1, " + it("r") + " değişiyor")
    legend(p1, p1.X(6.2), p1.Y(0.93), [(c, d, it("r") + " = " + str(r)) for r, (c, d) in zip([1, 2, 3, 5], styles)])

    p2 = Plot(410, 44, 270, 210, (0, 8), (0, 0.8))
    for (a, (c, d)) in zip([2, 1, 0.5], styles):
        curve(p2, lambda x, a=a: gamma_pdf(x, 2, a), 1e-4, 8, c, 2.1, d)
    x_axis(p2, ticks([0, 2, 4, 6, 8]), it("x"))
    y_axis(p2, ticks([0.2, 0.4, 0.6, 0.8], 1), it("f") + "(" + it("x") + ")")
    title(p2, it("r") + " = 2, " + ALPHA + " değişiyor")
    legend(p2, p2.X(4.3), p2.Y(0.75), [(c, d, ALPHA + " = " + num(a)) for a, (c, d) in zip([2, 1, 0.5], styles)])
    emit("gamma-aileleri", 720, 300, [p1, p2],
         "Gamma(r, α) yoğunlukları. Solda α = 1 iken r büyüdükçe tepe sağa kayar ve eğri yayvanlaşır; "
         "r = 1 üstel yoğunluktur. Sağda r = 2 iken α büyüdükçe yoğunluk sıfıra doğru sıkışır: "
         "α bir ölçek (oran) parametresidir.",
         WIDE, aria="Gamma densities: left panel alpha 1 with r 1, 2, 3, 5; right panel r 2 with alpha 2, 1, 0.5")


# ============================================================
# ustel-kuyruk: exponential lifetime, P(X > 1500) shaded
# ============================================================
def fig_exponential_tail():
    a = 0.001
    f = lambda x: a * math.exp(-a * x)
    p = Plot(78, 40, 440, 210, (0, 5000), (0, 0.0011))
    shade(p, f, 1500, 5000)
    curve(p, f, 0, 5000, THEORY, 2.2)
    p.vline(1500, 0, f(1500), PRACTICE, "4 3", 0.9)
    x_axis(p, ticks([0, 1000, 1500, 2000, 3000, 4000, 5000]), it("x"))
    y_axis(p, [(0.0005, "0,0005"), (0.001, "0,001")], it("f") + "(" + it("x") + ")")
    p.label(2600, 0.00058, "P(" + it("X") + " &gt; 1500) = " + it("e") + "<tspan font-size=\"10\" dy=\"-5\">" + MINUS + "1,5</tspan><tspan dy=\"5\">&#8203;</tspan> " + APPROX + " 0,2231",
            0, 0, TEXT, LABEL, "start")
    p.line([(2580, 0.00055), (2350, 0.00005)], TEXT, 1.0, None, 0.6)
    emit("ustel-kuyruk", 560, 290, [p],
         "Ortalama ömrü 1000 saat olan ampulün ömür yoğunluğu (α = 0,001). "
         "1500 saatin sağında kalan taralı alan, ampulün 1500 saatten uzun yanma olasılığıdır.",
         aria="Exponential density with rate 0.001; the tail beyond 1500 is shaded")


# ============================================================
# gamma-tamir: Gamma(2, 1/2) total repair time, P(X > 4) shaded
# ============================================================
def fig_gamma_repair():
    f = lambda x: gamma_pdf(x, 2, 0.5)
    p = Plot(62, 40, 450, 210, (0, 16), (0, 0.2))
    shade(p, f, 4, 16)
    curve(p, f, 0, 16, THEORY, 2.2)
    p.vline(4, 0, f(4), PRACTICE, "4 3", 0.9)
    x_axis(p, ticks([0, 2, 4, 6, 8, 10, 12, 14, 16]), it("x"))
    y_axis(p, ticks([0.05, 0.1, 0.15, 0.2], 2), it("f") + "(" + it("x") + ")")
    p.label(7.6, 0.15, "P(" + it("T") + " &gt; 4) = 3" + it("e") + "<tspan font-size=\"10\" dy=\"-5\">" + MINUS + "2</tspan><tspan dy=\"5\">&#8203;</tspan> " + APPROX + " 0,4060",
            0, 0, TEXT, LABEL)
    p.line([(8.2, 0.142), (7.0, 0.035)], TEXT, 1.0, None, 0.6)
    p.label(9.4, 0.095, it("f") + "(" + it("x") + ") = " + it("x") + it("e") + "<tspan font-size=\"10\" dy=\"-5\">" + MINUS + it("x") + "/2</tspan><tspan dy=\"5\">&#8203;</tspan>/4",
            0, 0, THEORY, LABEL)
    emit("gamma-tamir", 560, 290, [p],
         "İki arızanın toplam onarım süresi Gamma(2, 1/2) dağılımlıdır. "
         "4 saatin sağındaki taralı alan, toplam sürenin 4 saati aşma olasılığıdır.",
         aria="Gamma density with r 2 and alpha one half; the tail beyond 4 is shaded")


# ============================================================
# beta-aileleri: Beta(alpha, beta) densities, two panels
# ============================================================
def fig_beta_families():
    styles = [(THEORY, None), (PRACTICE, None), (REMARK, "7 4"), (BASE, "2 4")]
    p1 = Plot(52, 44, 270, 220, (0, 1), (0, 4))
    sym = [(1, 1), (2, 2), (5, 5), (0.5, 0.5)]
    for (a, b), (c, d) in zip(sym, styles):
        curve(p1, lambda x, a=a, b=b: beta_pdf(x, a, b), 0.0005, 0.9995, c, 2.1, d, n=800)
    x_axis(p1, ticks([0, 0.25, 0.5, 0.75, 1], 2), it("x"))
    y_axis(p1, ticks([1, 2, 3, 4]), it("f") + "(" + it("x") + ")")
    title(p1, "Simetrik: " + ALPHA + " = " + BETA)
    legend(p1, p1.X(0.08), p1.Y(3.85),
           [(c, d, ALPHA + " = " + BETA + " = " + num(a)) for (a, b), (c, d) in zip(sym, styles)])

    p2 = Plot(410, 44, 270, 220, (0, 1), (0, 4))
    asym = [(2, 5), (5, 2), (1, 3)]
    for (a, b), (c, d) in zip(asym, styles):
        curve(p2, lambda x, a=a, b=b: beta_pdf(x, a, b), 0.0005, 0.9995, c, 2.1, d, n=800)
    x_axis(p2, ticks([0, 0.25, 0.5, 0.75, 1], 2), it("x"))
    y_axis(p2, ticks([1, 2, 3, 4]), it("f") + "(" + it("x") + ")")
    title(p2, "Çarpık: " + ALPHA + " ≠ " + BETA)
    legend(p2, p2.X(0.30), p2.Y(3.85),
           [(c, d, ALPHA + " = " + num(a) + ", " + BETA + " = " + num(b)) for (a, b), (c, d) in zip(asym, styles)])
    emit("beta-aileleri", 720, 310, [p1, p2],
         "Beta(α, β) yoğunlukları (0, 1) aralığında yaşar. α = β iken eğri 1/2'ye göre simetriktir: "
         "α = β = 1 düzgün dağılımdır; ortak değer 1'den küçükken eğri U biçimini alır. α, β'dan büyükken kütle sağa, "
         "küçükken sola yığılır.",
         WIDE, aria="Beta densities: symmetric cases 1, 2, 5, 0.5 on the left; skewed cases on the right")


# ============================================================
# beta-olasilik: Beta(2, 3), P(X < 1/2) shaded
# ============================================================
def fig_beta_prob():
    f = lambda x: beta_pdf(x, 2, 3)
    p = Plot(62, 40, 450, 210, (0, 1), (0, 2))
    shade(p, f, 0, 0.5)
    curve(p, f, 0, 1, THEORY, 2.2)
    p.vline(0.5, 0, f(0.5), PRACTICE, "4 3", 0.9)
    x_axis(p, ticks([0, 0.25, 0.5, 0.75, 1], 2), it("x"))
    y_axis(p, ticks([0.5, 1, 1.5, 2], 1), it("f") + "(" + it("x") + ")")
    p.label(0.27, 0.45, "P(" + it("X") + " " + LT + " 1/2) = 11/16", 0, 0, TEXT, LABEL, "middle")
    p.label(0.72, f(0.72), it("f") + "(" + it("x") + ") = 12" + it("x") + "(1 " + MINUS + " " + it("x") + ")<tspan font-size=\"10\" dy=\"-5\">2</tspan><tspan dy=\"5\">&#8203;</tspan>",
            10, -4, THEORY, LABEL)
    emit("beta-olasilik", 560, 290, [p],
         "Beta(2, 3) yoğunluğu 1/3 noktasında tepe yapar. "
         "Taralı alan, makinenin günün yarısından azında meşgul olma olasılığıdır.",
         aria="Beta 2 3 density with the area left of one half shaded")


# ============================================================
# weibull-aileleri: Weibull(1, gamma) densities
# ============================================================
def fig_weibull():
    styles = [(BASE, "2 4"), (THEORY, None), (PRACTICE, None), (REMARK, "7 4")]
    gs = [0.5, 1, 2, 3.5]
    p = Plot(62, 40, 450, 220, (0, 3), (0, 1.6))
    for g, (c, d) in zip(gs, styles):
        curve(p, lambda y, g=g: weibull_pdf(y, 1.0, g), 0.0005, 3, c, 2.1, d, n=800)
    x_axis(p, ticks([0, 0.5, 1, 1.5, 2, 2.5, 3]), it("y"))
    y_axis(p, ticks([0.5, 1, 1.5]), it("f") + "(" + it("y") + ")")
    legend(p, p.X(1.85), p.Y(1.52),
           [(c, d, GAMMA_SMALL + " = " + num(g)) for g, (c, d) in zip(gs, styles)])
    emit("weibull-aileleri", 560, 300, [p],
         "α = 1 için Weibull yoğunlukları. γ = 1 üstel dağılımdır; γ 1'den küçükken yoğunluk sıfırda sınırsızdır, "
         "γ 1'den büyükken sıfırdan başlayıp bir tepe yapar ve γ büyüdükçe tepe 1 civarında sivrilir.",
         aria="Weibull densities with alpha 1 and gamma 0.5, 1, 2, 3.5")


# ============================================================
# cauchy-normal: Cauchy vs normal tails
# ============================================================
def fig_cauchy():
    p = Plot(62, 40, 470, 220, (-6, 6), (0, 0.45))
    curve(p, lambda x: normal_pdf(x, 0, 1), -6, 6, BASE, 2.0, "7 4")
    curve(p, lambda x: cauchy_pdf(x, 1, 0), -6, 6, THEORY, 2.2)
    curve(p, lambda x: cauchy_pdf(x, 2, 0), -6, 6, PRACTICE, 2.2)
    x_axis(p, ticks(range(-6, 7, 2)), it("x"))
    y_axis(p, ticks([0.1, 0.2, 0.3, 0.4], 1), it("f") + "(" + it("x") + ")", x=-6)
    legend(p, p.X(2.2), p.Y(0.43), [(BASE, "7 4", "N(0, 1)"),
                                     (THEORY, None, "Cauchy(1, 0)"),
                                     (PRACTICE, None, "Cauchy(2, 0)")])
    emit("cauchy-normal", 560, 300, [p],
         "Cauchy yoğunlukları çan biçimlidir ama kuyrukları normal yoğunluğunkinden çok daha kalındır: "
         "x büyürken normal yoğunluk üstel hızla, Cauchy yoğunluğu ise yalnızca 1/x² gibi söner. "
         "Momentlerin var olmaması bu kalın kuyruklardan gelir.",
         aria="Standard normal density against Cauchy densities with scale 1 and 2")


# ============================================================
# log-normal-aileleri: LogNormal(0, sigma^2) densities
# ============================================================
def fig_lognormal():
    styles = [(THEORY, None), (PRACTICE, None), (REMARK, "7 4")]
    ss = [0.25, 0.5, 1]
    p = Plot(62, 40, 450, 220, (0, 4), (0, 1.8))
    for s, (c, d) in zip(ss, styles):
        curve(p, lambda x, s=s: lognormal_pdf(x, 0, s), 0.001, 4, c, 2.1, d, n=800)
    x_axis(p, ticks([0, 1, 2, 3, 4]), it("x"))
    y_axis(p, ticks([0.5, 1, 1.5]), it("f") + "(" + it("x") + ")")
    legend(p, p.X(2.3), p.Y(1.7),
           [(c, d, MU + " = 0, " + SIGMA + " = " + num(s)) for s, (c, d) in zip(ss, styles)])
    emit("log-normal-aileleri", 560, 300, [p],
         "μ = 0 için log-normal yoğunluklar. Hepsi pozitif eksende yaşar ve sağa çarpıktır; "
         "σ büyüdükçe tepe sola kayar, sağ kuyruk uzar.",
         aria="Log-normal densities with mu 0 and sigma 0.25, 0.5, 1")


def main():
    fig_uniform()
    fig_gamma_function()
    fig_gamma_families()
    fig_exponential_tail()
    fig_gamma_repair()
    fig_beta_families()
    fig_beta_prob()
    fig_weibull()
    fig_cauchy()
    fig_lognormal()
    for name, md in OUT.items():
        path = OUT_DIR / f"{PREFIX}{name}.md"
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(md)
        print("wrote", path.name)


if __name__ == "__main__":
    main()
