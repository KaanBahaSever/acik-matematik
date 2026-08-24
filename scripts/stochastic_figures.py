# -*- coding: utf-8 -*-
"""
Generates the SVG figures used in the "Raslantı Süreçleri" (Stochastic
Processes) chapters.

The figures are NOT produced at build time: run this script and paste the
resulting markup straight into the .qmd files. Building the books therefore
needs neither Python nor Jupyter; CI runs Quarto alone.

The captions are Turkish on purpose — they are the text shown on the site.

Usage:   python scripts/stochastic_figures.py
Output:  scripts/_figures/fig<A..G>.md
"""
import io
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8")
from svg_plot import Plot, figure, TEXT, THEORY, PRACTICE, BASE, REMARK, fmt  # noqa: E402

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_figures")
os.makedirs(OUT_DIR, exist_ok=True)
OUT = {}

# ---------------------------------------------------------------- A: regression
X = [1, 2, 3, 4, 5]
Y = [2, 4, 5, 4, 5]
b1, b0 = 0.6, 2.2
p = Plot(58, 26, 400, 210, (0, 5.6), (0, 6))
p.grid(ys=[1, 2, 3, 4, 5])
p.axes([0, 1, 2, 3, 4, 5], [0, 1, 2, 3, 4, 5, 6], "X", "Y")
for x, y in zip(X, Y):
    yh = b0 + b1 * x
    p.add('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.4" stroke-dasharray="3 2.5" opacity="0.85"/>'
          % (p.X(x), p.Y(y), p.X(x), p.Y(yh), REMARK))
p.line([(0, b0), (5.4, b0 + b1 * 5.4)], THEORY, 2.1)
p.points(list(zip(X, Y)), PRACTICE, 4.6)
p.text_px(p.X(5.4) - 6, p.Y(b0 + b1 * 5.4) - 10, "&#374; = 2,2 + 0,6X", THEORY, 12, "end", True)
OUT["A"] = figure(500, 282, [p],
                  "Serpilme diyagram&#305;, en k&#252;&#231;&#252;k kareler do&#287;rusu ve art&#305;klar. Kesikli dikey par&#231;alar "
                  "<em>e<sub>i</sub></em> = <em>y<sub>i</sub></em> &#8722; <em>&#375;<sub>i</sub></em> hatalar&#305;d&#305;r; "
                  "EKK y&#246;ntemi bu par&#231;alar&#305;n <strong>karelerinin toplam&#305;n&#305;</strong> en k&#252;&#231;&#252;k yapar.",
                  aria="Serpilme diyagrami ve regresyon dogrusu")

# ------------------------------------------------------------- B: correlation
random.seed(7)


def panel(x0, data, title, color):
    q = Plot(x0, 42, 148, 172, (-0.15, 1.15), (-0.15, 1.15))
    q.axes([], [])
    q.points(data, color, 4.2)
    q.text_px(x0 + 74, 26, title, TEXT, 15, "middle", True)
    return q


n = 22
xs = [i / (n - 1) for i in range(n)]
pos = [(x, min(1, max(0, x + random.gauss(0, 0.09)))) for x in xs]
zero = [(x, random.random()) for x in xs]
neg = [(x, min(1, max(0, 1 - x + random.gauss(0, 0.09)))) for x in xs]
pA = panel(26, pos, "r &#8776; +0,95", PRACTICE)
pB = panel(202, zero, "r &#8776; 0", REMARK)
pC = panel(378, neg, "r &#8776; &#8722;0,95", BASE)
OUT["B"] = figure(552, 236, [pA, pB, pC],
                  "Korelasyon katsay&#305;s&#305;n&#305;n i&#351;areti ili&#351;kinin <strong>y&#246;n&#252;n&#252;</strong>, mutlak de&#287;eri "
                  "<strong>&#351;iddetini</strong> verir. Ortadaki da&#287;&#305;l&#305;mda do&#287;rusal bir e&#287;ilim yoktur.",
                  css_class="ders-grafik ders-grafik-genis",
                  aria="Pozitif, sifir ve negatif korelasyon ornekleri")

# ------------------------------------------------------- C: linearizable model
Xd = [0, 1, 2, 3, 4]
Yd = [1.5, 2.5, 3.5, 5.0, 7.5]
c, a = 1.5799, 0.39120
p1 = Plot(52, 30, 176, 172, (-0.35, 4.4), (0, 8.4))
p1.grid(ys=[2, 4, 6, 8])
p1.axes([0, 1, 2, 3, 4], [0, 2, 4, 6, 8], "X", "Y")
p1.line([(k / 20.0, c * math.exp(a * k / 20.0)) for k in range(0, 86)], THEORY, 2.0)
p1.points(list(zip(Xd, Yd)), PRACTICE, 4.2)
p1.text_px(140, 46, "&#374; = 1,58&#183;e^(0,391X)", THEORY, 11, "middle", True)
p1.text_px(140, 238, "orijinal eksen &#8212; e&#287;ri", TEXT, 11.5, "middle", True)

Ys = [math.log(v) for v in Yd]
p2 = Plot(300, 30, 176, 172, (-0.35, 4.4), (0, 2.4))
p2.grid(ys=[0.5, 1, 1.5, 2])
p2.axes([0, 1, 2, 3, 4], [0, 0.5, 1, 1.5, 2], "X", "Y*",
        yfmt=lambda v: ("%.1f" % v).replace(".", ","))
p2.line([(-0.2, 0.45737 + a * (-0.2)), (4.3, 0.45737 + a * 4.3)], THEORY, 2.0)
p2.points(list(zip(Xd, Ys)), PRACTICE, 4.2)
p2.text_px(388, 46, "Y* = 0,457 + 0,391X", THEORY, 11, "middle", True)
p2.text_px(388, 238, "Y* = ln Y ekseni &#8212; do&#287;ru", TEXT, 11.5, "middle", True)
OUT["C"] = figure(500, 254, [p1, p2],
                  "Ayn&#305; be&#351; g&#246;zlem. Solda orijinal eksende e&#287;ri, sa&#287;da <em>Y*</em> = ln <em>Y</em> "
                  "ekseninde do&#287;ru. D&#246;n&#252;&#351;&#252;m&#252;n tek amac&#305; sa&#287;daki resmi elde etmektir; en k&#252;&#231;&#252;k kareler "
                  "orada uygulan&#305;r.",
                  aria="Ustel modelin logaritma ile dogrusallastirilmasi")

# -------------------------------------------------------------- D: autocorrelation
T = [0, 1, 2, 3, 4]
Yt = [10, 12, 15, 14, 17]
Ybar = 13.6
p1 = Plot(52, 28, 176, 168, (-0.3, 4.3), (8, 18.5))
p1.grid(ys=[10, 12, 14, 16, 18])
p1.axes([0, 1, 2, 3, 4], [10, 12, 14, 16, 18], "t", "Y")
p1.line([(-0.3, Ybar), (4.3, Ybar)], BASE, 1.5, "5 4")
p1.line(list(zip(T, Yt)), THEORY, 2.0)
p1.points(list(zip(T, Yt)), PRACTICE, 4.2)
p1.text_px(232, p1.Y(Ybar) - 5, "&#562; = 13,6", BASE, 10.5, "end")
p1.text_px(140, 234, "seri: Y&#8348;", TEXT, 11.5, "middle", True)

lag = [(Yt[i - 1], Yt[i]) for i in range(1, 5)]
p2 = Plot(300, 28, 176, 168, (8.5, 18), (8.5, 18))
p2.grid(xs=[10, 12, 14, 16], ys=[10, 12, 14, 16])
p2.axes([10, 12, 14, 16], [10, 12, 14, 16], "Y&#8348;&#8331;&#8321;", "Y&#8348;")
p2.line([(8.5, Ybar), (18, Ybar)], BASE, 1.1, "4 3", 0.6)
p2.add('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.1" stroke-dasharray="4 3" opacity="0.6"/>'
       % (p2.X(Ybar), p2.y0, p2.X(Ybar), p2.y0 + p2.h, BASE))
p2.points(lag, PRACTICE, 4.4)
for (xx, yy) in lag:
    p2.text_px(p2.X(xx) + 7, p2.Y(yy) + 4, "(%s, %s)" % (fmt(xx), fmt(yy)), TEXT, 9.5)
p2.text_px(388, 234, "gecikme diyagram&#305; (k = 1)", TEXT, 11.5, "middle", True)
OUT["D"] = figure(500, 252, [p1, p2],
                  "Solda serinin kendisi, sa&#287;da her noktan&#305;n bir &#246;nceki de&#287;erine kar&#351;&#305; &#231;izimi. "
                  "Noktalar sol-alt ve sa&#287;-&#252;st &#231;eyreklere toplansayd&#305; <em>r</em><sub>1</sub> g&#252;&#231;l&#252; pozitif "
                  "olurdu; burada &#231;eyreklere da&#287;&#305;ld&#305;klar&#305; i&#231;in <em>r</em><sub>1</sub> = 0,186 gibi zay&#305;f bir de&#287;er &#231;&#305;kar.",
                  aria="Zaman serisi ve gecikme diyagrami")

# ------------------------------------------------------- E: moving averages
Th = [1, 2, 3, 4, 5]
Yh = [10, 14, 21, 29, 34]
mu = {3: 15.0, 4: 64 / 3.0, 5: 28.0}
a5, b5 = 34.5556, 6.5556
p = Plot(56, 26, 404, 208, (0.5, 7.6), (5, 52))
p.grid(ys=[10, 20, 30, 40, 50])
p.axes([1, 2, 3, 4, 5, 6, 7], [10, 20, 30, 40, 50], "t", "Y")
p.line(list(zip(Th, Yh)), THEORY, 2.1)
p.points(list(zip(Th, Yh)), THEORY, 4.4)
p.line([(k, v) for k, v in sorted(mu.items())], BASE, 2.0, "6 4")
p.hollow_points([(k, v) for k, v in sorted(mu.items())], BASE, 4.0)
p.line([(5, a5), (7, a5 + 2 * b5)], PRACTICE, 2.1)
p.points([(6, a5 + b5), (7, a5 + 2 * b5)], PRACTICE, 4.4)
p.hollow_points([(5, a5)], PRACTICE, 4.0)
p.vline(6, 5, a5 + b5, PRACTICE, "3 3", 0.35)
p.vline(7, 5, a5 + 2 * b5, PRACTICE, "3 3", 0.35)
p.text_px(p.X(5) + 6, p.Y(34) - 8, "Y&#8348;", THEORY, 11.5, "start", True)
p.text_px(p.X(5) + 6, p.Y(28) + 16, "&#956;&#8348; (tek katl&#305;)", BASE, 11.5, "start", True)
p.text_px(p.X(7) - 4, p.Y(a5 + 2 * b5) - 10, "a&#8325; + p&#183;b&#8325;", PRACTICE, 11.5, "end", True)
p.text_px(p.X(6), p.Y(41.11) + 18, "41,1", PRACTICE, 10.5, "middle")
p.text_px(p.X(7), p.Y(47.67) + 18, "47,7", PRACTICE, 10.5, "middle")
OUT["E"] = figure(500, 282, [p],
                  "Trendli bir seride tek katl&#305; hareketli ortalama (kesikli) veriyi <strong>geriden takip eder</strong>. "
                  "&#304;ki katl&#305; y&#246;ntem bu gecikmeyi <em>a</em><sub>5</sub> ve <em>b</em><sub>5</sub> katsay&#305;lar&#305;yla "
                  "d&#252;zeltip tahmini trendin &#252;st&#252;ne oturtur.",
                  aria="Tek katli ve iki katli hareketli ortalama karsilastirmasi")


# ------------------------------------------------------------- F: naive model
def mini(x0, series, title, forecast=None):
    m = len(series)
    ymin, ymax = min(series), max(series)
    pad = (ymax - ymin) * 0.25 + 1
    q = Plot(x0, 34, 96, 96, (0.4, m + 1.2), (ymin - pad, ymax + pad))
    q.axes([], [])
    q.line(list(zip(range(1, m + 1), series)), THEORY, 1.8)
    q.points(list(zip(range(1, m + 1), series)), THEORY, 2.8)
    if forecast is not None:
        q.line([(m, series[-1]), (m + 1, forecast)], PRACTICE, 1.8, "4 3")
        q.points([(m + 1, forecast)], PRACTICE, 3.4)
    q.text_px(x0 + 48, 24, title, TEXT, 11.5, "middle", True)
    return q


f1 = mini(34, [10, 15, 14, 13, 14], "sabit", 14)
f2 = mini(154, [6, 8, 11, 13, 15], "trend", 17)
f3 = mini(274, [10, 50, 40, 15, 10, 50, 40, 15], "mevsimsel", 10)
f4 = mini(394, [10, 20, 15, 17, 18, 29, 21, 22, 25, 30, 33, 34], "trend + mevsimsel", 28)
OUT["F"] = figure(500, 152, [f1, f2, f3, f4],
                  "Tabii modelin d&#246;rt h&#226;li. Kesikli k&#305;rm&#305;z&#305; par&#231;a, her durumda bir sonraki periyot i&#231;in "
                  "yap&#305;lan tahmindir; hangi form&#252;l&#252;n kullan&#305;laca&#287;&#305;n&#305; serinin &#351;ekli belirler.",
                  aria="Tabii modelin dort hali")


# ------------------------------------------------------------------ G: Poisson
def poisson_pmf(k, m):
    return math.exp(-m) * m ** k / math.factorial(k)


p = Plot(56, 26, 404, 190, (-0.6, 16.6), (0, 0.30))
p.grid(ys=[0.05, 0.10, 0.15, 0.20, 0.25])
p.axes(list(range(0, 17, 2)), [0, 0.05, 0.10, 0.15, 0.20, 0.25],
       "n", "P{Y&#8348; = n}", yfmt=lambda v: ("%.2f" % v).replace(".", ","))
for m, color, dx in ((2, BASE, -3.6), (4, THEORY, 0.0), (8, PRACTICE, 3.6)):
    for k in range(0, 17):
        v = poisson_pmf(k, m)
        if v < 0.0015:
            continue
        Xp, Y0, Y1 = p.X(k) + dx, p.Y(0), p.Y(v)
        p.add('<rect x="%.1f" y="%.1f" width="3.4" height="%.1f" fill="%s" opacity="0.9" rx="1"/>'
              % (Xp - 1.7, Y1, Y0 - Y1, color))
p.text_px(362, 52, "&#955;t = 2", BASE, 12, "start", True)
p.text_px(362, 70, "&#955;t = 4", THEORY, 12, "start", True)
p.text_px(362, 88, "&#955;t = 8", PRACTICE, 12, "start", True)
OUT["G"] = figure(500, 254, [p],
                  "Poisson olas&#305;l&#305;klar&#305;n&#305;n <em>&#955;t</em> ile de&#287;i&#351;imi. Ortalama b&#252;y&#252;d&#252;k&#231;e da&#287;&#305;l&#305;m&#305;n tepesi sa&#287;a "
                  "kayar ve yayvanla&#351;&#305;r; <em>&#955;t</em> = 2 gibi k&#252;&#231;&#252;k de&#287;erlerde da&#287;&#305;l&#305;m belirgin bi&#231;imde &#231;arp&#305;kt&#305;r.",
                  aria="Farkli lambda-t degerleri icin Poisson olasiliklari")

for name, content in OUT.items():
    with io.open(os.path.join(OUT_DIR, "fig%s.md" % name), "w", encoding="utf-8") as f:
        f.write(content)
print("generated:", ", ".join(sorted(OUT)))
