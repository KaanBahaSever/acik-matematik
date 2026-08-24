# -*- coding: utf-8 -*-
"""
Raslandı Süreçleri bölümlerindeki SVG çizimlerini üretir.

Grafikler derleme sırasında ÜRETİLMEZ; bu betik çalıştırılıp çıkan SVG
doğrudan .qmd dosyalarına ömülür. Böylece kitapların derlenmesi Python
ya da Jupyter gerektirmez; CI yalnızca Quarto ile çalışır.

Kullanım:  python scripts/raslanti_grafikleri.py
Çıktı:      scripts/_grafik/fig<A..G>.md
"""
import sys, io, math, os, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8")
from svg_cizim import Plot, figur, TXT, THE, PRA, BAS, REM, fmt

HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_grafik")
os.makedirs(HERE, exist_ok=True)
CIK = {}

# ---------------------------------------------------------------- A: regresyon
X = [1, 2, 3, 4, 5]
Y = [2, 4, 5, 4, 5]
b1, b0 = 0.6, 2.2
p = Plot(58, 26, 400, 210, (0, 5.6), (0, 6))
p.izgara(ys=[1, 2, 3, 4, 5])
p.eksen([0, 1, 2, 3, 4, 5], [0, 1, 2, 3, 4, 5, 6], "X", "Y")
for x, y in zip(X, Y):
    yh = b0 + b1 * x
    p.add('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.4" stroke-dasharray="3 2.5" opacity="0.85"/>'
          % (p.X(x), p.Y(y), p.X(x), p.Y(yh), REM))
p.cizgi([(0, b0), (5.4, b0 + b1 * 5.4)], THE, 2.1)
p.nokta(list(zip(X, Y)), PRA, 4.6)
p.yazi_px(p.X(5.4) - 6, p.Y(b0 + b1 * 5.4) - 10, "&#374; = 2,2 + 0,6X", THE, 12, "end", True)
CIK["A"] = figur(500, 282, [p],
                 "Serpilme diyagram&#305;, en k&#252;&#231;&#252;k kareler do&#287;rusu ve art&#305;klar. Kesikli dikey par&#231;alar "
                 "<em>e<sub>i</sub></em> = <em>y<sub>i</sub></em> &#8722; <em>&#375;<sub>i</sub></em> hatalar&#305;d&#305;r; "
                 "EKK y&#246;ntemi bu par&#231;alar&#305;n <strong>karelerinin toplam&#305;n&#305;</strong> en k&#252;&#231;&#252;k yapar.",
                 aria="Serpilme diyagrami ve regresyon dogrusu")

# ------------------------------------------------------------- B: korelasyon
random.seed(7)


def panel(x0, veriler, baslik, renk):
    q = Plot(x0, 42, 148, 172, (-0.15, 1.15), (-0.15, 1.15))
    q.eksen([], [])
    q.nokta(veriler, renk, 4.2)
    q.yazi_px(x0 + 74, 26, baslik, TXT, 15, "middle", True)
    return q


n = 22
xs = [i / (n - 1) for i in range(n)]
poz = [(x, min(1, max(0, x + random.gauss(0, 0.09)))) for x in xs]
sif = [(x, random.random()) for x in xs]
neg = [(x, min(1, max(0, 1 - x + random.gauss(0, 0.09)))) for x in xs]
pA = panel(26, poz, "r &#8776; +0,95", PRA)
pB = panel(202, sif, "r &#8776; 0", REM)
pC = panel(378, neg, "r &#8776; &#8722;0,95", BAS)
CIK["B"] = figur(552, 236, [pA, pB, pC],
                 "Korelasyon katsay&#305;s&#305;n&#305;n i&#351;areti ili&#351;kinin <strong>y&#246;n&#252;n&#252;</strong>, mutlak de&#287;eri "
                 "<strong>&#351;iddetini</strong> verir. Ortadaki da&#287;&#305;l&#305;mda do&#287;rusal bir e&#287;ilim yoktur.",
                 sinif="ders-grafik ders-grafik-genis",
                 aria="Pozitif, sifir ve negatif korelasyon ornekleri")

# ------------------------------------------------------- C: donusturulebilir
Xd = [0, 1, 2, 3, 4]
Yd = [1.5, 2.5, 3.5, 5.0, 7.5]
c, a = 1.5799, 0.39120
p1 = Plot(52, 30, 176, 172, (-0.35, 4.4), (0, 8.4))
p1.izgara(ys=[2, 4, 6, 8])
p1.eksen([0, 1, 2, 3, 4], [0, 2, 4, 6, 8], "X", "Y")
p1.cizgi([(k / 20.0, c * math.exp(a * k / 20.0)) for k in range(0, 86)], THE, 2.0)
p1.nokta(list(zip(Xd, Yd)), PRA, 4.2)
p1.yazi_px(140, 46, "&#374; = 1,58&#183;e^(0,391X)", THE, 11, "middle", True)
p1.yazi_px(140, 238, "orijinal eksen &#8212; e&#287;ri", TXT, 11.5, "middle", True)

Ys = [math.log(v) for v in Yd]
p2 = Plot(300, 30, 176, 172, (-0.35, 4.4), (0, 2.4))
p2.izgara(ys=[0.5, 1, 1.5, 2])
p2.eksen([0, 1, 2, 3, 4], [0, 0.5, 1, 1.5, 2], "X", "Y*",
         yfmt=lambda v: ("%.1f" % v).replace(".", ","))
p2.cizgi([(-0.2, 0.45737 + a * (-0.2)), (4.3, 0.45737 + a * 4.3)], THE, 2.0)
p2.nokta(list(zip(Xd, Ys)), PRA, 4.2)
p2.yazi_px(388, 46, "Y* = 0,457 + 0,391X", THE, 11, "middle", True)
p2.yazi_px(388, 238, "Y* = ln Y ekseni &#8212; do&#287;ru", TXT, 11.5, "middle", True)
CIK["C"] = figur(500, 254, [p1, p2],
                 "Ayn&#305; be&#351; g&#246;zlem. Solda orijinal eksende e&#287;ri, sa&#287;da <em>Y*</em> = ln <em>Y</em> "
                 "ekseninde do&#287;ru. D&#246;n&#252;&#351;&#252;m&#252;n tek amac&#305; sa&#287;daki resmi elde etmektir; en k&#252;&#231;&#252;k kareler "
                 "orada uygulan&#305;r.",
                 aria="Ustel modelin logaritma ile dogrusallastirilmasi")

# -------------------------------------------------------------- D: otokorelasyon
T = [0, 1, 2, 3, 4]
Yt = [10, 12, 15, 14, 17]
Ybar = 13.6
p1 = Plot(52, 28, 176, 168, (-0.3, 4.3), (8, 18.5))
p1.izgara(ys=[10, 12, 14, 16, 18])
p1.eksen([0, 1, 2, 3, 4], [10, 12, 14, 16, 18], "t", "Y")
p1.cizgi([(-0.3, Ybar), (4.3, Ybar)], BAS, 1.5, "5 4")
p1.cizgi(list(zip(T, Yt)), THE, 2.0)
p1.nokta(list(zip(T, Yt)), PRA, 4.2)
p1.yazi_px(232, p1.Y(Ybar) - 5, "&#562; = 13,6", BAS, 10.5, "end")
p1.yazi_px(140, 234, "seri: Y&#8348;", TXT, 11.5, "middle", True)

lag = [(Yt[i - 1], Yt[i]) for i in range(1, 5)]
p2 = Plot(300, 28, 176, 168, (8.5, 18), (8.5, 18))
p2.izgara(xs=[10, 12, 14, 16], ys=[10, 12, 14, 16])
p2.eksen([10, 12, 14, 16], [10, 12, 14, 16], "Y&#8348;&#8331;&#8321;", "Y&#8348;")
p2.cizgi([(8.5, Ybar), (18, Ybar)], BAS, 1.1, "4 3", 0.6)
p2.add('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.1" stroke-dasharray="4 3" opacity="0.6"/>'
       % (p2.X(Ybar), p2.y0, p2.X(Ybar), p2.y0 + p2.h, BAS))
p2.nokta(lag, PRA, 4.4)
for (xx, yy) in lag:
    p2.yazi_px(p2.X(xx) + 7, p2.Y(yy) + 4, "(%s, %s)" % (fmt(xx), fmt(yy)), TXT, 9.5)
p2.yazi_px(388, 234, "gecikme diyagram&#305; (k = 1)", TXT, 11.5, "middle", True)
CIK["D"] = figur(500, 252, [p1, p2],
                 "Solda serinin kendisi, sa&#287;da her noktan&#305;n bir &#246;nceki de&#287;erine kar&#351;&#305; &#231;izimi. "
                 "Noktalar sol-alt ve sa&#287;-&#252;st &#231;eyreklere toplansayd&#305; <em>r</em><sub>1</sub> g&#252;&#231;l&#252; pozitif "
                 "olurdu; burada &#231;eyreklere da&#287;&#305;ld&#305;klar&#305; i&#231;in <em>r</em><sub>1</sub> = 0,186 gibi zay&#305;f bir de&#287;er &#231;&#305;kar.",
                 aria="Zaman serisi ve gecikme diyagrami")

# ------------------------------------------------------- E: hareketli ortalamalar
Th = [1, 2, 3, 4, 5]
Yh = [10, 14, 21, 29, 34]
mu = {3: 15.0, 4: 64 / 3.0, 5: 28.0}
a5, b5 = 34.5556, 6.5556
p = Plot(56, 26, 404, 208, (0.5, 7.6), (5, 52))
p.izgara(ys=[10, 20, 30, 40, 50])
p.eksen([1, 2, 3, 4, 5, 6, 7], [10, 20, 30, 40, 50], "t", "Y")
p.cizgi(list(zip(Th, Yh)), THE, 2.1)
p.nokta(list(zip(Th, Yh)), THE, 4.4)
p.cizgi([(k, v) for k, v in sorted(mu.items())], BAS, 2.0, "6 4")
p.bosnokta([(k, v) for k, v in sorted(mu.items())], BAS, 4.0)
p.cizgi([(5, a5), (7, a5 + 2 * b5)], PRA, 2.1)
p.nokta([(6, a5 + b5), (7, a5 + 2 * b5)], PRA, 4.4)
p.bosnokta([(5, a5)], PRA, 4.0)
p.dikey(6, 5, a5 + b5, PRA, "3 3", 0.35)
p.dikey(7, 5, a5 + 2 * b5, PRA, "3 3", 0.35)
p.yazi_px(p.X(5) + 6, p.Y(34) - 8, "Y&#8348;", THE, 11.5, "start", True)
p.yazi_px(p.X(5) + 6, p.Y(28) + 16, "&#956;&#8348; (tek katl&#305;)", BAS, 11.5, "start", True)
p.yazi_px(p.X(7) - 4, p.Y(a5 + 2 * b5) - 10, "a&#8325; + p&#183;b&#8325;", PRA, 11.5, "end", True)
p.yazi_px(p.X(6), p.Y(41.11) + 18, "41,1", PRA, 10.5, "middle")
p.yazi_px(p.X(7), p.Y(47.67) + 18, "47,7", PRA, 10.5, "middle")
CIK["E"] = figur(500, 282, [p],
                 "Trendli bir seride tek katl&#305; hareketli ortalama (kesikli) veriyi <strong>geriden takip eder</strong>. "
                 "&#304;ki katl&#305; y&#246;ntem bu gecikmeyi <em>a</em><sub>5</sub> ve <em>b</em><sub>5</sub> katsay&#305;lar&#305;yla "
                 "d&#252;zeltip tahmini trendin &#252;st&#252;ne oturtur.",
                 aria="Tek katli ve iki katli hareketli ortalama karsilastirmasi")


# ------------------------------------------------------------- F: tabii model
def mini(x0, seri, baslik, tahmin=None):
    m = len(seri)
    ymin, ymax = min(seri), max(seri)
    pad = (ymax - ymin) * 0.25 + 1
    q = Plot(x0, 34, 96, 96, (0.4, m + 1.2), (ymin - pad, ymax + pad))
    q.eksen([], [])
    q.cizgi(list(zip(range(1, m + 1), seri)), THE, 1.8)
    q.nokta(list(zip(range(1, m + 1), seri)), THE, 2.8)
    if tahmin is not None:
        q.cizgi([(m, seri[-1]), (m + 1, tahmin)], PRA, 1.8, "4 3")
        q.nokta([(m + 1, tahmin)], PRA, 3.4)
    q.yazi_px(x0 + 48, 24, baslik, TXT, 11.5, "middle", True)
    return q


f1 = mini(34, [10, 15, 14, 13, 14], "sabit", 14)
f2 = mini(154, [6, 8, 11, 13, 15], "trend", 17)
f3 = mini(274, [10, 50, 40, 15, 10, 50, 40, 15], "mevsimsel", 10)
f4 = mini(394, [10, 20, 15, 17, 18, 29, 21, 22, 25, 30, 33, 34], "trend + mevsimsel", 28)
CIK["F"] = figur(500, 152, [f1, f2, f3, f4],
                 "Tabii modelin d&#246;rt h&#226;li. Kesikli k&#305;rm&#305;z&#305; par&#231;a, her durumda bir sonraki periyot i&#231;in "
                 "yap&#305;lan tahmindir; hangi form&#252;l&#252;n kullan&#305;laca&#287;&#305;n&#305; serinin &#351;ekli belirler.",
                 aria="Tabii modelin dort hali")


# ------------------------------------------------------------------ G: Poisson
def pois(k, m):
    return math.exp(-m) * m ** k / math.factorial(k)


p = Plot(56, 26, 404, 190, (-0.6, 16.6), (0, 0.30))
p.izgara(ys=[0.05, 0.10, 0.15, 0.20, 0.25])
p.eksen(list(range(0, 17, 2)), [0, 0.05, 0.10, 0.15, 0.20, 0.25],
        "n", "P{Y&#8348; = n}", yfmt=lambda v: ("%.2f" % v).replace(".", ","))
for m, renk, dx in ((2, BAS, -3.6), (4, THE, 0.0), (8, PRA, 3.6)):
    for k in range(0, 17):
        v = pois(k, m)
        if v < 0.0015:
            continue
        Xp, Y0, Y1 = p.X(k) + dx, p.Y(0), p.Y(v)
        p.add('<rect x="%.1f" y="%.1f" width="3.4" height="%.1f" fill="%s" opacity="0.9" rx="1"/>'
              % (Xp - 1.7, Y1, Y0 - Y1, renk))
p.yazi_px(362, 52, "&#955;t = 2", BAS, 12, "start", True)
p.yazi_px(362, 70, "&#955;t = 4", THE, 12, "start", True)
p.yazi_px(362, 88, "&#955;t = 8", PRA, 12, "start", True)
CIK["G"] = figur(500, 254, [p],
                 "Poisson olas&#305;l&#305;klar&#305;n&#305;n <em>&#955;t</em> ile de&#287;i&#351;imi. Ortalama b&#252;y&#252;d&#252;k&#231;e da&#287;&#305;l&#305;m&#305;n tepesi sa&#287;a "
                 "kayar ve yayvanla&#351;&#305;r; <em>&#955;t</em> = 2 gibi k&#252;&#231;&#252;k de&#287;erlerde da&#287;&#305;l&#305;m belirgin bi&#231;imde &#231;arp&#305;kt&#305;r.",
                 aria="Farkli lambda-t degerleri icin Poisson olasiliklari")

for ad, icerik in CIK.items():
    with io.open(os.path.join(HERE, "fig%s.md" % ad), "w", encoding="utf-8") as f:
        f.write(icerik)
print("uretildi:", ", ".join(sorted(CIK)))
