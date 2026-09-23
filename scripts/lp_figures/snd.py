# -*- coding: utf-8 -*-
"""
Figures of the chapter "Sınırlı Değişkenler"
(dersler/lineer-programlama/sinirli-degiskenler.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box: a figure that illustrates a
definition sits directly below that box. The figures are NOT produced at
build time. Run

    python scripts/lp_figures/snd.py
    python scripts/center_figures.py "lp-snd-*.md" --keep-width
    python scripts/check_figure_labels.py "scripts/_figures/lp-snd-*.md"

and paste the markup of scripts/_figures/lp-snd-<name>.md into the .qmd.
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
PREFIX = "lp-snd-"

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


class Panel:
    """Panel with x scale W/(x span) and y scale stretched by `stretch`."""

    def __init__(self, xr, yr, W=500, stretch=1.0):
        self.xr, self.yr = xr, yr
        self.kx = W / (xr[1] - xr[0])
        self.ky = self.kx * stretch
        self.H = self.ky * (yr[1] - yr[0])
        self.p = Plot(60, 30, W, self.H, xr, yr)

    def constraint(self, a, b, c, color=REMARK, width=1.6, opacity=0.8, dash=None):
        seg = clip_line(a, b, c, self.xr, self.yr)
        if len(seg) == 2:
            self.p.line(seg, color=color, width=width, opacity=opacity, dash=dash)

    def level(self, a, b, c):
        seg = clip_line(a, b, c, self.xr, self.yr)
        if len(seg) == 2:
            self.p.line(seg, color=BASE, width=1.4, dash="6 4", opacity=0.9)

    def gradient(self, start, a, b, length_px, text, dx=6, dy=0, anchor="start"):
        """Arrow perpendicular (on screen) to the level lines a*x + b*y = const."""
        ux, uy = a / self.kx ** 2, b / self.ky ** 2
        # length of (ux, uy) on screen
        n = math.hypot(ux * self.kx, uy * self.ky)
        end = (start[0] + ux / n * length_px, start[1] + uy / n * length_px)
        self.p.arrow(start, end, color=BASE, width=2.0, head=10)
        self.p.label(end[0], end[1], text, dx=dx, dy=dy, size=12, color=BASE, anchor=anchor)

    def bound(self, x, text, dx=6, dy=0, anchor="start", ytext=None):
        """Vertical bound line x = const, drawn across the whole panel."""
        self.p.line([(x, self.yr[0]), (x, self.yr[1])], color=PRACTICE, width=2.0, opacity=0.95)
        yt = self.yr[1] if ytext is None else ytext
        self.p.label(x, yt, text, dx=dx, dy=dy, size=12, color=PRACTICE, anchor=anchor)


# ============================================================
# ornek1: x1 <= 8 (no sign condition), max z = x1 + x2,
#         -x1 + 2x2 <= 8, x1 + 2x2 <= 10, x2 >= 0
# ============================================================
def fig_ornek1():
    xr, yr = (-9.5, 11.5), (-1.2, 6.4)
    P = Panel(xr, yr, W=500, stretch=1.45)
    p = P.p
    p.grid(xs=[x for x in range(-8, 12, 2) if x != 0], ys=range(1, 7))
    feas = [(-8, 0), (8, 0), (8, 1), (1, 4.5)]
    cut = [(8, 0), (10, 0), (8, 1)]
    p.polygon(feas, fill=THEORY, opacity=0.18, stroke=THEORY, width=1.2)
    p.polygon(cut, fill=REMARK, opacity=0.10, stroke=REMARK, width=1.0, dash="3 3")
    P.constraint(-1, 2, 8)
    P.constraint(1, 2, 10)
    P.level(1, 1, 9)
    P.level(1, 1, 4)
    p.origin_axes(xlabel="x₁", ylabel="x₂",
                  xticks=[x for x in range(-8, 12, 2) if x != 0], yticks=range(1, 7))
    P.bound(8, "x₁ = 8", dx=6, dy=16)
    # x1' = 8 - x1 grows to the left of the bound line
    p.arrow((8, 4.3), (6.3, 4.3), color=PRACTICE, width=1.8, head=9)
    p.label(8, 4.3, "x₁′ = 8 − x₁", dx=8, dy=4, size=12, color=PRACTICE)
    P.gradient((-5.0, 3.3), 1, 1, 40, "z artar", dx=6, dy=0)
    p.points([(8, 1)], color=PRACTICE, r=5)
    p.label(8, 1, "(8, 1)", dx=8, dy=-6, size=13)
    p.label(-4.3, 2.6, "(1)", size=12, color=REMARK)
    p.label(3.5, 4.0, "(2)", size=12, color=REMARK)
    p.label(10.3, 0.35, "z = 9", size=12, color=BASE)
    p.label(-1.4, 4.7, "z = 4", size=12, color=BASE, anchor="end")
    save("ornek1", figure(
        580, int(P.H + 70), [p],
        "Uygun bölge (−8, 0), (8, 0), (8, 1), (1, 4,5) köşeli dörtgendir. x₁ ≤ 8 sınırı, "
        "(1) −x₁ + 2x₂ = 8, (2) x₁ + 2x₂ = 10 doğrularının x₂ = 0 ile oluşturduğu üçgenden "
        "sağdaki küçük üçgeni (kesikli) atar. Yeni değişken x₁′ = 8 − x₁, x₁ = 8 doğrusunda sıfırdır "
        "ve sola doğru artar. Kesikli doğrular z = x₁ + x₂ = 4 ve z = 9 seviye doğrularıdır; "
        "maksimum (8, 1) köşesinde, sınırın üstünde alınır.",
        aria="Feasible quadrilateral (-8,0), (8,0), (8,1), (1,4.5); the bound x1 = 8 cuts off the small "
             "triangle (8,0), (10,0), (8,1); x1 prime grows to the left of x1 = 8; dashed level lines "
             "z = 4 and z = 9; maximum at (8,1)"))


# ============================================================
# ornek2: 0 <= x1 <= 9, max z = -x1 + 2x2,
#         -3x1 + 4x2 <= 24, x1 + 2x2 <= 16, x2 >= 0
# ============================================================
def fig_ornek2():
    xr, yr = (-1.5, 17.5), (-1.2, 9.6)
    P = Panel(xr, yr, W=500, stretch=1.0)
    p = P.p
    p.grid(xs=range(2, 18, 2), ys=range(2, 10, 2))
    feas = [(0, 0), (9, 0), (9, 3.5), (1.6, 7.2), (0, 6)]
    cut = [(9, 0), (16, 0), (9, 3.5)]
    p.polygon(feas, fill=THEORY, opacity=0.18, stroke=THEORY, width=1.2)
    p.polygon(cut, fill=REMARK, opacity=0.10, stroke=REMARK, width=1.0, dash="3 3")
    P.constraint(-3, 4, 24)
    P.constraint(1, 2, 16)
    P.level(-1, 2, 12.8)
    P.level(-1, 2, 6)
    p.origin_axes(xlabel="x₁", ylabel="x₂",
                  xticks=range(2, 18, 2), yticks=range(2, 10, 2))
    P.bound(9, "x₁ = 9", dx=6, dy=16)
    P.gradient((6.5, 6.7), -1, 2, 42, "z artar", dx=6, dy=0)
    p.points([(1.6, 7.2)], color=PRACTICE, r=5)
    p.label(1.6, 7.2, "(8/5, 36/5)", dx=-8, dy=-34, size=13, anchor="middle")
    p.label(-1.4, 4.45, "(1)", size=12, color=REMARK)
    p.label(14.0, 1.9, "(2)", size=12, color=REMARK)
    p.label(12.3, 8.2, "z = 64/5", size=12, color=BASE)
    p.label(13.0, 4.7, "z = 6", size=12, color=BASE)
    save("ornek2", figure(
        580, int(P.H + 70), [p],
        "Uygun bölge (0, 0), (9, 0), (9, 7/2), (8/5, 36/5), (0, 6) köşeli beşgendir. "
        "x₁ ≤ 9 sınırı, sınır olmasaydı bölgeye katılacak (9, 0), (16, 0), (9, 7/2) üçgenini "
        "(kesikli) atar. Kesikli doğrular z = −x₁ + 2x₂ = 6 ve z = 64/5 seviye doğrularıdır; "
        "maksimum (8/5, 36/5) köşesinde alınır ve orada sınır etkin değildir. "
        "(1) −3x₁ + 4x₂ = 24, (2) x₁ + 2x₂ = 16.",
        aria="Feasible pentagon (0,0), (9,0), (9,3.5), (1.6,7.2), (0,6); the bound x1 = 9 cuts off the "
             "triangle (9,0), (16,0), (9,3.5); dashed level lines z = 6 and z = 12.8; maximum at (1.6,7.2)"))


# ============================================================
# ornek3: -4 <= x1 <= 10, max z = -x1 + 3x2,
#         -x1 + 2x2 <= 8, x1 + 2x2 <= 12, x2 >= 0
# ============================================================
def fig_ornek3():
    xr, yr = (-9.5, 13.5), (-1.3, 7.2)
    P = Panel(xr, yr, W=500, stretch=1.45)
    p = P.p
    p.grid(xs=[x for x in range(-8, 14, 2) if x != 0], ys=range(1, 8))
    feas = [(-4, 0), (10, 0), (10, 1), (2, 5), (-4, 2)]
    cut_l = [(-8, 0), (-4, 0), (-4, 2)]
    cut_r = [(10, 0), (12, 0), (10, 1)]
    p.polygon(feas, fill=THEORY, opacity=0.18, stroke=THEORY, width=1.2)
    for cut in (cut_l, cut_r):
        p.polygon(cut, fill=REMARK, opacity=0.10, stroke=REMARK, width=1.0, dash="3 3")
    P.constraint(-1, 2, 8)
    P.constraint(1, 2, 12)
    P.level(-1, 3, 13)
    P.level(-1, 3, 4)
    p.origin_axes(xlabel="x₁", ylabel="x₂",
                  xticks=[x for x in range(-8, 14, 2) if x != 0], yticks=range(1, 8))
    P.bound(-4, "x₁ = −4", dx=6, dy=16)
    P.bound(10, "x₁ = 10", dx=6, dy=16)
    # the new variable x1' = x1 + 4 is measured from the line x1 = -4
    p.arrow((-4, 5.6), (-2.4, 5.6), color=PRACTICE, width=1.8, head=9)
    p.label(-4, 5.6, "x₁′ = x₁ + 4", dx=-8, dy=4, size=12, color=PRACTICE, anchor="end")
    P.gradient((6.4, 4.3), -1, 3, 40, "z artar", dx=6, dy=4)
    p.points([(2, 5)], color=PRACTICE, r=5)
    p.label(2, 5, "(2, 5)", dx=0, dy=-26, size=13, anchor="middle")
    p.label(-7.6, 1.4, "(1)", size=12, color=REMARK)
    p.label(11.2, 1.3, "(2)", size=12, color=REMARK)
    p.label(-9.2, 2.0, "z = 13", size=12, color=BASE)
    p.label(11.0, 5.6, "z = 4", size=12, color=BASE)
    save("ornek3", figure(
        580, int(P.H + 70), [p],
        "Uygun bölge (−4, 0), (10, 0), (10, 1), (2, 5), (−4, 2) köşeli beşgendir. −4 ≤ x₁ ≤ 10 "
        "sınırları, (1) −x₁ + 2x₂ = 8 ve (2) x₁ + 2x₂ = 12 doğrularıyla x₂ = 0'ın oluşturduğu "
        "üçgenin iki ucundan birer küçük üçgen (kesikli) atar. Yeni değişken x₁′ = x₁ + 4, "
        "x₁ = −4 doğrusundan başlayarak ölçülür. Kesikli doğrular z = −x₁ + 3x₂ = 4 ve z = 13 seviye "
        "doğrularıdır; maksimum (2, 5) köşesinde alınır.",
        aria="Feasible pentagon (-4,0), (10,0), (10,1), (2,5), (-4,2) between the bound lines x1 = -4 and "
             "x1 = 10; two small triangles are cut off; x1 prime is measured from x1 = -4; dashed level "
             "lines z = 4 and z = 13; maximum at (2,5)"))


# ============================================================
# ornek4: x1 >= -8, max z = -x1 + 3x2,
#         -2x1 + 3x2 <= 24, x1 + 2x2 <= 8, x2 >= 0
# ============================================================
def fig_ornek4():
    xr, yr = (-13.5, 9.8), (-1.3, 8.2)
    P = Panel(xr, yr, W=500, stretch=1.3)
    p = P.p
    p.grid(xs=[x for x in range(-12, 10, 2) if x != 0], ys=range(1, 9))
    xo, yo = -24 / 7, 40 / 7
    feas = [(-8, 0), (8, 0), (xo, yo), (-8, 8 / 3)]
    cut = [(-12, 0), (-8, 0), (-8, 8 / 3)]
    p.polygon(feas, fill=THEORY, opacity=0.18, stroke=THEORY, width=1.2)
    p.polygon(cut, fill=REMARK, opacity=0.10, stroke=REMARK, width=1.0, dash="3 3")
    P.constraint(-2, 3, 24)
    P.constraint(1, 2, 8)
    P.level(-1, 3, 144 / 7)
    P.level(-1, 3, 8)
    p.origin_axes(xlabel="x₁", ylabel="x₂",
                  xticks=[x for x in range(-12, 10, 2) if x != 0], yticks=range(1, 9))
    P.bound(-8, "x₁ = −8", dx=6, dy=4, ytext=6.0)
    p.arrow((-8, 7.3), (-6.9, 7.3), color=PRACTICE, width=1.8, head=9)
    p.label(-8, 7.3, "x₁′ = x₁ + 8", dx=-8, dy=4, size=12, color=PRACTICE, anchor="end")
    P.gradient((3.0, 4.7), -1, 3, 40, "z artar", dx=6, dy=4)
    p.points([(xo, yo)], color=PRACTICE, r=5)
    p.label(xo, yo, f"({MINUS}24/7, 40/7)", dx=-10, dy=40, size=13, anchor="middle")
    p.label(-12.9, 1.6, "(1)", size=12, color=REMARK)
    p.label(6.0, 1.7, "(2)", size=12, color=REMARK)
    p.label(4.2, 7.9, "z = 144/7", size=12, color=BASE)
    p.label(8.0, 6.3, "z = 8", size=12, color=BASE)
    save("ornek4", figure(
        580, int(P.H + 70), [p],
        "Uygun bölge (−8, 0), (8, 0), (−24/7, 40/7), (−8, 8/3) köşeli dörtgendir. x₁ ≥ −8 sınırı, "
        "sınır olmasaydı bölgeye katılacak (−12, 0), (−8, 0), (−8, 8/3) üçgenini (kesikli) atar. "
        "Yeni değişken x₁′ = x₁ + 8, x₁ = −8 doğrusundan başlayarak ölçülür. Kesikli doğrular "
        "z = −x₁ + 3x₂ = 8 ve z = 144/7 seviye doğrularıdır; maksimum (−24/7, 40/7) köşesinde alınır. "
        "(1) −2x₁ + 3x₂ = 24, (2) x₁ + 2x₂ = 8.",
        aria="Feasible quadrilateral (-8,0), (8,0), (-24/7,40/7), (-8,8/3); the bound x1 = -8 cuts off the "
             "triangle (-12,0), (-8,0), (-8,8/3); x1 prime is measured from x1 = -8; dashed level lines "
             "z = 8 and z = 144/7; maximum at (-24/7,40/7)"))


# ============================================================
# ek: x1 >= 5, 0 <= x2 <= 4, min z = x1 + 2x2,
#     x1 - x2 <= 3, x1 + x2 <= 10
# ============================================================
def fig_ek():
    xr, yr = (-0.8, 11.2), (-0.9, 6.3)
    P = Panel(xr, yr, W=500, stretch=1.0)
    p = P.p
    p.grid(xs=range(1, 12), ys=range(1, 7))
    feas = [(5, 2), (5, 4), (6, 4), (6.5, 3.5)]
    p.polygon(feas, fill=THEORY, opacity=0.22, stroke=THEORY, width=1.2)
    P.constraint(1, -1, 3)
    P.constraint(1, 1, 10)
    P.level(1, 2, 9)
    P.level(1, 2, 13)
    p.origin_axes(xlabel="x₁", ylabel="x₂",
                  xticks=range(1, 11), yticks=range(1, 7))
    P.bound(5, "x₁ = 5", dx=6, dy=16)
    p.line([(xr[0], 4), (xr[1], 4)], color=PRACTICE, width=2.0, opacity=0.95)
    p.label(8.9, 4, "x₂ = 4", dx=0, dy=-7, size=12, color=PRACTICE)
    P.gradient((2.5, 2.2), -1, -2, 40, "z azalır", dx=-6, dy=4, anchor="end")
    # Big M path: (5,0) is the start (x1' = x2 = 0), outside the region
    p.hollow_points([(5, 0)], color=PRACTICE, r=5)
    p.arrow((5, 0), (5, 1.8), color=PRACTICE, width=2.4, head=10)
    p.points([(5, 2)], color=PRACTICE, r=5)
    p.label(5, 0, "(5, 0)", dx=-10, dy=-6, size=13, anchor="end")
    p.label(5, 2, "(5, 2)", dx=-8, dy=4, size=13, anchor="end")
    p.label(9.2, 5.4, "(1)", size=12, color=REMARK)
    p.label(9.3, 1.4, "(2)", size=12, color=REMARK)
    p.label(0.2, 5.1, "z = 13", size=12, color=BASE)
    p.label(0.2, 3.3, "z = 9", size=12, color=BASE)
    save("ek", figure(
        580, int(P.H + 70), [p],
        "Uygun bölge (5, 2), (5, 4), (6, 4), (13/2, 7/2) köşeli küçük dörtgendir; x₁ ≥ 5 ve x₂ ≤ 4 "
        "sınırları onun iki kenarını oluşturur. Başlangıç tablosunun çözümü x₁′ = x₂ = 0, yani "
        "(5, 0) noktasıdır ve bölgenin dışındadır: (1) x₁ − x₂ = 3 kısıtı sağlanmaz, eksik kalan 2 "
        "birimi yapay değişken üstlenir. Tek iterasyon optimal (5, 2) köşesine gider. Kesikli doğrular "
        "z = x₁ + 2x₂ = 9 ve z = 13 seviye doğrularıdır. (2) x₁ + x₂ = 10.",
        aria="Small feasible quadrilateral (5,2), (5,4), (6,4), (6.5,3.5) bounded by x1 = 5 and x2 = 4; "
             "the Big M start (5,0) lies outside and one iteration moves to the optimal corner (5,2); "
             "dashed level lines z = 9 and z = 13"))


if __name__ == "__main__":
    fig_ornek1()
    fig_ornek2()
    fig_ornek3()
    fig_ornek4()
    fig_ek()
