# -*- coding: utf-8 -*-
"""
Figures of the chapter "Ortalama İçin Aralık Tahmini"
(dersler/matematiksel-istatistik/ortalama-icin-aralik-tahmini.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box: a figure that illustrates a
definition sits directly below that box. The figures are NOT produced at
build time. Run

    python scripts/statistics_figures/ort.py
    python scripts/center_figures.py "statistics-ort-*.md" --keep-width
    python scripts/check_figure_labels.py "scripts/_figures/statistics-ort-*.md"

and paste the markup of scripts/_figures/statistics-ort-<name>.md into the
.qmd. Captions are Turkish on purpose (they are shown on the site); aria
labels are plain ASCII.
"""
import io
import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, TEXT, THEORY, PRACTICE, BASE, REMARK  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "statistics-ort-"
OUT = {}

MINUS, MU, ALPHA, NU = "&#8722;", "&#956;", "&#945;", "&#957;"
LABEL = 13
TICK = 11
SAMPLES = 480


# ------------------------------------------------------------
# helpers
# ------------------------------------------------------------
def num(v, digits=None):
    """Decimal comma and a real minus sign."""
    if digits is None:
        s = f"{v:.4f}".rstrip("0").rstrip(".")
    else:
        s = f"{v:.{digits}f}"
    if s in ("-0", ""):
        s = "0"
    return s.replace("-", MINUS).replace(".", ",")


def it(s):
    return f'<tspan font-style="italic">{s}</tspan>'


def sub(s):
    return f'<tspan font-size="9" dy="3">{s}</tspan><tspan dy="-3">&#8203;</tspan>'


def normal_pdf(x):
    return math.exp(-0.5 * x * x) / math.sqrt(2 * math.pi)


def t_pdf(x, k):
    c = math.lgamma((k + 1) / 2) - math.lgamma(k / 2) - 0.5 * math.log(math.pi * k)
    return math.exp(c - (k + 1) / 2 * math.log(1 + x * x / k))


def t_quantile(p, k):
    """Upper quantile (p > 0.5) of Student t by Simpson integration and bisection."""
    def cdf(x, n=2000):
        h = x / n
        s = t_pdf(0, k) + t_pdf(x, k)
        for i in range(1, n):
            s += (4 if i % 2 else 2) * t_pdf(i * h, k)
        return 0.5 + s * h / 3
    lo, hi = 0.0, 50.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if cdf(mid) < p:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def sample(f, a, b, n=SAMPLES):
    return [(a + (b - a) * k / n, f(a + (b - a) * k / n)) for k in range(n + 1)]


def shade(p, f, a, b, color=PRACTICE, opacity=0.30, n=240):
    p.polygon([(a, 0)] + sample(f, a, b, n) + [(b, 0)], color, opacity)


def x_axis(p, ticks, name="", y=0.0):
    Y = p.Y(y)
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
        p.add(f'<text x="{right+4:.1f}" y="{Y+4:.1f}" fill="{TEXT}" font-size="12" font-style="italic" opacity="0.85">{name}</text>')


def y_axis(p, ticks, name="", x=None, digits=None):
    X = p.X(p.xmin if x is None else x)
    top, bottom = p.y0 - 10, p.Y(p.ymin)
    p.add(f'<g stroke="{TEXT}" stroke-width="1.1" opacity="0.5" fill="{TEXT}">'
          f'<line x1="{X:.1f}" y1="{bottom:.1f}" x2="{X:.1f}" y2="{top:.1f}"/>'
          f'<polygon points="{X:.1f},{top:.1f} {X-3.5:.1f},{top+8:.1f} {X+3.5:.1f},{top+8:.1f}" stroke="none"/></g>')
    for v in ticks:
        Y = p.Y(v)
        p.add(f'<line x1="{X-3:.1f}" y1="{Y:.1f}" x2="{X+3:.1f}" y2="{Y:.1f}" stroke="{TEXT}" stroke-width="1" opacity="0.7"/>')
        p.add(f'<text x="{X-7:.1f}" y="{Y+4:.1f}" fill="{TEXT}" font-size="{TICK}" text-anchor="end" opacity="0.8">{num(v, digits)}</text>')
    if name:
        p.add(f'<text x="{X+8:.1f}" y="{top+6:.1f}" fill="{TEXT}" font-size="12" font-style="italic" opacity="0.85">{name}</text>')


def legend(p, px, py, entries, row=20):
    for i, (lab, c, d) in enumerate(entries):
        y = py + i * row
        da = f' stroke-dasharray="{d}"' if d else ""
        p.add(f'<line x1="{px:.1f}" y1="{y:.1f}" x2="{px+26:.1f}" y2="{y:.1f}" stroke="{c}" stroke-width="2.2"{da}/>')
        p.text_px(px + 33, y + 4.5, lab, TEXT, 12.5)


def seg(p, x1, x2, y, color, width=2.4):
    p.add(f'<line x1="{p.X(x1):.1f}" y1="{p.Y(y):.1f}" x2="{p.X(x2):.1f}" y2="{p.Y(y):.1f}" '
          f'stroke="{color}" stroke-width="{width}" stroke-linecap="round"/>')


def leader(p, x1, y1, x2, y2, color=PRACTICE):
    p.add(f'<line x1="{p.X(x1):.1f}" y1="{p.Y(y1):.1f}" x2="{p.X(x2):.1f}" y2="{p.Y(y2):.1f}" '
          f'stroke="{color}" stroke-width="1" opacity="0.8"/>')


def emit(name, W, H, panels, caption, css_class="ders-grafik", aria=""):
    OUT[name] = figure(W, H, panels, caption, css_class, aria)


# ============================================================
# tekrarli-orneklem: 25 simulated 95% intervals, N(50, 16), n = 10
# ============================================================
MU0, SIG, N_OBS, REPS, SEED = 50.0, 4.0, 10, 25, 11


def simulated_intervals():
    rng = random.Random(SEED)
    half = 1.96 * SIG / math.sqrt(N_OBS)
    out = []
    for _ in range(REPS):
        xbar = sum(rng.gauss(MU0, SIG) for _ in range(N_OBS)) / N_OBS
        out.append((xbar - half, xbar, xbar + half))
    return out


def fig_repeated():
    rows = simulated_intervals()
    W, H = 560, 400
    p = Plot(60, 34, 460, 330, (45, 55), (0, REPS + 1))
    p.vline(MU0, 0.2, REPS + 0.6, TEXT, "5 4", 0.7)
    p.text_px(p.X(MU0), p.y0 - 10, f"{MU} = 50", TEXT, LABEL, "middle", bold=True)
    for i, (lo, xb, hi) in enumerate(rows, 1):
        miss = not (lo <= MU0 <= hi)
        c = PRACTICE if miss else THEORY
        seg(p, lo, hi, i, c, 2.6 if miss else 2.0)
        p.points([(xb, i)], c, 2.8)
    x_axis(p, [(v, num(v)) for v in range(45, 56)], "", y=0)
    p.text_px(p.X(55), p.Y(0) + 34, it("x&#772;") + " ve güven aralığı", TEXT, 12, "end")
    misses = sum(1 for lo, _, hi in rows if not (lo <= MU0 <= hi))
    emit("tekrarli-orneklem", W, H, [p],
         f"N(50, 16) kitlesinden çekilen 25 ayrı örneklemin (her biri n = 10) her birinden kurulan %95 güven "
         f"aralığı. Nokta örneklem ortalamasını gösterir. Aralıkların {REPS - misses} tanesi μ = 50'yi içeriyor, "
         f"{misses} tanesi (turuncu) içermiyor. Uzun vadede aralıkların yaklaşık %95'i μ'yü yakalar.",
         aria="Twenty five simulated 95 percent confidence intervals around the true mean 50; intervals that miss are highlighted")
    return misses


# ============================================================
# z-kritik: standard normal with central 1 - alpha and two tails alpha/2
# ============================================================
def fig_z_critical():
    W, H = 560, 270
    p = Plot(40, 30, 480, 180, (-3.6, 3.6), (0, 0.42))
    c = 1.96
    shade(p, normal_pdf, -3.6, -c, PRACTICE, 0.40)
    shade(p, normal_pdf, c, 3.6, PRACTICE, 0.40)
    shade(p, normal_pdf, -c, c, THEORY, 0.14)
    p.line(sample(normal_pdf, -3.6, 3.6), THEORY, 2.2)
    x_axis(p, [(0, "0"), (-c, ""), (c, "")], it("z"))
    for x in (-c, c):
        p.vline(x, 0, normal_pdf(x), PRACTICE, "4 3", 0.85)
    Y = p.Y(0)
    zlab = f"{it('z')}{sub('1' + MINUS + it(ALPHA) + '/2')}"
    p.text_px(p.X(-c), Y + 20, f"{MINUS}{zlab}", PRACTICE, 13, "middle", bold=True)
    p.text_px(p.X(c), Y + 20, zlab, PRACTICE, 13, "middle", bold=True)
    p.text(0, 0.14, f"1 {MINUS} {it(ALPHA)}", THEORY, LABEL + 1, "middle", bold=True)
    leader(p, -2.35, 0.012, -2.95, 0.07)
    p.text(-2.95, 0.078, f"{it(ALPHA)}/2", PRACTICE, LABEL, "middle", bold=True)
    leader(p, 2.35, 0.012, 2.95, 0.07)
    p.text(2.95, 0.078, f"{it(ALPHA)}/2", PRACTICE, LABEL, "middle", bold=True)
    emit("z-kritik", W, H, [p],
         "Standart normal eğrisinin ortasında 1 − α alan bırakan iki nokta: −z(1−α/2) ve z(1−α/2). Her "
         "kuyrukta α/2 alan kalır. Z = (X̄ − μ)/(σ/√n) bu iki nokta arasına 1 − α olasılıkla düşer.",
         aria="Standard normal density with central area 1 minus alpha and two tails of area alpha over 2")


# ============================================================
# guven-duzeyleri: 90, 95, 99 percent intervals for xbar = 498.3
# ============================================================
def fig_levels():
    W, H = 560, 230
    p = Plot(60, 24, 450, 150, (492, 505), (0, 4))
    xb = 498.3
    rows = ((3, "%90", 1.645, BASE), (2, "%95", 1.96, THEORY), (1, "%99", 2.576, PRACTICE))
    p.vline(xb, 0.4, 3.6, TEXT, "5 4", 0.6)
    for y, lab, z, c in rows:
        lo, hi = xb - 2 * z, xb + 2 * z
        seg(p, lo, hi, y, c, 3.0)
        p.points([(lo, y), (hi, y)], c, 3.2)
        p.text_px(p.x0 - 12, p.Y(y) + 4.5, lab, c, LABEL, "end", bold=True)
        p.label(lo, y, num(lo, 2), -6, -8, c, 11.5, "end")
        p.label(hi, y, num(hi, 2), 6, -8, c, 11.5, "start")
    x_axis(p, [(v, num(v)) for v in range(492, 506, 2)], "", y=0)
    p.text_px(p.X(xb), p.Y(0) + 32, f"{it('x&#772;')} = 498,3", TEXT, 12, "middle")
    emit("guven-duzeyleri", W, H, [p],
         "Aynı örneklemden (n = 25, σ = 10, x̄ = 498,3) kurulan %90, %95 ve %99 güven aralıkları. "
         "Güven düzeyi arttıkça aralık genişler; üçü de x̄'nin çevresinde simetriktir.",
         aria="Nested 90, 95 and 99 percent confidence intervals centred at 498.3")


# ============================================================
# t-z-karsilastirma: t with 9 df against N(0, 1), critical points
# ============================================================
def fig_t_vs_z():
    W, H = 560, 280
    f = lambda x: t_pdf(x, 9)
    p = Plot(40, 30, 480, 190, (-4.2, 4.2), (0, 0.42))
    ct, cz = 2.262, 1.96
    shade(p, f, ct, 4.2, PRACTICE, 0.40)
    shade(p, f, -4.2, -ct, PRACTICE, 0.40)
    p.line(sample(normal_pdf, -4.2, 4.2), BASE, 2.0, "6 4")
    p.line(sample(f, -4.2, 4.2), THEORY, 2.2)
    x_axis(p, [(0, "0"), (-ct, ""), (ct, ""), (-cz, ""), (cz, "")], "")
    for x in (-ct, ct):
        p.vline(x, 0, f(x), PRACTICE, "4 3", 0.85)
    for x in (-cz, cz):
        p.vline(x, 0, normal_pdf(x), BASE, "2 3", 0.85)
    Y = p.Y(0)
    p.text_px(p.X(ct) + 4, Y + 17, "2,262", PRACTICE, 12, "start", bold=True)
    p.text_px(p.X(-ct) - 4, Y + 17, f"{MINUS}2,262", PRACTICE, 12, "end", bold=True)
    p.text_px(p.X(cz) - 2, Y + 32, "1,96", BASE, 12, "end", bold=True)
    p.text_px(p.X(-cz) + 2, Y + 32, f"{MINUS}1,96", BASE, 12, "start", bold=True)
    legend(p, 380, 50, [(f"{it('t')}{sub('9')}", THEORY, None), (f"{it('N')}(0, 1)", BASE, "6 4")])
    emit("t-z-karsilastirma", W, H, [p],
         "t₉ yoğunluğu (düz) ve standart normal yoğunluk (kesikli). Her iki kuyrukta 0,025 alan bırakan "
         "noktalar t₉ için ±2,262, standart normal için ±1,96'dır. Kalın kuyruklar yüzünden t aralığı daha geniştir.",
         aria="Student t density with 9 degrees of freedom and the standard normal density with their 97.5 percent quantiles")


# ============================================================
# t-kantil-yakinsama: t_{nu, 0.975} against nu, limit 1.96
# ============================================================
def fig_t_quantiles():
    W, H = 560, 290
    p = Plot(56, 30, 460, 200, (0, 62), (1.6, 4.5))
    pts = [(k, t_quantile(0.975, k)) for k in range(2, 61)]
    p.add(f'<line x1="{p.X(0):.1f}" y1="{p.Y(1.96):.1f}" x2="{p.X(62):.1f}" y2="{p.Y(1.96):.1f}" '
          f'stroke="{BASE}" stroke-width="1.6" stroke-dasharray="6 4"/>')
    p.line(pts, THEORY, 1.4, None, 0.6)
    p.points(pts, THEORY, 2.6)
    for k, lab, dx, dy, anc in ((9, "2,262", 8, -8, "start"), (30, "2,042", 4, -12, "middle")):
        v = t_quantile(0.975, k)
        p.points([(k, v)], PRACTICE, 4.2)
        p.label(k, v, f"{it(NU)} = {k}: {lab}", dx, dy, PRACTICE, 12, anc, bold=True)
    p.label(2, 4.303, f"{it(NU)} = 2: 4,303", 10, 4, PRACTICE, 12, "start", bold=True)
    p.label(61, 1.96, f"{it('z')}{sub('0,975')} = 1,96", 0, 17, BASE, 12, "end", bold=True)
    # axes
    Yb = p.Y(1.6)
    p.add(f'<g stroke="{TEXT}" stroke-width="1.1" opacity="0.5" fill="{TEXT}">'
          f'<line x1="{p.x0-4:.1f}" y1="{Yb:.1f}" x2="{p.x0+p.w+10:.1f}" y2="{Yb:.1f}"/></g>')
    for v in (0, 10, 20, 30, 40, 50, 60):
        X = p.X(v)
        p.add(f'<line x1="{X:.1f}" y1="{Yb-3:.1f}" x2="{X:.1f}" y2="{Yb+3:.1f}" stroke="{TEXT}" stroke-width="1" opacity="0.7"/>')
        p.text_px(X, Yb + 16, num(v), TEXT, TICK, "middle")
    p.text_px(p.x0 + p.w + 14, Yb + 4, it(NU), TEXT, 12)
    y_axis(p, (2.0, 2.5, 3.0, 3.5, 4.0), "", 0, 1)
    emit("t-kantil-yakinsama", W, H, [p],
         "Serbestlik derecesine göre t(ν; 0,975) kantilleri. ν küçükken kantil 1,96'dan belirgin biçimde "
         "büyüktür; ν = 30 civarında fark 0,1'in altına iner ve ν büyüdükçe kantiller z(0,975) = 1,96'ya yaklaşır.",
         aria="The 97.5 percent quantiles of Student t for degrees of freedom 2 to 60 decreasing toward 1.96")


misses = fig_repeated()
fig_z_critical()
fig_levels()
fig_t_vs_z()
fig_t_quantiles()

for name, content in OUT.items():
    with io.open(OUT_DIR / f"{PREFIX}{name}.md", "w", encoding="utf-8", newline="\n") as fh:
        fh.write(content)
print(f"generated {len(OUT)} figures:", ", ".join(OUT), f"(misses: {misses})")
