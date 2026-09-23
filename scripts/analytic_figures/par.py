# -*- coding: utf-8 -*-
"""
Figures for the "Parabol" chapter of Analitik Geometri
(dersler/analitik-geometri/parabol.qmd).

The figures are NOT produced at build time. Run

    python scripts/analytic_figures/par.py
    python scripts/center_figures.py "analytic-par-*.md" --keep-width
    python scripts/check_figure_labels.py "scripts/_figures/analytic-par-*.md"

and paste each scripts/_figures/analytic-par-<name>.md block into the .qmd.
Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box: a figure that illustrates a
definition sits directly below that box.

Every drawing uses one scale on both axes, so parabolas, ellipses and right
angles look true. Labels are placed by a small collision-avoiding placer
(Pan.label and friends): each label tries its preferred positions and takes
the first one that touches no drawn line, point or other label. Axis numbers
that would touch something are left out. Anything that could not be placed
cleanly is reported on the console.

Colours: the conic itself is THEORY; the focus and the directrix of a
parabola are PRACTICE so that they stand out; other lines use BASE/REMARK.
Captions are Turkish (they are shown on the site); aria labels are ASCII.
"""
import io
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, WIDE, TEXT, BG, THEORY, PRACTICE, BASE, REMARK  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "analytic-par-"
OUT = {}

CW, ASC, DESC = 0.56, 0.78, 0.22       # same text-box model as check_figure_labels.py
NAME, NOTE, AXIS, TICK = 13.5, 12.5, 13, 11
PI = math.pi
DASH = "6 4"
UPRIGHT = set("ΔΓΘΛΣΦΨΩ")


# ---------------------------------------------------------------------------
# text markup
# ---------------------------------------------------------------------------
def markup(s, size):
    """Mini markup -> (svg text content, estimated width in px).

    'P_1' and 'x_{0}' give subscripts. Letter runs of length one or two
    (x, F, ep) and all-capital runs are variables and set in italic; longer
    words (cos, elips) and Greek capitals stay upright.
    """
    out, width, i = [], 0.0, 0
    sub = round(max(11.0, size * 0.8), 1)
    while i < len(s):
        c = s[i]
        if c == "_":
            if s[i + 1] == "{":
                j = s.index("}", i)
                t, i = s[i + 2:j], j + 1
            else:
                t, i = s[i + 1], i + 2
            inner, _ = markup(t, sub)
            out.append(f'<tspan font-size="{sub}" dy="4">{inner}</tspan><tspan dy="-4">&#8203;</tspan>')
            width += len(t) * CW * sub
            continue
        if c.isalpha():
            j = i
            while j < len(s) and s[j].isalpha() and s[j] not in UPRIGHT:
                j += 1
            if j == i:              # an upright Greek capital
                out.append(c)
                width += CW * size
                i += 1
                continue
            word = s[i:j]
            if len(word) <= 2 or word.isupper():
                out.append("".join(f'<tspan font-style="italic">{ch}</tspan>' for ch in word))
            else:
                out.append(word)
            width += len(word) * CW * size
            i = j
            continue
        out.append({"<": "&lt;", ">": "&gt;", "&": "&amp;"}.get(c, c))
        width += CW * size
        i += 1
    return "".join(out), width


def has_sub(s):
    return "_" in s


# rough advance widths (em) of the serif text face, for right-aligned edge labels
_W = {" ": 0.25, "=": 0.6, "+": 0.6, "−": 0.6, "(": 0.36, ")": 0.36, ",": 0.26, ".": 0.26,
      ":": 0.28, "/": 0.38, "²": 0.36, "δ": 0.5, "<": 0.6, ">": 0.6}


def real_width(s, size):
    w = 0.0
    for ch in s:
        if ch in _W:
            w += _W[ch]
        elif ch.isdigit():
            w += 0.55
        elif ch.isupper():
            w += 0.68
        else:
            w += 0.5
    return w * size


# ---------------------------------------------------------------------------
# geometry helpers
# ---------------------------------------------------------------------------
def seg_hits_rect(p, q, r):
    """Liang-Barsky: does segment pq meet rectangle r = (x0, y0, x1, y1)?"""
    x0, y0, x1, y1 = r
    dx, dy = q[0] - p[0], q[1] - p[1]
    t0, t1 = 0.0, 1.0
    for pp, qq in ((-dx, p[0] - x0), (dx, x1 - p[0]), (-dy, p[1] - y0), (dy, y1 - p[1])):
        if abs(pp) < 1e-12:
            if qq < 0:
                return False
        else:
            t = qq / pp
            if pp < 0:
                t0 = max(t0, t)
            else:
                t1 = min(t1, t)
            if t0 > t1:
                return False
    return True


def rect_overlap(a, b):
    w = min(a[2], b[2]) - max(a[0], b[0])
    h = min(a[3], b[3]) - max(a[1], b[1])
    return max(w, 0) * max(h, 0)


def pol(r, a, c=(0.0, 0.0)):
    return (c[0] + r * math.cos(a), c[1] + r * math.sin(a))


def arc_pts(c, r, a0, a1, n=None):
    n = n or max(24, int(abs(a1 - a0) * 40))
    return [(c[0] + r * math.cos(a0 + (a1 - a0) * k / n), c[1] + r * math.sin(a0 + (a1 - a0) * k / n))
            for k in range(n + 1)]


def lin(a, b, n=200):
    return [a + (b - a) * k / n for k in range(n + 1)]


def par_x(p2, vx, vy, y0, y1, sgn=1):
    """(y - vy)^2 = sgn * p2 * (x - vx), sampled over y in [y0, y1]."""
    return [(vx + sgn * (y - vy) ** 2 / p2, y) for y in lin(y0, y1)]


def par_y(p2, vx, vy, x0, x1, sgn=1):
    """(x - vx)^2 = sgn * p2 * (y - vy), sampled over x in [x0, x1]."""
    return [(x, vy + sgn * (x - vx) ** 2 / p2) for x in lin(x0, x1)]


def ellipse(cx, cy, a, b, n=240):
    return [(cx + a * math.cos(2 * PI * k / n), cy + b * math.sin(2 * PI * k / n)) for k in range(n + 1)]


def hyp_branch(cx, cy, a, b, side, y0, y1):
    return [(cx + side * a * math.sqrt(1 + ((y - cy) / b) ** 2), y) for y in lin(y0, y1)]


def mid(a, b):
    return ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)


# ---------------------------------------------------------------------------
# figure and panel with collision bookkeeping
# ---------------------------------------------------------------------------
class Fig:
    def __init__(self, W, H):
        self.W, self.H = W, H
        self.panels, self.segs, self.dots, self.boxes = [], [], [], []

    def panel(self, x0, y0, xr, yr, ppu):
        p = Pan(self, x0, y0, (xr[1] - xr[0]) * ppu, (yr[1] - yr[0]) * ppu, xr, yr)
        self.panels.append(p)
        return p

    def cost(self, box, pad=2.5):
        x0, y0, x1, y1 = box
        c = 0.0
        if x0 < 4 or y0 < 4 or x1 > self.W - 4 or y1 > self.H - 4:
            c += 1000
        ib = (x0 - pad, y0 - pad, x1 + pad, y1 + pad)
        for poly, w in self.segs:
            for a, b in zip(poly, poly[1:]):
                if seg_hits_rect(a, b, ib):
                    c += 100 * w
                    break
        for b in self.boxes:
            if rect_overlap(ib, b[:4]) > 0:
                c += 300
        for (cx, cy, r) in self.dots:
            if rect_overlap(ib, (cx - r - 1, cy - r - 1, cx + r + 1, cy + r + 1)) > 0:
                c += 250
        return c

    def audit(self, name):
        for b in self.boxes:
            ib = (b[0] + 0.5, b[1] + 0.5, b[2] - 0.5, b[3] - 0.5)
            for poly, w in self.segs:
                if w < 0.5:
                    continue
                if any(seg_hits_rect(a, c, ib) for a, c in zip(poly, poly[1:])):
                    print(f"  WARN {name}: label '{b[4]}' touches a line")
                    break

    def out(self, name, caption, aria, css="ders-grafik"):
        for p in self.panels:
            p.flush_numbers()
        self.audit(name)
        OUT[name] = figure(self.W, self.H, self.panels, caption, css, aria)


def equal_fig(xr, yr, ppu, margin=(60, 50, 60, 50)):
    """One equal-aspect panel with margins (left, top, right, bottom) in px."""
    l, t, r, b = margin
    W = (xr[1] - xr[0]) * ppu + l + r
    H = (yr[1] - yr[0]) * ppu + t + b
    f = Fig(round(W), round(H))
    return f, f.panel(l, t, xr, yr, ppu)


class Pan(Plot):
    def __init__(self, fig, x0, y0, w, h, xr, yr):
        super().__init__(x0, y0, w, h, xr, yr)
        self.fig = fig
        self.nums = []

    def px(self, pt):
        return (self.X(pt[0]), self.Y(pt[1]))

    def ppu(self):
        return self.w / (self.xmax - self.xmin)

    # -- recorded marks --------------------------------------------------------
    def rec(self, pts, weight=1.0):
        self.fig.segs.append(([self.px(q) for q in pts], weight))

    def line(self, pts, color=THEORY, width=1.9, dash=None, opacity=1.0, weight=1.0):
        super().line(pts, color, width, dash, opacity)
        if weight > 0:
            self.rec(pts, weight)

    def seg(self, a, b, color=THEORY, width=1.9, dash=None, opacity=1.0, weight=1.0):
        self.line([a, b], color, width, dash, opacity, weight)

    def arrow(self, p0, p1, color=THEORY, width=1.9, head=8.0, dash=None, opacity=1.0, weight=1.0):
        super().arrow(p0, p1, color, width, head, dash, opacity)
        if weight > 0:
            self.rec([p0, p1], weight)

    def dot(self, pt, color=TEXT, r=4.2):
        self.points([pt], color, r)
        X, Y = self.px(pt)
        self.fig.dots.append((X, Y, r))

    def hollow_dot(self, pt, color=TEXT, r=4.2):
        X, Y = self.px(pt)
        self.add(f'<circle cx="{X:.1f}" cy="{Y:.1f}" r="{r}" fill="{BG}" stroke="{color}" stroke-width="1.7"/>')
        self.fig.dots.append((X, Y, r))

    @staticmethod
    def _unit(A, B):
        dx, dy = B[0] - A[0], B[1] - A[1]
        n = math.hypot(dx, dy) or 1.0
        return dx / n, dy / n

    def right_angle(self, v, a, b, s=11, color=TEXT, opacity=0.8):
        """Right-angle square at v between the directions v->a and v->b (s px)."""
        V = self.px(v)
        ua = self._unit(V, self.px(a))
        ub = self._unit(V, self.px(b))
        p1 = (V[0] + s * ua[0], V[1] + s * ua[1])
        p2 = (p1[0] + s * ub[0], p1[1] + s * ub[1])
        p3 = (V[0] + s * ub[0], V[1] + s * ub[1])
        self.add(f'<path d="M{p1[0]:.1f},{p1[1]:.1f} L{p2[0]:.1f},{p2[1]:.1f} L{p3[0]:.1f},{p3[1]:.1f}" '
                 f'fill="none" stroke="{color}" stroke-width="1.2" opacity="{opacity}"/>')
        self.fig.segs.append(([p1, p2, p3], 1.0))

    def eq_tick(self, a, b, n=1, color=TEXT, length=12.0, width=1.5):
        """n short strokes across the middle of segment ab (equal-length marks)."""
        A, B = self.px(a), self.px(b)
        ux, uy = self._unit(A, B)
        nx, ny = -uy, ux
        M = ((A[0] + B[0]) / 2, (A[1] + B[1]) / 2)
        h = length / 2
        for k in range(n):
            off = (k - (n - 1) / 2) * 4.5
            cx, cy = M[0] + ux * off, M[1] + uy * off
            p, q = (cx - nx * h, cy - ny * h), (cx + nx * h, cy + ny * h)
            self.add(f'<line x1="{p[0]:.1f}" y1="{p[1]:.1f}" x2="{q[0]:.1f}" y2="{q[1]:.1f}" '
                     f'stroke="{color}" stroke-width="{width}"/>')
            self.fig.segs.append(([p, q], 1.0))

    def angle(self, c, a0, a1, r, color=TEXT, width=1.4, opacity=0.9):
        self.line(arc_pts(c, r, a0, a1), color, width, None, opacity)

    # -- axes ------------------------------------------------------------------
    def cart_axes(self, xr, yr, xl="X", yl="Y", step=1, opacity=0.6, xnums=(), ynums=(),
                  xl_pos=("e", "se", "ne"), yl_pos=("n", "nw", "ne")):
        """Arrowed axes from xr[0] to xr[1] and yr[0] to yr[1]; ticks every `step`;
        the numbers in xnums/ynums are written at the end, where they are free."""
        self.arrow((xr[0], 0), (xr[1], 0), TEXT, 1.2, 8, opacity=opacity)
        self.arrow((0, yr[0]), (0, yr[1]), TEXT, 1.2, 8, opacity=opacity)
        parts = []
        if step:
            for k in range(math.ceil(xr[0] / step), math.floor((xr[1] - 0.3) / step) + 1):
                if k:
                    X, Y = self.X(k * step), self.Y(0)
                    parts.append(f"M{X:.1f},{Y - 3.5:.1f} L{X:.1f},{Y + 3.5:.1f}")
                    self.fig.segs.append(([(X, Y - 3.5), (X, Y + 3.5)], 0.4))
            for k in range(math.ceil(yr[0] / step), math.floor((yr[1] - 0.3) / step) + 1):
                if k:
                    X, Y = self.X(0), self.Y(k * step)
                    parts.append(f"M{X - 3.5:.1f},{Y:.1f} L{X + 3.5:.1f},{Y:.1f}")
                    self.fig.segs.append(([(X - 3.5, Y), (X + 3.5, Y)], 0.4))
            self.add(f'<path d="{" ".join(parts)}" stroke="{TEXT}" stroke-width="1.1" opacity="{opacity}"/>')
        if xl:
            self.label(xr[1], 0, xl, xl_pos, gap=8, size=AXIS)
        if yl:
            self.label(0, yr[1], yl, yl_pos, gap=8, size=AXIS)
        self.nums += [("x", t) for t in xnums] + [("y", t) for t in ynums]

    def flush_numbers(self):
        ox, oy = self.X(0), self.Y(0)
        drawn = []
        for axis, t in self.nums:
            s = f"{t:g}".replace("-", "−")
            w = len(s) * CW * TICK
            if axis == "x":
                X = self.X(t)
                spots = [(X, oy + 16, "middle"), (X, oy - 7, "middle")]
            else:
                Y = self.Y(t) + 4
                spots = [(ox - 7, Y, "end"), (ox + 7, Y, "start")]
            for X, Y, anchor in spots:
                x0 = X - w / 2 if anchor == "middle" else X - w if anchor == "end" else X
                box = (x0, Y - ASC * TICK, x0 + w, Y + DESC * TICK)
                if self.fig.cost(box, 2.0) == 0:
                    drawn.append(f'<text x="{X:.1f}" y="{Y:.1f}" text-anchor="{anchor}">{s}</text>')
                    self.fig.boxes.append(box + (s,))
                    break
            else:
                print(f"  note: axis number {axis}={s} left out")
        if drawn:
            self.add(f'<g fill="{TEXT}" font-size="{TICK}" opacity="0.75">' + "".join(drawn) + "</g>")
        self.nums = []

    # -- labels ----------------------------------------------------------------
    def _box(self, pos, ax, ay, w, h, g):
        k = 0.72 * g
        if pos == "e":
            return (ax + g, ay - h / 2, ax + g + w, ay + h / 2), "start"
        if pos == "w":
            return (ax - g - w, ay - h / 2, ax - g, ay + h / 2), "end"
        if pos == "n":
            return (ax - w / 2, ay - g - h, ax + w / 2, ay - g), "middle"
        if pos == "s":
            return (ax - w / 2, ay + g, ax + w / 2, ay + g + h), "middle"
        if pos == "ne":
            return (ax + k, ay - k - h, ax + k + w, ay - k), "start"
        if pos == "nw":
            return (ax - k - w, ay - k - h, ax - k, ay - k), "end"
        if pos == "se":
            return (ax + k, ay + k, ax + k + w, ay + k + h), "start"
        if pos == "sw":
            return (ax - k - w, ay + k, ax - k, ay + k + h), "end"
        raise ValueError(pos)

    def _place(self, cands, text):
        best = None
        for box, anchor in cands:
            c = self.fig.cost(box)
            if best is None or c < best[0]:
                best = (c, box, anchor)
            if c == 0:
                break
        if best[0] > 0:
            print(f"  note: label '{text}' placed with cost {best[0]:.0f}")
        return best[1], best[2]

    def _draw_text(self, box, anchor, s, size, color, bold=False, edge=False):
        inner, _ = markup(s, size)
        x0, y0, x1, y1 = box
        base = y0 + ASC * size
        x = {"start": x0, "end": x1, "middle": (x0 + x1) / 2}[anchor]
        if anchor == "end" and edge:
            # a right-aligned label at the left edge of the drawing: write it
            # start-anchored at its real left end, so that the 0.56 em estimate
            # of check_figure_labels.py grows to the right, not out of the
            # viewBox that center_figures.py crops to the drawn content
            x, anchor = x1 - real_width(s, size), "start"
        weight = ' font-weight="600"' if bold else ""
        self.add(f'<text x="{x:.1f}" y="{base:.1f}" fill="{color}" font-size="{size}" '
                 f'text-anchor="{anchor}"{weight}>{inner}</text>')
        self.fig.boxes.append((x0, y0, x1, y1, s))

    def _wh(self, s, size):
        _, w = markup(s, size)
        return w, size * (ASC + DESC) + (3 if has_sub(s) else 0)

    def label(self, x, y, s, prefs=("ne", "nw", "se", "sw", "n", "s", "e", "w"), gap=7, size=NAME,
              color=TEXT, bold=False, leader=False, edge=False):
        """Label near data point (x, y); tries prefs with growing gaps, keeps the first clean spot.

        A pref may also be ('c', X, Y): a box centred on the data point (X, Y)."""
        w, h = self._wh(s, size)
        ax, ay = self.X(x), self.Y(y)
        cands = []
        for pos in prefs:
            if isinstance(pos, tuple):
                X, Y = self.X(pos[1]), self.Y(pos[2])
                cands.append(((X - w / 2, Y - h / 2, X + w / 2, Y + h / 2), "middle"))
                continue
            for g in (gap, gap + 4, gap + 9, gap + 15):
                cands.append(self._box(pos, ax, ay, w, h, g))
        box, anchor = self._place(cands, s)
        self._draw_text(box, anchor, s, size, color, bold, edge)
        if leader:
            self._leader((ax, ay), box, color)
        return box

    def _leader(self, P, box, color):
        cx = min(max(P[0], box[0]), box[2])
        cy = min(max(P[1], box[1]), box[3])
        ux, uy = self._unit(P, (cx, cy))
        a = (P[0] + ux * 6, P[1] + uy * 6)
        b = (cx - ux * 3, cy - uy * 3)
        self.add(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{color}" '
                 f'stroke-width="0.9" opacity="0.6"/>')

    def at(self, x, y, s, size=NOTE, color=TEXT, bold=False, anchor="middle"):
        """Label centred on a data point, no placement search (titles, notes)."""
        w, h = self._wh(s, size)
        X, Y = self.X(x), self.Y(y)
        if anchor == "middle":
            box = (X - w / 2, Y - h / 2, X + w / 2, Y + h / 2)
        elif anchor == "start":
            box = (X, Y - h / 2, X + w, Y + h / 2)
        else:
            box = (X - w, Y - h / 2, X, Y + h / 2)
        if self.fig.cost(box) > 0:
            print(f"  note: fixed label '{s}' collides (cost {self.fig.cost(box):.0f})")
        self._draw_text(box, anchor, s, size, color, bold)

    def along(self, a, b, s, side=1, t=0.5, gap=6, size=NOTE, color=TEXT,
              ts=(0, 0.1, -0.1, 0.2, -0.2, 0.3, -0.3)):
        """Label beside segment ab: side=+1 left of a->b (on screen), -1 right."""
        w, h = self._wh(s, size)
        A, B = self.px(a), self.px(b)
        ux, uy = self._unit(A, B)
        nx, ny = uy * side, -ux * side
        cands = []
        for dt in ts:
            tt = t + dt
            if not 0.05 <= tt <= 0.95:
                continue
            Mx, My = A[0] + (B[0] - A[0]) * tt, A[1] + (B[1] - A[1]) * tt
            for g in (gap, gap + 4, gap + 9):
                d = g + abs(nx) * w / 2 + abs(ny) * h / 2
                X, Y = Mx + nx * d, My + ny * d
                cands.append(((X - w / 2, Y - h / 2, X + w / 2, Y + h / 2), "middle"))
        box, anchor = self._place(cands, s)
        self._draw_text(box, anchor, s, size, color)

    def angle_label(self, c, a0, a1, r, s, size=NOTE, color=TEXT, gap=5, fs=(0, 0.12, -0.12, 0.25, -0.25)):
        w, h = self._wh(s, size)
        C = self.px(c)
        rp = r * self.ppu()
        cands = []
        for f in fs:
            t = (a0 + a1) / 2 + f * (a1 - a0)
            ux, uy = math.cos(t), -math.sin(t)
            ext = abs(ux) * w / 2 + abs(uy) * h / 2
            for g in (gap, gap + 4, gap + 9):
                d = rp + g + ext
                X, Y = C[0] + ux * d, C[1] + uy * d
                cands.append(((X - w / 2, Y - h / 2, X + w / 2, Y + h / 2), "middle"))
        box, anchor = self._place(cands, s)
        self._draw_text(box, anchor, s, size, color)


def origin(p, prefs=("sw", "se", "nw", "s", "w")):
    p.label(0, 0, "O", prefs, gap=6)


def focus(p, pt, s="F", prefs=("se", "sw", "s", "ne", "nw"), gap=9, size=NAME, leader=False):
    p.dot(pt, PRACTICE, 4.6)
    return p.label(*pt, s, prefs, gap=gap, size=size, color=PRACTICE, leader=leader)


def directrix(p, a, b, width=2.0):
    p.seg(a, b, PRACTICE, width, "7 5")


# ============================================================ parabol-ogeleri
TILT = math.radians(5)
PP = 1.2                       # parameter of the drawn parabola


def rot(u, v):
    return (u * math.cos(TILT) - v * math.sin(TILT), u * math.sin(TILT) + v * math.cos(TILT))


f, p = equal_fig((-1.55, 3.05), (-2.65, 2.85), 118, (60, 40, 60, 40))
A, F, H = rot(0, 0), rot(PP / 2, 0), rot(-PP / 2, 0)
P = rot(1.9 ** 2 / (2 * PP), 1.9)
K = rot(-PP / 2, 1.9)
p.seg(rot(-1.45, 0), rot(2.95, 0), TEXT, 1.2, "3 4", 0.55)
directrix(p, rot(-PP / 2, -2.55), rot(-PP / 2, 2.6), 2.2)
p.line([rot(v * v / (2 * PP), v) for v in lin(-2.45, 2.45)], THEORY, 2.5)
p.seg(P, F, BASE, 2.0)
p.seg(P, K, BASE, 2.0, "6 4")
p.right_angle(K, P, H, 11)
p.eq_tick(H, A, 1)
p.eq_tick(A, F, 1)
p.eq_tick(P, K, 2, BASE)
p.eq_tick(P, F, 2, BASE)
p.dot(H, TEXT)
p.dot(A, THEORY)
p.dot(P, TEXT)
p.dot(K, TEXT)
focus(p, F, "F", ("s", "se", "sw"))
p.label(*H, "H", ("sw", "nw", "w", "s"))
p.label(*A, "A", ("s", "sw", "se", "n"))
p.label(*P, "P", ("ne", "e", "n"))
p.label(*K, "K", ("nw", "w", "sw"))
p.label(*rot(-PP / 2, -2.55), "Δ", ("s", "sw", "se"), size=NAME + 1, color=PRACTICE)
p.label(*rot(2.8, 0), "asal eksen", ("s", "se", "n"), gap=6, size=NOTE)
f.out("parabol-ogeleri",
      "Parabolün öğeleri: odak <em>F</em>, doğrultman Δ, köşe <em>A</em>. Her <em>P</em> noktası için "
      "|<em>PF</em>| = |<em>PK</em>|; köşe <em>HF</em> parçasının orta noktasıdır.",
      aria="A parabol with focus F, directrix Delta, vertex A as midpoint of HF, and a point P "
           "with equal distances PF and PK")

# ============================================================ standart-y
f, p = equal_fig((-4.3, 4.3), (-2.25, 4.3), 64, (70, 40, 90, 40))
p.cart_axes((-4.2, 4.2), (-2.15, 4.2))
directrix(p, (-4.1, -1), (4.1, -1))
p.line(par_y(4, 0, 0, -3.6, 3.6), THEORY, 2.5)
P, Hh, F = (1.6, 0.64), (1.6, -1.0), (0.0, 1.0)
p.seg(P, F, BASE, 2.2)
p.seg(P, Hh, BASE, 2.2)
p.right_angle(Hh, P, (4, -1), 10)
p.eq_tick(P, F, 2, BASE)
p.eq_tick(P, Hh, 2, BASE)
p.dot(P)
p.dot(Hh)
p.dot((0, -1), PRACTICE, 3.6)
origin(p, ("se", "sw"))
focus(p, F, "F(0, p/2)", ("nw", "w", "n"))
p.label(*P, "P(x, y)", ("e", "se", "ne"))
p.label(*Hh, "H", ("s", "se", "sw"))
p.label(0, -1, "(0, −p/2)", ("sw", "s", "nw"), color=PRACTICE)
p.label(4.1, -1, "Δ: y = −p/2", ("n", "ne", "e", "s"), size=NOTE, color=PRACTICE)
p.label(3.3, 3.3 ** 2 / 4, "x² = 2py", ("e", "se", "w"), size=NOTE, color=THEORY)
f.out("standart-y",
      "Asal ekseni <em>Y</em>-ekseni olan parabol: |<em>PF</em>| = |<em>PH</em>| koşulu "
      "<em>x</em>² = 2<em>py</em> denklemine denktir.",
      aria="Parabola x2 = 2py with focus F(0, p/2), directrix y = -p/2 and a point P(x, y) with PF = PH")

# ============================================================ dort-konum
PPU4, GAPX, GAPY = 46, 96, 78
SIDE = 6.8 * PPU4
f = Fig(round(40 + 2 * SIDE + GAPX + 40), round(46 + 2 * SIDE + GAPY + 20))
panels = [
    ("x² = 2py", lambda: par_y(4, 0, 0, -3.0, 3.0), (0, 1), ((-3.1, -1), (3.1, -1)), (3.1, -1)),
    ("x² = −2py", lambda: par_y(4, 0, 0, -3.0, 3.0, -1), (0, -1), ((-3.1, 1), (3.1, 1)), (3.1, 1)),
    ("y² = 2px", lambda: par_x(4, 0, 0, -3.0, 3.0), (1, 0), ((-1, -3.1), (-1, 3.1)), (-1, -3.1)),
    ("y² = −2px", lambda: par_x(4, 0, 0, -3.0, 3.0, -1), (-1, 0), ((1, -3.1), (1, 3.1)), (1, -3.1)),
]
for k, (ttl, curve, Fp, (da, db), dl) in enumerate(panels):
    x0 = 40 + (k % 2) * (SIDE + GAPX)
    y0 = 46 + (k // 2) * (SIDE + GAPY)
    p = f.panel(x0, y0, (-3.4, 3.4), (-3.4, 3.4), PPU4)
    p.cart_axes((-3.3, 3.3), (-3.3, 3.3), opacity=0.5)
    directrix(p, da, db)
    p.line(curve(), THEORY, 2.4)
    origin(p, ("sw", "se", "nw", "ne"))
    focus(p, Fp, "F", ("se", "ne", "sw", "nw", "e", "w", "s", "n"))
    p.label(*dl, "Δ", ("s", "e", "w", "se", "sw", "n"), size=NAME + 0.5, color=PRACTICE)
    p.at(0, 3.4 + 26 / PPU4, ttl, NAME + 0.5, TEXT, bold=True)
f.out("dort-konum",
      "Köşesi başlangıç noktasında olan parabolün dört konumu (<em>p</em> = 2): birinci dereceden geçen "
      "değişken asal ekseni söyler, işaret açılma yönünü belirler.",
      aria="Four panels: parabolas x2 = 2py, x2 = -2py, y2 = 2px, y2 = -2px with focus F and directrix Delta",
      css=WIDE)

# ============================================================ x2-12y
f, p = equal_fig((-9.8, 9.9), (-4.3, 8.4), 28.5, (70, 40, 70, 40))
p.cart_axes((-9.7, 9.8), (-4.2, 8.3), step=3, xnums=(-9, -6, -3, 3, 6, 9), ynums=(-3, 3, 6))
directrix(p, (-9.6, -3), (9.6, -3))
p.line(par_y(12, 0, 0, -9, 9), THEORY, 2.5)
p.seg((-6, 3), (6, 3), TEXT, 1.2, "4 4", 0.7)
p.hollow_dot((-6, 3))
p.hollow_dot((6, 3))
origin(p, ("sw", "se"))
focus(p, (0, 3), "F(0, 3)", ("ne", "nw", "n"))
p.label(-6, 3, "(−6, 3)", ("w", "sw", "nw"))
p.label(6, 3, "(6, 3)", ("e", "se", "ne"))
p.label(9.6, -3, "Δ: y = −3", ("n", "nw", "s"), size=NOTE, color=PRACTICE)
p.label(7.5, 7.5 ** 2 / 12, "x² = 12y", ("e", "se"), size=NOTE, color=THEORY)
f.out("x2-12y",
      "<em>x</em>² = 12<em>y</em>: köşe <em>O</em>, odak <em>F</em>(0, 3), doğrultman <em>y</em> = −3; "
      "odak hizasındaki kirişin uzunluğu 2<em>p</em> = 12.",
      aria="Parabola x2 = 12y with focus F(0, 3), directrix y = -3 and the focal chord from (-6, 3) to (6, 3)")

# ============================================================ y2-8x
f, p = equal_fig((-4.4, 9.6), (-9.2, 9.5), 36, (60, 40, 90, 40))
p.cart_axes((-4.3, 9.5), (-9.1, 9.4), step=2, xnums=(2, 4, 6, 8), ynums=(-8, -6, -4, -2, 2, 4, 6, 8))
directrix(p, (-2, -9.0), (-2, 9.0))
p.line(par_x(8, 0, 0, -8.5, 8.5), THEORY, 2.5)
p.seg((2, -4), (2, 4), TEXT, 1.2, "4 4", 0.7)
p.hollow_dot((2, 4))
p.hollow_dot((2, -4))
p.dot((8, 8), TEXT, 3.8)
p.dot((8, -8), TEXT, 3.8)
origin(p, ("sw", "nw"))
focus(p, (2, 0), "F(2, 0)", ("se", "ne", "s"))
p.label(2, 4, "(2, 4)", ("e", "se", "ne"))
p.label(2, -4, "(2, −4)", ("e", "ne", "se"))
p.label(8, 8, "(8, 8)", ("e", "se"))
p.label(8, -8, "(8, −8)", ("e", "ne"))
p.label(-2, -9.0, "Δ: x = −2", ("s", "sw", "se"), size=NOTE, color=PRACTICE)
p.label(*par_x(8, 0, 0, 6.4, 6.4)[0], "y² = 8x", ("nw", "w", "n"), size=NOTE, color=THEORY)
f.out("y2-8x",
      "<em>y</em>² = 8<em>x</em>: köşe <em>O</em>, odak <em>F</em>(2, 0), doğrultman <em>x</em> = −2.",
      aria="Parabola y2 = 8x opening to the right with focus F(2, 0), directrix x = -2 and points (2, 4), (2, -4), (8, 8), (8, -8)")

# ============================================================ iki-noktadan
f, p = equal_fig((-1.8, 4.4), (-3.35, 3.45), 86, (60, 40, 110, 40))
p.cart_axes((-1.7, 4.3), (-3.25, 3.35), xnums=(1, 2, 3, 4), ynums=(-3, -2, -1, 1, 2, 3))
directrix(p, (-0.5, -3.2), (-0.5, 3.2))
p.line(par_x(2, 0, 0, -2.8, 2.8), THEORY, 2.5)
p.seg((2, -2), (2, 2), TEXT, 1.2, "4 4", 0.7)
p.dot((2, -2), BASE, 4.8)
p.dot((2, 2), BASE, 4.8)
origin(p, ("nw", "sw"))
focus(p, (0.5, 0), "F(1/2, 0)", ("se", "s", "ne"))
p.label(2, 2, "P_2(2, 2)", ("e", "se", "ne"), color=BASE)
p.label(2, -2, "P_1(2, −2)", ("e", "ne", "se"), color=BASE)
p.label(-0.5, -3.2, "Δ: x = −1/2", ("s", "sw", "se"), size=NOTE, color=PRACTICE)
p.label(3.5, math.sqrt(7), "y² = 2x", ("nw", "n", "w"), size=NOTE, color=THEORY)
f.out("iki-noktadan",
      "<em>P</em><sub>1</sub> ile <em>P</em><sub>2</sub> <em>X</em>-eksenine göre simetrik olduğundan asal "
      "eksen <em>X</em>-eksenidir; parabol <em>y</em>² = 2<em>x</em>.",
      aria="Parabola y2 = 2x through P1(2, -2) and P2(2, 2) with focus F(1/2, 0) and directrix x = -1/2")

# ============================================================ kose-sayisal
S6 = math.sqrt(6)
f, p = equal_fig((-1.3, 5.4), (-4.35, 3.5), 80, (60, 40, 150, 40))
p.cart_axes((-1.2, 5.3), (-4.25, 3.4), xnums=(-1, 1, 2, 3, 4, 5), ynums=(-4, -3, -2, -1, 1, 2, 3))
p.seg((-1.15, -3), (5.25, -3), BASE, 1.6, "4 4")
p.seg((2, -4.2), (2, 3.3), BASE, 1.6, "4 4")
directrix(p, (-1.15, -3.25), (5.25, -3.25), 1.9)
p.line(par_y(1, 2, -3, 2 - S6, 2 + S6), THEORY, 2.5)
p.hollow_dot((2 - math.sqrt(3), 0))
p.hollow_dot((2 + math.sqrt(3), 0))
p.dot((2, -3), TEXT)
origin(p, ("nw", "sw"))
p.dot((2, -2.75), PRACTICE, 3.6)
p.label(2, -2.75, "F(2, −11/4)", (("c", 2.7, -1.1),), size=NAME, color=PRACTICE, leader=True)
p.label(2, -3, "O′(2, −3)", (("c", 0.75, -2.82),), leader=True)
p.label(5.25, -3, "X′", ("e", "ne"), size=AXIS, color=BASE)
p.label(2, 3.3, "Y′", ("ne", "n", "e"), size=AXIS, color=BASE)
p.label(5.25, -3.25, "Δ: y = −13/4", ("se", "s", "e"), size=NOTE, color=PRACTICE)
p.label(4.2, 4.2 ** 2 - 4 * 4.2 + 1, "y = x² − 4x + 1", ("e", "se"), size=NOTE, color=THEORY)
f.out("kose-sayisal",
      "Eksenleri köşe <em>O</em>′(2, −3)'e ötelemek denklemi <em>x</em>′² = <em>y</em>′ standart biçimine "
      "getirir; odak <em>F</em>(2, −11/4), doğrultman <em>y</em> = −13/4.",
      aria="Parabola y = x2 - 4x + 1 with vertex O'(2, -3), translated axes X' and Y', focus F(2, -11/4) "
           "and directrix y = -13/4")

# ============================================================ teget
f, p = equal_fig((-3.3, 5.4), (-3.6, 4.0), 62, (60, 40, 70, 40))
p.cart_axes((-3.2, 5.3), (-3.5, 3.9))
p.line(par_x(2, 0, 0, -3.1, 3.1), THEORY, 2.5)
p.seg((2, 2), (2, 0), TEXT, 1.2, "4 4", 0.7)
p.seg((-3, -0.5), (5, 3.5), BASE, 2.3)
p.hollow_dot((-2, 0), BASE)
p.hollow_dot((2, 0))
p.dot((2, 2), TEXT, 4.6)
origin(p, ("sw", "se"))
p.label(2, 2, "P(x_0, y_0)", ("nw", "n", "w"))
p.label(-2, 0, "(−x_0, 0)", ("s", "sw", "se"), color=BASE)
p.label(2, 0, "(x_0, 0)", ("s", "se", "sw"))
p.label(-3, -0.5, "T", ("s", "sw", "w", "n"), size=NAME + 0.5, color=BASE)
p.label(*par_x(2, 0, 0, -2.7, -2.7)[0], "y² = 2px", ("se", "e", "s"), size=NOTE, color=THEORY)
f.out("teget",
      "<em>y</em>² = 2<em>px</em> parabolünün <em>P</em>(<em>x</em><sub>0</sub>, <em>y</em><sub>0</sub>) "
      "noktasındaki teğeti <em>y</em><sub>0</sub><em>y</em> = <em>p</em>(<em>x</em> + <em>x</em><sub>0</sub>); "
      "teğet <em>X</em>-eksenini (−<em>x</em><sub>0</sub>, 0)'da keser (çizimde <em>p</em> = 1, <em>P</em>(2, 2)).",
      aria="Parabola y2 = 2px with the tangent T at P(x0, y0) meeting the x axis at (-x0, 0)")

# ============================================================ teget-y2-8x
f, p = equal_fig((-3.4, 7.4), (-7.3, 7.7), 42, (60, 40, 110, 40))
p.cart_axes((-3.3, 7.3), (-7.2, 7.6), step=2, xnums=(-2, 2, 4, 6), ynums=(-6, -4, -2, 2, 4, 6))
p.line(par_x(8, 0, 0, -7, 7), THEORY, 2.5)
p.seg((-3, -1), (5, 7), BASE, 2.3)
p.hollow_dot((-2, 0), BASE)
p.dot((2, 4), TEXT, 4.6)
origin(p, ("se", "sw"))
focus(p, (2, 0), "F", ("se", "s", "ne"))
p.label(2, 4, "P(2, 4)", ("se", "e", "nw"))
p.label(-2, 0, "(−2, 0)", ("nw", "sw", "n"), color=BASE)
p.label(5, 7, "y = x + 2", ("e", "se", "ne"), size=NOTE, color=BASE)
p.label(*par_x(8, 0, 0, -6, -6)[0], "y² = 8x", ("se", "e"), size=NOTE, color=THEORY)
f.out("teget-y2-8x",
      "<em>y</em>² = 8<em>x</em> parabolünün <em>P</em>(2, 4) noktasındaki teğeti <em>y</em> = <em>x</em> + 2.",
      aria="Parabola y2 = 8x with the tangent y = x + 2 at P(2, 4), meeting the x axis at (-2, 0)")

# ============================================================ dogru-uc-durum
f, p = equal_fig((-3.3, 7.4), (-5.3, 7.3), 52, (150, 40, 60, 40))
p.cart_axes((-3.2, 7.3), (-5.2, 7.2), xnums=(2, 4, 6), ynums=(-4, -2, 2, 4, 6))
p.line(par_x(4, 0, 0, -5.0, 5.3), THEORY, 2.5)
p.seg((-3, -3), (5, 5), BASE, 2.2)
p.seg((-3, -2), (5, 6), PRACTICE, 2.2)
p.seg((-3, -1), (5, 7), REMARK, 2.2)
p.dot((0, 0), BASE, 4.6)
p.dot((4, 4), BASE, 4.6)
p.dot((1, 2), PRACTICE, 4.8)
origin(p, ("se", "s"))
p.label(1, 2, "T", ("se", "e", "s"), size=NAME + 0.5, color=PRACTICE)
p.label(-3, -3, "y = x: δ > 0", ("w", "sw", "nw"), size=NOTE, color=BASE, edge=True)
p.label(-3, -2, "y = x + 1: δ = 0", ("w", "sw", "nw"), size=NOTE, color=PRACTICE, edge=True)
p.label(-3, -1, "y = x + 2: δ < 0", ("w", "nw", "sw"), size=NOTE, color=REMARK, edge=True)
p.label(*par_x(4, 0, 0, -4.2, -4.2)[0], "y² = 4x", ("se", "e"), size=NOTE, color=THEORY)
f.out("dogru-uc-durum",
      "<em>y</em>² = 4<em>x</em> parabolü ve eğimi 1 olan üç doğru: δ = 4<em>p</em>(<em>p</em> − 2<em>mn</em>) "
      "= 8(2 − 2<em>n</em>) işaretine göre kesen, teğet (değme noktası <em>T</em>(1, 2)) ve kesmeyen doğru.",
      aria="Parabola y2 = 4x and three parallel lines of slope 1: y = x cuts it twice, y = x + 1 touches it "
           "at T(1, 2), y = x + 2 misses it",
      css=WIDE)

# ============================================================ kutupsal-uc-durum
f, p = equal_fig((-6.3, 6.6), (-5.4, 5.6), 50, (40, 40, 60, 30))
p.seg((-6.25, 0), (6.5, 0), TEXT, 1.1, None, 0.5)
p.seg((0, -4.6), (0, 4.6), TEXT, 1.1, "3 4", 0.55)
p.seg((-2, -5.3), (-2, 5.3), TEXT, 2.0, "7 5", 0.9)
ea, eb = 4 / 3, 2 / math.sqrt(3)
ha, hb = 4 / 3, 4 / math.sqrt(3)
p.line(ellipse(2 / 3, 0, ea, eb), THEORY, 2.5)
p.line(par_x(4, -1, 0, -5.2, 5.2), PRACTICE, 2.5)
p.line(hyp_branch(-8 / 3, 0, ha, hb, 1, -5.2, 5.2), BASE, 2.5)
p.line(hyp_branch(-8 / 3, 0, ha, hb, -1, -5.2, 5.2), BASE, 2.0, "6 5", 0.6)
p.dot((0, 0), TEXT, 5.0)
for y, col in ((1, THEORY), (2, PRACTICE), (4, BASE)):
    p.dot((0, y), col, 4.0)
p.label(0, 0, "F", ("sw", "se", "s"), size=NAME + 1)
p.label(-2, 5.3, "Δ", ("n", "ne", "nw"), size=NAME + 1)
p.label(0, 4, "ep = 4", ("e", "se", "ne"), size=NOTE, color=BASE)
p.label(0, 2, "ep = 2", ("e", "se", "ne"), size=NOTE, color=PRACTICE)
p.label(0, 1, "ep = 1", ("se", "e", "sw"), size=NOTE, color=THEORY)
p.label(*pol(1, math.radians(35), (2 / 3, 0)), "e = 1/2 (elips)", (("c", 2.75, 1.35),), size=NOTE, color=THEORY)
p.label(*par_x(4, -1, 0, 4.6, 4.6)[0], "e = 1 (parabol)", ("w", "nw", "e", "se"), size=NOTE, color=PRACTICE)
p.label(*hyp_branch(-8 / 3, 0, ha, hb, 1, 5.0, 5.0)[0], "e = 2 (hiperbol)", ("e", "ne", "se"), size=NOTE,
        color=BASE)
p.label(*hyp_branch(-8 / 3, 0, ha, hb, -1, 3.2, 3.2)[0], "öbür kol", ("e", "ne", "se", "w"), size=NOTE,
        color=BASE)
f.out("kutupsal-uc-durum",
      "Aynı odak <em>F</em> ve doğrultman Δ ile üç konik (<em>p</em> = 2): <em>e</em> &lt; 1 elips, "
      "<em>e</em> = 1 parabol, <em>e</em> &gt; 1 hiperbol. Kutupsal denklem Δ'nın <em>F</em> tarafında kalan "
      "kısmı verir; hiperbolün öbür kolu (kesikli) Δ'nın öbür yanındadır.",
      aria="Three conics with the same focus F and directrix Delta: ellipse e = 1/2, parabola e = 1, "
           "hyperbola e = 2 whose second branch lies beyond Delta",
      css=WIDE)

# ============================================================ kutupsal-turetim
R3 = math.sqrt(3)
f, p = equal_fig((-3.4, 4.5), (-3.3, 4.45), 68, (60, 40, 60, 40))
p.cart_axes((-3.3, 4.4), (-3.2, 4.35))
directrix(p, (-2, -3.1), (-2, 4.2))
p.line(par_x(4, -1, 0, -3.0, 4.0), THEORY, 2.5)
P, Hh, T = (2, 2 * R3), (-2, 2 * R3), (0, 2 * R3)
p.seg(Hh, P, TEXT, 1.4, "5 4", 0.85)
p.seg((0, 0), P, BASE, 2.3)
p.right_angle(T, P, (0, 0), 10)
p.angle((0, 0), 0, PI / 3, 0.55, TEXT, 1.4)
p.dot(P, TEXT, 4.6)
p.dot(Hh, TEXT, 4.0)
p.dot(T, TEXT, 3.6)
focus(p, (0, 0), "O = F", ("se", "s", "sw"))
p.label(*P, "P(x, y) = P(r, θ)", ("se", "e", "ne"))
p.label(*Hh, "H", ("w", "nw", "sw"))
p.label(*T, "T", ("nw", "n", "ne"))
p.label(-2, -3.1, "Δ", ("s", "se", "sw"), size=NAME + 1, color=PRACTICE)
p.along(Hh, T, "p", 1, gap=5)
p.along(T, P, "r cos θ", 1, gap=5)
p.along((0, 0), P, "r", 1, t=0.55, gap=5, size=NAME, color=BASE)
p.angle_label((0, 0), 0, PI / 3, 0.55, "θ", NAME)
f.out("kutupsal-turetim",
      "Kutup odakta: |<em>PF</em>| = <em>r</em> ve |<em>PH</em>| = <em>p</em> + <em>r</em> cos <em>θ</em>. "
      "|<em>PF</em>| = <em>e</em>|<em>PH</em>| koşulu <em>r</em> = <em>ep</em>/(1 − <em>e</em> cos <em>θ</em>) "
      "verir (çizimde <em>p</em> = 2, <em>e</em> = 1).",
      aria="Polar coordinates with the pole at the focus: PF = r and PH = p + r cos theta for a point P of "
           "the parabola")

# ============================================================ kutupsal-elips
f, p = equal_fig((-9.4, 9.6), (-6.2, 6.4), 36, (60, 40, 60, 40))
p.cart_axes((-9.3, 9.5), (-6.1, 6.3), step=2, xnums=(-6, -4, 2, 4, 6), ynums=(-2, 6))
directrix(p, (-8, -6.0), (-8, 6.0))
p.line(ellipse(8 / 3, 0, 16 / 3, 8 / R3), THEORY, 2.5)
p.seg((0, 0), (0, 4), BASE, 2.2)
p.dot((0, 4), BASE, 4.0)
p.dot((16 / 3, 0), TEXT, 3.8)
p.hollow_dot((8 / 3, 0), TEXT, 3.8)
p.dot((-8 / 3, 0), TEXT, 4.2)
p.dot((8, 0), TEXT, 4.2)
focus(p, (0, 0), "F = O", ("sw", "s", "se"))
p.label(16 / 3, 0, "F′", ("s", "se", "sw"))
p.label(8 / 3, 0, "M(8/3, 0)", ("s", "se", "sw"))
p.label(-8 / 3, 0, "(−8/3, 0)", ("nw", "sw", "w"))
p.label(8, 0, "(8, 0)", ("ne", "se", "e"))
p.label(0, 2.7, "ep = 4", ("w", "e"), size=NOTE, color=BASE)
p.label(-8, 6.0, "Δ: x = −8", ("ne", "e", "n"), size=NOTE, color=PRACTICE)
p.label(*pol(1, math.radians(40), (0, 0)), "r = 16/(4 − 2 cos θ)", (("c", 7.6, 4.3),), size=NOTE, color=THEORY)
f.out("kutupsal-elips",
      "<em>r</em> = 16/(4 − 2 cos <em>θ</em>): <em>e</em> = 1/2, kutup sol odakta; kartezyen denklem "
      "3<em>x</em>² − 16<em>x</em> + 4<em>y</em>² = 64.",
      aria="Ellipse 3x2 - 16x + 4y2 = 64 with the pole at its left focus F = O, center M(8/3, 0), "
           "vertices (-8/3, 0) and (8, 0) and directrix x = -8",
      css=WIDE)

# ============================================================ kutupsal-hiperbol
f, p = equal_fig((-9.4, 10.4), (-6.3, 6.5), 34, (60, 40, 60, 40))
p.cart_axes((-9.3, 10.3), (-6.2, 6.4), step=2, xnums=(-8, -6, -4, -2, 2, 6, 8), ynums=(-6, -4, -2, 2, 4, 6))
p.seg((-7.6, -5.7), (7.6, 5.7), TEXT, 1.1, "4 4", 0.5, weight=0.3)
p.seg((-7.6, 5.7), (7.6, -5.7), TEXT, 1.1, "4 4", 0.5, weight=0.3)
directrix(p, (3.2, -6.0), (3.2, 6.0))
p.line(hyp_branch(0, 0, 4, 3, 1, -6, 6), THEORY, 2.6)
p.line(hyp_branch(0, 0, 4, 3, -1, -6, 6), THEORY, 2.2, None, 0.45)
p.arrow((5, 0), (7.4, 0), TEXT, 2.6, 10)
p.seg((5, 0), (5, 2.25), BASE, 2.2)
p.dot((5, 2.25), BASE, 4.2)
p.dot((4, 0), TEXT, 4.2)
p.dot((-5, 0), TEXT, 3.8)
focus(p, (5, 0), "F(5, 0)", ("se", "s"))
p.label(-5, 0, "F′(−5, 0)", ("s", "sw", "se"))
p.label(4, 0, "(4, 0)", (("c", 5.15, -1.2),), size=NOTE, leader=True)
p.label(5, 1.125, "r = 9/4", ("e",), size=NOTE, color=BASE)
p.label(3.2, 6.0, "Δ: x = 16/5", ("nw", "n", "w"), size=NOTE, color=PRACTICE)
p.label(*hyp_branch(0, 0, 4, 3, 1, 4.2, 4.2)[0], "r = 9/(4 − 5 cos θ)", ("e", "se"), size=NOTE, color=THEORY)
f.out("kutupsal-hiperbol",
      "Kutup sağ odakta: <em>r</em> = 9/(4 − 5 cos <em>θ</em>) sağ kolu verir; sol kol (soluk) doğrultmanın "
      "öbür yanındadır. Ok kutupsal ekseni gösterir.",
      aria="Hyperbola x2/16 - y2/9 = 1 with the pole at the right focus F(5, 0), directrix x = 16/5, "
           "the polar axis arrow and the point (5, 9/4)",
      css=WIDE)

# ============================================================ odak-ii
f, p = equal_fig((-7.4, 6.3), (-4.5, 12.7), 32, (60, 40, 110, 40))
p.cart_axes((-7.3, 6.2), (-4.4, 12.6), step=2, xnums=(-6, -4, 2, 4, 6), ynums=(-4, -2, 2, 6, 8, 10, 12))
p.seg((-7.2, 4), (6.1, 4), BASE, 1.6, "4 4")
p.seg((-2, -4.3), (-2, 12.4), BASE, 1.6, "4 4")
directrix(p, (-5, -4.3), (-5, 12.4))
p.line(par_x(12, -2, 4, -4, 12), THEORY, 2.5)
p.seg((1, -2), (1, 10), TEXT, 1.2, "4 4", 0.7)
p.hollow_dot((1, -2))
p.hollow_dot((1, 10))
p.dot((-2, 4), TEXT)
origin(p, ("se", "sw"))
focus(p, (1, 4), "F(1, 4)", ("se", "ne", "s"))
p.label(-2, 4, "O′(−2, 4)", ("nw", "sw", "n"))
p.label(6.1, 4, "X′", ("e", "ne"), size=AXIS, color=BASE)
p.label(-2, 12.4, "Y′", ("ne", "n", "nw"), size=AXIS, color=BASE)
p.label(-5, -4.3, "Δ: x = −5", ("s", "sw", "se"), size=NOTE, color=PRACTICE)
p.label(*par_x(12, -2, 4, -2.6, -2.6)[0], "y² − 8y − 12x − 8 = 0", ("e", "se", "ne"), size=NOTE, color=THEORY)
f.out("odak-ii",
      "Köşe <em>O</em>′(−2, 4)'e öteleme denklemi <em>y</em>′² = 12<em>x</em>′ yapar; odak <em>F</em>(1, 4), "
      "doğrultman <em>x</em> = −5.",
      aria="Parabola (y - 4)2 = 12(x + 2) with vertex O'(-2, 4), translated axes, focus F(1, 4) and directrix x = -5")

# ============================================================ odak-iii
f, p = equal_fig((-13.4, 7.5), (-7.3, 7.4), 27, (60, 40, 70, 40))
p.cart_axes((-13.3, 7.4), (-7.2, 7.3), step=2, xnums=(-12, -10, -8, -6, -4, 2, 4, 6), ynums=(-6, -4, -2, 2, 4, 6))
p.seg((-13.2, 1), (7.3, 1), BASE, 1.6, "4 4")
p.seg((-3, -7.1), (-3, 7.1), BASE, 1.6, "4 4")
directrix(p, (-13.2, 5), (7.3, 5))
p.line(par_y(16, -3, 1, -12, 6, -1), THEORY, 2.5)
p.seg((-11, -3), (5, -3), TEXT, 1.2, "4 4", 0.7)
p.hollow_dot((-11, -3))
p.hollow_dot((5, -3))
p.dot((-3, 1), TEXT)
origin(p, ("se", "sw"))
focus(p, (-3, -3), "F(−3, −3)", ("sw", "se", "s"))
p.label(-3, 1, "O′(−3, 1)", ("ne", "nw", "n"))
p.label(-11, -3, "(−11, −3)", ("w", "sw", "nw"))
p.label(5, -3, "(5, −3)", ("e", "se", "ne"))
p.label(7.3, 1, "X′", ("e", "ne"), size=AXIS, color=BASE)
p.label(-3, 7.1, "Y′", ("ne", "n", "nw"), size=AXIS, color=BASE)
p.label(7.3, 5, "Δ: y = 5", ("n", "nw", "s"), size=NOTE, color=PRACTICE)
p.label(*par_y(16, -3, 1, -9, -9, -1)[0], "x² + 6x + 16y − 7 = 0", ("nw", "w", "n"), size=NOTE, color=THEORY, edge=True)
f.out("odak-iii",
      "Köşe <em>O</em>′(−3, 1)'e öteleme denklemi <em>x</em>′² = −16<em>y</em>′ yapar; parabol aşağı açılır, "
      "odak <em>F</em>(−3, −3), doğrultman <em>y</em> = 5.",
      aria="Parabola (x + 3)2 = -16(y - 1) opening downward with vertex O'(-3, 1), focus F(-3, -3) and directrix y = 5")

# ============================================================ dogru-125
R3b = 2 * math.sqrt(3)
f, p = equal_fig((-4.4, 9.5), (-6.4, 7.4), 48, (80, 40, 60, 40))
p.cart_axes((-4.3, 9.4), (-6.3, 7.3), step=2, xnums=(-4, -2, 2, 4, 6, 8), ynums=(-6, -4, -2, 4, 6))
p.line(par_x(4, 0, 0, -6, 6), THEORY, 2.5)
p.seg((-4, -2), (5.2, 7.2), REMARK, 2.2)
p.seg((-4, 0), (8.5, 6.25), PRACTICE, 2.2)
p.seg((-4, 2), (8.5, 2), TEXT, 2.0, None, 0.8)
p.seg((-4, 6), (8.2, -6.2), BASE, 2.2)
p.dot((4, 4), PRACTICE, 4.8)
p.dot((1, 2), TEXT, 4.4)
p.dot((2 - R3b + 2, -2 + R3b), BASE, 4.4)
p.dot((2 + R3b + 2, -2 - R3b), BASE, 4.4)
p.hollow_dot((0, 2), TEXT, 4.4)
p.label(4, 4, "T(4, 4)", ("se", "e", "s"), color=PRACTICE)
p.label(1, 2, "(1, 2)", ("s", "se", "sw"))
p.label(0, 2, "(0, 2)", (("c", -1.7, 2.5),), leader=True)
p.label(5.2, 7.2, "m = 1", ("e", "se", "w"), size=NOTE, color=REMARK)
p.label(8.5, 6.25, "m = 1/2", ("se", "e", "s"), size=NOTE, color=PRACTICE)
p.label(8.5, 2, "m = 0", ("e", "ne", "se"), size=NOTE, color=TEXT)
p.label(8.2, -6.2, "m = −1", ("e", "ne", "se"), size=NOTE, color=BASE)
p.label(*par_x(4, 0, 0, -3, -3)[0], "y² = 4x", ("sw", "w"), size=NOTE, color=THEORY)
f.out("dogru-125",
      "<em>y</em> = <em>mx</em> + 2 doğruları: <em>m</em> &gt; 1/2 kesmez, <em>m</em> = 1/2 teğet, "
      "<em>m</em> &lt; 1/2 (<em>m</em> ≠ 0) iki noktada keser; <em>m</em> = 0 eksene paraleldir ve tek "
      "noktada keser.",
      aria="Parabola y2 = 4x and the lines y = mx + 2 for m = 1, 1/2, 0, -1 through (0, 2); m = 1/2 touches "
           "at T(4, 4)",
      css=WIDE)


# ---------------------------------------------------------------------------
for name, content in OUT.items():
    with io.open(OUT_DIR / f"{PREFIX}{name}.md", "w", encoding="utf-8", newline="\n") as fh:
        fh.write(content)
print(f"generated {len(OUT)} figures:", ", ".join(OUT))
