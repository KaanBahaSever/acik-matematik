# -*- coding: utf-8 -*-
"""
Figures of the chapter "Sabit Katsayılı Homojen Denklemler"
(dersler/diferansiyel-denklemler/sabit-katsayili-homojen-denklemler.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution,
exercise or callout), never inside a definition box and never directly under
a heading. The figures are NOT produced at build time. Run

    python scripts/diffeq_figures/karakteristik.py
    python scripts/center_figures.py "diffeq-karakteristik-*.md"
    python scripts/check_figure_labels.py "scripts/_figures/diffeq-karakteristik-*.md"

and paste the markup of scripts/_figures/diffeq-karakteristik-<name>.md into the .qmd.
The captions are Turkish on purpose; the aria labels are plain ASCII.

Every curve is the solution of an initial value problem solved in the chapter,
so the numbers in the figure match the boxes exactly:
  y'' - y = 0,           y(0) = 3/2, y'(0) = 5/2   ->  y = 2e^x - (1/2)e^(-x)
  u'' + u' + u/4 = 0,    u(0) = 3,   u'(0) = -3/4  ->  u = (3 + 3t/4)e^(-t/2)
  4y'' + 4y' + 17y = 0,  y(0) = 2,   y'(0) = -1    ->  y = 2e^(-x/2) cos 2x
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import save, graph  # noqa: E402
from svg_plot import Plot, figure, sup, BASE, PRACTICE, TEXT, THEORY, WIDE  # noqa: E402

PREFIX = "diffeq-karakteristik-"
MINUS = "&#8722;"
PRIME = "&#8242;"
HALF = "&#189;"


def signed(v):
    return f"{MINUS}{abs(v):g}" if v < 0 else f"{v:g}"


def zero_lines(p, vertical=False):
    """Faint y = 0 line (and x = 0 line) inside an L-axes panel."""
    p.add(f'<line x1="{p.x0:.1f}" y1="{p.Y(0):.1f}" x2="{p.x0 + p.w:.1f}" y2="{p.Y(0):.1f}" '
          f'stroke="{TEXT}" stroke-width="0.9" opacity="0.35"/>')
    if vertical:
        p.add(f'<line x1="{p.X(0):.1f}" y1="{p.y0:.1f}" x2="{p.X(0):.1f}" y2="{p.y0 + p.h:.1f}" '
              f'stroke="{TEXT}" stroke-width="0.9" opacity="0.35"/>')


def heading(p, title, equation):
    """Bold case name and the equation, centred above the panel."""
    cx = p.x0 + p.w / 2
    p.text_px(cx, p.y0 - 38, title, TEXT, 12, "middle", True)
    p.text_px(cx, p.y0 - 21, equation, TEXT, 11, "middle")


# ============================================================
# The three root cases side by side
# ============================================================
def three_cases():
    W_PANEL, H_PANEL, Y0 = 172, 150, 56

    # -- distinct real roots: y'' - y = 0 ---------------------------------
    p1 = Plot(44, Y0, W_PANEL, H_PANEL, (-2.0, 1.5), (-4.0, 8.0))
    zero_lines(p1, vertical=True)
    p1.axes(xticks=[-2, -1, 0, 1], yticks=[-4, 0, 4, 8], xlabel="x", ylabel="y", xfmt=signed, yfmt=signed)
    graph(p1, lambda x: 2 * math.exp(x), -2.0, 1.5, n=180, color=BASE, width=1.5, dash="5 4")
    graph(p1, lambda x: -0.5 * math.exp(-x), -2.0, 1.5, n=180, color=PRACTICE, width=1.5, dash="5 4")
    graph(p1, lambda x: 2 * math.exp(x) - 0.5 * math.exp(-x), -2.0, 1.5, n=180, color=THEORY, width=2.3)
    p1.points([(0, 1.5)], color=THEORY, r=3.6)
    p1.label(-1.95, 2 * math.exp(-1.95), "2e" + sup("x"), dx=2, dy=-9, color=BASE, size=11.5)
    p1.label(0.35, -0.5 * math.exp(-0.35), MINUS + HALF + "e" + sup(MINUS + "x"), dx=0, dy=17,
             color=PRACTICE, size=11.5)
    heading(p1, "Farklı gerçel kökler", "y" + PRIME * 2 + " " + MINUS + " y = 0")

    # -- double root: u'' + u' + u/4 = 0 -----------------------------------
    p2 = Plot(274, Y0, W_PANEL, H_PANEL, (0.0, 12.0), (0.0, 4.0))
    p2.axes(xticks=[0, 4, 8, 12], yticks=[0, 1, 2, 3, 4], xlabel="t", ylabel="u")
    graph(p2, lambda t: 3 * math.exp(-t / 2), 0.0, 12.0, n=180, color=BASE, width=1.5, dash="5 4")
    graph(p2, lambda t: (3 + 0.75 * t) * math.exp(-t / 2), 0.0, 12.0, n=180, color=THEORY, width=2.3)
    p2.points([(0, 3)], color=THEORY, r=3.6)
    p2.label(2.6, 3 * math.exp(-1.3), "3e" + sup(MINUS + "t/2"), dx=-4, dy=18, color=BASE, size=11.5,
             anchor="end")
    p2.label(4.0, (3 + 3.0) * math.exp(-2.0), "(3 + 3t/4)e" + sup(MINUS + "t/2"), dx=4, dy=-8,
             color=THEORY, size=11.5)
    heading(p2, "Katlı kök", "u" + PRIME * 2 + " + u" + PRIME + " + u/4 = 0")

    # -- complex roots: 4y'' + 4y' + 17y = 0 ---------------------------------
    p3 = Plot(504, Y0, W_PANEL, H_PANEL, (0.0, 8.0), (-2.4, 2.4))
    zero_lines(p3)
    p3.axes(xticks=[0, 2, 4, 6, 8], yticks=[-2, 0, 2], xlabel="x", ylabel="y", xfmt=signed, yfmt=signed)
    graph(p3, lambda x: 2 * math.exp(-x / 2), 0.0, 8.0, n=180, color=BASE, width=1.5, dash="5 4")
    graph(p3, lambda x: -2 * math.exp(-x / 2), 0.0, 8.0, n=180, color=BASE, width=1.5, dash="5 4")
    graph(p3, lambda x: 2 * math.exp(-x / 2) * math.cos(2 * x), 0.0, 8.0, n=360, color=THEORY, width=2.3)
    p3.points([(0, 2)], color=THEORY, r=3.6)
    p3.label(2.1, 2 * math.exp(-1.05), "2e" + sup(MINUS + "x/2"), dx=2, dy=-7, color=BASE, size=11.5)
    p3.label(2.5, -2 * math.exp(-1.25), MINUS + "2e" + sup(MINUS + "x/2"), dx=2, dy=17, color=BASE,
             size=11.5)
    heading(p3, "Kompleks kökler", "4y" + PRIME * 2 + " + 4y" + PRIME + " + 17y = 0")

    em = lambda s: f"<em>{s}</em>"
    caption = (
        "Her kök türünden, bu bölümde çözülen birer başlangıç değer problemi. Solda " + em("y") + "″ − " + em("y") + " = 0 için "
        + em("y") + " = 2" + em("e") + "<sup>" + em("x") + "</sup> − ½" + em("e") + "<sup>−" + em("x")
        + "</sup> (düz) ve onu oluşturan iki terim (kesikli): " + em("x") + " büyürken birinci, küçülürken "
        "ikinci terim baskındır. Ortada " + em("u") + " = (3 + 3" + em("t") + "/4)" + em("e")
        + "<sup>−" + em("t") + "/2</sup> çözümü, karşılaştırma için kesikli 3" + em("e") + "<sup>−"
        + em("t") + "/2</sup> eğrisiyle: " + em("t") + " çarpanlı terim sönümü yavaşlatır ama "
        "sonunda üstel çarpan kazanır. Sağda " + em("y") + " = 2" + em("e") + "<sup>−" + em("x")
        + "/2</sup> cos 2" + em("x") + " sönümlü salınımı ve onu saran ±2" + em("e") + "<sup>−"
        + em("x") + "/2</sup> zarfı. Dolu noktalar başlangıç değerleridir."
    )
    return figure(
        700, 232, [p1, p2, p3], caption, css_class=WIDE,
        aria="Three panels. Left: y = 2e^x - (1/2)e^(-x) for y'' - y = 0 with the dashed terms 2e^x and "
             "-(1/2)e^(-x). Middle: u = (3 + 3t/4)e^(-t/2) for u'' + u' + u/4 = 0 with dashed 3e^(-t/2). "
             "Right: damped oscillation y = 2e^(-x/2) cos 2x for 4y'' + 4y' + 17y = 0 between the dashed "
             "envelopes plus and minus 2e^(-x/2).",
    )


if __name__ == "__main__":
    save(PREFIX, "uc-durum", three_cases())
