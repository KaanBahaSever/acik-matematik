# -*- coding: utf-8 -*-
"""
Figures of the chapter "Vektörizasyon ve Broadcasting"
(dersler/python-bilimsel/vektorizasyon-ve-broadcasting.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box and never directly under a heading;
concept figures stay visible (not inside a collapsed .cozum block).
The figures are NOT produced at build time. Run

    python scripts/python_figures/vek.py
    python scripts/center_figures.py "python-vek-*.md"
    python scripts/check_figure_labels.py "scripts/_figures/python-vek-*.md"

and paste the markup of scripts/_figures/python-vek-<name>.md into the .qmd.
Every figure is drawn from the same data the chapter's code computes (the
random points use the same generator and seed). Captions are Turkish on
purpose; aria labels are plain ASCII.
"""
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import (Plot, figure, WIDE, TEXT, THEORY, PRACTICE,  # noqa: E402
                      BASE, REMARK, BG)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "python-vek-"

MINUS = "&#8722;"
ARROW = "&#8594;"


def save(name, markup):
    (OUT_DIR / f"{PREFIX}{name}.md").write_text(markup, encoding="utf-8",
                                                newline="\n")
    print(f"{PREFIX}{name}.md")


def it(s):
    """Italic run inside an SVG <text>."""
    return f'<tspan font-style="italic">{s}</tspan>'


def sup(s, size=8.5):
    """Superscript inside an SVG <text>."""
    return (f'<tspan font-size="{size}" dy="-5">{s}</tspan>'
            f'<tspan dy="5">&#8203;</tspan>')


def dec(v, digits=2):
    """Decimal comma and a true minus sign: -0.5 -> '−0,50'."""
    s = f"{v:.{digits}f}"
    return s.replace(".", ",").replace("-", MINUS)


def canvas(W, H):
    """A Plot whose data coordinates are the pixel coordinates (y down)."""
    return Plot(0, 0, W, H, (0, W), (H, 0))


def rect(p, x, y, w, h, fill="none", fop=0.0, stroke=TEXT, sw=1.0,
         sop=0.55, dash=None):
    da = f' stroke-dasharray="{dash}"' if dash else ""
    p.add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
          f'fill="{fill}" fill-opacity="{fop}" stroke="{stroke}" '
          f'stroke-width="{sw}" stroke-opacity="{sop}"{da}/>')


def txt(p, x, y, s, color=TEXT, size=12, anchor="middle", bold=False,
        opacity=1.0):
    weight = ' font-weight="600"' if bold else ""
    op = f' opacity="{opacity}"' if opacity != 1.0 else ""
    p.add(f'<text x="{x:.1f}" y="{y:.1f}" fill="{color}" font-size="{size}" '
          f'text-anchor="{anchor}"{weight}{op}>{s}</text>')


def matrix(p, x0, y0, M, cw, ch, fill="none", fop=0.0, stroke=TEXT,
           color=TEXT, size=12, bold=False, dash=None, opacity=1.0, sop=0.55):
    """Draw the 2D array M as a grid of cells with its entries."""
    M = np.atleast_2d(M)
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            x, y = x0 + j * cw, y0 + i * ch
            rect(p, x, y, cw, ch, fill, fop, stroke, 1.0, sop, dash)
            txt(p, x + cw / 2, y + ch / 2 + size * 0.36, str(M[i, j]),
                color, size, "middle", bold, opacity)


# ============================================================
# axis: A.sum(axis=0) and A.sum(axis=1) for A = np.arange(12).reshape(3, 4)
# ============================================================
A = np.arange(12).reshape(3, 4)
CW, CH = 40, 32
p = canvas(660, 270)

# left panel: axis=0, the column sums
LX, LY = 92, 62
txt(p, LX + 2 * CW, 30, "A.sum(axis=0)", TEXT, 13, bold=True)
rect(p, LX, LY, CW, 3 * CH, THEORY, 0.10, "none", 0)
matrix(p, LX, LY, A, CW, CH)
# the axis-0 direction: down the rows
p.arrow((LX - 16, LY + 4), (LX - 16, LY + 3 * CH - 4), TEXT, 1.3, 7.0,
        None, 0.75)
txt(p, LX - 24, LY + 1.5 * CH + 4, "eksen 0", TEXT, 11.5, "end")
for j in range(4):
    xc = LX + j * CW + CW / 2
    p.arrow((xc, LY + 3 * CH + 5), (xc, LY + 3 * CH + 29), THEORY, 1.6, 7.0)
RY = LY + 3 * CH + 34
matrix(p, LX, RY, A.sum(axis=0)[None, :], CW, CH, PRACTICE, 0.12, PRACTICE,
       PRACTICE, 12, True, sop=0.9)
txt(p, LX + 2 * CW, RY + CH + 22, "(3, 4) " + ARROW + " (4,)", TEXT, 12)

# right panel: axis=1, the row sums
RX, RYY = 400, 62
txt(p, RX + 2 * CW + 24, 30, "A.sum(axis=1)", TEXT, 13, bold=True)
rect(p, RX, RYY, 4 * CW, CH, THEORY, 0.10, "none", 0)
matrix(p, RX, RYY, A, CW, CH)
# the axis-1 direction: across the columns
p.arrow((RX + 4, RYY + 3 * CH + 16), (RX + 4 * CW - 4, RYY + 3 * CH + 16),
        TEXT, 1.3, 7.0, None, 0.75)
txt(p, RX + 2 * CW, RYY + 3 * CH + 36, "eksen 1", TEXT, 11.5)
for i in range(3):
    yc = RYY + i * CH + CH / 2
    p.arrow((RX + 4 * CW + 5, yc), (RX + 4 * CW + 29, yc), THEORY, 1.6, 7.0)
CX = RX + 4 * CW + 34
matrix(p, CX, RYY, A.sum(axis=1)[:, None], CW, CH, PRACTICE, 0.12, PRACTICE,
       PRACTICE, 12, True, sop=0.9)
txt(p, RX + (5 * CW + 34) / 2, RY + CH + 22, "(3, 4) " + ARROW + " (3,)",
    TEXT, 12)

save("axis", figure(
    660, 270, [p],
    "<em>A</em> = np.arange(12).reshape(3, 4) matrisinde iki indirgeme. "
    "Solda <code>axis=0</code>: toplama 0. eksen boyunca, yani satırlar "
    "üzerinden yapılır, her sütun tek sayıya iner (ilk sütun 0 + 4 + 8 = 12) "
    "ve sonuç (4,) şeklindedir. Sağda <code>axis=1</code>: her satır tek "
    "sayıya iner (ilk satır 0 + 1 + 2 + 3 = 6) ve sonuç (3,) şeklindedir. "
    "Adı verilen eksen sonuçtan kaybolur.",
    WIDE,
    aria="A 3 by 4 matrix with entries 0 to 11 drawn twice. Left: arrows "
         "down each column give the column sums 12 15 18 21, shape (4,). "
         "Right: arrows along each row give the row sums 6 22 38, shape "
         "(3,)."))

# ============================================================
# yayma: a of shape (3, 1) plus b of shape (4,) gives shape (3, 4)
# ============================================================
a = np.array([[0], [10], [20]])
b = np.arange(4)
CW, CH = 38, 30
p = canvas(660, 230)
TOP = 50
AX, BX, SX = 24, 238, 452
# operand a: the real column and its three virtual copies
for j in range(4):
    real = j == 0
    matrix(p, AX + j * CW, TOP, a, CW, CH, THEORY, 0.20 if real else 0.05,
           THEORY if real else TEXT, TEXT, 12, False,
           None if real else "3 3", 1.0 if real else 0.45,
           0.8 if real else 0.4)
p.arrow((AX + CW / 2, TOP - 12), (AX + 4 * CW - 6, TOP - 12), THEORY, 1.4,
        7.0)
txt(p, AX + 2 * CW, TOP + 3 * CH + 24, it("a") + ": (3, 1)", TEXT, 12)
txt(p, AX + 2 * CW, TOP + 3 * CH + 42, ARROW + " (3, 4)", TEXT, 12)
txt(p, (AX + 4 * CW + BX) / 2, TOP + 1.5 * CH + 7, "+", TEXT, 20)
# operand b: the real row and its two virtual copies
for i in range(3):
    real = i == 0
    matrix(p, BX, TOP + i * CH, b[None, :], CW, CH, THEORY,
           0.20 if real else 0.05, THEORY if real else TEXT, TEXT, 12,
           False, None if real else "3 3", 1.0 if real else 0.45,
           0.8 if real else 0.4)
p.arrow((BX - 10, TOP + CH / 2), (BX - 10, TOP + 3 * CH - 6), THEORY, 1.4,
        7.0)
txt(p, BX + 2 * CW, TOP + 3 * CH + 24, it("b") + ": (4,) " + ARROW
    + " (1, 4)", TEXT, 12)
txt(p, BX + 2 * CW, TOP + 3 * CH + 42, ARROW + " (3, 4)", TEXT, 12)
txt(p, (BX + 4 * CW + SX) / 2, TOP + 1.5 * CH + 6, "=", TEXT, 20)
# the result
matrix(p, SX, TOP, a + b, CW, CH, PRACTICE, 0.12, PRACTICE, PRACTICE, 12,
       True, sop=0.9)
txt(p, SX + 2 * CW, TOP + 3 * CH + 24, it("a") + " + " + it("b")
    + ": (3, 4)", TEXT, 12)

save("yayma", figure(
    660, 230, [p],
    "Broadcasting ile (3, 1) şekilli <em>a</em> ve (4,) şekilli <em>b</em> "
    "toplanır. Önce <em>b</em>'nin şekli soldan 1 eklenerek (1, 4) olur. "
    "Sonra uzunluğu 1 olan eksenler karşı tarafın uzunluğuna uzatılır: <em>a</em>'nın "
    "sütunu sağa, <em>b</em>'nin satırı aşağı kopyalanmış gibi davranır. "
    "Kesikli çizilen kopyalar bellekte yoktur. Sonuç, "
    "<code>a + b</code> çıktısındaki (3, 4) şekilli dizidir.",
    WIDE,
    aria="Broadcasting of a column of shape (3, 1) with entries 0 10 20 and "
         "a row of shape (4,) with entries 0 1 2 3: the column is stretched "
         "to the right, the row downward (dashed virtual copies), and the "
         "sum is the 3 by 4 array with rows 0 1 2 3, 10 11 12 13, "
         "20 21 22 23."))

# ============================================================
# monte-carlo: 1000 points of default_rng(2024) in the unit square
# ============================================================
rng = np.random.default_rng(2024)
P = rng.random((1000, 2))
inside = (P**2).sum(axis=1) <= 1.0
n_in = int(inside.sum())
p = Plot(56, 22, 330, 330, (0, 1), (0, 1))
p.axes([0, 0.5, 1], [0, 0.5, 1], "x", "y",
       lambda v: dec(v, 1) if v == 0.5 else str(int(v)),
       lambda v: dec(v, 1) if v == 0.5 else str(int(v)))
rect(p, p.X(0), p.Y(1), p.w, p.h, "none", 0, TEXT, 1.0, 0.45)
p.arc(0, 0, 1, 0, math.pi / 2, TEXT, 1.6, None, 0.9, 96)
for (x, y), ok in zip(P, inside):
    color = THEORY if ok else PRACTICE
    p.add(f'<circle cx="{p.X(x):.1f}" cy="{p.Y(y):.1f}" r="1.7" '
          f'fill="{color}" fill-opacity="0.85"/>')
# legend under the square
LY = p.y0 + p.h + 40
p.add(f'<circle cx="{p.x0 + 6:.1f}" cy="{LY - 4:.1f}" r="4" '
      f'fill="{THEORY}"/>')
txt(p, p.x0 + 16, LY, f"içeride: {n_in}", TEXT, 12, "start")
p.add(f'<circle cx="{p.x0 + 176:.1f}" cy="{LY - 4:.1f}" r="4" '
      f'fill="{PRACTICE}"/>')
txt(p, p.x0 + 186, LY, f"dışarıda: {1000 - n_in}", TEXT, 12, "start")

save("monte-carlo", figure(
    420, 420, [p],
    "<code>default_rng(2024)</code> ile üretilen ilk 1000 nokta. "
    f"<em>x</em>² + <em>y</em>² &#8804; 1 maskesi {n_in} noktada doğrudur "
    "(mavi). Çeyrek dairenin alanı &#960;/4 olduğundan "
    f"4 &#183; {n_in}/1000 = {dec(4 * n_in / 1000, 3)} değeri &#960; için "
    "bir kestirimdir.",
    aria=f"Scatter of 1000 random points in the unit square with the "
         f"quarter circle x^2 + y^2 = 1; {n_in} points inside are blue, "
         f"{1000 - n_in} outside are red."))

# ============================================================
# uzaklik: six points, their distance matrix and nearest neighbours
# ============================================================
rng = np.random.default_rng(5)
Q = np.round(10 * rng.random((6, 2)), 1)
D = np.sqrt(((Q[:, None, :] - Q[None, :, :])**2).sum(axis=-1))
E = D.copy()
np.fill_diagonal(E, np.inf)
NN = E.argmin(axis=1)

pl = Plot(40, 40, 250, 250, (0, 10.5), (0, 10.5))
pl.axes([0, 5, 10], [0, 5, 10], "x", "y")
# nearest-neighbour arrows i -> NN[i]; a mutual pair gets one double arrow
done = set()
for i, j in enumerate(NN):
    i, j = int(i), int(j)
    if (j, i) in done:
        continue
    done.add((i, j))
    mutual = int(NN[j]) == i
    pi_, pj = Q[i], Q[j]
    d = pj - pi_
    u = d / np.linalg.norm(d)
    s0 = pi_ + 0.32 * u
    s1 = pj - 0.32 * u
    pl.arrow(tuple(s0), tuple(s1), PRACTICE, 1.6, 7.0)
    if mutual:
        pl.arrow(tuple(s1), tuple(s0), PRACTICE, 1.6, 7.0)
pl.points([tuple(q) for q in Q], THEORY, 4.2)
OFFSETS = {0: (8, -6, "start"), 1: (-3, -10, "end"), 2: (-8, -6, "end"),
           3: (8, 4, "start"), 4: (9, 5, "start"), 5: (8, -6, "start")}
for k, (x, y) in enumerate(Q):
    dx, dy, anc = OFFSETS[k]
    pl.label(x, y, str(k), dx, dy, THEORY, 12.5, anc, True)
txt(pl, pl.x0 + pl.w / 2, 22, "noktalar ve en yakın komşular", TEXT, 12.5,
    bold=True)

# right panel: the matrix D, darker for smaller distances
pr = canvas(700, 340)
MX, MY, MW, MH = 380, 52, 46, 36
dmax = D.max()
for i in range(6):
    txt(pr, MX - 12, MY + i * MH + MH / 2 + 4, str(i), THEORY, 12, "end",
        True)
    txt(pr, MX + i * MW + MW / 2, MY - 10, str(i), THEORY, 12, "middle",
        True)
    for j in range(6):
        x, y = MX + j * MW, MY + i * MH
        shade = 0.0 if i == j else 0.06 + 0.34 * (1 - D[i, j] / dmax)
        rect(pr, x, y, MW, MH, THEORY, round(shade, 3), TEXT, 0.8, 0.35)
        txt(pr, x + MW / 2, y + MH / 2 + 4, dec(D[i, j], 2), TEXT, 11)
    j = int(NN[i])
    rect(pr, MX + j * MW + 1.5, MY + i * MH + 1.5, MW - 3, MH - 3, "none",
         0, PRACTICE, 2.2, 1.0)
txt(pr, MX + 3 * MW, 22, "D[i, j] = |P[i] " + MINUS + " P[j]|", TEXT, 12.5,
    bold=True)

save("uzaklik", figure(
    700, 340, [pl, pr],
    "Solda <code>default_rng(5)</code> ile üretilen altı nokta; her ok bir "
    "noktadan en yakın komşusuna gider (1 ile 5 birbirinin en yakın "
    "komşusudur). Sağda broadcasting ile hesaplanan uzaklık matrisi "
    "<em>D</em>: uzaklık küçüldükçe hücre koyulaşır, her satırda köşegen "
    "dışındaki en küçük eleman çerçevelidir. Çerçeveli sütunlar "
    "<code>E.argmin(axis=1)</code> sonucu olan [1 5 1 1 2 1] dizisidir.",
    WIDE,
    aria="Left: six points labelled 0 to 5 in the square [0, 10]^2 with "
         "arrows to their nearest neighbours 1 5 1 1 2 1. Right: the 6 by 6 "
         "symmetric distance matrix with zeros on the diagonal; the smallest "
         "off-diagonal entry of each row is framed."))

# ============================================================
# zaman: measured run times against n on log-log axes
# ============================================================
# Measured on the author's machine by kod/vek/b29_zaman_tarama.py; the
# chapter prints exactly this table. Columns: loop over a list,
# np.vectorize, vectorised np.sum(x * x).
NS = [10, 100, 10**3, 10**4, 10**5, 10**6]
T_LOOP = [2.6e-07, 2.0e-06, 2.0e-05, 2.1e-04, 2.0e-03, 1.9e-02]
T_VECTORIZE = [5.7e-06, 1.2e-05, 7.6e-05, 7.0e-04, 8.0e-03, 8.4e-02]
T_NUMPY = [1.4e-06, 1.4e-06, 2.0e-06, 5.0e-06, 1.6e-04, 1.5e-03]
lg = math.log10
p = Plot(78, 34, 420, 290, (1, 6), (-7, -1))
p.grid(range(1, 7), range(-7, 0))
p.axes([], [], "n", "")
for k in range(1, 7):
    p.label(k, -7, "10" + sup(str(k)), 0, 18, TEXT, 11, "middle")
for k in range(-7, 0):
    p.label(1, k, "10" + sup(MINUS + str(-k)), -8, 4, TEXT, 11, "end")
p.text_px(p.x0 - 4, p.y0 - 14, "süre (saniye)", TEXT, 11.5, "middle")
series = [(T_LOOP, PRACTICE, None, "liste üzerinde döngü"),
          (T_VECTORIZE, REMARK, "6 4", "np.vectorize"),
          (T_NUMPY, THEORY, None, "np.sum(x * x)")]
for ts, color, dash, _ in series:
    pts = [(lg(n), lg(t)) for n, t in zip(NS, ts)]
    p.line(pts, color, 2.0, dash)
    p.points(pts, color, 3.4)
p.label(4.2, lg(2.1e-4) + 0.05, "liste üzerinde döngü", 0, 26, PRACTICE, 12,
        "start", True)
p.label(3.0, lg(7.6e-5), "np.vectorize", -6, -10, REMARK, 12, "end", True)
p.label(4.0, lg(5.0e-6), "np.sum(x * x)", 0, 22, THEORY, 12, "start", True)

save("zaman", figure(
    540, 360, [p],
    "Zaman taraması kodunun tablosu, iki ekseni de logaritmik ölçekte. Döngünün süresi <em>n</em> ile doğru orantılı büyür (eğim 1). "
    "Vektörel toplamın küçük <em>n</em> için yaklaşık 1 mikrosaniyelik sabit "
    "bir başlangıç maliyeti vardır, büyük <em>n</em>'de de döngüden 10 ile "
    "40 kat arasında hızlıdır. <code>np.vectorize</code> içeride yine Python "
    "döngüsü çalıştırdığı için düz döngüden de yavaştır. Sayılar makineye "
    "göre değişir; eğrilerin biçimi değişmez.",
    aria="Log-log plot of run time against n from 10 to 10^6 for three "
         "methods: a Python loop over a list grows linearly, np.vectorize "
         "is a few times slower, the vectorised np.sum stays near 1e-6 s "
         "up to n = 10^4 and then grows, staying 10 to 40 times faster than "
         "the loop."))

# ============================================================
# fark: np.diff(y) / h placed at the left end points and at the midpoints
# ============================================================
n = 17
x = np.linspace(0, 2 * np.pi, n)
h = x[1] - x[0]
y = np.sin(x)
d_fwd = np.diff(y) / h
mid = (x[:-1] + x[1:]) / 2
p = Plot(56, 26, 440, 240, (0, 2 * math.pi), (-1.15, 1.15))
p.origin_axes(it("x"), "", [], [-1, 1], yfmt=lambda v: MINUS + "1"
              if v < 0 else "1")
for k, s in [(1, "&#960;/2"), (2, "&#960;"), (3, "3&#960;/2"),
             (4, "2&#960;")]:
    xv = k * math.pi / 2
    p.add(f'<line x1="{p.X(xv):.1f}" y1="{p.Y(0) - 3:.1f}" '
          f'x2="{p.X(xv):.1f}" y2="{p.Y(0) + 3:.1f}" stroke="{TEXT}" '
          f'stroke-width="1" opacity="0.7"/>')
    dx, dy, anc = {1: (-6, 16, "end"), 2: (0, -7, "middle"),
                   3: (6, 16, "start"), 4: (0, -7, "middle")}[k]
    txt(p, p.X(xv) + dx, p.Y(0) + dy, s, TEXT, 11, anc, opacity=0.75)
curve = [(t, math.cos(t)) for t in np.linspace(0, 2 * math.pi, 241)]
p.line(curve, THEORY, 2.0)
p.hollow_points(list(zip(x[:-1], d_fwd)), PRACTICE, 3.6)
p.points(list(zip(mid, d_fwd)), BASE, 3.4)
# legend above the plot, right side
LX = p.x0 + 250
p.add(f'<circle cx="{LX:.1f}" cy="{p.y0 + 2:.1f}" r="3.6" fill="none" '
      f'stroke="{PRACTICE}" stroke-width="1.8"/>')
txt(p, LX + 10, p.y0 + 6, "sol uçta: x[:-1]", PRACTICE, 12, "start", True)
p.add(f'<circle cx="{LX:.1f}" cy="{p.y0 + 22:.1f}" r="3.4" '
      f'fill="{BASE}"/>')
txt(p, LX + 10, p.y0 + 26, "orta noktada", BASE, 12, "start", True)
p.label(4.05, math.cos(4.05), "cos " + it("x"), -10, 4, THEORY, 12.5, "end",
        True)

save("fark", figure(
    540, 300, [p],
    "sin <em>x</em> fonksiyonunun [0, 2&#960;] aralığındaki 17 noktalık "
    "ızgarada <code>np.diff(y) / h</code> ile bulunan 16 fark bölümü "
    "(<em>h</em> &#8776; 0,39). Değerler alt aralıkların sol uçlarına "
    "yazılınca (boş daireler) cos <em>x</em> eğrisinin yarım adım soluna "
    "kayar, en büyük hata 0,19 olur. Aynı sayılar orta noktalara yazılınca (dolu "
    "daireler) eğrinin üstüne oturur, en büyük hata 0,0063'e iner.",
    aria="The curve cos x on [0, 2 pi] with sixteen forward difference "
         "quotients of sin x: hollow red circles at the left end points "
         "are shifted half a step to the left of the curve, filled green "
         "dots at the midpoints lie on the curve."))
