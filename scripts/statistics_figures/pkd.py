# -*- coding: utf-8 -*-
"""
Figures of the chapter "Poisson ve Kesikli Düzgün Dağılımlar"
(dersler/matematiksel-istatistik/poisson-ve-kesikli-duzgun.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
callout), never inside a definition box. The figures are NOT produced at
build time. Run

    python scripts/statistics_figures/pkd.py
    python scripts/center_figures.py "statistics-pkd-*.md" --keep-width
    python scripts/check_figure_labels.py "scripts/_figures/statistics-pkd-*.md"

and paste the markup of scripts/_figures/statistics-pkd-<name>.md into the .qmd.
The captions are Turkish plain text on purpose (no LaTeX); the aria labels are
plain ASCII.
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
PREFIX = "statistics-pkd-"

LAMBDA, SIGMA, MINUS, LEQ, GEQ, APPROX = "&#955;", "&#963;", "&#8722;", "&#8804;", "&#8805;", "&#8776;"


def save(name, markup):
    (OUT_DIR / f"{PREFIX}{name}.md").write_text(markup, encoding="utf-8", newline="\n")


def comma(v, nd=2):
    """Tick label with a decimal comma: 0.25 -> '0,25'."""
    s = f"{v:.{nd}f}"
    return s.replace(".", ",")


def it(s):
    return f'<tspan font-style="italic">{s}</tspan>'


def sub(s, size=10):
    return f'<tspan font-size="{size}" dy="4">{s}</tspan><tspan dy="-4">&#8203;</tspan>'


def poisson(lam, k):
    return math.exp(-lam) * lam ** k / math.factorial(k)


def binom(n, p, k):
    if k > n:
        return 0.0
    return math.comb(n, k) * p ** k * (1 - p) ** (n - k)


def bars_px(p, pts, color, width, dx=0.0, opacity=0.85):
    """Bars shifted by dx pixels (for grouped bar charts)."""
    for x, y in pts:
        X, Y0, Y1 = p.X(x) + dx, p.Y(0), p.Y(y)
        p.add(f'<rect x="{X - width / 2:.1f}" y="{Y1:.1f}" width="{width}" height="{Y0 - Y1:.1f}" '
              f'fill="{color}" opacity="{opacity}" rx="1"/>')


def swatch(p, px, py, color, text, opacity=0.85, size=12.5):
    """Legend entry at pixel position (px, py): small square and text."""
    p.add(f'<rect x="{px:.1f}" y="{py - 9:.1f}" width="11" height="11" fill="{color}" opacity="{opacity}" rx="1.5"/>')
    p.text_px(px + 17, py + 1, text, size=size)


def dot_swatch(p, px, py, color, text, size=12.5):
    p.add(f'<circle cx="{px + 5.5:.1f}" cy="{py - 3.5:.1f}" r="4" fill="none" stroke="{color}" stroke-width="1.8"/>')
    p.text_px(px + 17, py + 1, text, size=size)


def brace(p, x0, x1, y, color=TEXT, depth=7, opacity=0.8):
    """Horizontal curly brace below data height y (pixel depth), opening upward."""
    X0, X1, Y = p.X(x0), p.X(x1), p.Y(y)
    m = (X0 + X1) / 2
    d = (f"M{X0:.1f},{Y:.1f} Q{X0:.1f},{Y + depth:.1f} {X0 + depth:.1f},{Y + depth:.1f} "
         f"L{m - depth:.1f},{Y + depth:.1f} Q{m:.1f},{Y + depth:.1f} {m:.1f},{Y + 2 * depth:.1f} "
         f"Q{m:.1f},{Y + depth:.1f} {m + depth:.1f},{Y + depth:.1f} "
         f"L{X1 - depth:.1f},{Y + depth:.1f} Q{X1:.1f},{Y + depth:.1f} {X1:.1f},{Y:.1f}")
    p.add(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="1.3" opacity="{opacity}"/>')


def tick(p, x, y, h=5, opacity=0.6):
    p.add(f'<line x1="{p.X(x):.1f}" y1="{p.Y(y) - h:.1f}" x2="{p.X(x):.1f}" y2="{p.Y(y) + h:.1f}" '
          f'stroke="{TEXT}" stroke-width="1.2" opacity="{opacity}"/>')


def event(p, x, y, color=PRACTICE, s=4.5):
    """An event on a time line, drawn as a small x."""
    X, Y = p.X(x), p.Y(y)
    p.add(f'<path d="M{X - s:.1f},{Y - s:.1f} L{X + s:.1f},{Y + s:.1f} M{X - s:.1f},{Y + s:.1f} L{X + s:.1f},{Y - s:.1f}" '
          f'stroke="{color}" stroke-width="2" stroke-linecap="round"/>')


# ============================================================
# Poisson pmf for three values of lambda
# ============================================================
W, H = 600, 300
p = Plot(60, 34, 500, 210, (-0.6, 18.6), (0, 0.40))
p.grid(ys=[0.1, 0.2, 0.3, 0.4])
p.axes(range(0, 19, 2), [0, 0.1, 0.2, 0.3, 0.4], xlabel="x", ylabel="P(X = x)",
       yfmt=lambda v: comma(v, 1))
series = [(1, BASE, -6.5), (4, THEORY, 0.0), (10, PRACTICE, 6.5)]
for lam, color, dx in series:
    bars_px(p, [(k, poisson(lam, k)) for k in range(19)], color, 6, dx)
for i, (lam, color, _) in enumerate(series):
    swatch(p, 420, 60 + 22 * i, color, f"{LAMBDA} = {lam}")
save("pmf", figure(W, H, [p],
                   "Poisson(λ) olasılık fonksiyonu λ = 1, 4 ve 10 için. Olasılıklar λ çevresinde toplanır; "
                   "λ büyüdükçe dağılım sağa kayar, yayılır (standart sapma √λ) ve simetriye yaklaşır.",
                   aria="Bar charts of the Poisson probability function for lambda 1, 4 and 10"))

# ============================================================
# splitting (0, t] into n pieces of length t/n
# ============================================================
W, H = 640, 190
p = Plot(40, 40, 560, 110, (0, 12), (0, 1))
y = 0.55
p.line([(0, y), (12.25, y)], color=TEXT, width=1.3, opacity=0.6)
p.add(f'<polygon points="{p.X(12.25) + 8:.1f},{p.Y(y):.1f} {p.X(12.25):.1f},{p.Y(y) - 3.5:.1f} '
      f'{p.X(12.25):.1f},{p.Y(y) + 3.5:.1f}" fill="{TEXT}" opacity="0.6"/>')
for k in range(13):
    tick(p, k, y)
hits = {1: 1.45, 4: 4.6, 5: 5.3, 9: 9.55}
for k in range(12):
    if k in hits:
        event(p, hits[k], y)
        p.polygon([(k, y - 0.09), (k + 1, y - 0.09), (k + 1, y + 0.09), (k, y + 0.09)],
                  fill=PRACTICE, opacity=0.12)
    p.label(k + 0.5, y, "1" if k in hits else "0", dy=-14, anchor="middle", size=12.5,
            color=PRACTICE if k in hits else TEXT)
p.label(0, y, "0", dy=24, anchor="middle", size=13)
p.label(12, y, it("t"), dy=24, anchor="middle", size=13)
brace(p, 2, 3, y - 0.2)
p.label(2.5, y - 0.2, "&#916;" + it("t") + " = " + it("t") + "/" + it("n"), dy=32, anchor="middle", size=12.5)
p.label(8.2, y - 0.2, it("n") + " parça, her parça bir Bernoulli denemesi", dy=32, anchor="middle", size=12.5)
save("bolme", figure(W, H, [p],
                     "(0, t] aralığı uzunluğu Δt = t/n olan n parçaya bölünür. Her parçada en fazla bir başarı olur "
                     "(üstteki 1 ya da 0); parçalar bağımsızdır. Toplam başarı sayısı Binom(n, λt/n) dağılımına uyar.",
                     css_class=WIDE,
                     aria="Time interval from 0 to t split into n pieces, each piece a Bernoulli trial"))

# ============================================================
# increments of the counting process
# ============================================================
W, H = 600, 200
p = Plot(40, 44, 520, 110, (0, 5.4), (0, 1))
y = 0.6
p.line([(0, y), (5.4, y)], color=TEXT, width=1.3, opacity=0.6)
p.add(f'<polygon points="{p.X(5.4) + 8:.1f},{p.Y(y):.1f} {p.X(5.4):.1f},{p.Y(y) - 3.5:.1f} '
      f'{p.X(5.4):.1f},{p.Y(y) + 3.5:.1f}" fill="{TEXT}" opacity="0.6"/>')
for k in range(6):
    tick(p, k, y, h=4)
    p.label(k, y, str(k), dy=20, anchor="middle", size=12)
p.polygon([(0, y - 0.1), (2, y - 0.1), (2, y + 0.1), (0, y + 0.1)], fill=THEORY, opacity=0.14)
p.polygon([(2, y - 0.1), (5, y - 0.1), (5, y + 0.1), (2, y + 0.1)], fill=PRACTICE, opacity=0.14)
for x in (0.35, 0.9, 1.6):
    event(p, x, y, color=THEORY)
for x in (2.45, 3.1, 3.5, 4.4):
    event(p, x, y, color=PRACTICE)
p.label(1.0, y + 0.1, it("Z") + sub("2") + " = 3", dy=-12, anchor="middle", size=13, color=THEORY)
p.label(3.5, y + 0.1, it("Z") + sub("5") + " " + MINUS + " " + it("Z") + sub("2") + " = 4",
        dy=-12, anchor="middle", size=13, color=PRACTICE)
brace(p, 0, 5, y - 0.3)
p.label(2.5, y - 0.3, it("Z") + sub("5") + " = 7", dy=34, anchor="middle", size=13)
save("artis", figure(W, H, [p],
                     "(0, 2] aralığında 3, (2, 5] aralığında 4 olay: toplamda Z₅ = 7. Ayrık iki aralıktaki sayılar "
                     "bağımsızdır, ama Z₂ ile Z₅ ortak bir parçayı paylaştıkları için bağımsız değildir.",
                     aria="Time line from 0 to 5 with three events in the first two units and four in the next three"))

# ============================================================
# traffic accidents: Poisson(10), the event X < 2 sits in the far left tail
# ============================================================
W, H = 600, 290
p = Plot(60, 34, 500, 200, (-0.8, 24.8), (0, 0.14))
p.grid(ys=[0.02 * k for k in range(1, 8)])
p.axes(range(0, 25, 2), [0, 0.04, 0.08, 0.12], xlabel="x", ylabel="P(X = x)",
       yfmt=lambda v: comma(v, 2))
p.polygon([(-0.5, 0), (1.5, 0), (1.5, 0.14), (-0.5, 0.14)], fill=PRACTICE, opacity=0.10)
p.bars([(k, poisson(10, k)) for k in range(2, 25)], color=THEORY, width=10)
p.bars([(k, poisson(10, k)) for k in range(0, 2)], color=PRACTICE, width=10, opacity=1.0)
p.arrow((2.9, 0.088), (1.0, 0.02), color=PRACTICE, width=1.4, head=7)
p.label(2.2, 0.112, "P(X &lt; 2)", size=12.5, color=PRACTICE)
p.label(2.2, 0.112, APPROX + " 0,0005", dy=17, size=12.5, color=PRACTICE)
p.label(17.5, 0.118, "Poisson(10)", anchor="middle", size=13, color=THEORY)
save("trafik", figure(W, H, [p],
                     "Bir gündeki kaza sayısı Poisson(10): olasılıklar 10 çevresinde toplanır. 0 ve 1 değerlerinin "
                     "(taralı bant) çubukları görülemeyecek kadar kısadır.",
                     aria="Poisson 10 probability function with the values 0 and 1 in a shaded band"))

# ============================================================
# defective items: Binom(20000, 1/10000) against Poisson(2)
# ============================================================
W, H = 600, 290
n, pp = 20000, 1 / 10000
p = Plot(60, 34, 500, 200, (-0.6, 10.6), (0, 0.30))
p.grid(ys=[0.05 * k for k in range(1, 7)])
p.axes(range(0, 11), [0, 0.1, 0.2, 0.3], xlabel="x", ylabel="P(X = x)", yfmt=lambda v: comma(v, 1))
p.polygon([(5.5, 0), (10.6, 0), (10.6, 0.30), (5.5, 0.30)], fill=PRACTICE, opacity=0.10)
bars_px(p, [(k, binom(n, pp, k)) for k in range(11)], BASE, 9, -5.5)
bars_px(p, [(k, poisson(2, k)) for k in range(11)], THEORY, 9, 5.5)
swatch(p, 380, 58, BASE, "Binom(20000; 0,0001)")
swatch(p, 380, 80, THEORY, "Poisson(2)")
p.label(8.05, 0.155, "X " + GEQ + " 6", anchor="middle", size=13, color=PRACTICE)
p.label(8.05, 0.155, APPROX + " 0,0166", dy=18, anchor="middle", size=12.5, color=PRACTICE)
save("kusurlu", figure(W, H, [p],
                       "Kusurlu ürün sayısı: Binom(20000; 0,0001) ve Poisson(2) olasılıkları yan yana. Çubuklar gözle "
                       "ayırt edilemez; taralı bölge istenen X ≥ 6 olayıdır.",
                       aria="Binomial 20000 0.0001 and Poisson 2 probabilities side by side"))

# ============================================================
# Binom(n, 2/n) approaches Poisson(2)
# ============================================================
W, H = 720, 260
panels = []
for i, nn in enumerate((4, 10, 40)):
    q = Plot(56 + i * 225, 44, 180, 160, (-0.6, 7.6), (0, 0.40))
    q.grid(ys=[0.1, 0.2, 0.3, 0.4])
    q.axes(range(0, 8), [0, 0.1, 0.2, 0.3, 0.4] if i == 0 else [], xlabel="x" if i == 2 else "",
           yfmt=lambda v: comma(v, 1))
    q.bars([(k, binom(nn, 2 / nn, k)) for k in range(8)], color=BASE, width=11)
    q.hollow_points([(k, poisson(2, k)) for k in range(8)], color=THEORY, r=3.6)
    q.text_px(q.x0 + q.w / 2, q.y0 - 16, it("n") + f" = {nn}", size=13, anchor="middle")
    panels.append(q)
leg = panels[2]
swatch(leg, leg.x0 + 70, leg.y0 + 18, BASE, "Binom(" + it("n") + ", 2/" + it("n") + ")", size=12)
dot_swatch(leg, leg.x0 + 70, leg.y0 + 40, THEORY, "Poisson(2)", size=12)
save("yakinsama", figure(W, H, panels,
                         "np = 2 sabit tutulup n büyütüldüğünde Binom(n, 2/n) olasılıkları (çubuklar) Poisson(2) "
                         "olasılıklarına (halkalar) yaklaşır; n = 40 için fark neredeyse görünmez.",
                         css_class=WIDE,
                         aria="Three panels: binomial n 2 over n bars for n 4, 10, 40 and Poisson 2 values as rings"))

# ============================================================
# a fair die: discrete uniform on 1..6
# ============================================================
W, H = 600, 280
s = math.sqrt(35 / 12)
p = Plot(60, 40, 500, 180, (0.3, 6.7), (0, 0.24))
p.grid(ys=[0.05, 0.10, 0.15, 0.20])
p.axes(range(1, 7), [0, 0.05, 0.1, 0.15, 0.2], xlabel="x", ylabel="P(X = x)", yfmt=lambda v: comma(v, 2))
p.polygon([(3.5 - s, 0), (3.5 + s, 0), (3.5 + s, 0.235), (3.5 - s, 0.235)], fill=REMARK, opacity=0.10)
p.bars([(k, 1 / 6) for k in range(1, 7)], color=THEORY, width=26)
p.vline(3.5, 0, 0.235, color=PRACTICE, dash="5 3", opacity=0.9)
p.label(3.5, 0.235, "E(X) = 3,5", dy=-6, anchor="middle", size=13, color=PRACTICE)
p.label(3.5 - s, 0.208, "3,5 " + MINUS + " " + SIGMA, dx=-5, anchor="end", size=12.5, color=REMARK)
p.label(3.5 + s, 0.208, "3,5 + " + SIGMA, dx=5, size=12.5, color=REMARK)
p.label(6.0, 1 / 6, "1/6", dx=18, dy=4, size=12.5)
save("zar", figure(W, H, [p],
                   "Zarın olasılık fonksiyonu: altı eşit çubuk. Beklenen değer 3,5 tam ortadadır; taralı bant "
                   "bir standart sapma (σ = √(35/12) ≈ 1,71) genişliğindedir.",
                   aria="Six equal bars of height one sixth with the mean 3.5 and a one sigma band"))

# ============================================================
# unequally spaced values: the mean as balance point
# ============================================================
W, H = 600, 270
xs = [1, 2, 4, 8, 10]
p = Plot(50, 40, 500, 210, (0, 11), (0, 0.34))
p.grid(ys=[0.05, 0.10, 0.15, 0.20])
p.axes(range(0, 12), [0, 0.1, 0.2], xlabel="x", ylabel="P(X = x)", yfmt=lambda v: comma(v, 1))
p.bars([(x, 0.2) for x in xs], color=THEORY, width=14)
p.vline(5, 0, 0.31, color=PRACTICE, dash="5 3", opacity=0.9)
p.label(5, 0.31, "E(X) = 5", dy=-6, anchor="middle", size=13, color=PRACTICE)
for x, yy in ((4, 0.22), (8, 0.24), (2, 0.26), (10, 0.28), (1, 0.30)):
    p.arrow((5, yy), (x, yy), color=REMARK, width=1.3, head=6)
    d = x - 5
    txt = ("+" if d > 0 else MINUS) + str(abs(d))
    if d > 0:
        p.label(x, yy, txt, dx=6, dy=4, size=12.5, color=REMARK)
    else:
        p.label(x, yy, txt, dx=-6, dy=4, anchor="end", size=12.5, color=REMARK)
save("denge", figure(W, H, [p],
                     "{1, 2, 4, 8, 10} üzerinde kesikli düzgün dağılım. Beklenen değer 5, eşit ağırlıkların denge "
                     "noktasıdır: oklar sapmaları gösterir ve −4 − 3 − 1 + 3 + 5 = 0. Varyans, sapma karelerinin ortalamasıdır.",
                     aria="Five equal bars at 1, 2, 4, 8, 10 balanced at the mean 5 with deviation arrows"))

print("ok")
