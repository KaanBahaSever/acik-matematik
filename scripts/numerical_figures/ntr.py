# -*- coding: utf-8 -*-
"""
Figures of the chapter "Nümerik Türev"
(dersler/numerik-analiz/numerik-turev.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box and never directly under a heading.
The figures are NOT produced at build time. Run

    python scripts/numerical_figures/ntr.py
    python scripts/center_figures.py "numerical-ntr-*.md"
    python scripts/check_figure_labels.py "scripts/_figures/numerical-ntr-*.md"

and paste the markup of scripts/_figures/numerical-ntr-<name>.md into the .qmd.
Captions are Turkish on purpose; aria labels are plain ASCII.

The error surface rises away from the viewer (the camera looks from the corner
x = 1, h = 0), so no part of it folds over another: the floor curves are
painted faintly before the translucent surface, everything else after it.
"""
import html
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, dot, TEXT, THEORY, PRACTICE, BASE, REMARK, BG, WIDE  # noqa: E402
from svg_plot3 import Camera, Space  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "numerical-ntr-"

MINUS = "&#8722;"
PRIME = "&#8242;"
APPROX = "&#8776;"


def save(name, markup):
    (OUT_DIR / f"{PREFIX}{name}.md").write_text(markup, encoding="utf-8", newline="\n")
    print(f"{PREFIX}{name}.md")


def it(s):
    """Italic run inside an SVG <text>."""
    return f'<tspan font-style="italic">{s}</tspan>'


def sup(s, size=8.5):
    """Superscript inside an SVG <text>."""
    return f'<tspan font-size="{size}" dy="-5">{s}</tspan><tspan dy="5">&#8203;</tspan>'


def sub(s, size=8.5):
    """Subscript inside an SVG <text>."""
    return f'<tspan font-size="{size}" dy="3.5">{s}</tspan><tspan dy="-3.5">&#8203;</tspan>'


def dec(v, digits=2):
    """Decimal comma and a true minus sign: -0.5 -> '−0,5'."""
    s = f"{v:.{digits}f}".rstrip("0").rstrip(".")
    return s.replace(".", ",").replace("-", MINUS)


def text_w(s, size):
    """Rough advance width of a label (0.56 em per visible character)."""
    plain = html.unescape(re.sub(r"<[^>]+>", "", s)).replace("​", "")
    return len(plain) * 0.56 * size


def plate(p, x, y, s, dx=0, dy=0, size=11.5, anchor="start", opacity=0.9):
    """Page-coloured rounded plate under a label that has to sit on lines."""
    px, py = p.X(x) + dx, p.Y(y) + dy
    w = text_w(s, size)
    x0 = px - (w / 2 if anchor == "middle" else w if anchor == "end" else 0)
    p.add(f'<rect x="{x0 - 2.5:.1f}" y="{py - 0.8 * size - 1:.1f}" width="{w + 5:.1f}" '
          f'height="{size + 3:.1f}" rx="3" fill="{BG}" opacity="{opacity}"/>')


def plabel(p, x, y, s, dx=0, dy=0, color=TEXT, size=11.5, anchor="start", bold=False):
    plate(p, x, y, s, dx, dy, size, anchor)
    p.label(x, y, s, dx, dy, color, size, anchor, bold)


def clip_line(p, f, a, b, n=200):
    """Sample y = f(x) on [a, b] and keep the runs inside the panel's y range."""
    runs, cur = [], []
    for k in range(n + 1):
        x = a + (b - a) * k / n
        y = f(x)
        if p.ymin <= y <= p.ymax:
            cur.append((x, y))
        elif cur:
            runs.append(cur)
            cur = []
    if cur:
        runs.append(cur)
    return [r for r in runs if len(r) > 1]


def draw_fn(p, f, a, b, color, width, dash=None, opacity=1.0, n=200):
    for run in clip_line(p, f, a, b, n):
        p.line(run, color, width, dash, opacity)


def frame(p, opacity=0.45):
    """Plain L-shaped axes without tick labels."""
    p.add(f'<g stroke="{TEXT}" stroke-width="1.1" opacity="{opacity}">'
          f'<line x1="{p.x0:.1f}" y1="{p.y0 + p.h:.1f}" x2="{p.x0 + p.w + 8:.1f}" y2="{p.y0 + p.h:.1f}"/>'
          f'<line x1="{p.x0:.1f}" y1="{p.y0 - 8:.1f}" x2="{p.x0:.1f}" y2="{p.y0 + p.h:.1f}"/></g>')


def xtick(p, x, s, size=11, opacity=0.85):
    Y = p.y0 + p.h
    p.add(f'<line x1="{p.X(x):.1f}" y1="{Y - 3:.1f}" x2="{p.X(x):.1f}" y2="{Y + 3:.1f}" '
          f'stroke="{TEXT}" stroke-width="1" opacity="0.6"/>')
    p.add(f'<text x="{p.X(x):.1f}" y="{Y + 17:.1f}" fill="{TEXT}" font-size="{size}" '
          f'text-anchor="middle" opacity="{opacity}">{s}</text>')


def ytick(p, y, s, size=11, opacity=0.75):
    p.add(f'<line x1="{p.x0 - 3:.1f}" y1="{p.Y(y):.1f}" x2="{p.x0 + 3:.1f}" y2="{p.Y(y):.1f}" '
          f'stroke="{TEXT}" stroke-width="1" opacity="0.6"/>')
    p.add(f'<text x="{p.x0 - 7:.1f}" y="{p.Y(y) + 4:.1f}" fill="{TEXT}" font-size="{size}" '
          f'text-anchor="end" opacity="{opacity}">{s}</text>')


def axis_names(p, xname, yname):
    p.text_px(p.x0 + p.w + 14, p.y0 + p.h + 4, xname, TEXT, 12)
    p.text_px(p.x0, p.y0 - 14, yname, TEXT, 12, "middle")


X0 = it("x") + sub("0")
FP = it("f") + PRIME


# ============================================================
# ileri-fark-kirisi: tangent and forward-difference chord of ln x at x0 = 1.8
# ============================================================
x0 = 1.8
f0 = math.log(x0)
slope_t = 1 / x0
H_BIG = 0.5
x1 = x0 + H_BIG
f1 = math.log(x1)
slope_c = (f1 - f0) / H_BIG          # 0.490245


def tangent(x):
    return f0 + slope_t * (x - x0)


PW, PH = 270, 230
pL = Plot(50, 50, PW, PH, (1.4, 2.6), (0.3, 1.0))
frame(pL)
axis_names(pL, it("x"), it("y"))
pL.text_px(pL.x0 + PW / 2, pL.y0 - 26, "Geometri (" + it("h") + " büyütülmüş)", TEXT, 12.5, "middle", True)
# guides from the two points to the x axis
pL.vline(x0, 0.3, f0, TEXT, "4 3", 0.4)
pL.vline(x1, 0.3, f1, TEXT, "4 3", 0.4)
draw_fn(pL, math.log, 1.4, 2.6, TEXT, 2.2)
draw_fn(pL, tangent, 1.4, 2.6, PRACTICE, 1.8)
pL.line([(x0, f0), (x1, f1)], THEORY, 2.2)
pL.points([(x0, f0)], TEXT, 4.2)
pL.points([(x1, f1)], THEORY, 4.2)
xtick(pL, x0, X0)
xtick(pL, x1, X0 + " + " + it("h"))
# h bracket below the tick labels
BY = pL.y0 + PH + 28
xa, xb = pL.X(x0), pL.X(x1)
pL.add(f'<path d="M{xa:.1f},{BY - 5:.1f} L{xa:.1f},{BY:.1f} L{xb:.1f},{BY:.1f} L{xb:.1f},{BY - 5:.1f}" '
       f'fill="none" stroke="{TEXT}" stroke-width="1.1" opacity="0.7"/>')
pL.text_px((xa + xb) / 2, BY + 15, it("h"), TEXT, 12.5, "middle")
# labels
pL.label(2.25, 0.925, "teğet, eğim " + FP + "(" + X0 + ")", 0, 0, PRACTICE, 11.5, "end", True)
pL.label(2.57, 0.80, it("y") + " = ln " + it("x"), 0, 0, TEXT, 12, "end")
CX = 2.05
pL.label(CX, 0.555, "kiriş, eğim", 0, 0, THEORY, 11.5, "middle", True)
num = it("f") + "(" + X0 + " + " + it("h") + ") " + MINUS + " " + it("f") + "(" + X0 + ")"
pL.label(CX, 0.50, num, 0, 0, THEORY, 11, "middle")
wbar = text_w(num, 11) / 2
pL.add(f'<line x1="{pL.X(CX) - wbar:.1f}" y1="{pL.Y(0.50) + 5:.1f}" x2="{pL.X(CX) + wbar:.1f}" '
       f'y2="{pL.Y(0.50) + 5:.1f}" stroke="{THEORY}" stroke-width="1"/>')
pL.label(CX, 0.50, it("h"), 0, 19, THEORY, 11, "middle")

# right panel: the true step h = 0.1
H = 0.1
x1r = x0 + H
f1r = math.log(x1r)
slope_cr = (f1r - f0) / H            # 0.5406722
gap = tangent(x1r) - f1r             # 0.0014883
pR = Plot(50 + PW + 85, 50, PW, PH, (1.78, 1.92), (0.575, 0.655))
pR.grid([1.8, 1.85, 1.9], [0.58, 0.6, 0.62, 0.64])
frame(pR)
axis_names(pR, it("x"), it("y"))
pR.text_px(pR.x0 + PW / 2, pR.y0 - 26, it("h") + " = 0,1", TEXT, 12.5, "middle", True)
for v in (1.8, 1.85, 1.9):
    xtick(pR, v, dec(v), 11, 0.75)
for v in (0.58, 0.6, 0.62, 0.64):
    ytick(pR, v, dec(v))
draw_fn(pR, math.log, 1.78, 1.92, TEXT, 2.2)
draw_fn(pR, tangent, 1.78, 1.92, PRACTICE, 1.6)
pR.line([(x0, f0), (x1r, f1r)], THEORY, 1.8)
pR.points([(x0, f0)], TEXT, 4.0)
pR.points([(x1r, f1r)], THEORY, 3.4)
pR.label(1.825, 0.622, "teğet", 0, 0, PRACTICE, 11.5, "end", True)
pR.label(1.828, 0.592, "kiriş", 0, 0, THEORY, 11.5, "start", True)
# magnifier: a small frame around x = 1.9 and an inset that blows it up
zx, zy = (1.8985, 1.9015), (0.6408, 0.6442)
pR.polygon([(zx[0], zy[0]), (zx[1], zy[0]), (zx[1], zy[1]), (zx[0], zy[1])], BG, 0.0, TEXT, 1.0)
ins = Plot(pR.x0 + 158, pR.y0 + 128, 108, 48, zx, zy)
ins.add(f'<rect x="{ins.x0 - 6:.1f}" y="{ins.y0 - 6:.1f}" width="{ins.w + 12:.1f}" height="{ins.h + 46:.1f}" '
        f'rx="4" fill="{BG}" stroke="{TEXT}" stroke-width="1" stroke-opacity="0.6"/>')
pR.add(f'<line x1="{pR.X(zx[0]):.1f}" y1="{pR.Y(zy[0]):.1f}" x2="{ins.x0 - 6:.1f}" y2="{ins.y0 - 6:.1f}" '
       f'stroke="{TEXT}" stroke-width="0.8" stroke-dasharray="3 2" opacity="0.6"/>')
draw_fn(ins, math.log, zx[0], zx[1], TEXT, 2.0, n=20)
draw_fn(ins, tangent, zx[0], zx[1], PRACTICE, 1.6, n=20)
ins.line([(zx[0], f0 + slope_cr * (zx[0] - x0)), (x1r, f1r)], THEORY, 1.6)
ins.points([(x1r, f1r)], THEORY, 3.0)
ins.points([(x1r, tangent(x1r))], PRACTICE, 3.0)
# vertical gap bracket, slightly right of x = 1.9
gx = ins.X(x1r) + 9
ya, yb = ins.Y(tangent(x1r)), ins.Y(f1r)
ins.add(f'<path d="M{gx - 4:.1f},{ya:.1f} L{gx:.1f},{ya:.1f} L{gx:.1f},{yb:.1f} L{gx - 4:.1f},{yb:.1f}" '
        f'fill="none" stroke="{TEXT}" stroke-width="1.1"/>')
ins.text_px(ins.x0 + ins.w / 2, ins.y0 + ins.h + 18, "fark = 0,0014883", TEXT, 11, "middle")
ins.text_px(ins.x0 + ins.w / 2, ins.y0 + ins.h + 33, APPROX + " " + it("h") + " · hata", TEXT, 11, "middle")

save("ileri-fark-kirisi", figure(
    int(pR.x0 + PW + 40), int(pL.y0 + PH + 60), [pL, pR, ins],
    "<em>f</em>(<em>x</em>) = ln <em>x</em> için <em>x</em><sub>0</sub> = 1,8 noktasındaki teğet ve ileri fark "
    "kirişi. Solda <em>h</em> = 0,5 alınarak abartılmış geometri: konkav eğrinin kirişi teğetten daha az "
    "eğimlidir (0,490245 &lt; 0,555556). Sağda gerçek adım <em>h</em> = 0,1: kirişin eğimi 0,5406722, teğetin "
    "eğimi 0,5555556. Büyütülen kutuda <em>x</em> = 1,9'da teğetin değeri 0,643343 ile ln 1,9 = 0,641854 "
    "arasındaki 0,0014883'lük fark görülür; bu, <em>h</em> ile mutlak hatanın çarpımıdır.",
    css_class=WIDE,
    aria="Two panels with the graph of ln x. Left: tangent at x0 = 1.8 and the chord to x0 + h with an "
         "exaggerated step h = 0.5. Right: the true step h = 0.1, with an inset magnifying the small vertical "
         "gap between the tangent and the curve at x = 1.9"))


# ============================================================
# orta-nokta-kirisi: centred chord of f(x) = x e^x around x0 = 2
# ============================================================
def fx(x):
    return x * math.exp(x)


TAB = {1.9: 12.703199, 2.0: 14.778112, 2.1: 17.148957}
s_mid = (TAB[2.1] - TAB[1.9]) / 0.2      # 22.228790
s_fwd = (TAB[2.1] - TAB[2.0]) / 0.1      # 23.708450
s_true = 3 * math.exp(2)                 # 22.167168

p = Plot(55, 30, 360, 290, (1.75, 2.25), (10, 21))
p.grid([1.8, 1.9, 2.0, 2.1, 2.2], [12, 14, 16, 18, 20])
frame(p)
axis_names(p, it("x"), it("y"))
for v in (12, 14, 16, 18, 20):
    ytick(p, v, str(v))
for v, s in ((1.9, X0 + " " + MINUS + " " + it("h")), (2.0, X0), (2.1, X0 + " + " + it("h"))):
    xtick(p, v, s)
for v in (1.9, 2.0, 2.1):
    p.vline(v, 10, TAB[v], TEXT, "4 3", 0.35)
draw_fn(p, fx, 1.75, 2.25, TEXT, 2.2)
draw_fn(p, lambda x: TAB[2.0] + s_true * (x - 2), 1.75, 2.25, THEORY, 1.8)
draw_fn(p, lambda x: TAB[2.0] + s_mid * (x - 2), 1.84, 2.16, PRACTICE, 1.1, "5 3", 0.9)
draw_fn(p, lambda x: TAB[2.0] + s_fwd * (x - 2), 1.93, 2.17, TEXT, 1.4, "6 4", 0.55)
p.line([(1.9, TAB[1.9]), (2.1, TAB[2.1])], PRACTICE, 2.4)
p.points([(v, TAB[v]) for v in (1.9, 2.0, 2.1)], TEXT, 4.2)
# labels: the centred chord above-left, the tangent below-right, the forward chord on the right
p.label(1.895, 13.35, "orta nokta kirişi", 0, 0, PRACTICE, 11.5, "end", True)
p.label(2.07, 15.0, "teğet, eğim 3" + it("e") + sup("2"), 0, 0, THEORY, 11.5, "start", True)
p.line([(2.18, 15.45), (2.205, 19.05)], THEORY, 0.9, None, 0.8)
p.label(2.205, 17.05, "ileri fark", 0, 0, TEXT, 11.5, "start", True)
p.label(2.205, 17.05, "kirişi", 0, 14, TEXT, 11.5, "start", True)
p.line([(2.2, 17.35), (2.16, 18.4)], TEXT, 0.9, None, 0.6)
# value box in the empty upper-left corner
bx, by = p.X(1.76), p.Y(20.8)
rows = [("orta nokta: 22,228790", PRACTICE), ("ileri fark: 23,708450", TEXT), ("gerçek: 22,167168", THEORY)]
p.add(f'<rect x="{bx:.1f}" y="{by:.1f}" width="150" height="58" rx="4" fill="{BG}" '
      f'stroke="{TEXT}" stroke-width="0.9" stroke-opacity="0.5"/>')
for k, (s, c) in enumerate(rows):
    p.text_px(bx + 8, by + 17 + 16 * k, s, c, 11, "start", c != TEXT)
save("orta-nokta-kirisi", figure(
    int(p.x0 + p.w + 40), int(p.y0 + p.h + 34), [p],
    "<em>f</em>(<em>x</em>) = <em>x</em> e<sup><em>x</em></sup> grafiği ve <em>x</em><sub>0</sub> = 2, "
    "<em>h</em> = 0,1 için tablo noktaları. Orta nokta kirişi (1,9; 12,703199) ile (2,1; 17,148957) "
    "noktalarını birleştirir; kesikli ince çizgi bu kirişin (2; 14,778112)'den geçen paralelidir ve teğetle "
    "neredeyse çakışır. Gri kesikli ileri fark kirişi belirgin biçimde daha diktir. Eğimler kutuda verilmiştir.",
    aria="Graph of x e^x near x = 2 with the table points at 1.9, 2.0 and 2.1, the centred chord, its parallel "
         "through the middle point, the tangent of slope 3 e^2 and the steeper forward difference chord"))


# ============================================================
# hata-loglog: errors of the forward and the centred difference against h
# ============================================================
def fp(x):
    return math.exp(x) * (x + 1)


HS = (0.1, 0.05, 0.025, 0.0125)
e_fwd = [abs((fx(2 + h) - fx(2)) / h - fp(2)) for h in HS]
e_mid = [abs((fx(2 + h) - fx(2 - h)) / (2 * h) - fp(2)) for h in HS]
C1 = 14.7781            # f''(2) / 2
C2 = 6.1575             # f'''(2) / 6

L10 = math.log10
p = Plot(70, 30, 360, 300, (-2.2, -0.6), (-4, 1))
p.grid([L10(v) for v in (0.01, 0.025, 0.05, 0.1)], list(range(-4, 2)))
frame(p)
for v, s in ((0.01, "0,01"), (0.025, "0,025"), (0.05, "0,05"), (0.1, "0,1")):
    xtick(p, L10(v), s, 11, 0.75)
for k in range(-4, 2):
    ytick(p, k, "10" + sup(MINUS + str(-k) if k < 0 else str(k)))
p.text_px(p.x0 + p.w + 14, p.y0 + p.h + 4, it("h"), TEXT, 12.5)
p.text_px(p.x0, p.y0 - 14, "mutlak hata", TEXT, 12, "middle")
# reference lines C1 h and C2 h^2 over the whole window
p.line([(-2.2, L10(C1) - 2.2), (-0.6, L10(C1) - 0.6)], THEORY, 1.1, "5 4", 0.7)
p.line([(-2.2, L10(C2) - 4.4), (-0.6, L10(C2) - 1.2)], PRACTICE, 1.1, "5 4", 0.7)
# data
pf = [(L10(h), L10(e)) for h, e in zip(HS, e_fwd)]
pm = [(L10(h), L10(e)) for h, e in zip(HS, e_mid)]
p.line(pf, THEORY, 2.0)
p.line(pm, PRACTICE, 2.0)
p.points(pf, THEORY, 4.2)
for X, Y in pm:
    p.add(f'<rect x="{p.X(X) - 4:.1f}" y="{p.Y(Y) - 4:.1f}" width="8" height="8" fill="{PRACTICE}"/>')


def slope_triangle(p, xa, xb, f, below, color, label):
    """Right triangle under (below=True) or over the line y = f(x) between xa and xb."""
    ya, yb = f(xa), f(xb)
    corner = (xb, ya) if below else (xa, yb)
    p.polygon([(xa, ya), (xb, yb), corner], color, 0.08, color, 0.9)
    if below:
        p.label(xb, (ya + yb) / 2, label, 6, 4, color, 11.5, "start", True)
        p.label((xa + xb) / 2, ya, "1", 0, 15, color, 11, "middle")
    else:
        p.label(xa, (ya + yb) / 2, label, -6, 4, color, 11.5, "end", True)
        p.label((xa + xb) / 2, yb, "1", 0, -6, color, 11, "middle")


slope_triangle(p, -1.6, -1.2, lambda x: L10(C1) + x, True, THEORY, "1")
slope_triangle(p, -2.0, -1.6, lambda x: L10(C2) + 2 * x, False, PRACTICE, "2")
p.label(-2.15, 0.45, "ileri fark, " + it("O") + "(" + it("h") + ")", 0, 0, THEORY, 12, "start", True)
p.label(-2.15, 0.45, "kesikli: 14,7781 " + it("h") + " (eğim 1)", 0, 16, THEORY, 11)
p.label(-0.65, -2.9, "orta nokta, " + it("O") + "(" + it("h") + sup("2") + ")", 0, 0, PRACTICE, 12, "end", True)
p.label(-0.65, -2.9, "kesikli: 6,1575 " + it("h") + sup("2") + " (eğim 2)", 0, 16, PRACTICE, 11, "end")
save("hata-loglog", figure(
    int(p.x0 + p.w + 40), int(p.y0 + p.h + 34), [p],
    "<em>f</em>(<em>x</em>) = <em>x</em> e<sup><em>x</em></sup> için <em>f</em>'(2) yaklaşımlarının mutlak "
    "hataları, log–log ölçekte. Daireler ileri fark, kareler orta nokta formülüdür; <em>h</em> = 0,1; 0,05; "
    "0,025; 0,0125. Kesikli doğrular 14,7781 <em>h</em> ve 6,1575 <em>h</em>² referanslarıdır. İleri fark "
    "hataları eğimi 1, orta nokta hataları eğimi 2 olan doğru üzerinde dizilir.",
    aria="Log-log plot of the absolute errors of the forward difference and the centred difference for "
         "the derivative of x e^x at 2, for h from 0.0125 to 0.1, with dashed reference lines of slope 1 and 2"))


# ============================================================
# ileri-fark-hata-yuzeyi: E(x, h) = (f(x + h) - f(x)) / h - f'(x) over [1, 3] x [0.01, 0.2]
# ============================================================
def E(x, h):
    return (fx(x + h) - fx(x)) / h - fp(x)


ZS = 5.5      # display scale: X = x - 1, Y = 10 h, Z = z / ZS


def P(x, h, z):
    return (x - 1.0, 10.0 * h, z / ZS)


def surf(x, h):
    return P(x, h, E(x, h))


cam = Camera(azimuth=222.0, elevation=24.0, center=(1.0, 1.0, 1.0))


def eq_plot(x0_, y0_, ppu, xr, yr):
    return Plot(x0_, y0_, (xr[1] - xr[0]) * ppu, (yr[1] - yr[0]) * ppu, xr, yr)


XA, HA, ZA = 3.4, 0.235, 12.2
corners = [surf(x, h) for x in (1, 3) for h in (0.01, 0.2)]
corners += [P(XA, 0, 0), P(1, HA, 0), P(1, 0, ZA), P(3, 0.2, 0), P(1, 0, 0)]
q = [cam.project(c)[:2] for c in corners]
pad = 0.3
xr = (min(a for a, _ in q) - pad, max(a for a, _ in q) + pad)
yr = (min(b for _, b in q) - pad, max(b for _, b in q) + 0.15)
pl = eq_plot(40, 30, 118, xr, yr)
S = Space(pl, cam)

# floor: the domain rectangle and the approximate level curves E = c
dom = [P(1, 0.01, 0), P(3, 0.01, 0), P(3, 0.2, 0), P(1, 0.2, 0), P(1, 0.01, 0)]
S.line(dom, TEXT, 0.9, "3 3", 0.45)


def level_h(c, x):
    """h in [0.01, 0.2] with E(x, h) = c (E increases with h), or None."""
    lo, hi = 0.01, 0.2
    if not (E(x, lo) <= c <= E(x, hi)):
        return None
    for _ in range(60):
        m = (lo + hi) / 2
        if E(x, m) < c:
            lo = m
        else:
            hi = m
    return (lo + hi) / 2


LEVELS = (0.5, 1.0, 2.0, 4.0)
level_tags = []
for c in LEVELS:
    pts = []
    for k in range(401):
        x = 1 + 2 * k / 400
        h = level_h(c, x)
        if h is not None:
            pts.append(P(x, h, 0))
    S.line(pts, BASE, 1.3, None, 0.85)
    level_tags.append((c, pts[0]))

# the surface
S.surface(surf, (1, 3), (0.01, 0.2), nu=24, nv=12, fill=THEORY, stroke=THEORY,
          opacity=(0.06, 0.22), stroke_width=0.3, stroke_opacity=0.08)
# sparse wire net: x = 1, 1.5, ..., 3 and h = 0.01, 0.05, 0.1, 0.15, 0.2
for k in range(5):
    xv = 1 + 0.5 * k
    S.curve(lambda t, xv=xv: surf(xv, t), 0.01, 0.2, THEORY, 0.7, 40, None, 0.55)
for hv in (0.01, 0.05, 0.1, 0.15, 0.2):
    S.curve(lambda t, hv=hv: surf(t, hv), 1, 3, THEORY, 0.7, 80, None, 0.55)
# axes from the corner x = 1, h = 0, z = 0
O = P(1, 0, 0)
S.arrow(O, P(XA, 0, 0), TEXT, 1.1, 7.0, None, 0.6)
S.arrow(O, P(1, HA, 0), TEXT, 1.1, 7.0, None, 0.6)
S.arrow(P(1, 0.2, 0), P(1, 0.2, ZA), TEXT, 1.1, 7.0, None, 0.6)
S.label(P(XA, 0, 0), it("x"), 10, 12, TEXT, 12.5, "middle")
S.label(P(1, HA, 0), it("h"), -10, 12, TEXT, 12.5, "middle")
S.label(P(1, 0.2, ZA), "hata", 0, -8, TEXT, 12, "middle")
for v in (2, 3):
    S.line([P(v, 0, 0), P(v, -0.012, 0)], TEXT, 1.0, None, 0.7)
    S.label(P(v, 0, 0), dec(v), 2, 15, TEXT, 10.5, "middle")
S.label(P(1, 0, 0), "1", 6, 15, TEXT, 10.5, "middle")
for v in (0.1, 0.2):
    S.line([P(1, v, 0), P(0.94, v, 0)], TEXT, 1.0, None, 0.7)
    S.label(P(1, v, 0), dec(v), -8, 14, TEXT, 10.5, "middle")
for v in (5, 10):
    S.line([P(1, 0.2, v), P(0.94, 0.2, v)], TEXT, 1.0, None, 0.7)
    S.label(P(1, 0.2, v), str(v), -9, 4, TEXT, 10.5, "end")
# highlighted cuts h = 0.1 and x = 2 and their crossing
S.curve(lambda t: surf(t, 0.1), 1, 3, PRACTICE, 2.4, 120)
S.curve(lambda t: surf(2.0, t), 0.01, 0.2, PRACTICE, 2.4, 60)
Pc = surf(2.0, 0.1)
S.point(Pc, TEXT, 4.4)
X, Y = S.pt(Pc)
plabel(pl, X, Y, X0 + " = 2, " + it("h") + " = 0,1", 10, 4, TEXT, 11.5, "start")
# level tags at the h = 0.2 (or x = 1) end of each floor curve, outside the domain
for c, end in level_tags:
    if c == 0.5:      # starts on the h axis: tag it inline at x = 1.5 instead
        X, Y = S.pt(P(1.5, level_h(c, 1.5), 0))
        plabel(pl, X, Y, dec(c), 0, 4, BASE, 10.5, "middle", True)
    else:
        S.label(end, dec(c), 1, -7, BASE, 10.5, "middle", True)
save("ileri-fark-hata-yuzeyi", figure(
    int(pl.x0 + pl.w + 30), int(pl.y0 + pl.h + 30), [pl],
    "İleri fark hatası <em>E</em>(<em>x</em>, <em>h</em>) = [<em>f</em>(<em>x</em> + <em>h</em>) &#8722; "
    "<em>f</em>(<em>x</em>)]/<em>h</em> &#8722; <em>f</em>'(<em>x</em>), <em>f</em>(<em>x</em>) = "
    "<em>x</em> e<sup><em>x</em></sup>, 1 &#8804; <em>x</em> &#8804; 3, 0,01 &#8804; <em>h</em> &#8804; 0,2. "
    "Yüzey <em>h</em> yönünde neredeyse doğrusal, <em>x</em> yönünde üstel büyür: en küçük değer yaklaşık "
    "0,041 (<em>x</em> = 1, <em>h</em> = 0,01), en büyük değer yaklaşık 10,9 (<em>x</em> = 3, <em>h</em> = 0,2). "
    "Vurgulu eğriler <em>h</em> = 0,1 ve <em>x</em> = 2 kesitleridir; kesişimlerinde hata 1,5412779'dur. "
    "Tabandaki eğriler yaklaşık eşit hata eğrileridir (0,5; 1; 2; 4).",
    aria="Surface of the forward difference error for x e^x over x from 1 to 3 and h from 0.01 to 0.2, "
         "growing linearly in h and exponentially in x, with the cuts h = 0.1 and x = 2 highlighted, their "
         "crossing marked, and level curves 0.5, 1, 2, 4 on the floor"))

# ============================================================
# uc-kiris: tangent at x_0 and the forward, backward and centred chords of a convex curve
# ============================================================
def gf(x):
    return 0.6 * math.exp(x)


GX0, GH = 1.3, 0.65
g_true = 0.6 * math.exp(GX0)
g_fwd = (gf(GX0 + GH) - gf(GX0)) / GH
g_bwd = (gf(GX0) - gf(GX0 - GH)) / GH
g_mid = (gf(GX0 + GH) - gf(GX0 - GH)) / (2 * GH)
# the centred slope is much closer to the true one than the one-sided slopes
assert abs(g_mid - g_true) < 0.35 * min(abs(g_fwd - g_true), abs(g_bwd - g_true))

p = Plot(50, 30, 400, 290, (0, 2.6), (0, 6.2))
frame(p)
axis_names(p, it("x"), it("y"))
for v, s_ in ((GX0 - GH, X0 + " " + MINUS + " " + it("h")), (GX0, X0), (GX0 + GH, X0 + " + " + it("h"))):
    p.vline(v, 0, gf(v), TEXT, "4 3", 0.4)
    xtick(p, v, s_, 12)


def through(x1, y1, m):
    return lambda x: y1 + m * (x - x1)


draw_fn(p, gf, 0.05, 2.5, TEXT, 2.6)
draw_fn(p, through(GX0, gf(GX0), g_true), GX0 - GH - 0.35, GX0 + GH + 0.35, THEORY, 2.2)
draw_fn(p, through(GX0, gf(GX0), g_fwd), GX0 - 0.25, GX0 + GH + 0.3, PRACTICE, 1.8, "8 4")
draw_fn(p, through(GX0, gf(GX0), g_bwd), GX0 - GH - 0.3, GX0 + 0.35, REMARK, 1.8, "2 3")
draw_fn(p, through(GX0 - GH, gf(GX0 - GH), g_mid), GX0 - GH - 0.2, GX0 + GH + 0.2, BASE, 2.2)
for v in (GX0 - GH, GX0, GX0 + GH):
    dot(p, (v, gf(v)), TEXT, 4.4)
XTOP = math.log(6.2 / 0.6)
p.label(XTOP, 6.2, it("y") + " = " + it("f") + "(" + it("x") + ")", 9, 12, TEXT, 12.5, "start", True)
# key in the empty upper-left corner
KEY = [(THEORY, None, 2.2, "teğet, eğim " + FP + "(" + X0 + ")"),
       (PRACTICE, "8 4", 1.8, "ileri fark kirişi"),
       (REMARK, "2 3", 1.8, "geri fark kirişi"),
       (BASE, None, 2.2, "orta nokta kirişi")]
kx, ky = p.x0 + 14, p.y0 + 6
p.add(f'<rect x="{kx:.1f}" y="{ky:.1f}" width="178" height="{18 * len(KEY) + 10}" rx="4" fill="{BG}" '
      f'stroke="{TEXT}" stroke-width="0.8" stroke-opacity="0.35"/>')
for k, (c, dash, w, s_) in enumerate(KEY):
    yy = ky + 16 + 18 * k
    da = f' stroke-dasharray="{dash}"' if dash else ""
    p.add(f'<line x1="{kx + 9:.1f}" y1="{yy - 4:.1f}" x2="{kx + 37:.1f}" y2="{yy - 4:.1f}" stroke="{c}" '
          f'stroke-width="{w}"{da}/>')
    p.text_px(kx + 44, yy, s_, c, 11.5, "start", c in (THEORY, BASE))
save("uc-kiris", figure(
    int(p.x0 + p.w + 110), int(p.y0 + p.h + 40), [p],
    "<em>x</em><sub>0</sub> noktasındaki teğet ve üç kiriş. İleri fark kirişi <em>x</em><sub>0</sub> ile "
    "<em>x</em><sub>0</sub> + <em>h</em>'yi, geri fark kirişi <em>x</em><sub>0</sub> &#8722; <em>h</em> ile "
    "<em>x</em><sub>0</sub>'ı, orta nokta kirişi <em>x</em><sub>0</sub> &#8722; <em>h</em> ile "
    "<em>x</em><sub>0</sub> + <em>h</em>'yi birleştirir. Tek yanlı kirişlerden biri teğetten dik, öteki yatık "
    "kalır; orta nokta kirişi ise teğete neredeyse paraleldir.",
    aria="A convex curve with the points at x0 - h, x0 and x0 + h, the tangent at x0, the steeper forward "
         "difference chord, the flatter backward difference chord and the centred chord from x0 - h to x0 + h, "
         "which is almost parallel to the tangent"))
