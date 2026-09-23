# -*- coding: utf-8 -*-
"""
Figures of the chapter "İki Faz Yöntemi"
(dersler/lineer-programlama/iki-faz-yontemi.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box: a figure that illustrates a
definition sits directly below that box. The figures are NOT produced at
build time. Run

    python scripts/lp_figures/ifz.py
    python scripts/center_figures.py "lp-ifz-*.md" --keep-width
    python scripts/check_figure_labels.py "scripts/_figures/lp-ifz-*.md"

and paste the markup of scripts/_figures/lp-ifz-<name>.md into the .qmd.
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
PREFIX = "lp-ifz-"

MINUS = "&#8722;"


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


def constraint(p, a, b, c, xr, yr, color=REMARK, width=1.5, opacity=0.8):
    seg = clip_line(a, b, c, xr, yr)
    if len(seg) == 2:
        p.line(seg, color=color, width=width, opacity=opacity)


def path(p, pts, color=PRACTICE):
    for u, v in zip(pts, pts[1:]):
        p.arrow(u, v, color=color, width=2.6, head=11)


# ============================================================
# isinma-yolu: phase 1 path of the diet example, (0,0) -> (0,2) -> (3,1)
# ============================================================
def fig_isinma_yolu():
    xr, yr = (-0.6, 7.4), (-0.6, 5.4)
    p, H = panel(xr, yr, W=480)
    p.grid(xs=range(1, 8), ys=range(1, 6))
    # feasible region x1 + x2 >= 4, x1 + 3x2 >= 6, x >= 0, clipped to the panel
    region = [(0, 5.4), (0, 4), (3, 1), (6, 0), (7.4, 0), (7.4, 5.4)]
    p.polygon(region, fill=THEORY, opacity=0.16, stroke="none")
    p.line([(0, 4), (3, 1), (6, 0)], color=THEORY, width=1.2)
    constraint(p, 1, 1, 4, xr, yr)
    constraint(p, 1, 3, 6, xr, yr)
    for zval in (9, 12):
        seg = clip_line(2, 3, zval, xr, yr)
        p.line(seg, color=BASE, width=1.4, dash="6 4", opacity=0.9)
    p.origin_axes(xlabel="x₁", ylabel="x₂", xticks=range(1, 8), yticks=range(1, 6))
    pts = [(0, 0), (0, 2), (3, 1)]
    path(p, pts)
    p.points(pts, color=PRACTICE, r=4.5)
    p.points([(0, 4), (6, 0)], color=THEORY, r=4.0)
    p.label(0, 0, "(0, 0)", dx=8, dy=-8, size=13)
    p.label(0, 2, "(0, 2)", dx=10, dy=4, size=13)
    p.label(3, 1, "(3, 1)", dx=-12, dy=20, size=13, anchor="end")
    p.label(0, 4, "(0, 4)", dx=10, dy=-4, size=13)
    p.label(6, 0, "(6, 0)", dx=-4, dy=-10, size=13)
    p.label(4.6, 4.3, "uygun bölge", size=12, color=THEORY)
    p.label(1.25, 3.25, "x₁ + x₂ = 4", size=12, color=REMARK)
    p.label(6.0, 0.62, "x₁ + 3x₂ = 6", size=12, color=REMARK, anchor="middle")
    p.label(5.5, -0.5, "z = 9", size=12, color=BASE)
    p.label(1.0, 3.75, "z = 12", size=12, color=BASE)
    save("isinma-yolu", figure(
        580, int(H + 70), [p],
        "Birinci fazın izlediği yol: (0, 0) → (0, 2) → (3, 1). İlk iki nokta uygun bölgenin "
        "dışındadır (yapay değişkenler pozitiftir); (3, 1) köşesine gelindiğinde g = 0 olur. "
        "İkinci faz bu köşeden başlar ve kesikli z = 9 seviye doğrusu onun optimal olduğunu gösterir.",
        aria="Unbounded feasible region above x1 + x2 = 4 and x1 + 3x2 = 6 with corners (0,4), (3,1), "
             "(6,0); the phase one path goes from (0,0) to (0,2) to (3,1); dashed level lines z = 9 "
             "and z = 12"))


# ============================================================
# bos-bolge: x1 + x2 <= 2 and x1 + 2x2 >= 6 do not meet in the first quadrant
# ============================================================
def fig_bos_bolge():
    xr, yr = (-0.6, 7.0), (-0.6, 4.4)
    p, H = panel(xr, yr, W=480)
    p.grid(xs=range(1, 8), ys=range(1, 5))
    p.polygon([(0, 0), (2, 0), (0, 2)], fill=THEORY, opacity=0.20,
              stroke=THEORY, width=1.2)
    p.polygon([(0, 3), (6, 0), (7.0, 0), (7.0, 4.4), (0, 4.4)], fill=REMARK,
              opacity=0.14, stroke="none")
    constraint(p, 1, 1, 2, xr, yr, color=THEORY)
    constraint(p, 1, 2, 6, xr, yr, color=REMARK)
    p.origin_axes(xlabel="x₁", ylabel="x₂", xticks=range(1, 7), yticks=range(1, 5))
    path(p, [(0, 0), (0, 2)])
    p.points([(0, 0), (0, 2)], color=PRACTICE, r=4.5)
    p.label(0, 0, "(0, 0)", dx=8, dy=-8, size=13)
    p.label(0, 2, "(0, 2)", dx=10, dy=-6, size=13)
    p.label(0.35, 0.55, "x₁ + x₂ ≤ 2", size=12, color=THEORY)
    p.label(3.9, 3.3, "x₁ + 2x₂ ≥ 6", size=12, color=REMARK)
    save("bos-bolge", figure(
        580, int(H + 70), [p],
        "x₁ + x₂ ≤ 2 üçgeni ile x₁ + 2x₂ ≥ 6 yarı düzlemi birinci bölgede kesişmez; uygun çözüm "
        "yoktur. Birinci faz (0, 0) noktasından (0, 2) köşesine gider ve orada durur: bu noktada "
        "x₁ + 2x₂ = 4 olup 6'ya 2 birim eksiktir, yani yapay değişken 2 değerinde kalır.",
        aria="Triangle x1 + x2 at most 2 and the half plane x1 + 2x2 at least 6 are disjoint in the "
             "first quadrant; phase one moves from (0,0) to (0,2) and stops"))


if __name__ == "__main__":
    fig_isinma_yolu()
    fig_bos_bolge()
