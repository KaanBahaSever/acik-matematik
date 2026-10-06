# -*- coding: utf-8 -*-
"""
Figures of the chapter "Newton-Raphson Metodu"
(dersler/numerik-analiz/newton-raphson-metodu.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution,
exercise or callout), never inside a definition box and never directly under a
heading. The figures are NOT produced at build time. Run

    python scripts/numerical_figures/nwt.py
    python scripts/center_figures.py "numerical-nwt-*.md"
    python scripts/check_figure_labels.py "scripts/_figures/numerical-nwt-*.md"

and paste the markup of scripts/_figures/numerical-nwt-<name>.md into the .qmd.
Captions are Turkish on purpose; aria labels are plain ASCII.

Every iterate is recomputed here from the iteration formula, so the drawn
tangents meet the x axis exactly at the values printed in the chapter.
"""
import html
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, dot, hollow, TEXT, THEORY, PRACTICE, BASE, REMARK, BG, WIDE  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "numerical-nwt-"

MINUS = "&#8722;"
SUBS = {"0": "&#8320;", "1": "&#8321;", "2": "&#8322;", "3": "&#8323;"}


def save(name, markup):
    (OUT_DIR / f"{PREFIX}{name}.md").write_text(markup, encoding="utf-8", newline="\n")
    print(f"{PREFIX}{name}.md")


def it(s):
    """Italic run inside an SVG <text>."""
    return f'<tspan font-style="italic">{s}</tspan>'


def pn(k):
    """The iterate p_k: italic p with a subscript digit."""
    return it("p") + SUBS[str(k)]


def dec(v, digits=2):
    """Decimal comma and a true minus sign: -0.5 -> '−0,5'."""
    s = f"{v:.{digits}f}".rstrip("0").rstrip(".")
    if s in ("-0", ""):
        s = "0"
    return s.replace(".", ",").replace("-", MINUS)


def text_w(s, size):
    """Rough advance width of a label (0.56 em per visible character)."""
    plain = html.unescape(re.sub(r"<[^>]+>", "", s)).replace("​", "")
    return len(plain) * 0.56 * size


def plate(p, x, y, s, dx=0, dy=0, size=11.5, anchor="start", opacity=0.9):
    """Page-coloured rounded plate under a label that has to sit on lines."""
    px, py = p.X(x) + dx, p.Y(y) + dy
    w = text_w(s, size)
    x0 = px - (w / 2 if anchor == "middle" else w if anchor == "end" else 0)
    p.add(f'<rect x="{x0 - 2.5:.1f}" y="{py - 0.8 * size - 1:.1f}" width="{w + 5:.1f}" '
          f'height="{size + 3:.1f}" rx="3" fill="{BG}" opacity="{opacity}"/>')


def plabel(p, x, y, s, dx=0, dy=0, color=TEXT, size=11.5, anchor="start", bold=False):
    plate(p, x, y, s, dx, dy, size, anchor)
    p.label(x, y, s, dx, dy, color, size, anchor, bold)


def graph_runs(f, x0, x1, ylo, yhi, n=400):
    """Samples of y = f(x) on [x0, x1], cut into the runs that stay in [ylo, yhi]."""
    runs, cur = [], []
    for k in range(n + 1):
        x = x0 + (x1 - x0) * k / n
        y = f(x)
        if ylo <= y <= yhi:
            cur.append((x, y))
        elif cur:
            runs.append(cur)
            cur = []
    if cur:
        runs.append(cur)
    return [r for r in runs if len(r) > 1]


def line_in_box(x0, y0, m, xr, yr):
    """The part of the line through (x0, y0) with slope m inside the box xr x yr."""
    ts = []
    for x in xr:
        y = y0 + m * (x - x0)
        if yr[0] <= y <= yr[1]:
            ts.append((x, y))
    if m != 0:
        for y in yr:
            x = x0 + (y - y0) / m
            if xr[0] <= x <= xr[1]:
                ts.append((x, y))
    ts.sort()
    return [ts[0], ts[-1]]


def axis_mark(p, x, color=PRACTICE, h=4.5, width=1.6):
    """Short vertical tick crossing the x axis at x."""
    X, Y = p.X(x), p.Y(0)
    p.add(f'<line x1="{X:.1f}" y1="{Y - h:.1f}" x2="{X:.1f}" y2="{Y + h:.1f}" stroke="{color}" '
          f'stroke-width="{width}" stroke-linecap="round"/>')


def newton(f, df, p0, n):
    ps = [p0]
    for _ in range(n):
        p = ps[-1]
        ps.append(p - f(p) / df(p))
    return ps


# ============================================================
# teget-fikri: the method picture on a generic increasing S-shaped curve
# ============================================================
# y = 3.5 / (1 + e^(-0.8 (x - 5))) - 0.6: convex left of x = 5, concave right
# of it. From p0 = 1.1 the tangent overshoots to p1 = 5.09 right of the root
# p = 3.03, and the tangent at p1 comes back to p2 = 3.36.
def s_curve(x):
    return 3.5 / (1 + math.exp(-0.8 * (x - 5))) - 0.6


def ds_curve(x):
    e = math.exp(-0.8 * (x - 5))
    return 3.5 * 0.8 * e / (1 + e) ** 2


def bisect_root(f, lo, hi):
    for _ in range(80):
        mid = (lo + hi) / 2
        if f(lo) * f(mid) <= 0:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


FP = "<tspan font-style=\"italic\">f</tspan>&#8242;"
S_ROOT = bisect_root(s_curve, 1.0, 5.0)
sp = newton(s_curve, ds_curve, 1.1, 2)
XS, YS = (-0.45, 7.0), (-0.95, 2.75)
ps_ = Plot(30, 30, 450, 300, XS, YS)
ps_.origin_axes(it("x"), it("y"))
ps_.line([(x, s_curve(x)) for x in [XS[0] + 0.02 * k for k in range(int((6.9 - XS[0]) / 0.02) + 1)]],
         TEXT, 2.0)
ps_.label(6.9, s_curve(6.9), it("y") + " = " + it("f") + "(" + it("x") + ")", -4, -12, TEXT, 12.5, "end")
# the two tangents, each from a little left of where it meets the axis to a little past its point
T_END = ((0.35, sp[1] + 0.9), (sp[2] - 0.3, sp[1] + 1.15))
for k in range(2):
    x0, y0, m = sp[k], s_curve(sp[k]), ds_curve(sp[k])
    lo, hi = T_END[k]
    ps_.line([(lo, y0 + m * (lo - x0)), (hi, y0 + m * (hi - x0))], PRACTICE, 1.8)
# guides from the axis to the curve
for k in range(3):
    ps_.line([(sp[k], 0), (sp[k], s_curve(sp[k]))], TEXT, 1.0, "4 3", 0.7)
for k in range(3):
    dot(ps_, (sp[k], s_curve(sp[k])), PRACTICE, 3.6 if k < 2 else 3.0)
    axis_mark(ps_, sp[k])
hollow(ps_, (S_ROOT, 0), TEXT, 3.6, 1.4)
# points on the curve
plabel(ps_, sp[0], s_curve(sp[0]), "(" + pn(0) + ", " + it("f") + "(" + pn(0) + "))", 4, 20, TEXT, 12)
plabel(ps_, sp[1], s_curve(sp[1]), "(" + pn(1) + ", " + it("f") + "(" + pn(1) + "))", -10, -2, TEXT, 12, "end")
# points on the axis
ps_.label(sp[0], 0, pn(0), 0, -9, PRACTICE, 12.5, "middle", True)
ps_.label(sp[1], 0, pn(1), 4, 17, PRACTICE, 12.5, "start", True)
ps_.label(S_ROOT, 0, it("p"), -5, -8, TEXT, 12.5, "end", True)
# p2 sits between the axis and the first tangent: guide it down below that tangent
P2_DY = 40
ps_.add(f'<line x1="{ps_.X(sp[2]):.1f}" y1="{ps_.Y(0) + 5:.1f}" x2="{ps_.X(sp[2]):.1f}" '
        f'y2="{ps_.Y(0) + P2_DY - 12:.1f}" stroke="{TEXT}" stroke-width="1.0" stroke-dasharray="2 2" opacity="0.6"/>')
ps_.label(sp[2], 0, pn(2), 0, P2_DY + 2, PRACTICE, 12.5, "middle", True)
# the slope labels, in the empty bands next to the far ends of the tangents
ps_.label(sp[1] + 0.1, 0, FP + "(" + pn(0) + ") eğimli teğet", 0, -24, PRACTICE, 11.5)
t1_end = T_END[1][1]
ps_.label(t1_end, s_curve(sp[1]) + ds_curve(sp[1]) * (t1_end - sp[1]),
          FP + "(" + pn(1) + ") eğimli teğet", -12, -4, PRACTICE, 11.5, "end")

save("teget-fikri", figure(
    520, 370, [ps_],
    "Newton-Raphson Metodunun geometrik anlamı. (<em>p</em><sub>0</sub>, <em>f</em>(<em>p</em><sub>0</sub>)) "
    "noktasındaki teğet <em>x</em> eksenini <em>p</em><sub>1</sub>'de, (<em>p</em><sub>1</sub>, "
    "<em>f</em>(<em>p</em><sub>1</sub>)) noktasındaki teğet <em>p</em><sub>2</sub>'de keser; "
    "<em>p</em><sub>2</sub>, <em>p</em> köküne <em>p</em><sub>0</sub>'dan çok daha yakındır.",
    aria="An increasing S shaped curve y = f(x) with root p. The tangent at (p0, f(p0)) with slope f'(p0) "
         "meets the x axis at p1, right of the root; the tangent at (p1, f(p1)) with slope f'(p1) meets the "
         "axis at p2, close to p"))

# ============================================================
# kotu-baslangic: f(x) = x^3 + 3x^2 - 1 from p0 = -2.5 and from p0 = -1.8
# ============================================================
def cubic(x):
    return x ** 3 + 3 * x ** 2 - 1


def dcubic(x):
    return 3 * x * x + 6 * x


ROOTS = (-2.879385, -0.652704, 0.532089)


def cubic_panel(p, xticks, yticks, title, xr, yr):
    p.axes(xticks, yticks, it("x"), it("y"), dec, dec)
    p.grid(xticks, yticks)
    # the x axis itself, where the iterates land
    p.line([(xr[0], 0), (xr[1], 0)], TEXT, 1.1, None, 0.75)
    # the bracket [-3, -2] that holds the wanted root
    band = 5 / (p.h / (yr[1] - yr[0]))
    p.polygon([(-3, -band), (-2, -band), (-2, band), (-3, band)], REMARK, 0.35)
    for run in graph_runs(cubic, xr[0], xr[1], yr[0], yr[1]):
        p.line(run, TEXT, 2.0)
    for r in ROOTS:
        if xr[0] <= r <= xr[1]:
            hollow(p, (r, 0), TEXT, 3.6, 1.4)
    p.text_px(p.x0 + p.w / 2, p.y0 - 22, title, TEXT, 13, "middle", True)


# left panel: zoom on [-3.5, -1.5] so that p0, p1 and p2 can be told apart
XL, YL = (-3.5, -1.5), (-4.0, 4.0)
pl = Plot(55, 50, 250, 260, XL, YL)
cubic_panel(pl, (-3.5, -3, -2.5, -2, -1.5), (-4, -2, 0, 2, 4),
            pn(0) + " = " + MINUS + "2,5", XL, YL)
ps = newton(cubic, dcubic, -2.5, 2)
# first tangent: from p1 on the axis up to (p0, f(p0)) and a little beyond
for k in range(2):
    x0, y0, m = ps[k], cubic(ps[k]), dcubic(ps[k])
    lo = min(ps[k], ps[k + 1]) - 0.12
    hi = max(ps[k], ps[k + 1]) + 0.12
    pl.line([(lo, y0 + m * (lo - x0)), (hi, y0 + m * (hi - x0))], PRACTICE, 1.8)
    pl.line([(x0, 0), (x0, y0)], TEXT, 1.0, "4 3", 0.7)
    dot(pl, (x0, y0), PRACTICE, 3.6)
for k in range(3):
    axis_mark(pl, ps[k])
dot(pl, (-2, 3), TEXT, 3.0)
plabel(pl, -2, 3, "(" + MINUS + "2, 3)", 6, -8, TEXT, 11)
pl.label(ps[0], 0, pn(0), 0, 17, PRACTICE, 12.5, "middle", True)
pl.label(ps[1], 0, pn(1), -6, -7, PRACTICE, 12.5, "end", True)
pl.label(ps[2], 0, pn(2), 6, 17, PRACTICE, 12.5, "start", True)
pl.label(-2.25, 0, "[" + MINUS + "3; " + MINUS + "2]", 0, 32, REMARK, 11.5, "middle")

# right panel: the whole picture on [-3.5, 1.5]
XR, YR = (-3.5, 1.5), (-8.0, 10.0)
pr = Plot(pl.x0 + pl.w + 85, 50, 250, 260, XR, YR)
cubic_panel(pr, (-3, -2, -1, 0, 1), (-8, -4, 0, 4, 8),
            pn(0) + " = " + MINUS + "1,8", XR, YR)
qs = newton(cubic, dcubic, -1.8, 3)
x0, y0, m = qs[0], cubic(qs[0]), dcubic(qs[0])
lo, hi = qs[0] - 0.45, qs[1] + 0.25
pr.line([(lo, y0 + m * (lo - x0)), (hi, y0 + m * (hi - x0))], PRACTICE, 1.8)
pr.line([(x0, 0), (x0, y0)], TEXT, 1.0, "4 3", 0.7)
pr.line([(qs[1], 0), (qs[1], cubic(qs[1]))], TEXT, 1.0, "4 3", 0.7)
dot(pr, (x0, y0), PRACTICE, 3.6)
dot(pr, (qs[1], cubic(qs[1])), PRACTICE, 3.0)
for k in range(4):
    axis_mark(pr, qs[k], PRACTICE, 4.5 if k < 2 else 3.5, 1.6 if k < 2 else 1.2)
for xc, yc, s, dx, dy, anc in ((-2, 3, "(" + MINUS + "2, 3)", 0, -10, "middle"),
                               (0, -1, "(0, " + MINUS + "1)", 0, 19, "middle")):
    dot(pr, (xc, yc), TEXT, 3.0)
    plabel(pr, xc, yc, s, dx, dy, TEXT, 11, anc)
pr.label(qs[0], 0, pn(0), 0, 17, PRACTICE, 12.5, "middle", True)
pr.label(qs[1], 0, pn(1), 6, 17, PRACTICE, 12.5, "start", True)
# the note on where the sequence ends up
NX, NY = 0.95, -5.6
pr.arrow((NX - 0.2, NY + 1.3), (0.56, -0.55), PRACTICE, 1.2, 6.5)
pr.label(NX, NY, pn(2) + ", " + pn(3) + ", ...", 0, 0, PRACTICE, 11.5, "middle")
pr.label(NX, NY, "0,53209 köküne", 0, 15, PRACTICE, 11.5, "middle")
pr.label(NX, NY, "gider", 0, 30, PRACTICE, 11.5, "middle")

save("kotu-baslangic", figure(
    int(pr.x0 + pr.w + 40), int(pl.y0 + pl.h + 50), [pl, pr],
    "<em>f</em>(<em>x</em>) = <em>x</em>³ + 3<em>x</em>² &#8722; 1 için iki başlangıç. Solda (yakınlaştırılmış "
    "pencere) <em>p</em><sub>0</sub> = &#8722;2,5'teki teğet <em>x</em> eksenini [&#8722;3; &#8722;2] bandının "
    "solunda, <em>p</em><sub>1</sub> = &#8722;3,06667'de keser; <em>p</em><sub>1</sub>'deki teğet "
    "<em>p</em><sub>2</sub> = &#8722;2,90088'i verir ve dizi banttaki köke döner. Sağda "
    "<em>p</em><sub>0</sub> = &#8722;1,8 yerel maksimuma yakındır, <em>f</em>&#8242;(<em>p</em><sub>0</sub>) = "
    "&#8722;1,08 küçüktür; neredeyse yatay teğet <em>p</em><sub>1</sub> = 0,87407'ye uzanır ve "
    "<em>p</em><sub>2</sub> = 0,61403, <em>p</em><sub>3</sub> = 0,53873 ile dizi 0,53209 köküne gider. "
    "İçi boş daireler köklerdir.",
    css_class=WIDE,
    aria="Two panels with the graph of x^3 + 3x^2 - 1. Left: from p0 = -2.5 the tangent hits the x axis at "
         "p1 = -3.06667, left of the bracket from -3 to -2, and the next tangent comes back to p2 = -2.90088. "
         "Right: from p0 = -1.8 near the local maximum the nearly flat tangent reaches p1 = 0.87407 and the "
         "sequence goes to the root 0.53209"))

# ============================================================
# cos-tegetler: f(x) = cos x - x, p0 = pi/4, and a zoom on the second step
# ============================================================
def fcos(x):
    return math.cos(x) - x


def dfcos(x):
    return -math.sin(x) - 1


cs = newton(fcos, dfcos, math.pi / 4, 3)
ROOT = 0.739085133215161

XA, YA = (0.4, 1.0), (-0.5, 0.55)
pa = Plot(60, 40, 250, 250, XA, YA)
xt = (0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0)
yt = (-0.4, -0.2, 0, 0.2, 0.4)
pa.axes(xt, yt, it("x"), it("y"), dec, dec)
pa.grid(xt, yt)
pa.line([(XA[0], 0), (XA[1], 0)], TEXT, 1.1, None, 0.75)
for run in graph_runs(fcos, XA[0], XA[1], YA[0], YA[1]):
    pa.line(run, TEXT, 2.0)
t0 = line_in_box(cs[0], fcos(cs[0]), dfcos(cs[0]), XA, YA)
pa.line(t0, PRACTICE, 1.8)
pa.line([(cs[0], 0), (cs[0], fcos(cs[0]))], TEXT, 1.0, "4 3", 0.7)
dot(pa, (cs[0], fcos(cs[0])), PRACTICE, 3.6)
axis_mark(pa, cs[0])
axis_mark(pa, cs[1])
pa.label(cs[0], fcos(cs[0]), pn(0) + " = π/4", -8, 18, PRACTICE, 12.5, "end", True)
pa.label(cs[1], 0, pn(1), 9, -11, PRACTICE, 12.5, "start", True)
# label the tangent where it has pulled away from the graph (upper left)
xl = 0.48
pa.label(xl, fcos(cs[0]) + dfcos(cs[0]) * (xl - cs[0]), "teğet", 8, 0, PRACTICE, 12)
pa.label(0.6, fcos(0.6), it("y") + " = " + it("f") + "(" + it("x") + ")", -6, 20, TEXT, 12.5, "end")
# frame that marks where the right panel zooms in (drawn larger than true size)
FX, FY = pa.X(cs[1]), pa.Y(0)
pa.add(f'<rect x="{FX - 7:.1f}" y="{FY - 7:.1f}" width="14" height="14" fill="none" stroke="{BASE}" '
       f'stroke-width="1.3"/>')

XB, YB = (0.7385, 0.7400), (-0.0012, 0.0008)
pb = Plot(pa.x0 + pa.w + 105, 40, 250, 250, XB, YB)
xbt = (0.7385, 0.739, 0.7395, 0.74)
ybt = (-0.001, -0.0005, 0, 0.0005)
pb.axes(xbt, ybt, it("x"), it("y"), lambda v: dec(v, 4), lambda v: dec(v, 4))
pb.grid(xbt, ybt)
pb.add(f'<rect x="{pb.x0:.1f}" y="{pb.y0:.1f}" width="{pb.w:.1f}" height="{pb.h:.1f}" fill="none" '
       f'stroke="{BASE}" stroke-width="1.3"/>')
pb.line([(XB[0], 0), (XB[1], 0)], TEXT, 1.1, None, 0.75)
# graph and tangent coincide at this scale: the graph is a wide pale band, the tangent a thin line on it
for run in graph_runs(fcos, XB[0], XB[1], YB[0], YB[1]):
    pb.line(run, TEXT, 5.0, None, 0.3)
t1 = line_in_box(cs[1], fcos(cs[1]), dfcos(cs[1]), XB, YB)
pb.line(t1, PRACTICE, 1.6)
pb.line([(cs[1], 0), (cs[1], fcos(cs[1]))], TEXT, 1.0, "4 3", 0.7)
dot(pb, (cs[1], fcos(cs[1])), PRACTICE, 3.6)
axis_mark(pb, cs[1])
hollow(pb, (ROOT, 0), TEXT, 5.0, 1.4)
dot(pb, (cs[2], 0), PRACTICE, 2.4)
pb.label(cs[1], 0, pn(1), 6, -8, PRACTICE, 12.5, "start", True)
pb.label(cs[2], 0, pn(2) + " ≈ " + it("p"), -10, 20, PRACTICE, 12.5, "end", True)
pb.label(cs[1], fcos(cs[1]), "(" + pn(1) + ", " + it("f") + "(" + pn(1) + "))", 8, 14, TEXT, 11)
pb.text_px(pb.x0 + pb.w / 2, pb.y0 - 12, "yakınlaştırma", BASE, 12, "middle", True)

save("cos-tegetler", figure(
    int(pb.x0 + pb.w + 40), int(pa.y0 + pa.h + 50), [pa, pb],
    "<em>f</em>(<em>x</em>) = cos <em>x</em> &#8722; <em>x</em> için Newton-Raphson adımları. Solda "
    "<em>p</em><sub>0</sub> = π/4 noktasındaki teğet <em>x</em> eksenini <em>p</em><sub>1</sub> = 0,739536'da "
    "keser; teğet grafiğe o kadar yakındır ki ancak uçlarda ayrılır. Küçük kare, sağda büyütülen "
    "[0,7385; 0,7400] × [&#8722;0,0012; 0,0008] penceresinin yerini gösterir (gerçek boyutu bu ölçekte bir "
    "pikselden küçüktür). Sağda grafik ile <em>p</em><sub>1</sub>'deki teğet ayırt edilemez; teğet "
    "<em>x</em> eksenini <em>p</em><sub>2</sub> = 0,739085178'de keser ve içi boş daireyle gösterilen "
    "<em>p</em> = 0,739085133 kökü bu ölçekte <em>p</em><sub>2</sub> ile üst üstedir.",
    css_class=WIDE,
    aria="Two panels. Left: graph of cos x - x on 0.4 to 1.0 with the tangent at p0 = pi/4 meeting the x axis "
         "at p1 = 0.739536 and a small frame around p1. Right: zoom on 0.7385 to 0.7400 where graph and the "
         "tangent at p1 coincide and the tangent meets the axis at p2 = 0.739085178, on top of the root"))
