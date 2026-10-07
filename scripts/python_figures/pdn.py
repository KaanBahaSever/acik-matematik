# -*- coding: utf-8 -*-
"""
Figures of the chapter "Pandas ile Veri Analizi"
(dersler/python-bilimsel/pandas-ile-veri-analizi.qmd).

Figures go INSIDE the box they explain (theorem, example, exercise or
callout), never inside a definition box, never inside a collapsed
.cozum/.ispat block when they carry the concept, and never directly under a
heading. The figures are NOT produced at build time. Run (with the course
venv, since the data is computed with pandas exactly as in the chapter code)

    set OPENBLAS_NUM_THREADS=1
    python scripts/python_figures/pdn.py
    python scripts/center_figures.py "python-pdn-*.md"
    python scripts/check_figure_labels.py "scripts/_figures/python-pdn-*.md"

and paste the markup of scripts/_figures/python-pdn-<name>.md into the .qmd.
The weather data set is regenerated here with the same generator, seed and
CSV round trip as the chapter code, so every number in a figure is the
number the chapter prints. Captions are Turkish on purpose; aria labels are
plain ASCII.
"""
import html
import io
import math
import os
import sys
from pathlib import Path

os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import (Plot, figure, WIDE, TEXT, THEORY, PRACTICE,  # noqa: E402
                      BASE, REMARK)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "python-pdn-"

MINUS = "&#8722;"
ARROW = "&#8594;"


def save(name, markup):
    (OUT_DIR / f"{PREFIX}{name}.md").write_text(markup, encoding="utf-8",
                                                newline="\n")
    print(f"{PREFIX}{name}.md")


def canvas(W, H):
    """A panel whose data coordinates are the pixel coordinates (y down)."""
    return Plot(0, 0, W, H, (0, W), (H, 0))


def dec(v, digits=2):
    """Decimal comma and a true minus sign: -0.5 -> '−0,50'."""
    s = f"{v:.{digits}f}"
    return s.replace(".", ",").replace("-", MINUS)


def code_num(s):
    """A number as Python prints it, with a true minus sign for the SVG."""
    return s.replace("-", MINUS)


def rect(p, x, y, w, h, fill="none", fop=0.0, stroke=TEXT, sw=1.0,
         sop=0.5, dash=None):
    da = f' stroke-dasharray="{dash}"' if dash else ""
    p.add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
          f'fill="{fill}" fill-opacity="{fop}" stroke="{stroke}" '
          f'stroke-width="{sw}" stroke-opacity="{sop}"{da}/>')


def txt(p, x, y, s, color=TEXT, size=12, anchor="middle", bold=False,
        italic=False, opacity=1.0):
    weight = ' font-weight="600"' if bold else ""
    slant = ' font-style="italic"' if italic else ""
    op = f' opacity="{opacity}"' if opacity != 1.0 else ""
    p.add(f'<text x="{x:.1f}" y="{y:.1f}" fill="{color}" font-size="{size}" '
          f'text-anchor="{anchor}"{weight}{slant}{op}>{s}</text>')


def table(p, x0, y0, widths, h, rows, fills=None, colors=None, bold=None,
          size=12, anchors=None):
    """Draw rows of cells. fills[i][j] = (color, opacity) or None."""
    for i, row in enumerate(rows):
        x = x0
        for j, s in enumerate(row):
            w = widths[j]
            f = fills[i][j] if fills else None
            if f:
                rect(p, x, y0 + i * h, w, h, f[0], f[1])
            else:
                rect(p, x, y0 + i * h, w, h)
            c = colors[i][j] if colors and colors[i][j] else TEXT
            b = bold[i][j] if bold else False
            a = anchors[j] if anchors else "middle"
            tx = {"middle": x + w / 2, "end": x + w - 7,
                  "start": x + 7}[a]
            txt(p, tx, y0 + i * h + h / 2 + size * 0.36, s, c, size, a, b)
            x += w


def nan_cell(s):
    return s == "NaN"


def note(p, x, y, lines, color, step=17):
    """Annotation lines starting at (x, y) inside a faint framed box.

    The box is as wide as the label checker's width estimate (0.56 em per
    character), so the estimated text never leaves the drawn content.
    """
    width = max(len(html.unescape(s)) * 0.56 * size for s, size, _ in lines)
    rect(p, x - 8, y - 16, width + 16, step * (len(lines) - 1) + 24,
         color, 0.06, color, 1.0, 0.45)
    for k, (s, size, bold) in enumerate(lines):
        txt(p, x, y + k * step, s, color, size, "start", bold)


# ------------------------------------------------------------------
# The chapter's weather data set: same generator, seed and CSV round trip
# ------------------------------------------------------------------
def weather():
    rng = np.random.default_rng(2025)
    days = pd.date_range("2025-01-01", "2025-12-31")
    t = np.arange(days.size)
    params = {"Ankara": (12.0, 11.5, 0.25, 4.0),
              "İzmir": (18.0, 8.5, 0.20, 8.0),
              "Erzurum": (6.0, 14.0, 0.30, 3.5)}
    names, temps, rains = [], [], []
    for name, (m, a, p, r) in params.items():
        wave = m - a * np.cos(2 * np.pi * (t - 15) / 365)
        temps.append(wave + rng.normal(0, 2.5, t.size))
        wet = rng.random(t.size) < p
        rains.append(np.where(wet, rng.exponential(r, t.size), 0.0))
        names += [name] * t.size
    temp = np.concatenate(temps).round(1) + 0.0
    lost = rng.choice(temp.size, size=30, replace=False)
    temp[lost] = np.nan
    df = pd.DataFrame({"tarih": np.tile(days, 3), "istasyon": names,
                       "sicaklik": temp,
                       "yagis": np.concatenate(rains).round(1)})
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    buf.seek(0)
    return pd.read_csv(buf, parse_dates=["tarih"])


DF = weather()
STATION_COLOR = {"Ankara": THEORY, "Erzurum": PRACTICE, "İzmir": BASE}


# ============================================================
# hizalama: a + b aligns the two Series on the union of their labels
# ============================================================
def fig_hizalama():
    a = pd.Series([1, 2, 3], index=["x", "y", "z"])
    b = pd.Series([10, 20, 30], index=["y", "z", "w"])
    s = a + b
    f = a.add(b, fill_value=0)
    union = s.index.tolist()                       # ['w', 'x', 'y', 'z']
    al, bl = a.reindex(union), b.reindex(union)
    W, H = 660, 300
    p = canvas(W, H)
    h = 28
    lw, vw = 30, 46
    common = {"y", "z"}
    nan_fill = (PRACTICE, 0.14)
    row_fill = (THEORY, 0.12)

    def show(v):
        return "NaN" if pd.isna(v) else code_num(str(v))

    # the two operands
    for name, ser, y0 in [("a", a, 52), ("b", b, 186)]:
        txt(p, 16 + (lw + vw) / 2, y0 - 12, name, TEXT, 13, bold=True,
            italic=True)
        rows = [[k, str(v)] for k, v in ser.items()]
        fills = [[(TEXT, 0.07), row_fill if k in common else None]
                 for k in ser.index]
        table(p, 16, y0, [lw, vw], h, rows, fills)
    # aligned operands on the union index
    MX, MY = 214, 100
    txt(p, MX + lw + vw, MY - 40, "birleşim indeksine hizalanmış",
        TEXT, 11.5)
    header = [["", "a", "b"]]
    table(p, MX, MY - h, [lw, vw, vw], h, header,
          [[None, (TEXT, 0.07), (TEXT, 0.07)]], bold=[[False, True, True]])
    rows, fills, colors = [], [], []
    for k in union:
        va, vb = show(al[k]), show(bl[k])
        rows.append([k, va, vb])
        base = row_fill if k in common else None
        fills.append([(TEXT, 0.07),
                      nan_fill if nan_cell(va) else base,
                      nan_fill if nan_cell(vb) else base])
        colors.append([None, PRACTICE if nan_cell(va) else None,
                       PRACTICE if nan_cell(vb) else None])
    table(p, MX, MY, [lw, vw, vw], h, rows, fills, colors)
    # the results
    RX = 436
    widths = [lw, 64, 104]
    table(p, RX, MY - h, widths, h, [["", "a + b", "fill_value=0"]],
          [[None, (TEXT, 0.07), (TEXT, 0.07)]], bold=[[False, True, True]],
          size=11.5)
    rows, fills, colors = [], [], []
    for k in union:
        vs, vf = show(s[k]), show(f[k])
        rows.append([k, vs, vf])
        base = row_fill if k in common else None
        fills.append([(TEXT, 0.07), nan_fill if nan_cell(vs) else base,
                      (BASE, 0.14) if k not in common else base])
        colors.append([None, PRACTICE if nan_cell(vs) else None,
                       BASE if k not in common else None])
    table(p, RX, MY, widths, h, rows, fills, colors)
    # arrows
    p.arrow((16 + lw + vw + 8, 52 + 1.5 * h), (MX - 8, MY + 1.2 * h),
            TEXT, 1.3, 7.0, None, 0.7)
    p.arrow((16 + lw + vw + 8, 186 + 1.5 * h), (MX - 8, MY + 2.8 * h),
            TEXT, 1.3, 7.0, None, 0.7)
    p.arrow((MX + lw + 2 * vw + 8, MY + 2 * h), (RX - 8, MY + 2 * h),
            TEXT, 1.3, 7.0, None, 0.7)
    txt(p, (MX + lw + 2 * vw + RX) / 2, MY + 2 * h - 8, "topla", TEXT, 11.5)
    txt(p, RX + lw + 64 + 52, MY + 4 * h + 22, "eksik taraf 0 sayılır",
        BASE, 11.5)
    save("hizalama", figure(
        W, H, [p],
        "<code>a + b</code> işleminin iki adımı. Önce iki Series etiketlerin "
        "birleşimi olan {w, x, y, z} indeksine hizalanır; etiketi olmayan "
        "taraf <code>NaN</code> ile doldurulur. Sonra değerler satır satır "
        "toplanır. Yalnız iki tarafta da bulunan y ve z etiketlerinde sayı "
        "çıkar. <code>a.add(b, fill_value=0)</code> ise eksik tarafı 0 "
        "sayar ve w ile x satırlarında da sonuç verir.",
        WIDE,
        aria="Series a with labels x y z and values 1 2 3, Series b with "
             "labels y z w and values 10 20 30. Both are aligned to the "
             "union index w x y z with NaN where a label is missing; the sum "
             "a + b is NaN NaN 12 23, and with fill_value=0 it is 30 1 12 "
             "23."))


# ============================================================
# dataframe: index, columns, a column and a row of the prime table
# ============================================================
def fig_dataframe():
    def is_prime(m):
        return m > 1 and all(m % d for d in range(2, math.isqrt(m) + 1))

    pr = [2, 3, 5, 7, 11, 13, 17]
    df = pd.DataFrame({"p": pr,
                       "ikilik": [bin(q)[2:] for q in pr],
                       "kok": [math.sqrt(q) for q in pr],
                       "ikiz": [is_prime(q + 2) for q in pr]})
    W, H = 660, 350
    p = canvas(W, H)
    X0, Y0, h = 132, 64, 26
    widths = [34, 46, 72, 86, 62]
    cols = df.columns.tolist()
    # header row
    hdr = [[""] + cols]
    table(p, X0, Y0, widths, h, hdr,
          [[None] + [(THEORY, 0.16)] * 4],
          colors=[[None] + [THEORY] * 4], bold=[[False] + [True] * 4])
    rows = []
    for i, r in df.iterrows():
        rows.append([str(i), str(r["p"]), r["ikilik"], f"{r['kok']:.6f}",
                     str(r["ikiz"])])
    fills = [[(TEXT, 0.09)] + [None] * 4 for _ in rows]
    colors = [[TEXT] + [None] * 4 for _ in rows]
    table(p, X0, Y0 + h, widths, h, rows, fills, colors, size=11.5)
    # dtypes row
    YD = Y0 + h * (len(rows) + 1) + 8
    xs = np.cumsum([X0] + widths)
    for j, c in enumerate(cols):
        txt(p, (xs[j + 1] + xs[j + 2]) / 2, YD + 16, str(df[c].dtype), TEXT,
            11.5, italic=True, opacity=0.8)
    txt(p, X0 + widths[0] - 4, YD + 16, "dtypes", TEXT, 11.5, "end",
        bold=True, opacity=0.8)
    # the column kok
    kx = xs[3]
    rect(p, kx + 1.5, Y0 + 1.5, widths[3] - 3, h * 8 - 3, "none", 0,
         PRACTICE, 2.2, 1.0)
    # the row with label 4
    ry = Y0 + h * 5
    rect(p, X0 + widths[0] + 1.5, ry + 1.5, sum(widths[1:]) - 3, h - 3,
         "none", 0, BASE, 2.2, 1.0)
    # annotations on the right
    RX = xs[-1] + 34
    ya = Y0 + 2 * h
    p.arrow((RX - 10, ya), (kx + widths[3] + 6, ya), PRACTICE, 1.4, 7.0)
    note(p, RX, ya + 4, [('df["kok"]', 12, True), ("bir Series,", 11.5,
                         False), ("indeksi 0, 1, ..., 6", 11.5, False)],
         PRACTICE)
    yb = ry + h / 2
    p.arrow((RX - 10, yb), (xs[-1] + 6, yb), BASE, 1.4, 7.0)
    note(p, RX, yb + 4, [("df.loc[4]", 12, True), ("bir Series,", 11.5,
                         False), ("indeksi sütun adları", 11.5, False)],
         BASE)
    # index and columns labels
    LXI = X0 - 96
    txt(p, LXI, Y0 + 4.5 * h - 12, "index", TEXT, 12, "start", True)
    txt(p, LXI, Y0 + 4.5 * h + 5, "satır", TEXT, 11.5, "start")
    txt(p, LXI, Y0 + 4.5 * h + 21, "etiketleri", TEXT, 11.5, "start")
    p.arrow((LXI + 40, Y0 + 4.5 * h - 26), (X0 - 4, Y0 + 3 * h), TEXT, 1.2,
            6.5, None, 0.7)
    txt(p, xs[1] + 4, Y0 - 26, "columns: sütun etiketleri", THEORY, 12,
        "start", True)
    p.arrow((xs[1] - 4, Y0 - 30), (xs[1] - 4, Y0 - 3), THEORY, 1.2, 6.5,
            None, 0.8)
    save("dataframe", figure(
        W, H, [p],
        "Asal sayılar tablosu <code>df</code>'nin parçaları. Soldaki gri "
        "sütun satır etiketleri (index), üstteki satır sütun etiketleridir "
        "(columns). Her sütun kendi türünde bir Series'tir; türler en altta "
        "<code>df.dtypes</code> satırında yazılıdır. Çerçeveli sütun "
        "<code>df[\"kok\"]</code>, çerçeveli satır <code>df.loc[4]</code> "
        "seçimidir; ikisi de birer Series olarak döner.",
        WIDE,
        aria="A table with index 0 to 6 and columns p, ikilik, kok, ikiz "
             "holding the primes 2 to 17, their binary digits, square roots "
             "and a twin prime flag. The column kok and the row with label 4 "
             "are framed; the dtypes int64, str, float64, bool are listed "
             "below the columns."))


# ============================================================
# eksik: three lost values of sin x filled by ffill and by interpolation
# ============================================================
def fig_eksik():
    x = np.linspace(0, np.pi, 9)
    s = pd.Series(np.sin(x), index=x.round(3))
    s.iloc[[2, 3, 6]] = np.nan
    ff = s.ffill().to_numpy()
    li = s.interpolate().to_numpy()
    miss = [2, 3, 6]
    known = [k for k in range(9) if k not in miss]
    W, H = 540, 350
    p = Plot(56, 30, 440, 230, (0, math.pi), (-0.05, 1.12))
    p.axes([], [0, 0.5, 1], "x", "",
           yfmt=lambda v: dec(v, 1) if v == 0.5 else str(int(v)))
    for k, lab in [(0, "0"), (2, "&#960;/4"), (4, "&#960;/2"),
                   (6, "3&#960;/4"), (8, "&#960;")]:
        p.label(x[k], -0.05, lab, 0, 17, TEXT, 11, "middle")
    for k in miss:
        p.vline(x[k], -0.05, 1.08, TEXT, "3 3", 0.35)
    xs = np.linspace(0, math.pi, 200)
    p.line(list(zip(xs, np.sin(xs))), TEXT, 1.2, "5 4", 0.55)
    p.label(4.4 * math.pi / 8, math.sin(4.4 * math.pi / 8), "sin " +
            '<tspan font-style="italic">x</tspan>', 0, -10, TEXT, 12,
            "start")
    # ffill: horizontal carry of the last known value
    p.line([(x[1], ff[1]), (x[3], ff[3])], PRACTICE, 1.8, "6 3")
    p.line([(x[5], ff[5]), (x[6], ff[6])], PRACTICE, 1.8, "6 3")
    p.hollow_points([(x[k], ff[k]) for k in miss], PRACTICE, 4.4)
    # linear interpolation between the neighbours
    p.line([(x[1], li[1]), (x[4], li[4])], BASE, 1.8)
    p.line([(x[5], li[5]), (x[7], li[7])], BASE, 1.8)
    p.points([(x[k], li[k]) for k in miss], BASE, 4.2)
    p.points([(x[k], s.iloc[k]) for k in known], THEORY, 4.4)
    # legend under the axis
    LY = p.y0 + p.h + 50
    p.add(f'<circle cx="{p.x0 + 6:.1f}" cy="{LY - 4:.1f}" r="4.4" '
          f'fill="{THEORY}"/>')
    txt(p, p.x0 + 16, LY, "bilinen değer", TEXT, 12, "start")
    p.add(f'<circle cx="{p.x0 + 140:.1f}" cy="{LY - 4:.1f}" r="4.4" '
          f'fill="none" stroke="{PRACTICE}" stroke-width="1.8"/>')
    txt(p, p.x0 + 150, LY, "ffill()", PRACTICE, 12, "start", True)
    p.add(f'<circle cx="{p.x0 + 244:.1f}" cy="{LY - 4:.1f}" r="4.2" '
          f'fill="{BASE}"/>')
    txt(p, p.x0 + 254, LY, "interpolate()", BASE, 12, "start", True)
    err_f = np.abs(ff[miss] - np.sin(x[miss])).max()
    err_l = np.abs(li[miss] - np.sin(x[miss])).max()
    # The Turkish suffixes follow how the numbers are read aloud
    # ("elli dört" -> 'tür, "on üç" -> 'e); recheck them if the data change.
    assert (dec(err_f, 2), dec(err_l, 2)) == ("0,54", "0,13")
    save("eksik", figure(
        W, H, [p],
        "sin <em>x</em> fonksiyonunun dokuz noktalık tablosunda kaybolan "
        "üç değer (kesikli dikey çizgiler). <code>ffill()</code> son bilinen "
        "değeri ileri taşır (boş daireler), en büyük hatası "
        f"{dec(err_f, 2)}'tür. <code>interpolate()</code> iki komşu bilinen "
        "değeri doğru parçasıyla birleştirir (dolu daireler), en büyük hatası "
        f"{dec(err_l, 2)}'e iner. Kesikli eğri gerçek sin <em>x</em>'tir.",
        aria="The curve sin x on [0, pi] with nine grid points, three of "
             "them missing at pi/4, 3pi/8 and 3pi/4. Forward fill carries "
             "the last known value horizontally (hollow red circles); linear "
             "interpolation joins the neighbours by segments (filled green "
             "dots) and stays closer to the curve."))


# ============================================================
# groupby: split - apply - combine on the six-row table
# ============================================================
def fig_groupby():
    df = pd.DataFrame({
        "istasyon": ["Ankara", "İzmir", "Ankara", "Erzurum", "İzmir",
                     "Erzurum"],
        "sicaklik": [0.4, 9.1, 23.6, -8.9, 27.8, 19.7]})
    means = df.groupby("istasyon")["sicaklik"].mean()
    W, H = 680, 300
    p = canvas(W, H)
    h = 26
    lw = [76, 70]
    LX, LY = 16, 70
    # titles
    txt(p, LX + sum(lw) / 2, 30, "ayır", TEXT, 13, bold=True)
    txt(p, 312, 30, "uygula: mean()", TEXT, 13, bold=True)
    txt(p, 576, 30, "birleştir", TEXT, 13, bold=True)
    table(p, LX, LY - h, lw, h, [["istasyon", "sicaklik"]],
          [[(TEXT, 0.07), (TEXT, 0.07)]], bold=[[True, True]], size=11.5)
    rows = [[r.istasyon, code_num(str(r.sicaklik))] for r in df.itertuples()]
    fills = [[(STATION_COLOR[r[0]], 0.16), (STATION_COLOR[r[0]], 0.07)]
             for r in rows]
    table(p, LX, LY, lw, h, rows, fills, size=11.5)
    # the groups
    GX = 232
    gw = [76, 70]
    gy = {"Ankara": 52, "Erzurum": 128, "İzmir": 204}
    res_y0 = 101
    RX = 506
    for k, (name, y0) in enumerate(gy.items()):
        part = df[df["istasyon"] == name]
        color = STATION_COLOR[name]
        grows = [[name, code_num(str(v))] for v in part["sicaklik"]]
        table(p, GX, y0, gw, h, grows,
              [[(color, 0.16), (color, 0.07)]] * len(grows), size=11.5)
        # split arrows: from the left table to the group
        p.arrow((LX + sum(lw) + 6, LY + 3 * h), (GX - 6, y0 + h),
                color, 1.4, 7.0, None, 0.85)
        # apply arrows: from the group to its row of the result
        ry = res_y0 + h + k * h + h / 2
        p.arrow((GX + sum(gw) + 6, y0 + h), (RX - 6, ry), color, 1.4, 7.0,
                None, 0.85)
        dy = 22 if name == "İzmir" else -9
        txt(p, GX + sum(gw) + 12, y0 + h + dy,
            code_num(f"{means[name]:.2f}"), color, 11.5, "start", True)
    table(p, RX, res_y0, [76, 70], h, [["istasyon", "sicaklik"]],
          [[(TEXT, 0.07), (TEXT, 0.07)]], bold=[[True, True]], size=11.5)
    rrows = [[k, code_num(f"{v:.2f}")] for k, v in means.items()]
    table(p, RX, res_y0 + h, [76, 70], h, rrows,
          [[(STATION_COLOR[r[0]], 0.16), (STATION_COLOR[r[0]], 0.07)]
           for r in rrows], size=11.5, bold=[[False, True]] * 3)
    save("groupby", figure(
        W, H, [p],
        "<code>df.groupby(\"istasyon\")[\"sicaklik\"].mean()</code> "
        "işleminin üç adımı. Ayır: satırlar istasyon adına göre üç gruba "
        "bölünür. Uygula: her grubun sıcaklıklarına <code>mean</code> "
        "uygulanır, örneğin Ankara için (0,4 + 23,6)/2 = 12. Birleştir: "
        "üç sonuç, indeksi grup adları olan tek bir Series'te toplanır.",
        WIDE,
        aria="Split apply combine: a six row table of stations and "
             "temperatures is split into three groups Ankara, Erzurum, "
             "Izmir; the mean of each group, 12.00, 5.40 and 18.45, is "
             "collected into a result table indexed by the station names."))


# ============================================================
# kutu: five-number summary of each station as a box plot
# ============================================================
def fig_kutu():
    q = [0, 0.25, 0.5, 0.75, 1]
    five = DF.groupby("istasyon")["sicaklik"].quantile(q).unstack()
    W, H = 560, 260
    p = Plot(100, 20, 420, 180, (-15, 35), (0, 3))
    p.grid(range(-10, 35, 10), [])
    p.axes(range(-10, 35, 10), [], "°C", "",
           xfmt=lambda v: code_num(str(int(v))))
    order = ["Ankara", "Erzurum", "İzmir"]
    for k, name in enumerate(order):
        yc = 2.5 - k
        lo, q1, me, q3, hi = five.loc[name].to_numpy()
        color = STATION_COLOR[name]
        y0, y1 = p.Y(yc + 0.22), p.Y(yc - 0.22)
        p.line([(lo, yc), (q1, yc)], TEXT, 1.3, None, 0.75)
        p.line([(q3, yc), (hi, yc)], TEXT, 1.3, None, 0.75)
        for v in (lo, hi):
            p.line([(v, yc - 0.12), (v, yc + 0.12)], TEXT, 1.3, None, 0.75)
        rect(p, p.X(q1), y0, p.X(q3) - p.X(q1), y1 - y0, color, 0.18, color,
             1.6, 0.95)
        p.line([(me, yc - 0.22), (me, yc + 0.22)], color, 2.6)
        txt(p, p.x0 - 12, p.Y(yc) + 4, name, color, 12.5, "end", True)
    # value labels for Ankara only
    lo, q1, me, q3, hi = five.loc["Ankara"].to_numpy()
    yc = 2.5
    for v, lab, dx in [(lo, "en küçük", 0), (q1, "<tspan font-style=\"italic\">Q</tspan>&#8321;", 0),
                       (me, "medyan", 0),
                       (q3, "<tspan font-style=\"italic\">Q</tspan>&#8323;", 0),
                       (hi, "en büyük", 0)]:
        p.label(v, yc + 0.22, lab, dx, -8, TEXT, 11, "middle")
    save("kutu", figure(
        W, H, [p],
        "Üç istasyonun sıcaklıkları için kutu grafiği, "
        "<code>quantile([0, 0.25, 0.5, 0.75, 1])</code> tablosundan. Kutu "
        "birinci çeyreklikten üçüncüye uzanır, kalın çizgi medyandır, "
        "bıyıklar en küçük ve en büyük ölçüme gider. İzmir'in kutusu sağda "
        "ve dar, Erzurum'unki solda ve geniştir: İzmir hem daha sıcak hem "
        "de yıl içinde daha az değişkendir.",
        aria="Horizontal box plots of the daily temperatures of Ankara, "
             "Erzurum and Izmir on an axis from -15 to 35 degrees: Ankara "
             "from -4.7 to 31.5 with quartiles 4.8, 11.6, 19.8; Erzurum from "
             "-13.6 to 25.6 with quartiles -3.9, 5.9, 15.25; Izmir from 6.4 "
             "to 31.4 with quartiles 12.2, 18.0, 23.0."))


# ============================================================
# merge: inner, left and outer joins of two small tables
# ============================================================
def fig_merge():
    mean_t = DF.groupby("istasyon", as_index=False)["sicaklik"].mean()
    mean_t["sicaklik"] = mean_t["sicaklik"].round(2)
    info = pd.DataFrame({"istasyon": ["Ankara", "İzmir", "Trabzon"],
                         "plaka": [6, 35, 61]})
    W, H = 680, 380
    p = canvas(W, H)
    h = 25
    key_fill = {"both": (THEORY, 0.15), "left_only": (PRACTICE, 0.15),
                "right_only": (BASE, 0.17)}

    def kind(k):
        a, b = k in set(mean_t["istasyon"]), k in set(info["istasyon"])
        return "both" if a and b else ("left_only" if a else "right_only")

    def fmt(v):
        if pd.isna(v):
            return "NaN"
        return str(v)

    def draw(x0, y0, frame, title):
        cols = frame.columns.tolist()
        widths = [78, 70, 56][:len(cols)]
        txt(p, x0 + sum(widths) / 2, y0 - 12, title, TEXT, 12, bold=True)
        table(p, x0, y0, widths, h, [cols], [[(TEXT, 0.07)] * len(cols)],
              bold=[[True] * len(cols)], size=11.5)
        rows, fills, colors = [], [], []
        for r in frame.itertuples(index=False):
            vals = [fmt(v) for v in r]
            rows.append(vals)
            fills.append([key_fill[kind(r[0])]] +
                         [(REMARK, 0.16) if nan_cell(v) else None
                          for v in vals[1:]])
            colors.append([None] + [REMARK if nan_cell(v) else None
                                    for v in vals[1:]])
        table(p, x0, y0 + h, widths, h, rows, fills, colors, size=11.5)

    draw(110, 40, mean_t, "mean_t (sol)")
    draw(390, 40, info, "info (sağ)")
    y2 = 210
    for k, how in enumerate(["inner", "left", "outer"]):
        res = mean_t.merge(info, on="istasyon", how=how)
        draw(16 + k * 222, y2, res, f'how="{how}"')
    # arrows from the inputs to the results
    for k in range(3):
        cx = 16 + k * 222 + 102
        p.arrow((cx, 160), (cx, y2 - 26), TEXT, 1.2, 6.5, None, 0.55)
    # legend under the short inner table
    LY = y2 + 3 * h + 28
    for j, (lab, key) in enumerate([("iki tabloda", "both"),
                                    ("yalnız solda", "left_only"),
                                    ("yalnız sağda", "right_only")]):
        y = LY + j * 20
        rect(p, 30, y - 10, 14, 12, key_fill[key][0], key_fill[key][1] + 0.1,
             key_fill[key][0], 1.0, 0.8)
        txt(p, 50, y, lab, TEXT, 11.5, "start")
    save("merge", figure(
        W, H, [p],
        "<code>mean_t.merge(info, on=\"istasyon\", how=...)</code> "
        "sonuçları (bölge sütunu yer kazanmak için çizilmedi). "
        "<code>inner</code> yalnız iki tabloda da bulunan anahtarları, "
        "<code>left</code> sol tablonun bütün anahtarlarını, "
        "<code>outer</code> iki tablonun bütün anahtarlarını tutar. "
        "Karşılığı olmayan hücreler <code>NaN</code> olur; bu yüzden "
        "<code>left</code> ve <code>outer</code> sonuçlarında plaka "
        "sütunu ondalıklı sayıya döner.",
        WIDE,
        aria="Two input tables: mean temperatures of Ankara, Erzurum, Izmir "
             "and plate numbers of Ankara, Izmir, Trabzon. Below, the inner "
             "join keeps Ankara and Izmir, the left join adds Erzurum with "
             "a NaN plate, the outer join also adds Trabzon with a NaN "
             "temperature."))


# ============================================================
# zaman: Ankara daily values, 31-day centred mean and monthly means
# ============================================================
def fig_zaman():
    raw = DF[DF["istasyon"] == "Ankara"].set_index("tarih")["sicaklik"]
    ank = raw.interpolate()
    smooth = ank.rolling(31, center=True).mean()
    monthly = raw.resample("ME").mean()
    mid = monthly.index - pd.Timedelta(days=15)
    t0 = pd.Timestamp("2025-01-01")

    def day(ts):
        return (ts - t0).days

    W, H = 680, 330
    p = Plot(56, 50, 590, 230, (0, 364), (-7, 34))
    p.grid([], [0, 10, 20, 30])
    p.axes([], [0, 10, 20, 30], "", "°C")
    starts = pd.date_range("2025-01-01", periods=12, freq="MS")
    names = ["Oca", "Şub", "Mar", "Nis", "May", "Haz", "Tem", "Ağu", "Eyl",
             "Eki", "Kas", "Ara"]
    for k, st in enumerate(starts):
        d = day(st)
        p.add(f'<line x1="{p.X(d):.1f}" y1="{p.y0 + p.h:.1f}" '
              f'x2="{p.X(d):.1f}" y2="{p.y0 + p.h + 5:.1f}" stroke="{TEXT}" '
              f'stroke-width="1" opacity="0.5"/>')
        p.label(d + 15, -7, names[k], 0, 17, TEXT, 11, "middle")
    p.line([(day(ts), v) for ts, v in ank.items()], THEORY, 0.9, None, 0.55)
    sm = smooth.dropna()
    p.line([(day(ts), v) for ts, v in sm.items()], PRACTICE, 2.6)
    p.points([(day(ts), v) for ts, v in zip(mid, monthly)], BASE, 4.2)
    # legend inside the cold, empty upper-left corner
    LX, LY = p.x0 + 14, p.y0 + 4
    p.add(f'<line x1="{LX:.1f}" y1="{LY:.1f}" x2="{LX + 22:.1f}" '
          f'y2="{LY:.1f}" stroke="{THEORY}" stroke-width="1.2" '
          f'opacity="0.7"/>')
    txt(p, LX + 30, LY + 4, "günlük", TEXT, 11.5, "start")
    p.add(f'<line x1="{LX:.1f}" y1="{LY + 20:.1f}" x2="{LX + 22:.1f}" '
          f'y2="{LY + 20:.1f}" stroke="{PRACTICE}" stroke-width="2.6"/>')
    txt(p, LX + 30, LY + 24, "31 günlük ortalama", TEXT, 11.5, "start")
    p.add(f'<circle cx="{LX + 11:.1f}" cy="{LY + 40:.1f}" r="4.2" '
          f'fill="{BASE}"/>')
    txt(p, LX + 30, LY + 44, "aylık ortalama", TEXT, 11.5, "start")
    save("zaman", figure(
        W, H, [p],
        "Ankara'nın 2025 sıcaklıkları; grafik çizme kodunun çizdiği üç "
        "katman. İnce çizgi eksikleri interpolasyonla doldurulmuş günlük "
        "değerlerdir. Kalın çizgi 31 günlük merkezî hareketli ortalamadır ve "
        "baştaki ile sondaki 15 günde tanımlı değildir. Noktalar "
        "<code>resample(\"ME\").mean()</code> ile bulunan aylık "
        "ortalamalardır ve ay ortalarına yerleştirilmiştir. Hareketli "
        "ortalama günlük gürültüyü bastırır, mevsim dalgası kalır.",
        WIDE,
        aria="Daily temperatures of Ankara in 2025 as a thin noisy line "
             "from about -5 to 31 degrees, a thick smooth 31-day centred "
             "moving average following a seasonal wave with minimum in "
             "January and maximum in July, and twelve dots for the monthly "
             "means placed at mid-month."))


if __name__ == "__main__":
    fig_hizalama()
    fig_dataframe()
    fig_eksik()
    fig_groupby()
    fig_kutu()
    fig_merge()
    fig_zaman()
