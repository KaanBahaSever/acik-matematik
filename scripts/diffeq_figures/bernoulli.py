# -*- coding: utf-8 -*-
"""
Figures of the chapter "Bernoulli ve Riccati Denklemleri"
(dersler/diferansiyel-denklemler/bernoulli-ve-riccati-denklemleri.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box and never directly under a heading.
The figures are NOT produced at build time. Run

    python scripts/diffeq_figures/bernoulli.py
    python scripts/center_figures.py "diffeq-bernoulli-*.md"
    python scripts/check_figure_labels.py "scripts/_figures/diffeq-bernoulli-*.md"

and paste the markup of scripts/_figures/diffeq-bernoulli-<name>.md into the .qmd.
The captions are Turkish on purpose; the aria labels are plain ASCII.
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import save, graph, slope_field, frame  # noqa: E402
from svg_plot import Plot, figure, sup, BASE, PRACTICE, REMARK, TEXT, THEORY  # noqa: E402

PREFIX = "diffeq-bernoulli-"
MINUS = "&#8722;"


def it(s):
    """Italic math letter inside an SVG <text>."""
    return f'<tspan font-style="italic">{s}</tspan>'


def num(v):
    """Tick label with a typographic minus sign and a decimal comma."""
    s = f"{v:g}".replace(".", ",")
    return s.replace("-", MINUS)


# ============================================================
# Logistic equation y' = y - y^2 (exercise: r = k = 1)
# General solution y = 1/(1 + C e^{-x}), C = 1/y0 - 1 for y(0) = y0;
# equilibria y = 0 (lost when dividing by y^2) and y = 1 (C = 0).
# ============================================================
def logistic():
    W, H = 540, 340
    p = Plot(52, 26, 430, 262, (-2.0, 5.0), (-1.0, 2.0))
    f = lambda x, y: y - y * y
    frame(p)
    slope_field(p, f, nx=21, ny=13, seg=12.0, opacity=0.55)
    p.axes(range(-2, 6), [-1, 0, 1, 2], xlabel="x", ylabel="y", xfmt=num, yfmt=num)

    # equilibrium solutions
    for yc in (0.0, 1.0):
        p.line([(p.xmin, yc), (p.xmax, yc)], color=PRACTICE, width=2.4)

    # solution curves through (0, y0), each drawn only on the branch that contains x = 0
    for y0 in (0.05, 0.25, 0.6, 1.5, -0.05, -0.3):
        C = 1.0 / y0 - 1.0
        lo, hi = p.xmin, p.xmax
        if C < 0:
            xs = math.log(-C)               # 1 + C e^{-x} = 0 here
            if xs < 0:
                lo = xs + 1e-6
            else:
                hi = xs - 1e-6
        graph(p, lambda x, C=C: 1.0 / (1.0 + C * math.exp(-x)), lo, hi, n=360,
              color=THEORY, width=1.9)

    p.label(5.0, 1.0, f"{it('y')} = 1", dx=-4, dy=-8, color=PRACTICE, size=12, anchor="end")
    p.label(5.0, 0.0, f"{it('y')} = 0", dx=-4, dy=-8, color=PRACTICE, size=12, anchor="end")

    svg = figure(W, H, [p],
                 "y' = y − y² denkleminin yön alanı: y = 0 ve y = 1 denge çözümleri ile "
                 "y(0) = 0,05; 0,25; 0,6; 1,5; −0,05; −0,3 başlangıç değerli çözümler.",
                 aria="Direction field of y' = y - y^2 with the equilibrium lines y = 0 and y = 1. "
                      "Solutions starting between 0 and 1 rise towards 1, the one starting at 1.5 falls "
                      "towards 1, and the two starting below 0 fall to minus infinity at a finite x.")
    save(PREFIX, "lojistik", svg)


# ============================================================
# Riccati IVP y' = y^2 + (1 + 2e^x) y + e^{2x}, y(0) = 0
# Particular solution y1 = -e^x; IVP solution y = -e^x + e^x/(2 - e^x),
# which exists on (-inf, ln 2) and tends to +inf as x -> ln 2.
# ============================================================
def riccati_blowup():
    W, H = 540, 340
    p = Plot(52, 26, 430, 262, (-3.0, 1.5), (-4.0, 4.0))
    f = lambda x, y: y * y + (1 + 2 * math.exp(x)) * y + math.exp(2 * x)
    frame(p)
    slope_field(p, f, nx=19, ny=13, seg=11.0, opacity=0.45)
    p.axes([-3, -2, -1, 0, 1], [-4, -2, 0, 2, 4], xlabel="x", ylabel="y", xfmt=num, yfmt=num)

    ln2 = math.log(2.0)
    p.vline(ln2, p.ymin, p.ymax, color=TEXT, dash="5 4", opacity=0.6)
    graph(p, lambda x: -math.exp(x), p.xmin, p.xmax, n=200, color=REMARK, width=2.0, dash="7 4")
    graph(p, lambda x: -math.exp(x) + math.exp(x) / (2.0 - math.exp(x)), p.xmin, ln2 - 1e-6,
          n=420, color=THEORY, width=2.3)
    p.points([(0.0, 0.0)], color=PRACTICE, r=4.2)

    p.label(ln2, 3.3, f"{it('x')} = ln 2", dx=6, dy=0, size=12)
    p.label(0.0, 0.0, f"{it('y')}(0) = 0", dx=-9, dy=-9, color=PRACTICE, size=12, anchor="end")
    p.label(0.42, -2.95, f"{it('y')}<tspan font-size=\"10\" dy=\"3\">1</tspan><tspan dy=\"-3\">&#8202; = {MINUS}e</tspan>"
            + sup(it("x"), size=10), dx=0, dy=0, color=REMARK, size=12, anchor="end")
    p.label(0.40, 2.5, "aranan çözüm", dx=0, dy=0, color=THEORY, size=12, anchor="end")

    svg = figure(W, H, [p],
                 "Riccati başlangıç değer probleminin çözümü x = ln 2'de sonsuza kaçar; "
                 "kesikli eğri özel çözüm y₁ = −eˣ.",
                 aria="Direction field of the Riccati equation y' = y^2 + (1 + 2e^x) y + e^(2x). "
                      "The dashed curve is the particular solution y1 = -e^x. The solution with y(0) = 0 "
                      "approaches 0 on the left, dips slightly below 0, passes through (0, 0) and goes "
                      "to plus infinity at the dashed vertical line x = ln 2.")
    save(PREFIX, "riccati-patlama", svg)


if __name__ == "__main__":
    logistic()
    riccati_blowup()
