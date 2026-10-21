# -*- coding: utf-8 -*-
"""
Figures of the chapter "Küme Cebiri, Görüntüler ve Tümevarım Üzerine Problemler"
(dersler/analiz-1/problemler-karisik.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box and never directly under a heading.
The figures are NOT produced at build time. Run

    python scripts/analysis1_problem_figures/ps6.py
    python scripts/center_figures.py "analysis1-ps6-*.md"
    python scripts/check_figure_labels.py "scripts/_figures/analysis1-ps6-*.md"

and paste the markup of scripts/_figures/analysis1-ps6-<name>.md into the .qmd.
The captions are Turkish on purpose; the aria labels are plain ASCII.
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, BASE, BG, PRACTICE, TEXT, THEORY  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "analysis1-ps6-"


def save(name, svg):
    (OUT_DIR / f"{PREFIX}{name}.md").write_text(svg, encoding="utf-8", newline="\n")
    print(f"{PREFIX}{name}.md")


def it(s):
    """Italic math letter inside an SVG <text>."""
    return f'<tspan font-style="italic">{s}</tspan>'


def subs(s, size=9):
    """Subscript inside an SVG <text>."""
    return f'<tspan font-size="{size}" dy="4">{s}</tspan><tspan dy="-4">&#8203;</tspan>'


def head_px(p, x1, y1, ux, uy, color, head=7.0):
    px, py = -uy, ux
    hw = head * 0.42
    p.add(f'<polygon points="{x1:.1f},{y1:.1f} {x1-ux*head+px*hw:.1f},{y1-uy*head+py*hw:.1f} '
          f'{x1-ux*head-px*hw:.1f},{y1-uy*head-py*hw:.1f}" fill="{color}"/>')


def arrow_between_px(p, a, b, color=THEORY, width=1.6, gap=12.0, head=7.0):
    """Arrow from pixel point a to pixel point b, both ends pulled back by `gap` pixels."""
    length = math.hypot(b[0] - a[0], b[1] - a[1]) or 1.0
    ux, uy = (b[0] - a[0]) / length, (b[1] - a[1]) / length
    x0, y0 = a[0] + ux * gap, a[1] + uy * gap
    x1, y1 = b[0] - ux * gap, b[1] - uy * gap
    sx, sy = x1 - ux * head * 0.8, y1 - uy * head * 0.8
    p.add(f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{sx:.1f}" y2="{sy:.1f}" stroke="{color}" '
          f'stroke-width="{width}" stroke-linecap="round"/>')
    head_px(p, x1, y1, ux, uy, color, head)


# ============================================================
# ayrik-kumeler: A subset of the complement of B means A and B are disjoint
# ============================================================
p = Plot(20, 20, 350, 200, (-3.5, 3.5), (-2.0, 2.0))     # 50 px per unit on both axes
x0, y0, x1, y1 = p.X(-3.5), p.Y(2.0), p.X(3.5), p.Y(-2.0)
bx, by, br = p.X(1.45), p.Y(-0.05), p.R(1.15)
# complement of B inside X: the rectangle with the disk of B cut out (even-odd fill)
p.add(f'<path d="M{x0:.1f},{y0:.1f} L{x1:.1f},{y0:.1f} L{x1:.1f},{y1:.1f} L{x0:.1f},{y1:.1f} Z '
      f'M{bx + br:.1f},{by:.1f} A{br:.1f},{br:.1f} 0 1 0 {bx - br:.1f},{by:.1f} '
      f'A{br:.1f},{br:.1f} 0 1 0 {bx + br:.1f},{by:.1f} Z" fill="{BASE}" fill-opacity="0.13" '
      f'fill-rule="evenodd" stroke="none"/>')
p.add(f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{x1 - x0:.1f}" height="{y1 - y0:.1f}" fill="none" '
      f'stroke="{TEXT}" stroke-width="1.2" opacity="0.6"/>')
p.add(f'<circle cx="{p.X(-1.45):.1f}" cy="{p.Y(-0.05):.1f}" r="{p.R(1.15):.1f}" fill="{THEORY}" '
      f'fill-opacity="0.16" stroke="none"/>')
p.circle(-1.45, -0.05, 1.15, THEORY, 1.7)
p.circle(1.45, -0.05, 1.15, PRACTICE, 1.7)
p.label(-1.45, -0.05, it("A"), 0, 5, THEORY, 14, "middle", True)
p.label(1.45, -0.05, it("B"), 0, 5, PRACTICE, 14, "middle", True)
p.label(-3.5, 2.0, it("X"), 10, 18, TEXT, 13, "start", True)
p.label(0.0, 1.55, "gölgeli bölge: " + it("B") + " dışı", 0, 4, BASE, 11.5, "middle")
save("ayrik-kumeler", figure(
    390, 240, [p],
    "Gölgeli bölge, <em>B</em>'nin <em>X</em>'e göre tümleyenidir. <em>A</em> ile <em>B</em> ayrık olduğu için "
    "<em>A</em> tamamen bu bölgenin içinde kalır; aynı nedenle <em>B</em> de <em>A</em>'nın tümleyeninin içindedir. "
    "İki kapsamanın da söylediği tek şey, <em>A</em> ile <em>B</em>'nin ortak elemanı olmamasıdır.",
    aria="Venn diagram: two disjoint discs A and B inside a rectangle X, the region outside B shaded, "
         "disc A lying entirely in the shaded region"))


# ============================================================
# fark-goruntusu: f(1) = f(2) = u, f(3) = v; A1 = {1, 3}, A2 = {2}
# ============================================================
p = Plot(0, 0, 380, 230, (0, 1), (0, 1))
XC, YC = 95.0, 285.0
X_POS = {1: 62.0, 3: 112.0, 2: 178.0}
Y_POS = {"u": 92.0, "v": 152.0}
p.add(f'<ellipse cx="{XC:.1f}" cy="120.0" rx="44.0" ry="98.0" fill="none" stroke="{TEXT}" '
      f'stroke-width="1.1" opacity="0.45"/>')
p.add(f'<ellipse cx="{YC:.1f}" cy="122.0" rx="38.0" ry="66.0" fill="none" stroke="{TEXT}" '
      f'stroke-width="1.1" opacity="0.45"/>')
# A1 = {1, 3} and A2 = {2} as rounded boxes inside X
p.add(f'<rect x="{XC - 24:.1f}" y="44.0" width="48.0" height="86.0" rx="14" fill="{THEORY}" fill-opacity="0.12" '
      f'stroke="{THEORY}" stroke-width="1.3"/>')
p.add(f'<rect x="{XC - 24:.1f}" y="158.0" width="48.0" height="38.0" rx="14" fill="{PRACTICE}" fill-opacity="0.12" '
      f'stroke="{PRACTICE}" stroke-width="1.3"/>')
p.text_px(XC - 50, 92.0, it("A") + subs("1"), THEORY, 13, "end", True)
p.text_px(XC - 50, 182.0, it("A") + subs("2"), PRACTICE, 13, "end", True)
p.text_px(XC, 14.0, it("X"), TEXT, 13, "middle", True)
p.text_px(YC, 46.0, it("Y"), TEXT, 13, "middle", True)
for a, b, col in ((1, "u", THEORY), (3, "v", THEORY), (2, "u", PRACTICE)):
    arrow_between_px(p, (XC, X_POS[a]), (YC, Y_POS[b]), col, 1.6, 12.0)
for a, ypx in X_POS.items():
    p.text_px(XC, ypx + 4.5, str(a), TEXT, 13, "middle")
for b, ypx in Y_POS.items():
    p.text_px(YC, ypx + 4.5, it(b), TEXT, 13, "middle")
p.text_px((XC + YC) / 2, 24.0, it("f"), TEXT, 13, "middle", True)
save("fark-goruntusu", figure(
    380, 230, [p],
    "<em>f</em>(1) = <em>f</em>(2) = <em>u</em> ve <em>f</em>(3) = <em>v</em>. <em>A</em><sub>1</sub> = {1, 3}, "
    "<em>A</em><sub>2</sub> = {2} için <em>f</em>(<em>A</em><sub>1</sub>) \\ <em>f</em>(<em>A</em><sub>2</sub>) = "
    "{<em>v</em>} olur; oysa <em>A</em><sub>1</sub> \\ <em>A</em><sub>2</sub> = {1, 3} ve görüntüsü {<em>u</em>, "
    "<em>v</em>}'dir. 1 ile 2 aynı görüntüyü paylaştığı için <em>u</em> farkta kaybolur.",
    aria="Arrow diagram of a function from X = {1, 2, 3} to Y = {u, v}: 1 and 2 go to u, 3 goes to v; "
         "A1 = {1, 3} and A2 = {2} are marked"))
