# -*- coding: utf-8 -*-
"""
Figures of the chapter "Hatalar ve Makine Sayıları"
(dersler/numerik-analiz/hatalar-ve-makine-sayilari.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box and never directly under a heading.
The figures are NOT produced at build time. Run

    python scripts/numerical_figures/hat.py
    python scripts/center_figures.py "numerical-hat-*.md"
    python scripts/check_figure_labels.py "scripts/_figures/numerical-hat-*.md"

and paste the markup of scripts/_figures/numerical-hat-<name>.md into the .qmd.
Captions are Turkish on purpose; aria labels are plain ASCII.
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, TEXT, THEORY, PRACTICE, REMARK, BG, WIDE  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "numerical-hat-"

MINUS = "&#8722;"


def save(name, markup):
    (OUT_DIR / f"{PREFIX}{name}.md").write_text(markup, encoding="utf-8", newline="\n")
    print(f"{PREFIX}{name}.md")


def it(s):
    """Italic run inside an SVG <text>."""
    return f'<tspan font-style="italic">{s}</tspan>'


def sup(s, size=8.5):
    """Superscript inside an SVG <text>."""
    return f'<tspan font-size="{size}" dy="-5">{s}</tspan><tspan dy="5">&#8203;</tspan>'


def sub(s, size=8):
    """Subscript inside an SVG <text>."""
    return f'<tspan font-size="{size}" dy="3">{s}</tspan><tspan dy="-3">&#8203;</tspan>'


def dec(v, digits=4):
    """Decimal comma and a true minus sign."""
    s = f"{v:.{digits}f}".rstrip("0").rstrip(".")
    return s.replace(".", ",").replace("-", MINUS)


def pixel_plot(W, H):
    """A panel whose data coordinates are the SVG pixels themselves (y grows downward)."""
    return Plot(0, 0, W, H, (0, W), (H, 0))


def brace(p, x1, x2, y, depth, color=TEXT, up=False, width=1.1, opacity=0.8):
    """Curly brace under (or, with up=True, over) the span x1..x2 at height y, tip pointing away."""
    s = -1 if up else 1
    r = min(6.0, (x2 - x1) / 4)
    xm, h = (x1 + x2) / 2, depth / 2
    d = (f"M{x1:.1f},{y:.1f} Q{x1:.1f},{y + s * h:.1f} {x1 + r:.1f},{y + s * h:.1f} "
         f"L{xm - r:.1f},{y + s * h:.1f} Q{xm:.1f},{y + s * h:.1f} {xm:.1f},{y + s * depth:.1f} "
         f"Q{xm:.1f},{y + s * h:.1f} {xm + r:.1f},{y + s * h:.1f} "
         f"L{x2 - r:.1f},{y + s * h:.1f} Q{x2:.1f},{y + s * h:.1f} {x2:.1f},{y:.1f}")
    p.add(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}" opacity="{opacity}"/>')


# ============================================================
# mutlak-bagil: the same absolute error 0.5 at p = 2 and at p = 100
# ============================================================
p = pixel_plot(520, 260)
BX0, BL, BHT = 60.0, 400.0, 22.0
PSTAR = it("p") + sup("*")
for pv, ps, top in ((2.0, 2.5, 58.0), (100.0, 100.5, 178.0)):
    u = BL / ps                              # pixels per unit: p* lands at the right end of the bar
    xe, xs = BX0 + pv * u, BX0 + ps * u
    p.text_px(BX0, top - 14, it("p") + " = " + dec(pv) + ",   " + PSTAR + " = " + dec(ps), TEXT, 12.5,
              "start", True)
    p.add(f'<rect x="{BX0:.1f}" y="{top:.1f}" width="{xe - BX0:.1f}" height="{BHT:.1f}" fill="{THEORY}" '
          f'fill-opacity="0.22" stroke="{THEORY}" stroke-width="1.1"/>')
    p.add(f'<rect x="{xe:.1f}" y="{top:.1f}" width="{xs - xe:.1f}" height="{BHT:.1f}" fill="{PRACTICE}" '
          f'fill-opacity="0.8" stroke="{PRACTICE}" stroke-width="1.1"/>')
    for x in (BX0, xe, xs):
        p.add(f'<line x1="{x:.1f}" y1="{top + BHT:.1f}" x2="{x:.1f}" y2="{top + BHT + 5:.1f}" stroke="{TEXT}" '
              f'stroke-width="1" opacity="0.7"/>')
    p.text_px(BX0, top + BHT + 18, "0", TEXT, 11.5, "middle")
    gap_lbl = "mutlak hata |" + it("p") + " " + MINUS + " " + PSTAR + "| = " + dec(ps - pv)
    if xs - xe > 40:
        p.text_px(xe, top + BHT + 18, it("p"), THEORY, 12, "middle")
        p.text_px(xs, top + BHT + 18, PSTAR, PRACTICE, 12, "middle")
        brace(p, xe, xs, top - 4, 9, PRACTICE, up=True)
        p.text_px(xs, top - 18, gap_lbl, PRACTICE, 12, "end")
    else:
        p.text_px(xe - 4, top + BHT + 18, it("p"), THEORY, 12, "end")
        p.text_px(xs + 4, top + BHT + 18, PSTAR, PRACTICE, 12, "start")
        p.add(f'<line x1="{xs - 1:.1f}" y1="{top - 22:.1f}" x2="{xs - 1:.1f}" y2="{top - 9:.1f}" '
              f'stroke="{PRACTICE}" stroke-width="1.2"/>')
        p.add(f'<polygon points="{xs - 1:.1f},{top - 2:.1f} {xs - 4.5:.1f},{top - 10:.1f} {xs + 2.5:.1f},'
              f'{top - 10:.1f}" fill="{PRACTICE}"/>')
        p.text_px(xs - 8, top - 18, gap_lbl, PRACTICE, 12, "end")
    rel = (ps - pv) / pv
    p.text_px(BX0 + BL, top + BHT + 40, "bağıl hata " + dec(ps - pv) + "/" + dec(pv) + " = " + dec(rel)
              + " (yüzde " + dec(100 * rel) + ")", PRACTICE, 12.5, "end", True)
save("mutlak-bagil", figure(
    520, 260, [p],
    "Aynı mutlak hata, iki farklı büyüklükte. Mavi çubuk <em>p</em>, turuncu parça |<em>p</em> &#8722; "
    "<em>p</em>*| = 0,5 mutlak hatasıdır; her satır kendi ölçeğinde çizilmiştir. <em>p</em> = 2 iken hata "
    "çubuğun dörtte biri kadardır (bağıl hata 0,25). <em>p</em> = 100 iken aynı hata ancak ince bir çizgidir "
    "(bağıl hata 0,005).",
    aria="Two bars drawn each to its own scale: p = 2 with p* = 2.5, where the absolute error 0.5 is a quarter "
         "of the bar and the relative error is 0.25, and p = 100 with p* = 100.5, where the same absolute error "
         "is a thin sliver and the relative error is 0.005"))

# ============================================================
# ieee-bitler: the 64 bits of the worked example, s | c | m
# ============================================================
BITS = "0" + "10000000011" + "1011100100010000000000000000000000000000000000000000"
assert len(BITS) == 64
BW, BH, GAP, X0 = 8.4, 18.0, 10.0, 40.0
TOP = 44.0


def bx(i):
    """Left edge of box i (0 = s, 1..11 = c_10..c_0, 12..63 = m_51..m_0)."""
    return X0 + i * BW + GAP * (i >= 1) + GAP * (i >= 12)


def bc(i):
    return bx(i) + BW / 2


W1 = int(bx(63) + BW + 40)
p = pixel_plot(W1, 200)
REGION = [(range(0, 1), REMARK), (range(1, 12), THEORY), (range(12, 64), PRACTICE)]
for idx, color in REGION:
    for i in idx:
        one = BITS[i] == "1"
        p.add(f'<rect x="{bx(i):.1f}" y="{TOP:.1f}" width="{BW:.1f}" height="{BH:.1f}" fill="{color}" '
              f'fill-opacity="{0.42 if one else 0.1}" stroke="{color}" stroke-width="0.7"/>')
        p.text_px(bc(i), TOP + 13, BITS[i], TEXT, 10, "middle", one)
# bit indices above the strip
p.text_px(bc(0), TOP - 7, it("s"), REMARK, 10.5, "middle")
p.text_px(bc(1), TOP - 7, it("c") + sub("10"), THEORY, 10.5, "middle")
p.text_px(bc(11), TOP - 7, it("c") + sub("0"), THEORY, 10.5, "middle")
p.text_px(bc(12), TOP - 7, it("m") + sub("51"), PRACTICE, 10.5, "middle")
p.text_px(bc(63), TOP - 7, it("m") + sub("0"), PRACTICE, 10.5, "middle")
# place values of the 1 bits, fanned out with leaders
WEIGHTS = [(1, "2" + sup("10"), 0, THEORY), (10, "2" + sup("1"), -12, THEORY), (11, "2" + sup("0"), 0, THEORY),
           (12, "1/2", 12, PRACTICE), (14, "1/8", 30, PRACTICE), (15, "1/16", 58, PRACTICE),
           (16, "1/32", 88, PRACTICE), (19, "1/256", 102, PRACTICE), (23, "1/4096", 114, PRACTICE)]
LEAD0, LEAD1, WY = TOP + BH + 2, TOP + BH + 22, TOP + BH + 35
for i, s, off, color in WEIGHTS:
    p.add(f'<line x1="{bc(i):.1f}" y1="{LEAD0:.1f}" x2="{bc(i) + off:.1f}" y2="{LEAD1:.1f}" '
          f'stroke="{color}" stroke-width="0.8" opacity="0.7"/>')
    p.text_px(bc(i) + off, WY, s, color, 11, "middle")
# braces with the field names
BY = WY + 12
for idx, color, name in ((range(0, 1), REMARK, it("s") + " (1 bit)"),
                         (range(1, 12), THEORY, it("c") + " (11 bit)"),
                         (range(12, 64), PRACTICE, it("m") + " (52 bit)")):
    a, b = bx(idx[0]), bx(idx[-1]) + BW
    brace(p, a, b, BY, 10, color)
    p.text_px((a + b) / 2, BY + 25, name, color, 11.5, "middle", True)
p.text_px((bx(0) + bx(63) + BW) / 2, BY + 52,
          it("s") + " = 0,   " + it("c") + " = 1027,   " + it("r") + " = 2" + sup("4") + " (1 + " + it("m") +
          ") = 27,56640625", TEXT, 12.5, "middle")
save("ieee-bitler", figure(
    W1, int(BY + 66), [p],
    "Örnekteki 64 bitlik makine sayısı. İlk bit işaret biti <em>s</em>, sonraki 11 bit karakteristik "
    "<em>c</em>, kalan 52 bit mantis <em>m</em>'dir. 1 olan bitlerin altında basamak ağırlıkları "
    "yazılıdır: <em>c</em> = 2<sup>10</sup> + 2 + 1 = 1027 ve <em>m</em> = 1/2 + 1/8 + 1/16 + 1/32 + "
    "1/256 + 1/4096.",
    aria="A strip of 64 bit boxes split into the sign bit s, the 11 bit characteristic c and the 52 bit "
         "mantissa m, with the place values of the one bits written below and the decoded value "
         "r = 2^4 (1 + m) = 27.56640625", css_class=WIDE))

# ============================================================
# normalize-dagilim: 2-digit normalized numbers with n = 0 and n = 1
# ============================================================
W2 = 640
p = pixel_plot(W2, 260)
AX0, AX1 = 70.0, 590.0
AY = 84.0                                   # top row
BY0, BY1 = 70.0, 590.0
BAY = 214.0                                 # bottom row (zoom of [0, 1.2])


def tx(v):
    return AX0 + v / 10 * (AX1 - AX0)


def zx(v):
    return BY0 + v / 1.2 * (BY1 - BY0)


def tick(x, y, h, color, width=1.0, opacity=0.9):
    p.add(f'<line x1="{x:.2f}" y1="{y - h:.1f}" x2="{x:.2f}" y2="{y:.1f}" stroke="{color}" '
          f'stroke-width="{width}" opacity="{opacity}"/>')


def number_axis(x0, x1, y):
    p.add(f'<line x1="{x0 - 6:.1f}" y1="{y:.1f}" x2="{x1 + 10:.1f}" y2="{y:.1f}" stroke="{TEXT}" '
          f'stroke-width="1.1" opacity="0.55"/>')
    p.add(f'<polygon points="{x1 + 16:.1f},{y:.1f} {x1 + 8:.1f},{y - 3.5:.1f} {x1 + 8:.1f},{y + 3.5:.1f}" '
          f'fill="{TEXT}" opacity="0.55"/>')


n0 = [k / 100 for k in range(10, 100)]      # 0,10 ... 0,99
n1 = [k / 10 for k in range(10, 100)]       # 1,0 ... 9,9
assert len(n0) == 90 and len(n1) == 90
# top row
number_axis(AX0, AX1, AY)
for v in n0:
    tick(tx(v), AY, 12, THEORY, 0.6)
for v in n1:
    tick(tx(v), AY, 12, PRACTICE, 1.0)
for k in range(11):
    p.add(f'<line x1="{tx(k):.1f}" y1="{AY:.1f}" x2="{tx(k):.1f}" y2="{AY + 4:.1f}" stroke="{TEXT}" '
          f'stroke-width="1" opacity="0.6"/>')
    p.text_px(tx(k), AY + 17, str(k), TEXT, 11, "middle")
brace(p, tx(0.10), tx(0.99), AY - 16, 9, THEORY, up=True)
p.text_px((tx(0.10) + tx(0.99)) / 2, AY - 31, it("n") + " = 0: aralık 0,01", THEORY, 11.5, "middle", True)
brace(p, tx(1.0), tx(9.9), AY - 16, 9, PRACTICE, up=True)
p.text_px((tx(1.0) + tx(9.9)) / 2, AY - 31, it("n") + " = 1: aralık 0,1", PRACTICE, 11.5, "middle", True)
# zoom wedge from [0, 1.2] of the top row to the bottom row
p.add(f'<polygon points="{tx(0):.1f},{AY + 24:.1f} {tx(1.2):.1f},{AY + 24:.1f} {BY1:.1f},{BAY - 48:.1f} '
      f'{BY0:.1f},{BAY - 48:.1f}" fill="{TEXT}" fill-opacity="0.035" stroke="{TEXT}" stroke-opacity="0.3" '
      f'stroke-width="0.8" stroke-dasharray="4 3"/>')
p.add(f'<line x1="{tx(0):.1f}" y1="{AY - 1:.1f}" x2="{tx(1.2):.1f}" y2="{AY - 1:.1f}" stroke="{TEXT}" '
      f'stroke-width="2.4" opacity="0.35"/>')
# bottom row
p.add(f'<rect x="{zx(0):.1f}" y="{BAY - 22:.1f}" width="{zx(0.1) - zx(0):.1f}" height="22" fill="{TEXT}" '
      f'fill-opacity="0.07" stroke="none"/>')
for k in range(-4, 12):                    # hatching, clipped by hand to the rectangle
    x_a = zx(0) + k * 6
    pts = [(x_a, BAY), (x_a + 22, BAY - 22)]
    (xa, ya), (xb, yb) = pts
    lo, hi = zx(0), zx(0.1)
    if xb < lo or xa > hi:
        continue
    if xa < lo:
        ya -= lo - xa
        xa = lo
    if xb > hi:
        yb += xb - hi
        xb = hi
    p.add(f'<line x1="{xa:.1f}" y1="{ya:.1f}" x2="{xb:.1f}" y2="{yb:.1f}" stroke="{TEXT}" stroke-width="0.7" '
          f'opacity="0.35"/>')
number_axis(BY0, BY1, BAY)
for v in n0:
    tick(zx(v), BAY, 12, THEORY, 1.0)
for v in (1.0, 1.1):
    tick(zx(v), BAY, 12, PRACTICE, 1.6)
for k in range(13):
    p.add(f'<line x1="{zx(k / 10):.1f}" y1="{BAY:.1f}" x2="{zx(k / 10):.1f}" y2="{BAY + 4:.1f}" stroke="{TEXT}" '
          f'stroke-width="1" opacity="0.6"/>')
    p.text_px(zx(k / 10), BAY + 17, dec(k / 10), TEXT, 11, "middle")
p.text_px(zx(0) + 2, BAY - 30, "normalize sayı yok", TEXT, 11, "start")
save("normalize-dagilim", figure(
    W2, int(BAY + 30), [p],
    "İki basamaklı (<em>k</em> = 2) pozitif normalize sayılar. Üstte [0, 10] aralığı: <em>n</em> = 0 için "
    "0,10; 0,11; …; 0,99 sayıları [0,1; 1) içine sıkışır, <em>n</em> = 1 için 1,0; 1,1; …; 9,9 sayıları "
    "0,1 aralıkla dizilir. Altta [0; 1,2] parçasının büyütmesi: 0 ile 0,10 arasında normalize sayı yoktur.",
    aria="Two number lines. Top: 0 to 10 with the 90 numbers 0.10 to 0.99 packed in blue ticks and the 90 "
         "numbers 1.0 to 9.9 spaced 0.1 apart in orange ticks. Bottom: a zoom of 0 to 1.2 showing the blue "
         "ticks 0.01 apart, orange ticks at 1.0 and 1.1 and an empty hatched gap between 0 and 0.10"))

# ============================================================
# kn-basamak: 5-digit chopping and rounding near pi
# ============================================================
XR = (3.14128, 3.14182)
SZ = 380
p = Plot(80, 40, SZ, SZ, XR, XR)
H = 0.0001
# frame axes, ticks, labels
p.add(f'<g stroke="{TEXT}" stroke-width="1.1" opacity="0.5">'
      f'<line x1="{p.x0:.1f}" y1="{p.y0 + SZ:.1f}" x2="{p.x0 + SZ + 8:.1f}" y2="{p.y0 + SZ:.1f}"/>'
      f'<line x1="{p.x0:.1f}" y1="{p.y0 - 8:.1f}" x2="{p.x0:.1f}" y2="{p.y0 + SZ:.1f}"/></g>')
TICKS = (3.1414, 3.1415, 3.1416, 3.1417)
p.grid(TICKS, TICKS)
for t in TICKS:
    p.add(f'<line x1="{p.X(t):.1f}" y1="{p.y0 + SZ:.1f}" x2="{p.X(t):.1f}" y2="{p.y0 + SZ + 4:.1f}" '
          f'stroke="{TEXT}" opacity="0.6"/>')
    p.add(f'<line x1="{p.x0 - 4:.1f}" y1="{p.Y(t):.1f}" x2="{p.x0:.1f}" y2="{p.Y(t):.1f}" stroke="{TEXT}" '
          f'opacity="0.6"/>')
    p.text_px(p.X(t), p.y0 + SZ + 17, dec(t), TEXT, 11, "middle")
    p.text_px(p.x0 - 8, p.Y(t) + 4, dec(t), TEXT, 11, "end")
p.text_px(p.x0 + SZ + 14, p.y0 + SZ + 4, it("y"), TEXT, 12.5)
p.text_px(p.x0, p.y0 - 14, "KN(" + it("y") + ")", TEXT, 12.5, "middle")
p.line([(XR[0], XR[0]), (XR[1], XR[1])], TEXT, 1.0, "5 4", 0.45)


def step(a, b, v, color, closed_left=True, open_right=True):
    p.line([(a, v), (b, v)], color, 2.4)
    if closed_left:
        p.points([(a, v)], color, 3.4)
    if open_right:
        p.add(f'<circle cx="{p.X(b):.1f}" cy="{p.Y(v):.1f}" r="3.4" fill="{BG}" stroke="{color}" '
              f'stroke-width="1.6"/>')


# the values at y = pi, under the step end markers
PI = math.pi
for v, color in ((3.1415, THEORY), (3.1416, PRACTICE)):
    p.add(f'<circle cx="{p.X(PI):.1f}" cy="{p.Y(v):.1f}" r="5.2" fill="{color}" stroke="{BG}" '
          f'stroke-width="1.2"/>')
# 5-digit rounding (orange): [a - 0.00005, a + 0.00005) -> a; partial steps cut at the frame
step(XR[0], 3.14135, 3.1413, PRACTICE, closed_left=False)
for a in (3.1414, 3.1415, 3.1416, 3.1417):
    step(a - H / 2, a + H / 2, a, PRACTICE)
step(3.14175, XR[1], 3.1418, PRACTICE, open_right=False)
# 5-digit chopping (blue): [a, a + 0.0001) -> a
for a in (3.1413, 3.1414, 3.1415, 3.1416, 3.1417):
    step(a, a + H, a, THEORY)
# y = pi
p.line([(PI, XR[0]), (PI, XR[1])], TEXT, 1.1, "4 3", 0.7)
p.label(PI, XR[1], it("y") + " = π", 0, -6, TEXT, 12, "middle")
p.label(PI, 3.1415, "kesme: 3,1415", 9, 18, THEORY, 12, "start", True)
p.label(PI, 3.1416, "yuvarlama: 3,1416", -9, -10, PRACTICE, 12, "end", True)
# legend
LX, LY = p.x0 + 14, p.y0 + 18
for k, (color, name) in enumerate(((THEORY, "5-basamak kesme"), (PRACTICE, "5-basamak yuvarlama"))):
    y = LY + 20 * k
    p.add(f'<line x1="{LX:.1f}" y1="{y:.1f}" x2="{LX + 26:.1f}" y2="{y:.1f}" stroke="{color}" '
          f'stroke-width="2.4"/>')
    p.text_px(LX + 34, y + 4, name, color, 11.5)
save("kn-basamak", figure(
    int(p.x0 + SZ + 40), int(p.y0 + SZ + 30), [p],
    "π yakınındaki sayıların 5-basamak kesme (mavi) ve 5-basamak yuvarlama (turuncu) ile bulunan "
    "<em>KN</em>(<em>y</em>) değerleri. Basamakların sol ucu dahil, sağ ucu hariçtir; kesikli köşegen "
    "<em>KN</em>(<em>y</em>) = <em>y</em> doğrusudur. Kesme basamakları köşegenin hep altında kalır, "
    "yuvarlama basamakları köşegeni ortalar. <em>y</em> = π doğrusu kesmede 3,1415, yuvarlamada 3,1416 "
    "değerini verir.",
    aria="Two step functions near pi: 5 digit chopping, steps of width 0.0001 below the diagonal, and 5 digit "
         "rounding, steps centred on the diagonal; the vertical line y = pi meets them at 3.1415 and 3.1416"))
