# -*- coding: utf-8 -*-
"""
Figures of the chapter "Sınıflar, Hata Yakalama ve Dosyalar"
(dersler/python-bilimsel/siniflar-hatalar-ve-dosyalar.qmd).

Figures go INSIDE the box they explain (theorem, example, solution or
callout), never inside a definition box (right below it instead) and never
directly under a heading. In this book concept figures must stay visible, so
they are not put inside a collapsed .cozum/.ispat block. The figures are NOT
produced at build time. Run

    python scripts/python_figures/snf.py
    python scripts/center_figures.py "python-snf-*.md"
    python scripts/check_figure_labels.py "scripts/_figures/python-snf-*.md"

and paste the markup of scripts/_figures/python-snf-<name>.md into the .qmd.
Captions are Turkish on purpose; aria labels are plain ASCII.

The data drawn here is recomputed exactly as in the code blocks of the
chapter (the exception hierarchy from __mro__, the vector operations, the
Newton iterates, the parsed CSV rows and the estimated cooling constant), so
the figures agree with the printed outputs.
"""
import csv
import html
import io
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import (Plot, figure, TEXT, THEORY, PRACTICE, BASE,  # noqa: E402
                      REMARK, BG, WIDE)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "python-snf-"

MINUS = "&#8722;"
HELLIP = "&#8230;"


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


def esc(s):
    """Escape code text for an SVG <text> body."""
    return html.escape(s, quote=False)


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


def box(p, cx, cy, w, h, color, fill_op=0.10, rx=6, width=1.5, dash=None):
    da = f' stroke-dasharray="{dash}"' if dash else ""
    p.add(f'<rect x="{cx - w / 2:.1f}" y="{cy - h / 2:.1f}" width="{w:.1f}" height="{h:.1f}" '
          f'rx="{rx}" fill="{color}" fill-opacity="{fill_op}" stroke="{color}" '
          f'stroke-width="{width}"{da}/>')


def xtick(p, v, s, size=11):
    p.add(f'<line x1="{p.X(v):.1f}" y1="{p.y0 + p.h:.1f}" x2="{p.X(v):.1f}" y2="{p.y0 + p.h + 4:.1f}" '
          f'stroke="{TEXT}" opacity="0.6"/>')
    p.text_px(p.X(v), p.y0 + p.h + 17, s, TEXT, size, "middle")


def ytick(p, v, s, size=11):
    p.add(f'<line x1="{p.x0 - 4:.1f}" y1="{p.Y(v):.1f}" x2="{p.x0:.1f}" y2="{p.Y(v):.1f}" '
          f'stroke="{TEXT}" opacity="0.6"/>')
    p.text_px(p.x0 - 7, p.Y(v) + 4, s, TEXT, size, "end")


# ============================================================
# 1. Names bound by "import numtools" and "from numtools import is_prime"
# ============================================================
def fig_namespaces():
    # same computation as 05_numtools_kullan.py
    def is_prime(n):
        if n < 2:
            return False
        d = 2
        while d * d <= n:
            if n % d == 0:
                return False
            d += 1
        return True
    twins = [(p, p + 2) for p in range(3, 80) if is_prime(p) and is_prime(p + 2)]
    assert twins[0] == (3, 5) and twins[-1] == (71, 73) and len(twins) == 8

    W, H = 640, 262
    p = pixel_plot(W, H)
    lx, rx = 100, 540                 # centres of the two columns
    y_mod, y_fn, y_tw = 72, 150, 222  # rows of the three names
    # left: the program's names
    box(p, lx, 140, 170, 210, TEXT, 0.04, rx=10, width=1.2)
    p.label(lx, 26, "programın adları", 0, 0, TEXT, 12.5, "middle", True)
    for y, s in ((y_mod, "numtools"), (y_fn, "is_prime"), (y_tw, "twins")):
        box(p, lx, y, 128, 30, THEORY, 0.12)
        p.label(lx, y, s, 0, 4.5, THEORY, 13, "middle", True)
    # right: the module object and the list object
    box(p, rx, 118, 170, 126, BASE, 0.06, rx=10, width=1.3)
    p.label(rx, 26, "numtools modülü", 0, 0, BASE, 12.5, "middle", True)
    for y, s in ((y_fn - 44, "gcd"), (y_fn, "is_prime")):
        box(p, rx, y, 128, 30, BASE, 0.14)
        p.label(rx, y, s, 0, 4.5, BASE, 13, "middle", True)
    box(p, rx, y_tw, 170, 32, PRACTICE, 0.08, rx=8, width=1.3)
    p.label(rx, y_tw, f"[(3, 5), {HELLIP}, (71, 73)]", 0, 4.5, PRACTICE, 12, "middle")
    # arrows
    x0, x1 = lx + 64, rx - 85
    p.arrow((x0, y_mod), (x1, y_mod), THEORY, 1.6, head=8)
    p.label((x0 + x1) / 2, y_mod, "import numtools", 0, -8, TEXT, 12, "middle")
    p.arrow((x0, y_fn), (rx - 64, y_fn), THEORY, 1.6, head=8)
    p.label((x0 + rx - 64) / 2, y_fn, "from numtools import is_prime", 0, -8, TEXT, 12, "middle")
    p.arrow((x0, y_tw), (x1, y_tw), THEORY, 1.6, head=8)
    p.label((x0 + x1) / 2, y_tw, "twins = [" + HELLIP + "]", 0, -8, TEXT, 12, "middle")
    cap = ("İkiz asalları bulan programdaki adlar ve bağlandıkları nesneler. <code>import numtools</code> "
           "programa yalnız <code>numtools</code> adını ekler; <code>gcd</code> fonksiyonuna "
           "<code>numtools.gcd</code> diye modülün içinden ulaşılır. <code>from numtools import is_prime</code> "
           "ise modüldeki fonksiyonu programın kendi adlarına <code>is_prime</code> adıyla bağlar.")
    aria = ("Left column: the program names numtools, is_prime and twins. Right column: the module numtools "
            "holding gcd and is_prime, and a list object. Arrows: numtools points to the whole module, "
            "is_prime points to the function inside the module, twins points to the list")
    save("ad-alanlari", figure(W, H, [p], cap, WIDE, aria))


# ============================================================
# 2. Order of the try / except / else / finally blocks
# ============================================================
def fig_try_flow():
    W, H = 600, 352
    p = pixel_plot(W, H)
    cx = 300
    bw, bh = 190, 38
    y_try, y_mid, y_fin, y_out = 50, 160, 252, 320
    xl, xr = 120, 480
    # try
    box(p, cx, y_try, bw, bh, THEORY, 0.10)
    p.label(cx, y_try, "try:  q = a / b", 0, 4.5, THEORY, 13, "middle", True)
    # else / except
    box(p, xl, y_mid, bw, bh + 8, BASE, 0.10)
    p.label(xl, y_mid, "else:", 0, -4, BASE, 13, "middle", True)
    p.label(xl, y_mid, "return q", 0, 13, BASE, 12, "middle")
    box(p, xr, y_mid, bw, bh + 8, PRACTICE, 0.10)
    p.label(xr, y_mid, "except ZeroDivisionError:", 0, -4, PRACTICE, 12.5, "middle", True)
    p.label(xr, y_mid, "return None", 0, 13, PRACTICE, 12, "middle")
    # finally
    box(p, cx, y_fin, bw, bh, REMARK, 0.10)
    p.label(cx, y_fin, "finally:", 0, 4.5, REMARK, 13, "middle", True)
    # branches from try
    p.arrow((cx - 40, y_try + bh / 2), (xl + 20, y_mid - bh / 2 - 4), BASE, 1.7, head=8)
    p.label(xl + 34, (y_try + y_mid) / 2, "istisna yok", 0, -4, BASE, 12, "end")
    p.label(xl + 34, (y_try + y_mid) / 2, "safe_ratio(7, 2)", 0, 11, BASE, 12, "end")
    p.arrow((cx + 40, y_try + bh / 2), (xr - 20, y_mid - bh / 2 - 4), PRACTICE, 1.7, head=8)
    p.label(xr - 34, (y_try + y_mid) / 2, "ZeroDivisionError", 0, -4, PRACTICE, 12)
    p.label(xr - 34, (y_try + y_mid) / 2, "safe_ratio(7, 0)", 0, 11, PRACTICE, 12)
    # other exceptions go straight to finally
    p.arrow((cx, y_try + bh / 2), (cx, y_fin - bh / 2), TEXT, 1.3, head=7, dash="5 4", opacity=0.75)
    plate_px(p, cx, (y_try + y_fin) / 2 + 4, "başka bir istisna", 12, "middle")
    p.label(cx, (y_try + y_fin) / 2, "başka bir istisna", 0, 4, TEXT, 12, "middle")
    # into finally
    p.arrow((xl + 20, y_mid + bh / 2 + 4), (cx - 60, y_fin - bh / 2), BASE, 1.7, head=8)
    p.arrow((xr - 20, y_mid + bh / 2 + 4), (cx + 60, y_fin - bh / 2), PRACTICE, 1.7, head=8)
    # exits
    p.arrow((cx - 50, y_fin + bh / 2), (cx - 120, y_out - 12), TEXT, 1.4, head=7)
    p.label(cx - 125, y_out, "değer döndürülür", 0, 4, TEXT, 12, "end")
    p.arrow((cx + 50, y_fin + bh / 2), (cx + 120, y_out - 12), TEXT, 1.3, head=7, dash="5 4", opacity=0.75)
    p.label(cx + 125, y_out, "istisna yukarı iletilir", 0, 4, TEXT, 12, "start")
    cap = ("<code>safe_ratio</code> fonksiyonunda blokların çalışma sırası. Önce <code>try</code> bloğu çalışır. "
           "İstisna çıkmazsa <code>else</code>, <code>ZeroDivisionError</code> çıkarsa <code>except</code> "
           "bloğu çalışır; başka türden bir istisna hiçbir <code>except</code> ile eşleşmez. Üç yolun hepsi "
           "<code>finally</code> bloğundan geçer: bu blok <code>return</code> deyiminden sonra bile çalışır.")
    aria = ("Flow chart: try block on top; if no exception the else block runs, if ZeroDivisionError the "
            "except block runs, any other exception goes straight down; all three paths pass through the "
            "finally block, after which a value is returned or the exception propagates")
    save("try-akisi", figure(W, H, [p], cap, "ders-grafik", aria))


# ============================================================
# 3. The exception hierarchy, built from __mro__ as in 10_istisna_soyu.py
# ============================================================
def fig_exception_tree():
    errors = [ZeroDivisionError, OverflowError, IndexError, KeyError, ValueError, TypeError]
    parent = {}
    for cls in errors:
        chain = list(reversed(cls.__mro__[:-1]))      # BaseException ... cls
        for a, b in zip(chain, chain[1:]):
            parent[b] = a
    # depth-first order of the tree rooted at BaseException
    children = {}
    for c, a in parent.items():
        children.setdefault(a, []).append(c)
    order = []

    def walk(c, depth):
        order.append((c, depth))
        for k in children.get(c, []):
            walk(k, depth + 1)
    walk(BaseException, 0)
    names = [c.__name__ for c, _ in order]
    assert names == ["BaseException", "Exception", "ArithmeticError", "ZeroDivisionError",
                     "OverflowError", "LookupError", "IndexError", "KeyError", "ValueError",
                     "TypeError"], names

    W, H = 470, 320
    p = pixel_plot(W, H)
    x0, y0, dy, ind = 24, 28, 29, 30
    pos = {}
    for i, (c, d) in enumerate(order):
        pos[c] = (x0 + d * ind, y0 + i * dy)
    # highlight the two subtrees caught by a parent class
    groups = ((ArithmeticError, PRACTICE, "except ArithmeticError"),
              (LookupError, THEORY, "except LookupError"))
    for cls, col, s in groups:
        rows = [cls] + children[cls]
        ys = [pos[c][1] for c in rows]
        xa = pos[cls][0] - 10
        p.add(f'<rect x="{xa:.1f}" y="{min(ys) - 15:.1f}" width="{448 - xa:.1f}" '
              f'height="{max(ys) - min(ys) + 28:.1f}" rx="8" fill="{col}" fill-opacity="0.08" '
              f'stroke="{col}" stroke-width="1.2" stroke-dasharray="5 3"/>')
        p.label(262, (min(ys) + max(ys)) / 2, s, 0, -3, col, 12, "start", True)
        p.label(262, (min(ys) + max(ys)) / 2, "bu türlerin hepsini yakalar", 0, 13, col, 11.5)
    # connectors
    for c, a in parent.items():
        (xa, ya), (xc, yc) = pos[a], pos[c]
        p.line([(xa + 8, ya + 8), (xa + 8, yc), (xc - 4, yc)], TEXT, 1.1, opacity=0.55)
    for c, d in order:
        x, y = pos[c]
        col = PRACTICE if c in (ArithmeticError, ZeroDivisionError, OverflowError) else \
            THEORY if c in (LookupError, IndexError, KeyError) else TEXT
        p.label(x, y, c.__name__, 0, 4.5, col, 12, "start", d <= 1 or c in (ArithmeticError, LookupError))
    cap = ("Bölümde karşılaştığımız istisna türlerinin soyağacı; her türün üst türü <code>__mro__</code> "
           "zincirinden okunmuştur. Bir <code>except</code> satırı, yazılan türü ve onun altındaki bütün "
           "türleri yakalar: <code>except ArithmeticError</code> hem sıfıra bölmeyi hem taşmayı, "
           "<code>except LookupError</code> hem liste indisi hem sözlük anahtarı hatasını yakalar.")
    aria = ("Indented tree: BaseException, Exception, then ArithmeticError with ZeroDivisionError and "
            "OverflowError, LookupError with IndexError and KeyError, ValueError and TypeError; the "
            "ArithmeticError and LookupError subtrees are framed")
    save("istisna-agaci", figure(W, H, [p], cap, "ders-grafik", aria))


# ============================================================
# 4. From a line of a Turkish CSV file to a pair of floats (21_turkce_csv.py)
# ============================================================
def fig_csv_pipeline():
    text = "x;f(x)\n0,5;0,4794\n1,0;0,8415\n1,5;0,9975\n"
    rows = list(csv.reader(io.StringIO(text), delimiter=";"))
    row = rows[1]
    fixed = [s.replace(",", ".") for s in row]
    nums = tuple(float(s) for s in fixed)
    assert row == ["0,5", "0,4794"] and nums == (0.5, 0.4794)

    W, H = 480, 300
    p = pixel_plot(W, H)
    x_left, x_right = 20, 460          # the boxes span the whole width
    cx = 330                           # centre of the value column
    steps = [
        ("dosyadaki satır", "0,5;0,4794\\n", TEXT),
        ("metin listesi", "[" + ", ".join(f"'{s}'" for s in row) + "]", THEORY),
        ("noktalı metinler", "[" + ", ".join(f"'{s}'" for s in fixed) + "]", THEORY),
        ("sayı çifti", f"({nums[0]}, {nums[1]})", PRACTICE),
    ]
    ops = ['csv.reader(f, delimiter=";")', 's.replace(",", ".")', "float(s)"]
    ys = [30, 112, 194, 276]
    for (lab, s, col), y in zip(steps, ys):
        box(p, (x_left + x_right) / 2, y, x_right - x_left, 36, col, 0.08)
        p.label(x_left + 12, y, lab, 0, 4.5, TEXT, 12, "start")
        p.label(cx, y, esc(s), 0, 4.5, col, 12.5, "middle", True)
    for (y1, y2), op in zip(zip(ys, ys[1:]), ops):
        p.arrow((cx, y1 + 19), (cx, y2 - 19), TEXT, 1.5, head=8)
        p.label(cx, (y1 + y2) / 2, esc(op), -12, 4.5, BASE, 12, "end", True)
    cap = ("<code>tr.csv</code> dosyasının ikinci satırının yolculuğu. <code>csv.reader</code> satırı "
           "noktalı virgülden böler ve satır sonunu atar; alanlar hâlâ metindir. Ondalık virgül noktaya "
           "çevrildikten sonra <code>float</code> her alanı sayıya dönüştürür.")
    aria = ("Four stacked boxes: the file line 0,5;0,4794 with a newline, the list of strings 0,5 and "
            "0,4794, the strings 0.5 and 0.4794, and the float pair (0.5, 0.4794); the arrows are labelled "
            "csv.reader with delimiter semicolon, replace comma by point, and float")
    save("csv-satiri", figure(W, H, [p], cap, "ders-grafik", aria))


# ============================================================
# 5. One class, two objects (24_ilk_sinif.py)
# ============================================================
def fig_class_objects():
    u, v = (3, 4), (5, 1)
    nu, nv = math.hypot(*u), math.hypot(*v)
    assert nu == 5.0 and abs(nv - 5.0990195135927845) < 1e-15

    W, H = 560, 318
    p = pixel_plot(W, H)
    # the class
    ccx, ccy = 280, 70
    box(p, ccx, ccy, 230, 100, BASE, 0.08, rx=10)
    p.label(ccx, ccy - 50, "sınıf Vec2", 0, -8, BASE, 12.5, "middle", True)
    p.label(ccx, ccy, "__init__(self, x, y)", 0, -12, BASE, 13, "middle", True)
    p.label(ccx, ccy, "norm(self)", 0, 14, BASE, 13, "middle", True)
    p.add(f'<line x1="{ccx - 100:.1f}" y1="{ccy + 1:.1f}" x2="{ccx + 100:.1f}" y2="{ccy + 1:.1f}" '
          f'stroke="{BASE}" stroke-width="0.8" opacity="0.5"/>')
    # the objects
    objs = (("u", 120, u, nu), ("v", 440, v, nv))
    oy = 215
    for name, ox, (x, y), n in objs:
        box(p, ox, oy, 150, 72, THEORY, 0.10, rx=10)
        p.label(ox - 75, oy - 36, "nesne " + name, 0, -8, THEORY, 12.5, "start", True)
        p.label(ox, oy, f"x = {x}", 0, -8, THEORY, 13, "middle")
        p.label(ox, oy, f"y = {y}", 0, 16, THEORY, 13, "middle")
        nstr = "5.0" if n == 5.0 else "5.099" + HELLIP
        p.label(ox, oy + 36, f"{name}.norm() = {nstr}", 0, 22, PRACTICE, 12, "middle")
        # "is an instance of" arrow from the object to the class
        sx = ox + (40 if ox < ccx else -40)
        tx = ccx + (-60 if ox < ccx else 60)
        p.arrow((sx, oy - 36), (tx, ccy + 50), TEXT, 1.3, head=7, dash="5 4", opacity=0.8)
    p.label(178, 150, "type(u)", 0, 0, TEXT, 11.5, "end")
    p.label(382, 150, "type(v)", 0, 0, TEXT, 11.5, "start")
    cap = ("Bir sınıf ve ondan üretilen iki nesne. Metotlar (<code>__init__</code>, <code>norm</code>) sınıfta "
           "bir kez tanımlıdır; her nesne kendi <code>x</code>, <code>y</code> niteliklerini taşır. "
           "<code>u.norm()</code> çağrısı <code>Vec2.norm(u)</code> demektir: metot, "
           "<code>self</code> yerine <code>u</code> konarak çalışır.")
    aria = ("A box for the class Vec2 with the methods __init__ and norm; below it two object boxes u with "
            "x = 3, y = 4 and v with x = 5, y = 1, each with a dashed arrow to the class; u.norm() = 5.0 "
            "and v.norm() = 5.099")
    save("sinif-nesne", figure(W, H, [p], cap, "ders-grafik", aria))


# ============================================================
# 6. Vector addition and subtraction with Vec2 (26_vec2_kullan.py)
# ============================================================
def fig_vector_ops():
    u, v = (3, 1), (1, 2)
    s = (u[0] + v[0], u[1] + v[1])
    d = (u[0] - v[0], u[1] - v[1])
    assert s == (4, 3) and d == (2, -1)

    ppu = 66
    xr, yr = (-0.6, 4.7), (-1.6, 3.6)
    p = Plot(40, 24, (xr[1] - xr[0]) * ppu, (yr[1] - yr[0]) * ppu, xr, yr)
    p.grid([1, 2, 3, 4], [-1, 1, 2, 3])
    p.origin_axes(it("x"), it("y"), (1, 2, 3, 4), (-1, 1, 2, 3), dec, dec, opacity=0.5)
    # parallelogram sides
    p.line([u, s], BASE, 1.2, "5 4", 0.7)     # parallel to v
    p.line([v, s], THEORY, 1.2, "5 4", 0.7)   # parallel to u
    # v -> u equals u - v
    p.arrow(v, u, PRACTICE, 1.4, head=7, dash="5 4", opacity=0.75)
    p.arrow((0, 0), u, THEORY, 2.2, head=9)
    p.arrow((0, 0), v, BASE, 2.2, head=9)
    p.arrow((0, 0), s, TEXT, 2.2, head=9)
    p.arrow((0, 0), d, PRACTICE, 2.2, head=9)
    p.label(*u, "u = Vec2(3, 1)", 8, 14, THEORY, 12.5, "start", True)
    p.label(*v, "v = Vec2(1, 2)", -8, -8, BASE, 12.5, "end", True)
    p.label(*s, "u + v = Vec2(4, 3)", -6, -10, TEXT, 12.5, "end", True)
    p.label(*d, "u " + MINUS + " v = Vec2(2, " + MINUS + "1)", 10, 6, PRACTICE, 12.5, "start", True)
    W = int(p.x0 + p.w + 30)
    H = int(p.y0 + p.h + 26)
    cap = ("<code>Vec2</code> ile hesaplanan <code>u + v</code> ve <code>u - v</code>. Toplam, "
           "<code>u</code> ile <code>v</code> üzerine kurulan paralelkenarın köşegenidir; fark ise "
           "<code>v</code>'nin ucundan <code>u</code>'nun ucuna giden vektördür (kesikli ok), başlangıç "
           "noktası orijine taşınmış olarak.")
    aria = ("Vectors from the origin: u = (3, 1), v = (1, 2), u + v = (4, 3) as the diagonal of the dashed "
            "parallelogram, and u - v = (2, -1), equal to the dashed arrow from the tip of v to the tip of u")
    save("vektor-islemleri", figure(W, H, [p], cap, "ders-grafik", aria))


# ============================================================
# 7. Newton's method cycling for x^3 - 2x + 2 from x0 = 0 (29_newton_istisna.py)
# ============================================================
def fig_newton_cycle():
    def f(x):
        return x ** 3 - 2 * x + 2

    def df(x):
        return 3 * x ** 2 - 2
    xs = [0.0]
    for _ in range(20):
        xs.append(xs[-1] - f(xs[-1]) / df(xs[-1]))
    assert xs[-4:] == [1.0, 0.0, 1.0, 0.0]
    r = -2.0
    for _ in range(60):
        r_new = r - f(r) / df(r)
        if abs(r_new - r) < 1e-12:
            r = r_new
            break
        r = r_new
    assert abs(r + 1.7692923542386314) < 1e-15

    xr, yr = (-2.3, 1.9), (-3.2, 4.4)
    p = Plot(48, 22, 430, 282, xr, yr)
    p.grid([-2, -1, 1], [-2, 2, 4])
    p.origin_axes(it("x"), it("y"), (-2, -1), (-2, 2, 4), dec, dec, opacity=0.5)
    pts = [(xr[0] + (xr[1] - xr[0]) * k / 400, 0) for k in range(401)]
    pts = [(x, f(x)) for x, _ in pts if yr[0] <= f(x) <= yr[1]]
    p.line(pts, THEORY, 2.3)
    # tangent at 0 down to x = 1, tangent at 1 down to x = 0
    p.line([(0, 0), (0, f(0))], TEXT, 1.0, "4 3", 0.7)
    p.arrow((0, f(0)), (1, 0), PRACTICE, 1.8, head=8)
    p.line([(1, 0), (1, f(1))], TEXT, 1.0, "4 3", 0.7)
    p.arrow((1, f(1)), (0, 0), PRACTICE, 1.8, head=8)
    for pt in ((0, f(0)), (1, f(1))):
        p.points([pt], THEORY, 4.0)
    p.points([(r, 0)], BASE, 4.6)
    p.label(r, 0, "kök " + "&#8776; " + dec(r, 3), 6, -10, BASE, 12, "start", True)
    p.label(0, 0, it("x") + sub("0") + ", " + it("x") + sub("2") + ", " + HELLIP + " = 0", -8, 18,
            PRACTICE, 12, "end", True)
    p.label(1, 0, it("x") + sub("1") + ", " + it("x") + sub("3") + ", " + HELLIP + " = 1", 0, 18,
            PRACTICE, 12, "middle", True)
    p.label(1.45, f(1.45), it("y") + " = " + it("x") + "³ " + MINUS + " 2" + it("x") + " + 2", -8, -2,
            THEORY, 12.5, "end", True)
    W = int(p.x0 + p.w + 30)
    H = int(p.y0 + p.h + 26)
    cap = ("<em>f</em>(<em>x</em>) = <em>x</em>³ &#8722; 2<em>x</em> + 2 için Newton yöntemi "
           "<em>x</em><sub>0</sub> = 0'dan başlayınca: 0'daki teğet ekseni 1'de, 1'deki teğet ekseni yine "
           "0'da keser. İterasyon 0, 1, 0, 1, … döngüsüne girer ve tek kök olan &#8722;1,769… noktasına "
           "hiç yaklaşmaz; <code>newton</code> fonksiyonu bu yüzden <code>ConvergenceError</code> fırlatır.")
    aria = ("Graph of y = x^3 - 2x + 2 with its single root near -1.769; the tangent at x = 0 meets the "
            "x axis at 1 and the tangent at x = 1 meets it at 0, so the Newton iterates alternate 0, 1, 0, 1")
    save("newton-dongusu", figure(W, H, [p], cap, "ders-grafik", aria))


# ============================================================
# 8. Cooling data read from sogutma.csv and the fitted model (32_sogutma.py)
# ============================================================
DATA = """t;T
0;90,0
2;77,7
4;67,2
6;58,2
8;
10;45,8
12;4l,3
14;37,4
16;34,6
18;3,18
20;29,6
"""


def fig_cooling():
    good, bad = [], []
    reader = csv.reader(io.StringIO(DATA), delimiter=";")
    next(reader)
    for line_no, row in enumerate(reader, start=2):
        try:
            t, T = (float(s.replace(",", ".")) for s in row)
            if T <= 20:
                raise ValueError("below room temperature")
            good.append((t, T))
        except ValueError:
            bad.append((line_no, float(row[0]), row[1]))
    ks = [math.log(70 / (T - 20)) / t for t, T in good if t > 0]
    k = sum(ks) / len(ks)
    assert len(good) == 8 and [b[0] for b in bad] == [6, 8, 11] and f"{k:.4f}" == "0.0989"

    xr, yr = (0, 21), (0, 95)
    p = Plot(56, 26, 420, 262, xr, yr)
    p.grid([5, 10, 15, 20], [20, 40, 60, 80])
    p.axes([0, 5, 10, 15, 20], [0, 20, 40, 60, 80], it("t"), it("T"), dec, dec)
    p.line([(0, 20), (21, 20)], TEXT, 1.0, "4 3", 0.55)
    p.label(21, 20, "oda sıcaklığı 20", 0, -6, TEXT, 11.5, "end")
    p.line([(t / 10, 20 + 70 * math.exp(-k * t / 10)) for t in range(0, 211)], THEORY, 2.2)
    p.points(good, PRACTICE, 4.4)
    for line_no, t, raw in bad:
        p.line([(t, 3), (t, 14)], REMARK, 1.2, "3 3", 0.9)
        p.add(f'<path d="M{p.X(t) - 4:.1f},{p.Y(8.5) - 4:.1f} L{p.X(t) + 4:.1f},{p.Y(8.5) + 4:.1f} '
              f'M{p.X(t) - 4:.1f},{p.Y(8.5) + 4:.1f} L{p.X(t) + 4:.1f},{p.Y(8.5) - 4:.1f}" '
              f'stroke="{REMARK}" stroke-width="1.8" stroke-linecap="round"/>')
        s = "boş" if raw == "" else f"'{raw}'"
        p.label(t, 14, s, 0, -6, REMARK, 11.5, "middle", True)
    p.label(9.5, 20 + 70 * math.exp(-k * 9.5), it("T") + " = 20 + 70" + it("e") +
            f'<tspan font-size="9" dy="-5">{MINUS}{dec(k, 4)}' + it("t") + '</tspan><tspan dy="5">&#8203;</tspan>',
            10, -10, THEORY, 12.5, "start", True)
    W = int(p.x0 + p.w + 40)
    H = int(p.y0 + p.h + 28)
    cap = ("<code>sogutma.csv</code> dosyasından okunan sekiz geçerli ölçüm (noktalar; <em>t</em> dakika, "
           "<em>T</em> santigrat derece) ve ortalama "
           "<em>k</em> &#8776; 0,0989 ile çizilen <em>T</em> = 20 + 70<em>e</em><sup>&#8722;<em>kt</em></sup> "
           "modeli. Alttaki çarpılar atlanan üç satırın zamanlarıdır: boş alan, harfli değer ve oda "
           "sıcaklığının altında kalan değer.")
    aria = ("Scatter of eight temperature readings T against time t from 0 to 20 minutes, decreasing from "
            "90 towards 30, with the curve T = 20 + 70 exp(-0.0989 t); crosses near the time axis at t = 8, "
            "12 and 18 mark the skipped rows")
    save("sogutma", figure(W, H, [p], cap, "ders-grafik", aria))


if __name__ == "__main__":
    fig_namespaces()
    fig_try_flow()
    fig_exception_tree()
    fig_csv_pipeline()
    fig_class_objects()
    fig_vector_ops()
    fig_newton_cycle()
    fig_cooling()
