# -*- coding: utf-8 -*-
"""
Figures of the chapter "Homojen Denklemler ve Homojene İndirgenebilenler"
(dersler/diferansiyel-denklemler/homojen-denklemler.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box and never directly under a heading.
The figures are NOT produced at build time. Run

    python scripts/diffeq_figures/homojen.py
    python scripts/center_figures.py "diffeq-homojen-*.md"
    python scripts/check_figure_labels.py "scripts/_figures/diffeq-homojen-*.md"

and paste the markup of scripts/_figures/diffeq-homojen-<name>.md into the .qmd.
The captions are Turkish on purpose; the aria labels are plain ASCII.

Conventions: lines through the origin are thin dashed lines, the slope marks
on them are short segments in the practice color, solution curves are in the
theory color. The axes have equal scales, so circles look like circles.
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import save, graph, rk4, solution_curve, slope_field, frame  # noqa: E402,F401

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, sup, PRACTICE, TEXT, THEORY  # noqa: E402

PREFIX = "diffeq-homojen-"
MINUS = "&#8722;"


def it(s):
    """Italic math letter inside an SVG <text>."""
    return f'<tspan font-style="italic">{s}</tspan>'


def num(v):
    """A tick label with a typographic minus sign."""
    return f"{v:g}".replace("-", MINUS)


def clip_line_through_origin(p, theta):
    """End points of the line through the origin with angle theta, clipped to the panel."""
    dx, dy = math.cos(theta), math.sin(theta)
    ts = []
    if abs(dx) > 1e-12:
        ts += [p.xmax / dx, p.xmin / dx]
    if abs(dy) > 1e-12:
        ts += [p.ymax / dy, p.ymin / dy]
    tpos = min(t for t in ts if t > 0)
    tneg = max(t for t in ts if t < 0)
    return (tneg * dx, tneg * dy), (tpos * dx, tpos * dy)


def segment(p, x, y, m, seg, color, width):
    """Short segment of slope m centred at the data point (x, y), length seg pixels."""
    sx = p.w / (p.xmax - p.xmin)
    sy = p.h / (p.ymax - p.ymin)
    vx, vy = sx, -m * sy
    n = math.hypot(vx, vy)
    ux, uy = vx / n * seg / 2, vy / n * seg / 2
    cx, cy = p.X(x), p.Y(y)
    p.add(f'<line x1="{cx-ux:.1f}" y1="{cy-uy:.1f}" x2="{cx+ux:.1f}" y2="{cy+uy:.1f}" '
          f'stroke="{color}" stroke-width="{width}" stroke-linecap="round"/>')


# ============================================================
# 2xy y' = y^2 - x^2: the slope is constant along every line through the
# origin; the solutions are the circles x^2 + y^2 = kx (exm-homojen-cember)
# ============================================================
def fig_isinlar():
    XR, YR = 3.3, 2.1
    PW = 460
    PH = PW * YR / XR          # equal scales
    W, H = 540, int(PH + 50)
    p = Plot(40, 24, PW, PH, (-XR, XR), (-YR, YR))
    p.origin_axes(xlabel="x", ylabel="y", yticks=(-2, -1, 1, 2), xfmt=num, yfmt=num)
    # x ticks by hand: every circle meets the x axis at an integer, so the
    # labels move off the crossing point, away from the origin
    oy = p.Y(0)
    boxes = []                 # pixel boxes of the tick labels, kept free of slope marks
    for t in (-3, -2, -1, 1, 2, 3):
        px = p.X(t)
        lx = px + 5 if t > 0 else px - 5
        wl = 7 * len(f"{abs(t)}") + (7 if t < 0 else 0)
        boxes.append((lx if t > 0 else lx - wl, oy + 5, lx + wl if t > 0 else lx, oy + 16))
        p.add(f'<line x1="{px:.1f}" y1="{oy-3:.1f}" x2="{px:.1f}" y2="{oy+3:.1f}" stroke="{TEXT}" stroke-width="1"/>')
        p.text_px(px + (5 if t > 0 else -5), oy + 15, num(t), size=11, anchor="start" if t > 0 else "end")

    def f(x, y):
        return (y * y - x * x) / (2 * x * y)

    angles = [10, 30, 50, 70, 110, 130, 150, 170]
    for a in angles:
        th = math.radians(a)
        (x0, y0), (x1, y1) = clip_line_through_origin(p, th)
        p.line([(x0, y0), (x1, y1)], color=TEXT, width=0.9, dash="3 4", opacity=0.35)
    for k in (1, 2, 3):
        for s in (1, -1):
            p.circle(s * k / 2, 0, k / 2, color=THEORY, width=1.9)
    for a in angles:
        th = math.radians(a)
        m = f(math.cos(th), math.sin(th))
        for r in (0.6, 1.2, 1.8, 2.4, 3.0):
            for s in (1, -1):
                x, y = s * r * math.cos(th), s * r * math.sin(th)
                cx, cy = p.X(x), p.Y(y)
                near_label = any(b[0] - 9 <= cx <= b[2] + 9 and b[1] - 9 <= cy <= b[3] + 9 for b in boxes)
                if abs(x) <= XR - 0.12 and abs(y) <= YR - 0.12 and not near_label:
                    segment(p, x, y, m, 15.0, PRACTICE, 2.2)
    p.label(2.05, 1.62, it("x") + sup("2", 10) + " + " + it("y") + sup("2", 10) + " = " + it("kx"),
            color=THEORY, size=12.5, anchor="middle")
    cap = ("2<em>xy</em><em>y</em>&#8242; = <em>y</em><sup>2</sup> &#8722; <em>x</em><sup>2</sup> denkleminde "
           "eğim yalnızca <em>y</em>/<em>x</em> oranına bağlıdır: orijinden geçen her kesikli doğru üzerindeki "
           "kısa parçalar birbirine paraleldir. Çözüm eğrileri, <em>k</em> = &#177;1, &#177;2, &#177;3 için "
           "çizilen <em>x</em><sup>2</sup> + <em>y</em><sup>2</sup> = <em>kx</em> çemberleridir; her çember bir "
           "doğruyu orijin dışında kestiği yerde o doğrunun ortak eğimiyle geçer.")
    aria = ("Slope marks of 2xy y' = y^2 - x^2 placed on eight dashed lines through the origin; on each line "
            "all marks are parallel. Six solution circles x^2 + y^2 = kx, k = 1, 2, 3 and -1, -2, -3, "
            "centred on the x axis and passing through the origin.")
    save(PREFIX, "isinlar", figure(W, H, [p], cap, aria=aria))


if __name__ == "__main__":
    fig_isinlar()
