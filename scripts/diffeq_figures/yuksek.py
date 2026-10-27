# -*- coding: utf-8 -*-
"""
Figures of the chapter "Yüksek Mertebe Lineer Denklemler"
(dersler/diferansiyel-denklemler/yuksek-mertebe-lineer-denklemler.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution,
exercise or callout), never inside a definition box and never directly under
a heading. The figures are NOT produced at build time. Run

    python scripts/diffeq_figures/yuksek.py
    python scripts/center_figures.py "diffeq-yuksek-*.md"
    python scripts/check_figure_labels.py "scripts/_figures/diffeq-yuksek-*.md"

and paste the markup of scripts/_figures/diffeq-yuksek-<name>.md into the .qmd.
The captions are Turkish on purpose; the aria labels are plain ASCII.

The curves come from two exercises of the chapter, so the numbers match the
boxes exactly:
  y'''' + 8y'' + 16y = 0   (roots +-2i, each double)  ->  basis cos 2x, x cos 2x, ...
  y''' - 3y' + 2y = 0,  y(0) = 0, y'(0) = 0, y''(0) = 9  ->  y = (3x - 1)e^x + e^(-2x)
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import save, graph  # noqa: E402
from svg_plot import Plot, figure, sup, BASE, PRACTICE, TEXT, THEORY  # noqa: E402

PREFIX = "diffeq-yuksek-"
MINUS = "&#8722;"
PRIME = "&#8242;"


def signed(v):
    """Tick label with a typographic minus and a decimal comma."""
    s = f"{abs(v):g}".replace(".", ",")
    return f"{MINUS}{s}" if v < 0 else s


def it(s):
    return f'<tspan font-style="italic">{s}</tspan>'


def zero_line(p):
    p.add(f'<line x1="{p.x0:.1f}" y1="{p.Y(0):.1f}" x2="{p.x0 + p.w:.1f}" y2="{p.Y(0):.1f}" '
          f'stroke="{TEXT}" stroke-width="0.9" opacity="0.35"/>')


# ============================================================
# Double complex roots: cos 2x stays bounded, x cos 2x grows linearly
# ============================================================
def double_complex():
    p = Plot(52, 26, 400, 250, (0.0, 9.0), (-9.6, 9.6))
    zero_line(p)
    p.axes(xticks=[0, 2, 4, 6, 8], yticks=[-8, -4, 0, 4, 8], xlabel="x", ylabel="y", xfmt=signed, yfmt=signed)
    graph(p, lambda x: x, 0.0, 9.0, color=TEXT, width=1.2, dash="5 4", opacity=0.6)
    graph(p, lambda x: -x, 0.0, 9.0, color=TEXT, width=1.2, dash="5 4", opacity=0.6)
    graph(p, lambda x: math.cos(2 * x), 0.0, 9.0, n=500, color=BASE, width=1.7)
    graph(p, lambda x: x * math.cos(2 * x), 0.0, 9.0, n=500, color=THEORY, width=2.3)
    # labels
    p.label(2 * math.pi, 2 * math.pi, it("x") + " cos 2" + it("x"), dx=0, dy=-12, color=THEORY, size=12,
            anchor="middle")
    p.label(0.3, 1.0, "cos 2" + it("x"), dx=0, dy=-12, color=BASE, size=12)
    p.label(8.55, 8.55, it("y") + " = " + it("x"), dx=-6, dy=-8, color=TEXT, size=11.5, anchor="end")
    p.label(2.2, -2.2, it("y") + " = " + MINUS + it("x"), dx=0, dy=22, color=TEXT, size=11.5, anchor="end")

    em = lambda s: f"<em>{s}</em>"
    caption = (
        "İki katlı ±2" + em("i") + " köklerinin etkisi. Basit bir kökten de gelebilecek cos 2" + em("x")
        + " çözümü −1 ile 1 arasında kalır; kökün iki katlı olmasıyla temel çözüm kümesine giren "
        + em("x") + " cos 2" + em("x") + " ise kesikli " + em("y") + " = ±" + em("x")
        + " doğruları arasında salınır, yani genliği " + em("x") + " ile doğrusal büyür."
    )
    return figure(
        480, 300, [p], caption,
        aria="Graphs of cos 2x, bounded between -1 and 1, and x cos 2x, which oscillates between the "
             "dashed lines y = x and y = -x, for x from 0 to 9.",
    )


# ============================================================
# Third-order IVP: y = (3x - 1)e^x + e^(-2x) through (0, 0)
# ============================================================
def third_order_ivp():
    f = lambda x: (3 * x - 1) * math.exp(x) + math.exp(-2 * x)
    p = Plot(52, 26, 400, 250, (-1.0, 1.1), (-0.8, 7.6))
    zero_line(p)
    p.axes(xticks=[-1, -0.5, 0, 0.5, 1], yticks=[0, 2, 4, 6], xlabel="x", ylabel="y", xfmt=signed, yfmt=signed)
    graph(p, f, -1.0, 1.1, n=500, color=THEORY, width=2.3)
    # horizontal tangent at the initial point
    p.line([(-0.32, 0.0), (0.32, 0.0)], color=PRACTICE, width=1.8, dash="5 3")
    p.points([(0, 0)], color=PRACTICE, r=4.2)
    p.label(0.0, 0.0, "(0, 0)", dx=8, dy=17, color=PRACTICE, size=11.5)
    p.label(0.62, f(0.62), it("y") + " = (3" + it("x") + " " + MINUS + " 1)" + it("e") + sup(it("x"), 10)
            + " + " + it("e") + sup(MINUS + "2" + it("x"), 10),
            dx=-10, dy=-4, color=THEORY, size=12, anchor="end")

    em = lambda s: f"<em>{s}</em>"
    caption = (
        "Başlangıç değer probleminin tek çözümü " + em("y") + " = (3" + em("x") + " − 1)" + em("e")
        + "<sup>" + em("x") + "</sup> + " + em("e") + "<sup>−2" + em("x") + "</sup>. Eğri (0, 0) "
        "noktasından " + em("y") + "′(0) = 0 gereği yatay teğetle (kesikli) geçer ve " + em("y")
        + "″(0) = 9 &gt; 0 olduğundan orada yukarı doğru bükülür."
    )
    return figure(
        480, 300, [p], caption,
        aria="Graph of y = (3x - 1)e^x + e^(-2x) for x from -1 to 1.1. The curve passes through the "
             "marked initial point (0, 0) with a dashed horizontal tangent and bends upward there.",
    )


if __name__ == "__main__":
    save(PREFIX, "katli-sanal", double_complex())
    save(PREFIX, "bdp", third_order_ivp())
