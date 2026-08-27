# -*- coding: utf-8 -*-
"""
Generates the SVG figures used in the "Analiz" (Analysis) chapters.

The figures are NOT produced at build time: run this script, then
scripts/center_figures.py "analysis-*.md" (which measures each drawing and
centers it in its viewBox), and paste the resulting markup into the .qmd
files — inside the theorem/example/proof box the figure explains, never
inside a definition box. Building the books therefore needs neither Python
nor Jupyter; CI runs Quarto alone.

The captions are Turkish on purpose — they are the text shown on the site.

Usage:   python scripts/analysis_figures.py && python scripts/center_figures.py "analysis-*.md"
Output:  scripts/_figures/analysis-<name>.md
"""
import io
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8")
from svg_plot import *  # noqa: E402,F403 — Plot, figure, colors, WIDE, hollow, dot, sup, ...

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_figures")
os.makedirs(OUT_DIR, exist_ok=True)
OUT = {}


# ---------------------------------------------------------------------------
# Shared helpers for the real line and for sequence plots
# ---------------------------------------------------------------------------
def number_line(p, y=0.0, ticks=(), labels=None, xlabel="", opacity=0.55):
    """A horizontal axis at data height y with tick marks and labels."""
    x0, x1 = p.xmin, p.xmax
    p.arrow((x0, y), (x1, y), TEXT, 1.1, head=7.0, opacity=opacity)
    for i, t in enumerate(ticks):
        X, Y = p.X(t), p.Y(y)
        p.add(f'<line x1="{X:.1f}" y1="{Y-4:.1f}" x2="{X:.1f}" y2="{Y+4:.1f}" stroke="{TEXT}" stroke-width="1" opacity="{opacity}"/>')
        lab = labels[i] if labels else fmt(t)
        p.text_px(X, Y + 16, lab, TEXT, 11, "middle")
    if xlabel:
        p.text_px(p.X(x1) - 2, p.Y(y) - 8, xlabel, TEXT, 11.5, "end", italic=True)


def segment(p, a, b, y=0.0, color=THEORY, width=4.0, opacity=0.5, left_closed=True, right_closed=True, r=4.0):
    """An interval drawn on the real line: thick bar plus filled (closed) or hollow (open) endpoints."""
    p.line([(a, y), (b, y)], color, width, opacity=opacity)
    for x, closed in ((a, left_closed), (b, right_closed)):
        if closed:
            p.points([(x, y)], color, r)
        else:
            hollow(p, (x, y), color, r, 1.6)


def seq_panel(x0, y0, w, h, n_max, yrange):
    """A panel for plotting a sequence a_n against n = 1..n_max."""
    return Plot(x0, y0, w, h, (0, n_max + 0.8), yrange)


def seq_points(p, values, color=PRACTICE, r=3.4, start=1):
    p.points([(start + i, v) for i, v in enumerate(values)], color, r)


def hband(p, lo, hi, color=THEORY, opacity=0.12):
    """Shade the horizontal band lo < y < hi across the whole panel."""
    p.polygon([(p.xmin, lo), (p.xmax, lo), (p.xmax, hi), (p.xmin, hi)], color, opacity)


def vband(p, lo, hi, color=PRACTICE, opacity=0.12):
    """Shade the vertical band lo < x < hi across the whole panel."""
    p.polygon([(lo, p.ymin), (lo, p.ymax), (hi, p.ymax), (hi, p.ymin)], color, opacity)


def curve(p, f, x0, x1, color=THEORY, width=1.9, samples=160, dash=None, opacity=1.0):
    """Polyline of y = f(x) on [x0, x1]."""
    pts = [(x0 + (x1 - x0) * k / samples, f(x0 + (x1 - x0) * k / samples)) for k in range(samples + 1)]
    p.line(pts, color, width, dash, opacity)


EPS, DELTA, ELL, INF, LEQ_S = "&#949;", "&#948;", "&#8467;", "&#8734;", "&#8804;"
SUB_N, SUB_K, SUB_M = '<tspan font-size="9" dy="4">n</tspan><tspan dy="-4">&#8203;</tspan>', \
    '<tspan font-size="9" dy="4">k</tspan><tspan dy="-4">&#8203;</tspan>', \
    '<tspan font-size="9" dy="4">m</tspan><tspan dy="-4">&#8203;</tspan>'


def subs(s, size=9):
    """Subscript inside an SVG <text>: 'a' + subs('n')."""
    return f'<tspan font-size="{size}" dy="4">{s}</tspan><tspan dy="-4">&#8203;</tspan>'

# ############################################################################
# PART F1: chapters 1-14 (logic, sets, relations, functions, order, absolute
# value, induction, supremum, number sets, Archimedes, roots, countability)
# ############################################################################

FORALL, EXISTS, CAP, CUP, SDIFF, IMPLIES = "&#8704;", "&#8707;", "&#8745;", "&#8746;", "&#916;", "&#8658;"
FLOOR_L, FLOOR_R, SQRT, NOTIN, IN_S, ELLIP = "&#8970;", "&#8971;", "&#8730;", "&#8713;", "&#8712;", "&#8230;"
BB_N, BB_Z, BB_Q, BB_R = "&#8469;", "&#8484;", "&#8474;", "&#8477;"


def arrow_px(p, x0, y0, x1, y1, color=THEORY, width=1.6, head=7.0, dash=None, opacity=1.0):
    """Arrow between two pixel positions (same look as Plot.arrow)."""
    dx, dy = x1 - x0, y1 - y0
    length = math.hypot(dx, dy) or 1.0
    ux, uy = dx / length, dy / length
    sx, sy = x1 - ux * head * 0.8, y1 - uy * head * 0.8
    da = f' stroke-dasharray="{dash}"' if dash else ""
    p.add(f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{sx:.1f}" y2="{sy:.1f}" stroke="{color}" stroke-width="{width}"{da} opacity="{opacity}" stroke-linecap="round"/>')
    px, py = -uy, ux
    hw = head * 0.42
    p.add(f'<polygon points="{x1:.1f},{y1:.1f} {x1-ux*head+px*hw:.1f},{y1-uy*head+py*hw:.1f} {x1-ux*head-px*hw:.1f},{y1-uy*head-py*hw:.1f}" fill="{color}" opacity="{opacity}"/>')


def arrow_between(p, a, b, color=THEORY, width=1.6, gap=7.0, head=7.0, dash=None, opacity=1.0):
    """Arrow from data point a to data point b with both ends pulled back `gap` pixels, so the marks stay clear."""
    x0, y0, x1, y1 = p.X(a[0]), p.Y(a[1]), p.X(b[0]), p.Y(b[1])
    length = math.hypot(x1 - x0, y1 - y0) or 1.0
    ux, uy = (x1 - x0) / length, (y1 - y0) / length
    arrow_px(p, x0 + ux * gap, y0 + uy * gap, x1 - ux * gap, y1 - uy * gap, color, width, head, dash, opacity)


def rrect_px(p, x, y, w, h, color, fill_opacity=0.08, width=1.4, rx=8, dash=None, transform=""):
    """Rounded rectangle in pixel coordinates, lightly filled with its own stroke color."""
    da = f' stroke-dasharray="{dash}"' if dash else ""
    tr = f' transform="{transform}"' if transform else ""
    p.add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{color}" fill-opacity="{fill_opacity}" stroke="{color}" stroke-width="{width}"{da}{tr}/>')


def ellipse_px(p, cx, cy, rx, ry, color=TEXT, width=1.1, opacity=0.45):
    p.add(f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="none" stroke="{color}" stroke-width="{width}" opacity="{opacity}"/>')


def hop(p, x0, x1, y, rise, color=THEORY, width=1.5):
    """Arched arrow from (x0, y) to (x1, y) along the number line; `rise` is the arch height in pixels."""
    X0, X1, Y = p.X(x0), p.X(x1), p.Y(y) - 5
    cx, cy = (X0 + X1) / 2, Y - 2 * rise      # quadratic control point: the arch peaks `rise` px above the line
    p.add(f'<path d="M{X0:.1f},{Y:.1f} Q{cx:.1f},{cy:.1f} {X1:.1f},{Y:.1f}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round"/>')
    t = 0.9                                    # a short straight piece near the end carries the arrowhead
    bx = (1 - t) ** 2 * X0 + 2 * (1 - t) * t * cx + t * t * X1
    by = (1 - t) ** 2 * Y + 2 * (1 - t) * t * cy + t * t * Y
    arrow_px(p, bx, by, X1, Y, color, width, 6.5)


# ============================================================ nested-quantifier
X_COL, Y_COL = 2.3, 7.7
ROWS3 = (8.0, 5.0, 2.0)
p1 = Plot(20, 44, 236, 150, (0, 10), (0, 10))
p2 = Plot(304, 44, 236, 150, (0, 10), (0, 10))
for p, title in ((p1, FORALL + "x " + EXISTS + "y  p(x, y)"), (p2, EXISTS + "y " + FORALL + "x  p(x, y)")):
    panel_title(p, title, TEXT, 13)
    for col, name in ((X_COL, "X"), (Y_COL, "Y")):
        ellipse_px(p, p.X(col), p.Y(5), 30, 62)
        p.text_px(p.X(col), p.Y(5) - 62 - 6, name, TEXT, 12, "middle", True, True)
    for i, y in enumerate(ROWS3):
        p.label(X_COL, y, "x" + (SUB1, SUB2, SUB3)[i], -10, 4, TEXT, 11.5, "end", False, True)
        p.label(Y_COL, y, "y" + (SUB1, SUB2, SUB3)[i], 10, 4, TEXT, 11.5, "start", False, True)
# left: every x gets a y of its own
for i, j in ((0, 1), (1, 2), (2, 0)):
    arrow_between(p1, (X_COL, ROWS3[i]), (Y_COL, ROWS3[j]), THEORY, 1.7, 8)
for y in ROWS3:
    dot(p1, (X_COL, y), TEXT, 3.6)
    dot(p1, (Y_COL, y), THEORY, 3.6)
p1.text_px(p1.x0 + p1.w / 2, p1.y0 + p1.h + 24, "her x için ayrı bir y (y, x'e bağlı)", THEORY, 11, "middle", False, True)
# right: one y serves every x
for y in ROWS3:
    arrow_between(p2, (X_COL, y), (Y_COL, ROWS3[1]), PRACTICE, 1.7, 8)
    dot(p2, (X_COL, y), TEXT, 3.6)
dot(p2, (Y_COL, ROWS3[0]), TEXT, 3.0)
dot(p2, (Y_COL, ROWS3[2]), TEXT, 3.0)
dot(p2, (Y_COL, ROWS3[1]), PRACTICE, 4.4)
p2.text_px(p2.x0 + p2.w / 2, p2.y0 + p2.h + 24, "hepsine uyan tek bir y (y, x'ten bağımsız)", PRACTICE, 11, "middle", False, True)
OUT["nested-quantifier"] = figure(
    560, 232, [p1, p2],
    "Solda &#8704;<em>x</em> &#8707;<em>y</em>: her <em>x</em> için ona uygun bir <em>y</em> seçilir ve seçim "
    "<em>x</em>'ten <em>x</em>'e değişebilir. Sağda &#8707;<em>y</em> &#8704;<em>x</em>: önce tek bir <em>y</em> "
    "sabitlenir ve bu <em>y</em> bütün <em>x</em>'ler için işe yarar. İkincisi birinciyi gerektirir; tersi doğru değildir.",
    css_class=WIDE, aria="Ic ice niceleyicilerde siranin onemi: her x icin ayri y ile hepsine uyan tek y")

# ============================================================ venn-islemler
p = Plot(0, 0, 400, 128, (0, 1), (0, 1))   # pixel canvas
VR, VD = 30.0, 17.0                          # circle radius and half distance of the centers


def venn_panel(p, cx, cy, mode, label):
    """Two overlapping circles A (left) and B (right); `mode` chooses the shaded region."""
    ax, bx = cx - VD, cx + VD
    hh = math.sqrt(VR * VR - VD * VD)
    lens = (f'M{cx:.1f},{cy-hh:.1f} A{VR},{VR} 0 0 1 {cx:.1f},{cy+hh:.1f} '
            f'A{VR},{VR} 0 0 1 {cx:.1f},{cy-hh:.1f} Z')
    disk = lambda x: f'M{x+VR:.1f},{cy:.1f} A{VR},{VR} 0 1 1 {x-VR:.1f},{cy:.1f} A{VR},{VR} 0 1 1 {x+VR:.1f},{cy:.1f} Z'
    fill = f'fill="{THEORY}" fill-opacity="0.3" stroke="none"'
    if mode == "cap":
        p.add(f'<path d="{lens}" {fill}/>')
    elif mode == "cup":
        p.add(f'<path d="{disk(ax)} {disk(bx)}" fill-rule="nonzero" {fill}/>')
    elif mode == "minus":
        p.add(f'<path d="{disk(ax)}" {fill}/>')
        p.add(f'<path d="{lens}" fill="{BG}" stroke="none"/>')
    elif mode == "delta":
        p.add(f'<path d="{disk(ax)} {disk(bx)}" fill-rule="nonzero" {fill}/>')
        p.add(f'<path d="{lens}" fill="{BG}" stroke="none"/>')
    for x in (ax, bx):
        p.add(f'<circle cx="{x:.1f}" cy="{cy:.1f}" r="{VR}" fill="none" stroke="{TEXT}" stroke-width="1.2" opacity="0.75"/>')
    p.text_px(ax - 9, cy - VR - 5, "A", TEXT, 11.5, "middle", False, True)
    p.text_px(bx + 9, cy - VR - 5, "B", TEXT, 11.5, "middle", False, True)
    p.text_px(cx, cy + VR + 21, label, TEXT, 12.5, "middle", True)


for i, (mode, label) in enumerate((("cap", "A " + CAP + " B"), ("cup", "A " + CUP + " B"),
                                   ("minus", "A \\ B"), ("delta", "A " + SDIFF + " B"))):
    venn_panel(p, 52 + 98 * i, 62, mode, label)
OUT["venn-islemler"] = figure(
    400, 128, [p],
    "İki kümenin Venn şemasında dört işlem: kesişim <em>A</em> &#8745; <em>B</em> (ikisinde de olanlar), "
    "birleşim <em>A</em> &#8746; <em>B</em> (en az birinde olanlar), fark <em>A</em> \\ <em>B</em> "
    "(<em>A</em>'da olup <em>B</em>'de olmayanlar) ve simetrik fark <em>A</em> &#916; <em>B</em> (yalnızca birinde olanlar).",
    aria="Venn semasi: kesisim, birlesim, fark ve simetrik fark")

# ============================================================ denklik-siniflari
p = Plot(20, 92, 360, 20, (-7, 9), (0, 1))
CLASS_COL = (THEORY, BASE, PRACTICE)
number_line(p, 0.5, ticks=())
for k in range(-6, 9):
    col = CLASS_COL[k % 3]
    dot(p, (k, 0.5), col, 4.0)
    p.label(k, 0.5, str(k).replace("-", MINUS), 0, 18, col, 11, "middle")
for i, members in enumerate(("&#8230;, &#8722;6, &#8722;3, 0, 3, 6, &#8230;",
                             "&#8230;, &#8722;5, &#8722;2, 1, 4, 7, &#8230;",
                             "&#8230;, &#8722;4, &#8722;1, 2, 5, 8, &#8230;")):
    bx = 11 + 128 * i
    rrect_px(p, bx, 12, 122, 46, CLASS_COL[i], 0.08, 1.3, 6)
    p.text_px(bx + 61, 30, "[" + str(i) + "]: kalan " + str(i), CLASS_COL[i], 11.5, "middle", True)
    p.text_px(bx + 61, 49, members, CLASS_COL[i], 10, "middle")
p.text_px(p.X(9) - 2, p.Y(0.5) - 9, BB_Z, TEXT, 12, "end", True)
OUT["denklik-siniflari"] = figure(
    400, 134, [p],
    "Mod 3 denkliği &#8484;'yi üç sınıfa böler: 3'e bölündüğünde 0, 1 ve 2 kalanını verenler. Her tam sayı "
    "tam olarak bir sınıfa düşer; sınıflar ayrıktır ve birleşimleri &#8484;'dir.",
    aria="Tam sayilarin mod 3 denklik siniflari: kalan 0, 1 ve 2")

# ============================================================ goruntu-ters-goruntu
sq = lambda x: x * x
p1 = Plot(30, 36, 236, 210, (-3.7, 3.7), (-1.3, 10.6))
p2 = Plot(300, 36, 236, 210, (-3.7, 3.7), (-1.3, 10.6))
for p in (p1, p2):
    p.origin_axes(xlabel="x", ylabel="y", xticks=(-3, -2, -1, 1, 2, 3), yticks=(4, 9))
    curve(p, sq, -3.2, 3.2, THEORY, 1.4, opacity=0.4)
    p.label(3.6, 10.1, "f(x) = x&#178;", 0, 0, THEORY, 11.5, "end", False, True)
# left: image of A = [-2, 3]
panel_title(p1, "Görüntü: f(A)")
vband(p1, -2, 3, BASE, 0.08)
curve(p1, sq, -2, 3, THEORY, 2.6)
p1.line([(3, 9), (0, 9)], PRACTICE, 1.1, "4 3", 0.85)
p1.line([(-2, 4), (-0.55, 4)], PRACTICE, 1.1, "4 3", 0.85)   # stops short of the "4" tick label
p1.points([(3, 9), (-2, 4)], THEORY, 3.4)
segment(p1, -2, 3, 0, BASE, 5, 0.9)
p1.line([(0, 0), (0, 9)], PRACTICE, 5, opacity=0.9)
p1.points([(0, 0), (0, 9)], PRACTICE, 4)
p1.label(0.5, 0, "A = [" + MINUS + "2, 3]", 0, 30, BASE, 11.5, "middle", True)
p1.label(0, 7.4, "f(A) = [0, 9]", 8, 0, PRACTICE, 11.5, "start", True)
# right: preimage of B = [4, 9]
panel_title(p2, "Ters görüntü: f" + sup(MINUS + "1") + "(B)")
hband(p2, 4, 9, PRACTICE, 0.10)
curve(p2, sq, -3, -2, THEORY, 2.6)
curve(p2, sq, 2, 3, THEORY, 2.6)
for x, y in ((-3, 9), (-2, 4), (2, 4), (3, 9)):
    p2.vline(x, 0, y, BASE, "4 3", 0.75)
p2.points([(-3, 9), (-2, 4), (2, 4), (3, 9)], THEORY, 3.4)
p2.line([(0, 4), (0, 9)], PRACTICE, 5, opacity=0.9)
p2.points([(0, 4), (0, 9)], PRACTICE, 4)
segment(p2, -3, -2, 0, BASE, 5, 0.9)
segment(p2, 2, 3, 0, BASE, 5, 0.9)
p2.label(0, 6.5, "B = [4, 9]", 8, 0, PRACTICE, 11.5, "start", True)
p2.label(0, 0, "f" + sup(MINUS + "1") + "(B) = [" + MINUS + "3, " + MINUS + "2] " + CUP + " [2, 3]", 0, 30, BASE, 11.5, "middle", True)
OUT["goruntu-ters-goruntu"] = figure(
    560, 276, [p1, p2],
    "Solda <em>A</em> = [&#8722;2, 3] aralığının görüntüsü: grafiğin <em>A</em> üzerindeki parçası <em>y</em> eksenine "
    "[0, 9] olarak yansır. Sağda <em>B</em> = [4, 9] şeridinin ters görüntüsü: grafiğin şeride düşen iki parçası "
    "<em>x</em> eksenine [&#8722;3, &#8722;2] &#8746; [2, 3] olarak iner.",
    css_class=WIDE, aria="x kare fonksiyonunda bir aralığın goruntusu ve bir aralığın ters goruntusu".replace("ğ", "g").replace("ı", "i"))

# ============================================================ birebir-orten
ROWS4 = (8.6, 6.2, 3.8, 1.4)
SUBS = (SUB1, SUB2, SUB3, "&#8324;")
panels = []
for i, (title, n_left, n_right, pairs, hot, empty) in enumerate((
        ("birebir, örten değil", 3, 4, ((0, 0), (1, 1), (2, 3)), (), (2,)),
        ("örten, birebir değil", 4, 3, ((0, 0), (1, 1), (2, 1), (3, 2)), (1, 2), ()),
        ("birebir-örten", 3, 3, ((0, 1), (1, 2), (2, 0)), (), ()))):
    p = Plot(12 + 184 * i, 44, 168, 150, (0, 10), (0, 10))
    panel_title(p, title, TEXT, 12)
    left = ROWS3 if n_left == 3 else ROWS4
    right = ROWS3 if n_right == 3 else ROWS4
    for col, name in ((X_COL, "X"), (Y_COL, "Y")):
        ellipse_px(p, p.X(col), p.Y(5), 27, 62)
        p.text_px(p.X(col), p.Y(5) - 62 - 6, name, TEXT, 12, "middle", True, True)
    for a, b in pairs:
        col = PRACTICE if a in hot else THEORY
        arrow_between(p, (X_COL, left[a]), (Y_COL, right[b]), col, 1.6, 7)
    for k, y in enumerate(left):
        dot(p, (X_COL, y), TEXT, 3.4)
        p.label(X_COL, y, "x" + SUBS[k], -9, 4, TEXT, 11, "end", False, True)
    for k, y in enumerate(right):
        if k in empty:
            hollow(p, (Y_COL, y), PRACTICE, 3.6, 1.5)
        else:
            dot(p, (Y_COL, y), THEORY, 3.4)
        p.label(Y_COL, y, "y" + SUBS[k], 9, 4, TEXT, 11, "start", False, True)
    panels.append(p)
OUT["birebir-orten"] = figure(
    560, 206, panels,
    "Solda farklı <em>x</em>'ler farklı <em>y</em>'lere gider ama <em>y</em><sub>3</sub>'e hiç ok gelmez (birebir, "
    "örten değil). Ortada her <em>y</em>'ye ok gelir ama <em>y</em><sub>2</sub>'ye iki ok gelir (örten, birebir değil). "
    "Sağda her <em>y</em>'ye tam bir ok gelir: birebir-örten.",
    css_class=WIDE, aria="Uc ok semasi: birebir ama orten degil, orten ama birebir degil, birebir-orten")

# ============================================================ aralik-turleri
A_PT, B_PT = 1.5, 3.5
panels = []
for i, (notation, kind, lc, rc, unbounded) in enumerate((
        ("(a, b)", "açık aralık", False, False, False),
        ("[a, b]", "kapalı aralık", True, True, False),
        ("[a, b)", "yarı açık aralık", True, False, False),
        ("(a, +" + INFTY + ")", "sınırsız açık aralık", False, False, True))):
    p = Plot(22, 22 + 44 * i, 210, 20, (-0.4, 5), (0, 1))
    if unbounded:
        number_line(p, 0.5, ticks=(A_PT,), labels=("a",))
        p.arrow((A_PT, 0.5), (4.97, 0.5), THEORY, 4, head=11, opacity=0.55)
        hollow(p, (A_PT, 0.5), THEORY, 4, 1.6)
    else:
        number_line(p, 0.5, ticks=(A_PT, B_PT), labels=("a", "b"))
        segment(p, A_PT, B_PT, 0.5, THEORY, 4, 0.55, lc, rc)
    p.text_px(246, p.Y(0.5) + 4, notation, TEXT, 12.5, "start", True)
    p.text_px(306, p.Y(0.5) + 4, kind, REMARK, 10.5, "start", False, True)
    panels.append(p)
OUT["aralik-turleri"] = figure(
    400, 196, panels,
    "Dolu nokta uç noktanın aralığa ait olduğunu, içi boş nokta ait olmadığını gösterir. Sonsuz tarafta uç nokta "
    "yoktur; aralık o yönde sınırsız sürer.",
    aria="Acik, kapali, yari acik ve sinirsiz aralik ornekleri sayi dogrusunda")

# ============================================================ mutlak-deger
p1 = Plot(24, 30, 236, 180, (-3.4, 3.4), (-0.7, 3.5))
panel_title(p1, "|x|: x'in 0'a uzaklığı")
p1.origin_axes(xlabel="x", ylabel="y", xticks=(-2, -1, 1, 2), yticks=(1, 2, 3))
p1.vline(-2, 0, 2, PRACTICE, "4 3", 0.8)
p1.vline(2, 0, 2, PRACTICE, "4 3", 0.8)
p1.line([(-2, 2), (2, 2)], PRACTICE, 1.0, "4 3", 0.6)
p1.line([(-3.2, 3.2), (0, 0), (3.2, 3.2)], THEORY, 2.2)
p1.points([(-2, 2), (2, 2)], PRACTICE, 3.6)
p1.label(0.35, 3.1, "y = |x|", 0, 0, THEORY, 12, "start", True, True)
p1.label(-2, 2, "|" + MINUS + "2| = 2", -8, -6, PRACTICE, 11, "end")
p1.label(2, 2, "|2| = 2", 8, -6, PRACTICE, 11, "start")

A0, EPS0 = 2.6, 1.0
p2 = Plot(300, 30, 236, 180, (-0.4, 5.4), (0, 1))
panel_title(p2, "|x " + MINUS + " a| &lt; " + EPS + ": x, a'ya " + EPS + "'dan yakın")
p2.polygon([(A0 - EPS0, 0.25), (A0 + EPS0, 0.25), (A0 + EPS0, 0.7), (A0 - EPS0, 0.7)], THEORY, 0.14)
number_line(p2, 0.45, ticks=(A0 - EPS0, A0, A0 + EPS0), labels=("a " + MINUS + " " + EPS, "a", "a + " + EPS))
hollow(p2, (A0 - EPS0, 0.45), THEORY, 4, 1.6)
hollow(p2, (A0 + EPS0, 0.45), THEORY, 4, 1.6)
dot(p2, (A0, 0.45), TEXT, 3.8)
XP = A0 + 0.6
dot(p2, (XP, 0.45), PRACTICE, 3.8)
p2.label(XP, 0.45, "x", 0, -9, PRACTICE, 12, "middle", True, True)
p2.arrow((A0, 0.62), (XP, 0.62), PRACTICE, 1.4, head=6.5)
p2.label((A0 + XP) / 2, 0.62, "|x " + MINUS + " a|", 0, -6, PRACTICE, 10.5, "middle", False, True)
p2.label(A0, 0.15, "(a " + MINUS + " " + EPS + ", a + " + EPS + ")", 0, 0, THEORY, 11.5, "middle", True)
OUT["mutlak-deger"] = figure(
    560, 216, [p1, p2],
    "Solda <em>y</em> = |<em>x</em>| grafiği: &#8722;2 ile 2 aynı değeri alır, çünkü ikisi de 0'a 2 uzaklıktadır. "
    "Sağda |<em>x</em> &#8722; <em>a</em>| &lt; <em>&#949;</em> eşitsizliği: <em>x</em>'in <em>a</em>'ya uzaklığı "
    "<em>&#949;</em>'dan küçüktür, yani <em>x</em> açık (<em>a</em> &#8722; <em>&#949;</em>, <em>a</em> + <em>&#949;</em>) aralığındadır.",
    css_class=WIDE, aria="Mutlak deger grafigi ve |x-a| kucuk epsilon esitsizliginin sayi dogrusundaki anlami")

# ============================================================ mutlak-deger-esitsizlik
p = Plot(24, 40, 356, 90, (-7, 11), (0, 1))
p.text_px(24 + 178, 22, "3 " + LEQ + " |x " + MINUS + " 2| " + LEQ + " 7   " + "&#8660;" + "   x " + IN_S + " [" + MINUS + "5, " + MINUS + "1] " + CUP + " [5, 9]", TEXT, 12, "middle", True)
number_line(p, 0.3, ticks=(-5, -1, 2, 5, 9), labels=(MINUS + "5", MINUS + "1", "2", "5", "9"))
segment(p, -5, -1, 0.3, BASE, 5, 0.6)
segment(p, 5, 9, 0.3, BASE, 5, 0.6)
p.vline(2, 0.3, 0.9, PRACTICE, "3 3", 0.6)
dot(p, (2, 0.3), PRACTICE, 4.4)
for x1, y, lab in ((5, 0.6, "3"), (-1, 0.6, "3"), (9, 0.87, "7"), (-5, 0.87, "7")):
    p.arrow((2, y), (x1, y), PRACTICE, 1.3, head=6.5)
    p.label((2 + x1) / 2, y, lab, 0, -5, PRACTICE, 11, "middle", True)
OUT["mutlak-deger-esitsizlik"] = figure(
    400, 134, [p],
    "2 merkezine uzaklığı en az 3 ve en çok 7 olan noktalar: 2'nin solunda [&#8722;5, &#8722;1], sağında [5, 9]. "
    "Aradaki (&#8722;1, 5) parçası 2'ye 3'ten yakındır, dıştaki noktalar 7'den uzaktır; ikisi de çözüm değildir.",
    aria="3 kucuk esit |x-2| kucuk esit 7 esitsizliginin cozum kumesi sayi dogrusunda")

# ============================================================ tumevarim-domino
p = Plot(0, 0, 400, 172, (0, 1), (0, 1))   # pixel canvas
DW, DH, BASE_Y = 18, 58, 128
DXS = [46, 104, 162, 220, 278]
p.add(f'<line x1="20" y1="{BASE_Y}" x2="380" y2="{BASE_Y}" stroke="{TEXT}" stroke-width="1.1" opacity="0.45"/>')
for i, x in enumerate(DXS):
    if i == 0:
        rrect_px(p, x, BASE_Y - DH, DW, DH, PRACTICE, 0.25, 1.4, 3, transform=f"rotate(30 {x + DW} {BASE_Y})")
    else:
        rrect_px(p, x, BASE_Y - DH, DW, DH, THEORY, 0.22, 1.4, 3)
    p.text_px(x + DW / 2, BASE_Y + 20, "P(" + str(i + 1) + ")", PRACTICE if i == 0 else THEORY, 11.5, "middle", True)
    if i < len(DXS) - 1:
        arrow_px(p, x + DW + 5, BASE_Y - DH - 12, DXS[i + 1] - 5, BASE_Y - DH - 12, THEORY, 1.4, 6.5)
arrow_px(p, DXS[-1] + DW + 5, BASE_Y - DH - 12, 330, BASE_Y - DH - 12, THEORY, 1.4, 6.5)
p.text_px(346, BASE_Y - 24, ELLIP, TEXT, 18, "middle")
p.text_px(22, BASE_Y + 38, "temel adım: P(1) doğru", PRACTICE, 10.5, "start", False, True)
p.text_px(200, 44, "tümevarım adımı: P(k) " + IMPLIES + " P(k + 1)", THEORY, 11.5, "middle", True)
OUT["tumevarim-domino"] = figure(
    400, 172, [p],
    "Tümevarım domino taşları gibidir: temel adım ilk taşı devirir, tümevarım adımı her taşın bir sonrakini "
    "devirdiğini güvence altına alır. İkisi birlikte bütün taşların devrilmesini, yani her <em>n</em> için "
    "<em>P</em>(<em>n</em>)'nin doğru olmasını sağlar.",
    aria="Tumevarim ilkesinin domino benzetmesi: ilk tas devrilir, her tas sonrakini devirir")

# ============================================================ supremum-sayi-dogrusu
p = Plot(30, 30, 350, 110, (-0.12, 1.55), (0, 1))
EPS1 = 0.28
p.polygon([(1 - EPS1, 0.2), (1, 0.2), (1, 0.5), (1 - EPS1, 0.5)], BASE, 0.16)
number_line(p, 0.35, ticks=(0, 0.5, 1 - EPS1, 1), labels=("0", "1/2", "1 " + MINUS + " " + EPS, "1"))
p.points([(1 - 1 / n, 0.35) for n in range(1, 15)], PRACTICE, 3.4)
p.label(0.05, 0.35, "A = {1 " + MINUS + " 1/n : n " + IN_S + " " + BB_N + "}", 0, -14, PRACTICE, 11, "start", True)
p.label(1 - EPS1 / 2, 0.5, "(1 " + MINUS + " " + EPS + ", 1]", 0, -6, BASE, 11, "middle", False, True)
p.vline(1, 0.35, 0.75, THEORY, "3 3", 0.6)
p.arrow((1, 0.75), (1.53, 0.75), THEORY, 5, head=11, opacity=0.5)
dot(p, (1, 0.75), THEORY, 4)
p.label(1.02, 0.75, "üst sınırlar: [1, " + INFTY + ")", 0, -10, THEORY, 11, "start", True)
hollow(p, (1, 0.35), THEORY, 4.4, 1.8)
p.label(1, 0.35, "sup A = 1 " + NOTIN + " A", 0, 31, THEORY, 11.5, "middle", True)
OUT["supremum-sayi-dogrusu"] = figure(
    400, 148, [p],
    "<em>A</em> = {1 &#8722; 1/<em>n</em>} kümesinin elemanları 1'e soldan yığılır; 1 kümeye ait olmayan (içi boş) "
    "en küçük üst sınırdır. 1'in sağındaki her sayı üst sınırdır ve 1'in hemen solundaki her (1 &#8722; <em>&#949;</em>, 1] "
    "penceresi kümeden en az bir eleman içerir.",
    aria="1 - 1/n kumesi sayi dogrusunda: supremum 1, ust sinirlar ve epsilon penceresi")

# ============================================================ ic-ice-araliklar
p = Plot(50, 24, 320, 150, (0, 4), (0, 6))
A_LIM = 2.0
ints = [(A_LIM - 1.5 / n, A_LIM + 1.1 / n) for n in range(1, 6)]
p.vline(A_LIM, 0.5, 5.5, PRACTICE, "4 3", 0.7)
for n, (a, b) in enumerate(ints, start=1):
    y = 6.5 - n
    segment(p, a, b, y, THEORY, 4, 0.5)
    p.label(0, y, "I" + subs(str(n)), -10, 4, THEORY, 11.5, "end", True, True)
    if n <= 2:
        s = subs(str(n))
        p.label(a, y, "a" + s, 0, -9, TEXT, 11, "middle", False, True)
        p.label(b, y, "b" + s, 0, -9, TEXT, 11, "middle", False, True)
p.label(A_LIM, 1.0, "&#8942;", 16, 7, TEXT, 17, "start")
number_line(p, 0.5, ticks=(A_LIM,), labels=("a",))
dot(p, (A_LIM, 0.5), PRACTICE, 4.2)
p.label(2.6, 0.5, CAP + " I" + SUB_N + " = {a}", 0, -9, PRACTICE, 11.5, "start", True)
OUT["ic-ice-araliklar"] = figure(
    400, 190, [p],
    "İç içe kapalı aralıklar <em>I</em><sub>1</sub> &#8835; <em>I</em><sub>2</sub> &#8835; <em>I</em><sub>3</sub> &#8835; &#8943;: "
    "sol uçlar artar, sağ uçlar azalır ve uzunluklar sıfıra gider. Kesişim boş değildir; tek bir <em>a</em> noktasından oluşur.",
    aria="Daralan ic ice kapali araliklar ve ortak nokta a")

# ============================================================ sayi-kumeleri
p = Plot(0, 0, 400, 230, (0, 1), (0, 1))   # pixel canvas
layers = (
    (16, 16, 368, 198, THEORY, BB_R, "reel sayılar", 347, (SQRT + "2", "&#960;", MINUS + SQRT + "3"), 209),
    (34, 44, 276, 152, BASE, BB_Q, "rasyonel sayılar", 270, ("1/2", MINUS + "3/4", "0,75"), 191),
    (52, 72, 178, 106, PRACTICE, BB_Z, "tam sayılar", 190, (MINUS + "1", "0", MINUS + "7"), 173),
    (70, 100, 80, 60, REMARK, BB_N, "doğal sayılar", 110, ("1, 2, 3, " + ELLIP,), 150),
)
for x, y, w, h, col, name, desc, cx, examples, dy in layers:
    rrect_px(p, x, y, w, h, col, 0.07, 1.4, 10)
    p.text_px(x + 12, y + 21, name, col, 15, "start", True)
    p.text_px(cx, dy, desc, col, 10, "middle", False, True)
    n = len(examples)
    top = 132 if n == 1 else (y + h) / 2 - 12 * (n - 1) + 4
    for k, ex in enumerate(examples):
        p.text_px(cx, top + 26 * k, ex, col, 12, "middle")
OUT["sayi-kumeleri"] = figure(
    400, 230, [p],
    "Sayı kümeleri iç içedir: &#8469; &#8834; &#8484; &#8834; &#8474; &#8834; &#8477;. Her katmanda bir öncekinde olmayan "
    "sayılar vardır: 0 ve negatifler &#8484;'ye, kesirler &#8474;'ya, &#8730;2 ve &#960; gibi irrasyoneller &#8477;'ye özgüdür.",
    aria="Ic ice sayi kumeleri: dogal, tam, rasyonel ve reel sayilar")

# ============================================================ arsimet
p = Plot(24, 34, 356, 70, (-0.3, 7.2), (0, 1))
BB, AA = 1.2, 5.3
number_line(p, 0.35, ticks=tuple(k * BB for k in range(6)), labels=("0", "b", "2b", "3b", "4b", "5b"))
for k in range(5):
    hop(p, k * BB, (k + 1) * BB, 0.35, 16, THEORY, 1.4)
p.points([(k * BB, 0.35) for k in range(6)], THEORY, 3.4)
p.vline(AA, 0.35, 0.95, PRACTICE, "3 3", 0.7)
dot(p, (AA, 0.35), PRACTICE, 4.2)
p.label(AA, 0.35, "a", 0, 16, PRACTICE, 11.5, "middle", True, True)
p.label(5 * BB, 0.35, "nb = 5b &gt; a", 6, -28, BASE, 11.5, "start", True)
OUT["arsimet"] = figure(
    400, 106, [p],
    "<em>b</em> &gt; 0 ne kadar küçük olursa olsun <em>b</em>, 2<em>b</em>, 3<em>b</em>, &#8230; adımları sayı doğrusunda "
    "ilerler ve sonunda <em>a</em>'yı geçer; örnekte 5<em>b</em> &gt; <em>a</em>. Arşimet özelliği böyle bir <em>n</em>'nin "
    "her zaman var olduğunu söyler.",
    aria="Arsimet ozelligi: b adimlari sonunda a sayisini gecer")

# ============================================================ taban-fonksiyonu
p = Plot(50, 26, 300, 236, (-2.8, 3.8), (-3.4, 3.7))
p.origin_axes(xlabel="x", ylabel="y", xticks=(-2, -1, 1, 2, 3), yticks=(-3, -2, 1, 2, 3))
# the step [-1, 0) covers the usual place of the "-1" tick label, so that one goes to the right of the axis
p.add(f'<text x="{p.X(0)+10:.1f}" y="{p.Y(-1)+4:.1f}" fill="{TEXT}" font-size="11" opacity="0.7">-1</text>')
for k in range(-3, 4):
    lo, hi = max(k, -2.7), min(k + 1, 3.7)
    p.line([(lo, k), (hi, k)], THEORY, 2.2)
for x, y, lab, dy in ((2.6, 2, FLOOR_L + "2,6" + FLOOR_R + " = 2", -12), (-1.5, -2, FLOOR_L + MINUS + "1,5" + FLOOR_R + " = " + MINUS + "2", 17)):
    p.vline(x, 0, y, PRACTICE, "4 3", 0.8)
    dot(p, (x, y), PRACTICE, 3.6)
    p.label(x, y, lab, 0, dy, PRACTICE, 11, "middle", True)
for k in range(-3, 4):
    if k >= -2:
        dot(p, (k, k), THEORY, 3.6)
    if k + 1 <= 3:
        hollow(p, (k + 1, k), THEORY, 3.6, 1.6)
p.label(-2.6, 3.3, "y = " + FLOOR_L + "x" + FLOOR_R, 0, 0, THEORY, 12.5, "start", True, True)
OUT["taban-fonksiyonu"] = figure(
    400, 282, [p],
    "Taban fonksiyonu <em>y</em> = &#8970;<em>x</em>&#8971; bir merdivendir: her [<em>p</em>, <em>p</em> + 1) aralığında "
    "sabit <em>p</em> değerini alır. Sol uç dolu (değer alınır), sağ uç içi boştur (bir üst basamağa sıçrar): "
    "&#8970;2,6&#8971; = 2 ve &#8970;&#8722;1,5&#8971; = &#8722;2.",
    aria="Taban fonksiyonunun basamak grafigi, sol uclar dolu sag uclar bos")

# ============================================================ kok2-supremum
p = Plot(24, 40, 356, 90, (-0.2, 2.25), (0, 1))
S2 = math.sqrt(2)
number_line(p, 0.3, ticks=(0, 1, 2))
segment(p, 0, S2, 0.3, BASE, 5, 0.6, False, False)
p.label(0.6, 0.3, "A = {y &gt; 0 : y&#178; &lt; 2}", 0, -12, BASE, 11, "middle", True)
hollow(p, (S2, 0.3), THEORY, 4.6, 1.8)
p.label(S2, 0.3, "x = sup A", 0, 16, THEORY, 11.5, "middle", True)
for x, y, lab, sentence, col in ((S2 - 0.22, 0.62, "x " + MINUS + " " + EPS, "Durum 1, x&#178; &gt; 2: x " + MINUS + " " + EPS + " de üst sınır", PRACTICE),
                                (S2 + 0.22, 0.9, "x + " + EPS, "Durum 2, x&#178; &lt; 2: x + " + EPS + " " + IN_S + " A", BASE)):
    p.vline(x, 0.3, y, col, "3 3", 0.7)
    dot(p, (x, y), col, 3.6)
    p.label(x, y, lab, 0, -8, col, 11, "middle", True)
    p.label(x, y, sentence, -10, 4, col, 10.5, "end", False, True)
OUT["kok2-supremum"] = figure(
    400, 134, [p],
    "<em>A</em> = {<em>y</em> &gt; 0 : <em>y</em>&#178; &lt; 2} kümesi ve en küçük üst sınırı <em>x</em>. "
    "<em>x</em>&#178; &gt; 2 olsaydı biraz küçüğü <em>x</em> &#8722; <em>&#949;</em> de üst sınır olurdu (<em>x</em> en küçük olamaz); "
    "<em>x</em>&#178; &lt; 2 olsaydı biraz büyüğü <em>x</em> + <em>&#949;</em> kümeye düşerdi (<em>x</em> üst sınır olamaz). "
    "Geriye <em>x</em>&#178; = 2 kalır.",
    aria="Karesi 2'den kucuk pozitif sayilar kumesinin supremumu ve iki celiski durumu")

# ============================================================ yogunluk
AV, BV, NV = 2.35, 2.65, 4
PV = 10
p1 = Plot(30, 30, 340, 40, (-0.3, 4.3), (0, 1))
number_line(p1, 0.5, ticks=(0, 1, 2, AV, BV, 3, 4), labels=("0", "1", "2", "a", "b", "3", "4"))
segment(p1, AV, BV, 0.5, BASE, 5, 0.55, False, False)
dot(p1, (PV / NV, 0.5), PRACTICE, 4)
p1.label(PV / NV, 0.5, "p/n", 0, -10, PRACTICE, 11.5, "middle", True)
p1.label(0.9, 0.5, "b " + MINUS + " a &lt; 1: arada tam sayı yok", 0, -10, REMARK, 10.5, "middle", False, True)
p2 = Plot(30, 122, 340, 40, (7.7, 12.3), (0, 1))
number_line(p2, 0.5, ticks=(8, 9, NV * AV, 10, NV * BV, 11, 12), labels=("8", "9", "na", "10", "nb", "11", "12"))
segment(p2, NV * AV, NV * BV, 0.5, BASE, 5, 0.55, False, False)
dot(p2, (PV, 0.5), PRACTICE, 4)
p2.label(PV, 0.5, "p", 0, -10, PRACTICE, 11.5, "middle", True, True)
p2.label(8.7, 0.5, "nb " + MINUS + " na &gt; 1: arada tam sayı var", 0, -10, REMARK, 10.5, "middle", False, True)
arrow_px(p1, 200, 82, 200, 106, TEXT, 1.4, 7, opacity=0.7)
p1.text_px(210, 98, "n ile çarp (n = 4)", TEXT, 11, "start", False, True)
OUT["yogunluk"] = figure(
    400, 176, [p1, p2],
    "Üstte <em>a</em> ile <em>b</em> arasında tam sayı olmayabilir. <em>n</em> ile çarpınca aralık 1'den uzun olur "
    "(<em>nb</em> &#8722; <em>na</em> &gt; 1) ve arasına bir <em>p</em> tam sayısı sığar; <em>n</em>'e bölünce "
    "<em>p</em>/<em>n</em> rasyonel sayısı <em>a</em> ile <em>b</em> arasına düşer.",
    aria="Rasyonellerin yogunlugu: aralik n ile buyutulunce arasina tam sayi p sigar")

# ============================================================ sayilabilir-zigzag
p = Plot(60, 30, 260, 260, (0.4, 5.8), (0.4, 5.8))
p.grid(range(1, 6), range(1, 6))
p.axes(range(1, 6), range(1, 6), xlabel="m", ylabel="n")
order = [(m, d - m) for d in range(2, 7) for m in range(1, d)]   # diagonals m + n = d, m increasing
numbered = set(order)
p.points([(m, n) for m in range(1, 6) for n in range(1, 6) if (m, n) not in numbered], REMARK, 2.6)
CR = 9.5   # radius (px) of the numbered discs; the arrows stop just outside them
for k in range(len(order) - 1):
    a, b = order[k], order[k + 1]
    if a[0] + a[1] == b[0] + b[1]:
        arrow_between(p, a, b, THEORY, 1.5, CR + 3)
    else:
        arrow_between(p, a, b, REMARK, 1.2, CR + 3, dash="4 3", opacity=0.8)
arrow_between(p, (5, 1), (1.32, 5.6), REMARK, 1.2, CR + 3, dash="4 3", opacity=0.8)
for k, (m, n) in enumerate(order, start=1):
    p.add(f'<circle cx="{p.X(m):.1f}" cy="{p.Y(n):.1f}" r="{CR}" fill="{BG}" stroke="{THEORY}" stroke-width="1.5"/>')
    p.label(m, n, str(k), 0, 3.5, THEORY, 10, "middle", True)
p.label(5.15, 5.55, "m + n = 6", 0, 0, REMARK, 10.5, "end", False, True)
OUT["sayilabilir-zigzag"] = figure(
    400, 316, [p],
    "&#8469; &#215; &#8469; çiftleri <em>m</em> + <em>n</em> toplamına göre köşegenlere ayrılır; her köşegen yukarıdan "
    "aşağıya (<em>m</em> artan sırada) numaralanır, sonra kesikli okla bir sonraki köşegene geçilir. Böylece her çift "
    "tam bir sıra numarası alır: &#960;(<em>m</em>, <em>n</em>) = <em>T</em>(<em>m</em> + <em>n</em>) + <em>m</em>.",
    aria="N x N izgarasinin kosegenler boyunca zigzag numaralanmasi")

# ############################################################################
# PART F2: chapters 15-26 (neighbourhoods, open and closed sets, accumulation
# points, open covers and Heine-Borel, sequences, convergence, squeeze,
# divergence to infinity, monotone sequences, subsequences, limsup/liminf,
# Cauchy sequences)
# ############################################################################

CAP, CUP, IN_S, NOTIN, ELLIP, BB_N = "&#8745;", "&#8746;", "&#8712;", "&#8713;", "&#8230;", "&#8469;"
SUBSET, NOTSUBSET, EMPTY, RARR, VDOTS, DARR = "&#8834;", "&#8836;", "&#8709;", "&#8594;", "&#8942;", "&#8595;"
NI = "&#8715;"          # "contains as member", U ∋ a


def ifmt(t):
    """Integer tick labels for the n axis."""
    return str(int(round(t)))


def mfmt(v):
    """Tick labels with a proper minus sign."""
    return fmt(v).replace("-", MINUS)


def nbhd(p, lo, hi, y, color=THEORY, half=0.16, opacity=0.14):
    """Shaded box over the interval (lo, hi) of a number line drawn at data height y."""
    p.polygon([(lo, y - half), (hi, y - half), (hi, y + half), (lo, y + half)], color, opacity)


def hline(p, y, color=THEORY, width=1.2, dash="5 4", opacity=0.85):
    """Horizontal reference line across the whole panel (a limit, a bound, a candidate)."""
    p.line([(p.xmin, y), (p.xmax, y)], color, width, dash, opacity)


def step_line(p, values, color=THEORY, width=1.5, opacity=0.9, start=1):
    """Right-continuous step curve: height values[i] on [start+i, start+i+1)."""
    pts = []
    for i, v in enumerate(values):
        pts += [(start + i, v), (start + i + 1, v)]
    p.line(pts, color, width, opacity=opacity)


def seq_axes(p, xticks, yticks):
    p.axes(xticks, yticks, xlabel="n", ylabel="a" + SUB_N, xfmt=ifmt, yfmt=mfmt)


# ============================================================ komsuluk
A_PT, E_PT = 2.5, 1.0
panels = []
for i, (name, kind, closed_ends, center_in) in enumerate((
        ("B(a, " + EPS + ")", "açık komşuluk", False, True),
        ("B*(a, " + EPS + ")", "delinmiş komşuluk", False, False),
        ("B[a, " + EPS + "]", "kapalı komşuluk", True, True))):
    p = Plot(84, 26 + 52 * i, 176, 22, (-0.2, 5.2), (0, 1))
    nbhd(p, A_PT - E_PT, A_PT + E_PT, 0.5, THEORY, 0.4, 0.10)
    number_line(p, 0.5, ticks=(A_PT - E_PT, A_PT, A_PT + E_PT), labels=("a " + MINUS + " " + EPS, "a", "a + " + EPS))
    segment(p, A_PT - E_PT, A_PT + E_PT, 0.5, THEORY, 4, 0.55, closed_ends, closed_ends)
    if center_in:
        dot(p, (A_PT, 0.5), THEORY, 4.0)
    else:
        hollow(p, (A_PT, 0.5), THEORY, 4.0, 1.6)
    p.text_px(70, p.Y(0.5) + 4, name, THEORY, 12.5, "end", True)
    p.text_px(280, p.Y(0.5) + 4, kind, REMARK, 10.5, "start", False, True)
    panels.append(p)
OUT["komsuluk"] = figure(
    400, 166, panels,
    "Aynı merkez ve yarıçapla üç komşuluk: <em>B</em>(<em>a</em>, <em>&#949;</em>) = (<em>a</em> &#8722; <em>&#949;</em>, "
    "<em>a</em> + <em>&#949;</em>) açık aralıktır; delinmiş komşuluk <em>B</em>*(<em>a</em>, <em>&#949;</em>) aynı aralıktan "
    "merkez <em>a</em>'nın çıkarılmışıdır; kapalı komşuluk <em>B</em>[<em>a</em>, <em>&#949;</em>] uç noktaları da içerir. "
    "Dolu nokta kümeye ait, içi boş nokta ait olmayan noktadır.",
    aria="Acik komsuluk, delinmis komsuluk ve kapali komsuluk sayi dogrusunda")

# ============================================================ acik-aralik
A_PT, B_PT, X_PT = 1.0, 4.5, 3.3
E_PT = min(X_PT - A_PT, B_PT - X_PT)
p = Plot(30, 48, 340, 80, (-0.3, 5.6), (0, 1))
nbhd(p, X_PT - E_PT, X_PT + E_PT, 0.3, PRACTICE, 0.15, 0.14)
number_line(p, 0.3, ticks=(A_PT, X_PT - E_PT, X_PT, B_PT), labels=("a", "x " + MINUS + " " + EPS, "x", "b = x + " + EPS))
segment(p, A_PT, B_PT, 0.3, THEORY, 4, 0.55, False, False)
dot(p, (X_PT, 0.3), PRACTICE, 4.2)
p.arrow((X_PT, 0.66), (A_PT, 0.66), REMARK, 1.3, head=6.5)
p.label((X_PT + A_PT) / 2, 0.66, "x " + MINUS + " a", 0, -5, REMARK, 11, "middle", False, True)
p.arrow((X_PT, 0.66), (B_PT, 0.66), PRACTICE, 1.3, head=6.5)
p.label((X_PT + B_PT) / 2, 0.66, "b " + MINUS + " x = " + EPS, 0, -5, PRACTICE, 11, "middle", True)
p.label(X_PT, 0.3, "B(x, " + EPS + ") " + SUBSET + " (a, b)", 0, 34, PRACTICE, 11.5, "middle", True)
p.text_px(200, 22, EPS + " = min{x " + MINUS + " a, b " + MINUS + " x}", TEXT, 12, "middle", True)
OUT["acik-aralik"] = figure(
    400, 160, [p],
    "(<em>a</em>, <em>b</em>) aralığının her <em>x</em> noktası bir iç noktadır: <em>x</em>'in iki uca olan uzaklıklarından "
    "küçüğü <em>&#949;</em> alınırsa <em>B</em>(<em>x</em>, <em>&#949;</em>) komşuluğu aralığın içinde kalır. Örnekte "
    "<em>b</em> &#8722; <em>x</em> daha küçüktür; komşuluk sağ uçta <em>b</em>'ye dayanır ama onu içermez.",
    aria="Acik aralikta bir noktanin icinde kalan komsulugu: epsilon uclara olan uzakliklarin kucugu")

# ============================================================ sonsuz-kesisim
p = Plot(120, 26, 240, 172, (-1.35, 1.35), (0, 6))
p.vline(0, 0.5, 5.8, PRACTICE, "4 3", 0.6)
for n in range(1, 5):
    y = 6.2 - n
    segment(p, -1 / n, 1 / n, y, THEORY, 4, 0.5, False, False)
    lab = "(" + MINUS + "1, 1)" if n == 1 else "(" + MINUS + "1/%d, 1/%d)" % (n, n)
    p.label(-1.35, y, lab, -8, 4, THEORY, 11.5, "end", True)
p.label(0, 1.35, VDOTS, 0, 4, TEXT, 12, "middle")
number_line(p, 0.5, ticks=(-1, 0, 1), labels=(MINUS + "1", "0", "1"))
dot(p, (0, 0.5), PRACTICE, 4.2)
p.label(-1.35, 0.5, "kesişim", -8, 4, PRACTICE, 11.5, "end", True)
p.label(0.12, 0.5, CAP + " (" + MINUS + "1/n, 1/n) = {0}", 0, -12, PRACTICE, 11.5, "start", True)
OUT["sonsuz-kesisim"] = figure(
    400, 216, [p],
    "(&#8722;1/<em>n</em>, 1/<em>n</em>) açık aralıkları 0 etrafında daralır; hepsinin ortak noktası yalnızca 0'dır. "
    "Sonsuz çoklukta açık kümenin kesişimi olan {0} açık değildir: 0'ın hiçbir komşuluğu tek noktalı bir kümeye sığmaz.",
    aria="Daralan (-1/n, 1/n) acik araliklari ve kesisimleri olan {0}")

# ============================================================ sonsuz-birlesim
p = Plot(120, 26, 240, 172, (-1.35, 1.35), (0, 6))
p.vline(-1, 1.6, 5.8, PRACTICE, "4 3", 0.5)
p.vline(1, 1.6, 5.8, PRACTICE, "4 3", 0.5)
for i, n in enumerate((2, 3, 4, 5)):
    y = 5.2 - i
    a = 1 - 1 / n
    segment(p, -a, a, y, THEORY, 4, 0.5, True, True)
    lab = "[" + MINUS + "%d/%d, %d/%d]" % (n - 1, n, n - 1, n)
    p.label(-1.35, y, lab, -8, 4, THEORY, 11.5, "end", True)
p.label(0, 1.35, VDOTS, 0, 4, TEXT, 12, "middle")
number_line(p, 0.5, ticks=(-1, 0, 1), labels=(MINUS + "1", "0", "1"))
segment(p, -1, 1, 0.5, PRACTICE, 4, 0.55, False, False)
p.label(-1.35, 0.5, "birleşim", -8, 4, PRACTICE, 11.5, "end", True)
p.label(0, 0.5, CUP + " [" + MINUS + "1 + 1/n, 1 " + MINUS + " 1/n] = (" + MINUS + "1, 1)", 0, -11, PRACTICE, 11, "middle", True)
OUT["sonsuz-birlesim"] = figure(
    400, 216, [p],
    "[&#8722;1 + 1/<em>n</em>, 1 &#8722; 1/<em>n</em>] kapalı aralıkları büyüyerek (&#8722;1, 1)'i doldurur; uç noktalar "
    "&#8722;1 ve 1 hiçbir aralığa girmez. Sonsuz çoklukta kapalı kümenin birleşimi olan (&#8722;1, 1) kapalı değildir.",
    aria="Buyuyen kapali araliklarin birlesimi olan (-1, 1) acik araligi")

# ============================================================ ne-acik-ne-kapali
E5 = 0.3
p = Plot(30, 36, 340, 84, (-0.8, 2.8), (0, 1))
nbhd(p, -E5, E5, 0.3, PRACTICE, 0.17, 0.16)
nbhd(p, 1 - E5, 1 + E5, 0.3, BASE, 0.17, 0.16)
number_line(p, 0.3, ticks=(0, 1, 2), labels=("0", "1", "2"))
segment(p, 0, 1, 0.3, THEORY, 4, 0.55, True, False)
dot(p, (2, 0.3), THEORY, 4.2)
p.vline(1, 0.5, 0.93, BASE, "3 3", 0.7)
p.text_px(p.X(1), p.Y(0.93) - 5, "B(1, " + EPS + ") " + CAP + " A " + NEQ + " " + EMPTY + " ama 1 " + NOTIN + " A: kapalı değil", BASE, 11, "middle", True)
p.vline(0, 0.5, 0.66, PRACTICE, "3 3", 0.7)
p.text_px(p.X(0), p.Y(0.66) - 5, "B(0, " + EPS + ") " + NOTSUBSET + " A: açık değil", PRACTICE, 11, "middle", True)
p.text_px(p.X(2), p.Y(0.66) - 5, "A = [0, 1) " + CUP + " {2}", THEORY, 11.5, "middle", True)
OUT["ne-acik-ne-kapali"] = figure(
    400, 128, [p],
    "<em>A</em> = [0, 1) &#8746; {2} kümesi açık değildir: 0 kümeye aittir ama her komşuluğu sola, kümenin dışına taşar. "
    "Kapalı da değildir: 1 kümeye ait olmadığı hâlde her komşuluğu [0, 1) parçasından noktalar içerir, yani tümleyen açık değildir.",
    aria="Ne acik ne kapali kume ornegi: [0, 1) birlesim {2}")

# ============================================================ yigilma-1-bolu-n
E6, X6, D6 = 0.13, 1 / 3, 0.05
p = Plot(40, 44, 330, 84, (-0.22, 1.12), (0, 1))
nbhd(p, -E6, E6, 0.3, THEORY, 0.17, 0.16)
nbhd(p, X6 - D6, X6 + D6, 0.3, BASE, 0.17, 0.2)
number_line(p, 0.3, ticks=(0, X6, 0.5, 1), labels=("0", "1/3", "1/2", "1"))
p.points([(1 / n, 0.3) for n in range(1, 41)], PRACTICE, 3.2)
hollow(p, (0, 0.3), THEORY, 4.2, 1.8)
p.vline(0, 0.5, 0.93, THEORY, "3 3", 0.7)
p.text_px(p.X(-E6), p.Y(0.93) - 5, "(" + MINUS + EPS + ", " + EPS + ") içinde sonsuz çoklukta 1/n var", THEORY, 11, "start", True)
p.vline(X6, 0.5, 0.66, BASE, "3 3", 0.7)
p.text_px(p.X(X6 - D6), p.Y(0.66) - 5, "B(1/3, " + DELTA + ") " + CAP + " A = {1/3}: sonlu", BASE, 11, "start", True)
p.label(0, 0.3, "0: yığılma noktası, 0 " + NOTIN + " A", 0, 30, THEORY, 11, "middle", True)
p.label(1, 0.3, "A = {1/n : n " + IN_S + " " + BB_N + "}", 0, 30, PRACTICE, 11, "middle", True)
OUT["yigilma-1-bolu-n"] = figure(
    400, 142, [p],
    "<em>A</em> = {1/<em>n</em>} kümesinin noktaları 0'a yığılır: 0'ın her (&#8722;<em>&#949;</em>, <em>&#949;</em>) komşuluğu, "
    "ne kadar dar olursa olsun, sonsuz çoklukta 1/<em>n</em> içerir; bu yüzden 0 kümeye ait olmasa da yığılma noktasıdır. "
    "1/3 gibi bir noktanın yeterince küçük komşuluğu ise kümeden yalnızca kendisini içerir; kümenin hiçbir noktası yığılma noktası değildir.",
    aria="1/n kumesinin sifirda yigilmasi: sifirin her komsulugunda sonsuz nokta, 1/3 civarinda sonlu nokta")

# ============================================================ izole-nokta
E7 = 0.4
p1 = Plot(50, 34, 320, 40, (-0.5, 3.8), (0, 1))
p2 = Plot(50, 96, 320, 40, (-0.5, 3.8), (0, 1))
nbhd(p1, 3 - E7, 3 + E7, 0.5, PRACTICE, 0.34, 0.16)
number_line(p1, 0.5, ticks=(0, 1, 2, 3), labels=("0", "1", "2", "3"))
segment(p1, 0, 2, 0.5, THEORY, 4, 0.55, False, False)
dot(p1, (3, 0.5), THEORY, 4.2)
p1.text_px(36, p1.Y(0.5) + 4, "A", THEORY, 13, "end", True, True)
p1.text_px(50, 22, "A = (0, 2) " + CUP + " {3}", THEORY, 11.5, "start", True)
p1.text_px(p1.X(3), 22, "B(3, " + EPS + ") " + CAP + " A = {3}: 3 izole nokta", PRACTICE, 11, "middle", True)
number_line(p2, 0.5, ticks=(0, 1, 2, 3), labels=("0", "1", "2", "3"))
segment(p2, 0, 2, 0.5, BASE, 4, 0.55, True, True)
hollow(p2, (3, 0.5), PRACTICE, 4.0, 1.6)
p2.text_px(36, p2.Y(0.5) + 4, "A&#8242;", BASE, 13, "end", True, True)
p2.text_px(p2.X(2.9), p2.Y(0.5) - 10, "yığılma noktaları: A&#8242; = [0, 2]", BASE, 11, "middle", True)
OUT["izole-nokta"] = figure(
    400, 140, [p1, p2],
    "Üstte <em>A</em> = (0, 2) &#8746; {3}: 3 noktasının kümeyle kesişimi yalnızca kendisi olan bir komşuluğu vardır, "
    "yani 3 izole noktadır. Altta yığılma noktaları kümesi <em>A</em>&#8242; = [0, 2]: 0 ve 2 kümeye ait olmadığı hâlde "
    "yığılma noktasıdır, 3 ise kümeye ait olduğu hâlde değildir.",
    aria="Izole nokta ve yigilma noktalari: (0, 2) birlesim {3} kumesi ile turevi [0, 2]")

# ============================================================ acik-ortu
p = Plot(110, 24, 250, 180, (-0.08, 1.12), (0, 7))
p.polygon([(0, 0.5), (1 / 6, 0.5), (1 / 6, 6.9), (0, 6.9)], PRACTICE, 0.13)
for i, n in enumerate((2, 3, 4, 5, 6)):
    y = 6.4 - i
    segment(p, 1 / n, 1, y, THEORY, 4, 0.5, False, False)
    p.label(-0.08, y, "U" + subs(str(n)) + " = (1/" + str(n) + ", 1)", -8, 4, THEORY, 11.5, "end", True)
p.label(0.5, 1.15, VDOTS, 0, 4, TEXT, 12, "middle")
number_line(p, 0.5, ticks=(0, 1 / 6, 0.5, 1), labels=("0", "1/6", "1/2", "1"))
segment(p, 0, 1, 0.5, PRACTICE, 4, 0.55, False, False)
p.label(-0.08, 0.5, "A = (0, 1)", -8, 4, PRACTICE, 11.5, "end", True)
p.label(0, 6.9, "(0, 1/6] örtülmeden kalır", 0, -5, PRACTICE, 10.5, "start", False, True)
OUT["acik-ortu"] = figure(
    400, 214, [p],
    "<em>U<sub>n</sub></em> = (1/<em>n</em>, 1) aralıkları <em>A</em> = (0, 1)'in bir açık örtüsüdür: her "
    "<em>x</em> &#8712; (0, 1) yeterince büyük <em>n</em> için <em>U<sub>n</sub></em>'ye düşer. Ama sonlu tanesi, "
    "örneğin <em>U</em><sub>2</sub>, &#8230;, <em>U</em><sub>6</sub>, yalnızca (1/6, 1)'i örter; 0'a yakın (0, 1/6] parçası "
    "hep açıkta kalır. (0, 1) kompakt değildir.",
    aria="(0, 1) araliginin (1/n, 1) acik ortusu; sonlu alt ortu 0 yakinini kacirir")

# ============================================================ heine-borel-ikiye-bolme
A9, U9 = 0.3, (0.2, 0.42)
levels = ((-1, 1), (0, 1), (0, 0.5), (0.25, 0.5), (0.25, 0.375))
p = Plot(90, 28, 280, 190, (-1.25, 1.25), (0, 6.4))
p.polygon([(U9[0], 0.5), (U9[1], 0.5), (U9[1], 1.75), (U9[0], 1.75)], PRACTICE, 0.12)
p.vline(A9, 0.5, 6.1, PRACTICE, "4 3", 0.7)
for i, (a, b) in enumerate(levels):
    y = 5.9 - 1.15 * i
    segment(p, a, b, y, THEORY, 4, 0.5, True, True, 3.6)
    lab = "I" + subs("1") + " = [" + MINUS + "M, M]" if i == 0 else "I" + subs(str(i + 1))
    p.label(-1.25, y, lab, -8, 4, THEORY, 11.5, "end", True)
p.text_px(90 + 140, 16, "her I" + SUB_N + " sonlu tane U" + subs("i") + " ile örtülemez, uzunluk 2M/2" + sup("n" + MINUS + "1"), THEORY, 11, "middle", False, True)
number_line(p, 0.5, ticks=(-1, 0, 1), labels=(MINUS + "M", "0", "M"))
segment(p, U9[0], U9[1], 0.5, PRACTICE, 4, 0.6, False, False)
dot(p, (A9, 0.5), PRACTICE, 4.2)
p.label(A9, 0.5, "a", 0, 16, PRACTICE, 11.5, "middle", True, True)
p.label(U9[1], 0.5, "U" + subs("i0") + " " + NI + " a", 8, 4, PRACTICE, 11.5, "start", True)
p.label(U9[1], 1.75 - 1.15 + 0.55, "I" + subs("5") + " " + SUBSET + " U" + subs("i0"), 8, 4, PRACTICE, 11, "start", True)
OUT["heine-borel-ikiye-bolme"] = figure(
    400, 226, [p],
    "İkiye bölme: [&#8722;<em>M</em>, <em>M</em>] sonlu tane <em>U<sub>i</sub></em> ile örtülemiyorsa iki yarısından en az "
    "biri de örtülemez; bu yarı seçilip yeniden bölünür. Daralan <em>I<sub>n</sub></em> aralıklarının ortak noktası <em>a</em>, "
    "örtüdeki bir <em>U</em><sub><em>i</em><sub>0</sub></sub> açık aralığına düşer; uzunluğu sıfıra giden <em>I<sub>n</sub></em> "
    "bir yerden sonra bu tek aralığın içine girer, yani tek bir <em>U<sub>i</sub></em> ile örtülür: çelişki.",
    aria="Heine-Borel ispatindaki ikiye bolme: daralan araliklar ve ortak noktayi iceren tek acik aralik")

# ============================================================ dizi-grafik
p1 = seq_panel(44, 40, 210, 150, 12, (-1.25, 1.25))
seq_axes(p1, (1, 5, 10), (-1, 0, 1))
hline(p1, 0, THEORY, 1.2, "5 4", 0.7)
seq_points(p1, [(-1) ** n / n for n in range(1, 13)], PRACTICE, 3.4)
panel_title(p1, "a" + SUB_N + " = (" + MINUS + "1)" + sup("n") + "/n")
p2 = seq_panel(318, 40, 210, 150, 12, (0, 1.25))
seq_axes(p2, (1, 5, 10), (0.5, 1))
hline(p2, 1, THEORY, 1.2, "5 4", 0.7)
seq_points(p2, [n / (n + 1) for n in range(1, 13)], PRACTICE, 3.4)
panel_title(p2, "a" + SUB_N + " = n/(n + 1)")
OUT["dizi-grafik"] = figure(
    560, 216, [p1, p2],
    "Bir dizinin grafiği: yatay eksende indis <em>n</em> = 1, 2, 3, &#8230;, düşeyde terim <em>a<sub>n</sub></em>. Solda "
    "(&#8722;1)<sup><em>n</em></sup>/<em>n</em> işaret değiştirerek 0'a yaklaşır; sağda <em>n</em>/(<em>n</em> + 1) "
    "artarak 1'e yaklaşır ama 1'e hiç ulaşmaz.",
    css_class=WIDE, aria="Iki dizi grafigi: (-1)^n/n sifira, n/(n+1) bire yaklasir")

# ============================================================ yakinsaklik-bant
N11, A11, E11, NE11 = 15, 2.0, 0.3, 6
p = seq_panel(46, 30, 300, 170, N11, (0.85, 2.45))
seq_axes(p, (1, 5, 10, 15), (1, 2))
hband(p, A11 - E11, A11 + E11, THEORY, 0.12)
hline(p, A11, THEORY, 1.2, "5 4", 0.85)
hline(p, A11 + E11, THEORY, 0.9, "3 3", 0.6)
hline(p, A11 - E11, THEORY, 0.9, "3 3", 0.6)
p.vline(NE11, 0.85, 2.45, PRACTICE, "4 3", 0.8)
vals = [2 * n / (n + 1) for n in range(1, N11 + 1)]
p.points([(n, v) for n, v in enumerate(vals, 1) if n < NE11], REMARK, 3.4)
p.points([(n, v) for n, v in enumerate(vals, 1) if n >= NE11], PRACTICE, 3.4)
p.label(N11 + 0.8, A11, "a = 2", 6, 4, THEORY, 11.5, "start", True)
p.label(N11 + 0.8, A11 + E11, "a + " + EPS, 6, 4, THEORY, 11, "start", False, True)
p.label(N11 + 0.8, A11 - E11, "a " + MINUS + " " + EPS, 6, 4, THEORY, 11, "start", False, True)
p.label(NE11, 2.45, "n" + subs(EPS), 0, -4, PRACTICE, 11.5, "middle", True, True)
p.label(2.6, 1.05, "a" + SUB_N + " = 2n/(n + 1)", 0, 0, PRACTICE, 11.5, "start", True)
OUT["yakinsaklik-bant"] = figure(
    400, 220, [p],
    "<em>a<sub>n</sub></em> = 2<em>n</em>/(<em>n</em> + 1) dizisi 2'ye yakınsar. Verilen <em>&#949;</em> için "
    "(2 &#8722; <em>&#949;</em>, 2 + <em>&#949;</em>) bandı taranmıştır: <em>n<sub>&#949;</sub></em>'dan önceki terimler "
    "bandın dışında kalabilir, ama <em>n<sub>&#949;</sub></em>'dan itibaren bütün terimler bandın içindedir. "
    "Daha küçük bir <em>&#949;</em> daha dar bir bant ve genellikle daha büyük bir <em>n<sub>&#949;</sub></em> demektir.",
    aria="Yakinsaklik tanimi: limit etrafindaki epsilon bandi ve n epsilon esigi")

# ============================================================ iraksak-eksi-bir-ussu-n
N12, A12 = 12, 0.6
p = seq_panel(46, 30, 300, 170, N12, (-1.4, 1.4))
seq_axes(p, (1, 5, 10), (-1, 0, 1))
hband(p, A12 - 0.5, A12 + 0.5, THEORY, 0.12)
hline(p, A12, THEORY, 1.2, "5 4", 0.85)
hline(p, A12 + 0.5, THEORY, 0.9, "3 3", 0.6)
hline(p, A12 - 0.5, THEORY, 0.9, "3 3", 0.6)
seq_points(p, [(-1) ** n for n in range(1, N12 + 1)], PRACTICE, 3.4)
p.label(0.4, A12, "a (aday)", 0, -4, THEORY, 11.5, "start", True)
p.label(N12 + 0.8, A12 + 0.5, "a + 1/2", 6, 4, THEORY, 11, "start", False, True)
p.label(N12 + 0.8, A12 - 0.5, "a " + MINUS + " 1/2", 6, 4, THEORY, 11, "start", False, True)
p.label(7, -0.55, "tek n: a" + SUB_N + " = " + MINUS + "1, bandın dışında", 0, 4, PRACTICE, 11, "middle", True)
p.label(7, 1.22, "a" + SUB_N + " = (" + MINUS + "1)" + sup("n"), 0, 4, PRACTICE, 11.5, "middle", True)
OUT["iraksak-eksi-bir-ussu-n"] = figure(
    400, 220, [p],
    "(&#8722;1)<sup><em>n</em></sup> dizisi hiçbir <em>a</em>'ya yakınsamaz: <em>&#949;</em> = 1/2 alınınca "
    "(<em>a</em> &#8722; 1/2, <em>a</em> + 1/2) bandının genişliği 1'dir ve 1 ile &#8722;1'i aynı anda içeremez. "
    "Hangi aday seçilirse seçilsin terimlerin sonsuz çoğu bandın dışında kalır.",
    aria="(-1)^n dizisinin iraksakligi: genisligi 1 olan bant 1 ile -1'i birlikte iceremez")

# ============================================================ sikistirma-dizi
N13 = 20
p = seq_panel(46, 30, 300, 180, N13, (-1.15, 1.15))
seq_axes(p, (1, 5, 10, 15, 20), (-1, 0, 1))
hline(p, 0, THEORY, 1.0, "5 4", 0.6)
curve(p, lambda x: 1 / x, 0.9, N13 + 0.8, THEORY, 1.4, dash="5 4", opacity=0.85)
curve(p, lambda x: -1 / x, 0.9, N13 + 0.8, THEORY, 1.4, dash="5 4", opacity=0.85)
seq_points(p, [math.cos(n) / n for n in range(1, N13 + 1)], PRACTICE, 3.4)
p.label(2.4, 1 / 2.4, "1/n", 7, -3, THEORY, 11.5, "start", True, True)
p.label(2.4, -1 / 2.4, MINUS + "1/n", 7, 12, THEORY, 11.5, "start", True, True)
p.label(N13 + 0.6, 0.95, "a" + SUB_N + " = (cos n)/n", 0, 0, PRACTICE, 11.5, "end", True)
OUT["sikistirma-dizi"] = figure(
    400, 226, [p],
    "(cos <em>n</em>)/<em>n</em> dizisinin terimleri &#8722;1/<em>n</em> ile 1/<em>n</em> arasında kalır. İki zarf da 0'a "
    "gittiğinden aradaki dizi 0'a sıkışır; terimlerin işaretinin düzensiz olması sonucu değiştirmez.",
    aria="Sikistirma teoremi: cos n bolu n dizisi -1/n ve 1/n zarflari arasinda sifira gider")

# ============================================================ sonsuza-iraksama
M14, NM14 = 20, 5
p1 = seq_panel(44, 40, 210, 150, 8, (0, 70))
seq_axes(p1, (1, 4, 8), (25, 50))
hline(p1, M14, PRACTICE, 1.2, "5 4", 0.85)
p1.vline(NM14, 0, 70, PRACTICE, "4 3", 0.8)
seq_points(p1, [n * n for n in range(1, 9)], PRACTICE, 3.4)
p1.label(0.4, M14, "M", 0, -4, PRACTICE, 11.5, "start", True, True)
p1.label(NM14, 62, "n" + subs("M"), 6, 4, PRACTICE, 11.5, "start", True, True)
panel_title(p1, "a" + SUB_N + " = n&#178; " + RARR + " +" + INF)
p2 = seq_panel(318, 40, 210, 150, 12, (0, 13))
seq_axes(p2, (1, 5, 10), (5, 10))
hline(p2, 4, PRACTICE, 1.2, "5 4", 0.85)
odd = [(n, n) for n in range(1, 13) if n % 2 == 1]
even = [(n, 3) for n in range(1, 13) if n % 2 == 0]
p2.points(odd, PRACTICE, 3.4)
p2.points(even, BASE, 3.4)
p2.label(0.4, 4, "M = 4", 0, -4, PRACTICE, 11.5, "start", True, True)
p2.label(12.6, 3, "çift n: a" + SUB_N + " = 3", 0, 14, BASE, 10.5, "end", True)
panel_title(p2, "tek n: a" + SUB_N + " = n,  çift n: a" + SUB_N + " = 3")
OUT["sonsuza-iraksama"] = figure(
    560, 216, [p1, p2],
    "Solda <em>n</em>&#178; dizisi +&#8734;'a ıraksar: her <em>M</em> için bir <em>n<sub>M</sub></em> vardır ve ondan sonraki "
    "bütün terimler <em>M</em>'yi aşar. Sağdaki dizi sınırsızdır ama +&#8734;'a gitmez: tek indisli terimler büyürken çift "
    "indisliler hep 3'te kalır, dolayısıyla <em>M</em> = 4 çizgisinin üstünde sonsuza dek kalınamaz.",
    css_class=WIDE, aria="Sonsuza iraksama: n kare her M'yi asar; sinirsiz ama sonsuza gitmeyen dizi")

# ============================================================ monoton-sinirli
N15, L15, E15, NE15 = 15, 1.0, 0.2, 6
p = seq_panel(46, 30, 300, 170, N15, (-0.12, 1.5))
seq_axes(p, (1, 5, 10, 15), (0.5, 1))
hband(p, L15 - E15, L15, BASE, 0.14)
for ub in (1.38, 1.2):
    hline(p, ub, REMARK, 1.0, "3 3", 0.6)
hline(p, L15, THEORY, 1.3, "5 4", 0.9)
p.vline(NE15, -0.12, 1.5, PRACTICE, "4 3", 0.8)
seq_points(p, [1 - 1 / n for n in range(1, N15 + 1)], PRACTICE, 3.4)
p.label(0.4, 1.29, "üst sınırlar", 0, 4, REMARK, 10.5, "start", False, True)
p.label(0.4, L15, "L = sup{a" + SUB_N + "} = 1", 0, -4, THEORY, 11.5, "start", True)
p.label(0.4, L15 - E15 / 2, "(L " + MINUS + " " + EPS + ", L]", 0, 4, BASE, 11, "start", True)
p.label(NE15, 1.5, "n" + subs(EPS), 0, -4, PRACTICE, 11.5, "middle", True, True)
p.label(4.2, 0.2, "a" + SUB_N + " = 1 " + MINUS + " 1/n", 0, 0, PRACTICE, 11.5, "start", True)
OUT["monoton-sinirli"] = figure(
    400, 220, [p],
    "Artan ve üstten sınırlı dizi <em>a<sub>n</sub></em> = 1 &#8722; 1/<em>n</em>: terimler kümesinin supremumu "
    "<em>L</em> = 1'dir. Supremum tanımı gereği (<em>L</em> &#8722; <em>&#949;</em>, <em>L</em>] bandına düşen bir "
    "<em>a</em><sub><em>n</em><sub>&#949;</sub></sub> vardır; dizi arttığından sonraki bütün terimler de bu bantta kalır. "
    "Bu, dizinin <em>L</em>'ye yakınsadığını gösterir.",
    aria="Monoton yakinsaklik teoremi: artan sinirli dizi supremumuna yakinsar")

# ============================================================ e-dizisi
N16 = 12
p = seq_panel(46, 30, 300, 170, N16, (1.8, 3.2))
seq_axes(p, (1, 5, 10), (2, 3))
hline(p, 3, REMARK, 1.0, "3 3", 0.6)
hline(p, math.e, THEORY, 1.3, "5 4", 0.9)
seq_points(p, [(1 + 1 / n) ** n for n in range(1, N16 + 1)], PRACTICE, 3.4)
p.label(0.4, 3, "3: üst sınır", 0, -4, REMARK, 10.5, "start", False, True)
p.label(0.4, math.e, "e " + APPROX + " 2,718", 0, -4, THEORY, 11.5, "start", True)
p.label(4.6, 2.05, "a" + SUB_N + " = (1 + 1/n)" + sup("n"), 0, 0, PRACTICE, 11.5, "start", True)
OUT["e-dizisi"] = figure(
    400, 220, [p],
    "(1 + 1/<em>n</em>)<sup><em>n</em></sup> dizisi artar ve 3'ü hiç geçmez; monoton yakınsaklık teoremi gereği bir "
    "limiti vardır. Bu limit <em>e</em> &#8776; 2,718 sayısıdır: dizi ona yavaş yaklaşır, <em>n</em> = 12'de bile "
    "henüz 2,61 civarındadır.",
    aria="(1 + 1/n)^n dizisi: artan, 3 ile sinirli, limiti e")

# ============================================================ alt-dizi
N17 = 14
p = seq_panel(46, 30, 300, 190, N17, (-2.35, 1.95))
seq_axes(p, (1, 5, 10), (-2, -1, 0, 1))
hline(p, 1, BASE, 1.2, "5 4", 0.85)
hline(p, -1, PRACTICE, 1.2, "5 4", 0.85)
vals = [(-1) ** n * (1 + 1 / n) for n in range(1, N17 + 1)]
p.points([(n, v) for n, v in enumerate(vals, 1) if n % 2 == 0], BASE, 3.6)
p.points([(n, v) for n, v in enumerate(vals, 1) if n % 2 == 1], PRACTICE, 3.6)
p.label(8, 1.6, "çift n: a" + SUB_N + " = 1 + 1/n " + RARR + " 1", 0, 4, BASE, 11.5, "middle", True)
p.label(8.5, -1.85, "tek n: a" + SUB_N + " = " + MINUS + "(1 + 1/n) " + RARR + " " + MINUS + "1", 0, 4, PRACTICE, 11.5, "middle", True)
p.label(N17 + 0.6, 0.3, "a" + SUB_N + " = (" + MINUS + "1)" + sup("n") + "(1 + 1/n)", 0, 0, TEXT, 11.5, "end", True)
OUT["alt-dizi"] = figure(
    400, 240, [p],
    "(&#8722;1)<sup><em>n</em></sup>(1 + 1/<em>n</em>) dizisi yakınsamaz, ama iki alt dizisi yakınsar: çift indisli "
    "terimler (<em>a</em><sub>2<em>k</em></sub>) yukarıdan 1'e, tek indisli terimler (<em>a</em><sub>2<em>k</em>&#8722;1</sub>) "
    "aşağıdan &#8722;1'e gider. Farklı limitli iki alt dizi, dizinin kendisinin yakınsak olamayacağını da gösterir.",
    aria="Alt diziler: cift indisli terimler 1'e, tek indisli terimler -1'e yakinsar")

# ============================================================ zirve-noktalari
Z_VALS = (2.0, 0.9, 1.4, 1.7, 0.6, 1.2, 1.5, 0.8, 1.1, 1.35, 0.7, 1.0, 1.25, 0.75, 0.95, 1.15)
N18 = len(Z_VALS)
peaks = [n for n in range(1, N18 + 1) if all(Z_VALS[n - 1] > Z_VALS[m - 1] for m in range(n + 1, N18 + 1))]
p = seq_panel(46, 30, 300, 180, N18, (0.1, 2.3))
seq_axes(p, (1, 5, 10, 15), (1, 2))
for n in peaks:
    p.line([(n, Z_VALS[n - 1]), (N18 + 0.8, Z_VALS[n - 1])], PRACTICE, 0.9, "4 3", 0.4)
p.line([(n, Z_VALS[n - 1]) for n in peaks], PRACTICE, 1.3, "6 4", 0.75)
p.points([(n, v) for n, v in enumerate(Z_VALS, 1) if n not in peaks], REMARK, 3.2)
p.points([(n, Z_VALS[n - 1]) for n in peaks], PRACTICE, 4.4)
for n in peaks[:-1]:
    p.label(n, Z_VALS[n - 1], "zirve", 0, -8, PRACTICE, 10, "middle", False, True)
p.label(N18 + 0.6, 0.32, "kesikli ışın: sonraki bütün terimler altında kalır", 0, 0, PRACTICE, 10.5, "end", False, True)
OUT["zirve-noktalari"] = figure(
    400, 226, [p],
    "Bir terim, kendisinden sonra gelen bütün terimlerden büyükse zirvedir; şekilde zirveler koyu, her birinden sağa "
    "çizilen kesikli ışının altında kalan terimler ise açık renklidir. Zirveler sonsuz çoklukta ise kendileri azalan bir alt "
    "dizi oluşturur; bu, her dizinin monoton bir alt dizisi olduğunun ispatındaki ilk durumdur.",
    aria="Zirve terimleri ve zirvelerin olusturdugu azalan alt dizi")

# ============================================================ limsup-liminf
N19 = 16
vals = [(-1) ** n + 1 / n for n in range(1, N19 + 1)]
sups = [max(vals[k:]) for k in range(N19)]
p = seq_panel(46, 30, 300, 190, N19, (-1.55, 1.95))
seq_axes(p, (1, 5, 10, 15), (-1, 0, 1))
hline(p, 1, THEORY, 1.0, "5 4", 0.7)
hline(p, -1, BASE, 1.0, "5 4", 0.7)
step_line(p, sups, THEORY, 1.6, 0.9)
p.line([(1, -1), (N19 + 0.8, -1)], BASE, 1.6, opacity=0.9)
seq_points(p, vals, PRACTICE, 3.4)
p.label(1.2, 1.78, "sup{a" + SUB_K + " : k " + GEQ + " n} " + DARR + " lim sup = 1", 0, 0, THEORY, 11, "start", True)
p.label(1.2, -1.25, "inf{a" + SUB_K + " : k " + GEQ + " n} = " + MINUS + "1 = lim inf", 0, 4, BASE, 11, "start", True)
p.label(N19 + 0.6, 0.3, "a" + SUB_N + " = (" + MINUS + "1)" + sup("n") + " + 1/n", 0, 0, PRACTICE, 11.5, "end", True)
OUT["limsup-liminf"] = figure(
    400, 240, [p],
    "(&#8722;1)<sup><em>n</em></sup> + 1/<em>n</em> dizisinin iki yığılma noktası vardır: 1 ve &#8722;1. Üstteki basamak "
    "eğrisi <em>n</em>'den sonraki terimlerin supremumudur; azalarak lim sup = 1'e iner. Alttaki çizgi aynı terimlerin "
    "infimumudur: tek indisli terimler &#8722;1'e üstten yaklaştığından her <em>n</em> için infimum tam &#8722;1'dir, "
    "yani lim inf = &#8722;1.",
    aria="lim sup ve lim inf: kuyruk supremumlarinin basamak egrisi ve kuyruk infimumu")

# ============================================================ cauchy-dizi
N20, NE20 = 16, 6
sums, acc = [], 0.0
for k in range(1, N20 + 1):
    acc += (-1) ** (k + 1) / k
    sums.append(acc)
LO20, HI20 = 0.60, 0.80
p = seq_panel(46, 30, 300, 180, N20, (0.35, 1.12))
seq_axes(p, (1, 5, 10, 15), (0.5, 1))
p.polygon([(NE20, LO20), (N20 + 0.8, LO20), (N20 + 0.8, HI20), (NE20, HI20)], BASE, 0.14)
p.line([(NE20, LO20), (N20 + 0.8, LO20)], BASE, 0.9, "3 3", 0.7)
p.line([(NE20, HI20), (N20 + 0.8, HI20)], BASE, 0.9, "3 3", 0.7)
p.vline(NE20, 0.35, 1.12, PRACTICE, "4 3", 0.8)
p.points([(n, v) for n, v in enumerate(sums, 1) if n < NE20], REMARK, 3.4)
p.points([(n, v) for n, v in enumerate(sums, 1) if n >= NE20], PRACTICE, 3.4)
p.arrow((N20 + 0.5, (LO20 + HI20) / 2), (N20 + 0.5, HI20), BASE, 1.2, head=6)
p.arrow((N20 + 0.5, (LO20 + HI20) / 2), (N20 + 0.5, LO20), BASE, 1.2, head=6)
p.label(N20 + 0.5, (LO20 + HI20) / 2, EPS, 8, 4, BASE, 12, "start", True, True)
p.label(NE20, 1.12, "n" + subs(EPS), 0, -4, PRACTICE, 11.5, "middle", True, True)
p.label(NE20 + 0.4, HI20, "m, n " + GEQ + " n" + subs(EPS) + " için |a" + SUB_M + " " + MINUS + " a" + SUB_N + "| &lt; " + EPS, 0, -7, BASE, 11, "start", True)
p.label(6.2, 0.48, "a" + SUB_N + " = 1 " + MINUS + " 1/2 + 1/3 " + MINUS + " " + ELLIP + " " + "&#177;" + " 1/n", 0, 0, PRACTICE, 11.5, "start", True)
OUT["cauchy-dizi"] = figure(
    400, 226, [p],
    "Cauchy dizisi: <em>n<sub>&#949;</sub></em>'dan sonraki bütün terimler genişliği <em>&#949;</em> olan bir şeride "
    "sığar, yani birbirlerine <em>&#949;</em>'dan yakındır. Şekilde hiçbir limit çizilmemiştir; tanım terimleri yalnızca "
    "birbiriyle karşılaştırır. Örnek 1 &#8722; 1/2 + 1/3 &#8722; &#8943; kısmi toplamlarıdır; reel sayılarda böyle bir "
    "dizi mutlaka yakınsar.",
    aria="Cauchy dizisi: n epsilon'dan sonra butun terimler genisligi epsilon olan bir seritte")

# ############################################################################
# PART F3: chapters 27-36 (limits of functions, sequential criterion, squeeze,
# one-sided limits, asymptotes, continuity, discontinuities, Bolzano and
# Weierstrass theorems, uniform continuity)
# ############################################################################

SUP_MINUS, SUP_PLUS = sup(MINUS, 8.5), sup("+", 8.5)
ARROW_R = "&#8594;"


def tfmt(v):
    """Tick label with the Turkish decimal comma: 0.2 -> '0,2'."""
    return fmt(v).replace(".", ",")


def named_ticks(names):
    """Tick formatter printing symbolic names (k, k - 1, ...) for the listed values."""
    return lambda t: names.get(t, fmt(t))


def band(p, x0, x1, y0, y1, color=THEORY, opacity=0.12):
    """Shade the axis-aligned rectangle [x0, x1] x [y0, y1] (data coordinates)."""
    p.polygon([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], color, opacity)


def guide(p, pts, color=TEXT, opacity=0.5, width=1.0):
    """Thin dashed guide line through the given data points."""
    p.line(pts, color, width, "4 3", opacity)


def osc_curve(p, f, x_lo, x_hi, color=THEORY, width=1.4, per_period=24, mirror=True):
    """Graph of y = f(x) on [x_lo, x_hi] (0 < x_lo) sampled uniformly in u = 1/x, so every
    oscillation of sin(1/x) gets `per_period` points; mirror=True also draws [-x_hi, -x_lo]."""
    u0, u1 = 1.0 / x_hi, 1.0 / x_lo
    n = int((u1 - u0) / (2 * PI) * per_period) + 8
    xs = [1.0 / (u1 - (u1 - u0) * k / n) for k in range(n + 1)]   # increasing x
    p.line([(x, f(x)) for x in xs], color, width)
    if mirror:
        p.line([(-x, f(-x)) for x in reversed(xs)], color, width)


# ============================================================ epsilon-delta
def f_lim(x):
    return 0.3 * x * x + 0.5


A_PT, EPS_V, DEL_V = 2.0, 0.35, 0.25
L_PT = f_lim(A_PT)
p = Plot(56, 22, 300, 250, (-0.3, 3.3), (-0.3, 3.3))
band(p, 0, p.xmax, L_PT - EPS_V, L_PT + EPS_V, THEORY, 0.12)
band(p, A_PT - DEL_V, A_PT + DEL_V, 0, p.ymax, PRACTICE, 0.12)
p.origin_axes("x", "y")
for y in (L_PT - EPS_V, L_PT + EPS_V):
    guide(p, [(0, y), (p.xmax, y)], THEORY, 0.55)
for x in (A_PT - DEL_V, A_PT + DEL_V):
    guide(p, [(x, 0), (x, p.ymax)], PRACTICE, 0.55)
guide(p, [(A_PT, 0), (A_PT, L_PT), (0, L_PT)], TEXT, 0.5)
curve(p, f_lim, -0.2, 3.0, THEORY, 1.9)
curve(p, f_lim, A_PT - DEL_V, A_PT + DEL_V, PRACTICE, 2.8)   # the piece of the graph over the window
hollow(p, (A_PT, L_PT), THEORY, 4.2, 1.8)
p.label(A_PT, 0, "a", 0, 15, TEXT, 11.5, "middle", True, True)
p.label(A_PT - DEL_V, 0, "a " + MINUS + " " + DELTA, -1, 15, PRACTICE, 10.5, "end", False, True)
p.label(A_PT + DEL_V, 0, "a + " + DELTA, 1, 15, PRACTICE, 10.5, "start", False, True)
p.label(0, L_PT, ELL, -7, 4, TEXT, 12, "end", True, True)
p.label(0, L_PT - EPS_V, ELL + " " + MINUS + " " + EPS, -7, 4, THEORY, 10.5, "end", False, True)
p.label(0, L_PT + EPS_V, ELL + " + " + EPS, -7, 4, THEORY, 10.5, "end", False, True)
p.label(2.75, f_lim(2.75), "y = f(x)", -8, -4, THEORY, 12, "end", True, True)
p.label(p.xmax, L_PT, "|f(x) " + MINUS + " " + ELL + "| &lt; " + EPS, -4, 4, THEORY, 10.5, "end", False, True)
p.label(A_PT, p.ymax, "0 &lt; |x " + MINUS + " a| &lt; " + DELTA, 0, -4, PRACTICE, 10.5, "middle", False, True)
OUT["epsilon-delta"] = figure(
    400, 296, [p],
    "Limit tanımının resmi: <em>y</em> ekseninde &#8467;'nin &#949; komşuluğu (yatay bant), <em>x</em> ekseninde "
    "<em>a</em>'nın &#948; komşuluğu (düşey pencere). Pencerede <em>a</em> dışındaki her <em>x</em> için grafik banda "
    "düşer; <em>a</em> noktasının kendisi delinmiştir, <em>f</em>(<em>a</em>) tanımlı olmasa da limit vardır. "
    "&#949; küçültülünce ona uygun yeni bir &#948; bulunmalıdır.",
    aria="Limit tanimi: epsilon bandi ve delta penceresi, a noktasi delinmis")

# ============================================================ sin-bir-bolu-x
p = Plot(40, 26, 330, 210, (-0.33, 0.33), (-1.45, 1.45))
p.origin_axes("x", "y", xticks=(-0.2, 0.2), xfmt=tfmt)
guide(p, [(-0.33, 1), (0.33, 1)], TEXT, 0.35)
guide(p, [(-0.33, -1), (0.33, -1)], TEXT, 0.35)
osc_curve(p, lambda x: math.sin(1 / x), 0.007, 0.33, THEORY, 1.4)
X_N = [1 / (PI / 2 + 2 * n * PI) for n in range(1, 5)]      # sin(1/x_n) = 1
Y_N = [1 / (3 * PI / 2 + 2 * n * PI) for n in range(1, 5)]  # sin(1/y_n) = -1
p.points([(x, 1) for x in X_N], BASE, 3.2)
p.points([(y, -1) for y in Y_N], PRACTICE, 3.2)
p.label(X_N[0], 1, "x" + SUB1, 0, -9, BASE, 11, "middle", False, True)
p.label(X_N[1], 1, "x" + SUB2, 0, -9, BASE, 11, "middle", False, True)
p.label(Y_N[0], -1, "y" + SUB1, 3, 15, PRACTICE, 11, "start", False, True)
p.label(Y_N[1], -1, "y" + SUB2, -3, 15, PRACTICE, 11, "end", False, True)
p.label(0.33, 1, "f(x" + subs("n") + ") = 1", -2, -6, BASE, 11, "end", False, True)
p.label(0.33, -1, "f(y" + subs("n") + ") = " + MINUS + "1", -2, 15, PRACTICE, 11, "end", False, True)
p.label(-0.32, 1.32, "y = sin(1/x)", 0, 0, THEORY, 12, "start", True, True)
p.label(-0.32, -1.32, "x" + subs("n") + " " + ARROW_R + " 0,  y" + subs("n") + " " + ARROW_R + " 0", 0, 4, TEXT, 10.5, "start", False, True)
OUT["sin-bir-bolu-x"] = figure(
    400, 262, [p],
    "<em>y</em> = sin(1/<em>x</em>) grafiği 0'a yaklaşırken gitgide sıklaşan salınımlar yapar; her salınımda "
    "&#8722;1 ile 1 arasındaki bütün değerleri alır. <em>x</em><sub><em>n</em></sub> noktalarında değer hep 1, "
    "<em>y</em><sub><em>n</em></sub> noktalarında hep &#8722;1'dir. İki dizi de 0'a gider ama görüntüleri farklı "
    "limitlere gittiğinden <em>x</em> &#8594; 0 iken limit yoktur.",
    aria="sin(1/x) grafigi ve 0'a giden x_n, y_n dizileri; goruntuler 1 ve -1")

# ============================================================ taban-limit-yok
K = 2
p = Plot(50, 24, 300, 226, (-0.5, 3.7), (-0.5, 3.6))
K_NAMES = {1: "k " + MINUS + " 1", 2: "k", 3: "k + 1"}
p.origin_axes("x", "y", xticks=(1, 2, 3), yticks=(1, 2, 3), xfmt=named_ticks(K_NAMES), yfmt=named_ticks(K_NAMES))
for m in range(0, 4):                       # the steps of the floor function
    p.line([(m, m), (min(m + 1, 3.6), m)], THEORY, 2.0)
    dot(p, (m, m), THEORY, 3.6)
    if m + 1 <= 3.6:
        hollow(p, (m + 1, m), THEORY, 3.6, 1.6)
XS = [K + 1.0 / n for n in range(2, 6)]     # from the right: floor = k
YS = [K - 1.0 / n for n in range(2, 6)]     # from the left: floor = k - 1
p.points([(x, K) for x in XS], PRACTICE, 3.4)
p.points([(y, K - 1) for y in YS], BASE, 3.4)
p.label(XS[0], K, "x" + SUB2, 2, -9, PRACTICE, 11, "start", False, True)
p.label(XS[1], K, "x" + SUB3, -2, -9, PRACTICE, 11, "end", False, True)
p.label(YS[0], K - 1, "y" + SUB2, -2, 16, BASE, 11, "end", False, True)
p.label(YS[1], K - 1, "y" + SUB3, 2, 16, BASE, 11, "start", False, True)
p.arrow((2.85, K + 0.45), (K + 0.12, K + 0.45), PRACTICE, 1.5, head=7)
p.label(2.48, K + 0.45, "x" + subs("n") + " " + ARROW_R + " k", 0, -7, PRACTICE, 11, "middle", False, True)
p.arrow((1.15, K - 1 - 0.45), (K - 0.12, K - 1 - 0.45), BASE, 1.5, head=7)
p.label(1.52, K - 1 - 0.45, "y" + subs("n") + " " + ARROW_R + " k", 0, 16, BASE, 11, "middle", False, True)
p.label(3.05, K, "f(x" + subs("n") + ") = k", 8, 4, PRACTICE, 10.5, "start", False, True)
p.label(1.05, K - 1, "f(y" + subs("n") + ") = k " + MINUS + " 1", 0, -9, BASE, 10.5, "start", False, True)
p.label(0.25, 0, "y = &#8970;x&#8971;", 4, -8, THEORY, 12, "start", True, True)
OUT["taban-limit-yok"] = figure(
    400, 272, [p],
    "Taban fonksiyonunun <em>k</em> tam sayısı yakınındaki grafiği. Sağdan yaklaşan "
    "<em>x</em><sub><em>n</em></sub> = <em>k</em> + 1/<em>n</em> dizisinde değerler hep <em>k</em>, soldan yaklaşan "
    "<em>y</em><sub><em>n</em></sub> = <em>k</em> &#8722; 1/<em>n</em> dizisinde hep <em>k</em> &#8722; 1'dir. "
    "İki dizi de <em>k</em>'ya gittiği hâlde görüntüleri farklı yerlere gider; dizisel ölçüt gereği "
    "<em>k</em>'da limit yoktur.",
    aria="Taban fonksiyonu k civarinda: sagdan gelen dizi k, soldan gelen dizi k-1 degerini verir")

# ============================================================ x-sin-bir-bolu-x
p = Plot(40, 24, 330, 220, (-0.42, 0.42), (-0.45, 0.45))
p.polygon([(0, 0), (0.42, 0.42), (0.42, -0.42)], THEORY, 0.07)     # the region |y| <= |x|
p.polygon([(0, 0), (-0.42, 0.42), (-0.42, -0.42)], THEORY, 0.07)
p.origin_axes("x", "y", xticks=(-0.2, 0.2), yticks=(-0.2, 0.2), xfmt=tfmt, yfmt=tfmt)
p.line([(-0.42, 0.42), (0, 0), (0.42, 0.42)], PRACTICE, 1.3, "5 4", 0.85)
p.line([(-0.42, -0.42), (0, 0), (0.42, -0.42)], PRACTICE, 1.3, "5 4", 0.85)
osc_curve(p, lambda x: x * math.sin(1 / x), 0.01, 0.42, THEORY, 1.5)
p.label(0.31, 0.31, "y = |x|", -6, -6, PRACTICE, 11.5, "end", False, True)
p.label(0.31, -0.31, "y = " + MINUS + "|x|", -6, 13, PRACTICE, 11.5, "end", False, True)
p.text_px(p.X(0) - 10, p.y0 + 14, "y = x sin(1/x)", THEORY, 12, "end", True, True)
OUT["x-sin-bir-bolu-x"] = figure(
    400, 268, [p],
    "<em>y</em> = <em>x</em> sin(1/<em>x</em>) grafiği, kesikli çizilen <em>y</em> = |<em>x</em>| ve "
    "<em>y</em> = &#8722;|<em>x</em>| zarfları arasında kalır: &#8722;|<em>x</em>| &#8804; <em>x</em> sin(1/<em>x</em>) "
    "&#8804; |<em>x</em>|. Salınımlar 0'a yaklaşırken sıklaşır, ama iki zarf 0'da birleştiğinden fonksiyon "
    "aralarında sıkışıp 0'a gider.",
    aria="x sin(1/x) grafigi, |x| ve -|x| zarflari arasinda 0'a sikisiyor")

# ============================================================ sin-x-bolu-x-geometri
XA = 0.8                                    # the angle x (radians)
CX, SX, TX = math.cos(XA), math.sin(XA), math.tan(XA)
PPU = 320 / 1.7                             # equal aspect
p = Plot(40, 20, 320, 1.4 * PPU, (-0.25, 1.45), (-0.25, 1.15))
p.origin_axes("", "")
p.arc(0, 0, 1, -0.12, PI / 2 + 0.06, TEXT, 1.0, opacity=0.4)
p.polygon([(0, 0), (1, 0), (1, TX)], PRACTICE, 0.10, PRACTICE, 1.4)    # big triangle OAT
p.sector(0, 0, 1, 0, XA, THEORY, 0.18)                                  # sector OAP
p.arc(0, 0, 1, 0, XA, THEORY, 2.2)
p.polygon([(0, 0), (1, 0), (CX, SX)], BASE, 0.20, BASE, 1.4)            # small triangle OAP
p.line([(0, 0), (1, TX)], PRACTICE, 1.4)
p.line([(0, 0), (CX, SX)], THEORY, 1.8)
guide(p, [(CX, SX), (CX, 0)], BASE, 0.8)                                # height sin x
RA = 0.05                                                               # right-angle mark at the foot
p.line([(CX - RA, 0), (CX - RA, RA), (CX, RA)], BASE, 1.0, opacity=0.8)
p.arc(0, 0, 0.22, 0, XA, THEORY, 1.3)
p.label(*polar(0.32, XA / 2), "x", 0, 4, THEORY, 12.5, "middle", True, True)
dot(p, (0, 0), TEXT, 3.2)
dot(p, (1, 0), TEXT, 3.2)
dot(p, (CX, SX), THEORY, 3.6)
dot(p, (1, TX), PRACTICE, 3.6)
p.label(0, 0, "O", -6, 15, TEXT, 11.5, "end", False, True)
p.label(1, 0, "B = (1, 0)", 4, 15, TEXT, 11, "start", False, True)
p.label(CX, SX, "P = (cos x, sin x)", -4, -9, THEORY, 11, "end", False, True)
p.label(1, TX, "T = (1, tan x)", 8, 4, PRACTICE, 11, "start", False, True)
p.label(CX, SX / 2, "sin x", -5, 4, BASE, 11.5, "end", False, True)
p.label(1, TX / 2, "tan x", 7, 4, PRACTICE, 11.5, "start", False, True)
p.label(0.5, 0, "1", 0, 14, TEXT, 11, "middle", False, True)
by = p.y0 + p.h + 28
p.text_px(p.x0 + p.w / 2, by, "alan: " + f'<tspan fill="{BASE}">üçgen OBP</tspan> &#8804; '
          f'<tspan fill="{THEORY}">daire dilimi OBP</tspan> &#8804; <tspan fill="{PRACTICE}">üçgen OBT</tspan>',
          TEXT, 11, "middle", False, True)
p.text_px(p.x0 + p.w / 2, by + 18, f'<tspan fill="{BASE}">&#189; sin x</tspan> &#8804; '
          f'<tspan fill="{THEORY}">&#189; x</tspan> &#8804; <tspan fill="{PRACTICE}">&#189; tan x</tspan>',
          TEXT, 12.5, "middle", True)
OUT["sin-x-bolu-x-geometri"] = figure(
    400, 340, [p],
    "Birim çemberde <em>x</em> açısı için üç alan iç içedir: <em>OBP</em> üçgeni (yüksekliği sin <em>x</em>), "
    "<em>OBP</em> daire dilimi (alanı <em>x</em>/2) ve <em>OBT</em> dik üçgeni (yüksekliği tan <em>x</em>). "
    "Alanları karşılaştırmak sin <em>x</em> &#8804; <em>x</em> &#8804; tan <em>x</em> eşitsizliğini verir; "
    "sin <em>x</em>'e bölüp sıkıştırınca sin <em>x</em>/<em>x</em> &#8594; 1 çıkar.",
    aria="Birim cemberde ucgen, daire dilimi ve buyuk ucgen: sin x, x ve tan x alan karsilastirmasi")

# ============================================================ tek-yonlu-limit
A1, LM, LP, FA = 2.0, 1.4, 2.4, 1.9


def g_left(x):
    return LM - 0.3 * (A1 - x) - 0.1 * (A1 - x) ** 2


def g_right(x):
    return LP + 0.25 * (x - A1) - 0.08 * (x - A1) ** 2


p = Plot(54, 22, 300, 236, (-0.3, 4.0), (-0.3, 3.3))
p.origin_axes("x", "y")
guide(p, [(0, LM), (A1, LM)], THEORY, 0.55)
guide(p, [(0, LP), (A1, LP)], PRACTICE, 0.55)
guide(p, [(0, FA), (A1, FA)], TEXT, 0.45)
guide(p, [(A1, 0), (A1, LP)], TEXT, 0.45)
curve(p, g_left, 0.3, A1, THEORY, 2.0)
curve(p, g_right, A1, 3.8, PRACTICE, 2.0)
hollow(p, (A1, LM), THEORY, 4.2, 1.8)
hollow(p, (A1, LP), PRACTICE, 4.2, 1.8)
dot(p, (A1, FA), TEXT, 4.2)
p.label(0, LM, "f(a" + SUP_MINUS + ")", -7, 4, THEORY, 11.5, "end", False, True)
p.label(0, LP, "f(a" + SUP_PLUS + ")", -7, 4, PRACTICE, 11.5, "end", False, True)
p.label(0, FA, "f(a)", -7, 4, TEXT, 11.5, "end", False, True)
p.label(A1, 0, "a", 0, 15, TEXT, 11.5, "middle", True, True)
p.arrow((1.05, 0.4), (A1 - 0.15, 0.4), THEORY, 1.5, head=7)
p.label(1.0, 0.4, "x " + ARROW_R + " a" + SUP_MINUS, -4, 4, THEORY, 11, "end", False, True)
p.arrow((2.95, 0.4), (A1 + 0.15, 0.4), PRACTICE, 1.5, head=7)
p.label(3.0, 0.4, "x " + ARROW_R + " a" + SUP_PLUS, 4, 4, PRACTICE, 11, "start", False, True)
p.label(3.3, g_right(3.3), "y = f(x)", 0, 18, TEXT, 12, "middle", True, True)
OUT["tek-yonlu-limit"] = figure(
    400, 282, [p],
    "<em>a</em> noktasında sıçrayan bir fonksiyon. Soldan yaklaşınca değerler <em>f</em>(<em>a</em><sup>&#8722;</sup>)'ye, "
    "sağdan yaklaşınca <em>f</em>(<em>a</em><sup>+</sup>)'ya yığılır; iki tek yönlü limit de vardır ama farklıdır, "
    "bu yüzden <em>x</em> &#8594; <em>a</em> limiti yoktur. Fonksiyonun <em>a</em>'daki değeri <em>f</em>(<em>a</em>) "
    "ise ikisinden de bağımsızdır: tek yönlü limitler yalnızca <em>a</em>'nın yanındaki noktalara bakar.",
    aria="Sicramali fonksiyon: sol limit, sag limit ve f(a) uc ayri deger")

# ============================================================ asimptotlar
p1 = Plot(34, 26, 232, 200, (-2.3, 2.3), (-0.6, 4.6))
p1.origin_axes("x", "y", xticks=(-2, -1, 1, 2), yticks=(1, 2, 3, 4))
p1.line([(0, -0.6), (0, 4.6)], PRACTICE, 1.4, "5 4", 0.85)
curve(p1, lambda x: 1 / (x * x), -2.3, -0.482, THEORY, 1.9, 200)
curve(p1, lambda x: 1 / (x * x), 0.482, 2.3, THEORY, 1.9, 200)
panel_title(p1, "düşey asimptot: x = 0")
p1.label(1.2, 1 / 1.44, "y = 1/x" + sup("2"), 8, -4, THEORY, 12, "start", True, True)

p2 = Plot(316, 26, 232, 200, (-4.3, 6.3), (-5.3, 9.3))
p2.origin_axes("x", "y", xticks=(-2, 2, 4), yticks=(-2, 4, 6))
p2.line([(1, -5.3), (1, 9.3)], PRACTICE, 1.4, "5 4", 0.85)
p2.line([(-4.3, 2), (6.3, 2)], BASE, 1.4, "5 4", 0.85)
curve(p2, lambda x: 2 + 3 / (x - 1), -4.3, 0.59, THEORY, 1.9, 240)
curve(p2, lambda x: 2 + 3 / (x - 1), 1.42, 6.3, THEORY, 1.9, 240)
panel_title(p2, "y = (2x + 1)/(x " + MINUS + " 1)")
p2.label(1, -4.6, "x = 1", 6, 4, PRACTICE, 10.5, "start", False, True)
p2.label(6.2, 2, "y = 2", 0, 13, BASE, 10.5, "end", False, True)
OUT["asimptotlar"] = figure(
    560, 248, [p1, p2],
    "Solda <em>y</em> = 1/<em>x</em><sup>2</sup>: <em>x</em> &#8594; 0 iken değerler sınırsız büyür, grafik "
    "<em>x</em> = 0 doğrusuna yaslanır (düşey asimptot); <em>x</em> &#8594; &#177;&#8734; iken de 0'a yaklaşır. "
    "Sağda <em>y</em> = (2<em>x</em> + 1)/(<em>x</em> &#8722; 1): <em>x</em> = 1'de düşey asimptot vardır; "
    "<em>x</em> &#8594; &#177;&#8734; iken limit 2 olduğundan <em>y</em> = 2 doğrusu yatay asimptottur.",
    css_class=WIDE, aria="Dusey asimptot x=0 (1/x kare) ve yatay asimptot y=2 ile dusey asimptot x=1")

# ============================================================ sureklilik-epsilon-delta
def f_cont(x):
    return 1.6 + 0.9 * math.sin(1.4 * (x - 1.2))


A_C, EPS_C, DEL_C = 1.9, 0.4, 0.35
FA_C = f_cont(A_C)
p = Plot(64, 22, 292, 250, (-0.3, 3.3), (-0.3, 3.3))
band(p, 0, p.xmax, FA_C - EPS_C, FA_C + EPS_C, THEORY, 0.12)
band(p, A_C - DEL_C, A_C + DEL_C, 0, p.ymax, PRACTICE, 0.12)
p.origin_axes("x", "y")
for y in (FA_C - EPS_C, FA_C + EPS_C):
    guide(p, [(0, y), (p.xmax, y)], THEORY, 0.55)
for x in (A_C - DEL_C, A_C + DEL_C):
    guide(p, [(x, 0), (x, p.ymax)], PRACTICE, 0.55)
guide(p, [(A_C, 0), (A_C, FA_C), (0, FA_C)], TEXT, 0.5)
curve(p, f_cont, -0.2, 3.2, THEORY, 1.9)
curve(p, f_cont, A_C - DEL_C, A_C + DEL_C, PRACTICE, 2.8)
dot(p, (A_C, FA_C), THEORY, 4.2)
p.label(A_C, 0, "a", 0, 15, TEXT, 11.5, "middle", True, True)
p.label(A_C - DEL_C, 0, "a " + MINUS + " " + DELTA, -1, 15, PRACTICE, 10.5, "end", False, True)
p.label(A_C + DEL_C, 0, "a + " + DELTA, 1, 15, PRACTICE, 10.5, "start", False, True)
p.label(0, FA_C, "f(a)", -7, 4, TEXT, 11.5, "end", True, True)
p.label(0, FA_C - EPS_C, "f(a) " + MINUS + " " + EPS, -7, 4, THEORY, 10.5, "end", False, True)
p.label(0, FA_C + EPS_C, "f(a) + " + EPS, -7, 4, THEORY, 10.5, "end", False, True)
p.label(0.35, f_cont(0.35), "y = f(x)", -2, 16, THEORY, 12, "start", True, True)
p.label(p.xmax, FA_C, "|f(x) " + MINUS + " f(a)| &lt; " + EPS, -4, 4, THEORY, 10.5, "end", False, True)
p.label(A_C, p.ymax, "|x " + MINUS + " a| &lt; " + DELTA, 0, -4, PRACTICE, 10.5, "middle", False, True)
OUT["sureklilik-epsilon-delta"] = figure(
    400, 296, [p],
    "Süreklilik tanımının resmi: <em>f</em>(<em>a</em>)'nın &#949; komşuluğu (yatay bant) verilince, <em>a</em>'nın "
    "öyle bir &#948; komşuluğu (düşey pencere) bulunur ki pencerenin tamamı, <em>a</em>'nın kendisi dâhil, banda "
    "taşınır. Limit resminden farkı, <em>a</em> noktasının artık delinmemesi ve hedef değerin "
    "<em>f</em>(<em>a</em>) olmasıdır.",
    aria="Sureklilik tanimi: epsilon bandi ve delinmemis delta penceresi")

# ============================================================ sureksizlik-turleri
A_D = 1.6
panels = [Plot(24 + 180 * i, 30, 152, 140, (-0.3, 3.3), (-0.3, 3.3)) for i in range(3)]
for p in panels:
    p.origin_axes("", "")
    guide(p, [(A_D, 0), (A_D, 3.3)], TEXT, 0.35)
    p.label(A_D, 0, "a", 0, 14, TEXT, 11, "middle", True, True)
# (a) removable: the limit exists, f(a) sits elsewhere
p = panels[0]
panel_title(p, "kaldırılabilir")
f_rem = lambda x: 0.8 + 0.45 * x + 0.3 * math.sin(2 * x)
curve(p, f_rem, 0.1, 3.1, THEORY, 1.9)
hollow(p, (A_D, f_rem(A_D)), THEORY, 3.8, 1.6)
dot(p, (A_D, 2.55), THEORY, 3.8)
p.label(A_D, 2.55, "f(a)", 7, 4, THEORY, 10.5, "start", False, True)
# (b) jump: both one-sided limits exist, they differ
p = panels[1]
panel_title(p, "sıçrama")
curve(p, lambda x: 0.9 + 0.35 * x, 0.1, A_D, THEORY, 1.9)
curve(p, lambda x: 2.1 + 0.3 * (x - A_D), A_D, 3.1, THEORY, 1.9)
hollow(p, (A_D, 2.1), THEORY, 3.8, 1.6)
dot(p, (A_D, 0.9 + 0.35 * A_D), THEORY, 3.8)
# (c) second kind: a one-sided limit fails to exist (here f blows up on both sides)
p = panels[2]
panel_title(p, "ikinci tür")
f_inf = lambda x: 0.9 + 0.35 / abs(x - A_D)
p.line([(A_D, 0), (A_D, 3.3)], PRACTICE, 1.2, "5 4", 0.8)
curve(p, f_inf, 0.1, A_D - 0.15, THEORY, 1.9, 200)
curve(p, f_inf, A_D + 0.15, 3.1, THEORY, 1.9, 200)
OUT["sureksizlik-turleri"] = figure(
    560, 196, panels,
    "Üç süreksizlik türü. Solda kaldırılabilir süreksizlik: limit vardır ama <em>f</em>(<em>a</em>) ondan farklıdır "
    "(ya da tanımsızdır); değer düzeltilirse süreklilik sağlanır. Ortada sıçrama: sağ ve sol limitler vardır ama eşit "
    "değildir. Sağda ikinci tür: tek yönlü limitlerden en az biri (burada ikisi de) sonlu bir sayı olarak yoktur.",
    css_class=WIDE, aria="Kaldirilabilir, sicrama ve ikinci tur sureksizlik ornekleri")

# ============================================================ ara-deger
A0, B0 = 0.5, 3.5


def f_ivt(x):
    return 0.45 * (x - 2) + 0.35 * math.sin(2.2 * x)


lo, hi = 2.0, 3.0                            # bisection for the zero c
for _ in range(60):
    mid = (lo + hi) / 2
    if f_ivt(mid) < 0:
        lo = mid
    else:
        hi = mid
C0 = (lo + hi) / 2
p = Plot(50, 24, 300, 220, (-0.3, 4.0), (-0.9, 1.5))
p.origin_axes("x", "y")
guide(p, [(A0, 0), (A0, f_ivt(A0))], TEXT, 0.5)
guide(p, [(B0, 0), (B0, f_ivt(B0))], TEXT, 0.5)
p.line([(A0, 0), (C0, 0)], BASE, 5.0, opacity=0.45)          # S = {x : f(x) < 0}
curve(p, f_ivt, A0, B0, THEORY, 2.0)
dot(p, (A0, f_ivt(A0)), THEORY, 3.6)
dot(p, (B0, f_ivt(B0)), THEORY, 3.6)
dot(p, (C0, 0), PRACTICE, 4.2)
p.label(A0, 0, "a", 0, 15, TEXT, 11.5, "middle", True, True)
p.label(B0, 0, "b", 0, 15, TEXT, 11.5, "middle", True, True)
p.label(C0, 0, "c", 0, 16, PRACTICE, 11.5, "middle", True, True)
p.label(C0, 0, "c = sup S", 0, 30, PRACTICE, 10.5, "middle", False, True)
p.label(C0, 0, "f(c) = 0", -8, -8, PRACTICE, 11, "end", False, True)
p.label(A0, f_ivt(A0), "f(a) &lt; 0", 0, 16, THEORY, 11, "middle", False, True)
p.label(B0, f_ivt(B0), "f(b) &gt; 0", 0, -9, THEORY, 11, "middle", False, True)
p.label((A0 + C0) / 2, 0, "S = {x : f(x) &lt; 0}", 0, 15, BASE, 10.5, "middle", False, True)
p.label(2.9, f_ivt(2.9), "y = f(x)", -10, -2, THEORY, 12, "end", True, True)
OUT["ara-deger"] = figure(
    400, 266, [p],
    "Bolzano teoremi: [<em>a</em>, <em>b</em>] üzerinde sürekli <em>f</em> için <em>f</em>(<em>a</em>) &lt; 0 &lt; "
    "<em>f</em>(<em>b</em>) ise grafik <em>x</em> eksenini bir <em>c</em> noktasında kesmek zorundadır. İspatta "
    "<em>c</em>, fonksiyonun negatif kaldığı <em>S</em> kümesinin supremumu olarak seçilir: eksende koyu çizilen "
    "parçanın sağ ucu.",
    aria="Bolzano teoremi: uclarda zit isaretli surekli fonksiyonun grafigi ekseni c noktasinda kesiyor")

# ============================================================ weierstrass-ekstremum
def f_ext(x):
    return 1.7 + 0.9 * math.sin(1.9 * (x - 0.5)) - 0.12 * x


AW, BW = 0.5, 3.5
samples = [(AW + (BW - AW) * k / 400, f_ext(AW + (BW - AW) * k / 400)) for k in range(401)]
XM, YM = max(samples, key=lambda t: t[1])
Xm, Ym = min(samples, key=lambda t: t[1])
p1 = Plot(44, 26, 222, 200, (-0.3, 4.0), (-0.3, 3.3))
p1.origin_axes("x", "y")
panel_title(p1, "[a, b] kapalı: max ve min alınır")
guide(p1, [(0, YM), (XM, YM), (XM, 0)], THEORY, 0.55)
guide(p1, [(0, Ym), (Xm, Ym), (Xm, 0)], PRACTICE, 0.55)
guide(p1, [(AW, 0), (AW, f_ext(AW))], TEXT, 0.4)
guide(p1, [(BW, 0), (BW, f_ext(BW))], TEXT, 0.4)
curve(p1, f_ext, AW, BW, THEORY, 2.0)
dot(p1, (AW, f_ext(AW)), TEXT, 3.4)
dot(p1, (BW, f_ext(BW)), TEXT, 3.4)
dot(p1, (XM, YM), THEORY, 4.0)
dot(p1, (Xm, Ym), PRACTICE, 4.0)
p1.label(AW, 0, "a", 0, 15, TEXT, 11, "middle", True, True)
p1.label(BW, 0, "b", 0, 15, TEXT, 11, "middle", True, True)
p1.label(XM, 0, "x" + subs("M"), 0, 15, THEORY, 11, "middle", True, True)
p1.label(Xm, 0, "x" + subs("m"), 0, 15, PRACTICE, 11, "middle", True, True)
p1.label(0, YM, "max f", -7, 4, THEORY, 10.5, "end", False, True)
p1.label(0, Ym, "min f", -7, 4, PRACTICE, 10.5, "end", False, True)

p2 = Plot(322, 26, 222, 200, (-0.15, 1.45), (-0.5, 6.5))
p2.origin_axes("x", "y", xticks=(0.5, 1), yticks=(2, 4, 6), xfmt=tfmt)
panel_title(p2, "(0, 1] kapalı değil: 1/x sınırsız")
segment(p2, 0, 1, 0, PRACTICE, 4.0, 0.5, False, True, 3.6)             # the domain (0, 1]
curve(p2, lambda x: 1 / x, 1 / 6.3, 1, THEORY, 2.0, 200)
dot(p2, (1, 1), THEORY, 4.0)
p2.label(1, 1, "min f = f(1) = 1", -6, 15, THEORY, 10.5, "end", False, True)
p2.label(0.34, 5.6, "sup f = +" + INF + ", max yok", 0, 4, PRACTICE, 10.5, "start", False, True)
p2.label(0.55, 1 / 0.55, "y = 1/x", 8, -2, THEORY, 12, "start", True, True)
OUT["weierstrass-ekstremum"] = figure(
    560, 248, [p1, p2],
    "Solda kapalı [<em>a</em>, <em>b</em>] aralığında sürekli bir fonksiyon: en büyük değer "
    "<em>x</em><sub><em>M</em></sub>'de, en küçük değer <em>x</em><sub><em>m</em></sub>'de gerçekten alınır. "
    "Sağda (0, 1] üzerinde <em>f</em>(<em>x</em>) = 1/<em>x</em>: aralık kapalı olmadığından fonksiyon sınırsızdır "
    "ve en büyük değer yoktur; en küçük değer <em>f</em>(1) = 1 ise alınır.",
    css_class=WIDE, aria="Kapali aralikta surekli fonksiyon max ve min alir; (0,1] uzerinde 1/x sinirsiz")

# ============================================================ duzgun-sureklilik
p1 = Plot(46, 26, 220, 210, (-0.3, 3.7), (-0.8, 11.2))
EPS_U = 1.0
for x_c, dlt in ((1.0, math.sqrt(2) - 1), (3.0, math.sqrt(10) - 3)):   # delta = the smaller half-width
    y_c = x_c * x_c
    band(p1, 0, p1.xmax, y_c - EPS_U, y_c + EPS_U, THEORY, 0.12)
    band(p1, x_c - dlt, x_c + dlt, 0, p1.ymax, PRACTICE, 0.16)
    guide(p1, [(0, y_c - EPS_U), (p1.xmax, y_c - EPS_U)], THEORY, 0.5)
    guide(p1, [(0, y_c + EPS_U), (p1.xmax, y_c + EPS_U)], THEORY, 0.5)
p1.origin_axes("x", "y", xticks=(1, 3), yticks=(1, 9))
panel_title(p1, "f(x) = x" + sup("2") + ": aynı " + EPS + ", farklı " + DELTA)
curve(p1, lambda x: x * x, -0.2, 3.32, THEORY, 1.9)
dot(p1, (1, 1), THEORY, 3.6)
dot(p1, (3, 9), THEORY, 3.6)
p1.label(1, 11.2, DELTA + SUB1, 0, 13, PRACTICE, 11, "middle", True, True)
p1.label(3, 11.2, DELTA + SUB2, 0, 13, PRACTICE, 11, "middle", True, True)
p1.label(p1.xmax, 1, EPS, -3, 4, THEORY, 11.5, "end", True, True)
p1.label(p1.xmax, 9, EPS, -3, 4, THEORY, 11.5, "end", True, True)

p2 = Plot(322, 26, 222, 210, (-0.12, 1.15), (-0.8, 8.4))
for x_c, dlt in ((0.5, 0.5 - 1 / 3), (0.2, 0.2 - 1 / 6)):
    y_c = 1 / x_c
    band(p2, 0, p2.xmax, y_c - EPS_U, y_c + EPS_U, THEORY, 0.12)
    band(p2, x_c - dlt, x_c + dlt, 0, p2.ymax, PRACTICE, 0.16)
    guide(p2, [(0, y_c - EPS_U), (p2.xmax, y_c - EPS_U)], THEORY, 0.5)
    guide(p2, [(0, y_c + EPS_U), (p2.xmax, y_c + EPS_U)], THEORY, 0.5)
p2.origin_axes("x", "y", xticks=(0.2, 0.5, 1), yticks=(2, 5), xfmt=tfmt)
panel_title(p2, "f(x) = 1/x, (0, 1): 0'a yaklaştıkça " + DELTA + " küçülür")
curve(p2, lambda x: 1 / x, 1 / 8.3, 1.0, THEORY, 1.9, 200)
dot(p2, (0.5, 2), THEORY, 3.6)
dot(p2, (0.2, 5), THEORY, 3.6)
p2.label(0.5, 8.4, DELTA + SUB1, 0, 13, PRACTICE, 11, "middle", True, True)
p2.label(0.2, 8.4, DELTA + SUB2, 0, 13, PRACTICE, 11, "middle", True, True)
p2.label(p2.xmax, 2, EPS, -3, 4, THEORY, 11.5, "end", True, True)
p2.label(p2.xmax, 5, EPS, -3, 4, THEORY, 11.5, "end", True, True)
OUT["duzgun-sureklilik"] = figure(
    560, 256, [p1, p2],
    "Solda <em>f</em>(<em>x</em>) = <em>x</em><sup>2</sup>: aynı &#949; için <em>x</em> = 1 yakınında geniş, "
    "<em>x</em> = 3 yakınında dar bir &#948; yeter; eğim büyüdükçe &#948; küçülür ama sınırlı bir aralıkta en "
    "küçük &#948; bütün noktalara yetişir. Sağda (0, 1) üzerinde <em>f</em>(<em>x</em>) = 1/<em>x</em>: 0'a "
    "yaklaştıkça aynı &#949; için gereken &#948; sınırsız küçülür; bütün noktalara birden uyan tek bir &#948; "
    "yoktur, fonksiyon düzgün sürekli değildir.",
    css_class=WIDE, aria="Ayni epsilon icin x kare fonksiyonunda farkli delta'lar ve 1/x'te 0'a yaklasirken kucule delta")

# ############################################################################
# ---- Extra figures requested by the chapter authors
# (fixed point, equivalent forms of completeness, sign function, infinite
# limit, limit at infinity, one-sided limits of a monotone function)
# ############################################################################

SUB_0 = "&#8320;"          # subscript zero, x₀


# ============================================================ sabit-nokta
def f_fix(x):
    return 0.8 - 0.5 * x + 0.25 * math.sin(4 * x)


lo, hi = 0.5, 0.8                            # bisection for the fixed point f(c) = c
for _ in range(60):
    mid = (lo + hi) / 2
    if f_fix(mid) - mid > 0:
        lo = mid
    else:
        hi = mid
C_FIX = (lo + hi) / 2
p = Plot(96, 30, 220, 220, (0, 1), (0, 1))   # the panel is exactly the unit square
p.add(f'<rect x="{p.x0}" y="{p.y0}" width="{p.w}" height="{p.h}" fill="none" stroke="{TEXT}" stroke-width="1.1" opacity="0.45"/>')
p.text_px(p.X(0), p.Y(0) + 16, "0", TEXT, 11, "middle")
p.text_px(p.X(1), p.Y(0) + 16, "1", TEXT, 11, "middle")
p.text_px(p.X(0) - 7, p.Y(1) + 4, "1", TEXT, 11, "end")
p.text_px(p.X(1) + 14, p.Y(0) + 4, "x", TEXT, 11, "start", False, True)
p.text_px(p.X(0) - 4, p.Y(1) - 14, "y", TEXT, 11, "middle", False, True)
guide(p, [(0, 0), (1, 1)], REMARK, 0.7)
p.label(0.5, 0.5, "y = x", -8, -4, REMARK, 11.5, "end", False, True)
guide(p, [(C_FIX, 0), (C_FIX, C_FIX)], TEXT, 0.5)
curve(p, f_fix, 0, 1, THEORY, 2.0, 200)
p.label(0.26, f_fix(0.26), "y = f(x)", 0, -9, THEORY, 12, "middle", True, True)
dot(p, (0, f_fix(0)), THEORY, 3.4)
dot(p, (1, f_fix(1)), THEORY, 3.4)
p.label(0, f_fix(0), "f(0)", 6, 14, THEORY, 10.5, "start", False, True)
p.label(1, f_fix(1), "f(1)", -6, 14, THEORY, 10.5, "end", False, True)
dot(p, (C_FIX, C_FIX), PRACTICE, 4.4)
p.label(C_FIX, 0, "c", 0, 16, PRACTICE, 11.5, "middle", True, True)
p.label(C_FIX, C_FIX, "f(c) = c", 10, 16, PRACTICE, 11.5, "start", True)
# g(x) = f(x) - x at the two ends: up on the left edge, down on the right edge
arrow_px(p, p.X(0) - 12, p.Y(0), p.X(0) - 12, p.Y(f_fix(0)), BASE, 1.6, 7)
p.text_px(p.X(0) - 18, (p.Y(0) + p.Y(f_fix(0))) / 2 + 4, "g(0) " + GEQ + " 0", BASE, 10.5, "end")
arrow_px(p, p.X(1) + 12, p.Y(1), p.X(1) + 12, p.Y(f_fix(1)), PRACTICE, 1.6, 7)
p.text_px(p.X(1) + 18, (p.Y(1) + p.Y(f_fix(1))) / 2 + 4, "g(1) " + LEQ + " 0", PRACTICE, 10.5, "start")
OUT["sabit-nokta"] = figure(
    400, 280, [p],
    "Sürekli <em>f</em>: [0, 1] &#8594; [0, 1] fonksiyonunun grafiği kareyi sol kenardan sağ kenara geçerken "
    "<em>y</em> = <em>x</em> köşegenini kesmek zorundadır; kesişim noktası <em>c</em>, <em>f</em>(<em>c</em>) = <em>c</em> "
    "sabit noktasıdır. <em>g</em>(<em>x</em>) = <em>f</em>(<em>x</em>) &#8722; <em>x</em> farkı 0'da &#8805; 0, 1'de "
    "&#8804; 0 olduğundan Bolzano teoremi arada bir sıfır verir.",
    aria="Birim karede surekli fonksiyon grafigi kosegeni kesiyor: sabit nokta c")

# ============================================================ tamlik-denklikleri
CW2, CH2 = 460, 350
BW2, BH2, R2, CX2, CY2 = 110, 42, 140, 230, 184
p = Plot(0, 0, CW2, CH2, (0, 1), (0, 1))     # pixel canvas
NODES = {}
for key, ang, lines in ((1, -90, ("Tamlık", "Aksiyomu")), (2, -18, ("Monoton", "Yakınsaklık")),
                        (4, 54, ("Bolzano&#8211;", "Weierstrass")), (5, 126, ("Cauchy", "Tamlığı")),
                        (3, 198, ("İç İçe", "Aralıklar"))):
    a = math.radians(ang)
    NODES[key] = (CX2 + R2 * math.cos(a), CY2 + R2 * math.sin(a), lines)


def box_exit(src, dst, gap=4.0):
    """Point where the segment from box centre `src` toward `dst` leaves the box, pushed `gap` px outward."""
    dx, dy = dst[0] - src[0], dst[1] - src[1]
    t = min(BW2 / 2 / abs(dx) if dx else 1e9, BH2 / 2 / abs(dy) if dy else 1e9)
    length = math.hypot(dx, dy)
    return src[0] + dx * t + dx / length * gap, src[1] + dy * t + dy / length * gap


def node_arrow(p, i, j, dash=None):
    """Arrow from box i to box j, both ends on the box borders; returns its end points."""
    s = box_exit(NODES[i], NODES[j])
    e = box_exit(NODES[j], NODES[i])
    arrow_px(p, s[0], s[1], e[0], e[1], BASE, 1.5, 7, dash)
    return s, e


def along_label(p, s, e, text, side=1, at=0.5, gap=4.0, size=9.5, color=BASE):
    """Italic label rotated along the segment s-e; side=+1 puts it on the right-hand side of the
    reading direction (the direction with dx >= 0), side=-1 on the other side; `at` is the position along the segment."""
    dx, dy = e[0] - s[0], e[1] - s[1]
    if dx < 0 or (dx == 0 and dy < 0):
        s, e, dx, dy = e, s, -dx, -dy
    length = math.hypot(dx, dy)
    ux, uy = dx / length, dy / length
    nx, ny = -uy, ux                                   # unit normal on the right-hand side
    off = gap + 0.75 * size if side > 0 else -gap      # glyphs rise above the baseline, i.e. toward -n
    x, y = s[0] + ux * length * at + nx * off, s[1] + uy * length * at + ny * off
    ang = math.degrees(math.atan2(dy, dx))
    p.add(f'<text x="{x:.1f}" y="{y:.1f}" fill="{color}" font-size="{size}" text-anchor="middle" font-style="italic" '
          f'transform="rotate({ang:.1f} {x:.1f} {y:.1f})">{text}</text>')


for key, (cx, cy, lines) in NODES.items():
    rrect_px(p, cx - BW2 / 2, cy - BH2 / 2, BW2, BH2, THEORY, 0.08, 1.4, 8)
    p.add(f'<circle cx="{cx - BW2 / 2 + 15:.1f}" cy="{cy:.1f}" r="9" fill="{THEORY}"/>')
    p.text_px(cx - BW2 / 2 + 15, cy + 4, str(key), BG, 11, "middle", True)
    tx = cx + 12                                       # centre of the text column right of the badge
    p.text_px(tx, cy - 2, lines[0], THEORY, 11, "middle", True)
    p.text_px(tx, cy + 12, lines[1], THEORY, 11, "middle", True)
s12, e12 = node_arrow(p, 1, 2)
p.text_px((s12[0] + e12[0]) / 2 + 8, (s12[1] + e12[1]) / 2 - 6, "Monoton Yak. Teoremi", BASE, 9.5, "start", False, True)
s24, e24 = node_arrow(p, 2, 4)
p.text_px((s24[0] + e24[0]) / 2 + 9, (s24[1] + e24[1]) / 2 + 4, "Monoton alt dizi", BASE, 9.5, "start", False, True)
s45, e45 = node_arrow(p, 4, 5)
p.text_px((s45[0] + e45[0]) / 2, NODES[4][1] + BH2 / 2 + 15, "Cauchy ölçütü", BASE, 9.5, "middle", False, True)
s13, e13 = node_arrow(p, 1, 3)
p.text_px((s13[0] + e13[0]) / 2 - 8, (s13[1] + e13[1]) / 2 - 6, "Cantor", BASE, 9.5, "end", False, True)
s34, e34 = node_arrow(p, 3, 4)
along_label(p, s34, e34, "ikiye bölme", 1, 0.62)
s41, e41 = node_arrow(p, 4, 1)
along_label(p, s41, e41, "ikiye bölme + supremum", 1, 0.5)
s51, e51 = node_arrow(p, 5, 1, dash="5 4")
# both labels of the dashed arrow sit on its outer side, stacked, clear of the 3 -> 4 arrow that crosses it
along_label(p, s51, e51, "ikiye bölme + supremum", -1, 0.66, gap=4.0)
along_label(p, s51, e51, "Arşimet özelliği ile", -1, 0.66, gap=18.0)
OUT["tamlik-denklikleri"] = figure(
    CW2, CH2, [p],
    "Tamlık aksiyomunun beş eşdeğer biçimi. Her ok, kuyruğundaki özelliğin ucundakini gerektirdiğini ve ispatta "
    "kullanılan aracı gösterir: 1 &#8594; 2 &#8594; 4 &#8594; 5 zinciri ile 1 &#8594; 3 &#8594; 4 yolu düz oklarla, "
    "4'ten ve 5'ten 1'e dönüş ikiye bölme ve supremum ile kurulur. Cauchy tamlığından aksiyoma dönüş (kesikli ok) "
    "ayrıca Arşimet özelliğine ihtiyaç duyar.",
    aria="Tamlik aksiyomu, monoton yakinsaklik, ic ice araliklar, Bolzano-Weierstrass ve Cauchy tamliginin denklik semasi")

# ============================================================ isaret-fonksiyonu
p = Plot(46, 28, 310, 150, (-3.4, 3.4), (-1.55, 1.55))
p.origin_axes("x", "y", xticks=(-3, -2, -1, 1, 2, 3), yticks=(1,), xfmt=mfmt, yfmt=mfmt)
# the lower step covers the usual place of the "-1" tick label, so that one goes to the right of the axis
p.add(f'<line x1="{p.X(0)-3:.1f}" y1="{p.Y(-1):.1f}" x2="{p.X(0)+3:.1f}" y2="{p.Y(-1):.1f}" stroke="{TEXT}" stroke-width="1" opacity="0.7"/>')
p.add(f'<text x="{p.X(0)+10:.1f}" y="{p.Y(-1)+4:.1f}" fill="{TEXT}" font-size="11" opacity="0.7">{MINUS}1</text>')
p.line([(0, 1), (3.25, 1)], THEORY, 2.2)
p.line([(-3.25, -1), (0, -1)], THEORY, 2.2)
hollow(p, (0, 1), THEORY, 4.0, 1.6)
hollow(p, (0, -1), THEORY, 4.0, 1.6)
dot(p, (0, 0), THEORY, 4.0)
p.label(2.0, 1, "y = sgn(x)", 0, -10, THEORY, 12, "middle", True, True)
OUT["isaret-fonksiyonu"] = figure(
    400, 200, [p],
    "İşaret fonksiyonu: pozitif <em>x</em>'lerde 1, negatif <em>x</em>'lerde &#8722;1, sıfırda 0. Grafik 0'da iki "
    "düzeye ayrılır; sağ limit 1, sol limit &#8722;1 olduğundan <em>x</em> &#8594; 0 iken limit yoktur ve fonksiyon 0'da "
    "süreksizdir.",
    aria="Isaret fonksiyonu sgn(x) grafigi: sagda 1, solda -1, orijinde 0")

# ============================================================ sonsuz-limit-m-delta
M4, D4 = 4.0, 0.5                            # delta = 1 / sqrt(M)
p = Plot(50, 24, 300, 226, (-2.2, 2.2), (-0.7, 10.7))
X_TOP = 1 / math.sqrt(p.ymax)                # where the graph leaves the panel at the top
band(p, -D4, D4, 0, p.ymax, PRACTICE, 0.12)
band(p, p.xmin, p.xmax, M4, p.ymax, THEORY, 0.08)
p.origin_axes("x", "y", xticks=(-2, -1, 1, 2), xfmt=mfmt)
hline(p, M4, THEORY, 1.2, "5 4", 0.85)
guide(p, [(-D4, 0), (-D4, p.ymax)], PRACTICE, 0.55)
guide(p, [(D4, 0), (D4, p.ymax)], PRACTICE, 0.55)
curve(p, lambda x: 1 / (x * x), -2.2, -X_TOP, THEORY, 1.9, 200)
curve(p, lambda x: 1 / (x * x), X_TOP, 2.2, THEORY, 1.9, 200)
curve(p, lambda x: 1 / (x * x), -D4, -X_TOP, PRACTICE, 2.8, 100)   # the pieces over the window
curve(p, lambda x: 1 / (x * x), X_TOP, D4, PRACTICE, 2.8, 100)
p.points([(-D4, M4), (D4, M4)], THEORY, 3.4)
hollow(p, (0, 0), PRACTICE, 4.0, 1.6)
p.label(0, M4, "M", -7, 4, THEORY, 11.5, "end", True, True)
p.label(p.xmax, M4, "y = M", -4, -5, THEORY, 10.5, "end", False, True)
p.label(-D4, 0, MINUS + DELTA, 0, 15, PRACTICE, 11, "middle", False, True)
p.label(D4, 0, DELTA, 0, 15, PRACTICE, 11, "middle", False, True)
p.label(1.3, 1 / 1.69, "y = 1/x" + sup("2"), 8, -4, THEORY, 12, "start", True, True)
p.label(p.xmax, 10.2, "0 &lt; |x| &lt; " + DELTA + " " + IMPLIES + " f(x) &gt; M", -4, 0, PRACTICE, 10.5, "end", False, True)
OUT["sonsuz-limit-m-delta"] = figure(
    400, 270, [p],
    "<em>x</em> &#8594; 0 iken 1/<em>x</em><sup>2</sup> &#8594; +&#8734;: hangi <em>M</em> verilirse verilsin, "
    "&#948; = 1/&#8730;<em>M</em> alınınca 0 &lt; |<em>x</em>| &lt; &#948; penceresindeki her <em>x</em> için "
    "<em>f</em>(<em>x</em>) &gt; <em>M</em> olur. Şekilde <em>M</em> = 4 ve &#948; = 0,5; pencere içindeki grafik "
    "parçası tümüyle <em>y</em> = <em>M</em> çizgisinin üstündedir. <em>M</em> büyüdükçe pencere daralır.",
    aria="Sonsuz limit tanimi: M cizgisi ve delta penceresi, 1/x kare pencerede M'nin ustunde")

# ============================================================ sonsuzda-limit-epsilon-k
E5, K5 = 0.2, 5.0                            # K = 1 / epsilon
p = Plot(50, 26, 320, 190, (0, 10.8), (-0.5, 2.25))
band(p, K5, p.xmax, p.ymin, p.ymax, PRACTICE, 0.08)
hband(p, -E5, E5, THEORY, 0.14)
p.origin_axes("x", "y", xticks=(2, 4, 6, 8, 10), yticks=(1, 2))
guide(p, [(0, E5), (p.xmax, E5)], THEORY, 0.55)
guide(p, [(0, -E5), (p.xmax, -E5)], THEORY, 0.55)
p.vline(K5, p.ymin, p.ymax, PRACTICE, "4 3", 0.8)
curve(p, lambda x: 1 / x, 0.5, K5, THEORY, 1.9, 200)
curve(p, lambda x: 1 / x, K5, p.xmax, PRACTICE, 2.6, 100)         # the tail inside the band
dot(p, (K5, 1 / K5), PRACTICE, 3.6)
p.label(0, E5, EPS, -7, 4, THEORY, 11, "end", False, True)
p.label(0, -E5, MINUS + EPS, -7, 4, THEORY, 11, "end", False, True)
p.label(K5, p.ymin, "K = 1/" + EPS, 0, 12, PRACTICE, 11, "middle", True, True)
p.label(1.0, 1.0, "y = 1/x", 8, -4, THEORY, 12, "start", True, True)
p.label(p.xmax, 2.05, "x &gt; K " + IMPLIES + " |f(x) " + MINUS + " 0| &lt; " + EPS, -4, 0, PRACTICE, 10.5, "end", False, True)
OUT["sonsuzda-limit-epsilon-k"] = figure(
    400, 244, [p],
    "<em>x</em> &#8594; +&#8734; iken 1/<em>x</em> &#8594; 0: verilen &#949; için <em>K</em> = 1/&#949; alınınca "
    "<em>x</em> &gt; <em>K</em> olan her <em>x</em>'te |<em>f</em>(<em>x</em>) &#8722; 0| &lt; &#949; olur. Şekilde "
    "&#949; = 0,2 ve <em>K</em> = 5; <em>K</em>'nın sağındaki grafik parçası (&#8722;&#949;, &#949;) bandının içinde "
    "kalır, solundaki parça bandın üstündedir. Daha küçük &#949; daha büyük <em>K</em> ister.",
    aria="Sonsuzda limit tanimi: epsilon bandi ve K esigi, 1/x K'nin sagindan itibaren bandin icinde")

# ============================================================ monoton-tek-yonlu-limit
A6, EPS6, X06 = 2.0, 0.6, 1.4                # x0 = a - delta
LM6, LP6, FA6 = 1.5, 2.5, 2.0                # f(a-), f(a+), f(a)


def h_left(x):
    return x / 2 + 0.5


def h_right(x):
    return x / 2 + 1.5


p = Plot(86, 24, 270, 236, (-0.3, 4.4), (-0.3, 3.9))
band(p, X06, A6, 0, p.ymax, BASE, 0.12)                    # the window (a - delta, a)
band(p, 0, A6, LM6 - EPS6, LM6, BASE, 0.12)                # the strip (f(a-) - eps, f(a-))
p.origin_axes("x", "y")
guide(p, [(0, LM6), (A6, LM6)], THEORY, 0.55)
guide(p, [(0, LP6), (A6, LP6)], PRACTICE, 0.55)
guide(p, [(0, FA6), (A6, FA6)], TEXT, 0.45)
guide(p, [(A6, 0), (A6, LP6)], TEXT, 0.45)
guide(p, [(0, LM6 - EPS6), (A6, LM6 - EPS6)], BASE, 0.55)
guide(p, [(X06, 0), (X06, h_left(X06)), (0, h_left(X06))], BASE, 0.55)
# value sets on the y axis: [f(0), f(a-)) on the left, (f(a+), f(4)] on the right
p.line([(0, h_left(0)), (0, LM6)], THEORY, 5, opacity=0.5)
p.line([(0, LP6), (0, h_right(4))], PRACTICE, 5, opacity=0.5)
dot(p, (0, h_left(0)), THEORY, 3.6)
dot(p, (0, h_right(4)), PRACTICE, 3.6)
hollow(p, (0, LM6), THEORY, 4.0, 1.6)
hollow(p, (0, LP6), PRACTICE, 4.0, 1.6)
dot(p, (0, FA6), TEXT, 3.6)
dot(p, (0, h_left(X06)), BASE, 3.4)
curve(p, h_left, 0, A6, THEORY, 2.0)
curve(p, h_right, A6, 4, PRACTICE, 2.0)
curve(p, h_left, X06, A6, BASE, 2.8)                       # the piece of the graph over the window
hollow(p, (A6, LM6), THEORY, 4.2, 1.8)
hollow(p, (A6, LP6), PRACTICE, 4.2, 1.8)
dot(p, (A6, FA6), TEXT, 4.2)
dot(p, (X06, h_left(X06)), BASE, 3.8)
p.label(0, LM6, "sup = f(a" + SUP_MINUS + ")", -7, 4, THEORY, 10.5, "end", False, True)
p.label(0, LP6, "inf = f(a" + SUP_PLUS + ")", -7, 4, PRACTICE, 10.5, "end", False, True)
p.label(0, FA6, "f(a)", -7, 4, TEXT, 10.5, "end", False, True)
p.label(0, LM6 - EPS6, "f(a" + SUP_MINUS + ") " + MINUS + " " + EPS, -7, 4, BASE, 10.5, "end", False, True)
p.label(0, h_left(X06), "f(x" + SUB_0 + ")", -7, 4, BASE, 10.5, "end", False, True)
p.label(A6, 0, "a", 0, 15, TEXT, 11.5, "middle", True, True)
p.label(X06, 0, "x" + SUB_0 + " = a " + MINUS + " " + DELTA, 6, 15, BASE, 10.5, "end", False, True)
p.label(3.4, h_right(3.4), "y = f(x)", 6, 22, TEXT, 12, "middle", True, True)
p.label(2.3, 1.75, "f(x" + SUB_0 + ") &gt; f(a" + SUP_MINUS + ") " + MINUS + " " + EPS, 0, 0, BASE, 10.5, "start", True)
p.label(2.3, 1.45, "x" + SUB_0 + " &lt; x &lt; a " + IMPLIES, 0, 0, BASE, 10, "start", False, True)
p.label(2.3, 1.18, "f(a" + SUP_MINUS + ") " + MINUS + " " + EPS + " &lt; f(x) &lt; f(a" + SUP_MINUS + ")", 0, 0, BASE, 10, "start", False, True)
OUT["monoton-tek-yonlu-limit"] = figure(
    400, 280, [p],
    "Artan <em>f</em> için <em>a</em>'nın solundaki değerlerin kümesi (<em>y</em> ekseninde koyu çizili) üstten "
    "sınırlıdır; supremumu <em>f</em>(<em>a</em><sup>&#8722;</sup>) sol limittir. Supremum tanımı gereği "
    "<em>f</em>(<em>a</em><sup>&#8722;</sup>) &#8722; &#949;'u aşan bir <em>f</em>(<em>x</em><sub>0</sub>) vardır; "
    "<em>x</em><sub>0</sub> &lt; <em>x</em> &lt; <em>a</em> için artanlık <em>f</em>(<em>x</em>)'i "
    "<em>f</em>(<em>x</em><sub>0</sub>) ile <em>f</em>(<em>a</em><sup>&#8722;</sup>) arasında tutar. Sağdaki değerlerin "
    "infimumu <em>f</em>(<em>a</em><sup>+</sup>) sağ limittir; <em>f</em>(<em>a</em>) ikisinin arasında kalır.",
    aria="Artan fonksiyonda sol limit sol degerlerin supremumu, sag limit sag degerlerin infimumu; f(a) arada")


# ---------------------------------------------------------------------------
for name, content in OUT.items():
    with io.open(os.path.join(OUT_DIR, "analysis-%s.md" % name), "w", encoding="utf-8") as f:
        f.write(content)
print("generated:", ", ".join(OUT))
