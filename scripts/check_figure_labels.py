"""Find figure labels that overlap each other, cover a point marker or leave the canvas.

The lecture-note figures are hand-placed SVG (scripts/svg_plot.py, svg_plot3.py),
so a label nudged a few pixels too far lands on its neighbour and nothing
complains. This script estimates the box of every <text> element from its
position, font size, anchor and length, and reports:

  * two labels whose boxes overlap,
  * a label that covers a point marker (<circle> with r <= 6),
  * a label that sticks out of the viewBox,
  * a label smaller than --min-size (default 10 px, tick labels excepted).

The width estimate is approximate (0.56 em per character), so treat a report
as "look at this one", then confirm on the rendered PNG.

Usage:
    python scripts/check_figure_labels.py "scripts/_figures/analytic-*.md"
    python scripts/check_figure_labels.py dersler/analitik-geometri/*.qmd
Exit code 1 when anything is reported.
"""
import glob
import html
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SVG = re.compile(r"<svg\b[^>]*viewBox=\"([-\d.]+) ([-\d.]+) ([\d.]+) ([\d.]+)\"[^>]*>(.*?)</svg>", re.S)
ARIA = re.compile(r'aria-label="([^"]*)"')
GROUP = re.compile(r"<g\b([^>]*)>|</g>")
TEXT = re.compile(r"<text\b([^>]*)>(.*?)</text>", re.S)
CIRCLE = re.compile(r"<circle\b([^>]*)/?>")
ATTR = re.compile(r'([\w-]+)="([^"]*)"')
TSPAN = re.compile(r"<tspan\b([^>]*)>(.*?)</tspan>", re.S)
TAG = re.compile(r"<[^>]+>")

CHAR_W = 0.56      # average advance width in em
ASCENT, DESCENT = 0.78, 0.22


def attrs(s):
    return dict(ATTR.findall(s))


def text_width(body, size):
    """Estimated advance width of a <text> body, tspans at their own size."""
    width, rest = 0.0, body
    for m in TSPAN.finditer(body):
        a = attrs(m.group(1))
        inner = html.unescape(TAG.sub("", m.group(2))).replace("​", "")
        width += len(inner) * CHAR_W * float(a.get("font-size", size))
    rest = TSPAN.sub("", body)
    width += len(html.unescape(TAG.sub("", rest)).replace("​", "")) * CHAR_W * size
    return width


def labels_of(svg_body):
    """(box, text, size) for every <text>, font size inherited from enclosing <g>."""
    out = []
    stack = [11.5]
    pos = 0
    tokens = sorted([(m.start(), "g", m) for m in GROUP.finditer(svg_body)] +
                    [(m.start(), "t", m) for m in TEXT.finditer(svg_body)], key=lambda t: t[0])
    for _, kind, m in tokens:
        if kind == "g":
            if m.group(0).startswith("</"):
                if len(stack) > 1:
                    stack.pop()
            else:
                a = attrs(m.group(1) or "")
                stack.append(float(a.get("font-size", stack[-1])))
            continue
        a = attrs(m.group(1))
        size = float(a.get("font-size", stack[-1]))
        x, y = float(a.get("x", 0)), float(a.get("y", 0))
        w = text_width(m.group(2), size)
        anchor = a.get("text-anchor", "start")
        x0 = x - w / 2 if anchor == "middle" else x - w if anchor == "end" else x
        box = (x0, y - ASCENT * size, x0 + w, y + DESCENT * size)
        shown = html.unescape(TAG.sub("", m.group(2))).replace("​", "").strip()
        if shown:
            out.append((box, shown, size))
    return out


def markers_of(svg_body):
    out = []
    for m in CIRCLE.finditer(svg_body):
        a = attrs(m.group(1))
        r = float(a.get("r", 0))
        if 0 < r <= 6:
            cx, cy = float(a.get("cx", 0)), float(a.get("cy", 0))
            out.append((cx - r, cy - r, cx + r, cy + r))
    return out


def overlap(a, b):
    w = min(a[2], b[2]) - max(a[0], b[0])
    h = min(a[3], b[3]) - max(a[1], b[1])
    return max(w, 0) * max(h, 0)


def area(b):
    return max(b[2] - b[0], 0) * max(b[3] - b[1], 0)


def check_svg(X0, Y0, W, H, body, min_size):
    problems = []
    labels = labels_of(body)
    for i in range(len(labels)):
        bi, ti, si = labels[i]
        if si < min_size:
            problems.append(f"too small ({si:g}px): '{ti}'")
        if bi[0] < X0 - 2 or bi[1] < Y0 - 2 or bi[2] > X0 + W + 2 or bi[3] > Y0 + H + 2:
            problems.append(f"outside the canvas: '{ti}'")
        for j in range(i + 1, len(labels)):
            bj, tj, _ = labels[j]
            ov = overlap(bi, bj)
            if ov > 0.12 * min(area(bi), area(bj)):
                problems.append(f"labels overlap: '{ti}' / '{tj}'")
        for mk in markers_of(body):
            if overlap(bi, mk) > 0.35 * area(mk):
                problems.append(f"label covers a point: '{ti}'")
                break
    return problems


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    min_size = 10.0
    for a in sys.argv[1:]:
        if a.startswith("--min-size="):
            min_size = float(a.split("=", 1)[1])
    files = sorted({f for pattern in args for f in glob.glob(pattern)})
    if not files:
        sys.exit("no files matched")
    bad = figures = 0
    for f in files:
        text = open(f, encoding="utf-8").read()
        for m in SVG.finditer(text):
            figures += 1
            X0, Y0, W, H = (float(m.group(k)) for k in range(1, 5))
            body = m.group(5)
            aria = ARIA.search(text[max(0, m.start() - 10):m.end()])
            name = aria.group(1)[:60] if aria else "?"
            for p in check_svg(X0, Y0, W, H, body, min_size):
                bad += 1
                print(f"{f}: [{name}] {p}")
    print(f"figures: {figures}, problems: {bad}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
