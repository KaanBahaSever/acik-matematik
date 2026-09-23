# -*- coding: utf-8 -*-
"""
Figures for the "Döndürme ve Paralel Eksenler" chapter of Analitik Geometri
(dersler/analitik-geometri/dondurme-ve-paralel-eksenler.qmd).

The figures are NOT produced at build time. Run

    python scripts/analytic_figures/don.py
    python scripts/center_figures.py "analytic-don-*.md" --keep-width

and paste each scripts/_figures/analytic-don-<name>.md block into the .qmd.
Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box: a figure that illustrates a
definition sits directly below that box.

Every drawing uses one scale on both axes, so circles, ellipses, right angles
and rotated axes look true. Rotated axes are always drawn together with the
original ones, with an arc marking the rotation angle. Labels are placed by a
small collision-avoiding placer (Fig.label and friends); any label that could
not be placed cleanly is reported on the console.

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
PREFIX = "analytic-don-"
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


def origin(p, prefs=("sw", "se", "nw", "s", "w"), off=None):
    """Origin dot and its label; off = (dx, dy) pixel offset for crowded origins."""
    if off:
        p.dot((0, 0), TEXT)
        p.label(0, 0, "O", (("c", p.X(0) + off[0], p.Y(0) + off[1]),))
        return
    p.dot((0, 0), TEXT)
    p.label(0, 0, "O", prefs, gap=8)


DASH = "5 4"
THIN = 1.3


# ---------------------------------------------------------------------------
# chapter helpers
# ---------------------------------------------------------------------------
def u(t):
    return (math.cos(t), math.sin(t))


def sc(v, k):
    return (v[0] * k, v[1] * k)


def add(*vs):
    return (sum(v[0] for v in vs), sum(v[1] for v in vs))


def rot(pt, t, c=(0.0, 0.0)):
    x, y = pt[0] - c[0], pt[1] - c[1]
    return (c[0] + x * math.cos(t) - y * math.sin(t), c[1] + x * math.sin(t) + y * math.cos(t))


COMPASS = ["e", "ne", "n", "nw", "w", "sw", "s", "se"]


def compass(t):
    """Compass positions ordered by closeness to the direction t (radians)."""
    k = round((t % (2 * PI)) / (PI / 4)) % 8
    return (COMPASS[k], COMPASS[(k + 1) % 8], COMPASS[(k - 1) % 8], COMPASS[(k + 2) % 8], COMPASS[(k - 2) % 8])


def num(k):
    s = f"{k:g}".replace("-", "−")
    return s


def axis_nums(p, xs=(), ys=(), size=11, yright=False):
    """Tick numbers under the X-axis and left of the Y-axis."""
    for k in xs:
        s = num(k)
        w, h = p._wh(s, size)
        X, Y = p.X(k), p.Y(0)
        p._draw_text((X - w / 2, Y + 6, X + w / 2, Y + 6 + h), "middle", s, size, TEXT, False)
    for k in ys:
        s = num(k)
        w, h = p._wh(s, size)
        X, Y = p.X(0), p.Y(k)
        if yright:
            p._draw_text((X + 7, Y - h / 2, X + 7 + w, Y + h / 2), "start", s, size, TEXT, False)
        else:
            p._draw_text((X - 7 - w, Y - h / 2, X - 7, Y + h / 2), "end", s, size, TEXT, False)


def base_axes(p, xr, yr, xl="X", yl="Y", ticks=False, opacity=0.6):
    p.cart_axes(xr, yr, xl, yl, ticks=ticks, opacity=opacity)


def rot_axes(p, th, xr, yr, names=("X'", "Y'"), c=(0.0, 0.0), color=THEORY, width=1.5, opacity=0.9,
             xprefs=None, yprefs=None):
    """Axes through c in the directions th and th + pi/2, drawn from xr[0] to xr[1] (and yr)."""
    e1, e2 = u(th), u(th + PI / 2)
    x0, x1 = add(c, sc(e1, xr[0])), add(c, sc(e1, xr[1]))
    y0, y1 = add(c, sc(e2, yr[0])), add(c, sc(e2, yr[1]))
    p.arrow(x0, x1, color, width, 8.5, opacity=opacity)
    p.arrow(y0, y1, color, width, 8.5, opacity=opacity)
    if names[0]:
        p.label(*x1, names[0], xprefs or compass(th), gap=8, size=AXIS, color=color)
    if names[1]:
        p.label(*y1, names[1], yprefs or compass(th + PI / 2), gap=8, size=AXIS, color=color)


def ang(p, c, a0, a1, r, s, color=TEXT, head=False, side="out", size=NAME, fs=None, width=1.5):
    p.angle(c, a0, a1, r, color, width, head=head)
    if s:
        kw = {} if fs is None else {"fs": fs}
        p.angle_label(c, a0, a1, r, s, side, size, color, **kw)


def dash(p, a, b, color=TEXT, opacity=0.6, width=THIN):
    p.seg(a, b, color, width, DASH, opacity)


def eq_tick(p, a, b, t=0.5, n=1, color=TEXT):
    """Small cross-strokes on segment ab marking equal lengths."""
    A, B = p.px(a), p.px(b)
    ux, uy = p._unit(A, B)
    nx, ny = -uy, ux
    for k in range(n):
        off = (k - (n - 1) / 2) * 4
        Mx, My = A[0] + (B[0] - A[0]) * t + ux * off, A[1] + (B[1] - A[1]) * t + uy * off
        p.add(f'<line x1="{Mx - nx * 6:.1f}" y1="{My - ny * 6:.1f}" x2="{Mx + nx * 6:.1f}" y2="{My + ny * 6:.1f}" '
              f'stroke="{color}" stroke-width="1.5"/>')
        p.fig.segs.append(([(Mx - nx * 6, My - ny * 6), (Mx + nx * 6, My + ny * 6)], 1.0))


def tick_on(p, pt, t, color=THEORY, s=4.0):
    """Tick mark at pt across an axis of direction t."""
    X, Y = p.px(pt)
    nx, ny = math.sin(t), math.cos(t)          # pixel unit normal of an axis with direction t
    p.add(f'<line x1="{X - s * nx:.1f}" y1="{Y - s * ny:.1f}" x2="{X + s * nx:.1f}" y2="{Y + s * ny:.1f}" '
          f'stroke="{color}" stroke-width="1.4"/>')
    p.fig.segs.append(([(X - s * nx, Y - s * ny), (X + s * nx, Y + s * ny)], 0.4))


def clipped(p, pt, d, color, width=2.2, rect=None, opacity=1.0):
    r = rect or (p.xmin, p.xmax, p.ymin, p.ymax)
    s = clip_line(pt, d, r)
    p.seg(s[0], s[1], color, width, None, opacity)
    return s


def curve(p, f, t0, t1, n=240):
    return [f(t0 + (t1 - t0) * k / n) for k in range(n + 1)]


def in_rect(pts, rect):
    xmin, xmax, ymin, ymax = rect
    return [q for q in pts if xmin <= q[0] <= xmax and ymin <= q[1] <= ymax]


def at_px(p, X, Y, s, size=NOTE, color=TEXT, anchor="middle", halo=False):
    """Label centred at pixel (X, Y)."""
    w, h = p._wh(s, size)
    x0 = {"middle": X - w / 2, "start": X, "end": X - w}[anchor]
    box = (x0, Y - h / 2, x0 + w, Y + h / 2)
    if p.fig.cost(box) > 0:
        print(f"  note: fixed label '{s}' collides (cost {p.fig.cost(box):.0f})")
    p._draw_text(box, anchor, s, size, color, halo)


E = "<em>{}</em>".format


# ============================================================ donme-tanimi
M, P = (1.0, 1.0), (4.0, 2.0)
Pp = rot(P, PI / 3, M)
aP = math.atan2(P[1] - M[1], P[0] - M[0])
f, p = equal_fig((0.35, 4.75), (0.4, 4.5), 110, (40, 30, 40, 30))
p.line(arc_pts(M, math.dist(M, P), aP - 0.12, aP + PI / 3 + 0.12), TEXT, 1.0, DASH, 0.35, weight=0.3)
p.arrow(M, P, THEORY, 2.0, 9)
p.arrow(M, Pp, THEORY, 2.0, 9)
eq_tick(p, M, P, 0.55)
eq_tick(p, M, Pp, 0.55)
ang(p, M, aP, aP + PI / 3, 0.75, "θ", PRACTICE, head=True)
p.dot(M, TEXT)
p.dot(P, THEORY, 4.6)
p.dot(Pp, PRACTICE, 4.6)
p.label(*M, "M", ("sw", "w", "s"), gap=8)
p.label(*P, "P", ("e", "se", "ne"), gap=8)
p.label(*Pp, "P'", ("nw", "w", "n"), gap=8)
f.out("donme-tanimi",
      f"{E('M')} merkezli {E('θ')} radyanlık dönme {E('P')}'yi, {E('M')}'ye uzaklığı aynı kalacak ve "
      f"{E('MP')}'den {E('MP')}'ne açı {E('θ')} olacak biçimde {E('P')}'ne götürür.",
      aria="Rotation about M by angle theta takes P to P prime; MP and MP prime have equal length")


# ============================================================ donme-orijin
P = (3.0, 1.0)
Pp = rot(P, PI / 6)
aP = math.atan2(1, 3)
f, p = equal_fig((-0.5, 3.8), (-0.5, 3.0), 118, (45, 40, 50, 35))
base_axes(p, (-0.5, 3.8), (-0.5, 3.0))
dash(p, P, (P[0], 0))
dash(p, P, (0, P[1]))
dash(p, Pp, (Pp[0], 0), PRACTICE, 0.75)
dash(p, Pp, (0, Pp[1]), PRACTICE, 0.75)
p.arrow((0, 0), P, THEORY, 2.0, 9)
p.arrow((0, 0), Pp, PRACTICE, 2.0, 9)
ang(p, (0, 0), 0, aP, 0.62, "α", TEXT, fs=(0, 0.1, -0.1))
ang(p, (0, 0), aP, aP + PI / 6, 1.15, "θ", PRACTICE, head=True)
origin(p)
p.dot(P, THEORY, 4.6)
p.dot(Pp, PRACTICE, 4.6)
p.label(P[0], 0, "x", ("s",), gap=7)
p.label(0, P[1], "y", ("w",), gap=8)
p.label(Pp[0], 0, "x'", ("s",), gap=7, color=PRACTICE)
p.label(0, Pp[1], "y'", ("w",), gap=8, color=PRACTICE)
p.along((0, 0), P, "r", 1, t=0.6, size=NAME)
p.along((0, 0), Pp, "r", 1, t=0.6, size=NAME)
p.label(*P, "P(x, y)", ("e", "se", "ne"))
p.label(*Pp, "P'(x', y')", ("ne", "e", "n"))
f.out("donme-orijin",
      f"{E('P')}'nin kutupsal açısı {E('α')}, {E('P')}'nünkü {E('α')} + {E('θ')}'dır; ikisinin de "
      f"{E('O')}'ya uzaklığı {E('r')}'dir.",
      aria="Rotation about the origin: P(x,y) at polar angle alpha and P prime at alpha plus theta, both at distance r")


# ============================================================ donme-bes-pi-bolu-dort
S2 = math.sqrt(2)
P, Pp = (2.0, S2), (1 - S2, -1 - S2)
aP = math.atan2(P[1], P[0])
f, p = equal_fig((-3.0, 3.0), (-3.2, 2.6), 82, (45, 40, 50, 35))
base_axes(p, (-3.0, 3.0), (-3.2, 2.6), ticks=True)
axis_nums(p, (-2, -1, 1, 2), (-2, -1, 1, 2), yright=True)
p.ring((0, 0), math.sqrt(6), TEXT, 1.1, DASH, 0.35, weight=0.3)
p.seg((0, 0), P, THEORY, 2.0)
p.seg((0, 0), Pp, PRACTICE, 2.0)
ang(p, (0, 0), aP, aP + 5 * PI / 4, 0.55, "5π/4", PRACTICE, head=True, size=NOTE, fs=(0, -0.1, 0.1, -0.2))
origin(p, ("se", "s", "sw"))
p.dot(P, THEORY, 4.6)
p.dot(Pp, PRACTICE, 4.6)
p.label(*P, "P(2, √2)", ("e", "se", "ne"), halo=True)
p.label(*Pp, "P'(1 − √2, −1 − √2)", ("se", "e", "s"), halo=True)
f.out("donme-bes-pi-bolu-dort",
      f"{E('P')}(2, √2) noktası {E('O')} etrafında 5{E('π')}/4 döndürülünce {E('P')}'(1 − √2, −1 − √2) "
      f"noktasına gider; iki nokta da yarıçapı √6 olan çember üzerindedir.",
      aria="Point P(2, sqrt 2) rotated by 5 pi over 4 about O to P prime(1 - sqrt 2, -1 - sqrt 2) on the circle of radius sqrt 6")


# ============================================================ ters-donme
P, Pp = (3.0, 1.0), (-1.0, 3.0)
aP = math.atan2(1, 3)
f, p = equal_fig((-2.0, 4.0), (-0.5, 3.8), 85, (45, 40, 50, 35))
base_axes(p, (-2.0, 4.0), (-0.5, 3.8), ticks=True)
axis_nums(p, (-1, 1, 2, 3), (1, 2, 3))
p.seg((0, 0), P, THEORY, 2.0)
p.seg((0, 0), Pp, PRACTICE, 2.0)
p.right_angle((0, 0), P, Pp, 11)
ang(p, (0, 0), aP, aP + PI / 2, 0.85, "π/2", PRACTICE, head=True, size=NOTE)
origin(p, ("sw", "se", "s"))
p.dot(P, THEORY, 4.6)
p.dot(Pp, PRACTICE, 4.6)
p.label(*P, "P(3, 1)", ("e", "ne", "se"))
p.label(*Pp, "P'(−1, 3)", ("w", "nw", "sw"))
f.out("ters-donme",
      f"{E('π')}/2 radyanlık dönme {E('P')}(3, 1)'i {E('P')}'(−1, 3)'e götürür; (2) formülleri {E('P')}'nden "
      f"{E('P')}'ye geri döndürür.",
      aria="Quarter turn about O takes P(3,1) to P prime(-1,3)")


# ============================================================ donme-m-etrafinda
M, P = (2.0, 1.0), (5.0, 2.0)
R = (P[0] - M[0], P[1] - M[1])
Rp = rot(R, PI / 3)
Pp = add(Rp, M)
aR = math.atan2(R[1], R[0])
f, p = equal_fig((-0.5, 5.9), (-0.5, 4.6), 92, (45, 40, 50, 35))
base_axes(p, (-0.5, 5.9), (-0.5, 4.6))
p.arrow((0, 0), M, TEXT, 1.4, 8, dash="6 4", opacity=0.75)
p.arrow(P, R, TEXT, 1.1, 7, dash="4 3", opacity=0.55)
p.arrow(Rp, Pp, TEXT, 1.1, 7, dash="4 3", opacity=0.55)
p.seg(M, P, THEORY, 2.0)
p.seg(M, Pp, THEORY, 2.0)
p.seg((0, 0), R, BASE, 2.0)
p.seg((0, 0), Rp, BASE, 2.0)
ang(p, M, aR, aR + PI / 3, 0.6, "θ", PRACTICE, head=True)
ang(p, (0, 0), aR, aR + PI / 3, 0.6, "θ", PRACTICE, head=True)
origin(p)
for q, c in ((M, TEXT), (P, THEORY), (Pp, THEORY), (R, BASE), (Rp, BASE)):
    p.dot(q, c, 4.4)
p.along((0, 0), M, "OM", -1, t=0.55, size=NOTE)
p.label(*M, "M(h, k)", ("nw", "w", "n"))
p.label(*P, "P(x, y)", ("e", "ne", "se"))
p.label(*R, "R", ("se", "s", "e"), gap=8)
p.label(*Rp, "R'", ("nw", "w", "n"), gap=8)
p.label(*Pp, "P'(x', y')", ("ne", "n", "e"))
f.out("donme-m-etrafinda",
      f"{E('P')} önce −{E('OM')} kadar ötelenip {E('R')}'ye, {E('R')} başlangıç etrafında {E('θ')} döndürülüp "
      f"{E('R')}'ne, {E('R')}' de {E('OM')} kadar ötelenip {E('P')}'ne götürülür.",
      aria="Rotation about M reduced to a translation, a rotation about O and a translation back", css=WIDE)


# ============================================================ m-etrafinda-dik
M, P, Pp = (1.0, 4.0), (2.0, 3.0), (2.0, 5.0)
f, p = equal_fig((-1.4, 4.0), (-0.5, 5.9), 84, (45, 40, 50, 35))
base_axes(p, (-1.4, 4.0), (-0.5, 5.9), ticks=True)
axis_nums(p, (-1, 1, 2, 3), (1, 2, 3, 4, 5))
p.line(arc_pts(M, S2, -PI / 4 - 0.25, PI / 4 + 0.25), TEXT, 1.0, DASH, 0.35, weight=0.3)
p.seg(M, P, THEORY, 2.0)
p.seg(M, Pp, PRACTICE, 2.0)
p.right_angle(M, P, Pp, 10)
ang(p, M, -PI / 4, PI / 4, 0.62, "π/2", PRACTICE, head=True, size=NOTE)
origin(p)
p.dot(M, TEXT)
p.dot(P, THEORY, 4.6)
p.dot(Pp, PRACTICE, 4.6)
p.label(*M, "M(1, 4)", ("w", "nw", "sw"))
p.label(*P, "P(2, 3)", ("se", "e", "s"))
p.label(*Pp, "P'(2, 5)", ("ne", "e", "n"))
f.out("m-etrafinda-dik",
      f"{E('P')}(2, 3), {E('M')}(1, 4) etrafında {E('π')}/2 döndürülünce {E('P')}'(2, 5) olur; {E('MP')} ile "
      f"{E('MP')}' eşit uzunlukta ve diktir.",
      aria="P(2,3) rotated a quarter turn about M(1,4) gives P prime(2,5)")


# ============================================================ m-etrafinda-pi-bolu-dort
M, A = (1.0, -1.0), (3.0, 1.0)
Ap = (1.0, 2 * S2 - 1)
f, p = equal_fig((-0.9, 4.1), (-1.8, 2.7), 100, (45, 40, 50, 35))
base_axes(p, (-0.9, 4.1), (-1.8, 2.7), ticks=True)
axis_nums(p, (3,), (-1, 1, 2))
dash(p, M, (3.9, -1.0), TEXT, 0.45)
p.line(arc_pts(M, 2 * S2, PI / 4 - 0.2, PI / 2 + 0.2), TEXT, 1.0, DASH, 0.35, weight=0.3)
p.seg(M, A, THEORY, 2.0)
p.seg(M, Ap, PRACTICE, 2.0)
ang(p, M, 0, PI / 4, 0.55, "π/4", TEXT, size=NOTE)
ang(p, M, PI / 4, PI / 2, 1.05, "π/4", PRACTICE, head=True, size=NOTE)
origin(p, ("nw", "sw", "w"))
p.dot(M, TEXT)
p.dot(A, THEORY, 4.6)
p.dot(Ap, PRACTICE, 4.6)
p.label(*M, "M(1, −1)", ("w", "sw", "nw"))
p.label(*A, "A(3, 1)", ("e", "se", "ne"))
p.label(*Ap, "A'(1, 2√2 − 1)", ("nw", "w", "n", "ne"), halo=True)
f.out("m-etrafinda-pi-bolu-dort",
      f"{E('A')}(3, 1), {E('M')}(1, −1) etrafında {E('π')}/4 döndürülünce {E('A')}'(1, 2√2 − 1) olur; "
      f"{E('MA')}' düşeydir.",
      aria="A(3,1) rotated by pi over 4 about M(1,-1) gives A prime(1, 2 sqrt 2 - 1)")


# ============================================================ eksen-dondurme
T = PI / 6
f, p = equal_fig((-3.2, 3.5), (-2.5, 3.5), 80, (40, 35, 45, 30))
base_axes(p, (-3.2, 3.5), (-2.5, 3.5))
rot_axes(p, T, (-2.6, 3.3), (-2.4, 3.2))
p.right_angle((0, 0), u(T), u(T + PI / 2), 11, THEORY)
ang(p, (0, 0), 0, T, 1.3, "θ", PRACTICE, head=True)
ang(p, (0, 0), PI / 2, PI / 2 + T, 1.3, "θ", PRACTICE, head=True)
origin(p, ("sw", "s", "w"))
f.out("eksen-dondurme",
      f"{E('XY')} sistemi {E('θ')} kadar döndürülünce {E('X')}'{E('Y')}' sistemi elde edilir; yeni eksenler de "
      f"birbirine diktir.",
      aria="Coordinate axes X, Y and the axes X prime, Y prime rotated by theta about O")


# ============================================================ eksen-dondurme-koordinatlar
T = PI / 6
P = (2.0, 3.0)
xp, yp = P[0] * math.cos(T) + P[1] * math.sin(T), -P[0] * math.sin(T) + P[1] * math.cos(T)
Fx, Fy = sc(u(T), xp), sc(u(T + PI / 2), yp)
f, p = equal_fig((-2.0, 4.3), (-0.8, 4.0), 90, (45, 40, 50, 35))
base_axes(p, (-2.0, 4.3), (-0.8, 4.0))
rot_axes(p, T, (-1.2, 4.3), (-0.8, 3.5))
dash(p, P, (P[0], 0))
dash(p, P, (0, P[1]))
dash(p, P, Fx, THEORY, 0.8)
dash(p, P, Fy, THEORY, 0.8)
p.right_angle(Fx, (0, 0), P, 9, THEORY)
p.right_angle(Fy, (0, 0), P, 9, THEORY)
p.seg((0, 0), P, PRACTICE, 2.0)
ang(p, (0, 0), 0, T, 0.7, "θ", THEORY, fs=(0, 0.12, -0.12))
ang(p, (0, 0), 0, math.atan2(3, 2), 1.3, "φ", PRACTICE, fs=(0.15, 0.25, 0.05, 0.35))
origin(p, ("sw", "s", "se"))
p.dot(P, PRACTICE, 4.6)
p.dot(Fx, THEORY, 3.4)
p.dot(Fy, THEORY, 3.4)
p.label(P[0], 0, "x", ("s",), gap=7)
p.label(0, P[1], "y", ("w", "nw"), gap=8)
p.label(*Fx, "x'", ("se", "e", "s"), gap=8, color=THEORY)
p.label(*Fy, "y'", ("sw", "w", "s"), gap=8, color=THEORY)
p.along((0, 0), P, "r", -1, t=0.72, size=NAME)
p.label(*P, "P(x, y) = P'(x', y')", ("ne", "n", "e", "nw"), halo=True)
f.out("eksen-dondurme-koordinatlar",
      f"Aynı {E('P')} noktası: {E('XY')} sisteminde kutupsal açısı {E('φ')}, {E('X')}'{E('Y')}' sisteminde "
      f"{E('φ')} − {E('θ')}; {E('O')}'ya uzaklığı iki sistemde de {E('r')}'dir.",
      aria="Point P with its projections on the old axes X, Y and on the rotated axes X prime, Y prime")


# ============================================================ eksen-pi-bolu-alti
T = PI / 6
P = (math.sqrt(3), 1.0)
f, p = equal_fig((-1.3, 3.1), (-0.8, 2.2), 125, (40, 35, 45, 30))
base_axes(p, (-1.3, 3.1), (-0.8, 2.2))
rot_axes(p, T, (-0.8, 2.95), (-0.6, 2.05))
for k in (1, 2):
    tick_on(p, sc(u(T), k), T)
    X, Y = p.px(sc(u(T), k))
    n = (math.sin(T), math.cos(T))
    at_px(p, X + n[0] * 14 + math.cos(T) * 12, Y + n[1] * 14 - math.sin(T) * 12, str(k), 11, THEORY)
dash(p, P, (P[0], 0))
dash(p, P, (0, P[1]))
ang(p, (0, 0), 0, T, 0.75, "π/6", PRACTICE, head=True, size=NOTE)
origin(p, ("sw", "s", "w"))
p.dot(P, PRACTICE, 4.6)
p.label(P[0], 0, "√3", ("s",), gap=7, size=NOTE)
p.label(0, P[1], "1", ("w",), gap=8, size=NOTE)
p.label(*P, "P(√3, 1) = P'(2, 0)", ("nw", "n", "w"), halo=True)
f.out("eksen-pi-bolu-alti",
      f"Eksenler {E('π')}/6 döndürülünce {E('P')}(√3, 1) yeni {E('X')}'-ekseni üzerine düşer ve yeni "
      f"koordinatları (2, 0) olur.",
      aria="Axes rotated by pi over 6; the point P(sqrt 3, 1) lies on the new X prime axis at distance 2")


# ============================================================ aci-korunur
T = PI / 12
K = (3.0, 2.0)
F1, F2 = PI / 6, 5 * PI / 12
XR, YR = (-1.25, 5.6), (-0.5, 4.4)
PPU = 43
W = round(2 * (XR[1] - XR[0]) * PPU + 40 + 60 + 40)
H = round((YR[1] - YR[0]) * PPU + 50 + 30)
f = Fig(W, H)
for i in range(2):
    p = f.panel(40 + i * ((XR[1] - XR[0]) * PPU + 60), 50, XR, YR, PPU)
    base_axes(p, XR, YR)
    rot_axes(p, T, (-0.4, 5.5), (-0.4, 4.35), xprefs=("ne", "n", "e"), yprefs=("ne", "e", "n"))
    rect = (XR[0], XR[1], YR[0], YR[1])
    s1 = clipped(p, K, u(F1), BASE, 2.2)
    s2 = clipped(p, K, u(F2), PRACTICE, 2.2)
    ref = 0 if i == 0 else T
    col = TEXT if i == 0 else THEORY
    dash(p, K, add(K, sc(u(ref), 2.1)), col, 0.75)
    if i == 0:
        ang(p, K, ref, F1, 1.0, "φ_1", col, size=NOTE, fs=(0, 0.2, -0.2, 0.35))
        ang(p, K, ref, F2, 1.6, "φ_2", col, size=NOTE, fs=(0.1, 0.25, 0.4, 0))
    else:
        ang(p, K, ref, F1, 1.0, "", col)
        ang(p, K, ref, F2, 1.6, "", col)
        m1 = add(K, sc(u((ref + F1) / 2), 1.0))
        m2 = add(K, sc(u((ref + F2) / 2), 1.6))
        p.label(*m1, "φ_1 − θ", (("c", p.X(4.75), p.Y(1.78)),), size=NOTE, color=col, leader=True)
        p.label(*m2, "φ_2 − θ", (("c", p.X(4.45), p.Y(4.12)),), size=NOTE, color=col, leader=True)
    ang(p, K, F1 + PI, F2 + PI, 0.8, "α", PRACTICE, head=True, fs=(0, 0.15, -0.15))
    p.dot(K, TEXT)
    p.label(*K, "K", ("se", "e", "s"), gap=8)
    p.label(*s1[1], "d_1", ("n", "nw", "w"), gap=7, color=BASE)
    p.label(*s2[1], "d_2", ("e", "ne", "w"), gap=7, color=PRACTICE)
    p.label(0, 0, "O", ("sw", "s", "w"), gap=8)
    p.dot((0, 0), TEXT, 3.4)
    title = "XY sistemine göre" if i == 0 else "X'Y' sistemine göre"
    at_px(p, p.x0 + p.w / 2, p.y0 - 30, title, NOTE, TEXT)
f.out("aci-korunur",
      f"Eksenler {E('θ')} döndürülünce her doğrunun eğim açısı {E('θ')} kadar azalır; {E('d')}<sub>1</sub>'den "
      f"{E('d')}<sub>2</sub>'ye yönlenmiş açı {E('α')} değişmez.",
      aria="Two lines through K: slope angles measured from the X direction and from the rotated X prime direction; the angle alpha between them is unchanged",
      css=WIDE)


# ============================================================ cember-dondurme
T = PI / 3
f, p = equal_fig((-4.2, 4.2), (-4.2, 4.2), 60, (40, 35, 45, 30))
base_axes(p, (-4.2, 4.2), (-4.2, 4.2))
rot_axes(p, T, (-4.1, 4.1), (-4.1, 4.1))
p.ring((0, 0), 3, PRACTICE, 2.4)
for k, name in ((0, "X"), (PI / 2, "Y"), (T, "X'"), (T + PI / 2, "Y'")):
    col = TEXT if name in ("X", "Y") else THEORY
    for sgn in (1, -1):
        q = sc(u(k), 3 * sgn)
        p.dot(q, col, 3.2)
        t = k if sgn > 0 else k + PI
        # label outside the circle, beside the axis (rotated a little counter-clockwise)
        lp = sc(u(t + 0.17), 3.5)
        X, Y = p.px(lp)
        at_px(p, X, Y, "3" if sgn > 0 else "−3", 11.5, col)
ang(p, (0, 0), 0, T, 0.85, "π/3", THEORY, head=True, size=NOTE)
origin(p, off=(10, 19))
f.out("cember-dondurme",
      f"{E('x')}² + {E('y')}² = 9 çemberi eksenler {E('π')}/3 döndürüldükten sonra da "
      f"{E('x')}'² + {E('y')}'² = 9 denklemiyle anlatılır.",
      aria="Circle of radius 3 about O with the axes X, Y and the axes rotated by pi over 3")


# ============================================================ dik-dogru
XR, YR = (-1.6, 5.0), (-4.8, 3.2)
f, p = equal_fig(XR, YR, 70, (45, 40, 50, 35))
p.arrow((0, 0), (XR[0], 0), THEORY, 1.4, 8.5, opacity=0.6)
p.arrow((0, 0), (0, YR[1]), THEORY, 1.4, 8.5, opacity=0.6)
p.arrow((XR[0], 0), (XR[1], 0), TEXT, 1.2, 8, opacity=0.6)
p.arrow((0, YR[0]), (0, YR[1]), TEXT, 1.2, 8, opacity=0.6)
p.label(XR[1], 0, "X", ("e", "se", "ne"), gap=8, size=AXIS)
p.label(0, YR[1], "Y", ("ne", "e"), gap=8, size=AXIS)
p.label(0, YR[1], "X'", ("nw", "w"), gap=8, size=AXIS, color=THEORY)
p.label(XR[0], 0, "Y'", ("nw", "n", "sw"), gap=8, size=AXIS, color=THEORY)
d1 = clipped(p, (4, 0), (-2, 1), PRACTICE, 2.3)
d2 = clipped(p, (2, 0), (1, 2), BASE, 2.3)
K = (12 / 5, 4 / 5)
p.right_angle(K, (4, 0), (2, 0), 10)
ang(p, (0, 0), 0, PI / 2, 0.6, "π/2", THEORY, head=True, size=NOTE)
origin(p, ("sw", "s", "se"))
p.dot(K, TEXT)
p.label(*K, "K", ("e", "ne", "se"), gap=9)
p.label(*d1[0], "d: x + 2y − 4 = 0", ("s", "sw", "w"), gap=7, size=NOTE, color=PRACTICE, halo=True)
p.label(*d2[0], "2x − y − 4 = 0", ("e", "se", "ne"), gap=7, size=NOTE, color=BASE, halo=True)
f.out("dik-dogru",
      f"Eksenler {E('π')}/2 döndürülünce {E('d')}'nin yeni denklemi 2{E('x')}' − {E('y')}' − 4 = 0 olur; bu "
      f"denklem {E('XY')}'de okunduğunda {E('d')}'ye dik bir doğru belirtir. İki doğru {E('K')}(12/5, 4/5)'te "
      f"dik kesişir.",
      aria="Line x + 2y - 4 = 0 and the perpendicular line 2x - y - 4 = 0 meeting at K; the axes turned by a quarter turn")


# ============================================================ xy-bir
T = PI / 4
f, p = equal_fig((-4.0, 4.0), (-4.0, 4.0), 60, (40, 35, 45, 30))
base_axes(p, (-4.0, 4.0), (-4.0, 4.0))
rot_axes(p, T, (-4.0, 4.1), (-4.0, 4.1), xprefs=("ne", "e", "n"), yprefs=("nw", "w", "n"))
for sgn in (1, -1):
    br = curve(p, lambda x: (sgn * x, sgn / x), 0.25, 4.0)
    p.line(br, PRACTICE, 2.5)
ang(p, (0, 0), 0, T, 0.85, "π/4", THEORY, head=True, size=NOTE)
origin(p, off=(22, 9))
p.dot((1, 1), PRACTICE, 4.4)
p.dot((-1, -1), PRACTICE, 4.4)
p.label(1, 1, "(1, 1)", ("e", "se", "n"), gap=8)
p.label(-1, -1, "(−1, −1)", ("w", "nw", "s"), gap=8)
p.label(1, 1, "x' = √2", ("nw", "w", "n"), gap=8, size=NOTE, color=THEORY)
p.label(3.0, 1 / 3.0, "x​y = 1", ("ne", "n", "e"), gap=8, size=NOTE, color=PRACTICE, halo=True)
p.label(3.0, 1 / 3.0, "x'² − y'² = 2", (("c", p.X(3.0), p.Y(1 / 3.0) - 44),), size=NOTE, color=THEORY, halo=True)
f.out("xy-bir",
      f"Eksenler {E('π')}/4 döndürülünce {E('xy')} = 1 eğrisinin denklemi {E('x')}'² − {E('y')}'² = 2 olur; "
      f"eğri yeni eksenlere göre simetrik durur.",
      aria="Hyperbola xy = 1 with axes rotated by pi over 4; vertices (1,1) and (-1,-1)")


# ============================================================ dikten-paralele
T, AL = D(20), D(60)
e1p, e2p = u(T), u(T + AL)
P = add(sc(e1p, 3), sc(e2p, 1.5))
A, B = sc(e1p, 3), sc(e2p, 1.5)
f, p = equal_fig((-0.8, 5.0), (-0.8, 5.0), 100, (40, 35, 50, 30))
base_axes(p, (-0.8, 5.0), (-0.8, 5.0))
p.right_angle((0, 0), (1, 0), (0, 1), 9)
p.arrow(sc(e1p, -0.8), sc(e1p, 4.8), THEORY, 1.5, 8.5, opacity=0.9)
p.arrow(sc(e2p, -0.8), sc(e2p, 4.9), THEORY, 1.5, 8.5, opacity=0.9)
p.label(*sc(e1p, 4.8), "X'", ("e", "ne", "se"), gap=8, size=AXIS, color=THEORY)
p.label(*sc(e2p, 4.9), "Y'", ("ne", "e", "n"), gap=8, size=AXIS, color=THEORY)
dash(p, P, A, THEORY, 0.85)
dash(p, P, B, THEORY, 0.85)
dash(p, P, (P[0], 0))
dash(p, P, (0, P[1]))
p.arrow((0, 0), (1, 0), TEXT, 2.6, 10)
p.arrow((0, 0), (0, 1), TEXT, 2.6, 10)
p.arrow((0, 0), e1p, THEORY, 2.6, 10)
p.arrow((0, 0), e2p, THEORY, 2.6, 10)
ang(p, (0, 0), 0, T, 1.55, "θ", PRACTICE, fs=(0, 0.15, -0.15))
ang(p, (0, 0), T, T + AL, 1.55, "α", PRACTICE, fs=(0, 0.15, -0.15))
origin(p, ("sw", "s", "w"))
p.dot(P, PRACTICE, 4.6)
p.dot(A, THEORY, 3.6)
p.dot(B, THEORY, 3.6)
p.label(1, 0, "e_1", ("s", "se"), gap=8)
p.label(0, 1, "e_2", ("w", "nw"), gap=8)
p.label(*e1p, "e_1'", ("se", "s", "e"), gap=6, color=THEORY)
p.label(*e2p, "e_2'", ("e", "ne", "se"), gap=6, color=THEORY)
p.label(*A, "A", ("se", "s", "e"), gap=7, color=THEORY)
p.label(*A, "x'", ("nw", "n"), gap=7, size=NOTE, color=THEORY)
p.label(*B, "B", ("w", "nw", "sw"), gap=7, color=THEORY)
p.label(*B, "y'", ("n", "nw", "ne"), gap=7, size=NOTE, color=THEORY)
p.label(P[0], 0, "x", ("s",), gap=7)
p.label(0, P[1], "y", ("w",), gap=8)
p.label(*P, "P(x, y) = P'(x', y')", ("ne", "e", "n"), halo=True)
f.out("dikten-paralele",
      f"Dik sistemde {E('P')}'nin koordinatları dikmelerle ({E('x')}, {E('y')}), eğik sistemde eksenlere "
      f"paralellerle ({E('x')}', {E('y')}') okunur; {E('OP')} = {E('x')} {E('e')}<sub>1</sub> + {E('y')} "
      f"{E('e')}<sub>2</sub> = {E('x')}' {E('e')}<sub>1</sub>' + {E('y')}' {E('e')}<sub>2</sub>'.",
      aria="Right-angled axes X, Y and oblique axes X prime, Y prime with their unit vectors; point P read in both systems",
      css=WIDE)


# ============================================================ kisitlama
T, AL = PI / 4, 2 * PI / 3
e1p, e2p = u(T), u(T + AL)
P = add(e1p, e2p)
f, p = equal_fig((-1.6, 1.8), (-1.6, 1.8), 145, (40, 35, 45, 30))
base_axes(p, (-1.6, 1.8), (-1.6, 1.8))
p.arrow(sc(e1p, -1.45), sc(e1p, 1.75), THEORY, 1.4, 8.5, opacity=0.75)
p.arrow(sc(e2p, -1.45), sc(e2p, 1.65), THEORY, 1.4, 8.5, opacity=0.75)
p.label(*sc(e1p, 1.75), "X'", ("ne", "e", "n"), gap=8, size=AXIS, color=THEORY)
p.label(*sc(e2p, 1.65), "Y'", ("nw", "w", "n"), gap=8, size=AXIS, color=THEORY)
p.poly([(0, 0), e1p, P, e2p], THEORY, 0.07)
dash(p, e1p, P, THEORY, 0.8)
dash(p, e2p, P, THEORY, 0.8)
p.arrow((0, 0), e1p, THEORY, 2.8, 11)
p.arrow((0, 0), e2p, THEORY, 2.8, 11)
ang(p, (0, 0), 0, T, 0.33, "θ = π/4", PRACTICE, size=NOTE, fs=(-0.1, 0, -0.25))
ang(p, (0, 0), T, T + AL, 0.5, "α = 2π/3", PRACTICE, size=NOTE, fs=(0.1, 0, 0.2, -0.1))
origin(p, ("se", "s", "sw"))
p.dot(P, PRACTICE, 4.6)
p.label(*e1p, "e_1'", ("se", "e", "s"), gap=7, color=THEORY)
p.label(*e2p, "e_2'", ("s", "sw", "w"), gap=7, color=THEORY)
p.label(*P, "P'(1, 1)", ("n", "nw", "ne"), halo=True)
f.out("kisitlama",
      f"{E('θ')} + {E('α')} = 11{E('π')}/12 &gt; {E('π')}/2 olsa da {E('e')}<sub>2</sub>' = (cos({E('θ')} + "
      f"{E('α')}), sin({E('θ')} + {E('α')})) yazılır ve (7) formülleri geçerli kalır.",
      aria="Oblique axes with theta pi over 4 and alpha 2 pi over 3; the parallelogram on e1 prime and e2 prime ends in the second quadrant")


# ============================================================ egik-nokta
T, AL = PI / 6, PI / 6
e1p, e2p = u(T), u(T + AL)
P = add(sc(e1p, 2), e2p)
A, B = sc(e1p, 2), e2p
f, p = equal_fig((-0.9, 3.2), (-0.5, 2.8), 135, (55, 35, 45, 30))
base_axes(p, (-0.9, 3.2), (-0.5, 2.8))
p.arrow(sc(e1p, -0.5), sc(e1p, 3.25), THEORY, 1.5, 8.5, opacity=0.9)
p.arrow(sc(e2p, -0.5), sc(e2p, 3.0), THEORY, 1.5, 8.5, opacity=0.9)
p.label(*sc(e1p, 3.25), "X'", ("e", "ne", "se"), gap=8, size=AXIS, color=THEORY)
p.label(*sc(e2p, 3.0), "Y'", ("ne", "e", "n"), gap=8, size=AXIS, color=THEORY)
for k in (1, 2):
    tick_on(p, sc(e1p, k), T)
    X, Y = p.px(sc(e1p, k))
    at_px(p, X + math.sin(T) * 14, Y + math.cos(T) * 14, str(k), 11, THEORY)
tick_on(p, e2p, T + AL)
X, Y = p.px(e2p)
at_px(p, X - math.sin(T + AL) * 13, Y - math.cos(T + AL) * 13, "1", 11, THEORY)
dash(p, P, A, THEORY, 0.85)
dash(p, P, B, THEORY, 0.85)
dash(p, P, (P[0], 0))
dash(p, P, (0, P[1]))
ang(p, (0, 0), 0, T, 0.55, "π/6", PRACTICE, size=NOTE, fs=(0, 0.15, -0.15))
ang(p, (0, 0), T, T + AL, 0.9, "π/6", PRACTICE, size=NOTE, fs=(0, 0.15, -0.15))
origin(p, off=(14, 14))
p.dot(P, PRACTICE, 4.6)
p.label(P[0], 0, "√3 + 1/2", ("s",), gap=7, size=NOTE)
p.label(0, P[1], "1 + √3/2", ("w",), gap=8, size=NOTE)
p.label(*P, "P'(2, 1)", ("ne", "e", "n"))
f.out("egik-nokta",
      f"{E('θ')} = {E('α')} = {E('π')}/6 olan eğik sistemde paralel koordinatları (2, 1) olan noktanın dik "
      f"koordinatları (√3 + 1/2, 1 + √3/2)'dir.",
      aria="Oblique system with theta = alpha = pi over 6; point with parallel coordinates (2,1)")


# ============================================================ farkli-baslangic
T, AL = D(20), D(60)
Op = (2.0, 1.5)
e1p, e2p = u(T), u(T + AL)
f, p = equal_fig((-0.5, 6.0), (-0.5, 5.0), 92, (40, 35, 50, 30))
base_axes(p, (-0.5, 6.0), (-0.5, 5.0))
dash(p, (0.8, Op[1]), (5.9, Op[1]), TEXT, 0.4)
dash(p, (Op[0], 0.3), (Op[0], 4.9), TEXT, 0.4)
p.label(5.9, Op[1], "X*", ("se", "e", "s"), gap=6, size=NOTE)
p.label(Op[0], 4.9, "Y*", ("nw", "w", "n"), gap=6, size=NOTE)
dash(p, Op, (Op[0], 0), TEXT, 0.55)
dash(p, Op, (0, Op[1]), TEXT, 0.55)
p.arrow(add(Op, sc(e1p, -1.0)), add(Op, sc(e1p, 3.9)), THEORY, 1.5, 8.5, opacity=0.9)
p.arrow(add(Op, sc(e2p, -1.0)), add(Op, sc(e2p, 3.4)), THEORY, 1.5, 8.5, opacity=0.9)
p.label(*add(Op, sc(e1p, 3.9)), "X'", ("e", "ne", "se"), gap=8, size=AXIS, color=THEORY)
p.label(*add(Op, sc(e2p, 3.4)), "Y'", ("ne", "e", "n"), gap=8, size=AXIS, color=THEORY)
p.arrow((0, 0), Op, PRACTICE, 1.4, 8, dash="6 4", opacity=0.8)
ang(p, Op, 0, T, 1.25, "θ", PRACTICE, fs=(0, 0.15, -0.15))
ang(p, Op, T, T + AL, 1.25, "α", PRACTICE, fs=(0, 0.15, -0.15))
origin(p, ("sw", "s", "w"))
p.dot(Op, PRACTICE, 4.6)
p.label(Op[0], 0, "a", ("s",), gap=7)
p.label(0, Op[1], "b", ("w",), gap=8)
p.label(*Op, "O'(a, b)", ("se", "s", "sw"), halo=True)
f.out("farkli-baslangic",
      f"Başlangıçlar farklıysa {E('XY')} önce {E('O')}'({E('a')}, {E('b')})'ye ötelenip {E('X')}*{E('Y')}* "
      f"elde edilir; {E('X')}*{E('Y')}* ile eğik {E('X')}'{E('Y')}' sisteminin başlangıcı ortaktır.",
      aria="Oblique system with origin O prime(a,b); the translated axes X star, Y star through O prime",
      css=WIDE)


# ============================================================ farkli-baslangic-ornek
AL = PI / 3
Op = (1.0, 2.0)
e2p = u(AL)
P = (4.0, 2 + math.sqrt(3))
A, B = (3.0, 2.0), add(Op, sc(e2p, 2))
f, p = equal_fig((-0.5, 5.1), (-0.5, 4.7), 98, (40, 35, 45, 30))
base_axes(p, (-0.5, 5.1), (-0.5, 4.7))
p.arrow((0.3, 2.0), (5.1, 2.0), THEORY, 1.5, 8.5, opacity=0.9)
p.arrow(add(Op, sc(e2p, -1.1)), add(Op, sc(e2p, 2.85)), THEORY, 1.5, 8.5, opacity=0.9)
p.label(5.1, 2.0, "X'", ("e", "ne", "se"), gap=8, size=AXIS, color=THEORY)
p.label(*add(Op, sc(e2p, 2.85)), "Y'", ("nw", "w", "n"), gap=8, size=AXIS, color=THEORY)
for k in (1, 2):
    tick_on(p, (1 + k, 2.0), 0)
    tick_on(p, add(Op, sc(e2p, k)), AL)
dash(p, P, A, THEORY, 0.85)
dash(p, P, B, THEORY, 0.85)
ang(p, Op, 0, AL, 0.5, "π/3", PRACTICE, size=NOTE, fs=(0, 0.15, -0.15))
origin(p, ("sw", "s", "w"))
p.dot(Op, PRACTICE, 4.6)
p.dot(P, PRACTICE, 4.6)
p.dot(A, THEORY, 3.4)
p.dot(B, THEORY, 3.4)
p.label(*Op, "O'(1, 2)", ("s", "sw", "se"), halo=True)
p.label(*P, "P(4, 2 + √3) = P'(2, 2)", ("n", "nw", "ne"), halo=True)
f.out("farkli-baslangic-ornek",
      f"Başlangıcı {E('O')}'(1, 2) ve eksen açısı {E('π')}/3 olan eğik sistemde {E('P')}(4, 2 + √3) noktasının "
      f"paralel koordinatları (2, 2)'dir.",
      aria="Oblique system with origin O prime(1,2) and axis angle pi over 3; the point P(4, 2 + sqrt 3) has parallel coordinates (2,2)")


# ============================================================ goruntuden-nokta
T = PI / 6
Pp = (2.0, 1.0)
P = rot(Pp, -T)
aP = math.atan2(P[1], P[0])
f, p = equal_fig((-0.5, 2.9), (-0.7, 1.6), 150, (40, 35, 45, 30))
base_axes(p, (-0.5, 2.9), (-0.7, 1.6))
p.line(arc_pts((0, 0), math.sqrt(5), aP - 0.1, aP + T + 0.1), TEXT, 1.0, DASH, 0.35, weight=0.3)
p.seg((0, 0), P, THEORY, 2.0)
p.seg((0, 0), Pp, PRACTICE, 2.0)
eq_tick(p, (0, 0), P, 0.5)
eq_tick(p, (0, 0), Pp, 0.5)
ang(p, (0, 0), aP, aP + T, 1.0, "π/6", PRACTICE, head=True, size=NOTE)
origin(p, ("nw", "sw", "w"))
p.dot(P, THEORY, 4.6)
p.dot(Pp, PRACTICE, 4.6)
p.label(*P, "P", ("se", "e", "s"), gap=8)
p.label(*Pp, "P'(2, 1)", ("ne", "n", "e"))
f.out("goruntuden-nokta",
      f"{E('O')} etrafında {E('π')}/6 döndürülünce {E('P')}'(2, 1)'e giden nokta "
      f"{E('P')}((2√3 + 1)/2, (√3 − 2)/2)'dir; |{E('OP')}| = |{E('OP')}'| = √5.",
      aria="Point P rotated by pi over 6 about O onto P prime(2,1)")


# ============================================================ exr-pi-bolu-alti
T = PI / 6
P = (3.0, 5.0)
xp, yp = P[0] * math.cos(T) + P[1] * math.sin(T), -P[0] * math.sin(T) + P[1] * math.cos(T)
Fx, Fy = sc(u(T), xp), sc(u(T + PI / 2), yp)
f, p = equal_fig((-2.4, 6.1), (-0.6, 5.8), 64, (45, 35, 45, 30))
base_axes(p, (-2.4, 6.1), (-0.6, 5.8))
rot_axes(p, T, (-0.8, 6.3), (-0.6, 3.45))
dash(p, P, (P[0], 0))
dash(p, P, (0, P[1]))
dash(p, P, Fx, THEORY, 0.85)
dash(p, P, Fy, THEORY, 0.85)
p.right_angle(Fx, (0, 0), P, 9, THEORY)
p.right_angle(Fy, (0, 0), P, 9, THEORY)
ang(p, (0, 0), 0, T, 0.95, "π/6", PRACTICE, head=True, size=NOTE)
origin(p, ("sw", "s", "se"))
p.dot(P, PRACTICE, 4.6)
p.dot(Fx, THEORY, 3.4)
p.dot(Fy, THEORY, 3.4)
p.label(P[0], 0, "3", ("s",), gap=7, size=NOTE)
p.label(0, P[1], "5", ("w", "nw"), gap=8, size=NOTE)
p.label(*Fx, "x' ≈ 5,10", ("se", "e", "s"), gap=8, size=NOTE, color=THEORY)
p.label(*Fy, "y' ≈ 2,83", ("sw", "w", "s"), gap=8, size=NOTE, color=THEORY, halo=True)
p.label(*P, "P(3, 5)", ("ne", "n", "e"))
f.out("exr-pi-bolu-alti",
      f"Eksenler {E('π')}/6 döndürülünce {E('P')}(3, 5)'in yeni koordinatları ((3√3 + 5)/2, (5√3 − 3)/2) "
      f"≈ (5,10; 2,83) olur.",
      aria="Point P(3,5) projected on the axes and on the axes rotated by pi over 6")


# ============================================================ exr-egimi-bir
XR, YR = (-3.8, 4.2), (-1.5, 4.2)
f, p = equal_fig(XR, YR, 66, (45, 40, 45, 30))
p.arrow((0, 0), (XR[0], 0), THEORY, 1.4, 8.5, opacity=0.6)
p.arrow((0, 0), (0, YR[1]), THEORY, 1.4, 8.5, opacity=0.6)
p.arrow((XR[0], 0), (XR[1], 0), TEXT, 1.2, 8, opacity=0.6)
p.arrow((0, YR[0]), (0, YR[1]), TEXT, 1.2, 8, opacity=0.6)
p.label(XR[1], 0, "X", ("e", "se", "ne"), gap=8, size=AXIS)
p.label(0, YR[1], "Y", ("ne", "e"), gap=8, size=AXIS)
p.label(0, YR[1], "X'", ("nw", "w"), gap=8, size=AXIS, color=THEORY)
p.label(XR[0], 0, "Y'", ("nw", "n", "sw"), gap=8, size=AXIS, color=THEORY)
d = clipped(p, (3, 0), (-1, 1), PRACTICE, 2.4)
ang(p, (0, 0), 0, PI / 2, 0.7, "π/2", THEORY, head=True, size=NOTE)
origin(p, ("sw", "s", "se"))
p.dot((0, 3), THEORY, 4.2)
p.dot((3, 0), THEORY, 4.2)
p.label(0, 3, "x' = 3", ("w", "nw", "sw"), gap=8, size=NOTE, color=THEORY, halo=True)
p.label(3, 0, "y' = −3", ("s", "se", "sw"), gap=8, size=NOTE, color=THEORY)
lab = p.label(*d[1], "d: x + y − 3 = 0", ("sw", "w"), gap=10, size=NOTE, color=PRACTICE, halo=True)
p.label(*d[1], "x' − y' − 3 = 0", (("c", (lab[0] + lab[2]) / 2, lab[3] + 11),), size=NOTE, color=THEORY, halo=True)
f.out("exr-egimi-bir",
      f"Eksenler {E('π')}/2 döndürülünce {E('x')} + {E('y')} − 3 = 0 doğrusu {E('X')}'{E('Y')}' sisteminde "
      f"{E('x')}' − {E('y')}' − 3 = 0 olur ve eğimi 1'dir.",
      aria="Line x + y - 3 = 0 with the axes turned by a quarter turn; it meets X prime at x prime = 3 and Y prime at y prime = -3")


# ============================================================ exr-karma-terim-elips
T = PI / 6
e1p, e2p = u(T), u(T + PI / 2)
f, p = equal_fig((-2.6, 2.6), (-2.6, 2.6), 88, (40, 35, 45, 30))
base_axes(p, (-2.6, 2.6), (-2.6, 2.6))
rot_axes(p, T, (-2.75, 2.75), (-2.4, 2.4))
ell = [add(sc(e1p, 2 * math.cos(t)), sc(e2p, math.sin(t))) for t in (2 * PI * k / 240 for k in range(241))]
p.line(ell, PRACTICE, 2.5)
ang(p, (0, 0), 0, T, 0.6, "π/6", PRACTICE, head=True, size=NOTE, fs=(0, 0.15, -0.15))
origin(p, off=(19, 11))
V = {"x' = 2": sc(e1p, 2), "x' = −2": sc(e1p, -2), "y' = 1": e2p, "y' = −1": sc(e2p, -1)}
prefs = {"x' = 2": ("se", "s", "e"), "x' = −2": ("nw", "n", "w"), "y' = 1": ("nw", "w", "n"),
         "y' = −1": ("se", "e", "s")}
for s, q in V.items():
    p.dot(q, THEORY, 4.0)
    p.label(*q, s, prefs[s], gap=8, size=NOTE, color=THEORY, halo=True)
q = add(sc(e1p, 2 * math.cos(2.2)), sc(e2p, math.sin(2.2)))
p.label(*q, "x'² + 4y'² = 4", (("c", p.X(1.8), p.Y(-1.45)),), size=NOTE, color=PRACTICE, halo=True)
f.out("exr-karma-terim-elips",
      f"7{E('x')}² − 6√3{E('xy')} + 13{E('y')}² = 16 eğrisi, eksenler {E('π')}/6 döndürülünce "
      f"{E('x')}'² + 4{E('y')}'² = 4 denklemiyle yazılır.",
      aria="Ellipse with semi-axes 2 and 1 along the axes rotated by pi over 6")


# ============================================================ exr-karma-terim-parabol
c3, s4 = 3 / 5, 4 / 5
T = math.atan2(4, 3)
e1p, e2p = (c3, s4), (-s4, c3)


def to_xy(a, b):
    return add(sc(e1p, a), sc(e2p, b))


f, p = equal_fig((-3.0, 4.0), (-2.0, 5.5), 70, (40, 35, 45, 30))
base_axes(p, (-3.0, 4.0), (-2.0, 5.5))
rot_axes(p, T, (-2.4, 6.6), (-2.2, 3.6), xprefs=("e", "ne", "se"))
par = [to_xy(a, (a * a - 2 * a) / 6) for a in (-2.5 + 7.5 * k / 240 for k in range(241))]
p.line(par, PRACTICE, 2.5)
V = to_xy(1, -1 / 6)
Q = to_xy(2, 0)
ang(p, (0, 0), 0, T, 0.45, "θ", PRACTICE, head=True, fs=(-0.1, 0, -0.25))
origin(p, off=(9, 18))
p.dot(V, PRACTICE, 4.4)
p.dot(Q, PRACTICE, 4.4)
p.label(*V, "tepe", ("se", "e", "s"), gap=8, size=NOTE, halo=True)
p.label(*Q, "(6/5, 8/5)", ("e", "se", "ne"), gap=8, size=NOTE, halo=True)
p.label(*to_xy(4.4, (4.4 ** 2 - 8.8) / 6), "x'² − 2x' − 6y' = 0", ("e", "se", "ne"), gap=10, size=NOTE,
        color=PRACTICE, halo=True)
f.out("exr-karma-terim-parabol",
      f"Eksenler {E('θ')} = arctan(4/3) kadar döndürülünce 9{E('x')}² + 24{E('xy')} + 16{E('y')}² + 90{E('x')} − "
      f"130{E('y')} = 0 eğrisi {E('x')}'² − 2{E('x')}' − 6{E('y')}' = 0 olur; eğrinin simetri ekseni "
      f"{E('Y')}'-eksenine paraleldir.",
      aria="Parabola x prime squared - 2 x prime - 6 y prime = 0 in axes rotated by arctan 4/3")


# ============================================================ exr-paralelden-dike
A45 = PI / 4
A, P, Hh = (1.0, 0.0), (1 + S2, S2), (1 + S2, 0.0)
Bq = (S2, S2)
f, p = equal_fig((-1.0, 3.6), (-1.0, 2.5), 118, (40, 35, 60, 30))
p.arrow((-1.0, 0), (3.6, 0), TEXT, 1.2, 8, opacity=0.6)
p.arrow((0, -1.0), (0, 2.5), TEXT, 1.2, 8, opacity=0.6)
p.label(3.6, 0, "X = X'", ("e", "se", "ne"), gap=8, size=AXIS)
p.label(0, 2.5, "Y", ("ne", "nw"), gap=8, size=AXIS)
p.arrow(sc(u(A45), -1.0), sc(u(A45), 3.2), THEORY, 1.5, 8.5, opacity=0.9)
p.label(*sc(u(A45), 3.2), "Y'", ("ne", "e", "n"), gap=8, size=AXIS, color=THEORY)
p.seg(A, P, THEORY, 2.3)
dash(p, P, Bq, THEORY, 0.85)
dash(p, P, Hh, TEXT, 0.7)
p.right_angle(Hh, A, P, 9)
ang(p, (0, 0), 0, A45, 0.5, "π/4", PRACTICE, size=NOTE, fs=(0, 0.15, -0.15))
ang(p, A, 0, A45, 0.45, "π/4", PRACTICE, size=NOTE, fs=(0, 0.15, -0.15))
origin(p, ("sw", "s", "nw"))
p.dot(A, THEORY, 4.2)
p.dot(Hh, TEXT, 3.6)
p.dot(Bq, THEORY, 3.6)
p.dot(P, PRACTICE, 4.6)
p.label(*A, "A(1, 0)", ("s", "sw", "se"), gap=8)
p.label(*Hh, "H", ("s", "se"), gap=8)
p.label(*P, "P'(1, 2)", ("ne", "n", "e"))
p.label(*Bq, "2", ("nw", "w"), gap=7, size=NOTE, color=THEORY)
p.along(A, Hh, "x_1", -1, t=0.45, size=NOTE)
p.along(Hh, P, "y_1", -1, t=0.5, size=NOTE)
p.along(A, P, "2", 1, t=0.5, size=NOTE, color=THEORY)
f.out("exr-paralelden-dike",
      f"Eksen açısı {E('π')}/4 olan eğik sistemde {E('P')}'(1, 2) noktası; {E('AHP')} dik üçgeninden "
      f"{E('x')}<sub>1</sub> = {E('y')}<sub>1</sub> = √2 ve {E('P')}(1 + √2, √2) bulunur.",
      aria="Oblique system with axis angle pi over 4; right triangle AHP gives x1 = y1 = sqrt 2")


# ============================================================ exr-oteleme-hiperbol
Op = (0.5, 0.5)
f, p = equal_fig((-4.0, 4.5), (-4.0, 4.5), 62, (40, 35, 45, 30))
base_axes(p, (-4.0, 4.5), (-4.0, 4.5))
p.arrow((-3.9, Op[1]), (4.5, Op[1]), THEORY, 1.5, 8.5, opacity=0.9)
p.arrow((Op[0], -3.9), (Op[0], 4.5), THEORY, 1.5, 8.5, opacity=0.9)
p.label(4.5, Op[1], "X'", ("ne", "e", "n"), gap=8, size=AXIS, color=THEORY)
p.label(Op[0], 4.5, "Y'", ("ne", "e"), gap=8, size=AXIS, color=THEORY)
for lo, hi in ((-4.4, -0.45), (0.45, 4.0)):
    br = in_rect([(Op[0] + a, Op[1] - 1.75 / a) for a in (lo + (hi - lo) * k / 240 for k in range(241))],
                 (-4.0, 4.5, -4.0, 4.5))
    p.line(br, PRACTICE, 2.5)
origin(p, ("sw", "s", "w"))
p.dot(Op, THEORY, 4.4)
p.label(*Op, "O'(1/2, 1/2)", ("ne", "e", "n"), halo=True)
p.label(-2.4, 2.4, "2x'y' + 7/2 = 0", (("c", p.X(-2.4), p.Y(2.4)),), size=NOTE, color=PRACTICE)
f.out("exr-oteleme-hiperbol",
      f"Eksenler {E('O')}'(1/2, 1/2)'ye ötelenince 2{E('xy')} − {E('x')} − {E('y')} + 4 = 0 eğrisinin denklemi "
      f"2{E('x')}'{E('y')}' + 7/2 = 0 olur.",
      aria="Hyperbola 2xy - x - y + 4 = 0 with the axes translated to O prime(1/2, 1/2)")


# ============================================================ exr-oteleme-elips
Op = (-2.5, 1.5)
f, p = equal_fig((-6.0, 1.5), (-1.0, 4.5), 74, (40, 35, 45, 30))
base_axes(p, (-6.0, 1.5), (-1.0, 4.5))
p.arrow((-5.95, Op[1]), (1.5, Op[1]), THEORY, 1.5, 8.5, opacity=0.9)
p.arrow((Op[0], -0.95), (Op[0], 4.5), THEORY, 1.5, 8.5, opacity=0.9)
p.label(1.5, Op[1], "X'", ("ne", "e", "n"), gap=8, size=AXIS, color=THEORY)
p.label(Op[0], 4.5, "Y'", ("ne", "e"), gap=8, size=AXIS, color=THEORY)
ka, kb = math.sqrt(6.5), math.sqrt(3.25)
ell = [(Op[0] + ka * math.cos(t) - kb * math.sin(t), Op[1] + kb * math.sin(t))
       for t in (2 * PI * k / 240 for k in range(241))]
p.line(ell, PRACTICE, 2.5)
origin(p, ("se", "s", "sw"))
p.dot(Op, THEORY, 4.4)
p.label(*Op, "O'(−5/2, 3/2)", ("se", "s", "sw"), halo=True)
qe = ell[70]
p.label(*qe, "x'² + 2x'y' + 3y'² = 13/2", (("c", p.X(-4.45), p.Y(4.1)),),
        size=NOTE, color=PRACTICE, halo=True, leader=True)
f.out("exr-oteleme-elips",
      f"Eksenler {E('O')}'(−5/2, 3/2)'ye ötelenince birinci dereceden terimler kaybolur; elipsin merkezi yeni "
      f"başlangıç noktasıdır.",
      aria="Tilted ellipse centred at O prime(-5/2, 3/2) with the translated axes")


# ============================================================ exr-arctan-dort-bolu-uc
f, p = equal_fig((-4.5, 3.0), (-2.3, 5.0), 70, (40, 35, 45, 30))
base_axes(p, (-4.5, 3.0), (-2.3, 5.0))
rot_axes(p, T, (-2.6, 3.9), (-2.0, 5.0), xprefs=("e", "ne", "se"), yprefs=("n", "nw", "w"))
par = [to_xy(a, a * a / 4) for a in (-3.4 + 7.0 * k / 240 for k in range(241))]
p.line(par, PRACTICE, 2.5)
Q1, Q2 = to_xy(2, 1), to_xy(-2, 1)
ang(p, (0, 0), 0, T, 0.6, "θ", PRACTICE, head=True, fs=(0, 0.15, -0.15))
origin(p, off=(9, 18))
p.dot(Q1, PRACTICE, 4.4)
p.dot(Q2, PRACTICE, 4.4)
p.label(*Q1, "(2, 1)", ("e", "se", "ne"), gap=8, size=NOTE, color=THEORY, halo=True)
p.label(*Q2, "(−2, 1)", ("s", "sw", "se"), gap=8, size=NOTE, color=THEORY, halo=True)
p.label(-1.1, 4.3, "x'² = 4y'", (("c", p.X(-1.1), p.Y(4.3)),), size=NOTE, color=PRACTICE)
f.out("exr-arctan-dort-bolu-uc",
      f"Eksenler arctan(4/3) döndürülünce 9{E('x')}² + 24{E('xy')} + 16{E('y')}² + 80{E('x')} − 60{E('y')} = 0 "
      f"eğrisinin denklemi {E('x')}'² = 4{E('y')}' olur; parabolün ekseni {E('Y')}'-eksenidir. İşaretli "
      f"noktaların yanındaki sayılar yeni ({E('x')}', {E('y')}') koordinatlarıdır.",
      aria="Parabola x prime squared = 4 y prime in axes rotated by arctan 4/3")


# ---------------------------------------------------------------------------
for name, content in OUT.items():
    with io.open(OUT_DIR / f"{PREFIX}{name}.md", "w", encoding="utf-8", newline="\n") as fh:
        fh.write(content)
print(f"generated {len(OUT)} figures:", ", ".join(OUT))
