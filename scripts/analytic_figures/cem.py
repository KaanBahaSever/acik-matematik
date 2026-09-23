# -*- coding: utf-8 -*-
"""
Figures for the "Cember" chapter of Analitik Geometri
(dersler/analitik-geometri/cember.qmd).

The figures are NOT produced at build time. Run

    python scripts/analytic_figures/cem.py
    python scripts/center_figures.py "analytic-cem-*.md" --keep-width

and paste each scripts/_figures/analytic-cem-<name>.md block in place of its
placeholder. Figures go INSIDE the box they explain (theorem, proof, example,
solution or exercise), never inside a definition box: a figure that
illustrates a definition sits directly below that box.

Every panel has the same number of pixels per unit on both axes, so circles
are round and right angles look right. Labels are placed by direction (an
angle and a gap) so that their estimated box never touches the point they
name; audit() then reports any label box that crosses a drawn line or
another label, and tick numbers that would collide are left out.

Captions are Turkish (they are shown on the site); aria labels are ASCII.
"""
import io
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, TEXT, BG, THEORY, PRACTICE, BASE, fmt  # noqa: E402
from check_figure_labels import text_width  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
OUT = {}

MINUS = "−"
SQRT = "√"
CAP = "∩"

LETTERS = "A-Za-zδωℓ"          # latin, delta, omega, script l
TOKEN = re.compile(r"S¹([₁₂]?)|[%s]+|[^%s]+" % (LETTERS, LETTERS))
SUBS = {"₁": "1", "₂": "2"}


def mk(s, size):
    """Label markup: letters italic, 'S¹', 'S¹₁', 'S¹₂' as a stacked sup/sub."""
    out = []
    for m in TOKEN.finditer(s):
        t = m.group(0)
        if t.startswith("S¹"):
            small = round(0.7 * size, 1)
            up = round(0.42 * size, 1)
            out.append('<tspan font-style="italic">S</tspan>'
                       f'<tspan font-size="{small}" dy="-{up}">1</tspan>')
            if m.group(1):
                back = round(0.52 * small, 1)
                down = round(0.78 * size, 1)
                out.append(f'<tspan font-size="{small}" dx="-{back}" dy="{down}">{SUBS[m.group(1)]}</tspan>'
                           f'<tspan dy="-{round(down - up, 1)}">&#8203;</tspan>')
            else:
                out.append(f'<tspan dy="{up}">&#8203;</tspan>')
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
    """Is the point marker (cx, cy, r) within m pixels of the box?"""
    cx, cy, r = dot
    dx = max(box[0] - cx, 0, cx - box[2])
    dy = max(box[1] - cy, 0, cy - box[3])
    return math.hypot(dx, dy) < r + m


def boxes_meet(a, b, m=0.0):
    return not (a[2] + m <= b[0] or b[2] + m <= a[0] or a[3] + m <= b[1] or b[3] + m <= a[1])


class Fig(Plot):
    """Equal-aspect panel that remembers what it drew, for the label audit."""

    def __init__(self, xr, yr, width, x0=60, y0=50):
        ppu = width / (xr[1] - xr[0])
        super().__init__(x0, y0, width, (yr[1] - yr[0]) * ppu, xr, yr)
        self.ppu = ppu
        self.segs = []      # (x1, y1, x2, y2, name) in pixels
        self.boxes = []     # (box, text)
        self.dots = []      # (cx, cy, r) of point markers
        self.rot_boxes = []  # bounding boxes of rotated labels (kept clear of tick numbers)

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

    def circ(self, c, r, color=THEORY, width=2.2, name="circle"):
        self.circle(c[0], c[1], r, color, width)
        n = 240
        self.reg_data([(c[0] + r * math.cos(2 * math.pi * k / n), c[1] + r * math.sin(2 * math.pi * k / n))
                       for k in range(n + 1)], name)

    def dot(self, pt, color=TEXT, r=4.2):
        self.points([pt], color, r)
        X, Y = self.X(pt[0]), self.Y(pt[1])
        self.dots.append((X, Y, r))

    def hollow_dot(self, pt, color=TEXT, r=4.2):
        X, Y = self.X(pt[0]), self.Y(pt[1])
        self.add(f'<circle cx="{X:.1f}" cy="{Y:.1f}" r="{r}" fill="{BG}" stroke="{color}" stroke-width="1.7"/>')
        self.dots.append((X, Y, r))

    def right_angle(self, v, d1, d2, s=10.0, color=TEXT, width=1.3):
        """Square corner marker at data point v between data directions d1 and d2."""
        X, Y = self.X(v[0]), self.Y(v[1])
        u = unit((d1[0], -d1[1]))
        w = unit((d2[0], -d2[1]))
        pts = [(X + s * u[0], Y + s * u[1]), (X + s * (u[0] + w[0]), Y + s * (u[1] + w[1])),
               (X + s * w[0], Y + s * w[1])]
        d = "M" + " L".join(f"{a:.1f},{b:.1f}" for a, b in pts)
        self.add(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}" opacity="0.85"/>')
        self.reg(pts, "right angle")

    # -- labels --------------------------------------------------------------
    def _box(self, x, y, markup, size, anchor):
        w = text_width(markup, size)
        x0 = x - w / 2 if anchor == "middle" else x - w if anchor == "end" else x
        return (x0, y - 0.78 * size, x0 + w, y + 0.22 * size)

    def lab_px(self, x, y, s, size=14, color=TEXT, anchor="start", bold=False, raw=False, opacity=None):
        markup = s if raw else mk(s, size)
        weight = ' font-weight="600"' if bold else ""
        op = f' opacity="{opacity}"' if opacity is not None else ""
        self.add(f'<text x="{x:.1f}" y="{y:.1f}" fill="{color}" font-size="{size}" '
                 f'text-anchor="{anchor}"{weight}{op}>{markup}</text>')
        box = self._box(x, y, markup, size, anchor)
        self.boxes.append((box, s))
        return box

    def lab(self, pt, s, ang, dist=7.0, size=14, color=TEXT, bold=False):
        """Put label s beside data point pt, in direction ang (degrees, y up),
        so that its whole box stays at least dist pixels away from the point."""
        markup = mk(s, size)
        w, h = text_width(markup, size), size
        c, sn = math.cos(math.radians(ang)), math.sin(math.radians(ang))
        ext = w / 2 * abs(c) + h / 2 * abs(sn)
        cx = self.X(pt[0]) + (dist + ext) * c
        cy = self.Y(pt[1]) - (dist + ext) * sn
        return self.lab_px(cx, cy + 0.28 * size, s, size, color, "middle", bold)

    def lab_along(self, a, b, t, s, off=8.0, size=14, color=TEXT):
        """Label written parallel to segment ab (data points), centered at parameter t,
        lifted off pixels to the upper side of the segment."""
        ax, ay, bx, by = self.X(a[0]), self.Y(a[1]), self.X(b[0]), self.Y(b[1])
        if bx < ax:
            ax, ay, bx, by = bx, by, ax, ay
        ux, uy = unit((bx - ax, by - ay))
        nx, ny = uy, -ux                      # screen normal pointing up
        px, py = ax + t * (bx - ax) + nx * off, ay + t * (by - ay) + ny * off
        ang = math.degrees(math.atan2(uy, ux))
        markup = mk(s, size)
        self.add(f'<text x="{px:.1f}" y="{py:.1f}" fill="{color}" font-size="{size}" text-anchor="middle" '
                 f'transform="rotate({ang:.2f} {px:.1f} {py:.1f})">{markup}</text>')
        w = text_width(markup, size)
        corners = [(-w / 2, 0.22 * size), (w / 2, 0.22 * size), (-w / 2, -0.78 * size), (w / 2, -0.78 * size)]
        pts = [(px + cx_ * ux - cy_ * uy, py + cx_ * uy + cy_ * ux) for cx_, cy_ in corners]
        self.rot_boxes.append((min(q[0] for q in pts), min(q[1] for q in pts),
                               max(q[0] for q in pts), max(q[1] for q in pts)))

    def title(self, s, size=14, dy=34, raw=False):
        """Centered line under the panel."""
        return self.lab_px(self.x0 + self.w / 2, self.y0 + self.h + dy, s, size, TEXT, "middle", raw=raw)

    def heading(self, s, size=14, dy=-18):
        return self.lab_px(self.x0 + self.w / 2, self.y0 + dy, s, size, TEXT, "middle", bold=True, raw=True)

    # -- axes ----------------------------------------------------------------
    def axes2(self, xr, yr, origin=True):
        ox, oy = self.X(0), self.Y(0)
        xa, xb = self.X(xr[0]), self.X(xr[1]) + 12
        ya, yb = self.Y(yr[0]), self.Y(yr[1]) - 12
        a = [f'<g stroke="{TEXT}" stroke-width="1.1" opacity="0.55" fill="{TEXT}">',
             f'<line x1="{xa:.1f}" y1="{oy:.1f}" x2="{xb - 6:.1f}" y2="{oy:.1f}"/>',
             f'<line x1="{ox:.1f}" y1="{ya:.1f}" x2="{ox:.1f}" y2="{yb + 6:.1f}"/>',
             f'<polygon points="{xb:.1f},{oy:.1f} {xb - 9:.1f},{oy - 3.8:.1f} {xb - 9:.1f},{oy + 3.8:.1f}" stroke="none"/>',
             f'<polygon points="{ox:.1f},{yb:.1f} {ox - 3.8:.1f},{yb + 9:.1f} {ox + 3.8:.1f},{yb + 9:.1f}" stroke="none"/>']
        for t in range(math.ceil(xr[0]), math.floor(xr[1]) + 1):
            if t:
                a.append(f'<line x1="{self.X(t):.1f}" y1="{oy - 3:.1f}" x2="{self.X(t):.1f}" y2="{oy + 3:.1f}"/>')
        for t in range(math.ceil(yr[0]), math.floor(yr[1]) + 1):
            if t:
                a.append(f'<line x1="{ox - 3:.1f}" y1="{self.Y(t):.1f}" x2="{ox + 3:.1f}" y2="{self.Y(t):.1f}"/>')
        a.append('</g>')
        self.add("\n  ".join(a))
        self.reg([(xa, oy), (xb, oy)], "x axis")
        self.reg([(ox, ya), (ox, yb)], "y axis")
        self.lab_px(xb + 6, oy + 5, "x", 14, TEXT, "start")
        self.lab_px(ox + 9, yb + 6, "y", 14, TEXT, "start")
        if origin:
            self.lab_px(ox - 6, oy + 16, "O", 13, TEXT, "end")

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
                box = self._box(x, y, s, 11, anchor)
                own = "x axis" if axis == "x" else "y axis"
                hit = any(seg_hits_box(a, b, c, d, box, 2.5) for a, b, c, d, n in self.segs if n != own)
                hit = hit or any(boxes_meet(box, b, 2.0) for b, _ in self.boxes)
                hit = hit or any(dot_near(box, d, 2.0) for d in self.dots)
                hit = hit or any(boxes_meet(box, b, 2.0) for b in self.rot_boxes)
                if hit:
                    dropped.append(f"{axis}={s}")
                    continue
                self.add(f'<text x="{x:.1f}" y="{y:.1f}" fill="{TEXT}" font-size="11" '
                         f'text-anchor="{anchor}" opacity="0.72">{s}</text>')
                self.boxes.append((box, s))
        return dropped

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


def empty_set(p, box, size=14):
    """Draw an empty-set sign right after a text box (the font lacks the glyph)."""
    r = 0.36 * size
    cx = box[2] + 1 + r
    cy = box[3] - 0.22 * size - 0.36 * size
    p.add(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="none" stroke="{TEXT}" stroke-width="1.3"/>')
    p.add(f'<line x1="{cx - 1.25 * r:.1f}" y1="{cy + 1.45 * r:.1f}" x2="{cx + 1.25 * r:.1f}" '
          f'y2="{cy - 1.45 * r:.1f}" stroke="{TEXT}" stroke-width="1.3"/>')


def cap_title(p, left, size=14, dy=34, empty=False):
    """Centered 'S¹ ∩ d = {...}' line; with empty=True the right side is a drawn empty set."""
    if not empty:
        return p.title(left, size, dy)
    x_end = p.x0 + p.w / 2 + 2
    box = p.lab_px(x_end, p.y0 + p.h + dy, left.rstrip(), size, TEXT, "end")
    empty_set(p, (box[0], box[1], box[2] + 8, box[3]), size)


def em(s):
    return f"<em>{s}</em>"


S1 = "<em>S</em><sup>1</sup>"
S11 = "<em>S</em><sup>1</sup><sub>1</sub>"
S12 = "<em>S</em><sup>1</sup><sub>2</sub>"


def emit(name, p, caption, aria, css="ders-grafik", extra_bottom=0, dropped=()):
    p.audit(name, dropped)
    W, H = canvas(p, extra_bottom)
    OUT[name] = figure(W, H, [p], caption, css, aria)


def pol(r, deg, c=(0.0, 0.0)):
    return (c[0] + r * math.cos(math.radians(deg)), c[1] + r * math.sin(math.radians(deg)))


def mid(a, b):
    return ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)


def angle_of(v):
    return math.degrees(math.atan2(v[1], v[0]))


# ============================================================ cember-tanimi
p = Fig((-4.2, 4.2), (-4.0, 4.0), 480)
O0 = (0.0, 0.0)
p.circ(O0, 3, THEORY, 2.4, "circle")
PS = [((2.60, 1.50), 30, "P₁"), ((-2.30, 1.93), 140, "P₂"), ((-1.03, -2.82), 250, "P₃")]
for pt, a, _ in PS:
    p.seg(O0, pt, TEXT, 1.4, name="radius")
for pt, a, s in PS:
    p.lab(mid(O0, pt), "r", a - 90, 6, 14)
    p.dot(pt)
    p.lab(pt, s, a, 8, 15)
p.dot(O0)
p.lab(O0, "M(a, b)", 185, 14, 14)
p.lab(pol(3, -45), "S¹", -45, 9, 16, THEORY)
emit("cember-tanimi", p,
     f"Merkezi {em('M')}, yarıçapı {em('r')} olan {S1} çemberi. Çemberin her noktası merkezden "
     f"aynı {em('r')} uzaklığındadır.",
     "A circle S1 with center M and three points P1, P2, P3 on it, each joined to M by a radius r")

# ============================================================ cember-dik-ucgen
p = Fig((-1, 7), (-1, 5), 480)
p.axes2((-1, 7), (-1, 5))
M = (3.0, 2.0)
P = pol(2.5, 40, M)
Q = (P[0], M[1])
p.circ(M, 2.5, THEORY, 2.2)
p.seg(M, Q, TEXT, 1.4, "5 4", name="x - a")
p.seg(Q, P, TEXT, 1.4, "5 4", name="y - b")
p.right_angle(Q, (-1, 0), (0, 1), 10)
p.seg(M, P, TEXT, 2.6, name="MP")
p.dot(M)
p.dot(P)
p.lab(mid(M, P), "r", 130, 6, 15)
p.lab(mid(M, Q), "x " + MINUS + " a", 270, 6, 14)
p.lab((Q[0], 2.78), "y " + MINUS + " b", 180, 6, 14)
p.lab(P, "P(x, y)", 45, 7, 14)
p.lab(M, "M(a, b)", 225, 7, 14)
p.lab(pol(2.5, 135, M), "S¹", 135, 8, 16, THEORY)
emit("cember-dik-ucgen", p,
     f"{em('P')}({em('x')}, {em('y')}) ile {em('M')}({em('a')}, {em('b')}) arasındaki uzaklık, dik kenarları "
     f"|{em('x')} &#8722; {em('a')}| ve |{em('y')} &#8722; {em('b')}| olan dik üçgenin hipotenüsüdür; "
     f"{em('P')} çember üzerindeyse bu uzaklık {em('r')}'dir.",
     "Circle with center M(a,b) and a point P(x,y) on it; the right triangle with legs x-a and y-b "
     "and hypotenuse r")

# ============================================================ standart-denklem-ornegi
p = Fig((-6, 2), (-1, 9), 440)
p.axes2((-6, 2), (-1, 9))
M = (-2.0, 5.0)
p.circ(M, 3, THEORY, 2.2)
p.seg(M, (1, 5), TEXT, 1.8, name="radius")
for pt in ((1, 5), (-5, 5), (-2, 8), (-2, 2)):
    p.dot(pt)
p.dot(M)
p.lab(M, "M(" + MINUS + "2, 5)", 215, 7, 14)
p.lab(mid(M, (1, 5)), "3", 90, 5, 15)
p.lab((1, 5), "(1, 5)", 0, 8, 14)
p.lab((-5, 5), "(" + MINUS + "5, 5)", 180, 8, 14)
p.lab((-2, 8), "(" + MINUS + "2, 8)", 90, 7, 14)
p.lab((-2, 2), "(" + MINUS + "2, 2)", 270, 7, 14)
p.lab(pol(3, 38, M), "S¹", 38, 10, 16, THEORY)
dr = p.numbers((-6, -4, -2, 2), (2, 4, 6, 8))
emit("standart-denklem-ornegi", p,
     f"Merkezi {em('M')}(&#8722;2, 5), yarıçapı 3 olan çember: "
     f"({em('x')} + 2)<sup>2</sup> + ({em('y')} &#8722; 5)<sup>2</sup> = 9. Merkezden dört yöne 3 birim "
     "gidilerek çemberin dört noktası bulunur.",
     "Circle with center M(-2,5) and radius 3 with the points (1,5), (-5,5), (-2,8), (-2,2) on it",
     dropped=dr)

# ============================================================ genel-denklem-ornegi
p = Fig((-3, 9), (-10, 2), 480)
p.axes2((-3, 9), (-10, 2), origin=False)
M = (3.0, -4.0)
p.circ(M, 5, THEORY, 2.2)
p.seg(M, (0, 0), TEXT, 2.6, name="MO")
for pt in ((0, 0), (6, 0), (0, -8)):
    p.dot(pt)
p.dot(M)
p.lab(M, "M(3, " + MINUS + "4)", 0, 8, 14)
p.lab((0, 0), "O", 135, 6, 14)
p.lab((6, 0), "(6, 0)", 45, 6, 14)
p.lab((0, -8), "(0, " + MINUS + "8)", 195, 10, 14)
p.lab(mid(M, (0, 0)), "5", angle_of((-3, 4)) + 90, 6, 15)
p.lab(pol(5, -45, M), "S¹", -45, 8, 16, THEORY)
dr = p.numbers((-2, 2, 4, 6, 8), (-8, -6, -4, -2, 2))
emit("genel-denklem-ornegi", p,
     f"{em('x')}<sup>2</sup> + {em('y')}<sup>2</sup> &#8722; 6{em('x')} + 8{em('y')} = 0 çemberinin merkezi "
     f"{em('M')}(3, &#8722;4), yarıçapı 5'tir. {em('F')} = 0 olduğundan çember orijinden geçer; eksenleri "
     "(6, 0) ve (0, &#8722;8) noktalarında da keser.",
     "Circle with center M(3,-4) and radius 5 through the origin, (6,0) and (0,-8)", dropped=dr)

# ============================================================ cap-uclari
p = Fig((-6, 8), (-4, 10), 480)
p.axes2((-6, 8), (-4, 10))
M = (1.0, 3.0)
A, B = (5.0, -1.0), (-3.0, 7.0)
R = math.sqrt(32)
p.circ(M, R, THEORY, 2.2)
p.seg(A, B, PRACTICE, 3.0, name="AB")
for pt in (A, B, M):
    p.dot(pt)
p.lab(A, "A(5, " + MINUS + "1)", -45, 7, 14)
p.lab(B, "B(" + MINUS + "3, 7)", 135, 7, 14)
p.lab(M, "M(1, 3)", 45, 7, 14)
p.lab(mid(M, A), "4" + SQRT + "2", 45, 6, 14, PRACTICE)
p.lab(pol(R, 60, M), "S¹", 60, 8, 16, THEORY)
dr = p.numbers((-4, -2, 2, 4, 6), (-2, 2, 4, 6, 8))
emit("cap-uclari", p,
     f"Çapın orta noktası merkezdir: {em('M')}(1, 3). Yarıçap |{em('MA')}| = 4&#8730;2 olduğundan çemberin "
     f"denklemi ({em('x')} &#8722; 1)<sup>2</sup> + ({em('y')} &#8722; 3)<sup>2</sup> = 32'dir.",
     "Circle with diameter AB from A(5,-1) to B(-3,7) and center M(1,3), radius 4 sqrt 2", dropped=dr)


# ============================================================ merkez-dogru-uzerinde (common parts)
def d_line(x):
    return (x - 11) / 3


def perp_line(x):
    return (11 - 6 * x) / 4


def blue_line_with_label(p):
    a, b = (-3, d_line(-3)), (10, d_line(10))
    p.seg(a, b, THEORY, 2.0, name="d")
    # written along d, above it, between M and the right edge (clear of the circle in step 2)
    p.lab_along(a, b, 0.66, "x " + MINUS + " 3y " + MINUS + " 11 = 0", 7, 14, THEORY)


# ============================================================ merkez-dogru-uzerinde-adim1
p = Fig((-3, 10), (-9, 5), 470)
p.axes2((-3, 10), (-9, 5))
A, B = (2.0, 3.0), (-1.0, 1.0)
N = (0.5, 2.0)
M = (3.5, -2.5)
blue_line_with_label(p)
p.seg((-1.5, 5), ((11 + 36) / 6, -9), BASE, 2.0, "7 5", name="perp bisector")
p.seg(A, B, TEXT, 1.4, name="AB")
p.right_angle(N, (3, 2), (-2, 3), 10)
p.dot(A)
p.dot(B)
p.hollow_dot(N)
p.dot(M, PRACTICE, 5)
p.lab(A, "A(2, 3)", 45, 7, 14)
p.lab(B, "B(" + MINUS + "1, 1)", 180, 8, 14)
p.lab(N, "N", -11, 12, 14)
p.lab_px(p.X(M[0]) + 16, p.Y(M[1]) + 15, "M(7/2, " + MINUS + "5/2)", 14, PRACTICE, "start")
p.lab((-1.5, 5), "6x + 4y = 11", 180, 8, 14, BASE)
dr = p.numbers((-2, 2, 4, 6, 8, 10), (-8, -6, -4, -2, 2, 4))
emit("merkez-dogru-uzerinde-adim1", p,
     f"{em('A')} ile {em('B')}'ye eşit uzaklıktaki noktalar, {em('AB')}'nin orta noktası {em('N')}'den geçen "
     f"dik doğru 6{em('x')} + 4{em('y')} = 11'dir. Merkez hem bu doğru hem de {em('x')} &#8722; 3{em('y')} "
     f"&#8722; 11 = 0 doğrusu üzerinde olduğundan ikisinin kesişimidir.",
     "The perpendicular bisector 6x+4y=11 of AB meets the line x-3y-11=0 at the center M(7/2,-5/2)",
     dropped=dr)

# ============================================================ merkez-dogru-uzerinde-adim2
p = Fig((-3, 10), (-9, 5), 470)
p.axes2((-3, 10), (-9, 5))
R = math.sqrt(65 / 2)
blue_line_with_label(p)
p.circ(M, R, PRACTICE, 2.2)
p.seg(M, A, TEXT, 1.4, "5 4", name="MA")
p.seg(M, B, TEXT, 1.4, "5 4", name="MB")
p.dot(A)
p.dot(B)
p.dot(M, PRACTICE, 4.6)
p.lab(M, "M(7/2, " + MINUS + "5/2)", -45, 7, 14, PRACTICE)
p.lab(A, "A(2, 3)", 45, 7, 14)
p.lab(B, "B(" + MINUS + "1, 1)", 180, 8, 14)
p.lab(mid(M, B), "r", angle_of((B[0] - M[0], B[1] - M[1])) + 90, 6, 15)
p.lab(pol(R, 225, M), "S¹", 225, 8, 16, PRACTICE)
dr = p.numbers((-2, 2, 4, 6, 8, 10), (-8, -6, -4, -2, 2, 4))
emit("merkez-dogru-uzerinde-adim2", p,
     f"Merkezi {em('M')}(7/2, &#8722;5/2) ve yarıçapı &#8730;(65/2) olan çember {em('A')} ile {em('B')}'den "
     f"geçer; merkezi {em('x')} &#8722; 3{em('y')} &#8722; 11 = 0 doğrusu üzerindedir.",
     "Circle with center M(7/2,-5/2) on the line x-3y-11=0 passing through A(2,3) and B(-1,1)",
     dropped=dr)

# ============================================================ dogru-cember-iki-nokta
p = Fig((-3, 3), (-3, 3), 440)
M = (0.0, 0.0)
p.circ(M, 2, THEORY, 2.4)
p.seg(M, (2, 0), TEXT, 1.4, name="radius")
p.seg((-2, -3), (1, 3), TEXT, 2.0, name="d")
x1 = (-4 + math.sqrt(76)) / 10
x2 = (-4 - math.sqrt(76)) / 10
A1, A2 = (x1, 2 * x1 + 1), (x2, 2 * x2 + 1)
H = (-0.4, 0.2)
p.seg(M, H, TEXT, 1.5, "4 3", name="MH")
p.right_angle(H, (0.4, -0.2), (1, 2), 8)
for pt in (A1, A2, M, H):
    p.dot(pt, TEXT, 4.2 if pt != H else 3.4)
p.lab(A1, "A₁", 115, 7, 15)
p.lab(A2, "A₂", 192, 7, 15)
p.lab(H, "H", 135, 6, 14)
p.lab(M, "M", -45, 6, 15)
p.lab(mid(M, H), "δ", 243.4, 6, 15)
p.lab((1, 0), "r", 270, 5, 15)
p.lab((-2, -3), "d", 180, 8, 15)
p.lab(pol(2, -45), "S¹", -45, 8, 16, THEORY)
cap_title(p, "S¹ " + CAP + " d = {A₁, A₂}", 15, 40)
emit("dogru-cember-iki-nokta", p,
     f"&#948; &lt; {em('r')}: merkezin doğruya uzaklığı yarıçaptan küçükse doğru çemberi iki noktada keser.",
     "A line d at distance delta less than r from the center M cuts the circle at A1 and A2",
     extra_bottom=30)

# ============================================================ dogru-cember-teget
p = Fig((-4, 3), (-3, 3.5), 460)
s5 = 2 * math.sqrt(5)
p.circ(M, 2, THEORY, 2.4)
p.seg(((-2.5 - s5) / 2, -2.5), ((3.5 - s5) / 2, 3.5), TEXT, 2.0, name="d")
T = (-4 / math.sqrt(5), 2 / math.sqrt(5))
p.seg(M, T, TEXT, 2.6, name="MT")
p.right_angle(T, (-T[0], -T[1]), (1, 2), 9)
p.dot(M)
p.dot(T)
p.lab(T, "T", 135, 7, 15)
p.lab(M, "M", -45, 6, 15)
p.lab(mid(M, T), "r = δ", angle_of(T) - 90, 6, 14)
p.lab(((-2.5 - s5) / 2, -2.5), "d", 180, 8, 15)
p.lab(pol(2, -45), "S¹", -45, 8, 16, THEORY)
cap_title(p, "S¹ " + CAP + " d = {T}", 15, 40)
emit("dogru-cember-teget", p,
     f"&#948; = {em('r')}: uzaklık yarıçapa eşitse doğru çembere tek bir {em('T')} noktasında dokunur.",
     "A line d at distance equal to r from the center M touches the circle at the single point T",
     extra_bottom=30)

# ============================================================ dogru-cember-kesismez
p = Fig((-4.5, 3), (-3, 3.5), 460)
p.circ(M, 2, THEORY, 2.4)
p.seg(M, (2, 0), TEXT, 1.4, name="radius")
p.seg((-4.5, -3), (-1.5, 3), TEXT, 2.0, name="d")
H = (-2.4, 1.2)
p.seg(M, H, TEXT, 1.5, "4 3", name="MH")
p.right_angle(H, (2.4, -1.2), (1, 2), 9)
p.dot(M)
p.dot(H, TEXT, 3.6)
p.lab(H, "H", 180, 8, 15)
p.lab(M, "M", -45, 6, 15)
p.lab(mid(M, H), "δ", 63.4, 6, 15)
p.lab((1, 0), "r", 270, 5, 15)
p.lab((-4.5, -3), "d", 180, 8, 15)
p.lab(pol(2, -45), "S¹", -45, 8, 16, THEORY)
cap_title(p, "S¹ " + CAP + " d = ", 15, 40, empty=True)
emit("dogru-cember-kesismez", p,
     f"&#948; &gt; {em('r')}: uzaklık yarıçaptan büyükse doğru ile çemberin ortak noktası yoktur.",
     "A line d at distance delta greater than r from the center M misses the circle", extra_bottom=30)

# ============================================================ teget-yaricap-dik
p = Fig((-0.5, 6.5), (-1.5, 5), 460)
M, T = (2.0, 1.0), (3.0, 3.0)
p.circ(M, math.sqrt(5), THEORY, 2.4)
p.seg((0, 4.5), (6.5, 1.25), TEXT, 2.0, name="d")
p.seg(M, T, TEXT, 2.6, name="MT")
p.right_angle(T, (-1, -2), (2, -1), 13, TEXT, 1.6)
p.dot(M)
p.dot(T)
p.lab(M, "M", 225, 7, 15)
p.lab(T, "T", 45, 7, 15)
p.lab((6.5, 1.25), "d", 45, 7, 15)
p.lab(pol(math.sqrt(5), 225, M), "S¹", 225, 8, 16, THEORY)
emit("teget-yaricap-dik", p,
     f"Teğet {em('d')}, değme noktası {em('T')}'deki {em('MT')} yarıçapına diktir.",
     "Tangent line d at T is perpendicular to the radius MT")

# ============================================================ teget-dogru-ornegi
p = Fig((-6, 10), (-6, 8), 480)
p.axes2((-6, 10), (-6, 8))
T = (3.0, 4.0)
p.circ(O0, 5, THEORY, 2.2)
p.seg((-1, 7), (10, -1.25), TEXT, 2.0, name="tangent")
p.seg(O0, T, TEXT, 2.6, name="OT")
p.right_angle(T, (-3, -4), (4, -3), 10)
p.dot(O0)
p.dot(T)
p.lab(T, "T(3, 4)", 45, 7, 14)
p.lab(mid(O0, T), "5", angle_of(T) + 90, 6, 15)
p.lab_px(p.X(0.45), p.Y(6.6), "3x + 4y " + MINUS + " 25 = 0", 14, TEXT, "start")
p.lab(pol(5, 225), "S¹", 225, 8, 16, THEORY)
dr = p.numbers((-6, -4, -2, 2, 4, 6, 8, 10), (-6, -4, -2, 2, 4, 6, 8))
emit("teget-dogru-ornegi", p,
     f"3{em('x')} + 4{em('y')} &#8722; 25 = 0 doğrusu {em('x')}<sup>2</sup> + {em('y')}<sup>2</sup> = 25 "
     f"çemberine {em('T')}(3, 4) noktasında teğettir; {em('OT')} yarıçapı teğete diktir.",
     "The line 3x+4y-25=0 touches the circle x2+y2=25 at T(3,4); OT is perpendicular to it", dropped=dr)

# ============================================================ kesismeyen-dogru-ornegi
p = Fig((-5, 5), (-5, 4), 480)
p.axes2((-5, 5), (-5, 4))
M, H = (2.0, 1.0), (-1.0, -2.0)
p.circ(M, 2, THEORY, 2.2)
p.seg((-5, 2), (2, -5), TEXT, 2.0, name="line")
p.seg(M, H, TEXT, 1.5, "5 4", name="MH")
p.right_angle(H, (1, 1), (-1, 1), 10)
p.dot(M)
p.dot(H)
p.lab(M, "M(2, 1)", 0, 8, 14)
p.lab(H, "H(" + MINUS + "1, " + MINUS + "2)", 225, 7, 14)
p.lab((0.2, -0.8), "3" + SQRT + "2", -45, 8, 14)
p.lab((-5, 2), "x + y + 3 = 0", 45, 6, 14)
p.lab(pol(2, 45, M), "S¹", 45, 8, 16, THEORY)
dr = p.numbers((-4, -2, 2, 4), (-4, -2, 2, 4))
emit("kesismeyen-dogru-ornegi", p,
     f"Merkez {em('M')}(2, 1)'in {em('x')} + {em('y')} + 3 = 0 doğrusuna uzaklığı 3&#8730;2 &#8776; 4,24'tür; "
     "bu, yarıçap 2'den büyük olduğundan doğru çemberle buluşmaz.",
     "The line x+y+3=0 misses the circle with center M(2,1) and radius 2; the distance MH is 3 sqrt 2",
     dropped=dr)


# ============================================================ two circles (split panels)
def two_circles(M2, r1, r2, xr, yr, width=440):
    p = Fig(xr, yr, width, 60, 64)
    p.circ((0, 0), r1, THEORY, 2.4, "S11")
    p.circ(M2, r2, PRACTICE, 2.4, "S12")
    return p


def meets(u, r1, r2):
    x = (u * u + r1 * r1 - r2 * r2) / (2 * u)
    return x, math.sqrt(r1 * r1 - x * x)


# -- iki-cember-kesisen-ic
p = two_circles((2.4, 0), 3, 1.6, (-3.6, 5.0), (-3.3, 3.3))
x, y = meets(2.4, 3, 1.6)
M1, M2 = (0, 0), (2.4, 0)
for pt in ((x, y), (x, -y)):
    p.dot(pt)
p.dot(M1, TEXT, 3.6)
p.dot(M2, TEXT, 3.6)
p.lab((x, y), "A₁", 45, 7, 15)
p.lab((x, -y), "A₂", -45, 7, 15)
p.lab(M1, "M₁", 225, 6, 15)
p.lab(M2, "M₂", 270, 6, 15)
p.lab(pol(3, 225), "S¹₁", 225, 8, 16, THEORY)
p.lab((M2[0] + 1.6, 0), "S¹₂", 0, 8, 16, PRACTICE)
p.title("S¹₁ " + CAP + " S¹₂ = {A₁, A₂}", 15, 40)
emit("iki-cember-kesisen-ic", p,
     f"|{em('r')}<sub>1</sub> &#8722; {em('r')}<sub>2</sub>| &lt; |{em('M')}<sub>1</sub>{em('M')}<sub>2</sub>| "
     f"&lt; {em('r')}<sub>1</sub> + {em('r')}<sub>2</sub>: çemberler iki noktada kesişir. Burada küçük "
     "çemberin merkezi büyük çemberin içindedir.",
     "Two circles meeting at A1 and A2; the center M2 of the small circle lies inside the large one",
     extra_bottom=30)

# -- iki-cember-kesisen-dis
p = two_circles((3.3, 0), 2.5, 1.6, (-3.1, 5.4), (-2.9, 2.9))
x, y = meets(3.3, 2.5, 1.6)
M1, M2 = (0, 0), (3.3, 0)
for pt in ((x, y), (x, -y)):
    p.dot(pt)
p.dot(M1, TEXT, 3.6)
p.dot(M2, TEXT, 3.6)
p.lab((x, y), "A₁", 80, 17, 15)
p.lab((x, -y), "A₂", -80, 17, 15)
p.lab(M1, "M₁", 270, 6, 15)
p.lab(M2, "M₂", 270, 6, 15)
p.lab(pol(2.5, 225), "S¹₁", 225, 8, 16, THEORY)
p.lab(pol(1.6, -45, M2), "S¹₂", -45, 8, 16, PRACTICE)
p.title("S¹₁ " + CAP + " S¹₂ = {A₁, A₂}", 15, 40)
emit("iki-cember-kesisen-dis", p,
     f"Aynı durum, küçük çemberin merkezi büyük çemberin dışındayken: yine |{em('r')}<sub>1</sub> &#8722; "
     f"{em('r')}<sub>2</sub>| &lt; |{em('M')}<sub>1</sub>{em('M')}<sub>2</sub>| &lt; {em('r')}<sub>1</sub> + "
     f"{em('r')}<sub>2</sub> ve iki ortak nokta vardır.",
     "Two circles meeting at A1 and A2; the center M2 of the small circle lies outside the large one",
     extra_bottom=30)

# -- iki-cember-teget-distan
p = two_circles((3.8, 0), 2.5, 1.3, (-3.1, 5.4), (-2.9, 2.9))
M1, M2, T = (0, 0), (3.8, 0), (2.5, 0)
p.seg(M1, M2, TEXT, 1.3, "4 3", name="M1M2")
p.dot(T)
p.dot(M1, TEXT, 3.6)
p.dot(M2, TEXT, 3.6)
p.lab(T, "T", 140, 10, 15)
p.lab(M1, "M₁", 270, 7, 15)
p.lab(M2, "M₂", 270, 7, 15)
p.lab(pol(2.5, 225), "S¹₁", 225, 8, 16, THEORY)
p.lab(pol(1.3, -45, M2), "S¹₂", -45, 8, 16, PRACTICE)
p.heading("dıştan teğet", 14, -16)
p.title("S¹₁ " + CAP + " S¹₂ = {T}", 15, 40)
emit("iki-cember-teget-distan", p,
     f"|{em('M')}<sub>1</sub>{em('M')}<sub>2</sub>| = {em('r')}<sub>1</sub> + {em('r')}<sub>2</sub>: "
     f"çemberler dıştan teğettir; {em('T')} merkezleri birleştiren doğru parçası üzerindedir.",
     "Two externally tangent circles touching at T on the segment M1M2", extra_bottom=30)

# -- iki-cember-teget-icten
p = two_circles((1.3, 0), 2.5, 1.2, (-3.1, 3.6), (-2.9, 2.9))
M1, M2, T = (0, 0), (1.3, 0), (2.5, 0)
p.seg(M1, T, TEXT, 1.3, "4 3", name="M1T")
p.dot(T)
p.dot(M1, TEXT, 3.6)
p.dot(M2, TEXT, 3.6)
p.lab(T, "T", 0, 7, 15)
p.lab(M1, "M₁", 235, 6, 15)
p.lab(M2, "M₂", 270, 7, 15)
p.lab(pol(2.5, 225), "S¹₁", 225, 8, 16, THEORY)
p.lab((1.3, 1.2), "S¹₂", 90, 8, 16, PRACTICE)
p.heading("içten teğet", 14, -16)
p.title("S¹₁ " + CAP + " S¹₂ = {T}", 15, 40)
emit("iki-cember-teget-icten", p,
     f"|{em('M')}<sub>1</sub>{em('M')}<sub>2</sub>| = |{em('r')}<sub>1</sub> &#8722; {em('r')}<sub>2</sub>|: "
     f"küçük çember büyüğün içinde kalarak ona {em('T')} noktasında dokunur.",
     "Two internally tangent circles touching at T; the small one lies inside the large one",
     extra_bottom=30)

# -- iki-cember-ortak-nokta-yok-disinda
p = two_circles((4.8, 0), 2.5, 1.2, (-3.1, 6.4), (-2.9, 2.9))
M1, M2 = (0, 0), (4.8, 0)
p.dot(M1, TEXT, 3.6)
p.dot(M2, TEXT, 3.6)
p.lab(M1, "M₁", 270, 7, 15)
p.lab(M2, "M₂", 270, 7, 15)
p.lab(pol(2.5, 225), "S¹₁", 225, 8, 16, THEORY)
p.lab(pol(1.2, -45, M2), "S¹₂", -45, 8, 16, PRACTICE)
p.heading("birbirinin dışında", 14, -16)
cap_title(p, "S¹₁ " + CAP + " S¹₂ = ", 15, 40, empty=True)
emit("iki-cember-ortak-nokta-yok-disinda", p,
     f"|{em('M')}<sub>1</sub>{em('M')}<sub>2</sub>| &gt; {em('r')}<sub>1</sub> + {em('r')}<sub>2</sub>: "
     "çemberler birbirinin dışında kalır, ortak noktaları yoktur.",
     "Two disjoint circles, each outside the other", extra_bottom=30)

# -- iki-cember-ortak-nokta-yok-icinde
p = two_circles((0.5, 0), 2.5, 1.2, (-3.1, 3.1), (-2.9, 2.9))
M1, M2 = (0, 0), (0.5, 0)
p.dot(M1, TEXT, 3.6)
p.dot(M2, TEXT, 3.6)
p.lab(M1, "M₁", 225, 6, 15)
p.lab(M2, "M₂", -45, 6, 15)
p.lab(pol(2.5, 225), "S¹₁", 225, 8, 16, THEORY)
p.lab((0.5, 1.2), "S¹₂", 90, 9, 16, PRACTICE)
p.heading("biri diğerinin içinde", 14, -16)
cap_title(p, "S¹₁ " + CAP + " S¹₂ = ", 15, 40, empty=True)
emit("iki-cember-ortak-nokta-yok-icinde", p,
     f"|{em('M')}<sub>1</sub>{em('M')}<sub>2</sub>| &lt; |{em('r')}<sub>1</sub> &#8722; {em('r')}<sub>2</sub>|: "
     "küçük çember büyüğün içinde kalır ve ona dokunmaz.",
     "A small circle inside a larger one without touching it", extra_bottom=30)

# ============================================================ iki-cember-ortak-kiris
p = Fig((-3.5, 7), (-3.5, 3.5), 500)
M1, M2 = (0.0, 0.0), (4.0, 0.0)
x, y = meets(4, 3, 2.5)
Hk = (x, 0.0)
p.circ(M1, 3, THEORY, 2.4, "S11")
p.circ(M2, 2.5, PRACTICE, 2.4, "S12")
p.seg(M1, M2, TEXT, 1.3, name="M1M2")
p.seg((x, -3.3), (x, 3.3), BASE, 2.0, "7 5", name="l")
p.seg(M1, Hk, BASE, 3.2, name="delta")
p.right_angle(Hk, (0, 1), (1, 0), 9)
for pt in ((x, y), (x, -y)):
    p.dot(pt)
p.dot(M1, TEXT, 3.8)
p.dot(M2, TEXT, 3.8)
p.lab((x, y), "A₁", 175, 12, 15)
p.lab((x, -y), "A₂", 185, 12, 15)
p.lab(M1, "M₁", 225, 6, 15)
p.lab(M2, "M₂", -45, 6, 15)
p.lab(mid(M1, Hk), "δ", 90, 6, 16, BASE)
p.lab((x, 3.3), "ℓ", 0, 6, 16, BASE)
p.lab(pol(3, 135), "S¹₁", 135, 8, 16, THEORY)
p.lab(pol(2.5, 45, M2), "S¹₂", 45, 8, 16, PRACTICE)
emit("iki-cember-ortak-kiris", p,
     f"İki çemberin denklemlerinin farkı, merkezleri birleştiren doğruya dik bir &#8467; doğrusudur; "
     f"ortak noktalar {S11} ile &#8467;'nin ortak noktalarıdır. Sayılarını {em('M')}<sub>1</sub>'in "
     f"&#8467;'ye uzaklığı &#948; belirler.",
     "Two intersecting circles, the line l through their common points, perpendicular to M1M2, "
     "and the distance delta from M1 to l")

# ============================================================ kesisen-cemberler-ornegi
p = Fig((-6, 11), (-6, 6), 500)
p.axes2((-6, 11), (-6, 6))
M2 = (6.0, 0.0)
r2 = math.sqrt(13)
p.circ(O0, 5, THEORY, 2.2, "S11")
p.circ(M2, r2, PRACTICE, 2.2, "S12")
p.seg((4, -6), (4, 6), BASE, 2.0, "7 5", name="x = 4")
p.dot((4, 3))
p.dot((4, -3))
p.dot(M2, PRACTICE, 4.2)
p.lab_px(p.X(4) + 8, p.Y(3) - 30, "A₁(4, 3)", 14, TEXT, "start")
p.lab_px(p.X(4) + 8, p.Y(-3) + 41, "A₂(4, " + MINUS + "3)", 14, TEXT, "start")
p.lab(M2, "M₂(6, 0)", -40, 7, 14)
p.lab((4, 6), "x = 4", 180, 6, 14, BASE)
p.lab(pol(5, 135), "S¹₁", 135, 8, 16, THEORY)
p.lab(pol(r2, -45, M2), "S¹₂", -45, 8, 16, PRACTICE)
dr = p.numbers((-6, -4, -2, 2, 4, 6, 8, 10), (-4, -2, 2, 4))
emit("kesisen-cemberler-ornegi", p,
     f"{em('x')}<sup>2</sup> + {em('y')}<sup>2</sup> = 25 ile ({em('x')} &#8722; 6)<sup>2</sup> + "
     f"{em('y')}<sup>2</sup> = 13 çemberleri {em('A')}<sub>1</sub>(4, 3) ve {em('A')}<sub>2</sub>(4, &#8722;3) "
     f"noktalarında kesişir; ortak kiriş {em('x')} = 4 doğrusu üzerindedir.",
     "Circles x2+y2=25 and (x-6)2+y2=13 meeting at A1(4,3) and A2(4,-3) on the common chord x=4",
     dropped=dr)

# ============================================================ distan-teget-ornegi
p = Fig((-3, 7), (-3, 8), 460)
p.axes2((-3, 7), (-3, 8))
M2 = (3.0, 4.0)
T = (1.2, 1.6)
p.circ(O0, 2, THEORY, 2.2, "S11")
p.circ(M2, 3, PRACTICE, 2.2, "S12")
p.seg(O0, M2, TEXT, 1.3, "4 3", name="OM2")
p.seg((-2, 4), (5, -1.25), BASE, 2.0, "7 5", name="common tangent")
p.dot(T)
p.dot(M2, PRACTICE, 4.2)
p.lab(M2, "M₂(3, 4)", 0, 8, 14)
p.lab_px(p.X(T[0]) + 14, p.Y(T[1]) + 3, "T(6/5, 8/5)", 14, TEXT, "start")
p.lab((5, -1.25), "3x + 4y " + MINUS + " 10 = 0", 20, 7, 14, BASE)
p.lab(pol(2, 225), "S¹₁", 225, 8, 16, THEORY)
p.lab(pol(3, 45, M2), "S¹₂", 45, 8, 16, PRACTICE)
dr = p.numbers((-2, 2, 4, 6), (-2, 2, 4, 6, 8))
emit("distan-teget-ornegi", p,
     f"{em('x')}<sup>2</sup> + {em('y')}<sup>2</sup> = 4 ile ({em('x')} &#8722; 3)<sup>2</sup> + "
     f"({em('y')} &#8722; 4)<sup>2</sup> = 9 çemberleri dıştan teğettir. Değme noktası "
     f"{em('T')}(6/5, 8/5) merkezleri birleştiren parça üzerindedir; ortak teğet "
     f"3{em('x')} + 4{em('y')} &#8722; 10 = 0'dır.",
     "Externally tangent circles x2+y2=4 and (x-3)2+(y-4)2=9 touching at T(6/5,8/5) "
     "with the common tangent 3x+4y-10=0", dropped=dr)

# ============================================================ merkez-ve-nokta
p = Fig((-4, 8), (-3, 9), 480)
p.axes2((-4, 8), (-3, 9))
M, P, Q = (2.0, 3.0), (5.0, -1.0), (5.0, 3.0)
p.circ(M, 5, THEORY, 2.2)
p.seg(M, Q, TEXT, 1.4, "5 4", name="MQ")
p.seg(Q, P, TEXT, 1.4, "5 4", name="QP")
p.right_angle(Q, (-1, 0), (0, -1), 10)
p.seg(M, P, TEXT, 2.6, name="MP")
p.dot(M)
p.dot(P)
p.lab(M, "M(2, 3)", 135, 7, 14)
p.lab(P, "P(5, " + MINUS + "1)", -45, 7, 14)
p.lab(mid(M, P), "5", angle_of((3, -4)) - 90, 6, 15)
p.lab(mid(M, Q), "3", 90, 5, 15)
p.lab(mid(Q, P), "4", 0, 6, 15)
p.lab(pol(5, 135, M), "S¹", 135, 8, 16, THEORY)
dr = p.numbers((-4, -2, 2, 4, 6), (-2, 2, 4, 6, 8))
emit("merkez-ve-nokta", p,
     f"Yarıçap |{em('MP')}|, dik kenarları 3 ve 4 olan dik üçgenin hipotenüsüdür: {em('r')} = 5.",
     "Circle with center M(2,3) through P(5,-1); the radius MP is the hypotenuse of a 3-4-5 right triangle",
     dropped=dr)

# ============================================================ uc-noktadan-cember
p = Fig((-1, 8), (-2, 5), 480)
p.axes2((-1, 8), (-2, 5))
M = (4.0, 1.0)
A, B, C = (5.0, 3.0), (6.0, 2.0), (3.0, -1.0)
R = math.sqrt(5)
p.circ(M, R, THEORY, 2.2)
for pt, nm in ((A, "MA"), (B, "MB"), (C, "MC")):
    p.seg(M, pt, TEXT, 1.4, "5 4", name=nm)
for pt in (A, B, C, M):
    p.dot(pt)
p.lab_px(p.X(M[0]) - 10, p.Y(M[1]) + 2, "M(4, 1)", 14, TEXT, "end")
p.lab(A, "A(5, 3)", 60, 7, 14)
p.lab(B, "B(6, 2)", 0, 8, 14)
p.lab(C, "C(3, " + MINUS + "1)", 225, 7, 14)
p.lab((3.65, 0.3), SQRT + "5", 180, 7, 14)
p.lab(pol(R, 150, M), "S¹", 150, 8, 16, THEORY)
dr = p.numbers((-1, 1, 2, 3, 4, 5, 6, 7, 8), (-2, -1, 1, 2, 3, 4, 5))
emit("uc-noktadan-cember", p,
     f"{em('A')}(5, 3), {em('B')}(6, 2) ve {em('C')}(3, &#8722;1) noktalarından geçen çemberin merkezi "
     f"{em('M')}(4, 1), yarıçapı &#8730;5'tir.",
     "Circle through A(5,3), B(6,2), C(3,-1) with center M(4,1) and radius sqrt 5", dropped=dr)

# ============================================================ orijin-merkezli-teget
p = Fig((-4, 4), (-3, 4), 480)
p.axes2((-4, 4), (-3, 4))
T = (-1.2, 1.6)
om = math.degrees(math.atan2(1.6, -1.2))
p.circ(O0, 2, THEORY, 2.2)
p.seg((-4, -0.5), (2, 4), TEXT, 2.0, name="line")
p.seg(O0, T, TEXT, 2.6, name="OT")
p.right_angle(T, (1.2, -1.6), (4, 3), 10)
p.arc(0, 0, 0.6, 0, math.radians(om), PRACTICE, 1.6)
p.reg_data([(0.6 * math.cos(math.radians(om * k / 40)), 0.6 * math.sin(math.radians(om * k / 40)))
            for k in range(41)], "omega arc")
p.dot(O0)
p.dot(T)
p.lab(T, "T(" + MINUS + "6/5, 8/5)", 127, 8, 14)
p.lab(mid(O0, T), "2", om + 90, 6, 15)
p.lab(pol(0.6, om / 2), "ω", om / 2, 5, 15, PRACTICE)
p.lab_along((-4, -0.5), (2, 4), 0.26, "3x " + MINUS + " 4y + 10 = 0", 7, 14)
p.lab(pol(2, -45), "S¹", -45, 8, 16, THEORY)
dr = p.numbers((-4, -3, -2, -1, 1, 2, 3, 4), (-3, -2, -1, 1, 2, 3, 4))
emit("orijin-merkezli-teget", p,
     f"Orijinin 3{em('x')} &#8722; 4{em('y')} + 10 = 0 doğrusuna uzaklığı 2'dir; merkezi orijin olan ve bu "
     f"doğruya teğet çember {em('x')}<sup>2</sup> + {em('y')}<sup>2</sup> = 4, değme noktası "
     f"{em('T')}(&#8722;6/5, 8/5)'tir.",
     "Circle x2+y2=4 tangent to the line 3x-4y+10=0 at T(-6/5,8/5); omega is the angle of OT", dropped=dr)

# ============================================================ dogru-cember-ortak-noktalar
p = Fig((-4, 4), (-4, 4.5), 480)
p.axes2((-4, 4), (-4, 4.5))
P1, P2 = (0.0, 3.0), (-2.4, -1.8)
p.circ(O0, 3, THEORY, 2.2)
p.seg((-3.5, -4), (0.75, 4.5), TEXT, 2.0, name="line")
p.dot(P1, PRACTICE, 4.6)
p.dot(P2, PRACTICE, 4.6)
p.lab_px(p.X(P1[0]) + 16, p.Y(P1[1]) - 8, "(0, 3)", 14, PRACTICE, "start")
p.lab(P2, "(" + MINUS + "12/5, " + MINUS + "9/5)", 178, 12, 14, PRACTICE)
p.lab((0.75, 4.5), "y = 2x + 3", 0, 8, 14)
p.lab(pol(3, -45), "S¹", -45, 8, 16, THEORY)
dr = p.numbers((-4, -3, -2, -1, 1, 2, 3, 4), (-4, -3, -2, -1, 1, 2, 3, 4))
emit("dogru-cember-ortak-noktalar", p,
     f"{em('y')} = 2{em('x')} + 3 doğrusu {em('x')}<sup>2</sup> + {em('y')}<sup>2</sup> = 9 çemberini (0, 3) ve "
     "(&#8722;12/5, &#8722;9/5) noktalarında keser.",
     "The line y=2x+3 cuts the circle x2+y2=9 at (0,3) and (-12/5,-9/5)", dropped=dr)


# ---------------------------------------------------------------------------
for name, content in OUT.items():
    with io.open(OUT_DIR / f"analytic-cem-{name}.md", "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
print(f"generated {len(OUT)} figures:", ", ".join(OUT))
