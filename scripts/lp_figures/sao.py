# -*- coding: utf-8 -*-
"""
Figures of the chapter "Sınırsız Çözüm ve Alternatif Optimal Çözüm"
(dersler/lineer-programlama/sinirsiz-ve-alternatif-optimal-cozum.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box: a figure that illustrates a
definition sits directly below that box. The figures are NOT produced at
build time. Run

    python scripts/lp_figures/sao.py
    python scripts/center_figures.py "lp-sao-*.md" --keep-width
    python scripts/check_figure_labels.py "scripts/_figures/lp-sao-*.md"

and paste the markup of scripts/_figures/lp-sao-<name>.md into the .qmd.
Captions are Turkish (they are shown on the site); aria labels are ASCII.
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, TEXT, THEORY, PRACTICE, BASE, REMARK  # noqa: E402
from svg_plot3 import Camera, Space, space_panel  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "lp-sao-"

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


def constraint(p, a, b, c, xr, yr, color=REMARK, width=1.4, opacity=0.75):
    seg = clip_line(a, b, c, xr, yr)
    if len(seg) == 2:
        p.line(seg, color=color, width=width, opacity=opacity)


def level(p, a, b, c, xr, yr):
    seg = clip_line(a, b, c, xr, yr)
    if len(seg) == 2:
        p.line(seg, color=BASE, width=1.4, dash="6 4", opacity=0.9)


def path(p, pts, color=PRACTICE):
    for u, v in zip(pts, pts[1:]):
        p.arrow(u, v, color=color, width=2.6, head=11)


def direction(p, start, vec, length, color=BASE):
    """Arrow of the given data length from start in the direction vec."""
    n = math.hypot(*vec)
    end = (start[0] + vec[0] / n * length, start[1] + vec[1] / n * length)
    p.arrow(start, end, color=color, width=2.0, head=10)
    return end


# ============================================================
# sinirsiz-basit: max z = 2x1 + x2, x1 - x2 <= 2, -2x1 + x2 <= 2
# ============================================================
def fig_sinirsiz_basit():
    xr, yr = (-0.6, 6.4), (-0.6, 6.4)
    p, H = panel(xr, yr)
    p.grid(xs=range(1, 7), ys=range(1, 7))
    region = [(0, 0), (2, 0), (6.4, 4.4), (6.4, 6.4), (2.2, 6.4), (0, 2)]
    p.polygon(region, fill=THEORY, opacity=0.16)
    constraint(p, 1, -1, 2, xr, yr)
    constraint(p, -2, 1, 2, xr, yr)
    level(p, 2, 1, 4, xr, yr)
    level(p, 2, 1, 10, xr, yr)
    axes(p, range(1, 7), range(1, 7))
    path(p, [(0, 0), (2, 0)])
    p.arrow((2, 0), (5.6, 3.6), color=PRACTICE, width=3.0, head=12)
    p.points([(0, 0), (2, 0)], color=PRACTICE, r=4.5)
    p.label(0, 0, "X₀", dx=-8, dy=18, size=13, anchor="end")
    p.label(2, 0, "X₁ = (2, 0)", dx=8, dy=-9, size=13)
    p.label(4.6, 1.95, "x₁ " + MINUS + " x₂ = 2", size=12, color=REMARK)
    p.label(2.35, 6.05, MINUS + "2x₁ + x₂ = 2", size=12, color=REMARK)
    p.label(0.15, 4.65, "z = 4", size=12, color=BASE)
    p.label(5.25, 0.35, "z = 10", size=12, color=BASE)
    p.label(3.1, 1.6, "(2 + λ, λ)", size=13, color=PRACTICE, anchor="end")
    direction(p, (4.3, 4.6), (2, 1), 1.1)
    p.label(4.3, 4.3, "z artar", size=12, color=BASE)
    p.label(0.45, 1.05, "uygun bölge", size=12, color=THEORY)
    save("sinirsiz-basit", figure(
        560, int(H + 70), [p],
        "Uygun bölge sağa ve yukarı doğru sınırsızdır. Simpleks X₀ = (0, 0) köşesinden X₁ = (2, 0) köşesine "
        "geçer; oradan x₁ − x₂ = 2 kenarı boyunca (2 + λ, λ) yönünde sonsuza kadar gidilebilir. "
        "Kesikli doğrular z = 4 ve z = 10 seviye doğrularıdır; bu yönde z = 4 + 3λ sınırsız büyür.",
        aria="Unbounded feasible region between x1 - x2 = 2 and -2x1 + x2 = 2; simplex path from (0,0) to (2,0) "
             "and an arrow along the edge x1 - x2 = 2 to infinity; dashed level lines z = 4 and z = 10"))


# ============================================================
# sinirsiz: -x1 + x2 <= 2, x1 + 4x2 >= 4, min z = -x1 - 2x2
# ============================================================
REGION_P1 = [(0, 1), (0, 2), (3.4, 5.4), (7.4, 5.4), (7.4, 0), (4, 0)]


def region_p1(p, xr, yr):
    p.grid(xs=range(1, 8), ys=range(1, 6))
    p.polygon(REGION_P1, fill=THEORY, opacity=0.16)
    constraint(p, -1, 1, 2, xr, yr)
    constraint(p, 1, 4, 4, xr, yr)


def fig_sinirsiz():
    xr, yr = (-0.6, 7.4), (-0.6, 5.4)
    p, H = panel(xr, yr, W=500)
    region_p1(p, xr, yr)
    level(p, 1, 2, 4, xr, yr)
    level(p, 1, 2, 10, xr, yr)
    axes(p, range(1, 8), range(1, 6))
    path(p, [(0, 1), (0, 2)])
    p.arrow((0, 2), (3.1, 5.1), color=PRACTICE, width=3.0, head=12)
    direction(p, (5.2, 1.0), (1, 2), 1.3)
    p.points([(0, 1), (0, 2), (4, 0)], color=PRACTICE, r=4.5)
    p.label(0, 1, "X₀ = (0, 1)", dx=9, dy=16, size=13)
    p.label(0, 2, "X₁ = (0, 2)", dx=12, dy=5, size=13)
    p.label(4, 0, "(4, 0)", dx=6, dy=-9, size=13)
    p.label(0.95, 4.85, MINUS + "x₁ + x₂ = 2", size=12, color=REMARK)
    p.label(1.2, 0.08, "x₁ + 4x₂ = 4", size=12, color=REMARK)
    p.label(1.15, 1.72, "z = " + MINUS + "4", size=12, color=BASE)
    p.label(6.05, 2.35, "z = " + MINUS + "10", size=12, color=BASE)
    p.label(5.2, 0.62, "z azalır", size=12, color=BASE, anchor="middle")
    p.label(2.05, 3.35, "(λ, 2 + λ)", size=13, color=PRACTICE)
    p.label(4.2, 4.3, "uygun bölge", size=12, color=THEORY)
    save("sinirsiz", figure(
        580, int(H + 70), [p],
        "−x₁ + x₂ ≤ 2, x₁ + 4x₂ ≥ 4 bölgesi sınırsızdır. Faz 2 X₀ = (0, 1) köşesinden X₁ = (0, 2) köşesine geçer; "
        "oradan −x₁ + x₂ = 2 kenarı boyunca (λ, 2 + λ) noktalarına gidildikçe z = −4 − 3λ sınırsız azalır. "
        "Kesikli doğrular z = −4 ve z = −10 seviye doğrularıdır, ok z'nin azaldığı yönü gösterir.",
        aria="Unbounded feasible region of -x1 + x2 at most 2, x1 + 4x2 at least 4 with corners (0,1), (0,2), (4,0); "
             "path from (0,1) to (0,2) then an arrow along -x1 + x2 = 2 to infinity; dashed level lines z = -4 "
             "and z = -10"))


# ============================================================
# sonlu: same region, min z = 2x1 - x2 (finite optimum at (0, 2))
# ============================================================
def fig_sonlu():
    xr, yr = (-0.6, 7.4), (-0.6, 5.4)
    p, H = panel(xr, yr, W=500)
    region_p1(p, xr, yr)
    level(p, 2, -1, -2, xr, yr)
    level(p, 2, -1, 6, xr, yr)
    axes(p, range(1, 8), range(1, 6))
    path(p, [(0, 1), (0, 2)])
    direction(p, (2.6, 1.2), (-2, 1), 1.3)
    p.points([(0, 1), (4, 0)], color=PRACTICE, r=4.5)
    p.points([(0, 2)], color=PRACTICE, r=5.5)
    p.label(0, 1, "X₀ = (0, 1)", dx=9, dy=16, size=13)
    p.label(0, 2, "X₁ = (0, 2)", dx=12, dy=5, size=13)
    p.label(4, 0, "(4, 0)", dx=6, dy=-9, size=13)
    p.label(3.5, 5.0, MINUS + "x₁ + x₂ = 2", size=12, color=REMARK)
    p.label(1.2, 0.08, "x₁ + 4x₂ = 4", size=12, color=REMARK)
    p.label(1.25, 5.0, "z = " + MINUS + "2", size=12, color=BASE, anchor="end")
    p.label(5.9, 4.3, "z = 6", size=12, color=BASE)
    p.label(2.1, 0.85, "z azalır", size=12, color=BASE, anchor="middle")
    p.label(5.0, 1.2, "uygun bölge", size=12, color=THEORY)
    save("sonlu", figure(
        580, int(H + 70), [p],
        "Aynı sınırsız bölgede min z = 2x₁ − x₂. Ok z'nin azaldığı yönü gösterir; bu yönde bölge sınırlıdır. "
        "Kesikli z = −2 doğrusu bölgeye yalnız X₁ = (0, 2) köşesinde değer, bölgenin geri kalanı z > −2 "
        "tarafındadır. Minimum −2'dir.",
        aria="The same unbounded region; dashed level lines 2x1 - x2 = -2 through (0,2) and 2x1 - x2 = 6; "
             "the optimum is the corner (0,2)"))


# ============================================================
# alternatif-basit: max z = x1 + 2x2, x1 + 2x2 <= 8, 3x1 + 2x2 <= 12
# ============================================================
def fig_alternatif_basit():
    xr, yr = (-0.6, 6.4), (-0.6, 6.6)
    p, H = panel(xr, yr)
    p.grid(xs=range(1, 7), ys=range(1, 7))
    region = [(0, 0), (4, 0), (2, 3), (0, 4)]
    p.polygon(region, fill=THEORY, opacity=0.16, stroke=THEORY, width=1.2)
    constraint(p, 1, 2, 8, xr, yr)
    constraint(p, 3, 2, 12, xr, yr)
    level(p, 1, 2, 4, xr, yr)
    axes(p, range(1, 7), range(1, 7))
    p.line([(0, 4), (2, 3)], color=PRACTICE, width=5.0, opacity=0.9)
    path(p, [(0, 0), (0, 4)])
    direction(p, (1.0, 1.4), (1, 2), 1.0)
    p.points([(0, 0), (0, 4), (2, 3)], color=PRACTICE, r=4.5)
    p.label(0, 0, "X₀", dx=-8, dy=18, size=13, anchor="end")
    p.label(0, 4, "X* = (0, 4)", dx=10, dy=-11, size=13)
    p.label(2, 3, "X** = (2, 3)", dx=10, dy=-4, size=13)
    p.label(4.4, 1.5, "x₁ + 2x₂ = 8", size=12, color=REMARK)
    p.label(4.4, 1.5, "(z = 8)", dx=0, dy=16, size=12, color=BASE)
    p.label(4.1, 0.55, "3x₁ + 2x₂ = 12", size=12, color=REMARK)
    p.label(0.2, 2.35, "z = 4", size=12, color=BASE)
    p.label(1.6, 2.1, "z artar", size=12, color=BASE)
    p.label(0.35, 0.7, "uygun bölge", size=12, color=THEORY)
    save("alternatif-basit", figure(
        560, int(H + 70), [p],
        "Amaç doğrusu z = x₁ + 2x₂, x₁ + 2x₂ ≤ 8 kısıtının doğrusuna paraleldir. z artırıldıkça seviye doğrusu "
        "bölgeyi tek bir köşede değil, X* = (0, 4) ile X** = (2, 3) arasındaki kalın kenar boyunca terk eder; "
        "bu kenarın her noktası z = 8 verir.",
        aria="Feasible quadrilateral with corners (0,0), (4,0), (2,3), (0,4); the edge from (0,4) to (2,3) lies on "
             "x1 + 2x2 = 8 and is drawn thick as the set of optimal solutions; dashed level line z = 4"))


# ============================================================
# optimal-isin: max z = x1 - x2, x1 - x2 <= 1, -x1 + x2 <= 2
# ============================================================
def fig_optimal_isin():
    xr, yr = (-0.6, 6.4), (-0.6, 6.4)
    p, H = panel(xr, yr)
    p.grid(xs=range(1, 7), ys=range(1, 7))
    region = [(0, 0), (1, 0), (6.4, 5.4), (6.4, 6.4), (4.4, 6.4), (0, 2)]
    p.polygon(region, fill=THEORY, opacity=0.16)
    constraint(p, 1, -1, 1, xr, yr)
    constraint(p, -1, 1, 2, xr, yr)
    level(p, 1, -1, -1, xr, yr)
    axes(p, range(1, 7), range(1, 7))
    path(p, [(0, 0), (1, 0)])
    p.arrow((1, 0), (5.9, 4.9), color=PRACTICE, width=4.0, head=13)
    direction(p, (4.2, 1.2), (1, -1), 1.0)
    p.points([(0, 0), (1, 0)], color=PRACTICE, r=4.5)
    p.label(0, 0, "X₀", dx=-8, dy=18, size=13, anchor="end")
    p.label(1, 0, "X₁ = (1, 0)", dx=8, dy=-9, size=13)
    p.label(4.1, 2.35, "x₁ " + MINUS + " x₂ = 1  (z = 1)", size=12, color=REMARK)
    p.label(2.55, 5.3, MINUS + "x₁ + x₂ = 2", size=12, color=REMARK, anchor="end")
    p.label(4.5, 5.3, "z = " + MINUS + "1", size=12, color=BASE)
    p.label(5.0, 0.85, "z artar", size=12, color=BASE)
    p.label(3.2, 1.5, "(1 + λ, λ)", size=13, color=PRACTICE)
    p.label(1.9, 2.3, "uygun bölge", size=12, color=THEORY)
    save("optimal-isin", figure(
        560, int(H + 70), [p],
        "İki paralel doğru arasındaki sınırsız şerit. Amaç z = x₁ − x₂ alttaki kenara paraleldir: bu kenar "
        "üzerindeki bütün (1 + λ, λ) noktaları z = 1 verir. Optimal değer sonludur, ama optimal çözümler "
        "X₁ = (1, 0) köşesinden başlayan sınırsız bir ışın oluşturur.",
        aria="Unbounded strip between x1 - x2 = 1 and -x1 + x2 = 2; the optimal solutions form the ray from (1,0) "
             "along x1 - x2 = 1, drawn thick with an arrow; dashed level line z = -1"))


# ============================================================
# alternatif-3b: the source example in R^3, optimal edge X* X**
# ============================================================
def fig_alternatif_3b(az=215.0, el=25.0, name="alternatif-3b"):
    O = (0.0, 0.0, 0.0)
    A = (1.0, 0.0, 0.0)
    B = (0.0, 0.5, 0.0)
    C = (0.0, 0.0, 2 / 3)
    D = (0.0, 1 / 8, 3 / 4)          # X*
    E = (1 / 7, 0.0, 6 / 7)          # X**
    cam = Camera(azimuth=az, elevation=el, scale=1.0)
    # faces with outward normals; a face is visible when its normal points to the viewer
    faces = [
        ([O, B, D, C], (-1, 0, 0)),
        ([O, A, E, C], (0, -1, 0)),
        ([O, A, B], (0, 0, -1)),
        ([A, B, D, E], (1, 2, 1)),
        ([C, D, E], (-4, -2, 3)),
    ]
    vis = [sum(n[i] * cam.d[i] for i in range(3)) > 0 for _, n in faces]
    corners = [O, A, B, C, D, E]
    proj = [cam.project(P)[:2] for P in corners]
    xs = [q[0] for q in proj]
    ys = [q[1] for q in proj]
    pad = 0.30
    xr = (min(xs) - pad, max(xs) + pad)
    yr = (min(ys) - pad, max(ys) + pad)
    p = space_panel(40, 20, 600, xr, yr)
    S = Space(p, cam)

    def edge_visible(u, v):
        return any(vis[k] and u in f and v in f for k, (f, _) in enumerate(faces))

    for k, (f, _) in enumerate(faces):
        if not vis[k]:
            S.polygon(f, fill=THEORY, opacity=0.05)
    for k, (f, _) in enumerate(faces):
        if vis[k]:
            S.polygon(f, fill=REMARK if k == 4 else THEORY, opacity=0.16 if k == 4 else 0.20)
    S.axes(1.3, 0.8, 1.15, labels=("x₁", "x₂", "x₃"), offsets=((12, -2), (-14, -2), (-12, -2)))
    edges = [(O, A), (O, B), (O, C), (A, B), (B, D), (D, C), (A, E), (E, C)]
    for u, v in edges:
        if edge_visible(u, v):
            S.line([u, v], color=THEORY, width=1.8)
        else:
            S.line([u, v], color=THEORY, width=1.2, dash="5 4", opacity=0.7)
    S.line([D, E], color=PRACTICE, width=5.0, opacity=0.9)
    for u, v in ((O, C), (C, D)):
        S.arrow(u, v, color=BASE, width=2.2, head=10, dash=None if edge_visible(u, v) else "5 4")
    for P in (O, A, B, C):
        S.point(P, color=TEXT, r=3.4)
    S.point(D, color=PRACTICE, r=4.8)
    S.point(E, color=PRACTICE, r=4.8)
    S.label(O, "O", dx=-10, dy=14, size=13, anchor="end")
    S.label(A, "A", dx=2, dy=22, size=13, anchor="middle")
    S.label(B, "B", dx=6, dy=16, size=13)
    S.label(C, "C", dx=-12, dy=4, size=13, anchor="end")
    S.label(D, "X*", dx=-12, dy=-4, size=14, anchor="end")
    S.label(E, "X**", dx=12, dy=-6, size=14)
    save(name, figure(
        640, int(p.h + 60), [p],
        "Uygun bölge köşeleri O, A(1, 0, 0), B(0, 1/2, 0), C(0, 0, 2/3), X*(0, 1/8, 3/4) ve X**(1/7, 0, 6/7) olan "
        "bir çokyüzlüdür. Simpleks O → C → X* yolunu izler (oklar). Amaç düzlemi 14x₁ + 4x₂ − 14x₃ = −10 bölgeye "
        "tek bir köşede değil, X*X** kenarı (kalın) boyunca değer: bu kenarın her noktası optimaldir. "
        "Köşelerdeki z değerleri O: 0, A: 14, B: 2, C: −28/3, X* ve X**: −10.",
        aria="Polytope in R3 with vertices O, A(1,0,0), B(0,1/2,0), C(0,0,2/3), X*(0,1/8,3/4), X**(1/7,0,6/7); "
             "hidden edges dashed; the optimal edge from X* to X** drawn thick; simplex path O to C to X*"))


if __name__ == "__main__":
    fig_sinirsiz_basit()
    fig_sinirsiz()
    fig_sonlu()
    fig_alternatif_basit()
    fig_optimal_isin()
    fig_alternatif_3b()
