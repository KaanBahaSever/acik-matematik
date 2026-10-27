# -*- coding: utf-8 -*-
"""
Figures of the chapter "Değişkenlerine Ayrılabilen Denklemler"
(dersler/diferansiyel-denklemler/degiskenlerine-ayrilabilen-denklemler.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box and never directly under a heading.
The figures are NOT produced at build time. Run

    python scripts/diffeq_figures/ayrilabilen.py
    python scripts/center_figures.py "diffeq-ayrilabilen-*.md"
    python scripts/check_figure_labels.py "scripts/_figures/diffeq-ayrilabilen-*.md"

and paste the markup of scripts/_figures/diffeq-ayrilabilen-<name>.md into the .qmd.
The captions are Turkish on purpose; the aria labels are plain ASCII.

Conventions: the slope field is drawn in the base color, solution curves in
the theory color, the equilibrium solution and the initial point in the
practice color.
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import save, graph, rk4, solution_curve, slope_field, frame  # noqa: E402,F401

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, PRACTICE, THEORY  # noqa: E402

PREFIX = "diffeq-ayrilabilen-"
MINUS, PI = "&#8722;", "&#960;"


def it(s):
    """Italic math letter inside an SVG <text>."""
    return f'<tspan font-style="italic">{s}</tspan>'


def num(v):
    """A tick label with a typographic minus sign."""
    return f"{v:g}".replace("-", MINUS)


def pi_tick(v):
    """Tick label for multiples of pi."""
    n = round(v / math.pi)
    if n == 0:
        return "0"
    s = (MINUS if n < 0 else "") + ("" if abs(n) == 1 else str(abs(n))) + PI
    return s


# ============================================================
# y' = y sin x: slope field, the family y = c e^{-cos x}, equilibrium y = 0
# (exm-ayrilabilen-logaritma)
# ============================================================
def fig_ysin():
    W, H = 560, 320
    p = Plot(48, 22, 452, 262, (-2 * math.pi, 2 * math.pi), (-3.4, 3.4))
    frame(p)
    slope_field(p, lambda x, y: y * math.sin(x), nx=27, ny=15, seg=11.0, opacity=0.55)
    p.axes([-2 * math.pi, -math.pi, 0, math.pi, 2 * math.pi], [-3, -2, -1, 0, 1, 2, 3],
           xlabel="x", ylabel="y", xfmt=pi_tick, yfmt=num)
    for cv in (0.25, 0.5, 1.0, -0.25, -0.5, -1.0):
        graph(p, lambda x, cv=cv: cv * math.exp(-math.cos(x)), p.xmin, p.xmax, color=THEORY, width=1.9)
    # equilibrium solution
    p.line([(p.xmin, 0), (p.xmax, 0)], color=PRACTICE, width=2.6)
    p.label(p.xmax, 0, it("y") + " = 0", dx=7, dy=4, color=PRACTICE, size=12)
    p.label(math.pi, math.e, it("c") + " = 1", dx=0, dy=-8, color=THEORY, size=12, anchor="middle")
    p.label(math.pi, -math.e, it("c") + " = " + MINUS + "1", dx=0, dy=18, color=THEORY, size=12, anchor="middle")
    cap = ("<em>y</em>&#8242; = <em>y</em> sin <em>x</em> denkleminin eğim alanı ve "
           "<em>y</em> = <em>c</em><em>e</em><sup>&#8722;cos <em>x</em></sup> çözüm eğrileri "
           "(<em>c</em> = &#177;1/4, &#177;1/2, &#177;1). <em>c</em> &gt; 0 olan eğriler üst dalda, "
           "<em>c</em> &lt; 0 olanlar alt dalda kalır; aradaki <em>y</em> = 0 doğrusu <em>c</em> = 0 seçimine "
           "karşılık gelen denge çözümüdür ve hiçbir çözüm eğrisi onu kesmez.")
    aria = ("Slope field of y' = y sin x on -2pi to 2pi with six solution curves y = c exp(-cos x), "
            "three above and three below the equilibrium line y = 0, which no curve crosses.")
    save(PREFIX, "ysin", figure(W, H, [p], cap, aria=aria))


# ============================================================
# y' = y^2, y(-3) = 0: the family y = -1/(x + c) never reaches y = 0
# (exm-ayrilabilen-sifir-baslangic)
# ============================================================
def fig_ykare():
    W, H = 540, 320
    p = Plot(48, 22, 452, 262, (-6, 1), (-3, 3))
    frame(p)
    slope_field(p, lambda x, y: y * y, nx=21, ny=15, seg=11.0, opacity=0.55)
    p.axes([-6, -5, -4, -3, -2, -1, 0, 1], [-3, -2, -1, 0, 1, 2, 3],
           xlabel="x", ylabel="y", xfmt=num, yfmt=num)
    for y0 in (0.4, 1.2, -0.4, -1.2):
        solution_curve(p, lambda x, y: y * y, -3, y0, n=900, color=THEORY, width=1.9)
    p.line([(p.xmin, 0), (p.xmax, 0)], color=PRACTICE, width=2.6)
    p.points([(-3, 0)], color=PRACTICE, r=4.6)
    p.label(-3, 0, "(" + MINUS + "3, 0)", dx=8, dy=-6, color=PRACTICE, size=12)
    p.label(0.15, 0, it("y") + " = 0", dx=0, dy=-7, color=PRACTICE, size=12, anchor="middle")
    cap = ("<em>y</em>&#8242; = <em>y</em><sup>2</sup> denkleminin eğim alanı ve (&#8722;3, &#177;0,4), "
           "(&#8722;3, &#177;1,2) noktalarından geçen <em>y</em> = &#8722;1/(<em>x</em> + <em>c</em>) çözümleri. "
           "Bu eğriler <em>x</em> ekseninin üstünde ya da altında kalır, <em>y</em> = 0 doğrusuna yaklaşır ama "
           "onu hiç kesmez; (&#8722;3, 0) noktasından geçen tek çözüm denge çözümü <em>y</em> = 0'dır.")
    aria = ("Slope field of y' = y squared with four solution curves through (-3, 0.4), (-3, 1.2), "
            "(-3, -0.4), (-3, -1.2); they blow up at vertical asymptotes and approach the line y = 0 "
            "without touching it. The point (-3, 0) lies on the equilibrium line y = 0.")
    save(PREFIX, "ykare", figure(W, H, [p], cap, aria=aria))


if __name__ == "__main__":
    fig_ysin()
    fig_ykare()
