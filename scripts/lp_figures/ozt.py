# -*- coding: utf-8 -*-
"""
Figures of the page "Uygulamalı Özet"
(dersler/lineer-programlama/uygulamali-ozet.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box: a figure that illustrates a
definition sits directly below that box. The figures are NOT produced at
build time. Run

    python scripts/lp_figures/ozt.py
    python scripts/center_figures.py "lp-ozt-*.md" --keep-width
    python scripts/check_figure_labels.py "scripts/_figures/lp-ozt-*.md"

and paste the markup of scripts/_figures/lp-ozt-<name>.md into the .qmd.
Captions are Turkish (they are shown on the site); aria labels are ASCII.

The page shows the rectangle rule A* = A - B*C/P of the simplex tableau:
one generic picture and two "maps" of a real tableau that colour every cell
by the work it needs (divide by the pivot, unit column, copy thanks to a
zero, rectangle rule).
"""
import sys
from fractions import Fraction as F
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, WIDE, TEXT, BG, THEORY, PRACTICE, BASE, REMARK  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "lp-ozt-"

MINUS = "&#8722;"
ARROW = "&#8594;"


def save(name, markup):
    (OUT_DIR / f"{PREFIX}{name}.md").write_text(markup, encoding="utf-8", newline="\n")
    print("wrote", PREFIX + name)


def canvas(W, H):
    """A panel whose data coordinates are plain pixels (y grows downward)."""
    return Plot(0, 0, W, H, (0, W), (H, 0))


def sub(base, s, size=10):
    """Subscript inside an SVG <text> without a special glyph."""
    return (f'{base}<tspan font-size="{size}" dy="3">{s}</tspan>'
            f'<tspan dy="-3">&#8203;</tspan>')


def num(q):
    """Fraction -> '5/2', '&#8722;1/3', '12'."""
    q = F(q)
    sign = MINUS if q < 0 else ""
    q = abs(q)
    body = str(q.numerator) if q.denominator == 1 else f"{q.numerator}/{q.denominator}"
    return sign + body


def cell(p, x, y, w, h, fill=None, opacity=0.0, stroke=TEXT, stroke_op=0.35, width=1.0):
    f = f'fill="{fill}" fill-opacity="{opacity}"' if fill else 'fill="none"'
    p.add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" {f} '
          f'stroke="{stroke}" stroke-opacity="{stroke_op}" stroke-width="{width}"/>')


def dashed_rect(p, x0, y0, x1, y1, color, dash="6 4", width=2.0):
    p.add(f'<rect x="{min(x0, x1):.1f}" y="{min(y0, y1):.1f}" width="{abs(x1 - x0):.1f}" '
          f'height="{abs(y1 - y0):.1f}" fill="none" stroke="{color}" stroke-width="{width}" '
          f'stroke-dasharray="{dash}" rx="3"/>')


def halo_text(p, x, y, s, size=12, bold=False):
    """Text with a page-coloured outline, so dashed guides run behind it."""
    weight = ' font-weight="600"' if bold else ""
    p.add(f'<text x="{x:.1f}" y="{y:.1f}" fill="{TEXT}" font-size="{size}" text-anchor="middle"{weight} '
          f'stroke="{BG}" stroke-width="3" stroke-opacity="0.9" paint-order="stroke">{s}</text>')


def swatch(p, x, y, color, opacity, text):
    cell(p, x, y - 12, 16, 16, fill=color, opacity=opacity, stroke=color, stroke_op=0.9)
    p.text_px(x + 24, y + 2, text, size=14)


# ============================================================
# The generic rectangle rule
# ============================================================
def rectangle_rule():
    W, H = 520, 330
    p = canvas(W, H)
    gx, gy, cw, ch = 150, 50, 62, 42
    ncol, nrow = 5, 4
    pr, pc = 1, 1          # pivot cell
    ar, ac = 3, 4          # the element A being updated

    # pivot row and pivot column bands
    for c in range(ncol):
        cell(p, gx + c * cw, gy + pr * ch, cw, ch, fill=THEORY, opacity=0.10, stroke_op=0)
    for r in range(nrow):
        cell(p, gx + pc * cw, gy + r * ch, cw, ch, fill=BASE, opacity=0.10, stroke_op=0)
    for r in range(nrow):
        for c in range(ncol):
            cell(p, gx + c * cw, gy + r * ch, cw, ch)

    def centre(r, c):
        return gx + c * cw + cw / 2, gy + r * ch + ch / 2

    special = {
        (pr, pc): ("P", THEORY, 0.40),
        (ar, ac): ("A", PRACTICE, 0.30),
        (ar, pc): ("B", REMARK, 0.28),
        (pr, ac): ("C", REMARK, 0.28),
    }
    for (r, c), (s, color, op) in special.items():
        cell(p, gx + c * cw, gy + r * ch, cw, ch, fill=color, opacity=op, stroke=color, stroke_op=0.9, width=1.4)

    # the rectangle through the four centres, drawn behind the letters
    (x0, y0), (x1, y1) = centre(pr, pc), centre(ar, ac)
    dashed_rect(p, x0, y0, x1, y1, REMARK)
    for (r, c), (s, _, _) in special.items():
        x, y = centre(r, c)
        halo_text(p, x, y + 6, s, size=17, bold=True)

    # band labels
    p.text_px(gx - 12, gy + pr * ch + ch / 2 + 4, "pivot satırı", color=THEORY, size=12, anchor="end", bold=True)
    p.text_px(gx + pc * cw + cw / 2, gy - 14, "pivot sütunu", color=BASE, size=12, anchor="middle", bold=True)
    p.text_px(gx - 12, gy + ar * ch + ch / 2 + 4, "A'nın satırı", size=12, anchor="end")
    p.text_px(gx + ac * cw + cw / 2, gy - 14, "A'nın sütunu", size=12, anchor="middle")

    # the formula
    fy = gy + nrow * ch + 40
    p.text_px(gx + ncol * cw / 2, fy, "A* = A " + MINUS + " (B · C) / P", size=17, anchor="middle", bold=True)
    p.text_px(gx + ncol * cw / 2, fy + 26, "yeni = eski " + MINUS + " çapraz köşelerin çarpımı / pivot",
              size=12, anchor="middle")
    return figure(W, H, [p],
                  "Dikdörtgen kuralı. Güncellenecek A elemanı ile pivot P bir dikdörtgenin karşılıklı "
                  "köşeleridir. Öbür iki köşe B (A'nın satırı ile pivot sütununun kesişimi) ve C "
                  "(A'nın sütunu ile pivot satırının kesişimi) olur. Yeni değer A − BC/P'dir.",
                  aria="Grid with pivot P, element A at the opposite corner of a dashed rectangle, "
                       "B in the row of A and the pivot column, C in the column of A and the pivot row; "
                       "formula A star equals A minus B times C over P")


# ============================================================
# Map of one simplex iteration
# ============================================================
COLS = ["v₀", "v₁", "v₂", "v₃", "v₄", "v₅"]


def pivot(vals, zrow, r, k):
    """New body and z row after pivoting on vals[r][k] (the tableau rule)."""
    prow = [x / vals[r][k] for x in vals[r]]
    out = [prow if i == r else [a - row[k] * c for a, c in zip(row, prow)]
           for i, row in enumerate(vals)]
    znew = [a - zrow[k] * c for a, c in zip(zrow, prow)]
    return out, znew


def tableau_map(cj, rows, cb, zrow, r, k, rects, caption, aria):
    """rows: list of (name, values v0..v5); r, k: pivot row and column index."""
    vals = [[F(x) for x in v] for _, v in rows]
    z = [F(x) for x in zrow]
    newvals, newz = pivot(vals, z, r, k)
    P = vals[r][k]

    nb = len(rows)
    W = 680
    x0, y0 = 20, 40
    wn, wc, wv = 84, 52, 84          # widths: x_B, c_B, value columns
    hh = 38                          # row height
    colx = [x0, x0 + wn] + [x0 + wn + wc + i * wv for i in range(6)]
    widths = [wn, wc] + [wv] * 6
    H = y0 + (nb + 3) * hh + 100
    p = canvas(W, H)

    def cx(j):
        return colx[j] + widths[j] / 2

    def ry(i):                       # i = 0: c_j row, 1: names, 2..: body, last: z row
        return y0 + i * hh

    # header rows
    p.text_px(cx(2), ry(0) + 25, sub("c", "j"), size=15, anchor="middle", bold=True)
    for j, c in enumerate(cj):
        p.text_px(cx(3 + j), ry(0) + 25, num(c), size=15, anchor="middle")
    for j, s in enumerate([sub("x", "B"), sub("c", "B")] + COLS):
        p.text_px(cx(j), ry(1) + 25, s, size=15, anchor="middle", bold=True)

    # category of every numeric cell
    texts = []                       # drawn last, above the dashed guides
    body = [(i, vals[i]) for i in range(nb)] + [(nb, z)]
    newbody = newvals + [newz]
    prow = vals[r]
    pcol = [vals[i][k] for i in range(nb)] + [z[k]]
    for i, v in body:
        yy = ry(2 + i)
        for j in range(6):
            if i == r and j == k:
                kind = "pivot"
            elif i == r:
                kind = "row"
            elif j == k:
                kind = "col"
            elif pcol[i] == 0 or prow[j] == 0:
                kind = "copy"
            else:
                kind = "rect"
            fill, op = {"pivot": (THEORY, 0.45), "row": (THEORY, 0.14), "col": (BASE, 0.16),
                        "copy": (TEXT, 0.0), "rect": (PRACTICE, 0.20)}[kind]
            cell(p, colx[2 + j], yy, wv, hh, fill=fill, opacity=op)
            old, new = v[j], newbody[i][j]
            if kind == "pivot":
                texts.append((cx(2 + j), yy + 25, f"[{num(old)}]", 15.5, True))
            elif kind == "rect":
                texts.append((cx(2 + j), yy + 25, f"{num(old)} {ARROW} {num(new)}", 14, False))
            else:
                texts.append((cx(2 + j), yy + 25, num(old), 15, False))
        # x_B and c_B cells
        name = rows[i][0] if i < nb else None
        cell(p, colx[0], yy, wn, hh)
        cell(p, colx[1], yy, wc, hh)
        if name:
            p.text_px(cx(0), yy + 25, name, size=15, anchor="middle")
            p.text_px(cx(1), yy + 25, num(cb[i]), size=15, anchor="middle")
        else:
            p.text_px(cx(0), yy + 25,
                      sub("z", "j") + " " + MINUS + " " + sub("c", "j"), size=14, anchor="middle")
    # thick rules as in the book's tables
    p.add(f'<line x1="{x0}" y1="{ry(2)}" x2="{colx[-1] + wv}" y2="{ry(2)}" stroke="{TEXT}" stroke-width="1.8" opacity="0.8"/>')
    p.add(f'<line x1="{x0}" y1="{ry(2 + nb)}" x2="{colx[-1] + wv}" y2="{ry(2 + nb)}" stroke="{TEXT}" stroke-width="1.8" opacity="0.8"/>')
    p.add(f'<line x1="{colx[2]}" y1="{ry(0)}" x2="{colx[2]}" y2="{ry(3 + nb)}" stroke="{TEXT}" stroke-width="1.8" opacity="0.8"/>')

    # rectangles of the chosen example cells
    def centre(i, j):
        return cx(2 + j), ry(2 + i) + hh / 2

    for (i, j), color in rects:
        (ax, ay), (px_, py_) = centre(i, j), centre(r, k)
        dashed_rect(p, ax, ay, px_, py_, color, width=2.2)
    for x, y, s, size, bold in texts:
        halo_text(p, x, y, s, size=size, bold=bold)

    # legend
    ly = ry(3 + nb) + 32
    swatch(p, x0 + 6, ly, THEORY, 0.30, f"pivot satırı: {num(P)}'ye bölünür")
    swatch(p, x0 + 330, ly, BASE, 0.30, "pivot sütunu: 1 ve 0'lar")
    swatch(p, x0 + 6, ly + 30, TEXT, 0.0, "0 kısayolu: aynen kalır")
    swatch(p, x0 + 330, ly + 30, PRACTICE, 0.35, "dikdörtgen kuralı: eski " + ARROW + " yeni")
    return figure(W, H, [p], caption, css_class=WIDE, aria=aria)


def first_iteration():
    rows = [("x₃", [4, 1, 0, 1, 0, 0]), ("x₄", [12, 0, 2, 0, 1, 0]), ("x₅", [18, 3, 2, 0, 0, 1])]
    return tableau_map(
        [3, 5, 0, 0, 0], rows, [0, 0, 0], [0, -3, -5, 0, 0, 0], 1, 2,
        [((2, 0), REMARK), ((3, 4), PRACTICE)],
        "Birinci iterasyonun haritası. Pivot 2'dir. Pivot sütununda 0 olan x₃ satırı ile pivot "
        "satırında 0 olan v₁, v₃, v₅ sütunları aynen kalır. Dikdörtgen kuralı yalnız dört hücreye "
        "uygulanır. Kesikli dikdörtgenler iki örneği gösteriyor: 18 − 2·12/2 = 6 ve "
        "0 − (−5)·1/2 = 5/2.",
        "Initial tableau of max 3x1+5x2 coloured by the work each cell needs: pivot 2 in row x4 "
        "column v2, row x3 and columns v1 v3 v5 are copied, four cells use the rectangle rule")


def second_iteration():
    rows = [("x₃", [4, 1, 0, 1, 0, 0]), ("x₂", [6, 0, 1, 0, F(1, 2), 0]), ("x₅", [6, 3, 0, 0, -1, 1])]
    return tableau_map(
        [3, 5, 0, 0, 0], rows, [0, 5, 0], [30, -3, 0, 0, F(5, 2), 0], 2, 1,
        [((0, 0), REMARK), ((3, 4), PRACTICE)],
        "İkinci iterasyonun haritası. Pivot 3'tür. Pivot sütununda 0 olan x₂ satırı ile pivot "
        "satırında 0 olan v₂, v₃ sütunları aynen kalır ve altı hücre dikdörtgen kuralıyla bulunur. "
        "İki örnek: 4 − 1·6/3 = 2 ve 5/2 − (−3)(−1)/3 = 3/2.",
        "First iteration tableau coloured by the work each cell needs: pivot 3 in row x5 column v1, "
        "row x2 and columns v2 v3 are copied, six cells use the rectangle rule")


# ============================================================
# Graphic method: candidate corners of max 2x1 + 3x2
# ============================================================
def graphic_candidates():
    xr, yr = (-0.4, 7.2), (-0.4, 5.0)
    W0 = 470
    H0 = W0 * (yr[1] - yr[0]) / (xr[1] - xr[0])
    p = Plot(60, 30, W0, H0, xr, yr)
    p.grid(xs=range(1, 8), ys=range(1, 5))
    corners = [(0, 0), (4, 0), (3, 1), (0, 2)]
    p.polygon(corners, fill=THEORY, opacity=0.18, stroke=THEORY, width=1.2)
    # constraint lines x1 + x2 = 4 and x1 + 3x2 = 6
    p.line([(-0.3, 4.3), (4.4, -0.4)], color=REMARK, width=1.5, opacity=0.8)
    p.line([(-0.3, 2.1), (7.2, -0.4)], color=REMARK, width=1.5, opacity=0.8)
    # level line 2x1 + 3x2 = 9 and the gradient
    p.line([(-0.3, 3.2), (4.8, -0.2)], color=BASE, width=1.4, dash="6 4", opacity=0.9)
    p.arrow((4.4, 2.4), (5.2, 3.6), color=BASE, width=1.6, head=8)
    p.label(5.2, 3.6, "c = (2, 3)", dx=8, dy=4, color=BASE, size=12)
    p.origin_axes(xlabel="x₁", ylabel="x₂", xticks=range(1, 7), yticks=range(1, 5))
    # candidates (filled) and the two infeasible intersections (hollow)
    p.points(corners, color=PRACTICE, r=4.2)
    p.hollow_points([(6, 0), (0, 4)], color=TEXT, r=4.0)
    p.label(0, 0, "O: z = 0", dx=8, dy=-8, size=12)
    p.label(4, 0, "A: z = 8", dx=-10, dy=-9, size=12, anchor="end")
    p.label(3, 1, "B: z = 9", dx=8, dy=-6, size=12, bold=True)
    p.label(0, 2, "C: z = 6", dx=8, dy=-8, size=12)
    p.label(6, 0, "(6, 0) uygun değil", dx=-6, dy=-12, size=11, anchor="middle")
    p.label(0, 4, "(0, 4) uygun değil", dx=10, dy=4, size=11)
    p.label(4.4, 0.9, "z = 9", dx=0, dy=-14, color=BASE, size=12)
    p.label(1.7, 2.7, "x₁ + x₂ = 4", dx=6, dy=0, color=REMARK, size=11.5)
    p.label(5.5, 0.5, "x₁ + 3x₂ = 6", dx=4, dy=-8, color=REMARK, size=11.5)
    return figure(560, H0 + 70, [p],
                  "Grafik yöntem. Uygun bölge OABC dörtgenidir ve aday noktalar dört köşedir. "
                  "Köşelerdeki z değerleri 0, 8, 9, 6 olduğundan optimum B(3, 1)'de, z = 9'dur. "
                  "Kesikli seviye doğrusu 2x₁ + 3x₂ = 9 bölgeye yalnız B'de değer. İçi boş iki "
                  "nokta kısıt doğrularının bölge dışındaki kesişimleridir; bunlar uygun olmayan "
                  "temel çözümlerdir.",
                  aria="Feasible quadrilateral with corners O(0,0), A(4,0), B(3,1), C(0,2) labelled "
                       "with z values 0, 8, 9, 6; dashed level line z = 9 through B; hollow points "
                       "(6,0) and (0,4) outside the region; gradient arrow (2,3)")


if __name__ == "__main__":
    save("grafik", graphic_candidates())
    save("dikdortgen", rectangle_rule())
    save("harita-1", first_iteration())
    save("harita-2", second_iteration())
