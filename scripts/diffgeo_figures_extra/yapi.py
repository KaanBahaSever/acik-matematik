# -*- coding: utf-8 -*-
"""
Figures of the chapter "Cartan Yapı Denklemleri"
(dersler/diferansiyel-geometri/1/yapi-denklemleri.qmd), key `yapi`.

The figures are NOT produced at build time. Run

    python scripts/diffgeo_figures_extra/yapi.py
    python scripts/center_figures.py "diffgeo-yapi-*.md" --keep-width

and paste the markup from scripts/_figures/diffgeo-yapi-<name>.md into the
.qmd file. Figures go INSIDE the box they explain (theorem, proof, example,
solution or exercise), never inside a definition box.

Colours follow the book's frame convention (cati-silindirik-cati,
cati-kuresel-cati): first frame field -> PRACTICE, second -> BASE,
third -> THEORY. Captions are Turkish (they are shown on the site); aria
labels are ASCII.
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
TH_S, PHI_S, RHO_S, PSI_S, THETA_S = "&#977;", "&#966;", "&#961;", "&#968;", "&#952;"


def subs(s, size=9):
    return f'<tspan font-size="{size}" dy="4">{s}</tspan><tspan dy="-4">&#8203;</tspan>'


def ital(s):
    return f'<tspan font-style="italic">{s}</tspan>'


def bold(s):
    return f'<tspan font-weight="700">{s}</tspan>'


def name(letter, k):
    return ital(letter) + subs(str(k))


def halo(panel, px, py, s, color=TEXT, size=11.5, anchor="start"):
    """Text on a page-coloured halo, so faint lines break around it."""
    panel.add(f'<text x="{px:.1f}" y="{py:.1f}" fill="{color}" font-size="{size}" '
              f'text-anchor="{anchor}" stroke="{BG}" stroke-width="3.2" stroke-linejoin="round" '
              f'paint-order="stroke">{s}</text>')


def right_angle(panel, foot, u, w, size=0.14, color=TEXT, opacity=0.6):
    """Small square at `foot` between the unit directions u and w (2-D data coordinates)."""
    a = (foot[0] + size * u[0], foot[1] + size * u[1])
    b = (a[0] + size * w[0], a[1] + size * w[1])
    c = (foot[0] + size * w[0], foot[1] + size * w[1])
    panel.line([a, b, c], color, 1.0, None, opacity)


# ============================================================ yapi-dual-izdusum
# yapi-dual-izdusum: top view of the plane z = 2 through p = (3, 4, 2). The cylindrical frame at p
# has E1 = (3/5, 4/5, 0) and E2 = (-4/5, 3/5, 0); the tangent vector v = (1, 2, 5) has horizontal
# part (1, 2). theta_i(v) = v . E_i(p) is the signed length of the orthogonal projection of v on
# the line through p in direction E_i: 11/5 along E1 and 2/5 along E2 (both asserted below).
# theta_3(v) = 5 is the vertical component and does not show in a top view; the caption says so.
def fig_dual_projection():
    P0 = (3.0, 4.0)
    E1 = (0.6, 0.8)
    E2 = (-0.8, 0.6)
    V = (1.0, 2.0)
    t1 = V[0] * E1[0] + V[1] * E1[1]
    t2 = V[0] * E2[0] + V[1] * E2[1]
    assert abs(t1 - 11 / 5) < 1e-12 and abs(t2 - 2 / 5) < 1e-12
    tip = (P0[0] + V[0], P0[1] + V[1])
    f1 = (P0[0] + t1 * E1[0], P0[1] + t1 * E1[1])
    f2 = (P0[0] + t2 * E2[0], P0[1] + t2 * E2[1])

    pl = cplane(30, 16, 370, (-0.7, 6.4), (-0.7, 7.0))

    # axes of the horizontal plane
    pl.arrow((0.0, 0.0), (6.1, 0.0), TEXT, 1.1, 7, None, 0.55)
    pl.arrow((0.0, 0.0), (0.0, 6.7), TEXT, 1.1, 7, None, 0.55)
    pl.label(6.1, 0.0, "x", 0, 17, TEXT, 11.5, "middle", False, True)
    pl.label(0.0, 6.7, "y", 9, 3, TEXT, 11.5, "start", False, True)

    # the circle r = 5 and the radius to p
    pl.line(circle_pts(0.0, 0.0, 5.0, math.radians(8), math.radians(88)), TEXT, 1.0, "4 3", 0.45)
    pl.line([(0.0, 0.0), P0], TEXT, 1.2, None, 0.5)
    pl.label(1.5, 2.0, ital("r") + " = 5", -8, -2, TEXT, 11.5, "end")

    # the two frame lines through p
    pl.line([(P0[0] - 0.9 * E1[0], P0[1] - 0.9 * E1[1]), (P0[0] + 3.0 * E1[0], P0[1] + 3.0 * E1[1])],
            PRACTICE, 1.0, "2 3", 0.6)
    pl.line([(P0[0] - 1.2 * E2[0], P0[1] - 1.2 * E2[1]), (P0[0] + 2.2 * E2[0], P0[1] + 2.2 * E2[1])],
            BASE, 1.0, "2 3", 0.6)

    # projections: thick translucent bands, dashed perpendiculars, right-angle marks
    pl.line([P0, f1], PRACTICE, 6.0, None, 0.28)
    pl.line([P0, f2], BASE, 6.0, None, 0.35)
    pl.line([tip, f1], TEXT, 1.0, "4 3", 0.6)
    pl.line([tip, f2], TEXT, 1.0, "4 3", 0.6)
    right_angle(pl, f1, (-E1[0], -E1[1]), (-E2[0], -E2[1]))
    right_angle(pl, f2, (-E2[0], -E2[1]), E1)

    # the vectors
    pl.arrow(P0, (P0[0] + E1[0], P0[1] + E1[1]), PRACTICE, 2.4, 9)
    pl.arrow(P0, (P0[0] + E2[0], P0[1] + E2[1]), BASE, 2.4, 9)
    pl.arrow(P0, tip, TEXT, 2.0, 9)
    dot(pl, P0, TEXT, 3.6)
    dot(pl, f1, PRACTICE, 3.0)
    dot(pl, f2, BASE, 3.0)

    pl.label(P0[0], P0[1], bold("p"), 6, 17, TEXT, 12, "start")
    pl.label(tip[0], tip[1], bold("v"), -8, -4, TEXT, 12, "end")
    pl.label(P0[0] + E1[0], P0[1] + E1[1], name("E", 1), 9, 6, PRACTICE, 11.5, "start")
    pl.label(P0[0] + E2[0], P0[1] + E2[1], name("E", 2), -10, 12, BASE, 11.5, "end")
    halo(pl, pl.X(f1[0]) + 9, pl.Y(f1[1]) + 12,
         name(THETA_S, 1) + "(" + bold("v") + ") = 11/5", PRACTICE, 11.5, "start")
    halo(pl, pl.X(f2[0]) - 12, pl.Y(f2[1]) + 16,
         name(THETA_S, 2) + "(" + bold("v") + ") = 2/5", BASE, 11.5, "end")

    return figure(
        430, 450, [pl],
        "<strong>p</strong> = (3, 4, 2) noktasından geçen yatay düzlem, yukarıdan. Silindirik çatının "
        "<em>E</em><sub>1</sub>(<strong>p</strong>) (turuncu) ve <em>E</em><sub>2</sub>(<strong>p</strong>) "
        "(yeşil) okları ile <strong>v</strong> = (1, 2, 5) vektörünün yatay kısmı (1, 2) çizilmiştir. "
        "<strong>v</strong>&#8217;nin <em>E</em><sub>1</sub> doğrultusundaki dik izdüşümünün uzunluğu "
        "<em>&#952;</em><sub>1</sub>(<strong>v</strong>) = 11/5, <em>E</em><sub>2</sub> doğrultusundakinin "
        "uzunluğu <em>&#952;</em><sub>2</sub>(<strong>v</strong>) = 2/5&#8217;tir. Üçüncü dual form "
        "<strong>v</strong>&#8217;nin düşey bileşenini okur: <em>&#952;</em><sub>3</sub>(<strong>v</strong>) = 5; "
        "bu bileşen yukarıdan bakışta görünmez.",
        aria="Top view of the horizontal plane through p = (3, 4, 2): the cylindrical frame arrows "
             "E1 = (3/5, 4/5) and E2 = (-4/5, 3/5) at p, the horizontal part (1, 2) of v, and the "
             "orthogonal projections of v on the two frame lines, of lengths 11/5 and 2/5",
    )


OUT["yapi-dual-izdusum"] = fig_dual_projection()


# ============================================================ yapi-kuresel-kutu
# yapi-kuresel-kutu: the small spherical-coordinate box at p (rho, theta, phi) = (4, 0.25, 0.5),
# with exaggerated increments. Its three edges from p run along F1 (rho grows), F2 (theta grows)
# and F3 (phi grows) and have lengths d rho, rho cos(phi) d theta, rho d phi: exactly the dual forms.
# The horizontal radius from the z axis to p (length rho cos phi) is drawn, since it is the radius
# of the parallel circle on which the theta edge is an arc -- that is where cos phi comes from.
def sph(rho, th, ph):
    return (rho * math.cos(ph) * math.cos(th), rho * math.cos(ph) * math.sin(th), rho * math.sin(ph))


def fig_spherical_box():
    R0, T0, F0 = 4.0, 0.25, 0.5
    DR, DT, DF = 1.1, 0.32, 0.28
    pl = space_panel(20, 16, 430, (-3.2, 4.4), (-1.9, 4.4))
    S = Space(pl, Camera(azimuth=62.0, elevation=16.0, scale=1.0))

    def at(Q, s, dx=0, dy=0, color=TEXT, size=11.5, anchor="start"):
        X, Y = S.pt(Q)
        halo(pl, pl.X(X) + dx, pl.Y(Y) + dy, s, color, size, anchor)

    S.floor_grid((0, 4), (0, 3), n=4, opacity=0.08)
    S.axes(5.6, 4.3, 4.4, offsets=((-4, 14), (10, 4), (-10, -4)))

    p = sph(R0, T0, F0)
    zp = p[2]
    foot = (p[0], p[1], 0.0)
    # radius rho, horizontal radius rho cos phi, drop to the floor
    S.line([(0.0, 0.0, 0.0), p], TEXT, 1.1, None, 0.55)
    S.guide([p, foot], TEXT, 0.45, 1.0)
    S.guide([(0.0, 0.0, 0.0), foot], TEXT, 0.6, 1.1)
    # the parallel circle and the meridian through p (thin)
    S.curve(lambda t: sph(R0, t, F0), -0.35, 1.2, TEXT, 0.9, 96, None, 0.4)
    S.curve(lambda t: sph(R0, T0, t), 0.0, 1.25, TEXT, 0.9, 96, None, 0.4)
    # the angle phi at the origin
    S.curve(lambda t: sph(1.1, T0, t), 0.0, F0, TEXT, 1.1, 40, None, 0.75)

    # box edges: thin for all twelve, thick and coloured for the three at p
    def corner(a, b, c):
        return sph(R0 + a * DR, T0 + b * DT, F0 + c * DF)

    for b in (0, 1):
        for c in (0, 1):
            S.line([corner(0, b, c), corner(1, b, c)], TEXT, 0.9, None, 0.5)
    for a in (0, 1):
        for c in (0, 1):
            S.curve(lambda t, a=a, c=c: sph(R0 + a * DR, T0 + t, F0 + c * DF), 0.0, DT, TEXT, 0.9, 24,
                    None, 0.5)
    for a in (0, 1):
        for b in (0, 1):
            S.curve(lambda t, a=a, b=b: sph(R0 + a * DR, T0 + b * DT, F0 + t), 0.0, DF, TEXT, 0.9, 24,
                    None, 0.5)
    # translucent faces through p
    n = 12
    face_r = [sph(R0, T0 + DT * k / n, F0) for k in range(n + 1)] + \
             [sph(R0, T0 + DT * (n - k) / n, F0 + DF) for k in range(n + 1)]
    S.polygon(face_r, THEORY, 0.07)

    S.line([p, corner(1, 0, 0)], PRACTICE, 3.0)
    S.curve(lambda t: sph(R0, T0 + t, F0), 0.0, DT, BASE, 3.0, 24)
    S.curve(lambda t: sph(R0, T0, F0 + t), 0.0, DF, THEORY, 3.0, 24)
    S.point(p, TEXT, 3.6)

    at(p, bold("p"), -8, 17, TEXT, 12, "end")
    at(sph(R0 + DR / 2, T0, F0), ital("d" + RHO_S), -2, -9, PRACTICE, 12, "end")
    at(sph(R0, T0 + DT, F0), ital(RHO_S) + " cos " + ital(PHI_S) + " " + ital("d" + TH_S),
       9, 6, BASE, 12, "start")
    at(sph(R0, T0, F0 + DF / 2), ital(RHO_S + " d" + PHI_S), -10, 2, THEORY, 12, "end")
    at(sph(R0 * 0.4, T0, F0), ital(RHO_S), 0, -8, TEXT, 12, "middle")
    at((foot[0] * 0.55, foot[1] * 0.55, 0.0), ital(RHO_S) + " cos " + ital(PHI_S), 0, 18, TEXT, 11.5,
       "middle")
    at(sph(1.35, T0, F0 / 2), ital(PHI_S), 3, 5, TEXT, 12, "start")

    return figure(
        470, 360, [pl],
        "Küresel koordinatlar <em>&#961;</em>, <em>&#977;</em>, <em>&#966;</em> değerlerinden "
        "<em>d&#961;</em>, <em>d&#977;</em>, <em>d&#966;</em> kadar artınca oluşan küçük kutu "
        "(artımlar görünsün diye büyütülmüştür). <strong>p</strong>&#8217;den çıkan üç kenar "
        "<em>F</em><sub>1</sub> (turuncu), <em>F</em><sub>2</sub> (yeşil) ve <em>F</em><sub>3</sub> (mavi) "
        "doğrultularındadır. <em>&#977;</em> kenarı, yarıçapı <em>&#961;</em> cos <em>&#966;</em> olan yatay "
        "paralel çemberin bir yayıdır; <em>&#966;</em> kenarı ise yarıçapı <em>&#961;</em> olan meridyenin "
        "bir yayıdır. Kenar uzunlukları <em>d&#961;</em>, <em>&#961;</em> cos <em>&#966;</em> <em>d&#977;</em> "
        "ve <em>&#961;</em> <em>d&#966;</em>, yani sırasıyla <em>&#952;</em><sub>1</sub>, "
        "<em>&#952;</em><sub>2</sub>, <em>&#952;</em><sub>3</sub> dual formlarıdır.",
        aria="Small spherical coordinate box at p with rho = 4, theta = 0.25, phi = 0.5; the edge along "
             "F1 has length d rho, the edge along F2 is an arc of the parallel circle of radius "
             "rho cos phi, the edge along F3 is an arc of the meridian of radius rho",
    )


OUT["yapi-kuresel-kutu"] = fig_spherical_box()


# ============================================================ yapi-silindirik-kutu
# yapi-silindirik-kutu: the small cylindrical-coordinate box at (r, theta, z) = (3, 0.35, 1.2);
# edges dr (along E1), r d theta (arc of the circle of radius r, along E2), dz (along E3).
def cyl(r, t, z):
    return (r * math.cos(t), r * math.sin(t), z)


def fig_cylindrical_box():
    R0, T0, Z0 = 3.0, 0.35, 1.2
    DR, DT, DZ = 1.1, 0.36, 1.1
    pl = space_panel(20, 16, 430, (-3.2, 4.2), (-1.9, 3.7))
    S = Space(pl, Camera(azimuth=58.0, elevation=18.0, scale=1.0))

    def at(Q, s, dx=0, dy=0, color=TEXT, size=11.5, anchor="start"):
        X, Y = S.pt(Q)
        halo(pl, pl.X(X) + dx, pl.Y(Y) + dy, s, color, size, anchor)

    S.floor_grid((0, 4), (0, 3), n=4, opacity=0.08)
    S.axes(5.3, 4.0, 3.6, offsets=((-4, 14), (10, 4), (-10, -4)))

    p = cyl(R0, T0, Z0)
    foot = (p[0], p[1], 0.0)
    S.guide([p, foot], TEXT, 0.45, 1.0)
    S.line([(0.0, 0.0, 0.0), foot], TEXT, 1.1, None, 0.55)
    S.curve(lambda t: cyl(R0, t, Z0), -0.3, 1.25, TEXT, 0.9, 96, None, 0.4)
    S.curve(lambda t: cyl(1.0, t, 0.0), 0.0, T0, TEXT, 1.1, 40, None, 0.75)

    def corner(a, b, c):
        return cyl(R0 + a * DR, T0 + b * DT, Z0 + c * DZ)

    for b in (0, 1):
        for c in (0, 1):
            S.line([corner(0, b, c), corner(1, b, c)], TEXT, 0.9, None, 0.5)
    for a in (0, 1):
        for c in (0, 1):
            S.curve(lambda t, a=a, c=c: cyl(R0 + a * DR, T0 + t, Z0 + c * DZ), 0.0, DT, TEXT, 0.9, 24,
                    None, 0.5)
    for a in (0, 1):
        for b in (0, 1):
            S.line([corner(a, b, 0), corner(a, b, 1)], TEXT, 0.9, None, 0.5)
    n = 12
    face = [cyl(R0, T0 + DT * k / n, Z0) for k in range(n + 1)] + \
           [cyl(R0, T0 + DT * (n - k) / n, Z0 + DZ) for k in range(n + 1)]
    S.polygon(face, THEORY, 0.07)

    S.line([p, corner(1, 0, 0)], PRACTICE, 3.0)
    S.curve(lambda t: cyl(R0, T0 + t, Z0), 0.0, DT, BASE, 3.0, 24)
    S.line([p, corner(0, 0, 1)], THEORY, 3.0)
    S.point(p, TEXT, 3.6)

    at(p, bold("p"), -8, 17, TEXT, 12, "end")
    at(cyl(R0 + DR / 2, T0, Z0), ital("dr"), -2, -9, PRACTICE, 12, "end")
    at(cyl(R0, T0 + DT, Z0), ital("r d" + TH_S), 9, 6, BASE, 12, "start")
    at(cyl(R0, T0, Z0 + DZ / 2), ital("dz"), -9, 4, THEORY, 12, "end")
    at((foot[0] * 0.6, foot[1] * 0.6, 0.0), ital("r"), 0, 17, TEXT, 12, "middle")
    at(cyl(1.3, T0 / 2, 0.0), ital(TH_S), 4, 6, TEXT, 12, "start")

    return figure(
        470, 330, [pl],
        "Silindirik koordinatlar <em>r</em>, <em>&#977;</em>, <em>z</em> değerlerinden "
        "<em>dr</em>, <em>d&#977;</em>, <em>dz</em> kadar artınca oluşan küçük kutu (artımlar "
        "büyütülmüştür). <strong>p</strong>&#8217;den çıkan üç kenar <em>E</em><sub>1</sub> (turuncu), "
        "<em>E</em><sub>2</sub> (yeşil) ve <em>E</em><sub>3</sub> (mavi) doğrultularındadır. "
        "<em>&#977;</em> kenarı yarıçapı <em>r</em> olan yatay çemberin bir yayıdır ve uzunluğu "
        "<em>r</em> <em>d&#977;</em>&#8217;dır; öteki iki kenarın uzunlukları <em>dr</em> ve <em>dz</em>&#8217;dir. "
        "Bunlar <em>&#952;</em><sub>1</sub>, <em>&#952;</em><sub>2</sub>, <em>&#952;</em><sub>3</sub> dual "
        "formlarıdır.",
        aria="Small cylindrical coordinate box at p with r = 3, theta = 0.35, z = 1.2; edges of lengths "
             "dr along E1, r d theta along E2 (an arc of the horizontal circle of radius r) and dz along E3",
    )


OUT["yapi-silindirik-kutu"] = fig_cylindrical_box()


# ============================================================ yapi-yukseklik-cati
# yapi-yukseklik-cati: the frame field E1 = cos z U1 + sin z U2, E2 = -sin z U1 + cos z U2, E3 = U3
# at the points (0, 0, z) for z = 0, pi/3, 2 pi/3, pi. The tips of E1 trace the helix
# t -> (cos t, sin t, t): one radian of turn per unit of height, which is omega_12 = dz.
# A second copy of the frame at (0, 3, pi/3) shows that a horizontal step does not turn the frame.
def fig_height_frame():
    pl = space_panel(20, 16, 440, (-2.6, 5.4), (-1.6, 4.6))
    S = Space(pl, Camera(azimuth=28.0, elevation=30.0, scale=1.0))

    def at(Q, s, dx=0, dy=0, color=TEXT, size=11.5, anchor="start"):
        X, Y = S.pt(Q)
        halo(pl, pl.X(X) + dx, pl.Y(Y) + dy, s, color, size, anchor)

    S.floor_grid((-1, 3), (-1, 1), n=4, opacity=0.08)
    S.axes(3.9, 1.8, 4.3, offsets=((-4, 14), (10, 4), (-10, -4)))
    S.curve(lambda t: (math.cos(t), math.sin(t), t), 0.0, math.pi, TEXT, 1.1, 120, "3 3", 0.6)

    heights = [0.0, math.pi / 3, 2 * math.pi / 3, math.pi]
    names = ["0", "&#960;/3", "2&#960;/3", "&#960;"]
    for z, nm in zip(heights, names):
        Q = (0.0, 0.0, z)
        S.arrow(Q, vadd(Q, (math.cos(z), math.sin(z), 0.0)), PRACTICE, 2.4, 7.5)
        S.arrow(Q, vadd(Q, (-math.sin(z), math.cos(z), 0.0)), BASE, 2.4, 7.5)
        S.point(Q, TEXT, 3.0)
        at(Q, ital("z") + " = " + nm, -12, 4, TEXT, 11, "end")
    top = (0.0, 0.0, math.pi)
    S.arrow(top, vadd(top, (0.0, 0.0, 1.0)), THEORY, 2.4, 7.5)
    at(vadd(top, (0.0, 0.0, 1.0)), name("E", 3), 8, 2, THEORY, 11.5, "start")

    # a second copy at the same height, three units along x
    h = math.pi / 3
    Q2 = (0.0, 3.0, h)
    S.guide([(0.0, 0.0, h), Q2], TEXT, 0.5, 1.0)
    S.arrow(Q2, vadd(Q2, (math.cos(h), math.sin(h), 0.0)), PRACTICE, 2.4, 7.5)
    S.arrow(Q2, vadd(Q2, (-math.sin(h), math.cos(h), 0.0)), BASE, 2.4, 7.5)
    S.point(Q2, TEXT, 3.0)

    z0 = (0.0, 0.0, 0.0)
    at(vadd(z0, (1.0, 0.0, 0.0)), name("E", 1), 2, 15, PRACTICE, 11.5, "middle")
    at(vadd(z0, (0.0, 1.0, 0.0)), name("E", 2), 8, 12, BASE, 11.5, "start")
    at(Q2, "(0, 3, &#960;/3)", -10, 20, TEXT, 11, "middle")

    return figure(
        480, 400, [pl],
        "<em>E</em><sub>1</sub> = cos <em>z</em> <em>U</em><sub>1</sub> + sin <em>z</em> <em>U</em><sub>2</sub>, "
        "<em>E</em><sub>2</sub> = &#8722;sin <em>z</em> <em>U</em><sub>1</sub> + cos <em>z</em> <em>U</em><sub>2</sub>, "
        "<em>E</em><sub>3</sub> = <em>U</em><sub>3</sub> çatı alanı <em>z</em> ekseni üzerinde dört yükseklikte. "
        "Çatı her birim yükselişte bir radyan döner: <em>E</em><sub>1</sub>&#8217;in uçları kesikli "
        "helis üzerindedir. Sağdaki kopya aynı yükseklikte, üç birim ötedeki (0, 3, &#960;/3) noktasındaki "
        "çatıdır ve soldakiyle aynıdır; yatay adımda çatı dönmez. Tek bağlantı formunun "
        "<em>&#969;</em><sub>12</sub> = <em>dz</em> olması bunu söyler.",
        aria="The frame field E1 = (cos z, sin z, 0), E2 = (-sin z, cos z, 0), E3 = U3 drawn at (0, 0, z) "
             "for z = 0, pi/3, 2 pi/3, pi; the tips of E1 lie on a dashed helix; a copy of the frame at "
             "(0, 3, pi/3) equals the frame at (0, 0, pi/3)",
    )


OUT["yapi-yukseklik-cati"] = fig_height_frame()


# ============================================================ yapi-duzlem-psi
# yapi-duzlem-psi: two panels. Left: the plane frame field with angle function psi = x/2, sampled
# on a grid (arrows at half length so neighbours do not touch). Right: one point, the natural
# frame U1, U2 in grey and E1, E2 turned by the angle psi.
def fig_plane_psi():
    L = cplane(24, 30, 300, (-0.6, 5.6), (-0.6, 3.1))
    for i in range(6):
        for j in range(3):
            x, y = float(i), float(j) * 1.25
            psi = x / 2
            c, s = math.cos(psi), math.sin(psi)
            L.arrow((x, y), (x + 0.45 * c, y + 0.45 * s), PRACTICE, 1.9, 6.5)
            L.arrow((x, y), (x - 0.45 * s, y + 0.45 * c), BASE, 1.9, 6.5)
            dot(L, (x, y), TEXT, 2.2)
    L.arrow((-0.4, -0.4), (5.4, -0.4), TEXT, 1.0, 6, None, 0.5)
    L.label(5.4, -0.4, "x", 0, 15, TEXT, 11.5, "middle", False, True)
    for i in range(6):
        L.line([(i, -0.45), (i, -0.35)], TEXT, 1.0, None, 0.6)
        L.label(i, -0.4, str(i), 0, 14, TEXT, 10, "middle")
    panel_title(L, ital(PSI_S) + " = " + ital("x") + "/2")

    R = cplane(360, 30, 250, (-1.4, 1.6), (-0.9, 1.6))
    O = (0.0, 0.0)
    psi = 0.6
    c, s = math.cos(psi), math.sin(psi)
    R.arrow(O, (1.2, 0.0), TEXT, 2.0, 8, None, 0.55)
    R.arrow(O, (0.0, 1.2), TEXT, 2.0, 8, None, 0.55)
    R.arrow(O, (1.2 * c, 1.2 * s), PRACTICE, 2.4, 9)
    R.arrow(O, (-1.2 * s, 1.2 * c), BASE, 2.4, 9)
    R.arc(0.0, 0.0, 0.55, 0.0, psi, TEXT, 1.2, None, 0.8)
    R.arc(0.0, 0.0, 0.42, math.pi / 2, math.pi / 2 + psi, TEXT, 1.2, None, 0.8)
    dot(R, O, TEXT, 3.2)
    R.label(1.2, 0.0, name("U", 1), 4, 16, TEXT, 11.5, "middle")
    R.label(0.0, 1.2, name("U", 2), 8, 2, TEXT, 11.5, "start")
    R.label(1.2 * c, 1.2 * s, name("E", 1), 7, 0, PRACTICE, 11.5, "start")
    R.label(-1.2 * s, 1.2 * c, name("E", 2), -6, -2, BASE, 11.5, "end")
    R.label(0.68 * math.cos(psi / 2), 0.68 * math.sin(psi / 2), ital(PSI_S), 2, 5, TEXT, 12, "start")
    R.label(-0.55 * math.sin(psi / 2), 0.55 * math.cos(psi / 2), ital(PSI_S), -3, -2, TEXT, 12, "end")
    R.label(0.0, 0.0, bold("p"), -6, 15, TEXT, 12, "end")
    panel_title(R, "bir noktada")

    return figure(
        630, 250, [L, R],
        "Düzlemde bir çatı alanı, bir açı fonksiyonuyla. Solda <em>&#968;</em> = <em>x</em>/2 için çatı "
        "alanının örnek noktalardaki değerleri (oklar yarı boyda çizilmiştir): <em>x</em> arttıkça çatı "
        "saatin tersi yönünde döner, <em>y</em> değişince hiç değişmez. Sağda tek bir noktada doğal çatı "
        "<em>U</em><sub>1</sub>, <em>U</em><sub>2</sub> (gri) ve onun <em>&#968;</em> açısı kadar "
        "döndürülmüşü olan <em>E</em><sub>1</sub> (turuncu), <em>E</em><sub>2</sub> (yeşil).",
        css_class=WIDE,
        aria="Left: plane frame field with angle psi = x/2 sampled on a grid, frames turning as x grows. "
             "Right: at one point the natural frame U1, U2 in grey and E1, E2 obtained by turning it "
             "through the angle psi",
    )


OUT["yapi-duzlem-psi"] = fig_plane_psi()


# ---------------------------------------------------------------------------
for key, content in OUT.items():
    with io.open(OUT_DIR / f"diffgeo-{key}.md", "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
print("generated:", len(OUT), "figures")
