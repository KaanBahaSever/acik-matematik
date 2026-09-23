# -*- coding: utf-8 -*-
"""
Figures of the chapter "Hipergeometrik, Geometrik ve Negatif Binom Dağılımları"
(dersler/matematiksel-istatistik/hipergeometrik-geometrik-ve-negatif-binom.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
callout), never inside a definition box: a figure that illustrates a
definition sits directly below that box. The figures are NOT produced at
build time. Run

    python scripts/statistics_figures/hgn.py
    python scripts/center_figures.py "statistics-hgn-*.md" --keep-width
    python scripts/check_figure_labels.py "scripts/_figures/statistics-hgn-*.md"

and paste the markup of scripts/_figures/statistics-hgn-<name>.md into the .qmd.

Captions are Turkish plain text (no LaTeX); aria labels are plain ASCII.
"""
import sys
from math import comb
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, WIDE, TEXT, THEORY, PRACTICE, BASE, REMARK  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "statistics-hgn-"


def save(name, markup):
    (OUT_DIR / f"{PREFIX}{name}.md").write_text(markup, encoding="utf-8", newline="\n")
    print("wrote", PREFIX + name)


def dec(v, nd=2):
    """Decimal comma: dec(0.25) -> '0,25'."""
    return f"{v:.{nd}f}".replace(".", ",")


def I(s):
    return f'<tspan font-style="italic">{s}</tspan>'


def sub(s):
    return f'<tspan font-size="11" dy="4">{s}</tspan><tspan dy="-4">&#8203;</tspan>'


def sup(s):
    return f'<tspan font-size="11" dy="-6">{s}</tspan><tspan dy="6">&#8203;</tspan>'


def rect(p, x, y, w, color, opacity=0.75, stroke_op=1.0):
    """Bar centred at data x with pixel width w and data height y."""
    X, Y0, Y1 = p.X(x), p.Y(0), p.Y(y)
    p.add(f'<rect x="{X - w / 2:.1f}" y="{Y1:.1f}" width="{w:.1f}" height="{max(Y0 - Y1, 0.6):.1f}" '
          f'fill="{color}" fill-opacity="{opacity}" stroke="{color}" stroke-width="0.9" '
          f'stroke-opacity="{stroke_op}"/>')


def legend(p, px, py, items, size=12, gap=19):
    """items: (color, text, kind), kind 'bar', 'line', 'dot' or 'ring<r>'; top-left corner at pixel (px, py)."""
    for i, (color, text, kind) in enumerate(items):
        y = py + i * gap
        if kind == "bar":
            p.add(f'<rect x="{px:.1f}" y="{y - 9:.1f}" width="14" height="10" fill="{color}" '
                  f'fill-opacity="0.75" stroke="{color}" stroke-width="0.9"/>')
        else:
            p.add(f'<line x1="{px - 1:.1f}" y1="{y - 4:.1f}" x2="{px + 15:.1f}" y2="{y - 4:.1f}" '
                  f'stroke="{color}" stroke-width="{2.0 if kind == "line" else 1.2}"/>')
            if kind == "dot":
                p.add(f'<circle cx="{px + 7:.1f}" cy="{y - 4:.1f}" r="3.4" fill="{color}"/>')
            elif kind.startswith("ring"):
                r = float(kind[4:])
                p.add(f'<circle cx="{px + 7:.1f}" cy="{y - 4:.1f}" r="{r}" fill="none" '
                      f'stroke="{color}" stroke-width="1.8"/>')
        p.text_px(px + 21, y, text, color, size)


# ============================================================
# siyah-top: HG(15, 5, 5), the event X >= 3 highlighted
# ============================================================
def fig_siyah_top():
    N, a, n = 15, 5, 5
    pm = [comb(a, x) * comb(N - a, n - x) / comb(N, n) for x in range(n + 1)]
    p = Plot(60, 30, 460, 220, (-0.6, 5.6), (0, 0.45))
    p.grid(ys=(0.1, 0.2, 0.3, 0.4))
    p.axes(range(6), (0.1, 0.2, 0.3, 0.4), xlabel="x", yfmt=lambda v: dec(v, 1))
    for x, v in enumerate(pm):
        color = PRACTICE if x >= 3 else THEORY
        rect(p, x, v, 34, color, 0.75 if x >= 3 else 0.45)
        nd = 4 if v < 0.01 else 3
        p.label(x, v, dec(v, nd), 0, -7, color, 11.5, "middle")
    legend(p, 330, 60, [(THEORY, "siyah top sayısı en çok 2", "bar"),
                        (PRACTICE, "siyah top sayısı en az 3", "bar")])
    p.text_px(35, 22, "P(X = x)", TEXT, 12, "start", italic=True)
    cap = ("15 toptan (5 siyah, 10 beyaz) iadesiz çekilen 5 top arasındaki siyah top sayısı <em>X</em>'in "
           "olasılık fonksiyonu. Siyahların beyazlardan çok olduğu durumlar <em>x</em> = 3, 4, 5 çubuklarıdır; "
           "toplam alanları 167/1001 &#8776; 0,167'dir.")
    save("siyah-top", figure(560, 290, [p], cap,
                             aria="Hypergeometric pmf N=15 a=5 n=5, bars x at least 3 highlighted"))


# ============================================================
# hg-binom: HG(15, 5, 5) against Binom(5, 1/3), same mean
# ============================================================
def fig_hg_binom():
    N, a, n = 15, 5, 5
    hg = [comb(a, x) * comb(N - a, n - x) / comb(N, n) for x in range(n + 1)]
    bi = [comb(n, x) * (1 / 3) ** x * (2 / 3) ** (n - x) for x in range(n + 1)]
    p = Plot(60, 30, 460, 220, (-0.6, 5.6), (0, 0.45))
    p.grid(ys=(0.1, 0.2, 0.3, 0.4))
    p.axes(range(6), (0.1, 0.2, 0.3, 0.4), xlabel="x", yfmt=lambda v: dec(v, 1))
    for x in range(n + 1):
        rect(p, x - 0.15, hg[x], 24, THEORY, 0.6)
        rect(p, x + 0.15, bi[x], 16, PRACTICE, 0.75)
    mu = 5 / 3
    p.vline(mu, 0, 0.43, TEXT, "5 4", 0.6)
    p.label(mu, 0.43, "E(X) = 5/3", 6, 4, TEXT, 12)
    legend(p, 330, 70, [(THEORY, "iadesiz: HG(15, 5, 5)", "bar"),
                        (PRACTICE, "iadeli: Binom(5, 1/3)", "bar")])
    p.text_px(35, 22, "P(X = x)", TEXT, 12, "start", italic=True)
    cap = ("Aynı torbadan iadesiz (hipergeometrik, geniş mavi) ve iadeli (binom, ince turuncu) çekilen 5 top "
           "arasındaki siyah top sayısının dağılımı. Beklenen değer ikisinde de 5/3'tür; iadesiz çekilişte "
           "olasılık ortaya daha çok toplanır ve varyans 10/9 yerine 50/63 olur.")
    save("hg-binom", figure(560, 290, [p], cap,
                            aria="Hypergeometric N=15 a=5 n=5 versus binomial n=5 p=1/3, same mean 5/3"))


# ============================================================
# duzeltme-faktoru: (N - n)/(N - 1) as a function of N
# ============================================================
def fig_duzeltme():
    p = Plot(60, 30, 460, 220, (0, 200), (0, 1.08))
    p.grid(xs=(50, 100, 150, 200), ys=(0.2, 0.4, 0.6, 0.8, 1.0))
    p.axes((0, 50, 100, 150, 200), (0.2, 0.4, 0.6, 0.8, 1.0), xlabel="N",
           yfmt=lambda v: dec(v, 1))
    p.line([(0, 1), (200, 1)], TEXT, 1.0, "4 3", 0.5)
    items = []
    for n, color in ((5, THEORY), (10, BASE), (20, PRACTICE)):
        pts = []
        steps = 400
        for i in range(steps + 1):
            N = n + (200 - n) * i / steps
            pts.append((N, (N - n) / (N - 1)))
        p.line(pts, color, 2.0)
        items.append((color, I("n") + f" = {n}", "line"))
    legend(p, 400, 185, items)
    p.text_px(35, 20, "(N &#8722; n)/(N &#8722; 1)", TEXT, 12, "start", italic=True)
    cap = ("Düzeltme faktörü (<em>N</em> &#8722; <em>n</em>)/(<em>N</em> &#8722; 1), kitle büyüklüğü <em>N</em>'nin "
           "fonksiyonu olarak, üç farklı örneklem büyüklüğü <em>n</em> için. <em>N</em> = <em>n</em> iken faktör 0'dır; "
           "<em>n</em> sabit kalıp <em>N</em> büyüdükçe 1'e yaklaşır. <em>n</em> ne kadar büyükse yaklaşma o kadar yavaştır.")
    save("duzeltme-faktoru", figure(560, 290, [p], cap,
                                    aria="Finite population correction (N-n)/(N-1) versus N for n = 5, 10, 20"))


# ============================================================
# geometrik-aile: Geo(p) for three values of p
# ============================================================
def fig_geometrik_aile():
    p = Plot(60, 30, 600, 230, (0.4, 10.6), (0, 0.8))
    p.grid(ys=(0.2, 0.4, 0.6))
    p.axes(range(1, 11), (0.2, 0.4, 0.6), xlabel="x", yfmt=lambda v: dec(v, 1))
    series = ((0.2, BASE, I("p") + " = 0,2"), (0.5, THEORY, I("p") + " = 0,5"),
              (0.75, PRACTICE, I("p") + " = 0,75"))
    for j, (pp, color, _) in enumerate(series):
        for x in range(1, 11):
            rect(p, x + (j - 1) * 0.26, (1 - pp) ** (x - 1) * pp, 14, color, 0.7)
    legend(p, 480, 60, [(c, t, "bar") for _, c, t in series])
    p.text_px(35, 22, "P(X = x)", TEXT, 12, "start", italic=True)
    cap = ("Geometrik dağılımın olasılık fonksiyonu <em>q</em><sup>x&#8722;1</sup><em>p</em>, üç farklı başarı "
           "olasılığı için. Her durumda olasılıklar <em>x</em> = 1'den başlayıp her adımda <em>q</em> = 1 &#8722; <em>p</em> "
           "oranında küçülür; <em>p</em> küçüldükçe dağılım sağa yayılır ve ilk başarı daha geç gelir.")
    save("geometrik-aile", figure(700, 300, [p], cap, WIDE,
                                  aria="Geometric pmf for p = 0.2, 0.5 and 0.75, x from 1 to 10"))


# ============================================================
# negatif-binom-aile: NB(k, 1/2) for k = 1, 2, 3, 5
# ============================================================
def fig_nb_aile():
    p = Plot(60, 30, 600, 230, (0.5, 20.5), (0, 0.55))
    p.grid(ys=(0.1, 0.2, 0.3, 0.4, 0.5))
    p.axes((1, 5, 10, 15, 20), (0.1, 0.2, 0.3, 0.4, 0.5), xlabel="x", yfmt=lambda v: dec(v, 1))
    q = 0.5
    # filled dots for k = 1, 3 and rings of two sizes for k = 2, 5, so that
    # coinciding values (x = 2, 4, 5, 6) stay visible
    style = {1: (THEORY, "dot"), 2: (BASE, "ring4.6"), 3: (PRACTICE, "dot"), 5: (REMARK, "ring6.2")}
    series = {k: [(x, comb(x - 1, k - 1) * q ** (x - k) * (1 - q) ** k) for x in range(k, 21)]
              for k in style}
    for k, (color, _) in style.items():
        p.line(series[k], color, 1.1, "3 3", 0.7)
    for k in (1, 3, 2, 5):
        color, kind = style[k]
        if kind == "dot":
            p.points(series[k], color, 3.4)
        else:
            p.hollow_points(series[k], color, float(kind[4:]))
    items = [(style[k][0], I("k") + f" = {k}", style[k][1]) for k in (1, 2, 3, 5)]
    legend(p, 520, 55, items)
    p.text_px(35, 22, "P(X = x)", TEXT, 12, "start", italic=True)
    cap = ("Başarı olasılığı <em>p</em> = 0,5 iken <em>k</em>-ıncı başarıya kadar yapılan deneme sayısının "
           "(negatif binom) olasılık fonksiyonu. <em>k</em> = 1 geometrik dağılımdır. <em>k</em> arttıkça dağılım "
           "<em>x</em> = <em>k</em>'dan başlar, sağa kayar ve yayılır; beklenen değer <em>k</em>/<em>p</em> = 2<em>k</em>'dır.")
    save("negatif-binom-aile", figure(700, 300, [p], cap, WIDE,
                                      aria="Negative binomial pmf with p = 0.5 for k = 1, 2, 3, 5"))


# ============================================================
# geometrik-toplam: a trial sequence split into k = 3 geometric waits
# ============================================================
def fig_geometrik_toplam():
    seq = ["F", "S", "F", "F", "S", "S"]       # failure / success
    p = Plot(0, 0, 700, 200, (0, 700), (0, 200))
    x0, w, gap, y = 70, 70, 20, 60
    centers = []
    for i, s in enumerate(seq):
        cx = x0 + i * (w + gap) + w / 2
        centers.append(cx)
        color = PRACTICE if s == "S" else THEORY
        op = 0.30 if s == "S" else 0.10
        p.add(f'<rect x="{cx - w / 2:.1f}" y="{y:.1f}" width="{w}" height="46" rx="6" fill="{color}" '
              f'fill-opacity="{op}" stroke="{color}" stroke-width="1.6"/>')
        txt = "B" if s == "S" else "B" + sup("c")
        p.text_px(cx, y + 29, txt, color, 16, "middle", italic=True)
        p.text_px(cx, y - 12, f"{i + 1}. deneme", TEXT, 11.5, "middle")
    groups = ((0, 1, "1"), (2, 4, "2"), (5, 5, "3"))
    vals = ("2", "3", "1")
    for (i0, i1, idx), v in zip(groups, vals):
        left = centers[i0] - w / 2 + 2
        right = centers[i1] + w / 2 - 2
        yb = y + 60
        p.add(f'<path d="M{left:.1f},{yb:.1f} L{left:.1f},{yb + 8:.1f} L{right:.1f},{yb + 8:.1f} '
              f'L{right:.1f},{yb:.1f}" fill="none" stroke="{TEXT}" stroke-width="1.3" opacity="0.7"/>')
        p.text_px((left + right) / 2, yb + 30, I("X") + sub(idx) + " = " + v, TEXT, 14, "middle")
    cap = ("Üçüncü başarının altıncı denemede geldiği bir dizi. Dizi başarılardan sonra kesilince üç bekleme "
           "süresine ayrılır: <em>X</em><sub>1</sub> = 2, <em>X</em><sub>2</sub> = 3, <em>X</em><sub>3</sub> = 1. "
           "Toplam deneme sayısı <em>X</em> = <em>X</em><sub>1</sub> + <em>X</em><sub>2</sub> + <em>X</em><sub>3</sub> = 6'dır.")
    save("geometrik-toplam", figure(700, 200, [p], cap, WIDE,
                                    aria="Six Bernoulli trials F S F F S S split into geometric waits 2, 3 and 1"))


# ============================================================
# uc-isabet: NB(3, 3/4), the event X >= 4 highlighted
# ============================================================
def fig_uc_isabet():
    k, pp = 3, 0.75
    q = 1 - pp
    p = Plot(60, 30, 460, 220, (2.4, 10.6), (0, 0.48))
    p.grid(ys=(0.1, 0.2, 0.3, 0.4))
    p.axes(range(3, 11), (0.1, 0.2, 0.3, 0.4), xlabel="x", yfmt=lambda v: dec(v, 1))
    for x in range(3, 11):
        v = comb(x - 1, k - 1) * q ** (x - k) * pp ** k
        color = PRACTICE if x >= 4 else THEORY
        rect(p, x, v, 30, color, 0.75 if x >= 4 else 0.45)
        if x <= 7:
            p.label(x, v, dec(v, 3), 0, -7, color, 11.5, "middle")
    legend(p, 330, 60, [(THEORY, "x = 3: ilk üç atış isabet", "bar"),
                        (PRACTICE, "x &#8805; 4: en az dört atış", "bar")])
    p.text_px(35, 22, "P(X = x)", TEXT, 12, "start", italic=True)
    cap = ("Üç isabete kadar yapılan atış sayısı <em>X</em>'in olasılık fonksiyonu (<em>k</em> = 3, <em>p</em> = 0,75). "
           "En az dört atış olayı turuncu çubukların hepsidir; olasılığını tek mavi çubuğu 1'den çıkararak "
           "buluruz: 1 &#8722; 27/64 = 37/64.")
    save("uc-isabet", figure(560, 290, [p], cap,
                             aria="Negative binomial pmf k=3 p=0.75, bars x at least 4 highlighted"))


if __name__ == "__main__":
    fig_siyah_top()
    fig_hg_binom()
    fig_duzeltme()
    fig_geometrik_aile()
    fig_nb_aile()
    fig_geometrik_toplam()
    fig_uc_isabet()
