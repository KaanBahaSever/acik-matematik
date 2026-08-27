# -*- coding: utf-8 -*-
"""
Generates the SVG figures used in the "Konveks Analiz" (Convex Analysis)
chapters.

The figures are NOT produced at build time: run this script, then
scripts/center_figures.py (which measures each drawing and centers it in its
viewBox), and paste the resulting markup into the .qmd files. A drawing
belongs INSIDE the theorem / proof / example / solution box it illustrates;
definition boxes never hold one — their figure goes right below the box.

The captions are Turkish on purpose — they are the text shown on the site.

Usage:   python scripts/convex_figures.py && python scripts/center_figures.py "convex-*.md"
Output:  scripts/_figures/convex-<name>.md
"""
import io
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8")
from svg_plot import *  # noqa: E402,F403 — Plot, figure, colors, cplane, blob, disk_fill, ...

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_figures")
os.makedirs(OUT_DIR, exist_ok=True)
OUT = {}

PI = math.pi
DEG = PI / 180.0

# Symbols that appear inside <text>; the rest of the labels are plain UTF-8.
LEQ, GEQ, IN, NOTIN = "&#8804;", "&#8805;", "&#8712;", "&#8713;"
INFTY, MINUS, CDOT, TIMES = "&#8734;", "&#8722;", "&#183;", "&#215;"
LANG, RANG, PERP, LAMBDA = "&#10216;", "&#10217;", "&#8869;", "&#955;"
ALPHA, THETA, EPS, DELTA = "&#945;", "&#952;", "&#949;", "&#948;"
DELTA_CAP = "&#916;"      # öncü esas minörler metinde büyük delta ile yazılır
SUB0, SUB1, SUB2, SUB3, SUBN = "&#8320;", "&#8321;", "&#8322;", "&#8323;", "&#8345;"
SUBK, SUBM, SUBI = "&#8342;", "&#8344;", "&#7522;"
CUP, CAP, SUBSET, EMPTY = "&#8746;", "&#8745;", "&#8834;", "&#8709;"
ARROW, NEQ, APPROX, PLUSMIN = "&#8594;", "&#8800;", "&#8776;", "&#177;"

# The panel is a plain slice of R^n, so both axes carry the same scale.
panel = cplane


# ---------------------------------------------------------------------------
# Drawing helpers shared by the whole file
# ---------------------------------------------------------------------------
def rect(x0, y0, x1, y1):
    """Corner points of an axis-aligned rectangle, counter-clockwise."""
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def region(p, pts, color=THEORY, fill_op=0.13, width=1.9, dash=None, opacity=1.0):
    """Filled polygon with its boundary drawn; dash it when the set is open."""
    p.polygon(pts, color, fill_op, stroke="none")
    p.line(list(pts) + [pts[0]], color, width, dash, opacity)


def ball(p, c, r, color=BASE, fill_op=0.15, dash=None, width=1.5):
    """Disk |x - c| < r (dashed boundary) or <= r (solid)."""
    disk_fill(p, c[0], c[1], r, color, fill_op)
    p.circle(c[0], c[1], r, color, width, dash)


def right_angle(p, o, d1, d2, size=0.3, color=TEXT, width=1.2, opacity=0.75):
    """Small square marking a right angle at o, between directions d1 and d2."""
    def unit(d):
        n = math.hypot(*d) or 1.0
        return (d[0] / n * size, d[1] / n * size)
    u, v = unit(d1), unit(d2)
    pts = [o, (o[0] + u[0], o[1] + u[1]),
           (o[0] + u[0] + v[0], o[1] + u[1] + v[1]), (o[0] + v[0], o[1] + v[1])]
    p.line([pts[1], pts[2], pts[3]], color, width, None, opacity)


def seg(p, a, b, color=THEORY, width=2.0, dash=None, opacity=1.0):
    p.line([a, b], color, width, dash, opacity)


def _pbox(p, pad=0.25):
    """The panel's data window, slightly enlarged so strokes reach the edge."""
    return (p.xmin - pad, p.ymin - pad, p.xmax + pad, p.ymax + pad)


def clip_seg(a, b, box):
    """Liang-Barsky: the part of the segment a-b inside box, or None."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    t0, t1 = 0.0, 1.0
    for num, den in ((-dx, a[0] - box[0]), (dx, box[2] - a[0]),
                     (-dy, a[1] - box[1]), (dy, box[3] - a[1])):
        if abs(num) < 1e-12:
            if den < 0:
                return None
            continue
        r = den / num
        if num < 0:
            if r > t1:
                return None
            t0 = max(t0, r)
        else:
            if r < t0:
                return None
            t1 = min(t1, r)
    return ((a[0] + t0 * dx, a[1] + t0 * dy), (a[0] + t1 * dx, a[1] + t1 * dy))


def clip_poly(pts, box):
    """Sutherland-Hodgman: the part of a polygon inside box."""
    def cut(a, b, axis, lim):
        t = (lim - a[axis]) / (b[axis] - a[axis])
        return (a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1]))

    out = list(pts)
    for axis, lim, keep_above in ((0, box[0], True), (0, box[2], False),
                                  (1, box[1], True), (1, box[3], False)):
        if not out:
            break
        cur, out = out, []
        for i, q in enumerate(cur):
            r = cur[i - 1]
            iq = q[axis] >= lim if keep_above else q[axis] <= lim
            ir = r[axis] >= lim if keep_above else r[axis] <= lim
            if iq:
                if not ir:
                    out.append(cut(r, q, axis, lim))
                out.append(q)
            elif ir:
                out.append(cut(r, q, axis, lim))
    return out


def extreme(poly, ang):
    """The point of a polygon that is farthest in the direction of the angle ang."""
    c, s_ = math.cos(ang), math.sin(ang)
    return max(poly, key=lambda q: q[0] * c + q[1] * s_)


def pseg(p, a, b, color=THEORY, width=2.0, dash=None, opacity=1.0, pad=0.25):
    """Segment drawn only where it stays inside the panel."""
    cut = clip_seg(a, b, _pbox(p, pad))
    if cut:
        p.line(list(cut), color, width, dash, opacity)


def wedge(p, o, a0, a1, r, color=THEORY, fill_op=0.14, width=1.9, samples=48):
    """Filled angular sector at o between the angles a0 and a1 (radians)."""
    pts = [o] + [(o[0] + r * math.cos(a0 + (a1 - a0) * k / samples),
                  o[1] + r * math.sin(a0 + (a1 - a0) * k / samples)) for k in range(samples + 1)]
    shade = clip_poly(pts, _pbox(p))
    if shade:
        p.polygon(shade, color, fill_op, stroke="none")
    pseg(p, o, pts[1], color, width)
    pseg(p, o, pts[-1], color, width)


def hyperline(p, a, b, color=THEORY, width=2.0, dash=None, opacity=1.0, pad=0.25):
    """The line (hyperplane in R^2) {x : <a,x> = b}, clipped to the panel."""
    n2 = a[0] ** 2 + a[1] ** 2
    foot = (a[0] * b / n2, a[1] * b / n2)             # doğrunun orijine en yakın noktası
    d = (-a[1] / math.sqrt(n2), a[0] / math.sqrt(n2))  # doğrultu vektörü
    box = _pbox(p, pad)
    span = 2 * ((box[2] - box[0]) + (box[3] - box[1]))
    pseg(p, (foot[0] - d[0] * span, foot[1] - d[1] * span),
         (foot[0] + d[0] * span, foot[1] + d[1] * span), color, width, dash, opacity, pad)


def halfplane(p, a, b, side=-1, color=THEORY, fill_op=0.12, width=2.0, dash=None):
    """Shade {x : <a,x> <= b} (side=-1) or {x : <a,x> >= b} (side=+1).

    The boundary line <a,x> = b is drawn across the whole panel; the shading is
    the panel rectangle clipped against that line.
    """
    x0, y0, x1, y1 = _pbox(p, 0.25)
    corners = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]

    def val(q):
        return a[0] * q[0] + a[1] * q[1] - b

    def inside(q):
        return val(q) <= 0 if side < 0 else val(q) >= 0

    keep = []
    for i in range(4):
        q, r = corners[i], corners[(i + 1) % 4]
        iq, ir = inside(q), inside(r)
        if iq:
            keep.append(q)
        if iq != ir:                       # kenar sınır doğrusunu kesiyor
            vq, vr = val(q), val(r)
            t = vq / (vq - vr)
            keep.append((q[0] + t * (r[0] - q[0]), q[1] + t * (r[1] - q[1])))
    if keep:
        p.polygon(keep, color, fill_op, stroke="none")
    hyperline(p, a, b, color, width, dash)


def curve(f, x0, x1, n=180):
    """Sample y = f(x) on [x0, x1] as a list of data points."""
    return [(x0 + (x1 - x0) * k / n, f(x0 + (x1 - x0) * k / n)) for k in range(n + 1)]


def numline(p, y, x0, x1, ticks=(), labels=(), color=TEXT, opacity=0.55):
    """A real axis drawn at height y with arrowheads at both ends."""
    p.line([(x0, y), (x1, y)], color, 1.2, None, opacity)
    p.arrow((x1 - 0.25, y), (x1, y), color, 1.2, head=7.0, opacity=opacity)
    p.arrow((x0 + 0.25, y), (x0, y), color, 1.2, head=7.0, opacity=opacity)
    for t, s in zip(ticks, labels):
        p.line([(t, y - 0.09), (t, y + 0.09)], color, 1.1, None, 0.7)
        p.label(t, y, s, 0, 20, color, 11, "middle")


def bracket(p, a, b, y, color=THEORY, width=3.2, left_closed=True, right_closed=True, r=4.2):
    """An interval on the real axis: filled dot = endpoint included."""
    p.line([(a, y), (b, y)], color, width)
    for x, closed in ((a, left_closed), (b, right_closed)):
        if closed:
            p.points([(x, y)], color, r)
        else:
            p.add(f'<circle cx="{p.X(x):.1f}" cy="{p.Y(y):.1f}" r="{r}" fill="{BG}" '
                  f'stroke="{color}" stroke-width="1.9"/>')


def runs_in(pts, p):
    """Split a polyline into the runs that stay inside a panel's data window."""
    out, cur = [], []
    for q in pts:
        if p.xmin <= q[0] <= p.xmax and p.ymin <= q[1] <= p.ymax:
            cur.append(q)
        else:
            if len(cur) > 1:
                out.append(cur)
            cur = []
    if len(cur) > 1:
        out.append(cur)
    return out


def hull(pts):
    """Convex hull of a point list (Andrew's monotone chain), counter-clockwise."""
    pts = sorted(set((round(x, 9), round(y, 9)) for x, y in pts))
    if len(pts) < 3:
        return list(pts)

    def half(seq):
        out = []
        for q in seq:
            while len(out) >= 2:
                (ax, ay), (bx, by) = out[-2], out[-1]
                if (bx - ax) * (q[1] - ay) - (by - ay) * (q[0] - ax) <= 0:
                    out.pop()
                else:
                    break
            out.append(q)
        return out

    lower, upper = half(pts), half(pts[::-1])
    return lower[:-1] + upper[:-1]


def offset_polygon(pts, r, samples=14):
    """Minkowski sum of a counter-clockwise convex polygon with a disk of radius r."""
    n = len(pts)
    out = []
    for i in range(n):
        q, s_ = pts[i], pts[(i + 1) % n]
        e = (s_[0] - q[0], s_[1] - q[1])
        ln = math.hypot(*e) or 1.0
        nrm = (e[1] / ln, -e[0] / ln)                 # dışa doğru normal
        out.append((q[0] + r * nrm[0], q[1] + r * nrm[1]))
        out.append((s_[0] + r * nrm[0], s_[1] + r * nrm[1]))
        # köşeyi yay ile yuvarla
        t = pts[(i + 2) % n]
        e2 = (t[0] - s_[0], t[1] - s_[1])
        ln2 = math.hypot(*e2) or 1.0
        nrm2 = (e2[1] / ln2, -e2[0] / ln2)
        a0, a1 = math.atan2(nrm[1], nrm[0]), math.atan2(nrm2[1], nrm2[0])
        while a1 < a0:
            a1 += 2 * PI
        out += [(s_[0] + r * math.cos(a0 + (a1 - a0) * k / samples),
                 s_[1] + r * math.sin(a0 + (a1 - a0) * k / samples)) for k in range(1, samples)]
    return out


def radial_boundary(c, inside, rmax=8.0, samples=200, steps=40):
    """Boundary of a region that is star-shaped about c, found by bisection along rays."""
    out = []
    for k in range(samples):
        th = 2 * PI * k / samples
        lo, hi = 0.0, rmax
        for _ in range(steps):
            mid = 0.5 * (lo + hi)
            if inside((c[0] + mid * math.cos(th), c[1] + mid * math.sin(th))):
                lo = mid
            else:
                hi = mid
        out.append((c[0] + lo * math.cos(th), c[1] + lo * math.sin(th)))
    return out


# ############################################################################
# PART 1 — Giriş  (R^n: iç çarpım, norm, topoloji, kompaktlık)
# ############################################################################

# ============================================================ iç çarpım ve açı
x_v, y_v = (3.4, 0.9), (1.1, 2.5)
nx = math.hypot(*x_v)
proj = (x_v[0] / nx, x_v[1] / nx)
t_pr = (x_v[0] * y_v[0] + x_v[1] * y_v[1]) / nx          # ||y|| cos(theta)
foot = (proj[0] * t_pr, proj[1] * t_pr)

p1 = panel(34, 42, 292, (-0.75, 4.15), (-0.55, 3.15))
p1.origin_axes(xlabel="", ylabel="")
p1.arrow((0, 0), x_v, THEORY, 2.2)
p1.arrow((0, 0), y_v, PRACTICE, 2.2)
seg(p1, y_v, foot, TEXT, 1.2, "4 3", 0.6)
right_angle(p1, foot, (y_v[0] - foot[0], y_v[1] - foot[1]), (-proj[0], -proj[1]), 0.22)
seg(p1, (0, 0), foot, BASE, 3.0)
p1.arc(0, 0, 0.95, math.atan2(x_v[1], x_v[0]), math.atan2(y_v[1], y_v[0]), REMARK, 1.5)
p1.label(0.72, 0.62, THETA, 6, 2, REMARK, 12.5, "start", True, True)
p1.label(*x_v, "x", 8, 10, THEORY, 13, "start", True, True)
p1.label(*y_v, "y", 2, -9, PRACTICE, 13, "start", True, True)
p1.label(foot[0], foot[1], "&#8214;y&#8214; cos " + THETA, 4, 20, BASE, 11.5, "middle", True)
panel_title(p1, "genel durum", TEXT, 11.5)

xo, yo = (3.1, 0.85), (-0.85, 3.1)                        # <xo, yo> = -2.635 + 2.635 = 0
p2 = panel(378, 42, 292, (-1.55, 3.35), (-0.55, 3.15))
p2.origin_axes(xlabel="", ylabel="")
p2.arrow((0, 0), xo, THEORY, 2.2)
p2.arrow((0, 0), yo, PRACTICE, 2.2)
right_angle(p2, (0, 0), xo, yo, 0.36)
p2.label(*xo, "x", 8, 10, THEORY, 13, "start", True, True)
p2.label(*yo, "y", -8, -6, PRACTICE, 13, "end", True, True)
p2.text(0.35, 2.55, LANG + "x, y" + RANG + " = 0", PRACTICE, 12, "start", True)
panel_title(p2, "dik (ortogonal) vektörler", TEXT, 11.5)

OUT["ic-carpim-aci"] = figure(
    700, 330, [p1, p2],
    "İç çarpım iki vektör arasındaki açıyı ölçer: &#10216;x, y&#10217; = &#8214;x&#8214; " + CDOT +
    " &#8214;y&#8214; " + CDOT + " cos " + THETA + ". Solda <em>y</em>'nin <em>x</em> yönündeki dik izdüşümü "
    "&#8214;y&#8214; cos " + THETA + " uzunluğundadır; iç çarpım bu uzunluğun &#8214;x&#8214; katıdır. "
    "Sağda açı 90&#176; olduğundan kosinüs sıfırdır: iç çarpımın sıfır olması ile diklik aynı şeydir.",
    css_class=WIDE, aria="Ic carpim ve aci; ortogonal vektorler")

# ======================================================== üçgen eşitsizliği
a_v, b_v = (2.5, 0.55), (0.85, 2.15)
s_v = (a_v[0] + b_v[0], a_v[1] + b_v[1])
p1 = panel(34, 46, 286, (-0.55, 4.15), (-0.5, 3.25))
p1.origin_axes(xlabel="", ylabel="")
p1.arrow((0, 0), a_v, THEORY, 2.1)
p1.arrow(a_v, s_v, PRACTICE, 2.1)
p1.arrow((0, 0), s_v, BASE, 2.4)
p1.arrow((0, 0), b_v, PRACTICE, 1.5, dash="5 4", opacity=0.55)
p1.label(*a_v, "x", 2, 18, THEORY, 12.5, "middle", True, True)
p1.label(a_v[0] + b_v[0] / 2, a_v[1] + b_v[1] / 2, "y", 10, 2, PRACTICE, 12.5, "start", True, True)
p1.label(*s_v, "x + y", -4, -8, BASE, 12.5, "end", True, True)
p1.text(0.15, 2.9, "&#8214;x + y&#8214; &lt; &#8214;x&#8214; + &#8214;y&#8214;", BASE, 12, "start", True)
panel_title(p1, "aynı doğrultuda değil", TEXT, 11.5)

a2 = (2.15, 1.15)
b2 = (a2[0] * 0.72, a2[1] * 0.72)
s2 = (a2[0] + b2[0], a2[1] + b2[1])
p2 = panel(372, 46, 286, (-0.55, 4.15), (-0.5, 3.25))
p2.origin_axes(xlabel="", ylabel="")
p2.arrow((0, 0), a2, THEORY, 2.1)
p2.arrow(a2, s2, PRACTICE, 2.1)
p2.label(a2[0] / 2, a2[1] / 2, "x", 4, -8, THEORY, 12.5, "middle", True, True)
p2.label(a2[0] + b2[0] / 2, a2[1] + b2[1] / 2, "y = " + ALPHA + "x", 6, -8, PRACTICE, 12.5, "start", True, True)
p2.points([s2], BASE, 4.2)
p2.text(0.15, 2.9, "&#8214;x + y&#8214; = &#8214;x&#8214; + &#8214;y&#8214;", BASE, 12, "start", True)
panel_title(p2, "aynı yönde: eşitlik hâli", TEXT, 11.5)

OUT["ucgen-esitsizligi"] = figure(
    690, 330, [p1, p2],
    "Üçgen eşitsizliği &#8214;x + y&#8214; " + LEQ + " &#8214;x&#8214; + &#8214;y&#8214;: iki kenar üzerinden "
    "dolaşmak, doğrudan gitmekten kısa olamaz. Eşitlik yalnızca sağdaki gibi <em>x</em> ile <em>y</em> aynı "
    "yöne baktığında, yani bir " + ALPHA + " " + GEQ + " 0 için <em>x</em> = " + ALPHA + "<em>y</em> olduğunda "
    "gerçekleşir; üçgen yassılıp doğru parçasına dönüşür.",
    css_class=WIDE, aria="Ucgen esitsizligi ve esitlik hali")

# ================================================================ komşuluklar
def _nb_panel(x0, title, dash, punctured):
    q = panel(x0, 50, 196, (-1.85, 1.85), (-1.85, 1.85))
    q.origin_axes(xlabel="", ylabel="", opacity=0.32)
    ball(q, (0, 0), 1.25, THEORY, 0.15, dash, 1.9)
    if punctured:
        hollow(q, (0, 0), TEXT, 4.0, 1.8)
    else:
        q.points([(0, 0)], TEXT, 3.4)
    q.label(0, 0, "a", -7, -7, TEXT, 12, "end", True, True)
    seg(q, (0, 0), (1.25 * math.cos(0.9), 1.25 * math.sin(0.9)), REMARK, 1.4, "4 3", 0.85)
    q.label(0.62 * math.cos(0.9), 0.62 * math.sin(0.9), "r", 7, -3, REMARK, 11.5, "start", True, True)
    panel_title(q, title, TEXT, 11.5)
    return q

q1 = _nb_panel(26, "B(a, r) — açık", "5 4", False)
q2 = _nb_panel(258, "B&#772;(a, r) — kapalı", None, False)
q3 = _nb_panel(490, "B*(a, r) — delinmiş", "5 4", True)
OUT["komsuluklar"] = figure(
    710, 300, [q1, q2, q3],
    "Bir <em>a</em> noktasının <em>r</em> yarıçaplı üç komşuluğu. Kesikli çember, çemberin kümeye "
    "<strong>ait olmadığını</strong> gösterir: açık komşulukta &#8214;x " + MINUS + " a&#8214; &lt; r, kapalı "
    "komşulukta &#8214;x " + MINUS + " a&#8214; " + LEQ + " r aranır. Delinmiş komşuluk açık komşuluktan "
    "merkezin çıkarılmasıyla elde edilir; yığılma noktası tanımında tam olarak bu küme kullanılır.",
    css_class=WIDE, aria="Acik, kapali ve delinmis komsuluklar")

# ================================================== iç, sınır ve dış noktalar
A_blob = blob(0.0, 0.05, 1.55, [(0.30, 2, 0.6), (0.18, 3, 2.1)])
p = panel(40, 44, 330, (-2.9, 3.5), (-2.5, 2.5))
region(p, A_blob, THEORY, 0.12, 2.0)
ic = (-0.35, 0.15)
ball(p, ic, 0.5, BASE, 0.20, None, 1.4)
p.points([ic], BASE, 3.6)
p.label(*ic, "iç nokta", -2, 30, BASE, 11.5, "middle", True)

# a boundary point: put it exactly on the blob curve
sn = A_blob[len(A_blob) * 7 // 24]
ball(p, sn, 0.5, PRACTICE, 0.20, None, 1.4)
p.points([sn], PRACTICE, 3.6)
p.label(sn[0], sn[1], "sınır noktası", 10, -16, PRACTICE, 11.5, "start", True)

dis = (2.55, -1.5)
ball(p, dis, 0.45, REMARK, 0.20, None, 1.4)
p.points([dis], REMARK, 3.6)
p.label(*dis, "dış nokta", 0, 30, REMARK, 11.5, "middle", True)
p.label(-2.1, -1.75, "A", 0, 0, THEORY, 14, "middle", True, True)
OUT["ic-sinir-dis"] = figure(
    420, 300, [p],
    "Bir <em>A</em> kümesine göre üç tür nokta. İç noktanın tamamen <em>A</em>'da kalan bir komşuluğu vardır; "
    "dış noktanın <em>A</em>'ya hiç değmeyen bir komşuluğu vardır; sınır noktasının ise <strong>her</strong> "
    "komşuluğu hem <em>A</em>'dan hem de <em>A</em> dışından nokta içerir. int<em>A</em> tüm iç noktaların, "
    "bd<em>A</em> tüm sınır noktalarının kümesidir.",
    aria="Ic, sinir ve dis noktalari")

# ============================================== kapanış ve yığılma noktaları
iso = (2.45, 1.15)
p1 = panel(30, 48, 300, (-2.1, 3.35), (-2.1, 2.1))
p1.origin_axes(xlabel="", ylabel="", opacity=0.28)
disk_fill(p1, 0, 0, 1.55, THEORY, 0.13)
p1.circle(0, 0, 1.55, THEORY, 2.0, "5 4")
hollow(p1, (0, 0), THEORY, 4.0, 1.8)
p1.points([iso], PRACTICE, 4.4)
p1.label(*iso, "q", 9, -6, PRACTICE, 12.5, "start", True, True)
p1.label(0, 0, "0", -9, -6, THEORY, 11.5, "end", True)
p1.label(-1.15, -1.3, "A", 0, 0, THEORY, 14, "middle", True, True)
panel_title(p1, "A = {0 &lt; &#8214;x&#8214; &lt; 1} " + CUP + " {q}", TEXT, 11.5)

p2 = panel(382, 48, 300, (-2.1, 3.35), (-2.1, 2.1))
p2.origin_axes(xlabel="", ylabel="", opacity=0.28)
disk_fill(p2, 0, 0, 1.55, THEORY, 0.10)
p2.circle(0, 0, 1.55, PRACTICE, 2.4)
p2.points([(0, 0)], PRACTICE, 4.4)
p2.points([iso], PRACTICE, 4.4)
p2.label(*iso, "q", 9, -6, PRACTICE, 12.5, "start", True, True)
p2.label(0, 0, "0", -9, -6, PRACTICE, 11.5, "end", True)
p2.text(-2.0, -1.85, "bd A: çember, 0 ve q", PRACTICE, 11.5, "start", True)
panel_title(p2, "A&#772; = kapalı disk " + CUP + " {q}", TEXT, 11.5)

OUT["kapanis-yigilma"] = figure(
    712, 320, [p1, p2],
    "Delinmiş açık disk ile ondan uzakta duran tek bir <em>q</em> noktasının birleşimi. Yığılma noktalarının "
    "kümesi kapalı disktir: <em>q</em> yalıtılmış olduğundan yığılma noktası <strong>değildir</strong>, buna "
    "karşılık kümeye ait olmayan 0 bir yığılma noktasıdır. Kapanış A&#772; = A " + CUP + " Yığ<em>A</em> "
    "olduğundan sağdaki kümeyi verir; sınır ise A&#772; \\ int<em>A</em>, yani çember ile 0 ve <em>q</em> "
    "noktalarıdır.",
    css_class=WIDE, aria="Kapanis, yigilma noktalari ve sinir")

# =========================================================== açık / kapalı / ne o ne bu
q1 = panel(24, 50, 200, (-1.9, 1.9), (-1.9, 1.9))
disk_fill(q1, 0, 0, 1.35, THEORY, 0.14)
q1.circle(0, 0, 1.35, THEORY, 2.1, "5 4")
q1.text(0, -1.72, "&#8214;x&#8214; &lt; 1", THEORY, 12, "middle", True)
panel_title(q1, "açık", TEXT, 11.5)

q2 = panel(256, 50, 200, (-1.9, 1.9), (-1.9, 1.9))
disk_fill(q2, 0, 0, 1.35, BASE, 0.14)
q2.circle(0, 0, 1.35, BASE, 2.4)
q2.text(0, -1.72, "&#8214;x&#8214; " + LEQ + " 1", BASE, 12, "middle", True)
panel_title(q2, "kapalı", TEXT, 11.5)

q3 = panel(488, 50, 200, (-1.9, 1.9), (-1.9, 1.9))
disk_fill(q3, 0, 0, 1.35, PRACTICE, 0.14)
q3.circle(0, 0, 1.35, PRACTICE, 2.4)
hollow(q3, (0, 0), PRACTICE, 4.2, 1.9)
q3.text(0, -1.72, "0 &lt; &#8214;x&#8214; " + LEQ + " 1", PRACTICE, 12, "middle", True)
panel_title(q3, "ne açık ne kapalı", TEXT, 11.5)

OUT["acik-kapali-kume"] = figure(
    714, 300, [q1, q2, q3],
    "Açık küme sınırının hiçbir noktasını, kapalı küme tümünü içerir. Üçüncü küme ikisi de değildir: çemberi "
    "içerdiğinden açık değildir (çember üzerindeki noktalar iç nokta olamaz), sınır noktası olan 0'ı "
    "içermediğinden kapalı değildir. Açıklık ile kapalılık birbirinin zıddı değil, tümleyen üzerinden "
    "tanımlanan iki ayrı özelliktir.",
    css_class=WIDE, aria="Acik, kapali ve ne acik ne kapali kumeler")

# ================================================================ A + B toplamı
# Panel 1: doğru parçası + doğru parçası = paralelkenar
Aseg = [(0.0, 0.0), (0.75, 1.65)]
Bseg = [(0.0, 0.0), (1.9, 0.0)]
p1 = panel(34, 54, 300, (-0.7, 3.55), (-1.15, 2.4))
p1.origin_axes(xlabel="", ylabel="", opacity=0.3)
para = [(0, 0), (1.9, 0), (2.65, 1.65), (0.75, 1.65)]
p1.polygon(para, PRACTICE, 0.16, stroke="none")
p1.line(para + [para[0]], PRACTICE, 2.1)
for t in (0.0, 0.25, 0.5, 0.75, 1.0):
    o = (Aseg[1][0] * t, Aseg[1][1] * t)
    seg(p1, o, (o[0] + Bseg[1][0], o[1] + Bseg[1][1]), PRACTICE, 1.0, "3 3", 0.5)
seg(p1, *Aseg, color=THEORY, width=3.4)
seg(p1, (0.0, -0.72), (1.9, -0.72), BASE, 3.4)
p1.label(0.34, 0.9, "A", -10, 0, THEORY, 13, "end", True, True)
p1.label(0.95, -0.72, "B", 0, 20, BASE, 13, "middle", True, True)
p1.label(1.7, 0.85, "A + B", 0, 0, PRACTICE, 13, "middle", True, True)
panel_title(p1, "iki doğru parçası", TEXT, 11.5)

# Panel 2: kare + disk = köşeleri yuvarlatılmış kare
p2 = panel(382, 54, 300, (-1.35, 2.9), (-1.6, 1.95))
p2.origin_axes(xlabel="", ylabel="", opacity=0.3)
rr = 0.5
sq = rect(0.0, 0.0, 1.25, 1.25)
rounded = []
for (cx, cy), a0 in ((sq[1], -0.5 * PI), (sq[2], 0.0), (sq[3], 0.5 * PI), (sq[0], PI)):
    rounded += circle_pts(cx, cy, rr, a0, a0 + 0.5 * PI, 20)
p2.polygon(rounded, PRACTICE, 0.16, stroke="none")
p2.line(rounded + [rounded[0]], PRACTICE, 2.1)
region(p2, sq, THEORY, 0.20, 2.0)
ball(p2, (-0.78, -1.05), rr, BASE, 0.22, None, 2.0)
p2.points([(-0.78, -1.05)], BASE, 3.0)
p2.label(0.62, 0.62, "A", 0, 5, THEORY, 13, "middle", True, True)
p2.label(-0.78, -1.05, "B", 0, 30, BASE, 13, "middle", True, True)
p2.label(1.72, 1.5, "A + B", 0, 0, PRACTICE, 13, "middle", True, True)
panel_title(p2, "kare ve disk", TEXT, 11.5)

OUT["kume-toplami"] = figure(
    712, 350, [p1, p2],
    "Kümelerin toplamı A + B = { x + y : x " + IN + " A, y " + IN + " B }, B kümesinin A'nın her noktasına "
    "ötelenmesiyle taranan bölgedir. Solda iki doğru parçasının toplamı bir paralelkenar, sağda bir kare ile "
    "diskin toplamı köşeleri yuvarlatılmış bir karedir: disk ile toplamak, kümeyi yarıçap kadar her yöne "
    "kalınlaştırmak demektir.",
    css_class=WIDE, aria="Iki kumenin toplami: paralelkenar ve yuvarlatilmis kare")

# ================================================= sınırlı dizi ve yakınsak alt dizi
pts_all = [(-1.55, 1.35), (1.72, -1.42), (-0.35, -1.66), (1.95, 1.15), (-1.82, -0.42),
           (0.95, 1.78), (-1.05, -1.15), (1.35, 0.15), (-1.68, 0.62), (0.25, -1.32),
           (1.55, 1.72), (-0.85, 1.62), (1.05, -1.78), (-1.42, -1.58), (0.55, 0.95)]
limit = (0.62, 0.28)
sub = [(limit[0] + 1.15 * math.cos(0.7 * k), limit[1] + 1.15 * math.sin(0.7 * k))
       for k in range(6)]
sub = [(limit[0] + (q[0] - limit[0]) * 0.62 ** k, limit[1] + (q[1] - limit[1]) * 0.62 ** k)
       for k, q in enumerate(sub)]
p = panel(44, 46, 320, (-2.5, 2.5), (-2.35, 2.35))
region(p, rect(-2.1, -2.1, 2.1, 2.1), REMARK, 0.07, 1.4, "6 5")
p.points(pts_all, TEXT, 3.0)
p.line(sub, PRACTICE, 1.4, "4 3", 0.75)
p.points(sub, PRACTICE, 4.2)
p.points([limit], BASE, 5.0)
p.label(*limit, "x" + SUB0, 11, 5, BASE, 12.5, "start", True, True)
p.label(*sub[0], "x" + SUBK + SUB1, 8, -8, PRACTICE, 11.5, "start", True, True)
p.label(*sub[1], "x" + SUBK + SUB2, -8, -6, PRACTICE, 11.5, "end", True, True)
p.label(-2.1, 2.1, "&#8214;x" + SUBK + "&#8214; " + LEQ + " M", 4, -8, REMARK, 11.5, "start", True)
OUT["bolzano-weierstrass"] = figure(
    420, 340, [p],
    "Bolzano-Weierstrass teoremi. Dizinin bütün terimleri &#8214;x" + SUBK + "&#8214; " + LEQ + " M "
    "kutusunda sıkıştığından, sonsuz sayıda terim aynı bölgede yığılmak zorundadır; bunlardan seçilen alt dizi "
    "bir x" + SUB0 + " noktasına yakınsar. Dizinin kendisi yakınsamayabilir — teorem yalnızca <em>bir</em> "
    "yakınsak alt dizinin varlığını söyler.",
    aria="Sinirli dizinin yakinsak alt dizisi")

# ============================================================== kompaktlık
q1 = panel(24, 52, 198, (-2.3, 2.3), (-2.3, 2.3))
region(q1, blob(0, 0, 1.5, [(0.26, 3, 0.4)]), BASE, 0.15, 2.3)
q1.text(0, -2.08, "kapalı ve sınırlı", BASE, 11.5, "middle", True)
panel_title(q1, "kompakt", TEXT, 11.5)

q2 = panel(256, 52, 198, (-2.3, 2.3), (-2.3, 2.3))
strip = [(-2.5, -0.85), (2.5, -0.85), (2.5, 0.85), (-2.5, 0.85)]
q2.polygon(strip, PRACTICE, 0.13, stroke="none")
q2.line([(-2.5, -0.85), (2.5, -0.85)], PRACTICE, 2.2)
q2.line([(-2.5, 0.85), (2.5, 0.85)], PRACTICE, 2.2)
q2.arrow((1.7, 0.0), (2.45, 0.0), PRACTICE, 1.5, head=7.0)
q2.arrow((-1.7, 0.0), (-2.45, 0.0), PRACTICE, 1.5, head=7.0)
q2.text(0, -2.08, "sınırlı değil", PRACTICE, 11.5, "middle", True)
panel_title(q2, "kompakt değil", TEXT, 11.5)

q3 = panel(488, 52, 198, (-2.3, 2.3), (-2.3, 2.3))
disk_fill(q3, 0, 0, 1.5, PRACTICE, 0.14)
q3.circle(0, 0, 1.5, PRACTICE, 2.2, "5 4")
q3.text(0, -2.08, "kapalı değil", PRACTICE, 11.5, "middle", True)
panel_title(q3, "kompakt değil", TEXT, 11.5)

OUT["kompakt-kume"] = figure(
    714, 310, [q1, q2, q3],
    "R<sup>n</sup> uzayında kompaktlık, kapalılık ile sınırlılığın birlikte sağlanmasıdır "
    "(Heine-Borel). Ortadaki şerit kapalıdır ama sınırlı değildir; sağdaki açık disk sınırlıdır ama kapalı "
    "değildir — her ikisinde de sınıra doğru giden bir dizi kurulabilir, oysa limit kümede yoktur.",
    css_class=WIDE, aria="Kompakt kume ile kompakt olmayan iki ornek")

# ==================================================== Weierstrass varlık teoremi
def _wf(x):
    return 0.45 * (x - 1.1) ** 2 + 0.55


p1 = Plot(46, 44, 268, 196, (-0.28, 2.95), (0.25, 1.85))
p1.axes([0, 1, 2], [0.5, 1.0, 1.5], "x", "f(x)")
p1.line(curve(_wf, 0.0, 2.6), THEORY, 2.2)
p1.vline(0.0, 0.25, _wf(0.0), REMARK, "4 3", 0.45)
p1.vline(2.6, 0.25, _wf(2.6), REMARK, "4 3", 0.45)
p1.points([(1.1, _wf(1.1)), (2.6, _wf(2.6))], PRACTICE, 4.6)
p1.label(1.1, _wf(1.1), "en küçük değer", 0, 20, PRACTICE, 11, "middle", True)
p1.label(2.6, _wf(2.6), "en büyük değer", -6, -10, PRACTICE, 11, "end", True)
p1.label(0.0, 0.25, "a", 0, 17, TEXT, 11.5, "middle", False, True)
p1.label(2.6, 0.25, "b", 0, 17, TEXT, 11.5, "middle", False, True)
panel_title(p1, "K = [a, b] kompakt", TEXT, 11.5)

p2 = Plot(392, 44, 268, 196, (-0.28, 2.95), (0.25, 1.85))
p2.axes([0, 1, 2], [0.5, 1.0, 1.5], "x", "f(x)")
p2.line(curve(_wf, 0.0, 2.6), THEORY, 2.2)
p2.vline(0.0, 0.25, _wf(0.0), REMARK, "4 3", 0.45)
p2.vline(2.6, 0.25, _wf(2.6), REMARK, "4 3", 0.45)
p2.hollow_points([(0.0, _wf(0.0)), (2.6, _wf(2.6))], PRACTICE, 4.6)
p2.points([(1.1, _wf(1.1))], PRACTICE, 4.6)
p2.label(1.1, _wf(1.1), "en küçük değer alınır", 0, 20, PRACTICE, 11, "middle", True)
p2.label(2.6, _wf(2.6), "en büyük değer yok", -6, -10, PRACTICE, 11, "end", True)
p2.label(0.0, 0.25, "a", 0, 17, TEXT, 11.5, "middle", False, True)
p2.label(2.6, 0.25, "b", 0, 17, TEXT, 11.5, "middle", False, True)
panel_title(p2, "K = (a, b) kompakt değil", TEXT, 11.5)

OUT["weierstrass-ekstremum"] = figure(
    690, 280, [p1, p2],
    "Weierstrass varlık teoremi kompaktlığı zorunlu kılar. Solda kapalı ve sınırlı bir aralıkta sürekli "
    "fonksiyon hem en küçük hem en büyük değerine ulaşır. Sağda aralık açıldığında en büyük değerin adayı "
    "uç noktadadır ama o nokta kümede olmadığından ulaşılamaz: supremum vardır, maksimum yoktur.",
    css_class=WIDE, aria="Weierstrass teoremi: kapali ve acik aralikta ekstremumlar")

# ================================================================= sup ve inf
p = Plot(40, 60, 520, 130, (-3.4, 3.9), (-1.05, 0.85))
numline(p, 0.0, -3.2, 3.7, (-3, -2, -1, 0, 1, 2, 3), ("&#8722;3", "&#8722;2", "&#8722;1", "0", "1", "2", "3"))
bracket(p, -1.0, 2.0, 0.0, THEORY, 3.6, False, True)
p.label(0.5, 0.0, "D", 0, -14, THEORY, 13, "middle", True, True)
p.line([(-3.15, -0.5), (-1.0, -0.5)], BASE, 3.0)
p.arrow((-2.6, -0.5), (-3.35, -0.5), BASE, 1.4, head=7.0)
p.label(-2.05, -0.5, "alt sınırlar", 0, 18, BASE, 11, "middle", True)
p.line([(2.0, -0.5), (3.65, -0.5)], PRACTICE, 3.0)
p.arrow((3.1, -0.5), (3.85, -0.5), PRACTICE, 1.4, head=7.0)
p.label(2.85, -0.5, "üst sınırlar", 0, 18, PRACTICE, 11, "middle", True)
p.vline(-1.0, -0.5, 0.0, BASE, "3 3", 0.7)
p.vline(2.0, -0.5, 0.0, PRACTICE, "3 3", 0.7)
p.label(-1.0, 0.0, "inf D = &#8722;1", -4, -14, BASE, 11.5, "end", True)
p.label(2.0, 0.0, "sup D = 2", 6, -14, PRACTICE, 11.5, "start", True)
OUT["sup-inf"] = figure(
    600, 230, [p],
    "D = (&#8722;1, 2] kümesi için alt sınırlar sola, üst sınırlar sağa uzanan iki yarı doğrudur. "
    "Infimum alt sınırların <strong>en büyüğü</strong>, supremum üst sınırların <strong>en küçüğüdür</strong>; "
    "ikisi de kümeye ait olmak zorunda değildir. Burada sup D = 2 kümededir (maksimumdur), "
    "inf D = &#8722;1 ise değildir.",
    aria="Alt ve ust sinirlar, infimum ve supremum")

# ============================================================ bağlantılı kümeler
p = Plot(44, 44, 520, 190, (-0.75, 4.85), (-0.55, 1.75))
numline(p, 1.15, -0.55, 4.7, (0, 1, 2, 3, 4), ("0", "1", "2", "3", "4"))
bracket(p, 0.0, 2.0, 1.15, THEORY, 3.6, True, True)
bracket(p, 2.0, 4.0, 1.15, PRACTICE, 3.6, False, False)
p.label(1.0, 1.15, "A = [0, 2]", 0, -14, THEORY, 11.5, "middle", True)
p.label(3.0, 1.15, "B = (2, 4)", 0, -14, PRACTICE, 11.5, "middle", True)
p.label(4.75, 1.15, "bağlantılı", 6, 4, BASE, 11.5, "start", True)
p.label(2.0, 1.15, "2 " + IN + " A " + CAP + " B&#772;", 0, 34, REMARK, 10.5, "middle")

numline(p, 0.0, -0.55, 4.7, (0, 1, 2, 3, 4), ("0", "1", "2", "3", "4"))
bracket(p, 0.0, 2.0, 0.0, THEORY, 3.6, False, False)
bracket(p, 2.0, 4.0, 0.0, PRACTICE, 3.6, False, False)
p.label(1.0, 0.0, "C = (0, 2)", 0, -14, THEORY, 11.5, "middle", True)
p.label(3.0, 0.0, "B = (2, 4)", 0, -14, PRACTICE, 11.5, "middle", True)
p.label(4.75, 0.0, "bağlantılı değil", 6, 4, REMARK, 11.5, "start", True)
p.label(2.0, 0.0, "2 hiçbirinde yok", 0, 34, REMARK, 10.5, "middle")
OUT["baglantili-kume"] = figure(
    640, 260, [p],
    "Ayrık olmak ile ayrılmış olmak farklı şeylerdir. Üstte 2 noktası A'ya ait ve aynı zamanda B&#772;'de "
    "olduğundan A " + CAP + " B&#772; " + NEQ + " " + EMPTY + "; kümeler ayrılmış değildir ve birleşimleri "
    "[0, 4) bağlantılıdır. Altta 2 noktası hiçbirine ait değildir, iki küme birbirinin kapanışına da "
    "değmez: birleşim bağlantılı değildir.",
    aria="Baglantili ve baglantili olmayan birlesimler")

# ================================================= yerel ve mutlak minimum
def _mf(x):
    return 0.35 * x ** 4 - 1.6 * x ** 2 + 0.4 * x + 2.2


_xs = [-2.1 + 4.2 * k / 2000 for k in range(2001)]
_glob = min(_xs, key=_mf)                        # mutlak minimum
_loc = min([x for x in _xs if x > 0.6], key=_mf)  # sağdaki yerel minimum

p = Plot(52, 46, 420, 232, (-2.55, 2.55), (-0.9, 3.3))
p.axes([-2, -1, 0, 1, 2], [0, 1, 2, 3], "x", "f(x)")
p.line(curve(_mf, -2.1, 2.1), THEORY, 2.2)
p.polygon(rect(_loc - 0.55, -0.9, _loc + 0.55, 3.3), PRACTICE, 0.10, stroke="none")
p.points([(_glob, _mf(_glob)), (_loc, _mf(_loc))], PRACTICE, 4.6)
p.label(_glob, _mf(_glob), "mutlak minimum", 0, 22, PRACTICE, 11, "middle", True)
p.label(_loc, _mf(_loc), "yerel minimum", 0, 22, PRACTICE, 11, "middle", True)
p.label(_loc + 0.55, 2.75, "B(x" + SUB0 + ", " + DELTA + ")", 6, 0, REMARK, 11, "start", True)
p.points([(2.1, _mf(2.1))], BASE, 4.2)
p.label(2.1, _mf(2.1), "mutlak maksimum", -8, -8, BASE, 11, "end", True)
OUT["yerel-mutlak-minimum"] = figure(
    520, 320, [p],
    "Yerel minimumda f(x" + SUB0 + ") " + LEQ + " f(x) eşitsizliği yalnızca bir B(x" + SUB0 + ", " + DELTA +
    ") komşuluğunda istenir; mutlak minimumda ise kümenin tamamında. Sağdaki nokta kendi komşuluğunun en "
    "alçak noktasıdır ama küresel olarak değildir. Konveks fonksiyonlarda bu ayrımın ortadan kalkacağını "
    "ileride göreceğiz.",
    aria="Yerel minimum ile mutlak minimum farki")


# ############################################################################
# PART 2 — Afin Kümeler ve Konveks Kümeler
# ############################################################################

# ================================================ doğru ve afin kombinasyon
xa, ya = (0.7, 0.75), (3.1, 2.15)


def _aff(t):
    return ((1 - t) * xa[0] + t * ya[0], (1 - t) * xa[1] + t * ya[1])


p = panel(48, 46, 430, (-0.95, 5.05), (-0.4, 3.35))
p.origin_axes(xlabel="", ylabel="", opacity=0.3)
seg(p, _aff(-0.62), _aff(1.72), REMARK, 1.6, "6 5", 0.8)
seg(p, xa, ya, THEORY, 3.4)
p.points([xa, ya], THEORY, 4.6)
p.points([_aff(0.5)], BASE, 4.2)
p.points([_aff(-0.62), _aff(1.72)], PRACTICE, 4.2)
p.label(*xa, "x  (" + LAMBDA + " = 0)", -8, -6, THEORY, 11.5, "end", True, False)
p.label(*ya, "y  (" + LAMBDA + " = 1)", 8, -6, THEORY, 11.5, "start", True, False)
p.label(*_aff(0.5), LAMBDA + " = ½", 4, 20, BASE, 11.5, "middle", True)
p.label(*_aff(-0.62), LAMBDA + " &lt; 0", -6, 16, PRACTICE, 11.5, "middle", True)
p.label(*_aff(1.72), LAMBDA + " &gt; 1", 4, -10, PRACTICE, 11.5, "start", True)
p.text(0.05, 2.75, "(1 " + MINUS + " " + LAMBDA + ")x + " + LAMBDA + "y", TEXT, 12.5, "start", True, True)
OUT["dogru-afin-kombinasyon"] = figure(
    500, 320, [p],
    "İki noktanın (1 " + MINUS + " " + LAMBDA + ")x + " + LAMBDA + "y kombinasyonu, " + LAMBDA +
    " bütün reel sayıları dolaştığında <strong>x ile y'den geçen doğruyu</strong> çizer. " + LAMBDA +
    " yalnızca [0, 1] aralığında kaldığında ise <strong>doğru parçası</strong> elde edilir: afin kümeleri "
    "doğrulara, konveks kümeleri doğru parçalarına duyarlı yapan fark tam olarak budur.",
    aria="Afin kombinasyon dogruyu, konveks kombinasyon dogru parcasini verir")

# ============================================ afin küme = alt uzayın ötelemesi
d_dir = (2.5, 0.95)
x0_v = (-0.55, 1.85)
p = panel(48, 46, 400, (-2.6, 3.4), (-1.9, 2.85))
p.origin_axes(xlabel="", ylabel="", opacity=0.32)
seg(p, (-2.55 * d_dir[0] / 2.5, -2.55 * d_dir[1] / 2.5), (2.4 * d_dir[0] / 2.5, 2.4 * d_dir[1] / 2.5),
    BASE, 2.4, "6 5")
seg(p, (x0_v[0] - 2.0 * d_dir[0] / 2.5 * 1.0, x0_v[1] - 2.0 * d_dir[1] / 2.5 * 1.0),
    (x0_v[0] + 2.6 * d_dir[0] / 2.5, x0_v[1] + 2.6 * d_dir[1] / 2.5), THEORY, 2.6)
p.arrow((0, 0), x0_v, PRACTICE, 2.2)
p.points([x0_v], THEORY, 4.4)
p.points([(0, 0)], BASE, 3.6)
x1_v = (x0_v[0] + 1.5 * d_dir[0] / 2.5, x0_v[1] + 1.5 * d_dir[1] / 2.5)
p.arrow((0, 0), x1_v, PRACTICE, 1.5, dash="5 4", opacity=0.6)
p.points([x1_v], THEORY, 4.0)
p.label(*x0_v, "x" + SUB0, -9, -5, PRACTICE, 12.5, "end", True, True)
p.label(*x1_v, "x" + SUB1, 8, -6, REMARK, 12, "start", True, True)
p.label(2.3, 3.05, "A", 0, 0, THEORY, 14, "middle", True, True)
p.label(2.25, 0.62, "L = A " + MINUS + " x" + SUB0, 8, 12, BASE, 12, "start", True)
p.label(0, 0, "0", -8, 14, BASE, 11.5, "end", True)
OUT["afin-oteleme"] = figure(
    500, 340, [p],
    "Boştan farklı bir afin küme, bir lineer alt uzayın ötelenmişidir. A üzerinden herhangi bir x" + SUB0 +
    " seçilip A " + MINUS + " x" + SUB0 + " kurulduğunda daima orijinden geçen aynı L alt uzayı çıkar — "
    "şekilde x" + SUB1 + " ile ötelemek de aynı doğruyu verir. Bu yüzden A'nın boyutu, paralel olduğu "
    "L alt uzayının boyutu olarak tanımlanır.",
    aria="Afin kume bir alt uzayin otelemesidir")

# ==================================================== hiperdüzlem ve yarı uzaylar
a_n, b_n = (1.0, 1.6), 1.6
p = panel(48, 46, 400, (-2.4, 3.6), (-1.6, 2.6))
halfplane(p, a_n, b_n, -1, THEORY, 0.13, 2.4)
halfplane(p, a_n, b_n, +1, PRACTICE, 0.13, 0.0)
p.origin_axes(xlabel="", ylabel="", opacity=0.3)
foot_n = (0.0, 1.0)                                   # 0 + 1.6*1 = 1.6 -> H üzerinde
p.arrow(foot_n, (foot_n[0] + 0.42 * a_n[0], foot_n[1] + 0.42 * a_n[1]), BASE, 2.4)
p.points([foot_n], BASE, 3.6)
p.label(foot_n[0] + 0.42 * a_n[0], foot_n[1] + 0.42 * a_n[1], "a", 7, -3, BASE, 13, "start", True, True)
p.label(2.55, -0.6, "H" + "&#8804;" + ": " + LANG + "a, x" + RANG + " " + LEQ + " b", 0, 0, THEORY, 11.5, "middle", True)
p.label(-0.75, 2.15, "H" + "&#8805;" + ": " + LANG + "a, x" + RANG + " " + GEQ + " b", 0, 0, PRACTICE, 11.5, "middle", True)
p.label(3.05, -0.9, "H: " + LANG + "a, x" + RANG + " = b", -6, 0, TEXT, 12, "end", True)
OUT["hiperduzlem-yari-uzay"] = figure(
    500, 360, [p],
    "Bir hiperdüzlem H = { x : " + LANG + "a, x" + RANG + " = b }, uzayı iki kapalı yarı uzaya böler. "
    "Normal vektör <em>a</em>, H'ye diktir ve " + LANG + "a, x" + RANG + " değerinin arttığı yönü gösterir; "
    "bu yüzden a'nın işaret ettiği taraf H" + "&#8805;" + ", ters taraf H" + "&#8804;" + " olur. "
    "R<sup>n</sup> uzayında H'nin boyutu n " + MINUS + " 1'dir.",
    aria="Hiperduzlem ve belirledigi iki yari uzay")

# ================================================== Örnek: x + 2y = 4 hiperdüzlemi
a_e = (1.0, 2.0)
p = panel(56, 46, 418, (-4.6, 6.9), (-5.1, 3.3))
p.grid([-4, -2, 0, 2, 4, 6], [-4, -2, 0, 2])
p.origin_axes(xlabel="", ylabel="", xticks=(-4, -2, 2, 4, 6), yticks=(-4, -2, 2))
hyperline(p, a_e, 4.0, THEORY, 2.6)
hyperline(p, a_e, 0.0, BASE, 2.2, "6 5")
hyperline(p, a_e, -3.0, PRACTICE, 2.6)
p.arrow((0, 0), a_e, REMARK, 2.2)
p.label(*a_e, "a = (1, 2)", 8, -4, REMARK, 11.5, "start", True)
p.points([(4.0, 0.0), (5.0, -4.0)], THEORY, 4.4)
p.arrow((4.0, 0.0), (5.0, -4.0), PRACTICE, 1.8, dash="5 4")
p.label(4.6, -2.0, "(1, &#8722;4)", 8, 4, PRACTICE, 11.5, "start", True)
p.label(-1.0, 2.5, "H: x + 2y = 4", 8, -8, THEORY, 11.5, "start", True)
p.label(2.0, -1.0, "L: x + 2y = 0", 10, 14, BASE, 11.5, "start", True)
p.label(-1.0, -1.0, "H" + SUB1 + ": x + 2y = &#8722;3", -8, 16, PRACTICE, 11.5, "end", True)
OUT["ornek-hiperduzlem"] = figure(
    520, 400, [p],
    "x + 2y = 4 hiperdüzlemi, ona paralel olan L alt uzayı (x + 2y = 0) ve (1, &#8722;4) ötelemesiyle elde "
    "edilen H" + SUB1 + " (x + 2y = &#8722;3). Üç doğru da a = (1, 2) vektörüne diktir; öteleme sabit terimi "
    "değiştirir, normali değiştirmez. Paralel hiperdüzlemler yalnızca sağ taraftaki b sayısıyla ayrılır.",
    aria="x + 2y = 4 hiperduzlemi ve paralelleri")

# ============================================================ afin bağımsızlık
v0, v1, v2 = (0.55, 0.6), (2.95, 0.95), (1.65, 2.65)
p1 = panel(36, 48, 292, (-0.35, 3.75), (-0.35, 3.15))
p1.polygon([v0, v1, v2], THEORY, 0.10, stroke="none")
p1.arrow(v0, v1, THEORY, 2.0)
p1.arrow(v0, v2, PRACTICE, 2.0)
p1.points([v0, v1, v2], TEXT, 4.2)
p1.label(*v0, "v" + SUB0, -8, 10, TEXT, 12, "end", True, True)
p1.label(*v1, "v" + SUB1, 8, 6, TEXT, 12, "start", True, True)
p1.label(*v2, "v" + SUB2, 4, -9, TEXT, 12, "start", True, True)
p1.label(1.9, 0.75, "v" + SUB1 + " " + MINUS + " v" + SUB0, 0, 22, THEORY, 11, "middle", True, True)
p1.label(0.95, 1.75, "v" + SUB2 + " " + MINUS + " v" + SUB0, -6, -4, PRACTICE, 11, "end", True, True)
panel_title(p1, "afin bağımsız — aff: düzlem", TEXT, 11.5)

w0, w1, w2 = (0.5, 0.6), (1.8, 1.35), (3.1, 2.1)
p2 = panel(380, 48, 292, (-0.35, 3.75), (-0.35, 3.15))
seg(p2, (0.0, 0.31), (3.55, 2.36), REMARK, 1.6, "6 5", 0.8)
p2.arrow(w0, w1, THEORY, 2.0)
p2.arrow(w0, w2, PRACTICE, 1.6, dash="5 4")
p2.points([w0, w1, w2], TEXT, 4.2)
p2.label(*w0, "v" + SUB0, -8, 10, TEXT, 12, "end", True, True)
p2.label(*w1, "v" + SUB1, 2, -10, TEXT, 12, "start", True, True)
p2.label(*w2, "v" + SUB2, 8, 6, TEXT, 12, "start", True, True)
p2.label(2.4, 1.72, "v" + SUB2 + " " + MINUS + " v" + SUB0 + " = 2(v" + SUB1 + " " + MINUS + " v" + SUB0 + ")",
         4, 22, PRACTICE, 10.5, "middle", True, False)
panel_title(p2, "afin bağımlı — aff: doğru", TEXT, 11.5)

OUT["afin-bagimsizlik"] = figure(
    700, 290, [p1, p2],
    "v" + SUB0 + ", v" + SUB1 + ", v" + SUB2 + " noktalarının afin bağımsız olması, v" + SUB1 + " " + MINUS +
    " v" + SUB0 + " ile v" + SUB2 + " " + MINUS + " v" + SUB0 + " farklarının lineer bağımsız olması demektir. "
    "Solda iki fark farklı doğrultudadır, afin örtü düzlemin tamamıdır (boyut 2). Sağda biri diğerinin katı "
    "olduğundan üç nokta bir doğru üzerindedir ve afin örtü yalnızca o doğrudur (boyut 1).",
    css_class=WIDE, aria="Afin bagimsiz ve afin bagimli nokta uculeri")

# ================================================= konveks kombinasyon: üçgen
u0, u1, u2 = (0.6, 0.6), (3.2, 1.0), (1.7, 2.8)
z_in = (0.5 * u0[0] + 0.3 * u1[0] + 0.2 * u2[0], 0.5 * u0[1] + 0.3 * u1[1] + 0.2 * u2[1])
w_out = (0.9 * u0[0] + 0.5 * u1[0] - 0.4 * u2[0], 0.9 * u0[1] + 0.5 * u1[1] - 0.4 * u2[1])
p = panel(50, 46, 400, (-0.5, 4.1), (-0.75, 3.3))
for i, j in ((0, 1), (1, 2), (2, 0)):
    q, r = (u0, u1, u2)[i], (u0, u1, u2)[j]
    d = (r[0] - q[0], r[1] - q[1])
    seg(p, (q[0] - 0.45 * d[0], q[1] - 0.45 * d[1]), (r[0] + 0.45 * d[0], r[1] + 0.45 * d[1]),
        REMARK, 1.3, "6 5", 0.7)
p.polygon([u0, u1, u2], THEORY, 0.16, stroke="none")
p.line([u0, u1, u2, u0], THEORY, 2.3)
p.points([u0, u1, u2], THEORY, 4.4)
p.points([z_in], BASE, 4.8)
p.points([w_out], PRACTICE, 4.8)
p.label(*u0, "x" + SUB1, -8, 10, THEORY, 12, "end", True, True)
p.label(*u1, "x" + SUB2, 8, 8, THEORY, 12, "start", True, True)
p.label(*u2, "x" + SUB3, 2, -10, THEORY, 12, "start", True, True)
p.label(*z_in, "½x" + SUB1 + " + 0,3x" + SUB2 + " + 0,2x" + SUB3, -8, -8, BASE, 10.5, "end", True)
p.label(*w_out, "0,9x" + SUB1 + " + 0,5x" + SUB2 + " " + MINUS + " 0,4x" + SUB3, 6, 16, PRACTICE, 10.5, "start", True)
OUT["konveks-kombinasyon-ucgen"] = figure(
    500, 330, [p],
    "Üç noktanın katsayıları toplamı 1 olan kombinasyonları düzlemin tamamını (afin örtüyü) tarar; "
    "katsayıların hepsi negatif olmadığında ise yalnızca üçgen, yani <strong>konveks örtü</strong> elde "
    "edilir. Turuncu noktanın katsayıları da 1'e toplanır ama biri negatif olduğundan nokta üçgenin dışına "
    "düşer.",
    aria="Konveks kombinasyon ucgeni, afin kombinasyon duzlemi tarar")

# ================================================ konveks / yıldız biçimli / hiçbiri
hexa = [(2.0 + 1.45 * math.cos(PI / 6 + k * PI / 3), 1.5 + 1.45 * math.sin(PI / 6 + k * PI / 3))
        for k in range(6)]
q1 = panel(26, 52, 202, (-0.55, 4.55), (-0.75, 3.75))
region(q1, hexa, BASE, 0.16, 2.2)
seg(q1, hexa[0], hexa[3], TEXT, 1.4, "5 4", 0.65)
seg(q1, hexa[1], hexa[4], TEXT, 1.4, "5 4", 0.65)
q1.text(2.0, -0.5, "her kiriş içeride", BASE, 11, "middle", True)
panel_title(q1, "konveks", TEXT, 11.5)

notch = [(0, 0), (4, 0), (4, 3), (2.5, 3), (2, 1.8), (1.5, 3), (0, 3)]
star = (2.0, 0.6)
q2 = panel(260, 52, 202, (-0.55, 4.55), (-0.75, 3.75))
region(q2, notch, PRACTICE, 0.14, 2.2)
for t in (0.0, 0.6, 1.15, 1.5, 2.5, 2.85, 3.4, 4.0):
    seg(q2, star, (t, 3.0), PRACTICE, 1.0, "3 3", 0.55)
seg(q2, star, (0.0, 0.0), PRACTICE, 1.0, "3 3", 0.55)
seg(q2, star, (4.0, 0.0), PRACTICE, 1.0, "3 3", 0.55)
seg(q2, star, (4.0, 2.2), PRACTICE, 1.0, "3 3", 0.55)
seg(q2, star, (0.0, 2.2), PRACTICE, 1.0, "3 3", 0.55)
q2.points([star], PRACTICE, 4.4)
q2.label(*star, "x", -8, 4, PRACTICE, 12.5, "end", True, True)
q2.text(2.0, -0.5, "x her noktayı görür", PRACTICE, 11, "middle", True)
panel_title(q2, "yıldız biçimli", TEXT, 11.5)

ushape = [(0, 0), (4, 0), (4, 3), (2.5, 3), (2.5, 1), (1.5, 1), (1.5, 3), (0, 3)]
q3 = panel(494, 52, 202, (-0.55, 4.55), (-0.75, 3.75))
region(q3, ushape, REMARK, 0.14, 2.2)
pL, pR = (0.6, 2.5), (3.4, 2.5)
seg(q3, pL, pR, PRACTICE, 2.0, "5 4")
q3.points([pL, pR], PRACTICE, 4.2)
cross(q3, (2.0, 2.5), PRACTICE, 5.5, 2.0)
q3.text(2.0, -0.5, "kiriş kümeden çıkar", REMARK, 11, "middle", True)
panel_title(q3, "yıldız biçimli de değil", TEXT, 11.5)

OUT["konveks-yildiz"] = figure(
    720, 330, [q1, q2, q3],
    "Konveks küme, herhangi iki noktasını birleştiren doğru parçasını tamamen içerir. Ortadaki küme konveks "
    "değildir ama <em>x</em> noktasına göre yıldız biçimlidir: <strong>bir</strong> nokta bütün kümeyi görür. "
    "Sağdaki kümede böyle bir nokta yoktur; iki kolun uçları arasındaki kiriş her seçimde boşluktan geçer. "
    "Bir kümenin konveks olması, <strong>her</strong> noktasına göre yıldız biçimli olmasıyla aynı şeydir.",
    css_class=WIDE, aria="Konveks, yildiz bicimli ve hicbiri olmayan kumeler")

# =============================================================== polihedral küme
poly = [(0.4, 0.3), (3.4, 0.5), (4.0, 2.1), (2.2, 3.2), (0.6, 2.2)]
p = panel(50, 48, 400, (-1.3, 5.7), (-1.05, 4.4))
p.origin_axes(xlabel="", ylabel="", opacity=0.28)
for i in range(len(poly)):
    q, r = poly[i], poly[(i + 1) % len(poly)]
    e = (r[0] - q[0], r[1] - q[1])
    a_i = (e[1], -e[0])                       # dışa doğru normal (köşeler saat yönünün tersinde)
    b_i = a_i[0] * q[0] + a_i[1] * q[1]
    hyperline(p, a_i, b_i, REMARK, 1.3, "6 5", 0.75)
    mid = ((q[0] + r[0]) / 2, (q[1] + r[1]) / 2)
    n = math.hypot(*a_i)
    p.arrow(mid, (mid[0] + a_i[0] / n * 0.55, mid[1] + a_i[1] / n * 0.55), BASE, 1.5, head=7.0)
region(p, poly, THEORY, 0.18, 2.4)
p.label(2.1, 1.6, "P", 0, 0, THEORY, 15, "middle", True, True)
p.text(5.55, 4.05, "P = { x : Ax " + LEQ + " b }", THEORY, 12.5, "end", True)
p.text(5.55, 3.72, "sonlu sayıda yarı uzayın kesişimi", REMARK, 11, "end", False)
OUT["polihedral-kume"] = figure(
    500, 380, [p],
    "Polihedral (çok yüzlü) küme, sonlu sayıda kapalı yarı uzayın kesişimidir. Her " + LANG + "a" + SUBI +
    ", x" + RANG + " " + LEQ + " b" + SUBI + " eşitsizliği bir doğrunun bir yanını keser; okla gösterilen "
    "dışa doğru normaller yasak yönü işaret eder. Kapalı yarı uzaylar hem kapalı hem konveks olduğundan "
    "kesişimleri de kapalı ve konvekstir.",
    aria="Polihedral kume yari uzaylarin kesisimi olarak")

# ============================================ konveksliğin işlemler altında korunması
tri = [(0.35, 0.4), (2.75, 0.55), (1.45, 2.5)]
p1 = panel(30, 52, 292, (-1.5, 4.0), (-1.6, 3.5))
p1.origin_axes(xlabel="", ylabel="", opacity=0.28)
sumset = offset_polygon(tri, 0.62)
p1.polygon(sumset, PRACTICE, 0.14, stroke="none")
p1.line(sumset + [sumset[0]], PRACTICE, 2.1)
region(p1, tri, THEORY, 0.20, 2.1)
ball(p1, (-0.85, -1.0), 0.62, BASE, 0.22, None, 2.0)
p1.points([(-0.85, -1.0)], BASE, 3.0)
p1.label(1.5, 1.05, "C" + SUB1, 0, 0, THEORY, 13, "middle", True, True)
p1.label(-0.85, -1.0, "C" + SUB2, 0, 30, BASE, 13, "middle", True, True)
p1.label(2.55, 2.6, "C" + SUB1 + " + C" + SUB2, 6, 0, PRACTICE, 12.5, "start", True, True)
panel_title(p1, "toplam", TEXT, 11.5)

base_blob = hull(blob(0.15, 0.1, 1.0, [(0.2, 3, 0.5), (0.12, 2, 1.4)]))
p2 = panel(374, 52, 292, (-2.3, 3.2), (-2.3, 2.8))
p2.origin_axes(xlabel="", ylabel="", opacity=0.28)
for k, (sc, col, op) in enumerate(((1.75, PRACTICE, 0.10), (1.0, THEORY, 0.16), (0.55, BASE, 0.22))):
    pts = [(x * sc, y * sc) for x, y in base_blob]
    p2.polygon(pts, col, op, stroke="none")
    p2.line(pts + [pts[0]], col, 2.0)
p2.points([(0, 0)], TEXT, 3.2)
p2.label(0, 0, "0", -8, 13, TEXT, 11, "end", True)
for sc, col, txt, size in ((0.55, BASE, "0,55 C", 11.5), (1.0, THEORY, "C", 13),
                          (1.75, PRACTICE, "1,75 C", 11.5)):
    tip = extreme([(x * sc, y * sc) for x, y in base_blob], 135 * DEG)
    p2.label(tip[0], tip[1], txt, -4, -4, col, size, "end", True, txt == "C")
panel_title(p2, "skaler kat", TEXT, 11.5)

OUT["konveks-korunum"] = figure(
    700, 350, [p1, p2],
    "Konvekslik toplama ve skaler ile çarpma altında korunur. Solda bir üçgen ile bir diskin toplamı, üçgenin "
    "yarıçap kadar her yöne kalınlaştırılmış hâlidir. Sağda " + ALPHA + "C kümeleri, C'nin orijine göre "
    "büyütülüp küçültülmüş kopyalarıdır. Aynı şey kesişim için de geçerlidir; buna karşılık iki konveks "
    "kümenin birleşimi genellikle konveks olmaz.",
    css_class=WIDE, aria="Konveks kumelerin toplami ve skaler kati")

# ============================================== lineer dönüşüm altında görüntü
T = ((1.15, 0.72), (0.38, 1.05))


def _T(q):
    return (T[0][0] * q[0] + T[0][1] * q[1], T[1][0] * q[0] + T[1][1] * q[1])


sq_c = rect(-1.0, -1.0, 1.0, 1.0)
circ_c = circle_pts(0, 0, 0.72, 0, 2 * PI, 72)
p1 = panel(34, 52, 268, (-2.0, 2.6), (-1.9, 2.3))
p1.origin_axes(xlabel="", ylabel="", opacity=0.3)
region(p1, sq_c, THEORY, 0.14, 2.1)
region(p1, circ_c, BASE, 0.18, 1.9)
p1.label(0, 0, "C", 0, 5, THEORY, 13, "middle", True, True)
panel_title(p1, "C " + SUBSET + " R&#178;", TEXT, 11.5)

p2 = panel(360, 52, 300, (-2.8, 3.4), (-2.4, 2.8))
p2.origin_axes(xlabel="", ylabel="", opacity=0.3)
region(p2, [_T(q) for q in sq_c], THEORY, 0.14, 2.1)
region(p2, [_T(q) for q in circ_c], BASE, 0.18, 1.9)
p2.label(0, 0, "T(C)", 0, 5, THEORY, 13, "middle", True, True)
panel_title(p2, "T(C) " + SUBSET + " R&#178;", TEXT, 11.5)

OUT["lineer-goruntu"] = figure(
    700, 330, [p1, p2],
    "Lineer (ve daha genel olarak afin) bir dönüşüm konveksliği korur: T((1 " + MINUS + " " + LAMBDA +
    ")x + " + LAMBDA + "y) = (1 " + MINUS + " " + LAMBDA + ")T(x) + " + LAMBDA + "T(y) olduğundan bir doğru "
    "parçasının görüntüsü yine doğru parçasıdır. Kare paralelkenara, disk elipse dönüşür; her ikisi de "
    "konveks kalır. Ters görüntü T<sup>&#8722;1</sup>(D) için de aynı sonuç geçerlidir.",
    css_class=WIDE, aria="Lineer donusum altinda konveks kumenin goruntusu")

# ================================================ int C konvekstir (Teorem ispatı)
C_blob = hull(blob(0.0, 0.0, 1.85, [(0.3, 2, 0.9), (0.16, 3, 2.4)]))
xr, yr = (-1.05, -0.55), (0.95, 0.75)
lam = 0.45
zr = ((1 - lam) * xr[0] + lam * yr[0], (1 - lam) * xr[1] + lam * yr[1])
rad = 0.42
p = panel(46, 48, 350, (-2.65, 2.95), (-2.5, 2.4))
region(p, C_blob, THEORY, 0.10, 2.1)
ball(p, xr, rad, BASE, 0.20, None, 1.7)
ball(p, yr, rad, BASE, 0.20, None, 1.7)
ball(p, zr, rad, PRACTICE, 0.24, None, 2.0)
seg(p, xr, yr, TEXT, 1.5, "5 4", 0.6)
p.points([xr, yr], BASE, 3.6)
p.points([zr], PRACTICE, 3.8)
p.arrow((xr[0], xr[1] + rad + 0.12), (zr[0], zr[1] + rad + 0.12), REMARK, 1.5, dash="4 3")
p.label((xr[0] + zr[0]) / 2, zr[1] + rad + 0.12, LAMBDA + "(y " + MINUS + " x)", 0, -8, REMARK, 11, "middle", True)
p.label(*xr, "x", -6, 16, BASE, 12.5, "end", True, True)
p.label(*yr, "y", 8, 12, BASE, 12.5, "start", True, True)
p.label(*zr, "(1" + MINUS + LAMBDA + ")x + " + LAMBDA + "y", 2, -20, PRACTICE, 11, "middle", True)
p.label(-2.05, 1.85, "C", 0, 0, THEORY, 14, "middle", True, True)
OUT["ic-nokta-konveks"] = figure(
    450, 340, [p],
    "int C kümesinin konveksliğinin ispatındaki fikir. x ve y iç noktaysa, her ikisinin de yarıçapı r olan "
    "bir yuvarı C'de kalır. Aradaki noktanın yuvarı B(x, r) yuvarının " + LAMBDA + "(y " + MINUS + " x) "
    "kadar ötelenmişidir ve C konveks olduğundan bu öteleme de C'nin içinde kalır; dolayısıyla ara nokta da "
    "bir iç noktadır.",
    aria="Ic noktalarin konveks kombinasyonu yine ic noktadir")

# ===================================================================== konveks örtü
cloud = [(0.45, 0.55), (2.05, 0.3), (3.35, 1.05), (3.05, 2.55), (1.55, 3.1),
         (0.35, 2.05), (1.75, 1.5), (2.35, 1.95), (1.15, 1.15)]
p1 = panel(34, 50, 282, (-0.35, 3.85), (-0.35, 3.5))
hl = hull(cloud)
p1.polygon(hl, THEORY, 0.14, stroke="none")
p1.line(hl + [hl[0]], THEORY, 2.3)
p1.points(cloud, PRACTICE, 4.2)
p1.text(1.85, -0.2, "sonlu nokta kümesi", THEORY, 11, "middle", True)
panel_title(p1, "conv(A): politop", TEXT, 11.5)

bean = blob(1.85, 1.6, 1.25, [(0.55, 1, 2.2), (0.42, 2, 0.4), (0.2, 3, 1.1)])
p2 = panel(376, 50, 282, (-0.35, 3.85), (-0.35, 3.5))
hb = hull(bean)
p2.polygon(hb, PRACTICE, 0.10, stroke="none")
p2.line(hb + [hb[0]], PRACTICE, 2.1, "6 5")
region(p2, bean, THEORY, 0.18, 2.1)
p2.text(1.85, -0.2, "girintiler doldurulur", PRACTICE, 11, "middle", True)
panel_title(p2, "conv(A): en küçük konveks küme", TEXT, 11.5)

OUT["konveks-ortu"] = figure(
    700, 330, [p1, p2],
    "Konveks örtü conv(A), A'yı kapsayan bütün konveks kümelerin kesişimi — yani A'yı kapsayan <strong>en "
    "küçük</strong> konveks kümedir. Solda sonlu bir nokta kümesinin etrafına gerilen lastik bir politop "
    "verir; sağda girintili bir bölgenin çukurları doldurulur. conv(A), A elemanlarının bütün konveks "
    "kombinasyonlarının kümesine eşittir.",
    css_class=WIDE, aria="Sonlu nokta kumesinin ve girintili bolgenin konveks ortusu")

# =============================================================== Carathéodory
cpts = [(0.5, 0.7), (2.4, 0.35), (3.7, 1.5), (2.85, 3.15), (1.0, 2.85), (1.9, 1.7)]
tri_c = [cpts[0], cpts[2], cpts[4]]
zc = (0.45 * tri_c[0][0] + 0.3 * tri_c[1][0] + 0.25 * tri_c[2][0],
      0.45 * tri_c[0][1] + 0.3 * tri_c[1][1] + 0.25 * tri_c[2][1])
p = panel(48, 48, 380, (-0.4, 4.35), (-0.45, 3.65))
hc = hull(cpts)
p.polygon(hc, THEORY, 0.09, stroke="none")
p.line(hc + [hc[0]], THEORY, 2.1, "6 5")
p.polygon(tri_c, PRACTICE, 0.20, stroke="none")
p.line(tri_c + [tri_c[0]], PRACTICE, 2.3)
p.points(cpts, TEXT, 4.0)
p.points(tri_c, PRACTICE, 4.8)
p.points([zc], BASE, 5.2)
p.label(*zc, "x", 9, 5, BASE, 13, "start", True, True)
p.label(2.1, 3.42, "conv(A)", 0, 0, THEORY, 12, "middle", True)
p.label(1.55, 1.05, "3 nokta yeter", 0, 0, PRACTICE, 11.5, "middle", True)
OUT["caratheodory"] = figure(
    470, 380, [p],
    "Carathéodory teoremi. conv(A) kümesindeki bir <em>x</em> noktası, başlangıçta kaç nokta kullanılırsa "
    "kullanılsın, A'nın <strong>en çok n + 1</strong> elemanının konveks kombinasyonu olarak yazılabilir. "
    "Düzlemde (n = 2) bu sayı 3'tür: x noktası daima köşeleri A'dan seçilen bir üçgenin içinde kalır. "
    "İspat, fazla noktaların katsayılarını birer birer sıfırlayan bir indirgemedir.",
    aria="Caratheodory teoremi: duzlemde uc nokta yeter")

# ===================================================================== Radon
r1 = [(0.5, 0.55), (3.3, 0.75), (3.0, 2.9), (0.85, 2.6)]
p1 = panel(34, 50, 282, (-0.35, 3.95), (-0.35, 3.35))
p1.line(r1 + [r1[0]], REMARK, 1.3, "6 5", 0.6)
seg(p1, r1[0], r1[2], THEORY, 2.4)
seg(p1, r1[1], r1[3], PRACTICE, 2.4)


def _cross_pt(a, b, c, d):
    d1 = (b[0] - a[0], b[1] - a[1])
    d2 = (d[0] - c[0], d[1] - c[1])
    den = d1[0] * d2[1] - d1[1] * d2[0]
    t = ((c[0] - a[0]) * d2[1] - (c[1] - a[1]) * d2[0]) / den
    return (a[0] + t * d1[0], a[1] + t * d1[1])


xc1 = _cross_pt(r1[0], r1[2], r1[1], r1[3])
p1.points([r1[0], r1[2]], THEORY, 4.6)
p1.points([r1[1], r1[3]], PRACTICE, 4.6)
p1.points([xc1], BASE, 5.0)
p1.label(*r1[0], "x" + SUB1, -8, 8, THEORY, 11.5, "end", True, True)
p1.label(*r1[2], "x" + SUB3, 8, -4, THEORY, 11.5, "start", True, True)
p1.label(*r1[1], "x" + SUB2, 8, 8, PRACTICE, 11.5, "start", True, True)
p1.label(*r1[3], "x&#8324;", -8, -4, PRACTICE, 11.5, "end", True, True)
p1.label(*xc1, "kesişim", 10, 16, BASE, 11, "start", True)
panel_title(p1, "dörtgen konumu", TEXT, 11.5)

r2 = [(0.5, 0.5), (3.4, 0.7), (1.9, 3.05)]
inner = ((r2[0][0] + r2[1][0] + r2[2][0]) / 3, (r2[0][1] + r2[1][1] + r2[2][1]) / 3)
p2 = panel(376, 50, 282, (-0.35, 3.95), (-0.35, 3.35))
p2.polygon(r2, THEORY, 0.16, stroke="none")
p2.line(r2 + [r2[0]], THEORY, 2.3)
p2.points(r2, THEORY, 4.6)
p2.points([inner], PRACTICE, 5.2)
p2.label(*r2[0], "x" + SUB1, -8, 8, THEORY, 11.5, "end", True, True)
p2.label(*r2[1], "x" + SUB2, 8, 8, THEORY, 11.5, "start", True, True)
p2.label(*r2[2], "x" + SUB3, 4, -9, THEORY, 11.5, "start", True, True)
p2.label(*inner, "x&#8324;", 9, 5, PRACTICE, 12, "start", True, True)
panel_title(p2, "biri üçgenin içinde", TEXT, 11.5)

OUT["radon"] = figure(
    700, 330, [p1, p2],
    "Radon teoremi: düzlemde 4 (genel olarak n + 2) nokta daima, konveks örtüleri kesişen iki ayrık parçaya "
    "bölünebilir. İki olası durum vardır. Solda dört nokta dörtgen konumundadır ve köşegenler kesişir: "
    "parçalar { x" + SUB1 + ", x" + SUB3 + " } ile { x" + SUB2 + ", x&#8324; }. Sağda bir nokta diğer üçünün "
    "üçgeninin içindedir; parçalar { x&#8324; } ile { x" + SUB1 + ", x" + SUB2 + ", x" + SUB3 + " } olur.",
    css_class=WIDE, aria="Radon teoreminin iki durumu")

# ====================================================================== Helly
cen4 = [(-1.3, -1.3), (1.3, -1.3), (1.3, 1.3), (-1.3, 1.3)]
R4 = 2.6
p1 = panel(30, 52, 282, (-4.2, 4.2), (-4.2, 4.2))
for c in cen4:
    disk_fill(p1, c[0], c[1], R4, THEORY, 0.07)
    p1.circle(c[0], c[1], R4, THEORY, 1.7)
common = radial_boundary((0, 0), lambda q: all(math.hypot(q[0] - c[0], q[1] - c[1]) <= R4 for c in cen4), 4.5)
p1.polygon(common, PRACTICE, 0.45, stroke="none")
p1.line(common + [common[0]], PRACTICE, 1.9)
p1.label(0, 0, "ortak", 0, 4, PRACTICE, 11.5, "middle", True)
panel_title(p1, "her üçü kesişiyor " + ARROW + " dördü de", TEXT, 11.5)

# kenar uzunlugu 2 olan eskenar ucgen: cevrel yaricap 2/sqrt(3) = 1,155
CIRC = 2.0 / math.sqrt(3)
cen3 = [(CIRC * math.cos(PI / 2 + k * 2 * PI / 3), CIRC * math.sin(PI / 2 + k * 2 * PI / 3))
        for k in range(3)]
R3 = 1.1                       # 1,1 < 1,155: ucunun ortak noktasi yoktur
p2 = panel(374, 52, 282, (-4.2, 4.2), (-4.2, 4.2))
for c in cen3:
    disk_fill(p2, c[0], c[1], R3, BASE, 0.10)
    p2.circle(c[0], c[1], R3, BASE, 1.9)
cross(p2, (0, 0), PRACTICE, 6.5, 2.4)
p2.text(0, -2.85, "ortak nokta yok", PRACTICE, 11.5, "middle", True)
panel_title(p2, "ikişerli kesişim yetmez", TEXT, 11.5)

OUT["helly"] = figure(
    700, 350, [p1, p2],
    "Helly teoremi: R<sup>n</sup>'de n + 1 taneli her alt ailenin kesişimi boş değilse, bütün ailenin "
    "kesişimi de boş değildir. Solda düzlemde dört disk vardır ve üçerli her kesişim doluysa dördünün ortak "
    "noktası da vardır. Sağdaki üç disk ikişer ikişer kesişir ama üçünün ortak noktası yoktur: düzlemde "
    "aranan sayı 2 değil, n + 1 = 3'tür.",
    css_class=WIDE, aria="Helly teoremi ve ikiserli kesisimin yetmedigi ornek")

# ==================================================================== simpleksler
q1 = panel(20, 56, 154, (-0.35, 3.35), (-0.35, 3.05))
q1.points([(1.5, 1.35)], THEORY, 5.4)
panel_title(q1, "0-simpleks", TEXT, 11.5)
q1.text(1.5, -0.2, "nokta", REMARK, 11, "middle")

q2 = panel(196, 56, 154, (-0.35, 3.35), (-0.35, 3.05))
seg(q2, (0.45, 0.75), (2.55, 1.95), THEORY, 2.8)
q2.points([(0.45, 0.75), (2.55, 1.95)], THEORY, 4.6)
panel_title(q2, "1-simpleks", TEXT, 11.5)
q2.text(1.5, -0.2, "doğru parçası", REMARK, 11, "middle")

q3 = panel(372, 56, 154, (-0.35, 3.35), (-0.35, 3.05))
t3 = [(0.4, 0.5), (2.7, 0.75), (1.35, 2.5)]
region(q3, t3, THEORY, 0.18, 2.3)
q3.points(t3, THEORY, 4.6)
panel_title(q3, "2-simpleks", TEXT, 11.5)
q3.text(1.5, -0.2, "üçgensel bölge", REMARK, 11, "middle")

q4 = panel(548, 56, 154, (-0.35, 3.35), (-0.35, 3.05))
t4 = [(0.35, 0.45), (2.75, 0.45), (1.55, 2.6)]
inner4 = (1.5, 1.15)
region(q4, t4, THEORY, 0.13, 2.3)
for v in t4:
    seg(q4, v, inner4, THEORY, 1.5, "5 4", 0.85)
q4.points(t4 + [inner4], THEORY, 4.4)
panel_title(q4, "3-simpleks", TEXT, 11.5)
q4.text(1.5, -0.2, "tetrahedron", REMARK, 11, "middle")

OUT["simpleksler"] = figure(
    720, 320, [q1, q2, q3, q4],
    "k-simpleks, afin bağımsız k + 1 noktanın konveks örtüsüdür; boyutu tam olarak k'dir. Bir nokta ekledikçe "
    "boyut bir artar. Simpleksler, Carathéodory teoreminin geometrik karşılığıdır: R<sup>n</sup>'de bir "
    "konveks örtünün her noktası, köşeleri kümeden seçilen bir n-simpleksin içindedir.",
    css_class=WIDE, aria="Sifir, bir, iki ve uc boyutlu simpleksler")

# =================================================================== köşe noktaları
pent = [(0.45, 0.6), (2.9, 0.4), (3.6, 2.2), (2.0, 3.3), (0.4, 2.35)]
q1 = panel(24, 54, 200, (-0.4, 4.2), (-0.5, 3.75))
region(q1, pent, THEORY, 0.14, 2.2)
q1.points(pent, PRACTICE, 5.0)
q1.text(1.95, -0.28, "köşeler: 5 nokta", PRACTICE, 11, "middle", True)
panel_title(q1, "politop", TEXT, 11.5)

q2 = panel(256, 54, 200, (-0.4, 4.2), (-0.5, 3.75))
disk_fill(q2, 1.9, 1.6, 1.5, THEORY, 0.14)
q2.circle(1.9, 1.6, 1.5, PRACTICE, 3.2)
q2.text(1.95, -0.28, "çemberin her noktası", PRACTICE, 11, "middle", True)
panel_title(q2, "disk", TEXT, 11.5)

q3 = panel(488, 54, 200, (-0.4, 4.2), (-0.5, 3.75))
halfplane(q3, (0.55, 1.0), 2.1, -1, THEORY, 0.14, 2.4)
q3.text(1.95, -0.28, "köşe noktası yok", REMARK, 11, "middle", True)
panel_title(q3, "yarı uzay", TEXT, 11.5)

OUT["kose-noktalari"] = figure(
    720, 320, [q1, q2, q3],
    "Bir köşe noktası, kümenin başka iki noktasının ortası olarak yazılamayan noktadır. Politopta yalnızca "
    "köşeler bu özelliği taşır; diskte çemberin <strong>her</strong> noktası bir köşe noktasıdır; yarı uzayda "
    "ise hiç yoktur, çünkü her nokta bir doğru parçasının içinde kalır. Kompakt konveks kümeler köşe "
    "noktalarının konveks örtüsüdür.",
    css_class=WIDE, aria="Politop, disk ve yari uzayda kose noktalari")

# ================================================== en yakın nokta ve tekliği
C_np = hull(blob(-0.35, 0.0, 1.5, [(0.28, 2, 0.7), (0.15, 3, 2.0)]))
y_np = (2.55, 1.55)
z_np = min(C_np, key=lambda q: (q[0] - y_np[0]) ** 2 + (q[1] - y_np[1]) ** 2)
a_np = (y_np[0] - z_np[0], y_np[1] - z_np[1])
b_np = a_np[0] * z_np[0] + a_np[1] * z_np[1]
p1 = panel(30, 50, 300, (-2.4, 3.5), (-2.2, 2.8))
region(p1, C_np, THEORY, 0.13, 2.1)
hyperline(p1, a_np, b_np, REMARK, 1.6, "6 5", 0.85)
p1.arrow(z_np, y_np, PRACTICE, 2.2)
p1.points([y_np], PRACTICE, 4.6)
p1.points([z_np], BASE, 4.6)
right_angle(p1, z_np, a_np, (-a_np[1], a_np[0]), 0.26)
p1.label(*y_np, "y", 9, -4, PRACTICE, 13, "start", True, True)
p1.label(*z_np, "z", -9, 10, BASE, 13, "end", True, True)
p1.label(-1.35, -1.15, "C", 0, 0, THEORY, 14, "middle", True, True)
panel_title(p1, "C konveks: tek en yakın nokta", TEXT, 11.5)

c1, c2, rr2 = (-1.15, -0.85), (-1.15, 0.85), 0.72
p2 = panel(382, 50, 300, (-2.4, 3.5), (-2.2, 2.8))
ball(p2, c1, rr2, THEORY, 0.14, None, 2.1)
ball(p2, c2, rr2, THEORY, 0.14, None, 2.1)
y2 = (1.1, 0.0)
def _toward(c):
    n = math.hypot(y2[0] - c[0], y2[1] - c[1])
    return (c[0] + (y2[0] - c[0]) / n * rr2, c[1] + (y2[1] - c[1]) / n * rr2)


z1, z2 = _toward(c1), _toward(c2)
p2.arrow(z1, y2, PRACTICE, 1.9)
p2.arrow(z2, y2, PRACTICE, 1.9)
p2.points([y2], PRACTICE, 4.6)
p2.points([z1, z2], BASE, 4.6)
p2.label(*y2, "y", 9, -4, PRACTICE, 13, "start", True, True)
p2.label(*z1, "z" + SUB1, -8, 12, BASE, 12, "end", True, True)
p2.label(*z2, "z" + SUB2, -8, -6, BASE, 12, "end", True, True)
p2.label(-1.15, -2.0, "C konveks değil", 0, 0, REMARK, 11.5, "middle", True)
panel_title(p2, "iki tane en yakın nokta", TEXT, 11.5)

OUT["en-yakin-nokta"] = figure(
    712, 340, [p1, p2],
    "Kapalı ve konveks bir C kümesinin, dışındaki bir y noktasına en yakın noktası <strong>vardır ve "
    "tektir</strong>. İki aday olsaydı ortalarını almak — konvekslik sayesinde C'de kalan bir nokta — daha "
    "kısa bir uzaklık verirdi. Sağdaki küme konveks olmadığından teklik bozulur: iki ayrı en yakın nokta "
    "ortaya çıkar. Solda z'den y'ye giden vektörün C'yi destekleyen doğruya dik olduğuna dikkat ediniz.",
    css_class=WIDE, aria="Konveks kumede en yakin noktanin tekligi")

# ============================================================= destek hiperdüzlemi
S_sup = [(0.4, 0.55), (2.9, 0.35), (3.75, 2.0)] + circle_pts(2.3, 2.05, 1.6, 0.35, 2.5, 40)
S_sup = hull(S_sup)
p = panel(48, 48, 350, (-1.0, 5.1), (-1.0, 4.2))
region(p, S_sup, THEORY, 0.14, 2.2)
def _outward(i):
    """Outward normal of the edge leaving vertex i (the hull is counter-clockwise)."""
    q, r = S_sup[i], S_sup[(i + 1) % len(S_sup)]
    e = (r[0] - q[0], r[1] - q[1])
    n = math.hypot(*e)
    return (e[1] / n, -e[0] / n)


i_bot = min(range(len(S_sup)),
            key=lambda i: (S_sup[i][1] + S_sup[(i + 1) % len(S_sup)][1]) / 2)
edge_pt = ((S_sup[i_bot][0] + S_sup[(i_bot + 1) % len(S_sup)][0]) / 2,
           (S_sup[i_bot][1] + S_sup[(i_bot + 1) % len(S_sup)][1]) / 2)
a_s = _outward(i_bot)
b_s = a_s[0] * edge_pt[0] + a_s[1] * edge_pt[1]
hyperline(p, a_s, b_s, PRACTICE, 2.2)
p.points([edge_pt], PRACTICE, 4.4)
n_s = math.hypot(*a_s)
p.arrow(edge_pt, (edge_pt[0] + a_s[0] / n_s * 0.75, edge_pt[1] + a_s[1] / n_s * 0.75), PRACTICE, 1.8)

top = max(S_sup, key=lambda q: q[1])
a_t = (0.0, 1.0)
hyperline(p, a_t, top[1], BASE, 2.2)
p.points([top], BASE, 4.4)
p.arrow(top, (top[0], top[1] + 0.75), BASE, 1.8)

# at a genuine vertex the supporting normals fill the whole normal cone
i_cor = max(range(len(S_sup)), key=lambda i: S_sup[i][0] - 0.25 * S_sup[i][1])
corner = S_sup[i_cor]
n_prev, n_next = _outward(i_cor - 1), _outward(i_cor)
ang0, ang1 = math.atan2(n_prev[1], n_prev[0]), math.atan2(n_next[1], n_next[0])
while ang1 < ang0:
    ang1 += 2 * PI
for k in range(4):
    ang = ang0 + (ang1 - ang0) * (k + 0.5) / 4
    a_c = (math.cos(ang), math.sin(ang))
    hyperline(p, a_c, a_c[0] * corner[0] + a_c[1] * corner[1], REMARK, 1.3, "5 4", 0.8)
p.points([corner], REMARK, 4.4)
p.label(*corner, "köşede tek değil", 10, 6, REMARK, 11, "start", True)
p.label(edge_pt[0] - 1.5, edge_pt[1], "destek doğrusu", 0, 22, PRACTICE, 11, "middle", True)
p.label(2.2, 2.0, "M", 0, 0, THEORY, 14, "middle", True, True)
OUT["destek-hiperduzlemi"] = figure(
    460, 380, [p],
    "Destek hiperdüzlemi, kümenin bir sınır noktasından geçen ve kümenin tamamını bir yanında bırakan "
    "hiperdüzlemdir. Düz kenarda ve düzgün sınır noktasında tektir; köşede ise sonsuz çoktur — kesikli "
    "doğruların hepsi kümeyi destekler. Ayırma teoremleri, dışarıdaki bir noktayı kümeden ayıran "
    "hiperdüzlemi tam olarak bu şekilde üretir.",
    aria="Destek hiperduzlemleri ve kosede tekligin bozulmasi")


# ############################################################################
# PART 3 — Ayırma Teoremleri ve Koniler
# ############################################################################

# ============================================================== iki kümeyi ayırma
M_sep = hull(blob(-1.55, 0.15, 1.15, [(0.22, 3, 0.6), (0.14, 2, 1.9)]))
N_sep = hull(blob(1.75, -0.05, 1.05, [(0.2, 2, 2.4), (0.13, 3, 0.3)]))
p = panel(48, 48, 370, (-3.3, 3.3), (-2.1, 2.1))
region(p, M_sep, THEORY, 0.14, 2.1)
region(p, N_sep, PRACTICE, 0.14, 2.1)
hyperline(p, (1.0, 0.22), 0.06, BASE, 2.4)
p.arrow((0.06, 0.0), (0.06 + 0.7, 0.0 + 0.154), BASE, 1.9)
p.label(0.85, 0.19, "a", 8, -2, BASE, 12.5, "start", True, True)
p.label(-1.55, 0.15, "M", 0, 5, THEORY, 14, "middle", True, True)
p.label(1.75, -0.05, "N", 0, 5, PRACTICE, 14, "middle", True, True)
p.label(-2.6, -1.55, LANG + "a, m" + RANG + " " + LEQ + " b", 0, 0, THEORY, 11.5, "start", True)
p.label(2.9, 1.5, LANG + "a, n" + RANG + " " + GEQ + " b", 0, 0, PRACTICE, 11.5, "end", True)
p.label(-0.55, 1.85, "H: " + LANG + "a, x" + RANG + " = b", 0, 0, BASE, 11.5, "middle", True)
OUT["ayirma-hiperduzlemi"] = figure(
    470, 320, [p],
    "Bir H hiperdüzlemi, M'nin bütün noktalarını " + LANG + "a, x" + RANG + " " + LEQ + " b, N'nin bütün "
    "noktalarını " + LANG + "a, x" + RANG + " " + GEQ + " b yarı uzayında bırakıyorsa iki kümeyi <strong>"
    "ayırır</strong>. Ayırma, iki kümeyi tek bir lineer eşitsizlikle birbirinden ayırt edebilmek demektir; "
    "konveks analizin dualite kuramı bu fikrin üzerine kurulur.",
    aria="Iki konveks kumeyi ayiran hiperduzlem")

# ================================== Teorem: kapalı konveks kümeden bir noktayı ayırma
M_pt = hull(blob(-0.55, -0.1, 1.5, [(0.3, 2, 1.1), (0.16, 3, 2.6)]))
x0_pt = (2.75, 1.5)
y_pt = min(M_pt, key=lambda q: (q[0] - x0_pt[0]) ** 2 + (q[1] - x0_pt[1]) ** 2)
a_pt = (x0_pt[0] - y_pt[0], x0_pt[1] - y_pt[1])
b_pt = a_pt[0] * y_pt[0] + a_pt[1] * y_pt[1]
p = panel(48, 50, 360, (-2.7, 4.0), (-2.4, 2.9))
region(p, M_pt, THEORY, 0.13, 2.1)
hyperline(p, a_pt, b_pt, BASE, 2.4)
p.arrow(y_pt, x0_pt, PRACTICE, 2.3)
p.points([x0_pt], PRACTICE, 4.8)
p.points([y_pt], BASE, 4.6)
right_angle(p, y_pt, a_pt, (-a_pt[1], a_pt[0]), 0.28)
mid_pt = ((y_pt[0] + x0_pt[0]) / 2, (y_pt[1] + x0_pt[1]) / 2)
p.label(*mid_pt, "a = x" + SUB0 + " " + MINUS + " y", 10, -6, PRACTICE, 11.5, "start", True)
p.label(*x0_pt, "x" + SUB0, 10, 4, PRACTICE, 13, "start", True, True)
p.label(*y_pt, "y", -10, 6, BASE, 13, "end", True, True)
p.label(-1.7, -1.5, "M&#772;", 0, 0, THEORY, 14, "middle", True, True)
p.label(-1.7, 0.9, LANG + "a, x" + RANG + " " + LEQ + " b", 0, 0, THEORY, 11.5, "middle", True)
p.label(3.9, 2.55, LANG + "a, x" + SUB0 + RANG + " = b + " + EPS + SUB0, 0, 0, PRACTICE, 11.5, "end", True)
OUT["nokta-ayirma"] = figure(
    460, 350, [p],
    "Kapalı konveks bir M&#772; kümesi ile dışındaki bir x" + SUB0 + " noktası daima <strong>kesin</strong> "
    "ayrılır. İspatın kurulumu şekilde görülüyor: y, x" + SUB0 + "'a en yakın nokta; a = x" + SUB0 + " " +
    MINUS + " y ise ayıran hiperdüzlemin normali. Hiperdüzlem y'den geçer ve a'ya diktir; bütün M&#772; bir "
    "yanda kalırken x" + SUB0 + ", " + EPS + SUB0 + " = &#8214;a&#8214;&#178; kadar öte yandadır.",
    aria="Kapali konveks kumeden bir noktanin kesin ayrilmasi")

# ================================== kesin ayırma: kompaktlık neden gerekli
K1 = hull(blob(-1.9, 0.6, 0.95, [(0.18, 3, 0.9)]))
K2 = hull(blob(2.0, -0.5, 1.05, [(0.2, 2, 1.7)]))
p1 = panel(30, 50, 300, (-3.3, 3.5), (-2.5, 2.4))
region(p1, K1, THEORY, 0.14, 2.1)
region(p1, K2, PRACTICE, 0.14, 2.1)
a_k = (1.0, 0.42)
lo = max(a_k[0] * q[0] + a_k[1] * q[1] for q in K1)
hi = min(a_k[0] * q[0] + a_k[1] * q[1] for q in K2)
hyperline(p1, a_k, lo + 0.18 * (hi - lo), BASE, 2.2, "5 4")
hyperline(p1, a_k, hi - 0.18 * (hi - lo), BASE, 2.2, "5 4")
hyperline(p1, a_k, 0.5 * (lo + hi), BASE, 2.4)
p1.label(-1.9, 0.6, "M" + SUB1, 0, 4, THEORY, 13, "middle", True, True)
p1.label(2.0, -0.5, "M" + SUB2, 0, 4, PRACTICE, 13, "middle", True, True)
p1.label(0.35, 1.75, EPS + SUB0 + " &gt; 0", 6, 0, BASE, 11.5, "start", True)
panel_title(p1, "biri kompakt: kesin ayrılır", TEXT, 11.5)

OUT["kesin-ayirma"] = figure(
    380, 350, [p1],
    "M" + SUB1 + " kompakt, M" + SUB2 + " kapalı ve ikisi ayrık olduğunda aralarına pozitif genişlikte "
    "bir şerit sığar: ayıran hiperdüzlem hiçbir kümeye değmez ve arada " + EPS + SUB0 + " &gt; 0 "
    "genişliğinde bir boşluk kalır. Kesin ayırmayı sıradan ayırmadan ayıran şey tam olarak bu boşluktur.",
    aria="Kompakt ve kapali iki konveks kumenin kesin ayrilmasi")

p2 = panel(46, 50, 320, (-1.1, 5.7), (-2.3, 2.6))
hyp = [(t, 1.0 / t) for t in [0.42 + 5.0 * k / 220 for k in range(221)]]
upper = hyp + [(5.6, 2.6), (0.42, 2.6)]
p2.polygon(upper, THEORY, 0.13, stroke="none")
p2.line(hyp, THEORY, 2.2)
halfplane(p2, (0.0, 1.0), 0.0, -1, PRACTICE, 0.13, 2.2)
p2.label(2.6, 1.35, "M" + SUB1 + ": y " + GEQ + " 1/x", 0, 0, THEORY, 11.5, "middle", True)
p2.label(2.6, -1.3, "M" + SUB2 + ": y " + LEQ + " 0", 0, 0, PRACTICE, 11.5, "middle", True)
p2.label(5.4, 0.19, "aralık " + ARROW + " 0", -4, -8, REMARK, 11, "end", True)
panel_title(p2, "ikisi de kapalı: kesin ayrılamaz", TEXT, 11.5)

OUT["kesin-ayirma-karsi-ornek"] = figure(
    400, 350, [p2],
    "Kompaktlık koşulu atılamaz. Bu iki küme kapalı, konveks ve ayrıktır; buna karşılık aralarındaki "
    "uzaklık x büyüdükçe sıfıra iner. Onları ayıran tek doğru y = 0'dır ve o da M" + SUB2 + "'ye "
    "değdiğinden pozitif bir " + EPS + SUB0 + " boşluğu bırakılamaz: kümeler ayrılır ama "
    "<strong>kesin</strong> ayrılamaz.",
    aria="Kesin ayrilamayan iki kapali konveks kume")

# ======================================================================= koniler
q1 = panel(24, 54, 200, (-2.4, 2.4), (-2.4, 2.4))
q1.origin_axes(xlabel="", ylabel="", opacity=0.3)
wedge(q1, (0, 0), 18 * DEG, 78 * DEG, 3.4, THEORY, 0.16, 2.2)
q1.points([(0, 0)], TEXT, 3.2)
q1.text(0, -2.15, "konveks koni", THEORY, 11, "middle", True)
panel_title(q1, "açısal bölge", TEXT, 11.5)

q2 = panel(256, 54, 200, (-2.4, 2.4), (-2.4, 2.4))
q2.origin_axes(xlabel="", ylabel="", opacity=0.3)
wedge(q2, (0, 0), 15 * DEG, 45 * DEG, 3.4, PRACTICE, 0.16, 2.2)
wedge(q2, (0, 0), 115 * DEG, 155 * DEG, 3.4, PRACTICE, 0.16, 2.2)
q2.points([(0, 0)], TEXT, 3.2)
q2.text(0, -2.15, "koni ama konveks değil", PRACTICE, 11, "middle", True)
panel_title(q2, "iki açısal bölge", TEXT, 11.5)

q3 = panel(488, 54, 200, (-2.4, 2.4), (-2.4, 2.4))
q3.origin_axes(xlabel="", ylabel="", opacity=0.3)
halfplane(q3, (-0.45, 1.0), 0.0, -1, BASE, 0.16, 2.4)
q3.points([(0, 0)], TEXT, 3.2)
q3.text(0, -2.15, "konveks koni", BASE, 11, "middle", True)
panel_title(q3, "orijinden geçen yarı uzay", TEXT, 11.5)

OUT["koniler"] = figure(
    720, 320, [q1, q2, q3],
    "Koni, pozitif skaler ile çarpma altında kapalı kümedir: x kümedeyse bütün " + LAMBDA + "x (" + LAMBDA +
    " &gt; 0) ışını da kümededir. Ortadaki küme bu koşulu sağlar ama konveks değildir — iki kolun noktalarını "
    "birleştiren kiriş dışarı çıkar. Bir koninin konveks olması, herhangi iki elemanının konik "
    "kombinasyonlarını içermesiyle aynı şeydir.",
    css_class=WIDE, aria="Konveks koni, konveks olmayan koni ve yari uzay")

# ==================================================================== dual koni
a1_d, a2_d = 20 * DEG, 80 * DEG
p = panel(52, 50, 360, (-2.9, 2.9), (-2.5, 2.9))
p.origin_axes(xlabel="", ylabel="", opacity=0.3)
wedge(p, (0, 0), a2_d - 90 * DEG, a1_d + 90 * DEG, 3.9, PRACTICE, 0.12, 2.0)
wedge(p, (0, 0), a1_d, a2_d, 3.9, THEORY, 0.22, 2.6)
right_angle(p, (0, 0), (math.cos(a1_d), math.sin(a1_d)),
            (math.cos(a1_d + 90 * DEG), math.sin(a1_d + 90 * DEG)), 0.5, REMARK, 1.3, 0.9)
p.points([(0, 0)], TEXT, 3.2)
p.label(2.0 * math.cos(50 * DEG), 2.0 * math.sin(50 * DEG), "K", 0, 4, THEORY, 15, "middle", True, True)
p.label(2.45 * math.cos(2 * DEG), 2.45 * math.sin(2 * DEG), "K*", 0, 4, PRACTICE, 15, "middle", True, True)
p.label(2.7 * math.cos(a1_d), 2.7 * math.sin(a1_d), "u" + SUB1, 6, -4, THEORY, 12, "start", True, True)
p.label(2.7 * math.cos(a2_d), 2.7 * math.sin(a2_d), "u" + SUB2, 6, -4, THEORY, 12, "start", True, True)
p.text(-2.8, -2.15, "K* = { x* : " + LANG + "x, x*" + RANG + " " + GEQ + " 0, her x " + IN + " K }",
       PRACTICE, 11.5, "start", True)
OUT["dual-koni"] = figure(
    470, 380, [p],
    "u" + SUB1 + " ile u" + SUB2 + " ışınlarının gerdiği K konisi ve onun dual konisi K*. K* bir x* "
    "vektörünü, K'nın <strong>her</strong> elemanıyla iç çarpımı negatif olmadığında içerir; bu, K'nın iki "
    "kenar ışınına dik iki yarı düzlemin kesişimi demektir. Dar bir koninin duali geniş olur: K burada "
    "60&#176;, K* ise 120&#176; açıklıktadır. Dual koni her zaman kapalı ve konvekstir.",
    aria="Bir koninin dual konisi")


# ############################################################################
# PART 4 — Konveks Fonksiyonlar
# ############################################################################

# ==================================================================== epigraf
def _ef(x):
    return 0.4 * x ** 2 + 0.3


p1 = Plot(46, 46, 276, 214, (-2.6, 2.6), (-0.2, 3.1))
p1.axes([-2, -1, 0, 1, 2], [0, 1, 2, 3], "x", "")
epi_pts = curve(_ef, -2.4, 2.4) + [(2.4, 3.1), (-2.4, 3.1)]
p1.polygon(epi_pts, THEORY, 0.16, stroke="none")
p1.line(curve(_ef, -2.4, 2.4), THEORY, 2.4)
p1.label(0.0, 2.0, "epi(f)", 0, 0, THEORY, 13, "middle", True)
p1.label(-1.75, _ef(-1.75), "f", -10, 0, THEORY, 13, "end", True, True)
panel_title(p1, "konveks fonksiyon", TEXT, 11.5)


def _eg(x):
    return 0.25 * x ** 4 - x ** 2 + 1.2


p2 = Plot(392, 46, 276, 214, (-2.6, 2.6), (-0.2, 3.1))
p2.axes([-2, -1, 0, 1, 2], [0, 1, 2, 3], "x", "")
epi_g = curve(_eg, -2.4, 2.4) + [(2.4, 3.1), (-2.4, 3.1)]
p2.polygon(epi_g, PRACTICE, 0.14, stroke="none")
p2.line(curve(_eg, -2.4, 2.4), PRACTICE, 2.4)
seg(p2, (-1.6, _eg(-1.6)), (1.6, _eg(1.6)), BASE, 2.2, "5 4")
p2.points([(-1.6, _eg(-1.6)), (1.6, _eg(1.6))], BASE, 4.2)
cross(p2, (0.0, _eg(-1.6)), BASE, 5.5, 2.0)
p2.label(0.0, _eg(-1.6), "kiriş epigraftan çıkar", 0, 20, BASE, 10.5, "middle", True)
p2.label(0.0, 2.35, "epi(g)", 0, 0, PRACTICE, 13, "middle", True)
panel_title(p2, "konveks olmayan fonksiyon", TEXT, 11.5)

OUT["epigraf"] = figure(
    700, 300, [p1, p2],
    "Bir fonksiyonun grafiküstü (epigraf) kümesi, grafiğinin üzerinde kalan noktalardan oluşur. Konveks "
    "fonksiyon <strong>tanımı gereği</strong> epigrafı konveks olan fonksiyondur. Sağdaki fonksiyonda "
    "epigrafın iki noktasını birleştiren kiriş kümenin dışına düşer; bu, kirişin grafiğin altına inmesiyle "
    "aynı şeydir.",
    css_class=WIDE, aria="Konveks ve konveks olmayan fonksiyonlarin epigraflari")

# ======================================================== kiriş eşitsizliği
def _kf(x):
    return 0.45 * x ** 2 + 0.35


kx1, kx2, klam = -1.8, 2.0, 0.35
kxm = klam * kx1 + (1 - klam) * kx2
kym = klam * _kf(kx1) + (1 - klam) * _kf(kx2)
p = Plot(56, 46, 420, 258, (-2.7, 2.8), (-0.35, 3.0))
p.axes([-2, -1, 0, 1, 2], [0, 1, 2, 3], "x", "")
p.line(curve(_kf, -2.4, 2.4), THEORY, 2.4)
seg(p, (kx1, _kf(kx1)), (kx2, _kf(kx2)), PRACTICE, 2.4)
p.points([(kx1, _kf(kx1)), (kx2, _kf(kx2))], PRACTICE, 4.4)
seg(p, (kxm, _kf(kxm)), (kxm, kym), BASE, 2.6)
p.points([(kxm, _kf(kxm)), (kxm, kym)], BASE, 4.4)
p.vline(kxm, -0.35, _kf(kxm), REMARK, "4 3", 0.5)
p.vline(kx1, -0.35, _kf(kx1), REMARK, "4 3", 0.4)
p.vline(kx2, -0.35, _kf(kx2), REMARK, "4 3", 0.4)
p.label(kx1, -0.35, "x" + SUB1, 0, 17, TEXT, 11.5, "middle", False, True)
p.label(kx2, -0.35, "x" + SUB2, 0, 17, TEXT, 11.5, "middle", False, True)
p.label(kxm, -0.35, LAMBDA + "x" + SUB1 + " + (1" + MINUS + LAMBDA + ")x" + SUB2, 0, 17, TEXT, 11, "middle")
p.label(kxm, kym, LAMBDA + "f(x" + SUB1 + ") + (1" + MINUS + LAMBDA + ")f(x" + SUB2 + ")", 10, -4, PRACTICE, 11, "start", True)
p.label(kxm, _kf(kxm), "f(" + LAMBDA + "x" + SUB1 + " + (1" + MINUS + LAMBDA + ")x" + SUB2 + ")", 10, 6, BASE, 11, "start", True)
OUT["kiris-esitsizligi"] = figure(
    540, 340, [p],
    "Konvekslik eşitsizliğinin okunuşu: iki nokta arasındaki <strong>kiriş daima grafiğin üstünde</strong> "
    "kalır. Yatay eksende " + LAMBDA + " ile alınan ağırlıklı ortalama, düşey eksende fonksiyon değerlerinin "
    "aynı ağırlıklarla ortalamasına karşılık gelir; mavi parça bu iki değer arasındaki farktır. Kesin "
    "konvekslikte bu fark uç noktalar dışında hep pozitiftir.",
    aria="Konveks fonksiyonda kiris grafigin ustundedir")

# ================================================= kesin konveks / konveks
p1 = Plot(46, 46, 276, 200, (-2.4, 2.4), (-0.3, 2.7))
p1.axes([-2, -1, 0, 1, 2], [0, 1, 2], "x", "")
p1.line(curve(lambda x: 0.42 * x ** 2 + 0.25, -2.2, 2.2), THEORY, 2.4)
seg(p1, (-1.7, 0.42 * 2.89 + 0.25), (1.5, 0.42 * 2.25 + 0.25), PRACTICE, 2.2, "5 4")
p1.points([(-1.7, 0.42 * 2.89 + 0.25), (1.5, 0.42 * 2.25 + 0.25)], PRACTICE, 4.2)
p1.label(-0.1, 1.35, "kiriş grafiğin kesin üstünde", 0, 0, PRACTICE, 10.5, "middle", True)
panel_title(p1, "kesin konveks", TEXT, 11.5)


def _pl(x):
    return max(-1.15 * x - 1.15, 0.0, 0.95 * x - 0.95)


p2 = Plot(392, 46, 276, 200, (-2.4, 2.4), (-0.3, 2.7))
p2.axes([-2, -1, 0, 1, 2], [0, 1, 2], "x", "")
p2.line(curve(_pl, -2.2, 2.2, 300), THEORY, 2.4)
seg(p2, (-0.75, 0.0), (0.8, 0.0), PRACTICE, 3.4)
p2.points([(-0.75, 0.0), (0.8, 0.0)], PRACTICE, 4.2)
p2.label(0.0, 0.0, "kiriş grafiğin üzerinde", 0, -12, PRACTICE, 10.5, "middle", True)
panel_title(p2, "konveks ama kesin değil", TEXT, 11.5)

OUT["kesin-konvekslik"] = figure(
    700, 290, [p1, p2],
    "Kesin konvekslikte uç noktalar dışında kiriş ile grafik hiç değmez. Sağdaki fonksiyon konvekstir ama "
    "düz parçası üzerinde kiriş grafiğin tam üstüne oturur; eşitsizlik eşitliğe dönüştüğünden kesin konveks "
    "değildir. Kesin konvekslik, bir eniyileme probleminin çözümünün tek olduğunu garanti etmek için "
    "istenen ek koşuldur.",
    css_class=WIDE, aria="Kesin konveks ve kesin olmayan konveks fonksiyon")

# ==================================================== konvekslerin supremumu
LINES = [(-1.45, -0.15), (-0.55, 0.55), (0.45, 0.75), (1.35, -0.05)]
p = Plot(52, 46, 400, 240, (-2.0, 2.0), (-1.3, 2.6))
p.axes([-1, 0, 1], [-1, 0, 1, 2], "x", "")
for m, c in LINES:
    pseg(p, (-1.75, m * -1.75 + c), (1.75, m * 1.75 + c), REMARK, 1.3, "6 5", 0.8)
p.line(curve(lambda x: max(m * x + c for m, c in LINES), -1.6, 1.6, 400), THEORY, 2.8)
p.label(-1.6, max(m * -1.6 + c for m, c in LINES), "f = sup f" + SUBI, 6, -10, THEORY, 12, "start", True)
p.label(1.6, LINES[1][0] * 1.6 + LINES[1][1], "f" + SUBI, 6, 8, REMARK, 11.5, "start", True, True)
OUT["supremum-konveks"] = figure(
    500, 320, [p],
    "Konveks fonksiyonların supremumu yine konvekstir, çünkü epi(sup f" + SUBI + ") = " + CAP +
    " epi(f" + SUBI + ") olur ve konveks kümelerin kesişimi konvekstir. Şekilde dört afin fonksiyonun "
    "supremumu parçalı doğrusal bir konveks fonksiyon verir. Tersine, her konveks fonksiyon kendisini "
    "alttan destekleyen afin fonksiyonların supremumu olarak yazılabilir.",
    aria="Afin fonksiyonlarin supremumu konvekstir")

# ================================================================ Jensen eşitsizliği
def _jf(x):
    return 0.4 * x ** 2 + 0.3


JX = [-1.9, 0.2, 1.9]
JL = [0.3, 0.45, 0.25]
jm = sum(l * x for l, x in zip(JL, JX))
jv = sum(l * _jf(x) for l, x in zip(JL, JX))
p = Plot(56, 46, 400, 240, (-2.5, 2.5), (-0.35, 2.6))
p.axes([-2, -1, 0, 1, 2], [0, 1, 2], "x", "")
gr = [(x, _jf(x)) for x in JX]
p.polygon(gr, PRACTICE, 0.16, stroke="none")
p.line(gr + [gr[0]], PRACTICE, 1.8, "5 4")
p.line(curve(_jf, -2.3, 2.3), THEORY, 2.4)
p.points(gr, PRACTICE, 4.4)
seg(p, (jm, _jf(jm)), (jm, jv), BASE, 2.6)
p.points([(jm, jv), (jm, _jf(jm))], BASE, 4.4)
for x, l in zip(JX, JL):
    p.vline(x, -0.35, _jf(x), REMARK, "4 3", 0.4)
    p.label(x, -0.35, LAMBDA + " = " + ("%.2f" % l).replace(".", ","), 0, 17, REMARK, 10.5, "middle")
p.label(jm, jv, "&#8721; " + LAMBDA + SUBI + " f(x" + SUBI + ")", 10, -2, PRACTICE, 11.5, "start", True)
p.label(jm, _jf(jm), "f(&#8721; " + LAMBDA + SUBI + " x" + SUBI + ")", 10, 12, BASE, 11.5, "start", True)
OUT["jensen"] = figure(
    500, 330, [p],
    "Jensen eşitsizliği, kiriş eşitsizliğinin sonlu çok noktaya genellemesidir. Grafik üzerindeki üç noktanın "
    "ağırlıklı ortalaması, üçgenin — yani epigrafın — içinde kalır; aynı ağırlıklarla alınan apsis "
    "ortalamasının fonksiyon değeri ise daima bunun altındadır. Ağırlıkların negatif olmaması ve toplamlarının "
    "1 etmesi şarttır.",
    aria="Jensen esitsizligi: uc noktali agirlikli ortalama")

# ============================================================== norm konvekstir
p1 = Plot(46, 46, 262, 196, (-2.4, 2.4), (-0.35, 2.5))
p1.axes([-2, -1, 0, 1, 2], [0, 1, 2], "x", "")
p1.line(curve(abs, -2.2, 2.2, 400), THEORY, 2.6)
seg(p1, (-1.7, 1.7), (1.2, 1.2), PRACTICE, 2.2, "5 4")
p1.points([(-1.7, 1.7), (1.2, 1.2)], PRACTICE, 4.2)
p1.label(0.0, 1.5, "kiriş üstte", 0, 0, PRACTICE, 10.5, "middle", True)
panel_title(p1, "f(x) = |x|", TEXT, 11.5)

p2 = panel(376, 46, 240, (-1.75, 1.75), (-1.75, 1.75))
p2.origin_axes(xlabel="", ylabel="", opacity=0.3)
region(p2, rect(-1.25, -1.25, 1.25, 1.25), REMARK, 0.08, 1.9)
region(p2, circle_pts(0, 0, 1.25, 0, 2 * PI, 96), THEORY, 0.10, 2.1)
region(p2, [(1.25, 0), (0, 1.25), (-1.25, 0), (0, -1.25)], PRACTICE, 0.14, 2.1)
p2.label(1.25, 1.25, "&#8214;x&#8214;" + "&#8734;", 6, -4, REMARK, 11.5, "start", True)
p2.label(0.88, 0.88, "&#8214;x&#8214;" + SUB2, 6, -4, THEORY, 11.5, "start", True)
p2.label(0.62, 0.62, "&#8214;x&#8214;" + SUB1, -4, 14, PRACTICE, 11.5, "end", True)
panel_title(p2, "birim yuvarlar", TEXT, 11.5)

OUT["norm-konveks"] = figure(
    680, 300, [p1, p2],
    "Norm fonksiyonu üçgen eşitsizliği ile homojenlik sayesinde konvekstir: &#8214;" + LAMBDA + "x" + SUB1 +
    " + (1" + MINUS + LAMBDA + ")x" + SUB2 + "&#8214; " + LEQ + " " + LAMBDA + "&#8214;x" + SUB1 + "&#8214; + "
    "(1" + MINUS + LAMBDA + ")&#8214;x" + SUB2 + "&#8214;. Bunun geometrik karşılığı, her normun birim "
    "yuvarının konveks olmasıdır — birim yuvar, normun 1 seviye kümesidir.",
    css_class=WIDE, aria="Norm konvekstir ve birim yuvarlari konvekstir")

# ================================================= Hessian: pozitif tanımlı / eyer
def _qpd(x, y):
    return x * x + 2 * x * y + 2 * y * y            # H = [[2, 2], [2, 4]], pozitif tanımlı


p1 = panel(34, 52, 268, (-2.9, 2.9), (-2.9, 2.9))
p1.origin_axes(xlabel="", ylabel="", opacity=0.3)
for c, op in ((2.4, 0.06), (1.2, 0.06), (0.4, 0.10)):
    lvl = []
    for k in range(145):
        th = 2 * PI * k / 144
        r = math.sqrt(c / _qpd(math.cos(th), math.sin(th)))
        lvl.append((r * math.cos(th), r * math.sin(th)))
    p1.polygon(lvl, THEORY, op, stroke="none")
    p1.line(lvl, THEORY, 1.9)
p1.points([(0, 0)], PRACTICE, 4.2)
p1.label(0, 0, "en küçük", 10, 16, PRACTICE, 11, "start", True)
p1.text(-2.8, -2.7, "seviye kümeleri konveks", THEORY, 11, "start", True)
panel_title(p1, "pozitif tanımlı Hessian", TEXT, 11.5)


def _qsad(x, y):
    return y * y - x * y                            # H = [[0, -1], [-1, 2]], tanımsız


p2 = panel(376, 52, 268, (-2.9, 2.9), (-2.9, 2.9))
p2.origin_axes(xlabel="", ylabel="", opacity=0.3)
hyperline(p2, (0.0, 1.0), 0.0, REMARK, 1.3, "5 4", 0.7)
hyperline(p2, (1.0, -1.0), 0.0, REMARK, 1.3, "5 4", 0.7)
for c, col in ((0.7, PRACTICE), (-0.7, BASE)):
    for lo, hi in ((0.22, 3.4), (-3.4, -0.22)):
        br = [(y - c / y, y) for y in [lo + (hi - lo) * k / 260 for k in range(261)]]
        for run in runs_in(br, p2):
            p2.line(run, col, 1.9)
cross(p2, (0, 0), TEXT, 5.5, 2.0)
p2.label(0, 0, "eyer noktası", 9, 16, TEXT, 11, "start", True)
p2.label(-1.6, 1.7, "q &gt; 0", 0, 0, PRACTICE, 11, "middle", True)
p2.label(2.15, 1.0, "q &lt; 0", 0, 0, BASE, 11, "middle", True)
panel_title(p2, "tanımsız Hessian", TEXT, 11.5)

OUT["hessian-seviye"] = figure(
    690, 350, [p1, p2],
    "İki kez sürekli türevlenebilir bir fonksiyon, ancak Hessian matrisi her noktada pozitif yarı-tanımlıysa "
    "konvekstir. Solda pozitif tanımlı bir kuadratik formun seviye eğrileri iç içe elipslerdir ve alt seviye "
    "kümeleri konvekstir. Sağdaki formda öncü esas minör " + DELTA_CAP + SUB2 + " negatif olduğundan Hessian "
    "tanımsızdır: seviye eğrileri hiperbol, orijin ise ne minimum ne maksimum olan bir eyer noktasıdır.",
    css_class=WIDE, aria="Pozitif tanimli ve tanimsiz Hessian icin seviye egrileri")

# =========================================== küpsel terim konveksliği bozar
def _cub(z):
    return z ** 3 - 3 * z


p = Plot(56, 48, 400, 250, (-2.5, 2.5), (-3.7, 3.7))
p.polygon(rect(-2.15, -3.7, 0.0, 3.7), PRACTICE, 0.09, stroke="none")
p.axes([-2, -1, 0, 1, 2], [-2, 0, 2], "z", "")
p.line(curve(_cub, -2.15, 2.15, 300), THEORY, 2.4)
seg(p, (-2.0, _cub(-2.0)), (-0.5, _cub(-0.5)), PRACTICE, 2.2, "5 4")
p.points([(-2.0, _cub(-2.0)), (-0.5, _cub(-0.5))], PRACTICE, 4.2)
p.label(-1.25, -0.31, "kiriş grafiğin altında", -6, 18, PRACTICE, 11, "middle", True)
p.label(-1.15, 3.35, "z &lt; 0: f&#8243; &lt; 0", 0, 0, PRACTICE, 11, "middle", True)
p.label(1.15, 3.35, "z &gt; 0: f&#8243; &gt; 0", 0, 0, BASE, 11, "middle", True)
OUT["kubik-konveks-degil"] = figure(
    500, 330, [p],
    "z<sup>3</sup> " + MINUS + " 3z fonksiyonunun ikinci türevi 6z'dir ve z &lt; 0 için negatiftir. Orada "
    "kiriş grafiğin <strong>altına</strong> düşer, dolayısıyla fonksiyon konveks değildir. Çok değişkenli "
    "bir fonksiyonda tek bir küpsel terimin bulunması da aynı şeyi yapar: Hessian, o değişkenin negatif "
    "olduğu bölgede pozitif yarı-tanımlı olmaktan çıkar.",
    aria="Kupsel terim konveksligi bozar")

# ================================================================ seviye kümeleri
def _lf(x):
    return 0.5 * x ** 2 - 0.4 * x + 0.3


ALP = 1.2
r_lo, r_hi = -1.0, 1.8                                # 0,5x² - 0,4x + 0,3 = 1,2 kökleri
p1 = Plot(46, 46, 276, 206, (-2.3, 2.9), (-0.55, 2.6))
p1.axes([-2, -1, 0, 1, 2], [0, 1, 2], "x", "")
p1.line([(-2.2, ALP), (2.8, ALP)], PRACTICE, 1.8, "5 4")
p1.line(curve(_lf, -1.75, 2.55), THEORY, 2.4)
p1.line([(r_lo, -0.32), (r_hi, -0.32)], BASE, 4.0)
p1.points([(r_lo, -0.32), (r_hi, -0.32)], BASE, 4.2)
p1.vline(r_lo, -0.32, ALP, REMARK, "4 3", 0.5)
p1.vline(r_hi, -0.32, ALP, REMARK, "4 3", 0.5)
p1.label(2.8, ALP, ALPHA, -2, -8, PRACTICE, 12, "end", True, True)
p1.label(0.4, -0.32, "f(x) " + LEQ + " " + ALPHA + ": bir aralık", 0, 18, BASE, 11, "middle", True)
panel_title(p1, "konveks f", TEXT, 11.5)

p2 = Plot(392, 46, 276, 206, (-1.9, 1.9), (-3.2, 3.2))
p2.axes([-1, 0, 1], [-2, 0, 2], "x", "")
p2.line([(-1.8, 0.5), (1.8, 0.5)], PRACTICE, 1.8, "5 4")
p2.line(curve(lambda x: x ** 3, -1.45, 1.45, 300), THEORY, 2.4)
p2.line([(-1.85, -2.6), (0.5 ** (1 / 3), -2.6)], BASE, 4.0)
p2.arrow((-1.35, -2.6), (-1.95, -2.6), BASE, 1.5, head=7.0)
p2.points([(0.5 ** (1 / 3), -2.6)], BASE, 4.2)
p2.vline(0.5 ** (1 / 3), -2.6, 0.5, REMARK, "4 3", 0.5)
seg(p2, (-1.4, -2.744), (-0.2, -0.008), PRACTICE, 2.0, "5 4")
p2.points([(-1.4, -2.744), (-0.2, -0.008)], PRACTICE, 4.0)
p2.label(1.8, 0.5, ALPHA, -2, -8, PRACTICE, 12, "end", True, True)
p2.label(-1.55, -1.1, "kiriş altta", -4, 0, PRACTICE, 10.5, "end", True)
panel_title(p2, "f(x) = x&#179;: tersi doğru değil", TEXT, 11.5)

OUT["seviye-kumeleri"] = figure(
    700, 300, [p1, p2],
    "Konveks bir fonksiyonun bütün L<sub>f</sub>(" + ALPHA + ") = { x : f(x) " + LEQ + " " + ALPHA +
    " } seviye kümeleri konvekstir. Bunun <strong>tersi doğru değildir</strong>: sağdaki x<sup>3</sup> "
    "fonksiyonunun her seviye kümesi bir aralık, yani konvekstir; buna karşılık kiriş grafiğin altına "
    "indiğinden fonksiyonun kendisi konveks değildir. Seviye kümeleri konveks olan fonksiyonlara "
    "kuazikonveks denir.",
    css_class=WIDE, aria="Seviye kumeleri konveks ama fonksiyon konveks degil")

# ================================================================== yönlü türev
def _df(x):
    return 0.55 * x ** 2 + 0.3


X0 = -0.6
p = Plot(56, 48, 400, 244, (-1.35, 1.85), (-0.15, 2.1))
p.axes([-1, 0, 1], [0, 1, 2], "x", "")
p.line(curve(_df, -1.2, 1.7), THEORY, 2.4)
for lam_d, col in ((1.6, REMARK), (0.9, REMARK), (0.45, PRACTICE)):
    x1 = X0 + lam_d
    p.line([(X0 - 0.3, _df(X0) + (_df(x1) - _df(X0)) / lam_d * (-0.3)),
            (x1 + 0.12, _df(X0) + (_df(x1) - _df(X0)) / lam_d * (lam_d + 0.12))], col, 1.5, "5 4", 0.85)
    p.points([(x1, _df(x1))], col, 3.8)
    p.label(x1, _df(x1), LAMBDA + " = " + ("%.2f" % lam_d).rstrip("0").rstrip(".").replace(".", ","),
            6, -6, col, 10.5, "start", True)
sl = 1.1 * X0
p.line([(X0 - 0.55, _df(X0) + sl * (-0.55)), (X0 + 0.95, _df(X0) + sl * 0.95)], BASE, 2.4)
p.points([(X0, _df(X0))], BASE, 4.6)
p.label(X0, _df(X0), "x" + SUB0, -8, 14, BASE, 12, "end", True, True)
p.label(X0 + 0.95, _df(X0) + sl * 0.95, "f&#8242;(x" + SUB0 + "; d)", 6, 10, BASE, 11.5, "start", True)
OUT["yonlu-turev"] = figure(
    500, 330, [p],
    "Yönlü türev, x" + SUB0 + " noktasından d yönünde çizilen kirişlerin eğiminin " + LAMBDA + " " + ARROW +
    " 0<sup>+</sup> limitidir. Konveks fonksiyonlarda bu eğimler " + LAMBDA + " küçüldükçe <strong>azalır</"
    "strong> ve alttan sınırlıdır; bu yüzden limit her yönde vardır — fonksiyon o noktada türevlenebilir "
    "olmasa bile.",
    aria="Yonlu turev: kiris egimlerinin limiti")

# ==================================================================== subgradient
def _sf(x):
    return abs(x) + 0.25 * x ** 2


p = Plot(56, 48, 410, 250, (-2.2, 2.5), (-0.9, 2.9))
p.axes([-2, -1, 0, 1, 2], [0, 1, 2], "x", "")
for s in (-1.0, -0.5, 0.0, 0.5, 1.0):
    pseg(p, (-2.05, s * -2.05), (2.05, s * 2.05), REMARK, 1.3, "5 4", 0.85)
p.line(curve(_sf, -1.95, 1.95, 400), THEORY, 2.6)
p.points([(0.0, 0.0)], PRACTICE, 4.8)
XT = 1.45
slt = 1.0 + 0.5 * XT
p.line([(XT - 1.1, _sf(XT) + slt * (-1.1)), (XT + 0.85, _sf(XT) + slt * 0.85)], BASE, 2.2)
p.points([(XT, _sf(XT))], BASE, 4.6)
p.label(0.0, 0.0, "kırılma: " + "&#8706;" + "f(0) = [" + MINUS + "1, 1]", -8, 22, PRACTICE, 11, "end", True)
p.label(XT, _sf(XT), "düzgün nokta: tek teğet", 8, -10, BASE, 11, "start", True)
OUT["subgradient"] = figure(
    510, 340, [p],
    "Bir x* subgradienti, grafiğe x" + SUB0 + " noktasında değen ve fonksiyonun her yerde <strong>altında</"
    "strong> kalan afin fonksiyonun eğimidir: f(x) " + MINUS + " f(x" + SUB0 + ") " + GEQ + " " + LANG +
    "x*, x " + MINUS + " x" + SUB0 + RANG + ". Düzgün noktalarda böyle tek bir doğru — teğet — vardır. "
    "Kırılma noktasında ise kesikli doğruların hepsi işe yarar; subgradientler bir aralık oluşturur.",
    aria="Subgradient: grafigi alttan destekleyen afin fonksiyonlar")

# ================================================== |x| fonksiyonunun subdiferansiyeli
p1 = Plot(46, 48, 276, 200, (-2.2, 2.2), (-1.05, 2.35))
p1.axes([-2, -1, 0, 1, 2], [0, 1, 2], "x", "")
for s in (-1.0, -0.6, -0.2, 0.2, 0.6, 1.0):
    pseg(p1, (-2.0, s * -2.0), (2.0, s * 2.0), REMARK, 1.3, "5 4", 0.85)
p1.line(curve(abs, -2.0, 2.0, 400), THEORY, 2.8)
p1.points([(0.0, 0.0)], PRACTICE, 4.8)
p1.label(-1.35, 1.35, "f(x) = |x|", -6, -6, THEORY, 11.5, "end", True)
panel_title(p1, "destekleyen doğrular yelpazesi", TEXT, 11.5)

p2 = Plot(392, 48, 276, 200, (-2.2, 2.2), (-1.75, 1.75))
p2.axes([-2, -1, 0, 1, 2], [-1, 0, 1], "x", "")
p2.line([(-2.05, -1.0), (0.0, -1.0)], PRACTICE, 2.8)
p2.line([(0.0, 1.0), (2.05, 1.0)], PRACTICE, 2.8)
p2.line([(0.0, -1.0), (0.0, 1.0)], PRACTICE, 2.8)
p2.points([(0.0, -1.0), (0.0, 1.0)], PRACTICE, 4.4)
p2.label(0.0, 0.0, "[" + MINUS + "1, 1]", 9, 4, PRACTICE, 11.5, "start", True)
p2.label(-1.4, -1.0, MINUS + "1", 0, -9, PRACTICE, 11, "middle", True)
p2.label(1.4, 1.0, "+1", 0, -9, PRACTICE, 11, "middle", True)
panel_title(p2, "&#8706;f(x) grafiği", TEXT, 11.5)

OUT["subdiferansiyel-mutlak-deger"] = figure(
    700, 300, [p1, p2],
    "f(x) = |x| fonksiyonu 0 noktasında türevlenebilir değildir ama subdiferansiyeli boş değildir: her "
    "x " + IN + " R için |x| " + GEQ + " x*x eşitsizliğini sağlayan x* değerleri tam olarak [" + MINUS +
    "1, 1] aralığını doldurur. Sağda " + "&#8706;" + "f'nin kendisi bir küme değerli dönüşüm olarak "
    "çizilmiştir: sıfırın dışında tek nokta, sıfırda ise bütün bir aralık.",
    css_class=WIDE, aria="Mutlak deger fonksiyonunun subdiferansiyeli")

# ============================================================== destek fonksiyonu
A_sup = hull(blob(0.0, 0.0, 1.35, [(0.3, 2, 0.8), (0.15, 3, 2.2)]))
p = panel(52, 48, 360, (-2.4, 3.6), (-2.3, 2.4))
p.origin_axes(xlabel="", ylabel="", opacity=0.3)
region(p, A_sup, THEORY, 0.14, 2.1)
dirv = (0.82, 0.58)
best = max(A_sup, key=lambda q: dirv[0] * q[0] + dirv[1] * q[1])
Sval = dirv[0] * best[0] + dirv[1] * best[1]
hyperline(p, dirv, Sval, PRACTICE, 2.3)
p.arrow((0, 0), (dirv[0] * 1.15, dirv[1] * 1.15), BASE, 2.2)
p.points([best], PRACTICE, 4.6)
p.points([(0, 0)], TEXT, 3.2)
p.label(dirv[0] * 1.15, dirv[1] * 1.15, "x", 8, 6, BASE, 13, "start", True, True)
p.label(*best, "en uzak nokta", 10, -8, PRACTICE, 11, "start", True)
p.label(0.0, -1.3, "A", 0, 0, THEORY, 14, "middle", True, True)
p.text(-2.3, 2.2, "S(x, A) = sup " + LANG + "x, a" + RANG, PRACTICE, 12, "start", True)
OUT["destek-fonksiyonu"] = figure(
    470, 350, [p],
    "Bir kümenin destek fonksiyonu, verilen x yönünde kümenin ne kadar uzağa gittiğini ölçer: "
    "S(x, A) = sup { " + LANG + "x, a" + RANG + " : a " + IN + " A }. Değeri, x'e dik olup A'yı destekleyen "
    "hiperdüzlemin konumunu belirler; supremum, o hiperdüzleme değen noktada alınır. Destek fonksiyonu her "
    "zaman konveks ve pozitif homojendir.",
    aria="Destek fonksiyonu ve destekleyen hiperduzlem")

# =========================================== indikatör ve pozitif homojen fonksiyon
p1 = Plot(46, 50, 276, 190, (-2.4, 2.4), (-0.5, 2.6))
p1.axes([-2, -1, 0, 1, 2], [0, 1, 2], "x", "")
p1.line([(-0.9, 0.0), (1.3, 0.0)], THEORY, 4.0)
p1.points([(-0.9, 0.0), (1.3, 0.0)], THEORY, 4.4)
for x in (-2.1, -1.75, -1.4, 1.7, 2.05):
    p1.arrow((x, 0.0), (x, 2.45), PRACTICE, 1.5, head=7.0)
p1.label(0.2, 0.0, "A", 0, 20, THEORY, 12.5, "middle", True, True)
p1.label(-1.75, 2.45, "+" + INFTY, 0, -8, PRACTICE, 11.5, "middle", True)
p1.label(1.9, 2.45, "+" + INFTY, 0, -8, PRACTICE, 11.5, "middle", True)
panel_title(p1, "indikatör " + DELTA + "(x, A)", TEXT, 11.5)


def _ph(x):
    return max(1.5 * x, -0.8 * x)


p2 = Plot(392, 50, 276, 190, (-2.4, 2.4), (-0.5, 3.4))
p2.axes([-2, -1, 0, 1, 2], [0, 1, 2, 3], "x", "")
epi_h = curve(_ph, -2.2, 2.2, 300) + [(2.2, 3.4), (-2.2, 3.4)]
p2.polygon(epi_h, BASE, 0.14, stroke="none")
p2.line(curve(_ph, -2.2, 2.2, 300), THEORY, 2.6)
p2.points([(0.8, _ph(0.8)), (1.6, _ph(1.6))], PRACTICE, 4.4)
p2.vline(0.8, 0.0, _ph(0.8), REMARK, "4 3", 0.5)
p2.vline(1.6, 0.0, _ph(1.6), REMARK, "4 3", 0.5)
p2.label(0.8, _ph(0.8), "f(x)", -8, -4, PRACTICE, 11, "end", True)
p2.label(1.6, _ph(1.6), "f(2x) = 2f(x)", 6, -4, PRACTICE, 11, "start", True)
p2.label(0.0, 2.5, "epi(f) bir konidir", 0, 0, BASE, 11, "middle", True)
panel_title(p2, "pozitif homojen f", TEXT, 11.5)

OUT["indikator-pozitif-homojen"] = figure(
    700, 300, [p1, p2],
    "Konveks analizin iki temel yapı taşı. İndikatör fonksiyonu bir kısıtı fonksiyona çevirir: A üzerinde 0, "
    "dışında +" + INFTY + " değerini alır, böylece &#8220;x " + IN + " A&#8221; koşulu amaç fonksiyonunun "
    "içine gömülür ve A konveksse " + DELTA + " de konveks olur. Pozitif homojen fonksiyonlarda "
    "f(" + LAMBDA + "x) = " + LAMBDA + "f(x) olduğundan epigraf bir konidir; destek fonksiyonu bu ailenin en "
    "önemli örneğidir.",
    css_class=WIDE, aria="Indikator fonksiyonu ve pozitif homojen fonksiyon")


# ---------------------------------------------------------------------------
for name, content in OUT.items():
    with io.open(os.path.join(OUT_DIR, "convex-%s.md" % name), "w", encoding="utf-8") as f:
        f.write(content)
print("generated %d figures:" % len(OUT))
print("  " + ", ".join(sorted(OUT)))
