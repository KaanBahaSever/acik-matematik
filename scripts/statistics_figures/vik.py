# -*- coding: utf-8 -*-
"""
Figures of the chapter "Varyans ve İki Kitle İçin Aralık Tahmini"
(dersler/matematiksel-istatistik/varyans-ve-iki-kitle-icin-aralik-tahmini.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution,
exercise or callout), never inside a definition box: a figure that
illustrates a definition sits directly below that box. The figures are NOT
produced at build time. Run

    python scripts/statistics_figures/vik.py
    python scripts/center_figures.py "statistics-vik-*.md" --keep-width
    python scripts/check_figure_labels.py "scripts/_figures/statistics-vik-*.md"

and paste the markup of scripts/_figures/statistics-vik-<name>.md into the
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
PREFIX = "statistics-vik-"
OUT = {}

MINUS, MU, SIGMA, NU, CHI = "&#8722;", "&#956;", "&#963;", "&#957;", "&#967;"
LEQ, NEQ, APPROX = "&#8804;", "&#8800;", "&#8776;"
SUP2 = "&#178;"
SUB1, SUB2 = "&#8321;", "&#8322;"
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


# -- densities ----------------------------------------------------------------
def chi2_pdf(x, k):
    if x <= 0:
        return 0.0
    return math.exp((k / 2 - 1) * math.log(x) - x / 2 - (k / 2) * math.log(2) - math.lgamma(k / 2))


def f_pdf(x, a, b):
    if x <= 0:
        return 0.0
    logc = math.lgamma((a + b) / 2) - math.lgamma(a / 2) - math.lgamma(b / 2) + (a / 2) * math.log(a / b)
    return math.exp(logc + (a / 2 - 1) * math.log(x) - ((a + b) / 2) * math.log(1 + a * x / b))


def normal_pdf(x, mu, s):
    return math.exp(-0.5 * ((x - mu) / s) ** 2) / (s * math.sqrt(2 * math.pi))


def sample(f, a, b, n=SAMPLES):
    return [(a + (b - a) * k / n, f(a + (b - a) * k / n)) for k in range(n + 1)]


def shade(p, f, a, b, color=PRACTICE, opacity=0.32):
    p.polygon([(a, 0)] + sample(f, a, b, 200) + [(b, 0)], color, opacity)


# -- axes -----------------------------------------------------------------------
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
        p.add(f'<text x="{X+8:.1f}" y="{top+6:.1f}" fill="{TEXT}" font-size="12" font-style="italic" opacity="0.85">{name}</text>')


def leader(p, x0, y0, x1, y1, color=PRACTICE):
    """Thin line from a data point to a label position (both in data units)."""
    p.add(f'<line x1="{p.X(x0):.1f}" y1="{p.Y(y0):.1f}" x2="{p.X(x1):.1f}" y2="{p.Y(y1):.1f}" '
          f'stroke="{color}" stroke-width="1" opacity="0.8"/>')


def two_tailed(name, f, xr, ymax, lo, hi, lo_lab, hi_lab, ticks, dist_label, dist_at,
               tail_at, mid_at, caption, aria, tail="0,025", middle="0,95"):
    """Density with both alpha/2 tails shaded and the middle 1 - alpha area marked."""
    W, H = 560, 250
    p = Plot(40, 26, 480, 180, xr, (0, ymax))
    shade(p, f, xr[0], xr[1], THEORY, 0.10)
    shade(p, f, xr[0] if xr[0] > 0 else 1e-9, lo)
    shade(p, f, hi, xr[1])
    p.line(sample(f, max(xr[0], 1e-6), xr[1]), THEORY, 2.0)
    x_axis(p, [(v, num(v)) for v in ticks] + [(lo, ""), (hi, "")], it("x"))
    Y = p.Y(0)
    for v, lab in ((lo, lo_lab), (hi, hi_lab)):
        p.vline(v, 0, f(v), PRACTICE, "4 3", 0.8)
        p.text_px(p.X(v), Y + 32, lab, PRACTICE, 12, "middle", bold=True)
    (lx, ly, ltx, lty), (rx, ry, rtx, rty) = tail_at
    leader(p, lx, ly, ltx, lty)
    p.text(ltx, lty, tail, PRACTICE, 12, "middle", bold=True)
    leader(p, rx, ry, rtx, rty)
    p.text(rtx, rty, tail, PRACTICE, 12, "middle", bold=True)
    p.text(mid_at[0], mid_at[1], middle, THEORY, LABEL, "middle", bold=True)
    p.text(dist_at[0], dist_at[1], dist_label, THEORY, LABEL, "start")
    OUT[name] = figure(W, H, [p], caption, aria=aria)


# ============================================================
# ki-kare-kantilleri: chi-square with 7 df, 0.05 in each tail
# ============================================================
def fig_chi2_quantiles():
    f = lambda x: chi2_pdf(x, 7)  # noqa: E731
    lo, hi = 2.17, 14.07
    two_tailed(
        "ki-kare-kantilleri", f, (0, 20), 0.145, lo, hi,
        f"{CHI}{SUP2}{sub('7; 0,05')} = 2,17", f"{CHI}{SUP2}{sub('7; 0,95')} = 14,07",
        (0, 4, 8, 12, 16, 20),
        f"{CHI}{SUP2}{sub('7')} yoğunluğu", (11.5, 0.11),
        ((1.5, 0.006, 0.9, 0.06), (15.0, 0.004, 16.6, 0.04)),
        (6.2, 0.055),
        "Serbestlik derecesi 7 olan ki-kare yoğunluğu. 2,17'nin solunda ve 14,07'nin sağında 0,05'er "
        "alan kalır; aradaki alan 0,90'dır. Varyans aralığında büyük kantil 14,07 alt sınırın, küçük "
        "kantil 2,17 üst sınırın paydasına gider.",
        "Chi-square density with 7 degrees of freedom, tails below 2.17 and above 14.07 shaded, "
        "each with area 0.05",
        tail="0,05", middle="0,90")


# ============================================================
# varyans-araligi: the interval 2.271 <= sigma^2 <= 16.0 around s^2 = 4.8
# ============================================================
def fig_variance_interval():
    W, H = 560, 130
    p = Plot(40, 20, 480, 60, (0, 18), (0, 1))
    x_axis(p, [(v, num(v)) for v in (0, 2, 4, 6, 8, 10, 12, 14, 16, 18)], f"{SIGMA}{SUP2}", y=0)
    lo, hi, s2 = 2.271, 16.0, 4.8
    yb = 0.55
    p.line([(lo, yb), (hi, yb)], THEORY, 5.0)
    for v in (lo, hi):
        p.line([(v, yb - 0.17), (v, yb + 0.17)], THEORY, 2.0)
    p.label(lo, yb, "2,27", 0, -14, THEORY, 12, "middle", bold=True)
    p.label(hi, yb, "16,0", 0, -14, THEORY, 12, "middle", bold=True)
    p.points([(s2, yb)], PRACTICE, 5.5)
    p.label(s2, yb, f"{it('s')}{SUP2} = 4,8", 0, -14, PRACTICE, 12, "middle", bold=True)
    mid = (lo + hi) / 2
    p.line([(mid, yb - 0.25), (mid, yb + 0.1)], TEXT, 1.2, "3 3", 0.7)
    p.label(mid, yb, f"orta nokta {APPROX} 9,14", 0, -14, TEXT, 11, "middle")
    OUT["varyans-araligi"] = figure(
        W, H, [p],
        "σ² için %95 güven aralığı [2,27; 16,0] ve nokta tahmini s² = 4,8. Tahmin aralığın ortasında "
        "değil, alt uca yakındır: aralık s²'nin iki yanına eşit uzanmaz, sağa doğru çok daha uzundur.",
        aria="Number line with the confidence interval from 2.27 to 16.0 for the variance and the "
             "point estimate 4.8 close to the lower end")


# ============================================================
# f-kantilleri: F with (8, 12) df, 0.025 in each tail
# ============================================================
def fig_f_quantiles():
    f = lambda x: f_pdf(x, 8, 12)  # noqa: E731
    lo, hi = 0.238, 3.51
    two_tailed(
        "f-kantilleri", f, (0, 5.5), 0.82, lo, hi,
        f"{it('F')}{sub('8, 12; 0,025')} {APPROX} 0,238", f"{it('F')}{sub('8, 12; 0,975')} = 3,51",
        (0, 1, 2, 3, 4, 5),
        f"{it('F')}{sub('8, 12')} yoğunluğu", (2.1, 0.55),
        ((0.15, 0.02, -0.12, 0.40), (3.8, 0.012, 4.35, 0.14)),
        (1.05, 0.28),
        "Serbestlik dereceleri 8 ve 12 olan F yoğunluğu. Sağ kuyruğun sınırı olan 0,975 kantili 3,51 "
        "tablodan okunur. Sol kuyruğun sınırı olan 0,025 kantili tabloda yoktur; serbestlik dereceleri "
        "yer değiştirmiş F dağılımının 0,975 kantilinden 1/4,20 ≈ 0,238 olarak bulunur. Her kuyruğun "
        "alanı 0,025, aradaki alan 0,95'tir.",
        "F density with 8 and 12 degrees of freedom, tails below 0.238 and above 3.51 shaded, "
        "each with area 0.025")


# ============================================================
# oran-araliklari: two intervals for sigma1^2/sigma2^2 on a log axis
# ============================================================
def fig_ratio_intervals():
    W, H = 580, 190
    lg = math.log10
    p = Plot(130, 30, 400, 110, (lg(0.2), lg(20)), (0, 2))
    ticks = (0.2, 0.5, 1, 2, 5, 10, 20)
    x_axis(p, [(lg(v), num(v)) for v in ticks], "oran", y=0)
    p.vline(0, 0, 2.05, REMARK, "5 3", 0.9)
    p.label(0, 2.05, "oran = 1", 0, -6, REMARK, 12, "middle", bold=True)
    rows = ((1.35, 0.570, 8.40, 2.0, "iki makine", "%95", THEORY),
            (0.6, 1.969, 14.25, 5.0, "iki yöntem", "%90", PRACTICE))
    for y, lo, hi, pt, name, level, c in rows:
        p.line([(lg(lo), y), (lg(hi), y)], c, 5.0)
        for v in (lo, hi):
            p.line([(lg(v), y - 0.14), (lg(v), y + 0.14)], c, 2.0)
        p.points([(lg(pt), y)], TEXT, 4.5)
        p.label(lg(lo), y, num(lo, 3 if lo < 1 else 2), 0, 22, c, 11, "middle")
        p.label(lg(hi), y, num(hi, 2), 0, 22, c, 11, "middle")
        p.text_px(p.x0 - 16, p.Y(y) - 2, name, c, 12, "end", bold=True)
        p.text_px(p.x0 - 16, p.Y(y) + 13, level, c, 11, "end")
    OUT["oran-araliklari"] = figure(
        W, H, [p],
        "Varyans oranı σ₁²/σ₂² için iki güven aralığı, logaritmik eksende (siyah noktalar s₁²/s₂² "
        "tahminleridir). Makinelerin aralığı 1'i içerir: varyansların eşit olması verilerle "
        "çelişmez. Yöntemlerin aralığı tümüyle 1'in sağındadır: birinci yöntemin varyansı daha büyüktür.",
        aria="Two confidence intervals for a variance ratio on a log axis: 0.570 to 8.40 contains 1, "
             "1.97 to 14.25 lies to the right of 1")


# ============================================================
# iki-kitle-durumlari: equal versus unequal population variances
# ============================================================
def fig_two_populations():
    W, H = 700, 250
    left = Plot(40, 46, 270, 160, (2, 26), (0, 0.44))
    right = Plot(400, 46, 270, 160, (2, 26), (0, 0.44))
    specs = ((left, ((10, 2), (16, 2)), f"{SIGMA}{SUB1}{SUP2} = {SIGMA}{SUB2}{SUP2}"),
             (right, ((10, 1), (16, 3)), f"{SIGMA}{SUB1}{SUP2} {NEQ} {SIGMA}{SUB2}{SUP2}"))
    for p, pops, title in specs:
        for (mu, s), c, lab in zip(pops, (THEORY, PRACTICE), ("1. kitle", "2. kitle")):
            pts = sample(lambda x, mu=mu, s=s: normal_pdf(x, mu, s), 2, 26)
            p.polygon([(2, 0)] + pts + [(26, 0)], c, 0.12)
            p.line(pts, c, 2.0)
            top = normal_pdf(mu, mu, s)
            p.label(mu, top, lab, 0, -8, c, 12, "middle", bold=True)
            p.vline(mu, 0, top, c, "4 3", 0.6)
        x_axis(p, [(v, num(v)) for v in (4, 8, 12, 16, 20, 24)], it("x"))
        p.text_px(p.x0 + p.w / 2, p.y0 - 26, title, TEXT, 13, "middle", bold=True)
    OUT["iki-kitle-durumlari"] = figure(
        W, H, [left, right],
        "Ortalamaları 10 ve 16 olan iki normal kitle. Solda iki eğri aynı biçimdedir, yalnız "
        "yerleri farklıdır: varyanslar eşittir ve tek bir ortak σ² tahmin edilir. Sağda birinci "
        "kitle dar, ikincisi geniştir: varyanslar farklıdır ve her biri ayrı tahmin edilir.",
        css_class=WIDE,
        aria="Two panels of two normal densities with means 10 and 16: equal spreads on the left, "
             "different spreads on the right")


# ============================================================
# welch-serbestlik: Welch degrees of freedom for n1 = 8, n2 = 12
# ============================================================
def fig_welch_df():
    W, H = 560, 270
    k1, k2 = 7, 11
    nu = lambda r: (r + 1) ** 2 / (r * r / k1 + 1 / k2)  # noqa: E731
    p = Plot(50, 30, 460, 180, (-2, 2), (5, 20))
    p.grid(ys=(7, 11, 18))
    pts = [(-2 + 4 * k / SAMPLES, nu(10 ** (-2 + 4 * k / SAMPLES))) for k in range(SAMPLES + 1)]
    p.line([(-2, 18), (2, 18)], REMARK, 1.4, "6 4", 0.9)
    p.line([(-2, 7), (2, 7)], REMARK, 1.4, "6 4", 0.9)
    p.line(pts, THEORY, 2.2)
    x_axis(p, [(v, lab) for v, lab in ((-2, "0,01"), (-1, "0,1"), (0, "1"), (1, "10"), (2, "100"))],
           it("R"), y=5)
    y_axis(p, (5, 7, 11, 15, 18, 20), it(NU), x=-2)
    p.label(-1.95, 18, f"{it('n')}{SUB1} + {it('n')}{SUB2} {MINUS} 2 = 18", 4, -6, REMARK, 12, "start", bold=True)
    p.label(1.95, 7, f"{it('n')}{SUB1} {MINUS} 1 = 7", -4, 17, REMARK, 12, "end", bold=True)
    rmax = k1 / k2
    p.points([(math.log10(rmax), 18)], THEORY, 4.0)
    p.label(math.log10(rmax), 18, f"{it('R')} = 7/11", 0, 20, THEORY, 12, "middle")
    rx = 7.5
    p.points([(math.log10(rx), nu(rx))], PRACTICE, 5.0)
    p.label(math.log10(rx), nu(rx), f"{it('R')} = 7,5;  {it(NU)} {APPROX} 8,89", 8, -10, PRACTICE, 12, "start", bold=True)
    OUT["welch-serbestlik"] = figure(
        W, H, [p],
        "n₁ = 8, n₂ = 12 için Welch serbestlik derecesi ν, R = (s₁²/n₁)/(s₂²/n₂) oranının fonksiyonu "
        "olarak (yatay eksen logaritmik). ν hiçbir zaman 18'i aşmaz ve 7'nin altına inmez; en büyük değer "
        "R = 7/11'de alınır. R büyüdükçe ν, birinci örneklemin n₁ − 1 = 7 değerine, R küçüldükçe ikinci "
        "örneklemin n₂ − 1 = 11 değerine yaklaşır. Turuncu nokta örnekteki R = 7,5 durumudur.",
        aria="Welch degrees of freedom as a function of the variance ratio R on a log axis, between 7 and 18, "
             "with the point R 7.5 and nu 8.89 marked")


fig_chi2_quantiles()
fig_variance_interval()
fig_f_quantiles()
fig_ratio_intervals()
fig_two_populations()
fig_welch_df()

for name, content in OUT.items():
    with io.open(OUT_DIR / f"{PREFIX}{name}.md", "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
print(f"generated {len(OUT)} figures:", ", ".join(OUT))
