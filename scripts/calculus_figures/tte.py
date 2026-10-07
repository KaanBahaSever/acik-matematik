# -*- coding: utf-8 -*-
"""
Figures of the chapter "Eğrisel İntegraller için Temel Teorem"
(dersler/integral-calculus/egrisel-integraller-icin-temel-teorem.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box and never directly under a heading.
Concept figures stay visible: `temel-teorem` and `kapali-egri` sit in the
statements of their theorems (before the proof), `egri-turleri` and
`basit-baglantili` directly below the definitions of a simple curve and of a
simply-connected region, `alanlar` in the prose after the two examples of the
test; `sarmal` and `ornek-4` sit under the question text of their examples.
Only `potansiyel-insa` lives in a proof block, because it draws the steps of
that proof.
The figures are NOT produced at build time. Run

    python scripts/calculus_figures/tte.py
    python scripts/center_figures.py "calculus-tte-*.md"
    python scripts/check_figure_labels.py "scripts/_figures/calculus-tte-*.md"

and paste the markup of scripts/_figures/calculus-tte-<name>.md into the .qmd.
Captions are Turkish on purpose; aria labels are plain ASCII.
"""
import html
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, panel_title, TEXT, THEORY, PRACTICE, BASE, BG, WIDE  # noqa: E402
from svg_plot3 import Camera, Space  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "calculus-tte-"

MINUS = "&#8722;"
NABLA = "&#8711;"
ZWSP = chr(0x200B)
PI = math.pi
DEG = PI / 180


def save(name, markup):
    (OUT_DIR / f"{PREFIX}{name}.md").write_text(markup, encoding="utf-8", newline="\n")
    print(f"{PREFIX}{name}.md")


def it(s):
    """Italic run inside an SVG <text>."""
    return f'<tspan font-style="italic">{s}</tspan>'


def bf(s):
    """Bold upright run (vectors) inside an SVG <text>."""
    return f'<tspan font-weight="700">{s}</tspan>'


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


def text_w(s, size):
    """Rough advance width of a label (0.5 em per visible character, tspans at their own size)."""
    def count(t):
        return len(html.unescape(re.sub(r"<[^>]+>", "", t)).replace(ZWSP, ""))
    width = 0.0
    for m in re.finditer(r'<tspan font-size="([\d.]+)"[^>]*>(.*?)</tspan>', s):
        width += count(m.group(2)) * 0.5 * float(m.group(1))
    rest = re.sub(r'<tspan font-size="[\d.]+"[^>]*>.*?</tspan>', "", s)
    return width + count(rest) * 0.5 * size


def plabel(p, x, y, s, dx=0, dy=0, color=TEXT, size=11.5, anchor="start", bold=False):
    """Label on a page-coloured plate, for text that must sit on lines or fills."""
    px, py = p.X(x) + dx, p.Y(y) + dy
    w = text_w(s, size)
    x0 = px - (w / 2 if anchor == "middle" else w if anchor == "end" else 0)
    p.add(f'<rect x="{x0 - 2.5:.1f}" y="{py - 0.8 * size - 1:.1f}" width="{w + 5:.1f}" '
          f'height="{size + 3:.1f}" rx="3" fill="{BG}" opacity="0.88"/>')
    p.label(x, y, s, dx, dy, color, size, anchor, bold)


def splabel(S, P, s, dx=0, dy=0, color=TEXT, size=11.5, anchor="start", bold=False):
    """plabel() at a space point."""
    X, Y = S.pt(P)
    plabel(S.p, X, Y, s, dx, dy, color, size, anchor, bold)


def catmull(points, n=24, closed=False):
    """Smooth curve through the given points (centripetal-free uniform Catmull-Rom)."""
    P = list(points)
    if closed:
        P = [P[-1]] + P + [P[0], P[1]]
    else:
        P = [P[0]] + P + [P[-1]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(n):
            t = k / n
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * (2 * p1[c] + (-p0[c] + p2[c]) * t
                                    + (2 * p0[c] - 5 * p1[c] + 4 * p2[c] - p3[c]) * t2
                                    + (-p0[c] + 3 * p1[c] - 3 * p2[c] + p3[c]) * t3) for c in range(2)))
    out.append(P[-2])
    return out


def arrow_on(p, pts, at, color, width=1.8, head=8.5):
    """Arrowhead on a polyline at the fraction `at` of its points, pointing along the polyline."""
    k = max(2, min(len(pts) - 3, int(at * (len(pts) - 1))))
    p.arrow(pts[k - 2], pts[k + 2], color, width, head)


def blob(cx, cy, rx, ry, wobble=(), n=160):
    """Closed smooth 'potato' curve: an ellipse with a few cosine wobbles of the radius."""
    pts = []
    for s in range(n):
        t = 2 * PI * s / n
        r = 1.0 + sum(a * math.cos(k * t + ph) for a, k, ph in wobble)
        pts.append((cx + rx * r * math.cos(t), cy + ry * r * math.sin(t)))
    return pts


def region_with_holes(p, outer, holes, color=THEORY, opacity=0.16, stroke=THEORY, width=1.6):
    """Shaded region bounded by `outer` with the closed curves `holes` cut out (even-odd fill)."""
    def ring(pts):
        return "M" + " L".join(p.P(x, y) for x, y in pts) + " Z"
    d = " ".join(ring(c) for c in [outer] + list(holes))
    p.add(f'<path d="{d}" fill="{color}" fill-opacity="{opacity}" fill-rule="evenodd" '
          f'stroke="{stroke}" stroke-width="{width}" stroke-linejoin="round"/>')


def compact_arrows(p, arrows, color=THEORY, width=1.1, head=5.5, dot_r=1.3):
    """Many arrows as two paths (shafts and heads); arrows = [(P0, P1)] in data coordinates."""
    shafts, heads, dots = [], [], []
    for P0, P1 in arrows:
        x0, y0, x1, y1 = p.X(P0[0]), p.Y(P0[1]), p.X(P1[0]), p.Y(P1[1])
        lpx = math.hypot(x1 - x0, y1 - y0)
        if lpx < 1.6:
            dots.append((P0[0], P0[1]))
            continue
        h = min(head, 0.55 * lpx)
        ux, uy = (x1 - x0) / lpx, (y1 - y0) / lpx
        sx, sy = x1 - ux * h * 0.8, y1 - uy * h * 0.8
        shafts.append(f"M{x0:.1f},{y0:.1f}L{sx:.1f},{sy:.1f}")
        hw = h * 0.42
        heads.append(f"M{x1:.1f},{y1:.1f}L{x1 - ux * h - uy * hw:.1f},{y1 - uy * h + ux * hw:.1f}"
                     f"L{x1 - ux * h + uy * hw:.1f},{y1 - uy * h - ux * hw:.1f}Z")
    if shafts:
        p.add(f'<path d="{"".join(shafts)}" fill="none" stroke="{color}" stroke-width="{width}" '
              f'stroke-linecap="round" opacity="0.8"/>')
        p.add(f'<path d="{"".join(heads)}" fill="{color}" stroke="none" opacity="0.8"/>')
    if dots:
        p.points(dots, color, dot_r)


def field_grid(p, F, xs, ys, fill=0.85, color=THEORY):
    """Arrows at the grid nodes, all shortened by one common factor (lengths stay comparable)."""
    vals = [((x, y), F(x, y)) for x in xs for y in ys]
    big = max(math.hypot(*v) for _, v in vals)
    step = min(xs[1] - xs[0], ys[1] - ys[0])
    s = fill * step / big
    compact_arrows(p, [(P0, (P0[0] + s * V[0], P0[1] + s * V[1])) for P0, V in vals], color)


def frame(p, color=TEXT, opacity=0.35):
    """Rounded frame around a plotting panel."""
    p.add(f'<rect x="{p.x0:.1f}" y="{p.y0:.1f}" width="{p.w:.1f}" height="{p.h:.1f}" rx="7" '
          f'fill="none" stroke="{color}" stroke-width="1.1" opacity="{opacity}"/>')


def signed(v):
    return (MINUS if v < 0 else "") + f"{abs(v):g}"


C1 = it("C") + sub("1")
C2 = it("C") + sub("2")

# ============================================================
# temel-teorem: level curves of f = x^2 + y^2 and two paths from A to B
# ============================================================
p = eq_plot(40, 30, 118, (-0.25, 2.85), (-0.25, 2.75))
p.origin_axes(it("x"), it("y"))
LEVELS = (1, 2, 3, 4, 5, 6)
for k in LEVELS:
    r = math.sqrt(k)
    p.line([(r * math.cos(t * DEG), r * math.sin(t * DEG)) for t in range(0, 91)], TEXT, 1.0, None, 0.42)
A = (math.cos(72 * DEG), math.sin(72 * DEG))
B = (2 * math.cos(18 * DEG), 2 * math.sin(18 * DEG))
c1 = catmull([A, (0.62, 1.32), (1.25, 1.18), B], 30)
c2 = catmull([A, (0.12, 1.55), (0.62, 2.22), (1.55, 1.95), (2.32, 0.95), B], 30)
p.line(c1, PRACTICE, 2.1)
p.line(c2, BASE, 2.1)
arrow_on(p, c1, 0.42, PRACTICE, 2.1)
arrow_on(p, c2, 0.47, BASE, 2.1)
p.points([A, B], TEXT, 4.2)
p.label(*A, it("A"), -9, 4, TEXT, 13, "end", True)
p.label(*B, it("B"), 5, 16, TEXT, 13, "start", True)
p.label(0.86, 1.30, C1, -2, 18, PRACTICE, 13, "middle", True)
p.label(2.12, 1.86, C2, 0, 0, BASE, 13, "start", True)
# level values just above the x axis, one per circle
for k in LEVELS:
    r = math.sqrt(k)
    t = 6 * DEG
    lab = (it("f") + " = 1") if k == 1 else str(k)
    plabel(p, r * math.cos(t), r * math.sin(t), lab, 0, 4, TEXT, 10.5, "middle")
p.label(0, 0, "0", -6, 14, TEXT, 11, "end")
save("temel-teorem", figure(
    int(p.x0 + p.w + 30), int(p.y0 + p.h + 30), [p],
    "<em>f</em>(<em>x</em>, <em>y</em>) = <em>x</em>² + <em>y</em>² fonksiyonunun <em>f</em> = 1, 2, …, 6 "
    "seviye eğrileri ve <em>A</em>'dan <em>B</em>'ye giden iki yol. <em>A</em> noktası <em>f</em> = 1, "
    "<em>B</em> noktası <em>f</em> = 4 eğrisi üzerindedir. "
    "<em>C</em><sub>2</sub> yolu <em>f</em> = 6 eğrisini aşıp geri dönse de iki yol boyunca "
    "∫ ∇<em>f</em> · <em>d</em><strong>r</strong> = <em>f</em>(<em>B</em>) &#8722; <em>f</em>(<em>A</em>) = 4 &#8722; 1 = 3 olur: "
    "yükselirken toplanan değerler alçalırken geri verilir.",
    aria="Quarter circles x^2 + y^2 = 1, 2, ..., 6 in the first quadrant, a point A on the circle f = 1 "
         "and a point B on the circle f = 4, joined by a short path C1 and by a long path C2 that goes "
         "out beyond the circle f = 6 and comes back"))

# ============================================================
# sarmal: the helix r(t) = (cos t, sin t, t), 0 <= t <= pi, and the segment from A to B
# ============================================================
# a flatter, more side-on view spreads A and B apart, and their labels sit outside the curve,
# so that the tall half turn does not make a narrow, very tall figure
cam = Camera(azimuth=55, elevation=18)
H = PI
box = [(1.75, 0, 0), (-1.25, 0, 0), (0, 1.5, 0), (0, -1.25, 0), (0, 0, H + 0.4),
       (1.0, 0, 0), (-1, 0, H), (0, 1, H / 2)]
pl, S = fit_space(cam, box, 40, 30, 92, 0.3)
# axes first, so that the curves are drawn over them
S.axes(1.75, 1.5, H + 0.4, -1.25, -1.25, 0.0, size=10, offsets=((-6, 12), (10, 5), (-10, -3)))
helix = [(math.cos(t), math.sin(t), t) for t in [H * k / 200 for k in range(201)]]
S.line(helix, BASE, 2.2)
S.arrow(helix[118], helix[126], BASE, 2.2, 9)
Aa, Bb = (1.0, 0.0, 0.0), (-1.0, 0.0, H)


def seg_ab(s):
    return (1 - 2 * s, 0.0, H * s)


S.line([Aa, Bb], PRACTICE, 1.9, "6 4")
# the midpoint of AB lies on the z axis, so the arrowhead sits a little above it
S.arrow(seg_ab(0.60), seg_ab(0.72), PRACTICE, 1.9, 8)
S.drop(Bb, 0.0)
# the shadow of the helix on the floor: half of the unit circle from A to (-1, 0, 0)
S.line([(math.cos(t), math.sin(t), 0.0) for t in [H * k / 100 for k in range(101)]], TEXT, 1.0, "4 3", 0.5)
S.point(Aa, TEXT, 4.2)
S.point(Bb, TEXT, 4.2)
splabel(S, Aa, it("A") + "(1, 0, 0)", -9, -8, TEXT, 10, "end")
splabel(S, Bb, it("B") + "(" + MINUS + "1, 0, " + it("π") + ")", 9, -7, TEXT, 10)
S.label((math.cos(0.78 * H), math.sin(0.78 * H), 0.78 * H), it("C"), 9, 5, BASE, 12.5, "start", True)
S.label((0, 0, 0), "O", -7, 13, TEXT, 10, "end")
save("sarmal", figure(
    int(pl.x0 + pl.w + 30), int(pl.y0 + pl.h + 30), [pl],
    "<em>C</em> sarmalı <em>A</em>(1, 0, 0) noktasından <em>B</em>(&#8722;1, 0, <em>π</em>) noktasına "
    "<em>z</em> ekseni çevresinde yarım tur atarak çıkar; zemindeki kesikli yay, sarmalın "
    "<em>xy</em>-düzlemindeki izdüşümüdür. Kesikli doğru parçası aynı iki noktayı birleştirir. Temel teoreme "
    "göre ∇<em>f</em> alanının bu iki yol boyunca integralleri eşittir.",
    aria="A half turn of the helix (cos t, sin t, t) from A(1, 0, 0) up to B(-1, 0, pi) around the z axis, "
         "and the dashed straight segment from A to B"))

# ============================================================
# kapali-egri: (a) a closed path split at A and B; (b) two paths from A to B closed up by -C2
# ============================================================
pa = eq_plot(40, 40, 70, (-2.3, 2.3), (-1.7, 1.75))
pb = eq_plot(pa.x0 + pa.w + 40, 40, 70, (-2.3, 2.3), (-1.7, 1.75))
loop = blob(0, 0, 1.85, 1.15, [(0.12, 2, 0.6), (0.06, 3, 1.1)], 240)
iA = min(range(len(loop)), key=lambda i: loop[i][0])           # leftmost point
iB = min(range(len(loop)), key=lambda i: -loop[i][0])          # rightmost point
Ap, Bp = loop[iA], loop[iB]
# walk from A to B over the top (the blob is traced counter-clockwise, so go backwards)
top = []
i = iA
while True:
    top.append(loop[i])
    if i == iB:
        break
    i = (i - 1) % len(loop)
bottom = []
i = iB
while True:
    bottom.append(loop[i])
    if i == iA:
        break
    i = (i - 1) % len(loop)
if top[len(top) // 2][1] < 0:      # make sure `top` is the upper arc
    top, bottom = [q for q in reversed(bottom)], [q for q in reversed(top)]
# (a) C = C1 (A -> B over the top) followed by C2 (B -> A along the bottom)
pa.line(top, PRACTICE, 2.1)
pa.line(bottom, BASE, 2.1)
arrow_on(pa, top, 0.5, PRACTICE, 2.1)
arrow_on(pa, bottom, 0.5, BASE, 2.1)
pa.points([Ap, Bp], TEXT, 4.2)
pa.label(*Ap, it("A"), -8, 5, TEXT, 13, "end", True)
pa.label(*Bp, it("B"), 8, 5, TEXT, 13, "start", True)
tq, bq = top[len(top) // 2], bottom[len(bottom) // 2]
pa.label(*tq, C1, 0, -12, PRACTICE, 13, "middle", True)
pa.label(*bq, C2, 0, 24, BASE, 13, "middle", True)
panel_title(pa, "(a)  " + it("C") + " = " + C1 + " ardından " + C2)
# (b) two paths C1, C2 from A to B; the closed path C1 followed by -C2
A2, B2 = (-1.9, -0.25), (1.9, 0.3)
up = catmull([A2, (-1.0, 1.0), (0.2, 1.15), (1.2, 1.05), B2], 30)
lo = catmull([A2, (-0.9, -1.05), (0.3, -0.75), (1.3, -0.95), B2], 30)
pb.line(up, PRACTICE, 2.1)
pb.line(lo, BASE, 2.1)
arrow_on(pb, up, 0.5, PRACTICE, 2.1)
lo_back = list(reversed(lo))
arrow_on(pb, lo_back, 0.55, BASE, 2.1)
pb.points([A2, B2], TEXT, 4.2)
pb.label(*A2, it("A"), -8, 5, TEXT, 13, "end", True)
pb.label(*B2, it("B"), 8, 5, TEXT, 13, "start", True)
pb.label(0.2, 1.15, C1, 0, -12, PRACTICE, 13, "middle", True)
pb.label(0.3, -0.85, MINUS + C2, 0, 26, BASE, 13, "middle", True)
panel_title(pb, "(b)  " + it("C") + " = " + C1 + " ardından " + MINUS + C2)
save("kapali-egri", figure(
    int(pb.x0 + pb.w + 30), int(pa.y0 + pa.h + 30), [pa, pb],
    "(a) Kapalı bir <em>C</em> yolu, üzerindeki iki <em>A</em>, <em>B</em> noktasında ikiye ayrılır: "
    "<em>A</em>'dan <em>B</em>'ye giden <em>C</em><sub>1</sub> ve <em>B</em>'den <em>A</em>'ya dönen "
    "<em>C</em><sub>2</sub>. (b) <em>A</em>'dan <em>B</em>'ye giden iki yoldan <em>C</em><sub>1</sub>'i "
    "izleyip <em>C</em><sub>2</sub>'yi ters yönde (&#8722;<em>C</em><sub>2</sub>) geri dönmek kapalı bir yol verir.",
    css_class=WIDE,
    aria="Two panels: a closed curve cut at a left point A and a right point B into an upper arc C1 from A "
         "to B and a lower arc C2 from B back to A; two paths from A to B, the upper one C1 and the lower "
         "one traversed backwards as -C2, together forming a closed path"))

# ============================================================
# potansiyel-insa: the paths used to differentiate f(x, y) = integral from (a, b) to (x, y)
# ============================================================
pa = eq_plot(40, 40, 62, (-0.3, 4.9), (-0.3, 3.7))
pb = eq_plot(pa.x0 + pa.w + 36, 40, 62, (-0.3, 4.9), (-0.3, 3.7))
D = blob(2.35, 1.75, 2.15, 1.5, [(0.1, 2, 0.4), (0.07, 3, 2.0), (0.04, 5, 0.3)], 240)
X, Y, RD = 3.15, 2.15, 0.62
base = (0.95, 0.75)
for p, kind in ((pa, "h"), (pb, "v")):
    p.origin_axes(it("x"), it("y"))
    p.polygon(D, THEORY, 0.10, THEORY, 1.5)
    p.polygon([(X + RD * math.cos(t * DEG), Y + RD * math.sin(t * DEG)) for t in range(0, 360, 4)],
              BASE, 0.16, BASE, 1.0)
    if kind == "h":
        mid = (X - 0.45, Y)
        path = catmull([base, (1.35, 1.55), (2.05, 2.0), mid], 30)
        seg = [mid, (X, Y)]
    else:
        mid = (X, Y - 0.45)
        path = catmull([base, (1.7, 1.0), (2.6, 1.45), mid], 30)
        seg = [mid, (X, Y)]
    p.line(path, PRACTICE, 2.0)
    arrow_on(p, path, 0.55, PRACTICE, 2.0, 8)
    p.arrow(seg[0], seg[1], BASE, 2.4, 8)
    p.points([base, mid, (X, Y)], TEXT, 3.6)
    p.label(*base, "(" + it("a") + ", " + it("b") + ")", 4, 15, TEXT, 11.5, "start")
    p.label(0.7, 2.75, it("D"), 0, 0, THEORY, 14, "middle", True)
    if kind == "h":
        plabel(p, *mid, "(" + it("x") + sub("1") + ", " + it("y") + ")", -6, -9, TEXT, 11.5, "end")
        plabel(p, X, Y, "(" + it("x") + ", " + it("y") + ")", 9, 4, TEXT, 11.5, "start")
        p.label(1.55, 1.85, C1, -10, 0, PRACTICE, 13, "end", True)
        p.label(X - 0.22, Y, C2, 0, 18, BASE, 13, "middle", True)
        panel_title(p, "(a)  yatay son parça")
    else:
        plabel(p, *mid, "(" + it("x") + ", " + it("y") + sub("1") + ")", 8, 10, TEXT, 11.5, "start")
        plabel(p, X, Y, "(" + it("x") + ", " + it("y") + ")", 9, -4, TEXT, 11.5, "start")
        p.label(2.0, 1.25, C1, 4, 18, PRACTICE, 13, "middle", True)
        p.label(X, Y - 0.22, C2, -8, 4, BASE, 13, "end", True)
        panel_title(p, "(b)  düşey son parça")
save("potansiyel-insa", figure(
    int(pb.x0 + pb.w + 30), int(pa.y0 + pa.h + 30), [pa, pb],
    "<em>f</em>(<em>x</em>, <em>y</em>) değerini veren yol, (<em>x</em>, <em>y</em>) merkezli ve "
    "<em>D</em>'de kalan diskin içinde bir doğru parçasıyla biter. (a) Yatay <em>C</em><sub>2</sub> "
    "parçasında <em>dy</em> = 0 olduğundan yalnız <em>P</em> katkı verir ve <em>f<sub>x</sub></em> = <em>P</em> "
    "bulunur. (b) Düşey parçada <em>dx</em> = 0'dır ve <em>f<sub>y</sub></em> = <em>Q</em> bulunur.",
    css_class=WIDE,
    aria="Two panels with a region D, a base point (a, b) and a disk around (x, y) inside D: a path C1 to "
         "(x1, y) followed by a horizontal segment C2 to (x, y); a path C1 to (x, y1) followed by a vertical "
         "segment C2 to (x, y)"))

# ============================================================
# egri-turleri: simple / not simple, closed / not closed
# ============================================================
W1 = 150
panels = []
x0 = 30
for k in range(4):
    q = eq_plot(x0, 46, 50, (-1.5, 1.5), (-1.3, 1.3))
    panels.append(q)
    x0 += q.w + 22
q1, q2, q3, q4 = panels
# simple, not closed: a gentle S curve
s_curve = catmull([(-1.25, -0.75), (-0.6, 0.85), (0.15, -0.2), (0.75, 0.75), (1.25, -0.5)], 26)
q1.line(s_curve, PRACTICE, 2.0)
q1.points([s_curve[0], s_curve[-1]], TEXT, 3.6)
panel_title(q1, "basit, kapalı değil", TEXT, 11)
# not simple, not closed: a curve with one loop
loop_curve = catmull([(-1.3, -0.9), (-0.3, 0.1), (0.55, 0.95), (0.95, 0.2), (0.3, -0.25),
                      (-0.2, 0.55), (0.2, 1.0), (1.3, 0.9)], 26)
q2.line(loop_curve, PRACTICE, 2.0)
q2.points([loop_curve[0], loop_curve[-1]], TEXT, 3.6)
panel_title(q2, "basit değil, kapalı değil", TEXT, 11)
# simple closed
q3.line(blob(0, 0, 1.15, 0.85, [(0.12, 2, 0.8), (0.07, 3, 0.2)], 160) + [blob(0, 0, 1.15, 0.85, [(0.12, 2, 0.8), (0.07, 3, 0.2)], 160)[0]], PRACTICE, 2.0)
panel_title(q3, "basit, kapalı", TEXT, 11)
# not simple, closed: a figure eight (lemniscate-like)
eight = [(1.25 * math.sin(t), 0.85 * math.sin(t) * math.cos(t) * 1.6) for t in [2 * PI * k / 200 for k in range(201)]]
q4.line(eight, PRACTICE, 2.0)
panel_title(q4, "basit değil, kapalı", TEXT, 11)
save("egri-turleri", figure(
    int(q4.x0 + q4.w + 24), int(q1.y0 + q1.h + 24), panels,
    "Eğri türleri. Kapalı olmayan eğrilerde uç noktalar işaretlidir. İkinci eğri kendisini bir kez keser; "
    "dördüncü eğri (8 biçimi) başladığı yere döner ama ortadaki noktadan iki kez geçer.",
    css_class=WIDE,
    aria="Four curves: a simple non-closed S shaped curve, a non-closed curve with a loop that crosses "
         "itself, a simple closed potato shaped curve and a closed figure eight"))

# ============================================================
# basit-baglantili: simply connected, with a hole, two pieces
# ============================================================
panels = []
x0 = 30
for k in range(3):
    q = eq_plot(x0, 46, 58, (-1.75, 1.75), (-1.35, 1.35))
    panels.append(q)
    x0 += q.w + 26
r1, r2, r3 = panels
outer = blob(0, 0, 1.5, 1.1, [(0.1, 2, 0.5), (0.06, 3, 1.6)], 200)
region_with_holes(r1, outer, [])
inner_curve = blob(0.1, 0.0, 0.85, 0.55, [(0.1, 2, 2.0)], 120)
r1.line(inner_curve + [inner_curve[0]], PRACTICE, 1.6, "5 3")
panel_title(r1, "basit bağlantılı", TEXT, 11)
hole = blob(0.15, 0.05, 0.42, 0.32, [(0.08, 2, 0.4)], 100)
region_with_holes(r2, outer, [list(reversed(hole))])
around = blob(0.15, 0.05, 0.95, 0.72, [(0.06, 2, 1.0)], 120)
r2.line(around + [around[0]], PRACTICE, 1.6, "5 3")
panel_title(r2, "delikli", TEXT, 11)
left = blob(-0.85, 0.15, 0.72, 0.85, [(0.08, 2, 0.3)], 140)
right = blob(0.95, -0.15, 0.62, 0.72, [(0.08, 3, 1.0)], 140)
region_with_holes(r3, left, [])
region_with_holes(r3, right, [])
panel_title(r3, "iki parçalı", TEXT, 11)
save("basit-baglantili", figure(
    int(r3.x0 + r3.w + 24), int(r1.y0 + r1.h + 24), panels,
    "Soldaki bölge basit bağlantılıdır: içindeki her basit kapalı eğri (kesikli) yalnız bölgenin noktalarını "
    "çevreler. Ortadaki bölgede deliği dolanan kesikli eğri, bölgede olmayan noktaları çevreler; sağdaki küme "
    "ise bağlantılı bile değildir. Bu iki küme basit bağlantılı değildir.",
    css_class=WIDE,
    aria="Three shaded sets: a region without holes containing a dashed simple closed curve, the same region "
         "with a hole and a dashed curve around the hole, and a set made of two separate pieces"))


# ============================================================
# alanlar: the fields of the two examples of the test
# ============================================================
def Fa(x, y):
    return (x - y, x - 2)


def Fb(x, y):
    return (3 + 2 * x * y, x * x - 3 * y * y)


pa = eq_plot(40, 40, 45, (-1.35, 5.35), (-1.35, 5.35))
pb = eq_plot(pa.x0 + pa.w + 50, 40, 68.5, (-2.2, 2.2), (-2.2, 2.2))
for p in (pa, pb):
    frame(p)
# (a)
xs = [-0.85 + 0.57 * i for i in range(11)]
field_grid(pa, Fa, xs, xs, 0.8, THEORY)
circ = [(2 + 2 * math.cos(t * DEG), 2 + 2 * math.sin(t * DEG)) for t in range(0, 361, 3)]
pa.line(circ, PRACTICE, 2.2)
for t0 in (40, 160, 280):
    pa.arrow((2 + 2 * math.cos((t0 - 6) * DEG), 2 + 2 * math.sin((t0 - 6) * DEG)),
             (2 + 2 * math.cos((t0 + 6) * DEG), 2 + 2 * math.sin((t0 + 6) * DEG)), PRACTICE, 2.2, 9)
pa.points([(2, 2)], TEXT, 3.2)
for v in (0, 2, 4):
    pa.text_px(pa.X(v), pa.y0 + pa.h + 15, signed(v), TEXT, 10.5, "middle")
    pa.text_px(pa.x0 - 6, pa.Y(v) + 4, signed(v), TEXT, 10.5, "end")
plabel(pa, 2, 2, "(2, 2)", 0, 17, TEXT, 10.5, "middle")
plabel(pa, 2 + 2 * math.cos(-40 * DEG), 2 + 2 * math.sin(-40 * DEG), it("C"), 10, 12, PRACTICE, 13, "start", True)
panel_title(pa, "(a)  " + it("P") + " = " + it("x") + " " + MINUS + " " + it("y") + ",  " + it("Q") + " = "
            + it("x") + " " + MINUS + " 2")
# (b)
xs = [-1.8 + 0.4 * i for i in range(10)]
field_grid(pb, Fb, xs, xs, 0.85, THEORY)
circ = [(1.2 * math.cos(t * DEG), 1.2 * math.sin(t * DEG)) for t in range(0, 361, 3)]
pb.line(circ, PRACTICE, 2.2)
for t0 in (30, 150, 270):
    pb.arrow((1.2 * math.cos((t0 - 7) * DEG), 1.2 * math.sin((t0 - 7) * DEG)),
             (1.2 * math.cos((t0 + 7) * DEG), 1.2 * math.sin((t0 + 7) * DEG)), PRACTICE, 2.2, 9)
for v in (-2, 0, 2):
    pb.text_px(pb.X(v), pb.y0 + pb.h + 15, signed(v), TEXT, 10.5, "middle")
    pb.text_px(pb.x0 - 6, pb.Y(v) + 4, signed(v), TEXT, 10.5, "end")
plabel(pb, 1.2 * math.cos(-45 * DEG), 1.2 * math.sin(-45 * DEG), it("C"), 10, 12, PRACTICE, 13, "start", True)
panel_title(pb, "(b)  " + it("P") + " = 3 + 2" + it("xy") + ",  " + it("Q") + " = " + it("x") + sup("2")
            + " " + MINUS + " 3" + it("y") + sup("2"))
save("alanlar", figure(
    int(pb.x0 + pb.w + 30), int(pa.y0 + pa.h + 34), [pa, pb],
    "Konservatiflik ölçütünün iki örneğindeki alanlar; okların hepsi aynı oranda kısaltılmıştır. "
    "(a) Merkezi (2, 2), yarıçapı 2 olan <em>C</em> çemberi boyunca oklar hep dolaşılma yönüne bakar ve "
    "integral 8<em>π</em> çıkar. (b) Konservatif alanda <em>C</em> çemberinin bazı yerlerinde oklar "
    "dolaşılma yönüne, bazı yerlerinde ters yöne bakar; katkılar birbirini götürür ve integral 0'dır.",
    css_class=WIDE,
    aria="Two arrow plots: the field (x - y, x - 2) on the square from -1 to 5 with the circle of radius 2 "
         "about (2, 2), along which every arrow points counterclockwise; the field (3 + 2xy, x^2 - 3y^2) on "
         "the square from -2 to 2 with a circle of radius 1.2 along which the arrows point partly along and "
         "partly against the curve"))

# ============================================================
# ornek-4: the curve r(t) = e^t sin t i + e^t cos t j, 0 <= t <= pi, and the segment C1
# ============================================================
EP = math.exp(PI)
p = Plot(60, 30, 300, 360, (-3.2, 10.0), (-25.5, 3.5))
p.origin_axes(it("x"), it("y"))
for v in (5,):
    p.add(f'<line x1="{p.X(v):.1f}" y1="{p.Y(0) - 3:.1f}" x2="{p.X(v):.1f}" y2="{p.Y(0) + 3:.1f}" '
          f'stroke="{TEXT}" stroke-width="1" opacity="0.7"/>')
    p.text_px(p.X(v) - 4, p.Y(0) + 15, str(v), TEXT, 10.5, "middle")
for v in (-10, -20):
    p.add(f'<line x1="{p.X(0) - 3:.1f}" y1="{p.Y(v):.1f}" x2="{p.X(0) + 3:.1f}" y2="{p.Y(v):.1f}" '
          f'stroke="{TEXT}" stroke-width="1" opacity="0.7"/>')
    p.text_px(p.X(0) - 7, p.Y(v) + 4, signed(v), TEXT, 10.5, "end")
curve = [(math.exp(t) * math.sin(t), math.exp(t) * math.cos(t)) for t in [PI * k / 300 for k in range(301)]]
p.line(curve, PRACTICE, 2.2)
arrow_on(p, curve, 0.76, PRACTICE, 2.2, 9)
p.line([(0, 1), (0, -EP)], BASE, 2.6)
p.arrow((0, -9.0), (0, -11.5), BASE, 2.6, 9)
p.points([(0, 1), (0, -EP)], TEXT, 4.0)
plabel(p, 0, 1, "(0, 1)", -8, -6, TEXT, 11.5, "end")
plabel(p, 0, -EP, "(0, " + MINUS + it("e") + sup(it("π")) + ")", -8, 5, TEXT, 11.5, "end")
p.label(math.exp(2.0) * math.sin(2.0), math.exp(2.0) * math.cos(2.0), it("C"), 10, 4, PRACTICE, 14, "start", True)
p.label(0, -5.0, C1, -9, 4, BASE, 14, "end", True)
save("ornek-4", figure(
    int(p.x0 + p.w + 30), int(p.y0 + p.h + 30), [p],
    "<em>C</em> eğrisi <strong>r</strong>(<em>t</em>) = <em>e<sup>t</sup></em> sin <em>t</em> <strong>i</strong> + "
    "<em>e<sup>t</sup></em> cos <em>t</em> <strong>j</strong>, 0 ≤ <em>t</em> ≤ <em>π</em>, (0, 1) noktasından "
    "sağa doğru açılıp (0, &#8722;<em>e<sup>π</sup></em>) ≈ (0; &#8722;23,1) noktasına iner. "
    "<em>C</em><sub>1</sub>, aynı iki noktayı birleştiren düşey doğru parçasıdır. Eksenlerdeki ölçekler farklıdır.",
    css_class="ders-grafik",
    aria="The curve e^t (sin t, cos t) for t from 0 to pi, starting at (0, 1), bulging to the right up to "
         "x about 7.5 and ending at (0, -e^pi), together with the vertical segment C1 on the y axis between "
         "the same two points"))
