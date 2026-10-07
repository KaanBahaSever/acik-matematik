# -*- coding: utf-8 -*-
"""
Figures of the chapter "Bir İzometrinin Teğet Dönüşümü"
(dersler/diferansiyel-geometri/1/izometrinin-teget-donusumu.qmd), key `itd`.

The figures are NOT produced at build time. Run

    python scripts/diffgeo_figures_extra/itd.py
    python scripts/center_figures.py "diffgeo-itd-*.md" --keep-width

and paste the markup from scripts/_figures/diffgeo-itd-<name>.md into the
.qmd file. Figures go INSIDE the box they explain (theorem, proof, example,
solution or exercise), never inside a definition box.

Colours follow the book's frame convention: first frame vector -> PRACTICE,
second -> BASE, third -> THEORY. Captions are Turkish (they are shown on the
site); aria labels are ASCII.
"""
import io
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import *  # noqa: E402,F403 -- Plot, figure, colours, WIDE, cplane, dot, ...
from svg_plot3 import *  # noqa: E402,F403 -- Camera, Space, space_panel, vector helpers

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
OUT = {}

MINUS_S = "&#8722;"
PHI_S, PI_CH, ALPHA_S, BETA_S, PSI_S = "&#966;", "&#960;", "&#945;", "&#946;", "&#968;"
SQRT_S = "&#8730;"


def subs(s, size=9):
    return f'<tspan font-size="{size}" dy="4">{s}</tspan><tspan dy="-4">&#8203;</tspan>'


def ital(s):
    return f'<tspan font-style="italic">{s}</tspan>'


def bold(s):
    return f'<tspan font-weight="700">{s}</tspan>'


def name(letter, k):
    return ital(letter) + subs(str(k))


def tangent(vec, pt):
    """Bold vector part with a bold subscript point: v_p."""
    return bold(vec) + f'<tspan font-size="9" dy="4" font-weight="700">{pt}</tspan><tspan dy="-4">&#8203;</tspan>'


def fstar():
    return ital("F") + subs("*")


def num(x):
    """Turkish number formatting with a real minus sign: -0.5 -> '&#8722;0,5'."""
    s = fmt(x).replace(".", ",")
    return s.replace("-", MINUS_S)


def halo(panel, px, py, s, color=TEXT, size=11.5, anchor="start"):
    """Text on a page-coloured halo, so faint lines break around it."""
    panel.add(f'<text x="{px:.1f}" y="{py:.1f}" fill="{color}" font-size="{size}" '
              f'text-anchor="{anchor}" stroke="{BG}" stroke-width="3.2" stroke-linejoin="round" '
              f'paint-order="stroke">{s}</text>')


def at(S, P, s, dx=0, dy=0, color=TEXT, size=11.5, anchor="start"):
    """Halo text hung on a space point of the Space S."""
    X, Y = S.pt(P)
    halo(S.p, S.p.X(X) + dx, S.p.Y(Y) + dy, s, color, size, anchor)


def at2(p, x, y, s, dx=0, dy=0, color=TEXT, size=11.5, anchor="start"):
    """Halo text hung on a data point of a plane panel."""
    halo(p, p.X(x) + dx, p.Y(y) + dy, s, color, size, anchor)


def fit_space(points, width, camera, margin=0.35, x0=10, y0=10):
    """An equal-aspect panel that just holds the projections of the given space points."""
    xs, ys = [], []
    for P in points:
        X, Y, _ = camera.project(P)
        xs.append(X)
        ys.append(Y)
    P = space_panel(x0, y0, width, (min(xs) - margin, max(xs) + margin), (min(ys) - margin, max(ys) + margin))
    return P, Space(P, camera)


def mat_apply(M, v):
    return tuple(sum(M[i][j] * v[j] for j in range(3)) for i in range(3))


def frame_arrows(S, Q, vecs, width=2.3, head=7.5, cols=(PRACTICE, BASE, THEORY)):
    for vec, col in zip(vecs, cols):
        S.arrow(Q, vadd(Q, vec), col, width, head)


# ============================================================ itd-uc-adim
# itd-uc-adim: the three steps of the tangent map formula in the plane, with the data of the
# planar example: C is the rotation with cos phi = 3/5, sin phi = 4/5, F = T C with translation
# by (5, 0). The tangent vector v_p, v = (2, 1) at p = (-2, 1), is (1) slid to the origin, (2)
# rotated by C to C(v) = (2/5, 11/5), (3) slid to F(p) = (3, -1). Dashed guides show the two
# slides; the arc at the origin shows the rotation angle.
def fig_three_steps():
    c, s = 3 / 5, 4 / 5
    C = lambda v: (c * v[0] - s * v[1], s * v[0] + c * v[1])
    p, v = (-2.0, 1.0), (2.0, 1.0)
    Cv = C(v)
    Fp = (C(p)[0] + 5.0, C(p)[1])
    assert abs(Cv[0] - 0.4) < 1e-12 and abs(Cv[1] - 2.2) < 1e-12
    assert abs(Fp[0] - 3.0) < 1e-12 and abs(Fp[1] + 1.0) < 1e-12
    pl = cplane(30, 18, 440, (-2.9, 4.3), (-1.9, 3.0))
    pl.origin_axes("x", "y", xticks=(-2, -1, 1, 2, 3, 4), yticks=(-1, 1))
    tip_p = (p[0] + v[0], p[1] + v[1])
    tip_F = (Fp[0] + Cv[0], Fp[1] + Cv[1])
    # step 1 guides: from p to O and from the tip of v_p to the tip of v
    pl.line([p, (0, 0)], TEXT, 1.0, "4 3", 0.55)
    pl.line([tip_p, v], TEXT, 1.0, "4 3", 0.55)
    # step 3 guides: from O to F(p) and from the tip of C(v) to the tip of F_*(v_p)
    pl.line([(0, 0), Fp], TEXT, 1.0, "4 3", 0.55)
    pl.line([Cv, tip_F], TEXT, 1.0, "4 3", 0.55)
    # step 2: rotation arc
    a0 = math.atan2(v[1], v[0])
    a1 = math.atan2(Cv[1], Cv[0])
    pl.arc(0, 0, 1.05, a0, a1, BASE, 1.6)
    am = a1 - 0.08
    pl.arrow((1.05 * math.cos(am - 0.05), 1.05 * math.sin(am - 0.05)), (1.05 * math.cos(a1), 1.05 * math.sin(a1)),
             BASE, 1.6, 7)
    pl.arrow(p, tip_p, PRACTICE, 2.4, 8.5)
    pl.arrow((0, 0), v, PRACTICE, 2.0, 8, None, 0.55)
    pl.arrow((0, 0), Cv, THEORY, 2.0, 8, None, 0.55)
    pl.arrow(Fp, tip_F, THEORY, 2.4, 8.5)
    for q in (p, Fp):
        pl.points([q], TEXT, 3.4)
    pl.points([(0, 0)], TEXT, 2.6)
    at2(pl, *p, bold("p"), -8, 14, TEXT, 12, "end")
    at2(pl, *Fp, ital("F") + "(" + bold("p") + ")", 8, 14, TEXT, 12, "start")
    at2(pl, -1.0, 1.5, tangent("v", "p"), -4, -10, PRACTICE, 12, "middle")
    at2(pl, *v, bold("v"), 8, 6, PRACTICE, 12, "start")
    at2(pl, *Cv, ital("C") + "(" + bold("v") + ")", -6, -6, THEORY, 12, "end")
    at2(pl, *tip_F, fstar() + "(" + tangent("v", "p") + ")", 8, 2, THEORY, 12, "start")
    at2(pl, 0.95, 0.95, ital(PHI_S), 4, 4, BASE, 12, "start")
    # step numbers on the guides
    at2(pl, -1.0, 0.5, "1", 4, 16, TEXT, 11, "middle")
    at2(pl, 1.5, -0.5, "3", -2, 18, TEXT, 11, "middle")
    at2(pl, 0.55, 1.05, "2", 0, 0, BASE, 11, "middle")
    return figure(
        500, 380, [pl],
        "Teğet dönüşümünün üç adımı, düzlemdeki örneğin verileriyle: <em>C</em>, cos&#8201;<em>&#966;</em> = 3/5, "
        "sin&#8201;<em>&#966;</em> = 4/5 olan dönme, <em>F</em> ise bu dönmenin ardından (5, 0) ile ötelemedir. "
        "<strong>p</strong> = (&#8722;2, 1) noktasındaki <strong>v</strong><sub><strong>p</strong></sub> "
        "(turuncu) önce başlangıç noktasına kaydırılır ve <strong>v</strong> = (2, 1) noktası olur (1), sonra "
        "<em>C</em> ile döndürülür ve <em>C</em>(<strong>v</strong>) = (0,4; 2,2) olur (2), son olarak "
        "<em>F</em>(<strong>p</strong>) = (3, &#8722;1) noktasına taşınır (3). Mavi ok "
        "<em>F</em><sub>*</sub>(<strong>v</strong><sub><strong>p</strong></sub>)&#8217;dir; okun yönünü "
        "ve uzunluğunu yalnızca <em>C</em> belirler, öteleme yalnızca okun yerini değiştirir.",
        aria="Plane with origin; tangent vector v_p at p = (-2, 1) with v = (2, 1); dashed guides slide it to "
             "the origin; an arc rotates v to C(v) = (0.4, 2.2); dashed guides slide C(v) to F(p) = (3, -1) "
             "where the blue arrow F_*(v_p) starts",
    )


OUT["itd-uc-adim"] = fig_three_steps()


# ============================================================ itd-paralel-oklar
# itd-paralel-oklar: the planar isometry F = T C (C the 3-4-5 rotation, translation by (5, 0))
# acting on the same vector part v = (2, 1) applied at three points p = (-2, 1), q = (1, -1),
# r = (-3, -1) (left panel). In the right panel the images F(p) = (3, -1), F(q) = (32/5, 1/5),
# F(r) = (4, -3) carry three equal arrows C(v) = (2/5, 11/5). Faint grid lines of the left panel and
# their images (a rotated grid) show the rigid motion; both panels use the same scale.
def fig_parallel_arrows():
    c, s = 3 / 5, 4 / 5
    C = lambda v: (c * v[0] - s * v[1], s * v[0] + c * v[1])
    F = lambda q: (C(q)[0] + 5.0, C(q)[1])
    v = (2.0, 1.0)
    pts = [(-2.0, 1.0), (1.0, -1.0), (-3.0, -1.0)]
    names = ["p", "q", "r"]
    imgs = [F(q) for q in pts]
    assert abs(imgs[1][0] - 6.4) < 1e-12 and abs(imgs[1][1] - 0.2) < 1e-12
    assert abs(imgs[2][0] - 4.0) < 1e-12 and abs(imgs[2][1] + 3.0) < 1e-12
    ppu = 40.0
    L = cplane(24, 30, ppu * 6.6, (-3.4, 3.2), (-3.4, 3.0))
    R = cplane(24 + ppu * 6.6 + 40, 30, ppu * 8.2, (-0.4, 7.8), (-3.4, 3.0))
    L.origin_axes("x", "y", xticks=(-2, 1, 2), yticks=(-2, -1, 1))
    R.origin_axes("x", "y", xticks=(2, 3, 4, 5, 6, 7), yticks=(-2, -1, 1, 2))
    # faint grid on the left and its image on the right
    for k in range(-3, 4):
        L.line([(k, -3.4), (k, 3.0)], TEXT, 0.7, None, 0.12)
        L.line([(-3.4, k), (3.2, k)], TEXT, 0.7, None, 0.12)
    for k in range(-3, 4):
        for seg in (((k, -6.0), (k, 6.0)), ((-6.0, k), (6.0, k))):
            a, b = F(seg[0]), F(seg[1])
            # clip the image line to the right panel by sampling
            samples = [(a[0] + (b[0] - a[0]) * t / 400, a[1] + (b[1] - a[1]) * t / 400) for t in range(401)]
            inside = [q for q in samples if -0.4 <= q[0] <= 7.8 and -3.4 <= q[1] <= 3.0]
            if len(inside) > 1:
                R.line([inside[0], inside[-1]], TEXT, 0.7, None, 0.12)
    for q, nm in zip(pts, names):
        L.arrow(q, (q[0] + v[0], q[1] + v[1]), PRACTICE, 2.3, 8)
        L.points([q], TEXT, 3.2)
        at2(L, *q, bold(nm), -6, 14, TEXT, 12, "end")
    Cv = C(v)
    for q, nm, (dx, dy, anc) in zip(imgs, names, ((6, 14, "start"), (-6, -6, "end"), (6, 14, "start"))):
        R.arrow(q, (q[0] + Cv[0], q[1] + Cv[1]), THEORY, 2.3, 8)
        R.points([q], TEXT, 3.2)
        at2(R, *q, ital("F") + "(" + bold(nm) + ")", dx, dy, TEXT, 11.5, anc)
    panel_title(L, "aynı <tspan font-weight=\"700\">v</tspan> = (2, 1), üç noktada")
    panel_title(R, "aynı <tspan font-style=\"italic\">C</tspan>(<tspan font-weight=\"700\">v</tspan>), görüntü noktalarında")
    W = 24 + ppu * 6.6 + 40 + ppu * 8.2 + 20
    H = 30 + ppu * 6.4 + 30
    return figure(
        W, H, [L, R],
        "Düzlemde <em>F</em>(<em>x</em>, <em>y</em>) = ((3<em>x</em> &#8722; 4<em>y</em>)/5 + 5, "
        "(4<em>x</em> + 3<em>y</em>)/5) izometrisi. Solda aynı <strong>v</strong> = (2, 1) vektör kısmı "
        "<strong>p</strong> = (&#8722;2, 1), <strong>q</strong> = (1, &#8722;1) ve <strong>r</strong> = (&#8722;3, &#8722;1) "
        "noktalarına uygulanmıştır. Sağda <em>F</em><sub>*</sub> altındaki görüntüleri: üç ok da aynı "
        "<em>C</em>(<strong>v</strong>) = (0,4; 2,2) vektör kısmına sahiptir ve <em>F</em>(<strong>p</strong>) = (3, &#8722;1), "
        "<em>F</em>(<strong>q</strong>) = (6,4; 0,2), <em>F</em>(<strong>r</strong>) = (4, &#8722;3) noktalarında uygulanır. "
        "Paralel oklar paralel oklara gider. Soldaki silik ızgara, sağda bütünüyle dönmüş ve kaymış bir ızgaraya dönüşür; "
        "iki panelin ölçeği aynıdır.",
        css_class=WIDE,
        aria="Two planes at the same scale. Left: the vector (2, 1) drawn at the points (-2, 1), (1, -1), (-3, -1) "
             "over a faint grid. Right: the image points (3, -1), (6.4, 0.2), (4, -3) each carrying the same arrow "
             "(0.4, 2.2) over the rotated and shifted grid",
    )


OUT["itd-paralel-oklar"] = fig_parallel_arrows()


# ============================================================ itd-helis
# itd-helis: the helix alpha(t) = (cos t, sin t, t), t in [0, 2 pi], and its image under
# F(x, y, z) = (x, z + 2, 1 - y) (rotation by -90 degrees about the x axis, then translation by
# (0, 2, 1)): beta(t) = (cos t, t + 2, 1 - sin t), a helix about the line x = 0, z = 1. At
# t = pi/2 the velocity alpha'(pi/2) = (-1, 0, 1) at (0, 1, pi/2) goes to beta'(pi/2) = (-1, 1, 0)
# at (0, 2 + pi/2, 0); both have length sqrt 2.
def fig_helix():
    C = ((1, 0, 0), (0, 0, 1), (0, -1, 0))
    a = (0.0, 2.0, 1.0)
    F = lambda q: vadd(mat_apply(C, q), a)
    alpha = lambda t: (math.cos(t), math.sin(t), t)
    beta = lambda t: F(alpha(t))
    t0 = math.pi / 2
    A0, V0 = alpha(t0), (-math.sin(t0), math.cos(t0), 1.0)
    B0, W0 = beta(t0), mat_apply(C, V0)
    assert vnorm(vsub(W0, (-1.0, 1.0, 0.0))) < 1e-12
    assert vnorm(vsub(B0, (0.0, 2.0 + math.pi / 2, 0.0))) < 1e-12
    cam = Camera(azimuth=16.0, elevation=24.0)
    pts = [alpha(2 * math.pi * k / 60) for k in range(61)] + [beta(2 * math.pi * k / 60) for k in range(61)]
    pts += [(0, 0, -0.4), (0, 0, 7.2), (0, 9.4, 0), (1.9, 0, 0), vadd(A0, V0), vadd(B0, W0)]
    P, S = fit_space(pts, 460, cam, 0.45)
    S.axes(1.9, 9.2, 7.1, 0, -1.3, -0.4)
    # axis of the image helix
    S.guide([(0, 1.6, 1.0), (0, 8.9, 1.0)], TEXT, 0.45)
    S.curve(alpha, 0, 2 * math.pi, TEXT, 1.6, 240, None, 0.85)
    S.curve(beta, 0, 2 * math.pi, TEXT, 1.6, 240, "5 3", 0.85)
    S.arrow(A0, vadd(A0, V0), PRACTICE, 2.4, 8)
    S.arrow(B0, vadd(B0, W0), THEORY, 2.4, 8)
    S.point(A0, TEXT, 3.2)
    S.point(B0, TEXT, 3.2)
    at(S, alpha(0.0), ital(ALPHA_S), 8, 4, TEXT, 13)
    at(S, beta(2 * math.pi), ital(BETA_S) + " = " + ital("F") + "(" + ital(ALPHA_S) + ")", 8, 14, TEXT, 12)
    at(S, A0, ital(ALPHA_S) + "(" + PI_CH + "/2)", 8, 12, TEXT, 11)
    at(S, vadd(A0, V0), ital(ALPHA_S) + "&#8242;(" + PI_CH + "/2)", -6, -4, PRACTICE, 11.5, "end")
    at(S, B0, ital(BETA_S) + "(" + PI_CH + "/2)", 6, 15, TEXT, 11)
    at(S, vadd(B0, W0), fstar() + "(" + ital(ALPHA_S) + "&#8242;(" + PI_CH + "/2))", -4, -8, THEORY, 11.5, "middle")
    at(S, (0, 8.9, 1.0), ital("x") + " = 0, " + ital("z") + " = 1", -2, -8, TEXT, 10.5, "end")
    return figure(
        round(P.x0 + P.w + 10), round(P.y0 + P.h + 10), [P],
        "<em>&#945;</em>(<em>t</em>) = (cos <em>t</em>, sin <em>t</em>, <em>t</em>) helisinin bir turu (düz) ve "
        "<em>F</em>(<em>x</em>, <em>y</em>, <em>z</em>) = (<em>x</em>, <em>z</em> + 2, 1 &#8722; <em>y</em>) izometrisi "
        "altındaki görüntüsü <em>&#946;</em>(<em>t</em>) = (cos <em>t</em>, <em>t</em> + 2, 1 &#8722; sin <em>t</em>) (kesikli). "
        "<em>&#946;</em>, <em>x</em> = 0, <em>z</em> = 1 doğrusu (silik kesikli) etrafında dolanan bir helistir. "
        "<em>t</em> = &#960;/2 anında <em>&#945;</em>&#8242;(&#960;/2) = (&#8722;1, 0, 1) (turuncu), "
        "<em>F</em><sub>*</sub> ile (&#8722;1, 1, 0) okuna (mavi) gider; bu, <em>&#946;</em>&#8242;(&#960;/2)&#8217;dir. "
        "İki okun uzunluğu da &#8730;2&#8217;dir: izometri süratleri korur.",
        aria="The helix (cos t, sin t, t) around the z axis, one turn, and its image (cos t, t + 2, 1 - sin t), a "
             "dashed helix around the line x = 0, z = 1 parallel to the y axis; at t = pi/2 the velocity "
             "(-1, 0, 1) and its image (-1, 1, 0)",
    )


OUT["itd-helis"] = fig_helix()


# ============================================================ itd-konform
# itd-konform: F(u, v) = (e^u cos v, e^u sin v) at p = (ln 2, pi/2). Left: the (u, v) plane with the
# arrows x = (1, 0) and y = (1, 1) at p (45 degrees apart) and a small square [ln 2, ln 2 + 0.4] x
# [pi/2, pi/2 + 0.4]. Right: F(p) = (0, 2) with the image arrows (0, 2) and (-2, 2) (lengths 2 and
# 2 sqrt 2, still 45 degrees apart) and the image of the square, a piece of an annular sector.
# Both panels use the same scale, so the doubling of lengths is visible.
def fig_conformal():
    u0, v0 = math.log(2.0), math.pi / 2
    Fm = lambda u, v: (math.exp(u) * math.cos(v), math.exp(u) * math.sin(v))
    J = ((0.0, -2.0), (2.0, 0.0))
    x, y = (1.0, 0.0), (1.0, 1.0)
    Jx = (J[0][0] * x[0] + J[0][1] * x[1], J[1][0] * x[0] + J[1][1] * x[1])
    Jy = (J[0][0] * y[0] + J[0][1] * y[1], J[1][0] * y[0] + J[1][1] * y[1])
    assert Jx == (0.0, 2.0) and Jy == (-2.0, 2.0)
    assert abs(Fm(u0, v0)[0]) < 1e-12 and abs(Fm(u0, v0)[1] - 2.0) < 1e-12
    ppu = 58.0
    L = cplane(26, 30, ppu * 2.7, (-0.2, 2.5), (-0.3, 4.5))
    R = cplane(26 + ppu * 2.7 + 50, 30, ppu * 4.0, (-3.0, 1.0), (-0.3, 4.5))
    L.origin_axes("u", "v", xticks=(1, 2), yticks=(1, 2, 3, 4))
    R.origin_axes("x", "y", xticks=(-2, -1), yticks=(1, 2, 4))
    h = 0.4
    sq = [(u0, v0), (u0 + h, v0), (u0 + h, v0 + h), (u0, v0 + h)]
    L.polygon(sq, TEXT, 0.10, TEXT, 1.0)
    # image of the square boundary
    bd = []
    for k in range(21):
        bd.append(Fm(u0 + h * k / 20, v0))
    for k in range(21):
        bd.append(Fm(u0 + h, v0 + h * k / 20))
    for k in range(21):
        bd.append(Fm(u0 + h - h * k / 20, v0 + h))
    for k in range(21):
        bd.append(Fm(u0, v0 + h - h * k / 20))
    R.polygon(bd, TEXT, 0.10, TEXT, 1.0)
    p = (u0, v0)
    L.arc(u0, v0, 0.45, 0.0, math.pi / 4, BASE, 1.4)
    L.arrow(p, (u0 + x[0], v0 + x[1]), PRACTICE, 2.3, 8)
    L.arrow(p, (u0 + y[0], v0 + y[1]), THEORY, 2.3, 8)
    L.points([p], TEXT, 3.2)
    Fp = (0.0, 2.0)
    R.arc(0.0, 2.0, 0.6, math.pi / 2, 3 * math.pi / 4, BASE, 1.4)
    R.arrow(Fp, (Jx[0], 2.0 + Jx[1]), PRACTICE, 2.3, 8)
    R.arrow(Fp, (Jy[0], 2.0 + Jy[1]), THEORY, 2.3, 8)
    R.points([Fp], TEXT, 3.2)
    at2(L, *p, bold("p"), -6, 14, TEXT, 12, "end")
    at2(L, u0 + 1.0, v0, bold("x") + ", uzunluk 1", -6, 16, PRACTICE, 11, "middle")
    at2(L, u0 + 1.0, v0 + 1.0, bold("y") + ", " + SQRT_S + "2", 6, 2, THEORY, 11, "start")
    at2(L, u0 + 0.5, v0 + 0.2, "45&#176;", 4, 0, BASE, 10.5, "start")
    at2(R, *Fp, ital("F") + "(" + bold("p") + ")", 8, 14, TEXT, 12, "start")
    at2(R, 0.0, 4.0, "uzunluk 2", 8, 4, PRACTICE, 11, "start")
    at2(R, -2.0, 4.0, "2" + SQRT_S + "2", -6, 4, THEORY, 11, "end")
    at2(R, -0.36, 2.88, "45&#176;", 0, 4, BASE, 10, "middle")
    W = 26 + ppu * 2.7 + 50 + ppu * 4.0 + 24
    H = 30 + ppu * 4.8 + 30
    return figure(
        W, H, [L, R],
        "<em>F</em>(<em>u</em>, <em>v</em>) = (<em>e</em><sup><em>u</em></sup> cos <em>v</em>, "
        "<em>e</em><sup><em>u</em></sup> sin <em>v</em>) dönüşümü <strong>p</strong> = (ln 2, &#960;/2) noktasında. "
        "Solda <strong>p</strong>&#8217;deki <strong>x</strong> = (1, 0) ve <strong>y</strong> = (1, 1) okları "
        "ile kenarı 0,4 olan küçük bir kare; sağda <em>F</em>(<strong>p</strong>) = (0, 2) noktasındaki görüntü "
        "okları (0, 2) ve (&#8722;2, 2) ile karenin görüntüsü. İki panelin ölçeği aynıdır. Oklar 90&#176; döner ve "
        "uzunlukları iki katına çıkar, ama aralarındaki 45&#176;&#8217;lik açı korunur: <em>F</em> açıları korur "
        "ama iç çarpımı korumaz.",
        aria="Left: the uv plane with two arrows (1, 0) and (1, 1) at p = (ln 2, pi/2), 45 degrees apart, and a "
             "small square. Right: at F(p) = (0, 2) the image arrows (0, 2) and (-2, 2), twice as long and still "
             "45 degrees apart, and the curved image of the square",
    )


OUT["itd-konform"] = fig_conformal()


# ============================================================ itd-yansima
# itd-yansima: reflection F(x, y, z) = (z + 2, y, x - 2) in the plane x - z = 2. The frame
# e1 = (1, 1, 0)/sqrt 2, e2 = (-1, 1, 0)/sqrt 2, e3 = (0, 0, 1) at p = (1, 0, 1) goes to the frame
# (0, 1, 1)/sqrt 2, (0, 1, -1)/sqrt 2, (1, 0, 0) at F(p) = (3, 0, -1). The dashed segment from p to
# F(p) is perpendicular to the mirror and meets it at its midpoint (2, 0, 0).
def fig_mirror():
    C = ((0, 0, 1), (0, 1, 0), (1, 0, 0))
    a = (2.0, 0.0, -2.0)
    F = lambda q: vadd(mat_apply(C, q), a)
    r2 = 1 / math.sqrt(2)
    e = [(r2, r2, 0.0), (-r2, r2, 0.0), (0.0, 0.0, 1.0)]
    p = (1.0, 0.0, 1.0)
    Fp = F(p)
    fe = [mat_apply(C, v) for v in e]
    assert vnorm(vsub(Fp, (3.0, 0.0, -1.0))) < 1e-12
    assert vnorm(vsub(vcross(fe[0], fe[1]), vscale(-1.0, fe[2]))) < 1e-12
    mid = (2.0, 0.0, 0.0)
    s1 = (r2, 0.0, r2)      # in the mirror
    s2 = (0.0, 1.0, 0.0)    # in the mirror
    cam = Camera(azimuth=15.0, elevation=12.0)
    corners = [vadd(mid, vadd(vscale(a1, s1), vscale(b1, s2))) for a1 in (-1.5, 1.5) for b1 in (-1.9, 1.9)]
    L = 0.8  # drawn length of the frame arrows
    e_d = [vscale(L, v) for v in e]
    fe_d = [vscale(L, v) for v in fe]
    pts = corners + [p, Fp] + [vadd(p, v) for v in e_d] + [vadd(Fp, v) for v in fe_d]
    P, S = fit_space(pts, 520, cam, 0.4)
    S.parallelogram(mid, s1, s2, (-1.5, 1.5), (-1.9, 1.9), THEORY, 0.10, THEORY, 0.9)
    S.guide([p, Fp], TEXT, 0.6)
    S.point(mid, TEXT, 2.4)
    frame_arrows(S, p, e_d)
    frame_arrows(S, Fp, fe_d)
    S.point(p, TEXT, 3.2)
    S.point(Fp, TEXT, 3.2)
    at(S, p, bold("p"), -6, 14, TEXT, 11.5, "end")
    at(S, Fp, ital("F") + "(" + bold("p") + ")", -10, -6, TEXT, 11.5, "end")
    at(S, vadd(p, e_d[0]), name("e", 1), -6, 4, PRACTICE, 11.5, "end")
    at(S, vadd(p, e_d[1]), name("e", 2), 6, 4, BASE, 11.5)
    at(S, vadd(p, e_d[2]), name("e", 3), 6, -2, THEORY, 11.5)
    at(S, vadd(Fp, fe_d[0]), fstar() + "(" + name("e", 1) + ")", 6, -2, PRACTICE, 11.5)
    at(S, vadd(Fp, fe_d[1]), fstar() + "(" + name("e", 2) + ")", 6, 12, BASE, 11.5)
    at(S, vadd(Fp, fe_d[2]), fstar() + "(" + name("e", 3) + ")", -6, 14, THEORY, 11.5, "end")
    at(S, vadd(mid, vadd(vscale(-1.5, s1), vscale(1.9, s2))), ital("x") + " " + MINUS_S + " " + ital("z") + " = 2",
       -4, -6, THEORY, 11, "end")
    return figure(
        round(P.x0 + P.w + 10), round(P.y0 + P.h + 10), [P],
        "<em>x</em> &#8722; <em>z</em> = 2 aynasındaki <em>F</em>(<em>x</em>, <em>y</em>, <em>z</em>) = (<em>z</em> + 2, "
        "<em>y</em>, <em>x</em> &#8722; 2) yansıması. <strong>p</strong> = (1, 0, 1)&#8217;deki "
        "<em>e</em><sub>1</sub>, <em>e</em><sub>2</sub>, <em>e</em><sub>3</sub> çatısı (turuncu, yeşil, mavi), "
        "<em>F</em>(<strong>p</strong>) = (3, 0, &#8722;1)&#8217;deki (0, 1, 1)/&#8730;2, (0, 1, &#8722;1)/&#8730;2, "
        "(1, 0, 0) çatısına gider. Kesikli doğru parçası aynaya diktir ve aynayı orta noktası (2, 0, 0)&#8217;da keser. "
        "Görüntü yine bir çatıdır, ama <em>e</em><sub>1</sub> &#215; <em>e</em><sub>2</sub> = <em>e</em><sub>3</sub> iken "
        "görüntüde birinci iki okun vektörel çarpımı üçüncünün tersidir.",
        aria="A tilted mirror plane x - z = 2; at p = (1, 0, 1) a frame of three arrows, at the mirror image "
             "F(p) = (3, 0, -1) the image frame; a dashed segment from p to F(p) crosses the mirror at (2, 0, 0)",
    )


OUT["itd-yansima"] = fig_mirror()


# ============================================================ itd-iki-cati
# itd-iki-cati: the two frames of the exercise: e1 = (2, 2, 1)/3, e2 = (-2, 1, 2)/3, e3 = (1, -2, 2)/3
# at p = (0, 1, 0) and f1 = (1, 0, 1)/sqrt 2, f2 = (0, 1, 0), f3 = (1, 0, -1)/sqrt 2 at q = (3, -1, 1).
# The orthogonal part C = B^T A carries the e frame to a frame at C(p) = (0, 1/3, 2 sqrt 2/3) that is
# parallel to the f frame (faint); the translation by a = q - C(p) slides it to q. A short helix
# attached to the e frame (its axis along e3) is carried along; its image turns the other way
# because det C = -1.
def fig_two_frames():
    A = ((2 / 3, 2 / 3, 1 / 3), (-2 / 3, 1 / 3, 2 / 3), (1 / 3, -2 / 3, 2 / 3))
    r2 = 1 / math.sqrt(2)
    B = ((r2, 0.0, r2), (0.0, 1.0, 0.0), (r2, 0.0, -r2))
    Cm = tuple(tuple(sum(B[k][i] * A[k][j] for k in range(3)) for j in range(3)) for i in range(3))
    p, q = (0.0, 1.0, 0.0), (3.0, -1.0, 1.0)
    Cp = mat_apply(Cm, p)
    a = vsub(q, Cp)
    F = lambda x: vadd(mat_apply(Cm, x), a)
    for i in range(3):
        assert vnorm(vsub(mat_apply(Cm, A[i]), B[i])) < 1e-12
    assert vnorm(vsub(F(p), q)) < 1e-12
    assert abs(Cp[1] - 1 / 3) < 1e-12 and abs(Cp[2] - 2 * math.sqrt(2) / 3) < 1e-12

    def body(s):
        h = (0.24 * math.cos(s), 0.24 * math.sin(s), 0.06 * s)
        return vadd(p, vadd(vadd(vscale(h[0], A[0]), vscale(h[1], A[1])), vscale(h[2], A[2])))

    cam = Camera(azimuth=20.0, elevation=24.0)
    pts = [p, q, Cp, (0, 0, 0)] + [vadd(p, v) for v in A] + [vadd(q, v) for v in B] + [vadd(Cp, v) for v in B]
    pts += [(3.3, 0, 0), (0, 2.2, 0), (0, 0, 2.2), (0, -1.6, 0)]
    P, S = fit_space(pts, 490, cam, 0.45)
    S.axes(3.3, 2.2, 2.2, 0, -1.6, 0)
    # the intermediate frame C(e_i) at C(p), faint
    for vec, col in zip(B, (PRACTICE, BASE, THEORY)):
        S.arrow(Cp, vadd(Cp, vec), col, 1.6, 6.5, "3 2", 0.55)
    S.curve(lambda s: mat_apply(Cm, body(s)), 0, 4 * math.pi, TEXT, 1.1, 200, None, 0.45)
    S.arrow(Cp, q, TEXT, 1.3, 7.5, "5 3", 0.7)
    S.curve(body, 0, 4 * math.pi, TEXT, 1.6, 200)
    S.curve(lambda s: F(body(s)), 0, 4 * math.pi, TEXT, 1.6, 200)
    frame_arrows(S, p, A)
    frame_arrows(S, q, B)
    for X in (p, q):
        S.point(X, TEXT, 3.2)
    S.point(Cp, TEXT, 2.6)
    at(S, p, bold("p"), 8, 14, TEXT, 12)
    at(S, q, bold("q"), -8, 14, TEXT, 12, "end")
    at(S, Cp, ital("C") + "(" + bold("p") + ")", -8, -2, TEXT, 11, "end")
    at(S, vadd(Cp, vscale(0.5, a)), bold("a") + " = " + bold("q") + " " + MINUS_S + " " + ital("C") + "(" + bold("p") + ")",
       0, 16, TEXT, 11, "middle")
    for i, (col, dx, dy, anc) in enumerate(((PRACTICE, 6, 4, "start"), (BASE, 6, 4, "start"), (THEORY, -6, -2, "end"))):
        at(S, vadd(p, A[i]), name("e", i + 1), dx, dy, col, 11.5, anc)
    for i, (col, dx, dy, anc) in enumerate(((PRACTICE, -6, -2, "end"), (BASE, 6, 4, "start"), (THEORY, -6, 12, "end"))):
        at(S, vadd(q, B[i]), name("f", i + 1), dx, dy, col, 11.5, anc)
    return figure(
        round(P.x0 + P.w + 10), round(P.y0 + P.h + 10), [P],
        "İki çatıyı eşleyen izometrinin iki adımı, alıştırmadaki çatılarla. <strong>p</strong> = (0, 1, 0)&#8217;daki "
        "<em>e</em><sub>1</sub>, <em>e</em><sub>2</sub>, <em>e</em><sub>3</sub> çatısını önce ortogonal kısım "
        "<em>C</em> = <em>B</em><sup>T</sup><em>A</em> döndürür; <em>C</em>(<strong>p</strong>) = (0, 1/3, 2&#8730;2/3) "
        "noktasındaki silik kesikli çatı, <strong>q</strong> = (3, &#8722;1, 1)&#8217;deki <em>f</em><sub>1</sub>, "
        "<em>f</em><sub>2</sub>, <em>f</em><sub>3</sub> çatısına paraleldir. Sonra öteleme onu <strong>a</strong> = "
        "<strong>q</strong> &#8722; <em>C</em>(<strong>p</strong>) kadar kaydırır. <em>e</em> çatısına iliştirilmiş "
        "kısa helis parçası da birlikte taşınır ve görüntüde hedef çatıya aynı biçimde iliştirilmiş çıkar; bu "
        "izometri bir yansıma içerdiğinden görüntü helis ters yönde döner.",
        aria="Coordinate axes; at p = (0, 1, 0) a frame e1, e2, e3 with a short helix attached along e3; at "
             "C(p) a faint dashed copy of the target frame; a dashed arrow a from C(p) to q = (3, -1, 1); at q the "
             "frame f1, f2, f3 with the image of the short helix",
    )


OUT["itd-iki-cati"] = fig_two_frames()


# ============================================================ itd-duzlemler
# itd-duzlemler: the plane P: y = -1 through p = (1/2, -1, 0) with normal (0, 1, 0), and its image
# under F = T C, C with columns (1, 0, 1)/sqrt 2, (1, 0, -1)/sqrt 2, (0, 1, 0), F(p) = (1, -2, 1):
# the plane x - z = 0 with normal (1, 0, -1)/sqrt 2 = C(u2). A triangle p, p + u1, p + u3 in P and
# its image triangle F(p), F(p) + C(u1), F(p) + C(u3) show how the plane is laid down.
def fig_planes():
    r2 = 1 / math.sqrt(2)
    c1, c2, c3 = (r2, 0.0, r2), (r2, 0.0, -r2), (0.0, 1.0, 0.0)
    Cm = tuple(tuple(col[i] for col in (c1, c2, c3)) for i in range(3))
    p = (0.5, -1.0, 0.0)
    Fp = (1.0, -2.0, 1.0)
    a = vsub(Fp, mat_apply(Cm, p))
    F = lambda x: vadd(mat_apply(Cm, x), a)
    assert vnorm(vsub(F(p), Fp)) < 1e-12
    for x_, z_ in ((0.0, 0.0), (1.3, -0.7), (-2.0, 1.5)):
        im = F((x_, -1.0, z_))
        assert abs(im[0] - im[2]) < 1e-12
    cam = Camera(azimuth=38.0, elevation=22.0)
    u1, u3 = (1.0, 0.0, 0.0), (0.0, 0.0, 1.0)
    # patch of P around p, and patch of the image plane around F(p) kept at y < -1.1
    Pc = [vadd(p, (dx, 0.0, dz)) for dx in (-1.1, 1.1) for dz in (-1.1, 1.1)]
    Qc = [vadd(Fp, vadd(vscale(s, c1), vscale(w, c3))) for s in (-1.4, 1.4) for w in (-1.0, 0.4)]
    pts = Pc + Qc + [vadd(p, (0, 1.1, 0)), vadd(Fp, vscale(1.1, c2))]
    P, S = fit_space(pts, 500, cam, 0.45)
    S.parallelogram(Fp, c1, c3, (-1.4, 1.4), (-1.0, 0.4), BASE, 0.10, BASE, 0.9)
    S.polygon([Fp, vadd(Fp, c1), vadd(Fp, c3)], BASE, 0.22, BASE, 1.1)
    S.arrow(Fp, vadd(Fp, vscale(1.1, c2)), BASE, 2.3, 8)
    S.guide([p, Fp], TEXT, 0.5)
    S.parallelogram(p, u1, u3, (-1.1, 1.1), (-1.1, 1.1), THEORY, 0.10, THEORY, 0.9)
    S.polygon([p, vadd(p, u1), vadd(p, u3)], THEORY, 0.22, THEORY, 1.1)
    S.arrow(p, vadd(p, (0, 1.1, 0)), THEORY, 2.3, 8)
    S.point(p, TEXT, 3.2)
    S.point(Fp, TEXT, 3.2)
    at(S, p, bold("p"), -8, 14, TEXT, 11.5, "end")
    at(S, Fp, ital("F") + "(" + bold("p") + ")", -8, 14, TEXT, 11.5, "end")
    at(S, vadd(p, (0, 1.1, 0)), "(0, 1, 0)", -6, -14, THEORY, 11, "middle")
    at(S, vadd(Fp, vscale(1.1, c2)), ital("C") + "(" + bold("u") + subs("2") + ")", 6, 4, BASE, 11)
    at(S, Pc[2], ital("P") + ": " + ital("y") + " = " + MINUS_S + "1", 6, 14, THEORY, 11)
    at(S, Qc[0], ital("F") + "(" + ital("P") + "): " + ital("x") + " = " + ital("z"), -6, 4, BASE, 11, "end")
    return figure(
        round(P.x0 + P.w + 10), round(P.y0 + P.h + 10), [P],
        "<em>P</em>: <em>y</em> = &#8722;1 düzlemi (mavi) ve <em>F</em> altındaki görüntüsü <em>x</em> &#8722; <em>z</em> = 0 "
        "düzlemi (yeşil). <strong>p</strong> = (1/2, &#8722;1, 0) noktası (1, &#8722;2, 1)&#8217;e gider; <em>P</em>&#8217;nin "
        "normali (0, 1, 0), ortogonal kısım altında görüntü düzlemin normali <em>C</em>(<strong>u</strong><sub>2</sub>) = "
        "(1, 0, &#8722;1)/&#8730;2 olur. <em>P</em> içindeki <strong>p</strong>, <strong>p</strong> + <strong>u</strong><sub>1</sub>, "
        "<strong>p</strong> + <strong>u</strong><sub>3</sub> üçgeni, görüntü düzlemde kenarları <em>C</em>(<strong>u</strong><sub>1</sub>) = "
        "(1, 0, 1)/&#8730;2 ve <em>C</em>(<strong>u</strong><sub>3</sub>) = (0, 1, 0) olan eş bir üçgene gider.",
        aria="Two plane patches: P, the plane y = -1 with normal (0, 1, 0) at p = (1/2, -1, 0) and a small triangle; "
             "its image, the plane x = z with normal (1, 0, -1)/sqrt 2 at (1, -2, 1) and the image triangle",
    )


OUT["itd-duzlemler"] = fig_planes()


# ---------------------------------------------------------------------------
for key, content in OUT.items():
    with io.open(OUT_DIR / f"diffgeo-{key}.md", "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
print("generated:", len(OUT), "figures")
