# -*- coding: utf-8 -*-
"""
Figures for the "Öteleme" chapter of Analitik Geometri
(dersler/analitik-geometri/oteleme.qmd).

The figures are NOT produced at build time. Run

    python scripts/analytic_figures/ote.py
    python scripts/center_figures.py "analytic-ote-*.md" --keep-width
    python scripts/check_figure_labels.py "scripts/_figures/analytic-ote-*.md"

and paste each scripts/_figures/analytic-ote-<name>.md block into the .qmd.
Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box: a figure that illustrates a
definition sits directly below that box.

Conventions: the old axes X, Y are solid; translated axes X', Y' are dashed
and drawn in the "practice" color, which also marks every quantity measured
in the new system. One scale on both axes, so circles and angles look true.
Labels go through the collision-avoiding placer shared with pkk.py; axis
numbers that would touch anything are dropped at finish().

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
PREFIX = "analytic-ote-"
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


def obl(u, v, alpha):
    """Parallel coordinates (u, v) with axis angle alpha -> drawing coordinates."""
    return (u + v * math.cos(alpha), v * math.sin(alpha))


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

    def polar_axis(self, L, xl="X", opacity=0.75):
        self.arrow((0, 0), (L, 0), TEXT, 1.4, 9, opacity=opacity)
        self.label(L, 0, xl, ("e", "se", "ne"), gap=8, size=AXIS)

    def oblique_axes(self, alpha, xr, vr, ticks=True, grid=None, opacity=0.6):
        """X-axis on the horizontal, Y-axis at angle alpha; grid = (xr_box, yr_box) draws
        faint lines x = k and y = k (parallel to the axes) clipped to that box."""
        ca, sa = math.cos(alpha), math.sin(alpha)
        if grid:
            (gx0, gx1), (gy0, gy1) = grid
            rect = (gx0, gx1, gy0, gy1)
            parts = []
            for k in range(-12, 13):
                if k == 0:
                    continue
                for pt, d in (((k, 0.0), (ca, sa)), ((k * ca, k * sa), (1.0, 0.0))):
                    s = clip_line(pt, d, rect)
                    if s:
                        a, b = self.px(s[0]), self.px(s[1])
                        parts.append(f"M{a[0]:.1f},{a[1]:.1f} L{b[0]:.1f},{b[1]:.1f}")
                        self.fig.segs.append(([a, b], 0.15))
            self.add(f'<path d="{" ".join(parts)}" stroke="{TEXT}" stroke-width="0.8" opacity="0.14" fill="none"/>')
        self.arrow((xr[0], 0), (xr[1], 0), TEXT, 1.3, 8.5, opacity=opacity + 0.1)
        self.arrow((vr[0] * ca, vr[0] * sa), (vr[1] * ca, vr[1] * sa), TEXT, 1.3, 8.5, opacity=opacity + 0.1)
        if ticks:
            parts = []
            for k in range(math.ceil(xr[0]), math.floor(xr[1] - 0.3) + 1):
                if k:
                    X, Y = self.X(k), self.Y(0)
                    parts.append(f"M{X:.1f},{Y - 3.5:.1f} L{X:.1f},{Y + 3.5:.1f}")
                    self.fig.segs.append(([(X, Y - 3.5), (X, Y + 3.5)], 0.4))
            nx, ny = sa, ca          # pixel normal of the Y-axis (y flipped)
            for k in range(math.ceil(vr[0]), math.floor(vr[1] - 0.3) + 1):
                if k:
                    X, Y = self.px((k * ca, k * sa))
                    parts.append(f"M{X - 3.5 * nx:.1f},{Y - 3.5 * ny:.1f} L{X + 3.5 * nx:.1f},{Y + 3.5 * ny:.1f}")
                    self.fig.segs.append(([(X - 3.5 * nx, Y - 3.5 * ny), (X + 3.5 * nx, Y + 3.5 * ny)], 0.4))
            self.add(f'<path d="{" ".join(parts)}" stroke="{TEXT}" stroke-width="1.1" opacity="{opacity}"/>')

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
    p.dot((0, 0), TEXT)
    p.label(0, 0, "O", prefs, gap=8)


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


def axes(p, nums=True, step=1, names=("X", "Y"), opacity=0.7):
    """Old (solid) axes over the whole panel; integer ticks, numbers placed at finish()."""
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
                p.fig.nums.append(("x", p, t))
        for k in range(math.ceil(p.ymin / step), math.floor((p.ymax - 0.4 * step) / step) + 1):
            t = k * step
            if t:
                X, Y = p.X(0), p.Y(t)
                parts.append(f"M{X - 3.5:.1f},{Y:.1f} L{X + 3.5:.1f},{Y:.1f}")
                p.fig.segs.append(([(X - 3.5, Y), (X + 3.5, Y)], 0.4))
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


# ============================================================ oteleme-vektoru
f, p = equal_fig((-0.8, 5.0), (-0.8, 5.0), 84, (40, 34, 60, 34))
axes(p, nums=False)
A, P, P2 = (2, 1), (1, 3), (3, 4)
p.seg(A, P2, TEXT, THIN, GUIDE, 0.6)
p.arrow(O, P, TEXT, 1.5, 8.5, opacity=0.55)
p.arrow(O, A, THEORY, 2.5, 10)
p.arrow(P, P2, THEORY, 2.5, 10)
name_axes(p)
origin(p)
for q in (A, P, P2):
    p.dot(q, TEXT)
p.label(*A, "A", ("se", "e", "s"))
p.label(*P, "P", ("nw", "w", "n"))
p.label(*P2, "P′ = P + a", ("ne", "e", "n", "nw"))
along_out(p, O, A, "a", P, THEORY, NAME)
along_out(p, P, P2, "a", A, THEORY, NAME)
finish(f, "oteleme-vektoru",
       "<em>f<sub>a</sub></em> ötelemesi <em>P</em> noktasını <em>a</em> = <em>OA</em> vektörü kadar kaydırır: "
       "<em>OA</em> ve <em>PP</em>′ okları paralel ve eşit uzunluktadır.",
       "Translation f_a: the point P moves by the vector a = OA to P' = P + a; OA and PP' are parallel and equal")


# ============================================================ sayisal-oteleme
f, p = equal_fig((-4.4, 4.4), (-3, 5.2), 60, M_)
axes(p)
A, P, P2 = (3, 4), (-3, -2), (0, 2)
p.seg(O, P, TEXT, THIN, GUIDE, 0.6)
p.seg(A, P2, TEXT, THIN, GUIDE, 0.6)
p.arrow(O, A, THEORY, 2.5, 10)
p.arrow(P, P2, THEORY, 2.5, 10)
name_axes(p)
origin(p)
for q in (A, P, P2):
    p.dot(q, TEXT)
p.label(*A, "A(3, 4)", ("e", "se", "ne", "nw"))
p.label(*P, "P(−3, −2)", ("s", "sw", "se", "w"))
p.label(*P2, "P′(0, 2)", ("e", "se", "ne"))
along_out(p, O, A, "a = (3, 4)", P, THEORY)
finish(f, "sayisal-oteleme",
       "<em>a</em> = (3, 4) ötelemesi <em>P</em>(−3, −2) noktasını <em>P</em>′(0, 2) noktasına taşır.",
       "Translation by a = (3, 4) takes P(-3, -2) to P'(0, 2)")


# ============================================================ bileske-ucgen
f, p = equal_fig((-1.0, 5.6), (-2.0, 2.9), 76, (30, 24, 30, 24))
P, Pb, Pab = (0, 0), (3, -1), (4, 2)
p.arrow(P, Pb, THEORY, 2.5, 10)
p.arrow(Pb, Pab, PRACTICE, 2.5, 10)
p.arrow(P, Pab, BASE, 3.2, 12)
for q in (P, Pb, Pab):
    p.dot(q, TEXT)
p.label(*P, "P", ("w", "sw", "nw"))
p.label(*Pb, "P + b", ("se", "s", "e"))
p.label(*Pab, "P + b + a", ("ne", "n", "e", "nw"))
along_out(p, P, Pb, "b", Pab, THEORY, NAME)
along_out(p, Pb, Pab, "a", P, PRACTICE, NAME)
along_out(p, P, Pab, "a + b", Pb, BASE, NAME)
finish(f, "bileske-ucgen",
       "Önce <em>b</em>, sonra <em>a</em> kadar ötelemek, <em>a</em> + <em>b</em> kadar tek bir ötelemeyle aynıdır.",
       "Composition of translations: P moves by b, then by a; the same as one move by a + b")


# ============================================================ bileske-sayisal
f, p = equal_fig((-5, 4), (-1, 8.2), 56, M_)
axes(p)
P, Mb, E = (2, 2), (-2, 5), (-1, 7)
p.arrow(P, Mb, THEORY, 2.5, 10)
p.arrow(Mb, E, PRACTICE, 2.5, 10)
p.arrow(P, E, BASE, 2.5, 10, dash="7 5")
name_axes(p)
origin(p)
for q in (P, Mb, E):
    p.dot(q, TEXT)
p.label(*P, "P(2, 2)", ("e", "se", "ne"))
p.label(*Mb, "f_b(P) = (−2, 5)", ("w", "sw", "nw"))
p.label(*E, "(−1, 7)", ("n", "nw", "ne", "w"))
along_out(p, P, Mb, "b = (−4, 3)", E, THEORY)
along_out(p, Mb, E, "a = (1, 2)", P, PRACTICE)
along_out(p, P, E, "a + b = (−3, 5)", Mb, BASE)
finish(f, "bileske-sayisal",
       "<em>P</em>(2, 2) noktasına önce <em>b</em> = (−4, 3), sonra <em>a</em> = (1, 2) ötelemesi uygulanır; "
       "sonuç, <em>a</em> + <em>b</em> = (−3, 5) ötelemesinin verdiği (−1, 7) noktasıdır.",
       "P(2, 2) moved by b = (-4, 3) and then by a = (1, 2) reaches (-1, 7), the same as one move by a + b = (-3, 5)")


# ============================================================ uzaklik-korunur
f, p = equal_fig((-0.7, 6.4), (-0.7, 5.9), 72, M_)
axes(p, nums=False, opacity=0.4)
P, Q, P2, Q2 = (1, 1), (4, 2), (2, 4), (5, 5)
p.arrow(P, P2, PRACTICE, 2.0, 9)
p.arrow(Q, Q2, PRACTICE, 2.0, 9)
p.seg(P, Q, THEORY, 3.0)
p.seg(P2, Q2, THEORY, 3.0)
eq_ticks(p, P, Q, 2, THEORY)
eq_ticks(p, P2, Q2, 2, THEORY)
name_axes(p)
origin(p)
for q in (P, Q, P2, Q2):
    p.dot(q, TEXT)
p.label(*P, "P", ("sw", "w", "s"))
p.label(*Q, "Q", ("se", "e", "s"))
p.label(*P2, "P′ = f_a(P)", ("nw", "w", "n"))
p.label(*Q2, "Q′ = f_a(Q)", ("ne", "n", "e"))
along_out(p, P, P2, "a", Q, PRACTICE, NAME)
along_out(p, Q, Q2, "a", P, PRACTICE, NAME)
finish(f, "uzaklik-korunur",
       "<em>PQ</em> parçası <em>a</em> kadar ötelenince uzunluğu değişmez: |<em>P</em>′<em>Q</em>′| = |<em>PQ</em>|.",
       "Translation preserves distance: segment PQ and its image P'Q' have equal length")


# ============================================================ uzaklik-sayisal
f, p = equal_fig((-4, 5.2), (-0.8, 8.2), 56, M_)
axes(p)
P, Q, P2, Q2 = (1, 2), (4, 6), (-2, 3), (1, 7)
p.arrow(P, P2, PRACTICE, 2.0, 9)
p.arrow(Q, Q2, PRACTICE, 2.0, 9)
p.seg(P, Q, THEORY, 2.8)
p.seg(P2, Q2, THEORY, 2.8)
name_axes(p)
origin(p)
for q in (P, Q, P2, Q2):
    p.dot(q, TEXT)
p.label(*P, "P(1, 2)", ("se", "e", "s"))
p.label(*Q, "Q(4, 6)", ("e", "se", "ne"))
p.label(*P2, "P′(−2, 3)", ("w", "sw", "nw"))
p.label(*Q2, "Q′(1, 7)", ("ne", "n", "e"))
along_out(p, P, Q, "5", P2, THEORY, NAME)
along_out(p, P2, Q2, "5", Q, THEORY, NAME)
along_out(p, P, P2, "a = (−3, 1)", Q, PRACTICE)
finish(f, "uzaklik-sayisal",
       "<em>a</em> = (−3, 1) ötelemesinden önce ve sonra iki nokta arasındaki uzaklık 5'tir.",
       "Segment from P(1, 2) to Q(4, 6) and its image under a = (-3, 1); both have length 5")


# ============================================================ dogrunun-otelenmesi
f, p = equal_fig((-3, 3.2), (-3, 6.2), 72, M_)
axes(p)
rect = (p.xmin, p.xmax, p.ymin, p.ymax)
d1 = clip_line((0, 1), (1, 2), rect)
d2 = clip_line((0, 2), (1, 2), rect)
p.seg(*d1, THEORY, 2.3)
p.seg(*d2, PRACTICE, 2.3)
p.arrow((0, 1), (1, 4), BASE, 2.0, 9)
p.arrow((-1, -1), (0, 2), BASE, 2.0, 9)
name_axes(p)
origin(p)
for q in ((0, 1), (-1, -1)):
    p.dot(q, THEORY)
for q in ((1, 4), (0, 2)):
    p.dot(q, PRACTICE)
p.label(0, 1, "(0, 1)", ("e", "se"), size=NOTE)
p.label(-1, -1, "(−1, −1)", ("e", "se", "s"), size=NOTE)
p.label(1, 4, "(1, 4)", ("w", "nw", "e"), size=NOTE)
p.label(0, 2, "(0, 2)", ("w", "nw", "sw"), size=NOTE)
along_out(p, (-1, -1), (0, 2), "a = (1, 3)", (0, 1), BASE)
p.label(*d1[0], "d: y = 2x + 1", ("e", "se", "ne"), gap=10, size=NOTE, color=THEORY)
p.label(*d2[1], "d′: y = 2x + 2", ("w", "sw", "nw"), gap=10, size=NOTE, color=PRACTICE)
finish(f, "dogrunun-otelenmesi",
       "<em>d</em> doğrusunun her noktası <em>a</em> = (1, 3) kadar ötelenince <em>d</em>′ doğrusu oluşur; "
       "iki doğrunun eğimi aynıdır.",
       "Line d: y = 2x + 1 translated by a = (1, 3) gives the parallel line d': y = 2x + 2")


# ============================================================ eksen-oteleme
f, p = equal_fig((-0.8, 7.0), (-0.8, 5.2), 70, M_)
axes(p, nums=False)
Op, P = (2.5, 1.2), (5.0, 4.2)
new_axes(p, Op)
p.arrow(O, Op, THEORY, 2.3, 9.5)
p.arrow(Op, P, NEW, 2.3, 9.5)
p.arrow(O, P, BASE, 2.3, 9.5)
name_axes(p)
origin(p)
p.dot(Op, NEW)
p.dot(P, TEXT)
p.label(Op[0], 0, "a", ("se", "sw"), size=NAME)
p.label(0, Op[1], "b", ("nw", "sw"), size=NAME)
p.label(*Op, "O′", ("se", "nw", "sw"), color=NEW)
block(p, *P, [("P(x, y)", TEXT), ("(x′, y′)", NEW)], ("e", "se", "ne"), size=NAME)
finish(f, "eksen-oteleme",
       "Eksenler <em>OO</em>′ = (<em>a</em>, <em>b</em>) kadar ötelenir; <em>OP</em> = <em>OO</em>′ + <em>O</em>′<em>P</em> "
       "eşitliğinden <em>x</em> = <em>x</em>′ + <em>a</em>, <em>y</em> = <em>y</em>′ + <em>b</em> çıkar.",
       "Old axes X, Y through O and translated dashed axes X', Y' through O'(a, b); vectors OO', O'P and OP")


# ============================================================ yeni-baslangic
f, p = equal_fig((-5, 6.2), (-4, 7.2), 50, M_)
axes(p)
Op, Q = (-3, 5), (4, -2)
new_axes(p, Op)
p.seg(Q, (Op[0], Q[1]), NEW, 1.3, GUIDE, 0.85)
p.seg(Q, (Q[0], Op[1]), NEW, 1.3, GUIDE, 0.85)
name_axes(p)
origin(p)
p.dot(Op, NEW)
p.dot(Q, TEXT)
p.label(*Op, "O′(−3, 5)", ("nw", "ne", "sw"), color=NEW)
block(p, *Q, [("Q: eski (4, −2)", TEXT), ("yeni (7, −7)", NEW)], ("se", "e", "sw", "s"))
along_out(p, (Op[0], Q[1]), Q, "7", (0, -4), NEW, NAME, t=0.3)
along_out(p, Q, (Q[0], Op[1]), "7", (2, 1), NEW, NAME)
finish(f, "yeni-baslangic",
       "Başlangıç noktası <em>O</em>′(−3, 5) olan yeni sistemde <em>Q</em>(4, −2) noktasının koordinatları (7, −7)'dir.",
       "Axes translated to O'(-3, 5); the point Q(4, -2) has new coordinates (7, -7)")


# ============================================================ yeniden-eskiye
f, p = equal_fig((-2, 5), (-1, 8.2), 62, M_)
axes(p)
Op, R = (2, 3), (1, 7)
new_axes(p, Op)
p.arrow(O, Op, THEORY, 2.3, 9.5)
p.arrow(Op, R, NEW, 2.3, 9.5)
name_axes(p)
origin(p)
p.dot(Op, NEW)
p.dot(R, TEXT)
p.label(*Op, "O′(2, 3)", ("se", "sw", "ne"), color=NEW)
block(p, *R, [("eski (1, 7)", TEXT), ("yeni (−1, 4)", NEW)], ("n", "w", "nw"))
along_out(p, O, Op, "(2, 3)", (0, 3), THEORY)
along_out(p, Op, R, "(−1, 4)", (3, 6), NEW)
finish(f, "yeniden-eskiye",
       "Yeni koordinatları (−1, 4) olan nokta, eski sistemde (2, 3) + (−1, 4) = (1, 7) noktasıdır.",
       "Axes translated by (2, 3); the point with new coordinates (-1, 4) is (1, 7) in the old system")


# ============================================================ aci-korunur
f, p = equal_fig((-1, 6.2), (-1, 5.2), 76, M_)
axes(p, nums=False)
Op, I = (4, 1), (2, 2)
new_axes(p, Op)
rect = (p.xmin, p.xmax, p.ymin, p.ymax)
d1 = clip_line((0, 1), (1, 0.5), rect)
d2 = clip_line((0, -4), (1, 3), rect)
p.seg(*d1, THEORY, 2.3)
p.seg(*d2, BASE, 2.3)
t1, t2 = math.atan(0.5), math.atan(3)
p.angle(I, t1, t2, 0.8, TEXT, 1.5, head=True)
name_axes(p)
origin(p)
p.dot(Op, NEW)
p.dot(I, TEXT)
p.label(*Op, "O′", ("se", "sw", "ne", "nw"), color=NEW)
p.label(*d1[1], "d_1", ("n", "nw", "s", "sw"), size=NAME, color=THEORY)
p.label(*d2[1], "d_2", ("e", "w", "se", "sw"), size=NAME, color=BASE)
p.angle_label(I, t1, t2, 0.8, "α", "out", NAME)
finish(f, "aci-korunur",
       "Eksenler ötelenince <em>d</em><sub>1</sub> ile <em>d</em><sub>2</sub> doğrularının denklemleri değişir, "
       "eğimleri ve aralarındaki <em>α</em> açısı değişmez.",
       "Two lines d1 and d2 with the directed angle alpha between them, drawn with old and translated axes")


# ============================================================ alan-korunur
f, p = equal_fig((-1, 6.2), (-3, 5.2), 62, M_)
axes(p)
Op = (3, -2)
A, B, C = (1, 1), (5, 2), (2, 4)
new_axes(p, Op)
p.poly([A, B, C], THEORY, 0.16, THEORY, 2.0)
name_axes(p)
origin(p)
p.dot(Op, NEW)
for q in (A, B, C):
    p.dot(q, TEXT)
p.label(*Op, "O′(3, −2)", ("se", "sw", "ne", "nw"), color=NEW)
p.label(*A, "A", ("sw", "w", "s", "nw"))
p.label(*B, "B", ("e", "se", "ne"))
p.label(*C, "C", ("n", "nw", "ne"))
p.label(2.2, 2.4, "alan = 11/2", (dc(p, 2.22, 2.42),), size=NOTE, color=THEORY)
finish(f, "alan-korunur",
       "<em>ABC</em> üçgeninin alanı eski sistemde de, eksenler (3, −2) kadar ötelendikten sonra da 11/2'dir.",
       "Triangle A(1, 1), B(5, 2), C(2, 4) with area 11/2, drawn with old axes and axes translated to O'(3, -2)")


# ============================================================ dogru-yeni-sistem
f, p = equal_fig((-4, 5), (-2, 9), 50, M_)
axes(p)
Op = (1, 5)
new_axes(p, Op)
rect = (p.xmin, p.xmax, p.ymin, p.ymax)
d = clip_line((0, 3), (1, 2), rect)
p.seg(*d, THEORY, 2.3)
name_axes(p)
origin(p)
p.dot(Op, NEW)
p.label(*Op, "O′(1, 5)", ("se", "e", "s"), color=NEW)
block(p, 2.7, 8.4, [("d: 2x − y + 3 = 0", THEORY), ("y′ = 2x′", NEW)], ("se", "e"), gap=10)
finish(f, "dogru-yeni-sistem",
       "<em>d</em> doğrusu yeni başlangıç noktası <em>O</em>′(1, 5)'ten geçtiği için yeni denkleminde sabit terim yoktur.",
       "Line 2x - y + 3 = 0 passing through O'(1, 5); in the translated system its equation is y' = 2x'")


# ============================================================ cember-sadelestirme
f, p = equal_fig((-3, 9), (-8, 2.2), 48, M_)
axes(p)
C, r = (2, -3), 4
new_axes(p, C)
p.ring(C, r, THEORY, 2.3)
R = (C[0] + r * math.cos(D(-50)), C[1] + r * math.sin(D(-50)))
p.seg(C, R, THEORY, 1.4)
name_axes(p)
origin(p)
p.dot(C, NEW)
p.dot(R, THEORY, 3.4)
p.label(*C, "O′(2, −3)", ("nw", "ne", "sw", "se"), color=NEW)
along_out(p, C, R, "4", (C[0] - 2, C[1] - 3), THEORY, NAME)
block(p, 7, 0.9, [("x² + y² − 4x + 6y − 3 = 0", THEORY), ("x′² + y′² = 16", NEW)],
      (dc(p, 6.9, 1.2), dc(p, 6.6, -7.2), dc(p, -1.4, 1.3)))
finish(f, "cember-sadelestirme",
       "Eksenler çemberin merkezi <em>O</em>′(2, −3) noktasına ötelenince denklem <em>x</em>′² + <em>y</em>′² = 16 olur.",
       "Circle of radius 4 centred at O'(2, -3); with the axes translated to O' its equation is x'^2 + y'^2 = 16")


# ============================================================ uc-oteleme
f, p = equal_fig((-1, 7.2), (-2, 3.4), 66, M_)
axes(p)
P, S1, S2, E = (4, 2), (1, 0), (5, -1), (6, 2)
p.arrow(P, S1, THEORY, 2.3, 9.5)
p.arrow(S1, S2, PRACTICE, 2.3, 9.5)
p.arrow(S2, E, BASE, 2.3, 9.5)
p.arrow(P, E, TEXT, 2.6, 10, dash="7 5", opacity=0.85)
name_axes(p)
origin(p)
for q in (P, S1, S2, E):
    p.dot(q, TEXT)
p.label(*P, "P(4, 2)", ("nw", "n", "w"))
p.label(*S1, "(1, 0)", ("s", "sw", "se"), size=NOTE)
p.label(*S2, "(5, −1)", ("se", "s", "e"), size=NOTE)
p.label(*E, "(6, 2)", ("ne", "e", "n"), size=NOTE)
along_out(p, P, S1, "c", S2, THEORY, NAME)
along_out(p, S1, S2, "b", P, PRACTICE, NAME)
along_out(p, S2, E, "a", S1, BASE, NAME)
along_out(p, P, E, "a + b + c = (2, 0)", S2, TEXT)
finish(f, "uc-oteleme",
       "<em>P</em>(4, 2) noktasına sırasıyla <em>c</em>, <em>b</em> ve <em>a</em> ötelemeleri uygulanır; "
       "sonuç, <em>a</em> + <em>b</em> + <em>c</em> = (2, 0) kadar tek ötelemenin verdiği (6, 2) noktasıdır.",
       "P(4, 2) moved by c, then b, then a reaches (6, 2), the same as one move by a + b + c = (2, 0)")


# ============================================================ dogrularla-eksen
f, p = equal_fig((-6, 5.2), (-2, 7), 50, M_)
axes(p)
Op, P = (-4, 5), (3, 0)
p.seg((Op[0], 0), P, NEW, 4.5, opacity=0.35, weight=0)
p.seg(P, (P[0], Op[1]), NEW, 1.3, GUIDE, 0.85)
new_axes(p, Op)
name_axes(p)
origin(p)
p.dot(Op, NEW)
p.dot(P, TEXT)
p.label(*Op, "O′(−4, 5)", ("nw", "sw", "ne"), color=NEW)
p.label(p.xmax - 0.6, Op[1], "y = 5", ("n", "s"), size=NOTE, color=NEW)
p.label(Op[0], p.ymax - 0.5, "x = −4", ("e", "w"), size=NOTE, color=NEW)
block(p, *P, [("P: eski (3, 0)", TEXT), ("yeni (7, −5)", NEW)], ("ne", "e", "se"))
along_out(p, (Op[0], 0), P, "7", (0, -3), NEW, NAME, t=0.35)
along_out(p, P, (P[0], Op[1]), "5", (5, 2), NEW, NAME)
finish(f, "dogrularla-eksen",
       "<em>y</em> = 5 ve <em>x</em> = −4 doğruları yeni eksenler olunca başlangıç noktası <em>O</em>′(−4, 5) olur; "
       "<em>P</em>(3, 0) noktası yeni sistemde (7, −5)'tir.",
       "New axes y = 5 and x = -4 meeting at O'(-4, 5); the point P(3, 0) has new coordinates (7, -5)")


# ============================================================ denklem-i
f, p = equal_fig((-2, 8.2), (-4.6, 3.2), 56, M_)
axes(p)
Op = (2, -1)
new_axes(p, Op)
ts = lin(0, 2 * PI, 180)
p.line([(Op[0] + 3 * math.cos(t), Op[1] + math.sqrt(6) * math.sin(t)) for t in ts], THEORY, 2.3)
name_axes(p)
origin(p)
p.dot(Op, NEW)
p.label(*Op, "O′(2, −1)", ("nw", "ne", "sw", "se"), color=NEW)
block(p, 6, 2, [("2x² + 3y² − 8x + 6y = 7", THEORY), ("2x′² + 3y′² = 18", NEW)],
      (dc(p, 6.3, 2.45), dc(p, 6.3, -3.9), dc(p, -0.3, -3.9)))
finish(f, "denklem-i",
       "Eksenler (2, −1) kadar ötelenince eğrinin denklemi 2<em>x</em>′² + 3<em>y</em>′² = 18 olur; "
       "eğri <em>O</em>′ etrafında simetriktir.",
       "Closed curve 2x^2 + 3y^2 - 8x + 6y = 7 centred at O'(2, -1); in the translated system 2x'^2 + 3y'^2 = 18")


# ============================================================ denklem-ii
f, p = equal_fig((-3, 6.4), (-3, 6.2), 56, M_)
axes(p)
Op = (3, 2)
new_axes(p, Op)
rect = (p.xmin, p.xmax, p.ymin, p.ymax)
l1 = clip_line((0, 0), (1, 1), rect)
l2 = clip_line((0, 2), (1, -1), rect)
p.seg(*l1, THEORY, 2.3)
p.seg(*l2, THEORY, 2.3)
name_axes(p)
origin(p)
p.dot((1, 1), TEXT)
p.dot(Op, NEW)
p.label(1, 1, "(1, 1)", ("e", "w", "s"), size=NOTE)
p.label(*Op, "O′(3, 2)", ("se", "ne", "sw"), color=NEW)
block(p, 5.2, 5.2, [("y = x", THEORY), ("y′ = x′ + 1", NEW)], ("se", "e", "nw"))
block(p, -2.1, 4.1, [("y = 2 − x", THEORY), ("y′ = −x′ − 3", NEW)], ("sw", "ne", "w"))
finish(f, "denklem-ii",
       "Eğri <em>y</em> = <em>x</em> ve <em>y</em> = 2 − <em>x</em> doğrularından oluşur; yeni sistemde bu doğrular "
       "<em>y</em>′ = <em>x</em>′ + 1 ve <em>y</em>′ = −<em>x</em>′ − 3 olur.",
       "Pair of lines y = x and y = 2 - x meeting at (1, 1), with axes translated to O'(3, 2)")


# ============================================================ denklem-iii
f, p = equal_fig((-2, 9), (-7, 5.2), 50, M_)
axes(p)
Op, C, r = (2, -1), (3.5, 0.25), math.sqrt(277) / 4
new_axes(p, Op)
p.ring(C, r, THEORY, 2.3)
name_axes(p)
origin(p)
p.dot(Op, NEW)
p.dot(C, THEORY, 3.6)
p.label(*Op, "O′(2, −1)", ("sw", "se", "nw", "ne"), color=NEW)
p.label(*C, "(7/2, 1/4)", ("ne", "e", "n", "se"), size=NOTE, color=THEORY)
block(p, 5, -6, [("2x² + 2y² − 14x − y − 10 = 0", THEORY), ("2x′² + 2y′² − 6x′ − 5y′ − 27 = 0", NEW)],
      (dc(p, 4.6, -5.7), dc(p, 5.0, -6.2)))
finish(f, "denklem-iii",
       "Yeni başlangıç noktası <em>O</em>′(2, −1) çemberin merkezi (7/2, 1/4) değildir; bu yüzden yeni denklemde "
       "birinci dereceden terimler kalır.",
       "Circle with centre (7/2, 1/4) and axes translated to O'(2, -1), which is not the centre")


# ============================================================ birinci-dereceyi-yok-et
f, p = equal_fig((-12, 10), (-6.4, 12.4), 27, M_)
axes(p, step=2)
Op = (-1, 3)
new_axes(p, Op)
vs = lin(-12, 12, 480)
for sgn in (1, -1):
    curve(p, [(Op[0] + sgn * math.sqrt((102 + 4 * v * v) / 3), Op[1] + v) for v in vs], THEORY, 2.3)
name_axes(p)
origin(p)
p.dot(Op, NEW)
for sgn in (1, -1):
    p.dot((Op[0] + sgn * math.sqrt(34), Op[1]), THEORY, 3.6)
p.label(*Op, "O′(−1, 3)", ("ne", "nw", "se", "sw"), color=NEW)
block(p, 4, 11, [("3x² − 4y² + 6x + 24y = 135", THEORY), ("3x′² − 4y′² = 102", NEW)],
      (dc(p, 4.4, 10.6), dc(p, -5.8, 10.6), dc(p, 4.4, -4.6)))
finish(f, "birinci-dereceyi-yok-et",
       "Eksenler <em>O</em>′(−1, 3) noktasına ötelenince eğrinin denklemi 3<em>x</em>′² − 4<em>y</em>′² = 102 olur.",
       "Two-branch curve 3x^2 - 4y^2 + 6x + 24y = 135 with axes translated to O'(-1, 3)")


# ============================================================ parabol-sadelestir
f, p = equal_fig((-2.4, 8), (-10.2, 4.2), 44, M_)
axes(p)
Op = (1, -3)
new_axes(p, Op)
curve(p, [(Op[0] + v * v / 8, Op[1] + v) for v in lin(-8, 8, 320)], THEORY, 2.3)
name_axes(p)
origin(p)
p.dot(Op, NEW)
for q in ((3, 1), (3, -7)):
    p.dot(q, THEORY, 3.6)
p.label(3, 1, "(3, 1)", ("se", "e", "nw"), size=NOTE)
p.label(3, -7, "(3, −7)", ("ne", "e", "sw"), size=NOTE)
p.label(*Op, "O′", ("nw", "sw", "w"), color=NEW)
block(p, 5.4, -1.8, [("y² − 8x + 6y + 17 = 0", THEORY), ("y′² = 8x′", NEW)],
      (dc(p, 5.4, -1.75), dc(p, 5.4, -4.3)))
finish(f, "parabol-sadelestir",
       "Eksenler <em>O</em>′(1, −3) noktasına ötelenince denklem <em>y</em>′² = 8<em>x</em>′ olur; "
       "eğri (3, 1) ve (3, −7) noktalarından geçer.",
       "Open curve y^2 - 8x + 6y + 17 = 0 with vertex O'(1, -3); in the translated system y'^2 = 8x'")


# ============================================================ eksen-bileske
f, p = equal_fig((-0.8, 7.4), (-0.8, 4.4), 72, M_)
axes(p, nums=False)
O1, O2 = (2, 1), (3.5, 3)
new_axes(p, O1, NEW, ("X′", "Y′"))
new_axes(p, O2, BASE, ("X″", "Y″"), dash=DOTTED, width=1.9)
p.arrow(O, O1, NEW, 2.3, 9.5)
p.arrow(O1, O2, BASE, 2.3, 9.5)
p.arrow(O, O2, TEXT, 2.6, 10, dash="7 5", opacity=0.85)
name_axes(p)
origin(p)
p.dot(O1, NEW)
p.dot(O2, BASE)
p.label(*O1, "O′", ("se", "nw", "sw"), color=NEW)
p.label(*O2, "O″", ("se", "nw", "ne"), color=BASE)
along_out(p, O, O1, "(c, d)", O2, NEW, halo=True)
along_out(p, O1, O2, "(a, b)", (5, 1.5), BASE, halo=True)
along_out(p, O, O2, "(a + c, b + d)", O1, TEXT, halo=True)
finish(f, "eksen-bileske",
       "Önce (<em>c</em>, <em>d</em>), sonra (<em>a</em>, <em>b</em>) kadar ötelenen eksenler, "
       "(<em>a</em> + <em>c</em>, <em>b</em> + <em>d</em>) kadar tek ötelemeyle aynı yere gelir.",
       "Three coordinate systems: XY at O, X'Y' at O' = O + (c, d), X''Y'' at O'' = O' + (a, b) = O + (a + c, b + d)")


# ============================================================ iki-sira
f, p = equal_fig((-4, 6.2), (-6, 1.6), 56, M_)
axes(p)
A, B, E = (4, -1), (-2, -3), (2, -4)
new_axes(p, E, BASE, ("X″", "Y″"), xs=(E[0] - 1.6, E[0] + 2.4), ys=(E[1] - 1.6, E[1] + 2.0))
p.arrow(O, A, THEORY, 2.3, 9.5)
p.arrow(A, E, THEORY, 2.3, 9.5)
p.arrow(O, B, PRACTICE, 2.3, 9.5)
p.arrow(B, E, PRACTICE, 2.3, 9.5)
name_axes(p)
origin(p)
p.dot(A, THEORY)
p.dot(B, PRACTICE)
p.dot(E, TEXT, 4.8)
p.label(*A, "(4, −1)", ("ne", "e", "n"), size=NOTE)
p.label(*B, "(−2, −3)", ("sw", "w", "s"), size=NOTE)
p.label(*E, "O″(2, −4)", ("sw", "se", "s"), color=BASE)
along_out(p, O, A, "T_2", E, THEORY, NAME)
along_out(p, A, E, "T_1", O, THEORY, NAME)
along_out(p, O, B, "T_1", E, PRACTICE, NAME)
along_out(p, B, E, "T_2", O, PRACTICE, NAME)
finish(f, "iki-sira",
       "Başlangıç noktası önce <em>T</em><sub>2</sub> sonra <em>T</em><sub>1</sub> ile de, önce <em>T</em><sub>1</sub> "
       "sonra <em>T</em><sub>2</sub> ile de aynı <em>O</em>″(2, −4) noktasına taşınır.",
       "Two orders of the axis translations T1 = T(-2,-3) and T2 = T(4,-1) both move the origin to (2, -4)")


# ---------------------------------------------------------------------------
for name, content in OUT.items():
    with io.open(OUT_DIR / f"{PREFIX}{name}.md", "w", encoding="utf-8", newline="\n") as fh:
        fh.write(content)
print(f"generated {len(OUT)} figures:", ", ".join(OUT))
