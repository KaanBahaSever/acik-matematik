# -*- coding: utf-8 -*-
"""
Figures of the chapter "Kutupsal Koordinatlarda İki Katlı İntegraller"
(dersler/integral-calculus/kutupsal-koordinatlarda-iki-katli-integraller.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box and never directly under a heading.
Concept figures stay visible: `bolgeler` and `bolunus` sit in the prose,
`kutupsal-dikdortgen` directly below the definition box of the polar
rectangle, `genel-bolge` in the statement of the theorem (before the proof);
`paraboloit`, `gul` and `silindir` sit under the question text of their
examples, and `koni-kure` under the question text of its exercise.
The figures are NOT produced at build time. Run

    python scripts/calculus_figures/kki.py
    python scripts/center_figures.py "calculus-kki-*.md"
    python scripts/check_figure_labels.py "scripts/_figures/calculus-kki-*.md"

and paste the markup of scripts/_figures/calculus-kki-<name>.md into the .qmd.
Captions are Turkish on purpose; aria labels are plain ASCII.
"""
import html
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, dot, panel_title, TEXT, THEORY, PRACTICE, BASE, BG, WIDE  # noqa: E402
from svg_plot3 import Camera, Space  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "calculus-kki-"

MINUS = "&#8722;"
ZWSP = chr(0x200B)
PI = math.pi
DEG = PI / 180


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


def subsup(base, lo, hi, size=8.5):
    """base with a subscript and a superscript stacked at the same x (r_i^*)."""
    return (f'{base}<tspan font-size="{size}" dy="-5">{hi}</tspan>'
            f'<tspan font-size="{size}" dx="-4" dy="8.5">{lo}</tspan><tspan dy="-3.5">&#8203;</tspan>')


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


def text_w(s, size):
    """Rough advance width of a label (0.43 em per visible character)."""
    def count(t):
        return len(html.unescape(re.sub(r"<[^>]+>", "", t)).replace(ZWSP, ""))
    width = 0.0
    for m in re.finditer(r'<tspan font-size="([\d.]+)"[^>]*>(.*?)</tspan>', s):
        width += count(m.group(2)) * 0.43 * float(m.group(1))
    rest = re.sub(r'<tspan font-size="[\d.]+"[^>]*>.*?</tspan>', "", s)
    return width + count(rest) * 0.43 * size


def plabel(p, x, y, s, dx=0, dy=0, color=TEXT, size=11.5, anchor="start", bold=False):
    """Label on a page-coloured plate, for text that must sit on a filled region."""
    px, py = p.X(x) + dx, p.Y(y) + dy
    w = text_w(s, size)
    x0 = px - (w / 2 if anchor == "middle" else w if anchor == "end" else 0)
    p.add(f'<rect x="{x0 - 2.5:.1f}" y="{py - 0.8 * size - 1:.1f}" width="{w + 5:.1f}" '
          f'height="{size + 3:.1f}" rx="3" fill="{BG}" opacity="0.85"/>')
    p.label(x, y, s, dx, dy, color, size, anchor, bold)


def splabel(S, P, s, dx=0, dy=0, color=TEXT, size=11.5, anchor="start", bold=False):
    X, Y = S.pt(P)
    plabel(S.p, X, Y, s, dx, dy, color, size, anchor, bold)


def pol(r, t):
    return (r * math.cos(t), r * math.sin(t))


def arc_pts(r, t0, t1, n=64):
    return [pol(r, t0 + (t1 - t0) * k / n) for k in range(n + 1)]


def sector_ring(p, r0, r1, t0, t1, color=THEORY, opacity=0.16, stroke=None, width=1.6):
    """Annular sector a <= r <= b, alpha <= theta <= beta (polar rectangle)."""
    pts = arc_pts(r1, t0, t1) + arc_pts(r0, t1, t0)
    p.polygon(pts, color, opacity)
    if stroke:
        p.line(pts + [pts[0]], stroke, width)


def angle_mark(p, t0, t1, r, color=TEXT, width=1.1, opacity=0.8):
    p.line(arc_pts(r, t0, t1, 24), color, width, None, opacity)


TH = it("θ")
R_ = it("r")
X_, Y_ = it("x"), it("y")

# ============================================================
# bolgeler: the unit disk and the upper half ring 1 <= r <= 2
# ============================================================
pa = eq_plot(40, 40, 62, (-1.6, 1.75), (-1.6, 1.75))
pb = eq_plot(pa.x0 + pa.w + 50, 40, 62, (-2.5, 2.75), (-0.55, 2.8))
pb.y0 = pa.y0 + pa.h - pb.h
for p in (pa, pb):
    p.origin_axes(X_, Y_)
# (a) unit disk
pa.polygon(arc_pts(1, 0, 2 * PI, 96), THEORY, 0.16)
pa.line(arc_pts(1, 0, 2 * PI, 96), THEORY, 1.9)
pa.label(0, 0, "0", -6, 14, TEXT, 11, "end")
pa.label(1, 0, "1", 5, 14, TEXT, 11)
pa.label(-0.45, 0.4, it("R"), 0, 0, THEORY, 14, "middle", True)
pa.label(pol(1, 52 * DEG)[0], pol(1, 52 * DEG)[1], X_ + sup("2") + " + " + Y_ + sup("2") + " = 1",
         6, -6, THEORY, 12)
panel_title(pa, "(a)  0 ≤ " + R_ + " ≤ 1,  0 ≤ " + TH + " ≤ 2" + it("π"))
# (b) half ring
sector_ring(pb, 1, 2, 0, PI, THEORY, 0.16)
pb.line(arc_pts(2, 0, PI), THEORY, 1.9)
pb.line(arc_pts(1, 0, PI), THEORY, 1.9)
pb.line([(-2, 0), (-1, 0)], THEORY, 1.9)
pb.line([(1, 0), (2, 0)], THEORY, 1.9)
# one ray: it enters the region at r = 1 and leaves it at r = 2
t0 = 150 * DEG
pb.line([(0, 0), pol(1, t0)], TEXT, 1.0, "4 3", 0.6)
pb.arrow(pol(1, t0), pol(2, t0), PRACTICE, 2.0, 8.0)
pb.label(0, 0, "0", -6, 14, TEXT, 11, "end")
for v in (1, 2):
    pb.label(v, 0, str(v), 0, 15, TEXT, 11, "middle")
    pb.label(-v, 0, MINUS + str(v), 0, 15, TEXT, 11, "middle")
pb.label(0.95, 1.05, it("R"), 0, 0, THEORY, 14, "middle", True)
pb.label(pol(2, 40 * DEG)[0], pol(2, 40 * DEG)[1], X_ + sup("2") + " + " + Y_ + sup("2") + " = 4",
         6, -4, THEORY, 12)
plabel(pb, 0, 0.42, X_ + sup("2") + " + " + Y_ + sup("2") + " = 1", 0, 4, THEORY, 11.5, "middle")
panel_title(pb, "(b)  1 ≤ " + R_ + " ≤ 2,  0 ≤ " + TH + " ≤ " + it("π"))
save("bolgeler", figure(
    int(pb.x0 + pb.w + 30), int(pa.y0 + pa.h + 30), [pa, pb],
    "Kutupsal koordinatlarla kolay yazılan iki bölge. (a) Birim disk: 0 ≤ <em>r</em> ≤ 1, "
    "0 ≤ <em>θ</em> ≤ 2<em>π</em>. (b) Üst yarı düzlemde <em>x</em>² + <em>y</em>² = 1 ile "
    "<em>x</em>² + <em>y</em>² = 4 çemberleri arasındaki yarım halka: 1 ≤ <em>r</em> ≤ 2, "
    "0 ≤ <em>θ</em> ≤ <em>π</em>. Okla gösterilen ışın bölgeye <em>r</em> = 1'de girer, "
    "<em>r</em> = 2'de çıkar.",
    css_class=WIDE,
    aria="Two panels: the unit disk x^2 + y^2 = 1 shaded, and the upper half ring between the "
         "circles of radius 1 and 2 with a ray crossing it from r = 1 to r = 2"))

# ============================================================
# kutupsal-dikdortgen: a <= r <= b, alpha <= theta <= beta
# ============================================================
A_, B_ = 1.3, 3.2
AL, BE = 18 * DEG, 62 * DEG
p = eq_plot(40, 30, 100, (-0.35, 3.6), (-0.35, 3.25))
p.origin_axes(X_, Y_)
sector_ring(p, A_, B_, AL, BE, THEORY, 0.16, THEORY, 2.0)
for t in (AL, BE):
    p.line([(0, 0), pol(A_, t)], TEXT, 1.0, "4 3", 0.6)
angle_mark(p, 0, AL, 0.55)
angle_mark(p, 0, BE, 0.85)
p.label(*pol(0.62, AL / 2), it("α"), 4, 5, TEXT, 12)
p.label(*pol(0.92, BE * 0.62), it("β"), 3, 2, TEXT, 12)
p.label(0, 0, it("O"), -6, 14, TEXT, 11.5, "end")
p.label(*pol(2.45, (AL + BE) / 2), it("R"), 0, 5, THEORY, 15, "middle", True)
p.label(*pol(B_, 46 * DEG), R_ + " = " + it("b"), 7, -2, THEORY, 12.5)
plabel(p, *pol(1.62, 40 * DEG), R_ + " = " + it("a"), 0, 4, THEORY, 12.5, "middle")
p.label(*pol(2.45, AL), TH + " = " + it("α"), 6, 16, THEORY, 12.5)
p.label(*pol(2.2, BE), TH + " = " + it("β"), -9, -2, THEORY, 12.5, "end")
save("kutupsal-dikdortgen", figure(
    int(p.x0 + p.w + 30), int(p.y0 + p.h + 30), [p],
    "Kutupsal dikdörtgen <em>R</em> = {(<em>r</em>, <em>θ</em>) | <em>a</em> ≤ <em>r</em> ≤ <em>b</em>, "
    "<em>α</em> ≤ <em>θ</em> ≤ <em>β</em>}: iki çember yayı ile iki ışın parçasının sınırladığı halka dilimi.",
    aria="A polar rectangle: the part of the ring between the radii a and b between the rays theta = alpha and "
         "theta = beta, with the angles alpha and beta marked at the origin"))

# ============================================================
# bolunus: the polar grid and one cell R_ij with its area
# ============================================================
M, N = 6, 7
pl = eq_plot(40, 40, 82, (-0.35, 3.6), (-0.35, 3.3))
pl.origin_axes(X_, Y_)
sector_ring(pl, A_, B_, AL, BE, THEORY, 0.10)
dr, dt = (B_ - A_) / M, (BE - AL) / N
for i in range(M + 1):
    pl.line(arc_pts(A_ + i * dr, AL, BE, 40), THEORY, 1.0 if 0 < i < M else 1.8)
for j in range(N + 1):
    t = AL + j * dt
    pl.line([pol(A_, t), pol(B_, t)], THEORY, 1.0 if 0 < j < N else 1.8)
    pl.line([(0, 0), pol(A_, t)], TEXT, 0.7, "3 3", 0.35)
I0, J0 = 3, 4                       # the highlighted cell R_ij
ri0, ri1 = A_ + (I0 - 1) * dr, A_ + I0 * dr
tj0, tj1 = AL + (J0 - 1) * dt, AL + J0 * dt
sector_ring(pl, ri0, ri1, tj0, tj1, PRACTICE, 0.35, PRACTICE, 2.0)
rs, ts = (ri0 + ri1) / 2, (tj0 + tj1) / 2
dot(pl, pol(rs, ts), PRACTICE, 3.4)
cx, cy = pol(ri1, tj1)
pl.line([pol(rs, ts), (cx - 0.05, cy + 0.75)], PRACTICE, 0.9, None, 0.8)
plabel(pl, cx - 0.05, cy + 0.75, it("R") + sub("ij"), 0, -5, PRACTICE, 13, "middle", True)
pl.label(0, 0, it("O"), -6, 14, TEXT, 11.5, "end")
panel_title(pl, "bölünüş")
# right panel: one enlarged cell
q0, q1 = 2.3, 3.5
u0, u1 = 22 * DEG, 46 * DEG
pr = eq_plot(pl.x0 + pl.w + 60, 40, 100, (-0.25, 3.65), (-0.25, 2.9))
pr.y0 = pl.y0 + pl.h - pr.h
for t in (u0, u1):
    pr.line([(0, 0), pol(q0, t)], TEXT, 1.0, "4 3", 0.55)
sector_ring(pr, q0, q1, u0, u1, PRACTICE, 0.22, PRACTICE, 2.0)
qs, us = (q0 + q1) / 2, (u0 + u1) / 2
pr.line(arc_pts(qs, u0, u1, 30), PRACTICE, 1.3, "5 3", 0.95)
dot(pr, pol(qs, us), PRACTICE, 3.6)
pr.label(0, 0, it("O"), -6, 14, TEXT, 11.5, "end")
# the center point, labelled outside the cell
cpx, cpy = pol(qs, us)
pr.line([(cpx, cpy), (cpx + 0.95, cpy - 0.55)], PRACTICE, 0.9, None, 0.8)
pr.label(cpx + 0.95, cpy - 0.55, "(" + subsup(R_, "i", "*") + ", " + subsup(TH, "j", "*") + ")", 0, 15,
         PRACTICE, 12, "middle")
# radial side: length delta r
pr.label(*pol(qs, u0), "Δ" + R_, 6, 18, TEXT, 12.5, "middle")
# middle arc: length r* delta theta, labelled on the inner side of the dashed arc
plabel(pr, *pol(qs - 0.08, us + 5 * DEG), subsup(R_, "i", "*") + " Δ" + TH, -6, 0, PRACTICE, 12.5, "end")
angle_mark(pr, u0, u1, 0.9, TEXT, 1.1)
pr.label(*pol(0.98, us), "Δ" + TH, 4, 4, TEXT, 12)
pr.label(*pol(q0, u1 + 2 * DEG), R_ + " = " + R_ + sub("i" + MINUS + "1"), -6, -4, TEXT, 11.5, "end")
pr.label(*pol(q1, u1), R_ + " = " + R_ + sub("i"), 0, -10, TEXT, 11.5, "middle")
panel_title(pr, "bir hücre")
save("bolunus", figure(
    int(pr.x0 + pr.w + 40), int(pl.y0 + pl.h + 30), [pl, pr],
    "Sol: <em>r</em> = <em>r<sub>i</sub></em> çemberleri ve <em>θ</em> = <em>θ<sub>j</sub></em> ışınları "
    "<em>R</em>'yi küçük kutupsal dikdörtgenlere böler. Sağ: bir <em>R<sub>ij</sub></em> hücresi. "
    "Işın yönündeki kenarı Δ<em>r</em>, merkezinden geçen yayın uzunluğu <em>r<sub>i</sub></em>* Δ<em>θ</em>'dır "
    "ve alanı tam olarak Δ<em>A<sub>ij</sub></em> = <em>r<sub>i</sub></em>* Δ<em>r</em> Δ<em>θ</em>'dır.",
    css_class=WIDE,
    aria="Left: a polar rectangle cut by circles and rays into small cells, one cell R_ij highlighted. "
         "Right: that cell enlarged, with the radial side delta r, the middle arc r* delta theta and "
         "its center point"))

# ============================================================
# genel-bolge: alpha <= theta <= beta, h1(theta) <= r <= h2(theta)
# ============================================================
GA, GB = 28 * DEG, 76 * DEG


def h1(t):
    return 1.35 + 0.22 * math.sin(3.2 * (t - GA))


def h2(t):
    return 3.0 + 0.35 * math.sin(5.0 * (t - GA) + 0.6)


ts_ = [GA + (GB - GA) * k / 80 for k in range(81)]
outer = [pol(h2(t), t) for t in ts_]
inner = [pol(h1(t), t) for t in reversed(ts_)]
p = eq_plot(40, 30, 100, (-0.35, 3.3), (-0.35, 3.5))
p.origin_axes(X_, Y_)
p.polygon(outer + inner, THEORY, 0.16)
p.line(outer, THEORY, 2.0)
p.line(list(reversed(inner)), THEORY, 2.0)
p.line([pol(h1(GA), GA), pol(h2(GA), GA)], THEORY, 2.0)
p.line([pol(h1(GB), GB), pol(h2(GB), GB)], THEORY, 2.0)
for t in (GA, GB):
    p.line([(0, 0), pol(h1(t), t)], TEXT, 1.0, "4 3", 0.6)
angle_mark(p, 0, GA, 0.5)
angle_mark(p, 0, GB, 0.8)
p.label(*pol(0.57, GA / 2), it("α"), 4, 5, TEXT, 12)
p.label(*pol(0.87, GB * 0.6), it("β"), 3, 2, TEXT, 12)
# a ray: enters D at h1, leaves at h2
TR = 38 * DEG
p.line([(0, 0), pol(h1(TR), TR)], TEXT, 1.0, "4 3", 0.6)
p.arrow(pol(h1(TR), TR), pol(h2(TR), TR), PRACTICE, 2.1, 8.5)
dot(p, pol(h1(TR), TR), PRACTICE, 3.2)
p.label(0, 0, it("O"), -6, 14, TEXT, 11.5, "end")
p.label(*pol(2.5, 63 * DEG), it("D"), 0, 5, THEORY, 15, "middle", True)
p.label(*pol(h2(36 * DEG), 36 * DEG), R_ + " = " + it("h") + sub("2") + "(" + TH + ")", 8, 4, THEORY, 12.5)
plabel(p, *pol(h1(58 * DEG) + 0.3, 58 * DEG), R_ + " = " + it("h") + sub("1") + "(" + TH + ")", 0, 4, THEORY, 12.5)
p.label(*pol(h2(GA), GA), TH + " = " + it("α"), 6, 10, THEORY, 12.5)
p.label(*pol(h2(GB), GB), TH + " = " + it("β"), -8, -4, THEORY, 12.5, "end")
save("genel-bolge", figure(
    int(p.x0 + p.w + 30), int(p.y0 + p.h + 30), [p],
    "<em>D</em> = {(<em>r</em>, <em>θ</em>) | <em>α</em> ≤ <em>θ</em> ≤ <em>β</em>, "
    "<em>h</em><sub>1</sub>(<em>θ</em>) ≤ <em>r</em> ≤ <em>h</em><sub>2</sub>(<em>θ</em>)}. Orijinden çıkan "
    "her ışın <em>D</em>'ye <em>r</em> = <em>h</em><sub>1</sub>(<em>θ</em>) eğrisinde girer, "
    "<em>r</em> = <em>h</em><sub>2</sub>(<em>θ</em>) eğrisinde çıkar; iç integralin sınırları bunlardır.",
    aria="A region between the rays theta = alpha and theta = beta whose inner boundary is r = h1(theta) "
         "and outer boundary r = h2(theta); a ray from the origin crosses it from the inner to the outer curve"))

# ============================================================
# paraboloit: the solid under z = 1 - x^2 - y^2 over the unit disk
# ============================================================
cam = Camera(azimuth=35.0, elevation=22.0)
pl3, S = fit_space(cam, [(1.55, 0, 0), (0, 1.5, 0), (0, 0, 1.45), (-1, -1, 0), (1, 1, 0), (1, -1, 0),
                         (-1, 1, 0)], 40, 30, 150, 0.15)
S.axes(1.55, 1.5, 1.45, -1.0, -1.0, 0.0, offsets=((-4, 14), (8, 5), (-9, -2)))
# base disk D
S.polygon([(math.cos(2 * PI * k / 96), math.sin(2 * PI * k / 96), 0) for k in range(97)], BASE, 0.18)
S.circle((0, 0, 0), (1, 0, 0), (0, 1, 0), 1.0, BASE, 1.6)
# the paraboloid cap, in polar parameters
S.surface(lambda r, t: (r * math.cos(t), r * math.sin(t), 1 - r * r), (0, 1), (0, 2 * PI), nu=6, nv=24,
          fill=THEORY, stroke=THEORY, opacity=(0.05, 0.22), stroke_width=0.5, stroke_opacity=0.45)
S.point((0, 0, 1), PRACTICE, 3.6)
splabel(S, (0, 0, 1), "(0, 0, 1)", 8, -6, PRACTICE, 12)
S.label((0.5, -0.45, 0), it("D"), 0, 6, BASE, 14, "middle", True)
S.label((0, 0.95, 1.0), it("z") + " = 1 " + MINUS + " " + X_ + sup("2") + " " + MINUS + " " + Y_ + sup("2"),
        -16, -2, THEORY, 12)
save("paraboloit", figure(
    int(pl3.x0 + pl3.w + 30), int(pl3.y0 + pl3.h + 30), [pl3],
    "<em>z</em> = 1 &#8722; <em>x</em>² &#8722; <em>y</em>² paraboloidi ile <em>xy</em>-düzlemi arasındaki cisim. "
    "Paraboloit düzlemi <em>x</em>² + <em>y</em>² = 1 çemberi boyunca keser; taban <em>D</em> birim disktir.",
    aria="A paraboloid cap z = 1 - x^2 - y^2 with vertex (0, 0, 1) above the unit disk D in the xy plane"))

# ============================================================
# gul: one loop of the four-leaved rose r = cos 2 theta
# ============================================================
p = eq_plot(40, 30, 175, (-1.15, 1.25), (-1.15, 1.15))
p.origin_axes(X_, Y_)


def rose(t):
    rr = math.cos(2 * t)
    return (rr * math.cos(t), rr * math.sin(t))


loop = [rose(-PI / 4 + (PI / 2) * k / 120) for k in range(121)]
p.polygon(loop, THEORY, 0.20)
p.line([rose(2 * PI * k / 480) for k in range(481)], THEORY, 1.8)
for t in (PI / 4, -PI / 4):
    p.line([pol(-1.05, t), pol(1.1, t)], TEXT, 1.0, "4 3", 0.55)
TR = 14 * DEG
p.arrow((0, 0), rose(TR), PRACTICE, 2.0, 8.0)
p.label(*pol(1.1, PI / 4), TH + " = " + it("π") + "/4", 4, -4, TEXT, 12)
p.label(*pol(1.1, -PI / 4), TH + " = " + MINUS + it("π") + "/4", 4, 12, TEXT, 12)
p.label(0.68, 0.0, it("D"), 0, -8, THEORY, 14, "middle", True)
p.label(*rose(TR), R_ + " = cos 2" + TH, 6, -6, PRACTICE, 12)
p.label(1, 0, "1", 6, 14, TEXT, 11)
save("gul", figure(
    int(p.x0 + p.w + 30), int(p.y0 + p.h + 30), [p],
    "<em>r</em> = cos 2<em>θ</em> dört yapraklı gülü. Sağdaki yaprak <em>θ</em> = &#8722;<em>π</em>/4 ile "
    "<em>θ</em> = <em>π</em>/4 ışınları arasındadır; bu açılardaki her ışın orijinden çıkıp eğriye "
    "<em>r</em> = cos 2<em>θ</em>'da ulaşır.",
    aria="The four-leaved rose r = cos 2 theta with its right loop shaded between the dashed rays "
         "theta = -pi/4 and theta = pi/4 and a ray from the origin to the curve"))

# ============================================================
# silindir: inside x^2 + y^2 = 2x, under z = x^2 + y^2
# ============================================================
# left: the base disk D in the plane
pd = eq_plot(40, 50, 92, (-0.45, 2.45), (-1.35, 1.45))
pd.origin_axes(X_, Y_)
pd.polygon(arc_pts(1, 0, 2 * PI, 96), THEORY, 0.0)
disk_pts = [(1 + math.cos(2 * PI * k / 96), math.sin(2 * PI * k / 96)) for k in range(97)]
pd.polygon(disk_pts, THEORY, 0.16)
pd.line(disk_pts, THEORY, 1.9)
TR = 32 * DEG
pd.arrow((0, 0), pol(2 * math.cos(TR), TR), PRACTICE, 2.0, 8.0)
pd.label(0, 0, "0", -6, 14, TEXT, 11, "end")
pd.label(1, 0, "1", 0, 15, TEXT, 11, "middle")
pd.label(2, 0, "2", 6, 15, TEXT, 11)
pd.label(1.05, -0.5, it("D"), 0, 0, THEORY, 14, "middle", True)
pd.label(*pol(2 * math.cos(TR), TR), R_ + " = 2 cos " + TH, 6, -6, PRACTICE, 12)
pd.label(1.0, 1.0, "(" + X_ + " " + MINUS + " 1)" + sup("2") + " + " + Y_ + sup("2") + " = 1", 0, -10, THEORY, 12, "middle")
panel_title(pd, "taban " + it("D"))
# right: the solid, with the paraboloid as a faint bowl behind it
cam = Camera(azimuth=35.0, elevation=24.0)
p3, S = fit_space(cam, [(0, 0, 0), (2.6, 0, 0), (0, 1.9, 0), (0, -1.3, 0), (0, 0, 4.7), (2, 0, 4),
                        (-2, 0, 4), (0, 2, 4), (0, -2, 4), (2, 0, 0)], pd.x0 + pd.w + 50, 40, 58, 0.25)
p3.y0 = pd.y0 + pd.h - p3.h
S.axes(2.6, 1.9, 4.7, 0.0, -1.3, 0.0)
# the paraboloid z = x^2 + y^2 (r <= 2)
S.wire(lambda r, t: (r * math.cos(t), r * math.sin(t), r * r), (0, 2.0), (0, 2 * PI), nu=4, nv=12,
       color=TEXT, width=0.6, opacity=0.22, samples=24)
# base disk
ring = [(1 + math.cos(2 * PI * k / 96), math.sin(2 * PI * k / 96), 0) for k in range(97)]
S.polygon(ring, BASE, 0.16)
S.line(ring, BASE, 1.4)
# cylinder x^2 + y^2 = 2x from z = 0 up to the paraboloid, where z = 2x
S.surface(lambda s_, t: (1 + math.cos(t), math.sin(t), s_ * 2 * (1 + math.cos(t))), (0, 1), (0, 2 * PI),
          nu=1, nv=40, fill=BASE, stroke=BASE, opacity=(0.08, 0.20), stroke_width=0.4, stroke_opacity=0.3)
# the top of the solid: z = x^2 + y^2 over D
S.surface(lambda q, t: (1 + q * math.cos(t), q * math.sin(t), (1 + q * math.cos(t)) ** 2 + (q * math.sin(t)) ** 2),
          (0, 1), (0, 2 * PI), nu=5, nv=24, fill=THEORY, stroke=THEORY, opacity=(0.06, 0.22),
          stroke_width=0.5, stroke_opacity=0.4)
S.curve(lambda t: (1 + math.cos(t), math.sin(t), 2 * (1 + math.cos(t))), 0, 2 * PI, THEORY, 2.0, 160)
S.label((2, 0, 4), it("z") + " = " + X_ + sup("2") + " + " + Y_ + sup("2"), -10, -4, THEORY, 12, "end")
S.label((1.0, 1.0, 0), it("D"), 12, 12, BASE, 13, "middle", True)
panel_title(p3, "cisim")
save("silindir", figure(
    int(p3.x0 + p3.w + 60), int(pd.y0 + pd.h + 30), [pd, p3],
    "Sol: taban <em>D</em>, (<em>x</em> &#8722; 1)² + <em>y</em>² = 1 diskidir; kutupsal denklemi "
    "<em>r</em> = 2 cos <em>θ</em>, &#8722;<em>π</em>/2 ≤ <em>θ</em> ≤ <em>π</em>/2. Sağ: <em>x</em>² + "
    "<em>y</em>² = 2<em>x</em> silindirinin içinde, <em>xy</em>-düzleminin üstünde ve <em>z</em> = <em>x</em>² + "
    "<em>y</em>² paraboloidinin altında kalan cisim.",
    css_class=WIDE,
    aria="Left: the disk (x - 1)^2 + y^2 = 1 with a ray from the origin to the circle r = 2 cos theta. "
         "Right: the solid inside the cylinder x^2 + y^2 = 2x under the paraboloid z = x^2 + y^2"))

# ============================================================
# koni-kure: above the cone z = sqrt(x^2 + y^2), below the sphere of radius 1
# ============================================================
cam = Camera(azimuth=35.0, elevation=18.0)
R0 = 1 / math.sqrt(2)
pk, S = fit_space(cam, [(1.2, 0, 0), (0, 1.25, 0), (0, 0, 1.3), (-0.8, -0.8, 0), (0.8, 0.8, 0),
                        (0.8, -0.8, 1), (-0.8, 0.8, 1)], 40, 30, 190, 0.12)
S.axes(1.2, 1.25, 1.3, -0.8, -0.8, 0.0, offsets=((-4, 14), (8, 5), (-9, -2)))
# the cone, r from 0 to 1/sqrt 2
S.surface(lambda r, t: (r * math.cos(t), r * math.sin(t), r), (0, R0), (0, 2 * PI), nu=4, nv=28,
          fill=BASE, stroke=BASE, opacity=(0.06, 0.20), stroke_width=0.45, stroke_opacity=0.4)
# the spherical cap, r from 0 to 1/sqrt 2
S.surface(lambda r, t: (r * math.cos(t), r * math.sin(t), math.sqrt(1 - r * r)), (0, R0), (0, 2 * PI),
          nu=4, nv=28, fill=THEORY, stroke=THEORY, opacity=(0.05, 0.20), stroke_width=0.45, stroke_opacity=0.4)
S.circle((0, 0, R0), (1, 0, 0), (0, 1, 0), R0, THEORY, 2.0)
# shadow disk r <= 1/sqrt 2 on the floor
S.polygon([(R0 * math.cos(2 * PI * k / 96), R0 * math.sin(2 * PI * k / 96), 0) for k in range(97)], TEXT, 0.08)
S.circle((0, 0, 0), (1, 0, 0), (0, 1, 0), R0, TEXT, 1.0, "4 3", 96, 0.6)
S.guide([(R0, 0, R0), (R0, 0, 0)])
S.label((0.57 * R0, -0.82 * R0, 1.25), it("x") + sup("2") + " + " + Y_ + sup("2") + " + " + it("z") + sup("2") + " = 1",
        0, 0, THEORY, 12)
splabel(S, (0, R0 * 0.75, R0 * 0.55), it("z") + " = √(" + X_ + sup("2") + " + " + Y_ + sup("2") + ")",
        40, 18, BASE, 12)
splabel(S, (R0, 0, R0 * 0.45), R_ + " = 1/√2", -8, 4, TEXT, 11.5, "end")
save("koni-kure", figure(
    int(pk.x0 + pk.w + 40), int(pk.y0 + pk.h + 30), [pk],
    "<em>z</em> = √(<em>x</em>² + <em>y</em>²) konisinin üstünde ve birim kürenin altında kalan "
    "dondurma külahı biçimli cisim. Koni ile küre <em>z</em> = 1/√2 yüksekliğinde, <em>r</em> = 1/√2 "
    "yarıçaplı çember boyunca kesişir; cismin <em>xy</em>-düzlemindeki izdüşümü bu yarıçaplı disktir.",
    aria="An ice cream cone shaped solid: the cone z = sqrt(x^2 + y^2) capped by the unit sphere, meeting "
         "along a circle of radius 1/sqrt 2, with the projected disk dashed on the floor"))
