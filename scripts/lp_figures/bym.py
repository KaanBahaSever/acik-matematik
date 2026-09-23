# -*- coding: utf-8 -*-
"""
Figures of the chapter "Büyük M Yöntemi"
(dersler/lineer-programlama/buyuk-m-yontemi.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box: a figure that illustrates a
definition sits directly below that box. The figures are NOT produced at
build time. Run

    python scripts/lp_figures/bym.py
    python scripts/center_figures.py "lp-bym-*.md" --keep-width
    python scripts/check_figure_labels.py "scripts/_figures/lp-bym-*.md"

and paste the markup of scripts/_figures/lp-bym-<name>.md into the .qmd.
Captions are Turkish (they are shown on the site); aria labels are ASCII.

Every figure compares the path of the Big M method with the graphical
picture: points where an artificial variable is still positive lie outside
the feasible region and are drawn hollow.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, THEORY, PRACTICE, BASE, REMARK  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "lp-bym-"

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


def axes(p, xt, yt):
    p.origin_axes(xlabel="x₁", ylabel="x₂", xticks=xt, yticks=yt)


def constraint(p, a, b, c, xr, yr, color=REMARK, width=1.5, opacity=0.8):
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
# ornek: the worked minimum example, min z = -3x1 + x2
# ============================================================
def fig_ornek():
    xr, yr = (-0.5, 3.9), (-0.5, 2.3)
    p, H = panel(xr, yr, W=480)
    p.grid(xs=range(1, 4), ys=range(1, 3))
    region = [(1, 0), (3, 0), (0.6, 0.8)]
    p.polygon(region, fill=THEORY, opacity=0.18, stroke=THEORY, width=1.2)
    constraint(p, 2, 1, 2, xr, yr)
    constraint(p, 1, 3, 3, xr, yr)
    level(p, 3, -1, 3, xr, yr)      # z = -3
    level(p, 3, -1, 9, xr, yr)      # z = -9
    axes(p, range(1, 4), range(1, 3))
    path(p, [(0, 0), (1, 0), (3, 0)])
    p.hollow_points([(0, 0)], color=PRACTICE, r=5)
    p.points([(1, 0), (3, 0)], color=PRACTICE, r=4.5)
    p.label(0, 0, "X₀", dx=-22, dy=-8, size=13)
    p.label(1, 0, "X₁", dx=-32, dy=-6, size=13)
    p.label(3, 0, "X₂", dx=-24, dy=-10, size=13)
    p.label(0.08, 2.12, "2x₁ + x₂ = 2", size=12, color=REMARK)
    p.label(1.95, 0.55, "x₁ + 3x₂ = 3", size=12, color=REMARK)
    p.label(1.72, 1.75, f"z = {MINUS}3", size=12, color=BASE)
    p.label(3.47, 1.0, f"z = {MINUS}9", size=12, color=BASE)
    p.label(1.25, 0.22, "uygun bölge", size=12, color=THEORY)
    save("ornek", figure(
        580, int(H + 70), [p],
        "Örneğin uygun bölgesi (boyalı üçgen) ve Büyük M yönteminin yolu: "
        "X₀ = (0, 0) → X₁ = (1, 0) → X₂ = (3, 0). İçi boş çizilen X₀ uygun bölgenin dışındadır; "
        "orada 2x₁ + x₂ ≥ 2 kısıtı sağlanmaz ve eksik kalan 2 birimi yapay değişken üstlenir. "
        "Kesikli doğrular z = −3 ve z = −9 seviye doğrularıdır. x₂ ≤ 4 kısıtı şeklin üstünde "
        "kalır ve bölgeyi etkilemez.",
        aria="Feasible triangle with corners (1,0), (3,0), (3/5,4/5); the Big M path goes from "
             "the infeasible origin to (1,0) and then to the optimal corner (3,0); dashed level "
             "lines z = -3 and z = -9"))


# ============================================================
# iki-yapay: the diet example with two artificial variables
# ============================================================
def fig_iki_yapay():
    xr, yr = (-0.5, 7.3), (-0.5, 5.3)
    p, H = panel(xr, yr, W=480)
    p.grid(xs=range(1, 8), ys=range(1, 6))
    region = [(0, 4), (0, 5.3), (7.3, 5.3), (7.3, 0), (6, 0), (3, 1)]
    p.polygon(region, fill=THEORY, opacity=0.16, stroke="none")
    p.line([(0, 5.3), (0, 4), (3, 1), (6, 0), (7.3, 0)], color=THEORY, width=1.2)
    constraint(p, 1, 1, 4, xr, yr)
    constraint(p, 1, 3, 6, xr, yr)
    level(p, 2, 3, 9, xr, yr)
    axes(p, range(1, 8), range(1, 6))
    pts = [(0, 0), (0, 2), (3, 1)]
    path(p, pts)
    p.hollow_points(pts[:2], color=PRACTICE, r=5)
    p.points(pts[2:], color=PRACTICE, r=4.5)
    p.label(0, 0, "X₀", dx=8, dy=-8, size=13)
    p.label(0, 2, "X₁", dx=10, dy=-6, size=13)
    p.label(3, 1, "X₂ = (3, 1)", dx=12, dy=4, size=13)
    p.label(4.25, 4.2, "uygun bölge", size=12, color=THEORY)
    p.label(0.3, 4.3, "x₁ + x₂ = 4", size=12, color=REMARK)
    p.label(5.05, 0.75, "x₁ + 3x₂ = 6", size=12, color=REMARK)
    p.label(5.3, -0.45, "z = 9", size=12, color=BASE)
    save("iki-yapay", figure(
        580, int(H + 70), [p],
        "Diyet örneğinde Büyük M yolu: X₀ = (0, 0) → X₁ = (0, 2) → X₂ = (3, 1). "
        "İçi boş çizilen ilk iki nokta sınırsız uygun bölgenin (boyalı) dışındadır; "
        "yapay değişkenlerin toplamı 10'dan 2'ye, sonra 0'a iner. Kesikli doğru "
        "z = 2x₁ + 3x₂ = 9 seviye doğrusudur ve uygun bölgeye yalnız (3, 1) köşesinde değer.",
        aria="Unbounded feasible region above the lines x1 + x2 = 4 and x1 + 3x2 = 6 with "
             "corners (0,4), (3,1), (6,0); Big M path from (0,0) to (0,2) to (3,1); dashed "
             "level line z = 9"))


# ============================================================
# max: max z = 2x1 + x2 with a >= and an = constraint
# ============================================================
def fig_max():
    xr, yr = (-0.5, 5.5), (-0.5, 4.5)
    p, H = panel(xr, yr, W=480)
    p.grid(xs=range(1, 6), ys=range(1, 5))
    constraint(p, 1, 1, 3, xr, yr)
    constraint(p, 1, -1, 1, xr, yr)
    constraint(p, 1, 2, 10, xr, yr)
    level(p, 2, 1, 11, xr, yr)
    p.line([(2, 1), (4, 3)], color=THEORY, width=6, opacity=0.55)
    axes(p, range(1, 6), range(1, 5))
    pts = [(0, 0), (1, 0), (2, 1), (4, 3)]
    path(p, pts)
    p.hollow_points(pts[:2], color=PRACTICE, r=5)
    p.points(pts[2:], color=PRACTICE, r=4.5)
    p.label(0, 0, "X₀", dx=-22, dy=-8, size=13)
    p.label(1, 0, "X₁", dx=-26, dy=-10, size=13)
    p.label(2, 1, "X₂ = (2, 1)", dx=12, dy=14, size=13)
    p.label(4, 3, "X₃ = (4, 3)", dx=-86, dy=-8, size=13)
    p.label(0.2, 3.55, "x₁ + x₂ = 3", size=12, color=REMARK)
    p.label(4.75, 3.45, "x₁ − x₂ = 1", size=12, color=REMARK)
    p.label(0.3, 4.3, "x₁ + 2x₂ = 10", size=12, color=REMARK)
    p.label(3.75, 1.45, "z = 11", size=12, color=BASE)
    save("max", figure(
        580, int(H + 70), [p],
        "Maksimum örneğinde uygun çözümler kümesi x₁ − x₂ = 1 doğrusunun (2, 1) ile (4, 3) "
        "arasındaki parçasıdır (kalın). Büyük M yolu: X₀ = (0, 0) → X₁ = (1, 0) → X₂ = (2, 1) "
        "→ X₃ = (4, 3); içi boş çizilen ilk iki nokta uygun değildir. Kesikli doğru "
        "z = 2x₁ + x₂ = 11 seviye doğrusudur.",
        aria="Feasible set is the segment from (2,1) to (4,3) on the line x1 - x2 = 1; Big M "
             "path from (0,0) to (1,0) to (2,1) to (4,3); dashed level line z = 11"))


# ============================================================
# uygunsuz: an infeasible maximum problem
# ============================================================
def fig_uygunsuz():
    xr, yr = (-0.5, 6.8), (-0.5, 4.8)
    p, H = panel(xr, yr, W=480)
    p.grid(xs=range(1, 7), ys=range(1, 5))
    p.polygon([(0, 0), (2, 0), (0, 2)], fill=THEORY, opacity=0.2, stroke=THEORY, width=1.2)
    p.polygon([(6, 0), (6.8, 0), (6.8, 4.8), (0, 4.8), (0, 4)], fill=REMARK, opacity=0.14,
              stroke="none")
    constraint(p, 1, 1, 2, xr, yr, color=THEORY)
    constraint(p, 2, 3, 12, xr, yr)
    axes(p, range(1, 7), range(1, 5))
    path(p, [(0, 0), (0, 2)])
    p.line([(0, 2), (0, 4)], color=BASE, width=2.4, dash="5 4", opacity=0.95)
    p.hollow_points([(0, 0), (0, 2)], color=PRACTICE, r=5)
    p.label(0, 0, "X₀", dx=8, dy=-8, size=13)
    p.label(0, 2, "X₁", dx=10, dy=-6, size=13)
    p.label(0, 3, "eksik: 6", dx=10, dy=4, size=12, color=BASE)
    p.label(0.25, 0.55, "x₁ + x₂ ≤ 2", size=12, color=THEORY)
    p.label(3.4, 3.5, "2x₁ + 3x₂ ≥ 12", size=12, color=REMARK)
    save("uygunsuz", figure(
        580, int(H + 70), [p],
        "Kısıtların ikisini birden sağlayan nokta yoktur: x₁ + x₂ ≤ 2 üçgeni ile "
        "2x₁ + 3x₂ ≥ 12 yarı düzlemi (ikisi de boyalı) kesişmez. Yöntem X₀ = (0, 0) noktasından "
        "üçgenin X₁ = (0, 2) köşesine gider ve durur; orada 2x₁ + 3x₂ = 6'dır ve eksik kalan "
        "12 − 6 = 6 birimi (kesikli parça) yapay değişken taşır.",
        aria="Triangle x1 + x2 at most 2 and half plane 2x1 + 3x2 at least 12 do not meet; "
             "Big M path from (0,0) to (0,2) with a dashed gap of 6 units up to the line"))


# ============================================================
# sifir: a redundant constraint, the artificial stays in the basis at 0
# ============================================================
def fig_sifir():
    xr, yr = (-0.5, 2.9), (-0.5, 2.7)
    p, H = panel(xr, yr, W=460)
    p.grid(xs=range(1, 4), ys=range(1, 3))
    constraint(p, 1, 1, 2, xr, yr)
    level(p, 1, 2, 2, xr, yr)
    p.line([(0, 2), (2, 0)], color=THEORY, width=6, opacity=0.55)
    axes(p, range(1, 3), range(1, 3))
    path(p, [(0, 0), (2, 0)])
    p.hollow_points([(0, 0)], color=PRACTICE, r=5)
    p.points([(2, 0)], color=PRACTICE, r=4.5)
    p.label(0, 0, "X₀", dx=-22, dy=-8, size=13)
    p.label(2, 0, "X₁ = (2, 0)", dx=8, dy=-12, size=13)
    p.label(1.1, 1.08, "x₁ + x₂ = 2", size=12, color=REMARK)
    p.label(1.1, 1.3, "2x₁ + 2x₂ = 4", size=12, color=REMARK)
    p.label(0.12, 1.07, "z = 2", size=12, color=BASE)
    save("sifir", figure(
        560, int(H + 70), [p],
        "İki kısıt aynı doğruyu verir; uygun çözümler kümesi (0, 2) ile (2, 0) arasındaki "
        "kalın parçadır. Yöntem uygun olmayan X₀ = (0, 0) noktasından tek adımda optimal "
        "X₁ = (2, 0) köşesine gider. Kesikli doğru z = x₁ + 2x₂ = 2 seviye doğrusudur.",
        aria="Both constraints give the line x1 + x2 = 2; the feasible set is the segment from "
             "(0,2) to (2,0); Big M path from (0,0) to (2,0); dashed level line z = 2"))


if __name__ == "__main__":
    fig_ornek()
    fig_iki_yapay()
    fig_max()
    fig_uygunsuz()
    fig_sifir()
