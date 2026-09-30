# -*- coding: utf-8 -*-
"""
Generates the SVG figures used in the "Analiz 3" chapters (dersler/analiz-3).

The figures are NOT produced at build time. Run this script, then

    python scripts/center_figures.py "analysis3-*.md"

and paste the resulting markup into the .qmd files. Figures go INSIDE the box
they explain (theorem, proof, example, solution), never inside a definition box
and never directly under a heading.

The captions are Turkish on purpose: they are the text shown on the site.

Usage:   python scripts/analysis3_figures.py && python scripts/center_figures.py "analysis3-*.md"
Output:  scripts/_figures/analysis3-<name>.md
"""
import io
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from svg_plot import *  # noqa: E402,F403 — Plot, figure, colors, WIDE, hollow, dot, ...

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_figures")
os.makedirs(OUT_DIR, exist_ok=True)
OUT = {}

EPS, MINUS_S, SQRT_S = "&#949;", "&#8722;", "&#8730;"


def subs(s, size=9):
    """Subscript inside an SVG <text>: 'f' + subs('n')."""
    return f'<tspan font-size="{size}" dy="4">{s}</tspan><tspan dy="-4">&#8203;</tspan>'


def sups(s, size=8.5):
    """Superscript inside an SVG <text>."""
    return f'<tspan font-size="{size}" dy="-5">{s}</tspan><tspan dy="5">&#8203;</tspan>'


def curve(p, f, x0, x1, color=THEORY, width=1.9, samples=240, dash=None, opacity=1.0):
    """Polyline of y = f(x) on [x0, x1]."""
    pts = [(x0 + (x1 - x0) * k / samples, f(x0 + (x1 - x0) * k / samples)) for k in range(samples + 1)]
    p.line(pts, color, width, dash, opacity)


def tfmt(v):
    """Tick label with the Turkish decimal comma: 0.5 -> '0,5'."""
    return fmt(v).replace(".", ",")


def frac_ticks(p, items, y=0.0, dy=15, size=10.5):
    """Hand-placed x tick labels such as 1/3, 1/2 at the given data abscissas."""
    for xv, txt in items:
        p.line([(xv, y), (xv, y)], TEXT, 1.0)
        p.label(xv, y, txt, 0, dy, TEXT, size, "middle")


# ============================================================ nok-xn
# The powers x^n on [0, 1]: the curves collapse onto the axis, (1, 1) stays put.
p = Plot(44, 22, 270, 220, (0, 1.06), (0, 1.1))
p.axes((0.5, 1), (0.5, 1), "x", "y", tfmt, tfmt)
for n, op in ((1, 1.0), (2, 0.85), (3, 0.72), (5, 0.6), (10, 0.5), (30, 0.42)):
    curve(p, lambda t, n=n: t ** n, 0, 1, THEORY, 1.8, 300, None, op)
p.line([(0, 0), (1, 0)], PRACTICE, 2.6)
hollow(p, (1, 0), PRACTICE, 3.6)
dot(p, (1, 1), PRACTICE, 3.8)
p.label(0.50, 0.50, "n = 1", -8, -6, THEORY, 10.5, "end", False, True)
p.label(1.0, 0.30, "n = 30", 8, 0, THEORY, 10.5, "start", False, True)
p.label(0.22, 0.0, "noktasal limit", 0, 16, PRACTICE, 10.5, "middle", False, True)
OUT["nok-xn"] = figure(
    390, 270, [p],
    "<em>f<sub>n</sub></em>(<em>x</em>) = <em>x<sup>n</sup></em> dizisinin <em>n</em> = 1, 2, 3, 5, 10, 30 terimleri. "
    "[0, 1) üzerinde eğriler yatay eksene çöker; (1, 1) noktası ise yerinde kalır. "
    "Noktasal limit <em>x</em> = 1'de sıçrar.",
    aria="Powers of x on the unit interval collapsing to zero except at the right endpoint")

# ============================================================ nok-tepe
# 2nx/(1+n^2x^2): the bump moves left, its height stays 1.
p = Plot(44, 22, 290, 200, (0, 1.05), (0, 1.18))
p.axes((0.25, 0.5, 1), (0.5, 1), "x", "y", tfmt, tfmt)
p.line([(0, 1), (1.0, 1)], TEXT, 1.0, "4 3", 0.5)
for n, op in ((1, 1.0), (2, 0.85), (4, 0.7), (8, 0.58), (20, 0.46)):
    curve(p, lambda t, n=n: 2 * n * t / (1 + n * n * t * t), 0, 1, THEORY, 1.8, 500, None, op)
    dot(p, (1.0 / n, 1), PRACTICE, 3.0)
p.label(1.0, 1.0, "n = 1", -4, -8, THEORY, 10.5, "end", False, True)
p.label(1.0, 2 * 20 / (1 + 400), "n = 20", -4, -7, THEORY, 10.5, "end", False, True)
OUT["nok-tepe"] = figure(
    380, 250, [p],
    "<em>f<sub>n</sub></em>(<em>x</em>) = 2<em>nx</em>/(1 + <em>n</em><sup>2</sup><em>x</em><sup>2</sup>) dizisinin "
    "<em>n</em> = 1, 2, 4, 8, 20 terimleri. Tepe noktası (1/<em>n</em>, 1) sola kayar ama alçalmaz; "
    "her sabit <em>x</em> noktasında değerler yine de 0'a gider.",
    aria="Bumps of height one sliding to the left while the pointwise limit is zero")

# ============================================================ nok-nx
# The lines y = nx: the values at x = 1 are 1, 2, 3, ...
p = Plot(44, 22, 250, 220, (0, 2.3), (0, 5.6))
p.axes((1, 2), (1, 2, 3, 4, 5), "x", "y")
p.line([(1, 0), (1, 5.3)], TEXT, 1.0, "4 3", 0.5)
for n in (1, 2, 3, 4, 5):
    xe = min(2.2, 5.4 / n)
    p.line([(0, 0), (xe, n * xe)], THEORY, 1.8, None, 1.0 - 0.1 * n)
    dot(p, (1, n), PRACTICE, 3.2)
    p.line([(0, n), (1, n)], TEXT, 1.0, "2 3", 0.35)
p.label(2.2, 2.2, "f" + subs("1"), 5, 4, THEORY, 11, "start", False, True)
p.label(2.2, 4.4, "f" + subs("2"), 5, 4, THEORY, 11, "start", False, True)
p.label(5.4 / 5, 5.4, "f" + subs("5"), -2, -7, THEORY, 11, "middle", False, True)
OUT["nok-nx"] = figure(
    350, 270, [p],
    "<em>f<sub>n</sub></em>(<em>x</em>) = <em>nx</em> doğruları. <em>x</em> = 1 noktasındaki değerler "
    "1, 2, 3, &#8230; sayı dizisini oluşturur ve bu dizi ıraksaktır.",
    aria="Lines through the origin with slopes one to five and their values at x equal one")

# ============================================================ dzg-serit
# The epsilon band around f: f_n must stay inside it on all of E.
def f_band(t):
    return 1.55 + 0.45 * math.sin(1.1 * t - 0.4) + 0.12 * t


def fn_band(t):
    return f_band(t) + 0.20 * math.sin(5.2 * t) * math.exp(-0.12 * t) * 0.85


EB = 0.34
A_E, B_E = 0.6, 4.6
p = Plot(44, 22, 300, 200, (0, 4.9), (0, 3.2))
p.axes((), (), "x", "y")
xs = [A_E + (B_E - A_E) * k / 120 for k in range(121)]
p.polygon([(t, f_band(t) + EB) for t in xs] + [(t, f_band(t) - EB) for t in reversed(xs)], THEORY, 0.13)
curve(p, lambda t: f_band(t) + EB, A_E, B_E, THEORY, 1.2, 200, "5 3", 0.9)
curve(p, lambda t: f_band(t) - EB, A_E, B_E, THEORY, 1.2, 200, "5 3", 0.9)
curve(p, f_band, A_E, B_E, THEORY, 2.1)
curve(p, fn_band, A_E, B_E, PRACTICE, 1.8, 400)
p.line([(A_E, 0), (B_E, 0)], BASE, 3.2)
p.vline(A_E, 0, f_band(A_E) + EB)
p.vline(B_E, 0, f_band(B_E) + EB)
p.label((A_E + B_E) / 2, 0, "E", 0, 16, BASE, 11.5, "middle", True, True)
p.label(B_E, f_band(B_E) + EB, "f + " + EPS, 6, 2, THEORY, 10.5, "start", False, True)
p.label(B_E, f_band(B_E), "f", 6, 4, THEORY, 10.5, "start", True, True)
p.label(B_E, f_band(B_E) - EB, "f " + MINUS_S + " " + EPS, 6, 6, THEORY, 10.5, "start", False, True)
p.label(3.05, f_band(3.05) - EB, "f" + subs("n"), 0, 18, PRACTICE, 10.5, "middle", False, True)
p.line([(3.05, f_band(3.05) - EB - 0.13), (2.78, fn_band(2.78) - 0.04)], PRACTICE, 1.0, None, 0.7)
OUT["dzg-serit"] = figure(
    500, 250, [p],
    "Düzgün yakınsaklığın geometrik anlamı: <em>n</em> &#8805; <em>N</em> olan her <em>f<sub>n</sub></em> grafiği, "
    "<em>E</em> kümesinin tamamı üzerinde <em>f</em>'nin çevresindeki &#949;-şeridinin içinde kalır.",
    css_class=WIDE,
    aria="A function f with an epsilon band around it and a nearby function staying inside the band")

# ============================================================ dzg-xn-serit
# x^N leaves the band of width 1/4 around the pointwise limit at x_N = 2^(-1/N).
p = Plot(44, 22, 290, 210, (0, 1.06), (0, 1.12))
p.axes((0.5, 1), (0.25, 0.5, 1), "x", "y", tfmt, tfmt)
p.polygon([(0, 0), (1, 0), (1, 0.25), (0, 0.25)], BASE, 0.16)
p.line([(0, 0.25), (1, 0.25)], BASE, 1.2, "5 3")
p.line([(0, 0.5), (1, 0.5)], TEXT, 1.0, "2 3", 0.45)
for n, op in ((3, 1.0), (8, 0.8), (25, 0.62)):
    curve(p, lambda t, n=n: t ** n, 0, 1, THEORY, 1.8, 400, None, op)
    dot(p, (2 ** (-1.0 / n), 0.5), PRACTICE, 3.4)
p.label(0.30, 0.25, EPS + subs("0") + " = 1/4 şeridi", 0, 14, BASE, 10.5, "middle", False, True)
p.label(2 ** (-1.0 / 3), 0.5, "x" + subs("3"), -6, -7, PRACTICE, 10.5, "end", False, True)
p.label(0.72, 0.72 ** 3, "N = 3", -9, -3, THEORY, 10.5, "end", False, True)
p.label(1.0, 0.80, "N = 25", 8, 0, THEORY, 10.5, "start", False, True)
OUT["dzg-xn-serit"] = figure(
    410, 262, [p],
    "<em>y</em> = <em>x<sup>N</sup></em> eğrileri (<em>N</em> = 3, 8, 25) ve noktasal limitin çevresindeki "
    "&#949;<sub>0</sub> = 1/4 şeridi. Her eğri <em>x<sub>N</sub></em> = 2<sup>&#8722;1/<em>N</em></sup> noktasında "
    "1/2 yüksekliğine ulaşır ve şeridin dışına çıkar.",
    aria="Power curves leaving the band of width one quarter near the right endpoint")

# ============================================================ dzg-cadir
# Tent functions: base [0, 2/n], apex (1/n, n^2).
p = Plot(44, 22, 270, 230, (0, 2.15), (0, 9.9))
p.axes((1, 2), (1, 4, 9), "x", "y")
for n, op in ((1, 1.0), (2, 0.8), (3, 0.62)):
    p.line([(0, 0), (1.0 / n, n * n), (2.0 / n, 0), (2, 0)], THEORY, 1.9, None, op)
    p.line([(0, n * n), (1.0 / n, n * n)], TEXT, 1.0, "2 3", 0.4)
    p.line([(1.0 / n, 0), (1.0 / n, n * n)], TEXT, 1.0, "2 3", 0.4)
    dot(p, (1.0 / n, n * n), PRACTICE, 3.2)
p.label(1.0, 1.0, "f" + subs("1"), 8, -5, THEORY, 11, "start", False, True)
p.label(0.5, 4.0, "f" + subs("2"), 8, -3, THEORY, 11, "start", False, True)
p.label(1.0 / 3, 9.0, "f" + subs("3"), 8, 0, THEORY, 11, "start", False, True)
p.label(1.0 / 3, 0, "1/3", -3, 15, TEXT, 10, "middle")
p.label(0.5, 0, "1/2", 5, 15, TEXT, 10, "middle")
OUT["dzg-cadir"] = figure(
    360, 282, [p],
    "Çadır fonksiyonları <em>f</em><sub>1</sub>, <em>f</em><sub>2</sub>, <em>f</em><sub>3</sub>: taban [0, 2/<em>n</em>] "
    "aralığına daralırken tepe yüksekliği <em>n</em><sup>2</sup> ile büyür. Her noktada değerler sonunda 0 olur, "
    "ama grafikler sıfır fonksiyonuna yaklaşmaz.",
    aria="Triangular tent functions getting narrower and taller")

# ============================================================ olc-xe-nx
# x e^{-nx}: apex (1/n, 1/(en)) moves left AND sinks.
p = Plot(50, 22, 300, 200, (0, 3.1), (0, 0.42))
p.axes((1, 2, 3), (0.1, 0.2, 0.3), "x", "y", tfmt, tfmt)
for n, op in ((1, 1.0), (2, 0.82), (4, 0.66), (8, 0.52)):
    curve(p, lambda t, n=n: t * math.exp(-n * t), 0, 3, THEORY, 1.8, 600, None, op)
    dot(p, (1.0 / n, 1.0 / (math.e * n)), PRACTICE, 3.2)
p.label(1.0, 1 / math.e, "(1, 1/e)", 6, -6, PRACTICE, 10.5, "start", False, True)
p.label(0.5, 0.5 / math.e, "(1/2, 1/(2e))", 7, -3, PRACTICE, 10.5, "start", False, True)
p.label(2.2, 2.2 * math.exp(-2.2), "n = 1", 0, -8, THEORY, 10.5, "start", False, True)
OUT["olc-xe-nx"] = figure(
    390, 252, [p],
    "<em>f<sub>n</sub></em>(<em>x</em>) = <em>x</em>e<sup>&#8722;<em>nx</em></sup> dizisinin <em>n</em> = 1, 2, 4, 8 terimleri. "
    "Tepe noktası (1/<em>n</em>, 1/(e<em>n</em>)) hem sola kayar hem alçalır; en büyük fark 0'a gittiğinden "
    "yakınsama düzgündür.",
    aria="Curves x times exp of minus n x with maxima moving left and down")

# ============================================================ int-dikdortgen
# Steps of height n on (0, 1/n]: every area equals 1.
p = Plot(44, 22, 270, 220, (0, 1.08), (0, 4.5))
p.axes((0.25, 0.5, 1), (1, 2, 4), "x", "y", tfmt, fmt)
for n, op in ((1, 0.10), (2, 0.16), (4, 0.24)):
    p.polygon([(0, 0), (1.0 / n, 0), (1.0 / n, n), (0, n)], THEORY, op, THEORY, 1.5)
p.label(0.75, 1.0, "f" + subs("1"), 0, -7, THEORY, 11, "middle", False, True)
p.label(0.375, 2.0, "f" + subs("2"), 0, -7, THEORY, 11, "middle", False, True)
p.label(0.25, 4.0, "f" + subs("4"), 8, 4, THEORY, 11, "start", False, True)
p.label(0.72, 0.5, "alan = 1", 0, 4, TEXT, 10.5, "middle", False, True)
OUT["int-dikdortgen"] = figure(
    360, 272, [p],
    "<em>f</em><sub>1</sub>, <em>f</em><sub>2</sub>, <em>f</em><sub>4</sub> basamak fonksiyonları. Dikdörtgenler incelip "
    "yükselirken alanları hep 1 kalır; noktasal limit olan sıfır fonksiyonunun altında ise alan yoktur.",
    aria="Rectangles of width one over n and height n, all with area one")

# ============================================================ tur-salinim
# sin(nx)/sqrt(n): amplitude shrinks, slopes grow.
p = Plot(44, 22, 330, 190, (-3.3, 3.3), (-1.2, 1.2))
p.axes((-3, -2, -1, 1, 2, 3), (-1, -0.5, 0.5, 1), "x", "y", fmt, tfmt)
for n, col, op, w in ((1, THEORY, 0.55, 1.6), (4, THEORY, 0.8, 1.7), (16, PRACTICE, 1.0, 1.7)):
    curve(p, lambda t, n=n: math.sin(n * t) / math.sqrt(n), -math.pi, math.pi, col, w, 900, None, op)
for h in (0.5, 0.25):
    p.line([(-math.pi, h), (math.pi, h)], TEXT, 1.0, "3 3", 0.35)
    p.line([(-math.pi, -h), (math.pi, -h)], TEXT, 1.0, "3 3", 0.35)
p.label(math.pi / 2, 1.0, "n = 1", 6, -3, THEORY, 10.5, "start", False, True)
p.label(-2.75, 0.5, "n = 4", 0, -7, THEORY, 10.5, "middle", False, True)
p.label(2.6, -0.25, "n = 16", 0, 30, PRACTICE, 10.5, "middle", False, True)
OUT["tur-salinim"] = figure(
    420, 240, [p],
    "<em>f<sub>n</sub></em>(<em>x</em>) = sin(<em>nx</em>)/&#8730;<em>n</em> dizisinin <em>n</em> = 1, 4, 16 terimleri. "
    "Genlik 1/&#8730;<em>n</em> ile küçülür, ama salınım sıklaştığından eğimler &#8730;<em>n</em> ile büyür.",
    css_class=WIDE,
    aria="Sine waves with shrinking amplitude and growing frequency")


PI_S = "&#960;"


def pifmt(v):
    """Tick label for a multiple of pi: -pi, pi, 3pi, pi/2 ..."""
    k = v / math.pi
    sign = MINUS_S if k < 0 else ""
    k = abs(k)
    if abs(k - 1) < 1e-9:
        return sign + PI_S
    if abs(k - round(k)) < 1e-9:
        return sign + str(int(round(k))) + PI_S
    if abs(k - 0.5) < 1e-9:
        return sign + PI_S + "/2"
    return fmt(v)


# ============================================================ fka-periyodik
# Periodic extension of f(x) = x from (-pi, pi]: a sawtooth.
p = Plot(30, 22, 380, 170, (-10.4, 10.4), (-4.2, 4.2))
p.origin_axes("x", "y", (-3 * math.pi, -math.pi, math.pi, 3 * math.pi), (-math.pi, math.pi), pifmt, pifmt)
for k in (-1, 0, 1):
    c = 2 * math.pi * k
    op = 1.0 if k == 0 else 0.5
    w = 2.4 if k == 0 else 1.8
    p.line([(c - math.pi, -math.pi), (c + math.pi, math.pi)], THEORY, w, None, op)
    p.line([(c + math.pi, 0), (c + math.pi, math.pi)], TEXT, 1.0, "3 3", 0.35)
    p.line([(c + math.pi, -math.pi), (c + math.pi, -1.25)], TEXT, 1.0, "3 3", 0.35)
    hollow(p, (c - math.pi, -math.pi), THEORY, 3.2)
    dot(p, (c + math.pi, math.pi), THEORY, 3.4)
p.line([(-3 * math.pi, -math.pi), (-3 * math.pi, -1.25)], TEXT, 1.0, "3 3", 0.35)
OUT["fka-periyodik"] = figure(
    440, 214, [p],
    "<em>f</em>(<em>x</em>) = <em>x</em> fonksiyonunun (&#8722;&#960;, &#960;] aralığındaki grafiği (koyu) ve "
    "2&#960; periyotlu genişlemesi. Genişleme &#960;'nin tek katlarında &#960;'den &#8722;&#960;'ye sıçrar; "
    "dolu nokta fonksiyonun o noktadaki değerini gösterir.",
    css_class=WIDE,
    aria="Sawtooth wave obtained by extending the identity function periodically")

# ============================================================ fny-dirichlet
# Dirichlet kernels D_2, D_5, D_10 on [-pi, pi].
def dirichlet(N, t):
    return 0.5 + sum(math.cos(k * t) for k in range(1, N + 1))


p = Plot(44, 22, 330, 220, (-3.35, 3.35), (-3.2, 11.4))
p.origin_axes("&#952;", "", (-math.pi, math.pi), (), pifmt)
for N, col, op, w in ((2, THEORY, 0.55, 1.6), (5, THEORY, 0.85, 1.7), (10, PRACTICE, 1.0, 1.7)):
    curve(p, lambda t, N=N: dirichlet(N, t), -math.pi, math.pi, col, w, 900, None, op)
    p.line([(-2.6, N + 0.5), (0, N + 0.5)], TEXT, 1.0, "2 3", 0.35)
    p.label(-2.6, N + 0.5, tfmt(N + 0.5), -5, 4, TEXT, 10.5, "end")
p.label(0.22, 10.5, "D" + subs("10"), 8, 2, PRACTICE, 11, "start", False, True)
p.label(0.40, 5.5, "D" + subs("5"), 12, 0, THEORY, 11, "start", False, True)
p.label(0.95, 2.5, "D" + subs("2"), 14, -4, THEORY, 11, "start", False, True)
OUT["fny-dirichlet"] = figure(
    420, 272, [p],
    "<em>D</em><sub>2</sub>, <em>D</em><sub>5</sub> ve <em>D</em><sub>10</sub> Dirichlet çekirdekleri. "
    "Ortadaki tepe <em>N</em> + 1/2 yüksekliğine çıkıp daralır; yanlarda çekirdek işaret değiştirerek salınır.",
    aria="Dirichlet kernels of order two five and ten on the interval from minus pi to pi")

# ============================================================ fny-kismi-toplamlar
# Step 0 / pi and the partial sums S_1, S_3, S_9 of its Fourier series.
def step_sum(K, t):
    return math.pi / 2 + 2 * sum(math.sin((2 * k - 1) * t) / (2 * k - 1) for k in range(1, K + 1))


p = Plot(44, 22, 330, 210, (-3.35, 3.35), (-0.75, 3.95))
p.origin_axes("x", "y", (-math.pi, math.pi), (), pifmt)
p.line([(-math.pi, 0), (0, 0)], TEXT, 2.6)
p.line([(0, math.pi), (math.pi, math.pi)], TEXT, 2.6)
p.line([(0, 0), (0, math.pi)], TEXT, 1.0, "3 3", 0.4)
for K, col, op, w in ((1, THEORY, 0.5, 1.5), (2, THEORY, 0.78, 1.6), (5, PRACTICE, 1.0, 1.7)):
    curve(p, lambda t, K=K: step_sum(K, t), -math.pi, math.pi, col, w, 900, None, op)
for xv in (-math.pi, 0.0, math.pi):
    dot(p, (xv, math.pi / 2), BASE, 3.6)
p.line([(-0.08, math.pi), (0.08, math.pi)], TEXT, 1.0, None, 0.6)
p.label(0, math.pi, PI_S, -8, -3, TEXT, 10.5, "end")
p.label(0, math.pi / 2, PI_S + "/2", -9, 4, BASE, 10.5, "end")
p.label(math.pi / 2, step_sum(1, math.pi / 2), "S" + subs("1"), 0, -8, THEORY, 11, "middle", False, True)
p.label(2.82, step_sum(5, 2.82), "S" + subs("9"), 6, -9, PRACTICE, 11, "start", False, True)
OUT["fny-kismi-toplamlar"] = figure(
    420, 262, [p],
    "Basamak fonksiyonu (koyu) ve Fourier serisinin <em>S</em><sub>1</sub>, <em>S</em><sub>3</sub>, <em>S</em><sub>9</sub> "
    "kısmi toplamları. Hepsi sıçramanın orta noktası (0, &#960;/2)'den geçer; sıçramanın hemen yanındaki aşım "
    "terim sayısı artınca kaybolmaz.",
    aria="Step function and partial sums of its Fourier series showing overshoot near the jump")

# ============================================================ fdy-fejer
# Fejer kernels K_2, K_5, K_10 and, for contrast, the Dirichlet kernel D_5.
def fejer(N, t):
    return sum(dirichlet(j, t) for j in range(N + 1)) / (N + 1)


p = Plot(44, 22, 330, 220, (-3.35, 3.35), (-1.7, 6.2))
p.origin_axes("&#952;", "", (-math.pi, math.pi), (), pifmt)
for N in (2, 5, 10):
    p.line([(-2.6, (N + 1) / 2), (0, (N + 1) / 2)], TEXT, 1.0, "2 3", 0.35)
    p.label(-2.6, (N + 1) / 2, tfmt((N + 1) / 2), -5, 4, TEXT, 10.5, "end")
curve(p, lambda t: dirichlet(5, t), -math.pi, math.pi, TEXT, 1.2, 900, "4 3", 0.55)
for N, col, op, w in ((2, THEORY, 0.55, 1.6), (5, THEORY, 0.85, 1.7), (10, PRACTICE, 1.0, 1.8)):
    curve(p, lambda t, N=N: fejer(N, t), -math.pi, math.pi, col, w, 900, None, op)
p.label(0.12, 5.5, "K" + subs("10"), 10, -4, PRACTICE, 11, "start", False, True)
p.label(0.62, 1.9, "K" + subs("5"), 10, -2, THEORY, 11, "start", False, True)
p.label(1.55, 0.55, "K" + subs("2"), 6, -6, THEORY, 11, "start", False, True)
p.label(-0.95, -1.05, "D" + subs("5"), -8, 12, TEXT, 11, "end", False, True)
OUT["fdy-fejer"] = figure(
    420, 272, [p],
    "<em>K</em><sub>2</sub>, <em>K</em><sub>5</sub> ve <em>K</em><sub>10</sub> Fejér çekirdekleri; karşılaştırma için "
    "<em>D</em><sub>5</sub> Dirichlet çekirdeği (kesikli). Fejér çekirdeği hiç negatif olmaz ve tepe dışında hızla söner.",
    aria="Fejer kernels are nonnegative while the Dirichlet kernel oscillates in sign")

# ============================================================ fsk-genisleme
# Even and odd extensions of x(pi - x) from [0, pi] to [-pi, pi].
def arch(t):
    return t * (math.pi - t)


panels = []
for idx, (title, sign) in enumerate((("çift genişleme", 1.0), ("tek genişleme", -1.0))):
    q = Plot(36 + idx * 236, 34, 200, 170, (-3.5, 3.5), (-3.0, 3.0))
    q.origin_axes("x", "", (math.pi,), (), pifmt)
    q.line([(-math.pi, -0.09), (-math.pi, 0.09)], TEXT, 1.0, None, 0.6)
    q.label(-math.pi, 0, MINUS_S + PI_S, 0, 15 if sign > 0 else -8, TEXT, 11, "middle")
    curve(q, lambda t, sign=sign: sign * arch(-t), -math.pi, 0, THEORY, 1.8, 200, None, 0.5)
    curve(q, arch, 0, math.pi, THEORY, 2.5, 200)
    q.line([(-0.12, math.pi ** 2 / 4), (0.12, math.pi ** 2 / 4)], TEXT, 1.0, None, 0.6)
    q.label(0, math.pi ** 2 / 4, PI_S + sups("2") + "/4", -8, -3, TEXT, 10, "end")
    panel_title(q, title)
    panels.append(q)
OUT["fsk-genisleme"] = figure(
    480, 232, panels,
    "<em>f</em>(<em>x</em>) = <em>x</em>(&#960; &#8722; <em>x</em>) fonksiyonunun [0, &#960;] üzerindeki grafiği (koyu) ile "
    "çift ve tek genişlemeleri. Çift genişleme <em>x</em> = 0'da köşe yapar; tek genişleme oradan düzgün geçer.",
    css_class=WIDE,
    aria="Even and odd extensions of the arch x times pi minus x")


# ---------------------------------------------------------------------------
for name, content in OUT.items():
    with io.open(os.path.join(OUT_DIR, "analysis3-%s.md" % name), "w", encoding="utf-8") as f:
        f.write(content)
print("generated:", ", ".join(OUT))
