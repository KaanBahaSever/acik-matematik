# -*- coding: utf-8 -*-
"""
Figures of the chapter "Matplotlib ile Grafik Çizimi"
(dersler/python-bilimsel/matplotlib-ile-grafik-cizimi.qmd).

Every figure redraws, with the theme-aware helpers of svg_plot/svg_plot3,
the plot that one code block of the chapter makes with Matplotlib. The data
are recomputed here with NumPy exactly as in that block (same grids, same
seeds) and the numbers the block prints are asserted, so the picture on the
page and the output under the code always describe the same data.

Figures go INSIDE the box they explain (example, exercise or callout); in an
example they come after the solution block so that they stay visible. Never
inside a definition box and never directly under a heading. The figures are
NOT produced at build time. Run

    python scripts/python_figures/mpl.py
    python scripts/center_figures.py "python-mpl-*.md"
    python scripts/check_figure_labels.py "scripts/_figures/python-mpl-*.md"

and paste the markup of scripts/_figures/python-mpl-<name>.md into the .qmd.
Captions are Turkish on purpose; aria labels are plain ASCII.
"""
import math
import os
import sys
from pathlib import Path

os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
import numpy as np  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, WIDE, TEXT, BG, THEORY, PRACTICE, BASE, REMARK  # noqa: E402
from svg_plot3 import Camera, Space, space_panel  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "python-mpl-"

MINUS, LAMBDA, THETA, PI_S = "&#8722;", "&#955;", "&#952;", "&#960;"
TICK = 11


def save(name, markup):
    (OUT_DIR / f"{PREFIX}{name}.md").write_text(markup, encoding="utf-8", newline="\n")
    print(f"{PREFIX}{name}.md")


def it(s):
    """Italic run inside an SVG <text>."""
    return f'<tspan font-style="italic">{s}</tspan>'


def sub(s, size=9.5):
    return f'<tspan font-size="{size}" dy="3">{s}</tspan><tspan dy="-3">&#8203;</tspan>'


def sup(s, size=9.5):
    return f'<tspan font-size="{size}" dy="-5">{s}</tspan><tspan dy="5">&#8203;</tspan>'


def dec(v, digits=None):
    """Decimal comma and a true minus sign: -0.25 -> '&#8722;0,25'."""
    s = f"{v:.4f}".rstrip("0").rstrip(".") if digits is None else f"{v:.{digits}f}"
    if s in ("-0", "", "-0.0", "-0.00"):
        s = "0" if digits is None else s.lstrip("-")
    return s.replace("-", MINUS).replace(".", ",")


def frame(p, opacity=0.55):
    """Full box around a panel, as Matplotlib draws its spines."""
    p.add(f'<rect x="{p.x0:.1f}" y="{p.y0:.1f}" width="{p.w:.1f}" height="{p.h:.1f}" fill="none" '
          f'stroke="{TEXT}" stroke-width="1" opacity="{opacity}"/>')


def xticks(p, values, labels=None, size=TICK):
    for k, v in enumerate(values):
        X = p.X(v)
        p.add(f'<line x1="{X:.1f}" y1="{p.y0 + p.h:.1f}" x2="{X:.1f}" y2="{p.y0 + p.h + 4:.1f}" '
              f'stroke="{TEXT}" opacity="0.6"/>')
        s = labels[k] if labels else dec(v)
        p.text_px(X, p.y0 + p.h + 16, s, TEXT, size, "middle")


def yticks(p, values, labels=None, size=TICK):
    for k, v in enumerate(values):
        Y = p.Y(v)
        p.add(f'<line x1="{p.x0 - 4:.1f}" y1="{Y:.1f}" x2="{p.x0:.1f}" y2="{Y:.1f}" '
              f'stroke="{TEXT}" opacity="0.6"/>')
        s = labels[k] if labels else dec(v)
        p.text_px(p.x0 - 7, Y + 4, s, TEXT, size, "end")


def title(p, s, size=12, dy=-10):
    p.text_px(p.x0 + p.w / 2, p.y0 + dy, s, TEXT, size, "middle")


def runs(xs, ys, lo, hi):
    """Split the polyline (xs, ys) into the pieces with lo <= y <= hi.

    NaN ends a piece (Matplotlib does the same); at a crossing of lo or hi
    the piece is cut at the interpolated boundary point, because Plot does
    not clip. -inf (log of an exact zero) counts as far below lo.
    """
    ys = np.where(np.isneginf(ys), lo - 1e3, ys)
    pieces, cur, prev = [], [], None
    for x, y in zip(xs, ys):
        x, y = float(x), float(y)
        if not math.isfinite(y):
            if len(cur) > 1:
                pieces.append(cur)
            cur, prev = [], None
            continue
        inside = lo <= y <= hi
        if prev is not None:
            px, py = prev
            p_in = lo <= py <= hi

            def at(b):
                t = (b - py) / (y - py)
                return (px + t * (x - px), b)

            if p_in and not inside:
                cur.append(at(hi if y > hi else lo))
                if len(cur) > 1:
                    pieces.append(cur)
                cur = []
            elif not p_in and inside:
                cur = [at(hi if py > hi else lo)]
            elif not p_in and not inside and (py - hi) * (y - lo) < 0 and (py - lo) * (y - hi) < 0:
                a, b = (hi, lo) if py > hi else (lo, hi)
                pieces.append([at(a), at(b)])
        if inside:
            cur.append((x, y))
        prev = (x, y)
    if len(cur) > 1:
        pieces.append(cur)
    return pieces


def decimate(p, pts, min_px=1.2):
    """Drop vertices closer than min_px pixels to the last kept one (keeps the end points)."""
    if len(pts) < 3:
        return pts
    out = [pts[0]]
    for q in pts[1:-1]:
        if math.hypot(p.X(q[0]) - p.X(out[-1][0]), p.Y(q[1]) - p.Y(out[-1][1])) >= min_px:
            out.append(q)
    out.append(pts[-1])
    return out


def legend_box(p, x, y, entries, size=11, width=100, row=17):
    """Matplotlib-like legend: a framed box at pixel (x, y) with (kind, color, text, extra) rows.

    kind is 'line' (extra = dash or None), 'thick' (extra = (width, opacity)),
    'dot', 'square' or 'bar'.
    """
    w = width
    h = row * len(entries) + 8
    p.add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="3" fill="{BG}" '
          f'fill-opacity="0.85" stroke="{TEXT}" stroke-opacity="0.3"/>')
    for k, (kind, color, text, extra) in enumerate(entries):
        cy = y + 4 + row * k + row / 2
        x1, x2 = x + 8, x + 30
        if kind == "line":
            da = f' stroke-dasharray="{extra}"' if extra else ""
            p.add(f'<line x1="{x1:.1f}" y1="{cy:.1f}" x2="{x2:.1f}" y2="{cy:.1f}" stroke="{color}" '
                  f'stroke-width="1.9"{da}/>')
        elif kind == "thick":
            wd, op = extra
            p.add(f'<line x1="{x1:.1f}" y1="{cy:.1f}" x2="{x2:.1f}" y2="{cy:.1f}" stroke="{color}" '
                  f'stroke-width="{wd}" opacity="{op}" stroke-linecap="round"/>')
        elif kind == "dot":
            p.add(f'<circle cx="{(x1 + x2) / 2:.1f}" cy="{cy:.1f}" r="3" fill="{color}"/>')
        elif kind == "square":
            p.add(f'<rect x="{(x1 + x2) / 2 - 3.5:.1f}" y="{cy - 3.5:.1f}" width="7" height="7" fill="{color}"/>')
        elif kind == "bar":
            p.add(f'<rect x="{x1:.1f}" y="{cy - 5:.1f}" width="{x2 - x1:.1f}" height="10" fill="{color}" '
                  f'fill-opacity="{extra}"/>')
        p.text_px(x + 38, cy + 4, text, TEXT, size)


def legend_row(p, x, y, entries, size=11.5, gap=18):
    """One-line legend below a figure; returns the x where it ends."""
    for kind, color, text, extra, tw in entries:
        if kind == "thick":
            wd, op = extra
            p.add(f'<line x1="{x:.1f}" y1="{y - 4:.1f}" x2="{x + 22:.1f}" y2="{y - 4:.1f}" stroke="{color}" '
                  f'stroke-width="{wd}" opacity="{op}" stroke-linecap="round"/>')
        elif kind == "line":
            da = f' stroke-dasharray="{extra}"' if extra else ""
            p.add(f'<line x1="{x:.1f}" y1="{y - 4:.1f}" x2="{x + 22:.1f}" y2="{y - 4:.1f}" stroke="{color}" '
                  f'stroke-width="1.9"{da}/>')
        elif kind == "dot":
            p.add(f'<circle cx="{x + 11:.1f}" cy="{y - 4:.1f}" r="3" fill="{color}"/>')
        elif kind == "square":
            p.add(f'<rect x="{x + 7.5:.1f}" y="{y - 7.5:.1f}" width="7" height="7" fill="{color}"/>')
        p.text_px(x + 28, y, text, TEXT, size)
        x += 28 + tw + gap
    return x


# ---------------------------------------------------------------------------
# marching squares (contour lines of gridded data, as Matplotlib's contour)
# ---------------------------------------------------------------------------
# cell corners a = Z[i, j], b = Z[i, j+1], c = Z[i+1, j+1], d = Z[i+1, j];
# edges B (bottom), R (right), T (top), L (left)
_CASES = {1: [("L", "B")], 2: [("B", "R")], 3: [("L", "R")], 4: [("R", "T")], 6: [("B", "T")],
          7: [("L", "T")], 8: [("T", "L")], 9: [("B", "T")], 11: [("R", "T")], 12: [("L", "R")],
          13: [("B", "R")], 14: [("L", "B")]}


def contour_lines(x, y, Z, level):
    """Polylines (lists of (x, y)) of Z = level on the grid Z[i, j] = f(x[j], y[i])."""
    ny, nx = Z.shape
    point = {}

    def edge(i, j, e):
        if e == "B":
            key, (i0, j0), (i1, j1) = ("h", i, j), (i, j), (i, j + 1)
        elif e == "T":
            key, (i0, j0), (i1, j1) = ("h", i + 1, j), (i + 1, j), (i + 1, j + 1)
        elif e == "L":
            key, (i0, j0), (i1, j1) = ("v", i, j), (i, j), (i + 1, j)
        else:
            key, (i0, j0), (i1, j1) = ("v", i, j + 1), (i, j + 1), (i + 1, j + 1)
        if key not in point:
            z0, z1 = Z[i0, j0], Z[i1, j1]
            t = (level - z0) / (z1 - z0)
            point[key] = (x[j0] + t * (x[j1] - x[j0]), y[i0] + t * (y[i1] - y[i0]))
        return key

    nbr = {}
    for i in range(ny - 1):
        for j in range(nx - 1):
            a, b, c, d = Z[i, j], Z[i, j + 1], Z[i + 1, j + 1], Z[i + 1, j]
            case = (a >= level) + 2 * (b >= level) + 4 * (c >= level) + 8 * (d >= level)
            if case in (0, 15):
                continue
            if case in (5, 10):
                centre_high = (a + b + c + d) / 4 >= level
                if (case == 5) == centre_high:
                    segs = [("B", "R"), ("T", "L")]
                else:
                    segs = [("L", "B"), ("R", "T")]
            else:
                segs = _CASES[case]
            for e0, e1 in segs:
                k0, k1 = edge(i, j, e0), edge(i, j, e1)
                nbr.setdefault(k0, []).append(k1)
                nbr.setdefault(k1, []).append(k0)
    lines, seen = [], set()
    # open chains first (start at an end with one neighbour), then closed loops
    starts = [k for k, v in nbr.items() if len(v) == 1] + list(nbr)
    for s in starts:
        if s in seen:
            continue
        chain, prev, cur = [s], None, s
        seen.add(s)
        while True:
            nxt = [k for k in nbr[cur] if k != prev and k not in seen]
            if not nxt:
                if len(chain) > 2 and chain[0] in nbr[cur]:
                    chain.append(chain[0])
                break
            prev, cur = cur, nxt[0]
            seen.add(cur)
            chain.append(cur)
        lines.append([point[k] for k in chain])
    return lines


def path_d(p, pts, close=False):
    d = " ".join(("M" if k == 0 else "L") + p.P(x, y) for k, (x, y) in enumerate(pts))
    return d + (" Z" if close else "")


# ============================================================
# ilk-grafik: the first plot (sin and cos) with the names of its parts
# ============================================================
def fig_first_plot():
    x = np.linspace(0, 2 * np.pi, 200)
    m = 0.05 * 2 * np.pi                       # Matplotlib's 5 % autoscale margin
    p = Plot(70, 56, 280, 190, (-m, 2 * np.pi + m), (-1.1, 1.1))
    # Figure: the whole canvas
    p.add(f'<rect x="12" y="12" width="476" height="306" rx="4" fill="none" stroke="{REMARK}" '
          f'stroke-width="1.2" stroke-dasharray="6 4"/>')
    p.text_px(22, 30, "Figure", REMARK, 12, "start", True)
    p.grid(range(0, 7), (-1, -0.5, 0, 0.5, 1))
    frame(p)
    xticks(p, range(0, 7))
    yticks(p, (-1, -0.5, 0, 0.5, 1))
    p.line(list(zip(x, np.sin(x))), THEORY, 2.0)
    p.line(list(zip(x, np.cos(x))), PRACTICE, 2.0, "6 4")
    title(p, "Sinüs ve kosinüs", 12.5, -12)
    p.text_px(p.x0 + p.w / 2, p.y0 + p.h + 34, it("x"), TEXT, 12, "middle")
    p.text_px(p.x0 - 44, p.y0 + p.h / 2 + 4, it("y"), TEXT, 12, "middle")
    lx, ly = p.x0 + 6, p.y0 + p.h - 48
    legend_box(p, lx, ly, [("line", THEORY, "sin " + it("x"), None),
                           ("line", PRACTICE, "cos " + it("x"), "6 4")], width=78)

    # the names of the parts, in the margin, with thin leaders
    def leader(x0, y0, x1, y1):
        p.add(f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" stroke="{REMARK}" '
              f'stroke-width="0.9"/>')

    col = 374
    leader(268, 40, col - 4, 40)
    p.text_px(col, 44, "ax.set_title", REMARK, 11.5)
    leader(p.x0 + p.w + 1, p.y0 - 1, col - 4, 70)
    p.text_px(col, 76, "Axes", REMARK, 11.5, "start", True)
    xc = 6.2
    leader(p.X(xc) + 2, p.Y(math.cos(xc)) + 3, col - 4, 102)
    p.text_px(col, 108, "ax.plot", REMARK, 11.5)
    leader(p.X(6.5), p.Y(-0.5), col - 4, 140)
    p.text_px(col, 145, "ax.grid", REMARK, 11.5)
    leader(lx + 40, ly + 42, lx + 40, 288)
    p.text_px(lx + 6, 302, "ax.legend", REMARK, 11.5)
    leader(p.x0 + p.w / 2 + 8, p.y0 + p.h + 30, p.x0 + p.w / 2 + 26, p.y0 + p.h + 30)
    p.text_px(p.x0 + p.w / 2 + 30, p.y0 + p.h + 34, "ax.set_xlabel", REMARK, 11.5)
    save("ilk-grafik", figure(
        500, 330, [p],
        "İlk örnekteki kodun çizdiği grafik. Kesikli çerçeve bütün tuvali, yani <em>Figure</em> nesnesini; "
        "içteki çerçeve tek koordinat sistemini, yani <em>Axes</em> nesnesini gösterir. Kenardaki etiketler "
        "her parçayı hangi metodun oluşturduğunu söyler.",
        aria="The plot of sin x (solid) and cos x (dashed) on 0 to 2 pi with a title, grid, legend and axis "
             "labels; margin notes name the parts: Figure, Axes, ax.set_title, ax.plot, ax.grid, ax.legend, "
             "ax.set_xlabel"))


# ============================================================
# taylor: Taylor polynomials of sin x and their errors (semilogy)
# ============================================================
def taylor_sin(x, n):
    total = np.zeros_like(x)
    for k in range(1, n + 1, 2):
        total += (-1) ** ((k - 1) // 2) * x**k / math.factorial(k)
    return total


def fig_taylor():
    x = np.linspace(-2 * np.pi, 2 * np.pi, 400)
    degrees = (1, 3, 5, 7)
    errs1 = [abs(math.sin(1.0) - taylor_sin(np.array([1.0]), n)[0]) for n in degrees]
    assert [f"{e:.2e}" for e in errs1] == ["1.59e-01", "8.14e-03", "1.96e-04", "2.73e-06"]
    colors = (THEORY, PRACTICE, BASE, REMARK)
    m = 0.05 * 4 * np.pi
    XR = (-2 * np.pi - m, 2 * np.pi + m)
    p1 = Plot(52, 40, 250, 190, XR, (-3, 3))
    p2 = Plot(52 + 250 + 92, 40, 250, 190, XR, (-16, 3))
    for p in (p1, p2):
        frame(p)
        xticks(p, (-6, -4, -2, 0, 2, 4, 6))
    yticks(p1, (-3, -2, -1, 0, 1, 2, 3))
    ex = (-15, -12, -9, -6, -3, 0, 3)
    yticks(p2, ex, ["10" + sup(dec(e)) for e in ex])
    p1.line(list(zip(x, np.sin(x))), TEXT, 5.0, None, 0.3)
    with np.errstate(divide="ignore"):
        for n, c in zip(degrees, colors):
            for piece in runs(x, taylor_sin(x, n), -3, 3):
                p1.line(piece, c, 1.7)
            err = np.log10(np.abs(np.sin(x) - taylor_sin(x, n)))
            for piece in runs(x, err, -16, 3):
                p2.line(decimate(p2, piece, 0.8), c, 1.7)
    title(p1, "Taylor polinomları")
    title(p2, "Hata |sin " + it("x") + " " + MINUS + " " + it("T") + sub(it("n")) + "(" + it("x") + ")|")
    ent = [("thick", TEXT, "sin " + it("x"), (5.0, 0.3), 30)]
    ent += [("line", c, it("n") + " = " + str(n), None, 36) for n, c in zip(degrees, colors)]
    legend_row(p1, 150, p1.y0 + p1.h + 48, ent, 11.5, 22)
    save("taylor", figure(
        660, 300, [p1, p2],
        "Alt grafik örneğindeki kodun çizdiği iki Axes. Solda kalın açık renkli eğri sin <em>x</em>, ince "
        "eğriler <em>T</em><sub>1</sub>, <em>T</em><sub>3</sub>, <em>T</em><sub>5</sub>, <em>T</em><sub>7</sub> "
        "Taylor polinomlarıdır; derece arttıkça polinom sinüse daha geniş bir aralıkta yapışır. Sağda aynı "
        "renklerle |sin <em>x</em> &#8722; <em>T<sub>n</sub></em>(<em>x</em>)| hataları logaritmik "
        "eksendedir: 0 yakınında hata 10<sup>&#8722;16</sup> düzeyine iner, uçlarda 10<sup>2</sup> düzeyine "
        "çıkar.",
        css_class=WIDE,
        aria="Two panels. Left: sin x as a thick light curve and its Taylor polynomials T1, T3, T5, T7 on "
             "-2 pi to 2 pi, clipped to -3..3. Right: the errors |sin x - Tn(x)| on a logarithmic y axis "
             "from 1e-16 to 1e3, V shaped with the minimum at x = 0"))


# ============================================================
# tanjant: tan x without and with NaN at the asymptotes
# ============================================================
def fig_tangent():
    x = np.linspace(-np.pi, np.pi, 1000)
    y = np.tan(x)
    y_cut = np.where(np.abs(y) > 10, np.nan, y)
    assert f"{np.max(np.abs(y)):.1f}" == "636.0" and int(np.isnan(y_cut).sum()) == 64
    m = 0.05 * 2 * np.pi
    XR = (-np.pi - m, np.pi + m)
    lo, hi = float(y.min()), float(y.max())
    my = 0.05 * (hi - lo)
    p1 = Plot(62, 40, 250, 180, XR, (lo - my, hi + my))
    p2 = Plot(62 + 250 + 72, 40, 250, 180, XR, (-10.5, 10.5))
    for p in (p1, p2):
        frame(p)
        xticks(p, (-3, -2, -1, 0, 1, 2, 3))
    yticks(p1, (-600, -400, -200, 0, 200, 400, 600))
    yticks(p2, (-10, -5, 0, 5, 10))
    p1.line(decimate(p1, list(zip(x, y)), 0.6), THEORY, 1.6)
    for piece in runs(x, y_cut, -10.5, 10.5):
        p2.line(piece, THEORY, 1.8)
    title(p1, "Düzeltilmemiş")
    title(p2, "|" + it("y") + "| &gt; 10 olan noktalar NaN")
    save("tanjant", figure(
        650, 250, [p1, p2],
        "tan <em>x</em> örneğindeki kodun çizdiği iki Axes. Solda Matplotlib, asimptotun iki yanındaki "
        "noktaları dikey çizgilerle birleştirmiş ve ölçeği ±600 düzeyine çıkarmıştır; dalların biçimi "
        "kaybolur. Sağda |<em>y</em>| &gt; 10 olan değerler NaN yapıldığı için çizgi asimptotlarda kopar.",
        css_class=WIDE,
        aria="Two panels of tan x on -pi to pi. Left: autoscaled to about -700..700, the branches look flat "
             "and two near vertical spikes join the branches across x = -pi/2 and x = pi/2. Right: values "
             "with |y| > 10 replaced by NaN, three clean branches between y = -10 and 10"))


# ============================================================
# parametrik-kutupsal: a Lissajous curve and the cardioid in polar axes
# ============================================================
def fig_param_polar():
    t = np.linspace(0, 2 * np.pi, 400)
    r = 1 + np.cos(t)
    area = 0.5 * np.sum(r[:-1] ** 2) * (t[1] - t[0])
    assert f"{area:.6f}" == f"{3 * np.pi / 2:.6f}" == "4.712389"
    p1 = space_panel(52, 52, 210, (-1.1, 1.1), (-1.1, 1.1))
    frame(p1)
    ticks = (-1, -0.5, 0, 0.5, 1)
    xticks(p1, ticks)
    yticks(p1, ticks)
    p1.line(list(zip(np.sin(3 * t), np.sin(2 * t))), THEORY, 1.9)
    title(p1, it("x") + " = sin 3" + it("t") + ",  " + it("y") + " = sin 2" + it("t"), 12, -12)
    # polar axes: r grid circles, angle spokes every 45 degrees, outer frame at r = 2.1
    R = 2.1
    p2 = space_panel(372, 52, 214, (-R, R), (-R, R))
    for rr in (0.5, 1.0, 1.5, 2.0):
        p2.circle(0, 0, rr, TEXT, 0.8, None, "none", 0.25)
    for k in range(8):
        a = k * math.pi / 4
        p2.line([(0, 0), (R * math.cos(a), R * math.sin(a))], TEXT, 0.8, None, 0.25)
        lab = f"{45 * k}°"
        ca, sa = math.cos(a), math.sin(a)
        p2.label(R * ca, R * sa, lab, 15 * ca, -15 * sa + 4, TEXT, TICK, "middle")
    p2.circle(0, 0, R, TEXT, 1.0, None, "none", 0.55)
    a = math.radians(157.5)                     # ax2.set_rlabel_position(157.5)
    for rr in (0.5, 1.0, 1.5, 2.0):
        p2.label(rr * math.cos(a), rr * math.sin(a), dec(rr), 0, -5, TEXT, 10.5, "middle")
    p2.line(list(zip(r * np.cos(t), r * np.sin(t))), THEORY, 2.0)
    p2.text_px(p2.x0 + p2.w / 2, p2.y0 - 30, it("r") + " = 1 + cos " + it(THETA), TEXT, 12, "middle")
    save("parametrik-kutupsal", figure(
        650, 300, [p1, p2],
        "Parametrik ve kutupsal örnekteki kodun çizdiği iki Axes. Solda eşit ölçekli eksende "
        "<em>x</em> = sin 3<em>t</em>, <em>y</em> = sin 2<em>t</em> Lissajous eğrisi; sağda kutupsal eksende "
        "<em>r</em> = 1 + cos <em>&#952;</em> kardioidi. Kutupsal eksende açılar derece, yarıçap çemberleri "
        "0,5 aralıklıdır.",
        css_class=WIDE,
        aria="Left: the Lissajous curve x = sin 3t, y = sin 2t in a square panel from -1.1 to 1.1. Right: polar "
             "axes with radius circles 0.5, 1, 1.5, 2 and spokes every 45 degrees, carrying the cardioid "
             "r = 1 + cos theta with its cusp at the pole and its far point at r = 2 on the 0 degree ray"))


# ============================================================
# ozdegerler: eigenvalues of a random 300 x 300 matrix (scatter)
# ============================================================
def fig_eigen_scatter():
    rng = np.random.default_rng(2024)
    n = 300
    A = rng.standard_normal((n, n)) / np.sqrt(n)
    lam = np.linalg.eigvals(A)
    is_real = np.abs(lam.imag) < 1e-12
    assert lam.size == 300 and int(is_real.sum()) == 12
    assert f"{np.abs(lam).max():.4f}" == "1.0453" and f"{np.mean(np.abs(lam) <= 1):.3f}" == "0.970"
    p = space_panel(62, 26, 300, (-1.5, 1.5), (-1.5, 1.5))
    frame(p)
    ticks = (-1.5, -1, -0.5, 0, 0.5, 1, 1.5)
    xticks(p, ticks)
    yticks(p, ticks)
    t = np.linspace(0, 2 * np.pi, 400)
    p.line(list(zip(np.cos(t), np.sin(t))), TEXT, 1.1, "5 4", 0.8)
    for z in lam[~is_real]:
        p.add(f'<circle cx="{p.X(z.real):.1f}" cy="{p.Y(z.imag):.1f}" r="2.6" fill="{THEORY}" '
              f'fill-opacity="0.85"/>')
    for z in lam[is_real]:
        p.add(f'<rect x="{p.X(z.real) - 3.5:.1f}" y="{p.Y(0) - 3.5:.1f}" width="7" height="7" '
              f'fill="{PRACTICE}"/>')
    p.text_px(p.x0 + p.w / 2, p.y0 + p.h + 36, "Re " + it(LAMBDA), TEXT, 12, "middle")
    p.text_px(p.x0 - 36, p.y0 - 8, "Im " + it(LAMBDA), TEXT, 12, "middle")
    legend_row(p, p.x0 - 10, p.y0 + p.h + 64,
               [("line", TEXT, "birim çember", "5 4", 68), ("dot", THEORY, "reel olmayan", None, 70),
                ("square", PRACTICE, "reel", None, 22)], 11, 14)
    save("ozdegerler", figure(
        400, 420, [p],
        "Saçılım örneğindeki kodun çizdiği grafik: girdileri bağımsız standart normal sayıların "
        "&#8730;300'e bölümü olan 300 × 300'lük bir matrisin 300 özdeğeri. Daireler reel olmayan, kareler "
        "12 reel özdeğerdir; noktalar birim diske neredeyse düzgün dağılır.",
        aria="Scatter plot in the complex plane, -1.5 to 1.5 on both axes: 288 non-real eigenvalues as dots "
             "spread evenly over the unit disk, symmetric about the real axis, 12 real eigenvalues as squares "
             "on the real axis, and the dashed unit circle"))


# ============================================================
# yarim-cember: histogram of the eigenvalues of a symmetric random matrix
# ============================================================
def fig_semicircle():
    rng = np.random.default_rng(7)
    n = 1000
    G = rng.standard_normal((n, n))
    H = (G + G.T) / np.sqrt(2 * n)
    lam = np.linalg.eigvalsh(H)
    counts, edges = np.histogram(lam, bins=40, density=True)
    width = edges[1] - edges[0]
    assert f"{lam[0]:.3f}, {lam[-1]:.3f}" == "-2.016, 1.975" and f"{width:.4f}" == "0.0998"
    assert f"{counts.max():.3f}" == "0.341"
    m = 0.05 * (edges[-1] - edges[0])
    p = Plot(58, 26, 420, 230, (edges[0] - m, edges[-1] + m), (0, 0.45))
    frame(p)
    xticks(p, (-2, -1.5, -1, -0.5, 0, 0.5, 1, 1.5, 2))
    yticks(p, (0, 0.1, 0.2, 0.3, 0.4))
    step = [(edges[0], 0.0)]
    for k, c in enumerate(counts):
        step += [(edges[k], c), (edges[k + 1], c)]
    step.append((edges[-1], 0.0))
    p.polygon(step, THEORY, 0.45)
    x = np.linspace(-2, 2, 400)
    p.line(list(zip(x, np.sqrt(4 - x**2) / (2 * np.pi))), TEXT, 2.0)
    p.text_px(p.x0 + p.w / 2, p.y0 + p.h + 34, it(LAMBDA), TEXT, 12, "middle")
    legend_box(p, p.x0 + p.w - 128, p.y0 + 8, [("bar", THEORY, "özdeğerler", 0.45),
                                                ("line", TEXT, "yarım çember", None)], width=120)
    save("yarim-cember", figure(
        500, 310, [p],
        "Histogram örneğindeki kodun çizdiği grafik: 1000 × 1000'lik simetrik rastgele bir matrisin "
        "özdeğerleri 40 kutuda, yoğunluk ölçeğinde. Siyah eğri &#8730;(4 &#8722; <em>x</em>²)/(2<em>&#960;</em>) "
        "yarım çember yoğunluğudur; dikdörtgenler onu yakından izler.",
        aria="Density histogram with 40 bins of the eigenvalues of a symmetric 1000 x 1000 random matrix, "
             "spread over -2 to 2, with the semicircle density sqrt(4 - x^2)/(2 pi) drawn on top; the "
             "bars follow the curve, highest near 0.32 at the centre"))


# ============================================================
# kontur: contour and contourf of z = x exp(-x^2 - y^2)
# ============================================================
def fig_contour():
    x = np.linspace(-2, 2, 200)
    y = np.linspace(-2, 2, 200)
    X, Y = np.meshgrid(x, y)
    Z = X * np.exp(-X**2 - Y**2)
    levels = np.linspace(-0.45, 0.45, 10)
    i, j = np.unravel_index(np.argmax(Z), Z.shape)
    assert f"{Z[i, j]:.4f}" == "0.4288" and f"{X[i, j]:.3f}, {Y[i, j]:.3f}" == "0.714, -0.010"
    S = 228
    p1 = space_panel(48, 40, S, (-2, 2), (-2, 2))
    p2 = space_panel(48 + S + 56, 40, S, (-2, 2), (-2, 2))
    shown = [lv for lv in levels if Z.min() < lv < Z.max()]          # +-0.45 never occur
    assert len(shown) == 8
    loops = {round(lv, 2): contour_lines(x, y, Z, lv) for lv in shown}
    for lv, ls in loops.items():
        assert len(ls) == 1 and ls[0][0] == ls[0][-1], lv            # one closed loop per level

    # right: filled bands as stacked super/sub-level sets; the colour bar uses the same stacking
    step_op = 0.2
    for lv in shown:
        loop = decimate(p2, loops[round(lv, 2)][0], 1.0)
        color = PRACTICE if lv > 0 else THEORY
        p2.add(f'<path d="{path_d(p2, loop, True)}" fill="{color}" fill-opacity="{step_op}" stroke="none"/>')
    # left: the lines, negative levels dashed as Matplotlib does with colors="k"
    for lv in shown:
        loop = decimate(p1, loops[round(lv, 2)][0], 1.0)
        da = ' stroke-dasharray="5 3"' if lv < 0 else ""
        p1.add(f'<path d="{path_d(p1, loop, True)}" fill="none" stroke="{TEXT}" stroke-width="1.3"{da} '
               f'opacity="0.9"/>')
    # inline level labels on a hollow patch, staggered on two rays per sign
    for lv in shown:
        loop = np.array(loops[round(lv, 2)][0])
        cx = 1 / math.sqrt(2) if lv > 0 else -1 / math.sqrt(2)
        k = int(round(abs(lv) / 0.1 - 0.5))                          # 0.05 -> 0, ..., 0.35 -> 3
        ang = (-55 if k % 2 == 0 else 55) if lv > 0 else (125 if k % 2 == 0 else -125)
        ang = math.radians(ang)
        d = np.arctan2(loop[:, 1], loop[:, 0] - cx)
        q = loop[np.argmin(np.abs(np.angle(np.exp(1j * (d - ang)))))]
        s = dec(lv, 2)
        w = 6.0 * len(s.replace("&#8722;", "-")) + 4
        X0, Y0 = p1.X(q[0]), p1.Y(q[1])
        p1.add(f'<rect x="{X0 - w / 2:.1f}" y="{Y0 - 7:.1f}" width="{w:.1f}" height="13" fill="{BG}"/>')
        p1.text_px(X0, Y0 + 4, s, TEXT, 10, "middle")
    for p, name in ((p1, "contour"), (p2, "contourf")):
        frame(p)
        xticks(p, (-2, -1, 0, 1, 2))
        yticks(p, (-2, -1, 0, 1, 2))
        title(p, name)
    # colour bar: 9 bands between consecutive levels
    bx, bw = p2.x0 + p2.w + 14, 14
    top, bot = p2.y0, p2.y0 + p2.h
    hb = (bot - top) / 9
    for b in range(9):
        lo = levels[b]
        mid = lo + 0.05
        n_layers = int(round((abs(mid) - 0.0) / 0.1))                # band [0.05, 0.15] -> 1 layer
        y_top = bot - (b + 1) * hb
        p2.add(f'<rect x="{bx:.1f}" y="{y_top:.1f}" width="{bw}" height="{hb:.1f}" fill="{BG}"/>')
        for _ in range(n_layers):
            color = PRACTICE if mid > 0 else THEORY
            p2.add(f'<rect x="{bx:.1f}" y="{y_top:.1f}" width="{bw}" height="{hb:.1f}" fill="{color}" '
                   f'fill-opacity="{step_op}"/>')
    p2.add(f'<rect x="{bx:.1f}" y="{top:.1f}" width="{bw}" height="{bot - top:.1f}" fill="none" '
           f'stroke="{TEXT}" stroke-opacity="0.5"/>')
    for b, lv in enumerate(levels):
        yy = bot - b * hb
        p2.add(f'<line x1="{bx + bw:.1f}" y1="{yy:.1f}" x2="{bx + bw + 3:.1f}" y2="{yy:.1f}" '
               f'stroke="{TEXT}" opacity="0.6"/>')
        p2.text_px(bx + bw + 6, yy + 4, dec(lv, 2), TEXT, 10.5)
    save("kontur", figure(
        660, 300, [p1, p2],
        "Kontur örneğindeki kodun çizdiği iki Axes: <em>z</em> = <em>x</em><em>e</em><sup>&#8722;<em>x</em>² "
        "&#8722; <em>y</em>²</sup> fonksiyonunun &#8722;0,45, &#8722;0,35, …, 0,45 seviyeleri. Solda "
        "<code>contour</code> çizgileri (negatif seviyeler kesikli, değerler çizginin üstünde), sağda "
        "<code>contourf</code> ile boyanmış bantlar ve renk çubuğu. Sağdaki tepe (0,707; 0) noktasında "
        "maksimum, soldaki çukur (&#8722;0,707; 0) noktasında minimumdur.",
        css_class=WIDE,
        aria="Two square panels over -2..2 squared. Left: contour lines of z = x exp(-x^2 - y^2) at levels "
             "-0.35 to 0.35, closed ovals around the maximum near (0.71, 0) and dashed ovals around the "
             "minimum near (-0.71, 0), each labelled with its value. Right: the same bands filled, red "
             "shades for positive and blue shades for negative values, with a colour bar from -0.45 to "
             "0.45"))


# ============================================================
# yuzey: the surface z = x exp(-x^2 - y^2) on a 21 x 21 grid
# ============================================================
def fig_surface():
    x = np.linspace(-2, 2, 21)
    X, Y = np.meshgrid(x, x)
    Z = X * np.exp(-X**2 - Y**2)
    assert Z.shape == (21, 21) and f"{Z.min():.4f}, {Z.max():.4f}" == "-0.4218, 0.4218"
    ZS = 3.3                                    # vertical stretch of Matplotlib's 4:4:3 box
    zf = -0.45 * ZS
    cam = Camera(azimuth=-60, elevation=25)
    corners = [(a, b, c) for a in (-2, 2) for b in (-2, 2) for c in (zf, 0.45 * ZS)]
    pr = [cam.project(P) for P in corners]
    xs, ys = [q[0] for q in pr], [q[1] for q in pr]
    pad = 0.35
    tick = 12                                   # the figure sits in the narrow column
    p = space_panel(40, 20, 430, (min(xs) - pad, max(xs) + pad),
                    (min(ys) - pad, max(ys) + pad))
    sp = Space(p, cam)
    # floor grid and the z axis on the back right edge
    for v in (-2, -1, 0, 1, 2):
        sp.line([(v, -2, zf), (v, 2, zf)], TEXT, 0.8, None, 0.2)
        sp.line([(-2, v, zf), (2, v, zf)], TEXT, 0.8, None, 0.2)
    sp.line([(2, 2, zf), (2, 2, 0.45 * ZS)], TEXT, 1.0, None, 0.55)
    for zv in (-0.4, -0.2, 0, 0.2, 0.4):
        sp.line([(2, 2, zv * ZS), (2, 2.12, zv * ZS)], TEXT, 1.0, None, 0.6)
        sp.label((2, 2, zv * ZS), dec(zv), 12, 4, TEXT, tick, "start")
    sp.label((2, 2, 0.45 * ZS), it("z"), 0, -8, TEXT, 13, "middle")
    # faces, back to front, each on an opaque underlay so that hidden faces stay hidden
    faces = []
    for i in range(20):
        for j in range(20):
            quad = [(X[i, j], Y[i, j], Z[i, j]), (X[i, j + 1], Y[i, j + 1], Z[i, j + 1]),
                    (X[i + 1, j + 1], Y[i + 1, j + 1], Z[i + 1, j + 1]), (X[i + 1, j], Y[i + 1, j], Z[i + 1, j])]
            zc = sum(q[2] for q in quad) / 4
            quad = [(a, b, c * ZS) for a, b, c in quad]
            dep = sum(cam.project(q)[2] for q in quad) / 4
            faces.append((dep, quad, zc))
    faces.sort(key=lambda f: f[0])
    zmax = float(Z.max())
    p.add(f'<g stroke="{TEXT}" stroke-width="0.4" stroke-opacity="0.55" stroke-linejoin="round">')
    for _, quad, zc in faces:
        pts = " ".join(p.P(*sp.pt(q)) for q in quad)
        t = min(abs(zc) / zmax, 1.0)
        color = PRACTICE if zc > 0 else THEORY
        p.add(f'<polygon points="{pts}" fill="{BG}"/>')
        p.add(f'<polygon points="{pts}" fill="{color}" fill-opacity="{0.06 + 0.8 * t:.2f}"/>')
    p.add('</g>')
    # tick labels on the two front edges of the floor
    for v in (-2, -1, 0, 1, 2):
        sp.line([(v, -2, zf), (v, -2.12, zf)], TEXT, 1.0, None, 0.6)
        sp.label((v, -2, zf), dec(v), -6, 16, TEXT, tick, "middle")
        sp.line([(2, v, zf), (2.12, v, zf)], TEXT, 1.0, None, 0.6)
        sp.label((2, v, zf), dec(v), 12, 12, TEXT, tick, "start")
    sp.label((0, -2, zf), it("x"), -22, 36, TEXT, 13, "middle")
    sp.label((2, 0, zf), it("y"), 34, 30, TEXT, 13, "middle")
    W = int(p.x0 + p.w + 40)
    H = int(p.y0 + p.h + 20)
    save("yuzey", figure(
        W, H, [p],
        "Yüzey örneğindeki kodun çizdiği grafik: <em>z</em> = <em>x</em><em>e</em><sup>&#8722;<em>x</em>² "
        "&#8722; <em>y</em>²</sup> yüzeyi 21 × 21'lik ızgaranın 400 dörtgeniyle, yükseklik pozitifken kırmızı, "
        "negatifken mavi tonlarla. Ön sağda tepe, arka solda çukur görünür; kaba ızgara yüzünden tepe hafifçe "
        "düzleşmiştir.",
        aria="A 3D surface z = x exp(-x^2 - y^2) over -2..2 squared, drawn as 400 quadrilaterals seen from "
             "azimuth -60 and elevation 25 degrees, a red hump near (0.7, 0) and a blue pit near (-0.7, 0), "
             "with a floor grid and z ticks from -0.4 to 0.4"))


if __name__ == "__main__":
    fig_first_plot()
    fig_taylor()
    fig_tangent()
    fig_param_polar()
    fig_eigen_scatter()
    fig_semicircle()
    fig_contour()
    fig_surface()
