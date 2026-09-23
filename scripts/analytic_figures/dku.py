# -*- coding: utf-8 -*-
"""Figures for the chapter "Dik Koordinatlar ve Uzaklık" of the Analitik Geometri book
(dersler/analitik-geometri/dik-koordinatlar-ve-uzaklik.qmd).

The figures are NOT produced at build time. Run

    python scripts/analytic_figures/dku.py
    python scripts/center_figures.py "analytic-dku-*.md" --keep-width

and paste each scripts/_figures/analytic-dku-<name>.md block into the .qmd.
Figures go INSIDE the box they explain (example, exercise, solution), never
inside a definition box: a figure that illustrates a definition sits directly
below that box.

Labels are placed by a small collision-avoiding placer (Scene): every drawn
segment, circle and point is registered as an obstacle, and each label tries
its preferred positions first, then the remaining directions, and takes the
spot that touches no line, point or other label. Tick numbers are placed last
and are dropped (with a console note) when every spot is taken.

Captions are Turkish (they are shown on the site); aria labels are ASCII.
"""
import html
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, WIDE, TEXT, BG, THEORY, BASE, PRACTICE, REMARK  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
OUT = {}
PREFIX = "analytic-dku-"

MINUS = "−"
SQRT = "√"
ASC, DESC = 0.78, 0.22
CHAR_W = 0.56          # same width model as scripts/check_figure_labels.py

PT, EDGE, NOTE, TICK, AXIS = 13.5, 13, 12.5, 11, 14


# ---------------------------------------------------------------------------
# label markup: $...$ toggles math mode (letters italic, '-' -> minus sign),
# _x / _{..} subscript, ^x / ^{..} superscript.
# ---------------------------------------------------------------------------
def _tokens(s, math_mode):
    toks, i, mm = [], 0, math_mode
    while i < len(s):
        c = s[i]
        if c == "$":
            mm = not mm
            i += 1
            continue
        if c in "_^" and i + 1 < len(s):
            lvl = -1 if c == "_" else 1
            if s[i + 1] == "{":
                j = s.index("}", i + 2)
                body, i = s[i + 2:j], j + 1
            else:
                body, i = s[i + 1], i + 2
            for ch in body:
                toks.append((MINUS if (mm and ch == "-") else ch, mm and ch.isascii() and ch.isalpha(), lvl))
            continue
        toks.append((MINUS if (mm and c == "-") else c, mm and c.isascii() and c.isalpha(), 0))
        i += 1
    return toks


def markup(s, size, math_mode=True):
    """SVG text body and estimated advance width of a label."""
    groups = []
    for t, it, lv in _tokens(s, math_mode):
        if groups and groups[-1][1] == it and groups[-1][2] == lv:
            groups[-1][0] += t
        else:
            groups.append([t, it, lv])
    out, cur, width, has_sub = [], 0.0, 0.0, False
    for t, it, lv in groups:
        fs = size if lv == 0 else round(size * 0.76, 1)
        target = {0: 0.0, -1: round(size * 0.3, 1), 1: -round(size * 0.4, 1)}[lv]
        dy, cur = target - cur, target
        has_sub = has_sub or lv == -1
        attrs = ""
        if it:
            attrs += ' font-style="italic"'
        if lv:
            attrs += f' font-size="{fs:g}"'
        if abs(dy) > 1e-9:
            attrs += f' dy="{dy:g}"'
        esc = html.escape(t, quote=False)
        out.append(f"<tspan{attrs}>{esc}</tspan>" if attrs else esc)
        width += len(t) * CHAR_W * fs
    return "".join(out), width, has_sub


# ---------------------------------------------------------------------------
# geometry helpers (pixel space)
# ---------------------------------------------------------------------------
def seg_hits_box(x1, y1, x2, y2, b):
    """Liang-Barsky: does the segment meet the rectangle b = (x0, y0, x1, y1)?"""
    dx, dy = x2 - x1, y2 - y1
    t0, t1 = 0.0, 1.0
    for p, q in ((-dx, x1 - b[0]), (dx, b[2] - x1), (-dy, y1 - b[1]), (dy, b[3] - y1)):
        if abs(p) < 1e-12:
            if q < 0:
                return False
        else:
            t = q / p
            if p < 0:
                if t > t1:
                    return False
                t0 = max(t0, t)
            else:
                if t < t0:
                    return False
                t1 = min(t1, t)
    return True


def boxes_overlap(a, b):
    return min(a[2], b[2]) > max(a[0], b[0]) and min(a[3], b[3]) > max(a[1], b[1])


def grow(b, d):
    return (b[0] - d, b[1] - d, b[2] + d, b[3] + d)


def circle_hits_box(cx, cy, r, b):
    nx = min(max(cx, b[0]), b[2])
    ny = min(max(cy, b[1]), b[3])
    return (nx - cx) ** 2 + (ny - cy) ** 2 < r * r


DIRS = {"e": (1, 0), "w": (-1, 0), "n": (0, -1), "s": (0, 1),
        "ne": (1, -1), "nw": (-1, -1), "se": (1, 1), "sw": (-1, 1)}
ALL_DIRS = ("e", "ne", "n", "nw", "w", "sw", "s", "se")


def box_at(ax, ay, d, gap, w, size, sub):
    """Label box beside the anchor (ax, ay) in direction d, `gap` pixels away."""
    ux, uy = DIRS[d]
    h = (ASC + DESC) * size + (0.25 * size if sub else 0)
    k = 0.72 if (ux and uy) else 1.0
    if ux > 0:
        x0 = ax + gap * k
    elif ux < 0:
        x0 = ax - gap * k - w
    else:
        x0 = ax - w / 2
    if uy < 0:
        y1 = ay - gap * k
        y0 = y1 - h
    elif uy > 0:
        y0 = ay + gap * k
        y1 = y0 + h
    else:
        y0 = ay - 0.43 * size
        y1 = y0 + h
    return (x0, y0, x0 + w, y1)


# ---------------------------------------------------------------------------
# Scene: an equal-aspect Plot plus obstacle bookkeeping and label placement
# ---------------------------------------------------------------------------
class Scene:
    def __init__(self, xr, yr, ppu, left=90, top=50, right=160, bottom=70):
        w, h = (xr[1] - xr[0]) * ppu, (yr[1] - yr[0]) * ppu
        self.p = Plot(left, top, w, h, xr, yr)
        self.xr, self.yr, self.ppu = xr, yr, ppu
        self.W, self.H = round(left + w + right), round(top + h + bottom)
        self.segs, self.dots, self.boxes, self.soft = [], [], [], []
        self.queue = []
        self.texts = []
        self.name = ""

    # -- mapping ------------------------------------------------------------
    def px(self, P):
        return (self.p.X(P[0]), self.p.Y(P[1]))

    # -- obstacles ----------------------------------------------------------
    def reg_seg(self, A, B, weight=200, data=True):
        a = self.px(A) if data else A
        b = self.px(B) if data else B
        self.segs.append((a[0], a[1], b[0], b[1], weight))

    def reg_poly(self, pts, weight=200, closed=False, data=True):
        seq = list(pts) + ([pts[0]] if closed else [])
        for a, b in zip(seq, seq[1:]):
            self.reg_seg(a, b, weight, data)

    # -- drawing ------------------------------------------------------------
    def seg(self, A, B, color=THEORY, width=2.1, dash=None, opacity=1.0, weight=200):
        self.p.line([A, B], color, width, dash, opacity)
        self.reg_seg(A, B, weight)

    def poly(self, pts, color=THEORY, width=2.1, dash=None, opacity=1.0, closed=True, weight=200):
        seq = list(pts) + ([pts[0]] if closed else [])
        self.p.line(seq, color, width, dash, opacity)
        self.reg_poly(pts, weight, closed)

    def fill(self, pts, color=THEORY, opacity=0.08):
        self.p.polygon(pts, color, opacity)

    def circle(self, C, r, color=REMARK, width=1.4, dash="6 4", opacity=0.75, weight=90):
        self.p.circle(C[0], C[1], r, color, width, dash, "none", opacity)
        pts = [(C[0] + r * math.cos(2 * math.pi * k / 96), C[1] + r * math.sin(2 * math.pi * k / 96))
               for k in range(96)]
        self.reg_poly(pts, weight, closed=True)

    def arrow(self, A, B, color=THEORY, width=2.0, head=9.0, dash=None, opacity=1.0, weight=200):
        self.p.arrow(A, B, color, width, head, dash, opacity)
        self.reg_seg(A, B, weight)

    def arc_arrow(self, C, r, a0, a1, color=THEORY, width=2.0, head=9.0, opacity=1.0, weight=200):
        """Circular arc from angle a0 to a1 (radians) with an arrowhead at a1."""
        n = max(24, int(abs(a1 - a0) * 30))
        pts = [(C[0] + r * math.cos(a0 + (a1 - a0) * k / n), C[1] + r * math.sin(a0 + (a1 - a0) * k / n))
               for k in range(n + 1)]
        # stop the shaft a little before the tip so it does not poke through the head
        self.p.line(pts[:-2], color, width, None, opacity)
        self.p.arrow(pts[-4], pts[-1], color, width, head, None, opacity)
        self.reg_poly(pts, weight)

    def dot(self, P, color=TEXT, r=3.8):
        self.p.points([P], color, r)
        X, Y = self.px(P)
        self.dots.append((X, Y, r))

    def ring(self, P, color=PRACTICE, r=4.6, width=1.9):
        X, Y = self.px(P)
        self.p.add(f'<circle cx="{X:.1f}" cy="{Y:.1f}" r="{r}" fill="{BG}" stroke="{color}" stroke-width="{width}"/>')
        self.dots.append((X, Y, r))

    def right_angle(self, V, U, W, size=11, color=TEXT, width=1.2, opacity=0.8):
        """Small square at vertex V between the rays V->U and V->W."""
        vx, vy = self.px(V)
        def unit(P):
            x, y = self.px(P)
            n = math.hypot(x - vx, y - vy)
            return ((x - vx) / n, (y - vy) / n)
        a, b = unit(U), unit(W)
        p1 = (vx + a[0] * size, vy + a[1] * size)
        p2 = (vx + (a[0] + b[0]) * size, vy + (a[1] + b[1]) * size)
        p3 = (vx + b[0] * size, vy + b[1] * size)
        self.p.add(f'<path d="M{p1[0]:.1f},{p1[1]:.1f} L{p2[0]:.1f},{p2[1]:.1f} L{p3[0]:.1f},{p3[1]:.1f}" '
                   f'fill="none" stroke="{color}" stroke-width="{width}" opacity="{opacity}"/>')
        self.reg_poly([p1, p2, p3], 60, data=False)

    def eq_tick(self, A, B, n=1, color=THEORY, length=11, width=1.8, t=0.5):
        """Equal-length hatch(es) across the segment AB."""
        ax, ay = self.px(A)
        bx, by = self.px(B)
        L = math.hypot(bx - ax, by - ay)
        ux, uy = (bx - ax) / L, (by - ay) / L
        nx, ny = -uy, ux
        mx, my = ax + (bx - ax) * t, ay + (by - ay) * t
        for k in range(n):
            off = (k - (n - 1) / 2) * 5
            cx, cy = mx + ux * off, my + uy * off
            p1 = (cx - nx * length / 2, cy - ny * length / 2)
            p2 = (cx + nx * length / 2, cy + ny * length / 2)
            self.p.add(f'<line x1="{p1[0]:.1f}" y1="{p1[1]:.1f}" x2="{p2[0]:.1f}" y2="{p2[1]:.1f}" '
                       f'stroke="{color}" stroke-width="{width}" stroke-linecap="round"/>')
            self.reg_seg(p1, p2, 80, data=False)

    def par_mark(self, A, B, n=1, color=THEORY, size=6.5, width=1.8, t=0.5):
        """Parallel-side chevron(s) pointing from A toward B."""
        ax, ay = self.px(A)
        bx, by = self.px(B)
        L = math.hypot(bx - ax, by - ay)
        ux, uy = (bx - ax) / L, (by - ay) / L
        nx, ny = -uy, ux
        mx, my = ax + (bx - ax) * t, ay + (by - ay) * t
        for k in range(n):
            off = (k - (n - 1) / 2) * 6 + size / 2
            tx, ty = mx + ux * off, my + uy * off
            p1 = (tx - ux * size + nx * size * 0.75, ty - uy * size + ny * size * 0.75)
            p2 = (tx - ux * size - nx * size * 0.75, ty - uy * size - ny * size * 0.75)
            self.p.add(f'<path d="M{p1[0]:.1f},{p1[1]:.1f} L{tx:.1f},{ty:.1f} L{p2[0]:.1f},{p2[1]:.1f}" '
                       f'fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round" '
                       f'stroke-linejoin="round"/>')
            self.reg_poly([p1, (tx, ty), p2], 80, data=False)

    # -- axes ---------------------------------------------------------------
    def axes(self, xnums=(), ynums=(), xticks=None, yticks=None, names=("X", "Y"),
             origin=True, origin_square=False, xnum_side="below", xaxis=None, yaxis=None):
        """Coordinate axes crossing at O with arrowheads at the positive ends."""
        xa = xaxis or self.xr
        ya = yaxis or self.yr
        col, op = TEXT, 0.7
        self.arrow((xa[0], 0), (xa[1], 0), col, 1.25, 9.0, None, op, weight=150)
        self.arrow((0, ya[0]), (0, ya[1]), col, 1.25, 9.0, None, op, weight=150)
        X1, Y0 = self.px((xa[1], 0))
        X0, Y1 = self.px((0, ya[1]))
        if names[0]:
            self.fixed_px(X1 + 7, Y0 + 5, names[0], AXIS, TEXT, math_mode=True)
        if names[1]:
            self.fixed_px(X0 - 4, Y1 - 9, names[1], AXIS, TEXT, math_mode=True)
        if xticks is None:
            xticks = [k for k in range(math.ceil(xa[0]), math.floor(xa[1]) + 1)
                      if k != 0 and xa[1] - k > 0.3]
        if yticks is None:
            yticks = [k for k in range(math.ceil(ya[0]), math.floor(ya[1]) + 1)
                      if k != 0 and ya[1] - k > 0.3]
        for t in xticks:
            X, Y = self.px((t, 0))
            self.p.add(f'<line x1="{X:.1f}" y1="{Y - 3.5:.1f}" x2="{X:.1f}" y2="{Y + 3.5:.1f}" '
                       f'stroke="{TEXT}" stroke-width="1.1" opacity="0.7"/>')
            self.reg_seg((X, Y - 3.5), (X, Y + 3.5), 25, data=False)
        for t in yticks:
            X, Y = self.px((0, t))
            self.p.add(f'<line x1="{X - 3.5:.1f}" y1="{Y:.1f}" x2="{X + 3.5:.1f}" y2="{Y:.1f}" '
                       f'stroke="{TEXT}" stroke-width="1.1" opacity="0.7"/>')
            self.reg_seg((X - 3.5, Y), (X + 3.5, Y), 25, data=False)
        # no number next to an arrowhead
        for t in xnums:
            if xa[1] - t > 0.3:
                self.tick_label((t, 0), num(t), "x", xnum_side)
        for t in ynums:
            if ya[1] - t > 0.3:
                self.tick_label((0, t), num(t), "y", "left")
        if origin_square:
            self.right_angle((0, 0), (1, 0), (0, 1), 10, TEXT, 1.1, 0.7)
        if origin:
            self.label((0, 0), "O", ("sw", "nw", "se"), PT, TEXT, gap=5)

    # -- labels ---------------------------------------------------------------
    def _text(self, x, base, body, size, color, halo=True, opacity=1.0):
        h = (f' stroke="{BG}" stroke-width="3.4" stroke-linejoin="round" paint-order="stroke"'
             if halo else "")
        o = f' opacity="{opacity}"' if opacity != 1.0 else ""
        # xml:space="preserve": renderers otherwise drop a space at the end of a <tspan>
        self.texts.append(f'<text x="{x:.1f}" y="{base:.1f}" fill="{color}" font-size="{size:g}"'
                          f'{h}{o} xml:space="preserve">{body}</text>')

    def fixed_px(self, x, base, s, size=NOTE, color=TEXT, math_mode=False, anchor="start",
                 halo=True, opacity=1.0, register=True):
        body, w, sub = markup(s, size, math_mode)
        x0 = x - w / 2 if anchor == "middle" else x - w if anchor == "end" else x
        self._text(x0, base, body, size, color, halo, opacity)
        if register:
            self.boxes.append((x0, base - ASC * size, x0 + w, base + DESC * size))

    def fixed(self, P, s, size=NOTE, color=TEXT, math_mode=False, anchor="middle", dy=0,
              halo=True, opacity=1.0):
        X, Y = self.px(P)
        self.fixed_px(X, Y + dy, s, size, color, math_mode, anchor, halo, opacity)

    def label(self, P, s, dirs=("ne",), size=PT, color=TEXT, gap=7, math_mode=True,
              halo=True, strict=False):
        """Queue a label beside the data point P; dirs are tried first, in order."""
        self.queue.append(("pt", P, s, tuple(dirs), size, color, gap, math_mode, halo, strict))

    def edge_label(self, A, B, s, away=None, toward=None, size=EDGE, color=TEXT,
                   ts=(0.5, 0.42, 0.58, 0.34, 0.66), gaps=(6, 10, 15), math_mode=True, both=False):
        """Queue a label beside the segment AB, on the side away from `away`
        (or toward `toward`); a data point either way."""
        self.queue.append(("edge", A, B, s, away, toward, size, color, ts, gaps, math_mode, both))

    def spot_label(self, spots, s, size=NOTE, color=TEXT, math_mode=False, halo=True, opacity=1.0):
        """Queue a label that may sit centred on any of the listed data points."""
        self.queue.append(("spot", spots, s, size, color, math_mode, halo, opacity))

    def tick_label(self, P, s, axis, side):
        """A tick number: placed after every other label and dropped if no spot is free."""
        X, Y = self.px(P)
        body, w, _ = markup(s, TICK, True)
        if axis == "x":
            if side == "below":
                b = (X - w / 2, Y + 6, X + w / 2, Y + 6 + (ASC + DESC) * TICK)
            else:
                b = (X - w / 2, Y - 6 - (ASC + DESC) * TICK, X + w / 2, Y - 6)
        else:
            b = (X - 7 - w, Y - 0.43 * TICK, X - 7, Y - 0.43 * TICK + (ASC + DESC) * TICK)
        self.soft.append((b, 40, id(b)))
        self.queue.append(("tick", P, s, axis, side, b))

    # -- placement ------------------------------------------------------------
    def score(self, box, rank, own=None):
        s = rank * 2.0
        g = grow(box, 2.5)
        for b in self.boxes:
            if boxes_overlap(g, b):
                s += 1000
        for cx, cy, r in self.dots:
            if circle_hits_box(cx, cy, r + 2.0, box):
                s += 800
        for x1, y1, x2, y2, wt in self.segs:
            if seg_hits_box(x1, y1, x2, y2, g):
                s += wt
        for b, wt, key in self.soft:
            if key != own and boxes_overlap(box, b):
                s += wt
        return s

    def pick(self, cands, own=None):
        best = None
        for rank, c in enumerate(cands):
            sc = self.score(c, rank, own)
            if best is None or sc < best[0]:
                best = (sc, c)
        return best

    def resolve(self):
        items = [q for q in self.queue if q[0] != "tick"] + [q for q in self.queue if q[0] == "tick"]
        for q in items:
            kind = q[0]
            if kind == "pt":
                _, P, s, dirs, size, color, gap, mm, halo, strict = q
                body, w, sub = markup(s, size, mm)
                X, Y = self.px(P)
                order = list(dirs) + ([] if strict else [d for d in ALL_DIRS if d not in dirs])
                cands = []
                for gp in (gap, gap + 5, gap + 11, gap + 18):
                    for d in dirs:
                        cands.append(box_at(X, Y, d, gp, w, size, sub))
                for d in order[len(dirs):]:
                    for gp in (gap, gap + 5):
                        cands.append(box_at(X, Y, d, gp, w, size, sub))
                sc, b = self.pick(cands)
                self.commit(b, body, size, color, halo, sc, s)
            elif kind == "edge":
                _, A, B, s, away, toward, size, color, ts, gaps, mm, both = q
                body, w, sub = markup(s, size, mm)
                h = (ASC + DESC) * size + (0.25 * size if sub else 0)
                ax, ay = self.px(A)
                bx, by = self.px(B)
                L = math.hypot(bx - ax, by - ay)
                nx, ny = -(by - ay) / L, (bx - ax) / L
                ref = away if away is not None else toward
                sides = [1.0]
                if ref is not None:
                    rx, ry = self.px(ref)
                    mx, my = (ax + bx) / 2, (ay + by) / 2
                    dot_ = (rx - mx) * nx + (ry - my) * ny
                    sgn = 1.0 if dot_ > 0 else -1.0
                    sides = [sgn if toward is not None else -sgn]
                if both:
                    sides.append(-sides[0])
                cands = []
                for sd in sides:
                    ex = abs(nx) * w / 2 + abs(ny) * h / 2
                    for gp in gaps:
                        for t in ts:
                            mx, my = ax + (bx - ax) * t, ay + (by - ay) * t
                            cx, cy = mx + sd * nx * (gp + ex), my + sd * ny * (gp + ex)
                            cands.append((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2))
                sc, b = self.pick(cands)
                self.commit(b, body, size, color, True, sc, s)
            elif kind == "spot":
                _, spots, s, size, color, mm, halo, opacity = q
                body, w, sub = markup(s, size, mm)
                cands = []
                for P in spots:
                    X, Y = self.px(P)
                    cands.append((X - w / 2, Y - 0.43 * size, X + w / 2, Y + 0.57 * size))
                sc, b = self.pick(cands)
                self.commit(b, body, size, color, halo, sc, s, opacity)
            else:
                _, P, s, axis, side, b0 = q
                body, w, _ = markup(s, TICK, True)
                x0, y0, x1, y1 = b0
                if axis == "x":
                    cands = [b0]
                    for sh in (w / 2 + 6, w / 2 + 9):
                        cands += [(x0 - sh, y0, x1 - sh, y1), (x0 + sh, y0, x1 + sh, y1)]
                else:
                    hh = y1 - y0
                    cands = [b0]
                    for sh in (hh / 2 + 4, hh / 2 + 7):
                        cands += [(x0, y0 - sh, x1, y1 - sh), (x0, y0 + sh, x1, y1 + sh)]
                sc, b = self.pick(cands, own=id(b0))
                if sc >= 100:
                    print(f"  [{self.name}] tick label {s} dropped (score {sc:.0f})")
                    continue
                self.commit(b, body, TICK, TEXT, True, 0, s, 0.8)

    def commit(self, b, body, size, color, halo, sc, s, opacity=1.0):
        if sc >= 100:
            print(f"  [{self.name}] label '{s}' collides (score {sc:.0f})")
        base = b[1] + ASC * size
        self._text(b[0], base, body, size, color, halo, opacity)
        self.boxes.append(b)

    def emit(self, name, caption, aria, css="ders-grafik"):
        self.name = name
        self.resolve()
        for t in self.texts:
            self.p.add(t)
        OUT[name] = figure(self.W, self.H, [self.p], caption, css, aria)


def num(t):
    s = f"{t:g}"
    return s.replace("-", MINUS)


def evens(a, b):
    return [k for k in range(math.ceil(a), math.floor(b) + 1) if k % 2 == 0 and k != 0]


def ints(a, b):
    return [k for k in range(math.ceil(a), math.floor(b) + 1) if k != 0]


def plane(xr, yr, ppu, xnums=(), ynums=(), origin=True, origin_square=False, xnum_side="below",
          xticks=None, yticks=None, xaxis=None, yaxis=None, **kw):
    sc = Scene(xr, yr, ppu, **kw)
    sc.axes(xnums=xnums, ynums=ynums, origin=origin, origin_square=origin_square, xnum_side=xnum_side,
            xticks=xticks, yticks=yticks, xaxis=xaxis, yaxis=yaxis)
    return sc


def centroid(*pts):
    return (sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts))


def S(n):
    return SQRT + str(n)


def triangle(sc, A, B, C, color=THEORY, width=2.1, fill=True):
    if fill:
        sc.fill([A, B, C], color, 0.07)
    sc.poly([A, B, C], color, width)


# ============================================================ sayi-dogrusu
sc = Scene((-3.8, 3.8), (-0.8, 1.0), 84, left=60, right=60)
sc.arrow((-3.8, 0), (3.8, 0), TEXT, 1.5, 10.0, None, 0.85, weight=150)
for k in range(-3, 4):
    X, Y = sc.px((k, 0))
    sc.p.add(f'<line x1="{X:.1f}" y1="{Y - 6:.1f}" x2="{X:.1f}" y2="{Y + 6:.1f}" stroke="{TEXT}" '
             f'stroke-width="1.3" opacity="0.85"/>')
    sc.reg_seg((X, Y - 6), (X, Y + 6), 25, data=False)
    sc.fixed((k, 0), num(k), 13, TEXT, True, "middle", dy=24)
X0, Y0 = sc.px((-3.72, 0))
sc.fixed_px(X0, Y0 + 24, "…", 13, TEXT, anchor="middle")
X0, Y0 = sc.px((3.62, 0))
sc.fixed_px(X0, Y0 + 24, "…", 13, TEXT, anchor="middle")
sc.seg((0, 0), (1, 0), PRACTICE, 4.6)
sc.label((0.5, 0), "birim", ("n",), NOTE, PRACTICE, gap=9, math_mode=False, strict=True)
sc.dot((2.5, 0), THEORY, 4.8)
sc.label((2.5, 0), "X", ("n",), 14, THEORY, gap=9, strict=True)
sc.arrow((0.35, 0.62), (3.35, 0.62), BASE, 1.6, 9.0)
sc.label((1.85, 0.62), "pozitif yön", ("n",), NOTE, BASE, gap=6, math_mode=False, strict=True)
sc.arrow((-0.35, 0.62), (-3.35, 0.62), REMARK, 1.6, 9.0)
sc.label((-1.85, 0.62), "negatif yön", ("n",), NOTE, REMARK, gap=6, math_mode=False, strict=True)
sc.emit("sayi-dogrusu",
        "Sayı doğrusu: 0 başlangıcı, 1 ise hem birimi hem de pozitif yönü belirler. "
        "0'ın 2,5 birim sağındaki <em>X</em> noktasının sayısı 2,5'tir.",
        "Number line with ticks from -3 to 3, the unit segment from 0 to 1, a point X at 2.5 "
        "and arrows showing the positive and negative directions", WIDE)

# ============================================================ dik-koordinat-sistemi
sc = plane((-1.8, 5.0), (-1.8, 4.0), 72, xnums=(-1, 1), ynums=(-1, 1), origin_square=True,
           xticks=(-1, 1, 3.5), yticks=(-1, 1, 2.5))
P = (3.5, 2.5)
sc.seg(P, (3.5, 0), TEXT, 1.2, "5 4", 0.7, weight=120)
sc.seg(P, (0, 2.5), TEXT, 1.2, "5 4", 0.7, weight=120)
sc.dot(P, PRACTICE, 4.6)
sc.label(P, "P(x, y)", ("ne",), 14, PRACTICE)
sc.label((3.5, 0), "x", ("s",), 14, TEXT, gap=7, strict=True)
sc.label((0, 2.5), "y", ("w",), 14, TEXT, gap=9, strict=True)
sc.emit("dik-koordinat-sistemi",
        "Dik koordinat düzlemi. <em>P</em>'den eksenlere inilen dikmeler <em>X</em>-eksenini "
        "<em>x</em>'te, <em>Y</em>-eksenini <em>y</em>'de keser; <em>P</em>'nin dik koordinatları "
        "(<em>x</em>, <em>y</em>)'dir.",
        "Coordinate plane with a point P and dashed perpendiculars to the axes marking its coordinates x and y")

# ============================================================ bolgeler
sc = plane((-5, 5), (-5, 5), 52, origin_square=True, xticks=(), yticks=())
for (sx, sy), col in (((1, 1), THEORY), ((-1, 1), BASE), ((-1, -1), PRACTICE), ((1, -1), REMARK)):
    sc.fill([(0, 0), (4.8 * sx, 0), (4.8 * sx, 4.8 * sy), (0, 4.8 * sy)], col, 0.17)
for (x, y), name, sig in (((2.5, 2.5), "I. bölge", "(+, +)"), ((-2.5, 2.5), "II. bölge", "(−, +)"),
                          ((-2.5, -2.5), "III. bölge", "(−, −)"), ((2.5, -2.5), "IV. bölge", "(+, −)")):
    sc.fixed((x, y), name, 14.5, TEXT, False, "middle", dy=-3, halo=False)
    sc.fixed((x, y), sig, 14, TEXT, False, "middle", dy=18, halo=False)
sc.emit("bolgeler",
        "Eksenler düzlemi dört bölgeye ayırır; parantez içindeki işaretler sırasıyla apsisin ve "
        "ordinatın işaretidir. Bölgeler saat yönünün tersine I'den IV'e sıralanır.",
        "The four quadrants of the coordinate plane shaded in four tones with the signs of the coordinates")

# ============================================================ bolge-bulma
sc = plane((-4, 6), (-6, 5), 48, xnums=(-4, -2, 2, 4), ynums=(-4, -2, 2, 4))
pts = {"A": (3, -2), "B": (-1, 4), "C": (-2, -5), "D": (0, 3), "E": (4, 1)}
for key, (x, y) in pts.items():
    if x != 0:
        sc.seg((x, y), (x, 0), TEXT, 1.0, "4 3", 0.55, weight=110)
    if y != 0 and x != 0:
        sc.seg((x, y), (0, y), TEXT, 1.0, "4 3", 0.55, weight=110)
for key, P in pts.items():
    sc.dot(P, PRACTICE if key != "D" else THEORY, 4.4)
sc.label(pts["A"], "A(3, -2)", ("se",))
sc.label(pts["B"], "B(-1, 4)", ("nw",))
sc.label(pts["C"], "C(-2, -5)", ("sw",))
sc.label(pts["D"], "D(0, 3)", ("e",))
sc.label(pts["E"], "E(4, 1)", ("ne",))
for spots, s in ((((5.3, 4.3), (4.6, 4.3), (5.3, 3.3)), "I"), (((-3.4, 4.3), (-3.4, 2.6), (-2.6, 1.6)), "II"),
                 (((-3.5, -3.6), (-3.5, -2.2), (-0.9, -3.0)), "III"), (((5.3, -4.4), (4.6, -4.4), (5.3, -3.5)), "IV")):
    sc.spot_label(spots, s, 15, REMARK, False, True, 0.8)
sc.emit("bolge-bulma",
        "<em>A</em> IV., <em>B</em> II., <em>C</em> III., <em>E</em> I. bölgededir; "
        "<em>D</em>(0, 3) ise <em>Y</em>-ekseni üzerinde olduğundan hiçbir bölgeye ait değildir.",
        "Points A(3,-2), B(-1,4), C(-2,-5), D(0,3) on the y axis and E(4,1) with dashed projections to the axes")

# ============================================================ pozitif-yon
sc = plane((-3, 3), (-3, 3), 86, xticks=(), yticks=())
sc.arc_arrow((0, 0), 1.8, 0.0, math.radians(300), THEORY, 2.3, 11.0)
sc.label((1.8 * math.cos(math.radians(45)), 1.8 * math.sin(math.radians(45))), "pozitif yön",
         ("ne", "e"), 13.5, THEORY, gap=9, math_mode=False)
sc.arc_arrow((0, 0), 0.9, 0.0, math.radians(-90), PRACTICE, 1.6, 9.0, opacity=0.75)
sc.label((1.2 * math.cos(math.radians(-35)), 1.2 * math.sin(math.radians(-35))), "negatif yön",
         ("e", "se"), 12.5, PRACTICE, gap=6, math_mode=False)
sc.emit("pozitif-yon",
        "Saat yönünün tersi pozitif yön, saat yönü negatif yöndür.",
        "Counterclockwise arc marked positive direction and a small clockwise arc marked negative direction")

# ============================================================ uzaklik-formulu
sc = plane((0, 6.5), (0, 5.0), 94, origin_square=True, xticks=(1.5, 4.5), yticks=(1.5, 3.8),
           xaxis=(-0.25, 6.5), yaxis=(-0.25, 5.0))
P1, P2, H = (1.5, 1.5), (4.5, 3.8), (4.5, 1.5)
for Q in (P1, P2):
    sc.seg(Q, (Q[0], 0), TEXT, 1.0, "4 3", 0.55, weight=110)
    sc.seg(Q, (0, Q[1]), TEXT, 1.0, "4 3", 0.55, weight=110)
sc.seg(P1, H, TEXT, 1.4, None, 0.85)
sc.seg(H, P2, TEXT, 1.4, None, 0.85)
sc.right_angle(H, P1, P2, 11)
sc.seg(P1, P2, PRACTICE, 2.9)
for Q in (P1, P2, H):
    sc.dot(Q, TEXT, 4.2)
sc.label(P1, "P_1(x_1, y_1)", ("sw", "nw"))
sc.label(P2, "P_2(x_2, y_2)", ("ne",))
sc.label(H, "H", ("se",))
sc.edge_label(P1, P2, "|P_1P_2|", away=H, size=14, color=PRACTICE)
sc.edge_label(P1, H, "x_2 - x_1", away=P2)
sc.edge_label(H, P2, "y_2 - y_1", away=P1)
sc.label((1.5, 0), "x_1", ("s",), 13.5, gap=7, strict=True)
sc.label((4.5, 0), "x_2", ("s",), 13.5, gap=7, strict=True)
sc.label((0, 1.5), "y_1", ("w",), 13.5, gap=8, strict=True)
sc.label((0, 3.8), "y_2", ("w",), 13.5, gap=8, strict=True)
sc.emit("uzaklik-formulu",
        "<em>P</em><sub>1</sub><em>HP</em><sub>2</sub> dik üçgeninin dik kenarları "
        "|<em>x</em><sub>2</sub> &#8722; <em>x</em><sub>1</sub>| ve |<em>y</em><sub>2</sub> &#8722; "
        "<em>y</em><sub>1</sub>|'dir; hipotenüs |<em>P</em><sub>1</sub><em>P</em><sub>2</sub>| Pisagor "
        "bağıntısıyla bulunur.",
        "Right triangle P1 H P2 with horizontal leg x2 minus x1 and vertical leg y2 minus y1; "
        "the hypotenuse is the distance P1P2", WIDE)

# ============================================================ ornek-uzaklik-i
sc = plane((-1, 5.5), (-3, 2.5), 76, xnums=ints(-1, 5), ynums=ints(-3, 2))
P1, P2, H = (4, 1), (3, -2), (3, 1)
sc.seg(H, P1, TEXT, 1.4, None, 0.85)
sc.seg(H, P2, TEXT, 1.4, None, 0.85)
sc.right_angle(H, P1, P2, 11)
sc.seg(P1, P2, PRACTICE, 2.9)
for Q in (P1, P2, H):
    sc.dot(Q, TEXT, 4.2)
sc.label(P1, "P_1(4, 1)", ("ne",))
sc.label(P2, "P_2(3, -2)", ("sw",))
sc.label(H, "H(3, 1)", ("nw",))
sc.edge_label(P1, P2, S(10), away=H, size=14, color=PRACTICE)
sc.edge_label(H, P1, "1", away=P2)
sc.edge_label(H, P2, "3", away=P1)
sc.emit("ornek-uzaklik-i",
        "Dik kenarları 1 ve 3 olan dik üçgenin hipotenüsü |<em>P</em><sub>1</sub><em>P</em><sub>2</sub>| = "
        "&#8730;10'dur.",
        "Points P1(4,1), P2(3,-2) and H(3,1) forming a right triangle with legs 1 and 3 and hypotenuse root 10")

# ============================================================ ornek-uzaklik-ii
sc = plane((-2.2, 5), (-7, 1), 70, xnums=(1, 2, 3), ynums=(-6, -4, -2))
P1, P2 = (2, -6), (2, -2)
sc.seg((2, -7), (2, 1), THEORY, 1.1, "5 4", 0.4, weight=60)
sc.seg(P1, P2, PRACTICE, 3.2)
sc.dot(P1, TEXT, 4.4)
sc.dot(P2, TEXT, 4.4)
sc.label(P1, "P_1(2, -6)", ("e",), gap=9)
sc.label(P2, "P_2(2, -2)", ("e",), gap=9)
sc.label((2, -4), "4", ("w",), 14, PRACTICE, gap=9)
sc.label((2, 0.75), "x = 2", ("e",), 12.5, THEORY, gap=8)
sc.emit("ornek-uzaklik-ii",
        "Apsisleri eşit iki nokta <em>x</em> = 2 düşey doğrusu üzerindedir; aralarındaki uzaklık "
        "ordinatlar farkının mutlak değeri olan 4'tür.",
        "Points P1(2,-6) and P2(2,-2) on the vertical line x = 2 at distance 4")

# ============================================================ ornek-uzaklik-iii
sc = plane((-7, 1.5), (-9, 1.5), 56, xnums=(-6, -4, -2), ynums=(-8, -6, -4, -2), origin=False,
           xnum_side="above")
P1, P2, H = (0, 0), (-6, -8), (-6, 0)
sc.seg(H, P1, THEORY, 2.0, None, 0.9)
sc.seg(H, P2, TEXT, 1.4, None, 0.85)
sc.right_angle(H, P1, P2, 11)
sc.seg(P1, P2, PRACTICE, 2.9)
for Q in (P1, P2, H):
    sc.dot(Q, TEXT, 4.2)
sc.label(P1, "P_1(0, 0)", ("ne",))
sc.label(P2, "P_2(-6, -8)", ("sw",))
sc.label(H, "H(-6, 0)", ("nw",))
sc.edge_label(P1, P2, "10", away=H, size=14, color=PRACTICE)
sc.edge_label(H, P1, "6", toward=P2, color=THEORY)
sc.edge_label(H, P2, "8", away=P1)
sc.emit("ornek-uzaklik-iii",
        "Başlangıç noktasına uzaklık: dik kenarları 6 ve 8 olan dik üçgenin hipotenüsü 10'dur.",
        "Right triangle with vertices at the origin, H(-6,0) and P2(-6,-8); legs 6 and 8, hypotenuse 10")

# ============================================================ ornek-apsisi-uc
sc = plane((-14, 8), (-5, 17), 23.5, xnums=(-10, -5, 5), ynums=(-5, 5, 10, 15))
P, Q1, Q2 = (-3, 6), (3, -2), (3, 14)
sc.circle(P, 10, REMARK, 1.3, "6 4", 0.7)
sc.seg((3, -5), (3, 17), THEORY, 1.5, "7 5", 0.9, weight=150)
sc.seg(P, (3, 6), TEXT, 1.2, "4 3", 0.7, weight=110)
sc.seg(P, Q1, PRACTICE, 2.7)
sc.seg(P, Q2, PRACTICE, 2.7)
sc.dot(P, TEXT, 4.4)
sc.dot(Q1, PRACTICE, 4.6)
sc.dot(Q2, PRACTICE, 4.6)
sc.label(P, "P(-3, 6)", ("w",), gap=9)
sc.label(Q1, "Q_1(3, -2)", ("e", "se"), gap=9)
sc.label(Q2, "Q_2(3, 14)", ("e", "ne"), gap=9)
sc.label((3, 16.4), "x = 3", ("e",), 13, THEORY, gap=8)
sc.edge_label(P, Q1, "10", away=(3, 6), size=13.5, color=PRACTICE)
sc.edge_label(P, Q2, "10", away=(3, 6), size=13.5, color=PRACTICE)
sc.edge_label(P, (3, 6), "6", toward=Q2, ts=(0.72, 0.78, 0.66, 0.28))
sc.emit("ornek-apsisi-uc",
        "<em>x</em> = 3 doğrusu, <em>P</em> merkezli 10 yarıçaplı çemberi <em>Q</em><sub>1</sub>(3, &#8722;2) "
        "ve <em>Q</em><sub>2</sub>(3, 14) noktalarında keser.",
        "Circle of radius 10 about P(-3,6) meeting the vertical line x = 3 at Q1(3,-2) and Q2(3,14)")

# ============================================================ ornek-cevre-i
sc = plane((-5, 4.5), (-4, 5.5), 50, xnums=evens(-5, 4), ynums=evens(-4, 5))
A, B, C = (0, 4), (-4, 1), (3, -3)
G = centroid(A, B, C)
triangle(sc, A, B, C)
for Q in (A, B, C):
    sc.dot(Q, TEXT, 4.2)
sc.label(A, "A(0, 4)", ("ne",))
sc.label(B, "B(-4, 1)", ("w",))
sc.label(C, "C(3, -3)", ("se",))
sc.edge_label(A, B, "5", away=G)
sc.edge_label(B, C, S(65), away=G)
sc.edge_label(C, A, S(58), away=G)
sc.emit("ornek-cevre-i",
        "Kenarları 5, &#8730;65 ve &#8730;58 olan üçgenin çevresi 5 + &#8730;65 + &#8730;58'dir.",
        "Triangle A(0,4), B(-4,1), C(3,-3) with side lengths 5, root 65 and root 58")

# ============================================================ ornek-cevre-ii
sc = plane((-3, 8.5), (-3, 6.5), 44, xnums=evens(-3, 8), ynums=evens(-3, 6))
A, B, C = (-2, 5), (4, 3), (7, -2)
G = centroid(A, B, C)
triangle(sc, A, B, C)
for Q in (A, B, C):
    sc.dot(Q, TEXT, 4.2)
sc.label(A, "A(-2, 5)", ("nw",))
sc.label(B, "B(4, 3)", ("ne",))
sc.label(C, "C(7, -2)", ("se",))
sc.edge_label(A, B, "2" + S(10), away=G)
sc.edge_label(B, C, S(34), away=G)
sc.edge_label(C, A, S(130), away=G)
sc.emit("ornek-cevre-ii",
        "Kenarları 2&#8730;10, &#8730;34 ve &#8730;130 olan üçgen.",
        "Triangle A(-2,5), B(4,3), C(7,-2) with side lengths 2 root 10, root 34 and root 130")

# ============================================================ ornek-ikizkenar-i
sc = plane((-5, 4.5), (-3, 7), 56, xnums=evens(-5, 4), ynums=evens(-3, 7))
A, B, C = (2, -2), (-3, -1), (1, 6)
G = centroid(A, B, C)
sc.fill([A, B, C], THEORY, 0.07)
sc.seg(A, B, TEXT, 1.4, None, 0.85)
sc.seg(B, C, THEORY, 2.7)
sc.seg(C, A, THEORY, 2.7)
sc.eq_tick(B, C)
sc.eq_tick(C, A)
for Q in (A, B, C):
    sc.dot(Q, TEXT, 4.2)
sc.label(A, "A(2, -2)", ("se",))
sc.label(B, "B(-3, -1)", ("sw",))
sc.label(C, "C(1, 6)", ("n",))
sc.edge_label(B, C, S(65), away=G, color=THEORY)
sc.edge_label(C, A, S(65), away=G, color=THEORY)
sc.edge_label(A, B, S(26), away=G)
sc.emit("ornek-ikizkenar-i",
        "|<em>BC</em>| = |<em>CA</em>| = &#8730;65: tepe noktası <em>C</em> olan ikizkenar üçgen.",
        "Isosceles triangle A(2,-2), B(-3,-1), C(1,6) with equal sides BC and CA of length root 65")

# ============================================================ ornek-ikizkenar-ii
sc = plane((-3, 7), (-3, 7), 50, xnums=evens(-3, 7), ynums=evens(-3, 7))
A, B, C = (-2, 2), (6, 6), (2, -2)
G = centroid(A, B, C)
sc.fill([A, B, C], THEORY, 0.07)
sc.seg(C, A, TEXT, 1.4, None, 0.85)
sc.seg(A, B, THEORY, 2.7)
sc.seg(B, C, THEORY, 2.7)
sc.eq_tick(A, B)
sc.eq_tick(B, C)
for Q in (A, B, C):
    sc.dot(Q, TEXT, 4.2)
sc.label(A, "A(-2, 2)", ("w",))
sc.label(B, "B(6, 6)", ("ne",))
sc.label(C, "C(2, -2)", ("s",))
sc.edge_label(A, B, "4" + S(5), away=G, color=THEORY)
sc.edge_label(B, C, "4" + S(5), away=G, color=THEORY)
sc.edge_label(C, A, "4" + S(2), away=G)
sc.emit("ornek-ikizkenar-ii",
        "|<em>AB</em>| = |<em>BC</em>| = 4&#8730;5: tepe noktası <em>B</em> olan ikizkenar üçgen.",
        "Isosceles triangle A(-2,2), B(6,6), C(2,-2) with equal sides AB and BC of length 4 root 5")

# ============================================================ ornek-dik-ucgen-i
sc = plane((-5.6, 4.7), (-2, 10), 50, xnums=evens(-5, 4), ynums=evens(-2, 10))
A, B, C = (-4, -1), (3, 2), (0, 9)
G = centroid(A, B, C)
sc.fill([A, B, C], THEORY, 0.07)
sc.seg(A, B, THEORY, 2.7)
sc.seg(B, C, THEORY, 2.7)
sc.seg(C, A, PRACTICE, 2.3)
sc.right_angle(B, A, C, 12)
sc.eq_tick(A, B)
sc.eq_tick(B, C)
for Q in (A, B, C):
    sc.dot(Q, TEXT, 4.2)
sc.label(A, "A(-4, -1)", ("sw",))
sc.label(B, "B(3, 2)", ("e",))
sc.label(C, "C(0, 9)", ("ne",))
sc.edge_label(A, B, S(58), away=G, color=THEORY)
sc.edge_label(B, C, S(58), away=G, color=THEORY)
sc.edge_label(C, A, S(116), away=G, color=PRACTICE)
sc.emit("ornek-dik-ucgen-i",
        "58 + 58 = 116 olduğundan <em>B</em> açısı diktir; eşit dik kenarlar üçgeni ikizkenar dik üçgen yapar.",
        "Right isosceles triangle A(-4,-1), B(3,2), C(0,9) with the right angle at B")

# ============================================================ ornek-dik-ucgen-ii
sc = plane((-3, 4), (-3, 5), 64, xnums=ints(-3, 3), ynums=ints(-3, 4))
A, B, C = (-2, 3), (0, 4), (3, -2)
G = centroid(A, B, C)
sc.fill([A, B, C], THEORY, 0.07)
sc.seg(A, B, THEORY, 2.5)
sc.seg(B, C, THEORY, 2.5)
sc.seg(A, C, PRACTICE, 2.3)
sc.right_angle(B, A, C, 11)
for Q in (A, B, C):
    sc.dot(Q, TEXT, 4.2)
sc.label(A, "A(-2, 3)", ("w",))
sc.label(B, "B(0, 4)", ("ne", "e"))
sc.label(C, "C(3, -2)", ("se",))
sc.edge_label(A, B, S(5), away=G, color=THEORY)
sc.edge_label(B, C, "3" + S(5), away=G, color=THEORY)
sc.edge_label(A, C, "5" + S(2), away=G, color=PRACTICE)
sc.emit("ornek-dik-ucgen-ii",
        "5 + 45 = 50 olduğundan <em>B</em> açısı diktir.",
        "Right triangle A(-2,3), B(0,4), C(3,-2) with the right angle at B")

# ============================================================ ornek-kare
sc = plane((-5, 1.5), (-3, 3), 72, xnums=ints(-5, 1), ynums=ints(-3, 2))
A, B, C, D = (-1, -2), (0, 1), (-3, 2), (-4, -1)
M = centroid(A, B, C, D)
sc.fill([A, B, C, D], THEORY, 0.07)
sc.seg(A, C, BASE, 1.6, "6 4", 0.95, weight=150)
sc.seg(B, D, PRACTICE, 1.6, "6 4", 0.95, weight=150)
sc.poly([A, B, C, D], THEORY, 2.6)
for V, U, W in ((A, B, D), (B, C, A), (C, D, B), (D, A, C)):
    sc.right_angle(V, U, W, 10)
for U, W in ((A, B), (B, C), (C, D), (D, A)):
    sc.eq_tick(U, W)
for Q in (A, B, C, D):
    sc.dot(Q, TEXT, 4.2)
sc.label(A, "A(-1, -2)", ("se",))
sc.label(B, "B(0, 1)", ("e",))
sc.label(C, "C(-3, 2)", ("nw",))
sc.label(D, "D(-4, -1)", ("w",))
for U, W in ((A, B), (B, C), (C, D), (D, A)):
    sc.edge_label(U, W, S(10), away=M, color=THEORY, ts=(0.3, 0.7, 0.24, 0.76))
sc.edge_label(A, C, S(20), color=BASE, ts=(0.28, 0.72, 0.22, 0.78), both=True, away=B)
sc.edge_label(B, D, S(20), color=PRACTICE, ts=(0.72, 0.28, 0.78, 0.22), both=True, away=A)
sc.emit("ornek-kare",
        "Dört kenarı &#8730;10, iki köşegeni &#8730;20 olan <em>ABCD</em> bir karedir.",
        "Square A(-1,-2), B(0,1), C(-3,2), D(-4,-1) with sides root 10 and diagonals root 20")

# ============================================================ ornek-dogrusal
sc = plane((-4.2, 5.2), (-3, 9), 52, xnums=evens(-4, 5), ynums=evens(-3, 9))
A, B, C = (-2, 8), (0, 4), (3, -2)
d = (1 / math.sqrt(5), -2 / math.sqrt(5))
sc.seg((A[0] - 0.45 * d[0] * 1.6, A[1] - 0.45 * d[1] * 1.6), (C[0] + 0.45 * d[0] * 1.6, C[1] + 0.45 * d[1] * 1.6),
       TEXT, 1.0, None, 0.35, weight=100)
sc.seg(A, B, THEORY, 3.0)
sc.seg(B, C, PRACTICE, 3.0)
off = 1.05
nrm = (-2 / math.sqrt(5), -1 / math.sqrt(5))        # toward the lower left of the line
A2 = (A[0] + off * nrm[0], A[1] + off * nrm[1])
C2 = (C[0] + off * nrm[0], C[1] + off * nrm[1])
sc.seg(A2, C2, TEXT, 1.1, None, 0.75, weight=150)
for E in (A2, C2):
    sc.seg((E[0] - 0.18 * nrm[0], E[1] - 0.18 * nrm[1]), (E[0] + 0.18 * nrm[0], E[1] + 0.18 * nrm[1]),
           TEXT, 1.2, None, 0.75, weight=80)
for Q in (A, B, C):
    sc.dot(Q, TEXT, 4.4)
sc.label(A, "A(-2, 8)", ("w",))
sc.label(B, "B(0, 4)", ("e",))
sc.label(C, "C(3, -2)", ("e",))
sc.edge_label(A, B, "2" + S(5), toward=(5, 9), color=THEORY, size=14)
sc.edge_label(B, C, "3" + S(5), toward=(5, 9), color=PRACTICE, size=14)
sc.edge_label(A2, C2, "5" + S(5), away=A, size=14, ts=(0.5, 0.44, 0.56, 0.38, 0.62))
sc.emit("ornek-dogrusal",
        "|<em>AB</em>| + |<em>BC</em>| = 2&#8730;5 + 3&#8730;5 = 5&#8730;5 = |<em>AC</em>|: "
        "<em>B</em>, <em>AC</em> doğru parçası üzerindedir.",
        "Collinear points A(-2,8), B(0,4), C(3,-2); AB is 2 root 5, BC is 3 root 5 and AC is 5 root 5")


# ============================================================ equidistant-point helper
def equidistant(name, xr, yr, ppu, A, B, C, P, r, rlabel, dirs, xnums, ynums, caption, aria, **kw):
    sc = plane(xr, yr, ppu, xnums=xnums, ynums=ynums, **kw)
    sc.circle(P, r, REMARK, 1.3, None, 0.55)
    sc.poly([A, B, C], THEORY, 1.5, None, 0.9)
    G = centroid(A, B, C)
    for Q in (A, B, C):
        sc.seg(P, Q, PRACTICE, 1.7, "6 4", 0.95, weight=150)
    for Q in (A, B, C):
        sc.dot(Q, TEXT, 4.2)
    sc.dot(P, PRACTICE, 5.0)
    names = ("A", "B", "C")
    for Q, nm, dd in zip((A, B, C), names, dirs[:3]):
        sc.label(Q, f"{nm}({num(Q[0])}, {num(Q[1])})", dd)
    sc.label(P, f"P({num(P[0])}, {num(P[1])})", dirs[3], 14, PRACTICE)
    for Q in (A, B, C):
        sc.edge_label(P, Q, rlabel, color=PRACTICE, both=True, away=G,
                      ts=(0.5, 0.4, 0.6, 0.32, 0.68))
    sc.emit(name, caption, aria)


equidistant("ornek-esit-uzaklik-i", (-2, 10), (-3, 9.5), 42, (1, 7), (8, 6), (7, -1), (4, 3), 5, "5",
            (("nw", "n"), ("e",), ("se",), ("s", "sw", "se")), evens(-2, 10), evens(-3, 9),
            "<em>P</em>(4, 3) üç köşeye de 5 birim uzaklıktadır; <em>P</em> merkezli 5 yarıçaplı çember "
            "<em>A</em>, <em>B</em> ve <em>C</em>'den geçer.",
            "Triangle A(1,7), B(8,6), C(7,-1) with the circumcenter P(4,3) and the circumcircle of radius 5")

equidistant("ornek-esit-uzaklik-ii", (-3, 9), (-8, 4), 42, (3, 3), (6, 2), (8, -2), (3, -2), 5, "5",
            (("n",), ("ne",), ("e",), ("sw",)), evens(-3, 9), evens(-8, 4),
            "<em>P</em>(3, &#8722;2) üç noktaya da 5 birim uzaklıktadır; <em>PA</em> düşey, <em>PC</em> yataydır.",
            "Points A(3,3), B(6,2), C(8,-2) with the equidistant point P(3,-2) and the circle of radius 5")

equidistant("ornek-esit-uzaklik-iii", (-15, 5.8), (-9, 11), 25, (4, 3), (2, 7), (-3, -8), (-5, 1),
            math.sqrt(85), S(85), (("e",), ("ne",), ("s",), ("w",)), (-15, -10, -5, 5), (-5, 5, 10),
            "Geniş açılı üçgende çevrel çemberin merkezi <em>P</em>(&#8722;5, 1) üçgenin dışında kalır; "
            "yarıçap &#8730;85 &#8776; 9,22'dir.",
            "Obtuse triangle A(4,3), B(2,7), C(-3,-8) whose circumcenter P(-5,1) lies outside the triangle")

# ============================================================ alistirma-nokta-cifti-i
sc = plane((-9.5, 4), (-12, 5.5), 36, xnums=(-6, -4, -2), ynums=(-10, -5, 4))
P1, P2, H = (-7, 4), (1, -11), (1, 4)
sc.seg(P1, H, TEXT, 1.4, None, 0.85)
sc.seg(H, P2, TEXT, 1.4, None, 0.85)
sc.right_angle(H, P1, P2, 11)
sc.seg(P1, P2, PRACTICE, 2.9)
for Q in (P1, P2, H):
    sc.dot(Q, TEXT, 4.2)
sc.label(P1, "P_1(-7, 4)", ("nw",))
sc.label(P2, "P_2(1, -11)", ("se",))
sc.label(H, "H(1, 4)", ("ne",))
sc.edge_label(P1, P2, "17", away=H, size=14, color=PRACTICE)
sc.edge_label(P1, H, "8", away=P2)
sc.edge_label(H, P2, "15", away=P1)
sc.emit("alistirma-nokta-cifti-i",
        "Dik kenarları 8 ve 15 olan dik üçgenin hipotenüsü 17'dir.",
        "Right triangle P1(-7,4), H(1,4), P2(1,-11) with legs 8 and 15 and hypotenuse 17")

# ============================================================ alistirma-nokta-cifti-ii
sc = plane((-5, 1.5), (-1, 4.5), 76, xnums=ints(-5, 1), ynums=ints(-1, 4))
P1, P2, H = (0, 3), (-4, 1), (-4, 3)
sc.seg(H, P1, TEXT, 1.4, None, 0.85)
sc.seg(H, P2, TEXT, 1.4, None, 0.85)
sc.right_angle(H, P1, P2, 11)
sc.seg(P1, P2, PRACTICE, 2.9)
for Q in (P1, P2, H):
    sc.dot(Q, TEXT, 4.2)
sc.label(P1, "P_1(0, 3)", ("e",))
sc.label(P2, "P_2(-4, 1)", ("sw",))
sc.label(H, "H(-4, 3)", ("nw",))
sc.edge_label(P1, P2, "2" + S(5), away=H, size=14, color=PRACTICE)
sc.edge_label(H, P1, "4", away=P2)
sc.edge_label(H, P2, "2", away=P1)
sc.emit("alistirma-nokta-cifti-ii",
        "Dik kenarları 4 ve 2 olan dik üçgenin hipotenüsü &#8730;20 = 2&#8730;5'tir.",
        "Right triangle P1(0,3), H(-4,3), P2(-4,1) with legs 4 and 2 and hypotenuse 2 root 5")


# ============================================================ right-triangle exercises
def right_triangle(name, xr, yr, ppu, A, B, C, labs, dirs, equal, caption, aria, xnums, ynums):
    sc = plane(xr, yr, ppu, xnums=xnums, ynums=ynums)
    G = centroid(A, B, C)
    sc.fill([A, B, C], THEORY, 0.07)
    sc.seg(A, B, THEORY, 2.6)
    sc.seg(B, C, THEORY, 2.6)
    sc.seg(C, A, PRACTICE, 2.3)
    sc.right_angle(B, A, C, 12)
    if equal:
        sc.eq_tick(A, B)
        sc.eq_tick(B, C)
    for Q in (A, B, C):
        sc.dot(Q, TEXT, 4.2)
    for Q, nm, dd in zip((A, B, C), "ABC", dirs):
        sc.label(Q, f"{nm}({num(Q[0])}, {num(Q[1])})", dd)
    sc.edge_label(A, B, labs[0], away=G, color=THEORY)
    sc.edge_label(B, C, labs[1], away=G, color=THEORY)
    sc.edge_label(C, A, labs[2], away=G, color=PRACTICE)
    sc.emit(name, caption, aria)


right_triangle("alistirma-dik-ucgen-i", (-1, 11.5), (-6, 6.5), 42, (10, 5), (3, 2), (6, -5),
               (S(58), S(58), S(116)), (("ne",), ("w",), ("s",)), True,
               "58 + 58 = 116 olduğundan <em>B</em> açısı diktir; üçgen ikizkenar dik üçgendir.",
               "Right isosceles triangle A(10,5), B(3,2), C(6,-5) with the right angle at B",
               evens(-1, 11), evens(-6, 6))

right_triangle("alistirma-dik-ucgen-ii", (-2.5, 10), (-8, 6.5), 42, (7, 5), (2, 3), (6, -7),
               (S(29), S(116), S(145)), (("ne",), ("w",), ("s",)), False,
               "29 + 116 = 145 olduğundan <em>B</em> açısı diktir.",
               "Right triangle A(7,5), B(2,3), C(6,-7) with the right angle at B",
               evens(-1, 8), evens(-8, 6))

right_triangle("alistirma-dik-ucgen-iii", (-1, 9.5), (-1, 9.5), 50, (8, 6), (4, 8), (2, 4),
               (S(20), S(20), S(40)), (("e",), ("n",), ("w",)), True,
               "20 + 20 = 40 olduğundan <em>B</em> açısı diktir; üçgen ikizkenar dik üçgendir.",
               "Right isosceles triangle A(8,6), B(4,8), C(2,4) with the right angle at B",
               evens(-1, 9), evens(-1, 9))

# ============================================================ orta-nokta
sc = plane((0, 7), (0, 5.5), 86, xticks=(1, 3.5, 6), yticks=(1, 2.75, 4.5),
           xaxis=(-0.25, 7), yaxis=(-0.25, 5.5))
P1, P2 = (1, 1), (6, 4.5)
M = ((P1[0] + P2[0]) / 2, (P1[1] + P2[1]) / 2)
for Q in (P1, M, P2):
    sc.seg(Q, (Q[0], 0), TEXT, 1.0, "4 3", 0.55, weight=110)
    sc.seg(Q, (0, Q[1]), TEXT, 1.0, "4 3", 0.55, weight=110)
sc.seg(P1, P2, THEORY, 2.6)
sc.eq_tick(P1, M)
sc.eq_tick(M, P2)
sc.dot(P1, TEXT, 4.2)
sc.dot(P2, TEXT, 4.2)
sc.dot(M, PRACTICE, 5.0)
sc.label(P1, "P_1(x_1, y_1)", ("sw", "se"))
sc.label(P2, "P_2(x_2, y_2)", ("ne",))
sc.label(M, "M", ("nw",), 15, PRACTICE)
for x, s in ((1, "x_1"), (3.5, "(x_1 + x_2)/2"), (6, "x_2")):
    sc.label((x, 0), s, ("s",), 13, gap=7, strict=True)
for y, s in ((1, "y_1"), (2.75, "(y_1 + y_2)/2"), (4.5, "y_2")):
    sc.label((0, y), s, ("w",), 13, gap=8, strict=True)
sc.emit("orta-nokta",
        "Orta nokta: <em>M</em>'nin koordinatları uç noktaların koordinatlarının ortalamasıdır ve "
        "|<em>P</em><sub>1</sub><em>M</em>| = |<em>MP</em><sub>2</sub>|'dir.",
        "Segment P1P2 with its midpoint M; the projections show that the coordinates of M are the averages", WIDE)


# ============================================================ triangle from midpoints helper
def from_midpoints(name, xr, yr, ppu, P1, P2, P3, pdirs, mdirs, caption, aria, xnums, ynums):
    sc = plane(xr, yr, ppu, xnums=xnums, ynums=ynums)
    Ms = [((P1[0] + P2[0]) / 2, (P1[1] + P2[1]) / 2), ((P2[0] + P3[0]) / 2, (P2[1] + P3[1]) / 2),
          ((P1[0] + P3[0]) / 2, (P1[1] + P3[1]) / 2)]
    sc.fill([P1, P2, P3], THEORY, 0.06)
    sc.poly([P1, P2, P3], THEORY, 2.6)
    sc.poly(Ms, PRACTICE, 1.7, "6 4", 0.95, weight=150)
    for Q in (P1, P2, P3):
        sc.dot(Q, TEXT, 4.2)
    for Q in Ms:
        sc.ring(Q, PRACTICE, 4.8)
    for Q, k, dd in zip((P1, P2, P3), "123", pdirs):
        sc.label(Q, f"P_{k}({num(Q[0])}, {num(Q[1])})", dd)
    for Q, dd in zip(Ms, mdirs):
        sc.label(Q, f"({num(Q[0])}, {num(Q[1])})", dd, 13, PRACTICE)
    sc.emit(name, caption, aria)


from_midpoints("alistirma-orta-noktalar-1", (-6, 10), (-5, 7), 34, (-5, -4), (1, 6), (9, -2),
               (("sw",), ("n",), ("e",)), (("w", "nw"), ("ne",), ("s",)),
               "Kenar orta noktaları (&#8722;2, 1), (5, 2) ve (2, &#8722;3) olan üçgenin köşeleri "
               "<em>P</em><sub>1</sub>(&#8722;5, &#8722;4), <em>P</em><sub>2</sub>(1, 6) ve "
               "<em>P</em><sub>3</sub>(9, &#8722;2)'dir.",
               "Triangle P1(-5,-4), P2(1,6), P3(9,-2) with its side midpoints and the dashed medial triangle",
               evens(-6, 10), evens(-5, 7))

# ============================================================ alistirma-dikdortgen
sc = plane((-1, 7.5), (-1, 5.5), 64, origin=False, xticks=(), yticks=())
O, A, C, B = (0, 0), (6, 0), (6, 4), (0, 4)
P = (2, 1.5)
sc.poly([O, A, C, B], TEXT, 2.4)
sc.seg(P, O, THEORY, 2.2)
sc.seg(P, C, THEORY, 2.2)
sc.seg(P, A, PRACTICE, 2.2, "7 4")
sc.seg(P, B, PRACTICE, 2.2, "7 4")
for Q in (O, A, C, B):
    sc.dot(Q, TEXT, 4.2)
sc.dot(P, TEXT, 4.6)
sc.label(O, "O(0, 0)", ("sw",))
sc.label(A, "A(a, 0)", ("s", "se"))
sc.label(C, "C(a, b)", ("ne",))
sc.label(B, "B(0, b)", ("w",))
sc.label(P, "P(x, y)", ("s", "w"))
lx, ly = sc.px((7.75, 3.2))
sc.p.add(f'<line x1="{lx:.1f}" y1="{ly - 4.5:.1f}" x2="{lx + 26:.1f}" y2="{ly - 4.5:.1f}" stroke="{THEORY}" '
         f'stroke-width="2.4"/>')
sc.fixed_px(lx + 33, ly, "|OP|^2 + |PC|^2", 13, TEXT, True, halo=False)
sc.p.add(f'<line x1="{lx:.1f}" y1="{ly + 22 - 4.5:.1f}" x2="{lx + 26:.1f}" y2="{ly + 22 - 4.5:.1f}" '
         f'stroke="{PRACTICE}" stroke-width="2.4" stroke-dasharray="7 4"/>')
sc.fixed_px(lx + 33, ly + 22, "|AP|^2 + |PB|^2", 13, TEXT, True, halo=False)
sc.emit("alistirma-dikdortgen",
        "Dikdörtgenin karşılıklı köşelerine uzaklıkların kareleri toplamı eşittir: "
        "|<em>OP</em>|² + |<em>PC</em>|² = |<em>AP</em>|² + |<em>PB</em>|².",
        "Rectangle O A C B with a point P joined to the opposite corners O, C by solid lines and A, B by dashed lines",
        WIDE)


# ============================================================ centroid helper
def centroid_fig(name, xr, yr, ppu, P1, P2, P3, pdirs, Gs, Gdirs, mlabels, caption, aria, xnums, ynums,
                 ratio_labels=False):
    sc = plane(xr, yr, ppu, xnums=xnums, ynums=ynums)
    Gp = centroid(P1, P2, P3)
    M1 = ((P2[0] + P3[0]) / 2, (P2[1] + P3[1]) / 2)     # opposite P1
    M2 = ((P1[0] + P3[0]) / 2, (P1[1] + P3[1]) / 2)     # opposite P2
    M3 = ((P1[0] + P2[0]) / 2, (P1[1] + P2[1]) / 2)     # opposite P3
    sc.fill([P1, P2, P3], THEORY, 0.06)
    sc.poly([P1, P2, P3], THEORY, 2.6)
    for V, Mm in ((P1, M1), (P2, M2), (P3, M3)):
        sc.seg(V, Mm, BASE, 1.5, "6 4", 0.95, weight=150)
    for Q in (P1, P2, P3):
        sc.dot(Q, TEXT, 4.2)
    for Q in (M1, M2, M3):
        sc.ring(Q, BASE, 4.4)
    sc.dot(Gp, PRACTICE, 5.0)
    for Q, k, dd in zip((P1, P2, P3), "123", pdirs):
        sc.label(Q, f"P_{k}({num(Q[0])}, {num(Q[1])})", dd)
    sc.label(Gp, Gs, Gdirs, 14, PRACTICE)
    for Mm, (s, dd) in zip((M1, M2, M3), mlabels):
        if s:
            sc.label(Mm, s, dd, 13, BASE)
    if ratio_labels:
        sc.edge_label(P1, Gp, "2k", both=True, away=P3, size=13, color=BASE, ts=(0.5, 0.4, 0.6))
        sc.edge_label(Gp, M1, "k", both=True, away=P3, size=13, color=BASE, ts=(0.5, 0.4, 0.6))
    sc.emit(name, caption, aria)


centroid_fig("alistirma-agirlik-merkezi-i", (-6, 6.5), (-4, 8), 42, (5, 7), (1, -3), (-5, 1),
             (("ne",), ("s",), ("w",)), "G(1/3, 5/3)", ("e", "se", "ne"),
             (("M(-2, -1)", ("sw",)), ("N(0, 4)", ("w", "nw")), ("", ())),
             "Kenarortaylar <em>G</em>(1/3, 5/3)'te kesişir; <em>G</em> her kenarortayı köşeden itibaren "
             "2 : 1 oranında böler.",
             "Triangle P1(5,7), P2(1,-3), P3(-5,1) with its three medians meeting at the centroid G(1/3,5/3)",
             evens(-6, 6), evens(-4, 8), ratio_labels=True)

centroid_fig("alistirma-agirlik-merkezi-ii", (-5, 7), (-4, 8), 42, (2, -1), (6, 7), (-4, -3),
             (("se",), ("ne",), ("sw",)), "G(4/3, 1)", ("se", "e", "s"),
             (("M(1, 2)", ("w", "nw")), ("", ()), ("", ())),
             "Kenarortaylar <em>G</em>(4/3, 1)'de kesişir; <em>P</em><sub>1</sub><em>M</em> kenarortayında "
             "|<em>P</em><sub>1</sub><em>G</em>| = 2 |<em>GM</em>|'dir.",
             "Triangle P1(2,-1), P2(6,7), P3(-4,-3) with its medians meeting at the centroid G(4/3,1)",
             evens(-5, 7), evens(-4, 8))

# ============================================================ egim-diklik
sc = Scene((-0.6, 2.1), (-2.15, 1.4), 150, left=110, right=200)
for k in range(-2, 9):
    x = k * 0.25
    sc.p.add(f'<line x1="{sc.p.X(x):.1f}" y1="{sc.p.Y(1.25):.1f}" x2="{sc.p.X(x):.1f}" y2="{sc.p.Y(-2.0):.1f}" '
             f'stroke="{TEXT}" stroke-width="0.7" opacity="0.13"/>')
for k in range(-8, 6):
    y = k * 0.25
    sc.p.add(f'<line x1="{sc.p.X(-0.5):.1f}" y1="{sc.p.Y(y):.1f}" x2="{sc.p.X(2.0):.1f}" y2="{sc.p.Y(y):.1f}" '
             f'stroke="{TEXT}" stroke-width="0.7" opacity="0.13"/>')
B0 = (0.0, 0.0)
m1, m2 = 0.8, -1.25
U, V, F = (1.0, m1), (1.0, m2), (1.0, 0.0)
sc.seg((-0.3, -0.3 * m1), (1.55, 1.55 * m1), THEORY, 1.4, None, 0.8)
sc.seg((-0.3, -0.3 * m2), (1.55, 1.55 * m2), PRACTICE, 1.4, None, 0.8)
sc.seg(B0, U, THEORY, 3.0)
sc.seg(B0, V, PRACTICE, 3.0)
sc.seg(B0, F, TEXT, 1.3, "5 4", 0.8, weight=120)
sc.seg((1.0, 1.2), (1.0, -1.9), TEXT, 1.2, "5 4", 0.6, weight=120)
sc.seg(U, V, BASE, 3.4)
sc.right_angle(B0, U, V, 13)
for Q in (B0, U, V):
    sc.dot(Q, TEXT, 4.6)
sc.label(B0, "B(p, q)", ("w",), 14)
sc.label(U, "U(p + 1, q + m_1)", ("e", "se"), 14, gap=9)
sc.label(V, "V(p + 1, q + m_2)", ("e", "ne"), 14, gap=9)
sc.edge_label(B0, F, "1", away=U, size=14)
sc.edge_label(U, V, "|m_1 - m_2|", away=B0, size=14, color=BASE, ts=(0.5, 0.56, 0.44, 0.62))
sc.label((1.55, 1.55 * m1), "eğim $m_1$", ("e", "ne", "n"), 13.5, THEORY, gap=6, math_mode=False)
sc.label((1.55, 1.55 * m2), "eğim $m_2$", ("e", "se", "s"), 13.5, PRACTICE, gap=6, math_mode=False)
sc.emit("egim-diklik",
        "<em>B</em>'den sağa bir birim gidince iki doğru <em>U</em> ve <em>V</em>'ye ulaşır. "
        "<em>UBV</em> açısı ancak ve ancak |<em>BU</em>|² + |<em>BV</em>|² = |<em>UV</em>|², "
        "yani <em>m</em><sub>1</sub><em>m</em><sub>2</sub> = &#8722;1 iken diktir.",
        "Two perpendicular lines through B with slopes m1 and m2; one unit to the right they reach U and V")

# ============================================================ alistirma-egimle-dik-i
sc = plane((-1, 11.5), (-6, 6.5), 50, xnums=evens(-1, 11), ynums=evens(-6, 6))
A, B, C = (10, 5), (3, 2), (6, -5)
G = centroid(A, B, C)
sc.fill([A, B, C], THEORY, 0.06)
sc.poly([A, B, C], THEORY, 2.5)
sh = 2.2 / sc.ppu      # the two horizontal legs overlap on 3 <= x <= 6; draw them 2.2 px apart
sc.seg((3, 2 - sh), (10, 2 - sh), BASE, 1.7, "6 4", 0.95, weight=150)
sc.seg((10, 2), A, BASE, 1.7, "6 4", 0.95, weight=150)
sc.seg((3, 2 + sh), (6, 2 + sh), PRACTICE, 1.7, "6 4", 0.95, weight=150)
sc.seg((6, 2), C, PRACTICE, 1.7, "6 4", 0.95, weight=150)
sc.right_angle(B, A, C, 12)
for Q in (A, B, C):
    sc.dot(Q, TEXT, 4.2)
sc.label(A, "A(10, 5)", ("ne",))
sc.label(B, "B(3, 2)", ("w",))
sc.label(C, "C(6, -5)", ("s",))
sc.edge_label((6, 2), (10, 2), "7", away=A, color=BASE, size=13.5, ts=(0.5, 0.4, 0.6))
sc.edge_label((10, 2), A, "3", away=B, color=BASE, size=13.5)
sc.edge_label(B, (6, 2), "3", toward=A, color=PRACTICE, size=13.5)
sc.edge_label((6, 2), C, "-7", away=B, color=PRACTICE, size=13.5)
sc.edge_label(B, A, "m_{AB} = 3/7", away=C, color=BASE, size=14, ts=(0.5, 0.6, 0.4, 0.7))
sc.edge_label(B, C, "m_{BC} = -7/3", away=A, color=PRACTICE, size=14, ts=(0.5, 0.6, 0.4, 0.7))
sc.emit("alistirma-egimle-dik-i",
        "Eğim üçgenleri: <em>m</em><sub><em>AB</em></sub> = 3/7 ve <em>m</em><sub><em>BC</em></sub> = &#8722;7/3; "
        "çarpımları &#8722;1 olduğundan <em>AB</em> &#8869; <em>BC</em>'dir.",
        "Triangle A(10,5), B(3,2), C(6,-5) with the slope triangles of AB (run 7, rise 3) and BC (run 3, rise -7)",
        WIDE)


# ============================================================ parallelogram helpers
def parallelogram_base(xr, yr, ppu, A, B, C, D, xnums, ynums, origin=False):
    sc = plane(xr, yr, ppu, xnums=xnums, ynums=ynums, origin=origin)
    return sc


# alistirma-paralelkenar-i
A, B, C, D = (-1, -5), (2, 1), (1, 5), (-2, -1)
M = (0, 0)
sc = parallelogram_base((-4.6, 5.1), (-6, 6), 52, A, B, C, D, (-2, 2), (-4, -2, 2, 4))
sc.fill([A, B, C, D], THEORY, 0.07)
sc.seg(A, C, TEXT, 1.3, "5 4", 0.7, weight=120)
sc.seg(B, D, TEXT, 1.3, "5 4", 0.7, weight=120)
sc.poly([A, B, C, D], THEORY, 2.6)
sc.par_mark(A, B, 1)
sc.par_mark(D, C, 1)
sc.par_mark(B, C, 2)
sc.par_mark(A, D, 2)
for Q in (A, B, C, D):
    sc.dot(Q, TEXT, 4.2)
sc.dot(M, PRACTICE, 4.8)
sc.label(A, "A(-1, -5)", ("s",))
sc.label(B, "B(2, 1)", ("e",))
sc.label(C, "C(1, 5)", ("n",))
sc.label(D, "D(-2, -1)", ("w",))
sc.label(M, "(0, 0)", ("se",), 13, PRACTICE)
for U, W, s in ((A, B, S(45)), (C, D, S(45)), (B, C, S(17)), (D, A, S(17))):
    sc.edge_label(U, W, s, away=M, color=THEORY, ts=(0.5, 0.36, 0.64, 0.28, 0.72))
sc.emit("alistirma-paralelkenar-i",
        "Karşılıklı kenarlar paraleldir (eğimler 2 ve &#8722;4) ve eşittir; köşegenler birbirini "
        "(0, 0)'da ortalar.",
        "Parallelogram A(-1,-5), B(2,1), C(1,5), D(-2,-1) with parallel marks and diagonals bisecting at the origin")

# alistirma-paralelkenar-ii
A, B, C, D = (2, 4), (6, 2), (8, 6), (4, 8)
M = (5, 5)
sc = plane((-0.5, 9), (-0.5, 9), 54, xnums=evens(-0.5, 9), ynums=evens(-0.5, 9))
sc.fill([A, B, C, D], THEORY, 0.07)
sc.seg(A, C, BASE, 1.6, "6 4", 0.95, weight=150)
sc.seg(B, D, PRACTICE, 1.6, "6 4", 0.95, weight=150)
sc.poly([A, B, C, D], THEORY, 2.6)
for V, U, W in ((A, B, D), (B, C, A), (C, D, B), (D, A, C)):
    sc.right_angle(V, U, W, 10)
for U, W in ((A, B), (B, C), (C, D), (D, A)):
    sc.eq_tick(U, W)
for Q in (A, B, C, D):
    sc.dot(Q, TEXT, 4.2)
sc.dot(M, TEXT, 3.2)
sc.label(A, "A(2, 4)", ("w",))
sc.label(B, "B(6, 2)", ("s",))
sc.label(C, "C(8, 6)", ("e",))
sc.label(D, "D(4, 8)", ("n",))
for U, W in ((A, B), (B, C), (C, D), (D, A)):
    sc.edge_label(U, W, S(20), away=M, color=THEORY, ts=(0.3, 0.7, 0.24, 0.76))
sc.edge_label(A, C, S(40), color=BASE, ts=(0.27, 0.73, 0.2, 0.8), both=True, away=B)
sc.edge_label(B, D, S(40), color=PRACTICE, ts=(0.27, 0.73, 0.2, 0.8), both=True, away=C)
sc.emit("alistirma-paralelkenar-ii",
        "Dört kenarı &#8730;20, köşegenleri &#8730;40 olan ve açıları dik olan <em>ABCD</em> bir karedir.",
        "Square A(2,4), B(6,2), C(8,6), D(4,8) with sides root 20 and diagonals root 40 meeting at (5,5)")

# alistirma-dikdortgen-mi
A, B, C, D = (-1, -5), (2, 1), (1, 5), (-2, -1)
sc = parallelogram_base((-4.6, 5.1), (-6, 6), 52, A, B, C, D, (-2, 2), (-4, -2, 2, 4))
sc.fill([A, B, C, D], THEORY, 0.06)
sc.seg(A, C, BASE, 2.3, "7 5", 1.0, weight=150)
sc.seg(B, D, PRACTICE, 2.3, "7 5", 1.0, weight=150)
sc.poly([A, B, C, D], THEORY, 2.6)
a_c = math.atan2(C[1] - B[1], C[0] - B[0])
a_a = math.atan2(A[1] - B[1], A[0] - B[0]) + 2 * math.pi
r = 0.5
arc = [(B[0] + r * math.cos(a_c + (a_a - a_c) * k / 40), B[1] + r * math.sin(a_c + (a_a - a_c) * k / 40))
       for k in range(41)]
sc.p.line(arc, TEXT, 1.4, None, 0.85)
sc.reg_poly(arc, 60)
for Q in (A, B, C, D):
    sc.dot(Q, TEXT, 4.2)
sc.label(A, "A(-1, -5)", ("s",))
sc.label(B, "B(2, 1)", ("e",))
sc.label(C, "C(1, 5)", ("n",))
sc.label(D, "D(-2, -1)", ("w",))
sc.edge_label(A, C, S(104), toward=D, color=BASE, size=13.5, ts=(0.19, 0.15, 0.23))
sc.edge_label(B, D, S(20), away=C, color=PRACTICE, size=13.5, ts=(0.3, 0.25, 0.35, 0.2))
sc.label(B, "∠$B$ ≠ 90°", ("se", "ne"), 13, TEXT, gap=22, math_mode=False)
sc.emit("alistirma-dikdortgen-mi",
        "Köşegenler eşit değildir (&#8730;104 &#8800; &#8730;20) ve <em>B</em> açısı dik değildir; "
        "<em>ABCD</em> bir dikdörtgen değildir.",
        "Parallelogram A(-1,-5), B(2,1), C(1,5), D(-2,-1) with unequal diagonals root 104 and root 20")

# ============================================================ alistirma-orta-noktalar-2
from_midpoints("alistirma-orta-noktalar-2", (-4, 10), (-9, 5), 37, (9, 0), (-3, 4), (1, -8),
               (("ne", "se"), ("nw",), ("s",)), (("n",), ("w",), ("e",)),
               "Kenar orta noktaları (3, 2), (&#8722;1, &#8722;2) ve (5, &#8722;4) olan üçgenin köşeleri "
               "<em>P</em><sub>1</sub>(9, 0), <em>P</em><sub>2</sub>(&#8722;3, 4) ve "
               "<em>P</em><sub>3</sub>(1, &#8722;8)'dir.",
               "Triangle P1(9,0), P2(-3,4), P3(1,-8) with its side midpoints and the dashed medial triangle",
               evens(-4, 10), evens(-9, 5))


# ---------------------------------------------------------------------------
for name, content in OUT.items():
    with open(OUT_DIR / f"{PREFIX}{name}.md", "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
print(f"generated {len(OUT)} figures:", ", ".join(OUT))
