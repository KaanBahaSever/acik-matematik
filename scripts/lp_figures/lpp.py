# -*- coding: utf-8 -*-
"""
Figures of the chapter "Lineer Programlama Problemi, Kanonik ve Standart Formlar"
(dersler/lineer-programlama/lineer-programlama-problemi.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution,
exercise or callout), never inside a definition box: a figure that
illustrates a definition sits directly below that box. The figures are NOT
produced at build time. Run

    python scripts/lp_figures/lpp.py
    python scripts/center_figures.py "lp-lpp-*.md" --keep-width
    python scripts/check_figure_labels.py "scripts/_figures/lp-lpp-*.md"

and paste the markup of scripts/_figures/lp-lpp-<name>.md into the .qmd.
The captions are Turkish on purpose (they are shown on the site); the aria
labels are plain ASCII.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, TEXT, THEORY, PRACTICE, BASE, REMARK  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "lp-lpp-"

MINUS = "&#8722;"
SUB = {"1": "&#8321;", "2": "&#8322;", "3": "&#8323;", "4": "&#8324;", "5": "&#8325;"}


def x(i):
    """x with a Unicode subscript digit."""
    return "x" + SUB[str(i)]


def save(name, markup):
    path = OUT_DIR / f"{PREFIX}{name}.md"
    path.write_text(markup, encoding="utf-8", newline="\n")
    print("wrote", path.name)


# ============================================================
# akis: general problem -> canonical -> standard -> solvable form
# ============================================================
def flowchart():
    W, H = 560, 560
    p = Plot(0, 0, W, H, (0, W), (H, 0))   # data y grows downward = pixels

    box_x0, box_x1 = 20, 540
    box_h = 62
    tops = [14, 166, 318, 470]
    boxes = [
        (BASE, "Genel problem",
         "kısıtlar ≤, ≥, = karışık; sağ taraf negatif, değişken işaretsiz olabilir"),
        (THEORY, "Kanonik form",
         "max: bütün kısıtlar ≤;  min: bütün kısıtlar ≥;  bütün değişkenler ≥ 0"),
        (PRACTICE, "Standart form",
         "bütün kısıtlar eşitlik;  bütün sağ taraflar ≥ 0;  bütün değişkenler ≥ 0"),
        (REMARK, "Simpleks yöntem ile çözülebilir hal",
         "standart form + katsayılar matrisinde m × m birim matris"),
    ]
    for (col, title, desc), top in zip(boxes, tops):
        p.add(f'<rect x="{box_x0}" y="{top}" width="{box_x1 - box_x0}" height="{box_h}" rx="9" '
              f'fill="{col}" fill-opacity="0.10" stroke="{col}" stroke-width="1.6"/>')
        cx = (box_x0 + box_x1) / 2
        p.text_px(cx, top + 26, title, col, 15, "middle", bold=True)
        p.text_px(cx, top + 48, desc, TEXT, 12.5, "middle")

    steps = [
        ["max'ta ≥ kısıtı, min'de ≤ kısıtı " + MINUS + "1 ile çarpılır",
         "eşitlik kısıtı iki eşitsizliğe ayrılır",
         "işaretsiz değişken x' " + MINUS + " x'' , x ≤ 0 olan değişken " + MINUS + "x' yazılır"],
        ["sağ tarafı negatif olan satır " + MINUS + "1 ile çarpılır",
         "≤ kısıta aylak (slack) değişken eklenir",
         "≥ kısıttan artık (surplus) değişken çıkarılır"],
        ["birim sütunu olmayan satıra yapay değişken eklenir",
         "yapay değişkenin amaç katsayısı: min için +M, max için " + MINUS + "M"],
    ]
    ax = 52
    for k, lines in enumerate(steps):
        y0 = tops[k] + box_h
        y1 = tops[k + 1]
        p.arrow((ax, y0 + 4), (ax, y1 - 3), TEXT, 1.8, 10, opacity=0.75)
        n = len(lines)
        mid = (y0 + y1) / 2
        first = mid - (n - 1) * 19 / 2 + 5
        for i, s in enumerate(lines):
            p.text_px(ax + 24, first + i * 19, s, TEXT, 13)

    cap = ("Bir lineer programlama problemini simpleks yöntem ile çözülebilir hale getirme. "
           "Okların yanında her geçişte yapılan işlemler yazılıdır.")
    aria = ("Flowchart: general problem, then canonical form, then standard form, "
            "then the form solvable by the simplex method; the operations of each step are written next to the arrows.")
    save("akis", figure(W, H, [p], cap, aria=aria))


# ============================================================
# aylak: production example, slack variables on the constraint lines
# ============================================================
def slack_region():
    W, H = 560, 470
    p = Plot(58, 30, 420, 390, (0, 88), (0, 108))
    p.grid(xs=(20, 40, 60, 80), ys=(20, 40, 60, 80, 100))
    p.axes((0, 20, 40, 60, 80), (20, 40, 60, 80, 100), x(1), x(2))
    region = [(0, 0), (40, 0), (40, 20), (20, 60), (0, 80)]
    p.polygon(region, THEORY, 0.14)
    # constraint lines clipped to the panel
    p.line([(0, 100), (50, 0)], BASE, 2.0)           # 2x1 + x2 = 100
    p.line([(0, 80), (80, 0)], PRACTICE, 2.0)        # x1 + x2 = 80
    p.line([(40, 0), (40, 106)], REMARK, 2.0)        # x1 = 40
    # labels
    p.label(12, 86, "2" + x(1) + " + " + x(2) + " = 100", 8, 0, BASE, 13)
    p.label(12, 86, "(" + x(3) + " = 0)", 8, 17, BASE, 13)
    p.label(66, 29, x(1) + " + " + x(2) + " = 80", 8, 0, PRACTICE, 13)
    p.label(66, 29, "(" + x(4) + " = 0)", 8, 17, PRACTICE, 13)
    p.label(40, 101, x(1) + " = 40", 8, 0, REMARK, 13)
    p.label(40, 101, "(" + x(5) + " = 0)", 8, 17, REMARK, 13)
    # points
    p.points([(20, 50), (40, 20)], PRACTICE, 4.5)
    p.label(20, 50, "P(20, 50)", -9, -8, TEXT, 13.5, "end")
    p.label(40, 20, "Q(40, 20)", 9, 18, TEXT, 13.5)

    cap = ("Üretim örneğinin kısıtları ve boyalı uygun bölge. Her kısıt doğrusu üzerinde o kısıtın aylak "
           "değişkeni sıfırdır. İçerideki P(20, 50) noktasında x₃ = 10, x₄ = 10, x₅ = 20; "
           "Q(40, 20) noktasında x₃ = 0, x₄ = 20, x₅ = 0.")
    aria = ("Feasible region of the production example bounded by 2x1 + x2 = 100, x1 + x2 = 80 and x1 = 40; "
            "on each line the corresponding slack variable is zero; points P(20,50) and Q(40,20).")
    save("aylak", figure(W, H, [p], cap, aria=aria))


if __name__ == "__main__":
    flowchart()
    slack_region()
