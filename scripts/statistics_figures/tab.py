# -*- coding: utf-8 -*-
"""
Figures of the page "Tablolar" (dersler/matematiksel-istatistik/tablolar.qmd).

Each figure shows which area its table gives. Figures go INSIDE the box they
explain, never inside a definition box. The figures are NOT produced at build
time. Run

    python scripts/statistics_figures/tab.py
    python scripts/center_figures.py "statistics-tab-*.md" --keep-width
    python scripts/check_figure_labels.py "scripts/_figures/statistics-tab-*.md"

and paste the markup of scripts/_figures/statistics-tab-<name>.md into the .qmd.
The captions are Turkish on purpose; the aria labels are plain ASCII.
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, TEXT, THEORY, PRACTICE  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "statistics-tab-"

W, H = 560, 250
PX, PY, PW, PH = 50, 30, 470, 170


def normal(x):
    return math.exp(-x * x / 2) / math.sqrt(2 * math.pi)


def student(x, nu):
    c = math.gamma((nu + 1) / 2) / (math.sqrt(nu * math.pi) * math.gamma(nu / 2))
    return c * (1 + x * x / nu) ** (-(nu + 1) / 2)


def chi2(x, k):
    if x <= 0:
        return 0.0
    return x ** (k / 2 - 1) * math.exp(-x / 2) / (2 ** (k / 2) * math.gamma(k / 2))


def fdens(x, a, b):
    if x <= 0:
        return 0.0
    c = math.gamma((a + b) / 2) / (math.gamma(a / 2) * math.gamma(b / 2)) * (a / b) ** (a / 2)
    return c * x ** (a / 2 - 1) * (1 + a * x / b) ** (-(a + b) / 2)


def sample(f, x0, x1, n=300):
    return [(x0 + (x1 - x0) * i / n, f(x0 + (x1 - x0) * i / n)) for i in range(n + 1)]


def shaded(p, f, x0, x1):
    pts = sample(f, x0, x1, 200)
    poly = [(x0, 0.0)] + pts + [(x1, 0.0)]
    p.polygon(poly, fill=THEORY, opacity=0.22)


def curve(p, f, x0, x1):
    p.line(sample(f, x0, x1), color=THEORY, width=2.2)


def cut(p, x, f, label):
    p.vline(x, 0, f(x), color=PRACTICE, dash=None, opacity=0.9)
    p.label(x, 0, label, dy=19, anchor="middle", color=PRACTICE, size=14, italic=True)


def base_axis(p, xlabel):
    p.line([(p.xmin, 0), (p.xmax, 0)], color=TEXT, width=1.1, opacity=0.5)
    p.label(p.xmax, 0, xlabel, dx=10, dy=5, size=14, italic=True)


def save(name, svg):
    (OUT_DIR / f"{PREFIX}{name}.md").write_text(svg, encoding="utf-8", newline="\n")


# ============================================================
# standard normal: area between 0 and z
# ============================================================
p = Plot(PX, PY, PW, PH, (-3.6, 3.6), (0, 0.42))
base_axis(p, "z")
shaded(p, normal, 0, 1.5)
curve(p, normal, -3.6, 3.6)
p.vline(0, 0, normal(0), color=TEXT, dash="4 3", opacity=0.6)
p.label(0, 0, "0", dy=18, anchor="middle", size=13)
cut(p, 1.5, normal, "z")
p.label(0.75, 0.13, "P(0 &#8804; Z &#8804; z)", dx=0, anchor="middle", size=13)
p.label(-2.2, 0.3, "N(0, 1)", anchor="middle", color=THEORY, size=13)
save("normal", figure(W, H, [p], "Tablodaki değer, standart normal eğrinin altında 0 ile z arasında kalan taralı alandır.",
                      aria="Standard normal density with the area from 0 to z shaded"))

# ============================================================
# t: area to the left of t_p
# ============================================================
p = Plot(PX, PY, PW, PH, (-4.2, 4.2), (0, 0.42))
base_axis(p, "t")
shaded(p, lambda x: student(x, 5), -4.2, 1.5)
curve(p, lambda x: student(x, 5), -4.2, 4.2)
p.label(0, 0, "0", dy=18, anchor="middle", size=13)
cut(p, 1.5, lambda x: student(x, 5), "t")
p.label(-0.9, 0.12, "p", anchor="middle", size=15, italic=True)
p.label(2.5, 0.3, "t dağılımı", anchor="middle", color=THEORY, size=13)
save("t", figure(W, H, [p], "Tablodaki t değeri, solunda kalan alan p olan noktadır: P(T ≤ t) = p.",
                 aria="t density with the area to the left of the quantile shaded"))

# ============================================================
# chi-square: area to the left of chi2_p
# ============================================================
k = 5
p = Plot(PX, PY, PW, PH, (0, 18), (0, 0.17))
base_axis(p, "x")
shaded(p, lambda x: chi2(x, k), 0, 9.2)
curve(p, lambda x: chi2(x, k), 0, 18)
p.label(0, 0, "0", dy=18, anchor="middle", size=13)
cut(p, 9.2, lambda x: chi2(x, k), "&#967;&#178;")
p.label(4.4, 0.05, "p", anchor="middle", size=15, italic=True)
p.label(13.5, 0.1, "&#967;&#178; dağılımı", anchor="middle", color=THEORY, size=13)
save("ki-kare", figure(W, H, [p], "Tablodaki χ² değeri, solunda kalan alan p olan noktadır.",
                       aria="Chi-square density with the area to the left of the quantile shaded"))

# ============================================================
# F: area to the left of F_p
# ============================================================
a, b = 6, 12
p = Plot(PX, PY, PW, PH, (0, 5), (0, 0.8))
base_axis(p, "x")
shaded(p, lambda x: fdens(x, a, b), 0, 2.4)
curve(p, lambda x: fdens(x, a, b), 0, 5)
p.label(0, 0, "0", dy=18, anchor="middle", size=13)
cut(p, 2.4, lambda x: fdens(x, a, b), "f")
p.label(1.0, 0.22, "p", anchor="middle", size=15, italic=True)
p.label(3.7, 0.5, "F dağılımı", anchor="middle", color=THEORY, size=13)
save("f", figure(W, H, [p], "Tablodaki F değeri, solunda kalan alan p olan noktadır: P(F ≤ f) = p.",
                 aria="F density with the area to the left of the quantile shaded"))
print("ok")
