# -*- coding: utf-8 -*-
"""
Figures for the "Paralel ve Kutupsal Koordinatlar" chapter of Analitik Geometri
(dersler/analitik-geometri/paralel-ve-kutupsal-koordinatlar.qmd).

The figures are NOT produced at build time. Run

    python scripts/analytic_figures/pkk.py
    python scripts/center_figures.py "analytic-pkk-*.md" --keep-width

and paste each scripts/_figures/analytic-pkk-<name>.md block into the .qmd.
Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box: a figure that illustrates a
definition sits directly below that box.

Every drawing uses one scale on both axes, so circles, right angles and the
oblique axes look true. Labels are placed by a small collision-avoiding
placer (Fig.label and friends): each label tries its preferred positions and
takes the first one that touches no drawn line, point or other label. Any
label that could not be placed cleanly is reported on the console.

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
PREFIX = "analytic-pkk-"
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


def origin(p, prefs=("sw", "se", "nw", "s", "w")):
    p.dot((0, 0), TEXT)
    p.label(0, 0, "O", prefs, gap=8)


DASH = "5 4"
THIN = 1.3


# ============================================================ paralel-sistem
A60 = D(60)
f, p = equal_fig((-1.0, 6.3), (-0.75, 3.15), 74)
p.oblique_axes(A60, (-1, 6), (-0.8, 3.5), grid=((-1.0, 6.0), (-0.72, 3.1)))
P = obl(3, 2, A60)
Xp, Yp = (3, 0), obl(0, 2, A60)
p.seg(obl(3, -0.45, A60), P, TEXT, THIN, DASH, 0.75)
p.seg(obl(-0.45, 2, A60), P, TEXT, THIN, DASH, 0.75)
p.angle((0, 0), 0, A60, 0.5, THEORY, 1.5)
p.angle(Xp, 0, A60, 0.5, THEORY, 1.5)
p.dot(Xp, THEORY)
p.dot(Yp, THEORY)
p.dot(P, PRACTICE, 4.6)
p.label(6.0, 0, "X", ("e", "se"), gap=8, size=AXIS)
p.label(*obl(0, 3.5, A60), "Y", ("ne", "e", "n"), gap=8, size=AXIS)
p.label(0, 0, "O", (("c", p.X(0) - 22, p.Y(0) + 13), "nw", "se"), gap=8)
p.label(*P, "P(x, y)", ("ne", "e", "n"))
p.label(*Xp, "x", ("se", "s", "sw"), gap=8)
p.label(*Yp, "y", ("nw", "w", "n"), gap=8)
p.angle_label((0, 0), 0, A60, 0.5, "α", "out", NAME, THEORY)
p.angle_label(Xp, 0, A60, 0.5, "α", "out", NAME, THEORY)
f.out("paralel-sistem",
      "Paralel koordinat sistemi: eksenler arasındaki açı <em>α</em>. <em>P</em>'den eksenlere paralel "
      "çizilen kesikli doğrular <em>X</em>-eksenini <em>x</em>'te, <em>Y</em>-eksenini <em>y</em>'de keser; "
      "<em>P</em>'nin koordinatları (<em>x</em>, <em>y</em>) olur. Soluk ızgara çizgileri de eksenlere paraleldir.",
      aria="Oblique coordinate system with axes at angle alpha; point P and its parallel projections x and y")


# ============================================================ benzerlikler
f, p = equal_fig((-4.2, 5.3), (-2.3, 2.85), 57, (60, 50, 90, 50))
p.oblique_axes(A60, (-4, 5), (-2.5, 3), grid=((-4.2, 5.0), (-2.2, 2.75)))
P, Pp = obl(2, 1, A60), obl(-2, -1, A60)
for Q, u, v in ((P, 2, 1), (Pp, -2, -1)):
    p.seg(Q, (u, 0), TEXT, THIN, DASH, 0.7)
    p.seg(Q, obl(0, v, A60), TEXT, THIN, DASH, 0.7)
p.seg(Pp, P, PRACTICE, 1.6, "6 4", 0.9)
s = clip_line((3, 0), (math.cos(A60), math.sin(A60)), (-4.2, 5.0, -2.3, 2.75))
p.seg(*s, BASE, 2.2)
p.seg((-4.1, math.sqrt(3)), (5.0, math.sqrt(3)), THEORY, 2.2)
p.angle((0, 0), 0, A60, 1.25, TEXT, 1.3)
p.dot((0, 0), TEXT)
p.dot(P, PRACTICE, 4.6)
p.dot(Pp, PRACTICE, 4.6)
p.label(5.0, 0, "X", ("e", "se"), gap=8, size=AXIS)
p.label(*obl(0, 3, A60), "Y", ("ne", "e", "nw"), gap=8, size=AXIS)
p.label(0, 0, "O", ("se", "s", "e"), gap=8)
p.label(*P, "P(2, 1)", ("n", "nw", "ne", "se"))
p.label(*Pp, "P'(−2, −1)", ("sw", "w", "s", "nw"))
p.label(*s[1], "x = 3", ("n", "ne", "e", "w"), gap=8, size=NOTE, color=BASE)
p.label(-4.1, math.sqrt(3), "y = 2", ("n", "ne", "nw"), gap=7, size=NOTE, color=THEORY)
p.angle_label((0, 0), 0, A60, 1.25, "α = π/3", "out", NOTE, fs=(0.12, 0.2, 0.28, 0))
f.out("benzerlikler",
      "<em>α</em> = <em>π</em>/3 olan eğik sistemde <em>P</em>(2, 1) ile <em>P</em>'(−2, −1) noktaları "
      "<em>O</em>'ya göre simetriktir (kesikli paralelkenarlar). <em>x</em> = 3 doğrusu <em>Y</em>-eksenine, "
      "<em>y</em> = 2 doğrusu <em>X</em>-eksenine paraleldir.",
      aria="Oblique system: points P(2,1) and P'(-2,-1) symmetric about O, lines x = 3 and y = 2 parallel to the axes")


# ============================================================ y-eksenine-gore-simetri
f, p = equal_fig((-1.8, 1.8), (-0.62, 1.45), 150, (60, 50, 60, 70))
p.oblique_axes(A60, (-1.8, 1.8), (-0.6, 1.6), ticks=False)
P, Pp, S, B = (1, 0), obl(-1, 1, A60), (-1, 0), obl(0, 1, A60)
M = (0.25, math.sqrt(3) / 4)
p.poly([(0, 0), S, Pp], BASE, 0.16)
p.seg((0, 0), Pp, BASE, 1.8)
p.seg(S, Pp, TEXT, THIN, DASH, 0.8)
p.seg(Pp, B, TEXT, THIN, DASH, 0.8)
p.seg(P, Pp, PRACTICE, 1.6, "6 4")
p.right_angle(M, P, obl(0, 1.6, A60), 10)
p.angle((0, 0), 0, A60, 0.2, THEORY, 1.4)
p.angle((0, 0), A60, 2 * A60, 0.3, PRACTICE, 1.4)
p.dot((0, 0), TEXT)
p.dot(P, THEORY, 4.6)
p.dot(Pp, PRACTICE, 4.6)
p.hollow_dot(S, TEXT, 4.6)
p.dot(B, TEXT, 3.4)
p.label(1.8, 0, "X", ("e", "se"), gap=8, size=AXIS)
p.label(*obl(0, 1.6, A60), "Y", ("ne", "e"), gap=8, size=AXIS)
p.label(0, 0, "O", ("se", "s"), gap=8)
p.label(*P, "P(1, 0)", ("s", "se"))
p.label(*Pp, "P'(−1, 1)", ("nw", "n", "w"))
p.label(*S, "S(−1, 0)", ("s", "sw"))
p.label(*B, "B(0, 1)", ("e", "se", "ne"))
p.along((0, 0), S, "1", 1, size=NOTE)
p.along(S, Pp, "1", 1, size=NOTE)
p.along((0, 0), Pp, "1", -1, t=0.62, size=NOTE)
p.angle_label((0, 0), 0, A60, 0.2, "π/3", "out", NOTE, THEORY, fs=(0, -0.15, 0.15, -0.3))
p.angle_label((0, 0), A60, 2 * A60, 0.3, "π/3", "out", NOTE, PRACTICE, fs=(0, -0.15, 0.15, -0.3))
p.at(-1.05, -0.47, "(−1, 0) simetrik nokta değildir", NOTE, REMARK)
f.out("y-eksenine-gore-simetri",
      "<em>α</em> = <em>π</em>/3 olan eğik sistemde <em>Y</em>-eksenine göre yansıma. <em>P</em>(1, 0)'ın "
      "simetriği <em>P</em>'(−1, 1)'dir; <em>OSP</em>' eşkenar üçgendir ve <em>OSP</em>'<em>B</em> bir paralelkenardır.",
      aria="Reflection of P(1,0) in the oblique Y-axis gives P'(-1,1); S(-1,0) is not the mirror image")


# ============================================================ karenin-dorduncu-kosesi
A45 = D(45)
f, p = equal_fig((-1.8, 1.8), (-0.35, 1.5), 150, (60, 50, 70, 60))
p.seg((-1.8, 0), (0, 0), TEXT, 1.0, None, 0.45)
p.arrow((0, 0), (1.8, 0), TEXT, 1.3, 8.5, opacity=0.7)
p.arrow((0, 0), obl(0, 2, A45), TEXT, 1.3, 8.5, opacity=0.7)
O, A, B, C, S = (0, 0), (1, 0), (1, 1), (0, 1), (-1, 0)
p.poly([O, A, B, C], THEORY, 0.10)
for a, b in ((O, A), (A, B), (B, C), (C, O)):
    p.seg(a, b, THEORY, 2.4)
p.seg(C, S, PRACTICE, 1.5, DASH)
p.right_angle(O, A, C, 11)
p.right_angle(A, O, B, 11)
p.angle(O, 0, A45, 0.36, TEXT, 1.3)
p.angle(S, 0, A45, 0.3, PRACTICE, 1.4)
for q in (O, A, B, C):
    p.dot(q, THEORY, 4.4)
p.dot(S, PRACTICE, 4.4)
p.label(1.8, 0, "X", ("e", "se"), gap=8, size=AXIS)
p.label(*obl(0, 2, A45), "Y", ("ne", "e"), gap=8, size=AXIS)
p.label(*O, "(0, 0)", ("s",), gap=9)
p.label(*A, "(1, 0)", ("s",), gap=9)
p.label(*S, "(−1, 0)", ("s",), gap=9)
p.label(*B, "(0, √2)", ("e", "se", "ne"))
p.label(*C, "(−1, √2)", ("nw", "w", "n"))
p.angle_label(O, 0, A45, 0.36, "π/4", "out", NOTE, fs=(0, -0.15, 0.15))
p.angle_label(S, 0, A45, 0.3, "π/4", "out", NOTE, PRACTICE, fs=(0, -0.15, -0.3))
f.out("karenin-dorduncu-kosesi",
      "<em>α</em> = <em>π</em>/4 olan eğik sistemde kenarı 1 olan kare. Köşelerin yanındaki sayılar paralel "
      "koordinatlardır; <em>C</em>'den <em>Y</em>-eksenine çizilen paralel <em>X</em>-eksenini (−1, 0)'da keser.",
      aria="Unit square in an oblique system with axis angle pi/4; fourth vertex has parallel coordinates (-1, sqrt 2)")


# ============================================================ kutupsal-koordinatlar
f, p = equal_fig((-0.5, 5.6), (-0.45, 3.2), 90, (50, 45, 60, 45))
P = pol(3, D(70))
p.polar_axis(5)
p.seg((0, 0), P, THEORY, 2.2)
p.angle((0, 0), 0, D(70), 0.7, PRACTICE, 1.6, head=True)
origin(p)
p.dot(P, PRACTICE, 4.6)
p.label(*P, "P(r, θ)", ("ne", "e", "n"))
p.along((0, 0), P, "r", 1, size=NAME)
p.angle_label((0, 0), 0, D(70), 0.7, "θ", "in", NAME, PRACTICE, fs=(0, -0.1, 0.1))
f.out("kutupsal-koordinatlar",
      "Kutupsal koordinatlar: <em>r</em> = |<em>OP</em>| kutuptan uzaklık, <em>θ</em> de kutupsal eksenden "
      "<em>OP</em>'ye saat yönünün tersine ölçülen açıdır.",
      aria="Polar coordinates: pole O, polar axis OX, point P at distance r and angle theta")


# ============================================================ kutupsal-noktalar
f, p = equal_fig((-5.4, 6.2), (-5.35, 5.5), 48, (70, 45, 50, 40))
grid = []
for r in range(1, 6):
    p.ring((0, 0), r, TEXT, 0.8, None, 0.16, weight=0.15)
for k in range(12):
    if k == 0:
        continue
    p.seg((0, 0), pol(5, k * PI / 6), TEXT, 0.8, None, 0.16, weight=0.15)
p.polar_axis(5.6)
pts = [((4, 0), TEXT), ((3, PI / 3), BASE), ((5, PI / 2), PRACTICE), ((4, 2 * PI / 3), THEORY),
       ((2, 4 * PI / 3), REMARK)]
for (r, a), col in pts[1:]:
    p.seg((0, 0), pol(r, a), col, 1.7)
p.angle((0, 0), 0, PI / 3, 0.5, BASE, 1.6)
p.angle((0, 0), 0, PI / 2, 0.7, PRACTICE, 1.6)
p.right_angle((0, 0), (1, 0), (0, 1), 10, PRACTICE)
p.angle((0, 0), 0, 2 * PI / 3, 0.9, THEORY, 1.6)
p.angle((0, 0), 0, 4 * PI / 3, 1.1, REMARK, 1.6, head=True)
p.dot((0, 0), TEXT)
dots = [((4, 0), TEXT), ((3, PI / 3), BASE), ((5, PI / 2), PRACTICE), ((2, 2 * PI / 3), THEORY),
        ((4, 2 * PI / 3), THEORY), ((2, 4 * PI / 3), REMARK)]
for (r, a), col in dots:
    p.dot(pol(r, a), col, 4.8)
p.label(0, 0, "O", ("sw", "s", "w"), gap=9)
p.label(4, 0, "(4, 0)", ("s", "se", "sw"), halo=True)
p.frac_label(*pol(3, PI / 3), "(3, ", "π", "3", ")", ("e", "ne", "se"))
p.frac_label(*pol(5, PI / 2), "(5, ", "π", "2", ")", ("n", "ne", "nw"))
p.frac_label(*pol(2, 2 * PI / 3), "(2, ", "2π", "3", ")", ("w", "nw", "sw"))
p.frac_label(*pol(4, 2 * PI / 3), "(4, ", "2π", "3", ")", ("w", "nw", "sw"))
p.frac_label(*pol(2, 4 * PI / 3), "(2, ", "4π", "3", ")", ("w", "sw", "nw"))
f.out("kutupsal-noktalar",
      "Altı noktanın kutupsal düzlemdeki yeri. Soluk çemberler <em>r</em> = 1, …, 5; soluk ışınlar her "
      "<em>π</em>/6'da bir. <em>O</em>'daki renkli yaylar her noktanın kutupsal açısını gösterir.",
      aria="Polar grid with six plotted points (4,0), (3,pi/3), (5,pi/2), (2,2pi/3), (4,2pi/3), (2,4pi/3)")


# ============================================================ dik-kutupsal-gecis
f, p = equal_fig((-1.0, 4.6), (-1.0, 3.0), 100, (50, 50, 60, 45))
P = (3, 2)
p.cart_axes((-1, 4.5), (-1, 3.0))
th = math.atan2(2, 3)
U = pol(1, th)
p.line(arc_pts((0, 0), 1, 0, PI / 2), TEXT, 1.2, "3 4", 0.55, weight=0.6)
p.seg((0, 0), P, THEORY, 2.2)
p.seg(P, (3, 0), TEXT, THIN, DASH, 0.75)
p.right_angle((3, 0), (0, 0), P, 11)
p.angle((0, 0), 0, th, 0.6, PRACTICE, 1.6)
origin(p, ("sw", "s", "w"))
p.dot(P, PRACTICE, 4.6)
p.hollow_dot(U, THEORY, 4.2)
p.label(*P, "P(x, y) = P(r, θ)", ("ne", "n", "e"))
p.along((0, 0), (3, 0), "x = r cos θ", -1, gap=18, size=NOTE)
p.along((3, 0), P, "y = r sin θ", -1, size=NOTE)
p.along((0, 0), P, "r = √(x² + y²)", 1, t=0.68, gap=8, size=NOTE, color=THEORY)
p.label(*U, "U(cos θ, sin θ)", (("c", p.X(0.02) + 60, p.Y(1.28)), "nw", "n"), size=NOTE, leader=True)
p.angle_label((0, 0), 0, th, 0.6, "θ", "out", NAME, PRACTICE, fs=(0, 0.12, -0.12, 0.3))
f.out("dik-kutupsal-gecis",
      "Dik ve kutupsal koordinatlar: <em>OHP</em> dik üçgeninden <em>x</em> = <em>r</em> cos <em>θ</em>, "
      "<em>y</em> = <em>r</em> sin <em>θ</em>. Birim çember üzerindeki <em>U</em> noktası (cos <em>θ</em>, "
      "sin <em>θ</em>)'dır.",
      aria="Right triangle O H P with legs r cos theta and r sin theta; point U on the unit circle")


# ============================================================ dikten-kutupsala
f, p = equal_fig((-3.0, 3.1), (-1.0, 3.0), 90, (55, 50, 60, 45))
P = (-2, 2)
p.cart_axes((-3, 3), (-1, 3))
p.seg((0, 0), P, THEORY, 2.2)
p.seg(P, (-2, 0), TEXT, THIN, DASH, 0.75)
p.seg(P, (0, 2), TEXT, THIN, DASH, 0.75)
p.angle((0, 0), 0, D(135), 0.6, PRACTICE, 1.6, head=True)
p.angle((0, 0), D(135), PI, 0.4, BASE, 1.5)
origin(p, ("se", "s", "sw"))
p.dot(P, PRACTICE, 4.6)
p.dot((-2, 0), TEXT, 3.2)
p.dot((0, 2), TEXT, 3.2)
p.label(*P, "(−2, 2)", ("nw", "w", "n"))
p.label(-2, 0, "−2", ("s", "sw"), size=NOTE)
p.label(0, 2, "2", ("e", "ne"), size=NOTE)
p.along((0, 0), P, "r = 2√2", -1, gap=7, size=NOTE, color=THEORY)
p.angle_label((0, 0), 0, D(135), 0.6, "θ = 3π/4", "out", NOTE, PRACTICE, fs=(-0.1, -0.2, 0, -0.3))
p.angle_label((0, 0), D(135), PI, 0.4, "π/4", "out", NOTE, BASE, fs=(0, 0.2, -0.2))
f.out("dikten-kutupsala",
      "(−2, 2) noktası ikinci bölgededir: <em>r</em> = 2√2 ve <em>θ</em> = 3<em>π</em>/4. "
      "<em>OP</em> negatif <em>X</em> yönüyle <em>π</em>/4 açı yapar.",
      aria="Point (-2, 2) in the second quadrant with r = 2 sqrt 2 and theta = 3 pi / 4")


# ============================================================ dogrunun-kutupsal-denklemi
R3 = math.sqrt(3)
f, p = equal_fig((-2.6, 3.6), (-2.6, 4.6), 80, (180, 45, 60, 45))
p.cart_axes((-2.5, 2.5), (-2.5, 4.5))
x0 = max(-2.5, (-2.5 - 2) / R3)
p.seg((x0, R3 * x0 + 2), (1.4, R3 * 1.4 + 2), THEORY, 2.4)
p.seg((-1.4, -1.4 * R3), (2.5, 2.5 * R3), PRACTICE, 2.4)
p.angle((0, 0), 0, PI / 3, 0.5, PRACTICE, 1.4)
p.dot((0, 2), THEORY, 4.4)
p.dot((0, 0), PRACTICE, 4.4)
p.label(0, 2, "(0, 2)", ("w", "nw", "sw"), size=NOTE)
p.label(0, 0, "(0, 0)", ("se", "e", "s"), size=NOTE)
p.at(-1.35, 3.95, "y = √3x + 2", NOTE, THEORY, anchor="middle")
p.at(-1.35, 3.62, "r sin θ − √3 r cos θ = 2", NOTE, THEORY, anchor="middle")
p.label(2.5, 2.5 * R3, "y = √3x", ("e",), gap=10, size=NOTE, color=PRACTICE)
p.label(2.5, 2.5 * R3 - 0.34, "θ = π/3", ("e",), gap=10, size=NOTE, color=PRACTICE)
p.label(-1.4, -1.4 * R3, "θ = 4π/3", ("w", "sw", "nw"), size=NOTE, color=PRACTICE)
p.angle_label((0, 0), 0, PI / 3, 0.5, "π/3", "out", NOTE, PRACTICE, fs=(0, -0.15, 0.15))
f.out("dogrunun-kutupsal-denklemi",
      "Paralel iki doğru: <em>y</em> = √3<em>x</em> + 2 kutuptan geçmez, kutupsal denklemi "
      "<em>r</em> sin <em>θ</em> − √3 <em>r</em> cos <em>θ</em> = 2'dir. Kutuptan geçen <em>y</em> = √3<em>x</em> "
      "doğrusu ise <em>θ</em> = <em>π</em>/3 ve <em>θ</em> = 4<em>π</em>/3 yarı doğrularının birleşimidir.",
      aria="Parallel lines y = sqrt3 x + 2 and y = sqrt3 x with their polar equations")


# ============================================================ kutupsal-uzaklik
f, p = equal_fig((-0.4, 5.6), (-0.4, 3.6), 92, (50, 45, 70, 45))
P1, P2 = pol(4, D(20)), pol(3.5, D(60))
p.polar_axis(5)
p.seg((0, 0), P1, THEORY, 2.0)
p.seg((0, 0), P2, THEORY, 2.0)
p.seg(P1, P2, PRACTICE, 2.8)
p.angle((0, 0), 0, D(20), 0.6, TEXT, 1.4)
p.angle((0, 0), 0, D(60), 1.0, TEXT, 1.4)
p.angle((0, 0), D(20), D(60), 1.5, PRACTICE, 1.7)
origin(p)
p.dot(P1, THEORY, 4.6)
p.dot(P2, THEORY, 4.6)
p.label(*P1, "P_1(r_1, θ_1)", ("e", "se", "ne"))
p.label(*P2, "P_2(r_2, θ_2)", ("n", "ne", "nw"))
p.along((0, 0), P1, "r_1", -1, t=0.72, size=NAME)
p.along((0, 0), P2, "r_2", 1, t=0.75, size=NAME)
p.along(P1, P2, "|P_1P_2|", -1, size=NAME, color=PRACTICE)
p.angle_label((0, 0), 0, D(20), 0.6, "θ_1", "out", NOTE, fs=(0.1, 0, 0.25))
p.angle_label((0, 0), 0, D(60), 1.0, "θ_2", "out", NOTE, fs=(0.3, 0.38, 0.2, 0.45))
p.angle_label((0, 0), D(20), D(60), 1.5, "θ_2 − θ_1", "out", NOTE, PRACTICE)
f.out("kutupsal-uzaklik",
      "Kutupsal koordinatlarda uzaklık: <em>P</em><sub>1</sub><em>OP</em><sub>2</sub> üçgeninde kenarlar "
      "<em>r</em><sub>1</sub>, <em>r</em><sub>2</sub> ve aradaki açının kosinüsü cos(<em>θ</em><sub>2</sub> − "
      "<em>θ</em><sub>1</sub>)'dir; |<em>P</em><sub>1</sub><em>P</em><sub>2</sub>| kosinüs teoremiyle bulunur.",
      aria="Triangle P1 O P2 with sides r1, r2 and angle theta2 minus theta1 at the pole")


# ============================================================ kutupsal-uzaklik-ornek
f, p = equal_fig((-0.8, 3.4), (-0.4, 4.35), 118, (60, 45, 110, 40))
P1, P2 = pol(2, PI / 6), (0, 4)
p.polar_axis(3)
p.seg((0, 0), P1, THEORY, 2.0)
p.seg((0, 0), P2, THEORY, 2.0)
p.seg(P1, P2, PRACTICE, 2.8)
p.right_angle(P1, (0, 0), P2, 11)
p.angle((0, 0), PI / 6, PI / 2, 0.7, PRACTICE, 1.5)
p.angle((0, 0), 0, PI / 6, 0.45, TEXT, 1.4)
origin(p)
p.dot(P1, THEORY, 4.6)
p.dot(P2, THEORY, 4.6)
p.label(*P1, "P_1(2, π/6)", ("e", "se", "ne"))
p.label(*P2, "P_2(4, π/2)", ("e", "ne", "se"))
p.along((0, 0), P1, "2", -1, size=NOTE)
p.along((0, 0), P2, "4", 1, size=NOTE)
p.along(P1, P2, "2√3", -1, size=NOTE, color=PRACTICE)
p.angle_label((0, 0), PI / 6, PI / 2, 0.7, "π/3", "out", NOTE, PRACTICE)
p.angle_label((0, 0), 0, PI / 6, 0.45, "π/6", "out", NOTE, fs=(0, -0.2, -0.35))
f.out("kutupsal-uzaklik-ornek",
      "<em>P</em><sub>1</sub>(2, <em>π</em>/6) ile <em>P</em><sub>2</sub>(4, <em>π</em>/2) arasındaki açı "
      "<em>π</em>/3'tür ve uzaklık 2√3 çıkar; üçgen <em>P</em><sub>1</sub>'de dik açılıdır.",
      aria="Triangle with sides 2 and 4 from the pole at angle pi/3; distance 2 sqrt 3, right angle at P1")


# ============================================================ kutupsal-ucgen-alani
f, p = equal_fig((-0.4, 6.0), (-0.4, 3.95), 90, (50, 45, 60, 45))
P1, P2 = pol(4, D(25)), pol(4.2, D(55))
u1 = pol(1, D(25))
t = P2[0] * u1[0] + P2[1] * u1[1]
H = (t * u1[0], t * u1[1])
p.polar_axis(5.5)
p.poly([(0, 0), P1, P2], THEORY, 0.12)
p.seg((0, 0), P1, THEORY, 2.0)
p.seg((0, 0), P2, THEORY, 2.0)
p.seg(P1, P2, THEORY, 2.0)
p.seg(P2, H, PRACTICE, 1.8, DASH)
p.right_angle(H, (0, 0), P2, 10)
p.angle((0, 0), 0, D(25), 0.6, TEXT, 1.4)
p.angle((0, 0), 0, D(55), 1.0, TEXT, 1.4)
origin(p)
p.dot(P1, THEORY, 4.6)
p.dot(P2, THEORY, 4.6)
p.dot(H, PRACTICE, 3.4)
p.label(*P1, "P_1(r_1, θ_1)", ("e", "se", "ne"))
p.label(*P2, "P_2(r_2, θ_2)", ("n", "ne", "nw"))
p.along((0, 0), P1, "r_1", -1, t=0.45, size=NAME)
p.along((0, 0), P2, "r_2", 1, t=0.6, size=NAME)
p.along(P2, H, "h", -1, size=NAME, color=PRACTICE)
p.label(*H, "H", ("s", "se", "sw"), size=NOTE)
p.angle_label((0, 0), 0, D(25), 0.6, "θ_1", "out", NOTE, fs=(0, 0.2, -0.2))
p.angle_label((0, 0), 0, D(55), 1.0, "θ_2", "out", NOTE, fs=(0.3, 0.38, 0.2, 0.45))
f.out("kutupsal-ucgen-alani",
      "Kutupsal koordinatlarda üçgenin alanı: taban |<em>OP</em><sub>1</sub>| = <em>r</em><sub>1</sub>, "
      "yükseklik <em>h</em> = <em>r</em><sub>2</sub> sin(<em>θ</em><sub>2</sub> − <em>θ</em><sub>1</sub>).",
      aria="Triangle O P1 P2 with the altitude h from P2 to O P1, foot H")


# ============================================================ kutupsal-alan-ornek
f, p = equal_fig((-4.0, 4.6), (-0.5, 6.0), 60, (110, 45, 110, 45))
P1, P2 = pol(4, PI / 6), pol(6, 2 * PI / 3)
p.arrow((-4.0, 0), (4.6, 0), TEXT, 1.2, 8, opacity=0.4)
p.arrow((0, -0.5), (0, 6.0), TEXT, 1.2, 8, opacity=0.4)
p.label(4.6, 0, "X", ("e", "se"), gap=8, size=AXIS)
p.poly([(0, 0), P1, P2], THEORY, 0.12)
p.seg((0, 0), P1, THEORY, 2.0)
p.seg((0, 0), P2, THEORY, 2.0)
p.seg(P1, P2, THEORY, 2.0)
p.right_angle((0, 0), P1, P2, 12)
p.angle((0, 0), 0, PI / 6, 0.6, PRACTICE, 1.5)
p.dot((0, 0), TEXT)
p.label(0, 0, "O", ("s", "sw", "se"), gap=9)
p.dot(P1, THEORY, 4.6)
p.dot(P2, THEORY, 4.6)
p.label(*P1, "P_1(4, π/6)", ("e", "se", "ne"))
p.label(*P2, "P_2(6, 2π/3)", ("w", "nw", "sw"))
p.along((0, 0), P1, "4", -1, size=NOTE)
p.along((0, 0), P2, "6", 1, t=0.55, size=NOTE)
p.angle_label((0, 0), 0, PI / 6, 0.6, "π/6", "out", NOTE, PRACTICE, fs=(0, -0.2, 0.2))
p.at(1.2, 2.2, "Alan = 12", NOTE + 0.5, THEORY, bold=True)
f.out("kutupsal-alan-ornek",
      "<em>O</em>, <em>P</em><sub>1</sub>(4, <em>π</em>/6), <em>P</em><sub>2</sub>(6, 2<em>π</em>/3) üçgeni: "
      "açılar farkı <em>π</em>/2 olduğundan üçgen <em>O</em>'da dik açılıdır ve alanı 12'dir.",
      aria="Right triangle O P1 P2 with legs 4 and 6 and area 12")


# ============================================================ kutupsal-dogru-denklemi
f, p = equal_fig((-0.6, 4.9), (-0.6, 4.1), 100, (50, 45, 60, 45))
Q = pol(2.5, PI / 4)
u = (-math.sqrt(0.5), math.sqrt(0.5))
d0, d1 = (Q[0] + u[0] * (-3.15), Q[1] + u[1] * (-3.15)), (Q[0] + u[0] * 3.07, Q[1] + u[1] * 3.07)
P = (Q[0] + 2 * u[0], Q[1] + 2 * u[1])
p.polar_axis(4.5)
p.seg(d0, d1, THEORY, 2.4)
p.seg((0, 0), Q, TEXT, 1.6, DASH, 0.85)
p.seg((0, 0), P, THEORY, 1.9)
p.seg(Q, P, PRACTICE, 2.8)
p.right_angle(Q, (0, 0), d0, 11)
thP = math.atan2(P[1], P[0])
p.angle((0, 0), 0, PI / 4, 0.6, TEXT, 1.4)
p.angle((0, 0), 0, thP, 1.0, TEXT, 1.4)
p.angle((0, 0), PI / 4, thP, 1.4, PRACTICE, 1.3)
origin(p)
p.dot(Q, TEXT, 4.6)
p.dot(P, THEORY, 4.6)
p.label(*Q, "Q(q, ω)", ("ne", "e", "se"))
p.label(*P, "P(r, θ)", ("ne", "e", "n"))
p.label(*d0, "d", ("e", "se", "ne"), size=NAME, color=THEORY)
p.along((0, 0), Q, "q", -1, t=0.55, size=NAME)
p.along((0, 0), P, "r", 1, t=0.6, size=NAME)
p.along(Q, P, "|QP|", 1, size=NOTE, color=PRACTICE)
p.angle_label((0, 0), 0, PI / 4, 0.6, "ω", "out", NAME, fs=(0, 0.1, -0.1, 0.2))
p.angle_label((0, 0), 0, thP, 1.0, "θ", "out", NAME, fs=(0.33, 0.25, 0.4, 0.15))
p.angle_label((0, 0), PI / 4, thP, 1.4, "θ − ω", "out", NOTE, PRACTICE)
f.out("kutupsal-dogru-denklemi",
      "Kutupsal doğru denklemi: <em>Q</em>(<em>q</em>, <em>ω</em>) kutuptan <em>d</em>'ye inilen dikmenin "
      "ayağıdır. <em>OQP</em> üçgeni <em>Q</em>'da dik açılı olduğundan <em>r</em> cos(<em>θ</em> − <em>ω</em>) "
      "= <em>q</em> olur.",
      aria="Line d with foot of perpendicular Q(q, omega) from the pole and a point P(r, theta) on d")


# ============================================================ ozel-durumlar
PPU4 = 46
f = Fig(726, 720)
cases = [
    ("A = 0, B > 0", (0, 2), "Q(1/B, π/2)", PI / 2, ((-3, 2), (3, 2))),
    ("A = 0, B < 0", (0, -2), "Q(−1/B, 3π/2)", 3 * PI / 2, ((-3, -2), (3, -2))),
    ("A > 0, B = 0", (2, 0), "Q(1/A, 0)", 0.0, ((2, -3), (2, 3))),
    ("A < 0, B = 0", (-2, 0), "Q(−1/A, π)", PI, ((-2, -3), (-2, 3))),
]
for i, (title, Q, qlab, om, (d0, d1)) in enumerate(cases):
    col, row = i % 2, i // 2
    p = f.panel(45 + col * 370, 52 + row * 360, (-3, 3), (-3, 3), PPU4)
    p.seg((-3, 0), (3, 0), TEXT, 1.2, None, 0.35, weight=0.6)
    p.arrow((0, -3), (0, 3), TEXT, 1.2, 8, opacity=0.35, weight=0.6)
    p.arrow((0, 0), (2.7, 0), TEXT, 1.5, 8.5, opacity=0.8)
    p.seg(d0, d1, THEORY, 2.5)
    if om == 0.0:
        p.seg((0, 0), Q, PRACTICE, 2.2, DASH)
    else:
        p.seg((0, 0), Q, PRACTICE, 1.8, DASH)
    p.right_angle(Q, (0, 0), d1 if i < 2 else d1, 10)
    if om > 0:
        p.angle((0, 0), 0, om, 0.55 if om < PI else 0.5, TEXT, 1.4, head=True)
    p.dot((0, 0), TEXT)
    p.dot(Q, PRACTICE, 4.6)
    p.at(0, 3.55, title, NOTE + 0.5, TEXT, bold=True)
    p.label(3, 0, "X", ("e", "se", "ne"), gap=8, size=AXIS)
    qp = {0: ("ne", "nw", "n"), 1: ("se", "sw", "s"), 2: ("se", "ne", "e"), 3: ("sw", "nw", "w")}[i]
    p.label(*Q, qlab, qp, gap=8, size=NOTE)
    op = {0: ("sw", "se"), 1: ("se", "e"), 2: ("nw", "sw", "ne"), 3: ("se", "ne", "sw")}[i]
    p.label(0, 0, "O", op, gap=8)
    p.label(*d1, "d", ("e", "ne", "n", "nw") if i < 2 else ("e", "ne", "nw"), gap=8, size=NAME, color=THEORY)
    alab = {0: "π/2", 1: "3π/2", 3: "π"}.get(i)
    if alab:
        fs = {0: (0.1, -0.1, 0.25), 1: (0, 0.06, -0.06), 3: (0, 0.1, -0.1)}[i]
        p.angle_label((0, 0), 0, om, 0.55 if om < PI else 0.5, alab, "out", NOTE, fs=fs)
f.out("ozel-durumlar",
      "<em>A</em> cos <em>θ</em> + <em>B</em> sin <em>θ</em> = 1/<em>r</em> doğrusunun dört özel durumu "
      "(örneklerde |<em>A</em>| ya da |<em>B</em>| = 1/2). Üst sıradaki (<em>A</em> = 0) doğrular kutupsal eksene "
      "paralel, alt sıradaki (<em>B</em> = 0) doğrular kutupsal eksene diktir.",
      aria="Four panels: horizontal lines y = 2 and y = -2, vertical lines x = 2 and x = -2 with feet Q",
      css=WIDE)


# ============================================================ r-sin-eksi-iki
f, p = equal_fig((-3.7, 4.6), (-2.7, 0.9), 64, (50, 45, 60, 50))
Q = (0, -2)
p.polar_axis(4)
p.seg((-3.5, -2), (4, -2), THEORY, 2.5)
p.seg((0, 0), Q, PRACTICE, 1.7, DASH)
p.right_angle(Q, (0, 0), (4, -2), 10)
p.angle((0, 0), 0, 3 * PI / 2, 0.4, TEXT, 1.4, head=True)
origin(p, ("se", "s"))
p.dot(Q, PRACTICE, 4.6)
p.label(*Q, "Q(2, 3π/2)", ("s", "sw", "se"), gap=8)
p.label(4, -2, "d", ("e", "ne"), gap=8, size=NAME, color=THEORY)
p.along((0, 0), Q, "2", 1, t=0.6, size=NOTE, color=PRACTICE)
p.angle_label((0, 0), 0, 3 * PI / 2, 0.4, "3π/2", "out", NOTE, fs=(0, 0.06, -0.06, 0.12))
f.out("r-sin-eksi-iki",
      "<em>r</em> sin <em>θ</em> = −2 doğrusu: kutuptan inilen dikmenin ayağı <em>Q</em>(2, 3<em>π</em>/2)'dir "
      "ve doğru kutupsal eksene paraleldir.",
      aria="Horizontal line y = -2 with foot Q(2, 3pi/2) of the perpendicular from the pole")


# ============================================================ eksene-dik-dogru
f, p = equal_fig((-0.5, 3.4), (-0.9, 3.3), 128, (50, 40, 130, 40))
R3 = math.sqrt(3)
H, K, P = (R3, 0), (R3, 1), (R3, 2.6)
p.polar_axis(3)
p.seg((R3, -0.8), (R3, 3.2), THEORY, 2.5)
p.seg((0, 0), K, TEXT, 1.7)
p.seg((0, 0), P, BASE, 1.9)
p.right_angle(H, (0, 0), K, 11)
thP = math.atan2(2.6, R3)
p.angle((0, 0), 0, PI / 6, 0.5, TEXT, 1.4)
p.angle((0, 0), 0, thP, 0.85, BASE, 1.4)
origin(p)
p.dot(H, TEXT, 3.4)
p.dot(K, PRACTICE, 4.6)
p.dot(P, BASE, 4.6)
p.label(*K, "(2, π/6)", ("e", "ne", "se"))
p.label(*P, "P(r, θ)", ("e", "ne", "se"))
p.label(R3, -0.8, "d", ("s", "se", "e"), gap=7, size=NAME, color=THEORY)
p.along((0, 0), K, "2", 1, t=0.6, size=NOTE)
p.along((0, 0), H, "√3", -1, t=0.35, size=NOTE)
p.along(H, K, "1", -1, size=NOTE)
p.along((0, 0), P, "r", 1, t=0.62, size=NAME, color=BASE)
p.angle_label((0, 0), 0, PI / 6, 0.5, "π/6", "out", NOTE, fs=(0, -0.15, 0.15))
p.angle_label((0, 0), 0, thP, 0.85, "θ", "out", NAME, BASE, fs=(0.3, 0.38, 0.2))
f.out("eksene-dik-dogru",
      "(2, <em>π</em>/6) noktasından geçen ve <em>OX</em>'e dik <em>d</em> doğrusu: <em>OHK</em> dik üçgeninden "
      "|<em>OH</em>| = √3, <em>OHP</em> dik üçgeninden <em>r</em> cos <em>θ</em> = √3.",
      aria="Vertical line x = sqrt 3 through (2, pi/6); foot H on the polar axis and a point P(r, theta)")


# ============================================================ dikme-ayagi
f, p = equal_fig((-3.0, 2.1), (-1.5, 4.0), 98, (60, 45, 150, 40))
Q = pol(1, 5 * PI / 6)
p.cart_axes((-3, 2), (-1.5, 4))
xa = (-1.5 - 2) / R3
p.seg((xa, -1.5), (1.1, R3 * 1.1 + 2), THEORY, 2.4)
p.seg((0, 0), Q, PRACTICE, 2.0, DASH)
p.right_angle(Q, (0, 0), (1.1, R3 * 1.1 + 2), 10)
p.angle((0, 0), 0, 5 * PI / 6, 0.35, PRACTICE, 1.4, head=True)
p.dot((0, 0), TEXT)
p.label(0, 0, "O", ("se", "s", "e"), gap=8)
p.dot(Q, PRACTICE, 4.6)
p.dot((0, 2), THEORY, 3.6)
p.label(*Q, "Q(1, 5π/6)", ("sw", "w", "s", "nw"))
p.label(0, 2, "(0, 2)", ("e", "se"), size=NOTE)
p.label(1.1, R3 * 1.1 + 2, "y = √3x + 2", ("e", "se"), gap=9, size=NOTE, color=THEORY)
p.along((0, 0), Q, "q = 1", 1, size=NOTE, color=PRACTICE)
p.angle_label((0, 0), 0, 5 * PI / 6, 0.35, "5π/6", "out", NOTE, PRACTICE, fs=(-0.3, -0.38, -0.2, -0.1))
f.out("dikme-ayagi",
      "<em>y</em> = √3<em>x</em> + 2 doğrusu için kutuptan inilen dikmenin ayağı <em>Q</em>(1, 5<em>π</em>/6); "
      "normal denklem <em>r</em> cos(<em>θ</em> − 5<em>π</em>/6) = 1.",
      aria="Line y = sqrt3 x + 2 with the foot Q(1, 5pi/6) of the perpendicular from the pole")


# ============================================================ orijinden-gecen-dogru
f, p = equal_fig((-1.0, 6.3), (-1.05, 2.9), 76, (50, 45, 60, 60))
p.oblique_axes(A60, (-1, 6), (-0.8, 3), grid=((-1.0, 6.0), (-0.72, 2.85)))
P, R = obl(2, 1, A60), obl(4, 2, A60)
Pp, Rp = (2, 0), (4, 0)
p.poly([(0, 0), Rp, R], BASE, 0.10)
p.poly([(0, 0), Pp, P], PRACTICE, 0.16)
p.seg((-0.6, -0.6 * P[1] / P[0]), (6, 6 * P[1] / P[0]), THEORY, 2.4)
p.seg(Pp, P, TEXT, THIN, DASH, 0.8)
p.seg(Rp, R, TEXT, THIN, DASH, 0.8)
p.seg(P, obl(0, 1, A60), TEXT, THIN, DASH, 0.6)
p.seg(R, obl(0, 2, A60), TEXT, THIN, DASH, 0.6)
p.dot((0, 0), TEXT)
p.dot(P, PRACTICE, 4.6)
p.dot(R, BASE, 4.6)
p.dot(Pp, TEXT, 3.4)
p.dot(Rp, TEXT, 3.4)
# dimension lines for x1 = OP' and x = OR' below the axis
for x_end, yy, s in ((2, -0.5, "x_1"), (4, -0.82, "x")):
    Y = p.Y(0) + (p.Y(yy) - p.Y(0))
    mid = x_end / 2
    w = len(s.replace("_", "")) * CW * NOTE + 10
    for xa_, xb_ in ((0, mid - w / 2 / p.ppu()), (mid + w / 2 / p.ppu(), x_end)):
        p.seg((xa_, yy), (xb_, yy), TEXT, 1.0, None, 0.55)
    for xe in (0, x_end):
        p.seg((xe, yy - 0.07), (xe, yy + 0.07), TEXT, 1.0, None, 0.55)
    p.at(mid, yy, s, NOTE)
p.label(6.0, 0, "X", ("e", "se"), gap=8, size=AXIS)
p.label(*obl(0, 3, A60), "Y", ("ne", "e", "nw"), gap=8, size=AXIS)
p.label(0, 0, "O", (("c", p.X(0) - 20, p.Y(0) + 13), "nw"), gap=8)
p.label(6, 6 * P[1] / P[0], "d", ("e", "se", "ne"), gap=8, size=NAME, color=THEORY)
p.label(*P, "P(x_1, y_1)", ("nw", "n", "ne"))
p.label(*R, "R(x, y)", ("ne", "e", "n"))
p.label(*Pp, "P'", ("se", "s"), size=NOTE)
p.label(*Rp, "R'", ("se", "s"), size=NOTE)
p.along(Pp, P, "y_1", -1, size=NOTE)
p.along(Rp, R, "y", -1, size=NOTE)
f.out("orijinden-gecen-dogru",
      "Eğik sistemde başlangıçtan geçen <em>d</em> doğrusu: <em>OP</em>'<em>P</em> ve <em>OR</em>'<em>R</em> "
      "üçgenleri benzer olduğundan <em>x</em>/<em>x</em><sub>1</sub> = <em>y</em>/<em>y</em><sub>1</sub>, "
      "yani <em>y</em> = <em>mx</em>.",
      aria="Oblique system: line d through O and points P, R with similar triangles O P' P and O R' R")


# ============================================================ paralel-uzaklik
f, p = equal_fig((-0.5, 6.6), (-0.6, 3.7), 78, (50, 45, 70, 50))
p.oblique_axes(A60, (-0.5, 6.5), (-0.3, 3.6), grid=((-0.5, 6.5), (-0.28, 3.5)))
P1, P2, R = obl(1, 1, A60), obl(4, 3, A60), obl(4, 1, A60)
p.seg(P1, (1, 0), TEXT, 1.2, DASH, 0.6)
p.seg(R, (4, 0), TEXT, 1.2, DASH, 0.6)
p.seg(P1, R, THEORY, 2.1)
p.seg(R, P2, THEORY, 2.1)
p.seg(P1, P2, PRACTICE, 2.8)
p.angle(R, A60, PI, 0.42, TEXT, 1.4)
p.angle((0, 0), 0, A60, 0.4, TEXT, 1.3)
p.dot((0, 0), TEXT)
p.dot((1, 0), TEXT, 3.2)
p.dot((4, 0), TEXT, 3.2)
for q in (P1, P2, R):
    p.dot(q, PRACTICE if q is not R else THEORY, 4.6)
p.label(6.5, 0, "X", ("e", "se"), gap=8, size=AXIS)
p.label(*obl(0, 3.6, A60), "Y", ("ne", "e", "nw"), gap=8, size=AXIS)
p.label(0, 0, "O", ("sw", "w", "s"), gap=8)
p.label(*P1, "P_1(x_1, y_1)", ("se", "s", "nw"))
p.label(*P2, "P_2(x_2, y_2)", ("ne", "e", "n"))
p.label(*R, "R(x_2, y_1)", ("se", "e", "s"))
p.label(1, 0, "x_1", ("s", "se"), size=NOTE)
p.label(4, 0, "x_2", ("s", "sw"), size=NOTE)
p.along(P1, R, "x_2 − x_1", -1, t=0.42, size=NOTE)
p.along(R, P2, "y_2 − y_1", -1, size=NOTE)
p.along(P1, P2, "|P_1P_2|", 1, t=0.45, size=NOTE, color=PRACTICE)
p.angle_label(R, A60, PI, 0.42, "π − α", "out", NOTE, fs=(0, 0.12, -0.12))
p.angle_label((0, 0), 0, A60, 0.4, "α", "out", NAME, fs=(0, -0.15, 0.15))
f.out("paralel-uzaklik",
      "Eğik sistemde uzaklık: <em>P</em><sub>1</sub><em>RP</em><sub>2</sub> üçgeninin kenarları "
      "|<em>x</em><sub>2</sub> − <em>x</em><sub>1</sub>| ve |<em>y</em><sub>2</sub> − <em>y</em><sub>1</sub>|, "
      "<em>R</em>'deki açı <em>π</em> − <em>α</em>'dır; kosinüs teoremi uzaklığı verir.",
      aria="Oblique system: triangle P1 R P2 with sides x2 - x1 and y2 - y1 and angle pi - alpha at R")


# ============================================================ uzaklik-i
f, p = equal_fig((-1.2, 3.4), (-0.45, 8.1), 64, (330, 40, 110, 40))
P1, P2 = (0, 6), pol(8, 5 * PI / 12)
p.polar_axis(3)
p.seg((0, 0), P1, THEORY, 2.0)
p.seg((0, 0), P2, THEORY, 2.0)
p.seg(P1, P2, PRACTICE, 2.8)
p.angle((0, 0), 5 * PI / 12, PI / 2, 2.5, TEXT, 1.4)
p.angle((0, 0), 0, 5 * PI / 12, 0.6, TEXT, 1.4)
p.dot((0, 0), TEXT)
p.label(0, 0, "O", ("s", "sw", "se"), gap=9)
p.dot(P1, THEORY, 4.6)
p.dot(P2, THEORY, 4.6)
p.label(*P1, "P_1(6, π/2)", ("w", "nw", "sw"))
p.label(*P2, "P_2(8, 5π/12)", ("e", "ne", "se"))
p.along((0, 0), P1, "6", 1, t=0.7, size=NOTE)
p.along((0, 0), P2, "8", -1, t=0.55, size=NOTE)
p.along(P1, P2, "≈ 2,70", 1, size=NOTE, color=PRACTICE)
p.angle_label((0, 0), 5 * PI / 12, PI / 2, 2.5, "π/12", "out", NOTE, fs=(0,))
p.at(-3.75, 3.6, "|P_1P_2| = √(100 − 24√6 − 24√2)", NOTE, PRACTICE, anchor="start")
p.angle_label((0, 0), 0, 5 * PI / 12, 0.6, "5π/12", "out", NOTE, fs=(-0.1, -0.2, 0, -0.3))
f.out("uzaklik-i",
      "(6, <em>π</em>/2) ve (8, 5<em>π</em>/12) noktaları kutuptan <em>π</em>/12 = 15° farklı yönlerde "
      "görünür; aralarındaki uzaklık yaklaşık 2,70'tir.",
      aria="Two points at distances 6 and 8 from the pole, 15 degrees apart, distance about 2.70")


# ============================================================ uzaklik-ii
f, p = equal_fig((-0.8, 5.6), (-0.45, 8.2), 64, (110, 40, 60, 40))
P1, P2 = pol(5, PI / 4), (0, 8)
p.polar_axis(5)
p.seg((0, 0), P1, THEORY, 2.0)
p.seg((0, 0), P2, THEORY, 2.0)
p.seg(P1, P2, PRACTICE, 2.8)
p.angle((0, 0), 0, PI / 4, 0.6, TEXT, 1.4)
p.angle((0, 0), PI / 4, PI / 2, 1.1, BASE, 1.5)
origin(p)
p.dot(P1, THEORY, 4.6)
p.dot(P2, THEORY, 4.6)
p.label(*P1, "P_1(5, π/4)", ("e", "se", "ne"))
p.label(*P2, "P_2(8, π/2)", ("w", "nw", "sw"))
p.along((0, 0), P1, "5", -1, t=0.6, size=NOTE)
p.along((0, 0), P2, "8", 1, t=0.6, size=NOTE)
p.along(P1, P2, "≈ 5,69", -1, size=NOTE, color=PRACTICE)
p.angle_label((0, 0), 0, PI / 4, 0.6, "π/4", "out", NOTE, fs=(0, -0.15, 0.15))
p.angle_label((0, 0), PI / 4, PI / 2, 1.1, "π/4", "out", NOTE, BASE, fs=(0, 0.15, -0.15))
f.out("uzaklik-ii",
      "(5, <em>π</em>/4) ile (8, <em>π</em>/2) arasındaki açı <em>π</em>/4'tür; uzaklık "
      "√(89 − 40√2) ≈ 5,69.",
      aria="Two points at distances 5 and 8 from the pole, 45 degrees apart, distance about 5.69")


# ============================================================ uzaklik-iii
f, p = equal_fig((-4.6, 3.1), (-5.0, 3.0), 66, (130, 45, 60, 40))
P1, P2 = pol(5, -2 * PI / 3), pol(4, 5 * PI / 6)
p.cart_axes((-4.5, 3.0), (-5.0, 3.0), yl="", ticks=False, opacity=0.35)
p.arrow((0, 0), (3.0, 0), TEXT, 1.5, 9, opacity=0.8)
p.seg((0, 0), P1, THEORY, 2.0)
p.seg((0, 0), P2, THEORY, 2.0)
p.seg(P1, P2, PRACTICE, 2.8)
p.right_angle((0, 0), P1, P2, 12)
p.angle((0, 0), 0, -2 * PI / 3, 0.6, BASE, 1.5, head=True, dash="4 3")
p.angle((0, 0), 0, 5 * PI / 6, 0.9, TEXT, 1.4, head=True)
p.dot((0, 0), TEXT)
p.label(0, 0, "O", ("se", "e", "ne"), gap=8)
p.dot(P1, THEORY, 4.6)
p.dot(P2, THEORY, 4.6)
p.label(*P1, "P_1(5, −2π/3)", ("e", "se", "ne"))
p.label(*P2, "P_2(4, 5π/6)", ("w", "nw", "sw"))
p.along((0, 0), P1, "5", 1, t=0.6, size=NOTE)
p.along((0, 0), P2, "4", -1, t=0.6, size=NOTE)
p.along(P1, P2, "√41", 1, size=NOTE, color=PRACTICE)
p.angle_label((0, 0), 0, -2 * PI / 3, 0.6, "−2π/3", "out", NOTE, BASE, fs=(0, 0.1, -0.1, 0.2))
p.angle_label((0, 0), 0, 5 * PI / 6, 0.9, "5π/6", "out", NOTE, fs=(-0.1, -0.2, 0, -0.3))
f.out("uzaklik-iii",
      "(5, −2<em>π</em>/3) saat yönünde ölçülen açıyla bulunur. İki yarıçap arasındaki açı "
      "3<em>π</em>/2 − <em>π</em> = <em>π</em>/2 olduğundan uzaklık √(25 + 16) = √41'dir.",
      aria="Points at distance 5 (angle -2pi/3) and 4 (angle 5pi/6) from the pole, perpendicular radii, distance sqrt 41")


# ============================================================ kutupsal-cember
f, p = equal_fig((-0.45, 6.3), (-0.4, 3.85), 86, (50, 45, 60, 45))
P1 = pol(4, PI / 6)
P = (3.204, 3.477)
p.polar_axis(6)
p.ring(P1, 1.5, THEORY, 2.3)
p.seg((0, 0), P1, TEXT, 1.8)
p.seg((0, 0), P, TEXT, 1.6, DASH, 0.85)
p.seg(P1, P, PRACTICE, 2.2)
thP = math.atan2(P[1], P[0])
p.angle((0, 0), 0, PI / 6, 0.8, TEXT, 1.4)
p.angle((0, 0), PI / 6, thP, 1.6, PRACTICE, 1.4)
origin(p)
p.dot(P1, THEORY, 4.6)
p.dot(P, PRACTICE, 4.6)
p.label(*P1, "P_1(r_1, θ_1)", ("se", "s", "e"), gap=8)
p.label(*P, "P(r, θ)", ("nw", "n", "w"))
p.along(P1, P, "a", -1, size=NAME, color=PRACTICE)
p.along((0, 0), P1, "r_1", -1, t=0.5, size=NAME)
p.along((0, 0), P, "r", 1, t=0.55, size=NAME)
p.angle_label((0, 0), 0, PI / 6, 0.8, "θ_1", "out", NOTE, fs=(0, -0.15, 0.15))
p.angle_label((0, 0), PI / 6, thP, 1.6, "θ − θ_1", "out", NOTE, PRACTICE, fs=(0, -0.3, 0.3))
f.out("kutupsal-cember",
      "<em>P</em><sub>1</sub>(<em>r</em><sub>1</sub>, <em>θ</em><sub>1</sub>) merkezli, <em>a</em> yarıçaplı "
      "çember: <em>POP</em><sub>1</sub> üçgeninde kosinüs teoremi çemberin kutupsal denklemini verir.",
      aria="Circle with centre P1(r1, theta1) and radius a; point P(r, theta) on it and triangle P O P1")


# ============================================================ kutupsaldan-dike-cember
f, p = equal_fig((-3.0, 5.2), (-5.0, 3.0), 58, (50, 45, 200, 40))
M = (1, -1)
p.cart_axes((-3, 5), (-5, 3))
p.ring(M, 3, THEORY, 2.5)
p.seg(M, (4, -1), PRACTICE, 2.0)
p.dot((0, 0), TEXT)
p.dot(M, THEORY, 4.6)
p.label(0, 0, "O", ("nw", "ne", "sw"), gap=8)
p.label(*M, "M(1, −1)", ("sw", "s", "nw"))
p.along(M, (4, -1), "3", 1, t=0.6, size=NOTE, color=PRACTICE)
p.at(7.1, 2.45, "(x − 1)² + (y + 1)² = 9", NOTE, THEORY, anchor="end")
p.at(7.1, 2.05, "r² − 2r(cos θ − sin θ) − 7 = 0", NOTE, THEORY, anchor="end")
f.out("kutupsaldan-dike-cember",
      "<em>r</em>² − 2<em>r</em>(cos <em>θ</em> − sin <em>θ</em>) − 7 = 0 eğrisi, merkezi <em>M</em>(1, −1) "
      "ve yarıçapı 3 olan çemberdir; kutup çemberin içinde kalır.",
      aria="Circle with centre (1,-1) and radius 3 together with its Cartesian and polar equations")


# ============================================================ egik-dogru
f, p = equal_fig((-0.8, 8.4), (-0.55, 4.5), 60, (50, 45, 60, 45))
R3 = math.sqrt(3)
T = (4 * R3, 0)
P0, A = pol(4, PI / 6), pol(2 * R3, PI / 3)
P = (0.346, 3.8)
p.polar_axis(7.8)
p.seg((-0.6, (4 * R3 + 0.6) / R3), (7.6, (4 * R3 - 7.6) / R3), THEORY, 2.5)
p.seg((0, 0), P0, TEXT, 1.8)
p.seg((0, 0), A, PRACTICE, 2.0, DASH)
p.seg((0, 0), P, BASE, 1.8)
p.right_angle(A, (0, 0), P0, 10)
p.angle((0, 0), 0, PI / 6, 0.6, TEXT, 1.4)
p.angle((0, 0), PI / 6, PI / 3, 1.05, PRACTICE, 1.4)
thP = math.atan2(P[1], P[0])
p.angle((0, 0), 0, thP, 1.65, BASE, 1.2)
p.angle(P0, 5 * PI / 6, 7 * PI / 6, 0.55, TEXT, 1.4)
p.angle(T, 0, 5 * PI / 6, 0.45, THEORY, 1.5)
origin(p)
p.dot(T, THEORY, 3.4)
p.dot(P0, TEXT, 4.6)
p.dot(A, PRACTICE, 4.6)
p.dot(P, BASE, 4.6)
p.label(*T, "T", ("s", "se", "sw"), size=NOTE)
p.label(*P0, "P_0(4, π/6)", ("ne", "e", "n"))
p.label(*A, "A", ("ne", "n", "e"))
p.label(*P, "P(r, θ)", ("ne", "sw", "w"))
p.label(7.6, (4 * R3 - 7.6) / R3, "d", ("s", "se", "e"), gap=7, size=NAME, color=THEORY)
p.along((0, 0), P0, "4", -1, t=0.6, size=NOTE)
p.along((0, 0), A, "2√3", 1, t=0.62, size=NOTE, color=PRACTICE)
p.along((0, 0), P, "r", 1, t=0.6, size=NAME, color=BASE)
p.angle_label((0, 0), 0, PI / 6, 0.6, "π/6", "out", NOTE, fs=(0, -0.15, 0.15))
p.angle_label((0, 0), PI / 6, PI / 3, 1.05, "π/6", "out", NOTE, PRACTICE, fs=(0, -0.15, 0.15))
p.angle_label((0, 0), 0, thP, 1.65, "θ", "out", NAME, BASE, fs=(0.4, 0.33, 0.45))
p.angle_label(P0, 5 * PI / 6, 7 * PI / 6, 0.55, "π/3", "out", NOTE, fs=(0, 0.15, -0.15))
p.angle_label(T, 0, 5 * PI / 6, 0.45, "5π/6", "out", NOTE, THEORY, fs=(0.1, 0.2, 0.3, 0))
f.out("egik-dogru",
      "<em>P</em><sub>0</sub>(4, <em>π</em>/6)'dan geçen ve kutupsal eksenle 5<em>π</em>/6 açı yapan "
      "<em>d</em> doğrusu. Kutuptan inilen dikmenin ayağı <em>A</em>(2√3, <em>π</em>/3); denklem "
      "<em>r</em> cos(<em>θ</em> − <em>π</em>/3) = 2√3.",
      aria="Line through P0(4, pi/6) making angle 5pi/6 with the polar axis; foot A of the perpendicular from O")


# ============================================================ yaricapa-dik-dogru
f, p = equal_fig((-5.5, 3.0), (-0.5, 5.1), 64, (50, 45, 60, 45))
P0 = pol(4, 2 * PI / 3)
v = (math.cos(PI / 6), math.sin(PI / 6))
Pl = (P0[0] - 2.5 * v[0], P0[1] - 2.5 * v[1])
l0, l1 = (P0[0] - 3.7 * v[0], P0[1] - 3.7 * v[1]), (P0[0] + 2.95 * v[0], P0[1] + 2.95 * v[1])
p.polar_axis(3)
p.seg((0, 0), pol(4.8, 2 * PI / 3), TEXT, 1.4, None, 0.8)
p.seg(l0, l1, THEORY, 2.5)
p.seg((0, 0), Pl, BASE, 1.8)
p.right_angle(P0, (0, 0), l1, 10)
thP = math.atan2(Pl[1], Pl[0])
p.angle((0, 0), 0, 2 * PI / 3, 0.5, TEXT, 1.4)
p.angle((0, 0), 0, thP, 0.9, BASE, 1.4)
p.dot((0, 0), TEXT)
p.label(0, 0, "O", ("s", "se", "sw"), gap=9)
p.dot(P0, PRACTICE, 4.6)
p.dot(Pl, BASE, 4.6)
p.label(*P0, "P_0(4, 2π/3)", ("e", "ne", "n"))
p.label(*Pl, "P(r, θ)", ("nw", "w", "n"))
p.label(*l1, "ℓ", ("e", "ne", "se"), gap=8, size=NAME + 1, color=THEORY)
p.along((0, 0), P0, "4", -1, t=0.55, size=NOTE)
p.along((0, 0), P0, "d", 1, t=0.4, size=NAME)
p.along((0, 0), Pl, "r", -1, t=0.55, size=NAME, color=BASE)
p.angle_label((0, 0), 0, 2 * PI / 3, 0.5, "2π/3", "out", NOTE, fs=(0.1, 0, 0.2, -0.1))
p.angle_label((0, 0), 0, thP, 0.9, "θ", "out", NAME, BASE, fs=(0.4, 0.3, 0.45, 0.2))
f.out("yaricapa-dik-dogru",
      "<em>OP</em><sub>0</sub>'a <em>P</em><sub>0</sub>'da dik olan ℓ doğrusu. Kutuptan ℓ'ye inilen dikmenin "
      "ayağı <em>P</em><sub>0</sub>'ın kendisidir; denklem <em>r</em> cos(<em>θ</em> − 2<em>π</em>/3) = 4.",
      aria="Line l perpendicular to O P0 at P0(4, 2pi/3), with a point P(r, theta) on l")


# ============================================================ kardioid
f, p = equal_fig((-2.4, 0.85), (-1.6, 1.85), 168, (60, 40, 60, 40))
p.cart_axes((-2.4, 0.8), (-1.6, 1.6))
card = [pol(1 - math.cos(2 * PI * k / 720), 2 * PI * k / 720) for k in range(721)]
p.line(card, THEORY, 2.6)
p.dot((0, 0), TEXT)
p.label(0, 0, "O", ("se", "ne", "s"), gap=8)
for q in ((-2, 0), (0, 1), (0, -1)):
    p.dot(q, PRACTICE, 4.6)
p.label(-2, 0, "(−2, 0)", ("w", "nw", "sw"), size=NOTE)
p.label(0, 1, "(0, 1)", ("ne", "e", "se"), size=NOTE)
p.label(0, -1, "(0, −1)", ("se", "e", "ne"), size=NOTE)
p.at(-2.35, 1.68, "r = 1 − cos θ", NOTE + 0.5, THEORY, anchor="start")
p.at(-2.35, 1.5, "(x² + y² + x)² = x² + y²", NOTE, THEORY, anchor="start")
f.out("kardioid",
      "<em>r</em> = 1 − cos <em>θ</em> kardioidi. Eğri kutupta sivri bir uç yapar ve sola doğru açılır; "
      "dik koordinatlardaki denklemi (<em>x</em>² + <em>y</em>² + <em>x</em>)² = <em>x</em>² + <em>y</em>²'dir.",
      aria="Cardioid r = 1 - cos theta with cusp at the pole and marked points (-2,0), (0,1), (0,-1)")


# ============================================================ lemniskat
f, p = equal_fig((-3.7, 3.75), (-1.62, 1.62), 90, (70, 70, 80, 70))
p.cart_axes((-3.6, 3.6), (-1.6, 1.6), yl_pos=("ne", "e"))
for s_ in (1, -1):
    p.seg((-1.6, -1.6 * s_), (1.6, 1.6 * s_), TEXT, 1.2, "5 4", 0.55, weight=0.8)
lem = []
for k in range(0, 801):
    t = -PI / 4 + (PI / 2) * k / 800
    c2 = max(math.cos(2 * t), 0.0)
    lem.append(pol(3 * math.sqrt(c2), t))
p.line(lem, THEORY, 2.6)
p.line([(-x, y) for x, y in lem], THEORY, 2.6)
p.dot((0, 0), TEXT)
p.label(0, 0, "O", (("c", p.X(0) + 12, p.Y(0) + 29), "s"), gap=10)
p.dot((3, 0), PRACTICE, 4.6)
p.dot((-3, 0), PRACTICE, 4.6)
p.label(3, 0, "(3, 0)", ("se", "ne", "e"), size=NOTE)
p.label(-3, 0, "(−3, 0)", ("sw", "nw", "w"), size=NOTE)
p.label(1.6, 1.6, "θ = π/4", ("ne", "e"), size=NOTE, color=REMARK)
p.label(-1.6, 1.6, "θ = 3π/4", ("nw", "w"), size=NOTE, color=REMARK)
p.at(0, 2.2, "(x² + y²)² = 9(x² − y²)", NOTE + 0.5, THEORY)
p.at(0, -2.05, "r² = 9 cos 2θ", NOTE + 0.5, THEORY)
f.out("lemniskat",
      "<em>r</em>² = 9 cos 2<em>θ</em> Bernoulli lemniskatı. Eğri yalnız kutupsal eksenle en çok "
      "<em>π</em>/4 açı yapan yönlerde ve bunların ters yönlerinde bulunur.",
      aria="Lemniscate r squared = 9 cos 2 theta with loops through (3,0) and (-3,0) and the lines y = x, y = -x",
      css=WIDE)


# ============================================================ merkezil-cember
f, p = equal_fig((-5.4, 6.5), (-5.35, 5.45), 46, (60, 45, 170, 40))
for r in range(1, 5):
    p.ring((0, 0), r, TEXT, 0.8, None, 0.16, weight=0.15)
for k in range(1, 12):
    p.seg((0, 0), pol(5, k * PI / 6), TEXT, 0.8, None, 0.16, weight=0.15)
p.polar_axis(6)
p.ring((0, 0), 5, THEORY, 2.6)
p.seg((0, 0), pol(5, PI / 3), PRACTICE, 2.0)
p.dot((0, 0), TEXT)
p.label(0, 0, "O", ("sw", "s", "w"), gap=8, halo=True)
p.dot((5, 0), PRACTICE, 4.6)
p.dot((0, 5), PRACTICE, 4.6)
p.label(5, 0, "(5, 0)", ("se", "s"), halo=True)
p.label(0, 5, "(5, π/2)", ("ne", "n"), halo=True)
p.along((0, 0), pol(5, PI / 3), "5", -1, size=NOTE, color=PRACTICE, halo=True)
p.at(4.25, 4.55, "r = 5", NOTE + 0.5, THEORY, anchor="start")
p.at(4.25, 4.05, "x² + y² = 25", NOTE, THEORY, anchor="start")
f.out("merkezil-cember",
      "Kutup merkezli, 5 yarıçaplı çember: kutupsal denklemi <em>r</em> = 5, dik denklemi "
      "<em>x</em>² + <em>y</em>² = 25.",
      aria="Circle of radius 5 centred at the pole on a faint polar grid")


# ============================================================ elips-kutupsal
f, p = equal_fig((-5.0, 5.2), (-4.0, 4.0), 56, (90, 45, 150, 45))
p.cart_axes((-5, 5), (-4, 4))
ell = [(4 * math.cos(2 * PI * k / 480), 3 * math.sin(2 * PI * k / 480)) for k in range(481)]
p.line(ell, THEORY, 2.6)
P = (2.4, 2.4)
p.seg((0, 0), P, PRACTICE, 2.1)
p.angle((0, 0), 0, PI / 4, 0.7, PRACTICE, 1.4)
p.dot((0, 0), TEXT)
p.label(0, 0, "O", ("sw", "s", "w"), gap=8)
for q in ((4, 0), (-4, 0), (0, 3), (0, -3)):
    p.dot(q, THEORY, 4.2)
p.dot(P, PRACTICE, 4.6)
p.label(4, 0, "(4, 0)", ("se", "s"), size=NOTE)
p.label(-4, 0, "(−4, 0)", ("sw", "s"), size=NOTE)
p.label(0, 3, "(0, 3)", ("nw", "w"), size=NOTE)
p.label(0, -3, "(0, −3)", ("sw", "w"), size=NOTE)
p.label(*P, "P(12√2/5, π/4)", ("ne", "e", "n"))
p.along((0, 0), P, "r", 1, t=0.6, size=NAME, color=PRACTICE)
p.angle_label((0, 0), 0, PI / 4, 0.7, "π/4", "out", NOTE, PRACTICE, fs=(0, -0.15, 0.15))
p.at(6.3, 3.75, "9x² + 16y² = 144", NOTE + 0.5, THEORY, anchor="end")
p.at(6.3, 3.35, "r = 12 / √(9 + 7 sin²θ)", NOTE, THEORY, anchor="end")
f.out("elips-kutupsal",
      "9<em>x</em>² + 16<em>y</em>² = 144 elipsi ve <em>θ</em> = <em>π</em>/4 yönündeki kutupsal yarıçap: "
      "<em>r</em> = 12√2/5, yani <em>P</em> = (12/5, 12/5).",
      aria="Ellipse 9x^2 + 16y^2 = 144 with semi-axes 4 and 3 and the polar radius at angle pi/4")


# ============================================================ r-cos-iki
f, p = equal_fig((-0.6, 4.6), (-2.15, 2.75), 100, (50, 45, 150, 45))
Q = (2, 0)
p.polar_axis(4)
p.seg((2, -2), (2, 2.5), THEORY, 2.5)
p.seg((0, 0), Q, PRACTICE, 2.6)
p.right_angle(Q, (4, 0), (2, 2.5), 11)
origin(p)
p.dot(Q, PRACTICE, 4.6)
p.label(*Q, "Q(2, 0)", ("se", "s", "sw"), gap=8)
p.label(2, 2.5, "d: r cos θ = 2", ("e", "ne"), gap=9, size=NOTE, color=THEORY)
p.along((0, 0), Q, "2", 1, size=NOTE, color=PRACTICE)
f.out("r-cos-iki",
      "<em>r</em> cos <em>θ</em> = 2 doğrusu: kutuptan inilen dikmenin ayağı <em>Q</em>(2, 0)'dır ve doğru "
      "kutupsal eksene diktir, yani <em>x</em> = 2.",
      aria="Vertical line x = 2 with foot Q(2, 0) of the perpendicular from the pole")


# ---------------------------------------------------------------------------
for name, content in OUT.items():
    with io.open(OUT_DIR / f"{PREFIX}{name}.md", "w", encoding="utf-8", newline="\n") as fh:
        fh.write(content)
print(f"generated {len(OUT)} figures:", ", ".join(OUT))
