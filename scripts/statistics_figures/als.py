# -*- coding: utf-8 -*-
"""
Figures of the chapter "Alıştırmalar" (dersler/matematiksel-istatistik/alistirmalar.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box. The figures are NOT produced at
build time. Run

    python scripts/statistics_figures/als.py
    python scripts/center_figures.py "statistics-als-*.md" --keep-width
    python scripts/check_figure_labels.py "scripts/_figures/statistics-als-*.md"

and paste the markup of scripts/_figures/statistics-als-<name>.md into the .qmd.
The captions are Turkish on purpose; the aria labels are plain ASCII.
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, TEXT, THEORY, PRACTICE, WIDE  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "statistics-als-"


def npdf(x, mu, s):
    return math.exp(-((x - mu) / s) ** 2 / 2) / (s * math.sqrt(2 * math.pi))


def sample(f, x0, x1, n=300):
    return [(x0 + (x1 - x0) * i / n, f(x0 + (x1 - x0) * i / n)) for i in range(n + 1)]


def area(p, f, x0, x1, color, opacity):
    p.polygon([(x0, 0.0)] + sample(f, x0, x1, 200) + [(x1, 0.0)], fill=color, opacity=opacity)


def save(name, svg):
    (OUT_DIR / f"{PREFIX}{name}.md").write_text(svg, encoding="utf-8", newline="\n")


# ============================================================
# power of the two-sided test: H0 mu = 9 against mu = 10
# ============================================================
LO, HI = 8.1775, 9.8225
h0 = lambda x: npdf(x, 9, 0.5)    # noqa: E731
h1 = lambda x: npdf(x, 10, 0.5)   # noqa: E731
X0, X1 = 7.2, 11.9
p = Plot(50, 60, 600, 230, (X0, X1), (0, 0.85))
p.line([(X0, 0), (X1, 0)], color=TEXT, width=1.1, opacity=0.5)
p.label(X1, 0, "x&#772;", dx=10, dy=5, size=15, italic=True)
# power: area under the mu = 10 curve over the rejection region
area(p, h1, HI, X1, PRACTICE, 0.28)
area(p, h1, X0, LO, PRACTICE, 0.28)
# alpha/2 tails under H0
area(p, h0, X0, LO, THEORY, 0.30)
area(p, h0, HI, X1, THEORY, 0.30)
p.line(sample(h0, X0, X1), color=THEORY, width=2.2)
p.line(sample(h1, X0, X1), color=PRACTICE, width=2.2, dash="7 4")
for c in (LO, HI):
    p.vline(c, 0, 0.84, color=TEXT, dash="4 3", opacity=0.7)
p.label(LO, 0, "8,1775", dy=37, anchor="middle", size=12.5)
p.label(HI, 0, "9,8225", dy=37, anchor="middle", size=12.5)
p.label(9, 0, "9", dy=19, anchor="middle", size=12.5)
p.label(10, 0, "10", dy=19, anchor="middle", size=12.5)
# curve names
p.label(8.35, h0(8.35), "&#956; = 9 (H&#8320;)", dx=-12, dy=-8, anchor="end", color=THEORY, size=13)
p.label(10.75, h1(10.75), "&#956; = 10", dx=12, dy=-8, color=PRACTICE, size=13)
# region names above the plot
p.text_px(p.X((X0 + LO) / 2), 48, "ret", anchor="middle", size=13)
p.text_px(p.X((LO + HI) / 2), 48, "kabul", anchor="middle", size=13)
p.text_px(p.X((HI + X1) / 2), 48, "ret", anchor="middle", size=13)
# legend
p.polygon([(11.05, 0.72), (11.25, 0.72), (11.25, 0.77), (11.05, 0.77)], fill=PRACTICE, opacity=0.35)
p.label(11.28, 0.72, "güç &#8776; 0,639", dx=4, dy=0, size=12.5)
p.polygon([(11.05, 0.62), (11.25, 0.62), (11.25, 0.67), (11.05, 0.67)], fill=THEORY, opacity=0.35)
p.label(11.28, 0.62, "&#945; = 0,10", dx=4, dy=0, size=12.5)
save("guc", figure(760, 330, [p],
                   "Mavi eğri H₀ altında (μ = 9), kesikli turuncu eğri μ = 10 iken X̄'nin dağılımı. "
                   "Mavi kuyruklar toplamı α = 0,10; turuncu taralı alan testin gücüdür.",
                   css_class=WIDE, aria="Two normal curves for the sample mean with the critical region and the power shaded"))
print("ok")
