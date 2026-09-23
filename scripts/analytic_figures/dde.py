# -*- coding: utf-8 -*-
"""
Figures of the chapter "Düzlemde Doğru Denklemleri"
(dersler/analitik-geometri/duzlemde-dogru-denklemleri.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box: a figure that illustrates a
definition sits directly below that box. The figures are NOT produced at
build time. Run

    python scripts/analytic_figures/dde.py
    python scripts/center_figures.py "analytic-dde-*.md" --keep-width
    python scripts/check_figure_labels.py "scripts/_figures/analytic-dde-*.md"

and paste the markup of scripts/_figures/analytic-dde-<name>.md into the .qmd.

Every figure is drawn through the small Fig wrapper below. It keeps the pixel
geometry of all lines and labels, drops axis numbers that would collide with
something, and prints a warning when a label touches a line, a point or
another label (check_figure_labels.py cannot see lines).

The captions are Turkish on purpose (they are shown on the site); the aria
labels are plain ASCII.
"""
import html
import io
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, WIDE, TEXT, THEORY, PRACTICE, BASE, BG  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "analytic-dde-"
OUT = {}

MINUS, OMEGA, PI_, SQRT = "&#8722;", "&#969;", "&#960;", "&#8730;"
ELL, APPROX, DEG = "&#8467;", "&#8776;", "&#176;"

NAME = 14      # point and object names
EQ = 13        # equations and measures
FR = 11.5      # digits of a small fraction
SUB = 11       # subscripts
TICK = 11      # axis numbers
GRAY_OP = 0.55


# ---------------------------------------------------------------------------
# inline markup
# ---------------------------------------------------------------------------
def I(s):
    """Italic run (a variable)."""
    return f'<tspan font-style="italic">{s}</tspan>'


def sub(s):
    return f'<tspan font-size="{SUB}" dy="4">{s}</tspan><tspan dy="-4">&#8203;</tspan>'


def m(s):
    """Minus sign for numbers written in labels: m('3') -> '−3'."""
    return MINUS + s


class Frac:
    def __init__(self, num, den, size=None):
        self.num, self.den, self.size = num, den, size


class Bar:
    """A letter with one or two overlines (d-bar, d-double-bar)."""

    def __init__(self, s, n=1):
        self.s, self.n = s, n


class Paren:
    """A tall parenthesis drawn as a path, sized to the fractions of the label."""

    def __init__(self, ch):
        self.ch = ch


# rough advance widths (em) of a serif face; only used for layout
_W = {" ": 0.25, "=": 0.6, "+": 0.6, "−": 0.6, "(": 0.36, ")": 0.36, ",": 0.26, ".": 0.26,
      ":": 0.28, "/": 0.38, "√": 0.6, "π": 0.56, "ω": 0.66, "ℓ": 0.42,
      "≈": 0.6, "°": 0.4, "f": 0.32, "i": 0.29, "j": 0.28, "l": 0.28, "m": 0.82,
      "r": 0.41, "s": 0.43, "t": 0.33, "w": 0.74, "c": 0.45, "e": 0.48, "z": 0.45}
TSPAN = re.compile(r"<tspan\b([^>]*)>(.*?)</tspan>", re.S)
TAG = re.compile(r"<[^>]+>")


def _chars_w(s):
    w = 0.0
    for ch in s:
        if ch == "​":
            continue
        if ch in _W:
            w += _W[ch]
        elif ch.isdigit():
            w += 0.55
        elif ch.isupper():
            w += 0.68
        elif ch.isalpha():
            w += 0.52
        else:
            w += 0.56
    return w


def est(markup, size):
    """Estimated advance width in px of an inline markup string."""
    w = 0.0
    for mt in TSPAN.finditer(markup):
        fs = re.search(r'font-size="([\d.]+)"', mt.group(1))
        w += _chars_w(html.unescape(TAG.sub("", mt.group(2)))) * (float(fs.group(1)) if fs else size)
    rest = TSPAN.sub("", markup)
    return w + _chars_w(html.unescape(TAG.sub("", rest))) * size


def nchars(markup):
    return len(html.unescape(TAG.sub("", markup)).replace("​", ""))


def has_sub(markup):
    return 'dy="4"' in markup


# ---------------------------------------------------------------------------
# geometry helpers (pixel space)
# ---------------------------------------------------------------------------
def seg_hits_box(a, b, box):
    """Liang-Barsky: does the segment ab meet the rectangle box?"""
    x0, y0, x1, y1 = box
    dx, dy = b[0] - a[0], b[1] - a[1]
    t0, t1 = 0.0, 1.0
    for p, q in ((-dx, a[0] - x0), (dx, x1 - a[0]), (-dy, a[1] - y0), (dy, y1 - a[1])):
        if p == 0:
            if q < 0:
                return False
        else:
            r = q / p
            if p < 0:
                if r > t1:
                    return False
                t0 = max(t0, r)
            else:
                if r < t0:
                    return False
                t1 = min(t1, r)
    return True


def boxes_meet(a, b, pad=0.0):
    return not (a[2] + pad <= b[0] or b[2] + pad <= a[0] or a[3] + pad <= b[1] or b[3] + pad <= a[1])


def grow(b, d):
    return (b[0] - d, b[1] - d, b[2] + d, b[3] + d)


def unit(v):
    n = math.hypot(v[0], v[1])
    return (v[0] / n, v[1] / n)


def fmt_num(v):
    s = str(int(v)) if float(v).is_integer() else f"{v:g}"
    return s.replace("-", MINUS)


# ---------------------------------------------------------------------------
# the figure wrapper
# ---------------------------------------------------------------------------
class Fig:
    def __init__(self, name, xr, yr, ppu, pad=(80, 56, 80, 56)):
        l, t, r, b = pad
        self.name = name
        self.xr, self.yr, self.ppu = xr, yr, ppu
        w, h = (xr[1] - xr[0]) * ppu, (yr[1] - yr[0]) * ppu
        self.p = Plot(l, t, w, h, xr, yr)
        self.W, self.H = max(560, round(l + w + r)), round(t + h + b)
        self.segs = []     # (a, b, kind)
        self.boxes = []    # (box, text, kind)
        self.marks = []    # (px, py, r)
        self.nums = []     # pending axis numbers

    # -- mapping -------------------------------------------------------------
    def X(self, x):
        return self.p.X(x)

    def Y(self, y):
        return self.p.Y(y)

    def px(self, P):
        return (self.X(P[0]), self.Y(P[1]))

    def _rec(self, pts, kind="obj"):
        for a, b in zip(pts, pts[1:]):
            self.segs.append((a, b, kind))

    # -- marks ---------------------------------------------------------------
    def line(self, pts, color=THEORY, width=2.0, dash=None, opacity=1.0, kind="obj"):
        self.p.line(pts, color, width, dash, opacity)
        self._rec([self.px(P) for P in pts], kind)

    def fline(self, f, x0, x1, **kw):
        self.line([(x0, f(x0)), (x1, f(x1))], **kw)

    def thick(self, a, b, color=PRACTICE, width=3.4, opacity=1.0):
        self.line([a, b], color, width, None, opacity)

    def guide(self, pts, dash="5 4", opacity=GRAY_OP, width=1.3, color=TEXT):
        self.line(pts, color, width, dash, opacity)

    def arrow(self, a, b, color=PRACTICE, width=2.2, head=9.0, opacity=1.0):
        self.p.arrow(a, b, color, width, head, None, opacity)
        self._rec([self.px(a), self.px(b)])

    def dim(self, a, b, color=TEXT, width=1.1, head=7.0, opacity=0.8):
        """Dimension line: a segment with an arrowhead at both ends."""
        mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
        self.p.arrow(mid, a, color, width, head, None, opacity)
        self.p.arrow(mid, b, color, width, head, None, opacity)
        self._rec([self.px(a), self.px(b)])

    def circle(self, c, r, color=TEXT, width=1.4, dash=None, opacity=1.0):
        self.p.circle(c[0], c[1], r, color, width, dash, "none", opacity)
        pts = [(c[0] + r * math.cos(2 * math.pi * k / 120), c[1] + r * math.sin(2 * math.pi * k / 120))
               for k in range(121)]
        self._rec([self.px(P) for P in pts])

    def arc(self, c, r, a0, a1, color=TEXT, width=1.4, head=True, opacity=0.85):
        """Angle arc from a0 to a1 (degrees, counter-clockwise), arrowhead at a1."""
        n = max(12, int(abs(a1 - a0) / 3))
        pts = [(c[0] + r * math.cos(math.radians(a0 + (a1 - a0) * k / n)),
                c[1] + r * math.sin(math.radians(a0 + (a1 - a0) * k / n))) for k in range(n + 1)]
        if head:
            # keep the head inside the arc: aim it along the chord of the last few samples
            k = max(2, n // 10)
            self.p.line(pts[:-k + 1], color, width, None, opacity)
            self.p.arrow(pts[-k], pts[-1], color, width, 7.0, None, opacity)
        else:
            self.p.line(pts, color, width, None, opacity)
        self._rec([self.px(P) for P in pts])

    def polygon(self, pts, fill=THEORY, opacity=0.12, stroke="none", width=1.6):
        self.p.polygon(pts, fill, opacity, stroke, width)
        if stroke != "none":
            self._rec([self.px(P) for P in list(pts) + [pts[0]]])

    def point(self, P, color=TEXT, r=4.2):
        self.p.points([P], color, r)
        self.marks.append((self.X(P[0]), self.Y(P[1]), r))

    def hollow(self, P, color=TEXT, r=4.0):
        x, y = self.px(P)
        self.p.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{BG}" stroke="{color}" stroke-width="1.6"/>')
        self.marks.append((x, y, r))

    def right_angle(self, V, u, v, size=10.0, color=TEXT, opacity=0.75):
        """Right-angle mark at V between the data directions u and v."""
        x, y = self.px(V)
        a = unit((u[0], -u[1]))
        b = unit((v[0], -v[1]))
        p1 = (x + size * a[0], y + size * a[1])
        p2 = (p1[0] + size * b[0], p1[1] + size * b[1])
        p3 = (x + size * b[0], y + size * b[1])
        self.p.add(f'<path d="M{p1[0]:.1f},{p1[1]:.1f} L{p2[0]:.1f},{p2[1]:.1f} L{p3[0]:.1f},{p3[1]:.1f}" '
                   f'fill="none" stroke="{color}" stroke-width="1.1" opacity="{opacity}"/>')
        self._rec([p1, p2, p3], "ra")

    def eq_tick(self, M, d, length=12.0, color=TEXT, width=1.5, opacity=0.9):
        """Short stroke across a segment of direction d at M (equal-length mark)."""
        x, y = self.px(M)
        n = unit((d[1], d[0]))   # pixel normal of the data direction (dx, dy) -> (dy, dx)
        h = length / 2
        a, b = (x - n[0] * h, y - n[1] * h), (x + n[0] * h, y + n[1] * h)
        self.p.add(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" '
                   f'stroke="{color}" stroke-width="{width}" opacity="{opacity}"/>')
        self._rec([a, b], "ra")

    def chevron(self, P, d, color=THEORY, size=7.0, width=1.8):
        """A '>' mark on a line at P pointing along the data direction d."""
        x, y = self.px(P)
        u = unit((d[0], -d[1]))
        n = (-u[1], u[0])
        tip = (x + u[0] * size * 0.6, y + u[1] * size * 0.6)
        a = (tip[0] - u[0] * size + n[0] * size * 0.7, tip[1] - u[1] * size + n[1] * size * 0.7)
        b = (tip[0] - u[0] * size - n[0] * size * 0.7, tip[1] - u[1] * size - n[1] * size * 0.7)
        self.p.add(f'<path d="M{a[0]:.1f},{a[1]:.1f} L{tip[0]:.1f},{tip[1]:.1f} L{b[0]:.1f},{b[1]:.1f}" '
                   f'fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round" '
                   f'stroke-linejoin="round"/>')
        self._rec([a, tip, b], "ra")

    # -- axes ----------------------------------------------------------------
    def axes(self, nums=True, xnums=None, ynums=None, xticks=None, yticks=None,
             skip_x=(), skip_y=(), labels=("X", "Y"), opacity=0.6):
        """Arrowed axes through the origin; integer ticks, numbers placed at finish()."""
        (x0, x1), (y0, y1) = self.xr, self.yr
        ox, oy = self.X(0), self.Y(0)
        L, R = self.X(x0), self.X(x1) + 16
        B, T = self.Y(y0), self.Y(y1) - 16
        a = [f'<g stroke="{TEXT}" stroke-width="1.15" opacity="{opacity}" fill="{TEXT}">',
             f'<line x1="{L:.1f}" y1="{oy:.1f}" x2="{R - 6:.1f}" y2="{oy:.1f}"/>',
             f'<line x1="{ox:.1f}" y1="{B:.1f}" x2="{ox:.1f}" y2="{T + 6:.1f}"/>',
             f'<polygon points="{R:.1f},{oy:.1f} {R - 9:.1f},{oy - 3.8:.1f} {R - 9:.1f},{oy + 3.8:.1f}" stroke="none"/>',
             f'<polygon points="{ox:.1f},{T:.1f} {ox - 3.8:.1f},{T + 9:.1f} {ox + 3.8:.1f},{T + 9:.1f}" stroke="none"/>']
        self.segs.append(((L, oy), (R, oy), "axis"))
        self.segs.append(((ox, B), (ox, T), "axis"))
        if xticks is None:
            xticks = [t for t in range(math.ceil(x0), math.floor(x1) + 1) if t != 0]
        if yticks is None:
            yticks = [t for t in range(math.ceil(y0), math.floor(y1) + 1) if t != 0]
        if nums:
            for t in xticks:
                X = self.X(t)
                a.append(f'<line x1="{X:.1f}" y1="{oy - 3.5:.1f}" x2="{X:.1f}" y2="{oy + 3.5:.1f}"/>')
            for t in yticks:
                Y = self.Y(t)
                a.append(f'<line x1="{ox - 3.5:.1f}" y1="{Y:.1f}" x2="{ox + 3.5:.1f}" y2="{Y:.1f}"/>')
        a.append('</g>')
        self.p.add("\n  ".join(a))
        if labels:
            self.label_at(R + 6, oy + 5, [I(labels[0])], "start", NAME - 0.5, TEXT, kind="axislabel")
            self.label_at(ox, T - 7, [I(labels[1])], "middle", NAME - 0.5, TEXT, kind="axislabel")
        if nums:
            xn = xticks if xnums is None else xnums
            yn = yticks if ynums is None else ynums
            for t in xn:
                if t not in skip_x:
                    self.nums.append(("x", t))
            for t in yn:
                if t not in skip_y:
                    self.nums.append(("y", t))

    # -- labels --------------------------------------------------------------
    def layout(self, parts, size):
        items = []
        for k, part in enumerate(parts):
            if isinstance(part, Frac):
                f = part.size or FR
                wn, wd = est(part.num, f), est(part.den, f)
                items.append(["f", max(wn, wd) + 9.0, part, f, wn, wd])
            elif isinstance(part, Bar):
                items.append(["b", max(est(I(part.s), size), 0.56 * size * len(part.s)), part])
            elif isinstance(part, Paren):
                items.append(["p", 0.42 * size, part])
            else:
                items.append(["t", est(part, size), part])
        for k, it in enumerate(items):
            if it[0] != "t":
                continue
            prev_f = k > 0 and items[k - 1][0] == "f"
            next_f = k + 1 < len(items) and items[k + 1][0] == "f"
            if prev_f and next_f:     # the checker measures 0.56 em per character: leave it room
                it[1] = max(it[1], 0.56 * size * nchars(it[2]))
        fr = [it for it in items if it[0] == "f"]
        subs = any(has_sub(it[2]) for it in items if it[0] == "t")
        if fr:
            f = max(it[3] for it in fr)
            ns = any(has_sub(it[2].num) for it in fr)
            ds = any(has_sub(it[2].den) for it in fr)
            asc = 0.30 * size + 2.6 + (4 if ns else 0) + 0.74 * f
            desc = -0.30 * size + 2.6 + 0.72 * f + 0.8 + (3 if ds else 0)
            asc = max(asc, 0.74 * size)
            desc = max(desc, 0.22 * size + (3 if subs else 0))
        else:
            asc, desc = 0.74 * size, 0.22 * size + (3.5 if subs else 0)
        return items, sum(it[1] for it in items), asc, desc

    def label_at(self, x, y, parts, anchor="start", size=EQ, color=TEXT, kind="label", bold=False, flip=False):
        """Composite label with its baseline at pixel (x, y).

        flip=True keeps a start-anchored position but writes the text anchored at
        its far end, so that a width estimate larger than the real text (the one
        of check_figure_labels.py) grows back into the figure, not out of it.
        """
        items, W, asc, desc = self.layout(parts, size)
        cur = x - (W / 2 if anchor == "middle" else W if anchor == "end" else 0)
        single = len(items) == 1 and items[0][0] == "t"
        bold_a = ' font-weight="600"' if bold else ""
        out = []
        n_items = len(items)
        for k, it in enumerate(items):
            kind_i, w = it[0], it[1]
            if kind_i == "t":
                prev_f = k > 0 and items[k - 1][0] == "f"
                next_f = k + 1 < n_items and items[k + 1][0] == "f"
                if single:
                    if flip:
                        tx, ta = (cur, "start") if anchor == "end" else (cur + w, "end")
                    else:
                        tx, ta = x, anchor
                elif next_f and not prev_f:
                    tx, ta = cur + w, "end"
                elif prev_f and next_f:
                    tx, ta = cur + w / 2, "middle"
                else:
                    tx, ta = cur, "start"
                out.append(f'<text x="{tx:.1f}" y="{y:.1f}" fill="{color}" font-size="{size}" '
                           f'text-anchor="{ta}"{bold_a}>{it[2]}</text>')
            elif kind_i == "b":
                part = it[2]
                out.append(f'<text x="{cur:.1f}" y="{y:.1f}" fill="{color}" font-size="{size}"{bold_a}>'
                           f'{I(part.s)}</text>')
                wl = est(I(part.s), size)
                for j in range(part.n):
                    yb = y - 0.80 * size - 1.6 - 2.8 * j
                    out.append(f'<line x1="{cur + 1.4:.1f}" y1="{yb:.1f}" x2="{cur + wl + 1.0:.1f}" y2="{yb:.1f}" '
                               f'stroke="{color}" stroke-width="1.1"/>')
            elif kind_i == "p":
                top, bot = y - asc + 1.0, y + desc - 1.0
                bulge = 3.2 if it[2].ch == "(" else -3.2
                x0 = cur + (w * 0.72 if it[2].ch == "(" else w * 0.28)
                out.append(f'<path d="M{x0:.1f},{top:.1f} Q{x0 - bulge * 1.9:.1f},{(top + bot) / 2:.1f} '
                           f'{x0:.1f},{bot:.1f}" fill="none" stroke="{color}" stroke-width="1.15" '
                           f'stroke-linecap="round"/>')
            else:
                part, f, wn, wd = it[2], it[3], it[4], it[5]
                cx = cur + w / 2
                bar = y - 0.30 * size
                nb = bar - 2.6 - (4 if has_sub(part.num) else 0)
                db = bar + 2.6 + 0.72 * f
                half = max(wn, wd) / 2 + 1.2
                out.append(f'<text x="{cx:.1f}" y="{nb:.1f}" fill="{color}" font-size="{f}" '
                           f'text-anchor="middle"{bold_a}>{part.num}</text>')
                out.append(f'<line x1="{cx - half:.1f}" y1="{bar:.1f}" x2="{cx + half:.1f}" y2="{bar:.1f}" '
                           f'stroke="{color}" stroke-width="1.0"/>')
                out.append(f'<text x="{cx:.1f}" y="{db:.1f}" fill="{color}" font-size="{f}" '
                           f'text-anchor="middle"{bold_a}>{part.den}</text>')
            cur += w
        self.p.add("\n  ".join(out))
        x0 = x - (W / 2 if anchor == "middle" else W if anchor == "end" else 0)
        box = (x0, y - asc, x0 + W, y + desc)
        text = html.unescape(TAG.sub("", "".join(it[2] if it[0] == "t" else "#" for it in items)))
        self.boxes.append((box, text, kind))
        return box

    def label(self, P, parts, pos="ne", gap=7.0, dx=0.0, dy=0.0, size=EQ, color=TEXT, bold=False):
        """Place a label on the `pos` side of the data point P, `gap` px away."""
        items, W, asc, desc = self.layout(parts, size)
        x, y = self.px(P)
        g = gap
        d = g * 0.72 + 3.0
        if pos == "e":
            bx, by = x + g, y - (asc + desc) / 2
        elif pos == "w":
            bx, by = x - g - W, y - (asc + desc) / 2
        elif pos == "n":
            bx, by = x - W / 2, y - g - asc - desc
        elif pos == "s":
            bx, by = x - W / 2, y + g
        elif pos == "ne":
            bx, by = x + d, y - d - asc - desc
        elif pos == "nw":
            bx, by = x - d - W, y - d - asc - desc
        elif pos == "se":
            bx, by = x + d, y + d
        elif pos == "sw":
            bx, by = x - d - W, y + d
        else:
            raise ValueError(pos)
        if pos in ("w", "nw", "sw"):
            return self.label_at(bx + W + dx, by + asc + dy, parts, "end", size, color, bold=bold)
        if pos in ("n", "s"):
            return self.label_at(bx + W / 2 + dx, by + asc + dy, parts, "middle", size, color, bold=bold)
        return self.label_at(bx + dx, by + asc + dy, parts, "start", size, color, bold=bold)

    # -- output --------------------------------------------------------------
    def _free(self, box, pad=2.5):
        b = grow(box, pad)
        for a, c, kind in self.segs:
            if kind != "axis" and seg_hits_box(a, c, b):
                return False
        for bb, _, _ in self.boxes:
            if boxes_meet(b, bb):
                return False
        for x, y, r in self.marks:
            if boxes_meet(b, (x - r, y - r, x + r, y + r)):
                return False
        return True

    def finish(self, caption, aria, css="ders-grafik", allow=()):
        ox, oy = self.X(0), self.Y(0)
        a = [f'<g fill="{TEXT}" font-size="{TICK}" opacity="0.75">']
        for axis, t in self.nums:
            s = fmt_num(t)
            w = est(s, TICK)
            if axis == "x":
                X = self.X(t)
                spots = [(X, oy + 16, "middle", (X - w / 2, oy + 16 - 0.74 * TICK, X + w / 2, oy + 16 + 0.22 * TICK)),
                         (X, oy - 7, "middle", (X - w / 2, oy - 7 - 0.74 * TICK, X + w / 2, oy - 7 + 0.22 * TICK))]
            else:
                Y = self.Y(t) + 4
                spots = [(ox - 7, Y, "end", (ox - 7 - w, Y - 0.74 * TICK, ox - 7, Y + 0.22 * TICK)),
                         (ox + 7, Y, "start", (ox + 7, Y - 0.74 * TICK, ox + 7 + w, Y + 0.22 * TICK))]
            for k, (X, Y, anchor, box) in enumerate(spots):
                if self._free(box):
                    a.append(f'<text x="{X:.1f}" y="{Y:.1f}" text-anchor="{anchor}">{s}</text>')
                    self.boxes.append((box, s, "num"))
                    if k:
                        print(f"  [{self.name}] axis number {axis}={s} moved to the other side")
                    break
            else:
                print(f"  [{self.name}] axis number {axis}={s} dropped")
        a.append("</g>")
        self.p.add("\n  ".join(a))
        self.report(allow)
        OUT[self.name] = figure(self.W, self.H, [self.p], caption, css, aria)

    def report(self, allow=()):
        labels = [(b, t) for b, t, k in self.boxes if k in ("label", "axislabel")]
        for b, t in labels:
            if t in allow:
                continue
            g = grow(b, 1.5)
            for a, c, kind in self.segs:
                if seg_hits_box(a, c, g):
                    print(f"  !! [{self.name}] label '{t}' touches a {kind} line "
                          f"({a[0]:.0f},{a[1]:.0f})-({c[0]:.0f},{c[1]:.0f})")
                    break
            for x, y, r in self.marks:
                if boxes_meet(g, (x - r, y - r, x + r, y + r)):
                    print(f"  !! [{self.name}] label '{t}' covers a point")
        for i in range(len(self.boxes)):
            for j in range(i + 1, len(self.boxes)):
                if boxes_meet(self.boxes[i][0], self.boxes[j][0], 1.0):
                    print(f"  !! [{self.name}] labels meet: '{self.boxes[i][1]}' / '{self.boxes[j][1]}'")


# common label pieces
def Pn(name, idx=None, coords=None):
    s = I(name) + (sub(idx) if idx is not None else "")
    return s + (f"({coords})" if coords is not None else "")


PXY = I("P") + "(" + I("x") + sub("0") + ", " + I("y") + sub("0") + ")"
X0 = I("x") + sub("0")
Y0 = I("y") + sub("0")
SQ3 = SQRT + "3"
R3 = math.sqrt(3.0)
S2 = math.sqrt(2.0)


def eqn(s):
    """Equation text: letters x, y, d become italic; '-' becomes a minus sign."""
    out = []
    for ch in s:
        if ch in "xyd":
            out.append(I(ch))
        elif ch == "-":
            out.append(MINUS)
        else:
            out.append(ch)
    return "".join(out)


# ============================================================ dde-nokta-egim
F = Fig("nokta-egim", (-1, 7), (-1, 5), 66)
F.axes(nums=False)
F.guide([(1, 1), (5, 1), (5, 3)])
F.right_angle((5, 1), (-1, 0), (0, 1))
F.line([(-1, 0), (7, 4)], THEORY, 2.3)
F.point((1, 1))
F.point((5, 3))
F.label((6.6, 3.8), [I("d")], "n", 10, size=NAME + 1, color=THEORY)
F.label((1, 1), [PXY], "s", 21, dx=-4, size=NAME)
F.label((5, 3), [I("Q") + "(" + I("x") + ", " + I("y") + ")"], "nw", 8, size=NAME)
F.label((3, 1), [I("x") + " " + MINUS + " " + X0], "s", 7)
F.label((5, 2), [I("y") + " " + MINUS + " " + Y0], "e", 8)
F.label_at(F.X(0) + 24, F.Y(4.25), [I("m") + " =", Frac(I("y") + " " + MINUS + " " + Y0,
                                                      I("x") + " " + MINUS + " " + X0, EQ)],
           "start", NAME)
F.finish(
    "Nokta-eğim denklemi: <em>d</em> doğrusu üzerindeki her <em>Q</em>(<em>x</em>, <em>y</em>) noktası için "
    "<em>P</em>'den <em>Q</em>'ya giden parçanın eğimi aynı <em>m</em> sayısıdır. Kesikli dik üçgenin "
    "kenarları <em>x</em> &#8722; <em>x</em><sub>0</sub> ve <em>y</em> &#8722; <em>y</em><sub>0</sub>'dır.",
    "Line d through P(x0, y0) and Q(x, y) with the slope triangle x - x0, y - y0 and the slope formula")

# ============================================================ dde-ozel-dogrular
F = Fig("ozel-dogrular", (-4, 6), (-3, 5), 50)
F.axes()
F.line([(-4, 0), (6, 5)], THEORY, 2.2)
F.line([(-4, -1), (6, -1)], PRACTICE, 2.2)
F.line([(3, -3), (3, 5)], BASE, 2.2)
F.point((0, 2))
F.label_at(F.X(6), F.Y(5) - 15, [I("y") + " =", Frac("1", "2"), I("x") + " + 2"], "end", EQ, THEORY)
F.label((0, 2), ["(0, 2)"], "nw", 8)
F.label_at(F.X(-4) + 2, F.Y(-1) + 18, [I("y") + " = " + m("1")], "start", EQ, PRACTICE)
F.label_at(F.X(3) + 8, F.Y(5) + 5, [I("x") + " = 3"], "start", EQ, BASE)
F.finish(
    "Üç tür doğru: eğimi 1/2 olup <em>Y</em>-eksenini (0, 2)'de kesen <em>y</em> = <em>x</em>/2 + 2 "
    "doğrusu, yatay <em>y</em> = &#8722;1 doğrusu ve düşey <em>x</em> = 3 doğrusu.",
    "Three lines: y = x/2 + 2 through (0, 2), the horizontal line y = -1 and the vertical line x = 3")

# ============================================================ dde-iki-nokta-ornek
F = Fig("iki-nokta-ornek", (-3, 4), (-3, 5), 58)
F.axes(skip_x=(1,), skip_y=(2,))
F.guide([(-1, 3), (2, 3), (2, -1)])
F.line([(-2.5, 5), (3.5, -3)], THEORY, 2.2)
F.hollow((1.25, 0), THEORY)
F.hollow((0, 5 / 3), THEORY)
F.point((2, -1))
F.point((-1, 3))
F.label_at(F.X(3.5) + 10, F.Y(-3) + 5, [I("y") + " = " + MINUS, Frac("4", "3"), I("x") + " +", Frac("5", "3")],
           "start", EQ, THEORY)
F.label((2, -1), [Pn("P", "1", "2, " + m("1"))], "e", 10, dy=1, size=NAME)
F.label((-1, 3), [Pn("P", "2", m("1") + ", 3")], "w", 10, dy=8, size=NAME)
F.label((0.5, 3), ["3"], "n", 5)
F.label((2, 1), [m("4")], "e", 7)
F.label((1.25, 0), [Frac("5", "4", 12)], "s", 6, dx=-7, color=THEORY)
F.label((0, 5 / 3), [Frac("5", "3", 12)], "w", 8, dy=11, color=THEORY)
F.finish(
    "<em>P</em><sub>1</sub>(2, &#8722;1) ve <em>P</em><sub>2</sub>(&#8722;1, 3)'ten geçen doğru. Eğim üçgeninde "
    "<em>x</em> 3 artarken <em>y</em> 4 azalır; doğru eksenleri (5/4, 0) ve (0, 5/3) noktalarında keser.",
    "Line through P1(2, -1) and P2(-1, 3) with slope triangle 3 and -4 and axis intercepts 5/4 and 5/3")

# ============================================================ dde-eksen-kesen
F = Fig("eksen-kesen", (-2, 6), (-5, 2), 60)
F.polygon([(0, 0), (4, 0), (0, -3)], THEORY, 0.13)
F.axes(skip_y=(-3,))
F.line([(-1, -3.75), (6, 1.5)], THEORY, 2.2)
F.point((4, 0))
F.point((0, -3))
F.label_at(F.X(6) - 10, F.Y(1.5) - 10, [eqn("3x - 4y - 12 = 0")], "end", EQ, THEORY)
F.label_at(F.X(4) + 3, F.Y(0) - 10, [I("A") + "(4, 0)"], "end", NAME)
F.label((0, -3), [I("B") + "(0, " + m("3") + ")"], "w", 10, dy=-3, size=NAME)
F.label((0, 0), [I("O")], "nw", 5, size=NAME)
F.finish(
    "<em>X</em>-eksenini <em>A</em>(4, 0), <em>Y</em>-eksenini <em>B</em>(0, &#8722;3) noktasında kesen "
    "doğru: <em>x</em>/4 &#8722; <em>y</em>/3 = 1, yani 3<em>x</em> &#8722; 4<em>y</em> &#8722; 12 = 0.",
    "Line 3x - 4y - 12 = 0 meeting the axes at A(4, 0) and B(0, -3), triangle OAB shaded")

# ============================================================ dde-orta-dikme
F = Fig("orta-dikme", (-3, 9), (-4, 7), 44)
F.axes(skip_x=(4,))
F.line([(7, 4), (-1, -2)], TEXT, 2.0, opacity=0.8)
F.eq_tick((5, 2.5), (4, 3))
F.eq_tick((1, -0.5), (4, 3))
F.line([(-1, 19 / 3), (6, -3)], THEORY, 2.2)
F.right_angle((3, 1), (4, 3), (-3, 4))
F.hollow((0, 5), THEORY)
F.hollow((3.75, 0), THEORY)
F.point((7, 4))
F.point((-1, -2))
F.point((3, 1), PRACTICE, 4.6)
F.label((7, 4), [Pn("P", "1", "7, 4")], "e", 10, size=NAME)
F.label((-1, -2), [Pn("P", "2", m("1") + ", " + m("2"))], "w", 10, size=NAME)
F.label_at(F.X(3) + 17, F.Y(1) + 12, [Pn("P", "0", "3, 1")], "start", NAME, PRACTICE)
F.label_at(F.X(0) + 9, F.Y(19 / 3) + 5, [Bar("d"), eqn(": 4x + 3y - 15 = 0")], "start", EQ, THEORY)
F.label((3.75, 0), [Frac("15", "4", 12)], "s", 6, dx=-12, color=THEORY)
F.finish(
    "<em>P</em><sub>1</sub><em>P</em><sub>2</sub> parçasının orta dikmesi: <em>d&#773;</em> doğrusu orta nokta "
    "<em>P</em><sub>0</sub>(3, 1)'den geçer ve parçaya diktir. Eşitlik çentikleri iki yarının eşit olduğunu gösterir.",
    "Segment P1(7, 4) P2(-1, -2) with midpoint P0(3, 1) and the perpendicular bisector 4x + 3y - 15 = 0")

# ============================================================ dde-genel-donusum
F = Fig("genel-donusum", (-4, 3), (-2, 4), 70)
F.axes(skip_x=(-3, -2), skip_y=(2,))
F.guide([(-8 / 3, 0), (0, 0)], width=3.0, opacity=0.5)
F.guide([(0, 0), (0, 2)], width=3.0, opacity=0.5)
F.line([(-4, -1), (2.5, 3.875)], THEORY, 2.2)
F.point((-8 / 3, 0))
F.point((0, 2))
F.label_at(F.X(2.5) - 10, F.Y(3.875) - 10, [eqn("3x - 4y + 8 = 0")], "end", EQ, THEORY)
F.label_at(F.X(-8 / 3) - 3, F.Y(0) + 23, [Paren("("), MINUS, Frac("8", "3"), ", 0", Paren(")")], "start", EQ)
F.label((-4 / 3, 0), [Frac("8", "3", 12)], "s", 7)
F.label((0, 2), ["(0, 2)"], "se", 8)
F.label((0, 1), ["2"], "e", 9)
F.finish(
    "3<em>x</em> &#8722; 4<em>y</em> + 8 = 0 doğrusu eksenleri (&#8722;8/3, 0) ve (0, 2)'de keser; "
    "eğim üçgeninin kenarları 8/3 ve 2 olduğundan eğim 2 : 8/3 = 3/4'tür.",
    "Line 3x - 4y + 8 = 0 with intercepts (-8/3, 0) and (0, 2) and slope triangle 8/3 by 2")

# ============================================================ dde-bes-birim
F = Fig("bes-birim", (-3, 9), (-4, 8), 44)
F.axes()
F.circle((3, 2), 5, TEXT, 1.3, "5 4", 0.4)
F.guide([(3, 2), (7, 2), (7, 5)])
F.line([(-3, -2.5), (9, 6.5)], THEORY, 2.2)
F.point((3, 2))
F.point((-1, -1))
F.point((7, 5))
F.label((8.8, 6.35), [I("d")], "n", 10, size=NAME + 1, color=THEORY)
F.label((3, 2), [Pn("P", "0", "3, 2")], "nw", 8, size=NAME)
F.label_at(F.X(-1) - 18, F.Y(-1) + 2.5, [Pn("P", "1", m("1") + ", " + m("1"))], "end", NAME)
F.label_at(F.X(7) + 22, F.Y(5) + 18, [Pn("P", "2", "7, 5")], "start", NAME)
F.label((1, 0.5), ["5"], "nw", 7, color=THEORY)
F.label((5, 3.5), ["5"], "nw", 7, color=THEORY)
F.label((5, 2), ["4"], "s", 6)
F.label((7, 3.5), ["3"], "e", 8)
F.finish(
    "<em>P</em><sub>0</sub>(3, 2)'den geçen, eğimi 3/4 olan <em>d</em> doğrusu. Merkezi <em>P</em><sub>0</sub>, "
    "yarıçapı 5 olan çember doğruyu aranan <em>P</em><sub>1</sub>(&#8722;1, &#8722;1) ve "
    "<em>P</em><sub>2</sub>(7, 5) noktalarında keser; yatay 4, düşey 3 birimlik adımın uzunluğu 5'tir.",
    "Line of slope 3/4 through P0(3, 2) and the circle of radius 5 about P0 meeting it at P1(-1, -1) and P2(7, 5)")

# ============================================================ dde-normal-denklem
F = Fig("normal-denklem", (-1, 6.5), (-1, 5), 70)
F.axes(nums=False)
P0 = (1.5, 1.5 * R3)
F.guide([(-0.4, -0.4 * R3), (2.5, 2.5 * R3)])
F.line([(0, 0), P0], TEXT, 1.4, opacity=0.8)
F.guide([P0, (1.5, 0)], dash="2 3", opacity=0.6, width=1.1)
F.guide([P0, (0, P0[1])], dash="2 3", opacity=0.6, width=1.1)
F.fline(lambda x: (6 - x) / R3, -0.5, 6.5, color=TEXT, width=2.2)
F.right_angle(P0, (-0.5, -R3 / 2), (R3 / 2, -0.5))
F.arc((0, 0), 0.6, 0, 60)
F.point((0, 0))
F.point(P0)
F.label((6.5, (6 - 6.5) / R3), [I("d")], "s", 7, size=NAME + 1)
F.label((2.5, 2.5 * R3), [ELL], "e", 6, size=NAME + 1)
F.label((0, 0), [I("O")], "se", 5, size=NAME)
F.label_at(F.X(P0[0]) + 18, F.Y(P0[1]) - 1, [Pn("P", "0") + "(" + X0 + ", " + Y0 + ")"], "start", NAME)
F.label((0.75, 0.75 * R3), [I("r")], "nw", 6, size=NAME)
F.label((0.6 * math.cos(math.radians(30)), 0.6 * math.sin(math.radians(30))), [I(OMEGA)], "e", 6, size=NAME)
F.label((1.5, 0), [X0], "s", 7)
F.label((0, P0[1]), [Y0], "w", 8)
F.finish(
    "Normal denklemin kuruluşu: orijinden <em>d</em>'ye inen dikme &#8467; doğrusu üzerindedir, uzunluğu "
    "<em>r</em>, <em>X</em>-ekseniyle yaptığı açı <em>&#969;</em>'dır. Dikmenin ayağı "
    "<em>P</em><sub>0</sub> = (<em>r</em> cos <em>&#969;</em>, <em>r</em> sin <em>&#969;</em>) noktasıdır.",
    "Line d, the perpendicular l from the origin with foot P0, length r and angle omega")

# ============================================================ dde-normal-ornek-yatay
F = Fig("normal-ornek-yatay", (-3, 3), (-1, 3), 85)
F.axes()
F.line([(-3, 1.75), (3, 1.75)], THEORY, 2.2)
F.thick((0, 0), (0, 1.75))
F.right_angle((0, 1.75), (0, -1), (1, 0))
F.arc((0, 0), 0.45, 0, 90)
F.point((0, 0))
F.point((0, 1.75))
F.label_at(F.X(3), F.Y(1.75) - 12, [I("y") + " " + MINUS, Frac("7", "4"), "= 0"], "end", EQ, THEORY)
F.label((0, 0), [I("O")], "sw", 5, size=NAME)
F.label((0, 1.75), [Paren("("), "0,", Frac("7", "4"), Paren(")")], "ne", 8)
F.label((0, 0.875), [I("r") + " =", Frac("7", "4")], "w", 9, color=PRACTICE)
F.label((0.45 * math.cos(math.radians(45)), 0.45 * math.sin(math.radians(45))),
        [I(OMEGA) + " =", Frac(I(PI_), "2")], "ne", 6)
F.finish(
    "4<em>y</em> &#8722; 7 = 0 doğrusuna orijinden inen dikme <em>Y</em>-ekseninin pozitif yarısı üzerindedir: "
    "<em>r</em> = 7/4, <em>&#969;</em> = <em>&#960;</em>/2.",
    "Horizontal line y = 7/4 with the perpendicular from the origin, r = 7/4 and omega = pi/2")

# ============================================================ dde-normal-ornek-ucuncu
F = Fig("normal-ornek-ucuncu", (-5, 2), (-4, 2), 72)
F.axes()
H = (-1.2, -1.6)
F.line([(-5, 1.25), (1.5, -3.625)], THEORY, 2.2)
F.thick((0, 0), H)
F.right_angle(H, (0.6, 0.8), (-0.8, 0.6))
F.arc((0, 0), 0.5, 0, 180 + math.degrees(math.atan(4 / 3)))
F.point((0, 0))
F.point(H)
F.label_at(F.X(-5) - 4, F.Y(1.25) - 12, [eqn("3x + 4y + 10 = 0")], "start", EQ, THEORY)
F.label((0, 0), [I("O")], "ne", 5, size=NAME)
F.label_at(F.X(H[0]) + 12, F.Y(H[1]) + 30,
           [Paren("("), MINUS, Frac("6", "5"), ", " + MINUS, Frac("8", "5"), Paren(")")], "end", EQ)
F.label((-0.66, -0.88), [I("r") + " = 2"], "e", 9, color=PRACTICE)
F.label((0.5 * math.cos(math.radians(150)), 0.5 * math.sin(math.radians(150))),
        [I(OMEGA) + " " + APPROX + " 233,13" + DEG], "nw", 6)
F.finish(
    "3<em>x</em> + 4<em>y</em> + 10 = 0 doğrusu: dikmenin ayağı (&#8722;6/5, &#8722;8/5) üçüncü bölgededir, "
    "<em>r</em> = 2 ve <em>&#969;</em> = <em>&#960;</em> + arctan(4/3) &#8776; 233,13&#176;.",
    "Line 3x + 4y + 10 = 0 with the perpendicular from the origin to (-6/5, -8/5), r = 2, omega about 233 degrees")

# ============================================================ dde-uzaklik-karsi-taraf
F = Fig("uzaklik-karsi-taraf", (-1, 5.5), (-1, 5.5), 80)
F.axes(nums=False)
c = 1 / S2
QR, QRS = (2 * c, 2 * c), (3.5 * c, 3.5 * c)
P, H = (1.768, 3.182), (0.707, 2.121)
F.guide([(-0.5, -0.5), (3.5, 3.5)])
F.fline(lambda x: 2 * S2 - x, -0.5, 3.3, color=TEXT, width=2.2)
F.fline(lambda x: 3.5 * S2 - x, -0.3, 5.3, color=THEORY, width=2.2, dash="7 5")
F.line([P, H], PRACTICE, 1.9, "5 4")
F.right_angle(QR, (1, 1), (-1, 1))
F.right_angle(QRS, (1, 1), (-1, 1))
F.right_angle(H, (1, 1), (1, -1))
F.arc((0, 0), 0.5, 0, 45)
F.point((0, 0))
F.point(QR, TEXT, 3.2)
F.point(QRS, TEXT, 3.2)
F.point(P)
F.point(H, TEXT, 3.4)
F.label((3.5, 3.5), [ELL], "e", 6, size=NAME + 1)
F.label((-0.5, 2 * S2 + 0.5), [I("d")], "w", 7, size=NAME + 1)
F.label((-0.3, 3.5 * S2 + 0.3), [Bar("d")], "w", 7, size=NAME + 1, color=THEORY)
F.label((c, c), [I("r")], "se", 5, size=NAME)
F.label((2.75 * c, 2.75 * c), [I("s")], "se", 5, size=NAME)
F.label((0, 0), [I("O")], "se", 5, size=NAME)
F.label((0.5 * math.cos(math.radians(22.5)), 0.5 * math.sin(math.radians(22.5))), [I(OMEGA)], "e", 6, size=NAME)
F.label(P, [PXY], "ne", 8, size=NAME)
F.label(H, [I("H")], "sw", 7, size=NAME)
F.label(((P[0] + H[0]) / 2, (P[1] + H[1]) / 2), [I("s")], "nw", 6, size=NAME, color=PRACTICE)
F.finish(
    "Birinci konum: <em>P</em>, <em>d</em>'nin orijinle karşı tarafındadır. <em>P</em>'den geçen paralel "
    "<em>d&#773;</em>, &#8467; dikmesini <em>Q</em><sub><em>r</em>+<em>s</em></sub>'de keser; <em>P</em>'nin "
    "<em>d</em>'ye uzaklığı iki paralel arasındaki <em>s</em> uzaklığıdır.",
    "Point P on the far side of line d: the parallel through P is at distance s beyond d along the perpendicular l")

# ============================================================ dde-uzaklik-ayni-taraf
F = Fig("uzaklik-ayni-taraf", (-5, 3.5), (-4, 3.5), 70)
F.axes(nums=False)
c = 1 / S2
QR, QMR, QMRT = (1.5 * c, 1.5 * c), (-1.5 * c, -1.5 * c), (-3 * c, -3 * c)
P, H = (-2.828, -1.414), (0.354, 1.768)
F.guide([(-2.8, -2.8), (2, 2)])
F.fline(lambda x: 1.5 * S2 - x, -1, 3.2, color=TEXT, width=2.2)
F.fline(lambda x: -1.5 * S2 - x, -4.5, 1, color=BASE, width=2.2)
F.fline(lambda x: -3 * S2 - x, -5, -0.8, color=THEORY, width=2.2, dash="7 5")
F.line([P, H], PRACTICE, 1.9, "5 4")
F.right_angle(QR, (-1, -1), (1, -1))
F.right_angle(QMR, (1, 1), (1, -1))
F.right_angle(QMRT, (1, 1), (1, -1))
F.right_angle(H, (-1, -1), (1, -1))
F.arc((0, 0), 0.45, 0, 45)
F.point((0, 0))
for Q in (QR, QMR, QMRT):
    F.point(Q, TEXT, 3.2)
F.point(P)
F.point(H, TEXT, 3.4)
F.label((2, 2), [ELL], "e", 6, size=NAME + 1)
F.label_at(F.X(3.3), F.Y(1.5 * S2 - 3.2) + 24,
           [I("d") + ": " + I("x") + " cos " + I(OMEGA) + " + " + I("y") + " sin " + I(OMEGA) + " " + MINUS
            + " " + I("r") + " = 0"], "end", EQ)
F.label((1, -1.5 * S2 - 1), [Bar("d", 2)], "e", 7, size=NAME + 1, color=BASE)
F.label((-0.8, -3 * S2 + 0.8), [Bar("d")], "e", 7, size=NAME + 1, color=THEORY)
F.label((0.75 * c, 0.75 * c), [I("r")], "nw", 5, size=NAME)
F.label((-0.75 * c, -0.75 * c), [I("r")], "nw", 5, size=NAME)
F.label((-2.25 * c, -2.25 * c), [I("t")], "nw", 5, size=NAME)
F.label((0, 0), [I("O")], "se", 5, size=NAME)
F.label((0.45 * math.cos(math.radians(22.5)), 0.45 * math.sin(math.radians(22.5))), [I(OMEGA)], "e", 6, size=NAME)
F.label(P, [PXY], "w", 9, dy=8, size=NAME)
F.label(H, [I("H")], "n", 10, size=NAME)
F.label(((P[0] + H[0]) / 2, (P[1] + H[1]) / 2), [I("t") + " + 2" + I("r")], "nw", 6, color=PRACTICE)
F.finish(
    "İkinci konum: <em>P</em> orijinle aynı taraftadır ve orijinin ötesindedir. Yeşil doğru <em>d</em>'nin "
    "orijine göre simetriğidir; <em>P</em>'den geçen paralel <em>d&#773;</em> ondan <em>t</em> kadar ötededir ve "
    "<em>P</em>'nin <em>d</em>'ye uzaklığı <em>t</em> + 2<em>r</em>'dir.",
    "Point P on the same side of line d as the origin, beyond it: the distance to d is t + 2r",
    css=WIDE)

# ============================================================ dde-uzaklik-ornek
F = Fig("uzaklik-ornek", (-4, 5), (-4, 4), 58)


def half_plane(f, xr, yr):
    """Corners of the panel rectangle clipped to f(x, y) <= 0 (f affine)."""
    rect = [(xr[0], yr[0]), (xr[1], yr[0]), (xr[1], yr[1]), (xr[0], yr[1])]
    out = []
    for i in range(4):
        a, b = rect[i], rect[(i + 1) % 4]
        fa, fb = f(*a), f(*b)
        if fa <= 0:
            out.append(a)
        if fa * fb < 0:
            t = fa / (fa - fb)
            out.append((a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])))
    return out


F.polygon(half_plane(lambda x, y: 8 * x + 15 * y - 24, (-4, 5), (-4, 4)), THEORY, 0.07)
F.axes()
P, H = (-2, -3), (6 / 17, 24 / 17)
F.fline(lambda x: (24 - 8 * x) / 15, -3.5, 5, color=THEORY, width=2.2)
F.line([P, H], PRACTICE, 1.9, "5 4")
F.right_angle(H, (-40, -75), (15, -8))
F.point((0, 0))
F.point(P)
F.point(H)
F.label_at(F.X(5), F.Y((24 - 40) / 15) + 24, [eqn("8x + 15y - 24 = 0")], "end", EQ, THEORY)
F.label((0, 0), [I("O")], "sw", 5, size=NAME)
F.label(P, [I("P") + "(" + m("2") + ", " + m("3") + ")"], "w", 10, size=NAME)
F.label_at(F.X(H[0]) - 3, F.Y(H[1]) - 16, [I("H")], "end", NAME)
F.label(((P[0] + H[0]) / 2, (P[1] + H[1]) / 2), ["5"], "se", 6, color=PRACTICE)
F.finish(
    "<em>P</em>(&#8722;2, &#8722;3) noktasının 8<em>x</em> + 15<em>y</em> &#8722; 24 = 0 doğrusuna uzaklığı "
    "|<em>PH</em>| = 5'tir. Taralı yarı düzlem doğrunun orijin tarafıdır; <em>s</em> = &#8722;5 &lt; 0 olduğundan "
    "<em>P</em> de bu taraftadır.",
    "Point P(-2, -3), line 8x + 15y - 24 = 0 and the foot H of the perpendicular; distance 5, origin side shaded")

# ============================================================ dde-normal-alistirma-ii
F = Fig("normal-alistirma-ii", (-9, 2), (-9, 2), 46)
F.axes(xnums=[-8, -6, -4, -2], ynums=[-8, -6, -4, -2])
H = (-4, -4)
F.line([(-9, 1), (1, -9)], THEORY, 2.2)
F.thick((0, 0), H)
F.right_angle(H, (1, 1), (-1, 1))
F.arc((0, 0), 1.0, 0, 225)
F.point((0, 0))
F.point(H)
F.label_at(F.X(-9) + 12, F.Y(1) + 2, [eqn("x + y + 8 = 0")], "start", EQ, THEORY)
F.label((0, 0), [I("O")], "ne", 5, size=NAME)
F.label(H, ["(" + m("4") + ", " + m("4") + ")"], "sw", 8)
F.label((-2, -2), [I("r") + " = 4" + SQRT + "2"], "se", 7, color=PRACTICE)
F.label((math.cos(math.radians(135)), math.sin(math.radians(135))),
        [I(OMEGA) + " =", Frac("5" + I(PI_), "4")], "nw", 5)
F.finish(
    "<em>x</em> + <em>y</em> + 8 = 0 doğrusuna orijinden inen dikmenin ayağı (&#8722;4, &#8722;4)'tür: "
    "<em>r</em> = 4&#8730;2, <em>&#969;</em> = 5<em>&#960;</em>/4.",
    "Line x + y + 8 = 0, perpendicular from the origin to (-4, -4), r = 4 sqrt 2 and omega = 5 pi/4")

# ============================================================ dde-normal-alistirma-iii
F = Fig("normal-alistirma-iii", (-7, 2), (-3, 3), 58)
F.axes()
H = (-5, 0)
F.thick((0, 0), H, width=3.8)
F.line([(-5, -3), (-5, 3)], THEORY, 2.2)
F.right_angle(H, (1, 0), (0, 1))
F.arc((0, 0), 0.8, 0, 180)
F.point((0, 0))
F.point(H)
F.label_at(F.X(-5) - 8, F.Y(3) + 5, [eqn("x + 5 = 0")], "end", EQ, THEORY)
F.label((0, 0), [I("O")], "se", 6, size=NAME)
F.label(H, ["(" + m("5") + ", 0)"], "nw", 8)
F.label((-2.5, 0), [I("r") + " = 5"], "s", 25, color=PRACTICE)
F.label_at(F.X(0) + 6, F.Y(0.8) - 8, [I(OMEGA) + " = " + I(PI_)], "start", EQ)
F.finish(
    "<em>x</em> + 5 = 0 düşey doğrusuna orijinden inen dikme <em>X</em>-ekseninin negatif yarısı üzerindedir: "
    "ayağı (&#8722;5, 0), <em>r</em> = 5, <em>&#969;</em> = <em>&#960;</em>.",
    "Vertical line x = -5, perpendicular from the origin along the negative x axis, r = 5 and omega = pi")

# ============================================================ dde-normal-alistirma-iv
F = Fig("normal-alistirma-iv", (-1, 7), (-1, 10), 50)
F.axes(xnums=[2, 4, 6], ynums=[2, 4, 6, 8, 10])
H = (9 * R3 / 4, 9 / 4)
F.fline(lambda x: 9 - R3 * x, -0.5, 5.7, color=THEORY, width=2.2)
F.thick((0, 0), H)
F.right_angle(H, (-R3 / 2, -0.5), (0.5, -R3 / 2))
F.arc((0, 0), 1.2, 0, 30)
F.point((0, 0))
F.point(H)
F.label_at(F.X(0) + 10, F.Y(9 + 0.5 * R3) + 5, [SQ3 + " " + eqn("x + y - 9 = 0")], "start", EQ, THEORY)
F.label((0, 0), [I("O")], "sw", 5, size=NAME)
F.label(H, [Paren("("), Frac("9" + SQ3, "4"), ",", Frac("9", "4"), Paren(")")], "ne", 9)
F.label((H[0] / 2, H[1] / 2), [I("r") + " =", Frac("9", "2")], "nw", 6, color=PRACTICE)
F.label((1.2 * math.cos(math.radians(15)), 1.2 * math.sin(math.radians(15))),
        [I(OMEGA) + " =", Frac(I(PI_), "6")], "e", 7, dy=-5)
F.finish(
    "&#8730;3<em>x</em> + <em>y</em> &#8722; 9 = 0 doğrusuna orijinden inen dikmenin ayağı "
    "(9&#8730;3/4, 9/4)'tür: <em>r</em> = 9/2, <em>&#969;</em> = <em>&#960;</em>/6.",
    "Line sqrt3 x + y - 9 = 0, perpendicular from the origin with r = 9/2 and omega = pi/6")

# ============================================================ dde-normal-alistirma-orijinden
F = Fig("normal-alistirma-orijinden", (-3, 4), (-3, 3), 72)
F.axes()
F.line([(-3, -2.25), (4, 3)], THEORY, 2.2)
F.guide([(-2.1, 2.8), (1.5, -2)])
F.right_angle((0, 0), (-0.8, -0.6), (0.6, -0.8))
F.arc((0, 0), 0.7, 0, 180 - math.degrees(math.atan(4 / 3)), color=PRACTICE)
F.arrow((0, 0), (-0.9, 1.2), PRACTICE, 2.4)
F.point((0, 0))
F.label_at(F.X(4) + 2, F.Y(3) + 22, [eqn("3x - 4y = 0")], "start", EQ, THEORY, flip=True)
F.label((-2.1, 2.8), [ELL], "w", 6, size=NAME + 1)
F.label_at(F.X(0) + 18, F.Y(0) + 17, [I("O")], "start", NAME)
F.label_at(F.X(0) + 8, F.Y(0.7) - 19, [I(OMEGA) + " " + APPROX + " 126,87" + DEG], "start", EQ, PRACTICE)
F.finish(
    "Orijinden geçen 3<em>x</em> &#8722; 4<em>y</em> = 0 doğrusu (<em>r</em> = 0). &#8467; doğruya dik olan "
    "doğrudur; seçilen işaret onun üst yarı düzlemdeki ışınını verir: <em>&#969;</em> &#8776; 126,87&#176;.",
    "Line 3x - 4y = 0 through the origin, the perpendicular l and the direction omega about 126.87 degrees")

# ============================================================ dde-uzaklik-alistirma-ii
F = Fig("uzaklik-alistirma-ii", (-3, 5), (-2, 8), 52)
F.axes()
P, H = (-1, 7), (121 / 50, 61 / 25)
F.fline(lambda x: 0.75 * x + 0.625, -3, 5, color=THEORY, width=2.2)
F.line([P, H], PRACTICE, 1.9, "5 4")
F.right_angle(H, (-0.6, 0.8), (0.8, 0.6))
F.point((0, 0))
F.point(P)
F.point(H)
F.label_at(F.X(5) + 2, F.Y(4.375) + 22, [eqn("6x - 8y + 5 = 0")], "start", EQ, THEORY, flip=True)
F.label((0, 0), [I("O")], "se", 5, size=NAME)
F.label(P, [I("P") + "(" + m("1") + ", 7)"], "w", 10, size=NAME)
F.label(H, [I("H")], "se", 7, size=NAME)
F.label(((P[0] + H[0]) / 2, (P[1] + H[1]) / 2), [Frac("57", "10", 12)], "ne", 7, color=PRACTICE)
F.finish(
    "<em>P</em>(&#8722;1, 7) noktasının 6<em>x</em> &#8722; 8<em>y</em> + 5 = 0 doğrusuna uzaklığı "
    "|<em>PH</em>| = 57/10'dur; <em>s</em> &gt; 0 olduğundan <em>P</em> ile orijin doğrunun farklı "
    "taraflarındadır.",
    "Point P(-1, 7), line 6x - 8y + 5 = 0 and the foot H; distance 57/10, P and the origin on opposite sides")

# ============================================================ dde-paralel-dogru
F = Fig("paralel-dogru", (-3, 5), (-7, 5), 46)
F.axes(xnums=[-2, 2, 4], ynums=[-6, -4, -2, 2, 4])
F.fline(lambda x: 1.5 * x + 2.5, -3, 1.6, color=TEXT, width=2.2, opacity=0.6)
F.fline(lambda x: 1.5 * x - 6, -0.6, 5, color=THEORY, width=2.2)
F.chevron((-0.9, 1.5 * -0.9 + 2.5), (2, 3), TEXT, 8.5)
F.chevron((3.1, 1.5 * 3.1 - 6), (2, 3), THEORY, 8.5)
F.point((2, -3))
F.label_at(F.X(1.6) + 10, F.Y(4.9) + 5, [eqn("3x - 2y + 5 = 0")], "start", EQ, flip=True)
F.label_at(F.X(5) + 10, F.Y(1.5) + 5, [eqn("3x - 2y - 12 = 0")], "start", EQ, THEORY, flip=True)
F.label((2, -3), ["(2, " + m("3") + ")"], "se", 8)
F.finish(
    "(2, &#8722;3)'ten geçen ve 3<em>x</em> &#8722; 2<em>y</em> + 5 = 0'a paralel olan doğru "
    "3<em>x</em> &#8722; 2<em>y</em> &#8722; 12 = 0'dır; iki doğrunun eğimi de 3/2'dir.",
    "Two parallel lines of slope 3/2, the new one through (2, -3), marked with parallel arrows")

# ============================================================ dde-dik-dogru
F = Fig("dik-dogru", (-5, 3), (-2, 6), 58)
F.axes()
K = (-63 / 29, 31 / 29)
F.fline(lambda x: (1 - 2 * x) / 5, -5, 3, color=TEXT, width=2.2, opacity=0.6)
F.fline(lambda x: 2.5 * x + 6.5, -3.4, -0.4, color=THEORY, width=2.2)
F.right_angle(K, (5, -2), (2, 5))
F.point((-1, 4))
F.point(K, TEXT, 3.4)
F.label_at(F.X(3) - 8, F.Y(-1) - 13, [eqn("2x + 5y - 1 = 0")], "start", EQ, flip=True)
F.label_at(F.X(0) + 9, F.Y(5.5) + 5, [eqn("5x - 2y + 13 = 0")], "start", EQ, THEORY, flip=True)
F.label((-1, 4), ["(" + m("1") + ", 4)"], "e", 9)
F.label_at(F.X(K[0]) - 5, F.Y(K[1]) - 15, [I("K")], "end", NAME)
F.finish(
    "(&#8722;1, 4)'ten geçen ve 2<em>x</em> + 5<em>y</em> &#8722; 1 = 0'a dik olan doğru "
    "5<em>x</em> &#8722; 2<em>y</em> + 13 = 0'dır; iki doğru <em>K</em>(&#8722;63/29, 31/29) noktasında dik kesişir.",
    "Line 5x - 2y + 13 = 0 through (-1, 4) perpendicular to 2x + 5y - 1 = 0, meeting it at K")

# ============================================================ dde-esit-parca
F = Fig("esit-parca", (-1, 6), (-1, 6), 66)
F.axes()
F.thick((0, 0), (5, 0), PRACTICE, 3.8, 0.85)
F.thick((0, 0), (0, 5), PRACTICE, 3.8, 0.85)
F.eq_tick((2.5, 0), (1, 0), 13, PRACTICE, 1.8, 1.0)
F.eq_tick((0, 2.5), (0, 1), 13, PRACTICE, 1.8, 1.0)
F.line([(-0.5, 5.5), (5.5, -0.5)], THEORY, 2.2)
F.point((5, 0))
F.point((0, 5))
F.point((2, 3))
F.label_at(F.X(5.5) + 8, F.Y(-0.5) + 6, [eqn("x + y - 5 = 0")], "start", EQ, THEORY, flip=True)
F.label((5, 0), ["(5, 0)"], "ne", 7)
F.label((0, 5), ["(0, 5)"], "ne", 7)
F.label((2, 3), ["(2, 3)"], "ne", 7)
F.label_at(F.X(2.5), F.Y(0) + 38, ["5"], "middle", NAME, PRACTICE, bold=True)
F.label_at(F.X(0) - 32, F.Y(2.5) + 5, ["5"], "end", NAME, PRACTICE, bold=True)
F.label((0, 0), [I("O")], "sw", 5, size=NAME)
F.finish(
    "(2, 3)'ten geçen ve eksenlerin pozitif yarılarından eşit parçalar ayıran doğru "
    "<em>x</em> + <em>y</em> &#8722; 5 = 0'dır; iki parçanın uzunluğu da 5'tir.",
    "Line x + y - 5 = 0 through (2, 3) cutting segments of length 5 from both axes")

# ============================================================ dde-paralel-uzaklik
F = Fig("paralel-uzaklik", (-3, 4), (-3, 3), 72)
F.axes()
H1, H2 = (-6 / 25, 8 / 25), (24 / 25, -32 / 25)
e = (0.8, 0.6)   # direction of the two lines


def off(P, k):
    return (P[0] - k * e[0], P[1] - k * e[1])


F.guide([(-2.25, 3), (2.25, -3)])
F.guide([(0, 0), off((0, 0), 1.12)], dash="2 3", opacity=0.6, width=1.0)
F.fline(lambda x: 0.75 * x + 0.5, -3, 3, color=THEORY, width=2.2)
F.fline(lambda x: 0.75 * x - 2, -1.3, 4, color=PRACTICE, width=2.2)
F.right_angle(H1, (-0.6, 0.8), (0.8, 0.6))
F.right_angle(H2, (0.6, -0.8), (0.8, 0.6))
F.dim(off(H1, 1.0), off((0, 0), 1.0))
F.dim(off((0, 0), 1.0), off(H2, 1.0))
F.dim(off(H1, 1.8), off(H2, 1.8))
F.point((0, 0))
F.point(H1, TEXT, 3.4)
F.point(H2, TEXT, 3.4)
F.label_at(F.X(-3) + 4, F.Y(-1.75) - 15, [eqn("3x - 4y + 2 = 0")], "end", EQ, THEORY, flip=True)
F.label_at(F.X(4) - 2, F.Y(1) + 22, [eqn("3x - 4y - 8 = 0")], "start", EQ, PRACTICE, flip=True)
mid1 = off(((H1[0]) / 2, (H1[1]) / 2), 1.0)
mid2 = off(((H2[0]) / 2, (H2[1]) / 2), 1.0)
mid3 = off(((H1[0] + H2[0]) / 2, (H1[1] + H2[1]) / 2), 1.8)
F.label(mid1, [Frac("2", "5", 12)], "sw", 6)
F.label(mid2, [Frac("8", "5", 12)], "sw", 6)
F.label(mid3, ["2"], "sw", 6, size=NAME)
F.label((0, 0), [I("O")], "ne", 5, size=NAME)
F.finish(
    "Paralel 3<em>x</em> &#8722; 4<em>y</em> + 2 = 0 ve 3<em>x</em> &#8722; 4<em>y</em> &#8722; 8 = 0 doğruları "
    "orijinin iki yanındadır: orijine uzaklıkları 2/5 ve 8/5, aralarındaki uzaklık 2/5 + 8/5 = 2'dir. "
    "Ölçüler, ortak dikme doğrultusunda çizilmiştir.",
    "Two parallel lines on both sides of the origin at distances 2/5 and 8/5, distance 2 between them",
    css=WIDE)

# ============================================================ dde-ucgen-yukseklik
F = Fig("ucgen-yukseklik", (0, 6.5), (0, 7), 72)
A, B, C = (1, 1), (5, 4), (2, 6)
D = (101 / 25, 82 / 25)
F.polygon([A, B, C], THEORY, 0.13)
F.axes()
F.guide([(0, 0.25), (6.5, (3 * 6.5 + 1) / 4)])
F.polygon([A, B, C], THEORY, 0.0, THEORY, 1.9)
F.line([C, D], PRACTICE, 1.9, "5 4")
F.right_angle(D, (-0.6, 0.8), (0.8, 0.6))
F.point(A)
F.point(B)
F.point(C)
F.point(D, TEXT, 3.2)
F.label_at(F.X(6.5) + 2, F.Y((3 * 6.5 + 1) / 4) + 22, [eqn("3x - 4y + 1 = 0")], "start", EQ, flip=True)
F.label(A, [I("A") + "(1, 1)"], "w", 9, dy=-3, size=NAME)
F.label_at(F.X(5) + 10, F.Y(4) + 15, [I("B") + "(5, 4)"], "start", NAME)
F.label(C, [I("C") + "(2, 6)"], "nw", 7, size=NAME)
F.label(D, [I("D")], "se", 6, size=NAME)
F.label((C[0] + 0.72 * (D[0] - C[0]), C[1] + 0.72 * (D[1] - C[1])),
        [I("h") + " =", Frac("17", "5")], "e", 8, dy=-6, color=PRACTICE)
F.label((3, 2.5), ["5"], "se", 6, size=NAME)
F.finish(
    "<em>A</em>(1, 1), <em>B</em>(5, 4), <em>C</em>(2, 6) üçgeninde <em>C</em>'den <em>AB</em>'ye inen yükseklik "
    "<em>h</em> = 17/5'tir; taban |<em>AB</em>| = 5 olduğundan alan 17/2'dir.",
    "Triangle A(1, 1), B(5, 4), C(2, 6) with the altitude CD of length 17/5 onto AB")


# ---------------------------------------------------------------------------
for name, content in OUT.items():
    with io.open(OUT_DIR / f"{PREFIX}{name}.md", "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
print(f"generated {len(OUT)} figures:", ", ".join(OUT))
