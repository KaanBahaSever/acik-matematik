# -*- coding: utf-8 -*-
"""
Generates the SVG figures used in the "Kompleks Analiz" (Complex Analysis)
chapters.

The figures are NOT produced at build time: run this script, then
scripts/center_figures.py (which measures each drawing and centers it in its
viewBox), and paste the resulting markup into the .qmd files — always OUTSIDE
definition/theorem boxes. Building the books therefore needs neither Python
nor Jupyter; CI runs Quarto alone.

The captions are Turkish on purpose — they are the text shown on the site.

Usage:   python scripts/complex_figures.py && python scripts/center_figures.py
Output:  scripts/_figures/complex-<name>.md
"""
import io
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8")
from svg_plot import *  # noqa: E402,F403 — Plot, figure, colors, cplane, polar, angle_arc, ...

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_figures")
os.makedirs(OUT_DIR, exist_ok=True)
OUT = {}

# ############################################################################
# PART: Kompleks Sayılar
# ############################################################################

# ============================================================ vektörler-ve-modül
# ---- V1: parallelogram rule for sum and difference
z1, z2 = (3.0, 1.0), (1.0, 2.0)
s = (z1[0] + z2[0], z1[1] + z2[1])
d = (z1[0] - z2[0], z1[1] - z2[1])

p1 = cplane(28, 30, 236, (-0.9, 4.6), (-1.6, 3.7))
p1.origin_axes()
p1.polygon([(0, 0), z1, s, z2], THEORY, 0.10)
p1.line([z1, s], THEORY, 1.3, "5 4", 0.6)
p1.line([z2, s], THEORY, 1.3, "5 4", 0.6)
p1.arrow((0, 0), z1, THEORY, 2.0)
p1.arrow((0, 0), z2, BASE, 2.0)
p1.arrow((0, 0), s, PRACTICE, 2.2)
p1.label(*z1, "z" + SUB1, 8, 12, THEORY, 12.5, "start", True, True)
p1.label(*z2, "z" + SUB2, -8, -6, BASE, 12.5, "end", True, True)
p1.label(*s, "z" + SUB1 + " + z" + SUB2, 6, -6, PRACTICE, 12.5, "start", True, True)
p1.text_px(28 + 118, 22, "toplam: paralelkenar kural&#305;", TEXT, 11.5, "middle", True)

p2 = cplane(300, 30, 236, (-0.9, 4.6), (-1.6, 3.7))
p2.origin_axes()
p2.arrow((0, 0), z1, THEORY, 2.0)
p2.arrow((0, 0), z2, BASE, 2.0)
p2.arrow(z2, z1, PRACTICE, 2.2)
p2.arrow((0, 0), d, PRACTICE, 1.6, dash="5 4", opacity=0.75)
p2.label(*z1, "z" + SUB1, 8, 12, THEORY, 12.5, "start", True, True)
p2.label(*z2, "z" + SUB2, -8, -6, BASE, 12.5, "end", True, True)
p2.label((z1[0] + z2[0]) / 2, (z1[1] + z2[1]) / 2, "z" + SUB1 + " " + MINUS + " z" + SUB2, 6, -8, PRACTICE, 12.5, "start", True, True)
p2.label(*d, "z" + SUB1 + " " + MINUS + " z" + SUB2, 6, 14, PRACTICE, 11, "start", False, True)
p2.text_px(300 + 118, 22, "fark: z" + SUB2 + "'den z" + SUB1 + "'e giden vekt&#246;r", TEXT, 11.5, "middle", True)
OUT["vektor-toplam-fark"] = figure(
    564, 268, [p1, p2],
    "Solda <em>z</em><sub>1</sub> + <em>z</em><sub>2</sub> toplam&#305; paralelkenar&#305;n k&#246;&#351;egenidir. "
    "Sa&#287;da <em>z</em><sub>1</sub> &#8722; <em>z</em><sub>2</sub> fark&#305;, <em>z</em><sub>2</sub> ucundan "
    "<em>z</em><sub>1</sub> ucuna giden vekt&#246;rd&#252;r; ba&#351;lang&#305;ca ta&#351;&#305;nm&#305;&#351; kopyas&#305; kesikli &#231;izilmi&#351;tir. "
    "Bu y&#252;zden |<em>z</em><sub>1</sub> &#8722; <em>z</em><sub>2</sub>| iki nokta aras&#305;ndaki uzakl&#305;kt&#305;r.",
    css_class=WIDE, aria="Kompleks sayilarin toplami ve farki icin vektor cizimi")

# ---- V2a: modulus = the length of the vector (right triangle)
z = (3.0, 2.0)
p = cplane(40, 24, 320, (-0.7, 4.3), (-0.6, 2.7))
p.origin_axes()
p.polygon([(0, 0), (z[0], 0), z], THEORY, 0.10)
p.line([(0, 0), (z[0], 0)], PRACTICE, 1.4, "5 4", 0.85)
p.line([(z[0], 0), z], PRACTICE, 1.4, "5 4", 0.85)
s = 0.16   # right-angle mark at (3, 0)
p.line([(z[0] - s, 0), (z[0] - s, s), (z[0], s)], PRACTICE, 1.1, None, 0.8)
p.arrow((0, 0), z, THEORY, 2.3)
dot(p, z, THEORY, 4.2)
p.label(*z, "z = 3 + 2i", 9, -4, THEORY, 12.5, "start", True)
p.label(1.5, 0, "x = 3", 0, 17, PRACTICE, 11.5, "middle", False, True)
p.label(z[0], 1.0, "y = 2", 9, 4, PRACTICE, 11.5, "start", False, True)
p.label(1.35, 1.05, "|z| = &#8730;13 " + APPROX + " 3,61", -7, -7, THEORY, 12, "end", True, True)
OUT["modul-uzunluk"] = figure(
    400, 260, [p],
    "Mod&#252;l, <em>z</em> vekt&#246;r&#252;n&#252;n boyudur: bile&#351;enleri <em>x</em> ve <em>y</em> olan dik &#252;&#231;genin "
    "hipoten&#252;s&#252;. Pisagor teoremi tan&#305;mdaki form&#252;l&#252; verir: |<em>z</em>| = &#8730;(<em>x</em>&#178; + <em>y</em>&#178;), "
    "&#246;rnekte |3 + 2<em>i</em>| = &#8730;(9 + 4) = &#8730;13.",
    aria="Modul: z vektorunun boyu, dik ucgenin hipotenusu")

# ---- V2b: conjugate as a reflection across the real axis
p = cplane(40, 24, 300, (-0.9, 4.4), (-2.9, 2.9))
p.origin_axes(yticks=(-2, -1, 1, 2))
p.arrow((0, 0), z, THEORY, 2.2)
p.arrow((0, 0), (z[0], -z[1]), PRACTICE, 2.0)
p.line([z, (z[0], -z[1])], REMARK, 1.2, "3 3", 0.75)
dot(p, z, THEORY)
dot(p, (z[0], -z[1]), PRACTICE)
dot(p, (z[0], 0), REMARK, 2.6)
p.label(*z, "z = 3 + 2i", 9, 4, THEORY, 12.5, "start", True)
p.label(z[0], -z[1], BAR_Z + " = 3 " + MINUS + " 2i", 9, 5, PRACTICE, 12.5, "start", True)
p.label(1.5, 1.0, "|z| = &#8730;13", -6, -8, THEORY, 12, "end", False, True)
p.label(1.5, -1.0, "|" + BAR_Z + "| = &#8730;13", -6, 14, PRACTICE, 12, "end", False, True)
OUT["modul-eslenik"] = figure(
    380, 372, [p],
    "E&#351;lenik <em>z&#773;</em>, <em>z</em>'nin reel eksene g&#246;re yans&#305;mas&#305;d&#305;r: reel k&#305;s&#305;m ayn&#305; "
    "kal&#305;r, sanal k&#305;sm&#305;n i&#351;areti de&#287;i&#351;ir. Yans&#305;ma boyu de&#287;i&#351;tirmedi&#287;inden "
    "|<em>z&#773;</em>| = |<em>z</em>| olur.",
    aria="Eslenik: reel eksene gore yansima, modul degismez")

# ---- V3: |z - z0| = R is a circle
z0, R = (1.0, -3.0), 2.0
p = cplane(40, 24, 300, (-1.9, 3.9), (-5.7, 0.7))
p.origin_axes(xticks=(-1, 1, 2, 3), yticks=(-5, -4, -3, -2, -1))
p.circle(*z0, R, THEORY, 2.0)
zc = (z0[0] + R * math.cos(0.7), z0[1] + R * math.sin(0.7))
p.line([z0, zc], PRACTICE, 1.6, "5 4")
p.line([(0, 0), z0], REMARK, 1.2, "3 3", 0.7)
dot(p, z0, THEORY, 4)
dot(p, zc, PRACTICE, 3.6)
p.label(*z0, "z" + SUB0 + " = 1 " + MINUS + " 3i", 8, 14, THEORY, 12, "start", True)
p.label((z0[0] + zc[0]) / 2, (z0[1] + zc[1]) / 2, "|z " + MINUS + " z" + SUB0 + "| = 2", 8, 10, PRACTICE, 11.5, "start", False, True)
p.label(*zc, "z", 8, -2, PRACTICE, 12.5, "start", True, True)
OUT["cember"] = figure(
    380, 356, [p],
    "|<em>z</em> &#8722; <em>z</em><sub>0</sub>| = <em>R</em> denklemi, <em>z</em><sub>0</sub>'a uzakl&#305;&#287;&#305; tam "
    "<em>R</em> olan noktalar&#305;n k&#252;mesidir: merkezi <em>z</em><sub>0</sub>, yar&#305;&#231;ap&#305; <em>R</em> olan &#231;ember. "
    "&#214;rnekteki |<em>z</em> &#8722; 1 + 3<em>i</em>| = 2 i&#231;in merkez 1 &#8722; 3<em>i</em>'dir; i&#351;aretlere dikkat.",
    aria="Merkezi 1-3i, yaricapi 2 olan cember")

# ================================================================= üstel-form
# ---- U1: polar form  z = r(cos θ + i sin θ)
r, th = 2.5, math.atan2(1.5, 2.0)
z = polar(r, th)
p = cplane(40, 24, 320, (-0.7, 3.3), (-0.6, 2.4))
p.origin_axes()
p.sector(0, 0, 0.75, 0, th, THEORY, 0.18)
p.arc(0, 0, 0.75, 0, th, THEORY, 1.4)
p.line([(z[0], 0), z], PRACTICE, 1.3, "5 4", 0.8)
p.line([(0, z[1]), z], PRACTICE, 1.3, "5 4", 0.8)
p.arrow((0, 0), z, THEORY, 2.3)
dot(p, z, THEORY)
p.label(*z, "z = r(cos " + THETA + " + i sin " + THETA + ")", 0, -12, THEORY, 12, "middle", True)
p.label(z[0] / 2, z[1] / 2, "r = |z|", -6, -8, THEORY, 12.5, "end", True, True)
p.label(0.85, 0.32, THETA, 0, 0, THEORY, 13, "start", True, True)
p.label(z[0], 0, "x = r cos " + THETA, 0, 16, PRACTICE, 11.5, "middle", False, True)
p.label(0, z[1], "y = r sin " + THETA, -8, 4, PRACTICE, 11.5, "end", False, True)
OUT["kutupsal-form"] = figure(
    400, 292, [p],
    "Kutupsal g&#246;sterimin iki verisi: <em>r</em>, vekt&#246;r&#252;n boyu (mod&#252;l); <em>&#952;</em>, pozitif reel "
    "eksenden vekt&#246;re saat y&#246;n&#252;n&#252;n tersine &#246;l&#231;&#252;len a&#231;&#305; (arg&#252;man). Bile&#351;enler "
    "<em>x</em> = <em>r</em> cos <em>&#952;</em>, <em>y</em> = <em>r</em> sin <em>&#952;</em> ile geri gelir.",
    aria="Kutupsal form: modul r ve arguman theta")

# ---- U2: arg z is a set — one point, many angles
z = (-1.0, -1.0)
A = -3 * PI / 4
p = cplane(24, 24, 300, (-2.0, 2.0), (-2.0, 2.0))
p.origin_axes()
p.line([(0, 0), polar(1.9, A)], REMARK, 1.1, "3 3", 0.6)
angle_arc(p, 0, A, 0.5, PRACTICE, 2.2)
spiral(p, 0, A + 2 * PI, 0.7, 0.9, THEORY, 1.7)
spiral(p, 0, A - 2 * PI, 1.05, 1.5, BASE, 1.7)
p.arrow((0, 0), z, TEXT, 2.0)
dot(p, z, TEXT, 4)
p.label(*z, "z = " + MINUS + "1 " + MINUS + " i", -4, 20, TEXT, 12.5, "end", True)
for rad, col in ((0.5, PRACTICE), (0.7, THEORY), (1.05, BASE)):
    dot(p, (rad, 0), col, 2.6)
# legend, outside the plot on the right
lx, ly = 340, 24 + 60
p.text_px(lx, ly, "ba&#351;lang&#305;&#231;: pozitif reel eksen", TEXT, 11, "start", False, True)
p.text_px(lx, ly + 28, "Arg z = " + MINUS + "3" + PI_S + "/4", PRACTICE, 12, "start", True)
p.text_px(lx, ly + 44, "(saat y&#246;n&#252;nde, 135&#176;)", PRACTICE, 10.5, "start", False, True)
p.text_px(lx, ly + 72, MINUS + "3" + PI_S + "/4 + 2" + PI_S + " = 5" + PI_S + "/4", THEORY, 12, "start", True)
p.text_px(lx, ly + 88, "(tersine, 225&#176;)", THEORY, 10.5, "start", False, True)
p.text_px(lx, ly + 116, MINUS + "3" + PI_S + "/4 " + MINUS + " 2" + PI_S + " = " + MINUS + "11" + PI_S + "/4", BASE, 12, "start", True)
p.text_px(lx, ly + 132, "(saat y&#246;n&#252;nde, 495&#176;)", BASE, 10.5, "start", False, True)
p.text_px(lx, ly + 164, "hepsi arg z k&#252;mesinin", TEXT, 11.5, "start", True)
p.text_px(lx, ly + 180, "eleman&#305;d&#305;r; Arg z tek", TEXT, 11.5, "start", True)
p.text_px(lx, ly + 196, "temsilcidir.", TEXT, 11.5, "start", True)
OUT["arg-kumesi"] = figure(
    540, 348, [p],
    "Ayn&#305; <em>z</em> noktas&#305;na pozitif reel eksenden ba&#351;layarak sonsuz &#231;oklukta a&#231;&#305;yla "
    "var&#305;l&#305;r: saat y&#246;n&#252;nde &#8722;3&#960;/4, saat y&#246;n&#252;n&#252;n tersine tam bir tur fazlas&#305;yla 5&#960;/4, "
    "ya da saat y&#246;n&#252;nde bir tur fazlas&#305;yla &#8722;11&#960;/4. K&#252;&#231;&#252;k harfli arg <em>z</em> bu a&#231;&#305;lar&#305;n "
    "<strong>t&#252;m&#252;n&#252;n k&#252;mesidir</strong>; b&#252;y&#252;k harfli Arg <em>z</em> i&#231;lerinden (&#8722;&#960;, &#960;] "
    "aral&#305;&#287;&#305;na d&#252;&#351;en tek de&#287;eri se&#231;er.",
    aria="Bir noktanin sonsuz coklukta argumani ve esas argumani")

# ---- U3: the principal value and its jump across the negative real axis
p = cplane(40, 24, 320, (-2.4, 2.4), (-2.2, 2.2))
p.sector(0, 0, 1.75, 0, PI, THEORY, 0.10)
p.sector(0, 0, 1.75, -PI, 0, PRACTICE, 0.10)
p.origin_axes()
p.line([(-2.35, 0), (0, 0)], THEORY, 3.4, None, 0.5)
angle_arc(p, 0, PI - 0.06, 0.5, THEORY, 2.0)
angle_arc(p, 0, -PI + 0.06, 0.36, PRACTICE, 2.0)
samples = [((1.5, 0), "Arg 1 = 0", 0, -10, "middle"), ((0, 1.5), "Arg i = " + PI_S + "/2", 8, -6, "start"),
           ((-1.5, 0), "Arg(" + MINUS + "1) = " + PI_S, -8, -8, "end"),
           ((0, -1.5), "Arg(" + MINUS + "i) = " + MINUS + PI_S + "/2", 8, 14, "start"),
           ((1.06, 1.06), "Arg(1 + i) = " + PI_S + "/4", 8, -4, "start"),
           ((-1.06, -1.06), "Arg(" + MINUS + "1 " + MINUS + " i) = " + MINUS + "3" + PI_S + "/4", 8, 16, "start")]
for pt, txt, dx, dy, anchor in samples:
    dot(p, pt, TEXT, 3.4)
    p.label(*pt, txt, dx, dy, TEXT, 11, anchor)
p.text_px(40 + 160, 24 + 22, "Arg z &gt; 0", THEORY, 12, "middle", True, True)
p.text_px(40 + 160, 24 + 300, "Arg z &lt; 0", PRACTICE, 12, "middle", True, True)
p.label(-0.62, 0.52, "&#252;stten yakla&#351;&#305;nca &#8594; " + PI_S, 0, 0, THEORY, 10.5, "end", False, True)
p.label(-0.55, -0.55, "alttan yakla&#351;&#305;nca &#8594; " + MINUS + PI_S, 0, 0, PRACTICE, 10.5, "end", False, True)
p.label(-2.3, 0, "eksen &#252;zerinde " + PI_S + " se&#231;ilir", 0, 16, THEORY, 10, "start", False, True)
OUT["esas-arguman-kesim"] = figure(
    400, 356, [p],
    "Esas arg&#252;man&#305;n kural&#305;: &#252;st yar&#305; d&#252;zlemde 0 ile &#960; aras&#305;, alt yar&#305; d&#252;zlemde 0 ile "
    "&#8722;&#960; aras&#305; &#246;l&#231;. Negatif reel eksende iki &#246;l&#231;&#252;m kar&#351;&#305;la&#351;&#305;r ve &#960; se&#231;ilir "
    "(&#8722;&#960; hi&#231; kullan&#305;lmaz); ekseni yukar&#305;dan a&#351;a&#287;&#305;ya ge&#231;erken Arg <em>z</em> "
    "aniden 2&#960; d&#252;&#351;er. Bu eksen, Arg'&#305;n s&#252;reksiz oldu&#287;u tek yerdir.",
    aria="Esas argumanin (-pi, pi] araligi ve negatif reel eksendeki sicramasi")

# ---- U4: arctan(y/x) versus Arg z = atan2(y, x)
p = cplane(30, 30, 340, (-2.9, 2.9), (-2.9, 2.9))
p.origin_axes()
p.line([(-1.85, -1.85), (1.85, 1.85)], REMARK, 1.1, "4 3", 0.55)
angle_arc(p, 0, PI / 4, 0.55, THEORY, 2.0)
angle_arc(p, 0, -3 * PI / 4, 0.42, PRACTICE, 2.0)
p.arrow((0, 0), (1.3, 1.3), THEORY, 2.0)
p.arrow((0, 0), (-1.3, -1.3), PRACTICE, 2.0)
dot(p, (1.3, 1.3), THEORY)
dot(p, (-1.3, -1.3), PRACTICE)
p.label(1.3, 1.3, "1 + i", 10, -2, THEORY, 12.5, "start", True)
p.label(-1.3, -1.3, MINUS + "1 " + MINUS + " i", -10, 6, PRACTICE, 12.5, "end", True)
p.label(0.72, 0.18, PI_S + "/4", 0, 0, THEORY, 11.5, "start", True)
p.label(0.30, -0.62, MINUS + "3" + PI_S + "/4", 0, 0, PRACTICE, 11.5, "start", True)
p.label(-1.85, -1.85, "y/x = 1 do&#287;rusu", -6, 4, REMARK, 10.5, "end", False, True)
p.label(1.0, 1.0, "arctan(1) = " + PI_S + "/4", 14, 8, THEORY, 10.5, "start", False, True)
p.label(-0.62, -0.62, "arctan(1) = " + PI_S + "/4 ?", -14, -2, PRACTICE, 10.5, "end", False, True)
# quadrant formulas
q = [((2.8, 2.6), "x &gt; 0", "arctan(y/x)", "end"), ((-2.8, 2.6), "x &lt; 0, y " + "&#8805;" + " 0", "arctan(y/x) + " + PI_S, "start"),
     ((-2.8, -2.45), "x &lt; 0, y &lt; 0", "arctan(y/x) " + MINUS + " " + PI_S, "start"), ((2.8, -2.45), "x &gt; 0", "arctan(y/x)", "end")]
for (x, y), cond, form, anchor in q:
    p.label(x, y, cond, 0, 0, TEXT, 10.5, anchor, False, True)
    p.label(x, y, "Arg z = " + form, 0, 15, TEXT, 11, anchor, True)
OUT["atan2-ceyrekler"] = figure(
    400, 400, [p],
    "1 + <em>i</em> ve &#8722;1 &#8722; <em>i</em> i&#231;in <em>y</em>/<em>x</em> oran&#305; ayn&#305;d&#305;r (1); "
    "arctan(<em>y</em>/<em>x</em>) ikisine de &#960;/4 der, &#231;&#252;nk&#252; hangi &#231;eyrekte oldu&#287;unu bilmez. "
    "atan2(<em>y</em>, <em>x</em>) i&#351;aretleri ayr&#305; ayr&#305; okur ve k&#246;&#351;elerdeki d&#252;zeltmeyi kendisi yapar; "
    "sonucu her zaman (&#8722;&#960;, &#960;] aral&#305;&#287;&#305;ndad&#305;r, yani tam olarak Arg <em>z</em>'dir.",
    aria="Arg z icin ceyreklere gore arctan duzeltmesi ve atan2")

# ---- U5: multiplication = rotate and scale
r1, t1 = 1.6, PI / 6
r2, t2 = 1.25, PI / 3
w1, w2, w = polar(r1, t1), polar(r2, t2), polar(r1 * r2, t1 + t2)
p = cplane(40, 24, 320, (-2.4, 2.4), (-0.6, 2.4))
p.origin_axes(xticks=(-2, -1, 1, 2))
p.circle(0, 0, r1 * r2, REMARK, 1.0, "4 3", opacity=0.5)
angle_arc(p, 0, t1, 0.5, THEORY, 1.8)
angle_arc(p, 0, t2, 0.72, BASE, 1.8)
angle_arc(p, 0, t1 + t2, 1.0, PRACTICE, 2.0)
p.arrow((0, 0), w1, THEORY, 2.0)
p.arrow((0, 0), w2, BASE, 2.0)
p.arrow((0, 0), w, PRACTICE, 2.3)
dot(p, w1, THEORY); dot(p, w2, BASE); dot(p, w, PRACTICE)
p.label(*w1, "z" + SUB1 + " = 1,6&#183;e<tspan font-size=\"9\" dy=\"-5\">i" + PI_S + "/6</tspan>", 8, 6, THEORY, 12, "start", True)
p.label(*w2, "z" + SUB2 + " = 1,25&#183;e<tspan font-size=\"9\" dy=\"-5\">i" + PI_S + "/3</tspan>", 8, -4, BASE, 12, "start", True)
p.label(*w, "z" + SUB1 + "z" + SUB2 + " = 2&#183;e<tspan font-size=\"9\" dy=\"-5\">i" + PI_S + "/2</tspan> = 2i", -8, -4, PRACTICE, 12, "end", True)
p.label(0.62, 0.12, THETA + SUB1, 0, 0, THEORY, 11.5, "start", True, True)
p.label(0.55, 0.62, THETA + SUB2, 0, 0, BASE, 11.5, "start", True, True)
p.label(-0.55, 0.95, THETA + SUB1 + " + " + THETA + SUB2, 0, 0, PRACTICE, 11.5, "end", True, True)
p.label(-2.0, 0.0, "|z| = 2 &#231;emberi", -2, -8, REMARK, 10.5, "start", False, True)
OUT["carpim-dondurme"] = figure(
    400, 264, [p],
    "&#199;arp&#305;mda mod&#252;ller &#231;arp&#305;l&#305;r, a&#231;&#305;lar toplan&#305;r: 1,6 &#183; 1,25 = 2 ve &#960;/6 + &#960;/3 = &#960;/2. "
    "<em>z</em><sub>1</sub> ile &#231;arpmak, d&#252;zlemi |<em>z</em><sub>1</sub>| oran&#305;nda &#246;l&#231;ekleyip "
    "arg <em>z</em><sub>1</sub> kadar d&#246;nd&#252;rmektir.",
    aria="Carpimda modullerin carpilmasi ve acilarin toplanmasi")

# ---- U6: Arg is not additive: (-1)(i) = -i
p = cplane(30, 24, 340, (-2.2, 3.6), (-1.9, 1.9))
p.origin_axes()
p.line([(-2.15, 0), (0, 0)], PRACTICE, 3.2, None, 0.35)
angle_arc(p, 0, PI - 0.05, 0.55, THEORY, 2.0)
angle_arc(p, PI, 3 * PI / 2 - 0.05, 0.75, BASE, 2.0)
angle_arc(p, 0, -PI / 2 + 0.05, 0.35, PRACTICE, 2.0)
p.arrow((0, 0), (-1.2, 0), THEORY, 2.0)
p.arrow((0, 0), (0, 1.2), BASE, 2.0)
p.arrow((0, 0), (0, -1.2), PRACTICE, 2.3)
dot(p, (-1.2, 0), THEORY); dot(p, (0, 1.2), BASE); dot(p, (0, -1.2), PRACTICE)
p.label(-1.2, 0, "z" + SUB1 + " = " + MINUS + "1", -4, -10, THEORY, 12.5, "end", True)
p.label(0, 1.2, "z" + SUB2 + " = i", 10, -2, BASE, 12.5, "start", True)
p.label(0, -1.2, "z" + SUB1 + "z" + SUB2 + " = " + MINUS + "i", 10, 14, PRACTICE, 12.5, "start", True)
p.label(-0.15, 0.62, "Arg z" + SUB1 + " = " + PI_S, -6, -6, THEORY, 11.5, "end", True)
p.label(-0.62, -0.62, "+ Arg z" + SUB2 + " = +" + PI_S + "/2", -6, 12, BASE, 11.5, "end", True)
p.label(0.42, -0.30, "Arg(z" + SUB1 + "z" + SUB2 + ") = " + MINUS + PI_S + "/2", 6, 6, PRACTICE, 11.5, "start", True)
p.text_px(p.X(3.5), p.Y(1.7), "Arg z" + SUB1 + " + Arg z" + SUB2 + " = 3" + PI_S + "/2", TEXT, 11.5, "end", True)
p.text_px(p.X(3.5), p.Y(1.7) + 17, "Arg(z" + SUB1 + "z" + SUB2 + ") = " + MINUS + PI_S + "/2", TEXT, 11.5, "end", True)
p.text_px(p.X(3.5), p.Y(1.7) + 36, "fark tam olarak 2" + PI_S + ":", TEXT, 11, "end", False, True)
p.text_px(p.X(3.5), p.Y(1.7) + 52, "ayn&#305; arg k&#252;mesi, farkl&#305; temsilci", TEXT, 11, "end", False, True)
OUT["arg-toplamsal-degil"] = figure(
    400, 262, [p],
    "&#8722;1'in a&#231;&#305;s&#305; &#960;, &#252;st&#252;ne <em>i</em>'nin &#960;/2'si eklenince toplam 3&#960;/2 olur ve ok alt yar&#305; "
    "d&#252;zleme, &#8722;<em>i</em> noktas&#305;na var&#305;r. Ama &#8722;<em>i</em>'nin esas arg&#252;man&#305; 3&#960;/2 de&#287;il, "
    "&#8722;&#960;/2'dir: toplam (&#8722;&#960;, &#960;] aral&#305;&#287;&#305;ndan ta&#351;m&#305;&#351; ve 2&#960; geri sar&#305;lm&#305;&#351;t&#305;r. "
    "K&#252;me olarak arg(<em>z</em><sub>1</sub><em>z</em><sub>2</sub>) = arg <em>z</em><sub>1</sub> + arg <em>z</em><sub>2</sub> "
    "e&#351;itli&#287;i yine de bozulmaz.",
    aria="Esas argumanin toplamsal olmadigini gosteren ornek")

# ==================================================================== kökler
p1 = cplane(24, 30, 250, (-3.4, 3.0), (-2.9, 3.0))
p1.origin_axes()
p1.circle(0, 0, 2, REMARK, 1.1, "4 3", opacity=0.6)
roots = [polar(2, -PI / 6 + 2 * PI * k / 3) for k in range(3)]
p1.polygon(roots, THEORY, 0.10, THEORY, 1.4)
angle_arc(p1, 0, -PI / 6, 0.8, PRACTICE, 1.8)
angle_arc(p1, -PI / 6, -PI / 6 + 2 * PI / 3, 1.05, BASE, 1.6)
for k, rt in enumerate(roots):
    p1.line([(0, 0), rt], THEORY, 1.2, None, 0.6)
    dot(p1, rt, PRACTICE if k == 0 else THEORY, 4.2)
p1.label(*roots[0], "c" + SUB0 + " = &#8730;3 " + MINUS + " i", 8, 14, PRACTICE, 12, "start", True)
p1.label(*roots[1], "c" + SUB1 + " = 2i", 8, -4, THEORY, 12, "start", True)
p1.label(*roots[2], "c" + SUB2 + " = " + MINUS + "&#8730;3 " + MINUS + " i", -8, 14, THEORY, 12, "end", True)
p1.label(0.95, -0.45, MINUS + PI_S + "/6", 6, 4, PRACTICE, 11, "start", True)
p1.label(0.55, 0.9, "2" + PI_S + "/3", 8, 0, BASE, 11, "start", True)
p1.text_px(24 + 125, 22, "(" + MINUS + "8i)<tspan font-size=\"9\" dy=\"-6\">1/3</tspan><tspan dy=\"6\">: |z| = 2 &#231;emberinde e&#351;kenar &#252;&#231;gen</tspan>", TEXT, 11.5, "middle", True)

p2 = cplane(300, 30, 250, (-3.2, 3.2), (-2.9, 3.0))
p2.origin_axes()
p2.circle(0, 0, 2, REMARK, 1.1, "4 3", opacity=0.6)
roots6 = [polar(2, 2 * PI * k / 6) for k in range(6)]
p2.polygon(roots6, THEORY, 0.10, THEORY, 1.4)
angle_arc(p2, 0, PI / 3, 0.9, BASE, 1.8)
for k, rt in enumerate(roots6):
    dot(p2, rt, PRACTICE if k == 1 else THEORY, 4.2)
labels6 = ["1", "&#969;", "&#969;&#178;", "&#969;&#179;", "&#969;<tspan font-size=\"9\" dy=\"-6\">4</tspan>", "&#969;<tspan font-size=\"9\" dy=\"-6\">5</tspan>"]
offs = [(10, 4, "start"), (8, -4, "start"), (-8, -4, "end"), (-10, 4, "end"), (-8, 16, "end"), (8, 16, "start")]
for rt, lab, (dx, dy, an) in zip(roots6, labels6, offs):
    p2.label(*rt, lab, dx, dy, PRACTICE if lab == "&#969;" else THEORY, 12.5, an, True, True)
p2.label(0.72, 0.42, "2" + PI_S + "/6", 6, 0, BASE, 11, "start", True)
p2.text_px(300 + 125, 22, "1<tspan font-size=\"9\" dy=\"-6\">1/6</tspan><tspan dy=\"6\">: birim k&#246;kleri, &#969; = e</tspan><tspan font-size=\"9\" dy=\"-6\">i2" + PI_S + "/6</tspan>", TEXT, 11.5, "middle", True)
OUT["kokler"] = figure(
    574, 292, [p1, p2],
    "Solda &#8722;8<em>i</em>'nin &#252;&#231; k&#252;p k&#246;k&#252;: esas k&#246;k <em>c</em><sub>0</sub> a&#231;&#305;s&#305; "
    "Arg(&#8722;8<em>i</em>)/3 = &#8722;&#960;/6 olan noktad&#305;r, di&#287;erleri 2&#960;/3'l&#252;k ad&#305;mlarla d&#246;nerek elde edilir. "
    "Sa&#287;da 1'in alt&#305;nc&#305; k&#246;kleri: her k&#246;k bir &#246;ncekinin <em>&#969;</em> ile &#231;arp&#305;m&#305;d&#305;r, "
    "yani 2&#960;/6 kadar d&#246;nd&#252;r&#252;lm&#252;&#351;&#252;d&#252;r.",
    css_class=WIDE, aria="Kup kokler ve birim kokleri cember uzerinde duzgun cokgen olusturur")
OUT["arg-kumesi"] = OUT["arg-kumesi"].replace('<figure class="ders-grafik">', '<figure class="ders-grafik ders-grafik-genis">')

# ================================================================== bölgeler
# ---- B1: interior, boundary and exterior points of an open disk
p = cplane(40, 24, 320, (-2.1, 2.7), (-1.95, 1.95))
p.origin_axes()
p.add(f'<circle cx="{p.X(0):.1f}" cy="{p.Y(0):.1f}" r="{p.R(1.4):.1f}" fill="{THEORY}" fill-opacity="0.10" stroke="none"/>')
p.circle(0, 0, 1.4, THEORY, 1.6, "5 4")
a, b, c = (0.45, 0.35), polar(1.4, PI / 4), (2.05, -0.95)
for pt, rad, col, txt, dx, dy, an in ((a, 0.36, BASE, "i&#231; nokta", 0, 30, "middle"),
                                     (b, 0.36, PRACTICE, "s&#305;n&#305;r noktas&#305;", 8, -18, "start"),
                                     (c, 0.30, REMARK, "d&#305;&#351; nokta", 0, 28, "middle")):
    p.add(f'<circle cx="{p.X(pt[0]):.1f}" cy="{p.Y(pt[1]):.1f}" r="{p.R(rad):.1f}" fill="{col}" fill-opacity="0.18" stroke="none"/>')
    p.circle(*pt, rad, col, 1.3)
    dot(p, pt, col, 3.6)
    p.label(*pt, txt, dx, dy, col, 11.5, an, True)
p.label(-1.4, 1.0, "S: |z| &lt; 1,4", -4, 0, THEORY, 12, "end", True, True)
OUT["ic-sinir-dis"] = figure(
    400, 300, [p],
    "A&#231;&#305;k disk <em>S</em> i&#231;in &#252;&#231; t&#252;r nokta. &#304;&#231; noktan&#305;n tamamen <em>S</em>'de kalan bir kom&#351;ulu&#287;u vard&#305;r; "
    "d&#305;&#351; noktan&#305;n <em>S</em>'ye hi&#231; de&#287;meyen bir kom&#351;ulu&#287;u vard&#305;r; s&#305;n&#305;r noktas&#305;n&#305;n ise "
    "<strong>her</strong> kom&#351;ulu&#287;u iki taraftan da nokta i&#231;erir. &#199;emberin kendisi <em>S</em>'ye ait olmad&#305;&#287;&#305;ndan "
    "(kesikli) k&#252;me a&#231;&#305;kt&#305;r.",
    aria="Acik diskin ic, sinir ve dis noktalari ve komsuluklari")

# ---- B2: the annulus 1 < |z| < 2 is connected by a polygonal path
p = cplane(40, 24, 320, (-2.5, 2.5), (-2.35, 2.35))
p.add(f'<path d="M{p.X(2):.1f},{p.Y(0):.1f} A{p.R(2):.1f},{p.R(2):.1f} 0 1,0 {p.X(-2):.1f},{p.Y(0):.1f} A{p.R(2):.1f},{p.R(2):.1f} 0 1,0 {p.X(2):.1f},{p.Y(0):.1f} Z '
      f'M{p.X(1):.1f},{p.Y(0):.1f} A{p.R(1):.1f},{p.R(1):.1f} 0 1,1 {p.X(-1):.1f},{p.Y(0):.1f} A{p.R(1):.1f},{p.R(1):.1f} 0 1,1 {p.X(1):.1f},{p.Y(0):.1f} Z" '
      f'fill="{THEORY}" fill-opacity="0.10" fill-rule="evenodd" stroke="none"/>')
p.origin_axes(xticks=(-2, -1, 1, 2))
p.circle(0, 0, 1, THEORY, 1.5, "5 4")
p.circle(0, 0, 2, THEORY, 1.5, "5 4")
path = [(1.45, 0.35), (0.9, 1.2), (-0.5, 1.45), (-1.35, 0.6)]
p.line(path, PRACTICE, 2.0)
p.points(path[1:-1], PRACTICE, 3.0)
dot(p, path[0], PRACTICE, 4.2); dot(p, path[-1], PRACTICE, 4.2)
p.label(*path[0], "z" + SUB1, 8, 10, PRACTICE, 12.5, "start", True, True)
p.label(*path[-1], "z" + SUB2, -8, 10, PRACTICE, 12.5, "end", True, True)
p.label(1.55, -1.55, "1 &lt; |z| &lt; 2", 0, 0, THEORY, 12, "start", True, True)
OUT["halka-domen"] = figure(
    400, 348, [p],
    "Halka 1 &lt; |<em>z</em>| &lt; 2 bir domendir: s&#305;n&#305;r &#231;emberlerini i&#231;ermedi&#287;inden a&#231;&#305;kt&#305;r ve herhangi "
    "iki noktas&#305;, halkadan hi&#231; &#231;&#305;kmayan sonlu say&#305;da do&#287;ru par&#231;as&#305;yla (&#231;okgensel yol) "
    "birle&#351;tirilebilir. Do&#287;rudan bir do&#287;ru par&#231;as&#305; i&#231;teki deli&#287;e girebilirdi; k&#305;r&#305;k &#231;izgi bunu a&#351;ar.",
    aria="Halka bolgesinde iki noktayi birlestiren cokgensel yol")

# ============================================================== cebirsel-yapı
# ---- the complex plane: a number is a point, 1 and i are the unit points
z = (2.0, 1.5)
p = cplane(40, 24, 320, (-0.8, 3.6), (-0.7, 2.3))
p.origin_axes(xlabel="Re (reel eksen)", ylabel="Im (sanal eksen)")
p.line([(z[0], 0), z], BASE, 1.3, "5 4", 0.8)
p.line([(0, z[1]), z], BASE, 1.3, "5 4", 0.8)
dot(p, z, THEORY, 4.2)
dot(p, (1, 0), REMARK, 3.4)
dot(p, (0, 1), REMARK, 3.4)
p.label(*z, "z = (x, y) = x + iy", 9, -6, THEORY, 12.5, "start", True)
p.label(z[0], 0, "x", 0, 16, TEXT, 12, "middle", False, True)
p.label(0, z[1], "y", -8, 4, TEXT, 12, "end", False, True)
p.label(1, 0, "1 = (1, 0)", 0, 16, REMARK, 11, "middle")
p.label(0, 1, "i = (0, 1)", -8, 4, REMARK, 11, "end")
p.label(0, 0, "0", -7, 14, TEXT, 11, "end")
OUT["kompleks-duzlem"] = figure(
    400, 280, [p],
    "Kompleks d&#252;zlem: yatay eksen reel k&#305;sm&#305;, d&#252;&#351;ey eksen sanal k&#305;sm&#305; ta&#351;&#305;r. "
    "<em>z</em> = (<em>x</em>, <em>y</em>) s&#305;ral&#305; ikilisi d&#252;zlemin bir noktas&#305;d&#305;r; 1 = (1, 0) reel eksende, "
    "<em>i</em> = (0, 1) sanal eksende birim uzakl&#305;ktaki noktalard&#305;r.",
    aria="Kompleks duzlem, z = x + iy noktasi, 1 ve i noktalari")

# ================================================================== bölgeler
# ---- 0 < |z| <= 1 is neither open nor closed
p = cplane(40, 24, 320, (-1.7, 1.7), (-1.5, 1.5))
p.origin_axes()
disk_fill(p, 0, 0, 1, THEORY, 0.12)
p.circle(0, 0, 1, THEORY, 2.0)
p.add(f'<circle cx="{p.X(0):.1f}" cy="{p.Y(0):.1f}" r="4.2" fill="{BG}" fill-opacity="1" stroke="{PRACTICE}" stroke-width="2"/>')
p.label(0, 0, "0 k&#252;mede de&#287;il", 9, -8, PRACTICE, 11.5, "start", True)
p.label(0.72, 0.72, "|z| = 1 k&#252;meye ait", 8, -4, THEORY, 11.5, "start", True)
p.label(-0.55, -0.62, "0 &lt; |z| " + LEQ + " 1", 0, 0, THEORY, 12.5, "middle", True, True)
OUT["ne-acik-ne-kapali"] = figure(
    400, 316, [p],
    "0 &lt; |<em>z</em>| &#8804; 1 k&#252;mesi. &#199;ember k&#252;meye aittir ama &#252;zerindeki hi&#231;bir nokta i&#231; nokta de&#287;ildir, "
    "dolay&#305;s&#305;yla k&#252;me a&#231;&#305;k de&#287;ildir. Ba&#351;lang&#305;&#231; noktas&#305; bir s&#305;n&#305;r noktas&#305;d&#305;r ama k&#252;mede "
    "de&#287;ildir, dolay&#305;s&#305;yla k&#252;me kapal&#305; da de&#287;ildir.",
    aria="Ne acik ne kapali kume: delinmis kapali birim disk")

# ================================================================= üstel-form
# ---- arg z on the number line: dots spaced 2π, the window (-π, π] catches exactly one
p = Plot(30, 44, 340, 84, (-4.5, 4.5), (-1.2, 1.2))
p.polygon([(-1, -0.45), (1, -0.45), (1, 0.45), (-1, 0.45)], THEORY, 0.12)
p.arrow((-4.5, 0), (4.5, 0), TEXT, 1.1, head=7, opacity=0.6)
for k in range(-4, 5):
    p.add(f'<line x1="{p.X(k):.1f}" y1="{p.Y(0)-4:.1f}" x2="{p.X(k):.1f}" y2="{p.Y(0)+4:.1f}" stroke="{TEXT}" stroke-width="1" opacity="0.6"/>')
    lab = "0" if k == 0 else (("" if k > 0 else MINUS) + ("" if abs(k) == 1 else str(abs(k))) + PI_S)
    p.label(k, 0, lab, 0, 18, TEXT, 10.5, "middle")
A = -0.75
for n in range(-2, 3):
    t = A + 2 * n
    if -4.5 < t < 4.5:
        dot(p, (t, 0), PRACTICE if n == 0 else BASE, 4.2 if n == 0 else 3.6)
p.label(A, 0, "Arg z = " + MINUS + "3" + PI_S + "/4", 0, -30, PRACTICE, 11.5, "middle", True)
p.label(A + 2, 0, "5" + PI_S + "/4", 0, -30, BASE, 11, "middle")
p.label(A - 2, 0, MINUS + "11" + PI_S + "/4", 0, -30, BASE, 11, "middle")
p.label(A + 4, 0, "13" + PI_S + "/4", 0, -30, BASE, 11, "middle")
# the window (-π, π]: open at -π, closed at π
p.add(f'<circle cx="{p.X(-1):.1f}" cy="{p.Y(0.45):.1f}" r="3.2" fill="{BG}" stroke="{THEORY}" stroke-width="1.6"/>')
p.add(f'<circle cx="{p.X(1):.1f}" cy="{p.Y(0.45):.1f}" r="3.2" fill="{THEORY}"/>')
p.label(0.12, 0, "(" + MINUS + PI_S + ", " + PI_S + "]", 0, -7, THEORY, 10.5, "middle", True)
# spacing bracket below the tick labels
p.arrow((A + 0.1, -0.9), (A + 1.9, -0.9), BASE, 1.2, head=6)
p.arrow((A + 1.9, -0.9), (A + 0.1, -0.9), BASE, 1.2, head=6)
p.label(A + 2.05, -0.9, "2" + PI_S + " aral&#305;k", 4, 4, BASE, 10.5, "start", False, True)
OUT["arg-sayi-dogrusu"] = figure(
    400, 164, [p],
    "arg(&#8722;1 &#8722; <em>i</em>) k&#252;mesi say&#305; do&#287;rusunda: 2&#960; aral&#305;kl&#305; sonsuz nokta. Uzunlu&#287;u 2&#960; olan "
    "(&#8722;&#960;, &#960;] penceresi bu noktalardan tam birini yakalar; yakalanan nokta Arg <em>z</em>'dir. "
    "Pencerenin sol ucu a&#231;&#305;k (&#8722;&#960; d&#305;&#351;ar&#305;da), sa&#287; ucu kapal&#305;d&#305;r (&#960; i&#231;eride).",
    aria="Arguman kumesi sayi dogrusunda ve esas arguman penceresi")

# ====================================================== rezidü: tekil nokta türleri
# ---- the three types at a glance: which Laurent coefficients are nonzero
p = Plot(146, 46, 350, 168, (-5.9, 2.9), (-0.35, 3.15))
p.polygon([(-5.9, -0.35), (-0.5, -0.35), (-0.5, 3.15), (-5.9, 3.15)], PRACTICE, 0.07)
p.add(f'<line x1="{p.X(-0.5):.1f}" y1="{p.y0:.1f}" x2="{p.X(-0.5):.1f}" y2="{p.y0+p.h:.1f}" stroke="{TEXT}" stroke-width="1" stroke-dasharray="4 3" opacity="0.5"/>')
rows = [(2.5, "kald&#305;r&#305;labilir", []),
        (1.5, "m = 2 kutup", [-1, -2]),
        (0.5, "esasl&#305;", [-1, -2, -3, -4, -5])]
for y, label, neg in rows:
    p.text_px(138, p.Y(y) + 4, label, TEXT, 11.5, "end", True)
    p.line([(-5.7, y - 0.5), (2.7, y - 0.5)], TEXT, 0.7, None, 0.15) if y > 0.5 else None
    p.points([(n, y) for n in range(0, 3)], THEORY, 3.6)
    p.points([(n, y) for n in neg], PRACTICE, 3.6)
for n in range(-5, 3):
    p.text_px(p.X(n), p.y0 + p.h + 16, str(n), TEXT, 10.5, "middle")
p.text_px(p.X(-1.5), p.y0 + p.h + 32, "kuvvet: (z " + MINUS + " z" + SUB0 + ")&#8319;", TEXT, 10.5, "middle", False, True)
p.text_px(p.X(-3.2), p.y0 - 10, "esas k&#305;s&#305;m (n &lt; 0)", PRACTICE, 11, "middle", True)
p.text_px(p.X(1.2), p.y0 - 10, "analitik k&#305;s&#305;m", THEORY, 11, "middle", True)
p.text_px(p.X(-5.7), p.Y(0.5) + 4, "&#8230;", PRACTICE, 13, "end", True)
p.text_px(p.X(-2), p.Y(1.5) - 12, "b&#8322; &#8800; 0, sonras&#305; yok", PRACTICE, 10, "middle", False, True)
OUT["uc-tip"] = figure(
    520, 258, [p],
    "&#220;&#231; tekillik tipi, tek bak&#305;&#351;ta: her sat&#305;r bir Laurent a&#231;&#305;l&#305;m&#305;d&#305;r, dolu noktalar "
    "s&#305;f&#305;rdan farkl&#305; katsay&#305;lar&#305; g&#246;sterir. Fark yaln&#305;zca <strong>esas k&#305;s&#305;mdaki</strong> "
    "(negatif kuvvetli) terim say&#305;s&#305;ndad&#305;r: hi&#231; yoksa kald&#305;r&#305;labilir, sonluysa kutup, "
    "sonsuzsa esasl&#305; tekil nokta.",
    css_class=WIDE, aria="Uc tekillik tipinin Laurent katsayilariyla karsilastirilmasi")

# ############################################################################
# PART: Analitik Fonksiyonlar
# ############################################################################

# ############################################################################
# PART: Analitik Fonksiyonlar
# ############################################################################


def sub(s, size=9):
    """Subscript inside an SVG <text>: 'u' + sub('x') -> u_x."""
    return f'<tspan font-size="{size}" dy="3">{s}</tspan><tspan dy="-3">&#8203;</tspan>'   # zero-width space: baseline reset that does not eat the following space


def _between(p, px, py, txt):
    """Map name and arrow placed in the gap between two panels."""
    p.text_px(px, py, txt, TEXT, 12, "middle", True)
    p.text_px(px, py + 22, "&#8594;", TEXT, 20, "middle")


def _blob_inner(cx, cy, sx, base_r, wobble, t, margin):
    """A point `margin` inside the boundary of an x-stretched blob(cx, cy, base_r, wobble), at polar angle t."""
    r = base_r + sum(a * math.cos(k * t + ph) for a, k, ph in wobble) - margin
    return (cx + sx * r * math.cos(t), cy + r * math.sin(t))


# ================================================= fonksiyonlar-ve-tasvirler
# ---- T1: w = z² — the hyperbolas x²−y²=c₁ and 2xy=c₂ land on the lines u=c₁, v=c₂
c1, c2 = 1.0, 2.0
zx = math.sqrt((1 + math.sqrt(5)) / 2)       # x⁴ − x² − 1 = 0 (with xy = 1)
z0 = (zx, 1 / zx)                            # intersection ≈ (1,27; 0,79)
p1 = cplane(24, 30, 240, (-3.3, 3.3), (-3.3, 3.3))
p1.origin_axes("x", "y")
ts = [-1.75 + 3.5 * k / 60 for k in range(61)]
p1.line([(math.cosh(t), math.sinh(t)) for t in ts], THEORY, 1.9)
p1.line([(-math.cosh(t), math.sinh(t)) for t in ts], THEORY, 1.9)
xs = [0.32 + (3.25 - 0.32) * k / 70 for k in range(71)]
p1.line([(x, 1 / x) for x in xs], PRACTICE, 1.9)
p1.line([(-x, -1 / x) for x in xs], PRACTICE, 1.9)
dot(p1, z0, TEXT, 3.8)
p1.label(*z0, "z&#8320;", -9, 4, TEXT, 12, "end", True, True)
p1.label(2.55, -2.7, "x&#178; &#8722; y&#178; = c&#8321;", 0, 0, THEORY, 11.5, "end", True)
p1.label(0.9, 2.4, "2xy = c&#8322;", 0, 0, PRACTICE, 11.5, "start", True)
panel_title(p1, "z-d&#252;zlemi")

p2 = cplane(316, 30, 240, (-3.3, 3.3), (-3.3, 3.3))
p2.origin_axes("u", "v")
p2.line([(c1, -3.2), (c1, 3.2)], THEORY, 1.9)
p2.line([(-3.2, c2), (3.2, c2)], PRACTICE, 1.9)
dot(p2, (c1, c2), TEXT, 3.8)
p2.label(c1, c2, "w&#8320; = z&#8320;&#178;", 8, -8, TEXT, 12, "start", True, True)
p2.label(c1, -2.7, "u = c&#8321;", 8, 0, THEORY, 11.5, "start", True)
p2.label(-3.1, c2, "v = c&#8322;", 0, -8, PRACTICE, 11.5, "start", True)
panel_title(p2, "w-d&#252;zlemi")
_between(p1, 290, 140, "w = z&#178;")
OUT["analitik-fonksiyonlar-hiperboller"] = figure(
    580, 318, [p1, p2],
    "<em>w</em> = <em>z</em>&#178; alt&#305;nda <em>x</em>&#178; &#8722; <em>y</em>&#178; = <em>c</em><sub>1</sub> hiperbol&#252;n&#252;n "
    "<strong>iki kolu da</strong> <em>u</em> = <em>c</em><sub>1</sub> dikey do&#287;rusunun tamam&#305;na, 2<em>xy</em> = <em>c</em><sub>2</sub> "
    "hiperbol&#252;n&#252;n iki kolu da <em>v</em> = <em>c</em><sub>2</sub> yatay do&#287;rusuna gider (&#231;izimde <em>c</em><sub>1</sub> = 1, "
    "<em>c</em><sub>2</sub> = 2). Hiperbollerin kesi&#351;ti&#287;i <em>z</em><sub>0</sub> noktas&#305;, do&#287;rular&#305;n kesi&#351;ti&#287;i "
    "<em>w</em><sub>0</sub> = <em>z</em><sub>0</sub>&#178; noktas&#305;na ta&#351;&#305;n&#305;r.",
    css_class=WIDE, aria="w = z kare altinda hiperbollerin dikey ve yatay dogrulara tasviri")

# ---- T2: the region x>0, y>0, xy<1 is swept by hyperbola arcs and lands on the strip 0<v<2
p1 = cplane(24, 30, 240, (-0.9, 3.4), (-0.9, 3.4))
p1.origin_axes("x", "y")
xs = [0.3 + (3.35 - 0.3) * k / 80 for k in range(81)]
reg = [(0, 0), (3.35, 0)] + [(x, 1 / x) for x in reversed(xs)] + [(0.3, 3.35), (0, 3.35)]
p1.polygon(reg, BASE, 0.14)
p1.line([(x, 1 / x) for x in xs], PRACTICE, 2.0)
for cc in (0.2, 0.65):                       # 2xy = 0,4 and 2xy = 1,3
    xs2 = [cc / 3.35 + (3.35 - cc / 3.35) * k / 80 for k in range(81)]
    p1.line([(x, cc / x) for x in xs2], THEORY, 1.4, "5 4", 0.85)
p1.line([(0, 0), (3.35, 0)], BASE, 2.4)
p1.line([(0, 0), (0, 3.35)], BASE, 2.4)
p1.label(1.3, 1 / 1.3, "xy = 1", 8, -6, PRACTICE, 11.5, "start", True)
p1.label(3.3, 2.95, "kesikli: 2xy = c&#8322;", 0, 0, THEORY, 11, "end", False, True)
p1.label(3.3, 2.65, "0 &lt; c&#8322; &lt; 2", 0, 0, THEORY, 11, "end", False, True)
p1.label(2.0, 0, "z = x", 0, 16, BASE, 11.5, "middle", True)
p1.label(0, 2.0, "z = iy", -8, 4, BASE, 11.5, "end", True)
panel_title(p1, "x &gt; 0, y &gt; 0, xy &lt; 1")

p2 = cplane(316, 30, 240, (-3.5, 3.5), (-3.6, 3.4))
p2.origin_axes("u", "v")
p2.polygon([(-3.5, 0), (3.5, 0), (3.5, 2), (-3.5, 2)], BASE, 0.14)
p2.line([(-3.5, 2), (3.5, 2)], PRACTICE, 2.0)
for vv in (0.4, 1.3):
    p2.line([(-3.5, vv), (3.5, vv)], THEORY, 1.4, "5 4", 0.85)
p2.line([(-3.5, 0), (3.5, 0)], BASE, 2.4)
p2.label(-3.4, 2, "v = 2", 0, -7, PRACTICE, 11.5, "start", True)
p2.label(-3.4, 0.72, "v = c&#8322;", 0, 0, THEORY, 11, "start", False, True)
p2.label(3.4, 0.72, "0 &lt; v &lt; 2", 0, 0, BASE, 11, "end", False, True)
p2.label(-1.75, 0, "z = iy &#8594; &#8722;y&#178;", 0, 16, BASE, 11, "middle", True)
p2.label(1.75, 0, "z = x &#8594; x&#178;", 0, 16, BASE, 11, "middle", True)
panel_title(p2, "0 &lt; v &lt; 2 &#351;eridi")
_between(p1, 290, 140, "w = z&#178;")
OUT["analitik-fonksiyonlar-serit"] = figure(
    580, 318, [p1, p2],
    "B&#246;lge, 0 &lt; <em>c</em><sub>2</sub> &lt; 2 olan 2<em>xy</em> = <em>c</em><sub>2</sub> hiperbol yaylar&#305;yla (kesikli) taran&#305;r; "
    "her yay <em>v</em> = <em>c</em><sub>2</sub> do&#287;rusunun tamam&#305;na gitti&#287;inden g&#246;r&#252;nt&#252; 0 &lt; <em>v</em> &lt; 2 &#351;erididir. "
    "S&#305;n&#305;rda pozitif <em>y</em> ekseni <em>u</em> ekseninin negatif yar&#305;s&#305;n&#305;, pozitif <em>x</em> ekseni pozitif yar&#305;s&#305;n&#305; "
    "&#246;rter; <em>xy</em> = 1 hiperbol&#252; <em>v</em> = 2 do&#287;rusuna gider.",
    css_class=WIDE, aria="Birinci ceyrekte xy kucuk 1 bolgesinin w = z kare altinda 0-2 seridine tasviri")

# ---- T3: w = e^z — the strip 0 ≤ y ≤ π and a rectangle inside it
a, b = -1.0, 1.0
p1 = cplane(24, 30, 200, (-2.4, 2.4), (-0.8, 3.9))
p1.origin_axes("x", "y")
p1.polygon([(-2.4, 0), (2.4, 0), (2.4, PI), (-2.4, PI)], BASE, 0.12)
p1.polygon([(a, 0), (b, 0), (b, PI), (a, PI)], REMARK, 0.20, REMARK, 1.3)
p1.line([(-2.4, 0), (2.4, 0)], PRACTICE, 2.0)
p1.line([(-2.4, PI), (2.4, PI)], THEORY, 2.0)
p1.label(-2.3, 0, "y = 0", 0, 15, PRACTICE, 11.5, "start", True)
p1.label(2.3, PI, "y = &#960;", 0, -6, THEORY, 11.5, "end", True)
p1.label(a, PI, "x = a", 0, -6, REMARK, 11, "middle", True)
p1.label(b, PI, "x = b", 0, -6, REMARK, 11, "middle", True)
panel_title(p1, "0 &#8804; y &#8804; &#960; &#351;eridi")

p2 = cplane(290, 30, 260, (-3.6, 3.6), (-1.6, 3.8))
p2.origin_axes("u", "v")
p2.polygon([(-3.6, 0), (3.6, 0), (3.6, 3.8), (-3.6, 3.8)], BASE, 0.12)
ra, rb = math.exp(a), math.exp(b)
p2.polygon(circle_pts(0, 0, rb, 0, PI) + circle_pts(0, 0, ra, PI, 0), REMARK, 0.20, REMARK, 1.3)
p2.line([(0.12, 0), (3.6, 0)], PRACTICE, 2.0)
p2.line([(-3.6, 0), (-0.12, 0)], THEORY, 2.0)
hollow(p2, (0, 0), TEXT)
p2.label(1.9, 0, "y = 0 &#8594; &#966; = 0", 0, 15, PRACTICE, 11, "middle", True)
p2.label(-1.9, 0, "y = &#960; &#8594; &#966; = &#960;", 0, 15, THEORY, 11, "middle", True)
p2.label(0, 0, "w = 0 hari&#231;", 0, 30, TEXT, 10.5, "middle", False, True)
p2.label(rb * 0.707, rb * 0.707, "&#961; = e" + sup("b"), 6, -4, REMARK, 11, "start", True)
p2.label(ra * 0.707, ra * 0.707, "&#961; = e" + sup("a"), 14, -2, REMARK, 11, "start", True)
panel_title(p2, "Im w &#8805; 0, w &#8800; 0")
_between(p1, 257, 118, "w = e" + sup("z"))
OUT["analitik-fonksiyonlar-ustel-serit"] = figure(
    574, 274, [p1, p2],
    "<em>e</em><sup><em>z</em></sup> alt&#305;nda yatay do&#287;rular &#305;&#351;&#305;na, dikey do&#287;rular &#231;embere gider: "
    "<em>a</em> &#8804; <em>x</em> &#8804; <em>b</em>, 0 &#8804; <em>y</em> &#8804; &#960; dikd&#246;rtgeni <em>e</em><sup><em>a</em></sup> &#8804; &#961; &#8804; <em>e</em><sup><em>b</em></sup> "
    "yar&#305;m halkas&#305;na b&#252;k&#252;l&#252;r. &#350;eridin alt kenar&#305; <em>y</em> = 0 pozitif reel eksene, &#252;st kenar&#305; <em>y</em> = &#960; "
    "negatif reel eksene gider; &#351;eridin tamam&#305; <em>w</em> = 0 &#231;&#305;kar&#305;lm&#305;&#351; &#252;st yar&#305; d&#252;zlemi &#246;rter.",
    css_class=WIDE, aria="e ussu z altinda yatay seridin ust yari duzleme, dikdortgenin yarim halkaya tasviri")

# ==================================================== limitler-ve-sureklilik
# ---- L1: the ε–δ picture of the limit definition
z0, zz, dl = (1.2, 1.0), (1.55, 1.3), 0.8
w0, fz, ep = (1.5, 1.2), (1.72, 1.42), 0.6
p1 = cplane(24, 30, 240, (-0.4, 2.6), (-0.4, 2.4))
p1.origin_axes(opacity=0.35)
disk_fill(p1, *z0, dl, THEORY, 0.10)
p1.circle(*z0, dl, THEORY, 1.5, "5 4")
rp = (z0[0] + dl * math.cos(-0.6), z0[1] + dl * math.sin(-0.6))
p1.line([z0, rp], THEORY, 1.3)
p1.label((z0[0] + rp[0]) / 2, (z0[1] + rp[1]) / 2, "&#948;", -8, 6, THEORY, 13, "end", True, True)
hollow(p1, z0, TEXT)
dot(p1, zz, TEXT)
p1.label(*z0, "z&#8320;", -8, -6, TEXT, 12.5, "end", True, True)
p1.label(*zz, "z", 0, -8, TEXT, 12.5, "middle", True, True)
panel_title(p1, "0 &lt; |z &#8722; z&#8320;| &lt; &#948;")

p2 = cplane(316, 30, 240, (-0.4, 2.6), (-0.4, 2.4))
p2.origin_axes(opacity=0.35)
disk_fill(p2, *w0, ep, PRACTICE, 0.10)
p2.circle(*w0, ep, PRACTICE, 1.5, "5 4")
rp = (w0[0] + ep * math.cos(-0.6), w0[1] + ep * math.sin(-0.6))
p2.line([w0, rp], PRACTICE, 1.3)
p2.label((w0[0] + rp[0]) / 2, (w0[1] + rp[1]) / 2, "&#949;", -8, 6, PRACTICE, 13, "end", True, True)
dot(p2, w0, TEXT)
dot(p2, fz, TEXT)
p2.label(*w0, "w&#8320;", -8, 14, TEXT, 12.5, "end", True, True)
p2.label(*fz, "f(z)", -6, -4, TEXT, 12.5, "end", True, True)
panel_title(p2, "|f(z) &#8722; w&#8320;| &lt; &#949;")
_between(p1, 290, 135, "f")
OUT["analitik-fonksiyonlar-epsilon-delta"] = figure(
    580, 302, [p1, p2],
    "Limit tan&#305;m&#305; iki d&#252;zlemde okunur: <em>z</em><sub>0</sub> merkezli delinmi&#351; &#948;-diskinin (merkez hari&#231;) "
    "her noktas&#305;, <em>f</em> alt&#305;nda <em>w</em><sub>0</sub> merkezli &#949;-diskinin i&#231;ine d&#252;&#351;melidir. "
    "&#948;, <em>z</em><sub>0</sub>'a hangi y&#246;nden yakla&#351;&#305;ld&#305;&#287;&#305;na bakmaz; ko&#351;ul diskin tamam&#305; i&#231;in ge&#231;erlidir.",
    css_class=WIDE, aria="Epsilon-delta limit tanimi: z-duzleminde delinmis delta diski, w-duzleminde epsilon diski")

# ---- L2: z / z̄ takes a different limit along every ray
p1 = cplane(24, 30, 240, (-1.5, 3.1), (-2.0, 2.3))
p1.origin_axes()
hollow(p1, (0, 0), TEXT)
p1.arrow((1.8, 0), (0.12, 0), THEORY, 2.0)
p1.arrow((0, 1.8), (0, 0.12), PRACTICE, 2.0)
p1.arrow((1.3, 1.3), (0.09, 0.09), REMARK, 2.0)
p1.label(1.0, 0, "z = x", 0, 16, THEORY, 11.5, "middle", True)
p1.label(0, 1.0, "z = iy", -8, 4, PRACTICE, 11.5, "end", True)
p1.label(1.3, 1.3, "z = x(1 + i)", 8, 4, REMARK, 11.5, "start", True)
panel_title(p1, "z &#8594; 0 yollar&#305;")

p2 = cplane(316, 30, 240, (-1.8, 1.8), (-1.7, 1.7))
p2.origin_axes()
p2.circle(0, 0, 1, BASE, 1.2, "4 3", opacity=0.7)
dot(p2, (1, 0), THEORY, 4.2)
dot(p2, (-1, 0), PRACTICE, 4.2)
dot(p2, (0, 1), REMARK, 4.2)
p2.label(1, 0, "f = 1", 10, -8, THEORY, 12, "start", True)          # outside the dashed circle
p2.label(-1, 0, "f = &#8722;1", -10, -8, PRACTICE, 12, "end", True)
p2.label(0, 1, "f = i", 10, -7, REMARK, 12, "start", True)          # above the circle top, not on it
p2.label(0, -1.35, "&#952; a&#231;&#305;l&#305; &#305;&#351;&#305;n boyunca f = e" + sup("2i&#952;"), 0, 0, TEXT, 11, "middle", False, True)
panel_title(p2, "f de&#287;erleri")
_between(p1, 290, 112, "f(z) = z / " + BAR_Z)
OUT["analitik-fonksiyonlar-yonlere-gore-limit"] = figure(
    580, 305, [p1, p2],
    "<em>f</em>(<em>z</em>) = <em>z</em>/<em>z&#773;</em> her &#305;&#351;&#305;n &#252;zerinde sabittir ama &#305;&#351;&#305;ndan &#305;&#351;&#305;na de&#287;i&#351;ir: "
    "reel eksende 1, sanal eksende &#8722;1, k&#246;&#351;egende <em>i</em>; genel olarak &#952; a&#231;&#305;l&#305; &#305;&#351;&#305;nda "
    "<em>e</em><sup>2<em>i</em>&#952;</sup>. De&#287;erler birim &#231;ember &#252;zerinde da&#287;&#305;ld&#305;&#287;&#305;ndan "
    "<em>z</em> &#8594; 0 i&#231;in tek bir limit yoktur.",
    css_class=WIDE, aria="z bolu z eslenik fonksiyonunun farkli yonlerde farkli limit degerleri")

# ---- L3: the Riemann sphere and a neighbourhood of ∞ (side view)
def _stereo(x):
    """Image on the sphere (centre (0,1), radius 1) of the plane point (x, 0)."""
    t = 4.0 / (x * x + 4.0)
    return (x * t, 2 - 2 * t)


zpt, far = (2.8, 0.0), (-3.5, 0.0)
p = cplane(30, 30, 340, (-3.8, 3.8), (-0.6, 2.6))
p.line([(-3.7, 0), (3.7, 0)], BASE, 1.8)
disk_fill(p, 0, 1, 1, THEORY, 0.06)
p.circle(0, 1, 1, THEORY, 1.8)
p.polygon(circle_pts(0, 1, 1, PI / 6, 5 * PI / 6), THEORY, 0.18)
p.line([(-0.866, 1.5), (0.866, 1.5)], REMARK, 1.1, "4 3", 0.8)
p.line([(0, 2), zpt], PRACTICE, 1.5)
p.line([(0, 2), far], PRACTICE, 1.3, "5 4", 0.8)
dot(p, (0, 2), TEXT, 4)
dot(p, (0, 0), TEXT, 3.2)
dot(p, zpt, PRACTICE, 4)
dot(p, far, PRACTICE, 4)
dot(p, _stereo(zpt[0]), PRACTICE, 4)
dot(p, _stereo(far[0]), PRACTICE, 3.4)
p.label(0, 2, "N &#8596; &#8734;", -8, -3, TEXT, 12, "end", True)
p.label(0, 0, "O", -7, 14, TEXT, 12, "end", True, True)
p.label(*zpt, "z", 7, -5, PRACTICE, 12.5, "start", True, True)
p.label(*_stereo(zpt[0]), "z&#8242;", 9, -2, PRACTICE, 12.5, "start", True, True)
p.label(*far, "|z| b&#252;y&#252;k", -4, 15, PRACTICE, 11, "start", False, True)
p.label(*_stereo(far[0]), "N'ye yak&#305;n", -9, 3, PRACTICE, 10.5, "end", False, True)
p.label(0.65, 2.02, "|z| &gt; 1/&#949; kom&#351;ulu&#287;u", 0, 0, THEORY, 11, "start", True)
p.label(3.7, 0, "kompleks d&#252;zlem", 0, 15, BASE, 11, "end", False, True)
panel_title(p, "Riemann k&#252;resi (yandan g&#246;r&#252;n&#252;&#351;)")
OUT["analitik-fonksiyonlar-riemann-kuresi"] = figure(
    400, 224, [p],
    "D&#252;zlemdeki <em>z</em> noktas&#305;, kuzey kutbu <em>N</em> ile birle&#351;tirilerek k&#252;redeki <em>z</em>&#8242; noktas&#305;na "
    "e&#351;lenir. Mod&#252;l&#252; b&#252;y&#252;yen noktalar&#305;n g&#246;r&#252;nt&#252;leri <em>N</em>'ye y&#305;&#287;&#305;l&#305;r; bu y&#252;zden "
    "|<em>z</em>| &gt; 1/&#949; k&#252;mesi, k&#252;rede <em>N</em> = &#8734; etraf&#305;ndaki k&#252;&#231;&#252;k bir takkeye kar&#351;&#305;l&#305;k gelir "
    "ve &#8734;'un bir kom&#351;ulu&#287;u say&#305;l&#305;r.",
    aria="Riemann kuresi ve stereografik izdusum; sonsuzun komsulugu kuzey kutbu etrafinda bir takke")

# ================================================================== turev
# ---- D1: Δz → 0 along every direction and every curve
z0 = (1.9, 1.6)
p = cplane(40, 24, 320, (-0.2, 3.6), (-0.2, 3.1))
p.origin_axes(opacity=0.35)
disk_fill(p, *z0, 1.0, BASE, 0.08)
p.circle(*z0, 1.0, BASE, 1.3, "5 4")
p.arrow((3.0, z0[1]), (z0[0] + 0.06, z0[1]), THEORY, 2.0)
p.arrow((z0[0], 2.7), (z0[0], z0[1] + 0.06), PRACTICE, 2.0)
dd = 1.1 / math.sqrt(2)
tail = (z0[0] - dd, z0[1] - dd)
p.arrow(tail, (z0[0] - 0.045, z0[1] - 0.045), REMARK, 2.0)
start = (0.95, 2.45)
vx, vy = z0[0] - start[0], z0[1] - start[1]
ln = math.hypot(vx, vy)
ux, uy = vx / ln, vy / ln
wav = []
for k in range(61):
    s = k / 60
    off = 0.22 * math.sin(2 * PI * s) * (1 - s)
    wav.append((start[0] + vx * s - uy * off, start[1] + vy * s + ux * off))
p.line(wav[:-3], REMARK, 1.6, "5 4")
p.arrow(wav[-4], (z0[0] - 0.03 * ux, z0[1] - 0.03 * uy), REMARK, 1.6, head=7.0)
dot(p, z0, TEXT, 4)
p.label(*z0, "z&#8320;", 8, 14, TEXT, 12.5, "start", True, True)
p.label(2.45, z0[1], "&#916;z = &#916;x", 0, -8, THEORY, 11.5, "middle", True)
p.label(z0[0], 2.7, "&#916;z = i&#916;y", 0, -8, PRACTICE, 11.5, "middle", True)
p.label(*tail, "&#916;z = &#916;x(1 + i)", -6, 4, REMARK, 11.5, "end", True)
p.label(*start, "e&#287;ri yol", -6, 4, REMARK, 11.5, "end", True)
panel_title(p, "&#916;w/&#916;z oran&#305; her yoldan ayn&#305; limite gitmeli")
OUT["analitik-fonksiyonlar-her-yonden"] = figure(
    400, 350, [p],
    "Kompleks t&#252;revde &#916;<em>z</em>, <em>z</em><sub>0</sub>'a yaln&#305;z sa&#287;dan-soldan de&#287;il, d&#252;zlemin her "
    "y&#246;n&#252;nden ve her e&#287;ri boyunca yakla&#351;&#305;r; &#916;<em>w</em>/&#916;<em>z</em> oran&#305;n&#305;n hepsinde ayn&#305; "
    "limite gitmesi gerekir. <em>z&#773;</em> (her yerde) ve |<em>z</em>|&#178; (<em>z</em> &#8800; 0 iken) i&#231;in yatay ile dikey yakla&#351;&#305;m&#305;n farkl&#305; "
    "&#231;&#305;kmas&#305;, t&#252;revin yoklu&#287;unu g&#246;stermeye yeter.",
    aria="Delta z'nin z0 noktasina cesitli yonlerden ve bir egri boyunca yaklasmasi")

# ========================================================== cauchy-riemann
# ---- C1: horizontal and vertical approach give the two expressions of f′(z₀)
x0, y0 = 2.0, 1.5
p = cplane(40, 24, 320, (-0.5, 4.3), (-0.5, 3.3))
p.origin_axes(xticks=(x0,), yticks=(y0,), xfmt=lambda t: "x&#8320;", yfmt=lambda t: "y&#8320;")
p.line([(x0, -0.2), (x0, 2.9)], BASE, 1.0, "4 3", 0.6)
p.line([(-0.2, y0), (4.2, y0)], BASE, 1.0, "4 3", 0.6)
p.arrow((3.3, y0), (x0 + 0.07, y0), THEORY, 2.2)
p.arrow((x0, 2.8), (x0, y0 + 0.07), PRACTICE, 2.2)
dot(p, (x0, y0), TEXT, 4)
p.label(x0, y0, "z&#8320;", -8, 16, TEXT, 12.5, "end", True, True)
p.label(2.65, y0, "&#916;z = &#916;x", 0, -8, THEORY, 11.5, "middle", True)
p.label(x0 + 0.12, y0, "f&#8242;(z&#8320;) = u" + sub("x") + " + iv" + sub("x"), 0, 20, THEORY, 11.5, "start", True)
p.label(x0, 2.2, "&#916;z = i&#916;y", -8, 4, PRACTICE, 11.5, "end", True)
p.label(x0, 2.35, "f&#8242;(z&#8320;) = v" + sub("y") + " &#8722; iu" + sub("y"), 8, 4, PRACTICE, 11.5, "start", True)
p.label(4.2, 3.05, "e&#351;itlenince: u" + sub("x") + " = v" + sub("y") + ",  u" + sub("y") + " = &#8722;v" + sub("x"), 0, 0, TEXT, 11.5, "end", True)
OUT["analitik-fonksiyonlar-yatay-dikey"] = figure(
    400, 325, [p],
    "T&#252;rev her y&#246;nden ayn&#305; oldu&#287;una g&#246;re iki &#246;zel y&#246;n kar&#351;&#305;la&#351;t&#305;r&#305;labilir: yatay yakla&#351;&#305;m "
    "<em>f</em>&#8242;(<em>z</em><sub>0</sub>) = <em>u</em><sub><em>x</em></sub> + <em>iv</em><sub><em>x</em></sub>, dikey yakla&#351;&#305;m "
    "<em>f</em>&#8242;(<em>z</em><sub>0</sub>) = <em>v</em><sub><em>y</em></sub> &#8722; <em>iu</em><sub><em>y</em></sub> verir. "
    "&#304;ki ifadenin reel ve sanal k&#305;s&#305;mlar&#305;n&#305;n e&#351;itli&#287;i Cauchy-Riemann denklemleridir.",
    aria="z0 noktasina yatay ve dikey yaklasim ve turevin iki ifadesi")

# ---- C2: the cube-root branch: r > 0, α < θ < α + 2π — one ray is left out
al = 5 * PI / 4
th = PI / 3 + 2 * PI                       # θ of the sample point, measured within (α, α + 2π)
zc = polar(2.0, th)
p = cplane(40, 24, 320, (-3.4, 3.4), (-3.2, 3.2))
p.origin_axes()
p.line([(0, 0), polar(3.3, al)], PRACTICE, 3.2, None, 0.35)
spiral(p, al, al + 2 * PI - 0.12, 1.0, 1.45, THEORY, 1.7)
angle_arc(p, al, th, 0.55, PRACTICE, 1.7)
p.line([(0, 0), zc], REMARK, 1.1, "4 3", 0.7)
hollow(p, (0, 0), TEXT)
dot(p, zc, TEXT, 4)
p.label(*zc, "z = re" + sup("i&#952;"), 8, -2, TEXT, 12, "start", True)
p.label(*polar(0.8, (al + th) / 2), "&#952;", 0, 4, PRACTICE, 13, "middle", True, True)
p.label(-2.2, -2.75, "&#952; = &#945; &#305;&#351;&#305;n&#305; hari&#231;", 0, 0, PRACTICE, 11, "middle", True)
p.label(-1.35, 1.4, "&#945; &lt; &#952; &lt; &#945; + 2&#960;", 0, 0, THEORY, 11.5, "end", True)
OUT["analitik-fonksiyonlar-kup-kok-dali"] = figure(
    400, 372, [p],
    "K&#252;p k&#246;k dal&#305; <em>r</em> &gt; 0 ve &#945; &lt; &#952; &lt; &#945; + 2&#960; ko&#351;ullar&#305;yla tan&#305;ml&#305;d&#305;r: her "
    "<em>z</em>'nin a&#231;&#305;s&#305; &#952; = &#945; &#305;&#351;&#305;n&#305;ndan ba&#351;layarak saat y&#246;n&#252;n&#252;n tersine tam bir tur "
    "i&#231;inde &#246;l&#231;&#252;l&#252;r. Bu &#305;&#351;&#305;n ve ba&#351;lang&#305;&#231; noktas&#305; d&#305;&#351;ar&#305;da b&#305;rak&#305;l&#305;r; "
    "kalan a&#231;&#305;k k&#252;mede dal tek de&#287;erli ve t&#252;revlenebilirdir.",
    aria="Kup kok dalinin aci araligi ve disarida birakilan isin")

# ---- C3: differentiable on the line y = x, analytic nowhere
p = cplane(40, 24, 320, (-2.3, 2.7), (-2.3, 2.3))
p.origin_axes()
p.line([(-2.2, -2.2), (2.0, 2.0)], THEORY, 2.0)
zq = (0.8, 0.8)
disk_fill(p, *zq, 0.6, PRACTICE, 0.14)
p.circle(*zq, 0.6, PRACTICE, 1.5, "5 4")
dot(p, zq, TEXT, 4)
p.label(2.0, 2.0, "y = x", 8, 4, THEORY, 12, "start", True, True)
p.label(*zq, "z&#8320;", -8, -6, TEXT, 12.5, "end", True, True)
p.label(zq[0] + 0.6, zq[1], "her kom&#351;uluk", 7, -4, PRACTICE, 11, "start", True)
p.label(zq[0] + 0.6, zq[1], "do&#287;rudan ta&#351;ar", 7, 11, PRACTICE, 11, "start", True)
p.label(-2.2, 1.7, "do&#287;ru &#252;zerinde:", 0, 0, THEORY, 11, "start", False, True)
p.label(-2.2, 1.42, "CR sa&#287;lan&#305;r, f&#8242; = 2x", 0, 0, THEORY, 11, "start", False, True)
p.label(2.6, -1.3, "do&#287;ru d&#305;&#351;&#305;nda:", 0, 0, REMARK, 11, "end", False, True)
p.label(2.6, -1.58, "CR bozuk, t&#252;rev yok", 0, 0, REMARK, 11, "end", False, True)
panel_title(p, "analitiklik a&#231;&#305;k bir disk ister")
OUT["analitik-fonksiyonlar-dogru-uzerinde-turev"] = figure(
    400, 366, [p],
    "<em>f</em>(<em>z</em>) = <em>x</em>&#178; + <em>iy</em>&#178; i&#231;in Cauchy-Riemann denklemleri yaln&#305;z <em>y</em> = <em>x</em> "
    "do&#287;rusunda sa&#287;lan&#305;r; t&#252;rev bu do&#287;runun her noktas&#305;nda vard&#305;r. Ama analitiklik <em>z</em><sub>0</sub>'&#305;n "
    "bir <strong>kom&#351;ulu&#287;unun her noktas&#305;nda</strong> t&#252;rev ister ve her disk do&#287;rudan ta&#351;ar: "
    "<em>f</em> hi&#231;bir noktada analitik de&#287;ildir.",
    aria="y = x dogrusu uzerinde turev var, analitiklik yok: her disk dogrudan tasar")

# ============================================================== analitiklik
# ---- A1: on a disconnected set f′ = 0 does not force f to be constant
p = cplane(40, 24, 320, (-3.6, 3.6), (-1.9, 1.9))
for cx, col, txt, nm in ((-2.0, THEORY, "f &#8801; a", "D&#8321;"), (2.0, PRACTICE, "f &#8801; b &#8800; a", "D&#8322;")):
    disk_fill(p, cx, 0, 1.25, BASE, 0.14)
    p.circle(cx, 0, 1.25, THEORY, 1.5, "5 4")
    p.label(cx, 0, txt, 0, 4, col, 12.5, "middle", True)
    p.label(cx, 1.25, nm, 0, -7, THEORY, 12, "middle", True, True)
p.label(0, -1.6, "D = D&#8321; &#8746; D&#8322; ba&#287;lant&#305;l&#305; de&#287;il", 0, 0, TEXT, 11.5, "middle", False, True)
panel_title(p, "f&#8242; = 0 her yerde, ama f sabit de&#287;il")
OUT["analitik-fonksiyonlar-baglantisiz"] = figure(
    400, 226, [p],
    "&#304;ki ayr&#305;k a&#231;&#305;k diskte ayr&#305; ayr&#305; sabit olan fonksiyonun t&#252;revi her noktada s&#305;f&#305;rd&#305;r, ama "
    "<em>a</em> &#8800; <em>b</em> ise fonksiyon sabit de&#287;ildir. Sabitlik teoremindeki <strong>domen</strong> (ba&#287;lant&#305;l&#305; "
    "a&#231;&#305;k k&#252;me) ko&#351;ulu tam da bunu engeller: iki diski birle&#351;tiren, k&#252;mede kalan bir yol yoktur.",
    aria="Iki ayrik diskte farkli sabit degerler: turev sifir, fonksiyon sabit degil")

# ---- A2: constancy is carried along a polygonal path inside the domain
pts = [(1.55 * x, y) for x, y in blob(0, 0, 2.0, [(0.3, 2, 0.4), (0.22, 3, 1.9), (0.12, 5, 0.7)])]
p = cplane(40, 24, 320, (-4.2, 4.2), (-2.9, 2.9))
closed_curve(p, pts, THEORY, 1.8, fill=BASE, opacity=0.10)
path = [(-2.3, -0.9), (-0.7, 1.1), (1.0, -0.8), (1.95, 0.45)]   # every vertex > 0.36 inside the boundary
p.line(path, PRACTICE, 2.0)
p.points(path[1:-1], PRACTICE, 3.0)
dot(p, path[0], PRACTICE, 4.2)
dot(p, path[-1], PRACTICE, 4.2)
p.label(*path[0], "z&#8321;", -8, 12, PRACTICE, 12.5, "end", True, True)
p.label(*path[-1], "z&#8322;", -9, -6, PRACTICE, 12.5, "end", True, True)   # upper-left: away from the boundary
for (xa, ya), (xb, yb), dx, dy, an in ((path[0], path[1], -9, 0, "end"), (path[1], path[2], 9, -3, "start"), (path[2], path[3], 9, 10, "start")):
    p.label((xa + xb) / 2, (ya + yb) / 2, "u sabit", dx, dy, PRACTICE, 10.5, an, False, True)
p.label(*_blob_inner(0, 0, 1.55, 2.0, [(0.3, 2, 0.4), (0.22, 3, 1.9), (0.12, 5, 0.7)], 2.35, 0.5), "D", 0, 4, THEORY, 13, "middle", True, True)
panel_title(p, "her do&#287;ru par&#231;as&#305;nda du/ds = &#8711;u &#183; U = 0")
OUT["analitik-fonksiyonlar-cokgensel-yol"] = figure(
    400, 292, [p],
    "&#8711;<em>u</em> = 0 oldu&#287;undan <em>u</em>, <em>D</em> i&#231;indeki her do&#287;ru par&#231;as&#305; boyunca sabittir. "
    "<em>D</em> bir domen oldu&#287;u i&#231;in <em>z</em><sub>1</sub> ile <em>z</em><sub>2</sub>, tamamen <em>D</em>'de kalan sonlu "
    "say&#305;da par&#231;ayla birle&#351;ir; sabitlik par&#231;adan par&#231;aya ta&#351;&#305;n&#305;r ve <em>u</em>(<em>z</em><sub>1</sub>) = "
    "<em>u</em>(<em>z</em><sub>2</sub>) &#231;&#305;kar.",
    aria="Domende iki noktayi birlestiren cokgensel yol boyunca u sabit kalir")

# ===================================================== harmonik-fonksiyonlar
# ---- H1: T = e^{−y} sin x as a steady temperature in the half strip 0 < x < π, y > 0
p = cplane(40, 24, 320, (-0.7, 3.9), (-0.7, 3.3))
p.origin_axes("x", "y", xticks=(PI,), xfmt=lambda t: "&#960;")
p.polygon([(0, 0), (PI, 0), (PI, 3.3), (0, 3.3)], BASE, 0.12)
p.line([(0, 0), (0, 3.3)], THEORY, 2.2)
p.line([(PI, 0), (PI, 3.3)], THEORY, 2.2)
p.line([(0, 0), (PI, 0)], PRACTICE, 2.4)
p.line([(PI * k / 60, 0.6 * math.sin(PI * k / 60)) for k in range(61)], PRACTICE, 1.3, "4 3", 0.85)
p.arrow((PI / 2, 2.15), (PI / 2, 3.0), REMARK, 1.8)
p.label(0, 1.7, "T = 0", -8, 4, THEORY, 11.5, "end", True)
p.label(PI, 1.7, "T = 0", 8, 4, THEORY, 11.5, "start", True)
p.label(PI / 2, 0, "y = 0: T = sin x", 0, 16, PRACTICE, 11.5, "middle", True)
p.label(PI / 2, 0.6, "sin x", 0, -6, PRACTICE, 10.5, "middle", False, True)
p.label(PI / 2, 2.6, "y &#8594; &#8734;: T &#8594; 0", 8, 4, REMARK, 11.5, "start", True)
panel_title(p, "T = e" + sup("&#8722;y") + " sin x: yar&#305; &#351;eritte dura&#287;an s&#305;cakl&#305;k")
OUT["analitik-fonksiyonlar-yari-serit"] = figure(
    400, 346, [p],
    "Harmonik <em>T</em> = <em>e</em><sup>&#8722;<em>y</em></sup> sin <em>x</em>, yar&#305; &#351;eritte durağan s&#305;cakl&#305;k da&#287;&#305;l&#305;m&#305;d&#305;r: "
    "dikey kenarlarda <em>T</em> = 0, taban &#252;zerinde <em>T</em> = sin <em>x</em> (kesikli profil) ve "
    "<em>y</em> &#8594; &#8734; iken <em>T</em> &#8594; 0. Bu s&#305;n&#305;r de&#287;erlerini sa&#287;layan bir Laplace &#231;&#246;z&#252;m&#252;d&#252;r.",
    aria="Yari seritte sicaklik dagiliminin sinir degerleri")

# ============================================= analitik-uzanim-ve-yansima
# ---- U1: chain of disks carrying f ≡ 0 from z₀ to P
DW = [(0.22, 2, 0.9), (0.18, 3, 2.4), (0.1, 5, 0.3)]
pts = [(-1.0 + 1.55 * (x + 1.0), y) for x, y in blob(-1.0, 0, 2.3, DW)]
p = cplane(30, 30, 340, (-5.0, 3.2), (-3.0, 3.0))
closed_curve(p, pts, THEORY, 1.8)
zs = [(-2.7, -0.35), (-1.85, 0.3), (-1.0, -0.25), (-0.15, 0.4)]
d = 1.25                                    # = distance from the path to the boundary: N0 is tangent to it (at the bottom)
disk_fill(p, *zs[0], d, PRACTICE, 0.08)
for zk in zs:
    p.circle(*zk, d, THEORY, 1.2, "5 4", opacity=0.7)
p.polygon(blob(*zs[0], 0.32, [(0.05, 3, 0.5)]), PRACTICE, 0.28, PRACTICE, 1.2)
# the radius is drawn at 150° (d = disk radius, as in the proof); the tangency itself is straight below z0,
# but a segment there leaves no room inside N0 for the "f ≡ 0" label (checked: < 3 px clearance everywhere)
rp = (zs[0][0] + d * math.cos(math.radians(150)), zs[0][1] + d * math.sin(math.radians(150)))
p.line([zs[0], rp], PRACTICE, 1.2)
p.label((zs[0][0] + rp[0]) / 2, (zs[0][1] + rp[1]) / 2, "d", 0, -6, PRACTICE, 12.5, "middle", True, True)
p.label(-2.7, -1.3, "f &#8801; 0", 0, 0, PRACTICE, 11, "middle", True, True)
p.line(zs, TEXT, 1.5)
for zk in zs:
    dot(p, zk, TEXT, 3.6)
# point labels sit in the gaps between the dashed arcs (checked numerically: > 9 px from every curve)
p.label(*zs[0], "z&#8320;", -22, 10, TEXT, 12, "end", True, True)
p.label(*zs[1], "z&#8321;", -22, -2, TEXT, 12, "end", True, True)
p.label(*zs[2], "z&#8322;", 22, 10, TEXT, 12, "start", True, True)
p.label(*zs[3], "P", 8, -4, TEXT, 12, "start", True, True)
p.label(-3.5, 1.1, "N&#8320;", 0, 0, THEORY, 11.5, "middle", True, True)
p.label(zs[1][0], zs[1][1] + d, "N&#8321;", 0, -6, THEORY, 11.5, "middle", True, True)
p.label(zs[2][0], zs[2][1] - d, "N&#8322;", 0, 14, THEORY, 11.5, "middle", True, True)
p.label(zs[3][0] + d, zs[3][1], "N&#8323;", 6, 4, THEORY, 11.5, "start", True, True)
p.label(*_blob_inner(-1.0, 0, 1.55, 2.3, DW, -0.5, 0.5), "D", 0, 4, THEORY, 13, "middle", True, True)   # lower-right lobe: 48 px from every dashed arc
panel_title(p, "z" + sub("k+1") + " &#8712; N" + sub("k") + ": s&#305;f&#305;r diskten diske ge&#231;er")
OUT["analitik-fonksiyonlar-disk-zinciri"] = figure(
    400, 327, [p],
    "<em>f</em>, <em>z</em><sub>0</sub> etraf&#305;ndaki k&#252;&#231;&#252;k alt domende s&#305;f&#305;rd&#305;r. &#199;okgensel yol &#252;zerinde "
    "ard&#305;&#351;&#305;k uzakl&#305;klar&#305; <em>d</em>'den k&#252;&#231;&#252;k noktalar se&#231;ilir; her <em>N</em><sub><em>k</em></sub> diski "
    "<em>D</em>'nin i&#231;inde kal&#305;r ve bir sonraki merkezi i&#231;erir (<em>d</em>: yolun <em>D</em>'nin s&#305;n&#305;r&#305;na uzakl&#305;&#287;&#305;). Yerel ger&#231;ek <em>N</em><sub>0</sub>'da <em>f</em> &#8801; 0 verir, "
    "kesi&#351;im &#252;zerinden <em>N</em><sub>1</sub>'e, oradan <em>N</em><sub>2</sub>'ye ge&#231;er ve <em>P</em>'ye ula&#351;&#305;r.",
    aria="Ozdes sifir olma ilkesinin kaniti: cokgensel yol boyunca ust uste binen disk zinciri")

# ---- U2: continuation of z^{1/2} around the origin returns with the opposite sign
r_in, r_out = 0.8, 3.0                     # hole radius 39 px: the "z = 0" label (ends at ~33 px) stays inside it
p = cplane(40, 24, 320, (-3.3, 3.3), (-3.3, 3.3))
doms = ((10, 170, THEORY, "D&#8321;, f&#8321;"), (130, 290, REMARK, "D&#8322;, f&#8322;"), (250, 410, PRACTICE, "D&#8323;, f&#8323;"))
for a0, a1, col, nm in doms:
    r0, r1 = math.radians(a0), math.radians(a1)
    p.polygon(circle_pts(0, 0, r_out, r0, r1) + circle_pts(0, 0, r_in, r1, r0), col, 0.12, col, 1.4)
    p.label(*polar(1.65, (r0 + r1) / 2), nm, 0, 4, col, 12, "middle", True, True)
hollow(p, (0, 0), TEXT)
p.label(0, 0, "z = 0", 7, 4, TEXT, 10.5, "start", True, False)   # explicit: a lone serif "0" reads like an "o" next to the hollow marker
spiral(p, math.radians(75), math.radians(75 + 335), 1.05, 1.05, TEXT, 1.6)
p.label(*polar(2.25, math.radians(150)), "f&#8322; = f&#8321;", 0, 4, TEXT, 11, "middle", True)
p.label(*polar(2.25, math.radians(270)), "f&#8323; = f&#8322;", 0, 4, TEXT, 11, "middle", True)
p.label(*polar(2.25, math.radians(30)), "f&#8323; = &#8722;f&#8321; !", 0, 4, PRACTICE, 11, "middle", True)
panel_title(p, "z" + sup("1/2") + " dal&#305; ba&#351;lang&#305;&#231; etraf&#305;nda bir tur uzat&#305;l&#305;nca")
OUT["analitik-fonksiyonlar-uzanim-zinciri"] = figure(
    400, 392, [p],
    "<em>f</em><sub>1</sub>, <em>D</em><sub>1</sub>'de <em>z</em><sup>1/2</sup>'nin bir dal&#305; olsun. <em>D</em><sub>2</sub>'ye, oradan "
    "<em>D</em><sub>3</sub>'e uzat&#305;l&#305;p ba&#351;lang&#305;&#231; noktas&#305;n&#305;n etraf&#305;nda tam tur d&#246;n&#252;l&#252;nce "
    "<em>D</em><sub>3</sub> &#8745; <em>D</em><sub>1</sub> kesi&#351;iminde <em>f</em><sub>3</sub> = &#8722;<em>f</em><sub>1</sub> bulunur: "
    "her ad&#305;mda kom&#351;u uzan&#305;mlar &#231;ak&#305;&#351;&#305;r ama zincirin sonu ba&#351;&#305;yla &#231;ak&#305;&#351;mak zorunda de&#287;ildir.",
    aria="Baslangic etrafinda uc domen zinciri; karekok dali tam turda isaret degistirir")

# ---- U3: the reflection principle — a domain symmetric about the real axis
p = cplane(40, 24, 320, (-4.0, 4.0), (-2.4, 2.4))
p.origin_axes()
ell = [(3.0 * math.cos(2 * PI * k / 120), 1.75 * math.sin(2 * PI * k / 120)) for k in range(120)]
closed_curve(p, ell, THEORY, 1.8, fill=BASE, opacity=0.10)
p.line([(-3.0, 0), (3.0, 0)], PRACTICE, 3.2, None, 0.5)
p.label(-1.6, 0, "f(x) reel", 0, 16, PRACTICE, 11.5, "middle", True)
zr, zrb = (1.5, 1.0), (1.5, -1.0)
p.line([zr, zrb], BASE, 1.1, "4 3", 0.7)
dot(p, zr, TEXT, 4)
dot(p, zrb, TEXT, 4)
p.label(*zr, "z", 8, 4, TEXT, 12.5, "start", True, True)
p.label(*zrb, BAR_Z, 8, 5, TEXT, 12.5, "start", True, True)
p.label(-2.3, 0.55, "D", 0, 0, THEORY, 13, "middle", True, True)
p.label(3.9, -2.1, "f(" + BAR_Z + ") = <tspan text-decoration=\"overline\">f(z)</tspan>", 0, 0, REMARK, 11.5, "end", True)
panel_title(p, "D reel eksene g&#246;re simetrik: z &#8712; D &#8660; " + BAR_Z + " &#8712; D")
OUT["analitik-fonksiyonlar-yansima"] = figure(
    400, 264, [p],
    "Yans&#305;ma prensibinin sahnesi: <em>D</em> reel eksene g&#246;re simetrik bir domendir ve eksenin bir par&#231;as&#305;n&#305; i&#231;erir. "
    "<em>f</em> bu par&#231;ada reel de&#287;er al&#305;yorsa, <em>z</em>'nin yans&#305;mas&#305; <em>z&#773;</em>'de fonksiyonun de&#287;eri "
    "<em>f</em>(<em>z</em>)'nin yans&#305;mas&#305;d&#305;r: <em>f</em>(<em>z&#773;</em>) = <span style=\"text-decoration:overline\"><em>f</em>(<em>z</em>)</span>.",
    aria="Reel eksene gore simetrik domen; z ve eslenigi, eksende f reel")

# ############################################################################
# PART: Elemanter Fonksiyonlar
# ############################################################################

# ############################################################################
# PART: Elemanter Fonksiyonlar
# ############################################################################
PHI, RHO, ALPHA, THETA_U, NOTIN = "&#966;", "&#961;", "&#945;", "&#920;", "&#8713;"
SQRT, ARROW, MAPSTO = "&#8730;", "&#8594;", "&#8594;"


def esup(s):
    """'e' with a superscript exponent, e.g. esup('z') -> e^z."""
    return "e" + sup(s)


# ============================================================ üstel-fonksiyon
# ---- E1: w = e^z sends vertical lines to circles and horizontal lines to rays
c1, c2 = 1.0, PI / 4
pz = cplane(24, 30, 236, (-1.2, 2.6), (-1.2, 2.3))
pz.origin_axes()
pz.line([(c1, -1.15), (c1, 2.05)], THEORY, 2.0)
pz.line([(-1.15, c2), (2.55, c2)], PRACTICE, 2.0)
dot(pz, (c1, c2), BASE, 4.2)
pz.label(c1, 2.05, "x = c" + SUB1, 7, -4, THEORY, 12, "start", True, True)
pz.label(2.55, c2, "y = c" + SUB2, -2, -7, PRACTICE, 12, "end", True, True)
pz.label(c1, c2, "z" + SUB0, 8, 15, BASE, 12.5, "start", True, True)
panel_title(pz, "z-d&#252;zlemi")

pw = cplane(314, 30, 236, (-3.5, 3.5), (-3.5, 3.5))
pw.origin_axes(xlabel="u", ylabel="v")
pw.circle(0, 0, math.e, THEORY, 2.0)
pw.line([(0, 0), (3.3, 3.3)], PRACTICE, 2.0)
pw.sector(0, 0, 0.8, 0, c2, PRACTICE, 0.16)
pw.arc(0, 0, 0.8, 0, c2, PRACTICE, 1.3)
w0 = polar(math.e, c2)
dot(pw, w0, BASE, 4.2)
hollow(pw, (0, 0), TEXT, 3.4)
pw.label(-1.15, -1.3, "|w| = " + esup("c" + SUB1), 0, 0, THEORY, 12, "middle", True, True)
pw.label(2.5, 3.2, "arg w = c" + SUB2, 0, 0, PRACTICE, 12, "end", True, True)
pw.label(0.95, 0.28, "c" + SUB2, 0, 0, PRACTICE, 11.5, "start", True, True)
pw.label(*w0, "w" + SUB0, 10, -2, BASE, 12.5, "start", True, True)
pw.label(0, 0, "0 al&#305;nmaz", 8, 16, TEXT, 10.5, "start", False, True)
panel_title(pw, "w-d&#252;zlemi: w" + SUB0 + " = " + esup("z" + SUB0))
pw.text_px(287, 150, "w = " + esup("z"), TEXT, 12.5, "middle", True)
pw.text_px(287, 172, ARROW, TEXT, 18, "middle", True)
OUT["elemanter-fonksiyonlar-ustel-dogru-cember"] = figure(
    574, 278, [pz, pw],
    "|<em>e<sup>z</sup></em>| = <em>e<sup>x</sup></em> ve arg <em>e<sup>z</sup></em> = <em>y</em>: reel k&#305;s&#305;m "
    "yar&#305;&#231;ap&#305;, sanal k&#305;s&#305;m a&#231;&#305;y&#305; belirler. Dikey do&#287;ru <em>x</em> = <em>c</em><sub>1</sub> "
    "&#231;ember |<em>w</em>| = <em>e</em><sup><em>c</em><sub>1</sub></sup> &#252;zerine, yatay do&#287;ru <em>y</em> = <em>c</em><sub>2</sub> "
    "arg <em>w</em> = <em>c</em><sub>2</sub> &#305;&#351;&#305;n&#305; &#252;zerine gider; kesi&#351;imleri <em>z</em><sub>0</sub> "
    "&#8614; <em>w</em><sub>0</sub> olur. Her pozitif yar&#305;&#231;ap bir <em>e<sup>x</sup></em> de&#287;eriyle "
    "elde edilir; yaln&#305;z 0 hi&#231;bir &#231;ember &#252;zerinde de&#287;ildir.",
    css_class=WIDE, aria="w = e^z altinda dikey dogru cembere, yatay dogru isina gider")

# ---- E2: the plane is sliced into horizontal strips of height 2π
p = cplane(40, 24, 320, (-5.8, 5.8), (-5.4, 10.6))
p.polygon([(-5.8, -PI), (5.8, -PI), (5.8, PI), (-5.8, PI)], THEORY, 0.12)
p.origin_axes()
for yv in (-PI, PI, 3 * PI):
    p.line([(-5.8, yv), (5.8, yv)], REMARK, 1.2, "5 4", 0.7)
for yv, lab in ((-PI, MINUS + PI_S), (PI, PI_S), (3 * PI, "3" + PI_S)):
    p.add(f'<line x1="{p.X(0)-3:.1f}" y1="{p.Y(yv):.1f}" x2="{p.X(0)+3:.1f}" y2="{p.Y(yv):.1f}" stroke="{TEXT}" stroke-width="1" opacity="0.7"/>')
    p.label(0, yv, lab, -7, -5, TEXT, 11, "end")
z0 = (2.0, 1.6)
ladder = [(z0[0], z0[1] - 2 * PI), z0, (z0[0], z0[1] + 2 * PI)]
p.line([ladder[0], ladder[-1]], PRACTICE, 1.1, "2 4", 0.8)
for pt in ladder:
    dot(p, pt, PRACTICE, 4.0)
p.label(*ladder[1], "z" + SUB0, 9, 4, PRACTICE, 12.5, "start", True, True)
p.label(*ladder[2], "z" + SUB0 + " + 2" + PI_S + "i", 9, 4, PRACTICE, 12.5, "start", True, True)
p.label(*ladder[0], "z" + SUB0 + " " + MINUS + " 2" + PI_S + "i", 9, 4, PRACTICE, 12.5, "start", True, True)
p.label(5.6, -2.3, MINUS + PI_S + " &lt; y " + LEQ + " " + PI_S, 0, 0, THEORY, 12, "end", True, True)
p.label(-0.5, 5.4, esup("z" + SUB0 + MINUS + "2" + PI_S + "i") + " = " + esup("z" + SUB0) + " = " + esup("z" + SUB0 + "+2" + PI_S + "i"),
        0, 0, PRACTICE, 11.5, "end", True)
OUT["elemanter-fonksiyonlar-ustel-seritler"] = figure(
    400, 512, [p],
    "<em>e</em><sup><em>z</em> + 2&#960;<em>i</em></sup> = <em>e<sup>z</sup></em>: <em>z</em><sub>0</sub> noktas&#305;n&#305; "
    "dikey y&#246;nde 2&#960; kayd&#305;rmak de&#287;eri de&#287;i&#351;tirmez. D&#252;zlem, 2&#960; y&#252;ksekli&#287;inde "
    "yatay &#351;eritlere b&#246;l&#252;n&#252;r; her &#351;erit ayn&#305; de&#287;er k&#252;mesini &#252;retir. "
    "Taral&#305; &#351;erit &#8722;&#960; &lt; <em>y</em> &#8804; &#960;, logaritman&#305;n esas de&#287;erinin "
    "(Log <em>z</em>) ya&#351;ad&#305;&#287;&#305; b&#246;lgedir.",
    aria="Ustel fonksiyonun 2 pi yuksekligindeki yatay periyot seritleri")

# ---- E3: e^z = w — one point in the w-plane, a vertical ladder of solutions in the z-plane
rho, phi = 3.3, PI / 4
lnrho = math.log(rho)
pz = cplane(24, 30, 180, (-2.6, 6.4), (-6.4, 8.6))
pz.origin_axes()
pz.line([(lnrho, -6.3), (lnrho, 8.4)], REMARK, 1.2, "5 4", 0.7)
sols = [(lnrho, phi + 2 * PI * n) for n in (-1, 0, 1)]
for pt in sols:
    dot(pz, pt, THEORY, 4.0)
pz.label(*sols[1], PHI, 9, 4, THEORY, 12, "start", True, True)
pz.label(*sols[2], PHI + " + 2" + PI_S, 9, 4, THEORY, 12, "start", True, True)
pz.label(*sols[0], PHI + " " + MINUS + " 2" + PI_S, 9, 4, THEORY, 12, "start", True, True)
pz.arrow((-1.3, sols[1][1] + 0.35), (-1.3, sols[2][1] - 0.35), PRACTICE, 1.4, head=7)
pz.arrow((-1.3, sols[2][1] - 0.35), (-1.3, sols[1][1] + 0.35), PRACTICE, 1.4, head=7)
pz.label(-1.5, (sols[1][1] + sols[2][1]) / 2, "2" + PI_S, 0, 4, PRACTICE, 12, "end", True)
pz.label(lnrho, -6.4, "x = ln " + RHO, -6, 15, REMARK, 11.5, "start", False, True)
panel_title(pz, "z-d&#252;zlemi: &#231;&#246;z&#252;mler")

pw = cplane(300, 65, 230, (-3.9, 3.9), (-3.9, 3.9))
pw.origin_axes(xlabel="u", ylabel="v")
pw.circle(0, 0, rho, REMARK, 1.1, "4 3", opacity=0.6)
w = polar(rho, phi)
pw.sector(0, 0, 0.9, 0, phi, THEORY, 0.16)
pw.arc(0, 0, 0.9, 0, phi, THEORY, 1.3)
pw.line([(0, 0), w], THEORY, 1.4, None, 0.8)
dot(pw, w, PRACTICE, 4.2)
pw.label(*w, "w = " + RHO + esup("i" + PHI), 8, -4, PRACTICE, 12.5, "start", True, True)
pw.label(w[0] / 2, w[1] / 2, RHO, -9, -2, THEORY, 12.5, "end", True, True)
pw.label(1.05, 0.3, PHI, 0, 0, THEORY, 12, "start", True, True)
panel_title(pw, "w-d&#252;zlemi")
pw.text_px(252, 168, "w = " + esup("z"), TEXT, 12.5, "middle", True)
pw.text_px(252, 190, ARROW, TEXT, 18, "middle", True)
OUT["elemanter-fonksiyonlar-ustel-cozum-merdiveni"] = figure(
    560, 378, [pz, pw],
    "<em>e<sup>z</sup></em> = <em>w</em> denkleminin &#231;&#246;z&#252;m&#252;: mod&#252;l e&#351;itli&#287;i "
    "<em>x</em> = ln <em>&#961;</em> dikey do&#287;rusunu, arg&#252;man e&#351;itli&#287;i <em>y</em> = <em>&#966;</em> + 2<em>n</em>&#960; "
    "basamaklar&#305;n&#305; verir. Tek bir <em>w</em> de&#287;eri, ayn&#305; dikey do&#287;ru &#252;zerinde 2&#960; aral&#305;klarla "
    "dizilmi&#351; sonsuz bir &#231;&#246;z&#252;m merdiveninden gelir; bu merdiven bir sonraki b&#246;l&#252;mde "
    "log <em>w</em> olacakt&#305;r.",
    css_class=WIDE, aria="e^z = w denkleminin dikey dogru uzerinde 2 pi aralikli sonsuz cozumu")

# ================================================================ logaritma
# ---- L1: a branch of log z — the ray θ = α is cut out, θ sweeps the open interval (α, α + 2π)
alpha = 3 * PI / 4
p = cplane(40, 24, 320, (-2.6, 2.6), (-2.6, 2.6))
p.origin_axes()
p.line([(0, 0), polar(3.6, alpha)], PRACTICE, 3.4, None, 0.45)
p.sector(0, 0, 0.55, 0, alpha, REMARK, 0.16)
p.arc(0, 0, 0.55, 0, alpha, REMARK, 1.3)
spiral(p, alpha + 0.12, alpha + 2 * PI - 0.12, 1.2, 1.2, THEORY, 1.8)
hollow(p, (0, 0), PRACTICE, 3.6)
p.label(0.36, 0.5, ALPHA, 0, 0, REMARK, 12, "start", True, True)
p.label(-1.9, 2.35, "dal kesimi", 0, 0, PRACTICE, 11.5, "start", True)
p.label(-1.9, 2.13, THETA + " = " + ALPHA, 0, 0, PRACTICE, 11.5, "start", False, True)
p.label(-1.4, 0.55, THETA + " " + ARROW + " " + ALPHA + sup("+"), 0, 0, THEORY, 11.5, "end", False, True)
p.label(-0.12, 1.72, THETA + " " + ARROW + " (" + ALPHA + " + 2" + PI_S + ")" + sup(MINUS), 0, 0, THEORY, 11.5, "end", False, True)
p.label(2.5, -2.42, "z = 0: dallanma noktas&#305;", 0, 0, PRACTICE, 10.5, "end", False, True)
p.label(2.5, -2.12, ALPHA + " &lt; " + THETA + " &lt; " + ALPHA + " + 2" + PI_S, 0, 0, THEORY, 12, "end", True, True)
OUT["elemanter-fonksiyonlar-log-dal-kesimi"] = figure(
    400, 392, [p],
    "Bir dal se&#231;mek, d&#252;zlemden bir &#305;&#351;&#305;n &#231;&#305;karmakt&#305;r: <em>&#952;</em> = <em>&#945;</em> &#305;&#351;&#305;n&#305; "
    "at&#305;l&#305;nca a&#231;&#305; kalan b&#246;lgede <em>&#945;</em> ile <em>&#945;</em> + 2&#960; aras&#305;nda tek de&#287;erli ve "
    "s&#252;rekli se&#231;ilebilir. Kesimin iki yakas&#305;nda a&#231;&#305; <em>&#945;</em>'ya ve <em>&#945;</em> + 2&#960;'ye "
    "yakla&#351;&#305;r: 2&#960;'lik fark, &#305;&#351;&#305;n&#305;n neden at&#305;lmak zorunda oldu&#287;unu g&#246;sterir. "
    "T&#252;m &#305;&#351;&#305;nlar&#305;n ortak ucu, dallanma noktas&#305; <em>z</em> = 0'd&#305;r.",
    aria="Logaritmanin bir dali: alfa isini kesilir, aci alfa ile alfa + 2 pi arasinda kalir")

# ---- L2: the principal branch — cut along the negative real axis, jump of 2π across it
p = cplane(40, 24, 320, (-3.0, 2.0), (-1.9, 1.9))
p.origin_axes()
p.line([(-2.95, 0), (0, 0)], REMARK, 3.4, None, 0.45)
angle_arc(p, 0, PI - 0.07, 0.62, THEORY, 1.8)
angle_arc(p, 0, -PI + 0.07, 0.42, PRACTICE, 1.8)
za, zb = (-1.6, 0.42), (-1.6, -0.42)
p.arrow(za, (-1.6, 0.07), THEORY, 1.5, head=6.5)
p.arrow(zb, (-1.6, -0.07), PRACTICE, 1.5, head=6.5)
dot(p, za, THEORY, 3.8)
dot(p, zb, PRACTICE, 3.8)
hollow(p, (0, 0), PRACTICE, 3.6)
p.label(*za, "Im Log z " + ARROW + " " + PI_S, 0, -9, THEORY, 11.5, "middle", True)
p.label(*zb, "Im Log z " + ARROW + " " + MINUS + PI_S, 0, 17, PRACTICE, 11.5, "middle", True)
p.label(-2.95, 0, "dal kesimi", 0, -8, REMARK, 11, "start", False, True)
p.label(0, 0, "dallanma noktas&#305;", 8, 45, PRACTICE, 10.5, "start", False, True)
p.label(0.5, 0.52, THETA_U, 0, 0, THEORY, 12, "start", True, True)
p.label(1.95, 1.6, MINUS + PI_S + " &lt; " + THETA_U + " &lt; " + PI_S, 0, 0, THEORY, 12, "end", True, True)
p.label(1.95, -1.6, "Log z = ln r + i" + THETA_U, 0, 0, TEXT, 11.5, "end", False, True)
OUT["elemanter-fonksiyonlar-log-esas-kesim"] = figure(
    400, 316, [p],
    "Esas dal Log <em>z</em> negatif reel ekseni atar. Eksene &#252;stten yakla&#351;an noktalarda "
    "Im Log <em>z</em> &#960;'ye, alttan yakla&#351;anlarda &#8722;&#960;'ye gider: kesim &#252;zerinde de&#287;er "
    "2&#960;<em>i</em> kadar s&#305;&#231;rar, s&#252;reklilik ve analitiklik orada kurtar&#305;lamaz. "
    "Dallanma noktas&#305; <em>z</em> = 0, kesimin ucudur.",
    aria="Esas dal: negatif reel eksen kesimi ve kesim uzerindeki 2 pi i sicramasi")

# ============================================================ kompleks-üsler
# ---- K1: Arg z2 + Arg z3 = −π lands outside (−π, π] — the source of the e^{2π} factor
z2, z3, z23 = (1.0, -1.0), (-1.0, -1.0), (-2.0, 0.0)
p = cplane(40, 24, 300, (-2.6, 1.9), (-1.55, 1.35))
p.origin_axes()
angle_arc(p, 0, -PI / 4, 0.5, THEORY, 1.7)
angle_arc(p, 0, -3 * PI / 4, 0.8, BASE, 1.7)
angle_arc(p, 0, PI - 0.05, 1.1, PRACTICE, 1.9)
p.line([(0, 0), z2], THEORY, 1.3, None, 0.6)
p.line([(0, 0), z3], BASE, 1.3, None, 0.6)
p.line([(0, 0), z23], PRACTICE, 1.3, None, 0.6)
dot(p, z2, THEORY, 4.0); dot(p, z3, BASE, 4.0); dot(p, z23, PRACTICE, 4.2)
p.label(*z2, "z" + SUB2 + " = 1 " + MINUS + " i", 0, 17, THEORY, 12, "middle", True)
p.label(*z3, "z" + SUB3 + " = " + MINUS + "1 " + MINUS + " i", 0, 17, BASE, 12, "middle", True)
p.label(*z23, "z" + SUB2 + "z" + SUB3 + " = " + MINUS + "2", 0, -10, PRACTICE, 12, "middle", True)
p.label(0.9, -0.1, MINUS + PI_S + "/4", 0, 0, THEORY, 11, "start", True)
p.label(-0.25, -1.05, MINUS + "3" + PI_S + "/4", 0, 0, BASE, 11, "middle", True)
p.label(-0.88, 0.9, PI_S, 0, 0, PRACTICE, 12, "end", True)
lx, ly = 362, 24 + 46
p.text_px(lx, ly, "Arg z" + SUB2 + " = " + MINUS + PI_S + "/4", THEORY, 12, "start", True)
p.text_px(lx, ly + 22, "Arg z" + SUB3 + " = " + MINUS + "3" + PI_S + "/4", BASE, 12, "start", True)
p.text_px(lx, ly + 48, "toplam = " + MINUS + PI_S + " " + NOTIN + " (" + MINUS + PI_S + ", " + PI_S + "]", TEXT, 12, "start", True)
p.text_px(lx, ly + 70, "Arg(z" + SUB2 + "z" + SUB3 + ") = " + PI_S + " = " + MINUS + PI_S + " + 2" + PI_S, PRACTICE, 12, "start", True)
p.text_px(lx, ly + 100, "|z" + sup("i") + "| = " + esup(MINUS + "Arg z") + " oldu&#287;undan", TEXT, 11, "start", False, True)
p.text_px(lx, ly + 118, "|z" + SUB2 + sup("i") + "z" + SUB3 + sup("i") + "| = " + esup(PI_S + "/4") + "&#183;" + esup("3" + PI_S + "/4") + " = " + esup(PI_S), TEXT, 11.5, "start")
p.text_px(lx, ly + 136, "|(z" + SUB2 + "z" + SUB3 + ")" + sup("i") + "| = " + esup(MINUS + PI_S), TEXT, 11.5, "start")
p.text_px(lx, ly + 156, "fark 2" + PI_S + " " + ARROW + " &#231;arpan " + esup("2" + PI_S), TEXT, 11.5, "start", True)
OUT["elemanter-fonksiyonlar-usler-arg-tasma"] = figure(
    574, 296, [p],
    "<em>z</em><sub>2</sub> ve <em>z</em><sub>3</sub>'&#252;n esas arg&#252;manlar&#305; toplan&#305;nca &#8722;&#960; "
    "&#231;&#305;kar; bu de&#287;er (&#8722;&#960;, &#960;] aral&#305;&#287;&#305;n&#305;n tam d&#305;&#351;&#305;ndad&#305;r ve "
    "&#231;arp&#305;m&#305;n esas arg&#252;man&#305; &#960; olur. <em>i</em> kuvveti al&#305;n&#305;rken a&#231;&#305;lar "
    "<em>i</em>&#183;<em>i</em> = &#8722;1 ile reel &#252;sse d&#246;n&#252;&#351;t&#252;&#287;&#252;nden 2&#960;'lik d&#252;zeltme "
    "<em>e</em><sup>2&#960;</sup> &#231;arpan&#305; olarak ortaya &#231;&#305;kar.",
    css_class=WIDE, aria="Esas argumanlarin toplami -pi araligin disina tasar; sonuc e^(2 pi) carpani")

# ---- K2: (−1)^{1/π} = e^{i(2n+1)} — infinitely many values on the unit circle, never repeating
p = cplane(24, 24, 300, (-1.55, 1.55), (-1.55, 1.55))
p.origin_axes()
p.circle(0, 0, 1, BASE, 1.6)
angs = [2 * n + 1 for n in range(-3, 5)]         # −5, −3, −1, 1, 3, 5, 7, 9
for a in angs:
    dot(p, polar(1, a), PRACTICE if a == 1 else THEORY, 3.8)
spiral(p, 1.0 + 0.06, 3.0 - 0.06, 1.38, 1.38, PRACTICE, 1.6)
hollow(p, (1, 0), BASE, 3.6)
lab = {1: ("e" + sup("i"), 10, 0, "start"), 3: ("e" + sup("3i"), -8, -6, "end"), 5: ("e" + sup("5i"), 6, 16, "start"),
       7: ("e" + sup("7i"), 10, 6, "start"), -1: ("e" + sup(MINUS + "i"), 10, 8, "start")}
for a, (s, dx, dy, an) in lab.items():
    p.label(*polar(1, a), s, dx, dy, PRACTICE if a == 1 else THEORY, 12, an, True)
p.label(*polar(1.38, 2.0), "2 rad", -2, -7, PRACTICE, 11.5, "middle", True, True)
p.label(1, 0, "1", 8, 15, BASE, 11.5, "start", True, True)
lx, ly = 344, 24 + 74
p.text_px(lx, ly, "(" + MINUS + "1)" + sup("1/" + PI_S) + " = " + esup("i(2n+1)"), TEXT, 12.5, "start", True)
p.text_px(lx, ly + 18, "n = 0, &#177;1, &#177;2, &#8230;", TEXT, 11, "start", False, True)
p.text_px(lx, ly + 48, "ard&#305;&#351;&#305;k de&#287;erler aras&#305;nda", PRACTICE, 11.5, "start", True)
p.text_px(lx, ly + 64, "a&#231;&#305; fark&#305; 2 radyan", PRACTICE, 11.5, "start", True)
p.text_px(lx, ly + 94, "2/(2" + PI_S + ") = 1/" + PI_S + " irrasyonel:", TEXT, 11.5, "start")
p.text_px(lx, ly + 110, "noktalar hi&#231; &#231;ak&#305;&#351;maz,", TEXT, 11.5, "start")
p.text_px(lx, ly + 126, "&#231;ember hi&#231; kapanmaz.", TEXT, 11.5, "start")
p.text_px(lx, ly + 156, "1 de&#287;eri hi&#231; al&#305;nmaz", BASE, 11, "start", False, True)
p.text_px(lx, ly + 172, "(2n + 1 = 2" + PI_S + "k olamaz)", BASE, 11, "start", False, True)
OUT["elemanter-fonksiyonlar-usler-birim-cember"] = figure(
    540, 348, [p],
    "(&#8722;1)<sup>1/&#960;</sup> k&#252;mesinin de&#287;erleri <em>e</em><sup><em>i</em>(2<em>n</em>+1)</sup>: hepsi "
    "birim &#231;ember &#252;zerindedir ve her ad&#305;mda a&#231;&#305; 2 radyan artar. 2, 2&#960; ile "
    "&#246;l&#231;&#252;lemedi&#287;inden noktalar bir d&#252;zg&#252;n &#231;okgen gibi kapanmaz; sonsuz &#231;oktur ve "
    "hi&#231;biri bir &#246;ncekiyle &#231;ak&#305;&#351;maz.",
    css_class=WIDE, aria="(-1)^(1/pi) degerleri birim cember uzerinde 2 radyan adimlarla, asla kapanmaz")

# ==================================================== trigonometrik-fonksiyonlar
# ---- T1: zeros of sin z on the real axis; solutions of sin z = 2 above and below it
Y2 = math.log(2 + math.sqrt(3))            # ≈ 1,317
p = cplane(30, 24, 340, (-0.9, 3 * PI + 0.9), (-2.3, 2.3))
p.origin_axes()
for yv in (Y2, -Y2):
    p.line([(-0.85, yv), (3 * PI + 0.85, yv)], REMARK, 1.1, "5 4", 0.65)
for xv, lab in ((PI / 2, PI_S + "/2"), (PI, PI_S), (2 * PI, "2" + PI_S), (5 * PI / 2, "5" + PI_S + "/2"), (3 * PI, "3" + PI_S)):
    p.add(f'<line x1="{p.X(xv):.1f}" y1="{p.Y(0)-3:.1f}" x2="{p.X(xv):.1f}" y2="{p.Y(0)+3:.1f}" stroke="{TEXT}" stroke-width="1" opacity="0.7"/>')
    p.label(xv, 0, lab, 0, 15, TEXT, 11, "middle")
for n in range(4):
    dot(p, (n * PI, 0), THEORY, 4.0)
for xv in (PI / 2, 5 * PI / 2):
    for yv in (Y2, -Y2):
        dot(p, (xv, yv), PRACTICE, 4.0)
p.label(3 * PI / 2, 0, "sin z = 0  (z = n" + PI_S + ")", 0, -10, THEORY, 12, "middle", True)
p.label(PI / 2, Y2, "sin z = 2", 9, -6, PRACTICE, 12, "start", True)
p.label(PI / 2, -Y2, "sin z = 2", 9, 15, PRACTICE, 12, "start", True)
p.label(3 * PI + 0.85, Y2, "y = ln(2+" + SQRT + "3)", -2, -6, REMARK, 11, "end", False, True)
p.label(3 * PI + 0.85, -Y2, "y = " + MINUS + "ln(2+" + SQRT + "3)", -2, 15, REMARK, 11, "end", False, True)
OUT["elemanter-fonksiyonlar-trig-sin-sifirlar"] = figure(
    400, 222, [p],
    "sin <em>z</em>'nin s&#305;f&#305;rlar&#305; yaln&#305;z reel eksendedir: <em>z</em> = <em>n</em>&#960;. "
    "Reel eksende |sin <em>x</em>| &#8804; 1 oldu&#287;undan sin <em>z</em> = 2 denkleminin &#231;&#246;z&#252;mleri "
    "eksenin d&#305;&#351;&#305;na &#231;&#305;kar: reel sin&#252;s&#252;n tepe yapt&#305;&#287;&#305; <em>x</em> = &#960;/2 + 2<em>n</em>&#960; "
    "dikeyleri &#252;zerinde, eksenin &#177;ln(2 + &#8730;3) &#8776; &#177;1,317 uza&#287;&#305;nda simetrik &#231;iftler.",
    aria="sin z sifirlari reel eksende; sin z = 2 cozumleri eksenin ustunde ve altinda")

# ======================================================= hiperbolik-fonksiyonlar
# ---- H1: z ↦ iz carries the real zeros of sin onto the imaginary zeros of sinh
p = cplane(40, 24, 320, (-7.4, 7.4), (-7.4, 7.4))
p.origin_axes()
angle_arc(p, 0.06, PI / 2 - 0.06, PI, REMARK, 1.6)
for n in (-2, -1, 1, 2):
    dot(p, (n * PI, 0), THEORY, 4.0)
    dot(p, (0, n * PI), PRACTICE, 4.0)
dot(p, (0, 0), TEXT, 4.0)
for yv in (-3 * PI / 2, -PI / 2, PI / 2, 3 * PI / 2):
    dot(p, (0, yv), BASE, 2.8)
for n, lab in ((-2, MINUS + "2" + PI_S), (-1, MINUS + PI_S), (1, PI_S), (2, "2" + PI_S)):
    p.label(n * PI, 0, lab, 0, 16, THEORY, 11, "middle")
    p.label(0, n * PI, lab + "i", -8, 4, PRACTICE, 11, "end")
p.label(7.3, 0, "sin z = 0", 0, -10, THEORY, 12, "end", True)
p.label(0, 2 * PI, "sinh z = 0", 10, 4, PRACTICE, 12, "start", True)
p.label(0, 3 * PI / 2, "cosh z = 0", 10, 4, BASE, 11, "start", False, True)
p.label(*polar(PI, PI / 4), "z " + MAPSTO + " iz", 8, -4, REMARK, 12, "start", True, True)
OUT["elemanter-fonksiyonlar-hiperbolik-donme"] = figure(
    400, 392, [p],
    "sin <em>z</em>'nin s&#305;f&#305;rlar&#305; reel eksende <em>n</em>&#960; noktalar&#305;, sinh <em>z</em>'ninkiler "
    "sanal eksende <em>n</em>&#960;<em>i</em> noktalar&#305;d&#305;r. &#304;kisi 90&#176;'lik <em>z</em> &#8614; <em>iz</em> "
    "d&#246;nd&#252;rmesiyle birbirine gider: sin <em>z</em> = &#8722;<em>i</em> sinh(<em>iz</em>) k&#246;pr&#252;s&#252;n&#252;n "
    "geometrik anlam&#305; budur. K&#252;&#231;&#252;k noktalar cosh <em>z</em>'nin s&#305;f&#305;rlar&#305;, "
    "(&#960;/2 + <em>n</em>&#960;)<em>i</em>.",
    aria="sin z sifirlari reel eksende, sinh z sifirlari sanal eksende; z -> iz dondurmesi")

# ############################################################################
# PART: İntegraller
# ############################################################################

# ############################################################################
# PART: İntegraller
# ############################################################################


def _arc_head(p, r, a, color, width=1.9, ccw=True, cx=0.0, cy=0.0, da=0.12):
    """Arrowhead lying ON the circle |z - c| = r at angle a (radians); ccw=False for clockwise motion."""
    b = a - da if ccw else a + da
    p.arrow((cx + r * math.cos(b), cy + r * math.sin(b)), (cx + r * math.cos(a), cy + r * math.sin(a)),
            color, width, head=8.0)


# ============================================ reel-değişkenli-integraller
# ---- I1: mean value theorem fails — w(t) = e^{it} returns to its start, its speed is never 0
t = PI / 3
w = polar(1, t)
v = (w[0] - math.sin(t), w[1] + math.cos(t))          # w + w'(t),  w'(t) = i e^{it}
p = cplane(40, 24, 320, (-1.4, 2.6), (-1.4, 1.9))
p.origin_axes()
p.circle(0, 0, 1, THEORY, 1.8)
p.line([(0, 0), w], REMARK, 1.1, "3 3", 0.6)
p.arrow(w, v, PRACTICE, 2.2)
dot(p, w, THEORY, 4)
dot(p, (1, 0), TEXT, 4)
p.label(1, 0, "w(0) = w(2π) = 1", 8, -8, TEXT, 11.5, "start", True)
p.label(*w, "w(t) = e" + sup("it"), 10, 1, THEORY, 12, "start", True)
p.label((w[0] + v[0]) / 2, (w[1] + v[1]) / 2, "w′(t) = ie" + sup("it") + ", |w′(t)| = 1", 8, -8, PRACTICE, 11.5, "start", True)
p.label(2.6, -1.3, "kiriş sıfır, hız hiç sıfır değil", 0, 0, REMARK, 10.5, "end", False, True)
OUT["integraller-omt-karsi-ornek"] = figure(
    400, 312, [p],
    "<em>w</em>(<em>t</em>) = <em>e<sup>it</sup></em>, [0, 2π] boyunca birim çemberi dolaşıp başladığı noktaya döner: "
    "kiriş <em>w</em>(2π) − <em>w</em>(0) = 0'dır. Hız vektörü <em>w</em>′(<em>t</em>) = <em>ie<sup>it</sup></em> ise "
    "her an çembere teğettir ve boyu hep 1'dir; sıfırlanan bir <em>w</em>′(<em>c</em>) yoktur. Ortalama değer teoremi "
    "kompleks değerli fonksiyonlara taşınmaz.",
    aria="Birim cember uzerinde w(t) = e^(it): kiris sifir, hiz vektoru hic sifir degil")

# ========================================================== yaylar-ve-çevreler
# ---- Y1: the broken line 0 -> 1+i -> 2+i is a single (simple) arc with a corner
p = cplane(40, 24, 320, (-0.45, 2.55), (-0.42, 1.5))
p.origin_axes(xticks=(1, 2), yticks=(1,))
p.line([(0, 0), (1, 1), (2, 1)], THEORY, 2.0)
p.arrow((0.4, 0.4), (0.55, 0.55), THEORY, 2.0)
p.arrow((1.4, 1), (1.55, 1), THEORY, 2.0)
dot(p, (0, 0), TEXT, 3.8)
dot(p, (1, 1), TEXT, 3.8)
dot(p, (2, 1), TEXT, 3.8)
p.label(0, 0, "0", -8, 15, TEXT, 12, "end", True)
p.label(1, 1, "1 + i", -7, -7, TEXT, 12, "end", True)
p.label(2, 1, "2 + i", 9, 4, TEXT, 12, "start", True)
p.label(0.62, 0.3, "z = x + ix", 0, 0, THEORY, 11.5, "start", False, True)
p.label(0.62, 0.3, "0 ≤ x ≤ 1", 0, 15, THEORY, 10.5, "start", False, True)
p.label(1.5, 1, "z = x + i", 0, -24, THEORY, 11.5, "middle", False, True)
p.label(1.5, 1, "1 ≤ x ≤ 2", 0, -10, THEORY, 10.5, "middle", False, True)
OUT["integraller-kirik-cizgi"] = figure(
    400, 256, [p],
    "Kırık çizgi tek bir yaydır: 0'dan 1 + <em>i</em>'ye <em>z</em> = <em>x</em> + <em>ix</em>, oradan 2 + <em>i</em>'ye "
    "<em>z</em> = <em>x</em> + <em>i</em> parçası; parametre <em>x</em> baştan sona artar. 1 + <em>i</em> köşesinde yön "
    "aniden değişir. Farklı <em>x</em> değerleri farklı noktalar verdiğinden yay basittir.",
    aria="0'dan 1+i'ye ve 2+i'ye giden kirik cizgi yayi")

# ---- Y2: same point set (unit circle), three different arcs
def _small_circle_panel(x0, title):
    q = cplane(x0, 36, 150, (-1.5, 1.5), (-1.5, 1.5))
    q.origin_axes()
    q.text_px(x0 + 75, 36 - 14, title, TEXT, 11.5, "middle", True)   # a little higher than panel_title: clears "Im"
    q.circle(0, 0, 1, THEORY, 1.9)
    dot(q, (1, 0), TEXT, 3.6)
    q.label(1, 0, "1", 6, -6, TEXT, 11, "start")
    return q


p1 = _small_circle_panel(40, "b) z = e" + sup("iθ"))
_arc_head(p1, 1, PI / 2, THEORY, ccw=True)
p1.text_px(40 + 75, 36 + 150 + 20, "saat yönünün tersine", TEXT, 10.5, "middle", False, True)
p2 = _small_circle_panel(215, "c) z = e" + sup("−iθ"))
_arc_head(p2, 1, PI / 2, THEORY, ccw=False)
p2.text_px(215 + 75, 36 + 150 + 20, "saat yönünde", TEXT, 10.5, "middle", False, True)
p3 = _small_circle_panel(390, "d) z = e" + sup("i2θ"))
_arc_head(p3, 1, PI / 2, THEORY, ccw=True)
# a two-turn dashed spiral inside: starts near z = 1 (marked), winds inward twice, ends with an arrowhead
spir = [polar(0.86 - 0.50 * k / 160, 0.35 + (4 * PI - 0.5) * k / 160) for k in range(161)]
p3.line(spir[:-2], PRACTICE, 1.5, "4 3")
p3.arrow(spir[-4], spir[-1], PRACTICE, 1.5, head=8)
dot(p3, spir[0], PRACTICE, 2.8)                                   # start of the double traversal
p3.text_px(390 + 75, 36 + 150 + 20, "iki kez dolaşılır", PRACTICE, 10.5, "middle", False, True)
OUT["integraller-ayni-cember-uc-yay"] = figure(
    580, 220, [p1, p2, p3],
    "Üçünün nokta kümesi aynı birim çemberdir; yay olarak üçü de farklıdır. (b) pozitif yönlü basit kapalı eğridir; "
    "(c) aynı çemberi saat yönünde dolaşır; (d) ise <em>θ</em> bir kez 0'dan 2π'ye giderken çemberi iki kez dolaşır "
    "— uçlar dışında da çakışan noktalar olduğundan basit kapalı eğri değildir.",
    css_class=WIDE, aria="Ayni birim cember, uc farkli yay: pozitif yon, negatif yon, iki tur")

# ---- Y3: a simple closed contour built from four smooth arcs; corners; interior / exterior
p = cplane(30, 24, 340, (-3.2, 3.6), (-2.0, 2.9))
p.origin_axes(opacity=0.35)
C = [(-2, -1), (2, -1)] + circle_pts(0, 0, 2, 0, PI)          # bottom, right side, arc, left side (closed)
closed_curve(p, C, THEORY, 2.0, fill=THEORY, opacity=0.10)
p.arrow((0.05, -1), (0.3, -1), THEORY, 2.0)                   # C1: rightwards
_arc_head(p, 2, PI / 2, THEORY, 2.0)                          # C3: leftwards at the top
p.arrow((2, -0.65), (2, -0.4), THEORY, 2.0)                    # C2: upwards
p.arrow((-2, -0.35), (-2, -0.6), THEORY, 2.0)                  # C4: downwards
for c in ((2, -1), (2, 0), (-2, 0), (-2, -1)):
    dot(p, c, PRACTICE, 3.8)
p.label(1.2, -1, "C₁", 0, 16, THEORY, 12.5, "middle", True, True)
p.label(2, -0.5, "C₂", 8, 4, THEORY, 12.5, "start", True, True)
p.label(*polar(2, 0.55), "C₃", 9, 0, THEORY, 12.5, "start", True, True)
p.label(-2, -0.5, "C₄", -8, 4, THEORY, 12.5, "end", True, True)
p.label(0.2, 2, "pozitif yön", 8, -6, THEORY, 10.5, "start", False, True)
p.label(-1.9, -1, "köşeler: z′ sıçrar", 0, 18, PRACTICE, 10.5, "middle", False, True)
p.label(0, 0.6, "iç bölge (sınırlı)", 0, 0, THEORY, 11.5, "middle", False, True)
p.label(-3.1, 2.55, "dış bölge (sınırsız)", 0, 0, TEXT, 11.5, "start", False, True)
OUT["integraller-basit-kapali-cevre"] = figure(
    400, 296, [p],
    "Dört düzgün yayın uç uca eklenmesiyle oluşan basit kapalı çevre <em>C</em> = <em>C</em><sub>1</sub> + <em>C</em><sub>2</sub> + "
    "<em>C</em><sub>3</sub> + <em>C</em><sub>4</sub>; uzunluğu parçaların uzunluklarının toplamıdır. Köşelerde <em>z</em>(<em>t</em>) "
    "süreklidir ama <em>z</em>′(<em>t</em>) sıçrar (parçalı sürekli). Jordan eğri teoremi: <em>C</em>, düzlemi sınırlı bir iç bölge "
    "ile sınırsız bir dış bölgeye ayırır.",
    aria="Dort duzgun yaydan olusan basit kapali cevre, koseler, ic ve dis bolge")

# ========================================================= çevre-integralleri
# ---- Ç1: the right half of |z| = 2 from -2i to 2i
p = cplane(60, 24, 280, (-2.7, 2.7), (-2.6, 2.6))
p.origin_axes()
p.circle(0, 0, 2, REMARK, 1.1, "4 3", opacity=0.6)
p.arc(0, 0, 2, -PI / 2, PI / 2, THEORY, 2.0)
_arc_head(p, 2, 0, THEORY, 2.0)
zt = polar(2, 0.9)
p.line([(0, 0), zt], REMARK, 1.1, "3 3", 0.6)
angle_arc(p, 0, 0.9, 0.7, THEORY, 1.5)
dot(p, (0, -2), TEXT, 4)
dot(p, (0, 2), TEXT, 4)
dot(p, zt, THEORY, 3.6)
p.label(0, 2, "2i", -9, -4, TEXT, 12, "end", True)
p.label(0, -2, "−2i", -9, 14, TEXT, 12, "end", True)
p.label(*zt, "z = 2e" + sup("iθ"), 9, -2, THEORY, 12, "start", True)
p.label(0.86, 0.36, "θ", 0, 0, THEORY, 12, "start", True, True)
p.label(*polar(2, -0.6), "C", 10, 4, THEORY, 13, "start", True, True)
p.label(-2.6, -2.3, "−π/2 ≤ θ ≤ π/2", 0, 0, TEXT, 11, "start", False, True)
OUT["integraller-sag-yarim-cember"] = figure(
    400, 320, [p],
    "|<em>z</em>| = 2 çemberinin sağ yarısı: <em>θ</em>, −π/2'den π/2'ye artarken <em>z</em> = 2<em>e<sup>iθ</sup></em> "
    "noktası −2<em>i</em>'den başlar, 2'den geçer ve 2<em>i</em>'de biter; dolaşım saat yönünün tersinedir.",
    aria="|z| = 2 cemberinin -2i'den 2i'ye sag yarisi")

# ---- Ç2: same endpoints, two different paths — OAB broken line vs. the diagonal OB
p = cplane(60, 24, 280, (-0.42, 1.6), (-0.34, 1.46))
p.origin_axes()
p.polygon([(0, 0), (0, 1), (1, 1)], THEORY, 0.08)
p.line([(0, 0), (0, 1), (1, 1)], THEORY, 2.0)
p.arrow((0, 0.42), (0, 0.56), THEORY, 2.0)
p.arrow((0.42, 1), (0.56, 1), THEORY, 2.0)
p.line([(0, 0), (1, 1)], PRACTICE, 2.0)
p.arrow((0.42, 0.42), (0.53, 0.53), PRACTICE, 2.0)
dot(p, (0, 0), TEXT, 4)
dot(p, (0, 1), TEXT, 4)
dot(p, (1, 1), TEXT, 4)
p.label(0, 0, "O = 0", -7, 16, TEXT, 12, "end", True)
p.label(0, 1, "A = i", -8, 4, TEXT, 12, "end", True)
p.label(1, 1, "B = 1 + i", 9, 4, TEXT, 12, "start", True)
p.label(0.5, 1, "C₁ = OAB", 0, -9, THEORY, 12, "middle", True, True)
p.label(0.62, 0.38, "C₂ = OB", 0, 0, PRACTICE, 12, "start", True, True)
p.label(1.58, 1.36, "OABO kapalı çevresi: C₁ − C₂", 0, 0, REMARK, 10.5, "end", False, True)
OUT["integraller-iki-yol"] = figure(
    400, 300, [p],
    "<em>O</em> = 0'dan <em>B</em> = 1 + <em>i</em>'ye iki yol: <em>C</em><sub>1</sub> = <em>OAB</em> kırık çizgisi ve "
    "<em>C</em><sub>2</sub> = <em>OB</em> köşegeni. <em>f</em>(<em>z</em>) = <em>y</em> − <em>x</em> − <em>i</em>3<em>x</em>² "
    "için iki integral farklı çıkar; fark, <em>OABO</em> üçgenini dolaşan kapalı <em>C</em><sub>1</sub> − <em>C</em><sub>2</sub> "
    "çevresi üzerindeki integraldir ve sıfır değildir.",
    aria="0'dan 1+i'ye iki yol: OAB kirik cizgisi ve OB kosegeni")

# ---- Ç3: upper semicircle |z| = 3 whose starting point lies on the branch cut θ = 0
p = cplane(30, 24, 340, (-3.7, 4.5), (-1.0, 3.6))
p.origin_axes()
p.line([(0, 0), (4.5, 0)], PRACTICE, 3.2, None, 0.35)          # dal kesimi: pozitif reel eksen
p.arc(0, 0, 3, 0, PI, THEORY, 2.0)
_arc_head(p, 3, PI / 2, THEORY, 2.0)
hollow(p, (0, 0), TEXT)
dot(p, (-3, 0), TEXT, 4)
hollow(p, (3, 0), PRACTICE, 4.2, 1.9)                           # f is undefined here
p.label(-3, 0, "−3", -8, -6, TEXT, 12, "end", True)
p.label(3, 0, "3", 8, -6, TEXT, 12, "start", True)
p.label(0, 0, "0", -8, 15, TEXT, 11, "end")
p.label(1.6, 0, "dal kesimi: θ = 0", 0, -8, PRACTICE, 11, "middle", True)
p.label(2.9, 0, "f(3) tanımsız", 0, 17, PRACTICE, 10.5, "middle", False, True)
p.label(*polar(3, 2.3), "C", -9, -2, THEORY, 13, "end", True, True)
OUT["integraller-dal-yarim-cember"] = figure(
    400, 244, [p],
    "0 &lt; arg <em>z</em> &lt; 2π dalının kesimi pozitif reel eksendir ve yolun başlangıç noktası <em>z</em> = 3 tam bu "
    "ışın üzerindedir: <em>f</em> orada tanımsızdır (boş nokta). Yine de <em>θ</em> → 0<sup>+</sup> iken integrandın sağ "
    "limiti vardır; parçalı sürekli integrand integrali kurtarır.",
    aria="Ust yarim cember, pozitif reel eksendeki dal kesimi, baslangic noktasi kesim uzerinde")

# ---- Ç4: full circle |z| = R against the cut of the principal branch (negative real axis)
p = cplane(50, 24, 300, (-2.9, 2.9), (-2.6, 2.6))
p.origin_axes()
p.line([(-2.9, 0), (0, 0)], PRACTICE, 3.2, None, 0.35)         # Log kesimi
p.circle(0, 0, 2, THEORY, 2.0)
_arc_head(p, 2, PI / 2, THEORY, 2.0)
_arc_head(p, 2, -PI / 2, THEORY, 2.0)
hollow(p, (0, 0), TEXT)
dot(p, (-2, 0), PRACTICE, 4.2)
dot(p, (2, 0), TEXT, 3.6)
p.label(2, 0, "θ = 0", 8, -6, TEXT, 11.5, "start")
p.label(-2, 0, "θ = ±π", -8, -10, PRACTICE, 11.5, "end", True)
p.label(-1.85, 0, "esas dal kesimi", 0, -8, PRACTICE, 10.5, "start", False, True)
p.label(-1.85, 0, "yolun iki ucu", 0, 15, PRACTICE, 10.5, "start", False, True)
p.label(*polar(2, PI / 4), "C: |z| = R", 9, -4, THEORY, 12, "start", True, True)
OUT["integraller-esas-dal-cember"] = figure(
    400, 320, [p],
    "Esas dalın kesimi negatif reel eksendir; <em>C</em> çemberi kesime yalnız <em>z</em> = −<em>R</em> noktasında değer ve "
    "tam da orası yolun başlangıcı (<em>θ</em> = −π) ile bitişidir (<em>θ</em> = π). İntegrand yalnız bu tek noktada "
    "tanımsızdır ve orada iki tek yanlı limiti vardır; parçalı süreklilik integral için yeterlidir.",
    aria="|z| = R cemberi ve esas dalin negatif reel eksendeki kesimi; kesim yolun uc noktasina deger")

# ============================================================= üst-sınırlar
# ---- Ü1: the quarter circle of |z| = 2 in the first quadrant, L = π
p = cplane(70, 24, 260, (-0.55, 2.7), (-0.5, 2.6))
p.origin_axes()
p.sector(0, 0, 2, 0, PI / 2, THEORY, 0.08)
p.arc(0, 0, 2, -0.45, PI / 2 + 0.45, REMARK, 1.1, "4 3", 0.6)     # the circle continues beyond the arc
p.arc(0, 0, 2, 0, PI / 2, THEORY, 2.2)
_arc_head(p, 2, PI / 4, THEORY, 2.2)
p.line([(0, 0), polar(2, 1.1)], REMARK, 1.1, "3 3", 0.6)
dot(p, (2, 0), TEXT, 4)
dot(p, (0, 2), TEXT, 4)
p.label(2, 0, "2", 6, 16, TEXT, 12, "start", True)
p.label(0, 2, "2i", -6, -8, TEXT, 12, "end", True)
p.label(*polar(1.0, 1.1), "|z| = 2", 8, 6, REMARK, 11, "start", False, True)
p.label(*polar(2.25, 1.15), "C", 0, 4, THEORY, 13, "middle", True, True)
p.label(1.0, 0, "L = ¼·2π·2 = π", 0, 17, REMARK, 11, "middle", False, True)
OUT["integraller-ceyrek-cember"] = figure(
    400, 296, [p],
    "<em>C</em>, |<em>z</em>| = 2 çemberinin birinci çeyrekte kalan yayıdır: <em>z</em> = 2'den <em>z</em> = 2<em>i</em>'ye "
    "saat yönünün tersine. Uzunluğu tam çemberin dörtte biri, <em>L</em> = π; ML eşitsizliğindeki <em>L</em> budur.",
    aria="|z| = 2 cemberinin birinci ceyrekteki yayi, uzunlugu pi")

# ---- Ü2: geometry of the reverse triangle inequality in the w = z³ plane
p = cplane(60, 36, 280, (-9.6, 9.6), (-9.4, 9.4))
p.text_px(p.x0 + p.w / 2, p.y0 - 14, "w = z³ düzlemi: |z| = 2 iken |w| = 8", TEXT, 11.5, "middle", True)   # clears "Im"
p.origin_axes()
p.circle(0, 0, 8, THEORY, 2.0)
w2 = polar(8, 2 * PI / 3)
p.line([(1, 0), w2], BASE, 1.4, "5 4")
p.line([(1, 0), (8, 0)], PRACTICE, 2.4)
dot(p, (1, 0), PRACTICE, 4.2)
dot(p, (8, 0), THEORY, 4)
dot(p, w2, THEORY, 4)
p.label(1, 0, "1", 0, 16, PRACTICE, 12, "middle", True)
p.label(8, 0, "8", 4, -9, THEORY, 12, "start", True)
p.label(4.5, 0, "|w − 1| = 7", 0, -8, PRACTICE, 11.5, "middle", True)
p.label(*w2, "w", -8, -4, THEORY, 12.5, "end", True, True)
p.label((1 + w2[0]) / 2, w2[1] / 2, "&gt; 7", -8, 2, BASE, 11.5, "end", True)
OUT["integraller-ters-ucgen"] = figure(
    400, 336, [p],
    "|<em>z</em>| = 2 iken <em>w</em> = <em>z</em>³ değeri |<em>w</em>| = 8 çemberi üzerindedir. 1 noktası bu çemberin "
    "içinde kaldığından çember üzerindeki her <em>w</em> için |<em>w</em> − 1| ≥ 8 − 1 = 7; en kısa uzaklık <em>w</em> = 8'de "
    "alınır. Ters yönlü üçgen eşitsizliği |<em>z</em>³ − 1| ≥ |<em>z</em>|³ − 1'in geometrik anlamı budur.",
    aria="w = z^3 duzleminde |w| = 8 cemberi ve 1 noktasinin cembere uzakligi en az 7")

# ---- Ü3: the segment from i to 1; the point nearest to the origin is the midpoint, |z| ≥ 1/√2
p = cplane(60, 24, 280, (-0.42, 1.55), (-0.42, 1.45))
p.origin_axes()
rr = 1 / math.sqrt(2)
p.arc(0, 0, rr, -0.35, PI / 2 + 0.35, BASE, 1.2, "4 3", 0.8)
p.line([(0, 1), (1, 0)], THEORY, 2.0)
p.arrow((0.62, 0.38), (0.72, 0.28), THEORY, 2.0)
p.line([(0, 0), (0.5, 0.5)], PRACTICE, 1.4, "5 4")
s = 0.06 / math.sqrt(2)
p.line([(0.5 - s, 0.5 - s), (0.5, 0.5 - 2 * s), (0.5 + s, 0.5 - s)], PRACTICE, 1.1)   # right-angle mark
dot(p, (0, 1), TEXT, 4)
dot(p, (1, 0), TEXT, 4)
dot(p, (0.5, 0.5), PRACTICE, 4.2)
p.label(0, 1, "i", -9, 4, TEXT, 12.5, "end", True, True)
p.label(1, 0, "1", 6, -7, TEXT, 12.5, "start", True)
p.label(0.5, 0.5, "(1 + i)/2", 10, -6, PRACTICE, 11.5, "start", True)
p.label(0.25, 0.25, "1/√2", 10, 10, PRACTICE, 11.5, "start", False, True)
p.label(*polar(rr, -0.22), "|z| = 1/√2", 8, 6, BASE, 11, "start", False, True)
p.label(0.74, 0.3, "C", 8, 10, THEORY, 13, "start", True, True)
p.label(1.55, 1.3, "L = |1 − i| = √2", 0, 0, THEORY, 11.5, "end", False, True)
OUT["integraller-dogru-parcasi-i-1"] = figure(
    400, 316, [p],
    "<em>i</em>'den 1'e giden doğru parçasının başlangıca en yakın noktası, başlangıçtan indirilen dikmenin ayağı olan "
    "orta nokta (1 + <em>i</em>)/2'dir; uzaklığı 1/√2. Parça, |<em>z</em>| = 1/√2 çemberine orada teğettir; dolayısıyla "
    "parça üzerinde |<em>z</em>| ≥ 1/√2 ve 1/|<em>z</em>|<sup>4</sup> ≤ 4 = <em>M</em> olur. Uzunluk <em>L</em> = √2.",
    aria="i'den 1'e dogru parcasi, orta noktasi ve baslangica en kisa uzaklik 1/sqrt(2)")

# ============================================================== ters-türevler
# ---- T1: a closed contour C split at z1, z2 into two paths: C = C1 − C2
p = cplane(40, 16, 320, (-3.5, 3.5), (-2.75, 2.75))
D = [(x, 0.82 * y) for x, y in blob(0, 0, 2.9, [(0.22, 2, 0.4), (0.14, 3, 1.3)])]
closed_curve(p, D, BASE, 1.3, "6 4")
ell = lambda t: (2 * math.cos(t), 1.2 * math.sin(t))
upper = [ell(PI - PI * k / 60) for k in range(61)]      # z1 -> z2 over the top
lower = [ell(PI + PI * k / 60) for k in range(61)]      # z1 -> z2 under the bottom
p.line(upper, THEORY, 2.0)
p.line(lower, PRACTICE, 2.0)
p.arrow(ell(1.75), ell(1.6), THEORY, 2.0)
p.arrow(ell(4.55), ell(4.7), PRACTICE, 2.0)
dot(p, (-2, 0), TEXT, 4.2)
dot(p, (2, 0), TEXT, 4.2)
p.label(-2, 0, "z₁", -9, 4, TEXT, 12.5, "end", True, True)
p.label(2, 0, "z₂", 9, 4, TEXT, 12.5, "start", True, True)
p.label(0.7, 1.2, "C₁", 0, -8, THEORY, 12.5, "middle", True, True)
p.label(0.7, -1.2, "C₂", 0, 16, PRACTICE, 12.5, "middle", True, True)
dl = D[int(120 * 2.45 / (2 * PI))]
p.label(0.76 * dl[0], 0.76 * dl[1], "D", 0, 4, BASE, 13, "middle", True, True)
p.label(0, 0, "C = C₁ − C₂", 0, -2, TEXT, 12, "middle", True)
p.label(0, 0, "(C₂ ters yönde dolaşılır)", 0, 14, REMARK, 10.5, "middle", False, True)
OUT["integraller-kapali-cevre-fark"] = figure(
    400, 284, [p],
    "Kapalı <em>C</em> çevresi üzerinde iki nokta seçilince <em>C</em>, ikisi de <em>z</em><sub>1</sub>'den <em>z</em><sub>2</sub>'ye "
    "giden iki yola ayrılır: <em>C</em><sub>1</sub> (üst) ve <em>C</em><sub>2</sub> (alt). <em>C</em>'yi dolaşmak "
    "<em>C</em><sub>1</sub>'i ileri, <em>C</em><sub>2</sub>'yi geri (−<em>C</em><sub>2</sub>) izlemektir; yoldan bağımsızlıkla "
    "iki integral eşit olduğundan <em>C</em> üzerindeki integral sıfırdır.",
    aria="Kapali cevre, z1 ve z2 noktalarinda iki yola ayrilmis: C = C1 - C2")

# ---- T2: the two halves of |z| = 2 with two different logarithm branches
def _half_panel(x0, title):
    q = cplane(x0, 36, 250, (-2.8, 2.8), (-2.7, 2.7))
    q.text_px(x0 + 125, 36 - 14, title, TEXT, 11.5, "middle", True)   # a little higher than panel_title: clears "Im"
    q.origin_axes()
    q.circle(0, 0, 2, REMARK, 1.1, "4 3", opacity=0.6)
    hollow(q, (0, 0), TEXT)
    dot(q, (0, 2), TEXT, 3.8)
    dot(q, (0, -2), TEXT, 3.8)
    q.label(0, 2, "2i", -9, -4, TEXT, 12, "end", True)
    q.label(0, -2, "−2i", -9, 14, TEXT, 12, "end", True)
    return q


p1 = _half_panel(24, "C₁ üzerinde Log z  (−π &lt; Θ &lt; π)")
p1.line([(-2.8, 0), (0, 0)], PRACTICE, 3.2, None, 0.35)
p1.arc(0, 0, 2, -PI / 2, PI / 2, THEORY, 2.0)
_arc_head(p1, 2, 0, THEORY, 2.0)
p1.label(*polar(2, PI / 4), "C₁", 9, -2, THEORY, 13, "start", True, True)
p1.label(-1.85, 0, "Log kesimi", 0, -8, PRACTICE, 10.5, "start", True)
p1.label(-1.85, 0, "Θ = ±π", 0, 15, PRACTICE, 10.5, "start", False, True)
p2 = _half_panel(300, "C₂ üzerinde log z  (0 &lt; θ &lt; 2π)")
p2.line([(0, 0), (2.8, 0)], PRACTICE, 3.2, None, 0.35)
p2.arc(0, 0, 2, PI / 2, 3 * PI / 2, THEORY, 2.0)
_arc_head(p2, 2, PI, THEORY, 2.0)
p2.label(*polar(2, 3 * PI / 4), "C₂", -9, -2, THEORY, 13, "end", True, True)
p2.label(0.45, 0, "log kesimi", 0, -8, PRACTICE, 10.5, "start", True)
p2.label(0.45, 0, "θ = 0", 0, 15, PRACTICE, 10.5, "start", False, True)
p2.text_px(287, 36 + 241 + 22, "her dalın kesimi, kullanıldığı yarım çembere dokunmaz", REMARK, 10.5, "middle", False, True)
OUT["integraller-iki-dal"] = figure(
    574, 312, [p1, p2],
    "Her yarım çember için kesimi öbür tarafta kalan bir dal seçilir: sağ yarı <em>C</em><sub>1</sub> üzerinde esas dal "
    "Log <em>z</em> (kesimi negatif reel eksen), sol yarı <em>C</em><sub>2</sub> üzerinde 0 &lt; <em>θ</em> &lt; 2π dalı "
    "(kesimi pozitif reel eksen). İki parçanın toplamı 2π<em>i</em>'yi verir. Tek bir dal çemberin tamamını kapsayamaz, "
    "çünkü her dalın kesimi çemberi keser.",
    css_class=WIDE, aria="|z| = 2 cemberinin iki yarisi ve her yari icin kesimi obur tarafta kalan logaritma dali")

# ---- T3: a path above the real axis and the cut of the branch −π/2 < θ < 3π/2 (negative imaginary axis)
p = cplane(40, 24, 320, (-3.7, 3.7), (-2.4, 2.8))
p.origin_axes()
p.line([(0, 0), (0, -2.4)], PRACTICE, 3.2, None, 0.35)         # f1 kesimi
c1 = [(-3 + 6 * k / 100, 2.0 * math.sin(PI * k / 100) + 0.6 * math.sin(2 * PI * k / 100)) for k in range(101)]
c2 = [(-3 + 6 * k / 100, -1.1 * math.sin(PI * k / 100)) for k in range(101)]
p.line(c2, BASE, 1.4, "2 4", 0.8)
p.arrow(c2[28], c2[31], BASE, 1.4, head=7)
p.line(c1, THEORY, 2.0)
p.arrow(c1[49], c1[52], THEORY, 2.0)
hollow(p, (0, 0), TEXT)
dot(p, (-3, 0), TEXT, 4)
dot(p, (3, 0), TEXT, 4)
p.label(-3, 0, "−3", -6, 17, TEXT, 12, "end", True)
p.label(3, 0, "3", 6, 17, TEXT, 12, "start", True)
p.label(-0.9, 2.3, "C₁ (üstten)", -4, -10, THEORY, 12, "end", True, True)
p.label(0, -1.7, "f₁ kesimi: θ = −π/2", 8, 0, PRACTICE, 11, "start", True)
p.label(-0.35, -1.55, "C₂ (alttan)", 0, 0, BASE, 11.5, "end", True, True)
p.label(-0.35, -1.9, "kesimi keser", 0, 0, BASE, 10.5, "end", False, True)
OUT["integraller-karekok-dal"] = figure(
    400, 276, [p],
    "−π/2 &lt; <em>θ</em> &lt; 3π/2 dalının kesimi negatif sanal eksendir: reel eksenin üstünden geçen her <em>C</em><sub>1</sub> "
    "yolu kesime hiç dokunmaz, dolayısıyla <em>f</em><sub>1</sub> bu yol üzerinde süreklidir ve ters türevi "
    "<em>F</em><sub>1</sub> kullanılabilir. Alttan geçen bir <em>C</em><sub>2</sub> ise kesimi keser; onun için "
    "π/2 &lt; <em>θ</em> &lt; 5π/2 dalı gerekir.",
    aria="-3'ten 3'e ustten gecen yol ve negatif sanal eksendeki dal kesimi; alttan gecen yol kesimi keser")

# ############################################################################
# PART: Cauchy Teoremleri
# ############################################################################

# ############################################################################
# PART: Cauchy Teoremleri
# ############################################################################
# Stil kararı: eksenlerin (Re/Im) bir anlam taşıdığı figürlerde (somut noktalar, çemberler,
# dikdörtgen) origin_axes() çizilir; şematik çevre/blob figürlerinde (kare örtüsü, iç kenarlar,
# ilmekler, kesikler, deformasyon, C_rho, d uzaklığı, komşuluk zinciri) eksen ÇİZİLMEZ —
# koordinatların bir anlamı yoktur ve etiketlerle çakışırlar. Sonraki kısımlar da bu kurala uyar.

# ---- küçük yardımcılar (yalnızca bu kısımda kullanılır) --------------------
def _sub(s, size=9):
    """Subscript inside an SVG <text>: 'C' + _sub('&#961;')."""
    # the zero-width space carries the baseline reset without eating the caller's own spaces (cf. svg_plot.sup)
    return f'<tspan font-size="{size}" dy="3">{s}</tspan><tspan dy="-3">&#8203;</tspan>'


def _mid_arrow(p, a, b, color, width=1.6, head=7.0):
    """Segment a->b with an arrowhead at its midpoint (orientation mark on a polygon edge)."""
    m = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
    p.line([a, b], color, width)
    p.arrow(a, m, color, width, head=head)


def _paired_arrows(p, a, b, c_fwd, c_back, off_px=4.0, trim=0.08, width=1.3, head=6.5):
    """Two thin arrows side by side along the segment a-b, in opposite directions:
    the forward one (a->b) on the left of the segment, the backward one on the right."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    L = math.hypot(dx, dy)
    ux, uy = dx / L, dy / L
    nx, ny = -uy, ux
    off = off_px / p.R(1.0)
    a1 = (a[0] + ux * trim + nx * off, a[1] + uy * trim + ny * off)
    b1 = (b[0] - ux * trim + nx * off, b[1] - uy * trim + ny * off)
    a2 = (a[0] + ux * trim - nx * off, a[1] + uy * trim - ny * off)
    b2 = (b[0] - ux * trim - nx * off, b[1] - uy * trim - ny * off)
    p.arrow(a1, b1, c_fwd, width, head=head)
    p.arrow(b2, a2, c_back, width, head=head)


def _ring_fill(p, outer_pts, cx, cy, r, color=THEORY, opacity=0.11):
    """Shade the inside of the closed polyline outer_pts minus the disk |z - c| < r (even-odd)."""
    d = " ".join(("M" if i == 0 else "L") + p.P(x, y) for i, (x, y) in enumerate(outer_pts)) + " Z"
    R = p.R(r)
    d += (f' M{p.X(cx + r):.1f},{p.Y(cy):.1f} A{R:.1f},{R:.1f} 0 1,0 {p.X(cx - r):.1f},{p.Y(cy):.1f} '
          f'A{R:.1f},{R:.1f} 0 1,0 {p.X(cx + r):.1f},{p.Y(cy):.1f} Z')
    p.add(f'<path d="{d}" fill="{color}" fill-opacity="{opacity}" fill-rule="evenodd" stroke="none"/>')


def _circle_arrow(p, cx, cy, r, ang, color, width=1.8, ccw=True, head=8.0):
    """Arrowhead placed ON the circle |z - c| = r at angle ang, pointing counter-clockwise (or clockwise)."""
    da = 0.05 if ccw else -0.05
    p.arrow((cx + r * math.cos(ang - da), cy + r * math.sin(ang - da)),
            (cx + r * math.cos(ang), cy + r * math.sin(ang)), color, width, head=head)


# ============================================================ cauchy-goursat
# ---- CG1: kare ve kısmi kare örtüsü (örtü lemması)
def _r_ortu(t):
    return 1.8 + 0.35 * math.cos(3 * t) + 0.15 * math.sin(2 * t)


def _ortu_icinde(x, y):
    return math.hypot(x, y) < _r_ortu(math.atan2(y, x))


C_pts = blob(0, 0, 1.8, [(0.35, 3, 0.0), (0.15, 2, -PI / 2)])
p = cplane(40, 24, 320, (-2.6, 2.9), (-2.45, 2.45))
h = 0.6
clip = " ".join(("M" if i == 0 else "L") + p.P(x, y) for i, (x, y) in enumerate(C_pts)) + " Z"
p.add(f'<defs><clipPath id="cg-ortu-clip"><path d="{clip}"/></clipPath></defs>')
p.add('<g clip-path="url(#cg-ortu-clip)">')
for i in range(-4, 4):
    for j in range(-4, 4):
        x0, y0 = i * h, j * h
        edge = ([(x0 + h * k / 5, y0) for k in range(6)] + [(x0 + h * k / 5, y0 + h) for k in range(6)]
                + [(x0, y0 + h * k / 5) for k in range(6)] + [(x0 + h, y0 + h * k / 5) for k in range(6)])
        flags = [_ortu_icinde(x, y) for x, y in edge]
        cell = [(x0, y0), (x0 + h, y0), (x0 + h, y0 + h), (x0, y0 + h)]
        if all(flags):
            p.polygon(cell, THEORY, 0.12)          # tam kare
        elif any(flags):
            p.polygon(cell, REMARK, 0.24)          # kısmi kare (C ile kesilmiş, içte kalan parça)
for k in range(-4, 5):
    p.line([(k * h, -2.4), (k * h, 2.4)], BASE, 0.8, None, 0.6)
    p.line([(-2.4, k * h), (2.4, k * h)], BASE, 0.8, None, 0.6)
p.add('</g>')
# vurgulanan tam kare ve içindeki z_j
p.polygon([(0, 0), (h, 0), (h, h), (0, h)], THEORY, 0.28, THEORY, 1.3)
dot(p, (0.16, 0.3), TEXT, 3.4)
p.label(0.16, 0.3, "z" + _sub("j"), 7, 4, TEXT, 12, "start", False, True)
closed_curve(p, C_pts, PRACTICE, 2.0, arrow_at=30)
p.label(*polar(_r_ortu(PI / 4), PI / 4), "C", 10, -6, PRACTICE, 13, "start", True, True)
p.label(-0.9, -0.9, "R", 0, 4, TEXT, 13, "middle", True, True)
# açıklama: renk anahtarı
for row, (col, op, txt) in enumerate(((THEORY, 0.12, "kare"), (REMARK, 0.24, "kısmi kare"))):
    lx, ly = p.X(1.45), p.Y(-1.55 - 0.42 * row)
    p.add(f'<rect x="{lx:.1f}" y="{ly - 10:.1f}" width="12" height="12" fill="{col}" fill-opacity="{op}" '
          f'stroke="{BASE}" stroke-width="0.8"/>')
    p.text_px(lx + 18, ly, txt, TEXT, 11)
OUT["cauchy-teoremleri-kare-ortu"] = figure(
    400, 356, [p],
    "<em>R</em> bölgesi (<em>C</em> ile içi) eksenlere paralel bir ızgarayla örtülür: tamamen <em>C</em>'nin "
    "içinde kalan hücreler <strong>kare</strong>, <em>C</em>'nin kestiği hücrelerin <em>R</em>'de kalan parçaları "
    "<strong>kısmi kare</strong>dir. Her alt bölgede lemmanın sabit <em>z<sub>j</sub></em> noktası seçilir; "
    "kısmi karenin sınırı, kare kenarlarının parçalarının yanı sıra <em>C</em>'nin yaylarını da içerir.",
    aria="Kapali egri C icindeki bolgenin kare ve kismi karelerle ortulmesi")

# ---- CG2: komşu karelerin iç kenarları birbirini götürür
p1 = cplane(24, 30, 250, (-0.3, 2.3), (-0.3, 2.3))
e = 0.08
for i in range(2):
    for j in range(2):
        x0, y0, x1, y1 = i, j, i + 1, j + 1
        edges = [((x0 + e, y0 + e), (x1 - e, y0 + e), j == 1),   # alt kenar (iç: j == 1)
                 ((x1 - e, y0 + e), (x1 - e, y1 - e), i == 0),   # sağ kenar (iç: i == 0)
                 ((x1 - e, y1 - e), (x0 + e, y1 - e), j == 0),   # üst kenar
                 ((x0 + e, y1 - e), (x0 + e, y0 + e), i == 1)]   # sol kenar
        for a, b, inner in edges:
            _mid_arrow(p1, a, b, PRACTICE if inner else THEORY, 1.6, 7.0)
p1.line([(0, 0), (2, 0), (2, 2), (0, 2), (0, 0)], TEXT, 1.0, None, 0.35)
p1.line([(1, 0), (1, 2)], TEXT, 1.0, None, 0.35)
p1.line([(0, 1), (2, 1)], TEXT, 1.0, None, 0.35)
for (cx, cy), lab in (((0.5, 0.5), "C" + SUB1), ((1.5, 0.5), "C" + SUB2), ((1.5, 1.5), "C" + SUB3), ((0.5, 1.5), "C&#8324;")):
    p1.label(cx, cy, lab, 0, 4, THEORY, 12.5, "middle", True, True)
panel_title(p1, "dört kare, her biri pozitif yönlü")

p2 = cplane(300, 30, 250, (-0.3, 2.3), (-0.3, 2.3))
p2.polygon([(0, 0), (2, 0), (2, 2), (0, 2)], THEORY, 0.08)
p2.line([(1, 0), (1, 2)], REMARK, 1.0, "4 3", 0.5)
p2.line([(0, 1), (2, 1)], REMARK, 1.0, "4 3", 0.5)
for a, b in (((0, 0), (2, 0)), ((2, 0), (2, 2)), ((2, 2), (0, 2)), ((0, 2), (0, 0))):
    _mid_arrow(p2, a, b, THEORY, 2.2, 8.0)
p2.label(2, 1.5, "C", 9, 4, THEORY, 13, "start", True, True)
p2.label(0.5, 1.5, "iç kenarlar", 0, -3, REMARK, 10.5, "middle", False, True)
p2.label(0.5, 1.5, "yok oldu", 0, 12, REMARK, 10.5, "middle", False, True)
panel_title(p2, "toplam: yalnızca dış sınır C kalır")
p2.text_px(287, 30 + 125 + 6, "&#8594;", TEXT, 20, "middle")
p2.text_px(287, 30 + 125 + 22, "topla", TEXT, 10, "middle", False, True)
OUT["cauchy-teoremleri-ic-kenarlar"] = figure(
    574, 330, [p1, p2],
    "Dört komşu karenin her biri pozitif yönde dolaşılınca ortak kenarlar iki kez ve <strong>zıt yönlerde</strong> "
    "katedilir (kırmızı çiftler); bu parçaların integralleri birbirini götürür. Toplamda yalnızca dış sınır "
    "üzerindeki integral kalır. Örtü lemmasındaki karelerde de aynı şey olur: iç kenarlar yok olur, geriye "
    "<em>C</em>'nin yayları kalır.",
    css_class=WIDE, aria="Dort komsu karenin ic kenarlarinin zit yonlerde katedilmesi ve dis sinirin kalmasi")

# ---- CG3: Log(z + 2) dal kesimi ile birim çember
p = cplane(40, 24, 320, (-3.7, 1.7), (-1.6, 1.6))
disk_fill(p, 0, 0, 1, THEORY, 0.10)
p.origin_axes(xticks=(-3,))
p.line([(-3.75, 0), (-2, 0)], REMARK, 3.4, None, 0.5)
dot(p, (-2, 0), REMARK, 3.8)
p.label(-2, 0, MINUS + "2", 0, 15, REMARK, 11.5, "middle", True)
p.label(-2.85, 0, "dal kesimi: z " + LEQ + " " + MINUS + "2", 0, -9, REMARK, 10.5, "middle", False, True)
# −2 ile diskin kenarı arasındaki boşluk
p.line([(-2, 0.22), (-1, 0.22)], TEXT, 1.0, None, 0.6)
p.line([(-2, 0.16), (-2, 0.28)], TEXT, 1.0, None, 0.6)
p.line([(-1, 0.16), (-1, 0.28)], TEXT, 1.0, None, 0.6)
p.label(-1.5, 0.22, "1", 0, -5, TEXT, 10.5, "middle", False, True)
p.label(-3.65, -0.9, "|" + MINUS + "2| = 2 &gt; 1", 0, 0, TEXT, 11, "start", False, True)
closed_curve(p, circle_pts(0, 0, 1), PRACTICE, 1.9, arrow_at=24)
p.label(0.72, 0.72, "C: |z| = 1", 8, -2, PRACTICE, 12, "start", True)
p.label(0, -1, "Log(z + 2) analitik", 0, 17, THEORY, 11, "middle", False, True)
OUT["cauchy-teoremleri-log-dal-kesimi"] = figure(
    400, 262, [p],
    "Log(<em>z</em> + 2)'nin dal kesimi, <em>w</em>-düzlemindeki negatif reel eksenin <em>z</em>-düzlemine "
    "taşınmış hâlidir: <em>z</em> = &#8722;2'den sola uzanan ışın. Işının başlangıca en yakın noktası "
    "&#8722;2 olup birim çemberin 1 birim dışındadır; kesim kapalı diske değmez, Log(<em>z</em> + 2) "
    "diskte analitiktir ve integral sıfırdır.",
    aria="Log(z+2) icin z=-2 noktasindan sola uzanan dal kesimi ve birim cember")

# ============================================= basit-ve-cok-baglantili-domenler
# ---- BD1: kendini kesen kapalı çevre dört basit ilmekten oluşur (gül eğrisi)
def _rose(t):
    r = 1.6 * math.cos(2 * t)
    return (r * math.cos(t), r * math.sin(t))


N = 360
rose = [_rose(2 * PI * k / N) for k in range(N)]
p = cplane(40, 24, 320, (-2.3, 2.3), (-2.0, 2.0))
for k in range(4):
    t0 = -PI / 4 + k * PI / 2
    p.polygon([_rose(t0 + (PI / 2) * m / 60) for m in range(61)], THEORY, 0.11)
p.line(rose + [rose[0]], PRACTICE, 1.9)
for k in range(4):
    t = k * PI / 2
    p.arrow(_rose(t - 0.02), _rose(t), PRACTICE, 1.9, head=8.0)
dot(p, (0, 0), TEXT, 3.6)
p.label(1.6, 0, "C" + SUB1, 9, 4, PRACTICE, 12.5, "start", True, True)
p.label(0, -1.6, "C" + SUB2, 0, 16, PRACTICE, 12.5, "middle", True, True)
p.label(-1.6, 0, "C" + SUB3, -9, 4, PRACTICE, 12.5, "end", True, True)
p.label(0, 1.6, "C&#8324;", 0, -9, PRACTICE, 12.5, "middle", True, True)
p.label(0.55, -0.75, "kesişim noktası", 0, 0, TEXT, 10.5, "start", False, True)
p.line([(0.5, -0.66), (0.07, -0.07)], TEXT, 1.0, None, 0.6)
OUT["cauchy-teoremleri-ilmekler"] = figure(
    400, 350, [p],
    "Dört yapraklı gül eğrisi kendini yalnızca başlangıç noktasında keser. Tek bir kapalı <em>C</em> çevresi "
    "olarak dolaşıldığında sırayla <em>C</em><sub>1</sub>, <em>C</em><sub>2</sub>, <em>C</em><sub>3</sub>, "
    "<em>C</em><sub>4</sub> basit kapalı ilmeklerinden geçer; her ilmek pozitif yönlüdür ve kendi içini çevreler. "
    "Cauchy-Goursat teoremi her birine ayrı ayrı uygulanır, integraller toplanır.",
    aria="Kendini kesen kapali egrinin dort basit kapali ilmege ayrilmasi")

# ---- BD2: kesiklerle iki basit çevreye ayırma (çok bağlantılı domen teoremi)
def _r_dis(t):
    return 2.2 + 0.2 * math.cos(2 * t)


C_out = [polar(_r_dis(2 * PI * k / 120), 2 * PI * k / 120) for k in range(120)]
c1, c2, rr = (-0.9, 0.25), (0.9, -0.25), 0.5
L1 = ((-2.4, 0.0), (c1[0] - rr, c1[1]))
L2 = ((c1[0] + rr, c1[1]), (c2[0] - rr, c2[1]))
L3 = ((c2[0] + rr, c2[1]), (2.4, 0.0))


def _half(c, a0, a1, n=36):
    return [(c[0] + rr * math.cos(a0 + (a1 - a0) * k / n), c[1] + rr * math.sin(a0 + (a1 - a0) * k / n)) for k in range(n + 1)]


p = cplane(40, 24, 320, (-2.9, 2.9), (-2.75, 2.75))
gamma1 = C_out[:61] + [L1[1]] + _half(c1, PI, 0) + [L2[1]] + _half(c2, PI, 0) + [L3[1]]
gamma2 = C_out[60:] + [C_out[0], L3[0]] + _half(c2, 0, -PI) + [L2[0]] + _half(c1, 0, -PI) + [L1[0]]
p.polygon(gamma1, THEORY, 0.13)
p.polygon(gamma2, PRACTICE, 0.11)
p.line(C_out + [C_out[0]], BASE, 2.0)
p.arrow(C_out[29], C_out[30], BASE, 2.0, head=8.5)
p.arrow(C_out[89], C_out[90], BASE, 2.0, head=8.5)
p.circle(*c1, rr, BASE, 1.8)
p.circle(*c2, rr, BASE, 1.8)
_circle_arrow(p, *c1, rr, PI / 2, BASE, 1.8, ccw=False)
_circle_arrow(p, *c2, rr, PI / 2, BASE, 1.8, ccw=False)
for a, b in (L1, L2, L3):
    p.line([a, b], REMARK, 1.2)
    _paired_arrows(p, a, b, THEORY, PRACTICE)
p.label(*polar(_r_dis(PI / 4), PI / 4), "C", 8, -4, BASE, 13, "start", True, True)
p.label(*c1, "C" + SUB1, 0, 4, BASE, 11.5, "middle", True, True)
p.label(*c2, "C" + SUB2, 0, 4, BASE, 11.5, "middle", True, True)
p.label(-1.9, 0.125, "L" + SUB1, 0, -13, REMARK, 11.5, "middle", False, True)
p.label(0, 0, "L" + SUB2, 0, -13, REMARK, 11.5, "middle", False, True)
p.label(1.9, -0.125, "L" + SUB3, 0, -13, REMARK, 11.5, "middle", False, True)
p.label(0, 1.3, "&#915;" + SUB1, 0, 4, THEORY, 13.5, "middle", True, True)
p.label(0, -1.3, "&#915;" + SUB2, 0, 4, PRACTICE, 13.5, "middle", True, True)
OUT["cauchy-teoremleri-kesikler"] = figure(
    400, 376, [p],
    "Dış çevre <em>C</em> ile iç çevreler <em>C</em><sub>1</sub>, <em>C</em><sub>2</sub> arasındaki bölge "
    "(<em>f</em>'nin analitik olduğu yer) <em>L</em><sub>1</sub>, <em>L</em><sub>2</sub>, <em>L</em><sub>3</sub> "
    "kesikleriyle iki parçaya bölünür; her parça, bölge solda kalacak biçimde yönlendirilmiş basit kapalı bir "
    "&#915; çevresiyle çevrilir. Her <em>L<sub>k</sub></em> iki kez ve zıt yönlerde katedildiğinden "
    "&#915;<sub>1</sub> ile &#915;<sub>2</sub>'nin integralleri toplanınca kesikler yok olur; geriye pozitif yönlü "
    "<em>C</em> ile negatif yönlü <em>C</em><sub>1</sub>, <em>C</em><sub>2</sub> kalır.",
    aria="Iki delikli bolgenin kesiklerle iki basit kapali cevreye ayrilmasi")

# ---- BD3: yolun deformasyonu ilkesi
C2_pts = blob(0, 0, 2.0, [(0.3, 3, -PI / 2)])
z_s = (0.3, 0.2)
p = cplane(40, 24, 320, (-2.8, 2.8), (-2.6, 2.6))
_ring_fill(p, C2_pts, z_s[0], z_s[1], 0.6, THEORY, 0.11)
closed_curve(p, C2_pts, PRACTICE, 1.9, arrow_at=30)
p.circle(*z_s, 0.6, PRACTICE, 1.9)
_circle_arrow(p, *z_s, 0.6, PI / 2, PRACTICE, 1.9)
cross(p, z_s, REMARK, 4.2, 1.7)
for ang in (0.35, 3.4, 4.5):
    r0 = 2.0 + 0.3 * math.sin(3 * ang)
    start = polar(r0 - 0.2, ang)
    dx, dy = z_s[0] - start[0], z_s[1] - start[1]
    L = math.hypot(dx, dy)
    end = (z_s[0] - dx / L * 0.85, z_s[1] - dy / L * 0.85)
    p.arrow(start, end, BASE, 1.4, head=7.0, dash="4 3")
p.label(*polar(2.0 + 0.3 * math.sin(3 * PI / 4), PI / 4), "C" + SUB2, 8, -4, PRACTICE, 13, "start", True, True)
p.label(z_s[0] + 0.6 * math.cos(PI / 4), z_s[1] + 0.6 * math.sin(PI / 4), "C" + SUB1, 6, -4, PRACTICE, 12.5, "start", True, True)
p.label(z_s[0] - 0.6, z_s[1], "tekil nokta", -8, 0, REMARK, 10.5, "end", False, True)
p.label(-1.15, -0.95, "f analitik", 0, 0, THEORY, 11.5, "middle", False, True)
OUT["cauchy-teoremleri-deformasyon"] = figure(
    400, 368, [p],
    "<em>C</em><sub>2</sub> çevresi, <em>f</em>'nin analitik olduğu gölgeli bölgeden geçerek "
    "<em>C</em><sub>1</sub>'e büzülür; tekil noktanın üstünden geçmediği sürece integral hiç değişmez. "
    "İki çevre de pozitif yönlüdür: çok bağlantılı domen teoremindeki negatif yönlü iç çevre, "
    "&#8722;<em>C</em><sub>1</sub> olarak sağ tarafa taşındığında (3) eşitliği çıkar.",
    aria="Dis cevrenin tekil noktayi cevreleyen ic cembere deforme edilmesi")

# ======================================================= cauchy-integral-formulu
# ---- CIF1: z_0 çevresindeki C_rho çemberi ile C arasındaki bölge
C_pts = blob(0, 0, 2.0, [(0.25, 3, 0.0)])
z0 = (0.4, -0.3)
p = cplane(40, 24, 320, (-2.8, 2.8), (-2.55, 2.55))
_ring_fill(p, C_pts, z0[0], z0[1], 0.5, THEORY, 0.11)
closed_curve(p, C_pts, PRACTICE, 1.9, arrow_at=30)
p.circle(*z0, 0.5, THEORY, 1.9)
_circle_arrow(p, *z0, 0.5, PI / 2, THEORY, 1.9)
p.line([z0, (z0[0] + 0.5, z0[1])], THEORY, 1.2, "4 3", 0.9)
dot(p, z0, TEXT, 3.8)
p.label(*z0, "z" + SUB0, -7, 13, TEXT, 12.5, "end", True, True)
p.label(z0[0] + 0.25, z0[1], "&#961;", 0, -5, THEORY, 12, "middle", False, True)
p.label(z0[0] + 0.5 * math.cos(PI / 4), z0[1] + 0.5 * math.sin(PI / 4), "C" + _sub("&#961;"), 5, -5, THEORY, 12.5, "start", True, True)
p.label(*polar(2.0 + 0.25 * math.cos(3 * PI / 4), PI / 4), "C", 8, -4, PRACTICE, 13, "start", True, True)
p.label(-0.7, 1.25, "f(z)/(z " + MINUS + " z" + SUB0 + ")", 0, 0, THEORY, 11, "middle", False, True)
p.label(-0.7, 1.25, "analitik", 0, 14, THEORY, 11, "middle", False, True)
OUT["cauchy-teoremleri-c-rho"] = figure(
    400, 364, [p],
    "İspatın sahnesi: <em>z</em><sub>0</sub> iç noktası, çevresindeki küçük <em>C<sub>&#961;</sub></em> çemberi ve "
    "aradaki halka. Halka üzerinde <em>f</em>(<em>z</em>)/(<em>z</em> &#8722; <em>z</em><sub>0</sub>) analitik "
    "olduğundan <em>C</em> üzerindeki integral <em>C<sub>&#961;</sub></em> üzerindekine eşittir. Yarıçap, "
    "sürekliliğin verdiği &#948;'dan küçük seçilir (<em>&#961;</em> &lt; <em>&#948;</em>); böylece çember "
    "üzerinde |<em>f</em>(<em>z</em>) &#8722; <em>f</em>(<em>z</em><sub>0</sub>)| &lt; <em>&#949;</em> kalır.",
    aria="Cevre C icindeki z0 noktasi etrafinda kucuk C_rho cemberi ve aradaki halka")

# ---- CIF2: d uzaklığı ve Δz'nin kaldığı disk (türev formülü ispatı)
def _r_C(t):
    return 2.0 + 0.25 * math.cos(3 * t)


C_pts = [polar(_r_C(2 * PI * k / 240), 2 * PI * k / 240) for k in range(240)]
z = (0.6, 0.1)
near = min(C_pts, key=lambda q: math.hypot(q[0] - z[0], q[1] - z[1]))
d = math.hypot(near[0] - z[0], near[1] - z[1])
dz = (0.4, -0.35)
zd = (z[0] + dz[0], z[1] + dz[1])
d2 = d - math.hypot(*dz)
s = polar(_r_C(3.5), 3.5)
p = cplane(30, 24, 340, (-2.55, 2.55), (-2.4, 2.4))
disk_fill(p, z[0], z[1], d, THEORY, 0.08)
p.circle(*z, d, REMARK, 1.2, "5 4", opacity=0.85)
p.circle(*zd, d2, THEORY, 1.2, "5 4", opacity=0.85)
p.line(C_pts + [C_pts[0]], PRACTICE, 1.9)
p.arrow(C_pts[59], C_pts[60], PRACTICE, 1.9, head=8.0)
p.line([z, near], REMARK, 1.4)
u = (-0.6, -0.8)
p.line([zd, (zd[0] + d2 * u[0], zd[1] + d2 * u[1])], THEORY, 1.3)
p.line([s, zd], TEXT, 1.1, "3 3", 0.7)
p.arrow(z, zd, THEORY, 2.2, head=8.0)
dot(p, z, TEXT, 3.8)
dot(p, zd, THEORY, 3.8)
dot(p, s, PRACTICE, 3.8)
dot(p, near, REMARK, 3.0)
p.label(*z, "z", -9, 13, TEXT, 12.5, "end", True, True)
p.label((z[0] + near[0]) / 2, (z[1] + near[1]) / 2, "d", -8, 0, REMARK, 12.5, "end", True, True)
p.label((z[0] + zd[0]) / 2, (z[1] + zd[1]) / 2, "&#916;z", 7, -3, THEORY, 12, "start", True, True)
p.label(*zd, "z+&#916;z", 9, 4, THEORY, 12, "start", True, True)
p.label(zd[0] + d2 * u[0] / 2, zd[1] + d2 * u[1] / 2, "d " + MINUS + " |&#916;z|", 6, 10, THEORY, 11, "start", False, True)
p.label(*s, "s", -10, 4, PRACTICE, 12.5, "end", True, True)
p.label(*polar(_r_C(3 * PI / 4), 3 * PI / 4), "C", -8, -4, PRACTICE, 13, "end", True, True)
OUT["cauchy-teoremleri-d-uzakligi"] = figure(
    400, 348, [p],
    "<em>d</em>, <em>z</em>'nin <em>C</em>'ye en kısa uzaklığıdır: <em>z</em> merkezli <em>d</em> yarıçaplı (kesikli "
    "çizgili) disk <em>C</em>'ye değer ama onu aşmaz. |&#916;<em>z</em>| &lt; <em>d</em> alındığında <em>z</em> + &#916;<em>z</em> "
    "bu diskin içinde kalır ve etrafındaki <em>d</em> &#8722; |&#916;<em>z</em>| yarıçaplı çember de diskin içinde kaldığından "
    "<em>C</em>'yi aşamaz; dolayısıyla <em>C</em> üzerindeki her <em>s</em> için |<em>s</em> &#8722; <em>z</em> &#8722; &#916;<em>z</em>| "
    "&#8805; <em>d</em> &#8722; |&#916;<em>z</em>| &gt; 0 olur ve payda hiçbir zaman sıfırlanmaz.",
    aria="z noktasinin C'ye uzakligi d ve z+dz'nin kaldigi disk")

# ---- CIF3: çemberin içindeki ve dışındaki tekil noktalar (örnek z/((9 - z^2)(z + i)))
p = cplane(40, 24, 320, (-3.9, 3.9), (-2.5, 2.5))
disk_fill(p, 0, 0, 2, THEORY, 0.10)
p.origin_axes(xticks=(-3, -1, 1, 3), yticks=(1,))
closed_curve(p, circle_pts(0, 0, 2), PRACTICE, 1.9, arrow_at=24)
cross(p, (3, 0), BASE, 4.2, 1.7)
cross(p, (-3, 0), BASE, 4.2, 1.7)
dot(p, (0, -1), THEORY, 4.0)
p.label(1.42, 1.42, "C: |z| = 2", 8, -2, PRACTICE, 12, "start", True)
p.label(3, 0, "dışarıda", 0, -10, BASE, 11, "middle", False, True)
p.label(-3, 0, "dışarıda", 0, -10, BASE, 11, "middle", False, True)
p.label(0, -1, "z" + SUB0 + " = " + MINUS + "i", 9, 4, THEORY, 12, "start", True)
p.label(0, -1, "içeride", 9, 18, THEORY, 10.5, "start", False, True)
OUT["cauchy-teoremleri-tekil-noktalar"] = figure(
    400, 324, [p],
    "İntegrandın üç tekil noktası vardır: 9 &#8722; <em>z</em>&#178; = 0 kökleri <em>z</em> = &#177;3 çemberin dışında, "
    "<em>z</em> = &#8722;<em>i</em> ise içindedir. Bu yüzden <em>z</em>/(9 &#8722; <em>z</em>&#178;) çarpanı, <em>C</em> "
    "üzerinde ve içinde analitik olan <em>f</em> rolünü üstlenir; (<em>z</em> + <em>i</em>) paydası ise formülün "
    "<em>z</em> &#8722; <em>z</em><sub>0</sub> çarpanıdır.",
    aria="|z|=2 cemberi, disaridaki tekil noktalar +-3 ve icerideki z0=-i")

# ================================================ liouville-ve-cebirin-temel-teoremi
# ---- L1: birin küp kökleri
roots = [polar(1, 2 * PI * k / 3) for k in range(3)]
p = cplane(40, 24, 320, (-1.9, 1.9), (-1.5, 1.5))
p.origin_axes()
p.circle(0, 0, 1, BASE, 1.3)
p.line([roots[1], roots[2]], BASE, 1.1, "4 3", 0.8)
p.line([(0, 0), roots[1]], BASE, 1.1, "4 3", 0.8)
angle_arc(p, 0, 2 * PI / 3, 0.38, REMARK, 1.6)
for rt in roots:
    dot(p, rt, THEORY, 4.2)
p.label(*roots[0], "z" + SUB1 + " = 1", 9, -8, THEORY, 12, "start", True)
p.label(*roots[1], "z" + SUB2 + " = e" + sup("i2&#960;/3"), -9, 2, THEORY, 12, "end", True)
p.label(*roots[2], "z" + SUB3 + " = e" + sup("i4&#960;/3"), -9, 8, THEORY, 12, "end", True)
p.label(0.3, 0.42, "2&#960;/3", 6, 0, REMARK, 11.5, "start", True)
p.label(-0.5, 0, MINUS + "&#189;", -3, 14, TEXT, 11, "end")
p.label(-0.5, -0.45, "z" + SUB3 + " = " + "z&#773;" + SUB2, 8, 4, BASE, 11, "start", False, True)
OUT["cauchy-teoremleri-kup-kokler"] = figure(
    400, 322, [p],
    "<em>z</em>&#179; = 1 denkleminin kökleri birim çember üzerinde 2&#960;/3'lük eşit aralıklarla dizilir. "
    "<em>z</em><sub>2</sub> ve <em>z</em><sub>3</sub> reel eksene göre birbirinin yansımasıdır: ikisinin de reel kısmı "
    "&#8722;1/2, sanal kısımları &#177;&#8730;3/2. Reel katsayılı <em>z</em>&#179; &#8722; 1'in reel olmayan "
    "köklerinin eşlenik çift oluşturması bu simetridir.",
    aria="Birin uc kup koku birim cember uzerinde, z2 ve z3 eslenik")

# ---- L2: düzlemin iki parçada sınırlanması (cebirin temel teoremi ispatı)
Rr = 1.6
p = cplane(40, 24, 320, (-3.2, 3.2), (-2.9, 2.9))
exterior_fill(p, 0, 0, Rr, PRACTICE, 0.07)
disk_fill(p, 0, 0, Rr, THEORY, 0.13)
p.origin_axes()
p.circle(0, 0, Rr, THEORY, 1.8)
p.line([(0, 0), (Rr, 0)], THEORY, 1.4)
dot(p, (Rr, 0), THEORY, 3.4)
p.label(Rr / 2, 0, "R", 0, -6, THEORY, 12.5, "middle", True, True)
p.label(0, 0, "|z| " + LEQ + " R", 0, -34, THEORY, 12, "middle", True)
p.label(0, 0, "kapalı ve sınırlı:", 0, -18, THEORY, 10.5, "middle", False, True)
p.label(0, 0, "|f| sürekli " + "&#8594;" + " sınırlı", 0, 30, THEORY, 10.5, "middle", False, True)
p.label(3.05, 2.55, "|z| &gt; R:", 0, 0, PRACTICE, 12, "end", True)
p.label(3.05, 2.55, "|f(z)| &lt; 2 / (|a&#8345;| R&#8319;)", 0, 17, PRACTICE, 11.5, "end")
OUT["cauchy-teoremleri-iki-parca"] = figure(
    400, 362, [p],
    "Cebirin temel teoreminin ispatında <em>f</em> = 1/<em>P</em> iki parçada sınırlanır: |<em>z</em>| &gt; <em>R</em> "
    "bölgesinde (5) eşitsizliği |<em>f</em>(<em>z</em>)| &lt; 2/(|<em>a<sub>n</sub></em>|<em>R<sup>n</sup></em>) verir; "
    "kapalı ve sınırlı |<em>z</em>| &#8804; <em>R</em> diskinde ise sürekli <em>f</em>'nin modülü kendiliğinden "
    "sınırlıdır. İki sınırın büyüğü tüm düzlemde geçerlidir ve Liouville teoremi devreye girer.",
    aria="Kapali disk |z| en fazla R ve disi: f her ikisinde ayri ayri sinirlidir")

# ========================================================= maksimum-modul-ilkesi
# ---- M1: çokgensel yol boyunca komşuluk zinciri
D_pts = blob(0, 0, 3.0, [(0.3, 2, 0.0), (0.2, 3, -PI / 2)])
Lp = [(-1.8, -0.35), (-0.8, 0.9), (0.6, -0.3), (2, 0.8)]
zs = [(-1.8, -0.35), (-1.3, 0.275), (-0.8, 0.9), (-0.1, 0.3), (0.6, -0.3), (1.3, 0.25), (2, 0.8)]
dd = 1.0
p = cplane(20, 24, 360, (-3.7, 3.7), (-3.2, 3.0))
closed_curve(p, D_pts, BASE, 1.5, "6 4", BASE, 0.05)
for k in (0, 1, 2, 6):                       # N0, N1 belirgin; N2 ve N_n soluk
    zk, strong = zs[k], k in (0, 1)
    disk_fill(p, zk[0], zk[1], dd, THEORY, 0.07 if strong else 0.04)
    p.circle(*zk, dd, THEORY, 1.6 if strong else 1.0, opacity=0.95 if strong else 0.5)
p.line(Lp, PRACTICE, 2.0)
p.line([zs[0], (zs[0][0] + dd * math.cos(-1.95), zs[0][1] + dd * math.sin(-1.95))], THEORY, 1.2)
p.label(zs[0][0] + 0.5 * math.cos(-1.95), zs[0][1] + 0.5 * math.sin(-1.95), "d", 8, 2, THEORY, 12.5, "start", True, True)
p.points(zs[1:-1], TEXT, 3.2)
dot(p, zs[0], TEXT, 4.0)
dot(p, zs[-1], TEXT, 4.0)
p.label(*zs[0], "z" + SUB0, -7, 14, TEXT, 12.5, "end", True, True)
p.label(*zs[1], "z" + SUB1, 3, 18, TEXT, 12, "start", True, True)      # L'nin sağ altında, N0 yayının 3 px içinde kalır
p.label(*zs[2], "z" + SUB2, -8, -6, TEXT, 12, "end", True, True)       # sol üstte: N1 çemberi z2'nin hemen üstünden geçer
p.label(*zs[-1], "z&#8345; = P", 9, 4, TEXT, 12.5, "start", True, True)
p.label(-2.55, -0.5, "N" + SUB0, 0, 4, THEORY, 12, "middle", True, True)
p.label(-2.25, 1.15, "N" + SUB1, 0, 4, THEORY, 12, "middle", True, True)   # N1'in dışında, N2 yayından uzak
p.label(-1.5, 2.0, "D", 0, 4, BASE, 13.5, "middle", True, True)
OUT["cauchy-teoremleri-komsuluk-zinciri"] = figure(
    400, 372, [p],
    "<em>z</em><sub>0</sub>'ı <em>P</em>'ye bağlayan çokgensel <em>L</em> yolu üzerinde, ardışık uzaklıkları "
    "<em>d</em>'den küçük noktalar seçilir ve her birinin etrafına <em>d</em> yarıçaplı bir <em>N<sub>k</sub></em> "
    "komşuluğu konur (<em>d</em>, <em>L</em>'nin <em>D</em>'nin sınırına en kısa uzaklığı). Her komşuluk "
    "<em>D</em>'nin içindedir ve her <em>z<sub>k</sub></em> bir önceki <em>N</em><sub><em>k</em>&#8722;1</sub>'in "
    "içinde kalır; sabitlik lemması komşuluktan komşuluğa aktarılarak <em>f</em>(<em>P</em>) = <em>f</em>(<em>z</em><sub>0</sub>) "
    "bulunur. Çizimde yalnızca ilk komşuluklar ve sonuncusu gösterilmiştir.",
    aria="Cokgensel yol boyunca ust uste binen komsuluklar zinciri")

# ---- M2: dikdörtgende |sin z| maksimumu
p = cplane(40, 24, 320, (-0.5, 3.7), (-0.55, 1.6))
p.polygon([(0, 0), (PI, 0), (PI, 1), (0, 1)], THEORY, 0.11)
p.origin_axes(xticks=(PI / 2, PI), yticks=(1,), xfmt=lambda v: "&#960;/2" if v < 2 else "&#960;")
p.line([(0, 0), (PI, 0), (PI, 1), (0, 1), (0, 0)], PRACTICE, 1.9)
p.line([(PI / 2, 0), (PI / 2, 1)], BASE, 1.1, "4 3", 0.8)
p.label(0.55, 0.5, "R", 0, 4, THEORY, 13, "middle", True, True)
dot(p, (PI / 2, 1), REMARK, 4.2)
p.label(PI / 2, 1, "z = &#960;/2 + i", 0, -22, REMARK, 12, "middle", True)
p.label(PI / 2, 1, "|sin z| = cosh 1 " + APPROX + " 1,54", 0, -8, REMARK, 11, "middle", False, True)
p.points([(0, 0), (PI, 0)], PRACTICE, 3.6)      # köşeler R'ye aittir: dolu nokta (içi boş nokta = dışlanan nokta)
p.label(0, 0, "|sin z| = 0", 6, 30, PRACTICE, 10.5, "start", False, True)
p.label(PI, 0, "|sin z| = 0", 0, 30, PRACTICE, 10.5, "middle", False, True)
OUT["cauchy-teoremleri-sin-dikdortgen"] = figure(
    400, 236, [p],
    "|sin <em>z</em>|&#178; = sin&#178;<em>x</em> + sinh&#178;<em>y</em> toplamında sin&#178;<em>x</em> terimi "
    "<em>x</em> = &#960;/2'de, artan sinh&#178;<em>y</em> terimi ise üst kenar <em>y</em> = 1'de en büyüktür. Maksimum bu yüzden üst kenarın ortasındaki &#960;/2 + <em>i</em> noktasındadır; "
    "iç noktada değil, teoremin dediği gibi sınırdadır. Alt kenarın köşelerinde ise modül sıfırlanır.",
    aria="0..pi, 0..1 dikdortgeninde |sin z| maksimumunun ust kenarda olmasi")

# ############################################################################
# PART: Seriler
# ############################################################################

# ############################################################################
# PART: Seriler
# ############################################################################

# extra symbols used in this part
THETA_C = "&#920;"      # Θ
GAMMA = "&#947;"        # γ
ARROW = "&#8594;"       # →
SQRT = "&#8730;"        # √


def sub_(s, size=9):
    """Subscript inside an SVG <text> (mirror of sup()): 'Θ' + sub_('2n')."""
    # zero-width space (like svg_plot.sup) so the baseline reset does not eat the caller's own spaces
    return f'<tspan font-size="{size}" dy="4">{s}</tspan><tspan dy="-4">&#8203;</tspan>'


def ring_arrow(p, cx, cy, r, a, color, width=1.8, head=8.0):
    """Arrowhead lying on the circle |z - c| = r at angle a (radians), pointing counter-clockwise."""
    p.arrow((cx + r * math.cos(a - 0.05), cy + r * math.sin(a - 0.05)),
            (cx + r * math.cos(a), cy + r * math.sin(a)), color, width, head=head)


# ========================================================= diziler-ve-seriler
# ---- S1: z_n = -2 + i(-1)^n/n² converges to -2, yet Arg z_n has no limit —
#          the points hop over the negative real axis, where Arg jumps by 2π
zs = [(-2.0, (-1) ** n / n ** 2) for n in range(1, 5)]          # z1 … z4
th2, th1 = math.atan2(zs[1][1], zs[1][0]), math.atan2(zs[0][1], zs[0][0])   # Θ2 ≈ π, Θ1 ≈ −π
p = cplane(40, 24, 330, (-2.95, 0.6), (-1.25, 0.85))
p.line([(-2.9, 0), (0, 0)], REMARK, 3.2, None, 0.4)               # the axis where Arg is discontinuous
p.origin_axes()
p.line([(0, 0), zs[0]], REMARK, 1.1, "3 3", 0.6)
p.line([(0, 0), zs[1]], REMARK, 1.1, "3 3", 0.6)
angle_arc(p, 0, th2 - 0.02, 0.42, THEORY, 1.8)
angle_arc(p, 0, th1 + 0.02, 0.32, PRACTICE, 1.8)
for k, (z, rad) in enumerate(zip(zs, (4.0, 3.6, 3.0, 2.5))):
    dot(p, z, PRACTICE if k % 2 == 0 else THEORY, rad)             # odd n below (red), even n above (blue)
p.label(*zs[0], "z" + SUB1 + " = " + MINUS + "2 " + MINUS + " i", 9, 4, PRACTICE, 12, "start", True)
p.label(*zs[1], "z" + SUB2 + " = " + MINUS + "2 + i/4", 9, -5, THEORY, 12, "start", True)
p.label(*zs[2], "z" + SUB3, 8, 13, PRACTICE, 11.5, "start", True)
p.label(*zs[3], "z&#8324;", -8, -4, THEORY, 11.5, "end", True)
p.label(-2, 0, "z" + sub_("n") + " " + ARROW + " " + MINUS + "2", -9, 15, TEXT, 11.5, "end", True)
p.label(-0.35, 0.55, THETA_C + SUB2 + " " + APPROX + " " + PI_S, 0, 0, THEORY, 11.5, "end", True)
p.label(-0.12, -0.62, THETA_C + SUB1 + " &lt; 0", 0, 0, PRACTICE, 11.5, "end", True)
p.label(-2.9, 0.62, THETA_C + sub_("2n") + " " + ARROW + " " + PI_S + "  (&#252;stten)", 0, 0, THEORY, 11, "start", False, True)
p.label(-2.9, -0.62, THETA_C + sub_("2n" + MINUS + "1") + " " + ARROW + " " + MINUS + PI_S + "  (alttan)", 0, 0, PRACTICE, 11, "start", False, True)
OUT["seriler-arg-sicrama"] = figure(
    400, 244, [p],
    "<em>z<sub>n</sub></em> = &#8722;2 + <em>i</em>(&#8722;1)<sup><em>n</em></sup>/<em>n</em>&#178; dizisi &#8722;2'ye yakınsar; "
    "ama terimler negatif reel eksenin bir üstüne bir altına düşer. Üstteki (çift indisli) terimlerin esas argümanı "
    "&#960;'ye, alttakilerin &#8722;&#960;'ye yaklaşır: nokta ve modül yakınsarken Arg <em>z<sub>n</sub></em>'nin limiti yoktur, "
    "çünkü esas argüman bu eksende 2&#960; sıçrar.",
    aria="Negatif reel eksene bir ustten bir alttan yaklasan dizi; esas arguman pi ile -pi arasinda salinir")

# ============================================================= taylor-serileri
# ---- T1: geometry of the proof of Taylor's theorem: r < r0 < R0 and |s - z| >= r0 - r
R0, r0 = 3.4, 1.9
z = (1.25, 0.4)                                   # |z| = r ≈ 1.31
s = polar(r0, math.radians(65))                   # a point of C0
p = cplane(40, 24, 320, (-3.9, 3.9), (-3.7, 3.7))
disk_fill(p, 0, 0, R0, THEORY, 0.07)
p.origin_axes()
p.circle(0, 0, R0, REMARK, 1.1, "5 4", opacity=0.75)
p.circle(0, 0, r0, THEORY, 1.8)
ring_arrow(p, 0, 0, r0, 3 * PI / 4, THEORY)
p.line([(0, 0), z], THEORY, 1.2, "3 3", 0.85)     # r = |z|
p.line([(0, 0), s], REMARK, 1.2, None, 0.85)      # r0 = |s|
p.line([s, z], PRACTICE, 1.9)                     # |s - z|
dot(p, z, THEORY, 4.0)
dot(p, s, PRACTICE, 4.0)
p.label(*z, "z", 8, 13, THEORY, 12.5, "start", True, True)
p.label(*s, "s", 8, -3, PRACTICE, 12.5, "start", True, True)
p.label(0.375, 0.12, "r", 0, -6, THEORY, 11.5, "middle", False, True)
p.label(0.337, 0.723, "r" + SUB0, 8, 4, REMARK, 11.5, "start", False, True)
p.label(*polar(r0, 3 * PI / 4), "C" + SUB0, -7, -5, THEORY, 12, "end", True, True)
p.label(-0.25, -2.9, "|z| = R" + SUB0, 0, 0, REMARK, 11, "end", False, True)
p.label(0.6, 2.25, "|s " + MINUS + " z| " + GEQ + " r" + SUB0 + " " + MINUS + " r", 0, 0, PRACTICE, 11.5, "middle", True)
OUT["seriler-taylor-ispat"] = figure(
    400, 352, [p],
    "Taylor teoremi ispatının sahnesi: <em>f</em>, kesikli |<em>z</em>| = <em>R</em><sub>0</sub> çemberinin içinde analitiktir. "
    "Sabit <em>z</em> noktası (|<em>z</em>| = <em>r</em>) ile bu çember arasına ara bir "
    "<em>C</em><sub>0</sub> : |<em>s</em>| = <em>r</em><sub>0</sub> çemberi yerleştirilir (<em>r</em> &lt; <em>r</em><sub>0</sub> &lt; <em>R</em><sub>0</sub>). "
    "<em>C</em><sub>0</sub> üzerindeki her <em>s</em> için |<em>s</em> &#8722; <em>z</em>| &#8805; <em>r</em><sub>0</sub> &#8722; <em>r</em> "
    "olduğundan kalan, (<em>r</em>/<em>r</em><sub>0</sub>)<sup><em>N</em></sup> çarpanıyla sıfıra gider.",
    aria="Taylor teoremi ispati: ic ice r, r0, R0 yaricaplari ve C0 cemberi uzerindeki s noktasi")

# ---- T2: 1/z about z0 = 1 — the disk grows until it touches the singularity at 0
p = cplane(40, 24, 320, (-1.3, 2.5), (-1.35, 1.35))
disk_fill(p, 1, 0, 1, THEORY, 0.12)
p.origin_axes()
p.circle(1, 0, 1, THEORY, 1.8)
p.line([(0, 0), (1, 0)], PRACTICE, 1.4, "5 4")
cross(p, (0, 0), PRACTICE, 4.5, 1.8)
dot(p, (1, 0), THEORY, 4.0)
p.label(0, 0, "0: tekil nokta", -8, 16, PRACTICE, 11.5, "end", True)
p.label(1, 0, "z" + SUB0 + " = 1", 0, 17, THEORY, 12, "middle", True)
p.label(0.5, 0, "R = 1", 0, -8, PRACTICE, 11.5, "middle", False, True)
p.label(1, 0.55, "|z " + MINUS + " 1| &lt; 1", 0, 0, THEORY, 12.5, "middle", True, True)
OUT["seriler-taylor-1z-yaricap"] = figure(
    400, 276, [p],
    "1/<em>z</em> fonksiyonunun tek tekil noktası 0'dır. <em>z</em><sub>0</sub> = 1 merkezli Taylor açılımı, "
    "merkezden büyüyüp tekil noktaya değen en büyük diskte, yani |<em>z</em> &#8722; 1| &lt; 1'de geçerlidir: "
    "yakınsaklık yarıçapı, merkezden en yakın tekil noktaya olan uzaklıktır.",
    aria="1/z fonksiyonunun z0 = 1 civarindaki Taylor diski: yaricap 1, cember tekil nokta 0'dan gecer")

# ============================================================ laurent-serileri
# ---- L1: geometry of the proof of Laurent's theorem: R1 < r1 < r < r2 < R2, contours C1, C2, γ
R1, R2, r1, r2 = 1.0, 3.3, 1.5, 2.7
z = polar(2.0, math.radians(35))                   # |z| = r = 2
s = polar(r2, math.radians(110))                   # a point of C2
p = cplane(40, 24, 320, (-3.8, 3.8), (-3.6, 3.6))
annulus_fill(p, 0, 0, R1, R2, THEORY, 0.07)        # domain of analyticity
annulus_fill(p, 0, 0, r1, r2, THEORY, 0.07)        # the closed annulus r1 <= |z| <= r2 (double tint)
p.origin_axes()
p.circle(0, 0, R1, REMARK, 1.1, "5 4", opacity=0.75)
p.circle(0, 0, R2, REMARK, 1.1, "5 4", opacity=0.75)
p.circle(0, 0, r1, THEORY, 1.8)
ring_arrow(p, 0, 0, r1, PI / 2, THEORY)
p.circle(0, 0, r2, THEORY, 1.8)
ring_arrow(p, 0, 0, r2, PI / 2, THEORY)
p.circle(*z, 0.3, PRACTICE, 1.8)
ring_arrow(p, z[0], z[1], 0.3, PI / 2, PRACTICE, 1.8, 7.0)
p.line([(0, 0), z], REMARK, 1.1, "3 3", 0.7)       # |z| = r
dot(p, z, PRACTICE, 3.6)
dot(p, s, TEXT, 3.6)
p.label(*z, "z", 16, 17, PRACTICE, 12.5, "start", True, True)
p.label(*z, GAMMA, -15, -7, PRACTICE, 12.5, "end", True, True)
p.label(*s, "s", -9, -2, TEXT, 12.5, "end", True, True)
p.label(0, r1, "C" + SUB1, -9, -4, THEORY, 12, "end", True, True)
p.label(0, r2, "C" + SUB2, -9, -4, THEORY, 12, "end", True, True)
p.label(R1, 0, "R" + SUB1, 3, 14, REMARK, 11.5, "start", False, True)
p.label(0, -R2, "R" + SUB2, 7, 4, REMARK, 11.5, "start", False, True)
p.label(1.016, 0.711, "r", 3, 12, REMARK, 11.5, "start", False, True)
OUT["seriler-laurent-ispat"] = figure(
    400, 352, [p],
    "Laurent teoremi ispatının sahnesi: <em>f</em>, kesikli çemberler arasındaki <em>R</em><sub>1</sub> &lt; |<em>z</em>| &lt; <em>R</em><sub>2</sub> "
    "halkasında analitiktir. İçine, <em>z</em> noktasını barındıran kapalı <em>r</em><sub>1</sub> &#8804; |<em>z</em>| &#8804; <em>r</em><sub>2</sub> "
    "halkası ve sınır çemberleri <em>C</em><sub>1</sub>, <em>C</em><sub>2</sub> yerleştirilir; <em>z</em>'nin çevresine de küçük bir "
    "<em>&#947;</em> çemberi. <em>C</em><sub>2</sub> üzerindeki <em>s</em> için |<em>z</em>/<em>s</em>| &lt; 1, "
    "<em>C</em><sub>1</sub> üzerindekiler için |<em>s</em>/<em>z</em>| &lt; 1 olduğundan iki farklı geometrik seri açılımı kullanılır.",
    aria="Laurent teoremi ispati: ic ice R1, r1, r2, R2 yaricapli cemberler, z noktasi ve etrafindaki kucuk gamma cemberi")

# ---- L2: f(z) = -1/((z-1)(z-2)) is analytic in three concentric domains D1, D2, D3
p = cplane(40, 24, 320, (-3.4, 3.4), (-3.0, 3.0))
exterior_fill(p, 0, 0, 2, REMARK, 0.07)
annulus_fill(p, 0, 0, 1, 2, BASE, 0.12)
disk_fill(p, 0, 0, 1, THEORY, 0.14)
p.origin_axes()
p.circle(0, 0, 1, REMARK, 1.2, "5 4", opacity=0.8)
p.circle(0, 0, 2, REMARK, 1.2, "5 4", opacity=0.8)
cross(p, (1, 0), PRACTICE, 4.5, 1.8)
cross(p, (2, 0), PRACTICE, 4.5, 1.8)
p.label(1, 0, "z = 1", 6, -7, PRACTICE, 11.5, "start", True)
p.label(2, 0, "z = 2", 6, -7, PRACTICE, 11.5, "start", True)
p.label(-0.45, 0.45, "D" + SUB1, 0, 0, THEORY, 13, "middle", True, True)
p.label(-1.06, 1.06, "D" + SUB2, 0, 0, BASE, 13, "middle", True, True)
p.label(-1.9, 1.9, "D" + SUB3, 0, 0, REMARK, 13, "middle", True, True)
OUT["seriler-uc-halka"] = figure(
    400, 330, [p],
    "<em>f</em>(<em>z</em>) = &#8722;1/[(<em>z</em> &#8722; 1)(<em>z</em> &#8722; 2)] fonksiyonunun tekil noktaları 1 ve 2'dir. "
    "Bu noktalardan geçen orijin merkezli çemberler düzlemi üç domene böler: <em>D</em><sub>1</sub> diski, "
    "<em>D</em><sub>2</sub> halkası ve <em>D</em><sub>3</sub> dış bölgesi. <em>f</em> her birinde analitiktir ve her birinde "
    "farklı bir Laurent serisine sahiptir; halka seçilmeden \"<em>f</em>'nin Laurent serisi\" belirsizdir.",
    aria="Tekil noktalar 1 ve 2'den gecen cemberlerin ayirdigi uc domen: disk D1, halka D2, dis bolge D3")

# ============================================ kuvvet-serilerinin-yakinsakligi
# ---- K1: convergence at z1 spreads to the whole disk through z1; nothing outside the circle of convergence
R, R1, R2 = 2.6, 1.6, 3.45
z1 = polar(R1, math.radians(35))
z2 = polar(R2, math.radians(40))
p = cplane(40, 24, 320, (-3.95, 3.95), (-3.7, 3.7))
disk_fill(p, 0, 0, R, THEORY, 0.06)
disk_fill(p, 0, 0, R1, THEORY, 0.14)
p.origin_axes()
p.circle(0, 0, R, THEORY, 2.0)
p.circle(0, 0, R1, THEORY, 1.3, "5 4")
p.circle(0, 0, R2, PRACTICE, 1.3, "5 4", opacity=0.85)
p.line([(0, 0), z1], THEORY, 1.2, "3 3", 0.85)
dot(p, (0, 0), TEXT, 3.6)
dot(p, z1, THEORY, 4.0)
hollow(p, z2, PRACTICE, 4.0, 1.8)
p.label(0, 0, "z" + SUB0, -7, 15, TEXT, 12, "end", True, True)
p.label(*z1, "z" + SUB1, 8, -4, THEORY, 12.5, "start", True, True)
p.label(0.63, 0.44, "R" + SUB1, 4, 13, THEORY, 11.5, "start", False, True)
p.label(*z2, "z" + SUB2, 8, -2, PRACTICE, 12.5, "start", True, True)
p.label(0, -0.8, "mutlak yakınsak", 0, 0, THEORY, 11.5, "middle", True)
p.label(0, 2.78, "yakınsaklık çemberi", 0, 0, THEORY, 11.5, "middle", True)
p.label(-R, 0, "R", -4, -5, THEORY, 11.5, "end", False, True)
p.label(0, -2.95, "z" + SUB2 + "'de yakınsasaydı", 0, 0, PRACTICE, 11.5, "middle", False, True)
p.label(0, -3.25, "(&#231;eli&#351;ki)", 0, 0, PRACTICE, 11.5, "middle", False, True)
OUT["seriler-yakinsaklik-cemberi"] = figure(
    400, 348, [p],
    "Seri <em>z</em><sub>1</sub>'de yakınsıyorsa, <em>z</em><sub>0</sub> merkezli ve <em>z</em><sub>1</sub>'den geçen çemberin "
    "içinde (koyu disk) mutlak yakınsar: yakınsaklık içeri doğru yayılır. Böyle disklerin en büyüğünün sınırı yakınsaklık çemberidir. "
    "Dışarıdaki bir <em>z</em><sub>2</sub>'de yakınsasaydı, aynı teorem <em>z</em><sub>2</sub>'den geçen kesikli çemberin içini de "
    "yakınsaklık bölgesi yapar ve ilk çember \"en büyük\" olmazdı.",
    aria="Yakinsaklik cemberi: z1'den gecen disk mutlak yakinsak, cemberin disindaki z2 noktasinda yakinsama yok")

# ---- K2: 1/(1+z²) is smooth on the real axis, yet the Maclaurin radius is 1 because of ±i
p = cplane(40, 24, 320, (-1.8, 1.8), (-1.75, 1.75))
disk_fill(p, 0, 0, 1, THEORY, 0.12)
p.origin_axes()
p.circle(0, 0, 1, THEORY, 1.8)
p.line([(-1.65, 0), (1.65, 0)], THEORY, 3.4, None, 0.5)   # f is smooth on the whole real axis
cross(p, (0, 1), PRACTICE, 4.5, 1.8)
cross(p, (0, -1), PRACTICE, 4.5, 1.8)
p.label(0, 1, "i", 9, 4, PRACTICE, 12.5, "start", True, True)
p.label(0, -1, MINUS + "i", 9, 5, PRACTICE, 12.5, "start", True, True)
p.label(0, -0.45, "|z| &lt; 1: seri yakınsar", 0, 0, THEORY, 11.5, "middle", True)
p.label(1.72, -1.3, "reel eksende f sorunsuz,", 0, 0, PRACTICE, 11, "end", False, True)
p.label(1.72, -1.57, "ama seri ıraksar", 0, 0, PRACTICE, 11, "end", False, True)
OUT["seriler-tekil-nokta-i"] = figure(
    400, 360, [p],
    "1/(1 + <em>z</em>&#178;) reel eksenin her noktasında düzgün ve sonsuz kez türevlenebilirdir; yine de Maclaurin serisi "
    "yalnız |<em>z</em>| &lt; 1'de yakınsar. Engel reel eksende değil, sanal eksendedir: tekil noktalar &#177;<em>i</em> "
    "merkeze 1 uzaklıktadır ve yakınsaklık çemberi onlara değince büyümesi durur.",
    aria="1/(1+z^2) icin birim disk: tekil noktalar i ve -i sanal eksende, reel eksende sorun gorunmez")

# ---- K3: a series in negative powers converges OUTSIDE a circle; with the positive part it gives the Laurent annulus
R1, R2 = 1.2, 2.7
z1 = polar(R1, math.radians(40))
p = cplane(40, 24, 320, (-3.4, 3.4), (-3.4, 3.4))
exterior_fill(p, 0, 0, R1, PRACTICE, 0.10)
disk_fill(p, 0, 0, R2, THEORY, 0.10)
p.origin_axes()
p.circle(0, 0, R1, PRACTICE, 1.8)
p.circle(0, 0, R2, THEORY, 1.4, "5 4")
dot(p, (0, 0), TEXT, 3.6)
dot(p, z1, PRACTICE, 4.0)
p.label(0, 0, "z" + SUB0, -7, 15, TEXT, 12, "end", True, True)
p.label(*z1, "z" + SUB1, 8, -3, PRACTICE, 12.5, "start", True, True)
p.label(-R1, 0, "R" + SUB1, -4, -5, PRACTICE, 11.5, "end", False, True)
p.label(-R2, 0, "R" + SUB2, -4, -5, THEORY, 11.5, "end", False, True)
p.label(0, 2.05, "pozitif kuvvetler", 0, 0, THEORY, 11, "middle", True)
p.label(0, 1.75, "|z " + MINUS + " z" + SUB0 + "| &lt; R" + SUB2 + "'de yakınsar", 0, 0, THEORY, 11, "middle")
p.label(0, -1.9, "Laurent halkası", 0, 0, TEXT, 11.5, "middle", True, True)
p.label(-3.2, -2.95, "negatif kuvvetler", 0, 0, PRACTICE, 11, "start", True)
p.label(-3.2, -3.25, "|z " + MINUS + " z" + SUB0 + "| &gt; R" + SUB1 + "'de yakınsar", 0, 0, PRACTICE, 11, "start")
OUT["seriler-negatif-kuvvet-dis"] = figure(
    400, 368, [p],
    "Negatif kuvvetli seri, <em>w</em> = 1/(<em>z</em> &#8722; <em>z</em><sub>0</sub>) değişimiyle sıradan bir kuvvet serisine döner; "
    "|<em>w</em>| küçük demek |<em>z</em> &#8722; <em>z</em><sub>0</sub>| büyük demektir. Bu yüzden bir <em>z</em><sub>1</sub> "
    "noktasında yakınsıyorsa, <em>z</em><sub>1</sub>'den geçen çemberin <strong>dışında</strong> (taralı dış bölge) mutlak yakınsar. "
    "Pozitif kuvvetli kısım ise bir diskte yakınsar; iki bölgenin kesişimi Laurent halkasıdır.",
    aria="Negatif kuvvetli seri R1 yaricapli cemberin disinda, pozitif kuvvetli seri R2 yaricapli diskin icinde yakinsar; kesisim halka")

# ======================================================= kuvvet-serileriyle-islemler
# ---- I1: 1/(z² sinh z): the punctured disk 0 < |z| < π reaches the nearest zeros ±πi of sinh
p = cplane(40, 24, 320, (-4.0, 4.0), (-3.9, 3.9))
disk_fill(p, 0, 0, PI, THEORY, 0.12)
p.origin_axes()
p.circle(0, 0, PI, THEORY, 1.6, "5 4")
cross(p, (0, PI), PRACTICE, 4.5, 1.8)
cross(p, (0, -PI), PRACTICE, 4.5, 1.8)
hollow(p, (0, 0), PRACTICE, 4.2, 1.8)
p.label(0, PI, PI_S + "i", 9, -3, PRACTICE, 12.5, "start", True, True)
p.label(0, -PI, MINUS + PI_S + "i", 9, 13, PRACTICE, 12.5, "start", True, True)
p.label(0, 0, "0 d&#305;&#351;ar&#305;da", 9, 15, PRACTICE, 11.5, "start", True)
p.label(1.1, -1.5, "0 &lt; |z| &lt; " + PI_S, 0, 0, THEORY, 12.5, "middle", True, True)
OUT["seriler-sinh-delinmis-disk"] = figure(
    400, 360, [p],
    "1/(<em>z</em>&#178; sinh <em>z</em>) fonksiyonu 0'da analitik değildir; sinh <em>z</em>'nin diğer sıfırları "
    "<em>n</em>&#960;<em>i</em> (<em>n</em> &#8800; 0) noktalarıdır ve orijine en yakınları &#177;&#960;<em>i</em>'dir. Bu yüzden Laurent açılımı, "
    "merkezi dışarıda bırakan 0 &lt; |<em>z</em>| &lt; &#960; delinmiş diskinde geçerlidir.",
    aria="Delinmis disk 0 &lt; |z| &lt; pi: merkez 0 haric, sinir sinh z'nin sifirlari pi i ve -pi i'den gecer")

# ############################################################################
# PART: Rezidüler ve Kutuplar
# ############################################################################

# ############################################################################
# PART: Rezidü (ayrık tekil noktalar, rezidü teoremi, tekil nokta türleri,
#       sıfırlar ve kutuplar, tekil noktalarda davranış)
# ############################################################################
def circ_arrow(p, cx, cy, r, a, color, width=1.8, ccw=True, head=8.0):
    """Arrowhead ON a circle at angle a (radians); ccw=False gives clockwise."""
    d = 0.12 if ccw else -0.12
    p.arrow((cx + r * math.cos(a - d), cy + r * math.sin(a - d)),
            (cx + r * math.cos(a), cy + r * math.sin(a)), color, width, head=head)


def cut(p, p0, p1, color=PRACTICE):
    """Branch cut: thick, low-opacity segment."""
    p.line([p0, p1], color, 3.2, None, 0.35)


# ================================================= ayrık-tekil-noktalar-ve-rezidü
# ---- R1: the singular points 1/n of 1/sin(pi/z) accumulate at the origin
p = cplane(40, 24, 320, (-1.3, 1.3), (-0.62, 0.62))
EPS = 0.3
disk_fill(p, 0, 0, EPS, REMARK, 0.12)
p.origin_axes()
p.circle(0, 0, EPS, REMARK, 1.3, "4 3")
p.line([(0, 0), polar(EPS, PI / 4)], REMARK, 1.1)
p.label(*polar(EPS / 2, PI / 4), "&#949;", -3, -5, REMARK, 12, "end", True, True)
ns = [1, 2, 3, 4, 5, 6, 8, 10, 15]
for k, n in enumerate(ns):
    rad = 4.0 - 0.27 * k
    p.points([(1 / n, 0), (-1 / n, 0)], PRACTICE, rad)
for n, txt in ((1, "1"), (2, "1/2"), (-1, MINUS + "1"), (-2, MINUS + "1/2")):
    p.label(1 / n, 0, txt, 0, 16, TEXT, 10.5, "middle")
hollow(p, (0, 0), TEXT, 3.4)
p.label(0, 0, "0", -6, -8, TEXT, 11.5, "end", True)
p.label(1.25, 0.45, "z<tspan font-size=\"9\" dy=\"3\">n</tspan><tspan dy=\"-3\" dx=\"3\">= 1/n &#8594; 0</tspan>", 0, 0, THEORY, 11.5, "end", True)
p.text_px(44, 24 + p.h - 20, "&#949; = 0,3 i&#231;in 1/4, 1/5, 1/6, &#8230;", TEXT, 11, "start", False, True)
p.text_px(44, 24 + p.h - 6, "hepsi i&#231;eride", TEXT, 11, "start", False, True)
OUT["rezidu-yigilma-noktasi"] = figure(
    400, int(p.h) + 48, [p],
    "1/sin(&#960;/<em>z</em>) fonksiyonunun tekil noktalar&#305; 0 ve 1/<em>n</em> (<em>n</em> = &#177;1, &#177;2, &#8230;) say&#305;lar&#305;d&#305;r; "
    "1/<em>n</em> noktalar&#305; orijine y&#305;&#287;&#305;l&#305;r. "
    "Her bir 1/<em>n</em> ayr&#305;kt&#305;r; ama 0 de&#287;ildir: &#949; ne kadar k&#252;&#231;&#252;k se&#231;ilirse se&#231;ilsin, "
    "0 &lt; |<em>z</em>| &lt; &#949; delinmi&#351; diski 1/<em>m</em> &lt; &#949; ko&#351;ulunu sa&#287;layan sonsuz &#231;oklukta tekil nokta i&#231;erir.",
    aria="1/n tekil noktalarinin orijinde yigilmasi; epsilon diski sonsuz cogunu icerir")

# ---- R2: for Log z the cut enters every punctured neighbourhood of 0
p = cplane(40, 24, 320, (-1.8, 1.2), (-1.0, 1.0))
EPS = 0.6
disk_fill(p, 0, 0, EPS, THEORY, 0.10)
p.origin_axes()
cut(p, (-1.78, 0), (0, 0))
p.line([(-EPS, 0), (0, 0)], PRACTICE, 3.6)
p.circle(0, 0, EPS, THEORY, 1.5, "5 4")
hollow(p, (0, 0), TEXT, 3.4)
p.label(0, 0, "0", 8, -6, TEXT, 11.5, "start", True)
p.label(-1.75, 0, "dal kesimi", 0, -9, PRACTICE, 11.5, "start", True)
p.label(-1.75, 0, "Log tan&#305;ms&#305;z", 0, 15, PRACTICE, 10.5, "start", False, True)
p.label(*polar(EPS, PI / 4), "0 &lt; |z| &lt; &#949;", 6, -4, THEORY, 11.5, "start", True)
p.text_px(44, 24 + p.h - 20, "her &#949; i&#231;in kesimin bir par&#231;as&#305;", TEXT, 11, "start", False, True)
p.text_px(44, 24 + p.h - 6, "(koyu) kom&#351;ulu&#287;un i&#231;inde kal&#305;r", TEXT, 11, "start", False, True)
OUT["rezidu-log-kesim"] = figure(
    400, int(p.h) + 48, [p],
    "Log <em>z</em> i&#231;in tekillik yaln&#305;z orijinde de&#287;il, negatif reel eksenin tamam&#305;ndad&#305;r (dal kesimi). "
    "Orijinin her delinmi&#351; &#949;-kom&#351;ulu&#287;u bu kesimden bir par&#231;a i&#231;erdi&#287;inden, fonksiyonun "
    "her yerinde analitik oldu&#287;u bir delinmi&#351; disk bulunamaz: 0 tekil ama <strong>ayr&#305;k de&#287;ildir</strong>.",
    aria="Negatif reel eksendeki dal kesimi orijinin her delinmis komsulugunu keser")

# ---- R3: contour |z-2| = 1 and the Laurent annulus 0 < |z-2| < 2
p = cplane(40, 24, 320, (-0.8, 4.6), (-2.3, 2.3))
disk_fill(p, 2, 0, 2, THEORY, 0.10)
p.origin_axes()
p.circle(2, 0, 2, THEORY, 1.4, "5 4")
p.circle(2, 0, 1, PRACTICE, 2.0)
circ_arrow(p, 2, 0, 1, PI / 2, PRACTICE, 2.0)
cross(p, (0, 0), PRACTICE)
cross(p, (2, 0), PRACTICE)
p.label(0, 0, "0", -8, 14, PRACTICE, 12, "end", True)
p.label(0, 0, "(d&#305;&#351;ar&#305;da)", -8, 27, PRACTICE, 10.5, "end", False, True)
p.label(2, 0, "2", 7, 14, PRACTICE, 12, "start", True)
p.label(2, 1, "C: |z " + MINUS + " 2| = 1", 0, -9, PRACTICE, 11.5, "middle", True)
p.label(2 + 2 * math.cos(PI / 4), 2 * math.sin(PI / 4), "|z " + MINUS + " 2| = 2", 6, -2, THEORY, 11.5, "start", True)
p.label(2, -1.3, "0 &lt; |z " + MINUS + " 2| &lt; 2", 0, 4, THEORY, 11.5, "middle", True, True)
p.label(2, -1.3, "a&#231;&#305;l&#305;m burada ge&#231;erli", 0, 18, THEORY, 10.5, "middle", False, True)
OUT["rezidu-kaydirilmis-halka"] = figure(
    400, int(p.h) + 48, [p],
    "&#199;evre <em>C</em> yaln&#305;z <em>z</em> = 2 tekil noktas&#305;n&#305; sarar; a&#231;&#305;l&#305;m bu y&#252;zden 2 merkezlidir. "
    "Kesikli &#231;ember di&#287;er tekil nokta 0'dan ge&#231;er: 0 &lt; |<em>z</em> &#8722; 2| &lt; 2 halkas&#305;, "
    "Laurent serisinin ge&#231;erli oldu&#287;u en b&#252;y&#252;k delinmi&#351; disktir ve <em>C</em> onun i&#231;inde kal&#305;r.",
    aria="|z-2|=1 cemberi ve 0&lt;|z-2|&lt;2 halkasi; 0 noktasi halkanin sinirinda")

# ======================================================== cauchy-rezidü-teoremi
# ---- R4: proof of the residue theorem — C minus the small circles C_k
p = cplane(40, 24, 320, (-3.9, 3.9), (-2.7, 2.7))
raw = blob(0, 0, 2.55, [(0.22, 2, 0.6), (0.12, 3, 2.2)])
Cpts = [(1.27 * x, 0.82 * y) for x, y in raw]
zs = [(-1.75, 0.5), (0.35, -0.95), (1.75, 0.7)]
RK = 0.5
# shaded region: inside C, outside the three C_k (even-odd fill)
d = " ".join(("M" if i == 0 else "L") + p.P(x, y) for i, (x, y) in enumerate(Cpts)) + " Z"
for (cx, cy) in zs:
    rr = p.R(RK)
    d += (f" M{p.X(cx + RK):.1f},{p.Y(cy):.1f} A{rr:.1f},{rr:.1f} 0 1,0 {p.X(cx - RK):.1f},{p.Y(cy):.1f}"
          f" A{rr:.1f},{rr:.1f} 0 1,0 {p.X(cx + RK):.1f},{p.Y(cy):.1f} Z")
p.add(f'<path d="{d}" fill="{BASE}" fill-opacity="0.10" fill-rule="evenodd" stroke="none"/>')
p.origin_axes(opacity=0.3)
closed_curve(p, Cpts, THEORY, 2.0, arrow_at=0)
for k, (cx, cy) in enumerate(zs):
    p.circle(cx, cy, RK, PRACTICE, 1.7)
    circ_arrow(p, cx, cy, RK, PI / 2 if k != 1 else -PI / 2, PRACTICE, 1.7, head=7.0)
    cross(p, (cx, cy), PRACTICE, 3.6)
p.label(*zs[0], "z" + SUB1, -25, 4, PRACTICE, 12, "end", True, True)
p.label(*zs[0], "C" + SUB1, 9, 30, PRACTICE, 11.5, "start", True, True)
p.label(*zs[1], "z" + SUB2, 25, 4, PRACTICE, 12, "start", True, True)
p.label(*zs[1], "C" + SUB2, -8, -25, PRACTICE, 11.5, "end", True, True)
p.label(*zs[2], "z" + SUB3, 25, 4, PRACTICE, 12, "start", True, True)
p.label(*zs[2], "C" + SUB3, -8, 28, PRACTICE, 11.5, "end", True, True)
p.label(*Cpts[0], "C", 8, -8, THEORY, 13, "start", True, True)
p.label(-0.6, 1.5, "f analitik", 0, 0, BASE, 11.5, "middle", True, True)
p.label(0.6, -1.9, "&#8230;", 0, 0, TEXT, 13, "middle", True)
OUT["rezidu-teorem-ispat"] = figure(
    400, int(p.h) + 48, [p],
    "&#304;spat&#305;n resmi: her tekil noktay&#305; saran k&#252;&#231;&#252;k pozitif y&#246;nl&#252; <em>C<sub>k</sub></em> &#231;emberleri "
    "<em>C</em> ile birlikte &#231;ok ba&#287;lant&#305;l&#305; bir b&#246;lgeyi s&#305;n&#305;rlar; g&#246;lgeli b&#246;lgede <em>f</em> analitiktir. "
    "Cauchy-Goursat teoremi &#8747;<sub><em>C</em></sub> &#8722; &#931; &#8747;<sub><em>C<sub>k</sub></em></sub> = 0 verir, "
    "her k&#252;&#231;&#252;k &#231;ember de 2&#960;<em>i</em> &#183; Rez katk&#305;s&#305; yapar.",
    aria="C cevresi icinde tekil noktalari saran kucuk cemberler; aradaki bolge golgeli")

# ---- R5: contours for the residue at infinity
p = cplane(40, 24, 320, (-3.2, 3.2), (-3.2, 3.2))
R1, R0 = 1.9, 2.7
raw = blob(0.2, 0.1, 1.15, [(0.12, 2, 1.0), (0.08, 3, 0.3)])
# C must stay clearly inside |z| = R1 (max |z| on C is about 1.64)
Cpts = [(0.2 + 1.10 * (x - 0.2), 0.1 + 0.9 * (y - 0.1)) for x, y in raw]
# shaded region: between C and C_0 (even-odd fill) -- f is analytic there, so the path can be deformed
rr = p.R(R0)
d = (f"M{p.X(R0):.1f},{p.Y(0):.1f} A{rr:.1f},{rr:.1f} 0 1,0 {p.X(-R0):.1f},{p.Y(0):.1f}"
     f" A{rr:.1f},{rr:.1f} 0 1,0 {p.X(R0):.1f},{p.Y(0):.1f} Z ")
d += " ".join(("M" if i == 0 else "L") + p.P(x, y) for i, (x, y) in enumerate(Cpts)) + " Z"
p.add(f'<path d="{d}" fill="{THEORY}" fill-opacity="0.10" fill-rule="evenodd" stroke="none"/>')
p.origin_axes(opacity=0.4)
p.circle(0, 0, R1, REMARK, 1.3, "5 4")
p.circle(0, 0, R0, THEORY, 2.0)
circ_arrow(p, 0, 0, R0, PI / 2, THEORY, 2.0, ccw=False)
circ_arrow(p, 0, 0, R0, -PI / 2, THEORY, 2.0, ccw=False)
closed_curve(p, Cpts, THEORY, 1.8, arrow_at=0)
for z in ((-0.5, 0.45), (0.55, -0.25), (0.8, 0.45)):
    cross(p, z, PRACTICE, 3.6)
p.label(*Cpts[40], "C", -6, -6, THEORY, 13, "end", True, True)
p.label(-R1, 0, "R" + SUB1, 5, 15, REMARK, 11.5, "start", True, True)
p.label(-R0, 0, "R" + SUB0, 5, 15, THEORY, 11.5, "start", True, True)
p.text_px(44, 24 + 12, "R" + SUB1 + " &lt; |z| &lt; &#8734;:", THEORY, 11.5, "start", True)
p.text_px(44, 24 + 27, "f analitik", THEORY, 11.5, "start", False, True)
p.text_px(40 + 320 - 4, 24 + p.h - 4, "C" + SUB0 + ": |z| = R" + SUB0, THEORY, 11.5, "end", True)
p.text_px(44, 24 + p.h - 18, "negatif y&#246;nl&#252;:", THEORY, 11, "start", False, True)
p.text_px(44, 24 + p.h - 4, "&#8734; solda kal&#305;r", THEORY, 11, "start", False, True)
OUT["rezidu-sonsuz-cevreler"] = figure(
    400, int(p.h) + 48, [p],
    "<em>C</em> &#231;evresi |<em>z</em>| = <em>R</em><sub>1</sub> &#231;emberinin i&#231;inde kal&#305;r; "
    "|<em>z</em>| &gt; <em>R</em><sub>1</sub> b&#246;lgesinde <em>f</em> analitiktir ve &#8734; ayr&#305;k bir tekil noktad&#305;r. "
    "<em>C</em><sub>0</sub> saat y&#246;n&#252;nde dola&#351;&#305;l&#305;r ki sonsuzdaki nokta solda kals&#305;n; "
    "g&#246;lgeli b&#246;lgede (<em>C</em> ile <em>C</em><sub>0</sub> aras&#305;nda) <em>f</em> analitik oldu&#287;undan &#8747;<sub><em>C</em></sub> = &#8722;&#8747;<sub><em>C</em><sub>0</sub></sub>.",
    aria="C cevresi, kesikli |z|=R1 cemberi ve saat yonunde dolasilan |z|=R0 cemberi")

# ---- R6: exercise b) — the cube roots of -1 and the essential point 0 inside |z| = 3
p = cplane(40, 24, 320, (-3.4, 3.4), (-3.4, 3.4))
p.origin_axes()
p.circle(0, 0, 1, REMARK, 1.1, "4 3", opacity=0.6)
p.circle(0, 0, 3, THEORY, 2.0)
circ_arrow(p, 0, 0, 3, PI / 2, THEORY, 2.0)
roots = [polar(1, PI / 3), (-1, 0), polar(1, -PI / 3)]
for z in roots:
    cross(p, z, PRACTICE)
cross(p, (0, 0), PRACTICE)
p.label(*roots[0], "e" + sup("i&#960;/3"), 8, -2, PRACTICE, 12, "start", True)
p.label(*roots[1], MINUS + "1", -8, -4, PRACTICE, 12, "end", True)
p.label(*roots[2], "e" + sup(MINUS + "i&#960;/3"), 8, 12, PRACTICE, 12, "start", True)
p.label(0, 0, "0 (esasl&#305;)", 9, 13, PRACTICE, 11.5, "start", True)
p.label(*polar(1, 3 * PI / 4), "|z| = 1", -6, -4, REMARK, 10.5, "end", False, True)
p.label(*polar(3, PI / 4), "C: |z| = 3", 5, -4, THEORY, 12, "start", True)
p.text_px(44, 24 + p.h - 18, "d&#246;rt tekil nokta da", TEXT, 11, "start", False, True)
p.text_px(44, 24 + p.h - 4, "C'nin i&#231;inde", TEXT, 11, "start", False, True)
OUT["rezidu-kupkokler-cember"] = figure(
    400, int(p.h) + 48, [p],
    "<em>z</em>&#179;<em>e</em><sup>1/<em>z</em></sup>/(1 + <em>z</em>&#179;) integrand&#305;n&#305;n d&#246;rt tekil noktas&#305;: "
    "1 + <em>z</em>&#179; = 0 denkleminin birim &#231;ember &#252;zerindeki &#252;&#231; k&#246;k&#252; ve orijindeki esasl&#305; tekillik. "
    "Hepsi |<em>z</em>| = 3 &#231;emberinin i&#231;inde oldu&#287;undan d&#246;rt rezid&#252; yerine tek bir rezid&#252; "
    "&#8212; sonsuzdaki rezid&#252; &#8212; yeter.",
    aria="Birim cember uzerindeki uc kok, orijin ve |z|=3 cevresi")

# ============================================================= tekil-nokta-türleri
# ---- R7: the branch 0 < theta < 2 pi of log z is analytic at z = i
p = cplane(40, 24, 320, (-1.6, 2.2), (-1.55, 1.55))
p.origin_axes()
cut(p, (0, 0), (2.18, 0))
disk_fill(p, 0, 1, 0.5, THEORY, 0.10)
p.circle(0, 1, 0.5, THEORY, 1.4, "5 4")
angle_arc(p, 0.0, PI / 2 - 0.04, 0.42, REMARK, 1.7)
cross(p, (0, 1), PRACTICE)
cross(p, (0, -1), PRACTICE)
p.label(0, 1, "i", -9, 4, PRACTICE, 13, "end", True, True)
p.label(0, -1, MINUS + "i", -9, 4, PRACTICE, 13, "end", True, True)
p.label(0.5, 1.0, "&#966; burada analitik", 17, 4, THEORY, 11, "start", False, True)
p.label(0.42, 0.42, THETA + " = " + PI_S + "/2", 7, -3, REMARK, 11.5, "start", True)
p.label(0.42, 0.42, "log i = i" + PI_S + "/2", 7, 12, REMARK, 10.5, "start", False, True)
p.label(1.2, 0, "dal kesimi", 0, 16, PRACTICE, 11.5, "middle", True)
p.label(1.2, 0, "(" + THETA + " = 0 ve " + THETA + " = 2" + PI_S + ")", 0, 30, PRACTICE, 10.5, "middle", False, True)
OUT["rezidu-log-dal-kutup"] = figure(
    400, int(p.h) + 48, [p],
    "Se&#231;ilen dal&#305;n kesimi pozitif reel eksendedir; <em>z</em> = <em>i</em> ondan uzak oldu&#287;u i&#231;in "
    "<em>&#966;</em>(<em>z</em>) = (log <em>z</em>)&#179;/(<em>z</em> + <em>i</em>) orada analitiktir ve kutup basittir. "
    "Bu dalda <em>i</em>'nin a&#231;&#305;s&#305; kesimden saat y&#246;n&#252;n&#252;n tersine &#246;l&#231;&#252;len &#960;/2'dir, "
    "yani log <em>i</em> = <em>i</em>&#960;/2.",
    aria="Pozitif reel eksendeki dal kesimi, i ve -i noktalari, theta = pi/2 acisi")

# ============================================================ sıfırlar-ve-kutuplar
# ---- R8: vanishing on a segment L forces f = 0 on the whole neighbourhood N_0
p = cplane(40, 24, 320, (-2.5, 2.5), (-2.4, 2.4))
p.origin_axes(opacity=0.3)
disk_fill(p, 0, 0, 0.7, REMARK, 0.14)
p.circle(0, 0, 2, THEORY, 1.5, "5 4")
p.circle(0, 0, 0.7, REMARK, 1.3, "4 3")
L0, L1 = (-1.3, -0.6), (1.3, 0.6)
p.line([L0, L1], PRACTICE, 2.4)
dot(p, (0, 0), TEXT, 3.8)
p.arrow(polar(0.8, 3 * PI / 4), polar(1.9, 3 * PI / 4), REMARK, 1.5, head=7.0)
p.label(0, 0, "z" + SUB0, 6, 15, TEXT, 12.5, "start", True, True)
p.label(*L1, "L: f = 0", -4, -9, PRACTICE, 12, "end", True, True)
p.label(0.5, -0.5, "N: f &#8801; 0", 8, 12, REMARK, 11.5, "start", True, True)
p.label(*polar(2, PI / 4), "N" + SUB0 + ": f analitik", 6, -4, THEORY, 12, "start", True, True)
p.text_px(44, 24 + 12, "Taylor katsay&#305;lar&#305; s&#305;f&#305;r", REMARK, 11, "start", False, True)
p.text_px(44, 24 + 27, "&#8658; t&#252;m N" + SUB0 + "'da f &#8801; 0", REMARK, 11, "start", False, True)
OUT["rezidu-dogru-parcasi"] = figure(
    400, int(p.h) + 48, [p],
    "&#304;ki ad&#305;ml&#305; yay&#305;lma: <em>f</em>, <em>z</em><sub>0</sub>'dan ge&#231;en <em>L</em> par&#231;as&#305;nda s&#305;f&#305;rsa "
    "s&#305;f&#305;rlar&#305;n ayr&#305;kl&#305;&#287;&#305; gere&#287;i k&#252;&#231;&#252;k <em>N</em> diskinin tamam&#305;nda s&#305;f&#305;rd&#305;r; "
    "o zaman <em>z</em><sub>0</sub>'daki b&#252;t&#252;n t&#252;revler, dolay&#305;s&#305;yla t&#252;m Taylor katsay&#305;lar&#305; s&#305;f&#305;rd&#305;r "
    "ve seri <em>f</em>'yi b&#252;y&#252;k <em>N</em><sub>0</sub> diskinin tamam&#305;nda temsil etti&#287;inden orada da <em>f</em> &#8801; 0 olur.",
    aria="z0 dan gecen L dogru parcasi, kucuk N diski ve buyuk N0 diski")

# ---- R9: exercise d) — the branch 0 < theta < 2 pi of z^{1/4} at z = -1
p = cplane(40, 24, 320, (-1.7, 2.0), (-1.3, 1.3))
p.origin_axes()
cut(p, (0, 0), (1.98, 0))
disk_fill(p, -1, 0, 0.4, THEORY, 0.10)
p.circle(-1, 0, 0.4, THEORY, 1.4, "5 4")
angle_arc(p, 0.0, PI - 0.05, 0.42, REMARK, 1.7)
angle_arc(p, 0.0, PI / 4 - 0.08, 0.26, THEORY, 1.5)
w = polar(1, PI / 4)
p.arrow((0, 0), w, THEORY, 2.0)
dot(p, w, PRACTICE, 3.8)
cross(p, (-1, 0), PRACTICE)
p.label(-1, 0, "z = " + MINUS + "1", 0, 50, PRACTICE, 12, "middle", True)
p.text_px(44, 24 + 12, "z" + sup("1/4") + " burada analitik", THEORY, 11, "start", False, True)
p.line([(-1.35, 1.08), (-1.12, 0.45)], THEORY, 1.0)
p.label(-0.1, 0.5, THETA + " = " + PI_S, 0, -6, REMARK, 11.5, "middle", True)
p.label(0.56, 0.12, THETA + "/4 = " + PI_S + "/4", 4, 2, THEORY, 10.5, "start", True)
p.label(*w, "&#966;(" + MINUS + "1) = e" + sup("i&#960;/4"), 9, 0, PRACTICE, 12, "start", True)
p.label(1.1, 0, "dal kesimi", 0, 16, PRACTICE, 11.5, "middle", True)
p.label(1.1, 0, "(" + THETA + " = 0 ve 2" + PI_S + ")", 0, 30, PRACTICE, 10.5, "middle", False, True)
OUT["rezidu-dorduncu-kok-dal"] = figure(
    400, int(p.h) + 48, [p],
    "Kesim pozitif reel eksende oldu&#287;undan <em>z</em> = &#8722;1'in a&#231;&#305;s&#305; bu dalda &#952; = &#960;'dir "
    "(kesimden saat y&#246;n&#252;n&#252;n tersine yar&#305;m tur); &#8722;&#960; se&#231;ilemez. Dal <em>z</em> = &#8722;1 civar&#305;nda analitiktir, "
    "rezid&#252; <em>&#966;</em>(&#8722;1) = <em>e</em><sup><em>i</em>&#960;/4</sup> = (1 + <em>i</em>)/&#8730;2 de&#287;eridir "
    "(&#351;ekilde ayn&#305; d&#252;zlemde g&#246;sterilmi&#351;tir).",
    aria="Pozitif reel eksendeki kesim, z=-1 icin theta=pi acisi ve e^{i pi/4} noktasi")

# ---- R10: the four roots of z^4 + 4 = 0 on |z| = sqrt 2
p = cplane(40, 24, 320, (-1.9, 1.9), (-1.75, 1.75))
p.origin_axes()
p.circle(0, 0, math.sqrt(2), REMARK, 1.2, "4 3", opacity=0.6)
p.line([(0, 0), (1, 1)], THEORY, 1.6)
angle_arc(p, 0.0, PI / 4 - 0.1, 0.45, THEORY, 1.6)
for z in ((-1, 1), (-1, -1), (1, -1)):
    cross(p, z, PRACTICE, 3.8)
cross(p, (1, 1), PRACTICE, 4.6, 2.0)
p.label(1, 1, "z" + SUB0 + " = 1 + i", 8, -3, PRACTICE, 12, "start", True)
p.label(1, 1, "= &#8730;2&#183;e" + sup("i&#960;/4"), 8, 13, PRACTICE, 11.5, "start", True)
p.label(-1, 1, MINUS + "1 + i", -8, -3, PRACTICE, 12, "end", True)
p.label(-1, -1, MINUS + "1 " + MINUS + " i", -8, 14, PRACTICE, 12, "end", True)
p.label(1, -1, "1 " + MINUS + " i", 8, 14, PRACTICE, 12, "start", True)
p.label(0.5, 0.15, PI_S + "/4", 6, 4, THEORY, 11.5, "start", True)
p.label(*polar(math.sqrt(2), 5 * PI / 4 + 0.35), "|z| = &#8730;2", -4, 14, REMARK, 10.5, "end", False, True)
OUT["rezidu-z4-kokler"] = figure(
    400, int(p.h) + 48, [p],
    "<em>z</em>&#8308; + 4 = 0 denkleminin d&#246;rt k&#246;k&#252; |<em>z</em>| = &#8730;2 &#231;emberi &#252;zerinde 90&#176; aral&#305;klarla dizilir; "
    "hepsi <em>z</em>/(<em>z</em>&#8308; + 4) i&#231;in basit kutuptur. <em>z</em><sub>0</sub> = 1 + <em>i</em> "
    "bunlardan a&#231;&#305;s&#305; &#960;/4 olan&#305;d&#305;r; di&#287;erleri <em>i</em> ile &#231;arp&#305;larak (90&#176; d&#246;nd&#252;r&#252;lerek) elde edilir.",
    aria="z^4+4=0 denkleminin dort koku kok 2 yaricapli cember uzerinde")

# ======================================================= tekil-noktalarda-davranış
# ---- R11: Casorati-Weierstrass — punctured delta-disk in the z-plane, epsilon-disk in the w-plane
p1 = cplane(24, 30, 250, (-1.5, 1.5), (-1.5, 1.5))
disk_fill(p1, 0, 0, 1, THEORY, 0.10)
p1.origin_axes()
p1.circle(0, 0, 1, THEORY, 1.5, "5 4")
p1.line([(0, 0), polar(1, 5 * PI / 6)], REMARK, 1.1)
p1.label(*polar(0.5, 5 * PI / 6), "&#948;", -2, -6, REMARK, 12, "middle", True, True)
hollow(p1, (0, 0), TEXT, 3.6)
p1.label(0, 0, "z" + SUB0, 7, 15, TEXT, 12.5, "start", True, True)
zpt = (0.45, 0.3)
dot(p1, zpt, PRACTICE, 4.0)
p1.label(*zpt, "z", 8, -2, PRACTICE, 13, "start", True, True)
p1.label(0, -1, "0 &lt; |z " + MINUS + " z" + SUB0 + "| &lt; &#948;", 0, 17, THEORY, 11.5, "middle", True)
panel_title(p1, "z-d&#252;zlemi")

p2 = cplane(300, 30, 250, (-1.5, 1.5), (-1.5, 1.5))
disk_fill(p2, 0, 0, 0.8, PRACTICE, 0.10)
p2.origin_axes()
p2.circle(0, 0, 0.8, PRACTICE, 1.5, "5 4")
p2.line([(0, 0), polar(0.8, 5 * PI / 6)], REMARK, 1.1)
p2.label(*polar(0.4, 5 * PI / 6), "&#949;", -2, -6, REMARK, 12, "middle", True, True)
dot(p2, (0, 0), TEXT, 3.8)
p2.label(0, 0, "w" + SUB0, 7, 15, TEXT, 12.5, "start", True, True)
wpt = (0.3, 0.22)
dot(p2, wpt, PRACTICE, 4.0)
p2.label(*wpt, "f(z)", 8, -3, PRACTICE, 13, "start", True, True)
p2.label(0, -0.8, "|w " + MINUS + " w" + SUB0 + "| &lt; &#949;", 0, 17, PRACTICE, 11.5, "middle", True)
panel_title(p2, "w-d&#252;zlemi")
p2.text_px(287, 30 + 125 + 5, "&#8594;", TEXT, 20, "middle", True)
p2.text_px(287, 30 + 125 - 12, "f", TEXT, 12.5, "middle", True, True)
OUT["rezidu-casorati-weierstrass"] = figure(
    574, int(p1.h) + 30 + 44, [p1, p2],
    "Casorati-Weierstrass: <em>w</em><sub>0</sub> ve &#949; ne olursa olsun, <em>z</em><sub>0</sub>'&#305;n "
    "<strong>her</strong> delinmi&#351; &#948;-kom&#351;ulu&#287;unda g&#246;r&#252;nt&#252;s&#252; <em>w</em><sub>0</sub>'&#305;n &#949;-diskine d&#252;&#351;en "
    "bir <em>z</em> vard&#305;r. &#948; k&#252;&#231;&#252;ld&#252;k&#231;e sol disk daral&#305;r ama sa&#287;daki hedefe d&#252;&#351;en bir nokta hep bulunur; "
    "esasl&#305; tekillik civar&#305;nda de&#287;erler d&#252;zlemin her yerinde yo&#287;undur.",
    css_class=WIDE, aria="Solda z0 etrafinda delinmis delta diski, sagda w0 etrafinda epsilon diski")

# ---- R12: solutions of e^{1/z} = w_0 pile up at the origin (w_0 = e^{1+i}: ln rho = 1, alpha = 1)
p = cplane(40, 24, 320, (-0.45, 1.2), (-0.62, 0.58))
DELTA = 0.36
disk_fill(p, 0, 0, DELTA, THEORY, 0.12)
p.origin_axes()
p.circle(0.5, 0, 0.5, REMARK, 1.2, "4 3")
p.circle(0, 0, DELTA, THEORY, 1.4, "5 4")
p.line([(0, 0), polar(DELTA, -2.5)], THEORY, 1.1)
p.label(*polar(DELTA / 2, -2.5), "&#948;", -3, -5, THEORY, 12, "end", True, True)
zn = []
for n in range(6):
    t = 1 + 2 * n * PI
    zn.append((1 / (1 + t * t), -t / (1 + t * t)))
for k, z in enumerate(zn):
    p.points([z], PRACTICE, max(1.6, 4.0 - 0.55 * k))
hollow(p, (0, 0), TEXT, 3.4)
p.label(0, 0, "0 (esasl&#305;)", -8, -8, TEXT, 11.5, "end", True)
p.label(*zn[0], "z" + SUB0, 9, 4, PRACTICE, 12.5, "start", True, True)
p.label(*zn[1], "z" + SUB1, 9, 5, PRACTICE, 12.5, "start", True, True)
p.label(*zn[2], "z" + SUB2 + ", &#8230;", 9, 1, PRACTICE, 11.5, "start", True, True)
p.label(0.5, 0.5, "|z " + MINUS + " 1/2| = 1/2 &#231;emberi", 0, -8, REMARK, 11, "middle", False, True)
# bottom-right corner, below the circle so the dashed curve does not run through the label
p.label(1.18, -0.5, "e" + sup("1/z<tspan font-size=\"7\" dy=\"2\">n</tspan><tspan dy=\"-2\">&#8203;</tspan>") + " = w" + SUB0, 0, 2, TEXT, 12, "end", True)
p.label(1.18, -0.5, "her n i&#231;in", 0, 17, TEXT, 10.5, "end", False, True)
OUT["rezidu-e1z-cozumler"] = figure(
    400, int(p.h) + 48, [p],
    "<em>w</em><sub>0</sub> = <em>e</em><sup>1+<em>i</em></sup> i&#231;in <em>z<sub>n</sub></em> = 1/(1 + <em>i</em>(1 + 2<em>n</em>&#960;)) "
    "noktalar&#305; |<em>z</em> &#8722; 1/2| = 1/2 &#231;emberi &#252;zerinde orijine do&#287;ru ko&#351;ar; her birinde "
    "<em>e</em><sup>1/<em>z</em></sup> tam olarak <em>w</em><sub>0</sub> de&#287;erini al&#305;r. &#948;-diski ne kadar k&#252;&#231;&#252;k "
    "olursa olsun sonsuz &#231;o&#287;u i&#231;eride kal&#305;r: de&#287;er her delinmi&#351; kom&#351;ulukta sonsuz kez al&#305;n&#305;r.",
    aria="e^(1/z)=w0 denkleminin cozumleri bir cember uzerinde orijine yigilir")

# ---- R13: cos(1/z) — two approach directions with different behaviour
p = cplane(24, 24, 240, (-1.2, 1.2), (-1.2, 1.2))
p.origin_axes()
for x0 in (1.0, -1.0):
    p.arrow((x0, 0), (0.14 * x0, 0), PRACTICE, 2.2)
for y0 in (1.0, -1.0):
    p.arrow((0, y0), (0, 0.14 * y0), THEORY, 2.2)
hollow(p, (0, 0), TEXT, 3.6)
p.label(0, 0, "0", 8, -7, TEXT, 12, "start", True)
p.label(0.55, 0, "x &#8594; 0", 0, -8, PRACTICE, 11.5, "middle", True, True)
p.label(-0.55, 0, "x &#8594; 0", 0, -8, PRACTICE, 11.5, "middle", True, True)
p.label(0, 0.6, "iy &#8594; 0", 8, 4, THEORY, 11.5, "start", True, True)
p.label(0, -0.6, "iy &#8594; 0", 8, 4, THEORY, 11.5, "start", True, True)
lx, ly = 288, 24 + 40
p.text_px(lx, ly, "reel eksen boyunca:", PRACTICE, 11.5, "start", True)
p.text_px(lx, ly + 17, "cos(1/x), " + MINUS + "1 ile 1 aras&#305;nda", PRACTICE, 11, "start", False, True)
p.text_px(lx, ly + 32, "durmadan sal&#305;n&#305;r; limit yok", PRACTICE, 11, "start", False, True)
p.text_px(lx, ly + 66, "sanal eksen boyunca:", THEORY, 11.5, "start", True)
p.text_px(lx, ly + 83, "|cos(1/iy)| = cosh(1/y) &#8594; &#8734;", THEORY, 11, "start", False, True)
p.text_px(lx, ly + 118, "y&#246;nler uyu&#351;muyor:", TEXT, 11.5, "start", True)
p.text_px(lx, ly + 134, "ne sonlu limit ne &#8734;", TEXT, 11.5, "start", True)
p.text_px(lx, ly + 150, "&#8658; esasl&#305; tekillik", TEXT, 11.5, "start", True)
OUT["rezidu-cos1z-yonler"] = figure(
    500, int(p.h) + 48, [p],
    "cos(1/<em>z</em>) i&#231;in orijine iki farkl&#305; y&#246;nden yakla&#351;ma: reel eksen boyunca de&#287;erler "
    "&#8722;1 ile 1 aras&#305;nda sal&#305;n&#305;r, sanal eksen boyunca mod&#252;l sonsuza gider. Tek bir limit "
    "(sonlu ya da &#8734;) olmad&#305;&#287;&#305;ndan tekillik ne kald&#305;r&#305;labilir ne kutuptur: esasl&#305;d&#305;r.",
    css_class=WIDE, aria="Orijine reel ve sanal eksen boyunca yaklasan oklar ve davranis ozeti")

# ############################################################################
# PART: Rezidü Uygulamaları
# ############################################################################

# ############################################################################
# PART: Uygulamalar (rezidü kuramının uygulamaları)
# ############################################################################

def _uyg_sub(s):
    """Subscript inside an SVG <text>: 'C' + _uyg_sub('R') + ' (R > 1)'.
    Like svg_plot.sup(): the baseline is restored by a zero-width space, so a plain-space
    tspan does not swallow the caller's following space."""
    return f'<tspan font-size="9" dy="4">{s}</tspan><tspan dy="-4">&#8203;</tspan>'


def _sup2(s, rest, size=9):
    """Superscript followed by text in the same <text>: 'z' + _sup2('6', ' = 1').
    svg_plot.sup() ends with a zero-width-space tspan, so the leading space of `rest` survives."""
    return sup(s, size) + rest


def _uyg_arc_arrow(p, cx, cy, r, a, color, width=1.9, ccw=True, d=0.035):
    """Arrowhead placed ON the circle |z - c| = r at angle a, along the ccw (or cw) tangent."""
    s = 1 if ccw else -1
    p0 = (cx + r * math.cos(a - s * d), cy + r * math.sin(a - s * d))
    p1 = (cx + r * math.cos(a + s * d), cy + r * math.sin(a + s * d))
    p.arrow(p0, p1, color, width, head=8.0)


def _uyg_seg_arrow(p, a, b, color, width=1.9, t=0.5):
    """Arrowhead placed ON the segment a -> b at fraction t of its length."""
    m = (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
    p0 = (m[0] - (b[0] - a[0]) * 0.02, m[1] - (b[1] - a[1]) * 0.02)
    p.arrow(p0, m, color, width, head=8.0)


# ============================================ has-olmayan-integraller
# ---- H1: the semicircular contour; only upper-half-plane zeros of q are enclosed
p = cplane(40, 24, 320, (-1.55, 1.55), (-0.78, 1.32))
p.sector(0, 0, 1.0, 0, PI, THEORY, 0.10)
p.origin_axes()
p.line([(-1, 0), (1, 0)], PRACTICE, 2.0)
_uyg_seg_arrow(p, (-1, 0), (1, 0), PRACTICE, 2.0, 0.3)
p.arc(0, 0, 1.0, 0, PI, PRACTICE, 2.0)
_uyg_arc_arrow(p, 0, 0, 1.0, PI / 2, PRACTICE, 2.0)
p.label(-1, 0, MINUS + "R", 0, 15, TEXT, 11, "middle")
p.label(1, 0, "R", 0, 15, TEXT, 11, "middle")
p.label(*polar(1, 0.75), "C" + _uyg_sub("R"), 8, -2, PRACTICE, 12.5, "start", True, True)
for z, name, dx, dy, an in (((0.5, 0.55), "z" + SUB1, 8, 4, "start"),
                            ((-0.55, 0.35), "z" + SUB2, -8, 4, "end"),
                            ((-0.1, 0.8), "z" + SUB3, -8, 1, "end")):
    cross(p, z, THEORY, 4.2)
    p.label(*z, name, dx, dy, THEORY, 12, an, True, True)
zb = (0.5, -0.55)
cross(p, zb, REMARK, 3.6, 1.4)
p.label(*zb, "z&#773;" + SUB1 + " (dışarıda)", 8, 4, REMARK, 11, "start", False, True)
OUT["uygulamalar-yarim-cember"] = figure(
    400, 288, [p],
    "Yarım çember yöntemi: yol, [&#8722;<em>R</em>, <em>R</em>] doğru parçası ile üst yarım çember "
    "<em>C<sub>R</sub></em>'den oluşur ve pozitif yönde dolaşılır. Yalnızca üst yarı düzlemdeki sıfırlar "
    "<em>z</em><sub>1</sub>, <em>z</em><sub>2</sub>, <em>z</em><sub>3</sub> yolun içindedir; <em>q</em> reel katsayılı "
    "olduğundan her kutbun eşleniği de kutuptur, ama alt yarı düzlemde kalır ve rezidü toplamına girmez.",
    aria="Yarim cember cevresi ve ust yari duzlemdeki kutuplar")

# ---- H2: the six roots of z^6 = -1; three of them are enclosed by the semicircle
p = cplane(40, 42, 320, (-1.85, 1.85), (-1.42, 1.72))
p.sector(0, 0, 1.4, 0, PI, THEORY, 0.08)
p.origin_axes()
p.circle(0, 0, 1, REMARK, 1.0, "4 3", opacity=0.55)
p.line([(-1.4, 0), (1.4, 0)], PRACTICE, 2.0)
_uyg_seg_arrow(p, (-1.4, 0), (1.4, 0), PRACTICE, 2.0, 0.36)
p.arc(0, 0, 1.4, 0, PI, PRACTICE, 2.0)
_uyg_arc_arrow(p, 0, 0, 1.4, PI / 2, PRACTICE, 2.0)
p.label(*polar(1.4, 0.75), "C" + _uyg_sub("R") + " (R &gt; 1)", 8, -2, PRACTICE, 12, "start", True, True)
angle_arc(p, 0, PI / 6, 0.45, PRACTICE, 1.6)
p.label(0.5, 0.1, "&#960;/6", 0, 0, PRACTICE, 11, "start", True)
angle_arc(p, PI / 6, PI / 2, 0.62, BASE, 1.5)
p.label(0.43, 0.6, "2&#960;/6", 0, 0, BASE, 11, "start", True)
root_labels = [("c" + SUB0, 9, 12, "start"), ("c" + SUB1 + " = i", 9, -4, "start"), ("c" + SUB2, -9, 12, "end"),
               ("c" + SUB3, -9, 4, "end"), ("c&#8324;", 9, 14, "start"), ("c&#8325;", 9, 4, "start")]
for k, (lab, dx, dy, an) in enumerate(root_labels):
    z = polar(1, PI / 6 + k * PI / 3)
    if k < 3:
        dot(p, z, THEORY, 4.0)
        p.label(*z, lab, dx, dy, THEORY, 12, an, True, True)
    else:
        hollow(p, z, REMARK, 3.8)
        p.label(*z, lab, dx, dy, REMARK, 12, an, False, True)
p.label(-1.4, 0, MINUS + "R", 0, 15, TEXT, 11, "middle")
p.label(1.4, 0, "R", 0, 15, TEXT, 11, "middle")
p.text_px(200, 24, "z" + _sup2("6", " = " + MINUS + "1 kökleri: c") + _uyg_sub("k") + " = e"
          + sup("i(&#960;/6 + 2k&#960;/6)"), TEXT, 11.5, "middle", True)
OUT["uygulamalar-z6-kokleri"] = figure(
    400, 358, [p],
    "<em>z</em><sup>6</sup> = &#8722;1'in altı kökü birim çember üzerinde &#960;/3 aralıklarla dizilir; "
    "<em>c</em><sub>0</sub>, <em>c</em><sub>1</sub>, <em>c</em><sub>2</sub> üst yarı düzlemde, "
    "<em>c</em><sub>3</sub>, <em>c</em><sub>4</sub>, <em>c</em><sub>5</sub> alt yarı düzlemdedir. "
    "<em>R</em> &gt; 1 alınır alınmaz yarım çember yolu tam olarak üstteki üç kutbu içine alır; "
    "hiçbir kök reel eksende olmadığından yol tekil noktaya değmez.",
    aria="z^6 = -1 kokleri ve ust yarim cember")

# ---- H3: P.V. exists but the integral diverges: two cancelling areas under y = x
p = cplane(40, 24, 320, (-1.55, 1.55), (-1.3, 1.3))
p.polygon([(-1, 0), (0, 0), (-1, -1)], PRACTICE, 0.18)
p.polygon([(0, 0), (1, 0), (1, 1)], THEORY, 0.18)
p.origin_axes(xlabel="x", ylabel="y")
p.line([(-1.25, -1.25), (1.25, 1.25)], THEORY, 1.9)
p.vline(-1, -1.15, 1.15, REMARK, "4 3", 0.6)
p.vline(1, -1.15, 1.15, REMARK, "4 3", 0.6)
p.label(1.25, 1.25, "y = x", 8, 0, THEORY, 12, "start", True, True)
p.label(-1, 0, MINUS + "R", -6, -8, TEXT, 11, "end")
p.label(1, 0, "R", 6, 16, TEXT, 11, "start")
p.label(-0.72, -0.4, MINUS + "R&#178;/2", 0, 0, PRACTICE, 12.5, "middle", True)
p.label(0.72, 0.3, "+R&#178;/2", 0, 0, THEORY, 12.5, "middle", True)
OUT["uygulamalar-simetrik-kesme"] = figure(
    400, 338, [p],
    "<em>f</em>(<em>x</em>) = <em>x</em> için simetrik kesme [&#8722;<em>R</em>, <em>R</em>] iki eşit ve zıt "
    "işaretli alan verir: toplam her <em>R</em> için sıfırdır, dolayısıyla esas değer 0'dır. Oysa "
    "(2) tanımı iki ucu bağımsız kesmeye izin verir; tek taraflı limitlerin ikisi de yoktur (örneğin "
    "<em>R</em><sub>1</sub> = 2<em>R</em><sub>2</sub> alınırsa fark sınırsız büyür), dolayısıyla integral ıraksar.",
    aria="y = x altinda birbirini goturen iki ucgen alan")

# ============================================ fourier-integralleri-ve-jordan-lemmasi
# ---- J1: Jordan's inequality  sin θ ≥ 2θ/π on [0, π/2]
_tick = lambda t: "&#960;/2" if abs(t - PI / 2) < 1e-6 else "&#960;"
p = Plot(44, 34, 316, 156, (0, 3.36), (0, 1.2))
sin_pts = [(k * PI / 120, math.sin(k * PI / 120)) for k in range(121)]
p.polygon([(0, 0)] + sin_pts[:61] + [(PI / 2, 1)], THEORY, 0.16)
p.polygon([(PI / 2, 1)] + sin_pts[60:] + [(PI, 0)], THEORY, 0.07)
p.axes((PI / 2, PI), (1,), "&#952;", "y", xfmt=_tick)
p.vline(PI / 2, 0, 1, REMARK, "4 3", 0.6)
p.line(sin_pts, THEORY, 2.0)
p.line([(0, 0), (PI / 2, 1)], PRACTICE, 1.9)
p.line([(PI / 2, 1), (PI, 0)], PRACTICE, 1.4, "5 4", 0.8)
p.label(2.0, 0.99, "y = sin &#952;", 0, 0, THEORY, 12, "start", True, True)
p.label(0.85, 0.32, "y = 2&#952;/&#960;", 0, 0, PRACTICE, 12, "start", True, True)
panel_title(p, "Jordan eşitsizliği: sin &#952; &#8805; 2&#952;/&#960;  (0 &#8804; &#952; &#8804; &#960;/2)")
OUT["uygulamalar-jordan-esitsizlik"] = figure(
    400, 232, [p],
    "[0, &#960;/2] aralığında sinüs içbükeydir: grafiği, (0, 0) ile (&#960;/2, 1) noktalarını birleştiren "
    "kirişin üstünde kalır, yani sin <em>&#952;</em> &#8805; 2<em>&#952;</em>/&#960;. Grafik <em>&#952;</em> = &#960;/2 "
    "doğrusuna göre simetrik olduğundan aynı kestirim [&#960;/2, &#960;] aralığında da (kesikli kiriş) geçerlidir; "
    "iki yarı toplanınca &#8747;<sub>0</sub><sup>&#960;</sup> e<sup>&#8722;<em>R</em> sin <em>&#952;</em></sup> d<em>&#952;</em> &lt; &#960;/<em>R</em> çıkar.",
    aria="sin theta ve 2theta/pi kirisi: Jordan esitsizligi")

# ---- J2: e^{-aR sin θ} on the arc is small except near the two ends
p = Plot(44, 34, 316, 156, (0, 3.36), (0, 1.2))
c2 = [(k * PI / 240, math.exp(-2 * math.sin(k * PI / 240))) for k in range(241)]
c10 = [(k * PI / 240, math.exp(-10 * math.sin(k * PI / 240))) for k in range(241)]
p.polygon([(0, 0)] + c10 + [(PI, 0)], PRACTICE, 0.2)
p.axes((PI / 2, PI), (1,), "&#952;", "y", xfmt=_tick)
p.line(c2, THEORY, 1.8, "5 4")
p.line(c10, PRACTICE, 2.0)
p.label(PI / 2, 0.135, "aR = 2", 0, -8, THEORY, 12, "middle", True)
p.label(0.55, 0.07, "aR = 10", 0, 0, PRACTICE, 12, "start", True)
p.label(PI / 2, 0.52, "taralı alan &lt; &#960;/(aR)", 0, 0, PRACTICE, 11, "middle", False, True)
p.label(0.12, 1.1, "yayın iki ucunda (reel eksende) değer 1", 0, 0, TEXT, 10.5, "start", False, True)
panel_title(p, "|exp(iaRe" + sup("i&#952;") + ")| = e" + sup("&#8722;aR sin &#952;") + " çarpanı yay üzerinde")
OUT["uygulamalar-jordan-sonum"] = figure(
    400, 232, [p],
    "<em>C<sub>R</sub></em> üzerinde e<sup>i<em>az</em></sup> çarpanının modülü e<sup>&#8722;<em>aR</em> sin <em>&#952;</em></sup>'dır: "
    "yayın uçlarında 1'e eşittir ama <em>aR</em> büyüdükçe yayın iç kısmında hızla sıfıra çöker. Bu yüzden eğrinin "
    "altındaki alan &#960;/(<em>aR</em>) ile sınırlıdır ve yay integralinde ML kestirimindeki <em>R</em> çarpanı "
    "yok olur — Jordan lemmasının kazancı budur.",
    aria="e^{-aR sin theta} egrileri: aR buyudukce sadece uclar kalir")

# ============================================ girintili-yollar
# ---- G1: the small clockwise semicircle around a simple pole on the real axis
x0, rho, R2 = 1.7, 1.0, 1.5
p = cplane(40, 30, 320, (-0.9, 4.1), (-1.65, 1.95))
p.origin_axes()
p.circle(x0, 0, R2, REMARK, 1.1, "4 3", opacity=0.6)
p.arc(x0, 0, rho, 0, PI, PRACTICE, 2.1)
_uyg_arc_arrow(p, x0, 0, rho, PI / 2, PRACTICE, 2.1, ccw=False)
dot(p, (x0, 0), PRACTICE, 4.0)
p.label(x0, 0, "x" + SUB0, 0, 16, PRACTICE, 12, "middle", True, True)
p.label(x0 - rho, 0, "x" + SUB0 + " " + MINUS + " &#961;", 0, 16, TEXT, 11, "middle")
p.label(x0 + rho, 0, "x" + SUB0 + " + &#961;", 0, 16, TEXT, 11, "middle")
p.label(x0 + 0.12, rho, "C" + _uyg_sub("&#961;"), 10, -6, PRACTICE, 12.5, "start", True, True)
p.label(x0, 0.58, "saat yönünde", 0, 0, PRACTICE, 10.5, "middle", False, True)
p.label(x0, 0.28, "yarım tur: " + MINUS + "&#960;iB" + SUB0, 0, 0, TEXT, 11, "middle", False, True)
p.label(x0 - 0.9, R2 + 0.1, "0 &lt; |z " + MINUS + " x" + SUB0 + "| &lt; R" + SUB2, 0, 0, REMARK, 10.5, "start", False, True)
OUT["uygulamalar-kucuk-yay"] = figure(
    400, 284, [p],
    "Reel eksendeki basit kutup <em>x</em><sub>0</sub>, yarıçapı <em>&#961;</em> olan üst yarım çember "
    "<em>C<sub>&#961;</sub></em> ile <strong>saat yönünde</strong> dolaşılır (kesikli çember, Laurent temsilinin "
    "geçerli olduğu delinmiş disk). Tam tur 2&#960;<em>iB</em><sub>0</sub> verirken yarım tur bunun yarısını "
    "verir; yön saat yönünde olduğundan işaret eksidir: <em>&#961;</em> &#8594; 0 iken integral &#8722;&#960;<em>iB</em><sub>0</sub>'a gider.",
    aria="Basit kutup cevresinde saat yonunde kucuk yarim cember")

# ---- G2: the indented contour for the Dirichlet integral
rho, R = 0.35, 1.6
p = cplane(40, 24, 320, (-2.1, 2.1), (-0.6, 1.95))
p.polygon(circle_pts(0, 0, R, 0, PI) + circle_pts(0, 0, rho, PI, 0), THEORY, 0.10)
p.origin_axes()
p.line([(rho, 0), (R, 0)], PRACTICE, 2.1)
_uyg_seg_arrow(p, (rho, 0), (R, 0), PRACTICE, 2.1, 0.55)
p.line([(-R, 0), (-rho, 0)], PRACTICE, 2.1)
_uyg_seg_arrow(p, (-R, 0), (-rho, 0), PRACTICE, 2.1, 0.45)
p.arc(0, 0, R, 0, PI, PRACTICE, 2.1)
_uyg_arc_arrow(p, 0, 0, R, PI / 2, PRACTICE, 2.1)
p.arc(0, 0, rho, 0, PI, PRACTICE, 2.1)
_uyg_arc_arrow(p, 0, 0, rho, PI / 2, PRACTICE, 2.1, ccw=False)
hollow(p, (0, 0), REMARK, 3.4)
p.label(1.0, 0, "L" + SUB1, 0, 17, PRACTICE, 12.5, "middle", True, True)
p.label(-1.0, 0, "L" + SUB2, 0, 17, PRACTICE, 12.5, "middle", True, True)
p.label(*polar(R, 0.7), "C" + _uyg_sub("R"), 8, -2, PRACTICE, 12.5, "start", True, True)
p.label(0.1, rho, "C" + _uyg_sub("&#961;"), 8, -5, PRACTICE, 12.5, "start", True, True)
for x, t in ((-R, MINUS + "R"), (-rho, MINUS + "&#961;"), (rho, "&#961;"), (R, "R")):
    p.label(x, 0, t, 0, 17, TEXT, 10.5, "middle")
p.label(0, 0, "0: girintiyle dışarıda", 10, 32, REMARK, 10.5, "start", False, True)
OUT["uygulamalar-girintili-yol"] = figure(
    400, 270, [p],
    "Girintili yol dört parçadan oluşur ve pozitif yönde dolaşılır: <em>L</em><sub>1</sub> (<em>&#961;</em>'dan "
    "<em>R</em>'ye), büyük yarım çember <em>C<sub>R</sub></em> (saat yönünün tersine), <em>L</em><sub>2</sub> "
    "(&#8722;<em>R</em>'den &#8722;<em>&#961;</em>'ya) ve orijini üstten dolaşan küçük yarım çember "
    "<em>C<sub>&#961;</sub></em> (&#8722;<em>&#961;</em>'dan <em>&#961;</em>'ya, yani <strong>saat yönünde</strong>). "
    "Orijin yolun dışında kaldığından taralı bölgede integrand analitiktir ve Cauchy-Goursat teoremi uygulanır.",
    aria="Dirichlet integrali icin girintili yol: L1, CR, L2, C_rho")

# ---- G3: the same contour with the log branch cut pointing down and the pole 2i inside
rho, R, pole = 0.4, 2.6, (0, 2)
p = cplane(40, 30, 320, (-3.0, 3.0), (-2.35, 2.9))
p.polygon(circle_pts(0, 0, R, 0, PI) + circle_pts(0, 0, rho, PI, 0), THEORY, 0.08)
p.origin_axes()
p.line([(0, 0), (0, -2.25)], REMARK, 3.4, None, 0.4)
p.line([(rho, 0), (R, 0)], PRACTICE, 1.8)
_uyg_seg_arrow(p, (rho, 0), (R, 0), PRACTICE, 1.8, 0.75)
p.line([(-R, 0), (-rho, 0)], PRACTICE, 1.8)
_uyg_seg_arrow(p, (-R, 0), (-rho, 0), PRACTICE, 1.8, 0.25)
p.arc(0, 0, R, 0, PI, PRACTICE, 1.8, samples=96)
_uyg_arc_arrow(p, 0, 0, R, PI / 2, PRACTICE, 1.8)
p.arc(0, 0, rho, 0, PI, PRACTICE, 1.8)
_uyg_arc_arrow(p, 0, 0, rho, PI / 2, PRACTICE, 1.8, ccw=False)
cross(p, pole, THEORY, 4.2)
p.label(*pole, "2i", 9, 4, THEORY, 12.5, "start", True, True)
p.label(1.5, 0, "arg z = 0", 0, -8, TEXT, 11, "middle", False, True)
p.label(-1.5, 0, "arg z = &#960;", 0, -8, TEXT, 11, "middle", False, True)
p.label(1.5, 0, "L" + SUB1, 0, 16, PRACTICE, 12, "middle", True, True)
p.label(-1.5, 0, "L" + SUB2, 0, 16, PRACTICE, 12, "middle", True, True)
p.label(*polar(R, 0.6), "C" + _uyg_sub("R"), 8, -2, PRACTICE, 12.5, "start", True, True)
p.label(0.1, rho, "C" + _uyg_sub("&#961;"), 8, -5, PRACTICE, 12.5, "start", True, True)
p.label(0, -1.35, "dal kesimi", 8, 0, REMARK, 11, "start", False, True)
p.label(0, -1.35, "(arg z = " + MINUS + "&#960;/2)", 8, 14, REMARK, 10.5, "start", False, True)
p.label(-2.95, 2.7, MINUS + "&#960;/2 &lt; arg z &lt; 3&#960;/2", 0, 0, THEORY, 11.5, "start", True)
OUT["uygulamalar-dal-kesimi-asagida"] = figure(
    400, 356, [p],
    "log <em>z</em> için &#8722;&#960;/2 &lt; arg <em>z</em> &lt; 3&#960;/2 dalı seçilince dal kesimi negatif sanal "
    "eksene, yani yolun <em>uzağına</em> düşer; kesim yola yalnızca orijinde yaklaşır, orijin ise girintiyle dışarıda "
    "bırakılmıştır. Bu dalda <em>L</em><sub>1</sub> üzerinde arg <em>z</em> = 0, <em>L</em><sub>2</sub> üzerinde "
    "arg <em>z</em> = &#960; olur — negatif eksendeki ln <em>r</em> + <em>i</em>&#960; terimi buradan gelir. "
    "<em>&#961;</em> &lt; 2 &lt; <em>R</em> koşuluyla tek kutup 2<em>i</em> yolun içindedir.",
    aria="Girintili yol, asagi bakan dal kesimi ve 2i kutbu")

# ============================================ dal-kesimi-boyunca-integrasyon
# ---- D1: the keyhole contour around the branch cut arg z = 0
rho, R, g = 0.3, 1.5, 0.07
a_out, a_in = math.asin(g / R), math.asin(g / rho)
xin, xout = rho * math.cos(a_in), R * math.cos(a_out)
p = cplane(40, 24, 320, (-2.0, 2.0), (-1.95, 1.95))
keyhole = (circle_pts(0, 0, R, a_out, 2 * PI - a_out) + [(xout, -g), (xin, -g)]
           + circle_pts(0, 0, rho, 2 * PI - a_in, a_in) + [(xin, g), (xout, g)])
p.polygon(keyhole, THEORY, 0.09)
p.origin_axes()
p.line([(0, 0), (2.0, 0)], REMARK, 3.4, None, 0.4)
p.arc(0, 0, R, a_out, 2 * PI - a_out, PRACTICE, 2.1, samples=120)
_uyg_arc_arrow(p, 0, 0, R, 3 * PI / 4, PRACTICE, 2.1)
p.arc(0, 0, rho, a_in, 2 * PI - a_in, PRACTICE, 2.1)
_uyg_arc_arrow(p, 0, 0, rho, PI, PRACTICE, 2.1, ccw=False, d=0.12)
p.line([(xin, g), (xout, g)], PRACTICE, 2.1)
_uyg_seg_arrow(p, (xin, g), (xout, g), PRACTICE, 2.1, 0.5)
p.line([(xout, -g), (xin, -g)], PRACTICE, 2.1)
_uyg_seg_arrow(p, (xout, -g), (xin, -g), PRACTICE, 2.1, 0.5)
cross(p, (-1, 0), THEORY, 4.2)
p.label(-1, 0, "z = " + MINUS + "1", 0, -12, THEORY, 12, "middle", True)
p.label(-1, 0, "&#952; = &#960;", 0, 18, THEORY, 10.5, "middle", False, True)
p.label(*polar(R, 2.0), "C" + _uyg_sub("R"), -6, -6, PRACTICE, 12.5, "end", True, True)
p.label(-0.2, -0.28, "C" + _uyg_sub("&#961;"), -4, 12, PRACTICE, 12.5, "end", True, True)
p.label(0.4, g, "üst yaka: &#952; = 0", 0, -11, TEXT, 10.5, "start", False, True)
p.label(0.4, -g, "alt yaka: &#952; = 2&#960;", 0, 15, TEXT, 10.5, "start", False, True)
p.label(1.55, 0, "dal kesimi", 0, -8, REMARK, 11, "start", False, True)
OUT["uygulamalar-kesik-halka"] = figure(
    400, 384, [p],
    "Kesik halka: dal kesimi pozitif reel eksendir. Yol, kesimin üst yakasında <em>&#961;</em>'dan <em>R</em>'ye "
    "gider, <em>C<sub>R</sub></em> üzerinde saat yönünün tersine tam tur atar, alt yakada geri döner ve "
    "<em>C<sub>&#961;</sub></em> üzerinde saat yönünde başlangıca varır. Üst yakada <em>&#952;</em> = 0 ile "
    "<em>z</em><sup>&#8722;<em>a</em></sup> = <em>r</em><sup>&#8722;<em>a</em></sup>, alt yakada <em>&#952;</em> = 2&#960; ile "
    "<em>z</em><sup>&#8722;<em>a</em></sup> = <em>r</em><sup>&#8722;<em>a</em></sup>e<sup>&#8722;<em>i</em>2<em>a</em>&#960;</sup>'dır; "
    "tek kutup <em>z</em> = &#8722;1 halkanın içindedir.",
    aria="Dal kesimi boyunca kesik halka (anahtar deligi) yolu")

# ---- D2: in the branch 0 < θ < 2π the argument of -i is 3π/2, not -π/2
p = cplane(40, 24, 320, (-1.75, 1.75), (-1.6, 1.6))
p.origin_axes()
p.line([(0, 0), (1.75, 0)], REMARK, 3.4, None, 0.4)
angle_arc(p, 0, PI / 2, 0.35, THEORY, 1.7)
angle_arc(p, 0, 3 * PI / 2, 0.75, PRACTICE, 2.0)
cross(p, (0, 1), THEORY, 4.2)
cross(p, (0, -1), THEORY, 4.2)
p.label(0, 1, "i", 10, 4, THEORY, 13, "start", True, True)
p.label(0, 1, "z" + _sup2("1/2", " = e") + sup("i&#960;/4"), 10, -12, THEORY, 10.5, "start")
p.label(0, -1, MINUS + "i", 10, 4, THEORY, 13, "start", True, True)
p.label(0, -1, "z" + _sup2("1/2", " = e") + sup("i3&#960;/4"), 10, 20, THEORY, 10.5, "start")
p.label(0, 0.35, "&#952; = &#960;/2", 5, -7, THEORY, 10.5, "start", True)
p.label(-0.44, -0.78, "&#952; = 3&#960;/2", 0, 0, PRACTICE, 11.5, "end", True)
p.label(-0.44, -0.78, "(" + MINUS + "&#960;/2 değil)", 0, 14, PRACTICE, 10.5, "end", False, True)
p.label(1.0, 0, "kesim: &#952; = 0", 0, -8, REMARK, 10.5, "start", False, True)
p.label(-1.7, 1.45, "0 &lt; &#952; &lt; 2&#960;", 0, 0, THEORY, 12, "start", True)
OUT["uygulamalar-arg-eksi-i"] = figure(
    400, 366, [p],
    "0 &lt; <em>&#952;</em> &lt; 2&#960; dalında açı, kesimden (pozitif reel eksen) başlayarak saat yönünün tersine "
    "ölçülür: <em>i</em> için <em>&#952;</em> = &#960;/2, &#8722;<em>i</em> için <em>&#952;</em> = 3&#960;/2 — "
    "esas argüman &#8722;&#960;/2 bu dalda geçerli değildir. Bu yüzden &#8722;<em>i</em> noktasında "
    "<em>z</em><sup>1/2</sup> = e<sup>i3&#960;/4</sup> alınır; &#8722;&#960;/2 kullanılırsa rezidünün işareti yanlış çıkar.",
    aria="0 &lt; theta &lt; 2pi dalinda arg(-i) = 3pi/2")

# ============================================ trigonometrik-integraller
# ---- T1: on the unit circle z^{-1} = z̄; z + z^{-1} = 2 cos θ, z - z^{-1} = 2i sin θ
th = math.radians(50)
z = polar(1, th)
zb = (z[0], -z[1])
p = cplane(40, 24, 320, (-1.5, 2.0), (-1.35, 1.35))
p.origin_axes()
p.circle(0, 0, 1, BASE, 1.8)
_uyg_arc_arrow(p, 0, 0, 1, 2 * PI / 3, BASE, 1.8)
p.label(*polar(1, 2.35), "C", -6, -4, BASE, 12.5, "end", True, True)
p.line([(0, 0), z], THEORY, 1.6)
p.line([z, zb], REMARK, 1.1, "4 3", 0.7)
p.line([z, (0, z[1])], REMARK, 1.1, "4 3", 0.7)
angle_arc(p, 0, th, 0.3, THEORY, 1.5)
p.label(*polar(0.4, th / 2), "&#952;", 0, 4, THEORY, 12.5, "start", True, True)
dot(p, z, THEORY, 4.0)
dot(p, zb, THEORY, 4.0)
p.label(*z, "z = e" + sup("i&#952;"), 9, -3, THEORY, 12, "start", True)
p.label(*zb, "z" + _sup2(MINUS + "1", " = e") + _sup2(MINUS + "i&#952;", " = " + BAR_Z), 9, 14, THEORY, 12, "start", True)
dot(p, (z[0], 0), PRACTICE, 3.4)
p.label(z[0], 0, "cos &#952;", -6, 15, PRACTICE, 11, "end", False, True)
dot(p, (0, z[1]), PRACTICE, 3.4)
p.label(0, z[1], "sin &#952;", -8, 4, PRACTICE, 11, "end", False, True)
tip = (z[0] - 0.35 * math.sin(th), z[1] + 0.35 * math.cos(th))
p.arrow(z, tip, PRACTICE, 1.9)
p.label(*tip, "dz = iz d&#952;", 4, -8, PRACTICE, 11.5, "start", False, True)
p.label(1.1, 0.5, "z + z" + _sup2(MINUS + "1", " = 2 cos &#952;"), 0, 0, TEXT, 11.5, "start")
p.label(1.1, 0.28, "z " + MINUS + " z" + _sup2(MINUS + "1", " = 2i sin &#952;"), 0, 0, TEXT, 11.5, "start")
OUT["uygulamalar-birim-cember-z"] = figure(
    400, 320, [p],
    "Birim çember üzerinde |<em>z</em>| = 1 olduğundan <em>z</em><sup>&#8722;1</sup> = <em>z&#773;</em>: "
    "<em>z</em> ile <em>z</em><sup>&#8722;1</sup> reel eksene göre simetriktir. Toplamları reel ve tam 2 cos <em>&#952;</em>, "
    "farkları sanal ve 2<em>i</em> sin <em>&#952;</em>'dır; (3) değişimleri bu geometrinin cebirsel yazımıdır. "
    "<em>&#952;</em> artarken <em>z</em> çember boyunca teğet yönde, <em>iz</em> hızıyla ilerler: d<em>z</em> = <em>iz</em> d<em>&#952;</em>.",
    aria="Birim cember uzerinde z ve z^{-1}: cos ve sin geometrisi")

# ---- T2: the two roots of the quadratic are reciprocal-like: one inside, one outside
p = cplane(24, 30, 236, (-1.45, 1.45), (-2.3, 1.35))
p.origin_axes()
p.circle(0, 0, 1, BASE, 1.8)
_uyg_arc_arrow(p, 0, 0, 1, 2 * PI / 3, BASE, 1.8)
p.label(*polar(1, 2.35), "C", -6, -4, BASE, 12.5, "end", True, True)
dot(p, (0, -0.5), THEORY, 4.2)
p.label(0, -0.5, "z" + SUB1, 9, 4, THEORY, 12.5, "start", True, True)
hollow(p, (0, -2), REMARK, 4.0)
p.label(0, -2, "z" + SUB2, 9, 4, REMARK, 12.5, "start", True, True)
panel_title(p, "1 + a sin &#952;, a = 0,8")
lx, ly = 290, 30 + 44
p.text_px(lx, ly, "paydanın sıfırları (a = 0,8):", TEXT, 11, "start", False, True)
p.text_px(lx, ly + 30, "z" + SUB1 + " = " + MINUS + "i/2,  |z" + SUB1 + "| = 1/2 &lt; 1", THEORY, 12, "start", True)
p.text_px(lx, ly + 46, "birim çemberin içinde", THEORY, 10.5, "start", False, True)
p.text_px(lx, ly + 76, "z" + SUB2 + " = " + MINUS + "2i,  |z" + SUB2 + "| = 2 &gt; 1", REMARK, 12, "start", True)
p.text_px(lx, ly + 92, "birim çemberin dışında", REMARK, 10.5, "start", False, True)
p.text_px(lx, ly + 124, "z" + SUB1 + "z" + SUB2 + " = " + MINUS + "1  &#8658;  |z" + SUB1 + "|&#183;|z" + SUB2 + "| = 1:", TEXT, 11.5, "start", True)
p.text_px(lx, ly + 140, "biri içerideyse öteki", TEXT, 11.5, "start", True)
p.text_px(lx, ly + 156, "zorunlu olarak dışarıdadır.", TEXT, 11.5, "start", True)
OUT["uygulamalar-kutup-cifti"] = figure(
    520, 364, [p],
    "<em>a</em> = 0,8 için paydanın sıfırları <em>z</em><sub>1</sub> = &#8722;<em>i</em>/2 ve "
    "<em>z</em><sub>2</sub> = &#8722;2<em>i</em>'dir. Çarpımları &#8722;1 olduğundan modülleri birbirinin tersidir: "
    "büyük olanı çemberin dışında kalır, küçük olanı içeride. Rezidü teoremine yalnızca içerideki "
    "<em>z</em><sub>1</sub> girer; aynı akıl yürütme (b) alıştırmasındaki <em>z</em><sub>+</sub><em>z</em><sub>&#8722;</sub> = 1 için de geçerlidir.",
    css_class=WIDE, aria="Birim cemberin icinde ve disinda kalan kutup cifti")

# ============================================ arguman-ilkesi-ve-rouche
# ---- A1: C in the z-plane and its image Γ = f(C) winding around w = 0
p1 = cplane(24, 34, 250, (-1.45, 1.45), (-1.45, 1.45))
p1.origin_axes()
p1.circle(0, 0, 1, BASE, 1.9)
_uyg_arc_arrow(p1, 0, 0, 1, 2 * PI / 3, BASE, 1.9)
p1.label(*polar(1, 2.35), "C", -6, -4, BASE, 12.5, "end", True, True)
cross(p1, (0.3, 0.2), THEORY, 4.2)
p1.label(0.3, 0.2, "f'nin sıfırı", 8, 4, THEORY, 11, "start", False, True)
zt = polar(1, math.radians(40))
dot(p1, zt, PRACTICE, 4.2)
p1.label(*zt, "z(t)", 8, -4, PRACTICE, 12.5, "start", True, True)
panel_title(p1, "z düzlemi")

p2 = cplane(300, 34, 250, (-0.9, 2.0), (-1.15, 1.75))
p2.origin_axes(xlabel="u", ylabel="v")
gam = [(0.3 + math.cos(t) + 0.3 * math.cos(2 * t), 0.2 + 0.9 * math.sin(t)) for t in (2 * PI * k / 120 for k in range(120))]
closed_curve(p2, gam, THEORY, 1.9, arrow_at=42)
p2.label(-0.26, 1.05, "&#915; = f(C)", 0, -12, THEORY, 12.5, "middle", True, True)
tw = math.radians(40)
w = (0.3 + math.cos(tw) + 0.3 * math.cos(2 * tw), 0.2 + 0.9 * math.sin(tw))
p2.line([(0, 0), w], REMARK, 1.1, "4 3", 0.8)
angle_arc(p2, 0, math.atan2(w[1], w[0]), 0.4, PRACTICE, 1.7)
p2.label(*polar(0.5, 0.3), "&#966;", 2, 2, PRACTICE, 12.5, "start", True, True)
dot(p2, (0, 0), TEXT, 3.2)
p2.label(0, 0, "0", -7, 14, TEXT, 11.5, "end", True)
dot(p2, w, PRACTICE, 4.2)
p2.label(*w, "w = f(z(t))", 6, -8, PRACTICE, 12.5, "start", True, True)
panel_title(p2, "w düzlemi: w = f(z)")
OUT["uygulamalar-dolanma-sayisi"] = figure(
    570, 300, [p1, p2],
    "<em>z</em>(<em>t</em>) noktası <em>C</em>'yi pozitif yönde bir kez dolaşırken görüntüsü <em>w</em> = <em>f</em>(<em>z</em>(<em>t</em>)), "
    "<em>w</em> düzleminde kapalı &#915; eğrisini çizer. <em>f</em>, <em>C</em> üzerinde sıfırlanmadığından &#915; orijinden geçmez ve "
    "<em>&#966;</em> = arg <em>w</em> sürekli izlenebilir; tur tamamlandığında biriken fark &#916;<sub><em>C</em></sub> arg <em>f</em>, "
    "2&#960;'nin bir katıdır. Burada &#915; orijini bir kez sarar: dolanma sayısı 1, yani <em>C</em> içinde bir sıfır.",
    css_class=WIDE, aria="C cevresi ve goruntusu Gamma'nin orijin etrafinda dolanmasi")

# ---- A2: Rouché's proof — F(C) stays inside |w - 1| < 1, so it cannot wind around 0
p = cplane(40, 24, 320, (-0.8, 2.4), (-1.35, 1.35))
disk_fill(p, 1, 0, 1, THEORY, 0.10)
p.origin_axes(xlabel="u", ylabel="v")
p.circle(1, 0, 1, THEORY, 1.6, "5 4")
dot(p, (1, 0), TEXT, 3.2)
p.label(1, 0, "1", 0, 16, TEXT, 11.5, "middle")
fc = [(1 + 0.5 * math.cos(t) + 0.15 * math.cos(3 * t), 0.55 * math.sin(t)) for t in (2 * PI * k / 120 for k in range(120))]
closed_curve(p, fc, PRACTICE, 2.0, arrow_at=15)
p.label(1, 0.2, "F(C)", 0, 0, PRACTICE, 12.5, "middle", True, True)
# extreme rays from 0: tangent to F(C) at the points of maximal / minimal argument
w1 = max(fc, key=lambda q: math.atan2(q[1], q[0]))
w2 = (w1[0], -w1[1])
ang = math.atan2(w1[1], w1[0])
p.line([(0, 0), w1], REMARK, 1.1, "4 3", 0.8)
p.line([(0, 0), w2], REMARK, 1.1, "4 3", 0.8)
p.arc(0, 0, 0.38, -ang, ang, PRACTICE, 1.6)
_uyg_arc_arrow(p, 0, 0, 0.38, ang, PRACTICE, 1.6, ccw=True)
_uyg_arc_arrow(p, 0, 0, 0.38, -ang, PRACTICE, 1.6, ccw=False)
dot(p, (0, 0), PRACTICE, 4.0)
p.label(0, 0, "0", -8, 14, PRACTICE, 12, "end", True)
p.label(-0.78, 1.2, "|w " + MINUS + " 1| &lt; 1", 0, 0, THEORY, 11.5, "start", True)
p.label(-0.75, -1.12, "0 açık diskin dışında:", 0, 0, REMARK, 10.5, "start", False, True)
p.label(-0.75, -1.27, "arg F salınır, tam tur atamaz", 0, 0, PRACTICE, 10.5, "start", False, True)
OUT["uygulamalar-rouche-disk"] = figure(
    400, 342, [p],
    "<em>C</em> üzerinde |<em>F</em>(<em>z</em>) &#8722; 1| &lt; 1 olduğundan görüntü eğrisi <em>F</em>(<em>C</em>), merkezi 1 "
    "olan açık birim diskin içinde kalır. Orijin bu diskin dışındadır (sınır üzerinde); diskteki bir kapalı eğri orijini "
    "saramaz — arg <em>F</em> ileri geri salınır ama tam tur biriktiremez. Dolayısıyla &#916;<sub><em>C</em></sub> arg <em>F</em> = 0 "
    "ve <em>f</em> + <em>g</em> ile <em>f</em> aynı sayıda sıfıra sahiptir.",
    aria="Rouche ispati: F(C) egrisi |w-1| &lt; 1 diskinin icinde kalir")

# ============================================ ters-laplace-donusumu
# ---- L1: the Bromwich line L_R and the closing semicircle C_R centred at γ, opening left
g, R, R0 = 0.45, 1.2, 0.7
p = cplane(40, 24, 320, (-1.55, 1.65), (-1.55, 1.55))
p.sector(g, 0, R, PI / 2, 3 * PI / 2, THEORY, 0.08)
p.origin_axes(xlabel="Re s", ylabel="Im s")
p.line([(g, -1.55), (g, 1.55)], REMARK, 1.0, "4 3", 0.55)
p.circle(0, 0, R0, BASE, 1.2, "4 3", opacity=0.8)
p.line([(g, -R), (g, R)], PRACTICE, 2.2)
_uyg_seg_arrow(p, (g, -R), (g, R), PRACTICE, 2.2, 0.62)
p.arc(g, 0, R, PI / 2, 3 * PI / 2, PRACTICE, 1.8, "6 4", samples=64)
_uyg_arc_arrow(p, g, 0, R, PI, PRACTICE, 1.8)
dot(p, (g, R), PRACTICE, 3.2)
dot(p, (g, -R), PRACTICE, 3.2)
p.label(g, R, "&#947; + iR", 8, 4, PRACTICE, 11.5, "start", False, True)
p.label(g, -R, "&#947; " + MINUS + " iR", 8, 4, PRACTICE, 11.5, "start", False, True)
p.label(g, 0.6, "L" + _uyg_sub("R"), 8, 0, PRACTICE, 12.5, "start", True, True)
p.label(g - 0.84, 0.855, "C" + _uyg_sub("R"), -6, -6, PRACTICE, 12.5, "end", True, True)
p.label(g, 1.5, "Re s = &#947;", 8, 0, REMARK, 10.5, "start", False, True)
for s, lab, dx, dy, an in (((-0.3, 0.45), "s" + SUB1, 8, -3, "start"), ((-0.3, -0.45), "s" + SUB2, 8, 5, "start"),
                           ((-0.55, 0), "s" + SUB3, -2, 15, "middle"), ((0.1, 0.28), "s&#8324;", 8, 4, "start")):
    cross(p, s, THEORY, 4.0)
    p.label(*s, lab, dx, dy, THEORY, 11, an, True, True)
p.label(*polar(R0, -1.05), "|s| = R" + SUB0, 16, 12, BASE, 10.5, "start", False, True)
p.label(-1.5, -1.45, "R &gt; R" + SUB0 + " + &#947;", 0, 0, TEXT, 11, "start", False, True)
OUT["uygulamalar-bromwich"] = figure(
    400, 382, [p],
    "Bromwich yolu <em>L<sub>R</sub></em>, Re <em>s</em> = <em>&#947;</em> dikey doğrusu üzerinde "
    "<em>&#947;</em> &#8722; <em>iR</em>'den <em>&#947;</em> + <em>iR</em>'ye gider. Yol, merkezi <em>&#947;</em> olan ve "
    "<strong>sola</strong> açılan <em>C<sub>R</sub></em> yarım çemberiyle (<em>s</em> = <em>&#947;</em> + <em>R</em>e<sup>i<em>&#952;</em></sup>, "
    "&#960;/2 &#8804; <em>&#952;</em> &#8804; 3&#960;/2) kapatılır. Tüm tekil noktalar |<em>s</em>| &#8804; <em>R</em><sub>0</sub> diskindedir; "
    "<em>R</em> &gt; <em>R</em><sub>0</sub> + <em>&#947;</em> alınınca hepsi yarım dairesel bölgenin içinde kalır.",
    aria="Bromwich dogrusu ve gamma merkezli sola acilan yarim cember")

# ---- L2: pole positions decide growth versus oscillation (exercise d)
r2 = math.sqrt(2)
p = cplane(40, 30, 320, (-2.1, 2.9), (-2.05, 2.05))
p.origin_axes(xlabel="Re s", ylabel="Im s")
p.circle(0, 0, r2, REMARK, 1.0, "4 3", opacity=0.55)
cross(p, (r2, 0), PRACTICE, 4.4)
cross(p, (-r2, 0), PRACTICE, 4.4)
cross(p, (0, r2), THEORY, 4.4)
cross(p, (0, -r2), THEORY, 4.4)
p.label(r2, 0, "&#8730;2", 0, 17, PRACTICE, 11.5, "middle", True)
p.label(-r2, 0, MINUS + "&#8730;2", 0, 17, PRACTICE, 11.5, "middle", True)
p.label(0, r2, "i&#8730;2", -9, 4, THEORY, 11.5, "end", True)
p.label(0, -r2, MINUS + "i&#8730;2", -9, 4, THEORY, 11.5, "end", True)
p.label(2.85, 1.85, "reel çift &#177;&#8730;2:", 0, 0, PRACTICE, 11.5, "end", True)
p.label(2.85, 1.62, "cosh &#8730;2t, büyüme", 0, 0, PRACTICE, 11, "end", False, True)
p.label(2.85, -1.62, "sanal çift &#177;i&#8730;2:", 0, 0, THEORY, 11.5, "end", True)
p.label(2.85, -1.85, "cos &#8730;2t, salınım", 0, 0, THEORY, 11, "end", False, True)
OUT["uygulamalar-kutup-konumu"] = figure(
    400, 340, [p],
    "<em>s</em><sup>4</sup> = 4 denkleminin dört kökü |<em>s</em>| = &#8730;2 çemberi üzerindedir. Reel eksendeki "
    "çift e<sup>&#177;&#8730;2<em>t</em></sup> üstellerini, yani hiperbolik (büyüyen) terimi; sanal eksendeki çift "
    "e<sup>&#177;<em>i</em>&#8730;2<em>t</em></sup> üstellerini, yani trigonometrik (salınan) terimi doğurur. "
    "Kutbun reel kısmı büyüme hızını, sanal kısmı salınım frekansını verir.",
    aria="Reel ve sanal eksendeki kutup ciftleri: buyume ve salinim")

for name, content in OUT.items():
    with io.open(os.path.join(OUT_DIR, "complex-%s.md" % name), "w", encoding="utf-8") as f:
        f.write(content)
print("generated:", ", ".join(OUT))
