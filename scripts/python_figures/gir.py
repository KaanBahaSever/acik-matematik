# -*- coding: utf-8 -*-
"""
Figures of the chapter "Python ile İlk Adımlar: Sayılar, Değişkenler ve
İfadeler" (dersler/python-bilimsel/python-ile-ilk-adimlar.qmd).

Figures go INSIDE the box they explain (theorem, example, exercise or
callout) or in the running text right after the paragraph that introduces
them, never inside a definition box, never inside a collapsed solution and
never directly under a heading. The figures are NOT produced at build time.
Run

    python scripts/python_figures/gir.py
    python scripts/center_figures.py "python-gir-*.md"
    python scripts/check_figure_labels.py "scripts/_figures/python-gir-*.md"

and paste the markup of scripts/_figures/python-gir-<name>.md into the .qmd.
Captions are Turkish on purpose; aria labels are plain ASCII.

Every plotted number is computed here with the same Python expressions the
chapter runs (divmod, the toy floating-point system, math.ulp, the sequence
(1 + 1/n)**n, cmath.exp and Fraction.limit_denominator), so the drawings match
the printed outputs exactly.
"""
import cmath
import math
import sys
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import (Plot, figure, cplane, WIDE, TEXT, THEORY, PRACTICE,  # noqa: E402
                      BASE, REMARK, BG)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "python-gir-"

MINUS = "&#8722;"
EPS = "&#949;"
OMEGA = "&#969;"
CDOT = "&#183;"


def save(name, markup):
    (OUT_DIR / f"{PREFIX}{name}.md").write_text(markup, encoding="utf-8", newline="\n")
    print(f"{PREFIX}{name}.md")


def it(s):
    """Italic run inside an SVG <text>."""
    return f'<tspan font-style="italic">{s}</tspan>'


def sub(s, size=10):
    """Subscript inside an SVG <text>; the zero-width space resets the baseline."""
    return f'<tspan font-size="{size}" dy="3.5">{s}</tspan><tspan dy="-3.5">&#8203;</tspan>'


def sup(s, size=10):
    """Superscript inside an SVG <text>."""
    return f'<tspan font-size="{size}" dy="-5">{s}</tspan><tspan dy="5">&#8203;</tspan>'


def num(v):
    """Integer with a true minus sign."""
    return str(v).replace("-", MINUS)


def dec(v, digits=4):
    """Decimal comma and a true minus sign: 0.3125 -> '0,3125'."""
    s = f"{v:.{digits}f}".rstrip("0").rstrip(".")
    if s in ("-0", ""):
        s = "0"
    return s.replace(".", ",").replace("-", MINUS)


def pow10(k):
    """'10' with a superscript exponent, '1' for k = 0."""
    if k == 0:
        return "1"
    return "10" + sup(num(k))


def hline_axis(p, y, x0, x1, opacity=0.55):
    """A horizontal number line in data coordinates with an arrowhead on the right."""
    X0, X1, Y = p.X(x0), p.X(x1), p.Y(y)
    p.add(f'<g stroke="{TEXT}" stroke-width="1.1" opacity="{opacity}" fill="{TEXT}">'
          f'<line x1="{X0:.1f}" y1="{Y:.1f}" x2="{X1:.1f}" y2="{Y:.1f}"/>'
          f'<polygon points="{X1 + 8:.1f},{Y:.1f} {X1:.1f},{Y - 3.5:.1f} {X1:.1f},{Y + 3.5:.1f}" '
          f'stroke="none"/></g>')


def tick(p, x, y, half, opacity=0.6):
    X, Y = p.X(x), p.Y(y)
    p.add(f'<line x1="{X:.1f}" y1="{Y - half:.1f}" x2="{X:.1f}" y2="{Y + half:.1f}" '
          f'stroke="{TEXT}" stroke-width="1" opacity="{opacity}"/>')


def rect(p, xa, xb, y_px_top, height, color, fill_opacity=0.18, width=1.2):
    """Rectangle spanning data x in [xa, xb], top edge at a pixel y."""
    X0, X1 = sorted((p.X(xa), p.X(xb)))
    p.add(f'<rect x="{X0:.1f}" y="{y_px_top:.1f}" width="{X1 - X0:.1f}" height="{height:.1f}" '
          f'fill="{color}" fill-opacity="{fill_opacity}" stroke="{color}" stroke-width="{width}"/>')


def bracket_below(p, xa, xb, y_px, color=TEXT, opacity=0.65):
    """A flat bracket under a stretch of a number line, ends turned up."""
    X0, X1 = p.X(xa), p.X(xb)
    p.add(f'<path d="M{X0 + 1:.1f},{y_px - 5:.1f} L{X0 + 1:.1f},{y_px:.1f} L{X1 - 1:.1f},{y_px:.1f} '
          f'L{X1 - 1:.1f},{y_px - 5:.1f}" fill="none" stroke="{color}" stroke-width="1.1" '
          f'opacity="{opacity}"/>')


# ============================================================
# tam-bolme: divmod(17, 5) and divmod(-17, 5) on the number line
# ============================================================
W1, H1 = 640, 270
XR = (-25, 21)
rows = []
for a, base_y in ((17, 70), (-17, 200)):
    b = 5
    q, r = divmod(a, b)
    p = Plot(22, base_y - 50, 596, 50, XR, (0, 1))    # data y = 0 is the number line
    hline_axis(p, 0, XR[0] + 0.3, XR[1] - 0.6)
    for t in range(XR[0] + 1, XR[1]):
        tick(p, t, 0, 4.5 if t % 5 == 0 else 2.2, 0.6 if t % 5 == 0 else 0.35)
    for t in range(-20, 21, 5):
        # the label of a takes the place of a crowding neighbour, but never of q*b
        if abs(t - a) > 2 or t == q * b:
            p.label(t, 0, num(t), 0, 17, TEXT, 11, "middle")
    Y = p.Y(0)
    # q blocks of length b from 0 to q*b, right on top of the line
    lo, hi = sorted((0, q * b))
    for s in range(lo, hi, b):
        rect(p, s, s + b, Y - 17, 14, THEORY, 0.16)
        p.text_px((p.X(s) + p.X(s + b)) / 2, Y - 6, "5", THEORY, 10.5, "middle", True)
    # the remainder block from q*b to a, one level higher
    rect(p, q * b, a, Y - 35, 14, PRACTICE, 0.28, 1.4)
    p.points([(a, 0)], PRACTICE, 4.4)
    p.label(a, 0, num(a), 0, 17, PRACTICE, 11.5, "middle", True)
    p.label(a, 0, it("r") + " = " + num(r), 6, -24, PRACTICE, 12, "start", True)
    p.label((lo + hi) / 2, 0, it("q") + " = " + num(q), 0, -26, THEORY, 12, "middle", True)
    # the equation on the free side of the line
    if a > 0:
        ex, anchor = XR[0] + 0.6, "start"
    else:
        ex, anchor = XR[1] - 0.6, "end"
    p.label(ex, 0, f"divmod({num(a)}, 5) = ({num(q)}, {num(r)})", 0, -38, TEXT, 12, anchor, True)
    p.label(ex, 0, f"{num(a)} = 5 {CDOT} {'(' + num(q) + ')' if q < 0 else num(q)} + {num(r)}",
            0, -20, TEXT, 12, anchor)
    rows.append(p)

save("tam-bolme", figure(
    W1, H1, rows,
    "<code>divmod(17, 5)</code> ve <code>divmod(-17, 5)</code> sayı doğrusunda. Mavi bloklar "
    "|<em>q</em>| tane 5 uzunluğunda adımdır ve 0'dan, <em>a</em>'yı aşmayan en büyük 5 katı olan "
    "<em>q</em> &#183; 5'e ulaşır; turuncu blok <em>r</em> = <em>a</em> &#8722; 5<em>q</em> "
    "kalanıdır. İki durumda da 0 &#8804; <em>r</em> &lt; 5 olur; &#8722;17 için bölüm &#8722;3 değil "
    "&#8722;4'tür.",
    css_class=WIDE,
    aria="Two number lines. Top: three blocks of length 5 from 0 to 15 (q = 3) and a remainder "
         "block from 15 to 17 (r = 2). Bottom: four blocks of length 5 from 0 down to -20 (q = -4) "
         "and a remainder block from -20 to -17 (r = 3)."))


# ============================================================
# oyuncak-float: the 20 positive numbers (1 + m/4) * 2**e, -2 <= e <= 2
# ============================================================
toy = [(1 + m / 4) * 2.0 ** e for e in range(-2, 3) for m in range(4)]
W2, H2 = 640, 270

top = Plot(30, 30, 570, 40, (0, 8), (0, 1))        # data y = 0 is the line
hline_axis(top, 0, 0, 8.05)
top.add(f'<rect x="{top.X(0) - 3:.1f}" y="{top.Y(0) - 11:.1f}" width="{top.X(1) - top.X(0) + 6:.1f}" '
        f'height="22" rx="3" fill="{REMARK}" fill-opacity="0.12" stroke="none"/>')
for t in range(0, 9):
    tick(top, t, 0, 4.5)
    top.label(t, 0, str(t), 0, 18, TEXT, 11, "middle")
top.points([(x, 0) for x in toy], THEORY, 3.0)
for e, lab in ((0, "1/4"), (1, "1/2"), (2, "1")):
    bracket_below(top, 2 ** e, 2 ** (e + 1), top.Y(0) + 30)
    top.text_px((top.X(2 ** e) + top.X(2 ** (e + 1))) / 2, top.Y(0) + 45,
                "aralık " + lab, TEXT, 11, "middle")
top.text_px(top.X(0) - 2, top.Y(0) - 18, "0 ile 8 arası", TEXT, 11.5, "start", True)

zoom = Plot(30, 150, 570, 40, (0, 1), (0, 1))
hline_axis(zoom, 0, 0, 1.006)
for t, lab in ((0, "0"), (0.25, "0,25"), (0.5, "0,5"), (0.75, "0,75"), (1, "1")):
    tick(zoom, t, 0, 4.5)
    zoom.label(t, 0, lab, 0, 18, TEXT, 11, "middle")
zoom.points([(x, 0) for x in toy if x <= 1.0], THEORY, 3.6)
for e, lab in ((-2, "1/16"), (-1, "1/8")):
    bracket_below(zoom, 2.0 ** e, 2.0 ** (e + 1), zoom.Y(0) + 30)
    zoom.text_px((zoom.X(2.0 ** e) + zoom.X(2.0 ** (e + 1))) / 2, zoom.Y(0) + 45,
                 "aralık " + lab, TEXT, 11, "middle")
zoom.add(f'<rect x="{zoom.X(0) + 1:.1f}" y="{zoom.Y(0) - 9:.1f}" width="{zoom.X(0.25) - zoom.X(0) - 6:.1f}" '
         f'height="18" rx="3" fill="{REMARK}" fill-opacity="0.12" stroke="none"/>')
zoom.text_px(zoom.X(0.125), zoom.Y(0) - 14, "sayı yok", REMARK, 11, "middle")
zoom.text_px(zoom.X(0) - 2, zoom.Y(0) - 32, "0 ile 1 arasının 8 kat büyütmesi", TEXT, 11.5, "start", True)

save("oyuncak-float", figure(
    W2, H2, [top, zoom],
    "Mantisi 2 bitlik oyuncak sistemin 20 pozitif sayısı, (1 + <em>m</em>/4) &#183; 2<sup><em>e</em></sup>. "
    "Her [2<sup><em>e</em></sup>, 2<sup><em>e</em>+1</sup>) aralığında dört sayı eşit aralıklı durur; "
    "aralık bir sonraki ikilik aralıkta iki katına çıkar. Altta, üstteki gölgeli [0, 1] parçası 8 kat "
    "büyütülmüştür: 0 ile 0,25 arasında sistemin hiçbir sayısı yoktur.",
    css_class=WIDE,
    aria="Top: the number line from 0 to 8 with the 20 toy floating point numbers, spaced 1/4 on "
         "[1, 2), 1/2 on [2, 4) and 1 on [4, 8). Bottom: an 8 times zoom of [0, 1] with spacing "
         "1/16 on [1/4, 1/2), 1/8 on [1/2, 1) and an empty gap between 0 and 1/4."))


# ============================================================
# ulp-bagil: relative spacing math.ulp(x)/x on a log2 x axis
# ============================================================
eps = math.ulp(1.0)
W3, H3 = 540, 300
p3 = Plot(80, 40, 410, 200, (-3, 4), (0.35, 1.1))
p3.grid(xs=range(-3, 5), ys=(0.5, 1.0))
xlabels = {-3: "1/8", -2: "1/4", -1: "1/2", 0: "1", 1: "2", 2: "4", 3: "8", 4: "16"}
p3.axes(range(-3, 5), (0.5, 1.0), it("x"), "",
        xfmt=lambda t: xlabels[int(t)],
        yfmt=lambda v: EPS if v == 1.0 else EPS + "/2")
p3.text_px(p3.X(-3) - 4, p3.Y(1.1) - 14, "ulp(" + it("x") + ") / " + it("x"), TEXT, 11.5, "middle")
for e in range(-3, 4):
    pts = []
    n_s = 120
    for k in range(n_s):
        t = e + k / n_s
        x = 2.0 ** t
        pts.append((t, math.ulp(x) / x / eps))
    t_end = e + 1 - 1e-9
    x_end = math.nextafter(2.0 ** (e + 1), 0)
    pts.append((t_end, math.ulp(x_end) / x_end / eps))
    p3.line(pts, THEORY, 2.0)
    if e < 3:
        p3.vline(e + 1, pts[-1][1], 1.0, THEORY, "3 3", 0.55)
    p3.points([(e, 1.0)], THEORY, 3.0)
p3.label(0.5, 0.425, "bir ikilik aralıkta ulp(" + it("x") + ") sabit, " + it("x")
         + " büyüdükçe oran azalır", 0, 4, TEXT, 11, "middle")

save("ulp-bagil", figure(
    W3, H3, [p3],
    "Bağıl aralık <code>math.ulp(x)/x</code>, logaritmik <em>x</em> ekseninde. Bir "
    "[2<sup><em>e</em></sup>, 2<sup><em>e</em>+1</sup>) aralığında ardışık <code>float</code>'lar "
    "arasındaki uzaklık sabit olduğundan bağıl aralık &#949;'dan &#949;/2'ye iner ve her 2 kuvvetinde "
    "yeniden &#949;'a sıçrar. Yuvarlamanın bağıl hatası bunun yarısıyla, en fazla &#949;/2 ile sınırlıdır.",
    aria="Sawtooth graph of ulp(x)/x for x from 1/8 to 16 on a logarithmic axis: on every interval "
         "between consecutive powers of two it falls from eps to eps/2 and jumps back to eps at the "
         "next power of two."))


# ============================================================
# e-hata: |(1 + 1/n)**n - e| for n = 10**k, k = 1..16, log-log
# ============================================================
errs = []
for k in range(1, 17):
    n = 10 ** k
    approx = (1 + 1 / n) ** n
    errs.append((k, math.log10(abs(approx - math.e))))
W4, H4 = 540, 330
p4 = Plot(80, 40, 410, 230, (0.5, 16.5), (-9, 1))
p4.grid(xs=range(2, 17, 2), ys=range(-8, 1, 2))
p4.axes(range(2, 17, 2), range(-8, 1, 2), it("n"), "",
        xfmt=lambda t: pow10(int(t)), yfmt=lambda v: pow10(int(v)))
p4.text_px(p4.X(0.5) - 4, p4.Y(1) - 14, "hata", TEXT, 11.5, "middle", italic=True)
# truncation error e/(2n): slope -1, clipped at the bottom of the panel
k_clip = 9 + math.log10(math.e / 2)
p4.line([(1, math.log10(math.e / 2) - 1), (k_clip, -9)], BASE, 1.6, "6 4")
# rounding error bound e * n * 2**-53, clipped at the bottom of the panel
r0 = math.log10(math.e * 2.0 ** -53)
k_lo = -9 - r0
p4.line([(k_lo, -9), (16, r0 + 16)], REMARK, 1.6, "2 3")
p4.line(errs, PRACTICE, 1.6)
p4.points(errs, PRACTICE, 3.6)
p4.label(3.4, math.log10(math.e / 2) - 3.4, it("e") + "/(2" + it("n") + ")", 10, 4, BASE, 12,
         "start", True)
p4.label(14.1, -1.0, it("e") + " " + CDOT + " " + it("n") + " " + CDOT + " 2" + sup(MINUS + "53"),
         0, 0, REMARK, 12, "end", True)
kmin, ymin = min(errs, key=lambda t: t[1])
p4.label(kmin, ymin, "en iyi: " + it("n") + " = " + pow10(kmin), 16, 18, PRACTICE, 11.5, "start", True)
p4.label(16, errs[-1][1], it("n") + " = " + pow10(16) + ": sonuç 1", -8, -10, PRACTICE, 11.5, "end")

save("e-hata", figure(
    W4, H4, [p4],
    "(1 + 1/<em>n</em>)<sup><em>n</em></sup> ile <em>e</em> arasındaki fark, <em>e</em> sayısına "
    "yaklaşan dizi örneğindeki kodun 16 değeri, log-log ölçekte. Kesikli çizgi yöntemin "
    "<em>e</em>/(2<em>n</em>) hatası, noktalı çizgi yuvarlama hatasının "
    "<em>e</em> &#183; <em>n</em> &#183; 2<sup>&#8722;53</sup> kaba tahminidir. "
    "Hata önce <em>n</em> ile azalır, <em>n</em> = 10<sup>8</sup> civarında en küçük değerini alır, "
    "sonra yuvarlama yüzünden büyür.",
    aria="Log-log plot of the error of (1 + 1/n)^n against n = 10^1 ... 10^16: the points follow "
         "the dashed line e/(2n) down to about 3e-8 at n = 10^8 and then rise along the dotted line "
         "e n 2^-53 up to 1.7 at n = 10^16."))


# ============================================================
# birim-kokleri: the six roots of z**6 = 1 from cmath.exp
# ============================================================
n6 = 6
roots = [cmath.exp(2j * cmath.pi * k / n6) for k in range(n6)]
W5, H5 = 420, 420
p5 = cplane(45, 30, 330, (-1.5, 1.5), (-1.5, 1.5))
p5.origin_axes("Re", "Im")
p5.circle(0, 0, 1, BASE, 1.4, "5 4")
p5.polygon([(w.real, w.imag) for w in roots], THEORY, 0.10, THEORY, 1.5)
p5.arc(0, 0, 0.32, 0, math.pi / 3, PRACTICE, 1.4)
p5.label(0.32 * math.cos(math.pi / 6), 0.32 * math.sin(math.pi / 6), "&#960;/3", 6, 2,
         PRACTICE, 12, "start", True)
p5.points([(w.real, w.imag) for w in roots], PRACTICE, 4.6)
offsets = {0: (8, -8, "start"), 1: (6, -10, "start"), 2: (-6, -10, "end"),
           3: (-8, -8, "end"), 4: (-6, 20, "end"), 5: (6, 20, "start")}
for k, w in enumerate(roots):
    dx, dy, anchor = offsets[k]
    s = it(OMEGA) + sub(str(k), 10)
    if k == 0:
        s += " = 1"
    if k == 3:
        s += " = " + MINUS + "1"
    p5.label(w.real, w.imag, s, dx, dy, TEXT, 12, anchor, True)

save("birim-kokleri", figure(
    W5, H5, [p5],
    "<em>z</em><sup>6</sup> = 1 denkleminin <code>cmath.exp(2j * cmath.pi * k / 6)</code> ile "
    "hesaplanan altı kökü. Kökler birim çember üzerinde düzgün bir altıgenin köşeleridir ve ardışık "
    "iki kök arasındaki açı &#960;/3'tür.",
    aria="The unit circle with the six sixth roots of unity omega_0 = 1, omega_1, omega_2, "
         "omega_3 = -1, omega_4, omega_5 forming a regular hexagon; the angle pi/3 between "
         "omega_0 and omega_1 is marked."))


# ============================================================
# pi-kesir: distance to pi of Fraction(math.pi).limit_denominator(N), N = 1..1000
# ============================================================
pf = Fraction(math.pi)
best = []
for N in range(1, 1001):
    f = pf.limit_denominator(N)
    best.append((N, f, math.log10(abs(float(f - pf)))))
W6, H6 = 540, 320
p6 = Plot(80, 40, 410, 220, (0, 3), (-7.2, 0))
p6.grid(xs=range(0, 4), ys=range(-6, 1, 2))
p6.axes(range(0, 4), range(-6, 1, 2), it("N"), "",
        xfmt=lambda t: str(10 ** int(t)), yfmt=lambda v: pow10(int(v)))
p6.text_px(p6.X(0) - 4, p6.Y(0) - 14, "hata", TEXT, 11.5, "middle", italic=True)
steps = []                     # step function: constant on [log N, log(N + 1))
for N, f, y in best:
    x0 = math.log10(N)
    x1 = math.log10(N + 1) if N < 1000 else 3.0
    if not steps or steps[-1][1] != y:
        steps.append((x0, y))
    steps.append((x1, y))
p6.line(steps, THEORY, 1.8)
marks = {10: (8, -8, "start"), 100: (8, -8, "start"), 1000: (-6, -10, "end")}
for N, (dx, dy, anchor) in marks.items():
    _, f, y = best[N - 1]
    x = math.log10(N)
    p6.points([(x, y)], PRACTICE, 4.4)
    p6.label(x, y, f"{f.numerator}/{f.denominator}", dx, dy, PRACTICE, 12, anchor, True)
_, f1, y1 = best[0]
p6.label(0, y1, "3", 6, -8, THEORY, 12, "start", True)

save("pi-kesir", figure(
    W6, H6, [p6],
    "Paydası en fazla <em>N</em> olan kesirler arasında &#960;'ye en yakın olanın hatası, "
    "<code>limit_denominator(N)</code> ile <em>N</em> = 1, 2, &#8230;, 1000 için. Hata basamak "
    "basamak azalır: 22/7, <em>N</em> = 7'den 56'ya kadar en iyi kesirdir ve <em>N</em> = 57'de "
    "yerini 179/57'ye bırakır; 355/113 ise <em>N</em> = 113'ten 1000'e kadar en iyi kesir kalır. Turuncu noktalar örnekteki kodun "
    "yazdırdığı <em>N</em> = 10, 100, 1000 değerleridir.",
    aria="Step graph on log-log axes of the distance to pi of the best fraction with denominator "
         "at most N, for N from 1 to 1000: 3 at N = 1, 22/7 at N = 10, 311/99 at N = 100 and "
         "355/113 at N = 1000 with error about 2.7e-7."))
