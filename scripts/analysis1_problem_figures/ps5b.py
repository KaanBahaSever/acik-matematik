# -*- coding: utf-8 -*-
"""
Figures of the chapter "Doğal Sayılar, İrrasyonel Sayılar, Sayılabilirlik ve
Eşitsizlikler Üzerine Problemler"
(dersler/analiz-1/problemler-dogal-sayilar-sayilabilirlik-esitsizlikler.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box and never directly under a heading.
The figures are NOT produced at build time. Run

    python scripts/analysis1_problem_figures/ps5b.py
    python scripts/center_figures.py "analysis1-ps5b-*.md"
    python scripts/check_figure_labels.py "scripts/_figures/analysis1-ps5b-*.md"

and paste the markup of scripts/_figures/analysis1-ps5b-<name>.md into the .qmd.
The captions are Turkish on purpose; the aria labels are plain ASCII.

Conventions: an endpoint that belongs to an interval is filled, one that does
not is hollow; a union is drawn as a thick band on the number line.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, hollow, TEXT, BG, THEORY, PRACTICE, BASE, REMARK  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "analysis1-ps5b-"

MINUS, INFTY = "&#8722;", "&#8734;"


def save(name, svg):
    (OUT_DIR / f"{PREFIX}{name}.md").write_text(svg, encoding="utf-8", newline="\n")
    print(f"{PREFIX}{name}.md")


def it(s):
    """Italic math letter inside an SVG <text>."""
    return f'<tspan font-style="italic">{s}</tspan>'


def subs(s, size=9):
    """Subscript inside an SVG <text>."""
    return f'<tspan font-size="{size}" dy="4">{s}</tspan><tspan dy="-4">&#8203;</tspan>'


def sups(s, size=9):
    """Superscript inside an SVG <text>."""
    return f'<tspan font-size="{size}" dy="-5">{s}</tspan><tspan dy="5">&#8203;</tspan>'


def number_line(p, x0, x1, ticks, labels, y=0.0):
    """Horizontal number line at height y with an arrowhead on the right."""
    p.arrow((x0, y), (x1, y), TEXT, 1.1, head=8, opacity=0.55)
    for t, s in zip(ticks, labels):
        p.add(f'<line x1="{p.X(t):.1f}" y1="{p.Y(y) - 4:.1f}" x2="{p.X(t):.1f}" y2="{p.Y(y) + 4:.1f}" '
              f'stroke="{TEXT}" stroke-width="1" opacity="0.55"/>')
        p.label(t, y, s, 0, 17, TEXT, 11, "middle")


# ============================================================
# aile-b: the nested intervals [1, 1 + 1/n] shrink to the point 1
# ============================================================
p = Plot(30, 20, 400, 200, (0.72, 2.28), (-0.7, 6.6))
number_line(p, 0.74, 2.25, [1, 1.5, 2], ["1", "1,5", "2"])
p.vline(1, 0, 6.4, TEXT, "3 3", 0.45)
XS = 1.3
p.vline(XS, 0, 6.4, REMARK, "5 4", 0.9)
for n in range(1, 7):
    y = 7 - n
    right = 1 + 1 / n
    inside = right >= XS
    col = THEORY if inside else PRACTICE
    p.line([(1, y), (right, y)], col, 4, None, 0.75)
    p.points([(1, y), (right, y)], col, 3.6)
    p.label(1, y, it("n") + f" = {n}", -12, 4, col, 11.5, "end")
p.points([(1, 0)], BASE, 4.4)
p.label(XS, 0, it("x"), 0, 17, REMARK, 12, "middle", bold=True)
p.label(1.62, 3.1, it("x") + " bu aralıkların", 0, 0, PRACTICE, 11, "start")
p.label(1.62, 2.2, "dışında kalır", 0, 0, PRACTICE, 11, "start")
save("aile-b", figure(
    470, 270, [p],
    "[1, 1 + 1/<em>n</em>] aralıkları <em>n</em> büyüdükçe 1 noktasına doğru daralır. 1'den büyük bir "
    "<em>x</em> sayısı (şekilde <em>x</em> = 1,3), 1/<em>n</em> &lt; <em>x</em> &#8722; 1 olduğu andan "
    "itibaren (burada <em>n</em> = 4'ten itibaren) aralıkların dışında kalır; bütün aralıklarda ortak olan "
    "tek nokta 1'dir. En uzun aralık <em>n</em> = 1'e karşılık gelen [1, 2] aralığıdır.",
    aria="Nested closed intervals from 1 to 1 + 1/n for n = 1 to 6; a point x = 1.3 lies outside "
         "the intervals from n = 4 on; only the point 1 lies in all of them"))

# ============================================================
# aile-g: the rays (-oo, (2n-1)/(n+1)] fill (-oo, 2) without reaching 2
# ============================================================
p = Plot(30, 20, 420, 200, (-2.35, 2.55), (-0.7, 6.6))
number_line(p, -2.3, 2.5, [-1, 0, 1, 2], [MINUS + "1", "0", "1", "2"])
p.vline(2, 0, 6.4, REMARK, "5 4", 0.9)
for n in range(1, 7):
    y = 7 - n
    right = (2 * n - 1) / (n + 1)
    p.arrow((right, y), (-1.95, y), THEORY, 4, head=11, opacity=0.75)
    p.points([(right, y)], THEORY, 3.6)
    p.label(-1.95, y, it("n") + f" = {n}", -8, 4, THEORY, 11.5, "end")
p.line([(-2.25, 0), (2, 0)], BASE, 5, None, 0.6)
hollow(p, (2, 0), BASE, 4.4, 1.8)
p.label(2, 6.4, "2'ye ulaşılmaz", -6, -2, REMARK, 11, "end")
save("aile-g", figure(
    470, 270, [p],
    "Işınların sağ uçları 1/2, 1, 5/4, 7/5, 3/2, 11/7, … sayılarıdır; bu sayılar artarak 2'ye "
    "yaklaşır ama 2'ye hiç ulaşmaz. Birleşim, sayı doğrusundaki kalın bantla gösterilen "
    "(&#8722;&#8734;, 2) ışınıdır.",
    aria="Rays from minus infinity to (2n-1)/(n+1) for n = 1 to 6; the right endpoints increase "
         "towards 2 without reaching it; their union is the ray from minus infinity to 2, 2 excluded"))

# ============================================================
# ara-kume: A in B in C, f maps C onto A; the shaded rings form D and h moves
# them one ring inwards, the white rings are fixed
# ============================================================
W, H = 510, 346
p = Plot(0, 0, W, H, (0, W), (H, 0))          # identity map: data = pixels
DX, DY = 34, 28
names = [it("C"), it("B"), it("A"), it("f") + "(" + it("B") + ")", it("f") + "(" + it("A") + ")",
         it("f") + sups("2") + "(" + it("B") + ")"]
for i in range(6):
    x0, y0 = 10 + DX * i, 10 + DY * i
    x1, y1 = W - 10 - DX * i, H - 10 - DY * i
    shaded = i in (0, 2, 4)
    fill = THEORY if shaded else BG
    op = 0.20 if shaded else 1.0
    p.add(f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="{BG}" stroke="none"/>')
    if shaded:
        p.add(f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="{fill}" '
              f'fill-opacity="{op}" stroke="none"/>')
    p.add(f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="none" '
          f'stroke="{TEXT}" stroke-width="1.2" opacity="0.7"/>')
    p.text_px(x0 + 7, y0 + 20, names[i], TEXT, 12, "start", bold=True)
band_text = [
    it("D") + subs("1") + " = " + it("C") + " " + MINUS + " " + it("B"),
    it("h") + "(" + it("x") + ") = " + it("x"),
    it("D") + subs("2") + " = " + it("f") + "(" + it("D") + subs("1") + ")",
    it("h") + "(" + it("x") + ") = " + it("x"),
    it("D") + subs("3") + " = " + it("f") + "(" + it("D") + subs("2") + ")",
]
for i, s in enumerate(band_text):
    col = THEORY if i % 2 == 0 else TEXT
    p.text_px(W / 2, 10 + DY * i + 20, s, col, 12, "middle", bold=(i % 2 == 0))
p.text_px(W / 2, 10 + DY * 5 + 30, "&#8230;", TEXT, 14, "middle")
p.arrow((483, 240), (415, 240), PRACTICE, 1.9, head=9)
p.text_px(449, 233, it("f"), PRACTICE, 12.5, "middle", bold=True)
p.arrow((415, 210), (347, 210), PRACTICE, 1.9, head=9)
p.text_px(381, 203, it("f"), PRACTICE, 12.5, "middle", bold=True)
save("ara-kume", figure(
    W, H, [p],
    "<em>C</em>, <em>B</em>, <em>A</em>, <em>f</em>(<em>B</em>), <em>f</em>(<em>A</em>), … kümeleri iç "
    "içedir. Mavi halkalar <em>D</em> kümesini oluşturur ve <em>h</em> her mavi halkayı <em>f</em> ile bir "
    "sonraki mavi halkaya taşır; boyasız halkalarda <em>h</em> birim fonksiyondur. En dıştaki halka "
    "(<em>C</em> &#8722; <em>B</em>) böylece boşalır: <em>h</em>, <em>C</em>'yi <em>B</em>'nin üzerine eşler.",
    aria="Nested rectangles C, B, A, f(B), f(A), f2(B); the rings C minus B, A minus f(B) and f(A) minus "
         "f2(B) are shaded and arrows labelled f move each shaded ring to the next one inside"))
