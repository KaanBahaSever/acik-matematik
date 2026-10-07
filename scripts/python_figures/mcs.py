# -*- coding: utf-8 -*-
"""
Figures of the chapter "Rastgele Sayılar ve Monte Carlo Yöntemleri"
(dersler/python-bilimsel/rastgele-sayilar-ve-monte-carlo.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box and never directly under a heading;
concept figures stay visible (not inside a collapsed .cozum block).
The figures are NOT produced at build time. Run

    python scripts/python_figures/mcs.py
    python scripts/center_figures.py "python-mcs-*.md"
    python scripts/check_figure_labels.py "scripts/_figures/python-mcs-*.md"

and paste the markup of scripts/_figures/python-mcs-<name>.md into the .qmd.
Every figure is drawn from the same data the chapter's code computes: the
random samples come from np.random.default_rng with the same seed and the
same sequence of calls as the code block the caption names. Captions are
Turkish on purpose; aria labels are plain ASCII.
"""
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import (Plot, figure, WIDE, TEXT, THEORY, PRACTICE,  # noqa: E402
                      BASE, REMARK)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "python-mcs-"

MINUS = "&#8722;"
PI_S = "&#960;"
MU = "&#956;"
SQRT = "&#8730;"


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


def dec(v, digits=2):
    """Decimal comma and a true minus sign: -0.5 -> '−0,50'."""
    s = f"{v:.{digits}f}"
    return s.replace(".", ",").replace("-", MINUS)


def num(v):
    """Tick label with a decimal comma: 0.5 -> '0,5', 2.0 -> '2'."""
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    if s in ("-0", ""):
        s = "0"
    return s.replace(".", ",").replace("-", MINUS)


def txt(p, x, y, s, color=TEXT, size=12, anchor="middle", bold=False,
        opacity=1.0):
    weight = ' font-weight="600"' if bold else ""
    op = f' opacity="{opacity}"' if opacity != 1.0 else ""
    p.add(f'<text x="{x:.1f}" y="{y:.1f}" fill="{color}" font-size="{size}" '
          f'text-anchor="{anchor}"{weight}{op}>{s}</text>')


def bar(p, x0, x1, y, color, fop=0.28, sop=0.75):
    """Histogram bar on [x0, x1] from 0 up to y (data coordinates)."""
    X0, X1, Y0, Y1 = p.X(x0), p.X(x1), p.Y(0), p.Y(y)
    p.add(f'<rect x="{X0:.1f}" y="{Y1:.1f}" width="{X1 - X0:.1f}" '
          f'height="{Y0 - Y1:.1f}" fill="{color}" fill-opacity="{fop}" '
          f'stroke="{color}" stroke-width="0.8" stroke-opacity="{sop}"/>')


def hline(p, x0, x1, y, color=TEXT, dash="5 4", width=1.3, opacity=0.8):
    p.add(f'<line x1="{p.X(x0):.1f}" y1="{p.Y(y):.1f}" x2="{p.X(x1):.1f}" '
          f'y2="{p.Y(y):.1f}" stroke="{color}" stroke-width="{width}" '
          f'stroke-dasharray="{dash}" opacity="{opacity}"/>')


def seg(p, a, b, color=TEXT, width=1.0, dash=None, opacity=1.0):
    da = f' stroke-dasharray="{dash}"' if dash else ""
    p.add(f'<line x1="{p.X(a[0]):.1f}" y1="{p.Y(a[1]):.1f}" '
          f'x2="{p.X(b[0]):.1f}" y2="{p.Y(b[1]):.1f}" stroke="{color}" '
          f'stroke-width="{width}"{da} opacity="{opacity}" '
          f'stroke-linecap="round"/>')


def legend_line(p, x, y, color, label, dash=None, dot=False, width=2.0):
    """A short line sample at pixel (x, y) followed by its label."""
    da = f' stroke-dasharray="{dash}"' if dash else ""
    p.add(f'<line x1="{x:.1f}" y1="{y - 4:.1f}" x2="{x + 22:.1f}" '
          f'y2="{y - 4:.1f}" stroke="{color}" stroke-width="{width}"{da}/>')
    if dot:
        p.add(f'<circle cx="{x + 11:.1f}" cy="{y - 4:.1f}" r="3.2" '
              f'fill="{color}"/>')
    txt(p, x + 28, y, label, TEXT, 11.5, "start")


def f_gauss(x):
    return np.exp(-x**2)


EXACT_GAUSS = math.sqrt(math.pi) / 2 * math.erf(1)

# ============================================================
# ters-donusum: inverse transform for Exp(2), code b08 (seed 11)
# ============================================================
lam = 2.0
n = 100_000
rng = np.random.default_rng(11)
u = rng.random(n)
x = -np.log(1 - u) / lam
counts, edges = np.histogram(x, bins=30, range=(0, 3))
dens = counts / (n * np.diff(edges))

pl = Plot(58, 40, 270, 220, (0, 2.5), (0, 1))
pl.axes([0, 0.5, 1, 1.5, 2, 2.5], [0, 0.5, 1], it("x"), it("u"), num, num)
xs = np.linspace(0, 2.5, 160)
pl.line(list(zip(xs, 1 - np.exp(-lam * xs))), THEORY, 2.2)
for uk in u[:6]:
    xk = -math.log(1 - uk) / lam
    seg(pl, (0, uk), (xk, uk), PRACTICE, 1.1, "4 3", 0.85)
    pl.arrow((xk, uk), (xk, 0.012), PRACTICE, 1.3, 6.5)
    pl.points([(0, uk)], PRACTICE, 3.0)
pl.label(1.55, 1 - math.exp(-3.1), it("F") + "(" + it("x") + ") = 1 "
         + MINUS + " " + it("e") + sup(MINUS + "2" + it("x")), 0, 22,
         THEORY, 12.5, "start", True)
txt(pl, pl.x0 + pl.w / 2, 20, "u " + "&#8594;" + " x = F" + sup(MINUS + "1")
    + "(u)", TEXT, 12.5, bold=True)

pr = Plot(420, 40, 270, 220, (0, 3), (0, 2.1))
pr.axes([0, 1, 2, 3], [0, 1, 2], it("x"), "", num, num)
for j in range(30):
    bar(pr, edges[j], edges[j + 1], dens[j], THEORY, 0.25, 0.6)
xs = np.linspace(0, 3, 200)
pr.line(list(zip(xs, lam * np.exp(-lam * xs))), PRACTICE, 2.2)
pr.label(0.62, lam * math.exp(-lam * 0.62), "2" + it("e") + sup(MINUS + "2"
         + it("x")), 10, -4, PRACTICE, 12.5, "start", True)
txt(pr, pr.x0 + pr.w / 2, 20, "100 000 örneğin histogramı", TEXT, 12.5,
    bold=True)

save("ters-donusum", figure(
    720, 300, [pl, pr],
    "Ters dönüşüm örneğindeki kodun verisi. Solda yöntemin kendisi: "
    "<code>default_rng(11)</code> üretecinin ilk altı <em>u</em> sayısı "
    "dikey eksenden <em>F</em>(<em>x</em>) = 1 &#8722; <em>e</em><sup>&#8722;2"
    "<em>x</em></sup> eğrisine, oradan yatay eksendeki "
    "<em>x</em> = &#8722;ln(1 &#8722; <em>u</em>)/2 noktasına taşınır. Eğri "
    "sıfırın yakınında dik olduğundan <em>u</em> ekseninin geniş bir "
    "parçası küçük <em>x</em>'lerin dar bir aralığına taşınır; <em>x</em>'ler "
    "bu yüzden sıfırın yakınında sıklaşır. Sağda 100 000 değerin 30 kutulu "
    "yoğunluk "
    "histogramı ve Üstel(2) yoğunluğu 2<em>e</em><sup>&#8722;2<em>x</em>"
    "</sup>.",
    WIDE,
    aria="Left: the distribution function F(x) = 1 - exp(-2x) with six "
         "uniform numbers u on the vertical axis carried to the curve and "
         "down to x = F^-1(u). Right: density histogram of 100000 inverse "
         "transform samples on [0, 3] with 30 bins and the exponential "
         "density 2 exp(-2x) on top."))

# ============================================================
# buyuk-sayilar: running means of dice (b10, seed 5) and Cauchy (b11, seed 6)
# ============================================================
n = 10_000
k = np.arange(1, n + 1)
rng = np.random.default_rng(5)
rolls = rng.integers(1, 7, size=(5, n))
dice = rolls.cumsum(axis=1) / k
rng = np.random.default_rng(6)
cauchy = rng.standard_cauchy(size=(5, n)).cumsum(axis=1) / k
idx = np.unique(np.round(np.logspace(0, 4, 400)).astype(int)) - 1
lk = np.log10(k[idx])
COLORS = [THEORY, PRACTICE, BASE, REMARK, TEXT]


def log_ticks(p, y):
    for e in range(5):
        s = "1" if e == 0 else ("10" if e == 1 else "10" + sup(str(e)))
        p.label(e, y, s, 0, 17, TEXT, 11, "middle")


pl = Plot(50, 40, 280, 210, (0, 4), (1, 6))
pl.grid(range(5), range(1, 7))
pl.axes([], [1, 2, 3, 4, 5, 6], it("n"), "", num, num)
log_ticks(pl, 1)
for row, color in zip(dice, COLORS):
    pl.line(list(zip(lk, row[idx])), color, 1.4,
            opacity=0.6 if color == TEXT else 0.9)
hline(pl, 0, 4, 3.5, TEXT, "6 4", 1.4, 0.9)
pl.label(4, 3.5, MU + " = 3,5", -2, -8, TEXT, 12, "end", True)
txt(pl, pl.x0 + pl.w / 2, 20, "zar: ortalama 3,5'e yaklaşır", TEXT, 12.5,
    bold=True)

pr = Plot(420, 40, 280, 210, (0, 4), (-50, 30))
pr.grid(range(5), [-40, -20, 0, 20])
pr.axes([], [-40, -20, 0, 20], it("n"), "", num, num)
log_ticks(pr, -50)
for row, color in zip(cauchy, COLORS):
    pr.line(list(zip(lk, row[idx])), color, 1.4,
            opacity=0.6 if color == TEXT else 0.9)
txt(pr, pr.x0 + pr.w / 2, 20, "Cauchy: ortalama yerleşmez", TEXT, 12.5,
    bold=True)

save("buyuk-sayilar", figure(
    720, 290, [pl, pr],
    "Koşu ortalamaları, yatay eksen logaritmik. Solda büyük sayılar yasası "
    "örneğindeki beş zar deneyi: <em>X&#772;</em><sub><em>n</em></sub> her "
    "yolda 3,5'e yerleşir. Sağda uyarı kutusundaki Cauchy kodunun beş yolu: "
    "arada bir gelen çok büyük bir değer ortalamayı sıçratır (bir yolda "
    "&#8722;46'ya kadar) ve yollar hiçbir sayıya yerleşmez; Cauchy "
    "dağılımının beklenen değeri yoktur.",
    WIDE,
    aria="Two panels of five running-mean paths against n on a log axis "
         "from 1 to 10^4. Left: dice averages settle at 3.5. Right: Cauchy "
         "averages jump to values between -46 and 27 and do not settle."))

# ============================================================
# merkezi-limit: standardised means of Exp(1) samples, code b12 (seed 8)
# ============================================================
rng = np.random.default_rng(8)
reps = 100_000
t = np.linspace(-4, 4, 201)
phi = np.exp(-t**2 / 2) / np.sqrt(2 * np.pi)
panels = []
for j, nn in enumerate([1, 4, 32]):
    xx = rng.exponential(1.0, size=(reps, nn))
    z = (xx.mean(axis=1) - 1.0) * np.sqrt(nn)
    hd, he = np.histogram(z, bins=40, range=(-4, 4), density=True)
    p = Plot(36 + j * 226, 40, 190, 190, (-4, 4), (0, 1.0))
    p.axes([-4, -2, 0, 2, 4], [0, 0.5, 1] if j == 0 else [], it("z"), "",
           num, num)
    for a, b, h in zip(he[:-1], he[1:], hd):
        if h > 0:
            bar(p, a, b, h, THEORY, 0.25, 0.6)
    p.line(list(zip(t, phi)), PRACTICE, 2.0)
    txt(p, p.x0 + p.w / 2, 22, it("n") + f" = {nn}", TEXT, 13, bold=True)
    panels.append(p)
panels[0].label(1.2, 0.33, it("&#966;") + "(" + it("z") + ")", 0, 0,
                PRACTICE, 12.5, "start", True)

save("merkezi-limit", figure(
    720, 270, panels,
    "Merkezi limit teoremi kodunun çizdiği üç histogram: Üstel(1) "
    "dağılımından alınan <em>n</em> elemanlı örneklemlerin standartlaştırılmış "
    "ortalaması <em>Z</em> = &#8730;<em>n</em> (<em>X&#772;</em><sub><em>n"
    "</em></sub> &#8722; 1), her <em>n</em> için 100 000 tekrar. "
    "<em>n</em> = 1'de histogram üstel yoğunluğun kaydırılmışıdır ve çok "
    "çarpıktır; <em>n</em> = 4'te çarpıklık azalır; <em>n</em> = 32'de "
    "histogram standart normal yoğunluk <em>&#966;</em>(<em>z</em>) "
    "eğrisine neredeyse oturur.",
    WIDE,
    aria="Three density histograms of standardised means of exponential "
         "samples for n = 1, 4 and 32 with the standard normal density on "
         "top; the skewed shape for n = 1 approaches the bell curve as n "
         "grows."))

# ============================================================
# ortalama-deger: Monte Carlo integral of exp(-x^2), code b14 (seed 14)
# ============================================================
rng = np.random.default_rng(14)
N = 10_000
u = rng.random(N)
y = f_gauss(u)
I_hat = float(y.mean())
p = Plot(56, 30, 420, 230, (0, 1), (0, 1.1))
p.axes([0, 0.5, 1], [0, 0.5, 1], it("x"), it("y"), num, num)
xs = np.linspace(0, 1, 120)
p.polygon([(0, 0)] + list(zip(xs, f_gauss(xs))) + [(1, 0)], THEORY, 0.13)
p.polygon([(0, 0), (0, I_hat), (1, I_hat), (1, 0)], PRACTICE, 0.0,
          PRACTICE, 1.6, "6 4")
p.line(list(zip(xs, f_gauss(xs))), THEORY, 2.3)
for uk, yk in zip(u[:30], y[:30]):
    seg(p, (uk, 0), (uk, yk), TEXT, 0.8, None, 0.35)
p.points(list(zip(u[:30], y[:30])), TEXT, 2.8)
p.label(0.03, 1.0, it("y") + " = " + it("e") + sup(MINUS + it("x") + "²", 10),
        10, -16, THEORY, 12.5, "start", True)
p.label(0.98, I_hat, "ortalama yükseklik " + dec(I_hat, 4), 0, -9,
        PRACTICE, 12, "end", True)

save("ortalama-deger", figure(
    520, 300, [p],
    "Monte Carlo integral kodunun verisi. Noktalar, <code>default_rng(14)"
    "</code> ile üretilen ilk 30 <em>u</em> sayısında <em>e</em><sup>&#8722;"
    "<em>u</em>²</sup> değerleridir. Kesikli dikdörtgenin yüksekliği, "
    f"10 000 değerin ortalaması olan {dec(I_hat, 4)} sayısıdır; dikdörtgenin "
    "alanı, eğrinin altında kalan taralı alanın (0,7468) kestirimidir. "
    "Eğrinin dikdörtgenin üstüne taşan parçasıyla dikdörtgenin içinde "
    "eğrinin üstünde kalan boşluğun alanları yaklaşık eşittir.",
    aria="The curve y = exp(-x^2) on [0, 1] with the area under it shaded, "
         "thirty sample points on the curve with thin stems, and a dashed "
         "rectangle of height 0.7477, the mean of 10000 sampled heights."))

# ============================================================
# hata: RMS error of plain Monte Carlo against N, code b17 (seed 17)
# ============================================================
Ef2 = math.sqrt(math.pi / 8) * math.erf(math.sqrt(2))
sigma = math.sqrt(Ef2 - EXACT_GAUSS**2)
rng = np.random.default_rng(17)
reps = 400
NS = [10, 100, 1000, 10_000, 100_000]
rms, trap = [], []
for N in NS:
    est = np.array([f_gauss(rng.random(N)).mean() for _ in range(reps)])
    rms.append(float(np.sqrt(np.mean((est - EXACT_GAUSS) ** 2))))
    xg = np.linspace(0, 1, N)
    trap.append(abs(float(np.trapezoid(f_gauss(xg), xg)) - EXACT_GAUSS))
print("rms", [f"{v:.2e}" for v in rms])
print("trap", [f"{v:.2e}" for v in trap])
lg = math.log10
p = Plot(76, 34, 440, 230, (1, 5), (-12, 0))
p.grid(range(1, 6), range(-12, 1, 2))
p.axes([], [], it("N"), "")
for e in range(1, 6):
    p.label(e, -12, "10" + sup(str(e)), 0, 18, TEXT, 11, "middle")
for e in range(-12, 1, 3):
    s = "1" if e == 0 else "10" + sup(MINUS + str(-e))
    p.label(1, e, s, -8, 4, TEXT, 11, "end")
p.text_px(p.x0 - 4, p.y0 - 14, "hata", TEXT, 11.5, "middle")
mc = [(lg(N), lg(v)) for N, v in zip(NS, rms)]
th = [(1, lg(sigma / math.sqrt(10))), (5, lg(sigma / math.sqrt(1e5)))]
tr = [(lg(N), lg(v)) for N, v in zip(NS, trap)]
p.line(th, THEORY, 1.6, "6 4", 0.9)
p.points(mc, THEORY, 4.2)
p.line(tr, PRACTICE, 2.0)
p.points(tr, PRACTICE, 3.6)
p.label(3, lg(rms[2]), "Monte Carlo: eğim " + MINUS + "1/2", 0, -16,
        THEORY, 12, "middle", True)
p.label(3, lg(trap[2]), "yamuk kuralı: eğim " + MINUS + "2", 12, -2,
        PRACTICE, 12, "start", True)

save("hata", figure(
    560, 330, [p],
    "Hata hızı kodunun tablosu, iki ekseni de logaritmik ölçekte. Mavi: "
    "<em>N</em> noktalı Monte Carlo kestiriminin 400 tekrar üzerinden "
    "karekök ortalama kare hatası (noktalar); kesikli çizgi kuramsal "
    "<em>&#963;</em>/&#8730;<em>N</em> değeridir ve noktalar onun üstüne "
    "oturur. Kırmızı: aynı sayıda nokta kullanan yamuk kuralının hatası. "
    "Bir boyutta yamuk kuralı çok daha hızlıdır; Monte Carlo'da bir "
    "basamak kazanmak için nokta sayısını 100 ile çarpmak gerekir.",
    aria="Log-log plot of error against N from 10 to 10^5. The Monte Carlo "
         "root mean square error falls with slope -1/2 along the dashed "
         "line sigma / sqrt(N); the trapezoid rule error falls with slope "
         "-2 from about 1e-3 to 6e-12."))

# ============================================================
# guven: twenty 95% confidence intervals, code b16 (seed 16)
# ============================================================
rng = np.random.default_rng(16)
Nci, runs = 1000, 20
centers, halves = [], []
for _ in range(runs):
    yy = f_gauss(rng.random(Nci))
    centers.append(float(yy.mean()))
    halves.append(1.96 * float(yy.std(ddof=1)) / math.sqrt(Nci))
p = Plot(40, 40, 440, 240, (0.715, 0.775), (0.5, runs + 0.5))
p.axes([0.72, 0.73, 0.74, 0.75, 0.76, 0.77], [], "", "", num, num)
seg(p, (EXACT_GAUSS, 0.5), (EXACT_GAUSS, runs + 0.5), TEXT, 1.4, "6 4",
    0.85)
p.label(EXACT_GAUSS, runs + 0.5, it("I") + " = 0,7468", 0, -8, TEXT, 12.5,
        "middle", True)
misses = 0
for j, (c, h) in enumerate(zip(centers, halves)):
    row = runs - j
    ok = c - h <= EXACT_GAUSS <= c + h
    color = THEORY if ok else PRACTICE
    misses += not ok
    seg(p, (c - h, row), (c + h, row), color, 2.4 if not ok else 1.8)
    p.points([(c, row)], color, 3.0)
print("misses", misses)

save("guven", figure(
    560, 350, [p],
    "Güven aralığı kodunun ilk döngüsündeki 20 bağımsız tekrar: her satırda "
    "<em>N</em> = 1000 noktalı kestirim (nokta) ve %95 güven aralığı. "
    "Kesikli çizgi gerçek değerdir. 19 aralık onu içerir, biri (kırmızı) "
    "ıskalar. Aralıklar tekrardan tekrara yer değiştirir; uzun vadede "
    "yaklaşık %95'i gerçek değeri yakalar.",
    aria="Twenty horizontal confidence intervals of half width about "
         "0.0125 stacked vertically around the dashed line I = 0.7468; "
         "nineteen cross the line, one red interval near 0.7315 misses "
         "it."))

# ============================================================
# yuruyus: eight random walks of 400 steps, code b20 (seed 20)
# ============================================================
rng = np.random.default_rng(20)
m, n = 5000, 400
steps = rng.choice([-1, 1], size=(m, n))
S = np.zeros((m, n + 1), dtype=int)
S[:, 1:] = steps.cumsum(axis=1)
kk = np.arange(n + 1)
p = Plot(56, 30, 440, 260, (0, n), (-50, 50))
p.grid([100, 200, 300, 400], [-40, -20, 0, 20, 40])
p.axes([0, 100, 200, 300, 400], [-40, -20, 0, 20, 40], it("n"),
       it("S") + "<tspan font-size=\"8.5\" dy=\"3\">n</tspan>", num, num)
for path, color in zip(S[:8], [THEORY, PRACTICE, BASE, REMARK] * 2):
    p.line(list(zip(kk, path)), color, 1.1, opacity=0.85)
env = np.sqrt(kk)
for c in (1, 2):
    for sgn in (1, -1):
        p.line(list(zip(kk, sgn * c * env)), TEXT, 1.4, "6 4", 0.8)
p.label(n, 2 * math.sqrt(n), "2" + SQRT + it("n"), 6, 4, TEXT, 12, "start",
        True)
p.label(n, math.sqrt(n), SQRT + it("n"), 6, 4, TEXT, 12, "start", True)
p.label(n, -math.sqrt(n), MINUS + SQRT + it("n"), 6, 4, TEXT, 12, "start",
        True)
p.label(n, -2 * math.sqrt(n), MINUS + "2" + SQRT + it("n"), 6, 4, TEXT, 12,
        "start", True)

save("yuruyus", figure(
    570, 320, [p],
    "Rastgele yürüyüş kodunun çizdiği ilk sekiz yol, her biri 400 adım. "
    "Kesikli eğriler &#177;&#8730;<em>n</em> ve &#177;2&#8730;<em>n</em>"
    "'dir. Yollar sıfırın etrafında dolaşır ama uzaklaştıkları mesafe "
    "<em>n</em> ile değil &#8730;<em>n</em> ile büyür: 400 adımda tipik "
    "uzaklık 20 civarıdır ve 5000 yolun %96'sı &#177;40 bandında biter.",
    aria="Eight random walk paths of 400 steps starting at 0, between -43 "
         "and 20, with dashed parabolic envelopes plus and minus sqrt(n) "
         "and plus and minus 2 sqrt(n)."))
