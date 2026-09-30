# -*- coding: utf-8 -*-
"""
Figures of the chapter "Türevlenebilme ve Toplam Diferansiyel"
(dersler/analiz-4/turevlenebilme-ve-toplam-diferansiyel.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box and never directly under a heading.
The figures are NOT produced at build time. Run

    python scripts/analysis4_figures/dif.py
    python scripts/center_figures.py "analysis4-dif-*.md"
    python scripts/check_figure_labels.py "scripts/_figures/analysis4-dif-*.md"

and paste the markup of scripts/_figures/analysis4-dif-<name>.md into the .qmd.
Captions are Turkish on purpose; aria labels are plain ASCII.

Conventions: a boundary that belongs to the set is solid, one that does not is
dashed; a point of the set is filled, a point outside it is hollow. Every
drawing with a circle has equal x and y scales.
"""
import html
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, dot, hollow, disk_fill, TEXT, THEORY, PRACTICE, BASE, BG  # noqa: E402
from svg_plot3 import Camera, Space, vadd, vscale  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "analysis4-dif-"

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
    """Decimal comma: 0.5 -> '0,5', negative sign as a true minus."""
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


# ============================================================
# kok-xy: z = sqrt(|xy|) and its only candidate tangent plane z = 0
# ============================================================
cam = Camera(azimuth=-25.0, elevation=24.0)        # the diagonal y = x runs across the page
pl, S = fit_space(cam, [(1.6, 0, 0), (-1.3, 0, 0), (0, 1.6, 0), (0, -1.3, 0), (0, 0, 1.45),
                        (1, 1, 1), (-1, -1, 1), (1, -1, 1), (-1, 1, 1), (1, 1, 0), (-1, -1, 0),
                        (1, -1, 0), (-1, 1, 0)], 40, 30, 150, 0.25)
S.axes(1.6, 1.6, 1.45, -1.3, -1.3, 0.0)
sq = [(-1, -1, 0), (1, -1, 0), (1, 1, 0), (-1, 1, 0)]
S.polygon(sq, TEXT, 0.10)
S.line(sq + [sq[0]], TEXT, 0.9, None, 0.45)
S.surface(lambda u, v: (u, v, math.sqrt(abs(u * v))), (-1, 1), (-1, 1), nu=16, nv=16, fill=THEORY,
          stroke=THEORY, opacity=(0.05, 0.22), stroke_width=0.45, stroke_opacity=0.4)
S.curve(lambda t: (t, t, abs(t)), -1, 1, PRACTICE, 2.7, 80)
S.curve(lambda t: (t, -t, abs(t)), -1, 1, PRACTICE, 2.7, 80)
S.point((0, 0, 0), TEXT, 3.8)
splabel(S, (1, 1, 1), it("y") + " = " + it("x") + " kesiti: " + it("z") + " = |" + it("x") + "|",
        30, -12, PRACTICE, 12, "end")
splabel(S, (-1, 0.4, math.sqrt(0.4)), it("z") + " = √|" + it("x") + it("y") + "|", -12, -4, THEORY, 12.5, "end")
S.label((1, -1, 0), it("z") + " = 0", -8, 14, TEXT, 12, "end")
S.label((0, 0, 0), "(0, 0, 0)", -8, 16, TEXT, 11.5, "end")
save("kok-xy", figure(
    int(pl.x0 + pl.w + 40), int(pl.y0 + pl.h + 30), [pl],
    "<em>z</em> = &#8730;|<em>xy</em>| yüzeyi eksenler üzerinde <em>z</em> = 0 düzlemine (gri) yapışıktır; "
    "kısmi türevlerin önerdiği tek aday teğet düzlem budur. Köşegenler boyunca ise <em>z</em> = |<em>x</em>| "
    "olur ve grafik orijinde V biçiminde kırılır, düzlemden uzaklıkla aynı mertebede ayrılır.",
    aria="Surface z = sqrt(|xy|) over the square [-1, 1]^2 touching the grey plane z = 0 along the axes, "
         "with the V-shaped sections z = |x| over the diagonals y = x and y = -x"))

# ============================================================
# merdiven: the staircase path a -> p1 -> a + h of the sufficiency proof
# ============================================================
A = (0.6, 0.6)
P1 = (1.5, 0.6)
P2 = (1.5, 1.3)
C1, C2 = (1.1, 0.6), (1.5, 0.95)
RB = 1.4
p = eq_plot(40, 30, 130, (-0.9, 2.1), (-0.9, 2.1))
disk_fill(p, A[0], A[1], RB, THEORY, 0.07)
p.circle(A[0], A[1], RB, THEORY, 1.6, "6 4")
ang = math.radians(128)
p.label(A[0] + RB * math.cos(ang), A[1] + RB * math.sin(ang), it("B") + "(" + it("a") + ", " + it("r") + ")",
        -6, -6, THEORY, 12.5, "end")
ang = math.radians(215)
RE = (A[0] + RB * math.cos(ang), A[1] + RB * math.sin(ang))
p.line([A, RE], THEORY, 1.2, None, 0.8)
p.label((A[0] + RE[0]) / 2, (A[1] + RE[1]) / 2, it("r"), -2, -8, THEORY, 12.5, "middle")
p.line([A, P2], TEXT, 1.0, "4 3", 0.6)
PR = 4.0 / 130                                     # a point radius in data units


def seg_arrow(a, b):
    """Arrow from point a to point b, trimmed so that it stops at the point markers."""
    L = math.hypot(b[0] - a[0], b[1] - a[1])
    u = ((b[0] - a[0]) / L, (b[1] - a[1]) / L)
    p.arrow((a[0] + u[0] * PR, a[1] + u[1] * PR), (b[0] - u[0] * 1.6 * PR, b[1] - u[1] * 1.6 * PR),
            PRACTICE, 2.0, 9.0)


seg_arrow(A, P1)
seg_arrow(P1, P2)
p.points([A, P1, P2], TEXT, 4.0)
hollow(p, C1, PRACTICE, 3.8, 1.7)
hollow(p, C2, PRACTICE, 3.8, 1.7)
p.label(A[0], A[1], it("a"), -8, 16, TEXT, 13, "end")
p.label(P1[0], P1[1], it("p") + sub("1"), 9, 16, TEXT, 13)
p.label(P2[0], P2[1], it("a") + " + " + it("h"), -8, -9, TEXT, 13, "end")
p.label(C1[0], C1[1], it("c") + sub("1"), 0, 19, PRACTICE, 13, "middle")
p.label(C2[0], C2[1], it("c") + sub("2"), -9, 5, PRACTICE, 13, "end")
p.label((A[0] + P1[0]) / 2 - 0.1, A[1], it("h") + sub("1"), 0, -9, PRACTICE, 13, "middle")
p.label(P1[0], (P1[1] + P2[1]) / 2 + 0.12, it("h") + sub("2"), 9, 5, PRACTICE, 13)
save("merdiven", figure(
    450, 440, [p],
    "<em>a</em>'dan <em>a</em> + <em>h</em>'ye eksenlere paralel adımlarla gidilir: önce <em>h</em><sub>1</sub>"
    "<em>e</em><sub>1</sub> ile <em>p</em><sub>1</sub>'e, sonra <em>h</em><sub>2</sub><em>e</em><sub>2</sub> ile "
    "<em>p</em><sub>2</sub> = <em>a</em> + <em>h</em>'ye. Her adımda ortalama değer teoremi, o adımın doğru "
    "parçası üzerinde bir <em>c<sub>k</sub></em> noktası verir; bütün parçalar <em>B</em>(<em>a</em>, <em>r</em>) "
    "yuvarının içindedir.",
    aria="Open ball around a with the staircase path from a horizontally to p1 and vertically to a + h, "
         "the mean value points c1 and c2 on the two steps and the dashed segment from a to a + h"))

# ============================================================
# sin-ters-kare: the section y = 0 of (x^2 + y^2) sin(1/(x^2 + y^2))
# ============================================================
p = eq_plot(70, 30, 400, (-0.6, 0.6), (-0.4, 0.4))
p.arrow((-0.64, 0), (0.66, 0), TEXT, 1.0, 7.0, None, 0.5)
p.arrow((0, -0.42), (0, 0.44), TEXT, 1.0, 7.0, None, 0.5)
for t in (-0.5, 0.5):
    p.line([(t, -0.008), (t, 0.008)], TEXT, 1.0, None, 0.6)
    p.label(t, 0, dec(t), 0, 17, TEXT, 11, "middle")
for t in (-0.3, 0.3):
    p.line([(-0.008, t), (0.008, t)], TEXT, 1.0, None, 0.6)
    p.label(0, t, dec(t), -7, 4, TEXT, 11, "end")
p.label(0.66, 0, it("x"), 0, -8, TEXT, 12.5, "middle")
p.label(0, 0.44, it("z"), 9, 6, TEXT, 12.5)
# the envelopes z = x^2 and z = -x^2
env = [(-0.6 + 1.2 * k / 120, (-0.6 + 1.2 * k / 120) ** 2) for k in range(121)]
p.line(env, TEXT, 1.1, "5 4", 0.55)
p.line([(x, -z) for x, z in env], TEXT, 1.1, "5 4", 0.55)
# the tangent line z = 0 of the section
p.line([(-0.6, 0), (0.6, 0)], PRACTICE, 2.8)


def branch(sign):
    """Points of g(x) = x^2 sin(1/x^2) from x = 0.6 in toward 0, sampled evenly in the phase 1/x^2."""
    pts, u = [], 1 / 0.36
    while u < 400:
        x = 1 / math.sqrt(u)
        pts.append((sign * x, x * x * math.sin(u)))
        u += math.pi / 32 if x > 0.3 else math.pi / 12 if x > 0.15 else math.pi / 5
    return pts + [(0.0, 0.0)]


for sgn in (1, -1):
    p.line(branch(sgn), THEORY, 1.1)
dot(p, (0, 0), TEXT, 3.6)
XPK = 1 / math.sqrt(2.5 * math.pi)                 # a peak of g: sin(1/x^2) = 1
p.line([(0.27, 0.225), (XPK + 0.005, XPK * XPK + 0.01)], THEORY, 0.9, None, 0.8)
p.label(0.27, 0.225, it("z") + " = " + it("x") + "² sin(1/" + it("x") + "²)", 0, -5, THEORY, 12, "end")
p.label(0.6, 0.36, it("z") + " = " + it("x") + "²", 6, 4, TEXT, 12)
p.label(0.6, -0.36, it("z") + " = " + MINUS + it("x") + "²", 6, 4, TEXT, 12)
p.label(-0.6, 0, "teğet:", -8, -3, PRACTICE, 12, "end")
p.label(-0.6, 0, it("z") + " = 0", -8, 12, PRACTICE, 12, "end")
save("sin-ters-kare", figure(
    700, 380, [p],
    "<em>y</em> = 0 kesiti: <em>z</em> = <em>x</em>² sin(1/<em>x</em>²) eğrisi <em>z</em> = &#177;<em>x</em>² "
    "parabollerinin arasında kalır ve orijine yaklaştıkça giderek sıklaşan salınımlar yapar. Paraboller "
    "orijinde <em>z</em> = 0 doğrusuna teğettir ve eğriyi de bu teğete yapıştırır.",
    aria="Graph of x^2 sin(1/x^2) oscillating ever faster between the dashed parabolas z = x^2 and z = -x^2, "
         "squeezed onto the thick tangent line z = 0 at the origin"))

# ============================================================
# teget-paraboloit: z = 2x^2 + y^2, its tangent plane and normal at P = (1, 1, 3)
# ============================================================
ZS = 0.35                                           # vertical scale factor (the drawing is compressed)
ZRIM = 8.0                                          # the surface is drawn up to the rim z = 8


def V(x, y, z):
    return (x, y, ZS * z)


def fq(x, y):
    return 2 * x * x + y * y


def bowl(r, t):
    """Elliptic polar coordinates: z = r^2 on the ellipse 2x^2 + y^2 = r^2."""
    return V(r * math.cos(t) / math.sqrt(2), r * math.sin(t), r * r)


PQ = (1.0, 1.0, 3.0)
cam = Camera(azimuth=65.0, elevation=20.0)         # P and the normal on the visible outer side
RR = math.sqrt(ZRIM)
corners = [bowl(RR, 2 * math.pi * k / 48) for k in range(48)] +           [V(x, y, 4 * x + 2 * y - 3) for x in (0.2, 1.8) for y in (0.2, 1.8)] +           [V(2.6, 0, 0), V(0, 3.3, 0), V(0, 0, 10.5), V(*vadd(PQ, vscale(0.3, (4, 2, -1))))]
pl, S = fit_space(cam, corners, 40, 30, 95, 0.3)
S.axes(2.6, 3.3, ZS * 10.5)
S.surface(bowl, (0, RR), (0, 2 * math.pi), nu=8, nv=28, fill=THEORY, stroke=THEORY,
          opacity=(0.05, 0.22), stroke_width=0.45, stroke_opacity=0.4)
tp = [V(x, y, 4 * x + 2 * y - 3) for x, y in ((0.2, 0.2), (1.8, 0.2), (1.8, 1.8), (0.2, 1.8))]
S.polygon(tp, PRACTICE, 0.16)
S.line(tp + [tp[0]], PRACTICE, 1.0, None, 0.7)
X1 = math.sqrt((ZRIM - 1) / 2)                      # C1 reaches the rim at x = +-sqrt(3.5)
Y2 = math.sqrt(ZRIM - 2)                            # C2 reaches the rim at y = +-sqrt(6)
S.curve(lambda t: V(t, 1.0, fq(t, 1.0)), -X1, X1, THEORY, 2.6, 80)
S.curve(lambda t: V(1.0, t, fq(1.0, t)), -Y2, Y2, BASE, 2.6, 80)
T1 = [V(1 + t, 1, 3 + 4 * t) for t in (-0.6, 0.6)]
T2 = [V(1, 1 + t, 3 + 2 * t) for t in (-0.6, 0.6)]
S.line(T1, PRACTICE, 2.4)
S.line(T2, PRACTICE, 2.4)
NV = vscale(0.3, (4, 2, -1))
S.arrow(V(*PQ), V(*vadd(PQ, NV)), TEXT, 1.8, 9.0)
S.point(V(*PQ), PRACTICE, 4.2)
splabel(S, V(*PQ), it("P"), 8, 16, PRACTICE, 13, "start", True)
splabel(S, V(X1, 1, ZRIM), it("C") + sub("1"), -8, 4, THEORY, 13, "end", True)
splabel(S, V(1, Y2, ZRIM), it("C") + sub("2"), 8, 4, BASE, 13, "start", True)
splabel(S, T1[1], it("T") + sub("1"), -8, 4, PRACTICE, 13, "end", True)
splabel(S, T2[1], it("T") + sub("2"), 8, 4, PRACTICE, 13, "start", True)
splabel(S, tp[3], it("z") + " = 4" + it("x") + " + 2" + it("y") + " " + MINUS + " 3", 8, 4, PRACTICE, 12)
splabel(S, V(*vadd(PQ, NV)), "(4, 2, " + MINUS + "1)", -8, 12, TEXT, 11.5, "end")
for zt in (5, 10):
    S.line([V(-0.06, 0, zt), V(0.06, 0, zt)], TEXT, 1.0, None, 0.6)
    S.label(V(0, 0, zt), str(zt), -8, 4, TEXT, 10.5, "end")
save("teget-paraboloit", figure(
    int(pl.x0 + pl.w + 60), int(pl.y0 + pl.h + 30), [pl],
    "<em>z</em> = 2<em>x</em>² + <em>y</em>² paraboloidi ve <em>P</em> = (1, 1, 3) noktasındaki teğet düzlemi "
    "<em>z</em> = 4<em>x</em> + 2<em>y</em> &#8722; 3. Düzlem, <em>C</em><sub>1</sub> (<em>y</em> = 1) ve "
    "<em>C</em><sub>2</sub> (<em>x</em> = 1) kesit eğrilerinin <em>T</em><sub>1</sub>, <em>T</em><sub>2</sub> "
    "teğetlerini içerir; ok, (4, 2, &#8722;1) normal vektörünün 0,3 katıdır. Düşey eksen kısaltılmıştır.",
    aria="Elliptic paraboloid with the tangent plane at P = (1, 1, 3), the section curves C1 and C2 through P, "
         "their tangent lines T1 and T2 and the normal vector (4, 2, -1) scaled by 0.3; vertical axis compressed"))
