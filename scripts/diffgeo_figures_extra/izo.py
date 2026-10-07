# -*- coding: utf-8 -*-
"""
Figures of the chapter "Öklid Uzayının İzometrileri"
(dersler/diferansiyel-geometri/1/izometriler.qmd), key `izo`.

The figures are NOT produced at build time. Run

    python scripts/diffgeo_figures_extra/izo.py
    python scripts/center_figures.py "diffgeo-izo-*.md" --keep-width

and paste the markup from scripts/_figures/diffgeo-izo-<name>.md into the
.qmd file. Figures go INSIDE the box they explain (theorem, proof, example,
solution or exercise), never inside a definition box.

Colours: original objects in TEXT (grey), intermediate stages dashed,
final images in THEORY; translations and velocities in PRACTICE. The images
of the unit points u1, u2, u3 follow the book's frame convention
(PRACTICE, BASE, THEORY). Captions are Turkish; aria labels are ASCII.
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
TH_S, PHI_S, PI_CH, ALPHA_S, BETA_S, GAMMA_S, TAU_S, KAPPA_S, PI_S2 = (
    "&#977;", "&#966;", "&#960;", "&#945;", "&#946;", "&#947;", "&#964;", "&#954;", "&#928;")


def subs(s, size=9):
    return f'<tspan font-size="{size}" dy="4">{s}</tspan><tspan dy="-4">&#8203;</tspan>'


def ital(s):
    return f'<tspan font-style="italic">{s}</tspan>'


def bold(s):
    return f'<tspan font-weight="700">{s}</tspan>'


def name(letter, k):
    return ital(letter) + subs(str(k))


def bname(letter, k):
    return bold(letter) + subs(str(k))


def halo(panel, px, py, s, color=TEXT, size=11.5, anchor="start"):
    """Text on a page-coloured halo, so faint lines break around it."""
    panel.add(f'<text x="{px:.1f}" y="{py:.1f}" fill="{color}" font-size="{size}" '
              f'text-anchor="{anchor}" stroke="{BG}" stroke-width="3.2" stroke-linejoin="round" '
              f'paint-order="stroke">{s}</text>')


def at(S, Q, s, dx=0, dy=0, color=TEXT, size=11.5, anchor="start"):
    X, Y = S.pt(Q)
    halo(S.p, S.p.X(X) + dx, S.p.Y(Y) + dy, s, color, size, anchor)


def pat(pl, P, s, dx=0, dy=0, color=TEXT, size=11.5, anchor="start"):
    halo(pl, pl.X(P[0]) + dx, pl.Y(P[1]) + dy, s, color, size, anchor)


def rot2(p, t):
    c, s = math.cos(t), math.sin(t)
    return (c * p[0] - s * p[1], s * p[0] + c * p[1])


def plane_axes(pl, xr, yr, xlabel="x", ylabel="y"):
    pl.arrow((xr[0], 0.0), (xr[1], 0.0), TEXT, 1.1, 7, None, 0.55)
    pl.arrow((0.0, yr[0]), (0.0, yr[1]), TEXT, 1.1, 7, None, 0.55)
    pl.label(xr[1], 0.0, ital(xlabel), 0, 16, TEXT, 11.5, "middle")
    pl.label(0.0, yr[1], ital(ylabel), 9, 4, TEXT, 11.5, "start")


# ============================================================ izo-duzlem-donmesi
# izo-duzlem-donmesi: the rotation of the plane through the angle theta about the origin. The point p
# at distance r and polar angle phi goes to q at the same distance and polar angle phi + theta (the
# derivation of the rotation formula in exm-izo-duzlem-donmesi). Generic angles, no numbers.
def fig_plane_rotation():
    r, phi, th = 2.8, math.radians(20), math.radians(48)
    p = (r * math.cos(phi), r * math.sin(phi))
    q = (r * math.cos(phi + th), r * math.sin(phi + th))
    pl = cplane(24, 16, 450, (-0.7, 3.6), (-0.6, 3.4))
    plane_axes(pl, (-0.5, 3.4), (-0.4, 3.2))
    pl.line(circle_pts(0.0, 0.0, r, math.radians(-4), math.radians(94)), TEXT, 1.0, "4 3", 0.45)
    pl.line([(0.0, 0.0), p], TEXT, 1.6, None, 0.8)
    pl.line([(0.0, 0.0), q], THEORY, 1.6)
    angle_arc(pl, 0.0, phi, 0.75, TEXT, 1.2, False)
    angle_arc(pl, phi, phi + th, 1.35, PRACTICE, 1.6, True)
    # the travelled arc of the circle, from p to q
    pl.line(circle_pts(0.0, 0.0, r, phi, phi + th), PRACTICE, 2.2, None, 0.55)
    dot(pl, (0.0, 0.0), TEXT, 3.0)
    dot(pl, p, TEXT, 3.8)
    dot(pl, q, THEORY, 3.8)
    pat(pl, p, bold("p") + " = (" + name("p", 1) + ", " + name("p", 2) + ")", -4, 22, TEXT, 12, "end")
    pat(pl, q, bold("q") + " = (" + name("q", 1) + ", " + name("q", 2) + ")", 9, -6, THEORY, 12, "start")
    pm = (0.62 * p[0], 0.62 * p[1])
    pat(pl, pm, ital("r"), -2, -7, TEXT, 12, "middle")
    pat(pl, (0.95 * math.cos(phi / 2), 0.95 * math.sin(phi / 2)), ital(PHI_S), 2, 5, TEXT, 12, "start")
    mid = phi + th / 2
    pat(pl, (1.55 * math.cos(mid), 1.55 * math.sin(mid)), ital(TH_S), 4, 2, PRACTICE, 12.5, "start")
    pat(pl, (0.0, 0.0), "0", -6, 15, TEXT, 11, "end")
    return figure(
        500, 460, [pl],
        "Düzlemin başlangıç noktası çevresinde <em>&#977;</em> açısıyla dönmesi. <strong>p</strong> noktası "
        "başlangıç noktasına uzaklığı <em>r</em> aynı kalarak, <em>x</em> ekseniyle yaptığı <em>&#966;</em> "
        "açısı <em>&#966;</em> + <em>&#977;</em> olacak biçimde <strong>q</strong> noktasına gider; turuncu yay "
        "noktanın çember üzerinde aldığı yoldur.",
        aria="Rotation of the plane about the origin: the point p at distance r and polar angle phi moves "
             "along the dashed circle of radius r to the point q at polar angle phi plus theta",
    )


OUT["izo-duzlem-donmesi"] = fig_plane_rotation()


# ============================================================ izo-oteleme
# izo-oteleme: translation by a in R^3. A triangle p, q, r and its translate p + a, q + a, r + a;
# the three dashed arrows from the vertices to their images are parallel to and as long as the arrow
# a drawn from the origin.
def fig_translation():
    pl = space_panel(16, 16, 460, (-4.4, 4.8), (-2.6, 4.2))
    S = Space(pl, Camera(azimuth=32.0, elevation=20.0))
    S.floor_grid((-1, 4), (-2, 4), n=5, opacity=0.07)
    S.axes(4.8, 5.0, 3.6, offsets=((-4, 14), (10, 4), (-10, -4)))
    a = (-0.4, 2.6, 1.4)
    tri = [(3.6, -1.6, 0.0), (3.8, 0.2, 0.2), (2.2, -1.0, 1.5)]
    img = [vadd(P, a) for P in tri]
    S.polygon(tri, TEXT, 0.12, TEXT, 1.4)
    S.polygon(img, THEORY, 0.16, THEORY, 1.8)
    for P, Q in zip(tri, img):
        S.arrow(P, Q, PRACTICE, 1.6, 8, "5 3", 0.9)
    O = (0.0, 0.0, 0.0)
    S.arrow(O, a, PRACTICE, 2.6, 9)
    for P in tri:
        S.point(P, TEXT, 3.2)
    for P in img:
        S.point(P, THEORY, 3.2)
    at(S, a, bold("a"), -9, -3, PRACTICE, 12.5, "end")
    names = ("p", "q", "r")
    offs = ((6, 15, "start"), (8, 6, "start"), (-8, -2, "end"))
    for nm, P, (dx, dy, anc) in zip(names, tri, offs):
        at(S, P, bold(nm), dx, dy, TEXT, 12, anc)
    offs2 = ((8, 13, "start"), (9, 5, "start"), (-8, -4, "end"))
    for nm, P, (dx, dy, anc) in zip(names, img, offs2):
        at(S, P, bold(nm) + " + " + bold("a"), dx, dy, THEORY, 12, anc)
    return figure(
        470, 360, [pl],
        "<strong>a</strong> ile öteleme. Köşeleri <strong>p</strong>, <strong>q</strong>, <strong>r</strong> "
        "olan üçgenin her köşesi aynı <strong>a</strong> okunu (turuncu, kesikli) izleyerek kayar ve "
        "<strong>p</strong> + <strong>a</strong>, <strong>q</strong> + <strong>a</strong>, "
        "<strong>r</strong> + <strong>a</strong> köşeli üçgene (mavi) gider. Kenar farkları, örneğin "
        "(<strong>q</strong> + <strong>a</strong>) &#8722; (<strong>p</strong> + <strong>a</strong>) = "
        "<strong>q</strong> &#8722; <strong>p</strong>, hiç değişmez; bu yüzden kenar uzunlukları da değişmez.",
        aria="Translation by a in space: a triangle with vertices p, q, r and its translate with vertices "
             "p + a, q + a, r + a; dashed arrows from the vertices to their images are parallel to the "
             "arrow a drawn from the origin",
    )


OUT["izo-oteleme"] = fig_translation()


# ============================================================ izo-yansima
# izo-yansima: reflection in the plane Pi: x + 2y + 2z = 0 with unit normal n = (1, 2, 2)/3
# (exm-izo-duzleme-gore-yansima). p = (3, 0, 3) goes to R(p) = (1, -4, -1); the midpoint (2, -2, 1)
# lies on Pi and the segment p R(p) is parallel to n.
def fig_reflection():
    n = (1 / 3, 2 / 3, 2 / 3)
    p = (3.0, 0.0, 3.0)
    Rp = vsub(p, vscale(2 * vdot(p, n), n))
    m = vscale(0.5, vadd(p, Rp))
    assert vnorm(vsub(Rp, (1.0, -4.0, -1.0))) < 1e-12 and vnorm(vsub(m, (2.0, -2.0, 1.0))) < 1e-12
    assert abs(vdot(m, n)) < 1e-12
    w1 = vunit((2.0, -1.0, 0.0))
    w2 = vcross(n, w1)
    assert abs(vnorm(w2) - 1) < 1e-12 and abs(vdot(w2, n)) < 1e-12
    pl = space_panel(16, 16, 475, (-4.6, 4.4), (-3.8, 4.4))
    S = Space(pl, Camera(azimuth=-12.0, elevation=24.0))
    S.axes(4.2, 3.4, 4.0, xmin=-1.0, ymin=-4.6, zmin=-1.6, offsets=((-6, 14), (10, 4), (-10, -4)))
    c = (1.0, -1.0, 0.5)
    # the part of the segment behind the plane first, then the plane, then the rest
    S.guide([Rp, m], TEXT, 0.55, 1.3)
    S.parallelogram(c, w1, w2, (-3.0, 2.6), (-2.1, 2.1), THEORY, 0.14, THEORY, 1.0)
    S.guide([m, p], TEXT, 0.8, 1.3)
    O = (0.0, 0.0, 0.0)
    S.arrow(O, vscale(1.6, n), PRACTICE, 2.4, 9)
    # right-angle mark at m between the segment (direction n) and the plane (direction w1)
    s = 0.32
    a1 = vadd(m, vscale(s, n))
    a2 = vadd(a1, vscale(s, w1))
    a3 = vadd(m, vscale(s, w1))
    S.line([a1, a2, a3], TEXT, 1.0, None, 0.7)
    S.point(O, TEXT, 3.0)
    S.point(m, TEXT, 3.2)
    S.point(p, TEXT, 3.8)
    S.point(Rp, THEORY, 3.8)
    at(S, p, bold("p") + " = (3, 0, 3)", 8, -4, TEXT, 12, "start")
    at(S, Rp, ital("R") + "(" + bold("p") + ") = (1, " + MINUS_S + "4, " + MINUS_S + "1)", 10, 16, THEORY, 12, "start")
    at(S, m, "(2, " + MINUS_S + "2, 1)", -10, -8, TEXT, 11.5, "end")
    at(S, vscale(1.6, n), bold("n"), 8, 2, PRACTICE, 12.5, "start")
    at(S, vadd(c, vadd(vscale(-2.7, w1), vscale(-1.8, w2))), ital(PI_S2), 6, -6, THEORY, 12.5, "start")
    return figure(
        510, 480, [pl],
        "Birim normali <strong>n</strong> = (1, 2, 2)/3 olan <em>&#928;</em>: <em>x</em> + 2<em>y</em> + "
        "2<em>z</em> = 0 düzlemine göre yansıma. <strong>p</strong> = (3, 0, 3) noktası düzlemin öbür yanındaki "
        "<em>R</em>(<strong>p</strong>) = (1, &#8722;4, &#8722;1) noktasına gider. İki noktayı birleştiren "
        "kesikli doğru parçası <strong>n</strong>&#8217;ye paraleldir ve düzlemi orta noktası (2, &#8722;2, 1)"
        "&#8217;de dik keser.",
        aria="Reflection in the plane x + 2y + 2z = 0 with unit normal n = (1, 2, 2)/3: the point p = (3, 0, 3) "
             "and its mirror image R(p) = (1, -4, -1); the dashed segment joining them is parallel to n and "
             "meets the plane at right angles at its midpoint (2, -2, 1)",
    )


OUT["izo-yansima"] = fig_reflection()


# ============================================================ izo-ayristirma
# izo-ayristirma: two panels in the xy plane, C = rotation about the z axis by pi/2, a = (3, 1, 0).
# Left, F = TC: the triangle (1, 0), (3, 0), (1, 1) turns about the origin (dashed) and then moves
# by a; the origin goes to a. Right, CT: the triangle first moves by a (dashed) and then turns about
# the origin; the origin goes to C(a) = (-1, 3). The two final triangles differ.
def fig_decomposition():
    tri = [(1.0, 0.0), (3.0, 0.0), (1.0, 1.0)]
    a = (3.0, 1.0)
    rot = math.pi / 2

    def tr(P, v):
        return (P[0] + v[0], P[1] + v[1])

    def draw(pl, stages, origin_img, origin_lbl):
        plane_axes(pl, (pl_x[pl][0], pl_x[pl][1]), (pl_y[pl][0], pl_y[pl][1]))
        S0, S1, S2 = stages
        pl.polygon(S0, TEXT, 0.12, TEXT, 1.3)
        pl.polygon(S1, TEXT, 0.0, TEXT, 1.2, "4 3")
        pl.polygon(S2, THEORY, 0.18, THEORY, 1.8)
        for S_, col in ((S0, TEXT), (S1, TEXT), (S2, THEORY)):
            dot(pl, S_[0], col, 3.4)
        dot(pl, (0.0, 0.0), TEXT, 3.0)
        dot(pl, origin_img, PRACTICE, 3.6)
        pat(pl, origin_img, origin_lbl, 8, -6, PRACTICE, 11.5, "start")

    pl_x, pl_y = {}, {}
    # left panel: rotate first, then translate
    L = cplane(24, 34, 270, (-1.8, 4.6), (-0.9, 4.9))
    pl_x[L], pl_y[L] = (-1.6, 4.4), (-0.7, 4.7)
    S1 = [rot2(P, rot) for P in tri]
    S2 = [tr(P, a) for P in S1]
    draw(L, (tri, S1, S2), a, ital("F") + "(0) = " + bold("a"))
    angle_arc(L, 0.12, rot - 0.12, 1.0, TEXT, 1.4, True)
    pat(L, (0.36, 0.56), ital("C"), 0, 4, TEXT, 12, "middle")
    L.arrow((0.0, 0.0), a, PRACTICE, 2.0, 8)
    for P, Q in zip(S1, S2):
        L.arrow(P, Q, PRACTICE, 1.2, 7, "4 3", 0.75)
    pat(L, (1.5, 3.5), ital("T"), 0, -9, PRACTICE, 12, "middle")
    panel_title(L, ital("F") + " = " + ital("TC") + ": önce " + ital("C") + ", sonra " + ital("T"))

    # right panel: translate first, then rotate
    R = cplane(330, 34, 270, (-2.8, 6.6), (-0.9, 6.9))
    pl_x[R], pl_y[R] = (-2.6, 6.4), (-0.7, 6.7)
    T1 = [tr(P, a) for P in tri]
    T2 = [rot2(P, rot) for P in T1]
    Ca = rot2(a, rot)
    draw(R, (tri, T1, T2), Ca, ital("C") + "(" + bold("a") + ")")
    R.arrow((0.0, 0.0), a, PRACTICE, 2.0, 8)
    R.arrow((0.0, 0.0), Ca, PRACTICE, 1.4, 7, "4 3", 0.8)
    angle_arc(R, math.atan2(1, 3) + 0.08, math.atan2(1, 3) + rot - 0.08, 3.16, TEXT, 1.2, True)
    pat(R, a, bold("a"), 8, 4, PRACTICE, 12, "start")
    panel_title(R, ital("CT") + ": önce " + ital("T") + ", sonra " + ital("C"))

    return figure(
        630, 330, [L, R],
        "<em>z</em> ekseni çevresinde dik açılık dönme <em>C</em> ile (3, 1, 0) ile öteleme <em>T</em>, "
        "<em>xy</em> düzleminde. Gri üçgen başlangıç, kesikli üçgen ara adım, mavi üçgen sonuçtur. Solda "
        "<em>F</em> = <em>TC</em>: üçgen önce orijin çevresinde döner, sonra <strong>a</strong> kadar kayar; "
        "orijin <strong>a</strong>&#8217;ya gider. Sağda <em>CT</em>: üçgen önce kayar, sonra orijin çevresinde "
        "döner; orijin <em>C</em>(<strong>a</strong>) = (&#8722;1, 3)&#8217;e gider. İki sonuç farklıdır.",
        css_class=WIDE,
        aria="Two panels in the xy plane with C the quarter turn about the origin and T the translation by "
             "a = (3, 1). Left: F = TC, a triangle is first rotated about the origin, then translated by a; the "
             "origin goes to a. Right: CT, the triangle is first translated, then rotated; the origin goes to "
             "C(a) = (-1, 3). The two final triangles are different",
    )


OUT["izo-ayristirma"] = fig_decomposition()


# ============================================================ izo-eksen-donmesi
# izo-eksen-donmesi: the rotation through 2 pi/3 about the diagonal e = (1, 1, 1)/sqrt 3
# (exm-izo-kosegen-eksen). The unit points lie in the plane x + y + z = 1 on the circle of centre
# (1, 1, 1)/3 and radius sqrt(6)/3; the rotation carries u1 -> u2 -> u3 -> u1 along that circle.
def fig_axis_rotation():
    e = vunit((1.0, 1.0, 1.0))
    c = (1 / 3, 1 / 3, 1 / 3)
    u = [(1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)]
    f1 = vunit(vsub(u[0], c))
    f2 = vcross(e, f1)
    rad = vnorm(vsub(u[0], c))
    assert abs(rad - math.sqrt(6) / 3) < 1e-12

    def circ(t):
        return vadd(c, vadd(vscale(rad * math.cos(t), f1), vscale(rad * math.sin(t), f2)))

    # u2 sits at angle 2 pi/3 and u3 at 4 pi/3 on this parametrisation (right-hand turn about e)
    assert vnorm(vsub(circ(2 * math.pi / 3), u[1])) < 1e-12
    assert vnorm(vsub(circ(4 * math.pi / 3), u[2])) < 1e-12

    pl = space_panel(16, 16, 505, (-1.25, 1.35), (-0.75, 1.75))
    S = Space(pl, Camera(azimuth=35.0, elevation=24.0))
    S.axes(1.45, 1.45, 1.45, offsets=((-4, 14), (10, 4), (-10, -4)))
    O3 = (0.0, 0.0, 0.0)
    S.line([vscale(-0.35, e), O3], TEXT, 1.2, "5 3", 0.6)
    S.polygon(u, THEORY, 0.10, THEORY, 0.9, "3 3")
    S.curve(circ, 0.0, 2 * math.pi, TEXT, 1.0, 160, "3 3", 0.6)
    cols = (PRACTICE, BASE, THEORY)
    for k in range(3):
        t0 = 2 * math.pi * k / 3
        S.segment_arrow(circ, t0 + 0.14, t0 + 2 * math.pi / 3 - 0.2, cols[(k + 1) % 3], 2.2, 8.5, 80)
    S.line([vscale(0.0, e), vscale(1.75, e)], TEXT, 1.4, "5 3", 0.75)
    S.arrow((0.0, 0.0, 0.0), vscale(0.62, e), TEXT, 2.0, 8)
    S.point(c, TEXT, 2.8)
    for k in range(3):
        S.point(u[k], cols[k], 3.8)
    S.point(O3, TEXT, 2.8)
    at(S, u[0], bname("u", 1), -8, 14, PRACTICE, 12, "end")
    at(S, u[1], bname("u", 2), 6, 15, BASE, 12, "start")
    at(S, u[2], bname("u", 3), -10, -6, THEORY, 12, "end")
    at(S, vscale(1.75, e), "(1, 1, 1)", 6, -4, TEXT, 11.5, "start")
    at(S, vscale(0.62, e), bold("e"), -8, -2, TEXT, 12, "end")
    at(S, circ(math.pi / 3), "2" + PI_CH + "/3", 2, 16, BASE, 11.5, "start")
    return figure(
        540, 520, [pl],
        "Köşegen <strong>e</strong> = (1, 1, 1)/&#8730;3 çevresinde 2&#960;/3 açısıyla dönme. Birim noktalar "
        "<strong>u</strong><sub>1</sub>, <strong>u</strong><sub>2</sub>, <strong>u</strong><sub>3</sub>, eksene dik "
        "<em>x</em> + <em>y</em> + <em>z</em> = 1 düzlemindeki eşkenar üçgenin köşeleridir; üçgenin merkezi "
        "(1, 1, 1)/3 eksen üzerindedir. Dönme her köşeyi kesikli çember üzerinde üçte bir tur ilerletir: "
        "<strong>u</strong><sub>1</sub> &#8594; <strong>u</strong><sub>2</sub> &#8594; <strong>u</strong><sub>3</sub> "
        "&#8594; <strong>u</strong><sub>1</sub>.",
        aria="Rotation through 2 pi over 3 about the diagonal axis through the origin and (1, 1, 1): the unit "
             "points u1, u2, u3 are the vertices of an equilateral triangle in the plane x + y + z = 1 centred "
             "on the axis, and arrows along the circle through them show u1 to u2, u2 to u3, u3 to u1",
    )


OUT["izo-eksen-donmesi"] = fig_axis_rotation()


# ============================================================ izo-sabit-nokta
# izo-sabit-nokta: top view (xy plane) of F = T_a C with C the quarter turn about the z axis and
# a = (2, 0, 0) (exm-izo-sabit-noktalar). The square (2, 1), (3, 1), (3, 2), (2, 2) turns about the
# origin to (-1, 2), (-1, 3), (-2, 3), (-2, 2) (dashed) and then moves by (2, 0) to (1, 2), (1, 3),
# (0, 3), (0, 2): the quarter turn of the first square about c = (1, 1), the trace of the fixed line.
def fig_fixed_point():
    sq = [(2.0, 1.0), (3.0, 1.0), (3.0, 2.0), (2.0, 2.0)]
    mid = [rot2(P, math.pi / 2) for P in sq]
    img = [(P[0] + 2.0, P[1]) for P in mid]
    assert [tuple(round(v, 9) for v in P) for P in mid] == [(-1, 2), (-1, 3), (-2, 3), (-2, 2)]
    assert [tuple(round(v, 9) for v in P) for P in img] == [(1, 2), (1, 3), (0, 3), (0, 2)]
    c = (1.0, 1.0)
    for P, Q in zip(sq, img):
        assert abs(math.hypot(P[0] - c[0], P[1] - c[1]) - math.hypot(Q[0] - c[0], Q[1] - c[1])) < 1e-12
    pl = cplane(20, 16, 450, (-2.8, 3.8), (-0.8, 3.7))
    plane_axes(pl, (-2.6, 3.6), (-0.6, 3.5))
    for k in range(1, 4):
        pl.line([(k, -0.06), (k, 0.06)], TEXT, 1.0, None, 0.6)
        pl.label(k, 0.0, str(k), 0, 15, TEXT, 10.5, "middle")
        pl.line([(-0.06, k), (0.06, k)], TEXT, 1.0, None, 0.6)
    pl.label(0.0, 1.0, "1", -8, 4, TEXT, 10.5, "end")
    pl.polygon(sq, TEXT, 0.12, TEXT, 1.3)
    pl.polygon(mid, TEXT, 0.0, TEXT, 1.2, "4 3")
    pl.polygon(img, THEORY, 0.18, THEORY, 1.8)
    # the translation by (2, 0) of each corner of the intermediate square
    for P, Q in zip(mid, img):
        pl.arrow(P, Q, PRACTICE, 1.2, 7, "4 3", 0.8)
    # the quarter turn about c, seen on the corner (2, 1) -> (1, 2)
    pl.line([c, sq[0]], TEXT, 1.0, "3 3", 0.7)
    pl.line([c, img[0]], TEXT, 1.0, "3 3", 0.7)
    arc = [(c[0] + 0.62 * math.cos(t), c[1] + 0.62 * math.sin(t))
           for t in [0.3 + (math.pi / 2 - 0.6) * k / 40 for k in range(41)]]
    pl.line(arc[:-2], PRACTICE, 1.6)
    pl.arrow(arc[-3], arc[-1], PRACTICE, 1.6, 7.0)
    dot(pl, c, PRACTICE, 4.2)
    dot(pl, sq[0], TEXT, 3.2)
    dot(pl, img[0], THEORY, 3.2)
    pat(pl, c, bold("c") + " = (1, 1)", -8, -8, PRACTICE, 12, "end")
    pat(pl, sq[0], "(2, 1)", 6, 15, TEXT, 11, "start")
    pat(pl, img[0], "(1, 2)", 8, 14, THEORY, 11, "start")
    pat(pl, (-1.5, 2.5), ital("C"), 0, 4, TEXT, 12, "middle")
    pat(pl, (0.5, 3.0), "+ (2, 0)", 0, -10, PRACTICE, 11, "middle")
    return figure(
        490, 350, [pl],
        "<em>F</em> = <em>T</em><sub><strong>a</strong></sub><em>C</em>, <strong>a</strong> = (2, 0, 0), "
        "yukarıdan bakış. Gri kare <em>C</em> ile orijin çevresinde çeyrek tur döner (kesikli kare), sonra "
        "(2, 0) kadar kayar (turuncu oklar) ve mavi kareye gelir. Sonuç, gri karenin <strong>c</strong> = (1, 1) "
        "çevresinde çeyrek tur döndürülmüş hâlidir: örneğin (2, 1) köşesi (1, 2)&#8217;ye gider. "
        "<em>F</em>, <strong>c</strong>&#8217;den geçen dikey doğru çevresinde bir dönmedir.",
        aria="Top view of F = T_a C with C the quarter turn about the z axis and a = (2, 0, 0): a grey square "
             "with corners (2, 1), (3, 1), (3, 2), (2, 2) is rotated about the origin to a dashed square and "
             "translated by (2, 0) to a blue square with corners (1, 2), (1, 3), (0, 3), (0, 2), which is the "
             "grey square turned a quarter about the point c = (1, 1)",
    )


OUT["izo-sabit-nokta"] = fig_fixed_point()


# ============================================================ izo-helis-donme
# izo-helis-donme: the helix alpha(t) = (2 cos t, 2 sin t, t) and its image beta(t) =
# (2 cos t, -t - 3, 2 sin t + 3) under F = T_a C, C the quarter turn about the x axis, a = (0, -3, 3)
# (exm-izo-helis-goruntusu); 0 <= t <= 2 pi. The axis of beta (x = 0, z = 3) dashed; velocities at t = 0.
def fig_helix_rotation():
    def alpha(t):
        return (2 * math.cos(t), 2 * math.sin(t), t)

    def C(p):
        return (p[0], -p[2], p[1])

    def beta(t):
        return vadd((0.0, -3.0, 3.0), C(alpha(t)))

    for t in (0.0, 1.0, 2.5):
        assert vnorm(vsub(beta(t), (2 * math.cos(t), -t - 3, 2 * math.sin(t) + 3))) < 1e-12
    pl = space_panel(16, 16, 520, (-9.5, 4.5), (-2.4, 7.6))
    S = Space(pl, Camera(azimuth=12.0, elevation=18.0))
    S.axes(3.4, 3.0, 7.4, ymin=-10.6, offsets=((-4, 14), (10, 4), (-10, -4)))
    S.line([(0.0, -2.2, 3.0), (0.0, -10.2, 3.0)], THEORY, 1.2, "6 4", 0.6)
    S.curve(alpha, 0.0, 2 * math.pi, TEXT, 2.0, 240, None, 0.8)
    S.curve(beta, 0.0, 2 * math.pi, THEORY, 2.3, 240)
    S.segment_arrow(alpha, 4.6, 5.1, TEXT, 2.0, 8.5, 30)
    S.segment_arrow(beta, 4.6, 5.1, THEORY, 2.3, 8.5, 30)
    a0, b0 = alpha(0.0), beta(0.0)
    S.arrow(a0, vadd(a0, (0.0, 2.0, 1.0)), PRACTICE, 2.2, 8)
    S.arrow(b0, vadd(b0, C((0.0, 2.0, 1.0))), PRACTICE, 2.2, 8)
    S.point(a0, TEXT, 3.4)
    S.point(b0, THEORY, 3.4)
    at(S, alpha(2 * math.pi), ital(ALPHA_S), 8, 4, TEXT, 12.5, "start")
    at(S, beta(2 * math.pi), ital(BETA_S) + " = " + ital("F") + "(" + ital(ALPHA_S) + ")", 0, 22, THEORY, 12,
       "middle")
    at(S, a0, ital(ALPHA_S) + "(0)", -9, -4, TEXT, 11, "end")
    at(S, b0, ital(BETA_S) + "(0)", -9, 4, THEORY, 11, "end")
    return figure(
        560, 360, [pl],
        "<em>&#945;</em>(<em>t</em>) = (2 cos <em>t</em>, 2 sin <em>t</em>, <em>t</em>) helisi (gri) ve onun "
        "<em>F</em> = <em>T</em><sub><strong>a</strong></sub><em>C</em> altındaki görüntüsü "
        "<em>&#946;</em>(<em>t</em>) = (2 cos <em>t</em>, &#8722;<em>t</em> &#8722; 3, 2 sin <em>t</em> + 3) "
        "(mavi), 0 &#8804; <em>t</em> &#8804; 2&#960;. <em>C</em>, <em>x</em> ekseni çevresinde dik açılık dönme, "
        "<strong>a</strong> = (0, &#8722;3, 3)&#8217;tür. <em>&#946;</em>&#8217;nın ekseni <em>x</em> = 0, "
        "<em>z</em> = 3 doğrusudur (kesikli); küçük oklar hareket yönünü gösterir. Turuncu oklar <em>t</em> = 0 "
        "anındaki hızlardır; ikisinin de uzunluğu &#8730;5&#8217;tir.",
        aria="The helix alpha(t) = (2 cos t, 2 sin t, t) around the z axis and its image beta(t) = "
             "(2 cos t, -t - 3, 2 sin t + 3) around the dashed line x = 0, z = 3, for t from 0 to 2 pi, with the "
             "velocity arrows at t = 0",
    )


OUT["izo-helis-donme"] = fig_helix_rotation()


# ============================================================ izo-helis-ayna
# izo-helis-ayna: the helix alpha(t) = (2 cos t, 2 sin t, t), 0 <= t <= 6 pi/5, above the mirror
# plane z = 0 and its mirror image gamma(t) = (2 cos t, 2 sin t, -t) below it
# (exm-izo-aynadaki-helis). Arrows show the direction of travel: alpha climbs while turning
# counterclockwise (seen from above), gamma descends while turning the same way.
def fig_helix_mirror():
    def alpha(t):
        return (2 * math.cos(t), 2 * math.sin(t), t)

    def gamma(t):
        return (2 * math.cos(t), 2 * math.sin(t), -t)

    t1 = 1.2 * math.pi
    pl = space_panel(16, 16, 440, (-4.4, 4.6), (-4.6, 4.6))
    S = Space(pl, Camera(azimuth=35.0, elevation=14.0))
    S.line([(0.0, 0.0, -4.4), (0.0, 0.0, 4.4)], TEXT, 1.1, "5 3", 0.5)
    S.curve(gamma, 0.0, t1, PRACTICE, 2.2, 200)
    S.parallelogram((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (-2.9, 2.9), (-2.9, 2.9),
                    TEXT, 0.10, TEXT, 0.9)
    S.curve(alpha, 0.0, t1, THEORY, 2.2, 200)
    S.segment_arrow(alpha, 2.2, 2.7, THEORY, 2.2, 8.5, 30)
    S.segment_arrow(gamma, 2.2, 2.7, PRACTICE, 2.2, 8.5, 30)
    # a pair of mirror points
    t = 1.0
    S.guide([alpha(t), gamma(t)], TEXT, 0.6, 1.0)
    S.point(alpha(t), THEORY, 3.2)
    S.point(gamma(t), PRACTICE, 3.2)
    S.point((2 * math.cos(t), 2 * math.sin(t), 0.0), TEXT, 2.4)
    at(S, alpha(t1), ital(ALPHA_S) + ",  " + ital(TAU_S) + " = 1/5", -8, -4, THEORY, 12, "end")
    at(S, gamma(t1), ital(GAMMA_S) + " = " + ital("M") + "(" + ital(ALPHA_S) + "),  " + ital(TAU_S)
       + " = " + MINUS_S + "1/5", -8, 14, PRACTICE, 12, "end")
    at(S, (2.9, -2.9, 0.0), ital("z") + " = 0", -6, 16, TEXT, 11.5, "end")
    return figure(
        470, 420, [pl],
        "<em>&#945;</em>(<em>t</em>) = (2 cos <em>t</em>, 2 sin <em>t</em>, <em>t</em>) helisi (mavi) ve "
        "<em>xy</em> düzlemindeki aynadaki görüntüsü <em>&#947;</em>(<em>t</em>) = (2 cos <em>t</em>, 2 sin "
        "<em>t</em>, &#8722;<em>t</em>) (turuncu), 0 &#8804; <em>t</em> &#8804; 6&#960;/5. Kesikli doğru bir "
        "nokta çiftini birleştirir ve aynaya diktir. Oklar hareket yönünü gösterir: iki eğri yukarıdan bakınca "
        "aynı yönde döner, ama <em>&#945;</em> dönerken yükselir, <em>&#947;</em> alçalır. Eğrilikleri aynıdır "
        "(2/5), burulmaları zıt işaretlidir.",
        aria="The helix alpha(t) = (2 cos t, 2 sin t, t) above the mirror plane z = 0 and its mirror image "
             "gamma(t) = (2 cos t, 2 sin t, -t) below it, with arrows showing the direction of travel and a "
             "dashed segment joining a pair of mirror points perpendicular to the plane",
    )


OUT["izo-helis-ayna"] = fig_helix_mirror()


# ---------------------------------------------------------------------------
for key, content in OUT.items():
    with io.open(OUT_DIR / f"diffgeo-{key}.md", "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
print("generated:", len(OUT), "figures")
