# -*- coding: utf-8 -*-
"""
Figures of the chapter "Kümeler, Fonksiyonlar ve Tümevarım Üzerine Problemler"
(dersler/analiz-1/problemler-kumeler-fonksiyonlar-tumevarim.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box and never directly under a heading.
The figures are NOT produced at build time. Run

    python scripts/analysis1_problem_figures/ps4a.py
    python scripts/center_figures.py "analysis1-ps4a-*.md"
    python scripts/check_figure_labels.py "scripts/_figures/analysis1-ps4a-*.md"

and paste the markup of scripts/_figures/analysis1-ps4a-<name>.md into the .qmd.
The captions are Turkish on purpose; the aria labels are plain ASCII.

Conventions: in the Venn diagrams the shaded region is the set named under the
panel; on the function graphs a point that belongs to a set is a filled dot and
the preimage on the x axis is drawn as a thick segment.
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, BASE, PRACTICE, TEXT, THEORY, WIDE  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "analysis1-ps4a-"

MINUS, CAP, SUPM1 = "&#8722;", "&#8745;", "&#8722;1"


def save(name, svg):
    (OUT_DIR / f"{PREFIX}{name}.md").write_text(svg, encoding="utf-8", newline="\n")
    print(f"{PREFIX}{name}.md")


def it(s):
    """Italic math letter inside an SVG <text>."""
    return f'<tspan font-style="italic">{s}</tspan>'


def sups(s, size=9):
    """Superscript inside an SVG <text>."""
    return f'<tspan font-size="{size}" dy="-5">{s}</tspan><tspan dy="5">&#8203;</tspan>'


def num(v):
    """A tick label with a typographic minus sign and simple fractions."""
    special = {0.5: "1/2", -0.5: "&#8722;1/2"}
    if v in special:
        return special[v]
    s = f"{v:g}"
    return s.replace("-", MINUS)


# ---------------------------------------------------------------------------
# Venn diagrams of two sets
# ---------------------------------------------------------------------------
VR, VD = 38.0, 22.0          # circle radius and half distance of the centers (pixels)


def _disk(x, cy, r=VR):
    return (f'M{x + r:.1f},{cy:.1f} A{r},{r} 0 1 1 {x - r:.1f},{cy:.1f} '
            f'A{r},{r} 0 1 1 {x + r:.1f},{cy:.1f} Z')


def _lens(cx, cy, r=VR, d=VD):
    hh = math.sqrt(r * r - d * d)
    return (f'M{cx:.1f},{cy - hh:.1f} A{r},{r} 0 0 1 {cx:.1f},{cy + hh:.1f} '
            f'A{r},{r} 0 0 1 {cx:.1f},{cy - hh:.1f} Z')


def venn(p, cx, cy, shade, title, r=VR, d=VD, opacity=0.32):
    """Two circles A (left) and B (right) centred around (cx, cy).

    shade maps a region name to a colour: "a" = only in A, "ab" = in both,
    "b" = only in B.
    """
    ax, bx = cx - d, cx + d
    for region, color in shade.items():
        fill = f'fill="{color}" fill-opacity="{opacity}" stroke="none"'
        if region == "ab":
            p.add(f'<path d="{_lens(cx, cy, r, d)}" {fill}/>')
        elif region == "a":
            p.add(f'<path d="{_disk(ax, cy, r)} {_lens(cx, cy, r, d)}" fill-rule="evenodd" {fill}/>')
        elif region == "b":
            p.add(f'<path d="{_disk(bx, cy, r)} {_lens(cx, cy, r, d)}" fill-rule="evenodd" {fill}/>')
    for x in (ax, bx):
        p.add(f'<circle cx="{x:.1f}" cy="{cy:.1f}" r="{r}" fill="none" stroke="{TEXT}" stroke-width="1.2" opacity="0.75"/>')
    p.text_px(ax - 0.62 * r, cy - 0.78 * r - 4, "A", TEXT, 12, "middle", False, True)
    p.text_px(bx + 0.62 * r, cy - 0.78 * r - 4, "B", TEXT, 12, "middle", False, True)
    p.text_px(cx, cy + r + 22, title, TEXT, 12, "middle", True)


def venn_figure(name, panels, caption, aria):
    """panels: list of (shade, title); laid out left to right."""
    step = 2 * (VR + VD) + 56
    W = int(step * len(panels))
    H = 2 * VR + 60
    p = Plot(0, 0, W, H, (0, W), (0, H))
    for i, (shade, title) in enumerate(panels):
        venn(p, step / 2 + step * i, VR + 12, shade, title)
    save(name, figure(W, H, [p], caption, aria=aria))


# ============================================================
# venn-fark-a: A \ (B \ A) = A
# ============================================================
venn_figure(
    "venn-fark-a",
    [({"b": PRACTICE}, "B \\ A"), ({"a": THEORY, "ab": THEORY}, "A \\ (B \\ A) = A")],
    "Solda <em>B</em> \\ <em>A</em>: <em>B</em>'nin <em>A</em> dışında kalan hilal biçimli parçası. "
    "Bu parça <em>A</em> ile hiç örtüşmediğinden <em>A</em>'dan onu çıkarmak hiçbir şey koparmaz; "
    "sağda kalan bölge <em>A</em>'nın tamamıdır.",
    "Venn semasi: B fark A ve A fark (B fark A) esittir A")

# ============================================================
# venn-fark-b: A \ (A \ B) = A cap B
# ============================================================
venn_figure(
    "venn-fark-b",
    [({"a": PRACTICE}, "A \\ B"), ({"ab": THEORY}, "A \\ (A \\ B) = A " + CAP + " B")],
    "Solda <em>A</em> \\ <em>B</em>: <em>A</em>'nın <em>B</em> dışında kalan parçası. "
    "<em>A</em>'dan bu parça çıkarılınca geriye yalnızca iki çemberin ortak bölgesi, "
    "yani <em>A</em> &#8745; <em>B</em> kalır.",
    "Venn semasi: A fark B ve A fark (A fark B) esittir A kesisim B")

# ============================================================
# venn-fark-c: A cap (B \ A) is empty
# ============================================================
venn_figure(
    "venn-fark-c",
    [({"b": PRACTICE}, "B \\ A"), ({"a": THEORY, "ab": THEORY, "b": PRACTICE}, "A ile B \\ A ayrık")],
    "Solda <em>B</em> \\ <em>A</em>. Sağda <em>A</em> ile <em>B</em> \\ <em>A</em> iki ayrı tonla "
    "birlikte çizilmiştir: iki bölgenin ortak noktası yoktur, "
    "dolayısıyla kesişimleri boş kümedir.",
    "Venn semasi: A ile B fark A ayrik, kesisim bos")

# ============================================================
# venn-simetrik-fark: D = elements in exactly one of A, B
# ============================================================
p = Plot(0, 0, 260, 140, (0, 260), (0, 140))
R5, D5 = 52.0, 30.0
CX, CY = 130.0, 62.0
venn(p, CX, CY, {"a": THEORY, "b": THEORY}, "D: yalnız birinde olanlar", R5, D5)
p.text_px(CX - D5 - 0.55 * R5, CY + 4, "A \\ B", TEXT, 11, "middle", True)
p.text_px(CX + D5 + 0.55 * R5, CY + 4, "B \\ A", TEXT, 11, "middle", True)
p.text_px(CX, CY + 4, "A " + CAP + " B", TEXT, 10.5, "middle", False)
save("venn-simetrik-fark", figure(
    260, 140, [p],
    "<em>A</em> ile <em>B</em>'nin simetrik farkı <em>D</em>: iki kümeden yalnızca birine ait olan "
    "elemanlar. Taralı bölge iki hilalden oluşur; ortadaki <em>A</em> &#8745; <em>B</em> bölgesi "
    "(her iki kümede olanlar) ile iki çemberin dışı <em>D</em>'ye girmez.",
    aria="Venn semasi: simetrik fark, iki hilal taranmis, ortak bolge bos"))

# ============================================================
# cember-fonksiyon-degil: the unit circle fails the vertical line test
# ============================================================
PPU = 78.0
p = Plot(30, 24, PPU * 3.0, PPU * 3.0, (-1.5, 1.5), (-1.5, 1.5))
p.polygon([(-1, -1), (1, -1), (1, 1), (-1, 1)], fill=BASE, opacity=0.07, stroke=BASE, width=1.0, dash="4 3")
p.origin_axes("x", "y")
p.circle(0, 0, 1, THEORY, 2.0)
p.label(1, 0, "1", 5, 15, TEXT, 11, "start")
p.label(-1, 0, MINUS + "1", -5, 15, TEXT, 11, "end")
p.label(0, 1, "1", -5, -5, TEXT, 11, "end")
p.label(0, -1, MINUS + "1", -5, 14, TEXT, 11, "end")
p.line([(0.6, -1.42), (0.6, 1.42)], PRACTICE, 1.3, dash="5 3")
p.points([(0.6, 0.8), (0.6, -0.8)], PRACTICE, 4.2)
p.label(0.6, 0.8, "(3/5, 4/5)", 8, -7, PRACTICE, 11.5, "start", True)
p.label(0.6, -0.8, "(3/5, " + MINUS + "4/5)", 8, 34, PRACTICE, 11.5, "start", True)
p.label(0.6, 1.42, "x = 3/5", 6, 4, PRACTICE, 11, "start", False, True)
p.label(-1, 1, "A " + "&#215;" + " B", 4, -6, BASE, 11, "start", True)
save("cember-fonksiyon-degil", figure(
    300, 290, [p],
    "Birim çember (mavi) ve [&#8722;1, 1] &#215; [&#8722;1, 1] karesi (kesikli çerçeve). "
    "<em>x</em> = 3/5 düşey doğrusu çemberi iki noktada keser: aynı <em>x</em> değerine iki farklı "
    "<em>y</em> karşılık gelir, dolayısıyla çember bir fonksiyon grafiği değildir.",
    aria="Birim cember, x = 3/5 dogrusu cemberi iki noktada kesiyor"))


# ============================================================
# Graph helpers
# ============================================================
def curve(p, f, x0, x1, ymin, ymax, color=THEORY, width=2.0, n=400, opacity=1.0):
    """Plot y = f(x) on [x0, x1], dropping the points outside [ymin, ymax]."""
    seg = []
    for k in range(n + 1):
        x = x0 + (x1 - x0) * k / n
        y = f(x)
        if ymin <= y <= ymax:
            seg.append((x, y))
        elif seg:
            if len(seg) > 1:
                p.line(seg, color, width, opacity=opacity)
            seg = []
    if len(seg) > 1:
        p.line(seg, color, width, opacity=opacity)


def preimage_segment(p, a, b):
    """Thick segment [a, b] on the x axis with filled end points."""
    p.line([(a, 0), (b, 0)], BASE, 5, opacity=0.9)
    p.points([(a, 0), (b, 0)], BASE, 4.0)


# ============================================================
# ters-kare-ters-goruntu: f(x) = 1/x^2, preimage of [1, 4]
# ============================================================
p = Plot(28, 26, 300, 200, (-2.4, 2.4), (-0.7, 5.3))
p.polygon([(-2.4, 1), (2.4, 1), (2.4, 4), (-2.4, 4)], fill=PRACTICE, opacity=0.10)
p.origin_axes("x", "y", xticks=(-1, -0.5, 0.5, 1), yticks=(1, 4), xfmt=num, yfmt=num)
xc = 1 / math.sqrt(5.2)
curve(p, lambda x: 1 / (x * x), -2.4, -xc, -1, 5.2)
curve(p, lambda x: 1 / (x * x), xc, 2.4, -1, 5.2)
for x0, y0 in ((-1, 1), (-0.5, 4), (0.5, 4), (1, 1)):
    p.vline(x0, 0, y0, BASE, "4 3", 0.75)
p.points([(-1, 1), (-0.5, 4), (0.5, 4), (1, 1)], THEORY, 3.4)
preimage_segment(p, -1, -0.5)
preimage_segment(p, 0.5, 1)
p.label(2.35, 2.5, it("G") + " = [1, 4]", 0, 4, PRACTICE, 11.5, "end", True)
p.label(1.55, 1 / 1.55 ** 2, it("f") + "(" + it("x") + ") = 1/" + it("x") + sups("2"), 4, -12, THEORY, 11.5, "start", True)
p.label(0, 0, it("f") + sups(SUPM1) + "(" + it("G") + "): [&#8722;1, &#8722;1/2] ve [1/2, 1]",
        0, 38, BASE, 11.5, "middle", True)
save("ters-kare-ters-goruntu", figure(
    356, 290, [p],
    "<em>f</em>(<em>x</em>) = 1/<em>x</em>&#178; grafiğinin <em>G</em> = [1, 4] şeridine düşen iki parçası, "
    "<em>x</em> eksenine [&#8722;1, &#8722;1/2] ve [1/2, 1] aralıkları olarak iner. "
    "Ters görüntü bu iki aralığın birleşimidir.",
    aria="1 bolu x kare grafigi ve [1,4] seridinin ters goruntusu iki aralik"))

# ============================================================
# bileske-ters-goruntu: h(x) = (x + 2)^2, preimage of [0, 4]
# ============================================================
p = Plot(28, 26, 300, 210, (-5.3, 1.6), (-1.0, 9.6))
p.polygon([(-5.3, 0), (1.6, 0), (1.6, 4), (-5.3, 4)], fill=PRACTICE, opacity=0.10)
p.origin_axes("x", "y", xticks=(-4, -2), yticks=(4, 9), xfmt=num, yfmt=num)
curve(p, lambda x: (x + 2) ** 2, -5.3, 1.6, -1, 9.4)
p.vline(-4, 0, 4, BASE, "4 3", 0.75)
p.points([(-4, 4), (0, 4)], THEORY, 3.4)
preimage_segment(p, -4, 0)
p.label(-5.2, 2, it("G") + " = [0, 4]", 0, 4, PRACTICE, 11.5, "start", True)
p.label(-2.0, 7.2, it("h") + "(" + it("x") + ") = (" + it("x") + " + 2)" + sups("2"), 0, 0,
        THEORY, 11.5, "middle", True)
p.label(-2, 0, it("h") + sups(SUPM1) + "(" + it("G") + ") = [&#8722;4, 0]", 0, 38, BASE, 11.5, "middle", True)
save("bileske-ters-goruntu", figure(
    356, 300, [p],
    "<em>h</em>(<em>x</em>) = (<em>x</em> + 2)&#178; parabolünün <em>G</em> = [0, 4] şeridinde kalan parçası, "
    "<em>x</em> ekseninde tek bir aralığa, [&#8722;4, 0] aralığına iner.",
    aria="x arti 2 nin karesi grafigi ve [0,4] seridinin ters goruntusu [-4,0]"))

# ============================================================
# bijeksiyon-grafigi: f(x) = x / sqrt(x^2 + 1) between the lines y = -1 and y = 1
# ============================================================
p = Plot(28, 22, 340, 170, (-6.2, 6.2), (-1.5, 1.5))
p.polygon([(-6.2, -1), (6.2, -1), (6.2, 1), (-6.2, 1)], fill=PRACTICE, opacity=0.07)
p.line([(-6.2, 1), (6.2, 1)], PRACTICE, 1.2, dash="5 3", opacity=0.9)
p.line([(-6.2, -1), (6.2, -1)], PRACTICE, 1.2, dash="5 3", opacity=0.9)
p.origin_axes("x", "y", xticks=(-4, -2, 2, 4), xfmt=num)
curve(p, lambda x: x / math.sqrt(x * x + 1), -6.2, 6.2, -1.5, 1.5, THEORY, 2.2)
p.label(-6.1, 1, it("y") + " = 1", 0, -6, PRACTICE, 11, "start")
p.label(6.1, -1, it("y") + " = " + MINUS + "1", 0, 15, PRACTICE, 11, "end")
p.label(1.7, 1.7 / math.sqrt(1.7 ** 2 + 1), it("f") + "(" + it("x") + ")", 8, 16, THEORY, 11.5, "start", True)
save("bijeksiyon-grafigi", figure(
    396, 230, [p],
    "<em>f</em>(<em>x</em>) = <em>x</em>/&#8730;(<em>x</em>&#178; + 1) grafiği <em>y</em> = &#8722;1 ve "
    "<em>y</em> = 1 doğruları arasındaki şeritte kalır, bu doğrulara hiç değmez ve şeridin her "
    "yüksekliğine tam bir kez ulaşır.",
    aria="x bolu kok x kare arti 1 grafigi, y = -1 ve y = 1 asimptotlari arasinda"))
