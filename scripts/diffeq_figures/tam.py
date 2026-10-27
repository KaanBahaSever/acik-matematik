# -*- coding: utf-8 -*-
"""
Figures of the chapter "Tam Diferansiyel Denklemler"
(dersler/diferansiyel-denklemler/tam-diferansiyel-denklemler.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise) or, for a concept figure that must stay visible, in plain text right
after the paragraph it explains; never inside a definition box and never
directly under a heading. The figures are NOT produced at build time. Run

    python scripts/diffeq_figures/tam.py
    python scripts/center_figures.py "diffeq-tam-*.md"
    python scripts/check_figure_labels.py "scripts/_figures/diffeq-tam-*.md"

and paste the markup of scripts/_figures/diffeq-tam-<name>.md into the .qmd.
The captions are Turkish on purpose; the aria labels are plain ASCII.

Needs numpy and contourpy (author side only) for the level curves.
"""
import math
import sys
from pathlib import Path

import numpy as np
from contourpy import contour_generator

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import save, frame  # noqa: E402,F401
from svg_plot import Plot, figure, BG, PRACTICE, TEXT, THEORY  # noqa: E402

PREFIX = "diffeq-tam-"
MINUS, PI_S = "&#8722;", "&#960;"


def it(s):
    """Italic math letter inside an SVG <text>."""
    return f'<tspan font-style="italic">{s}</tspan>'


def num(v):
    """Tick label with a typographic minus sign."""
    return f"{v:g}".replace(".", ",").replace("-", MINUS)


def plate_label(p, x, y, s, width_chars, dx=0, dy=0, color=TEXT, size=11.5, anchor="start"):
    """Label on a page-coloured plate, so curves running behind it stay readable."""
    w = width_chars * 0.55 * size
    px, py = p.X(x) + dx, p.Y(y) + dy
    x0 = px - (w / 2 if anchor == "middle" else w if anchor == "end" else 0)
    p.add(f'<rect x="{x0 - 2.5:.1f}" y="{py - 0.8 * size - 1:.1f}" width="{w + 5:.1f}" '
          f'height="{size + 3:.1f}" rx="3" fill="{BG}" opacity="0.9"/>')
    p.label(x, y, s, dx, dy, color, size, anchor)


def level_lines(f, xr, yr, levels, n=500):
    """Polylines of f(x, y) = c for each c, on an n-by-n grid of the window."""
    xs = np.linspace(xr[0], xr[1], n)
    ys = np.linspace(yr[0], yr[1], n)
    X, Y = np.meshgrid(xs, ys)
    gen = contour_generator(xs, ys, f(X, Y))
    return {c: [seg.tolist() for seg in gen.lines(c)] for c in levels}


# ============================================================
# seviye: level curves of F(x, y) = x^2 e^y + sin y (exm-tam-baslangic-kosullu)
# ============================================================
XR, YR = (-1.5, 1.5), (-0.5, 3.5)
p = Plot(48, 22, 430, 280, XR, YR)
p.grid(xs=(-1, -0.5, 0, 0.5, 1), ys=(0, 1, 2, 3))
p.axes(xticks=(-1.5, -1, -0.5, 0, 0.5, 1, 1.5), yticks=(0, 1, 2, 3), xlabel=it("x"), ylabel=it("y"),
       xfmt=num, yfmt=num)
frame(p, 0.25)


def F(x, y):
    return x**2 * np.exp(y) + np.sin(y)


others = (-0.3, 0.3, 0.75, 1.5, 3, 6, 12)
lines = level_lines(F, XR, YR, others + (1.0,))
for c in others:
    for seg in lines[c]:
        p.line(seg, THEORY, 1.3, opacity=0.8)
for seg in lines[1.0]:
    p.line(seg, PRACTICE, 2.6)

# the initial point (0, pi/2), where M = N = 0
y0 = math.pi / 2
p.points([(0, y0)], TEXT, 4.2)
plate_label(p, 0, y0, f"(0, {PI_S}/2)", 7.2, dx=-10, dy=4, anchor="end", size=11.5)

# level values on a few curves (x chosen where the curve is far from the others)
def y_on_level(c, x, lo, hi):
    """Solve F(x, y) = c for y in [lo, hi] by bisection."""
    a, b = lo, hi
    fa = F(x, a) - c
    for _ in range(80):
        m = (a + b) / 2
        fm = F(x, m) - c
        if (fa < 0) == (fm < 0):
            a, fa = m, fm
        else:
            b = m
    return (a + b) / 2


plate_label(p, 1.18, y_on_level(1.0, 1.18, -0.5, 1.0), f"{it('F')} = 1", 4.6, dx=0, dy=4,
            color=PRACTICE, size=12, anchor="middle")
for c, xc, lo, hi in ((3, 1.25, -0.5, 3.5), (6, 1.05, -0.5, 3.5), (12, 0.86, 1.0, 3.5)):
    plate_label(p, xc, y_on_level(c, xc, lo, hi), f"{it('F')} = {c}", 4.6 + len(str(c)) * 0.5,
                dy=4, color=THEORY, size=11, anchor="middle")
plate_label(p, -0.62, y_on_level(0.3, -0.62, -0.5, 1.0), f"{it('F')} = 0,3", 6.0, dy=4,
            color=THEORY, size=11, anchor="middle")

svg = figure(510, 345, [p],
             "Örnekteki potansiyel fonksiyonun F(x, y) = c seviye eğrileri; her biri denklemin bir "
             "çözüm eğrisidir. Kalın çizilen F = 1 eğrisi başlangıç noktası (0, π/2) üzerinden geçer ve "
             "orada birbirini kesen iki koldan oluşur.",
             aria="Level curves of F(x,y) = x^2 e^y + sin y for several values; the level F = 1 is drawn "
                  "thick and consists of two branches crossing at the initial point (0, pi/2).")
save(PREFIX, "seviye-egrileri", svg)
