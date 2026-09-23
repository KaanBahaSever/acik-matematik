# -*- coding: utf-8 -*-
"""
Figures of the chapter "Bernoulli, Binom ve Çok Terimli Dağılımlar"
(dersler/matematiksel-istatistik/bernoulli-binom-ve-cok-terimli.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
callout), never inside a definition box. The figures are NOT produced at
build time. Run

    python scripts/statistics_figures/bbc.py
    python scripts/center_figures.py "statistics-bbc-*.md" --keep-width
    python scripts/check_figure_labels.py "scripts/_figures/statistics-bbc-*.md"

and paste the markup of scripts/_figures/statistics-bbc-<name>.md into the .qmd.
The captions are Turkish plain text on purpose (no LaTeX); the aria labels are
plain ASCII.
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, WIDE, TEXT, THEORY, PRACTICE, BASE, REMARK, panel_title  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "statistics-bbc-"

MINUS, LEQ, GEQ, APPROX = "&#8722;", "&#8804;", "&#8805;", "&#8776;"
S1, S2, S3 = (f'<tspan font-size="10" dy="4">{d}</tspan><tspan dy="-4">&#8203;</tspan>' for d in "123")


def save(name, markup):
    (OUT_DIR / f"{PREFIX}{name}.md").write_text(markup, encoding="utf-8", newline="\n")


def comma(v, nd=2):
    """Number with a decimal comma: 0.25 -> '0,25'."""
    return f"{v:.{nd}f}".replace(".", ",")


def it(s):
    return f'<tspan font-style="italic">{s}</tspan>'


def binom(n, p, k):
    return math.comb(n, k) * p ** k * (1 - p) ** (n - k)


def bar(p, x, y, color, width, opacity=0.85):
    X, Y0, Y1 = p.X(x), p.Y(0), p.Y(y)
    p.add(f'<rect x="{X - width / 2:.1f}" y="{Y1:.1f}" width="{width}" height="{max(Y0 - Y1, 0.8):.1f}" '
          f'fill="{color}" opacity="{opacity}" rx="1.5"/>')


def swatch(p, px, py, color, text, opacity=0.85, size=12.5):
    p.add(f'<rect x="{px:.1f}" y="{py - 9:.1f}" width="11" height="11" fill="{color}" opacity="{opacity}" rx="1.5"/>')
    p.text_px(px + 17, py + 1, text, size=size)


PX = it("X")
PMF_LABEL = "P(" + PX + " = " + it("x") + ")"


# ============================================================
# binom-bicim: Binom(10, p) for p = 0.2, 0.5, 0.8
# ============================================================
W, H = 700, 250
panels = []
for i, (pp, title) in enumerate([(0.2, "sağa çarpık"), (0.5, "simetrik"), (0.8, "sola çarpık")]):
    q = Plot(52 + i * 222, 44, 188, 160, (-0.7, 10.7), (0, 0.40))
    q.grid(ys=[0.1, 0.2, 0.3])
    q.axes(range(0, 11, 2), [0, 0.1, 0.2, 0.3] if i == 0 else [], xlabel="", ylabel="",
           yfmt=lambda v: comma(v, 1))
    for k in range(11):
        bar(q, k, binom(10, pp, k), THEORY, 10)
    m = 10 * pp
    q.vline(m, 0, 0.345, PRACTICE, "4 3", 0.9)
    q.label(m, 0.345, "E(" + PX + ") = " + f"{m:g}", 0, -5, PRACTICE, 12, "middle", True)
    panel_title(q, it("p") + " = " + comma(pp, 1) + " (" + title + ")", TEXT, 12.5)
    q.text_px(q.x0 + q.w / 2, q.y0 + q.h + 34, it("x"), TEXT, 12, "middle")
    panels.append(q)
save("binom-bicim", figure(
    W, H, panels,
    "Binom(10, p) olasılık fonksiyonu p = 0,2, 0,5 ve 0,8 için. Olasılıklar beklenen değer np çevresinde "
    "toplanır. p = 0,5 iken çubuklar 5'e göre simetriktir; p = 0,2 ile p = 0,8 birbirinin aynadaki görüntüsüdür.",
    WIDE, aria="Three binomial pmfs with n 10 and p 0.2, 0.5, 0.8, each with its mean marked"))


# ============================================================
# uc-atis: Binom(3, 1/2), P(X > 1)
# ============================================================
W, H = 560, 300
q = Plot(80, 50, 420, 200, (-0.6, 3.6), (0, 0.5))
q.grid(ys=[0.125, 0.25, 0.375])
q.axes(range(4), [0, 0.125, 0.25, 0.375], xlabel=it("x"), ylabel=PMF_LABEL,
       yfmt=lambda v: {0: "0", 0.125: "1/8", 0.25: "2/8", 0.375: "3/8"}[v])
vals = [1 / 8, 3 / 8, 3 / 8, 1 / 8]
txt = ["1/8", "3/8", "3/8", "1/8"]
for k in range(4):
    col = PRACTICE if k > 1 else THEORY
    bar(q, k, vals[k], col, 44, 0.85 if k > 1 else 0.4)
    q.label(k, vals[k], txt[k], 0, -8, col, 13, "middle", True)
q.text_px(q.X(2.5), q.y0 - 16, "P(" + PX + " &gt; 1) = 3/8 + 1/8 = 1/2", PRACTICE, 13, "middle", True)
save("uc-atis", figure(
    W, H, [q],
    "Düzgün bir paranın üç atışında tura sayısı X, Binom(3, 1/2) dağılımlıdır. "
    "X &gt; 1 olayına x = 2 ve x = 3 çubukları karşılık gelir; olasılığı bu iki çubuğun toplamıdır.",
    aria="Binomial pmf with n 3 and p one half, bars at 2 and 3 highlighted, total one half"))


# ============================================================
# test-kuyruk: Binom(20, 1/5), P(X >= 10)
# ============================================================
W, H = 580, 300
q = Plot(70, 40, 460, 210, (-0.7, 20.7), (0, 0.27))
q.grid(ys=[0.05, 0.1, 0.15, 0.2])
q.axes(range(0, 21, 5), [0, 0.05, 0.1, 0.15, 0.2], xlabel=it("x"), ylabel=PMF_LABEL,
       yfmt=lambda v: comma(v, 2))
for k in range(21):
    bar(q, k, binom(20, 0.2, k), PRACTICE if k >= 10 else THEORY, 11, 0.9 if k >= 10 else 0.6)
q.polygon([(9.5, 0), (20.5, 0), (20.5, 0.03), (9.5, 0.03)], PRACTICE, 0.10, PRACTICE, 1.0, "4 3")
q.vline(4, 0, 0.255, BASE, "4 3", 0.9)
q.label(4, 0.255, "E(" + PX + ") = 4", 6, 4, BASE, 12.5, "start", True)
q.label(15, 0.03, "P(" + PX + " " + GEQ + " 10) " + APPROX + " 0,0026", 0, -14, PRACTICE, 13, "middle", True)
save("test-kuyruk", figure(
    W, H, [q],
    "Rastgele işaretlenen 20 soruluk testte doğru sayısı X, Binom(20, 1/5) dağılımlıdır. "
    "Olasılıkların neredeyse tamamı 0 ile 8 arasındadır; x ≥ 10 çubukları (kesikli çerçeve) çizimde "
    "ancak seçilebilecek kadar kısadır ve toplamları yaklaşık 0,0026'dır.",
    aria="Binomial pmf with n 20 and p 0.2; the tail from 10 on is framed and almost invisible"))


# ============================================================
# fark-dagilimi: X ~ Binom(5, 1/2) and D = |2X - 5|
# ============================================================
W, H = 700, 290
group = {5: REMARK, 3: PRACTICE, 1: THEORY}
L = Plot(60, 50, 300, 190, (-0.7, 5.7), (0, 0.7))
L.grid(ys=[0.2, 0.4, 0.6])
L.axes(range(6), [0, 0.2, 0.4, 0.6], xlabel=it("x"), ylabel="", yfmt=lambda v: comma(v, 1))
for k in range(6):
    d = abs(2 * k - 5)
    pr = binom(5, 0.5, k)
    bar(L, k, pr, group[d], 26)
    L.label(k, pr, f"{math.comb(5, k)}/32", 0, -7, TEXT, 11.5, "middle")
panel_title(L, PX + " (yazı sayısı)", TEXT, 12.5)
R = Plot(470, 50, 190, 190, (-0.2, 6.2), (0, 0.7))
R.grid(ys=[0.2, 0.4, 0.6])
R.axes([1, 3, 5], [], xlabel=it("d"), ylabel="")
for d, pr, t in [(1, 20 / 32, "20/32"), (3, 10 / 32, "10/32"), (5, 2 / 32, "2/32")]:
    bar(R, d, pr, group[d], 30)
    R.label(d, pr, t, 0, -7, TEXT, 11.5, "middle")
R.vline(15 / 8, 0, 0.5, BASE, "4 3", 0.9)
R.label(15 / 8, 0.5, "E(" + it("D") + ") = 15/8", 5, -4, BASE, 12.5, "start", True)
panel_title(R, it("D") + " = |2" + PX + " " + MINUS + " 5|", TEXT, 12.5)
R.arrow((-3.2, 0.36), (-0.9, 0.36), BASE, 1.8, 9)
R.text_px(R.X(-2.05), R.Y(0.36) - 10, "birleştir", BASE, 12, "middle")
save("fark-dagilimi", figure(
    W, H, [L, R],
    "Hilesiz para beş kez atılıyor; X yazı sayısı, D = |2X − 5| yazı ile tura sayıları arasındaki farkın mutlak "
    "değeridir. Aynı renkteki iki çubuk D'nin aynı değerini verir (x ile 5 − x); bunlar birleşince sağdaki "
    "dağılım çıkar ve beklenen değer 15/8 olur.",
    WIDE, aria="Left binomial pmf with n 5 colored in three pairs, right the pmf of the absolute difference with mean 15 over 8"))


# ============================================================
# kirmizi-top: Binom(3, 1/5)
# ============================================================
W, H = 560, 290
q = Plot(80, 40, 420, 200, (-0.6, 3.6), (0, 0.6))
q.grid(ys=[0.1, 0.2, 0.3, 0.4, 0.5])
q.axes(range(4), [0, 0.1, 0.2, 0.3, 0.4, 0.5], xlabel=it("x"), ylabel=PMF_LABEL, yfmt=lambda v: comma(v, 1))
for k, t in zip(range(4), ["0,512", "0,384", "0,096", "0,008"]):
    pr = binom(3, 0.2, k)
    bar(q, k, pr, THEORY, 44)
    q.label(k, pr, t, 0, -8, TEXT, 13, "middle", True)
save("kirmizi-top", figure(
    W, H, [q],
    "Üç iadeli çekilişte kırmızı top sayısı X, Binom(3, 1/5) dağılımlıdır. Başarı olasılığı küçük olduğundan "
    "olasılıklar x = 0 tarafında yığılır ve her adımda hızla küçülür.",
    aria="Binomial pmf with n 3 and p 0.2: 0.512, 0.384, 0.096, 0.008"))


# ============================================================
# cok-terimli-marjinal: trinomial n = 5, p = (1/5, 2/5, 2/5), column sums
# ============================================================
W, H = 560, 560
P3 = (0.2, 0.4, 0.4)


def tri(a, b):
    c = 5 - a - b
    return (math.factorial(5) / (math.factorial(a) * math.factorial(b) * math.factorial(c))
            * P3[0] ** a * P3[1] ** b * P3[2] ** c)


pmax = max(tri(a, b) for a in range(6) for b in range(6 - a))
T = Plot(90, 40, 400, 290, (-0.6, 5.6), (-0.6, 5.6))
T.grid(xs=range(6), ys=range(6))
T.axes(range(6), range(6), xlabel=it("x") + S1, ylabel=it("x") + S2)
for a in range(6):
    for b in range(6 - a):
        r = 17 * math.sqrt(tri(a, b) / pmax)
        T.add(f'<circle cx="{T.X(a):.1f}" cy="{T.Y(b):.1f}" r="{max(r, 1.6):.1f}" fill="{THEORY}" '
              f'fill-opacity="0.55" stroke="{THEORY}" stroke-width="1"/>')
T.label(3.4, 4.6, it("x") + S3 + " = 5 " + MINUS + " " + it("x") + S1 + " " + MINUS + " " + it("x") + S2,
        0, 0, TEXT, 13, "middle")
T.label(3.4, 4.6, "alan olasılıkla orantılı", 0, 20, BASE, 12, "middle")
B = Plot(90, 380, 400, 140, (-0.6, 5.6), (0, 0.5))
B.grid(ys=[0.1, 0.2, 0.3, 0.4])
B.axes(range(6), [0, 0.2, 0.4], xlabel=it("x") + S1, ylabel="", yfmt=lambda v: comma(v, 1))
for a in range(6):
    s = sum(tri(a, b) for b in range(6 - a))
    bar(B, a, s, PRACTICE, 30)
    B.label(a, s, comma(s, 4), 0, -7, TEXT, 11.5, "middle")
B.text_px(B.x0 + B.w + 12, B.y0 + 30, "sütun", PRACTICE, 12, "start", True)
B.text_px(B.x0 + B.w + 12, B.y0 + 46, "toplamları", PRACTICE, 12, "start", True)
save("cok-terimli-marjinal", figure(
    W, H, [T, B],
    "Beş iadeli çekilişte kırmızı (p₁ = 1/5), beyaz (p₂ = 2/5) ve öteki renkler (p₃ = 2/5) için çok terimli "
    "olasılıklar: (x₁, x₂) noktasındaki dairenin alanı P(X₁ = x₁, X₂ = x₂) ile orantılıdır. Her sütun "
    "toplandığında alttaki çubuklar, yani Binom(5, 1/5) olasılıkları çıkar.",
    aria="Trinomial probabilities on a triangular grid drawn as disks, and below their column sums forming a binomial pmf"))

print("wrote", len(list(OUT_DIR.glob(PREFIX + "*.md"))), "figures")
