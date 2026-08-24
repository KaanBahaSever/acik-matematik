# -*- coding: utf-8 -*-
"""
Generates the SVG figures used in the "Kriptografi" (Cryptography) chapters.

The figures are NOT produced at build time: run this script, then
scripts/center_figures.py "crypto-*.md" (which measures each drawing and
centers it in its viewBox), and paste the resulting markup into the .qmd
files — always OUTSIDE definition/theorem boxes. Building the books
therefore needs neither Python nor Jupyter; CI runs Quarto alone.

The captions are Turkish on purpose — they are the text shown on the site.

Usage:   python scripts/crypto_figures.py && python scripts/center_figures.py "crypto-*.md"
Output:  scripts/_figures/crypto-<name>.md
"""
import io
import math  # noqa: F401 — used by figure sections
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8")
from svg_plot import *  # noqa: E402,F403 — Plot, figure, colors, helpers

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_figures")
os.makedirs(OUT_DIR, exist_ok=True)
OUT = {}

# ############################################################################
# PART: Skytale
# ############################################################################

"""Figures for the skytale chapter (Kriptografi / Klasik Kriptografi I).

Two block diagrams drawn in raw pixel coordinates on a dummy panel:
  skytale-silindir : the rod with the wound band, letters in three rows,
                     and the unwound strip with the scrambled order
  skytale-izgara   : the 3x5 grid with write (row) / read (column) arrows
"""
def parrow(p, x0, y0, x1, y1, color, width=1.8, head=8.0, dash=None, opacity=1.0):
    """Straight arrow in PIXEL coordinates with a filled head."""
    dx, dy = x1 - x0, y1 - y0
    length = math.hypot(dx, dy) or 1.0
    ux, uy = dx / length, dy / length
    sx, sy = x1 - ux * head * 0.8, y1 - uy * head * 0.8
    da = f' stroke-dasharray="{dash}"' if dash else ""
    p.add(f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{sx:.1f}" y2="{sy:.1f}" '
          f'stroke="{color}" stroke-width="{width}"{da} opacity="{opacity}" stroke-linecap="round"/>')
    px, py = -uy, ux
    hw = head * 0.42
    p.add(f'<polygon points="{x1:.1f},{y1:.1f} {x1-ux*head+px*hw:.1f},{y1-uy*head+py*hw:.1f} '
          f'{x1-ux*head-px*hw:.1f},{y1-uy*head-py*hw:.1f}" fill="{color}" opacity="{opacity}"/>')


# ============================================================ skytale-silindir
# The message SALDIRISAFAKTA + X pad, written in 3 rows onto 5 windings.
ROWS = [["S", "A", "L", "D", "I"],
        ["R", "I", "&#350;", "A", "F"],
        ["A", "K", "T", "A", "X"]]
CT = ["S", "R", "A", "A", "I", "K", "L", "&#350;", "T", "D", "A", "A", "I", "F", "X"]

W1, H1 = 520, 276
p = Plot(0, 0, W1, H1, (0, W1), (0, H1))

# rod ends sticking out of the band
for rx0 in (44, 386):
    p.add(f'<rect x="{rx0}" y="94" width="50" height="32" rx="9" '
          f'fill="{REMARK}" fill-opacity="0.16" stroke="{REMARK}" stroke-width="1.2"/>')
# cylinder body
p.add(f'<rect x="90" y="70" width="300" height="80" rx="16" '
      f'fill="{THEORY}" fill-opacity="0.07" stroke="{THEORY}" stroke-width="1.6"/>')

# five windings of the band as diagonal stripes (top x0 = 108 + 50k, slant 16)
for k in range(5):
    xt = 108 + 50 * k
    op = 0.16 if k % 2 == 0 else 0.09
    p.add(f'<polygon points="{xt},70 {xt+50},70 {xt+66},150 {xt+16},150" '
          f'fill="{BASE}" fill-opacity="{op}" stroke="{BASE}" stroke-width="1.2" stroke-opacity="0.75"/>')

# the letters: three rows along the rod, one letter per winding
for r, (by, shift) in enumerate([(96, 4.4), (118, 8.8), (140, 13.2)]):
    for k, ch in enumerate(ROWS[r]):
        col = REMARK if ch == "X" else TEXT
        p.text_px(133 + 50 * k + shift, by, ch, col, 13, "middle", bold=True)

# writing direction arrow along the rod
parrow(p, 100, 52, 250, 52, THEORY, 1.8)
p.text_px(100, 40, "yazma y&#246;n&#252;: silindir boyunca", THEORY, 11.5)

# "deri şerit" pointer to a winding
p.text_px(398, 40, "deri &#351;erit", REMARK, 11.5, "middle", italic=True)
parrow(p, 392, 46, 345, 66, REMARK, 1.3, head=6.5)

# the diameter is the key
p.add(f'<line x1="392" y1="70" x2="444" y2="70" stroke="{REMARK}" stroke-width="1" '
      f'stroke-dasharray="3 3" opacity="0.55"/>')
p.add(f'<line x1="392" y1="150" x2="444" y2="150" stroke="{REMARK}" stroke-width="1" '
      f'stroke-dasharray="3 3" opacity="0.55"/>')
parrow(p, 452, 108, 452, 72, PRACTICE, 1.8, head=7.0)
parrow(p, 452, 112, 452, 148, PRACTICE, 1.8, head=7.0)
p.text_px(452, 168, "&#231;ap = anahtar", PRACTICE, 11.5, "middle", bold=True)

# unwind arrow + the unwound strip
parrow(p, 240, 158, 240, 196, REMARK, 1.6)
p.text_px(252, 182, "&#351;eridi &#231;&#246;z", REMARK, 11.5, italic=True)

p.add(f'<rect x="50" y="206" width="420" height="30" rx="4" '
      f'fill="{BASE}" fill-opacity="0.08" stroke="{BASE}" stroke-width="1.5"/>')
for b in range(1, 5):  # winding boundaries: every 3 letters
    xb = 50 + 84 * b
    p.add(f'<line x1="{xb+3}" y1="206" x2="{xb-3}" y2="236" stroke="{BASE}" '
          f'stroke-width="1.2" opacity="0.6"/>')
for i, ch in enumerate(CT):
    col = REMARK if ch == "X" else TEXT
    p.text_px(64 + 28 * i, 226, ch, col, 12.5, "middle", bold=True)
p.text_px(260, 258, "&#231;&#246;z&#252;lm&#252;&#351; &#351;erit: harfler sarg&#305; sarg&#305; (s&#252;tun s&#252;tun) dizilir", TEXT, 11.5, "middle")

OUT["skytale-silindir"] = figure(
    W1, H1, [p],
    "SALDIRI &#350;AFAKTA mesaj&#305; (dolgu harfi X ile) silindire sar&#305;l&#305; deri &#351;eride "
    "&#252;&#231; s&#305;ra h&#226;linde, silindir boyunca yaz&#305;l&#305;r. &#350;erit &#231;&#246;z&#252;ld&#252;&#287;&#252;nde harfler sarg&#305; "
    "sarg&#305; okunur ve ortaya SRAAIKL&#350;TDAAIFX kar&#305;&#351;&#305;k dizisi &#231;&#305;kar. Mesaj&#305;, ancak ayn&#305; "
    "&#231;apta bir silindire sahip olan ki&#351;i geri sararak okuyabilir.",
    aria="Skytale: silindire sarili seritte uc sira harf ve cozulmus seridin karisik harf sirasi")

# ============================================================ skytale-izgara
W2, H2 = 432, 234
p = Plot(0, 0, W2, H2, (0, W2), (0, H2))

CW, CH, GX, GY = 44, 36, 120, 64  # cell size, grid top-left
for r in range(3):
    for c in range(5):
        if c == 0:
            fill, op, stroke = PRACTICE, 0.13, PRACTICE
        else:
            fill, op, stroke = THEORY, 0.07, THEORY
        p.add(f'<rect x="{GX+c*CW}" y="{GY+r*CH}" width="{CW}" height="{CH}" rx="4" '
              f'fill="{fill}" fill-opacity="{op}" stroke="{stroke}" stroke-width="1.3"/>')
for r in range(3):
    for c in range(5):
        ch = ROWS[r][c]
        col = PRACTICE if c == 0 else (REMARK if ch == "X" else TEXT)
        p.text_px(GX + c * CW + CW / 2, GY + r * CH + 22.5, ch, col, 13, "middle", bold=True)

# write direction (rows) and read direction (columns)
parrow(p, GX, 50, GX + 5 * CW, 50, THEORY, 1.8)
p.text_px(GX + 2.5 * CW, 36, "yazma: sat&#305;r sat&#305;r", THEORY, 11.5, "middle")
parrow(p, 104, GY, 104, GY + 3 * CH, PRACTICE, 1.8)
p.text_px(96, 112, "okuma:", PRACTICE, 11, "end")
p.text_px(96, 126, "s&#252;tun s&#252;tun", PRACTICE, 11, "end")

# m and n annotations
p.text_px(352, 113, "m = 3 sat&#305;r", TEXT, 11.5, italic=True)
p.text_px(352, 127, "(anahtar)", REMARK, 10.5)
p.text_px(GX + 2.5 * CW, 190, "n = 5 s&#252;tun", REMARK, 11)

# assembled ciphertext, first column highlighted
p.add(f'<text x="{GX + 2.5 * CW:.1f}" y="214" fill="{TEXT}" font-size="12.5" text-anchor="middle">'
      f'&#351;ifreli metin: <tspan fill="{PRACTICE}" font-weight="600">SRA</tspan> '
      f'AIK L&#350;T DAA IFX</text>')

OUT["skytale-izgara"] = figure(
    W2, H2, [p],
    "Sarmak, mesaj&#305; 3 &#215; 5&#8217;lik &#305;zgaraya sat&#305;r sat&#305;r yazmakt&#305;r; &#351;ifrelemek ise ayn&#305; "
    "&#305;zgaray&#305; s&#252;tun s&#252;tun okumakt&#305;r. K&#305;rm&#305;z&#305; s&#252;tun, &#351;ifreli metnin ilk &#252;&#231; harfini "
    "verir; X yaln&#305;zca &#305;zgaray&#305; tamamlayan dolgu harfidir.",
    aria="Izgara modeli: satir satir yazma ve sutun sutun okuma yonleri")

# ############################################################################
# PART: Zigzag ve Rota
# ############################################################################

"""Figures for the rail-fence / route cipher chapter
(kriptografi/klasik-kriptografi-1/zigzag-rota.qmd).

All drawing happens in PIXEL coordinates on a single Plot panel per figure:
p = Plot(0, 0, W, H, (0, W), (0, H)) plus raw SVG via p.add / p.text_px.
"""
# Turkish diacritics -> HTML entities (SVG text and captions)
_TR = {"ı": "&#305;", "ğ": "&#287;", "ş": "&#351;", "ç": "&#231;",
       "ö": "&#246;", "ü": "&#252;", "İ": "&#304;", "Ğ": "&#286;",
       "Ş": "&#350;", "Ç": "&#199;", "Ö": "&#214;", "Ü": "&#220;"}


def tr(s):
    for k, v in _TR.items():
        s = s.replace(k, v)
    return s


def head_at(p, x0, y0, x1, y1, t, color, head=6.5, opacity=0.8):
    """Small filled arrowhead placed at parameter t of the segment, oriented along it."""
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy) or 1.0
    ux, uy = dx / L, dy / L
    mx, my = x0 + dx * t, y0 + dy * t
    nx, ny = -uy, ux
    hw = head * 0.42
    p.add(f'<polygon points="{mx:.1f},{my:.1f} '
          f'{mx - ux * head + nx * hw:.1f},{my - uy * head + ny * hw:.1f} '
          f'{mx - ux * head - nx * hw:.1f},{my - uy * head - ny * hw:.1f}" '
          f'fill="{color}" opacity="{opacity}"/>')


def arr(p, x0, y0, x1, y1, color=TEXT, width=1.6, head=7.0, opacity=0.8):
    """Straight arrow in pixel coordinates with a filled head."""
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy) or 1.0
    ux, uy = dx / L, dy / L
    sx, sy = x1 - ux * head * 0.8, y1 - uy * head * 0.8
    p.add(f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{sx:.1f}" y2="{sy:.1f}" '
          f'stroke="{color}" stroke-width="{width}" opacity="{opacity}" stroke-linecap="round"/>')
    head_at(p, x0, y0, x1, y1, 1.0, color, head, opacity)


def token(p, x, y, ch, color, r=10.0, size=13):
    """Letter on a page-background disk so the path threads between the letters."""
    p.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{BG}"/>')
    p.text_px(x, y + 4.5, ch, color, size, "middle", bold=True)


# ============================================================ zigzag-raylar
# The 3-rail zigzag of MATEMATIKGUZELDIR: letters at the wave vertices,
# faint rail lines, thin arrows along the path, read-out line below.
MSG = "MATEMATİKGÜZELDİR"          # 17 letters, spaces already dropped
K = 3
PERIOD = 2 * (K - 1)                # 4
pattern = [(i % PERIOD) if (i % PERIOD) < K else PERIOD - (i % PERIOD)
           for i in range(len(MSG))]
RAIL_COLORS = [THEORY, PRACTICE, BASE]

W, H = 580, 208
p = Plot(0, 0, W, H, (0, W), (0, H))
X0, DX = 70, 30
YS = (52, 100, 148)
xs = [X0 + i * DX for i in range(len(MSG))]

# faint rail lines behind everything
for y in YS:
    p.add(f'<line x1="{X0 - 14}" y1="{y}" x2="{xs[-1] + 14}" y2="{y}" '
          f'stroke="{REMARK}" stroke-width="1" opacity="0.30"/>')

# rail labels on the left
for j, y in enumerate(YS):
    p.text_px(14, y + 4, tr(f"{j + 1}. ray"), RAIL_COLORS[j], 11.5, "start", bold=True)

# one-period bracket over the first wave (positions 0..4)
bx0, bx1, by = xs[0], xs[4], 28
p.add(f'<g stroke="{REMARK}" stroke-width="1.2" opacity="0.8">'
      f'<line x1="{bx0}" y1="{by}" x2="{bx1}" y2="{by}"/>'
      f'<line x1="{bx0}" y1="{by}" x2="{bx0}" y2="{by + 6}"/>'
      f'<line x1="{bx1}" y1="{by}" x2="{bx1}" y2="{by + 6}"/></g>')
p.text_px((bx0 + bx1) / 2, 18, tr("bir periyot: 2(k&#8722;1) = 4 adım"),
          REMARK, 11, "middle", italic=True)

# the zigzag path: thin polyline + a small arrowhead on every segment
pts = [(xs[i], YS[pattern[i]]) for i in range(len(MSG))]
d = " ".join(("M" if i == 0 else "L") + f"{x},{y}" for i, (x, y) in enumerate(pts))
p.add(f'<path d="{d}" fill="none" stroke="{REMARK}" stroke-width="1.3" '
      f'opacity="0.6" stroke-linejoin="round"/>')
for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
    head_at(p, xa, ya, xb, yb, 0.62, REMARK, 6.0, 0.75)

# letters as tokens, colored by rail
for i, ch in enumerate(MSG):
    token(p, xs[i], YS[pattern[i]], tr(ch), RAIL_COLORS[pattern[i]])

# read-out line: ciphertext grouped by rail color
p.add(f'<text x="{W / 2}" y="190" font-size="12.5" text-anchor="middle" fill="{TEXT}">'
      f'<tspan font-style="italic">{tr("şifreli metin:")}</tspan>'
      f'<tspan font-weight="600" fill="{THEORY}" dx="7">MMKER</tspan>'
      f'<tspan dx="6">+</tspan>'
      f'<tspan font-weight="600" fill="{PRACTICE}" dx="6">{tr("AEAİGZLİ")}</tspan>'
      f'<tspan dx="6">+</tspan>'
      f'<tspan font-weight="600" fill="{BASE}" dx="6">{tr("TTÜD")}</tspan></text>')

OUT["zigzag-raylar"] = figure(
    W, H, [p],
    tr("Üç ray üzerinde zigzag: MATEMATİKGÜZELDİR mesajının harfleri, ince oklarla "
       "gösterilen aşağı–yukarı dalgalanan yol boyunca sırayla yerleştirilir; desen her "
       "2(<em>k</em>&#8722;1) = 4 adımda bir tekrarlanır. Şifreli metin raylar tek tek "
       "okunarak oluşur: önce 1. ray (MMKER), sonra 2. (AEAİGZLİ), en son 3. (TTÜD)."),
    css_class=WIDE,
    aria="Uc ray uzerinde zigzag yolu: harfler dalga boyunca dizilir, raylar sirayla okunur")

# ============================================================ zigzag-rota-spirali
# 3x4 grid with GIZLIMEKTUPX and the clockwise inward spiral reading route.
GRID = ["GİZL", "İMEK", "TUPX"]
M, N = 3, 4


def spiral_cw(m, n):
    top, bottom, left, right = 0, m - 1, 0, n - 1
    order = []
    while top <= bottom and left <= right:
        for c in range(left, right + 1):
            order.append((top, c))
        top += 1
        for r in range(top, bottom + 1):
            order.append((r, right))
        right -= 1
        if top <= bottom:
            for c in range(right, left - 1, -1):
                order.append((bottom, c))
            bottom -= 1
        if left <= right:
            for r in range(bottom, top - 1, -1):
                order.append((r, left))
            left += 1
    return order


W, H = 400, 252
p = Plot(0, 0, W, H, (0, W), (0, H))
CELL, GX, GY = 52, 96, 44


def center(rc):
    r, c = rc
    return (GX + c * CELL + CELL / 2, GY + r * CELL + CELL / 2)


# cells
for r in range(M):
    for c in range(N):
        p.add(f'<rect x="{GX + c * CELL}" y="{GY + r * CELL}" width="{CELL}" height="{CELL}" '
              f'rx="4" fill="{THEORY}" fill-opacity="0.10" stroke="{THEORY}" stroke-width="1.4"/>')

order = spiral_cw(M, N)

# reading-order numbers in the top-right corner of each cell
for idx, (r, c) in enumerate(order, start=1):
    p.text_px(GX + c * CELL + CELL - 6, GY + r * CELL + 13, str(idx),
              REMARK, 9, "end")

# the spiral route through the cell centers (trimmed before the last letter)
cs = [center(rc) for rc in order]
lx, ly = cs[-1]
px_, py_ = cs[-2]
ux, uy = (lx - px_) / math.hypot(lx - px_, ly - py_), (ly - py_) / math.hypot(lx - px_, ly - py_)
tip = (lx - ux * 17, ly - uy * 17)
d = " ".join(("M" if i == 0 else "L") + f"{x:.1f},{y:.1f}" for i, (x, y) in enumerate(cs[:-1]))
p.add(f'<path d="{d}" fill="none" stroke="{PRACTICE}" stroke-width="2.4" '
      f'opacity="0.9" stroke-linejoin="round" stroke-linecap="round"/>')
arr(p, px_, py_, tip[0], tip[1], PRACTICE, 2.4, 8.0, 0.9)

# letters as tokens on top of the route
for r in range(M):
    for c in range(N):
        x, y = center((r, c))
        token(p, x, y, tr(GRID[r][c]), TEXT, 11, 14)

# starting corner marker
p.text_px(GX - 4, 24, tr("başlangıç köşesi"), PRACTICE, 11, "start", italic=True)
arr(p, GX + 14, 29, GX + 24, GY + 12, PRACTICE, 1.4, 6.5, 0.85)

# ciphertext under the grid
p.add(f'<text x="{W / 2}" y="{GY + M * CELL + 34}" font-size="12.5" text-anchor="middle" fill="{TEXT}">'
      f'<tspan font-style="italic">{tr("şifreli metin:")}</tspan>'
      f'<tspan font-weight="600" fill="{PRACTICE}" dx="7">{tr("GİZLKXPUTİME")}</tspan></text>')

OUT["zigzag-rota-spirali"] = figure(
    W, H, [p],
    tr("Rota şifresi: GİZLİMEKTUPX metni 3&#215;4 tabloya satır satır yazılır, sonra sol üst "
       "köşeden başlayıp saat yönünde içe kıvrılan spiral rota boyunca okunur; köşelerdeki "
       "küçük sayılar okuma sırasını gösterir. Sonuç: GİZLKXPUTİME."),
    aria="Uc carpi dort tabloda saat yonunde ice kivrilan spiral okuma rotasi")

# ############################################################################
# PART: Bacon Şifreleme
# ############################################################################

"""Block diagrams for the Bacon cipher chapter
(kriptografi/klasik-kriptografi-1/bacon-sifreleme.qmd).

All drawing is done in PIXEL coordinates on a single Plot panel per figure:
p = Plot(0, 0, W, H, (0, W), (0, H)) and raw SVG via p.add / p.text_px.
"""
# Turkish diacritics -> HTML entities (SVG text and captions)
_TR = {"ı": "&#305;", "ğ": "&#287;", "ş": "&#351;", "ç": "&#231;",
       "ö": "&#246;", "ü": "&#252;", "İ": "&#304;", "Ğ": "&#286;",
       "Ş": "&#350;", "Ç": "&#199;", "Ö": "&#214;", "Ü": "&#220;"}


def tr(s):
    for k, v in _TR.items():
        s = s.replace(k, v)
    return s


ARR = "&#8594;"      # right arrow
GEQ = "&#8805;"      # >=
CDOT = "&#183;"      # middle dot


def rect(p, x, y, w, h, color, opacity=0.10, lw=1.6, dash=None, rx=6):
    da = f' stroke-dasharray="{dash}"' if dash else ""
    p.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
          f'fill="{color}" fill-opacity="{opacity}" stroke="{color}" stroke-width="{lw}"{da}/>')


def arr(p, x0, y0, x1, y1, color=TEXT, width=1.6, head=7.0, opacity=0.7, dash=None):
    """Straight arrow in pixel coordinates with a filled head."""
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy) or 1.0
    ux, uy = dx / L, dy / L
    sx, sy = x1 - ux * head * 0.8, y1 - uy * head * 0.8
    da = f' stroke-dasharray="{dash}"' if dash else ""
    p.add(f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{sx:.1f}" y2="{sy:.1f}" '
          f'stroke="{color}" stroke-width="{width}"{da} opacity="{opacity}" stroke-linecap="round"/>')
    nx, ny = -uy, ux
    hw = head * 0.42
    p.add(f'<polygon points="{x1:.1f},{y1:.1f} '
          f'{x1 - ux * head + nx * hw:.1f},{y1 - uy * head + ny * hw:.1f} '
          f'{x1 - ux * head - nx * hw:.1f},{y1 - uy * head - ny * hw:.1f}" '
          f'fill="{color}" opacity="{opacity}"/>')


# ============================================================ bacon-kodlama
# One letter (M) unfolding into its five two-valued a/b cells.
W, H = 400, 196
p = Plot(0, 0, W, H, (0, W), (0, H))

# the letter M at the top
rect(p, 178, 14, 44, 36, PRACTICE, opacity=0.12)
p.text_px(200, 38, "M", TEXT, 16, "middle", bold=True)
p.text_px(232, 27, tr("alfabedeki sıra numarası: 12"), REMARK, 10.5, "start")
p.text_px(232, 42, tr("(A = 0'dan sayarak)"), REMARK, 10.5, "start")

arr(p, 200, 52, 200, 82)

# five a/b cells
code = "abbaa"
for i, ch in enumerate(code):
    x = 84 + 48 * i
    cx = x + 20
    if ch == "b":
        rect(p, x, 88, 40, 40, PRACTICE, opacity=0.16)
        p.text_px(cx, 114, "b", PRACTICE, 15, "middle", bold=True)
    else:
        rect(p, x, 88, 40, 40, THEORY, opacity=0.08)
        p.text_px(cx, 114, "a", TEXT, 15, "middle")
    p.text_px(cx, 146, f"{i + 1}", REMARK, 10, "middle")

p.text_px(200, 176,
          tr(f"her yuvada 2 seçenek: 2{CDOT}2{CDOT}2{CDOT}2{CDOT}2 = 32 kalıp {GEQ} 26 harf"),
          TEXT, 11.5, "middle")

OUT["bacon-kodlama"] = figure(
    W, H, [p],
    tr("Bacon kodunda her harf, yalnızca a ve b sembollerinden oluşan beş yuvalık bir "
       "kalıba açılır: alfabede 12 numaralı harf olan M'nin kodu <code>abbaa</code>'dır. "
       "İki değerli beş yuva toplam 32 farklı kalıp üretir; bu da 26 harfin tamamına yeter."),
    aria="M harfinin bes yuvali a/b koduna acilisi: abbaa")

# ============================================================ bacon-gizleme
# The carrier sentence "Kediler süt sever" with the b-form letters set bold
# and colored; the extracted a/b string and the 5-groups decoded below.
W, H = 560, 172
p = Plot(0, 0, W, H, (0, W), (0, H))

carrier = "Kediler süt sever"
letters = [c for c in carrier if c != " "]
bits = "abbaa" + "aaaaa" + "baabb"          # MAT
breaks_before = {7: 1, 10: 2}               # word gaps after "Kediler" and "süt"


def xpos(i):
    extra = 0
    for k, n in breaks_before.items():
        if i >= k:
            extra = 14 * n
    return 46 + 30 * i + extra


p.text_px(46, 26, tr("taşıyıcı cümle (normal biçim = a, kalın biçim = b):"),
          REMARK, 11, "start")

for i, (ch, b) in enumerate(zip(letters, bits)):
    x = xpos(i)
    if b == "b":
        p.text_px(x, 64, tr(ch), PRACTICE, 17, "middle", bold=True)
        p.text_px(x, 94, "b", PRACTICE, 11.5, "middle", bold=True)
    else:
        p.text_px(x, 64, tr(ch), TEXT, 17, "middle")
        p.text_px(x, 94, "a", TEXT, 11.5, "middle")

# brackets under the three 5-groups and the decoded letters
for g, dec in enumerate("MAT"):
    x0, x1 = xpos(5 * g) - 10, xpos(5 * g + 4) + 10
    p.add(f'<path d="M{x0},102 L{x0},108 L{x1},108 L{x1},102" fill="none" '
          f'stroke="{REMARK}" stroke-width="1.4"/>')
    cx = (x0 + x1) / 2
    arr(p, cx, 112, cx, 124, REMARK, width=1.3, head=6.0)
    p.text_px(cx, 142, dec, PRACTICE, 15, "middle", bold=True)

p.text_px(270, 165, tr("beşli gruplar çözülür: gizli mesaj MAT"),
          REMARK, 11, "middle")

OUT["bacon-gizleme"] = figure(
    W, H, [p],
    tr("Gizli kanalın görünür hâli: taşıyıcı cümlenin her harfi iki biçimden birinde "
       "dizilir (normal = a, kalın = b). Harf biçimlerinden okunan a/b dizisi beşerli "
       "gruplandığında <code>abbaa&#8201;aaaaa&#8201;baabb</code>, yani MAT mesajı ortaya çıkar."),
    css_class=WIDE,
    aria="Kediler sut sever cumlesinde harf bicimlerinden a/b dizisi ve MAT cozumu")

# ############################################################################
# PART: Sonlu Cisimler
# ############################################################################

"""Figures for the "Sonlu Cisimler (Galois Cisimleri)" chapter (kriptografi)."""
def box(p, x, y, w, h, color, fill_op=0.10, sw=1.6, rx=6):
    p.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
          f'fill="{color}" fill-opacity="{fill_op}" stroke="{color}" stroke-width="{sw}"/>')


def parrow(p, x0, y0, x1, y1, color, width=1.7, head=8.0):
    """Straight arrow in PIXEL coordinates (Plot.arrow uses data coords with flipped y)."""
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy) or 1.0
    ux, uy = dx / L, dy / L
    sx, sy = x1 - ux * head * 0.8, y1 - uy * head * 0.8
    p.add(f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{sx:.1f}" y2="{sy:.1f}" '
          f'stroke="{color}" stroke-width="{width}" stroke-linecap="round"/>')
    px, py = -uy, ux
    hw = head * 0.42
    p.add(f'<polygon points="{x1:.1f},{y1:.1f} '
          f'{x1-ux*head+px*hw:.1f},{y1-uy*head+py*hw:.1f} '
          f'{x1-ux*head-px*hw:.1f},{y1-uy*head-py*hw:.1f}" fill="{color}"/>')


# ======================================================== sonlu-bayt-polinom
# One byte {57} = 01010111 read as a polynomial: the 1-bits become the terms.
W, H = 460, 190
p = Plot(0, 0, W, H, (0, W), (0, H))

p.text_px(W / 2, 20, "Bir bayt&#305; polinom olarak okumak: {57} = 01010111",
          TEXT, 12, "middle", True)

bits = [0, 1, 0, 1, 0, 1, 1, 1]          # b7 ... b0 of 0x57
SUBS = ["&#8327;", "&#8326;", "&#8325;", "&#8324;",
        "&#8323;", "&#8322;", "&#8321;", "&#8320;"]  # subscript 7..0
CX = [74 + 44 * i for i in range(8)]      # cell centers
TOP, BOT = 50, 86                          # cell top / bottom

for i, b in enumerate(bits):
    cx = CX[i]
    p.text_px(cx, TOP - 8, "b" + SUBS[i], REMARK, 10.5, "middle", False, True)
    if b:
        box(p, cx - 20, TOP, 40, BOT - TOP, PRACTICE, 0.12, 1.7)
        p.text_px(cx, TOP + 24.5, "1", PRACTICE, 15, "middle", True)
    else:
        box(p, cx - 20, TOP, 40, BOT - TOP, THEORY, 0.0, 1.2)
        p.text_px(cx, TOP + 24.5, "0", TEXT, 15, "middle")

# arrows from the 1-cells down to the polynomial terms
ones = [i for i, b in enumerate(bits) if b]           # positions 1,3,5,6,7
terms = ["x" + sup("6"), "x" + sup("4"), "x" + sup("2"), "x", "1"]
TY = 134
for i in ones:
    parrow(p, CX[i], BOT + 4, CX[i], TY - 14, REMARK, 1.4, 6.5)
for i, t in zip(ones, terms):
    p.text_px(CX[i], TY, t, PRACTICE, 13.5, "middle", True, True)
for i, j in zip(ones, ones[1:]):
    p.text_px((CX[i] + CX[j]) / 2, TY, "+", TEXT, 12.5, "middle")

p.text_px(W / 2, 168,
          "bitler = GF(2) katsay&#305;lar&#305;; polinomda yaln&#305;z 1 olan bitler g&#246;r&#252;n&#252;r",
          REMARK, 10.5, "middle")

OUT["sonlu-bayt-polinom"] = figure(
    W, H, [p],
    "Bir bayt&#305;n sekiz biti, katsay&#305;lar&#305; GF(2)'de olan bir polinomun "
    "katsay&#305; listesidir: {57} = 01010111 bayt&#305;, yaln&#305;zca 1 olan bitlerin "
    "kuvvetleri al&#305;narak <em>x</em><sup>6</sup> + <em>x</em><sup>4</sup> + "
    "<em>x</em><sup>2</sup> + <em>x</em> + 1 polinomuna d&#246;n&#252;&#351;&#252;r.",
    aria="Bir baytin sekiz bitinin GF(2) katsayili polinom terimlerine eslenmesi")


# ======================================================== sonlu-carpma-akisi
# Flow: two bytes -> polynomial product (degree up to 14) -> mod m(x) -> byte.
W, H = 560, 200
p = Plot(0, 0, W, H, (0, W), (0, H))

# input bytes (left column)
box(p, 24, 42, 104, 36, THEORY)
p.text_px(76, 65, "{57}", THEORY, 14, "middle", True)
p.text_px(76, 94, "x" + sup("6") + "+x" + sup("4") + "+x" + sup("2") + "+x+1",
          THEORY, 10.5, "middle")

box(p, 24, 112, 104, 36, THEORY)
p.text_px(76, 135, "{83}", THEORY, 14, "middle", True)
p.text_px(76, 164, "x" + sup("7") + "+x+1", THEORY, 10.5, "middle")

# middle: raw polynomial product
box(p, 192, 70, 170, 54, REMARK)
p.text_px(277, 91, "polinom &#231;arp&#305;m&#305;", TEXT, 12, "middle", True)
p.text_px(277, 110, "derece 14'e kadar", TEXT, 10.5, "middle")
p.text_px(277, 140, "bayta s&#305;&#287;maz!", PRACTICE, 10.5, "middle", True)

parrow(p, 128, 60, 190, 89, THEORY)
parrow(p, 128, 130, 190, 105, THEORY)

# right: result byte
box(p, 432, 70, 104, 54, PRACTICE)
p.text_px(484, 93, "{C1}", PRACTICE, 14, "middle", True)
p.text_px(484, 112, "x" + sup("7") + "+x" + sup("6") + "+1", PRACTICE, 10.5, "middle")
p.text_px(484, 140, "yine tek bayt", REMARK, 10.5, "middle")

parrow(p, 362, 97, 430, 97, PRACTICE)
p.text_px(396, 86, "mod m(x)", TEXT, 11.5, "middle", True)
p.text_px(396, 114, "kalan&#305; al", REMARK, 10, "middle")

p.text_px(W / 2, 186,
          "m(x) = x" + sup("8") + " + x" + sup("4") + " + x" + sup("3") +
          " + x + 1 = {11B} &#8212; AES'in sabit indirgenemez polinomu",
          TEXT, 11, "middle")

OUT["sonlu-carpma-akisi"] = figure(
    W, H, [p],
    "GF(2<sup>8</sup>)'de &#231;arpman&#305;n ak&#305;&#351;&#305;: iki bayt polinom olarak "
    "&#231;arp&#305;l&#305;r, derecesi 14'e kadar &#231;&#305;kabilen ara sonu&#231; "
    "indirgenemez m(x) polinomuna b&#246;l&#252;n&#252;p kalan al&#305;n&#305;r ve sonu&#231; "
    "yeniden tek bir bayta s&#305;&#287;ar: {57} &#183; {83} = {C1}.",
    css_class=WIDE,
    aria="Iki baytin polinom carpimi ve m(x) ile indirgeme akis semasi")

# ############################################################################
# PART: DES ve 3DES
# ############################################################################

"""Block/flow diagrams for the DES chapter (kriptografi/simetrik/blok-sifreler/des.qmd).

All drawing is done in PIXEL coordinates on a single Plot panel per figure:
p = Plot(0, 0, W, H, (0, W), (0, H)) and raw SVG via p.add / p.text_px.
"""
# Turkish diacritics -> HTML entities (SVG text and captions)
_TR = {"ı": "&#305;", "ğ": "&#287;", "ş": "&#351;", "ç": "&#231;",
       "ö": "&#246;", "ü": "&#252;", "İ": "&#304;", "Ğ": "&#286;",
       "Ş": "&#350;", "Ç": "&#199;", "Ö": "&#214;", "Ü": "&#220;"}


def tr(s):
    for k, v in _TR.items():
        s = s.replace(k, v)
    return s


XOR = "&#8853;"      # circled plus
ARR = "&#8594;"      # right arrow
DOTS = "&#8942;"     # vertical ellipsis
HELLIP = "&#8230;"   # horizontal ellipsis
MID = "&#8722;"      # minus sign


def sub(s, size=9):
    """Subscript inside an SVG <text> (mirror of svg_plot.sup)."""
    return f'<tspan font-size="{size}" dy="4">{s}</tspan><tspan dy="-4">&#8203;</tspan>'


def rect(p, x, y, w, h, color, opacity=0.10, lw=1.6, dash=None, rx=6):
    da = f' stroke-dasharray="{dash}"' if dash else ""
    p.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
          f'fill="{color}" fill-opacity="{opacity}" stroke="{color}" stroke-width="{lw}"{da}/>')


def bx(p, x, y, w, h, color, label, size=11.5, bold=True, sub_label=None):
    """Rounded box with a centred label (optional smaller second line)."""
    rect(p, x, y, w, h, color)
    if sub_label is None:
        p.text_px(x + w / 2, y + h / 2 + 4, tr(label), TEXT, size, "middle", bold=bold)
    else:
        p.text_px(x + w / 2, y + h / 2 - 3, tr(label), TEXT, size, "middle", bold=bold)
        p.text_px(x + w / 2, y + h / 2 + 12, tr(sub_label), TEXT, 10.5, "middle")


def arr(p, x0, y0, x1, y1, color=TEXT, width=1.6, head=7.0, opacity=0.7, dash=None):
    """Straight arrow in pixel coordinates with a filled head."""
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy) or 1.0
    ux, uy = dx / L, dy / L
    sx, sy = x1 - ux * head * 0.8, y1 - uy * head * 0.8
    da = f' stroke-dasharray="{dash}"' if dash else ""
    p.add(f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{sx:.1f}" y2="{sy:.1f}" '
          f'stroke="{color}" stroke-width="{width}"{da} opacity="{opacity}" stroke-linecap="round"/>')
    nx, ny = -uy, ux
    hw = head * 0.42
    p.add(f'<polygon points="{x1:.1f},{y1:.1f} '
          f'{x1 - ux * head + nx * hw:.1f},{y1 - uy * head + ny * hw:.1f} '
          f'{x1 - ux * head - nx * hw:.1f},{y1 - uy * head - ny * hw:.1f}" '
          f'fill="{color}" opacity="{opacity}"/>')


def xor_node(p, cx, cy, r=11, color=PRACTICE):
    p.add(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{BG}" stroke="{color}" stroke-width="1.8"/>')
    p.add(f'<line x1="{cx - r + 3}" y1="{cy}" x2="{cx + r - 3}" y2="{cy}" stroke="{color}" stroke-width="1.6"/>')
    p.add(f'<line x1="{cx}" y1="{cy - r + 3}" x2="{cx}" y2="{cy + r - 3}" stroke="{color}" stroke-width="1.6"/>')


# ============================================================ des-genel-yapi
# Vertical overall flow: plaintext -> IP -> L0|R0 -> 16 Feistel rounds
# (fed by the key schedule) -> swap -> IP^-1 -> ciphertext.
W, H = 460, 496
p = Plot(0, 0, W, H, (0, W), (0, H))
CX, BX0, BW = 165, 60, 210   # main column

bx(p, BX0, 18, BW, 34, BASE, "64 bitlik açık metin bloğu")
arr(p, CX, 52, CX, 68)
bx(p, BX0, 70, BW, 34, REMARK, "başlangıç permütasyonu IP")
arr(p, CX, 104, CX, 120)
bx(p, BX0, 122, 103, 30, THEORY, "L" + sub("0") + " (32 bit)", bold=False)
bx(p, BX0 + 107, 122, 103, 30, THEORY, "R" + sub("0") + " (32 bit)", bold=False)
arr(p, CX, 152, CX, 168)

# big Feistel box with two sample rounds inside
rect(p, BX0, 170, BW, 130, THEORY)
p.text_px(CX, 188, tr("16 Feistel döngüsü"), TEXT, 12, "middle", bold=True)
rect(p, 80, 198, 170, 26, THEORY, opacity=0.16, lw=1.1, rx=4)
p.text_px(CX, 215, tr("1. döngü — K") + sub("1"), TEXT, 11, "middle")
p.text_px(CX, 242, DOTS, TEXT, 12, "middle")
rect(p, 80, 252, 170, 26, THEORY, opacity=0.16, lw=1.1, rx=4)
p.text_px(CX, 269, tr("16. döngü — K") + sub("16"), TEXT, 11, "middle")

# key schedule box on the right feeding the rounds
rect(p, 302, 200, 148, 82, PRACTICE)
p.text_px(376, 226, tr("anahtar üretimi"), TEXT, 11.5, "middle", bold=True)
p.text_px(376, 242, "(key schedule)", TEXT, 10.5, "middle")
p.text_px(376, 262, "K" + sub("1") + " " + HELLIP + " K" + sub("16"), TEXT, 11.5, "middle")
arr(p, 302, 211, 254, 211, PRACTICE, opacity=0.85)
arr(p, 302, 265, 254, 265, PRACTICE, opacity=0.85)

arr(p, CX, 300, CX, 316)
bx(p, BX0, 318, BW, 40, THEORY, "son takas (swap)",
   sub_label="(L" + sub("16") + ", R" + sub("16") + ") " + ARR + " (R" + sub("16") + ", L" + sub("16") + ")")
arr(p, CX, 358, CX, 374)
bx(p, BX0, 376, BW, 34, REMARK, "ters permütasyon IP" + sup(MID + "1"))
arr(p, CX, 410, CX, 426)
bx(p, BX0, 428, BW, 34, BASE, "64 bitlik şifreli metin bloğu")

OUT["des-genel-yapi"] = figure(
    W, H, [p],
    tr("DES'in kuşbakışı akışı: 64 bitlik blok başlangıç permütasyonu IP'den geçip iki yarıya bölünür, "
       "anahtar üretiminden gelen K<sub>1</sub>, &#8230;, K<sub>16</sub> alt anahtarlarıyla 16 Feistel "
       "döngüsünde işlenir; son takas ve IP<sup>&#8722;1</sup> ile şifreli metin elde edilir."),
    aria="DES genel akis semasi: IP, 16 Feistel dongusu, takas ve ters IP")

# ============================================================ des-feistel-turu
# One Feistel round: two lanes L/R, the f box and the XOR, crossing outputs.
W, H = 460, 330
p = Plot(0, 0, W, H, (0, W), (0, H))
LX, RX = 120, 340   # lane centres

bx(p, LX - 55, 24, 110, 32, THEORY, "L" + sub("i" + MID + "1") + " (32 bit)", bold=False)
bx(p, RX - 55, 24, 110, 32, THEORY, "R" + sub("i" + MID + "1") + " (32 bit)", bold=False)

# lanes
p.add(f'<line x1="{LX}" y1="56" x2="{LX}" y2="139" stroke="{TEXT}" stroke-width="1.6" opacity="0.7"/>')
p.add(f'<line x1="{RX}" y1="56" x2="{RX}" y2="205" stroke="{TEXT}" stroke-width="1.6" opacity="0.7"/>')
p.add(f'<circle cx="{RX}" cy="150" r="2.6" fill="{TEXT}" opacity="0.7"/>')   # tap on the R lane

# f box, its input from R and the subkey from above
rect(p, 190, 126, 100, 48, PRACTICE)
p.text_px(240, 156, "f", TEXT, 16, "middle", bold=True, italic=True)
arr(p, RX, 150, 292, 150)
arr(p, 240, 94, 240, 124, PRACTICE, opacity=0.85)
p.text_px(248, 102, "K" + sub("i") + " (48 bit)", PRACTICE, 11.5, "start", bold=True)

# f output into the XOR on the L lane
arr(p, 190, 150, 133, 150, PRACTICE, opacity=0.85)
xor_node(p, LX, 150)
p.add(f'<line x1="{LX}" y1="161" x2="{LX}" y2="205" stroke="{TEXT}" stroke-width="1.6" opacity="0.7"/>')

# crossing outputs
arr(p, RX, 205, 112, 266)
arr(p, LX, 205, 333, 266)

bx(p, 40, 270, 140, 32, THEORY,
   "L" + sub("i") + " = R" + sub("i" + MID + "1"), bold=False)
bx(p, 250, 270, 170, 32, THEORY,
   "R" + sub("i") + " = L" + sub("i" + MID + "1") + " " + XOR + " f(R" + sub("i" + MID + "1") + ", K" + sub("i") + ")",
   size=11, bold=False)

OUT["des-feistel-turu"] = figure(
    W, H, [p],
    tr("Tek bir Feistel döngüsü: sağ yarı R<sub>i&#8722;1</sub> hiç değişmeden çaprazlama sola taşınır; "
       "sol yarı L<sub>i&#8722;1</sub> ise sağ yarının f fonksiyonundan geçmiş hâliyle XOR'lanarak yeni "
       "sağ yarıyı oluşturur. Anahtar devreye yalnızca f'nin içinde girer."),
    aria="Tek Feistel dongusu: L ve R seritleri, f kutusu ve XOR")

# ============================================================ des-f-fonksiyonu
# The four stages of f: E expansion, subkey XOR, 8 S-boxes, P permutation.
W, H = 460, 372
p = Plot(0, 0, W, H, (0, W), (0, H))
CX = 200

bx(p, 125, 16, 150, 30, BASE, "R" + sub("i" + MID + "1") + " (32 bit)", bold=False)
arr(p, CX, 46, CX, 62)
bx(p, 85, 64, 230, 38, THEORY, "genişletme E", sub_label="32 bit " + ARR + " 48 bit")
p.text_px(322, 80, tr("16 kenar biti"), REMARK, 10.5, "start")
p.text_px(322, 93, tr("iki kez kullanılır"), REMARK, 10.5, "start")
arr(p, CX, 102, CX, 127)
p.text_px(208, 119, "48 bit", REMARK, 10.5, "start")

xor_node(p, CX, 140)
arr(p, 320, 140, 214, 140, PRACTICE, opacity=0.85)
p.text_px(326, 144, "K" + sub("i") + " (48 bit)", PRACTICE, 11.5, "start", bold=True)

# S-box row: 8 boxes of 40 px, 6 px gaps, spanning 17..379, with the classic
# fan-out line above and collector line below
centers = [17 + k * 46 + 20 for k in range(8)]
p.add(f'<line x1="{CX}" y1="151" x2="{CX}" y2="163" stroke="{TEXT}" stroke-width="1.6" opacity="0.7"/>')
p.add(f'<line x1="{centers[0]}" y1="163" x2="{centers[-1]}" y2="163" stroke="{TEXT}" stroke-width="1.4" opacity="0.7"/>')
p.add(f'<line x1="{centers[0]}" y1="227" x2="{centers[-1]}" y2="227" stroke="{TEXT}" stroke-width="1.4" opacity="0.7"/>')
for k, c in enumerate(centers):
    x = 17 + k * 46
    rect(p, x, 175, 40, 40, PRACTICE)
    p.text_px(x + 20, 199, "S" + sub(str(k + 1)), TEXT, 12, "middle", bold=True)
    arr(p, c, 163, c, 173, width=1.3, head=5.0)
    p.add(f'<line x1="{c}" y1="215" x2="{c}" y2="227" stroke="{TEXT}" stroke-width="1.3" opacity="0.7"/>')
arr(p, CX, 227, CX, 254)
p.text_px(188, 245, tr("her kutu: 6 bit ") + ARR + " 4 bit", REMARK, 10.5, "end")
p.text_px(208, 248, "32 bit", REMARK, 10.5, "start")

bx(p, 85, 256, 230, 38, THEORY, "P permütasyonu", sub_label="32 bitin yerini karıştırır")
arr(p, CX, 294, CX, 310)
bx(p, 105, 312, 190, 34, BASE,
   "f(R" + sub("i" + MID + "1") + ", K" + sub("i") + ") — 32 bit", bold=False)

OUT["des-f-fonksiyonu"] = figure(
    W, H, [p],
    tr("f fonksiyonunun dört aşaması: E genişletmesi 32 biti 48 bite çıkarır, sonuç alt anahtar "
       "K<sub>i</sub> ile XOR'lanır, 48 bit sekiz S-kutusundan geçerek 32 bite iner ve P permütasyonu "
       "bu bitleri bloğun geneline dağıtır."),
    aria="f fonksiyonunun dort asamasi: E genislemesi, alt anahtar XOR, 8 S-kutusu, P permutasyonu")

# ============================================================ des-3des-ede
# The E-D-E chain of 3DES with the K1 = K2 collapse annotation.
W, H = 560, 190
p = Plot(0, 0, W, H, (0, W), (0, H))
BY, BH = 70, 44

p.text_px(38, 96, "P", TEXT, 14, "middle", bold=True, italic=True)
p.text_px(38, 112, tr("açık metin"), REMARK, 10.5, "middle")
arr(p, 56, 92, 78, 92)
bx(p, 80, BY, 90, BH, THEORY, "E", sub_label="şifrele")
arr(p, 170, 92, 213, 92)
bx(p, 215, BY, 90, BH, PRACTICE, "D", sub_label="çöz")
arr(p, 305, 92, 348, 92)
bx(p, 350, BY, 90, BH, THEORY, "E", sub_label="şifrele")
arr(p, 440, 92, 462, 92)
p.text_px(482, 96, "C", TEXT, 14, "middle", bold=True, italic=True)
p.text_px(482, 112, tr("şifreli metin"), REMARK, 10.5, "middle")

for kx, ks in ((125, "1"), (260, "2"), (395, "3")):
    arr(p, kx, 42, kx, 68, PRACTICE, opacity=0.85)
    p.text_px(kx, 34, "K" + sub(ks), PRACTICE, 12, "middle", bold=True)

# collapse annotation: dashed frame around the first two boxes
rect(p, 74, 62, 237, 58, REMARK, opacity=0.0, lw=1.3, dash="5 4")
p.add(f'<line x1="192" y1="122" x2="192" y2="136" stroke="{REMARK}" '
      f'stroke-width="1.2" stroke-dasharray="4 3" opacity="0.8"/>')
p.text_px(226, 152, tr("K") + sub("1") + tr(" = K") + sub("2") + tr(" seçilirse bu iki kutu birbirini yok eder;"),
          TEXT, 11, "middle")
p.text_px(226, 168, tr("geriye tek DES kalır ") + ARR + tr(" geriye uyumluluk"), TEXT, 11, "middle")

OUT["des-3des-ede"] = figure(
    W, H, [p], tr(
        "3DES'in E&#8211;D&#8211;E zinciri: açık metin önce K<sub>1</sub> ile şifrelenir, K<sub>2</sub> ile "
        "çözülür, K<sub>3</sub> ile yeniden şifrelenir. K<sub>1</sub> = K<sub>2</sub> seçildiğinde ilk iki "
        "kutu birbirini yok eder ve sistem tek DES'e dönüşür — eski donanımla geriye uyumluluğun sırrı."),
    css_class=WIDE,
    aria="3DES E-D-E zinciri ve K1 esittir K2 durumunda tek DES'e cokme")

# ############################################################################
# PART: AES
# ############################################################################

"""AES chapter figures: state matrix, round flow, ShiftRows, MixColumns."""
# ---------------------------------------------------------------- helpers
def sub(s, size=9):
    """Subscript inside an SVG <text>."""
    return f'<tspan font-size="{size}" dy="3">{s}</tspan><tspan dy="-3">&#8203;</tspan>'


def box(p, x, y, w, h, color=THEORY, fo=0.10, sw=1.6, rx=5, dash=None):
    da = f' stroke-dasharray="{dash}"' if dash else ""
    p.add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
          f'fill="{color}" fill-opacity="{fo}" stroke="{color}" stroke-width="{sw}"{da}/>')


def cell(p, x, y, w, h, label, color=THEORY, fo=0.10, size=11.5, bold=False, tcolor=None):
    box(p, x, y, w, h, color, fo, 1.3, rx=3)
    p.text_px(x + w / 2, y + h / 2 + 4, label, tcolor or color, size, "middle", bold)


def px_arrow(p, x0, y0, x1, y1, color=TEXT, width=1.6, head=7.0, opacity=0.9):
    import math as m
    dx, dy = x1 - x0, y1 - y0
    L = m.hypot(dx, dy) or 1.0
    ux, uy = dx / L, dy / L
    sx, sy = x1 - ux * head * 0.8, y1 - uy * head * 0.8
    p.add(f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{sx:.1f}" y2="{sy:.1f}" stroke="{color}" '
          f'stroke-width="{width}" opacity="{opacity}" stroke-linecap="round"/>')
    px_, py_ = -uy, ux
    hw = head * 0.42
    p.add(f'<polygon points="{x1:.1f},{y1:.1f} {x1-ux*head+px_*hw:.1f},{y1-uy*head+py_*hw:.1f} '
          f'{x1-ux*head-px_*hw:.1f},{y1-uy*head-py_*hw:.1f}" fill="{color}" opacity="{opacity}"/>')


# ================================================================ 1. state matrix
W, H = 564, 268
p = Plot(0, 0, W, H, (0, W), (0, H))

p.text_px(W / 2, 22, "16 baytl&#305;k giri&#351; dizisi  in&#8320;, in&#8321;, &#8230;, in&#8321;&#8325;",
          TEXT, 11.5, "middle", True)

# input stream: 16 cells
cw, ch = 26, 24
sx, sy = 74, 34
for i in range(16):
    col = PRACTICE if i < 4 else (BASE if i < 8 else THEORY)
    fo = 0.16 if i < 8 else 0.08
    cell(p, sx + i * cw, sy, cw, ch, str(i), col, fo, 11)

# state grid 4x4, column-major contents
gx, gy, gc = 150, 112, 30
for c in range(4):
    for r in range(4):
        col = PRACTICE if c == 0 else (BASE if c == 1 else THEORY)
        fo = 0.16 if c < 2 else 0.08
        cell(p, gx + c * gc, gy + r * gc, gc, gc, str(r + 4 * c), col, fo, 11.5)

# arrows: first four bytes -> column 0, next four -> column 1
px_arrow(p, sx + 2 * cw, sy + ch + 4, gx + gc / 2, gy - 6, PRACTICE, 1.7)
px_arrow(p, sx + 6 * cw, sy + ch + 4, gx + gc + gc / 2, gy - 6, BASE, 1.7)

# row / column indices
for r in range(4):
    p.text_px(gx - 10, gy + r * gc + gc / 2 + 4, f"r = {r}", REMARK, 10, "end")
for c in range(4):
    p.text_px(gx + c * gc + gc / 2, gy + 4 * gc + 14, f"{c}", REMARK, 10, "middle")
p.text_px(gx + 2 * gc, gy + 4 * gc + 28, "s&#252;tun  c", REMARK, 10, "middle")

# formula on the right
fx = 360
p.text_px(fx, gy + 30, "yerle&#351;tirme kural&#305;:", TEXT, 11, "start", True)
p.text_px(fx, gy + 52, f'<tspan font-style="italic">s</tspan>{sub("r,c")} = in{sub("r + 4c")}',
          THEORY, 12.5, "start", True)
p.text_px(fx, gy + 76, f'&#246;rnek:  <tspan font-style="italic">s</tspan>{sub("1,2")} = in{sub("9")}',
          REMARK, 11, "start")

OUT["aes-durum-matrisi"] = figure(
    W, H, [p],
    "128 bitlik blok, 16 bayt olarak <strong>s&#252;tun s&#252;tun</strong> 4&#215;4 durum matrisine "
    "yerle&#351;tirilir: ilk d&#246;rt bayt birinci s&#252;tunu, sonraki d&#246;rt bayt ikinci s&#252;tunu doldurur. "
    "H&#252;credeki say&#305; bayt&#305;n giri&#351; dizisindeki s&#305;ras&#305;d&#305;r; kural "
    "<em>s</em><sub>r,c</sub> = in<sub>r+4c</sub>.",
    css_class=WIDE,
    aria="16 baytlik girisin sutun sutun 4x4 durum matrisine yerlestirilmesi")


# ================================================================ 2. round flow
W, H = 430, 470
p = Plot(0, 0, W, H, (0, W), (0, H))

bx, bw, bh = 105, 150, 28
cx = bx + bw / 2


def flow_box(y, label, color):
    box(p, bx, y, bw, bh, color, 0.12)
    p.text_px(cx, y + bh / 2 + 4, label, color, 12, "middle", True)


p.text_px(cx, 18, "a&#231;&#305;k metin blo&#287;u (128 bit)", TEXT, 11.5, "middle", True)
px_arrow(p, cx, 26, cx, 42, TEXT, 1.4)

flow_box(44, "AddRoundKey", BASE)
p.text_px(bx + bw + 14, 62, "beyazlatma &#8212; K&#8320;", REMARK, 10.5, "start")

px_arrow(p, cx, 72, cx, 90, TEXT, 1.4)

loop_ys = (92, 140, 188, 236)
labels = ("SubBytes", "ShiftRows", "MixColumns", "AddRoundKey")
colors = (THEORY, THEORY, THEORY, BASE)
for y, lab, col in zip(loop_ys, labels, colors):
    flow_box(y, lab, col)
for y in loop_ys[:-1]:
    px_arrow(p, cx, y + bh, cx, y + 46, TEXT, 1.4)

# Shannon roles on the left
p.text_px(bx - 12, loop_ys[0] + 18, "kar&#305;&#351;&#305;kl&#305;k", REMARK, 10.5, "end")
p.text_px(bx - 20, (loop_ys[1] + loop_ys[2]) / 2 + 32, "yay&#305;lma", REMARK, 10.5, "end")
p.add(f'<path d="M{bx-8},{loop_ys[1]+4} h-4 v88 h4" fill="none" stroke="{REMARK}" stroke-width="1.2" opacity="0.7"/>')
p.text_px(bx - 12, loop_ys[3] + 18, "anahtar", REMARK, 10.5, "end")

# loop bracket on the right
lb_top, lb_bot = loop_ys[0] - 4, loop_ys[-1] + bh + 4
p.add(f'<path d="M{bx+bw+10},{lb_top} h8 v{lb_bot-lb_top} h-8" fill="none" '
      f'stroke="{PRACTICE}" stroke-width="1.6"/>')
p.text_px(bx + bw + 28, (lb_top + lb_bot) / 2 - 2,
          f'&#215;(<tspan font-style="italic">N</tspan>{sub("r")} &#8722; 1)', PRACTICE, 12, "start", True)
p.text_px(bx + bw + 28, (lb_top + lb_bot) / 2 + 16, "d&#246;ng&#252;", PRACTICE, 10.5, "start")

px_arrow(p, cx, loop_ys[-1] + bh, cx, 300, TEXT, 1.4)

final_ys = (302, 350, 398)
for y, lab, col in zip(final_ys, ("SubBytes", "ShiftRows", "AddRoundKey"), (THEORY, THEORY, BASE)):
    flow_box(y, lab, col)
for y in final_ys[:-1]:
    px_arrow(p, cx, y + bh, cx, y + 46, TEXT, 1.4)

fb_top, fb_bot = final_ys[0] - 4, final_ys[-1] + bh + 4
p.add(f'<path d="M{bx+bw+10},{fb_top} h8 v{fb_bot-fb_top} h-8" fill="none" '
      f'stroke="{REMARK}" stroke-width="1.4"/>')
p.text_px(bx + bw + 28, (fb_top + fb_bot) / 2 - 2, "son d&#246;ng&#252;:", REMARK, 10.5, "start", True)
p.text_px(bx + bw + 28, (fb_top + fb_bot) / 2 + 14, "MixColumns yok", REMARK, 10.5, "start")

px_arrow(p, cx, final_ys[-1] + bh, cx, 444, TEXT, 1.4)
p.text_px(cx, 460, "&#351;ifreli metin (128 bit)", TEXT, 11.5, "middle", True)

OUT["aes-tur-akisi"] = figure(
    W, H, [p],
    "AES &#351;ifrelemesinin ak&#305;&#351;&#305;: &#246;nce beyazlatma amac&#305;yla bir <strong>AddRoundKey</strong>, "
    "ard&#305;ndan <em>N</em><sub>r</sub> &#8722; 1 kez tekrarlanan tam d&#246;ng&#252; ve MixColumns "
    "ad&#305;m&#305; at&#305;lm&#305;&#351; son d&#246;ng&#252;. Mavi kutular veri d&#246;n&#252;&#351;&#252;mlerini, ye&#351;il kutular "
    "anahtar&#305;n kar&#305;&#351;t&#305;r&#305;ld&#305;&#287;&#305; ad&#305;m&#305; g&#246;sterir.",
    aria="AES tur akisi: AddRoundKey, dongu SubBytes ShiftRows MixColumns AddRoundKey, son tur MixColumns'suz")


# ================================================================ 3. ShiftRows
W, H = 564, 232
p = Plot(0, 0, W, H, (0, W), (0, H))

gc = 34, 30
cw2, ch2 = 34, 30
lx, ly = 60, 60
rx_, ry = 368, 60

rows = ("a", "b", "c", "d")
SUBS = (SUB0, SUB1, SUB2, SUB3)

p.text_px(lx + 2 * cw2, 44, "&#246;nce", TEXT, 11.5, "middle", True)
p.text_px(rx_ + 2 * cw2, 44, "sonra", TEXT, 11.5, "middle", True)

for r in range(4):
    for c in range(4):
        # left grid: natural order
        name = rows[r] + SUBS[c]
        hot = (c == 1)
        cell(p, lx + c * cw2, ly + r * ch2, cw2, ch2, name,
             PRACTICE if hot else THEORY, 0.20 if hot else 0.08, 11.5, hot)
        # right grid: row r rotated left by r
        c_src = (c + r) % 4
        name2 = rows[r] + SUBS[c_src]
        hot2 = (c_src == 1)
        cell(p, rx_ + c * cw2, ly + r * ch2, cw2, ch2, name2,
             PRACTICE if hot2 else THEORY, 0.20 if hot2 else 0.08, 11.5, hot2)

shift_lbl = ("de&#287;i&#351;mez", "1 sola", "2 sola", "3 sola")
for r in range(4):
    yy = ly + r * ch2 + ch2 / 2
    px_arrow(p, lx + 4 * cw2 + 10, yy, rx_ - 10, yy, BASE, 1.5)
    p.text_px((lx + 4 * cw2 + rx_) / 2, yy - 6, shift_lbl[r], BASE, 10.5, "middle")

p.text_px(W / 2, ly + 4 * ch2 + 26,
          "vurgulu s&#252;tunun d&#246;rt bayt&#305; d&#246;rt farkl&#305; s&#252;tuna da&#287;&#305;l&#305;r",
          REMARK, 11, "middle")

OUT["aes-shiftrows"] = figure(
    W, H, [p],
    "ShiftRows her sat&#305;r&#305; kendi numaras&#305; kadar sola d&#246;nd&#252;r&#252;r: 0. sat&#305;r sabit "
    "kal&#305;r, 1. sat&#305;r bir, 2. sat&#305;r iki, 3. sat&#305;r &#252;&#231; bayt kayar. Solda ayn&#305; "
    "s&#252;tunda duran d&#246;rt bayt (koyu h&#252;creler) sa&#287;da d&#246;rt farkl&#305; s&#252;tuna "
    "da&#287;&#305;lm&#305;&#351;t&#305;r.",
    css_class=WIDE,
    aria="ShiftRows: satirlarin 0,1,2,3 bayt sola dondurulmesi, bir sutunun dort sutuna dagilmasi")


# ================================================================ 4. MixColumns
W, H = 564, 236
p = Plot(0, 0, W, H, (0, W), (0, H))

# state on the left with column 1 highlighted (example values)
gx, gy, gc = 40, 64, 30
colvals = ("D4", "BF", "5D", "30")
for c in range(4):
    for r in range(4):
        if c == 1:
            cell(p, gx + c * gc, gy + r * gc, gc, gc, colvals[r], PRACTICE, 0.20, 10.5, True)
        else:
            box(p, gx + c * gc, gy + r * gc, gc, gc, REMARK, 0.05, 1.0, rx=3)
            p.text_px(gx + c * gc + gc / 2, gy + r * gc + gc / 2 + 4, "&#183;", REMARK, 11, "middle")
p.text_px(gx + 2 * gc, 46, "durum", TEXT, 11.5, "middle", True)
p.text_px(gx + 2 * gc, gy + 4 * gc + 18, "c s&#252;tunu", PRACTICE, 10.5, "middle")

# arrow from column to the product
px_arrow(p, gx + 4 * gc + 8, gy + 2 * gc, 232, gy + 2 * gc, PRACTICE, 1.7)

# fixed matrix
mx, my, mw, mh = 240, 64, 32, 30
MAT = (("02", "03", "01", "01"),
       ("01", "02", "03", "01"),
       ("01", "01", "02", "03"),
       ("03", "01", "01", "02"))
box(p, mx - 6, my - 6, 4 * mw + 12, 4 * mh + 12, THEORY, 0.05, 1.6, rx=7)
for r in range(4):
    for c in range(4):
        p.text_px(mx + c * mw + mw / 2, my + r * mh + mh / 2 + 4, MAT[r][c],
                  THEORY, 11.5, "middle", MAT[r][c] != "01")
p.text_px(mx + 2 * mw, 46, "sabit matris", THEORY, 11.5, "middle", True)

# input vector
vx = mx + 4 * mw + 22
for r in range(4):
    cell(p, vx, my + r * mh, 30, mh, colvals[r], PRACTICE, 0.20, 10.5, True)

p.text_px(vx + 46, my + 2 * mh + 4, "=", TEXT, 14, "middle", True)

# result vector
outvals = ("04", "66", "81", "E5")
ox = vx + 62
for r in range(4):
    cell(p, ox, my + r * mh, 30, mh, outvals[r], BASE, 0.20, 10.5, True)
p.text_px(ox + 15, my + 4 * mh + 18, "yeni s&#252;tun", BASE, 10.5, "middle")

p.text_px(mx + 2 * mw + 30, my + 4 * mh + 40,
          "&#231;arp&#305;m ve toplam GF(2&#8312;) i&#231;inde: toplama &#8853; (XOR), &#231;arpma mod m(x)",
          REMARK, 10.5, "middle")

OUT["aes-mixcolumns"] = figure(
    W, H, [p],
    "MixColumns durumun her s&#252;tununu ayr&#305; ayr&#305; ele al&#305;r: s&#252;tun, sabit "
    "d&#246;ng&#252;sel matrisle GF(2&#8312;) &#252;zerinde &#231;arp&#305;l&#305;r ve yerine yeni s&#252;tun "
    "yaz&#305;l&#305;r. &#214;rnekteki (D4, BF, 5D, 30) s&#252;tunu (04, 66, 81, E5) s&#252;tununa "
    "d&#246;n&#252;&#351;&#252;r.",
    css_class=WIDE,
    aria="MixColumns: bir sutunun sabit 4x4 matrisle GF(2^8) uzerinde carpilmasi")

for name, content in OUT.items():
    with io.open(os.path.join(OUT_DIR, "crypto-%s.md" % name), "w", encoding="utf-8") as f:
        f.write(content)
print("generated:", ", ".join(OUT))
