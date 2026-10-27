# -*- coding: utf-8 -*-
"""
Figures of the chapter "Birinci Mertebe Lineer Denklemler"
(dersler/diferansiyel-denklemler/birinci-mertebe-lineer-denklemler.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box and never directly under a heading.
The figures are NOT produced at build time. Run

    python scripts/diffeq_figures/lineer.py
    python scripts/center_figures.py "diffeq-lineer-*.md"
    python scripts/check_figure_labels.py "scripts/_figures/diffeq-lineer-*.md"

and paste the markup of scripts/_figures/diffeq-lineer-<name>.md into the .qmd.
The captions are Turkish on purpose; the aria labels are plain ASCII.
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import save, graph, slope_field, frame, linspace, clip_runs  # noqa: E402
from svg_plot import Plot, figure, BASE, PRACTICE, REMARK, TEXT, THEORY  # noqa: E402

PREFIX = "diffeq-lineer-"
MINUS = "&#8722;"


# ============================================================
# Direction field of y' + x y = x e^{x^2/2} with the IVP y(0) = 1
# ============================================================
def ivp_field():
    p = Plot(48, 22, 430, 330, (-2.2, 2.2), (-3.0, 6.0))
    p.grid(xs=[0], ys=[0])
    slope_field(p, lambda x, y: x * math.exp(x * x / 2) - x * y, nx=19, ny=15, seg=12.0, opacity=0.55)
    frame(p)
    p.axes(xticks=[-2, -1, 0, 1, 2], yticks=[-2, 0, 2, 4, 6], xlabel="x", ylabel="y",
           xfmt=lambda v: f"{MINUS}{abs(v):g}" if v < 0 else f"{v:g}",
           yfmt=lambda v: f"{MINUS}{abs(v):g}" if v < 0 else f"{v:g}")

    def member(c):
        return lambda x: math.exp(x * x / 2) / 2 + c * math.exp(-x * x / 2)

    for c in (-3, -2, -1, 0, 2, 3):
        graph(p, member(c), -2.2, 2.2, color=THEORY, width=1.4, opacity=0.8)
    graph(p, member(0.5), -2.2, 2.2, color=PRACTICE, width=2.8)
    p.points([(0, 1)], color=PRACTICE, r=4.2)
    p.label(0, 1, "y(0) = 1", dx=8, dy=17, color=PRACTICE, size=12, bold=True)
    p.label(0.22, 1.5, "y = cosh(x²/2)", color=PRACTICE, size=12)
    p.label(0, member(-3)(0), "c = " + MINUS + "3", dx=-6, dy=16, color=THEORY, size=11, anchor="end")
    p.label(-0.08, member(3)(0), "c = 3", dx=0, dy=-8, color=THEORY, size=11, anchor="end")
    return figure(
        530, 390, [p],
        "y′ + xy = x·e^(x²/2) denkleminin yön alanı ve c = −3, −2, −1, 0, 2, 3 için genel çözüm "
        "ailesinin eğrileri; kalın eğri, y(0) = 1 koşulunu sağlayan y = cosh(x²/2) çözümüdür. Bütün eğriler, "
        "|x| büyüdükçe birbirine yaklaşır.",
        aria="Direction field of y' + x y = x exp(x^2/2) with six members of the general solution "
             "and the solution y = cosh(x^2/2) through (0, 1) highlighted",
    )


# ============================================================
# Curves x = 1/(2y) + c/y^3 of y^2 dx + (3xy - 1) dy = 0, y > 0
# ============================================================
def linear_in_x():
    p = Plot(48, 22, 430, 300, (-1.5, 2.5), (0.0, 2.4))
    p.grid(xs=[0])
    frame(p)
    p.axes(xticks=[-1, 0, 1, 2], yticks=[0, 1, 2], xlabel="x", ylabel="y",
           xfmt=lambda v: f"{MINUS}{abs(v):g}" if v < 0 else f"{v:g}")

    # the hyperbola 3xy = 1 where dy/dx is undefined
    graph(p, lambda x: 1 / (3 * x), 0.05, 2.5, color=REMARK, width=1.5, dash="5 4")
    p.label(1.8, 0.05, "xy = 1/3", color=REMARK, size=11.5)

    def curve(c, color, width, opacity=1.0):
        pts = [(1 / (2 * y) + c / y**3, y) for y in linspace(0.04, 2.4, 900)]
        for run in clip_runs(pts, p):
            p.line(run, color=color, width=width, opacity=opacity)

    for c in (-0.6, -0.04, -0.01, 0.0, 0.03, 0.15, 0.5):
        curve(c, THEORY, 1.4, 0.8)
    c0 = -0.15
    curve(c0, PRACTICE, 2.6)
    yf = math.sqrt(-6 * c0)
    xf = 1 / (3 * yf)
    p.points([(xf, yf)], color=PRACTICE, r=4.2)
    p.label(-1.0, 0.24, "c = " + MINUS + "0,15", dx=0, dy=-10, color=PRACTICE, size=11.5, bold=True)
    return figure(
        530, 360, [p],
        "y² dx + (3xy − 1) dy = 0 denkleminin x = 1/(2y) + c/y³ çözüm eğrilerinden bazıları. c &lt; 0 "
        "olduğunda eğri, kesikli xy = 1/3 hiperbolü üzerinde dikey teğetle geri döner (kalın eğride "
        "işaretli nokta); orada dy/dx tanımsızdır. Böyle bir eğri y'yi x'in bir fonksiyonu olarak vermez, "
        "ama x'i her zaman y'nin bir fonksiyonu olarak verir.",
        aria="Solution curves x = 1/(2y) + c/y^3 for several c in the upper half plane; for negative c "
             "the curves turn back on the dashed hyperbola xy = 1/3",
    )


if __name__ == "__main__":
    save(PREFIX, "yon-alani", ivp_field())
    save(PREFIX, "x-e-gore", linear_in_x())
