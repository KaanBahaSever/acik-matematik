# -*- coding: utf-8 -*-
"""
Generates the SVG figures used in the "Olasılık Teorisi" chapters (dersler/olasilik-teorisi).

Same authoring flow as scripts/analysis_figures.py: the figures are NOT produced
at build time. Run this script, then

    python scripts/center_figures.py "probability-*.md"

(which measures each drawing and centers it in its viewBox) and paste the
resulting markup into the .qmd files — inside the theorem/example/proof box the
figure explains, never inside a definition box. Building the books therefore
needs neither Python nor Jupyter; CI runs Quarto alone.

The captions are Turkish on purpose — they are the text shown on the site.

Usage:   python scripts/probability_figures.py && python scripts/center_figures.py "probability-*.md"
Output:  scripts/_figures/probability-<name>.md
"""
import io
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from svg_plot import *  # noqa: E402,F403 — Plot, figure, colors, WIDE, hollow, dot, ...

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_figures")
os.makedirs(OUT_DIR, exist_ok=True)
OUT = {}

EPS, DELTA, ELL, INF, LEQ_S = "&#949;", "&#948;", "&#8467;", "&#8734;", "&#8804;"
PRIME, GEQ_S, NEQ_S, TIMES_S, MINUS_S = "&#8242;", "&#8805;", "&#8800;", "&#215;", "&#8722;"
INT_S, SUM_S, ARROW = "&#8747;", "&#8721;", "&#8594;"


def subs(s, size=9):
    """Subscript inside an SVG <text>: 'x' + subs('0')."""
    return f'<tspan font-size="{size}" dy="4">{s}</tspan><tspan dy="-4">&#8203;</tspan>'


def sups(s, size=8.5):
    """Superscript inside an SVG <text>."""
    return f'<tspan font-size="{size}" dy="-5">{s}</tspan><tspan dy="5">&#8203;</tspan>'


def curve(p, f, x0, x1, color=THEORY, width=1.9, samples=200, dash=None, opacity=1.0):
    """Polyline of y = f(x) on [x0, x1]."""
    pts = [(x0 + (x1 - x0) * k / samples, f(x0 + (x1 - x0) * k / samples)) for k in range(samples + 1)]
    p.line(pts, color, width, dash, opacity)


def guide(p, pts, color=TEXT, opacity=0.5, width=1.0):
    """Thin dashed guide line through the given data points."""
    p.line(pts, color, width, "4 3", opacity)


def tfmt(v):
    """Tick label with the Turkish decimal comma: 0.5 -> '0,5'."""
    return fmt(v).replace(".", ",")


def rect(p, x0, x1, y0, y1, color=THEORY, opacity=0.16, stroke=None, width=1.0):
    """Axis-aligned rectangle in data coordinates."""
    p.polygon([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], color, opacity,
              stroke if stroke else "none", width)


def through(f, x0, slope, x):
    """The line through (x0, f(x0)) with the given slope, evaluated at x."""
    return f(x0) + slope * (x - x0)

def clipped(p, f, x0, x1, color=THEORY, width=1.9, samples=400, opacity=1.0):
    """Like curve(), but drops the pieces that fall outside the panel's y-range."""
    run = []
    for k in range(samples + 1):
        x = x0 + (x1 - x0) * k / samples
        try:
            y = f(x)
        except (ValueError, ZeroDivisionError, OverflowError):
            y = None
        if y is None or not (p.ymin <= y <= p.ymax):
            if len(run) > 1:
                p.line(run, color, width, None, opacity)
            run = []
        else:
            run.append((x, y))
    if len(run) > 1:
        p.line(run, color, width, None, opacity)

# ============================================================ artan-dizi-halkalar
# Increasing sequence A1 c A2 c A3 c A4 c ... drawn as eccentric nested disks; the rings
# B1 = A1, B_n = A_n \ A_{n-1} are shaded in decreasing tones. Used in the continuity proof.
# (cx, r) of each disk; centres drift right so the rings stay thin on the left, wide on the right.
DISKS = [(-0.42, 0.34), (-0.30, 0.54), (-0.16, 0.76), (0.0, 1.0)]
LIMIT = (0.10, 1.17)                       # dashed hint: the sequence goes on
TONES = [0.48, 0.35, 0.24, 0.14]           # B1 darkest, outer rings lighter

p = Plot(14, 9, 245, 235.2, (-1.2, 1.3), (-1.2, 1.2))   # equal aspect: 98 px per unit


def circ_path(cx, r):
    """Closed circle path in pixels (two half-arcs), centre (cx, 0)."""
    R = p.R(r)
    return ("M%s A%.1f,%.1f 0 1,0 %s A%.1f,%.1f 0 1,0 %s Z"
            % (p.P(cx + r, 0), R, R, p.P(cx - r, 0), R, R, p.P(cx + r, 0)))


def ring(outer, inner, opacity):
    """Shade outer \\ inner with an even-odd fill."""
    d = circ_path(*outer) + " " + circ_path(*inner)
    p.add('<path d="%s" fill="%s" fill-opacity="%.2f" fill-rule="evenodd" stroke="none"/>'
          % (d, THEORY, opacity))


def on_stroke(cx, r, ang_deg, s):
    """Label sitting on a circle's boundary at the given angle, with a page-coloured halo."""
    a = math.radians(ang_deg)
    px, py = p.X(cx + r * math.cos(a)), p.Y(r * math.sin(a)) + 4
    common = 'x="%.1f" y="%.1f" font-size="11.5" font-style="italic" font-weight="600" text-anchor="middle"' % (px, py)
    p.add('<text %s fill="%s" stroke="%s" stroke-width="4" stroke-linejoin="round">%s</text>' % (common, BG, BG, s))
    p.add('<text %s fill="%s">%s</text>' % (common, TEXT, s))


# shaded pieces: the inner disk and the three rings
p.add('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s" fill-opacity="%.2f" stroke="none"/>'
      % (p.X(DISKS[0][0]), p.Y(0), p.R(DISKS[0][1]), THEORY, TONES[0]))
for k in range(1, 4):
    ring(DISKS[k], DISKS[k - 1], TONES[k])

# boundaries and the dashed continuation
for cx, r in DISKS:
    p.circle(cx, 0, r, TEXT, 1.3)
p.circle(LIMIT[0], 0, LIMIT[1], TEXT, 1.1, dash="5 4", opacity=0.5)

# ring names along the wide side, where each ring has room
right = [cx + r for cx, r in DISKS]
p.label(DISKS[0][0], 0, "B" + subs("1"), 0, 4, TEXT, 11.5, "middle", True, True)
for k in range(1, 4):
    p.label((right[k - 1] + right[k]) / 2, 0, "B" + subs(str(k + 1)), 0, 4, TEXT, 11.5, "middle", True, True)
p.label((right[3] + LIMIT[0] + LIMIT[1]) / 2, 0, "...", 0, 3, TEXT, 12, "middle", True)

# names of the sets on their boundaries, spread out along the 60-degree ray
for k, (cx, r) in enumerate(DISKS):
    on_stroke(cx, r, 60, "A" + subs(str(k + 1)))

# notes on the right
NX = p.x0 + p.w + 24
LIM = '<tspan font-style="normal">lim</tspan>'
p.text_px(NX, 52, "B" + subs("1") + " = A" + subs("1") + ",   B" + subs("n") + " = A" + subs("n")
          + " &#8745; A" + subs("n" + MINUS_S + "1") + sups("c"), TEXT, 11.5, "start", True, True)
p.text_px(NX, 72, "halkalar ikişer ikişer ayrık", TEXT, 10.5, "start", False, True)
p.text_px(NX, 106, "B" + subs("1") + ", ..., B" + subs("n") + "'nin birleşimi = A" + subs("n"),
          TEXT, 11.5, "start", False, True)
p.text_px(NX, 126, LIM + " A" + subs("n") + " = bütün A" + subs("n") + "'lerin birleşimi",
          TEXT, 11.5, "start", False, True)
p.text_px(NX, 162, "P(A" + subs("n") + ") = P(B" + subs("1") + ") + ... + P(B" + subs("n") + ")",
          PRACTICE, 11.5, "start", True, True)
p.text_px(NX, 182, "P(B" + subs("i") + ") = P(A" + subs("i") + ") " + MINUS_S + " P(A" + subs("i" + MINUS_S + "1") + ")",
          PRACTICE, 11.5, "start", False, True)
p.text_px(NX, 202, "teleskopik toplam: P(A" + subs("n") + ")'ye sadeleşir", PRACTICE, 10.5, "start", False, True)

OUT["artan-dizi-halkalar"] = figure(
    540, 254, [p],
    "Artan bir olay dizisi <em>A</em><sub>1</sub> &#8834; <em>A</em><sub>2</sub> &#8834; <em>A</em><sub>3</sub> "
    "&#8834; <em>A</em><sub>4</sub> &#8834; &#8943; ve onu oluşturan halkalar. En içteki bölge "
    "<em>B</em><sub>1</sub> = <em>A</em><sub>1</sub>, sonraki halkalar <em>B</em><sub>2</sub> = <em>A</em><sub>2</sub> "
    "&#8726; <em>A</em><sub>1</sub>, <em>B</em><sub>3</sub> = <em>A</em><sub>3</sub> &#8726; <em>A</em><sub>2</sub>, "
    "<em>B</em><sub>4</sub> = <em>A</em><sub>4</sub> &#8726; <em>A</em><sub>3</sub>'tür. Halkalar ikişer ikişer "
    "ayrıktır ve ilk <em>n</em> halkanın birleşimi <em>A</em><sub><em>n</em></sub>'yi verir; bütün halkaların birleşimi "
    "ise dizinin limiti &#8746;<em>A</em><sub><em>n</em></sub>'dir. Bu yüzden <em>P</em>(<em>A</em><sub><em>n</em></sub>) = "
    "<em>P</em>(<em>B</em><sub>1</sub>) + &#8943; + <em>P</em>(<em>B</em><sub><em>n</em></sub>) olur ve "
    "<em>n</em> &#8594; &#8734; alınınca süreklilik teoremi çıkar.",
    css_class=WIDE,
    aria="Ic ice dort daire A1 A2 A3 A4 ve aralarindaki ayrik halkalar B1 B2 B3 B4; ilk n halkanin birlesimi An verir")

# ============================================================ azalan-dizi-sureklilik
# Decreasing sequence A1 > A2 > A3 > A4 > ... drawn as eccentric nested disks, the twin of the
# increasing-sequence figure: the outermost disk is the lightest, the tints deepen inwards and the
# limit (the intersection of all A_n) sits in the middle, hatched. Used for part (b) of continuity.
# (cx, r) of each disk; centres drift left so the rings stay thin on the left, wide on the right.
DISKS = [(0.0, 1.0), (-0.12, 0.80), (-0.22, 0.62), (-0.30, 0.46)]
LIMIT = (-0.38, 0.26)                      # the intersection; dashed rim: the sequence goes on
TONES = [0.10, 0.12, 0.15, 0.18]           # stacked, so the tint deepens towards the centre
PID = "azalan-h"

p = Plot(14, 9, 245, 235.2, (-1.2, 1.3), (-1.2, 1.2))   # equal aspect: 98 px per unit

p.add('<defs>'
      f'<pattern id="{PID}" patternUnits="userSpaceOnUse" width="5" height="5" patternTransform="rotate(45)">'
      f'<line x1="2.5" y1="0" x2="2.5" y2="5" stroke="{THEORY}" stroke-width="1.2" opacity="0.85"/></pattern>'
      '</defs>')


def on_stroke(cx, r, ang_deg, s):
    """Label sitting on a circle's boundary at the given angle, with a page-coloured halo."""
    a = math.radians(ang_deg)
    px, py = p.X(cx + r * math.cos(a)), p.Y(r * math.sin(a)) + 4
    common = 'x="%.1f" y="%.1f" font-size="11.5" font-style="italic" font-weight="600" text-anchor="middle"' % (px, py)
    p.add('<text %s fill="%s" stroke="%s" stroke-width="4" stroke-linejoin="round">%s</text>' % (common, BG, BG, s))
    p.add('<text %s fill="%s">%s</text>' % (common, TEXT, s))


# the disks, largest first, each a little darker than the one around it
for (cx, r), tone in zip(DISKS, TONES):
    p.polygon(circle_pts(cx, 0, r), THEORY, tone)
# the limit: solid tint plus hatching
p.polygon(circle_pts(LIMIT[0], 0, LIMIT[1]), THEORY, 0.30)
p.polygon(circle_pts(LIMIT[0], 0, LIMIT[1]), f"url(#{PID})", 1.0)

# boundaries; the limit's rim is dashed
for cx, r in DISKS:
    p.circle(cx, 0, r, TEXT, 1.3)
p.circle(LIMIT[0], 0, LIMIT[1], TEXT, 1.1, dash="4 3")

# names of the sets on their boundaries, spread out along the 60-degree ray
for k, (cx, r) in enumerate(DISKS):
    on_stroke(cx, r, 60, "A" + subs(str(k + 1)))
# the sequence goes on: dots in the wide part of the innermost ring
p.label((DISKS[3][0] + DISKS[3][1] + LIMIT[0] + LIMIT[1]) / 2, 0, "...", 0, 3, TEXT, 12, "middle", True)

# the limit is named outside the picture, with a leader down to its rim
ang = math.radians(232)
tip = (LIMIT[0] + LIMIT[1] * math.cos(ang), LIMIT[1] * math.sin(ang))
end = (-0.58, -0.98)
p.line([tip, end], TEXT, 1.0, opacity=0.7)
dot(p, tip, TEXT, 2.0)
p.label(end[0], end[1], "kesişim", -3, 12, TEXT, 11, "middle", True)

# notes on the right
NX = p.x0 + p.w + 24
LIM = '<tspan font-style="normal">lim</tspan>'
An, An1, Anc = "A" + subs("n"), "A" + subs("n+1"), "A" + subs("n") + sups("c")
p.text_px(NX, 44, An + " azalıyor: her " + An1 + ", " + An + "'nin içinde", TEXT, 11.5, "start", True, True)
p.text_px(NX, 64, "daireler küçülür, tonlar koyulaşır", TEXT, 10.5, "start", False, True)
p.text_px(NX, 102, "kesişim = " + LIM + " " + An + " = bütün " + An + "'lerin", TEXT, 11.5, "start", False, True)
p.text_px(NX, 118, "ortak kısmı (taralı bölge)", TEXT, 11.5, "start", False, True)
p.text_px(NX, 150, "P(" + An + ") " + ARROW + " P(kesişim)", PRACTICE, 12, "start", True, True)
p.text_px(NX, 182, "tümleyenleri artan bir dizidir: " + Anc + " büyür", TEXT, 11.5, "start", False, True)
p.text_px(NX, 202, "1 " + MINUS_S + " P(" + An + ") = P(" + Anc + ") " + ARROW + " 1 " + MINUS_S + " P(kesişim)",
          PRACTICE, 11.5, "start", False, True)
p.text_px(NX, 222, "(a) şıkkı tümleyenlere uygulanır", PRACTICE, 10.5, "start", False, True)

OUT["azalan-dizi-sureklilik"] = figure(
    540, 254, [p],
    "Azalan bir olay dizisi: <em>A</em><sub>1</sub>, <em>A</em><sub>2</sub>'yi, o da <em>A</em><sub>3</sub>'ü "
    "kapsar ve dizi böyle sürer. Daireler küçüldükçe tonlar koyulaşır; ortadaki taralı bölge bütün "
    "<em>A</em><sub><em>n</em></sub>'lerin ortak kısmı, yani dizinin limiti &#8745;<em>A</em><sub><em>n</em></sub>'dir. "
    "Süreklilik teoreminin (b) şıkkı <em>P</em>(<em>A</em><sub><em>n</em></sub>)'nin bu limitin olasılığına "
    "yaklaştığını söyler. İspat için tümleyenlere geçilir: <em>A</em><sub><em>n</em></sub><sup>c</sup> artan bir "
    "dizidir, (a) şıkkı ona uygulanır ve <em>P</em>(<em>A</em><sub><em>n</em></sub>) = 1 &#8722; "
    "<em>P</em>(<em>A</em><sub><em>n</em></sub><sup>c</sup>) eşitliği sonucu verir.",
    css_class=WIDE,
    aria="Ic ice dort daire A1 A2 A3 A4 kuculerek ortadaki tarali kesisime yaklasiyor; sagda P(An) kesisimin olasiligina yakinsar notu ve tumleyenlerin artan dizi oldugu")

# ============================================================ bagimsiz-vs-ayrik
# Disjoint versus independent: two panels at the same scale (150 px per unit).
# Left: two disjoint events inside the sample space — they cannot happen together, so
# P(A n B) = 0 while P(A)P(B) > 0. Right: geometric probability on the unit square —
# a horizontal strip of height p and a vertical strip of width q meet in a rectangle of area p*q.
S = 150.0                                   # pixels per unit in both panels
PW, PH = 236, 175                           # panel size in pixels
XR, YR = (0, PW / S), (0, PH / S)           # data ranges giving equal x/y scale


def _disk(cx, cy, r, n=96):
    return [(cx + r * math.cos(2 * math.pi * k / n), cy + r * math.sin(2 * math.pi * k / n))
            for k in range(n)]


# ---- left panel: disjoint (hence dependent) ---------------------------------------
p1 = Plot(24, 30, PW, PH, XR, YR)
panel_title(p1, "ayrık: kesişim boş (bağımlı)", TEXT, 11)
OX0, OX1, OY0, OY1 = 0.06, 1.51, 0.14, 1.14
p1.polygon([(OX0, OY0), (OX1, OY0), (OX1, OY1), (OX0, OY1)], TEXT, 0.0, TEXT, 1.0)
p1.label(OX1, OY1, "&#937;", -6, 15, TEXT, 12, "end", False, True)
R = 0.30
XA, XB, YC = 0.40, 1.17, 0.66
p1.polygon(_disk(XA, YC, R), THEORY, 0.18)
p1.polygon(_disk(XB, YC, R), PRACTICE, 0.18)
p1.circle(XA, YC, R, THEORY, 1.6)
p1.circle(XB, YC, R, PRACTICE, 1.6)
p1.label(XA, YC, "A", 0, 5, THEORY, 13, "middle", True, True)
p1.label(XB, YC, "B", 0, 5, PRACTICE, 13, "middle", True, True)
p1.label((OX0 + OX1) / 2, OY0, "B gerçekleştiyse A gerçekleşmemiştir", 0, -8, TEXT, 10, "middle", False, True)
p1.text_px(p1.x0 + p1.w / 2, 232, "P(A &#8745; B) = 0 " + NEQ_S + " P(A)P(B) &gt; 0", TEXT, 11.5, "middle", True)

# ---- right panel: independent strips on the unit square ---------------------------
p2 = Plot(300, 30, PW, PH, XR, YR)
panel_title(p2, "bağımsız: P(A) = p, P(B) = q", TEXT, 11)
UX0, UY0 = 0.36, 0.14                        # lower-left corner of the unit square
UX1, UY1 = UX0 + 1.0, UY0 + 1.0
PA, QB = 0.5, 0.4                            # p = height of A, q = width of B
AY0, AY1 = UY0 + 0.36, UY0 + 0.36 + PA       # horizontal strip A
BX0, BX1 = UX0 + 0.42, UX0 + 0.42 + QB       # vertical strip B
rect(p2, UX0, UX1, AY0, AY1, THEORY, 0.18)
rect(p2, BX0, BX1, UY0, UY1, PRACTICE, 0.18)
rect(p2, BX0, BX1, AY0, AY1, BASE, 0.55)
rect(p2, UX0, UX1, AY0, AY1, THEORY, 0.0, THEORY, 1.4)
rect(p2, BX0, BX1, UY0, UY1, PRACTICE, 0.0, PRACTICE, 1.4)
p2.polygon([(UX0, UY0), (UX1, UY0), (UX1, UY1), (UX0, UY1)], TEXT, 0.0, TEXT, 1.0)
p2.label(UX1, UY1, "&#937;", -6, 15, TEXT, 12, "end", False, True)
p2.label(UX0, (AY0 + AY1) / 2, "A", 8, 5, THEORY, 13, "start", True, True)
p2.label((BX0 + BX1) / 2, UY1, "B", 0, 16, PRACTICE, 13, "middle", True, True)
p2.label((BX0 + BX1) / 2, (AY0 + AY1) / 2, "alan", 0, -2, TEXT, 10.5, "middle", True)
p2.label((BX0 + BX1) / 2, (AY0 + AY1) / 2, "p&#183;q", 0, 12, TEXT, 11, "middle", True, True)
# dimension marks: p on the left of the square, q under it
BX = UX0 - 0.09
p2.line([(BX, AY0), (BX, AY1)], THEORY, 1.2)
p2.line([(BX - 0.03, AY0), (BX + 0.03, AY0)], THEORY, 1.2)
p2.line([(BX - 0.03, AY1), (BX + 0.03, AY1)], THEORY, 1.2)
p2.label(BX, (AY0 + AY1) / 2, "p", -6, 4, THEORY, 12, "end", True, True)
BY = UY0 - 0.07
p2.line([(BX0, BY), (BX1, BY)], PRACTICE, 1.2)
p2.line([(BX0, BY - 0.03), (BX0, BY + 0.03)], PRACTICE, 1.2)
p2.line([(BX1, BY - 0.03), (BX1, BY + 0.03)], PRACTICE, 1.2)
p2.label((BX0 + BX1) / 2, BY, "q", 0, 15, PRACTICE, 12, "middle", True, True)
p2.text_px(p2.x0 + p2.w / 2, 232, "P(A &#8745; B) = p&#183;q = P(A)P(B) &gt; 0", TEXT, 11.5, "middle", True)

OUT["bagimsiz-vs-ayrik"] = figure(
    560, 245, [p1, p2],
    "Ayrıklık ile bağımsızlık farklı kavramlardır. Solda <em>A</em> ile <em>B</em> ayrıktır: birlikte "
    "gerçekleşemezler, dolayısıyla <em>P</em>(<em>A</em> &#8745; <em>B</em>) = 0 iken <em>P</em>(<em>A</em>)<em>P</em>(<em>B</em>) "
    "pozitiftir; olaylar bağımlıdır. Sağda örnek uzay birim karedir ve olasılık alanla ölçülür: yüksekliği "
    "<em>p</em> olan yatay şerit <em>A</em> ile genişliği <em>q</em> olan düşey şerit <em>B</em>, alanı "
    "<em>p</em>&#183;<em>q</em> = <em>P</em>(<em>A</em>)<em>P</em>(<em>B</em>) olan bir dikdörtgende kesişir; olaylar "
    "bağımsızdır ve kesişimleri boş değildir.",
    css_class=WIDE,
    aria="Solda ornek uzayda kesismeyen A ve B daireleri (ayrik ama bagimli); sagda birim karede yatay ve dusey seritlerin p carpi q alanli kesisimi (bagimsiz)")

# ============================================================ bagimsizlik-destek-dikdortgen
# Support criterion for independence: a product set [a,b]x[c,d] (all vertical sections equal)
# versus the triangle 0 < y < x < 1 (sections change with x, so X and Y cannot be independent).
def it(s):
    return '<tspan font-style="italic">%s</tspan>' % s


A, B, C, D = 0.25, 1.05, 0.2, 0.8      # the rectangle
X1, X2 = 0.5, 0.85                     # two sections in the rectangle
XT, XT2 = 0.35, 0.8                    # two sections in the triangle


def panel(px):
    q = Plot(px, 30, 200, 200, (-0.2, 1.32), (-0.22, 1.3))
    return q


def xf_left(t):
    return {A: it("a"), B: it("b"), X1: it("x") + subs("1"), X2: it("x") + subs("2")}[t]


def yf_left(t):
    return {C: it("c"), D: it("d")}[t]


def xf_right(t):
    return {XT: it("x"), XT2: it("x") + PRIME, 1.0: "1"}[t]


# --- left: product set -------------------------------------------------------
p1 = panel(40)
p1.polygon([(A, C), (B, C), (B, D), (A, D)], THEORY, 0.22, THEORY, 1.4)
p1.origin_axes("x", "y", xticks=(A, X1, X2, B), yticks=(C, D), xfmt=xf_left, yfmt=yf_left)
for x in (X1, X2):
    p1.line([(x, C), (x, D)], PRACTICE, 3.2)
guide(p1, [(0, C), (A, C)], TEXT, 0.4)
guide(p1, [(0, D), (A, D)], TEXT, 0.4)
panel_title(p1, "çarpım kümesi: bağımsız olabilir", TEXT, 11.5)
p1.label(0.66, 1.19, it("f") + "(" + it("x") + ", " + it("y") + ") = " + it("g") + "(" + it("x") + ")&#8239;"
         + it("h") + "(" + it("y") + ")", 0, 0, THEORY, 11, "middle")
p1.label(0.66, 1.02, "her " + it("x") + " için kesit (" + it("c") + ", " + it("d") + "): eşit", 0, 0, PRACTICE, 10.5, "middle")
p1.label(0.675, 0.5, it("D"), 0, 4, THEORY, 12, "middle", True)

# --- right: triangle ---------------------------------------------------------
p2 = panel(322)
p2.polygon([(0, 0), (1, 0), (1, 1)], THEORY, 0.22, THEORY, 1.4)
p2.origin_axes("x", "y", xticks=(XT, XT2, 1.0), yticks=(1.0,), xfmt=xf_right)
for x in (XT, XT2):
    p2.line([(x, 0), (x, x)], PRACTICE, 3.2)
guide(p2, [(1, 0), (1, 1)], TEXT, 0.3)
# a point above the diagonal: f = 0 there although both marginals are positive
hollow(p2, (0.25, 0.5), PRACTICE, 3.8, 1.6)
p2.label(0.25, 0.5, it("f") + " = 0", 0, -9, PRACTICE, 10.5, "middle")
panel_title(p2, "çarpım kümesi değil: bağımsız olamaz", TEXT, 11.5)
p2.label(0.72, 1.17, "kesitler farklı: (0, " + it("x") + "), (0, " + it("x") + PRIME + ")", 0, 0, PRACTICE, 10.5, "middle")
p2.label(0.6, 1.03, it("y") + "'nin aralığı " + it("x") + "'e bağlı", 0, 0, PRACTICE, 10.5, "middle")
p2.label(0.6, 0.25, it("D"), 0, 4, THEORY, 12, "middle", True)

OUT["bagimsizlik-destek-dikdortgen"] = figure(
    560, 245, [p1, p2],
    "Destek ölçütü. Solda destek <em>D</em> = [<em>a</em>, <em>b</em>]&#215;[<em>c</em>, <em>d</em>] bir çarpım kümesidir: <em>x</em> ne olursa olsun düşey kesit aynı "
    "(<em>c</em>, <em>d</em>) aralığıdır; yoğunluk <em>g</em>(<em>x</em>)<em>h</em>(<em>y</em>) biçiminde "
    "çarpanlara ayrılabilir, yani <em>X</em> ve <em>Y</em> bağımsız olabilir. Sağda destek üçgendir: kesit "
    "(0, <em>x</em>), <em>x</em> büyüdükçe uzar; <em>y</em>'nin aralığı <em>x</em>'e bağlıdır. Köşegenin üstündeki "
    "içi boş noktada <em>f</em> = 0 iken iki marjinal de pozitiftir, dolayısıyla <em>f</em> &#8800; "
    "<em>f<sub>X</sub> f<sub>Y</sub></em>: değişkenler bağımsız olamaz.",
    css_class=WIDE,
    aria="Solda dikdortgen destek ve esit uzunlukta iki dusey kesit; sagda ucgen destek, farkli uzunlukta iki kesit ve f sifir olan bir nokta")

# ============================================================ basamakli-dagilim-fonksiyonu
# Step distribution function F(x) = 1 - 1/(n+1) on [n, n+1), F = 0 for x < 1.
# The jump at n is P({n}) = 1/(n(n+1)); the steps shrink and F climbs towards 1.
N_MAX = 6
XMIN, XMAX = -0.6, 6.9


def F(n):
    return 1 - 1 / (n + 1)


def frac_tick(v):
    """Tick labels as the fractions used in the text."""
    k = round(v * 12)
    return {0: "0", 6: "1/2", 8: "2/3", 9: "3/4", 12: "1"}.get(k, fmt(v))


# dots shrink a little where the steps get too tight to keep them apart
RADIUS = {1: 3.6, 2: 3.6, 3: 3.6, 4: 3.4, 5: 2.9, 6: 2.4}

p = Plot(52, 28, 306, 246, (XMIN, XMAX), (-0.05, 1.07))
p.axes(range(0, N_MAX + 1), (0, 1 / 2, 2 / 3, 3 / 4, 1.0), "x", "F(x)", yfmt=frac_tick)
# the asymptote y = 1
guide(p, [(XMIN, 1.0), (XMAX, 1.0)], TEXT, 0.4)
# flat pieces (right-continuous: closed on the left, open on the right)
p.line([(XMIN + 0.05, 0), (1, 0)], THEORY, 2.2)
for n in range(1, N_MAX + 1):
    hi = F(n)
    nxt = n + 1 if n < N_MAX else XMAX - 0.05
    p.line([(n, hi), (nxt, hi)], THEORY, 2.2)
    guide(p, [(n, F(n - 1) if n > 1 else 0.0), (n, hi)], THEORY, 0.5)
# the jump at x = 2 measured by a double arrow
p.line([(2, 1 / 2), (2.5, 1 / 2)], PRACTICE, 1.0, None, 0.7)
p.arrow((2.3, 1 / 2 + 0.014), (2.3, 2 / 3 - 0.014), PRACTICE, 1.3, 6.0)
p.arrow((2.3, 2 / 3 - 0.014), (2.3, 1 / 2 + 0.014), PRACTICE, 1.3, 6.0)
p.label(2.3, (1 / 2 + 2 / 3) / 2, "P({2}) = 1/6", 8, 4, PRACTICE, 10.5, "start", False, True)
# end points: hollow at the level being left, filled at the new level
for n in range(1, N_MAX + 1):
    r = RADIUS[n]
    hollow(p, (n, F(n - 1) if n > 1 else 0.0), THEORY, r, 1.6)
    dot(p, (n, F(n)), THEORY, r)
OUT["basamakli-dagilim-fonksiyonu"] = figure(
    400, 300, [p],
    "Basamaklı dağılım fonksiyonu: <em>x</em> &lt; 1 için <em>F</em>(<em>x</em>) = 0, "
    "<em>n</em> &#8804; <em>x</em> &lt; <em>n</em> + 1 için <em>F</em>(<em>x</em>) = 1 &#8722; 1/(<em>n</em> + 1). "
    "Her pozitif tam sayıda bir sıçrama vardır ve sıçramanın yüksekliği o noktanın olasılığıdır: "
    "<em>P</em>({<em>n</em>}) = 1/(<em>n</em>(<em>n</em> + 1)), örneğin <em>P</em>({2}) = 1/6. "
    "Fonksiyon sağdan süreklidir (her basamağın sol ucu dolu, sağ ucu boştur); basamaklar küçülerek "
    "kesikli çizgiyle gösterilen <em>y</em> = 1 düzeyine yaklaşır.",
    aria="Pozitif tam sayilarda sicrayan basamakli dagilim fonksiyonu; sicramalar kuculerek y = 1 duzeyine yaklasir")

# ============================================================ bayes-agac-uc-torba
# Tree diagram for the three-urn problem: pick an urn (1/3 each), then draw a ball.
p = Plot(20, 16, 520, 222, (0, 10), (-1.35, 6.1))
ROOT = (0.6, 3.0)
URNS = [(3.3, 5.0), (3.3, 3.0), (3.3, 1.0)]
PB = [(1, 4), (2, 4), (3, 4)]                      # (white, red) counts per urn
for i, (ux, uy) in enumerate(URNS):
    p.line([ROOT, (ux, uy)], TEXT, 1.4)
    mx, my = (ROOT[0] + ux) / 2, (ROOT[1] + uy) / 2
    p.label(mx, my, "1/3", -4, -6 if uy >= 3 else 14, TEXT, 10.5, "end", False, True)
    dot(p, (ux, uy), TEXT, 4.2)
    p.label(ux, uy, "Torba " + ("I", "II", "III")[i], 0, -11, TEXT, 11, "middle", True, False)
    w, tot = PB[i]
    for j, (lab, col, prob, dy) in enumerate((("beyaz", THEORY, w, 0.55), ("kırmızı", PRACTICE, tot - w, -0.55))):
        ex, ey = 6.4, uy + dy
        p.line([(ux, uy), (ex, ey)], col, 1.4)
        p.label((ux + ex) / 2, (uy + ey) / 2, "%d/4" % prob, 0, -6 if dy > 0 else 13, col, 10, "middle", False, True)
        dot(p, (ex, ey), col, 3.6)
        joint = "1/3 &#183; %d/4 = %d/12" % (prob, prob)
        p.label(ex, ey, lab + ":  " + joint, 9, 4, col, 10.5, "start", False, True)
dot(p, ROOT, TEXT, 4.6)
p.label(ROOT[0], ROOT[1], "torba seç", 0, 16, TEXT, 10.5, "middle", False, True)
p.label(2.6, -0.85, "P(B) = 1/12 + 2/12 + 3/12 = 1/2", 0, 0, THEORY, 11, "middle", True, True)
p.label(7.4, -0.85, "P(I | B) = (1/12) / (1/2) = 1/6", 0, 0, PRACTICE, 11, "middle", True, True)
OUT["bayes-agac-uc-torba"] = figure(
    560, 240, [p],
    "Üç torba problemi için ağaç diyagramı. Birinci dallanma torbanın seçilmesi, ikincisi topun çekilmesidir; "
    "bir yaprağın olasılığı yol üzerindeki olasılıkların çarpımıdır. Beyaz top çekilmesi olasılığı beyaz "
    "yaprakların toplamıdır (toplam olasılık formülü); çekilen top beyazken torbanın I olması olasılığı, "
    "ilgili yaprağın bu toplama oranıdır (Bayes teoremi).",
    css_class=WIDE,
    aria="Uc torba probleminin agac diyagrami: torba secimi ve top cekilisi dallari, yaprak olasiliklari")

# ============================================================ bayes-taban-oran
# Base-rate picture of the medical-test example: 10 000 people drawn as a 40 x 25 grid of squares,
# each square 10 people. The 100 sick people (10 squares) are filled in PRACTICE; the 198 healthy
# people with a false-positive test (about 20 squares) in light THEORY; everyone else stays empty.
# Beside the grid: the counts and P(hasta | pozitif) = 99 / 297 = 1/3.
COLS, ROWS = 40, 25
p = Plot(14, 34, 280, 175, (0, COLS), (0, ROWS))        # 7 px per square in both directions

# the two coloured blocks, top-left corner: sick = cols 0-1, false positives = cols 2-5, five rows each
for r in range(5):
    for c in range(2):
        rect(p, c, c + 1, ROWS - 1 - r, ROWS - r, PRACTICE, 0.9)
    for c in range(2, 6):
        rect(p, c, c + 1, ROWS - 1 - r, ROWS - r, THEORY, 0.5)

# grid lines and frame
for c in range(1, COLS):
    p.line([(c, 0), (c, ROWS)], TEXT, 0.5, None, 0.3)
for r in range(1, ROWS):
    p.line([(0, r), (COLS, r)], TEXT, 0.5, None, 0.3)
p.polygon([(0, 0), (COLS, 0), (COLS, ROWS), (0, ROWS)], TEXT, 0.0, TEXT, 1.0)
# the set of positive tests: a heavy outline around the two blocks together
p.polygon([(0, ROWS - 5), (6, ROWS - 5), (6, ROWS), (0, ROWS)], TEXT, 0.0, TEXT, 1.6)

panel_title(p, "10 000 kişi, her kare 10 kişi", TEXT, 11.5)
p.add(f'<rect x="{p.x0 + 3 * 7 - 4}" y="{p.y0 + 5 * 7 + 3}" width="106" height="14" rx="3" fill="{BG}"/>')
p.text_px(p.x0 + 3 * 7, p.y0 + 5 * 7 + 14, "test pozitif: 297 kişi", TEXT, 10, "start", False, True)
p.text_px(p.x0 + p.w / 2, 232, "kalın çerçeve = pozitif çıkanlar; hastaların 99'u, sağlıklıların 198'i",
          TEXT, 9.5, "middle", False, True)

# ---- the legend and the arithmetic on the right -------------------------------------------
LX = 312


def swatch(y, color, opacity, stroke_w=0.8):
    p.add(f'<rect x="{LX}" y="{y - 10}" width="13" height="11" fill="{color}" fill-opacity="{opacity}" '
          f'stroke="{TEXT}" stroke-width="{stroke_w}"/>')


swatch(46, PRACTICE, 0.9)
p.text_px(LX + 20, 46, "hasta: 100 kişi (%1), 99'u pozitif", TEXT, 10.5, "start")
swatch(66, THEORY, 0.5)
p.text_px(LX + 20, 66, "sağlıklı, yanlış pozitif: 9 900 &#183; 0,02 = 198", TEXT, 10.5, "start")
swatch(86, BG, 1.0)
p.text_px(LX + 20, 86, "sağlıklı, negatif: 9 702 kişi", TEXT, 10.5, "start")

p.text_px(LX, 118, "P(T) = 0,01 &#183; 0,99 + 0,99 &#183; 0,02", TEXT, 11, "start")
p.text_px(LX + 34, 136, "= 0,0099 + 0,0198 = 0,0297", TEXT, 11, "start")
p.add(f'<line x1="{LX}" y1="150" x2="{LX + 232}" y2="150" stroke="{TEXT}" stroke-width="1" opacity="0.45"/>')
p.text_px(LX, 172, "P(H | T) = 99 / (99 + 198)", TEXT, 11.5, "start", True)
p.text_px(LX + 62, 192, "= 99 / 297 = 1/3", TEXT, 11.5, "start", True)
p.text_px(LX, 216, "pozitif çıkan üç kişiden yalnızca biri hasta:", PRACTICE, 10.5, "start", False, True)
p.text_px(LX, 232, "yanlış pozitifler doğru pozitiflerden çok", PRACTICE, 10.5, "start", False, True)

OUT["bayes-taban-oran"] = figure(
    570, 244, [p],
    "Tıbbi test örneğinin sayım resmi: 10 000 kişilik toplulukta her kare 10 kişiyi gösterir. Turuncu kareler "
    "100 hastayı (%1), açık mavi kareler testi yanlış pozitif çıkan yaklaşık 198 sağlıklı kişiyi gösterir; "
    "kalın çerçeve testi pozitif çıkan 297 kişiyi kuşatır. Hastaların %99'unda test pozitif çıksa da hasta "
    "kitle küçük, sağlıklı kitle büyük olduğundan yanlış pozitiflerin sayısı doğru pozitifleri aşar ve "
    "<em>P</em>(<em>H</em> | <em>T</em>) = 99/297 = 1/3 kalır. Bayes teoremi bu sayımın olasılık diliyle "
    "yazılmış hâlidir.",
    css_class=WIDE,
    aria="40 x 25 kare izgara: sol ustte turuncu hasta kareleri ve acik mavi yanlis pozitif kareleri kalin cerceve icinde; sagda sayilar ve P(H | T) = 99/297 = 1/3 hesabi")

# ============================================================ beklenen-deger-denge
# Expected value as the balance point of the probability masses.
PM = [(-2, 1 / 6), (-1, 1 / 6), (0, 1 / 6), (1, 1 / 6), (2, 1 / 6), (3, 1 / 6)]
MEAN = sum(x * w for x, w in PM)
p1 = Plot(44, 30, 226, 186, (-3.2, 4.2), (-0.13, 0.42))
p1.axes((-2, -1, 0, 1, 2, 3), (1 / 6, 2 / 6), "x", "f(x)", yfmt=lambda v: "%d/6" % round(v * 6))
panel_title(p1, "düzgün kütle: E(X) = 1/2", THEORY)
for x, w in PM:
    p1.add('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" fill-opacity="0.5" stroke="%s" stroke-width="0.9"/>'
           % (p1.X(x - 0.36), p1.Y(w), p1.X(x + 0.36) - p1.X(x - 0.36), p1.Y(0) - p1.Y(w), THEORY, THEORY))
p1.polygon([(MEAN, 0), (MEAN - 0.25, -0.1), (MEAN + 0.25, -0.1)], PRACTICE, 0.9)
p1.label(MEAN, -0.1, "E(X)", 0, 15, PRACTICE, 11, "middle", True, True)

PM2 = [(0, 0.5), (1, 0.25), (2, 0.125), (3, 0.0625), (4, 0.0625)]
MEAN2 = sum(x * w for x, w in PM2)
p2 = Plot(322, 30, 226, 186, (-1.2, 5.2), (-0.16, 0.6))
p2.axes((0, 1, 2, 3, 4), (0.25, 0.5), "x", "f(x)", yfmt=tfmt)
panel_title(p2, "çarpık kütle: E(X) = " + tfmt(round(MEAN2, 4)), THEORY)
for x, w in PM2:
    p2.add('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" fill-opacity="0.5" stroke="%s" stroke-width="0.9"/>'
           % (p2.X(x - 0.36), p2.Y(w), p2.X(x + 0.36) - p2.X(x - 0.36), p2.Y(0) - p2.Y(w), THEORY, THEORY))
p2.polygon([(MEAN2, 0), (MEAN2 - 0.22, -0.12), (MEAN2 + 0.22, -0.12)], PRACTICE, 0.9)
p2.label(MEAN2, -0.12, "E(X)", 0, 15, PRACTICE, 11, "middle", True, True)
OUT["beklenen-deger-denge"] = figure(
    560, 240, [p1, p2],
    "Beklenen değer, olasılık kütlelerinin denge noktasıdır: eksen bir çubuk, olasılıklar üzerine konmuş "
    "ağırlıklar gibi düşünülürse çubuk tam <em>E</em>(<em>X</em>) noktasında dengede durur. Solda simetrik "
    "kütle ortada dengelenir; sağda kütle sola yığıldığından denge noktası sola kayar ve alınan değerlerden "
    "hiçbirine eşit olmak zorunda değildir.",
    aria="Iki olasilik kutle dagilimi ve altlarinda denge noktasini gosteren ucgen destek")

# ============================================================ bileske-donusum-sema
# The composition Y = g o X: sample space -> values of X -> values of Y, and the pull-back of (-inf, y].
p = Plot(0, 0, 560, 245, (0, 56), (0, 24.5))   # 10 px per unit in both directions
INV = "&#8315;&#185;"          # superscript -1
MI = "(" + MINUS_S + INF + ", y]"


def curved_arrow(p, a, c, b, color, width=1.4, head=7.0):
    """Quadratic Bezier arrow a -> b with control point c (data coordinates)."""
    ax, ay, cx, cy, bx, by = p.X(a[0]), p.Y(a[1]), p.X(c[0]), p.Y(c[1]), p.X(b[0]), p.Y(b[1])
    p.add('<path d="M %.1f %.1f Q %.1f %.1f %.1f %.1f" fill="none" stroke="%s" stroke-width="%.1f"/>'
          % (ax, ay, cx, cy, bx, by, color, width))
    dx, dy = bx - cx, by - cy
    L = math.hypot(dx, dy) or 1.0
    ux, uy = dx / L, dy / L
    px, py = -uy, ux
    hw = head * 0.42
    p.add('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>'
          % (bx, by, bx - ux * head + px * hw, by - uy * head + py * hw,
             bx - ux * head - px * hw, by - uy * head - py * hw, color))


LV = 11.5   # the common level of the two number lines
# --- the sample space Omega (left) ---
p.add('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s" fill-opacity="0.06" stroke="%s" stroke-width="1.2"/>'
      % (p.X(8.0), p.Y(LV), 65.0, 78.0, TEXT, TEXT))
p.label(8.0, 17.4, "&#937;", 0, 0, TEXT, 13, "middle", True, True)
# the pre-image (Y <= y) inside Omega
p.add('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s" fill-opacity="0.30" stroke="%s" stroke-width="1.2"/>'
      % (p.X(7.4), p.Y(9.8), 38.0, 30.0, PRACTICE, PRACTICE))
p.label(7.4, 9.8, "(Y " + LEQ_S + " y)", 0, 4, PRACTICE, 11, "middle", True, True)

# --- the values of X (middle line) ---
p.arrow((19.6, LV), (35.2, LV), TEXT, 1.2, 7.0, opacity=0.6)
p.label(35.0, LV, "&#8477;", 0, -9, TEXT, 11.5, "end", True, False)
C0, C1 = 23.0, 29.6
p.line([(C0, LV), (C1, LV)], PRACTICE, 6.0, None, 0.35)
dot(p, (C0, LV), PRACTICE, 3.6)
dot(p, (C1, LV), PRACTICE, 3.6)
p.label((C0 + C1) / 2, LV, "g" + INV + MI, 0, -12, PRACTICE, 11, "middle", True, True)
p.label((C0 + C1) / 2, LV, "X'in değerleri", 0, 17, TEXT, 10.5, "middle", False, True)

# --- the values of Y (right line) ---
p.arrow((39.6, LV), (55.4, LV), TEXT, 1.2, 7.0, opacity=0.6)
p.label(55.2, LV, "&#8477;", 0, -9, TEXT, 11.5, "end", True, False)
YV = 49.6
p.line([(39.6, LV), (YV, LV)], PRACTICE, 6.0, None, 0.35)
dot(p, (YV, LV), PRACTICE, 3.6)
p.label(YV, LV, "y", 0, 17, PRACTICE, 11.5, "middle", True, True)
p.label(44.6, LV, MI, 0, -12, PRACTICE, 11, "middle", True, True)
p.label(46.0, LV, "Y'nin değerleri", 0, 31, TEXT, 10.5, "middle", False, True)

# --- the two maps and the composition ---
p.arrow((14.9, LV), (19.0, LV), THEORY, 1.8, 8.0)
p.label(16.9, LV, "X", 0, -8, THEORY, 12.5, "middle", True, True)
p.arrow((35.6, LV), (39.2, LV), THEORY, 1.8, 8.0)
p.label(37.4, LV, "g", 0, -8, THEORY, 12.5, "middle", True, True)
curved_arrow(p, (10.6, 18.7), (28.0, 24.2), (46.5, 15.6), THEORY, 1.5, 8.0)
p.label(28.0, 22.4, "Y = g(X),   Y(&#969;) = g(X(&#969;))", 0, 0, THEORY, 12, "middle", True, True)

# --- the pull-back chain along the bottom ---
BL = 2.2
p.label(8.0, BL, "olay", 0, 4, PRACTICE, 12, "middle", True, False)
p.label(26.3, BL, "Borel kümesi", 0, 4, PRACTICE, 12, "middle", True, False)
p.label(46.0, BL, "Borel kümesi", 0, 4, PRACTICE, 12, "middle", True, False)
p.arrow((21.0, BL), (11.0, BL), TEXT, 1.3, 7.0, opacity=0.7)
p.label(16.0, BL, "X" + INV, 0, -6, TEXT, 11, "middle", False, True)
p.arrow((40.0, BL), (32.0, BL), TEXT, 1.3, 7.0, opacity=0.7)
p.label(36.0, BL, "g" + INV, 0, -6, TEXT, 11, "middle", False, True)
p.label(8.0, 4.9, "X" + INV + "(g" + INV + MI + ")", 0, 0, PRACTICE, 10.5, "middle", False, True)

OUT["bileske-donusum-sema"] = figure(
    560, 245, [p],
    "Bileşke <em>Y</em> = <em>g</em> &#8728; <em>X</em>, bir sonucu önce <em>X</em> ile bir sayıya, sonra "
    "<em>g</em> ile ikinci bir sayıya götürür. (<em>Y</em> &#8804; <em>y</em>) olayı sağdan sola geri "
    "çekilerek bulunur: (&#8722;&#8734;, <em>y</em>] Borel kümesidir, <em>g</em> Borel-ölçülebilir olduğundan "
    "<em>g</em><sup>&#8722;1</sup>((&#8722;&#8734;, <em>y</em>]) de Borel kümesidir ve <em>X</em> rastgele "
    "değişken olduğundan onun ters görüntüsü bir olaydır. Koşulun <em>X</em>'e değil <em>g</em>'ye "
    "konmasının nedeni budur.",
    css_class=WIDE,
    aria="Ornek uzay, X'in degerleri ve Y'nin degerleri; y'nin solundaki yari dogru g ve X ile geri cekilerek Omega icindeki olaya ulasiyor")

# ============================================================ binom-normal-yaklasim
# B(n; 0.3) bars for n = 5, 20, 80 with the matching normal density N(np, np(1-p)) on top.
P_B = 0.3


def binom_pmf(n, p, k):
    return math.comb(n, k) * p ** k * (1 - p) ** (n - k)


def norm_pdf(x, mu, sd):
    return math.exp(-(x - mu) ** 2 / (2 * sd * sd)) / (sd * math.sqrt(2 * math.pi))


SPECS = (
    (5, (-0.9, 5.9), (0, 1, 2, 3, 4, 5), (0.1, 0.2, 0.3, 0.4), 0.44),
    (20, (-0.9, 13.5), (0, 4, 8, 12), (0.1, 0.2), 0.23),
    (80, (9.5, 38.5), (12, 18, 24, 30, 36), (0.05, 0.1), 0.115),
)
panels = []
for i, (n, xr, xt, yt, ymax) in enumerate(SPECS):
    mu = n * P_B
    sd = math.sqrt(n * P_B * (1 - P_B))
    q = Plot(24 + i * 184, 32, 160, 170, xr, (0.0, ymax))
    q.axes(xt, yt, "x", "", yfmt=tfmt)
    panel_title(q, "n = %d" % n, THEORY)
    for k in range(n + 1):
        if not (xr[0] < k < xr[1]):
            continue
        h = binom_pmf(n, P_B, k)
        if h < 0.0002:
            continue
        q.add('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" fill-opacity="0.5" stroke="%s" stroke-width="0.9"/>'
              % (q.X(k - 0.4), q.Y(h), q.X(k + 0.4) - q.X(k - 0.4), q.Y(0) - q.Y(h), THEORY, THEORY))
    curve(q, lambda x, m=mu, s=sd: norm_pdf(x, m, s), xr[0] + 0.05, xr[1] - 0.05, PRACTICE, 1.9, 240)
    q.text_px(q.x0 + q.w - 4, q.y0 + 14, "np = " + tfmt(mu), PRACTICE, 10, "end", False, True)
    q.text_px(q.x0 + q.w - 4, q.y0 + 27, "&#963; = " + tfmt(round(sd, 2)), PRACTICE, 10, "end", False, True)
    panels.append(q)
OUT["binom-normal-yaklasim"] = figure(
    570, 236, panels,
    "<em>p</em> = 0,3 için binom çubukları ve üstlerine çizilen N(<em>np</em>, <em>np</em>(1 &#8722; <em>p</em>)) normal "
    "yoğunluğu. <em>n</em> = 5'te çubuklar sağa çarpıktır ve çan eğrisine uymaz; <em>n</em> büyüdükçe çarpıklık "
    "silinir ve <em>n</em> = 80'de çubuk tepeleri neredeyse eğrinin üstündedir. Bu, binom dağılımının "
    "normal yaklaşımıdır; nedenini merkezi limit teoremiyle göreceğiz.",
    css_class=WIDE,
    aria="n = 5, 20 ve 80 icin p = 0,3 binom cubuklari ve ustlerine oturan normal yogunluk egrisi")

# ============================================================ binom-olasilik-fonksiyonu
# Binomial pmf for n = 10 and three values of p, side by side.
N_B = 10


def binom_pmf(n, p, k):
    return math.comb(n, k) * p ** k * (1 - p) ** (n - k)


panels = []
for i, (pp, col) in enumerate(((0.2, THEORY), (0.5, BASE), (0.8, PRACTICE))):
    q = Plot(24 + i * 184, 32, 160, 170, (-0.9, 10.9), (0.0, 0.34))
    q.axes((0, 2, 4, 6, 8, 10), (0.1, 0.2, 0.3), "x", "", yfmt=tfmt)
    panel_title(q, "p = " + tfmt(pp), col)
    for k in range(N_B + 1):
        h = binom_pmf(N_B, pp, k)
        q.add('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" fill-opacity="0.55" stroke="%s" stroke-width="0.9"/>'
              % (q.X(k - 0.38), q.Y(h), q.X(k + 0.38) - q.X(k - 0.38), q.Y(0) - q.Y(h), col, col))
    q.label(N_B * pp, binom_pmf(N_B, pp, round(N_B * pp)), "np = " + fmt(N_B * pp), 0, -13, col, 10, "middle", False, True)
    panels.append(q)
OUT["binom-olasilik-fonksiyonu"] = figure(
    570, 236, panels,
    "<em>n</em> = 10 için binom olasılık fonksiyonu. Kütle <em>np</em> çevresinde toplanır: <em>p</em> = 0,5'te "
    "simetrik, küçük <em>p</em>'de sağa, büyük <em>p</em>'de sola çarpıktır. Çubukların toplam yüksekliği her "
    "panelde 1'dir.",
    css_class=WIDE,
    aria="n=10 icin p=0,2, 0,5 ve 0,8 degerlerinde binom olasilik fonksiyonu cubuklari")

# ============================================================ borel-uretme
# How the Borel sigma-algebra is generated: open intervals -> complement and countable union
# (repeated) -> sigma(open intervals) = B(R). Below, three sample Borel sets on the number line.
# Data coordinates are pixels: x from the left, y from the top (yrange reversed on purpose).
W, H = 560, 230
p = Plot(0, 0, W, H, (0, W), (H, 0))


def rbox(x1, y1, x2, y2, color, opacity, width=1.5):
    p.add('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="7" fill="%s" fill-opacity="%.2f" '
          'stroke="%s" stroke-width="%.1f"/>' % (p.X(x1), p.Y(y1), p.X(x2) - p.X(x1), p.Y(y2) - p.Y(y1),
                                                  color, opacity, color, width))


# --- top: the generation scheme ---------------------------------------------------------------
BY1, BY2 = 12, 66
BOXES = ((14, 162, THEORY, 0.10, 1.5, ("açık aralıklar", "(a, b)")),
         (206, 356, BASE, 0.10, 1.5, ("tümleyen ve", "sayılabilir birleşim", "(sayılabilir kez)")),
         (400, 546, THEORY, 0.16, 2.2, ("&#963;(açık aralıklar)", "= " + "<tspan font-weight=\"bold\">B</tspan>(&#8477;)")))
for x1, x2, col, op, wd, lines in BOXES:
    rbox(x1, BY1, x2, BY2, col, op, wd)
    cx, n = (x1 + x2) / 2, len(lines)
    for i, s in enumerate(lines):
        small = s.startswith("(sayılabilir")
        size = 9.5 if small else 11.5
        yy = (BY1 + BY2) / 2 + (i - (n - 1) / 2) * 15 + 4
        p.label(cx, yy, s, 0, 0, col if not small else TEXT, size, "middle", not small and i == 0, small)
p.arrow((BOXES[0][1] + 5, (BY1 + BY2) / 2), (BOXES[1][0] - 5, (BY1 + BY2) / 2), TEXT, 1.6, 8)
p.arrow((BOXES[1][1] + 5, (BY1 + BY2) / 2), (BOXES[2][0] - 5, (BY1 + BY2) / 2), TEXT, 1.6, 8)
p.label(W / 2, BY2 + 16, "en küçük &#963;-cebir: aralıklardan tümleyen ve sayılabilir birleşimle üretilen her küme Borel'dir",
        0, 0, TEXT, 10, "middle", False, True)

# --- bottom: three example Borel sets ---------------------------------------------------------
TY, LY, CY = 106, 162, 194        # title, number line and caption rows
PANELS = ((14, 178), (206, 356), (382, 546))


def number_line(x1, x2, y):
    p.arrow((x1, y), (x2, y), TEXT, 1.1, 6.5, opacity=0.6)


def name(x, y, s, color=TEXT):
    """Name of a marked point, just below the line (the dot itself marks the spot)."""
    p.label(x, y, s, 0, 17, color, 10.5, "middle", False, True)


def title(x1, x2, s, color=THEORY):
    p.label((x1 + x2) / 2, TY, s, 0, 0, color, 11.5, "middle", True)


def caption(x1, x2, lines):
    for i, s in enumerate(lines):
        p.label((x1 + x2) / 2, CY + 13 * i, s, 0, 0, TEXT, 9.5, "middle", False, True)


# (1) the closed interval [a, b]
x1, x2 = PANELS[0]
title(x1, x2, "kapalı aralık [a, b]")
number_line(x1, x2, LY)
a, b = x1 + 38, x2 - 42
p.line([(a, LY), (b, LY)], THEORY, 3.4)
dot(p, (a, LY), THEORY, 4.0)
dot(p, (b, LY), THEORY, 4.0)
name(a, LY, "a")
name(b, LY, "b")
caption(x1, x2, ("{a}, (a, b) ve {b} kümelerinin", "birleşimi"))

# (2) the singleton {a}
x1, x2 = PANELS[1]
title(x1, x2, "tek nokta {a}")
number_line(x1, x2, LY)
a = (x1 + x2) / 2
for k, (half, dy) in enumerate(((52, -30), (30, -16))):
    p.line([(a - half, LY + dy), (a + half, LY + dy)], THEORY, 1.8, None, 0.9 - 0.2 * k)
    hollow(p, (a - half, LY + dy), THEORY, 3.0, 1.4)
    hollow(p, (a + half, LY + dy), THEORY, 3.0, 1.4)
guide(p, [(a, LY - 36), (a, LY)], PRACTICE, 0.55)
dot(p, (a, LY), PRACTICE, 4.2)
name(a, LY, "a", PRACTICE)
p.label(a + 61, LY - 30, "n = 1", 0, 4, THEORY, 9.5, "start", False, True)
p.label(a + 61, LY - 16, "n = 2", 0, 4, THEORY, 9.5, "start", False, True)
caption(x1, x2, ("iç içe (a " + MINUS_S + " 1/n, a + 1/n) açık", "aralıklarının kesişimi"))

# (3) the rationals Q
x1, x2 = PANELS[2]
title(x1, x2, "rasyoneller &#8474;")
number_line(x1, x2, LY)
for t in (0.06, 0.13, 0.19, 0.28, 0.33, 0.41, 0.50, 0.55, 0.62, 0.71, 0.77, 0.86):
    dot(p, (x1 + t * (x2 - x1), LY), THEORY, 2.6)
p.label(x1 + 0.94 * (x2 - x1), LY, "&#8230;", 0, -6, THEORY, 11, "middle")
p.label(x1 + 0.28 * (x2 - x1), LY, "q" + subs("1"), 0, -9, THEORY, 9.5, "middle", False, True)
p.label(x1 + 0.55 * (x2 - x1), LY, "q" + subs("2"), 0, -9, THEORY, 9.5, "middle", False, True)
p.label(x1 + 0.13 * (x2 - x1), LY, "q" + subs("3"), 0, -9, THEORY, 9.5, "middle", False, True)
p.label(x1 + 0.71 * (x2 - x1), LY, "q" + subs("4"), 0, -9, THEORY, 9.5, "middle", False, True)
caption(x1, x2, ("sayılabilir tane tek noktanın", "birleşimi"))

OUT["borel-uretme"] = figure(
    W, H, [p],
    "Borel cebrinin kuruluşu. Açık aralıklar sınıfından başlanır; tümleyen ve sayılabilir birleşim "
    "işlemleri (dolayısıyla sayılabilir kesişim de) sayılabilir kez uygulanarak ulaşılan her küme "
    "Borel kümesidir ve bu kümelerin sınıfı, açık aralıkları kapsayan en küçük &#963;-cebir olan "
    "<strong>B</strong>(&#8477;)'dir. Altta üç örnek: kapalı aralık [<em>a</em>, <em>b</em>] iki tek nokta ile "
    "bir açık aralığın birleşimi, tek nokta {<em>a</em>} daralan açık aralıkların kesişimi, &#8474; ise "
    "sayılabilir tane tek noktanın birleşimi olarak Borel'dir.",
    css_class=WIDE,
    aria="Ustte uc kutu ve oklar: acik araliklar, tumleyen ve sayilabilir birlesim, Borel cebri B(R). "
         "Altta uc sayi dogrusu: kapali aralik, tek nokta ve rasyoneller kumesi ornek Borel kumeleri")

# ============================================================ carpim-yogunlugu-lnz
# Z = XY for the density f = 2 on the triangle 0 < x < y < 1 (exm-carpim-varyansi):
# left, the event {XY <= z} cut out of the triangle by the hyperbola xy = z (z = 0.3);
# right, the density f_Z(z) = -ln z on (0, 1] with F_Z(z) shaded.
Z0 = 0.3
SQ = math.sqrt(Z0)


def it(s):
    return '<tspan font-style="italic">%s</tspan>' % s


FZ = it("F") + subs(it("Z")) + "(" + it("z") + ")"
fz = it("f") + subs(it("Z")) + "(" + it("z") + ")"


def xfmt_l(t):
    if abs(t - Z0) < 1e-9:
        return it("z")
    if abs(t - SQ) < 1e-9:
        return "&#8730;" + it("z")
    return fmt(t)


# ---- left: the triangle and the hyperbola -------------------------------------
p1 = Plot(46, 34, 196, 184, (-0.17, 1.32), (-0.17, 1.28))
# the support of the joint density
p1.polygon([(0, 0), (1, 1), (0, 1)], THEORY, 0.16, THEORY, 1.4)
# the event {xy <= z} inside the triangle
hyp = [(Z0 + (SQ - Z0) * k / 40, Z0 / (Z0 + (SQ - Z0) * k / 40)) for k in range(41)]
p1.polygon([(0, 0), (0, 1), (Z0, 1)] + hyp, PRACTICE, 0.42, "none")
# the hyperbola: solid where it bounds the event, dashed below the diagonal
curve(p1, lambda x: Z0 / x, Z0, SQ, PRACTICE, 1.9, 60)
curve(p1, lambda x: Z0 / x, SQ, 1.0, PRACTICE, 1.3, 60, "4 3", 0.7)
p1.origin_axes("x", "y", xticks=(Z0, SQ, 1), yticks=(1,), xfmt=xfmt_l)
guide(p1, [(SQ, 0), (SQ, SQ)], TEXT, 0.45)
guide(p1, [(Z0, 0), (Z0, Z0)], TEXT, 0.45)
panel_title(p1, it("f") + "(" + it("x") + ", " + it("y") + ") = 2,   0 &lt; " + it("x") + " &lt; " + it("y") + " &lt; 1", THEORY, 11)
p1.label(0.17, 0.6, it("xy") + " " + LEQ_S + " " + it("z"), 0, 0, PRACTICE, 11, "middle", True)
p1.label(0.6, 0.8, it("xy") + " = " + it("z"), 0, 0, PRACTICE, 10.5, "middle")
p1.label(0.97, 0.17, FZ + " = " + it("z") + " " + MINUS_S + " " + it("z") + " ln " + it("z"), 0, 0, PRACTICE, 10, "middle")
p1.label(0.97, 0.05, "(turuncu alanın 2 katı)", 0, 0, PRACTICE, 9.5, "middle")

# ---- right: the density of Z ----------------------------------------------------
p2 = Plot(318, 34, 226, 184, (0, 1.14), (0, 3.4))
g = lambda z: -math.log(z)
# area under the curve (clipped at the top), F_Z(z) part in orange
zs = [0.001 + (1 - 0.001) * k / 400 for k in range(401)]
under = [(z, min(g(z), 3.4)) for z in zs]
p2.polygon([(0, 0)] + [(0, 3.4)] + under + [(1, 0)], THEORY, 0.16, "none")
part = [(z, min(g(z), 3.4)) for z in zs if z <= Z0]
p2.polygon([(0, 0), (0, 3.4)] + part + [(Z0, g(Z0)), (Z0, 0)], PRACTICE, 0.42, "none")
clipped(p2, g, 0.001, 1.0, THEORY, 2.0)
p2.axes((Z0, 0.5, 1), (1, 2, 3), "z", fz, xfmt=lambda t: it("z") if abs(t - Z0) < 1e-9 else fmt(t))
guide(p2, [(Z0, 0), (Z0, g(Z0))], TEXT, 0.45)
p2.add('<circle cx="%.1f" cy="%.1f" r="4.2" fill="%s" stroke="%s" stroke-width="1.6"/>'
       % (p2.X(Z0), p2.Y(g(Z0)), PRACTICE, BG))
panel_title(p2, fz + " = " + MINUS_S + "ln " + it("z") + ",   0 &lt; " + it("z") + " &lt; 1", THEORY, 11)
p2.label(0.14, 1.2, FZ, 0, 0, PRACTICE, 11, "middle", True)
p2.label(0.52, 0.2, "alan = 1", 0, 0, THEORY, 10.5, "middle")
p2.label(0.72, 2.9, it("E") + "(" + it("Z") + ") = 1/4", 0, 0, TEXT, 11, "middle")
p2.label(0.72, 2.45, "Var(" + it("Z") + ") = 7/144", 0, 0, TEXT, 11, "middle")
p2.label(Z0, g(Z0), MINUS_S + "ln " + it("z"), 9, -6, PRACTICE, 10.5, "start")

OUT["carpim-yogunlugu-lnz"] = figure(
    560, 245, [p1, p2],
    "<em>Z</em> = <em>XY</em> çarpımının dağılımı. Solda mavi üçgen, ortak yoğunluğun 2 olduğu bölge; "
    "<em>xy</em> = <em>z</em> hiperbolünün altında kalan turuncu parça {<em>XY</em> &#8804; <em>z</em>} olayıdır ve "
    "alanının 2 katı <em>F<sub>Z</sub></em>(<em>z</em>) = <em>z</em> &#8722; <em>z</em> ln <em>z</em> verir. "
    "Sağda <em>Z</em>'nin yoğunluğu &#8722;ln <em>z</em>: <em>z</em> &#8594; 0 iken sınırsız büyür ama altındaki "
    "toplam alan 1'dir; turuncu alan yine <em>F<sub>Z</sub></em>(<em>z</em>)'dir. Beklenen değer "
    "<em>E</em>(<em>Z</em>) = 1/4, varyans 7/144'tür.",
    css_class=WIDE,
    aria="Solda ucgen bolgede xy esit z hiperboluyle kesilen olay; sagda f_Z(z) = -ln z yogunlugu ve F_Z(z) alani")

# ============================================================ carpma-kurali-agac
# Tree diagram for the multiplication rule: root -> 3 branches (a_i) -> 2 branches each (b_j) -> 6 leaves.
# The panel maps data coordinates one-to-one onto pixels (y grows downward).
p = Plot(0, 0, 480, 252, (0, 480), (252, 0))
ROOT = (56, 130)
AX, LX = 218, 380                       # x of the first-step nodes and of the leaves
AY = (64, 130, 196)                     # y of the first-step nodes
DY = 17                                 # half the vertical spread of a leaf pair
MID1 = (ROOT[0] + AX) / 2
MID2 = (AX + LX) / 2


def ix(k):
    """Upright subscript index inside an italic label."""
    return subs('<tspan font-style="normal">%s</tspan>' % k)


# column headers
p.text_px(MID1, 20, "1. adım: n" + subs("1") + " = 3 biçim", THEORY, 11, "middle", True, False)
p.text_px(MID2, 20, "2. adım: n" + subs("2") + " = 2 biçim", PRACTICE, 11, "middle", True, False)
p.text_px(LX + 12, 20, "sonuçlar", TEXT, 11, "start", True, False)

for i, ay in enumerate(AY):
    # first step: root -> a_i
    p.line([ROOT, (AX, ay)], THEORY, 1.5)
    if ay < ROOT[1]:
        p.label(MID1, (ROOT[1] + ay) / 2, "a" + ix(i + 1), -3, -6, THEORY, 11, "end", False, True)
    elif ay > ROOT[1]:
        p.label(MID1, (ROOT[1] + ay) / 2, "a" + ix(i + 1), -3, 15, THEORY, 11, "end", False, True)
    else:
        p.label(MID1, ay, "a" + ix(i + 1), 0, -6, THEORY, 11, "middle", False, True)
    # second step: a_i -> (a_i, b_j)
    for j, sgn in enumerate((-1, 1)):
        ly = ay + sgn * DY
        p.line([(AX, ay), (LX, ly)], PRACTICE, 1.5)
        p.label(MID2, (ay + ly) / 2, "b" + ix(j + 1), 0, -6 if sgn < 0 else 13, PRACTICE, 11, "middle", False, True)
        dot(p, (LX, ly), TEXT, 3.4)
        p.label(LX, ly, "(a" + ix(i + 1) + ", b" + ix(j + 1) + ")", 11, 4, TEXT, 10.5, "start", False, True)
    dot(p, (AX, ay), THEORY, 4.0)

dot(p, ROOT, TEXT, 4.6)
p.label(ROOT[0], ROOT[1], "başla", -9, 4, TEXT, 10.5, "end", False, True)
p.text_px(240, 243, "n" + ix(1) + " n" + ix(2) + " = 3 &#183; 2 = 6 sonuç", TEXT, 12, "middle", True, True)

OUT["carpma-kurali-agac"] = figure(
    480, 252, [p],
    "Çarpma kuralı için ağaç diyagramı. Birinci adım <em>a</em><sub>1</sub>, <em>a</em><sub>2</sub>, "
    "<em>a</em><sub>3</sub> biçimlerinden biriyle yapılır (<em>n</em><sub>1</sub> = 3 dal); hangisi seçilmiş "
    "olursa olsun ikinci adım <em>b</em><sub>1</sub> ya da <em>b</em><sub>2</sub> biçimiyle yapılır "
    "(<em>n</em><sub>2</sub> = 2 dal). Her yaprak bir (<em>a</em><sub><em>i</em></sub>, <em>b</em><sub><em>j</em></sub>) "
    "çiftine, yani işin bir yapılış biçimine karşılık gelir; yaprak sayısı dal sayılarının çarpımı 3 &#183; 2 = 6'dır.",
    aria="Carpma kurali agac diyagrami: kokten uc dal, her daldan iki dal, toplam alti yaprak")

# ============================================================ cauchy-yogunlugu
# Two panels: X uniform on (-pi/2, pi/2) with the curve y = tan x on the left,
# the Cauchy density of Y = tan X against the standard normal on the right.
HALF_PI = math.pi / 2
INV_PI = 1 / math.pi


def cauchy(y):
    return INV_PI / (1 + y * y)


def normal(y):
    return math.exp(-y * y / 2) / math.sqrt(2 * math.pi)


def mfmt(v):
    """Turkish decimal comma and a true minus sign on tick labels."""
    return tfmt(v).replace("-", MINUS_S)


# ---------------------------------------------------------------- left panel
p = Plot(44, 28, 226, 192, (-2.2, 2.2), (-2.8, 2.8))
p.origin_axes("x", "y")
# the uniform density: a flat line at height 1/pi over (-pi/2, pi/2), shaded beneath
rect(p, -HALF_PI, HALF_PI, 0, INV_PI, PRACTICE, 0.22)
p.line([(-HALF_PI, INV_PI), (HALF_PI, INV_PI)], PRACTICE, 2.0)
# vertical asymptotes of tan
guide(p, [(-HALF_PI, -2.8), (-HALF_PI, 2.8)], TEXT, 0.5)
guide(p, [(HALF_PI, -2.8), (HALF_PI, 2.8)], TEXT, 0.5)
clipped(p, math.tan, -1.5, 1.5, THEORY, 2.0, 600)
# labels
p.label(-HALF_PI, 0, MINUS_S + "&#960;/2", -4, -5, TEXT, 10.5, "end")
p.label(HALF_PI, 0, "&#960;/2", 4, -5, TEXT, 10.5, "start")
p.label(-1.5, 0.6, "f" + subs("X") + "(x) = 1/&#960;", 0, 0, PRACTICE, 10.5, "start", False, True)
p.label(0.3, -0.95, "y = tan x", 0, 0, THEORY, 10.5, "start", False, True)
p.text_px(p.x0 + p.w / 2, p.y0 - 12, "Düzgün X ve y = tan x", TEXT, 11.5, "middle", True)

# --------------------------------------------------------------- right panel
q = Plot(318, 28, 216, 192, (-6.8, 6.8), (0, 0.44))
q.axes((-6, -3, -1, 0, 1, 3, 6), (0.1, 0.2, 0.3, 0.4), "y", "f" + subs("Y") + "(y)",
       xfmt=mfmt, yfmt=tfmt)
# shaded tails |y| > 1 under the Cauchy curve
N = 120
left_tail = [(-6.8, 0)] + [(-6.8 + 5.8 * k / N, cauchy(-6.8 + 5.8 * k / N)) for k in range(N + 1)] + [(-1, 0)]
right_tail = [(1, 0)] + [(1 + 5.8 * k / N, cauchy(1 + 5.8 * k / N)) for k in range(N + 1)] + [(6.8, 0)]
q.polygon(left_tail, PRACTICE, 0.25)
q.polygon(right_tail, PRACTICE, 0.25)
# the standard normal for comparison (faint, dashed) and the Cauchy density
curve(q, normal, -6.8, 6.8, TEXT, 1.5, 300, "5 3", 0.55)
curve(q, cauchy, -6.8, 6.8, PRACTICE, 2.0, 300)
dot(q, (0, INV_PI), PRACTICE, 3.2)
# labels
q.label(-1.1, INV_PI, "1/&#960; &#8776; 0,318", 0, 4, PRACTICE, 10.5, "end")
q.label(0.75, 0.37, "standart normal", 0, 0, TEXT, 10.5, "start", False, True)
q.label(-2.6, 0.06, "Cauchy", 0, 0, PRACTICE, 10.5, "end", False, True)
q.label(3.95, 0.22, "P(|Y| &gt; 1) = 1/2", 0, 0, PRACTICE, 10.5, "middle", False, True)
q.arrow((3.2, 0.2), (2.45, 0.065), PRACTICE, 1.2, 6.0)
q.text_px(q.x0 + q.w / 2, q.y0 - 12, "Y = tan X: Cauchy yoğunluğu", TEXT, 11.5, "middle", True)

OUT["cauchy-yogunlugu"] = figure(
    560, 245, [p, q],
    "Tanjant dönüşümü ve Cauchy yoğunluğu. Solda <em>X</em>, (&#8722;&#960;/2, &#960;/2) aralığında düzgün dağılır: "
    "yoğunluğu 1/&#960; yüksekliğindeki dikdörtgendir; <em>y</em> = tan <em>x</em> eğrisi bu aralığı bütün gerçel "
    "eksene gerer, uçlara yaklaştıkça diklesir. Sağda <em>Y</em> = tan <em>X</em>'in yoğunluğu "
    "1/(&#960;(1 + <em>y</em><sup>2</sup>)) ile kesikli standart normal yoğunluk karşılaştırılmıştır: tepe 1/&#960; "
    "&#8776; 0,318 normalinkinden alçaktır, ama kuyruklar çok daha ağırdır; taralı |<em>Y</em>| &gt; 1 bölgesinin "
    "olasılığı 1/2'dir.",
    css_class=WIDE,
    aria="Solda duzgun dagilimli X'in dikdortgen yogunlugu ve y = tan x egrisi, sagda Y = tan X'in Cauchy "
         "yogunlugu ile kesikli standart normal yogunlugu; |Y| buyuk 1 kuyruklari taranmis")

# ============================================================ cebir-sigma-cebir-fark
# An algebra that is not a sigma-algebra: on N, the class of sets that are finite or have a finite
# complement. A_n = {2n} is finite (in the algebra), finite unions stay finite (in the algebra),
# but the countable union {2, 4, 6, ...} is infinite with an infinite complement (not in it).
# Data x = the natural number, data y = pixels from the top (yrange is reversed on purpose).
W, H = 560, 250
p = Plot(12, 0, 536, H, (0.35, 13.95), (H, 0))
NS = list(range(1, 13))          # the naturals shown; the dots continue as "..."
X_DOTS = 13.3                    # where the ellipsis sits
ROWS = (52, 128, 202)            # y of the three number lines (pixels from top)


def number_line(y):
    p.line([(0.5, y), (13.75, y)], TEXT, 1.0, None, 0.35)
    p.label(X_DOTS, y, "&#8230;", 0, 4, TEXT, 12, "middle")


def dots(y, chosen, color, r_on=4.2):
    """Grey dots for every n, filled coloured dots for the chosen ones."""
    for n in NS:
        if n in chosen:
            p.add('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s"/>' % (p.X(n), p.Y(y), r_on, color))
        else:
            p.add('<circle cx="%.1f" cy="%.1f" r="2.6" fill="%s" opacity="0.35"/>' % (p.X(n), p.Y(y), TEXT))


def row_title(y, left, right, right_color):
    p.text_px(p.X(0.5), p.Y(y), left, TEXT, 11, "start")
    p.text_px(p.X(13.75), p.Y(y), right, right_color, 11, "end", True)


def box(x1, x2, y, color, opacity, dash=None):
    """Frame around the dots of one row (rounded rect in pixel coordinates)."""
    da = ' stroke-dasharray="%s"' % dash if dash else ""
    p.add('<rect x="%.1f" y="%.1f" width="%.1f" height="18" rx="5" fill="%s" fill-opacity="%.2f" '
          'stroke="%s" stroke-width="1.5"%s/>' % (p.X(x1), p.Y(y) - 9, p.X(x2) - p.X(x1), color, opacity, color, da))


# --- row 1: the sets A_n = {2n}, each a single point ----------------------------------------
y = ROWS[0]
row_title(y - 32, "A" + subs("n") + " = {2n}:  A" + subs("1") + " = {2}, A" + subs("2") + " = {4}, "
          "A" + subs("3") + " = {6}, &#8230;   her biri sonlu", "cebirde", THEORY)
number_line(y)
evens = [n for n in NS if n % 2 == 0]
for k, n in enumerate(evens, 1):
    p.add('<circle cx="%.1f" cy="%.1f" r="7.5" fill="none" stroke="%s" stroke-width="1.3"/>' % (p.X(n), p.Y(y), THEORY))
    p.label(n, y, "A" + subs(str(k)), 0, -14, THEORY, 9.5, "middle", False, True)
dots(y, evens, THEORY)
for n in NS:
    p.label(n, y, str(n), 0, 17, TEXT, 9.5, "middle")

# --- row 2: a finite union stays finite -------------------------------------------------------
y = ROWS[1]
row_title(y - 24, "sonlu birleşim:  A" + subs("1") + ", A" + subs("2") + ", A" + subs("3") + " birleşimi = {2, 4, 6}   sonlu",
          "cebirde", THEORY)
number_line(y)
box(1.55, 6.45, y, THEORY, 0.14)
dots(y, {2, 4, 6}, THEORY)

# --- row 3: the countable union of all A_n is the even numbers ----------------------------------
y = ROWS[2]
row_title(y - 24, "sayılabilir birleşim:  bütün A" + subs("n") + "'lerin birleşimi = {2, 4, 6, 8, &#8230;}   sonsuz",
          "cebirde DEĞİL", PRACTICE)
number_line(y)
box(1.55, 13.9, y, PRACTICE, 0.10, "5 3")
dots(y, evens, PRACTICE)
p.text_px(p.X(0.5), p.Y(y + 28), "tümleyeni {1, 3, 5, &#8230;} de sonsuz: ne kendisi ne tümleyeni sonlu",
          PRACTICE, 10.5, "start", False, True)

OUT["cebir-sigma-cebir-fark"] = figure(
    W, H, [p],
    "&#937; = &#8469; üzerinde \"sonlu ya da tümleyeni sonlu\" kümelerin sınıfı bir cebirdir ama "
    "&#963;-cebir değildir. <em>A<sub>n</sub></em> = {2<em>n</em>} kümelerinin her biri sonludur ve sınıftadır; "
    "sonlu tanesinin birleşimi yine sonludur ve sınıfta kalır. Bütün <em>A<sub>n</sub></em>'lerin sayılabilir "
    "birleşimi ise çift sayılar kümesidir: hem kendisi hem tümleyeni sonsuz olduğundan sınıfın dışına çıkar. "
    "Cebir ile &#963;-cebir arasındaki fark tam olarak bu sayılabilir birleşim adımıdır.",
    css_class=WIDE,
    aria="Dogal sayilar uzerinde uc satir: tek noktali A_n kumeleri, sonlu birlesimleri cebirde, "
         "sayilabilir birlesimi olan cift sayilar kesikli cerceveyle cebirde degil")

# ============================================================ chebyshev-kuyruk
# Chebyshev's inequality: the two tails |X - mu| >= k*sigma of a density (left, k = 2) and
# the bound 1/k^2 against the true normal tail probability 2(1 - Phi(k)) (right).
def phi_pdf(x):
    return math.exp(-x * x / 2) / math.sqrt(2 * math.pi)


def norm_tail(k):
    """P(|Z| >= k) = 2(1 - Phi(k)) for the standard normal."""
    return 2 * (1 - 0.5 * (1 + math.erf(k / math.sqrt(2))))


MU, SIG = "&#956;", "&#963;"
K = 2


def xfmt_(t):
    if t < 0:
        return MU + " " + MINUS_S + " " + str(K) + SIG
    return MU + " + " + str(K) + SIG


# ---- left: density with the two tails shaded ---------------------------------
p1 = Plot(44, 30, 226, 190, (-4.6, 4.6), (-0.05, 0.47))
p1.origin_axes("x", "f", xticks=(-K, K), xfmt=xfmt_)
p1.text_px(p1.X(0), p1.Y(0) + 15, MU, TEXT, 11, "middle")
panel_title(p1, "k = 2: " + MU + " &#177; 2" + SIG + " dışındaki kuyruklar", PRACTICE)
N = 120
left_tail = [(-4.5, 0)] + [(-4.5 + (-K + 4.5) * j / N, phi_pdf(-4.5 + (-K + 4.5) * j / N)) for j in range(N + 1)] + [(-K, 0)]
right_tail = [(K, 0)] + [(K + (4.5 - K) * j / N, phi_pdf(K + (4.5 - K) * j / N)) for j in range(N + 1)] + [(4.5, 0)]
p1.polygon(left_tail, PRACTICE, 0.55)
p1.polygon(right_tail, PRACTICE, 0.55)
curve(p1, phi_pdf, -4.5, 4.5, THEORY, 2.1, 360)
guide(p1, [(-K, 0), (-K, phi_pdf(-K))], PRACTICE, 0.8)
guide(p1, [(K, 0), (K, phi_pdf(K))], PRACTICE, 0.8)
# the tail probability, pointing at both shaded pieces
p1.label(-2.75, 0.30, "P(|X " + MINUS_S + " " + MU + "| " + GEQ_S + " 2" + SIG + ")", 0, 0, PRACTICE, 10.5, "middle", True)
p1.arrow((-2.75, 0.27), (-2.55, 0.05), PRACTICE, 1.3, 6.5)
p1.label(2.9, 0.30, "gerçek: 0,046", 0, 0, THEORY, 10.5, "middle")
p1.label(2.9, 0.235, "sınır: 1/k" + sups("2") + " = 0,25", 0, 0, PRACTICE, 10.5, "middle")
p1.arrow((2.75, 0.20), (2.55, 0.05), PRACTICE, 1.3, 6.5)

# ---- right: bound versus true probability as a function of k ------------------
p2 = Plot(322, 30, 226, 190, (0.8, 4.15), (0.0, 1.08))
p2.axes((1, 2, 3, 4), (0.25, 0.5, 0.75, 1), "k", "", yfmt=tfmt)
panel_title(p2, "k'ya göre: sınır ve gerçek olasılık", TEXT)
curve(p2, lambda k: 1 / (k * k), 1.0, 4.1, PRACTICE, 2.1, 200)
curve(p2, norm_tail, 1.0, 4.1, THEORY, 2.1, 200)
# legend in the empty upper-right corner; the colours match the curves
p2.text_px(p2.x0 + p2.w - 2, p2.y0 + 52, "1/k" + sups("2") + " (Chebyshev sınırı)", PRACTICE, 10.5, "end", True)
p2.text_px(p2.x0 + p2.w - 2, p2.y0 + 72, "2(1 " + MINUS_S + " &#934;(k)) (normal, gerçek)", THEORY, 10.5, "end", True)
for k, sb, sn, dyb, dyn in ((1, "1", "0,317", 4, 4), (2, "0,25", "0,046", -8, -8), (3, "0,111", "0,003", -8, -8)):
    dot(p2, (k, 1 / (k * k)), PRACTICE, 4.0)
    dot(p2, (k, norm_tail(k)), THEORY, 4.0)
    p2.label(k, 1 / (k * k), sb, 8, dyb, PRACTICE, 10.5, "start")
    p2.label(k, norm_tail(k), sn, 8, dyn, THEORY, 10.5, "start")

OUT["chebyshev-kuyruk"] = figure(
    560, 244, [p1, p2],
    "Chebyshev eşitsizliği, beklenen değerden en az <em>k</em>&#963; uzağa düşme olasılığını dağılımdan bağımsız "
    "olarak 1/<em>k</em><sup>2</sup> ile sınırlar. Solda bir yoğunluğun &#956; &#177; 2&#963; dışındaki iki kuyruğu "
    "taralıdır: sınır 1/4'tür, normal dağılım için gerçek olasılık 0,046'dır. Sağda <em>k</em> büyüdükçe iki eğri "
    "de sıfıra iner; ama sınır (turuncu) gerçek olasılığın (mavi) hep üstünde kalır ve aradaki açık, sınırın "
    "genelliğinin bedelidir.",
    css_class=WIDE,
    aria="Solda bir yogunlugun mu arti eksi 2 sigma disindaki kuyruklari taralidir; sagda k'ya gore Chebyshev siniri 1/k kare ve normal kuyruk olasiligi 2(1-Phi(k)) egrileri, k = 1, 2, 3 noktalarinda degerleriyle")

# ============================================================ dagilim-fonksiyonu-uc-para
# Step distribution function of X = number of heads in three tosses of a fair coin.
JUMPS = [(0, 0.0, 1 / 8), (1, 1 / 8, 4 / 8), (2, 4 / 8, 7 / 8), (3, 7 / 8, 1.0)]


def eighths(v):
    k = round(v * 8)
    return {0: "0", 8: "1"}.get(k, "%d/8" % k)


p = Plot(52, 26, 300, 206, (-1.3, 4.4), (-0.08, 1.12))
p.axes((0, 1, 2, 3), (1 / 8, 4 / 8, 7 / 8, 1.0), "x", "F" + subs("X") + "(x)", yfmt=eighths)
# flat pieces (right-continuous: closed on the left, open on the right)
p.line([(-1.25, 0), (0, 0)], THEORY, 2.2)
for x, lo, hi in JUMPS:
    nxt = x + 1 if x < 3 else 4.3
    p.line([(x, hi), (nxt, hi)], THEORY, 2.2)
    guide(p, [(x, lo), (x, hi)], THEORY, 0.5)
    dot(p, (x, hi), THEORY, 4.0)
    if x < 3:
        hollow(p, (x + 1, hi), THEORY, 4.0, 1.6)
hollow(p, (0, 0), THEORY, 4.0, 1.6)
guide(p, [(-1.3, 1.0), (4.4, 1.0)], TEXT, 0.35)
p.label(2.32, (4 / 8 + 7 / 8) / 2, "P(X = 2) = 3/8", 6, 4, PRACTICE, 10.5, "start", False, True)
p.arrow((2.25, 4 / 8 + 0.02), (2.25, 7 / 8 - 0.02), PRACTICE, 1.3, 6.0)
p.arrow((2.25, 7 / 8 - 0.02), (2.25, 4 / 8 + 0.02), PRACTICE, 1.3, 6.0)
OUT["dagilim-fonksiyonu-uc-para"] = figure(
    400, 256, [p],
    "Düzgün bir paranın üç kez atılmasında tura sayısı <em>X</em>'in dağılım fonksiyonu. Basamaklar "
    "0, 1, 2, 3 noktalarındadır; her basamağın yüksekliği o noktanın olasılığıdır (<em>P</em>(<em>X</em> = 2) = "
    "3/8). Fonksiyon sağdan süreklidir: her basamakta sağ uç dolu, sol uç boştur.",
    aria="Uc para atisindaki tura sayisinin basamakli dagilim fonksiyonu")

# ============================================================ dagilim-fonksiyonu-uc-tur
# Three kinds of distribution function on the same axes: discrete (steps), continuous
# (triangular, kinks but no jumps) and mixed (one jump at x = 1, then a ramp up to 1).
XR, YR = (-0.5, 3.5), (0.0, 1.15)


def F_tri(x):
    # triangular density on [0, 2]: f(x) = x on [0,1], 2 - x on [1,2]
    if x <= 0:
        return 0.0
    if x <= 1:
        return x * x / 2
    if x <= 2:
        return 1 - (2 - x) ** 2 / 2
    return 1.0


def F_mix(x):
    if x < 1:
        return 0.0
    if x <= 3:
        return 1 / 3 + (2 / 3) * (x - 1) / 2
    return 1.0


def quarters(v):
    k = round(v * 4)
    return {0: "0", 4: "1"}.get(k, "%d/4" % k)


def thirds(v):
    k = round(v * 3)
    return {0: "0", 3: "1"}.get(k, "%d/3" % k)


def make(x0, title):
    p = Plot(x0, 30, 140, 170, XR, YR)
    panel_title(p, title, THEORY)
    guide(p, [(XR[0], 1.0), (XR[1], 1.0)], TEXT, 0.35)
    return p


# --- discrete: jumps 1/4, 1/2, 1/4 at x = 0, 1, 2 ------------------------------
p1 = make(40, "kesikli")
p1.axes((0, 1, 2, 3), (1 / 4, 3 / 4, 1.0), "x", "F(x)", yfmt=quarters)
LEV = [(0, 0.0, 1 / 4), (1, 1 / 4, 3 / 4), (2, 3 / 4, 1.0)]
p1.line([(XR[0], 0), (0, 0)], THEORY, 2.2)
for x, lo, hi in LEV:
    nxt = x + 1 if x < 2 else XR[1]
    p1.line([(x, hi), (nxt, hi)], THEORY, 2.2)
    guide(p1, [(x, lo), (x, hi)], THEORY, 0.5)
    dot(p1, (x, hi), THEORY, 3.4)
    if x < 2:
        hollow(p1, (x + 1, hi), THEORY, 3.4, 1.5)
hollow(p1, (0, 0), THEORY, 3.4, 1.5)
p1.label(2.05, 0.5, "sıçramalar", 0, 0, PRACTICE, 10, "start", False, True)

# --- continuous: triangular distribution on [0, 2] ------------------------------
p2 = make(222, "sürekli")
p2.axes((0, 1, 2, 3), (1 / 2, 1.0), "x", "F(x)", yfmt=tfmt)
curve(p2, F_tri, XR[0], XR[1], THEORY, 2.2, 240)
dot(p2, (0, 0), THEORY, 2.6)
dot(p2, (2, 1), THEORY, 2.6)
p2.label(2.1, 0.5, "kırılma var,", 0, 0, PRACTICE, 10, "start", False, True)
p2.label(2.1, 0.5, "sıçrama yok", 0, 13, PRACTICE, 10, "start", False, True)

# --- mixed: jump of 1/3 at x = 1, then a ramp reaching 1 at x = 3 ---------------
p3 = make(404, "karma")
p3.axes((0, 1, 2, 3), (1 / 3, 1.0), "x", "F(x)", yfmt=thirds)
p3.line([(XR[0], 0), (1, 0)], THEORY, 2.2)
p3.line([(1, 1 / 3), (3, 1), (XR[1], 1)], THEORY, 2.2)
guide(p3, [(1, 0), (1, 1 / 3)], THEORY, 0.5)
hollow(p3, (1, 0), THEORY, 3.4, 1.5)
dot(p3, (1, 1 / 3), THEORY, 3.4)
p3.label(1.15, 0.2, "sıçrama", 0, 0, PRACTICE, 10, "start", False, True)
p3.label(1.15, 0.2, "1/3", 0, 13, PRACTICE, 10, "start", False, True)

OUT["dagilim-fonksiyonu-uc-tur"] = figure(
    570, 236, [p1, p2, p3],
    "Üç dağılım fonksiyonu türü. Kesikli türde <em>F</em> basamaklıdır ve olasılık sıçramalarda "
    "toplanır; sürekli türde <em>F</em> hiç sıçramaz, olasılık aralığa yayılır; karma türde hem "
    "sıçrama hem eğimli parça vardır. Üçü de aynı üç özelliği taşır: azalmayan, sağdan sürekli, "
    "uç limitleri 0 ve 1. Fark yalnızca sıçramaların varlığındadır.",
    css_class=WIDE,
    aria="Uc panelde kesikli, surekli ve karma dagilim fonksiyonlari: basamakli, S bicimli ve sicramali rampa")

# ============================================================ de-morgan-venn
# De Morgan: the complement of "A or B" is "not A and not B" -- the same region read two ways.
R_D, D_D = 0.9, 1.1           # circle radius and centre distance (they overlap)
RX_D, RY_D = 2.0, 1.3         # half-sides of the sample-space rectangle


def _arc_d(cx, cy, a0, a1, n=64):
    return [(cx + R_D * math.cos(a0 + (a1 - a0) * k / n), cy + R_D * math.sin(a0 + (a1 - a0) * k / n))
            for k in range(n + 1)]


def union_outline(xa, xb, y):
    """Boundary of A u B: arc of A outside B, then arc of B outside A."""
    th = math.acos((D_D / 2) / R_D)
    return _arc_d(xa, y, th, 2 * math.pi - th) + _arc_d(xb, y, math.pi + th, 3 * math.pi - th)


def holed(q, hole_pts, opacity):
    """Sample-space rectangle with a hole cut out (even-odd fill) = complement of the hole."""
    rect_pts = [(-RX_D, -RY_D), (RX_D, -RY_D), (RX_D, RY_D), (-RX_D, RY_D)]
    d = "M" + " L".join(q.P(x, yy) for x, yy in rect_pts) + " Z "
    d += "M" + " L".join(q.P(x, yy) for x, yy in hole_pts) + " Z"
    q.add('<path d="%s" fill="%s" fill-opacity="%.2f" fill-rule="evenodd" stroke="none"/>' % (d, THEORY, opacity))


PW_D, PH_D, XR_D = 236.0, 156.0, 2.15
YR_D = XR_D * PH_D / PW_D      # equal px-per-unit on both axes: circles stay circles


def dm_panel(px, title, mode):
    q = Plot(px, 42, PW_D, PH_D, (-XR_D, XR_D), (-YR_D, YR_D))
    xa, xb, y = -D_D / 2, D_D / 2, 0.0
    if mode == "birlesim":
        holed(q, union_outline(xa, xb, y), 0.34)            # outside A u B, in one stroke
    else:
        holed(q, _arc_d(xa, y, 0, 2 * math.pi), 0.19)       # A^c ...
        holed(q, _arc_d(xb, y, 0, 2 * math.pi), 0.19)       # ... and B^c: overlap comes out darker
    q.polygon([(-RX_D, -RY_D), (RX_D, -RY_D), (RX_D, RY_D), (-RX_D, RY_D)], TEXT, 0.0, TEXT, 1.0)
    q.circle(xa, y, R_D, TEXT, 1.4)
    q.circle(xb, y, R_D, TEXT, 1.4)
    q.label(xa - 0.3, 0.45, "A", 0, 0, TEXT, 12, "middle", True, True)
    q.label(xb + 0.3, 0.45, "B", 0, 0, TEXT, 12, "middle", True, True)
    q.text_px(q.X(RX_D) - 5, q.Y(RY_D) + 14, "&#937;", TEXT, 11, "end", False, True)
    panel_title(q, title, THEORY, 11.5)
    return q


p1 = dm_panel(28, "(A veya B) değil", "birlesim")
p2 = dm_panel(296, "A değil ve B değil", "kesisim")
# the shaded region, named beneath each panel
p1.text_px(p1.x0 + p1.w / 2, p1.y0 + p1.h + 19, "(A veya B)" + sups("c") + " : ne A ne B gerçekleşir",
           THEORY, 11, "middle", False, True)
p2.text_px(p2.x0 + p2.w / 2, p2.y0 + p2.h + 19, "A" + sups("c") + " &#8745; B" + sups("c")
           + " : A değil, aynı zamanda B değil", THEORY, 11, "middle", False, True)
p1.text_px(280, p1.y0 + p1.h / 2 + 5, "=", TEXT, 16, "middle", True)
# legend for the right panel: light = one complement, dark = both
p2.text_px(p2.x0 + p2.w / 2, p2.y0 + p2.h + 34, "iki tarama üst üste; koyu bölge ikisinin ortak kısmı",
           TEXT, 9.5, "middle")
p1.text_px(p1.x0 + p1.w / 2, p1.y0 + p1.h + 34, "tek tarama: birleşimin dışı",
           TEXT, 9.5, "middle")

OUT["de-morgan-venn"] = figure(
    560, 240, [p1, p2],
    "De Morgan kuralı (<em>A</em> &#8746; <em>B</em>)<sup>c</sup> = <em>A</em><sup>c</sup> &#8745; <em>B</em><sup>c</sup>. "
    "Solda birleşimin tümleyeni bir kerede taranmıştır: ne <em>A</em> ne <em>B</em> gerçekleşir. Sağda önce "
    "<em>A</em><sup>c</sup>, sonra <em>B</em><sup>c</sup> ayrı ayrı taranmış, iki taramanın üst üste geldiği koyu "
    "bölge ortaya çıkmıştır; bu bölge soldakiyle aynıdır. Kural, \"veya\"nın değilini \"ve\"nin değillerine "
    "çevirir; (<em>A</em> &#8745; <em>B</em>)<sup>c</sup> = <em>A</em><sup>c</sup> &#8746; <em>B</em><sup>c</sup> "
    "biçimi de aynı yolla okunur.",
    css_class=WIDE,
    aria="Iki Venn semasi: solda A birlesim B nin disi taranmis, sagda A tumleyeni ile B tumleyeni ust uste "
         "taranmis ve kesisimleri koyu; iki bolge ayni")

# ============================================================ deger-kumesi-turleri
# Three kinds of value set D_X on the same number line: finite, countably infinite, uncountable.
OMEGA, DOTS = "&#969;", "&#8230;"
DX = "D" + subs("X")
X0, X1 = -0.45, 4.75
p = Plot(12, 14, 376, 228, (-0.55, 4.9), (0, 3))


def number_line(y):
    p.arrow((X0, y), (X1, y), TEXT, 1.1, 6.5, opacity=0.6)
    for k in range(5):
        p.line([(k, y - 0.045), (k, y + 0.045)], TEXT, 1.0, None, 0.6)
        p.label(k, y, str(k), 0, 15, TEXT, 9.5, "middle", False, False)


ROWS = [2.5, 1.5, 0.5]
for y in ROWS:
    number_line(y)
# (1) finite: number of heads in three tosses
p.points([(k, ROWS[0]) for k in (0, 1, 2, 3)], THEORY, 4.0)
p.label(X0, ROWS[0], DX + " = {0, 1, 2, 3}", 0, -14, THEORY, 11, "start", True, True)
p.label(X1, ROWS[0], "sonlu: üç atışta tura sayısı", 0, -14, TEXT, 10.5, "end", False, True)
# (2) countably infinite: number of tosses until the first head
p.points([(k, ROWS[1]) for k in (1, 2, 3, 4)], THEORY, 4.0)
rect(p, 4.24, 4.62, ROWS[1] - 0.07, ROWS[1] + 0.07, BG, 1.0)
p.label(4.43, ROWS[1], DOTS, 0, 2, THEORY, 13, "middle", True, False)
p.label(X0, ROWS[1], DX + " = {1, 2, 3, " + DOTS + "}", 0, -14, THEORY, 11, "start", True, True)
p.label(X1, ROWS[1], "sayılabilir: ilk turaya kadar atış sayısı", 0, -14, TEXT, 10.5, "end", False, True)
# (3) uncountable: the interval [0, 1] as image of w^2 on [-1, 1]
p.line([(0, ROWS[2]), (1, ROWS[2])], THEORY, 5.0)
dot(p, (0, ROWS[2]), THEORY, 4.0)
dot(p, (1, ROWS[2]), THEORY, 4.0)
p.label(X0, ROWS[2], DX + " = [0, 1]", 0, -14, THEORY, 11, "start", True, True)
p.label(X1, ROWS[2], "sayılamaz: X(" + OMEGA + ") = " + OMEGA + sups("2") + ", &#937; = [" + MINUS_S + "1, 1]",
        0, -14, TEXT, 10.5, "end", False, True)
OUT["deger-kumesi-turleri"] = figure(
    400, 256, [p],
    "Üç rastgele değişkenin değer kümesi <em>D<sub>X</sub></em> aynı sayı doğrusunda. Üç para atışında tura sayısı "
    "sonlu bir küme, ilk turaya kadar yapılan atış sayısı sayılabilir sonsuz bir küme, [&#8722;1, 1] üzerinde "
    "&#969;<sup>2</sup> ise bir aralık verir. İlk iki tür kesikli rastgele değişkenlerin, üçüncüsü sürekli "
    "rastgele değişkenlerin örneğidir; <em>X</em> değer kümesinin dışında hiçbir değer almaz.",
    aria="Uc sayi dogrusu: sonlu kume 0 1 2 3, sayilabilir kume 1 2 3 ve devami, sayilamaz aralik 0 ile 1 arasi")

# ============================================================ dikdortgen-formulu
# Inclusion-exclusion picture of the rectangle formula
#   P(a < X <= b, c < Y <= d) = F(b,d) - F(a,d) - F(b,c) + F(a,c).
# Left: the plane with the target rectangle and the four quarter planes.
# Right: a sign table, one quarter plane per row.
A, B, C, D = 3.2, 7.2, 2.6, 6.6
NAMES = {A: "a", B: "b", C: "c", D: "d"}
XR, YR = (0.0, 9.6), (0.0, 9.0)


def hatch(p, x0, x1, y0, y1, color, slope=1, spacing=7.0, width=1.0, opacity=0.55):
    """Diagonal hatching clipped to the data rectangle [x0,x1] x [y0,y1]."""
    X0, X1, Y0, Y1 = p.X(x0), p.X(x1), p.Y(y1), p.Y(y0)
    step = spacing * math.sqrt(2)
    ks = [Y - slope * X for X in (X0, X1) for Y in (Y0, Y1)]
    k, segs = min(ks) + step / 2, []
    while k < max(ks):
        pts = []
        for X in (X0, X1):
            Y = slope * X + k
            if Y0 - 1e-6 <= Y <= Y1 + 1e-6:
                pts.append((X, Y))
        for Y in (Y0, Y1):
            X = (Y - k) / slope
            if X0 - 1e-6 <= X <= X1 + 1e-6:
                pts.append((X, Y))
        uniq = []
        for q in pts:
            if all(abs(q[0] - u[0]) > 1e-3 or abs(q[1] - u[1]) > 1e-3 for u in uniq):
                uniq.append(q)
        if len(uniq) >= 2:
            segs.append("M%.1f,%.1f L%.1f,%.1f" % (uniq[0][0], uniq[0][1], uniq[1][0], uniq[1][1]))
        k += step
    p.add('<path d="%s" fill="none" stroke="%s" stroke-width="%s" opacity="%s"/>'
          % (" ".join(segs), color, width, opacity))


def soft(p, px, py, s, size=9.5, anchor="start"):
    p.add('<text x="%.1f" y="%.1f" fill="%s" font-size="%s" text-anchor="%s" opacity="0.72">%s</text>'
          % (px, py, TEXT, size, anchor, s))


def tick_name(v):
    return NAMES[v]


# ---- left panel: the plane ------------------------------------------------
p = Plot(40, 26, 236, 190, XR, YR)
p.axes((A, B), (C, D), "x", "y", xfmt=tick_name, yfmt=tick_name)
# F(b,d): the quarter plane below and to the left of (b,d)
rect(p, XR[0], B, YR[0], D, THEORY, 0.10)
# F(a,d) and F(b,c): hatched strips; where they overlap, F(a,c) is cross-hatched
hatch(p, XR[0], A, YR[0], D, PRACTICE, slope=1)
hatch(p, XR[0], B, YR[0], C, PRACTICE, slope=-1)
# edges of the quarter planes
guide(p, [(XR[0], D), (B, D), (B, YR[0])], TEXT, 0.45)
guide(p, [(XR[0], C), (B, C)], TEXT, 0.45)
guide(p, [(A, YR[0]), (A, D)], TEXT, 0.45)
# the event itself
rect(p, A, B, C, D, THEORY, 0.34, THEORY, 1.5)
cx, cy = p.X((A + B) / 2), p.Y((C + D) / 2)
p.text_px(cx, cy - 3, "a &lt; X " + LEQ_S + " b", THEORY, 10.5, "middle", False, True)
p.text_px(cx, cy + 12, "c &lt; Y " + LEQ_S + " d", THEORY, 10.5, "middle", False, True)
# corners
for xy in ((A, C), (B, C), (A, D), (B, D)):
    dot(p, xy, TEXT, 2.8)
p.label(B, D, "F(b,d)", 6, -6, TEXT, 11.5, "start")
p.label(A, D, "F(a,d)", -6, -6, TEXT, 11.5, "end")
p.label(B, C, "F(b,c)", 6, 15, TEXT, 11.5, "start")
# F(a,c) sits on the cross-hatched corner: back it with the page colour
lx, ly = p.X(A) - 6, p.Y(C) + 15
p.add('<rect x="%.1f" y="%.1f" width="44" height="14" rx="2" fill="%s" opacity="0.9"/>'
      % (lx - 41, ly - 10.5, BG))
p.text_px(lx, ly, "F(a,c)", TEXT, 11.5, "end")


# ---- right column: sign table ---------------------------------------------
def sign_row(py, qx, qy, sign, name, note):
    col = THEORY if sign == "+" else PRACTICE
    q = Plot(298, py, 40, 32, XR, YR)
    # a plain L frame without the overshoot of axes(), so rows stay separate
    q.add('<path d="M298,%.1f L298,%.1f L338,%.1f" fill="none" stroke="%s" stroke-width="1.1" opacity="0.45"/>'
          % (py, py + 32, py + 32, TEXT))
    rect(q, XR[0], qx, YR[0], qy, col, 0.40)
    q.polygon([(A, C), (B, C), (B, D), (A, D)], TEXT, 0.0, TEXT, 0.9, "2 2")
    q.text_px(360, py + 21, sign, col, 15, "middle", True)
    q.text_px(372, py + 14, name, TEXT, 11.5)
    soft(q, 372, py + 28, note)
    return q


rows = [
    sign_row(30, B, D, "+", "F(b,d)", "X " + LEQ_S + " b, Y " + LEQ_S + " d"),
    sign_row(74, A, D, MINUS_S, "F(a,d)", "X " + LEQ_S + " a, Y " + LEQ_S + " d"),
    sign_row(118, B, C, MINUS_S, "F(b,c)", "X " + LEQ_S + " b, Y " + LEQ_S + " c"),
    sign_row(162, A, C, "+", "F(a,c)", "X " + LEQ_S + " a, Y " + LEQ_S + " c (iki kez çıkarıldı)"),
]
t = rows[0]
t.text_px(427, 17, "Terimlerin işaretleri", TEXT, 11.5, "middle", True)
t.add('<line x1="298" y1="206" x2="556" y2="206" stroke="%s" stroke-width="1" opacity="0.4"/>' % TEXT)
t.text_px(427, 222, "P(a &lt; X " + LEQ_S + " b, c &lt; Y " + LEQ_S + " d)", TEXT, 11.5, "middle")
t.text_px(427, 238, "= F(b,d) " + MINUS_S + " F(a,d) " + MINUS_S + " F(b,c) + F(a,c)", TEXT, 11.5, "middle")

OUT["dikdortgen-formulu"] = figure(
    560, 250, [p] + rows,
    "Dikdörtgen formülünün içerme–dışarma yorumu. Solda koyu taralı dikdörtgen "
    "(<em>a</em>, <em>b</em>] &#215; (<em>c</em>, <em>d</em>] olayıdır; <em>F</em>(<em>b</em>,<em>d</em>) bu dikdörtgeni "
    "içeren sol-alt çeyrek düzlemin olasılığıdır. Eğik taramalı şeritler <em>F</em>(<em>a</em>,<em>d</em>) ve "
    "<em>F</em>(<em>b</em>,<em>c</em>) bölgeleridir; ortak parçaları <em>F</em>(<em>a</em>,<em>c</em>) çapraz taralıdır ve "
    "iki kez çıkarıldığı için bir kez geri eklenir. Sağdaki tablo her terimin işaretini gösterir.",
    css_class=WIDE,
    aria="Dikdortgen formulunun icerme-disarma semasi: (a,b]x(c,d] dikdortgeni, dort ceyrek duzlem ve isaret tablosu")

# ============================================================ dogru-parcasi-oran
# A random point C on the segment AB of length k; the event |AC|/|BC| < a is the initial
# interval [0, ak/(1+a)). Drawn with a = 3/2 so the threshold sits at 0.6 k.
XC = 0.35          # position of C (in units of k) used for the sketch
XT = 0.6           # a k / (1 + a) for a = 3/2
A_VAL = 1.5

# ---- left panel: the segment and the event ---------------------------------
p1 = Plot(40, 30, 232, 190, (-0.12, 1.12), (-1.15, 1.05))
panel_title(p1, "AB üzerinde rastgele C noktası", TEXT)

# dimension lines for |AC| = x and |BC| = k - x
YD = 0.62
for xa, xb, s in ((0, XC, "|AC| = x"), (XC, 1, "|BC| = k " + MINUS_S + " x")):
    p1.line([(xa, YD), (xb, YD)], THEORY, 1.2)
    p1.line([(xa, YD - 0.07), (xa, YD + 0.07)], THEORY, 1.2)
    p1.line([(xb, YD - 0.07), (xb, YD + 0.07)], THEORY, 1.2)
    p1.label((xa + xb) / 2, YD, s, 0, -7, THEORY, 10.5, "middle", False, True)

# the event E = [0, ak/(1+a)) as a band and a heavy stroke, open at the right end
rect(p1, 0, XT, -0.1, 0.1, PRACTICE, 0.22)
p1.line([(0, 0), (1, 0)], TEXT, 1.6)
p1.line([(0, 0), (XT, 0)], PRACTICE, 3.2)
hollow(p1, (XT, 0), PRACTICE, 3.6, 1.6)

# the points A, C, B
for x, name in ((0, "A"), (XC, "C"), (1, "B")):
    dot(p1, (x, 0), TEXT, 3.6)
    p1.label(x, 0, name, 0, -12, TEXT, 11.5, "middle", True, True)
p1.label(0, 0, "0", 0, 19, TEXT, 10.5, "middle")
p1.label(XC, 0, "x", 0, 19, TEXT, 10.5, "middle", False, True)
p1.label(XT, 0, "ak/(1+a)", 0, 19, PRACTICE, 10.5, "middle", False, True)
p1.label(1, 0, "k", 0, 19, TEXT, 10.5, "middle", False, True)

# the answer
p1.label(0.5, -0.62, "E = {x : x/(k " + MINUS_S + " x) &lt; a} = [0, ak/(1+a))", 0, 0,
         PRACTICE, 10.5, "middle", False, True)
p1.label(0.5, -0.95, "P(E) = uzunluk(E)/k = a/(1+a)", 0, 0, PRACTICE, 11.5, "middle", True, True)

# ---- right panel: the ratio as a function of x ------------------------------
p2 = Plot(322, 30, 226, 190, (-0.1, 1.16), (-0.35, 4.3))
p2.origin_axes("x", "oran", opacity=0.5)
panel_title(p2, "oran |AC|/|BC| = x/(k " + MINUS_S + " x)", TEXT)

# vertical asymptote at x = k and the level a
guide(p2, [(1, 0), (1, 4.1)], TEXT, 0.45)
p2.label(1, 0, "k", 0, 15, TEXT, 10.5, "middle", False, True)
guide(p2, [(0, A_VAL), (XT, A_VAL)], PRACTICE, 0.8)
p2.label(0, A_VAL, "a", -6, 4, PRACTICE, 11, "end", True, True)
guide(p2, [(XT, 0), (XT, A_VAL)], PRACTICE, 0.8)

# the event on the x axis
rect(p2, 0, XT, -0.12, 0.12, PRACTICE, 0.22)
p2.line([(0, 0), (XT, 0)], PRACTICE, 3.2)
p2.label(XT, 0, "ak/(1+a)", 2, 15, PRACTICE, 10.5, "middle", False, True)

clipped(p2, lambda x: x / (1 - x), 0, 0.99, THEORY, 2.2, 400)
dot(p2, (XT, A_VAL), PRACTICE, 4.0)
p2.label(0.24, 1.0, "oran &lt; a", 0, 0, PRACTICE, 10.5, "middle", False, True)
p2.label(0.86, 1.05, "oran &gt; a", 0, 0, THEORY, 10.5, "middle", False, True)
p2.label(0.44, 3.65, "oran artar,", 0, 0, THEORY, 10, "middle", False, True)
p2.label(0.44, 3.2, "x " + ARROW + " k iken " + INF + "'a gider", 0, 0, THEORY, 10, "middle", False, True)

OUT["dogru-parcasi-oran"] = figure(
    560, 245, [p1, p2],
    "<em>k</em> uzunluğundaki <em>AB</em> doğru parçası üzerinde rastgele bir <em>C</em> noktası: konumu "
    "<em>x</em> = |<em>AC</em>| ile kodlanır ve [0, <em>k</em>] üzerinde düzgün dağılır. Solda, "
    "|<em>AC</em>|/|<em>BC</em>| &lt; <em>a</em> olayının tam olarak [0, <em>ak</em>/(1+<em>a</em>)) alt aralığı "
    "olduğu görülür; olasılığı uzunluk oranı <em>a</em>/(1+<em>a</em>)'dır ve <em>k</em>'ye bağlı değildir. "
    "Sağda oran fonksiyonu <em>x</em>/(<em>k</em>&#8722;<em>x</em>) çizilidir: sıfırdan başlayıp artarak "
    "sonsuza gittiğinden <em>a</em> düzeyinin altında kaldığı küme bir başlangıç aralığıdır.",
    css_class=WIDE,
    aria="AB dogru parcasi uzerinde C noktasi ve |AC| bolu |BC| orani a dan kucuk olayinin alt araligi; sagda oran fonksiyonunun grafigi")

# ============================================================ donusum-kare-iki-dal
# Y = X^2 for X uniform on (-2, 3): the two inverse branches and the resulting density.
p1 = Plot(44, 30, 226, 190, (-2.8, 3.6), (-1.1, 9.9))
p1.origin_axes("x", "y", xticks=(), yticks=(4, 9))
panel_title(p1, "y = x" + sups("2") + ", X düzgün (" + MINUS_S + "2, 3)", THEORY)
p1.line([(-2, -0.9), (3, -0.9)], PRACTICE, 4.0, None, 0.5)
p1.label(-2, -0.9, MINUS_S + "2", 0, 15, PRACTICE, 10.5, "middle", False, False)
p1.label(3, -0.9, "3", 0, 15, PRACTICE, 10.5, "middle", False, False)
curve(p1, lambda x: x * x, -2.45, 3.1, THEORY, 2.1, 240)
Y0 = 2.0
sq = math.sqrt(Y0)
guide(p1, [(-sq, 0), (-sq, Y0), (sq, Y0), (sq, 0)], BASE, 0.9, 1.4)
dot(p1, (-sq, Y0), BASE, 3.6)
dot(p1, (sq, Y0), BASE, 3.6)
p1.label(-sq, 0, MINUS_S + "&#8730;y", -6, -7, BASE, 10.5, "middle", False, True)
p1.label(sq, 0, "&#8730;y", 6, -7, BASE, 10.5, "middle", False, True)
p1.label(1.3, 6.4, "y &gt; 4: tek dal", 0, 0, THEORY, 10, "end", False, True)
p1.label(0, 3.0, "y &lt; 4: iki dal", 0, 0, BASE, 10, "middle", False, True)
guide(p1, [(-2.8, 4), (3.6, 4)], TEXT, 0.3)

p2 = Plot(322, 30, 226, 190, (-0.8, 9.9), (-0.06, 0.66))
p2.origin_axes("y", "f" + subs("Y") + "(y)", xticks=(4, 9), yticks=(0.2, 0.4), yfmt=tfmt)
panel_title(p2, "Y'nin yoğunluğu", THEORY)
clipped(p2, lambda y: 1 / (5 * math.sqrt(y)), 0.11, 4.0, BASE, 2.2, 300)
clipped(p2, lambda y: 1 / (10 * math.sqrt(y)), 4.0, 9.0, THEORY, 2.2, 300)
dot(p2, (4, 0.1), BASE, 3.4)
hollow(p2, (4, 0.05), THEORY, 3.4, 1.4)
p2.label(1.4, 1 / (5 * math.sqrt(1.4)), "1/(5&#8730;y)", 10, -2, BASE, 10.5, "start", False, True)
p2.label(6.5, 1 / (10 * math.sqrt(6.5)), "1/(10&#8730;y)", 0, -12, THEORY, 10.5, "middle", False, True)
OUT["donusum-kare-iki-dal"] = figure(
    560, 244, [p1, p2],
    "<em>X</em>, (&#8722;2, 3) üzerinde düzgün dağılırken <em>Y</em> = <em>X</em><sup>2</sup>'nin yoğunluğu. "
    "0 &lt; <em>y</em> &lt; 4 için hem &#8722;&#8730;<em>y</em> hem &#8730;<em>y</em> tanım aralığındadır: iki dal "
    "katkı verir ve yoğunluk 1/(5&#8730;<em>y</em>) olur. 4 &lt; <em>y</em> &lt; 9 için yalnızca &#8730;<em>y</em> "
    "kalır ve yoğunluk yarıya, 1/(10&#8730;<em>y</em>)'ye düşer; <em>y</em> = 4'te yoğunluk sıçrar.",
    aria="Parabol uzerinde iki ters dal ve Y=X kare icin iki parcali yogunluk egrisi")

# ============================================================ duzgun-dagilim-fonksiyonu
# Distribution function of the uniform distribution on [0, 1]: 0, then x, then 1.
# The point a = 0.6 shows F(a) = F(a-): a continuous F gives no mass to single points.
A = 0.6
p = Plot(48, 26, 306, 206, (-0.5, 2.3), (-0.16, 1.28))
p.origin_axes("x", "F(x)", xticks=(1,), yticks=(1,))
# guides: the level 1 and the corner at x = 1
guide(p, [(0, 1), (2.3, 1)], TEXT, 0.35)
guide(p, [(1, 0), (1, 1)], TEXT, 0.35)
# the distribution function, one polyline through its three pieces
p.line([(-0.55, 0), (0, 0), (1, 1), (2.25, 1)], THEORY, 2.2)
# names of the three pieces
p.label(-0.28, 0, "F(x) = 0", 0, -9, THEORY, 10.5, "middle", False, True)
p.label(0.10, 0.80, "F(x) = x", 0, 0, THEORY, 10.5, "start", False, True)
p.label(1.66, 1, "F(x) = 1", 0, -9, THEORY, 10.5, "middle", False, True)
# the point a and its reading F(a)
guide(p, [(A, 0), (A, A)], PRACTICE, 0.7)
guide(p, [(0, A), (A, A)], PRACTICE, 0.7)
dot(p, (A, A), PRACTICE, 4.2)
p.label(A, 0, "a", 0, 15, PRACTICE, 11, "middle", True, True)
p.label(0, A, "F(a)", -6, 4, PRACTICE, 10.5, "end", True, True)
# no jump at a: single points carry no probability
p.label(1.08, 0.45, "P({a}) = F(a) " + MINUS_S + " F(a" + sups("&#8722;") + ") = 0", 0, 0,
        PRACTICE, 10, "start", False, True)
p.label(1.08, 0.32, "sıçrama yok", 0, 0, PRACTICE, 10, "start", False, True)
OUT["duzgun-dagilim-fonksiyonu"] = figure(
    400, 255, [p],
    "[0, 1] üzerindeki düzgün dağılımın dağılım fonksiyonu: <em>x</em> &lt; 0 için 0, 0 &#8804; <em>x</em> &#8804; 1 "
    "için <em>x</em>, <em>x</em> &gt; 1 için 1. Fonksiyon azalmayan, sağdan sürekli ve limit koşullarını sağlayan bir "
    "dağılım fonksiyonudur; üstelik her yerde süreklidir. Bu yüzden <em>a</em> noktasında sıçrama yoktur: "
    "<em>P</em>({<em>a</em>}) = <em>F</em>(<em>a</em>) &#8722; <em>F</em>(<em>a</em><sup>&#8722;</sup>) = 0 ve bir "
    "aralığın olasılığı yalnızca uzunluğudur.",
    aria="Birim aralik uzerinde duzgun dagilimin dagilim fonksiyonu: sifir, sonra x, sonra bir; a noktasinda sicrama yok")

# ============================================================ duzgun-karakteristik-sinc
# Characteristic function of the uniform distribution on (-1, 1): sin t / t.
def sinc(t):
    return 1.0 if abs(t) < 1e-9 else math.sin(t) / t


p = Plot(48, 28, 306, 200, (-13.5, 13.5), (-0.38, 1.18))
p.origin_axes("t", "&#966;" + subs("X") + "(t)", xticks=(-4 * math.pi, -2 * math.pi, 2 * math.pi, 4 * math.pi),
              yticks=(0.5, 1.0), xfmt=lambda v: ("&#8722;" if v < 0 else "") + ("2&#960;" if abs(abs(v) - 2 * math.pi) < 0.1 else "4&#960;"),
              yfmt=tfmt)
guide(p, [(-13.5, 1), (13.5, 1)], TEXT, 0.3)
# envelopes +-1/t, kept inside the plotting window (1/t <= 1 above, -1/t >= -0.36 below)
curve(p, lambda t: 1 / t, 1.0, 13.4, PRACTICE, 1.0, 200, "4 3", 0.55)
curve(p, lambda t: -1 / t, 2.8, 13.4, PRACTICE, 1.0, 200, "4 3", 0.55)
curve(p, lambda t: -1 / t, -13.4, -1.0, PRACTICE, 1.0, 200, "4 3", 0.55)
curve(p, lambda t: 1 / t, -13.4, -2.8, PRACTICE, 1.0, 200, "4 3", 0.55)
curve(p, sinc, -13.4, 13.4, THEORY, 2.1, 600)
dot(p, (0, 1), THEORY, 4.0)
p.label(0, 1, "&#966;" + subs("X") + "(0) = 1", -9, -8, THEORY, 10.5, "end", False, True)
p.label(7.2, 1 / 7.2, "|&#966;" + subs("X") + "(t)| " + LEQ_S + " 1/|t|", 6, -6, PRACTICE, 10, "start", False, True)
p.label(5.3, -0.31, "sin t / t", 0, 0, THEORY, 11, "start", True, True)
OUT["duzgun-karakteristik-sinc"] = figure(
    400, 250, [p],
    "(&#8722;1, 1) üzerinde düzgün dağılımın karakteristik fonksiyonu &#966;<sub><em>X</em></sub>(<em>t</em>) = "
    "sin <em>t</em> / <em>t</em>. Sıfırda 1'e eşittir, her yerde mutlak değerce 1'i aşmaz ve sönümlü salınımla "
    "sıfıra gider; 2&#960;'nin katlarında sıfırlanır. Kesikli zarflar &#177;1/<em>t</em> sönümün hızını gösterir.",
    aria="sin t bolu t egrisi; sifirda 1, sonumlu salinim, arti eksi 1 bolu t zarflari")

# ============================================================ geometrik-hafizasizlik
# Memorylessness of Geo(p = 0.3): the tail beyond 3, divided by P(X > 3), is the original pmf shifted by 3.
P_G, Q_G = 0.3, 0.7
YMAX = 0.345
HW = 0.30                      # half bar width in data units
M = 3                          # the conditioning event is X > M
TAIL = Q_G ** M                # P(X > 3) = q^3 = 0.343

pl = Plot(44, 30, 226, 188, (0.3, 10.7), (0.0, YMAX))
pr = Plot(322, 30, 226, 188, (0.3 + M, 10.7 + M), (0.0, YMAX))
pl.axes((1, 2, 3, 4, 5, 6, 7, 8, 9, 10), (0.1, 0.2, 0.3), "x", "f(x)", yfmt=tfmt)
pr.axes((4, 5, 6, 7, 8, 9, 10, 11, 12, 13), (0.1, 0.2, 0.3), "x", "f(x | X &gt; 3)", yfmt=tfmt)
panel_title(pl, "Geo(p),  p = 0,3,  q = 0,7", THEORY)
panel_title(pr, "X &gt; 3 verildiğinde", PRACTICE)


def pmf(k):
    return Q_G ** (k - 1) * P_G


def bar(p, k, h, col, hatch=False):
    x0, x1, y0, y1 = p.X(k - HW), p.X(k + HW), p.Y(h), p.Y(0)
    w, hh = x1 - x0, y1 - y0
    p.add('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s"/>' % (x0, y0, w, hh, BG))
    p.add('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" fill-opacity="%s" stroke="%s" stroke-width="0.9"/>'
          % (x0, y0, w, hh, col, "0.22" if hatch else "0.55", col))
    if hatch:
        # diagonal hatching, clipped analytically to the bar
        step = 4.0
        c = x0 - y1
        while c < x1 - y0:
            # line x - y = c, restricted to [x0, x1] x [y0, y1]
            pts = []
            for x in (x0, x1):
                y = x - c
                if y0 <= y <= y1:
                    pts.append((x, y))
            for y in (y0, y1):
                x = y + c
                if x0 < x < x1:
                    pts.append((x, y))
            if len(pts) >= 2:
                (ax, ay), (bx, by) = pts[0], pts[-1]
                p.add('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="0.8" opacity="0.8"/>'
                      % (ax, ay, bx, by, col))
            c += step


# matching arrows (drawn first, so the bars sit on top of them)
for k in (1, 2, 3):
    h = pmf(k)
    xs, ys = pl.X(k + HW), pl.Y(h)
    xe = pr.X(k + M - HW)
    pl.add('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.1" stroke-dasharray="4 3" opacity="0.75"/>'
           % (xs, ys, xe - 5.5, ys, PRACTICE))
    pl.add('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s" opacity="0.9"/>'
           % (xe, ys, xe - 7, ys - 3, xe - 7, ys + 3, PRACTICE))

for k in range(1, 11):
    bar(pl, k, pmf(k), THEORY if k <= M else PRACTICE, hatch=(k > M))
for k in range(M + 1, M + 11):
    bar(pr, k, pmf(k) / TAIL, PRACTICE)

pl.label(7.8, 0.118, "taralı kuyruk:", 0, 0, PRACTICE, 10.5, "middle", False, True)
pl.label(7.8, 0.090, "P(X &gt; 3) = q" + sups("3") + " = 0,343", 0, 0, PRACTICE, 10.5, "middle", False, True)
pr.label(10.3, 0.255, "kuyruk, P(X &gt; 3)'e bölündü:", 0, 0, PRACTICE, 10.5, "middle", False, True)
pr.label(10.3, 0.225, "x = 3 + n çubuğu, soldaki x = n ile aynı", 0, 0, TEXT, 10, "middle", False, True)
pr.label(10.3, 0.165, "P(X &gt; 3 + n | X &gt; 3) = P(X &gt; n)", 0, 0, PRACTICE, 10.5, "middle", False, True)

OUT["geometrik-hafizasizlik"] = figure(
    560, 245, [pl, pr],
    "Geometrik dağılımın hafızasızlığı (<em>p</em> = 0,3). Solda <em>X</em> &gt; 3 kuyruğu taralıdır ve "
    "toplam olasılığı <em>q</em><sup>3</sup> = 0,343'tür. Sağda bu kuyruk <em>P</em>(<em>X</em> &gt; 3)'e "
    "bölünerek koşullu dağılıma dönüştürülmüştür: <em>x</em> = 4, 5, 6, &#8230; çubukları soldaki "
    "<em>x</em> = 1, 2, 3, &#8230; çubuklarıyla tam aynı yüksekliktedir. Üç başarısızlıktan sonra kalan bekleme "
    "süresi, en baştaki bekleme süresiyle aynı dağılıma sahiptir; kesikli oklar bu eşlemeyi gösterir.",
    css_class=WIDE,
    aria="Geometrik dagilim p = 0,3: solda X buyuk 3 kuyrugu tarali, sagda kosullu dagilim ayni cubuk yukseklikleriyle")

# ============================================================ geometrik-olasilik-carpim
# Geometric probability: two numbers from (0,1), probability that their product is below 1/2.
p = Plot(56, 22, 214, 214, (-0.12, 1.22), (-0.12, 1.22))
p.origin_axes("x", "y", xticks=(0.5, 1), yticks=(0.5, 1), xfmt=tfmt, yfmt=tfmt)
# the sample space: unit square
p.polygon([(0, 0), (1, 0), (1, 1), (0, 1)], TEXT, 0.0, TEXT, 1.0)
# the event xy < 1/2
region = [(0, 0), (0.5, 0)] + [(0.5 + 0.5 * k / 150, 1 / (2 * (0.5 + 0.5 * k / 150))) for k in range(151)]
region = [(0, 0), (1, 0)] + [(1 - 0.5 * k / 150, 1 / (2 * (1 - 0.5 * k / 150))) for k in range(151)] + [(0.5, 1), (0, 1)]
p.polygon(region, THEORY, 0.22)
curve(p, lambda x: 1 / (2 * x), 0.5, 1.0, THEORY, 2.0, 200)
p.line([(0.5, 1.0), (0.5, 1.0)], THEORY, 1.0)
p.label(0.33, 0.45, "xy &lt; 1/2", 0, 0, THEORY, 11.5, "middle", True, True)
p.label(0.86, 0.86, "xy &gt; 1/2", 0, 0, PRACTICE, 10.5, "middle", False, True)
p.label(1.0, 0.5, "y = 1/(2x)", 8, 4, THEORY, 10.5, "start", False, True)
p.text_px(p.x0 + p.w + 40, p.y0 + 70, "P = 1/2 + (1/2) ln 2", THEORY, 12, "start", True, True)
APPROX_S = "&#8776;"
p.text_px(p.x0 + p.w + 40, p.y0 + 92, APPROX_S + " 0,847", THEORY, 11.5, "start", False, True)
p.text_px(p.x0 + p.w + 40, p.y0 + 130, "taranan alan / kare alanı", TEXT, 10.5, "start", False, True)
OUT["geometrik-olasilik-carpim"] = figure(
    400, 250, [p],
    "(0, 1) aralığından rastgele seçilen iki sayının çarpımının 1/2'den küçük olması olayı. Örnek uzay birim "
    "karedir; olay, <em>y</em> = 1/(2<em>x</em>) hiperbolünün altında kalan bölgedir. Olasılık, alanların "
    "oranıdır: 1/2 + (1/2) ln 2 &#8776; 0,847.",
    aria="Birim karede carpimi yarimdan kucuk olan bolge taranmis; sinir egrisi y = 1 bolu 2x hiperbolu")

# ============================================================ geometrik-olasilik-fonksiyonu
# Geometric distribution (trials until the first success), p = 0.3, with the memoryless tail.
P_G = 0.3
p = Plot(48, 28, 306, 204, (0.2, 13.8), (0.0, 0.36))
p.axes((1, 3, 5, 7, 9, 11, 13), (0.1, 0.2, 0.3), "x", "f(x)", yfmt=tfmt)
for k in range(1, 14):
    h = (1 - P_G) ** (k - 1) * P_G
    col = PRACTICE if k > 5 else THEORY
    p.add('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" fill-opacity="0.55" stroke="%s" stroke-width="0.9"/>'
          % (p.X(k - 0.38), p.Y(h), p.X(k + 0.38) - p.X(k - 0.38), p.Y(0) - p.Y(h), col, col))
p.label(1, P_G, "f(x) = (1 " + MINUS_S + " p)" + sups("x" + MINUS_S + "1") + " p,   p = 0,3", 14, -4, THEORY, 10.5, "start", False, True)
p.label(9.0, 0.16, "P(X &gt; 5) = (1 " + MINUS_S + " p)" + sups("5") + " " + "&#8776;" + " 0,168", 0, 0, PRACTICE, 10.5, "middle", False, True)
p.label(9.0, 0.115, "kuyruk, başlangıçla aynı biçimde", 0, 0, PRACTICE, 10, "middle", False, True)
OUT["geometrik-olasilik-fonksiyonu"] = figure(
    400, 252, [p],
    "İlk başarıya kadar yapılan deneme sayısının (geometrik dağılım, <em>p</em> = 0,3) olasılık fonksiyonu. "
    "Çubuklar sabit oranla (1 &#8722; <em>p</em>) küçülür; bu yüzden 5. denemeden sonraki kuyruk (turuncu), "
    "baştan başlayan dağılımın küçültülmüş kopyasıdır. Hafızasızlık özelliği tam olarak budur: ilk beş "
    "deneme başarısızsa, kalan bekleme yine geometriktir.",
    aria="Geometrik dagilimin olasilik fonksiyonu; besinci denemeden sonraki kuyruk farkli renkte")

# ============================================================ hipergeometrik-binom
# Hypergeometric HG(N, M, n) versus binomial B(n, M/N) for small and large N.
def hg_pmf(N, M, n, x):
    return math.comb(M, x) * math.comb(N - M, n - x) / math.comb(N, n)


def binom_pmf(n, p, k):
    return math.comb(n, k) * p ** k * (1 - p) ** (n - k)


N_S = 5
panels = []
for i, (NN, MM) in enumerate(((20, 8), (200, 80))):
    q = Plot(44 + i * 278, 30, 226, 190, (-0.7, 5.7), (0.0, 0.46))
    q.axes((0, 1, 2, 3, 4, 5), (0.1, 0.2, 0.3, 0.4), "x", "", yfmt=tfmt)
    panel_title(q, "N = %d, M = %d, n = %d" % (NN, MM, N_S), TEXT)
    pp = MM / NN
    for k in range(N_S + 1):
        h = hg_pmf(NN, MM, N_S, k)
        b = binom_pmf(N_S, pp, k)
        q.add('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" fill-opacity="0.55" stroke="%s" stroke-width="0.9"/>'
              % (q.X(k - 0.40), q.Y(h), q.X(k + 0.10) - q.X(k - 0.40), q.Y(0) - q.Y(h), THEORY, THEORY))
        q.add('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" fill-opacity="0.75" stroke="%s" stroke-width="0.9"/>'
              % (q.X(k + 0.14), q.Y(b), q.X(k + 0.40) - q.X(k + 0.14), q.Y(0) - q.Y(b), PRACTICE, PRACTICE))
    # legend
    lx = 3.55
    q.add('<rect x="%.1f" y="%.1f" width="11" height="9" fill="%s" fill-opacity="0.55" stroke="%s" stroke-width="0.9"/>'
          % (q.X(lx) - 16, q.Y(0.425) - 4.5, THEORY, THEORY))
    q.label(lx, 0.425, "HG(%d, %d, %d)" % (NN, MM, N_S), 0, 4, THEORY, 10, "start")
    q.add('<rect x="%.1f" y="%.1f" width="6" height="9" fill="%s" fill-opacity="0.75" stroke="%s" stroke-width="0.9"/>'
          % (q.X(lx) - 13.5, q.Y(0.375) - 4.5, PRACTICE, PRACTICE))
    q.label(lx, 0.375, "B(5; " + tfmt(pp) + ")", 0, 4, PRACTICE, 10, "start")
    panels.append(q)
OUT["hipergeometrik-binom"] = figure(
    560, 245, panels,
    "İadesiz çekilişte başarı sayısının hipergeometrik dağılımı (geniş mavi çubuk) ile aynı <em>n</em> ve "
    "<em>p</em> = <em>M</em>/<em>N</em> için binom dağılımı (ince turuncu çubuk). Solda kitle küçükken "
    "(<em>n</em>/<em>N</em> = 0,25) hipergeometrik daha sivri: iadesiz çekiliş varyansı küçültür. Sağda kitle on "
    "kat büyüyünce (<em>n</em>/<em>N</em> = 0,025) çubuklar neredeyse çakışır; <em>N</em> &#8594; &#8734; iken "
    "hipergeometrik dağılım binom dağılımına yaklaşır.",
    css_class=WIDE,
    aria="N=20 ve N=200 icin hipergeometrik ve binom olasilik cubuklarinin karsilastirilmasi")

# ============================================================ icerme-disarma-uc-olay
# Inclusion-exclusion for three events: a three-circle Venn diagram inside the sample space.
# Each of the seven pieces carries the number of times it is counted in P(A) + P(B) + P(C);
# the notes on the right show how the alternating sum brings every count back to exactly 1.
R_C = 1.0                                       # common radius of the three circles
CA, CB, CC = (-0.6, 0.45), (0.6, 0.45), (0.0, -0.55)   # centres (pairwise distance about 1.2)
RX, RY = 2.15, 1.64                             # half-sides of the sample-space rectangle
PID = "icdis-h"                                 # id of the hatch pattern

p = Plot(12, 10, 288, 230.4, (-2.3, 2.3), (-1.84, 1.84))   # equal aspect: 62.6 px per unit


def inside(pt, c):
    return (pt[0] - c[0]) ** 2 + (pt[1] - c[1]) ** 2 <= R_C * R_C + 1e-9


def triple_pts(n=720):
    """Boundary of A n B n C: the boundary points of each circle that lie inside the other two."""
    pts = []
    for c, others in ((CA, (CB, CC)), (CB, (CA, CC)), (CC, (CA, CB))):
        for k in range(n):
            a = 2 * math.pi * k / n
            q = (c[0] + R_C * math.cos(a), c[1] + R_C * math.sin(a))
            if all(inside(q, o) for o in others):
                pts.append(q)
    gx = sum(q[0] for q in pts) / len(pts)
    gy = sum(q[1] for q in pts) / len(pts)
    pts.sort(key=lambda q: math.atan2(q[1] - gy, q[0] - gx))
    return pts


# hatch used for the triple intersection
p.add('<defs>'
      f'<pattern id="{PID}" patternUnits="userSpaceOnUse" width="5" height="5" patternTransform="rotate(45)">'
      f'<line x1="2.5" y1="0" x2="2.5" y2="5" stroke="{TEXT}" stroke-width="1.1" opacity="0.7"/></pattern>'
      '</defs>')

# the sample space
p.polygon([(-RX, -RY), (RX, -RY), (RX, RY), (-RX, RY)], TEXT, 0.0, TEXT, 1.0)

# the three events as light tints, so that the overlaps come out darker
for c, col in ((CA, THEORY), (CB, PRACTICE), (CC, BASE)):
    p.polygon(circle_pts(c[0], c[1], R_C), col, 0.15)
    p.circle(c[0], c[1], R_C, col, 1.7)

# the triple intersection, hatched
p.polygon(triple_pts(), f"url(#{PID})", 1.0)

# names of the events, just outside their circles
p.label(CA[0] - 0.72, CA[1] + 0.72, "A", -3, 2, THEORY, 12.5, "middle", True, True)
p.label(CB[0] + 0.72, CB[1] + 0.72, "B", 3, 2, PRACTICE, 12.5, "middle", True, True)
p.label(CC[0] + 0.72, CC[1] - 0.72, "C", 3, 8, BASE, 12.5, "middle", True, True)
p.text_px(p.X(-RX) + 6, p.Y(RY) + 15, "&#937;", TEXT, 12, "start", False, True)


def count(x, y, s, halo=False):
    """How many times the piece is counted in P(A) + P(B) + P(C)."""
    if halo:
        px, py = p.X(x), p.Y(y) + 4.5
        common = 'x="%.1f" y="%.1f" font-size="13" font-weight="700" text-anchor="middle"' % (px, py)
        p.add('<text %s fill="%s" stroke="%s" stroke-width="5" stroke-linejoin="round">%s</text>' % (common, BG, BG, s))
        p.add('<text %s fill="%s">%s</text>' % (common, TEXT, s))
    else:
        p.label(x, y, s, 0, 4.5, TEXT, 13, "middle", True)


count(-1.05, 0.72, "1")           # only A
count(1.05, 0.72, "1")            # only B
count(0.0, -1.05, "1")            # only C
count(0.0, 0.86, "2")             # A n B, not C
count(-0.62, -0.24, "2")          # A n C, not B
count(0.62, -0.24, "2")           # B n C, not A
count(0.0, 0.11, "3", halo=True)  # A n B n C
p.text_px(p.X(0), p.Y(-RY) + 12, "sayılar: P(A) + P(B) + P(C)'de kaç kez sayıldığı", TEXT, 9.5, "middle", False, True)

# the formula, term by term, and the bookkeeping for each kind of piece
NX = 318
CAP = "&#8745;"
p.text_px(NX, 34, "P(A veya B veya C) =", TEXT, 12, "start", True)
p.text_px(NX + 8, 56, "+ P(A) + P(B) + P(C)", TEXT, 11.5, "start")
p.text_px(NX + 8, 76, MINUS_S + " P(A " + CAP + " B) " + MINUS_S + " P(A " + CAP + " C) " + MINUS_S + " P(B " + CAP + " C)",
          TEXT, 11.5, "start")
p.text_px(NX + 8, 96, "+ P(A " + CAP + " B " + CAP + " C)", TEXT, 11.5, "start")

p.text_px(NX, 130, "her bölge tam bir kez sayılır:", TEXT, 11, "start", False, True)
p.text_px(NX + 14, 152, "tek olayda:   1 " + MINUS_S + " 0 + 0 = 1 kez", PRACTICE, 11.5, "start")
p.text_px(NX + 14, 174, "iki olayda:   2 " + MINUS_S + " 1 + 0 = 1 kez", PRACTICE, 11.5, "start")
p.text_px(NX + 14, 196, "üç olayda:   3 " + MINUS_S + " 3 + 1 = 1 kez", PRACTICE, 11.5, "start", True)
p.add(f'<rect x="{NX - 3}" y="186" width="12" height="11" fill="url(#{PID})" stroke="{TEXT}" stroke-width="0.7"/>')
p.text_px(NX + 8, 218, "(taralı bölge üç ikili kesişimde de çıkarılır,", TEXT, 9.5, "start", False, True)
p.text_px(NX + 8, 232, "üçlü kesişimde bir kez geri eklenir)", TEXT, 9.5, "start", False, True)

OUT["icerme-disarma-uc-olay"] = figure(
    560, 250, [p],
    "Üç olay için içerme–dışarma formülünün Venn şeması. Örnek uzay &#937; içindeki <em>A</em>, <em>B</em>, "
    "<em>C</em> daireleri yedi ayrık bölge oluşturur; her bölgedeki sayı, o bölgenin "
    "<em>P</em>(<em>A</em>) + <em>P</em>(<em>B</em>) + <em>P</em>(<em>C</em>) toplamında kaç kez sayıldığını gösterir. "
    "İkili kesişimler çıkarılınca iki olaya ait bölgeler 2 &#8722; 1 = 1 kez, ortadaki taralı bölge ise "
    "3 &#8722; 3 = 0 kez sayılmış olur; üçlü kesişim geri eklenince o da 1'e tamamlanır. Böylece formül, "
    "birleşimin her parçasını tam bir kez sayar.",
    css_class=WIDE,
    aria="Dikdortgen ornek uzay icinde kesisen A B C daireleri; yedi bolgede 1 2 ve 3 sayilari; sagda icerme disarma formulunun terimleri ve her bolgenin bir kez sayildigini gosteren hesap")

# ============================================================ iki-nokta-yakinlik
# Two random points on a segment, scaled to the unit square: (u, v) with u = |AL|/k, v = |AM|/k.
# The event "L is closer to M than to A" is |u - v| < u, i.e. v < 2u; its complement is the
# triangle with corners (0,0), (0,1), (1/2,1) of area 1/4, so P(E) = 3/4.
p = Plot(56, 22, 214, 214, (-0.12, 1.22), (-0.12, 1.22))     # equal aspect
p.origin_axes("u", "v", xticks=(0.5, 1), yticks=(1,), xfmt=tfmt)
# the sample space: unit square
p.polygon([(0, 0), (1, 0), (1, 1), (0, 1)], TEXT, 0.0, TEXT, 1.0)
# the event E = {v < 2u}: the square minus the corner triangle
p.polygon([(0, 0), (1, 0), (1, 1), (0.5, 1)], THEORY, 0.22)
# the complement triangle, left bare, and its boundary line v = 2u
p.line([(0, 0), (0.5, 1)], THEORY, 2.0)
p.label(0.62, 0.40, "E: v &lt; 2u", 0, 0, THEORY, 11.5, "middle", True, True)
p.label(0.16, 0.80, "E" + sups("c"), 0, 0, PRACTICE, 11, "middle", True, True)
p.label(0.40, 0.72, "v = 2u", 6, 4, THEORY, 10.5, "start", False, True)
# corners of the triangle and its two legs
dot(p, (0.5, 1), PRACTICE, 3.4)
p.label(0.5, 1, "(1/2, 1)", 8, -7, PRACTICE, 10, "start", False, True)
p.label(0.25, 1, "1/2", 0, -8, PRACTICE, 10, "middle", False, True)
# the numbers, on the right
RX = p.x0 + p.w + 30
p.text_px(RX, p.y0 + 62, "alan(E" + sups("c") + ") = 1/2 &#183; 1/2 &#183; 1 = 1/4", PRACTICE, 10.5, "start", False, True)
p.text_px(RX, p.y0 + 96, "P(E) = 1 " + MINUS_S + " 1/4 = 3/4", THEORY, 12, "start", True, True)
p.text_px(RX, p.y0 + 132, "olasılık = taranan alan", TEXT, 10.5, "start", False, True)
p.text_px(RX, p.y0 + 148, "(kare alanı 1)", TEXT, 10.5, "start", False, True)
OUT["iki-nokta-yakinlik"] = figure(
    400, 250, [p],
    "Bir doğru parçası üzerinde rastgele seçilen iki nokta için ölçekli sonuç uzayı: birim kare, olasılık ölçüsü alan. "
    "<em>L</em>'nin <em>M</em>'ye <em>A</em>'dan daha yakın olması olayı |<em>u</em> &#8722; <em>v</em>| &lt; <em>u</em>, "
    "yani <em>v</em> &lt; 2<em>u</em> bölgesidir (taralı). Tümleyeni, köşeleri (0, 0), (0, 1) ve (1/2, 1) olan "
    "üçgendir; alanı 1/4 olduğundan aranan olasılık 3/4'tür ve parçanın uzunluğundan bağımsızdır.",
    aria="Birim karede v kucuktur 2u bolgesi taranmis; sol ust kose ucgeni tumleyen, alani 1/4, olasilik 3/4")

# ============================================================ iki-olay-venn
# Two overlapping events inside the sample space: the four disjoint pieces and their probabilities
# (P(A) = 0.6, P(B) = 0.5, P(A n B) = 0.3 from the worked example).
R_C, D_C = 1.0, 1.2            # circle radius and distance between the centres (they overlap)
RX, RY = 2.6, 1.45             # half-sides of the sample-space rectangle


def _disk(cx, cy, n=96):
    return [(cx + R_C * math.cos(2 * math.pi * k / n), cy + R_C * math.sin(2 * math.pi * k / n))
            for k in range(n)]


p = Plot(22, 14, 356, 200, (-2.67, 2.67), (-1.5, 1.5))   # equal aspect: 66.7 px per unit
SHIFT = -0.12                  # nudge the pair left so the outer label has room on the right
XA, XB = -D_C / 2 + SHIFT, D_C / 2 + SHIFT

# the sample space
p.polygon([(-RX, -RY), (RX, -RY), (RX, RY), (-RX, RY)], TEXT, 0.0, TEXT, 1.0)
# the two events, tinted so that the four pieces come out in four different tones
p.polygon(_disk(XA, 0), THEORY, 0.16)
p.polygon(_disk(XB, 0), PRACTICE, 0.16)
p.circle(XA, 0, R_C, THEORY, 1.6)
p.circle(XB, 0, R_C, PRACTICE, 1.6)

# names of the events, just outside the circles, and of the sample space
p.label(XA - 0.85, 0.85, "A", 0, 4, THEORY, 12.5, "middle", True, True)
p.label(XB + 0.85, 0.85, "B", 0, 4, PRACTICE, 12.5, "middle", True, True)
p.text_px(p.X(RX) - 6, p.Y(RY) + 15, "&#937;", TEXT, 12, "end", False, True)


def piece(x, prob, name):
    """Probability of a piece, with the piece's name beneath it."""
    p.label(x, 0, prob, 0, -2, TEXT, 13, "middle", True)
    p.label(x, 0, name, 0, 13, TEXT, 9.5, "middle")


piece(XA - 0.42, "0,3", "yalnız A")
piece((XA + XB) / 2, "0,3", "A &#8745; B")
piece(XB + 0.42, "0,2", "yalnız B")
piece((XB + R_C + RX) / 2, "0,2", "ne A ne B")

# the four pieces exhaust the sample space
p.text_px(p.x0 + p.w / 2, 233, "P(&#937;) = 0,3 + 0,3 + 0,2 + 0,2 = 1", TEXT, 11.5, "middle")

OUT["iki-olay-venn"] = figure(
    400, 246, [p],
    "<em>P</em>(<em>A</em>) = 0,6, <em>P</em>(<em>B</em>) = 0,5, <em>P</em>(<em>A</em> &#8745; <em>B</em>) = 0,3 olan "
    "iki olayın Venn şeması. Dikdörtgen örnek uzay &#937;'yı gösterir ve dört ayrık parçaya ayrılır: "
    "yalnız <em>A</em> (<em>A</em> &#8726; <em>B</em>), hem <em>A</em> hem <em>B</em> (<em>A</em> &#8745; <em>B</em>), "
    "yalnız <em>B</em> (<em>B</em> &#8726; <em>A</em>) ve ikisi de değil (<em>A</em><sup>c</sup> &#8745; <em>B</em><sup>c</sup>). "
    "Parçaların olasılıkları 0,3; 0,3; 0,2 ve 0,2'dir; toplamları 1 = <em>P</em>(&#937;) eder. Örnekteki her soru, "
    "bu dört sayıdan uygun olanları toplayarak yanıtlanır.",
    aria="Dikdortgen ornek uzay icinde kesisen A ve B daireleri; dort ayrik parcanin olasiliklari 0,3 0,3 0,2 ve 0,2")

# ============================================================ kare-eksi-bir-iki-dagilim
# Distribution function of X = omega^2 on Omega = [-1, 2] with uniform P: two curved pieces
# glued continuously at x = 1, where only the slope changes.
def F1(x):
    return 2 * math.sqrt(x) / 3


def F2(x):
    return (1 + math.sqrt(x)) / 3


def thirds(v):
    return {0: "0", 2: "2/3", 3: "1"}[round(v * 3)]


SQRT = "&#8730;"
p = Plot(50, 26, 304, 206, (-0.5, 4.5), (-0.08, 1.12))
p.axes((0, 1, 4), (2 / 3, 1.0), "x", "F" + subs("X") + "(x)", yfmt=thirds)
guide(p, [(-0.5, 1.0), (4.5, 1.0)], TEXT, 0.35)
# flat pieces
p.line([(-0.5, 0), (0, 0)], TEXT, 2.0, None, 0.7)
p.line([(4, 1), (4.5, 1)], TEXT, 2.0, None, 0.7)
# curved pieces
curve(p, F1, 0, 1, THEORY, 2.3, 200)
curve(p, F2, 1, 4, BASE, 2.3, 200)
# the kink at x = 1
guide(p, [(1, 0), (1, 2 / 3)], TEXT, 0.45)
guide(p, [(-0.5, 2 / 3), (1, 2 / 3)], TEXT, 0.45)
dot(p, (1, 2 / 3), TEXT, 4.2)
p.label(1, 2 / 3, "F(1) = 2/3", 9, 15, TEXT, 11, "start", True, True)
p.label(1, 2 / 3, "sürekli: sıçrama yok, eğim değişir", 9, 30, TEXT, 10, "start", False, True)
p.label(0.12, 0.88, "F(x) = 2" + SQRT + "x / 3", 0, 0, THEORY, 11, "start", False, True)
p.label(3.15, 0.56, "F(x) = (1 + " + SQRT + "x) / 3", 0, 0, BASE, 11, "middle", False, True)
OUT["kare-eksi-bir-iki-dagilim"] = figure(
    400, 256, [p],
    "&#937; = [&#8722;1, 2] üzerinde <em>X</em>(&#969;) = &#969;<sup>2</sup>'nin dağılım fonksiyonu. "
    "0 &#8804; <em>x</em> &lt; 1 iken (<em>X</em> &#8804; <em>x</em>) olayı iki uçtan birden büyür ve "
    "<em>F</em> hızla yükselir; <em>x</em> &#8805; 1'den sonra sol uç &#8722;1'e takılır, olay yalnızca sağ "
    "uçtan büyür ve <em>F</em> yavaşlar. İki parça <em>x</em> = 1'de aynı değeri (2/3) verir: fonksiyon "
    "süreklidir, değişen yalnızca eğimdir.",
    aria="Omega ustunde omega kare degiskeninin dagilim fonksiyonu; x=1 noktasinda surekli ama egimi degisen iki egri parcasi")

# ============================================================ kare-onimaj-iki-durum
# X(w) = w^2 on Omega = [-1, 2]: the event (X <= x) is [-sqrt(x), sqrt(x)] cut down to Omega.
# Two regimes: for x < 1 the whole interval fits; for x >= 1 the left end is stuck at -1.
import math

OMEGA = "&#969;"
SQ = "&#8730;x"
XR, YR = (-1.45, 2.45), (-0.55, 4.5)


def sq(w):
    return w * w


def panel(x0, title, level, note):
    p = Plot(x0, 28, 226, 192, XR, YR)
    p.origin_axes(OMEGA, "X(" + OMEGA + ")", xticks=(-1, 2), yticks=(1, 4),
                  xfmt=lambda t: fmt(t).replace("-", MINUS_S))
    panel_title(p, title, THEORY)
    r = math.sqrt(level)
    lo, hi = max(-1.0, -r), r
    # Omega on the axis, with its name
    p.line([(-1, 0), (2, 0)], TEXT, 3.2, None, 0.8)
    p.label(1.0, 0, "&#937; = [" + MINUS_S + "1, 2]", 0, 16, TEXT, 10.5, "middle", False, True)
    # the event and the region below the level
    rect(p, lo, hi, 0, level, PRACTICE, 0.12)
    p.line([(lo, 0), (hi, 0)], PRACTICE, 7, None, 0.6)
    curve(p, sq, -1, 2, THEORY, 2.2, 160)
    guide(p, [(max(XR[0], -r), level), (r, level)], PRACTICE, 0.8)
    guide(p, [(r, 0), (r, level)], PRACTICE, 0.8)
    dot(p, (r, level), PRACTICE, 3.4)
    p.label(0, level, "x", -6, -5, PRACTICE, 11.5, "end", True, True)
    p.label(r, 0, SQ, 4, -6, PRACTICE, 11, "start", True, True)
    p.text_px(p.x0 + p.w / 2 + 8, 237, note, PRACTICE, 10.5, "middle", False, True)
    return p, r


# left: 0 <= x < 1, the whole interval [-sqrt(x), sqrt(x)] lies inside Omega
p1, r1 = panel(44, "0 " + LEQ_S + " x &lt; 1", 0.5,
               "uzunluk 2" + SQ + "  " + ARROW + "  F(x) = 2" + SQ + "/3")
guide(p1, [(-r1, 0), (-r1, 0.5)], PRACTICE, 0.8)
dot(p1, (-r1, 0.5), PRACTICE, 3.4)
p1.label(-r1, 0, MINUS_S + SQ, -4, -6, PRACTICE, 11, "end", True, True)

# right: 1 <= x < 4, the left end -sqrt(x) falls outside Omega; the event starts at -1
p2, r2 = panel(322, "1 " + LEQ_S + " x &lt; 4", 2.5,
               "uzunluk 1 + " + SQ + "  " + ARROW + "  F(x) = (1 + " + SQ + ")/3")
p2.line([(XR[0] + 0.02 + 0.03 * k, sq(XR[0] + 0.02 + 0.03 * k)) for k in range(15)], THEORY, 1.4, "2 3", 0.45)
p2.line([(-1, 0), (-1, 2.5)], TEXT, 1.4)
p2.label(-1, 2.05, "&#937; burada", 5, 0, TEXT, 10, "start", False, True)
p2.label(-1, 1.72, "biter", 5, 0, TEXT, 10, "start", False, True)
p2.label(-1, 0, MINUS_S + "1", 5, -6, PRACTICE, 11, "start", True, True)

OUT["kare-onimaj-iki-durum"] = figure(
    560, 250, [p1, p2],
    "&#937; = [&#8722;1, 2] üzerinde <em>X</em>(&#969;) = &#969;<sup>2</sup> için (<em>X</em> &#8804; <em>x</em>) "
    "olayı, [&#8722;&#8730;<em>x</em>, &#8730;<em>x</em>] aralığının &#937; ile kesişimidir. "
    "<em>x</em> &lt; 1 iken aralık &#937;'nın içine sığar ve olayın uzunluğu 2&#8730;<em>x</em> olur; "
    "<em>x</em> &#8805; 1 olunca sol uç &#937;'nın sınırı &#8722;1'e takılır, olay yalnızca sağ uçtan büyür ve "
    "uzunluk 1 + &#8730;<em>x</em>'e düşer. Dağılım fonksiyonunun <em>x</em> = 1'de formül değiştirmesi "
    "bu takılmanın sonucudur.",
    css_class=WIDE,
    aria="Iki panel: X(w)=w kare parabolu, x duzeyinin altinda kalan w kumesi omega ekseninde taranmis; solda x kucuk 1 ile simetrik aralik, sagda x buyuk esit 1 ile sol ucu -1 de kesilen aralik")

# ============================================================ karma-para-duzgun
# Mixed random variable: a coin toss; tails gives X = 0, heads gives X uniform on (0, 1).
# F has a jump of 1/2 at 0 (discrete mass) and then a ramp of slope 1/2 (continuous part).
def halves(v):
    return {0: "0", 1: "1/2", 2: "1"}[round(v * 2)]


p = Plot(50, 26, 304, 206, (-0.6, 1.6), (-0.08, 1.12))
p.axes((0, 1), (0, 0.5, 1.0), "x", "F" + subs("X") + "(x)", yfmt=halves)
guide(p, [(-0.6, 1.0), (1.6, 1.0)], TEXT, 0.35)
guide(p, [(-0.6, 0.5), (0, 0.5)], TEXT, 0.45)
# flat piece for x < 0, the ramp, the flat piece for x >= 1
p.line([(-0.6, 0), (0, 0)], THEORY, 2.4)
p.line([(0, 0.5), (1, 1)], THEORY, 2.4)
p.line([(1, 1), (1.6, 1)], THEORY, 2.4)
hollow(p, (0, 0), THEORY, 4.2, 1.7)
dot(p, (0, 0.5), THEORY, 4.2)
dot(p, (1, 1), THEORY, 4.2)
# the jump at 0: discrete mass P(X = 0) = 1/2
p.arrow((0, 0.05), (0, 0.45), PRACTICE, 1.4, 6.0)
p.arrow((0, 0.45), (0, 0.05), PRACTICE, 1.4, 6.0)
p.label(0, 0.25, "P(X = 0) = 1/2", 9, 4, PRACTICE, 11, "start", True, True)
p.label(0, 0.25, "sıçrama: kesikli kütle", 9, 18, PRACTICE, 10, "start", False, True)
p.label(0.34, 0.5, "eğim 1/2: sürekli parça", 0, 0, THEORY, 11, "start", False, True)
p.label(-0.32, 0.0, "F = 0", 0, -9, THEORY, 10.5, "middle", False, True)
p.label(1.3, 1.0, "F = 1", 0, -9, THEORY, 10.5, "middle", False, True)
OUT["karma-para-duzgun"] = figure(
    400, 256, [p],
    "Karma bir rastgele değişkenin dağılım fonksiyonu: para yazı gelirse <em>X</em> = 0, tura gelirse "
    "<em>X</em> (0, 1) üzerinde düzgün seçilir. <em>x</em> = 0'daki sıçrama <em>P</em>(<em>X</em> = 0) = 1/2 "
    "kesikli kütlesidir; (0, 1) üzerindeki eğimi 1/2 olan rampa ise olasılığın geri kalan yarısının aralığa "
    "yayıldığını gösterir. Fonksiyon ne basamaklı ne de düzdür: sıçrama ile rampa bir aradadır.",
    aria="Para ve duzgun secimden olusan karma degiskenin dagilim fonksiyonu; sifirda yarim sicrama, sonra egimi yarim olan rampa")

# ============================================================ kesikli-donusum-katlama
# Discrete transform Y = X^2 for X uniform on {-2,-1,0,1,2}: the probability of -1 and -2 "folds" onto 1 and 4.
# One pixel-like canvas (data unit = pixel, y upward) so that the arrows can cross freely between the two groups.
p = Plot(0, 0, 560, 245, (0, 560), (0, 245))
BASE_Y = 44          # common baseline of both bar charts
UNIT = 62            # pixels per 1/5
BW = 24              # bar width
COL = {2: BASE, 1: THEORY, 0: PRACTICE}   # colour by |x|


def yaxis(x, top):
    p.line([(x, BASE_Y), (x, top)], TEXT, 1.1, None, 0.5)
    for k, lab in ((1, "1/5"), (2, "2/5")):
        y = BASE_Y + k * UNIT
        p.line([(x - 3, y), (x + 3, y)], TEXT, 1.1, None, 0.5)
        p.label(x - 6, y, lab, 0, 4, TEXT, 10.5, "end", False, False)


# --- left group: f_X ---------------------------------------------------------
XPOS = {-2: 56, -1: 98, 0: 140, 1: 182, 2: 224}
p.line([(30, BASE_Y), (248, BASE_Y)], TEXT, 1.1, None, 0.5)
yaxis(30, BASE_Y + 2.3 * UNIT)
for x, cx in XPOS.items():
    rect(p, cx - BW / 2, cx + BW / 2, BASE_Y, BASE_Y + UNIT, COL[abs(x)], 0.85)
    p.label(cx, BASE_Y, (MINUS_S + str(-x)) if x < 0 else str(x), 0, 15, TEXT, 11, "middle", False, False)
p.label(254, BASE_Y, "x", 0, 4, TEXT, 11.5, "start", False, True)
p.label(140, 228, "f" + subs("X") + "(x) = 1/5, her x için", 0, 0, TEXT, 11.5, "middle", True, False)

# --- right group: f_Y --------------------------------------------------------
YU = 34                                  # pixels per unit of y (true scale 0..4)
YPOS = {v: 352 + YU * v for v in (0, 1, 2, 3, 4)}
p.line([(320, BASE_Y), (506, BASE_Y)], TEXT, 1.1, None, 0.5)
yaxis(320, BASE_Y + 2.3 * UNIT)
for v, cx in YPOS.items():
    p.line([(cx, BASE_Y - 3), (cx, BASE_Y + 3)], TEXT, 1.1, None, 0.5)
    p.label(cx, BASE_Y, str(v), 0, 15, TEXT, 11, "middle", False, False)
p.label(512, BASE_Y, "y", 0, 4, TEXT, 11.5, "start", False, True)
# y = 0: one block; y = 1 and y = 4: two stacked blocks of 1/5, the upper one coming from the negative x
rect(p, YPOS[0] - BW / 2, YPOS[0] + BW / 2, BASE_Y, BASE_Y + UNIT, PRACTICE, 0.85)
for v, col in ((1, THEORY), (4, BASE)):
    cx = YPOS[v]
    rect(p, cx - BW / 2, cx + BW / 2, BASE_Y, BASE_Y + UNIT, col, 0.85)
    rect(p, cx - BW / 2, cx + BW / 2, BASE_Y + UNIT, BASE_Y + 2 * UNIT, col, 0.5)
    p.line([(cx - BW / 2, BASE_Y + UNIT), (cx + BW / 2, BASE_Y + UNIT)], BG, 1.4)
    r = int(round(v ** 0.5))
    p.label(cx + BW / 2 + 4, BASE_Y + UNIT / 2, "f" + subs("X") + "(" + str(r) + ")", 0, 4, col, 10, "start", False, True)
    p.label(cx + BW / 2 + 4, BASE_Y + 1.5 * UNIT, "f" + subs("X") + "(" + MINUS_S + str(r) + ")", 0, 4, col, 10, "start", False, True)
p.label(413, 228, "f" + subs("Y") + "(y), Y = X" + sups("2"), 0, 0, TEXT, 11.5, "middle", True, False)


# --- dashed curved arrows: the negative values are folded over onto the positive ones ---
def fold_arrow(x0, y0, x1, y1, color, rise, drop):
    """Dashed cubic from (x0,y0) going up by `rise`, then coming down onto (x1,y1) from `drop` above."""
    c1, c2 = (x0, y0 + rise), (x1, y1 + drop)
    P = [(p.X(x0), p.Y(y0)), (p.X(c1[0]), p.Y(c1[1])), (p.X(c2[0]), p.Y(c2[1])), (p.X(x1), p.Y(y1))]
    d = 'M %.1f %.1f C %.1f %.1f %.1f %.1f %.1f %.1f' % (P[0] + P[1] + P[2] + P[3])
    p.add('<path d="%s" fill="none" stroke="%s" stroke-width="1.4" stroke-dasharray="4 3" opacity="0.85"/>' % (d, color))
    hx, hy = P[3]
    ux, uy = hx - P[2][0], hy - P[2][1]
    n = math.hypot(ux, uy) or 1.0
    ux, uy = ux / n, uy / n
    px, py, head, hw = -uy, ux, 7.5, 3.2
    p.add('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s" opacity="0.95"/>'
          % (hx, hy, hx - ux * head + px * hw, hy - uy * head + py * hw, hx - ux * head - px * hw, hy - uy * head - py * hw, color))


TOP = BASE_Y + UNIT + 3
fold_arrow(XPOS[-1], TOP, YPOS[1], BASE_Y + 2 * UNIT + 3, THEORY, 70, 40)
fold_arrow(XPOS[-2], TOP, YPOS[4], BASE_Y + 2 * UNIT + 3, BASE, 108, 62)
p.label(280, 152, "x ile " + MINUS_S + "x", 0, 0, TEXT, 10, "middle", False, True)
p.label(280, 138, "aynı y'ye gider", 0, 0, TEXT, 10, "middle", False, True)

OUT["kesikli-donusum-katlama"] = figure(
    560, 245, [p],
    "<em>X</em>, {&#8722;2, &#8722;1, 0, 1, 2} üzerinde her değeri 1/5 olasılıkla alırken <em>Y</em> = "
    "<em>X</em><sup>2</sup>'nin olasılık fonksiyonu. Kare fonksiyonu <em>x</em> ile &#8722;<em>x</em>'i aynı noktaya "
    "götürdüğünden negatif değerlerin olasılığı pozitif olanların üstüne katlanır: <em>f</em><sub><em>Y</em></sub>(1) = "
    "<em>f</em><sub><em>X</em></sub>(&#8722;1) + <em>f</em><sub><em>X</em></sub>(1) = 2/5 ve <em>f</em><sub><em>Y</em></sub>(4) = 2/5. "
    "Yalnızca 0'ın tek ters görüntüsü vardır; <em>f</em><sub><em>Y</em></sub>(0) = 1/5 olarak kalır ve toplam yine 1'dir.",
    css_class=WIDE,
    aria="Solda X'in bes esit cubugu, sagda Y=X kare icin 0, 1 ve 4 noktalarindaki cubuklar; eksi 1 ve eksi 2 cubuklari kesikli oklarla 1 ve 4 cubuklarinin ustune katlaniyor")

# ============================================================ kesikli-kavram-haritasi
# Concept map for a discrete random variable: the induced measure P_X, the distribution
# function F and the probability function f determine one another.
p = Plot(0, 0, 560, 250, (0, 560), (250, 0))   # data coordinates = pixel coordinates
PX = "P" + subs("X")


def box(cx, cy, w, h, s, size=12.5):
    p.add('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="7" fill="%s" fill-opacity="0.09" '
          'stroke="%s" stroke-width="1.4"/>' % (cx - w / 2, cy - h / 2, w, h, THEORY, THEORY))
    p.text_px(cx, cy + 4.5, s, THEORY, size, "middle", True, True)


def both_ways(a, b):
    p.arrow(a, b, PRACTICE, 1.4, 7.0)
    p.arrow(b, a, PRACTICE, 1.4, 7.0)


# the three nodes
box(280, 30, 156, 27, "(&#8477;, B(&#8477;), P" + subs("X", 8) + ")", 12)
box(150, 215, 56, 28, "F")
box(410, 215, 56, 28, "f")
p.text_px(150, 243, "dağılım fonksiyonu", TEXT, 10, "middle", False, True)
p.text_px(410, 243, "olasılık fonksiyonu", TEXT, 10, "middle", False, True)
# where the top node comes from: X carries (Omega, U, P) to the real line
p.text_px(140, 34, "(&#937;, U, P)", BASE, 11, "end", False, True)
p.arrow((147, 30), (198, 30), BASE, 1.4, 7.0)
p.text_px(172, 22, "X", BASE, 11, "middle", True, True)
# edges (each transition works in both directions)
both_ways((238, 44), (168, 200))
both_ways((322, 44), (392, 200))
both_ways((181, 215), (379, 215))
# left edge: P_X <-> F
p.text_px(178, 112, "F(x) = " + PX + "((" + MINUS_S + INF + ", x])", PRACTICE, 10.5, "end")
p.text_px(172, 133, PX + "((a, b]) = F(b) " + MINUS_S + " F(a)", PRACTICE, 10.5, "end")
# right edge: P_X <-> f
p.text_px(382, 112, "f(x) = " + PX + "({x})", PRACTICE, 10.5, "start")
p.text_px(388, 133, PX + "(B) = " + SUM_S + " f(x)  (x B içinde)", PRACTICE, 10.5, "start")
# bottom edge: F <-> f
p.text_px(280, 204, "F(x) = " + SUM_S + " f(x" + subs("i") + "),  x" + subs("i") + " " + LEQ_S + " x",
          PRACTICE, 10.5, "middle")
p.text_px(280, 233, "f(x) = F(x) " + MINUS_S + " F(x&#8315;)", PRACTICE, 10.5, "middle")
p.text_px(280, 130, "aynı dağılım", TEXT, 10.5, "middle", False, True)
OUT["kesikli-kavram-haritasi"] = figure(
    560, 250, [p],
    "Kesikli bir rastgele değişkenin dağılımını betimleyen üç nesne. <em>X</em> fonksiyonu olasılık uzayını "
    "sayı doğrusuna taşır ve <em>P<sub>X</sub></em> ölçüsünü doğurur; bu ölçü, dağılım fonksiyonu <em>F</em> ve "
    "olasılık fonksiyonu <em>f</em> birbirini belirler. Kenarlardaki formüller her geçişin iki yönünü verir: "
    "<em>f</em>'den <em>F</em>'ye biriktirerek, <em>F</em>'den <em>f</em>'ye sıçramaları okuyarak geçilir.",
    css_class=WIDE,
    aria="Ucgen sema: ustte olcu P_X, altta dagilim fonksiyonu F ve olasilik fonksiyonu f; kenarlarda cift yonlu gecis formulleri")

# ============================================================ konvolusyon-serit
# Convolution of two independent U(0,1) densities. Left: the unit square (f = 1) and the
# lines x + y = z for z = 0.5 and z = 1.5; f_Z(z) is the integral of f along the line, i.e. the
# x-length of the chord inside the square. Right: the resulting triangular density of Z = X + Y.
def it(s):
    return '<tspan font-style="italic">%s</tspan>' % s


FZ = it("f") + subs(it("Z"))
Z1, Z2 = 0.5, 1.5

# ---- left panel: the support and two lines x + y = z (equal pixel scale on both axes)
p1 = Plot(40, 30, 226, 192, (-0.2, 1.8), (-0.22, 1.48))
rect(p1, 0, 1, 0, 1, THEORY, 0.12, THEORY, 1.3)
p1.polygon([(0, 0), (Z1, 0), (0, Z1)], THEORY, 0.3)
p1.origin_axes("x", "y", xticks=(1,), yticks=(1,))
p1.label(0, 0, "0", -6, 14, TEXT, 10.5, "end")
# z = 0.5: the line, thin beyond the square, thick inside it
p1.line([(-0.12, Z1 + 0.12), (Z1 + 0.12, -0.12)], THEORY, 1.1, "5 3", 0.8)
p1.line([(0, Z1), (Z1, 0)], THEORY, 3.2)
# z = 1.5
p1.line([(Z2 - 1.12, 1.12), (1.12, Z2 - 1.12)], PRACTICE, 1.1, "5 3", 0.8)
p1.line([(Z2 - 1, 1), (1, Z2 - 1)], PRACTICE, 3.2)
p1.label(0.65, 0.68, it("f") + " = 1", 0, 0, THEORY, 11, "middle")
p1.label(Z1 + 0.12, -0.12, it("z") + " = 0,5", 8, 3, THEORY, 10.5, "start", True)
p1.label(1.12, Z2 - 1.12, it("z") + " = 1,5", 8, 3, PRACTICE, 10.5, "start", True)
p1.text_px(p1.X(1.12), p1.Y(1.36), it("x") + " + " + it("y") + " = " + it("z") + " doğrusu", THEORY, 10, "start")
p1.text_px(p1.X(1.12), p1.Y(1.24), "boyunca " + it("f") + "'yi topla:", THEORY, 10, "start")
p1.text_px(p1.X(1.12), p1.Y(1.12), "kalın parçanın uzunluğu", THEORY, 10, "start")
panel_title(p1, FZ + "(" + it("z") + ") = " + INT_S + " " + it("f") + subs(it("X")) + "(" + it("x") + ") "
            + it("f") + subs(it("Y")) + "(" + it("z") + " " + MINUS_S + " " + it("x") + ") d" + it("x"), TEXT, 11)

# ---- right panel: the triangular density of Z
p2 = Plot(322, 30, 226, 192, (-0.2, 2.3), (-0.14, 1.22))
p2.origin_axes("z", FZ + "(" + it("z") + ")", xticks=(Z1, 1, Z2, 2), yticks=(0.5, 1), xfmt=tfmt, yfmt=tfmt)
p2.polygon([(0, 0), (1, 1), (2, 0)], BASE, 0.12)
p2.line([(0, 0), (1, 1), (2, 0)], BASE, 2.2)
guide(p2, [(Z1, 0), (Z1, Z1)], THEORY, 0.7)
guide(p2, [(Z2, 0), (Z2, 2 - Z2)], PRACTICE, 0.7)
guide(p2, [(0, 0.5), (Z2, 0.5)], TEXT, 0.35)
dot(p2, (Z1, Z1), THEORY, 4)
dot(p2, (Z2, 2 - Z2), PRACTICE, 4)
p2.label(Z1, Z1, FZ + "(0,5) = 0,5", 9, 15, THEORY, 10.5, "start", True)
p2.label(Z2, 2 - Z2, FZ + "(1,5) = 0,5", 8, -2, PRACTICE, 10.5, "start", True)
p2.label(1, 1, it("z"), -8, 2, BASE, 10.5, "end")
p2.label(1, 1, "2 " + MINUS_S + " " + it("z"), 10, 2, BASE, 10.5, "start")
panel_title(p2, it("Z") + " = " + it("X") + " + " + it("Y") + " üçgen yoğunluk", BASE, 11)

OUT["konvolusyon-serit"] = figure(
    560, 245, [p1, p2],
    "Konvolüsyon formülünün geometrisi. <em>X</em> ve <em>Y</em> bağımsız, (0, 1) üzerinde düzgün olsun; ortak "
    "yoğunluk birim karede <em>f</em> = 1'dir. <em>f<sub>Z</sub></em>(<em>z</em>), <em>x</em> + <em>y</em> = <em>z</em> "
    "doğrusu boyunca <em>f</em>'nin toplamıdır: yalnızca karenin içindeki kalın parça katkı verir ve bu parçanın "
    "<em>x</em>-uzunluğu <em>z</em> = 0,5 ile <em>z</em> = 1,5 için 0,5'tir. Doğru karede kaydıkça bu uzunluk önce "
    "<em>z</em>, sonra 2 &#8722; <em>z</em> olur; sağdaki üçgen yoğunluk böyle doğar. Sol panelde açık taralı "
    "<em>x</em> + <em>y</em> &#8804; 0,5 üçgeni <em>F<sub>Z</sub></em>(0,5) = 1/8 olasılığıdır.",
    css_class=WIDE,
    aria="Solda birim kare ve x arti y esittir z dogrulari z = 0,5 ve z = 1,5 icin; sagda Z = X + Y toplaminin ucgen yogunlugu")

# ============================================================ korelasyon-sacilim
# Three deterministic point clouds illustrating rho ~ 0.9, rho ~ -0.9 and rho = 0.
def cloud(rho, n=60, seed=7):
    """Pseudo-random but reproducible points with the requested correlation (no random module)."""
    pts = []
    s = seed
    for k in range(n):
        s = (1103515245 * s + 12345) % 2147483648
        u1 = s / 2147483648
        s = (1103515245 * s + 12345) % 2147483648
        u2 = s / 2147483648
        # Box-Muller
        r = math.sqrt(-2 * math.log(max(u1, 1e-9)))
        z1, z2 = r * math.cos(2 * math.pi * u2), r * math.sin(2 * math.pi * u2)
        x = z1
        y = rho * z1 + math.sqrt(1 - rho * rho) * z2
        pts.append((x, y))
    return pts


panels = []
for i, (rho, col, ttl) in enumerate(((0.9, THEORY, "&#961; &#8776; 0,9"), (-0.9, PRACTICE, "&#961; &#8776; " + MINUS_S + "0,9"), (0.0, BASE, "&#961; = 0"))):
    q = Plot(24 + i * 184, 34, 160, 160, (-3.2, 3.2), (-3.2, 3.2))
    q.origin_axes("x", "y")
    panel_title(q, ttl, col)
    q.points(cloud(rho, 70, 11 + i), col, 2.8)
    if abs(rho) > 0:
        q.line([(-2.8, -2.8 * rho), (2.8, 2.8 * rho)], col, 1.2, "5 4", 0.7)
    panels.append(q)
OUT["korelasyon-sacilim"] = figure(
    570, 226, panels,
    "Korelasyon katsayısı doğrusal ilişkinin yönünü ve gücünü ölçer. Solda &#961;'ya yakın pozitif: noktalar "
    "artan bir doğru çevresinde toplanır; ortada negatif: azalan doğru; sağda &#961; = 0: doğrusal bir eğilim "
    "yok. &#961; = 0 bağımsızlık demek değildir — yalnızca doğrusal bağın yokluğudur.",
    css_class=WIDE,
    aria="Uc sacilim grafigi: pozitif, negatif ve sifir korelasyon")

# ============================================================ kosullu-daraltma
# Conditional probability as a change of sample space: on the left, A and B inside Omega with
# B lightly tinted and A n B darkly tinted; on the right, B alone blown up as the new sample
# space, with A n B inside it. P(A | B) is the share of A n B inside B.
R_C, D_C = 1.0, 1.2                 # radius of the two circles and the distance between the centres
RX, RY = 2.28, 1.55                 # half-sides of the sample-space rectangle (left panel)
XA, XB = -D_C / 2 - 0.05, D_C / 2 - 0.05
S = 1.55                            # blow-up factor of B on the right


def lens(xa, xb, r, n=40):
    """Intersection of the discs centred at (xa, 0) and (xb, 0): right arc of the left disc, then left arc of the right disc."""
    th = math.acos((xb - xa) / (2 * r))
    pts = [(xa + r * math.cos(-th + 2 * th * k / n), r * math.sin(-th + 2 * th * k / n)) for k in range(n + 1)]
    pts += [(xb + r * math.cos(math.pi - th + 2 * th * k / n), r * math.sin(math.pi - th + 2 * th * k / n))
            for k in range(n + 1)]
    return pts


def disk(cx, cy, r, n=96):
    return [(cx + r * math.cos(2 * math.pi * k / n), cy + r * math.sin(2 * math.pi * k / n)) for k in range(n)]


# both panels share the same scale: 48 px per unit in x and y
pL = Plot(10, 30, 240, 168, (-2.5, 2.5), (-1.75, 1.75))
pR = Plot(310, 30, 240, 168, (-2.5, 2.5), (-1.75, 1.75))

# ---- left: the original sample space -------------------------------------------------------
pL.polygon([(-RX, -RY), (RX, -RY), (RX, RY), (-RX, RY)], TEXT, 0.0, TEXT, 1.0)
pL.polygon(disk(XB, 0, R_C), THEORY, 0.16)                     # B, light
pL.polygon(lens(XA, XB, R_C), THEORY, 0.55)                    # A n B, dark
pL.circle(XA, 0, R_C, PRACTICE, 1.6)
pL.circle(XB, 0, R_C, THEORY, 1.6)
pL.label(XA - 1.04, 0.6, "A", 0, 4, PRACTICE, 12.5, "middle", True, True)
pL.label(XB + 1.04, 0.6, "B", 0, 4, THEORY, 12.5, "middle", True, True)
pL.text_px(pL.X(RX) - 5, pL.Y(RY) + 14, "&#937;", TEXT, 12, "end", False, True)
pL.label((XA + XB) / 2, -0.05, "A &#8745; B", 0, 4, BG, 10.5, "middle", True)
panel_title(pL, "Örnek uzay &#937;", TEXT, 11.5)
pL.text_px(pL.x0 + pL.w / 2, 222, "P(A) = alan(A) / alan(&#937;)", TEXT, 11.5, "middle", True)
pL.text_px(pL.x0 + pL.w / 2, 240, "A'nın &#937; içindeki payı", TEXT, 10.5, "middle", False, True)

# ---- right: B is the new sample space -------------------------------------------------------
pR.polygon(disk(0, 0, S * R_C), THEORY, 0.16)
pR.polygon([((x - XB) * S, y * S) for x, y in lens(XA, XB, R_C)], THEORY, 0.55)
pR.circle(0, 0, S * R_C, THEORY, 1.8)
# the part of A's boundary that lies inside B, so A is still recognisable
th = math.acos(D_C / (2 * R_C))
pR.arc((XA - XB) * S, 0, S * R_C, -th, th, PRACTICE, 1.6)
pR.label(1.2 * S * math.cos(0.5), 1.2 * S * math.sin(0.5), "B", 0, 4, THEORY, 12.5, "middle", True, True)
pR.label((XA - XB) * S / 2 + 0.02, -0.05, "A &#8745; B", 0, 4, BG, 10.5, "middle", True)
panel_title(pR, "Yeni örnek uzay: B", TEXT, 11.5)
pR.text_px(pR.x0 + pR.w / 2, 222, "P(A | B) = P(A &#8745; B) / P(B)", TEXT, 11.5, "middle", True)
pR.text_px(pR.x0 + pR.w / 2, 240, "= alan(A &#8745; B) / alan(B): payı B'ye göre", TEXT, 10.5, "middle", False, True)

# ---- the arrow between the panels: conditioning on B ----------------------------------------
pL.add(f'<line x1="256" y1="114" x2="298" y2="114" stroke="{TEXT}" stroke-width="1.4"/>'
       f'<polygon points="298,114 291,110 291,118" fill="{TEXT}"/>')
pL.text_px(280, 100, "B biliniyor", TEXT, 10, "middle", False, True)
pL.text_px(280, 130, "&#937; yerine B", TEXT, 10, "middle", False, True)

OUT["kosullu-daraltma"] = figure(
    560, 250, [pL, pR],
    "Koşullu olasılık, örnek uzayın daraltılmasıdır. Solda <em>A</em> ve <em>B</em> olayları &#937; içinde "
    "durur; <em>B</em> açık, <em>A</em> &#8745; <em>B</em> koyu renkle taranmıştır ve <em>P</em>(<em>A</em>), "
    "<em>A</em>'nın &#937; içindeki payıdır. <em>B</em>'nin gerçekleştiği öğrenilince &#937;'nın <em>B</em> dışındaki "
    "kısmı elenir ve sağda <em>B</em> yeni örnek uzay olur; <em>A</em> artık ancak <em>A</em> &#8745; <em>B</em> "
    "üzerinden gerçekleşebilir. <em>P</em>(<em>A</em> | <em>B</em>) = <em>P</em>(<em>A</em> &#8745; <em>B</em>) / "
    "<em>P</em>(<em>B</em>) bölmesi, olasılıkları <em>B</em>'nin toplamı 1 olacak biçimde yeniden ölçekler.",
    css_class=WIDE,
    aria="Solda dikdortgen ornek uzay icinde A ve B daireleri, B acik ve A kesisim B koyu tarali; sagda yalniz B buyutulmus yeni ornek uzay olarak, icinde A kesisim B koyu tarali")

# ============================================================ kosullu-ortalama-ucgen
# Uniform density f = 2 on the triangle 0 < x < y < 1: the vertical section at x = x0,
# its midpoint (1 + x0)/2, and the regression line E(Y | X = x) = (1 + x)/2.
X0 = 0.4


def it(s):
    return '<tspan font-style="italic">%s</tspan>' % s


XSUB = it("x") + subs("0")


def xfmt_(t):
    return XSUB if abs(t - X0) < 1e-9 else fmt(t)


def yfmt_(t):
    if abs(t - 0.5) < 1e-9:
        return "1/2"
    if abs(t - (1 + X0) / 2) < 1e-9:
        return "(1+" + XSUB + ")/2"
    return fmt(t)


p = Plot(40, 24, 256, 208, (-0.16, 1.36), (-0.12, 1.11))
# the support of the joint density, lightly shaded
p.polygon([(0, 0), (0, 1), (1, 1)], THEORY, 0.14, THEORY, 1.4)
p.origin_axes("x", "y", xticks=(X0, 1), yticks=(0.5, (1 + X0) / 2, 1), xfmt=xfmt_, yfmt=yfmt_)
p.text_px(p.X(0) - 7, p.Y(0) + 15, "0", TEXT, 11, "end")
# guides: the x0 tick up to the lower edge, the midpoint across to the y axis, the corner (1,1)
guide(p, [(X0, 0), (X0, X0)], TEXT, 0.45)
guide(p, [(0, (1 + X0) / 2), (X0, (1 + X0) / 2)], TEXT, 0.45)
guide(p, [(1, 0), (1, 1)], TEXT, 0.3)
# regression line y = (1 + x)/2, dashed
p.line([(0, 0.5), (1, 1)], BASE, 1.9, "6 4")
# the vertical section at x = x0 (thick) and its midpoint
p.line([(X0, X0), (X0, 1)], PRACTICE, 3.4)
p.add('<circle cx="%.1f" cy="%.1f" r="4.4" fill="%s" stroke="%s" stroke-width="1.6"/>'
      % (p.X(X0), p.Y((1 + X0) / 2), BASE, BG))
# labels
p.label(0.2, 0.44, it("f") + "(" + it("x") + ", " + it("y") + ") = 2", 0, 0, THEORY, 10.5, "middle")
p.label(X0, 0.92, it("Y") + " | " + it("X") + " = " + XSUB, -7, 0, PRACTICE, 10.5, "end")
p.label(X0, 0.84, "düzgün", -7, 0, PRACTICE, 10.5, "end")
p.label(1, 1, it("E") + "(" + it("Y") + " | " + it("X") + " = " + it("x") + ") = (1 + " + it("x") + ")/2",
        8, 4, BASE, 10.5, "start")
OUT["kosullu-ortalama-ucgen"] = figure(
    400, 246, [p],
    "Üçgen üzerinde düzgün dağılımın koşullu ortalaması. Taralı üçgen, <em>f</em>(<em>x</em>, <em>y</em>) = 2 "
    "yoğunluğunun tanım bölgesidir. <em>X</em> = <em>x</em><sub>0</sub> verilmişken <em>Y</em> yalnızca kalın düşey "
    "kesit üzerinde, (<em>x</em><sub>0</sub>, 1) aralığında düzgün dağılır; koşullu beklenen değer bu kesitin orta "
    "noktası (1 + <em>x</em><sub>0</sub>)/2'dir. <em>x</em><sub>0</sub> değiştikçe orta noktalar kesikli "
    "<em>y</em> = (1 + <em>x</em>)/2 doğrusunu çizer: (0, 1/2)'den (1, 1)'e uzanan regresyon doğrusu.",
    aria="Ucgen bolge uzerinde x = x0 dusey kesiti, orta noktasi ve kosullu ortalama dogrusu y = (1+x)/2")

# ============================================================ kosullu-yogunluk-kesit
# Conditional density as a normalised section: f(x, y) = 1/x on 0 < y < x < 1, f_X(x) = 1,
# so f_{Y|X=x0}(y) = 1/x0 on (0, x0) — a rectangle of area 1 on the y axis.
X0 = 0.6


def it(s):
    return '<tspan font-style="italic">%s</tspan>' % s


XSUB = it("x") + subs("0")
COND = it("f") + subs(it("Y") + " | " + it("X") + " = " + XSUB)


def xf(t):
    return XSUB if abs(t - X0) < 1e-9 else fmt(t)


def yf(t):
    return "1/" + XSUB if abs(t - 1 / X0) < 1e-9 else fmt(t)


# --- left: the support and the section at x = x0 ------------------------------
p1 = Plot(40, 30, 200, 200, (-0.2, 1.32), (-0.22, 1.3))
p1.polygon([(0, 0), (1, 0), (1, 1)], THEORY, 0.2, THEORY, 1.4)
p1.origin_axes("x", "y", xticks=(X0, 1.0), yticks=(X0, 1.0), xfmt=xf, yfmt=xf)
guide(p1, [(1, 0), (1, 1)], TEXT, 0.3)
guide(p1, [(0, X0), (X0, X0)], TEXT, 0.45)
p1.line([(X0, 0), (X0, X0)], PRACTICE, 3.6)
panel_title(p1, "ortak yoğunluk ve " + it("x") + " = " + XSUB + " kesiti", TEXT, 11.5)
p1.label(0.64, 1.13, it("f") + "(" + it("x") + ", " + it("y") + ") = 1/" + it("x") + ",  0 &lt; " + it("y")
         + " &lt; " + it("x") + " &lt; 1", 0, 0, THEORY, 10.5, "middle")
p1.label(X0, 0.42, "kesit", 7, 0, PRACTICE, 10.5, "start")
p1.label(X0, 0.27, "(0, " + XSUB + ")", 7, 0, PRACTICE, 10.5, "start")
p1.label(0.82, 0.14, it("D"), 0, 4, THEORY, 12, "middle", True)
# arrow across the gap between the panels: divide the section by f_X(x0)
p1.arrow((1.48, 0.55), (1.96, 0.55), PRACTICE, 1.8, 8)
p1.label(1.72, 0.55, "kesit / " + it("f") + subs(it("X")) + "(" + XSUB + ")", 0, -8, PRACTICE, 10, "middle")
p1.label(1.72, 0.55, it("f") + subs(it("X")) + "(" + XSUB + ") = 1", 0, 16, PRACTICE, 10, "middle")

# --- right: the conditional density on the y axis -----------------------------
p2 = Plot(336, 30, 190, 200, (-0.2, 1.32), (-0.3, 2.1))
p2.origin_axes("y", "", xticks=(X0, 1.0), yticks=(1.0, 1 / X0), xfmt=xf, yfmt=yf)
rect(p2, 0, X0, 0, 1 / X0, PRACTICE, 0.2, PRACTICE, 1.6)
p2.line([(0, 1 / X0), (X0, 1 / X0)], PRACTICE, 3.0)
p2.line([(X0, 0), (1.22, 0)], PRACTICE, 3.0)
panel_title(p2, "koşullu yoğunluk " + COND, TEXT, 11.5)
p2.label(0.5, 1.9, COND + "(" + it("y") + ") = 1/" + XSUB, 0, 0, PRACTICE, 10.5, "middle")
p2.label(X0 / 2, 0.55, "alan = 1", 0, 4, TEXT, 11, "middle", True)
p2.label(X0 / 2, 1.3, "(0, " + XSUB + ") üzerinde", 0, 4, PRACTICE, 10, "middle")
p2.label(X0 / 2, 1.06, "düzgün", 0, 4, PRACTICE, 10, "middle")
p2.label(0.92, 0.0, "kesit dışında 0", 0, -8, PRACTICE, 10, "middle")

OUT["kosullu-yogunluk-kesit"] = figure(
    560, 245, [p1, p2],
    "Koşullu yoğunluk, ortak yoğunluğun bir kesitidir. Solda <em>f</em>(<em>x</em>, <em>y</em>) = 1/<em>x</em> "
    "yoğunluğunun üçgen desteği ve <em>x</em> = <em>x</em><sub>0</sub> apsisindeki kalın düşey kesit (0, "
    "<em>x</em><sub>0</sub>) görülür. Bu kesit üzerindeki değerler <em>f<sub>X</sub></em>(<em>x</em><sub>0</sub>) = 1 "
    "marjinaline bölününce sağdaki koşullu yoğunluk çıkar: (0, <em>x</em><sub>0</sub>) üzerinde sabit "
    "1/<em>x</em><sub>0</sub>, kesit dışında 0. Dikdörtgenin alanı 1'dir; <em>X</em> = <em>x</em><sub>0</sub> "
    "verilmişken <em>Y</em>, (0, <em>x</em><sub>0</sub>) üzerinde düzgün dağılır.",
    css_class=WIDE,
    aria="Solda ucgen destek ve x = x0 dusey kesiti; sagda y ekseni uzerinde (0, x0) araliginda 1/x0 yuksekliginde alani 1 olan kosullu yogunluk dikdortgeni")

# ============================================================ kovaryans-isaret
# The sign of the covariance: a scatter with rho ~ 0.7, axes through the mean point (mu_X, mu_Y),
# the four quadrants coloured by the sign of (x - mu_X)(y - mu_Y).
def cloud(rho, n=60, seed=7):
    """Pseudo-random but reproducible points with the requested correlation (no random module)."""
    pts = []
    s = seed
    for k in range(n):
        s = (1103515245 * s + 12345) % 2147483648
        u1 = s / 2147483648
        s = (1103515245 * s + 12345) % 2147483648
        u2 = s / 2147483648
        # Box-Muller
        r = math.sqrt(-2 * math.log(max(u1, 1e-9)))
        z1, z2 = r * math.cos(2 * math.pi * u2), r * math.sin(2 * math.pi * u2)
        x = z1
        y = rho * z1 + math.sqrt(1 - rho * rho) * z2
        pts.append((x, y))
    return pts


def it(s):
    return '<tspan font-style="italic">%s</tspan>' % s


MUX = "&#956;" + subs(it("X"))
MUY = "&#956;" + subs(it("Y"))
PROD = "(" + it("x") + " " + MINUS_S + " " + MUX + ")(" + it("y") + " " + MINUS_S + " " + MUY + ")"

XR, YR = 3.3, 2.5
p = Plot(56, 26, 296, 186, (-XR, XR), (-YR, YR))
# quadrants: positive product in blue, negative product in orange
rect(p, 0, XR, 0, YR, THEORY, 0.11)
rect(p, -XR, 0, -YR, 0, THEORY, 0.11)
rect(p, -XR, 0, 0, YR, PRACTICE, 0.11)
rect(p, 0, XR, -YR, 0, PRACTICE, 0.11)
p.axes((0,), (0,), "x", "y", xfmt=lambda t: MUX, yfmt=lambda t: MUY)
# dashed axes through the mean point
guide(p, [(-XR, 0), (XR, 0)], TEXT, 0.55)
guide(p, [(0, -YR), (0, YR)], TEXT, 0.55)
# the cloud, each point coloured by the sign of its product
pos, neg = [], []
for x, y in cloud(0.7, 60, 5):
    x, y = 0.85 * x, 0.85 * y
    if abs(x) < 2.9 and abs(y) < 1.95:
        (pos if x * y > 0 else neg).append((x, y))
p.points(pos, THEORY, 2.9)
p.points(neg, PRACTICE, 2.9)
p.add('<circle cx="%.1f" cy="%.1f" r="4.2" fill="%s" stroke="%s" stroke-width="1.6"/>'
      % (p.X(0), p.Y(0), TEXT, BG))
# corner labels: the product's sign in each quadrant
GT, LT = " &gt; 0", " &lt; 0"
p.text_px(p.x0 + p.w - 6, p.y0 + 14, PROD + GT, THEORY, 10, "end", True)
p.text_px(p.x0 + 6, p.y0 + 14, PROD + LT, PRACTICE, 10, "start", True)
p.text_px(p.x0 + 6, p.y0 + p.h - 7, PROD + GT, THEORY, 10, "start", True)
p.text_px(p.x0 + p.w - 6, p.y0 + p.h - 7, PROD + LT, PRACTICE, 10, "end", True)
# big signs
p.label(2.55, 0.75, "+", 0, 7, THEORY, 22, "middle", True)
p.label(-2.55, -0.75, "+", 0, 7, THEORY, 22, "middle", True)
p.label(-2.55, 0.75, MINUS_S, 0, 7, PRACTICE, 22, "middle", True)
p.label(2.55, -0.75, MINUS_S, 0, 7, PRACTICE, 22, "middle", True)
# the conclusion, under the axis
p.text_px(p.x0 + p.w / 2, p.y0 + p.h + 34,
          "Cov(" + it("X") + ", " + it("Y") + ") = bu çarpımların ortalaması &gt; 0", TEXT, 11, "middle")
OUT["kovaryans-isaret"] = figure(
    400, 255, [p],
    "Kovaryansın işareti. Kesikli eksenler ortalama noktası (<em>&#956;<sub>X</sub></em>, <em>&#956;<sub>Y</sub></em>)'de "
    "kesişir; sağ üst ve sol alt çeyreklerde (<em>x</em> &#8722; <em>&#956;<sub>X</sub></em>)(<em>y</em> &#8722; "
    "<em>&#956;<sub>Y</sub></em>) çarpımı pozitif (mavi), öteki iki çeyrekte negatiftir (turuncu). Noktaların çoğu "
    "mavi çeyreklerde toplandığından çarpımların ortalaması, yani Cov(<em>X</em>, <em>Y</em>), pozitif çıkar. "
    "<em>X</em> büyükken <em>Y</em> küçük olma eğiliminde olsaydı turuncu çeyrekler ağır basar ve kovaryans negatif olurdu.",
    aria="Ortalama noktasindan gecen kesikli eksenlerle dort ceyrege bolunmus sacilim; pozitif carpim mavi, negatif carpim turuncu")

# ============================================================ kule-kurali
# Tower rule on the three-coin example: X1 = heads in three tosses, X2 = heads in the first two.
# Left: the conditional pmf of X1 given X2 = x2 (two equal bars) and its mean x2 + 1/2.
# Middle: weight by P(X2 = x2) = 2/8, 4/8, 2/8. Right: the marginal of X1 and E(X1) = 3/2.
def it(s):
    return '<tspan font-style="italic">%s</tspan>' % s


def col(s, c, bold=False):
    return '<tspan fill="%s"%s>%s</tspan>' % (c, ' font-weight="bold"' if bold else "", s)


X1 = it("X") + subs("1")
X2 = it("X") + subs("2")
XR, YR = (-0.7, 3.7), (0.0, 1.1)
WEIGHTS = ("2/8", "4/8", "2/8")
MEANS = ("1/2", "3/2", "5/2")


def mean_marker(q, m, txt):
    """Dashed guide from the axis up to the label, and the mean as a dot on the axis."""
    guide(q, [(m, 0), (m, 0.82)], PRACTICE, 0.8, 1.2)
    q.add('<circle cx="%.1f" cy="%.1f" r="4.2" fill="%s" stroke="%s" stroke-width="1.5"/>'
          % (q.X(m), q.Y(0), PRACTICE, BG))
    q.label(m, 0.82, txt, 0, -6, PRACTICE, 11, "middle", True)


panels = []
for i in range(3):
    q = Plot(44 + i * 104, 44, 88, 110, XR, YR)
    q.axes((0, 1, 2, 3), (0.5,) if i == 0 else (), "", "", yfmt=lambda t: "1/2")
    q.bars([(i, 0.5), (i + 1, 0.5)], THEORY, 12, 0.85)
    mean_marker(q, i + 0.5, MEANS[i])
    panel_title(q, X2 + " = %d" % i, TEXT, 11)
    q.text_px(q.x0 + q.w / 2, q.y0 + q.h + 33, "P(" + X2 + " = %d) = %s" % (i, WEIGHTS[i]), BASE, 10, "middle")
    panels.append(q)

# header over the three conditional panels
panels[0].text_px(44 + 148, 14, X2 + " = " + it("x") + subs("2") + " verilmişken " + X1
                  + "'in koşullu dağılımı", THEORY, 10.5, "middle")
panels[0].text_px(44, 206, "E(" + X1 + " | " + X2 + " = " + it("x") + subs("2") + ") = "
                  + it("x") + subs("2") + " + 1/2", PRACTICE, 10.5, "start")

# the weighting arrow
mid = Plot(340, 44, 80, 110, (0, 1), (0, 1))
mid.text_px(380, 78, "P(" + X2 + " = " + it("x") + subs("2") + ") ile", BASE, 10, "middle")
mid.text_px(380, 92, "ağırlıklandır", BASE, 10, "middle")
mid.arrow((0.1, 0.42), (0.9, 0.42), BASE, 2.0, 9)

# right: the marginal of X1 and its mean
r = Plot(432, 44, 100, 110, XR, YR)
r.axes((0, 1, 2, 3), (1 / 8, 3 / 8), "", "", yfmt=lambda t: "1/8" if t < 0.2 else "3/8")
r.bars([(0, 1 / 8), (1, 3 / 8), (2, 3 / 8), (3, 1 / 8)], THEORY, 12, 0.45)
mean_marker(r, 1.5, "3/2")
panel_title(r, X1 + "'in marjinali", TEXT, 11)
r.text_px(r.x0 + r.w / 2, r.y0 + r.h + 33, "E(" + X1 + ") = 3/2", PRACTICE, 10.5, "middle", True)

# the computation and the rule
r.text_px(280, 228,
          "E[E(" + X1 + " | " + X2 + ")] = " + col("1/2", PRACTICE) + " &#183; " + col("2/8", BASE) + " + "
          + col("3/2", PRACTICE) + " &#183; " + col("4/8", BASE) + " + " + col("5/2", PRACTICE) + " &#183; "
          + col("2/8", BASE) + " = 12/8 = " + col("3/2", PRACTICE, True) + " = E(" + X1 + ")",
          TEXT, 11, "middle")
r.text_px(280, 247, "Kule kuralı:  E[E(" + it("Y") + " | " + it("X") + ")] = E(" + it("Y") + ")",
          TEXT, 11.5, "middle", True)

OUT["kule-kurali"] = figure(
    560, 254, panels + [mid, r],
    "Kule kuralı üç para atışı örneğinde. Solda, ilk iki atıştaki tura sayısı <em>X</em><sub>2</sub> = "
    "<em>x</em><sub>2</sub> verilmişken toplam tura sayısı <em>X</em><sub>1</sub>, <em>x</em><sub>2</sub> ve "
    "<em>x</em><sub>2</sub> + 1 değerlerini eşit olasılıkla alır; dilim ortalaması "
    "E(<em>X</em><sub>1</sub> | <em>X</em><sub>2</sub> = <em>x</em><sub>2</sub>) = <em>x</em><sub>2</sub> + 1/2 "
    "eksende turuncu noktayla gösterilmiştir. Bu üç dilim ortalaması P(<em>X</em><sub>2</sub> = "
    "<em>x</em><sub>2</sub>) = 2/8, 4/8, 2/8 ağırlıklarıyla toplanınca sağdaki marjinal dağılımın ortalaması "
    "E(<em>X</em><sub>1</sub>) = 3/2 çıkar: E[E(<em>X</em><sub>1</sub> | <em>X</em><sub>2</sub>)] = "
    "E(<em>X</em><sub>1</sub>).",
    css_class=WIDE,
    aria="Uc para atisinda kule kurali: X2 = 0, 1, 2 icin X1'in kosullu dagilimlari ve ortalamalari, agirliklandirma oku ve X1'in marjinali ile ortalamasi 3/2")

# ============================================================ marjinal-projeksiyon
# Marginal density as 'integrate the other variable away': f(x, y) = xy on (0,1) x (0,2)
# (exercise e of the chapter), the vertical strip at x = x0, f_X(x) = 2x below, f_Y(y) = y/2 on the left.
X0 = 0.65


def it(s):
    return '<tspan font-style="italic">%s</tspan>' % s


XSUB = it("x") + subs("0")
FX = it("f") + subs(it("X"))
FY = it("f") + subs(it("Y"))

# main panel: the support D = (0,1) x (0,2), shaded darker where xy is larger
p = Plot(118, 22, 180, 150, (0, 1), (0, 2))
p.axes((), (1, 2), "", "")
rect(p, 0, 1, 0, 2, THEORY, 0.08, THEORY, 1.3)
for c in (0.25, 0.5, 0.8, 1.15, 1.55):
    # the region {xy > c} inside D, bounded by the hyperbola y = c/x
    arc = [(x, c / x) for x in [c / 2 + (1 - c / 2) * k / 60 for k in range(61)]]
    p.polygon(arc + [(1, 2)], THEORY, 0.10)
    p.line(arc, THEORY, 0.8, None, 0.5)
# the vertical section at x = x0
rect(p, X0 - 0.028, X0 + 0.028, 0, 2, PRACTICE, 0.55)
p.line([(X0, 0), (X0, 2)], PRACTICE, 1.2)
p.text_px(p.x0, 14, it("f") + "(" + it("x") + ", " + it("y") + ") = " + it("x") + it("y"), THEORY, 11.5, "start")
p.text_px(p.X(X0) + 4, 14, it("y") + " boyunca topla", PRACTICE, 9.5, "middle", False, True)
# a horizontal section at y = y0, sent to the left marginal the same way
Y0 = 1.5
rect(p, 0, 1, Y0 - 0.035, Y0 + 0.035, BASE, 0.5)
p.line([(0, Y0), (1, Y0)], BASE, 1.2)

# bottom strip: the marginal of X
b = Plot(118, 192, 180, 52, (0, 1), (0, 2.35))


def xfmt_(t):
    return XSUB if abs(t - X0) < 1e-9 else fmt(t)


b.axes((0, X0, 1), (2,), "x", "", xfmt=xfmt_)
b.polygon([(0, 0), (1, 0), (1, 2)], PRACTICE, 0.14)
b.line([(0, 0), (1, 2)], PRACTICE, 2.0)
guide(b, [(X0, 0), (X0, 2 * X0)], PRACTICE, 0.7)
dot(b, (X0, 2 * X0), PRACTICE, 3.6)
b.label(1, 2, FX + "(" + it("x") + ") = 2" + it("x"), 10, 4, PRACTICE, 11, "start")
# the arrow from the strip to f_X(x0), with the defining integral beside it
p.add('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.6"/>'
      % (p.X(X0), p.Y(0) + 3, p.X(X0), b.Y(2 * X0) - 10, PRACTICE))
p.add('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>'
      % (p.X(X0), b.Y(2 * X0) - 5, p.X(X0) - 3.5, b.Y(2 * X0) - 13, p.X(X0) + 3.5, b.Y(2 * X0) - 13, PRACTICE))
p.text_px(p.X(X0) + 9, p.Y(0) + 14, FX + "(" + XSUB + ") = " + INT_S + " " + it("f") + "(" + XSUB + ", " + it("y") +
          ") d" + it("y") + " = 2" + XSUB, PRACTICE, 10.5, "start")

# left strip: the marginal of Y, drawn against the same y scale
l = Plot(28, 22, 64, 150, (0, 1.15), (0, 2))
def yfmt_(t):
    return it("y") + subs("0") if abs(t - Y0) < 1e-9 else fmt(t)


l.axes((0, 1), (1, Y0, 2), "", "", yfmt=yfmt_)
l.polygon([(0, 0), (1, 2), (0, 2)], BASE, 0.14)
l.line([(0, 0), (1, 2)], BASE, 2.0)
l.text_px(l.x0 - 2, 14, FY + "(" + it("y") + ") = " + it("y") + "/2", BASE, 11, "start")
guide(l, [(0, Y0), (Y0 / 2, Y0)], BASE, 0.7)
dot(l, (Y0 / 2, Y0), BASE, 3.6)
l.add('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.6"/>'
      % (p.x0 - 3, p.Y(Y0), l.X(Y0 / 2) + 12, p.Y(Y0), BASE))
l.add('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>'
      % (l.X(Y0 / 2) + 6, p.Y(Y0), l.X(Y0 / 2) + 14, p.Y(Y0) - 3.5, l.X(Y0 / 2) + 14, p.Y(Y0) + 3.5, BASE))
l.text_px(l.x0 + l.w / 2 + 6, 214, it("x") + " boyunca topla", BASE, 9.5, "middle", False, True)
l.text_px(l.x0 + l.w / 2 + 6, 228, FY + "(" + it("y") + subs("0") + ") = " + it("y") + subs("0") + "/2", BASE, 9.5, "middle")
OUT["marjinal-projeksiyon"] = figure(
    400, 262, [l, p, b],
    "Marjinal yoğunluk, öteki değişkeni integralle yok ederek bulunur. Ortadaki dikdörtgen "
    "<em>f</em>(<em>x</em>, <em>y</em>) = <em>xy</em> ortak yoğunluğunun tanım bölgesidir; köşeye doğru koyulaşan "
    "gölge ve <em>xy</em> = sabit düzey eğrileri yoğunluğun büyüdüğü yönü gösterir. <em>x</em> = <em>x</em><sub>0</sub> "
    "düşey şeridi üzerinde <em>y</em>'ye göre integral alınınca alttaki eğrinin bir noktası, "
    "<em>f<sub>X</sub></em>(<em>x</em><sub>0</sub>) = 2<em>x</em><sub>0</sub>, çıkar; <em>y</em> = <em>y</em><sub>0</sub> "
    "yatay şeridi üzerinde <em>x</em>'e göre integral almak da soldaki <em>f<sub>Y</sub></em>(<em>y</em>) = <em>y</em>/2 "
    "eğrisinin bir noktasını verir.",
    aria="Dikdortgen bolge uzerinde f(x,y)=xy yogunlugu, x=x0 dusey seridi, altta f_X(x)=2x egrisi ve "
         "seritten f_X(x0) noktasina ok, solda f_Y(y)=y/2 egrisi")

# ============================================================ mgf-turev-moment
# Moment generating function of the exponential(1) law, M(t) = 1/(1 - t): the value 1 at t = 0,
# the tangent there with slope E(X) = 1, and the vertical asymptote at t = 1.
def it(s):
    return '<tspan font-style="italic">%s</tspan>' % s


def M(t):
    return 1 / (1 - t)


DPRIME = "&#8243;"
MT = it("M") + "(" + it("t") + ")"

p = Plot(48, 26, 306, 206, (-1.65, 1.2), (-0.35, 2.7))
p.origin_axes("t", "M", xticks=(-1, 1), yticks=(2,))
# tangent at t = 0: y = 1 + t
p.line([(-1.25, -0.25), (0.8, 1.8)], PRACTICE, 1.7, "6 4", 0.9)
# vertical asymptote t = 1
p.line([(1, -0.3), (1, 2.65)], TEXT, 1.2, "5 4", 0.55)
p.add('<text transform="translate(%.1f,%.1f) rotate(-90)" fill="%s" font-size="10.5" text-anchor="middle" '
      'opacity="0.85">düşey asimptot, %s = 1</text>' % (p.X(1) - 6, p.Y(2.15), TEXT, it("t")))
# the curve itself, cut where it leaves the panel
clipped(p, M, -1.6, 0.66, THEORY, 2.2, 500)
p.label(0.36, M(0.36), MT + " = 1/(1 " + MINUS_S + " " + it("t") + ")", -8, -2, THEORY, 11, "end", True)
# M(0) = 1
dot(p, (0, 1), THEORY, 4.4)
p.label(0, 1, it("M") + "(0) = 1", -8, -4, THEORY, 10.5, "end", True)
p.label(0.93, 0.78, "teğet,", 0, 0, PRACTICE, 10.5, "end", False, True)
p.label(0.93, 0.55, "eğim " + it("E") + "(" + it("X") + ") = 1", 0, 0, PRACTICE, 10.5, "end", False, True)
# what the derivatives at 0 read off — notes in the empty upper-left corner
X0, Y0 = p.X(-1.6), p.Y(2.55)
p.text_px(X0, Y0, "üstel(1) için " + it("M") + "(" + it("t") + ") = 1/(1 " + MINUS_S + " " + it("t") + "),  " + it("t") + " &lt; 1", TEXT, 10.5)
p.text_px(X0, Y0 + 20, it("M") + "(0) = 1", THEORY, 10.5, "start", True)
p.text_px(X0, Y0 + 40, it("M") + PRIME + "(0) = " + it("E") + "(" + it("X") + ") = 1", PRACTICE, 10.5, "start", True)
p.text_px(X0, Y0 + 60, it("M") + DPRIME + "(0) = " + it("E") + "(" + it("X") + sups("2") + ") = 2", THEORY, 10.5, "start", True)
p.text_px(X0, Y0 + 80, "Var(" + it("X") + ") = 2 " + MINUS_S + " 1" + sups("2") + " = 1", TEXT, 10.5)

OUT["mgf-turev-moment"] = figure(
    400, 255, [p],
    "Üstel dağılımın moment üreten fonksiyonu <em>M</em>(<em>t</em>) = 1/(1 &#8722; <em>t</em>), yalnız "
    "<em>t</em> &lt; 1 için tanımlıdır ve <em>t</em> = 1'de sonsuza gider. Her moment üreten fonksiyon gibi "
    "<em>M</em>(0) = 1'dir; <em>t</em> = 0'daki teğetin eğimi <em>M</em>&#8242;(0) = <em>E</em>(<em>X</em>) = 1, "
    "eğrilik ise <em>M</em>&#8243;(0) = <em>E</em>(<em>X</em><sup>2</sup>) = 2 verir. Momentler, tek bir "
    "fonksiyonun sıfırdaki türevlerinden okunur.",
    aria="Ustel dagilimin moment ureten fonksiyonu 1/(1-t) egrisi, t = 0 noktasinda degeri 1 ve egimi 1 olan teget, t = 1 dusey asimptot; turevlerin momentleri verdigi notlar")

# ============================================================ monoton-donusum
# Distribution-function technique for a monotone g: solving g(x) <= y on the x-axis, increasing vs decreasing.
INV = "&#8315;&#185;"
GINV = "g" + INV + "(y)"
FX = "F" + subs("X")
FY = "F" + subs("Y")


def g_up(x):
    return 0.15 * x * x + 0.4 * x + 0.4


def g_down(x):
    return 4.4 - 0.4 * x - 0.15 * x * x


YL = 2.4
XS = (-0.4 + math.sqrt(0.16 + 1.2)) / 0.3      # g_up(XS) = YL = g_down(XS)
XMIN, XMAX, YMIN, YMAX = -0.3, 4.7, -1.0, 5.2


def panel(x0, g, up):
    p = Plot(x0, 30, 226, 190, (XMIN, XMAX), (YMIN, YMAX))
    p.origin_axes("x", "y")
    panel_title(p, "g artan" if up else "g azalan", THEORY)
    # the solution set of g(x) <= y on the x-axis
    a, b = ((XMIN, XS) if up else (XS, XMAX - 0.15))
    p.line([(a, 0), (b, 0)], PRACTICE, 6.0, None, 0.35)
    dot(p, (XS, 0), PRACTICE, 3.8)
    # the level y and the pre-image point
    guide(p, [(XMIN, YL), (XS, YL)], PRACTICE, 0.8)
    guide(p, [(XS, 0), (XS, YL)], PRACTICE, 0.8)
    dot(p, (XS, YL), THEORY, 4.0)
    p.label(XMIN, YL, "y", -5, 4, PRACTICE, 11.5, "end", True, True)
    curve(p, g, 0.0, 4.35, THEORY, 2.2, 160)
    p.label(XS, 0, GINV, 0, 15, PRACTICE, 11, "middle", True, True)
    if up:
        p.label((a + b) / 2 - 0.15, 0, "x " + LEQ_S + " " + GINV, 0, 30, PRACTICE, 11, "middle", False, True)
        p.label(3.3, 1.35, "g(x) " + LEQ_S + " y", 0, 0, THEORY, 11, "middle", False, True)
        p.label(0.5, 4.45, FY + "(y) = " + FX + "(" + GINV + ")", 0, 0, THEORY, 11.5, "start", True, True)
        p.label(4.3, g(4.3), "g", -10, 2, THEORY, 12, "end", True, True)
    else:
        p.label((a + b) / 2 + 0.15, 0, "x " + GEQ_S + " " + GINV, 0, 30, PRACTICE, 11, "middle", False, True)
        p.label(1.15, 1.35, "g(x) " + LEQ_S + " y", 0, 0, THEORY, 11, "middle", False, True)
        p.label(4.55, 4.45, FY + "(y) = 1 " + MINUS_S + " " + FX + "(" + GINV + ")", 0, 0, THEORY, 11.5, "end", True, True)
        p.label(1.5, g(1.5), "g", 9, -6, THEORY, 12, "start", True, True)
    return p


p1 = panel(44, g_up, True)
p2 = panel(322, g_down, False)
OUT["monoton-donusum"] = figure(
    560, 245, [p1, p2],
    "Dağılım fonksiyonu tekniğinin özü <em>g</em>(<em>x</em>) &#8804; <em>y</em> eşitsizliğini "
    "<em>x</em> için çözmektir. <em>g</em> artan ise çözüm kümesi <em>g</em><sup>&#8722;1</sup>(<em>y</em>)'nin "
    "solundaki yarı doğrudur ve <em>F<sub>Y</sub></em>(<em>y</em>) = <em>F<sub>X</sub></em>(<em>g</em><sup>&#8722;1</sup>(<em>y</em>)); "
    "<em>g</em> azalan ise sağındaki yarı doğrudur ve <em>F<sub>Y</sub></em>(<em>y</em>) = 1 &#8722; "
    "<em>F<sub>X</sub></em>(<em>g</em><sup>&#8722;1</sup>(<em>y</em>)). <em>F<sub>X</sub></em> sürekli olduğundan "
    "uç noktanın dahil olup olmaması sonucu değiştirmez.",
    aria="Solda artan, sagda azalan g egrisi; y duzeyinin altinda kalan x kumesi eksende taranmis ve F_Y'nin F_X cinsinden formulu yazili")

# ============================================================ nokta-olasiligi-sifir
# Why P(X = a) = 0 for a continuous variable: nested intervals [a-h, a+h] with h = 0.5, 0.25, 0.1
# under a bell-shaped density; the area ~ 2h f(a) shrinks to 0 while f(a) stays positive.
A_P = 0.8


def f_bell(x):
    return math.exp(-x * x / 2) / math.sqrt(2 * math.pi)


p = Plot(48, 26, 306, 206, (-2.6, 3.9), (-0.05, 0.47))
p.origin_axes("x", "y", xticks=(2,), yticks=(0.2, 0.4), yfmt=tfmt)
for h, op in ((0.5, 0.14), (0.25, 0.26), (0.1, 0.5)):
    xs = [A_P - h + 2 * h * k / 30 for k in range(31)]
    p.polygon([(A_P - h, 0)] + [(x, f_bell(x)) for x in xs] + [(A_P + h, 0)], PRACTICE, op)
    guide(p, [(A_P - h, 0), (A_P - h, f_bell(A_P - h))], PRACTICE, 0.6)
    guide(p, [(A_P + h, 0), (A_P + h, f_bell(A_P + h))], PRACTICE, 0.6)
curve(p, f_bell, -2.55, 3.85, THEORY, 2.2, 320)
guide(p, [(A_P, 0), (A_P, f_bell(A_P))], TEXT, 0.5)
dot(p, (A_P, f_bell(A_P)), THEORY, 4.0)
p.label(A_P, 0, "a", 0, 15, PRACTICE, 11, "middle", True, True)
p.label(A_P - 0.5, 0, "a" + MINUS_S + "h", 0, 15, PRACTICE, 10, "middle", False, True)
p.label(A_P + 0.5, 0, "a+h", 0, 15, PRACTICE, 10, "middle", False, True)
p.label(A_P, f_bell(A_P), "f(a)", 8, -4, THEORY, 11, "start", True, True)
p.label(1.55, 0.435, "alan " + "&#8776; 2h" + "&#183;" + "f(a)", 0, 0, PRACTICE, 11, "middle", True, True)
p.label(2.85, 0.35, "h " + ARROW + " 0:", 0, 0, TEXT, 11, "middle", True, True)
p.label(2.85, 0.285, "alan " + ARROW + " 0,", 0, 0, PRACTICE, 11, "middle", False, True)
p.label(2.85, 0.22, "P(X = a) = 0", 0, 0, PRACTICE, 11, "middle", True, True)
p.label(2.85, 0.135, "ama f(a) &gt; 0", 0, 0, THEORY, 11, "middle", False, True)
OUT["nokta-olasiligi-sifir"] = figure(
    400, 256, [p],
    "Sürekli bir değişkende tek noktanın olasılığı sıfırdır. <em>a</em> çevresindeki [<em>a</em> &#8722; <em>h</em>, "
    "<em>a</em> + <em>h</em>] aralığının olasılığı eğri altındaki taralı alandır, yaklaşık 2<em>h</em>·<em>f</em>(<em>a</em>); "
    "<em>h</em> küçüldükçe (0,5; 0,25; 0,1) bu alan sıfıra çekilir ve limitte <em>P</em>(<em>X</em> = <em>a</em>) = 0 kalır. "
    "Oysa <em>f</em>(<em>a</em>) sıfır değildir: yoğunluk bir olasılık değil, birim uzunluğa düşen olasılıktır.",
    aria="Can egrisi altinda a noktasi cevresinde ic ice uc daralan aralik; alan sifira giderken f(a) pozitif kalir")

# ============================================================ normal-68-95-99
# Standard normal density with nested one-, two-, three-sigma bands and their probabilities.
def phi_pdf(x):
    return math.exp(-x * x / 2) / math.sqrt(2 * math.pi)


def erf_prob(k):
    # P(|Z| < k) = 2 Phi(k) - 1
    return math.erf(k / math.sqrt(2))


def sig_fmt(v):
    v = int(round(v))
    if v == 0:
        return "&#956;"
    s = "&#956;" + (MINUS_S if v < 0 else "+")
    return s + ("" if abs(v) == 1 else "%d" % abs(v)) + "&#963;"


p = Plot(18, 20, 370, 214, (-3.9, 3.9), (-0.02, 0.70))
# horizontal axis only (no vertical axis, so the bracket labels stay clear)
oy = p.Y(0)
p.add('<g stroke="%s" stroke-width="1.1" opacity="0.5" fill="%s">'
      '<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f"/>'
      '<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" stroke="none"/></g>'
      % (TEXT, TEXT, p.x0 - 4, oy, p.x0 + p.w + 4, oy,
         p.x0 + p.w + 4, oy, p.x0 + p.w - 4, oy - 3.5, p.x0 + p.w - 4, oy + 3.5))
for t in (-3, -2, -1, 0, 1, 2, 3):
    p.add('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1" opacity="0.7"/>'
          % (p.X(t), oy - 3, p.X(t), oy + 3, TEXT))
    p.text_px(p.X(t), oy + 15, sig_fmt(t), TEXT, 11, "middle")


def band(k, op):
    pts = [(-k, 0)] + [(-k + 2 * k * j / 160, phi_pdf(-k + 2 * k * j / 160)) for j in range(161)] + [(k, 0)]
    p.polygon(pts, THEORY, op)


band(3, 0.13)
band(2, 0.17)
band(1, 0.24)
for k in (1, 2, 3):
    guide(p, [(-k, 0), (-k, phi_pdf(k))], THEORY, 0.6)
    guide(p, [(k, 0), (k, phi_pdf(k))], THEORY, 0.6)
curve(p, phi_pdf, -3.85, 3.85, THEORY, 2.1, 360)

# brackets above the curve
for k, y, col in ((1, 0.46, THEORY), (2, 0.55, THEORY), (3, 0.64, THEORY)):
    tick = 0.025
    p.line([(-k, y - tick), (-k, y), (k, y), (k, y - tick)], col, 1.1)
    pct = 100 * erf_prob(k)
    p.label(0, y, "%" + tfmt(round(pct, 1)), 0, -4, col, 11, "middle", True)

OUT["normal-68-95-99"] = figure(
    400, 255, [p],
    "Bir, iki, üç standart sapma kuralı. <em>N</em>(&#956;, &#963;<sup>2</sup>) yoğunluğunun altında iç içe üç "
    "bant: ortalamanın bir standart sapma yakını yüzde 68,3, iki standart sapma yakını yüzde 95,4, üç standart "
    "sapma yakını yüzde 99,7 olasılık taşır. Kuyruklarda kalan toplam olasılık binde üçtür; normal dağılımlı bir "
    "büyüklük ortalamasından üç &#963; uzağa hemen hiç düşmez.",
    aria="Standart normal egri altinda bir, iki ve uc sigma bantlari ve yuzde 68,3, 95,4, 99,7 olasiliklari")

# ============================================================ normal-yogunluk
# Normal densities with different spreads, and the standard normal with Phi(z) shaded.
def phi_pdf(x, s=1.0):
    return math.exp(-x * x / (2 * s * s)) / (s * math.sqrt(2 * math.pi))


p1 = Plot(44, 30, 226, 190, (-4.6, 4.6), (-0.06, 0.88))
p1.origin_axes("x", "y", xticks=(-2, 2), yticks=(0.4, 0.8), yfmt=tfmt)
panel_title(p1, "N(0, &#963;" + sups("2") + ") yoğunlukları", THEORY)
for s, col in ((0.5, PRACTICE), (1.0, THEORY), (2.0, BASE)):
    curve(p1, lambda x, ss=s: phi_pdf(x, ss), -4.5, 4.5, col, 2.0, 360)
p1.label(0.62, phi_pdf(0.62, 0.5), "&#963; = 0,5", 8, -2, PRACTICE, 10.5, "start", False, True)
p1.label(1.15, phi_pdf(1.15, 1.0), "&#963; = 1", 8, 0, THEORY, 10.5, "start", False, True)
p1.label(2.9, phi_pdf(2.9, 2.0), "&#963; = 2", 6, -4, BASE, 10.5, "start", False, True)

Z0 = 1.0
p2 = Plot(322, 30, 226, 190, (-3.7, 3.7), (-0.05, 0.5))
p2.origin_axes("z", "y", xticks=(-2, -1, 2), yticks=(0.2, 0.4), yfmt=tfmt)
panel_title(p2, "standart normal: &#934;(z) alanı", THEORY)
p2.polygon([(-3.6, 0)] + [(-3.6 + (Z0 + 3.6) * k / 200, phi_pdf(-3.6 + (Z0 + 3.6) * k / 200)) for k in range(201)]
           + [(Z0, 0)], THEORY, 0.20)
curve(p2, phi_pdf, -3.6, 3.6, THEORY, 2.1, 360)
guide(p2, [(Z0, 0), (Z0, phi_pdf(Z0))], PRACTICE, 0.8)
p2.label(Z0, 0, "z", 0, 15, PRACTICE, 11, "middle", True, True)
p2.label(-1.0, 0.07, "&#934;(z)", 0, 0, THEORY, 11.5, "middle", True, True)
p2.label(2.2, 0.2, "1 " + MINUS_S + " &#934;(z)", 0, 0, PRACTICE, 10.5, "middle", False, True)
OUT["normal-yogunluk"] = figure(
    560, 244, [p1, p2],
    "Solda sıfır ortalamalı normal yoğunluklar: &#963; küçüldükçe eğri dikleşir ve kütle ortalamaya toplanır; "
    "her eğrinin altındaki alan 1'dir. Sağda standart normal dağılım fonksiyonu &#934;(<em>z</em>) = <em>P</em>(<em>Z</em> &#8804; <em>z</em>), "
    "<em>z</em>'nin solunda kalan alan olarak; simetri gereği &#934;(&#8722;<em>z</em>) = 1 &#8722; &#934;(<em>z</em>).",
    aria="Farkli standart sapmali normal yogunluklar ve standart normal egri altinda Phi(z) alani")

# ============================================================ onimaj-olay
# The preimage (X <= a) of X(w) = w^2 on Omega = [-1, 1]: a subset of Omega that must be an event.
import math

A = 0.45
R = math.sqrt(A)
OMEGA, SQRT = "&#969;", "&#8730;"

p = Plot(46, 24, 318, 200, (-1.45, 1.45), (-0.24, 1.26))
p.origin_axes(OMEGA, "X(" + OMEGA + ")", xticks=(-1, 1), yticks=(1,))
# the sample space Omega = [-1, 1] as a thick segment on the horizontal axis
p.line([(-1, 0), (1, 0)], TEXT, 4.0, None, 0.35)
p.label(0, 0, "&#937; = [" + MINUS_S + "1, 1]", 0, 30, TEXT, 10.5, "middle", False, True)
# level a and the two points where the curve meets it
guide(p, [(-1.25, A), (1.25, A)], PRACTICE, 0.8)
p.label(1.25, A, "a", 6, 4, PRACTICE, 11.5, "start", True, True)
guide(p, [(-R, 0), (-R, A)], PRACTICE, 0.8)
guide(p, [(R, 0), (R, A)], PRACTICE, 0.8)
# the curve X(w) = w^2, defined only on Omega
curve(p, lambda w: w * w, -1, 1, THEORY, 2.2, 200)
dot(p, (-1, 1), THEORY, 3.0)
dot(p, (1, 1), THEORY, 3.0)
p.label(0.98, 1.13, "X(" + OMEGA + ") = " + OMEGA + sups("2"), 0, 0, THEORY, 11.5, "middle", True, True)
# the preimage (X <= a) = [-sqrt a, sqrt a] shaded on the axis
p.line([(-R, 0), (R, 0)], PRACTICE, 6.0, None, 0.9)
dot(p, (-R, A), PRACTICE, 3.6)
dot(p, (R, A), PRACTICE, 3.6)
p.label(-R, 0, MINUS_S + SQRT + "a", 0, 15, PRACTICE, 11, "middle", True, False)
p.label(R, 0, SQRT + "a", 0, 15, PRACTICE, 11, "middle", True, False)
# the note: this set must be an event (a background patch keeps the axis from cutting the text)
rect(p, -0.56, 0.56, 0.615, 0.905, BG, 1.0)
p.label(0, 0.83, "(X " + LEQ_S + " a) = [" + MINUS_S + SQRT + "a, " + SQRT + "a]", 0, 0, PRACTICE, 11.5, "middle", True, True)
p.label(0, 0.68, "bir olay olmalı (U içinde)", 0, 0, TEXT, 10.5, "middle", False, True)
OUT["onimaj-olay"] = figure(
    400, 256, [p],
    "Rastgele değişken koşulunun geometrisi: &#937; = [&#8722;1, 1] üzerinde <em>X</em>(&#969;) = &#969;<sup>2</sup> "
    "alınmıştır. \"<em>X</em> &#8804; <em>a</em>\" sorusu, eğrinin <em>a</em> düzeyinin altında kaldığı "
    "&#969; noktalarını, yani [&#8722;&#8730;<em>a</em>, &#8730;<em>a</em>] aralığını seçer. Tanım, her <em>a</em> "
    "için bu ters görüntünün &#963;-cebir <em>U</em>'nun bir elemanı olmasını ister; burada kapalı aralık bir Borel "
    "kümesi olduğundan koşul sağlanır ve <em>P</em>(<em>X</em> &#8804; <em>a</em>) = &#8730;<em>a</em> olur.",
    aria="Parabol X(omega) = omega kare uzerinde a duzeyi; egrinin a altinda kaldigi omega araligi eksende taranmis")

# ============================================================ oran-toplam-bolge
# Image region of (U1, U2) = (Y2/(Y1+Y2), Y1+Y2) when Y1, Y2 > 1: u2 > max(1/u1, 1/(1-u1)).
YMAX_R = 6.4
U_LO, U_HI = 1.0 / YMAX_R, 1.0 - 1.0 / YMAX_R


def bound(u):
    return max(1.0 / u, 1.0 / (1.0 - u))


p = Plot(56, 30, 300, 196, (-0.06, 1.12), (0.0, YMAX_R + 0.5))
p.axes((0.5, 1.0), (2, 4, 6), "u" + subs("1"), "u" + subs("2"), xfmt=tfmt)
region = [(U_LO, YMAX_R)]
region += [(U_LO + (U_HI - U_LO) * k / 200, bound(U_LO + (U_HI - U_LO) * k / 200)) for k in range(201)]
region += [(U_HI, YMAX_R)]
p.polygon(region, THEORY, 0.20)
clipped(p, lambda u: 1 / u, 0.02, 0.999, PRACTICE, 1.9, 400)
clipped(p, lambda u: 1 / (1 - u), 0.001, 0.98, BASE, 1.9, 400)
guide(p, [(0, 0), (0, YMAX_R + 0.5)], TEXT, 0.45)
guide(p, [(1, 0), (1, YMAX_R + 0.5)], TEXT, 0.45)
guide(p, [(0, 2), (0.5, 2)], TEXT, 0.45)
guide(p, [(0.5, 0), (0.5, 2)], TEXT, 0.45)
dot(p, (0.5, 2), TEXT, 4.0)
p.label(0.5, 2, "(1/2, 2)", 8, 14, TEXT, 10.5, "start", True, True)
p.label(0.5, 4.75, "E", 0, 0, THEORY, 15, "middle", True, True)
p.label(0.5, 4.1, "E bir dikdörtgen değildir", 0, 0, THEORY, 10, "middle", False, True)
p.label(0.5, 6.1, "yukarıya doğru sınırsız", 0, 0, TEXT, 9.5, "middle", False, True)
p.label(0.175, 5.9, "u" + subs("2") + " = 1/u" + subs("1"), -4, 0, PRACTICE, 10.5, "end", False, True)
p.label(0.845, 5.9, "u" + subs("2") + " = 1/(1 &#8722; u" + subs("1") + ")", 4, 0, BASE, 10.5, "start", False, True)
p.label(0.5, 1.05, "her noktada u" + subs("2") + " &gt; 2", 0, 0, TEXT, 10, "middle", False, True)
OUT["oran-toplam-bolge"] = figure(
    420, 258, [p],
    "<em>Y</em><sub>1</sub>, <em>Y</em><sub>2</sub> &gt; 1 bölgesinin <em>U</em><sub>1</sub> = "
    "<em>Y</em><sub>2</sub>/(<em>Y</em><sub>1</sub> + <em>Y</em><sub>2</sub>), <em>U</em><sub>2</sub> = "
    "<em>Y</em><sub>1</sub> + <em>Y</em><sub>2</sub> dönüşümü altındaki görüntüsü. İki sınır eğrisi "
    "(1/2, 2) noktasında kesişir; <em>E</em>, ikisinin de üstünde kalan bölgedir ve her noktasında "
    "<em>u</em><sub>2</sub> &gt; 2'dir. <em>E</em> iki aralığın çarpımı olmadığından &#8212; "
    "<em>u</em><sub>1</sub>'in alabileceği değerler <em>u</em><sub>2</sub>'ye bağlıdır &#8212; "
    "<em>U</em><sub>1</sub> ile <em>U</em><sub>2</sub> bağımsız olamaz.",
    aria="u1 u2 duzleminde 1/u1 ve 1/(1-u1) egrilerinin ustunde kalan taranmis bolge; egriler (1/2, 2) noktasinda kesisiyor")

# ============================================================ ornek-uzay-turleri
# Three kinds of sample space: finite (two dice, 36 outcomes), countably infinite
# (toss until the first head), uncountable (temperature in (-10, 35)).

# --- left: finite, a 6 x 6 grid of outcomes ---------------------------------
p1 = Plot(46, 40, 130, 130, (0.4, 6.6), (0.4, 6.6))          # equal aspect
panel_title(p1, "sonlu: iki zar, 36 sonuç", THEORY, 11)
p1.axes(range(1, 7), range(1, 7))
p1.points([(i, j) for i in range(1, 7) for j in range(1, 7) if (i, j) != (6, 6)], THEORY, 3.4)
dot(p1, (6, 6), PRACTICE, 3.6)
p1.text_px(p1.x0 + p1.w / 2, p1.y0 + p1.h + 31, "birinci zar", TEXT, 10.5, "middle", False, True)
p1.add('<text x="%.1f" y="%.1f" fill="%s" font-size="10.5" font-style="italic" text-anchor="middle" '
       'transform="rotate(-90 %.1f %.1f)">ikinci zar</text>'
       % (p1.x0 - 24, p1.y0 + p1.h / 2, TEXT, p1.x0 - 24, p1.y0 + p1.h / 2))
p1.label(6, 6, "&#969; = (6, 6)", 5, -9, PRACTICE, 9.5, "end", False, True)

# --- middle: countably infinite, points 1, 2, 3, ... on a number line ---------
p2 = Plot(214, 40, 156, 130, (0.3, 6.7), (-0.8, 1.2))
panel_title(p2, "sayılabilir sonsuz: ilk tura", THEORY, 11)
p2.arrow((0.3, 0), (6.7, 0), TEXT, 1.1, 7.0, opacity=0.6)
SEQ = ["T", "YT", "YYT", "YYYT", "YYYYT"]
for n in range(1, 6):
    col = PRACTICE if n == 3 else THEORY
    dot(p2, (n, 0), col, 4.0)
    p2.label(n, 0, "&#969;" + subs(str(n)), 0, 17, TEXT, 10.5, "middle", False, True)
    p2.label(n, 0, SEQ[n - 1], 0, -11 if n % 2 else -24, col, 9.5, "middle", False, False)
p2.label(6.05, 0, "&#8230;", 0, 4, TEXT, 13, "middle", True, False)
p2.text_px(p2.x0 + p2.w / 2, p2.y0 + p2.h + 8, "kaçıncı atışta tura geldi: 1, 2, 3, &#8230;",
           TEXT, 10.5, "middle", False, True)
p2.text_px(p2.x0 + p2.w / 2, p2.y0 + p2.h + 24, "&#937; = {&#969;" + subs("1") + ", &#969;" + subs("2")
           + ", &#969;" + subs("3") + ", &#8230;}", TEXT, 10.5, "middle", False, False)

# --- right: uncountable, the open interval (-10, 35) ------------------------
p3 = Plot(400, 40, 156, 130, (-20, 45), (-0.8, 1.2))
panel_title(p3, "sayılamaz: sıcaklık", THEORY, 11)
p3.line([(-20, 0), (45, 0)], TEXT, 1.0, None, 0.35)
p3.line([(-10, 0), (35, 0)], THEORY, 4.0)
hollow(p3, (-10, 0), THEORY, 4.0, 1.6)
hollow(p3, (35, 0), THEORY, 4.0, 1.6)
for t in (-10, 0, 35):
    p3.line([(t, -0.05), (t, 0.05)], TEXT, 1.0, None, 0.6)
    p3.label(t, 0, (MINUS_S + "10") if t == -10 else str(t), 0, 18, TEXT, 10.5, "middle")
dot(p3, (21.7, 0), PRACTICE, 3.6)
p3.label(21.7, 0, "&#969; = 21,7", 0, -11, PRACTICE, 10.5, "middle", False, True)
p3.text_px(p3.x0 + p3.w / 2, p3.y0 + p3.h + 8, "&#969; bu aralıkta herhangi bir sayı", TEXT, 10.5, "middle", False, True)
p3.text_px(p3.x0 + p3.w / 2, p3.y0 + p3.h + 24, "&#937; = (" + MINUS_S + "10, 35), derece", TEXT, 10.5, "middle")

OUT["ornek-uzay-turleri"] = figure(
    570, 236, [p1, p2, p3],
    "Üç tür örnek uzay. Solda iki zar atıldığında sonuç bir sayı çifti, örnek uzay ise 6 &#215; 6 = 36 noktalık "
    "sonlu bir kümedir. Ortada para tura gelinceye kadar atılır; sonuçlar &#969;<sub>1</sub> = T, "
    "&#969;<sub>2</sub> = YT, &#969;<sub>3</sub> = YYT, &#8230; diye sayılarak sonsuza dek sürer, örnek uzay "
    "sayılabilir sonsuzdur. Sağda yarınki sıcaklık (&#8722;10, 35) aralığındaki herhangi bir gerçel sayı "
    "olabilir; bu örnek uzay sayılamazdır ve olaylar aralıklar ile onların birleşimleridir.",
    css_class=WIDE,
    aria="Uc ornek uzay: iki zar icin 6x6 nokta izgarasi, ilk tura icin sayi dogrusunda sonsuz nokta dizisi, "
         "sicaklik icin (-10, 35) araligi")

# ============================================================ ortak-yogunluk-dikdortgen
# Uniform joint density on D = (0,2) x (2,4): the triangle X + Y <= 3 and the square X <= 1, Y <= 3.
K = 76                                     # pixels per data unit on both axes (equal aspect)
XR, YR = (-0.3, 2.6), (1.7, 4.3)


def it(s):
    """Italic variable name inside an SVG <text>."""
    return '<tspan font-style="italic">%s</tspan>' % s


p = Plot(30, 30, (XR[1] - XR[0]) * K, (YR[1] - YR[0]) * K, XR, YR)
p.axes((0, 1, 2), (2, 3, 4), "x", "y")
# the support D of the density, lightly shaded, with its outline
rect(p, 0, 2, 2, 4, THEORY, 0.14, THEORY, 1.4)
# the event X <= 1, Y <= 3: dashed guides through x = 1 and y = 3 down to the axes
guide(p, [(1, 1.7), (1, 3)], BASE, 0.9, 1.3)
guide(p, [(-0.3, 3), (1, 3)], BASE, 0.9, 1.3)
# the event X + Y <= 3 inside D: the triangle with vertices (0,2), (1,2), (0,3)
p.polygon([(0, 2), (1, 2), (0, 3)], PRACTICE, 0.45)
p.line([(-0.3, 3.3), (1.3, 1.7)], PRACTICE, 1.9)
dot(p, (1, 2), PRACTICE, 3.0)
dot(p, (0, 3), PRACTICE, 3.0)
# labels
p.label(1 / 3, 7 / 3, "1/8", 0, 4, PRACTICE, 11, "middle", True)
p.label(1.22, 1.84, it("x") + " + " + it("y") + " = 3", 0, 0, PRACTICE, 11)
p.label(0.1, 3.88, "D", 0, 0, THEORY, 12, "start", True, True)
p.label(1.45, 3.5, it("f") + " = 1/4", 0, 4, THEORY, 12, "middle")
# legend in the free strip to the right of the panel
lx = p.x0 + p.w + 18
p.add('<rect x="%.1f" y="%.1f" width="11" height="11" fill="%s" fill-opacity="0.45" stroke="%s" stroke-width="1.2"/>'
      % (lx, 64, PRACTICE, PRACTICE))
p.text_px(lx + 17, 74,it("P") + "(" + it("X") + " + " + it("Y") + " " + LEQ_S + " 3) = 1/8", PRACTICE, 10.5)
p.add('<rect x="%.1f" y="%.1f" width="11" height="11" fill="none" stroke="%s" stroke-width="1.3" stroke-dasharray="3 2"/>'
      % (lx, 88, BASE, ))
p.text_px(lx + 17, 98,it("P") + "(" + it("X") + " " + LEQ_S + " 1, " + it("Y") + " " + LEQ_S + " 3) = 1/4", BASE, 10.5)
OUT["ortak-yogunluk-dikdortgen"] = figure(
    400, 256, [p],
    "Dikdörtgen üzerinde sabit ortak yoğunluk. Açık taralı <em>D</em> = (0, 2) &#215; (2, 4) dikdörtgeni "
    "yoğunluğun 1/4 değerini aldığı bölgedir; <em>D</em> içindeki bir bölgenin olasılığı, alanının 4'e oranıdır. "
    "<em>x</em> + <em>y</em> = 3 doğrusunun altında kalan koyu üçgenin alanı 1/2 olduğundan "
    "<em>P</em>(<em>X</em> + <em>Y</em> &#8804; 3) = 1/8; kesikli çizgilerle sınırlanan (0, 1] &#215; (2, 3] karesinin "
    "alanı 1 olduğundan <em>P</em>(<em>X</em> &#8804; 1, <em>Y</em> &#8804; 3) = 1/4.",
    aria="Dikdortgen uzerinde sabit ortak yogunluk: (0,2)x(2,4) dikdortgeni, x+y=3 dogrusu ve altinda kalan "
         "ucgen ile x=1, y=3 kesikli cizgileri")

# ============================================================ ortak-yogunluk-ucgen-bolge
# Two typical supports of a joint density: 0 < y < x < 1 and x + y < 1 in the unit square.
def region_panel(px, title, tri, note, xs_line):
    q = Plot(px, 30, 200, 190, (-0.18, 1.3), (-0.18, 1.3))
    q.origin_axes("x", "y", xticks=(1,), yticks=(1,))
    q.polygon([(0, 0), (1, 0), (1, 1), (0, 1)], TEXT, 0.0, TEXT, 0.9, "4 3")
    q.polygon(tri, THEORY, 0.24, THEORY, 1.4)
    guide(q, xs_line, PRACTICE, 0.9, 1.6)
    q.label(0.5, 1.15, title, 0, 0, THEORY, 11.5, "middle", True, True)
    q.label(note[0], note[1], note[2], 0, 0, PRACTICE, 10.5, "middle", False, True)
    return q


p1 = region_panel(44, "0 &lt; y &lt; x &lt; 1", [(0, 0), (1, 0), (1, 1)],
                  (0.62, -0.12, "x sabit: y, 0'dan x'e"), [(0.62, 0), (0.62, 0.62)])
p1.label(0.75, 0.25, "D", 0, 0, THEORY, 12, "middle", True, True)
p2 = region_panel(322, "x + y &lt; 1", [(0, 0), (1, 0), (0, 1)],
                  (0.4, -0.12, "x sabit: y, 0'dan 1 " + MINUS_S + " x'e"), [(0.4, 0), (0.4, 0.6)])
p2.label(0.28, 0.28, "D", 0, 0, THEORY, 12, "middle", True, True)
OUT["ortak-yogunluk-ucgen-bolge"] = figure(
    560, 244, [p1, p2],
    "Ortak yoğunluğun sıfırdan farklı olduğu bölge <em>D</em>, marjinal ve koşullu yoğunlukları hesaplarken "
    "integral sınırlarını belirler. Solda <em>D</em> = {0 &lt; <em>y</em> &lt; <em>x</em> &lt; 1}: sabit bir "
    "<em>x</em> için <em>y</em>, 0'dan <em>x</em>'e gider. Sağda <em>D</em> = {<em>x</em> + <em>y</em> &lt; 1}: "
    "<em>y</em>, 0'dan 1 &#8722; <em>x</em>'e gider. Her iki bölge de birim karenin yarısıdır.",
    aria="Birim kare icinde iki ucgen bolge: y kucuk x ve x arti y kucuk 1; sabit x icin dikey kesit cizgisi")

# ============================================================ para-silindir-modeller
# A coin of radius 1 falls flat on the base (radius 3) of a cylinder. Left: the length model
# that only records the distance d = |OM| in [0, 2]. Right: the area model, where the coin's
# centre M is uniform on the disk d <= 2 and the coin covers O exactly when d <= 1.
R_BASE, R_COIN = 3.0, 1.0
R_CENT = R_BASE - R_COIN          # the centre may fall anywhere in the disk of radius 2

# ---- left panel: the length model ------------------------------------------
p1 = Plot(26, 22, 176, 200, (-0.3, 2.45), (-1.15, 1.05))
panel_title(p1, "uzunluk modeli (yanlış)", TEXT)
rect(p1, 0, 1, -0.1, 0.1, PRACTICE, 0.22)
p1.line([(0, 0), (2, 0)], TEXT, 1.6)
p1.line([(0, 0), (1, 0)], PRACTICE, 3.2)
for t in (0, 1, 2):
    p1.line([(t, -0.09), (t, 0.09)], TEXT, 1.4)
    p1.label(t, 0, str(t), 0, 19, TEXT, 10.5, "middle")
p1.label(2, 0, "d", 12, 4, TEXT, 11.5, "start", False, True)
p1.label(0.5, 0, "A" + subs("1") + " = [0, 1]", 0, -10, PRACTICE, 11, "middle", True, True)
p1.label(1, 0.38, "&#937;" + subs("1") + " = [0, 2]", 0, -10, TEXT, 11, "middle", False, True)
p1.label(1, -0.5, "P" + subs("1") + "(A" + subs("1") + ") = uzunluk oranı", 0, 0, PRACTICE, 10.5, "middle", False, True)
p1.label(1, -0.8, "= 1/2", 0, 0, PRACTICE, 11.5, "middle", True, True)

# ---- right panel: the area model (equal aspect: 30 px per unit) -------------
p2 = Plot(226, 22, 326, 210, (-3.55, 7.32), (-3.5, 3.5))
panel_title(p2, "alan modeli (doğru)", TEXT)
# the base, the region of the centre, and the covering event
p2.circle(0, 0, R_BASE, TEXT, 1.6)
disk_fill(p2, 0, 0, R_CENT, THEORY, 0.14)
p2.circle(0, 0, R_CENT, THEORY, 1.2, "4 3")
disk_fill(p2, 0, 0, R_COIN, PRACTICE, 0.35)
p2.circle(0, 0, R_COIN, PRACTICE, 1.4)
dot(p2, (0, 0), TEXT, 3.4)
p2.label(0, 0, "O", 5, -5, TEXT, 11, "start", True, True)

# a coin touching the wall: its centre is on the dashed circle d = 2
ang = math.radians(135)
MX, MY = R_CENT * math.cos(ang), R_CENT * math.sin(ang)
p2.circle(MX, MY, R_COIN, BASE, 1.8)
disk_fill(p2, MX, MY, R_COIN, BASE, 0.12)
dot(p2, (MX, MY), BASE, 3.4)
p2.label(MX, MY, "M", -6, 4, BASE, 11, "end", True, True)
p2.line([(0, 0), (MX, MY)], BASE, 1.2)
p2.label(0.75 * MX, 0.75 * MY, "d", -9, 9, BASE, 11, "middle", False, True)

# radius of the base, marked along the negative x axis... below the coin
p2.line([(0, 0), (0, -R_BASE)], TEXT, 1.0, "3 3", 0.6)
p2.label(0, -2.55, "R = 3", 5, 4, TEXT, 10, "start", False, True)

# legend on the right
LX = 3.45
p2.label(LX, 2.25, "taban: yarıçap 3", 0, 0, TEXT, 10.5, "start", False, True)
p2.label(LX, 1.55, "para: yarıçap 1, merkezi M", 0, 0, BASE, 10.5, "start", False, True)
p2.label(LX, 0.6, "&#937;" + subs("2") + ": d " + LEQ_S + " 2 (merkezin bölgesi)", 0, 0, THEORY, 10.5, "start", False, True)
p2.label(LX, -0.35, "A" + subs("2") + ": d " + LEQ_S + " 1 (O örtülür)", 0, 0, PRACTICE, 10.5, "start", False, True)
p2.label(LX, -1.45, "P" + subs("2") + "(A" + subs("2") + ") = alan oranı", 0, 0, PRACTICE, 10.5, "start", False, True)
p2.label(LX, -2.2, "= " + "&#960;" + "&#183;1" + sups("2") + " / " + "&#960;" + "&#183;2" + sups("2") + " = 1/4", 0, 0, PRACTICE, 11.5, "start", True, True)

OUT["para-silindir-modeller"] = figure(
    560, 245, [p1, p2],
    "Yarıçapı 1 olan para, taban yarıçapı 3 olan silindirin tabanına düşüyor; paranın merkezi <em>M</em> "
    "taban merkezine <em>d</em> &#8804; 2 uzaklıkta kalır ve merkez ancak <em>d</em> &#8804; 1 iken örtülür. "
    "Solda yalnızca <em>d</em> uzaklığını kaydeden uzunluk modeli, [0, 1] aralığının [0, 2] içindeki payı "
    "olarak 1/2 verir. Sağda paranın merkezinin düşebileceği bölge (kesikli disk) ve merkezin örtüldüğü "
    "bölge (turuncu disk) görülür; şansın alanla orantılı olduğu doğru modelde olasılık alan oranı 1/4'tür. "
    "Fark, merkezden uzak konumların yakın konumlardan daha çok yer kaplamasından gelir.",
    css_class=WIDE,
    aria="Solda d uzakliginin [0,2] sayi dogrusunda [0,1] araligi taranmis; sagda yaricapi 3 taban, merkezin dusebilecegi yaricapi 2 disk, yaricapi 1 ortme bolgesi ve duvara degen bir para")

# ============================================================ paralelkenar-donusum
# The linear change of variables y1 = x1 + x2, y2 = x1 carries the unit square D
# onto the parallelogram E = {0 < y2 < 1, y2 < y1 < y2 + 1}. Both panels share the
# same pixels-per-unit scale so the two unit areas compare by eye.


def var(name, sub):
    """Italic variable with a subscript, e.g. y1."""
    return '<tspan font-style="italic">%s</tspan>%s' % (name, subs(sub))


def rotated(p, x, y, s, angle, dx=0, dy=0, color=TEXT, size=10):
    """Text centred at a data point, nudged by (dx, dy) pixels, rotated about its anchor."""
    px, py = p.X(x) + dx, p.Y(y) + dy
    p.add('<text x="%.1f" y="%.1f" fill="%s" font-size="%s" text-anchor="middle" '
          'transform="rotate(%d %.1f %.1f)">%s</text>' % (px, py, color, size, angle, px, py, s))


def corner(p, pt, letter, dx, dy, anchor):
    """A marked vertex with its letter; the same letter names the image vertex."""
    dot(p, pt, PRACTICE, 3.4)
    p.label(pt[0], pt[1], letter, dx, dy, PRACTICE, 11, anchor, True, True)


# -- left panel: the unit square D ---------------------------------------------------
L = Plot(12, 30, 175, 177, (-0.3, 1.45), (-0.22, 1.55))
L.origin_axes(var("x", "1"), var("x", "2"), xticks=(1,), yticks=(1,))
rect(L, 0, 1, 0, 1, THEORY, 0.18, THEORY, 1.6)
L.label(0.5, 0.5, "D", 0, 4, THEORY, 12.5, "middle", True, True)
corner(L, (0, 0), "P", 6, -6, "start")
corner(L, (1, 0), "Q", -6, -6, "end")
corner(L, (1, 1), "R", -6, 13, "end")
corner(L, (0, 1), "S", 6, 13, "start")
L.label(0.5, 0, var("x", "2") + " = 0", 0, 15, TEXT, 10, "middle")
L.label(0.5, 1, var("x", "2") + " = 1", 0, -7, TEXT, 10, "middle")
rotated(L, 0, 0.5, var("x", "1") + " = 0", -90, -6, 0)
rotated(L, 1, 0.5, var("x", "1") + " = 1", -90, 14, 0)
panel_title(L, 'Birim kare <tspan font-style="italic">D</tspan>')

# -- the map itself, drawn in the gap between the panels ------------------------------
def px_to_x(p, px):
    return p.xmin + (px - p.x0) / p.w * (p.xmax - p.xmin)


L.arrow((px_to_x(L, 196), 0.5), (px_to_x(L, 254), 0.5), TEXT, 1.6, 7.0)
L.text_px(225, L.Y(0.5) - 9, var("y", "1") + " = " + var("x", "1") + " + " + var("x", "2"), TEXT, 10, "middle")
L.text_px(225, L.Y(0.5) + 16, var("y", "2") + " = " + var("x", "1"), TEXT, 10, "middle")

# -- right panel: the image E --------------------------------------------------------
R = Plot(263, 30, 275, 177, (-0.3, 2.45), (-0.22, 1.55))
R.origin_axes(var("y", "1"), var("y", "2"), xticks=(1, 2), yticks=(1,))
R.polygon([(0, 0), (1, 0), (2, 1), (1, 1)], THEORY, 0.18, THEORY, 1.6)
R.label(1, 0.5, "E", 0, 4, THEORY, 12.5, "middle", True, True)
corner(R, (0, 0), "P", -6, -5, "end")
corner(R, (1, 1), "Q", 7, 13, "start")
corner(R, (2, 1), "R", 6, -5, "start")
corner(R, (1, 0), "S", -7, -6, "end")
R.label(0.5, 0, var("y", "2") + " = 0", 0, 15, TEXT, 10, "middle")
R.label(1.5, 1, var("y", "2") + " = 1", 0, -7, TEXT, 10, "middle")
rotated(R, 0.5, 0.5, var("y", "1") + " = " + var("y", "2"), -45, -6, -6)
rotated(R, 1.5, 0.5, var("y", "1") + " = " + var("y", "2") + " + 1", -45, 10, 10)
R.label(0.12, 1.3, '|<tspan font-style="italic">J</tspan>| = 1: alan korunur', 0, 0, TEXT, 10, "start")
panel_title(R, 'Paralelkenar <tspan font-style="italic">E</tspan>')

OUT["paralelkenar-donusum"] = figure(
    560, 218, [L, R],
    "<em>Y</em><sub>1</sub> = <em>X</em><sub>1</sub> + <em>X</em><sub>2</sub>, <em>Y</em><sub>2</sub> = <em>X</em><sub>1</sub> "
    "doğrusal dönüşümü birim kare <em>D</em>'yi paralelkenar <em>E</em>'ye taşır. Köşeler "
    "<em>P</em>(0,0) &#8614; (0,0), <em>Q</em>(1,0) &#8614; (1,1), <em>R</em>(1,1) &#8614; (2,1), "
    "<em>S</em>(0,1) &#8614; (1,0) noktalarına gider; <em>D</em>'nin <em>x</em><sub>1</sub> = 0 ve "
    "<em>x</em><sub>1</sub> = 1 kenarları <em>y</em><sub>2</sub> = 0 ve <em>y</em><sub>2</sub> = 1 doğrularına, "
    "<em>x</em><sub>2</sub> = 0 ve <em>x</em><sub>2</sub> = 1 kenarları <em>y</em><sub>1</sub> = <em>y</em><sub>2</sub> ve "
    "<em>y</em><sub>1</sub> = <em>y</em><sub>2</sub> + 1 doğrularına düşer. |<em>J</em>| = 1 olduğundan alan korunur: "
    "iki bölgenin de alanı 1'dir ve <em>E</em> üzerinde yoğunluk 1 kalır.",
    css_class=WIDE,
    aria="Birim karenin dogrusal donusumle paralelkenara tasinmasi; koseler ayni harflerle eslenmis, kenar dogrulari etiketli")

# ============================================================ pascal-ucgeni
# Pascal's triangle, rows 0..6, with the identity C(n+1, r) = C(n, r-1) + C(n, r) shown on
# C(5, 2) = C(4, 1) + C(4, 2) = 4 + 6 = 10, and the row sums 2^n on the right.
# The panel maps data coordinates onto pixels one-to-one (y downwards).
p = Plot(0, 0, 400, 258, (0, 400), (258, 0))

CXC, Y0, DY, DX = 186, 40, 27, 34       # centre x, first-row baseline, row and column spacing
XL, XR = 62, 316                        # the columns of row indices (left) and row sums (right)


def C(n, r):
    return math.comb(n, r)


def pos(n, r):
    """Pixel centre of the entry C(n, r)."""
    return CXC + (r - n / 2) * DX, Y0 + n * DY


HI = {(4, 1), (4, 2)}                   # the two parents, tinted
TARGET = (5, 2)                         # their sum, outlined

for n in range(7):
    for r in range(n + 1):
        x, y = pos(n, r)
        if (n, r) in HI:
            p.add(f'<circle cx="{x}" cy="{y}" r="11" fill="{PRACTICE}" fill-opacity="0.22" stroke="{PRACTICE}" stroke-width="1.2"/>')
        elif (n, r) == TARGET:
            p.add(f'<circle cx="{x}" cy="{y}" r="11" fill="{PRACTICE}" fill-opacity="0.22" stroke="{PRACTICE}" stroke-width="2.2"/>')
        hi = (n, r) in HI or (n, r) == TARGET
        p.text_px(x, y + 4, str(C(n, r)), PRACTICE if hi else TEXT, 11.5 if hi else 11, "middle", hi)
    # row index on the left, row sum on the right
    y = Y0 + n * DY
    p.text_px(XL, y + 4, "n = %d" % n, THEORY, 10.5, "end", False, True)
    p.text_px(XR, y + 4, "2" + sups(str(n)) + " = %d" % 2 ** n, THEORY, 10.5, "start")

# the two short arrows: parents -> sum
tx, ty = pos(*TARGET)
for (n, r) in sorted(HI):
    sx, sy = pos(n, r)
    dx, dy = tx - sx, ty - sy
    L = math.hypot(dx, dy)
    ux, uy = dx / L, dy / L
    p.arrow((sx + ux * 12, sy + uy * 12), (tx - ux * 12.5, ty - uy * 12.5), PRACTICE, 1.6, 6.5)

p.text_px(XR + 26, Y0 - 18, "satır toplamı", THEORY, 10.5, "middle", False, True)
p.text_px(XL - 14, Y0 - 18, "satır", THEORY, 10.5, "middle", False, True)

p.text_px(200, 232, "C(n+1, r) = C(n, r" + MINUS_S + "1) + C(n, r)", THEORY, 11.5, "middle", True, True)
p.text_px(200, 250, "C(5, 2) = C(4, 1) + C(4, 2) = 4 + 6 = 10", PRACTICE, 11, "middle", True)

OUT["pascal-ucgeni"] = figure(
    400, 258, [p],
    "Pascal üçgeninin 0'dan 6'ya kadar olan satırları; <em>n</em>-inci satırda <em>C</em>(<em>n</em>, 0), "
    "&#8230;, <em>C</em>(<em>n</em>, <em>n</em>) binom katsayıları durur. Pascal özdeşliği her sayının, bir üst "
    "satırda sol ve sağ üstündeki iki sayının toplamı olduğunu söyler: vurgulu örnekte "
    "<em>C</em>(5, 2) = <em>C</em>(4, 1) + <em>C</em>(4, 2) = 4 + 6 = 10. Sağdaki toplamlar, binom teoreminin "
    "<em>a</em> = <em>x</em> = 1 hâlinden çıkan &#8721;<sub><em>r</em></sub> <em>C</em>(<em>n</em>, <em>r</em>) = 2<sup><em>n</em></sup> "
    "eşitliğini gösterir.",
    aria="Pascal ucgeni satir 0 ile 6 arasi; 4 ve 6 sayilarindan 10 sayisina oklar Pascal ozdesligini gosterir; sagda satir toplamlari 2 ussu n")

# ============================================================ pmf-den-cdf
# From the probability function to the distribution function (three fair coins, X = number
# of heads): each bar on the left becomes a jump of the same height on the right.
F_VALS = [(0, 1 / 8), (1, 3 / 8), (2, 3 / 8), (3, 1 / 8)]
CUM = [(0, 0.0, 1 / 8), (1, 1 / 8, 4 / 8), (2, 4 / 8, 7 / 8), (3, 7 / 8, 1.0)]


def eighths(v):
    k = round(v * 8)
    return {0: "0", 4: "1/2", 8: "1"}.get(k, "%d/8" % k)


p1 = Plot(46, 30, 222, 186, (-0.7, 3.7), (0.0, 0.47))
p1.axes((0, 1, 2, 3), (1 / 8, 3 / 8), "x", "f(x)", yfmt=eighths)
panel_title(p1, "olasılık fonksiyonu f", PRACTICE)
for x, v in F_VALS:
    p1.bars([(x, v)], PRACTICE, 16, 0.35)
    p1.line([(x, 0), (x, v)], PRACTICE, 2.4)
    dot(p1, (x, v), PRACTICE, 3.6)
    p1.label(x, v, eighths(v), 0, -9, PRACTICE, 10.5, "middle", True)
p1.label(1.5, 0.43, "çubuklar toplamı 1", 0, 0, TEXT, 10.5, "middle", False, True)

p2 = Plot(322, 30, 222, 186, (-0.7, 3.9), (-0.06, 1.12))
p2.axes((0, 1, 2, 3), (1 / 8, 4 / 8, 7 / 8, 1.0), "x", "F(x)", yfmt=eighths)
panel_title(p2, "dağılım fonksiyonu F", THEORY)
guide(p2, [(-0.7, 1.0), (3.9, 1.0)], TEXT, 0.3)
p2.line([(-0.65, 0), (0, 0)], THEORY, 2.0)
for x, lo, hi in CUM:
    nxt = x + 1 if x < 3 else 3.8
    p2.line([(x, hi), (nxt, hi)], THEORY, 2.0)
    guide(p2, [(x, lo), (x, hi)], THEORY, 0.45)
    dot(p2, (x, hi), THEORY, 3.4)
    if x < 3:
        hollow(p2, (x + 1, hi), THEORY, 3.4, 1.4)
    # the jump, measured with the same colour as the bar it comes from
    p2.arrow((x + 0.16, lo + 0.012), (x + 0.16, hi - 0.012), PRACTICE, 1.4, 6.0)
    p2.arrow((x + 0.16, hi - 0.012), (x + 0.16, lo + 0.012), PRACTICE, 1.4, 6.0)
    p2.label(x + 0.16, (lo + hi) / 2, eighths(hi - lo), 8, 4, PRACTICE, 10.5, "start", True)
hollow(p2, (0, 0), THEORY, 3.4, 1.4)
p2.label(0.55, 0.80, "soldan sağa biriktir", 0, 0, THEORY, 10.5, "middle", False, True)
p2.label(2.75, 0.24, "sıçrama = çubuk", 0, 0, PRACTICE, 10.5, "middle", False, True)
# the passage between the panels
p2.text_px(295, 103, "f " + ARROW + " F", TEXT, 12.5, "middle", True, True)
OUT["pmf-den-cdf"] = figure(
    560, 245, [p1, p2],
    "Olasılık fonksiyonundan dağılım fonksiyonuna geçiş; üç para atışında tura sayısı. Soldaki çubuklar "
    "değerleri soldan sağa biriktirilince sağdaki merdiven çıkar: <em>F</em>(1) = 1/8 + 3/8 = 1/2. Her "
    "çubuk, sağda aynı noktadaki sıçramanın yüksekliği olarak yeniden görünür; bu yüzden <em>F</em> "
    "verildiğinde sıçramaları okumak <em>f</em>'yi geri verir.",
    aria="Solda 0,1,2,3 noktalarindaki cubuklar 1/8, 3/8, 3/8, 1/8; sagda ayni yukseklikte sicramalari olan basamakli dagilim fonksiyonu")

# ============================================================ poisson-binom-yaklasim
# B(n; 2/n) bars for n = 5, 20, 100 against Poisson(2) probabilities drawn as hollow points.
LAM = 2


def binom_pmf(n, p, k):
    return math.comb(n, k) * p ** k * (1 - p) ** (n - k)


def pois(lam, k):
    return math.exp(-lam) * lam ** k / math.factorial(k)


panels = []
for i, n in enumerate((5, 20, 100)):
    p = LAM / n
    q = Plot(24 + i * 184, 32, 160, 170, (-0.9, 8.9), (0.0, 0.38))
    q.axes((0, 2, 4, 6, 8), (0.1, 0.2, 0.3), "x", "", yfmt=tfmt)
    panel_title(q, "n = %d, p = %s" % (n, tfmt(p)), THEORY)
    for k in range(0, 9):
        h = binom_pmf(n, p, k) if k <= n else 0.0
        if h > 0.0002:
            q.add('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" fill-opacity="0.5" stroke="%s" stroke-width="0.9"/>'
                  % (q.X(k - 0.36), q.Y(h), q.X(k + 0.36) - q.X(k - 0.36), q.Y(0) - q.Y(h), THEORY, THEORY))
    for k in range(0, 9):
        hollow(q, (k, pois(LAM, k)), PRACTICE, 3.2, 1.5)
    if i == 0:
        lx = q.x0 + q.w - 62
        q.add('<rect x="%.1f" y="%.1f" width="9" height="9" fill="%s" fill-opacity="0.5" stroke="%s" stroke-width="0.9"/>'
              % (lx, q.y0 + 8, THEORY, THEORY))
        q.text_px(lx + 14, q.y0 + 16, "B(n; 2/n)", THEORY, 10, "start", False, True)
        q.add('<circle cx="%.1f" cy="%.1f" r="3.2" fill="%s" stroke="%s" stroke-width="1.5"/>'
              % (lx + 4.5, q.y0 + 27, BG, PRACTICE))
        q.text_px(lx + 14, q.y0 + 31, "Poisson(2)", PRACTICE, 10, "start", False, True)
    panels.append(q)
OUT["poisson-binom-yaklasim"] = figure(
    570, 236, panels,
    "<em>np</em> = &#955; = 2 sabit tutulup <em>n</em> büyütüldüğünde B(<em>n</em>, <em>p</em>) çubukları "
    "Poisson(2) olasılıklarına (içi boş noktalar) yaklaşır. <em>n</em> = 5'te <em>x</em> = 2 çubuğu Poisson "
    "değerinin epey üstünde, <em>x</em> = 0 çubuğu ise altındadır; <em>n</em> = 100'de fark artık gözle "
    "seçilemez. Limitte <em>x</em> = 1 ile <em>x</em> = 2 eşit olasılıklı olur.",
    css_class=WIDE,
    aria="np = 2 sabitken n = 5, 20 ve 100 icin binom cubuklari ve Poisson(2) olasiliklarini gosteren ici bos noktalar")

# ============================================================ poisson-olasilik-fonksiyonu
# Poisson pmf for lambda = 1, 4, 10.
def pois(lam, k):
    return math.exp(-lam) * lam ** k / math.factorial(k)


panels = []
for i, (lam, col) in enumerate(((1, THEORY), (4, BASE), (10, PRACTICE))):
    q = Plot(24 + i * 184, 32, 160, 170, (-0.9, 20.9), (0.0, 0.4))
    q.axes((0, 5, 10, 15, 20), (0.1, 0.2, 0.3), "x", "", yfmt=tfmt)
    panel_title(q, "&#955; = %d" % lam, col)
    for k in range(0, 21):
        h = pois(lam, k)
        if h < 0.0005:
            continue
        q.add('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" fill-opacity="0.55" stroke="%s" stroke-width="0.9"/>'
              % (q.X(k - 0.4), q.Y(h), q.X(k + 0.4) - q.X(k - 0.4), q.Y(0) - q.Y(h), col, col))
    q.label(13.5, 0.325, "E(X) = Var(X) = %d" % lam, 0, 0, col, 10, "middle", False, True)
    panels.append(q)
OUT["poisson-olasilik-fonksiyonu"] = figure(
    570, 236, panels,
    "Poisson olasılık fonksiyonu. &#955; küçükken kütle sıfıra yakın ve sağa çarpık; &#955; büyüdükçe dağılım "
    "&#955; çevresinde simetrikleşir ve normal eğriye benzemeye başlar. Ortalama da varyans da &#955;'dır.",
    css_class=WIDE,
    aria="Lambda 1, 4 ve 10 icin Poisson olasilik fonksiyonu cubuklari")

# ============================================================ poisson-zaman-ekseni
# A Poisson event stream on the time axis [0, 10]: event instants from a deterministic LCG
# (exponential inter-arrival times, rate 2 per unit), unit intervals and their event counts.
def lcg_events(seed, lam=2.0, T=10.0):
    m, a = 2 ** 31 - 1, 48271
    s, t, ev = seed, 0.0, []
    while True:
        s = (a * s) % m
        t += -math.log((s + 0.5) / m) / lam
        if t >= T:
            break
        ev.append(t)
    return ev


EV = lcg_events(23948)
COUNTS = [sum(1 for t in EV if k <= t < k + 1) for k in range(10)]

p = Plot(30, 48, 344, 116, (0.0, 10.0), (0.0, 1.0))
Y_AX = 0.30          # the time axis (data y)
Y_TOP = 0.98         # top of the interval separators
Y_CNT = 0.84         # row of counts
HL = 3               # the highlighted interval [3, 4)

# highlighted interval
rect(p, HL, HL + 1, 0.0, Y_TOP, PRACTICE, 0.12)
# interval separators
for k in range(0, 11):
    p.vline(k, 0.0, Y_TOP, TEXT, "4 3", 0.45)
# time axis with arrowhead
ax_px = p.Y(Y_AX)
p.add('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.2" opacity="0.7"/>'
      % (p.X(0) - 2, ax_px, p.X(10) + 14, ax_px, TEXT))
p.add('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s" opacity="0.7"/>'
      % (p.X(10) + 20, ax_px, p.X(10) + 12, ax_px - 3.5, p.X(10) + 12, ax_px + 3.5, TEXT))
p.text_px(p.X(10) + 22, ax_px + 4, "t", TEXT, 11.5, "start", False, True)
for k in range(0, 11):
    p.text_px(p.X(k), ax_px + 16, str(k), TEXT, 10.5, "middle")
# events: a thin stem and a filled dot on the axis
for t in EV:
    p.add('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1" opacity="0.55"/>'
          % (p.X(t), ax_px, p.X(t), p.Y(Y_AX + 0.22), THEORY))
    p.add('<circle cx="%.1f" cy="%.1f" r="2.7" fill="%s"/>' % (p.X(t), ax_px, THEORY))
# counts above each interval
for k in range(10):
    bold = (k == HL)
    p.label(k + 0.5, Y_CNT, str(COUNTS[k]), 0, 4, PRACTICE, 12 if bold else 11, "middle", bold)
# header row and the highlighted interval's name
p.text_px(p.X(0) - 2, p.y0 - 18, "her birim aralıktaki olay sayısı", PRACTICE, 10.5, "start", False, True)
p.text_px(p.X(10) + 2, p.y0 - 18, "olay anları", THEORY, 10.5, "end", False, True)
p.text_px(p.X(HL + 0.5), ax_px + 32, "[3, 4)", PRACTICE, 10.5, "middle", False, True)
# lesson lines
p.text_px(200, 198, "birim zamandaki olay sayısı ~ Poisson(&#955;)", PRACTICE, 11.5, "middle", False, True)
p.text_px(200, 219, "ayrık aralıklar: bağımsız sayımlar, aralık uzunluğu t ise Poisson(&#955;t)", TEXT, 10.5, "middle", False, True)
p.text_px(200, 238, "(çizimde birim zamanda ortalama 2 olay; %d aralıkta toplam %d olay)" % (10, len(EV)), TEXT, 9.5, "middle", False, True)

OUT["poisson-zaman-ekseni"] = figure(
    400, 255, [p],
    "Zaman ekseni üzerinde bir Poisson süreci: mavi noktalar olay anlarıdır, kesikli çizgiler ekseni birim "
    "aralıklara böler ve turuncu sayılar her aralıktaki olay sayısını verir. Her birim aralıktaki sayım aynı "
    "Poisson(&#955;) dağılımına sahiptir; ayrık aralıklardaki sayımlar bağımsızdır ve uzunluğu <em>t</em> olan "
    "bir aralıktaki sayım Poisson(&#955;<em>t</em>) dağılımlıdır. Çağrı merkezi örneğindeki "
    "\"<em>t</em> dakikada Poisson(3<em>t</em>)\" modeli tam olarak bu tablodur.",
    aria="Zaman ekseninde olay anlari, birim araliklara bolunmus eksen ve her araliktaki olay sayilari")

# ============================================================ rastgele-degisken-sema
# A random variable as a map: the eight outcomes of three coin tosses sent to the number line.
p = Plot(20, 18, 520, 214, (0, 10), (-0.55, 6.0))
OUTC = [("YYY", 0), ("YYT", 1), ("YTY", 1), ("TYY", 1), ("YTT", 2), ("TYT", 2), ("TTY", 2), ("TTT", 3)]
# the sample space as an ellipse on the left
p.add('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s" fill-opacity="0.06" stroke="%s" stroke-width="1.2"/>'
      % (p.X(2.0), p.Y(2.9), p.X(3.55) - p.X(2.0), p.Y(2.9) - p.Y(5.5), TEXT, TEXT))
p.label(2.0, 5.12, "&#937;", 0, 0, TEXT, 13, "middle", True, True)
ys = [5.0 - 0.6 * k for k in range(8)]
xs = [1.35 if k % 2 == 0 else 2.65 for k in range(8)]
# the number line on the right
p.arrow((5.6, 3.0), (9.6, 3.0), TEXT, 1.2, 7.0, opacity=0.6)
p.label(9.55, 3.0, "&#8477;", 0, -10, TEXT, 12, "end", True, False)
XV = {0: 6.2, 1: 7.2, 2: 8.2, 3: 9.2}
for v, x in XV.items():
    p.line([(x, 2.85), (x, 3.15)], TEXT, 1.2)
    p.label(x, 3.0, str(v), 0, 20, TEXT, 11.5, "middle", True, False)
# the event (X <= 1): points and half-line shaded
p.line([(5.6, 3.0), (XV[1], 3.0)], THEORY, 6.0, None, 0.35)
for k, (name, v) in enumerate(OUTC):
    col = THEORY if v <= 1 else TEXT
    dot(p, (xs[k], ys[k]), col, 3.4)
    p.label(xs[k], ys[k], name, -7 if k % 2 == 0 else 7, 4, col, 10, "end" if k % 2 == 0 else "start", False, False)
    p.line([(xs[k] + 0.12, ys[k]), (XV[v] - 0.08, 3.0 + (0.18 if v <= 1 else -0.18))], col, 0.9, None, 0.55)
for v in (0, 1):
    dot(p, (XV[v], 3.0), THEORY, 4.0)
p.label(6.7, 3.0, "(X " + LEQ_S + " 1)", 0, -16, THEORY, 11, "middle", True, True)
p.label(2.0, -0.3, "X(&#969;) = tura sayısı", 0, 0, TEXT, 11, "middle", False, True)
p.label(7.6, 5.4, "X : &#937; &#8594; &#8477;", 0, 0, TEXT, 12, "middle", True, True)
p.label(7.6, 4.75, "(X " + LEQ_S + " 1) = {YYY, YYT, YTY, TYY}: bir olay", 0, 0, THEORY, 10.5, "middle", False, True)
OUT["rastgele-degisken-sema"] = figure(
    560, 240, [p],
    "Rastgele değişken, örnek uzayın her sonucuna bir sayı eşleyen fonksiyondur; burada üç para atışında tura "
    "sayısı. \"<em>X</em> &#8804; 1\" gibi bir koşul, sayı doğrusunda bir yarı doğruya, örnek uzayda ise "
    "oraya giden sonuçların kümesine karşılık gelir. Tanım, bu kümelerin hepsinin birer olay (&#963;-cebrin "
    "elemanı) olmasını ister; olasılıkları ancak o zaman anlamlıdır.",
    css_class=WIDE,
    aria="Ornek uzayin sekiz sonucu sayi dogrusundaki 0,1,2,3 degerlerine oklarla esleniyor; X kucuk esit 1 olayi taranmis")

# ============================================================ sagdan-sureklilik
# Zoom on one jump of a distribution function at x = a: the left limit F(a-) = 0.4 is not
# attained (open point), the value F(a) = 0.7 is (closed point); the jump is P(X = a).
A, FL, FR = 2.0, 0.4, 0.7
XR, YR = (0.9, 3.1), (0.15, 1.02)


def F_left(x):
    return FL - 0.15 * (A - x) ** 2


def F_right(x):
    return FR + 0.15 * (1 - (A + 1 - x) ** 2)


def xfmt_a(v):
    return "a"


def yfmt_F(v):
    return "F(a" + sups(MINUS_S) + ")" if abs(v - FL) < 1e-9 else "F(a)"


p = Plot(58, 30, 300, 202, XR, YR)
p.axes((A,), (FL, FR), "x", "F(x)", xfmt=xfmt_a, yfmt=yfmt_F)
# guides from the axes to the two special points
guide(p, [(XR[0], FL), (A, FL)], TEXT, 0.4)
guide(p, [(XR[0], FR), (A, FR)], TEXT, 0.4)
guide(p, [(A, YR[0]), (A, FL)], TEXT, 0.4)
# the two branches of F
curve(p, F_left, XR[0] + 0.02, A, THEORY, 2.2, 120)
curve(p, F_right, A, XR[1] - 0.02, THEORY, 2.2, 120)
# the jump: P(X = a) = F(a) - F(a-)
p.arrow((A, FL + 0.03), (A, FR - 0.03), PRACTICE, 1.4, 6.5)
p.arrow((A, FR - 0.03), (A, FL + 0.03), PRACTICE, 1.4, 6.5)
p.label(A, (FL + FR) / 2, "P(X = a) = F(a) " + MINUS_S + " F(a" + sups(MINUS_S) + ")",
        9, 4, PRACTICE, 10.5, "start", False, True)
# approach from the left: the open point is the limit, not a value
p.arrow((1.35, 0.50), (1.86, 0.455), THEORY, 1.2, 6.0, opacity=0.75)
p.label(1.42, 0.60, "x " + "&#8593;" + " a:  F(x) " + ARROW + " F(a" + sups(MINUS_S) + ")",
        0, 0, THEORY, 10.5, "middle", False, True)
# approach from the right: F(x) goes to the value F(a)
p.arrow((2.62, 0.92), (2.14, 0.79), THEORY, 1.2, 6.0, opacity=0.75)
p.label(2.62, 0.98, "x " + "&#8595;" + " a:  F(x) " + ARROW + " F(a)",
        0, 0, THEORY, 10.5, "middle", False, True)
hollow(p, (A, FL), THEORY, 4.2, 1.7)
dot(p, (A, FR), THEORY, 4.2)
p.label(A, FR, "sağdan sürekli", -9, -7, THEORY, 10, "end", False, True)
OUT["sagdan-sureklilik"] = figure(
    400, 256, [p],
    "Bir dağılım fonksiyonunun <em>a</em> noktasındaki sıçraması. Soldan yaklaşırken <em>F</em>(<em>x</em>), "
    "değer olarak alınmayan sol limit <em>F</em>(<em>a</em><sup>&#8722;</sup>)'ye (boş nokta) gider; "
    "sağdan yaklaşırken fonksiyonun gerçek değeri <em>F</em>(<em>a</em>)'ya (dolu nokta) gider: "
    "sağdan süreklilik budur. Sıçramanın yüksekliği <em>P</em>(<em>X</em> = <em>a</em>) = "
    "<em>F</em>(<em>a</em>) &#8722; <em>F</em>(<em>a</em><sup>&#8722;</sup>) nokta olasılığıdır.",
    aria="Dagilim fonksiyonunun a noktasindaki sicramasi: soldan limit bos nokta, sagdan deger dolu nokta, aradaki fark P(X = a)")

# ============================================================ secme-dort-yol
# The four ways of choosing r objects out of n: order matters or not, repetition allowed or not.
# Everything is placed in pixel coordinates; the panel only carries the drawing.
p = Plot(0, 0, 400, 258, (0, 400), (0, 258))

CX = (90, 248)          # left edges of the two cell columns
CW = 150                # cell width
CY = (44, 152)          # top edges of the two cell rows
CH = 100                # cell height
COLC = (PRACTICE, THEORY)   # column colour: repetition allowed (orange) / not allowed (blue)

p.text_px(244, 14, "n farklı nesneden r tanesini seçmek", TEXT, 11, "middle", False, True)
p.text_px(CX[0] + CW / 2, 34, "tekrarlı (iadeli)", COLC[0], 11.5, "middle", True)
p.text_px(CX[1] + CW / 2, 34, "tekrarsız (iadesiz)", COLC[1], 11.5, "middle", True)

for j, (name, note) in enumerate((("sıra önemli", "(sıralı)"), ("sıra önemsiz", "(sırasız)"))):
    yc = CY[j] + CH / 2
    p.text_px(42, yc - 2, name, TEXT, 11.5, "middle", True)
    p.text_px(42, yc + 13, note, TEXT, 10, "middle", False, True)

CELLS = {
    # (row, col): formula, name, count, outcomes for a, b, c with r = 2
    (0, 0): ("n" + sups("r"), "çarpma kuralı", "9",
             ("aa  ab  ac", "ba  bb  bc", "ca  cb  cc")),
    (0, 1): ("P(n, r) = n!/(n" + MINUS_S + "r)!", "permütasyon", "6",
             ("ab  ac  ba", "bc  ca  cb")),
    (1, 0): ("C(n+r" + MINUS_S + "1, r)", "tekrarlı kombinasyon", "6",
             ("aa  ab  ac", "bb  bc  cc")),
    (1, 1): ("C(n, r) = n!/(r!(n" + MINUS_S + "r)!)", "kombinasyon", "3",
             ("ab  ac  bc",)),
}
for (j, i), (formula, name, count, rows) in CELLS.items():
    x, y, col = CX[i], CY[j], COLC[i]
    p.add(f'<rect x="{x}" y="{y}" width="{CW}" height="{CH}" rx="4" fill="{col}" fill-opacity="0.10" '
          f'stroke="{col}" stroke-width="1.2"/>')
    cx = x + CW / 2
    p.text_px(cx, y + 19, formula, col, 12, "middle", True, True)
    p.text_px(cx, y + 34, name, col, 10, "middle", False, True)
    p.add(f'<line x1="{x + 14}" y1="{y + 42}" x2="{x + CW - 14}" y2="{y + 42}" stroke="{col}" '
          f'stroke-width="0.8" opacity="0.6"/>')
    p.text_px(cx, y + 56, "n = 3, r = 2:  " + count + " seçim", TEXT, 10.5, "middle", True)
    for k, row in enumerate(rows):
        p.text_px(cx, y + 69 + 12 * k, row, TEXT, 9.5, "middle", False, True)

OUT["secme-dort-yol"] = figure(
    400, 258, [p],
    "<em>n</em> farklı nesneden <em>r</em> tanesini seçmenin dört yolu. Sütunlar tekrara (iadeye) izin "
    "verilip verilmediğini, satırlar sıranın önemli olup olmadığını ayırır; her hücrede sayma formülü ve "
    "<em>a</em>, <em>b</em>, <em>c</em> nesnelerinden ikisinin seçilmesi örneği (<em>n</em> = 3, <em>r</em> = 2) "
    "vardır. Sıralı seçimler 9 ve 6, sırasız seçimler 6 ve 3 tanedir; sıra önemsizleşince <em>ab</em> ile "
    "<em>ba</em> aynı seçim sayılır, tekrar yasaklanınca <em>aa</em> gibi seçimler düşer.",
    aria="Iki satir iki sutunluk sema: sira onemli veya onemsiz, tekrarli veya tekrarsiz secim formulleri ve n=3 r=2 ornekleri")

# ============================================================ surekli-kavram-haritasi
# Concept map for a continuous random variable: the distribution P_X, the distribution function F
# and the density f determine one another; the edges carry the translation rules.
# The panel uses pixel coordinates directly (y grows downward like the SVG canvas).
W, H = 560, 236
p = Plot(0, 0, W, H, (0, W), (H, 0))

TOP = (280, 34)
FN = (92, 172)
DN = (468, 172)


def node(c, w, h, color):
    x, y = c
    p.add('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="6" fill="%s" fill-opacity="0.09" '
          'stroke="%s" stroke-width="1.3"/>' % (x - w / 2, y - h / 2, w, h, color, color))


def edge(a, b, color=TEXT, shrink=0.0):
    p.arrow(a, b, color, 1.4, 7.0, opacity=0.75)
    p.arrow(b, a, color, 1.4, 7.0, opacity=0.75)


# nodes
node(TOP, 150, 26, TEXT)
p.text_px(TOP[0], TOP[1] + 4.5, "(&#8477;, B(&#8477;), P" + subs("X") + ")", TEXT, 12, "middle", True, True)
p.text_px(TOP[0], TOP[1] - 21, "X'in olasılık dağılımı", TEXT, 9.5, "middle", False, True)

node(FN, 34, 26, THEORY)
p.text_px(FN[0], FN[1] + 5, "F", THEORY, 14, "middle", True, True)
p.text_px(FN[0], FN[1] + 27, "dağılım fonksiyonu", THEORY, 9.5, "middle", False, True)

node(DN, 34, 26, PRACTICE)
p.text_px(DN[0], DN[1] + 5, "f", PRACTICE, 14, "middle", True, True)
p.text_px(DN[0], DN[1] + 27, "yoğunluk fonksiyonu", PRACTICE, 9.5, "middle", False, True)

# edges (two-way: each pair of objects determines the other)
edge((238, 50), (109, 158))     # P_X <-> F
edge((322, 50), (451, 158))     # P_X <-> f
edge((115, 172), (445, 172))    # F <-> f

# left edge: P_X <-> F
p.text_px(184, 84, "F(x) = P" + subs("X") + "((" + MINUS_S + INF + ", x])", TEXT, 11, "end", False, False)
p.text_px(166, 103, "P" + subs("X") + "((a, b]) = F(b) " + MINUS_S + " F(a)", TEXT, 11, "end", False, False)

# right edge: P_X <-> f
p.text_px(376, 84, "P" + subs("X") + "(B) = " + INT_S + subs("B") + " f", TEXT, 11, "start", False, False)
p.text_px(394, 103, "f " + GEQ_S + " 0,  " + INT_S + " f = 1", TEXT, 11, "start", False, False)

# bottom edge: F <-> f
p.text_px(280, 163, "F(x) = " + INT_S + subs(MINUS_S + INF) + sups("x") + " f(t) dt", THEORY, 11, "middle", False, False)
p.text_px(280, 190, "f = F" + PRIME + "  (kırılma noktaları dışında)", PRACTICE, 11, "middle", False, False)

# the fact that separates the continuous case from the discrete one
p.text_px(280, 226, "P(X = a) = 0:  tek nokta olasılık taşımaz, aralık uçları önemsizdir", TEXT, 10.5, "middle", False, True)

OUT["surekli-kavram-haritasi"] = figure(
    W, H, [p],
    "Sürekli bir <em>X</em> için üç nesne aynı dağılımı anlatır: olasılık dağılımı <em>P<sub>X</sub></em>, "
    "dağılım fonksiyonu <em>F</em> ve yoğunluk <em>f</em>. Kenarlardaki kurallar birinden ötekine nasıl "
    "geçileceğini söyler: <em>F</em>, <em>f</em>'nin integrali; <em>f</em>, <em>F</em>'nin türevidir; olasılıklar "
    "ya <em>F</em>'nin farkı ya <em>f</em>'nin integralidir. Kesikli durumdan farkı, hiçbir tek noktanın "
    "olasılık taşımamasıdır.",
    css_class=WIDE,
    aria="Ucgen kavram haritasi: ustte olasilik dagilimi P_X, altta dagilim fonksiyonu F ve yogunluk f; kenarlarda birinden otekine gecis formulleri")

# ============================================================ tek-nokta-borel
# The singleton {a} as the intersection of the nested open intervals (a - 1/n, a + 1/n), n = 1..4.
# Data y is measured in pixels from the bottom of the panel, so rows are placed directly.
p = Plot(142, 24, 240, 160, (-1.22, 1.22), (0, 160))
Y_LINE = 20                                   # the number line
ROWS = [(1, 132), (2, 104), (3, 76), (4, 48)]  # (n, data y) from the widest interval down
WIDTHS = {1: 2.8, 2: 2.4, 3: 2.0, 4: 1.7}
TONES = {1: 1.0, 2: 0.85, 3: 0.72, 4: 0.6}
FRAC = {1: "1", 2: "1/2", 3: "1/3", 4: "1/4"}

# nested shading: the overlaps darken toward a, where every interval still contains the point
for n, y in ROWS:
    rect(p, -1 / n, 1 / n, Y_LINE, y, THEORY, 0.06)
# the number line
p.arrow((-1.16, Y_LINE), (1.2, Y_LINE), TEXT, 1.2, 7.0, opacity=0.6)
p.label(1.18, Y_LINE, "&#8477;", 0, -9, TEXT, 11.5, "end", True, False)
for x, s in ((-1, "a " + MINUS_S + " 1"), (1, "a + 1")):
    p.line([(x, Y_LINE - 4), (x, Y_LINE + 4)], TEXT, 1.2)
    p.label(x, Y_LINE, s, 0, 19, TEXT, 11, "middle", False, True)
# the point a runs through every row
guide(p, [(0, Y_LINE), (0, 140)], PRACTICE, 0.55)
# the open intervals, one per row, thinner and lighter as n grows
for n, y in ROWS:
    p.line([(-1 / n, y), (1 / n, y)], THEORY, WIDTHS[n], None, TONES[n])
    hollow(p, (-1 / n, y), THEORY, 3.4, 1.5)
    hollow(p, (1 / n, y), THEORY, 3.4, 1.5)
    p.text_px(130, p.Y(y) + 4,
              "A" + subs(str(n)) + " = (a " + MINUS_S + " " + FRAC[n] + ", a + " + FRAC[n] + ")",
              TEXT, 10.5, "end", False, True)
# the intersection: the single point a on the number line
dot(p, (0, Y_LINE), PRACTICE, 4.4)
p.label(0, Y_LINE, "a", 0, 19, PRACTICE, 12, "middle", True, True)
p.text_px(p.X(0), p.y0 + p.h + 35,
          "&#8745; A" + subs("n") + " = &#8745; (a " + MINUS_S + " 1/n, a + 1/n) = {a}",
          PRACTICE, 11.5, "middle", True, True)
OUT["tek-nokta-borel"] = figure(
    400, 226, [p],
    "Tek nokta kümesi {<em>a</em>}, iç içe daralan açık aralıkların kesişimidir. Her "
    "<em>A<sub>n</sub></em> = (<em>a</em> &#8722; 1/<em>n</em>, <em>a</em> + 1/<em>n</em>) aralığı "
    "<em>a</em>'yı içerir; <em>a</em>'dan farklı her nokta ise Arşimet özelliği gereği yeterince büyük "
    "<em>n</em> için aralığın dışında kalır. Böylece kesişimde yalnızca <em>a</em> kalır ve {<em>a</em>} "
    "bir Borel kümesidir.",
    aria="Sayi dogrusu uzerinde a noktasi ve a etrafinda ic ice daralan dort acik aralik; kesisimleri tek nokta a")

# ============================================================ toplam-fark-kafes
# The map (x1, x2) -> (y1, y2) = (x1 + x2, x1 - x2) on the lattice {0,1}^2: four source points with
# their probabilities, and their four images on a sparse checkerboard inside {0,1,2} x {-1,0,1}.
def it(s):
    return '<tspan font-style="italic">%s</tspan>' % s


X1, X2 = it("x") + subs("1"), it("x") + subs("2")
Y1, Y2 = it("y") + subs("1"), it("y") + subs("2")

# (x1, x2) -> probability f(x1, x2), taken from the worked example
SRC = {(0, 0): "1/9", (0, 1): "2/9", (1, 0): "2/9", (1, 1): "4/9"}
IMG = {(0, 0): (0, 0), (0, 1): (1, -1), (1, 0): (1, 1), (1, 1): (2, 0)}

# left panel: the source lattice, 70 px per unit
p1 = Plot(58, 44, 175, 175, (-0.6, 1.7), (-0.6, 1.7))
p1.origin_axes(X1, X2, xticks=(1,), yticks=(1,))
p1.text_px(p1.X(0) - 7, p1.Y(0) + 15, "0", TEXT, 11, "end")
panel_title(p1, "(" + X1 + ", " + X2 + ") kafesi", THEORY)
for (a, b), pr in SRC.items():
    p1.points([(a, b)], THEORY, 4.6)
    p1.label(a, b, pr, 7, -7, THEORY, 10.5, "start")

# right panel: the image lattice, 50 px per unit; empty cells drawn hollow
p2 = Plot(340, 46, 170, 165, (-0.7, 2.7), (-1.65, 1.65))
p2.origin_axes(Y1, Y2, xticks=(1, 2), yticks=(-1, 1))
panel_title(p2, "(" + Y1 + ", " + Y2 + ") = (" + X1 + "+" + X2 + ", " + X1 + MINUS_S + X2 + ")", PRACTICE)
images = set(IMG.values())
for u in (0, 1, 2):
    for v in (-1, 0, 1):
        if (u, v) not in images:
            hollow(p2, (u, v), TEXT, 3.6, 1.2)
for (a, b), pr in SRC.items():
    u, v = IMG[(a, b)]
    p2.points([(u, v)], PRACTICE, 4.6)
    if (u, v) == (0, 0):
        # keep the origin label clear of the incoming dashed connector
        p2.label(u, v, pr, -8, 17, PRACTICE, 10.5, "end")
    else:
        p2.label(u, v, pr, 7, -7, PRACTICE, 10.5, "start")

# dashed connectors for two of the four points (chosen so they do not cross), in absolute pixels;
# the second one arcs upward so it does not run through the empty cell (1, 0)
for (a, b), bulge in (((0, 1), 0.0), ((1, 1), -30.0)):
    u, v = IMG[(a, b)]
    x0, y0 = p1.X(a), p1.Y(b)
    x1, y1 = p2.X(u), p2.Y(v)
    L = math.hypot(x1 - x0, y1 - y0)
    ux, uy = (x1 - x0) / L, (y1 - y0) / L
    cx, cy = (x0 + x1) / 2 - uy * bulge, (y0 + y1) / 2 + ux * bulge
    # shorten both ends so the curve does not sit on the dots or their labels
    sx, sy = x0 + ux * 26, y0 + uy * 26
    tx, ty = x1 - cx, y1 - cy
    T = math.hypot(tx, ty)
    tx, ty = tx / T, ty / T
    ex, ey = x1 - tx * 9, y1 - ty * 9
    p2.add('<path d="M%.1f,%.1f Q%.1f,%.1f %.1f,%.1f" fill="none" stroke="%s" stroke-width="1.1" '
           'stroke-dasharray="5 4" opacity="0.55"/>' % (sx, sy, cx, cy, ex, ey, BASE))
    hw = 3.2
    p2.add('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s" opacity="0.8"/>'
           % (ex + tx * 6, ey + ty * 6, ex - ty * hw, ey + tx * hw, ex + ty * hw, ey - tx * hw, BASE))

# notes: the map is one-to-one; the image lattice is sparse
p2.text_px(286, 80, "birebir", BASE, 11, "middle", True, True)
p2.text_px(430, 234, "görüntü kafesi seyrek: " + Y1 + " + " + Y2 + " = 2" + X1 + " çift", TEXT, 10.5, "middle", False, True)

OUT["toplam-fark-kafes"] = figure(
    560, 245, [p1, p2],
    "Toplam ve fark dönüşümü. Solda (<em>x</em><sub>1</sub>, <em>x</em><sub>2</sub>) kafesi {0, 1}<sup>2</sup> ve her "
    "noktaya düşen olasılık; sağda (<em>y</em><sub>1</sub>, <em>y</em><sub>2</sub>) = (<em>x</em><sub>1</sub> + "
    "<em>x</em><sub>2</sub>, <em>x</em><sub>1</sub> &#8722; <em>x</em><sub>2</sub>) altındaki görüntüleri. Dört nokta dört "
    "farklı görüntüye gider, dönüşüm birebirdir ve olasılıklar olduğu gibi taşınır. Görüntü kafesinin yalnızca "
    "<em>y</em><sub>1</sub> + <em>y</em><sub>2</sub> çift olan hücreleri dolar; içi boş hücrelerin olasılığı sıfırdır.",
    css_class=WIDE,
    aria="Solda {0,1} kare kafesindeki dort nokta ve olasiliklari, sagda toplam ve fark donusumu altindaki "
         "dort goruntu noktasi; kesikli oklar eslemeyi gosterir")

# ============================================================ toplam-olasilik-venn
# Law of total probability: the sample space cut into four vertical strips A_1..A_4 (a partition),
# the event B as a horizontal ellipse, and the four disjoint slices B n A_i hatched differently.
# Beside the picture, the slice probabilities add up to P(B).
CUTS = [0.0, 3.4, 7.6, 11.2, 16.0]          # strip boundaries (data units; 20 px per unit)
CX, CY, RA, RB = 8.0, 4.5, 7.4, 2.4         # ellipse B: centre and semi-axes
PID = "tovenn-h"                             # id prefix for the hatch patterns


def slice_pts(xl, xr, n=40):
    """The part of the ellipse between x = xl and x = xr, as a polygon (upper arc, then lower arc back)."""
    def half(x):
        return RB * math.sqrt(max(0.0, 1.0 - ((x - CX) / RA) ** 2))
    xs = [xl + (xr - xl) * k / n for k in range(n + 1)]
    return [(x, CY + half(x)) for x in xs] + [(x, CY - half(x)) for x in reversed(xs)]


p = Plot(14, 28, 320, 180, (0, 16), (0, 9))   # equal aspect: 20 px per unit

# hatch patterns, all in the colour of B so the slices read as parts of one event
p.add('<defs>'
      f'<pattern id="{PID}1" patternUnits="userSpaceOnUse" width="6" height="6" patternTransform="rotate(45)">'
      f'<line x1="3" y1="0" x2="3" y2="6" stroke="{THEORY}" stroke-width="1.1" opacity="0.75"/></pattern>'
      f'<pattern id="{PID}2" patternUnits="userSpaceOnUse" width="6" height="6" patternTransform="rotate(-45)">'
      f'<line x1="3" y1="0" x2="3" y2="6" stroke="{THEORY}" stroke-width="1.1" opacity="0.75"/></pattern>'
      f'<pattern id="{PID}3" patternUnits="userSpaceOnUse" width="6" height="6">'
      f'<line x1="0" y1="3" x2="6" y2="3" stroke="{THEORY}" stroke-width="1.1" opacity="0.75"/></pattern>'
      f'<pattern id="{PID}4" patternUnits="userSpaceOnUse" width="7" height="7">'
      f'<circle cx="3.5" cy="3.5" r="1.25" fill="{THEORY}" opacity="0.8"/></pattern>'
      '</defs>')

# the slices B n A_i: light tint plus a distinct hatch each
XL, XR = CX - RA, CX + RA
for i in range(4):
    xl, xr = max(CUTS[i], XL), min(CUTS[i + 1], XR)
    pts = slice_pts(xl, xr)
    p.polygon(pts, THEORY, 0.12)
    p.polygon(pts, f"url(#{PID}{i + 1})", 1.0)

# the sample space and the partition into strips, drawn over the hatching so the cuts stay crisp
p.polygon([(0, 0), (16, 0), (16, 9), (0, 9)], TEXT, 0.0, TEXT, 1.2)
for x in CUTS[1:-1]:
    p.line([(x, 0), (x, 9)], TEXT, 1.2)

# outline of B (raw ellipse in pixel coordinates)
p.add(f'<ellipse cx="{p.X(CX):.1f}" cy="{p.Y(CY):.1f}" rx="{p.R(RA):.1f}" ry="{p.R(RB):.1f}" '
      f'fill="none" stroke="{THEORY}" stroke-width="1.8"/>')

# names: strips along the top, B above its left tip, the sample space in the bottom-right corner
for i in range(4):
    p.label((CUTS[i] + CUTS[i + 1]) / 2, 8.2, "A" + subs(str(i + 1)), 0, 0, TEXT, 12, "middle", True, True)
p.label(1.15, 6.25, "B", 0, 0, THEORY, 12.5, "middle", True, True)
p.text_px(p.x0 + p.w - 6, p.y0 + p.h - 6, "&#937;", TEXT, 12, "end", False, True)

# slice labels on a background halo so the hatching does not cut through the letters
for i, x in enumerate((2.2, 5.5, 9.4, 13.2)):
    X, Y = p.X(x), p.Y(CY)
    p.add(f'<rect x="{X - 22:.1f}" y="{Y - 8:.1f}" width="44" height="16" rx="3" fill="{BG}"/>')
    p.text_px(X, Y + 4, "B &#8745; A" + subs(str(i + 1)), THEORY, 10.5, "middle", True, True)

# the arithmetic beside the picture: one term per slice, then the total
LX = 352
p.text_px(LX, 40, "dört dilim ikişer ikişer ayrık, o yüzden", TEXT, 10.5, "start", False, True)
p.text_px(LX, 62, "P(B) = " + SUM_S + subs("i") + " P(B &#8745; A" + subs("i") + ")", TEXT, 12, "start")
for i in range(4):
    y = 92 + 24 * i
    p.add(f'<rect x="{LX}" y="{y - 10}" width="16" height="11" fill="{THEORY}" fill-opacity="0.12" '
          f'stroke="{THEORY}" stroke-width="0.8"/>')
    p.add(f'<rect x="{LX}" y="{y - 10}" width="16" height="11" fill="url(#{PID}{i + 1})"/>')
    k = subs(str(i + 1))
    p.text_px(LX + 24, y, f"P(B &#8745; A{k}) = P(A{k}) P(B | A{k})", TEXT, 10.5, "start")
p.add(f'<line x1="{LX + 24}" y1="178" x2="{LX + 190}" y2="178" stroke="{TEXT}" stroke-width="1" opacity="0.45"/>')
p.text_px(LX, 200, "P(B) = " + SUM_S + subs("i") + " P(A" + subs("i") + ") P(B | A" + subs("i") + ")",
          TEXT, 12, "start", True)

OUT["toplam-olasilik-venn"] = figure(
    560, 228, [p],
    "Toplam olasılık formülünün Venn şeması. Düşey çizgiler örnek uzay &#937;'yı ikişer ikişer ayrık "
    "<em>A</em><sub>1</sub>, <em>A</em><sub>2</sub>, <em>A</em><sub>3</sub>, <em>A</em><sub>4</sub> parçalarına böler; "
    "<em>B</em> olayı da bu çizgilerle dört ayrık dilime <em>B</em> &#8745; <em>A</em><sub><em>i</em></sub> ayrılır. "
    "Ayrık dilimlerin olasılıkları toplanarak <em>P</em>(<em>B</em>) bulunur; her dilimin olasılığı ise koşullu "
    "olasılığın tanımıyla <em>P</em>(<em>A</em><sub><em>i</em></sub>) <em>P</em>(<em>B</em> | <em>A</em><sub><em>i</em></sub>) "
    "biçiminde yazılır.",
    css_class=WIDE,
    aria="Dikdortgen ornek uzay dort dusey parcaya bolunmus; ortadaki elips B her parcada ayri taranmis bir dilime ayrilmis; yaninda toplam olasilik formulu")

# ============================================================ tumleyen-parcalama
# B split by A: B = (A and B) or (not-A and B); used in the "complements stay independent" proof.
R_T, D_T = 0.95, 1.1


def _arc(cx, cy, a0, a1, n=48):
    return [(cx + R_T * math.cos(a0 + (a1 - a0) * k / n), cy + R_T * math.sin(a0 + (a1 - a0) * k / n))
            for k in range(n + 1)]


th = math.acos((D_T / 2) / R_T)
XA, XB = -D_T / 2, D_T / 2
lens = _arc(XA, 0, -th, th) + _arc(XB, 0, math.pi - th, math.pi + th)
b_minus_a = _arc(XB, 0, -(math.pi - th), math.pi - th) + _arc(XA, 0, th, -th)

p = Plot(60, 26, 280, 170, (-2.4, 2.4), (-1.45, 1.45))
p.polygon([(-2.3, -1.35), (2.3, -1.35), (2.3, 1.35), (-2.3, 1.35)], TEXT, 0.0, TEXT, 1.0)
p.polygon(lens, THEORY, 0.45)
p.polygon(b_minus_a, PRACTICE, 0.35)
p.circle(XA, 0, R_T, TEXT, 1.3)
p.circle(XB, 0, R_T, TEXT, 1.3)
p.label(XA - 0.45, 0.6, "A", 0, 0, TEXT, 12, "middle", True, True)
p.label(XB + 0.45, 0.6, "B", 0, 0, TEXT, 12, "middle", True, True)
p.label(0, 0, "A &#8745; B", 0, 4, THEORY, 10.5, "middle", True, True)
p.label(XB + 0.32, -0.15, "A" + sups("c") + " &#8745; B", 0, 4, PRACTICE, 10.5, "middle", True, True)
p.text_px(p.x0 + p.w + 14, p.y0 + 50, "B, iki ayrık parçanın birleşimi:", TEXT, 10.5, "start", False, True)
p.text_px(p.x0 + p.w + 14, p.y0 + 72, "A &#8745; B  ve  A" + sups("c") + " &#8745; B", TEXT, 11, "start", True, True)
p.text_px(p.x0 + p.w + 14, p.y0 + 100, "o yüzden", TEXT, 10.5, "start", False, True)
p.text_px(p.x0 + p.w + 14, p.y0 + 120, "P(B) = P(A &#8745; B) + P(A" + sups("c") + " &#8745; B)", TEXT, 11, "start", False, True)
OUT["tumleyen-parcalama"] = figure(
    560, 200, [p],
    "<em>B</em> olayı, <em>A</em>'nın gerçekleşip gerçekleşmemesine göre iki ayrık parçaya ayrılır. "
    "<em>A</em> ile <em>B</em> bağımsızken <em>P</em>(<em>A</em> &#8745; <em>B</em>) = <em>P</em>(<em>A</em>)"
    "<em>P</em>(<em>B</em>) yerine konursa, kalan parçanın olasılığı (1 &#8722; <em>P</em>(<em>A</em>))"
    "<em>P</em>(<em>B</em>) = <em>P</em>(<em>A</em><sup>c</sup>)<em>P</em>(<em>B</em>) çıkar: tümleyen de "
    "<em>B</em>'den bağımsızdır.",
    css_class=WIDE,
    aria="B olayinin A ile kesisen ve A disinda kalan iki ayrik parcaya bolunmesi")

# ============================================================ ucgen-x-arti-y
# Uniform density f = 2 on the triangle x + y < 1 and the event X > 2Y, i.e. y < x/2:
# the sub-triangle with corners (0,0), (1,0), (2/3, 1/3); probability = area ratio = 1/3.
def it(s):
    return '<tspan font-style="italic">%s</tspan>' % s


p = Plot(36, 22, 208, 208, (-0.16, 1.22), (-0.16, 1.22))
# support of the density: the triangle x + y < 1, lightly shaded
p.polygon([(0, 0), (1, 0), (0, 1)], THEORY, 0.16, THEORY, 1.4)
p.origin_axes("x", "y", xticks=(1,), yticks=(1,))
guide(p, [(0, 1 / 3), (2 / 3, 1 / 3)], TEXT, 0.4)
p.label(0, 1 / 3, "1/3", -6, 4, TEXT, 10.5, "end")
# the event region y < x/2 inside the triangle
p.polygon([(0, 0), (1, 0), (2 / 3, 1 / 3)], PRACTICE, 0.42, PRACTICE, 1.4)
# the line y = x/2, extended a little past the triangle
p.line([(0, 0), (1.14, 0.57)], PRACTICE, 1.8, "6 4")
# the corner (2/3, 1/3)
guide(p, [(2 / 3, 0), (2 / 3, 1 / 3)], TEXT, 0.4)
dot(p, (2 / 3, 1 / 3), PRACTICE, 3.6)
p.label(1.14, 0.57, it("y") + " = " + it("x") + "/2", 0, -8, PRACTICE, 10.5, "end")
p.label(0.2, 0.5, it("f") + " = 2", 0, 0, THEORY, 11, "middle")
p.label(0.33, 0.07, it("X") + " &gt; 2" + it("Y"), 0, 0, PRACTICE, 10.5, "middle", True)
p.label(2 / 3, 0, "2/3", 0, 14, TEXT, 9.5, "middle")
p.label(0, 0, "0", -6, 14, TEXT, 10.5, "end")
# the computation on the right, in pixel coordinates
x0 = 262
lines = [
    (34, it("X") + " &gt; 2" + it("Y") + ", yani " + it("y") + " &lt; " + it("x") + "/2", PRACTICE, True),
    (60, "Destek: alan 1/2,", THEORY, False),
    (76, it("f") + " = 2 (sabit)", THEORY, False),
    (104, "Olay üçgeni: tepe (2/3, 1/3),", PRACTICE, False),
    (120, "taban 1, yükseklik 1/3,", PRACTICE, False),
    (136, "alan = 1/2 &#183; 1 &#183; 1/3 = 1/6", PRACTICE, False),
    (166, "Alan oranı:", TEXT, False),
    (184, it("P") + "(" + it("X") + " &gt; 2" + it("Y") + ") = 2 &#183; 1/6", TEXT, True),
    (202, "= (1/6) / (1/2) = 1/3", TEXT, True),
]
for py, s, col, bold in lines:
    p.text_px(x0, py, s, col, 10.5, "start", bold)
OUT["ucgen-x-arti-y"] = figure(
    400, 246, [p],
    "Sabit yoğunlukta olasılık alan oranına döner. Açık taralı üçgen <em>x</em> + <em>y</em> &lt; 1 desteğidir; "
    "üzerinde <em>f</em> = 2. <em>X</em> &gt; 2<em>Y</em> olayı <em>y</em> &lt; <em>x</em>/2 demektir: kesikli "
    "<em>y</em> = <em>x</em>/2 doğrusu desteği (2/3, 1/3) noktasında keser ve olay, köşeleri (0, 0), (1, 0), "
    "(2/3, 1/3) olan koyu üçgendir. Alanı 1/6 olduğundan <em>P</em>(<em>X</em> &gt; 2<em>Y</em>) = 2 &#183; 1/6 = "
    "1/3; yani olayın alanının desteğin alanına oranı.",
    aria="Ucgen x arti y kucuk 1 icinde y = x/2 dogrusunun altinda kalan olay bolgesi ve alan orani hesabi")

# ============================================================ ucgen-yogunluk-ve-dagilim
# Triangular density f(x) = 1 - |x| on [-1, 1] and its distribution function.
def f_tri(x):
    return max(0.0, 1.0 - abs(x))


def F_tri(x):
    if x <= -1:
        return 0.0
    if x <= 0:
        return (x + 1) ** 2 / 2
    if x <= 1:
        return 1 - (1 - x) ** 2 / 2
    return 1.0


p1 = Plot(44, 30, 226, 190, (-1.7, 1.7), (-0.1, 1.2))
p1.origin_axes("x", "y", xticks=(-1, 1), yticks=(1,))
panel_title(p1, "yoğunluk f(x) = 1 " + MINUS_S + " |x|", THEORY)
p1.polygon([(-1, 0), (0, 1), (0.4, 0.6), (0.4, 0)], PRACTICE, 0.25)
p1.polygon([(-1, 0), (0, 1), (1, 0)], THEORY, 0.10)
curve(p1, f_tri, -1.6, 1.6, THEORY, 2.2, 320)
guide(p1, [(0.4, 0), (0.4, 0.6)], PRACTICE, 0.7)
p1.label(0.4, 0, "a", 0, 15, PRACTICE, 11, "middle", True, True)
p1.label(-0.35, 0.28, "F(a)", 0, 0, PRACTICE, 11, "middle", True, True)
p1.label(1.05, 0.75, "toplam alan 1", 0, 0, THEORY, 10.5, "middle", False, True)

p2 = Plot(322, 30, 226, 190, (-1.7, 1.7), (-0.1, 1.2))
p2.origin_axes("x", "y", xticks=(-1, 1), yticks=(0.5, 1), yfmt=tfmt)
panel_title(p2, "dağılım fonksiyonu F(x)", THEORY)
guide(p2, [(-1.7, 1), (1.7, 1)], TEXT, 0.35)
curve(p2, F_tri, -1.6, 1.6, THEORY, 2.2, 320)
guide(p2, [(0.4, 0), (0.4, F_tri(0.4))], PRACTICE, 0.7)
guide(p2, [(0, F_tri(0.4)), (0.4, F_tri(0.4))], PRACTICE, 0.7)
dot(p2, (0.4, F_tri(0.4)), PRACTICE, 4.0)
p2.label(0.4, 0, "a", 0, 15, PRACTICE, 11, "middle", True, True)
p2.label(0, F_tri(0.4), "F(a) = 0,82", -6, 4, PRACTICE, 10.5, "end", False, True)
p2.label(-1.0, 0.18, "F" + PRIME + " = f", 0, 0, THEORY, 10.5, "middle", False, True)
OUT["ucgen-yogunluk-ve-dagilim"] = figure(
    560, 244, [p1, p2],
    "Üçgen yoğunluk ve dağılım fonksiyonu. Solda <em>F</em>(<em>a</em>) = <em>P</em>(<em>X</em> &#8804; "
    "<em>a</em>), yoğunluğun <em>a</em>'nın solunda kalan alanıdır; sağda aynı değer eğri üzerinde okunur. "
    "Yoğunluk kırık olduğu hâlde dağılım fonksiyonu süreklidir ve <em>F</em>&#8242; = <em>f</em> bağıntısı "
    "kırılma noktaları dışında geçerlidir.",
    aria="Ucgen yogunluk fonksiyonu ve onun dagilim fonksiyonu; F(a) alan olarak ve egri uzerinde")

# ============================================================ uretilen-sigma-cebir-atomlar
# Omega = {a,b,c,d} cut into the atoms {a}, {b}, {c,d}; the eight members of
# sigma({{a},{b}}) shown as unions of those atoms.  Pixel drawing, no axes.
W_F, H_F = 564, 202
p = Plot(0, 0, W_F, H_F, (0, W_F), (H_F, 0))     # identity map: data = pixels

ATOM_COLOR = {"a": THEORY, "b": PRACTICE, "cd": BASE}
FILL_OP = 0.40
SIGMA, OMEGA, EMPTY = "&#963;", "&#937;", "&#8709;"


def atom_boxes(x, y, w, h):
    """Quadrant geometry: a top-left, b top-right, {c,d} the whole bottom row."""
    return {"a": (x, x + w / 2, y, y + h / 2),
            "b": (x + w / 2, x + w, y, y + h / 2),
            "cd": (x, x + w, y + h / 2, y + h)}


def partition(x, y, w, h, atoms, border=1.2, dash_op=0.35):
    """Rectangle Omega with its three atoms; the atoms listed in `atoms` are shaded."""
    for key, (x0, x1, y0, y1) in atom_boxes(x, y, w, h).items():
        if key in atoms:
            rect(p, x0, x1, y0, y1, ATOM_COLOR[key], FILL_OP)
    # internal atom boundaries (dashed) and the outer frame (solid)
    p.line([(x, y + h / 2), (x + w, y + h / 2)], TEXT, 0.9, "3 2.5", dash_op)
    p.line([(x + w / 2, y), (x + w / 2, y + h / 2)], TEXT, 0.9, "3 2.5", dash_op)
    rect(p, x, x + w, y, y + h, TEXT, 0.0, TEXT, border)


# ---- title and sub-headings -------------------------------------------------
p.text_px(W_F / 2, 17, SIGMA + "({{a},{b}}) = atomların bütün birleşimleri",
          TEXT, 12, "middle", True)
p.text_px(16, 37, OMEGA + " = {a, b, c, d}", TEXT, 11, "start", False, True)
p.text_px(383, 37, SIGMA + "(L)'nin sekiz elemanı", TEXT, 11, "middle", False, True)

# ---- left: Omega with its points and atoms ------------------------------------
LX, LY, LW, LH = 16, 46, 174, 128
partition(LX, LY, LW, LH, ("a", "b", "cd"), border=1.4)
for name, (cx, cy) in {"a": (56, 80), "b": (143, 80), "c": (72, 144), "d": (134, 144)}.items():
    dot(p, (cx, cy), TEXT, 3.2)
    p.text_px(cx + 7, cy + 4, name, TEXT, 12, "start", False, True)
p.text_px(LX + 5, LY + 12, "{a}", ATOM_COLOR["a"], 10.5, "start", True)
p.text_px(LX + LW - 5, LY + 12, "{b}", ATOM_COLOR["b"], 10.5, "end", True)
p.text_px(LX + LW - 5, LY + LH - 6, "{c, d}", ATOM_COLOR["cd"], 10.5, "end", True)
p.text_px(LX, 189,
          "atomlar: " +
          '<tspan fill="%s" font-weight="600">{a}</tspan>, ' % ATOM_COLOR["a"] +
          '<tspan fill="%s" font-weight="600">{b}</tspan>, ' % ATOM_COLOR["b"] +
          '<tspan fill="%s" font-weight="600">{c, d}</tspan>' % ATOM_COLOR["cd"],
          TEXT, 10.5, "start")

# ---- right: the eight unions of atoms ----------------------------------------
MEMBERS = [((), EMPTY), (("a",), "{a}"), (("b",), "{b}"), (("cd",), "{c, d}"),
           (("a", "b"), "{a, b}"), (("a", "cd"), "{a, c, d}"),
           (("b", "cd"), "{b, c, d}"), (("a", "b", "cd"), OMEGA)]
MW, MH, GAP_X = 64, 50, 22
for i, (atoms, label) in enumerate(MEMBERS):
    col, row = i % 4, i // 4
    x = 222 + col * (MW + GAP_X)
    y = 46 + row * 78
    partition(x, y, MW, MH, atoms, border=1.1, dash_op=0.3)
    for name, (fx, fy) in {"a": (0.25, 0.25), "b": (0.75, 0.25), "c": (0.36, 0.75), "d": (0.64, 0.75)}.items():
        p.text_px(x + fx * MW, y + fy * MH + 3, name, TEXT, 8.5, "middle", False, True)
    if label is EMPTY:
        # the render font lacks U+2205, so draw the empty-set sign by hand
        cx, cy = x + MW / 2, y + MH + 11
        p.add('<circle cx="%.1f" cy="%.1f" r="3.5" fill="none" stroke="%s" stroke-width="1.25"/>'
              % (cx, cy, TEXT))
        p.add('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.25" stroke-linecap="round"/>'
              % (cx - 4.8, cy + 4.8, cx + 4.8, cy - 4.8, TEXT))
    else:
        p.text_px(x + MW / 2, y + MH + 15, label, TEXT, 10.5, "middle", True)

OUT["uretilen-sigma-cebir-atomlar"] = figure(
    W_F, H_F, [p],
    "&#937; = {<em>a</em>, <em>b</em>, <em>c</em>, <em>d</em>} üzerinde <em>L</em> = {{<em>a</em>}, {<em>b</em>}} "
    "sınıfının ürettiği &#963;-cebir. {<em>a</em>} ve {<em>b</em>} verilince tümleyen ve birleşim işlemleri "
    "{<em>c</em>, <em>d</em>} kümesini de zorunlu kılar; bu üç küme &#937;'yı parçalayan atomlardır. "
    "&#963;(<em>L</em>)'nin sekiz elemanı, atomların altkümelerinin birleşimleridir: hiçbir atomu almayan &#8709;'den "
    "üçünü de alan &#937;'ya kadar 2<sup>3</sup> = 8 küme. <em>c</em> ile <em>d</em> hiçbir olayda birbirinden ayrılmaz.",
    css_class=WIDE,
    aria="Omega dort noktali bir dikdortgen olarak uc atoma bolunmus; yaninda sigma cebirin sekiz elemani "
         "atom birlesimleri olarak kucuk dikdortgenlerde taranmis")

# ============================================================ ustel-cift-destek
# Joint density f(x, y) = 6 e^(-3x-2y) on the first quadrant: level lines 3x + 2y = c,
# shading that fades away from the origin, and the two exponential marginals on the edges.
def it(s):
    return '<tspan font-style="italic">%s</tspan>' % s


XR, YR = (0.0, 1.6), (0.0, 2.4)
p = Plot(100, 22, 240, 148, XR, YR)

# shading: bands c <= 3x + 2y < c + 0.5 with exponentially decreasing opacity
step = 0.5
c = 0.0
while c < 6.0:
    c2 = c + step
    pts = [(0, c / 2), (c / 3, 0), (c2 / 3, 0), (0, c2 / 2)]
    p.polygon(pts, THEORY, 0.36 * math.exp(-0.5 * c))
    c = c2
# the remaining corner (3x + 2y >= 6 never enters the panel, so nothing to do)

p.axes((0.5, 1.0, 1.5), (1, 2), "x", "", xfmt=tfmt)
p.text_px(p.x0 + 7, p.y0 - 2, "y", TEXT, 11.5, "start", False, True)

# level lines 3x + 2y = c and their labels, rotated along the lines
for cv in (1, 2, 3, 4):
    p.line([(0, cv / 2), (cv / 3, 0)], THEORY, 1.7)
    mx, my = (p.X(0) + p.X(cv / 3)) / 2, (p.Y(cv / 2) + p.Y(0)) / 2
    dxp, dyp = p.X(cv / 3) - p.X(0), p.Y(0) - p.Y(cv / 2)
    ang = math.degrees(math.atan2(dyp, dxp))
    s, co = math.sin(math.radians(ang)), math.cos(math.radians(ang))
    off = 5.5
    tx, ty = mx + s * off, my - co * off
    p.add('<text x="%.1f" y="%.1f" fill="%s" font-size="9.5" text-anchor="middle" '
          'transform="rotate(%.1f %.1f %.1f)">%s</text>'
          % (tx, ty, THEORY, ang, tx, ty, it("f") + " = 6e" + sups(MINUS_S + str(cv))))

# the joint density and the family of level lines, in the empty top-right corner
p.text_px(p.X(1.58), 38, it("f") + "(" + it("x") + ", " + it("y") + ") = 6e"
          + sups(MINUS_S + "3" + it("x") + MINUS_S + "2" + it("y")), THEORY, 11, "end", True)
p.text_px(p.X(1.58), 54, "düzey doğruları 3" + it("x") + " + 2" + it("y") + " = " + it("c"),
          THEORY, 10, "end")

# bottom marginal f_X(x) = 3 e^(-3x)
pb = Plot(100, 190, 240, 34, XR, (0.0, 3.4))
fx = lambda x: 3 * math.exp(-3 * x)
pts = [(XR[0] + (XR[1] - XR[0]) * k / 120, fx(XR[0] + (XR[1] - XR[0]) * k / 120)) for k in range(121)]
pb.polygon([(0, 0)] + pts + [(1.6, 0)], PRACTICE, 0.22)
pb.line(pts, PRACTICE, 1.7)
pb.line([(0, 0), (1.6, 0)], TEXT, 1.0, None, 0.45)
pb.text_px(pb.X(1.58), pb.y0 + 13, it("f") + subs(it("X")) + "(" + it("x") + ") = 3e"
           + sups(MINUS_S + "3" + it("x")), PRACTICE, 10, "end")

# left marginal f_Y(y) = 2 e^(-2y), value growing to the left
pl = Plot(36, 22, 46, 148, (2.3, 0.0), YR)
fy = lambda y: 2 * math.exp(-2 * y)
pts = [(fy(YR[0] + (YR[1] - YR[0]) * k / 120), YR[0] + (YR[1] - YR[0]) * k / 120) for k in range(121)]
pl.polygon([(0, 0)] + pts + [(0, 2.4)], PRACTICE, 0.22)
pl.line(pts, PRACTICE, 1.7)
pl.line([(0, 0), (0, 2.4)], TEXT, 1.0, None, 0.45)
pl.text_px(pl.x0 + 1, pl.y0 + 13, it("f") + subs(it("Y")) + "(" + it("y") + ") =", PRACTICE, 10, "start")
pl.text_px(pl.x0 + 1, pl.y0 + 30, "2e" + sups(MINUS_S + "2" + it("y")), PRACTICE, 10, "start")

# the conclusion
p.text_px(200, 244,
          '<tspan fill="%s">%s</tspan> = <tspan fill="%s">%s</tspan>   %s   bağımsız   %s   Cov(%s, %s) = 0'
          % (THEORY, it("f"), PRACTICE, it("f") + subs(it("X")) + " &#183; " + it("f") + subs(it("Y")),
             ARROW, ARROW, it("X"), it("Y")), TEXT, 11, "middle")

OUT["ustel-cift-destek"] = figure(
    400, 256, [p, pb, pl],
    "Birinci çeyrekte <em>f</em>(<em>x</em>, <em>y</em>) = 6e<sup>&#8722;3<em>x</em>&#8722;2<em>y</em></sup> "
    "ortak yoğunluğu. Yoğunluk yalnızca 3<em>x</em> + 2<em>y</em> toplamına bağlıdır; bu yüzden düzey "
    "eğrileri paralel doğrulardır ve gölge orijinden uzaklaştıkça açılır. Kenarlardaki marjinaller "
    "<em>f</em><sub><em>X</em></sub>(<em>x</em>) = 3e<sup>&#8722;3<em>x</em></sup> ve "
    "<em>f</em><sub><em>Y</em></sub>(<em>y</em>) = 2e<sup>&#8722;2<em>y</em></sup> üstel yoğunluklardır; "
    "çarpımları ortak yoğunluğu verdiğinden <em>X</em> ile <em>Y</em> bağımsızdır, dolayısıyla "
    "Cov(<em>X</em>, <em>Y</em>) = 0 olur.",
    aria="Birinci ceyrekte 6e ussu eksi 3x eksi 2y ortak yogunlugunun paralel duzey dogrulari, solan golge ve kenarlarda iki ustel marjinal")

# ============================================================ ustel-hafizasizlik
# Memorylessness of the exponential distribution (lambda = 1): the tail beyond s, shifted left by s
# and divided by P(X > s), coincides with the original density.
S_M = 1.0
TAIL_M = math.exp(-S_M)  # P(X > s) = e^{-s}


def f_m(x):
    return math.exp(-x) if x >= 0 else 0.0


def f_cond(t):
    # density of X - s given X > s: f(s + t) / P(X > s) = e^{-t}
    return f_m(S_M + t) / TAIL_M if t >= 0 else 0.0


p1 = Plot(44, 30, 226, 190, (-0.18, 4.2), (-0.09, 1.13))
p1.origin_axes("x", "y", xticks=(2, 3, 4), yticks=(0.5, 1), yfmt=tfmt)
panel_title(p1, "Üstel(1) yoğunluğu ve X &gt; s kuyruğu", THEORY)
tail = [(S_M, 0)] + [(S_M + (4.1 - S_M) * k / 120, f_m(S_M + (4.1 - S_M) * k / 120)) for k in range(121)] + [(4.1, 0)]
p1.polygon(tail, PRACTICE, 0.28)
curve(p1, f_m, 0, 4.1, THEORY, 2.2, 300)
p1.line([(-0.18, 0), (0, 0)], THEORY, 2.2)
dot(p1, (0, 1), THEORY, 3.4)
guide(p1, [(S_M, 0), (S_M, f_m(S_M))], PRACTICE, 0.8)
p1.label(S_M, 0, "s", 0, 15, PRACTICE, 11, "middle", True, True)
p1.label(1.8, 0.10, "P(X &gt; s) = e" + sups(MINUS_S + "s"), 0, 0, PRACTICE, 10.5, "start", True, True)
p1.label(2.2, 0.62, "f(x) = e" + sups(MINUS_S + "x"), 0, 0, THEORY, 10.5, "start", False, True)

p2 = Plot(322, 30, 226, 190, (-0.18, 4.2), (-0.09, 1.13))
p2.origin_axes("t", "y", xticks=(1, 2, 3, 4), yticks=(0.5, 1), yfmt=tfmt)
panel_title(p2, "kaydırılmış kuyruk: aynı eğri", PRACTICE)
curve(p2, f_m, 0, 4.1, THEORY, 3.4, 300)
p2.line([(-0.18, 0), (0, 0)], THEORY, 3.4)
curve(p2, f_cond, 0, 4.1, PRACTICE, 1.8, 300, dash="6,4")
dot(p2, (0, 1), THEORY, 3.4)
p2.label(0.55, 0.78, "f(t) = e" + sups(MINUS_S + "t"), 0, 0, THEORY, 10.5, "start", False, True)
p2.label(1.1, 0.52, "f(s + t) / P(X &gt; s)", 0, 0, PRACTICE, 10.5, "start", False, True)
p2.label(1.1, 0.52, "= e" + sups(MINUS_S + "(s+t)") + " / e" + sups(MINUS_S + "s") + " = e" + sups(MINUS_S + "t"),
         0, 15, PRACTICE, 10.5, "start", False, True)
p2.label(1.65, 0.30, "P(X &gt; s + t | X &gt; s) = P(X &gt; t)", 0, 0, TEXT, 10, "start", True, True)
OUT["ustel-hafizasizlik"] = figure(
    560, 244, [p1, p2],
    "Üstel dağılımın hafızasızlığı (&#955; = 1). Solda <em>s</em>'nin sağında kalan kuyruk, "
    "<em>P</em>(<em>X</em> &gt; <em>s</em>) = e<sup>&#8722;<em>s</em></sup> alanıdır. Sağda bu kuyruk <em>s</em> kadar sola kaydırılıp "
    "e<sup>&#8722;<em>s</em></sup>'e bölünmüştür: <em>X</em> &gt; <em>s</em> verildiğinde kalan sürenin yoğunluğu (kesikli) "
    "orijinal yoğunlukla birebir çakışır. Geçen <em>s</em> süresi, kalan süre hakkında hiçbir bilgi taşımaz: "
    "<em>P</em>(<em>X</em> &gt; <em>s</em> + <em>t</em> | <em>X</em> &gt; <em>s</em>) = <em>P</em>(<em>X</em> &gt; <em>t</em>).",
    css_class=WIDE,
    aria="Ustel yogunlukta s otesi kuyruk ve bu kuyrugun sola kaydirilip olceklenince orijinal yogunlukla cakismasi")

# ============================================================ ustel-lambda-karsilastirma
# Exponential distribution for lambda = 1 and 2: densities on the left, distribution functions on the right.
pa = Plot(46, 32, 220, 168, (-0.15, 4.1), (0.0, 2.15))
pa.axes((0, 1, 2, 3, 4), (0.5, 1.0, 1.5, 2.0), "x", "f(x)", yfmt=tfmt)
panel_title(pa, "yoğunluk  &#955;e" + sups("&#8722;&#955;x"), TEXT)
curve(pa, lambda x: 2 * math.exp(-2 * x), 0, 4.05, PRACTICE, 2.0, 300)
curve(pa, lambda x: math.exp(-x), 0, 4.05, THEORY, 2.0, 300)
dot(pa, (0, 2), PRACTICE, 3.4)
dot(pa, (0, 1), THEORY, 3.4)
pa.label(0.55, 2 * math.exp(-1.1), "&#955; = 2", 8, -2, PRACTICE, 10.5, "start", True, False)
pa.label(1.6, math.exp(-1.6), "&#955; = 1", 8, -4, THEORY, 10.5, "start", True, False)
pa.label(2.6, 1.55, "E(X) = 1/&#955;", 0, 0, TEXT, 10.5, "middle", False, True)
pa.label(2.6, 1.3, "Var(X) = 1/&#955;" + sups("2"), 0, 0, TEXT, 10.5, "middle", False, True)
pb = Plot(330, 32, 220, 168, (-0.15, 4.1), (0.0, 1.12))
pb.axes((0, 1, 2, 3, 4), (0.5, 1.0), "x", "F(x)", yfmt=tfmt)
panel_title(pb, "dağılım  1 &#8722; e" + sups("&#8722;&#955;x"), TEXT)
guide(pb, [(-0.15, 1), (4.1, 1)], TEXT, 0.35)
curve(pb, lambda x: 1 - math.exp(-2 * x), 0, 4.05, PRACTICE, 2.0, 300)
curve(pb, lambda x: 1 - math.exp(-x), 0, 4.05, THEORY, 2.0, 300)
pb.label(0.45, 1 - math.exp(-0.9), "&#955; = 2", -6, -8, PRACTICE, 10.5, "end", True, False)
pb.label(2.2, 1 - math.exp(-2.2), "&#955; = 1", 4, 16, THEORY, 10.5, "start", True, False)
OUT["ustel-lambda-karsilastirma"] = figure(
    570, 236, [pa, pb],
    "&#955; = 1 ve &#955; = 2 için üstel dağılım. Yoğunluk sıfırda &#955; değerinden başlayıp geometrik hızla "
    "azalır; &#955; büyüdükçe kütle sıfıra yığılır, ortalama 1/&#955; küçülür. Dağılım fonksiyonu "
    "1 &#8722; e<sup>&#8722;&#955;<em>x</em></sup> de aynı ölçüde daha hızlı 1'e yaklaşır.",
    css_class=WIDE,
    aria="Lambda 1 ve 2 icin ustel yogunluk egrileri solda, dagilim fonksiyonlari sagda")

# ============================================================ ustel-yogunluk-ve-dagilim
# Exponential density f(x) = e^{-x/5}/5 and its distribution function; F(a) as an area and as a point.
LAM_E = 0.2
A_E = 5.0


def f_exp(x):
    return LAM_E * math.exp(-LAM_E * x) if x >= 0 else 0.0


def F_exp(x):
    return 1 - math.exp(-LAM_E * x) if x >= 0 else 0.0


p1 = Plot(44, 30, 226, 190, (-1.8, 21.5), (-0.025, 0.245))
p1.origin_axes("x", "y", xticks=(10, 15, 20), yticks=(0.1, 0.2), yfmt=tfmt)
panel_title(p1, "yoğunluk f(x) = e" + sups(MINUS_S + "x/5") + "/5", THEORY)
area = [(0, 0)] + [(A_E * k / 40, f_exp(A_E * k / 40)) for k in range(41)] + [(A_E, 0)]
p1.polygon(area, PRACTICE, 0.25)
curve(p1, f_exp, 0, 21.0, THEORY, 2.2, 320)
p1.line([(-1.8, 0), (0, 0)], THEORY, 2.2)
dot(p1, (0, LAM_E), THEORY, 3.4)
guide(p1, [(A_E, 0), (A_E, f_exp(A_E))], PRACTICE, 0.7)
p1.label(A_E, 0, "a", 0, 15, PRACTICE, 11, "middle", True, True)
p1.label(2.3, 0.06, "F(a)", 0, 0, PRACTICE, 11, "middle", True, True)
p1.label(12.5, 0.14, "toplam alan 1", 0, 0, THEORY, 10.5, "middle", False, True)

p2 = Plot(322, 30, 226, 190, (-1.8, 21.5), (-0.1, 1.2))
p2.origin_axes("x", "y", xticks=(10, 15, 20), yticks=(0.5, 1), yfmt=tfmt)
panel_title(p2, "dağılım fonksiyonu F(x) = 1 " + MINUS_S + " e" + sups(MINUS_S + "x/5"), THEORY)
guide(p2, [(-1.8, 1), (21.5, 1)], TEXT, 0.35)
curve(p2, F_exp, 0, 21.0, THEORY, 2.2, 320)
p2.line([(-1.8, 0), (0, 0)], THEORY, 2.2)
guide(p2, [(A_E, 0), (A_E, F_exp(A_E))], PRACTICE, 0.7)
guide(p2, [(0, F_exp(A_E)), (A_E, F_exp(A_E))], PRACTICE, 0.7)
dot(p2, (A_E, F_exp(A_E)), PRACTICE, 4.0)
p2.label(A_E, 0, "a", 0, 15, PRACTICE, 11, "middle", True, True)
p2.label(0, F_exp(A_E), "F(a) = 0,63", -6, 4, PRACTICE, 10.5, "end", False, True)
p2.label(14, 0.72, "F" + PRIME + " = f", 0, 0, THEORY, 10.5, "middle", False, True)
OUT["ustel-yogunluk-ve-dagilim"] = figure(
    560, 244, [p1, p2],
    "Üstel yoğunluk <em>f</em>(<em>x</em>) = e<sup>&#8722;<em>x</em>/5</sup>/5 (<em>x</em> &#8805; 0) ve dağılım "
    "fonksiyonu <em>F</em>(<em>x</em>) = 1 &#8722; e<sup>&#8722;<em>x</em>/5</sup>. Solda <em>F</em>(<em>a</em>), "
    "yoğunluğun <em>a</em>'nın solunda kalan alanıdır; sağda aynı değer eğri üzerinde okunur. Yoğunluk sıfırda "
    "1/5'ten başlayıp söner; <em>F</em> sürekli olarak artar, 1'e yaklaşır ama hiçbir noktada 1'e ulaşmaz.",
    aria="Ustel yogunluk egrisi altinda F(a) alani ve dagilim fonksiyonu egrisi uzerinde ayni deger")

# ============================================================ uzunluk-yontemi-giris
# The "length method" on three warm-up examples: F(x) = length of (X <= x) / length of Omega.
OMEGA = "&#969;"
XW = "X(" + OMEGA + ")"


def panel(x0, xr, yr, title, omega, f, level, lo, hi, xt, yt, lo_lbl, hi_lbl, note1, note2, om_at):
    p = Plot(x0, 30, 150, 165, xr, yr)
    p.origin_axes(OMEGA, XW, xticks=xt, yticks=yt, xfmt=lambda t: fmt(t).replace("-", MINUS_S))
    panel_title(p, title, THEORY)
    # the sample space as a thick segment on the omega axis
    p.line([(omega[0], 0), (omega[1], 0)], TEXT, 3.2, None, 0.8)
    p.label(om_at, 0, "&#937;", 0, -6, TEXT, 10.5, "middle", False, True)
    # region below the level x over the event, then the event itself on the axis
    rect(p, lo, hi, 0, level, PRACTICE, 0.12)
    p.line([(lo, 0), (hi, 0)], PRACTICE, 7, None, 0.6)
    curve(p, f, omega[0], omega[1], THEORY, 2.2, 120)
    guide(p, [(min(lo, 0), level), (hi, level)], PRACTICE, 0.8)
    for e in (lo, hi):
        if e != 0:
            guide(p, [(e, 0), (e, level)], PRACTICE, 0.8)
            dot(p, (e, level), PRACTICE, 3.4)
    if lo_lbl:
        p.label(lo, 0, lo_lbl, 0, 15, PRACTICE, 11, "middle", True, True)
    p.label(hi, 0, hi_lbl, 0, 15, PRACTICE, 11, "middle", True, True)
    # notes under the panel
    p.text_px(p.x0 + p.w / 2 + 6, 212, note1, PRACTICE, 10.5, "middle", False, True)
    p.text_px(p.x0 + p.w / 2 + 6, 227, note2, THEORY, 10.5, "middle", True, True)
    return p


p1 = panel(36, (-0.22, 1.32), (-0.24, 1.32), XW + " = " + OMEGA, (0, 1), lambda w: w, 0.6,
           0, 0.6, (1,), (1,), "", "x", "uzunluk = x", "F(x) = x / 1 = x", 0.85)
p1.label(0, 0.6, "x", -6, 4, PRACTICE, 11.5, "end", True, True)

p2 = panel(226, (-0.55, 3.45), (-1.05, 6.85), XW + " = 2" + OMEGA, (0, 3), lambda w: 2 * w, 3,
           0, 1.5, (3,), (6,), "", "x/2", "uzunluk = x/2", "F(x) = (x/2) / 3 = x/6", 2.5)
p2.label(0, 3, "x", -6, 4, PRACTICE, 11.5, "end", True, True)

p3 = panel(416, (-1.36, 1.36), (-0.24, 1.32), XW + " = |" + OMEGA + "|", (-1, 1), abs, 0.5,
           -0.5, 0.5, (-1, 1), (1,), MINUS_S + "x", "x", "uzunluk = 2x", "F(x) = 2x / 2 = x", 0.82)
p3.label(0, 0.5, "x", -6, -5, PRACTICE, 11.5, "end", True, True)

OUT["uzunluk-yontemi-giris"] = figure(
    570, 240, [p1, p2, p3],
    "Uzunluk yöntemi: bir aralık üzerinde uzunluk ölçüsüyle kurulan olasılık uzayında "
    "<em>F</em>(<em>x</em>), (<em>X</em> &#8804; <em>x</em>) olayının uzunluğunun &#937;'nın uzunluğuna "
    "oranıdır. Her panelde <em>x</em> düzeyinin altında kalan &#969;'lar &#969; ekseninde taranmıştır; "
    "bu aralığın uzunluğu <em>x</em>'e bağlı olarak okunur ve &#937;'nın uzunluğuna (1, 3, 2) bölünür. "
    "Aynı <em>x</em> için taralı küme fonksiyona göre değişir: doğru için tek parça, mutlak değer için "
    "0'a göre simetrik bir aralık.",
    css_class=WIDE,
    aria="Uc panel: X(w)=w, X(w)=2w ve X(w)=|w| icin x duzeyinin altinda kalan w kumesi omega ekseninde taranmis; uzunluklari x, x/2 ve 2x")

# ============================================================ varyans-yayilma
# Two densities with the same mean mu = 0 but different spread: sigma = 0.6 (narrow) and sigma = 1.5 (wide).
# Below the axis, the interval [mu - sigma, mu + sigma] of each is marked as a bracket in its own colour.
def it(s):
    return '<tspan font-style="italic">%s</tspan>' % s


def gauss(sigma):
    return lambda x: math.exp(-x * x / (2 * sigma * sigma)) / (sigma * math.sqrt(2 * math.pi))


S_SMALL, S_BIG = 0.6, 1.5
SIG, MU = "&#963;", "&#956;"

p = Plot(40, 26, 330, 214, (-4.2, 4.2), (-0.34, 0.76))
p.origin_axes(it("x"), it("f") + "(" + it("x") + ")")
# hide the part of the vertical axis below the x axis: the brackets live there
p.add('<rect x="%.1f" y="%.1f" width="8" height="%.1f" fill="%s"/>'
      % (p.X(0) - 4, p.Y(0) + 2, p.y0 + p.h + 6 - p.Y(0), BG))
# dashed line at the common mean
guide(p, [(0, 0), (0, 0.70)], TEXT, 0.55)
p.label(0, 0, MU, 0, 14, TEXT, 11.5, "middle", False, True)
# the two densities
curve(p, gauss(S_SMALL), -2.6, 2.6, THEORY, 2.0, 240)
curve(p, gauss(S_BIG), -4.1, 4.1, PRACTICE, 2.0, 240)
p.label(0.62, gauss(S_SMALL)(0.62), SIG + " = 0,6", 9, -2, THEORY, 11, "start")
p.label(2.15, gauss(S_BIG)(2.15), SIG + " = 1,5", 8, -3, PRACTICE, 11, "start")


def bracket(y, sigma, color, note):
    """Horizontal bracket [mu - sigma, mu + sigma] below the axis with end ticks and a note."""
    t = 0.022
    p.line([(-sigma, y + t), (-sigma, y - t)], color, 1.5)
    p.line([(sigma, y + t), (sigma, y - t)], color, 1.5)
    p.line([(-sigma, y), (sigma, y)], color, 1.5)
    p.label(sigma, y, note, 9, 4, color, 11, "start")


bracket(-0.13, S_SMALL, THEORY, SIG + " küçük: [" + MU + MINUS_S + SIG + ", " + MU + "+" + SIG + "] dar")
bracket(-0.26, S_BIG, PRACTICE, SIG + " büyük: aralık geniş")

OUT["varyans-yayilma"] = figure(
    400, 255, [p],
    "Varyans, dağılımın ortalama etrafındaki yayılımını ölçer. İki yoğunluğun beklenen değeri aynı "
    "&#956; noktasıdır; dar eğrinin standart sapması &#963; = 0,6, geniş eğrininki &#963; = 1,5'tir. "
    "Eksenin altındaki parantezler [&#956; &#8722; &#963;, &#956; + &#963;] aralıklarını gösterir: kütle merkeze "
    "yığılmışsa varyans küçük, merkezden uzağa saçılmışsa büyüktür.",
    aria="Ayni ortalama etrafinda dar ve genis iki yogunluk egrisi; eksenin altinda her biri icin "
         "ortalama arti eksi standart sapma araligi")

# ============================================================ vektor-sema
# A random vector as a map Omega -> R^2: the sample space on the left, a small coordinate
# plane on the right, a Borel rectangle B and its preimage ((X, Y) in B) shaded alike.
def it(s):
    return '<tspan font-style="italic">%s</tspan>' % s


def px_arrow(p, x0, y0, x1, y1, color, width=0.9, head=5.0, opacity=0.6):
    """Thin arrow given directly in pixel coordinates (spans two panels)."""
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy) or 1.0
    ux, uy = dx / L, dy / L
    sx, sy = x1 - ux * head * 0.8, y1 - uy * head * 0.8
    p.add('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="%.1f" opacity="%.2f"/>'
          % (x0, y0, sx, sy, color, width, opacity))
    px_, py_ = -uy, ux
    hw = head * 0.42
    p.add('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s" opacity="%.2f"/>'
          % (x1, y1, x1 - ux * head + px_ * hw, y1 - uy * head + py_ * hw,
             x1 - ux * head - px_ * hw, y1 - uy * head - py_ * hw, color, opacity))


# left panel: the sample space, drawn in pixel-like data units (52 px per unit, equal aspect)
p = Plot(20, 16, 520, 214, (0, 10), (-0.12, 4.0))
OX, OY, ORX, ORY = 2.0, 2.0, 1.75, 1.6
p.add('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s" fill-opacity="0.06" stroke="%s" stroke-width="1.2"/>'
      % (p.X(OX), p.Y(OY), p.R(ORX), p.R(ORY), TEXT, TEXT))
p.label(OX, OY + ORY - 0.32, "&#937;", 0, 4, TEXT, 13, "middle", True, True)
# the preimage of B: a smooth blob inside Omega, shaded like B
pre = blob(2.45, 1.75, 0.66, [(0.10, 2, 0.6), (0.06, 3, 1.9)])
closed_curve(p, pre, PRACTICE, 1.4, None, PRACTICE, 0.28)

# right panel: the coordinate plane (45 px per unit on both axes)
q = Plot(345, 30, 180, 160, (-0.45, 3.55), (-0.5, 3.056))
q.origin_axes("x", "y")
BX0, BX1, BY0, BY1 = 1.3, 2.6, 1.0, 2.1
rect(q, BX0, BX1, BY0, BY1, PRACTICE, 0.28, PRACTICE, 1.4)
q.label(BX0, BY1, "B", 6, 14, PRACTICE, 12.5, "start", True, True)

# outcomes and their images: three inside the preimage -> inside B, two outside -> outside B
INSIDE = [((2.25, 1.95), (1.7, 1.75)), ((2.7, 1.55), (2.25, 1.25)), ((2.2, 1.45), (1.55, 1.3))]
OUTSIDE = [((1.05, 2.45), (0.5, 2.35)), ((1.35, 0.95), (3.05, 0.4))]
for (w, img) in INSIDE + OUTSIDE:
    col = PRACTICE if (w, img) in INSIDE else TEXT
    dot(p, w, col, 3.2)
    dot(q, img, col, 3.2)
    x0, y0 = p.X(w[0]) + 4, p.Y(w[1]) - 1
    x1, y1 = q.X(img[0]) - 5, q.Y(img[1]) + 1
    px_arrow(p, x0, y0, x1, y1, col, 0.9, 5.5, 0.55)
p.label(2.25, 1.95, "&#969;", -6, -4, PRACTICE, 11, "end", False, True)
p.label(1.05, 2.45, "&#969;&#8242;", -6, 3, TEXT, 11, "end", False, True)
p.label(OX, 0.02, "taralı olay: (" + it("X") + ", " + it("Y") + ") " + it("B") + " içinde", 0, 4, PRACTICE, 10.5, "middle", False, True)

# the map itself: a thick arrow between the two pictures, at the top
p.arrow((3.9, 3.55), (5.95, 3.55), TEXT, 1.6, 8.0)
p.label(4.92, 3.55, "(" + it("X") + ", " + it("Y") + ") : &#937; &#8594; &#8477;" + sups("2"), 0, -9, TEXT, 12, "middle", True)
p.label(4.92, 3.55, "&#969; &#8594; (" + it("X") + "(&#969;), " + it("Y") + "(&#969;))", 0, 16, TEXT, 10.5, "middle", False, True)
# the distribution: probability of B is the probability of its preimage
p.text_px(400, 227, it("P") + subs("(" + it("X") + "," + it("Y") + ")") + "(" + it("B") + ") = " + it("P") +
          "((" + it("X") + ", " + it("Y") + ") " + it("B") + " içinde)", TEXT, 12, "middle", True)
OUT["vektor-sema"] = figure(
    560, 240, [p, q],
    "Rastgele vektör, örnek uzayın her sonucuna bir sayı çifti (bir düzlem noktası) eşleyen fonksiyondur. "
    "Düzlemde bir <em>B</em> Borel kümesi (burada bir dikdörtgen) alındığında, görüntüsü <em>B</em>'ye düşen "
    "sonuçların kümesi &#937;'da bir olaydır: ((<em>X</em>, <em>Y</em>) &#8712; <em>B</em>) önimajı. "
    "Vektörün dağılımı <em>P</em><sub>(<em>X</em>,<em>Y</em>)</sub>, her <em>B</em>'ye bu önimajın olasılığını "
    "verir; böylece &#937; üzerindeki olasılık düzleme taşınır.",
    css_class=WIDE,
    aria="Ornek uzay elipsinden koordinat duzlemine giden rastgele vektor; duzlemdeki B dikdortgeni ve "
         "Omega icindeki onimaji ayni renkte taranmis, birkac sonuc oklarla goruntulerine baglanmis")

# ============================================================ venn-olay-islemleri
# Four small Venn panels: A u B, A n B, A^c, A \ B inside the sample space.
R_V, D_V = 0.95, 1.1          # circle radius and centre distance (they overlap)


def _arc(cx, cy, a0, a1, n=48):
    return [(cx + R_V * math.cos(a0 + (a1 - a0) * k / n), cy + R_V * math.sin(a0 + (a1 - a0) * k / n))
            for k in range(n + 1)]


def lens(xa, xb, y):
    """A n B as a polygon (arc of A inside B, then arc of B inside A)."""
    th = math.acos((D_V / 2) / R_V)
    return _arc(xa, y, -th, th) + _arc(xb, y, math.pi - th, math.pi + th)


def crescent(xa, xb, y):
    """A \\ B as a polygon (arc of A outside B, then arc of B inside A, reversed)."""
    th = math.acos((D_V / 2) / R_V)
    return _arc(xa, y, th, 2 * math.pi - th) + _arc(xb, y, math.pi + th, math.pi - th)


PW_V, PH_V, XR_V = 122.0, 100.0, 2.15
# equal px-per-unit on both axes, so a circle of radius R_V stays a circle
YR_V = XR_V * PH_V / PW_V


def venn_panel(px, title, shade):
    q = Plot(px, 34, PW_V, PH_V, (-XR_V, XR_V), (-YR_V, YR_V))
    xa, xb, y = -D_V / 2, D_V / 2, 0.0
    # the sample space
    q.polygon([(-2.05, -1.62), (2.05, -1.62), (2.05, 1.62), (-2.05, 1.62)], TEXT, 0.0, TEXT, 1.0)
    if shade == "birlesim":
        q.polygon(_arc(xa, y, 0, 2 * math.pi), THEORY, 0.28)
        q.polygon(_arc(xb, y, 0, 2 * math.pi), THEORY, 0.28)
    elif shade == "kesisim":
        q.polygon(lens(xa, xb, y), THEORY, 0.42)
    elif shade == "tumleyen":
        # rectangle with a circular hole: even-odd fill on a raw path
        rect_pts = [(-2.05, -1.62), (2.05, -1.62), (2.05, 1.62), (-2.05, 1.62)]
        d = "M" + " L".join(q.P(x, yy) for x, yy in rect_pts) + " Z "
        d += "M" + " L".join(q.P(x, yy) for x, yy in _arc(xa, y, 0, 2 * math.pi)) + " Z"
        q.add('<path d="%s" fill="%s" fill-opacity="0.28" fill-rule="evenodd" stroke="none"/>' % (d, THEORY))
    elif shade == "fark":
        q.polygon(crescent(xa, xb, y), THEORY, 0.42)
    q.circle(xa, y, R_V, TEXT, 1.3)
    q.circle(xb, y, R_V, TEXT, 1.3)
    q.label(xa - 0.35, 0.55, "A", 0, 0, TEXT, 11.5, "middle", True, True)
    q.label(xb + 0.35, 0.55, "B", 0, 0, TEXT, 11.5, "middle", True, True)
    q.text_px(q.x0 + q.w - 4, q.y0 + 12, "&#937;", TEXT, 10.5, "end", False, True)
    q.text_px(q.x0 + q.w / 2, q.y0 + q.h + 18, title, THEORY, 11.5, "middle", True, False)
    return q


panels = [venn_panel(14, "A veya B", "birlesim"),
          venn_panel(152, "A ve B", "kesisim"),
          venn_panel(290, "A değil", "tumleyen"),
          venn_panel(428, "A ama B değil", "fark")]
OUT["venn-olay-islemleri"] = figure(
    564, 172, panels,
    "Olay işlemlerinin Venn şemaları. Dikdörtgen örnek uzay &#937;'yı, daireler <em>A</em> ve <em>B</em> "
    "olaylarını gösterir. Soldan sağa: birleşim <em>A</em> &#8746; <em>B</em>, kesişim <em>A</em> &#8745; <em>B</em>, "
    "tümleyen <em>A</em><sup>c</sup> ve fark <em>A</em> &#8726; <em>B</em> = <em>A</em> &#8745; <em>B</em><sup>c</sup> "
    "(<em>A</em>'nın gerçekleşip <em>B</em>'nin gerçekleşmediği sonuçlar).",
    css_class=WIDE,
    aria="Dort Venn semasi: birlesim, kesisim, tumleyen ve fark olaylari taranmis")

# ============================================================ yildiz-cubuk
# Stars-and-bars encoding of the solutions of x + y + z = 7: two example strings,
# the parts labelled, and the count C(9,2) = 36. No axes; the panel is a pixel canvas.
W_SB, H_SB = 400, 214
X0_SB, PITCH_SB = 56, 28          # first slot centre and slot spacing (9 slots: 56 .. 280)
NAMES_SB = ("x", "y", "z")


def slot_x(i):
    return X0_SB + PITCH_SB * i


def star(p, cx, cy, r=7.0, color=THEORY):
    pts = []
    for k in range(10):
        ang = -math.pi / 2 + k * math.pi / 5
        rr = r if k % 2 == 0 else r * 0.42
        pts.append("%.1f,%.1f" % (cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    p.add('<polygon points="%s" fill="%s" stroke="none"/>' % (" ".join(pts), color))


def bar(p, cx, cy, half=9.5, color=PRACTICE):
    p.add('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="2.6" stroke-linecap="round"/>'
          % (cx, cy - half, cx, cy + half, color))


def brace(p, xa, xb, y, color=TEXT):
    p.add('<path d="M%.1f,%.1f V%.1f H%.1f V%.1f" fill="none" stroke="%s" stroke-width="1" opacity="0.55"/>'
          % (xa, y - 4, y, xb, y - 4, color))


def italic(s):
    return '<tspan font-style="italic">%s</tspan>' % s


def row(p, cy, seq, tuple_text):
    """seq: string of '*' and '|' with 9 symbols; draws it, braces each part, labels x, y, z."""
    for i, ch in enumerate(seq):
        if ch == "*":
            star(p, slot_x(i), cy)
        else:
            bar(p, slot_x(i), cy)
    # split into parts (lists of star slot indices)
    parts, cur = [], []
    for i, ch in enumerate(seq):
        if ch == "|":
            parts.append(cur)
            cur = []
        else:
            cur.append(i)
    parts.append(cur)
    bars = [i for i, ch in enumerate(seq) if ch == "|"]
    yb, yl = cy + 17, cy + 32
    for k, part in enumerate(parts):
        if part:
            xa, xb = slot_x(part[0]) - 9, slot_x(part[-1]) + 9
        else:
            if k == 0:
                c = slot_x(bars[0]) - 15
            elif k == len(parts) - 1:
                c = slot_x(bars[-1]) + 15
            else:
                c = (slot_x(bars[k - 1]) + slot_x(bars[k])) / 2
            xa, xb = c - 4, c + 4
        brace(p, xa, xb, yb)
        p.text_px((xa + xb) / 2, yl, italic(NAMES_SB[k]) + " = %d" % len(part), TEXT, 11, "middle")
    p.text_px(312, cy + 4, ARROW + " " + tuple_text, TEXT, 12, "start", True)


p = Plot(0, 0, W_SB, H_SB, (0, W_SB), (0, H_SB))
# header and slot numbers
p.text_px((slot_x(0) + slot_x(8)) / 2, 24,
          italic("x") + " + " + italic("y") + " + " + italic("z") + " = 7", TEXT, 12.5, "middle", True)
p.add('<g fill="%s" font-size="9.5" opacity="0.5">%s</g>'
      % (TEXT, "".join('<text x="%.1f" y="45" text-anchor="middle">%d</text>' % (slot_x(i), i + 1) for i in range(9))))
# the two example strings
row(p, 70, "**|****|*", "(2, 4, 1)")
row(p, 136, "|*******|", "(0, 7, 0)")
# the count
p.text_px(slot_x(0) - 9, 199, "7 yıldız + 2 çubuk = 9 yer", TEXT, 11, "start")
p.text_px(382, 199, "C(9, 7) = C(9, 2) = 36", TEXT, 12, "end", True)

OUT["yildiz-cubuk"] = figure(
    W_SB, H_SB, [p],
    "Yıldız–çubuk kodlaması. <em>x</em> + <em>y</em> + <em>z</em> = 7 denkleminin her çözümü, 7 yıldız ile "
    "2 çubuktan oluşan 9 simgelik bir diziye karşılık gelir: çubuklar diziyi üç parçaya böler, her parçadaki "
    "yıldız sayısı bir bilinmeyenin değeridir; boş parça 0 demektir. Dizi, 9 yerden yıldızların (ya da "
    "çubukların) yerini seçmekle belirlenir, dolayısıyla çözüm sayısı C(9, 7) = C(9, 2) = 36'dır.",
    aria="Yildiz-cubuk kodlamasi: x+y+z=7 icin (2,4,1) ve (0,7,0) cozumlerinin yildiz ve cubuk dizileri, 9 yer ve C(9,2)=36")

# ============================================================ yogunluk-alan-olasilik
# Interval probability P(a < X <= b): area under the density on the left, F(b) - F(a) on the right.
# Density f(x) = x e^{-x} (x > 0), F(x) = 1 - (1 + x) e^{-x}; a = 0.5, b = 1.5.
A_I, B_I = 0.5, 1.5


def f_gam(x):
    return x * math.exp(-x) if x > 0 else 0.0


def F_gam(x):
    return 1 - (1 + x) * math.exp(-x) if x > 0 else 0.0


p1 = Plot(44, 30, 226, 190, (-0.5, 5.6), (-0.04, 0.46))
p1.origin_axes("x", "y", xticks=(3, 5), yticks=(0.2, 0.4), yfmt=tfmt)
panel_title(p1, "yoğunluk f(x) = x e" + sups(MINUS_S + "x"), THEORY)
area = [(A_I, 0)] + [(A_I + (B_I - A_I) * k / 40, f_gam(A_I + (B_I - A_I) * k / 40)) for k in range(41)] + [(B_I, 0)]
p1.polygon(area, PRACTICE, 0.3)
curve(p1, f_gam, 0, 5.5, THEORY, 2.2, 320)
p1.line([(-0.5, 0), (0, 0)], THEORY, 2.2)
guide(p1, [(A_I, 0), (A_I, f_gam(A_I))], PRACTICE, 0.8)
guide(p1, [(B_I, 0), (B_I, f_gam(B_I))], PRACTICE, 0.8)
p1.label(A_I, 0, "a", 0, 15, PRACTICE, 11, "middle", True, True)
p1.label(B_I, 0, "b", 0, 15, PRACTICE, 11, "middle", True, True)
p1.label(3.6, 0.335, "P(a &lt; X " + LEQ_S + " b)", 0, 0, PRACTICE, 11, "middle", True, True)
p1.label(3.6, 0.275, "= taralı alan " + "&#8776; 0,35", 0, 0, PRACTICE, 10.5, "middle", False, True)

p2 = Plot(322, 30, 226, 190, (-0.5, 5.6), (-0.1, 1.2))
p2.origin_axes("x", "y", xticks=(3, 5), yticks=(1,), yfmt=tfmt)
panel_title(p2, "dağılım fonksiyonu F(x)", THEORY)
guide(p2, [(-0.5, 1), (5.6, 1)], TEXT, 0.35)
curve(p2, F_gam, 0, 5.5, THEORY, 2.2, 320)
p2.line([(-0.5, 0), (0, 0)], THEORY, 2.2)
FA, FB = F_gam(A_I), F_gam(B_I)
guide(p2, [(A_I, 0), (A_I, FA)], PRACTICE, 0.8)
guide(p2, [(B_I, 0), (B_I, FB)], PRACTICE, 0.8)
guide(p2, [(0, FA), (2.4, FA)], PRACTICE, 0.8)
guide(p2, [(0, FB), (2.4, FB)], PRACTICE, 0.8)
dot(p2, (A_I, FA), PRACTICE, 4.0)
dot(p2, (B_I, FB), PRACTICE, 4.0)
p2.label(A_I, 0, "a", 0, 15, PRACTICE, 11, "middle", True, True)
p2.label(B_I, 0, "b", 0, 15, PRACTICE, 11, "middle", True, True)
p2.label(0, FA, "F(a)", -5, 3, PRACTICE, 10.5, "end", False, True)
p2.label(0, FB, "F(b)", -5, 4, PRACTICE, 10.5, "end", False, True)
p2.arrow((2.3, FA + 0.02), (2.3, FB - 0.02), PRACTICE, 1.3, 6.0)
p2.arrow((2.3, FB - 0.02), (2.3, FA + 0.02), PRACTICE, 1.3, 6.0)
p2.label(2.5, (FA + FB) / 2, "F(b) " + MINUS_S + " F(a)", 0, 4, PRACTICE, 10.5, "start", True, True)
p2.label(4.0, 0.68, "F" + PRIME + " = f", 0, 0, THEORY, 10.5, "middle", False, True)
OUT["yogunluk-alan-olasilik"] = figure(
    560, 244, [p1, p2],
    "Aralık olasılığının iki görünümü. Solda <em>P</em>(<em>a</em> &lt; <em>X</em> &#8804; <em>b</em>), yoğunluk "
    "eğrisinin altında <em>a</em> ile <em>b</em> arasında kalan alandır; sağda aynı sayı dağılım fonksiyonunun "
    "iki değeri arasındaki fark <em>F</em>(<em>b</em>) &#8722; <em>F</em>(<em>a</em>) olarak okunur. Sürekli değişkende "
    "uç noktalar sıfır olasılık taşıdığından aralığın açık ya da kapalı olması sonucu değiştirmez; "
    "dört aralık olasılığı da bu alana eşittir.",
    css_class=WIDE,
    aria="Solda yogunluk egrisi altinda a ile b arasindaki tarali alan, sagda dagilim fonksiyonunda F(b) eksi F(a) farki")

# ============================================================ zar-ikili-bagimsiz
# Two dice: the 36 outcomes as a grid; A = first is 2, B = second is 5, C = sum is 7.
p = Plot(60, 24, 226, 226, (0.3, 6.7), (0.3, 6.7))
# grid
for k in range(7):
    p.line([(0.5 + k, 0.5), (0.5 + k, 6.5)], TEXT, 0.8, None, 0.35)
    p.line([(0.5, 0.5 + k), (6.5, 0.5 + k)], TEXT, 0.8, None, 0.35)
for x in range(1, 7):
    p.label(x, 0.5, str(x), 0, 15, TEXT, 10.5, "middle", False, False)
    p.label(0.5, x, str(x), -8, 4, TEXT, 10.5, "end", False, False)
p.label(3.5, 0.5, "birinci zar (x)", 0, 32, TEXT, 10.5, "middle", False, True)
p.text_px(p.x0 - 44, p.y0 + 8, "ikinci zar (y)", TEXT, 10.5, "start", False, True)
# A: x = 2 (column), B: y = 5 (row), C: x + y = 7 (anti-diagonal)
for y in range(1, 7):
    rect(p, 2 - 0.5, 2 + 0.5, y - 0.5, y + 0.5, THEORY, 0.22)
for x in range(1, 7):
    rect(p, x - 0.5, x + 0.5, 5 - 0.5, 5 + 0.5, PRACTICE, 0.22)
for x in range(1, 7):
    y = 7 - x
    p.circle(x, y, 0.33, BASE, 1.8)
dot(p, (2, 5), TEXT, 4.6)
p.text_px(p.x0 + p.w + 30, p.y0 + 30, "A: x = 2  (sütun)", THEORY, 11, "start", True, False)
p.text_px(p.x0 + p.w + 30, p.y0 + 52, "B: y = 5  (satır)", PRACTICE, 11, "start", True, False)
p.text_px(p.x0 + p.w + 30, p.y0 + 74, "C: x + y = 7  (çember)", BASE, 11, "start", True, False)
p.text_px(p.x0 + p.w + 30, p.y0 + 112, "her biri 6/36 = 1/6", TEXT, 10.5, "start", False, True)
p.text_px(p.x0 + p.w + 30, p.y0 + 132, "ikili kesişimler tek nokta: 1/36 = 1/6 &#183; 1/6", TEXT, 10.5, "start", False, True)
p.text_px(p.x0 + p.w + 30, p.y0 + 152, "A &#8745; B &#8745; C = {(2, 5)}: 1/36 &#8800; 1/216", TEXT, 10.5, "start", False, True)
OUT["zar-ikili-bagimsiz"] = figure(
    560, 262, [p],
    "İki zar atışının 36 sonucu. <em>A</em> (ilk zar 2) bir sütun, <em>B</em> (ikinci zar 5) bir satır, "
    "<em>C</em> (toplam 7) bir köşegendir; üçünün de olasılığı 1/6'dır ve her ikili kesişim tek bir kareden "
    "oluşur, yani olaylar ikişer ikişer bağımsızdır. Ama üçlü kesişim de aynı tek kare (2, 5)'tir: "
    "1/36 &#8800; (1/6)<sup>3</sup>, dolayısıyla üçü birlikte bağımsız değildir.",
    css_class=WIDE,
    aria="Iki zar atisinin 36 sonucu izgarada; bir sutun, bir satir ve bir kosegen olarak uc olay")

# ============================================================ zar-mutlak-fark
# Absolute difference of two dice: unequal masses (bars) and unequal steps (distribution function).
F36 = {0: 6, 1: 10, 2: 8, 3: 6, 4: 4, 5: 2}          # numerators of f(k) = F36[k]/36
CUM = {}                                              # cumulative numerators 6, 16, 24, 30, 34, 36
run = 0
for k in range(6):
    run += F36[k]
    CUM[k] = run


def y36(v):
    k = round(v * 36)
    return "1" if k == 36 else "%d/36" % k


p1 = Plot(52, 30, 218, 186, (-0.7, 5.9), (0.0, 0.335))
p1.axes((0, 1, 2, 3, 4, 5), (6 / 36, 10 / 36), "x", "f(x)", yfmt=y36)
panel_title(p1, "olasılık fonksiyonu", THEORY)
for k in range(6):
    v = F36[k] / 36
    p1.line([(k, 0), (k, v)], THEORY, 3.2)
    dot(p1, (k, v), THEORY, 3.6)
    p1.label(k, v, "%d/36" % F36[k], 0, -9, TEXT, 9.5, "middle", False, False)

p2 = Plot(322, 30, 222, 186, (-1.0, 6.7), (-0.06, 1.12))
p2.axes((0, 1, 2, 3, 4, 5), (16 / 36, 24 / 36, 1.0), "x", "F(x)", yfmt=y36)
panel_title(p2, "dağılım fonksiyonu", THEORY)
p2.line([(-0.95, 0), (0, 0)], THEORY, 2.0)
for k in range(6):
    lo = (CUM[k - 1] / 36) if k > 0 else 0.0
    hi = CUM[k] / 36
    nxt = k + 1 if k < 5 else 6.65
    p2.line([(k, hi), (nxt, hi)], THEORY, 2.0)
    guide(p2, [(k, lo), (k, hi)], THEORY, 0.45)
    dot(p2, (k, hi), THEORY, 3.4)
    if k < 5:
        hollow(p2, (k + 1, hi), THEORY, 3.4, 1.4)
hollow(p2, (0, 0), THEORY, 3.4, 1.4)
guide(p2, [(-1.0, 16 / 36), (1, 16 / 36)], TEXT, 0.3)
guide(p2, [(-1.0, 24 / 36), (2, 24 / 36)], TEXT, 0.3)
p2.label(1.55, 11 / 36, "sıçrama = f(1) = 10/36", 7, 4, PRACTICE, 10, "start", False, True)
p2.arrow((1.55, 6 / 36 + 0.02), (1.55, 16 / 36 - 0.02), PRACTICE, 1.3, 6.0)
p2.arrow((1.55, 16 / 36 - 0.02), (1.55, 6 / 36 + 0.02), PRACTICE, 1.3, 6.0)

OUT["zar-mutlak-fark"] = figure(
    560, 240, [p1, p2],
    "Düzgün iki zarın gösterdiği sayıların mutlak farkı <em>X</em> = |<em>i</em> &#8722; <em>j</em>|. Solda "
    "olasılık fonksiyonu: kütleler eşit değildir, en olası fark 0 değil 1'dir (10/36). Sağda dağılım "
    "fonksiyonu: basamak yükseklikleri de eşit değildir; her basamak o noktanın kütlesi kadardır ve "
    "merdiven 6/36'dan başlayıp 16/36, 24/36, 30/36, 34/36 düzeylerinden geçerek 1'e ulaşır.",
    css_class=WIDE,
    aria="Iki zarin mutlak farki icin esit olmayan yukseklikli olasilik cubuklari ve esit olmayan basamakli dagilim fonksiyonu")

# ============================================================ zar-olasilik-ve-dagilim
# A fair die: probability function (bars) and distribution function (steps), side by side.
def sixths(v):
    k = round(v * 6)
    return "1" if k == 6 else "%d/6" % k


p1 = Plot(48, 30, 222, 186, (0.2, 7.3), (0.0, 0.24))
p1.axes((1, 2, 3, 4, 5, 6), (1 / 6,), "x", "f(x)", yfmt=sixths)
panel_title(p1, "olasılık fonksiyonu", THEORY)
for k in range(1, 7):
    p1.line([(k, 0), (k, 1 / 6)], THEORY, 3.2)
    dot(p1, (k, 1 / 6), THEORY, 3.6)
guide(p1, [(0.2, 1 / 6), (7.3, 1 / 6)], TEXT, 0.3)

p2 = Plot(322, 30, 222, 186, (-0.4, 7.6), (-0.06, 1.12))
p2.axes((1, 2, 3, 4, 5, 6), (1 / 6, 3 / 6, 5 / 6, 1.0), "x", "F(x)", yfmt=sixths)
panel_title(p2, "dağılım fonksiyonu", THEORY)
p2.line([(-0.35, 0), (1, 0)], THEORY, 2.0)
for k in range(1, 7):
    lo, hi = (k - 1) / 6, k / 6
    nxt = k + 1 if k < 6 else 7.5
    p2.line([(k, hi), (nxt, hi)], THEORY, 2.0)
    guide(p2, [(k, lo), (k, hi)], THEORY, 0.45)
    dot(p2, (k, hi), THEORY, 3.4)
    if k < 6:
        hollow(p2, (k + 1, hi), THEORY, 3.4, 1.4)
hollow(p2, (1, 0), THEORY, 3.4, 1.4)
p2.label(4.05, 3 / 6, "sıçrama = f(4) = 1/6", 8, 12, PRACTICE, 10, "start", False, True)
OUT["zar-olasilik-ve-dagilim"] = figure(
    560, 240, [p1, p2],
    "Düzgün bir zarda gelen sayı <em>X</em>. Solda olasılık fonksiyonu: altı noktada eşit kütle 1/6. Sağda "
    "dağılım fonksiyonu: her tam sayıda 1/6'lık bir basamak. İki gösterim birbirini belirler — basamağın "
    "yüksekliği kütleyi, kütlelerin birikimi basamakları verir.",
    aria="Zar icin olasilik fonksiyonu cubuklari ve basamakli dagilim fonksiyonu")


# ---------------------------------------------------------------------------
for name, content in OUT.items():
    with io.open(os.path.join(OUT_DIR, "probability-%s.md" % name), "w", encoding="utf-8") as f:
        f.write(content)
print("generated:", ", ".join(OUT))
