# -*- coding: utf-8 -*-
"""
Figures of the chapter "Bağlantı Formları"
(dersler/diferansiyel-geometri/1/baglanti-formlari.qmd), key `baglanti`.

The figures are NOT produced at build time. Run

    python scripts/diffgeo_figures_extra/baglanti.py
    python scripts/center_figures.py "diffgeo-baglanti-*.md" --keep-width

and paste the markup from scripts/_figures/diffgeo-baglanti-<name>.md into the
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
TH_S, PHI_S, RHO_S, OMEGA_S, DELTA_S, PI_CH = "&#977;", "&#966;", "&#961;", "&#969;", "&#916;", "&#960;"


def subs(s, size=9):
    return f'<tspan font-size="{size}" dy="4">{s}</tspan><tspan dy="-4">&#8203;</tspan>'


def ital(s):
    return f'<tspan font-style="italic">{s}</tspan>'


def bold(s):
    return f'<tspan font-weight="700">{s}</tspan>'


def name(letter, k):
    return ital(letter) + subs(str(k))


def omega(ij):
    return ital(OMEGA_S) + subs(ij)


def halo(panel, px, py, s, color=TEXT, size=11.5, anchor="start"):
    """Text on a page-coloured halo, so faint lines break around it."""
    panel.add(f'<text x="{px:.1f}" y="{py:.1f}" fill="{color}" font-size="{size}" '
              f'text-anchor="{anchor}" stroke="{BG}" stroke-width="3.2" stroke-linejoin="round" '
              f'paint-order="stroke">{s}</text>')


def at(S, P, s, dx=0, dy=0, color=TEXT, size=11.5, anchor="start"):
    """Halo text hung on a space point of the Space S."""
    X, Y = S.pt(P)
    halo(S.p, S.p.X(X) + dx, S.p.Y(Y) + dy, s, color, size, anchor)


def cyl_frame(theta):
    """Cylindrical frame at polar angle theta: E1, E2, E3."""
    c, s = math.cos(theta), math.sin(theta)
    return (c, s, 0.0), (-s, c, 0.0), (0.0, 0.0, 1.0)


# ============================================================ baglanti-vida
# baglanti-vida: the frame field E1 = cos z U1 + sin z U2, E2 = -sin z U1 + cos z U2, E3 = U3 at
# five points of the z axis, z = 0, pi/4, pi/2, 3pi/4, pi. Climbing along U3 the frame turns by
# the height itself (an eighth of a turn per pi/4), which is omega12(U3) = dz(U3) = 1: E1 turns
# toward E2 at unit rate. The tips of E1 lie on the helix (cos z, sin z, z), drawn faint and
# dashed; E3 = U3 is the same everywhere and is drawn once, at the top. The height labels sit on
# the page-right side of each disc, where no arrow of that level reaches.
def fig_screw():
    AZ, EL = 35.0, 17.0
    P = space_panel(10, 10, 360, (-2.2, 3.4), (-1.0, 4.9))
    S = Space(P, Camera(azimuth=AZ, elevation=EL))
    right = (-math.sin(math.radians(AZ)), math.cos(math.radians(AZ)), 0.0)
    heights = [k * math.pi / 4 for k in range(5)]
    names = ["0", PI_CH + "/4", PI_CH + "/2", "3" + PI_CH + "/4", PI_CH]
    for z in heights:
        e1, e2, e3 = cyl_frame(z)
        assert abs(vdot(e1, e2)) < 1e-12 and abs(vnorm(e1) - 1) < 1e-12
    S.line([(0, 0, -0.6), (0, 0, 4.3)], TEXT, 1.1, None, 0.55)
    S.arrow((0, 0, 4.2), (0, 0, 4.6), TEXT, 1.1, 7, None, 0.55)
    S.label((0, 0, 4.6), "z", 8, 0, TEXT, 11.5, "start", False, True)
    for z in heights:
        S.circle((0, 0, z), (1, 0, 0), (0, 1, 0), 1.0, TEXT, 0.8, None, 96, 0.28)
    S.curve(lambda t: (math.cos(t), math.sin(t), t), -0.15, math.pi + 0.15, PRACTICE, 1.1, 160,
            "4 3", 0.55)
    for z, zname in zip(heights, names):
        e1, e2, _ = cyl_frame(z)
        Q = (0.0, 0.0, z)
        S.arrow(Q, vadd(Q, e1), PRACTICE, 2.3, 7.5)
        S.arrow(Q, vadd(Q, e2), BASE, 2.3, 7.5)
        S.point(Q, TEXT, 3.0)
        at(S, vadd(Q, vscale(1.25, right)), ital("z") + " = " + zname, 0, 4, TEXT, 11, "start")
    top = (0.0, 0.0, heights[-1])
    S.arrow(top, vadd(top, (0, 0, 1)), THEORY, 2.3, 7.5)
    at(S, vadd(top, (0, 0, 1)), name("E", 3), 8, 4, THEORY, 11.5)
    e1, e2, _ = cyl_frame(0.0)
    at(S, e1, name("E", 1), -6, 12, PRACTICE, 11.5, "end")
    at(S, e2, name("E", 2), 4, 14, BASE, 11.5, "start")
    return figure(
        380, 400, [P],
        "Yükseklikle dönen çatı alanı <em>z</em> ekseninin beş noktasında: <em>z</em> = 0, "
        "&#960;/4, &#960;/2, 3&#960;/4, &#960;. Her yatay düzlemde çatı sabittir; yukarı çıktıkça "
        "<em>E</em><sub>1</sub> (turuncu) ile <em>E</em><sub>2</sub> (yeşil) birlikte, yükseklik kadar "
        "açıyla döner: her &#960;/4 yükselişte turun sekizde biri. <em>E</em><sub>1</sub>&#8217;in "
        "uçları kesikli helis üzerindedir. <em>U</em><sub>3</sub> yönünde birim hızla çıkarken <em>E</em><sub>1</sub>, "
        "<em>E</em><sub>2</sub>&#8217;ye doğru birim hızla döner: <em>&#969;</em><sub>12</sub>(<em>U</em><sub>3</sub>) "
        "= <em>dz</em>(<em>U</em><sub>3</sub>) = 1. <em>E</em><sub>3</sub> (mavi) her yerde aynıdır.",
        aria="The z axis with the rotating frame E1 = (cos z, sin z, 0), E2 = (-sin z, cos z, 0) drawn at "
             "heights 0, pi/4, pi/2, 3pi/4, pi; the frame turns by the height; the tips of E1 lie on "
             "a dashed helix; E3 = U3 drawn once at the top",
    )


OUT["baglanti-vida"] = fig_screw()


# ============================================================ baglanti-donme-hizi
# baglanti-donme-hizi: top view of the xy plane with the cylindrical (polar) frame. p lies on the
# circle r = 3 at polar angle 30 degrees, q on the same circle at 65 degrees, s on the ray of p at
# r = 5. The frame at q is turned by the same 35 degrees as the polar angle: a copy of E1(q) is
# drawn dashed at p and the arc between E1(p) and that copy repeats the arc at O. Along the ray
# (from p to s) the polar angle does not change and neither does the frame.
def fig_rotation_rate():
    pl = cplane(18, 14, 360, (-1.2, 6.4), (-0.9, 6.2))
    a_p, a_q = math.radians(30.0), math.radians(65.0)
    R1, R2 = 3.0, 5.0
    O = (0.0, 0.0)
    p = polar(R1, a_p)
    q = polar(R1, a_q)
    s = polar(R2, a_p)
    # axes
    pl.arrow((-0.9, 0.0), (6.2, 0.0), TEXT, 1.1, 7, None, 0.5)
    pl.arrow((0.0, -0.7), (0.0, 6.0), TEXT, 1.1, 7, None, 0.5)
    pl.label(6.2, 0.0, "x", -2, 16, TEXT, 11.5, "middle", False, True)
    pl.label(0.0, 6.0, "y", 8, 2, TEXT, 11.5, "start", False, True)
    # circle r = 3 (dashed, first quadrant and a bit more) and the two rays
    pl.arc(0.0, 0.0, R1, math.radians(-8), math.radians(100), TEXT, 1.0, "4 3", 0.45)
    pl.line([O, polar(5.9, a_p)], TEXT, 1.0, "4 3", 0.45)
    pl.line([O, q], TEXT, 1.0, "4 3", 0.45)
    # the angle 35 degrees at O
    pl.arc(0.0, 0.0, 1.1, a_p, a_q, TEXT, 1.2, None, 0.8)
    mid = (a_p + a_q) / 2
    pl.label(1.45 * math.cos(mid), 1.45 * math.sin(mid), DELTA_S + ital(TH_S), 0, 4, TEXT, 11.5, "middle")

    def frame(P, a, op=1.0):
        e1, e2 = polar(1.0, a), polar(1.0, a + math.pi / 2)
        pl.arrow(P, (P[0] + e1[0], P[1] + e1[1]), PRACTICE, 2.3, 8.5, None, op)
        pl.arrow(P, (P[0] + e2[0], P[1] + e2[1]), BASE, 2.3, 8.5, None, op)

    frame(p, a_p)
    frame(q, a_q)
    frame(s, a_p)
    # copy of E1(q) placed at p, and the arc between E1(p) and it
    cq = polar(1.0, a_q)
    pl.arrow(p, (p[0] + cq[0], p[1] + cq[1]), PRACTICE, 1.4, 7.5, "3 2.5", 0.8)
    pl.arc(p[0], p[1], 0.62, a_p, a_q, TEXT, 1.2, None, 0.8)
    pl.label(p[0] + 0.88 * math.cos(mid), p[1] + 0.88 * math.sin(mid), DELTA_S + ital(TH_S),
             0, 4, TEXT, 11, "middle")
    # the motion from p to q along the circle, drawn as a thin arrow on the circle
    for P in (p, q, s):
        dot(pl, P, TEXT, 3.4)
    dot(pl, O, TEXT, 3.0)
    pl.label(0.0, 0.0, "O", -7, 15, TEXT, 11.5, "end")
    pl.label(p[0], p[1], bold("p"), 4, 17, TEXT, 12, "start")
    pl.label(q[0], q[1], bold("q"), -8, 4, TEXT, 12, "end")
    pl.label(s[0], s[1], bold("s"), 6, 16, TEXT, 12, "start")
    e1q, e2q = polar(1.0, a_q), polar(1.0, a_q + math.pi / 2)
    pl.label(q[0] + e1q[0], q[1] + e1q[1], name("E", 1), 6, 2, PRACTICE, 11.5, "start")
    pl.label(q[0] + e2q[0], q[1] + e2q[1], name("E", 2), -6, 2, BASE, 11.5, "end")
    e1s, e2s = polar(1.0, a_p), polar(1.0, a_p + math.pi / 2)
    pl.label(s[0] + e1s[0], s[1] + e1s[1], name("E", 1), 6, 4, PRACTICE, 11.5, "start")
    pl.label(s[0] + e2s[0], s[1] + e2s[1], name("E", 2), -6, 0, BASE, 11.5, "end")
    pl.label(p[0] + e1s[0], p[1] + e1s[1], name("E", 1), 8, 10, PRACTICE, 11.5, "start")
    pl.label(p[0] + e2s[0], p[1] + e2s[1], name("E", 2), -8, 2, BASE, 11.5, "end")
    pl.label(0.2, 5.55, ital("r") + " = 3 çemberi boyunca: çatı " + DELTA_S + ital(TH_S) + " kadar döner",
             0, 0, TEXT, 11, "start")
    pl.label(0.2, 5.05, "ışın boyunca (" + bold("p") + " &#8594; " + bold("s") + "): çatı değişmez",
             0, 0, TEXT, 11, "start")
    return figure(
        396, 410, [pl],
        "<em>xy</em> düzlemine üstten bakış: silindirik çatının <em>E</em><sub>1</sub> (turuncu) ve "
        "<em>E</em><sub>2</sub> (yeşil) okları <strong>p</strong>, <strong>q</strong> ve "
        "<strong>s</strong> noktalarında. <strong>p</strong>&#8217;den <strong>q</strong>&#8217;ya "
        "<em>r</em> = 3 çemberi üzerinde giderken çatı, noktanın <em>O</em> etrafındaki açısı "
        "<em>&#916;&#977;</em> kadar döner: kesikli turuncu ok <em>E</em><sub>1</sub>(<strong>q</strong>)&#8217;nun "
        "<strong>p</strong>&#8217;ye taşınmış kopyasıdır ve <em>E</em><sub>1</sub>(<strong>p</strong>) ile "
        "arasındaki açı <em>O</em>&#8217;daki açıyla aynıdır. Işın boyunca, <strong>p</strong>&#8217;den "
        "<strong>s</strong>&#8217;ye giderken açı ve çatı değişmez. Dönme hızı "
        "<em>&#969;</em><sub>12</sub>(<strong>v</strong>) = <em>d&#977;</em>(<strong>v</strong>)&#8217;dir.",
        aria="Top view of the xy plane. Points p and q on the circle r = 3 at polar angles 30 and 65 "
             "degrees, s on the ray of p at r = 5. Cylindrical frame E1 orange and E2 green at each point. "
             "A dashed copy of E1(q) at p makes the same angle delta theta with E1(p) as the angle at O; "
             "the frame at s equals the frame at p",
    )


OUT["baglanti-donme-hizi"] = fig_rotation_rate()


# ============================================================ baglanti-yarim-duzlem
# baglanti-yarim-duzlem: the half plane theta = 330 degrees through the z axis (translucent), a
# path inside it and the cylindrical frame at three points of the path: all three frames are the
# same, (cos 330, sin 330, 0), (-sin 330, cos 330, 0), U3. A second half plane theta = 100 degrees
# carries one frame, turned by 130 degrees: the frame depends on theta only. The two half planes
# open like a book facing the viewer (camera azimuth 35): theta = 330 to the page left, theta = 100
# to the page right; the floor arc marks the 130 degrees between them.
T0_DEG, T1_DEG = 330.0, 100.0


def fig_half_plane():
    P = space_panel(10, 10, 400, (-4.3, 4.0), (-1.9, 4.2))
    S = Space(P, Camera(azimuth=35.0, elevation=24.0))
    t0, t1 = math.radians(T0_DEG), math.radians(T1_DEG)

    def hp(theta, r, z):
        return (r * math.cos(theta), r * math.sin(theta), z)

    # the z axis
    S.line([(0, 0, -0.9), (0, 0, 3.6)], TEXT, 1.1, None, 0.55)
    S.arrow((0, 0, 3.4), (0, 0, 3.8), TEXT, 1.1, 7, None, 0.55)
    S.label((0, 0, 3.8), "z", 8, 0, TEXT, 11.5, "start", False, True)

    def draw_frame(Q, frame, scale=0.9):
        for vec, col in zip(frame, (PRACTICE, BASE, THEORY)):
            S.arrow(Q, vadd(Q, vscale(scale, vec)), col, 2.2, 7)
        S.point(Q, TEXT, 3.0)

    def plane(th, op):
        S.polygon([hp(th, 0, -0.8), hp(th, 4.0, -0.8), hp(th, 4.0, 3.2), hp(th, 0, 3.2)], TEXT, op,
                  TEXT, 0.8)

    # painter's order: back half plane and its frame, floor arc, then the front half plane
    plane(t1, 0.07)
    Q2 = hp(t1, 2.4, 1.2)
    draw_frame(Q2, cyl_frame(t1))
    turn = math.radians(130.0)
    S.curve(lambda u: hp(t0 + turn * u, 1.3, -0.8), 0.0, 1.0, TEXT, 1.1, 40, None, 0.7)
    at(S, hp(t0 + turn / 2, 1.3, -0.8), "130°", 0, 16, TEXT, 11, "middle")
    plane(t0, 0.11)
    # a path inside the front half plane, with the same frame at three of its points
    path = [hp(t0, 0.8 + 2.6 * u, 0.1 + 2.3 * u + 0.5 * math.sin(3.0 * u)) for u in [k / 60 for k in range(61)]]
    S.line(path, TEXT, 1.4, "5 3", 0.7)
    E1, E2, E3 = cyl_frame(t0)
    pts = [path[6], path[30], path[54]]
    for Q in pts:
        draw_frame(Q, (E1, E2, E3))
    Q = pts[2]
    at(S, vadd(Q, vscale(0.9, E1)), name("E", 1), 6, 8, PRACTICE, 11.5)
    at(S, vadd(Q, vscale(0.9, E2)), name("E", 2), -6, 12, BASE, 11.5, "end")
    at(S, vadd(Q, vscale(0.9, E3)), name("E", 3), 6, 2, THEORY, 11.5)
    at(S, hp(t0, 4.0, 3.2), ital(TH_S) + " = 330°", -4, -6, TEXT, 11, "end")
    at(S, hp(t1, 4.0, 3.2), ital(TH_S) + " = 100°", 4, -6, TEXT, 11, "start")
    return figure(
        420, 330, [P],
        "<em>z</em> ekseninden geçen <em>&#977;</em> = 330° yarım düzlemi içindeki bir yol (kesikli) "
        "ve yolun üç noktasında silindirik çatı: <em>E</em><sub>1</sub> (turuncu), "
        "<em>E</em><sub>2</sub> (yeşil), <em>E</em><sub>3</sub> (mavi). Yol boyunca "
        "<em>&#977;</em> değişmediği için <em>V</em>[<em>&#977;</em>] = 0 ve üç çatı aynıdır: "
        "&#8711;<sub><em>V</em></sub><em>E</em><sub>1</sub> = &#8711;<sub><em>V</em></sub><em>E</em><sub>2</sub> = 0. "
        "Sağdaki <em>&#977;</em> = 100° yarım düzlemindeki çatı ise 130° dönmüştür; çatı yalnızca "
        "<em>&#977;</em>&#8217;ya bağlıdır.",
        aria="Two vertical half planes through the z axis at theta = 330 and 100 degrees. A dashed path "
             "inside the first carries three identical cylindrical frames E1 orange, E2 green, E3 blue; "
             "the second half plane carries one frame turned by 130 degrees",
    )


OUT["baglanti-yarim-duzlem"] = fig_half_plane()


# ============================================================ baglanti-kuresel
# baglanti-kuresel: two panels in the meridian half plane (horizontal r, vertical z).
# (a) points of the circle rho = 4 at latitudes 25 and 55 degrees with F1 (orange, outward) and
#     F3 (blue, north); a dashed copy of F1 of the lower point sits at the upper point and the arc
#     between them repeats the 30 degree arc at O: moving north F1 turns toward F3 at the rate of
#     phi, omega13 = dphi.
# (b) one point at latitude 40 degrees: F1, F3 and the direction -E1 (towards the z axis) into
#     which F2 turns when moving east; -E1 = -cos(phi) F1 + sin(phi) F3, drawn as the parallelogram
#     of its two components. F2 points out of the page (dot in a circle).
def fig_spherical():
    RHO = 4.0
    pa = cplane(22, 30, 300, (-0.8, 5.6), (-0.8, 5.4))
    pb = cplane(372, 30, 300, (-0.8, 5.6), (-0.8, 5.4))
    for pl in (pa, pb):
        pl.arrow((-0.6, 0.0), (5.4, 0.0), TEXT, 1.1, 7, None, 0.5)
        pl.arrow((0.0, -0.6), (0.0, 5.2), TEXT, 1.1, 7, None, 0.5)
        pl.label(5.4, 0.0, "r", -2, 16, TEXT, 11.5, "middle", False, True)
        pl.label(0.0, 5.2, "z", 8, 2, TEXT, 11.5, "start", False, True)
        pl.arc(0.0, 0.0, RHO, math.radians(-8), math.radians(92), TEXT, 1.0, "4 3", 0.45)
        dot(pl, (0.0, 0.0), TEXT, 3.0)
        pl.label(0.0, 0.0, "O", -7, 15, TEXT, 11.5, "end")

    # (a)
    f1, f2 = math.radians(25.0), math.radians(55.0)
    for f in (f1, f2):
        P = polar(RHO, f)
        pa.line([(0.0, 0.0), P], TEXT, 1.0, "4 3", 0.45)
        o = polar(1.0, f)
        n = polar(1.0, f + math.pi / 2)
        pa.arrow(P, (P[0] + o[0], P[1] + o[1]), PRACTICE, 2.3, 8.5)
        pa.arrow(P, (P[0] + n[0], P[1] + n[1]), THEORY, 2.3, 8.5)
        dot(pa, P, TEXT, 3.4)
    P2 = polar(RHO, f2)
    c1 = polar(1.0, f1)
    pa.arrow(P2, (P2[0] + c1[0], P2[1] + c1[1]), PRACTICE, 1.4, 7.5, "3 2.5", 0.8)
    pa.arc(P2[0], P2[1], 0.6, f1, f2, TEXT, 1.2, None, 0.8)
    mid = (f1 + f2) / 2
    pa.label(P2[0] + 0.86 * math.cos(mid), P2[1] + 0.86 * math.sin(mid), DELTA_S + ital(PHI_S), 0, 4,
             TEXT, 11, "middle")
    pa.arc(0.0, 0.0, 1.2, f1, f2, TEXT, 1.2, None, 0.8)
    pa.label(1.55 * math.cos(mid), 1.55 * math.sin(mid), DELTA_S + ital(PHI_S), 0, 4, TEXT, 11, "middle")
    P1 = polar(RHO, f1)
    o1, n1 = polar(1.0, f1), polar(1.0, f1 + math.pi / 2)
    pa.label(P1[0] + o1[0], P1[1] + o1[1], name("F", 1), 6, 6, PRACTICE, 11.5)
    pa.label(P1[0] + n1[0], P1[1] + n1[1], name("F", 3), -2, -6, THEORY, 11.5, "end")
    o2, n2 = polar(1.0, f2), polar(1.0, f2 + math.pi / 2)
    pa.label(P2[0] + o2[0], P2[1] + o2[1], name("F", 1), 6, 0, PRACTICE, 11.5)
    pa.label(P2[0] + n2[0], P2[1] + n2[1], name("F", 3), -6, 2, THEORY, 11.5, "end")
    panel_title(pa, "kuzeye yürürken: " + omega("13") + " = " + ital("d" + PHI_S))

    # (b)
    f = math.radians(40.0)
    cf, sf = math.cos(f), math.sin(f)
    P = polar(RHO, f)
    pb.line([(0.0, 0.0), P], TEXT, 1.0, "4 3", 0.45)
    o = (cf, sf)
    n = (-sf, cf)
    L = 1.6                                   # the three arrows at p are drawn 1.6 units long
    comp_o = (-cf * L * o[0], -cf * L * o[1])           # -cos(phi) F1
    comp_n = (sf * L * n[0], sf * L * n[1])             # +sin(phi) F3
    tip = (P[0] + comp_o[0] + comp_n[0], P[1] + comp_o[1] + comp_n[1])
    assert abs(tip[0] - (P[0] - L)) < 1e-12 and abs(tip[1] - P[1]) < 1e-12   # = p - L E1
    pb.line([(P[0] + comp_o[0], P[1] + comp_o[1]), tip], TEXT, 1.0, "3 2.5", 0.55)
    pb.line([(P[0] + comp_n[0], P[1] + comp_n[1]), tip], TEXT, 1.0, "3 2.5", 0.55)
    pb.arrow(P, (P[0] + comp_o[0], P[1] + comp_o[1]), PRACTICE, 1.6, 7.5, "4 2.5", 0.9)
    pb.arrow(P, (P[0] + comp_n[0], P[1] + comp_n[1]), THEORY, 1.6, 7.5, "4 2.5", 0.9)
    pb.arrow(P, (P[0] + L * o[0], P[1] + L * o[1]), PRACTICE, 2.3, 8.5)
    pb.arrow(P, (P[0] + L * n[0], P[1] + L * n[1]), THEORY, 2.3, 8.5)
    pb.arrow(P, tip, BASE, 2.3, 8.5)
    # F2 out of the page at p
    X, Y = pb.X(P[0]), pb.Y(P[1])
    pb.add(f'<circle cx="{X:.1f}" cy="{Y:.1f}" r="6.5" fill="{BG}" stroke="{BASE}" stroke-width="1.6"/>')
    pb.add(f'<circle cx="{X:.1f}" cy="{Y:.1f}" r="2.2" fill="{BASE}"/>')
    pb.label(P[0] + L * o[0], P[1] + L * o[1], name("F", 1), 6, 4, PRACTICE, 11.5)
    pb.label(P[0] + L * n[0], P[1] + L * n[1], name("F", 3), -4, -6, THEORY, 11.5, "end")
    pb.label(tip[0], tip[1], MINUS_S + name("E", 1), -6, 4, BASE, 11.5, "end")
    pb.label(P[0] + comp_o[0], P[1] + comp_o[1], MINUS_S + "cos " + ital(PHI_S) + " " + name("F", 1),
             4, 17, PRACTICE, 11, "middle")
    pb.label(P[0] + comp_n[0], P[1] + comp_n[1], "sin " + ital(PHI_S) + " " + name("F", 3), -12, 2,
             THEORY, 11, "end")
    pb.label(P[0], P[1], name("F", 2), 10, 20, BASE, 11.5, "start")
    pb.label(P[0], P[1], "(sayfadan dışarı)", 10, 34, BASE, 10.5, "start")
    panel_title(pb, "doğuya yürürken " + name("F", 2) + ", " + MINUS_S + name("E", 1) + " yönüne döner")
    return figure(
        700, 380, [pa, pb],
        "Küresel çatının bağlantı formları, meridyen yarım düzleminde (yatay eksen <em>r</em>, düşey "
        "eksen <em>z</em>). Solda: <em>&#961;</em> = 4 çemberi üzerinde kuzeye yürürken dışa bakan "
        "<em>F</em><sub>1</sub> (turuncu), kuzeye bakan <em>F</em><sub>3</sub>&#8217;e (mavi) doğru, "
        "enlemdeki artış <em>&#916;&#966;</em> kadar döner; kesikli ok alttaki "
        "<em>F</em><sub>1</sub>&#8217;in taşınmış kopyasıdır. Bu, <em>&#969;</em><sub>13</sub> = "
        "<em>d&#966;</em> demektir. Sağda: doğuya bakan <em>F</em><sub>2</sub> (yeşil, sayfadan "
        "dışarı) doğuya yürürken <em>z</em> eksenine doğru, &#8722;<em>E</em><sub>1</sub> yönüne "
        "döner ve &#8722;<em>E</em><sub>1</sub> = &#8722;cos <em>&#966;</em> <em>F</em><sub>1</sub> + "
        "sin <em>&#966;</em> <em>F</em><sub>3</sub>&#8217;tür; dönmenin cos <em>&#966;</em> kadarı "
        "<em>F</em><sub>1</sub>&#8217;e, sin <em>&#966;</em> kadarı <em>F</em><sub>3</sub>&#8217;e "
        "yöneliktir: <em>&#969;</em><sub>12</sub> = cos <em>&#966;</em> <em>d&#977;</em>, "
        "<em>&#969;</em><sub>23</sub> = sin <em>&#966;</em> <em>d&#977;</em>.",
        css_class=WIDE,
        aria="Two panels in the meridian half plane with axes r and z. Left: points of the circle rho = 4 "
             "at latitudes 25 and 55 degrees with F1 outward orange and F3 north blue; a dashed copy of the "
             "lower F1 at the upper point makes the angle delta phi with the upper F1, the same as the angle "
             "at O. Right: at latitude 40 degrees F1, F3 and the vector -E1 toward the z axis, decomposed "
             "into -cos phi F1 and sin phi F3; F2 points out of the page",
    )


OUT["baglanti-kuresel"] = fig_spherical()


# ============================================================ baglanti-helis
# baglanti-helis: the frame field H1 = (4/5)E2 + (3/5)E3, H2 = -E1, H3 = -(3/5)E2 + (4/5)E3 (a = 4,
# b = 3) on two helices of the same slope 3/4: radius 4, (4 cos u, 4 sin u, 3u), and radius 2,
# (2 cos u, 2 sin u, 1.5u). On each helix H1, H2, H3 is its Frenet frame T, N, B. Frames are drawn
# at u = -0.3 and u = 1.9 on the large helix and at u = 1.9 on the small one: at the same polar
# angle the two frames are identical, while the curvatures differ, 4/25 and 8/25. The helices are
# drawn in the text colour so that the blue of H3 stays reserved for the frame.
def fig_helix():
    P = space_panel(10, 10, 420, (-4.9, 5.1), (-3.3, 7.4))
    S = Space(P, Camera(azimuth=35.0, elevation=27.0))

    def helix(R):
        return lambda u: (R * math.cos(u), R * math.sin(u), 0.75 * R * u)

    def hframe(u):
        e1, e2, e3 = cyl_frame(u)
        h1 = vadd(vscale(0.8, e2), vscale(0.6, e3))
        h2 = vscale(-1.0, e1)
        h3 = vadd(vscale(-0.6, e2), vscale(0.8, e3))
        return h1, h2, h3

    # the Frenet check: H1 is the unit tangent of both helices, H2 the principal normal
    for R in (4.0, 2.0):
        for u in (-0.3, 1.9):
            d = (-R * math.sin(u), R * math.cos(u), 0.75 * R)
            dd = (-R * math.cos(u), -R * math.sin(u), 0.0)
            assert vnorm(vsub(vunit(d), hframe(u)[0])) < 1e-12
            assert vnorm(vsub(vunit(dd), hframe(u)[1])) < 1e-12
    S.line([(0, 0, -1.8), (0, 0, 7.0)], TEXT, 1.1, None, 0.55)
    S.arrow((0, 0, 6.9), (0, 0, 7.3), TEXT, 1.1, 7, None, 0.55)
    S.label((0, 0, 7.3), "z", 8, 0, TEXT, 11.5, "start", False, True)
    for R, lo, hi in ((2.0, -1.0, 3.6), (4.0, -0.75, 2.3)):
        S.curve(helix(R), lo, hi, TEXT, 1.5, 240, None, 0.6)
    for R, u in ((2.0, 1.9), (4.0, -0.3), (4.0, 1.9)):
        Q = helix(R)(u)
        for vec, col in zip(hframe(u), (PRACTICE, BASE, THEORY)):
            S.arrow(Q, vadd(Q, vec), col, 2.3, 7.5)
        S.point(Q, TEXT, 3.2)
    Q = helix(4.0)(1.9)
    h1, h2, h3 = hframe(1.9)
    at(S, vadd(Q, h1), name("H", 1) + " = " + ital("T"), 6, 2, PRACTICE, 11)
    at(S, vadd(Q, h2), name("H", 2) + " = " + ital("N"), -4, 14, BASE, 11, "end")
    at(S, vadd(Q, h3), name("H", 3) + " = " + ital("B"), -6, -4, THEORY, 11, "end")
    at(S, helix(4.0)(2.3), ital("R") + " = 4:  " + ital("&#954;") + " = 4/25", -8, 2, TEXT, 11, "end")
    at(S, helix(2.0)(3.6), ital("R") + " = 2:  " + ital("&#954;") + " = 8/25", -8, -4, TEXT, 11, "end")
    return figure(
        440, 460, [P],
        "Eğimi 3/4 olan iki helis: yarıçapı 4 olan (4 cos <em>u</em>, 4 sin <em>u</em>, 3<em>u</em>) "
        "ve yarıçapı 2 olan (2 cos <em>u</em>, 2 sin <em>u</em>, 1,5<em>u</em>). "
        "<em>H</em><sub>1</sub> = (4/5)<em>E</em><sub>2</sub> + (3/5)<em>E</em><sub>3</sub> (turuncu), "
        "<em>H</em><sub>2</sub> = &#8722;<em>E</em><sub>1</sub> (yeşil), "
        "<em>H</em><sub>3</sub> = &#8722;(3/5)<em>E</em><sub>2</sub> + (4/5)<em>E</em><sub>3</sub> (mavi) "
        "çatı alanı her iki helis boyunca helisin Frenet çatısı <em>T</em>, <em>N</em>, <em>B</em>&#8217;dir. "
        "Aynı <em>&#977;</em> açısındaki iki noktada çatılar tamamen aynıdır; farklı olan, <em>T</em> "
        "yönünde yürürken <em>&#977;</em>&#8217;nın artma hızıdır. Bu yüzden bağlantı formları "
        "<em>&#969;</em><sub>12</sub> = (4/5) <em>d&#977;</em> ve <em>&#969;</em><sub>23</sub> = "
        "(3/5) <em>d&#977;</em> iki helise farklı eğrilik ve burulma verir: <em>&#954;</em> = 4/25 ile "
        "8/25, <em>&#964;</em> = 3/25 ile 6/25.",
        aria="Two helices of slope 3/4 around the z axis, radius 4 and radius 2, with the frame field "
             "H1 orange, H2 green, H3 blue drawn at two points of the large helix and one point of the "
             "small helix; at the same polar angle the frames coincide; they are the Frenet frames T, N, B",
    )


OUT["baglanti-helis"] = fig_helix()


# ---------------------------------------------------------------------------
for key, content in OUT.items():
    with io.open(OUT_DIR / f"diffgeo-{key}.md", "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
print("generated:", len(OUT), "figures")
