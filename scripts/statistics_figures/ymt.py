# -*- coding: utf-8 -*-
"""
Figures of the chapter "Yakınsama ve Merkezi Limit Teoremi"
(dersler/matematiksel-istatistik/yakinsama-ve-merkezi-limit-teoremi.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box: a figure that illustrates a
definition sits directly below that box. The figures are NOT produced at
build time. Run

    python scripts/statistics_figures/ymt.py
    python scripts/center_figures.py "statistics-ymt-*.md" --keep-width
    python scripts/check_figure_labels.py "scripts/_figures/statistics-ymt-*.md"

and paste the markup of scripts/_figures/statistics-ymt-<name>.md into the
.qmd. Captions are Turkish on purpose (they are shown on the site); aria
labels are plain ASCII.
"""
import io
import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, WIDE, TEXT, THEORY, PRACTICE, BASE, REMARK  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "statistics-ymt-"
OUT = {}

MINUS, MU, SIGMA, APPROX, LEQ, GEQ = "&#8722;", "&#956;", "&#963;", "&#8776;", "&#8804;", "&#8805;"
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
    return f'<tspan font-size="10" dy="3">{s}</tspan><tspan dy="-3">&#8203;</tspan>'


def xbar(n=""):
    """X with a combining overline and an optional subscript."""
    return it("X&#772;") + (sub(it(n)) if n else "")


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


def y_axis(p, ticks, name="", x=None, labels=None):
    X = p.X(p.xmin if x is None else x)
    top, bottom = p.y0 - 10, p.Y(p.ymin)
    p.add(f'<g stroke="{TEXT}" stroke-width="1.1" opacity="0.5" fill="{TEXT}">'
          f'<line x1="{X:.1f}" y1="{bottom:.1f}" x2="{X:.1f}" y2="{top:.1f}"/>'
          f'<polygon points="{X:.1f},{top:.1f} {X-3.5:.1f},{top+8:.1f} {X+3.5:.1f},{top+8:.1f}" stroke="none"/></g>')
    for i, v in enumerate(ticks):
        Y = p.Y(v)
        lab = num(v) if labels is None else labels[i]
        p.add(f'<line x1="{X-3:.1f}" y1="{Y:.1f}" x2="{X+3:.1f}" y2="{Y:.1f}" stroke="{TEXT}" stroke-width="1" opacity="0.7"/>')
        p.add(f'<text x="{X-7:.1f}" y="{Y+4:.1f}" fill="{TEXT}" font-size="{TICK}" text-anchor="end" opacity="0.8">{lab}</text>')
    if name:
        p.add(f'<text x="{X+8:.1f}" y="{top+6:.1f}" fill="{TEXT}" font-size="12" opacity="0.85">{name}</text>')


def legend(p, px, py, items, gap=19):
    """Legend rows (color, text, dash) starting at pixel (px, py)."""
    for i, (color, text, dash) in enumerate(items):
        y = py + i * gap
        da = f' stroke-dasharray="{dash}"' if dash else ""
        p.add(f'<line x1="{px:.1f}" y1="{y-4:.1f}" x2="{px+22:.1f}" y2="{y-4:.1f}" stroke="{color}" stroke-width="2.2"{da}/>')
        p.text_px(px + 28, y, text, TEXT, 12, "start")


def guide(p, x, mu, s, color=PRACTICE):
    p.vline(x, 0, pdf(x, mu, s), color, "4 3", 0.8)


def std_normal_area(name, a, b, area, bounds, caption, aria, area_at, xmean="", extra=None):
    """Standard normal curve with P(a < Z < b) shaded (bounds: (z, z label, x label))."""
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
    p.text(x, y, area, PRACTICE, LABEL, "middle", bold=True)
    if extra:
        extra(p)
    OUT[name] = figure(W, H, [p], caption, aria=aria)


# ============================================================
# para-ortalama: running proportion of heads, three simulated paths
# ============================================================
def fig_coin():
    W, H = 560, 280
    p = Plot(56, 30, 460, 200, (0, 3), (0, 1))
    p.polygon([(0, 0.45), (3, 0.45), (3, 0.55), (0, 0.55)], REMARK, 0.16)
    p.line([(0, 0.5), (3, 0.5)], TEXT, 1.0, "5 4", 0.6)
    rng = random.Random(20260923)
    colors = (THEORY, PRACTICE, BASE)
    for c in colors:
        heads, pts = 0, []
        for n in range(1, 1001):
            heads += rng.random() < 0.5
            pts.append((math.log10(n), heads / n))
        p.line(pts, c, 1.6, None, 0.95)
    x_axis(p, [(0, "1"), (1, "10"), (2, "100"), (3, "1000")], it("n"))
    y_axis(p, (0.25, 0.5, 0.75, 1.0), "", 0, ["0,25", "1/2", "0,75", "1"])
    p.text_px(p.X(0) - 7, p.Y(0) + 4, "0", TEXT, TICK, "end")
    p.text_px(p.X(3) - 4, p.Y(0.55) - 8, f"1/2 {MINUS} 0,05 ile 1/2 + 0,05 arası", REMARK, 12, "end")
    p.text_px(p.x0 + 10, p.y0 - 12, f"ilk {it('n')} atıştaki tura oranı, {xbar('n')}", TEXT, 12, "start")
    OUT["para-ortalama"] = figure(
        W, H, [p],
        "Düzgün bir paranın 1000 kez atıldığı üç ayrı deneyde, ilk n atıştaki tura oranı (yatay eksen "
        "logaritmik). İlk atışlarda oran 0 ile 1 arasında sert dalgalanır; n büyüdükçe üç yol da 1/2'nin "
        "çevresindeki 0,45 ile 0,55 arasındaki banda girer ve orada kalır.",
        aria="Three simulated running proportions of heads over 1000 tosses approaching one half, log scale in n")


# ============================================================
# kesikli-duzgun-f: F_n of the discrete uniform on {1/n,...,1} vs F(x) = x
# ============================================================
def step_panel(x0, n, color):
    p = Plot(x0, 40, 250, 180, (-0.25, 1.3), (0, 1.1))
    p.line([(-0.25, 0), (0, 0), (1, 1), (1.3, 1)], THEORY, 2.0)
    for k in range(0, n + 1):
        a = k / n
        b = (k + 1) / n if k < n else 1.3
        yv = k / n
        if k == 0:
            p.line([(-0.25, 0), (1 / n, 0)], color, 2.0)
            continue
        p.line([(a, yv), (b, yv)], color, 2.0)
        p.vline(a, (k - 1) / n, yv, color, "2 2", 0.7)
        p.add(f'<circle cx="{p.X(a):.1f}" cy="{p.Y(yv):.1f}" r="2.4" fill="{color}"/>')
    x_axis(p, [(0, "0"), (0.5, "0,5"), (1, "1")], it("x"))
    y_axis(p, (0.5, 1.0), "", -0.25)
    p.text_px(p.x0 + p.w / 2, p.y0 - 20, f"{it('n')} = {n}", TEXT, 13, "middle", bold=True)
    return p


def fig_discrete_uniform():
    W, H = 700, 270
    left = step_panel(50, 5, PRACTICE)
    right = step_panel(400, 20, PRACTICE)
    legend(left, 70, 44, [(THEORY, f"{it('F')}({it('x')}) = {it('x')}", None),
                          (PRACTICE, f"{it('F')}{sub(it('n'))}({it('x')})", None)])
    OUT["kesikli-duzgun-f"] = figure(
        W, H, [left, right],
        "{1/n, 2/n, …, 1} kümesi üzerindeki kesikli düzgün dağılımın basamaklı dağılım fonksiyonu Fₙ "
        "(turuncu) ile U(0, 1) dağılımının F(x) = x fonksiyonu (mavi). Solda n = 5, sağda n = 20: "
        "basamaklar 1/n yüksekliğindedir ve n büyüdükçe doğruya yapışır.",
        css_class=WIDE,
        aria="Step distribution functions of the discrete uniform on k over n for n 5 and 20 approaching the line F(x) = x")


# ============================================================
# mlt-ustel: standardized sums of Exp(1) variables (exact gamma densities)
# ============================================================
def std_gamma_pdf(z, n):
    s = n + math.sqrt(n) * z
    if s <= 0:
        return 0.0
    return math.sqrt(n) * math.exp((n - 1) * math.log(s) - s - math.lgamma(n))


def fig_clt_exponential():
    W, H = 560, 280
    p = Plot(46, 30, 470, 200, (-3.5, 4.0), (0, 0.56))
    xs = [-3.5 + 7.5 * k / 600 for k in range(601)]
    items = [(2, BASE, "5 3"), (8, PRACTICE, None), (32, REMARK, None)]
    p.line(curve(0, 1, -3.5, 4.0), THEORY, 2.4)
    for n, c, dash in items:
        p.line([(x, std_gamma_pdf(x, n)) for x in xs], c, 1.9, dash)
    x_axis(p, [(k, num(k)) for k in range(-3, 5)], it("z"))
    y_axis(p, (0.1, 0.2, 0.3, 0.4, 0.5), "", -3.5)
    legend(p, 350, 50, [(BASE, f"{it('n')} = 2", "5 3"), (PRACTICE, f"{it('n')} = 8", None),
                        (REMARK, f"{it('n')} = 32", None), (THEORY, f"{it('N')}(0, 1)", None)])
    OUT["mlt-ustel"] = figure(
        W, H, [p],
        "Üstel(1) dağılımlı n bağımsız değişkenin standartlaştırılmış toplamının (ya da ortalamasının) "
        "gerçek yoğunluğu, n = 2, 8 ve 32 için. Üstel dağılım çok çarpıktır; yine de n büyüdükçe eğriler "
        "standart normal yoğunluğa (mavi) yaklaşır.",
        aria="Exact densities of standardized sums of exponential variables for n 2, 8, 32 approaching the standard normal density")


# ============================================================
# zar-toplam: pmf of the sum of n dice with the normal density (n = 1, 2, 5)
# ============================================================
def dice_pmf(n):
    dist = {0: 1.0}
    for _ in range(n):
        nd = {}
        for s, pr in dist.items():
            for k in range(1, 7):
                nd[s + k] = nd.get(s + k, 0.0) + pr / 6
        dist = nd
    return dist


def fig_dice_sums():
    W, H = 700, 250
    specs = [(1, 45, (0.2, 6.8), 0.25, (1, 2, 3, 4, 5, 6), (0.1, 0.2)),
             (2, 265, (1.2, 12.8), 0.18, (2, 4, 7, 10, 12), (0.05, 0.1, 0.15)),
             (5, 485, (4.2, 30.8), 0.115, (5, 10, 15, 20, 25, 30), (0.05, 0.1))]
    panels = []
    for n, x0, xr, ymax, xt, yt in specs:
        p = Plot(x0, 40, 180, 160, xr, (0, ymax))
        dist = dice_pmf(n)
        for s, pr in sorted(dist.items()):
            p.polygon([(s - 0.5, 0), (s - 0.5, pr), (s + 0.5, pr), (s + 0.5, 0)], PRACTICE, 0.30,
                      stroke=PRACTICE, width=0.9)
        mu, sd = 3.5 * n, math.sqrt(35 * n / 12)
        p.line(curve(mu, sd, xr[0], xr[1]), THEORY, 2.0)
        x_axis(p, [(v, num(v)) for v in xt], "")
        y_axis(p, yt, "", xr[0])
        p.text_px(p.x0 + p.w / 2, p.y0 - 20, f"{it('n')} = {n}", TEXT, 13, "middle", bold=True)
        panels.append(p)
    OUT["zar-toplam"] = figure(
        W, H, panels,
        "n zarın toplamının olasılıkları (genişliği 1 olan turuncu dikdörtgenler) ve aynı beklenen değer "
        "ile varyansa sahip N(3,5n; 35n/12) eğrisi, n = 1, 2 ve 5 için. Tek zarın dağılımı düzdür; "
        "iki zarda üçgen olur, beş zarda şimdiden çan eğrisine çok yakındır.",
        css_class=WIDE,
        aria="Probability bars of the sum of 1, 2 and 5 dice with the matching normal density")


# ============================================================
# zar-a: P(|Z| <= 0.59) = 0.4448
# ============================================================
def fig_dice_a():
    std_normal_area(
        "zar-a", -0.59, 0.59, "0,4448",
        [(-0.59, num(-0.59), "3,4"), (0.59, "0,59", "3,6")],
        "100 zar atışının ortalaması için 3,4 ≤ X̄ ≤ 3,6 olayı yaklaşık olarak −0,59 ≤ Z ≤ 0,59 olayına "
        "karşılık gelir; taralı alan 2 · 0,2224 = 0,4448'dir. Eksenin altındaki ikinci satırda "
        "X̄'nin karşılık gelen değerleri var.",
        "Standard normal density with the area between -0.59 and 0.59 shaded, area 0.4448",
        area_at=(0, 0.16), xmean="")


# ============================================================
# zar-b: the same band for n = 100 and n = 10000
# ============================================================
def band_panel(x0, n, xr, ymax, xt, yt, area):
    p = Plot(x0, 40, 250, 170, xr, (0, ymax))
    sd = math.sqrt(35 / 12 / n)
    p.polygon([(3.4, 0), (3.4, ymax * 0.98), (3.6, ymax * 0.98), (3.6, 0)], REMARK, 0.10)
    shade(p, 3.5, sd, max(3.4, xr[0]), min(3.6, xr[1]))
    p.line(curve(3.5, sd, xr[0], xr[1]), THEORY, 2.0)
    for v in (3.4, 3.6):
        p.vline(v, 0, ymax * 0.98, REMARK, "4 3", 0.9)
    x_axis(p, [(v, num(v)) for v in xt], it("x&#772;"))
    y_axis(p, yt, "", xr[0])
    p.text_px(p.x0 + p.w / 2, p.y0 - 20, f"{it('n')} = {n:,}".replace(",", " "), TEXT, 13, "middle", bold=True)
    return p, area


def fig_dice_b():
    W, H = 700, 270
    left, _ = band_panel(50, 100, (2.9, 4.1), 2.6, (3.0, 3.4, 3.6, 4.0), (1, 2), "0,4448")
    right, _ = band_panel(400, 10000, (3.34, 3.66), 26, (3.4, 3.5, 3.6), (10, 20), "")
    left.text(3.5, 0.75, "0,4448", PRACTICE, LABEL, "middle", bold=True)
    right.label(3.535, 14, f"{APPROX} 1", 0, 0, PRACTICE, LABEL, "start", bold=True)
    OUT["zar-b"] = figure(
        W, H, [left, right],
        "Zar ortalamasının yaklaşık yoğunluğu N(3,5; (35/12)/n) ve 3,4 ile 3,6 arasındaki bant. "
        "n = 100 iken bandın içinde kalan alan 0,4448'dir. n = 10 000 iken yoğunluk öylesine sivrilir ki "
        "(eksen ölçeği farklı) bütün alan bandın içine sığar: olasılık 0,999999995'tir.",
        css_class=WIDE,
        aria="Approximate densities of the dice mean for n 100 and 10000 with the band from 3.4 to 3.6")


# ============================================================
# zar-d: exact pmf of the sum of 100 dice near 350, continuity correction
# ============================================================
def fig_dice_d():
    W, H = 580, 280
    xr = (329.5, 370.5)
    p = Plot(56, 34, 460, 190, xr, (0, 0.027))
    dist = dice_pmf(100)
    mu, sd = 350, math.sqrt(875 / 3)
    shade(p, mu, sd, 349.5, 350.5, THEORY, 0.35)
    for s in range(330, 371):
        pr = dist[s]
        hot = s == 350
        c = PRACTICE if hot else BASE
        p.polygon([(s - 0.5, 0), (s - 0.5, pr), (s + 0.5, pr), (s + 0.5, 0)], c,
                  0.45 if hot else 0.14, stroke=c, width=1.0 if hot else 0.7)
    p.line(curve(mu, sd, xr[0], xr[1]), THEORY, 2.0)
    x_axis(p, [(v, num(v)) for v in (330, 340, 350, 360, 370)], it("t"))
    y_axis(p, (0.01, 0.02), "", xr[0])
    p.label(350, dist[350], f"{it('P')}({it('T')} = 350)", 0, -10, PRACTICE, 12.5, "middle", bold=True)
    p.label(361, pdf(361, mu, sd), f"{it('N')}(350; 291,67)", 8, -6, THEORY, 12.5, "start", bold=True)
    OUT["zar-d"] = figure(
        W, H, [p],
        "100 zarın toplamı T'nin 330 ile 370 arasındaki gerçek olasılıkları (dikdörtgenler) ve "
        "N(350; 291,67) eğrisi. T = 350 olasılığı, genişliği 1 olan turuncu dikdörtgenin alanıdır; "
        "normal yaklaşımda bunun yerine eğrinin altında 349,5 ile 350,5 arasında kalan ince şerit alınır.",
        aria="Exact probabilities of the sum of 100 dice between 330 and 370 with the normal density; bar at 350 highlighted")


# ============================================================
# ustel-toplam: sum of 100 Exp(1) lifetimes, P(T >= 110)
# ============================================================
def fig_exp_sum():
    W, H = 580, 270
    xr = (62, 138)
    p = Plot(56, 30, 460, 190, xr, (0, 0.044))
    shade(p, 100, 10, 110, xr[1])
    p.line(curve(100, 10, xr[0], xr[1]), THEORY, 2.0)
    xs = [xr[0] + (xr[1] - xr[0]) * k / 500 for k in range(501)]
    p.line([(x, math.exp(99 * math.log(x) - x - math.lgamma(100))) for x in xs], BASE, 1.8, "5 3")
    guide(p, 110, 100, 10)
    x_axis(p, [(v, num(v)) for v in (70, 80, 90, 100, 110, 120, 130)], it("t"))
    y_axis(p, (0.01, 0.02, 0.03, 0.04), "", xr[0])
    p.add(f'<line x1="{p.X(115):.1f}" y1="{p.Y(0.006):.1f}" x2="{p.X(121):.1f}" y2="{p.Y(0.0125):.1f}" '
          f'stroke="{PRACTICE}" stroke-width="1" opacity="0.8"/>')
    p.label(121, 0.0125, "0,1587", 2, -4, PRACTICE, LABEL, "start", bold=True)
    legend(p, 72, 50, [(THEORY, f"{it('N')}(100, 100)", None), (BASE, "gerçek yoğunluk (gamma)", "5 3")])
    OUT["ustel-toplam"] = figure(
        W, H, [p],
        "100 parçanın toplam ömrü T için N(100, 100) yaklaşımı (mavi) ve T'nin gerçek yoğunluğu (kesikli). "
        "İki eğri neredeyse çakışır. Taralı sağ kuyruk T ≥ 110 olayıdır; alanı yaklaşık 0,5 − 0,3413 = 0,1587.",
        aria="Normal density N(100,100) and the exact gamma density of the total lifetime, right tail beyond 110 shaded")


# ============================================================
# radyo: X-bar ~ N(4, 1/16), two tails beyond 3.5 and 4.5
# ============================================================
def fig_radio():
    W, H = 560, 260
    xr = (2.95, 5.05)
    p = Plot(46, 26, 470, 180, xr, (0, 1.75))
    shade(p, 4, 0.25, xr[0], 3.5)
    shade(p, 4, 0.25, 4.5, xr[1])
    p.line(curve(4, 0.25, xr[0], xr[1]), THEORY, 2.0)
    for v in (3.5, 4.5):
        guide(p, v, 4, 0.25)
    p.vline(4, 0, pdf(4, 4, 0.25), TEXT, "4 3", 0.45)
    x_axis(p, [(v, num(v)) for v in (3.0, 3.5, 4.0, 4.5, 5.0)], it("x&#772;"))
    Y = p.Y(0)
    for v, z in ((3.5, f"{it('z')} = {MINUS}2"), (4.5, f"{it('z')} = 2")):
        p.text_px(p.X(v), Y + 32, z, BASE, 11, "middle")
    y_axis(p, (0.5, 1.0, 1.5), "", xr[0])
    p.label(3.25, 0.12, "0,0228", 0, 0, PRACTICE, LABEL, "middle", bold=True)
    p.label(4.75, 0.12, "0,0228", 0, 0, PRACTICE, LABEL, "middle", bold=True)
    p.label(4.3, pdf(4.3, 4, 0.25), f"{it('N')}(4; 1/16)", 10, -4, THEORY, 12.5, "start", bold=True)
    OUT["radyo"] = figure(
        W, H, [p],
        "16 kişilik örneklemin ortalama dinleme süresi X̄ ~ N(4; 1/16). Ortalamanın 4'ten yarım saatten "
        "fazla sapması iki kuyruğun (X̄ < 3,5 ve X̄ > 4,5) toplam alanıdır: 2 · 0,0228 = 0,0456.",
        aria="Normal density with mean 4 and sd 0.25, both tails beyond 3.5 and 4.5 shaded")


# ============================================================
# boy-mlt: P(|Z| < 1.58) = 0.8858 against the Chebyshev bound 0.6
# ============================================================
def fig_height():
    def extra(p):
        p.text_px(p.X(3.5), p.y0 + 10, f"Chebyshev alt sınırı: 0,6", REMARK, 12, "end", bold=True)
    std_normal_area(
        "boy-mlt", -1.58, 1.58, "0,8858",
        [(-1.58, num(-1.58), f"{MU} {MINUS} 1"), (1.58, "1,58", f"{MU} + 1")],
        "30 kişilik örneklemde |X̄ − μ| < 1 olayı yaklaşık olarak −1,58 < Z < 1,58 olayıdır; taralı alan "
        "2 · 0,4429 = 0,8858. Chebyshev eşitsizliği yalnız 0,6'lık bir alt sınır verir; normal yaklaşımın "
        "değeri bu sınırın üstündedir.",
        "Standard normal density with the area between -1.58 and 1.58 shaded, area 0.8858",
        area_at=(0, 0.16), xmean="", extra=extra)


fig_coin()
fig_discrete_uniform()
fig_clt_exponential()
fig_dice_sums()
fig_dice_a()
fig_dice_b()
fig_dice_d()
fig_exp_sum()
fig_radio()
fig_height()

for name, content in OUT.items():
    with io.open(OUT_DIR / f"{PREFIX}{name}.md", "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
print(f"generated {len(OUT)} figures:", ", ".join(OUT))
