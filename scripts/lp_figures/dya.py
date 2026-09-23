# -*- coding: utf-8 -*-
"""
Figures of the chapter "Duyarlılık Analizi"
(dersler/lineer-programlama/duyarlilik-analizi.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box: a figure that illustrates a
definition sits directly below that box. The figures are NOT produced at
build time. Run

    python scripts/lp_figures/dya.py
    python scripts/center_figures.py "lp-dya-*.md" --keep-width
    python scripts/check_figure_labels.py "scripts/_figures/lp-dya-*.md"

and paste the markup of scripts/_figures/lp-dya-<name>.md into the .qmd.
Captions are Turkish (they are shown on the site); aria labels are ASCII.
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, THEORY, PRACTICE, BASE, REMARK  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "lp-dya-"


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


def constraint(p, a, b, c, xr, yr, color=REMARK, width=1.4, opacity=0.75, dash=None):
    seg = clip_line(a, b, c, xr, yr)
    if len(seg) == 2:
        p.line(seg, color=color, width=width, opacity=opacity, dash=dash)


def level(p, a, b, c, xr, yr, color=BASE, dash="6 4"):
    seg = clip_line(a, b, c, xr, yr)
    if len(seg) == 2:
        p.line(seg, color=color, width=1.5, dash=dash, opacity=0.9)


def cone(p, v, d1, d2, r, color=PRACTICE, opacity=0.18, samples=24):
    """Filled sector at vertex v between the directions d1 and d2 (radius r)."""
    a1 = math.atan2(d1[1], d1[0])
    a2 = math.atan2(d2[1], d2[0])
    pts = [v]
    for k in range(samples + 1):
        a = a1 + (a2 - a1) * k / samples
        pts.append((v[0] + r * math.cos(a), v[1] + r * math.sin(a)))
    p.polygon(pts, fill=color, opacity=opacity)


def legend(p, x, y, dy, entries, length=0.45):
    """Line samples with labels, one entry per row, starting at data (x, y)."""
    for k, (color, dash, width, text) in enumerate(entries):
        yy = y - k * dy
        p.line([(x, yy), (x + length, yy)], color=color, width=width, dash=dash, opacity=0.95)
        p.label(x + length, yy, text, dx=8, dy=4, size=12, color=color)


def unit(d, r):
    n = math.hypot(*d)
    return (d[0] / n * r, d[1] / n * r)


# ============================================================
# temel-disi-egim: max z = 5x1 + c2 x2, x2 nonbasic, c2 <= 5/2
# ============================================================
def fig_temel_disi_egim():
    xr, yr = (-0.6, 5.2), (-0.6, 4.8)
    p, H = panel(xr, yr, W=470)
    p.grid(xs=range(1, 6), ys=range(1, 5))
    region = [(0, 0), (3, 0), (2, 2), (0, 4)]
    p.polygon(region, fill=THEORY, opacity=0.16, stroke=THEORY, width=1.2)
    constraint(p, 1, 1, 4, xr, yr)
    constraint(p, 2, 1, 6, xr, yr)
    # the edge (3,0)-(2,2) is the level line for c2 = 5/2
    p.line([(3, 0), (2, 2)], color=PRACTICE, width=3.2)
    # c2 = 2 (current) and c2 = 4 (outside the range) through (3, 0)
    level(p, 5, 2, 15, xr, yr, color=BASE)
    level(p, 5, 4, 15, xr, yr, color=THEORY, dash="3 4")
    p.origin_axes(xlabel="x₁", ylabel="x₂", xticks=range(1, 6), yticks=range(1, 5))
    p.points([(3, 0)], color=PRACTICE, r=4.5)
    p.points([(2, 2)], color=THEORY, r=4.0)
    p.label(3, 0, "(3, 0)", dx=10, dy=-8, size=13)
    p.label(2, 2, "(2, 2)", dx=-44, dy=-8, size=13)
    p.label(3.52, 0.62, "x₁ + x₂ = 4", size=12, color=REMARK)
    p.label(0.5, 0.6, "uygun bölge", size=12, color=THEORY)
    legend(p, 2.75, 4.4, 0.42, [
        (BASE, "6 4", 1.5, "c₂ = 2"),
        (PRACTICE, None, 3.2, "c₂ = 5/2 (kenar)"),
        (THEORY, "3 4", 1.5, "c₂ = 4"),
    ])
    save("temel-disi-egim", figure(
        560, int(H + 70), [p],
        "z = 5x₁ + c₂x₂ amaç fonksiyonunun (3, 0) köşesinden geçen seviye doğruları. "
        "c₂ = 2 iken doğru bölgenin dışından geçer ve (3, 0) tek optimal köşedir. c₂ büyüdükçe doğru "
        "yatıklaşır; c₂ = 5/2 olunca 2x₁ + x₂ = 6 kenarının üzerine oturur (kalın kenar). "
        "c₂ = 4 iken doğru bölgeyi keser ve (2, 2) köşesi daha büyük z verir.",
        aria="Feasible quadrilateral (0,0), (3,0), (2,2), (0,4); level lines of 5x1 + c2 x2 through "
             "(3,0) for c2 = 2, c2 = 5/2 (on the edge 2x1 + x2 = 6) and c2 = 4"))


# ============================================================
# temelde-yelpaze: max z = c1 x1 + 2x2 at (2, 2), 2 <= c1 <= 4
# ============================================================
def fig_temelde_yelpaze():
    xr, yr = (-0.6, 5.2), (-0.6, 4.8)
    p, H = panel(xr, yr, W=470)
    p.grid(xs=range(1, 6), ys=range(1, 5))
    region = [(0, 0), (3, 0), (2, 2), (0, 4)]
    p.polygon(region, fill=THEORY, opacity=0.16, stroke=THEORY, width=1.2)
    constraint(p, 1, 1, 4, xr, yr, color=PRACTICE, width=2.4, opacity=0.9)
    constraint(p, 2, 1, 6, xr, yr, color=REMARK, width=2.4, opacity=0.9)
    # current level line c1 = 3
    level(p, 3, 2, 10, xr, yr, color=BASE)
    v = (2, 2)
    # gradients (2,2) and (4,2) are the normals of the two edges
    cone(p, v, (1, 1), (2, 1), 1.35)
    p.arrow(v, (v[0] + unit((3, 2), 1.35)[0], v[1] + unit((3, 2), 1.35)[1]),
            color=BASE, width=2.0, head=10)
    p.origin_axes(xlabel="x₁", ylabel="x₂", xticks=range(1, 6), yticks=range(1, 5))
    p.points([v], color=PRACTICE, r=4.5)
    p.label(2, 2, "(2, 2)", dx=-50, dy=-4, size=13)
    p.label(3.25, 2.95, "c = (3, 2)", size=12, color=BASE)
    legend(p, 2.55, 4.45, 0.4, [
        (PRACTICE, None, 2.4, "c₁ = 2:  x₁ + x₂ = 4"),
        (BASE, "6 4", 1.5, "c₁ = 3:  3x₁ + 2x₂ = 10"),
        (REMARK, None, 2.4, "c₁ = 4:  2x₁ + x₂ = 6"),
    ])
    p.label(0.5, 0.6, "uygun bölge", size=12, color=THEORY)
    save("temelde-yelpaze", figure(
        560, int(H + 70), [p],
        "z = c₁x₁ + 2x₂ için (2, 2) köşesi. c₁ = 3 iken kesikli seviye doğrusu bölgeye yalnız bu köşede "
        "değer. c₁ = 2 olunca seviye doğrusu x₁ + x₂ = 4 kenarına, c₁ = 4 olunca 2x₁ + x₂ = 6 kenarına "
        "oturur. Gradyan c = (c₁, 2) açık boyalı açının içinde kaldıkça, yani 2 ≤ c₁ ≤ 4 iken, (2, 2) optimal kalır.",
        aria="Feasible quadrilateral with vertex (2,2) between the edges x1 + x2 = 4 and 2x1 + x2 = 6; "
             "dashed level line 3x1 + 2x2 = 10, gradient arrow (3,2) inside the shaded cone of the "
             "edge normals (1,1) and (2,1)"))


# ============================================================
# min-yelpaze: min z = c1 x1 + 3x2 at (3, 1), 1 <= c1 <= 3
# ============================================================
def fig_min_yelpaze():
    xr, yr = (-0.6, 7.4), (-0.6, 5.0)
    p, H = panel(xr, yr, W=500)
    p.grid(xs=range(1, 8), ys=range(1, 5))
    region = [(0, 5.0), (0, 4), (3, 1), (6, 0), (7.4, 0), (7.4, 5.0)]
    p.polygon(region, fill=THEORY, opacity=0.16)
    p.line([(0, 5.0), (0, 4), (3, 1), (6, 0), (7.4, 0)], color=THEORY, width=1.2)
    constraint(p, 1, 1, 4, xr, yr, color=PRACTICE, width=2.4, opacity=0.9)
    constraint(p, 1, 3, 6, xr, yr, color=REMARK, width=2.4, opacity=0.9)
    level(p, 2, 3, 9, xr, yr, color=BASE)
    v = (3, 1)
    # minimum: -grad must lie in the cone of the outward normals -(1,1), -(1,3)
    cone(p, v, (-1, -1), (-1, -3), 1.2)
    g = unit((-2, -3), 1.2)
    p.arrow(v, (v[0] + g[0], v[1] + g[1]), color=BASE, width=2.0, head=10)
    p.origin_axes(xlabel="x₁", ylabel="x₂", xticks=range(1, 8), yticks=range(1, 5))
    p.points([v], color=PRACTICE, r=4.5)
    p.label(3, 1, "(3, 1)", dx=10, dy=-8, size=13)
    p.label(2.05, 0.3, "−c = (−2, −3)", size=12, color=BASE, anchor="end")
    p.label(5.0, 2.2, "uygun bölge", size=12, color=THEORY)
    legend(p, 3.75, 4.55, 0.42, [
        (REMARK, None, 2.4, "c₁ = 1:  x₁ + 3x₂ = 6"),
        (BASE, "6 4", 1.5, "c₁ = 2:  2x₁ + 3x₂ = 9"),
        (PRACTICE, None, 2.4, "c₁ = 3:  x₁ + x₂ = 4"),
    ])
    save("min-yelpaze", figure(
        580, int(H + 70), [p],
        "min z = c₁x₁ + 3x₂ için (3, 1) köşesi. c₁ = 2 iken kesikli seviye doğrusu bölgeye yalnız bu "
        "köşede değer. c₁ = 3 olunca seviye doğrusu x₁ + x₂ = 4 kenarına, c₁ = 1 olunca x₁ + 3x₂ = 6 "
        "kenarına oturur. Minimumda seviye doğrusu gradyanın tersi −c = (−c₁, −3) yönünde kaydırılır; −c açık boyalı açının "
        "içinde kaldıkça, yani 1 ≤ c₁ ≤ 3 iken, (3, 1) optimal kalır.",
        aria="Unbounded feasible region above the lines x1 + x2 = 4 and x1 + 3x2 = 6 with vertex (3,1); "
             "dashed level line 2x1 + 3x2 = 9 and the arrow -grad z = (-2,-3) inside the shaded cone"))


# ============================================================
# sag-taraf-kayma: b1 of x1 + x2 <= b1 moves the optimal vertex
# ============================================================
def fig_sag_taraf_kayma():
    xr, yr = (-0.6, 6.6), (-0.6, 6.8)
    p, H = panel(xr, yr, W=420)
    p.grid(xs=range(1, 7), ys=range(1, 7))
    region = [(0, 0), (3, 0), (2, 2), (0, 4)]
    p.polygon(region, fill=THEORY, opacity=0.16, stroke=THEORY, width=1.2)
    constraint(p, 2, 1, 6, xr, yr)
    constraint(p, 1, 1, 4, xr, yr, color=THEORY, width=1.8, opacity=0.9)
    constraint(p, 1, 1, 3, xr, yr, color=BASE, dash="6 4", opacity=0.9)
    constraint(p, 1, 1, 6, xr, yr, color=BASE, dash="6 4", opacity=0.9)
    # the optimal vertex (6 - b1, 2b1 - 6) walks along 2x1 + x2 = 6
    p.line([(3, 0), (0, 6)], color=PRACTICE, width=3.2)
    p.origin_axes(xlabel="x₁", ylabel="x₂", xticks=range(1, 7), yticks=range(1, 7))
    p.points([(3, 0), (2, 2), (0, 6)], color=PRACTICE, r=4.5)
    p.label(3, 0, "b₁ = 3", dx=-12, dy=-6, size=13, anchor="end")
    p.label(2, 2, "b₁ = 4", dx=10, dy=4, size=13)
    p.label(0, 6, "b₁ = 6", dx=10, dy=-6, size=13)
    p.label(4.3, 1.95, "x₁ + x₂ = 6", size=12, color=BASE)
    p.label(3.55, 0.75, "x₁ + x₂ = 4", size=12, color=THEORY)
    p.label(0.08, -0.45, "x₁ + x₂ = 3", size=12, color=BASE)
    p.label(0.3, 0.6, "uygun bölge", size=12, color=THEORY)
    save("sag-taraf-kayma", figure(
        560, int(H + 70), [p],
        "x₁ + x₂ ≤ b₁ kısıtının sağ tarafı değiştikçe kısıt doğrusu kendine paralel kayar. Optimal köşe "
        "(6 − b₁, 2b₁ − 6) noktasıdır ve 2x₁ + x₂ = 6 doğrusunun kalın çizilen parçası boyunca yürür: "
        "b₁ = 3 iken (3, 0), b₁ = 4 iken (2, 2), b₁ = 6 iken (0, 6). Bu aralığın dışında köşenin bir "
        "koordinatı negatif olur.",
        aria="Feasible region for b1 = 4 and the parallel lines x1 + x2 = 3, 4, 6; the optimal vertex "
             "moves along 2x1 + x2 = 6 from (3,0) to (0,6)"))


if __name__ == "__main__":
    fig_temel_disi_egim()
    fig_temelde_yelpaze()
    fig_min_yelpaze()
    fig_sag_taraf_kayma()
