# -*- coding: utf-8 -*-
"""
Figures of the chapter "Üç Katlı İntegraller"
(dersler/integral-calculus/uc-katli-integraller.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box and never directly under a heading.
Concept figures stay visible: under a definition box, in the statement part of
a theorem or example, or in plain text. The figures are NOT produced at build
time. Run

    python scripts/calculus_figures/uki.py
    python scripts/center_figures.py "calculus-uki-*.md"
    python scripts/check_figure_labels.py "scripts/_figures/calculus-uki-*.md"

and paste the markup of scripts/_figures/calculus-uki-<name>.md into the .qmd.
Captions are Turkish on purpose; aria labels are plain ASCII.

All solids are drawn with translucent faces. Edges that the solid itself hides
are dashed; which faces are hidden is decided from the camera direction.
"""
import html
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, dot, TEXT, THEORY, PRACTICE, BASE, BG, WIDE  # noqa: E402
from svg_plot3 import Camera, Space, vadd, vsub, vscale, vdot  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "calculus-uki-"

MINUS = "&#8722;"
ZWSP = chr(0x200B)
LE = "&#8804;"


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


def text_w(s, size):
    """Rough advance width of a label (0.5 em per visible character)."""
    def count(t):
        return len(html.unescape(re.sub(r"<[^>]+>", "", t)).replace(ZWSP, ""))
    width = 0.0
    for m in re.finditer(r'<tspan font-size="([\d.]+)"[^>]*>(.*?)</tspan>', s):
        width += count(m.group(2)) * 0.5 * float(m.group(1))
    rest = re.sub(r'<tspan font-size="[\d.]+"[^>]*>.*?</tspan>', "", s)
    return width + count(rest) * 0.5 * size


def plate(p, px, py, s, size, anchor):
    """Page-coloured plate under a label that sits on a translucent face."""
    w = text_w(s, size)
    x0 = px - (w / 2 if anchor == "middle" else w if anchor == "end" else 0)
    p.add(f'<rect x="{x0 - 3:.1f}" y="{py - 0.8 * size - 1.5:.1f}" width="{w + 6:.1f}" '
          f'height="{size + 4:.1f}" rx="3" fill="{BG}" opacity="0.82"/>')


def slabel(S, P, s, dx=0, dy=0, color=TEXT, size=12, anchor="start", bold=False, plated=False):
    """Label at a space point, optionally on a plate."""
    X, Y = S.pt(P)
    if plated:
        plate(S.p, S.p.X(X) + dx, S.p.Y(Y) + dy, s, size, anchor)
    S.p.label(X, Y, s, dx, dy, color, size, anchor, bold)


def leader(S, P, dx, dy, s, color=TEXT, size=12, anchor="start", bold=False):
    """Label pushed (dx, dy) pixels away from the space point P, with a thin leader line to P."""
    p = S.p
    X, Y = S.pt(P)
    px, py = p.X(X), p.Y(Y)
    tx, ty = px + dx, py + dy
    # the leader starts at the point of the label's box nearest to P
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


def box_edges(S, lo, hi, color=THEORY, width=1.5, opacity=1.0, hidden_opacity=0.55):
    """The twelve edges of an axis-parallel box; the three that meet at the far
    corner (smallest x, y and z) are hidden and dashed. Valid for cameras whose
    direction has positive x, y and z components."""
    x0, y0, z0 = lo
    x1, y1, z1 = hi
    far = (x0, y0, z0)
    for e in ((x1, y0, z0), (x0, y1, z0), (x0, y0, z1)):
        S.line([far, e], color, width * 0.75, "4 3", hidden_opacity)
    vis = [((x1, y0, z0), (x1, y1, z0)), ((x1, y0, z0), (x1, y0, z1)), ((x0, y1, z0), (x1, y1, z0)),
           ((x0, y1, z0), (x0, y1, z1)), ((x0, y0, z1), (x1, y0, z1)), ((x0, y0, z1), (x0, y1, z1)),
           ((x1, y1, z0), (x1, y1, z1)), ((x1, y0, z1), (x1, y1, z1)), ((x0, y1, z1), (x1, y1, z1))]
    for a, b in vis:
        S.line([a, b], color, width, None, opacity)


def box_faces(S, lo, hi, fill=THEORY, opacity=0.12):
    """The three faces of a box that face the camera (top, front x = max, right y = max)."""
    x0, y0, z0 = lo
    x1, y1, z1 = hi
    S.polygon([(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)], fill, opacity)
    S.polygon([(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)], fill, opacity * 0.8)
    S.polygon([(x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1)], fill, opacity * 0.65)


def split_runs(S, pts, visible, color=THEORY, width=1.8):
    """Draw a polyline in solid runs where visible(midpoint index) is true and dashed runs elsewhere."""
    run, state = [pts[0]], None
    for k in range(len(pts) - 1):
        v = visible(k)
        if state is not None and v != state:
            S.line(run, color, width, None, 1.0) if state else S.line(run, color, width * 0.6, "4 3", 0.6)
            run = [pts[k]]
        state = v
        run.append(pts[k + 1])
    S.line(run, color, width, None, 1.0) if state else S.line(run, color, width * 0.6, "4 3", 0.6)


def frange(a, b, n):
    return [a + (b - a) * k / n for k in range(n + 1)]


def axes2d(p, xmax, ymax, xlabel, ylabel, xmin=0.0, ymin=0.0, color=TEXT, size=12):
    """Arrow axes through the origin of a 2-D panel."""
    p.arrow((xmin, 0), (xmax, 0), color, 1.1, 7.0, None, 0.6)
    p.arrow((0, ymin), (0, ymax), color, 1.1, 7.0, None, 0.6)
    p.label(xmax, 0, it(xlabel), -2, 4 + size, color, size, "end")
    p.label(0, ymax, it(ylabel), 8, 6, color, size)


def tick2d(p, axis, v, s=None, color=TEXT, size=11):
    s = s if s is not None else str(v).replace("-", MINUS)
    if axis == "x":
        p.line([(v, 0), (v, 0)], color, 1)
        p.add(f'<line x1="{p.X(v):.1f}" y1="{p.Y(0) - 3:.1f}" x2="{p.X(v):.1f}" y2="{p.Y(0) + 3:.1f}" '
              f'stroke="{color}" stroke-width="1" opacity="0.7"/>')
        p.label(v, 0, s, 0, 5 + size, color, size, "middle")
    else:
        p.add(f'<line x1="{p.X(0) - 3:.1f}" y1="{p.Y(v):.1f}" x2="{p.X(0) + 3:.1f}" y2="{p.Y(v):.1f}" '
              f'stroke="{color}" stroke-width="1" opacity="0.7"/>')
        p.label(0, v, s, -7, 4, color, size, "end")


def tick3(S, P, s, dx, dy, tdir=(0, 1, 0), length=0.07, color=TEXT, size=11):
    a = vadd(P, vscale(-length, tdir))
    b = vadd(P, vscale(length, tdir))
    S.line([a, b], color, 1.0, None, 0.7)
    S.label(P, s, dx, dy, color, size, "middle")


# ============================================================
# kutu: the box B cut into sub-boxes, and one sub-box B_ijk enlarged
# ============================================================
cam = Camera(azimuth=35.0, elevation=22.0)
BX0, BX1, BY0, BY1, BZ0, BZ1 = 0.4, 2.8, 1.0, 4.2, 0.6, 2.2
DX = 0.8
pl, S = fit_space(cam, [(0, 0, 0), (3.6, 0, 0), (0, 5.0, 0), (0, 0, 3.0), (BX1, BY1, BZ1), (BX1, BY0, BZ0)],
                  30, 30, 72, 0.25)
S.axes(3.6, 5.0, 3.0, size=14, offsets=((-5, 15), (11, 5), (-11, -4)))
box_faces(S, (BX0, BY0, BZ0), (BX1, BY1, BZ1), THEORY, 0.13)
GRID = dict(color=THEORY, width=0.7, dash=None, opacity=0.55)
for x in frange(BX0, BX1, 3)[1:-1]:
    S.line([(x, BY0, BZ1), (x, BY1, BZ1)], **GRID)
    S.line([(x, BY1, BZ0), (x, BY1, BZ1)], **GRID)
for y in frange(BY0, BY1, 4)[1:-1]:
    S.line([(BX0, y, BZ1), (BX1, y, BZ1)], **GRID)
    S.line([(BX1, y, BZ0), (BX1, y, BZ1)], **GRID)
for zz in frange(BZ0, BZ1, 2)[1:-1]:
    S.line([(BX1, BY0, zz), (BX1, BY1, zz)], **GRID)
    S.line([(BX0, BY1, zz), (BX1, BY1, zz)], **GRID)
box_edges(S, (BX0, BY0, BZ0), (BX1, BY1, BZ1), THEORY, 1.6)
# the highlighted sub-box at the front-right-top corner
LO, HI = (BX1 - DX, BY1 - DX, BZ1 - DX), (BX1, BY1, BZ1)
box_faces(S, LO, HI, PRACTICE, 0.42)
box_edges(S, LO, HI, PRACTICE, 1.8, 1.0, 0.0)
leader(S, (BX1 - 0.4, BY1 - 0.4, BZ1), 120, -105, it("B") + sub(it("ijk"), 11), PRACTICE, 15, "start", True)
slabel(S, (BX0, BY0 + 0.3, BZ1), it("B"), -4, -10, THEORY, 16, "end", True)

# right panel: the sub-box enlarged
SX, SY, SZ = 1.3, 1.6, 1.1
left = pl.x0 + pl.w + 40
pr, S2 = fit_space(cam, [(0, 0, 0), (SX, 0, 0), (0, SY, 0), (0, 0, SZ), (SX, SY, SZ), (SX, 0, SZ), (0, SY, SZ)],
                   left, 110, 105, 0.35)
box_faces(S2, (0, 0, 0), (SX, SY, SZ), PRACTICE, 0.22)
box_edges(S2, (0, 0, 0), (SX, SY, SZ), PRACTICE, 1.8, 1.0, 0.6)
SP = (0.62, 0.78, 0.5)
S2.guide([SP, (SP[0], SP[1], 0)], TEXT, 0.5)
S2.point(SP, PRACTICE, 4.2)
S2.point((SP[0], SP[1], 0), TEXT, 2.2)
leader(S2, SP, 30, -150, "(" + it("x") + sub(it("ijk"), 10.5) + "*, " + it("y") + sub(it("ijk"), 10.5) + "*, "
       + it("z") + sub(it("ijk"), 10.5) + "*)", PRACTICE, 14, "middle")
# edge lengths
slabel(S2, ((SX) / 2, SY, 0), "Δ" + it("x"), 10, 18, TEXT, 15)
slabel(S2, (SX, SY / 2, 0), "Δ" + it("y"), -4, 22, TEXT, 15, "middle")
slabel(S2, (SX, 0, SZ / 2), "Δ" + it("z"), -10, 5, TEXT, 15, "end")
slabel(S2, (0, SY, SZ), it("B") + sub(it("ijk"), 11), 6, -10, PRACTICE, 15, "start", True)
save("kutu", figure(
    int(pr.x0 + pr.w + 30), int(max(pl.y0 + pl.h, pr.y0 + pr.h) + 30), [pl, pr],
    "Solda <em>B</em> kutusu <em>l</em> = 3, <em>m</em> = 4, <em>n</em> = 2 için 24 alt kutuya bölünmüş; "
    "turuncu alt kutu <em>B<sub>ijk</sub></em>'dır. Sağda bu alt kutu büyütülmüştür: kenarları "
    "&#916;<em>x</em>, &#916;<em>y</em>, &#916;<em>z</em>, hacmi &#916;<em>V</em> = "
    "&#916;<em>x</em> &#916;<em>y</em> &#916;<em>z</em>'dir ve içinden bir örnek nokta seçilir.",
    css_class=WIDE,
    aria="Left: a rectangular box B in space cut by a grid into 3 by 4 by 2 sub-boxes, one corner "
         "sub-box shaded. Right: that sub-box enlarged with edges Delta x, Delta y, Delta z and a "
         "sample point inside"))


# ============================================================
# tipler: solids of type 1, 2 and 3 with their projections D
# ============================================================
def blob_r(t, r0):
    """Radius of a smooth, slightly irregular closed curve."""
    return r0 * (1 + 0.10 * math.cos(2 * t) + 0.06 * math.sin(3 * t))


def blob_solid(S, amap, ca, cb, r0, u1, u2, nt=32):
    """Solid {(a, b) in D, u1(a, b) <= c <= u2(a, b)} drawn through the axis map amap(a, b, c) -> (x, y, z).

    D is the closed curve r = blob_r(t) about (ca, cb), drawn on the coordinate plane c = 0.
    Returns the boundary point function bpt(t, s).
    """
    cam_d = S.cam.d

    def bpt(t, s=1.0):
        rr = s * blob_r(t, r0)
        return ca + rr * math.cos(t), cb + rr * math.sin(t)

    def front(t):
        h = 1e-4
        a0, b0 = bpt(t - h)
        a1, b1 = bpt(t + h)
        n = amap(b1 - b0, -(a1 - a0), 0.0)        # outward normal of the wall, mapped to space
        return vdot(n, cam_d) > 0

    ts = frange(0.0, 2 * math.pi, 120)
    floor = [amap(*bpt(t), 0.0) for t in ts]
    S.polygon(floor, BASE, 0.20, BASE, 1.4)
    sil = [ts[k] for k in range(len(ts) - 1) if front(ts[k]) != front(ts[k + 1])]
    for t in sil:
        a, b = bpt(t)
        S.guide([amap(a, b, u1(a, b)), amap(a, b, 0.0)], TEXT, 0.5)
    # the caps are flat-tinted (one polygon each); only the wall is shaded face by face
    tc = frange(0.0, 2 * math.pi, 72)
    S.polygon([amap(*bpt(t), u1(*bpt(t))) for t in tc], THEORY, 0.08)
    S.surface(lambda v, t: amap(*bpt(t), u1(*bpt(t)) + v * (u2(*bpt(t)) - u1(*bpt(t)))), (0.0, 1.0),
              (0.0, 2 * math.pi), nu=1, nv=nt, fill=THEORY, stroke="none", opacity=(0.08, 0.24))
    S.polygon([amap(*bpt(t), u2(*bpt(t))) for t in tc], THEORY, 0.18)
    S.line([amap(*bpt(t), u2(*bpt(t))) for t in ts], THEORY, 1.8)
    split_runs(S, [amap(*bpt(t), u1(*bpt(t))) for t in ts], lambda k: front(0.5 * (ts[k] + ts[k + 1])))
    for t in sil:
        a, b = bpt(t)
        S.line([amap(a, b, u1(a, b)), amap(a, b, u2(a, b))], THEORY, 1.8)
    return bpt


def u_low(a, b, ca, cb, base):
    return base + 0.14 * math.sin(2.0 * (a - ca)) + 0.10 * math.cos(2.2 * (b - cb))


def u_high(a, b, ca, cb, base):
    return base + 0.18 * math.cos(1.8 * (a - ca)) - 0.15 * math.sin(1.6 * (b - cb))


cam = Camera(azimuth=35.0, elevation=22.0)
panels = []
left = 20
R0 = 0.62
TL = 13.5           # label size: the three panels share one 39rem column, so the drawing is kept small
# name, axis map, centre of D, range of the third variable, axis extents, label data
TYPES = (
    ("1", lambda a, b, c: (a, b, c), (1.5, 2.0), (1.5, 2.7), (2.5, 3.3, 3.3), "z", ("x", "y"), "xy",
     ((0.9, 0.5), (34, -34, "start")), ((1.4, 1.0), (30, 22, "start"))),
    ("2", lambda a, b, c: (c, a, b), (2.0, 1.7), (2.2, 3.4), (4.0, 3.1, 3.0), "x", ("y", "z"), "yz",
     ((math.pi, 1.0), (-10, 4, "end")), ((1.5, 1.0), (-30, -40, "end"))),
    ("3", lambda a, b, c: (a, c, b), (1.5, 1.7), (1.9, 3.3), (2.5, 4.0, 3.0), "y", ("x", "z"), "xz",
     ((0.3, 0.45), (10, 40, "start")), ((2.2, 1.0), (-12, -38, "end"))),
)
for (name, amap, (ca, cb), (lo, hi), (ex, ey, ez), cv, (av, bv), plane, lab2, lab1) in TYPES:
    ext = [(0, 0, 0), (ex, 0, 0), (0, ey, 0), (0, 0, ez)]
    ext += [amap(ca + dx, cb + dy, c) for dx in (-0.8, 0.8) for dy in (-0.8, 0.8) for c in (0.0, hi + 0.25)]
    pl, S = fit_space(cam, ext, left, 40, 48, 0.25)
    left += pl.w + 20
    S.axes(ex, ey, ez, size=TL, offsets=((-5, 15), (11, 5), (-11, -4)))
    u1 = (lambda a, b, ca=ca, cb=cb, lo=lo: u_low(a, b, ca, cb, lo))
    u2 = (lambda a, b, ca=ca, cb=cb, hi=hi: u_high(a, b, ca, cb, hi))
    bpt = blob_solid(S, amap, ca, cb, R0, u1, u2)
    a, b = bpt(0.0, 0.0)
    slabel(S, amap(a, b, 0.0), it("D"), 0, 6, BASE, 16, "middle", True)
    cE = u2(a, b) if name == "2" else 0.5 * (u1(a, b) + u2(a, b))
    slabel(S, amap(a, b, cE), it("E"), -12 if name == "3" else 0, 6, THEORY, 16, "middle", True)
    args = "(" + it(av) + ", " + it(bv) + ")"
    (t2, s2), (dx2, dy2, an2) = lab2
    (t1, s1), (dx1, dy1, an1) = lab1
    ta, tb = bpt(t2, s2)
    leader(S, amap(ta, tb, u2(ta, tb)), dx2, dy2, it(cv) + " = " + it("u") + sub("2", 10.5) + args, THEORY, TL, an2)
    ta, tb = bpt(t1, s1)
    leader(S, amap(ta, tb, u1(ta, tb)), dx1, dy1, it(cv) + " = " + it("u") + sub("1", 10.5) + args, THEORY, TL, an1)
    panels.append((pl, name, plane))
YT = max(q.y0 + q.h for q, _, _ in panels) + 18
for q, name, plane in panels:
    q.text_px(q.x0 + q.w / 2, YT, "tip " + name + ": " + it("D") + ", " + it(plane) + "-düzleminde",
              TEXT, 14, "middle", True)
panels = [q for q, _, _ in panels]
save("tipler", figure(
    int(left), int(max(q.y0 + q.h for q in panels) + 44), panels,
    "Üç tip katı bölge. Tip 1'de <em>E</em>, <em>xy</em>-düzlemindeki <em>D</em> izdüşümünün üstünde "
    "<em>z</em> = <em>u</em><sub>1</sub>(<em>x</em>, <em>y</em>) ile <em>z</em> = <em>u</em><sub>2</sub>(<em>x</em>, "
    "<em>y</em>) yüzeyleri arasında kalır. Tip 2'de <em>D</em> <em>yz</em>-düzlemindedir ve <em>x</em> iki yüzey "
    "arasında değişir; tip 3'te <em>D</em> <em>xz</em>-düzlemindedir ve <em>y</em> iki yüzey arasında değişir. "
    "Kesikli çizgiler cismi izdüşümüne bağlar.",
    css_class=WIDE,
    aria="Three panels: a solid E between a lower and an upper surface over a region D in the xy plane, a solid "
         "between two surfaces x = u1 and x = u2 over D in the yz plane, and a solid between y = u1 and y = u2 "
         "over D in the xz plane"))


# ============================================================
# ornek-2: the solid under z = 12xy over the triangle 0 <= y <= x <= 1, and its projection D
# ============================================================
ZS = 0.1            # z is drawn at one tenth of its size: the solid is 12 units tall


def e2(x, y, z):
    return (x, y, ZS * z)


def draw_e2(S, mesh=True, edge=1.7):
    """The solid E = {0 <= x <= 1, 0 <= y <= x, 0 <= z <= 12xy} (z scaled by ZS)."""
    S.polygon([e2(0, 0, 0), e2(1, 0, 0), e2(1, 1, 0)], BASE, 0.16)
    # the face y = x (turned away from the camera)
    S.surface(lambda u, w: e2(u, u, w * 12 * u * u), (0, 1), (0, 1), nu=12, nv=2, fill=THEORY, stroke="none",
              opacity=(0.05, 0.12))
    S.line([e2(0, 0, 0), e2(1, 1, 0)], THEORY, edge * 0.6, "4 3", 0.6)
    # the top z = 12xy
    S.surface(lambda u, v: e2(u, u * v, 12 * u * u * v), (0, 1), (0, 1), nu=8 if mesh else 2,
              nv=8 if mesh else 2, fill=THEORY, stroke=THEORY if mesh else "none", opacity=(0.08, 0.26),
              stroke_width=0.45, stroke_opacity=0.35)
    # the face x = 1
    S.polygon([e2(1, 0, 0), e2(1, 1, 0), e2(1, 1, 12)], THEORY, 0.20)
    for a, b in ((e2(0, 0, 0), e2(1, 0, 0)), (e2(1, 0, 0), e2(1, 1, 0)), (e2(1, 1, 0), e2(1, 1, 12)),
                 (e2(1, 0, 0), e2(1, 1, 12))):
        S.line([a, b], THEORY, edge)
    S.curve(lambda u: e2(u, u, 12 * u * u), 0, 1, THEORY, edge, 60)


cam2 = Camera(azimuth=-30.0, elevation=30.0)
EXT2 = [(0, 0, 0), (1.5, 0, 0), (0, 1.55, 0), (0, 0, 1.5), e2(1, 1, 12), e2(1, 0, 0)]
pl, S = fit_space(cam2, EXT2, 30, 30, 190, 0.2)
S.axes(1.5, 1.55, 1.5)
draw_e2(S)
tick3(S, (1, 0, 0), "1", -10, 10, (0, 1, 0))
tick3(S, (0, 1, 0), "1", 0, -8, (1, 0, 0))
slabel(S, e2(1, 1, 12), "(1, 1, 12)", 8, -4, TEXT, 11.5)
slabel(S, e2(0.78, 0.35, 0.5), it("E"), 0, 5, THEORY, 15, "middle", True)
leader(S, e2(0.55, 0.45, 12 * 0.55 * 0.45), -60, -48, it("z") + " = 12" + it("xy"), THEORY, 12.5, "end")

# the projection D in the xy-plane
q = eq_plot(pl.x0 + pl.w + 50, 60, 190, (-0.15, 1.45), (-0.15, 1.3))
q.polygon([(0, 0), (1, 0), (1, 1)], BASE, 0.22, BASE, 1.6)
axes2d(q, 1.4, 1.25, "x", "y")
q.line([(0, 0), (1.15, 1.15)], THEORY, 1.6)
q.line([(1, 0), (1, 1.15)], THEORY, 1.6)
q.label(1.15, 1.15, it("y") + " = " + it("x"), -8, -2, THEORY, 12.5, "end")
q.label(1, 0.45, it("x") + " = 1", 8, 4, THEORY, 12.5)
q.arrow((0.62, 0.0), (0.62, 0.62), PRACTICE, 2.0, 8.0)
q.label(0.62, 0.32, it("y") + ": 0 → " + it("x"), 7, 4, PRACTICE, 11.5)
q.label(0.84, 0.64, it("D"), 0, 5, BASE, 15, "middle", True)
tick2d(q, "x", 1)
tick2d(q, "y", 1)
save("ornek-2", figure(
    int(q.x0 + q.w + 30), int(max(pl.y0 + pl.h, q.y0 + q.h) + 30), [pl, q],
    "Solda <em>E</em> cismi: altta <em>z</em> = 0, üstte <em>z</em> = 12<em>xy</em> yüzeyi, yanlarda "
    "<em>y</em> = <em>x</em> ve <em>x</em> = 1 düzlemleri (dikey eksen 1/10 ölçeklidir). Sağda <em>E</em>'nin "
    "<em>xy</em>-düzlemine izdüşümü olan <em>D</em> üçgeni; ok, sabit <em>x</em> için <em>y</em>'nin 0'dan "
    "<em>x</em>'e değiştiğini gösterir.",
    css_class=WIDE,
    aria="Left: the solid E bounded below by the plane z = 0, above by the surface z = 12xy, and by the planes "
         "y = x and x = 1, with top corner (1, 1, 12). Right: its projection D, the triangle with vertices (0, 0), "
         "(1, 0), (1, 1), with a vertical arrow from y = 0 to y = x"))

# ============================================================
# tarama: how the iterated integral dz dy dx sweeps out the solid of Example 2
# ============================================================
panels = []
left = 20
TITLES = (it("z") + ", 0'dan 12" + it("xy") + "'ye", it("y") + ", 0'dan " + it("x") + "'e",
          it("x") + ", 0'dan 1'e")
SUBT = ("(" + it("x") + " ve " + it("y") + " sabit)", "(" + it("x") + " sabit)", "")
for k in range(3):
    pl, S = fit_space(cam2, EXT2, left, 30, 142, 0.15)
    left += pl.w + 20
    S.axes(1.5, 1.55, 1.5, labels=("x", "y", "z"), size=13.5, offsets=((-5, 15), (11, 5), (-11, -4)))
    draw_e2(S, mesh=False, edge=1.3)
    if k == 0:
        x0, y0 = 0.8, 0.5
        S.line([e2(x0, y0, 0), e2(x0, y0, 12 * x0 * y0)], PRACTICE, 3.0)
        S.point(e2(x0, y0, 0), PRACTICE, 3.6)
        S.point(e2(x0, y0, 12 * x0 * y0), PRACTICE, 3.6)
    elif k == 1:
        x0 = 0.7
        tri = [e2(x0, 0, 0), e2(x0, x0, 0), e2(x0, x0, 12 * x0 * x0)]
        S.polygon(tri, PRACTICE, 0.45, PRACTICE, 1.6)
        S.arrow(e2(x0, 0.08, 0.6), e2(x0, x0 - 0.04, 0.6), PRACTICE, 2.0, 8.0)
    else:
        for x0 in (0.25, 0.5, 0.75, 1.0):
            tri = [e2(x0, 0, 0), e2(x0, x0, 0), e2(x0, x0, 12 * x0 * x0)]
            S.polygon(tri, PRACTICE, 0.35, PRACTICE, 1.3)
        S.arrow(e2(0.05, -0.12, 0), e2(1.0, -0.12, 0), PRACTICE, 2.0, 8.0)
    panels.append(pl)
YT = max(q.y0 + q.h for q in panels) + 16
for k, q in enumerate(panels):
    q.text_px(q.x0 + q.w / 2, YT, TITLES[k], TEXT, 14, "middle", True)
    if SUBT[k]:
        q.text_px(q.x0 + q.w / 2, YT + 19, SUBT[k], TEXT, 13.5, "middle")
save("tarama", figure(
    int(left), int(YT + 32), panels,
    "<em>z</em> &#8594; <em>y</em> &#8594; <em>x</em> sırasındaki ardışık integral <em>E</em>'yi üç adımda tarar. "
    "Önce sabit (<em>x</em>, <em>y</em>) için <em>z</em> 0'dan 12<em>xy</em>'ye giden bir dikey çubuk, sonra sabit "
    "<em>x</em> için bu çubukların süpürdüğü üçgen dilim, en sonda <em>x</em> 0'dan 1'e giderken dilimlerin "
    "doldurduğu cisim.",
    css_class=WIDE,
    aria="Three copies of the solid of Example 2: a vertical segment from z = 0 to z = 12xy at a fixed point, a "
         "triangular slice at a fixed x swept in the y direction, and several slices filling the solid as x goes "
         "from 0 to 1"))


# ============================================================
# ornek-3: the solid between the paraboloid y = x^2 + z^2 and the plane y = 4,
# its projection D1 on the xy-plane and D3 on the xz-plane
# ============================================================
cam = Camera(azimuth=35.0, elevation=22.0)
d = cam.d
EXT3 = [(0, 0, 0), (3.0, 0, 0), (0, 5.4, 0), (0, 0, 2.9), (0, 0, -2.2), (-2.2, 0, 0)]
EXT3 += [(2 * math.cos(t), 4, 2 * math.sin(t)) for t in frange(0, 2 * math.pi, 24)]
EXT3 += [(2 * math.cos(t), 0, 2 * math.sin(t)) for t in frange(0, 2 * math.pi, 24)]
pl, S = fit_space(cam, EXT3, 20, 30, 62, 0.2)


def par(s_, t):
    return (s_ * math.cos(t), s_ * s_, s_ * math.sin(t))


# D3: the disk x^2 + z^2 <= 4 in the plane y = 0, with the dashed projection lines
S.polygon([(2 * math.cos(t), 0, 2 * math.sin(t)) for t in frange(0, 2 * math.pi, 120)], BASE, 0.20, BASE, 1.4)
S.line([(-2.2, 0, 0), (0, 0, 0)], TEXT, 1.1, None, 0.55)
S.line([(0, 0, -2.2), (0, 0, 0)], TEXT, 1.1, None, 0.55)
S.axes(3.0, 5.4, 2.9, size=13, offsets=((-5, 15), (11, 5), (-11, -4)))
A = math.hypot(d[0], d[2])
phi0 = math.atan2(d[2], d[0])
# silhouette of the cap circle seen along y: tangent points where the circle's normal is orthogonal to d
for t in (phi0 + math.pi / 2, phi0 - math.pi / 2):
    S.guide([(2 * math.cos(t), 4, 2 * math.sin(t)), (2 * math.cos(t), 0, 2 * math.sin(t))], TEXT, 0.5)
# the paraboloid wall, then the cap y = 4
S.surface(par, (0.0, 2.0), (0.0, 2 * math.pi), nu=6, nv=24, fill=THEORY, stroke=THEORY, opacity=(0.05, 0.22),
          stroke_width=0.4, stroke_opacity=0.22)
S.polygon([(2 * math.cos(t), 4, 2 * math.sin(t)) for t in frange(0, 2 * math.pi, 120)], THEORY, 0.16)
S.line([(2 * math.cos(t), 4, 2 * math.sin(t)) for t in frange(0, 2 * math.pi, 120)], THEORY, 1.8)
# silhouette (contour generator) of the paraboloid: d . (2x, -1, 2z) = 0
for sign in (1, -1):
    pts = []
    for s_ in frange(0.33, 2.0, 80):
        c = d[1] / (2 * s_ * A)
        if abs(c) <= 1:
            t = phi0 + sign * math.acos(c)
            pts.append(par(s_, t))
    S.line(pts, THEORY, 1.8)
S.line([(0, 0, 0), (0, 4, 0)], TEXT, 0.9, "4 3", 0.5)
tick3(S, (0, 4, 0), "4", 2, 17, (1, 0, 0), size=12)
slabel(S, (0.0, 2.6, 0.0), it("E"), -6, -18, THEORY, 14.5, "middle", True)
leader(S, par(1.35, 2.3), -20, -40, it("y") + " = " + it("x") + "² + " + it("z") + "²", THEORY, 13, "end")
leader(S, (2 * math.cos(0.4), 4, 2 * math.sin(0.4)), 40, -30, it("y") + " = 4", THEORY, 13)
slabel(S, (0.3, 0, -1.4), it("D") + sub("3", 10.5), 0, 5, BASE, 14, "middle", True)

# the two projections stacked in a column to the right of the solid
PP3 = 28
COL = pl.x0 + pl.w + 34
TITLE_GAP = 34                      # room for the panel title under each projection
col_h = (5.8 + 5.4) * PP3 + 2 * TITLE_GAP + 10
top = pl.y0 + max(0.0, (pl.h - col_h) / 2)

# D1 in the xy-plane: x^2 <= y <= 4
q1 = eq_plot(COL, top, PP3, (-2.6, 2.9), (-0.6, 5.2))
q1.polygon([(x, x * x) for x in frange(-2, 2, 60)], BASE, 0.22, BASE, 1.5)
axes2d(q1, 2.8, 5.1, "x", "y", -2.6, -0.5, size=12.5)
q1.line([(x, x * x) for x in frange(-2.25, 2.25, 60)], THEORY, 1.6)
q1.line([(-2.5, 4), (2.5, 4)], THEORY, 1.6)
q1.label(2.25, 2.25 ** 2, it("y") + " = " + it("x") + "²", 6, 12, THEORY, 12.5)
q1.label(0.95, 4, it("y") + " = 4", 0, 16, THEORY, 12.5, "middle")
q1.label(-0.85, 2.5, it("D") + sub("1", 10.5), 0, 5, BASE, 14, "middle", True)
tick2d(q1, "x", -2, MINUS + "2", size=11.5)
tick2d(q1, "x", 2, size=11.5)
q1.text_px(q1.x0 + q1.w / 2, q1.y0 + q1.h + 24, it("xy") + "-düzlemine izdüşüm", TEXT, 12.5, "middle", True)

# D3 in the xz-plane: x^2 + z^2 <= 4
q3 = eq_plot(COL, q1.y0 + q1.h + TITLE_GAP + 10, PP3, (-2.6, 3.2), (-2.7, 2.7))
q3.polygon([(2 * math.cos(t), 2 * math.sin(t)) for t in frange(0, 2 * math.pi, 120)], BASE, 0.22, BASE, 1.5)
axes2d(q3, 3.1, 2.6, "x", "z", -2.6, -2.6, size=12.5)
q3.label(0.08, -1.15, it("x") + "² + " + it("z") + "² " + LE + " 4", 0, 5, BASE, 12, "middle")
q3.label(-0.95, 0.75, it("D") + sub("3", 10.5), 0, 5, BASE, 14, "middle", True)
q3.label(-2, 0, MINUS + "2", -5, 16, TEXT, 11.5, "end")
q3.label(2, 0, "2", 5, 16, TEXT, 11.5)
q3.text_px(q3.x0 + q3.w / 2, q3.y0 + q3.h + 24, it("xz") + "-düzlemine izdüşüm", TEXT, 12.5, "middle", True)
save("ornek-3", figure(
    int(q3.x0 + q3.w + 60), int(max(pl.y0 + pl.h, q3.y0 + q3.h + 30) + 20), [pl, q1, q3],
    "Solda <em>y</em> = <em>x</em>² + <em>z</em>² paraboloidi ile <em>y</em> = 4 düzlemi arasındaki <em>E</em> "
    "cismi ve onun <em>xz</em>-düzlemine izdüşümü <em>D</em><sub>3</sub>. Sağ üstte <em>E</em>'nin "
    "<em>xy</em>-düzlemine izdüşümü <em>D</em><sub>1</sub> (<em>x</em>² &#8804; <em>y</em> &#8804; 4), sağ altta "
    "<em>D</em><sub>3</sub> diski (<em>x</em>² + <em>z</em>² &#8804; 4).",
    css_class=WIDE,
    aria="Left: a solid bowl opening along the y axis, bounded by the paraboloid y = x^2 + z^2 and the plane "
         "y = 4, with its projection, a disk of radius 2, in the xz plane. Top right: the parabolic region between "
         "y = x^2 and y = 4. Bottom right: the disk x^2 + z^2 at most 4"))


# ============================================================
# ornek-4: E = {0 <= x <= 1, 0 <= y <= x^2, 0 <= z <= y} and its three projections
# ============================================================
cam4 = Camera(azimuth=-40.0, elevation=28.0)
# the solid is drawn smaller than the projections' row is wide, so the figure stays low
# (the y axis runs on past the slanted edge so that its label clears the edges)
EXT4 = [(0, 0, 0), (1.45, 0, 0), (0, 1.7, 0), (0, 0, 1.25), (1, 1, 1), (1, 1, 0)]
pl, S = fit_space(cam4, EXT4, 150, 30, 135, 0.15)
S.axes(1.45, 1.7, 1.25, size=12.5, offsets=((-5, 15), (10, 3), (-11, -4)))
# hidden faces first: the floor and the parabolic cylinder y = x^2
S.polygon([(u, u * u, 0) for u in frange(0, 1, 40)] + [(1, 0, 0)], BASE, 0.16)
S.surface(lambda u, w: (u, u * u, w * u * u), (0, 1), (0, 1), nu=14, nv=2, fill=THEORY, stroke="none",
          opacity=(0.05, 0.10))
S.curve(lambda u: (u, u * u, 0), 0, 1, THEORY, 1.1, 60, "4 3", 0.6)
# the top z = y and the front x = 1
S.surface(lambda u, v: (u, v * u * u, v * u * u), (0, 1), (0, 1), nu=8, nv=4, fill=THEORY, stroke=THEORY,
          opacity=(0.10, 0.26), stroke_width=0.45, stroke_opacity=0.3)
S.polygon([(1, 0, 0), (1, 1, 0), (1, 1, 1)], THEORY, 0.20)
for a, b in (((0, 0, 0), (1, 0, 0)), ((1, 0, 0), (1, 1, 0)), ((1, 1, 0), (1, 1, 1)), ((1, 0, 0), (1, 1, 1))):
    S.line([a, b], THEORY, 1.8)
S.curve(lambda u: (u, u * u, u * u), 0, 1, THEORY, 1.8, 60)
tick3(S, (0, 1, 0), "1", 0, -9, (1, 0, 0), size=11.5)
tick3(S, (0, 0, 1), "1", -12, 4, (1, 0, 0), size=11.5)
S.label((1, 0, 0), "1", -12, 12, TEXT, 11.5, "middle")
slabel(S, (0.93, 0.55, 0.2), it("E"), 0, 5, THEORY, 14.5, "middle", True)
leader(S, (0.75, 0.42, 0.42), -60, -30, it("z") + " = " + it("y"), THEORY, 12.5, "end")
leader(S, (0.62, 0.3844, 0.0), -80, 40, it("y") + " = " + it("x") + "²", THEORY, 12.5, "end")
leader(S, (1, 0.75, 0.35), 50, 30, it("x") + " = 1", THEORY, 12.5)

PPU2 = 112
ROW = pl.y0 + pl.h + 22
specs = (
    ("x", "y", lambda t: (t, t * t), [(u, u * u) for u in frange(0, 1, 40)] + [(1, 0)],
     it("y") + " = " + it("x") + "²", (0.55, 0.30), "1", it("xy")),
    ("y", "z", lambda t: (t, t), [(0, 0), (1, 1), (1, 0)], it("z") + " = " + it("y"), (0.45, 0.45), "2", it("yz")),
    ("x", "z", lambda t: (t, t * t), [(u, u * u) for u in frange(0, 1, 40)] + [(1, 0)],
     it("z") + " = " + it("x") + "²", (0.55, 0.30), "3", it("xz")),
)
qs = []
left = 20
for h, v, curve, poly, lab, labpt, idx, plane in specs:
    q = eq_plot(left, ROW, PPU2, (-0.18, 1.4), (-0.18, 1.28))
    left += q.w + 30
    q.polygon(poly, BASE, 0.22, BASE, 1.5)
    axes2d(q, 1.35, 1.25, h, v, -0.12, -0.12)
    q.line([curve(t) for t in frange(0, 1.07, 50)], THEORY, 1.6)
    q.add(f'<line x1="{q.X(1):.1f}" y1="{q.Y(0):.1f}" x2="{q.X(1):.1f}" y2="{q.Y(1):.1f}" stroke="{THEORY}" '
          f'stroke-width="1.6"/>')
    c1 = curve(0.62)
    q.label(c1[0], c1[1], lab, -8, -4, THEORY, 12, "end")
    q.label(0.78, 0.2, it("D") + sub(idx, 10.5), 0, 5, BASE, 14, "middle", True)
    tick2d(q, "x", 1)
    tick2d(q, "y", 1)
    q.text_px(q.x0 + q.w / 2, q.y0 + q.h + 22, plane + "-düzlemine izdüşüm", TEXT, 12, "middle", True)
    qs.append(q)
# centre the 3-D panel above the row of projections
row_w = qs[-1].x0 + qs[-1].w - qs[0].x0
shift = qs[0].x0 + (row_w - pl.w) / 2 - pl.x0
pl.x0 += shift
save("ornek-4", figure(
    int(qs[-1].x0 + qs[-1].w + 30), int(ROW + qs[0].h + 36), [pl] + qs,
    "Üstte <em>E</em> cismi: altta <em>z</em> = 0, üstte <em>z</em> = <em>y</em> düzlemi, önde <em>x</em> = 1 "
    "düzlemi, arkada <em>y</em> = <em>x</em>² parabolik silindiri. Altta <em>E</em>'nin üç koordinat düzlemine "
    "izdüşümleri: <em>D</em><sub>1</sub> (0 &#8804; <em>y</em> &#8804; <em>x</em>²), <em>D</em><sub>2</sub> "
    "(0 &#8804; <em>z</em> &#8804; <em>y</em> &#8804; 1) ve <em>D</em><sub>3</sub> (0 &#8804; <em>z</em> &#8804; "
    "<em>x</em>²).",
    css_class=WIDE,
    aria="Top: a curved wedge in the unit cube bounded by z = 0, the plane z = y, the plane x = 1 and the "
         "parabolic cylinder y = x^2. Bottom: its projections, the region under y = x^2 in the xy plane, the "
         "triangle under z = y in the yz plane and the region under z = x^2 in the xz plane"))


# ============================================================
# ornek-6: E = {-1 <= y <= 1, y^2 <= x <= 1, 0 <= z <= x} and its projection D
# ============================================================
cam6 = Camera(azimuth=-72.0, elevation=40.0)
d6 = cam6.d
EXT6 = [(0, 0, 0), (1.6, 0, 0), (0, 1.6, 0), (0, 0, 1.45), (0, -1.2, 0), (1, -1, 0), (1, 1, 1), (1, -1, 1)]
pl, S = fit_space(cam6, EXT6, 30, 30, 165, 0.15)
S.line([(0, -1.2, 0), (0, 0, 0)], TEXT, 1.1, None, 0.55)
S.axes(1.6, 1.6, 1.45)
# hidden floor D, then the parabolic wall x = y^2
S.polygon([(v * v, v, 0) for v in frange(-1, 1, 60)], BASE, 0.16)
S.surface(lambda v, w: (v * v, v, w * v * v), (-1, 1), (0, 1), nu=24, nv=2, fill=THEORY, stroke="none",
          opacity=(0.05, 0.14))


def wall_front(v):
    """Does the wall x = y^2 face the camera at height-independent parameter y = v?"""
    return vdot((-1.0, 2 * v, 0.0), d6) > 0


VS = frange(-1, 1, 80)
split_runs(S, [(v * v, v, 0) for v in VS], lambda k: wall_front(0.5 * (VS[k] + VS[k + 1])))
for v0, v1 in zip(VS, VS[1:]):
    if wall_front(v0) != wall_front(v1):
        S.line([(v0 * v0, v0, 0), (v0 * v0, v0, v0 * v0)], THEORY, 1.4)
# the top z = x and the front x = 1
S.surface(lambda v, t: (v * v + t * (1 - v * v), v, v * v + t * (1 - v * v)), (-1, 1), (0, 1), nu=8, nv=4,
          fill=THEORY, stroke=THEORY, opacity=(0.10, 0.26), stroke_width=0.45, stroke_opacity=0.3)
S.polygon([(1, -1, 0), (1, 1, 0), (1, 1, 1), (1, -1, 1)], THEORY, 0.18)
for a, b in (((1, -1, 0), (1, 1, 0)), ((1, -1, 0), (1, -1, 1)), ((1, 1, 0), (1, 1, 1)), ((1, -1, 1), (1, 1, 1))):
    S.line([a, b], THEORY, 1.8)
S.curve(lambda v: (v * v, v, v * v), -1, 1, THEORY, 1.8, 60)
tick3(S, (1, 0, 0), "1", -12, 10, (0, 1, 0))
slabel(S, (1, 0.05, 0.5), it("E"), 0, 5, THEORY, 15, "middle", True)
leader(S, (0.55, -0.2, 0.55), -60, -50, it("z") + " = " + it("x"), THEORY, 12.5, "end")
leader(S, (0.64, 0.8, 0.0), 60, 10, it("x") + " = " + it("y") + "²", THEORY, 12.5)
leader(S, (1, -0.6, 0.25), 50, 34, it("x") + " = 1", THEORY, 12.5)

q = eq_plot(pl.x0 + pl.w + 50, 40, 130, (-0.25, 1.55), (-1.3, 1.35))
q.polygon([(v * v, v) for v in frange(-1, 1, 60)], BASE, 0.22, BASE, 1.5)
axes2d(q, 1.5, 1.3, "x", "y", -0.2, -1.25)
q.line([(v * v, v) for v in frange(-1.13, 1.13, 60)], THEORY, 1.6)
q.line([(1, -1.2), (1, 1.2)], THEORY, 1.6)
q.label(1.13 ** 2, 1.13, it("x") + " = " + it("y") + "²", -10, 2, THEORY, 12, "end")
q.label(1, -1.2, it("x") + " = 1", 7, 4, THEORY, 12)
YA = -0.45
q.arrow((YA * YA, YA), (1, YA), PRACTICE, 2.0, 8.0)
q.label(0.6, YA, it("x") + ": " + it("y") + "² → 1", 0, 17, PRACTICE, 11.5, "middle")
q.label(0.62, 0.35, it("D"), 0, 5, BASE, 15, "middle", True)
q.label(1, 0, "1", 6, 15, TEXT, 11)
save("ornek-6", figure(
    int(q.x0 + q.w + 30), int(max(pl.y0 + pl.h, q.y0 + q.h) + 30), [pl, q],
    "Solda <em>E</em> cismi: altta <em>z</em> = 0, üstte <em>z</em> = <em>x</em> düzlemi; yan yüzleri "
    "<em>x</em> = 1 düzlemi ve <em>x</em> = <em>y</em>² parabolik silindiridir. Sağda izdüşümü <em>D</em>: sabit "
    "<em>y</em> için <em>x</em>, <em>y</em>²'den 1'e değişir.",
    css_class=WIDE,
    aria="Left: a solid bounded below by z = 0, above by the plane z = x, in front by the plane x = 1 and behind "
         "by the parabolic cylinder x = y^2. Right: its projection D between the parabola x = y^2 and the line "
         "x = 1, with a horizontal arrow from the parabola to the line"))

# ============================================================
# piramit: the solid of the iterated integral int_0^1 int_0^(1-x) int_0^(2-2z) dy dz dx
# ============================================================
cam = Camera(azimuth=35.0, elevation=22.0)
EXT8 = [(0, 0, 0), (1.6, 0, 0), (0, 2.6, 0), (0, 0, 1.35), (1, 2, 0)]
pl, S = fit_space(cam, EXT8, 30, 30, 150, 0.2)
S.axes(1.6, 2.6, 1.35, size=13, offsets=((-5, 15), (11, 5), (-11, -4)))
A0, A1, A2, A3, AP = (0, 0, 0), (1, 0, 0), (1, 2, 0), (0, 2, 0), (0, 0, 1)
S.polygon([A0, A1, A2, A3], BASE, 0.18)
S.polygon([A1, A2, AP], THEORY, 0.22)
S.polygon([A2, A3, AP], THEORY, 0.14)
for a, b in ((A1, A2), (A2, A3), (A1, AP), (A2, AP), (A3, AP)):
    S.line([a, b], THEORY, 1.8)
for a, b in ((A0, A1), (A0, A3), (A0, AP)):
    S.line([a, b], THEORY, 1.1, "4 3", 0.7)
for P, s_, dx, dy, an in ((A1, "(1, 0, 0)", -10, -7, "end"), (A2, "(1, 2, 0)", 6, 16, "start"),
                          (A3, "(0, 2, 0)", 4, -8, "start"), (AP, "(0, 0, 1)", -8, -6, "end")):
    S.point(P, PRACTICE, 3.8)
    slabel(S, P, s_, dx, dy, TEXT, 12, an)
leader(S, (0.55, 0.5, 0.45), -90, -40, it("x") + " + " + it("z") + " = 1", THEORY, 13, "end")
leader(S, (0.25, 1.2, 0.4), 40, -50, it("y") + " + 2" + it("z") + " = 2", THEORY, 13)
save("piramit", figure(
    int(pl.x0 + pl.w + 40), int(pl.y0 + pl.h + 30), [pl],
    "Ardışık integralin cismi: tabanı <em>xy</em>-düzlemindeki [0, 1] &#215; [0, 2] dikdörtgeni, tepesi "
    "(0, 0, 1) olan bir piramit. Eğik yüzleri <em>x</em> + <em>z</em> = 1 ve <em>y</em> + 2<em>z</em> = 2 "
    "düzlemleridir; arka yüzleri koordinat düzlemleridir.",
    aria="A pyramid with rectangular base 0 to 1 in x and 0 to 2 in y on the xy plane and apex (0, 0, 1), with "
         "slanted faces x + z = 1 and y + 2z = 2"))
