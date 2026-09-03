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
