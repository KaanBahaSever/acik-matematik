# -*- coding: utf-8 -*-
"""
Figures for the "Vektörler" chapter of Analitik Geometri
(dersler/analitik-geometri/vektorler.qmd).

The figures are NOT produced at build time. Run this script, then

    python scripts/center_figures.py "analytic-vek-*.md" --keep-width
    python scripts/check_figure_labels.py "scripts/_figures/analytic-vek-*.md"

and paste the resulting markup into the .qmd file. Figures go INSIDE the box
they explain (theorem, proof, example or solution), never inside a definition
box: a figure that illustrates a definition sits directly below that box.

Every label is placed by the centre of its estimated box, pushed away from the
point or the segment it names (see at_point / at_segment), so it never sits on
a line. Vector names with an arrow over them (the book's \\overrightarrow{AB})
are drawn as text plus a small arrow, because the combining arrow U+20D7 is not
in the figure font.

The captions are Turkish on purpose: they are the text shown on the site.
The aria labels are plain ASCII.

Usage:   python scripts/analytic_figures/vek.py
Output:  scripts/_figures/analytic-vek-<name>.md
"""
import html
import io
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import *  # noqa: E402,F403 - Plot, figure, colors, WIDE, cplane, ...
from svg_plot3 import *  # noqa: E402,F403 - Camera, Space, space_panel, vector helpers

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "analytic-vek-"
OUT = {}

MINUS_S = "&#8722;"
DBAR = "&#8214;"
ALPHA, BETA, GAMMA = "&#945;", "&#946;", "&#947;"

NAME = 14      # point and vector names
NOTE = 13      # coordinate labels, titles, axis names
TICK = 11      # axis numbers
THICK, HEAD = 2.6, 12.0
THIN, THIN_HEAD = 1.7, 9.5
DOT_R = 4.0


# ---------------------------------------------------------------------------
# text helpers
# ---------------------------------------------------------------------------
_TAG = re.compile(r"<[^>]+>")
_TSPAN = re.compile(r"<tspan\b([^>]*)>(.*?)</tspan>", re.S)


_NARROW = set(" ()[],.;:|!'1")


def _chars_w(s, em):
    """Advance of a plain string in em: narrow punctuation and spaces count less."""
    return sum(0.34 if ch in _NARROW else em for ch in s)


def text_w(s, size, em=0.60):
    """Generous width estimate of a text body (tspans at their own size)."""
    w = 0.0
    for m in _TSPAN.finditer(s):
        fs = re.search(r'font-size="([\d.]+)"', m.group(1))
        inner = html.unescape(_TAG.sub("", m.group(2))).replace("​", "")
        w += _chars_w(inner, em) * (float(fs.group(1)) if fs else size)
    rest = html.unescape(_TAG.sub("", _TSPAN.sub("", s))).replace("​", "")
    return w + _chars_w(rest, em) * size


def sub(s, size=NAME):
    """Subscript inside an SVG <text>."""
    fs = max(11.0, round(0.76 * size, 1))
    d = round(0.28 * size, 1)
    return f'<tspan font-size="{fs}" dy="{d}">{s}</tspan><tspan dy="{-d}">&#8203;</tspan>'


def htext(p, px, py, s, color=TEXT, size=NAME, anchor="middle", italic=False, bold=False):
    """Text at a pixel position with a page-coloured halo, so faint lines break under it."""
    st = (' font-style="italic"' if italic else "") + (' font-weight="600"' if bold else "")
    p.add(f'<text x="{px:.1f}" y="{py:.1f}" fill="{color}" font-size="{size}" text-anchor="{anchor}"{st} '
          f'stroke="{BG}" stroke-width="3.4" stroke-linejoin="round" paint-order="stroke">{s}</text>')


class Lab:
    """A label made of text pieces, over-arrowed names and stacked fractions.

    It is drawn by the centre of its box; w and h are the estimated box size in pixels.
    """

    def __init__(self, size=NAME, color=TEXT):
        self.size, self.color, self.items = size, color, []

    def t(self, s, italic=True):
        desc = 0.26 * self.size if "dy=" in s else 0.0
        self.items.append(("t", s, italic, text_w(s, self.size), 0.72 * self.size, desc))
        return self

    def v(self, letters):
        """Letters with an arrow over them: the book's overrightarrow."""
        w = text_w(letters, self.size, 0.66) + 2
        self.items.append(("v", letters, True, w, 1.10 * self.size, 0.0))
        return self

    def f(self, num, den, fs=None):
        """Stacked fraction num / den."""
        fs = fs or max(11.0, 0.86 * self.size)
        w = max(text_w(num, fs), text_w(den, fs)) + 5
        axis = 0.30 * self.size
        asc = axis + 3 + 0.92 * fs
        desc = -axis + 3 + 0.76 * fs
        self.items.append(("f", (num, den, fs), True, w, asc, desc))
        return self

    def g(self, px):
        """Empty room of px pixels between two pieces."""
        self.items.append(("g", "", False, float(px), 0.0, 0.0))
        return self

    @property
    def w(self):
        return sum(i[3] for i in self.items)

    @property
    def wbox(self):
        """Width used to keep the label clear of its anchor: never below the plain
        0.56 em per character that check_figure_labels.py assumes."""
        n = 0.0
        for kind, s, _, w, _, _ in self.items:
            if kind in ("t", "v"):
                n += text_w(s, self.size, 0.56) if not _NARROW.intersection(s) else                     0.56 * self.size * len(html.unescape(_TAG.sub("", s)).replace("​", ""))
            elif kind == "f":
                n += w
            else:
                n += w
        return max(self.w, n)

    @property
    def asc(self):
        return max(i[4] for i in self.items)

    @property
    def desc(self):
        return max(i[5] for i in self.items)

    @property
    def h(self):
        return self.asc + self.desc

    def draw(self, p, cx, cy):
        base = cy - self.h / 2 + self.asc
        x = cx - self.w / 2
        c, sz = self.color, self.size
        for kind, s, it, w, _, _ in self.items:
            mid = x + w / 2
            if kind == "g":
                pass
            elif kind == "t":
                htext(p, mid, base, s, c, sz, "middle", it)
            elif kind == "v":
                htext(p, mid, base, s, c, sz, "middle", True)
                y = base - 0.94 * sz
                x0 = mid - w / 2 + 0.10 * sz
                x1 = mid + w / 2 + 0.10 * sz
                hl = 0.36 * sz
                p.add(f'<line x1="{x0:.1f}" y1="{y:.1f}" x2="{x1 - hl * 0.7:.1f}" y2="{y:.1f}" '
                      f'stroke="{c}" stroke-width="1.2"/>')
                p.add(f'<polygon points="{x1:.1f},{y:.1f} {x1 - hl:.1f},{y - hl * 0.40:.1f} '
                      f'{x1 - hl:.1f},{y + hl * 0.40:.1f}" fill="{c}"/>')
            else:
                num, den, fs = s
                bar = base - 0.30 * sz
                htext(p, mid, bar - 3 - 0.20 * fs, num, c, fs, "middle", True)
                htext(p, mid, bar + 3 + 0.74 * fs, den, c, fs, "middle", True)
                p.add(f'<line x1="{mid - w / 2 + 1:.1f}" y1="{bar:.1f}" x2="{mid + w / 2 - 1:.1f}" '
                      f'y2="{bar:.1f}" stroke="{c}" stroke-width="1.1"/>')
            x += w


def L(s, size=NAME, color=TEXT, italic=True):
    return Lab(size, color).t(s, italic)


def V(letters, size=NAME, color=TEXT):
    return Lab(size, color).v(letters)


DIRS = {"e": (1, 0), "ne": (1, -1), "n": (0, -1), "nw": (-1, -1), "w": (-1, 0),
        "sw": (-1, 1), "s": (0, 1), "se": (1, 1)}


def _unit(dx, dy):
    n = math.hypot(dx, dy) or 1.0
    return dx / n, dy / n


def at_point(p, xy, lab, pos, gap=6.0, r=DOT_R):
    """Label beside a point: its box lies beyond r + gap pixels in direction pos
    (a compass name or a pixel direction, y down)."""
    dx, dy = _unit(*(DIRS[pos] if isinstance(pos, str) else pos))
    X, Y = p.X(xy[0]), p.Y(xy[1])
    s = abs(dx) * lab.wbox / 2 + abs(dy) * lab.h / 2
    lab.draw(p, X + dx * (r + gap + s), Y + dy * (r + gap + s))


def at_segment(p, a, b, lab, hint, t=0.5, gap=7.0):
    """Label beside segment ab at parameter t, on the side of the compass hint;
    the whole box stays gap pixels away from the line."""
    ax, ay, bx, by = p.X(a[0]), p.Y(a[1]), p.X(b[0]), p.Y(b[1])
    ux, uy = _unit(bx - ax, by - ay)
    hx, hy = DIRS[hint] if isinstance(hint, str) else hint
    nx, ny = -uy, ux
    if nx * hx + ny * hy < 0:
        nx, ny = -nx, -ny
    mx, my = ax + t * (bx - ax), ay + t * (by - ay)
    s = abs(nx) * lab.wbox / 2 + abs(ny) * lab.h / 2
    lab.draw(p, mx + nx * (gap + s), my + ny * (gap + s))


def at_data(p, xy, lab):
    """Label centred at a data point."""
    lab.draw(p, p.X(xy[0]), p.Y(xy[1]))


# ---------------------------------------------------------------------------
# drawing helpers
# ---------------------------------------------------------------------------
def arrow_px(p, x0, y0, x1, y1, color=TEXT, width=THICK, head=HEAD, dash=None, opacity=1.0):
    """Arrow between pixel points, filled head at (x1, y1)."""
    ux, uy = _unit(x1 - x0, y1 - y0)
    sx, sy = x1 - ux * head * 0.8, y1 - uy * head * 0.8
    da = f' stroke-dasharray="{dash}"' if dash else ""
    p.add(f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{sx:.1f}" y2="{sy:.1f}" stroke="{color}" '
          f'stroke-width="{width}"{da} opacity="{opacity}" stroke-linecap="round"/>')
    px, py = -uy, ux
    hw = head * 0.42
    p.add(f'<polygon points="{x1:.1f},{y1:.1f} {x1 - ux * head + px * hw:.1f},{y1 - uy * head + py * hw:.1f} '
          f'{x1 - ux * head - px * hw:.1f},{y1 - uy * head - py * hw:.1f}" fill="{color}" opacity="{opacity}"/>')


def varrow(p, a, b, color=TEXT, width=THICK, head=HEAD, gap0=0.0, gap1=0.0, dash=None,
           opacity=1.0, shift=(0.0, 0.0)):
    """Arrow from data point a to b, trimmed by gap0/gap1 pixels (to stop at a dot's rim)
    and optionally shifted by a pixel offset."""
    ax, ay, bx, by = p.X(a[0]), p.Y(a[1]), p.X(b[0]), p.Y(b[1])
    ux, uy = _unit(bx - ax, by - ay)
    arrow_px(p, ax + ux * gap0 + shift[0], ay + uy * gap0 + shift[1],
             bx - ux * gap1 + shift[0], by - uy * gap1 + shift[1], color, width, head, dash, opacity)


def dot(p, xy, color=TEXT, r=DOT_R):
    p.points([xy], color, r)


def dline(p, a, b, color=TEXT, width=1.2, dash="6 4", opacity=0.55):
    p.line([a, b], color, width, dash, opacity)


def clip_seg(a, b, box):
    """Liang-Barsky: the part of segment ab inside box = (xmin, xmax, ymin, ymax)."""
    (x0, y0), (x1, y1) = a, b
    dx, dy = x1 - x0, y1 - y0
    t0, t1 = 0.0, 1.0
    for pp, q in ((-dx, x0 - box[0]), (dx, box[1] - x0), (-dy, y0 - box[2]), (dy, box[3] - y0)):
        if pp == 0:
            if q < 0:
                return None
            continue
        t = q / pp
        if pp < 0:
            t0 = max(t0, t)
        else:
            t1 = min(t1, t)
    if t0 > t1:
        return None
    return (x0 + t0 * dx, y0 + t0 * dy), (x0 + t1 * dx, y0 + t1 * dy)


def divider(p, x, y0, y1):
    """Faint vertical rule between two side-by-side panels drawn on one Plot."""
    p.line([(x, y0), (x, y1)], TEXT, 1.0, None, 0.18)


def title_px(p, cx, y, lab):
    lab.draw(p, cx, y)


# ---------------------------------------------------------------------------
# 3-D helpers
# ---------------------------------------------------------------------------
def space_fit(cam, pts, width, pad=0.3, x0=24.0, y0=24.0):
    """Equal-aspect panel whose data window is the projection of pts plus pad."""
    pr = [cam.project(P) for P in pts]
    xs, ys = [q[0] for q in pr], [q[1] for q in pr]
    p = space_panel(x0, y0, width, (min(xs) - pad, max(xs) + pad), (min(ys) - pad, max(ys) + pad))
    return p, Space(p, cam)


def pdir(S, v):
    """Pixel direction (y down) of the space vector v."""
    a, b = S.pt((0.0, 0.0, 0.0)), S.pt(v)
    return _unit(S.p.X(b[0]) - S.p.X(a[0]), S.p.Y(b[1]) - S.p.Y(a[1]))


def axes3(S, ends, negs=(0.0, 0.0, 0.0), names=("x", "y", "z"), opacity=0.6, neg_opacity=0.35,
          width=1.2, size=NOTE, gap=5.0):
    """Coordinate axes: faint negative parts, arrows on the positive parts, names past the tips."""
    O = (0.0, 0.0, 0.0)
    for k in range(3):
        e = [0.0, 0.0, 0.0]
        e[k] = 1.0
        tip = vscale(ends[k], tuple(e))
        if negs[k]:
            S.line([vscale(negs[k], tuple(e)), O], TEXT, width, None, neg_opacity)
        S.arrow(O, tip, TEXT, width, 8.0, None, opacity)
        if names and names[k]:
            at_point(S.p, S.pt(tip), L(names[k], size), pdir(S, tuple(e)), gap, 0.0)


def tick3(S, P, axis_vec, lab=None, pos=None, length=7.0, gap=3.0, opacity=0.7):
    """Tick mark across an axis at P, optionally labelled in direction pos."""
    p = S.p
    X, Y = S.pt(P)
    px, py = p.X(X), p.Y(Y)
    dx, dy = pdir(S, axis_vec)
    nx, ny = -dy, dx
    p.add(f'<line x1="{px - nx * length / 2:.1f}" y1="{py - ny * length / 2:.1f}" '
          f'x2="{px + nx * length / 2:.1f}" y2="{py + ny * length / 2:.1f}" stroke="{TEXT}" '
          f'stroke-width="1.1" opacity="{opacity}"/>')
    if lab is not None:
        at_point(p, (X, Y), lab, pos, gap, length / 2)


def arrow3(S, A, B, color=TEXT, width=THICK, head=HEAD, gap0=0.0, gap1=0.0, dash=None,
           opacity=1.0, shift=(0.0, 0.0)):
    varrow(S.p, S.pt(A), S.pt(B), color, width, head, gap0, gap1, dash, opacity, shift)


def seg3(S, A, B, lab, hint, t=0.5, gap=7.0):
    at_segment(S.p, S.pt(A), S.pt(B), lab, hint, t, gap)


def pt3(S, A, lab, pos, gap=6.0, r=DOT_R):
    at_point(S.p, S.pt(A), lab, pos, gap, r)


def tick_num(v):
    return (MINUS_S if v < 0 else "") + fmt(abs(v)).replace(".", ",")


def save(name, W, H, panels, caption, css, aria):
    OUT[name] = figure(round(W), round(H), panels, caption, css, aria)


# ===========================================================================
# 1. yonlu-dogru-parcalari: AB and BA on the same segment
# ===========================================================================
p = cplane(30, 24, 760, (-0.9, 8.9), (-0.75, 3.75))
divider(p, 4.0, -0.5, 3.5)
A1, B1 = (0.0, 0.0), (3.0, 3.0)
varrow(p, A1, B1, THEORY, THICK, HEAD, gap0=DOT_R)
dot(p, A1)
at_point(p, A1, L("A"), "sw")
at_point(p, B1, L("B"), "nw", r=6)
at_segment(p, A1, B1, V("AB", NAME, THEORY), "se")
A2, B2 = (5.0, 0.0), (8.0, 3.0)
varrow(p, B2, A2, THEORY, THICK, HEAD, gap0=DOT_R)
dot(p, B2)
at_point(p, A2, L("A"), "sw", r=6)
at_point(p, B2, L("B"), "ne")
at_segment(p, A2, B2, V("BA", NAME, THEORY), "se")
save("yonlu-dogru-parcalari", 820, p.h + 48, [p],
     "Aynı doğru parçası üzerinde iki farklı yönlü doğru parçası: solda ok <em>B</em>'yi, "
     "sağda <em>A</em>'yı gösterir.",
     WIDE, "The directed segments AB and BA on the same segment, arrows pointing opposite ways")


# ===========================================================================
# 2. ayni-dogrultu / 3. ters-yonlu: arrows on two parallel lines
# ===========================================================================
def two_lines(C, D, caption, aria, name):
    p = cplane(30, 24, 570, (-1.25, 8.05), (-0.75, 2.75))
    for y, k in ((2.0, "1"), (0.0, "2")):
        dline(p, (-1.0, y), (7.0, y))
        at_point(p, (7.0, y), L("d" + sub(k)), "e", 8.0, 0.0)
    A, B = (1.0, 2.0), (4.0, 2.0)
    varrow(p, A, B, THEORY, THICK, HEAD, gap0=DOT_R)
    varrow(p, C, D, THEORY, THICK, HEAD, gap0=DOT_R)
    for Q, s in ((A, "A"), (B, "B"), (C, "C"), (D, "D")):
        if s in "AC":
            dot(p, Q)
        at_point(p, Q, L(s), "n", 6.0, 6.0)
    save(name, 630, p.h + 48, [p], caption, "ders-grafik", aria)


two_lines((1.0, 0.0), (5.0, 0.0),
          "<em>d</em><sub>1</sub> &#8741; <em>d</em><sub>2</sub> olduğundan <em>AB</em> ve <em>CD</em> "
          "yönlü doğru parçaları aynı doğrultuludur.",
          "Two parallel dashed lines d1 and d2 with arrows AB and CD pointing the same way",
          "ayni-dogrultu")
two_lines((4.0, 0.0), (1.0, 0.0),
          "<em>AB</em> ile <em>CD</em> aynı doğrultulu ama ters yönlüdür: biri sağı, öteki solu gösterir.",
          "Two parallel dashed lines with arrow AB pointing right and arrow CD pointing left",
          "ters-yonlu")


# ===========================================================================
# 4. ayni-vektorun-temsilcileri: three representatives of (3, 2)
# ===========================================================================
p = cplane(30, 24, 520, (-1.0, 8.0), (-2.0, 6.0))
p.grid(range(-1, 9), range(-2, 7))
pairs = [((0.0, 0.0), (3.0, 2.0), "A", "B", "sw", "ne"),
         ((4.0, -1.0), (7.0, 1.0), "C", "D", "sw", "ne"),
         ((1.0, 3.0), (4.0, 5.0), "E", "F", "nw", "ne")]
for a, b, sa, sb, pa, pb in pairs:
    varrow(p, a, b, THEORY, THICK, HEAD, gap0=DOT_R)
    dot(p, a)
    at_point(p, a, L(sa), pa)
    at_point(p, b, L(sb), pb, r=5)
save("ayni-vektorun-temsilcileri", 580, p.h + 48, [p],
     "Aynı vektörün üç temsilcisi: <em>AB</em>, <em>CD</em> ve <em>EF</em> okları aynı yönde ve aynı "
     "uzunluktadır; her biri sağa 3, yukarı 2 birim gider.",
     "ders-grafik", "Three equal parallel arrows AB, CD, EF on a square grid, each moving 3 right and 2 up")


# ===========================================================================
# 5. ayni-uclu-iki-parca (3-D): AB and CD with the same coordinate triple
# ===========================================================================
# The usual default (azimuth 35) looks almost along the plane of the two arrows,
# whose normal is (1, -2, 1), and they fall on top of each other. From azimuth 60
# and a low elevation they stand side by side and the scene stays wide.
cam = Camera(azimuth=60, elevation=15)
AX = 3.5
p, S = space_fit(cam, [(AX, 0, 0), (0, AX, 0), (0, 0, AX), (-0.6, 0, 0), (0, -0.6, 0), (0, 0, -0.4)],
                 640, pad=0.35)
axes3(S, (AX, AX, AX), (-0.6, -0.6, -0.4))
ex, ey, ez = (1.0, 0, 0), (0, 1.0, 0), (0, 0, 1.0)
for v in (1, 2, 3):
    tick3(S, (v, 0, 0), ex, None if v == 1 else L(str(v), TICK, TEXT, False), "s")
    tick3(S, (0, v, 0), ey, L(str(v), TICK, TEXT, False), "s")
    tick3(S, (0, 0, v), ez, None if v == 1 else L(str(v), TICK, TEXT, False), "w")
A, B, C, D = (0, 0, 1.0), (0, 1.0, 3.0), (1.0, 0, 0), (1.0, 1.0, 2.0)
arrow3(S, A, B, THEORY, THICK, HEAD, gap0=DOT_R)
arrow3(S, C, D, THEORY, THICK, HEAD, gap0=DOT_R)
for Q in (A, B, C, D):
    S.point(Q, TEXT, DOT_R)
pt3(S, A, L("A(0, 0, 1)", NOTE), (1.0, 0.45))
pt3(S, B, L("B(0, 1, 3)", NOTE), "e")
pt3(S, C, L("C(1, 0, 0)", NOTE), "s", 8.0)
pt3(S, D, L("D(1, 1, 2)", NOTE), "w")
save("ayni-uclu-iki-parca", 700, p.h + 48, [p],
     "<em>AB</em> ve <em>CD</em> yönlü doğru parçaları paralel, aynı yönlü ve eşit uzunluktadır; "
     "ikisi de (0, 1, 2) üçlüsüne gider.",
     WIDE, "Coordinate axes in space with parallel equal arrows from A(0,0,1) to B(0,1,3) and from C(1,0,0) to D(1,1,2)")


# ===========================================================================
# 6. c-noktasi (3-D): the parallelogram ABDC
# ===========================================================================
# The normal of the parallelogram ABDC is about (-12, 25, -10): the same kind of view.
cam = Camera(azimuth=-55, elevation=28)
XR, YR, ZR = (-5.0, 7.0), (-3.0, 5.0), (-3.0, 4.0)
p, S = space_fit(cam, [(XR[1], 0, 0), (XR[0], 0, 0), (0, YR[1], 0), (0, YR[0], 0), (0, 0, ZR[1]),
                       (0, 0, ZR[0]), (6, 4, 2), (-4, -2, -1)], 603, pad=0.5)
axes3(S, (XR[1], YR[1], ZR[1]), (XR[0], YR[0], ZR[0]), neg_opacity=0.5)
for v in (-4, -2, 2, 4, 6):
    tick3(S, (v, 0, 0), ex, L(tick_num(v), TICK, TEXT, False), "s")
for v in (-2, 2, 4):
    tick3(S, (0, v, 0), ey, L(tick_num(v), TICK, TEXT, False), (0.6, 1.0))
# CD crosses the z axis right at z = -2, so that tick keeps its mark but not its number
tick3(S, (0, 0, -2), ez)
tick3(S, (0, 0, 2), ez, L(tick_num(2), TICK, TEXT, False), "w")
A, B, C, D = (1.0, 2.0, 3.0), (6.0, 4.0, 2.0), (-4.0, -2.0, -1.0), (1.0, 0.0, -2.0)
S.line([A, C], TEXT, 1.2, "5 4", 0.6)
S.line([B, D], TEXT, 1.2, "5 4", 0.6)
arrow3(S, A, B, THEORY, THICK, HEAD, gap0=DOT_R)
arrow3(S, C, D, THEORY, THICK, HEAD, gap0=DOT_R)
for Q in (A, B, C, D):
    S.point(Q, TEXT, DOT_R)
pt3(S, A, L("A(1, 2, 3)", NOTE), "nw")
pt3(S, B, L("B(6, 4, 2)", NOTE), "ne")
pt3(S, C, L(f"C({MINUS_S}4, {MINUS_S}2, {MINUS_S}1)", NOTE), "sw")
pt3(S, D, L(f"D(1, 0, {MINUS_S}2)", NOTE), "se")
save("c-noktasi", 700, p.h + 48, [p],
     "<em>AB</em> ile <em>CD</em> aynı vektörü temsil ettiğinden <em>ABDC</em> bir paralelkenardır; "
     "kesikli kenarlar <em>AC</em> ve <em>BD</em>'dir.",
     WIDE, "Axes in space with arrows AB and CD, A(1,2,3), B(6,4,2), C(-4,-2,-1), D(1,0,-2), and dashed sides AC and BD of the parallelogram ABDC")


# ===========================================================================
# 7. konum-vektoru (3-D): OP and the coordinate box
# ===========================================================================
cam = Camera(azimuth=35, elevation=18)
AXE = (5.0, 5.0, 4.2)
Pp = (3.0, 4.0, 2.5)
p, S = space_fit(cam, [(AXE[0], 0, 0), (0, AXE[1], 0), (0, 0, AXE[2]), (-0.7, 0, 0), (0, -0.7, 0), (0, 0, -0.5)],
                 690, pad=0.35)
axes3(S, AXE, (-0.7, -0.7, -0.5))
S.coordinate_box(Pp, TEXT, 0.5, 1.1, "5 4", True)
S.point((3.0, 4.0, 0.0), TEXT, 2.4)
tick3(S, (3.0, 0, 0), ex, L("p" + sub("1", NOTE), NOTE), (0.35, 1.0))
tick3(S, (0, 4.0, 0), ey, L("p" + sub("2", NOTE), NOTE), "s")
tick3(S, (0, 0, 2.5), ez, L("p" + sub("3", NOTE), NOTE), "w")
O = (0.0, 0.0, 0.0)
arrow3(S, O, Pp, THEORY, THICK, HEAD, gap0=DOT_R, gap1=DOT_R)
S.point(O, TEXT, DOT_R)
S.point(Pp, TEXT, DOT_R)
pt3(S, O, L("O"), (-0.5, 0.87), 6.0)
pt3(S, Pp, Lab(NAME).t("P(p" + sub("1") + ", p" + sub("2") + ", p" + sub("3") + ")"), "ne")
seg3(S, O, Pp, V("OP", NAME, THEORY), "nw")
save("konum-vektoru", 700, p.h + 48, [p],
     "<em>P</em> noktasının konum vektörü, başlangıç noktasından <em>P</em>'ye çizilen oktur; "
     "kesikli çizgiler <em>P</em>'nin koordinatlarını eksenler üzerinde okutur.",
     WIDE, "Position vector OP in space with dashed guides from P to the coordinate axes marking p1, p2, p3")


# ===========================================================================
# 8. toplama-uc-uca: adding two vectors tip to tail
# ===========================================================================
p = cplane(30, 24, 755, (-0.7, 9.9), (-0.8, 3.9))
divider(p, 4.3, -0.6, 3.7)
u0, u1 = (0.0, 0.0), (3.0, 0.8)
v0, v1 = (0.8, 1.2), (2.0, 3.5)
varrow(p, u0, u1, TEXT)
varrow(p, v0, v1, TEXT)
at_segment(p, u0, u1, L("u"), "s")
at_segment(p, v0, v1, L("v"), "e")
U0, U1, V1 = (5.0, 0.0), (8.0, 0.8), (9.2, 3.1)
varrow(p, U0, V1, PRACTICE)
varrow(p, U0, U1, TEXT)
varrow(p, U1, V1, TEXT)
at_segment(p, U0, U1, L("u"), "s")
at_segment(p, U1, V1, L("v"), "e")
at_segment(p, U0, V1, L("u + v", NAME, PRACTICE), "nw")
save("toplama-uc-uca", 815, p.h + 48, [p],
     "Solda <em>u</em> ve <em>v</em>; sağda <em>v</em>, <em>u</em>'nun ucundan başlatılmıştır ve "
     "<em>u</em>'nun başlangıcından <em>v</em>'nin ucuna giden ok <em>u</em> + <em>v</em>'dir.",
     WIDE, "Left: vectors u and v drawn apart. Right: v starts at the tip of u and the red arrow u + v closes the triangle")


# ===========================================================================
# 9. ucgen-kurali
# ===========================================================================
p = cplane(30, 24, 710, (-0.8, 6.3), (-0.8, 4.7))
A, B, C = (0.0, 0.0), (4.0, 1.0), (5.0, 4.0)
varrow(p, A, C, PRACTICE, THICK, HEAD, DOT_R, DOT_R + 1)
varrow(p, A, B, TEXT, THICK, HEAD, DOT_R, DOT_R + 1)
varrow(p, B, C, TEXT, THICK, HEAD, DOT_R, DOT_R + 1)
for Q in (A, B, C):
    dot(p, Q)
at_point(p, A, L("A"), "sw")
at_point(p, B, L("B"), "se")
at_point(p, C, L("C"), "ne")
at_segment(p, A, B, V("AB"), "s")
at_segment(p, B, C, V("BC"), "e")
at_segment(p, A, C, V("AC", NAME, PRACTICE), "nw")
save("ucgen-kurali", 830, p.h + 48, [p],
     "Üçgen kuralı: <em>A</em>'dan <em>B</em>'ye, oradan <em>C</em>'ye gitmek, doğrudan <em>A</em>'dan "
     "<em>C</em>'ye gitmekle aynı yer değiştirmedir.",
     "ders-grafik", "Triangle rule: arrows AB and BC tip to tail and the red arrow AC")


# ===========================================================================
# 10. paralelkenar-kurali
# ===========================================================================
PA, PB, PC, PD = (0.0, 0.0), (4.0, 0.0), (5.5, 2.5), (1.5, 2.5)


def parallelogram(p, size=NAME, dot_r=DOT_R):
    """Parallelogram ABCD with the arrows u = AB, v = AD and dashed BC, DC; corner and u, v labels."""
    dline(p, PB, PC)
    dline(p, PD, PC)
    varrow(p, PA, PB, TEXT, THICK, HEAD, dot_r, dot_r + 1)
    varrow(p, PA, PD, TEXT, THICK, HEAD, dot_r, dot_r + 1)
    for Q in (PA, PB, PC, PD):
        dot(p, Q, TEXT, dot_r)
    at_point(p, PA, L("A", size), "sw", 5.0, dot_r)
    at_point(p, PB, L("B", size), "se", 5.0, dot_r)
    at_point(p, PC, L("C", size), "ne", 5.0, dot_r)
    at_point(p, PD, L("D", size), "nw", 5.0, dot_r)
    at_segment(p, PA, PB, L("u", size), "s")
    at_segment(p, PA, PD, L("v", size), "w")


p = cplane(30, 24, 625, (-0.8, 6.5), (-0.8, 3.3))
varrow(p, PA, PC, PRACTICE, THICK, HEAD, DOT_R, DOT_R + 1)
parallelogram(p)
at_segment(p, PA, PC, L("u + v", NAME, PRACTICE), "nw", t=0.58)
save("paralelkenar-kurali", 685, p.h + 48, [p],
     "Paralelkenar kuralı: <em>u</em> ve <em>v</em> ortak <em>A</em> noktasından çizilince toplamları, "
     "üzerlerine kurulan paralelkenarın <em>AC</em> köşegenidir.",
     "ders-grafik", "Parallelogram ABCD with u = AB, v = AD and the red diagonal AC = u + v")


# ===========================================================================
# 11. skalerle-carpim: u, 2u, -u, -3/2 u on parallel lines
# ===========================================================================
p = cplane(30, 24, 520, (-4.0, 5.0), (-4.0, 6.0))
p.grid(range(-4, 6), range(-4, 7))
box = (-4.0, 5.0, -4.0, 6.0)
rows = [((0.0, 4.0), (2.0, 5.0), TEXT, L("u"), "n"),
        ((0.0, 2.0), (4.0, 4.0), THEORY, L("2u", NAME, THEORY), "n"),
        ((0.0, 0.0), (-2.0, -1.0), PRACTICE, L(MINUS_S + "u", NAME, PRACTICE), "n"),
        ((0.0, -2.0), (-3.0, -3.5), PRACTICE,
         Lab(NAME, PRACTICE).t(MINUS_S, False).f("3", "2").t("u"), "s")]
for a, b, col, lab, hint in rows:
    seg = clip_seg((-4.0, a[1] - 2.0), (5.0, a[1] + 2.5), box)
    dline(p, *seg, opacity=0.5)
for a, b, col, lab, hint in rows:
    varrow(p, a, b, col, THICK, HEAD, gap0=DOT_R)
    dot(p, a)
    at_segment(p, a, b, lab, hint)
save("skalerle-carpim", 580, p.h + 48, [p],
     "<em>u</em> = (2, 1) ve katları kendi paralel doğruları üzerinde: pozitif katlar <em>u</em> ile "
     "aynı yönü (sağı), negatif katlar ters yönü (solu) gösterir.",
     "ders-grafik", "Arrows u, 2u, -u and -3/2 u on four parallel dashed lines of slope 1/2, all starting on one vertical")


# ===========================================================================
# 12. ters-vektor-ve-fark
# ===========================================================================
p = cplane(30, 24, 775, (0.3, 9.8), (-2.0, 2.6))
divider(p, 5.0, -1.8, 2.4)
varrow(p, (1.0, 0.0), (4.0, 0.0), TEXT)
varrow(p, (4.0, -1.2), (1.0, -1.2), THEORY)
at_segment(p, (1.0, 0.0), (4.0, 0.0), L("u"), "s")
at_segment(p, (4.0, -1.2), (1.0, -1.2), L(MINUS_S + "u", NAME, THEORY), "s")
O2, U2, V2 = (6.0, 0.0), (9.0, 0.0), (8.0, 2.0)
varrow(p, O2, U2, TEXT, THICK, HEAD, DOT_R)
varrow(p, O2, V2, TEXT, THICK, HEAD, DOT_R)
varrow(p, V2, U2, PRACTICE, THICK, HEAD, 2.0)
dot(p, O2)
at_segment(p, O2, U2, L("u"), "s")
at_segment(p, O2, V2, L("v"), "nw")
at_segment(p, V2, U2, L("u " + MINUS_S + " v", NAME, PRACTICE), "e")
save("ters-vektor-ve-fark", 835, p.h + 48, [p],
     "Solda <em>u</em> ile ters vektörü &#8722;<em>u</em>: aynı uzunlukta, zıt yönlü. Sağda <em>u</em> ve "
     "<em>v</em> aynı noktadan çizilince <em>u</em> &#8722; <em>v</em>, <em>v</em>'nin ucundan "
     "<em>u</em>'nun ucuna giden oktur.",
     WIDE, "Left: u and its opposite -u. Right: u and v from one point and the red arrow u - v from the tip of v to the tip of u")


# ===========================================================================
# 13. kosegen-vektorleri: the four diagonal vectors, 2 x 2 panels
# ===========================================================================
PW, GAPX, TOP, ROWGAP = 330, 44, 40, 14
panels = []
specs = [("(a)", "u + v", PA, PC, "nw"),
         ("(b)", MINUS_S + "(u + v)", PC, PA, "nw"),
         ("(c)", "u " + MINUS_S + " v", PD, PB, "ne"),
         ("(d)", "v " + MINUS_S + " u", PB, PD, "ne")]
for k, (tag, expr, a, b, hint) in enumerate(specs):
    col, row = k % 2, k // 2
    x0 = 20 + col * (PW + GAPX)
    q = cplane(x0, 0, PW, (-0.9, 6.4), (-0.75, 3.25))
    q.y0 = TOP + row * (q.h + TOP + ROWGAP)
    varrow(q, a, b, PRACTICE, THICK, 11.0, DOT_R + 1, DOT_R + 1)
    parallelogram(q, NOTE)
    at_segment(q, a, b, L(expr, NOTE, PRACTICE), hint, t=0.5 if hint == "ne" else 0.56)
    title_px(q, q.x0 + PW / 2, q.y0 - 22, Lab(NOTE).t(tag, False).g(8).t(expr))
    panels.append(q)
Hk = panels[-1].y0 + panels[-1].h + 30
save("kosegen-vektorleri", 2 * PW + GAPX + 40, Hk, panels,
     "<em>u</em> ve <em>v</em> üzerine kurulan paralelkenarın köşegen vektörleri: "
     "(a) <em>AC</em> = <em>u</em> + <em>v</em>, (b) <em>CA</em> = &#8722;(<em>u</em> + <em>v</em>), "
     "(c) <em>DB</em> = <em>u</em> &#8722; <em>v</em>, (d) <em>BD</em> = <em>v</em> &#8722; <em>u</em>.",
     WIDE, "Four copies of the parallelogram ABCD, each with one red diagonal: u + v, -(u + v), u - v, v - u")


# ===========================================================================
# 14. paralel-vektorler
# ===========================================================================
p = cplane(30, 24, 545, (-1.3, 8.3), (-4.0, 4.7))
for a in ((0.0, 0.0), (1.0, 2.0), (7.0, -1.0)):
    y = lambda x, a=a: a[1] + (x - a[0]) / 3.0
    dline(p, (-1.0, y(-1.0)), (8.0, y(8.0)), opacity=0.5)
arrows = [((0.0, 0.0), (3.0, 1.0), TEXT, L("u"), "s"),
          ((1.0, 2.0), (7.0, 4.0), THEORY, L("v = 2u", NAME, THEORY), "n"),
          ((7.0, -1.0), (4.0, -2.0), PRACTICE, L("w = " + MINUS_S + "u", NAME, PRACTICE), "s")]
for a, b, col, lab, hint in arrows:
    varrow(p, a, b, col, THICK, HEAD, gap0=DOT_R)
    dot(p, a)
    at_segment(p, a, b, lab, hint)
save("paralel-vektorler", 605, p.h + 48, [p],
     "<em>u</em>, <em>v</em> = 2<em>u</em> ve <em>w</em> = &#8722;<em>u</em> paralel doğrular üzerindedir; "
     "<em>v</em> ile <em>u</em> aynı yönlü, <em>w</em> ile <em>u</em> zıt yönlüdür.",
     "ders-grafik", "Three parallel dashed lines of slope 1/3 carrying u, v = 2u and w = -u")


# ===========================================================================
# 15. birim-vektor
# ===========================================================================
p = cplane(36, 24, 520, (-1.5, 5.0), (-1.5, 4.0))


def axes2(p, xr, yr, xt, yt, names=("x", "y")):
    """Axes through the origin with arrowheads, tick marks, numbers and names."""
    ox, oy = p.X(0), p.Y(0)
    arrow_px(p, p.X(xr[0]), oy, p.X(xr[1]), oy, TEXT, 1.2, 8.0, None, 0.6)
    arrow_px(p, ox, p.Y(yr[0]), ox, p.Y(yr[1]), TEXT, 1.2, 8.0, None, 0.6)
    for t in xt:
        t, pos = t if isinstance(t, tuple) else (t, "s")
        p.add(f'<line x1="{p.X(t):.1f}" y1="{oy - 3.5:.1f}" x2="{p.X(t):.1f}" y2="{oy + 3.5:.1f}" '
              f'stroke="{TEXT}" stroke-width="1.1" opacity="0.7"/>')
        at_point(p, (t, 0), L(tick_num(t), TICK, TEXT, False), pos, 3.0, 3.5)
    for t in yt:
        t, pos = t if isinstance(t, tuple) else (t, "w")
        p.add(f'<line x1="{ox - 3.5:.1f}" y1="{p.Y(t):.1f}" x2="{ox + 3.5:.1f}" y2="{p.Y(t):.1f}" '
              f'stroke="{TEXT}" stroke-width="1.1" opacity="0.7"/>')
        at_point(p, (0, t), L(tick_num(t), TICK, TEXT, False), pos, 3.0, 3.5)
    at_point(p, (xr[1], 0), L(names[0], NOTE), "e", 5.0, 0.0)
    at_point(p, (0, yr[1]), L(names[1], NOTE), "n", 5.0, 0.0)


# the numbers at +-1 sit diagonally outside the unit circle, not on it
axes2(p, (-1.5, 5.0), (-1.5, 4.0), ((-1, (-1.0, 1.6)), (1, (1.0, 1.6)), 2, 3, 4),
      ((-1, (-1.6, 1.0)), (1, (-1.6, -1.0)), 2, 3))
p.circle(0, 0, 1.0, TEXT, 1.3, "5 4", "none", 0.6)
varrow(p, (0, 0), (4.0, 3.0), TEXT, THIN, THIN_HEAD, gap0=DOT_R)
varrow(p, (0, 0), (0.8, 0.6), PRACTICE, 3.6, 13.0, gap0=DOT_R)
dot(p, (0, 0))
at_point(p, (0, 0), L("O"), "sw")
at_point(p, (4.0, 3.0), L("u"), "ne", 4.0, 3.0)
at_data(p, (0.40, 1.42), Lab(NAME, PRACTICE).f("u", DBAR + "u" + DBAR, NAME))
save("birim-vektor", 580, p.h + 48, [p],
     "<em>u</em> = (4, 3) ve aynı ışın üzerindeki birim vektör <em>u</em>/&#8214;<em>u</em>&#8214; = (0,8; 0,6); "
     "birim vektörün ucu birim çemberin üzerindedir.",
     "ders-grafik", "Vector u from O to (4,3) and the thick red unit vector u over its norm ending on the dashed unit circle")


# ===========================================================================
# 16. standart-birim-vektorler (3-D)
# ===========================================================================
# A low, shallow view: with the usual 22 degrees the far corner (3, 4, 0) drops so far
# that u looks level with O and runs along e2.
cam = Camera(azimuth=18, elevation=15)
U = (3.0, 4.0, 2.0)
AXE = (4.6, 5.6, 3.6)
p, S = space_fit(cam, [(AXE[0], 0, 0), (0, AXE[1], 0), (0, 0, AXE[2]), U], 706, pad=0.4)
axes3(S, AXE)
# the box with corners O and U, minus the three edges of the red path
x_, y_, z_ = U
corners = {(i, j, k): (i * x_, j * y_, k * z_) for i in (0, 1) for j in (0, 1) for k in (0, 1)}
path = {((0, 0, 0), (1, 0, 0)), ((1, 0, 0), (1, 1, 0)), ((1, 1, 0), (1, 1, 1))}
for a in corners:
    for b in corners:
        if a < b and sum(abs(a[i] - b[i]) for i in range(3)) == 1 and (a, b) not in path:
            S.line([corners[a], corners[b]], TEXT, 1.0, "4 4", 0.45)
O = (0.0, 0.0, 0.0)
X3, XY3 = (3.0, 0.0, 0.0), (3.0, 4.0, 0.0)
arrow3(S, O, X3, PRACTICE, THICK, HEAD)
arrow3(S, X3, XY3, PRACTICE, THICK, HEAD)
arrow3(S, XY3, U, PRACTICE, THICK, HEAD, gap1=3.0)
arrow3(S, O, U, TEXT, THICK, HEAD, gap0=DOT_R, gap1=3.0)
for e in (ex, ey, ez):
    arrow3(S, O, e, THEORY, 3.2, 11.5, gap0=DOT_R)
S.point(O, TEXT, DOT_R)
S.point(U, TEXT, 3.4)
pt3(S, O, L("O"), (0.3, 1.0), 6.0)
pt3(S, ex, Lab(NAME, THEORY).t("e" + sub("1")), "n", 7.0, 3.0)
pt3(S, ey, Lab(NAME, THEORY).t("e" + sub("2")), "s", 7.0, 3.0)
pt3(S, ez, Lab(NAME, THEORY).t("e" + sub("3")), "w", 7.0, 3.0)
pt3(S, U, Lab(NAME).t("u = (u" + sub("1") + ", u" + sub("2") + ", u" + sub("3") + ")"), (1.0, 0.3))
seg3(S, O, X3, Lab(NAME, PRACTICE).t("u" + sub("1") + "e" + sub("1")), "s", t=0.5)
seg3(S, X3, XY3, Lab(NAME, PRACTICE).t("u" + sub("2") + "e" + sub("2")), "s")
seg3(S, XY3, U, Lab(NAME, PRACTICE).t("u" + sub("3") + "e" + sub("3")), "e")
save("standart-birim-vektorler", 700, p.h + 48, [p],
     "<em>u</em> = (<em>u</em><sub>1</sub>, <em>u</em><sub>2</sub>, <em>u</em><sub>3</sub>), eksenler boyunca "
     "uç uca eklenen <em>u</em><sub>1</sub><em>e</em><sub>1</sub>, <em>u</em><sub>2</sub><em>e</em><sub>2</sub> "
     "ve <em>u</em><sub>3</sub><em>e</em><sub>3</sub> oklarının toplamıdır.",
     WIDE, "Standard unit vectors e1, e2, e3 and the vector u reached by the red path u1 e1, u2 e2, u3 e3 along a box")


# ===========================================================================
# 17. duzlemdes-vektorler (3-D): u, v in one plane, w in a parallel plane
# ===========================================================================
# A low view keeps the two plane pieces apart on the page; the axes are a small
# detached tripod, only for orientation.
cam = Camera(azimuth=30, elevation=15)
Z2 = 3.0
TRI = (6.0, -2.6, 0.0)          # where the orientation tripod stands
p, S = space_fit(cam, [(0, 0, 0), (6, 0, 0), (0, 5, 0), (6, 5, 0), (0, 0, Z2), (6, 5, Z2), (6, 0, Z2),
                       TRI], 660, pad=0.5)


def tripod(S, T, n=1.3):
    for k, name in enumerate("xyz"):
        e = [0.0, 0.0, 0.0]
        e[k] = n
        tip = vadd(T, tuple(e))
        S.arrow(T, tip, TEXT, 1.1, 7.0, None, 0.5)
        at_point(S.p, S.pt(tip), L(name, NOTE), pdir(S, tuple(e)), 4.0, 0.0)


tripod(S, TRI)
S.parallelogram((0, 0, 0), ex, ey, (0, 6), (0, 5), THEORY, 0.15, THEORY, 1.0)
u0, u1, v1 = (1.0, 1.0, 0.0), (4.0, 1.0, 0.0), (2.0, 3.5, 0.0)
arrow3(S, u0, (3.0, 3.0, 0.0), TEXT, 1.6, 9.5, gap0=DOT_R, dash="5 4", opacity=0.6)
arrow3(S, u0, u1, PRACTICE, THICK, HEAD, gap0=DOT_R)
arrow3(S, u0, v1, BASE, THICK, HEAD, gap0=DOT_R)
S.point(u0, TEXT, 3.6)
seg3(S, u0, u1, L("u", NAME, PRACTICE), "s")
seg3(S, u0, v1, L("v", NAME, BASE), "w", t=0.6)
S.parallelogram((0, 0, Z2), ex, ey, (0, 6), (0, 5), THEORY, 0.08, THEORY, 1.0)
w0, w1 = (3.0, 2.0, Z2), (5.0, 4.0, Z2)
arrow3(S, w0, w1, THEORY, THICK, HEAD, gap0=DOT_R)
S.point(w0, TEXT, 3.6)
seg3(S, w0, w1, L("w", NAME, THEORY), "n")
pt3(S, (6, 0, 0), Lab(NAME, THEORY).t("D" + sub("1")), "w", 6.0, 0.0)
pt3(S, (6, 0, Z2), Lab(NAME, THEORY).t("D" + sub("2")), "w", 6.0, 0.0)
save("duzlemdes-vektorler", 700, p.h + 48, [p],
     "Düzlemdeş vektörler: <em>u</em> ile <em>v</em> alt düzlemde, <em>w</em> ona paralel üst düzlemde "
     "çizilmiştir. <em>w</em>'nun ortak başlangıç noktasından çizilen kopyası (kesikli) da alt düzlemde kalır.",
     WIDE, "Two parallel horizontal planes D1 and D2; u and v lie in D1, w in D2, and a dashed copy of w starts at the common point in D1")


# ===========================================================================
# 18. uc-vektor-ayrisimi (2-D): w = alpha u + beta v
# ===========================================================================
p = cplane(30, 24, 565, (-1.2, 6.0), (-1.3, 4.3))
O, Uu, Vv, W, Q = (0, 0), (2.0, 0.0), (0.5, 1.5), (4.0, 3.0), (3.0, 0.0)
dline(p, (-1.0, 0.0), (5.5, 0.0))
dline(p, (2.7, -0.9), (4.3, 3.9))
varrow(p, O, W, THEORY, THICK, HEAD, DOT_R, DOT_R + 1)
varrow(p, O, Uu, TEXT, THICK, HEAD, DOT_R)
varrow(p, O, Vv, TEXT, THICK, HEAD, DOT_R)
ppu = p.w / (p.xmax - p.xmin)
SH = 11.0
varrow(p, O, Q, PRACTICE, 1.9, 9.5, 0.0, 0.0, shift=(0.0, SH))
varrow(p, Q, W, PRACTICE, 2.2, 10.5, DOT_R + 1, DOT_R + 1)
for Z in (O, W, Q):
    dot(p, Z)
at_point(p, O, L("O"), "sw")
at_point(p, W, L("W"), (1.0, 0.25))
at_point(p, Q, L("Q"), "se")
at_segment(p, O, Uu, L("u"), "n")
at_segment(p, O, Vv, L("v"), "w")
at_segment(p, O, W, L("w", NAME, THEORY), "nw", t=0.55)
at_segment(p, (O[0], O[1] - SH / ppu), (Q[0], Q[1] - SH / ppu), L(ALPHA + "u", NAME, PRACTICE), "s", gap=5.0)
at_segment(p, Q, W, L(BETA + "v", NAME, PRACTICE), "e", t=0.45)
save("uc-vektor-ayrisimi", 625, p.h + 48, [p],
     "<em>W</em>'den <em>v</em>'ye paralel çizilen doğru, <em>u</em> doğrusunu <em>Q</em>'da keser; "
     "böylece <em>w</em> = <em>&#945;u</em> + <em>&#946;v</em> olur.",
     "ders-grafik", "Decomposition in a plane: w from O to W equals alpha u along the u line to Q plus beta v from Q to W")


# ===========================================================================
# 19. uzayda-ayrisim (3-D): x = alpha u + beta v + gamma w
# ===========================================================================
# x to the right, y receding: X then stands well clear of the plane, with its own
# dotted drop to the plane showing its height.
cam = Camera(azimuth=-50, elevation=22)
X3, P3, Q3 = (6.0, 4.5, 3.0), (4.5, 3.0, 0.0), (3.0, 0.0, 0.0)
u3, v3, w3 = (2.0, 0.0, 0.0), (1.0, 2.0, 0.0), (1.0, 1.0, 2.0)
p, S = space_fit(cam, [(-0.5, -0.5, 0), (7, -0.5, 0), (7, 5, 0), (-0.5, 5, 0), X3, (0, 0, 2.4)],
                 715, pad=0.4)
S.parallelogram((0, 0, 0), ex, ey, (-0.5, 7.0), (-0.5, 5.0), THEORY, 0.09, THEORY, 1.0)
axes3(S, (7.6, 5.6, 2.4), names=("x", "y", "z"), opacity=0.35)
O = (0.0, 0.0, 0.0)
S.guide([vsub(P3, vscale(0.35, w3)), X3], TEXT, 0.55, 1.1, "5 4")
S.guide([vsub(Q3, vscale(0.35, v3)), P3], TEXT, 0.55, 1.1, "5 4")
S.drop(X3, 0.0, TEXT, 0.4, 1.0, "2 3", True)
Pp = S.p
dxp, dyp = pdir(S, ex)
SHIFT = (-dyp * 11.0, dxp * 11.0) if dxp > 0 else (dyp * 11.0, -dxp * 11.0)   # 11 px to the lower side
arrow3(S, O, X3, THEORY, THICK, HEAD, DOT_R, DOT_R + 1)
arrow3(S, O, Q3, PRACTICE, 1.9, 9.5, 0.0, 0.0, shift=SHIFT)
arrow3(S, Q3, P3, PRACTICE, 2.2, 10.5, DOT_R + 1, DOT_R + 1)
arrow3(S, P3, X3, PRACTICE, 2.2, 10.5, DOT_R + 1, DOT_R + 1)
arrow3(S, O, u3, TEXT, THICK, HEAD, DOT_R)
arrow3(S, O, v3, TEXT, THICK, HEAD, DOT_R)
arrow3(S, O, w3, TEXT, THICK, HEAD, DOT_R)
for Z in (O, Q3, P3, X3):
    S.point(Z, TEXT, DOT_R)
pt3(S, O, L("O"), (-1.0, 0.3), 7.0)
pt3(S, u3, L("u"), (0.25, -1.0), 9.0, 3.0)
pt3(S, v3, L("v"), "e", 6.0, 3.0)
pt3(S, w3, L("w"), "w", 6.0, 3.0)
pt3(S, X3, L("X"), "ne")
pt3(S, Q3, L("Q"), (-0.3, -1.0), 6.0)
pt3(S, P3, L("P"), "se")
seg3(S, O, X3, L("x", NAME, THEORY), "n", t=0.6)
qa, qb = S.pt(O), S.pt(Q3)
ppu = Pp.w / (Pp.xmax - Pp.xmin)
sa = (qa[0] + SHIFT[0] / ppu, qa[1] - SHIFT[1] / ppu)
sb = (qb[0] + SHIFT[0] / ppu, qb[1] - SHIFT[1] / ppu)
at_segment(Pp, sa, sb, L(ALPHA + "u", NAME, PRACTICE), "s", t=0.5, gap=5.0)
seg3(S, Q3, P3, L(BETA + "v", NAME, PRACTICE), "s")
seg3(S, P3, X3, L(GAMMA + "w", NAME, PRACTICE), "e")
pt3(S, (7.0, 5.0, 0.0), Lab(NAME, THEORY).t("D"), "e", 6.0, 0.0)
save("uzayda-ayrisim", 700, p.h + 48, [p],
     "<em>X</em>'ten <em>w</em>'ya paralel çizilen doğru <em>u</em> ile <em>v</em>'nin düzlemini <em>P</em>'de, "
     "<em>P</em>'den <em>v</em>'ye paralel çizilen doğru <em>u</em> doğrusunu <em>Q</em>'da keser; "
     "böylece <em>x</em> = <em>&#945;u</em> + <em>&#946;v</em> + <em>&#947;w</em> olur.",
     WIDE, "Decomposition in space: x from O to X equals alpha u to Q, beta v to P in the plane, and gamma w up to X")


# ===========================================================================
# 20. birlesme-ozdesligi: two ways to add three arrows
# ===========================================================================
BA_, BB_, BC_, BD_ = (0.0, 0.0), (4.0, 0.0), (5.0, 3.0), (1.0, 4.0)
panels = []
PW2 = 335
for k in range(2):
    q = cplane(20 + k * (PW2 + 50), 44, PW2, (-0.9, 6.2), (-0.8, 4.8))
    if k == 0:
        varrow(q, BA_, BC_, PRACTICE, 2.2, 10.5, DOT_R + 1, DOT_R + 1, dash="6 4")
    else:
        varrow(q, BB_, BD_, PRACTICE, 2.2, 10.5, DOT_R + 1, DOT_R + 1, dash="6 4")
    for a, b in ((BA_, BB_), (BB_, BC_), (BC_, BD_)):
        varrow(q, a, b, TEXT, THIN, THIN_HEAD, DOT_R + 1, DOT_R + 1)
    varrow(q, BA_, BD_, THEORY, 3.0, 12.0, DOT_R + 1, DOT_R + 1)
    for Z in (BA_, BB_, BC_, BD_):
        dot(q, Z)
    at_point(q, BA_, L("A", NOTE), "sw", 5.0)
    at_point(q, BB_, L("B", NOTE), "se", 5.0)
    at_point(q, BC_, L("C", NOTE), "ne", 5.0)
    at_point(q, BD_, L("D", NOTE), "nw", 5.0)
    at_segment(q, BA_, BD_, V("AD", NOTE, THEORY), "w")
    if k == 0:
        at_segment(q, BA_, BC_, V("AC", NOTE, PRACTICE), "se")
        t = Lab(NOTE).t("(", False).v("AB").t(" + ", False).v("BC").t(") + ", False).v("CD")
    else:
        at_segment(q, BB_, BD_, V("BD", NOTE, PRACTICE), "ne")
        t = Lab(NOTE).v("AB").t(" + (", False).v("BC").t(" + ", False).v("CD").t(")", False)
    title_px(q, q.x0 + PW2 / 2, q.y0 - 22, t)
    panels.append(q)
save("birlesme-ozdesligi", 2 * PW2 + 90, panels[0].h + 80, panels,
     "Solda önce <em>AB</em> ile <em>BC</em> birleştirilip <em>AC</em>, sağda önce <em>BC</em> ile "
     "<em>CD</em> birleştirilip <em>BD</em> bulunur; iki yol da <em>A</em>'dan <em>D</em>'ye varır.",
     WIDE, "Two copies of the path A B C D: left with the dashed red arrow AC, right with the dashed red arrow BD; both end with AD")


# ===========================================================================
# 21. agirlik-merkezi
# ===========================================================================
p = cplane(30, 24, 608, (-0.8, 6.9), (-0.8, 5.7))
A, B, C = (0.0, 0.0), (6.0, 0.0), (2.0, 5.0)
M = (4.0, 2.5)
G = (8.0 / 3.0, 5.0 / 3.0)
p.line([A, B, C, A], TEXT, 1.2, None, 0.8)
dline(p, A, M, TEXT, 1.2, "5 4", 0.5)
varrow(p, G, A, PRACTICE, THICK, HEAD, DOT_R + 1, DOT_R + 1)
varrow(p, G, B, THEORY, THICK, HEAD, DOT_R + 1, DOT_R + 1)
varrow(p, G, C, TEXT, THICK, HEAD, DOT_R + 1, DOT_R + 1)
varrow(p, G, M, BASE, THICK, 11.0, DOT_R + 1, DOT_R + 1)
for Z in (A, B, C, M, G):
    dot(p, Z)
at_point(p, A, L("A"), "sw")
at_point(p, B, L("B"), "se")
at_point(p, C, L("C"), "n")
at_point(p, M, L("M"), "ne")
at_point(p, G, L("G"), (-1.0, -0.35), 7.0)
at_segment(p, G, A, V("GA", NAME, PRACTICE), "nw")
at_segment(p, G, B, V("GB", NAME, THEORY), "ne")
at_segment(p, G, C, V("GC"), "w")
at_segment(p, G, M, V("GM", NAME, BASE), "se")
save("agirlik-merkezi", 668, p.h + 48, [p],
     "<em>G</em> ağırlık merkezinden köşelere giden vektörler; <em>M</em>, <em>BC</em>'nin orta noktasıdır ve "
     "<em>GA</em> = &#8722;2 <em>GM</em>, <em>GB</em> + <em>GC</em> = 2 <em>GM</em> olur.",
     "ders-grafik", "Triangle ABC with centroid G, midpoint M of BC, and arrows from G to A, B, C and M")


# ---------------------------------------------------------------------------
for name, content in OUT.items():
    with io.open(OUT_DIR / f"{PREFIX}{name}.md", "w", encoding="utf-8", newline="\n") as fh:
        fh.write(content)
print("generated:", ", ".join(OUT))
