# -*- coding: utf-8 -*-
"""
Figures of the chapter "Kısmi Türevler"
(dersler/analiz-4/kismi-turevler.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box and never directly under a heading.
The figures are NOT produced at build time. Run

    python scripts/analysis4_figures/kis.py
    python scripts/center_figures.py "analysis4-kis-*.md"
    python scripts/check_figure_labels.py "scripts/_figures/analysis4-kis-*.md"

and paste the markup of scripts/_figures/analysis4-kis-<name>.md into the .qmd.
Captions are Turkish on purpose; aria labels are plain ASCII.

Value maps are drawn without color scales: a few labelled level curves, or
two translucent tints for the positive and the negative region.
"""
import html
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, dot, panel_title, TEXT, THEORY, PRACTICE, BASE, BG, WIDE  # noqa: E402
from svg_plot3 import Camera, Space, vadd, vscale  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "analysis4-kis-"

MINUS = "&#8722;"
ZWSP = chr(0x200B)          # the zero-width space the sub/sup helpers leave behind


def save(name, markup):
    (OUT_DIR / f"{PREFIX}{name}.md").write_text(markup, encoding="utf-8", newline="\n")
    print(f"{PREFIX}{name}.md")


def it(s):
    """Italic run inside an SVG <text>."""
    return f'<tspan font-style="italic">{s}</tspan>'


def sub(s, size=8.5):
    """Subscript inside an SVG <text>."""
    return f'<tspan font-size="{size}" dy="3.5">{s}</tspan><tspan dy="-3.5">&#8203;</tspan>'


def sup(s, size=8.5):
    """Superscript inside an SVG <text>."""
    return f'<tspan font-size="{size}" dy="-5">{s}</tspan><tspan dy="5">&#8203;</tspan>'


def eq_plot(x0, y0, ppu, xr, yr):
    """Panel with the same number of pixels per unit on both axes."""
    return Plot(x0, y0, (xr[1] - xr[0]) * ppu, (yr[1] - yr[0]) * ppu, xr, yr)


def fit_space(cam, pts, x0, y0, ppu, pad=0.12):
    """Equal-aspect panel just large enough for the projections of pts."""
    q = [cam.project(P)[:2] for P in pts]
    xr = (min(a for a, _ in q) - pad, max(a for a, _ in q) + pad)
    yr = (min(b for _, b in q) - pad, max(b for _, b in q) + pad)
    plot = eq_plot(x0, y0, ppu, xr, yr)
    return plot, Space(plot, cam)


def dec(v):
    """Decimal comma: 0.5 -> '0,5'."""
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return s.replace(".", ",").replace("-", MINUS)


def text_w(s, size):
    """Rough advance width of a label (0.43 em per visible character, tspans at their own size)."""
    def count(t):
        return len(html.unescape(re.sub(r"<[^>]+>", "", t)).replace(ZWSP, ""))
    width = 0.0
    for m in re.finditer(r'<tspan font-size="([\d.]+)"[^>]*>(.*?)</tspan>', s):
        width += count(m.group(2)) * 0.43 * float(m.group(1))
    rest = re.sub(r'<tspan font-size="[\d.]+"[^>]*>.*?</tspan>', "", s)
    return width + count(rest) * 0.43 * size


def plabel(p, x, y, s, dx=0, dy=0, color=TEXT, size=11.5, anchor="start", bold=False):
    """Label on a page-coloured plate, for text that must sit on a meshed surface.

    (A stroke halo with paint-order is painted per tspan and would erase the
    previous glyphs, so a rounded rectangle is laid under the text instead.)
    """
    px, py = p.X(x) + dx, p.Y(y) + dy
    w = text_w(s, size)
    x0 = px - (w / 2 if anchor == "middle" else w if anchor == "end" else 0)
    p.add(f'<rect x="{x0 - 2.5:.1f}" y="{py - 0.8 * size - 1:.1f}" width="{w + 5:.1f}" '
          f'height="{size + 3:.1f}" rx="3" fill="{BG}" opacity="0.85"/>')
    p.label(x, y, s, dx, dy, color, size, anchor, bold)


def splabel(S, P, s, dx=0, dy=0, color=TEXT, size=11.5, anchor="start", bold=False):
    """plabel() at a space point."""
    X, Y = S.pt(P)
    plabel(S.p, X, Y, s, dx, dy, color, size, anchor, bold)


X0, Y0, Z0 = it("x") + sub("0"), it("y") + sub("0"), it("z") + sub("0")

# ============================================================
# mutlak: f(x, y) = |x| + |y| - |x + y|
# ============================================================
L = 2.0
p = eq_plot(80, 30, 92, (-L, L), (-L, L))
# f = 0 on the closed first and third quadrants, f > 0 on the other two
p.polygon([(0, 0), (L, 0), (L, L), (0, L)], TEXT, 0.07)
p.polygon([(0, 0), (-L, 0), (-L, -L), (0, -L)], TEXT, 0.07)
p.polygon([(0, 0), (-L, 0), (-L, L), (0, L)], PRACTICE, 0.10)
p.polygon([(0, 0), (L, 0), (L, -L), (0, -L)], PRACTICE, 0.10)
p.line([(-L, -L), (L, -L), (L, L), (-L, L), (-L, -L)], TEXT, 0.8, None, 0.35)
# level curves f = c: right angles with corners (c/2, -c/2) and (-c/2, c/2)
LEVELS = (0.5, 1.0, 1.5, 2.0, 2.5, 3.0)
for c in LEVELS:
    h = c / 2
    p.line([(h, -L), (h, -h), (L, -h)], PRACTICE, 1.25, "5 3", 0.9)
    p.line([(-h, L), (-h, h), (-L, h)], PRACTICE, 1.25, "5 3", 0.9)
    p.label(L, -h, it("f") + " = " + dec(c), 6, 4, PRACTICE, 11)
    p.label(-L, h, it("f") + " = " + dec(c), -6, 4, PRACTICE, 11, "end")
# the diagonal y = -x, where f = 2|x|
p.line([(-L, L), (L, -L)], TEXT, 1.2, "1.5 3.5", 0.8)
p.label(L, -L, it("y") + " = " + MINUS + it("x") + " üzerinde " + it("f") + " = 2|" + it("x") + "|",
        0, 19, TEXT, 11.5, "end")
# the coordinate axes: the only lines the partial derivatives look at
p.arrow((-L - 0.12, 0), (L + 0.3, 0), THEORY, 2.4, 9.0)
p.arrow((0, -L - 0.12), (0, L + 0.3), THEORY, 2.4, 9.0)
p.label(L + 0.3, 0, it("x"), 0, -9, THEORY, 12.5, "middle")
p.label(0, L + 0.3, it("y"), 10, 5, THEORY, 12.5)
p.label(1.0, 1.0, it("f") + " = 0", 0, 5, TEXT, 13, "middle")
p.label(-1.0, -1.0, it("f") + " = 0", 0, 5, TEXT, 13, "middle")
dot(p, (0, 0), TEXT, 3.8)
p.label(0, 0, "(0, 0)", 7, -8, TEXT, 11.5)
save("mutlak", figure(
    560, 470, [p],
    "<em>f</em>(<em>x</em>, <em>y</em>) = |<em>x</em>| + |<em>y</em>| &#8722; |<em>x</em> + <em>y</em>| "
    "fonksiyonu birinci ve üçüncü bölgede (gri) sıfırdır; ikinci ve dördüncü bölgede <em>f</em> = "
    "2&#183;min{|<em>x</em>|, |<em>y</em>|} &gt; 0 olur ve kesikli çizgiler <em>f</em> = 0,5; 1; …; 3 seviye "
    "eğrileridir. Kısmi türevlerin baktığı kalın eksenler üzerinde <em>f</em> = 0'dır; <em>y</em> = "
    "&#8722;<em>x</em> doğrusu boyunca ise <em>f</em> = 2|<em>x</em>| bir kırık yapar.",
    aria="Plane with the first and third quadrants shaded grey where f = 0, and right-angled level "
         "curves f = 0.5 to 3 in the second and fourth quadrants, the axes drawn thick and the line "
         "y = -x dotted"))

# ============================================================
# kesit: the two vertical sections of the graph through P
# ============================================================
XP, YP = 1.5, 1.5


def fk(x, y):
    return 3 - 0.2 * x * x - 0.1 * y * y


ZP = fk(XP, YP)                                       # 2.325
P3 = (XP, YP, ZP)
FX, FY = -0.4 * XP, -0.2 * YP                         # -0.6, -0.3
ZT = 3.5
cam = Camera(azimuth=35.0, elevation=22.0)
pl, S = fit_space(cam, [(0, 0, 0), (3.7, 0, 0), (0, 3.7, 0), (0, 0, 4.0), (3, 3, 0), (3, 0, ZT),
                        (0, 3, ZT), (3, 3, ZT)], 40, 30, 82, 0.3)
S.axes(3.7, 3.7, 4.0)
# the two vertical planes y = y0 and x = x0
for quad in ([(0, YP, 0), (3, YP, 0), (3, YP, ZT), (0, YP, ZT)],
             [(XP, 0, 0), (XP, 3, 0), (XP, 3, ZT), (XP, 0, ZT)]):
    S.polygon(quad, TEXT, 0.06)
    S.line(quad + [quad[0]], TEXT, 0.8, None, 0.35)
# the surface S
S.surface(lambda u, v: (u, v, fk(u, v)), (0, 3), (0, 3), nu=10, nv=10, fill=THEORY, stroke=THEORY,
          opacity=(0.06, 0.24), stroke_width=0.5, stroke_opacity=0.4)
# section curves and tangent lines
S.curve(lambda t: (t, YP, fk(t, YP)), 0, 3, THEORY, 2.8, 80)
S.curve(lambda t: (XP, t, fk(XP, t)), 0, 3, BASE, 2.8, 80)
T1 = [vadd(P3, vscale(t, (1, 0, FX))) for t in (-1.2, 1.2)]
T2 = [vadd(P3, vscale(t, (0, 1, FY))) for t in (-1.2, 1.2)]
S.line(T1, PRACTICE, 2.2)
S.line(T2, PRACTICE, 2.2)
S.drop(P3)
S.point(P3, PRACTICE, 4.2)
splabel(S, P3, it("P") + "(" + X0 + ", " + Y0 + ", " + Z0 + ")", -14, 15, PRACTICE, 12, "end")
S.label((XP, YP, 0), "(" + X0 + ", " + Y0 + ", 0)", 8, 14, TEXT, 11.5)
S.label((0, YP, ZT), it("y") + " = " + Y0, 0, -8, TEXT, 11.5, "middle")
S.label((XP, 3, ZT), it("x") + " = " + X0, 6, -6, TEXT, 11.5)
S.label((3, YP, fk(3, YP)), it("C") + sub("1"), -12, 6, THEORY, 13, "end", True)
S.label((XP, 3, fk(XP, 3)), it("C") + sub("2"), 9, 10, BASE, 13, "start", True)
S.label(T1[1], it("T") + sub("1"), -6, 14, PRACTICE, 13, "end", True)
S.label(T2[1], it("T") + sub("2"), 8, -4, PRACTICE, 13, "start", True)
S.label((3, 0, fk(3, 0)), it("S"), -10, 4, THEORY, 14, "end", True)
save("kesit", figure(
    int(pl.x0 + pl.w + 60), int(pl.y0 + pl.h + 30), [pl],
    "<em>z</em> = <em>f</em>(<em>x</em>, <em>y</em>) grafiği olan <em>S</em> yüzeyi (burada <em>f</em> = "
    "3 &#8722; 0,2<em>x</em>² &#8722; 0,1<em>y</em>², <em>x</em><sub>0</sub> = <em>y</em><sub>0</sub> = 1,5). "
    "<em>y</em> = <em>y</em><sub>0</sub> düzlemi <em>S</em>'yi <em>C</em><sub>1</sub> eğrisi, "
    "<em>x</em> = <em>x</em><sub>0</sub> düzlemi <em>C</em><sub>2</sub> eğrisi boyunca keser. "
    "<em>T</em><sub>1</sub> ve <em>T</em><sub>2</sub> teğetlerinin eğimleri <em>f<sub>x</sub></em>(<em>x</em><sub>0</sub>, "
    "<em>y</em><sub>0</sub>) ve <em>f<sub>y</sub></em>(<em>x</em><sub>0</sub>, <em>y</em><sub>0</sub>)'dır.",
    aria="Surface patch over a square with the vertical planes y = y0 and x = x0 through the point P, "
         "the two section curves C1 and C2 and their tangent lines T1 and T2 at P"))

# ============================================================
# paraboloit: z = 4 - x^2 - 2y^2, sections y = 1 and x = 1 through P = (1, 1, 1)
# ============================================================


def fp(x, y):
    return 4 - x * x - 2 * y * y


def para(r, phi):
    """Elliptic polar coordinates: the base ellipse x^2 + 2y^2 = 4 is r = 1."""
    x, y = 2 * r * math.cos(phi), math.sqrt(2) * r * math.sin(phi)
    return (x, y, fp(x, y))


PP = (1.0, 1.0, 1.0)
box = [(-2, -1.6, 0), (2, -1.6, 0), (-2, 1.6, 0), (2, 1.6, 0), (0, 0, 4.7), (2.6, 0, 0), (0, 2.2, 0),
       (-2, 1, 4), (2, 1, 4), (1, -1.6, 4), (1, 1.6, 4)]
panels = []
left = 30
# each panel looks at its own section plane from about 30 degrees off its normal
for k, az in ((1, 60.0), (2, 30.0)):
    cam = Camera(azimuth=az, elevation=22.0)
    pl, S = fit_space(cam, box, left, 40, 70, 0.3)
    left += pl.w + 40
    S.axes(2.6, 2.2, 4.7, -2.0, -1.6, 0.0, offsets=((0, 14), (6, 12), (0, -8)))
    S.surface(para, (0, 1), (0, 2 * math.pi), nu=6, nv=16, fill=THEORY, stroke=THEORY,
              opacity=(0.05, 0.22), stroke_width=0.5, stroke_opacity=0.4)
    if k == 1:
        quad = [(-2, 1, 0), (2, 1, 0), (2, 1, 4), (-2, 1, 4)]
    else:
        quad = [(1, -1.6, 0), (1, 1.6, 0), (1, 1.6, 4), (1, -1.6, 4)]
    S.polygon(quad, TEXT, 0.07)
    S.line(quad + [quad[0]], TEXT, 0.8, None, 0.4)
    if k == 1:
        r2 = math.sqrt(2)
        S.curve(lambda t: (t, 1.0, 2 - t * t), -r2, r2, THEORY, 2.8, 80)
        T = [(1 + t, 1.0, 1 - 2 * t) for t in (-1.0, 0.5)]
        S.line(T, PRACTICE, 2.2)
        S.label((-2, 1, 4), it("y") + " = 1", 4, 14, TEXT, 11.5)
        S.label((-r2, 1.0, 0.0), it("C") + sub("1"), -8, -6, THEORY, 13, "end", True)
        splabel(S, T[0], it("T") + sub("1") + ": " + it("z") + " = " + MINUS + "2" + it("x") + " + 3",
                -8, -4, PRACTICE, 12, "end")
        panel_title(pl, it("y") + " = 1 kesiti")
    else:
        r15 = math.sqrt(1.5)
        S.curve(lambda t: (1.0, t, 3 - 2 * t * t), -r15, r15, BASE, 2.8, 80)
        T = [(1.0, 1 + t, 1 - 4 * t) for t in (-0.5, 0.25)]
        S.line(T, PRACTICE, 2.2)
        S.label((1, -1.6, 4), it("x") + " = 1", 6, 16, TEXT, 11.5)
        S.label((1.0, -r15, 0.0), it("C") + sub("2"), -8, -4, BASE, 13, "end", True)
        splabel(S, T[0], it("T") + sub("2") + ": " + it("z") + " = " + MINUS + "4" + it("y") + " + 5",
                8, -6, PRACTICE, 12)
        panel_title(pl, it("x") + " = 1 kesiti")
    S.drop(PP)
    S.point(PP, PRACTICE, 4.0)
    splabel(S, PP, "(1, 1, 1)", 9, 4, PRACTICE, 11.5)
    S.label((1, 1, 0), "(1, 1)", 8, 13, TEXT, 11.5)
    splabel(S, (0, 0, 4), it("z") + " = 4 " + MINUS + " " + it("x") + "² " + MINUS + " 2" + it("y") + "²",
            12, -6, THEORY, 11.5)
    panels.append(pl)
save("paraboloit", figure(
    int(left), int(max(q.y0 + q.h for q in panels) + 30), panels,
    "<em>z</em> = 4 &#8722; <em>x</em>² &#8722; 2<em>y</em>² paraboloidinin <em>z</em> &#8805; 0 kısmı. Solda "
    "<em>y</em> = 1 düzlemi yüzeyi <em>C</em><sub>1</sub>: <em>z</em> = 2 &#8722; <em>x</em>² parabolü boyunca "
    "keser; teğeti <em>T</em><sub>1</sub>'in eğimi <em>f<sub>x</sub></em>(1, 1) = &#8722;2'dir. Sağda "
    "<em>x</em> = 1 düzlemi <em>C</em><sub>2</sub>: <em>z</em> = 3 &#8722; 2<em>y</em>² parabolünü verir; "
    "teğeti <em>T</em><sub>2</sub>'nin eğimi <em>f<sub>y</sub></em>(1, 1) = &#8722;4'tür.",
    css_class=WIDE,
    aria="Two views of the paraboloid z = 4 - x^2 - 2y^2 with the point (1, 1, 1): on the left the plane "
         "y = 1 with the section parabola C1 and its tangent T1, on the right the plane x = 1 with C2 and T2"))

# ============================================================
# sureksiz: f = xy/(x^2 + y^2) is constant on rays, sin(2 theta)/2
# ============================================================
R1 = 1.0
p = eq_plot(40, 30, 150, (-1.3, 1.3), (-1.3, 1.3))


def wedge(a0, a1, n=24):
    return [(0.0, 0.0)] + [(R1 * math.cos(a0 + (a1 - a0) * k / n), R1 * math.sin(a0 + (a1 - a0) * k / n))
                           for k in range(n + 1)]


# f > 0 on the first and third quadrants, f < 0 on the second and fourth
for q in range(4):
    color = PRACTICE if q % 2 == 0 else THEORY
    p.polygon(wedge(q * math.pi / 2, (q + 1) * math.pi / 2), color, 0.14 if q % 2 == 0 else 0.18)
p.circle(0, 0, R1, TEXT, 0.9, None, "none", 0.4)
for k in range(16):
    if k % 2:
        a = k * math.pi / 8
        p.line([(0, 0), (R1 * math.cos(a), R1 * math.sin(a))], TEXT, 0.9, None, 0.5)
D = R1 / math.sqrt(2)
p.line([(-D, -D), (D, D)], PRACTICE, 2.8)
p.line([(-D, D), (D, -D)], THEORY, 2.8)
p.arrow((-1.25, 0), (1.3, 0), TEXT, 2.2, 9.0)
p.arrow((0, -1.25), (0, 1.3), TEXT, 2.2, 9.0)
p.label(1.3, 0, it("x"), -2, 17, TEXT, 12.5, "end")
p.label(0, 1.3, it("y"), 9, 5, TEXT, 12.5)
RL = 1.1
for a, s, col in ((45, "1/2", PRACTICE), (225, "1/2", PRACTICE), (135, MINUS + "1/2", THEORY),
                  (315, MINUS + "1/2", THEORY)):
    ar = math.radians(a)
    p.label(RL * math.cos(ar), RL * math.sin(ar), it("f") + " = " + s, 0, 4, col, 12, "middle", True)
p.label(R1, 0, it("f") + " = 0", 8, -7, TEXT, 11.5)
p.label(0, R1, it("f") + " = 0", 7, -8, TEXT, 11.5)
p.label(-R1, 0, it("f") + " = 0", -8, -7, TEXT, 11.5, "end")
p.label(0, -R1, it("f") + " = 0", 7, 16, TEXT, 11.5)
dot(p, (0, 0), TEXT, 3.6)
p.label(0, -1.3, "orijinde " + it("f") + "(0, 0) = 0", 0, 22, TEXT, 11.5, "middle")
p.label(0, -1.3, "kalın eksenler: kısmi türevlerin gördüğü doğrular", 0, 39, TEXT, 11.5, "middle")
save("sureksiz", figure(
    480, 480, [p],
    "<em>f</em>(<em>x</em>, <em>y</em>) = <em>xy</em>/(<em>x</em>² + <em>y</em>²) orijinden çıkan her ışın "
    "üzerinde sabittir ve değeri sin 2<em>&#952;</em>/2'dir; ince ışınlar 22,5° aralıklıdır. "
    "Turuncu bölgelerde <em>f</em> &gt; 0, mavi bölgelerde <em>f</em> &lt; 0'dır. <em>y</em> = <em>x</em> "
    "üzerinde <em>f</em> = 1/2, <em>y</em> = &#8722;<em>x</em> üzerinde <em>f</em> = &#8722;1/2, eksenlerde ise "
    "<em>f</em> = 0 = <em>f</em>(0, 0) olur.",
    aria="Unit disc divided into rays every 22.5 degrees, the first and third quadrants tinted for f "
         "positive and the others for f negative, the diagonal y = x marked f = 1/2, the diagonal y = -x "
         "marked f = -1/2 and the axes marked f = 0"))
