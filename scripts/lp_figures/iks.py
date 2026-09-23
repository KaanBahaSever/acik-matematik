# -*- coding: utf-8 -*-
"""
Figures of the chapter "İşaret Kısıtlaması Olmayan Değişkenler"
(dersler/lineer-programlama/isaret-kisitlamasiz-degiskenler.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box: a figure that illustrates a
definition sits directly below that box. The figures are NOT produced at
build time. Run

    python scripts/lp_figures/iks.py
    python scripts/center_figures.py "lp-iks-*.md" --keep-width
    python scripts/check_figure_labels.py "scripts/_figures/lp-iks-*.md"

and paste the markup of scripts/_figures/lp-iks-<name>.md into the .qmd.
Captions are Turkish (they are shown on the site); aria labels are ASCII.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, THEORY, PRACTICE, BASE, REMARK  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "lp-iks-"

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


def panel(xr, yr, W=480):
    """Equal-aspect panel at a fixed left/top margin."""
    H = W * (yr[1] - yr[0]) / (xr[1] - xr[0])
    return Plot(60, 30, W, H, xr, yr), H


def constraint(p, a, b, c, xr, yr, color=REMARK, width=1.6, opacity=0.8):
    seg = clip_line(a, b, c, xr, yr)
    if len(seg) == 2:
        p.line(seg, color=color, width=width, opacity=opacity)


def level(p, a, b, c, xr, yr):
    seg = clip_line(a, b, c, xr, yr)
    if len(seg) == 2:
        p.line(seg, color=BASE, width=1.4, dash="6 4", opacity=0.9)


# ============================================================
# ornek1: min z = x1 + x2, x1 free, -x1 + 2x2 <= 6, x1 - x2 <= 4, x2 >= 0
# ============================================================
def fig_ornek1():
    xr, yr = (-8.5, 16.5), (-1.5, 11.5)
    p, H = panel(xr, yr, W=500)
    p.grid(xs=[x for x in range(-8, 17, 2) if x != 0], ys=range(2, 12, 2))
    full = [(-6, 0), (4, 0), (14, 10)]
    quad = [(0, 0), (4, 0), (14, 10), (0, 3)]
    p.polygon(full, fill=THEORY, opacity=0.16, stroke=THEORY, width=1.2)
    p.polygon(quad, fill=PRACTICE, opacity=0.16, stroke="none")
    constraint(p, -1, 2, 6, xr, yr)
    constraint(p, 1, -1, 4, xr, yr)
    level(p, 1, 1, -6, xr, yr)
    level(p, 1, 1, 0, xr, yr)
    p.origin_axes(xlabel="x₁", ylabel="x₂",
                  xticks=[-4, 4, 8, 12], yticks=range(2, 12, 2))
    # direction in which z decreases
    p.arrow((13.5, 3.2), (11.5, 1.2), color=BASE, width=2.0, head=10)
    p.label(13.2, 3.6, "z azalır", size=12, color=BASE)
    p.points([(-6, 0)], color=PRACTICE, r=5)
    p.points([(0, 0)], color=REMARK, r=4.5)
    p.label(-6, 0, f"({MINUS}6, 0)", dx=-6, dy=18, size=13, anchor="end")
    p.label(0, 0, "(0, 0)", dx=-6, dy=18, size=12, anchor="end")
    p.label(5.5, 4.2, "x₁ ≥ 0", size=12, color=PRACTICE)
    p.label(-3.9, 0.45, "x₁ &lt; 0", size=12, color=THEORY)
    p.label(8.4, 8.3, "(1)", size=12, color=REMARK)
    p.label(10.2, 5.4, "(2)", size=12, color=REMARK)
    p.label(-7.9, 3.1, f"z = {MINUS}6", size=12, color=BASE)
    p.label(-5.4, 7.0, "z = 0", size=12, color=BASE)
    save("ornek1", figure(
        580, int(H + 70), [p],
        "Uygun bölge (−6, 0), (4, 0), (14, 10) köşeli üçgendir ve x₁ ekseninin soluna taşar. "
        "Kesikli doğrular z = x₁ + x₂ = −6 ve z = 0 seviye doğrularıdır; ok z'nin azaldığı yönü "
        "gösterir. Minimum (−6, 0) köşesinde alınır. x₁ ≥ 0 da istenseydi yalnız koyu renkli "
        "kısım kalır ve minimum (0, 0) noktasında z = 0 olurdu. (1) −x₁ + 2x₂ = 6, (2) x₁ − x₂ = 4.",
        aria="Feasible triangle with corners (-6,0), (4,0), (14,10) extending left of the x2 axis; "
             "dashed level lines z = -6 and z = 0; minimum at (-6,0); the part with x1 nonnegative is shaded darker"))


# ============================================================
# ek: max z = x1 + 4x2, x1 free, -x1 + x2 <= 4, x1 + 2x2 <= 2, x2 >= 0
# ============================================================
def fig_ek():
    xr, yr = (-5.3, 3.6), (-0.8, 3.4)
    p, H = panel(xr, yr, W=500)
    p.grid(xs=[x for x in range(-5, 4) if x != 0], ys=range(1, 4))
    full = [(-4, 0), (2, 0), (-2, 2)]
    sub = [(0, 0), (2, 0), (0, 1)]
    p.polygon(full, fill=THEORY, opacity=0.16, stroke=THEORY, width=1.2)
    p.polygon(sub, fill=PRACTICE, opacity=0.18, stroke="none")
    constraint(p, -1, 1, 4, xr, yr)
    constraint(p, 1, 2, 2, xr, yr)
    level(p, 1, 4, 4, xr, yr)
    level(p, 1, 4, 6, xr, yr)
    p.origin_axes(xlabel="x₁", ylabel="x₂",
                  xticks=[x for x in range(-5, 4) if x != 0], yticks=range(1, 4))
    # gradient of z = x1 + 4x2
    g0 = (1.3, 1.55)
    p.arrow(g0, (g0[0] + 0.2, g0[1] + 0.8), color=BASE, width=2.0, head=10)
    p.label(g0[0] + 0.28, g0[1] + 0.55, "z artar", size=12, color=BASE)
    # simplex path
    for u, v in (((0, 0), (0, 1)), ((0, 1), (-2, 2))):
        p.arrow(u, v, color=PRACTICE, width=2.6, head=11)
    p.points([(0, 0), (0, 1), (-2, 2)], color=PRACTICE, r=4.5)
    p.label(0, 0, "X₀", dx=8, dy=-8, size=13)
    p.label(0, 1, "X₁", dx=10, dy=4, size=13)
    p.label(-2, 2, "X₂", dx=-6, dy=-12, size=13, anchor="middle")
    p.label(-1.5, 2.95, "(1)", size=12, color=REMARK)
    p.label(2.2, -0.65, "(2)", size=12, color=REMARK)
    p.label(-2.5, 3.05, "z = 6", size=12, color=BASE)
    p.label(-5.1, 2.45, "z = 4", size=12, color=BASE)
    p.label(-3.2, 0.25, "uygun bölge", size=12, color=THEORY)
    save("ek", figure(
        580, int(H + 70), [p],
        "Uygun bölge (−4, 0), (2, 0), (−2, 2) köşeli üçgendir; koyu renkli (0, 0), (2, 0), (0, 1) "
        "üçgeni onun x₁ ≥ 0 olan kısmıdır. Simpleks yöntem X₀ = (0, 0) → X₁ = (0, 1) → "
        "X₂ = (−2, 2) yolunu izler. X₁'de z = 4 ile koyu üçgenin en iyisine ulaşılır; x₁ negatif "
        "olabildiği için yöntem durmaz ve z = 6 değerini veren X₂'ye geçer. (1) −x₁ + x₂ = 4, (2) x₁ + 2x₂ = 2.",
        aria="Feasible triangle with corners (-4,0), (2,0), (-2,2); the part with x1 nonnegative is the smaller "
             "triangle (0,0), (2,0), (0,1); simplex path (0,0) to (0,1) to (-2,2); dashed level lines z = 4 and z = 6"))


if __name__ == "__main__":
    fig_ornek1()
    fig_ek()
