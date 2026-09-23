# -*- coding: utf-8 -*-
"""
Figures of the chapter "Simpleks Yöntem"
(dersler/lineer-programlama/simpleks-yontem.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box: a figure that illustrates a
definition sits directly below that box. The figures are NOT produced at
build time. Run

    python scripts/lp_figures/smp.py
    python scripts/center_figures.py "lp-smp-*.md" --keep-width
    python scripts/check_figure_labels.py "scripts/_figures/lp-smp-*.md"

and paste the markup of scripts/_figures/lp-smp-<name>.md into the .qmd.
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
PREFIX = "lp-smp-"

MINUS = "&#8722;"
LEQ = "&#8804;"


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


def axes(p, xr, yr, xt, yt):
    p.origin_axes(xlabel="x₁", ylabel="x₂", xticks=xt, yticks=yt)


def constraint(p, a, b, c, xr, yr, color=REMARK, width=1.4, opacity=0.75):
    seg = clip_line(a, b, c, xr, yr)
    if len(seg) == 2:
        p.line(seg, color=color, width=width, opacity=opacity)


def path(p, pts, color=PRACTICE):
    for u, v in zip(pts, pts[1:]):
        p.arrow(u, v, color=color, width=2.6, head=11)


# ============================================================
# komsu-gecis: moving from X0 = (2, 2) to X1 = (4, 0) along an edge
# ============================================================
def fig_komsu_gecis():
    xr, yr = (-0.6, 6.2), (-0.6, 4.2)
    p, H = panel(xr, yr)
    p.grid(xs=range(1, 7), ys=range(1, 5))
    region = [(0, 0), (4, 0), (2, 2), (0, 3)]
    p.polygon(region, fill=THEORY, opacity=0.16, stroke=THEORY, width=1.2)
    constraint(p, 1, 1, 4, xr, yr)
    constraint(p, 1, 2, 6, xr, yr)
    axes(p, xr, yr, range(1, 7), range(1, 5))
    path(p, [(2, 2), (4, 0)])
    p.points([(2, 2), (4, 0)], color=PRACTICE, r=4.5)
    p.label(2, 2, "X₀ = (2, 2)", dx=10, dy=-10, size=13)
    p.label(4, 0, "X₁ = (4, 0)", dx=6, dy=-12, size=13)
    p.label(0.55, 3.75, "x₁ + x₂ = 4", size=12, color=REMARK)
    p.label(4.9, 0.6, "x₁ + 2x₂ = 6", size=12, color=REMARK)
    p.label(0.9, 0.9, "uygun bölge", size=12, color=THEORY)
    save("komsu-gecis", figure(
        560, int(H + 70), [p],
        "Baz değişimi uygun bölgenin bir kenarı boyunca yürümektir: x₄ baza girerken "
        "X₀ = (2, 2) köşesinden x₁ + x₂ = 4 kenarı üzerinde X₁ = (4, 0) köşesine gidilir.",
        aria="Feasible quadrilateral with corners (0,0), (4,0), (2,2), (0,3); an arrow along the edge "
             "x1 + x2 = 4 from (2,2) to (4,0)"))


# ============================================================
# simpleks-yolu: the path of the worked example (min z = -4x1 - 5x2)
# ============================================================
def fig_simpleks_yolu():
    xr, yr = (-0.6, 4.2), (-0.6, 3.6)
    p, H = panel(xr, yr, W=480)
    p.grid(xs=range(1, 5), ys=range(1, 4))
    region = [(0, 0), (2, 0), (2.8, 0.4), (7 / 3, 4 / 3), (1 / 3, 7 / 3), (0, 2)]
    p.polygon(region, fill=THEORY, opacity=0.16, stroke=THEORY, width=1.2)
    for a, b, c in ((1, -2, 2), (2, 1, 6), (1, 2, 5), (-1, 1, 2)):
        constraint(p, a, b, c, xr, yr)
    # level lines of z = -4x1 - 5x2
    for zval in (-10, -16):
        seg = clip_line(4, 5, -zval, xr, yr)
        p.line(seg, color=BASE, width=1.4, dash="6 4", opacity=0.9)
    axes(p, xr, yr, range(1, 5), range(1, 4))
    pts = [(0, 0), (0, 2), (1 / 3, 7 / 3), (7 / 3, 4 / 3)]
    path(p, pts)
    p.points(pts, color=PRACTICE, r=4.5)
    p.label(0, 0, "X₀", dx=8, dy=-8, size=13)
    p.label(0, 2, "X₁", dx=10, dy=18, size=13)
    p.label(1 / 3, 7 / 3, "X₂", dx=-6, dy=-12, size=13)
    p.label(7 / 3, 4 / 3, "X₃", dx=10, dy=-4, size=13)
    # constraint names at the panel border
    p.label(0.55, -0.5, "(1)", size=12, color=REMARK)
    p.label(3.3, -0.35, "(2)", size=12, color=REMARK)
    p.label(-0.45, 1.1, "(4)", size=12, color=REMARK)
    p.label(-0.5, 2.95, "(3)", size=12, color=REMARK)
    p.label(0.7, 1.05, "uygun bölge", size=12, color=THEORY)
    p.label(0.12, 3.3, f"z = {MINUS}16", size=12, color=BASE)
    p.label(1.3, 0.2, f"z = {MINUS}10", size=12, color=BASE)
    save("simpleks-yolu", figure(
        580, int(H + 70), [p],
        "Simpleks yolu: X₀ = (0, 0) → X₁ = (0, 2) → X₂ = (1/3, 7/3) → X₃ = (7/3, 4/3). "
        "Her adım komşu köşeye geçer ve z değeri 0, −10, −13, −16 diye azalır; kesikli doğrular "
        "z = −10 ve z = −16 seviye doğrularıdır. (1) x₁ − 2x₂ = 2, (2) 2x₁ + x₂ = 6, "
        "(3) x₁ + 2x₂ = 5, (4) −x₁ + x₂ = 2.",
        aria="Hexagonal feasible region of the worked example with the simplex path from (0,0) to (0,2) "
             "to (1/3,7/3) to (7/3,4/3) and dashed level lines z = -10 and z = -16"))


# ============================================================
# max-yolu: the 2-variable maximum example (max z = 3x1 + 2x2)
# ============================================================
def fig_max_yolu():
    xr, yr = (-0.6, 5.4), (-0.6, 4.4)
    p, H = panel(xr, yr)
    p.grid(xs=range(1, 6), ys=range(1, 5))
    region = [(0, 0), (3.5, 0), (3, 1), (2, 2), (0, 3)]
    p.polygon(region, fill=THEORY, opacity=0.16, stroke=THEORY, width=1.2)
    for a, b, c in ((1, 1, 4), (1, 2, 6), (2, 1, 7)):
        constraint(p, a, b, c, xr, yr)
    seg = clip_line(3, 2, 11, xr, yr)
    p.line(seg, color=BASE, width=1.4, dash="6 4", opacity=0.9)
    axes(p, xr, yr, range(1, 6), range(1, 5))
    pts = [(0, 0), (3.5, 0), (3, 1)]
    path(p, pts)
    p.points(pts, color=PRACTICE, r=4.5)
    p.points([(2, 2), (0, 3)], color=THEORY, r=3.5)
    p.label(0, 0, "X₀", dx=8, dy=-8, size=13)
    p.label(3.5, 0, "X₁", dx=8, dy=-8, size=13)
    p.label(3, 1, "X₂ = (3, 1)", dx=12, dy=4, size=13)
    p.label(4.6, -0.5, "x₁ + x₂ = 4", size=12, color=REMARK)
    p.label(4.2, 1.15, "x₁ + 2x₂ = 6", size=12, color=REMARK)
    p.label(1.6, 4.1, "2x₁ + x₂ = 7", size=12, color=REMARK)
    p.label(0.6, 1.0, "uygun bölge", size=12, color=THEORY)
    p.label(0.45, 3.6, "z = 11", size=12, color=BASE)
    save("max-yolu", figure(
        560, int(H + 70), [p],
        "Maksimum örneğinde simpleks yolu: X₀ = (0, 0) → X₁ = (7/2, 0) → X₂ = (3, 1). "
        "Kesikli doğru z = 3x₁ + 2x₂ = 11 seviye doğrusudur; uygun bölge bu doğrunun "
        "tamamen altında kalır ve ona yalnız X₂ köşesinde değer.",
        aria="Feasible pentagon with corners (0,0), (3.5,0), (3,1), (2,2), (0,3); simplex path "
             "from (0,0) to (3.5,0) to (3,1) and the dashed level line z = 11"))


if __name__ == "__main__":
    fig_komsu_gecis()
    fig_simpleks_yolu()
    fig_max_yolu()
