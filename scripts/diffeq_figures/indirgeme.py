# -*- coding: utf-8 -*-
"""
Figures of the chapter "Mertebe İndirgeme"
(dersler/diferansiyel-denklemler/mertebe-indirgeme.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box and never directly under a heading.
The figures are NOT produced at build time. Run

    python scripts/diffeq_figures/indirgeme.py
    python scripts/center_figures.py "diffeq-indirgeme-*.md"
    python scripts/check_figure_labels.py "scripts/_figures/diffeq-indirgeme-*.md"

and paste the markup of scripts/_figures/diffeq-indirgeme-<name>.md into the .qmd.
The captions are Turkish on purpose; the aria labels are plain ASCII.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import save, graph  # noqa: E402
from svg_plot import Plot, figure, BASE, PRACTICE, TEXT, THEORY  # noqa: E402

PREFIX = "diffeq-indirgeme-"
MINUS = "&#8722;"


def it(s):
    """Italic math letter inside an SVG <text>."""
    return f'<tspan font-style="italic">{s}</tspan>'


def num(v):
    return f"{v:g}".replace("-", MINUS)


# ============================================================
# Blow-up of the IVP y'' = 2 y y', y(0) = 1, y'(0) = 1: y = 1/(1 - x)
# ============================================================
def blow_up():
    W, H = 560, 380
    p = Plot(56, 28, 450, 300, (-3, 3), (-2.5, 6))
    p.origin_axes(xlabel="x", ylabel="y",
                  xticks=(-3, -2, -1, 1, 2), yticks=(-2, -1, 2, 3, 4, 5),
                  xfmt=num, yfmt=num)
    # vertical asymptote x = 1
    p.vline(1, -2.5, 6, color=TEXT, dash="5 4", opacity=0.55)
    p.label(1, 5.75, f"{it('x')} = 1", dx=7, dy=4, size=11.5)
    # the other branch of the same formula (not part of the IVP solution)
    graph(p, lambda x: 1 / (1 - x), 1.02, 3, color=BASE, width=1.5, dash="5 4", opacity=0.6)
    # the solution on (-inf, 1)
    graph(p, lambda x: 1 / (1 - x), -3, 0.985, n=600, color=THEORY, width=2.2)
    # tangent with slope y'(0) = 1 at the initial point
    p.line([(-0.9, 0.1), (0.9, 1.9)], color=PRACTICE, width=1.4, dash="4 3", opacity=0.9)
    p.points([(0, 1)], color=PRACTICE, r=4.2)
    p.label(0, 1, "(0, 1)", dx=9, dy=19, size=11.5, color=PRACTICE)
    p.label(-2.9, 1.35, f"{it('y')} = 1/(1 {MINUS} {it('x')})", size=12, color=THEORY)
    caption = ("y'' = 2yy', y(0) = 1, y'(0) = 1 probleminin çözümü y = 1/(1 − x). "
               "Eğri (0, 1) noktasından eğimi 1 olan kesikli teğetle çıkar ve x soldan 1'e "
               "yaklaşırken sonsuza gider; çözüm yalnız (−∞, 1) aralığında yaşar. Soluk kesikli "
               "eğri aynı formülün x > 1 dalıdır ve bu problemin çözümüne ait değildir.")
    aria = ("Graph of y = 1/(1 - x) for x below 1 through the initial point (0, 1) with a tangent "
            "of slope 1; the curve rises to infinity at the vertical asymptote x = 1, and the "
            "faded branch for x above 1 is not part of the solution.")
    save(PREFIX, "patlama", figure(W, H, [p], caption, aria=aria))


if __name__ == "__main__":
    blow_up()
