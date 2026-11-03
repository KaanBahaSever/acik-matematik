# -*- coding: utf-8 -*-
"""
Figures of the course "Bilgisayar Programlama" (dersler/bilgisayar-programlama):
flow charts of an algorithm, of if/else, if/elif/else and while, and the index
diagram of a list.

Figures go INSIDE the box they explain (example, solution or callout), never
inside a definition box (right below it instead) and never directly under a
heading. The figures are NOT produced at build time. Run

    python scripts/programming_figures.py
    python scripts/center_figures.py "programming-*.md"
    python scripts/check_figure_labels.py "scripts/_figures/programming-*.md"

and paste the markup of scripts/_figures/programming-<name>.md into the .qmd.
Captions are Turkish on purpose; aria labels are plain ASCII.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svg_plot import Plot, figure, TEXT, THEORY, PRACTICE, BASE, WIDE  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parent / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "programming-"
LW = 1.4       # stroke width of the arrows
HEAD = 7       # arrowhead size


def save(name, markup):
    (OUT_DIR / f"{PREFIX}{name}.md").write_text(markup, encoding="utf-8", newline="\n")
    print(f"{PREFIX}{name}.md")


def pixel_plot(W, H):
    """A Plot whose data coordinates are the pixel coordinates (y down)."""
    return Plot(0, 0, W, H, (0, W), (H, 0))


def box(p, cx, cy, w, h, color, fill_op=0.10, rx=6):
    """Process step: a rounded rectangle."""
    p.add(f'<rect x="{cx - w / 2:.1f}" y="{cy - h / 2:.1f}" width="{w:.1f}" height="{h:.1f}" '
          f'rx="{rx}" fill="{color}" fill-opacity="{fill_op}" stroke="{color}" stroke-width="1.5"/>')


def terminal(p, cx, cy, w, h, color):
    """Start / end of a flow chart: a stadium shape."""
    box(p, cx, cy, w, h, color, 0.10, rx=h / 2)


def io_box(p, cx, cy, w, h, color, slant=12):
    """Input / output step: a parallelogram."""
    x0, x1, y0, y1 = cx - w / 2, cx + w / 2, cy - h / 2, cy + h / 2
    pts = f"{x0 + slant:.1f},{y0:.1f} {x1 + slant / 2:.1f},{y0:.1f} {x1 - slant:.1f},{y1:.1f} {x0 - slant / 2:.1f},{y1:.1f}"
    p.add(f'<polygon points="{pts}" fill="{color}" fill-opacity="0.10" '
          f'stroke="{color}" stroke-width="1.5"/>')


def diamond(p, cx, cy, hw, hh, color, fill_op=0.08):
    """Decision: a diamond."""
    pts = f"{cx:.1f},{cy - hh:.1f} {cx + hw:.1f},{cy:.1f} {cx:.1f},{cy + hh:.1f} {cx - hw:.1f},{cy:.1f}"
    p.add(f'<polygon points="{pts}" fill="{color}" fill-opacity="{fill_op}" '
          f'stroke="{color}" stroke-width="1.5"/>')


# ============================================================
# 1. Flow chart of the averaging algorithm
# ============================================================
def fig_algorithm():
    W, H = 660, 104
    p = pixel_plot(W, H)
    cy = 52
    xs = [52, 178, 330, 482, 608]
    widths = [80, 120, 132, 116, 80]
    terminal(p, xs[0], cy, widths[0], 36, BASE)
    io_box(p, xs[1], cy, widths[1], 40, PRACTICE)
    box(p, xs[2], cy, widths[2], 40, THEORY)
    io_box(p, xs[3], cy, widths[3], 40, PRACTICE)
    terminal(p, xs[4], cy, widths[4], 36, BASE)
    labels = [("Başla", BASE), ("a ve b'yi al", PRACTICE), ("o = (a + b) / 2", THEORY),
              ("o'yu yaz", PRACTICE), ("Bitir", BASE)]
    for x, (s, c) in zip(xs, labels):
        p.label(x, cy, s, 0, 4.5, c, 12.5, "middle", True)
    for k in range(4):
        x0 = xs[k] + widths[k] / 2 + (4 if k in (1, 3) else 2)
        x1 = xs[k + 1] - widths[k + 1] / 2 - (6 if k + 1 in (1, 3) else 2)
        p.arrow((x0, cy), (x1, cy), TEXT, LW, head=HEAD)
    p.label(xs[1], cy + 34, "girdi", 0, 0, TEXT, 10.5, "middle")
    p.label(xs[2], cy + 34, "işlem", 0, 0, TEXT, 10.5, "middle")
    p.label(xs[3], cy + 34, "çıktı", 0, 0, TEXT, 10.5, "middle")
    cap = ("Ortalama algoritmasının akış şeması. Oval kutular başlangıcı ve bitişi, eğik kutular "
           "girdi ve çıktıyı, dikdörtgen kutu bir hesabı gösterir; oklar adımların sırasını verir.")
    aria = ("Flow chart from left to right: start, read a and b, compute o equals a plus b over 2, "
            "print o, end")
    save("algoritma-ortalama", figure(W, H, [p], cap, WIDE, aria))


# ============================================================
# 2. Flow chart of if / else
# ============================================================
def fig_if_else():
    W, H = 560, 250
    p = pixel_plot(W, H)
    cx, dy = 280, 74
    hw, hh = 92, 42
    lx, rx, by = 110, 450, 150
    p.arrow((cx, 10), (cx, dy - hh), TEXT, LW, head=HEAD)
    diamond(p, cx, dy, hw, hh, THEORY)
    p.label(cx, dy, "koşul", 0, -3, THEORY, 12.5, "middle", True)
    p.label(cx, dy, "doğru mu?", 0, 13, THEORY, 11.5, "middle")
    # True to the left, False to the right
    p.line([(cx - hw, dy), (lx, dy)], TEXT, LW)
    p.arrow((lx, dy), (lx, by - 18), TEXT, LW, head=HEAD)
    p.label((cx - hw + lx) / 2, dy, "Evet", 0, -7, TEXT, 11.5, "middle")
    p.line([(cx + hw, dy), (rx, dy)], TEXT, LW)
    p.arrow((rx, dy), (rx, by - 18), TEXT, LW, head=HEAD)
    p.label((cx + hw + rx) / 2, dy, "Hayır", 0, -7, TEXT, 11.5, "middle")
    for x, s in ((lx, "if bloğu"), (rx, "else bloğu")):
        box(p, x, by, 150, 36, BASE)
        p.label(x, by, s, 0, 4.5, BASE, 12.5, "middle", True)
    # common exit
    ey = 222
    for x in (lx, rx):
        p.line([(x, by + 18), (x, ey - 26)], TEXT, LW)
    p.line([(lx, ey - 26), (rx, ey - 26)], TEXT, LW)
    p.arrow((cx, ey - 26), (cx, ey - 14), TEXT, LW, head=HEAD)
    box(p, cx, ey, 270, 28, TEXT, 0.06)
    p.label(cx, ey, "yapıdan sonraki ilk satır", 0, 4.5, TEXT, 12, "middle")
    cap = ("Bir <code>if-else</code> yapısının akışı. Koşul doğruysa yalnız <code>if</code> bloğu, "
           "yanlışsa yalnız <code>else</code> bloğu çalışır; iki yol da yapıdan sonraki satırda birleşir.")
    aria = ("Flow chart: the condition is tested; if true the if block runs, otherwise the else block "
            "runs; both paths join at the next line")
    save("kosul-if-else", figure(W, H, [p], cap, WIDE, aria))


# ============================================================
# 3. Flow chart of if / elif / else
# ============================================================
def fig_elif():
    W, H = 640, 300
    p = pixel_plot(W, H)
    d1, d2, b3x = 105, 330, 545
    row1, row2, row3 = 95, 190, 268
    hw, hh = 82, 42
    p.arrow((d1, 14), (d1, row1 - hh), TEXT, LW, head=HEAD)
    for cx, k in ((d1, 1), (d2, 2)):
        diamond(p, cx, row1, hw, hh, THEORY)
        p.label(cx, row1, f"koşul{k}", 0, -3, THEORY, 12, "middle", True)
        p.label(cx, row1, "doğru mu?", 0, 13, THEORY, 11.5, "middle")
    p.arrow((d1 + hw, row1), (d2 - hw, row1), TEXT, LW, head=HEAD)
    p.label((d1 + d2) / 2, row1, "Hayır", 0, -7, TEXT, 11.5, "middle")
    p.line([(d2 + hw, row1), (b3x, row1)], TEXT, LW)
    p.arrow((b3x, row1), (b3x, row2 - 18), TEXT, LW, head=HEAD)
    p.label((d2 + hw + b3x) / 2, row1, "Hayır", 0, -7, TEXT, 11.5, "middle")
    for cx in (d1, d2):
        p.arrow((cx, row1 + hh), (cx, row2 - 18), TEXT, LW, head=HEAD)
        p.label(cx, (row1 + hh + row2 - 18) / 2, "Evet", 7, 4, TEXT, 11.5, "start")
    for cx, s in ((d1, "if bloğu"), (d2, "elif bloğu"), (b3x, "else bloğu")):
        box(p, cx, row2, 130, 36, BASE)
        p.label(cx, row2, s, 0, 4.5, BASE, 12.5, "middle", True)
    for cx in (d1, d2, b3x):
        p.arrow((cx, row2 + 18), (cx, row3 - 16), TEXT, LW, head=HEAD)
    box(p, (d1 + b3x) / 2, row3, b3x - d1 + 150, 32, TEXT, 0.06)
    p.label((d1 + b3x) / 2, row3, "yapıdan sonraki ilk satır", 0, 4.5, TEXT, 12.5, "middle")
    cap = ("Bir <code>if-elif-else</code> yapısının akışı. Koşullar yazıldıkları sırayla denenir; "
           "doğru çıkan ilk koşulun bloğu çalışır ve geri kalanlara bakılmaz. Hiçbir koşul doğru "
           "değilse <code>else</code> bloğu çalışır.")
    aria = ("Flow chart: condition 1 is tested; if true the if block runs, otherwise condition 2 is "
            "tested; if true the elif block runs, otherwise the else block runs; all paths join")
    save("kosul-elif", figure(W, H, [p], cap, WIDE, aria))


# ============================================================
# 4. Positive and negative indices of a list
# ============================================================
def fig_indices():
    items = ["elma", "armut", "kiraz", "portakal", "muz", "çilek"]
    n = len(items)
    W, H = 640, 150
    p = pixel_plot(W, H)
    cw, ch = 96, 40
    x0 = (W - n * cw) / 2
    cy = 76
    for k, s in enumerate(items):
        cx = x0 + cw * k + cw / 2
        box(p, cx, cy, cw, ch, THEORY, 0.08, rx=0)
        p.label(cx, cy, f'"{s}"', 0, 4.5, TEXT, 12.5, "middle")
        p.label(cx, cy - ch / 2, str(k), 0, -10, BASE, 13, "middle", True)
        p.label(cx, cy + ch / 2, f"&#8722;{n - k}", 0, 22, PRACTICE, 13, "middle", True)
    p.label(x0 - 10, cy - ch / 2 - 10, "indeks", 0, 0, BASE, 11.5, "end")
    p.label(x0 - 10, cy + ch / 2 + 22, "negatif", 0, 0, PRACTICE, 11.5, "end")
    p.label(x0 - 10, cy + 4.5, "meyve", 0, 0, TEXT, 11.5, "end", True)
    cap = ("Altı elemanlı <code>meyve</code> listesinin indeksleri. Üstteki indeksler baştan 0'dan "
           "başlayarak, alttaki negatif indeksler sondan &#8722;1'den başlayarak sayılır; örneğin "
           "<code>meyve[2]</code> ve <code>meyve[-4]</code> aynı eleman olan <code>\"kiraz\"</code>'dır.")
    aria = ("Six boxes holding elma, armut, kiraz, portakal, muz, cilek; indices 0 to 5 above and "
            "minus 6 to minus 1 below")
    save("liste-indeksleri", figure(W, H, [p], cap, WIDE, aria))


# ============================================================
# 5. Flow chart of while
# ============================================================
def fig_while():
    W, H = 560, 250
    p = pixel_plot(W, H)
    cx, dy = 200, 78
    hw, hh = 92, 42
    by = 172
    p.arrow((cx, 10), (cx, dy - hh), TEXT, LW, head=HEAD)
    diamond(p, cx, dy, hw, hh, THEORY)
    p.label(cx, dy, "koşul", 0, -3, THEORY, 12.5, "middle", True)
    p.label(cx, dy, "doğru mu?", 0, 13, THEORY, 11.5, "middle")
    # True: down into the body, then back up to the test
    p.arrow((cx, dy + hh), (cx, by - 18), TEXT, LW, head=HEAD)
    p.label(cx, (dy + hh + by - 18) / 2, "Evet", 7, 4, TEXT, 11.5, "start")
    box(p, cx, by, 170, 36, BASE)
    p.label(cx, by, "döngü bloğu", 0, 4.5, BASE, 12.5, "middle", True)
    lx = cx - hw - 34
    p.line([(cx, by + 18), (cx, by + 40), (lx, by + 40), (lx, dy)], TEXT, LW)
    p.arrow((lx, dy), (cx - hw, dy), TEXT, LW, head=HEAD)
    p.label(lx, by + 40, "yeniden denetle", 6, 16, TEXT, 11, "start")
    # False: to the right, out of the loop
    ex = 455
    p.arrow((cx + hw, dy), (ex - 80, dy), TEXT, LW, head=HEAD)
    p.label((cx + hw + ex - 80) / 2, dy, "Hayır", 0, -7, TEXT, 11.5, "middle")
    box(p, ex, dy, 160, 46, TEXT, 0.06)
    p.label(ex, dy, "döngüden sonraki", 0, -3, TEXT, 12, "middle")
    p.label(ex, dy, "ilk satır", 0, 13, TEXT, 12, "middle")
    cap = ("Bir <code>while</code> döngüsünün akışı. Koşul her yinelemeden önce yeniden denetlenir; "
           "doğru olduğu sürece blok çalışır ve akış koşula geri döner. Koşul yanlış çıktığında "
           "döngüden çıkılır.")
    aria = ("Flow chart: the condition is tested; if true the loop body runs and the flow returns to "
            "the test; if false the program continues after the loop")
    save("while-akisi", figure(W, H, [p], cap, WIDE, aria))


if __name__ == "__main__":
    fig_algorithm()
    fig_if_else()
    fig_elif()
    fig_indices()
    fig_while()
