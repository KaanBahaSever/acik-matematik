# -*- coding: utf-8 -*-
"""
Figures of the chapter "Vektör Alanları"
(dersler/integral-calculus/vektor-alanlari.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box and never directly under a heading.
Concept figures stay visible: nokta-ok below the definition of a vector field,
bilgisayar in the prose on scaled computer plots, akis below the definition of
a flow line, cekim in the prose after the gravitational field example and
gradyan under the question text of the gradient field example. The figures of
the worked solutions (donme, zk) and of the sketching exercise (ciz) sit in
their solution blocks.
The figures are NOT produced at build time. Run

    python scripts/calculus_figures/val.py
    python scripts/center_figures.py "calculus-val-*.md"
    python scripts/check_figure_labels.py "scripts/_figures/calculus-val-*.md"

and paste the markup of scripts/_figures/calculus-val-<name>.md into the .qmd.
Captions are Turkish on purpose; aria labels are plain ASCII.
"""
import html
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, panel_title, TEXT, THEORY, PRACTICE, BASE, BG, WIDE  # noqa: E402
from svg_plot3 import Camera, Space, vadd, vsub, vscale, vnorm  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "calculus-val-"

MINUS = "&#8722;"
NABLA = "&#8711;"
ZWSP = chr(0x200B)          # the zero-width space the sub/sup helpers leave behind


def save(name, markup):
    (OUT_DIR / f"{PREFIX}{name}.md").write_text(markup, encoding="utf-8", newline="\n")
    print(f"{PREFIX}{name}.md")


def it(s):
    """Italic run inside an SVG <text>."""
    return f'<tspan font-style="italic">{s}</tspan>'


def bf(s):
    """Bold upright run (vectors) inside an SVG <text>."""
    return f'<tspan font-weight="700">{s}</tspan>'


def sup(s, size=9):
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
    """Label on a page-coloured plate, for text that must sit on top of arrows."""
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


def vec2(p, P0, V, s=1.0, color=THEORY, width=1.4, head=7.0, dot_r=1.4):
    """Arrow from P0 along s*V; the head shrinks on short arrows, a zero vector becomes a dot."""
    P1 = (P0[0] + s * V[0], P0[1] + s * V[1])
    lpx = math.hypot(p.X(P1[0]) - p.X(P0[0]), p.Y(P1[1]) - p.Y(P0[1]))
    if lpx < 1.6:
        p.points([P0], color, dot_r)
        return
    p.arrow(P0, P1, color, width, min(head, 0.55 * lpx))


def vec3(S, P0, V, s=1.0, color=THEORY, width=1.4, head=7.0, dot_r=1.4):
    """Space arrow from P0 along s*V (the head is sized on the projected length)."""
    P1 = vadd(P0, vscale(s, V))
    a, b = S.pt(P0), S.pt(P1)
    p = S.p
    lpx = math.hypot(p.X(b[0]) - p.X(a[0]), p.Y(b[1]) - p.Y(a[1]))
    if lpx < 1.6:
        p.points([a], color, dot_r)
        return
    p.arrow(a, b, color, width, min(head, 0.55 * lpx))


def compact_arrows(p, arrows, color=THEORY, width=1.2, head=6.0, dot_r=1.3):
    """Many arrows as two paths (all shafts, all heads); arrows = [(P0, P1)] in data coordinates.

    Heads shrink on short arrows and a vanishing arrow becomes a dot, as in vec2(); writing the whole
    field as two paths keeps the markup small.
    """
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
              f'stroke-linecap="round"/>')
        p.add(f'<path d="{"".join(heads)}" fill="{color}" stroke="none"/>')
    if dots:
        p.points(dots, color, dot_r)


def field_grid(p, F, xs, ys, fill=0.85, color=THEORY, width=1.2, head=6.0):
    """Computer-style plot: arrows at the grid nodes, all shortened by one common factor."""
    vals = [((x, y), F(x, y)) for x in xs for y in ys]
    big = max(math.hypot(*v) for _, v in vals)
    step = min(xs[1] - xs[0], ys[1] - ys[0])
    s = fill * step / big
    compact_arrows(p, [(P0, (P0[0] + s * V[0], P0[1] + s * V[1])) for P0, V in vals], color, width, head)
    return s


def rdp(pts, eps):
    """Ramer-Douglas-Peucker simplification of a polyline (eps in data units)."""
    if len(pts) < 3:
        return pts
    (ax, ay), (bx, by) = pts[0], pts[-1]
    dx, dy = bx - ax, by - ay
    n = math.hypot(dx, dy)
    best, k = -1.0, 0
    for i in range(1, len(pts) - 1):
        px, py = pts[i]
        d = abs(dy * (px - ax) - dx * (py - ay)) / n if n > 0 else math.hypot(px - ax, py - ay)
        if d > best:
            best, k = d, i
    if best <= eps:
        return [pts[0], pts[-1]]
    return rdp(pts[:k + 1], eps)[:-1] + rdp(pts[k:], eps)


def frame(p, color=TEXT, opacity=0.35):
    """Rounded frame around a plotting panel."""
    p.add(f'<rect x="{p.x0:.1f}" y="{p.y0:.1f}" width="{p.w:.1f}" height="{p.h:.1f}" rx="7" '
          f'fill="none" stroke="{color}" stroke-width="1.1" opacity="{opacity}"/>')


def cross_axes(p, opacity=0.35):
    """Thin axes through the origin, clipped to the panel."""
    p.line([(p.xmin, 0), (p.xmax, 0)], TEXT, 0.9, None, opacity)
    p.line([(0, p.ymin), (0, p.ymax)], TEXT, 0.9, None, opacity)


def signed(v):
    """Tick text with a true minus sign."""
    return (MINUS if v < 0 else "") + f"{abs(v):g}"


def frame_ticks(p, values, size=10.5, opacity=0.7):
    """Tick marks with labels on the bottom and the left edge of a framed panel."""
    yb = p.y0 + p.h
    for v in values:
        X, Y = p.X(v), p.Y(v)
        p.add(f'<line x1="{X:.1f}" y1="{yb:.1f}" x2="{X:.1f}" y2="{yb + 4:.1f}" stroke="{TEXT}" '
              f'stroke-width="1" opacity="{opacity}"/>')
        p.text_px(X, yb + 16, signed(v), TEXT, size, "middle")
        p.add(f'<line x1="{p.x0 - 4:.1f}" y1="{Y:.1f}" x2="{p.x0:.1f}" y2="{Y:.1f}" stroke="{TEXT}" '
              f'stroke-width="1" opacity="{opacity}"/>')
        p.text_px(p.x0 - 7, Y + 4, signed(v), TEXT, size, "end")


def contour(f, xr, yr, level, nx=160, ny=160):
    """Marching squares: the level set f = level as a list of polylines (data coordinates)."""
    xs = [xr[0] + (xr[1] - xr[0]) * i / nx for i in range(nx + 1)]
    ys = [yr[0] + (yr[1] - yr[0]) * j / ny for j in range(ny + 1)]
    V = [[f(x, y) - level for y in ys] for x in xs]
    for i in range(nx + 1):
        for j in range(ny + 1):
            if V[i][j] == 0.0:
                V[i][j] = 1e-12

    def cut(key):
        kind, i, j = key
        if kind == "h":
            a, b = V[i][j], V[i + 1][j]
            s = a / (a - b)
            return (xs[i] + s * (xs[i + 1] - xs[i]), ys[j])
        a, b = V[i][j], V[i][j + 1]
        s = a / (a - b)
        return (xs[i], ys[j] + s * (ys[j + 1] - ys[j]))

    segs = []
    for i in range(nx):
        for j in range(ny):
            edges = [("h", i, j), ("v", i + 1, j), ("h", i, j + 1), ("v", i, j)]
            ends = [((i, j), (i + 1, j)), ((i + 1, j), (i + 1, j + 1)),
                    ((i, j + 1), (i + 1, j + 1)), ((i, j), (i, j + 1))]
            hit = [e for e, (u, w) in zip(edges, ends) if (V[u[0]][u[1]] > 0) != (V[w[0]][w[1]] > 0)]
            if len(hit) == 2:
                segs.append((hit[0], hit[1]))
            elif len(hit) == 4:
                centre = (V[i][j] + V[i + 1][j] + V[i + 1][j + 1] + V[i][j + 1]) / 4
                if (centre > 0) == (V[i][j] > 0):
                    segs += [(hit[0], hit[1]), (hit[2], hit[3])]
                else:
                    segs += [(hit[0], hit[3]), (hit[1], hit[2])]
    # chain the segments through their shared edge crossings
    nbr = {}
    for k, (a, b) in enumerate(segs):
        nbr.setdefault(a, []).append(k)
        nbr.setdefault(b, []).append(k)
    used = [False] * len(segs)
    lines = []
    for k0 in range(len(segs)):
        if used[k0]:
            continue
        used[k0] = True
        a, b = segs[k0]
        chain = [a, b]
        for direction in (0, 1):
            while True:
                end = chain[-1] if direction == 0 else chain[0]
                nxt = [k for k in nbr[end] if not used[k]]
                if not nxt:
                    break
                k = nxt[0]
                used[k] = True
                u, w = segs[k]
                new = w if u == end else u
                if direction == 0:
                    chain.append(new)
                else:
                    chain.insert(0, new)
        lines.append([cut(e) for e in chain])
    return lines


def mid_arrow(p, pts, F, color, width=1.6, head=8.0, at=0.5):
    """Arrowhead on a polyline at the fraction `at` of its points, oriented along the field F."""
    k = max(1, min(len(pts) - 2, int(at * (len(pts) - 1))))
    a, b = pts[k - 1], pts[k + 1]
    d = (b[0] - a[0], b[1] - a[1])
    v = F(*pts[k])
    if d[0] * v[0] + d[1] * v[1] < 0:
        a, b = b, a
    p.arrow(a, b, color, width, head)


VF = bf("F")


def args(*names):
    return "(" + ", ".join(it(n) for n in names) + ")"


# ============================================================
# nokta-ok: the arrow F(x, y) drawn from the point (x, y); the same in space
# ============================================================
def G2(x, y):
    return (0.55 - 0.35 * y + 0.12 * x, 0.40 + 0.30 * x - 0.08 * y)


pa = eq_plot(40, 30, 54, (-2.5, 3.4), (-1.7, 2.9))
pa.origin_axes(it("x"), it("y"))
pa.label(0, 0, "0", -6, 14, TEXT, 10.5, "end")
BASES2 = [(-1.9, 1.7), (-1.5, -0.9), (0.6, 2.1), (2.4, -0.9), (-0.7, 0.75)]
for P0 in BASES2:
    pa.points([P0], THEORY, 2.6)
    vec2(pa, P0, G2(*P0), 1.0, THEORY, 1.7, 8.0)
PH = (1.5, 0.75)
pa.points([PH], PRACTICE, 3.4)
vec2(pa, PH, G2(*PH), 1.0, PRACTICE, 2.2, 9.0)
TIP = (PH[0] + G2(*PH)[0], PH[1] + G2(*PH)[1])
pa.label(*PH, args("x", "y"), 4, 17, PRACTICE, 11.5, "start")
pa.label(*TIP, VF + args("x", "y"), 6, -4, PRACTICE, 12, "start")
panel_title(pa, "Düzlemde")

cam = Camera(azimuth=35.0, elevation=22.0)


def G3(x, y, z):
    return (-0.55 + 0.25 * z, 0.55 - 0.12 * x + 0.1 * z, 0.45 - 0.2 * y + 0.1 * x)


BASES3 = [(0.4, 2.3, 2.2), (2.6, 2.6, 0.6), (0.3, 0.6, 2.9), (2.8, 0.5, 2.6), (1.0, 3.3, 0.4)]
PH3 = (2.2, 1.0, 1.0)
ends3 = [vadd(P, G3(*P)) for P in BASES3 + [PH3]]
pb, Sb = fit_space(cam, [(0, 0, 0), (3.6, 0, 0), (0, 4.2, 0), (0, 0, 3.7)] + BASES3 + [PH3] + ends3,
                   pa.x0 + pa.w + 70, 30, 54, 0.3)
Sb.axes(3.6, 4.2, 3.7)
Sb.label((0, 0, 0), "0", -4, -6, TEXT, 10.5, "end")
for P0 in BASES3:
    Sb.point(P0, THEORY, 2.6)
    vec3(Sb, P0, G3(*P0), 1.0, THEORY, 1.7, 8.0)
Sb.drop(PH3, 0.0, TEXT, 0.4)
Sb.point(PH3, PRACTICE, 3.4)
vec3(Sb, PH3, G3(*PH3), 1.0, PRACTICE, 2.2, 9.0)
splabel(Sb, PH3, args("x", "y", "z"), -8, 4, PRACTICE, 11.5, "end")
Sb.label(vadd(PH3, G3(*PH3)), VF + args("x", "y", "z"), 6, -6, PRACTICE, 12, "start")
panel_title(pb, "Uzayda")
save("nokta-ok", figure(
    int(pb.x0 + pb.w + 30), int(max(pa.y0 + pa.h, pb.y0 + pb.h) + 30), [pa, pb],
    "Bir vektör alanı her noktaya bir vektör atar. <b>F</b>(<em>x</em>, <em>y</em>) vektörünü "
    "başlangıcı (<em>x</em>, <em>y</em>) noktası olan bir okla, uzayda <b>F</b>(<em>x</em>, <em>y</em>, "
    "<em>z</em>) vektörünü başlangıcı (<em>x</em>, <em>y</em>, <em>z</em>) olan bir okla çizeriz. "
    "Birkaç temsilci noktadaki oklar alanın genel görünüşünü verir.",
    css_class=WIDE,
    aria="Left: a few arrows in the plane, each starting at its base point; the highlighted arrow F(x, y) "
         "starts at the point (x, y). Right: the same picture in space with the arrow F(x, y, z) "
         "starting at (x, y, z)"))

# ============================================================
# donme: the twelve arrows of the table for F(x, y) = -y i + x j
# ============================================================
TABLE = [(1, 0), (2, 2), (3, 0), (0, 1), (-2, 2), (0, 3),
         (-1, 0), (-2, -2), (-3, 0), (0, -1), (2, -2), (0, -3)]


def ROT(x, y):
    return (-y, x)


p = eq_plot(40, 30, 40, (-4.7, 4.7), (-4.7, 4.7))
for rad in (1.0, 2.0 * math.sqrt(2.0), 3.0):
    p.circle(0, 0, rad, TEXT, 1.0, "4 4", "none", 0.45)
p.origin_axes(it("x"), it("y"), xticks=(-2, 2), yticks=(-2, 2),
              xfmt=lambda v: (MINUS if v < 0 else "") + f"{abs(v):g}",
              yfmt=lambda v: (MINUS if v < 0 else "") + f"{abs(v):g}")
for P0 in TABLE:
    vec2(p, P0, ROT(*P0), 1.0, THEORY, 1.9, 9.0)
    p.points([P0], PRACTICE, 3.2)
plabel(p, 1, 1, VF + "(1, 0)", 5, 10, THEORY, 11.5, "start")
plabel(p, 3, 3, VF + "(3, 0)", 8, 4, THEORY, 11.5, "start")
plabel(p, 0, 4, VF + "(2, 2)", -6, -8, THEORY, 11.5, "end")
plabel(p, -3, 3, VF + "(0, 3)", -4, -8, THEORY, 11.5, "end")
save("donme", figure(
    int(p.x0 + p.w + 40), int(p.y0 + p.h + 30), [p],
    "Tablodaki on iki vektör, başlangıçları kendi noktalarında olacak biçimde çizildi. Her ok, "
    "orijin merkezli bir çembere (kesikli) teğettir ve uzunluğu o çemberin yarıçapına eşittir; "
    "oklar saat yönünün tersine döner.",
    aria="Twelve arrows of the field F = -y i + x j at the points of the table, each tangent to a dashed "
         "circle centred at the origin, of radius 1, 2 sqrt 2 or 3, and as long as that radius"))

# ============================================================
# bilgisayar: three computer-style plots with scaled arrows
# ============================================================
PW = 186
panels = []
specs = [
    ("rot", 5.0, lambda x, y: (-y, x),
     VF + " = " + MINUS + it("y") + " " + bf("i") + " + " + it("x") + " " + bf("j")),
    ("ysin", 6.0, lambda x, y: (y, math.sin(x)),
     VF + " = " + it("y") + " " + bf("i") + " + sin " + it("x") + " " + bf("j")),
    ("ln", 5.0, lambda x, y: (math.log(1 + y * y), math.log(1 + x * x)),
     VF + " = ln(1 + " + it("y") + "²) " + bf("i") + " + ln(1 + " + it("x") + "²) " + bf("j")),
]
for k, (_, a, F, title) in enumerate(specs):
    x0 = 40 + k * (PW + 52)
    q = Plot(x0, 46, PW, PW, (-a * 1.2, a * 1.2), (-a * 1.2, a * 1.2))
    frame(q)
    cross_axes(q)
    n = 11
    grid = [-a + 2 * a * i / (n - 1) for i in range(n)]
    field_grid(q, F, grid, grid, 0.9, THEORY, 1.15, 5.5)
    frame_ticks(q, (-a, 0, a))
    q.text_px(q.x0 + q.w / 2, q.y0 - 12, title, TEXT, 11, "middle")
    panels.append(q)
save("bilgisayar", figure(
    int(panels[-1].x0 + PW + 40), int(46 + PW + 40), panels,
    "Bilgisayarla çizilmiş üç vektör alanı. Oklar aynı oranda kısaltıldı: birbirine çarpmazlar ama "
    "uzunlukları gerçek uzunluklarıyla orantılıdır. Soldaki alan dönme alanıdır.",
    css_class=WIDE,
    aria="Three square panels with arrows on an 11 by 11 grid, scaled by a common factor: the rotation "
         "field -y i + x j on [-5, 5]^2, the field y i + sin x j on [-6, 6]^2 and the field "
         "ln(1 + y^2) i + ln(1 + x^2) j on [-5, 5]^2"))

# ============================================================
# zk: F(x, y, z) = z k
# ============================================================
cam = Camera(azimuth=35.0, elevation=20.0)
COLS = [(1.0, 0.6), (1.0, 2.0), (1.0, 3.4), (2.6, 0.6), (2.6, 2.0), (2.6, 3.4)]
ZS = (-1.6, -0.8, 0.8, 1.6)
SZ = 0.55
pz, Sz = fit_space(cam, [(0, 0, -2.6), (0, 0, 2.7), (3.6, 0, 0), (0, 4.4, 0), (3.4, 4.0, 0),
                         (2.6, 3.4, 1.6 + SZ * 1.6), (1.0, 0.6, -1.6 - SZ * 1.6)], 40, 30, 62, 0.25)


def zk_arrow(xy, zz):
    vec3(Sz, (xy[0], xy[1], zz), (0, 0, zz), SZ, THEORY, 1.9, 8.0)
    Sz.point((xy[0], xy[1], zz), PRACTICE, 2.8)


# below the floor first, then the floor, then the axes and the upper arrows
Sz.line([(0, 0, -2.5), (0, 0, 0)], TEXT, 1.1, None, 0.55)
for xy in COLS:
    for zz in ZS:
        if zz < 0:
            zk_arrow(xy, zz)
Sz.polygon([(0, 0, 0), (3.4, 0, 0), (3.4, 4.0, 0), (0, 4.0, 0)], BASE, 0.10, BASE, 0.9)
Sz.floor_grid((0, 3.4), (0, 4.0), 4, 0.0, TEXT, 0.10)
Sz.axes(3.6, 4.4, 2.7)
Sz.label((0, 0, 0), "0", -7, 12, TEXT, 10.5, "end")
for xy in COLS:
    Sz.point((xy[0], xy[1], 0.0), PRACTICE, 2.8)
    for zz in ZS:
        if zz > 0:
            zk_arrow(xy, zz)
Sz.label((3.4, 4.0, 0), it("z") + " = 0", 8, 4, BASE, 11.5)
save("zk", figure(
    int(pz.x0 + pz.w + 40), int(pz.y0 + pz.h + 30), [pz],
    "<b>F</b>(<em>x</em>, <em>y</em>, <em>z</em>) = <em>z</em> <b>k</b>. Bütün oklar düşeydir: "
    "<em>xy</em>-düzleminin üstünde yukarı, altında aşağı bakar ve düzlemden uzaklaştıkça uzar. "
    "Düzlemin üzerindeki noktalarda vektör sıfırdır.",
    aria="Vertical arrows of the field z k at four heights over six points of the xy-plane: arrows above "
         "the shaded plane z = 0 point up, arrows below it point down, and both grow with the distance "
         "from the plane; on the plane the field is zero"))

# ============================================================
# cekim: the gravitational field -c x / |x|^3, arrows toward the origin
# ============================================================
cam = Camera(azimuth=35.0, elevation=20.0)
dirs = [(sx, sy, sz) for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1)]
dirs += [(sx, sy, 0) for sx in (-1, 1) for sy in (-1, 1)]
dirs += [(sx, 0, sz) for sx in (-1, 1) for sz in (-1, 1)]
dirs += [(0, sy, sz) for sy in (-1, 1) for sz in (-1, 1)]
dirs = [vscale(1.0 / vnorm(d), d) for d in dirs]
RADII = (1.2, 1.85, 2.7)
CG = 0.55 * RADII[0] ** 2          # arrow length c / r^2, 0.55 on the inner shell
AX = 3.2
pc, Sc = fit_space(cam, [(AX, 0, 0), (-AX, 0, 0), (0, AX, 0), (0, -AX, 0), (0, 0, AX), (0, 0, -AX)]
                   + [vscale(RADII[-1], d) for d in dirs], 40, 30, 58, 0.3)
items = []
for d in dirs:
    for rr in RADII:
        P0 = vscale(rr, d)
        items.append((Sc.depth(P0), P0, vscale(-CG / rr ** 2, d)))
# axes behind, arrows back to front, the mass M at the origin
Sc.line([(-AX, 0, 0), (0, 0, 0)], TEXT, 1.0, None, 0.4)
Sc.line([(0, -AX, 0), (0, 0, 0)], TEXT, 1.0, None, 0.4)
Sc.line([(0, 0, -AX), (0, 0, 0)], TEXT, 1.0, None, 0.4)
for dep, P0, V in sorted(items, key=lambda t: t[0]):
    vec3(Sc, P0, V, 1.0, THEORY, 1.5, 7.0)
Sc.axes(AX, AX, AX, opacity=0.55)
Sc.point((0, 0, 0), PRACTICE, 4.6)
splabel(Sc, (0, 0, 0), it("M"), 8, 17, PRACTICE, 12.5, "start", True)
save("cekim", figure(
    int(pc.x0 + pc.w + 40), int(pc.y0 + pc.h + 30), [pc],
    "Orijindeki <em>M</em> kütlesinin kütle çekim alanı. Oklar orijine yönelir; büyüklükleri uzaklığın "
    "karesiyle ters orantılı olduğundan orijine yaklaştıkça hızla uzar. Oklar orijin merkezli üç "
    "küre üzerindeki noktalardan çizildi.",
    aria="Arrows of the gravitational field at points of three spheres centred at the origin, all "
         "pointing toward the mass M at the origin; arrows on the inner sphere are much longer than "
         "those on the outer ones"))

# ============================================================
# gradyan: level curves of f = x^2 y - y^3 and the gradient field 2xy i + (x^2 - 3y^2) j
# ============================================================
def f6(x, y):
    return x * x * y - y ** 3


def g6(x, y):
    return (2 * x * y, x * x - 3 * y * y)


A6 = 4.5
p = eq_plot(40, 30, 40, (-A6, A6), (-A6, A6))
frame(p, TEXT, 0.4)
for c in range(6, 96, 6):            # equally spaced levels +-6, +-12, ..., +-90
    for lev in (c, -c):
        for line in contour(f6, (-A6, A6), (-A6, A6), lev, 200, 200):
            if len(line) > 2:
                p.line(rdp(line, 0.012), THEORY, 0.95, None, 0.75)
# the zero level set consists of the lines y = 0, y = x, y = -x
for (u, v) in ((1, 0), (1, 1), (1, -1)):
    p.line([(-A6 * u, -A6 * v), (A6 * u, A6 * v)], BASE, 1.3, None, 0.9)
grid6 = [-3.5 + i for i in range(8)]
field_grid(p, g6, grid6, grid6, 0.9, PRACTICE, 1.3, 6.0)
frame_ticks(p, (-4, 0, 4))
plabel(p, -A6, 0, it("f") + " = 0", 6, -7, BASE, 11, "start")
save("gradyan", figure(
    int(p.x0 + p.w + 40), int(p.y0 + p.h + 30), [p],
    "<em>f</em>(<em>x</em>, <em>y</em>) = <em>x</em>²<em>y</em> &#8722; <em>y</em>³ fonksiyonunun seviye "
    "eğrileri (mavi; ardışık seviyeler arasındaki fark 6'dır, <em>f</em> = 0 seviyesi üç doğrudur) ve "
    "gradyan vektör alanı (turuncu, oklar aynı oranda kısaltılmış). Oklar seviye eğrilerine diktir; "
    "eğrilerin sık olduğu yerde uzun, seyrek olduğu yerde kısadır.",
    aria="Contour map of f = x^2 y - y^3 on the square [-4.5, 4.5]^2 with the zero level set made of the "
         "lines y = 0, y = x and y = -x, and the scaled gradient vectors 2xy i + (x^2 - 3y^2) j on an 8 by 8 grid, "
         "perpendicular to the level curves and longest near the edges"))

# ============================================================
# akis: flow lines of F = y i + sin x j, i.e. the curves y^2 + 2 cos x = c
# ============================================================
def F7(x, y):
    return (y, math.sin(x))


def H7(x, y):
    return y * y + 2.0 * math.cos(x)


XR7, YR7 = (-6.8, 6.8), (-3.4, 3.4)
p = eq_plot(30, 20, 34, XR7, YR7)
gx = [-6.4 + 0.8 * i for i in range(17)]
gy = [-3.2 + 0.8 * i for i in range(9)]
field_grid(p, F7, gx, gy, 0.8, TEXT, 1.0, 5.0)
p.line([(XR7[0], 0), (XR7[1], 0)], TEXT, 1.0, None, 0.45)
p.line([(0, YR7[0]), (0, YR7[1])], TEXT, 1.0, None, 0.45)
for c in (-1.2, 0.4, 3.4, 5.6):
    for line in contour(H7, XR7, YR7, c, 340, 170):
        if len(line) > 12:
            p.line(rdp(line, 0.01), THEORY, 1.8)
            mid_arrow(p, line, F7, THEORY, 1.8, 8.0, 0.5)
# the separatrix c = 2, joining the equilibria (-2 pi, 0), (0, 0) and (2 pi, 0)
for line in contour(H7, XR7, YR7, 2.0, 340, 170):
    if len(line) > 12:
        p.line(rdp(line, 0.01), BASE, 1.6, "6 4")
for k in (-2, -1, 0, 1, 2):
    p.points([(k * math.pi, 0)], BASE, 3.0)
# a particle on the flow line c = 3.4 and its velocity F(P)
PX = 1.0
PY = math.sqrt(3.4 - 2.0 * math.cos(PX))
p.points([(PX, PY)], PRACTICE, 4.0)
vec2(p, (PX, PY), F7(PX, PY), 0.55, PRACTICE, 2.4, 9.0)
plabel(p, PX, PY, it("P"), -6, -8, PRACTICE, 12.5, "end", True)
TIPX, TIPY = PX + 0.55 * F7(PX, PY)[0], PY + 0.55 * F7(PX, PY)[1]
plabel(p, TIPX, TIPY, VF + "(" + it("P") + ")", 6, -6, PRACTICE, 12, "start", True)
plabel(p, XR7[1], 0, it("x"), -3, 15, TEXT, 11.5, "end")
plabel(p, 0, YR7[1], it("y"), 6, 11, TEXT, 11.5, "start")
save("akis", figure(
    int(p.x0 + p.w + 30), int(p.y0 + p.h + 30), [p],
    "<b>F</b>(<em>x</em>, <em>y</em>) = <em>y</em> <b>i</b> + sin <em>x</em> <b>j</b> alanı (ince oklar, "
    "kısaltılmış) ve birkaç akış çizgisi (mavi). Akış çizgisi üzerindeki bir <em>P</em> noktasında alanın "
    "vektörü <b>F</b>(<em>P</em>) eğriye teğettir ve parçacığın o andaki hızını verir. Yeşil noktalarda "
    "<b>F</b> = <b>0</b>'dır; kesikli eğriler, kapalı akış çizgilerini dalgalı olanlardan ayıran akış "
    "çizgileridir.",
    aria="Scaled arrows of the field y i + sin x j on [-6.4, 6.4] x [-3.2, 3.2] with several flow lines: "
         "closed loops around (pi, 0) and (-pi, 0), wavy curves above and below, dashed curves joining "
         "the zeros (-2 pi, 0), (0, 0) and (2 pi, 0) of the field; at a point P on an upper flow line the "
         "tangent arrow F(P)"))

# ============================================================
# ciz: exercise, F(x, y) = -1/2 i + (y - x) j on the integer grid of [-2, 2]^2
# ============================================================
def F5(x, y):
    return (-0.5, y - x)


p = eq_plot(40, 30, 60, (-2.9, 2.9), (-2.9, 2.9))
p.line([(-2.75, -2.75), (2.75, 2.75)], BASE, 1.4, "6 4", 0.9)
p.origin_axes(it("x"), it("y"))
for v in (-2, -1, 1, 2):
    # x ticks on the side the arrows leave free: above for x > 0, below for x < 0
    p.label(v, 0, signed(v), 9, -6 if v > 0 else 16, TEXT, 10.5, "start" if v > 0 else "middle")
    p.label(0, v, signed(v), 7, -5, TEXT, 10.5, "start")
S5 = 0.22
for xx in range(-2, 3):
    for yy in range(-2, 3):
        p.points([(xx, yy)], PRACTICE, 2.4)
        vec2(p, (xx, yy), F5(xx, yy), S5, THEORY, 1.7, 7.0)
plabel(p, 2.75, 2.75, it("y") + " = " + it("x"), -4, 16, BASE, 11.5, "end")
save("ciz", figure(
    int(p.x0 + p.w + 40), int(p.y0 + p.h + 30), [p],
    "<b>F</b>(<em>x</em>, <em>y</em>) = &#8722;½ <b>i</b> + (<em>y</em> &#8722; <em>x</em>) <b>j</b> "
    "alanının tam sayı koordinatlı noktalardaki vektörleri (hepsi aynı oranda kısaltılmış). Oklar "
    "<em>y</em> = <em>x</em> doğrusu üzerinde yatay ve sola doğrudur; doğrunun üstünde yukarı, altında "
    "aşağı eğilir ve doğrudan uzaklaştıkça uzar.",
    aria="Arrows of the field -1/2 i + (y - x) j at the 25 integer points of [-2, 2]^2, scaled by a common "
         "factor; on the dashed line y = x they are short and point left, above it they point up and "
         "left, below it down and left, and they grow with the distance from the line"))
