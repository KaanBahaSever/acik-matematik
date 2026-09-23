# -*- coding: utf-8 -*-
"""
Figures of the chapter "Örneklem Dağılımları"
(dersler/matematiksel-istatistik/orneklem-dagilimlari.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box: a figure that illustrates a
definition sits directly below that box. The figures are NOT produced at
build time. Run

    python scripts/statistics_figures/odg.py
    python scripts/center_figures.py "statistics-odg-*.md" --keep-width
    python scripts/check_figure_labels.py "scripts/_figures/statistics-odg-*.md"

and paste the markup of scripts/_figures/statistics-odg-<name>.md into the
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
PREFIX = "statistics-odg-"
OUT = {}

MINUS, NU, CHI, APPROX = "&#8722;", "&#957;", "&#967;", "&#8776;"
LABEL = 13     # names of curves and areas
TICK = 11      # axis numbers
SAMPLES = 480


# ------------------------------------------------------------
# helpers
# ------------------------------------------------------------
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


def sup(s):
    return f'<tspan font-size="9" dy="-5">{s}</tspan><tspan dy="5">&#8203;</tspan>'


def chi2_pdf(x, k):
    if x <= 0:
        return 0.0
    return math.exp((k / 2 - 1) * math.log(x) - x / 2 - (k / 2) * math.log(2) - math.lgamma(k / 2))


def t_pdf(x, k):
    c = math.lgamma((k + 1) / 2) - math.lgamma(k / 2) - 0.5 * math.log(math.pi * k)
    return math.exp(c - (k + 1) / 2 * math.log(1 + x * x / k))


def f_pdf(x, a, b):
    if x <= 0:
        return 0.0
    c = (math.lgamma((a + b) / 2) - math.lgamma(a / 2) - math.lgamma(b / 2)
         + (a / 2) * math.log(a) + (b / 2) * math.log(b))
    return math.exp(c + (a / 2 - 1) * math.log(x) - (a + b) / 2 * math.log(b + a * x))


def normal_pdf(x, mu=0.0, s=1.0):
    return math.exp(-0.5 * ((x - mu) / s) ** 2) / (s * math.sqrt(2 * math.pi))


def sample(f, a, b, n=SAMPLES, ymax=None):
    """Points of f on [a, b]; with ymax the part above ymax is dropped
    (used for densities that blow up at 0)."""
    pts = [(a + (b - a) * k / n, f(a + (b - a) * k / n)) for k in range(n + 1)]
    if ymax is not None:
        pts = [(x, y) for x, y in pts if y <= ymax]
    return pts


def shade(p, f, a, b, color=PRACTICE, opacity=0.30, n=240):
    pts = [(a, 0)] + sample(f, a, b, n) + [(b, 0)]
    p.polygon(pts, color, opacity)


def x_axis(p, ticks, name=""):
    """Horizontal axis at y = 0 with an arrow head; ticks are (value, label)."""
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


def y_axis(p, ticks, name="", x=None, digits=None):
    X = p.X(p.xmin if x is None else x)
    top, bottom = p.y0 - 10, p.Y(0)
    p.add(f'<g stroke="{TEXT}" stroke-width="1.1" opacity="0.5" fill="{TEXT}">'
          f'<line x1="{X:.1f}" y1="{bottom:.1f}" x2="{X:.1f}" y2="{top:.1f}"/>'
          f'<polygon points="{X:.1f},{top:.1f} {X-3.5:.1f},{top+8:.1f} {X+3.5:.1f},{top+8:.1f}" stroke="none"/></g>')
    for v in ticks:
        Y = p.Y(v)
        p.add(f'<line x1="{X-3:.1f}" y1="{Y:.1f}" x2="{X+3:.1f}" y2="{Y:.1f}" stroke="{TEXT}" stroke-width="1" opacity="0.7"/>')
        p.add(f'<text x="{X-7:.1f}" y="{Y+4:.1f}" fill="{TEXT}" font-size="{TICK}" text-anchor="end" opacity="0.8">{num(v, digits)}</text>')
    if name:
        p.add(f'<text x="{X+8:.1f}" y="{top+6:.1f}" fill="{TEXT}" font-size="12" font-style="italic" opacity="0.85">{name}</text>')


def legend(p, px, py, entries, row=20):
    """entries: (label, color, dash). Drawn at pixel position (px, py)."""
    for i, (lab, c, d) in enumerate(entries):
        y = py + i * row
        da = f' stroke-dasharray="{d}"' if d else ""
        p.add(f'<line x1="{px:.1f}" y1="{y:.1f}" x2="{px+26:.1f}" y2="{y:.1f}" stroke="{c}" stroke-width="2.2"{da}/>')
        p.text_px(px + 33, y + 4.5, lab, TEXT, 12.5)


def guide(p, x, f, color=PRACTICE):
    p.vline(x, 0, f(x), color, "4 3", 0.85)


def emit(name, W, H, panels, caption, css_class="ders-grafik", aria=""):
    OUT[name] = figure(W, H, panels, caption, css_class, aria)


# ============================================================
# ki-kare-aile: chi-square densities for nu = 1, 2, 4, 8
# ============================================================
def fig_chi2_family():
    W, H = 560, 290
    p = Plot(46, 30, 470, 210, (0, 16), (0, 0.5))
    entries = []
    for k, c, d in ((1, REMARK, "6 4"), (2, BASE, None), (4, THEORY, None), (8, PRACTICE, None)):
        p.line(sample(lambda x, k=k: chi2_pdf(x, k), 0.0005 if k == 1 else 1e-6, 16, ymax=0.5), c, 2.1, d)
        entries.append((f"{it(NU)} = {k}", c, d))
    x_axis(p, [(v, num(v)) for v in (0, 2, 4, 6, 8, 10, 12, 14)], it("u"))
    y_axis(p, (0.1, 0.2, 0.3, 0.4, 0.5), it("f") + "(" + it("u") + ")", 0)
    legend(p, 360, 70, entries)
    emit("ki-kare-aile", W, H, [p],
         "Serbestlik derecesi ν = 1, 2, 4 ve 8 olan χ² yoğunlukları. ν = 1 ve ν = 2 için eğri sıfırdan "
         "başlayarak azalır; ν ≥ 3 için tepe ν − 2 noktasındadır. ν büyüdükçe eğri sağa kayar, yayılır "
         "ve daha simetrik bir çan biçimine yaklaşır.",
         aria="Chi-square densities with 1, 2, 4 and 8 degrees of freedom")


# ============================================================
# ki-kare-normal: chi-square 50 against N(50, 100)
# ============================================================
def fig_chi2_normal():
    W, H = 560, 280
    p = Plot(50, 30, 460, 200, (15, 95), (0, 0.045))
    p.line(sample(lambda x: normal_pdf(x, 50, 10), 15, 95), PRACTICE, 2.0, "6 4")
    p.line(sample(lambda x: chi2_pdf(x, 50), 15, 95), THEORY, 2.2)
    x_axis(p, [(v, num(v)) for v in (20, 30, 40, 50, 60, 70, 80, 90)], it("u"))
    y_axis(p, (0.01, 0.02, 0.03, 0.04), "", 15, 2)
    legend(p, 372, 58, [(f"{CHI}{sup('2')}{sub('50')}", THEORY, None),
                        (f"{it('N')}(50, 100)", PRACTICE, "6 4")], row=22)
    emit("ki-kare-normal", W, H, [p],
         "χ²₅₀ yoğunluğu (düz) ile aynı ortalama ve varyansa sahip N(50, 100) yoğunluğu (kesikli). "
         "İki eğri birbirine çok yakındır; χ² eğrisinin tepesi biraz solda, sağ kuyruğu biraz daha "
         "kalındır.",
         aria="Chi-square density with 50 degrees of freedom and the normal density with mean 50 and variance 100")


# ============================================================
# ki-kare-kantiller: chi-square 9, quantiles 2.70 and 19.02
# ============================================================
def fig_chi2_quantiles():
    W, H = 560, 270
    f = lambda x: chi2_pdf(x, 9)
    p = Plot(46, 30, 470, 190, (0, 26), (0, 0.11))
    lo, hi = 2.7004, 19.0228
    shade(p, f, 0, lo, PRACTICE, 0.40)
    shade(p, f, hi, 26, PRACTICE, 0.40)
    shade(p, f, lo, hi, THEORY, 0.14)
    p.line(sample(f, 0, 26), THEORY, 2.2)
    x_axis(p, [(v, num(v)) for v in (0, 5, 10, 15, 25)] + [(lo, ""), (hi, "")], it("u"))
    guide(p, lo, f)
    guide(p, hi, f)
    Y = p.Y(0)
    p.text_px(p.X(lo), Y + 32, "2,70", PRACTICE, 12, "middle", bold=True)
    p.text_px(p.X(hi), Y + 32, "19,02", PRACTICE, 12, "middle", bold=True)
    p.text(9.2, 0.035, "0,95", THEORY, LABEL, "middle", bold=True)
    # leaders to the thin tails
    p.add(f'<line x1="{p.X(1.9):.1f}" y1="{p.Y(0.006):.1f}" x2="{p.X(1.2):.1f}" y2="{p.Y(0.045):.1f}" stroke="{PRACTICE}" stroke-width="1" opacity="0.8"/>')
    p.text(1.2, 0.05, "0,025", PRACTICE, 12.5, "middle", bold=True)
    p.add(f'<line x1="{p.X(20.2):.1f}" y1="{p.Y(0.006):.1f}" x2="{p.X(21.8):.1f}" y2="{p.Y(0.034):.1f}" stroke="{PRACTICE}" stroke-width="1" opacity="0.8"/>')
    p.text(21.8, 0.039, "0,025", PRACTICE, 12.5, "middle", bold=True)
    emit("ki-kare-kantiller", W, H, [p],
         "χ²₉ yoğunluğu. 2,70'in solunda ve 19,02'nin sağında 0,025'er alan kalır; aradaki alan 0,95'tir. "
         "Dağılım simetrik olmadığından iki kantil 0'a göre simetrik değildir; ayrı ayrı okunur.",
         aria="Chi-square density with 9 degrees of freedom, tails below 2.70 and above 19.02 shaded with area 0.025 each")


# ============================================================
# t-aile: t densities for nu = 1, 3, 10 and the standard normal
# ============================================================
def fig_t_family():
    W, H = 560, 280
    p = Plot(46, 30, 470, 200, (-5, 5), (0, 0.42))
    entries = []
    for k, c, d in ((1, REMARK, None), (3, BASE, None), (10, THEORY, None)):
        p.line(sample(lambda x, k=k: t_pdf(x, k), -5, 5), c, 2.1, d)
        entries.append((f"{it(NU)} = {k}", c, d))
    p.line(sample(normal_pdf, -5, 5), PRACTICE, 2.0, "6 4")
    entries.append((f"{it('N')}(0, 1)", PRACTICE, "6 4"))
    x_axis(p, [(v, num(v)) for v in range(-4, 5)], it("t"))
    y_axis(p, (0.1, 0.2, 0.3, 0.4), "", -5)
    legend(p, 395, 52, entries)
    emit("t-aile", W, H, [p],
         "Serbestlik derecesi ν = 1, 3 ve 10 olan t yoğunlukları ile standart normal yoğunluk (kesikli). "
         "Hepsi 0'a göre simetriktir. t eğrilerinin tepesi daha alçak, kuyrukları daha kalındır; ν büyüdükçe "
         "eğri standart normale yaklaşır.",
         aria="Student t densities with 1, 3 and 10 degrees of freedom and the standard normal density")


# ============================================================
# t-simetrik: t with 9 df, P(-2.262 <= T <= 2.262) = 0.95
# ============================================================
def fig_t_symmetric():
    W, H = 560, 260
    f = lambda x: t_pdf(x, 9)
    p = Plot(46, 30, 470, 180, (-4.5, 4.5), (0, 0.42))
    c = 2.2622
    shade(p, f, -4.5, -c, PRACTICE, 0.40)
    shade(p, f, c, 4.5, PRACTICE, 0.40)
    shade(p, f, -c, c, THEORY, 0.14)
    p.line(sample(f, -4.5, 4.5), THEORY, 2.2)
    x_axis(p, [(v, num(v)) for v in (-4, -1, 0, 1, 4)] + [(-c, ""), (c, "")], it("t"))
    guide(p, -c, f)
    guide(p, c, f)
    Y = p.Y(0)
    p.text_px(p.X(-c), Y + 32, f"{MINUS}2,262", PRACTICE, 12, "middle", bold=True)
    p.text_px(p.X(c), Y + 32, "2,262", PRACTICE, 12, "middle", bold=True)
    p.text(0, 0.14, "0,95", THEORY, LABEL, "middle", bold=True)
    p.add(f'<line x1="{p.X(-2.9):.1f}" y1="{p.Y(0.012):.1f}" x2="{p.X(-3.5):.1f}" y2="{p.Y(0.07):.1f}" stroke="{PRACTICE}" stroke-width="1" opacity="0.8"/>')
    p.text(-3.5, 0.078, "0,025", PRACTICE, 12.5, "middle", bold=True)
    p.add(f'<line x1="{p.X(2.9):.1f}" y1="{p.Y(0.012):.1f}" x2="{p.X(3.5):.1f}" y2="{p.Y(0.07):.1f}" stroke="{PRACTICE}" stroke-width="1" opacity="0.8"/>')
    p.text(3.5, 0.078, "0,025", PRACTICE, 12.5, "middle", bold=True)
    emit("t-simetrik", W, H, [p],
         "t₉ yoğunluğu. Simetri nedeniyle 2,262'nin sağındaki ve −2,262'nin solundaki alanlar eşittir "
         "(0,025'er); aradaki alan 0,95'tir.",
         aria="Student t density with 9 degrees of freedom, both tails beyond 2.262 shaded with area 0.025 each")


# ============================================================
# f-aile: F densities for (2, 10), (5, 10), (20, 30)
# ============================================================
def fig_f_family():
    W, H = 560, 280
    p = Plot(46, 30, 470, 200, (0, 4), (0, 1.2))
    entries = []
    for (a, b), c in (((2, 10), REMARK), ((5, 10), BASE), ((20, 30), THEORY)):
        p.line(sample(lambda x, a=a, b=b: f_pdf(x, a, b), 1e-6, 4), c, 2.1)
        entries.append((f"({it(NU)}{sub('1')}, {it(NU)}{sub('2')}) = ({a}, {b})", c, None))
    x_axis(p, [(v, num(v)) for v in (0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5)], it("x"))
    y_axis(p, (0.2, 0.4, 0.6, 0.8, 1.0, 1.2), "", 0)
    legend(p, 330, 60, entries)
    emit("f-aile", W, H, [p],
         "Serbestlik dereceleri (2, 10), (5, 10) ve (20, 30) olan F yoğunlukları. Hepsi yalnız pozitif "
         "değerler alır ve sağa çarpıktır; serbestlik dereceleri büyüdükçe dağılım 1'in çevresinde toplanır.",
         aria="F densities with degrees of freedom 2 and 10, 5 and 10, 20 and 30")


fig_chi2_family()
fig_chi2_normal()
fig_chi2_quantiles()
fig_t_family()
fig_t_symmetric()
fig_f_family()

for name, content in OUT.items():
    with io.open(OUT_DIR / f"{PREFIX}{name}.md", "w", encoding="utf-8", newline="\n") as fh:
        fh.write(content)
print(f"generated {len(OUT)} figures:", ", ".join(OUT))
