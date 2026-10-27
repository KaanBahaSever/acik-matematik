# -*- coding: utf-8 -*-
"""
Figures of the chapter "İkinci Mertebe Lineer Denklemler"
(dersler/diferansiyel-denklemler/ikinci-mertebe-lineer-denklemler.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box and never directly under a heading.
The figures are NOT produced at build time. Run

    python scripts/diffeq_figures/ikinci.py
    python scripts/center_figures.py "diffeq-ikinci-*.md"
    python scripts/check_figure_labels.py "scripts/_figures/diffeq-ikinci-*.md"

and paste the markup of scripts/_figures/diffeq-ikinci-<name>.md into the .qmd.
The captions are Turkish on purpose; the aria labels are plain ASCII.
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import save, graph  # noqa: E402
from svg_plot import Plot, figure, sup, BASE, PRACTICE, TEXT, THEORY  # noqa: E402

PREFIX = "diffeq-ikinci-"
MINUS, PI_S = "&#8722;", "&#960;"


def pi_ticks(t):
    """Tick labels for multiples of pi/2."""
    k = round(t / (math.pi / 2))
    table = {-2: MINUS + PI_S, -1: MINUS + PI_S + "/2", 0: "0", 1: PI_S + "/2", 2: PI_S}
    return table.get(k, "")


def num(t):
    """Tick label with a decimal comma and a true minus sign."""
    s = f"{t:g}"
    return s.replace("-", MINUS).replace(".", ",")


# ============================================================
# Proportional solutions: the family C cos x cannot meet y(0)=3, y'(0)=5
# ============================================================
def proportional():
    W, H = 470, 310
    p = Plot(48, 26, 384, 248, (-math.pi - 0.15, math.pi + 0.15), (-6.6, 6.6))
    p.origin_axes("x", "y", xticks=[-math.pi, math.pi], yticks=[-6, 6], xfmt=pi_ticks, yfmt=num)
    for c in (-3, -2, -1, 1, 2):
        graph(p, lambda t, c=c: c * math.cos(t), p.xmin, p.xmax, color=BASE, width=1.1, opacity=0.45)
    graph(p, lambda t: 3 * math.cos(t), p.xmin, p.xmax, color=BASE, width=1.9, dash="6 4")
    graph(p, lambda t: 3 * math.cos(t) + 5 * math.sin(t), p.xmin, p.xmax, color=THEORY, width=2.3)
    # tangent directions at the initial point
    p.line([(-0.55, 3), (0.55, 3)], color=BASE, width=1.6)
    p.line([(-0.42, 3 - 5 * 0.42), (0.42, 3 + 5 * 0.42)], color=PRACTICE, width=1.6, dash="3 3")
    p.points([(0, 3)], color=PRACTICE, r=4.2)
    p.label(0, 3, "(0, 3)", dx=-8, dy=-8, anchor="end", color=PRACTICE)
    p.label(0.25, 4.25, "eğim 5", dx=-10, dy=0, anchor="end", color=PRACTICE, size=11)
    p.label(0.55, 3, "eğim 0", dx=6, dy=-6, color=BASE, size=11)
    # legend in the empty lower-right corner
    rows = [(-4.3, "3 cos x + 5 sin x", dict(color=THEORY, width=2.3)),
            (-5.25, "3 cos x", dict(color=BASE, width=1.9, dash="6 4")),
            (-6.2, "C cos x", dict(color=BASE, width=1.1, opacity=0.6))]
    for yy, text, style in rows:
        p.line([(1.15, yy), (1.55, yy)], **style)
        p.label(1.62, yy, text, dx=0, dy=4, color=style["color"], size=11.5)
    cap = ("y = C cos x ailesinin (0, 3) noktasından geçen tek üyesi 3 cos x'tir ve bu eğrinin o noktadaki "
           "eğimi 0'dır. Eğimi 5 olan 3 cos x + 5 sin x çözümü ailenin hiçbir üyesine eşit değildir.")
    aria = "Family C cos x and the solution 3 cos x + 5 sin x through the point (0, 3) with slope 5"
    save(PREFIX, "orantili", figure(W, H, [p], cap, aria=aria))


# ============================================================
# IVP of y'' - 4y = 0 with y(0) = 1, y'(0) = -4
# ============================================================
def exponential_ivp():
    W, H = 470, 310
    p = Plot(48, 26, 384, 248, (-0.65, 1.05), (-4.2, 5.6))
    p.origin_axes("x", "y", xticks=[-0.5, 0.5, 1], yticks=[-4, -2, 2, 4], xfmt=num, yfmt=num)
    graph(p, lambda t: 1.5 * math.exp(-2 * t), p.xmin, p.xmax, color=BASE, width=1.4, dash="5 4", opacity=0.8)
    graph(p, lambda t: -0.5 * math.exp(2 * t), p.xmin, p.xmax, color=BASE, width=1.4, dash="5 4", opacity=0.8)
    graph(p, lambda t: -0.5 * math.exp(2 * t) + 1.5 * math.exp(-2 * t), p.xmin, p.xmax, color=THEORY, width=2.3)
    p.line([(-0.28, 1 + 4 * 0.28), (0.28, 1 - 4 * 0.28)], color=PRACTICE, width=1.6, dash="3 3")
    p.points([(0, 1)], color=PRACTICE, r=4.2)
    p.label(0, 1, "(0, 1)", dx=-8, dy=16, anchor="end", color=PRACTICE)
    p.label(-0.63, 2.55, "y(x)", dx=0, dy=0, color=THEORY, size=11.5, italic=True)
    p.label(0.62, 1.5 * math.exp(-1.24), "(3/2) e" + sup(MINUS + "2x", 10), dx=0, dy=-10, color=BASE, size=11.5)
    p.label(-0.35, -0.5 * math.exp(-0.7), MINUS + "(1/2) e" + sup("2x", 10), dx=0, dy=24, anchor="middle",
            color=BASE, size=11.5)
    cap = ("y = " + MINUS + "(1/2) e<sup>2x</sup> + (3/2) e<sup>" + MINUS + "2x</sup> çözümü (0, 1) noktasından "
           + MINUS + "4 eğimiyle geçer; o noktadaki kısa kesikli doğru teğettir. Uzun kesikli eğriler, bu çözümü oluşturan (3/2) e<sup>" + MINUS
           + "2x</sup> ve " + MINUS + "(1/2) e<sup>2x</sup> terimleridir.")
    aria = "Solution of y'' - 4y = 0 through (0, 1) with slope -4 and its two exponential terms"
    save(PREFIX, "ustel-bdp", figure(W, H, [p], cap, aria=aria))


# ============================================================
# x^2 and x|x|: the interval decides linear dependence
# ============================================================
def interval():
    W, H = 470, 310
    p = Plot(48, 26, 384, 248, (-1.08, 1.08), (-1.15, 1.15))
    p.origin_axes("x", "y", xticks=[-1, -0.5, 0.5, 1], yticks=[-1, 1], xfmt=num, yfmt=num)
    p.polygon([(0, -1.15), (1, -1.15), (1, 1.15), (0, 1.15)], fill=THEORY, opacity=0.07)
    graph(p, lambda t: t * t, -1, 1, color=THEORY, width=2.3)
    graph(p, lambda t: t * abs(t), -1, 1, color=PRACTICE, width=2.0, dash="6 4")
    p.label(-0.5, 0.55, "y = x" + sup("2", 10), dx=0, dy=0, anchor="middle", color=THEORY)
    p.label(-0.5, -0.62, "y = x|x|", dx=0, dy=0, anchor="middle", color=PRACTICE)
    p.label(0.5, -0.62, "(0, 1) aralığında", dx=0, dy=0, anchor="middle", color=TEXT, size=11)
    p.label(0.5, -0.62, "iki grafik çakışır", dx=0, dy=15, anchor="middle", color=TEXT, size=11)
    cap = ("x<sup>2</sup> ile x|x| fonksiyonları (0, 1) aralığında aynıdır, ("
           + MINUS + "1, 0) aralığında ise birbirinin ters işaretlisidir. Bu yüzden (0, 1) üzerinde "
           "lineer bağımlı, (" + MINUS + "1, 1) üzerinde lineer bağımsızdırlar.")
    aria = "Graphs of x^2 and x|x| on (-1, 1); they coincide on (0, 1)"
    save(PREFIX, "aralik", figure(W, H, [p], cap, aria=aria))


if __name__ == "__main__":
    proportional()
    exponential_ivp()
    interval()
