# -*- coding: utf-8 -*-
"""
Figures of the chapter "Veri Yapıları ve Comprehension"
(dersler/python-bilimsel/veri-yapilari.qmd).

Figures go INSIDE the box they explain (example, exercise or callout), never
inside a definition box, never inside a collapsed .cozum block and never
directly under a heading. The figures are NOT produced at build time. Run

    python scripts/python_figures/ver.py
    python scripts/center_figures.py "python-ver-*.md"
    python scripts/check_figure_labels.py "scripts/_figures/python-ver-*.md"

and paste the markup of scripts/_figures/python-ver-<name>.md into the .qmd.
Captions are Turkish on purpose; aria labels are plain ASCII.

Every drawn value is computed here with the same Python expressions the
chapter's code blocks use (slices, set operations, the zip rule of Pascal's
triangle, itertools.product, the sieve), so the pictures match the printed
outputs exactly.
"""
import math
import sys
from collections import Counter
from itertools import product
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import (Plot, figure, WIDE, TEXT, THEORY, PRACTICE,  # noqa: E402
                      BASE, REMARK, BG)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "python-ver-"
MINUS = "&#8722;"


def save(name, markup):
    (OUT_DIR / f"{PREFIX}{name}.md").write_text(markup, encoding="utf-8", newline="\n")
    print(f"{PREFIX}{name}.md")


def canvas(W, H):
    """A panel whose data coordinates are the pixel coordinates (y downward)."""
    return Plot(0, 0, W, H, (0, W), (H, 0))


def num(v):
    """Integer label with a true minus sign."""
    return str(v).replace("-", MINUS)


def cell(p, x, y, w, h, s, fill=BG, fill_op=1.0, stroke=TEXT, stroke_op=0.55,
         width=1.2, color=TEXT, size=15, bold=False, rx=0):
    """A rectangle with its top-left corner at (x, y) and a centred label."""
    p.add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
          f'fill="{fill}" fill-opacity="{fill_op}" stroke="{stroke}" '
          f'stroke-opacity="{stroke_op}" stroke-width="{width}"/>')
    if s != "":
        p.text_px(x + w / 2, y + h / 2 + 0.36 * size, s, color, size, "middle", bold)


def curved_arrow(p, x0, y0, x1, y1, lift, color=THEORY, width=1.5, head=7.0):
    """Quadratic arc from (x0, y0) to (x1, y1) bulging `lift` px upward, with a head."""
    cx, cy = (x0 + x1) / 2, min(y0, y1) - lift
    ux, uy = x1 - cx, y1 - cy
    n = math.hypot(ux, uy)
    ux, uy = ux / n, uy / n
    ex, ey = x1 - ux * head * 0.8, y1 - uy * head * 0.8
    p.add(f'<path d="M{x0:.1f},{y0:.1f} Q{cx:.1f},{cy:.1f} {ex:.1f},{ey:.1f}" fill="none" '
          f'stroke="{color}" stroke-width="{width}" stroke-linecap="round"/>')
    px, py, hw = -uy, ux, head * 0.42
    p.add(f'<polygon points="{x1:.1f},{y1:.1f} {x1 - ux * head + px * hw:.1f},'
          f'{y1 - uy * head + py * hw:.1f} {x1 - ux * head - px * hw:.1f},'
          f'{y1 - uy * head - py * hw:.1f}" fill="{color}"/>')


def ref_dot(p, x, y, color):
    p.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.2" fill="{color}"/>')


# ============================================================
# indeksler: positive and negative indices of primes = [2, 3, 5, 7, 11, 13]
# ============================================================
primes6 = [2, 3, 5, 7, 11, 13]
n6 = len(primes6)
W, H = 680, 180
p = canvas(W, H)
X0, CW, Y0, CH = 170, 80, 62, 46
for i, v in enumerate(primes6):
    x = X0 + i * CW
    assert primes6[i] == primes6[i - n6] == v       # i and i - len name the same cell
    cell(p, x, Y0, CW, CH, str(v), size=15, bold=True)
    p.text_px(x + CW / 2, Y0 - 14, str(i), THEORY, 14, "middle", True)
    p.text_px(x + CW / 2, Y0 + CH + 26, num(i - n6), PRACTICE, 14, "middle", True)
p.text_px(X0 - 16, Y0 - 14, "i", THEORY, 14, "end", italic=True)
p.text_px(X0 - 16, Y0 + CH / 2 + 5, "primes", TEXT, 14, "end")
p.text_px(X0 - 16, Y0 + CH + 26, '<tspan font-style="italic">i</tspan> ' + MINUS + " 6", PRACTICE, 14,
          "end")
save("indeksler", figure(
    W, H, [p],
    "<code>primes</code> listesinin altı hücresi. Üstteki sayılar baştan sayılan indislerdir "
    "(0, 1, …, 5), alttakiler sondan sayılan negatif indislerdir (&#8722;6, …, &#8722;1). "
    "Aynı sütundaki iki indis aynı elemanı gösterir: <code>primes[i]</code> ile "
    "<code>primes[i - 6]</code> aynı sayıdır.",
    aria="Six cells holding 2, 3, 5, 7, 11, 13; indices 0 to 5 above the cells and "
         "negative indices -6 to -1 below them"))


# ============================================================
# dilim: the slices a[2:5] and a[::2] of a = list(range(10, 18))
# ============================================================
a = list(range(10, 18))
idx = list(range(len(a)))
sel1, sel2 = idx[2:5], idx[::2]
assert [a[i] for i in sel1] == a[2:5] and [a[i] for i in sel2] == a[::2]
W, H = 700, 300
p = canvas(W, H)
X0, CW, CH = 150, 64, 40
R1, R2 = 66, 196                       # tops of the two rows

# row 1: cut points 0..8 and the half-open slice a[2:5]
for k in range(len(a) + 1):
    x = X0 + k * CW
    hot = k in (2, 5)
    p.add(f'<line x1="{x:.1f}" y1="{R1 - 10:.1f}" x2="{x:.1f}" y2="{R1 + CH + 10:.1f}" '
          f'stroke="{PRACTICE if hot else TEXT}" stroke-width="{2.2 if hot else 1}" '
          f'opacity="{1 if hot else 0.35}"/>')
    p.text_px(x, R1 - 16, str(k), PRACTICE if hot else TEXT, 14, "middle", hot)
for i, v in enumerate(a):
    on = i in sel1
    cell(p, X0 + i * CW + 3, R1, CW - 6, CH, str(v),
         fill=PRACTICE if on else BG, fill_op=0.20 if on else 1,
         stroke=PRACTICE if on else TEXT, stroke_op=1 if on else 0.5,
         color=PRACTICE if on else TEXT, bold=on)
p.text_px(X0 - 18, R1 - 16, "kesim", TEXT, 13.5, "end")
p.text_px(X0 - 18, R1 + CH / 2 + 5, "a[2:5]", PRACTICE, 15, "end", True)
bx0, bx1, by = X0 + 2 * CW, X0 + 5 * CW, R1 + CH + 18
p.add(f'<path d="M{bx0:.1f},{by - 6:.1f} L{bx0:.1f},{by:.1f} L{bx1:.1f},{by:.1f} '
      f'L{bx1:.1f},{by - 6:.1f}" fill="none" stroke="{PRACTICE}" stroke-width="1.5"/>')
p.text_px((bx0 + bx1) / 2, by + 20, "5 " + MINUS + " 2 = 3 eleman: [12, 13, 14]",
          PRACTICE, 14, "middle")

# row 2: every second element, a[::2]
for i, v in enumerate(a):
    on = i in sel2
    cell(p, X0 + i * CW + 3, R2, CW - 6, CH, str(v),
         fill=THEORY if on else BG, fill_op=0.18 if on else 1,
         stroke=THEORY if on else TEXT, stroke_op=1 if on else 0.5,
         color=THEORY if on else TEXT, bold=on)
    p.text_px(X0 + i * CW + CW / 2, R2 + CH + 18, str(i), TEXT, 12.5, "middle")
for i, j in zip(sel2, sel2[1:]):
    curved_arrow(p, X0 + i * CW + CW / 2 + 4, R2 - 3, X0 + j * CW + CW / 2 - 4, R2 - 3, 22)
p.text_px(X0 + 1 * CW + CW / 2, R2 - 22, "+2", THEORY, 13, "middle", True)
p.text_px(X0 - 18, R2 + CH / 2 + 5, "a[::2]", THEORY, 15, "end", True)
p.text_px(X0 - 18, R2 + CH + 18, "indis", TEXT, 12.5, "end")
save("dilim", figure(
    W, H, [p],
    "Dilimleme, elemanların arasındaki kesim noktalarıyla düşünülür. Üstte "
    "<code>a[2:5]</code>, 2 ve 5 numaralı kesimlerin arasında kalan üç elemanı alır; "
    "5 numaralı indis dahil değildir. Altta <code>a[::2]</code>, baştan başlayıp ikişer "
    "atlayarak çift indisli elemanları seçer: [10, 12, 14, 16].",
    aria="The list 10 to 17 drawn twice: above, cut points 0 to 8 between the cells and "
         "the slice a[2:5] taking 12, 13, 14; below, arcs jumping two cells at a time "
         "for a[::2] taking 10, 12, 14, 16"))


# ============================================================
# takma-ad: state after b = a, c = a.copy(), a.append(4)
# ============================================================
obj_a = [1, 2, 3]
b_ref = obj_a
c_obj = obj_a.copy()
obj_a.append(4)
assert b_ref is obj_a and c_obj is not obj_a and c_obj == [1, 2, 3]
W, H = 640, 250
p = canvas(W, H)
NX, NW, NH = 50, 50, 38
names = {"a": 62, "b": 126, "c": 196}           # vertical centres of the name boxes
LX, LW, LH = 360, 52, 42
L1, L2 = 76, 196                                  # vertical centres of the two lists
for nm, yc in names.items():
    col = PRACTICE if nm == "c" else THEORY
    cell(p, NX, yc - NH / 2, NW, NH, nm, fill=col, fill_op=0.12, stroke=col,
         stroke_op=0.9, color=col, size=14.5, bold=True, rx=6)
for i, v in enumerate(obj_a):
    cell(p, LX + i * LW, L1 - LH / 2, LW, LH, str(v), size=14.5)
for i, v in enumerate(c_obj):
    cell(p, LX + i * LW, L2 - LH / 2, LW, LH, str(v), size=14.5)
p.arrow((NX + NW + 4, names["a"]), (LX - 4, L1 - 6), THEORY, 1.7)
p.arrow((NX + NW + 4, names["b"]), (LX - 4, L1 + 8), THEORY, 1.7)
p.arrow((NX + NW + 4, names["c"]), (LX - 4, L2), PRACTICE, 1.7)
p.text_px(LX + 2 * LW, L1 - LH / 2 - 12, "tek bir liste nesnesi", THEORY, 14, "middle")
p.text_px(LX + 1.5 * LW, L2 + LH / 2 + 22, "a.copy() ile kurulan yeni nesne",
          PRACTICE, 14, "middle")
save("takma-ad", figure(
    W, H, [p],
    "Kodun sonundaki durum. <code>a</code> ve <code>b</code> adları aynı liste nesnesine "
    "bağlıdır; bu yüzden <code>a.append(4)</code> değişikliği <code>b</code> üzerinden de "
    "görünür ve <code>b is a</code> doğrudur. <code>c</code> ise kopyalama anındaki içerikle "
    "kurulmuş ayrı bir nesnedir.",
    aria="Names a and b both point to one list object [1, 2, 3, 4]; name c points to a "
         "separate list object [1, 2, 3]"))


# ============================================================
# paylasilan-satir: [[0] * 3] * 3 shares one row, the loop builds three rows
# ============================================================
bad = [[0] * 3] * 3
good = []
for _ in range(3):
    good.append([0] * 3)
bad[0][0] = 1
good[0][0] = 1
assert bad[0] is bad[2] and good[0] is not good[2]
W, H = 760, 260
p = canvas(W, H)
SW, SH = 42, 38                              # outer-list slot size
TOPS = 62


def outer_list(p, x, color):
    """Three stacked slots of an outer list; returns the slot centres."""
    centres = []
    for i in range(3):
        y = TOPS + i * SH
        cell(p, x, y, SW, SH, "", stroke=color, stroke_op=0.9, width=1.4)
        p.text_px(x - 10, y + SH / 2 + 5, str(i), TEXT, 13, "end")
        centres.append((x + SW / 2, y + SH / 2))
        ref_dot(p, x + SW / 2, y + SH / 2, color)
    return centres


def row_obj(p, x, yc, row, w=40, h=32):
    for k, v in enumerate(row):
        cell(p, x + k * w, yc - h / 2, w, h, str(v), size=14,
             color=PRACTICE if v else TEXT, bold=bool(v))


# left panel
p.text_px(190, 30, "bad = [[0] * 3] * 3", PRACTICE, 14, "middle", True)
cs = outer_list(p, 60, PRACTICE)
RX, RY = 230, TOPS + 1.5 * SH
row_obj(p, RX, RY, bad[0])
for k, (x, y) in enumerate(cs):
    p.arrow((x + 4, y), (RX - 4, RY + (k - 1) * 9), PRACTICE, 1.6)
p.text_px(190, 214, "bad[0] is bad[2]  →  True", PRACTICE, 13.5, "middle")

# right panel
p.text_px(570, 30, "good: döngüyle kurulan", THEORY, 14, "middle", True)
cs = outer_list(p, 440, THEORY)
for k, (x, y) in enumerate(cs):
    row_obj(p, 610, y, good[k])
    p.arrow((x + 4, y), (606, y), THEORY, 1.6)
p.text_px(570, 214, "good[0] is good[2]  →  False", THEORY, 13.5, "middle")
p.add(f'<line x1="380" y1="20" x2="380" y2="226" stroke="{TEXT}" stroke-width="1" '
      f'opacity="0.2" stroke-dasharray="4 4"/>')
save("paylasilan-satir", figure(
    W, H, [p],
    "Solda <code>[[0] * 3] * 3</code> ifadesinin kurduğu yapı: dış listenin üç gözü de "
    "aynı satır nesnesini gösterir, bu yüzden <code>bad[0][0] = 1</code> ataması üç "
    "satırda birden görünür. Sağda döngü her turda yeni bir <code>[0] * 3</code> "
    "listesi kurar; atama yalnız ilk satırı değiştirir.",
    css_class=WIDE,
    aria="Left: three slots of an outer list all pointing to one row [1, 0, 0]. "
         "Right: three slots pointing to three separate rows [1, 0, 0], [0, 0, 0], [0, 0, 0]"))


# ============================================================
# venn: U = {1..20}, A = even numbers, B = multiples of 3
# ============================================================
U = set(range(1, 21))
A = set(range(2, 21, 2))
B = set(range(3, 21, 3))
only_a, both, only_b, rest = sorted(A - B), sorted(A & B), sorted(B - A), sorted(U - (A | B))
assert len(A | B) == 13 and len(only_a) == 7 and len(rest) == 7
W, H = 600, 360
p = canvas(W, H)
CA, CB, RR, CY = 240, 370, 120, 190
p.add(f'<rect x="20" y="40" width="560" height="300" rx="10" fill="none" '
      f'stroke="{TEXT}" stroke-opacity="0.55" stroke-width="1.3"/>')
for cx, col in ((CA, THEORY), (CB, BASE)):
    p.add(f'<circle cx="{cx}" cy="{CY}" r="{RR}" fill="{col}" fill-opacity="0.10" '
          f'stroke="{col}" stroke-width="1.8"/>')


def inside(x, y, cx):
    return (x - cx) ** 2 + (y - CY) ** 2 < RR ** 2


spots = {
    "a": [(170, 132), (220, 132), (165, 170), (215, 170), (165, 208), (215, 208), (190, 246)],
    "ab": [(305, 135), (305, 175), (305, 215)],
    "b": [(425, 150), (425, 190), (425, 230)],
    "u": [(52, 95), (305, 64), (550, 95), (52, 190), (550, 190), (52, 290), (550, 290)],
}
groups = {"a": (only_a, THEORY), "ab": (both, TEXT), "b": (only_b, BASE), "u": (rest, TEXT)}
for key, (vals, col) in groups.items():
    for v, (x, y) in zip(vals, spots[key]):
        ina, inb = inside(x, y, CA), inside(x, y, CB)
        assert (ina, inb) == {"a": (True, False), "ab": (True, True),
                              "b": (False, True), "u": (False, False)}[key]
        p.text_px(x, y + 5, str(v), col, 15, "middle", key == "ab")
p.text_px(140, 92, "A", THEORY, 15.5, "middle", True)
p.text_px(470, 92, "B", BASE, 15.5, "middle", True)
p.text_px(34, 64, "U", TEXT, 15, "start", True)
p.text_px(205, 290, "A - B", REMARK, 13.5, "middle")
p.text_px(305, 262, "A &amp; B", REMARK, 13.5, "middle")
p.text_px(408, 290, "B - A", REMARK, 13.5, "middle")
p.text_px(32, 330, "U - (A | B)", REMARK, 13.5, "start")
save("venn", figure(
    W, H, [p],
    "<em>U</em> = {1, …, 20} içinde <em>A</em> çift sayılar, <em>B</em> 3'ün katları. "
    "Her bölgedeki sayılar, altındaki Python ifadesinin verdiği kümedir: "
    "<code>A - B</code> yedi, <code>A &amp; B</code> üç, <code>B - A</code> üç, "
    "<code>U - (A | B)</code> yedi eleman içerir.",
    aria="Venn diagram inside the rectangle U = 1..20: circle A of even numbers and circle "
         "B of multiples of 3; A only holds 2 4 8 10 14 16 20, the overlap 6 12 18, "
         "B only 3 9 15 and the outside 1 5 7 11 13 17 19"))


# ============================================================
# pascal-mod2: parity of the first 32 rows of Pascal's triangle
# ============================================================
rows = [[1]]
for n in range(1, 32):
    prev = rows[-1]
    rows.append([x + y for x, y in zip([0] + prev, prev + [0])])
assert sum(1 for r in rows for c in r if c % 2 == 1) == 3 ** 5
W, H = 520, 470
p = canvas(W, H)
DX, DY, XC, YT, RAD = 14, 14 * math.sqrt(3) / 2, 270, 50, 5.4
for n, r in enumerate(rows):
    for k, c in enumerate(r):
        x, y = XC + (k - n / 2) * DX, YT + n * DY
        if c % 2:
            p.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{RAD}" fill="{THEORY}"/>')
        else:
            p.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{RAD - 0.6}" fill="none" '
                  f'stroke="{TEXT}" stroke-opacity="0.35" stroke-width="1"/>')
    if n in (0, 8, 16, 24, 31):
        p.text_px(XC - n / 2 * DX - 14, YT + n * DY + 5, f"n = {n}", TEXT, 15, "end")
LX0, LY0 = 400, 60
p.add(f'<circle cx="{LX0}" cy="{LY0}" r="{RAD}" fill="{THEORY}"/>')
p.text_px(LX0 + 12, LY0 + 5, "tek", TEXT, 15)
p.add(f'<circle cx="{LX0}" cy="{LY0 + 26}" r="{RAD - 0.6}" fill="none" stroke="{TEXT}" '
      f'stroke-opacity="0.35" stroke-width="1"/>')
p.text_px(LX0 + 12, LY0 + 31, "çift", TEXT, 15)
save("pascal-mod2", figure(
    W, H, [p],
    "Pascal üçgeninin ilk 32 satırı (<em>n</em> = 0, …, 31); her nokta bir binom "
    "katsayısıdır. Dolu noktalar tek, boş noktalar çift katsayılardır. Satırlar koddaki "
    "<code>zip</code> kuralıyla üretildi; tek katsayılar Sierpinski üçgenini çizer ve "
    "sayıları 3<sup>5</sup> = 243'tür.",
    aria="The first 32 rows of Pascal's triangle as dots, filled for odd and hollow for "
         "even binomial coefficients, forming the Sierpinski triangle"))


# ============================================================
# iki-zar: distribution of the sum of two dice via itertools.product
# ============================================================
sums = Counter(x + y for x, y in product(range(1, 7), repeat=2))
assert sum(sums.values()) == 36 and sums[7] == 6
W, H = 560, 300
p = Plot(70, 40, 440, 200, (1.4, 12.6), (0, 6.6))
p.grid(ys=range(1, 7))
p.axes(range(2, 13), range(0, 7), "toplam", "")
p.text_px(70, 24, "sonuç sayısı", TEXT, 13, "middle", italic=True)
for s in sorted(sums):
    x0, x1 = p.X(s - 0.36), p.X(s + 0.36)
    y1 = p.Y(sums[s])
    p.add(f'<rect x="{x0:.1f}" y="{y1:.1f}" width="{x1 - x0:.1f}" height="{p.Y(0) - y1:.1f}" '
          f'fill="{THEORY}" fill-opacity="{0.85 if s == 7 else 0.45}" rx="1.5"/>')
    p.label(s, sums[s], str(sums[s]), 0, -7, THEORY, 13, "middle", s == 7)
p.label(7, 6, "6/36 = 1/6", 26, -2, PRACTICE, 13.5, "start", True)
save("iki-zar", figure(
    W, H, [p],
    "İki zarın toplamı için <code>product(range(1, 7), repeat=2)</code> ile sayılan 36 "
    "sonucun dağılımı. Çubuk yükseklikleri <code>Counter</code> nesnesindeki sayılardır; "
    "en olası toplam 7'dir.",
    aria="Bar chart of the number of outcomes for each sum of two dice, 2 to 12: "
         "1 2 3 4 5 6 5 4 3 2 1"))


# ============================================================
# kalbur: the sieve of Eratosthenes on 1..100
# ============================================================
N = 100
is_prime = [True] * (N + 1)
is_prime[0] = is_prime[1] = False
first_hit = {}                              # composite -> the prime that crossed it first
q = 2
while q * q <= N:
    if is_prime[q]:
        for m in range(q * q, N + 1, q):
            if is_prime[m]:
                first_hit[m] = q
        is_prime[q * q::q] = [False] * len(range(q * q, N + 1, q))
    q += 1
assert sum(is_prime) == 25 and set(first_hit.values()) == {2, 3, 5, 7}
SHADE = {2: (TEXT, 0.10), 3: (THEORY, 0.24), 5: (BASE, 0.28), 7: (REMARK, 0.40)}
W, H = 460, 530
p = canvas(W, H)
G0X, G0Y, CS = 20, 20, 42
for n in range(1, N + 1):
    r, c = divmod(n - 1, 10)
    x, y = G0X + c * CS, G0Y + r * CS
    if is_prime[n]:
        cell(p, x, y, CS, CS, str(n), fill=PRACTICE, fill_op=0.26, stroke=TEXT,
             stroke_op=0.35, width=1, color=PRACTICE, size=15, bold=True)
    elif n in first_hit:
        col, op = SHADE[first_hit[n]]
        cell(p, x, y, CS, CS, str(n), fill=col, fill_op=op, stroke=TEXT, stroke_op=0.35,
             width=1, size=15)
    else:
        cell(p, x, y, CS, CS, str(n), stroke=TEXT, stroke_op=0.35, width=1, size=15)
for q in (2, 3, 5, 7):                      # the crossing of q starts at q*q
    r, c = divmod(q * q - 1, 10)
    col = SHADE[q][0]
    p.add(f'<rect x="{G0X + c * CS + 2:.1f}" y="{G0Y + r * CS + 2:.1f}" width="{CS - 4}" '
          f'height="{CS - 4}" fill="none" stroke="{col}" stroke-width="2.6"/>')
legend = [("asal", PRACTICE, 0.26), ("2 ile elenen", TEXT, 0.10),
          ("3 ile elenen", THEORY, 0.24), ("5 ile elenen", BASE, 0.28),
          ("7 ile elenen", REMARK, 0.40)]
LY = G0Y + 10 * CS + 26
for i, (s, col, op) in enumerate(legend):
    lx = G0X + (i % 3) * 140
    ly = LY + (i // 3) * 30
    cell(p, lx, ly - 13, 18, 18, "", fill=col, fill_op=op, stroke=TEXT, stroke_op=0.35,
         width=1)
    p.text_px(lx + 26, ly + 1, s, TEXT, 14)
lx, ly = G0X + 2 * 140, LY + 30
p.add(f'<rect x="{lx:.1f}" y="{ly - 13:.1f}" width="18" height="18" fill="none" '
      f'stroke="{TEXT}" stroke-width="2.6"/>')
p.text_px(lx + 26, ly + 1, "eleme başı p²", TEXT, 14)
save("kalbur", figure(
    W, H, [p],
    "Eratosthenes kalburu 1'den 100'e kadar. Her bileşik sayı, onu ilk kez eleyen asalın "
    "rengini taşır; bu asal, sayının en küçük asal bölenidir. Kalın çerçeveli 4, 9, 25 ve "
    "49, sırasıyla 2, 3, 5 ve 7 ile elemenin başladığı <em>p</em>² sayılarıdır. "
    "&#8730;100 = 10 olduğundan 7'den sonra eleme gerekmez; 1 dışında elenmeden kalan "
    "25 sayı asaldır.",
    aria="A 10 by 10 grid of the numbers 1 to 100; the 25 primes are highlighted and every "
         "composite is shaded by its smallest prime factor 2, 3, 5 or 7; the squares "
         "4, 9, 25, 49 have thick frames"))
