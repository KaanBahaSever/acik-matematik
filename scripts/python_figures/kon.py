# -*- coding: utf-8 -*-
"""
Figures of the chapter "Kontrol Yapıları ve Fonksiyonlar"
(dersler/python-bilimsel/kontrol-yapilari-ve-fonksiyonlar.qmd).

Figures go INSIDE the box they explain (theorem, proposition, example or
callout), never inside a definition box (right below it instead) and never
directly under a heading. In this book concept figures must stay visible, so
they are not put inside a collapsed .cozum/.ispat block. The figures are NOT
produced at build time. Run

    python scripts/python_figures/kon.py
    python scripts/center_figures.py "python-kon-*.md"
    python scripts/check_figure_labels.py "scripts/_figures/python-kon-*.md"

and paste the markup of scripts/_figures/python-kon-<name>.md into the .qmd.
Captions are Turkish on purpose; aria labels are plain ASCII.

Every number drawn here is recomputed with the same algorithm as the code
block of the chapter it illustrates (partial sums, lattice points, Euclid's
divisions, the Collatz orbit, Newton iterates, Fibonacci calls), so the
figures agree with the printed outputs.
"""
import html
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import (Plot, figure, sup, TEXT, THEORY, PRACTICE, BASE,  # noqa: E402
                      REMARK, BG, WIDE)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "python-kon-"

MINUS = "&#8722;"
CDOT = "&#183;"
SUP = 9.5          # exponent size of the 10^k labels


def save(name, markup):
    (OUT_DIR / f"{PREFIX}{name}.md").write_text(markup, encoding="utf-8", newline="\n")
    print(f"{PREFIX}{name}.md")


def it(s):
    """Italic run inside an SVG <text>."""
    return f'<tspan font-style="italic">{s}</tspan>'


def sub(s, size=8.5):
    """Subscript inside an SVG <text>."""
    return f'<tspan font-size="{size}" dy="3">{s}</tspan><tspan dy="-3">&#8203;</tspan>'


def dec(v, digits=2):
    """Decimal comma and a true minus sign: -0.5 -> '−0,5'."""
    s = f"{v:.{digits}f}"
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    if s in ("-0", ""):
        s = "0"
    return s.replace(".", ",").replace("-", MINUS)


def sci(v, digits=1):
    """Scientific notation with a decimal comma: 0.0857 -> '8,6·10⁻²'."""
    e = math.floor(math.log10(abs(v)))
    m = v / 10 ** e
    if round(m, digits) >= 10:
        m, e = m / 10, e + 1
    return f"{dec(m, digits)}{CDOT}10" + sup(str(e).replace("-", MINUS), SUP)


def pow10(e):
    """Tick label 10^e."""
    return "10" + sup(str(e).replace("-", MINUS), SUP)


def text_w(s, size):
    """Rough advance width of a label (0.56 em per visible character)."""
    plain = html.unescape(re.sub(r"<[^>]+>", "", s)).replace("​", "")
    return len(plain) * 0.56 * size


def plate_px(p, px, py, s, size=11.5, anchor="start", opacity=0.92):
    """Page-coloured plate under a label that has to sit on lines."""
    w = text_w(s, size)
    x0 = px - (w / 2 if anchor == "middle" else w if anchor == "end" else 0)
    p.add(f'<rect x="{x0 - 2.5:.1f}" y="{py - 0.8 * size - 1:.1f}" width="{w + 5:.1f}" '
          f'height="{size + 3:.1f}" rx="3" fill="{BG}" opacity="{opacity}"/>')


def pixel_plot(W, H):
    """A Plot whose data coordinates are the pixel coordinates (y down)."""
    return Plot(0, 0, W, H, (0, W), (H, 0))


def box(p, cx, cy, w, h, color, fill_op=0.10, rx=6):
    p.add(f'<rect x="{cx - w / 2:.1f}" y="{cy - h / 2:.1f}" width="{w:.1f}" height="{h:.1f}" '
          f'rx="{rx}" fill="{color}" fill-opacity="{fill_op}" stroke="{color}" stroke-width="1.5"/>')


def diamond(p, cx, cy, hw, hh, color, fill_op=0.08):
    pts = f"{cx:.1f},{cy - hh:.1f} {cx + hw:.1f},{cy:.1f} {cx:.1f},{cy + hh:.1f} {cx - hw:.1f},{cy:.1f}"
    p.add(f'<polygon points="{pts}" fill="{color}" fill-opacity="{fill_op}" '
          f'stroke="{color}" stroke-width="1.5"/>')


# ============================================================
# 1. Flow of an if / elif / else statement
# ============================================================
def fig_flow():
    W, H = 640, 300
    p = pixel_plot(W, H)
    d1, d2, b3x = 105, 330, 545
    row1, row2, row3 = 95, 190, 268
    hw, hh = 82, 42
    # entry arrow
    p.arrow((d1, 14), (d1, row1 - hh), TEXT, 1.4, head=7)
    diamond(p, d1, row1, hw, hh, THEORY)
    diamond(p, d2, row1, hw, hh, THEORY)
    for cx, k in ((d1, 1), (d2, 2)):
        p.label(cx, row1, f"koşul {k}", 0, -3, THEORY, 12, "middle", True)
        p.label(cx, row1, "doğru mu?", 0, 13, THEORY, 11.5, "middle")
    # keywords
    p.label(d1 - hw + 6, row1 - hh + 4, "if", 0, 0, BASE, 13, "middle", True)
    p.label(d2 - hw + 6, row1 - hh + 4, "elif", 0, 0, BASE, 13, "middle", True)
    # "Hayır" branches
    p.arrow((d1 + hw, row1), (d2 - hw, row1), TEXT, 1.4, head=7)
    p.label((d1 + d2) / 2, row1, "Hayır", 0, -7, TEXT, 11.5, "middle")
    p.line([(d2 + hw, row1), (b3x, row1)], TEXT, 1.4)
    p.arrow((b3x, row1), (b3x, row2 - 18), TEXT, 1.4, head=7)
    p.label((d2 + hw + b3x) / 2, row1, "Hayır", 0, -7, TEXT, 11.5, "middle")
    # "Evet" branches
    for cx in (d1, d2):
        p.arrow((cx, row1 + hh), (cx, row2 - 18), TEXT, 1.4, head=7)
        p.label(cx, (row1 + hh + row2 - 18) / 2, "Evet", 7, 4, TEXT, 11.5, "start")
    # blocks
    for cx, k in ((d1, 1), (d2, 2), (b3x, 3)):
        box(p, cx, row2, 120, 36, BASE)
        p.label(cx, row2, f"blok {k}", 0, 4.5, BASE, 12.5, "middle", True)
    p.label(b3x - 60, row2 - 18, "else", -6, -6, BASE, 13, "end", True)
    # common exit
    for cx in (d1, d2, b3x):
        p.arrow((cx, row2 + 18), (cx, row3 - 16), TEXT, 1.4, head=7)
    box(p, (d1 + b3x) / 2, row3, b3x - d1 + 150, 32, TEXT, 0.06)
    p.label((d1 + b3x) / 2, row3, "if deyiminden sonraki ilk satır", 0, 4.5, TEXT, 12.5, "middle")
    cap = ("Bir <code>if</code>/<code>elif</code>/<code>else</code> deyiminin akışı. Koşullar yazıldıkları "
           "sırayla sınanır; doğru çıkan ilk koşulun bloğu çalışır ve geri kalanlar atlanır. Hiçbir "
           "koşul doğru değilse <code>else</code> bloğu çalışır. Hangi yoldan gidilirse gidilsin, sonunda "
           "deyimden sonraki satıra geçilir.")
    aria = ("Flow chart: condition 1 is tested; if true block 1 runs, otherwise condition 2 is tested; "
            "if true block 2 runs, otherwise the else block 3 runs; all three paths join at the next line")
    save("akis", figure(W, H, [p], cap, WIDE, aria))


# ============================================================
# 2. Partial sums of sum 1/k^2 and their error
# ============================================================
def fig_basel():
    limit = math.pi ** 2 / 6
    partial = []
    s = 0.0
    for k in range(1, 31):
        s += 1 / k ** 2
        partial.append((k, s))
    errors = []
    for j in range(1, 6):
        n = 10 ** j
        s = 0.0
        for k in range(1, n + 1):
            s += 1 / k ** 2
        errors.append((j, limit - s))

    W, H = 630, 290
    a = Plot(62, 40, 225, 190, (0, 31), (1.0, 1.7))
    a.grid(ys=(1.2, 1.4, 1.6))
    a.axes((0, 10, 20, 30), (1.0, 1.2, 1.4, 1.6), "", "",
           yfmt=lambda v: dec(v, 1))
    a.label(31, 1.0, it("n"), 14, 4, TEXT, 12)
    a.label(0, 1.7, it("S") + sub(it("n")), -4, -14, TEXT, 12, "middle")
    a.line([(0, limit), (31, limit)], BASE, 1.4, dash="6 4")
    a.label(31, limit, "π²/6 ≈ 1,6449", 0, -8, BASE, 11.5, "end", True)
    a.points(partial, THEORY, 2.8)
    a.label(15.5, 1.7, "Kısmi toplamlar", 0, -14, TEXT, 12, "middle", True)

    b = Plot(395, 40, 195, 190, (0.6, 5.4), (-5.4, -0.6))
    b.grid(xs=(1, 2, 3, 4, 5), ys=(-1, -2, -3, -4, -5))
    b.axes((1, 2, 3, 4, 5), (-1, -2, -3, -4, -5), "", "",
           xfmt=lambda v: pow10(int(v)), yfmt=lambda v: pow10(int(v)))
    b.label(5.4, -5.4, it("n"), 14, 4, TEXT, 12)
    b.line([(0.6, -0.6), (5.4, -5.4)], BASE, 1.4, dash="6 4")
    b.label(1.3, -1.3, "1/" + it("n"), 8, -6, BASE, 12, "start", True)
    b.line([(j, math.log10(e)) for j, e in errors], PRACTICE, 1.2, opacity=0.6)
    b.points([(j, math.log10(e)) for j, e in errors], PRACTICE, 4.0)
    b.label(3.0, -0.6, "Fark: π²/6 " + MINUS + " " + it("S") + sub(it("n")), 0, -14, TEXT, 12,
            "middle", True)
    cap = ("Sol: <em>S<sub>n</sub></em> = 1 + 1/4 + ⋯ + 1/<em>n</em>² kısmi toplamları artarak "
           "π²/6 ≈ 1,6449 değerine yaklaşır. Sağ: iç içe döngülü kodun yazdırdığı farklar "
           "(<em>n</em> = 10, 100, …, 100000) logaritmik eksenlerde; noktalar kesikli 1/<em>n</em> "
           "doğrusunun hemen altındadır, yani fark yaklaşık 1/<em>n</em> kadardır.")
    cap = cap.replace("⋯", "&#8943;")
    aria = ("Left: partial sums S_n of 1/k^2 for n = 1 to 30 increasing towards the dashed line pi^2/6. "
            "Right: log-log plot of pi^2/6 - S_n for n = 10 to 100000, lying just below the line 1/n")
    save("basel", figure(W, H, [a, b], cap, WIDE, aria))


# ============================================================
# 3. Lattice points in the disk of radius 5
# ============================================================
def fig_lattice():
    r = 5
    W, H = 400, 400
    p = Plot(40, 30, 330, 330, (-6, 6), (-6, 6))
    p.origin_axes(it("x"), it("y"), opacity=0.45)
    p.circle(0, 0, r, BASE, 1.8)
    inside = on = 0
    for x in range(-r - 1, r + 2):
        for y in range(-r - 1, r + 2):
            q = x * x + y * y
            if q < r * r:
                p.points([(x, y)], THEORY, 3.2)
                inside += 1
            elif q == r * r:
                p.points([(x, y)], PRACTICE, 4.2)
                on += 1
            elif abs(x) <= r and abs(y) <= r:
                p.hollow_points([(x, y)], TEXT, 2.6)
    assert inside + on == 81 and on == 12
    p.label(5.6, -5.0, it("x") + "² + " + it("y") + "² = 25", 0, 26, BASE, 12, "end", True)
    cap = ("<em>r</em> = 5 için kodun saydığı kafes noktaları: dairenin içindeki 69 nokta (mavi) ile "
           "çemberin tam üstündeki 12 nokta (turuncu) birlikte <em>N</em>(5) = 81 eder; π·5² ≈ 78,54 ile "
           "karşılaştırın. Boş halkalar karenin içinde kalıp daireye girmeyen noktalardır.")
    aria = ("Integer lattice points in the square from -5 to 5; 69 points strictly inside the circle "
            "x^2 + y^2 = 25 are filled, the 12 points on the circle are highlighted, the rest are hollow")
    save("kafes", figure(W, H, [p], cap, "ders-grafik", aria))


# ============================================================
# 4. Euclid's algorithm as tiling a 1071 x 462 rectangle with squares
# ============================================================
def fig_euclid():
    A, B = 1071, 462
    # the divisions printed by the chapter's while loop
    steps = []
    a, b = A, B
    while b != 0:
        q, r = divmod(a, b)
        steps.append((a, b, q, r))
        a, b = b, r
    assert [(s[1], s[2]) for s in steps] == [(462, 2), (147, 3), (21, 7)]
    W, H = 540, 300
    w = 470
    h = w * B / A
    p = Plot(40, 40, w, h, (0, A), (0, B))
    cols = (THEORY, BASE, PRACTICE)
    ops = (0.10, 0.16, 0.38)
    # lay the squares: horizontal run, vertical run, horizontal run
    x0, y0, x1, y1 = 0, 0, A, B          # remaining rectangle
    horizontal = True
    for i, (a, b, q, r) in enumerate(steps):
        side = b
        for t in range(q):
            if horizontal:
                sx, sy = x0 + t * side, y0
            else:
                sx, sy = x0, y0 + t * side
            p.polygon([(sx, sy), (sx + side, sy), (sx + side, sy + side), (sx, sy + side)],
                      cols[i], ops[i], stroke=cols[i], width=1.3)
            if side >= 100:
                p.label(sx + side / 2, sy + side / 2, str(side), 0, 4.5, cols[i], 12.5 if side > 200 else 11.5,
                        "middle", True)
        if horizontal:
            x0 += q * side
        else:
            y0 += q * side
        horizontal = not horizontal
    # dimension labels
    p.label(A / 2, 0, "1071", 0, 18, TEXT, 12, "middle")
    p.label(0, B / 2, "462", -7, 4, TEXT, 12, "end")
    p.arrow((A - 75, B + 75), (A - 40, B + 4), PRACTICE, 1.3, head=6)
    p.label(A - 75, B + 75, "21 kenarlı 7 kare", -4, -2, PRACTICE, 12, "end", True)
    cap = ("Öklid algoritması geometrik olarak: 1071 × 462 dikdörtgeninden sığdığı kadar büyük kare "
           "kesilir. 462 kenarlı 2 kare, kalan 147 × 462 şeritten 147 kenarlı 3 kare, kalan 147 × 21 "
           "şeritten 21 kenarlı 7 kare çıkar ve hiçbir şey artmaz. Bölümler 2, 3, 7 kare sayılarıdır; "
           "son karenin kenarı 21 = ebob(1071, 462)'dir.")
    aria = ("A 1071 by 462 rectangle tiled greedily by squares: two squares of side 462, three of side "
            "147 stacked in the remaining strip, and seven small squares of side 21 along the top of it")
    save("oklid", figure(W, H, [p], cap, "ders-grafik", aria))


# ============================================================
# 5. Collatz orbit of 27
# ============================================================
def fig_collatz():
    n = 27
    orbit = [n]
    while n != 1:
        n = n // 2 if n % 2 == 0 else 3 * n + 1
        orbit.append(n)
    steps = len(orbit) - 1
    peak = max(orbit)
    kpeak = orbit.index(peak)
    assert steps == 111 and peak == 9232
    W, H = 540, 300
    p = Plot(66, 34, 420, 210, (0, 115), (0, 10000))
    p.grid(ys=(2500, 5000, 7500, 10000))
    p.axes((0, 20, 40, 60, 80, 100), (0, 2500, 5000, 7500, 10000), "", "",
           yfmt=lambda v: str(int(v)))
    p.label(115, 0, it("k"), 14, 4, TEXT, 12)
    p.label(0, 10000, it("n") + sub(it("k")), -4, -14, TEXT, 12, "middle")
    p.line(list(enumerate(orbit)), THEORY, 1.4)
    p.points([(0, orbit[0]), (kpeak, peak), (steps, 1)], PRACTICE, 4.2)
    p.label(0, orbit[0], it("n") + sub("0") + " = 27", 6, -14, PRACTICE, 12, "start", True)
    p.label(kpeak, peak, f"en büyük terim {peak} (" + it("k") + f" = {kpeak})", -10, 4, PRACTICE, 12,
            "end", True)
    p.label(steps, 1, "1'e ulaştı", 4, -38, PRACTICE, 12, "end", True)
    p.label(steps, 1, "(" + it("k") + f" = {steps})", 4, -23, PRACTICE, 12, "end", True)
    cap = (f"27'den başlayan Collatz dizisinin terimleri. Dizi {steps} adımda 1'e iner; yol boyunca "
           f"{kpeak}. adımda {peak} değerine kadar tırmanır. Başlangıç değeri küçük olsa da adım sayısını "
           "önceden kestirmek zordur; bu yüzden döngü <code>while</code> ile yazılır.")
    aria = (f"Collatz orbit of 27 plotted against the step k: it wanders, climbs to the maximum {peak} "
            f"at step {kpeak} and reaches 1 after {steps} steps")
    save("collatz", figure(W, H, [p], cap, "ders-grafik", aria))


# ============================================================
# 6. Divisor pairs of 36 on a logarithmic line
# ============================================================
def fig_divisors():
    n = 36
    divs = [d for d in range(1, n + 1) if n % d == 0]
    root = math.isqrt(n)
    W, H = 540, 300
    L = math.log(n)
    p = Plot(50, 30, 440, 220, (-0.08, L + 0.08), (0, 1))
    x_of = lambda d: p.X(math.log(d))
    base_y = p.Y(0)
    sx = 440 / (L + 0.16)
    # shaded half d <= sqrt(n)
    p.add(f'<rect x="{x_of(1):.1f}" y="{base_y - 236:.1f}" width="{x_of(root) - x_of(1):.1f}" '
          f'height="236" fill="{PRACTICE}" fill-opacity="0.06"/>')
    # axis
    p.add(f'<line x1="{x_of(1) - 14:.1f}" y1="{base_y:.1f}" x2="{x_of(n) + 14:.1f}" y2="{base_y:.1f}" '
          f'stroke="{TEXT}" stroke-width="1.2" opacity="0.6"/>')
    cx = x_of(root)
    p.add(f'<line x1="{cx:.1f}" y1="{base_y + 4:.1f}" x2="{cx:.1f}" y2="{base_y - 246:.1f}" '
          f'stroke="{TEXT}" stroke-width="1" stroke-dasharray="4 3" opacity="0.55"/>')
    # arcs d -- n/d, all centred at sqrt(n)
    for d in divs:
        if d >= root:
            break
        R = (math.log(root) - math.log(d)) * sx
        pts = " ".join(f"{cx + R * math.cos(math.pi * t / 60):.1f},{base_y - R * math.sin(math.pi * t / 60):.1f}"
                       for t in range(61))
        p.add(f'<polyline points="{pts}" fill="none" stroke="{THEORY}" stroke-width="1.7" opacity="0.85"/>')
        s = f"{d} {CDOT} {n // d}"
        plate_px(p, cx, base_y - R - 5, s, 11.5, "middle")
        p.text_px(cx, base_y - R - 5, s, THEORY, 11.5, "middle", True)
    s = f"{root} {CDOT} {root}"
    # divisor ticks and labels
    for d in divs:
        X = x_of(d)
        col = PRACTICE if d <= root else THEORY
        p.add(f'<circle cx="{X:.1f}" cy="{base_y:.1f}" r="3.8" fill="{col}"/>')
        p.text_px(X, base_y + 18, str(d), col, 12, "middle", True)
    p.text_px(cx + 8, base_y - 12, s, PRACTICE, 11.5, "start", True)
    p.text_px(cx, base_y + 36, "√36 = 6", TEXT, 12, "middle")
    p.text_px(x_of(1) + 4, base_y - 222, it("d") + " ≤ √" + it("n"), PRACTICE, 12, "start", True)
    cap = ("36'nın bölenleri logaritmik ölçekli bir doğru üzerinde. Her <em>d</em> böleni, "
           "<em>d</em> · (36/<em>d</em>) = 36 eşitliğindeki eşine bir yayla bağlıdır. Bütün yayların "
           "merkezi √36 = 6 noktasıdır, bu yüzden her çiftin küçük elemanı 6'yı aşmaz. Aynı eşleme her "
           "<em>n</em> için geçerlidir: <em>n</em>'nin 1 ve kendisi dışında bir böleni varsa, 2 ile "
           "√<em>n</em> arasında da bir böleni vardır.")
    cap = cap.replace("…", "&#8230;")
    aria = ("Divisors 1, 2, 3, 4, 6, 9, 12, 18, 36 on a logarithmic line; arcs join 1-36, 2-18, 3-12, "
            "4-9 and are all centred at 6 = sqrt(36), so the smaller member of each pair is at most 6")
    save("bolen-ciftleri", figure(W, H, [p], cap, "ders-grafik", aria))


# ============================================================
# 7. Newton iterates for sqrt(2): error on a log scale
# ============================================================
def fig_newton():
    a, x = 2, 1.0
    xs = [x]
    for _ in range(5):
        x = (x + a / x) / 2
        xs.append(x)
    ref = math.sqrt(2)
    errs = [abs(v - ref) for v in xs]
    assert all(e > 0 for e in errs)
    W, H = 510, 300
    p = Plot(70, 30, 370, 220, (-0.4, 5.6), (-17, 0.6))
    p.grid(ys=(0, -4, -8, -12, -16))
    p.axes((0, 1, 2, 3, 4, 5), (0, -4, -8, -12, -16), "", "",
           xfmt=lambda v: str(int(v)), yfmt=lambda v: pow10(int(v)))
    p.label(5.6, -17, it("k"), 14, 4, TEXT, 12)
    p.label(-0.4, 0.6, "|" + it("x") + sub(it("k")) + " " + MINUS + " √2|", 0, -12, TEXT, 12, "middle")
    eps = math.log10(2.0 ** -52)
    p.line([(-0.4, eps), (5.6, eps)], BASE, 1.3, dash="6 4")
    p.label(-0.3, eps, "makine duyarlığı 2,2" + CDOT + "10" + sup(MINUS + "16", SUP), 4, -7, BASE, 11.5,
            "start", True)
    pts = [(k, math.log10(e)) for k, e in enumerate(errs)]
    p.line(pts, THEORY, 1.5)
    p.points(pts, PRACTICE, 4.2)
    for k, e in enumerate(errs):
        p.label(k, math.log10(e), sci(e), 9, -6, TEXT, 11.5, "start")
    cap = ("√2 için Newton iterasyonunun (<em>x</em><sub>0</sub> = 1) hatası logaritmik ölçekte. Hata "
           "üssü her adımda kabaca ikiye katlanır: 10<sup>−1</sup>, 10<sup>−3</sup>, 10<sup>−6</sup>, "
           "10<sup>−12</sup>. Beşinci adımda hata makine duyarlığına iner; daha fazla adım bir şey "
           "kazandırmaz.")
    aria = ("Semilog plot of the error of the Newton iterates for sqrt 2 starting at 1: about 4e-1, "
            "9e-2, 2e-3, 2e-6, 2e-12 and 2e-16, the last one on the dashed machine epsilon line")
    save("newton-hata", figure(W, H, [p], cap, "ders-grafik", aria))


# ============================================================
# 8. Call tree of the naive recursive fib(5)
# ============================================================
def fig_fib_tree():
    nodes, edges = [], []
    leaf = [0]

    def build(n, depth):
        idx = len(nodes)
        nodes.append([n, depth, 0.0])
        if n < 2:
            nodes[idx][2] = leaf[0]
            leaf[0] += 1
            return idx
        c1 = build(n - 1, depth + 1)
        c2 = build(n - 2, depth + 1)
        nodes[idx][2] = (nodes[c1][2] + nodes[c2][2]) / 2
        edges.append((idx, c1))
        edges.append((idx, c2))
        return idx

    build(5, 0)
    assert len(nodes) == 15 and leaf[0] == 8
    W, H = 660, 300
    slot, x0, y0, dy = 76, 50, 32, 60
    P = lambda i: (x0 + nodes[i][2] * slot, y0 + nodes[i][1] * dy)
    p = pixel_plot(W, H)
    for i, j in edges:
        (xa, ya), (xb, yb) = P(i), P(j)
        p.add(f'<line x1="{xa:.1f}" y1="{ya + 12:.1f}" x2="{xb:.1f}" y2="{yb - 12:.1f}" '
              f'stroke="{TEXT}" stroke-width="1.1" opacity="0.55"/>')
    colors = {3: PRACTICE, 2: BASE}
    for i, (n, depth, _) in enumerate(nodes):
        cx, cy = P(i)
        col = colors.get(n, THEORY if n >= 4 else REMARK)
        box(p, cx, cy, 54, 24, col, 0.16 if n in colors else 0.08, rx=5)
        p.text_px(cx, cy + 4.5, f"fib({n})", col, 12, "middle", n in colors or n >= 4)
    cap = ("Saf özyinelemeli <code>fib(5)</code> çağrısının ağacı: toplam 15 çağrı. "
           "<code>fib(3)</code> (turuncu) iki kez, <code>fib(2)</code> (yeşil) üç kez baştan hesaplanır. "
           "<em>n</em> büyüdükçe aynı alt ağaçlar katlanarak tekrarlanır; <code>fib(30)</code> için çağrı "
           "sayısı 2692537'dir.")
    aria = ("Call tree of the naive recursive fib(5): 15 nodes; fib(3) appears twice and fib(2) three "
            "times, each recomputed from scratch; the leaves are fib(1) and fib(0)")
    save("fib-agac", figure(W, H, [p], cap, WIDE, aria))


if __name__ == "__main__":
    fig_flow()
    fig_basel()
    fig_lattice()
    fig_euclid()
    fig_collatz()
    fig_divisors()
    fig_newton()
    fig_fib_tree()
