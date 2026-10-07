# -*- coding: utf-8 -*-
"""
Figures of the chapter "Yönlendirme"
(dersler/diferansiyel-geometri/1/yonlendirme.qmd), key `yonlen`.

The figures are NOT produced at build time. Run

    python scripts/diffgeo_figures_extra/yonlen.py
    python scripts/center_figures.py "diffgeo-yonlen-*.md" --keep-width

and paste the markup from scripts/_figures/diffgeo-yonlen-<name>.md into the
.qmd file. Figures go INSIDE the box they explain (theorem, proof, example,
solution or exercise), never inside a definition box.

Colours follow the book's frame convention: e1 -> PRACTICE, e2 -> BASE,
e3 -> THEORY; images under an isometry keep the colour of their originals.
Captions are Turkish (they are shown on the site); aria labels are ASCII.
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
TH_S, EPS_S, VTH_S = "&#952;", "&#949;", "&#977;"
TIMES_S = "&#215;"


def subs(s, size=9):
    return f'<tspan font-size="{size}" dy="4">{s}</tspan><tspan dy="-4">&#8203;</tspan>'


def ital(s):
    return f'<tspan font-style="italic">{s}</tspan>'


def bold(s):
    return f'<tspan font-weight="700">{s}</tspan>'


def name(letter, k):
    return ital(letter) + subs(str(k))


def fstar(arg):
    """F_*(arg)"""
    return ital("F") + subs("*") + "(" + arg + ")"


def halo(panel, px, py, s, color=TEXT, size=11.5, anchor="start"):
    """Text on a page-coloured halo, so faint lines break around it."""
    panel.add(f'<text x="{px:.1f}" y="{py:.1f}" fill="{color}" font-size="{size}" '
              f'text-anchor="{anchor}" stroke="{BG}" stroke-width="3.2" stroke-linejoin="round" '
              f'paint-order="stroke">{s}</text>')


def at(S, P, s, dx=0, dy=0, color=TEXT, size=11.5, anchor="start"):
    X, Y = S.pt(P)
    halo(S.p, S.p.X(X) + dx, S.p.Y(Y) + dy, s, color, size, anchor)


def arc3(S, O, a, b, r, t0, t1, color=TEXT, width=1.3, head=7.0, opacity=0.8):
    """Arc O + r(cos t a + sin t b), t in [t0, t1], with an arrowhead at t1."""
    def f(t):
        return vadd(O, vadd(vscale(r * math.cos(t), a), vscale(r * math.sin(t), b)))
    n = 40
    pts = [f(t0 + (t1 - t0) * k / n) for k in range(n + 1)]
    S.line(pts[:-3], color, width, None, opacity)
    S.arrow(pts[-4], pts[-1], color, width, head, None, opacity)


def frame(S, P, E, length=1.0, width=2.4, head=9.0):
    cols = (PRACTICE, BASE, THEORY)
    for k in range(3):
        S.arrow(P, vadd(P, vscale(length, E[k])), cols[k], width, head)


def depth_curve(S, f, t0, t1, color, width=2.0, n=360, back=0.3, center=None):
    """Space curve drawn in two bands: the half behind `center` faint, the front half solid.
    Returns a function that draws the front half, so other objects can be painted in between."""
    pts = [f(t0 + (t1 - t0) * k / n) for k in range(n + 1)]
    c = center if center is not None else (0.0, 0.0, 0.0)
    runs = []
    for k in range(n):
        mid = vscale(0.5, vadd(pts[k], pts[k + 1]))
        front = S.depth(mid) >= S.depth((c[0], c[1], mid[2]))
        if runs and runs[-1][0] == front:
            runs[-1][1].append(pts[k + 1])
        else:
            runs.append((front, [pts[k], pts[k + 1]]))
    for front, run in runs:
        if not front:
            S.line(run, color, width, None, back)

    def draw_front():
        for front, run in runs:
            if front:
                S.line(run, color, width)
    return draw_front


# ============================================================ yonlen-sag-sol-cati
# yonlen-sag-sol-cati: (P) e1 = x, e2 = y, e3 = z: positively oriented, e1 x e2 = e3.
# (N) e1 = y, e2 = x, e3 = z: negatively oriented, e1 x e2 = -e3 (drawn dashed, pointing down).
# The arc shows the short turn from e1 to e2; the right-hand rule reads e1 x e2 off it.
def fig_right_left():
    cam = Camera(azimuth=45.0, elevation=24.0)
    X, Y, Z = (1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)
    O = (0.0, 0.0, 0.0)
    panels = []
    for k, (E, title) in enumerate((((X, Y, Z), "pozitif yönlü (sağ elli)"),
                                    ((Y, X, Z), "negatif yönlü (sol elli)"))):
        pl = space_panel(20 + k * 370, 34, 340, (-1.45, 1.45), (-1.35, 1.3))
        S = Space(pl, cam)
        frame(S, O, E, 1.0, 2.6, 10)
        arc3(S, O, E[0], E[1], 0.55, 0.12, math.pi / 2 - 0.1, TEXT, 1.4, 8, 0.85)
        S.point(O, TEXT, 3.2)
        at(S, E[0], name("e", 1), -6 if k == 0 else 8, 16, PRACTICE, 12.5, "end" if k == 0 else "start")
        at(S, E[1], name("e", 2), 8 if k == 0 else -6, 16, BASE, 12.5, "start" if k == 0 else "end")
        if k == 0:
            at(S, E[2], name("e", 3) + " = " + name("e", 1) + " " + TIMES_S + " " + name("e", 2), 9, 4, THEORY,
               12.5)
        else:
            at(S, E[2], name("e", 3), 9, 4, THEORY, 12.5)
            S.arrow(O, (0.0, 0.0, -1.0), TEXT, 1.6, 8, "5 3", 0.75)
            at(S, (0.0, 0.0, -1.0), name("e", 1) + " " + TIMES_S + " " + name("e", 2) + " = " + MINUS_S
               + name("e", 3), 10, 4, TEXT, 12)
        panel_title(pl, title)
        panels.append(pl)
    return figure(
        740, 400, panels,
        "Solda pozitif yönlü, sağda negatif yönlü bir çatı. Kavisli ok <em>e</em><sub>1</sub>&#8217;i kısa "
        "yoldan <em>e</em><sub>2</sub>&#8217;ye döndürür. Sağ elin parmakları bu yönde kıvrılınca başparmak "
        "<em>e</em><sub>1</sub> &#215; <em>e</em><sub>2</sub> yönünü gösterir. Solda bu yön "
        "<em>e</em><sub>3</sub>&#8217;tür; sağda ise <em>e</em><sub>3</sub>&#8217;ün tersidir (kesikli ok).",
        css_class=WIDE,
        aria="Left: a positively oriented frame e1, e2, e3 with e1 x e2 = e3. Right: the frame with e1 and e2 "
             "interchanged, negatively oriented, where e1 x e2 = -e3 points downward",
    )


OUT["yonlen-sag-sol-cati"] = fig_right_left()


# ============================================================ yonlen-cevrim
# yonlen-cevrim: mnemonic for the cross products of a frame with sign eps = e1 . e2 x e3:
# following the arrows e1 -> e2 -> e3 -> e1, the product of two consecutive vectors is eps times the third.
def fig_cycle():
    pl = cplane(20, 20, 470, (-1.75, 3.6), (-1.5, 1.45))
    R = 1.0
    angs = [90.0, -30.0, 210.0]
    pos = [(R * math.cos(math.radians(a)), R * math.sin(math.radians(a))) for a in angs]
    cols = (PRACTICE, BASE, THEORY)
    for k in range(3):
        a0 = math.radians(angs[k]) - 0.36
        a1 = math.radians(angs[k]) - math.radians(120) + 0.36
        pts = circle_pts(0.0, 0.0, R, a0, a1, 40)
        pl.line(pts[:-3], TEXT, 1.6, None, 0.75)
        pl.arrow(pts[-4], pts[-1], TEXT, 1.6, 8, None, 0.75)
    for k in range(3):
        dot(pl, pos[k], cols[k], 4.0)
    pl.label(pos[0][0], pos[0][1], name("e", 1), 0, -11, PRACTICE, 12, "middle")
    pl.label(pos[1][0], pos[1][1], name("e", 2), 9, 15, BASE, 12, "start")
    pl.label(pos[2][0], pos[2][1], name("e", 3), -9, 15, THEORY, 12, "end")
    E = [name("e", k) for k in (1, 2, 3)]
    X = " " + TIMES_S + " "
    eps = ital(EPS_S)
    rows = [(E[0] + X + E[1] + " = " + eps + E[2], E[1] + X + E[0] + " = " + MINUS_S + eps + E[2]),
            (E[1] + X + E[2] + " = " + eps + E[0], E[2] + X + E[1] + " = " + MINUS_S + eps + E[0]),
            (E[2] + X + E[0] + " = " + eps + E[1], E[0] + X + E[2] + " = " + MINUS_S + eps + E[1])]
    pl.polygon([(1.25, -0.9), (3.62, -0.9), (3.62, 1.32), (1.25, 1.32)], TEXT, 0.05)
    pl.label(1.4, 1.05, "ok yönünde", 0, 0, TEXT, 11.5, "start", True)
    pl.label(2.55, 1.05, "ters yönde", 0, 0, TEXT, 11.5, "start", True)
    for k, (a, b) in enumerate(rows):
        y = 0.55 - 0.6 * k
        pl.label(1.4, y, a, 0, 0, TEXT, 12, "start")
        pl.label(2.55, y, b, 0, 0, TEXT, 12, "start")
    return figure(
        620, 300, [pl],
        "Bir çatının vektörel çarpım tablosunu hatırlamanın yolu. Oklar boyunca ardışık iki vektörün "
        "çarpımı üçüncünün <em>&#949;</em> katıdır (örneğin <em>e</em><sub>2</sub> &#215; <em>e</em><sub>3</sub> = "
        "<em>&#949;</em> <em>e</em><sub>1</sub>); oklara karşı gidince işaret değişir. Burada "
        "<em>&#949;</em> = <em>e</em><sub>1</sub> &#183; <em>e</em><sub>2</sub> &#215; <em>e</em><sub>3</sub>&#8217;tür.",
        aria="Cycle diagram e1 to e2 to e3 to e1: the cross product of two consecutive vectors along the arrows "
             "is eps times the third, against the arrows minus eps times the third",
    )


OUT["yonlen-cevrim"] = fig_cycle()


# ============================================================ yonlen-duzlem
# yonlen-duzlem: plane isometries acting on the natural frame U1, U2 (grey).
# Left: rotation by 30 degrees, images (cos 30, sin 30) and (-sin 30, cos 30), turn from image 1 to image 2
# counterclockwise. Right: reflection in the line through 0 at angle 30 degrees; U1 -> (cos 60, sin 60),
# U2 -> (sin 60, -cos 60); the turn from image 1 to image 2 is clockwise.
def fig_plane():
    panels = []
    a = math.radians(30)
    c, s = math.cos(a), math.sin(a)
    c2, s2 = math.cos(2 * a), math.sin(2 * a)
    for k in range(2):
        pl = cplane(20 + k * 300, 36, 270, (-1.45, 1.55), (-1.15, 1.45))
        # faint axes
        pl.line([(-1.35, 0.0), (1.45, 0.0)], TEXT, 0.8, None, 0.35)
        pl.line([(0.0, -1.05), (0.0, 1.35)], TEXT, 0.8, None, 0.35)
        pl.arrow((0.0, 0.0), (1.0, 0.0), TEXT, 1.6, 8, None, 0.45)
        pl.arrow((0.0, 0.0), (0.0, 1.0), TEXT, 1.6, 8, None, 0.45)
        if k == 0:
            i1, i2 = (c, s), (-s, c)
            t0 = math.atan2(i1[1], i1[0])
            arc = circle_pts(0.0, 0.0, 0.48, t0 + 0.12, t0 + math.pi / 2 - 0.12, 30)
            pl.label(1.0, 0.0, name("U", 1), 4, 15, TEXT, 11.5, "start")
            pl.label(0.0, 1.0, name("U", 2), 7, 3, TEXT, 11.5, "start")
            pl.label(i1[0], i1[1], ital("C") + "(" + name("U", 1) + ")", 7, 0, PRACTICE, 11.5, "start")
            pl.label(i2[0], i2[1], ital("C") + "(" + name("U", 2) + ")", -6, -4, BASE, 11.5, "end")
            pl.arc(0.0, 0.0, 0.8, 0.0, a, TEXT, 1.1, None, 0.7)
            pl.label(0.8 * math.cos(a / 2), 0.8 * math.sin(a / 2), "30°", 5, 5, TEXT, 11, "start")
            panel_title(pl, "dönme")
        else:
            i1, i2 = (c2, s2), (s2, -c2)
            # the mirror line at angle 30 degrees
            pl.line([(-1.3 * c, -1.3 * s), (1.45 * c, 1.45 * s)], TEXT, 1.2, "6 4", 0.7)
            pl.label(1.45 * c, 1.45 * s, "ℓ", 4, -3, TEXT, 12, "start", False, True)
            t0 = math.atan2(i1[1], i1[0])
            arc = circle_pts(0.0, 0.0, 0.48, t0 - 0.12, t0 - math.pi / 2 + 0.12, 30)
            pl.label(1.0, 0.0, name("U", 1), 4, 15, TEXT, 11.5, "start")
            pl.label(0.0, 1.0, name("U", 2), -7, 3, TEXT, 11.5, "end")
            pl.label(i1[0], i1[1], ital("C") + "(" + name("U", 1) + ")", 8, 2, PRACTICE, 11.5, "start")
            pl.label(i2[0], i2[1], ital("C") + "(" + name("U", 2) + ")", 8, 10, BASE, 11.5, "start")
            panel_title(pl, "yansıma")
        pl.line(arc[:-3], TEXT, 1.4, None, 0.85)
        pl.arrow(arc[-4], arc[-1], TEXT, 1.4, 7, None, 0.85)
        pl.arrow((0.0, 0.0), i1, PRACTICE, 2.4, 9)
        pl.arrow((0.0, 0.0), i2, BASE, 2.4, 9)
        dot(pl, (0.0, 0.0), TEXT, 3.0)
        panels.append(pl)
    return figure(
        600, 300, panels,
        "Düzlemde doğal çatı <em>U</em><sub>1</sub>, <em>U</em><sub>2</sub> (gri) ve iki ortogonal dönüşüm "
        "altındaki görüntüsü. Solda 30° dönme: görüntüde de birinci oktan ikinciye kısa dönüş saatin tersi "
        "yönündedir. Sağda başlangıç noktasından geçen ve <em>x</em> ekseniyle 30° açı yapan ℓ doğrusunda "
        "yansıma: görüntüde bu dönüş saat yönüne çevrilmiştir.",
        css_class=WIDE,
        aria="Left: the natural plane frame and its image under a rotation through 30 degrees, both turning "
             "counterclockwise. Right: its image under the reflection in the line at 30 degrees, which turns "
             "clockwise",
    )


OUT["yonlen-duzlem"] = fig_plane()


# ============================================================ yonlen-ayna
# yonlen-ayna: the reflection R(x, y, z) = (-x, y, z) in the yz plane. The frame
# e1 = (1,0,1)/sqrt2, e2 = (-1,0,1)/sqrt2, e3 = (0,-1,0) at p = (2, 1, 1) (right-handed: e1 x e2 = e3) and its
# image at R(p) = (-2, 1, 1): R*(e1) = (-1,0,1)/sqrt2 = e2, R*(e2) = (1,0,1)/sqrt2 = e1, R*(e3) = e3 (left-handed).
S2 = 1 / math.sqrt(2)
E_FRAME = ((S2, 0.0, S2), (-S2, 0.0, S2), (0.0, -1.0, 0.0))


def refl_x(v):
    return (-v[0], v[1], v[2])


def mirror_scene(pl, cam, z_lo=-0.4, z_hi=2.5, y_lo=-1.6, y_hi=3.0):
    S = Space(pl, cam)
    # the mirror: a patch of the plane x = 0
    S.polygon([(0.0, y_lo, z_lo), (0.0, y_hi, z_lo), (0.0, y_hi, z_hi), (0.0, y_lo, z_hi)], TEXT, 0.07,
              TEXT, 0.8)
    S.line([(0.0, y_lo, 0.0), (0.0, y_hi, 0.0)], TEXT, 0.8, "4 3", 0.4)
    return S


def fig_mirror():
    cam = Camera(azimuth=-40.0, elevation=12.0)
    pl = space_panel(16, 16, 660, (-3.3, 3.3), (-1.35, 2.75))
    S = mirror_scene(pl, cam)
    p = (2.0, 1.0, 1.0)
    q = refl_x(p)
    img = tuple(refl_x(v) for v in E_FRAME)
    S.guide([p, q], TEXT, 0.5, 1.0, "3 3")
    for P, E in ((q, img), (p, E_FRAME)):
        arc3(S, P, E[0], E[1], 0.42, 0.15, math.pi / 2 - 0.12, TEXT, 1.2, 7, 0.8)
        frame(S, P, E, 1.0, 2.4, 9)
        S.point(P, TEXT, 3.4)
    at(S, p, bold("p"), 6, 16, TEXT, 12)
    at(S, q, ital("R") + "(" + bold("p") + ")", -7, 17, TEXT, 12, "end")
    at(S, vadd(p, E_FRAME[0]), name("e", 1), 7, 5, PRACTICE, 12)
    at(S, vadd(p, E_FRAME[1]), name("e", 2), -2, -8, BASE, 12, "end")
    at(S, vadd(p, E_FRAME[2]), name("e", 3), -9, 5, THEORY, 12, "end")
    rs = ital("R") + subs("*")
    at(S, vadd(q, img[0]), rs + name("e", 1), -7, -2, PRACTICE, 12, "end")
    at(S, vadd(q, img[1]), rs + name("e", 2), 7, -6, BASE, 12)
    at(S, vadd(q, img[2]), rs + name("e", 3), -8, 6, THEORY, 12, "end")
    at(S, (0.0, 3.0, 2.5), ital("yz") + " düzlemi", -4, 14, TEXT, 11, "end")
    return figure(
        700, 480, [pl],
        "<em>yz</em> düzleminde yansıma. <strong>p</strong> = (2, 1, 1) noktasındaki sağ elli "
        "<em>e</em><sub>1</sub>, <em>e</em><sub>2</sub>, <em>e</em><sub>3</sub> çatısı (sağda) ve "
        "<em>R</em>(<strong>p</strong>) = (&#8722;2, 1, 1) noktasındaki görüntüsü (solda). Kavisli oklar "
        "birinci vektörden ikinciye kısa dönüşü gösterir. Ayna <em>e</em><sub>1</sub> ile "
        "<em>e</em><sub>2</sub>&#8217;nin doğrultularını yer değiştirir, <em>e</em><sub>3</sub>&#8217;ü "
        "olduğu gibi bırakır; bu yüzden görüntüde dönüş tersine çevrilir ve görüntü çatı sol ellidir.",
        aria="Reflection in the yz plane drawn as a translucent mirror: the right-handed frame at p = (2, 1, 1) "
             "and its left-handed image frame at R(p) = (-2, 1, 1)",
    )


OUT["yonlen-ayna"] = fig_mirror()


# ============================================================ yonlen-vektorel-ayna
# yonlen-vektorel-ayna: v = (0, 1, 2), w = (1, 0, 0) at p = (2, 0, 0); v x w = (0, 2, -1).
# Under R (reflection in the yz plane): R*v = v and R*(v x w) = v x w (both parallel to the mirror),
# R*w = -w; hence R*v x R*w = (0, -2, 1) = -R*(v x w) (dashed).
def fig_cross_mirror():
    cam = Camera(azimuth=55.0, elevation=15.0)
    pl = space_panel(16, 16, 520, (-3.4, 3.4), (-1.6, 2.6))
    S = mirror_scene(pl, cam, -1.4, 2.4, -1.6, 2.4)
    p = (2.0, 0.0, 0.0)
    q = refl_x(p)
    v, w = (0.0, 1.0, 2.0), (1.0, 0.0, 0.0)
    vw = vcross(v, w)
    rv, rw = refl_x(v), refl_x(w)
    rvw = refl_x(vw)
    cr = vcross(rv, rw)
    assert vw == (0.0, 2.0, -1.0) and max(abs(cr[i] + rvw[i]) for i in range(3)) < 1e-12
    S.guide([p, q], TEXT, 0.45, 1.0, "3 3")
    for P, a, b in ((q, rv, rw), (p, v, w)):
        S.arrow(P, vadd(P, a), PRACTICE, 2.3, 9)
        S.arrow(P, vadd(P, b), BASE, 2.3, 9)
    S.arrow(p, vadd(p, vw), THEORY, 2.5, 9)
    S.arrow(q, vadd(q, rvw), THEORY, 2.5, 9)
    S.arrow(q, vadd(q, cr), TEXT, 1.9, 9, "5 3", 0.85)
    S.point(p, TEXT, 3.4)
    S.point(q, TEXT, 3.4)
    rs = ital("R") + subs("*")
    at(S, p, bold("p"), 9, 5, TEXT, 12)
    at(S, q, ital("R") + "(" + bold("p") + ")", -9, 5, TEXT, 12, "end")
    at(S, vadd(p, v), bold("v"), 8, 4, PRACTICE, 12)
    at(S, vadd(p, w), bold("w"), -4, 15, BASE, 12, "end")
    at(S, vadd(p, vw), bold("v") + " " + TIMES_S + " " + bold("w"), 8, 8, THEORY, 12)
    at(S, vadd(q, rv), rs + bold("v"), 8, 4, PRACTICE, 12)
    at(S, vadd(q, rw), rs + bold("w"), 4, 15, BASE, 12)
    at(S, vadd(q, rvw), rs + "(" + bold("v") + " " + TIMES_S + " " + bold("w") + ")", 8, 10, THEORY, 12)
    at(S, vadd(q, cr), rs + bold("v") + " " + TIMES_S + " " + rs + bold("w"), -8, -2, TEXT, 12, "end")
    return figure(
        632, 380, [pl],
        "<strong>v</strong> = (0, 1, 2), <strong>w</strong> = (1, 0, 0) ve <strong>v</strong> &#215; "
        "<strong>w</strong> = (0, 2, &#8722;1) (solda) ile <em>yz</em> düzlemindeki yansımada görüntüleri "
        "(sağda). Aynaya paralel olan <strong>v</strong> ile <strong>v</strong> &#215; <strong>w</strong> "
        "değişmez, aynaya dik olan <strong>w</strong> ters döner. Bu yüzden "
        "<em>R</em><sub>*</sub><strong>v</strong> &#215; <em>R</em><sub>*</sub><strong>w</strong> (kesikli ok), "
        "<em>R</em><sub>*</sub>(<strong>v</strong> &#215; <strong>w</strong>) (mavi ok) ile zıt yönlüdür.",
        aria="Vectors v = (0, 1, 2), w = (1, 0, 0) and v x w at p, and their mirror images in the yz plane; the "
             "image of v x w and the cross product of the images point in opposite directions",
    )


OUT["yonlen-vektorel-ayna"] = fig_cross_mirror()


# ============================================================ yonlen-helis-ayna
# yonlen-helis-ayna: helix beta(t) = (2 cos t, 2 sin t, t/2) (a = 2, b = 1/2, right-handed) and its image
# under the mirror F(x, y, z) = (x, 8 - y, z) in the plane y = 4: (2 cos t, 8 - 2 sin t, t/2), left-handed.
# Frenet frames at t0: T = (-2 sin, 2 cos, 1/2)/c, N = (-cos, -sin, 0), B = (sin/2, -cos/2, 2)/c with
# c = sqrt(17)/2; image: Tbar = F*(T), Nbar = F*(N), Bbar = -F*(B) = (-sin/2, -cos/2, -2)/c.
def fig_helix_mirror():
    A_, B_ = 2.0, 0.5
    c = math.sqrt(A_ * A_ + B_ * B_)
    cam = Camera(azimuth=14.0, elevation=11.0)
    pl = space_panel(16, 16, 680, (-3.0, 10.6), (-4.3, 4.1))
    S = Space(pl, cam)

    def beta(t):
        return (A_ * math.cos(t), A_ * math.sin(t), B_ * t)

    def bbar(t):
        return (A_ * math.cos(t), 8.0 - A_ * math.sin(t), B_ * t)

    t1 = 2 * math.pi
    front1 = depth_curve(S, beta, -t1, t1, TEXT, 2.0, 400, 0.25, (0.0, 0.0, 0.0))
    front2 = depth_curve(S, bbar, -t1, t1, TEXT, 2.0, 400, 0.25, (0.0, 8.0, 0.0))
    # the mirror plane y = 4
    S.polygon([(-2.4, 4.0, -3.6), (2.4, 4.0, -3.6), (2.4, 4.0, 3.6), (-2.4, 4.0, 3.6)], TEXT, 0.06, TEXT, 0.8)
    # the two axes
    S.line([(0.0, 0.0, -3.7), (0.0, 0.0, 3.7)], TEXT, 0.9, "4 3", 0.45)
    S.line([(0.0, 8.0, -3.7), (0.0, 8.0, 3.7)], TEXT, 0.9, "4 3", 0.45)
    front1()
    front2()
    t0 = 1.0
    sn, cs = math.sin(t0), math.cos(t0)
    T = (-A_ * sn / c, A_ * cs / c, B_ / c)
    N = (-cs, -sn, 0.0)
    Bv = (B_ * sn / c, -B_ * cs / c, A_ / c)
    Tb, Nb = (T[0], -T[1], T[2]), (N[0], -N[1], N[2])
    Bb = vcross(Tb, Nb)
    assert max(abs(Bb[i] + (Bv[0], -Bv[1], Bv[2])[i]) for i in range(3)) < 1e-12
    L = 1.5
    P, Q = beta(t0), bbar(t0)
    for X0, E in ((P, (T, N, Bv)), (Q, (Tb, Nb, Bb))):
        S.arrow(X0, vadd(X0, vscale(L, E[0])), PRACTICE, 2.3, 9)
        S.arrow(X0, vadd(X0, vscale(L, E[1])), BASE, 2.3, 9)
        S.arrow(X0, vadd(X0, vscale(L, E[2])), THEORY, 2.3, 9)
        S.point(X0, TEXT, 3.2)
    at(S, vadd(P, vscale(L, T)), ital("T"), 7, 2, PRACTICE, 12)
    at(S, vadd(P, vscale(L, N)), ital("N"), -6, 12, BASE, 12, "end")
    at(S, vadd(P, vscale(L, Bv)), ital("B"), 7, 2, THEORY, 12)
    at(S, vadd(Q, vscale(L, Tb)), ital("T&#773;"), -7, 2, PRACTICE, 12, "end")
    at(S, vadd(Q, vscale(L, Nb)), ital("N&#773;"), 2, 15, BASE, 12)
    at(S, vadd(Q, vscale(L, Bb)), ital("B&#773;"), 7, 8, THEORY, 12)
    at(S, beta(-t1), ital("&#946;"), -8, 4, TEXT, 12.5, "end")
    at(S, bbar(-t1), ital("F") + "(" + ital("&#946;") + ")", 8, 4, TEXT, 12.5)
    at(S, (0.0, 4.0, -3.6), "ayna: " + ital("y") + " = 4", 0, 18, TEXT, 11.5, "middle")
    return figure(
        712, 460, [pl],
        "<em>a</em> = 2, <em>b</em> = 1/2 için sağ elli helis <em>&#946;</em> (solda) ve "
        "<em>y</em> = 4 düzlemindeki ayna görüntüsü <em>F</em>(<em>&#946;</em>) (sağda). Arkada "
        "kalan kısımlar soluk çizilmiştir. Karşılıklı noktalarda Frenet çatıları gösterilmiştir. Teğet ve "
        "asli normal aynaya göre simetriktir; binormal ise aynadaki karşılığının tersine döner: "
        "<em>B&#773;</em> = &#8722;<em>F</em><sub>*</sub>(<em>B</em>).",
        css_class=WIDE,
        aria="A right-handed circular helix about the z axis and its mirror image in the plane y = 4, a "
             "left-handed helix about the line x = 0, y = 8, with the Frenet frames at corresponding points",
    )


OUT["yonlen-helis-ayna"] = fig_helix_mirror()


# ============================================================ yonlen-eksen
# yonlen-eksen: a rotation about the axis spanned by e3. e1, e2 span the perpendicular plane;
# C(e1) = cos(th) e1 + sin(th) e2 and C(e2) = -sin(th) e1 + cos(th) e2 with th = 50 degrees drawn;
# C(e3) = e3. A point p at height 1.9 turns on a horizontal circle to C(p).
def fig_axis():
    cam = Camera(azimuth=30.0, elevation=20.0)
    pl = space_panel(16, 16, 690, (-2.0, 2.0), (-1.05, 2.45))
    S = Space(pl, cam)
    th = math.radians(50)
    O = (0.0, 0.0, 0.0)
    e1, e2, e3 = (1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)
    R = 1.2
    S.line([(0.0, 0.0, -0.5), (0.0, 0.0, 2.15)], TEXT, 1.0, "6 4", 0.55)
    S.circle(O, e1, e2, R, TEXT, 1.0, "4 3", 120, 0.5)
    Ce1 = (math.cos(th), math.sin(th), 0.0)
    Ce2 = (-math.sin(th), math.cos(th), 0.0)
    # a point and its image on a horizontal circle
    h, rp, phi = 1.65, 0.95, math.radians(55)
    H = (0.0, 0.0, h)
    u1 = (math.cos(phi), math.sin(phi), 0.0)
    u2 = (-math.sin(phi), math.cos(phi), 0.0)
    P = vadd(H, vscale(rp, u1))
    CP = vadd(H, vadd(vscale(rp * math.cos(th), u1), vscale(rp * math.sin(th), u2)))
    S.circle(H, e1, e2, rp, TEXT, 0.9, "3 3", 100, 0.45)
    arc3(S, H, u1, u2, rp, 0.05, th - 0.04, TEXT, 1.4, 7, 0.8)
    S.guide([H, P], TEXT, 0.5, 1.0, "2 3")
    S.guide([H, CP], TEXT, 0.5, 1.0, "2 3")
    S.point(P, TEXT, 3.2)
    S.point(CP, TEXT, 3.2)
    at(S, P, bold("p"), 2, 17, TEXT, 12, "middle")
    at(S, CP, ital("C") + "(" + bold("p") + ")", 9, 5, TEXT, 12)
    # frame and images
    S.arrow(O, vscale(R, e1), PRACTICE, 2.2, 9, None, 0.5)
    S.arrow(O, vscale(R, e2), BASE, 2.2, 9, None, 0.5)
    S.arrow(O, vscale(R, Ce1), PRACTICE, 2.6, 10)
    S.arrow(O, vscale(R, Ce2), BASE, 2.6, 10)
    S.arrow(O, vscale(R, e3), THEORY, 2.6, 10)
    arc3(S, O, e1, e2, 0.55, 0.06, th - 0.05, TEXT, 1.2, 6, 0.8)
    arc3(S, O, e2, vscale(-1.0, e1), 0.55, 0.06, th - 0.05, TEXT, 1.2, 6, 0.8)
    S.point(O, TEXT, 3.0)
    at(S, vscale(R, e1), name("e", 1), -6, 14, PRACTICE, 12, "end")
    at(S, vscale(R, e2), name("e", 2), 8, 12, BASE, 12)
    at(S, vscale(R, Ce1), ital("C") + "(" + name("e", 1) + ")", 4, 17, PRACTICE, 12, "middle")
    at(S, vscale(R, Ce2), ital("C") + "(" + name("e", 2) + ")", 7, -6, BASE, 12)
    at(S, vscale(R, e3), name("e", 3) + " = " + ital("C") + "(" + name("e", 3) + ")", -9, 4, THEORY, 12, "end")
    a1 = vadd(vscale(0.72 * math.cos(th / 2), e1), vscale(0.72 * math.sin(th / 2), e2))
    a2 = vadd(vscale(0.72 * math.cos(th / 2), e2), vscale(-0.72 * math.sin(th / 2), e1))
    at(S, a1, ital(VTH_S), 12, 13, TEXT, 12, "start")
    at(S, a2, ital(VTH_S), 2, -5, TEXT, 12, "middle")
    return figure(
        722, 510, [pl],
        "Bir dönmenin ekseni ve açısı. <em>e</em><sub>3</sub> eksen üzerindedir ve yerinde kalır; "
        "<em>e</em><sub>1</sub> ile <em>e</em><sub>2</sub> eksene dik düzlemde aynı <em>&#977;</em> açısı "
        "kadar döner (resimde <em>&#977;</em> = 50°). Her <strong>p</strong> noktası eksene dik bir "
        "çember üzerinde aynı açıyla <em>C</em>(<strong>p</strong>)&#8217;ye taşınır.",
        aria="Rotation about the axis spanned by e3: e1 and e2 turn through the same angle in the perpendicular "
             "plane, e3 stays fixed, and a point p moves on a horizontal circle to C(p)",
    )


OUT["yonlen-eksen"] = fig_axis()


# ============================================================ yonlen-dik-donme
# yonlen-dik-donme: C(p) = a x p + (p . a) a for a unit vector a (drawn vertical). p = (1.4, 0, 1.0) splits into
# (p . a) a = (0, 0, 1.0) and the perpendicular part q = (1.4, 0, 0); C(p) = (0, 1.4, 1.0): the perpendicular part
# turns by a right angle about a (a x p = a x q).
def fig_quarter_turn():
    cam = Camera(azimuth=32.0, elevation=20.0)
    pl = space_panel(16, 16, 560, (-1.6, 2.2), (-0.7, 2.25))
    S = Space(pl, cam)
    O = (0.0, 0.0, 0.0)
    h, r = 1.0, 1.4
    H = (0.0, 0.0, h)
    P = (r, 0.0, h)
    CP = (0.0, r, h)
    S.line([(0.0, 0.0, -0.5), (0.0, 0.0, 2.1)], TEXT, 1.0, "6 4", 0.5)
    S.circle(H, (1.0, 0.0, 0.0), (0.0, 1.0, 0.0), r, TEXT, 0.9, "3 3", 100, 0.45)
    arc3(S, H, (1.0, 0.0, 0.0), (0.0, 1.0, 0.0), r, 0.06, math.pi / 2 - 0.05, TEXT, 1.4, 7, 0.8)
    S.arrow(O, H, THEORY, 2.4, 9)
    S.arrow(H, P, PRACTICE, 2.4, 9)
    S.arrow(H, CP, BASE, 2.4, 9)
    # right-angle mark at H between the two horizontal arms
    m = 0.16
    S.line([(m, 0.0, h), (m, m, h), (0.0, m, h)], TEXT, 1.0, None, 0.6)
    S.point(O, TEXT, 3.0)
    S.point(P, TEXT, 3.2)
    S.point(CP, TEXT, 3.2)
    at(S, (0.0, 0.0, 2.1), "eksen: " + bold("a"), 6, -4, TEXT, 12, "start")
    at(S, vscale(0.3, H), "(" + bold("p") + " &#183; " + bold("a") + ")" + bold("a"), -8, 4, THEORY, 12, "end")
    at(S, P, bold("p"), -2, 18, TEXT, 12, "middle")
    at(S, CP, ital("C") + "(" + bold("p") + ")", 9, 5, TEXT, 12)
    at(S, vscale(0.5, vadd(H, P)), bold("q"), -8, -4, PRACTICE, 12, "end")
    at(S, vscale(0.5, vadd(H, CP)), bold("a") + " &#215; " + bold("q"), 4, -7, BASE, 12, "start")
    return figure(
        592, 430, [pl],
        "<em>C</em>(<strong>p</strong>) = <strong>a</strong> &#215; <strong>p</strong> + "
        "(<strong>p</strong> &#183; <strong>a</strong>)<strong>a</strong> dönüşümü. <strong>p</strong>, "
        "<strong>a</strong> doğrultusundaki (<strong>p</strong> &#183; <strong>a</strong>)<strong>a</strong> "
        "parçasına ve ona dik <strong>q</strong> parçasına ayrılır. Birinci parça yerinde kalır, "
        "<strong>q</strong> ise <strong>a</strong> &#215; <strong>q</strong>&#8217;ya, yani eksen etrafında "
        "dik açı kadar döndürülmüş hâline gider.",
        aria="The map C(p) = a x p + (p . a) a: the component of p along the unit vector a stays, the "
             "perpendicular component q turns by a right angle about a to a x q",
    )


OUT["yonlen-dik-donme"] = fig_quarter_turn()


# ---------------------------------------------------------------------------
for key, content in OUT.items():
    with io.open(OUT_DIR / f"diffgeo-{key}.md", "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
print("generated:", len(OUT), "figures")
