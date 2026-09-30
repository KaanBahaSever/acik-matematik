# -*- coding: utf-8 -*-
"""
Figures of the chapter "Yüksek Mertebeden Kısmi Türevler"
(dersler/analiz-4/yuksek-mertebeden-kismi-turevler.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box and never directly under a heading.
The figures are NOT produced at build time. Run

    python scripts/analysis4_figures/yuk.py
    python scripts/center_figures.py "analysis4-yuk-*.md"
    python scripts/check_figure_labels.py "scripts/_figures/analysis4-yuk-*.md"

and paste the markup of scripts/_figures/analysis4-yuk-<name>.md into the .qmd.
Captions are Turkish on purpose; aria labels are plain ASCII.

Conventions: a boundary that belongs to the set is solid, one that does not is
dashed. Sign maps use two translucent tints (positive / negative), no color
scale; every drawing with a circle has equal x and y scales.
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, dot, disk_fill, TEXT, THEORY, PRACTICE  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "analysis4-yuk-"

MINUS, THETA = "&#8722;", "&#952;"


def save(name, markup):
    (OUT_DIR / f"{PREFIX}{name}.md").write_text(markup, encoding="utf-8", newline="\n")
    print(f"{PREFIX}{name}.md")


def it(s):
    """Italic run inside an SVG <text>."""
    return f'<tspan font-style="italic">{s}</tspan>'


def sub(s, size=8.5):
    """Subscript inside an SVG <text>."""
    return f'<tspan font-size="{size}" dy="3.5">{s}</tspan><tspan dy="-3.5">&#8203;</tspan>'


def eq_plot(x0, y0, ppu, xr, yr):
    """Panel with the same number of pixels per unit on both axes."""
    return Plot(x0, y0, (xr[1] - xr[0]) * ppu, (yr[1] - yr[0]) * ppu, xr, yr)


def dec(v):
    """Decimal comma: 0.5 -> '0,5', negative sign as a true minus."""
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return s.replace(".", ",").replace("-", MINUS)


def fsub(idx):
    """f with an italic subscript, e.g. f_xy."""
    return it("f") + sub(it(idx))


# ============================================================
# kesitler: t -> f_x(0, t) = -t and t -> f_y(t, 0) = t
# ============================================================
p = eq_plot(60, 40, 110, (-1.5, 1.5), (-1.5, 1.5))
p.origin_axes(it("t"), "", (-1, 1), (-1, 1), dec, dec, 0.5)
p.line([(-1.5, 1.5), (1.5, -1.5)], THEORY, 2.3)
p.line([(-1.5, -1.5), (1.5, 1.5)], PRACTICE, 2.3)
# slope triangles between t = 0.5 and t = 1
for s, col in ((1, PRACTICE), (-1, THEORY)):
    a, b, c = (0.5, 0.5 * s), (1.0, 0.5 * s), (1.0, 1.0 * s)
    p.polygon([a, b, c], col, 0.16)
    p.line([a, b, c], col, 1.4)
p.label(1.0, 0.75, "eğim 1", 8, -3, PRACTICE, 12)
p.label(1.0, 0.75, "= " + fsub("yx") + "(0, 0)", 8, 13, PRACTICE, 12)
p.label(1.0, -0.75, "eğim " + MINUS + "1", 8, -3, THEORY, 12)
p.label(1.0, -0.75, "= " + fsub("xy") + "(0, 0)", 8, 13, THEORY, 12)
p.label(1.5, 1.5, fsub("y") + "(" + it("t") + ", 0) = " + it("t"), 0, -9, PRACTICE, 12.5, "middle")
p.label(-1.5, 1.5, fsub("x") + "(0, " + it("t") + ") = " + MINUS + it("t"), 0, -9, THEORY, 12.5, "middle")
save("kesitler", figure(
    560, 430, [p],
    "Eksenler üzerindeki birinci türevler: <em>f<sub>x</sub></em>(0, <em>t</em>) = &#8722;<em>t</em> ve "
    "<em>f<sub>y</sub></em>(<em>t</em>, 0) = <em>t</em>. Karışık türevler bu iki doğrunun orijindeki "
    "eğimleridir: <em>f<sub>xy</sub></em>(0, 0) = &#8722;1, <em>f<sub>yx</sub></em>(0, 0) = 1.",
    aria="Two lines through the origin, t to -t and t to t, each with a small slope triangle between "
         "t = 0.5 and t = 1 marked slope -1 = fxy(0, 0) and slope 1 = fyx(0, 0)"))

# ============================================================
# sekiz-bolge: f = (r^2/4) sin 4 theta, level curves and eight sign sectors
# ============================================================
LIM = 1.5
p = eq_plot(40, 30, 120, (-LIM, LIM), (-LIM, LIM))
RIM = [(LIM, 0), (LIM, LIM), (0, LIM), (-LIM, LIM), (-LIM, 0), (-LIM, -LIM), (0, -LIM), (LIM, -LIM)]
for k in range(8):
    # sin 4 theta > 0 on the sectors k * 45 deg < theta < (k + 1) * 45 deg with k even
    p.polygon([(0, 0), RIM[k], RIM[(k + 1) % 8]], PRACTICE if k % 2 == 0 else THEORY,
              0.13 if k % 2 == 0 else 0.15)
p.line(RIM + [RIM[0]], TEXT, 0.8, None, 0.35)


def inside(q):
    return abs(q[0]) <= LIM and abs(q[1]) <= LIM


def level_pts(c, a0, a1, n=120):
    """The level curve (r^2/4) sin 4 theta = c on the sector a0 < theta < a1, cut to the square."""
    def at(th):
        r = math.sqrt(4 * c / math.sin(4 * th))
        return (r * math.cos(th), r * math.sin(th))

    def edge(t_in, t_out):
        for _ in range(50):
            tm = (t_in + t_out) / 2
            if inside(at(tm)):
                t_in = tm
            else:
                t_out = tm
        return at(t_in)

    eps = 1e-6
    ths = [a0 + eps + (a1 - a0 - 2 * eps) * (0.5 - 0.5 * math.cos(math.pi * k / n)) for k in range(n + 1)]
    runs, cur = [], []
    for t_prev, t in zip([None] + ths[:-1], ths):
        q = at(t)
        if inside(q):
            if not cur and t_prev is not None:
                cur.append(edge(t, t_prev))
            cur.append(q)
        elif cur:
            cur.append(edge(t_prev, t))
            runs.append(cur)
            cur = []
    if cur:
        runs.append(cur)
    return runs


LEVELS = (0.02, 0.08, 0.18, 0.3)
for k in range(8):
    a0, a1 = k * math.pi / 4, (k + 1) * math.pi / 4
    for c in LEVELS:
        if k % 2 == 0:
            for run in level_pts(c, a0, a1):
                p.line(run, PRACTICE, 1.4)
        else:
            for run in level_pts(-c, a0, a1):
                p.line([q for q in run], THEORY, 1.4, "5 3")
# the zero set: the axes and the lines y = x, y = -x
p.line([(-LIM, -LIM), (LIM, LIM)], TEXT, 1.0, None, 0.5)
p.line([(-LIM, LIM), (LIM, -LIM)], TEXT, 1.0, None, 0.5)
p.arrow((-LIM, 0), (LIM + 0.18, 0), TEXT, 1.0, 7.0, None, 0.6)
p.arrow((0, -LIM), (0, LIM + 0.18), TEXT, 1.0, 7.0, None, 0.6)
p.label(LIM + 0.18, 0, it("x"), 4, 16, TEXT, 12.5, "middle")
p.label(0, LIM + 0.18, it("y"), 10, 5, TEXT, 12.5)
for k in range(8):
    a = (k + 0.5) * math.pi / 4
    p.label(1.3 * math.cos(a), 1.3 * math.sin(a), "+" if k % 2 == 0 else MINUS, 0, 6,
            PRACTICE if k % 2 == 0 else THEORY, 17, "middle", True)
# value labels along the rays theta = 15 deg (positive) and theta = -15 deg (negative)
for c in LEVELS:
    r = math.sqrt(4 * c / math.sin(math.pi / 3))
    for sgn, col, a in ((1, PRACTICE, math.pi / 12), (-1, THEORY, -math.pi / 12)):
        q = (r * math.cos(a), r * math.sin(a))
        p.label(q[0], q[1], dec(sgn * c), 4, -4 if sgn > 0 else 12, col, 10)
save("sekiz-bolge", figure(
    480, 460, [p],
    "<em>f</em> = <em>xy</em>(<em>x</em>² &#8722; <em>y</em>²)/(<em>x</em>² + <em>y</em>²) = "
    "(<em>r</em>²/4) sin 4<em>&#952;</em> fonksiyonunun seviye eğrileri: düz çizgiler <em>f</em> = 0,02; 0,08; "
    "0,18; 0,3, kesikli çizgiler aynı değerlerin negatifleri. <em>f</em>, eksenler ve <em>y</em> = &#177;<em>x</em> "
    "doğruları üzerinde sıfırdır; orijin çevresindeki sekiz bölgede işaret sırayla değişir.",
    aria="Square around the origin cut by the axes and the lines y = x and y = -x into eight sectors, "
         "alternately marked plus and minus, with the level curves f = +-0.02, 0.08, 0.18, 0.3 in them"))

# ============================================================
# ikinci-fark: the rectangle of the second difference inside B((x0, y0), r)
# ============================================================
XC, YC, R = 2.5, 2.5, 2.4
H, K = 1.1, 0.9
TH = (2.94, 2.95)
X0, Y0 = it("x") + sub("0"), it("y") + sub("0")
p = eq_plot(50, 40, 72, (-0.3, 5.4), (-0.3, 5.4))
p.arrow((0, 0), (5.2, 0), TEXT, 1.1, 7.0, None, 0.6)
p.arrow((0, 0), (0, 5.2), TEXT, 1.1, 7.0, None, 0.6)
p.label(5.2, 0, it("x"), 0, 16, TEXT, 12.5, "middle")
p.label(0, 5.2, it("y"), 10, 5, TEXT, 12.5)
disk_fill(p, XC, YC, R, THEORY, 0.06)
p.circle(XC, YC, R, THEORY, 1.6, "6 4")
ang = math.radians(58)
p.label(XC + R * math.cos(ang), YC + R * math.sin(ang),
        it("B") + "((" + X0 + ", " + Y0 + "), " + it("r") + ")", 6, -6, THEORY, 12.5)
rect = [(XC, YC), (XC + H, YC), (XC + H, YC + K), (XC, YC + K)]
p.polygon(rect, PRACTICE, 0.2)
p.line(rect + [rect[0]], PRACTICE, 1.6)
p.points(rect, TEXT, 3.0)
# the signs of the four corner values in F(h, k)
for (cx, cy), s, dx, dy in (((XC, YC), "+", 8, -6), ((XC + H, YC), MINUS, -8, -6),
                            ((XC, YC + K), MINUS, 8, 16), ((XC + H, YC + K), "+", -8, 16)):
    p.label(cx, cy, s, dx, dy, TEXT, 15, "start" if dx > 0 else "end", True)
p.label(XC, YC, "(" + X0 + ", " + Y0 + ")", -8, 17, TEXT, 11.5, "end")
p.label(XC + H, YC, "(" + X0 + " + " + it("h") + ", " + Y0 + ")", 8, 17, TEXT, 11.5)
p.label(XC, YC + K, "(" + X0 + ", " + Y0 + " + " + it("k") + ")", -8, -7, TEXT, 11.5, "end")
p.label(XC + H, YC + K, "(" + X0 + " + " + it("h") + ", " + Y0 + " + " + it("k") + ")", 0, -9, TEXT, 11.5,
        "middle")
# dimension arrows h and k
GAP = 0.3
HY, KX = YC - GAP, XC - GAP
for a, b in (((XC + H / 2, HY), (XC, HY)), ((XC + H / 2, HY), (XC + H, HY)),
             ((KX, YC + K / 2), (KX, YC)), ((KX, YC + K / 2), (KX, YC + K))):
    p.arrow(a, b, TEXT, 1.1, 7.0, None, 0.75)
p.line([(XC, YC - 0.06), (XC, HY - 0.08)], TEXT, 0.8, None, 0.5)
p.line([(XC + H, YC - 0.06), (XC + H, HY - 0.08)], TEXT, 0.8, None, 0.5)
p.line([(XC - 0.06, YC), (KX - 0.08, YC)], TEXT, 0.8, None, 0.5)
p.line([(XC - 0.06, YC + K), (KX - 0.08, YC + K)], TEXT, 0.8, None, 0.5)
p.label(XC + H / 2, HY, it("h"), 0, 16, TEXT, 13, "middle")
p.label(KX, YC + K / 2, it("k"), -8, 5, TEXT, 13, "end")
# the intermediate point of the lemma, labelled to the right with a leader
dot(p, TH, PRACTICE, 3.8)
TOP = (2.55, 3.98)
p.line([(TH[0] - 0.04, TH[1] + 0.06), TOP], TEXT, 0.9, "3 3", 0.6)
p.label(TOP[0], TOP[1], "(" + X0 + " + " + it(THETA) + sub("1") + it("h") + ", " + Y0 + " + "
        + it(THETA) + sub("2") + it("k") + ")", 0, -5, PRACTICE, 12, "middle")
save("ikinci-fark", figure(
    560, 480, [p],
    "İkinci fark <em>F</em>(<em>h</em>, <em>k</em>), dikdörtgenin köşelerindeki değerleri gösterilen "
    "işaretlerle toplar. |<em>h</em>|, |<em>k</em>| &lt; <em>r</em>/2 olduğundan kapalı dikdörtgen "
    "<em>B</em>((<em>x</em><sub>0</sub>, <em>y</em><sub>0</sub>), <em>r</em>) yuvarının içindedir; "
    "lemmanın verdiği ara nokta (<em>x</em><sub>0</sub> + <em>&#952;</em><sub>1</sub><em>h</em>, "
    "<em>y</em><sub>0</sub> + <em>&#952;</em><sub>2</sub><em>k</em>) dikdörtgenin içinde kalır.",
    aria="Dashed circle around (x0, y0) containing the rectangle with corners (x0, y0) and (x0 + h, y0 + k), "
         "corner signs plus, minus, minus, plus, and an interior point (x0 + theta1 h, y0 + theta2 k)"))
