# -*- coding: utf-8 -*-
"""
Figures for the "Elips" chapter of Analitik Geometri
(dersler/analitik-geometri/elips.qmd).

The figures are NOT produced at build time. Run

    python scripts/analytic_figures/elp.py
    python scripts/center_figures.py "analytic-elp-*.md" --keep-width

and paste each scripts/_figures/analytic-elp-<name>.md block in place of its
placeholder. Figures go INSIDE the box they explain (theorem, proof, example,
solution or exercise), never inside a definition box: a figure that
illustrates a definition sits directly below that box.

Every 2-D panel has the same number of pixels per unit on both axes, so
ellipses, circles and right angles look true. Labels are placed by direction
(an angle and a gap); lab_auto() tries a list of directions and takes the
first one whose box touches no drawn line, point or other label. audit()
reports whatever still collides, and tick numbers that would collide are
left out. The three cone figures use an orthographic camera (svg_plot3);
the parts of the cone and of the conic that face away from the viewer are
dashed.

Captions are Turkish (they are shown on the site); aria labels are ASCII.
"""
import io
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, WIDE, TEXT, BG, THEORY, PRACTICE, BASE, REMARK, fmt  # noqa: E402
from svg_plot3 import Camera, vadd, vsub, vscale, vdot, vcross, vunit  # noqa: E402
from check_figure_labels import text_width  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
OUT = {}

MINUS = "−"
SQRT = "√"
NAME, DESC, TICK = 14, 13, 11

LETTERS = "A-Za-zθ"
TOKEN = re.compile(r"&#?\w+;|_([A-Za-z0-9])|[%s]+|[^%s_&]+" % (LETTERS, LETTERS))

# Fraktur D (U+1D507) outline in em units, baseline at y = 0, y pointing down
# (the fonts have no glyph for it; same outline as in dzu.py).
FRAK_D = ("M.9 -.467Q.9 -.331 .837 -.168Q.656 .031 .584 .031Q.557 .031 .456 -.009Q.397 -.032 .323 -.055"
          "Q.259 -.073 .226 -.073Q.194 -.073 .162 -.048Q.133 -.028 .104 .018L.086 0Q.127 -.083 .208 -.152"
          "Q.285 -.152 .336 -.184Q.39 -.216 .39 -.261Q.39 -.302 .354 -.345Q.292 -.422 .292 -.442"
          "Q.292 -.477 .302 -.495Q.318 -.523 .347 -.552Q.393 -.598 .469 -.637L.487 -.625Q.463 -.609 .444 -.588"
          "Q.419 -.563 .404 -.54Q.39 -.518 .39 -.504Q.39 -.489 .438 -.418Q.493 -.341 .493 -.316"
          "Q.493 -.273 .45 -.228Q.41 -.186 .324 -.149Q.385 -.137 .477 -.104Q.606 -.055 .633 -.055"
          "Q.68 -.055 .699 -.068Q.722 -.084 .766 -.152Q.789 -.185 .802 -.243Q.814 -.299 .814 -.37"
          "Q.814 -.517 .735 -.595Q.632 -.698 .444 -.698Q.267 -.698 .18 -.611Q.109 -.54 .104 -.418"
          "L.08 -.431Q.08 -.58 .177 -.676Q.232 -.731 .301 -.754Q.404 -.787 .474 -.787Q.596 -.787 .678 -.764"
          "Q.748 -.744 .82 -.674Q.9 -.594 .9 -.467Z")
FRAK_ADV = 0.98


def mk(s, size):
    """Label markup: latin letters italic, '_d' a subscript."""
    out = []
    for m in TOKEN.finditer(s):
        t = m.group(0)
        if t.startswith("&"):
            out.append(t)
        elif m.group(1):
            small = max(11, round(0.72 * size, 1))
            down = round(0.3 * size, 1)
            out.append(f'<tspan font-size="{small}" dy="{down}" font-style="italic">{m.group(1)}</tspan>'
                       f'<tspan dy="-{down}">&#8203;</tspan>')
        elif re.match("[%s]" % LETTERS, t):
            out.append(f'<tspan font-style="italic">{t}</tspan>')
        else:
            out.append(t)
    return "".join(out)


def unit(v):
    n = math.hypot(v[0], v[1]) or 1.0
    return (v[0] / n, v[1] / n)


def seg_hits_box(x1, y1, x2, y2, box, m):
    """Liang-Barsky: does the segment meet the box grown by m pixels?"""
    bx0, by0, bx1, by1 = box[0] - m, box[1] - m, box[2] + m, box[3] + m
    dx, dy = x2 - x1, y2 - y1
    t0, t1 = 0.0, 1.0
    for p, q in ((-dx, x1 - bx0), (dx, bx1 - x1), (-dy, y1 - by0), (dy, by1 - y1)):
        if p == 0:
            if q < 0:
                return False
        else:
            r = q / p
            if p < 0:
                t0 = max(t0, r)
            else:
                t1 = min(t1, r)
            if t0 > t1:
                return False
    return True


def dot_near(box, dot, m):
    cx, cy, r = dot
    dx = max(box[0] - cx, 0, cx - box[2])
    dy = max(box[1] - cy, 0, cy - box[3])
    return math.hypot(dx, dy) < r + m


def boxes_meet(a, b, m=0.0):
    return not (a[2] + m <= b[0] or b[2] + m <= a[0] or a[3] + m <= b[1] or b[3] + m <= a[1])


def pol(r, deg, c=(0.0, 0.0)):
    return (c[0] + r * math.cos(math.radians(deg)), c[1] + r * math.sin(math.radians(deg)))


def mid(a, b):
    return ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)


def angle_of(v):
    return math.degrees(math.atan2(v[1], v[0]))


def ell_pt(t_deg, a, b, c=(0.0, 0.0), rot=0.0):
    """Point of the ellipse with semi-axes a, b (a along the rotated x axis) at parameter t."""
    t, r = math.radians(t_deg), math.radians(rot)
    u, v = a * math.cos(t), b * math.sin(t)
    return (c[0] + u * math.cos(r) - v * math.sin(r), c[1] + u * math.sin(r) + v * math.cos(r))


def ell_normal(t_deg, a, b, rot=0.0):
    """Outward normal direction (degrees) of the ellipse at parameter t."""
    t = math.radians(t_deg)
    return angle_of((math.cos(t) / a, math.sin(t) / b)) + rot


class Fig(Plot):
    """Equal-aspect panel that remembers what it drew, for label placement and audit."""

    def __init__(self, xr, yr, width, x0=50, y0=40):
        ppu = width / (xr[1] - xr[0])
        super().__init__(x0, y0, width, (yr[1] - yr[0]) * ppu, xr, yr)
        self.ppu = ppu
        self.segs = []
        self.boxes = []
        self.dots = []
        self.bounds = (x0 - 44, y0 - 34, x0 + width + 44, y0 + self.h + 34)

    # -- registry ------------------------------------------------------------
    def reg(self, pts_px, name):
        for (a, b), (c, d) in zip(pts_px, pts_px[1:]):
            self.segs.append((a, b, c, d, name))

    def reg_data(self, pts, name):
        self.reg([(self.X(x), self.Y(y)) for x, y in pts], name)

    # -- marks ---------------------------------------------------------------
    def seg(self, a, b, color=TEXT, width=1.8, dash=None, opacity=1.0, name="segment"):
        self.line([a, b], color, width, dash, opacity)
        self.reg_data([a, b], name)

    def poly(self, pts, color=THEORY, width=2.4, dash=None, opacity=1.0, name="curve"):
        self.line(pts, color, width, dash, opacity)
        self.reg_data(pts, name)

    def ell(self, c, a, b, rot=0.0, color=THEORY, width=2.4, dash=None, name="ellipse", t0=0.0, t1=360.0):
        n = max(48, int(abs(t1 - t0) / 1.5))
        pts = [ell_pt(t0 + (t1 - t0) * k / n, a, b, c, rot) for k in range(n + 1)]
        self.poly(pts, color, width, dash, 1.0, name)

    def circ(self, c, r, color=THEORY, width=2.2, dash=None, name="circle"):
        self.ell(c, r, r, 0.0, color, width, dash, name)

    def dot(self, pt, color=TEXT, r=4.2):
        self.points([pt], color, r)
        self.dots.append((self.X(pt[0]), self.Y(pt[1]), r))

    def right_angle(self, v, d1, d2, s=10.0, color=TEXT, width=1.3):
        X, Y = self.X(v[0]), self.Y(v[1])
        u = unit((d1[0], -d1[1]))
        w = unit((d2[0], -d2[1]))
        pts = [(X + s * u[0], Y + s * u[1]), (X + s * (u[0] + w[0]), Y + s * (u[1] + w[1])),
               (X + s * w[0], Y + s * w[1])]
        d = "M" + " L".join(f"{a:.1f},{b:.1f}" for a, b in pts)
        self.add(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}" opacity="0.85"/>')
        self.reg(pts, "right angle")

    def angle_arc(self, v, a0, a1, r_px, color=TEXT, width=1.4, name="angle arc"):
        r = r_px / self.ppu
        n = 40
        pts = [pol(r, a0 + (a1 - a0) * k / n, v) for k in range(n + 1)]
        self.poly(pts, color, width, None, 1.0, name)

    def arrow_px(self, x0, y0, x1, y1, color=TEXT, width=1.3, head=8.0, opacity=1.0):
        dx, dy = x1 - x0, y1 - y0
        L = math.hypot(dx, dy) or 1.0
        ux, uy = dx / L, dy / L
        sx, sy = x1 - ux * head * 0.8, y1 - uy * head * 0.8
        self.add(f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{sx:.1f}" y2="{sy:.1f}" stroke="{color}" '
                 f'stroke-width="{width}" opacity="{opacity}" stroke-linecap="round"/>')
        px, py, hw = -uy, ux, head * 0.42
        self.add(f'<polygon points="{x1:.1f},{y1:.1f} {x1 - ux * head + px * hw:.1f},{y1 - uy * head + py * hw:.1f} '
                 f'{x1 - ux * head - px * hw:.1f},{y1 - uy * head - py * hw:.1f}" fill="{color}" opacity="{opacity}"/>')

    def dim(self, a, b, color=TEXT, width=1.2, name="dimension"):
        """Two-headed measuring arrow between data points a and b."""
        m = mid(a, b)
        X0, Y0, X1, Y1, XM, YM = self.X(a[0]), self.Y(a[1]), self.X(b[0]), self.Y(b[1]), self.X(m[0]), self.Y(m[1])
        self.arrow_px(XM, YM, X0, Y0, color, width, 8.0)
        self.arrow_px(XM, YM, X1, Y1, color, width, 8.0)
        self.reg([(X0, Y0), (X1, Y1)], name)

    def clip(self, a, b):
        """Clip the segment ab (data) to the panel rectangle."""
        x0, y0 = a
        dx, dy = b[0] - a[0], b[1] - a[1]
        t0, t1 = 0.0, 1.0
        for p, q in ((-dx, x0 - self.xmin), (dx, self.xmax - x0), (-dy, y0 - self.ymin), (dy, self.ymax - y0)):
            if p == 0:
                if q < 0:
                    return None
            else:
                r = q / p
                if p < 0:
                    t0 = max(t0, r)
                else:
                    t1 = min(t1, r)
        if t0 > t1:
            return None
        return (x0 + t0 * dx, y0 + t0 * dy), (x0 + t1 * dx, y0 + t1 * dy)

    def line_clipped(self, a, b, color=TEXT, width=2.0, dash=None, name="line"):
        ab = self.clip(a, b)
        self.seg(ab[0], ab[1], color, width, dash, 1.0, name)
        return ab

    # -- labels --------------------------------------------------------------
    def _box(self, x, y, markup, size, anchor):
        w = text_width(markup, size)
        x0 = x - w / 2 if anchor == "middle" else x - w if anchor == "end" else x
        return (x0, y - 0.78 * size, x0 + w, y + 0.22 * size)

    def lab_px(self, x, y, s, size=NAME, color=TEXT, anchor="start", bold=False, raw=False):
        markup = s if raw else mk(s, size)
        weight = ' font-weight="600"' if bold else ""
        self.add(f'<text x="{x:.1f}" y="{y:.1f}" fill="{color}" font-size="{size}" '
                 f'text-anchor="{anchor}"{weight}>{markup}</text>')
        box = self._box(x, y, markup, size, anchor)
        self.boxes.append((box, s))
        return box

    def _place(self, pt, s, ang, dist, size, raw):
        markup = s if raw else mk(s, size)
        w, h = text_width(markup, size), size
        c, sn = math.cos(math.radians(ang)), math.sin(math.radians(ang))
        ext = w / 2 * abs(c) + h / 2 * abs(sn)
        cx = self.X(pt[0]) + (dist + ext) * c
        cy = self.Y(pt[1]) - (dist + ext) * sn
        return cx, cy + 0.28 * size, self._box(cx, cy + 0.28 * size, markup, size, "middle")

    def lab(self, pt, s, ang, dist=7.0, size=NAME, color=TEXT, raw=False):
        """Label s beside data point pt in direction ang (degrees, y up), its box dist px away."""
        x, y, _ = self._place(pt, s, ang, dist, size, raw)
        return self.lab_px(x, y, s, size, color, "middle", raw=raw)

    def cost(self, box, ignore=()):
        c = 0
        for a, b, cc, d, n in self.segs:
            if n not in ignore and seg_hits_box(a, b, cc, d, box, 2.0):
                c += 1
        c += sum(3 for b, _ in self.boxes if boxes_meet(box, b, 2.0))
        c += sum(3 for d in self.dots if dot_near(box, d, 2.0))
        B = self.bounds
        if box[0] < B[0] or box[1] < B[1] or box[2] > B[2] or box[3] > B[3]:
            c += 5
        return c

    def lab_auto(self, pt, s, prefs=(45, 135, -45, -135, 90, -90, 0, 180), dist=7.0, size=NAME,
                 color=TEXT, raw=False, grow=(0, 5, 11)):
        best = None
        for g in grow:
            for ang in prefs:
                x, y, box = self._place(pt, s, ang, dist + g, size, raw)
                c = self.cost(box)
                if c == 0:
                    return self.lab_px(x, y, s, size, color, "middle", raw=raw)
                if best is None or c < best[0]:
                    best = (c, x, y)
        return self.lab_px(best[1], best[2], s, size, color, "middle", raw=raw)

    def lab_seg(self, a, b, s, side=1, dist=5.0, t=0.5, size=NAME, color=TEXT):
        """Label beside segment ab at parameter t, on the left (side=1) or right (side=-1) of a->b."""
        pt = (a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1]))
        return self.lab(pt, s, angle_of((b[0] - a[0], b[1] - a[1])) + 90 * side, dist, size, color)

    def lab_line(self, a, b, s, ts=(0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1), dist=6.0, size=NAME,
                 color=TEXT, sides=(1, -1)):
        """Label beside segment ab: the first (t, side) whose box touches nothing."""
        best = None
        for t in ts:
            for side in sides:
                pt = (a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1]))
                ang = angle_of((b[0] - a[0], b[1] - a[1])) + 90 * side
                x, y, box = self._place(pt, s, ang, dist, size, False)
                c = self.cost(box)
                if c == 0:
                    return self.lab_px(x, y, s, size, color, "middle")
                if best is None or c < best[0]:
                    best = (c, x, y)
        return self.lab_px(best[1], best[2], s, size, color, "middle")

    def lab_out(self, a, b, s, ref, dist=5.0, t=0.5, size=NAME, color=TEXT):
        """Label beside segment ab at parameter t, on the side away from the data point ref."""
        pt = (a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1]))
        n = (-(b[1] - a[1]), b[0] - a[0])
        if n[0] * (ref[0] - pt[0]) + n[1] * (ref[1] - pt[1]) > 0:
            n = (-n[0], -n[1])
        return self.lab(pt, s, angle_of(n), dist, size, color)

    def leader(self, box, target, color=TEXT):
        """Thin line from the edge of a label box to a data point."""
        tx, ty = self.X(target[0]), self.Y(target[1])
        cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
        # exit point of the ray from the box centre toward the target, 3 px outside the box
        dx, dy = tx - cx, ty - cy
        hw, hh = (box[2] - box[0]) / 2 + 3, (box[3] - box[1]) / 2 + 3
        k = min(hw / abs(dx) if dx else 1e9, hh / abs(dy) if dy else 1e9)
        sx, sy = cx + k * dx, cy + k * dy
        self.add(f'<line x1="{sx:.1f}" y1="{sy:.1f}" x2="{tx:.1f}" y2="{ty:.1f}" stroke="{color}" '
                 f'stroke-width="0.9" opacity="0.7"/>')
        self.reg([(sx, sy), (tx, ty)], "leader")

    def frak(self, pt, tail="", ang=0, dist=7.0, size=15, color=TEXT):
        """The fraktur plane name D (an outline path) beside a data point."""
        gw = FRAK_ADV * size
        w = gw + (text_width(tail, size) if tail else 0.0)
        c, sn = math.cos(math.radians(ang)), math.sin(math.radians(ang))
        ext = w / 2 * abs(c) + size / 2 * abs(sn)
        cx = self.X(pt[0]) + (dist + ext) * c
        cy = self.Y(pt[1]) - (dist + ext) * sn
        x0, base = cx - w / 2, cy + 0.30 * size
        self.add(f'<path d="{FRAK_D}" transform="translate({x0:.1f} {base:.1f}) scale({size:.2f})" '
                 f'fill="{color}"/>')
        self.boxes.append(((x0, cy - size / 2, x0 + w, cy + size / 2), "D"))

    # -- axes ----------------------------------------------------------------
    def axes2(self, xr, yr, origin=True, ticks=1.0, xname="X", yname="Y"):
        ox, oy = self.X(0), self.Y(0)
        xa, xb = self.X(xr[0]), self.X(xr[1]) + 12
        ya, yb = self.Y(yr[0]), self.Y(yr[1]) - 12
        a = [f'<g stroke="{TEXT}" stroke-width="1.1" opacity="0.55" fill="{TEXT}">',
             f'<line x1="{xa:.1f}" y1="{oy:.1f}" x2="{xb - 6:.1f}" y2="{oy:.1f}"/>',
             f'<line x1="{ox:.1f}" y1="{ya:.1f}" x2="{ox:.1f}" y2="{yb + 6:.1f}"/>',
             f'<polygon points="{xb:.1f},{oy:.1f} {xb - 9:.1f},{oy - 3.8:.1f} {xb - 9:.1f},{oy + 3.8:.1f}" stroke="none"/>',
             f'<polygon points="{ox:.1f},{yb:.1f} {ox - 3.8:.1f},{yb + 9:.1f} {ox + 3.8:.1f},{yb + 9:.1f}" stroke="none"/>']
        if ticks:
            k0, k1 = math.ceil(xr[0] / ticks), math.floor(xr[1] / ticks)
            for k in range(k0, k1 + 1):
                t = k * ticks
                if k:
                    a.append(f'<line x1="{self.X(t):.1f}" y1="{oy - 3:.1f}" x2="{self.X(t):.1f}" y2="{oy + 3:.1f}"/>')
            k0, k1 = math.ceil(yr[0] / ticks), math.floor(yr[1] / ticks)
            for k in range(k0, k1 + 1):
                t = k * ticks
                if k:
                    a.append(f'<line x1="{ox - 3:.1f}" y1="{self.Y(t):.1f}" x2="{ox + 3:.1f}" y2="{self.Y(t):.1f}"/>')
        a.append('</g>')
        self.add("\n  ".join(a))
        self.reg([(xa, oy), (xb, oy)], "x axis")
        self.reg([(ox, ya), (ox, yb)], "y axis")
        self.lab_px(xb + 5, oy + 5, xname, NAME, TEXT, "start")
        self.lab_px(ox + 8, yb + 6, yname, NAME, TEXT, "start")
        if origin:
            self.lab_px(ox - 6, oy + 16, "O", 13, TEXT, "end")

    def tick_mark(self, pt, axis):
        X, Y = self.X(pt[0]), self.Y(pt[1])
        if axis == "x":
            self.add(f'<line x1="{X:.1f}" y1="{Y - 4:.1f}" x2="{X:.1f}" y2="{Y + 4:.1f}" stroke="{TEXT}" '
                     f'stroke-width="1.2" opacity="0.7"/>')
        else:
            self.add(f'<line x1="{X - 4:.1f}" y1="{Y:.1f}" x2="{X + 4:.1f}" y2="{Y:.1f}" stroke="{TEXT}" '
                     f'stroke-width="1.2" opacity="0.7"/>')

    def numbers(self, xs=(), ys=()):
        """Tick numbers, drawn last; any that would touch a line or a label is dropped."""
        ox, oy = self.X(0), self.Y(0)
        dropped = []
        for axis, vals in (("x", xs), ("y", ys)):
            for t in vals:
                s = fmt(t).replace("-", MINUS)
                if axis == "x":
                    x, y, anchor = self.X(t), oy + 17, "middle"
                else:
                    x, y, anchor = ox - 7, self.Y(t) + 4, "end"
                box = self._box(x, y, s, TICK, anchor)
                own = "x axis" if axis == "x" else "y axis"
                hit = any(seg_hits_box(a, b, c, d, box, 2.5) for a, b, c, d, n in self.segs if n != own)
                hit = hit or any(boxes_meet(box, b, 2.0) for b, _ in self.boxes)
                hit = hit or any(dot_near(box, d, 2.0) for d in self.dots)
                if hit:
                    dropped.append(f"{axis}={s}")
                    continue
                self.add(f'<text x="{x:.1f}" y="{y:.1f}" fill="{TEXT}" font-size="{TICK}" '
                         f'text-anchor="{anchor}" opacity="0.72">{s}</text>')
                self.boxes.append((box, s))
        return dropped

    def int_numbers(self, step=1, skip=()):
        xs = [k * step for k in range(math.ceil(self.xmin / step), math.floor(self.xmax / step) + 1)
              if k and k * step not in skip]
        ys = [k * step for k in range(math.ceil(self.ymin / step), math.floor(self.ymax / step) + 1)
              if k and k * step not in skip]
        return self.numbers(xs, ys)

    # -- audit ---------------------------------------------------------------
    def audit(self, name, dropped=()):
        msgs = []
        for i, (b, s) in enumerate(self.boxes):
            for a, bb, c, d, n in self.segs:
                if seg_hits_box(a, bb, c, d, b, 1.5):
                    msgs.append(f"'{s}' touches {n}")
                    break
            for b2, s2 in self.boxes[i + 1:]:
                if boxes_meet(b, b2, 1.0):
                    msgs.append(f"'{s}' meets '{s2}'")
            for dd in self.dots:
                if dot_near(b, dd, 1.5):
                    msgs.append(f"'{s}' touches a point")
                    break
        if dropped:
            msgs.append("dropped tick numbers: " + ", ".join(dropped))
        for m in msgs:
            print(f"  [{name}] {m}")


def canvas(p, extra_bottom=0):
    return int(p.x0 * 2 + p.w), int(p.y0 * 2 + p.h + extra_bottom)


def em(s):
    return f"<em>{s}</em>"


def emit(name, p, caption, aria, css="ders-grafik", dropped=(), extra_bottom=0):
    p.audit(name, dropped)
    W, H = canvas(p, extra_bottom)
    OUT[name] = figure(W, H, [p], caption, css, aria)


def emit_multi(name, panels, W, H, caption, aria, css=WIDE):
    for k, p in enumerate(panels):
        p.audit(f"{name}#{k}")
    OUT[name] = figure(W, H, panels, caption, css, aria)


def sub_i(s):
    return f"{em(s[0])}<sub>{s[1:]}</sub>"


F1, F2, A1, A2, B1, B2 = sub_i("F1"), sub_i("F2"), sub_i("A1"), sub_i("A2"), sub_i("B1"), sub_i("B2")
X2, Y2 = f"{em('x')}<sup>2</sup>", f"{em('y')}<sup>2</sup>"


def foci_pts(a, b, c0=(0.0, 0.0), rot=0.0, vertical=False):
    c = math.sqrt(a * a - b * b)
    if vertical:
        return (c0[0], c0[1] + c), (c0[0], c0[1] - c)
    return pol(c, rot, c0), pol(c, rot + 180, c0)


# ============================================================ elips-tanimi
p = Fig((-0.5, 8.5), (-0.5, 6.5), 560)
p.axes2((-0.5, 8.5), (-0.5, 6.5), ticks=0)
p.right_angle((0, 0), (1, 0), (0, 1), 9)
M, a, b, rot = (4.0, 3.0), 3.0, 2.0, 20.0
c = math.sqrt(5)
f1, f2 = pol(c, rot, M), pol(c, rot + 180, M)
a1, a2 = pol(a, rot, M), pol(a, rot + 180, M)
b1, b2 = pol(b, rot + 90, M), pol(b, rot - 90, M)
P = ell_pt(70, a, b, M, rot)
p.seg(a2, a1, TEXT, 1.2, None, 0.8, "major axis")
p.seg(b2, b1, TEXT, 1.2, None, 0.8, "minor axis")
p.right_angle(M, pol(1, rot), pol(1, rot + 90), 9)
p.ell(M, a, b, rot)
p.seg(P, f1, PRACTICE, 2.0, name="PF1")
p.seg(P, f2, BASE, 2.0, name="PF2")
for q in (a1, a2, b1, b2, M):
    p.dot(q, TEXT, 3.8)
p.dot(f1, PRACTICE)
p.dot(f2, PRACTICE)
p.dot(P)
p.lab_out(P, f1, "|PF_1|", M, 6, 0.5, NAME, PRACTICE)
p.lab_out(P, f2, "|PF_2|", M, 6, 0.5, NAME, BASE)
p.lab_auto(P, "P(x, y)", (ell_normal(70, a, b, rot), 90, 60, 120))
p.lab_auto(f1, "F_1", (-110, -90, -70, -130))
p.lab_auto(f2, "F_2", (-110, -90, -70, -130))
p.lab_auto(a1, "A_1", (rot, rot + 30, rot - 30))
p.lab_auto(a2, "A_2", (rot + 180, rot + 150, rot + 210))
p.lab_auto(b1, "B_1", (rot + 90, rot + 60, rot + 120))
p.lab_auto(b2, "B_2", (rot - 90, rot - 60, rot - 120))
p.lab_auto(M, "M", (-70, -110, -45, -135, 200))
emit("elips-tanimi", p,
     f"{em('F')}<sub>1</sub> ve {em('F')}<sub>2</sub> odaklı elips: her {em('P')} noktası için "
     f"|{em('PF')}<sub>1</sub>| + |{em('PF')}<sub>2</sub>| = 2{em('a')}. {A1}{A2} ve {B1}{B2} elipsin "
     f"merkezi {em('M')}'de dik kesişen eksenleridir.",
     "An inclined ellipse with foci F1 and F2, center M, vertices A1, A2, B1, B2 and a point P "
     "joined to both foci")

# ============================================================ tanim-nokta
p = Fig((-6, 6), (-4.5, 4.5), 560)
p.axes2((-6, 6), (-4.5, 4.5))
p.ell((0, 0), 5, 4)
Q = (4.0, 2.4)
f1, f2 = (3.0, 0.0), (-3.0, 0.0)
p.seg(Q, f1, PRACTICE, 2.0, name="QF1")
p.seg(Q, f2, BASE, 2.0, name="QF2")
p.dot(f1, PRACTICE)
p.dot(f2, PRACTICE)
p.dot(Q)
p.lab_out(Q, f1, "13/5", f2, 6, 0.5, NAME, PRACTICE)
p.lab_out(Q, f2, "37/5", f1, 6, 0.3, NAME, BASE)
p.lab_auto(Q, "Q(4, 12/5)", (40, 55, 25, 70))
p.lab_auto(f1, "F_1", (-90, -60, -120))
p.lab_auto(f2, "F_2", (-90, -60, -120))
dr = p.int_numbers()
emit("tanim-nokta", p,
     f"{em('Q')}(4, 12/5) noktasının odaklara uzaklıkları 13/5 ve 37/5'tir; toplamları 10 = 2{em('a')} "
     f"olduğundan {em('Q')}, {X2}/25 + {Y2}/16 = 1 elipsinin üzerindedir.",
     "Ellipse x2/25+y2/16=1 with foci (3,0), (-3,0) and the point Q(4,12/5) joined to both foci",
     dropped=dr)

# ============================================================ kose-koordinatlari
p = Fig((-6.5, 6.5), (-4.5, 4.5), 560)
p.axes2((-6.5, 6.5), (-4.5, 4.5), ticks=0)
p.ell((0, 0), 5, 3)
b1, f1, f2 = (0.0, 3.0), (4.0, 0.0), (-4.0, 0.0)
p.seg(b1, f1, PRACTICE, 2.0, name="B1F1")
p.seg(b1, f2, BASE, 2.0, name="B1F2")
p.right_angle((0, 0), (1, 0), (0, 1), 9)
P = ell_pt(35, 5, 3)
for q in ((5.0, 0.0), (-5.0, 0.0), b1, (0.0, -3.0), P):
    p.dot(q)
p.dot(f1, PRACTICE)
p.dot(f2, PRACTICE)
p.lab_out(b1, f1, "a", (0, 0), 6, 0.5, NAME + 1, PRACTICE)
p.lab_out(b1, f2, "a", (0, 0), 6, 0.5, NAME + 1, BASE)
p.lab((0, 1.5), "b", 0, 6, NAME + 1)
p.lab((2, 0), "c", -90, 6, NAME + 1)
p.lab_auto((5.0, 0.0), "A_1(a, 0)", (-40, -60, -25))
p.lab_auto((-5.0, 0.0), "A_2(" + MINUS + "a, 0)", (-140, -120, -155))
p.lab_auto(b1, "B_1(0, b)", (125, 145, 110))
p.lab_auto((0.0, -3.0), "B_2(0, " + MINUS + "b)", (-125, -145, -110))
p.lab_auto(f1, "F_1(c, 0)", (-90, -75, -105))
p.lab_auto(f2, "F_2(" + MINUS + "c, 0)", (-90, -75, -105))
p.lab_auto(P, "P(x, y)", (ell_normal(35, 5, 3), 30, 50))
emit("kose-koordinatlari", p,
     f"Uzak köşeler ({MINUS}{em('a')}, 0), ({em('a')}, 0); yakın köşeler (0, &#177;{em('b')}). "
     f"{B1}'den iki odağa uzaklık {em('a')}'dır; {em('O')}{B1}{F1} dik üçgeni "
     f"{em('b')}<sup>2</sup> + {em('c')}<sup>2</sup> = {em('a')}<sup>2</sup> bağıntısını verir.",
     "Ellipse with a=5, b=3, c=4: vertices A1, A2, B1, B2, foci F1, F2, the segments B1F1 and B1F2 "
     "of length a and the right triangle O B1 F1")

# ============================================================ standart-denklem-ispat
p = Fig((-6.5, 6.5), (-4.5, 4.5), 560)
p.axes2((-6.5, 6.5), (-4.5, 4.5), ticks=0)
p.ell((0, 0), 5, 3)
P = (2.0, 3 * math.sqrt(21) / 5)
Hh = (2.0, 0.0)
f1, f2 = (4.0, 0.0), (-4.0, 0.0)
p.seg(P, Hh, TEXT, 1.4, "5 4", name="PH")
p.right_angle(Hh, (0, 1), (1, 0), 9)
p.seg(P, f1, PRACTICE, 2.0, name="PF1")
p.seg(P, f2, BASE, 2.0, name="PF2")
for q in ((5.0, 0.0), (-5.0, 0.0), (0.0, 3.0), (0.0, -3.0), P):
    p.dot(q)
p.dot(Hh, TEXT, 3.4)
p.dot(f1, PRACTICE)
p.dot(f2, PRACTICE)
p.lab_out(P, f1, "|PF_1|", Hh, 5, 0.6, NAME, PRACTICE)
p.lab_out(P, f2, "|PF_2|", Hh, 6, 0.5, NAME, BASE)
p.lab_auto(P, "P(x, y)", (90, 75, 105, 60))
p.lab_auto(Hh, "H(x, 0)", (-110, -90, -130))
p.lab_auto((5.0, 0.0), "A_1(a, 0)", (-40, -60, -25))
p.lab_auto((-5.0, 0.0), "A_2(" + MINUS + "a, 0)", (-140, -120, -155))
p.lab_auto((0.0, 3.0), "B_1(0, b)", (125, 145, 110))
p.lab_auto((0.0, -3.0), "B_2(0, " + MINUS + "b)", (-125, -145, -110))
p.lab_auto(f1, "F_1(c, 0)", (-90, -75, -60))
p.lab_auto(f2, "F_2(" + MINUS + "c, 0)", (-90, -75, -105))
emit("standart-denklem-ispat", p,
     f"{em('P')}'den {em('X')}-eksenine inen dikmenin ayağı {em('H')}; {em('PHF')}<sub>1</sub> ve "
     f"{em('PHF')}<sub>2</sub> dik üçgenlerinde Pisagor bağıntısı |{em('PF')}<sub>1</sub>| ve "
     f"|{em('PF')}<sub>2</sub>|'yi {em('x')} cinsinden verir.",
     "Ellipse with a=5, b=3, a point P on it, the foot H of the perpendicular to the X axis and the "
     "segments PF1, PF2")

# ============================================================ kose-ve-nokta
p = Fig((-5, 5), (-3, 3), 560)
p.axes2((-5, 5), (-3, 3))
p.ell((0, 0), 4, 2)
P = (2.0, math.sqrt(3))
for q in ((4.0, 0.0), (-4.0, 0.0), P):
    p.dot(q)
p.lab_auto((4.0, 0.0), "A_1(4, 0)", (-40, -60, -25))
p.lab_auto((-4.0, 0.0), "A_2(" + MINUS + "4, 0)", (-140, -120, -155))
p.lab_auto(P, "P(2, " + SQRT + "3)", (45, 60, 30))
dr = p.int_numbers()
emit("kose-ve-nokta", p,
     f"Uzak köşeleri (&#177;4, 0) olan ve {em('P')}(2, &#8730;3) noktasından geçen elips: "
     f"{X2}/16 + {Y2}/4 = 1.",
     "Ellipse x2/16+y2/4=1 with vertices (4,0), (-4,0) through the point P(2, sqrt 3)", dropped=dr)

# ============================================================ odaklar-100-64
p = Fig((-12, 12), (-9.5, 9.5), 560)
p.axes2((-12, 12), (-9.5, 9.5), ticks=2)
p.ell((0, 0), 10, 8)
f1, f2 = (6.0, 0.0), (-6.0, 0.0)
yd = -1.3
p.seg(f1, (6.0, yd - 0.4), TEXT, 0.9, None, 0.6, "guide")
p.seg(f2, (-6.0, yd - 0.4), TEXT, 0.9, None, 0.6, "guide")
p.dim((-6.0, yd), (6.0, yd))
for q in ((10.0, 0.0), (-10.0, 0.0), (0.0, 8.0), (0.0, -8.0)):
    p.dot(q, TEXT, 3.4)
p.dot(f1, PRACTICE)
p.dot(f2, PRACTICE)
p.lab_auto(f1, "F_1(6, 0)", (90, 70, 110))
p.lab_auto(f2, "F_2(" + MINUS + "6, 0)", (90, 110, 70))
p.lab((3.0, yd), "2c = 12", -90, 5)
dr = p.int_numbers(2)
emit("odaklar-100-64", p,
     f"{X2}/100 + {Y2}/64 = 1 elipsinde {em('c')} = 6: odaklar {F1}(6, 0) ve {F2}({MINUS}6, 0), "
     f"aralarındaki uzaklık 2{em('c')} = 12.",
     "Ellipse x2/100+y2/64=1 with foci (6,0), (-6,0) and the distance 2c=12 between them", dropped=dr)

# ============================================================ dusey
p = Fig((-4.5, 4.5), (-6, 6), 440)
p.axes2((-4.5, 4.5), (-6, 6))
p.ell((0, 0), 3, 5)
for q in ((0.0, 5.0), (0.0, -5.0), (3.0, 0.0), (-3.0, 0.0)):
    p.dot(q)
f1, f2 = (0.0, 4.0), (0.0, -4.0)
p.dot(f1, PRACTICE)
p.dot(f2, PRACTICE)
p.lab_auto((0.0, 5.0), "(0, 5)", (30, 45, 15))
p.lab_auto((0.0, -5.0), "(0, " + MINUS + "5)", (-30, -45, -15))
p.lab_auto((3.0, 0.0), "(3, 0)", (40, 55, 25))
p.lab_auto((-3.0, 0.0), "(" + MINUS + "3, 0)", (140, 125, 155))
p.lab_auto(f1, "F_1(0, 4)", (180, 200, 160))
p.lab_auto(f2, "F_2(0, " + MINUS + "4)", (180, 160, 200))
dr = p.int_numbers()
emit("dusey", p,
     f"{X2}/9 + {Y2}/25 = 1 elipsinin asal ekseni {em('Y')}-eksenidir: uzak köşeler (0, &#177;5), "
     f"yakın köşeler (&#177;3, 0), odaklar (0, &#177;4).",
     "Ellipse x2/9+y2/25=1 with vertical major axis, vertices (0,5), (0,-5), (3,0), (-3,0) and foci "
     "(0,4), (0,-4)", dropped=dr)

# ============================================================ kareye-tamamlama
p = Fig((-2, 6), (-4, 2), 560)
p.axes2((-2, 6), (-4, 2))
M = (2.0, -1.0)
p.seg((-2, -1), (6, -1), TEXT, 1.1, "6 4", 0.7, "X'")
p.seg((2, -4), (2, 2), TEXT, 1.1, "6 4", 0.7, "Y'")
p.ell(M, 3, 2)
f1, f2 = (2 + math.sqrt(5), -1.0), (2 - math.sqrt(5), -1.0)
for q in ((5.0, -1.0), (-1.0, -1.0), (2.0, 1.0), (2.0, -3.0), M):
    p.dot(q)
p.dot(f1, PRACTICE)
p.dot(f2, PRACTICE)
p.lab((6, -1), "X'", 90, 5, 13)
p.lab((2, 2), "Y'", 0, 6, 13)
p.lab_auto(M, "M(2, " + MINUS + "1)", (-45, -30, -60))
p.lab_auto((5.0, -1.0), "(5, " + MINUS + "1)", (-40, 40, -25))
p.lab_auto((-1.0, -1.0), "(" + MINUS + "1, " + MINUS + "1)", (-140, 140, -155))
p.lab_auto((2.0, 1.0), "(2, 1)", (40, 55, 25))
p.lab_auto((2.0, -3.0), "(2, " + MINUS + "3)", (-40, -55, -25))
p.lab_auto(f1, "F_1", (90, 70, 110))
p.lab_auto(f2, "F_2", (90, 110, 70))
dr = p.int_numbers()
emit("kareye-tamamlama", p,
     f"4{X2} + 9{Y2} &#8722; 16{em('x')} + 18{em('y')} &#8722; 11 = 0 elipsi: merkez {em('M')}(2, &#8722;1), "
     f"{em('a')} = 3, {em('b')} = 2, odaklar (2 &#177; &#8730;5, &#8722;1). Kesikli doğrular merkeze "
     f"ötelenmiş {em('X')}'{em('Y')}' eksenleridir.",
     "Ellipse (x-2)2/9+(y+1)2/4=1 with center M(2,-1), its four vertices, foci and the translated axes "
     "through M", dropped=dr)

# ============================================================ parametre-25-16
p = Fig((-6, 7.5), (-4.8, 4.8), 560)
p.axes2((-6, 7.5), (-4.8, 4.8))
p.ell((0, 0), 5, 4)
top, bot = (3.0, 3.2), (3.0, -3.2)
xd = 6.4
p.seg(top, (xd + 0.3, 3.2), TEXT, 0.9, None, 0.6, "guide")
p.seg(bot, (xd + 0.3, -3.2), TEXT, 0.9, None, 0.6, "guide")
p.dim((xd, 3.2), (xd, -3.2))
p.seg(top, bot, PRACTICE, 3.0, name="chord")
p.right_angle((3.0, 0.0), (0, 1), (-1, 0), 9)
p.dot(top)
p.dot(bot)
f1, f2 = (3.0, 0.0), (-3.0, 0.0)
p.dot(f1, PRACTICE)
p.dot(f2, PRACTICE)
p.lab_auto(top, "(3, 16/5)", (100, 115, 130))
p.lab_auto(bot, "(3, " + MINUS + "16/5)", (-100, -115, -130))
p.lab_auto(f1, "F_1", (-135, -150, -120))
p.lab_auto(f2, "F_2", (-90, -60, -120))
p.lab((xd, 0.9), "2p = 32/5", 0, 6)
dr = p.int_numbers()
emit("parametre-25-16", p,
     f"{X2}/25 + {Y2}/16 = 1 elipsinde {F1}(3, 0) odağından asal eksene dik kirişin uzunluğu "
     f"2{em('p')} = 2{em('b')}<sup>2</sup>/{em('a')} = 32/5'tir.",
     "Ellipse x2/25+y2/16=1 and the focal chord x=3 from (3,16/5) to (3,-16/5) of length 32/5",
     dropped=dr)

# ============================================================ teget-genel
p = Fig((-6, 7.5), (-4, 5.5), 560)
p.axes2((-6, 7.5), (-4, 5.5), ticks=0)
p.ell((0, 0), 5, 3)
P = (3.0, 2.4)
ta, tb = (-1.0, 3.75 + 0.45), (7.2, 3.75 - 0.45 * 7.2)
p.seg(ta, tb, PRACTICE, 2.2, name="tangent")
for v, s, ang in ((5, "a", -45), (-5, MINUS + "a", -135), (4, "c", -90), (-4, MINUS + "c", -90)):
    p.tick_mark((v, 0), "x")
    p.lab((v, 0), s, ang, 7, NAME)
for v, s in ((3, "b"), (-3, MINUS + "b")):
    p.tick_mark((0, v), "y")
    p.lab((0, v), s, 125 if v > 0 else -125, 7, NAME)
p.dot(P)
p.lab_auto(P, "P(x_0, y_0)", (60, 75, 45, 90))
p.lab_seg(ta, tb, "T_d", -1, 6, 0.93, NAME + 1, PRACTICE)
bx = p.lab_px(p.X(-5.6), p.Y(-3.55), "x²/a² + y²/b² = 1", NAME, THEORY, "start")
p.leader(bx, ell_pt(-118, 5, 3), THEORY)
emit("teget-genel", p,
     f"Elipsin {em('P')}({em('x')}<sub>0</sub>, {em('y')}<sub>0</sub>) noktasındaki teğeti "
     f"{em('x')}<sub>0</sub>{em('x')}/{em('a')}<sup>2</sup> + {em('y')}<sub>0</sub>{em('y')}/{em('b')}<sup>2</sup> = 1 "
     "doğrusudur; elipsle yalnız bu noktada buluşur.",
     "Ellipse x2/a2+y2/b2=1 with the tangent line T_d at a point P(x0,y0)")

# ============================================================ teget-normal-sayisal
p = Fig((-6, 9), (-4.8, 6.5), 560)
p.axes2((-6, 9), (-4.8, 6.5))
p.ell((0, 0), 5, 4)
P = (3.0, 3.2)
ta, tb = (-1.0, (25 + 3) / 5), (8.5, (25 - 3 * 8.5) / 5)
na, nb = (0.5, (25 * 0.5 - 27) / 15), (4.9, (25 * 4.9 - 27) / 15)
p.seg(ta, tb, PRACTICE, 2.2, name="tangent")
p.seg(na, nb, BASE, 2.2, name="normal")
p.right_angle(P, (5, -3), (3, 5), 10)
f1, f2 = (3.0, 0.0), (-3.0, 0.0)
p.dot(f1, PRACTICE, 3.6)
p.dot(f2, PRACTICE, 3.6)
p.dot(P)
p.lab_auto(P, "P(3, 16/5)", (104, 112, 96), grow=(0, 6, 12, 18, 24, 30, 36))
p.lab_auto(f1, "F_1", (-60, -45, -120))
p.lab_auto(f2, "F_2", (-60, -120, -45))
p.lab_seg(ta, tb, "3x + 5y = 25", 1, 6, 0.82, NAME, PRACTICE)
p.lab_seg(na, nb, "25x " + MINUS + " 15y = 27", 1, 6, 0.9, NAME, BASE)
dr = p.int_numbers()
emit("teget-normal-sayisal", p,
     f"{X2}/25 + {Y2}/16 = 1 elipsinin {em('P')}(3, 16/5) noktasındaki teğeti 3{em('x')} + 5{em('y')} = 25, "
     f"normali 25{em('x')} &#8722; 15{em('y')} = 27'dir; eğimleri &#8722;3/5 ve 5/3.",
     "Ellipse x2/25+y2/16=1 with the tangent 3x+5y=25 and the normal 25x-15y=27 at P(3,16/5)",
     dropped=dr)

# ============================================================ dogru-durumlari
p = Fig((-6, 6), (-5.5, 5.5), 560)
p.axes2((-6, 6), (-5.5, 5.5), ticks=0)
p.ell((0, 0), 4, 3)
cols = {1.0: BASE, math.sqrt(13): PRACTICE, 5.2: REMARK}
ends = {}
for n, col in cols.items():
    ends[n] = p.line_clipped((-6, 3 + n), (6, -3 + n), col, 2.0, None, f"n={n:.2f}")
x1 = (16 + math.sqrt(16 * 16 + 4 * 13 * 128)) / 26
x2 = (16 - math.sqrt(16 * 16 + 4 * 13 * 128)) / 26
for xx in (x1, x2):
    p.dot((xx, 1 - xx / 2), BASE)
T = (8 / math.sqrt(13), 9 / math.sqrt(13))
p.dot(T, PRACTICE)
for n, s in ((1.0, "Δ &gt; 0"), (math.sqrt(13), "Δ = 0"), (5.2, "Δ &lt; 0")):
    a_, b_ = ends[n]
    p.lab_seg(a_, b_, s, 1, 6, 0.9, NAME, cols[n])
emit("dogru-durumlari", p,
     f"{X2}/16 + {Y2}/9 = 1 elipsi ve eğimi &#8722;1/2 olan üç doğru: {em('n')} = 1 iken iki ortak nokta, "
     f"{em('n')} = &#8730;13 iken teğet, {em('n')} = 5,2 iken ortak nokta yok.",
     "Ellipse x2/16+y2/9=1 and three parallel lines of slope -1/2: secant, tangent and missing line")

# ============================================================ dogru-kesen
p = Fig((-3, 3), (-1.8, 2.2), 560)
p.axes2((-3, 3), (-1.8, 2.2))
p.ell((0, 0), 2, 1)
la, lb = (-3.0, -0.5), (2.4, 2.2)
p.seg(la, lb, PRACTICE, 2.2, name="line")
p.dot((0.0, 1.0))
p.dot((-2.0, 0.0))
p.lab_auto((0.0, 1.0), "(0, 1)", (125, 140, 110))
p.lab_auto((-2.0, 0.0), "(" + MINUS + "2, 0)", (135, 120, 150))
p.lab_seg(la, lb, "y = x/2 + 1", -1, 6, 0.83, NAME, PRACTICE)
dr = p.int_numbers()
emit("dogru-kesen", p,
     f"{em('y')} = {em('x')}/2 + 1 doğrusu {X2}/4 + {Y2} = 1 elipsini (0, 1) ve (&#8722;2, 0) "
     "noktalarında keser.",
     "Ellipse x2/4+y2=1 cut by the line y=x/2+1 at (0,1) and (-2,0)", dropped=dr)

# ============================================================ teget-n-bulma
p = Fig((-7.5, 7.5), (-6.5, 6.5), 560)
p.axes2((-7.5, 7.5), (-6.5, 6.5))
p.ell((0, 0), 5, 3)
s34 = math.sqrt(34)
d1 = p.line_clipped((-7.5, -7.5 + s34), (7.5, 7.5 + s34), PRACTICE, 2.0, None, "d1")
d2 = p.line_clipped((-7.5, -7.5 - s34), (7.5, 7.5 - s34), PRACTICE, 2.0, None, "d2")
P1, P2 = (-25 / s34, 9 / s34), (25 / s34, -9 / s34)
p.dot(P1)
p.dot(P2)
p.lab_auto(P1, "P_1", (-45, -30, -60, 135))
p.lab_auto(P2, "P_2", (135, 150, 120, -45))
p.lab_seg(d1[0], d1[1], "d_1: y = x + " + SQRT + "34", 1, 6, 0.62, NAME, PRACTICE)
p.lab_seg(d2[0], d2[1], "d_2: y = x " + MINUS + " " + SQRT + "34", -1, 6, 0.38, NAME, PRACTICE)
dr = p.int_numbers(skip=(-7, 7))
emit("teget-n-bulma", p,
     f"{em('y')} = {em('x')} &#177; &#8730;34 doğruları {X2}/25 + {Y2}/9 = 1 elipsine "
     f"{em('P')}<sub>1</sub>({MINUS}25/&#8730;34, 9/&#8730;34) ve {em('P')}<sub>2</sub>(25/&#8730;34, "
     f"{MINUS}9/&#8730;34) noktalarında teğettir.",
     "Ellipse x2/25+y2/9=1 with the two tangents of slope 1, y=x+sqrt34 and y=x-sqrt34, and their "
     "points of contact P1, P2", dropped=dr)

# ============================================================ monge
p = Fig((-7, 7), (-7, 7), 640)
p.axes2((-7, 7), (-7, 7))
s34 = math.sqrt(34)
p.poly([(-5, -3), (5, -3), (5, 3), (-5, 3), (-5, -3)], TEXT, 1.0, "4 3", 0.6, "rectangle")
p.circ((0, 0), s34, PRACTICE, 1.8, "7 5", "monge")
lines = []
ov = 0.45 / math.sqrt(2)
for sx, sy in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
    # the side y = sx*x + sy*sqrt34 of the square, from one vertex to the next, slightly overshooting
    x0, x1 = (-s34, 0.0) if sx * sy > 0 else (0.0, s34)
    a_, b_ = (x0 - ov, sx * (x0 - ov) + sy * s34), (x1 + ov, sx * (x1 + ov) + sy * s34)
    p.seg(a_, b_, BASE, 1.6, None, 1.0, "tangent")
p.ell((0, 0), 5, 3)
V = [(0, s34), (s34, 0), (0, -s34), (-s34, 0)]
for k, v in enumerate(V):
    inward = (-v[0], -v[1])
    d1 = pol(1, angle_of(inward) + 45)
    d2 = pol(1, angle_of(inward) - 45)
    p.right_angle(v, d1, d2, 9)
    p.dot(v)
for q in ((5, 3), (-5, 3), (5, -3), (-5, -3)):
    p.dot(q, TEXT, 3.2)
p.lab_auto(V[0], "(0, " + SQRT + "34)", (22, 158), grow=tuple(range(0, 70, 4)))
p.lab_auto(V[1], "(" + SQRT + "34, 0)", (-22, 22), grow=tuple(range(0, 70, 4)))
p.lab_auto(V[2], "(0, " + MINUS + SQRT + "34)", (-22, -158), grow=tuple(range(0, 70, 4)))
p.lab_auto(V[3], "(" + MINUS + SQRT + "34, 0)", (-158, 158), grow=tuple(range(0, 70, 4)))
bx = p.lab_px(p.X(3.6), p.Y(6.3), "x² + y² = 34", NAME, PRACTICE, "start")
p.leader(bx, pol(s34, 58), PRACTICE)
dr = p.int_numbers()
emit("monge", p,
     f"{X2}/25 + {Y2}/9 = 1 elipsinin eğimi &#177;1 olan dört teğeti bir kare oluşturur; karenin köşeleri "
     f"ve 10 &#215; 6 dikdörtgenin köşeleri Monge çemberi {X2} + {Y2} = 34 üzerindedir.",
     "Ellipse x2/25+y2/9=1, its Monge circle x2+y2=34, the four tangents of slope 1 and -1 forming a "
     "square with vertices on the circle, and the bounding 10 by 6 rectangle", css=WIDE, dropped=dr)

# ============================================================ dis-merkezlik
p = Fig((-6, 6), (-5.5, 5.5), 600)
p.axes2((-6, 6), (-5.5, 5.5), ticks=0)
fam = [(0.0, 5.0, THEORY, 60, "e = 0"), (0.6, 4.0, PRACTICE, 72, "e = 0,6"),
       (0.8, 3.0, BASE, 66, "e = 0,8"), (0.95, 5 * math.sqrt(1 - 0.95 ** 2), REMARK, 58, "e = 0,95")]
for e, bb, col, _, _ in fam:
    p.ell((0, 0), 5, bb, 0, col, 2.0, None, f"e={e}")
for e, bb, col, _, _ in fam:
    if e == 0:
        p.dot((0, 0), col, 3.6)
    else:
        p.dot((5 * e, 0), col, 3.6)
        p.dot((-5 * e, 0), col, 3.6)
for e, bb, col, t, s in fam:
    q = ell_pt(t, 5, bb)
    p.lab(q, s, ell_normal(t, 5, bb), 4, NAME, col)
emit("dis-merkezlik", p,
     f"Asal yarı ekseni {em('a')} = 5 olan elipsler: {em('e')} büyüdükçe odaklar (&#177;5{em('e')}, 0) "
     f"uzak köşelere yaklaşır ve elips basıklaşır; {em('e')} = 0 çemberdir.",
     "Four ellipses with a=5 and eccentricity 0, 0.6, 0.8, 0.95, with their foci on the X axis",
     css=WIDE)

# ============================================================ asal-yedek-cember
p = Fig((-6.5, 6.5), (-6.5, 6.5), 560)
p.axes2((-6.5, 6.5), (-6.5, 6.5), ticks=0)
p.circ((0, 0), 5, PRACTICE, 1.8, None, "big")
p.circ((0, 0), 3, BASE, 1.8, None, "small")
p.ell((0, 0), 5, 3)
for v, s, ang in ((5, "a", -45), (-5, MINUS + "a", -135)):
    p.tick_mark((v, 0), "x")
    p.lab((v, 0), s, ang, 5, NAME)
for v, s, ang in ((3, "b", 135), (-3, MINUS + "b", -135)):
    p.tick_mark((0, v), "y")
    p.lab((0, v), s, ang, 5, NAME)
p.lab(pol(5, 45), "asal çember", 45, 7, DESC, PRACTICE, raw=True)
p.lab_px(p.X(-1.55), p.Y(1.15), "yedek çember", DESC, BASE, "middle", raw=True)
bx = p.lab_px(p.X(2.2), p.Y(-6.05), "x²/a² + y²/b² = 1", NAME, THEORY, "start")
p.leader(bx, ell_pt(-62, 5, 3), THEORY)
emit("asal-yedek-cember", p,
     f"Elipsin asal çemberi {X2} + {Y2} = {em('a')}<sup>2</sup>, yedek çemberi {X2} + {Y2} = "
     f"{em('b')}<sup>2</sup>; elips ikisinin arasında kalır.",
     "Ellipse with a=5, b=3 between its major circle of radius a and minor circle of radius b")

# ============================================================ parametrik
p = Fig((-6.5, 6.5), (-6, 6), 700)
p.axes2((-6.5, 6.5), (-6, 6), ticks=0)
th = 50.0
R = pol(5, th)
S = pol(3, th)
Hh, K = (R[0], 0.0), (S[0], 0.0)
P = (R[0], S[1])
p.circ((0, 0), 5, PRACTICE, 1.4, None, "big")
p.circ((0, 0), 3, BASE, 1.4, None, "small")
p.ell((0, 0), 5, 3)
p.seg((0, 0), R, TEXT, 1.6, name="OR")
p.seg(R, Hh, TEXT, 1.3, "5 4", name="RH")
p.seg(S, K, TEXT, 1.3, "5 4", name="SK")
p.seg(S, P, TEXT, 1.6, name="SP")
p.right_angle(Hh, (0, 1), (-1, 0), 8)
p.right_angle(K, (0, 1), (-1, 0), 8)
p.angle_arc((0, 0), 0, th, 30, TEXT, 1.3)
for v, s, ang in ((5, "a", -45), (-5, MINUS + "a", -135)):
    p.tick_mark((v, 0), "x")
    p.lab((v, 0), s, ang, 5, NAME)
for v, s, ang in ((3, "b", 135), (-3, MINUS + "b", -135)):
    p.tick_mark((0, v), "y")
    p.lab((0, v), s, ang, 5, NAME)
p.dot(R)
p.dot(S)
p.dot(P, PRACTICE)
p.dot(Hh, TEXT, 3.4)
p.dot(K, TEXT, 3.4)
p.lab(pol(30 / p.ppu, th / 2), "θ", th / 2, 4, NAME + 1)
p.lab_auto(R, "R", (60, 45, 30))
p.lab_auto(S, "S", (185, 195, 175))
p.lab_auto(P, "P", (10, 20, 0, 30), 6, NAME + 1)
p.lab_auto(Hh, "H", (-60, -90, -45))
p.lab_auto(K, "K", (-120, -90, -135))
emit("parametrik", p,
     f"{em('P')}'nin apsisi {em('R')}'den, ordinatı {em('S')}'den gelir: "
     f"{em('P')} = ({em('a')} cos &#952;, {em('b')} sin &#952;).",
     "Ellipse with a=5, b=3 and its two circles; for theta=50 degrees the ray OR meets the circles at "
     "R and S, and P on the ellipse has the abscissa of R and the ordinate of S", css=WIDE)

# ============================================================ odak-dogrultman
p = Fig((-9.5, 9.5), (-5, 5), 660)
p.axes2((-9.5, 9.5), (-5, 5), ticks=0)
p.ell((0, 0), 5, 4)
dx = 25 / 3
p.seg((dx, -4.6), (dx, 4.6), BASE, 2.0, name="D1")
p.seg((-dx, -4.6), (-dx, 4.6), BASE, 2.0, name="D2")
p.right_angle((dx, 0), (0, 1), (-1, 0), 8)
p.right_angle((-dx, 0), (0, 1), (1, 0), 8)
P = (4.0, 2.4)
f1, f2 = (3.0, 0.0), (-3.0, 0.0)
p.seg(P, f1, PRACTICE, 2.0, name="r")
p.seg(P, (dx, 2.4), PRACTICE, 1.6, "5 4", name="d")
p.right_angle((dx, 2.4), (-1, 0), (0, -1), 8)
for v, s, ang in ((5, "a", -45), (-5, MINUS + "a", -135)):
    p.tick_mark((v, 0), "x")
    p.lab((v, 0), s, ang, 5, NAME)
p.dot(P)
p.dot(f1, PRACTICE)
p.dot(f2, PRACTICE)
p.lab_auto(P, "P(x, y)", (120, 135, 105, 150, 90), grow=tuple(range(0, 34, 3)))
p.lab_auto(f1, "F_1(c, 0)", (-90, -110, -70))
p.lab_auto(f2, "F_2(" + MINUS + "c, 0)", (-90, -70, -110))
p.lab((dx, 4.6), "Δ_1", 90, 5, NAME + 1, BASE)
p.lab((-dx, 4.6), "Δ_2", 90, 5, NAME + 1, BASE)
p.lab((dx, -4.2), "x = a²/c", 180, 7, NAME, BASE)
p.lab((-dx, -4.2), "x = " + MINUS + "a²/c", 0, 7, NAME, BASE)
p.lab_seg(P, f1, "r", -1, 5, 0.5, NAME + 1, PRACTICE)
p.lab(mid(P, (dx, 2.4)), "d", 90, 5, NAME + 1, PRACTICE)
emit("odak-dogrultman", p,
     f"{X2}/25 + {Y2}/16 = 1 elipsinin doğrultmanları {em('x')} = &#177;25/3. Elipsin her {em('P')} noktası "
     f"için {em('r')}/{em('d')} = |{em('PF')}<sub>1</sub>|/{em('d')}({em('P')}, &#916;<sub>1</sub>) = "
     f"{em('e')} = 3/5.",
     "Ellipse x2/25+y2/16=1 with its directrices x=25/3 and x=-25/3, a point P, its distance r to F1 "
     "and its distance d to the directrix", css=WIDE)

# ============================================================ ikinci-tanim
p = Fig((-9.5, 6.5), (-5, 5), 560)
p.axes2((-9.5, 6.5), (-5, 5))
p.ell((0, 0), 5, 4)
dx = -25 / 3
p.seg((dx, -5), (dx, 4.7), BASE, 2.0, name="directrix")
P = (-4.0, 2.4)
F = (-3.0, 0.0)
p.seg(P, F, PRACTICE, 2.0, name="r")
p.seg(P, (dx, 2.4), PRACTICE, 1.6, "5 4", name="d")
p.right_angle((dx, 2.4), (1, 0), (0, -1), 8)
p.dot(P)
p.dot(F, PRACTICE)
p.lab_auto(P, "P", (90, 70, 110, 45))
p.lab_auto(F, "F(" + MINUS + "3, 0)", (-60, -45, -75, -90))
p.lab((dx, 4.7), "x = " + MINUS + "25/3", 10, 6, NAME, BASE)
p.lab_seg(P, F, "r", -1, 5, 0.5, NAME + 1, PRACTICE)
p.lab(mid(P, (dx, 2.4)), "d", 90, 5, NAME + 1, PRACTICE)
p.lab_px(p.X(3.2), p.Y(4.4), "r/d = 3/5", NAME, TEXT, "middle")
dr = p.int_numbers()
emit("ikinci-tanim", p,
     f"{em('F')}({MINUS}3, 0) noktasına ve {em('x')} = {MINUS}25/3 doğrusuna uzaklıklarının oranı 3/5 olan "
     f"noktalar {X2}/25 + {Y2}/16 = 1 elipsini oluşturur.",
     "Ellipse x2/25+y2/16=1 as the locus with focus F(-3,0), directrix x=-25/3 and ratio r/d=3/5",
     dropped=dr)

# ============================================================ exr-iki-noktadan
p = Fig((-7, 7), (-5, 5), 560)
p.axes2((-7, 7), (-5, 5))
p.ell((0, 0), 6, 4)
Q1, Q2 = (-3.0, 2 * math.sqrt(3)), (4.0, 4 * math.sqrt(5) / 3)
p.dot(Q1)
p.dot(Q2)
f1, f2 = (2 * math.sqrt(5), 0.0), (-2 * math.sqrt(5), 0.0)
p.dot(f1, PRACTICE, 3.6)
p.dot(f2, PRACTICE, 3.6)
p.lab_auto(Q1, "(" + MINUS + "3, 2" + SQRT + "3)", (120, 135, 105))
p.lab_auto(Q2, "(4, 4" + SQRT + "5/3)", (50, 65, 35))
p.lab_auto(f1, "F_1", (90, 110, 70))
p.lab_auto(f2, "F_2", (90, 70, 110))
dr = p.int_numbers()
emit("exr-iki-noktadan", p,
     f"({MINUS}3, 2&#8730;3) ve (4, 4&#8730;5/3) noktalarından geçen {X2}/36 + {Y2}/16 = 1 elipsi; "
     "odakları (&#177;2&#8730;5, 0).",
     "Ellipse x2/36+y2/16=1 through (-3, 2 sqrt3) and (4, 4 sqrt5/3) with foci (2 sqrt5, 0), (-2 sqrt5, 0)",
     dropped=dr)

# ============================================================ exr-odaklardan-geometrik-yer
p = Fig((-7, 5), (-2.5, 4.5), 560)
p.axes2((-7, 5), (-2.5, 4.5))
M = (-1.0, 1.0)
p.seg((-6, 1), (4, 1), TEXT, 1.1, "6 4", 0.7, "major axis")
p.ell(M, 5, 3)
f1, f2 = (3.0, 1.0), (-5.0, 1.0)
p.dot(M)
p.dot(f1, PRACTICE)
p.dot(f2, PRACTICE)
p.lab_auto(f1, "F_1(3, 1)", (-90, -110, -70))
p.lab_auto(f2, "F_2(" + MINUS + "5, 1)", (-90, -70, -110))
p.lab_auto(M, "M(" + MINUS + "1, 1)", (-90, -70, -110))
dr = p.int_numbers()
emit("exr-odaklardan-geometrik-yer", p,
     f"{F1}(3, 1) ve {F2}({MINUS}5, 1) noktalarına uzaklıkları toplamı 10 olan noktalar: merkezi "
     f"{em('M')}({MINUS}1, 1) olan ({em('x')} + 1)<sup>2</sup>/25 + ({em('y')} &#8722; 1)<sup>2</sup>/9 = 1 elipsi.",
     "Ellipse (x+1)2/25+(y-1)2/9=1 with foci (3,1), (-5,1) and center M(-1,1)", dropped=dr)

# ============================================================ exr-kosul-merkez-i
p = Fig((-6, 6), (-2.8, 6.8), 560)
p.axes2((-6, 6), (-2.8, 6.8))
M = (0.0, 2.0)
p.seg((-5, 2), (5, 2), TEXT, 1.1, "6 4", 0.7, "major axis")
p.ell(M, 5, 4)
f1, f2 = (3.0, 2.0), (-3.0, 2.0)
p.dot(M)
p.dot(f1, PRACTICE)
p.dot(f2, PRACTICE)
p.lab_auto(f1, "F_1(3, 2)", (-90, -110, -70))
p.lab_auto(f2, "F_2(" + MINUS + "3, 2)", (-90, -70, -110))
p.lab_auto(M, "M(0, 2)", (45, 30, 60))
dr = p.int_numbers()
emit("exr-kosul-merkez-i", p,
     f"Odakları ({MINUS}3, 2), (3, 2) ve asal eksen uzunluğu 10 olan elips: "
     f"{X2}/25 + ({em('y')} &#8722; 2)<sup>2</sup>/16 = 1.",
     "Ellipse x2/25+(y-2)2/16=1 with center M(0,2) and foci (-3,2), (3,2)", dropped=dr)

# ============================================================ exr-kosul-merkez-ii
p = Fig((-1.5, 11.5), (-5, 5), 560)
p.axes2((-1.5, 11.5), (-5, 5), origin=False)
M = (5.0, 0.0)
p.seg((5, -4), (5, 4), TEXT, 1.1, "6 4", 0.7, "minor axis")
p.ell(M, 5, 4)
for q in ((0.0, 0.0), (10.0, 0.0), (5.0, 4.0), (5.0, -4.0)):
    p.dot(q)
p.dot(M, TEXT, 3.4)
p.lab_auto((0.0, 0.0), "(0, 0)", (-135, -150, 135))
p.lab_auto((10.0, 0.0), "(10, 0)", (-45, -30, 45))
p.lab_auto((5.0, 4.0), "(5, 4)", (60, 45, 120))
p.lab_auto((5.0, -4.0), "(5, " + MINUS + "4)", (-60, -45, -120))
p.lab_auto(M, "M(5, 0)", (45, 30, 60))
dr = p.int_numbers()
emit("exr-kosul-merkez-ii", p,
     f"Köşeleri (0, 0), (10, 0), (5, 4), (5, {MINUS}4) olan elipsin merkezi {em('M')}(5, 0): "
     f"({em('x')} &#8722; 5)<sup>2</sup>/25 + {Y2}/16 = 1.",
     "Ellipse (x-5)2/25+y2/16=1 with vertices (0,0), (10,0), (5,4), (5,-4) and center M(5,0)", dropped=dr)

# ============================================================ exr-teget-12-8
p = Fig((-4, 7), (-3.5, 4.5), 560)
p.axes2((-4, 7), (-3.5, 4.5))
p.ell((0, 0), math.sqrt(12), math.sqrt(8))
P = (2.0, 4 / math.sqrt(3))
ta, tb = (-1.0, 7 / math.sqrt(3)), (6.8, -0.8 / math.sqrt(3))
p.seg(ta, tb, PRACTICE, 2.2, name="tangent")
p.dot(P)
p.lab_auto(P, "P(2, 4/" + SQRT + "3)", (60, 75, 45))
p.lab_line(ta, tb, "x + " + SQRT + "3y " + MINUS + " 6 = 0", (0.8, 0.85, 0.75, 0.9), 6, NAME, PRACTICE, (1,))
dr = p.int_numbers()
emit("exr-teget-12-8", p,
     f"{X2}/12 + {Y2}/8 = 1 elipsinin {em('P')}(2, 4/&#8730;3) noktasındaki teğeti "
     f"{em('x')} + &#8730;3{em('y')} &#8722; 6 = 0.",
     "Ellipse x2/12+y2/8=1 with the tangent x+sqrt3 y-6=0 at P(2, 4/sqrt3)", dropped=dr)

# ============================================================ exr-dogru-irdele-b
p = Fig((-6.5, 6.5), (-6, 6), 560)
p.axes2((-6.5, 6.5), (-6, 6))
p.ell((0, 0), math.sqrt(20), math.sqrt(5))
t1 = p.line_clipped((-6.5, 11.5), (6.5, -1.5), PRACTICE, 2.0, None, "n=5")
t2 = p.line_clipped((-6.5, 1.5), (6.5, -11.5), PRACTICE, 2.0, None, "n=-5")
t3 = p.line_clipped((-6.5, 8.5), (6.5, -4.5), BASE, 1.6, "7 5", "n=2")
p.dot((4.0, 1.0))
p.dot((-4.0, -1.0))
p.lab_auto((4.0, 1.0), "(4, 1)", (45, 60, 30))
p.lab_auto((-4.0, -1.0), "(" + MINUS + "4, " + MINUS + "1)", (-135, -150, -120))
p.lab_seg(t1[0], t1[1], "n = 5", 1, 6, 0.9, NAME, PRACTICE)
p.lab_line(t2[0], t2[1], "n = " + MINUS + "5", (0.85, 0.8, 0.75, 0.7, 0.9), 6, NAME, PRACTICE)
p.lab_seg(t3[0], t3[1], "n = 2", -1, 6, 0.93, NAME, BASE)
dr = p.int_numbers()
emit("exr-dogru-irdele-b", p,
     f"{em('y')} = &#8722;{em('x')} + {em('n')} doğruları {X2}/20 + {Y2}/5 = 1 elipsine {em('n')} = &#177;5 "
     f"iken (4, 1) ve ({MINUS}4, {MINUS}1) noktalarında teğettir; {em('n')} = 2 doğrusu elipsi keser.",
     "Ellipse x2/20+y2/5=1 with the tangents y=-x+5, y=-x-5 at (4,1), (-4,-1) and the secant y=-x+2",
     dropped=dr)

# ============================================================ exr-dis-merkezlik-aci-i
p = Fig((-2.6, 2.6), (-1.6, 1.6), 560)
p.axes2((-2.6, 2.6), (-1.6, 1.6), ticks=0)
p.ell((0, 0), 2, 1)
s3 = math.sqrt(3)
f1, f2, b1, b2 = (s3, 0.0), (-s3, 0.0), (0.0, 1.0), (0.0, -1.0)
p.seg(f1, b1, PRACTICE, 2.0, name="F1B1")
p.seg(f1, b2, PRACTICE, 2.0, name="F1B2")
p.right_angle((0, 0), (1, 0), (0, 1), 9)
p.angle_arc(f1, 150, 210, 44, TEXT, 1.4)
for q in (b1, b2):
    p.dot(q)
p.dot(f1, PRACTICE)
p.dot(f2, PRACTICE)
p.lab(pol(44 / p.ppu, 169, f1), "π/3", 169, 4, NAME)
p.lab_seg(f1, b1, "a", -1, 5, 0.5, NAME + 1, PRACTICE)
p.lab((s3 / 2, 0), "c", -90, 5, NAME + 1)
p.lab_auto(f1, "F_1", (-60, -45, -75))
p.lab_auto(f2, "F_2", (-90, -60, -120))
p.lab_auto(b1, "B_1", (120, 135, 105))
p.lab_auto(b2, "B_2", (-120, -135, -105))
emit("exr-dis-merkezlik-aci-i", p,
     f"{F1} odağı yedek ekseni &#960;/3 açısı altında görür; {em('O')}{F1}{B1} dik üçgeninde "
     f"cos(&#960;/6) = {em('c')}/{em('a')} = {em('e')} = &#8730;3/2.",
     "Ellipse x2/4+y2=1: the focus F1 sees the minor axis B1B2 under the angle pi/3")

# ============================================================ exr-dis-merkezlik-aci-ii
p = Fig((-2.2, 2.2), (-1.4, 1.7), 560)
p.axes2((-2.2, 2.2), (-1.4, 1.7), ticks=0)
p.ell((0, 0), math.sqrt(2), 1)
f1, f2, b1 = (1.0, 0.0), (-1.0, 0.0), (0.0, 1.0)
p.seg(b1, f1, PRACTICE, 2.0, name="B1F1")
p.seg(b1, f2, PRACTICE, 2.0, name="B1F2")
p.right_angle(b1, (1, -1), (-1, -1), 11)
p.right_angle((0, 0), (1, 0), (0, 1), 9)
p.dot(b1)
p.dot(f1, PRACTICE)
p.dot(f2, PRACTICE)
p.lab_seg(b1, f1, "a", 1, 5, 0.55, NAME + 1, PRACTICE)
p.lab((0.5, 0), "c", -90, 5, NAME + 1)
p.lab_auto(f1, "F_1", (-60, -45, -75))
p.lab_auto(f2, "F_2", (-120, -135, -105))
p.lab_auto(b1, "B_1", (60, 45, 120))
emit("exr-dis-merkezlik-aci-ii", p,
     f"{B1}, {F2}{F1} parçasını dik açı altında görür; {em('O')}{B1}{F1} ikizkenar dik üçgeninde "
     f"sin(&#960;/4) = {em('c')}/{em('a')} = {em('e')} = &#8730;2/2.",
     "Ellipse x2/2+y2=1: the vertex B1 sees the segment F2F1 under a right angle")

# ============================================================ exr-kose-dis-merkezlik
p = Fig((-8, 6.5), (-6.5, 4), 560)
p.axes2((-8, 6.5), (-6.5, 4))
M = (-1.0, -1.0)
p.seg((-7, -1), (5, -1), TEXT, 1.1, "6 4", 0.7, "major axis")
p.ell(M, 6, math.sqrt(20))
A = (5.0, -1.0)
f1, f2 = (3.0, -1.0), (-5.0, -1.0)
p.dot(M)
p.dot(A)
p.dot(f1, PRACTICE)
p.dot(f2, PRACTICE)
p.lab_auto(M, "M(" + MINUS + "1, " + MINUS + "1)", (-90, -70, -110))
p.lab_auto(A, "A_1(5, " + MINUS + "1)", (-30, -45, 30))
p.lab_auto(f1, "F_1(3, " + MINUS + "1)", (-90, -70, -110))
p.lab_auto(f2, "F_2(" + MINUS + "5, " + MINUS + "1)", (-90, -70, -110))
dr = p.int_numbers()
emit("exr-kose-dis-merkezlik", p,
     f"Merkezi {em('M')}({MINUS}1, {MINUS}1), uzak köşesi {A1}(5, {MINUS}1), dış merkezliği 2/3 olan elips: "
     f"({em('x')} + 1)<sup>2</sup>/36 + ({em('y')} + 1)<sup>2</sup>/20 = 1.",
     "Ellipse (x+1)2/36+(y+1)2/20=1 with center M(-1,-1), vertex A1(5,-1) and foci (3,-1), (-5,-1)",
     dropped=dr)

# ============================================================ exr-donme-ile-donusum
p = Fig((-4, 4), (-4, 4), 560)
p.axes2((-4, 4), (-4, 4))
p.ell((0, 0), 2, 3, 0, THEORY, 2.4, None, "vertical")
p.ell((0, 0), 3, 2, 0, PRACTICE, 2.4, None, "horizontal")
arc = [pol(3.0, 90 + 90 * k / 60) for k in range(61)]
p.line(arc[:-3], TEXT, 1.4, "5 4")
p.reg_data(arc, "rotation arc")
p.arrow(arc[-4], arc[-1], TEXT, 1.4, 8.0)
p.dot((0.0, 3.0), TEXT, 3.4)
p.dot((-3.0, 0.0), TEXT, 3.4)
p.lab(pol(3.0, 135), "π/2", 135, 6, NAME)
p.lab_auto(ell_pt(80, 2, 3), "9x² + 4y² = 36", (30, 20, 40), 6, NAME, THEORY)
p.lab_auto(ell_pt(-15, 3, 2), "4x² + 9y² = 36", (-40, -30, -50), 6, NAME, PRACTICE)
dr = p.int_numbers()
emit("exr-donme-ile-donusum", p,
     f"9{X2} + 4{Y2} = 36 elipsi başlangıç noktası etrafında &#960;/2 döndürülünce 4{X2} + 9{Y2} = 36 "
     "elipsine gelir; (0, 3) noktası (&#8722;3, 0) noktasına taşınır.",
     "Ellipses 9x2+4y2=36 and 4x2+9y2=36; a quarter turn about the origin carries (0,3) to (-3,0)",
     dropped=dr)


# ===========================================================================
# 3-D cones
# ===========================================================================
ALPHA = math.radians(30)
TANA = math.tan(ALPHA)
HC = 2.0                       # the nappes reach z = +-HC
RC = HC * TANA
AZ, EL = -60.0, 18.0
CAM = Camera(AZ, EL)
DV = CAM.d
DH = (math.cos(math.radians(AZ)), math.sin(math.radians(AZ)), 0.0)    # horizontal, toward the viewer
RT = (-math.sin(math.radians(AZ)), math.cos(math.radians(AZ)), 0.0)   # horizontal, screen right
EZ = (0.0, 0.0, 1.0)


def rho(psi):
    return (math.cos(math.radians(psi)), math.sin(math.radians(psi)), 0.0)


def horiz(deg):
    """Horizontal unit vector at angle deg from the viewer direction DH (toward RT)."""
    return vadd(vscale(math.cos(math.radians(deg)), DH), vscale(math.sin(math.radians(deg)), RT))


def gen_dir(psi, up=True):
    """Unit direction of the generator at azimuth psi (upper nappe if up)."""
    r = rho(psi)
    return vadd(vscale(math.sin(ALPHA), r), vscale(math.cos(ALPHA) * (1 if up else -1), EZ))


def visible(P):
    """Outer side of the cone at P faces the viewer."""
    g = (P[0], P[1], -P[2] * TANA * TANA)
    return vdot(g, DV) > 0


def pr(P):
    X, Y, _ = CAM.project(P)
    return (X, Y)


def hull(pts):
    pts = sorted(set(pts))
    if len(pts) < 3:
        return pts

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lower, upper = [], []
    for q in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], q) <= 0:
            lower.pop()
        lower.append(q)
    for q in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], q) <= 0:
            upper.pop()
        upper.append(q)
    return lower[:-1] + upper[:-1]


def draw_runs(p, pts3, color, width, name, force_solid=False):
    """Space polyline: visible runs solid, hidden runs dashed."""
    runs, cur, cur_vis = [], [], None
    for P in pts3:
        v = True if force_solid else visible(P)
        if cur and v != cur_vis:
            runs.append((cur_vis, cur + [pr(P)]))
            cur = []
        cur.append(pr(P))
        cur_vis = v
    if cur:
        runs.append((cur_vis, cur))
    for v, r in runs:
        if len(r) >= 2:
            p.line(r, color, width, None if v else "5 4", 1.0 if v else 0.75)
            p.reg_data(r, name)


def cone_panel(x0, y0, width, xr=(-1.85, 1.85), yr=(-2.5, 2.5)):
    return Fig(xr, yr, width, x0, y0)


def draw_cone(p, scale_note=None):
    n = 180
    up_rim = [(RC * math.cos(2 * math.pi * k / n), RC * math.sin(2 * math.pi * k / n), HC) for k in range(n + 1)]
    lo_rim = [(q[0], q[1], -HC) for q in up_rim]
    V0 = (0.0, 0.0, 0.0)
    for rim in (up_rim, lo_rim):
        h = hull([pr(q) for q in rim] + [pr(V0)])
        p.polygon(h + [h[0]], TEXT, 0.05, stroke="none")
    # axis
    p.line([pr((0, 0, -HC - 0.25)), pr((0, 0, HC + 0.25))], TEXT, 1.0, "3 3", 0.55)
    p.reg_data([pr((0, 0, -HC - 0.25)), pr((0, 0, HC + 0.25))], "axis")
    # rims: the upper one is seen from above, the lower one has a hidden back half
    draw_runs(p, up_rim, TEXT, 1.4, "rim", force_solid=True)
    draw_runs(p, lo_rim, TEXT, 1.4, "rim")
    # silhouette generators
    k = TANA * math.tan(math.radians(EL))
    for sgn, z in ((1, HC), (-1, -HC)):
        psi0 = math.degrees(math.acos(sgn * k))
        for psi in (AZ + psi0, AZ - psi0):
            q = (RC * math.cos(math.radians(psi)), RC * math.sin(math.radians(psi)), z)
            p.line([pr(V0), pr(q)], TEXT, 1.4)
            p.reg_data([pr(V0), pr(q)], "generator")


def plane_patch(p, C, e1, e2, s1, s2, color=BASE, opacity=0.16):
    corners = [vadd(C, vadd(vscale(a, e1), vscale(b, e2))) for a, b in ((s1[0], s2[0]), (s1[1], s2[0]),
                                                                         (s1[1], s2[1]), (s1[0], s2[1]))]
    pts = [pr(q) for q in corners]
    p.polygon(pts, color, opacity, stroke=color, width=1.0)
    p.reg_data(pts + [pts[0]], "plane edge")
    return corners


def section(n_vec, k, samples=720):
    """Runs of the cone curve {P on the cone : n.P = k}, |z| <= HC, as lists of space points."""
    runs, cur = [], []
    for i in range(samples + 1):
        psi = 360.0 * i / samples
        r = rho(psi)
        # P(t) = t * (tan(a) r + ez), t = z
        den = TANA * vdot(n_vec, r) + n_vec[2]
        ok = False
        if abs(den) > 1e-9:
            t = k / den
            if abs(t) <= HC:
                ok = True
                P = vadd(vscale(t * TANA, r), vscale(t, EZ))
                if cur and (P[2] > 0) != (cur[-1][2] > 0):
                    runs.append(cur)
                    cur = []
                cur.append(P)
        if not ok and cur:
            runs.append(cur)
            cur = []
    if cur:
        runs.append(cur)
    # join the run that wraps through psi = 0
    if len(runs) > 1 and runs[0] and runs[-1] and vnorm2(vsub(runs[0][0], runs[-1][-1])) < 1e-3:
        runs[0] = runs[-1] + runs[0]
        runs.pop()
    return runs


def vnorm2(v):
    return vdot(v, v)


def vertex_label(p, ang=180):
    p.dot(pr((0, 0, 0)), TEXT, 3.4)
    p.lab_auto(pr((0, 0, 0)), "V", (ang, 180 - ang, ang + 15, ang - 15, 165 - ang, 195 - ang), 8, NAME,
               grow=tuple(range(0, 30, 3)))


def frak_side(p, corners, side="right"):
    """Plane name beside the leftmost or rightmost projected corner of a patch."""
    pts = [pr(q) for q in corners]
    q = max(pts, key=lambda t: t[0]) if side == "right" else min(pts, key=lambda t: t[0])
    p.frak(q, "", 0 if side == "right" else 180, 6)


def panel_heading(p, s):
    p.lab_px(p.x0 + p.w / 2, p.y0 + p.h + 26, s, NAME, TEXT, "middle", bold=True, raw=True)


# ---------------------------------------------------------------- konik-cember-elips
PW = 300
pa = cone_panel(40, 20, PW)
pb = cone_panel(40 + PW + 20, 20, PW)
for p in (pa, pb):
    draw_cone(p)
# circle: horizontal plane z = 1.25
zc = 1.25
e1, e2 = horiz(35), horiz(125)
cs = plane_patch(pa, (0, 0, zc), e1, e2, (-1.25, 1.25), (-1.25, 1.25))
for run in section(EZ, zc):
    draw_runs(pa, run + [run[0]], PRACTICE, 2.6, "conic")
frak_side(pa, cs)
vertex_label(pa)
panel_heading(pa, "çember")
# ellipse: plane tilted 20 degrees from the horizontal
w = horiz(70)
nE = vunit(vadd(vscale(math.cos(math.radians(20)), EZ), vscale(math.sin(math.radians(20)), w)))
CE = (0.0, 0.0, 1.2)
u1 = vunit(vsub(w, vscale(vdot(w, nE), nE)))
u2 = vcross(nE, u1)
cs = plane_patch(pb, CE, u1, u2, (-1.35, 1.35), (-1.3, 1.3))
for run in section(nE, vdot(nE, CE)):
    draw_runs(pb, run + [run[0]], PRACTICE, 2.6, "conic")
frak_side(pb, cs)
vertex_label(pb)
panel_heading(pb, "elips")
emit_multi("konik-cember-elips", [pa, pb], 2 * PW + 100, int(pa.h + 70),
           "Eksene dik bir düzlem koniyi çember boyunca, ana doğrulardan daha yatık bir düzlem ise "
           "kapalı bir eğri olan elips boyunca keser.",
           "A double cone cut by a plane perpendicular to its axis (circle) and by a slightly tilted "
           "plane (ellipse)")

# ---------------------------------------------------------------- konik-parabol-hiperbol
pa = cone_panel(40, 20, PW)
pb = cone_panel(40 + PW + 20, 20, PW)
for p in (pa, pb):
    draw_cone(p)
# parabola: plane parallel to the generator at azimuth psig
psig = AZ + 210
nP = vsub(vscale(math.cos(ALPHA), rho(psig)), vscale(math.sin(ALPHA), EZ))
zv = 0.55                                  # height of the parabola's vertex
sv = zv / math.cos(ALPHA)
Vp = vscale(sv, gen_dir(psig + 180))        # vertex of the parabola, on the opposite generator
kP = vdot(nP, Vp)
g = gen_dir(psig)
tP = (-math.sin(math.radians(psig)), math.cos(math.radians(psig)), 0.0)
draw_runs(pa, [vscale(s, g) for s in [HC / math.cos(ALPHA) * k / 60 for k in range(61)]], BASE, 1.8, "parallel")
cs = plane_patch(pa, Vp, g, tP, (-0.15, 1.9), (-1.3, 1.3))
for run in section(nP, kP):
    draw_runs(pa, run, PRACTICE, 2.6, "conic")
frak_side(pa, cs)
vertex_label(pa)
panel_heading(pa, "parabol")
# hyperbola: vertical plane at distance delta from the axis
wH = horiz(25)
delta = 0.42
tH = vcross(EZ, wH)
CH = vscale(delta, wH)
cs = plane_patch(pb, CH, tH, EZ, (-1.3, 1.3), (-2.15, 2.15))
for run in section(wH, delta):
    draw_runs(pb, run, PRACTICE, 2.6, "conic")
frak_side(pb, cs)
vertex_label(pb)
panel_heading(pb, "hiperbol")
emit_multi("konik-parabol-hiperbol", [pa, pb], 2 * PW + 100, int(pa.h + 70),
           "Bir ana doğruya paralel düzlem koniyi kapanmayan tek kollu bir eğri, parabol boyunca keser; "
           "eksene paralel düzlem ise iki parçayı birden keser ve iki kollu hiperbolü verir.",
           "A double cone cut by a plane parallel to a generator (parabola) and by a plane parallel to "
           "the axis (hyperbola)")

# ---------------------------------------------------------------- konik-yozuk
PW3 = 210
panels = [cone_panel(30 + k * (PW3 + 16), 20, PW3) for k in range(3)]
for p in panels:
    draw_cone(p)
pa, pb, pc = panels
# point: horizontal plane through the vertex
e1, e2 = horiz(35), horiz(125)
cs = plane_patch(pa, (0, 0, 0), e1, e2, (-1.25, 1.25), (-1.25, 1.25))
pa.dot(pr((0, 0, 0)), PRACTICE, 5.0)
pa.lab(pr((0, 0, 0)), "V", 180, 13, NAME)
frak_side(pa, cs)
panel_heading(pa, "nokta")
# line: tangent plane along a generator
psi0 = AZ + 50
g0 = gen_dir(psi0)
t0 = (-math.sin(math.radians(psi0)), math.cos(math.radians(psi0)), 0.0)
L = HC / math.cos(ALPHA)
cs = plane_patch(pb, (0, 0, 0), g0, t0, (-L, L), (-0.55, 0.55))
pb.line([pr(vscale(-L, g0)), pr(vscale(L, g0))], PRACTICE, 2.8)
pb.reg_data([pr(vscale(-L, g0)), pr(vscale(L, g0))], "conic")
vertex_label(pb, 0)
frak_side(pb, cs, "left")
panel_heading(pb, "doğru")
# two lines: plane through the axis
wA = horiz(15)
tA = vcross(EZ, wA)
cs = plane_patch(pc, (0, 0, 0), tA, EZ, (-1.35, 1.35), (-2.15, 2.15))
psiA = math.degrees(math.atan2(tA[1], tA[0]))
for psi in (psiA, psiA + 180):
    ends = [vscale(HC / math.cos(ALPHA), gen_dir(psi, True)), vscale(HC / math.cos(ALPHA), gen_dir(psi + 180, False))]
    pc.line([pr(ends[0]), pr(ends[1])], PRACTICE, 2.8)
    pc.reg_data([pr(ends[0]), pr(ends[1])], "conic")
pc.dot(pr((0, 0, 0)), TEXT, 3.4)
pc.lab(pr((0, 0, 0)), "V", 0, 13, NAME)
frak_side(pc, cs)
panel_heading(pc, "kesişen iki doğru")
emit_multi("konik-yozuk", panels, 3 * PW3 + 92, int(pa.h + 70),
           "Düzlem koninin köşesinden geçerse yozlaşmış konikler çıkar: yalnız köşe {V}, bir ana doğru "
           "ya da köşede kesişen iki ana doğru.".replace("{V}", em("V")),
           "Degenerate conics: a plane through the vertex meets the cone in the vertex only, along one "
           "generator (tangent plane) or in two generators")


# ---------------------------------------------------------------------------
for name, content in OUT.items():
    with io.open(OUT_DIR / f"analytic-elp-{name}.md", "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
print(f"generated {len(OUT)} figures:", ", ".join(OUT))
