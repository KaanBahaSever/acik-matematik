# -*- coding: utf-8 -*-
"""
Figures of the chapter "Momentler Yöntemi"
(dersler/matematiksel-istatistik/momentler-yontemi.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box: a figure that illustrates a
definition sits directly below that box. The figures are NOT produced at
build time. Run

    python scripts/statistics_figures/mom.py
    python scripts/center_figures.py "statistics-mom-*.md" --keep-width
    python scripts/check_figure_labels.py "scripts/_figures/statistics-mom-*.md"

and paste the markup of scripts/_figures/statistics-mom-<name>.md into the
.qmd. Captions are Turkish on purpose (they are shown on the site); aria
labels are plain ASCII.
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, TEXT, THEORY, PRACTICE, BASE, REMARK  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "statistics-mom-"
OUT = {}

MINUS, APPROX = "&#8722;", "&#8776;"
THETA, LAMBDA, MU, SIGMA = "&#952;", "&#955;", "&#956;", "&#963;"
LABEL = 13     # names of curves and marks
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


XBAR = it("x&#773;")   # x with a combining overline (export_figures.lua composes it for Typst)


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
    """Legend at pixel (px, py) = top-left; entries are (kind, color, dash, text), kind 'line' or 'bar'."""
    for k, (kind, color, dash, s) in enumerate(entries):
        y = py + k * row
        if kind == "bar":
            p.add(f'<rect x="{px+6:.1f}" y="{y-6:.1f}" width="12" height="12" fill="{color}" opacity="0.85" rx="1.5"/>')
        elif kind == "dot":
            p.add(f'<circle cx="{px+12:.1f}" cy="{y:.1f}" r="4.2" fill="{color}"/>')
        else:
            da = f' stroke-dasharray="{dash}"' if dash else ""
            p.add(f'<line x1="{px:.1f}" y1="{y:.1f}" x2="{px+24:.1f}" y2="{y:.1f}" stroke="{color}" stroke-width="2.4"{da} stroke-linecap="round"/>')
        p.text_px(px + 31, y + 4.5, s, TEXT, size)


def hat_label(p, x, y, dx, dy, base, rest, color=TEXT, size=LABEL):
    """Text 'base rest' at a data point with a small hat drawn over the first
    glyph (a combining circumflex is not composed by every renderer)."""
    px, py = p.X(x) + dx, p.Y(y) + dy
    p.text_px(px, py, it(base) + rest, color, size)
    cx, top = px + 0.30 * size, py - 0.80 * size
    w, h = 0.26 * size, 0.20 * size
    p.add(f'<path d="M{cx-w:.1f},{top:.1f} L{cx:.1f},{top-h:.1f} L{cx+w:.1f},{top:.1f}" '
          f'fill="none" stroke="{color}" stroke-width="1.1" stroke-linejoin="round"/>')


def emit(name, W, H, panels, caption, css_class="ders-grafik", aria=""):
    OUT[name] = figure(W, H, panels, caption, css_class, aria)


# ============================================================
# tahmin-edici-dagilimi: distribution of p-hat = X-bar, n = 10, p = 0.3
# ============================================================
def fig_estimator_distribution():
    n, pr = 10, 0.3
    pmf = [math.comb(n, k) * pr ** k * (1 - pr) ** (n - k) for k in range(n + 1)]
    p = Plot(62, 44, 460, 210, (-0.05, 1.05), (0, 0.32))
    p.grid([], [0.1, 0.2, 0.3])
    p.bars([(k / n, pmf[k]) for k in range(n + 1) if k != 4], BASE, 24, 0.75)
    p.bars([(0.4, pmf[4])], PRACTICE, 24, 0.9)
    p.vline(0.3, pmf[3], 0.315, THEORY, "5 3", 0.95)
    p.label(0.3, 0.315, "gerçek " + it("p") + " = 0,3", -8, 4, THEORY, LABEL, "end")
    p.label(0.4, pmf[4], "gözlenen tahmin: 0,4", 16, -4, PRACTICE, LABEL)
    x_axis(p, [(k / n, num(k / n, 1)) for k in range(n + 1)], "")
    y_axis(p, ticks([0.1, 0.2, 0.3], 1), "olasılık", x=-0.05)
    p.text_px(p.x0 + p.w / 2, p.Y(0) + 36, "tahmin edicinin alabileceği değerler " + it("k") + "/10",
              TEXT, 12, "middle")
    emit("tahmin-edici-dagilimi", 580, 330, [p],
         "p = 0,3 iken 10 atışlık örneklemden hesaplanan p̂ = X̄ tahmin edicisinin olasılık fonksiyonu. "
         "Tahmin edici 0; 0,1; …; 1 değerlerinden birini rastgele alır; bu örneklemde gözlenen değer 0,4'tür.",
         aria="Bar chart of the distribution of the sample proportion for n 10 and p 0.3; the bar at 0.4 is highlighted")


# ============================================================
# kuvvet-ailesi: densities (1 + theta) x^theta on [0, 1]
# ============================================================
def fig_power_family():
    p = Plot(62, 40, 450, 230, (0, 1), (0, 4))
    p.grid([0.25, 0.5, 0.75], [1, 2, 3])
    styles = [(REMARK, "7 4"), (BASE, "2 4"), (THEORY, None), (PRACTICE, None)]
    thetas = [-0.5, 0, 1, 3]
    for th, (c, d) in zip(thetas, styles):
        curve(p, lambda x, th=th: (1 + th) * x ** th, 0.0005, 1, c, 2.2, d, n=600)
    for th, (c, d) in zip(thetas, styles):
        m = (1 + th) / (th + 2)
        X, Y = p.X(m), p.Y(0)
        p.add(f'<polygon points="{X:.1f},{Y-3:.1f} {X-5:.1f},{Y-12:.1f} {X+5:.1f},{Y-12:.1f}" fill="{c}"/>')
    x_axis(p, ticks([0, 0.25, 0.5, 0.75, 1], 2), it("x"))
    y_axis(p, ticks([1, 2, 3, 4]), it("f") + "(" + it("x") + "; " + THETA + ")")
    legend(p, p.X(0.2), p.Y(3.75),
           [("line", c, d, THETA + " = " + num(th)) for th, (c, d) in zip(thetas, styles)])
    emit("kuvvet-ailesi", 560, 310, [p],
         "Kuvvet ailesinden dört yoğunluk. θ büyüdükçe kütle 1'e doğru kayar; eksenin üstündeki üçgenler "
         "beklenen değerleri 1/3, 1/2, 2/3 ve 4/5'i gösterir. Bu yüzden X̄ bize θ hakkında bilgi verir.",
         aria="Densities (1+theta) x to the theta for theta -0.5, 0, 1, 3 with their means marked on the axis")


# ============================================================
# kuvvet-moment-denklemi: solving (1+theta)/(theta+2) = 0.24
# ============================================================
def fig_power_moment_equation():
    mu = lambda t: (1 + t) / (t + 2)
    th_hat = -13 / 19
    p = Plot(62, 40, 450, 220, (-1, 6), (0, 1))
    p.grid([0, 2, 4, 6], [0.5, 0.75])
    p.line([(-1, 1), (6, 1)], TEXT, 1.0, "3 4", 0.45)
    curve(p, mu, -0.999, 6, THEORY, 2.3)
    p.line([(-1, 0.24), (th_hat, 0.24)], PRACTICE, 1.6, "5 3")
    p.line([(th_hat, 0.24), (th_hat, 0)], PRACTICE, 1.6, "5 3")
    p.points([(th_hat, 0.24)], PRACTICE, 4.5)
    p.label(-1, 0.24, "0,24", -7, 4, PRACTICE, TICK, "end")
    p.label(th_hat, 0.24, XBAR + " = 0,24", 12, 22, PRACTICE, LABEL)
    hat_label(p, th_hat, 0.24, 12, 42, THETA, " " + APPROX + " " + MINUS + "0,684", PRACTICE)
    p.label(3.2, mu(3.2), it("E") + "(" + it("X") + ") = (1 + " + THETA + ")/(" + THETA + " + 2)", 0, -12, THEORY, LABEL, "middle")
    x_axis(p, ticks([-1, 0, 1, 2, 3, 4, 5, 6]), THETA)
    y_axis(p, ticks([0.5, 0.75, 1], 2), it("E") + "(" + it("X") + ")", x=-1)
    emit("kuvvet-moment-denklemi", 560, 300, [p],
         "E(X) = (1 + θ)/(θ + 2) eğrisi artandır ve 0 ile 1 arasındaki her değeri bir kez alır. "
         "Yatay x̄ = 0,24 çizgisi eğriyi tek bir noktada keser; o noktanın apsisi θ̂ = −13/19 ≈ −0,684 tahminidir.",
         aria="Increasing curve of the mean against theta; the horizontal line at 0.24 meets it above theta hat -0.684")


# ============================================================
# normal-uyum: ten observations and the fitted N(5, 0.06) density
# ============================================================
def fig_normal_fit():
    mu, s2 = 5.0, 0.06
    s = math.sqrt(s2)
    f = lambda x: math.exp(-(x - mu) ** 2 / (2 * s2)) / (s * math.sqrt(2 * math.pi))
    p = Plot(62, 40, 450, 210, (4.2, 5.8), (0, 1.9))
    band = [(mu - s, 0)] + sample(f, mu - s, mu + s, 200) + [(mu + s, 0)]
    p.polygon(band, THEORY, 0.14)
    curve(p, f, 4.2, 5.8, THEORY, 2.3)
    p.vline(mu, 0, f(mu), THEORY, "5 3", 0.8)
    data = [4.8, 5.2, 5.0, 4.6, 5.4, 5.1, 4.9, 5.3, 4.7, 5.0]
    seen = {}
    for v in data:
        k = seen.get(v, 0)
        seen[v] = k + 1
        p.add(f'<circle cx="{p.X(v):.1f}" cy="{p.Y(0) - 7 - 12 * k:.1f}" r="4.6" fill="{PRACTICE}"/>')
    hat_label(p, mu, f(mu), 8, -8, MU, " = 5", THEORY)
    p.line([(mu, 0.32), (mu + s, 0.32)], THEORY, 1.4)
    hat_label(p, mu, 0.32, 8, -8, SIGMA, " " + APPROX + " 0,245", THEORY, 12)
    x_axis(p, ticks([4.2, 4.4, 4.6, 4.8, 5.0, 5.2, 5.4, 5.6, 5.8], 1), it("x"))
    y_axis(p, ticks([0.5, 1, 1.5], 1), it("f") + "(" + it("x") + ")")
    legend(p, p.X(5.38), p.Y(1.8), [("dot", PRACTICE, None, "gözlemler")])
    emit("normal-uyum", 560, 290, [p],
         "On paketin ağırlıkları (noktalar; 5,0 iki kez gözlendi) ve momentler yöntemiyle kurulan N(5; 0,06) yoğunluğu. "
         "Taralı şerit μ̂ ± σ̂ aralığıdır.",
         aria="Ten observations as dots on the axis and the fitted normal density with mean 5 and variance 0.06")


# ============================================================
# poisson-iki-tahmin: observed frequencies against Poisson(1.85) and Poisson(1.4275)
# ============================================================
def fig_poisson_two():
    freq = {0: 3, 1: 5, 2: 6, 3: 4, 4: 2}
    n = 20
    l1, l2 = 1.85, 1.4275
    pois = lambda k, l: math.exp(-l) * l ** k / math.factorial(k)
    p = Plot(62, 40, 470, 210, (-0.6, 6.6), (0, 0.4))
    p.grid([], [0.1, 0.2, 0.3, 0.4])
    ks = range(7)
    p.bars([(k - 0.22, freq.get(k, 0) / n) for k in ks], BASE, 13, 0.75)
    p.bars([(k, pois(k, l1)) for k in ks], THEORY, 13, 0.9)
    p.bars([(k + 0.22, pois(k, l2)) for k in ks], PRACTICE, 13, 0.9)
    x_axis(p, [(k, str(k)) for k in ks], it("k"))
    y_axis(p, ticks([0.1, 0.2, 0.3, 0.4], 1), "oran / olasılık", x=-0.6)
    legend(p, p.X(3.7), p.Y(0.39), [("bar", BASE, None, "gözlenen oran"),
                                     ("bar", THEORY, None, "Poisson(1,85)"),
                                     ("bar", PRACTICE, None, "Poisson(1,4275)")])
    emit("poisson-iki-tahmin", 580, 290, [p],
         "Yirmi dakikada gözlenen çağrı sayılarının oranları ile iki moment tahmininden kurulan Poisson olasılıkları. "
         "Ortalamadan gelen λ̂₁ = 1,85 ile varyanstan gelen λ̂₂ = 1,4275 farklı modeller verir.",
         aria="Grouped bars: observed proportions of call counts and Poisson probabilities with lambda 1.85 and 1.4275")


# ============================================================
# ucgen-celiski: triangular density with theta-hat = 1.4 and an observation at 1.6
# ============================================================
def fig_triangle_conflict():
    th = 1.4
    p = Plot(62, 40, 450, 210, (0, 1.8), (0, 1.6))
    p.grid([0.5, 1, 1.5], [0.5, 1, 1.5])
    p.polygon([(0, 0), (0, 2 / th), (th, 0)], THEORY, 0.12)
    p.line([(0, 2 / th), (th, 0)], THEORY, 2.3)
    p.line([(th, 0), (1.8, 0)], THEORY, 2.3)
    p.vline(th, 0, 1.2, THEORY, "5 3", 0.8)
    hat_label(p, th, 1.2, -58, -6, THETA, " = 1,4", THEORY)
    xbar = 7 / 15
    X, Y = p.X(xbar), p.Y(0)
    p.add(f'<polygon points="{X:.1f},{Y+4:.1f} {X-5:.1f},{Y+13:.1f} {X+5:.1f},{Y+13:.1f}" fill="{TEXT}" opacity="0.8"/>')
    data = [0.2, 0.1, 0.4, 0.3, 0.2, 1.6]
    seen = {}
    for v in data:
        k = seen.get(v, 0)
        seen[v] = k + 1
        c = REMARK if v > th else PRACTICE
        p.add(f'<circle cx="{p.X(v):.1f}" cy="{p.Y(0) - 7 - 12 * k:.1f}" r="4.6" fill="{c}"/>')
    p.label(1.6, 0, "gözlem 1,6", 0, -20, REMARK, LABEL, "middle")
    p.label(0.62, 2 / th * (1 - 0.62 / th), it("f") + "(" + it("x") + ") = 2(1,4 " + MINUS + " " + it("x") + ")/1,96",
            8, -8, THEORY, LABEL)
    x_axis(p, [(0.5, ""), (1.0, "1,0"), (1.5, "1,5")], it("x"))
    p.text_px(X, Y + 28, XBAR + " = 7/15", TEXT, 12, "middle")
    y_axis(p, ticks([0.5, 1, 1.5], 1), it("f") + "(" + it("x") + ")")
    emit("ucgen-celiski", 560, 300, [p],
         "θ̂ = 3x̄ = 1,4 ile kurulan üçgen yoğunluk 1,4'ün sağında sıfırdır; oysa gözlemlerden biri 1,6'dır. "
         "Moment tahmini, verinin kendisiyle çelişen bir model üretebilir.",
         aria="Triangular density on 0 to 1.4 with the observations as dots; one observation at 1.6 lies outside the support")


def main():
    fig_estimator_distribution()
    fig_power_family()
    fig_power_moment_equation()
    fig_normal_fit()
    fig_poisson_two()
    fig_triangle_conflict()
    for name, md in OUT.items():
        path = OUT_DIR / f"{PREFIX}{name}.md"
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(md)
        print("wrote", path.name)


if __name__ == "__main__":
    main()
