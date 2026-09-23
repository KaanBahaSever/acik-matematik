# -*- coding: utf-8 -*-
"""
Figures of the chapter "İstatistiğe Giriş ve Betimsel Ölçüler"
(dersler/matematiksel-istatistik/istatistige-giris.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
callout), never inside a definition box. The figures are NOT produced at
build time. Run

    python scripts/statistics_figures/itg.py
    python scripts/center_figures.py "statistics-itg-*.md" --keep-width
    python scripts/check_figure_labels.py "scripts/_figures/statistics-itg-*.md"

and paste the markup of scripts/_figures/statistics-itg-<name>.md into the .qmd.
The captions are Turkish plain text on purpose (no LaTeX); the aria labels are
plain ASCII.
"""
import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, WIDE, TEXT, THEORY, PRACTICE, BASE, REMARK, BG, panel_title  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "statistics-itg-"

MINUS, LEQ, APPROX = "&#8722;", "&#8804;", "&#8776;"
SUB = {"1": "&#8321;", "2": "&#8322;", "3": "&#8323;"}


def save(name, markup):
    (OUT_DIR / f"{PREFIX}{name}.md").write_text(markup, encoding="utf-8", newline="\n")


def comma(v, nd=2):
    """Number with a decimal comma: 0.25 -> '0,25'."""
    return f"{v:.{nd}f}".replace(".", ",")


def it(s):
    return f'<tspan font-style="italic">{s}</tspan>'


def dot(p, x, y, color, r=4.5, opacity=1.0):
    p.add(f'<circle cx="{p.X(x):.1f}" cy="{p.Y(y):.1f}" r="{r}" fill="{color}" opacity="{opacity}"/>')


def ring(p, x, y, color, r=4.5, opacity=0.55):
    p.add(f'<circle cx="{p.X(x):.1f}" cy="{p.Y(y):.1f}" r="{r}" fill="none" stroke="{color}" '
          f'stroke-width="1.3" opacity="{opacity}"/>')


def rect_px(p, x, y, w, h, fill, opacity, stroke="none", rx=4, sw=1.2):
    p.add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}" '
          f'fill-opacity="{opacity}" stroke="{stroke}" stroke-width="{sw}"/>')


def seg_px(p, x1, y1, x2, y2, color=TEXT, width=1.2, opacity=0.6, dash=None):
    da = f' stroke-dasharray="{dash}"' if dash else ""
    p.add(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" '
          f'stroke-width="{width}" opacity="{opacity}"{da}/>')


def hline_axis(p, x_ticks, fmt=lambda v: f"{v:g}", y=0):
    """Bare horizontal number line at data height y with ticks below."""
    Y = p.Y(y)
    seg_px(p, p.x0, Y, p.x0 + p.w, Y, TEXT, 1.1, 0.45)
    for t in x_ticks:
        seg_px(p, p.X(t), Y, p.X(t), Y + 4, TEXT, 1.0, 0.45)
        p.text_px(p.X(t), Y + 17, fmt(t), TEXT, 11, "middle")


# ============================================================
# dort-yontem: four probability sampling designs on 96 units
# ============================================================
COLS, ROWS = 12, 8
N_POP = COLS * ROWS
STEP = 21


def grid_panel(ox, oy, title):
    q = Plot(ox, oy, COLS * STEP, ROWS * STEP, (0, COLS), (ROWS, 0))
    panel_title(q, title, TEXT, 13)
    return q


def cell(q, idx):
    """Centre (data coords) of unit number idx = 1..96, numbered row by row."""
    r, c = divmod(idx - 1, COLS)
    return c + 0.5, r + 0.5


def draw_units(q, chosen):
    for idx in range(1, N_POP + 1):
        x, y = cell(q, idx)
        if idx in chosen:
            dot(q, x, y, PRACTICE, 5.2)
        else:
            ring(q, x, y, TEXT, 4.2, 0.35)


rng = random.Random(7)
W, H = 700, 470
panels = []
PX0, PX1, PY0, PY1 = 50, 398, 40, 262

# simple random sample
q = grid_panel(PX0, PY0, "Basit rasgele örnekleme")
draw_units(q, set(rng.sample(range(1, N_POP + 1), 12)))
panels.append(q)

# stratified: rows 0-3 (48), rows 4-5 (24), rows 6-7 (24); allocation 6, 3, 3
q = grid_panel(PX1, PY0, "Tabakalı örnekleme")
strata = [(0, 4, 6, THEORY, "48"), (4, 6, 3, REMARK, "24"), (6, 8, 3, BASE, "24")]
chosen = set()
for r0, r1, k, col, size in strata:
    rect_px(q, q.X(0) - 3, q.Y(r0) + 1.5, q.w + 6, q.Y(r1) - q.Y(r0) - 3, col, 0.13, col, 5, 1.0)
    units = [r * COLS + c + 1 for r in range(r0, r1) for c in range(COLS)]
    chosen |= set(rng.sample(units, k))
    q.text_px(q.x0 + q.w + 10, (q.Y(r0) + q.Y(r1)) / 2 + 4, size, col, 11.5, "start", True)
draw_units(q, chosen)
panels.append(q)

# systematic: k = 96/12 = 8, start 5
q = grid_panel(PX0, PY1, "Sistematik örnekleme")
sys_units = [5 + 8 * j for j in range(12)]
draw_units(q, set(sys_units))
panels.append(q)

# cluster: 16 clusters = half rows of 6 units; choose 2
q = grid_panel(PX1, PY1, "Küme örneklemesi")
clusters = [(r, h) for r in range(ROWS) for h in range(2)]
pick = rng.sample(clusters, 2)
chosen = set()
for r, h in clusters:
    sel = (r, h) in pick
    rect_px(q, q.X(6 * h) + 1.5, q.Y(r) + 2, 6 * STEP - 3, STEP - 4,
            PRACTICE if sel else TEXT, 0.14 if sel else 0.03,
            PRACTICE if sel else TEXT, 5, 1.2 if sel else 0.6)
    if sel:
        chosen |= {r * COLS + 6 * h + c + 1 for c in range(6)}
draw_units(q, chosen)
panels.append(q)

save("dort-yontem", figure(
    W, H, panels,
    "96 birimlik aynı kitleden dört olasılığa bağlı yöntemle seçilen 12 birim (dolu noktalar). "
    "Basit rasgele: her 12 birimlik alt küme eşit olasılıklı. Tabakalı: 48, 24 ve 24 birimlik "
    "tabakalardan orantılı olarak 6, 3 ve 3 birim. Sistematik: 5. birimden başlayıp her 8. birim. "
    "Küme: 6 birimlik 16 kümeden rasgele seçilen 2 kümenin bütün birimleri.",
    WIDE, aria="Four 12 by 8 grids of units showing simple random, stratified, systematic and cluster samples"))


# ============================================================
# bilesik-artis: 90 000 growing by 50, 20, 90 percent
# ============================================================
W, H = 580, 330
q = Plot(78, 36, 440, 230, (0, 3.35), (0, 350))
q.grid(ys=[50, 100, 150, 200, 250, 300])
q.axes([0, 1, 2, 3], [0, 100, 200, 300], xlabel="yıl", ylabel="değer (bin)",
       yfmt=lambda v: f"{v:g}")
g = 3.42 ** (1 / 3)
a = (1.5 + 1.2 + 1.9) / 3
xs = [3 * i / 240 for i in range(241)]
q.line([(t, 90 * a ** t) for t in xs], REMARK, 1.6, "6 4", 0.9)
q.line([(t, 90 * g ** t) for t in xs], THEORY, 2.0)
ring(q, 3, 90 * a ** 3, REMARK, 4.5, 1.0)
actual = [(0, 90), (1, 135), (2, 162), (3, 307.8)]
q.line(actual, PRACTICE, 1.8, None, 0.9)
for x, y in actual:
    dot(q, x, y, PRACTICE, 4.5)
q.label(1, 135, "135", -8, -9, PRACTICE, 12, "end", True)
q.label(2, 162, "162", 8, 16, PRACTICE, 12, "start", True)
q.label(3, 307.8, "307,8", 10, 12, PRACTICE, 12, "start", True)
q.label(0, 90, "90", 8, 16, PRACTICE, 12, "start", True)
q.label(3, 324.45, "324,5", 10, -2, REMARK, 12, "start", True)
# legend
lx, ly = q.x0 + 16, q.y0 + 14
for i, (col, dash, txt) in enumerate([
        (PRACTICE, None, "gerçek artışlar (%50, %20, %90)"),
        (THEORY, None, "sabit oran: geometrik ortalama 1,5066"),
        (REMARK, "6 4", "sabit oran: aritmetik ortalama 1,5333")]):
    yy = ly + 20 * i
    seg_px(q, lx, yy - 4, lx + 26, yy - 4, col, 2.0, 0.95, dash)
    q.text_px(lx + 34, yy, txt, TEXT, 12)
save("bilesik-artis", figure(
    W, H, [q],
    "90 bin liralık eşyanın üç yıllık değeri. Gerçek yol (kırık çizgi) ile her yıl 1,5066 katına çıkan sabit "
    "artış aynı noktada, 307,8 binde biter. Oranların aritmetik ortalaması 1,5333 ise değeri 324,5 bine "
    "çıkararak olduğundan büyük gösterir.",
    aria="Value over three years: actual growth path and constant geometric mean growth both end at 307.8, "
         "arithmetic mean growth overshoots to 324.5"))


# ============================================================
# yarim-cember: HM <= GM <= AM for a = 8, b = 2
# ============================================================
W, H = 560, 370
PW, PH = 460, 250
XR = (-0.8, 10.8)
YR = (-1.0, -1.0 + (XR[1] - XR[0]) * PH / PW)
q = Plot(50, 30, PW, PH, XR, YR)
pts = [(5 + 5 * math.cos(math.pi * k / 300), 5 * math.sin(math.pi * k / 300)) for k in range(301)]
q.polygon(pts, THEORY, 0.06)
q.line(pts, TEXT, 1.4, None, 0.55)
q.line([(0, 0), (10, 0)], TEXT, 1.4, None, 0.7)
O, P, C = (5, 0), (8, 0), (8, 4)
Hf = (5 + 1.8 * 0.6, 1.8 * 0.8)
q.line([Hf, P], TEXT, 1.0, "4 3", 0.6)
# right angle marks at P and at H
q.line([(8 - 0.3, 0), (8 - 0.3, 0.3), (8, 0.3)], TEXT, 0.9, None, 0.55)
ux, uy = 0.6, 0.8
vx, vy = 0.8, -0.6
s = 0.3
q.line([(Hf[0] + s * vx, Hf[1] + s * vy), (Hf[0] + s * vx + s * ux, Hf[1] + s * vy + s * uy),
        (Hf[0] + s * ux, Hf[1] + s * uy)], TEXT, 0.9, None, 0.55)
q.line([O, C], THEORY, 2.6)
q.line([P, C], PRACTICE, 2.6)
# DC drawn parallel to OC, shifted to the upper left, so that both segments stay visible
off = 0.22
nx, ny = -0.8 * off, 0.6 * off
q.line([(Hf[0] + nx, Hf[1] + ny), (C[0] + nx, C[1] + ny)], REMARK, 3.2)
for e in (Hf, C):
    q.line([(e[0] + 0.4 * nx, e[1] + 0.4 * ny), (e[0] + 1.6 * nx, e[1] + 1.6 * ny)], REMARK, 1.4)
for pnt in (O, P, C, Hf, (0, 0), (10, 0)):
    dot(q, pnt[0], pnt[1], TEXT, 3.2)
q.label(0, 0, "A", -6, 18, TEXT, 13, "middle", True)
q.label(10, 0, "B", 6, 18, TEXT, 13, "middle", True)
q.label(5, 0, "O", 0, 18, TEXT, 13, "middle", True)
q.label(8, 0, "P", 0, 18, TEXT, 13, "middle", True)
q.label(8, 4, "C", 8, -6, TEXT, 13, "start", True)
q.label(Hf[0], Hf[1], "D", 4, 20, TEXT, 13, "start", True)
q.label(4, 0, "a = 8", 0, 36, TEXT, 12.5, "middle")
q.label(9, 0, "b = 2", 0, 36, TEXT, 12.5, "middle")
seg_px(q, q.X(0), q.Y(0) + 24, q.X(8) - 2, q.Y(0) + 24, TEXT, 1.0, 0.5)
seg_px(q, q.X(8) + 2, q.Y(0) + 24, q.X(10), q.Y(0) + 24, TEXT, 1.0, 0.5)
# legend in the empty upper left corner
ly = q.Y(0) + 66
for lx, col, txt in [(q.x0 + 10, THEORY, "OC = AO = 5 (yarıçap)"),
                     (q.x0 + 200, PRACTICE, "PC = GO = 4"),
                     (q.x0 + 330, REMARK, "DC = HO = 3,2")]:
    seg_px(q, lx, ly - 4, lx + 24, ly - 4, col, 3.0, 1.0)
    q.text_px(lx + 32, ly, txt, TEXT, 12.5)
save("yarim-cember", figure(
    W, H, [q],
    "Çapı a + b = 10 olan yarım çember. Yarıçap OC aritmetik ortalamadır (5). P'deki dikme PC, "
    "dik üçgendeki yükseklik bağıntısından √(ab) = 4 uzunluğundadır. P'den OC'ye inilen dikmenin ayağı D için "
    "DC = PC²/OC = 16/5 = 3,2 harmonik ortalamadır (OC üzerindeki parça, görünsün diye yanına çizildi). "
    "Dik üçgende hipotenüs dik kenardan uzun olduğundan DC ≤ PC ≤ OC.",
    aria="Semicircle construction showing harmonic mean 3.2, geometric mean 4 and arithmetic mean 5 of 8 and 2"))


# ============================================================
# uc-deger: effect of an outlier on mean and median (broken axis)
# ============================================================
W, H = 620, 300


def data_row(oy, data, mean, med, title):
    # main part 0..8 on 400 px, break, then 98..102 on 60 px
    main = Plot(60, oy, 400, 60, (0, 17.4), (0, 1))
    tail = Plot(500, oy, 70, 60, (97.5, 102.5), (0, 1))
    Y = main.Y(0)
    seg_px(main, main.x0, Y, main.x0 + main.w, Y, TEXT, 1.1, 0.45)
    seg_px(main, tail.x0, Y, tail.x0 + tail.w, Y, TEXT, 1.1, 0.45)
    for bx in (main.x0 + main.w + 12, main.x0 + main.w + 20):
        seg_px(main, bx - 4, Y + 6, bx + 4, Y - 6, TEXT, 1.2, 0.6)
    for t in range(0, 18, 2):
        seg_px(main, main.X(t), Y, main.X(t), Y + 4, TEXT, 1.0, 0.45)
        main.text_px(main.X(t), Y + 17, str(t), TEXT, 11, "middle")
    seg_px(main, tail.X(100), Y, tail.X(100), Y + 4, TEXT, 1.0, 0.45)
    main.text_px(tail.X(100), Y + 17, "100", TEXT, 11, "middle")
    seen = {}
    for v in data:
        k = seen.get(v, 0)
        seen[v] = k + 1
        pl = tail if v > 50 else main
        dot(pl, v, 0.16 + 0.26 * k, THEORY, 5.5)
    main.text_px(main.x0 - 44, oy - 28, title, TEXT, 12.5, "start", True)
    # median and mean markers
    main.vline(med, -0.05, 0.9, PRACTICE, "4 3", 0.95)
    main.vline(mean, -0.05, 0.9, REMARK, "4 3", 0.95)
    return main, tail, Y


m1, t1, y1 = data_row(40, [1, 2, 3, 4, 4, 5, 6, 7], 4, 4, "1, 2, 3, 4, 4, 5, 6, 7")
m1.label(4, 0.9, "ortalama = medyan = 4", 0, -6, TEXT, 12.5, "middle", True)
m2, t2, y2 = data_row(185, [1, 2, 3, 4, 4, 5, 6, 100], 125 / 8, 4, "1, 2, 3, 4, 4, 5, 6, 100")
m2.label(4, 0.9, "medyan = 4", 0, -6, PRACTICE, 12.5, "middle", True)
m2.label(125 / 8, 0.9, "ortalama = 15,625", 0, -6, REMARK, 12.5, "middle", True)
save("uc-deger", figure(
    W, H, [m1, t1, m2, t2],
    "Üstte sekiz gözlemin ortalaması ve medyanı 4'tür. Altta en büyük gözlem 7 yerine 100 olunca medyan "
    "yine 4 kalır, ortalama ise 15,625'e fırlar: aritmetik ortalama tek bir uç değere çok duyarlıdır. "
    "Eksendeki kırık, 17 ile 98 arasının atlandığını gösterir.",
    aria="Dot plots of 1,2,3,4,4,5,6,7 and 1,2,3,4,4,5,6,100 with median 4 and means 4 and 15.625"))


# ============================================================
# mod: shoe sizes with two modes
# ============================================================
W, H = 560, 300
freq = {36: 1, 37: 2, 38: 3, 39: 2, 40: 3, 41: 1, 42: 2, 43: 1}
q = Plot(70, 40, 420, 200, (35.3, 43.7), (0, 3.6))
q.grid(ys=[1, 2, 3])
q.axes(range(36, 44), [0, 1, 2, 3], xlabel="numara", ylabel="frekans")
for x, f in freq.items():
    mode = f == 3
    col = PRACTICE if mode else THEORY
    q.bars([(x, f)], col, 34, 0.85 if mode else 0.45)
    q.label(x, f, str(f), 0, -7, col, 12.5, "middle", True)
q.text_px(q.X(39), q.y0 - 12, "iki mod: 38 ve 40", PRACTICE, 13, "middle", True)
save("mod", figure(
    W, H, [q],
    "On beş öğrencinin ayakkabı numaralarının frekansları. En yüksek frekans 3'tür ve iki değerde "
    "görülür; veri kümesinin 38 ve 40 olmak üzere iki modu vardır.",
    aria="Bar chart of shoe size frequencies with two highest bars at 38 and 40"))


# ============================================================
# ayni-ortalama: same mean, different spread
# ============================================================
W, H = 600, 250
A = [48, 49, 50, 51, 52]
B = [30, 40, 50, 60, 70]
rows = []
for k, (data, name, s2) in enumerate([(A, "A", "2,5"), (B, "B", "250")]):
    q = Plot(90, 34 + 100 * k, 460, 50, (25, 75), (0, 1))
    hline_axis(q, range(25, 80, 5))
    q.vline(50, 0, 0.95, TEXT, "4 3", 0.55)
    for v in data:
        dot(q, v, 0.3, THEORY if name == "A" else PRACTICE, 4.2)
    lo, hi = min(data), max(data)
    yb = q.Y(0.3) - 16
    seg_px(q, q.X(lo), yb, q.X(hi), yb, TEXT, 1.0, 0.55)
    seg_px(q, q.X(lo), yb - 4, q.X(lo), yb + 4, TEXT, 1.0, 0.55)
    seg_px(q, q.X(hi), yb - 4, q.X(hi), yb + 4, TEXT, 1.0, 0.55)
    q.text_px(q.x0 - 62, q.Y(0.3) + 5, "Grup " + name, TEXT, 13, "start", True)
    side = hi + 1.5
    q.label(side, 0.3, it("s") + "² = " + s2, 6, 5, TEXT, 12.5, "start")
    rows.append(q)
rows[0].label(50, 0.95, "ortalama 50", 0, -4, TEXT, 12, "middle")
save("ayni-ortalama", figure(
    W, H, rows,
    "İki grubun ortalaması da 50'dir, ama A'nın gözlemleri 48 ile 52 arasında sıkışmışken B'ninkiler "
    "30 ile 70 arasına yayılır. Ortalama bu farkı göremez; örneklem varyansı A için 2,5, B için 250'dir.",
    aria="Two dot plots with mean 50: group A tightly packed, group B widely spread"))


# ============================================================
# ceyreklikler: quartiles of ten observations with a box
# ============================================================
W, H = 600, 250
x = [12, 15, 17, 20, 22, 25, 28, 30, 34, 41]
Q1, Q2, Q3 = 16.5, 23.5, 31
q = Plot(40, 60, 520, 120, (10, 44), (0, 1))
hline_axis(q, range(10, 45, 5))
ybox0, ybox1 = 0.55, 0.9
top, bot = q.Y(ybox1), q.Y(ybox0)
rect_px(q, q.X(Q1), top, q.X(Q3) - q.X(Q1), bot - top, THEORY, 0.14, THEORY, 2, 1.6)
seg_px(q, q.X(Q2), top, q.X(Q2), bot, PRACTICE, 2.4, 1.0)
mid = (top + bot) / 2
seg_px(q, q.X(12), mid, q.X(Q1), mid, THEORY, 1.4, 0.9)
seg_px(q, q.X(Q3), mid, q.X(41), mid, THEORY, 1.4, 0.9)
for v in (12, 41):
    seg_px(q, q.X(v), mid - 7, q.X(v), mid + 7, THEORY, 1.4, 0.9)
for v in x:
    dot(q, v, 0.2, TEXT, 4.2, 0.75)
for v, nm, col in [(Q1, "1", THEORY), (Q2, "2", PRACTICE), (Q3, "3", THEORY)]:
    q.text_px(q.X(v), top - 8, it("Q") + SUB[nm] + " = " + comma(v, 1).replace(",0", ""),
              col, 12.5, "middle", True)
yb = bot + 14
seg_px(q, q.X(Q1), yb, q.X(Q3), yb, TEXT, 1.0, 0.55)
seg_px(q, q.X(Q1), yb - 4, q.X(Q1), yb + 4, TEXT, 1.0, 0.55)
seg_px(q, q.X(Q3), yb - 4, q.X(Q3), yb + 4, TEXT, 1.0, 0.55)
q.text_px(q.X(Q3) + 10, yb + 4, it("Q") + SUB["3"] + " " + MINUS + " " + it("Q") + SUB["1"] + " = 14,5",
          TEXT, 12, "start")
save("ceyreklikler", figure(
    W, H, [q],
    "On gözlem (alttaki noktalar) ve çeyreklikleri. Kutu Q1 = 16,5 ile Q3 = 31 arasındadır ve "
    "gözlemlerin ortadaki yarısını taşır; içindeki çizgi medyandır (Q2 = 23,5). Bıyıklar en küçük (12) ve "
    "en büyük (41) gözleme uzanır. Kutunun genişliği çeyrekler arası açıklıktır.",
    aria="Box plot of ten observations with quartiles 16.5, 23.5 and 31, whiskers to 12 and 41"))

print("done")
