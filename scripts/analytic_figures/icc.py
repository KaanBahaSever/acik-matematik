# -*- coding: utf-8 -*-
"""
Generates the SVG figures of the "İç Çarpım" chapter of Analitik Geometri
(dersler/analitik-geometri/ic-carpim.qmd).

The figures are NOT produced at build time. Run this script, then

    python scripts/center_figures.py "analytic-icc-*.md" --keep-width

and paste the resulting markup into the .qmd file. Figures go INSIDE the box
they explain (theorem, proof, example, solution or exercise), never inside a
definition box: a figure that illustrates a definition sits directly below it.

Plane figures use scripts/svg_plot.py with equal aspect (angles look true);
space figures use scripts/svg_plot3.py (orthographic camera). Every label is
placed by its estimated box (the same estimate scripts/check_figure_labels.py
uses) so that it sits beside its line or point, never on top of it.

The captions are Turkish on purpose - they are the text shown on the site.
The aria labels are plain ASCII.

Usage:   python scripts/analytic_figures/icc.py
Output:  scripts/_figures/analytic-icc-<name>.md
"""
import io
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import *  # noqa: E402,F403 - Plot, figure, colors, WIDE, cplane, ...
from svg_plot3 import *  # noqa: E402,F403 - Camera, Space, space_panel, vector helpers
from check_figure_labels import text_width  # noqa: E402 - same box estimate as the checker

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
KEY = "icc"
OUT = {}

MINUS_S, SQRT, NORM, APPROX_S = "&#8722;", "&#8730;", "&#8214;", "&#8776;"
LANG, RANG, LEQ_S, PI_T, DEG = "&#10216;", "&#10217;", "&#8804;", "&#960;", "&#176;"
THETA_S = "&#952;"

S_VEC, S_PT, S_NOTE, S_AXIS = 15, 14, 13, 13     # font sizes (px)


# ---------------------------------------------------------------------------
# text helpers
# ---------------------------------------------------------------------------
def it(s):
    return f'<tspan font-style="italic">{s}</tspan>'


def sub(s, size=11):
    return f'<tspan font-size="{size}" dy="4">{s}</tspan><tspan dy="-4">&#8203;</tspan>'


U, V, W, X_, Y_, Z_ = it("u"), it("v"), it("w"), it("x"), it("y"), it("z")
UPV = f"{U} + {V}"
UMV = f"{U} {MINUS_S} {V}"
IZD = "izd" + sub(U) + "(" + V + ")"
IP_UV = f"{LANG}{U}, {V}{RANG}"


def theta(k=None):
    return it(THETA_S) + (sub(str(k)) if k else "")


def num(v):
    """Tick number with a real minus sign and a decimal comma."""
    return fmt(v).replace("-", MINUS_S).replace(".", ",")


DIRS = {"r": (1, 0), "l": (-1, 0), "a": (0, -1), "b": (0, 1),
        "ur": (0.7071, -0.7071), "ul": (-0.7071, -0.7071),
        "lr": (0.7071, 0.7071), "ll": (-0.7071, 0.7071)}


def unit2(v):
    n = math.hypot(v[0], v[1]) or 1.0
    return (v[0] / n, v[1] / n)


def put(p, cx, cy, s, color=TEXT, size=S_PT, halo=False):
    """Text whose (estimated) box is centred on pixel (cx, cy).

    halo=True lays a page-coloured rounded box under the text, so a line that
    has to pass beneath a label breaks there. (A stroke halo with paint-order
    would be simpler, but it is painted per tspan and erases the glyphs of the
    previous run, e.g. the bowl of an italic P before an upright bracket.)
    """
    if halo:
        w = text_width(s, size)
        p.add(f'<rect x="{cx - w / 2 - 2.5:.1f}" y="{cy - 0.5 * size - 1.5:.1f}" width="{w + 5:.1f}" '
              f'height="{size + 3:.1f}" rx="3" fill="{BG}" opacity="0.92"/>')
    p.add(f'<text x="{cx:.1f}" y="{cy + 0.28 * size:.1f}" fill="{color}" font-size="{size}" '
          f'text-anchor="middle">{s}</text>')


def near_px(p, px, py, s, d, gap=7, color=TEXT, size=S_PT, halo=False):
    """Put the label beside pixel (px, py) in direction d, its box `gap` px away."""
    dx, dy = DIRS[d] if isinstance(d, str) else unit2(d)
    w, h = text_width(s, size), size
    ext = abs(dx) * w / 2 + abs(dy) * h / 2
    put(p, px + dx * (gap + ext), py + dy * (gap + ext), s, color, size, halo)


def near(p, pt, s, d, gap=7, color=TEXT, size=S_PT, halo=False):
    near_px(p, p.X(pt[0]), p.Y(pt[1]), s, d, gap, color, size, halo)


def along_px(p, a, b, s, hint, t=0.5, gap=7, color=TEXT, size=S_VEC, halo=False):
    """Label beside the pixel segment a-b at fraction t, on the side of `hint`."""
    ux, uy = unit2((b[0] - a[0], b[1] - a[1]))
    nx, ny = -uy, ux
    hx, hy = DIRS[hint] if isinstance(hint, str) else hint
    if nx * hx + ny * hy < 0:
        nx, ny = -nx, -ny
    mx, my = a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])
    near_px(p, mx, my, s, (nx, ny), gap, color, size, halo)


def along(p, a, b, s, hint, t=0.5, gap=7, color=TEXT, size=S_VEC, halo=False):
    along_px(p, (p.X(a[0]), p.Y(a[1])), (p.X(b[0]), p.Y(b[1])), s, hint, t, gap, color, size, halo)


def line_px(p, pts, color=TEXT, width=1.2, dash=None, opacity=1.0):
    d = " ".join(("M" if i == 0 else "L") + f"{x:.1f},{y:.1f}" for i, (x, y) in enumerate(pts))
    da = f' stroke-dasharray="{dash}"' if dash else ""
    p.add(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}"{da} '
          f'opacity="{opacity}" stroke-linejoin="round" stroke-linecap="round"/>')


def square2(p, V_, d1, d2, s, color=TEXT, width=1.2):
    """Right-angle mark at data point V_ between data directions d1, d2 (side s, data units)."""
    a, b = unit2(d1), unit2(d2)
    pts = [(V_[0] + s * a[0], V_[1] + s * a[1]),
           (V_[0] + s * (a[0] + b[0]), V_[1] + s * (a[1] + b[1])),
           (V_[0] + s * b[0], V_[1] + s * b[1])]
    p.line(pts, color, width)


def tick2(p, M, d, half=6, color=TEXT, width=1.5):
    """Equal-length tick across the data direction d at data point M."""
    ux, uy = unit2((d[0], -d[1]))            # pixel direction
    x, y = p.X(M[0]), p.Y(M[1])
    line_px(p, [(x - uy * half, y + ux * half), (x + uy * half, y - ux * half)], color, width)


def brace_px(p, a, b, n, depth=9, color=TEXT, width=1.2):
    """Curly brace from pixel a to pixel b bulging along the unit pixel normal n; returns its tip."""
    ux, uy = unit2((b[0] - a[0], b[1] - a[1]))
    h = depth / 2
    m = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)

    def q(P, s, t):   # P + s*n + t*u
        return (P[0] + s * n[0] + t * ux, P[1] + s * n[1] + t * uy)
    pts = [a, q(a, h, 0), q(a, h, h), q(m, h, -h), q(m, h, 0), q(m, 2 * h, 0),
           q(m, h, 0), q(m, h, h), q(b, h, -h), q(b, h, 0), b]
    f = lambda P: f"{P[0]:.1f},{P[1]:.1f}"
    d = (f"M{f(pts[0])} Q{f(pts[1])} {f(pts[2])} L{f(pts[3])} Q{f(pts[4])} {f(pts[5])} "
         f"Q{f(pts[6])} {f(pts[7])} L{f(pts[8])} Q{f(pts[9])} {f(pts[10])}")
    p.add(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}" '
          f'stroke-linejoin="round" stroke-linecap="round"/>')
    return q(m, 2 * h, 0)


def axes2(p, xl, yl, xticks=(), yticks=(), opacity=0.55):
    """Axes through the data origin with arrowheads, across the whole panel."""
    ox, oy = p.X(0), p.Y(0)
    left, right = p.x0 - 4, p.x0 + p.w + 8
    top, bottom = p.y0 - 8, p.y0 + p.h + 4
    a = [f'<g stroke="{TEXT}" stroke-width="1.1" opacity="{opacity}" fill="{TEXT}">',
         f'<line x1="{left:.1f}" y1="{oy:.1f}" x2="{right:.1f}" y2="{oy:.1f}"/>',
         f'<line x1="{ox:.1f}" y1="{bottom:.1f}" x2="{ox:.1f}" y2="{top:.1f}"/>',
         f'<polygon points="{right + 1:.1f},{oy:.1f} {right - 8:.1f},{oy - 3.8:.1f} '
         f'{right - 8:.1f},{oy + 3.8:.1f}" stroke="none"/>',
         f'<polygon points="{ox:.1f},{top - 1:.1f} {ox - 3.8:.1f},{top + 8:.1f} '
         f'{ox + 3.8:.1f},{top + 8:.1f}" stroke="none"/>']
    for t in xticks:
        a.append(f'<line x1="{p.X(t):.1f}" y1="{oy - 3.5:.1f}" x2="{p.X(t):.1f}" y2="{oy + 3.5:.1f}"/>')
    for t in yticks:
        a.append(f'<line x1="{ox - 3.5:.1f}" y1="{p.Y(t):.1f}" x2="{ox + 3.5:.1f}" y2="{p.Y(t):.1f}"/>')
    a.append('</g>')
    p.add("\n  ".join(a))
    for t in xticks:
        put(p, p.X(t), oy + 14, num(t), TEXT, 11, True)
    for t in yticks:
        put(p, ox - 7 - text_width(num(t), 11) / 2, p.Y(t), num(t), TEXT, 11, True)
    put(p, right + 4, oy + 16, it(xl), TEXT, S_AXIS)
    put(p, ox + 13, top + 2, it(yl), TEXT, S_AXIS)


def dot(p, pt, color=TEXT, r=3.4):
    p.points([pt], color, r)


def save_all():
    for name, content in OUT.items():
        with io.open(OUT_DIR / f"analytic-{KEY}-{name}.md", "w", encoding="utf-8", newline="\n") as f:
            f.write(content)
    print("generated:", ", ".join(OUT))


# ---------------------------------------------------------------------------
# 3-D helpers
# ---------------------------------------------------------------------------
def fit_space(cam, pts, W=700, pad=(40, 40, 34, 34), max_h=None):
    """Equal-aspect panel that holds the projections of `pts`, W px wide (pad: l, r, t, b)."""
    xs = [cam.project(P)[0] for P in pts]
    ys = [cam.project(P)[1] for P in pts]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    l, r, t, b = pad
    ppu = (W - l - r) / (x1 - x0)
    if max_h:
        ppu = min(ppu, (max_h - t - b) / (y1 - y0))
    width = (x1 - x0) * ppu
    p = space_panel((W - width) / 2, t, width, (x0, x1), (y0, y1))
    return p, Space(p, cam), int(round(t + p.h + b))


def px3(S, P):
    X, Y = S.pt(P)
    return (S.p.X(X), S.p.Y(Y))


def near3(S, P, s, d, gap=7, color=TEXT, size=S_PT, halo=False):
    x, y = px3(S, P)
    near_px(S.p, x, y, s, d, gap, color, size, halo)


def along3(S, A, B, s, hint, t=0.5, gap=7, color=TEXT, size=S_VEC, halo=False):
    along_px(S.p, px3(S, A), px3(S, B), s, hint, t, gap, color, size, halo)


def screen_dir(S, A, B):
    a, b = px3(S, A), px3(S, B)
    return unit2((b[0] - a[0], b[1] - a[1]))


def axes3(S, rng, labels=("X", "Y", "Z"), opacity=0.6, gap=5, label_dirs=None, colors=(TEXT,) * 3):
    """Coordinate axes from their min to max value, arrowheads at the max ends."""
    for k in range(3):
        a, b = [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]
        a[k], b[k] = rng[k]
        S.arrow(tuple(a), tuple(b), colors[k], 1.15, 8.0, None, opacity)
        d = label_dirs[k] if label_dirs else screen_dir(S, (0, 0, 0), tuple(b))
        near3(S, tuple(b), it(labels[k]), d, gap, colors[k], S_AXIS)


def arc3(S, O, a, b, r, color, width=1.6, n=48):
    """Arc of radius r at O from direction a to direction b; returns the 3-D midpoint."""
    e1 = vunit(a)
    e2 = vunit(vsub(b, vscale(vdot(b, e1), e1)))
    ang = math.acos(max(-1.0, min(1.0, vdot(e1, vunit(b)))))
    pts = [vadd(O, vadd(vscale(r * math.cos(ang * k / n), e1), vscale(r * math.sin(ang * k / n), e2)))
           for k in range(n + 1)]
    S.line(pts, color, width)
    return vadd(O, vadd(vscale(r * math.cos(ang / 2), e1), vscale(r * math.sin(ang / 2), e2)))


def arc_label3(S, O, mid, s, gap=5, color=TEXT, size=S_PT, halo=False):
    """Label just outside an arc, pushed away from its vertex on the screen."""
    o, m = px3(S, O), px3(S, mid)
    near_px(S.p, m[0], m[1], s, (m[0] - o[0], m[1] - o[1]), gap, color, size, halo)


def callout(p, anchor, center, s, color=TEXT, size=S_PT):
    """Label centred at pixel `center` with a thin leader line to pixel `anchor`."""
    w, h = text_width(s, size), size
    dx, dy = anchor[0] - center[0], anchor[1] - center[1]
    # leave the label box along the leader
    k = min((w / 2 + 3) / abs(dx) if dx else 1e9, (h / 2 + 3) / abs(dy) if dy else 1e9)
    line_px(p, [(center[0] + k * dx, center[1] + k * dy), anchor], color, 0.9, None, 0.8)
    put(p, center[0], center[1], s, color, size)


def square3(S, Q, a, b, s, color=TEXT, width=1.2):
    """Right-angle mark at Q in the plane of a and b (a projected square)."""
    ea, eb = vunit(a), vunit(b)
    pts = [vadd(Q, vscale(s, ea)), vadd(Q, vadd(vscale(s, ea), vscale(s, eb))), vadd(Q, vscale(s, eb))]
    S.line(pts, color, width)


# ===========================================================================
# 1. ucgen-esitsizligi - the triangle u, v, u + v
# ===========================================================================
p = cplane(20, 16, 600, (-0.6, 5.9), (-1.2, 4.05))
O2, A2, B2 = (0, 0), (4, 1), (5, 3.5)
p.arrow(O2, B2, BASE, 3.0, 12)
p.arrow(O2, A2, THEORY, 2.2, 10)
p.arrow(A2, B2, PRACTICE, 2.2, 10)
dot(p, O2)
dot(p, A2)
along(p, O2, A2, U, "b", color=THEORY)
along(p, A2, B2, V, "r", color=PRACTICE)
along(p, O2, B2, UPV, "ul", color=BASE)
near(p, O2, it("O"), "ll")
near(p, A2, it("A"), "lr")
near(p, B2, it("B"), "ur")
put(p, p.X(2.5), p.Y(-0.85),
    f"{NORM}{UPV}{NORM} {LEQ_S} {NORM}{U}{NORM} + {NORM}{V}{NORM}", TEXT, S_NOTE)
OUT["ucgen-esitsizligi"] = figure(
    640, 520, [p],
    "<em>u</em> ile <em>v</em> uç uca eklenince <em>u</em> + <em>v</em> üçgenin üçüncü kenarı olur. "
    "Bu kenarın uzunluğu öteki iki kenarın uzunlukları toplamını aşamaz: "
    "&#8214;<em>u</em> + <em>v</em>&#8214; &#8804; &#8214;<em>u</em>&#8214; + &#8214;<em>v</em>&#8214;.",
    aria="Triangle O A B with sides u from O to A, v from A to B and u plus v from O to B")


# ===========================================================================
# 2. aci-kosinus - the triangle O A B of the cosine proof
# ===========================================================================
p = cplane(20, 16, 582, (-0.6, 5.9), (-1.0, 2.95))
O2, A2, B2 = (0, 0), (3, 2.2), (5, 0)
ta = math.atan2(2.2, 3)
p.arc(0, 0, 0.72, 0, ta, TEXT, 1.4)
near(p, (0.72 * math.cos(ta / 2), 0.72 * math.sin(ta / 2)), theta(), (math.cos(ta / 2), -math.sin(ta / 2)),
     5, TEXT, S_PT)
p.arrow(O2, A2, THEORY, 2.2, 10)
p.arrow(O2, B2, PRACTICE, 2.2, 10)
p.arrow(A2, B2, BASE, 2.2, 10)
dot(p, O2)
along(p, O2, A2, U, "ul", color=THEORY)
along(p, A2, B2, W, "ur", color=BASE)
along(p, O2, B2, V, "b", color=PRACTICE)
near(p, O2, it("O"), "ll")
near(p, A2, it("A"), "a")
near(p, B2, it("B"), "lr")
put(p, p.X(5.05), p.Y(2.45), f"{W} = {V} {MINUS_S} {U}", TEXT, S_NOTE)
OUT["aci-kosinus"] = figure(
    620, 390, [p],
    "<em>u</em> ile <em>v</em> aynı <em>O</em> noktasından çizilir; <em>A</em>'dan <em>B</em>'ye giden "
    "üçüncü kenar <em>w</em> = <em>v</em> &#8722; <em>u</em> olur. <em>O</em> köşesindeki açı "
    "<em>&#952;</em>'dır ve Kosinüs Teoremi bu üçgene uygulanır.",
    aria="Triangle O A B with u from O to A, v from O to B, w from A to B and the angle theta at O")


# ===========================================================================
# 3. aci-dik-xz - w and x in the XZ-plane
# ===========================================================================
R2 = math.sqrt(2) / 2
p = cplane(40, 30, 480, (-1.5, 1.5), (-0.5, 1.5))
p.grid(xs=(-1, 0, 1), ys=(0, 1))
axes2(p, "X", "Z", xticks=(-1, 1), yticks=(1,))
Wv, Xv = (-1, R2), (R2, 1)
square2(p, (0, 0), Wv, Xv, 0.12)
p.arrow((0, 0), Wv, PRACTICE, 2.4, 11)
p.arrow((0, 0), Xv, THEORY, 2.4, 11)
near(p, Wv, W, "ul", 6, PRACTICE, S_VEC)
near(p, Wv, f"({MINUS_S}1, {SQRT}2/2)", "ll", 8, TEXT, S_NOTE)
near(p, Xv, X_, "ur", 6, THEORY, S_VEC)
near(p, Xv, f"({SQRT}2/2, 1)", "lr", 8, TEXT, S_NOTE)
OUT["aci-dik-xz"] = figure(
    560, 380, [p],
    "<em>w</em> ile <em>x</em>'in ikinci bileşeni 0 olduğundan ikisi de <em>XZ</em>-düzleminde yatar. "
    "Bu düzlemde çizildiklerinde aralarındaki açının dik olduğu görülür.",
    aria="The XZ-plane with the vectors w and x drawn from the origin and a right-angle mark between them")


# ===========================================================================
# 5. aci-genis-xy - u = (1, 0) and v = (-1, 1) in the XY-plane
# ===========================================================================
p = cplane(40, 30, 480, (-1.5, 1.5), (-0.5, 1.5))
p.grid(xs=(-1, 0, 1), ys=(0, 1))
axes2(p, "X", "Y", xticks=(-1, 1), yticks=(1,))
Uv, Vv = (1, 0), (-1, 1)
p.arc(0, 0, 0.3, 0, 3 * PI / 4, BASE, 1.7)
am = 3 * PI / 8
near(p, (0.3 * math.cos(am), 0.3 * math.sin(am)), f"3{PI_T}/4", (math.cos(am), -math.sin(am)), 5,
     BASE, S_PT, True)
p.arrow((0, 0), Uv, THEORY, 2.4, 11)
p.arrow((0, 0), Vv, PRACTICE, 2.4, 11)
along(p, (0, 0), Uv, U, "b", t=0.72, gap=16, color=THEORY)
near(p, Vv, V, "ul", 6, PRACTICE, S_VEC)
OUT["aci-genis-xy"] = figure(
    560, 380, [p],
    "<em>u</em> = (1, 0, 0) ve <em>v</em> = (&#8722;1, 1, 0) vektörleri <em>XY</em>-düzleminde yatar. "
    "Aralarındaki açı 3&#960;/4'tür; iç çarpımları negatif, açı geniştir.",
    aria="The XY-plane with u along the X axis, v pointing up-left and the obtuse angle 3 pi over 4 between them")


# ===========================================================================
# 6. isaret-uc-durum - the sign of the inner product, three cases
# ===========================================================================
PPU6 = 62
YR6 = (-0.35, 1.95)
specs6 = [((-0.35, 2.35), (1.2, 1.4), f"{IP_UV} &gt; 0 (dar açı)"),
          ((-0.35, 2.35), (0.0, 1.8), f"{IP_UV} = 0 (dik)"),
          ((-1.45, 2.35), (-1.2, 1.4), f"{IP_UV} &lt; 0 (geniş açı)")]
widths6 = [(xr[1] - xr[0]) * PPU6 for xr, _, _ in specs6]
gap6 = (700 - 40 - sum(widths6)) / 2
panels6, x0 = [], 20.0
for (xr, vt, cap), w6 in zip(specs6, widths6):
    q = cplane(x0, 26, w6, xr, YR6)
    x0 += w6 + gap6
    va = math.atan2(vt[1], vt[0])
    if abs(va - PI / 2) < 1e-9:
        square2(q, (0, 0), (1, 0), (0, 1), 0.2)
    else:
        q.arc(0, 0, 0.42, 0, va, TEXT, 1.4)
        near(q, (0.42 * math.cos(va / 2), 0.42 * math.sin(va / 2)), theta(),
             (math.cos(va / 2), -math.sin(va / 2)), 4, TEXT, S_PT)
    q.arrow((0, 0), (2, 0), THEORY, 2.2, 10)
    q.arrow((0, 0), vt, PRACTICE, 2.2, 10)
    dot(q, (0, 0))
    along(q, (0, 0), (2, 0), U, "b", t=0.85, color=THEORY)
    near(q, vt, V, "r" if vt[0] >= 0 else "l", 6, PRACTICE, S_VEC)
    near(q, (0, 0), it("O"), "ll", 6)
    put(q, q.x0 + q.w / 2, q.y0 + q.h + 30, cap, TEXT, S_NOTE)
    panels6.append(q)
OUT["isaret-uc-durum"] = figure(
    700, 220, panels6,
    "İç çarpımın işareti açıyı belirler: pozitifse açı dar, sıfırsa dik, negatifse geniştir.",
    css_class=WIDE,
    aria="Three panels: u horizontal and v making an acute, a right and an obtuse angle with u")


# ===========================================================================
# 7. dik-izdusum - the orthogonal projection of v onto u
# ===========================================================================
p = cplane(20, 20, 790, (-0.75, 6.85), (-1.5, 3.7))
P0, UE, Q7, R7 = (0, 0), (6, 1.2), (3, 3.2), (3.5, 0.7)
ud = unit2(UE)
dn = (ud[1], -ud[0])                           # data normal pointing below u
ppu7 = p.w / (p.xmax - p.xmin)
ta, tv = math.atan2(1.2, 6), math.atan2(3.2, 3)
p.arc(0, 0, 0.75, ta, tv, TEXT, 1.4)
near(p, (0.75 * math.cos((ta + tv) / 2), 0.75 * math.sin((ta + tv) / 2)), theta(),
     (math.cos((ta + tv) / 2), -math.sin((ta + tv) / 2)), 5, TEXT, S_PT)
p.line([Q7, R7], TEXT, 1.3, "5 4", 0.8)
square2(p, R7, (Q7[0] - R7[0], Q7[1] - R7[1]), UE, 0.2)
p.arrow(P0, UE, THEORY, 2.2, 10)
p.arrow(P0, Q7, PRACTICE, 2.2, 10)
sh = 7 / ppu7                                   # the projection arrow runs 7 px below u
Ps, Rs = (P0[0] + sh * dn[0], P0[1] + sh * dn[1]), (R7[0] + sh * dn[0], R7[1] + sh * dn[1])
p.arrow(Ps, Rs, BASE, 3.4, 12)
bo = 17 / ppu7
Pb, Rb = (P0[0] + bo * dn[0], P0[1] + bo * dn[1]), (R7[0] + bo * dn[0], R7[1] + bo * dn[1])
npx = unit2((dn[0], -dn[1]))
tip = brace_px(p, (p.X(Pb[0]), p.Y(Pb[1])), (p.X(Rb[0]), p.Y(Rb[1])), npx, 10, BASE, 1.3)
near_px(p, tip[0], tip[1], IZD, npx, 4, BASE, S_VEC)
dot(p, P0)
dot(p, Q7)
dot(p, R7)
near(p, UE, U, "b", 8, THEORY, S_VEC)
along(p, P0, Q7, V, "ul", color=PRACTICE)
along(p, Q7, R7, it("QR"), "r", t=0.45, gap=8, color=TEXT, size=S_NOTE)
near(p, P0, it("P"), "l", 9)
near(p, Q7, it("Q"), "a")
near(p, R7, it("R"), "lr", 14)
OUT["dik-izdusum"] = figure(
    830, 590, [p],
    "<em>P</em>'den çizilen <em>v</em>'nin ucu <em>Q</em>'dan <em>u</em> doğrultusuna dikme inilir; "
    "dikmenin ayağı <em>R</em>'dir. <em>P</em>'den <em>R</em>'ye giden vektör <em>v</em>'nin <em>u</em> üzerine "
    "dik izdüşümü izd<sub><em>u</em></sub>(<em>v</em>)'dir.",
    css_class=WIDE,
    aria="Vector v from P to Q, the direction u, the perpendicular from Q to the foot R and the projection from P to R")


# ===========================================================================
# 8. izdusum-yon - the projection points along u or against it
# ===========================================================================
PPU8 = 38
XR8, YR8 = (-3.2, 5.2), (-0.95, 2.45)
w8 = (XR8[1] - XR8[0]) * PPU8
gap8 = 700 - 40 - 2 * w8
panels8 = []
for k, (Qk, title) in enumerate((((2.5, 2.0), f"{IP_UV} &gt; 0"), ((-2.0, 2.0), f"{IP_UV} &lt; 0"))):
    q = cplane(20 + k * (w8 + gap8), 44, w8, XR8, YR8)
    F = (Qk[0], 0.0)
    q.line([(-3, 0), (5, 0)], TEXT, 1.0, "4 4", 0.55)
    q.line([Qk, F], TEXT, 1.3, "5 4", 0.8)
    square2(q, F, (0, 1), (-1, 0) if Qk[0] > 0 else (1, 0), 0.32)
    q.arrow((0, 0), (4, 0), THEORY, 2.2, 10)
    q.arrow((0, 0), Qk, PRACTICE, 2.2, 10)
    sh = -6 / PPU8 if Qk[0] > 0 else 0.0
    q.arrow((0, sh), (F[0], sh), BASE, 3.4, 12)
    dot(q, (0, 0))
    dot(q, Qk)
    near(q, (4, 0), U, "a", 7, THEORY, S_VEC)
    along(q, (0, 0), Qk, V, "ul" if Qk[0] > 0 else "ur", color=PRACTICE)
    near_px(q, q.X(F[0] / 2), q.Y(sh), IZD, "b", 7, BASE, S_VEC)
    near(q, (0, 0), it("P"), "ll" if Qk[0] > 0 else "lr", 7)
    near(q, Qk, it("Q"), "a", 7)
    put(q, q.x0 + q.w / 2, q.y0 - 22, title, TEXT, S_PT)
    panels8.append(q)
OUT["izdusum-yon"] = figure(
    700, 230, panels8,
    "Solda &#10216;<em>u</em>, <em>v</em>&#10217; &gt; 0: izdüşüm <em>u</em> ile aynı yönlüdür. "
    "Sağda &#10216;<em>u</em>, <em>v</em>&#10217; &lt; 0: izdüşüm <em>u</em> ile zıt yönlüdür.",
    css_class=WIDE,
    aria="Two panels: the projection of v onto u points along u when the inner product is positive and against u when it is negative")


# ===========================================================================
# 15. birim-toplam - three unit vectors with sum 0
# ===========================================================================
PPU15 = 180
S3 = math.sqrt(3) / 2
left = cplane(20, 30, (1.35 + 0.9) * PPU15, (-0.9, 1.35), (-1.05, 1.05))
cols = (THEORY, PRACTICE, BASE)
names = (U, V, W)
tips = ((1, 0), (-0.5, S3), (-0.5, -S3))
for k in range(3):
    a0 = 2 * PI * k / 3
    left.arc(0, 0, 0.26, a0 + 0.06, a0 + 2 * PI / 3 - 0.06, TEXT, 1.3)
    am = a0 + PI / 3
    near(left, (0.26 * math.cos(am), 0.26 * math.sin(am)), f"2{PI_T}/3", (math.cos(am), -math.sin(am)),
         5, TEXT, S_NOTE)
for k in range(3):
    left.arrow((0, 0), tips[k], cols[k], 2.3, 10)
dot(left, (0, 0))
near(left, tips[0], U, "r", 6, THEORY, S_VEC)
near(left, tips[1], V, "ul", 5, PRACTICE, S_VEC)
near(left, tips[2], W, "ll", 5, BASE, S_VEC)
near(left, (0, 0), it("O"), (-1, 0.0), 22)
yc = left.Y(0)                                  # the triangle is centred on the level of O
right = cplane(left.x0 + left.w + 20, yc - (1.05 - S3 / 2) * PPU15, 1.6 * PPU15, (-0.3, 1.3), (-0.35, 1.05))
T0, T1, T2 = (0, 0), (1, 0), (0.5, S3)
right.polygon([T0, T1, T2], BASE, 0.07)
right.arrow(T0, T1, THEORY, 2.3, 10)
right.arrow(T1, T2, PRACTICE, 2.3, 10)
right.arrow(T2, T0, BASE, 2.3, 10)
along(right, T0, T1, U, "b", color=THEORY)
along(right, T1, T2, V, "ur", color=PRACTICE)
along(right, T2, T0, W, "ul", color=BASE)
capy = left.y0 + left.h + 28
put(left, left.X(0.2), capy, f"{U}, {V}, {W} ikişer ikişer 2{PI_T}/3 açı yapar", TEXT, S_NOTE)
put(right, right.X(0.5), capy, f"{U} + {V} + {W} = 0", TEXT, S_NOTE)
OUT["birim-toplam"] = figure(
    760, int(capy + 16), [left, right],
    "Solda aynı noktadan çizilen <em>u</em>, <em>v</em>, <em>w</em> birim vektörleri; ikişer ikişer "
    "2&#960;/3 açı yaparlar. Sağda aynı vektörler uç uca eklenir ve kenar uzunluğu 1 olan bir eşkenar "
    "üçgen oluşturur: <em>u</em> + <em>v</em> + <em>w</em> = 0.",
    css_class=WIDE,
    aria="Left: three unit vectors from one point with angles 2 pi over 3 between them. Right: the same vectors head to tail forming an equilateral triangle")


# ===========================================================================
# 16. paralelkenar - the parallelogram law
# ===========================================================================
p = cplane(20, 20, 812, (-0.8, 5.75), (-0.62, 2.62))
O2, A2, C2, B2 = (0, 0), (4, 0), (5, 2), (1, 2)
p.line([B2, C2], TEXT, 1.2, None, 0.55)
p.line([A2, C2], TEXT, 1.2, None, 0.55)
p.arrow(O2, C2, BASE, 3.2, 12)
p.arrow(B2, A2, REMARK, 3.2, 12)
p.arrow(O2, A2, THEORY, 2.2, 10)
p.arrow(O2, B2, PRACTICE, 2.2, 10)
dot(p, O2)
along(p, O2, A2, U, "b", color=THEORY)
along(p, O2, B2, V, "l", color=PRACTICE)
along(p, O2, C2, UPV, "ul", t=0.74, color=BASE)
along(p, B2, A2, UMV, "ll", t=0.24, color=REMARK)
near(p, O2, it("O"), "ll")
near(p, A2, it("A"), "lr")
near(p, C2, it("C"), "ur")
near(p, B2, it("B"), "ul")
OUT["paralelkenar"] = figure(
    850, 450, [p],
    "Kenarları <em>u</em> ve <em>v</em> olan paralelkenarın köşegenleri <em>u</em> + <em>v</em> ve "
    "<em>u</em> &#8722; <em>v</em>'dir. Köşegenlerin kareleri toplamı dört kenarın kareleri toplamına eşittir.",
    css_class=WIDE,
    aria="Parallelogram O A C B with sides u and v and the diagonals u plus v and u minus v")


# ===========================================================================
# 17. kosegenler-esit - the rectangle has equal diagonals
# ===========================================================================
p = cplane(20, 20, 683, (-0.8, 3.75), (-0.62, 2.62))
O2, A2, C2, B2 = (0, 0), (3, 0), (3, 2), (0, 2)
p.line([B2, C2], TEXT, 1.2, None, 0.55)
p.line([A2, C2], TEXT, 1.2, None, 0.55)
square2(p, O2, (1, 0), (0, 1), 0.17)
p.arrow(O2, C2, BASE, 3.2, 12)
p.arrow(B2, A2, REMARK, 3.2, 12)
p.arrow(O2, A2, THEORY, 2.2, 10)
p.arrow(O2, B2, PRACTICE, 2.2, 10)
dot(p, O2)
along(p, O2, A2, U, "b", color=THEORY)
along(p, O2, B2, V, "l", color=PRACTICE)
along(p, O2, C2, UPV, "ul", t=0.3, color=BASE)
along(p, B2, A2, UMV, "ll", t=0.3, color=REMARK)
along(p, O2, C2, f"{SQRT}13", "lr", t=0.7, color=BASE, size=S_NOTE)
along(p, B2, A2, f"{SQRT}13", "ur", t=0.7, color=REMARK, size=S_NOTE)
near(p, O2, it("O"), "ll")
near(p, A2, it("A"), "lr")
near(p, C2, it("C"), "ur")
near(p, B2, it("B"), "ul")
OUT["kosegenler-esit"] = figure(
    720, 510, [p],
    "<em>u</em> = (3, 0, 0) ve <em>v</em> = (0, 2, 0) dik olduğundan paralelkenar bir dikdörtgendir; "
    "iki köşegenin uzunluğu da &#8730;13'tür.",
    aria="Rectangle O A C B with sides u and v, a right angle at O and the equal diagonals u plus v and u minus v")


# ===========================================================================
# 19. eskenar-dortgen - the diagonals of a rhombus are perpendicular
# ===========================================================================
p = cplane(34, 26, 496, (-0.5, 4.8), (-0.5, 4.8))
p.grid(xs=(1, 2, 3, 4), ys=(1, 2, 3, 4))
axes2(p, "X", "Y", xticks=(1, 2, 3, 4), yticks=(1, 2, 3, 4))
O2, A2, C2, B2 = (0, 0), (3, 1), (4, 4), (1, 3)
p.line([A2, C2], TEXT, 1.2, None, 0.6)
p.line([B2, C2], TEXT, 1.2, None, 0.6)
square2(p, (2, 2), (1, 1), (1, -1), 0.2)
p.arrow(O2, C2, BASE, 3.2, 12)
p.arrow(B2, A2, REMARK, 3.2, 12)
p.arrow(O2, A2, THEORY, 2.2, 10)
p.arrow(O2, B2, PRACTICE, 2.2, 10)
for s0, s1 in ((O2, A2), (A2, C2), (C2, B2), (B2, O2)):
    tick2(p, ((s0[0] + s1[0]) / 2, (s0[1] + s1[1]) / 2), (s1[0] - s0[0], s1[1] - s0[1]))
dot(p, O2)
along(p, O2, A2, U, "b", t=0.7, color=THEORY)
along(p, O2, B2, V, "l", t=0.7, color=PRACTICE)
along(p, O2, C2, UPV, "ul", t=0.74, color=BASE)
along(p, B2, A2, UMV, "ur", t=0.78, color=REMARK)
near(p, O2, it("O"), "ll", 6)
near(p, A2, it("A") + "(3, 1)", "lr", 6, TEXT, S_NOTE)
near(p, B2, it("B") + "(1, 3)", "ul", 6, TEXT, S_NOTE)
near(p, C2, it("C") + "(4, 4)", "ur", 6, TEXT, S_NOTE)
OUT["eskenar-dortgen"] = figure(
    560, 560, [p],
    "<em>u</em> = (3, 1) ve <em>v</em> = (1, 3) eşit uzunlukludur; üzerlerine kurulan paralelkenar bir "
    "eşkenar dörtgendir. Köşegenleri <em>u</em> + <em>v</em> = (4, 4) ile <em>u</em> &#8722; <em>v</em> = "
    "(2, &#8722;2) birbirine diktir.",
    aria="Rhombus O A C B on a grid with its perpendicular diagonals u plus v and u minus v meeting at (2, 2)")


# ===========================================================================
# 4. aci-dar-3b - u = (1, 1, 0) and v = (1, 0, 1) make pi/3
# ===========================================================================
O3 = (0.0, 0.0, 0.0)
cam = Camera(azimuth=72, elevation=32)
A3, B3 = (1.0, 1.0, 0.0), (1.0, 0.0, 1.0)
AX = ((0, 1.5), (0, 1.5), (0, 1.5))
p, S, H = fit_space(cam, [O3, (1.5, 0, 0), (0, 1.5, 0), (0, 0, 1.5), A3, B3], 700, (70, 70, 40, 40))
axes3(S, AX)
for P0_, P1_ in ((A3, (1, 0, 0)), (A3, (0, 1, 0)), (B3, (1, 0, 0)), (B3, (0, 0, 1))):
    S.guide([P0_, P1_], TEXT, 0.45, 1.0, "4 3")
for P_ in ((1, 0, 0), (0, 1, 0), (0, 0, 1)):
    S.point(P_, TEXT, 2.4)
S.line([A3, B3], TEXT, 1.4, "6 4", 0.8)
mid = arc3(S, O3, A3, B3, 0.36, BASE, 1.7)
arc_label3(S, O3, mid, f"{PI_T}/3", 5, BASE, S_PT)
S.arrow(O3, A3, THEORY, 2.4, 11)
S.arrow(O3, B3, PRACTICE, 2.4, 11)
S.point(O3, TEXT, 3.2)
along3(S, O3, A3, U, "b", t=0.62, color=THEORY)
along3(S, O3, B3, V, "l", t=0.62, color=PRACTICE)
near3(S, A3, it("A") + "(1, 1, 0)", screen_dir(S, O3, A3), 7, TEXT, S_NOTE)
near3(S, B3, it("B") + "(1, 0, 1)", screen_dir(S, O3, B3), 7, TEXT, S_NOTE)
near3(S, O3, it("O"), "r", 8)
OUT["aci-dar-3b"] = figure(
    700, H, [p],
    "<em>u</em> = (1, 1, 0) ve <em>v</em> = (1, 0, 1) başlangıç noktasından çizilir. <em>O</em>, <em>A</em>, "
    "<em>B</em> noktaları kenar uzunluğu &#8730;2 olan bir eşkenar üçgenin köşeleridir; bu yüzden "
    "<em>u</em> ile <em>v</em> arasındaki açı &#960;/3'tür.",
    css_class=WIDE,
    aria="Axes X, Y, Z with the vectors u to A(1, 1, 0) and v to B(1, 0, 1) and the angle pi over 3 between them")


# ===========================================================================
# 9. izd-ornek-i - v is perpendicular to u, the projection is 0
# ===========================================================================
cam = Camera(azimuth=20, elevation=12)
Uu, Vv = (-1.0, 1.0, -2.0), (1.0, 3.0, 1.0)
AX = ((-2.5, 3.5), (-2.5, 3.5), (-2.5, 3.5))
ends = [tuple(a if i == k else 0 for i in range(3)) for k in range(3) for a in AX[k]]
p, S, H = fit_space(cam, ends + [Uu, Vv], 700, (60, 60, 40, 40))
axes3(S, AX)
S.line([vscale(-1.3, Uu), vscale(1.3, Uu)], THEORY, 1.1, "5 4", 0.6)
square3(S, O3, Uu, Vv, 0.34)
S.arrow(O3, Uu, THEORY, 2.5, 11)
S.arrow(O3, Vv, PRACTICE, 2.5, 11)
S.point(O3, TEXT, 3.2)
along3(S, O3, Uu, U, "l", t=0.55, color=THEORY)
along3(S, O3, Vv, V, "a", t=0.55, color=PRACTICE)
near3(S, Uu, f"({MINUS_S}1, 1, {MINUS_S}2)", "l", 12, TEXT, S_NOTE)
near3(S, Vv, "(1, 3, 1)", screen_dir(S, O3, Vv), 8, TEXT, S_NOTE)
near3(S, O3, IZD + " = 0", (1, 0.55), 50, BASE, S_NOTE)
OUT["izd-ornek-i"] = figure(
    700, H, [p],
    "<em>v</em> = (1, 3, 1), <em>u</em> = (&#8722;1, 1, &#8722;2) doğrultusuna diktir. <em>v</em>'nin ucundan "
    "<em>u</em> doğrultusuna inen dikmenin ayağı başlangıç noktasıdır; izdüşüm sıfır vektörüdür.",
    css_class=WIDE,
    aria="Axes X, Y, Z with u = (-1, 1, -2), its line dashed, and v = (1, 3, 1) perpendicular to it at the origin")


# ===========================================================================
# 10. izd-ornek-ii - the projection points against u
# ===========================================================================
cam = Camera(azimuth=65, elevation=14)
Uu, Vv = (2.0, -1.0, 3.0), (-4.0, 1.0, 2.0)
Rr = vscale(-3 / 14, Uu)
AX = ((-4.5, 3.5), (-4.5, 3.5), (-4.5, 3.5))
ends = [tuple(a if i == k else 0 for i in range(3)) for k in range(3) for a in AX[k]]
p, S, H = fit_space(cam, ends + [Uu, Vv], 700, (60, 60, 40, 40))
axes3(S, AX)
S.line([vscale(-0.6, Uu), vscale(1.3, Uu)], THEORY, 1.1, "5 4", 0.6)
S.line([Vv, Rr], TEXT, 1.3, "5 4", 0.85)
square3(S, Rr, vsub(Vv, Rr), Uu, 0.3)
S.arrow(O3, Uu, THEORY, 2.4, 11)
S.arrow(O3, Vv, PRACTICE, 2.4, 11)
S.arrow(O3, Rr, BASE, 3.6, 11)
S.point(O3, TEXT, 3.0)
S.point(Rr, TEXT, 3.0)
along3(S, O3, Uu, U, "r", t=0.6, color=THEORY)
along3(S, O3, Vv, V, "a", t=0.55, color=PRACTICE)
near3(S, Uu, f"(2, {MINUS_S}1, 3)", "r", 12, TEXT, S_NOTE)
near3(S, Vv, f"({MINUS_S}4, 1, 2)", screen_dir(S, O3, Vv), 8, TEXT, S_NOTE)
near3(S, Rr, it("R"), "l", 9)
near3(S, O3, IZD, (-1, 0.8), 30, BASE, S_VEC)
OUT["izd-ornek-ii"] = figure(
    700, H, [p],
    "<em>v</em> = (&#8722;4, 1, 2)'nin <em>u</em> = (2, &#8722;1, 3) üzerine izdüşümü "
    "izd<sub><em>u</em></sub>(<em>v</em>) = (&#8722;3/7, 3/14, &#8722;9/14)'tür. İç çarpım negatif olduğundan "
    "izdüşüm <em>u</em>'ya zıt yönlüdür ve <em>u</em>'nun kesikli uzantısı üzerinde kalır.",
    css_class=WIDE,
    aria="Axes X, Y, Z with u, v, the perpendicular from the tip of v to the foot R on the extension of u and the short projection from the origin to R")


# ===========================================================================
# 11. izd-ornek-iii - the projection is half of u
# ===========================================================================
cam = Camera(azimuth=20, elevation=10)
Uu, Vv = (2.0, -1.0, 3.0), (1.0, -2.0, 1.0)
Rr = (1.0, -0.5, 1.5)
AX = ((-2.5, 3.5), (-2.5, 3.5), (-2.5, 3.5))
ends = [tuple(a if i == k else 0 for i in range(3)) for k in range(3) for a in AX[k]]
p, S, H = fit_space(cam, ends + [Uu, Vv], 700, (60, 60, 40, 40))
axes3(S, AX)
S.line([Vv, Rr], TEXT, 1.3, "5 4", 0.85)
square3(S, Rr, vsub(Vv, Rr), vscale(-1, Uu), 0.28)
S.arrow(O3, Uu, THEORY, 2.2, 11)
S.arrow(O3, Rr, BASE, 4.2, 12)
S.arrow(O3, Vv, PRACTICE, 2.4, 11)
S.point(O3, TEXT, 3.0)
S.point(Rr, TEXT, 3.0)
near3(S, Uu, U, "l", 8, THEORY, S_VEC)
near3(S, Uu, f"(2, {MINUS_S}1, 3)", "r", 8, TEXT, S_NOTE)
along3(S, O3, Rr, IZD, "l", t=0.5, gap=9, color=BASE)
along3(S, O3, Vv, V, "b", t=0.55, color=PRACTICE)
near3(S, Vv, f"(1, {MINUS_S}2, 1)", screen_dir(S, O3, Vv), 8, TEXT, S_NOTE)
near3(S, Rr, f"(1, {MINUS_S}1/2, 3/2)", "r", 10, TEXT, S_NOTE)
OUT["izd-ornek-iii"] = figure(
    700, H, [p],
    "<em>v</em> = (1, &#8722;2, 1)'nin <em>u</em> = (2, &#8722;1, 3) üzerine izdüşümü "
    "izd<sub><em>u</em></sub>(<em>v</em>) = (1, &#8722;1/2, 3/2)'dir; dikmenin ayağı <em>u</em>'nun tam "
    "ortasına düşer.",
    css_class=WIDE,
    aria="Axes X, Y, Z with u, v and the projection of v onto u, which is exactly half of u")


# ===========================================================================
# 12. dogrultu-acilari - the three direction angles
# ===========================================================================
cam = Camera(azimuth=38, elevation=20)
Pp = (2.0, 2.5, 3.0)
AX = ((0, 3.5), (0, 3.5), (0, 3.5))
ACOL = (PRACTICE, BASE, REMARK)
p, S, H = fit_space(cam, [O3, (3.5, 0, 0), (0, 3.5, 0), (0, 0, 3.5), Pp], 700, (60, 60, 40, 40))
axes3(S, AX, colors=ACOL, opacity=0.75)
F = (2.0, 2.5, 0.0)
S.guide([Pp, F], TEXT, 0.5)
S.guide([F, (2.0, 0, 0)], TEXT, 0.5)
S.guide([F, (0, 2.5, 0)], TEXT, 0.5)
S.point(F, TEXT, 2.2)
for k, r in ((0, 1.8), (1, 1.2), (2, 0.6)):
    e = tuple(1.0 if i == k else 0.0 for i in range(3))
    m = arc3(S, O3, Pp, e, r, ACOL[k], 1.8)
    if k < 2:
        arc_label3(S, O3, m, theta(k + 1), 5, ACOL[k], S_PT)
    else:                      # the theta1 arc passes just outside this one
        mx, my = px3(S, m)
        callout(p, (mx, my), (mx - 40, my - 58), theta(3), ACOL[k], S_PT)
S.arrow(O3, Pp, THEORY, 3.0, 12)
S.point(O3, TEXT, 3.0)
near3(S, Pp, U, "ur", 6, THEORY, S_VEC)
OUT["dogrultu-acilari"] = figure(
    700, H, [p],
    "<em>u</em> vektörünün doğrultu açıları: <em>&#952;</em><sub>1</sub>, <em>&#952;</em><sub>2</sub>, "
    "<em>&#952;</em><sub>3</sub> sırasıyla <em>u</em>'nun <em>X</em>-, <em>Y</em>- ve <em>Z</em>-eksenlerinin "
    "pozitif yönleriyle yaptığı açılardır.",
    css_class=WIDE,
    aria="Axes X, Y, Z in three colors with a vector u and the three angles theta 1, theta 2, theta 3 it makes with the axes")


# ===========================================================================
# 13. dogrultman-ornek - u = (2, -1, 2) and its direction angles
# ===========================================================================
cam = Camera(azimuth=35, elevation=20)
Pp = (2.0, -1.0, 2.0)
U0 = (2 / 3, -1 / 3, 2 / 3)
AX = ((0, 2.8), (-1.8, 2.0), (0, 2.8))
ends = [tuple(a if i == k else 0 for i in range(3)) for k in range(3) for a in AX[k]]
p, S, H = fit_space(cam, ends + [Pp], 700, (90, 90, 40, 40))
axes3(S, AX, colors=ACOL, opacity=0.75)
F = (2.0, -1.0, 0.0)
S.guide([Pp, F], TEXT, 0.5)
S.guide([F, (2.0, 0, 0)], TEXT, 0.5)
S.guide([F, (0, -1.0, 0)], TEXT, 0.5)
S.point(F, TEXT, 2.2)
labs = (f"{theta(1)} {APPROX_S} 48,19{DEG}", f"{theta(2)} {APPROX_S} 109,47{DEG}",
        f"{theta(3)} {APPROX_S} 48,19{DEG}")
MIDS13 = []
O13 = px3(S, O3)
for k, r in ((0, 1.35), (1, 1.65), (2, 1.1)):
    e = tuple(1.0 if i == k else 0.0 for i in range(3))
    MIDS13.append(px3(S, arc3(S, O3, Pp, e, r, ACOL[k], 1.8)))
for k in (1, 2):
    mx, my = MIDS13[k]
    near_px(p, mx, my, labs[k], (mx - O13[0], my - O13[1]), 5, ACOL[k], S_NOTE)
mx, my = MIDS13[0]              # the negative Y axis runs right past this arc
callout(p, (mx, my), (mx - 62, my - 48), labs[0], ACOL[0], S_NOTE)
S.arrow(O3, Pp, THEORY, 2.6, 12)
S.arrow(O3, U0, TEXT, 3.6, 11)
S.point(O3, TEXT, 3.0)
along3(S, O3, Pp, U, "r", t=0.7, color=THEORY)
along3(S, O3, U0, it("u") + sub("0"), "l", t=0.6, color=TEXT)
near3(S, Pp, it("P") + f"(2, {MINUS_S}1, 2)", screen_dir(S, O3, Pp), 8, TEXT, S_NOTE)
OUT["dogrultman-ornek"] = figure(
    700, H, [p],
    "<em>u</em> = (2, &#8722;1, 2) ve <em>u</em> yönündeki birim vektör <em>u</em><sub>0</sub> = "
    "(2/3, &#8722;1/3, 2/3). <em>u</em>, <em>Y</em>-ekseninin pozitif yönüyle geniş açı, öteki iki eksenle "
    "eşit dar açılar yapar.",
    css_class=WIDE,
    aria="Axes X, Y, Z with u = (2, -1, 2), the unit vector u0 along it and the three direction angles")


# ===========================================================================
# 14. dik-ucgen-3b - the right triangle A B C
# ===========================================================================
cam = Camera(azimuth=45, elevation=16)
A3, B3, C3 = (0.0, 0.0, 0.0), (2.0, -1.0, 1.0), (3.0, -4.0, -4.0)
AX = ((0, 3.5), (-4.5, 1.0), (-4.5, 1.5))
ends = [tuple(a if i == k else 0 for i in range(3)) for k in range(3) for a in AX[k]]
p, S, H = fit_space(cam, ends + [B3, C3], 700, (70, 70, 40, 40))
axes3(S, AX)
S.polygon([A3, B3, C3], BASE, 0.08)
square3(S, B3, vsub(A3, B3), vsub(C3, B3), 0.4)
S.arrow(A3, C3, BASE, 2.6, 12)
S.arrow(A3, B3, THEORY, 2.6, 12)
S.arrow(B3, C3, PRACTICE, 2.6, 12)
for P_ in (A3, B3, C3):
    S.point(P_, TEXT, 3.0)
G = vscale(1 / 3, vadd(vadd(A3, B3), C3))
gx, gy = px3(S, G)


def out_of(P_):
    x, y = px3(S, P_)
    return (x - gx, y - gy)


along3(S, A3, B3, U, out_of(vscale(0.5, vadd(A3, B3))), color=THEORY)
along3(S, B3, C3, V, out_of(vscale(0.5, vadd(B3, C3))), color=PRACTICE)
along3(S, A3, C3, W, out_of(vscale(0.5, vadd(A3, C3))), color=BASE)
near3(S, A3, it("A") + "(0, 0, 0)", out_of(A3), 8, TEXT, S_NOTE)
near3(S, B3, it("B") + f"(2, {MINUS_S}1, 1)", out_of(B3), 8, TEXT, S_NOTE)
near3(S, C3, it("C") + f"(3, {MINUS_S}4, {MINUS_S}4)", out_of(C3), 8, TEXT, S_NOTE)
OUT["dik-ucgen-3b"] = figure(
    700, H, [p],
    "<em>u</em> + <em>v</em> = <em>w</em> olduğundan üç vektör <em>ABC</em> üçgeninin kenarlarıdır; "
    "&#10216;<em>u</em>, <em>v</em>&#10217; = 0 olduğundan <em>B</em> köşesindeki açı diktir.",
    css_class=WIDE,
    aria="Axes X, Y, Z with the triangle A B C, sides u from A to B, v from B to C, w from A to C and a right angle at B")


# ===========================================================================
# 18. esit-farklar-3b - the equilateral triangle U V W
# ===========================================================================
cam = Camera(azimuth=35, elevation=22)
U3, V3, W3 = (1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)
AX = ((0, 1.4), (0, 1.4), (0, 1.4))
p, S, H = fit_space(cam, [O3, (1.4, 0, 0), (0, 1.4, 0), (0, 0, 1.4)], 700, (90, 90, 50, 50))
for k in range(3):
    b = tuple(AX[k][1] if i == k else 0.0 for i in range(3))
    e = tuple(1.0 if i == k else 0.0 for i in range(3))
    S.arrow(e, b, TEXT, 1.15, 8.0, None, 0.6)
    near3(S, b, it("XYZ"[k]), screen_dir(S, O3, b), 5, TEXT, S_AXIS)
for e, nm in ((U3, U), (V3, V), (W3, W)):       # behind the triangle: dashed
    S.line([O3, vscale(0.93, e)], TEXT, 1.3, "5 4", 0.55)
S.polygon([U3, V3, W3], THEORY, 0.08)
ext = vadd(U3, vscale(0.5, vunit(vsub(U3, V3))))
S.line([U3, ext], TEXT, 1.3, "5 4", 0.8)
m = arc3(S, U3, vsub(U3, V3), vsub(W3, U3), 0.2, TEXT, 1.5)
arc_label3(S, U3, m, f"2{PI_T}/3", 5, TEXT, S_NOTE)
ECOL = (THEORY, PRACTICE, BASE)
S.arrow(V3, U3, ECOL[0], 2.8, 12)
S.arrow(U3, W3, ECOL[1], 2.8, 12)
S.arrow(W3, V3, ECOL[2], 2.8, 12)
for P_ in (O3, U3, V3, W3):
    S.point(P_, TEXT, 2.8)
G = (1 / 3, 1 / 3, 1 / 3)
gx, gy = px3(S, G)
along3(S, V3, U3, UMV, out_of(vscale(0.5, vadd(V3, U3))), color=ECOL[0])
along3(S, U3, W3, f"{W} {MINUS_S} {U}", out_of(vscale(0.5, vadd(U3, W3))), color=ECOL[1])
along3(S, W3, V3, f"{V} {MINUS_S} {W}", out_of(vscale(0.5, vadd(W3, V3))), color=ECOL[2])
for e, nm in ((U3, U), (V3, V), (W3, W)):
    along3(S, O3, e, nm, "a", t=0.5, gap=5, color=TEXT, size=S_NOTE)
near3(S, U3, it("U") + "(1, 0, 0)", (0.35, 1), 8, TEXT, S_NOTE)
near3(S, V3, it("V") + "(0, 1, 0)", (-0.4, 1), 8, TEXT, S_NOTE)
near3(S, W3, it("W") + "(0, 0, 1)", "r", 8, TEXT, S_NOTE)
OUT["esit-farklar-3b"] = figure(
    700, H, [p],
    "<em>u</em> = <em>e</em><sub>1</sub>, <em>v</em> = <em>e</em><sub>2</sub>, <em>w</em> = <em>e</em><sub>3</sub> "
    "için <em>UVW</em> eşkenar bir üçgendir. Fark vektörleri üçgenin kenarlarını sırayla dolaşır; ardışık iki "
    "kenar vektörü arasındaki açı, dış açı olan 2&#960;/3'tür.",
    css_class=WIDE,
    aria="Axes X, Y, Z with the equilateral triangle U V W on the unit points and its edge vectors u - v, w - u, v - w")


# ===========================================================================
# 20. izd-alistirma-iii - projection of (1, -2, 1) onto (4, -4, 7)
# ===========================================================================
cam = Camera(azimuth=50, elevation=12)
Uu, Vv = (4.0, -4.0, 7.0), (1.0, -2.0, 1.0)
Rr = (76 / 81, -76 / 81, 133 / 81)
AX = ((-0.5, 4.5), (-4.5, 0.5), (-0.5, 7.5))
ends = [tuple(a if i == k else 0 for i in range(3)) for k in range(3) for a in AX[k]]
p, S, H = fit_space(cam, ends + [Uu, Vv], 700, (80, 80, 40, 40))
axes3(S, AX)
S.line([Vv, Rr], TEXT, 1.3, "5 4", 0.85)
square3(S, Rr, vsub(Vv, Rr), vscale(-1, Uu), 0.3)
S.arrow(O3, Uu, THEORY, 2.2, 11)
S.arrow(O3, Rr, BASE, 4.2, 12)
S.arrow(O3, Vv, PRACTICE, 2.4, 11)
S.point(O3, TEXT, 3.0)
S.point(Rr, TEXT, 3.0)
near3(S, Uu, f"{U} = (4, {MINUS_S}4, 7)", screen_dir(S, O3, Uu), 8, THEORY, S_VEC)
along3(S, O3, Rr, IZD, "r", t=0.5, gap=9, color=BASE)
along3(S, O3, Vv, V, "b", t=0.55, color=PRACTICE)
near3(S, Vv, f"(1, {MINUS_S}2, 1)", screen_dir(S, O3, Vv), 8, TEXT, S_NOTE)
OUT["izd-alistirma-iii"] = figure(
    700, H, [p],
    "<em>v</em> = (1, &#8722;2, 1)'nin <em>u</em> = (4, &#8722;4, 7) üzerine izdüşümü "
    "izd<sub><em>u</em></sub>(<em>v</em>) = (76/81, &#8722;76/81, 133/81)'dir; bileşen 19/81 pozitif olduğundan "
    "izdüşüm <em>u</em> ile aynı yönlüdür.",
    css_class=WIDE,
    aria="Axes X, Y, Z with the long vector u, the vector v and the short projection of v onto u with the right angle at its foot")


# ===========================================================================
# 21. paralel-i - three vectors on the Y axis
# ===========================================================================
cam = Camera(azimuth=32, elevation=20)
AX = ((0, 1.5), (0, 3.6), (0, 1.5))
p, S, H = fit_space(cam, [O3, (1.5, 0, 0), (0, 3.6, 0), (0, 0, 1.5)], 700, (60, 60, 40, 40))
axes3(S, AX)
for t in (1, 2, 3):
    S.line([(-0.06, t, 0), (0.06, t, 0)], TEXT, 1.1, None, 0.7)
    near3(S, (0, t, 0), num(t), "b", 6, TEXT, 11)
specs = ((3, 0.0, W, BASE, 2.0, 10), (2, 0.15, V, PRACTICE, 2.8, 11), (1, 0.3, U, THEORY, 3.6, 12))
for L, dz, nm, col, wd, hd in specs:
    if dz:
        S.line([(0, L, dz), (0, L, 0)], TEXT, 1.1, "3 3", 0.7)
    S.arrow((0, 0, dz), (0, L, dz), col, wd, hd)
for L, dz, nm, col, wd, hd in specs:
    near3(S, (0, L, dz), nm, "a", 7, col, S_VEC)
S.point(O3, TEXT, 3.0)
OUT["paralel-i"] = figure(
    700, H, [p],
    "<em>u</em> = (0, 1, 0), <em>v</em> = (0, 2, 0), <em>w</em> = (0, 3, 0) hepsi <em>Y</em>-ekseninin "
    "pozitif kısmı üzerindedir; aynı doğrultu ve yöndedirler. Görünsünler diye oklar biraz yukarı kaydırılarak "
    "çizilmiştir.",
    css_class=WIDE,
    aria="Axes X, Y, Z with three arrows of lengths 1, 2, 3 along the positive Y axis, drawn slightly apart")


# ===========================================================================
# 22. paralel-ii - three vectors on the line y = z of the YZ-plane
# ===========================================================================
cam = Camera(azimuth=15, elevation=14)
AX = ((0, 1.5), (0, 6.8), (0, 6.8))
p, S, H = fit_space(cam, [O3, (1.5, 0, 0), (0, 6.8, 0), (0, 0, 6.8)], 700, (60, 110, 40, 40))
S.polygon([(0, 0, 0), (0, 6.5, 0), (0, 6.5, 6.5), (0, 0, 6.5)], TEXT, 0.05)
axes3(S, AX)
S.line([O3, (0, 6.5, 6.5)], TEXT, 1.1, "5 4", 0.55)
m = arc3(S, O3, (0, 1, 0), (0, 1, 1), 2.3, TEXT, 1.4)
arc_label3(S, O3, m, f"{PI_T}/4", 5, TEXT, S_PT)
specs = ((6, 0.0, Z_, BASE, 2.0, 10), (3, 0.0, Y_, PRACTICE, 3.0, 11), (1, 0.0, X_, THEORY, 4.2, 12))
for L, dx, nm, col, wd, hd in specs:
    S.arrow((dx, 0, 0), (dx, L, L), col, wd, hd)
for L, dx, nm, col, wd, hd in specs:
    tip3 = (dx, L, L)
    near3(S, tip3, f"(0, {L}, {L})", "lr", 6, TEXT, S_NOTE)
    along3(S, (dx, 0, 0), tip3, nm, "ul", t=0.88 if L > 1 else 0.7, color=col)
S.point(O3, TEXT, 3.0)
OUT["paralel-ii"] = figure(
    700, H, [p],
    "<em>x</em> = (0, 1, 1), <em>y</em> = (0, 3, 3), <em>z</em> = (0, 6, 6) <em>YZ</em>-düzleminde, "
    "<em>y</em> = <em>z</em> açıortay doğrusu üzerindedir; bu doğru <em>Y</em>-ekseniyle &#960;/4 açı yapar. "
    "Kısa oklar uzunların üstüne daha kalın çizilmiştir.",
    css_class=WIDE,
    aria="Axes X, Y, Z with the faint square of the YZ-plane, its diagonal y = z and three arrows along it of lengths 1, 3, 6 times (0, 1, 1)")


save_all()
