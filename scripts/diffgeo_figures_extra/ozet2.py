# -*- coding: utf-8 -*-
"""
Figures of the chapter "Çatı Alanlarının Özeti"
(dersler/diferansiyel-geometri/1/cati-alanlari-ozeti.qmd), key `ozet2`.

The figures are NOT produced at build time. Run

    python scripts/diffgeo_figures_extra/ozet2.py
    python scripts/center_figures.py "diffgeo-ozet2-*.md" --keep-width

and paste the markup from scripts/_figures/diffgeo-ozet2-<name>.md into the
.qmd file. Figures go INSIDE the box they explain (theorem, proof, example,
solution or exercise), never inside a definition box.

Colours follow the book's frame convention: first frame field -> PRACTICE,
second -> BASE, third -> THEORY. Captions are Turkish (they are shown on the
site); aria labels are ASCII.
"""
import io
import math
import sys
from fractions import Fraction as Fr
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import *  # noqa: E402,F403 -- Plot, figure, colours, WIDE, cplane, dot, ...

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
OUT = {}

MINUS_S = "&#8722;"
TH_S, OMEGA_S, KAPPA_S, TAU_S = "&#977;", "&#969;", "&#954;", "&#964;"


def subs(s, size=9):
    return f'<tspan font-size="{size}" dy="4">{s}</tspan><tspan dy="-4">&#8203;</tspan>'


def ital(s):
    return f'<tspan font-style="italic">{s}</tspan>'


def name(letter, k):
    return ital(letter) + subs(str(k))


def frac_s(q):
    """Fraction -> SVG text with a proper minus sign."""
    if q == 0:
        return "0"
    s = str(abs(q.numerator)) if q.denominator == 1 else f"{abs(q.numerator)}/{q.denominator}"
    return (MINUS_S if q < 0 else "") + s


def box(panel, x0, y0, x1, y1, color, fill_opacity=0.07, width=1.3):
    panel.add(f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{x1 - x0:.1f}" height="{y1 - y0:.1f}" rx="7" '
              f'fill="{color}" fill-opacity="{fill_opacity}" stroke="{color}" stroke-width="{width}"/>')


def matrix(panel, cx, cy, entries, cw=38, rh=19, color=TEXT, size=11.5):
    """3x3 matrix of strings centred at (cx, cy) in pixel coordinates, with square brackets."""
    top, bottom = cy - 1.5 * rh - 3, cy + 1.5 * rh - 1
    xl, xr = cx - 1.5 * cw - 2, cx + 1.5 * cw + 2
    for x, s in ((xl, 1), (xr, -1)):
        panel.add(f'<polyline points="{x + 5 * s:.1f},{top:.1f} {x:.1f},{top:.1f} {x:.1f},{bottom:.1f} '
                  f'{x + 5 * s:.1f},{bottom:.1f}" fill="none" stroke="{TEXT}" stroke-width="1.1"/>')
    for i in range(3):
        for j in range(3):
            panel.text_px(cx + (j - 1) * cw, cy + (i - 1) * rh + 4, entries[i][j], color, size, "middle")


# ============================================================ ozet2-form-matrisi
# ozet2-form-matrisi: helix frame H1 = (4/5)E2 + (3/5)E3, H2 = -E1, H3 = -(3/5)E2 + (4/5)E3 built
# from the cylindrical frame; its connection matrix is omega = dtheta * M with
# M = [[0, 4/5, 0], [-4/5, 0, 3/5], [0, -3/5, 0]]. At p = (4, 0, 0) on the helix
# (4 cos(s/5), 4 sin(s/5), 3s/5) the tangent is T = (0, 4/5, 3/5) = (4/5)E2 + (3/5)E3, and
# dtheta(T) = 1/5, dtheta(E2) = 1/r = 1/4, dtheta(E1) = dtheta(E3) = 0 (asserted below).
def fig_form_matrix():
    M = [[Fr(0), Fr(4, 5), Fr(0)], [Fr(-4, 5), Fr(0), Fr(3, 5)], [Fr(0), Fr(-3, 5), Fr(0)]]
    p = (4.0, 0.0, 0.0)
    r2 = p[0] ** 2 + p[1] ** 2

    def dtheta(v):
        return (-p[1] * v[0] + p[0] * v[1]) / r2

    T = (0.0, 0.8, 0.6)
    E1, E2, E3 = (1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)
    assert abs(dtheta(T) - 0.2) < 1e-12 and abs(dtheta(E2) - 0.25) < 1e-12
    assert dtheta(E1) == 0 and dtheta(E3) == 0
    kT, kE2 = Fr(1, 5), Fr(1, 4)
    MT = [[kT * m for m in row] for row in M]
    ME2 = [[kE2 * m for m in row] for row in M]
    assert MT[0][1] == Fr(4, 25) and MT[1][2] == Fr(3, 25)          # kappa = a/c^2, tau = b/c^2
    assert ME2[0][1] == Fr(1, 5) and ME2[1][2] == Fr(3, 20)
    assert all(MT[i][j] == Fr(4, 5) * ME2[i][j] for i in range(3) for j in range(3))  # T = (4/5)E2 + (3/5)E3

    W, H = 640, 330
    P = Plot(0, 0, W, H, (0, W), (H, 0))
    to_s = lambda A: [[frac_s(q) for q in row] for row in A]

    # top: the matrix of 1-forms
    box(P, 175, 12, 465, 118, THEORY)
    P.text_px(320, 32, "bağlantı formlarının matrisi", THEORY, 11.5, "middle", True)
    P.text_px(250, 79, ital(OMEGA_S) + " = " + ital("d" + TH_S) + " &#183;", TEXT, 13, "end")
    matrix(P, 330, 75, to_s(M), cw=40)

    # bottom: the three evaluations
    cols = [(110, PRACTICE, 0.10, 2.0), (320, BASE, 0.07, 1.3), (530, TEXT, 0.035, 1.1)]
    heads = [ital("T") + " yönünde (helis boyunca)",
             "silindirik " + name("E", 2) + " yönünde",
             name("E", 1) + " ya da " + name("E", 3) + " yönünde"]
    for (cx, col, fo, wd), head in zip(cols, heads):
        box(P, cx - 100, 196, cx + 100, 318, col, fo, wd)
        P.text_px(cx, 215, head, col if col != TEXT else TEXT, 11, "middle", True)
    matrix(P, 110, 256, to_s(MT), cw=40)
    matrix(P, 320, 256, to_s(ME2), cw=40)
    P.text_px(530, 262, "sıfır matrisi", TEXT, 12, "middle")
    P.text_px(110, 306, ital(KAPPA_S) + " = 4/25,&#160;&#160;" + ital(TAU_S) + " = 3/25", PRACTICE, 11.5,
              "middle", True)
    P.text_px(320, 306, "çatı daha hızlı döner", BASE, 11, "middle")
    P.text_px(530, 306, "çatı hiç dönmez", TEXT, 11, "middle")

    # arrows with the values of dtheta
    for (x0, y0), (x1, y1), txt, anchor, dx in (
            ((250, 120), (130, 192), ital("d" + TH_S) + "(" + ital("T") + ") = 1/5", "end", -8),
            ((320, 120), (320, 192), ital("d" + TH_S) + "(" + name("E", 2) + ") = 1/4", "start", 8),
            ((390, 120), (510, 192), ital("d" + TH_S) + " = 0", "start", 10)):
        P.arrow((x0, y0), (x1, y1), TEXT, 1.4, 8, None, 0.7)
        P.text_px((x0 + x1) / 2 + dx, (y0 + y1) / 2 + 4, txt, TEXT, 11, anchor)

    return figure(
        W, H, [P],
        "Helise uyarlanmış <em>H</em><sub>1</sub>, <em>H</em><sub>2</sub>, <em>H</em><sub>3</sub> çatı "
        "alanının bağlantı formları tek bir matriste toplanır: <em>&#969;</em> = <em>d&#977;</em> çarpı sabit "
        "bir ters simetrik matris (üstte). Bir 1-form matrisi her teğet vektöre bir sayı matrisi verir. "
        "<strong>p</strong> = (4, 0, 0) noktasında helisin birim teğeti <em>T</em>&#8217;ye uygulanınca "
        "Frenet formüllerinin katsayı matrisi çıkar ve <em>&#954;</em> = 4/25, <em>&#964;</em> = 3/25 okunur "
        "(solda). Eksen etrafında yatay ilerleyişte çatı daha hızlı döner (ortada); dışa ya da yukarı "
        "ilerleyişte hiç dönmez (sağda). <em>T</em> = (4/5)<em>E</em><sub>2</sub> + (3/5)<em>E</em><sub>3</sub> "
        "olduğundan soldaki matris, ortadakinin 4/5 katıdır.",
        css_class=WIDE,
        aria="Diagram: on top the connection matrix omega = dtheta times the skew matrix with entries 4/5 and "
             "3/5. Three arrows lead down: applied to the helix tangent T it gives the Frenet matrix with "
             "kappa 4/25 and tau 3/25; applied to the cylindrical E2 it gives entries 1/5 and 3/20; applied "
             "to E1 or E3 it gives the zero matrix",
    )


OUT["ozet2-form-matrisi"] = fig_form_matrix()


# ============================================================ ozet2-duzlem-cemberler
# ozet2-duzlem-cemberler: plane frame field F1 = -sin(theta) U1 + cos(theta) U2,
# F2 = -cos(theta) U1 - sin(theta) U2 (angle psi = theta + pi/2) sampled on the circles r = 1, 2, 3
# at the same three polar angles. Along each counterclockwise circle F1 = T and F2 = N (T turned by
# +90 degrees), and omega12(T) = dtheta(T) = 1/r is the plane curvature (asserted below).
def fig_plane_circles():
    radii = (1.0, 2.0, 3.0)
    angles = [math.radians(a) for a in (25, 145, 265)]
    L = 0.5

    for rr in radii:
        for a in angles:
            x, y = rr * math.cos(a), rr * math.sin(a)
            T = (-math.sin(a), math.cos(a))                  # unit tangent of the ccw circle
            N = (-T[1], T[0])                                # T turned by +90 degrees
            F1 = (math.cos(a + math.pi / 2), math.sin(a + math.pi / 2))
            F2 = (-math.sin(a + math.pi / 2), math.cos(a + math.pi / 2))
            assert max(abs(F1[0] - T[0]), abs(F1[1] - T[1]), abs(F2[0] - N[0]), abs(F2[1] - N[1])) < 1e-12
            dth_T = (-y * T[0] + x * T[1]) / (x * x + y * y)
            assert abs(dth_T - 1 / rr) < 1e-12

    pl = cplane(20, 12, 400, (-3.9, 3.9), (-3.75, 3.9))
    pl.arrow((-3.7, 0.0), (3.75, 0.0), TEXT, 1.0, 6, None, 0.45)
    pl.arrow((0.0, -3.6), (0.0, 3.75), TEXT, 1.0, 6, None, 0.45)
    pl.label(3.75, 0.0, "x", -2, 16, TEXT, 11.5, "middle", False, True)
    pl.label(0.0, 3.75, "y", 9, 4, TEXT, 11.5, "start", False, True)

    for rr in radii:
        pl.line(circle_pts(0.0, 0.0, rr), THEORY, 1.5, None, 0.75)
        # orientation arrowhead near the polar angle 80 degrees
        a0, a1 = math.radians(78), math.radians(84)
        pl.arrow((rr * math.cos(a0), rr * math.sin(a0)), (rr * math.cos(a1), rr * math.sin(a1)),
                 THEORY, 1.5, 7, None, 0.9)

    # rays through the sample points
    for a in angles:
        pl.line([(0.3 * math.cos(a), 0.3 * math.sin(a)), (3.55 * math.cos(a), 3.55 * math.sin(a))],
                TEXT, 0.9, "3 4", 0.45)

    for rr in radii:
        for a in angles:
            x, y = rr * math.cos(a), rr * math.sin(a)
            T = (-math.sin(a), math.cos(a))
            N = (-T[1], T[0])
            pl.arrow((x, y), (x + L * T[0], y + L * T[1]), PRACTICE, 2.0, 7)
            pl.arrow((x, y), (x + L * N[0], y + L * N[1]), BASE, 2.0, 7)
            dot(pl, (x, y), TEXT, 2.6)

    hollow(pl, (0.0, 0.0), TEXT, 3.4)

    # frame labels at the outer point on the 265 degree ray (open region at the bottom)
    a = angles[2]
    x, y = 3.0 * math.cos(a), 3.0 * math.sin(a)
    T = (-math.sin(a), math.cos(a))
    N = (-T[1], T[0])
    pl.label(x + L * T[0], y + L * T[1], name("F", 1) + " = " + ital("T"), 7, 5, PRACTICE, 11.5, "start")
    pl.label(x + L * N[0], y + L * N[1], name("F", 2) + " = " + ital("N"), -7, 8, BASE, 11.5, "end")

    # curvature labels on the circles, near the polar angle 200 degrees (empty region)
    kt = ital(KAPPA_S + "&#771;")
    for rr, s in zip(radii, ("1", "1/2", "1/3")):
        a = math.radians(205)
        pl.label(rr * math.cos(a), rr * math.sin(a), kt + " = " + s, -6, 16, THEORY, 11, "end")

    return figure(
        440, 425, [pl],
        "Düzlemde <em>F</em><sub>1</sub> = &#8722;sin <em>&#977;</em> <em>U</em><sub>1</sub> + cos <em>&#977;</em> "
        "<em>U</em><sub>2</sub> (turuncu), <em>F</em><sub>2</sub> = &#8722;cos <em>&#977;</em> <em>U</em><sub>1</sub> "
        "&#8722; sin <em>&#977;</em> <em>U</em><sub>2</sub> (yeşil) çatı alanı; oklar yarıçapı 1, 2 ve 3 olan "
        "çemberler üzerinde aynı üç kutupsal açıda çizilmiştir. Merkezi orijin olan, saatin tersi yönünde "
        "dolaşılan her çember boyunca <em>F</em><sub>1</sub> birim teğet <em>T</em>, <em>F</em><sub>2</sub> "
        "birim normal <em>N</em>&#8217;dir. Aynı ışın üzerindeki çatılar aynıdır; yarıçap yalnızca bir tur "
        "boyunca katedilen yolu, dolayısıyla <em>d&#977;</em>(<em>T</em>) = 1/<em>r</em> düzlem eğriliğini "
        "belirler. Çatı alanı orijinde tanımlı değildir.",
        aria="Plane frame field F1, F2 drawn at three polar angles on the concentric circles of radius 1, 2 "
             "and 3 around the origin; along each counterclockwise circle F1 is the unit tangent and F2 the "
             "unit normal; frames on the same ray agree; plane curvatures 1, 1/2 and 1/3 are marked",
    )


OUT["ozet2-duzlem-cemberler"] = fig_plane_circles()


# ---------------------------------------------------------------------------
for key, content in OUT.items():
    with io.open(OUT_DIR / f"diffgeo-{key}.md", "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
print("generated:", len(OUT), "figures")
