# -*- coding: utf-8 -*-
"""
Figures of the chapter "Dual Simpleks Algoritması"
(dersler/lineer-programlama/dual-simpleks-algoritmasi.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box: a figure that illustrates a
definition sits directly below that box. The figures are NOT produced at
build time. Run

    python scripts/lp_figures/dsa.py
    python scripts/center_figures.py "lp-dsa-*.md" --keep-width
    python scripts/check_figure_labels.py "scripts/_figures/lp-dsa-*.md"

and paste the markup of scripts/_figures/lp-dsa-<name>.md into the .qmd.
Captions are Turkish (they are shown on the site); aria labels are ASCII.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, TEXT, THEORY, PRACTICE, BASE, REMARK  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "lp-dsa-"


def save(name, markup):
    (OUT_DIR / f"{PREFIX}{name}.md").write_text(markup, encoding="utf-8", newline="\n")
    print("wrote", PREFIX + name)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def clip_line(a, b, c, xr, yr):
    """End points of the line a*x + b*y = c inside the box xr x yr."""
    pts = []
    x0, x1 = xr
    y0, y1 = yr
    if b != 0:
        for x in (x0, x1):
            y = (c - a * x) / b
            if y0 - 1e-9 <= y <= y1 + 1e-9:
                pts.append((x, y))
    if a != 0:
        for y in (y0, y1):
            x = (c - b * y) / a
            if x0 - 1e-9 <= x <= x1 + 1e-9:
                pts.append((x, y))
    uniq = []
    for p in pts:
        if all(abs(p[0] - q[0]) > 1e-9 or abs(p[1] - q[1]) > 1e-9 for q in uniq):
            uniq.append(p)
    return uniq[:2]


def panel(xr, yr, W=460):
    """Equal-aspect panel at a fixed left/top margin."""
    H = W * (yr[1] - yr[0]) / (xr[1] - xr[0])
    return Plot(60, 30, W, H, xr, yr), H


def constraint(p, a, b, c, xr, yr, color=REMARK, width=1.4, opacity=0.75):
    seg = clip_line(a, b, c, xr, yr)
    if len(seg) == 2:
        p.line(seg, color=color, width=width, opacity=opacity)


def level(p, a, b, c, xr, yr):
    seg = clip_line(a, b, c, xr, yr)
    p.line(seg, color=BASE, width=1.4, dash="6 4", opacity=0.9)


def path(p, pts, color=PRACTICE):
    for u, v in zip(pts, pts[1:]):
        p.arrow(u, v, color=color, width=2.6, head=11)


# ============================================================
# primal-yol: dual simplex path in the x1x2-plane
#   x1 + 2x2 >= 6, x1 + x2 >= 5, min z = 3x1 + 5x2
# ============================================================
def fig_primal_yol():
    xr, yr = (-0.6, 7.4), (-0.6, 6.0)
    p, H = panel(xr, yr, W=470)
    p.grid(xs=range(1, 8), ys=range(1, 6))
    xm, ym = 7.2, 5.8
    region = [(0, ym), (0, 5), (4, 1), (6, 0), (xm, 0), (xm, ym)]
    p.polygon(region, fill=THEORY, opacity=0.16, stroke="none")
    p.line([(0, ym), (0, 5), (4, 1), (6, 0), (xm, 0)], color=THEORY, width=1.2)
    constraint(p, 1, 2, 6, xr, yr)
    constraint(p, 1, 1, 5, xr, yr)
    level(p, 3, 5, 17, xr, yr)
    p.origin_axes(xlabel="x₁", ylabel="x₂", xticks=range(1, 8), yticks=range(1, 6))
    pts = [(0, 0), (0, 3), (4, 1)]
    path(p, pts)
    p.points(pts, color=PRACTICE, r=4.5)
    p.label(0, 0, "X₀", dx=8, dy=-8, size=13)
    p.label(0, 3, "X₁", dx=-8, dy=-14, size=13, anchor="end")
    p.label(4, 1, "X₂", dx=10, dy=-8, size=13)
    p.label(3.35, 4.3, "uygun bölge", size=12, color=THEORY)
    p.label(6.4, 0.18, "(1)", size=12, color=REMARK)
    p.label(0.55, 4.7, "(2)", size=12, color=REMARK)
    p.label(0.45, 3.4, "z = 17", size=12, color=BASE)
    save("primal-yol", figure(
        560, int(H + 70), [p],
        "Dual simpleks yolu: X₀ = (0, 0) → X₁ = (0, 3) → X₂ = (4, 1). İlk iki nokta uygun bölgenin "
        "dışındadır; z değeri 0, 15, 17 diye artarak optimuma alttan yaklaşır. Kesikli doğru "
        "z = 17 seviye doğrusudur. (1) x₁ + 2x₂ = 6, (2) x₁ + x₂ = 5.",
        aria="Unbounded feasible region above the lines x1 + 2x2 = 6 and x1 + x2 = 5; dual simplex path "
             "from (0,0) to (0,3) to (4,1) with the dashed level line z = 17"))


# ============================================================
# dual-yol: the same iterations seen in the dual problem
#   y1 + y2 <= 3, 2y1 + y2 <= 5, max g = 6y1 + 5y2
# ============================================================
def fig_dual_yol():
    xr, yr = (-0.5, 3.7), (-0.5, 3.7)
    p, H = panel(xr, yr, W=440)
    p.grid(xs=range(1, 4), ys=range(1, 4))
    region = [(0, 0), (2.5, 0), (2, 1), (0, 3)]
    p.polygon(region, fill=THEORY, opacity=0.16, stroke=THEORY, width=1.2)
    constraint(p, 1, 1, 3, xr, yr)
    constraint(p, 2, 1, 5, xr, yr)
    level(p, 6, 5, 17, xr, yr)
    p.origin_axes(xlabel="y₁", ylabel="y₂", xticks=range(1, 4), yticks=range(1, 4))
    pts = [(0, 0), (2.5, 0), (2, 1)]
    path(p, pts)
    p.points(pts, color=PRACTICE, r=4.5)
    p.points([(0, 3)], color=THEORY, r=3.5)
    p.label(0, 0, "Y₀", dx=8, dy=-8, size=13)
    p.label(2.5, 0, "Y₁", dx=-10, dy=18, size=13, anchor="end")
    p.label(2, 1, "Y₂", dx=-12, dy=16, size=13, anchor="end")
    p.label(0.45, 0.7, "dual uygun bölge", size=12, color=THEORY)
    p.label(3.2, 0.12, "(1)", size=12, color=REMARK)
    p.label(0.85, 3.45, "(2)", size=12, color=REMARK)
    p.label(0.12, 3.5, "g = 17", size=12, color=BASE)
    save("dual-yol", figure(
        560, int(H + 70), [p],
        "Aynı iterasyonlar dual problemde: Y₀ = (0, 0) → Y₁ = (5/2, 0) → Y₂ = (2, 1). Her nokta dual "
        "uygun bölgenin bir köşesidir ve g değeri 0, 15, 17 diye artar; kesikli doğru g = 17 seviye "
        "doğrusudur. (1) y₁ + y₂ = 3, (2) 2y₁ + y₂ = 5.",
        aria="Dual feasible quadrilateral with corners (0,0), (2.5,0), (2,1), (0,3); simplex path from "
             "(0,0) to (2.5,0) to (2,1) and the dashed level line g = 17"))


if __name__ == "__main__":
    fig_primal_yol()
    fig_dual_yol()
