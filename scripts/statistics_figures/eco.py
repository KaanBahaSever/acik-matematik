# -*- coding: utf-8 -*-
"""
Figures of the chapter "En Çok Olabilirlik Yöntemi"
(dersler/matematiksel-istatistik/en-cok-olabilirlik-yontemi.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box: a figure that illustrates a
definition sits directly below that box. The figures are NOT produced at
build time. Run

    python scripts/statistics_figures/eco.py
    python scripts/center_figures.py "statistics-eco-*.md" --keep-width
    python scripts/check_figure_labels.py "scripts/_figures/statistics-eco-*.md"

and paste the markup of scripts/_figures/statistics-eco-<name>.md into the
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
PREFIX = "statistics-eco-"
OUT = {}

MINUS, APPROX = "&#8722;", "&#8776;"
LAMBDA, THETA, MU, SIGMA = "&#955;", "&#952;", "&#956;", "&#963;"
LABEL = 13     # names of curves and points
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


def hat(s):
    """Italic letter with a combining circumflex (theta hat, p hat)."""
    return f'<tspan font-style="italic">{s}&#770;</tspan>'


def sup(s):
    return f'<tspan font-size="10" dy="-5">{s}</tspan><tspan dy="5">&#8203;</tspan>'


# ---------------------------------------------------------------------------
# drawing helpers (same conventions as the other statistics figure scripts)
# ---------------------------------------------------------------------------
def sample(f, a, b, n=SAMPLES):
    return [(a + (b - a) * k / n, f(a + (b - a) * k / n)) for k in range(n + 1)]


def curve(p, f, a, b, color=THEORY, width=2.2, dash=None, n=SAMPLES):
    """Plot f on [a, b]; pieces outside the panel's y range are dropped."""
    run = []
    for x, y in sample(f, a, b, n):
        if p.ymin <= y <= p.ymax:
            run.append((x, y))
        else:
            if len(run) > 1:
                p.line(run, color, width, dash)
            run = []
    if len(run) > 1:
        p.line(run, color, width, dash)


def x_axis(p, ticks, name="", at=None):
    """Horizontal axis with an arrow head; ticks are (value, label) pairs."""
    Y = p.Y(p.ymin if at is None else at)
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
    top, bottom = p.y0 - 10, p.Y(p.ymin)
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
    """Legend at pixel (px, py) = top-left; entries are (color, dash, text)."""
    for k, (color, dash, s) in enumerate(entries):
        y = py + k * row
        da = f' stroke-dasharray="{dash}"' if dash else ""
        p.add(f'<line x1="{px:.1f}" y1="{y:.1f}" x2="{px+24:.1f}" y2="{y:.1f}" stroke="{color}" stroke-width="2.4"{da} stroke-linecap="round"/>')
        p.text_px(px + 31, y + 4.5, s, TEXT, size)


def title(p, s, size=12.5):
    p.text_px(p.x0 + p.w / 2, p.y0 - 16, s, TEXT, size, "middle", True)


def emit(name, W, H, panels, caption, css_class="ders-grafik", aria=""):
    OUT[name] = figure(W, H, panels, caption, css_class, aria)


def poisson_pmf(x, lam):
    return math.exp(-lam) * lam ** x / math.factorial(x)


def normal_pdf(x, mu, s):
    return math.exp(-0.5 * ((x - mu) / s) ** 2) / (s * math.sqrt(2 * math.pi))


# ============================================================
# iki-bakis: the same Poisson formula read in x and in lambda
# ============================================================
def fig_two_views():
    p1 = Plot(58, 48, 270, 200, (-0.6, 8.6), (0, 0.3))
    bars = [(x, poisson_pmf(x, 2)) for x in range(9)]
    p1.bars([b for b in bars if b[0] != 2], THEORY, 14, 0.75)
    p1.bars([(2, poisson_pmf(2, 2))], PRACTICE, 14, 0.95)
    x_axis(p1, [(x, str(x)) for x in range(9)], it("x"))
    y_axis(p1, ticks([0.1, 0.2, 0.3], 1), it("f") + "(" + it("x") + "; 2)")
    title(p1, LAMBDA + " = 2 sabit, " + it("x") + " değişiyor")
    p1.label(2, poisson_pmf(2, 2), num(poisson_pmf(2, 2), 4), 10, -6, PRACTICE, LABEL)

    L = lambda lam: lam ** 2 * math.exp(-lam) / 2
    p2 = Plot(420, 48, 270, 200, (0, 8), (0, 0.3))
    curve(p2, L, 0, 8, THEORY, 2.2)
    p2.vline(2, 0, L(2), PRACTICE, "4 3", 0.9)
    p2.points([(2, L(2))], PRACTICE, 4.5)
    p2.label(2, L(2), num(L(2), 4), 10, -8, PRACTICE, LABEL)
    p2.label(4.6, 0.19, it("L") + "(" + LAMBDA + ") = " + LAMBDA + sup("2") + it("e") + sup(MINUS + LAMBDA) + "/2",
             0, 0, THEORY, LABEL)
    x_axis(p2, ticks([0, 2, 4, 6, 8]), LAMBDA)
    y_axis(p2, ticks([0.1, 0.2, 0.3], 1), it("L") + "(" + LAMBDA + ")")
    title(p2, it("x") + " = 2 sabit, " + LAMBDA + " değişiyor")
    emit("iki-bakis", 740, 290, [p1, p2],
         "Aynı formül, iki bakış. Solda λ = 2 sabitken x'e göre Poisson olasılıkları; çubukların toplamı 1'dir. "
         "Sağda gözlem x = 2 sabitken λ'ya göre olabilirlik fonksiyonu; en büyük değerini λ = 2'de alır. "
         "Vurgulu çubuk ile vurgulu nokta aynı sayıdır: f(2; 2) = L(2) ≈ 0,2707.",
         WIDE, aria="Left: Poisson probabilities for lambda 2 as bars. Right: likelihood of lambda for the single observation 2, maximal at 2")


# ============================================================
# poisson-olabilirlik: L and ln L for the sample 2, 4, 3, 1, 5, 3
# ============================================================
def fig_poisson_likelihood():
    data = [2, 4, 3, 1, 5, 3]
    n, s = len(data), sum(data)
    c = sum(math.log(math.factorial(x)) for x in data)
    lnL = lambda lam: -n * lam + s * math.log(lam) - c
    L5 = lambda lam: math.exp(lnL(lam)) * 1e5

    p1 = Plot(58, 48, 270, 200, (0, 8), (0, 3.2))
    curve(p1, L5, 0.01, 8, THEORY, 2.2)
    p1.vline(3, 0, L5(3), PRACTICE, "4 3", 0.9)
    p1.points([(3, L5(3))], PRACTICE, 4.5)
    p1.label(3, L5(3), hat(LAMBDA) + " = 3", 10, -6, PRACTICE, LABEL)
    x_axis(p1, ticks([0, 2, 3, 4, 6, 8]), LAMBDA)
    y_axis(p1, ticks([1, 2, 3]), it("L") + "(" + LAMBDA + ") · 10" + sup("5"))
    title(p1, "Olabilirlik")

    p2 = Plot(420, 48, 270, 200, (0.5, 8), (-24, -8))
    curve(p2, lnL, 0.5, 8, THEORY, 2.2)
    p2.vline(3, -24, lnL(3), PRACTICE, "4 3", 0.9)
    p2.points([(3, lnL(3))], PRACTICE, 4.5)
    p2.label(3, lnL(3), hat(LAMBDA) + " = 3", 10, -8, PRACTICE, LABEL)
    x_axis(p2, [(v, num(v)) for v in (1, 2, 3, 4, 6, 8)], LAMBDA)
    y_axis(p2, ticks([-24, -20, -16, -12, -8]), "ln " + it("L") + "(" + LAMBDA + ")", x=0.5)
    title(p2, "Log-olabilirlik")
    emit("poisson-olabilirlik", 740, 290, [p1, p2],
         "Örneklem 2, 4, 3, 1, 5, 3 için Poisson olabilirliği (solda) ve logaritması (sağda). "
         "L(λ) çok küçük sayılardan oluşur (en büyük değeri yaklaşık 2,85 · 10⁻⁵), ln L ise rahat okunur; "
         "ikisi de en büyük değerini aynı noktada, λ = x̄ = 3'te alır.",
         WIDE, aria="Poisson likelihood and log likelihood of the sample 2 4 3 1 5 3, both maximal at lambda 3")


# ============================================================
# bernoulli-olabilirlik: L(p) = p^3 (1 - p)^2
# ============================================================
def fig_bernoulli_likelihood():
    L = lambda q: q ** 3 * (1 - q) ** 2
    p = Plot(70, 36, 450, 220, (0, 1), (0, 0.04))
    curve(p, L, 0, 1, THEORY, 2.2)
    for q in (0.2, 0.5, 0.8):
        p.vline(q, 0, L(q), BASE, "3 3", 0.8)
        p.points([(q, L(q))], BASE, 3.6)
    p.label(0.2, L(0.2), num(L(0.2), 5), -8, -6, TEXT, 12, "end")
    p.label(0.5, L(0.5), num(L(0.5), 5), -10, -4, TEXT, 12, "end")
    p.label(0.8, L(0.8), num(L(0.8), 5), 10, -4, TEXT, 12)
    p.vline(0.6, 0, L(0.6), PRACTICE, "4 3", 0.9)
    p.points([(0.6, L(0.6))], PRACTICE, 4.5)
    p.label(0.6, L(0.6), hat("p") + " = 0,6:  " + num(L(0.6), 5), 0, -12, PRACTICE, LABEL, "middle")
    p.label(0.03, 0.037, it("L") + "(" + it("p") + ") = " + it("p") + sup("3") + "(1 " + MINUS + " " + it("p") + ")" + sup("2"),
            0, 0, THEORY, LABEL)
    x_axis(p, ticks([0, 0.2, 0.4, 0.5, 0.6, 0.8, 1], 1), it("p"))
    y_axis(p, ticks([0.01, 0.02, 0.03, 0.04], 2), it("L") + "(" + it("p") + ")")
    emit("bernoulli-olabilirlik", 580, 300, [p],
         "Gözlemler 0, 1, 0, 1, 1 iken olabilirlik L(p) = p³(1 − p)². "
         "Birkaç aday değer işaretli: p = 0,6 bu beş sonucu en olası kılan değerdir.",
         aria="Bernoulli likelihood p cubed times one minus p squared, maximal at 0.6, with values at 0.2, 0.5, 0.8 marked")


# ============================================================
# normal-yukseklikler: likelihood as a product of density heights
# ============================================================
def fig_normal_heights():
    data = [3, 5, 6, 7, 9]
    p = Plot(62, 30, 560, 230, (0, 12), (0, 0.22))
    cands = [(6, 2, THEORY, None), (4, 2, REMARK, "7 4"), (6, 3, BASE, "2 4")]
    for mu, s, c, d in cands:
        curve(p, lambda x, mu=mu, s=s: normal_pdf(x, mu, s), 0, 12, c, 2.2, d)
    for x in data:
        p.vline(x, 0, normal_pdf(x, 6, 2), THEORY, "3 3", 0.9)
    p.points([(x, 0) for x in data], PRACTICE, 4.6)
    x_axis(p, [(v, str(v)) for v in (0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12)], it("x"))
    y_axis(p, ticks([0.05, 0.1, 0.15, 0.2], 2), it("f") + "(" + it("x") + ")")
    legend(p, p.X(7.9), p.Y(0.21), [
        (THEORY, None, "N(6, 4):  " + it("L") + " " + APPROX + " 2,59 · 10" + sup(MINUS + "5")),
        (BASE, "2 4", "N(6, 9):  " + it("L") + " " + APPROX + " 1,37 · 10" + sup(MINUS + "5")),
        (REMARK, "7 4", "N(4, 4):  " + it("L") + " " + APPROX + " 2,13 · 10" + sup(MINUS + "6")),
    ], size=12)
    emit("normal-yukseklikler", 740, 300, [p],
         "Beş gözlem (eksen üzerindeki noktalar) ve üç aday normal yoğunluk. Bir adayın olabilirliği, gözlemlerin üstündeki "
         "yoğunluk yüksekliklerinin çarpımıdır; kesikli çizgiler N(6, 4) için bu yükseklikleri gösteriyor. "
         "Merkezi kaydırmak (N(4, 4)) ya da eğriyi yaymak (N(6, 9)) çarpımı küçültür.",
         WIDE, aria="Five data points 3 5 6 7 9 with normal densities N 6 4, N 4 4 and N 6 9; heights of N 6 4 at the points drawn")


# ============================================================
# normal-theta: ln L(theta) for N(theta, theta), sample 0, 2, 2, 4
# ============================================================
def fig_normal_theta():
    data = [0, 2, 2, 4]
    n = len(data)
    lnL = lambda t: -n / 2 * math.log(2 * math.pi * t) - sum((x - t) ** 2 for x in data) / (2 * t)
    p = Plot(70, 36, 450, 220, (0.3, 7), (-14, -6))
    curve(p, lnL, 0.3, 7, THEORY, 2.2)
    p.vline(2, -14, lnL(2), PRACTICE, "4 3", 0.9)
    p.points([(2, lnL(2))], PRACTICE, 4.5)
    p.label(2, lnL(2), hat(THETA) + " = 2:  ln " + it("L") + " " + APPROX + " " + num(lnL(2), 2), 10, -10, PRACTICE, LABEL)
    x_axis(p, [(v, num(v)) for v in (1, 2, 3, 4, 5, 6, 7)], THETA)
    y_axis(p, ticks([-14, -12, -10, -8, -6]), "ln " + it("L") + "(" + THETA + ")", x=0.3)
    emit("normal-theta", 580, 300, [p],
         "N(θ, θ) modelinde 0, 2, 2, 4 örneklemi için log-olabilirlik. "
         "Eğrinin tek bir tepesi vardır ve bu tepe θ² + θ = 6 denkleminin pozitif kökü θ = 2'dedir.",
         aria="Log likelihood of theta for the N theta theta model and the sample 0 2 2 4, maximal at theta 2")


# ============================================================
# duzgun-olabilirlik: L(theta) = theta^-3 on [5, inf), 0 before
# ============================================================
def fig_uniform_likelihood():
    p = Plot(70, 36, 450, 220, (0, 12), (0, 0.009))
    p.line([(0, 0), (5, 0)], THEORY, 2.6)
    curve(p, lambda t: t ** -3, 5, 12, THEORY, 2.2)
    p.vline(5, 0, 0.008, PRACTICE, "4 3", 0.9)
    p.points([(5, 0.008)], PRACTICE, 4.5)
    p.hollow_points([(5, 0)], THEORY, 4.2)
    p.label(5, 0.008, hat(THETA) + " = max " + it("x") + "<tspan font-size=\"10\" dy=\"4\">i</tspan><tspan dy=\"-4\">&#8203;</tspan> = 5", 10, -4, PRACTICE, LABEL)
    p.label(8.2, 0.0035, it("L") + "(" + THETA + ") = 1/" + THETA + sup("3"), 0, 0, THEORY, LABEL)
    p.label(2.5, 0.0, it("L") + "(" + THETA + ") = 0", 0, -10, THEORY, LABEL, "middle")
    x_axis(p, [(v, str(v)) for v in (0, 2, 3, 5, 8, 10, 12)], THETA)
    y_axis(p, [(0.002, "0,002"), (0.004, "0,004"), (0.006, "0,006"), (0.008, "0,008")], it("L") + "(" + THETA + ")")
    emit("duzgun-olabilirlik", 580, 300, [p],
         "U(0, θ) modelinde 2, 3, 5 gözlemleri için olabilirlik. θ < 5 iken 5 gözlemi imkânsızdır ve L(θ) = 0'dır; "
         "θ ≥ 5 iken L(θ) = 1/θ³ azalır. En büyük değer, türevin sıfır olduğu bir noktada değil, "
         "sıçramanın olduğu θ = 5'te alınır.",
         aria="Uniform likelihood for the observations 2 3 5: zero before 5, then one over theta cubed; maximum at 5")


def main():
    fig_two_views()
    fig_poisson_likelihood()
    fig_bernoulli_likelihood()
    fig_normal_heights()
    fig_normal_theta()
    fig_uniform_likelihood()
    for name, md in OUT.items():
        path = OUT_DIR / f"{PREFIX}{name}.md"
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(md)
        print("wrote", path.name)


if __name__ == "__main__":
    main()
