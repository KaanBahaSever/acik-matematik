# -*- coding: utf-8 -*-
"""
Figures for the "Koniklerin Sınıflandırılması" chapter of Analitik Geometri
(dersler/analitik-geometri/koniklerin-siniflandirilmasi.qmd).

The figures are NOT produced at build time. Run

    python scripts/analytic_figures/kns.py
    python scripts/center_figures.py "analytic-kns-*.md" --keep-width

and paste each scripts/_figures/analytic-kns-<name>.md block into the .qmd.
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
PREFIX = "analytic-kns-"
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
            if len(word) == 1 or word.isupper() or set(word) <= set("xy"):
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



# ---------------------------------------------------------------------------
# helpers for this chapter
# ---------------------------------------------------------------------------
import re  # noqa: E402

_WORD = re.compile(r"(?<![A-Za-z<>/])([A-Za-z]+)(?![A-Za-z>])")


def C(s):
    """Caption markup: inside $...$ single letters (and x/y runs) are set in italic, _{..} is a subscript."""
    def conv(m):
        t = m.group(1)
        t = _WORD.sub(lambda k: "".join(f"<em>{c}</em>" for c in k.group(1))
                      if len(k.group(1)) == 1 or set(k.group(1)) <= set("xyXY") else k.group(1), t)
        return re.sub(r"_\{([^}]*)\}|_(\w)", lambda k: f"<sub>{k.group(1) or k.group(2)}</sub>", t)
    return re.sub(r"\$([^$]*)\$", conv, s)


def frame(th, c=(0.0, 0.0)):
    """Map coordinates in axes turned by th (origin c) to drawing coordinates."""
    e1, e2 = u(th), u(th + PI / 2)
    return lambda a, b: (c[0] + a * e1[0] + b * e2[0], c[1] + a * e1[1] + b * e2[1])


def samp(t0, t1, n=500):
    return [t0 + (t1 - t0) * k / n for k in range(n + 1)]


def pieces(pts, rect):
    out, cur = [], []
    for q in pts:
        if rect[0] <= q[0] <= rect[1] and rect[2] <= q[1] <= rect[3]:
            cur.append(q)
        else:
            if len(cur) > 1:
                out.append(cur)
            cur = []
    if len(cur) > 1:
        out.append(cur)
    return out


def draw(p, pts, color=PRACTICE, width=2.5, dash=None, opacity=1.0, pad=0.04, weight=1.0):
    """Polyline clipped to the panel (split into the runs that stay inside)."""
    rect = (p.xmin + pad, p.xmax - pad, p.ymin + pad, p.ymax - pad)
    runs = pieces(pts, rect)
    for r in runs:
        p.line(r, color, width, dash, opacity, weight)
    return runs


def full_line(p, pt, d, color, width=2.3, dash=None, opacity=1.0, weight=1.0, pad=0.04):
    rect = (p.xmin + pad, p.xmax - pad, p.ymin + pad, p.ymax - pad)
    s = clip_line(pt, d, rect)
    p.seg(s[0], s[1], color, width, dash, opacity, weight)
    return s


def axes(p, step=1, xl="X", yl="Y", opacity=0.6, ticks=True, lo=None, hi=None,
         xl_pos=("e", "se", "ne"), yl_pos=("n", "nw", "ne")):
    """Grey arrowed X, Y axes over the whole panel; returns the tick values."""
    x0, x1 = (lo or (p.xmin, p.ymin))[0], (hi or (p.xmax, p.ymax))[0]
    y0, y1 = (lo or (p.xmin, p.ymin))[1], (hi or (p.xmax, p.ymax))[1]
    p.arrow((x0, 0), (x1, 0), TEXT, 1.2, 8, opacity=opacity)
    p.arrow((0, y0), (0, y1), TEXT, 1.2, 8, opacity=opacity)
    xs = [k * step for k in range(math.ceil(x0 / step), math.floor((x1 - 0.3 * step) / step) + 1) if k]
    ys = [k * step for k in range(math.ceil(y0 / step), math.floor((y1 - 0.3 * step) / step) + 1) if k]
    if ticks:
        parts = []
        for k in xs:
            X, Y = p.X(k), p.Y(0)
            parts.append(f"M{X:.1f},{Y - 3.5:.1f} L{X:.1f},{Y + 3.5:.1f}")
            p.fig.segs.append(([(X, Y - 3.5), (X, Y + 3.5)], 0.4))
        for k in ys:
            X, Y = p.X(0), p.Y(k)
            parts.append(f"M{X - 3.5:.1f},{Y:.1f} L{X + 3.5:.1f},{Y:.1f}")
            p.fig.segs.append(([(X - 3.5, Y), (X + 3.5, Y)], 0.4))
        p.add(f'<path d="{" ".join(parts)}" stroke="{TEXT}" stroke-width="1.1" opacity="{opacity}"/>')
    p._axis_names = (x1, y1, xl, yl, xl_pos, yl_pos)
    return xs, ys


def axis_names(p):
    x1, y1, xl, yl, xl_pos, yl_pos = p._axis_names
    if xl:
        p.label(x1, 0, xl, xl_pos, gap=8, size=AXIS)
    if yl:
        p.label(0, y1, yl, yl_pos, gap=8, size=AXIS)


def numbers(p, xs=(), ys=(), size=11, yright=False, skip=()):
    """Tick numbers; a number that would touch a curve, a dot or a label is left out."""
    for k in xs:
        if k in skip:
            continue
        s = num(k)
        w, h = p._wh(s, size)
        X, Y = p.X(k), p.Y(0)
        box = (X - w / 2, Y + 6, X + w / 2, Y + 6 + h)
        if p.fig.cost(box, pad=1.0) < 25:
            p._draw_text(box, "middle", s, size, TEXT, False)
    for k in ys:
        if ("y", k) in skip:
            continue
        s = num(k)
        w, h = p._wh(s, size)
        X, Y = p.X(0), p.Y(k)
        box = (X + 7, Y - h / 2, X + 7 + w, Y + h / 2) if yright else (X - 7 - w, Y - h / 2, X - 7, Y + h / 2)
        if p.fig.cost(box, pad=1.0) < 25:
            p._draw_text(box, "start" if yright else "end", s, size, TEXT, False)


def turned_axes(p, to, xr, yr, names=("X'", "Y'"), color=THEORY, width=1.5, opacity=0.9, dash=None,
                xprefs=None, yprefs=None, th=None):
    """Axes of a turned (and/or moved) frame: to(a, b) maps frame coordinates to the drawing."""
    p.arrow(to(xr[0], 0), to(xr[1], 0), color, width, 8.5, dash=dash, opacity=opacity)
    p.arrow(to(0, yr[0]), to(0, yr[1]), color, width, 8.5, dash=dash, opacity=opacity)
    t = th if th is not None else 0.0
    return lambda: (p.label(*to(xr[1], 0), names[0], xprefs or compass(t), gap=8, size=AXIS, color=color),
                    p.label(*to(0, yr[1]), names[1], yprefs or compass(t + PI / 2), gap=8, size=AXIS,
                            color=color))


def around(cx, cy, dx, dy, n=5):
    """Candidate centres (data units) on a small grid around (cx, cy), nearest first."""
    pts = [(cx + dx * i / n, cy + dy * j / n) for i in range(-n, n + 1) for j in range(-n, n + 1)]
    return sorted(pts, key=lambda q: math.hypot((q[0] - cx) / (dx or 1), (q[1] - cy) / (dy or 1)))


def stack(p, lines, centers, size=NOTE, gap=3, halo=True, anchor=None):
    """One or more centred text lines [(text, colour), ...]; the first clean centre wins.

    anchor = data point: draw a thin leader from it to the text."""
    whs = [p._wh(s, size) for s, _ in lines]
    H = sum(h for _, h in whs) + gap * (len(lines) - 1)
    best = None
    for (cx, cy) in centers:
        X, Y = p.X(cx), p.Y(cy)
        y, boxes = Y - H / 2, []
        for (w, h) in whs:
            boxes.append((X - w / 2, y, X + w / 2, y + h))
            y += h + gap
        c = sum(p.fig.cost(b) for b in boxes)
        if best is None or c < best[0]:
            best = (c, boxes)
        if c == 0:
            break
    if best[0] > 0:
        print(f"  note: '{lines[0][0]}' placed with cost {best[0]:.0f}")
    boxes = best[1]
    if anchor is not None:
        ub = (min(b[0] for b in boxes), boxes[0][1], max(b[2] for b in boxes), boxes[-1][3])
        p._leader(p.px(anchor), ub, TEXT)
    for (s, c), b in zip(lines, boxes):
        p._draw_text(b, "middle", s, size, c, halo)
    return boxes


def ring(p, pt, s, size=NAME, color=TEXT, r0=12, r1=46, halo=False, first=None):
    """Label on rings around pt: every 15 degrees, nearest ring first (first = preferred angle, degrees)."""
    w, h = p._wh(s, size)
    X, Y = p.px(pt)
    angs = list(range(0, 360, 15))
    if first is not None:
        angs.sort(key=lambda a: abs((a - first + 180) % 360 - 180))
    cands = []
    for r in range(r0, r1 + 1, 3):
        for a in angs:
            t = math.radians(a)
            ext = abs(math.cos(t)) * w / 2 + abs(math.sin(t)) * h / 2
            cands.append(("c", X + (r + ext) * math.cos(t), Y - (r + ext) * math.sin(t)))
    return p.label(pt[0], pt[1], s, tuple(cands), size=size, color=color, halo=halo)


def origin_auto(p, first=225):
    p.dot((0, 0), TEXT)
    ring(p, (0, 0), "O", first=first)


def lab(p, pt, s, prefs, color=TEXT, size=NAME, gap=7, halo=True, leader=False):
    return p.label(pt[0], pt[1], s, prefs, gap=gap, size=size, color=color, halo=halo, leader=leader)


def ellipse_pts(to, a, b, n=360):
    return [to(a * math.cos(t), b * math.sin(t)) for t in samp(0, 2 * PI, n)]


def hyp_pts(to, a, b, s=1, T=4.0, vertical=False, n=900):
    """One branch: (s a cosh t, b sinh t) in frame coordinates (swapped if vertical)."""
    out = []
    for t in samp(-T, T, n):
        A, B = s * a * math.cosh(t), b * math.sinh(t)
        out.append(to(B, A) if vertical else to(A, B))
    return out


S2, S3, S5 = math.sqrt(2), math.sqrt(3), math.sqrt(5)
ID = frame(0.0)


# ============================================================ oteleme-elips
Op = (2.0, -3.0)
f, p = equal_fig((-1.8, 6.8), (-6.0, 1.6), 58, (40, 30, 45, 30))
xs, ys = axes(p)
names_new = turned_axes(p, frame(0.0, Op), (-3.7, 4.75), (-2.95, 4.55), xprefs=("ne", "se", "e"),
                        yprefs=("e", "ne", "nw"))
p.line(ellipse_pts(frame(0.0, Op), 3, 2), PRACTICE, 2.6)
p.dot(Op, THEORY, 4.4)
V = {"(−1, −3)": ((-1.0, -3.0), ("nw", "sw", "n")), "(5, −3)": ((5.0, -3.0), ("ne", "se", "n")),
     "(2, −5)": ((2.0, -5.0), ("se", "sw", "e")), "(2, −1)": ((2.0, -1.0), ("ne", "nw", "e"))}
for s, (q, pr) in V.items():
    p.dot(q, PRACTICE, 4.2)
origin(p, ("sw", "se", "nw"))
axis_names(p)
names_new()
for s, (q, pr) in V.items():
    lab(p, q, s, pr, size=NOTE)
lab(p, Op, "O'(2, −3)", ("se", "sw", "ne"), color=THEORY, size=NOTE)
stack(p, [("4x² + 9y² − 16x + 54y + 61 = 0", PRACTICE), ("x'²/9 + y'²/4 = 1", THEORY)],
      around(4.6, -5.35, 1.6, 0.5))
numbers(p, xs, ys)
f.out("oteleme-elips",
      C("Eksenler $O'(2, −3)$'e ötelenince birinci dereceden terimler kaybolur ve elipsin standart denklemi "
        "ortaya çıkar."),
      aria="Ellipse 4x2 + 9y2 - 16x + 54y + 61 = 0 with the axes translated to O prime(2, -3)")


# ============================================================ donme-parabol (shared data)
R4 = frame(PI / 4)
XR, YR = (-6.2, 2.6), (-3.2, 4.2)
par4 = [(-(t * t + 2) / 12, -(t * t + 2) / 12 - t) for t in samp(-8.6, 2.6, 700)]
V4 = (-11 / 12, 25 / 12)

# ============================================================ donme-parabol-donme
f, p = equal_fig(XR, YR, 58, (40, 30, 45, 30))
xs, ys = axes(p)
nn = turned_axes(p, R4, (-4.3, 3.55), (-2.9, 5.6), th=PI / 4, xprefs=("se", "e", "s"), yprefs=("ne", "e", "n"))
draw(p, par4, PRACTICE, 2.6)
ang(p, (0, 0), 0, PI / 4, 0.75, "π/4", THEORY, head=True, size=NOTE, fs=(0, 0.15, -0.15))
p.dot(V4, PRACTICE, 4.4)
origin_auto(p, first=290)
axis_names(p)
nn()
lab(p, V4, "V", ("ne", "e", "n", "nw"))
qa = (-27 / 12, -27 / 12 + 5)
stack(p, [("x² + y² − 2xy + 12x + 2 = 0", PRACTICE)], around(-1.75, 3.72, 0.3, 0.2), anchor=qa)
numbers(p, xs, ys)
f.out("donme-parabol-donme",
      C("Eksenler $π/4$ döndürülünce karma terim kaybolur: $y'² + 3√2x' − 3√2y' + 1 = 0$."),
      aria="Parabola x2 + y2 - 2xy + 12x + 2 = 0 with the axes turned by pi over 4")


# ============================================================ donme-parabol-oteleme
f, p = equal_fig(XR, YR, 58, (40, 30, 45, 30))
axes(p, ticks=False, opacity=0.45)
turned_axes(p, R4, (-4.3, 3.55), (-2.9, 5.6), color=THEORY, width=1.2, opacity=0.55, dash="6 4",
            th=PI / 4)
R4V = frame(PI / 4, V4)
n2 = turned_axes(p, R4V, (-7.2, 2.7), (-3.9, 2.25), names=("X''", "Y''"), color=BASE, width=1.6,
                 th=PI / 4, xprefs=("se", "e", "s"), yprefs=("sw", "w", "s"))
draw(p, par4, PRACTICE, 2.6)
p.dot(V4, BASE, 4.6)
origin_auto(p, first=290)
axis_names(p)
lab(p, R4(3.55, 0), "X'", ("se", "e", "s"), color=THEORY, size=AXIS, halo=False, gap=8)
lab(p, R4(0, 5.6), "Y'", ("ne", "e", "n"), color=THEORY, size=AXIS, halo=False, gap=8)
n2()
p.along(R4V(-7.0, 0), R4V(1.8, 0), "y = x + 3", -1, t=0.84, size=NOTE, color=BASE, halo=True)
stack(p, [("V(−11/12, 25/12)", TEXT)], around(1.3, 2.9, 1.2, 0.9), size=NOTE, anchor=V4)
stack(p, [("y''² = −3√2 x''", PRACTICE)], around(-4.3, 0.9, 0.9, 0.7))
f.out("donme-parabol-oteleme",
      C("Eksenler tepe noktasına ötelenince parabolün standart denklemi $y''² = −3√2 x''$ elde edilir."),
      aria="The same parabola with new axes through its vertex V(-11/12, 25/12)")


# ============================================================ konik-turleri
PPU, SIDE, GX, L, TOP, ROWGAP = 27, 7 * 27, 46, 22, 28, 58
W = L * 2 + 3 * SIDE + 2 * GX
H = TOP + 2 * SIDE + ROWGAP + 30
f = Fig(W, H)
Rg = (-3.5, 3.5)


def k_hyp(p):
    for s in (1, -1):
        draw(p, [(s * 2 * math.cosh(t), math.sinh(t)) for t in samp(-2.2, 2.2, 300)], PRACTICE, 2.4)
    for m in (0.5, -0.5):
        full_line(p, (0, 0), (1, m), TEXT, 1.1, "4 3", 0.5, weight=0.3)


def k_par(p):
    draw(p, [(t * t / 4, t) for t in samp(-3.6, 3.6, 300)], PRACTICE, 2.4)


def k_cross(p):
    for m in (0.5, -0.5):
        full_line(p, (0, 0), (1, m), PRACTICE, 2.4, pad=0.2)


def k_par2(p):
    for c in (2, -2):
        full_line(p, (0, c), (1, 0), PRACTICE, 2.4, pad=0.2)


def k_point(p):
    p.dot((0, 0), PRACTICE, 5.2)


PANELS = [("elips", "x²/9 + y²/4 = 1", lambda p: p.line(ellipse_pts(ID, 3, 2), PRACTICE, 2.4)),
          ("hiperbol", "x²/4 − y² = 1", k_hyp),
          ("parabol", "y² = 4x", k_par),
          ("kesişen iki doğru", "x² − 4y² = 0", k_cross),
          ("paralel iki doğru", "y² = 4", k_par2),
          ("tek nokta", "x² + 2y² = 0", k_point)]
for i, (title, eq, fn) in enumerate(PANELS):
    r, c = divmod(i, 3)
    x0, y0 = L + c * (SIDE + GX), TOP + r * (SIDE + ROWGAP)
    p = f.panel(x0, y0, Rg, Rg, PPU)
    p.arrow((-3.3, 0), (3.3, 0), TEXT, 1.1, 7, opacity=0.55)
    p.arrow((0, -3.3), (0, 3.1), TEXT, 1.1, 7, opacity=0.55)
    fn(p)
    p.label(3.3, 0, "X", ("se", "ne", "e"), gap=7, size=12)
    p.label(0, 3.1, "Y", ("e", "w"), gap=7, size=12)
    at_px(p, x0 + SIDE / 2, y0 - 12, title, 13)
    at_px(p, x0 + SIDE / 2, y0 + SIDE + 15, eq, 12, PRACTICE)
f.out("konik-turleri",
      "İkinci dereceden denklemlerin belirttiği kümeler: üç konik ve üç yozlaşmış durum (sanal elips ile "
      "sanal iki doğru boş kümedir, çizilmez).",
      aria="Six panels: ellipse, hyperbola, parabola, two crossing lines, two parallel lines, a single point",
      css=WIDE)


# ============================================================ kesisen-dogrular
f, p = equal_fig((-4.5, 4.5), (-3.0, 4.5), 60, (40, 30, 45, 30))
xs, ys = axes(p)
d1 = full_line(p, (-2, 0), (2, 1), PRACTICE, 2.4)
d2 = full_line(p, (1, 0), (-1, 1), THEORY, 2.4)
K = (0.0, 1.0)
p.dot(K, TEXT, 4.6)
origin(p, ("sw", "se", "s"))
axis_names(p)
lab(p, K, "K(0, 1)", ("w", "nw", "sw", "n"))
a1, b1 = sorted(d1)
p.along(a1, b1, "x − 2y + 2 = 0", -1, t=0.8, size=NOTE, color=PRACTICE, halo=True)
a2, b2 = sorted(d2)
p.along(a2, b2, "x + y − 1 = 0", 1, t=0.82, size=NOTE, color=THEORY, halo=True)
numbers(p, xs, ys)
f.out("kesisen-dogrular",
      C("$d$ > 0 ve $D$ = 0: $x² − xy − 2y² + x + 4y − 2 = 0$ denklemi $K(0, 1)$'de kesişen iki doğrudur."),
      aria="Two lines x - 2y + 2 = 0 and x + y - 1 = 0 meeting at K(0, 1)")


# ============================================================ merkez-tanimi
Mc = (2.0, 1.0)
P = (2 + 3 * math.cos(D(40)), 1 + 2 * math.sin(D(40)))
Ps = (2 * Mc[0] - P[0], 2 * Mc[1] - P[1])
f, p = equal_fig((-1.6, 5.8), (-1.6, 3.6), 72, (30, 25, 35, 25))
p.line(ellipse_pts(frame(0.0, Mc), 3, 2), PRACTICE, 2.6)
p.seg(P, Ps, THEORY, 1.9)
eq_tick(p, P, Mc, 0.5, 1, THEORY)
eq_tick(p, Mc, Ps, 0.5, 1, THEORY)
p.dot(Mc, TEXT, 4.6)
p.dot(P, THEORY, 4.4)
p.dot(Ps, THEORY, 4.4)
lab(p, Mc, "M", ("se", "nw", "s", "n"))
lab(p, P, "P", ("ne", "e", "n"))
lab(p, Ps, "P*", ("sw", "w", "s"))
f.out("merkez-tanimi",
      C("$M$, koniğin merkezidir: koniğin her $P$ noktasının $M$'ye göre simetriği $P$* de konik üzerindedir."),
      aria="Ellipse with centre M; a point P and its reflection P star through M both lie on the ellipse")


# ============================================================ merkez-elips
P = (3 * math.cos(D(50)), 2 * math.sin(D(50)))
f, p = equal_fig((-3.8, 3.8), (-2.6, 2.6), 70, (40, 30, 45, 30))
axes(p, ticks=False)
p.line(ellipse_pts(ID, 3, 2), PRACTICE, 2.6)
p.seg(P, (-P[0], -P[1]), THEORY, 1.7, "6 4")
p.dot(P, THEORY, 4.4)
p.dot((-P[0], -P[1]), THEORY, 4.4)
origin(p, ("sw", "se", "nw"))
axis_names(p)
lab(p, P, "P(x_1, y_1)", ("ne", "e", "n"))
lab(p, (-P[0], -P[1]), "P*(−x_1, −y_1)", ("sw", "w", "s"))
f.out("merkez-elips",
      C("Elipsin her noktasının $O$'ya göre simetriği de elips üzerindedir."),
      aria="Ellipse x2/9 + y2/4 = 1 with a point P and its reflection through the origin")


# ============================================================ merkez-hiperbol
t9 = 0.9
P = (2 * math.cosh(t9), 1.5 * math.sinh(t9))
f, p = equal_fig((-4.2, 4.2), (-3.0, 3.0), 66, (40, 30, 45, 30))
axes(p, ticks=False)
for m in (0.75, -0.75):
    full_line(p, (0, 0), (1, m), TEXT, 1.1, "4 3", 0.5, weight=0.3)
for s in (1, -1):
    draw(p, hyp_pts(ID, 2, 1.5, s, 2.3), PRACTICE, 2.6)
p.seg(P, (-P[0], -P[1]), THEORY, 1.7, "6 4")
p.dot(P, THEORY, 4.4)
p.dot((-P[0], -P[1]), THEORY, 4.4)
origin(p, ("sw", "se", "nw"))
axis_names(p)
lab(p, P, "P(x_1, y_1)", ("e", "se", "ne"))
lab(p, (-P[0], -P[1]), "P*(−x_1, −y_1)", ("w", "nw", "sw"))
f.out("merkez-hiperbol",
      C("Hiperbolün bir kolundaki her noktanın $O$'ya göre simetriği öbür koldadır."),
      aria="Hyperbola x2/4 - y2/2.25 = 1; a point P on the right branch and its reflection on the left branch")


# ============================================================ paralel-dogrular
f, p = equal_fig((-5.0, 4.0), (-3.2, 3.2), 60, (40, 30, 45, 30))
xs, ys = axes(p)
Mp = (-1.0, 0.0)
u1 = full_line(p, (1, 0), (-2, 1), PRACTICE, 2.4)
u2 = full_line(p, (-3, 0), (-2, 1), PRACTICE, 2.4)
um = full_line(p, (-1, 0), (-2, 1), THEORY, 1.4, "6 4", 0.9)
p.arrow((-2.6, 0), (0.55, 0), BASE, 1.9, 8.5)
p.arrow((-1, -1.9), (-1, 1.9), BASE, 1.9, 8.5)
p.dot(Mp, BASE, 4.6)
origin(p, ("se", "s", "sw"))
axis_names(p)
lab(p, (0.55, 0), "X'", ("ne", "n", "nw"), color=BASE, size=AXIS, halo=False, gap=8)
lab(p, (-1, 1.9), "Y'", ("w", "nw", "e"), color=BASE, size=AXIS, halo=False, gap=8)
lab(p, Mp, "M(−1, 0)", ("sw", "nw", "s"), size=NOTE)
p.along(*sorted(u1), "x + 2y − 1 = 0", 1, t=0.86, size=NOTE, color=PRACTICE, halo=True)
p.along(*sorted(u2), "x + 2y + 3 = 0", -1, t=0.12, size=NOTE, color=PRACTICE, halo=True)
stack(p, [("merkezler: x + 2y + 1 = 0", THEORY)], around(-2.3, 2.75, 0.3, 0.2), anchor=(-3.4, 1.2))
numbers(p, xs, ys)
f.out("paralel-dogrular",
      C("$d$ = $D$ = 0 ve $a'_{33}$ = −4 < 0: denklem paralel iki doğrudur; merkezler aralarındaki orta "
        "doğrudadır."),
      aria="Two parallel lines x + 2y - 1 = 0 and x + 2y + 3 = 0 with the line of centres between them")


# ============================================================ parametreli-aile
Mf = (1.0, 0.0)
RM = frame(PI / 4, Mf)
f, p = equal_fig((-3.0, 5.0), (-4.0, 4.0), 76, (40, 30, 45, 30))
xs, ys = axes(p)
nn = turned_axes(p, RM, (-5.3, 5.3), (-4.2, 4.2), names=("X''", "Y''"), color=TEXT, width=1.2,
                 opacity=0.55, dash="6 4", th=PI / 4)
ang(p, Mf, 0, PI / 4, 0.8, "π/4", TEXT, head=True, size=NOTE, fs=(0, 0.15, -0.15))
e_big = ellipse_pts(RM, 2 / S3, 2)
e_small = ellipse_pts(RM, 1 / S2, 0.5)
p.line(e_big, THEORY, 2.4)
p.line(e_small, BASE, 2.4)
for s in (1, -1):
    draw(p, [(1 + x, 1 / x) for x in samp(s * 0.22, s * 4.2, 500)], PRACTICE, 2.4)
for c in (1 + S3, 1 - S3):
    full_line(p, (c, 0), (1, -1), REMARK, 2.4)
p.dot(Mf, TEXT, 4.8)
origin(p, ("sw", "nw", "s"))
axis_names(p)
nn()
stack(p, [("M(1, 0)", TEXT), ("(m = 2)", TEXT)], around(1.75, -0.45, 0.5, 0.35), size=NOTE)
stack(p, [("m = −2", THEORY)], around(-1.55, 1.45, 0.4, 0.4))
stack(p, [("m = 3", BASE)], around(1.0, -1.0, 0.2, 0.15))
lab(p, (1 + 0.45, 1 / 0.45), "m = 0", ("e", "ne", "se"), color=PRACTICE, size=NOTE)
lab(p, (1 + S3 - 3.7, 3.7), "m = −1", ("w", "sw", "nw"), color=REMARK, size=NOTE)
numbers(p, xs, ys)
f.out("parametreli-aile",
      C("$mx² − 2xy + my² − 2mx + 2y + 2 = 0$ ailesinin bazı üyeleri; merkezli üyelerin hepsi $M(1, 0)$ "
        "merkezlidir ve eksenleri $π/4$ döndürülmüş doğrultudadır."),
      aria="Members m = -2, 3, 0, -1 of the family; the central ones are centred at M(1, 0)", css=WIDE)


# ============================================================ exr-donme-parabol
TH = math.atan2(2, 1)
RT = frame(TH)
f, p = equal_fig((-4.2, 6.0), (-1.5, 6.2), 54, (40, 30, 45, 30))
xs, ys = axes(p)
nn = turned_axes(p, RT, (-0.75, 6.9), (-2.3, 4.6), th=TH, xprefs=("e", "ne", "se"), yprefs=("n", "nw", "w"))
draw(p, [RT(t * t / 8, t) for t in samp(-5.2, 4.8, 500)], PRACTICE, 2.6)
ang(p, (0, 0), 0, TH, 0.95, "θ = arctan 2", TEXT, head=True, size=NOTE, fs=(-0.1, 0, -0.25, 0.1))
Q = (2 * S5, 0.0)
p.dot(Q, PRACTICE, 4.4)
origin_auto(p, first=210)
axis_names(p)
nn()
stack(p, [("(2√5, 0)", TEXT), ("x' = 2, y' = −4", THEORY)], around(Q[0], -0.85, 0.3, 0.2), size=NOTE)
stack(p, [("y'² = 8x'", PRACTICE)], around(*RT(4.2, 1.9), 0.8, 0.8))
numbers(p, xs, ys)
f.out("exr-donme-parabol",
      C("Eksenler arctan 2 kadar döndürülünce $4x² − 4xy + y² − 8√5x − 16√5y = 0$ parabolü $y'² = 8x'$ olur; "
        "parabolün ekseni $y = 2x$ doğrusudur."),
      aria="Parabola y prime squared = 8 x prime in axes turned by arctan 2")


# ============================================================ exr-donme-hiperbol (shared)
XR, YR = (-4.5, 9.0), (-2.5, 10.5)
branches = [[(2 + t, 4 + 8 / t) for t in samp(1.2, 7.1, 500)],
            [(2 + t, 4 + 8 / t) for t in samp(-6.6, -1.2, 500)]]

# ============================================================ exr-donme-hiperbol-donme
f, p = equal_fig(XR, YR, 47, (40, 30, 45, 30))
xs, ys = axes(p, step=2)
nn = turned_axes(p, R4, (-3.4, 12.6), (-3.4, 6.2), th=PI / 4, xprefs=("se", "e", "s"), yprefs=("ne", "e", "n"))
full_line(p, (2, 0), (0, 1), TEXT, 1.1, "4 3", 0.5, weight=0.3)
full_line(p, (0, 4), (1, 0), TEXT, 1.1, "4 3", 0.5, weight=0.3)
for br in branches:
    draw(p, br, PRACTICE, 2.6)
ang(p, (0, 0), 0, PI / 4, 1.3, "π/4", THEORY, head=True, size=NOTE, fs=(0, 0.15, -0.15))
origin_auto(p, first=202)
axis_names(p)
nn()
stack(p, [("xy − 2y − 4x = 0", PRACTICE)], around(6.3, 9.8, 1.5, 0.6), anchor=(2 + 1.9, 4 + 8 / 1.9))
numbers(p, xs, ys)
f.out("exr-donme-hiperbol-donme",
      C("Eksenler $π/4$ döndürülünce karma terim kaybolur: $x'² − y'² − 6√2x' + 2√2y' = 0$."),
      aria="Hyperbola xy - 2y - 4x = 0 with the axes turned by pi over 4", css=WIDE)


# ============================================================ exr-donme-hiperbol-oteleme
Cc = (2.0, 4.0)
RC = frame(PI / 4, Cc)
A1, A2 = (2 + 2 * S2, 4 + 2 * S2), (2 - 2 * S2, 4 - 2 * S2)
f, p = equal_fig(XR, YR, 47, (40, 30, 45, 30))
axes(p, step=2, ticks=False, opacity=0.45)
turned_axes(p, R4, (-3.4, 12.6), (-3.4, 6.2), color=THEORY, width=1.2, opacity=0.55, dash="6 4", th=PI / 4)
n2 = turned_axes(p, RC, (-8.2, 7.9), (-5.3, 7.6), names=("X''", "Y''"), color=BASE, width=1.6, th=PI / 4,
                 xprefs=("se", "e", "s"), yprefs=("ne", "e", "n", "sw"))
full_line(p, (2, 0), (0, 1), TEXT, 1.1, "4 3", 0.45, weight=0.3)
full_line(p, (0, 4), (1, 0), TEXT, 1.1, "4 3", 0.45, weight=0.3)
for br in branches:
    draw(p, br, PRACTICE, 2.6)
p.dot(Cc, BASE, 4.6)
p.dot(A1, PRACTICE, 4.4)
p.dot(A2, PRACTICE, 4.4)
origin_auto(p, first=202)
axis_names(p)
lab(p, R4(12.6, 0), "X'", ("se", "e", "s"), color=THEORY, size=AXIS, halo=False, gap=8)
lab(p, R4(0, 6.2), "Y'", ("ne", "e", "n"), color=THEORY, size=AXIS, halo=False, gap=8)
n2()
stack(p, [("C(2, 4)", TEXT)], around(0.7, 4.35, 0.2, 0.15))
lab(p, A1, "A_1", ("se", "e", "s"))
lab(p, A2, "A_2", ("nw", "w", "n"))
stack(p, [("x''² − y''² = 16", PRACTICE)], around(7.3, 6.6, 0.8, 0.8))
f.out("exr-donme-hiperbol-oteleme",
      C("Eksenler merkez $C(2, 4)$'e ötelenince ikizkenar hiperbolün standart denklemi $x''² − y''² = 16$ "
        "elde edilir."),
      aria="The same hyperbola with new axes through its centre C(2, 4) and vertices A1, A2", css=WIDE)


# ============================================================ exr-cins-i
Mi = (3 / 32, 5 / 32)
RI = frame(PI / 4, Mi)
ay, bx = math.sqrt(2045 / 512), math.sqrt(2045 / 128)
f, p = equal_fig((-6.0, 6.0), (-6.0, 6.0), 44, (40, 30, 45, 30))
xs, ys = axes(p, step=2)
nn = turned_axes(p, RI, (-8.2, 8.2), (-8.2, 8.2), names=("X''", "Y''"), th=PI / 4,
                 xprefs=("se", "e", "s"), yprefs=("ne", "n", "e"))
for m in (0.5, -0.5):
    full_line(p, Mi, frame(PI / 4)(1, m), TEXT, 1.1, "4 3", 0.5, weight=0.3)
for s in (1, -1):
    draw(p, hyp_pts(RI, ay, bx, s, 3.0, vertical=True), PRACTICE, 2.6)
ang(p, Mi, 0, PI / 4, 1.2, "π/4", THEORY, head=True, size=NOTE, fs=(0, 0.15, -0.15))
Av1, Av2 = RI(0, ay), RI(0, -ay)
p.dot(Av1, PRACTICE, 4.4)
p.dot(Av2, PRACTICE, 4.4)
p.dot(Mi, THEORY, 4.0)
p.dot((0, 0), TEXT)
p.label(*Mi, "M", (("c", p.X(Mi[0]) + 8, p.Y(Mi[1]) + 26),), size=NAME, color=THEORY)
ring(p, (0, 0), "O", first=210)
axis_names(p)
nn()
lab(p, Av1, "A_1", ("sw", "w", "s", "ne"))
lab(p, Av2, "A_2", ("ne", "e", "n", "sw"))
stack(p, [("3x² − 10xy + 3y² + x − 32 = 0", PRACTICE)], around(-2.2, 5.4, 1.2, 0.4),
      anchor=RI(bx * math.sinh(0.8), ay * math.cosh(0.8)))
numbers(p, xs, ys)
f.out("exr-cins-i",
      C("$d$ = 16 > 0, $D$ = 2045/4 > 0: konik, asal ekseni $Y''$-ekseni olan bir hiperboldür."),
      aria="Hyperbola 3x2 - 10xy + 3y2 + x - 32 = 0, centre M near the origin, axes turned by pi over 4")


# ============================================================ exr-cins-ii
TH = math.atan2(2, 3)
RT = frame(TH)
a2, b2 = math.sqrt(168 / 13), math.sqrt(21 / 13)
f, p = equal_fig((-4.4, 4.4), (-3.0, 3.0), 62, (40, 30, 45, 30))
xs, ys = axes(p)
nn = turned_axes(p, RT, (-5.0, 5.0), (-3.3, 3.3), th=TH, xprefs=("e", "ne", "se"), yprefs=("n", "nw", "ne"))
E2 = ellipse_pts(RT, a2, b2)
p.line(E2, PRACTICE, 2.6)
ang(p, (0, 0), 0, TH, 1.25, "", TEXT, head=True)
for q in (RT(a2, 0), RT(-a2, 0), RT(0, b2), RT(0, -b2)):
    p.dot(q, PRACTICE, 4.2)
origin_auto(p, first=300)
axis_names(p)
nn()
stack(p, [("θ = arctan(2/3)", TEXT)], around(3.4, -0.85, 0.5, 0.3), anchor=pol(1.25, TH * 0.3))
lab(p, RT(a2, 0), "√(168/13)", ("se", "e", "s"), size=NOTE, color=PRACTICE)
lab(p, RT(0, b2), "√(21/13)", ("nw", "w", "n", "ne"), size=NOTE, color=PRACTICE)
stack(p, [("41x² − 84xy + 76y² = 168", PRACTICE)], around(-2.2, -2.6, 1.0, 0.3), anchor=E2[215])
numbers(p, xs, ys)
f.out("exr-cins-ii",
      C("Eksenler arctan(2/3) döndürülünce elipsin denklemi $13x'² + 104y'² = 168$ olur."),
      aria="Ellipse 41x2 - 84xy + 76y2 = 168 in axes turned by arctan 2/3")


# ============================================================ exr-cins-iii
TH = math.atan2(3, 4)
RT = frame(TH)
f, p = equal_fig((-3.4, 4.2), (-4.1, 2.0), 70, (40, 30, 45, 30))
xs, ys = axes(p, yl_pos=("e", "ne", "nw"))
nn = turned_axes(p, RT, (-3.6, 4.2), (-4.4, 2.2), th=TH, xprefs=("e", "ne", "se"), yprefs=("n", "nw", "w"))
draw(p, [RT(t, -t * t / 2) for t in samp(-2.5, 2.6, 400)], PRACTICE, 2.6)
ang(p, (0, 0), 0, TH, 1.3, "θ = arctan(3/4)", TEXT, head=True, size=NOTE, fs=(0.1, 0, 0.25))
Q1, Q2 = (2.8, -0.4), (-0.4, -2.8)
p.dot(Q1, PRACTICE, 4.4)
p.dot(Q2, PRACTICE, 4.4)
origin_auto(p, first=110)
axis_names(p)
nn()
lab(p, Q1, "(2,8; −0,4)", ("e", "se", "ne", "s"), size=NOTE)
lab(p, Q2, "(−0,4; −2,8)", ("w", "sw", "nw", "s"), size=NOTE)
stack(p, [("x'² = −2y'", PRACTICE)], around(*RT(0.9, -2.3), 0.6, 0.6))
numbers(p, xs, ys)
f.out("exr-cins-iii",
      C("Eksenler arctan(3/4) döndürülünce $16x² + 24xy + 9y² − 30x + 40y = 0$ parabolü $x'² = −2y'$ olur."),
      aria="Parabola x prime squared = -2 y prime in axes turned by arctan 3/4")


# ============================================================ exr-parametreli
f, p = equal_fig((-3.5, 3.5), (-4.5, 4.5), 66, (40, 30, 45, 30))
xs, ys = axes(p)
for s in (1, -1):
    draw(p, [(-1 / y - 0.75 * y, y) for y in (s * v for v in samp(0.2, 4.6, 600))], PRACTICE, 2.5)
for c in (2, -2):
    full_line(p, (0, c), (1, -2), THEORY, 2.4)
# 5x^2 + 6xy + 2y^2 = (2x + y)^2 + (x + y)^2 = 4: 2x + y = 2cos t, x + y = 2 sin t
E5 = [(2 * math.cos(t) - 2 * math.sin(t), -2 * math.cos(t) + 4 * math.sin(t)) for t in samp(0, 2 * PI, 400)]
p.line(E5, BASE, 2.5)
origin(p, ("sw", "se", "nw"))
axis_names(p)
lab(p, (-1 / 0.6 - 0.45, 0.6), "m = 0", ("nw", "w", "n", "sw"), color=PRACTICE, size=NOTE)
lab(p, (0.6, 0.8), "m = 4", ("ne", "e", "n"), color=THEORY, size=NOTE)
stack(p, [("m = 5", BASE)], around(-0.55, 0.75, 0.2, 0.2))
numbers(p, xs, ys)
f.out("exr-parametreli",
      C("$mx² + 2(m − 2)xy + (m − 3)y² − 4 = 0$ ailesi: $m$ < 4 için hiperbol, $m$ = 4 için paralel iki doğru, "
        "$m$ > 4 için elips."),
      aria="Three members of the family: hyperbola for m = 0, parallel lines for m = 4, ellipse for m = 5")


# ============================================================ exr-merkez-hiperbol
Mh = (-1.0, -1.0)
lam1, lam2 = 0.5 + math.sqrt(10.25), 0.5 - math.sqrt(10.25)
ev = (1.0, (3 - lam1) / 2)
th_h = math.atan2(ev[1], ev[0])
RH = frame(th_h, Mh)
ah, bh = 2 / math.sqrt(lam1), 2 / math.sqrt(-lam2)
f, p = equal_fig((-6.0, 4.0), (-6.0, 4.0), 55, (40, 30, 45, 30))
xs, ys = axes(p, step=2)
p.arrow((-5.9, -1), (4.0, -1), THEORY, 1.6, 8.5)
p.arrow((-1, -5.9), (-1, 4.0), THEORY, 1.6, 8.5)
for s in (1, -1):
    draw(p, hyp_pts(RH, ah, bh, s, 3.2), PRACTICE, 2.6)
p.dot(Mh, THEORY, 4.6)
origin(p, ("ne", "se", "nw"))
axis_names(p)
lab(p, (4.0, -1), "X'", ("ne", "se", "n"), color=THEORY, size=AXIS, halo=False, gap=8)
lab(p, (-1, 4.0), "Y'", ("nw", "ne", "w"), color=THEORY, size=AXIS, halo=False, gap=8)
stack(p, [("M(−1, −1)", TEXT)], around(-1.8, -1.8, 0.4, 0.4), anchor=Mh)
stack(p, [("3x'² − 4x'y' − 2y'² = 4", PRACTICE)], around(-3.4, 3.2, 1.2, 0.6))
numbers(p, xs, ys)
f.out("exr-merkez-hiperbol",
      C("Hiperbolün merkezi $M(−1, −1)$; eksenler $M$'ye ötelenince birinci dereceden terimler kaybolur."),
      aria="Hyperbola 3x2 - 4xy - 2y2 + 2x - 8y - 7 = 0 with centre M(-1, -1) and translated axes")


# ============================================================ exr-merkez-oteleme
Mo = (-1.0, 3.0)
lo_ = 3.5 - math.sqrt(11.25)
hi_ = 3.5 + math.sqrt(11.25)
th_o = math.atan2((2 - lo_) / 3, 1.0)
RO = frame(th_o, Mo)
ao, bo = math.sqrt(54 / lo_), math.sqrt(54 / hi_)
f, p = equal_fig((-18.5, 16.5), (-8.5, 14.5), 19, (40, 30, 45, 30))
xs, ys = axes(p, step=5)
p.arrow((-18.4, 3), (16.5, 3), THEORY, 1.6, 8.5)
p.arrow((-1, -8.4), (-1, 14.5), THEORY, 1.6, 8.5)
E6 = ellipse_pts(RO, ao, bo, 600)
p.line(E6, PRACTICE, 2.6)
p.dot(Mo, THEORY, 4.6)
origin(p, ("se", "sw", "s"))
axis_names(p)
lab(p, (16.5, 3), "X'", ("ne", "se", "n"), color=THEORY, size=AXIS, halo=False, gap=8)
lab(p, (-1, 14.5), "Y'", ("ne", "nw", "e"), color=THEORY, size=AXIS, halo=False, gap=8)
stack(p, [("M(−1, 3)", TEXT)], around(2.6, 5.0, 0.8, 0.5), anchor=Mo)
stack(p, [("2x'² − 6x'y' + 5y'² = 54", PRACTICE)], around(10.5, 1.5, 1.0, 0.4),
      anchor=min(E6, key=lambda q: math.dist(q, (5.5, 1.5))))
numbers(p, xs, ys)
f.out("exr-merkez-oteleme",
      C("Elipsin merkezi $M(−1, 3)$; eksenler $M$'ye ötelenince birinci dereceden terimler kaybolur."),
      aria="Long thin ellipse 2x2 - 6xy + 5y2 + 22x - 36y + 11 = 0 with centre M(-1, 3) and translated axes",
      css=WIDE)


# ============================================================ exr-merkez-dogrusu
Od = (0.0, -3.0)
f, p = equal_fig((-3.0, 9.0), (-8.0, 4.0), 46, (40, 30, 45, 30))
xs, ys = axes(p, step=2)
g1 = full_line(p, (3 + 2 * S3, 0), (1, 1), PRACTICE, 2.4)
g2 = full_line(p, (3 - 2 * S3, 0), (1, 1), PRACTICE, 2.4)
gm = full_line(p, (3, 0), (1, 1), THEORY, 1.4, "6 4", 0.9)
p.arrow((-2.2, -3), (2.2, -3), BASE, 1.9, 8.5)
p.arrow((0, -5.2), (0, -0.9), BASE, 1.9, 8.5, weight=1.0)
p.dot(Od, BASE, 4.6)
origin(p, ("nw", "sw", "ne"))
axis_names(p)
lab(p, (2.2, -3), "X'", ("se", "ne", "s"), color=BASE, size=AXIS, halo=False, gap=8)
lab(p, (0, -0.9), "Y'", ("w", "e", "nw"), color=BASE, size=AXIS, halo=False, gap=8)
ring(p, Od, "O'(0, −3)", size=NOTE, first=200, halo=True)
p.along(*sorted(g1), "x − y = 3 + 2√3", -1, t=0.85, size=NOTE, color=PRACTICE, halo=True)
p.along(*sorted(g2), "x − y = 3 − 2√3", 1, t=0.85, size=NOTE, color=PRACTICE, halo=True)
stack(p, [("merkezler:", THEORY), ("x − y = 3", THEORY)], around(3.7, -0.7, 0.2, 0.15))
numbers(p, xs, ys)
f.out("exr-merkez-dogrusu",
      C("$d$ = $D$ = 0: konik paralel iki doğrudur ve $(t, t − 3)$ biçimindeki her nokta bir merkezdir."),
      aria="Parallel lines x - y = 3 +- 2 sqrt 3 with the line of centres x - y = 3 and O prime(0, -3)")


# ============================================================ exr-paralel-dogrular
f, p = equal_fig((-5.0, 3.0), (-2.5, 5.5), 64, (40, 30, 45, 30))
xs, ys = axes(p)
h1 = full_line(p, (-3, 0), (1, 1), PRACTICE, 2.4)
h2 = full_line(p, (-0.5, 0), (1, 1), PRACTICE, 2.4)
hm = (-4.25 + 0.04, -2.5 + 0.04), (1.45, 3.2)
p.seg(*hm, THEORY, 1.4, "6 4", 0.9)
origin(p, ("se", "s", "e"))
axis_names(p)
p.along(*sorted(h1), "x − y + 3 = 0", 1, t=0.8, size=NOTE, color=PRACTICE, halo=True)
p.along(*sorted(h2), "2x − 2y + 1 = 0", -1, t=0.84, size=NOTE, color=PRACTICE, halo=True)
lab(p, hm[1], "x − y = −7/4", ("n", "ne", "nw"), color=THEORY, size=NOTE, gap=6)
numbers(p, xs, ys)
f.out("exr-paralel-dogrular",
      C("$d$ = $D$ = 0 ve $a'_{33}$ = −25/8 < 0: denklem paralel iki doğrudur."),
      aria="Parallel lines x - y + 3 = 0 and 2x - 2y + 1 = 0 with the line of centres x - y = -7/4")


# ---------------------------------------------------------------------------
for name, content in OUT.items():
    with io.open(OUT_DIR / f"{PREFIX}{name}.md", "w", encoding="utf-8", newline="\n") as fh:
        fh.write(content)
print(f"generated {len(OUT)} figures:", ", ".join(OUT))
