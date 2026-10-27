# -*- coding: utf-8 -*-
"""
Shared helpers for the figure scripts of dersler/diferansiyel-denklemler.

Every chapter has its own script scripts/diffeq_figures/<key>.py that writes
scripts/_figures/diffeq-<key>-<name>.md. Figures go INSIDE the box they
explain (theorem, proof, example, solution or exercise), never inside a
definition box and never directly under a heading. The figures are NOT
produced at build time. Run

    python scripts/diffeq_figures/<key>.py
    python scripts/center_figures.py "diffeq-<key>-*.md"
    python scripts/check_figure_labels.py "scripts/_figures/diffeq-<key>-*.md"

and paste the markup of scripts/_figures/diffeq-<key>-<name>.md into the .qmd.
Captions are Turkish on purpose; aria labels are plain ASCII.

The helpers below cover what most differential-equation pictures need:
direction fields, numerically integrated solution curves, and clipping of
explicit curves to the panel.
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import BASE, TEXT  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)


def save(prefix, name, svg):
    """Write one figure to scripts/_figures/<prefix><name>.md (UTF-8, LF)."""
    (OUT_DIR / f"{prefix}{name}.md").write_text(svg, encoding="utf-8", newline="\n")
    print(f"{prefix}{name}.md")


def linspace(a, b, n):
    if n == 1:
        return [a]
    return [a + (b - a) * i / (n - 1) for i in range(n)]


def clip_runs(pts, p, pad=0.0):
    """Split a polyline into the runs that stay inside the panel of Plot p.

    Points outside the y range (or non-finite ones) break the curve, so
    asymptotes and blow-ups never draw stray vertical lines.
    """
    lo, hi = p.ymin - pad, p.ymax + pad
    runs, cur = [], []
    for x, y in pts:
        ok = y is not None and math.isfinite(y) and lo <= y <= hi and p.xmin <= x <= p.xmax
        if ok:
            cur.append((x, y))
        elif cur:
            runs.append(cur)
            cur = []
    if cur:
        runs.append(cur)
    return [r for r in runs if len(r) > 1]


def graph(p, f, x0, x1, n=400, **style):
    """Draw y = f(x) on [x0, x1], clipped to the panel; f may raise or return None."""
    pts = []
    for x in linspace(x0, x1, n):
        try:
            y = f(x)
        except (ValueError, ZeroDivisionError, OverflowError):
            y = None
        pts.append((x, y))
    for run in clip_runs(pts, p):
        p.line(run, **style)


def rk4(f, x0, y0, x1, n=600):
    """Integrate y' = f(x, y) from (x0, y0) to x1 (either direction) with RK4.

    Integration stops early when the solution blows up or f is undefined.
    """
    h = (x1 - x0) / n
    x, y = x0, y0
    pts = [(x, y)]
    for _ in range(n):
        try:
            k1 = f(x, y)
            k2 = f(x + h / 2, y + h * k1 / 2)
            k3 = f(x + h / 2, y + h * k2 / 2)
            k4 = f(x + h, y + h * k3)
        except (ValueError, ZeroDivisionError, OverflowError):
            break
        y = y + h * (k1 + 2 * k2 + 2 * k3 + k4) / 6
        x = x + h
        if not math.isfinite(y) or abs(y) > 1e6:
            break
        pts.append((x, y))
    return pts


def solution_curve(p, f, x0, y0, n=600, **style):
    """Draw the solution of y' = f(x, y) through (x0, y0) across the whole panel."""
    left = list(reversed(rk4(f, x0, y0, p.xmin, n)))
    right = rk4(f, x0, y0, p.xmax, n)
    for run in clip_runs(left[:-1] + right, p):
        p.line(run, **style)


def slope_field(p, f, nx=17, ny=13, seg=13.0, color=BASE, width=1.2, opacity=0.75):
    """Short line segments of slope f(x, y) at an nx-by-ny grid of the panel.

    seg is the segment length in pixels; the direction is computed in pixel
    space, so the segments are correct even when the axes have unequal scales.
    Grid points where f is undefined are skipped.
    """
    sx = p.w / (p.xmax - p.xmin)
    sy = p.h / (p.ymax - p.ymin)
    dx_data = (p.xmax - p.xmin) / nx
    dy_data = (p.ymax - p.ymin) / ny
    parts = [f'<g stroke="{color}" stroke-width="{width}" opacity="{opacity}" stroke-linecap="round">']
    for i in range(nx):
        for j in range(ny):
            x = p.xmin + (i + 0.5) * dx_data
            y = p.ymin + (j + 0.5) * dy_data
            try:
                m = f(x, y)
            except (ValueError, ZeroDivisionError, OverflowError):
                continue
            if m is None or not math.isfinite(m):
                continue
            vx, vy = sx, -m * sy          # pixel direction of (1, m)
            norm = math.hypot(vx, vy)
            ux, uy = vx / norm * seg / 2, vy / norm * seg / 2
            cx, cy = p.X(x), p.Y(y)
            parts.append(f'<line x1="{cx-ux:.1f}" y1="{cy-uy:.1f}" x2="{cx+ux:.1f}" y2="{cy+uy:.1f}"/>')
    parts.append("</g>")
    p.add("".join(parts))


def frame(p, opacity=0.35):
    """Thin rectangle around the panel (useful behind a slope field)."""
    p.add(f'<rect x="{p.x0:.1f}" y="{p.y0:.1f}" width="{p.w:.1f}" height="{p.h:.1f}" '
          f'fill="none" stroke="{TEXT}" stroke-width="0.8" opacity="{opacity}"/>')
