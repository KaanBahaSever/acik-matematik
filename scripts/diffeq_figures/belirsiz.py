# -*- coding: utf-8 -*-
"""
Figures of the chapter "Belirsiz Katsayılar Yöntemi"
(dersler/diferansiyel-denklemler/belirsiz-katsayilar-yontemi.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box and never directly under a heading.
The figures are NOT produced at build time. Run

    python scripts/diffeq_figures/belirsiz.py
    python scripts/center_figures.py "diffeq-belirsiz-*.md"
    python scripts/check_figure_labels.py "scripts/_figures/diffeq-belirsiz-*.md"

and paste the markup of scripts/_figures/diffeq-belirsiz-<name>.md into the .qmd.
The captions are Turkish on purpose; the aria labels are plain ASCII.

Figures:
  rezonans  y'' + y = cos x: the particular solution (x/2) sin x between the
            envelope lines y = x/2 and y = -x/2, next to the bounded particular
            solution -(1/3) cos 2x of y'' + y = cos 2x.
  gecici    y'' + 2y' + 5y = 17 sin 2x: three solutions with y'(0) = 0 and
            y(0) = 8, 0, -8 approach the particular solution -4 cos 2x + sin 2x.
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import save, graph  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, BASE, PRACTICE, TEXT, THEORY  # noqa: E402

PREFIX = "diffeq-belirsiz-"
PI = math.pi
MINUS = "&#8722;"


def it(s):
    """Italic math letter inside an SVG <text>."""
    return f'<tspan font-style="italic">{s}</tspan>'


def sub(s):
    """Subscript inside an SVG <text>; the second tspan restores the baseline."""
    return f'<tspan font-size="9" dy="3">{s}</tspan><tspan dy="-3">&#8203;</tspan>'


def num(v):
    """Tick label with a typographic minus sign."""
    s = f"{v:g}"
    return s.replace("-", MINUS)


def pi_label(t):
    k = round(t / PI)
    return "&#960;" if k == 1 else f"{k}&#960;"


def legend(p, px, py, color, text, width=2.0, dash=None):
    """Short line sample followed by a label, at pixel position (px, py)."""
    da = f' stroke-dasharray="{dash}"' if dash else ""
    p.add(f'<line x1="{px:.1f}" y1="{py - 4:.1f}" x2="{px + 22:.1f}" y2="{py - 4:.1f}" '
          f'stroke="{color}" stroke-width="{width}"{da} stroke-linecap="round"/>')
    p.text_px(px + 28, py, text, size=11.5)


# ============================================================
# rezonans: y'' + y = cos x versus y'' + y = cos 2x
# ============================================================
def fig_rezonans():
    W, H = 560, 310
    p = Plot(46, 26, 430, 244, (0, 6 * PI), (-10, 10))
    p.grid(ys=[0])
    p.axes([k * PI for k in range(1, 7)], [-8, -4, 0, 4, 8], it("x"), it("y"),
           xfmt=pi_label, yfmt=num)
    # envelope lines y = x/2 and y = -x/2
    end = 6 * PI
    p.line([(0, 0), (end, end / 2)], color=TEXT, width=1.2, dash="5 4", opacity=0.7)
    p.line([(0, 0), (end, -end / 2)], color=TEXT, width=1.2, dash="5 4", opacity=0.7)
    # bounded particular solution of y'' + y = cos 2x
    graph(p, lambda x: -math.cos(2 * x) / 3, 0, end, n=800, color=BASE, width=1.8)
    # resonant particular solution of y'' + y = cos x
    graph(p, lambda x: x / 2 * math.sin(x), 0, end, n=800, color=THEORY, width=2.1)
    # envelope labels at the right end
    p.label(end, end / 2, f'{it("y")} = {it("x")}/2', dx=7, dy=5)
    p.label(end, -end / 2, f'{it("y")} = {MINUS}{it("x")}/2', dx=7, dy=-5)
    # legend in the empty upper-left corner
    lx, ly = p.x0 + 12, p.y0 + 14
    legend(p, lx, ly, THEORY, f'{it("y")} = ({it("x")}/2) sin {it("x")}', width=2.1)
    legend(p, lx, ly + 20, BASE, f'{it("y")} = {MINUS}(1/3) cos 2{it("x")}', width=1.8)
    caption = ("y'' + y = cos x denkleminin özel çözümü (x/2) sin x, y = x/2 ve y = −x/2 doğruları "
               "arasında giderek büyüyen bir salınımdır (rezonans). Sağ taraf cos 2x olduğunda "
               "özel çözüm −(1/3) cos 2x sınırlı kalır.")
    aria = ("Graph of y = (x/2) sin x for x from 0 to 6 pi, oscillating between the dashed lines "
            "y = x/2 and y = -x/2 with growing amplitude, together with the small bounded curve "
            "y = -(1/3) cos 2x.")
    save(PREFIX, "rezonans", figure(W, H, [p], caption, aria=aria))


# ============================================================
# gecici: transient y_h dies out, all solutions approach y_p
# ============================================================
def fig_gecici():
    W, H = 560, 310
    p = Plot(46, 26, 430, 244, (0, 3 * PI), (-10, 10))
    p.grid(ys=[0])
    p.axes([k * PI for k in range(1, 4)], [-8, -4, 0, 4, 8], it("x"), it("y"),
           xfmt=pi_label, yfmt=num)

    def yp(x):
        return -4 * math.cos(2 * x) + math.sin(2 * x)

    # y = e^{-x}(c1 cos 2x + c2 sin 2x) + yp, with y'(0) = 0:
    # y(0) = c1 - 4, y'(0) = -c1 + 2 c2 + 2  ->  c1 = y0 + 4, c2 = (c1 - 2)/2
    starts = []
    for y0 in (8, 0, -8):
        c1 = y0 + 4
        c2 = (c1 - 2) / 2
        graph(p, lambda x, c1=c1, c2=c2: math.exp(-x) * (c1 * math.cos(2 * x) + c2 * math.sin(2 * x)) + yp(x),
              0, 3 * PI, n=700, color=BASE, width=1.5)
        starts.append((0, y0))
    graph(p, yp, 0, 3 * PI, n=700, color=THEORY, width=2.4)
    p.points(starts, color=PRACTICE, r=4.0)
    # legend in the empty upper-right region
    lx, ly = p.X(4.1), p.y0 + 14
    legend(p, lx, ly, THEORY, f'{it("y")}{sub("p")} = {MINUS}4 cos 2{it("x")} + sin 2{it("x")}', width=2.4)
    legend(p, lx, ly + 20, BASE, f"{it('y')}{sub('h')} + {it('y')}{sub('p')} (üç çözüm)", width=1.5)
    caption = ("y'' + 2y' + 5y = 17 sin 2x denkleminin y'(0) = 0 ve y(0) = 8, 0, −8 koşullarını "
               "sağlayan üç çözümü: homojen kısım üstel olarak söndükçe üçü de aynı özel çözüme yaklaşır.")
    aria = ("Three solution curves starting at y = 8, 0 and -8 on the y axis with zero slope; "
            "they oscillate with decaying difference and merge with the particular solution "
            "y = -4 cos 2x + sin 2x, drawn as a thick curve.")
    save(PREFIX, "gecici", figure(W, H, [p], caption, aria=aria))


if __name__ == "__main__":
    fig_rezonans()
    fig_gecici()
