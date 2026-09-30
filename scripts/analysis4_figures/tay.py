# -*- coding: utf-8 -*-
"""
Figures of the chapter "Taylor Formülü"
(dersler/analiz-4/taylor-formulu.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box and never directly under a heading.
The figures are NOT produced at build time. Run

    python scripts/analysis4_figures/tay.py
    python scripts/center_figures.py "analysis4-tay-*.md"
    python scripts/check_figure_labels.py "scripts/_figures/analysis4-tay-*.md"

and paste the markup of scripts/_figures/analysis4-tay-<name>.md into the .qmd.
The captions are Turkish on purpose; the aria labels are plain ASCII.

Conventions: a boundary that belongs to the set is solid, one that does not is
dashed; a point of the set is filled, a point outside it is hollow. The
maps-to arrow is not in the renderer's fallback font, so it is written as a
bar followed by an arrow (MAPSTO).
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, blob, closed_curve, dot, hollow, TEXT, THEORY, PRACTICE, BASE, WIDE  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "analysis4-tay-"

MINUS, THETA, DELTA = "&#8722;", "&#952;", "&#948;"
MAPSTO = '|<tspan dx="-2.2">&#8594;</tspan>'


def save(name, markup):
    (OUT_DIR / f"{PREFIX}{name}.md").write_text(markup, encoding="utf-8", newline="\n")
    print(f"{PREFIX}{name}.md")


def it(s):
    """Italic run inside an SVG <text>."""
    return f'<tspan font-style="italic">{s}</tspan>'


def sup(s, size=8.5):
    """Superscript inside an SVG <text>."""
    return f'<tspan font-size="{size}" dy="-5">{s}</tspan><tspan dy="5">&#8203;</tspan>'


def num(v):
    return f"{v:g}".replace("-", MINUS).replace(".", ",")


def eq_plot(x0, y0, ppu, xr, yr):
    """Panel with the same number of pixels per unit on both axes."""
    return Plot(x0, y0, (xr[1] - xr[0]) * ppu, (yr[1] - yr[0]) * ppu, xr, yr)


def inside(poly, q):
    """Even-odd point-in-polygon test."""
    x, y = q
    c = False
    for (x1, y1), (x2, y2) in zip(poly, poly[1:] + poly[:1]):
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
            c = not c
    return c


def bezier(P0, C, P1, n=80):
    return [((1 - t) ** 2 * P0[0] + 2 * t * (1 - t) * C[0] + t * t * P1[0],
             (1 - t) ** 2 * P0[1] + 2 * t * (1 - t) * C[1] + t * t * P1[1])
            for t in (k / n for k in range(n + 1))]


# ============================================================
# dogru-parcasi: L(a; x) extended to t in (-delta, 1 + delta) inside the open set U
# ============================================================
p = eq_plot(20, 20, 62, (-2.85, 6.95), (-1.9, 2.05))
U_PTS = [(2.6 * x, 1.65 * y) for x, y in blob(0.0, 0.0, 1.0, [(0.07, 3, 0.9), (0.05, 5, 2.4), (0.04, 2, 1.1)])]
closed_curve(p, U_PTS, THEORY, 1.5, "6 4", THEORY, 0.13)
A = (-0.95, -0.45)
XP = (0.85, 0.4)
H = (XP[0] - A[0], XP[1] - A[1])
D, TH = 0.25, 0.35


def seg(t):
    return (A[0] + t * H[0], A[1] + t * H[1])


C = seg(TH)
for t in [k / 20 * (1 + 2 * D + 0.3) - D - 0.15 for k in range(21)]:
    assert inside(U_PTS, seg(t)), t            # the segment, extended a little further, stays in U
p.line([seg(-D), A], TEXT, 1.5, "4 3", 0.8)
p.line([XP, seg(1 + D)], TEXT, 1.5, "4 3", 0.8)
p.line([A, XP], TEXT, 2.8)
hollow(p, seg(-D), TEXT, 3.4)
hollow(p, seg(1 + D), TEXT, 3.4)
L = math.hypot(*H)
N = (-H[1] / L * 0.24, H[0] / L * 0.24)          # offset of the h arrow, above the segment
p.arrow((A[0] + N[0], A[1] + N[1]), (XP[0] + N[0], XP[1] + N[1]), TEXT, 1.2, 7.0, None, 0.75)
mid = seg(0.5)
p.label(mid[0] + N[0], mid[1] + N[1], it("h") + " = " + it("x") + " " + MINUS + " " + it("a"), -8, -14,
        TEXT, 12, "middle")
dot(p, A, THEORY, 4.2)
dot(p, C, PRACTICE, 4.2)
dot(p, XP, BASE, 4.2)
p.label(*A, it("a"), 3, 18, THEORY, 13.5)
p.label(*XP, it("x"), 2, 18, BASE, 13.5)
p.label(*C, it("c") + " = " + it("a") + " + " + it(THETA) + it("h"), 2, 20, PRACTICE, 12.5)
p.label(*seg(-D), it("a") + " " + MINUS + " " + it(DELTA) + it("h"), -8, 4, TEXT, 12, "end")
p.label(*seg(1 + D), it("x") + " + " + it(DELTA) + it("h"), 8, 4, TEXT, 12)
p.label(-1.25, 0.95, it("U"), 0, 0, THEORY, 15, "middle", True)
# the parameter line
TY = -0.55


def tx(t):
    return 3.9 + 1.75 * t


p.arrow((tx(-0.5), TY), (tx(1.6), TY), TEXT, 1.1, 7.0, None, 0.55)
p.label(tx(1.6), TY, it("t"), 0, 17, TEXT, 12.5, "end")
p.line([(tx(-D), TY), (tx(1 + D), TY)], TEXT, 3.0)
hollow(p, (tx(-D), TY), TEXT, 3.6)
hollow(p, (tx(1 + D), TY), TEXT, 3.6)
for t, col in ((0.0, THEORY), (TH, PRACTICE), (1.0, BASE)):
    dot(p, (tx(t), TY), col, 4.2)
for t, s, col in ((-D, MINUS + it(DELTA), TEXT), (0.0, "0", THEORY), (TH, it(THETA), PRACTICE),
                  (1.0, "1", BASE), (1 + D, "1 + " + it(DELTA), TEXT)):
    p.label(tx(t), TY, s, 0, 20, col, 12.5, "middle")
# the map t -> a + t h
ARC = bezier((tx(0.5), TY + 0.22), (3.5, 2.1), (2.2, 1.2))
p.line(ARC[:-3], TEXT, 1.4, None, 0.85)
p.arrow(ARC[-4], ARC[-1], TEXT, 1.4, 8.0, None, 0.85)
p.label(3.65, 1.65, it("t") + " " + MAPSTO + " " + it("a") + " + " + it("t") + it("h"), 6, 0, TEXT, 12.5)
save("dogru-parcasi", figure(
    660, 300, [p],
    "Açık <em>U</em> kümesinde <em>a</em> ile <em>x</em>'i birleştiren <em>L</em>(<em>a</em>; <em>x</em>) doğru "
    "parçası ve <em>h</em> = <em>x</em> &#8722; <em>a</em>. <em>t</em> &#8614; <em>a</em> + <em>th</em> eşlemesi "
    "(&#8722;<em>&#948;</em>, 1 + <em>&#948;</em>) aralığını, iki ucundan kesikli uzatılmış parçaya götürür ve "
    "parça hâlâ <em>U</em>'nun içindedir; 0, <em>&#952;</em> ve 1 sırasıyla <em>a</em>, <em>c</em> = <em>a</em> + "
    "<em>&#952;h</em> ve <em>x</em> noktalarına gider (aynı renkler).",
    css_class=WIDE,
    aria="An open set U with the segment from a to x, dashed extensions to a - delta h and x + delta h, the "
         "point c = a + theta h, and on the right the interval from -delta to 1 + delta with the points 0, "
         "theta, 1 and a curved arrow t to a + t h"))

# ============================================================
# ustel-kosinus-kesit: g(t) = -e^t sin t and its Taylor polynomials of order 1 and 2
# ============================================================


def g(t):
    return -math.exp(t) * math.sin(t)


p = Plot(60, 30, 430, 330, (-1.0, 1.15), (-2.5, 1.2))
p.origin_axes(it("t"), "", (-1, -0.5, 0.5, 1), (-2, -1, 1), num, num, 0.45)
TS = [-1 + 2 * k / 200 for k in range(201)]
p.line([(t, -t) for t in TS], PRACTICE, 1.8, "7 4")
p.line([(t, -t - t * t) for t in TS], BASE, 2.3, "0.5 4.5")
p.line([(t, g(t)) for t in TS], THEORY, 2.6)
dot(p, (0, 0), TEXT, 4.0)
p.label(1, -1, MINUS + it("t"), 8, 4, PRACTICE, 12.5)
p.label(1, -2, MINUS + it("t") + " " + MINUS + " " + it("t") + "²", 8, 1, BASE, 12.5)
p.label(1, g(1), it("g") + "(" + it("t") + ") = " + MINUS + it("e") + sup(it("t")) + " sin " + it("t"), -12, 12,
        THEORY, 12.5, "end")
save("ustel-kosinus-kesit", figure(
    660, 400, [p],
    "<em>f</em>(<em>x</em>, <em>y</em>) = <em>e<sup>y</sup></em> cos <em>x</em> fonksiyonunun (<em>&#960;</em>/2 + "
    "<em>t</em>, <em>t</em>) doğrusu boyunca kesiti <em>g</em>(<em>t</em>) = &#8722;<em>e<sup>t</sup></em> sin "
    "<em>t</em> (düz), birinci mertebeden Taylor polinomu &#8722;<em>t</em> (kesikli) ve ikinci mertebeden "
    "Taylor polinomu &#8722;<em>t</em> &#8722; <em>t</em>² (noktalı). İkinci mertebeden polinom <em>t</em> = 0 "
    "civarında eğriye çok daha iyi yapışır.",
    aria="Graph of g(t) = -e^t sin t for t between -1 and 1 with the dashed line -t and the dotted parabola "
         "-t - t^2, all three passing through the origin"))
