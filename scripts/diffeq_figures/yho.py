# -*- coding: utf-8 -*-
"""
Figures of the chapter "Yüksek Mertebe Homojen Olmayan Denklemler"
(dersler/diferansiyel-denklemler/yuksek-mertebe-homojen-olmayan-denklemler.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box and never directly under a heading.
The figures are NOT produced at build time. Run

    python scripts/diffeq_figures/yho.py
    python scripts/center_figures.py "diffeq-yho-*.md"
    python scripts/check_figure_labels.py "scripts/_figures/diffeq-yho-*.md"

and paste the markup of scripts/_figures/diffeq-yho-<name>.md into the .qmd.
The captions are Turkish on purpose; the aria labels are plain ASCII.
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import save, graph  # noqa: E402
from svg_plot import Plot, figure, BASE, PRACTICE, TEXT, THEORY, MINUS  # noqa: E402

PREFIX = "diffeq-yho-"


def it(s):
    """Italic math letter inside an SVG <text>."""
    return f'<tspan font-style="italic">{s}</tspan>'


def sup(s):
    """Small raised exponent."""
    return f'<tspan baseline-shift="super" font-size="8.5">{s}</tspan>'


def num(v):
    return f"{v:g}".replace("-", MINUS)


# ============================================================
# IVP y''' - y' = 2x, y(0) = 0, y'(0) = 0, y''(0) = 2  ->  y = 4 cosh x - 4 - x^2
# compared with the parabola y = x^2 built from the initial data
def fig_bdp():
    W, H = 440, 330
    p = Plot(40, 24, 360, 268, (-2.2, 2.2), (-1.0, 9.0))
    p.grid(xs=(-2, -1, 1, 2), ys=(2, 4, 6, 8))
    p.origin_axes(xlabel="x", ylabel="y", xticks=(-2, -1, 1, 2), yticks=(2, 4, 6, 8), xfmt=num, yfmt=num)

    def sol(x):
        return 4 * math.cosh(x) - 4 - x * x

    graph(p, lambda x: x * x, -2.2, 2.2, color=BASE, width=1.7, dash="6 4")
    graph(p, sol, -2.2, 2.2, color=THEORY, width=2.2)
    p.points([(0, 0)], color=PRACTICE, r=4.2)

    p.label(1.78, 7.55, f"{it('y')} = 4 cosh {it('x')} {MINUS} 4 {MINUS} {it('x')}{sup('2')}",
            color=THEORY, size=11.5, anchor="end")
    p.label(1.72, 2.35, f"{it('y')} = {it('x')}{sup('2')}", color=BASE, size=11.5)
    p.label(0, 0, "(0, 0)", dx=8, dy=-8, color=PRACTICE, size=11)
    caption = ("Başlangıç değer probleminin çözümü (düz çizgi) ve başlangıç verilerinin belirlediği "
               "y = x² parabolü (kesikli çizgi). İkisi başlangıç noktasında aynı değeri, aynı eğimi ve "
               "aynı ikinci türevi taşır; bu yüzden orada neredeyse çakışırlar.")
    aria = ("Graph of the solution y = 4 cosh x - 4 - x^2 of the initial value problem together with the "
            "dashed parabola y = x^2; both pass through the origin with zero slope and second derivative 2.")
    save(PREFIX, "bdp", figure(W, H, [p], caption, aria=aria))


if __name__ == "__main__":
    fig_bdp()
