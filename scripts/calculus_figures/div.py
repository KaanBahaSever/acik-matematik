# -*- coding: utf-8 -*-
"""
Figures of the chapter "Diverjans Teoremi"
(dersler/integral-calculus/diverjans-teoremi.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box and never directly under a heading.
Concept figures stay visible: cisim in the statement part of the Divergence
Theorem, iki-yuzey in the statement part of the corollary on the region between
two closed surfaces, kaynak-kuyu and alistirma-alan under the question texts
that refer to them, parabolik under the question text of its example and ozet
in the plain text of the summary section. The proof figure tip-1 sits in the
proof block and gauss in the solution step it illustrates.
The figures are NOT produced at build time. Run

    python scripts/calculus_figures/div.py
    python scripts/center_figures.py "calculus-div-*.md"
    python scripts/check_figure_labels.py "scripts/_figures/calculus-div-*.md"

and paste the markup of scripts/_figures/calculus-div-<name>.md into the .qmd.
Captions are Turkish on purpose; aria labels are plain ASCII.
"""
import html
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, panel_title, blob, TEXT, THEORY, PRACTICE, BASE, BG, WIDE  # noqa: E402
from svg_plot3 import Camera, Space, vadd, vsub, vscale, vdot, vcross, vunit  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "calculus-div-"

MINUS = "&#8722;"
ZWSP = chr(0x200B)


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


def plate(p, px, py, s, size, anchor):
    """Page-coloured plate under a label that sits on a translucent face or on arrows."""
    w = text_w(s, size)
    x0 = px - (w / 2 if anchor == "middle" else w if anchor == "end" else 0)
    p.add(f'<rect x="{x0 - 3:.1f}" y="{py - 0.8 * size - 1.5:.1f}" width="{w + 6:.1f}" '
          f'height="{size + 4:.1f}" rx="3" fill="{BG}" opacity="0.85"/>')


def plabel(p, x, y, s, dx=0, dy=0, color=TEXT, size=12, anchor="start", bold=False):
    """Label at a data point of a 2-D panel, on a plate."""
    plate(p, p.X(x) + dx, p.Y(y) + dy, s, size, anchor)
    p.label(x, y, s, dx, dy, color, size, anchor, bold)


def slabel(S, P, s, dx=0, dy=0, color=TEXT, size=12, anchor="start", bold=False, plated=False):
    """Label at a space point, optionally on a plate."""
    X, Y = S.pt(P)
    if plated:
        plate(S.p, S.p.X(X) + dx, S.p.Y(Y) + dy, s, size, anchor)
    S.p.label(X, Y, s, dx, dy, color, size, anchor, bold)


def leader_px(p, px, py, dx, dy, s, color=TEXT, size=12, anchor="start", bold=False):
    """Label pushed (dx, dy) pixels away from the pixel point (px, py), with a thin leader line."""
    tx, ty = px + dx, py + dy
    w = text_w(s, size)
    lx = tx + (-w / 2 if anchor == "middle" else -w if anchor == "end" else 0)
    bx0, bx1, by0, by1 = lx - 3, lx + w + 3, ty - 0.95 * size, ty + 0.45 * size
    sx, sy = min(max(px, bx0), bx1), min(max(py, by0), by1)
    length = math.hypot(px - sx, py - sy)
    k = max(0.0, (length - 3.0) / length) if length > 0 else 0.0
    ex, ey = sx + (px - sx) * k, sy + (py - sy) * k
    p.add(f'<line x1="{sx:.1f}" y1="{sy:.1f}" x2="{ex:.1f}" y2="{ey:.1f}" stroke="{color}" '
          f'stroke-width="0.9" opacity="0.75"/>')
    p.text_px(tx, ty, s, color, size, anchor, bold)


def leader(S, P, dx, dy, s, color=TEXT, size=12, anchor="start", bold=False):
    """leader_px() at a space point."""
    X, Y = S.pt(P)
    leader_px(S.p, S.p.X(X), S.p.Y(Y), dx, dy, s, color, size, anchor, bold)


def leader2(p, P, dx, dy, s, color=TEXT, size=12, anchor="start", bold=False):
    """leader_px() at a data point of a 2-D panel."""
    leader_px(p, p.X(P[0]), p.Y(P[1]), dx, dy, s, color, size, anchor, bold)


def frange(a, b, n):
    return [a + (b - a) * k / n for k in range(n + 1)]


def split_runs(S, pts, visible, color=THEORY, width=1.8):
    """Draw a polyline in solid runs where visible(segment index) is true and dashed runs elsewhere."""
    run, state = [pts[0]], None
    for k in range(len(pts) - 1):
        v = visible(k)
        if state is not None and v != state:
            S.line(run, color, width, None, 1.0) if state else S.line(run, color, width * 0.6, "4 3", 0.6)
            run = [pts[k]]
        state = v
        run.append(pts[k + 1])
    S.line(run, color, width, None, 1.0) if state else S.line(run, color, width * 0.6, "4 3", 0.6)


def vec2(p, P0, V, s=1.0, color=THEORY, width=1.4, head=7.0, dot_r=1.3):
    """Arrow from P0 along s*V; the head shrinks on short arrows, a tiny vector becomes a dot."""
    P1 = (P0[0] + s * V[0], P0[1] + s * V[1])
    lpx = math.hypot(p.X(P1[0]) - p.X(P0[0]), p.Y(P1[1]) - p.Y(P0[1]))
    if lpx < 1.6:
        p.points([P0], color, dot_r)
        return
    p.arrow(P0, P1, color, width, min(head, 0.55 * lpx))


def field_grid(p, F, xs, ys, fill=0.9, color=THEORY, width=1.2, head=6.0):
    """Computer-style plot: arrows at the grid nodes, all shortened by one common factor."""
    vals = [((x, y), F(x, y)) for x in xs for y in ys]
    big = max(math.hypot(*v) for _, v in vals)
    step = min(xs[1] - xs[0], ys[1] - ys[0])
    s = fill * step / big
    for P0, V in vals:
        vec2(p, P0, V, s, color, width, head)
    return s


def frame(p, color=TEXT, opacity=0.35):
    """Rounded frame around a plotting panel."""
    p.add(f'<rect x="{p.x0:.1f}" y="{p.y0:.1f}" width="{p.w:.1f}" height="{p.h:.1f}" rx="7" '
          f'fill="none" stroke="{color}" stroke-width="1.1" opacity="{opacity}"/>')


def cross_axes(p, opacity=0.35):
    """Thin axes through the origin, clipped to the panel."""
    p.line([(p.xmin, 0), (p.xmax, 0)], TEXT, 0.9, None, opacity)
    p.line([(0, p.ymin), (0, p.ymax)], TEXT, 0.9, None, opacity)


def axis_ticks(p, a, size=10.5):
    """Tick marks and labels at x = -a, a and y = -a, a on the axes through the origin, on plates."""
    lab = lambda v: (MINUS if v < 0 else "") + f"{abs(v):g}"
    for v in (-a, a):
        p.add(f'<line x1="{p.X(v):.1f}" y1="{p.Y(0) - 4:.1f}" x2="{p.X(v):.1f}" y2="{p.Y(0) + 4:.1f}" '
              f'stroke="{TEXT}" stroke-width="1.1" opacity="0.6"/>')
        plabel(p, v, 0, lab(v), 0, 17, TEXT, size, "middle")
        p.add(f'<line x1="{p.X(0) - 4:.1f}" y1="{p.Y(v):.1f}" x2="{p.X(0) + 4:.1f}" y2="{p.Y(v):.1f}" '
              f'stroke="{TEXT}" stroke-width="1.1" opacity="0.6"/>')
        plabel(p, 0, v, lab(v), -8, 4, TEXT, size, "end")


def evenodd_ring(p, outer, inner, color=THEORY, opacity=0.14):
    """Shade the region between two closed polylines (data coordinates)."""
    def path(pts):
        return "M" + " L".join(p.P(x, y) for x, y in pts) + " Z"
    p.add(f'<path d="{path(outer)} {path(inner)}" fill="{color}" fill-opacity="{opacity}" '
          f'fill-rule="evenodd" stroke="none"/>')


def outward_normal(pts, k):
    """Outward unit normal of a counter-clockwise closed polyline at vertex k."""
    a, b = pts[k - 1], pts[(k + 1) % len(pts)]
    tx, ty = b[0] - a[0], b[1] - a[1]
    n = math.hypot(tx, ty)
    return (ty / n, -tx / n)


# ------------------------------------------------------------
# a smooth closed "rounded box" solid (superellipsoid)
# ------------------------------------------------------------
def spow(t, e):
    return math.copysign(abs(t) ** e, t)


def make_solid(A, B, C, e=0.55, center=(0.0, 0.0, 0.0)):
    """Parametrization (u, v) -> point of a superellipsoid, u = longitude, v = colatitude."""
    def f(u, v):
        x = A * spow(math.sin(v), e) * spow(math.cos(u), e)
        y = B * spow(math.sin(v), e) * spow(math.sin(u), e)
        z = C * spow(math.cos(v), e)
        return (center[0] + x, center[1] + y, center[2] + z)
    return f


def solid_normal(A, B, C, e, P, center=(0.0, 0.0, 0.0)):
    """Outward unit normal of |x/A|^p + |y/B|^p + |z/C|^p = 1, p = 2/e, at P."""
    p = 2.0 / e
    x, y, z = vsub(P, center)
    g = (spow(x / A, p - 1) / A, spow(y / B, p - 1) / B, spow(z / C, p - 1) / C)
    return vunit(g)


def draw_solid(S, f, normal, nu=40, nv=20, opacity=(0.06, 0.26)):
    """Shaded solid without a mesh; three parallels and four meridians, hidden halves dashed."""
    S.surface(f, (0.0, 2 * math.pi), (0.0, math.pi), nu=nu, nv=nv, fill=THEORY, stroke="none",
              opacity=opacity)
    curves = [[f(u, v) for u in frange(0.0, 2 * math.pi, 160)] for v in (0.55, math.pi / 2, math.pi - 0.55)]
    curves += [[f(u, v) for v in frange(0.02, math.pi - 0.02, 80)] for u in (0.0, math.pi / 2, math.pi, 1.5 * math.pi)]
    for c in curves:
        run, state = [c[0]], None
        for k in range(len(c) - 1):
            v = vdot(normal(c[k]), S.cam.d) > 0
            if state is not None and v != state:
                S.line(run, THEORY, 0.8, None if state else "3 3", 0.55 if state else 0.35)
                run = [c[k]]
            state = v
            run.append(c[k + 1])
        S.line(run, THEORY, 0.8, None if state else "3 3", 0.55 if state else 0.35)


def silhouette(S, f, n=360):
    """Approximate outline of the projected solid: convex hull of many projected surface points."""
    pts = []
    for i in range(48):
        for j in range(1, 24):
            pts.append(S.pt(f(2 * math.pi * i / 48, math.pi * j / 24)))
    pts.append(S.pt(f(0.0, 0.0)))
    pts.append(S.pt(f(0.0, math.pi)))
    pts = sorted(set(pts))

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lower, upper = [], []
    for q in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], q) <= 0:
            lower.pop()
        lower.append(q)
    for q in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], q) <= 0:
            upper.pop()
        upper.append(q)
    hull = lower[:-1] + upper[:-1]
    return hull + [hull[0]]


cam = Camera(azimuth=35.0, elevation=22.0)

# ============================================================
# cisim: a solid E, its closed boundary S and outward unit normals
# ============================================================
SA, SB, SC, SE = 1.45, 1.95, 1.0, 0.55
fS = make_solid(SA, SB, SC, SE)
NL = 0.75                                       # arrow length of the normals
spots = [(0.0, 0.0), (math.radians(118), math.radians(78)), (math.radians(-52), math.radians(84)),
         (0.0, math.pi), (math.radians(60), math.radians(118))]
bases = [fS(u, v) for u, v in spots]
tips = [vadd(P, vscale(NL, solid_normal(SA, SB, SC, SE, P))) for P in bases]
ext = [fS(2 * math.pi * i / 24, math.pi * j / 12) for i in range(24) for j in range(13)] + tips
pc, Sc = fit_space(cam, ext, 30, 30, 92, 0.3)
draw_solid(Sc, fS, lambda P: solid_normal(SA, SB, SC, SE, P))
hull = silhouette(Sc, fS)
pc.line(hull, THEORY, 1.6)
for P, T in zip(bases, tips):
    front = vdot(solid_normal(SA, SB, SC, SE, P), cam.d) > -0.05
    Sc.point(P, PRACTICE, 2.6)
    Sc.arrow(P, T, PRACTICE, 1.9 if front else 1.4, 8.0, None if front else "4 3", 1.0 if front else 0.75)
lab_off = [(8, -2), (10, 4), (-8, 4), (8, 6), (8, 10)]
for (dx, dy), T in zip(lab_off, tips):
    anc = "end" if dx < 0 else "start"
    slabel(Sc, T, bf("n"), dx, dy, PRACTICE, 13, anc)
slabel(Sc, (0.0, -0.15, 0.0), it("E"), 0, 6, THEORY, 16, "middle", True, True)
slabel(Sc, fS(math.radians(150), math.radians(30)), it("S"), 6, -10, THEORY, 15, "start", True, True)
save("cisim", figure(
    int(pc.x0 + pc.w + 30), int(pc.y0 + pc.h + 30), [pc],
    "Basit katı bölge <em>E</em> ve onu çevreleyen kapalı <em>S</em> yüzeyi. Pozitif yönde birim normal "
    "<b>n</b> her noktada <em>E</em>'nin dışına bakar (kesikli ok, görünmeyen alt yüzdeki normaldir). Diverjans Teoremi, "
    "<b>F</b>'nin <em>S</em>'den dışarı akısını div <b>F</b>'nin <em>E</em> üzerindeki integraline eşitler.",
    aria="A rounded closed solid E bounded by the surface S, with unit normal arrows n at six points of S, "
         "all pointing out of E: up at the top, down at the bottom and sideways on the sides"))


# ============================================================
# tip-1: the solid as a type 1 region; bottom S1, top S2, vertical side S3, projection D
# ============================================================
CA, CB, R0 = 1.5, 2.0, 0.85
LO, HI = 1.0, 2.5


def br(t):
    return R0 * (1 + 0.10 * math.cos(2 * t) + 0.06 * math.sin(3 * t))


def bpt(t, s=1.0):
    rr = s * br(t)
    return CA + rr * math.cos(t), CB + rr * math.sin(t)


def u1(x, y):
    return LO + 0.14 * math.sin(2.0 * (x - CA)) + 0.10 * math.cos(2.2 * (y - CB))


def u2(x, y):
    return HI + 0.18 * math.cos(1.8 * (x - CA)) - 0.16 * math.sin(1.7 * (y - CB))


def wall_front(t):
    h = 1e-4
    a0, b0 = bpt(t - h)
    a1, b1 = bpt(t + h)
    n = (b1 - b0, -(a1 - a0), 0.0)
    return vdot(n, cam.d) > 0


# the panel sits in the 24rem column, so the axes stay short and the labels are set large
ext = [(0, 0, 0), (3.0, 0, 0), (0, 3.8, 0), (0, 0, 3.3)]
ext += [(CA + dx, CB + dy, c) for dx in (-1.0, 1.0) for dy in (-1.0, 1.0) for c in (0.0, HI + 0.3)]
pt1, S1 = fit_space(cam, ext, 30, 30, 92, 0.25)
S1.axes(3.0, 3.8, 3.3, size=14, offsets=((-5, 15), (11, 5), (-11, -4)))
S1.label((0, 0, 0), "0", -7, 13, TEXT, 12, "end")
ts = frange(0.0, 2 * math.pi, 140)
floor = [(*bpt(t), 0.0) for t in ts]
S1.polygon(floor, BASE, 0.22, BASE, 1.4)
sil = [ts[k] for k in range(len(ts) - 1) if wall_front(ts[k]) != wall_front(ts[k + 1])]
for t in sil:
    a, b = bpt(t)
    S1.guide([(a, b, u1(a, b)), (a, b, 0.0)], TEXT, 0.5)
tc = frange(0.0, 2 * math.pi, 90)
# bottom cap S1, wall S3, top cap S2
S1.polygon([(*bpt(t), u1(*bpt(t))) for t in tc], THEORY, 0.10)
S1.surface(lambda v, t: (*bpt(t), u1(*bpt(t)) + v * (u2(*bpt(t)) - u1(*bpt(t)))), (0.0, 1.0),
           (0.0, 2 * math.pi), nu=1, nv=40, fill=THEORY, stroke="none", opacity=(0.07, 0.22))
S1.polygon([(*bpt(t), u2(*bpt(t))) for t in tc], THEORY, 0.20)
S1.line([(*bpt(t), u2(*bpt(t))) for t in ts], THEORY, 1.8)
split_runs(S1, [(*bpt(t), u1(*bpt(t))) for t in ts], lambda k: wall_front(0.5 * (ts[k] + ts[k + 1])))
for t in sil:
    a, b = bpt(t)
    S1.line([(a, b, u1(a, b)), (a, b, u2(a, b))], THEORY, 1.8)


def grad(u, x, y, h=1e-5):
    return ((u(x + h, y) - u(x - h, y)) / (2 * h), (u(x, y + h) - u(x, y - h)) / (2 * h))


# normal on the top S2
xa, ya = bpt(2.2, 0.35)
gx, gy = grad(u2, xa, ya)
P2 = (xa, ya, u2(xa, ya))
S1.point(P2, PRACTICE, 2.6)
S1.arrow(P2, vadd(P2, vscale(0.8, vunit((-gx, -gy, 1.0)))), PRACTICE, 1.9, 8.0)
slabel(S1, vadd(P2, vscale(0.8, vunit((-gx, -gy, 1.0)))), bf("n"), 7, 2, PRACTICE, 15)
# normal on the bottom S1 (front part)
xb, yb = bpt(0.35, 0.55)
gx, gy = grad(u1, xb, yb)
P1 = (xb, yb, u1(xb, yb))
S1.point(P1, PRACTICE, 2.6)
T1 = vadd(P1, vscale(0.62, vunit((gx, gy, -1.0))))
S1.arrow(P1, T1, PRACTICE, 1.9, 8.0)
slabel(S1, T1, bf("n"), 9, -5, PRACTICE, 15)
# normal on the wall S3
tw = 1.05
xw, yw = bpt(tw)
h = 1e-4
a0, b0 = bpt(tw - h)
a1, b1 = bpt(tw + h)
nw = vunit((b1 - b0, -(a1 - a0), 0.0))
P3 = (xw, yw, 0.5 * (u1(xw, yw) + u2(xw, yw)))
S1.point(P3, PRACTICE, 2.6)
T3 = vadd(P3, vscale(0.7, nw))
S1.arrow(P3, T3, PRACTICE, 1.9, 8.0)
slabel(S1, T3, bf("n"), 8, 5, PRACTICE, 15)
# labels
a, b = bpt(0.0, 0.0)
slabel(S1, (a, b, 0.0), it("D"), 0, 6, BASE, 16, "middle", True, True)
slabel(S1, (a - 0.15, b - 0.25, 0.5 * (u1(a, b) + u2(a, b))), it("E"), 0, 6, THEORY, 16, "middle", True, True)
ta, tb = bpt(4.0)
leader(S1, (ta, tb, u2(ta, tb)), 4, -50,
       it("S") + sub("2", 10.5) + ": " + it("z") + " = " + it("u") + sub("2", 10.5) + "(" + it("x") + ", " + it("y")
       + ")", THEORY, 14, "middle")
ta, tb = bpt(-0.75)
leader(S1, (ta, tb, u1(ta, tb)), -30, -36,
       it("S") + sub("1", 10.5) + ": " + it("z") + " = " + it("u") + sub("1", 10.5) + "(" + it("x") + ", " + it("y")
       + ")", THEORY, 14, "end")
ta, tb = bpt(-1.25)
leader(S1, (ta, tb, 0.5 * (u1(ta, tb) + u2(ta, tb)) + 0.25), -46, -8, it("S") + sub("3", 10.5), THEORY, 14, "end")
save("tip-1", figure(
    int(pt1.x0 + pt1.w + 30), int(pt1.y0 + pt1.h + 30), [pt1],
    "<em>E</em>'ye tip 1 bölge olarak bakmak. Sınır üç parçadır: alttaki <em>S</em><sub>1</sub>, üstteki "
    "<em>S</em><sub>2</sub> ve <em>D</em>'nin sınırı üzerinde yükselen düşey <em>S</em><sub>3</sub>. "
    "Dış normal <em>S</em><sub>2</sub>'de yukarı, <em>S</em><sub>1</sub>'de aşağı bakar; "
    "<em>S</em><sub>3</sub>'te yataydır, bu yüzden orada <b>k</b> &#183; <b>n</b> = 0 olur.",
    aria="A solid E over a region D of the xy plane: the lower boundary surface S1 z = u1(x, y), the upper "
         "surface S2 z = u2(x, y) and the vertical side S3 over the boundary of D; outward normals point up "
         "on S2, down on S1 and horizontally on S3"))


# ============================================================
# parabolik: the solid of the example, bounded by z = 1 - x^2, z = 0, y = 0 and y + z = 2
# ============================================================
cam2 = Camera(azimuth=32.0, elevation=20.0)
ext = [(0, 0, 0), (2.0, 0, 0), (-1.3, 0, 0), (0, 2.9, 0), (0, 0, 1.6), (1, 2, 0), (-1, 2, 0)]
pp, Sp = fit_space(cam2, ext, 30, 30, 125, 0.3)
# hidden axis parts first
Sp.line([(-1.3, 0, 0), (0, 0, 0)], TEXT, 1.0, "4 3", 0.45)
# back face y = 0 and bottom face z = 0
xs_ = frange(-1.0, 1.0, 60)
Sp.polygon([(x, 0.0, 1 - x * x) for x in xs_], THEORY, 0.10)
Sp.polygon([(-1, 0, 0), (1, 0, 0), (1, 2, 0), (-1, 2, 0)], BASE, 0.14)
# hidden edges: x = -1 on the floor
Sp.line([(-1, 0, 0), (-1, 2, 0)], THEORY, 1.0, "4 3", 0.6)
# slanted face y = 2 - z and the parabolic roof z = 1 - x^2
Sp.surface(lambda x, s: (x, 2 - s * (1 - x * x), s * (1 - x * x)), (-1.0, 1.0), (0.0, 1.0), nu=16, nv=3,
           fill=THEORY, stroke=THEORY, opacity=(0.08, 0.22), stroke_width=0.4, stroke_opacity=0.18)
Sp.surface(lambda x, s: (x, s * (1 + x * x), 1 - x * x), (-1.0, 1.0), (0.0, 1.0), nu=16, nv=4,
           fill=THEORY, stroke=THEORY, opacity=(0.10, 0.28), stroke_width=0.4, stroke_opacity=0.18)
# edges
Sp.line([(x, 0.0, 1 - x * x) for x in xs_], THEORY, 1.8)
Sp.line([(x, 1 + x * x, 1 - x * x) for x in xs_], THEORY, 1.8)
Sp.line([(1, 0, 0), (1, 2, 0)], THEORY, 1.8)
Sp.line([(-1, 2, 0), (1, 2, 0)], THEORY, 1.8)
Sp.line([(-1, 0, 0), (1, 0, 0)], THEORY, 1.0, "4 3", 0.6)
# visible axes
Sp.arrow((0, 0, 0), (2.0, 0, 0), TEXT, 1.1, 7.0, None, 0.55)
Sp.line([(0, 0, 0), (0, 2.0, 0)], TEXT, 1.0, "4 3", 0.45)
Sp.arrow((0, 2.0, 0), (0, 2.9, 0), TEXT, 1.1, 7.0, None, 0.55)
Sp.line([(0, 0, 0), (0, 0, 1.0)], TEXT, 1.0, "4 3", 0.45)
Sp.arrow((0, 0, 1.0), (0, 0, 1.6), TEXT, 1.1, 7.0, None, 0.55)
Sp.label((2.0, 0, 0), it("x"), -4, 14, TEXT, 12, "middle")
Sp.label((0, 2.9, 0), it("y"), 10, 5, TEXT, 12, "middle")
Sp.label((0, 0, 1.6), it("z"), -10, -2, TEXT, 12, "middle")
for P, s_, dx, dy, anc in (((0, 0, 1), "(0, 0, 1)", -10, -6, "end"), ((1, 0, 0), "(1, 0, 0)", -10, 12, "end"),
                           ((0, 2, 0), "(0, 2, 0)", 8, 16, "start")):
    Sp.point(P, PRACTICE, 3.0)
    slabel(Sp, P, s_, dx, dy, TEXT, 11.5, anc, False, True)
leader(Sp, (0.2, 0.45, 1 - 0.2 ** 2), 40, -62, it("z") + " = 1 " + MINUS + " " + it("x") + sup("2"), THEORY, 12, "start")
leader(Sp, (-0.3, 2 - 0.45 * (1 - 0.3 ** 2), 0.45 * (1 - 0.3 ** 2)), 120, -40,
       it("y") + " + " + it("z") + " = 2", THEORY, 12, "start")
save("parabolik", figure(
    int(pp.x0 + pp.w + 30), int(pp.y0 + pp.h + 30), [pp],
    "<em>E</em> cismi: üstten <em>z</em> = 1 &#8722; <em>x</em>² parabolik silindiri, alttan <em>z</em> = 0, "
    "arkadan <em>y</em> = 0 ve sağdan <em>y</em> + <em>z</em> = 2 düzlemiyle sınırlıdır. Yüzeyi dört "
    "parçadan oluşur.",
    aria="The solid bounded above by the parabolic cylinder z = 1 - x^2, below by the plane z = 0, behind by the "
         "plane y = 0 and on the right by the slanted plane y + z = 2; corner points (0, 0, 1), (1, 0, 0), "
         "(-1, 0, 0) and (0, 2, 0)"))


# ============================================================
# iki-yuzey: cross-section of the region between two closed surfaces
# ============================================================
pi2 = eq_plot(30, 30, 64, (-3.0, 3.1), (-2.7, 2.9))
outer = blob(0.0, 0.1, 2.35, [(0.22, 2, 0.4), (0.12, 3, 1.1)], 220)
inner = blob(-0.25, 0.15, 0.95, [(0.10, 2, 1.3), (0.05, 3, 0.2)], 160)
evenodd_ring(pi2, outer, inner, THEORY, 0.16)
pi2.line(outer + [outer[0]], THEORY, 1.9)
pi2.line(inner + [inner[0]], PRACTICE, 1.9)
# n2 on the outer surface
k2 = int(0.12 * len(outer))
Q2 = outer[k2]
n2 = outward_normal(outer, k2)
pi2.points([Q2], THEORY, 2.8)
pi2.arrow(Q2, (Q2[0] + 0.7 * n2[0], Q2[1] + 0.7 * n2[1]), THEORY, 1.9, 8.0)
pi2.label(Q2[0] + 0.7 * n2[0], Q2[1] + 0.7 * n2[1], bf("n") + sub("2"), 6, 2, THEORY, 13)
# n1 and -n1 at the top of the inner surface
k1 = int(0.25 * len(inner))
Q1 = inner[k1]
n1 = outward_normal(inner, k1)
pi2.points([Q1], PRACTICE, 2.8)
pi2.arrow(Q1, (Q1[0] + 0.65 * n1[0], Q1[1] + 0.65 * n1[1]), PRACTICE, 1.4, 7.0, "4 3", 0.75)
pi2.label(Q1[0] + 0.65 * n1[0], Q1[1] + 0.65 * n1[1], bf("n") + sub("1"), 7, 0, PRACTICE, 13)
pi2.arrow(Q1, (Q1[0] - 0.65 * n1[0], Q1[1] - 0.65 * n1[1]), PRACTICE, 2.0, 8.0)
pi2.label(Q1[0] - 0.65 * n1[0], Q1[1] - 0.65 * n1[1], MINUS + bf("n") + sub("1"), 7, 10, PRACTICE, 13)
# labels
plabel(pi2, 1.15, -1.0, it("E"), 0, 5, THEORY, 16, "middle", True)
k = int(0.62 * len(outer))
leader2(pi2, outer[k], -18, 24, it("S") + sub("2"), THEORY, 13, "end", True)
k = int(0.70 * len(inner))
leader2(pi2, inner[k], 30, 30, it("S") + sub("1"), PRACTICE, 13, "start", True)
save("iki-yuzey", figure(
    int(pi2.x0 + pi2.w + 30), int(pi2.y0 + pi2.h + 30), [pi2],
    "Kesit görünüşü: <em>E</em>, içteki <em>S</em><sub>1</sub> ile dıştaki <em>S</em><sub>2</sub> kapalı "
    "yüzeyleri arasında kalır. <em>E</em>'nin dış normali <em>S</em><sub>2</sub> üzerinde <b>n</b><sub>2</sub>'dir; "
    "<em>S</em><sub>1</sub> üzerinde ise deliğin içine, yani &#8722;<b>n</b><sub>1</sub> yönüne bakar "
    "(kesikli ok, <em>S</em><sub>1</sub>'in kendi dış normali <b>n</b><sub>1</sub>'dir).",
    aria="Cross-section of a region E between an inner closed surface S1 and an outer closed surface S2; the "
         "outward normal n2 on S2 points away from E, while on S1 the outward normal of E is -n1, pointing into "
         "the hole, opposite to the dashed outward normal n1 of S1"))


# ============================================================
# gauss: an arbitrary closed surface S around the charge, the small sphere S1 and the field
# ============================================================
pg = eq_plot(30, 30, 62, (-2.9, 3.4), (-2.6, 2.8))
Sg = blob(0.3, 0.1, 2.25, [(0.25, 2, 2.0), (0.15, 3, 0.4), (0.07, 5, 1.0)], 240)
A_SM = 0.62
ring = [(A_SM * math.cos(2 * math.pi * k / 160), A_SM * math.sin(2 * math.pi * k / 160)) for k in range(160)]
evenodd_ring(pg, Sg, ring, THEORY, 0.13)
pg.line(Sg + [Sg[0]], THEORY, 1.9)
pg.line(ring + [ring[0]], PRACTICE, 1.8)
# radial field arrows, length ~ 1/r^2
for k in range(8):
    a = 2 * math.pi * k / 8 + math.pi / 8
    for r, L in ((0.82, 0.62), (1.62, 0.62 * (0.82 / 1.62) ** 2 * 1.6)):
        P0 = (r * math.cos(a), r * math.sin(a))
        vec2(pg, P0, (math.cos(a), math.sin(a)), L, BASE, 1.5, 7.0)
pg.points([(0, 0)], PRACTICE, 3.6)
pg.label(0, 0, it("Q"), -6, -6, PRACTICE, 12, "end", True)
pg.line([(0, 0), (A_SM * math.cos(-0.55), A_SM * math.sin(-0.55))], TEXT, 1.1, None, 0.8)
pg.label(0.5 * A_SM * math.cos(-0.55), 0.5 * A_SM * math.sin(-0.55), it("a"), 2, 14, TEXT, 12, "middle")
plabel(pg, -0.98, -0.98, it("G"), 0, 5, THEORY, 15, "middle", True)
k = int(0.40 * len(Sg))
leader2(pg, Sg[k], -14, -22, it("S"), THEORY, 14, "end", True)
leader2(pg, (A_SM * math.cos(0.08), A_SM * math.sin(0.08)), 66, 2, it("S") + sub("1"), PRACTICE, 13, "start", True)
save("gauss", figure(
    int(pg.x0 + pg.w + 30), int(pg.y0 + pg.h + 30), [pg],
    "Kesit görünüşü: <em>Q</em> yükü orijinde, <em>S</em> onu içine alan herhangi bir kapalı yüzey, "
    "<em>S</em><sub>1</sub> ise orijin merkezli küçük <em>a</em> yarıçaplı küredir. <b>E</b> alanı (oklar) "
    "orijinde tanımsızdır ama aradaki <em>G</em> bölgesinde div <b>E</b> = 0 olduğundan iki yüzeyin akısı "
    "eşittir.",
    aria="Cross-section: a charge Q at the origin, a small circle S1 of radius a around it, an irregular closed "
         "curve S enclosing both, the region G between them shaded, and radial field arrows that get shorter "
         "with the distance from the charge"))


# ============================================================
# kaynak-kuyu: the field x^2 i + y^2 j with a source P1 and a sink P2
# ============================================================
A2 = 2.0
PPU = 66
# the arrows point up and to the right, so the panel leaves room on those sides
pk = eq_plot(40, 30, PPU, (-2.3, 2.62), (-2.3, 2.62))
frame(pk)
cross_axes(pk)
pk.line([(-2.3, 2.3), (2.3, -2.3)], TEXT, 1.2, "6 4", 0.6)
grid = frange(-A2, A2, 8)
field_grid(pk, lambda x, y: (x * x, y * y), grid, grid, 0.9, THEORY, 1.2, 6.0)
axis_ticks(pk, A2)
for P, s_, dx, dy in (((1.0, 1.0), it("P") + sub("1"), 9, 17), ((-1.0, -1.0), it("P") + sub("2"), 9, 17)):
    pk.points([P], PRACTICE, 4.0)
    plabel(pk, P[0], P[1], s_, dx, dy, PRACTICE, 13, "start", True)
pk.label(1.6, 2.62, "div " + bf("F") + " &gt; 0", 0, -9, TEXT, 12, "middle")
pk.label(-1.4, -2.3, "div " + bf("F") + " &lt; 0", 0, 19, TEXT, 12, "middle")
pk.label(2.3, -2.3, it("y") + " = " + MINUS + it("x"), 8, 19, TEXT, 12, "start")
save("kaynak-kuyu", figure(
    int(pk.x0 + pk.w + 40), int(pk.y0 + pk.h + 34), [pk],
    "<b>F</b>(<em>x</em>, <em>y</em>) = <em>x</em>² <b>i</b> + <em>y</em>² <b>j</b> alanı (oklar aynı oranda "
    "kısaltıldı). <em>P</em><sub>1</sub>(1, 1)'in çevresinden çıkan oklar girenlerden uzun, "
    "<em>P</em><sub>2</sub>(&#8722;1, &#8722;1)'in çevresinde ise kısadır. Kesikli <em>y</em> = &#8722;<em>x</em> "
    "doğrusunun üstünde div <b>F</b> &gt; 0, altında div <b>F</b> &lt; 0'dır.",
    aria="Arrow plot of the field x^2 i + y^2 j on the square from -2 to 2, all arrows pointing up and to the "
         "right and growing away from the axes; the source P1 = (1, 1) above and the sink P2 = (-1, -1) below "
         "the dashed line y = -x"))


# ============================================================
# alistirma-alan: the field x i + y^2 j of the exercise with the points P1 and P2
# ============================================================
# the arrows point up everywhere and away from the y axis sideways
pa = eq_plot(40, 30, PPU, (-2.62, 2.62), (-2.3, 2.62))
frame(pa)
cross_axes(pa)
field_grid(pa, lambda x, y: (x, y * y), grid, grid, 0.9, THEORY, 1.2, 6.0)
axis_ticks(pa, A2)
for P, s_, dx, dy in (((-1.0, 1.0), it("P") + sub("1"), 10, 18), ((-1.0, -1.0), it("P") + sub("2"), 10, 18)):
    pa.points([P], PRACTICE, 4.0)
    plabel(pa, P[0], P[1], s_, dx, dy, PRACTICE, 13, "start", True)
save("alistirma-alan", figure(
    int(pa.x0 + pa.w + 40), int(pa.y0 + pa.h + 34), [pa],
    "<b>F</b>(<em>x</em>, <em>y</em>) = <em>x</em> <b>i</b> + <em>y</em>² <b>j</b> alanı (oklar aynı oranda "
    "kısaltıldı) ve <em>P</em><sub>1</sub>(&#8722;1, 1), <em>P</em><sub>2</sub>(&#8722;1, &#8722;1) noktaları.",
    aria="Arrow plot of the field x i + y^2 j on the square from -2 to 2; all arrows point upward, their vertical "
         "part grows away from the x axis and their horizontal part points away from the y axis; the points "
         "P1 = (-1, 1) and P2 = (-1, -1) are marked"))


# ============================================================
# ozet: interval/curve and endpoints, surface and boundary curve, solid and boundary surface
# ============================================================
# panel 1: [a, b] and a curve C from r(a) to r(b)
po = eq_plot(20, 40, 56, (-0.4, 3.1), (-0.25, 2.7))
po.line([(0.1, 2.2), (2.6, 2.2)], BASE, 1.9)
po.points([(0.1, 2.2), (2.6, 2.2)], PRACTICE, 3.6)
po.label(0.1, 2.2, it("a"), 0, 18, TEXT, 12.5, "middle")
po.label(2.6, 2.2, it("b"), 0, 18, TEXT, 12.5, "middle")


def ccurve(t):
    return (0.15 + 2.4 * t, 0.55 + 0.55 * math.sin(2.6 * t + 0.3) * (1 - 0.3 * t) + 0.35 * t)


cpts = [ccurve(k / 120) for k in range(121)]
po.line(cpts, THEORY, 1.9)
po.arrow(cpts[58], cpts[64], THEORY, 1.9, 8.0)
po.points([cpts[0], cpts[-1]], PRACTICE, 3.6)
po.label(*cpts[0], bf("r") + "(" + it("a") + ")", 0, 20, TEXT, 12, "middle")
po.label(*cpts[-1], bf("r") + "(" + it("b") + ")", 0, -10, TEXT, 12, "middle")
po.label(*cpts[90], it("C"), 2, 18, THEORY, 13, "middle", True)

# panel 2: a cap-like surface S with boundary curve C and a normal n


def capf(r, t):
    x, y = 0.95 * r * math.cos(t), 1.2 * r * math.sin(t)
    return (x, y, 0.8 * (1 - r * r) + 0.10 * r * math.sin(3 * t))


cam3 = Camera(azimuth=35.0, elevation=32.0)
ext = [capf(1.0, t) for t in frange(0, 2 * math.pi, 48)] + [(0, 0, 0.8 + 0.7)]
pm, Sm = fit_space(cam3, ext, po.x0 + po.w + 30, 40, 72, 0.3)
Sm.surface(capf, (0.0, 1.0), (0.0, 2 * math.pi), nu=5, nv=24, fill=THEORY, stroke=THEORY,
           opacity=(0.08, 0.28), stroke_width=0.4, stroke_opacity=0.15)
ts2 = frange(0.0, 2 * math.pi, 180)
bd = [capf(1.0, t) for t in ts2]
# the part of the rim behind the dome is dashed
split_runs(Sm, bd, lambda k: vdot((math.cos(ts2[k]) / 0.95, math.sin(ts2[k]) / 1.2, 0.0), cam3.d) > -0.15,
           PRACTICE, 1.9)
Sm.arrow(bd[14], bd[20], PRACTICE, 1.9, 8.0)
Pn = capf(0.0, 0.0)
Sm.point(Pn, PRACTICE, 2.6)
Sm.arrow(Pn, vadd(Pn, (0, 0, 0.7)), PRACTICE, 1.9, 8.0)
slabel(Sm, vadd(Pn, (0, 0, 0.7)), bf("n"), 8, 4, PRACTICE, 13)
slabel(Sm, capf(0.55, 2.6), it("S"), 0, 5, THEORY, 14, "middle", True, True)
slabel(Sm, bd[32], it("C"), 8, 14, PRACTICE, 13, "start", True)

# panel 3: a solid E with boundary S and outward normals
fO = make_solid(1.0, 1.35, 0.7, 0.55)
spots3 = [(0.0, 0.0), (math.radians(118), math.radians(85)), (math.radians(-52), math.radians(88)), (0.0, math.pi)]
b3 = [fO(u, v) for u, v in spots3]
t3 = [vadd(P, vscale(0.55, solid_normal(1.0, 1.35, 0.7, 0.55, P))) for P in b3]
ext = [fO(2 * math.pi * i / 24, math.pi * j / 12) for i in range(24) for j in range(13)] + t3
pe, Se = fit_space(cam, ext, pm.x0 + pm.w + 30, 40, 66, 0.3)
draw_solid(Se, fO, lambda P: solid_normal(1.0, 1.35, 0.7, 0.55, P), 32, 16)
Se.p.line(silhouette(Se, fO), THEORY, 1.5)
for P, T in zip(b3, t3):
    front = vdot(solid_normal(1.0, 1.35, 0.7, 0.55, P), cam.d) > -0.05
    Se.point(P, PRACTICE, 2.4)
    Se.arrow(P, T, PRACTICE, 1.8 if front else 1.3, 7.5, None if front else "4 3", 1.0 if front else 0.75)
slabel(Se, t3[0], bf("n"), 7, 4, PRACTICE, 13)
slabel(Se, t3[1], bf("n"), 2, 16, PRACTICE, 13)
slabel(Se, (0.0, -0.1, 0.0), it("E"), 0, 6, THEORY, 15, "middle", True, True)
slabel(Se, fO(math.radians(150), math.radians(32)), it("S"), 6, -8, THEORY, 14, "start", True, True)

YT = max(q.y0 + q.h for q in (po, pm, pe)) + 18
for q, s in ((po, "Eğri ve uç noktaları"), (pm, "Yüzey ve sınır eğrisi"), (pe, "Cisim ve sınır yüzeyi")):
    q.text_px(q.x0 + q.w / 2, YT, s, TEXT, 12.5, "middle", True)
save("ozet", figure(
    int(pe.x0 + pe.w + 24), int(YT + 24), [po, pm, pe],
    "Temel teoremlerin ortak yapısı. Solda bir aralık ve bir eğri ile uç noktaları (analizin temel teoremi, "
    "eğrisel integraller için temel teorem), ortada bir yüzey ve sınır eğrisi (Green ve Stokes teoremleri), "
    "sağda bir cisim ve sınır yüzeyi (Diverjans Teoremi). Her teorem, bölge üzerindeki bir türevin integralini "
    "yalnız sınırdaki değerlere bağlar.",
    css_class=WIDE,
    aria="Three panels: an interval [a, b] and a curve C from r(a) to r(b); a surface S with its oriented boundary "
         "curve C and a normal n; a solid E with its closed boundary surface S and outward normals n"))
