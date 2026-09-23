# -*- coding: utf-8 -*-
"""
Figures of the chapter "Normal Dağılım"
(dersler/matematiksel-istatistik/normal-dagilim.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box: a figure that illustrates a
definition sits directly below that box. The figures are NOT produced at
build time. Run

    python scripts/statistics_figures/nor.py
    python scripts/center_figures.py "statistics-nor-*.md" --keep-width
    python scripts/check_figure_labels.py "scripts/_figures/statistics-nor-*.md"

and paste the markup of scripts/_figures/statistics-nor-<name>.md into the
.qmd. Captions are Turkish on purpose (they are shown on the site); aria
labels are plain ASCII.
"""
import io
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, WIDE, TEXT, THEORY, PRACTICE, BASE, REMARK  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "statistics-nor-"
OUT = {}

MINUS, MU, SIGMA, APPROX = "&#8722;", "&#956;", "&#963;", "&#8776;"
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


def pdf(x, mu, s):
    return math.exp(-0.5 * ((x - mu) / s) ** 2) / (s * math.sqrt(2 * math.pi))


def curve(mu, s, a, b, n=SAMPLES):
    return [(a + (b - a) * k / n, pdf(a + (b - a) * k / n, mu, s)) for k in range(n + 1)]


def shade(p, mu, s, a, b, color=PRACTICE, opacity=0.32):
    pts = [(a, 0)] + curve(mu, s, a, b, 200) + [(b, 0)]
    p.polygon(pts, color, opacity)


def x_axis(p, ticks, name="", y=0.0):
    """Horizontal axis with an arrow head, ticks given as (value, label) pairs."""
    Y = p.Y(y)
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
    for v in ticks:
        Y = p.Y(v)
        p.add(f'<line x1="{X-3:.1f}" y1="{Y:.1f}" x2="{X+3:.1f}" y2="{Y:.1f}" stroke="{TEXT}" stroke-width="1" opacity="0.7"/>')
        p.add(f'<text x="{X-7:.1f}" y="{Y+4:.1f}" fill="{TEXT}" font-size="{TICK}" text-anchor="end" opacity="0.8">{num(v)}</text>')
    if name:
        p.add(f'<text x="{X+8:.1f}" y="{top+6:.1f}" fill="{TEXT}" font-size="12" font-style="italic" opacity="0.85">{name}</text>')


def guide(p, x, mu, s, color=PRACTICE):
    p.vline(x, 0, pdf(x, mu, s), color, "4 3", 0.8)


def std_normal_area(name, a, b, area, bounds, caption, aria, area_at, leader=None, xmean=""):
    """Standard normal curve with P(a < Z < b) shaded.

    bounds: (z, z label, x label) for the ends of the shaded interval; the x
    label is the matching value of X, written smaller underneath. Integer
    ticks -3..3 are added where they do not crowd a bound. xmean labels z = 0
    with the mean of X.
    """
    W, H = 560, 250
    p = Plot(40, 26, 480, 180, (-3.6, 3.6), (0, 0.42))
    shade(p, 0, 1, max(a, -3.6), min(b, 3.6))
    p.line(curve(0, 1, -3.6, 3.6), THEORY, 2.0)
    zs = [z for z, _, _ in bounds]
    ints = [k for k in range(-3, 4) if all(abs(k - z) > 0.55 for z in zs)]
    x_axis(p, [(k, "") for k in ints] + [(z, "") for z in zs], it("z"))
    Y = p.Y(0)
    for k in ints:
        p.text_px(p.X(k), Y + 17, num(k), TEXT, TICK, "middle")
    if xmean and 0 in ints:
        p.vline(0, 0, pdf(0, 0, 1), TEXT, "4 3", 0.45)
        p.text_px(p.X(0), Y + 32, xmean, BASE, 11, "middle")
    for z, zlab, xlab in bounds:
        guide(p, z, 0, 1)
        p.text_px(p.X(z), Y + 17, zlab, TEXT, 12, "middle", bold=True)
        if xlab:
            p.text_px(p.X(z), Y + 32, xlab, BASE, 11, "middle")
    x, y = area_at
    if leader is not None:
        lx, ly = leader
        p.add(f'<line x1="{p.X(lx):.1f}" y1="{p.Y(ly):.1f}" x2="{p.X(x):.1f}" y2="{p.Y(y)+4:.1f}" '
              f'stroke="{PRACTICE}" stroke-width="1" opacity="0.8"/>')
    p.text(x, y, area, PRACTICE, LABEL, "middle", bold=True)
    OUT[name] = figure(W, H, [p], caption, aria=aria)


# ============================================================
# parametreler: effect of mu and sigma (two panels)
# ============================================================
def fig_parameters():
    W, H = 700, 270
    left = Plot(40, 40, 270, 180, (-10, 20), (0, 0.15))
    right = Plot(390, 40, 270, 180, (-20, 20), (0, 0.22))
    colors = (THEORY, PRACTICE, BASE)
    # left: same sigma = 3, means 0, 5, 10
    for mu, c in zip((0, 5, 10), colors):
        pts = curve(mu, 3, -10, 20)
        left.polygon([(-10, 0)] + pts + [(20, 0)], c, 0.10)
        left.line(pts, c, 2.0)
        left.label(mu, pdf(mu, mu, 3), f"{MU} = {mu}", 0, -8, c, 12, "middle", bold=True)
    x_axis(left, [(v, num(v)) for v in (-10, -5, 0, 5, 10, 15, 20)], it("x"))
    y_axis(left, (0.05, 0.1), "", -10)
    left.text_px(left.x0 + left.w / 2, left.y0 - 26, f"{SIGMA} = 3, ortalamalar farklı", TEXT, 12, "middle", bold=True)
    # right: same mean 0, sigma = 2, 4, 8
    for s, c, dx, dy, anc in ((2, THEORY, 12, 4, "start"), (4, PRACTICE, 20, 14, "start"), (8, BASE, 0, -8, "middle")):
        pts = curve(0, s, -20, 20)
        right.polygon([(-20, 0)] + pts + [(20, 0)], c, 0.10)
        right.line(pts, c, 2.0)
        if s == 8:
            right.label(13, pdf(13, 0, 8), f"{SIGMA} = {s}", 6, -12, c, 12, "start", bold=True)
        else:
            xs = s * 0.9
            right.label(xs, pdf(xs, 0, s), f"{SIGMA} = {s}", dx, dy, c, 12, anc, bold=True)
    x_axis(right, [(v, num(v)) for v in (-20, -10, 0, 10, 20)], it("x"))
    y_axis(right, (0.1, 0.2), "", -20)
    right.text_px(right.x0 + right.w / 2, right.y0 - 26, f"{MU} = 0, standart sapmalar farklı", TEXT, 12, "middle", bold=True)
    OUT["parametreler"] = figure(
        W, H, [left, right],
        "Solda standart sapması 3 olan, ortalamaları 0, 5 ve 10 olan üç normal eğri: "
        "μ değişince eğrinin biçimi aynı kalır, yalnız yatay olarak kayar. Sağda ortalaması 0, "
        "standart sapmaları 2, 4 ve 8 olan üç normal eğri: σ büyüdükçe eğri basıklaşır ve yayılır, "
        "altındaki alan yine 1 kalır.",
        css_class=WIDE,
        aria="Two panels of normal densities: equal sigma with means 0, 5, 10 and equal mean with sigma 2, 4, 8")


# ============================================================
# tablo-alani: P(0 <= Z <= 1.25) = 0.3944
# ============================================================
def fig_table_area():
    std_normal_area(
        "tablo-alani", 0, 1.25, "0,3944",
        [(0, "0", ""), (1.25, "1,25", "")],
        "Standart normal eğrisinin altında 0 ile 1,25 arasında kalan alan: tablonun 1,2 satırı ile "
        "0,05 sütununun kesiştiği değer, P(0 ≤ Z ≤ 1,25) = 0,3944.",
        "Standard normal density with the area between 0 and 1.25 shaded, equal to 0.3944",
        area_at=(0.62, 0.17))


# ============================================================
# standartlastirma: N(3, 4) on (3, 5) <-> N(0, 1) on (0, 1)
# ============================================================
def fig_standardization():
    W, H = 700, 250
    left = Plot(30, 40, 280, 170, (-4, 10), (0, 0.21))
    right = Plot(400, 40, 280, 170, (-3.5, 3.5), (0, 0.42))
    shade(left, 3, 2, 3, 5)
    left.line(curve(3, 2, -4, 10), THEORY, 2.0)
    x_axis(left, [(v, num(v)) for v in (-3, -1, 1, 3, 5, 7, 9)], it("x"))
    guide(left, 3, 3, 2)
    guide(left, 5, 3, 2)
    left.text(4, 0.07, "0,3413", PRACTICE, 12, "middle", bold=True)
    left.text_px(left.x0 + left.w / 2, left.y0 - 22, f"{it('X')} ~ {it('N')}(3, 4)", TEXT, 12.5, "middle", bold=True)
    shade(right, 0, 1, 0, 1)
    right.line(curve(0, 1, -3.5, 3.5), THEORY, 2.0)
    x_axis(right, [(v, num(v)) for v in (-3, -2, -1, 0, 1, 2, 3)], it("z"))
    guide(right, 0, 0, 1)
    guide(right, 1, 0, 1)
    right.text(0.5, 0.14, "0,3413", PRACTICE, 12, "middle", bold=True)
    right.text_px(right.x0 + right.w / 2, right.y0 - 22, f"{it('Z')} ~ {it('N')}(0, 1)", TEXT, 12.5, "middle", bold=True)
    # arrow between the panels
    ax0, ax1, ay = 318, 392, 120
    right.add(f'<line x1="{ax0}" y1="{ay}" x2="{ax1-9}" y2="{ay}" stroke="{REMARK}" stroke-width="1.8"/>'
              f'<polygon points="{ax1},{ay} {ax1-9},{ay-4} {ax1-9},{ay+4}" fill="{REMARK}"/>')
    right.text_px((ax0 + ax1) / 2, ay - 26, f"{it('z')} =", REMARK, 12, "middle")
    right.text_px((ax0 + ax1) / 2, ay - 10, f"({it('x')} {MINUS} 3)/2", REMARK, 12, "middle")
    OUT["standartlastirma"] = figure(
        W, H, [left, right],
        "Standartlaştırma alanı korur: N(3, 4) eğrisinin altında 3 ile 5 arasında kalan alan, "
        "z = (x − 3)/2 dönüşümüyle standart normal eğrisinin altında 0 ile 1 arasında kalan alana "
        "dönüşür; ikisi de 0,3413'tür.",
        css_class=WIDE,
        aria="Area between 3 and 5 under the N(3,4) density equals the area between 0 and 1 under the standard normal density")


# ============================================================
# agirlik-a/b/c: weights X ~ N(68.5, 2.3^2)
# ============================================================
def fig_weights():
    std_normal_area(
        "agirlik-a", 1.52, 9, "0,0643",
        [(1.52, "1,52", "72")],
        "Ağırlıklar N(68,5; 2,3²) dağılımlı. X > 72 olayı Z > 1,52 olayına karşılık gelir; sağ kuyruğun "
        "alanı 0,5 − 0,4357 = 0,0643'tür. Eksenin altındaki ikinci satırdaki sayılar X'in karşılık gelen değerleridir.",
        "Standard normal density with the right tail beyond 1.52 shaded, area 0.0643",
        area_at=(2.35, 0.12), leader=(1.9, 0.03), xmean="68,5")
    std_normal_area(
        "agirlik-b", 0.65, 1.52, "0,1935",
        [(0.65, "0,65", "70"), (1.52, "1,52", "72")],
        "70 < X < 72 olayı 0,65 < Z < 1,52 olayına karşılık gelir; taralı alan "
        "0,4357 − 0,2422 = 0,1935'tir.",
        "Standard normal density with the area between 0.65 and 1.52 shaded, area 0.1935",
        area_at=(2.25, 0.26), leader=(1.05, 0.12), xmean="68,5")
    std_normal_area(
        "agirlik-c", -1.52, 0.65, "0,6779",
        [(-1.52, num(-1.52), "65"), (0.65, "0,65", "70")],
        "65 < X < 70 olayı −1,52 < Z < 0,65 olayına karşılık gelir; aralık 0'ı içerdiği için iki "
        "tablo alanı toplanır: 0,4357 + 0,2422 = 0,6779.",
        "Standard normal density with the area between -1.52 and 0.65 shaded, area 0.6779",
        area_at=(-0.45, 0.16), xmean="68,5")


# ============================================================
# kuantil-a/b: X ~ N(3, 36)
# ============================================================
def quantile_fig(name, a, b, area, ticks, caption, aria, area_at, leader=None):
    W, H = 560, 250
    p = Plot(40, 26, 480, 180, (-16, 22), (0, 0.07))
    shade(p, 3, 6, a, b)
    p.line(curve(3, 6, -16, 22), THEORY, 2.0)
    x_axis(p, [(v, "") for v, _ in ticks], it("x"))
    for v, lab in ticks:
        guide(p, v, 3, 6, PRACTICE if v != 3 else TEXT)
        p.text_px(p.X(v), p.Y(0) + 17, lab, TEXT, 12, "middle")
    x, y = area_at
    if leader is not None:
        lx, ly = leader
        p.add(f'<line x1="{p.X(lx):.1f}" y1="{p.Y(ly):.1f}" x2="{p.X(x):.1f}" y2="{p.Y(y)+4:.1f}" '
              f'stroke="{PRACTICE}" stroke-width="1" opacity="0.8"/>')
    p.text(x, y, area, PRACTICE, LABEL, "middle", bold=True)
    OUT[name] = figure(W, H, [p], caption, aria=aria)


def fig_quantiles():
    quantile_fig(
        "kuantil-a", 12.869, 22, "0,05",
        [(3, f"{MU} = 3"), (12.869, f"{it('x')}{sub('0')} {APPROX} 12,87")],
        "X ~ N(3, 36) için sağ kuyruğun alanı 0,05 olacak biçimde seçilen nokta: "
        "x₀ = 3 + 6 · 1,645 ≈ 12,87.",
        "Normal density with mean 3 and sd 6, right tail beyond 12.87 shaded with area 0.05",
        area_at=(16.5, 0.03), leader=(14.6, 0.004))
    quantile_fig(
        "kuantil-b", -6.869, 22, "0,95",
        [(-6.869, f"{MINUS}{it('x')}{sub('0')} {APPROX} {MINUS}6,87"), (3, f"{MU} = 3")],
        "X ~ N(3, 36) için P(X > −x₀) = 0,95 koşulu: −x₀ noktasının sağındaki alan 0,95, "
        "solundaki alan 0,05'tir; buradan x₀ ≈ 6,87 bulunur.",
        "Normal density with mean 3 and sd 6, area to the right of -6.87 shaded, equal to 0.95",
        area_at=(8.5, 0.025))


# ============================================================
# binomial bars with a normal curve and continuity correction
# ============================================================
def binom_pmf(n, p, k):
    return math.comb(n, k) * p ** k * (1 - p) ** (n - k)


def binom_fig(name, n, prob, lo, hi, xr, yr, yticks, xticks, caption, aria, area_at):
    W, H = 580, 270
    p = Plot(50, 30, 480, 190, xr, yr)
    mu, s = n * prob, math.sqrt(n * prob * (1 - prob))
    k0, k1 = max(0, math.ceil(xr[0] + 0.5)), min(n, math.floor(xr[1] - 0.5))
    shade(p, mu, s, lo - 0.5, hi + 0.5, THEORY, 0.20)
    for k in range(k0, k1 + 1):
        h = binom_pmf(n, prob, k)
        inside = lo <= k <= hi
        color = PRACTICE if inside else BASE
        p.polygon([(k - 0.5, 0), (k - 0.5, h), (k + 0.5, h), (k + 0.5, 0)],
                  color, 0.30 if inside else 0.12, stroke=color, width=1.0)
    p.line(curve(mu, s, xr[0], xr[1]), THEORY, 2.0)
    for v in (lo - 0.5, hi + 0.5):
        p.vline(v, 0, yr[1] * 0.93, THEORY, "5 3", 0.9)
    x_axis(p, [(k, num(k)) for k in xticks], it("x"))
    y_axis(p, yticks, "", xr[0])
    p.label(lo - 0.5, yr[1] * 0.93, num(lo - 0.5), 0, -6, THEORY, 12, "middle", bold=True)
    p.label(hi + 0.5, yr[1] * 0.93, num(hi + 0.5), 0, -6, THEORY, 12, "middle", bold=True)
    x, y, text = area_at
    p.text(x, y, text, THEORY, 12, "start")
    OUT[name] = figure(W, H, [p], caption, aria=aria)


def fig_binomial():
    binom_fig(
        "para-yaklasim", 12, 0.5, 4, 6, (-0.9, 12.9), (0, 0.27), (0.05, 0.1, 0.15, 0.2), range(0, 13),
        "Binom(12; 1/2) olasılıkları, her biri x − 1/2 ile x + 1/2 arasında duran genişliği 1 olan "
        "dikdörtgenler olarak çizildi; eğri N(6, 3) yoğunluğudur. 4, 5 ve 6'nın dikdörtgenleri "
        "(turuncu) 3,5 ile 6,5 arasını kaplar; bu yüzden normal yaklaşımda eğrinin altında 3,5 ile "
        "6,5 arasında kalan alan (mavi) kullanılır.",
        "Binomial 12, 1/2 probabilities as unit-width bars with the N(6,3) density; bars 4 to 6 and the "
        "area between 3.5 and 6.5 are shaded",
        (8.6, 0.2, f"{it('N')}(6, 3)"))
    binom_fig(
        "kiz-ogrenci", 30, 0.5, 11, 19, (6.1, 23.9), (0, 0.16), (0.05, 0.1, 0.15), range(7, 24),
        "Binom(30; 1/2) olasılıkları ve N(15; 7,5) eğrisi. 11'den 19'a kadar (uçlar dâhil) olan "
        "dikdörtgenler 10,5 ile 19,5 arasını kaplar; yaklaşık olasılık eğrinin bu aralıktaki alanıdır.",
        "Binomial 30, 1/2 probabilities with the N(15, 7.5) density; bars 11 to 19 and the area between "
        "10.5 and 19.5 are shaded",
        (20.1, 0.125, f"{it('N')}(15; 7,5)"))


fig_parameters()
fig_table_area()
fig_standardization()
fig_weights()
fig_quantiles()
fig_binomial()

for name, content in OUT.items():
    with io.open(OUT_DIR / f"{PREFIX}{name}.md", "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
print(f"generated {len(OUT)} figures:", ", ".join(OUT))
