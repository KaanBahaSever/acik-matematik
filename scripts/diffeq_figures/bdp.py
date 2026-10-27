# -*- coding: utf-8 -*-
"""
Figures of the chapter "Başlangıç ve Sınır Değer Problemleri; Varlık ve Teklik"
(dersler/diferansiyel-denklemler/baslangic-sinir-deger-problemleri.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box and never directly under a heading.
The figures are NOT produced at build time. Run

    python scripts/diffeq_figures/bdp.py
    python scripts/center_figures.py "diffeq-bdp-*.md"
    python scripts/check_figure_labels.py "scripts/_figures/diffeq-bdp-*.md"

and paste the markup of scripts/_figures/diffeq-bdp-<name>.md into the .qmd.
The captions are Turkish on purpose; the aria labels are plain ASCII.

    karekok-bolge   y' = y/sqrt(x): slope field in x > 0, the excluded half-plane
                    x <= 0, the open rectangle D around (1, 2) and the solution
                    curve through (1, 2)
    tekil-zarf      y' = sqrt(y): the half-parabolas y = (x + c)^2/4, x > -c,
                    approaching the x-axis tangentially at (-c, 0); glued to the
                    axis they give the solutions y_a, so y = 0 and y_a both pass
                    through every (a, 0)
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import save, graph, slope_field  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, BASE, BG, PRACTICE, TEXT, THEORY  # noqa: E402

PREFIX = "diffeq-bdp-"
MINUS, SQRT, LEQ = "&#8722;", "&#8730;", "&#8804;"


def it(s):
    """Italic math letter inside an SVG <text>."""
    return f'<tspan font-style="italic">{s}</tspan>'


def num(v):
    """A tick label with a typographic minus sign."""
    return f"{v:g}".replace("-", MINUS)


def plate(p, x, y, width, size, dx=0, dy=0, anchor="start"):
    """Page-coloured rounded plate under a label that sits on slope-field segments."""
    px, py = p.X(x) + dx, p.Y(y) + dy
    x0 = px - (width / 2 if anchor == "middle" else width if anchor == "end" else 0)
    p.add(f'<rect x="{x0 - 2.5:.1f}" y="{py - 0.8 * size - 1:.1f}" width="{width + 5:.1f}" '
          f'height="{size + 3:.1f}" rx="3" fill="{BG}" opacity="0.85"/>')


def axes_through_origin(p, xticks, yticks, xlabels=None, ylabels=None):
    """Axes through the data origin with arrowheads, ticks and tick labels."""
    ox, oy = p.X(0), p.Y(0)
    left, right = p.x0 - 4, p.x0 + p.w + 6
    top, bottom = p.y0 - 6, p.y0 + p.h + 4
    p.add(f'<g stroke="{TEXT}" stroke-width="1.1" opacity="0.55" fill="{TEXT}">'
          f'<line x1="{left:.1f}" y1="{oy:.1f}" x2="{right:.1f}" y2="{oy:.1f}"/>'
          f'<line x1="{ox:.1f}" y1="{bottom:.1f}" x2="{ox:.1f}" y2="{top:.1f}"/>'
          f'<polygon points="{right:.1f},{oy:.1f} {right-8:.1f},{oy-3.5:.1f} {right-8:.1f},{oy+3.5:.1f}" stroke="none"/>'
          f'<polygon points="{ox:.1f},{top:.1f} {ox-3.5:.1f},{top+8:.1f} {ox+3.5:.1f},{top+8:.1f}" stroke="none"/>'
          '</g>')
    for i, t in enumerate(xticks):
        lab = xlabels[i] if xlabels else num(t)
        p.add(f'<line x1="{p.X(t):.1f}" y1="{oy-3:.1f}" x2="{p.X(t):.1f}" y2="{oy+3:.1f}" '
              f'stroke="{TEXT}" stroke-width="1" opacity="0.6"/>')
        p.text_px(p.X(t), oy + 16, lab, TEXT, 11, "middle")
    for i, t in enumerate(yticks):
        lab = ylabels[i] if ylabels else num(t)
        p.add(f'<line x1="{ox-3:.1f}" y1="{p.Y(t):.1f}" x2="{ox+3:.1f}" y2="{p.Y(t):.1f}" '
              f'stroke="{TEXT}" stroke-width="1" opacity="0.6"/>')
        p.text_px(ox - 7, p.Y(t) + 4, lab, TEXT, 11, "end")
    p.text_px(right - 2, oy - 8, "x", TEXT, 12.5, "end", italic=True)
    p.text_px(ox + 8, top + 10, "y", TEXT, 12.5, "start", italic=True)


# ============================================================
# karekok-bolge: y' = y/sqrt(x), y(1) = 2; D = (1/2, 3/2) x (1, 3) inside x > 0
# ============================================================
p = Plot(40, 24, 330, 240, (-1.0, 3.0), (-0.6, 5.0))

# the half-plane x <= 0 where f and df/dy are undefined
p.polygon([(p.xmin, p.ymin), (0, p.ymin), (0, p.ymax), (p.xmin, p.ymax)], PRACTICE, 0.09)
p.label(-0.5, 4.72, f"{it('x')} {LEQ} 0:", 0, 0, PRACTICE, 11.5, "middle")
p.label(-0.5, 4.72, f"{it('f')} tanımsız", 0, 15, PRACTICE, 11.5, "middle")


def f(x, y):
    """Slope of y' = y/sqrt(x); raises for x < 0, ZeroDivisionError at x = 0.

    The band below the x-axis is left empty so the tick labels stay readable.
    """
    if y < 0:
        return None
    return y / math.sqrt(x)


slope_field(p, f, nx=12, ny=12, seg=12.0, color=BASE, width=1.1, opacity=0.55)

# the open rectangle D around (1, 2)
D = [(0.5, 1.0), (1.5, 1.0), (1.5, 3.0), (0.5, 3.0)]
p.polygon(D, THEORY, 0.13, stroke=THEORY, width=1.4, dash="5 3")
p.label(0.5, 3.0, it("D"), 6, 16, THEORY, 13, "start", bold=True)

axes_through_origin(p, (0.5, 1, 1.5, 2, 2.5), (1, 2, 3, 4),
                    xlabels=("1/2", "1", "3/2", "2", "5/2"))
# the line x = 0 (boundary of the region where the hypotheses hold)
p.add(f'<line x1="{p.X(0):.1f}" y1="{p.Y(p.ymin):.1f}" x2="{p.X(0):.1f}" y2="{p.Y(p.ymax):.1f}" '
      f'stroke="{PRACTICE}" stroke-width="1.6" stroke-dasharray="6 4"/>')

# solution through (1, 2): y = 2 exp(2 sqrt(x) - 2) (checked in sympy)
graph(p, lambda x: 2 * math.exp(2 * math.sqrt(x) - 2), 1e-4, p.xmax, n=500, color=THEORY, width=2.3)
p.points([(1, 2)], PRACTICE, 4.2)
plate(p, 1, 2, 34, 12, 9, 16)
p.label(1, 2, "(1, 2)", 9, 16, PRACTICE, 12, "start", bold=True)

save(PREFIX, "karekok-bolge", figure(
    400, 300, [p],
    "<em>y</em>&#8242; = <em>y</em>/&#8730;<em>x</em> denkleminin eğim alanı. Sol yarı düzlemde (<em>x</em> &#8804; 0) "
    "<em>f</em> tanımsızdır; kesikli çerçeveli açık dikdörtgen <em>D</em> = (1/2, 3/2) &#215; (1, 3) tamamen "
    "<em>x</em> &gt; 0 bölgesinde kalır ve (1, 2) noktasını içerir. Kalın eğri (1, 2) noktasından geçen çözüm "
    "eğrisidir; teorem bu eğrinin varlığını ve tekliğini (1, 2) noktasının yakınında garanti eder.",
    aria="Slope field of y' = y/sqrt(x) for x greater than 0, the half-plane x at most 0 shaded as undefined, "
         "the open rectangle D = (1/2, 3/2) x (1, 3) around the point (1, 2) and the solution curve through it"))


# ============================================================
# tekil-zarf: y' = sqrt(y), half-parabolas y = (x + c)^2/4 (x > -c) and y = 0
# ============================================================
p = Plot(30, 24, 400, 220, (-4.4, 5.6), (-0.7, 3.3))
YTOP = 3.2
CS = (2, 1, 0, -1, -2, -3)          # vertex of each branch at x = -c

axes_through_origin(p, (-2, -1, 1, 2, 3, 4, 5), (1, 2, 3))
for c in CS:
    a = -c
    x_end = a + 2 * math.sqrt(YTOP)
    graph(p, lambda x, a=a: (x - a) ** 2 / 4, a, x_end, n=90, color=BASE, width=1.8)

# the singular solution y = 0 drawn on top, then the tangency points
p.line([(p.xmin, 0), (p.xmax, 0)], PRACTICE, 2.6)
p.points([(-c, 0) for c in CS], PRACTICE, 3.6)
p.label(-3.3, 0, f"{it('y')} = 0", 0, -24, PRACTICE, 12.5, "middle", bold=True)
p.label(-3.3, 0, "tekil çözüm", 0, -9, PRACTICE, 11.5, "middle")
# family label in the empty upper-left corner, in the colour of the branches
p.label(-4.3, 2.75, f"{it('y')} = ({it('x')} + {it('c')})&#178;/4", 0, 0, BASE, 12.5, "start")

save(PREFIX, "tekil-zarf", figure(
    430, 280, [p],
    "<em>y</em>&#8242; = &#8730;<em>y</em> denkleminin <em>y</em> = (<em>x</em> + <em>c</em>)&#178;/4, "
    "<em>x</em> &gt; &#8722;<em>c</em> çözüm eğrileri (<em>c</em> = 2, 1, 0, &#8722;1, &#8722;2, &#8722;3) ve "
    "tekil çözüm <em>y</em> = 0. Her parça, <em>x</em> eksenine (&#8722;<em>c</em>, 0) noktasında teğet olarak "
    "yaklaşır; parçayı eksenin bu noktanın solundaki kısmıyla birleştirmek <em>y</em><sub><em>a</em></sub> "
    "çözümünü verir (<em>a</em> = &#8722;<em>c</em>). Böylece eksenin her (<em>a</em>, 0) noktasından hem "
    "<em>y</em> = 0 hem de <em>y</em><sub><em>a</em></sub> geçer.",
    aria="Half-parabolas y = (x + c)^2/4 for x greater than -c with c = 2, 1, 0, -1, -2, -3 leaving the "
         "x-axis tangentially, and the singular solution y = 0 drawn as a thick line"))
