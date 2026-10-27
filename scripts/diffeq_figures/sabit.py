# -*- coding: utf-8 -*-
"""
Figures of the chapter "Keyfi Sabitlerin Yok Edilmesi"
(dersler/diferansiyel-denklemler/keyfi-sabitlerin-yok-edilmesi.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution,
exercise or callout), never inside a definition box and never directly under a
heading. The figures are NOT produced at build time. Run

    python scripts/diffeq_figures/sabit.py
    python scripts/center_figures.py "diffeq-sabit-*.md"
    python scripts/check_figure_labels.py "scripts/_figures/diffeq-sabit-*.md"

and paste the markup of scripts/_figures/diffeq-sabit-<name>.md into the .qmd.
The captions are Turkish on purpose; the aria labels are plain ASCII.

    clairaut-zarf   the lines y = cx + c^2 (c = -2, -1.5, ..., 2) of the family
                    whose equation is y = xy' + (y')^2, each tangent to the
                    parabola y = -x^2/4 at (-2c, -c^2): the singular solution is
                    the envelope of the family
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import save, graph  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, BASE, BG, PRACTICE, TEXT  # noqa: E402

PREFIX = "diffeq-sabit-"
MINUS = "&#8722;"


def it(s):
    """Italic math letter inside an SVG <text>."""
    return f'<tspan font-style="italic">{s}</tspan>'


def num(v):
    """A tick label with a typographic minus sign."""
    return f"{v:g}".replace("-", MINUS)


def plate_px(p, px, py, width, size, anchor="start"):
    """Page-coloured rounded plate under a label that sits on other lines."""
    x0 = px - (width / 2 if anchor == "middle" else width if anchor == "end" else 0)
    p.add(f'<rect x="{x0 - 2.5:.1f}" y="{py - 0.8 * size - 1:.1f}" width="{width + 5:.1f}" '
          f'height="{size + 3:.1f}" rx="3" fill="{BG}" opacity="0.88"/>')


def axes_through_origin(p, xticks, yticks):
    """Axes through the data origin with arrowheads; tick labels sit on plates."""
    ox, oy = p.X(0), p.Y(0)
    left, right = p.x0 - 4, p.x0 + p.w + 6
    top, bottom = p.y0 - 6, p.y0 + p.h + 4
    p.add(f'<g stroke="{TEXT}" stroke-width="1.1" opacity="0.55" fill="{TEXT}">'
          f'<line x1="{left:.1f}" y1="{oy:.1f}" x2="{right:.1f}" y2="{oy:.1f}"/>'
          f'<line x1="{ox:.1f}" y1="{bottom:.1f}" x2="{ox:.1f}" y2="{top:.1f}"/>'
          f'<polygon points="{right:.1f},{oy:.1f} {right-8:.1f},{oy-3.5:.1f} {right-8:.1f},{oy+3.5:.1f}" stroke="none"/>'
          f'<polygon points="{ox:.1f},{top:.1f} {ox-3.5:.1f},{top+8:.1f} {ox+3.5:.1f},{top+8:.1f}" stroke="none"/>'
          '</g>')
    for t in xticks:
        p.add(f'<line x1="{p.X(t):.1f}" y1="{oy-3:.1f}" x2="{p.X(t):.1f}" y2="{oy+3:.1f}" '
              f'stroke="{TEXT}" stroke-width="1" opacity="0.6"/>')
        plate_px(p, p.X(t), oy + 16, 6.5 * len(num(t).replace(MINUS, "-")), 11, "middle")
        p.text_px(p.X(t), oy + 16, num(t), TEXT, 11, "middle")
    for t in yticks:
        p.add(f'<line x1="{ox-3:.1f}" y1="{p.Y(t):.1f}" x2="{ox+3:.1f}" y2="{p.Y(t):.1f}" '
              f'stroke="{TEXT}" stroke-width="1" opacity="0.6"/>')
        plate_px(p, ox - 7, p.Y(t) + 4, 6.5 * len(num(t).replace(MINUS, "-")), 11, "end")
        p.text_px(ox - 7, p.Y(t) + 4, num(t), TEXT, 11, "end")
    p.text_px(right - 2, oy - 8, "x", TEXT, 12.5, "end", italic=True)
    p.text_px(ox + 8, top + 10, "y", TEXT, 12.5, "start", italic=True)


# ============================================================
# clairaut-zarf: y = cx + c^2 and the envelope y = -x^2/4
# ============================================================
p = Plot(30, 24, 380, 290, (-5.0, 5.0), (-6.5, 3.0))
CS = [k / 2 for k in range(-4, 5)]          # c = -2, -1.5, ..., 2



def line_in_panel(p, m, b):
    """End points of the part of y = m x + b inside the panel (exact clipping of a straight line)."""
    lo, hi = p.xmin, p.xmax
    if m != 0:
        xa, xb = sorted(((p.ymin - b) / m, (p.ymax - b) / m))
        lo, hi = max(lo, xa), min(hi, xb)
    return [(lo, m * lo + b), (hi, m * hi + b)]


for c in CS:
    p.line(line_in_panel(p, c, c * c), BASE, 1.3, opacity=0.85)
axes_through_origin(p, (-4, -2, 2, 4), (-4, -2, 2))
graph(p, lambda x: -x * x / 4, p.xmin, p.xmax, n=160, color=PRACTICE, width=2.6)
# tangency points (-2c, -c^2) (checked in sympy)
p.points([(-2 * c, -c * c) for c in CS], PRACTICE, 3.4)

# the region below the parabola contains no line of the family: room for its label
p.label(2.0, -3.0, f"{it('y')} = {MINUS}{it('x')}&#178;/4", 0, 0, PRACTICE, 12.5, "middle", bold=True)
p.label(2.0, -3.0, "tekil çözüm (zarf)", 0, 16, PRACTICE, 11.5, "middle")
# family label at the left edge; its plate starts left of the panel so no stub of a line peeks out
plate_px(p, p.x0 - 1, p.Y(2.45), 90, 12.5)
p.text_px(p.x0 + 2, p.Y(2.45), f"{it('y')} = {it('c')}{it('x')} + {it('c')}&#178;", BASE, 12.5, "start")

save(PREFIX, "clairaut-zarf", figure(
    440, 340, [p],
    "<em>y</em> = <em>cx</em> + <em>c</em>&#178; ailesinin <em>c</em> = &#8722;2, &#8722;1,5, &#8230;, 2 "
    "değerlerine karşılık gelen doğruları ve tekil çözüm <em>y</em> = &#8722;<em>x</em>&#178;/4. "
    "Her doğru parabole (&#8722;2<em>c</em>, &#8722;<em>c</em>&#178;) noktasında teğettir; parabol, "
    "doğru ailesinin zarfıdır ve altında ailenin hiçbir doğrusu yoktur.",
    aria="The lines y = cx + c^2 for c from -2 to 2 in steps of 0.5, each tangent to the parabola "
         "y = -x^2/4 at the point (-2c, -c^2); the parabola is the envelope of the family"))
