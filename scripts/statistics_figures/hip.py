# -*- coding: utf-8 -*-
"""
Figures of the chapter "Hipotez Testlerine Giriş"
(dersler/matematiksel-istatistik/hipotez-testlerine-giris.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box: a figure that illustrates a
definition sits directly below that box. The figures are NOT produced at
build time. Run

    python scripts/statistics_figures/hip.py
    python scripts/center_figures.py "statistics-hip-*.md" --keep-width
    python scripts/check_figure_labels.py "scripts/_figures/statistics-hip-*.md"

and paste the markup of scripts/_figures/statistics-hip-<name>.md into the
.qmd. Captions are Turkish on purpose (they are shown on the site); aria
labels are plain ASCII.
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, WIDE, TEXT, THEORY, PRACTICE, BASE, REMARK  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "statistics-hip-"

MINUS, MU, ALPHA, BETA, PI_S, APPROX = "&#8722;", "&#956;", "&#945;", "&#946;", "&#960;", "&#8776;"
SUB0, SUB1 = "&#8320;", "&#8321;"
LABEL = 13
TICK = 11
SAMPLES = 400


def num(v, digits=None):
    """Decimal comma and a real minus sign: -1.645 -> '&#8722;1,645'."""
    s = f"{v:.4f}".rstrip("0").rstrip(".") if digits is None else f"{v:.{digits}f}"
    if s in ("-0", ""):
        s = "0"
    return s.replace("-", MINUS).replace(".", ",")


def it(s):
    return f'<tspan font-style="italic">{s}</tspan>'


def sub(s):
    return f'<tspan font-size="10" dy="3">{s}</tspan><tspan dy="-3">&#8203;</tspan>'


def pdf(x, mu=0.0, s=1.0):
    return math.exp(-0.5 * ((x - mu) / s) ** 2) / (s * math.sqrt(2 * math.pi))


def ncdf(z):
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))


def curve(f, a, b, n=SAMPLES):
    return [(a + (b - a) * k / n, f(a + (b - a) * k / n)) for k in range(n + 1)]


def shade(p, f, a, b, color=PRACTICE, opacity=0.32):
    p.polygon([(a, 0)] + curve(f, a, b, 240) + [(b, 0)], color, opacity)


def x_axis(p, ticks, name=""):
    """Horizontal axis at y = 0 with an arrow head; ticks are (value, label)."""
    Y = p.Y(0)
    left, right = p.x0 - 4, p.x0 + p.w + 10
    p.add(f'<g stroke="{TEXT}" stroke-width="1.1" opacity="0.5" fill="{TEXT}">'
          f'<line x1="{left:.1f}" y1="{Y:.1f}" x2="{right:.1f}" y2="{Y:.1f}"/>'
          f'<polygon points="{right:.1f},{Y:.1f} {right-8:.1f},{Y-3.5:.1f} {right-8:.1f},{Y+3.5:.1f}" stroke="none"/></g>')
    for v, lab in ticks:
        X = p.X(v)
        p.add(f'<line x1="{X:.1f}" y1="{Y-3:.1f}" x2="{X:.1f}" y2="{Y+3:.1f}" stroke="{TEXT}" stroke-width="1" opacity="0.7"/>')
        if lab:
            p.add(f'<text x="{X:.1f}" y="{Y+16:.1f}" fill="{TEXT}" font-size="{TICK}" text-anchor="middle" opacity="0.8">{lab}</text>')
    if name:
        p.add(f'<text x="{right+4:.1f}" y="{Y+4:.1f}" fill="{TEXT}" font-size="13" font-style="italic" opacity="0.85">{name}</text>')


def leader(p, x0, y0, x1, y1, color=PRACTICE):
    p.add(f'<line x1="{p.X(x0):.1f}" y1="{p.Y(y0):.1f}" x2="{p.X(x1):.1f}" y2="{p.Y(y1):.1f}" '
          f'stroke="{color}" stroke-width="1" opacity="0.8"/>')


def save(name, svg):
    (OUT_DIR / f"{PREFIX}{name}.md").write_text(svg, encoding="utf-8", newline="\n")


# ============================================================
# alfa-beta: H0 mu = 50 against H1 mu = 52, sd of the mean 1, reject if xbar > 51.5
# ============================================================
def fig_alpha_beta():
    C = 51.5
    X0, X1 = 46.3, 55.7
    h0 = lambda x: pdf(x, 50, 1)   # noqa: E731
    h1 = lambda x: pdf(x, 52, 1)   # noqa: E731
    p = Plot(40, 44, 500, 200, (X0, X1), (0, 0.43))
    shade(p, h1, X0, C, PRACTICE, 0.26)      # beta
    shade(p, h0, C, X1, THEORY, 0.40)        # alpha
    p.line(curve(h0, X0, X1), THEORY, 2.2)
    p.line(curve(h1, X0, X1), PRACTICE, 2.2, dash="7 4")
    ticks = [(k, num(k)) for k in range(47, 56)]
    x_axis(p, ticks, "x&#772;")
    p.vline(C, 0, 0.425, TEXT, "4 3", 0.75)
    p.label(C, 0, "c = 51,5", dy=33, anchor="middle", size=12.5, bold=True)
    # curve names
    p.label(48.2, h0(48.2), f"H{SUB0}: {MU} = 50", dx=-8, dy=-6, anchor="end", color=THEORY, size=LABEL)
    p.label(53.8, h1(53.8), f"H{SUB1}: {MU} = 52", dx=8, dy=-6, color=PRACTICE, size=LABEL)
    # area names with leader lines
    leader(p, 54.3, 0.235, 52.15, 0.035, THEORY)
    p.label(54.3, 0.235, f"{ALPHA} {APPROX} 0,0668", dy=-5, anchor="middle", color=THEORY, size=LABEL, bold=True)
    leader(p, 47.6, 0.235, 50.8, 0.05, PRACTICE)
    p.label(47.6, 0.235, f"{BETA} {APPROX} 0,3085", dy=-5, anchor="middle", color=PRACTICE, size=LABEL, bold=True)
    # region names above the panel
    p.text_px(p.X((X0 + C) / 2), 34, "kabul bölgesi", anchor="middle", size=LABEL)
    p.text_px(p.X((C + X1) / 2), 34, "ret bölgesi", anchor="middle", size=LABEL)
    save("alfa-beta", figure(
        580, 290, [p],
        "Düz mavi eğri H₀ doğruyken (μ = 50), kesikli turuncu eğri μ = 52 iken X̄'nin dağılımı. "
        "c = 51,5'in sağındaki koyu mavi alan I. tip hata olasılığı α, solundaki turuncu alan "
        "II. tip hata olasılığı β'dır.",
        aria="Two normal curves for the sample mean, the alpha area to the right of c under H0 and the beta area to the left of c under H1"))


# ============================================================
# kritik-bolgeler: the three alternatives on the z scale
# ============================================================
def fig_critical_regions():
    X0, X1 = -3.4, 3.4
    zc1, zc2 = 1.645, 1.96
    panels = []
    specs = [
        (f"H{SUB1}: {MU} &gt; {MU}{SUB0}", [(zc1, X1)], [(zc1, f"z{sub('1' + MINUS + ALPHA)}")],
         [(2.45, 0.16, 2.25, 0.03, ALPHA)]),
        (f"H{SUB1}: {MU} &lt; {MU}{SUB0}", [(X0, -zc1)], [(-zc1, f"{MINUS}z{sub('1' + MINUS + ALPHA)}")],
         [(-2.45, 0.16, -2.25, 0.03, ALPHA)]),
        (f"H{SUB1}: {MU} &#8800; {MU}{SUB0}", [(X0, -zc2), (zc2, X1)],
         [(-zc2, f"{MINUS}z{sub('1' + MINUS + ALPHA + '/2')}"), (zc2, f"z{sub('1' + MINUS + ALPHA + '/2')}")],
         [(-2.55, 0.16, -2.4, 0.02, f"{ALPHA}/2"), (2.55, 0.16, 2.4, 0.02, f"{ALPHA}/2")]),
    ]
    for i, (title, regions, crit, areas) in enumerate(specs):
        p = Plot(20 + i * 232, 40, 205, 130, (X0, X1), (0, 0.42))
        for a, b in regions:
            shade(p, pdf, a, b, PRACTICE, 0.40)
        p.line(curve(pdf, X0, X1), THEORY, 2.0)
        x_axis(p, [(0, "0")] + [(z, "") for z, _ in crit])
        for z, lab in crit:
            p.vline(z, 0, pdf(z), PRACTICE, "4 3", 0.85)
            p.label(z, 0, lab, dy=18, anchor="middle", size=12.5)
        for lx, ly, tx, ty, s in areas:
            leader(p, lx, ly, tx, ty)
            p.label(lx, ly, s, dy=-5, anchor="middle", color=PRACTICE, size=LABEL, bold=True)
        p.text_px(p.x0 + p.w / 2, 22, title, anchor="middle", size=LABEL)
        panels.append(p)
    save("kritik-bolgeler", figure(
        720, 220, panels,
        "Z istatistiğinin ölçeğinde üç karşı hipotezin ret bölgeleri (turuncu). Tek yönlü testlerde "
        "α bütünüyle karşı hipotezin gösterdiği kuyruğa konur; iki yönlü testte iki kuyruğa α/2'şer bölünür.",
        css_class=WIDE,
        aria="Three standard normal curves with the rejection region of the right-sided, left-sided and two-sided z test shaded"))


# ============================================================
# guc-fonksiyonu: power of the two-sided test, mu0 = 50, sigma = 4, alpha = 0.05
# ============================================================
def power2(mu, n, mu0=50.0, s=4.0, z=1.96):
    d = (mu - mu0) * math.sqrt(n) / s
    return ncdf(-z - d) + 1 - ncdf(z - d)


def fig_power():
    X0, X1 = 46.0, 54.0
    p = Plot(60, 30, 470, 220, (X0, X1), (0, 1.0))
    p.grid(xs=range(46, 55), ys=(0.25, 0.5, 0.75, 1.0))
    p.axes(range(46, 55), (0, 0.25, 0.5, 0.75, 1.0), xlabel=MU, ylabel=f"{PI_S}({MU})",
           xfmt=lambda v: num(v), yfmt=lambda v: num(v))
    p.line([(X0, 0.05), (X1, 0.05)], REMARK, 1.3, dash="5 4")
    p.label(47.0, 0.05, f"{ALPHA} = 0,05", dy=-6, anchor="middle", color=REMARK, size=12)
    p.line(curve(lambda m: power2(m, 16), X0, X1), THEORY, 2.3)
    p.line(curve(lambda m: power2(m, 64), X0, X1), PRACTICE, 2.3, dash="7 4")
    pts = [(52, power2(52, 16)), (53, power2(53, 16))]
    p.points(pts, THEORY, 4.2)
    p.label(52, pts[0][1], "0,516", dx=9, dy=5, color=THEORY, size=12.5, bold=True)
    p.label(53, pts[1][1], "0,851", dx=9, dy=6, color=THEORY, size=12.5, bold=True)
    # legend in the empty middle top
    lx, ly = 48.55, 0.92
    p.line([(lx, ly), (lx + 0.45, ly)], THEORY, 2.3)
    p.label(lx + 0.55, ly, "n = 16", dy=4, size=12.5)
    p.line([(lx, ly - 0.1), (lx + 0.45, ly - 0.1)], PRACTICE, 2.3, dash="7 4")
    p.label(lx + 0.55, ly - 0.1, "n = 64", dy=4, size=12.5)
    save("guc-fonksiyonu", figure(
        580, 290, [p],
        "H₀: μ = 50 hipotezinin iki yönlü testi için güç fonksiyonu (σ = 4, α = 0,05). "
        "Eğri μ = 50'de en düşük değeri α'yı alır ve μ, 50'den uzaklaştıkça 1'e yaklaşır; "
        "örneklem büyüdükçe (n = 64) daha dik yükselir.",
        aria="Power function of the two-sided z test for n = 16 and n = 64, minimum 0.05 at mu = 50"))


# ============================================================
# p-degeri-tek-yonlu: observed z = -1.9, left-sided test
# ============================================================
def fig_p_one_sided():
    X0, X1 = -3.6, 3.6
    Z, ZC = -1.9, -1.645
    p = Plot(40, 26, 480, 180, (X0, X1), (0, 0.42))
    shade(p, pdf, X0, Z, PRACTICE, 0.42)
    p.line(curve(pdf, X0, X1), THEORY, 2.1)
    ints = [k for k in range(-3, 4) if abs(k - Z) > 0.5 and abs(k - ZC) > 0.5]
    x_axis(p, [(k, num(k)) for k in ints] + [(Z, ""), (ZC, "")], it("z"))
    p.vline(Z, 0, pdf(Z), PRACTICE, None, 0.9)
    p.label(Z, 0, "&#8722;1,9", dy=17, anchor="middle", color=PRACTICE, size=12.5, bold=True)
    p.vline(ZC, 0, 0.33, REMARK, "4 3", 0.9)
    p.label(ZC, 0.33, "&#8722;1,645", dy=-6, anchor="middle", color=REMARK, size=12)
    leader(p, -2.9, 0.17, -2.2, 0.02)
    p.label(-2.9, 0.17, f"p {APPROX} 0,0287", dy=-5, anchor="middle", color=PRACTICE, size=LABEL, bold=True)
    p.label(1.9, pdf(1.9), "N(0, 1)", dx=10, dy=-8, color=THEORY, size=LABEL)
    save("p-degeri-tek-yonlu", figure(
        560, 250, [p],
        "Sola yönlü testte gözlenen z = −1,9 için p değeri, eğrinin altında −1,9'un solunda kalan "
        "alandır (turuncu). Kesikli çizgi α = 0,05 düzeyindeki kritik değer −1,645'tir; gözlenen "
        "değer onun solunda kaldığından p < 0,05'tir.",
        aria="Standard normal curve with the left tail below -1.9 shaded as the p value and the critical value -1.645 marked"))


# ============================================================
# p-degeri-iki-yonlu: observed z = 1.67, two-sided test
# ============================================================
def fig_p_two_sided():
    X0, X1 = -3.6, 3.6
    Z, ZC = 1.67, 1.96
    p = Plot(40, 26, 480, 180, (X0, X1), (0, 0.42))
    shade(p, pdf, X0, -Z, PRACTICE, 0.42)
    shade(p, pdf, Z, X1, PRACTICE, 0.42)
    p.line(curve(pdf, X0, X1), THEORY, 2.1)
    ints = [k for k in range(-3, 4) if abs(abs(k) - Z) > 0.5 and abs(abs(k) - ZC) > 0.5]
    x_axis(p, [(k, num(k)) for k in ints] + [(Z, ""), (-Z, ""), (ZC, ""), (-ZC, "")], it("z"))
    for s in (-1, 1):
        p.vline(s * Z, 0, pdf(Z), PRACTICE, None, 0.9)
        p.label(s * Z, 0, num(s * Z), dy=17, anchor="middle", color=PRACTICE, size=12.5, bold=True)
        p.vline(s * ZC, 0, 0.30, REMARK, "4 3", 0.9)
        p.label(s * ZC, 0.30, num(s * ZC), dy=-6, anchor="middle", color=REMARK, size=12)
        leader(p, s * 2.85, 0.17, s * 2.1, 0.02)
        p.label(s * 2.85, 0.17, f"0,0475", dy=-5, anchor="middle", color=PRACTICE, size=LABEL, bold=True)
    save("p-degeri-iki-yonlu", figure(
        560, 250, [p],
        "İki yönlü testte gözlenen z = 1,67 için p değeri, iki kuyruktaki turuncu alanların toplamıdır: "
        "p ≈ 2 · 0,0475 = 0,095. Kesikli çizgiler α = 0,05 düzeyindeki kritik değerler ±1,96'dır; "
        "gözlenen değer bunların arasında kalır.",
        aria="Standard normal curve with both tails beyond 1.67 shaded as the two-sided p value and the critical values 1.96 marked"))


fig_alpha_beta()
fig_critical_regions()
fig_power()
fig_p_one_sided()
fig_p_two_sided()
print("ok")
