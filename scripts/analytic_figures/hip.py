# -*- coding: utf-8 -*-
"""
Figures for the "Hiperbol" chapter of Analitik Geometri
(dersler/analitik-geometri/hiperbol.qmd).

The figures are NOT produced at build time. Run

    python scripts/analytic_figures/hip.py
    python scripts/center_figures.py "analytic-hip-*.md" --keep-width
    python scripts/check_figure_labels.py "scripts/_figures/analytic-hip-*.md"

and paste each scripts/_figures/analytic-hip-<name>.md block into the .qmd.
Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box: a figure that illustrates a
definition sits directly below that box.

Conventions: one scale on both axes, so the curves, right angles and circles
look true. Hyperbolas are drawn with both branches in the "theory" color,
asymptotes dashed. Labels go through the collision-avoiding placer of ote.py;
axis numbers that would touch anything are dropped at finish().

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
PREFIX = "analytic-hip-"
OUT = {}

CW, ASC, DESC = 0.56, 0.78, 0.22       # same text-box model as check_figure_labels.py
NAME, NOTE, AXIS = 13.5, 12.5, 13      # font sizes: point names, annotations, axis names
D = math.radians
PI = math.pi


# ---------------------------------------------------------------------------
# text markup
# ---------------------------------------------------------------------------
def markup(s, size):
    """Mini markup -> (svg text content, estimated width in px).

    'P_1' and 'x_{12}' give subscripts; single letters (Latin or Greek) are set
    in italic, longer words (cos, sin, Alan) upright.
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
            while j < len(s) and s[j].isalpha():
                j += 1
            word = s[i:j]
            if len(word) == 1 or word.isupper():
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


def rw(s):
    """Realistic advance width of s in em (Georgia-like), for laying out pieces of one label."""
    table = {"(": 0.36, ")": 0.36, ",": 0.26, " ": 0.26, "π": 0.56, "/": 0.4, "−": 0.6}
    return sum(table.get(c, 0.55) for c in s)


def has_sub(s):
    return "_" in s


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


def clip_line(pt, d, rect):
    """Part of the infinite line pt + t d inside rect = (xmin, xmax, ymin, ymax), data units."""
    xmin, xmax, ymin, ymax = rect
    t0, t1 = -1e9, 1e9
    for p0, dd, lo, hi in ((pt[0], d[0], xmin, xmax), (pt[1], d[1], ymin, ymax)):
        if abs(dd) < 1e-12:
            if not lo <= p0 <= hi:
                return None
            continue
        a, b = (lo - p0) / dd, (hi - p0) / dd
        t0, t1 = max(t0, min(a, b)), min(t1, max(a, b))
    if t0 >= t1:
        return None
    return (pt[0] + t0 * d[0], pt[1] + t0 * d[1]), (pt[0] + t1 * d[0], pt[1] + t1 * d[1])


def pol(r, a):
    return (r * math.cos(a), r * math.sin(a))


def arc_pts(c, r, a0, a1, n=None):
    n = n or max(24, int(abs(a1 - a0) * 40))
    return [(c[0] + r * math.cos(a0 + (a1 - a0) * k / n), c[1] + r * math.sin(a0 + (a1 - a0) * k / n))
            for k in range(n + 1)]


# ---------------------------------------------------------------------------
# figure and panel with collision bookkeeping
# ---------------------------------------------------------------------------
class Fig:
    def __init__(self, W, H):
        self.W, self.H = W, H
        self.panels, self.segs, self.dots, self.boxes = [], [], [], []
        self.nums, self.axis_names = [], []

    def panel(self, x0, y0, xr, yr, ppu):
        p = Pan(self, x0, y0, (xr[1] - xr[0]) * ppu, (yr[1] - yr[0]) * ppu, xr, yr)
        self.panels.append(p)
        return p

    # -- collision model -----------------------------------------------------
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
        bad = 0
        for b in self.boxes:
            ib = (b[0] + 0.5, b[1] + 0.5, b[2] - 0.5, b[3] - 0.5)
            for poly, w in self.segs:
                if w < 0.5:
                    continue
                if any(seg_hits_rect(a, c, ib) for a, c in zip(poly, poly[1:])):
                    print(f"  WARN {name}: label '{b[4]}' touches a line")
                    bad += 1
                    break
        return bad

    def out(self, name, caption, aria, css="ders-grafik"):
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

    def ring(self, c, r, color=THEORY, width=1.9, dash=None, opacity=1.0, fill="none", weight=1.0):
        super().circle(c[0], c[1], r, color, width, dash, fill, opacity)
        if weight > 0:
            self.rec(arc_pts(c, r, 0, 2 * PI, 160), weight)

    def poly(self, pts, fill=THEORY, opacity=0.12, stroke="none", width=1.4, dash=None):
        self.polygon(pts, fill, opacity, stroke, width, dash)
        if stroke != "none":
            self.rec(list(pts) + [pts[0]])

    def dot(self, pt, color=TEXT, r=4.2):
        self.points([pt], color, r)
        X, Y = self.px(pt)
        self.fig.dots.append((X, Y, r))

    def hollow_dot(self, pt, color=TEXT, r=4.2):
        X, Y = self.px(pt)
        self.add(f'<circle cx="{X:.1f}" cy="{Y:.1f}" r="{r}" fill="{BG}" stroke="{color}" stroke-width="1.7"/>')
        self.fig.dots.append((X, Y, r))

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

    @staticmethod
    def _unit(A, B):
        dx, dy = B[0] - A[0], B[1] - A[1]
        n = math.hypot(dx, dy) or 1.0
        return dx / n, dy / n

    def angle(self, c, a0, a1, r, color=TEXT, width=1.4, head=False, dash=None, opacity=0.9):
        """Angle arc from a0 to a1 (radians, data orientation) with an optional arrowhead at a1."""
        rp = r * self.ppu()
        hl = 7.5
        if head:
            sgn = 1 if a1 > a0 else -1
            a1s = a1 - sgn * (hl * 0.85) / rp
            self.line(arc_pts(c, r, a0, a1s), color, width, dash, opacity)
            tip = self.px(pol_add(c, pol(r, a1)))
            base = self.px(pol_add(c, pol(r, a1 - sgn * hl / rp)))
            ux, uy = self._unit(base, tip)
            hw = hl * 0.45
            self.add(f'<polygon points="{tip[0]:.1f},{tip[1]:.1f} {tip[0] - ux * hl - uy * hw:.1f},'
                     f'{tip[1] - uy * hl + ux * hw:.1f} {tip[0] - ux * hl + uy * hw:.1f},'
                     f'{tip[1] - uy * hl - ux * hw:.1f}" fill="{color}" opacity="{opacity}"/>')
        else:
            self.line(arc_pts(c, r, a0, a1), color, width, dash, opacity)

    # -- axes ------------------------------------------------------------------
    def cart_axes(self, xr, yr, xl="X", yl="Y", ticks=True, opacity=0.6, xl_pos=("e", "se", "ne"),
                  yl_pos=("n", "nw", "ne")):
        self.arrow((xr[0], 0), (xr[1], 0), TEXT, 1.2, 8, opacity=opacity)
        self.arrow((0, yr[0]), (0, yr[1]), TEXT, 1.2, 8, opacity=opacity)
        if ticks:
            parts = []
            for k in range(math.ceil(xr[0]), math.floor(xr[1] - 0.25) + 1):
                if k:
                    X, Y = self.X(k), self.Y(0)
                    parts.append(f"M{X:.1f},{Y - 3.5:.1f} L{X:.1f},{Y + 3.5:.1f}")
                    self.fig.segs.append(([(X, Y - 3.5), (X, Y + 3.5)], 0.4))
            for k in range(math.ceil(yr[0]), math.floor(yr[1] - 0.25) + 1):
                if k:
                    X, Y = self.X(0), self.Y(k)
                    parts.append(f"M{X - 3.5:.1f},{Y:.1f} L{X + 3.5:.1f},{Y:.1f}")
                    self.fig.segs.append(([(X - 3.5, Y), (X + 3.5, Y)], 0.4))
            self.add(f'<path d="{" ".join(parts)}" stroke="{TEXT}" stroke-width="1.1" opacity="{opacity}"/>')
        if xl:
            self.label(xr[1], 0, xl, xl_pos, gap=8, size=AXIS)
        if yl:
            self.label(0, yr[1], yl, yl_pos, gap=8, size=AXIS)

    # -- labels ----------------------------------------------------------------
    def _box(self, pos, ax, ay, w, h, g):
        """Box (x0, y0, x1, y1) and text anchor for a compass position around pixel (ax, ay)."""
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

    def _draw_text(self, box, anchor, s, size, color, halo, bold=False, sub=False):
        inner, _ = markup(s, size)
        x0, y0, x1, y1 = box
        base = y0 + ASC * size + (0 if not sub else 0)
        x = {"start": x0, "end": x1, "middle": (x0 + x1) / 2}[anchor]
        if halo:
            self.add(f'<rect x="{x0 - 2:.1f}" y="{y0 - 1:.1f}" width="{x1 - x0 + 4:.1f}" height="{y1 - y0 + 2:.1f}" '
                     f'rx="3" fill="{BG}" opacity="0.88"/>')
        weight = ' font-weight="600"' if bold else ""
        self.add(f'<text x="{x:.1f}" y="{base:.1f}" fill="{color}" font-size="{size}" '
                 f'text-anchor="{anchor}"{weight}>{inner}</text>')
        self.fig.boxes.append((x0, y0, x1, y1, s))

    def _wh(self, s, size):
        _, w = markup(s, size)
        return w, size * (ASC + DESC) + (3 if has_sub(s) else 0)

    def label(self, x, y, s, prefs=("ne", "nw", "se", "sw", "n", "s", "e", "w"), gap=7, size=NAME,
              color=TEXT, halo=False, bold=False, leader=False):
        """Label near data point (x, y); tries prefs x growing gaps, keeps the first clean spot.

        A pref may also be ('c', X, Y): a box centred on pixel (X, Y)."""
        w, h = self._wh(s, size)
        ax, ay = self.X(x), self.Y(y)
        cands = []
        for pos in prefs:
            if isinstance(pos, tuple):
                X, Y = pos[1], pos[2]
                cands.append(((X - w / 2, Y - h / 2, X + w / 2, Y + h / 2), "middle"))
                continue
            for g in (gap, gap + 4, gap + 9, gap + 15):
                cands.append(self._box(pos, ax, ay, w, h, g))
        box, anchor = self._place(cands, s)
        self._draw_text(box, anchor, s, size, color, halo, bold, has_sub(s))
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

    def at(self, x, y, s, size=NOTE, color=TEXT, halo=False, bold=False, anchor="middle"):
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
        self._draw_text(box, anchor, s, size, color, halo, bold, has_sub(s))

    def along(self, a, b, s, side=1, t=0.5, gap=6, size=NOTE, color=TEXT, halo=False, ts=(0, 0.1, -0.1, 0.2, -0.2, 0.3, -0.3)):
        """Label beside segment ab: side=+1 left of a->b (on screen), -1 right."""
        w, h = self._wh(s, size)
        A, B = self.px(a), self.px(b)
        ux, uy = self._unit(A, B)
        nx, ny = uy * side, -ux * side        # screen-left normal for side=+1
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
        self._draw_text(box, anchor, s, size, color, halo, False, has_sub(s))

    def angle_label(self, c, a0, a1, r, s, side="out", size=NOTE, color=TEXT, gap=5,
                    fs=(0, 0.12, -0.12, 0.25, -0.25, 0.38, -0.38), halo=False):
        """Label for the angle arc of radius r at c between a0 and a1."""
        w, h = self._wh(s, size)
        C = self.px(c)
        rp = r * self.ppu()
        cands = []
        for f in fs:
            t = (a0 + a1) / 2 + f * (a1 - a0)
            ux, uy = math.cos(t), -math.sin(t)
            ext = abs(ux) * w / 2 + abs(uy) * h / 2
            for g in (gap, gap + 4, gap + 9):
                d = rp + g + ext if side == "out" else rp - g - ext
                if side == "in" and d < ext + 3:
                    continue
                X, Y = C[0] + ux * d, C[1] + uy * d
                cands.append(((X - w / 2, Y - h / 2, X + w / 2, Y + h / 2), "middle"))
        if not cands:
            return self.angle_label(c, a0, a1, r, s, "out", size, color, gap, fs, halo)
        box, anchor = self._place(cands, s)
        self._draw_text(box, anchor, s, size, color, halo, False, has_sub(s))

    def frac_label(self, x, y, head, num, den, tail, prefs, gap=7, size=NAME, color=TEXT, halo=True):
        """Label like '(3, π/3)' with the fraction set vertically: head + num/den + tail."""
        fsz = 12
        wh = rw(head) * size
        wf = max(rw(num), rw(den)) * fsz + 4
        wt = rw(tail) * size
        w, h = wh + wf + wt, 29.0
        # check_figure_labels.py measures the whole <text> at 0.56 em per character,
        # so the collision box is widened to that estimate
        w_est = (len(head) + len(tail)) * CW * size + (len(num) + len(den)) * CW * fsz
        ax, ay = self.X(x), self.Y(y)
        cands = []
        for pos in prefs:
            for g in (gap, gap + 4, gap + 9, gap + 15):
                b, a = self._box(pos, ax, ay, w, h, g)
                cands.append(((b[0], b[1], b[0] + max(w, w_est), b[3]), a))
        box, _ = self._place(cands, head + num + "/" + den + tail)
        x0, y0, _, y1 = box
        x1 = x0 + w
        cy = (y0 + y1) / 2
        bar = cy - 1
        base = bar + 4.4
        if halo:
            self.add(f'<rect x="{x0 - 2:.1f}" y="{y0:.1f}" width="{w + 4:.1f}" height="{h:.1f}" rx="3" '
                     f'fill="{BG}" opacity="0.88"/>')
        fx = x0 + wh + wf / 2
        hi, _ = markup(head, size)
        ni, _ = markup(num, fsz)
        di, _ = markup(den, fsz)
        ti, _ = markup(tail, size)
        self.add(f'<text fill="{color}" font-size="{size}" x="{x0:.1f}" y="{base:.1f}">{hi}'
                 f'<tspan x="{fx - rw(num) * fsz / 2:.1f}" y="{bar - 3:.1f}" font-size="{fsz}">{ni}</tspan>'
                 f'<tspan x="{fx - rw(den) * fsz / 2:.1f}" y="{bar + 12.2:.1f}" font-size="{fsz}">{di}</tspan>'
                 f'<tspan x="{x0 + wh + wf:.1f}" y="{base:.1f}">{ti}</tspan></text>')
        self.add(f'<line x1="{fx - wf / 2 + 1:.1f}" y1="{bar:.1f}" x2="{fx + wf / 2 - 1:.1f}" y2="{bar:.1f}" '
                 f'stroke="{color}" stroke-width="1"/>')
        self.fig.boxes.append((x0, y0, x1, y1, head + num + "/" + den + tail))


def pol_add(a, b):
    return (a[0] + b[0], a[1] + b[1])


def origin(p, prefs=("sw", "se", "nw", "s", "w")):
    """Dot and label at O. Asymptotes and axes often all meet at O, so after the
    compass positions the label also tries boxes centred at growing distances
    in the free wedges between them."""
    p.dot((0, 0), TEXT)
    X, Y = p.X(0), p.Y(0)
    cands = list(prefs)
    for r in (13, 17, 22, 28, 34):
        for ang in (-135, -45, -150, -30, 135, 45, -110, -70, 110, 70):
            cands.append(("c", X + r * math.cos(D(ang)), Y - r * math.sin(D(ang))))
    p.label(0, 0, "O", cands, gap=8)


DASH = "5 4"
THIN = 1.3

TICK = 11
NEW = PRACTICE             # new axes and every quantity measured in the new system
DASH_NEW = "7 5"
DOTTED = "2 3.5"
GUIDE = "4 4"
O = (0.0, 0.0)


# ---------------------------------------------------------------------------
# helpers of this chapter: axes with numbers, translated axes, label blocks
# ---------------------------------------------------------------------------
def fmt_num(t):
    s = f"{t:g}"
    return s.replace("-", "−")


def axes(p, nums=True, step=1, names=("X", "Y"), opacity=0.7, numbered=None):
    """Axes over the whole panel; ticks every `step`, numbers placed at finish().

    numbered: if given, only these tick values get a number."""
    p.arrow((p.xmin, 0), (p.xmax, 0), TEXT, 1.25, 8.5, opacity=opacity)
    p.arrow((0, p.ymin), (0, p.ymax), TEXT, 1.25, 8.5, opacity=opacity)
    if nums:
        parts = []
        for k in range(math.ceil(p.xmin / step), math.floor((p.xmax - 0.4 * step) / step) + 1):
            t = k * step
            if t:
                X, Y = p.X(t), p.Y(0)
                parts.append(f"M{X:.1f},{Y - 3.5:.1f} L{X:.1f},{Y + 3.5:.1f}")
                p.fig.segs.append(([(X, Y - 3.5), (X, Y + 3.5)], 0.4))
                if numbered is None or t in numbered:
                    p.fig.nums.append(("x", p, t))
        for k in range(math.ceil(p.ymin / step), math.floor((p.ymax - 0.4 * step) / step) + 1):
            t = k * step
            if t:
                X, Y = p.X(0), p.Y(t)
                parts.append(f"M{X - 3.5:.1f},{Y:.1f} L{X + 3.5:.1f},{Y:.1f}")
                p.fig.segs.append(([(X - 3.5, Y), (X + 3.5, Y)], 0.4))
                if numbered is None or t in numbered:
                    p.fig.nums.append(("y", p, t))
        p.add(f'<path d="{" ".join(parts)}" stroke="{TEXT}" stroke-width="1.1" opacity="{opacity}"/>')
    if names:
        p.fig.axis_names.append((p, (p.xmax, 0), names[0], ("e", "se", "ne"), TEXT))
        p.fig.axis_names.append((p, (0, p.ymax), names[1], ("n", "nw", "ne"), TEXT))


def new_axes(p, o, color=NEW, names=("X′", "Y′"), dash=DASH_NEW, width=1.7, xs=None, ys=None):
    """Translated axes through o: dashed, same directions as the old ones."""
    x0 = p.xmin if xs is None else xs[0]
    x1 = p.xmax if xs is None else xs[1]
    y0 = p.ymin if ys is None else ys[0]
    y1 = p.ymax if ys is None else ys[1]
    p.arrow((x0, o[1]), (x1, o[1]), color, width, 8.5, dash)
    p.arrow((o[0], y0), (o[0], y1), color, width, 8.5, dash)
    if names:
        p.fig.axis_names.append((p, (x1, o[1]), names[0], ("e", "ne", "se"), color))
        p.fig.axis_names.append((p, (o[0], y1), names[1], ("n", "ne", "nw"), color))


def name_axes(p):
    for q, (x, y), s, prefs, c in p.fig.axis_names:
        q.label(x, y, s, prefs, gap=8, size=AXIS, color=c)
    p.fig.axis_names.clear()


def dc(p, x, y):
    """Label candidate: a box centred on data point (x, y)."""
    return ("c", p.X(x), p.Y(y))


def along_out(p, a, b, s, away, color=TEXT, size=NOTE, t=0.5, gap=6, halo=False):
    """Label beside segment ab, on the side away from the data point `away`."""
    A, B, Q = p.px(a), p.px(b), p.px(away)
    ux, uy = p._unit(A, B)
    nx, ny = uy, -ux
    M = ((A[0] + B[0]) / 2, (A[1] + B[1]) / 2)
    side = -1 if nx * (Q[0] - M[0]) + ny * (Q[1] - M[1]) > 0 else 1
    p.along(a, b, s, side, t, gap, size, color, halo)


def block(p, x, y, lines, prefs, gap=8, size=NOTE, halo=False):
    """Several stacked lines [(text, color), ...] placed as one label near (x, y)."""
    ws = [markup(s, size)[1] for s, _ in lines]
    w, lh, h1 = max(ws), size * 1.3, size * (ASC + DESC)
    h = lh * (len(lines) - 1) + h1
    ax, ay = p.X(x), p.Y(y)
    cands = []
    for pos in prefs:
        if isinstance(pos, tuple):
            X, Y = pos[1], pos[2]
            cands.append(((X - w / 2, Y - h / 2, X + w / 2, Y + h / 2), "middle"))
            continue
        for g in (gap, gap + 4, gap + 9, gap + 15):
            cands.append(p._box(pos, ax, ay, w, h, g))
    box, anchor = p._place(cands, " / ".join(s for s, _ in lines))
    x0, y0, x1, _ = box
    for i, ((s, c), wi) in enumerate(zip(lines, ws)):
        top = y0 + i * lh
        if anchor == "start":
            lb = (x0, top, x0 + wi, top + h1)
        elif anchor == "end":
            lb = (x1 - wi, top, x1, top + h1)
        else:
            cx = (x0 + x1) / 2
            lb = (cx - wi / 2, top, cx + wi / 2, top + h1)
        p._draw_text(lb, anchor, s, size, c, halo)


def eq_ticks(p, a, b, n=2, color=TEXT):
    """Equal-length marks across the middle of segment ab."""
    A, B = p.px(a), p.px(b)
    ux, uy = p._unit(A, B)
    nx, ny = -uy, ux
    Mx, My = (A[0] + B[0]) / 2, (A[1] + B[1]) / 2
    parts = []
    for k in range(n):
        off = (k - (n - 1) / 2) * 5
        cx, cy = Mx + ux * off, My + uy * off
        a1, a2 = (cx - nx * 7, cy - ny * 7), (cx + nx * 7, cy + ny * 7)
        parts.append(f"M{a1[0]:.1f},{a1[1]:.1f} L{a2[0]:.1f},{a2[1]:.1f}")
        p.fig.segs.append(([a1, a2], 1.0))
    p.add(f'<path d="{" ".join(parts)}" stroke="{color}" stroke-width="1.6" stroke-linecap="round"/>')


def curve(p, pts, color=THEORY, width=2.2, dash=None):
    """Polyline clipped to the panel (runs of points inside the data rectangle)."""
    run = []
    for q in pts:
        if p.xmin <= q[0] <= p.xmax and p.ymin <= q[1] <= p.ymax:
            run.append(q)
        else:
            if len(run) > 1:
                p.line(run, color, width, dash)
            run = []
    if len(run) > 1:
        p.line(run, color, width, dash)


def lin(a, b, n):
    return [a + (b - a) * k / n for k in range(n + 1)]


def finish(f, name, caption, aria, css=None):
    """Place the axis numbers that do not collide with anything, then write the figure."""
    for axis, p, t in f.nums:
        s = fmt_num(t)
        w, h = len(s) * CW * TICK, TICK * (ASC + DESC)
        if axis == "x":
            X, Y = p.X(t), p.Y(0)
            box, anchor, tx = (X - w / 2, Y + 5, X + w / 2, Y + 5 + h), "middle", X
        else:
            X, Y = p.X(0), p.Y(t)
            box, anchor, tx = (X - 6 - w, Y - h / 2, X - 6, Y + h / 2), "end", X - 6
        pad = (box[0] - 1.5, box[1] - 1.5, box[2] + 1.5, box[3] + 1.5)
        clash = any(w_ >= 0.5 and any(seg_hits_rect(a, c, pad) for a, c in zip(poly, poly[1:]))
                    for poly, w_ in f.segs)
        clash = clash or any(rect_overlap(pad, b[:4]) > 0 for b in f.boxes)
        clash = clash or any(rect_overlap(pad, (cx - r, cy - r, cx + r, cy + r)) > 0 for cx, cy, r in f.dots)
        if clash:
            continue
        p.add(f'<text x="{tx:.1f}" y="{box[1] + ASC * TICK:.1f}" fill="{TEXT}" font-size="{TICK}" '
              f'text-anchor="{anchor}" opacity="0.75">{s}</text>')
    f.out(name, caption, aria, css or (WIDE if f.W > 620 else "ders-grafik"))




M_ = (40, 34, 50, 34)      # default margins (left, top, right, bottom)
S3 = math.sqrt(3)
ASYM = "6 5"               # dash of asymptotes
FAINT = 0.45               # opacity of faint helper lines


# ---------------------------------------------------------------------------
# helpers of this chapter
# ---------------------------------------------------------------------------
def hyp(p, a, b, m=(0.0, 0.0), span=(-3.0, 3.0), vertical=False, color=THEORY, width=2.4, n=240):
    """Both branches of a hyperbola with center m.

    Horizontal: (x - m1)^2/a^2 - (y - m2)^2/b^2 = 1, span is the y-range.
    Vertical:   (y - m2)^2/a^2 - (x - m1)^2/b^2 = 1, span is the x-range.
    Points outside the panel are dropped by curve()."""
    c0 = m[0] if vertical else m[1]
    t0, t1 = math.asinh((span[0] - c0) / b), math.asinh((span[1] - c0) / b)
    for s in (1, -1):
        pts = []
        for k in range(n + 1):
            t = t0 + (t1 - t0) * k / n
            if vertical:
                pts.append((m[0] + b * math.sinh(t), m[1] + s * a * math.cosh(t)))
            else:
                pts.append((m[0] + s * a * math.cosh(t), m[1] + b * math.sinh(t)))
        curve(p, pts, color, width)


def ell(p, a, b, color=THEORY, width=2.4, n=240):
    pts = [(a * math.cos(2 * PI * k / n), b * math.sin(2 * PI * k / n)) for k in range(n + 1)]
    p.line(pts, color, width)


def line_x(p, f, x0, x1, color=PRACTICE, width=2.0, dash=None, opacity=1.0, weight=1.0):
    """Graph of the linear function f on [x0, x1], cut to the panel."""
    k, c = f(1.0) - f(0.0), f(0.0)
    seg = clip_line((0.0, c), (1.0, k), (max(x0, p.xmin), min(x1, p.xmax), p.ymin, p.ymax))
    if seg:
        p.seg(seg[0], seg[1], color, width, dash, opacity, weight)
    return seg


def asymptotes(p, k, m=(0.0, 0.0), color=PRACTICE, width=1.6, opacity=1.0):
    """The two lines y - m2 = +-k (x - m1), cut to the panel; returns the two segments."""
    out = []
    for s in (1, -1):
        out.append(line_x(p, lambda x, s=s: m[1] + s * k * (x - m[0]), p.xmin, p.xmax,
                          color, width, ASYM, opacity))
    return out


def vseg(p, x, y0, y1, color, width=1.8, dash=None, opacity=1.0):
    p.seg((x, y0), (x, y1), color, width, dash, opacity)


def dots(p, pts, color=TEXT, r=4.2):
    for q in pts:
        p.dot(q, color, r)


def em(s):
    return f"<em>{s}</em>"


def e_sub(s, k):
    return f"<em>{s}</em><sub>{k}</sub>"


F1, F2, A1, A2 = e_sub("F", 1), e_sub("F", 2), e_sub("A", 1), e_sub("A", 2)
XX, YY = em("x"), em("y")


# ============================================================ tanim
f, p = equal_fig((-1, 9), (-1, 8), 48, M_)
axes(p, nums=True)
M = (4.0, 3.0)
P = (7.0, 3 + 2 * S3)
p.seg((0, 3), (8, 3), TEXT, 1.1, None, FAINT)
p.ring(M, 1.5, PRACTICE, 1.6)
hyp(p, 1.5, 2, M, (-0.6, 6.6))
p.seg(P, (6.5, 3), TEXT, 1.3)
p.seg(P, (1.5, 3), TEXT, 1.3)
name_axes(p)
origin(p)
pts = {"F_2": (1.5, 3), "A_2": (2.5, 3), "M": M, "A_1": (5.5, 3), "F_1": (6.5, 3)}
dots(p, pts.values())
p.dot(P, PRACTICE, 4.6)
for s, q in pts.items():
    p.label(*q, s, ("s", "sw", "se"), gap=6)
p.label(*P, "P(x, y)", ("ne", "e", "n"))
along_out(p, P, (1.5, 3), "|PF_2|", (6.5, 3), TEXT, NOTE, t=0.45)
along_out(p, P, (6.5, 3), "|PF_1|", (1.5, 3), TEXT, NOTE, t=0.55)
p.label(4 + 1.5 * math.cos(D(-60)), 3 + 1.5 * math.sin(D(-60)), "asal çember",
        (dc(p, 3.2, 0.75), dc(p, 4.6, 0.75), "s", "se"), size=NOTE, color=PRACTICE, leader=True)
finish(f, "tanim",
       f"Odakları {F1}, {F2} olan hiperbol: sağ kolun her {em('P')} noktasında "
       f"|{em('PF')}<sub>2</sub>| &#8722; |{em('PF')}<sub>1</sub>| = 2{em('a')}.",
       "Hyperbol with foci F1, F2, center M, vertices A1, A2 and the principal circle; "
       "a point P on the right branch joined to both foci")


# ============================================================ standart
f, p = equal_fig((-5, 5), (-3.5, 3.5), 52, M_)
axes(p, numbered={-4, 4, -3, 3})
hyp(p, 2, 1.5, span=(-3.2, 3.2))
name_axes(p)
origin(p)
dots(p, [(2, 0), (-2, 0), (2.5, 0), (-2.5, 0)])
p.label(2, 0, "A_1(a, 0)", ("sw", "s"), gap=6, size=NOTE)
p.label(-2, 0, "A_2(−a, 0)", ("se", "s"), gap=6, size=NOTE)
p.label(2.5, 0, "F_1(c, 0)", ("ne", "n"), gap=6, size=NOTE)
p.label(-2.5, 0, "F_2(−c, 0)", ("nw", "n"), gap=6, size=NOTE)
finish(f, "standart",
       f"Merkezi {em('O')}, asal ekseni {em('X')}-ekseni olan hiperbol: köşeler (&#177;{em('a')}, 0), "
       f"odaklar (&#177;{em('c')}, 0).",
       "Hyperbola x2/a2 - y2/b2 = 1 with both branches, vertices (+-a, 0) and foci (+-c, 0)")


# ============================================================ asimptot
f, p = equal_fig((-6, 6), (-4.5, 4.5), 54, M_)
axes(p, nums=False)
asymptotes(p, 0.75)
hyp(p, 2, 1.5, span=(-4, 4))
name_axes(p)
origin(p)
dots(p, [(2, 0), (-2, 0), (2.5, 0), (-2.5, 0)])
p.label(2, 0, "A_1", ("sw", "s"), gap=6)
p.label(-2, 0, "A_2", ("se", "s"), gap=6)
p.label(2.5, 0, "F_1", ("ne", "n"), gap=6)
p.label(-2.5, 0, "F_2", ("nw", "n"), gap=6)
p.label(5.2, 3.9, "y = (b/a)x", ("nw", "w", "n"), size=NOTE, color=PRACTICE)
p.label(5.2, -3.9, "y = −(b/a)x", ("sw", "w", "s"), size=NOTE, color=PRACTICE)
p.label(4.2, 0.75 * math.sqrt(4.2 ** 2 - 4), "y = (b/a)√(x² − a²)",
        (dc(p, 3.2, 3.9), dc(p, 2.6, 3.9), dc(p, 4.3, 1.0)), size=NOTE, color=THEORY, leader=True)
p.label(-4.2, -0.75 * math.sqrt(4.2 ** 2 - 4), "y = −(b/a)√(x² − a²)",
        (dc(p, -3.2, -3.9), dc(p, -2.6, -3.9), dc(p, -4.3, -1.0)), size=NOTE, color=THEORY, leader=True)
finish(f, "asimptot",
       "Kollar uzaklaştıkça merkezden geçen iki asimptota yaklaşır.",
       "Hyperbola x2/4 - y2/2.25 = 1 with its asymptotes y = +-(b/a)x dashed; the upper right and "
       "lower left pieces are labelled with their equations")


# ============================================================ yedek-eksen
f, p = equal_fig((-5, 5), (-3.5, 3.5), 52, M_)
axes(p, nums=False)
p.seg((-2, 0), (2, 0), BASE, 4.0, weight=0.3)
p.seg((0, -1.5), (0, 1.5), PRACTICE, 4.0, weight=0.3)
hyp(p, 2, 1.5, span=(-3.2, 3.2))
name_axes(p)
origin(p, ("sw", "nw", "w"))
dots(p, [(2, 0), (-2, 0), (2.5, 0), (-2.5, 0), (0, 1.5), (0, -1.5)])
p.label(2, 0, "A_1(a, 0)", ("sw", "s"), gap=6, size=NOTE)
p.label(-2, 0, "A_2(−a, 0)", ("se", "s"), gap=6, size=NOTE)
p.label(2.5, 0, "F_1(c, 0)", ("ne", "n"), gap=6, size=NOTE)
p.label(-2.5, 0, "F_2(−c, 0)", ("nw", "n"), gap=6, size=NOTE)
p.label(0, 1.5, "B_1(0, b)", ("e", "ne", "se"), gap=7, size=NOTE, color=PRACTICE)
p.label(0, -1.5, "B_2(0, −b)", ("e", "se", "ne"), gap=7, size=NOTE, color=PRACTICE)
finish(f, "yedek-eksen",
       f"Asal eksen uzunluğu 2{em('a')}, yedek eksen uzunluğu 2{em('b')}; {e_sub('B', 1)} ve {e_sub('B', 2)} "
       "hiperbolün üzerinde değildir.",
       "Hyperbola with the principal axis segment A2A1 of length 2a and the conjugate axis segment B1B2 "
       "of length 2b on the y-axis")


# ============================================================ ornek-cizim
f, p = equal_fig((-4.5, 4.5), (-4.5, 4.5), 56, M_)
axes(p)
p.poly([(-1, -S3), (1, -S3), (1, S3), (-1, S3)], THEORY, 0.0, TEXT, 1.1, "4 4")
asymptotes(p, S3)
hyp(p, 1, S3, span=(-4.3, 4.3))
name_axes(p)
origin(p, ("sw", "nw", "se"))
dots(p, [(1, 0), (-1, 0), (2, 0), (-2, 0), (2, 3), (2, -3)])
p.label(1, 0, "A_1", ("sw", "nw"), gap=6)
p.label(-1, 0, "A_2", ("se", "ne"), gap=6)
p.label(2, 0, "F_1(2, 0)", ("se", "ne", "s"), gap=6, size=NOTE)
p.label(-2, 0, "F_2(−2, 0)", ("sw", "nw", "s"), gap=6, size=NOTE)
p.label(2, 3, "(2, 3)", ("e", "se", "ne"), size=NOTE)
p.label(2, -3, "(2, −3)", ("e", "ne", "se"), size=NOTE)
p.label(4.5 / S3, 4.5, "y = √3x", ("w", "sw", "e"), gap=10, size=NOTE, color=PRACTICE)
p.label(-4.5 / S3, 4.5, "y = −√3x", ("e", "se", "w"), gap=10, size=NOTE, color=PRACTICE)
p.label(3.6, -2.2, "x² − y²/3 = 1", (dc(p, 3.55, -1.2), dc(p, 3.55, -0.8), "e"), size=NOTE, color=THEORY)
finish(f, "ornek-cizim",
       f"{XX}<sup>2</sup> &#8722; {YY}<sup>2</sup>/3 = 1 hiperbolü: köşeler (&#177;1, 0), odaklar (&#177;2, 0), "
       f"asimptotlar {YY} = &#177;&#8730;3{XX}.",
       "Hyperbola x2 - y2/3 = 1 with its basic rectangle, asymptotes y = +-sqrt3 x, vertices, foci "
       "and the points (2, 3), (2, -3)")


# ============================================================ dikey
f, p = equal_fig((-4.5, 4.5), (-5, 5), 56, M_)
axes(p, nums=False)
asymptotes(p, 4 / 3)
hyp(p, 2, 1.5, span=(-3.4, 3.4), vertical=True)
name_axes(p)
origin(p, ("sw", "se", "nw"))
dots(p, [(0, 2), (0, -2), (0, 2.5), (0, -2.5), (1.5, 0), (-1.5, 0)])
p.label(0, 2, "A_1(0, a)", ("se", "sw"), gap=6, size=NOTE)
p.label(0, -2, "A_2(0, −a)", ("ne", "nw"), gap=6, size=NOTE)
p.label(0, 2.5, "F_1(0, c)", ("e", "ne"), gap=7, size=NOTE)
p.label(0, -2.5, "F_2(0, −c)", ("se", "e"), gap=7, size=NOTE)
p.label(1.5, 0, "B_1(b, 0)", ("s", "se"), gap=7, size=NOTE)
p.label(-1.5, 0, "B_2(−b, 0)", ("s", "sw"), gap=7, size=NOTE)
p.label(3.6, 4.8, "y = (a/b)x", ("e", "se", "s"), size=NOTE, color=PRACTICE)
p.label(-3.6, 4.8, "y = −(a/b)x", ("w", "sw", "s"), size=NOTE, color=PRACTICE)
finish(f, "dikey",
       f"Odakları {em('Y')}-ekseninde olan hiperbol: kollar yukarı ve aşağı açılır.",
       "Hyperbola y2/4 - x2/2.25 = 1 opening up and down, with asymptotes y = +-(a/b)x, vertices "
       "(0, +-a), foci (0, +-c) and the conjugate axis ends (+-b, 0)")


# ============================================================ otelenmis
f, p = equal_fig((-3, 7), (-6, 4), 52, M_)
axes(p)
M = (2.0, -1.0)
S13 = math.sqrt(13)
new_axes(p, M, TEXT, ("X′", "Y′"), "5 4", 1.2)
asymptotes(p, 1.5, M)
hyp(p, 2, 3, M, (-5.5, 3.5))
name_axes(p)
origin(p, ("nw", "ne", "sw"))
dots(p, [M, (4, -1), (0, -1), (2 + S13, -1), (2 - S13, -1)])
p.label(*M, "M(2, −1)", (dc(p, 3.15, -1.33), "s"), gap=7)
p.label(4, -1, "A_1", ("se", "ne"), gap=6)
p.label(0, -1, "A_2", ("se", "ne"), gap=6)
p.label(2 + S13, -1, "F_1", ("s", "n"), gap=6)
p.label(2 - S13, -1, "F_2", ("s", "n"), gap=6)
p.label(16 / 3, 4, "y = 3x/2 − 4", ("e", "se", "s"), size=NOTE, color=PRACTICE, halo=False)
p.label(-4 / 3, 4, "y = −3x/2 + 2", ("w", "sw", "s"), size=NOTE, color=PRACTICE)
finish(f, "otelenmis",
       f"Merkezi {em('M')}(2, &#8722;1) olan hiperbol: öteleme ile {em('x')}′<sup>2</sup>/4 &#8722; "
       f"{em('y')}′<sup>2</sup>/9 = 1 olur.",
       "Hyperbola (x-2)2/4 - (y+1)2/9 = 1 with center M(2,-1), translated axes X', Y' and asymptotes "
       "y = 3x/2 - 4, y = -3x/2 + 2")


# ============================================================ ikizkenar
f, p = equal_fig((-5, 5), (-5, 5), 54, M_)
axes(p, nums=False)
p.poly([(-2, -2), (2, -2), (2, 2), (-2, 2)], THEORY, 0.0, TEXT, 1.1, "4 4")
asymptotes(p, 1.0)
hyp(p, 2, 2, span=(-4.5, 4.5))
p.right_angle((0, 0), (1, 1), (-1, 1), 12)
name_axes(p)
origin(p, ("s", "sw", "se"))
c = 2 * math.sqrt(2)
dots(p, [(2, 0), (-2, 0), (c, 0), (-c, 0)])
p.label(2, 0, "A_1", ("sw", "s"), gap=6)
p.label(-2, 0, "A_2", ("se", "s"), gap=6)
p.label(c, 0, "F_1", ("ne", "n"), gap=6)
p.label(-c, 0, "F_2", ("nw", "n"), gap=6)
p.label(4.9, 4.9, "y = x", ("w", "sw"), gap=10, size=NOTE, color=PRACTICE)
p.label(-4.9, 4.9, "y = −x", ("e", "se"), gap=10, size=NOTE, color=PRACTICE)
p.label(4, -1, "x² − y² = 4", (dc(p, 4.1, -0.9), dc(p, 4.1, 0.9), "e"), size=NOTE, color=THEORY)
finish(f, "ikizkenar",
       "İkizkenar hiperbolde temel dikdörtgen karedir ve asimptotlar birbirine diktir.",
       "Rectangular hyperbola x2 - y2 = 4 with its basic square and the perpendicular asymptotes y = x, y = -x")


# ============================================================ parametre
f, p = equal_fig((-5, 5), (-3.5, 3.5), 56, M_)
axes(p, nums=False)
y1 = 1.125
p.seg((2.5, -y1), (2.5, y1), PRACTICE, 2.8)
hyp(p, 2, 1.5, span=(-3.2, 3.2))
p.right_angle((2.5, 0), (3.5, 0), (2.5, 1), 9)
name_axes(p)
origin(p)
dots(p, [(2, 0), (-2, 0), (-2.5, 0)])
dots(p, [(2.5, 0), (2.5, y1), (2.5, -y1)], PRACTICE)
p.label(2, 0, "A_1", ("sw", "nw", "s"), gap=6)
p.label(-2, 0, "A_2", ("se", "s"), gap=6)
p.label(2.5, 0, "F_1", ("se", "s"), gap=7)
p.label(-2.5, 0, "F_2", ("sw", "s"), gap=6)
p.label(2.5, y1, "M_1(c, y_1)", ("e", "se", "ne"), gap=8, size=NOTE)
p.label(2.5, -y1, "M_2(c, −y_1)", ("e", "ne", "se"), gap=8, size=NOTE)
p.label(2.5, y1 / 2, "b²/a", ("e", "w"), gap=6, size=NOTE, color=PRACTICE)
finish(f, "parametre",
       f"Odaktan asal eksene dik kiriş: |{e_sub('M', 1)}{e_sub('M', 2)}| = 2{em('b')}<sup>2</sup>/{em('a')}.",
       "Hyperbola x2/4 - y2/2.25 = 1 and the focal chord M1M2 perpendicular to the principal axis at F1")


# ============================================================ teget
f, p = equal_fig((-5, 6), (-3.5, 4.5), 48, M_)
axes(p, nums=False)
P = (4.0, 1.5 * S3)
line_x(p, lambda x: S3 / 2 * (x - 1), 0.5, 5.4, PRACTICE, 2.2)
hyp(p, 2, 1.5, span=(-3.2, 4))
name_axes(p)
origin(p)
dots(p, [(2, 0), (-2, 0), (2.5, 0), (-2.5, 0)])
p.dot(P, PRACTICE, 4.6)
p.label(2, 0, "A_1", ("sw", "s"), gap=6)
p.label(-2, 0, "A_2", ("se", "s"), gap=6)
p.label(2.5, 0, "F_1", ("se", "s"), gap=6)
p.label(-2.5, 0, "F_2", ("sw", "s"), gap=6)
p.label(*P, "P(x_0, y_0)", ("nw", "w", "n"), gap=8)
p.label(5.4, S3 / 2 * 4.4, "T_d", ("nw", "w", "n"), gap=8, color=PRACTICE)
finish(f, "teget",
       f"{em('P')}({em('x')}<sub>0</sub>, {em('y')}<sub>0</sub>) noktasındaki teğet: "
       f"{em('x')}<sub>0</sub>{em('x')}/{em('a')}<sup>2</sup> &#8722; {em('y')}<sub>0</sub>{em('y')}/{em('b')}<sup>2</sup> = 1.",
       "Hyperbola x2/4 - y2/2.25 = 1 and its tangent line at the point P(4, 1.5 sqrt3) of the right branch")


# ============================================================ ornek-disaridan-teget
f, p = equal_fig((-6, 7), (-7, 7), 40, M_)
axes(p)
line_x(p, lambda x: S3 * (x - 1), 0, 4.7, PRACTICE, 2.1)
line_x(p, lambda x: -S3 * (x - 1), 0, 4.7, PRACTICE, 2.1)
hyp(p, 2, 3, span=(-6.5, 6.5))
name_axes(p)
origin(p, ("nw", "sw", "w"))
T1, T2 = (4.0, 3 * S3), (4.0, -3 * S3)
dots(p, [(1, 0)], TEXT, 4.6)
dots(p, [T1, T2], PRACTICE, 4.6)
p.label(1, 0, "P(1, 0)", (dc(p, 1.0, -1.45), dc(p, 1.0, 1.45), "s"), gap=8)
p.label(*T1, "(4, 3√3)", ("e", "se"), gap=8, size=NOTE)
p.label(*T2, "(4, −3√3)", ("e", "ne"), gap=8, size=NOTE)
p.label(2.5, S3 * 1.5, "x − y/√3 = 1", (dc(p, 1.35, 3.1), dc(p, 1.25, 3.6)), size=NOTE, color=PRACTICE)
p.label(2.5, -S3 * 1.5, "x + y/√3 = 1", (dc(p, 1.35, -3.1), dc(p, 1.25, -3.6)), size=NOTE, color=PRACTICE)
finish(f, "ornek-disaridan-teget",
       f"{em('P')}(1, 0)'dan hiperbole çizilen iki teğet, sağ kola (4, &#177;3&#8730;3)'te değer.",
       "Hyperbola x2/4 - y2/9 = 1 and the two tangents from P(1, 0), touching the right branch at (4, +-3 sqrt3)")


# ============================================================ normal
f, p = equal_fig((-6.5, 15.5), (-6.5, 10), 30, M_)
axes(p, step=1, numbered={-5, 5, 10, 15})
P = (5.0, 16 / 3)
line_x(p, lambda x: (5 * x - 9) / 3, 0, 6.6, PRACTICE, 2.1)
line_x(p, lambda x: (125 - 9 * x) / 15, 0, 15, BASE, 2.1)
hyp(p, 3, 4, span=(-6, 9.5))
p.right_angle(P, (6.5, (5 * 6.5 - 9) / 3), (7, (125 - 63) / 15), 11)
name_axes(p)
origin(p, ("sw", "se"))
p.dot(P, TEXT, 4.6)
p.label(*P, "P(5, 16/3)", ("nw", "w", "n"), gap=9)
p.label(6.6, 8, "5x − 3y = 9", ("w", "nw"), gap=10, size=NOTE, color=PRACTICE)
p.label(12, (125 - 108) / 15, "9x + 15y = 125", ("ne", "n", "e"), gap=10, size=NOTE, color=BASE)
finish(f, "normal",
       f"{em('P')}'deki teğet ve normal birbirine diktir.",
       "Hyperbola x2/9 - y2/16 = 1 with the tangent 5x - 3y = 9 and the normal 9x + 15y = 125 at P(5, 16/3)")


# ============================================================ dogru-durumlari
f, p = equal_fig((-6, 6), (-5, 5), 56, M_)
axes(p, nums=False)
asymptotes(p, 0.75, color=TEXT, width=1.1, opacity=FAINT)
r7 = math.sqrt(7)
line_x(p, lambda x: 0.5 * x + 0.5, -6, 6, PRACTICE, 2.0)
line_x(p, lambda x: x + r7 / 2, -6, 6, BASE, 2.0)
line_x(p, lambda x: x - 1, -6, 6, REMARK, 2.0, "9 5")
line_x(p, lambda x: 0.75 * x - 1, -6, 6, TEXT, 1.8)
hyp(p, 2, 1.5, span=(-4.5, 4.5))
name_axes(p)
origin(p, ("se", "sw", "ne"))
x1, x2 = (2 + math.sqrt(54)) / 2.5, (2 - math.sqrt(54)) / 2.5
dots(p, [(x1, 0.5 * x1 + 0.5), (x2, 0.5 * x2 + 0.5)], PRACTICE)
dots(p, [(-8 / r7, -9 / (2 * r7))], BASE)
dots(p, [(13 / 6, 5 / 8)], TEXT)
p.label(-5.6, -2.3, "d_1", ("n", "nw", "ne"), gap=6, color=PRACTICE)
p.label(5 - r7 / 2, 5, "d_2", ("w", "sw", "e"), gap=8, color=BASE)
p.label(6, 5, "d_3", ("w", "sw", "s"), gap=8, color=REMARK)
p.label(-16 / 3, -5, "d_4", ("e", "ne", "n"), gap=8, color=TEXT)
finish(f, "dogru-durumlari",
       f"Bir doğru hiperbolü iki noktada kesebilir ({e_sub('d', 1)}), ona teğet olabilir ({e_sub('d', 2)}), "
       f"onunla hiç buluşmayabilir ({e_sub('d', 3)}); bir asimptota paralelse tek noktada keser ({e_sub('d', 4)}).",
       "Hyperbola x2/4 - y2/2.25 = 1 and four lines: a secant, a tangent, a line missing the curve "
       "and a line parallel to an asymptote that meets the curve once", WIDE)


# ============================================================ dis-merkezlik
f, p = equal_fig((-6, 6), (-5, 5), 48, M_)
axes(p, nums=False)
for b, col in ((1.5, THEORY), (2 * S3, PRACTICE), (2 * math.sqrt(15), BASE)):
    hyp(p, 2, b, span=(-4.5, 4.5), color=col, width=2.2)
name_axes(p)
origin(p)
dots(p, [(2, 0), (-2, 0)])
p.label(2, 0, "A_1", ("se", "sw", "s"), gap=6)
p.label(-2, 0, "A_2", ("sw", "se", "s"), gap=6)
p.label(2 * math.sqrt(1 + 4.5 ** 2 / 60), 4.5, "e = 4", ("w", "sw"), gap=8, size=NOTE, color=BASE)
p.label(2 * math.sqrt(1 + 4.5 ** 2 / 12), 4.5, "e = 2", ("e", "se"), gap=8, size=NOTE, color=PRACTICE)
p.label(5.6, 0.75 * math.sqrt(5.6 ** 2 - 4), "e = 1,25", ("se", "s", "e"), gap=8, size=NOTE, color=THEORY)
finish(f, "dis-merkezlik",
       f"Köşeler aynıyken {em('e')} büyüdükçe asimptotlar dikleşir ve kollar açılır; {em('e')} 1'e "
       "yaklaştıkça kollar asal eksene doğru kapanır.",
       "Three hyperbolas with the same vertices (+-2, 0) and eccentricities 1.25, 2 and 4")


# ============================================================ dogrultman
f, p = equal_fig((-4.6, 4.6), (-3.4, 3.5), 58, M_)
axes(p, nums=False)
P, H = (4.0, 1.5 * S3), (1.6, 1.5 * S3)
for x in (1.6, -1.6):
    vseg(p, x, -3.0, 3.2, PRACTICE, 1.5)
p.seg(P, H, TEXT, 1.4)
p.seg(P, (2.5, 0), TEXT, 1.4)
p.right_angle(H, (2.6, 1.5 * S3), (1.6, 1.5), 9)
hyp(p, 2, 1.5, span=(-3.0, 3.0))
name_axes(p)
origin(p, ("sw", "nw"))
dots(p, [(2, 0), (-2, 0), (2.5, 0), (-2.5, 0), H])
p.dot(P, PRACTICE, 4.6)
p.label(1.6, -3.0, "Δ_1", ("s", "se"), gap=6, color=PRACTICE)
p.label(-1.6, -3.0, "Δ_2", ("s", "sw"), gap=6, color=PRACTICE)
p.label(1.6, 0, "a²/c", ("sw", "s"), gap=6, size=NOTE, color=PRACTICE)
p.label(-1.6, 0, "−a²/c", ("se", "s"), gap=6, size=NOTE, color=PRACTICE)
p.label(2, 0, "A_1", ("se", "s"), gap=5)
p.label(-2, 0, "A_2", ("sw", "s"), gap=5)
p.label(2.5, 0, "F_1", ("ne", "se"), gap=6)
p.label(-2.5, 0, "F_2", ("nw", "sw"), gap=6)
p.label(*P, "P(x, y)", ("ne", "e", "n"))
p.label(*H, "H", ("nw", "w", "sw"), gap=7)
p.along(H, P, "|PH|", 1, 0.5, 6, NOTE)
along_out(p, P, (2.5, 0), "|PF_1|", H, TEXT, NOTE, t=0.5)
finish(f, "dogrultman",
       f"Hiperbolün her noktasında |{em('PF')}<sub>1</sub>| = {em('e')}&#183;|{em('PH')}|.",
       "Hyperbola x2/4 - y2/2.25 = 1 with its directrices x = +-1.6; for P on the right branch the "
       "distances PF1 and PH to the focus and to the directrix are marked")


# ============================================================ parametrik
f, p = equal_fig((-5, 5), (-3.5, 3.5), 56, M_)
axes(p, nums=False)
T, H, P = (1.0, S3), (4.0, 0.0), (4.0, 1.5 * S3)
p.ring((0, 0), 2, PRACTICE, 1.6)
p.seg((0, 0), T, TEXT, 1.5)
p.seg(T, H, TEXT, 1.5)
p.seg(P, H, TEXT, 1.3, "4 4")
p.right_angle(T, (0, 0), H, 9)
p.angle((0, 0), 0, PI / 3, 0.55, TEXT, 1.3)
hyp(p, 2, 1.5, span=(-3.2, 3.2))
name_axes(p)
origin(p, ("sw", "nw"))
dots(p, [T, H])
p.dot(P, PRACTICE, 4.6)
p.label(*T, "T", ("nw", "n", "w"), gap=7)
p.label(*H, "H(x, 0)", ("s", "se"), gap=8, size=NOTE)
p.label(*P, "P(x, y)", ("e", "ne", "se"), gap=8)
along_out(p, (0, 0), T, "a", H, TEXT, NAME, t=0.6)
p.angle_label((0, 0), 0, PI / 3, 0.55, "θ", size=NAME)
p.label(4.2, -0.75 * math.sqrt(4.2 ** 2 - 4), "x²/a² − y²/b² = 1",
        (dc(p, 3.6, -3.1), dc(p, 3.2, -1.1), "se"), size=NOTE, color=THEORY)
finish(f, "parametrik",
       f"{em('OTH')} dik üçgeninde cos&#8201;{em('θ')} = {em('a')}/{em('x')} olduğundan "
       f"{em('x')} = {em('a')}&#8201;sec&#8201;{em('θ')}, {em('y')} = {em('b')}&#8201;tan&#8201;{em('θ')}.",
       "Hyperbola x2/4 - y2/2.25 = 1 with its principal circle; theta = pi/3, T on the circle, "
       "the tangent TH and the point P above H")


# ============================================================ exr-elips-dogrultman
f, p = equal_fig((-14, 14), (-8, 8), 22, M_)
axes(p, step=2, numbered={-12, -8, -4, 4, 8, 12})
for x in (12.5, -12.5):
    vseg(p, x, -7, 7, PRACTICE, 1.8)
ell(p, 10, 6)
name_axes(p)
origin(p, ("sw", "nw"))
dots(p, [(8, 0), (-8, 0)])
p.label(8, 0, "F_1(8, 0)", ("nw", "n", "ne"), gap=6, size=NOTE)
p.label(-8, 0, "F_2(−8, 0)", ("ne", "n", "nw"), gap=6, size=NOTE)
p.label(12.5, -7, "Δ_1: x = 25/2", ("w", "nw"), gap=7, size=NOTE, color=PRACTICE)
p.label(-12.5, -7, "Δ_2: x = −25/2", ("e", "ne"), gap=7, size=NOTE, color=PRACTICE)
finish(f, "exr-elips-dogrultman",
       f"Elipsin doğrultmanları elipsin dışında, {em('x')} = &#177;25/2'de durur.",
       "Ellipse x2/100 + y2/36 = 1 with foci (+-8, 0) and directrices x = +-25/2")


# ============================================================ exr-cizim
f, p = equal_fig((-6, 6), (-4.5, 4.5), 50, M_)
axes(p)
r7 = math.sqrt(7)
p.poly([(-2, -S3), (2, -S3), (2, S3), (-2, S3)], THEORY, 0.0, TEXT, 1.1, "4 4")
asymptotes(p, S3 / 2)
hyp(p, 2, S3, span=(-4.2, 4.2))
name_axes(p)
origin(p, ("sw", "nw", "se"))
dots(p, [(2, 0), (-2, 0), (r7, 0), (-r7, 0), (4, 3), (4, -3)])
p.label(2, 0, "A_1(2, 0)", ("sw", "s"), gap=6, size=NOTE)
p.label(-2, 0, "A_2(−2, 0)", ("se", "s"), gap=6, size=NOTE)
p.label(r7, 0, "F_1(√7, 0)", ("ne", "n"), gap=6, size=NOTE)
p.label(-r7, 0, "F_2(−√7, 0)", ("nw", "n"), gap=6, size=NOTE)
p.label(4, 3, "(4, 3)", ("e", "se"), gap=8, size=NOTE)
p.label(4, -3, "(4, −3)", ("e", "ne"), gap=8, size=NOTE)
p.label(4.5 / (S3 / 2), 4.5, "y = (√3/2)x", ("w", "sw", "s"), gap=8, size=NOTE, color=PRACTICE)
p.label(4.5 / (S3 / 2), -4.5, "y = −(√3/2)x", ("w", "nw", "n"), gap=8, size=NOTE, color=PRACTICE)
finish(f, "exr-cizim",
       f"3{XX}<sup>2</sup> &#8722; 4{YY}<sup>2</sup> = 12 hiperbolü, temel dikdörtgeni ve asimptotları.",
       "Hyperbola 3x2 - 4y2 = 12 with its basic rectangle, asymptotes y = +-(sqrt3/2)x, vertices, foci "
       "and the points (4, 3), (4, -3)", WIDE)


# ============================================================ exr-odak-koseden
f, p = equal_fig((-12, 8), (-8, 10), 27, M_)
axes(p, numbered={-10, -6, -2, 2, 6, -6, 6, 8, -4, 4})
M = (-2.0, 1.0)
k = math.sqrt(5) / 2
p.seg((p.xmin, 1), (p.xmax, 1), TEXT, 1.1, None, FAINT)
asymptotes(p, k, M, PRACTICE, 1.4, 0.75)
hyp(p, 4, math.sqrt(20), M, (-7, 9))
name_axes(p)
origin(p, ("sw", "se"))
dots(p, [M, (2, 1), (-6, 1), (4, 1), (-8, 1)])
p.label(*M, "M(−2, 1)", (dc(p, -2, 2.55), "s"), gap=7, size=NOTE)
p.label(2, 1, "A_1(2, 1)", ("se", "sw", "s"), gap=6, size=NOTE)
p.label(-6, 1, "A_2(−6, 1)", ("sw", "se", "s"), gap=6, size=NOTE)
p.label(4, 1, "F_1(4, 1)", ("ne", "n"), gap=6, size=NOTE)
p.label(-8, 1, "F_2(−8, 1)", ("nw", "n"), gap=6, size=NOTE)
finish(f, "exr-odak-koseden",
       f"Odakları ve köşeleri {em('y')} = 1 doğrusu üzerinde olan, merkezi {em('M')}(&#8722;2, 1) hiperbol.",
       "Hyperbola (x+2)2/16 - (y-1)2/20 = 1 with center M(-2, 1), vertices (2, 1), (-6, 1) and foci (4, 1), (-8, 1)")


# ============================================================ exr-i-hiperbol
f, p = equal_fig((-7.4, 7.4), (-4.6, 4.6), 42, M_)
axes(p)
a, yc = 2 * S3, 2 / S3
asymptotes(p, 1 / S3)
for x in (3, -3):
    vseg(p, x, -2, 2, BASE, 1.6)
p.seg((4, -yc), (4, yc), TEXT, 1.6)
hyp(p, a, 2, span=(-4.5, 4.5))
name_axes(p)
origin(p, ("sw", "nw"))
dots(p, [(4, 0), (-4, 0), (a, 0), (-a, 0)])
dots(p, [(4, yc), (4, -yc)], TEXT, 3.8)
p.label(4, 0, "F_1(4, 0)", ("ne", "n"), gap=6, size=NOTE)
p.label(-4, 0, "F_2(−4, 0)", ("nw", "n"), gap=6, size=NOTE)
p.label(a, 0, "A_1", (dc(p, (3 + a) / 2, -0.36), dc(p, (3 + a) / 2, 0.36)), size=NOTE)
p.label(-a, 0, "A_2", (dc(p, -(3 + a) / 2, -0.36), dc(p, -(3 + a) / 2, 0.36)), size=NOTE)
p.label(4, yc, "M_1", ("e", "ne"), gap=6, size=NOTE)
p.label(4, -yc, "M_2", ("e", "se"), gap=6, size=NOTE)
p.label(3, -2, "x = 3", ("s", "sw", "se"), gap=5, size=NOTE, color=BASE)
p.label(-3, -2, "x = −3", ("s", "se", "sw"), gap=5, size=NOTE, color=BASE)
p.label(7.4, 7.4 / S3, "y = x/√3", ("nw", "n", "w"), gap=8, size=NOTE, color=PRACTICE)
p.label(7.4, -7.4 / S3, "y = −x/√3", ("sw", "s", "w"), gap=8, size=NOTE, color=PRACTICE)
finish(f, "exr-i-hiperbol",
       f"{XX}<sup>2</sup>/12 &#8722; {YY}<sup>2</sup>/4 = 1: odaklar (&#177;4, 0), asimptotlar "
       f"{YY} = &#177;{XX}/&#8730;3, doğrultmanlar {XX} = &#177;3.",
       "Hyperbola x2/12 - y2/4 = 1 with foci (+-4, 0), asymptotes y = +-x/sqrt3, directrices x = +-3 "
       "and the focal chord M1M2")


# ============================================================ exr-ii-hiperbol
f, p = equal_fig((-8, 8), (-5, 5), 38, M_)
axes(p)
a, b, yc = math.sqrt(10), math.sqrt(6), 6 / math.sqrt(10)
k = b / a
asymptotes(p, k)
for x in (2.5, -2.5):
    vseg(p, x, -2, 2, BASE, 1.6)
p.seg((4, -yc), (4, yc), TEXT, 1.6)
hyp(p, a, b, span=(-4.5, 4.5))
name_axes(p)
origin(p, ("sw", "nw"))
dots(p, [(4, 0), (-4, 0), (a, 0), (-a, 0)])
dots(p, [(4, yc), (4, -yc)], TEXT, 3.8)
p.label(4, 0, "F_1(4, 0)", ("ne", "n"), gap=6, size=NOTE)
p.label(-4, 0, "F_2(−4, 0)", ("nw", "n"), gap=6, size=NOTE)
p.label(a, 0, "A_1", (dc(p, (2.5 + a) / 2, -0.36), dc(p, (2.5 + a) / 2, 0.36)), size=NOTE)
p.label(-a, 0, "A_2", (dc(p, -(2.5 + a) / 2, -0.36), dc(p, -(2.5 + a) / 2, 0.36)), size=NOTE)
p.label(4, yc, "M_1", ("e", "ne"), gap=6, size=NOTE)
p.label(4, -yc, "M_2", ("e", "se"), gap=6, size=NOTE)
p.label(2.5, -2, "x = 5/2", ("s", "sw", "se"), gap=5, size=NOTE, color=BASE)
p.label(-2.5, -2, "x = −5/2", ("s", "se", "sw"), gap=5, size=NOTE, color=BASE)
p.label(5 / k, 5, "y = (√15/5)x", ("e", "se", "s"), gap=8, size=NOTE, color=PRACTICE)
p.label(5 / k, -5, "y = −(√15/5)x", ("e", "ne", "n"), gap=8, size=NOTE, color=PRACTICE)
finish(f, "exr-ii-hiperbol",
       f"{XX}<sup>2</sup>/10 &#8722; {YY}<sup>2</sup>/6 = 1: odaklar (&#177;4, 0), asimptotlar "
       f"{YY} = &#177;(&#8730;15/5){XX}, doğrultmanlar {XX} = &#177;5/2.",
       "Hyperbola x2/10 - y2/6 = 1 with foci (+-4, 0), asymptotes y = +-(sqrt15/5)x, directrices "
       "x = +-5/2 and the focal chord M1M2")


# ============================================================ exr-ikizkenar
f, p = equal_fig((-12, 12), (-10, 10), 23, M_)
axes(p, step=2, numbered={-6, 6})
d = 3 * math.sqrt(2)
p.poly([(-6, -6), (6, -6), (6, 6), (-6, 6)], THEORY, 0.0, TEXT, 1.1, "4 4")
asymptotes(p, 1.0)
for x in (d, -d):
    vseg(p, x, -7, 7, BASE, 1.6)
hyp(p, 6, 6, span=(-9.5, 9.5))
p.right_angle((0, 0), (1, 1), (-1, 1), 12)
name_axes(p)
origin(p, ("s", "sw", "se"))
c = 6 * math.sqrt(2)
dots(p, [(6, 0), (-6, 0), (c, 0), (-c, 0)])
p.label(6, 0, "A_1", ("se", "sw", "s"), gap=6)
p.label(-6, 0, "A_2", ("sw", "se", "s"), gap=6)
p.label(c, 0, "F_1(6√2, 0)", ("ne", "n"), gap=6, size=NOTE)
p.label(-c, 0, "F_2(−6√2, 0)", ("nw", "n"), gap=6, size=NOTE)
p.label(9.8, 9.8, "y = x", ("w", "sw"), gap=10, size=NOTE, color=PRACTICE)
p.label(-9.8, 9.8, "y = −x", ("e", "se"), gap=10, size=NOTE, color=PRACTICE)
p.label(d, -7, "x = 3√2", ("s", "se", "sw"), gap=5, size=NOTE, color=BASE)
p.label(-d, -7, "x = −3√2", ("s", "sw", "se"), gap=5, size=NOTE, color=BASE)
finish(f, "exr-ikizkenar",
       f"{XX}<sup>2</sup> &#8722; {YY}<sup>2</sup> = 36 bir ikizkenar hiperboldür: {em('a')} = {em('b')} = 6, "
       f"asimptotlar {YY} = &#177;{XX}.",
       "Rectangular hyperbola x2 - y2 = 36 with its basic square, the asymptotes y = +-x and the "
       "directrices x = +-3 sqrt2")


# ============================================================ exr-teget-mi
f, p = equal_fig((-6, 7), (-4, 4), 40, M_)
axes(p)
a, b = math.sqrt(5), math.sqrt(5) / 2
asymptotes(p, 0.5, color=TEXT, width=1.1, opacity=FAINT)
line_x(p, lambda x: (3 * x - 5) / 4, -2, 7, PRACTICE, 2.1)
hyp(p, a, b, span=(-3.5, 3.5))
name_axes(p)
origin(p, ("sw", "nw"))
p.dot((3, 1), PRACTICE, 4.6)
p.label(3, 1, "(3, 1)", ("nw", "n", "w"), gap=8, size=NOTE)
p.label(7, 4, "3x − 4y − 5 = 0", ("sw", "w"), gap=8, size=NOTE, color=PRACTICE)
p.label(-4, 1.5, "x² − 4y² = 5", (dc(p, -4.6, -0.8), dc(p, -3.6, 3.6), "w"), size=NOTE, color=THEORY)
finish(f, "exr-teget-mi",
       f"3{XX} &#8722; 4{YY} &#8722; 5 = 0 doğrusu hiperbole (3, 1) noktasında teğettir.",
       "Hyperbola x2 - 4y2 = 5 and the line 3x - 4y - 5 = 0 touching it at (3, 1)")


# ============================================================ exr-lambda
f, p = equal_fig((-9, 9), (-11, 11), 28, M_)
axes(p, step=1, numbered={-8, -5, 5, 8})
asymptotes(p, 2.0, color=TEXT, width=1.1, opacity=FAINT)
line_x(p, lambda x: (5 * x - 9) / 2, -9, 9, PRACTICE, 2.1)
line_x(p, lambda x: (5 * x + 9) / 2, -9, 9, PRACTICE, 2.1)
line_x(p, lambda x: 2.5 * x, -9, 9, BASE, 1.6, "6 4")
hyp(p, 3, 6, span=(-10.5, 10.5))
name_axes(p)
origin(p, ("se", "nw"))
dots(p, [(5, 8), (-5, -8)], PRACTICE, 4.6)
p.label(5, 8, "(5, 8)", ("e", "se"), gap=8, size=NOTE)
p.label(-5, -8, "(−5, −8)", ("w", "nw"), gap=8, size=NOTE)
p.label((22 + 9) / 5, 11, "λ = −9", ("e", "se"), gap=8, size=NOTE, color=PRACTICE)
p.label((22 - 9) / 5, 11, "λ = 9", ("w", "sw"), gap=8, size=NOTE, color=PRACTICE)
p.label(4.4, 11, "λ = 0", ("sw", "w", "s"), gap=8, size=NOTE, color=BASE)
finish(f, "exr-lambda",
       f"{em('λ')} = &#177;9'da doğru hiperbole teğet; &#8722;9 &lt; {em('λ')} &lt; 9 iken hiperbolü kesmez.",
       "Hyperbola 4x2 - y2 = 36 and the parallel lines 5x - 2y + lambda = 0 for lambda = -9, 0, 9; "
       "the outer two touch the curve at (5, 8) and (-5, -8)")


# ============================================================ exr-noktadan-teget
f, p = equal_fig((-9, 9), (-10, 7), 30, M_)
axes(p, step=1, numbered={-8, -6, -4, -2, 2, 4, 6, 8})
asymptotes(p, 1.0, color=TEXT, width=1.1, opacity=FAINT)
line_x(p, lambda x: -13 / 5 * x - 48 / 5, -6.0, 0.15, PRACTICE, 2.1)
line_x(p, lambda x: 5 / 3 * x - 16 / 3, -2.5, 7.4, BASE, 2.1)
hyp(p, 4, 4, span=(-9.5, 6.5))
name_axes(p)
origin(p, ("se", "nw"))
P = (-1.0, -7.0)
p.dot(P, TEXT, 4.6)
dots(p, [(-13 / 3, 5 / 3)], PRACTICE, 4.6)
dots(p, [(5, 3)], BASE, 4.6)
p.label(*P, "P(−1, −7)", ("w", "nw", "sw"), gap=8)
p.label(-6.0, 6.0, "t_1", ("w", "nw", "sw"), gap=8, color=PRACTICE)
p.label(7.4, 7.0, "t_2", ("e", "se", "s"), gap=8, color=BASE)
p.label(-13 / 3, 5 / 3, "(−13/3, 5/3)", ("w", "nw", "sw"), gap=8, size=NOTE)
p.label(5, 3, "(5, 3)", ("e", "se"), gap=8, size=NOTE)
finish(f, "exr-noktadan-teget",
       f"{em('P')}(&#8722;1, &#8722;7)'den çizilen iki teğetten biri sol kola, öteki sağ kola değer.",
       "Hyperbola x2 - y2 = 16 and the two tangents from P(-1, -7): t1 touches the left branch at "
       "(-13/3, 5/3), t2 the right branch at (5, 3)")


# ---------------------------------------------------------------------------
for name, content in OUT.items():
    with io.open(OUT_DIR / f"{PREFIX}{name}.md", "w", encoding="utf-8", newline="\n") as fh:
        fh.write(content)
print(f"generated {len(OUT)} figures:", ", ".join(OUT))
