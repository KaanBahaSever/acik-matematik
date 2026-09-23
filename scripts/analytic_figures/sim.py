# -*- coding: utf-8 -*-
"""Figures for dersler/analitik-geometri/uzayda-simetri.qmd (chapter key: sim).

Every drawing here is three-dimensional and goes through scripts/svg_plot3.py
(orthographic Camera on an equal-aspect svg_plot.Plot panel). The figures go
INSIDE the box they explain (example, solution, proof), never inside a
definition box.

Colour code shared by all figures: the mirror (a line or a plane) is blue
(THEORY), the point P is orange (PRACTICE), its mirror image P' is green
(BASE), the foot K and the dashed segment PP' are in the text colour. Equal
halves PK and KP' carry the same tick marks; K carries a right-angle mark.

Labels are placed after the projection, in page pixels: `Fig.place` tries a
ring of candidate positions around the anchor and keeps the one that touches
no drawn line, point or earlier label, so labels never sit on the geometry.
Plane patches are registered as occluders: whatever lies behind a patch is
drawn thin, dashed and faint.

Usage:   python scripts/analytic_figures/sim.py
         python scripts/center_figures.py "analytic-sim-*.md" --keep-width
Output:  scripts/_figures/analytic-sim-<name>.md
"""
import html
import io
import math
import re
import sys
from fractions import Fraction as Fr
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, WIDE, TEXT, BG, THEORY, PRACTICE, BASE, REMARK  # noqa: E402
from svg_plot3 import Camera, Space, vadd, vsub, vscale, vdot, vcross, vnorm, vunit  # noqa: E402

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
OUT = {}

MINUS, SQRT, PRIME = "−", "√", "′"
NAME, DESC, TICK, AXIS = 14.0, 12.5, 11, 14.5      # font sizes (px)

# Fraktur D (U+1D507) outline in em units, baseline at y = 0, y pointing down. Book fonts
# and rsvg have no glyph for it, so it is drawn as a path (from TeX Gyre DejaVu Math, GUST
# Font License), the same outline as in dzu.py.
FRAK_PATH = ("M.9 -.467Q.9 -.331 .837 -.168Q.656 .031 .584 .031Q.557 .031 .456 -.009Q.397 -.032 .323 -.055"
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
NARROW = "ders-grafik"                              # tall scenes stay in the standard column

# ---------------------------------------------------------------------------
# text helpers
# ---------------------------------------------------------------------------


def it(s):
    return f'<tspan font-style="italic">{s}</tspan>'


def sub(s, size=NAME):
    return (f'<tspan font-size="{0.76 * size:.1f}" dy="4">{s}</tspan>'
            f'<tspan dy="-4">&#8203;</tspan>')


def num(v):
    """Integer or fraction with a real minus sign."""
    v = Fr(v)
    s = str(abs(v.numerator)) if v.denominator == 1 else f"{abs(v.numerator)}/{v.denominator}"
    return (MINUS + s) if v < 0 else s


def triple(*vs):
    return "(" + ", ".join(v if isinstance(v, str) else num(v) for v in vs) + ")"


def pn(letter, idx=None, prime=False, size=NAME):
    """Point name: italic letter, optional subscript, optional prime."""
    return it(letter) + (sub(idx, size) if idx else "") + (PRIME if prime else "")


def var_eq(s):
    """Italicise the single-letter variables x, y, z in an equation string."""
    return re.sub(r"(?<![A-Za-z])([xyz])(?![A-Za-z])", lambda m: it(m.group(1)), s)


_TSPAN = re.compile(r"<tspan\b([^>]*)>(.*?)</tspan>", re.S)
_TAG = re.compile(r"<[^>]+>")
_FS = re.compile(r'font-size="([\d.]+)"')
CW = 0.58          # estimated advance per character, in em (a little wider than the checker's)


def text_width(s, size):
    w = 0.0
    for m in _TSPAN.finditer(s):
        fs = _FS.search(m.group(1))
        inner = html.unescape(_TAG.sub("", m.group(2))).replace("​", "")
        w += len(inner) * CW * (float(fs.group(1)) if fs else size)
    rest = html.unescape(_TAG.sub("", _TSPAN.sub("", s))).replace("​", "")
    return w + len(rest) * CW * size


def seg_hits_box(p, q, b):
    """Liang-Barsky: does the segment pq meet the box b = (x0, y0, x1, y1)?"""
    x0, y0, x1, y1 = b
    dx, dy = q[0] - p[0], q[1] - p[1]
    t0, t1 = 0.0, 1.0
    for pk, qk in ((-dx, p[0] - x0), (dx, x1 - p[0]), (-dy, p[1] - y0), (dy, y1 - p[1])):
        if pk == 0:
            if qk < 0:
                return False
        else:
            t = qk / pk
            if pk < 0:
                t0 = max(t0, t)
            else:
                t1 = min(t1, t)
            if t0 > t1:
                return False
    return True


def box_overlap(a, b):
    w = min(a[2], b[2]) - max(a[0], b[0])
    h = min(a[3], b[3]) - max(a[1], b[1])
    return max(w, 0) * max(h, 0)


def inside(poly, x, y):
    """Even-odd point-in-polygon test in page pixels."""
    c = False
    n = len(poly)
    for i in range(n):
        (x1, y1), (x2, y2) = poly[i], poly[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
            c = not c
    return c


DIRS = {"r": 0, "ur": 45, "u": 90, "ul": 135, "l": 180, "dl": 225, "d": 270, "dr": 315}
DEFAULT_ORDER = ["ur", "r", "ul", "u", "dr", "d", "dl", "l",
                 22.5, 67.5, 112.5, 157.5, 202.5, 247.5, 292.5, 337.5]

# point styles
SEG = dict(color=TEXT, width=1.7, dash="7 5", opacity=0.9)
SEG_HID = dict(color=TEXT, width=1.1, dash="3 4", opacity=0.45, w=0.4)


def F(*vs):
    return tuple(Fr(v) for v in vs)


def fl(P):
    return tuple(float(c) for c in P)


def mirror_plane(P, n, D):
    """Image of P in the plane n.X + D = 0 (exact, on Fractions)."""
    delta = sum(a * b for a, b in zip(n, P)) + D
    mu = Fr(-2) * delta / sum(a * a for a in n)
    return tuple(p + mu * a for p, a in zip(P, n))


def mirror_line(P, P0, v):
    """(foot K, image P') of P for the line P0 + t v (exact, on Fractions)."""
    lam = sum((p - q) * a for p, q, a in zip(P, P0, v)) / sum(a * a for a in v)
    K = tuple(q + lam * a for q, a in zip(P0, v))
    return K, tuple(2 * k - p for k, p in zip(K, P))


# ---------------------------------------------------------------------------
# the figure object: a Space plus a registry of what is drawn, in pixels
# ---------------------------------------------------------------------------


class Fig:
    def __init__(self, az, el, extent, width=600, pad=70):
        self.cam = Camera(az, el)
        pr = [self.cam.project(P) for P in extent]
        xs, ys = [a for a, _, _ in pr], [b for _, b, _ in pr]
        self.ppu = width / (max(xs) - min(xs))
        h = (max(ys) - min(ys)) * self.ppu
        self.p = Plot(pad, pad, width, h, (min(xs), max(xs)), (min(ys), max(ys)))
        self.S = Space(self.p, self.cam)
        self.W, self.H = width + 2 * pad, h + 2 * pad
        self.d = self.cam.d
        self.segs, self.dots, self.boxes, self.texts = [], [], [], []
        self.sid = 0          # stroke id: a label crossing one stroke pays once, however finely sampled
        self.pending = []     # tick numbers wait until the whole drawing is registered
        self.occ = []

    # -- projection ---------------------------------------------------------
    def px(self, P):
        X, Y = self.S.pt(P)
        return (self.p.X(X), self.p.Y(Y))

    def u(self, pixels):
        """Pixels -> space units."""
        return pixels / self.ppu

    def _reg(self, Ps, w=1.0):
        self._reg_px([self.px(P) for P in Ps], w)

    def _reg_px(self, q, w=1.0):
        self.sid += 1
        for a, b in zip(q, q[1:]):
            self.segs.append((a, b, w, self.sid))

    # -- occlusion by plane patches ------------------------------------------
    def add_occluder(self, Ps):
        n = vcross(vsub(Ps[1], Ps[0]), vsub(Ps[2], Ps[0]))
        if vdot(n, self.d) < 0:
            n = vscale(-1.0, n)
        self.occ.append((Ps[0], vunit(n), [self.px(P) for P in Ps]))

    def hidden(self, P):
        x, y = self.px(P)
        return any(vdot(vsub(P, A), n) < -1e-6 and inside(poly, x, y) for A, n, poly in self.occ)

    # -- drawing ------------------------------------------------------------
    def line(self, Ps, color=TEXT, width=1.6, dash=None, opacity=1.0, w=1.0):
        self.S.line(Ps, color, width, dash, opacity)
        if w:
            self._reg(Ps, w)

    def guide(self, Ps, color=TEXT, opacity=0.5, width=1.0, dash="4 3", w=0.7):
        self.line(Ps, color, width, dash, opacity, w)

    def arrow(self, P0, P1, color=THEORY, width=2.2, head=10.0, dash=None, opacity=1.0, w=1.0,
              halo=False):
        if halo:
            self.S.line([P0, P1], BG, width + 3.4, None, 1.0)
        self.S.arrow(P0, P1, color, width, head, dash, opacity)
        self._reg([P0, P1], w)

    def polygon(self, Ps, fill=THEORY, opacity=0.14):
        self.S.polygon(Ps, fill, opacity)

    def patch(self, Ps, color=THEORY, fill=0.15, edge=1.3, edge_op=0.75, occlude=True):
        """A translucent piece of a plane with its outline; optionally an occluder."""
        self.polygon(Ps, color, fill)
        self.line(list(Ps) + [Ps[0]], color, edge, None, edge_op, w=0.6)
        if occlude:
            self.add_occluder(Ps)

    def point(self, P, color=TEXT, r=4.4):
        self.S.point(P, color, r)
        x, y = self.px(P)
        self.dots.append((x, y, r))

    def split(self, Ps, flag):
        """Cut a sampled polyline into runs on which flag(point) is constant."""
        runs, cur, state = [], [Ps[0]], flag(Ps[0])
        for P in Ps[1:]:
            f_ = flag(P)
            if f_ != state:
                runs.append((state, cur + [P]))
                cur, state = [P], f_
            else:
                cur.append(P)
        runs.append((state, cur))
        return runs

    def styled(self, Ps, flag, on, off):
        """Draw a polyline with style `on` where flag holds and `off` elsewhere."""
        for state, run in self.split(Ps, flag):
            st = on if state else off
            if st is not None and len(run) > 1:
                self.line(run, **st)

    def seg(self, A, B, vis=None, hid=None, n=240):
        """Straight segment: style `vis` where seen, `hid` where a registered patch hides it."""
        vis = dict(SEG) if vis is None else vis
        hid = dict(SEG_HID) if hid is None else hid
        pts = [vadd(A, vscale(k / n, vsub(B, A))) for k in range(n + 1)]
        self.styled(pts, lambda P: not self.hidden(P), vis, hid)

    def right_angle(self, Q, a, b, size=17, color=TEXT, width=1.5, opacity=0.95):
        s = self.u(size)
        a, b = vunit(a), vunit(b)
        pts = [vadd(Q, vscale(s, a)), vadd(Q, vadd(vscale(s, a), vscale(s, b))), vadd(Q, vscale(s, b))]
        self.line(pts, color, width, None, opacity, w=0.5)

    def eq_tick(self, A, B, count=1, length=12, gap=5, color=TEXT, width=1.7, at=0.5):
        """Equal-length tick marks across the segment AB (drawn in page pixels)."""
        (xa, ya), (xb, yb) = self.px(A), self.px(B)
        L = math.hypot(xb - xa, yb - ya)
        ux, uy = (xb - xa) / L, (yb - ya) / L
        nx, ny = -uy, ux
        mx, my = xa + at * (xb - xa), ya + at * (yb - ya)
        for k in range(count):
            off = (k - (count - 1) / 2) * gap
            cx, cy = mx + ux * off, my + uy * off
            a = (cx - nx * length / 2, cy - ny * length / 2)
            b = (cx + nx * length / 2, cy + ny * length / 2)
            self.p.add(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" '
                       f'stroke="{color}" stroke-width="{width}" stroke-linecap="round"/>')
            self._reg_px([a, b], 0.8)

    def sphere(self, C, r, color, fill=0.12, eq_width=1.4):
        """Translucent sphere: shaded disk, outline and an equator whose back half is dashed."""
        cx, cy = self.px(C)
        R = r * self.ppu
        self.p.add(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{R:.1f}" fill="{color}" '
                   f'fill-opacity="{fill}" stroke="none"/>')
        for rr, ww, op in ((0.95, 0.10, 0.05), (0.89, 0.14, 0.04), (0.82, 0.18, 0.035),
                           (0.73, 0.22, 0.03)):
            self.p.add(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{rr * R:.1f}" fill="none" '
                       f'stroke="{color}" stroke-width="{ww * R:.1f}" stroke-opacity="{op}"/>')
        self.p.add(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{R:.1f}" fill="none" stroke="{color}" '
                   f'stroke-width="1.8" opacity="0.9"/>')
        self._reg_px([(cx + R * math.cos(2 * math.pi * k / 96), cy + R * math.sin(2 * math.pi * k / 96))
                      for k in range(97)], 1.0)
        ring = [vadd(C, (r * math.cos(2 * math.pi * k / 120), r * math.sin(2 * math.pi * k / 120), 0.0))
                for k in range(121)]
        self.styled(ring, lambda Q: vdot(vsub(Q, C), self.d) >= 0,
                    dict(color=color, width=eq_width, opacity=0.7, w=0.4),
                    dict(color=color, width=1.0, dash="5 4", opacity=0.45, w=0.2))

    # -- axes -------------------------------------------------------------
    def axes(self, rng, labels=("X", "Y", "Z"), width=1.4, opacity=0.8, color=TEXT, head=9.0,
             special=None):
        """Coordinate axes over the given (lo, hi) ranges, arrowheads at the positive ends.
        Parts hidden behind a registered patch are thin and dashed; negative parts are solid.
        special = {k: dict(color=..., width=...)} restyles one axis (a mirror axis, say)."""
        E = ((1, 0, 0), (0, 1, 0), (0, 0, 1))
        for k, (lo, hi) in enumerate(rng):
            e = E[k]
            col, wid = color, width
            op = opacity
            if special and k in special:
                col = special[k].get("color", col)
                wid = special[k].get("width", wid)
                op = special[k].get("opacity", 1.0)
            vis = dict(color=col, width=wid, opacity=op, w=1.0)
            hid = dict(color=col, width=1.0, dash="4 3", opacity=0.45, w=0.5)
            n = 240
            tip = vscale(hi, e)
            cut = hi - self.u(head * 1.4)
            pts = [vscale(lo + (cut - lo) * j / n, e) for j in range(n + 1)]
            self.styled(pts, lambda P: not self.hidden(P), vis, hid)
            self.arrow(vscale(cut, e), tip, col, wid, head, None, op, w=1.0)
            if labels and labels[k]:
                self.axis_label(e, tip, labels[k], color=col)

    def axis_label(self, e, tip, s, size=AXIS, gap=8, color=TEXT):
        x0, y0 = self.px((0, 0, 0))
        x1, y1 = self.px(tip)
        L = math.hypot(x1 - x0, y1 - y0) or 1.0
        ax, ay = (x1 - x0) / L, (y1 - y0) / L
        w, h = text_width(s, size), size
        ext = min(w / 2 / abs(ax) if ax else 1e9, h / 2 / abs(ay) if ay else 1e9)
        cx, cy = x1 + ax * (gap + ext), y1 + ay * (gap + ext)
        self._text(cx, cy, it(s), size, color, w, h)

    def ticks(self, axis, vals, size=TICK, side=None, length=6.0, label=True, skip=(), limit=12.0):
        k = "xyz".index(axis)
        e = [0.0, 0.0, 0.0]
        e[k] = 1.0
        x0, y0 = self.px((0, 0, 0))
        x1, y1 = self.px(tuple(e))
        L = math.hypot(x1 - x0, y1 - y0)
        ax, ay = (x1 - x0) / L, (y1 - y0) / L
        nx, ny = -ay, ax
        for v in vals:
            P = [0.0, 0.0, 0.0]
            P[k] = v
            x, y = self.px(tuple(P))
            a = (x - nx * length / 2, y - ny * length / 2)
            b = (x + nx * length / 2, y + ny * length / 2)
            self.p.add(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" '
                       f'stroke="{TEXT}" stroke-width="1.1" opacity="0.8"/>')
            self._reg_px([a, b], 0.5)
        if label:
            self.pending.append((k, [v for v in vals if v not in skip], size, side, limit, ax, ay, nx, ny))

    def _flush(self):
        jobs, self.pending = self.pending, []
        for k, vals, size, side, limit, ax, ay, nx, ny in jobs:
            for v in vals:
                P = [0.0, 0.0, 0.0]
                P[k] = v
                x, y = self.px(tuple(P))
                s = num(int(v)) if float(v).is_integer() else str(v).replace(".", ",")
                w, h = text_width(s, size), size
                best = None
                for sg in ((side,) if side else (1, -1)):
                    for gap in (5, 9, 14):
                        for slide in (0, 6, -6, 12, -12):
                            ext = abs(nx) * w / 2 + abs(ny) * h / 2
                            cx = x + sg * nx * (gap + ext) + ax * slide
                            cy = y + sg * ny * (gap + ext) + ay * slide
                            box = (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)
                            c = self.cost(box) + gap * 0.15 + abs(slide) * 0.25
                            if best is None or c < best[0]:
                                best = (c, cx, cy)
                if best[0] > limit:
                    print(f"   tick {'xyz'[k]}={v}: no clean spot (cost {best[0]:.1f}), number left out")
                    continue
                self._text(best[1], best[2], s, size, TEXT, w, h, opacity=0.85)

    # -- labels ---------------------------------------------------------------
    def cost(self, box, pad=3.0):
        b = (box[0] - pad, box[1] - pad, box[2] + pad, box[3] + pad)
        c = 0.0
        for o in self.boxes:
            ov = box_overlap(b, o)
            if ov > 0:
                c += 60 + ov / 5
        for x, y, r in self.dots:
            if b[0] - r < x < b[2] + r and b[1] - r < y < b[3] + r:
                c += 45
        hit = {}
        for p, q, w, sid in self.segs:
            if w and sid not in hit and seg_hits_box(p, q, b):
                hit[sid] = w
        c += 9 * sum(hit.values())
        if b[0] < 4 or b[1] < 4 or b[2] > self.W - 4 or b[3] > self.H - 4:
            c += 200
        return c

    def _text(self, cx, cy, s, size, color, w, h, opacity=1.0, halo=True):
        self.boxes.append((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2))
        base = cy + 0.28 * h
        op = f' opacity="{opacity}"' if opacity < 1 else ""
        stroke = (f' stroke="{BG}" stroke-width="3.6" stroke-linejoin="round" paint-order="stroke"'
                  if halo else "")
        self.texts.append(f'<text x="{cx:.1f}" y="{base:.1f}" fill="{color}" font-size="{size}" '
                          f'text-anchor="middle"{op}{stroke}>{s}</text>')

    def place(self, anchor, s, size=NAME, color=TEXT, prefs=None, d=7.0, leader=False,
              opacity=1.0, only=False, far=(0, 7, 15, 26, 40), w_px=None):
        """Put text s next to anchor (a space point, or a pixel pair given as ('px', x, y)).
        The cheapest candidate on a ring around the anchor is used; earlier prefs win ties."""
        self._flush()
        if isinstance(anchor, tuple) and anchor and anchor[0] == "px":
            x, y = anchor[1], anchor[2]
        else:
            x, y = self.px(anchor)
        w, h = (w_px or text_width(s, size)), size
        order = list(prefs) if prefs else list(DEFAULT_ORDER)
        if not only and prefs:
            order += [o for o in DEFAULT_ORDER if o not in order]
        best = None
        for k, name in enumerate(order):
            if name == "c":
                cands = [(x, y, 0)]
            else:
                th = math.radians(DIRS.get(name, name) if isinstance(name, str) else name)
                c_, s_ = math.cos(th), -math.sin(th)
                ext = min(w / 2 / abs(c_) if abs(c_) > 1e-9 else 1e9, h / 2 / abs(s_) if abs(s_) > 1e-9 else 1e9)
                cands = [(x + c_ * (d + e + ext), y + s_ * (d + e + ext), e) for e in far]
            for cx, cy, e in cands:
                box = (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)
                c = self.cost(box) + k * 0.8 + e * 0.15
                if best is None or c < best[0]:
                    best = (c, cx, cy, e)
        c, cx, cy, e = best
        if c > 12:
            print(f"   label '{html.unescape(_TAG.sub('', s))}': cost {c:.1f}")
        if leader and e >= 15:
            bx = min(max(x, cx - w / 2), cx + w / 2)
            by = min(max(y, cy - h / 2), cy + h / 2)
            L = math.hypot(bx - x, by - y)
            if L > 8:
                ux, uy = (bx - x) / L, (by - y) / L
                self.texts.insert(0, f'<line x1="{x + ux * 5:.1f}" y1="{y + uy * 5:.1f}" x2="{bx - ux * 3:.1f}" '
                                     f'y2="{by - uy * 3:.1f}" stroke="{color}" stroke-width="0.9" opacity="0.7"/>')
        self._text(cx, cy, s, size, color, w, h, opacity)
        return cx, cy

    def plane_name(self, anchor, tail="", size=NAME, color=THEORY, prefs=None, d=7.0, only=False,
                   far=(0, 7, 15, 26, 40)):
        """The fraktur D (an outline path) followed by the text `tail`, placed like a label.
        The <text> tail carries the characters, so the label checker still sees it."""
        gw = FRAK_ADV * size
        w = gw + (text_width(tail, size) if tail else 0.0)
        cx, cy = self.place(anchor, tail or "D", size, color, prefs, d, only=only, far=far, w_px=w)
        self.texts.pop()
        x0, base = cx - w / 2, cy + 0.28 * size
        self.texts.append(f'<path d="{FRAK_PATH}" transform="translate({x0:.1f} {base:.1f}) scale({size:.2f})" '
                          f'fill="{color}" stroke="{BG}" stroke-width="{3.6 / size:.3f}" '
                          f'stroke-linejoin="round" paint-order="stroke"/>')
        if tail:
            self.texts.append(f'<text x="{x0 + gw:.1f}" y="{base:.1f}" fill="{color}" font-size="{size}" '
                              f'text-anchor="start" stroke="{BG}" stroke-width="3.6" '
                              f'stroke-linejoin="round" paint-order="stroke">{tail}</text>')
        return cx, cy

    def sang(self, vec):
        """Page angle (degrees, 0 = right, 90 = up) of the space direction vec."""
        X, Y, _ = self.cam.project(vadd(self.cam.center, vec))
        return math.degrees(math.atan2(Y, X))

    # -- output -------------------------------------------------------------
    def render(self, name, caption, aria, css=WIDE):
        self._flush()
        print(f"-- {name} (warnings above belong to it)")
        for t in self.texts:
            self.p.add(t)
        OUT[name] = figure(round(self.W), round(self.H), [self.p], caption, css, aria)


def plane_patch(C, e1, e2, s, t):
    """Corners of C + [s0, s1] e1 + [t0, t1] e2."""
    return [vadd(C, vadd(vscale(a, e1), vscale(b, e2))) for a, b in
            ((s[0], t[0]), (s[1], t[0]), (s[1], t[1]), (s[0], t[1]))]


def face_dir(f, n):
    """The direction in the plane with normal n that the camera sees at full length."""
    return vunit(vcross(n, f.d))


def mirror_marks(f, P, K, Pp, a, count=1, size=17):
    """Right-angle mark at K between the mirror direction a and KP, and equal ticks on PK, KP'."""
    f.right_angle(K, a, vsub(P, K), size)
    f.eq_tick(P, K, count)
    f.eq_tick(K, Pp, count)


O3 = (0.0, 0.0, 0.0)


# ============================================================ dogruya-gore-kurulum
cam = Camera(35, 22)
th = math.radians(9)
ed = vunit(vadd(vscale(math.cos(th), cam.r), vscale(math.sin(th), cam.u)))      # along d
en = vunit(vadd(vscale(-math.sin(th), cam.r), vscale(math.cos(th), cam.u)))     # page-up normal
K = O3
Pa, Pb = vscale(-3.6, ed), vscale(2.6, ed)
P0 = vscale(-2.2, ed)
V1 = vadd(P0, vscale(1.05, ed))
P = vscale(1.75, en)
Pp = vscale(-1.75, en)
f = Fig(35, 22, [Pa, Pb, P, Pp], width=520, pad=80)
f.line([Pa, Pb], THEORY, 2.4, None, 1.0)
f.seg(P, Pp)
f.arrow(P0, V1, REMARK, 3.2, 12.0)
mirror_marks(f, P, K, Pp, ed)
f.point(P0, THEORY, 4.2)
f.point(K, TEXT, 4.2)
f.point(P, PRACTICE, 5.0)
f.point(Pp, BASE, 5.0)
f.place(Pa, it("d"), NAME + 2, THEORY, prefs=[90, 110, 70], only=True)
f.place(P0, pn("P", "0") + triple(pn("x", "0"), pn("y", "0"), pn("z", "0")), NAME, THEORY,
        prefs=[270, 250, 290])
f.place(vscale(0.5, vadd(P0, V1)), it("v"), NAME + 1, REMARK, prefs=[90, 80, 100])
f.place(K, it("K"), NAME, prefs=[315, 300, 330, 290])
f.place(P, pn("P") + triple(pn("x", "1"), pn("y", "1"), pn("z", "1")), NAME, PRACTICE,
        prefs=[0, 20, 340])
f.place(Pp, pn("P", prime=True) + triple(pn("x", "1") + PRIME, pn("y", "1") + PRIME, pn("z", "1") + PRIME),
        NAME, BASE, prefs=[0, 340, 20])
f.render(
    "dogruya-gore-kurulum",
    "<em>P</em> noktasının <em>d</em> doğrusuna göre simetriği <em>P</em>&#8242;: <em>P</em>&#8217;den "
    "<em>d</em>&#8217;ye inilen dikmenin ayağı <em>K</em>&#8217;dır ve <em>P</em>&#8242; bu dikmenin "
    "uzantısında, <em>K</em>&#8217;nın öbür yanında durur. Çentikler |<em>PK</em>| = "
    "|<em>KP</em>&#8242;| eşitliğini gösterir; <em>d</em>, <em>P</em><sub>0</sub> noktasından geçer ve "
    "doğrultman vektörü <em>v</em>&#8217;dir.",
    "A line d through P0 with direction vector v, a point P above it and its mirror image P' below; "
    "the dashed segment PP' meets d at right angles at K, with equal tick marks on PK and KP'")


# ============================================================ dogru-ornek
P0e, ve, Pe = F(0, 0, 2), F(2, 4, 1), F(3, 4, -2)
Ke, Ppe = mirror_line(Pe, P0e, ve)
assert Ke == F(Fr(12, 7), Fr(24, 7), Fr(20, 7)) and Ppe == F(Fr(3, 7), Fr(20, 7), Fr(54, 7))
P0, v, P, K, Pp = fl(P0e), fl(ve), fl(Pe), fl(Ke), fl(Ppe)
D0, D1 = P0, vadd(P0, vscale(1.2, v))
# seen almost square-on to the plane of d and PP', so the right angle at K reads as one
f = Fig(-25, 15, [(4.2, 0, 0), (0, 5.4, 0), (0, 0, 8.6), (0, 0, -2.5), P, Pp, D1], width=470, pad=80)
f.axes(((0, 4.2), (0, 5.4), (-2.5, 8.6)))
f.guide([P, (P[0], P[1], 0)], TEXT, 0.4, 1.0, "3 3", w=0.4)
f.guide([Pp, (Pp[0], Pp[1], 0)], TEXT, 0.4, 1.0, "3 3", w=0.4)
f.point((P[0], P[1], 0), TEXT, 2.4)
f.point((Pp[0], Pp[1], 0), TEXT, 2.4)
f.line([D0, D1], THEORY, 2.4, None, 1.0)
f.arrow(P0, vadd(P0, v), REMARK, 3.0, 12.0)
f.seg(P, Pp)
mirror_marks(f, P, K, Pp, v)
f.ticks("z", (2, 4, 6, 8), skip=(2,))
f.point(P0, THEORY, 4.2)
f.point(K, TEXT, 4.4)
f.point(P, PRACTICE, 5.0)
f.point(Pp, BASE, 5.0)
f.place(O3, it("O"), NAME, prefs=[235, 250, 215])
f.place(D1, it("d"), NAME + 2, THEORY, prefs=[f.sang(v), f.sang(v) + 30, f.sang(v) - 30])
f.place(P0, pn("P", "0"), NAME, THEORY, prefs=[180, 200, 160])
f.place(vadd(P0, vscale(0.45, v)), it("v"), NAME + 1, REMARK, prefs=[f.sang(v) + 90, f.sang(v) - 90])
f.place(K, it("K"), NAME, prefs=[f.sang(v) - 90, f.sang(v) - 60, f.sang(v) + 150])
f.place(P, pn("P") + triple(3, 4, -2), NAME, PRACTICE, prefs=[0, 340, 20])
f.place(Pp, pn("P", prime=True) + triple(Fr(3, 7), Fr(20, 7), Fr(54, 7)), NAME, BASE, prefs=[0, 20, 340])
f.render(
    "dogru-ornek",
    "<em>P</em>(3, 4, &#8722;2) noktası, <em>d</em>: <em>x</em>/2 = <em>y</em>/4 = <em>z</em> &#8722; 2 "
    "doğrusu ve simetriği <em>P</em>&#8242;(3/7, 20/7, 54/7). <em>d</em>, <em>P</em><sub>0</sub>(0, 0, 2) "
    "noktasından <em>v</em> = (2, 4, 1) doğrultusunda geçer; dikmenin ayağı "
    "<em>K</em>(12/7, 24/7, 20/7), <em>PP</em>&#8242; parçasının orta noktasıdır.",
    "Axes X, Y, Z; the line d through P0(0, 0, 2) with direction v = (2, 4, 1); the point P(3, 4, -2), "
    "its mirror image P'(3/7, 20/7, 54/7) and the foot K(12/7, 24/7, 20/7) with a right-angle mark "
    "and equal tick marks", NARROW)


# ============================================================ dogru-parametrik
P0e, ve, Pe = F(1, 1, 2), F(1, 0, 1), F(3, 2, 5)
Ke, Ppe = mirror_line(Pe, P0e, ve)
assert Ke == F(Fr(7, 2), 1, Fr(9, 2)) and Ppe == F(4, 0, 4)
P0, v, P, K, Pp = fl(P0e), fl(ve), fl(Pe), fl(Ke), fl(Ppe)
D0, D1 = vadd(P0, vscale(-1.0, v)), vadd(P0, vscale(3.5, v))
f = Fig(30, 18, [(5.4, 0, 0), (0, 3.4, 0), (0, 0, 6.2), D0, D1, P], width=520, pad=80)
f.axes(((0, 5.4), (0, 3.4), (0, 6.2)))
Y1 = [(0, 1, 0), (5, 1, 0), (5, 1, 6), (0, 1, 6)]          # the plane y = 1 that holds d
f.polygon(Y1, REMARK, 0.08)
f.line(Y1 + [Y1[0]], REMARK, 1.0, None, 0.5, w=0.4)
f.line([D0, D1], THEORY, 2.4, None, 1.0)
f.arrow(P0, vadd(P0, v), REMARK, 3.0, 12.0)
f.seg(P, Pp)
mirror_marks(f, P, K, Pp, v)
f.ticks("y", (1, 2, 3), skip=(3,))
f.point(P0, THEORY, 4.2)
f.point(K, TEXT, 4.4)
f.point(P, PRACTICE, 5.0)
f.point(Pp, BASE, 5.0)
f.place(O3, it("O"), NAME, prefs=[235, 250, 215])
f.place(D1, it("d"), NAME + 2, THEORY, prefs=[f.sang(v), f.sang(v) + 30, f.sang(v) - 30])
f.place(P0, pn("P", "0"), NAME, THEORY, prefs=[f.sang(v) + 90, f.sang(v) + 120, 180])
f.place(vadd(P0, vscale(0.5, v)), it("v"), NAME + 1, REMARK, prefs=[f.sang(v) - 90, f.sang(v) + 90])
f.place(K, it("K"), NAME, prefs=[f.sang(v) + 150, 180, 200, 160])
f.place(P, pn("P") + triple(3, 2, 5), NAME, PRACTICE, prefs=[20, 0, 45])
f.place(Pp, pn("P", prime=True) + triple(4, 0, 4), NAME, BASE, prefs=[340, 0, 315])
f.place((4.3, 1, 0.9), it("y") + " = 1", DESC + 0.5, REMARK, prefs=["c"], only=True)
f.render(
    "dogru-parametrik",
    "<em>d</em>: <em>x</em> = 1 + <em>&#955;</em>, <em>y</em> = 1, <em>z</em> = 2 + <em>&#955;</em> "
    "doğrusu soluk çizilen <em>y</em> = 1 düzleminde kalır; <em>P</em> bu düzlemin önünde "
    "(<em>y</em> = 2), <em>P</em>&#8242; arkasındadır (<em>y</em> = 0). <em>P</em>(3, 2, 5) noktasının "
    "simetriği <em>P</em>&#8242;(4, 0, 4), dikmenin ayağı <em>K</em>(7/2, 1, 9/2)&#8217;dir.",
    "Axes X, Y, Z; the line d: x = 1 + t, y = 1, z = 2 + t through P0(1, 1, 2) with direction "
    "v = (1, 0, 1); the point P(3, 2, 5), its image P'(4, 0, 4) and the foot K(7/2, 1, 9/2) with a "
    "right-angle mark and equal tick marks", NARROW)


# ============================================================ eksenler
Pe = F(2, 3, 2)
Ke, Ppe = mirror_line(Pe, F(0, 0, 0), F(0, 0, 1))
assert Ke == F(0, 0, 2) and Ppe == F(-2, -3, 2)
P, K, Pp = fl(Pe), fl(Ke), fl(Ppe)
f = Fig(35, 20, [(3.3, 0, 0), (-3, 0, 0), (0, 4.3, 0), (0, -4, 0), (0, 0, 3.5), (0, 0, -0.6)],
        width=580, pad=70)
f.axes(((-3, 3.3), (-4, 4.3), (-0.6, 3.5)), special={2: dict(color=THEORY, width=3.0)})
for Q in (P, Pp):
    f.guide([Q, (Q[0], Q[1], 0)], TEXT, 0.45, 1.0, "3 3", w=0.4)
    f.point((Q[0], Q[1], 0), TEXT, 2.6)
f.guide([(P[0], P[1], 0), (Pp[0], Pp[1], 0)], TEXT, 0.35, 1.0, "2 4", w=0.4)   # the shadow runs through O
f.seg(P, Pp)
mirror_marks(f, P, K, Pp, (0, 0, 1), size=24)
f.point(K, TEXT, 4.4)
f.point(P, PRACTICE, 5.0)
f.point(Pp, BASE, 5.0)
f.place(O3, it("O"), NAME, prefs=[200, 180, 220])
f.place(K, pn("K") + triple(0, 0, 2), NAME, prefs=[135, 120, 150, 45])
f.place(P, pn("P") + triple(2, 3, 2), NAME, PRACTICE, prefs=[0, 20, 340])
f.place(Pp, pn("P", prime=True) + triple(-2, -3, 2), NAME, BASE, prefs=[160, 180, 140])
f.render(
    "eksenler",
    "<em>P</em>(2, 3, 2) noktasının <em>Z</em>-eksenine göre simetriği <em>P</em>&#8242;(&#8722;2, "
    "&#8722;3, 2). Dikmenin ayağı <em>K</em>(0, 0, 2) eksenin üzerindedir; <em>PP</em>&#8242; parçası "
    "<em>z</em> = 2 yüksekliğinde yataydır. Soluk kesikli çizgiler iki noktanın <em>XY</em>-düzlemine "
    "inen dikmeleridir.",
    "Axes X, Y, Z with the Z axis highlighted as the mirror; P(2, 3, 2), its image P'(-2, -3, 2) and "
    "the foot K(0, 0, 2) on the Z axis with a right-angle mark; faint drops from P and P' to the XY "
    "plane")


# ============================================================ duzleme-gore-kurulum
K = O3
P, Pp = (0.0, 0.0, 2.2), (0.0, 0.0, -2.2)
PL = plane_patch(O3, (1, 0, 0), (0, 1, 0), (-2.4, 2.4), (-2.6, 2.6))
f = Fig(35, 22, PL + [P, Pp], width=520, pad=80)
f.patch(PL, THEORY, 0.16)
f.seg(P, Pp)
f.arrow(K, (0, 0, 0.75), THEORY, 3.4, 12.0)
f.right_angle(K, face_dir(f, (0, 0, 1)), (0, 0, 1))
f.eq_tick(P, K)
f.eq_tick(K, Pp)
f.point(K, TEXT, 4.4)
f.point(P, PRACTICE, 5.0)
f.point(Pp, BASE, 5.0)
f.plane_name(PL[3], "", NAME + 5, THEORY, prefs=[270, 225, 315])
f.place(K, it("K"), NAME, prefs=[225, 200, 250])
f.place((0, 0, 0.62), it("n") + " = " + triple(it("A"), it("B"), it("C")), NAME, THEORY,
        prefs=[180, 160, 200])
f.place(P, pn("P") + triple(pn("x", "1"), pn("y", "1"), pn("z", "1")), NAME, PRACTICE, prefs=[0, 20, 340])
f.place(Pp, pn("P", prime=True) + triple(pn("x", "1") + PRIME, pn("y", "1") + PRIME, pn("z", "1") + PRIME),
        NAME, BASE, prefs=[0, 340, 20])
f.render(
    "duzleme-gore-kurulum",
    "<em>P</em> noktasının bir düzleme göre simetriği <em>P</em>&#8242;: <em>P</em>&#8217;den düzleme "
    "inilen dikme düzlemi <em>K</em>&#8217;da keser ve normal vektör <em>n</em>&#8217;ye paraleldir; "
    "<em>P</em>&#8242; bu dikmenin düzlemin öbür yanında kalan kısmında, <em>K</em>&#8217;ya "
    "<em>P</em> kadar uzaktadır. Düzlemin arkasında kalan parça daha soluktur.",
    "A translucent plane patch D, the point K on it with the normal vector n = (A, B, C), the point P "
    "above and its mirror image P' below on the same perpendicular, a right-angle mark at K and equal "
    "tick marks on PK and KP'")


# ============================================================ duzlem-nokta
ne, De = F(1, -2, 2), Fr(-3)
Pe = F(2, -2, 3)
Ppe = mirror_plane(Pe, ne, De)
Ke = tuple((a + b) / 2 for a, b in zip(Pe, Ppe))
assert Ppe == F(0, 2, -1) and Ke == F(1, 0, 1)
P, K, Pp, n = fl(Pe), fl(Ke), fl(Ppe), fl(ne)
e1, e2 = (2, 1, 0), (0, 1, 1)
assert vdot(e1, n) == 0 and vdot(e2, n) == 0
PL = plane_patch(K, e1, e2, (-1.2, 1.2), (-1.2, 1.2))
f = Fig(10, 28, PL + [P, Pp, (3.4, 0, 0), (-1.2, 0, 0), (0, 3.4, 0), (0, -3.2, 0), (0, 0, 4.3),
                      (0, 0, -2.3)], width=560, pad=70)
f.add_occluder(PL)
f.axes(((-1.2, 3.4), (-3.2, 3.4), (-2.3, 4.3)))
f.patch(PL, THEORY, 0.15, occlude=False)
f.seg(P, Pp)
f.arrow(K, vadd(K, vscale(0.45, n)), THEORY, 3.4, 12.0)
mirror_marks(f, P, K, Pp, face_dir(f, n))
f.point(K, TEXT, 4.4)
f.point(P, PRACTICE, 5.0)
f.point(Pp, BASE, 5.0)
f.place(O3, it("O"), NAME, prefs=[200, 225, 180])
f.plane_name(PL[1], ": " + var_eq("x − 2y + 2z − 3 = 0"), NAME, THEORY, prefs=[270, 315, 225, 0])
f.place(vadd(K, vscale(0.4, n)), it("n"), NAME + 1, THEORY, prefs=[f.sang(n) + 90, f.sang(n) - 90])
f.place(K, pn("K") + triple(1, 0, 1), NAME, prefs=[f.sang(n) - 90, 0, 340, 20])
f.place(P, pn("P") + triple(2, -2, 3), NAME, PRACTICE, prefs=[0, 20, 160, 180])
f.place(Pp, pn("P", prime=True) + triple(0, 2, -1), NAME, BASE, prefs=[0, 340, 20])
f.render(
    "duzlem-nokta",
    "<em>P</em>(2, &#8722;2, 3) noktasının <em>x</em> &#8722; 2<em>y</em> + 2<em>z</em> &#8722; 3 = 0 "
    "düzlemine göre simetriği <em>P</em>&#8242;(0, 2, &#8722;1). <em>PP</em>&#8242; parçası normal "
    "<em>n</em> = (1, &#8722;2, 2) doğrultusundadır ve düzlemi orta noktası <em>K</em>(1, 0, 1)&#8217;de "
    "dik keser; düzlemin arkasında kalan parçalar kesikli ve soluktur.",
    "Axes X, Y, Z; a patch of the plane x - 2y + 2z - 3 = 0 around K(1, 0, 1); the point P(2, -2, 3), "
    "its image P'(0, 2, -1), the normal n from K, a right-angle mark at K and equal tick marks")


# ============================================================ koordinat-duzlemleri
Pe = F(2, 3, 2)
Ppe = mirror_plane(Pe, F(0, 0, 1), Fr(0))
assert Ppe == F(2, 3, -2)
P, K, Pp = fl(Pe), (2.0, 3.0, 0.0), fl(Ppe)
PL = [(0, 0, 0), (3, 0, 0), (3, 4, 0), (0, 4, 0)]
f = Fig(35, 20, [(3.5, 0, 0), (0, 4.6, 0), (0, 0, 3.2), (0, 0, -3.0), P, Pp], width=520, pad=80)
f.add_occluder([(0, 0, 0), (3, 0, 0), (3, 4, 0), (0, 4, 0)])
f.axes(((0, 3.5), (0, 4.6), (-3.0, 3.2)))
f.patch(PL, THEORY, 0.15, occlude=False)
f.guide([K, (2, 0, 0)], TEXT, 0.5, 1.0, "3 3")
f.guide([K, (0, 3, 0)], TEXT, 0.5, 1.0, "3 3")
f.seg(P, Pp)
mirror_marks(f, P, K, Pp, face_dir(f, (0, 0, 1)))
f.ticks("x", (2,))
f.ticks("y", (3,))
f.point(K, TEXT, 4.4)
f.point(P, PRACTICE, 5.0)
f.point(Pp, BASE, 5.0)
f.place(O3, it("O"), NAME, prefs=[160, 180, 135])
f.place((3, 2, 0), it("XY") + "-düzlemi", NAME, THEORY, prefs=[250, 270, 225, 290])
f.place(K, pn("K") + triple(2, 3, 0), NAME, prefs=[0, 340, 20, 315])
f.place(P, pn("P") + triple(2, 3, 2), NAME, PRACTICE, prefs=[0, 20, 340])
f.place(Pp, pn("P", prime=True) + triple(2, 3, -2), NAME, BASE, prefs=[0, 340, 20])
f.render(
    "koordinat-duzlemleri",
    "<em>P</em>(2, 3, 2) noktasının <em>XY</em>-düzlemine göre simetriği <em>P</em>&#8242;(2, 3, "
    "&#8722;2). Dikme <em>Z</em>-eksenine paraleldir ve düzlemi <em>K</em>(2, 3, 0)&#8217;da keser; "
    "düzlemin altında kalan parça kesikli ve soluktur.",
    "Axes X, Y, Z; the part [0,3] x [0,4] of the XY plane; P(2, 3, 2) above it, P'(2, 3, -2) below and "
    "the foot K(2, 3, 0) with guides to the axes, a right-angle mark and equal tick marks")


# ============================================================ kure
Me, ne3 = F(3, 0, 0), F(1, 1, 1)
Mpe = mirror_plane(Me, ne3, Fr(0))
Fe = tuple((a + b) / 2 for a, b in zip(Me, Mpe))
assert Mpe == F(1, -2, -2) and Fe == F(2, -1, -1) and sum(Fe) == 0
M, Mp, Fm = fl(Me), fl(Mpe), fl(Fe)
a1 = vunit((1, -1, 0))
a2 = vunit((1, 1, -2))
PL = plane_patch(Fm, a1, a2, (-2.6, 2.6), (-2.9, 2.9))
# nearly edge-on to the mirror: the plane is a band and MM' crosses it at right angles
f = Fig(-40, 20, PL + [(5.4, 0, 0), (-1, 0, 0), (0, 3.2, 0), (0, -4.3, 0), (0, 0, 3.3), (0, 0, -4.3),
                       vadd(M, (0, 0, 2.1)), vadd(Mp, (0, 0, -2.1)), vadd(M, (2.1, 0, 0))],
        width=560, pad=70)
f.add_occluder(PL)
f.axes(((-1, 5.4), (-3.2, 3.2), (-3.0, 3.3)))
f.patch(PL, THEORY, 0.13, occlude=False)
f.sphere(M, 2.0, PRACTICE)
f.sphere(Mp, 2.0, BASE)
f.seg(M, Mp)
f.right_angle(Fm, face_dir(f, (1, 1, 1)), vsub(M, Fm))
f.point(Fm, TEXT, 3.2)
f.point(M, PRACTICE, 4.6)
f.point(Mp, BASE, 4.6)
f.place(O3, it("O"), NAME, prefs=[160, 135, 180])
f.place(M, pn("M") + triple(3, 0, 0), NAME, PRACTICE, prefs=[0, 340, 20])
f.place(Mp, pn("M", prime=True) + triple(1, -2, -2), NAME, BASE, prefs=[180, 200, 160])
f.plane_name(PL[2], ": " + var_eq("x + y + z = 0"), NAME, THEORY, prefs=[90, 45, 135, 0])
f.render(
    "kure",
    "(<em>x</em> &#8722; 3)<sup>2</sup> + <em>y</em><sup>2</sup> + <em>z</em><sup>2</sup> = 4 küresi "
    "(turuncu) ve <em>x</em> + <em>y</em> + <em>z</em> = 0 düzlemine göre simetriği (yeşil). Merkez "
    "<em>M</em>(3, 0, 0) merkeze,<em>M</em>&#8242;(1, &#8722;2, &#8722;2)&#8217;ye gider; "
    "<em>MM</em>&#8242; parçası düzlemi orta noktası (2, &#8722;1, &#8722;1)&#8217;de dik keser ve "
    "yarıçap 2 olarak kalır.",
    "Axes X, Y, Z; a patch of the plane x + y + z = 0; the sphere S of radius 2 about M(3, 0, 0) and its "
    "mirror image S' about M'(1, -2, -2); the dashed segment MM' meets the plane at right angles at "
    "(2, -1, -1)", NARROW)


# ============================================================ dogru-duzlem
ne, De = F(2, -3, 4), Fr(4)
P0e, P1e, ve = F(1, 0, 0), F(3, 1, 3), F(2, 1, 3)
P0pe, P1pe = mirror_plane(P0e, ne, De), mirror_plane(P1e, ne, De)
assert P0pe == F(Fr(5, 29), Fr(36, 29), Fr(-48, 29)) and P1pe == F(Fr(11, 29), Fr(143, 29), Fr(-65, 29))
Se = F(Fr(1, 13), Fr(-6, 13), Fr(-18, 13))
assert sum(a * b for a, b in zip(ne, Se)) + De == 0
we = tuple(b - a for a, b in zip(P0pe, P1pe))
assert we == F(Fr(6, 29), Fr(107, 29), Fr(-17, 29))
assert all(s - p == Fr(-6, 13) * w for s, p, w in zip(Se, P0pe, we))
K0e = tuple((a + b) / 2 for a, b in zip(P0e, P0pe))
K1e = tuple((a + b) / 2 for a, b in zip(P1e, P1pe))
P0, P1, P0p, P1p, S, w, v, n = map(fl, (P0e, P1e, P0pe, P1pe, Se, we, ve, ne))
K0, K1 = fl(K0e), fl(K1e)
# plane patch: an orthonormal frame of the plane centred between S, K0 and K1
b1 = vunit(vsub(K1, K0))
b2 = vunit(vcross(n, b1))
Cn = vscale(1 / 3, vadd(S, vadd(K0, K1)))
cs = [(vdot(vsub(Q, Cn), b1), vdot(vsub(Q, Cn), b2)) for Q in (S, K0, K1)]
m = 0.9
PL = plane_patch(Cn, b1, b2, (min(c[0] for c in cs) - m, max(c[0] for c in cs) + m),
                 (min(c[1] for c in cs) - m, max(c[1] for c in cs) + m))
L0, L1 = -0.8, 1.3
dA, dB = vadd(P0, vscale(L0, v)), vadd(P0, vscale(L1, v))
eA, eB = vadd(P0p, vscale(L0, w)), vadd(P0p, vscale(L1, w))
f = Fig(35, 25, PL + [dA, dB, eA, eB, (4.2, 0, 0), (-1, 0, 0), (0, 5.3, 0), (0, -1, 0), (0, 0, 4.3),
                       (0, 0, -3)], width=560, pad=70)
f.add_occluder(PL)
f.axes(((-1, 4.2), (-1, 5.3), (-3, 4.3)))
f.patch(PL, THEORY, 0.13, occlude=False)
f.seg(dA, dB, dict(color=PRACTICE, width=2.4, opacity=1.0), dict(color=PRACTICE, width=1.3, dash="5 4",
                                                                  opacity=0.55, w=0.5))
f.seg(eA, eB, dict(color=BASE, width=2.4, opacity=1.0), dict(color=BASE, width=1.3, dash="5 4",
                                                              opacity=0.55, w=0.5))
thin = dict(color=TEXT, width=1.2, dash="5 4", opacity=0.8)
for A_, B_ in ((P0, P0p), (P1, P1p)):
    f.seg(A_, B_, thin)
f.point(K0, TEXT, 2.6)
f.point(K1, TEXT, 2.6)
f.point(S, THEORY, 4.6)
for Q, col in ((P0, PRACTICE), (P1, PRACTICE), (P0p, BASE), (P1p, BASE)):
    f.point(Q, col, 4.6)
f.place(O3, it("O"), NAME, prefs=[200, 225, 180])
f.place(dB, it("d"), NAME + 2, PRACTICE, prefs=[f.sang(v), f.sang(v) + 30, f.sang(v) - 30])
f.place(eB, it("d") + PRIME, NAME + 2, BASE, prefs=[f.sang(w), f.sang(w) + 30, f.sang(w) - 30])
f.place(P0, pn("P", "0"), NAME, PRACTICE, prefs=[f.sang(v) - 90, f.sang(v) + 90])
f.place(P1, pn("P", "1"), NAME, PRACTICE, prefs=[f.sang(v) - 90, f.sang(v) + 90])
f.place(P0p, pn("P", "0", True), NAME, BASE, prefs=[f.sang(w) + 90, f.sang(w) - 90])
f.place(P1p, pn("P", "1", True), NAME, BASE, prefs=[f.sang(w) + 90, f.sang(w) - 90])
f.place(S, it("S"), NAME, THEORY, prefs=[270, 225, 315, 180, 0])
f.plane_name(PL[0], "", NAME + 5, THEORY, prefs=[225, 270, 180, 315])
f.render(
    "dogru-duzlem",
    "<em>d</em> doğrusu (turuncu) ve 2<em>x</em> &#8722; 3<em>y</em> + 4<em>z</em> + 4 = 0 "
    "düzlemine göre simetriği <em>d</em>&#8242; (yeşil). <em>P</em><sub>0</sub>(1, 0, 0) ve "
    "<em>P</em><sub>1</sub>(3, 1, 3) noktalarının simetrikleri <em>P</em><sub>0</sub>&#8242;(5/29, 36/29, "
    "&#8722;48/29) ve <em>P</em><sub>1</sub>&#8242;(11/29, 143/29, &#8722;65/29)&#8217;dir; iki doğru "
    "düzlemi aynı <em>S</em>(1/13, &#8722;6/13, &#8722;18/13) noktasında keser. Düzlemin arkasında kalan "
    "parçalar kesiklidir.",
    "Axes X, Y, Z; a patch of the plane 2x - 3y + 4z + 4 = 0; the line d through P0 and P1 and its "
    "mirror image d' through P0' and P1'; thin dashed perpendiculars P0P0' and P1P1'; both lines meet "
    "the plane at S")


# ============================================================ exr-dogru-nokta
P0e, ve, Pe = F(1, -1, 2), F(2, 1, -2), F(1, 8, 2)
Ke, Ppe = mirror_line(Pe, P0e, ve)
assert Ke == F(3, 0, 0) and Ppe == F(5, -8, -2)
assert sum((a - b) ** 2 for a, b in zip(Pe, Ke)) == 72
P0, v, P, K, Pp = fl(P0e), fl(ve), fl(Pe), fl(Ke), fl(Ppe)
D0, D1 = vadd(P0, vscale(-0.5, v)), vadd(P0, vscale(2.0, v))
f = Fig(50, 20, [(6.3, 0, 0), (0, 9.4, 0), (0, -9, 0), (0, 0, 3.3), (0, 0, -3), P, Pp, D0, D1],
        width=600, pad=70)
f.axes(((0, 6.3), (-9, 9.4), (-3, 3.3)))
f.line([D0, D1], THEORY, 2.4, None, 1.0)
f.seg(P, Pp)
mirror_marks(f, P, K, Pp, v)
f.ticks("y", (-8, -4, 4, 8))
f.point(P0, THEORY, 4.2)
f.point(K, TEXT, 4.4)
f.point(P, PRACTICE, 5.0)
f.point(Pp, BASE, 5.0)
f.place(O3, it("O"), NAME, prefs=[250, 235, 270])
f.place(D1, it("d"), NAME + 2, THEORY, prefs=[f.sang(v), f.sang(v) + 30, f.sang(v) - 30])
f.place(P0, pn("P", "0"), NAME, THEORY, prefs=[f.sang(v) + 90, f.sang(v) - 90])
f.place(K, pn("K") + triple(3, 0, 0), NAME, prefs=[315, 290, 250, 200, 160])
f.place(vscale(0.5, vadd(P, K)), "6" + SQRT + "2", DESC + 0.5, prefs=[90, 70, 110])
f.place(P, pn("P") + triple(1, 8, 2), NAME, PRACTICE, prefs=[0, 20, 340])
f.place(Pp, pn("P", prime=True) + triple(5, -8, -2), NAME, BASE, prefs=[180, 200, 160])
f.render(
    "exr-dogru-nokta",
    "<em>P</em>(1, 8, 2) noktası, <em>d</em>: (<em>x</em> &#8722; 1)/2 = <em>y</em> + 1 = "
    "(<em>z</em> &#8722; 2)/(&#8722;2) doğrusu ve simetriği <em>P</em>&#8242;(5, &#8722;8, &#8722;2). "
    "Dikmenin ayağı <em>K</em>(3, 0, 0)&#8217;dır ve <em>P</em>&#8217;nin <em>d</em>&#8217;ye uzaklığı "
    "|<em>PK</em>| = 6&#8730;2&#8217;dir.",
    "Axes X, Y, Z; the line d through P0(1, -1, 2) with direction (2, 1, -2); P(1, 8, 2), its image "
    "P'(5, -8, -2) and the foot K(3, 0, 0) with a right-angle mark and equal tick marks; the distance "
    "PK = 6 sqrt 2")


# ============================================================ exr-duzlem-bul
ne, De = F(1, -2, 2), Fr(-12)
Ae, Be = F(1, 2, 3), F(3, -2, 7)
assert mirror_plane(Ae, ne, De) == Be
Ke = tuple((a + b) / 2 for a, b in zip(Ae, Be))
assert Ke == F(2, 0, 5)
A_, B_, K, n = fl(Ae), fl(Be), fl(Ke), fl(ne)
e1, e2 = (2, 1, 0), (0, 1, 1)
PL = plane_patch(K, e1, e2, (-1.5, 1.5), (-1.5, 1.5))
f = Fig(10, 28, PL + [A_, B_, (4.3, 0, 0), (0, 3.4, 0), (0, -3.3, 0), (0, 0, 8.4)], width=540, pad=70)
f.add_occluder(PL)
f.axes(((0, 4.3), (-3.3, 3.4), (0, 8.4)))
f.patch(PL, THEORY, 0.15, occlude=False)
f.seg(A_, B_)
mirror_marks(f, B_, K, A_, face_dir(f, n))
f.point(K, TEXT, 4.4)
f.point(A_, PRACTICE, 5.0)
f.point(B_, BASE, 5.0)
f.place(O3, it("O"), NAME, prefs=[200, 225, 180])
f.plane_name(PL[1], ": " + var_eq("x − 2y + 2z − 12 = 0"), NAME, THEORY, prefs=[270, 315, 225, 0])
f.place(K, pn("K") + triple(2, 0, 5), NAME, prefs=[0, 340, 20, 180])
f.place(A_, pn("A") + triple(1, 2, 3), NAME, PRACTICE, prefs=[0, 340, 20])
f.place(B_, pn("B") + triple(3, -2, 7), NAME, BASE, prefs=[180, 160, 200])
f.render(
    "exr-duzlem-bul",
    "<em>A</em>(1, 2, 3) ile simetriği <em>B</em>(3, &#8722;2, 7) arasındaki ayna, <em>AB</em> "
    "parçasının orta noktası <em>K</em>(2, 0, 5)&#8217;ten geçen ve <em>AB</em>&#8217;ye dik olan "
    "<em>x</em> &#8722; 2<em>y</em> + 2<em>z</em> &#8722; 12 = 0 düzlemidir. Düzlemin arkasında "
    "kalan parça kesikli ve soluktur.",
    "Axes X, Y, Z; a patch of the plane x - 2y + 2z - 12 = 0 around K(2, 0, 5); the points A(1, 2, 3) "
    "and B(3, -2, 7) joined by a dashed segment through K, with a right-angle mark and equal tick "
    "marks", NARROW)


# ============================================================ exr-dogru-paralel
ne, De = F(1, -1, 1), Fr(-3)
P0e, P1e, ve = F(1, 2, 7), F(2, 3, 7), F(1, 1, 0)
P0pe, P1pe = mirror_plane(P0e, ne, De), mirror_plane(P1e, ne, De)
assert P0pe == F(-1, 4, 5) and P1pe == F(0, 5, 5)
K0e = tuple((a + b) / 2 for a, b in zip(P0e, P0pe))
K1e = tuple((a + b) / 2 for a, b in zip(P1e, P1pe))
assert K0e == F(0, 3, 6) and K1e == F(1, 4, 6)
P0, P1, P0p, P1p, K0, K1, v, n = map(fl, (P0e, P1e, P0pe, P1pe, K0e, K1e, ve, ne))
e2 = (1, 0, -1)
assert vdot(e2, n) == 0
PL = plane_patch(K0, v, e2, (-1.6, 2.6), (-1.2, 1.2))
dA, dB = vadd(P0, vscale(-1.5, v)), vadd(P0, vscale(2.0, v))
eA, eB = vadd(P0p, vscale(-1.0, v)), vadd(P0p, vscale(2.5, v))
# seen from behind (-x, +y): the only views that show both the lines and the normal at full length
f = Fig(140, 32, PL + [dA, dB, eA, eB, (4.3, 0, 0), (-2, 0, 0), (0, 6.6, 0), (0, 0, 8.4)], width=560, pad=70)
f.add_occluder(PL)
f.axes(((-2, 4.3), (0, 6.6), (0, 8.4)))
f.patch(PL, THEORY, 0.14, occlude=False)
f.seg(dA, dB, dict(color=PRACTICE, width=2.4, opacity=1.0), dict(color=PRACTICE, width=1.3, dash="5 4",
                                                                  opacity=0.55, w=0.5))
f.seg(eA, eB, dict(color=BASE, width=2.4, opacity=1.0), dict(color=BASE, width=1.3, dash="5 4",
                                                              opacity=0.55, w=0.5))
thin = dict(color=TEXT, width=1.2, dash="5 4", opacity=0.8)
for A_, B_ in ((P0, P0p), (P1, P1p)):
    f.seg(A_, B_, thin)
f.point(K0, TEXT, 2.6)
f.point(K1, TEXT, 2.6)
for Q, col in ((P0, PRACTICE), (P1, PRACTICE), (P0p, BASE), (P1p, BASE)):
    f.point(Q, col, 4.6)
f.place(O3, it("O"), NAME, prefs=[250, 225, 270])
f.place(dB, it("d"), NAME + 2, PRACTICE, prefs=[f.sang(v), f.sang(v) + 30, f.sang(v) - 30])
f.place(eB, it("d") + PRIME, NAME + 2, BASE, prefs=[f.sang(v), f.sang(v) + 30, f.sang(v) - 30])
for Q, s_, col, side in ((P0, pn("P", "0"), PRACTICE, 90), (P1, pn("P", "1"), PRACTICE, 90),
                         (P0p, pn("P", "0", True), BASE, -90), (P1p, pn("P", "1", True), BASE, -90)):
    f.place(Q, s_, NAME, col, prefs=[f.sang(v) + side, f.sang(v) + side + 25, f.sang(v) + side - 25])
f.plane_name(PL[1], "", NAME + 5, THEORY, prefs=[0, 315, 45])
f.render(
    "exr-dogru-paralel",
    "<em>x</em> &#8722; <em>y</em> + <em>z</em> &#8722; 3 = 0 düzlemine paralel <em>d</em> doğrusu "
    "(turuncu) ve simetriği <em>d</em>&#8242; (yeşil). İki doğru da (1, 1, 0) doğrultusundadır ve "
    "düzlemin iki yanında, ona &#8730;3 uzaklıktadır; kesikli dikmelerin ayakları (0, 3, 6) ve "
    "(1, 4, 6)&#8217;dır.",
    "Axes X, Y, Z; a patch of the plane x - y + z - 3 = 0; the line d through P0(1, 2, 7) and P1(2, 3, 7) "
    "above it and the parallel line d' through P0'(-1, 4, 5) and P1'(0, 5, 5) below it, joined by "
    "dashed perpendiculars through the plane", NARROW)


# ============================================================ exr-duzlem-duzlem
T1 = [(6, 0, 0), (0, 3, 0), (0, 0, 2)]
T2 = [(3, 0, 0), (0, 6, 0), (0, 0, 2)]
for Q in T1:
    assert Q[0] + 2 * Q[1] + 3 * Q[2] == 6
for Q in T2:
    assert 2 * Q[0] + Q[1] + 3 * Q[2] == 6
MQ = [(0, 0, 0), (3, 3, 0), (3, 3, 2.5), (0, 0, 2.5)]
LA, LB = (0, 0, 2), (2, 2, 0)
for Q in (LA, LB):
    assert Q[0] == Q[1] and Q[0] + 2 * Q[1] + 3 * Q[2] == 6 and 2 * Q[0] + Q[1] + 3 * Q[2] == 6
f = Fig(60, 24, [(6.6, 0, 0), (0, 6.6, 0), (0, 0, 3.0), (3, 3, 2.5)], width=600, pad=70)
f.axes(((0, 6.6), (0, 6.6), (0, 3.0)))
f.polygon(T1, PRACTICE, 0.15)
f.line(T1 + [T1[0]], PRACTICE, 1.4, None, 0.8, w=0.6)
f.polygon(T2, BASE, 0.15)
f.line(T2 + [T2[0]], BASE, 1.4, None, 0.8, w=0.6)
f.polygon(MQ, THEORY, 0.16)
f.line(MQ + [MQ[0]], THEORY, 1.4, None, 0.85, w=0.6)
f.line([LA, LB], TEXT, 3.4, None, 0.95)
f.seg((6, 0, 0), (0, 6, 0), dict(color=TEXT, width=1.3, dash="5 4", opacity=0.8))
f.right_angle((3, 3, 0), (-1, -1, 0), (1, -1, 0))
for Q, col in (((6, 0, 0), PRACTICE), ((0, 6, 0), BASE), ((3, 3, 0), TEXT)):
    f.point(Q, col, 4.4)
f.point(LA, TEXT, 3.2)
f.point(LB, TEXT, 3.2)
f.place(O3, it("O"), NAME, prefs=[250, 270, 225])
f.place((6, 0, 0), triple(6, 0, 0), NAME, PRACTICE, prefs=[270, 225, 315])
f.place((0, 6, 0), triple(0, 6, 0), NAME, BASE, prefs=[270, 315, 225])
f.plane_name((2.2, 0.55, 0.35), sub("1", NAME + 2), NAME + 2, PRACTICE, prefs=["c"], only=True)
f.plane_name((0.55, 2.2, 0.35), sub("1", NAME + 2) + PRIME, NAME + 2, BASE, prefs=["c"], only=True)
f.plane_name((3, 3, 2.5), ": " + it("x") + " = " + it("y"), NAME, THEORY, prefs=[45, 90, 0])
f.render(
    "exr-duzlem-duzlem",
    "Birinci bölgedeki parçalar: <em>x</em> + 2<em>y</em> + 3<em>z</em> = 6 (turuncu), "
    "simetriği 2<em>x</em> + <em>y</em> + 3<em>z</em> = 6 (yeşil) ve ayna "
    "<em>x</em> = <em>y</em> (mavi). Üç düzlem kalın çizilen ortak doğru boyunca kesişir; "
    "(6, 0, 0) noktasının görüntüsü (0, 6, 0)&#8217;dır.",
    "Axes X, Y, Z; in the first octant the triangle of the plane x + 2y + 3z = 6, the triangle of its "
    "image 2x + y + 3z = 6 and the vertical mirror x = y; the three planes share the bold line from "
    "(0, 0, 2) to (2, 2, 0); (6, 0, 0) and (0, 6, 0) are joined by a dashed segment through (3, 3, 0)")


# ============================================================ exr-bilesim
P, P1, P2 = (2.0, 3.0, 2.0), (2.0, 3.0, -2.0), (2.0, -3.0, -2.0)
F1, F2, F3 = (2.0, 3.0, 0.0), (2.0, 0.0, -2.0), (2.0, 0.0, 0.0)
# seen from the -y side, so that PP2 and the X axis show their right angle
f = Fig(-60, 35, [(3.7, 0, 0), (0, 4.4, 0), (0, -4, 0), (0, 0, 3.2), (0, 0, -3), P, P1, P2], width=560, pad=120)
f.S.parallelogram(O3, (1, 0, 0), (0, 1, 0), (0, 2.8), (-0.2, 3.8), THEORY, 0.06)
f.S.parallelogram(O3, (1, 0, 0), (0, 0, 1), (0, 2.8), (-2.8, 0.2), BASE, 0.06)
f.axes(((0, 3.7), (-4, 4.4), (-3, 3.2)), special={0: dict(color=THEORY, width=3.0)})
f.seg(P, P1)
f.seg(P1, P2)
f.seg(P, P2, dict(color=REMARK, width=1.4, dash="2 4", opacity=0.9))
f.right_angle(F3, (1, 0, 0), vsub(P, F3), 18)
f.eq_tick(P, F1)
f.eq_tick(F1, P1)
f.eq_tick(P1, F2, 2)
f.eq_tick(F2, P2, 2)
for Q in (F1, F2):
    f.point(Q, TEXT, 3.0)
f.point(F3, TEXT, 3.4)
f.point(P, PRACTICE, 5.0)
f.point(P1, REMARK, 5.0)
f.point(P2, BASE, 5.0)
f.place(O3, it("O"), NAME, prefs=[160, 135, 180])
f.place(P, pn("P") + triple(2, 3, 2), NAME, PRACTICE, prefs=[0, 20, 340])
f.place(P1, pn("P", "1") + triple(2, 3, -2), NAME, REMARK, prefs=[340, 0, 315, 290])
f.place(P2, pn("P", "2") + triple(2, -3, -2), NAME, BASE, prefs=[180, 200, 160])
f.render(
    "exr-bilesim",
    "<em>P</em>(2, 3, 2) noktasının <em>XY</em>-düzlemine göre simetriği <em>P</em><sub>1</sub>(2, 3, "
    "&#8722;2), onun da <em>XZ</em>-düzlemine göre simetriği <em>P</em><sub>2</sub>(2, &#8722;3, "
    "&#8722;2)&#8217;dir. Noktalı <em>PP</em><sub>2</sub> parçası <em>X</em>-eksenini (2, 0, 0)&#8217;da "
    "dik keser: <em>P</em><sub>2</sub>, <em>P</em>&#8217;nin <em>X</em>-eksenine göre simetriğidir.",
    "Axes X, Y, Z with the X axis highlighted; P(2, 3, 2), P1(2, 3, -2) below the XY plane and "
    "P2(2, -3, -2) behind the XZ plane; dashed segments P P1 and P1 P2 through the feet (2, 3, 0) and "
    "(2, 0, -2), and a dotted segment P P2 meeting the X axis at right angles at (2, 0, 0)")


# ---------------------------------------------------------------------------
for name, content in OUT.items():
    path = OUT_DIR / f"analytic-sim-{name}.md"
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(content)
    print("wrote", path.name)
