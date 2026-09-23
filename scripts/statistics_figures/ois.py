# -*- coding: utf-8 -*-
"""
Figures of the chapter "Örneklem ve İstatistikler"
(dersler/matematiksel-istatistik/orneklem-ve-istatistikler.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box: a figure that illustrates a
definition sits directly below that box. The figures are NOT produced at
build time. Run

    python scripts/statistics_figures/ois.py
    python scripts/center_figures.py "statistics-ois-*.md" --keep-width
    python scripts/check_figure_labels.py "scripts/_figures/statistics-ois-*.md"

and paste the markup of scripts/_figures/statistics-ois-<name>.md into the
.qmd. Captions are Turkish on purpose (they are shown on the site); aria
labels are plain ASCII.
"""
import io
import itertools
import math
import sys
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, WIDE, TEXT, THEORY, PRACTICE, BASE, REMARK  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "statistics-ois-"
OUT = {}

MINUS, MU, SIGMA = "&#8722;", "&#956;", "&#963;"
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


def sub(s):
    return f'<tspan font-size="9" dy="3">{s}</tspan><tspan dy="-3">&#8203;</tspan>'


XBAR = it("X&#772;")


def pdf(x, mu, s):
    return math.exp(-0.5 * ((x - mu) / s) ** 2) / (s * math.sqrt(2 * math.pi))


def curve(mu, s, a, b, n=SAMPLES):
    return [(a + (b - a) * k / n, pdf(a + (b - a) * k / n, mu, s)) for k in range(n + 1)]


def shade(p, mu, s, a, b, color=PRACTICE, opacity=0.32):
    pts = [(a, 0)] + curve(mu, s, a, b, 200) + [(b, 0)]
    p.polygon(pts, color, opacity)


def x_axis(p, ticks, name=""):
    """Horizontal axis with an arrow head, ticks given as (value, label) pairs."""
    Y = p.Y(p.ymin)
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


def y_axis(p, ticks, name="", digits=None):
    X = p.X(p.xmin)
    top, bottom = p.y0 - 10, p.Y(p.ymin)
    p.add(f'<g stroke="{TEXT}" stroke-width="1.1" opacity="0.5" fill="{TEXT}">'
          f'<line x1="{X:.1f}" y1="{bottom:.1f}" x2="{X:.1f}" y2="{top:.1f}"/>'
          f'<polygon points="{X:.1f},{top:.1f} {X-3.5:.1f},{top+8:.1f} {X+3.5:.1f},{top+8:.1f}" stroke="none"/></g>')
    for v in ticks:
        Y = p.Y(v)
        p.add(f'<line x1="{X-3:.1f}" y1="{Y:.1f}" x2="{X+3:.1f}" y2="{Y:.1f}" stroke="{TEXT}" stroke-width="1" opacity="0.7"/>')
        p.add(f'<text x="{X-7:.1f}" y="{Y+4:.1f}" fill="{TEXT}" font-size="{TICK}" text-anchor="end" opacity="0.8">{num(v, digits)}</text>')
    if name:
        p.add(f'<text x="{X+8:.1f}" y="{top+6:.1f}" fill="{TEXT}" font-size="12" opacity="0.85">{name}</text>')


def bar(p, x, y, color, width, opacity=0.85):
    X, Y0, Y1 = p.X(x), p.Y(0), p.Y(y)
    p.add(f'<rect x="{X - width / 2:.1f}" y="{Y1:.1f}" width="{width}" height="{max(Y0 - Y1, 0.8):.1f}" '
          f'fill="{color}" opacity="{opacity}" rx="1.5"/>')


def swatch(p, px, py, color, text, opacity=0.85, size=12.5):
    p.add(f'<rect x="{px:.1f}" y="{py - 9:.1f}" width="11" height="11" fill="{color}" opacity="{opacity}" rx="1.5"/>')
    p.text_px(px + 17, py + 1, text, size=size)


def line_key(p, px, py, color, text, dash=None, size=12.5):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    p.add(f'<line x1="{px:.1f}" y1="{py - 4:.1f}" x2="{px + 20:.1f}" y2="{py - 4:.1f}" stroke="{color}" stroke-width="2"{d}/>')
    p.text_px(px + 26, py + 1, text, size=size)


# ------------------------------------------------------------
# the finite population of the worked examples
# ------------------------------------------------------------
POP = (2, 4, 10, 12, 18)
MEAN_DIST, MEDIAN_DIST = {}, {}
for c in itertools.combinations(POP, 3):
    m = Fraction(sum(c), 3)
    MEAN_DIST[m] = MEAN_DIST.get(m, 0) + Fraction(1, 10)
    md = sorted(c)[1]
    MEDIAN_DIST[md] = MEDIAN_DIST.get(md, 0) + Fraction(1, 10)
MU_POP = Fraction(sum(POP), len(POP))                       # 46/5
E_MEDIAN = sum(k * v for k, v in MEDIAN_DIST.items())       # 44/5


def population_panel(p, dist, color, width, name="x"):
    for x, pr in dist.items():
        bar(p, float(x), float(pr), color, width)
    x_axis(p, [(v, num(v)) for v in range(2, 19, 2)], it(name))
    y_axis(p, (0.1, 0.2, 0.3, 0.4), "", 1)
    # population values as hollow dots just above the axis
    for v in POP:
        p.add(f'<circle cx="{p.X(v):.1f}" cy="{p.Y(0) - 0.1:.1f}" r="4" fill="none" stroke="{BASE}" stroke-width="1.8"/>')


# ============================================================
# xbar-dagilimi: sampling distribution of the mean, n = 3 without replacement
# ============================================================
def fig_mean_distribution():
    W, H = 560, 280
    p = Plot(50, 50, 460, 180, (1, 19), (0, 0.45))
    population_panel(p, MEAN_DIST, THEORY, 11)
    mu = float(MU_POP)
    p.vline(mu, 0, 0.36, PRACTICE, "5 4", 0.9)
    p.label(mu, 0.36, f"{MU} = 9,2", 0, -6, PRACTICE, LABEL, "middle", bold=True)
    p.text_px(p.x0 + 8, p.y0 - 24, f"P({XBAR} = {it('x')})", TEXT, 12)
    swatch(p, 330, p.y0 - 22, THEORY, f"{XBAR} olasılıkları")
    p.add(f'<circle cx="{335.5:.1f}" cy="{p.y0 - 3.5:.1f}" r="4" fill="none" stroke="{BASE}" stroke-width="1.8"/>')
    p.text_px(347, p.y0 + 1, "kitle değerleri", size=12.5)
    OUT["xbar-dagilimi"] = figure(
        W, H, [p],
        "Kitle değerleri 2, 4, 10, 12 ve 18 (halkalar) 2 ile 18 arasına yayılmışken, iadesiz "
        "çekilen 3 birimlik örneklemlerin ortalamaları (çubuklar) 16/3 ile 40/3 arasında kalır ve "
        "kitle ortalaması μ = 9,2 çevresinde toplanır.",
        aria="Bar chart of the sampling distribution of the mean of 3 draws without replacement "
             "from 2, 4, 10, 12, 18, with the population values and the mean 9.2 marked")


# ============================================================
# medyan-dagilimi: sampling distribution of the median
# ============================================================
def fig_median_distribution():
    W, H = 560, 280
    p = Plot(50, 50, 460, 180, (1, 19), (0, 0.45))
    population_panel(p, MEDIAN_DIST, REMARK, 16, "y")
    for x, pr in MEDIAN_DIST.items():
        p.label(x, float(pr), f"{pr.numerator * (10 // pr.denominator)}/10", 0, -6, REMARK, 12, "middle", bold=True)
    em, mu = float(E_MEDIAN), float(MU_POP)
    p.vline(em, 0, 0.22, THEORY, "5 4", 0.9)
    p.vline(mu, 0, 0.30, PRACTICE, "5 4", 0.9)
    p.label(em, 0.22, f"{it('E')}({it('Y')}) = 8,8", -8, 4, THEORY, 12.5, "end", bold=True)
    p.label(em, 0.30, f"{MU} = 9,2", -8, 4, PRACTICE, 12.5, "end", bold=True)
    p.add(f'<line x1="{p.X(em) - 6:.1f}" y1="{p.Y(0.30):.1f}" x2="{p.X(mu):.1f}" y2="{p.Y(0.30):.1f}" '
          f'stroke="{PRACTICE}" stroke-width="1" opacity="0.8"/>')
    p.text_px(p.x0 + 8, p.y0 - 24, f"P({it('Y')} = {it('y')})", TEXT, 12)
    swatch(p, 330, p.y0 - 22, REMARK, f"medyan {it('Y')} olasılıkları")
    p.add(f'<circle cx="{335.5:.1f}" cy="{p.y0 - 3.5:.1f}" r="4" fill="none" stroke="{BASE}" stroke-width="1.8"/>')
    p.text_px(347, p.y0 + 1, "kitle değerleri", size=12.5)
    OUT["medyan-dagilimi"] = figure(
        W, H, [p],
        "Aynı örneklemlerin medyanı Y yalnız 4, 10 ve 12 değerlerini alır. Beklenen değeri "
        "E(Y) = 8,8, kitle ortalaması 9,2'den farklıdır; olasılıklar da örneklem ortalamasınınkinden "
        "daha geniş bir aralığa yayılmıştır.",
        aria="Bar chart of the sampling distribution of the median of 3 draws without replacement "
             "from 2, 4, 10, 12, 18: values 4, 10, 12 with probabilities 3/10, 4/10, 3/10")


# ============================================================
# duzeltme-carpani: sqrt((N - n)/(N - 1)) for N = 100
# ============================================================
def fig_correction_factor():
    W, H = 560, 270
    N = 100
    p = Plot(50, 40, 460, 180, (0, 100), (0, 1.08))
    p.polygon([(0, 0), (5, 0), (5, 1.08), (0, 1.08)], BASE, 0.14)
    pts = [(1 + 99 * k / SAMPLES, math.sqrt((N - 1 - 99 * k / SAMPLES) / (N - 1))) for k in range(SAMPLES + 1)]
    p.line(pts, THEORY, 2.2)
    x_axis(p, [(v, num(v)) for v in (0, 5, 20, 40, 60, 80, 100)], it("n"))
    y_axis(p, (0.2, 0.4, 0.6, 0.8, 1.0), "", 1)
    v5 = math.sqrt(95 / 99)
    p.add(f'<circle cx="{p.X(5):.1f}" cy="{p.Y(v5):.1f}" r="4" fill="{PRACTICE}"/>')
    p.label(5, v5, "n = 5 için 0,98", 10, 26, PRACTICE, 12.5, "start", bold=True)
    v50 = math.sqrt(50 / 99)
    p.add(f'<circle cx="{p.X(50):.1f}" cy="{p.Y(v50):.1f}" r="4" fill="{PRACTICE}"/>')
    p.label(50, v50, "n = 50 için 0,71", 8, -12, PRACTICE, 12.5, "start", bold=True)
    p.label(8, 0.32, "n &lt; 0,05N", 0, 0, BASE, 12.5, "start", bold=True)
    p.text_px(p.x0 + 12, p.y0 - 18, f"&#8730;((N {MINUS} n)/(N {MINUS} 1)),  N = 100", THEORY, 12.5, "start", bold=True)
    OUT["duzeltme-carpani"] = figure(
        W, H, [p],
        "N = 100 birimlik bir kitlede standart hatayı düzelten √((N − n)/(N − 1)) çarpanı. Örneklem "
        "kitlenin %5'inden küçükken (taralı şerit) çarpan 1'e çok yakındır; n büyüdükçe küçülür ve "
        "n = N olduğunda sıfır olur.",
        aria="Graph of the square root of the finite population correction factor for N 100 as a "
             "function of n, close to 1 for n below 5 and zero at n 100")


# ============================================================
# normal-xbar: density of the mean of a normal sample, n = 1, 4, 16
# ============================================================
def fig_normal_mean():
    W, H = 560, 290
    p = Plot(40, 40, 480, 200, (-3.4, 3.4), (0, 1.7))
    styles = ((1, BASE, "n = 1"), (4, PRACTICE, "n = 4"), (16, THEORY, "n = 16"))
    for n, c, lab in styles:
        s = 1 / math.sqrt(n)
        pts = curve(0, s, -3.4, 3.4)
        p.polygon([(-3.4, 0)] + pts + [(3.4, 0)], c, 0.10)
        p.line(pts, c, 2.1)
    p.label(0, pdf(0, 0, 1 / 4), "n = 16", 10, 4, THEORY, LABEL, "start", bold=True)
    p.label(0.45, pdf(0.45, 0, 1 / 2), "n = 4", 8, -4, PRACTICE, LABEL, "start", bold=True)
    p.label(1.25, pdf(1.25, 0, 1), "n = 1", 6, -6, BASE, LABEL, "start", bold=True)
    labels = {-3: f"{MU}{MINUS}3{SIGMA}", -2: f"{MU}{MINUS}2{SIGMA}", -1: f"{MU}{MINUS}{SIGMA}", 0: MU,
              1: f"{MU}+{SIGMA}", 2: f"{MU}+2{SIGMA}", 3: f"{MU}+3{SIGMA}"}
    x_axis(p, [(k, labels[k]) for k in range(-3, 4)], "")
    OUT["normal-xbar"] = figure(
        W, H, [p],
        "N(μ, σ²) kitlesinden alınan örneklemin ortalaması N(μ, σ²/n) dağılımlıdır. n = 1, 4 ve 16 "
        "için standart sapma σ, σ/2 ve σ/4 olur: eğri μ'de kalır ama n büyüdükçe daralır ve yükselir.",
        aria="Three normal densities centred at mu with standard deviations sigma, sigma over 2 and "
             "sigma over 4 for sample sizes 1, 4 and 16")


# ============================================================
# normal-ornek: P(48 <= X <= 53) vs P(48 <= Xbar <= 53), N(50, 36), n = 9
# ============================================================
def fig_normal_example():
    W, H = 700, 280
    left = Plot(30, 50, 290, 170, (32, 68), (0, 0.21))
    right = Plot(390, 50, 290, 170, (32, 68), (0, 0.21))
    for p, s, area, title, at in ((left, 6, "0,3208", f"Tek gözlem: {it('X')} ~ {it('N')}(50, 36)", (50.5, 0.022)),
                                  (right, 2, "0,7745", f"{XBAR} ~ {it('N')}(50, 4), n = 9", (61, 0.12))):
        shade(p, 50, s, 48, 53)
        p.line(curve(50, s, 32, 68), THEORY, 2.0)
        for x in (48, 53):
            p.vline(x, 0, pdf(x, 50, s), PRACTICE, "4 3", 0.8)
        x_axis(p, [(v, num(v)) for v in (35, 40, 45, 50, 55, 60, 65)], it("x"))
        p.text(at[0], at[1], area, PRACTICE, LABEL, "middle", bold=True)
        if s == 2:
            p.add(f'<line x1="{p.X(58.5):.1f}" y1="{p.Y(0.115):.1f}" x2="{p.X(51.5):.1f}" y2="{p.Y(0.06):.1f}" '
                  f'stroke="{PRACTICE}" stroke-width="1" opacity="0.8"/>')
        p.text_px(p.x0 + p.w / 2, p.y0 - 24, title, TEXT, 12.5, "middle", bold=True)
    OUT["normal-ornek"] = figure(
        W, H, [left, right],
        "Aynı aralık, iki farklı dağılım: 48 ile 53 arasına tek bir gözlemin düşme olasılığı yaklaşık "
        "0,3208 iken, 9 gözlemin ortalamasının düşme olasılığı 0,7745'tir. Ortalamanın dağılımı μ = 50 "
        "çevresinde üç kat daha dardır (standart sapma 6 yerine 2).",
        css_class=WIDE,
        aria="Two normal densities with mean 50 and standard deviations 6 and 2; the area between 48 "
             "and 53 is 0.3208 on the left and 0.7745 on the right")


# ============================================================
# orneklem-buyuklugu: P(|Xbar - mu| < 0.5 sigma): Chebyshev bound vs normal
# ============================================================
def fig_sample_size():
    W, H = 560, 290
    p = Plot(50, 50, 460, 190, (0, 100), (0, 1.05))
    cheb = [(4 + 96 * k / SAMPLES, 1 - 4 / (4 + 96 * k / SAMPLES)) for k in range(SAMPLES + 1)]
    exact = [(1 + 99 * k / SAMPLES, math.erf(0.5 * math.sqrt(1 + 99 * k / SAMPLES) / math.sqrt(2)))
             for k in range(SAMPLES + 1)]
    p.add(f'<line x1="{p.X(0):.1f}" y1="{p.Y(0.95):.1f}" x2="{p.X(100):.1f}" y2="{p.Y(0.95):.1f}" '
          f'stroke="{BASE}" stroke-width="1.3" stroke-dasharray="5 4"/>')
    p.label(100, 0.95, "0,95", 0, 16, BASE, 12, "end", bold=True)
    p.line(exact, THEORY, 2.2)
    p.line(cheb, PRACTICE, 2.2)
    e16 = math.erf(0.5 * 4 / math.sqrt(2))
    p.add(f'<circle cx="{p.X(16):.1f}" cy="{p.Y(e16):.1f}" r="4.2" fill="{THEORY}"/>')
    p.vline(16, 0, e16, THEORY, "3 3", 0.7)
    p.add(f'<circle cx="{p.X(80):.1f}" cy="{p.Y(0.95):.1f}" r="4.2" fill="{PRACTICE}"/>')
    p.vline(80, 0, 0.95, PRACTICE, "3 3", 0.7)
    x_axis(p, [(v, num(v)) for v in (0, 16, 40, 60, 80, 100)], it("n"))
    y_axis(p, (0.2, 0.4, 0.6, 0.8, 1.0), "", 1)
    line_key(p, p.X(42), p.Y(0.42), THEORY, "normal kitlede gerçek olasılık")
    line_key(p, p.X(42), p.Y(0.30), PRACTICE, "Chebyshev alt sınırı 1 &#8722; 4/n")
    p.text_px(p.x0 + 8, p.y0 - 24, f"P(|{XBAR} {MINUS} {MU}| &lt; 0,5{SIGMA})", TEXT, 12)
    OUT["orneklem-buyuklugu"] = figure(
        W, H, [p],
        "Örneklem ortalamasının μ'ye 0,5σ'dan daha yakın olma olasılığı. Chebyshev alt sınırı "
        "(turuncu) her dağılım için geçerlidir ve 0,95'e ancak n = 80'de ulaşır; kitle normalse "
        "gerçek olasılık (mavi) 0,95'i n = 16'da geçer.",
        aria="Chebyshev lower bound 1 - 4/n and the normal probability for the mean to be within half a "
             "sigma of mu as functions of n, with the level 0.95 reached at n 80 and n 16")


fig_mean_distribution()
fig_median_distribution()
fig_correction_factor()
fig_normal_mean()
fig_normal_example()
fig_sample_size()

for name, content in OUT.items():
    with io.open(OUT_DIR / f"{PREFIX}{name}.md", "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
print(f"generated {len(OUT)} figures:", ", ".join(OUT))
