# -*- coding: utf-8 -*-
"""
Figures of the chapter "Wronskiyen ve Lineer Bağımsızlık"
(dersler/diferansiyel-denklemler/wronskiyen-ve-lineer-bagimsizlik.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box and never directly under a heading.
The figures are NOT produced at build time. Run

    python scripts/diffeq_figures/wronski.py
    python scripts/center_figures.py "diffeq-wronski-*.md"
    python scripts/check_figure_labels.py "scripts/_figures/diffeq-wronski-*.md"

and paste the markup of scripts/_figures/diffeq-wronski-<name>.md into the .qmd.
The captions are Turkish on purpose; the aria labels are plain ASCII.
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import save, graph, frame  # noqa: E402
from svg_plot import Plot, figure, BASE, PRACTICE, TEXT, THEORY  # noqa: E402

PREFIX = "diffeq-wronski-"
MINUS = "&#8722;"
PI = "&#960;"


def signed(v):
    return f"{MINUS}{abs(v):g}" if v < 0 else f"{v:g}"


# ============================================================
# x^3 and |x|^3: zero Wronskian, yet independent on the real line
# ============================================================
def cube_and_abs_cube():
    p = Plot(48, 24, 430, 270, (-1.45, 1.45), (-2.9, 2.9))
    p.grid(xs=[0], ys=[0])
    frame(p)
    p.axes(xticks=[-1, 0, 1], yticks=[-2, 0, 2], xlabel="x", ylabel="y", xfmt=signed, yfmt=signed)

    graph(p, lambda x: x**3, -1.45, 1.45, color=THEORY, width=2.4)
    graph(p, lambda x: abs(x)**3, -1.45, 1.45, color=PRACTICE, width=2.4, dash="7 5")

    p.label(-1.25, (-1.25)**3, "y = x³", dx=10, dy=4, color=THEORY, size=12.5, bold=True)
    p.label(-1.25, 1.25**3, "y = |x|³", dx=10, dy=0, color=PRACTICE, size=12.5, bold=True)
    p.label(0.2, -1.5, "x &gt; 0 için |x|³ = x³", color=TEXT, size=12)
    p.label(0.2, -2.2, "x &lt; 0 için |x|³ = " + MINUS + "x³", color=TEXT, size=12)
    p.label(-1.0, 1.0, "(" + MINUS + "1, 1)", dx=9, dy=-8, color=PRACTICE, size=11)
    p.points([(-1, 1), (1, 1)], color=PRACTICE, r=3.8)
    p.points([(-1, -1)], color=THEORY, r=3.8)
    p.label(1.0, 1.0, "(1, 1)", dx=-8, dy=-8, color=TEXT, size=11, anchor="end")
    p.label(-1.0, -1.0, "(" + MINUS + "1, " + MINUS + "1)", dx=8, dy=16, color=THEORY, size=11)
    return figure(
        530, 340, [p],
        "y = x³ (düz) ve y = |x|³ (kesikli) eğrileri. Sağ yarıda iki eğri çakışır, sol yarıda biri "
        "öbürünün x eksenine göre yansımasıdır. Her yarıda birbirinin sabit katıdırlar, ama bütün ℝ "
        "üzerinde aynı sabitle orantılı değildirler: x = 1'de değerler eşit, x = −1'de zıt işaretlidir.",
        aria="Graphs of y = x^3 (solid) and y = |x|^3 (dashed); they coincide for x positive and are "
             "mirror images for x negative",
    )


# ============================================================
# y'' + y = 0: many solutions through (0, 1), one for each slope
# ============================================================
def through_one_point():
    p = Plot(48, 24, 430, 270, (-math.pi, math.pi), (-2.6, 2.6))
    p.grid(xs=[0], ys=[0])
    frame(p)
    p.axes(xticks=[], yticks=[-2, -1, 0, 1, 2], xlabel="x", ylabel="y", yfmt=signed)
    ticks = [(-math.pi, MINUS + PI), (-math.pi / 2, MINUS + PI + "/2"), (0, "0"),
             (math.pi / 2, PI + "/2"), (math.pi, PI)]
    for xv, s in ticks:
        p.text_px(p.X(xv), p.y0 + p.h + 16, s, size=11, anchor="middle")

    def member(k):
        return lambda x: math.cos(x) + k * math.sin(x)

    for k in (-2, -1, 0, 1):
        graph(p, member(k), -math.pi, math.pi, color=BASE, width=1.5, opacity=0.8)
    graph(p, member(2), -math.pi, math.pi, color=PRACTICE, width=2.8)

    xm = math.atan(2.0)
    p.label(xm, member(2)(xm), "k = 2", dx=12, dy=-6, color=PRACTICE, size=12.5, bold=True)
    p.label(-xm, member(-2)(-xm), "k = " + MINUS + "2", dx=-12, dy=-6, color=BASE, size=12, anchor="end")
    p.points([(0, 1)], color=TEXT, r=4.2)
    return figure(
        530, 340, [p],
        "y″ + y = 0 denkleminin (0, 1) noktasından geçen y = cos x + k sin x çözümlerinden bazıları "
        "(k = −2, −1, 0, 1, 2). Hepsi aynı noktadan geçer, ama o noktadaki eğimleri k'dir ve birbirinden "
        "farklıdır. Kalın eğri, y′(0) = 2 koşulunu da sağlayan tek çözümdür: y = cos x + 2 sin x. Eğrilerin "
        "x = ±π'de yeniden buluşması da teklikle çelişmez: oradaki eğimleri −k'dir ve yine birbirinden farklıdır.",
        aria="Five solutions cos x + k sin x of y'' + y = 0 through the point (0, 1) with different "
             "slopes k; the solution with k = 2 is highlighted",
    )


if __name__ == "__main__":
    save(PREFIX, "kup-mutlak", cube_and_abs_cube())
    save(PREFIX, "ayni-nokta", through_one_point())
