# -*- coding: utf-8 -*-
"""
Figures of the chapter "Diferansiyel Denklemler: Kavram ve Sınıflandırma"
(dersler/diferansiyel-denklemler/siniflandirma.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box and never directly under a heading.
The figures are NOT produced at build time. Run

    python scripts/diffeq_figures/sinif.py
    python scripts/center_figures.py "diffeq-sinif-*.md"
    python scripts/check_figure_labels.py "scripts/_figures/diffeq-sinif-*.md"

and paste the markup of scripts/_figures/diffeq-sinif-<name>.md into the .qmd.
The captions are Turkish on purpose; the aria labels are plain ASCII.

Figures:
  sarkac-sinus  sin(theta) against the line theta: the nonlinear term of the
                pendulum equation and its small-angle approximation
                (exm-sinif-lineer-sarkac)
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import save, graph  # noqa: E402
from svg_plot import Plot, figure, BASE, PRACTICE, THEORY  # noqa: E402

PREFIX = "diffeq-sinif-"
MINUS, PI_S, THETA = "&#8722;", "&#960;", "&#952;"


def it(s):
    """Italic math letter inside an SVG <text>."""
    return f'<tspan font-style="italic">{s}</tspan>'


# ============================================================
# sarkac-sinus: sin(theta) versus theta
# ============================================================
def pendulum_sine():
    W, H = 520, 290
    p = Plot(50, 26, 420, 220, (-math.pi, math.pi + 0.35), (-2.1, 2.1))
    names = {round(-math.pi, 6): f"{MINUS}{PI_S}", round(-math.pi / 2, 6): f"{MINUS}{PI_S}/2",
             round(math.pi / 2, 6): f"{PI_S}/2", round(math.pi, 6): PI_S}
    p.origin_axes(xlabel=it(THETA), ylabel="y", xticks=[-math.pi, -math.pi / 2, math.pi / 2, math.pi],
                  yticks=[-1, 1], xfmt=lambda v: names[round(v, 6)],
                  yfmt=lambda v: f"{v:g}".replace("-", MINUS))
    # band of small angles where the two graphs are hard to tell apart
    p.polygon([(-0.5, -2.1), (0.5, -2.1), (0.5, 2.1), (-0.5, 2.1)], fill=PRACTICE, opacity=0.10)
    graph(p, lambda t: t, -math.pi, math.pi, color=BASE, width=1.7, dash="6 4")
    graph(p, math.sin, -math.pi, math.pi, color=THEORY, width=2.3)
    p.label(1.62, 1.62, it(THETA), dx=10, dy=4, color=BASE, size=12)
    p.label(2.35, math.sin(2.35), f"sin {it(THETA)}", dx=4, dy=-10, color=THEORY, size=12)
    caption = ("y = sin θ eğrisi (düz) ile y = θ doğrusu (kesikli). Sıfıra yakın açılarda (gölgeli şerit, "
               "|θ| ≤ 0,5) iki grafik neredeyse çakışır; açı büyüdükçe sin θ doğrudan ayrılır ve "
               "bükülür. Lineer bir terim, bilinmeyenin sabit bir katı olduğundan grafiği hep "
               "orijinden geçen bir doğrudur.")
    aria = ("Graph of sin(theta) and of the line theta on [-pi, pi]; they nearly coincide on the "
            "shaded band where |theta| is at most 0.5 and separate for larger angles.")
    return figure(W, H, [p], caption, aria=aria)


if __name__ == "__main__":
    save(PREFIX, "sarkac-sinus", pendulum_sine())
