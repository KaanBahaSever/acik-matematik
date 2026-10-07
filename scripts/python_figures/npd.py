# -*- coding: utf-8 -*-
"""
Figures of the chapter "NumPy Dizileri"
(dersler/python-bilimsel/numpy-dizileri.qmd).

Figures go INSIDE the box they explain (theorem, example, exercise or
callout), never inside a definition box, never inside a collapsed
.cozum/.ispat block when they carry the concept, and never directly under a
heading. The figures are NOT produced at build time. Run (with the course
venv, since the data is computed with NumPy exactly as in the chapter code)

    set OPENBLAS_NUM_THREADS=1
    python scripts/python_figures/npd.py
    python scripts/center_figures.py "python-npd-*.md"
    python scripts/check_figure_labels.py "scripts/_figures/python-npd-*.md"

and paste the markup of scripts/_figures/python-npd-<name>.md into the .qmd.
Captions are Turkish on purpose; aria labels are plain ASCII.

Most figures here are diagrams of memory and index sets, drawn on a canvas
whose data coordinates are pixels (y grows downward).
"""
import os
import sys
from pathlib import Path

os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
import numpy as np  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import (Plot, figure, TEXT, THEORY, PRACTICE, BASE,  # noqa: E402
                      REMARK, BG)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "python-npd-"

MINUS = "&#8722;"
TIMES = "&#215;"
CDOT = "&#183;"


def save(name, markup):
    (OUT_DIR / f"{PREFIX}{name}.md").write_text(markup, encoding="utf-8",
                                                newline="\n")
    print(f"{PREFIX}{name}.md")


def canvas(W, H):
    """A panel whose data coordinates are the pixel coordinates."""
    return Plot(0, 0, W, H, (0, W), (H, 0))


def dec(v, digits=2):
    """Decimal comma and a true minus sign: -0.5 -> '−0,5'."""
    s = f"{v:.{digits}f}".rstrip("0").rstrip(".")
    if s in ("-0", ""):
        s = "0"
    return s.replace(".", ",").replace("-", MINUS)


def one_decimal(v):
    """Float with one decimal as Python prints it, decimal comma: 1.0 -> '1,0'."""
    return f"{v:.1f}".replace(".", ",").replace("-", MINUS)


def num(v):
    """Integer label with a true minus sign."""
    return str(int(v)).replace("-", MINUS)


def rect(p, x, y, w, h, fill="none", opacity=0.0, stroke=TEXT,
         stroke_op=0.55, width=1.0, dash=None):
    da = f' stroke-dasharray="{dash}"' if dash else ""
    p.add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
          f'fill="{fill}" fill-opacity="{opacity}" stroke="{stroke}" '
          f'stroke-opacity="{stroke_op}" stroke-width="{width}"{da}/>')


def cell(p, x, y, w, h, label, fill="none", opacity=0.0, bold=False,
         color=TEXT, size=12.5):
    rect(p, x, y, w, h, fill, opacity)
    p.text_px(x + w / 2, y + h / 2 + size * 0.36, label, color, size,
              "middle", bold)


def strip(p, x, y, w, h, labels, fills=None, bold=None, size=12.5):
    """A row of cells; fills[k] = (color, opacity) or None."""
    for k, s in enumerate(labels):
        f = fills[k] if fills else None
        b = bold[k] if bold else False
        if f:
            cell(p, x + k * w, y, w, h, s, f[0], f[1], b, size=size)
        else:
            cell(p, x + k * w, y, w, h, s, bold=b, size=size)


def grid(p, x, y, w, h, M, fills=None, bold=None, size=12.5):
    """A matrix of cells; M is a 2D array of labels."""
    for i in range(M.shape[0]):
        strip(p, x, y + i * h, w, h, list(M[i]),
              None if fills is None else list(fills[i]),
              None if bold is None else list(bold[i]), size)


def same(shape, value):
    """Object array of the given shape filled with one (color, opacity)."""
    f = np.empty(shape, dtype=object)
    for ij in np.ndindex(*shape):
        f[ij] = value
    return f


def hline_arrow(p, x0, x1, y, color=TEXT, width=1.3, opacity=0.8):
    p.arrow((x0, y), (x1, y), color, width, 7.0, None, opacity)


def bracket(p, x0, x1, y, color=TEXT, tick=5, opacity=0.7, down=True):
    s = tick if down else -tick
    p.add(f'<path d="M{x0:.1f},{y - s:.1f} L{x0:.1f},{y:.1f} L{x1:.1f},'
          f'{y:.1f} L{x1:.1f},{y - s:.1f}" fill="none" stroke="{color}" '
          f'stroke-width="1.3" opacity="{opacity}"/>')


# ============================================================
# A Python list of float objects versus a float64 array
# ============================================================
def fig_list_vs_array():
    W, H = 560, 350
    p = canvas(W, H)
    values = [k / 2 for k in range(5)]          # as in the chapter code
    arr = np.array(values)

    # --- list: table of addresses, objects scattered in memory
    p.text_px(30, 26, "Python listesi", TEXT, 12.5, "start", True)
    cw, ch, tx, ty = 40, 30, 30, 40
    for k in range(5):
        rect(p, tx + k * cw, ty, cw, ch)
    p.text_px(tx + 5 * cw + 10, ty + 20, "adres tablosu", TEXT, 11)
    # (x, y) of the object boxes, deliberately out of order
    spots = [(250, 150), (40, 190), (400, 110), (140, 128), (330, 200)]
    ow, oh = 76, 30
    for k, (bx, by) in enumerate(spots):
        cx, cy = tx + k * cw + cw / 2, ty + ch / 2
        p.add(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="3.2" fill="{TEXT}"/>')
        p.arrow((cx, cy + 4), (bx + ow / 2, by - 2), THEORY, 1.3, 7.0)
        # header part (type, reference count) and value part
        rect(p, bx, by, 26, oh, REMARK, 0.22)
        rect(p, bx + 26, by, ow - 26, oh, THEORY, 0.10)
        p.text_px(bx + 13, by + oh / 2 + 4, "tür", TEXT, 11, "middle")
        p.text_px(bx + 26 + (ow - 26) / 2, by + oh / 2 + 4.5,
                  one_decimal(values[k]), TEXT, 12.5, "middle", True)
    p.text_px(530, 252, "her eleman ayrı bir float nesnesi", TEXT, 11,
              "end")

    # --- array: header plus one contiguous block
    y0 = 270
    p.text_px(30, y0, "NumPy dizisi", TEXT, 12.5, "start", True)
    hx, hy, hw, hh = 30, y0 + 14, 120, 54
    rect(p, hx, hy, hw, hh, REMARK, 0.12)
    p.text_px(hx + 8, hy + 16, f"dtype: {arr.dtype}", TEXT, 11)
    p.text_px(hx + 8, hy + 31, f"shape: ({arr.shape[0]},)", TEXT, 11)
    p.text_px(hx + 8, hy + 46, f"strides: ({arr.strides[0]},)", TEXT, 11)
    bx, bw = 200, 64
    by = hy + 6
    p.arrow((hx + hw + 4, by + 21), (bx - 4, by + 21), THEORY, 1.3, 7.0)
    strip(p, bx, by, bw, 32, [one_decimal(v) for v in arr],
          [(BASE, 0.14)] * 5, [True] * 5)
    for k in range(5):
        p.text_px(bx + k * bw, by + 47, str(k * arr.itemsize), TEXT, 11,
                  "middle")
    p.text_px(bx + 5 * bw, by + 47, str(arr.nbytes), TEXT, 11, "middle")
    p.text_px(bx + 5 * bw + 12, by + 22, "bayt", TEXT, 11)
    save("liste-dizi", figure(
        W, H + 10, [p],
        "Aynı beş sayı (0,0; 0,5; 1,0; 1,5 ve 2,0) iki biçimde. Üstte "
        "Python listesi: her eleman bellekte başka bir yerde duran, kendi "
        "tür ve sayaç bilgisini taşıyan bir <code>float</code> nesnesidir; "
        "liste yalnız bu nesnelerin adreslerini tutar. Altta "
        "<code>float64</code> dizisi: sayılar 8'er baytlık bitişik bir "
        "blokta yan yana durur; <code>dtype</code>, <code>shape</code> ve "
        "<code>strides</code> bu bloğun nasıl okunacağını söyler.",
        aria="Top: a Python list as a table of five addresses whose arrows "
             "point to five float objects scattered in memory, each with a "
             "type header and a value 0.0, 0.5, 1.0, 1.5, 2.0. Bottom: a "
             "NumPy array header with dtype float64, shape (5,), strides "
             "(8,) pointing to one contiguous block of the same five values "
             "at byte offsets 0, 8, 16, 24, 32."))


# ============================================================
# linspace versus arange, and the floating step pitfall
# ============================================================
def fig_grids():
    W, H = 540, 270
    p = canvas(W, H)
    L, R = 50, 490

    def line(y, a, b, ticks):
        X = lambda t: L + (t - a) / (b - a) * (R - L)  # noqa: E731
        p.add(f'<line x1="{L - 12}" y1="{y}" x2="{R + 12}" y2="{y}" '
              f'stroke="{TEXT}" stroke-width="1.1" opacity="0.5"/>')
        for t in ticks:
            p.add(f'<line x1="{X(t):.1f}" y1="{y - 4}" x2="{X(t):.1f}" '
                  f'y2="{y + 4}" stroke="{TEXT}" stroke-width="1" '
                  f'opacity="0.6"/>')
            p.text_px(X(t), y + 22, dec(t), TEXT, 11, "middle")
        return X

    # row 1: linspace(0, 1, 5), both ends included
    y = 50
    pts = np.linspace(0, 1, 5)
    p.text_px(L - 12, y - 20, "np.linspace(0, 1, 5)", TEXT, 12, "start",
              True)
    p.text_px(R + 12, y - 20, f"{pts.size} nokta, 1 dahil", THEORY, 11.5,
              "end")
    X = line(y, 0, 1, pts)
    for t in pts:
        p.add(f'<circle cx="{X(t):.1f}" cy="{y}" r="5" fill="{THEORY}"/>')

    # row 2: arange(0, 1, 0.25), the end point is excluded
    y = 135
    pts = np.arange(0, 1, 0.25)
    p.text_px(L - 12, y - 20, "np.arange(0, 1, 0.25)", TEXT, 12, "start",
              True)
    p.text_px(R + 12, y - 20, f"{pts.size} nokta, 1 dahil değil", BASE,
              11.5, "end")
    X = line(y, 0, 1, np.linspace(0, 1, 5))
    for t in pts:
        p.add(f'<circle cx="{X(t):.1f}" cy="{y}" r="5" fill="{BASE}"/>')
    p.add(f'<circle cx="{X(1):.1f}" cy="{y}" r="5" fill="{BG}" '
          f'stroke="{BASE}" stroke-width="1.6"/>')

    # row 3: arange(1, 1.3, 0.1) produces a fourth point beyond 1.3
    y = 220
    pts = np.arange(1, 1.3, 0.1)
    p.text_px(L - 12, y - 20, "np.arange(1, 1.3, 0.1)", TEXT, 12, "start",
              True)
    p.text_px(R + 12, y - 20, f"{pts.size} nokta, sonuncusu "
              f"{dec(pts[-1], 16)}", PRACTICE, 11.5, "end")
    X = line(y, 1, 1.3, [1, 1.1, 1.2, 1.3])
    for t in pts[:-1]:
        p.add(f'<circle cx="{X(t):.1f}" cy="{y}" r="5" fill="{BASE}"/>')
    p.add(f'<circle cx="{X(pts[-1]):.1f}" cy="{y}" r="5" '
          f'fill="{PRACTICE}"/>')
    save("aralik", figure(
        W, H, [p],
        "Üstte <code>linspace</code> nokta sayısıyla çalışır ve iki ucu da "
        "alır. Ortada <code>arange</code> aynı adımla 1'e varmadan durur. "
        "Altta ondalık adımlı <code>arange</code>: eleman sayısı "
        "(1,3 &#8722; 1)/0,1 oranının yukarı yuvarlanmasıyla belirlenir; bu "
        "oran yuvarlama hatası yüzünden 3 değil 3,0000000000000004 çıktığı "
        "için dördüncü bir nokta eklenir ve o nokta 1,3'ün biraz "
        "sağındadır.",
        aria="Three number lines. linspace(0, 1, 5) gives five points 0, "
             "0.25, 0.5, 0.75, 1. arange(0, 1, 0.25) gives four points and "
             "1 is an open circle. arange(1, 1.3, 0.1) gives 1, 1.1, 1.2 "
             "and an unexpected fourth point 1.3000000000000003."))


# ============================================================
# Row-major memory layout of a 3 x 4 array and its strides
# ============================================================
def fig_memory():
    W, H = 560, 320
    p = canvas(W, H)
    A = np.arange(12).reshape(3, 4)
    colors = [THEORY, BASE, PRACTICE]
    i, j = 2, 1
    flat = A.ravel()

    # memory strip
    sx, sy, cw, ch = 40, 36, 40, 32
    p.text_px(sx, 24, f"bellekteki blok: {A.size} {TIMES} {A.itemsize} "
              f"bayt", TEXT, 12, "start", True)
    for k, v in enumerate(flat):
        r = k // A.shape[1]
        cell(p, sx + k * cw, sy, cw, ch, str(v), colors[r], 0.16,
             bold=(k == i * A.shape[1] + j))
        p.text_px(sx + k * cw + cw / 2, sy + ch + 16, str(k * A.itemsize),
                  TEXT, 10.5, "middle")
    for r in range(3):
        x0 = sx + r * 4 * cw + 3
        x1 = sx + (r + 1) * 4 * cw - 3
        bracket(p, x0, x1, sy + ch + 26, colors[r], 5, 0.9, down=True)
        p.text_px((x0 + x1) / 2, sy + ch + 42, f"satır {r}", colors[r], 11.5,
                  "middle", True)
    k9 = i * A.shape[1] + j
    rect(p, sx + k9 * cw, sy, cw, ch, "none", 0, PRACTICE, 1, 2.4)

    # the same block read as a 3 x 4 matrix
    gx, gy = 220, 168
    p.text_px(gx + 2 * cw, gy - 14, "A = np.arange(12).reshape(3, 4)", TEXT,
              12, "middle", True)
    for r in range(3):
        for c in range(4):
            cell(p, gx + c * cw, gy + r * ch, cw, ch, str(A[r, c]),
                 colors[r], 0.16, bold=(r == i and c == j))
    rect(p, gx + j * cw, gy + i * ch, cw, ch, "none", 0, PRACTICE, 1, 2.4)
    # axis 0 (down) and axis 1 (right)
    p.arrow((gx - 14, gy), (gx - 14, gy + 3 * ch), TEXT, 1.3, 7.0, None,
            0.8)
    p.text_px(gx - 22, gy + 1.5 * ch - 4, "eksen 0", TEXT, 11.5, "end",
              True)
    p.text_px(gx - 22, gy + 1.5 * ch + 12, f"+{A.strides[0]} bayt", TEXT,
              11, "end")
    hline_arrow(p, gx, gx + 4 * cw, gy + 3 * ch + 14)
    p.text_px(gx + 2 * cw, gy + 3 * ch + 32,
              f"eksen 1: +{A.strides[1]} bayt", TEXT, 11.5, "middle", True)
    off = i * A.strides[0] + j * A.strides[1]
    p.text_px(gx + 4 * cw + 16, gy + 2 * ch + 4, f"A[{i}, {j}] = {A[i, j]}",
              PRACTICE, 12, "start", True)
    p.text_px(gx + 4 * cw + 16, gy + 2 * ch + 21,
              f"{i}{CDOT}{A.strides[0]} + {j}{CDOT}{A.strides[1]} = {off} "
              f"bayt", PRACTICE, 11)
    save("bellek", figure(
        W, H, [p],
        "<code>np.arange(12).reshape(3, 4)</code> dizisinin verisi bellekte "
        "tek bir bloktur; şekil yalnız bu bloğun nasıl okunacağını belirler. "
        "Satır öncelikli sırada önce 0. satırın dört elemanı, sonra 1. ve "
        "2. satırınkiler gelir. Bir sütun sağa gitmek 8, bir satır aşağı "
        "inmek 4 &#183; 8 = 32 bayt ilerlemektir; bu iki sayı dizinin "
        "<code>strides</code> değeridir ve <code>A[2, 1]</code> elemanı "
        "bloğun başından 2 &#183; 32 + 1 &#183; 8 = 72 bayt ötede başlar.",
        aria="Top: a strip of twelve cells 0 to 11 with byte offsets 0 to 88,"
             " grouped by brackets into row 0, row 1, row 2. Bottom: the same"
             " values as a 3 by 4 grid with an arrow down labeled axis 0 "
             "plus 32 bytes and an arrow right labeled axis 1 plus 8 bytes;"
             " element A[2, 1] = 9 is highlighted in both and sits at byte "
             "72."))


# ============================================================
# Four slices of A = np.arange(20).reshape(4, 5)
# ============================================================
def fig_slices():
    A = np.arange(20).reshape(4, 5)
    idx = np.arange(20).reshape(4, 5)
    cases = [("A[1]", lambda M: M[1]),
             ("A[:, 2]", lambda M: M[:, 2]),
             ("A[1:3, 1:4]", lambda M: M[1:3, 1:4]),
             ("A[::2, ::2]", lambda M: M[::2, ::2])]
    cw, ch = 30, 26
    pw, ph = 5 * cw, 4 * ch
    W, H = 2 * pw + 90, 2 * (ph + 70) + 10
    p = canvas(W, H)
    for n, (title, sl) in enumerate(cases):
        px = 30 + (n % 2) * (pw + 40)
        py = 34 + (n // 2) * (ph + 70)
        chosen = set(np.ravel(sl(idx)).tolist())
        shape = sl(A).shape
        fills = np.empty((4, 5), dtype=object)
        bold = np.zeros((4, 5), dtype=bool)
        for r in range(4):
            for c in range(5):
                on = idx[r, c] in chosen
                fills[r, c] = (THEORY, 0.30) if on else None
                bold[r, c] = on
        grid(p, px, py, cw, ch, A.astype(str), fills, bold, 12)
        p.text_px(px + pw / 2, py - 10, title, THEORY, 12.5, "middle", True)
        sh = "(" + ", ".join(str(s) for s in shape) + \
             ("," if len(shape) == 1 else "") + ")"
        p.text_px(px + pw / 2, py + ph + 19, f"şekil {sh}", TEXT, 11.5,
                  "middle")
    save("dilim", figure(
        W, H, [p],
        "<code>A = np.arange(20).reshape(4, 5)</code> dizisinden dört seçim. "
        "Tek bir tamsayı indeks (<code>A[1]</code>, <code>A[:, 2]</code>) o "
        "ekseni ortadan kaldırır ve bir boyutlu bir dizi verir; dilimler "
        "eksenleri korur. <code>A[::2, ::2]</code> her iki eksende ikişer "
        "atlayarak seçer.",
        aria="Four copies of the 4 by 5 grid holding 0 to 19 with the "
             "selected cells shaded: A[1] the second row, shape (5,); "
             "A[:, 2] the third column, shape (4,); A[1:3, 1:4] the block "
             "6 7 8 / 11 12 13, shape (2, 3); A[::2, ::2] the cells 0 2 4 / "
             "10 12 14, shape (2, 3)."))


# ============================================================
# A view shares memory, a copy does not
# ============================================================
def fig_view_copy():
    W, H = 540, 250
    p = canvas(W, H)
    a = np.arange(6)
    s = a[1:4]
    c = a[1:4].copy()
    cw, ch = 50, 32
    ax, ay = 180, 96
    p.text_px(ax - 14, ay + 21, "a = np.arange(6)", TEXT, 12, "end", True)
    fills = [None] * 6
    for k in range(1, 4):
        fills[k] = (THEORY, 0.22)
    strip(p, ax, ay, cw, ch, [str(v) for v in a], fills)
    for k in range(6):
        p.text_px(ax + k * cw + cw / 2, ay - 8, str(k), TEXT, 10.5, "middle")
    # the view: a bracket over the shared cells
    x0, x1 = ax + cw + 3, ax + 4 * cw - 3
    bracket(p, x0, x1, ay - 22, THEORY, 6, 1.0, down=False)
    p.text_px((x0 + x1) / 2, ay - 34, "s = a[1:4]: görünüm, aynı bellek",
              THEORY, 12, "middle", True)
    # the copy: a new block
    cx, cy = ax + cw, 196
    strip(p, cx, cy, cw, ch, [str(v) for v in c], [(PRACTICE, 0.18)] * 3)
    p.text_px(cx - 14, cy + 21, "c = a[1:4].copy()", TEXT, 12, "end", True)
    p.text_px(cx + 3 * cw + 14, cy + 21, "kopya: yeni bellek", PRACTICE, 12,
              "start", True)
    for k in range(3):
        xm = cx + k * cw + cw / 2
        p.arrow((xm, ay + ch + 4), (xm, cy - 4), PRACTICE, 1.3, 7.0, "4 3")
    assert np.shares_memory(a, s) and not np.shares_memory(a, c)
    save("gorunum", figure(
        W, H, [p],
        "<code>s = a[1:4]</code> kendi verisi olmayan bir görünümdür: "
        "<code>a</code>'nın 1, 2 ve 3 numaralı hücrelerine bakar, bu yüzden "
        "<code>s[0] = 100</code> ataması <code>a[1]</code>'i değiştirir. "
        "<code>c = a[1:4].copy()</code> ise aynı değerleri yeni bir bloğa "
        "yazar; <code>c</code> üzerinde yapılan değişiklik <code>a</code>'ya "
        "ulaşmaz.",
        aria="An array a with cells 0 to 5. A bracket over cells 1 to 3 "
             "labeled s = a[1:4], view, same memory. Dashed arrows copy "
             "the values 1, 2, 3 down into a separate block labeled c = "
             "a[1:4].copy(), copy, new memory."))


# ============================================================
# Fancy indexing: x[idx] with a repeated index
# ============================================================
def fig_fancy():
    W, H = 600, 250
    p = canvas(W, H)
    x = np.array([10, 20, 30, 40, 50])
    idx = np.array([3, 0, 3, 1])
    y = x[idx]
    cw, ch = 72, 32
    xx, xy = 140, 50
    p.text_px(xx - 14, xy + 21, "x", TEXT, 13, "end", True)
    strip(p, xx, xy, cw, ch, [str(v) for v in x], [(BASE, 0.14)] * 5)
    for k in range(5):
        p.text_px(xx + k * cw + cw / 2, xy - 8, str(k), TEXT, 10.5, "middle")
    p.text_px(xx + 5 * cw + 12, xy - 8, "konum", TEXT, 10.5)
    rx, ry = xx + cw / 2, 170
    p.text_px(rx - 14, ry + 21, "x[idx]", TEXT, 13, "end", True)
    strip(p, rx, ry, cw, ch, [str(v) for v in y], [(THEORY, 0.20)] * 4,
          [True] * 4)
    for k, t in enumerate(idx):
        p.text_px(rx + k * cw + cw / 2, ry + ch + 18, str(t), THEORY, 11.5,
                  "middle", True)
        p.arrow((xx + t * cw + cw / 2, xy + ch + 3),
                (rx + k * cw + cw / 2, ry - 4), THEORY, 1.4, 7.0)
    p.text_px(rx - 14, ry + ch + 18, "idx", THEORY, 11.5, "end", True)
    save("fancy", figure(
        W, H, [p],
        "<code>x[idx]</code> ile <code>idx = [3, 0, 3, 1]</code>: sonucun "
        "<em>k</em>-ıncı elemanı <code>x[idx[k]]</code>'dir. İndeksler "
        "istenen sırada verilebilir ve tekrar edebilir; 3 numaralı konum iki "
        "kez seçilmiştir. Sonuç, <code>x</code>'ten bağımsız yeni bir "
        "dizidir.",
        aria="Array x = 10 20 30 40 50 with positions 0 to 4. Arrows go from "
             "positions 3, 0, 3, 1 down to the four cells of x[idx] = 40 10 "
             "40 20, with idx written under them; position 3 sends two "
             "arrows."))


# ============================================================
# Sieve of Eratosthenes on a boolean array, read as 10 x 10
# ============================================================
def fig_sieve():
    N = 100
    is_prime = np.ones(N + 1, dtype=bool)
    is_prime[:2] = False
    for q in range(2, int(N**0.5) + 1):
        if is_prime[q]:
            is_prime[q * q::q] = False
    assert is_prime.sum() == 25
    nums = np.arange(1, N + 1).reshape(10, 10)
    mask = is_prime[1:].reshape(10, 10)
    cw, ch = 34, 28
    W, H = 10 * cw + 40, 10 * ch + 40
    p = canvas(W, H)
    fills = np.empty((10, 10), dtype=object)
    for r in range(10):
        for c in range(10):
            fills[r, c] = (PRACTICE, 0.26) if mask[r, c] else None
    grid(p, 20, 20, cw, ch, nums.astype(str), fills, mask, 12)
    save("kalbur", figure(
        W, H, [p],
        "Kalburdan sonra <code>is_prime[1:].reshape(10, 10)</code> maskesi: "
        "1'den 100'e kadar sayılar satır satır dizilmiş, maskenin "
        "<code>True</code> olduğu 25 asal vurgulanmıştır. 2 ve 5 dışındaki "
        "asalların hepsi 1, 3, 7 ya da 9 ile biten sütunlarda durur.",
        aria="A 10 by 10 grid with the numbers 1 to 100 row by row; the 25 "
             "primes 2 3 5 7 11 ... 97 are shaded and bold."))


# ============================================================
# Stacking: vstack and hstack of two 2 x 3 arrays
# ============================================================
def fig_stack():
    A = np.array([[1, 2, 3], [4, 5, 6]])
    B = np.array([[7, 8, 9], [10, 11, 12]])
    V = np.vstack([A, B])
    Hs = np.hstack([A, B])
    cw, ch = 40, 30
    W, H = 580, 340
    p = canvas(W, H)
    fa, fb = (THEORY, 0.20), (PRACTICE, 0.20)

    def fills_of(M, top_rows=None, left_cols=None):
        f = np.empty(M.shape, dtype=object)
        for r in range(M.shape[0]):
            for c in range(M.shape[1]):
                inA = (r < top_rows) if top_rows else (c < left_cols)
                f[r, c] = fa if inA else fb
        return f

    # inputs
    ax, bx, iy = 150, 330, 40
    grid(p, ax, iy, cw, ch, A.astype(str), same(A.shape, fa))
    grid(p, bx, iy, cw, ch, B.astype(str), same(B.shape, fb))
    p.text_px(ax + 1.5 * cw, iy - 10, "A", THEORY, 13, "middle", True)
    p.text_px(bx + 1.5 * cw, iy - 10, "B", PRACTICE, 13, "middle", True)

    # vstack
    vx, vy = 60, 170
    grid(p, vx, vy, cw, ch, V.astype(str), fills_of(V, top_rows=2))
    p.text_px(vx + 1.5 * cw, vy - 12, "np.vstack([A, B])", TEXT, 12,
              "middle", True)
    p.text_px(vx + 1.5 * cw, vy + 4 * ch + 18,
              f"şekil ({V.shape[0]}, {V.shape[1]})", TEXT, 11.5, "middle")
    p.arrow((vx + 3 * cw + 14, vy), (vx + 3 * cw + 14, vy + 4 * ch), TEXT,
            1.3, 7.0, None, 0.8)
    p.text_px(vx + 3 * cw + 22, vy + 2 * ch + 4, "eksen 0", TEXT, 11.5)

    # hstack
    hx, hy = 290, 170
    grid(p, hx, hy, cw, ch, Hs.astype(str), fills_of(Hs, left_cols=3))
    p.text_px(hx + 3 * cw, hy - 12, "np.hstack([A, B])", TEXT, 12,
              "middle", True)
    hline_arrow(p, hx, hx + 6 * cw, hy + 2 * ch + 14)
    p.text_px(hx + 3 * cw, hy + 2 * ch + 32, "eksen 1", TEXT, 11.5,
              "middle")
    p.text_px(hx + 3 * cw, hy + 2 * ch + 52,
              f"şekil ({Hs.shape[0]}, {Hs.shape[1]})", TEXT, 11.5, "middle")
    save("yigma", figure(
        W, H, [p],
        "İki 2 &#215; 3 dizi. <code>np.vstack</code> onları 0 ekseni "
        "boyunca alt alta koyar ve 4 &#215; 3 bir dizi verir; "
        "<code>np.hstack</code> 1 ekseni boyunca yan yana koyar ve "
        "2 &#215; 6 bir dizi verir. Birleştirilen eksen dışındaki "
        "uzunluklar aynı olmalıdır.",
        aria="Two 2 by 3 arrays A = 1..6 and B = 7..12. Below left, "
             "np.vstack([A, B]) is a 4 by 3 grid with A on top of B and an "
             "arrow down labeled axis 0; below right, np.hstack([A, B]) is a "
             "2 by 6 grid with A left of B and an arrow right labeled axis "
             "1."))


if __name__ == "__main__":
    fig_list_vs_array()
    fig_grids()
    fig_memory()
    fig_slices()
    fig_view_copy()
    fig_fancy()
    fig_sieve()
    fig_stack()
