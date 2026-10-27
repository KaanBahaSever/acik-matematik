# -*- coding: utf-8 -*-
"""
Figures of the chapter "Çözüm Kavramı ve Çözüm Aileleri"
(dersler/diferansiyel-denklemler/cozumler.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box and never directly under a heading.
The figures are NOT produced at build time. Run

    python scripts/diffeq_figures/cozum.py
    python scripts/center_figures.py "diffeq-cozum-*.md"
    python scripts/check_figure_labels.py "scripts/_figures/diffeq-cozum-*.md"

and paste the markup of scripts/_figures/diffeq-cozum-<name>.md into the .qmd.
The captions are Turkish on purpose; the aria labels are plain ASCII.

Figures:
  parabol-ailesi  the family y = (x + c)^2 of (y')^2 - 4y = 0 with the singular
                  solution y = 0 touching every parabola (exm-cozum-parabol-tekil)
  sinus-ailesi    the family y = sin x + c of y' = cos x with the member through
                  the initial point (0, 2) highlighted (exm-cozum-kosinus)
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import save, graph  # noqa: E402
from svg_plot import Plot, figure, BASE, PRACTICE, TEXT, THEORY  # noqa: E402

PREFIX = "diffeq-cozum-"
MINUS, PI_S, SQ = "&#8722;", "&#960;", "&#178;"


def it(s):
    """Italic math letter inside an SVG <text>."""
    return f'<tspan font-style="italic">{s}</tspan>'


def num(v):
    s = f"{v:g}"
    return s.replace("-", MINUS)


# ============================================================
# parabol-ailesi: y = (x + c)^2 and the singular solution y = 0
# ============================================================
def parabola_family():
    W, H = 520, 300
    p = Plot(50, 34, 420, 220, (-5.2, 5.2), (-0.7, 4.6))
    cs = [3, 1, -1, -3]
    p.origin_axes(xlabel="x", ylabel="y", xticks=[-c for c in cs],
                  yticks=[2, 4], xfmt=num, yfmt=num)
    for c in cs:
        graph(p, lambda x, c=c: (x + c) ** 2, -5.2, 5.2, color=THEORY, width=1.7, opacity=0.85)
    # the singular solution: the x-axis itself, drawn on top of the axis line
    p.line([(-5.2, 0), (5.2, 0)], color=PRACTICE, width=3.0)
    # vertices: every parabola touches y = 0 there; the parameter sits inside each cup
    p.points([(-c, 0) for c in cs], color=PRACTICE, r=3.4)
    for c in cs:
        p.label(-c, 0, f"{it('c')} = {num(c)}", dy=-12, color=THEORY, size=11, anchor="middle")
    p.label(-5.15, 0, f"{it('y')} = 0", dy=-9, color=PRACTICE, size=12, bold=True)
    caption = ("(y′)² − 4y = 0 denkleminin y = (x + c)² ailesinden c = 3, 1, −1, −3 için dört "
               "çözüm eğrisi. Her parabol x eksenine tepe noktası x = −c'de (vurgulu noktalar) "
               "değer. Kalın çizgi y = 0 tekil çözümüdür: ailenin hiçbir üyesi değildir, ama "
               "bütün parabollere teğettir.")
    aria = ("Four parabolas y = (x + c)^2 for c = 3, 1, -1, -3, each touching the x-axis at "
            "its vertex x = -c; the x-axis y = 0 is highlighted as the singular solution.")
    return figure(W, H, [p], caption, aria=aria)


# ============================================================
# sinus-ailesi: y = sin x + c and the member through (0, 2)
# ============================================================
def sine_family():
    W, H = 520, 330
    p = Plot(70, 26, 410, 262, (-2 * math.pi, 2 * math.pi + 0.7), (-3.4, 5.4))
    ticks = [-2 * math.pi, -math.pi, math.pi, 2 * math.pi]
    names = {round(-2 * math.pi, 6): f"{MINUS}2{PI_S}", round(-math.pi, 6): f"{MINUS}{PI_S}",
             round(math.pi, 6): PI_S, round(2 * math.pi, 6): f"2{PI_S}"}
    p.origin_axes(xlabel="x", ylabel="y", xticks=ticks, yticks=[-2, 2, 4],
                  xfmt=lambda v: names[round(v, 6)], yfmt=num)
    # every member ends at height c on both edges (sin(+-2 pi) = 0): label on the left
    for c in [-2, 0, 4]:
        graph(p, lambda x, c=c: math.sin(x) + c, -2 * math.pi, 2 * math.pi,
              color=BASE, width=1.5, opacity=0.75)
        p.label(-2 * math.pi, c, f"{it('c')} = {num(c)}", dx=-9, dy=(-4 if c == 0 else 4),
                color=BASE, size=11, anchor="end")
    graph(p, lambda x: math.sin(x) + 2, -2 * math.pi, 2 * math.pi, color=PRACTICE, width=2.6)
    p.label(-2 * math.pi, 2, f"{it('c')} = 2", dx=-9, dy=4, color=PRACTICE, size=11,
            anchor="end", bold=True)
    p.points([(0, 2)], color=PRACTICE, r=4.2)
    p.label(0, 2, "(0, 2)", dx=10, dy=18, color=PRACTICE, size=12)
    caption = ("y′ = cos x denkleminin y = sin x + c ailesinden c = −2, 0, 2, 4 için çözüm "
               "eğrileri. Eğriler birbirinin düşey ötelemesidir ve kesişmez; (0, 2) noktasından "
               "yalnızca c = 2 için elde edilen y = sin x + 2 eğrisi (kalın) geçer.")
    aria = ("Curves y = sin x + c for c = -2, 0, 2, 4 on [-2 pi, 2 pi]; the curve "
            "y = sin x + 2 through the point (0, 2) is highlighted.")
    return figure(W, H, [p], caption, aria=aria)


if __name__ == "__main__":
    save(PREFIX, "parabol-ailesi", parabola_family())
    save(PREFIX, "sinus-ailesi", sine_family())
