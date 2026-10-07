# -*- coding: utf-8 -*-
"""
Figures of the chapter "NumPy ile Lineer Cebir"
(dersler/python-bilimsel/numpy-ile-lineer-cebir.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution,
exercise or callout), never inside a definition box and never directly under a
heading. Concept figures of this course stay visible: they are not put inside
collapsed .cozum/.ispat blocks. The figures are NOT produced at build time. Run

    python scripts/python_figures/lin.py
    python scripts/center_figures.py "python-lin-*.md"
    python scripts/check_figure_labels.py "scripts/_figures/python-lin-*.md"

and paste the markup of scripts/_figures/python-lin-<name>.md into the .qmd.
Captions are Turkish on purpose; aria labels are plain ASCII.

Every plotted number is recomputed here with NumPy by the same code the
chapter shows (Hilbert errors, least-squares fit, SVD, low-rank images). Run
the script with the course packages (Python 3.12 with NumPy 2.5,
SciPy 1.18, SymPy 1.14) (Python 3.12 with NumPy 2.5, SciPy 1.18,
SymPy 1.14; OPENBLAS_NUM_THREADS=1) so the floating-point data match the printed outputs.
"""
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import (Plot, figure, dot, hollow, circle_pts, panel_title,  # noqa: E402
                      WIDE, TEXT, THEORY, PRACTICE, BASE, REMARK, BG)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "python-lin-"

MINUS = "&#8722;"
KAPPA = "&#954;"
SIGMA = "&#963;"
EPS = "&#949;"
TIMES = "&#215;"
APPROX = "&#8776;"


def save(name, markup):
    (OUT_DIR / f"{PREFIX}{name}.md").write_text(markup, encoding="utf-8", newline="\n")
    print(f"{PREFIX}{name}.md")


def it(s):
    """Italic run inside an SVG <text>."""
    return f'<tspan font-style="italic">{s}</tspan>'


def sub(s, size=9.5):
    """Subscript inside an SVG <text>; the zero-width space resets the baseline."""
    return f'<tspan font-size="{size}" dy="3.5">{s}</tspan><tspan dy="-3.5">&#8203;</tspan>'


def sup(s, size=9.5):
    """Superscript inside an SVG <text>."""
    return f'<tspan font-size="{size}" dy="-5">{s}</tspan><tspan dy="5">&#8203;</tspan>'


def dec(v, digits=2):
    """Decimal comma and a true minus sign: -0.5 -> '−0,5'."""
    s = f"{v:.{digits}f}".rstrip("0").rstrip(".")
    if s in ("-0", ""):
        s = "0"
    return s.replace(".", ",").replace("-", MINUS)


def pow10(k):
    """Tick label 10^k with a true minus sign."""
    return "10" + sup(str(k).replace("-", MINUS), 10)


def rect(p, x, y, w, h, fill="none", opacity=1.0, stroke=TEXT, width=1.0, stroke_opacity=0.55):
    p.add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{fill}" '
          f'fill-opacity="{opacity}" stroke="{stroke}" stroke-width="{width}" '
          f'stroke-opacity="{stroke_opacity}"/>')


def pixel_plot(W, H):
    """A Plot whose data coordinates are the SVG pixels themselves (y grows down)."""
    return Plot(0, 0, W, H, (0, W), (H, 0))


# ============================================================
# carpim-boyutlari: the shape rule of A @ B, (3, 4) @ (4, 2) -> (3, 2)
# ============================================================
def fig_matmul_shapes():
    W, H = 540, 250
    p = pixel_plot(W, H)
    c = 40                                   # cell size in pixels
    m, n, q = 3, 4, 2
    i_hi, j_hi = 1, 0                        # highlighted row of A, column of B
    ax, ay = 30, 70                          # A: n columns x m rows
    bx, by = ax + n * c + 50, ay - (n - m) * c / 2
    cx, cy = bx + q * c + 50, ay

    def grid(x0, y0, rows, cols):
        for r in range(rows):
            for k in range(cols):
                rect(p, x0 + k * c, y0 + r * c, c, c, stroke_opacity=0.45)

    # highlights first, the grid lines on top
    rect(p, ax, ay + i_hi * c, n * c, c, fill=THEORY, opacity=0.22, stroke="none")
    rect(p, bx + j_hi * c, by, c, n * c, fill=BASE, opacity=0.22, stroke="none")
    rect(p, cx + j_hi * c, cy + i_hi * c, c, c, fill=PRACTICE, opacity=0.35, stroke="none")
    grid(ax, ay, m, n)
    grid(bx, by, n, q)
    grid(cx, cy, m, q)
    for x0, y0, cols, rows in ((ax, ay, n, m), (bx, by, q, n), (cx, cy, q, m)):
        rect(p, x0, y0, cols * c, rows * c, width=1.6, stroke_opacity=0.8)

    mid = ay + m * c / 2 + 6
    p.text_px(ax + n * c + 25, mid, "@", TEXT, 12.5, "middle", True)
    p.text_px(bx + q * c + 25, mid, "=", TEXT, 12.5, "middle", True)

    # entries of the highlighted row, column and product cell
    for k in range(n):
        p.text_px(ax + k * c + c / 2, ay + i_hi * c + c / 2 + 4,
                  it("a") + sub(it("i") + str(k + 1)), THEORY, 12, "middle")
        p.text_px(bx + j_hi * c + c / 2, by + k * c + c / 2 + 4,
                  it("b") + sub(str(k + 1) + it("j")), BASE, 12, "middle")
    p.text_px(cx + j_hi * c + c / 2, cy + i_hi * c + c / 2 + 4,
              it("c") + sub(it("ij")), PRACTICE, 12, "middle", True)

    # names and shapes under the blocks
    base_y = max(ay + m * c, by + n * c) + 24
    p.text_px(ax + n * c / 2, base_y, it("A") + ": (3, 4)", TEXT, 12, "middle", True)
    p.text_px(bx + q * c / 2, base_y, it("B") + ": (4, 2)", TEXT, 12, "middle", True)
    p.text_px(cx + q * c / 2, base_y, it("C") + ": (3, 2)", TEXT, 12, "middle", True)
    p.text_px(ax - 8, ay + i_hi * c + c / 2 + 4, it("i"), THEORY, 12, "end", True)
    p.text_px(bx + j_hi * c + c / 2, by - 8, it("j"), BASE, 12, "middle", True)

    # the entry formula and the inner-dimension rule, centred under the blocks
    centre = (ax + cx + q * c) / 2
    terms = " + ".join(it("a") + sub(it("i") + str(k)) + it("b") + sub(str(k) + it("j"))
                       for k in range(1, n + 1))
    p.text_px(centre, base_y + 30, it("c") + sub(it("ij")) + " = " + terms, PRACTICE, 12, "middle",
              True)
    p.text_px(centre, base_y + 54,
              "iç boyutlar eşit olmalı: " + it("A") + "'nın 4 sütunu, " + it("B") + "'nin 4 satırı",
              TEXT, 11.5, "middle")
    save("carpim-boyutlari", figure(
        W, H + 40, [p],
        "<code>A @ B</code> için boyut kuralı: (3, 4) şekilli <em>A</em> ile (4, 2) şekilli <em>B</em>'nin "
        "çarpımı (3, 2) şekillidir. <em>C</em>'nin <em>i</em>. satır, <em>j</em>. sütundaki elemanı, "
        "<em>A</em>'nın <em>i</em>. satırı ile <em>B</em>'nin <em>j</em>. sütununun iç çarpımıdır. Bu "
        "yüzden <em>A</em>'nın sütun sayısı <em>B</em>'nin satır sayısına eşit olmak zorundadır.",
        aria="A 3 by 4 grid A with row i shaded, times a 4 by 2 grid B with column j shaded, equals a "
             "3 by 2 grid C with the entry c_ij shaded; c_ij = a_i1 b_1j + ... + a_i4 b_4j"))


# ============================================================
# iki-dogru: a well and an ill conditioned 2 x 2 system, b2 raised by 0.1
# ============================================================
def fig_two_lines():
    A_good = np.array([[1.0, 1.0], [1.0, -1.0]])
    A_bad = np.array([[1.0, 1.0], [1.0, 1.1]])
    b_good, b_bad = np.array([2.0, 0.0]), np.array([2.0, 2.1])
    db = np.array([0.0, 0.1])
    XR = YR = (-0.6, 2.6)
    S = 236
    panels = []
    cases = [(A_good, b_good, "İyi koşullu: " + KAPPA + " = 1"),
             (A_bad, b_bad, "Kötü koşullu: " + KAPPA + " " + APPROX + " 42")]
    for k, (A, b, title) in enumerate(cases):
        p = Plot(46 + k * (S + 70), 40, S, S, XR, YR)
        ticks = (0, 1, 2)
        p.axes(ticks, ticks, it("x"), it("y"))
        p.grid(ticks, ticks)
        x = np.linalg.solve(A, b)
        x2 = np.linalg.solve(A, b + db)
        kappa = np.linalg.cond(A)
        assert abs(kappa - (1.0 if k == 0 else 42.0762)) < 1e-3

        def row_line(a, rhs, color, dash=None):
            # a[0] x + a[1] y = rhs, drawn over the x range and clipped to the y range
            xs = np.linspace(XR[0], XR[1], 2)
            ys = (rhs - a[0] * xs) / a[1]
            pts = []
            for t in np.linspace(0, 1, 200):
                xx = XR[0] + t * (XR[1] - XR[0])
                yy = (rhs - a[0] * xx) / a[1]
                if YR[0] <= yy <= YR[1]:
                    pts.append((xx, yy))
            p.line(pts, color, 2.0, dash)
            return xs, ys

        row_line(A[0], b[0], THEORY)
        row_line(A[1], b[1], BASE)
        row_line(A[1], b[1] + db[1], BASE, "6 4")
        p.points([tuple(x)], TEXT, 4.4)
        p.points([tuple(x2)], PRACTICE, 4.4)
        panel_title(p, title, TEXT, 12.5)
        if k == 0:
            p.label(x[0], x[1], "(1, 1)", 0, -13, TEXT, 12, "middle")
            p.label(x2[0], x2[1], "(1,05; 0,95)", 9, 15, PRACTICE, 12, "start", True)
            p.label(2.2, -0.2, it("x") + " + " + it("y") + " = 2", 0, 0, THEORY, 12, "end", True)
            p.label(1.5, 2.3, it("x") + " " + MINUS + " " + it("y") + " = 0", 0, 0, BASE, 12, "end", True)
            p.label(2.55, 1.2, it("x") + " " + MINUS + " " + it("y") + " = 0,1", 0, 0, BASE, 12, "end")
        else:
            p.label(x[0], x[1], "(1, 1)", 9, -8, TEXT, 12, "start")
            p.label(x2[0], x2[1], "(0, 2)", 9, -6, PRACTICE, 12, "start", True)
            p.label(1.9, -0.45, it("x") + " + " + it("y") + " = 2", 0, 0, THEORY, 12, "end", True)
            p.label(2.55, 1.85, it("x") + " + 1,1" + it("y") + " = 2,1", 0, 0, BASE, 12, "end", True)
            p.label(2.55, 1.5, it("x") + " + 1,1" + it("y") + " = 2,2", 0, 0, BASE, 12, "end")
        panels.append(p)
    save("iki-dogru", figure(
        2 * S + 150, S + 100, panels,
        "Her iki sistemde de ikinci denklemin sağ tarafı 0,1 artırıldı: ikinci doğru, kesikli konumuna "
        "kayar. Solda doğrular dik açıyla kesiştiği için çözüm (1, 1)'den yalnızca (1,05; 0,95)'e "
        "gider. Sağda doğrular neredeyse paraleldir; aynı küçük kayma kesişim noktasını (1, 1)'den "
        "(0, 2)'ye taşır.",
        WIDE,
        aria="Two panels. Left: lines x + y = 2 and x - y = 0 meet at right angles at (1, 1); shifting "
             "the second line moves the solution to (1.05, 0.95). Right: lines x + y = 2 and "
             "x + 1.1y = 2.1 are nearly parallel; the same shift moves the solution from (1, 1) to "
             "(0, 2)"))


# ============================================================
# hilbert: relative error and residual of solve vs inv for H_n, n = 5..12
# ============================================================
def hilbert_data():
    """The table printed by the chapter's Hilbert example."""
    def rel_err(approx, exact):
        return np.linalg.norm(approx - exact) / np.linalg.norm(exact)

    rows = []
    for n in range(5, 13):
        i = np.arange(1, n + 1)
        H = 1.0 / (i[:, None] + i[None, :] - 1)
        x_true = np.ones(n)
        b = H @ x_true
        x1 = np.linalg.solve(H, b)
        x2 = np.linalg.inv(H) @ b
        rows.append((n, np.linalg.cond(H), rel_err(x1, x_true), rel_err(x2, x_true),
                     rel_err(H @ x1, b), rel_err(H @ x2, b)))
    return rows


def fig_hilbert():
    rows = hilbert_data()
    eps = np.finfo(float).eps
    ns = [r[0] for r in rows]
    XR, YR = (4.6, 12.4), (-17.0, 1.5)
    PW, PH = 228, 250
    yt = (-16, -12, -8, -4, 0)
    panels = []
    specs = [
        ("Göreli hata", [(2, THEORY, "solve"), (3, PRACTICE, "inv")], True),
        ("Göreli artık", [(4, THEORY, "solve"), (5, PRACTICE, "inv")], False),
    ]
    for k, (title, series, guide) in enumerate(specs):
        p = Plot(70 + k * (PW + 80), 40, PW, PH, XR, YR)
        p.axes(ns, yt, it("n"), "", str, pow10)
        p.grid((), yt)
        if guide:
            pts = [(r[0], math.log10(r[1] * eps)) for r in rows]
            p.line(pts, TEXT, 1.4, "5 4", 0.75)
        for col, color, _ in series:
            pts = [(r[0], math.log10(r[col])) for r in rows]
            p.line(pts, color, 2.0)
            p.points(pts, color, 3.6)
        panel_title(p, title, TEXT, 12.5)
        # legend in the empty upper-left corner
        lx, ly = 5.0, 0.2
        entries = [(color, name, None) for _, color, name in series]
        if guide:
            entries.append((TEXT, KAPPA + "(" + it("H") + sub(it("n")) + ")" + TIMES + EPS, "5 4"))
        for e, (color, name, dash) in enumerate(entries):
            yy = ly - e * 1.9
            p.line([(lx, yy), (lx + 0.8, yy)], color, 2.0 if dash is None else 1.4, dash)
            p.label(lx + 0.8, yy, name, 6, 4, color if dash is None else TEXT, 12, "start", True)
        panels.append(p)
    save("hilbert", figure(
        2 * PW + 170, PH + 90, panels,
        "Hilbert sistemleri <em>H</em><sub><em>n</em></sub><em>x</em> = <em>b</em> için "
        "<code>solve</code> ve <code>inv</code> ile bulunan çözümler (dikey eksen logaritmik). "
        "Solda göreli hata: ikisi de koşul sayısıyla büyür; kesikli çizgi κ(<em>H</em><sub><em>n</em></sub>)·ε "
        "kaba tahminidir. Sağda göreli artık ‖<em>H</em><sub><em>n</em></sub><em>x</em> &#8722; "
        "<em>b</em>‖/‖<em>b</em>‖: <code>solve</code>'un artığı 10<sup>&#8722;16</sup> düzeyinde kalır, "
        "<code>inv</code>'inki koşul sayısıyla birlikte büyür.",
        WIDE,
        aria="Two log-scale panels over n = 5 to 12. Left: relative error of solve and of inv, both "
             "growing with n, inv above solve, with the dashed estimate kappa times eps. Right: relative "
             "residual; solve stays near 1e-16 while inv grows to about 5e-2"))


# ============================================================
# spektral: A = [[2, 1], [1, 2]] maps the unit circle onto an ellipse whose
# axes are the eigenvectors
# ============================================================
def fig_spectral():
    A = np.array([[2.0, 1.0], [1.0, 2.0]])
    w, V = np.linalg.eig(A)
    w, V = np.real_if_close(w), np.real_if_close(V)
    order = np.argsort(w)[::-1]
    w, V = w[order], V[:, order]               # 3 first, then 1
    assert np.allclose(w, [3, 1])
    R = 3.5
    S = 340
    p = Plot(40, 30, S, S, (-R, R), (-R, R))
    p.origin_axes(it("x"), it("y"), (-3, -2, 2, 3), (-3, -2, 2, 3), dec, dec)
    circ = circle_pts(0, 0, 1, samples=120)
    p.line(circ, TEXT, 1.4, "4 3", 0.8)
    ell = [tuple(A @ np.array(q)) for q in circ]
    p.line(ell, THEORY, 2.0)
    q1, q2 = V[:, 0], V[:, 1]
    p.arrow((0, 0), tuple(w[0] * q1), PRACTICE, 2.0)
    p.arrow((0, 0), tuple(q1), PRACTICE, 2.6, head=9)
    p.arrow((0, 0), tuple(w[1] * q2), PRACTICE, 2.6, head=9)
    x = np.array([1.0, 0.0])
    Ax = A @ x
    p.arrow((0, 0), tuple(x), BASE, 2.0, head=8)
    p.arrow((0, 0), tuple(Ax), BASE, 2.0, head=8, dash="5 3")
    p.label(*(w[0] * q1), it("A") + it("q") + sub("1") + " = 3" + it("q") + sub("1"), 8, 2, PRACTICE, 12,
            "start", True)
    p.label(*(0.45 * q1), it("q") + sub("1"), -5, -5, PRACTICE, 12, "end", True)
    p.label(*q2, it("A") + it("q") + sub("2") + " = " + it("q") + sub("2"), -6, -8, PRACTICE, 12, "end", True)
    p.label(0.7, 0, it("x"), 0, 17, BASE, 12, "middle", True)
    p.label(*Ax, it("A") + it("x"), 8, 4, BASE, 12, "start", True)
    p.label(-2.0, -2.75, it("A") + "'nın görüntüsü", 0, 0, THEORY, 12, "middle", True)
    save("spektral", figure(
        S + 80, S + 60, [p],
        "<em>A</em> = [[2, 1], [1, 2]] birim çemberi (kesikli) elipse götürür. Elipsin eksenleri "
        "<em>A</em>'nın dik özvektörleri boyuncadır: <em>q</em><sub>1</sub> = (1, 1)/√2 doğrultusu 3 kat "
        "uzar, <em>q</em><sub>2</sub> = (&#8722;1, 1)/√2 doğrultusu olduğu gibi kalır. Özvektör olmayan "
        "<em>x</em> = (1, 0) ise <em>Ax</em> = (2, 1)'e gider ve doğrultusu değişir.",
        aria="Unit circle (dashed) and its image ellipse under A = [[2, 1], [1, 2]]; eigenvector q1 along "
             "(1, 1) is stretched to 3 q1, eigenvector q2 along (-1, 1) is unchanged, and x = (1, 0) is "
             "mapped to Ax = (2, 1), which points in a different direction"))


# ============================================================
# parabol: least-squares parabola through 15 noisy points (seed 7)
# ============================================================
def fig_parabola():
    rng = np.random.default_rng(7)
    t = np.linspace(0, 4, 15)
    y = 1 + 2 * t - 0.5 * t**2 + rng.normal(0, 0.3, t.size)
    M = np.column_stack([np.ones_like(t), t, t**2])
    c, rss, rank, sv = np.linalg.lstsq(M, y)
    assert abs(c[0] - 0.92977395) < 1e-8
    XR, YR = (-0.25, 4.3), (0.0, 3.9)
    p = Plot(56, 30, 420, 280, XR, YR)
    xt, yt = (0, 1, 2, 3, 4), (0, 1, 2, 3)
    p.axes(xt, yt, it("t"), it("y"))
    p.grid(xt, yt)
    tt = np.linspace(-0.1, 4.15, 120)
    p.line(list(zip(tt, 1 + 2 * tt - 0.5 * tt**2)), BASE, 1.6, "6 4")
    p.line(list(zip(tt, c[0] + c[1] * tt + c[2] * tt**2)), THEORY, 2.2)
    yhat = M @ c
    for ti, yi, hi in zip(t, y, yhat):
        p.line([(ti, yi), (ti, hi)], PRACTICE, 1.6)
    p.points(list(zip(t, y)), TEXT, 3.8)
    # legend in the empty band under the arch
    lx, ly = 1.15, 0.95
    legend = [(THEORY, None, "uydurulan parabol"), (BASE, "6 4", "1 + 2" + it("t") + " " + MINUS + " 0,5"
               + it("t") + sup("2")), (PRACTICE, None, "artıklar")]
    for e, (color, dash, name) in enumerate(legend):
        yy = ly - e * 0.3
        p.line([(lx, yy), (lx + 0.35, yy)], color, 2.0, dash)
        p.label(lx + 0.35, yy, name, 7, 4, color, 12, "start", True)
    save("parabol", figure(
        int(p.x0 + p.w + 40), int(p.y0 + p.h + 40), [p],
        "On beş gürültülü veri noktası, <code>lstsq</code> ile uydurulan parabol "
        "<em>y</em> &#8776; 0,930 + 2,028<em>t</em> &#8722; 0,505<em>t</em><sup>2</sup> ve verinin "
        "üretildiği 1 + 2<em>t</em> &#8722; 0,5<em>t</em><sup>2</sup> eğrisi (kesikli). Dikey parçalar "
        "artıklardır; <code>lstsq</code> bunların kareleri toplamını en küçük yapar.",
        aria="Fifteen noisy data points, the least-squares parabola y = 0.930 + 2.028 t - 0.505 t^2, the "
             "dashed generating curve 1 + 2t - 0.5t^2 and vertical residual segments"))


# ============================================================
# svd-elips: A = [[3, 0], [4, 5]] maps v1, v2 onto sigma1 u1, sigma2 u2
# ============================================================
def fig_svd_ellipse():
    A = np.array([[3.0, 0.0], [4.0, 5.0]])
    U, s, Vt = np.linalg.svd(A)
    assert np.allclose(s, [math.sqrt(45), math.sqrt(5)])
    v1, v2 = Vt[0], Vt[1]
    u1, u2 = U[:, 0], U[:, 1]
    left = Plot(40, 60, 200, 200, (-1.5, 1.5), (-1.5, 1.5))
    right = Plot(330, 30, 260, 260, (-7.5, 7.5), (-7.5, 7.5))
    left.origin_axes(it("x"), it("y"))
    right.origin_axes(it("x"), it("y"), (-6, -3, 3, 6), (-3, 3, 6), dec, dec)
    circ = circle_pts(0, 0, 1, samples=120)
    left.line(circ, THEORY, 2.0)
    right.line([tuple(A @ np.array(q)) for q in circ], THEORY, 2.0)
    left.arrow((0, 0), tuple(v1), PRACTICE, 2.4, head=9)
    left.arrow((0, 0), tuple(v2), BASE, 2.4, head=9)
    right.arrow((0, 0), tuple(s[0] * u1), PRACTICE, 2.4, head=9)
    right.arrow((0, 0), tuple(s[1] * u2), BASE, 2.4, head=9)
    left.label(*v1, it("v") + sub("1"), -6, 14, PRACTICE, 12.5, "end", True)
    left.label(*v2, it("v") + sub("2"), -6, -6, BASE, 12.5, "end", True)
    right.label(*(s[0] * u1), SIGMA + sub("1") + it("u") + sub("1"), -9, 4, PRACTICE, 12.5, "end", True)
    right.label(*(s[1] * u2), SIGMA + sub("2") + it("u") + sub("2"), -4, -10, BASE, 12.5, "end", True)
    right.label(3.2, -4.2, SIGMA + sub("1") + " = 3√5 " + APPROX + " " + dec(s[0], 2), 0, 0, PRACTICE, 12,
                "start", True)
    right.label(3.2, -5.6, SIGMA + sub("2") + " = √5 " + APPROX + " " + dec(s[1], 2), 0, 0, BASE, 12,
                "start", True)
    panel_title(left, "birim çember", TEXT, 12.5)
    panel_title(right, it("A") + "'nın görüntüsü: elips", TEXT, 12.5)
    # the map between the panels
    y_mid = left.y0 + left.h / 2
    left.add(f'<line x1="{left.x0 + left.w + 18:.1f}" y1="{y_mid:.1f}" x2="{right.x0 - 26:.1f}" '
             f'y2="{y_mid:.1f}" stroke="{TEXT}" stroke-width="1.6" opacity="0.8"/>')
    left.add(f'<polygon points="{right.x0 - 18:.1f},{y_mid:.1f} {right.x0 - 27:.1f},{y_mid - 4.5:.1f} '
             f'{right.x0 - 27:.1f},{y_mid + 4.5:.1f}" fill="{TEXT}" opacity="0.8"/>')
    left.text_px((left.x0 + left.w + right.x0) / 2 - 4, y_mid - 9, it("A"), TEXT, 12.5, "middle", True)
    save("svd-elips", figure(
        610, 320, [left, right],
        "<em>A</em> = [[3, 0], [4, 5]] matrisinin tekil değer ayrışımının geometrisi. Birim çemberdeki dik "
        "<em>v</em><sub>1</sub>, <em>v</em><sub>2</sub> vektörleri, elipsin yarı eksenleri olan "
        "σ<sub>1</sub><em>u</em><sub>1</sub> ve σ<sub>2</sub><em>u</em><sub>2</sub> vektörlerine gider. "
        "Vektörlerin işaretleri <code>svd</code>'nin döndürdüğü gibidir; işaret seçimi keyfidir.",
        WIDE,
        aria="Two panels. Left: unit circle with orthonormal vectors v1 and v2 pointing down-left and "
             "up-left. Right: the image ellipse under A = [[3, 0], [4, 5]] with semi-axes sigma1 u1 of "
             "length 3 sqrt 5 and sigma2 u2 of length sqrt 5"))


# ============================================================
# dusuk-rank: a 32 x 32 image and its rank 2, 6 and 12 approximations
# ============================================================
def image_data():
    n = 32
    g = np.linspace(-1, 1, n)
    X, Y = g[None, :], g[:, None]
    R = np.sqrt(X**2 + Y**2)
    ring = np.exp(-((R - 0.6) / 0.12) ** 2)
    band = (np.abs(X - Y) < 0.15).astype(float)
    return np.clip(ring + band, 0, 1)


def heatmap(p, x0, y0, F, cell):
    """Draw F (values clipped to [0, 1]) as grey cells; one path per opacity level."""
    levels = np.clip(np.round(np.clip(F, 0, 1) * 10), 0, 10).astype(int)
    for lev in range(1, 11):
        d = []
        for r in range(F.shape[0]):
            k = 0
            while k < F.shape[1]:
                if levels[r, k] != lev:
                    k += 1
                    continue
                start = k
                while k < F.shape[1] and levels[r, k] == lev:
                    k += 1
                wpx = (k - start) * cell
                d.append(f"M{x0 + start * cell:g} {y0 + r * cell:g}h{wpx:g}v{cell:g}h-{wpx:g}z")
        if d:
            p.add(f'<path d="{"".join(d)}" fill="{TEXT}" fill-opacity="{lev / 10:.1f}"/>')
    rect(p, x0, y0, F.shape[1] * cell, F.shape[0] * cell, width=1.2, stroke_opacity=0.6)


def fig_low_rank():
    img = image_data()
    U, s, Vt = np.linalg.svd(img)
    assert np.linalg.matrix_rank(img) == 32
    cell, gap = 4, 26
    side = 32 * cell
    W = 4 * side + 3 * gap + 40
    p = pixel_plot(W, 230)
    panels = [(img, "özgün (rank 32)", None)]
    for k in (2, 6, 12):
        img_k = (U[:, :k] * s[:k]) @ Vt[:k]
        err = np.linalg.norm(img - img_k, 2)
        assert abs(err - s[k]) < 1e-9
        panels.append((img_k, it("k") + " = " + str(k), "hata " + APPROX + " " + dec(err, 2)))
    for e, (F, title, note) in enumerate(panels):
        x0 = 20 + e * (side + gap)
        heatmap(p, x0, 40, F, cell)
        p.text_px(x0 + side / 2, 30, title, TEXT, 12.5, "middle", True)
        if note:
            p.text_px(x0 + side / 2, 40 + side + 20, note, PRACTICE, 12, "middle")
    save("dusuk-rank", figure(
        W, 200, [p],
        "32 × 32 boyutlu bir matris gri tonlu bir görüntü olarak (renk ne kadar yoğunsa değer o kadar "
        "büyük) ve onun "
        "<code>svd</code> ile bulunan rank 2, 6 ve 12 yaklaşımları. Alttaki sayılar 2-normundaki "
        "hatalardır ve sırasıyla σ<sub>3</sub>, σ<sub>7</sub>, σ<sub>13</sub> tekil değerlerine eşittir. "
        "Çizimde 0'ın altına ya da 1'in üstüne taşan değerler 0 ve 1'e kırpıldı.",
        WIDE,
        aria="Four 32 by 32 grey-scale images: the original ring crossed by a diagonal band, and its rank "
             "2, 6 and 12 approximations from the SVD with 2-norm errors 4.51, 2.87 and 1.08"))


if __name__ == "__main__":
    fig_matmul_shapes()
    fig_two_lines()
    fig_hilbert()
    fig_spectral()
    fig_parabola()
    fig_svd_ellipse()
    fig_low_rank()
