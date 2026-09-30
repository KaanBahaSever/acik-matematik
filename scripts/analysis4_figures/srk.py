# -*- coding: utf-8 -*-
"""
Figures of the chapter "Çok Değişkenli Fonksiyonlarda Süreklilik"
(dersler/analiz-4/cok-degiskenli-fonksiyonlarda-sureklilik.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box and never directly under a heading.
The figures are NOT produced at build time. Run

    python scripts/analysis4_figures/srk.py
    python scripts/center_figures.py "analysis4-srk-*.md"
    python scripts/check_figure_labels.py "scripts/_figures/analysis4-srk-*.md"

and paste the markup of scripts/_figures/analysis4-srk-<name>.md into the .qmd.
The captions are Turkish on purpose; the aria labels are plain ASCII.

Conventions: a boundary that belongs to the set is solid, one that does not is
dashed; a point of the set is filled, a point outside it is hollow. Every
drawing that contains a circle uses equal x and y scales.
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, hollow, dot, disk_fill, TEXT, THEORY, PRACTICE  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "analysis4-srk-"

MINUS = "&#8722;"


def save(name, markup):
    (OUT_DIR / f"{PREFIX}{name}.md").write_text(markup, encoding="utf-8", newline="\n")
    print(f"{PREFIX}{name}.md")


def it(s):
    """Italic run inside an SVG <text>."""
    return f'<tspan font-style="italic">{s}</tspan>'


def sub(s, size=8.5):
    """Subscript inside an SVG <text>."""
    return f'<tspan font-size="{size}" dy="3.5">{s}</tspan><tspan dy="-3.5">&#8203;</tspan>'


def sup(s, size=8.5):
    """Superscript inside an SVG <text>."""
    return f'<tspan font-size="{size}" dy="-5">{s}</tspan><tspan dy="5">&#8203;</tspan>'


def num(v):
    return f"{v:g}".replace("-", MINUS).replace(".", ",")


def eq_plot(x0, y0, ppu, xr, yr):
    """Panel with the same number of pixels per unit on both axes."""
    return Plot(x0, y0, (xr[1] - xr[0]) * ppu, (yr[1] - yr[0]) * ppu, xr, yr)


X0 = it("x") + sub("0")

# ============================================================
# izole: D = B[0, 1] together with the isolated point (3, 0)
# ============================================================
p = eq_plot(40, 30, 78, (-1.5, 4.5), (-1.5, 1.5))
p.origin_axes(it("x"), it("y"), (), (), num, num, 0.45)
# the closed unit ball belongs to D: shaded, solid boundary
disk_fill(p, 0, 0, 1, THEORY, 0.16)
p.circle(0, 0, 1, THEORY, 2.0)
p.label(-0.5, 0.42, it("B") + "[0, 1]", 0, 0, THEORY, 12.5, "middle", True)
# the open ball B(x0, 1) around the isolated point: dashed
p.circle(3, 0, 1, PRACTICE, 1.7, "6 4")
ang = math.radians(42)
p.label(3 + math.cos(ang), math.sin(ang), it("B") + "(" + X0 + ", 1)", 6, -3, PRACTICE, 12.5)
dot(p, (3, 0), THEORY, 4.2)
p.label(3, 0, X0 + " = (3, 0)", 0, -11, THEORY, 12, "middle")
# a limit point on the unit circle
dot(p, (1, 0), TEXT, 3.0)
p.line([(1.05, -0.06), (1.35, -0.62)], TEXT, 0.9, None, 0.6)
p.label(1.35, -0.62, "yığılma", 0, 12, TEXT, 11.5, "middle")
p.label(1.35, -0.62, "noktası", 0, 25, TEXT, 11.5, "middle")
save("izole", figure(
    560, 300, [p],
    "<em>D</em> = <em>B</em>[0, 1] &#8746; {(3, 0)} kümesi. <em>x</em><sub>0</sub> = (3, 0) merkezli, 1 "
    "yarıçaplı yuvar kapalı birim yuvara değmez (aradaki en kısa uzaklık 1'dir); bu yüzden "
    "<em>B</em>(<em>x</em><sub>0</sub>, 1) &#8745; <em>D</em> = {<em>x</em><sub>0</sub>} olur ve "
    "<em>x</em><sub>0</sub> izole bir noktadır. (1, 0) gibi bir yığılma noktasının ise her yuvarı "
    "<em>D</em>'nin başka noktalarını da içerir.",
    aria="Closed unit disc shaded with a solid boundary, the isolated point (3, 0) with a dashed circle "
         "of radius 1 around it that does not meet the disc, and the limit point (1, 0) on the unit circle"))

# ============================================================
# kaldirilabilir: radial section r -> sin(r^2)/r^2 with the displaced value at r = 0
# ============================================================


def g(r):
    return math.sin(r * r) / (r * r)


p = Plot(50, 30, 440, 250, (-3.0, 3.0), (-0.3, 1.2))
p.axes((-3, -2, -1, 0, 1, 2, 3), (0, 0.5, 1), it("r"), "", num, num)
p.line([(-3.0, 0), (3.0, 0)], TEXT, 0.8, None, 0.35)
p.line([(-3.0, 1), (3.0, 1)], TEXT, 1.0, "5 4", 0.55)
for s in (-1, 1):
    pts = [(s * (0.004 + (3.0 - 0.004) * k / 300), 0.0) for k in range(301)]
    p.line([(x, g(x)) for x, _ in pts], THEORY, 2.3)
# the arrow that moves the value f(0, 0) = 0 up to the limit 1
p.arrow((0, 0.03), (0, 0.955), TEXT, 1.1, 7.0, "4 3", 0.8)
hollow(p, (0, 1), THEORY, 4.0, 1.8)
dot(p, (0, 0), PRACTICE, 4.2)
p.label(0, 1, "limit 1", 0, -11, THEORY, 12, "middle")
p.label(0, 0, it("f") + "(0, 0) = 0", 8, -7, PRACTICE, 12)
p.label(0, 0.5, "değeri 1 yap", 7, 4, TEXT, 11.5)
save("kaldirilabilir", figure(
    540, 330, [p],
    "<em>f</em>'nin orijinden geçen bir doğru boyunca kesiti: <em>r</em> &#8800; 0 için "
    "<em>g</em>(<em>r</em>) = sin(<em>r</em>²)/<em>r</em>² eğrisi, <em>r</em> uzaklığı işaretli alınmıştır. "
    "Eğri <em>r</em> &#8594; 0 iken 1'e yaklaşır (içi boş nokta), oysa <em>f</em>(0, 0) = 0'dır (dolu nokta). "
    "Bu tek değer 1 yapılınca fonksiyon orijinde sürekli olur.",
    aria="Graph of sin(r^2)/r^2 for r between -3 and 3 without r = 0, approaching 1 at r = 0 where a hollow "
         "point sits, the filled point (0, 0) below it and a dashed arrow moving the value from 0 to 1"))

# ============================================================
# yerellik: the ball about (a, b) of radius |(a, b)| misses the origin
# ============================================================
A, B = 1.5, 1.0
R = math.hypot(A, B)                                   # 1.8028
p = eq_plot(40, 30, 86, (-1.5, 3.5), (-1.5, 3.0))
disk_fill(p, A, B, R, THEORY, 0.13)
p.origin_axes(it("x"), it("y"), (), (), num, num, 0.45)
p.circle(A, B, R, THEORY, 1.8, "6 4")
p.line([(A, B), (0, 0)], TEXT, 1.2, None, 0.8)
nx, ny = -B / R, A / R                                 # unit normal of the radius, pointing up-left
p.label(A / 2 + 0.13 * nx, B / 2 + 0.13 * ny, it("r"), 0, 4, TEXT, 13, "middle")
dot(p, (A, B), THEORY, 4.0)
p.label(A, B, "(" + it("a") + ", " + it("b") + ")", 8, -7, THEORY, 12.5)
hollow(p, (0, 0), PRACTICE, 4.2, 1.8)
p.label(0, 0, "özel nokta (0, 0)", -8, 18, PRACTICE, 12, "end")
p.label(A, B + 1.12, "burada " + it("f") + " = " + it("x") + "²" + it("y") + "²/(" + it("x") + "² + "
        + it("y") + "²)", 0, 0, TEXT, 11.5, "middle")
save("yerellik", figure(
    500, 440, [p],
    "(<em>a</em>, <em>b</em>) = (1,5; 1) merkezli, <em>r</em> = &#8214;(<em>a</em>, <em>b</em>)&#8214; &#8776; 1,80 "
    "yarıçaplı açık yuvar. Orijin çemberin üzerindedir, yani yuvara ait değildir; bu yuvarda <em>f</em>, "
    "<em>x</em>²<em>y</em>²/(<em>x</em>² + <em>y</em>²) rasyonel fonksiyonuyla çakışır ve "
    "(<em>a</em>, <em>b</em>)'deki süreklilik oradan gelir.",
    aria="Open disc around (1.5, 1) whose radius equals the distance to the origin, so the dashed boundary "
         "circle passes through the hollow origin, with the radius drawn as a segment"))
