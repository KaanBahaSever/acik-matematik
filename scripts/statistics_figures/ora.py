# -*- coding: utf-8 -*-
"""
Figures of the chapter "Oran için Aralık Tahmini"
(dersler/matematiksel-istatistik/oran-icin-aralik-tahmini.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box: a figure that illustrates a
definition sits directly below that box. The figures are NOT produced at
build time. Run

    python scripts/statistics_figures/ora.py
    python scripts/center_figures.py "statistics-ora-*.md" --keep-width
    python scripts/check_figure_labels.py "scripts/_figures/statistics-ora-*.md"

and paste the markup of scripts/_figures/statistics-ora-<name>.md into the
.qmd. Captions are Turkish on purpose (they are shown on the site); aria
labels are plain ASCII.
"""
import io
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, TEXT, THEORY, PRACTICE, BASE, REMARK  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "statistics-ora-"
OUT = {}

MINUS, CHI, SUP2 = "&#8722;", "&#967;", "&#178;"
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


def y_axis(p, ticks, name="", x=None, digits=None):
    X = p.X(p.xmin if x is None else x)
    top, bottom = p.y0 - 10, p.Y(p.ymin)
    p.add(f'<g stroke="{TEXT}" stroke-width="1.1" opacity="0.5" fill="{TEXT}">'
          f'<line x1="{X:.1f}" y1="{bottom:.1f}" x2="{X:.1f}" y2="{top:.1f}"/>'
          f'<polygon points="{X:.1f},{top:.1f} {X-3.5:.1f},{top+8:.1f} {X+3.5:.1f},{top+8:.1f}" stroke="none"/></g>')
    for v in ticks:
        Y = p.Y(v)
        p.add(f'<line x1="{X-3:.1f}" y1="{Y:.1f}" x2="{X+3:.1f}" y2="{Y:.1f}" stroke="{TEXT}" stroke-width="1" opacity="0.7"/>')
        p.add(f'<text x="{X-7:.1f}" y="{Y+4:.1f}" fill="{TEXT}" font-size="{TICK}" text-anchor="end" opacity="0.8">{num(v, digits)}</text>')
    if name:
        p.add(f'<text x="{X+8:.1f}" y="{top+6:.1f}" fill="{TEXT}" font-size="12" font-style="italic" opacity="0.85">{name}</text>')


def npdf(x, mu, s):
    return math.exp(-0.5 * ((x - mu) / s) ** 2) / (s * math.sqrt(2 * math.pi))


def chi2_pdf(x, k):
    if x <= 0:
        return 0.0
    return math.exp((k / 2 - 1) * math.log(x) - x / 2 - (k / 2) * math.log(2) - math.lgamma(k / 2))


def f_pdf(x, a, b):
    if x <= 0:
        return 0.0
    lg = math.lgamma((a + b) / 2) - math.lgamma(a / 2) - math.lgamma(b / 2)
    return math.exp(lg + (a / 2) * math.log(a / b) + (a / 2 - 1) * math.log(x)
                    - ((a + b) / 2) * math.log(1 + a * x / b))


def sampled(fn, a, b, n=SAMPLES):
    return [(a + (b - a) * k / n, fn(a + (b - a) * k / n)) for k in range(n + 1)]


def shade(p, fn, a, b, color, opacity):
    p.polygon([(a, 0)] + sampled(fn, a, b, 200) + [(b, 0)], color, opacity)


def interval_row(p, y, lo, hi, est, color, lo_lab, hi_lab):
    """Horizontal confidence interval with end caps, the estimate as a dot."""
    p.add(f'<line x1="{p.X(lo):.1f}" y1="{p.Y(y):.1f}" x2="{p.X(hi):.1f}" y2="{p.Y(y):.1f}" '
          f'stroke="{color}" stroke-width="3" stroke-linecap="round"/>')
    for v in (lo, hi):
        p.add(f'<line x1="{p.X(v):.1f}" y1="{p.Y(y)-7:.1f}" x2="{p.X(v):.1f}" y2="{p.Y(y)+7:.1f}" '
              f'stroke="{color}" stroke-width="2"/>')
    p.points([(est, y)], color, 4.5)
    if lo_lab:
        p.label(lo, y, lo_lab, 0, 22, color, 11.5, "middle")
    if hi_lab:
        p.label(hi, y, hi_lab, 0, 22, color, 11.5, "middle")


# ============================================================
# phat-dagilimi: distribution of X/n for n = 40, p = 0.3 and its normal approximation
# ============================================================
def fig_phat():
    n, prob = 40, 0.3
    W, H = 560, 270
    p = Plot(50, 34, 470, 190, (0, 0.66), (0, 6.3))
    mu, s = prob, math.sqrt(prob * (1 - prob) / n)
    for k in range(0, 27):
        h = math.comb(n, k) * prob ** k * (1 - prob) ** (n - k) * n    # probability / bar width
        a, b = (k - 0.5) / n, (k + 0.5) / n
        p.polygon([(max(a, 0), 0), (max(a, 0), h), (b, h), (b, 0)], BASE, 0.16, stroke=BASE, width=0.9)
    p.line(sampled(lambda x: npdf(x, mu, s), 0, 0.66), THEORY, 2.2)
    p.vline(prob, 0, 6.0, PRACTICE, "5 3", 0.9)
    p.label(prob, 6.0, f"{it('p')} = 0,3", 0, -6, PRACTICE, LABEL, "middle", bold=True)
    x_axis(p, [(v / 10, num(v / 10)) for v in range(0, 7)], "x/n")
    y_axis(p, (1, 2, 3, 4, 5, 6), "olasılık / genişlik")
    p.label(0.42, npdf(0.42, mu, s), f"{it('N')}(0,3; 0,00525)", 10, -4, THEORY, LABEL, "start", bold=True)
    OUT["phat-dagilimi"] = figure(
        W, H, [p],
        "n = 40 ve p = 0,3 iken p̂ = X/n oranının olasılıkları: k/40 değerinin olasılığı, genişliği 1/40 "
        "olan bir dikdörtgenin alanıdır. Üstteki eğri N(p, pq/n) = N(0,3; 0,00525) yoğunluğudur; "
        "dikdörtgenler eğriyi yakından izler ve p = 0,3 çevresinde toplanır.",
        aria="Probabilities of X over n for n 40 and p 0.3 drawn as bars of width 1/40, with the normal density of mean 0.3 and variance 0.00525")


# ============================================================
# guven-duzeyi: twenty 95% intervals from simulated samples, n = 50, p = 0.4
# ============================================================
COUNTS = [19, 23, 18, 19, 19, 19, 15, 9, 18, 21, 18, 19, 15, 15, 20, 14, 21, 19, 20, 18]


def fig_coverage():
    n, prob, z = 50, 0.4, 1.96
    W, H = 560, 380
    p = Plot(60, 40, 460, 290, (0.05, 0.75), (0.2, 20.8))
    p.vline(prob, 0.3, 20.7, TEXT, "5 3", 0.7)
    p.label(prob, 20.7, f"gerçek {it('p')} = 0,4", 0, -8, TEXT, LABEL, "middle", bold=True)
    missed = 0
    for i, x in enumerate(COUNTS):
        row = 20 - i
        ph = x / n
        e = z * math.sqrt(ph * (1 - ph) / n)
        covers = ph - e < prob < ph + e
        color = THEORY if covers else PRACTICE
        missed += not covers
        p.add(f'<line x1="{p.X(ph - e):.1f}" y1="{p.Y(row):.1f}" x2="{p.X(ph + e):.1f}" y2="{p.Y(row):.1f}" '
              f'stroke="{color}" stroke-width="{2.2 if covers else 3}" stroke-linecap="round"/>')
        p.points([(ph, row)], color, 3.2)
        if not covers:
            p.label(ph + e, row, "p'yi kaçıran aralık", 10, 4, PRACTICE, 12, "start", bold=True)
    assert missed == 1
    x_axis(p, [(v / 10, num(v / 10)) for v in range(1, 8)], "p", y=0.2)
    for row in (1, 5, 10, 15, 20):
        p.text_px(p.x0 - 8, p.Y(21 - row) + 4, str(row), TEXT, TICK, "end")
    p.text_px(p.x0 - 8, p.y0 - 12, "örneklem", TEXT, 12, "middle")
    OUT["guven-duzeyi"] = figure(
        W, H, [p],
        "Aynı kitleden (p = 0,4) alınmış 20 ayrı n = 50 hacimli örneklemden hesaplanan %95'lik güven "
        "aralıkları; noktalar p̂ değerleridir. Aralıklar örneklemden örnekleme değişir, p ise sabittir. "
        "Burada 20 aralığın 19'u p'yi içeriyor; uzun vadede aralıkların yaklaşık %95'i içerir.",
        aria="Twenty 95 percent confidence intervals for p from simulated samples of size 50 with p 0.4; one interval misses p")


# ============================================================
# hata-payi: margin of error 1.96 sqrt(p(1-p)/n) as a function of p
# ============================================================
def fig_margin():
    W, H = 560, 280
    p = Plot(60, 34, 450, 200, (0, 1), (0, 0.112))
    for n, color, lx in ((100, THEORY, 0.5), (400, PRACTICE, 0.5), (1068, BASE, 0.5)):
        fn = lambda x, n=n: 1.96 * math.sqrt(max(x * (1 - x), 0) / n)
        p.line(sampled(fn, 0, 1), color, 2.2)
        p.label(lx, fn(lx), f"{it('n')} = {n}", 0, -7, color, LABEL, "middle", bold=True)
    p.add(f'<line x1="{p.X(0):.1f}" y1="{p.Y(0.03):.1f}" x2="{p.X(1):.1f}" y2="{p.Y(0.03):.1f}" '
          f'stroke="{TEXT}" stroke-width="1" stroke-dasharray="5 3" opacity="0.6"/>')
    p.label(1, 0.03, "0,03", 6, 4, TEXT, 12, "start")
    x_axis(p, [(v / 10, num(v / 10)) for v in range(0, 11)], "p")
    y_axis(p, (0.02, 0.04, 0.06, 0.08, 0.1), "", 0, 2)
    p.text_px(p.x0 + 6, p.y0 - 12, "hata payı", TEXT, 12, "start")
    OUT["hata-payi"] = figure(
        W, H, [p],
        "%95 güven düzeyinde hata payı 1,96·√(p(1 − p)/n), p'nin fonksiyonu olarak. Her n için en büyük "
        "değer p = 1/2'de alınır; n = 1068 iken bu en büyük değer bile 0,03'ün altında kalır.",
        aria="Margin of error 1.96 times sqrt of p(1-p)/n against p for n 100, 400 and 1068, with a dashed line at 0.03")


# ============================================================
# fark-araliklari: two intervals for p1 - p2, one containing 0 and one not
# ============================================================
def fig_differences():
    W, H = 560, 210
    p = Plot(40, 30, 480, 130, (-0.055, 0.095), (0, 3))
    p.vline(0, 0.2, 2.9, TEXT, "5 3", 0.7)
    p.label(0, 2.9, "0", 0, -6, TEXT, LABEL, "middle", bold=True)
    interval_row(p, 2.1, -0.0194, 0.0794, 0.03, THEORY, num(-0.0194), num(0.0794))
    p.label(0.03, 2.1, "iki makine", 0, -12, THEORY, 12, "middle", bold=True)
    interval_row(p, 0.9, -0.0369, -0.0124, -0.0247, PRACTICE, num(-0.0369), num(-0.0124))
    p.label(-0.0247, 0.9, "grip aşısı", 0, -12, PRACTICE, 12, "middle", bold=True)
    x_axis(p, [(v / 100, num(v / 100)) for v in range(-4, 10, 2)], "", y=0)
    p.text_px(p.x0 + p.w + 10, p.Y(0) - 8, f"{it('p')}{sub('1')} {MINUS} {it('p')}{sub('2')}", TEXT, 12, "end")
    OUT["fark-araliklari"] = figure(
        W, H, [p],
        "p₁ − p₂ için iki %95'lik güven aralığı. İki makine örneğindeki aralık 0'ı içerir: verilere göre "
        "kusur oranları eşit olabilir. Grip aşısı örneğindeki aralığın tamamı 0'ın solundadır: aşılananlarda "
        "grip oranı belirgin biçimde daha düşüktür.",
        aria="Two confidence intervals for p1 minus p2 on a common axis; the machine interval contains zero, the flu vaccine interval lies left of zero")


# ============================================================
# ki-kare-kantilleri: chi-square with 7 df, 2.5% tails
# ============================================================
def fig_chi2():
    k, lo, hi = 7, 1.69, 16.01
    W, H = 560, 260
    p = Plot(40, 30, 480, 190, (0, 22), (0, 0.125))
    fn = lambda x: chi2_pdf(x, k)
    shade(p, fn, lo, hi, THEORY, 0.16)
    shade(p, fn, 0, lo, PRACTICE, 0.45)
    shade(p, fn, hi, 22, PRACTICE, 0.45)
    p.line(sampled(fn, 0, 22), THEORY, 2.2)
    for v in (lo, hi):
        p.vline(v, 0, fn(v), PRACTICE, "4 3", 0.9)
    x_axis(p, [(0, "0"), (5, "5"), (10, "10"), (20, "20"), (lo, ""), (hi, "")], it("x"))
    p.label(lo, 0, "1,69", 0, 31, PRACTICE, 12, "middle", bold=True)
    p.label(hi, 0, "16,01", 0, 31, PRACTICE, 12, "middle", bold=True)
    p.label(7.2, 0.045, "0,95", 0, 0, THEORY, LABEL, "middle", bold=True)
    p.add(f'<line x1="{p.X(1.1):.1f}" y1="{p.Y(0.005):.1f}" x2="{p.X(0.9):.1f}" y2="{p.Y(0.07):.1f}" '
          f'stroke="{PRACTICE}" stroke-width="1" opacity="0.8"/>')
    p.label(0.9, 0.07, "0,025", 0, -5, PRACTICE, 12, "middle", bold=True)
    p.add(f'<line x1="{p.X(17.2):.1f}" y1="{p.Y(0.004):.1f}" x2="{p.X(18.2):.1f}" y2="{p.Y(0.03):.1f}" '
          f'stroke="{PRACTICE}" stroke-width="1" opacity="0.8"/>')
    p.label(18.2, 0.03, "0,025", 0, -5, PRACTICE, 12, "middle", bold=True)
    p.label(9.6, fn(9.6), f"{CHI}{SUP2}, 7 serbestlik derecesi", 12, -4, THEORY, LABEL, "start", bold=True)
    OUT["ki-kare-kantilleri"] = figure(
        W, H, [p],
        "7 serbestlik dereceli χ² yoğunluğu. Solunda 0,025 alan bırakan nokta 1,69, solunda 0,975 alan "
        "bırakan nokta 16,01'dir; ikisinin arasında 0,95 alan kalır. Eğri simetrik olmadığından iki nokta "
        "ortalama 7'ye eşit uzaklıkta değildir.",
        aria="Chi-square density with 7 degrees of freedom, tails of area 0.025 below 1.69 and above 16.01 shaded")


# ============================================================
# f-kantilleri: F with (12, 15) df, 5% tails
# ============================================================
def fig_f():
    a, b = 12, 15
    lo, hi = 1 / 2.62, 2.48
    W, H = 560, 260
    p = Plot(40, 30, 480, 190, (0, 4), (0, 0.95))
    fn = lambda x: f_pdf(x, a, b)
    shade(p, fn, lo, hi, THEORY, 0.16)
    shade(p, fn, 0, lo, PRACTICE, 0.45)
    shade(p, fn, hi, 4, PRACTICE, 0.45)
    p.line(sampled(fn, 0, 4), THEORY, 2.2)
    for v in (lo, hi):
        p.vline(v, 0, fn(v), PRACTICE, "4 3", 0.9)
    x_axis(p, [(0, "0"), (1, "1"), (2, "2"), (3, "3"), (4, ""), (lo, ""), (hi, "")], it("x"))
    p.label(lo, 0, "0,382", 0, 31, PRACTICE, 12, "middle", bold=True)
    p.label(hi, 0, "2,48", 0, 31, PRACTICE, 12, "middle", bold=True)
    p.label(1.05, 0.3, "0,90", 0, 0, THEORY, LABEL, "middle", bold=True)
    p.add(f'<line x1="{p.X(0.3):.1f}" y1="{p.Y(0.03):.1f}" x2="{p.X(0.15):.1f}" y2="{p.Y(0.45):.1f}" '
          f'stroke="{PRACTICE}" stroke-width="1" opacity="0.8"/>')
    p.label(0.15, 0.45, "0,05", 0, -5, PRACTICE, 12, "middle", bold=True)
    p.add(f'<line x1="{p.X(2.75):.1f}" y1="{p.Y(0.02):.1f}" x2="{p.X(3.0):.1f}" y2="{p.Y(0.16):.1f}" '
          f'stroke="{PRACTICE}" stroke-width="1" opacity="0.8"/>')
    p.label(3.0, 0.16, "0,05", 0, -5, PRACTICE, 12, "middle", bold=True)
    p.label(1.45, fn(1.45), f"{it('F')}(12, 15)", 12, -4, THEORY, LABEL, "start", bold=True)
    OUT["f-kantilleri"] = figure(
        W, H, [p],
        "(12, 15) serbestlik dereceli F yoğunluğu. Solunda 0,95 alan bırakan nokta 2,48, solunda 0,05 alan "
        "bırakan nokta 1/2,62 ≈ 0,382'dir (2,62, serbestlik dereceleri yer değiştirmiş F(15, 12) dağılımının "
        "0,95 kantilidir); aralarında 0,90 alan kalır.",
        aria="F density with 12 and 15 degrees of freedom, tails of area 0.05 below 0.382 and above 2.48 shaded")


# ============================================================
# lastik-verisi: dot plot of the two tyre samples
# ============================================================
def fig_tyres():
    A = [10, 27, 7, 15, 18, 20, 8]
    B = [14, 12, 16, 14, 15, 13, 17, 11, 16, 12]
    W, H = 560, 220
    p = Plot(90, 20, 430, 150, (5, 29), (0, 4))
    for data, base, color, name in ((A, 2.6, THEORY, "A markası"), (B, 0.6, PRACTICE, "B markası")):
        seen = {}
        for v in data:
            k = seen.get(v, 0)
            seen[v] = k + 1
            p.add(f'<circle cx="{p.X(v):.1f}" cy="{p.Y(base) - 12 * k:.1f}" r="5" fill="{color}" fill-opacity="0.75"/>')
        m = sum(data) / len(data)
        p.add(f'<line x1="{p.X(m):.1f}" y1="{p.Y(base) + 10:.1f}" x2="{p.X(m):.1f}" y2="{p.Y(base) - 34:.1f}" '
              f'stroke="{color}" stroke-width="1.6" stroke-dasharray="4 3"/>')
        p.label(m, base, f"ort. {num(m)}", 0, -40, color, 12, "middle", bold=True)
        p.text_px(p.x0 - 10, p.Y(base) + 4, name, color, 12, "end", bold=True)
    x_axis(p, [(v, num(v)) for v in range(5, 30, 5)], "gün", y=0)
    OUT["lastik-verisi"] = figure(
        W, H, [p],
        "İki lastik markasının dayanma süreleri. Ortalamalar (15 ve 14) birbirine yakın, fakat A markasının "
        "gözlemleri B markasınınkilerden çok daha geniş bir alana yayılmış.",
        aria="Dot plot of the tyre lifetimes of brand A and brand B with their means 15 and 14 marked")


# ============================================================
# ucret-varyans-orani: interval for the variance ratio compared with 1
# ============================================================
def fig_wage_ratio():
    W, H = 560, 170
    p = Plot(40, 30, 480, 90, (0, 4.5), (0, 2))
    p.vline(1, 0.15, 1.9, TEXT, "5 3", 0.7)
    p.label(1, 1.9, "1", 0, -6, TEXT, LABEL, "middle", bold=True)
    interval_row(p, 1.0, 0.340, 4.113, 1.25, THEORY, "0,340", "4,113")
    p.label(1.25, 1.0, "1,25", 0, -12, THEORY, 12, "middle", bold=True)
    x_axis(p, [(v, num(v)) for v in range(0, 5)], "", y=0)
    p.text_px(p.x0 + p.w + 10, p.Y(0) - 8, f"&#963;{sub('1')}{SUP2} / &#963;{sub('2')}{SUP2}", TEXT, 12, "end")
    OUT["ucret-varyans-orani"] = figure(
        W, H, [p],
        "σ₁²/σ₂² oranı (A ve B firmaları) için %90'lık güven aralığı (0,340; 4,113) ve nokta tahmini 1,25. Aralık 1'i "
        "içerdiğinden iki firmanın ücret varyanslarının eşit olması verilerle çelişmez.",
        aria="Confidence interval from 0.340 to 4.113 for the ratio of the two variances, containing 1")


fig_phat()
fig_coverage()
fig_margin()
fig_differences()
fig_chi2()
fig_f()
fig_tyres()
fig_wage_ratio()

for name, content in OUT.items():
    with io.open(OUT_DIR / f"{PREFIX}{name}.md", "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
print(f"generated {len(OUT)} figures:", ", ".join(OUT))
