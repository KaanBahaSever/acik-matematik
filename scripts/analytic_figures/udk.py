# -*- coding: utf-8 -*-
"""Figures for dersler/analitik-geometri/uzayda-dik-koordinat-sistemi.qmd (chapter key: udk).

Every drawing here is three-dimensional and goes through scripts/svg_plot3.py
(orthographic Camera on an equal-aspect svg_plot.Plot panel). The figures go
INSIDE the box they explain (example, solution, proof), never inside a
definition box.

Labels are placed after the projection, in page pixels: `Fig.place` tries a
ring of candidate positions around the anchor and keeps the one that touches
no drawn line, point or earlier label, so labels never sit on the geometry.

Usage:   python scripts/analytic_figures/udk.py
         python scripts/center_figures.py "analytic-udk-*.md" --keep-width
Output:  scripts/_figures/analytic-udk-<name>.md
"""
import html
import io
import math
import re
import sys
from fractions import Fraction
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, WIDE, TEXT, BG, THEORY, PRACTICE, BASE, REMARK  # noqa: E402
from svg_plot3 import Camera, Space, vadd, vsub, vscale, vdot, vnorm, vunit  # noqa: E402

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
OUT = {}

MINUS, SQRT = "−", "√"
NAME, DESC, TICK, AXIS = 13.5, 12.5, 11, 14.5      # font sizes (px)

# ---------------------------------------------------------------------------
# text helpers
# ---------------------------------------------------------------------------


def it(s):
    return f'<tspan font-style="italic">{s}</tspan>'


def sub(s, size=NAME):
    return (f'<tspan font-size="{0.76 * size:.1f}" dy="4">{s}</tspan>'
            f'<tspan dy="-4">&#8203;</tspan>')


def num(v):
    """Integer with a real minus sign."""
    return (MINUS + str(-v)) if v < 0 else str(v)


def triple(*vs):
    return "(" + ", ".join(v if isinstance(v, str) else num(v) for v in vs) + ")"


def pt_name(letter, idx=None, size=NAME):
    return it(letter) + (sub(idx, size) if idx else "")


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


DIRS = {"r": 0, "ur": 45, "u": 90, "ul": 135, "l": 180, "dl": 225, "d": 270, "dr": 315}
DEFAULT_ORDER = ["ur", "r", "ul", "u", "dr", "d", "dl", "l",
                 22.5, 67.5, 112.5, 157.5, 202.5, 247.5, 292.5, 337.5]


# ---------------------------------------------------------------------------
# the figure object: a Space plus a registry of what is drawn, in pixels
# ---------------------------------------------------------------------------


class Fig:
    def __init__(self, az, el, extent, width=600, pad=80):
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

    # -- projection ---------------------------------------------------------
    def px(self, P):
        X, Y = self.S.pt(P)
        return (self.p.X(X), self.p.Y(Y))

    def depth(self, P):
        return vdot(P, self.d)

    def u(self, pixels):
        """Pixels -> space units."""
        return pixels / self.ppu

    def _reg(self, Ps, w=1.0):
        self._reg_px([self.px(P) for P in Ps], w)

    def _reg_px(self, q, w=1.0):
        self.sid += 1
        for a, b in zip(q, q[1:]):
            self.segs.append((a, b, w, self.sid))

    # -- drawing ------------------------------------------------------------
    def line(self, Ps, color=TEXT, width=1.6, dash=None, opacity=1.0, w=1.0):
        self.S.line(Ps, color, width, dash, opacity)
        if w:
            self._reg(Ps, w)

    def guide(self, Ps, color=TEXT, opacity=0.5, width=1.0, dash="4 3", w=0.7):
        self.line(Ps, color, width, dash, opacity, w)

    def arrow(self, P0, P1, color=THEORY, width=2.2, head=10.0, dash=None, opacity=1.0, w=1.0):
        self.S.arrow(P0, P1, color, width, head, dash, opacity)
        self._reg([P0, P1], w)

    def polygon(self, Ps, fill=THEORY, opacity=0.14):
        self.S.polygon(Ps, fill, opacity)

    def point(self, P, color=TEXT, r=4.0):
        self.S.point(P, color, r)
        x, y = self.px(P)
        self.dots.append((x, y, r))

    def hollow(self, P, color=TEXT, r=3.6):
        self.S.hollow(P, color, r)
        x, y = self.px(P)
        self.dots.append((x, y, r))

    def split(self, Ps, flag):
        """Cut a sampled polyline into runs on which flag(point) is constant."""
        runs, cur, state = [], [Ps[0]], flag(Ps[0])
        for P in Ps[1:]:
            f = flag(P)
            if f != state:
                runs.append((state, cur + [P]))
                cur, state = [P], f
            else:
                cur.append(P)
        runs.append((state, cur))
        return runs

    def styled(self, Ps, flag, on, off):
        """Draw a polyline with style `on` where flag holds and `off` elsewhere
        (each style a dict of line() keywords, or None to skip)."""
        for state, run in self.split(Ps, flag):
            st = on if state else off
            if st is not None and len(run) > 1:
                self.line(run, **st)

    def right_angle(self, Q, a, b, size=11, color=TEXT, width=1.1, opacity=0.8):
        s = self.u(size)
        a, b = vunit(a), vunit(b)
        pts = [vadd(Q, vscale(s, a)), vadd(Q, vadd(vscale(s, a), vscale(s, b))), vadd(Q, vscale(s, b))]
        self.line(pts, color, width, None, opacity, w=0.5)

    def sphere(self, C, r, color, fill=0.13, lats=(-60, -30, 30, 60), lons=6, eq_width=1.7):
        """Translucent sphere: shaded disk, faint latitude/longitude net (front lines
        stronger than back ones), outline and a bold equator whose back half is dashed."""
        cx, cy = self.px(C)
        R = r * self.ppu
        self.p.add(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{R:.1f}" fill="{color}" '
                   f'fill-opacity="{fill}" stroke="none"/>')
        # soft relief that works in both themes: more of the sphere colour towards the rim
        for rr, ww, op in ((0.95, 0.10, 0.05), (0.89, 0.14, 0.04), (0.82, 0.18, 0.035),
                           (0.73, 0.22, 0.03), (0.62, 0.26, 0.02)):
            self.p.add(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{rr * R:.1f}" fill="none" '
                       f'stroke="{color}" stroke-width="{ww * R:.1f}" stroke-opacity="{op}"/>')

        def front(Q):
            return vdot(vsub(Q, C), self.d) >= 0

        def ring(f, n=120):
            return [f(2 * math.pi * k / n) for k in range(n + 1)]

        grid_on = dict(color=color, width=0.8, opacity=0.42, w=0.15)
        grid_off = dict(color=color, width=0.7, opacity=0.16, w=0.0)
        for lat in lats:
            a = math.radians(lat)
            self.styled(ring(lambda t: vadd(C, (r * math.cos(a) * math.cos(t), r * math.cos(a) * math.sin(t),
                                                r * math.sin(a)))), front, grid_on, grid_off)
        for k in range(lons):
            ph = math.pi * k / lons
            self.styled(ring(lambda t: vadd(C, (r * math.cos(t) * math.cos(ph), r * math.cos(t) * math.sin(ph),
                                                r * math.sin(t)))), front, grid_on, grid_off)
        # outline (the silhouette circle of an orthographic view)
        self.p.add(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{R:.1f}" fill="none" stroke="{color}" '
                   f'stroke-width="1.4" opacity="0.8"/>')
        self._reg_px([(cx + R * math.cos(2 * math.pi * k / 96), cy + R * math.sin(2 * math.pi * k / 96))
                      for k in range(97)], 1.0)
        self.styled(ring(lambda t: vadd(C, (r * math.cos(t), r * math.sin(t), 0.0))), front,
                    dict(color=color, width=eq_width, opacity=0.95),
                    dict(color=color, width=1.2, dash="5 4", opacity=0.65))

    # -- axes -------------------------------------------------------------
    def axes(self, rng, neg="dash", labels=("X", "Y", "Z"), width=1.3, opacity=0.8,
             color=TEXT, hidden=None, head=9.0):
        """Coordinate axes over the given (lo, hi) ranges, arrowheads at the positive ends.
        neg: 'dash' draws the negative parts thin and dashed, 'solid' like the positive parts.
        hidden(P) -> True marks a stretch as hidden behind a surface (drawn dashed, faint)."""
        E = ((1, 0, 0), (0, 1, 0), (0, 0, 1))
        for k, (lo, hi) in enumerate(rng):
            e = E[k]
            vis = dict(color=color, width=width, opacity=opacity, w=1.0)
            hid = dict(color=color, width=1.0, dash="4 3", opacity=0.45, w=0.5)
            negst = hid if neg == "dash" else vis
            n = 240
            if lo < 0:
                pts = [vscale(lo * (1 - j / 60), e) for j in range(61)]
                self.styled(pts, (lambda P: not hidden(P)) if hidden else (lambda P: True), negst, hid)
            tip = vscale(hi, e)
            pts = [vscale(hi * j / n, e) for j in range(n + 1)]
            cut = int(n * max(0.0, 1 - self.u(head * 1.4) / hi))
            self.styled(pts[:cut + 1], (lambda P: not hidden(P)) if hidden else (lambda P: True), vis, hid)
            self.arrow(pts[cut], tip, color, width, head, None, opacity, w=1.0)
            if labels and labels[k]:
                self.axis_label(e, tip, labels[k])

    def axis_label(self, e, tip, s, size=AXIS, gap=8):
        x0, y0 = self.px((0, 0, 0))
        x1, y1 = self.px(tip)
        L = math.hypot(x1 - x0, y1 - y0) or 1.0
        ax, ay = (x1 - x0) / L, (y1 - y0) / L
        w, h = text_width(s, size), size
        ext = min(w / 2 / abs(ax) if ax else 1e9, h / 2 / abs(ay) if ay else 1e9)
        cx, cy = x1 + ax * (gap + ext), y1 + ay * (gap + ext)
        self._text(cx, cy, it(s), size, TEXT, w, h)

    def ticks(self, axis, vals, size=TICK, side=None, length=6.0, label=True, skip=(), limit=12.0):
        """Tick marks across an axis and numbers beside them: both sides of the axis are
        tried (or only `side`, +1/-1 along the page normal), also slid a little along the
        axis; a number that finds no clean spot (cost above `limit`) is left out and reported."""
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
            self._tick_labels(k, vals, size, side, limit, ax, ay, nx, ny)

    def _tick_labels(self, k, vals, size, side, limit, ax, ay, nx, ny):
        axis = "xyz"[k]
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
                print(f"   tick {axis}={v}: no clean spot (cost {best[0]:.1f}), number left out")
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

    def _text(self, cx, cy, s, size, color, w, h, opacity=1.0, halo=True, bold=False):
        """Text whose (estimated) box is centred on (cx, cy)."""
        self.boxes.append((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2))
        base = cy + 0.28 * h
        extra = ' font-weight="600"' if bold else ""
        op = f' opacity="{opacity}"' if opacity < 1 else ""
        stroke = (f' stroke="{BG}" stroke-width="3.6" stroke-linejoin="round" paint-order="stroke"'
                  if halo else "")
        self.texts.append(f'<text x="{cx:.1f}" y="{base:.1f}" fill="{color}" font-size="{size}" '
                          f'text-anchor="middle"{extra}{op}{stroke}>{s}</text>')

    def place(self, anchor, s, size=NAME, color=TEXT, prefs=None, d=7.0, leader=False,
              opacity=1.0, only=False, far=(0, 7, 15, 26, 40), vec=False):
        """Put text s next to anchor (a space point, or a pixel pair given as ('px', x, y)).
        Candidates lie on a ring around the anchor; the cheapest one (no lines, points or
        labels under it; earlier entries of prefs win ties) is used. prefs may contain 'c'
        (centred on the anchor). With leader=True a far placement gets a thin guide line."""
        self._flush()
        if isinstance(anchor, tuple) and anchor and anchor[0] == "px":
            x, y = anchor[1], anchor[2]
        else:
            x, y = self.px(anchor)
        w, h = text_width(s, size), size + (5 if vec else 0)
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
            # guide from the anchor to the nearest point of the text box
            bx = min(max(x, cx - w / 2), cx + w / 2)
            by = min(max(y, cy - h / 2), cy + h / 2)
            L = math.hypot(bx - x, by - y)
            if L > 8:
                ux, uy = (bx - x) / L, (by - y) / L
                self.texts.insert(0, f'<line x1="{x + ux * 5:.1f}" y1="{y + uy * 5:.1f}" x2="{bx - ux * 3:.1f}" '
                                     f'y2="{by - uy * 3:.1f}" stroke="{color}" stroke-width="0.9" opacity="0.7"/>')
        if vec:
            cy2 = cy + 2.5
            self._text(cx, cy2, s, size, color, w, size, opacity)
            self.boxes[-1] = (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)
            ytop = cy2 - size / 2 - 3.5
            x0a, x1a = cx - w / 2 + 1, cx + w / 2 + 1
            self.texts.append(f'<line x1="{x0a:.1f}" y1="{ytop:.1f}" x2="{x1a - 3:.1f}" y2="{ytop:.1f}" '
                              f'stroke="{color}" stroke-width="1.1"/>')
            self.texts.append(f'<polygon points="{x1a:.1f},{ytop:.1f} {x1a - 5:.1f},{ytop - 2.6:.1f} '
                              f'{x1a - 5:.1f},{ytop + 2.6:.1f}" fill="{color}"/>')
        else:
            self._text(cx, cy, s, size, color, w, h, opacity)
        return cx, cy

    # -- output -------------------------------------------------------------
    def render(self, name, caption, aria):
        self._flush()
        print(f"-- {name} (warnings above belong to it)")
        for t in self.texts:
            self.p.add(t)
        OUT[name] = figure(round(self.W), round(self.H), [self.p], caption, WIDE, aria)


def box_edges(lo, hi, d):
    """The 12 edges of the box [lo, hi] with a flag: False when both faces meeting at
    the edge turn away from the viewer (a hidden edge)."""
    corners = {}
    for i in (0, 1):
        for j in (0, 1):
            for k in (0, 1):
                corners[(i, j, k)] = (hi[0] if i else lo[0], hi[1] if j else lo[1], hi[2] if k else lo[2])

    def face_front(axis, side):
        return (d[axis] > 0) if side else (d[axis] < 0)

    out = []
    for a in range(3):
        b, c = [t for t in range(3) if t != a]
        for sb in (0, 1):
            for sc in (0, 1):
                i0, i1 = [0, 0, 0], [0, 0, 0]
                i0[b] = i1[b] = sb
                i0[c] = i1[c] = sc
                i1[a] = 1
                vis = face_front(b, sb) or face_front(c, sc)
                out.append((corners[tuple(i0)], corners[tuple(i1)], vis))
    return out


def disc(C, r, n=120, z=None):
    return [(C[0] + r * math.cos(2 * math.pi * k / n), C[1] + r * math.sin(2 * math.pi * k / n),
             C[2] if z is None else z) for k in range(n + 1)]


def dist2(A, B):
    return sum((Fraction(a) - Fraction(b)) ** 2 for a, b in zip(A, B))


O3 = (0.0, 0.0, 0.0)


# ============================================================ eksenler-ve-sag-el
f = Fig(35, 22, [(-1, 0, 0), (4, 0, 0), (0, -1, 0), (0, 4, 0), (0, 0, -1), (0, 0, 4)], width=560)
f.axes(((-1, 4), (-1, 4), (-1, 4)), neg="dash", width=1.5, opacity=0.85)
arc = [(1.2 * math.cos(t), 1.2 * math.sin(t), 0.0) for t in
       (math.pi / 2 * k / 80 for k in range(81))]
f.line(arc[:-6], PRACTICE, 2.2)
f.arrow(arc[-8], arc[-1], PRACTICE, 2.2, 11)
B0, B1 = (0.55, 0.95, 0.45), (0.55, 0.95, 1.85)
f.arrow(B0, B1, THEORY, 4.0, 15)
for ax in "xyz":
    f.ticks(ax, (1, 2, 3))
f.place(O3, it("O"), NAME, prefs=[240, 250, 230, "dl"], only=False)
f.place(vscale(0.5, vadd(B0, B1)), "sağ el kuralı", DESC, THEORY, prefs=["r"])
f.render(
    "eksenler-ve-sag-el",
    "Sağ el kuralına göre yönlendirilmiş eksenler: <em>X</em>-ekseni okuyucuya doğru (sol aşağı), "
    "<em>Y</em>-ekseni sağa, <em>Z</em>-ekseni yukarı. Pozitif <em>X</em>-ekseninden pozitif "
    "<em>Y</em>-eksenine kıvrılan parmaklar (turuncu ok) başparmağı pozitif <em>Z</em>-ekseni "
    "yönüne (mavi ok) getirir. Eksenlerin negatif kısımları kesiklidir.",
    "Three coordinate axes X, Y, Z through O with ticks 1, 2, 3; a quarter-circle arrow in the XY "
    "plane from the positive X axis to the positive Y axis and a thick upward arrow beside the Z "
    "axis labelled right hand rule")

# ============================================================ koordinat-duzlemleri
A = 3.0
f = Fig(35, 22, [(A, A, 0), (-A, -A, 0), (A, -A, 0), (-A, A, 0), (0, 0, 3.8), (0, 0, -A), (3.8, 0, 0)],
        width=600)
for P0, e1, e2, col in (((0, 0, 0), (1, 0, 0), (0, 1, 0), THEORY),
                        ((0, 0, 0), (0, 1, 0), (0, 0, 1), BASE),
                        ((0, 0, 0), (1, 0, 0), (0, 0, 1), PRACTICE)):
    f.S.parallelogram(P0, e1, e2, (-A, A), (-A, A), col, 0.13)
    cs = [vadd(vscale(a, e1), vscale(b, e2)) for a, b in ((-A, -A), (A, -A), (A, A), (-A, A), (-A, -A))]
    f.line(cs, col, 1.1, None, 0.6, w=0.6)
f.axes(((-A, 3.8), (-A, 3.8), (-A, 3.8)), neg="solid", width=2.0, opacity=0.9)
f.place(O3, it("O"), NAME, prefs=[250, 235, 265, 215])
f.place((2.3, -2.35, 0), it("XY") + "-düzlemi", NAME, THEORY, prefs=["c"], only=False)
f.place((0, 2.0, 2.35), it("YZ") + "-düzlemi", NAME, BASE, prefs=["c"], only=False)
f.place((2.2, 0, -2.45), it("XZ") + "-düzlemi", NAME, PRACTICE, prefs=["c"], only=False)
f.render(
    "koordinat-duzlemleri",
    "Üç koordinat düzlemi: <em>XY</em>-düzlemi (<em>z</em> = 0, mavi), <em>YZ</em>-düzlemi "
    "(<em>x</em> = 0, yeşil) ve <em>XZ</em>-düzlemi (<em>y</em> = 0, turuncu). İkişer ikişer "
    "kesişme doğruları koordinat eksenleridir; düzlemlerin yalnız −3 ile 3 arasındaki parçaları "
    "çizilmiştir.",
    "The three coordinate planes as translucent squares from -3 to 3: XY plane blue, YZ plane "
    "green, XZ plane orange, meeting along the X, Y and Z axes at O")

# ============================================================ nokta-ve-koordinatlari
P = (3.0, 4.0, 3.0)
Pxy, Fx, Fy, Fz = (3.0, 4.0, 0.0), (3.0, 0.0, 0.0), (0.0, 4.0, 0.0), (0.0, 0.0, 3.0)
f = Fig(35, 22, [(4, 0, 0), (0, 5, 0), (0, 0, 4), O3], width=560)
for a, b, _ in box_edges((0, 0, 0), P, f.d):
    f.line([a, b], TEXT, 0.8, None, 0.22, w=0.3)
f.axes(((0, 4), (0, 5), (0, 4)), width=1.5)
f.guide([P, Pxy], TEXT, 0.75, 1.3, "5 4")
f.guide([Pxy, Fx], TEXT, 0.75, 1.3, "5 4")
f.guide([Pxy, Fy], TEXT, 0.75, 1.3, "5 4")
f.guide([P, Fz], TEXT, 0.75, 1.3, "5 4")
f.right_angle(Pxy, (-1, 0, 0), (0, -1, 0), 14)
f.right_angle(Pxy, (0, 0, 1), (0, -1, 0), 14)
f.right_angle(Fx, (-1, 0, 0), (0, 1, 0), 14)
f.right_angle(Fy, (0, -1, 0), (1, 0, 0), 14)
f.right_angle(Fz, (0, 0, -1), (3, 4, 0), 14)
f.point(P, PRACTICE, 4.6)
f.point(Pxy, TEXT, 3.6)
for Q in (Fx, Fy, Fz):
    f.point(Q, TEXT, 3.2)
f.place(O3, it("O"), NAME, prefs=[250, 235, 265])
f.place(P, it("P") + "(" + it("x") + ", " + it("y") + ", " + it("z") + ")", NAME, PRACTICE, prefs=["ur", "r"])
f.place(Pxy, pt_name("P", it("xy")), NAME, prefs=["dr", "r", "d"])
f.place(Fx, it("x"), NAME, prefs=["dl", "d", "l"])
f.place(Fy, it("y"), NAME, prefs=["d", "dr", "dl"])
f.place(Fz, it("z"), NAME, prefs=["l", "ul", "dl"])
f.render(
    "nokta-ve-koordinatlari",
    "<em>P</em> noktasının koordinatları: <em>P</em>&#8217;den <em>XY</em>-düzlemine inilen dikmenin "
    "ayağı <em>P</em><sub><em>xy</em></sub>&#8217;dir; <em>P</em><sub><em>xy</em></sub>&#8217;den "
    "eksenlere inilen dikmeler <em>x</em> ve <em>y</em>&#8217;yi, <em>P</em>&#8217;den <em>Z</em>-eksenine "
    "inilen dikme <em>z</em>&#8217;yi verir.",
    "Point P above the XY plane with the dashed perpendicular to its foot P_xy, dashed lines from "
    "P_xy to the points x and y on the X and Y axes, a dashed line from P to the point z on the Z "
    "axis, right angle marks and a faint box for depth")

# ============================================================ bolgeler
A = 3.0
f = Fig(35, 22, [(A, A, 0), (-A, -A, 0), (A, -A, 0), (-A, A, 0), (0, 0, 3.8), (0, 0, -A), (3.8, 0, 0)],
        width=620)
for P0, e1, e2 in (((0, 0, 0), (1, 0, 0), (0, 1, 0)), ((0, 0, 0), (0, 1, 0), (0, 0, 1)),
                   ((0, 0, 0), (1, 0, 0), (0, 0, 1))):
    f.S.parallelogram(P0, e1, e2, (-A, A), (-A, A), TEXT, 0.05)
    cs = [vadd(vscale(a, e1), vscale(b, e2)) for a, b in ((-A, -A), (A, -A), (A, A), (-A, A), (-A, -A))]
    f.line(cs, TEXT, 0.9, None, 0.28, w=0.4)
for Ps in (((A, 0, 0), (A, A, 0), (A, A, A), (A, 0, A)), ((0, A, 0), (A, A, 0), (A, A, A), (0, A, A)),
           ((0, 0, A), (A, 0, A), (A, A, A), (0, A, A))):
    f.polygon(Ps, PRACTICE, 0.13)
for a, b, vis in box_edges((0, 0, 0), (A, A, A), f.d):
    if vis:
        f.line([a, b], PRACTICE, 1.1, None, 0.55, w=0.5)
f.axes(((-A, 3.8), (-A, 3.8), (-A, 3.8)), neg="solid", width=1.6, opacity=0.85)
f.place(O3, it("O"), NAME, prefs=[250, 235, 265, 215])
octs = []
for sx in (1, -1):
    for sy in (1, -1):
        for sz in (1, -1):
            octs.append((sx, sy, sz))
deps = [vdot((sx, sy, sz), f.d) for sx, sy, sz in octs]
lo, hi = min(deps), max(deps)
for (sx, sy, sz), dep in sorted(zip(octs, deps), key=lambda t: -t[1]):
    s = "(" + ",".join("+" if v > 0 else MINUS for v in (sx, sy, sz)) + ")"
    op = round(0.5 + 0.5 * (dep - lo) / (hi - lo), 2)
    f.place((1.5 * sx, 1.5 * sy, 1.5 * sz), s, NAME, TEXT, prefs=["c"], opacity=op, d=4)
f.render(
    "bolgeler",
    "Koordinat düzlemleri uzayı sekiz bölgeye ayırır; her bölge, içindeki noktaların koordinat "
    "işaretleriyle anılır. Turuncu kutu birinci bölgenin (+,+,+) bir parçasıdır; arkada kalan "
    "bölgelerin etiketleri daha soluktur.",
    "The three coordinate planes as faint squares from -3 to 3 and the eight octants labelled by "
    "their sign triples at the points plus or minus 1.5; the first octant box is shaded orange")

# ============================================================ dikme-ayaklari-ornegi
P = (2.0, -3.0, 4.0)
feet_pl = [(2.0, -3.0, 0.0), (0.0, -3.0, 4.0), (2.0, 0.0, 4.0)]
feet_ax = [(2.0, 0.0, 0.0), (0.0, -3.0, 0.0), (0.0, 0.0, 4.0)]
f = Fig(22, 22, [(3, 0, 0), (-1, 0, 0), (0, -4, 0), (0, 2, 0), (0, 0, 5), (0, 0, -1)], width=560)
for a, b, _ in box_edges((0, -3, 0), (2, 0, 4), f.d):
    f.line([a, b], TEXT, 1.0, "3 3", 0.42, w=0.6)
f.axes(((-1, 3), (-4, 2), (-1, 5)), neg="solid", width=1.5)
f.guide([P, feet_pl[0]], PRACTICE, 0.95, 2.0, "6 4", w=1)
f.guide([P, feet_pl[1]], BASE, 0.95, 2.0, "6 4", w=1)
f.guide([P, feet_pl[2]], THEORY, 0.95, 2.0, "6 4", w=1)
f.ticks("x", (1, 2), skip=(2,))
f.ticks("y", (-3, -2, -1, 1), skip=(-3,))
f.ticks("z", (1, 2, 3, 4), skip=(4,))
f.point(P, TEXT, 5.0)
f.point(feet_pl[0], PRACTICE, 3.8)
f.point(feet_pl[1], BASE, 3.8)
f.point(feet_pl[2], THEORY, 3.8)
for Q in feet_ax:
    f.point(Q, TEXT, 3.4)
f.place(O3, it("O"), NAME, prefs=[300, 315, 285])
f.place(P, it("P") + triple(2, -3, 4), NAME, prefs=["ul", "u", "l"])
f.place(feet_pl[0], pt_name("P", it("xy")) + " = " + triple(2, -3, 0), DESC, PRACTICE, prefs=["dl", "l", "d"])
f.place(feet_pl[1], triple(0, -3, 4), DESC, BASE, prefs=["l", "ul", "u"])
f.place(feet_pl[2], triple(2, 0, 4), DESC, THEORY, prefs=["r", "ur", "dr"])
f.place(feet_ax[0], triple(2, 0, 0), DESC, prefs=["dr", "r", "d"])
f.place(feet_ax[1], triple(0, -3, 0), DESC, prefs=["d", "dl", "dr"])
f.place(feet_ax[2], triple(0, 0, 4), DESC, prefs=["ur", "r", "u"])
f.render(
    "dikme-ayaklari-ornegi",
    "<em>P</em>(2, −3, 4) noktası ve kenarları eksenlere paralel prizma. Renkli kesikli çizgiler "
    "<em>P</em>&#8217;den <em>XY</em>-, <em>YZ</em>- ve <em>XZ</em>-düzlemlerine inilen dikmelerdir; "
    "eksenler üzerindeki üç nokta, eksenlere inilen dikmelerin ayaklarıdır.",
    "Point P(2, -3, 4) with the dashed box of edges parallel to the axes, the colored dashed "
    "perpendiculars from P to its feet on the three coordinate planes and the feet on the three axes")

# ============================================================ yz-duzlemi
f = Fig(28, 20, [(3, 0, 0), (0, -3, 0), (0, 3.7, 0), (0, 0, 3.7), (0, 0, -3), (0, 3, 3), (0, -3, -3)],
        width=560)
f.S.parallelogram(O3, (0, 1, 0), (0, 0, 1), (-3, 3), (-3, 3), BASE, 0.16)
cs = [(0, -3, -3), (0, 3, -3), (0, 3, 3), (0, -3, 3), (0, -3, -3)]
f.line(cs, BASE, 1.8, None, 0.9)
f.axes(((0, 3), (-3, 3.7), (-3, 3.7)), neg="solid", width=1.9, opacity=0.9)
f.ticks("y", (1, 2, 3))
f.ticks("z", (1, 2, 3))
f.place(O3, it("O"), NAME, prefs=[250, 235, 265, 215])
f.place((0, 2.1, 2.45), it("x") + " = 0", NAME + 1, BASE, prefs=["c"])
f.render(
    "yz-duzlemi",
    "<em>x</em> = 0 denklemini sağlayan noktalar <em>YZ</em>-koordinat düzlemini oluşturur; "
    "düzlemin −3 ≤ <em>y</em> ≤ 3, −3 ≤ <em>z</em> ≤ 3 karesiyle sınırlı parçası çizilmiştir. "
    "Pozitif <em>X</em>-ekseni düzlemden okuyucuya doğru çıkar.",
    "The YZ plane x = 0 as a green translucent square from -3 to 3 in y and z, the positive X axis "
    "coming out toward the reader, ticks 1, 2, 3 on the Y and Z axes")

# ============================================================ z-bir-duzlemi
f = Fig(35, 24, [(3, 0, 0), (-2, 0, 0), (0, 3, 0), (0, -2, 0), (0, 0, 3), (0, 0, -1),
                 (2, 2, 1), (-2, -2, 1), (2, -2, 1), (-2, 2, 1)], width=580)
Hz = 1.0


def under_plane(Q):
    """Below z = 1 and seen through the square |x|, |y| <= 2 of that plane."""
    if Q[2] >= Hz - 1e-9:
        return False
    t = (Hz - Q[2]) / f.d[2]
    x, y = Q[0] + t * f.d[0], Q[1] + t * f.d[1]
    return abs(x) <= 2 and abs(y) <= 2


f.axes(((-2, 3), (-2, 3), (-1, 3)), neg="solid", width=1.5, hidden=under_plane)
f.S.parallelogram((0, 0, Hz), (1, 0, 0), (0, 1, 0), (-2, 2), (-2, 2), THEORY, 0.17)
cs = [(-2, -2, Hz), (2, -2, Hz), (2, 2, Hz), (-2, 2, Hz), (-2, -2, Hz)]
f.line(cs, THEORY, 1.8, None, 0.95)
f.ticks("z", (1, 2), side=-1)
f.point((0, 0, Hz), THEORY, 4.4)
f.place(O3, it("O"), NAME, prefs=[250, 235, 265, 215])
f.place((0, 0, Hz), "(0, 0, 1)", NAME, THEORY, prefs=["r", "ur", "dr"])
f.place((-1.2, 1.55, Hz), it("z") + " = 1", NAME + 1, THEORY, prefs=["c"])
f.render(
    "z-bir-duzlemi",
    "<em>z</em> = 1 düzlemi: <em>XY</em>-düzleminin 1 birim yukarısında ve ona paralel. "
    "<em>Z</em>-ekseni düzlemi (0, 0, 1) noktasında deler; düzlemin arkasında kalan eksen parçaları "
    "kesikli ve soluktur.",
    "The plane z = 1 as a blue translucent square from -2 to 2 in x and y, pierced by the Z axis at "
    "(0, 0, 1); axis parts behind the plane are dashed")

# ============================================================ x1-y2-dogrusu
f = Fig(32, 20, [(3, 0, 0), (0, 4, 0), (0, 0, 3), (0, 0, -2), (1, 2, 3), (1, 2, -2)], width=520)
f.S.parallelogram((1, 0, 0), (0, 1, 0), (0, 0, 1), (0, 3), (-2, 3), THEORY, 0.10)
f.S.parallelogram((0, 2, 0), (1, 0, 0), (0, 0, 1), (0, 2), (-2, 3), BASE, 0.10)
f.axes(((0, 3), (0, 4), (-2, 3)), neg="solid", width=1.5)
f.guide([(1, 0, 0), (1, 2, 0)], TEXT, 0.7, 1.2, "5 4")
f.guide([(0, 2, 0), (1, 2, 0)], TEXT, 0.7, 1.2, "5 4")
f.line([(1, 2, -2), (1, 2, 0)], PRACTICE, 3.0, "7 5", 0.95)
f.line([(1, 2, 0), (1, 2, 3)], PRACTICE, 3.2, None, 1.0)
f.ticks("x", (1,))
f.ticks("y", (1, 2, 3))
f.point((1, 2, 0), TEXT, 4.4)
f.place(O3, it("O"), NAME, prefs=[250, 235, 265, 215])
f.place((1, 2, 0), "(1, 2, 0)", NAME, prefs=["dr", "r", "d"])
cx, cy = f.px((1, 2, 3))
f.place(("px", cx, cy + 2), it("x") + " = 1", NAME, PRACTICE, prefs=["r"], d=10)
f.place(("px", cx, cy + 22), it("y") + " = 2", NAME, PRACTICE, prefs=["r"], d=10)
f.render(
    "x1-y2-dogrusu",
    "<em>x</em> = 1, <em>y</em> = 2 koşullarını sağlayan noktalar, (1, 2, 0) noktasından geçen ve "
    "<em>Z</em>-eksenine paralel olan doğruyu oluşturur. Soluk mavi ve yeşil parçalar "
    "<em>x</em> = 1 ve <em>y</em> = 2 düzlemleridir; doğru bu iki düzlemin kesişimidir. Doğrunun "
    "<em>XY</em>-düzleminin altındaki kısmı kesiklidir.",
    "The vertical line x = 1, y = 2 through (1, 2, 0), solid above the XY plane and dashed below, "
    "with faint pieces of the planes x = 1 and y = 2 meeting along it")

# ============================================================ dolu-silindir
f = Fig(35, 20, [(2, 0, 0), (-2, 0, 0), (0, 2, 0), (0, -2, 0), (0, 0, 2.5), (0, 0, -2)], width=520)
h0, h1 = -1.5, 1.5
phs = [math.atan2(-f.d[0], f.d[1]), math.atan2(f.d[0], -f.d[1])]   # silhouette angles


def cyl(ph, z):
    return (math.cos(ph), math.sin(ph), z)


def front_rim(Q):
    return Q[0] * f.d[0] + Q[1] * f.d[1] >= 0


f.axes(((-2, 2), (-2, 2), (-2, 2.5)), neg="solid", width=1.4,
       hidden=lambda Q: (abs(Q[0]) < 1e-12 and abs(Q[1]) < 1e-12
                         and h0 - f.d[2] / math.hypot(f.d[0], f.d[1]) <= Q[2] <= h1))
# side surface: region between the silhouette lines, bounded by the front rims
a0 = phs[0]
fr = [a0 + math.pi * k / 90 for k in range(91)]
if not front_rim(cyl(fr[45], 0)):
    fr = [a0 - math.pi * k / 90 for k in range(91)]
outline = [cyl(t, h1) for t in fr] + [cyl(t, h0) for t in reversed(fr)]
f.S.polygon(disc((0, 0, h1), 1.0), PRACTICE, 0.10)
f.S.polygon(outline, PRACTICE, 0.13)
f.S.polygon(disc((0, 0, 0), 1.0), PRACTICE, 0.22)
f.line(disc((0, 0, 0), 1.0), PRACTICE, 1.9, None, 1.0)
for ph in phs:
    f.line([cyl(ph, h0), cyl(ph, h1)], PRACTICE, 1.7, None, 0.95)
f.line(disc((0, 0, h1), 1.0), PRACTICE, 1.9, None, 1.0)
f.styled(disc((0, 0, h0), 1.0, 240), front_rim, dict(color=PRACTICE, width=1.9, opacity=1.0),
         dict(color=PRACTICE, width=1.3, dash="5 4", opacity=0.75))
f.line([O3, (0, 1, 0)], TEXT, 2.4, None, 0.95)
f.ticks("y", (1,), label=False)
f.point((0, 1, 0), TEXT, 3.2)
f.place(O3, it("O"), NAME, prefs=[160, 180, 200, 140])
f.place(vscale(0.5, (0, 1, 0)), "1", NAME, prefs=["u", "ul", "ur"], d=5)
cx, cy = f.px(cyl(phs[0] if f.px(cyl(phs[0], h1))[0] > f.px(cyl(phs[1], h1))[0] else phs[1], h1))
f.place(("px", cx, cy + 6), it("x") + "² + " + it("y") + "² ≤ 1", NAME, PRACTICE, prefs=["r", "ur"], d=12)
f.render(
    "dolu-silindir",
    "<em>x</em>² + <em>y</em>² ≤ 1 kümesi: <em>Z</em>-ekseni çevresindeki, yarıçapı 1 olan dolu "
    "silindir (−1,5 ≤ <em>z</em> ≤ 1,5 parçası). Koyu taralı daire <em>XY</em>-düzlemindeki "
    "kesittir; aynı daire her yükseklikte tekrarlanır.",
    "Solid circular cylinder x^2 + y^2 at most 1 around the Z axis for z from -1.5 to 1.5, with "
    "its top and bottom circles, the shaded unit disk in the XY plane and the radius 1 from O "
    "along the Y axis")

# ============================================================ birim-kup
f = Fig(35, 22, [(2, 0, 0), (0, 2, 0), (0, 0, 2), O3], width=500)
for Ps in (((1, 0, 0), (1, 1, 0), (1, 1, 1), (1, 0, 1)), ((0, 1, 0), (1, 1, 0), (1, 1, 1), (0, 1, 1)),
           ((0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1))):
    f.polygon(Ps, THEORY, 0.17)


def in_cube_back(Q):
    return all(0 <= c <= 1 + 1e-9 for c in Q)


f.axes(((0, 2), (0, 2), (0, 2)), width=1.5, hidden=in_cube_back)
for a, b, vis in box_edges((0, 0, 0), (1, 1, 1), f.d):
    if vis:
        f.line([a, b], THEORY, 2.0, None, 1.0)
for ax in "xyz":
    f.ticks(ax, (1,), label=False)
f.point((1, 1, 1), THEORY, 4.6)
f.place(O3, it("O"), NAME, prefs=[250, 235, 265, 215])
f.place((1, 0, 0), "1", NAME, prefs=["dr", "d", "r"])
f.place((0, 1, 0), "1", NAME, prefs=["d", "dr", "dl"])
f.place((0, 0, 1), "1", NAME, prefs=["l", "ul", "dl"])
f.place((1, 1, 1), "(1, 1, 1)", NAME, THEORY, prefs=["ur", "r", "u"])
f.render(
    "birim-kup",
    "Birim küp: 0 ≤ <em>x</em>, <em>y</em>, <em>z</em> ≤ 1. <em>O</em>&#8217;da buluşan üç ayrıtı "
    "eksenler üzerindedir ve arkada kaldıkları için kesiklidir; görünen üç yüz <em>x</em> = 1, "
    "<em>y</em> = 1 ve <em>z</em> = 1 yüzleridir.",
    "The unit cube with vertices 0 and 1 in each coordinate, three visible faces shaded, the "
    "hidden edges along the axes dashed and the vertex (1, 1, 1) marked")

# ============================================================ uzaklik-ispati
P1, P2, Qp = (1.0, 1.0, 1.0), (3.0, 5.0, 4.0), (3.0, 5.0, 1.0)
P1f, Qf = (1.0, 1.0, 0.0), (3.0, 5.0, 0.0)
f = Fig(18, 20, [(4, 0, 0), (0, 6, 0), (0, 0, 5), O3], width=600)
f.axes(((0, 4), (0, 6), (0, 5)), width=1.5)
f.polygon([P1, Qp, Qf, P1f], TEXT, 0.07)
f.guide([P1, P1f], TEXT, 0.6, 1.1)
f.guide([Qp, Qf], TEXT, 0.6, 1.1)
f.guide([P1f, Qf], TEXT, 0.6, 1.1)
f.line([P1, Qp], PRACTICE, 2.8)
f.line([Qp, P2], BASE, 2.8)
f.line([P1, P2], THEORY, 2.8)
f.right_angle(Qp, vsub(P1, Qp), (0, 0, 1), 12)
for Q in (P1, P2, Qp):
    f.point(Q, TEXT, 4.4)
for Q in (P1f, Qf):
    f.hollow(Q, TEXT, 3.8)
f.place(O3, it("O"), NAME, prefs=[250, 235, 265, 215])
f.place(P1, pt_name("P", "1") + "(" + pt_name("x", "1") + ", " + pt_name("y", "1") + ", "
        + pt_name("z", "1") + ")", NAME, prefs=[100, 90, 110, 120], only=True)
f.place(P2, pt_name("P", "2") + "(" + pt_name("x", "2") + ", " + pt_name("y", "2") + ", "
        + pt_name("z", "2") + ")", NAME, prefs=["ur", "u", "r"])
f.place(Qp, it("Q") + "(" + pt_name("x", "2") + ", " + pt_name("y", "2") + ", " + pt_name("z", "1") + ")",
        NAME, prefs=["ur", "r", "dr"])
f.place(P1f, pt_name("P", "1") + "′", NAME, prefs=["dl", "l", "d"])
f.place(Qf, it("Q") + "′", NAME, prefs=["dr", "r", "d"])
# the long label sits in the shaded strip under P1Q, below the Y axis that crosses the strip
# (|P1Q| = |P1'Q'|, so the label names both of the equal sides)
t_, s_ = 0.5, 0.62
qa = [f.px(vadd(vscale(1 - t_, U), vscale(t_, V))) for U, V in ((P1, Qp), (P1f, Qf))]
f.place(("px", qa[0][0] + s_ * (qa[1][0] - qa[0][0]), qa[0][1] + s_ * (qa[1][1] - qa[0][1])), SQRT + "((" + pt_name("x", "2", DESC) + " " + MINUS + " "
        + pt_name("x", "1", DESC) + ")² + (" + pt_name("y", "2", DESC) + " " + MINUS + " "
        + pt_name("y", "1", DESC) + ")²)", DESC, PRACTICE, prefs=["c"], d=6)
f.place(vscale(0.5, vadd(Qp, P2)), "|" + pt_name("z", "2", DESC) + " " + MINUS + " "
        + pt_name("z", "1", DESC) + "|", DESC, BASE, prefs=["r"], d=8)
f.render(
    "uzaklik-ispati",
    "Uzaklık formülünün ispatı: <em>Q</em> yardımcı noktasıyla <em>P</em><sub>1</sub><em>QP</em><sub>2</sub> "
    "üçgeni <em>Q</em>&#8217;da diktir. Yatay kenar <em>P</em><sub>1</sub><em>Q</em> (turuncu), "
    "<em>XY</em>-düzlemindeki <em>P</em><sub>1</sub>&#8242;<em>Q</em>&#8242; ile aynı uzunluktadır; "
    "düşey kenar <em>QP</em><sub>2</sub> (yeşil) kotların farkıdır; hipotenüs "
    "<em>P</em><sub>1</sub><em>P</em><sub>2</sub> (mavi) aranan uzaklıktır.",
    "Right triangle P1 Q P2 with the right angle at Q: horizontal leg P1 Q, vertical leg Q P2 and "
    "hypotenuse P1 P2; the feet P1' and Q' in the XY plane and the shaded rectangle P1 Q Q' P1'")

# ============================================================ kure-geometrik-yer
C0, R0 = (2.0, 3.0, 3.0), 2.0
f = Fig(35, 20, [(5, 0, 0), (0, 6, 0), (0, 0, 6), O3], width=560)
f.axes(((0, 5), (0, 6), (0, 6)), width=1.5)
f.sphere(C0, R0, THEORY)
e = vunit(vadd(vadd(vscale(0.62, f.cam.r), vscale(0.64, f.cam.u)), vscale(0.45, f.d)))
Pk = vadd(C0, vscale(R0, e))
f.line([C0, Pk], PRACTICE, 2.6)
f.point(C0, TEXT, 4.4)
f.point(Pk, PRACTICE, 4.4)
f.place(O3, it("O"), NAME, prefs=[250, 235, 265, 215])
f.place(C0, pt_name("P", "0") + "(" + pt_name("x", "0") + ", " + pt_name("y", "0") + ", "
        + pt_name("z", "0") + ")", NAME, prefs=["d", "dl", "dr"], d=8)
f.place(Pk, it("P") + "(" + it("x") + ", " + it("y") + ", " + it("z") + ")", NAME, PRACTICE,
        prefs=["ur", "r", "u"], d=9)
f.place(vscale(0.5, vadd(C0, Pk)), it("r"), NAME + 1, PRACTICE, prefs=["ul", "l", "u"], d=5)
f.render(
    "kure-geometrik-yer",
    "<em>P</em><sub>0</sub> noktasına uzaklığı <em>r</em> olan <em>P</em> noktaları, merkezi "
    "<em>P</em><sub>0</sub> ve yarıçapı <em>r</em> olan küreyi oluşturur. Koyu çember kürenin "
    "ekvatorudur; arkada kalan yarısı kesiklidir.",
    "Translucent sphere with center P0 and radius r, a point P on its surface joined to P0 by a "
    "red segment labelled r, the equator drawn bold with its back half dashed")

# ============================================================ ikizkenar-dik-ucgen
Ap, Bp, Cp = (-2.0, 5.0, 8.0), (-6.0, 7.0, 4.0), (-3.0, 4.0, 4.0)
assert dist2(Ap, Bp) == 36 and dist2(Bp, Cp) == 18 and dist2(Cp, Ap) == 18
f = Fig(38, 18, [(1, 0, 0), (-7, 0, 0), (0, 8, 0), (0, 0, 9), O3, Ap, Bp, Cp], width=600)
f.axes(((-7, 1), (0, 8), (0, 9)), neg="solid", width=1.5)
for Q in (Ap, Bp, Cp):
    f.guide([Q, (Q[0], Q[1], 0)], TEXT, 0.5, 1.0)
    f.hollow((Q[0], Q[1], 0), TEXT, 3.2)
f.polygon([Ap, Bp, Cp], BASE, 0.2)
f.line([Ap, Bp, Cp, Ap], BASE, 2.4)
f.right_angle(Cp, vsub(Ap, Cp), vsub(Bp, Cp), 13)
for Q in (Ap, Bp, Cp):
    f.point(Q, TEXT, 4.4)
f.place(O3, it("O"), NAME, prefs=[250, 235, 265, 215])
f.place(Ap, it("A") + triple(-2, 5, 8), NAME, prefs=["u", "ul", "ur"])
f.place(Bp, it("B") + triple(-6, 7, 4), NAME, prefs=["r", "ur", "dr"])
f.place(Cp, it("C") + triple(-3, 4, 4), NAME, prefs=["dl", "l", "d"])
f.place(vscale(0.5, vadd(Ap, Bp)), "6", NAME, BASE, prefs=["ur", "u", "r"], d=6)
f.place(vscale(0.5, vadd(Bp, Cp)), "3" + SQRT + "2", NAME, BASE, prefs=["d", "dr", "dl"], d=6)
f.place(vscale(0.5, vadd(Cp, Ap)), "3" + SQRT + "2", NAME, BASE, prefs=["l", "ul", "dl"], d=6)
f.render(
    "ikizkenar-dik-ucgen",
    "<em>A</em>(−2, 5, 8), <em>B</em>(−6, 7, 4), <em>C</em>(−3, 4, 4) üçgeni: |<em>BC</em>| = "
    "|<em>CA</em>| = 3√2 ve |<em>AB</em>| = 6 olduğundan <em>C</em> köşesinde dik ikizkenar üçgendir. "
    "Kesikli çizgiler köşelerden <em>XY</em>-düzlemine inen dikmelerdir.",
    "Triangle A(-2, 5, 8), B(-6, 7, 4), C(-3, 4, 4) shaded green with a right angle mark at C and "
    "side lengths 6, 3 root 2, 3 root 2; dashed drops from the vertices to the XY plane")

# ============================================================ kure-dort-nokta
M4, R4 = (1.0, 3.0, 4.0), 3.0
pts4 = {"A": (3.0, 2.0, 2.0), "B": (-1.0, 1.0, 3.0), "C": (0.0, 5.0, 6.0), "D": (2.0, 1.0, 2.0)}
for Q in pts4.values():
    assert dist2(Q, M4) == 9
f = Fig(35, 20, [(5, 0, 0), (-3, 0, 0), (0, 7, 0), (0, -1, 0), (0, 0, 8), O3], width=600)
f.axes(((-3, 5), (-1, 7), (0, 8)), neg="solid", width=1.4)
f.ticks("x", (-2, 2, 4))
f.ticks("y", (2, 4, 6))
f.ticks("z", (2, 4, 6))
f.sphere(M4, R4, PRACTICE)
cols = {"A": THEORY, "B": BASE, "C": PRACTICE, "D": REMARK}
for k, Q in pts4.items():
    back = vdot(vsub(Q, M4), f.d) < 0
    f.guide([M4, Q], TEXT, 0.4 if back else 0.75, 1.1, "4 3")
f.point(M4, TEXT, 4.6)
for k, Q in pts4.items():
    back = vdot(vsub(Q, M4), f.d) < 0
    f.S.p.add(f'<g opacity="{0.55 if back else 1}">')
    f.point(Q, cols[k], 4.6)
    f.S.p.add('</g>')
f.place(O3, it("O"), NAME, prefs=[250, 235, 265, 215])
f.place(M4, it("M") + triple(1, 3, 4), NAME, prefs=["dr", "d", "r"], d=6)
f.place(vscale(0.5, vadd(M4, pts4["C"])), "3", NAME, prefs=["ul", "l", "u"], d=5)
lab_pref = {"A": ["dr", "r", 300], "B": ["l", "ul", "dl"], "C": ["ur", "u", "r"], "D": ["dl", "d", 240]}
for k in "CBAD":
    Q = pts4[k]
    back = vdot(vsub(Q, M4), f.d) < 0
    f.place(Q, it(k) + triple(*[int(c) for c in Q]), NAME, cols[k], prefs=lab_pref[k], d=8,
            leader=True, opacity=0.8 if back else 1.0)
f.render(
    "kure-dort-nokta",
    "<em>A</em>, <em>B</em>, <em>C</em>, <em>D</em> noktalarının her biri <em>M</em>(1, 3, 4) "
    "merkezine 3 birim uzaklıktadır; dördü de yarıçapı 3 olan küre üzerindedir. Kürenin arka "
    "yüzündeki noktalar (<em>B</em> ve <em>D</em>) daha soluk çizilmiştir.",
    "Sphere with center M(1, 3, 4) and radius 3 with the four points A(3, 2, 2), B(-1, 1, 3), "
    "C(0, 5, 6), D(2, 1, 2) on it, dashed radii from M and the label 3 on MC")

# ============================================================ kure-merkez-yaricap
M5, R5 = (3.0, -2.0, 4.0), 6.0
assert (-6) ** 2 / 4 + 4 ** 2 / 4 + (-8) ** 2 / 4 + 7 == 36
f = Fig(30, 18, [(10, 0, 0), (-4, 0, 0), (0, 5, 0), (0, -9, 0), (0, 0, 11), (0, 0, -3)], width=600)
f.axes(((-4, 10), (-9, 5), (-3, 11)), neg="solid", width=1.4)
f.ticks("x", (-3, 3, 6, 9))
f.ticks("y", (-9, -6, -3, 3))
f.ticks("z", (-3, 3, 6, 9))
f.sphere(M5, R5, PRACTICE, fill=0.11)
rc = math.sqrt(R5 ** 2 - M5[2] ** 2)
assert abs(rc - math.sqrt(20)) < 1e-12
f.styled(disc((3, -2, 0), rc, 160), lambda Q: vdot(vsub(Q, M5), f.d) >= 0,
         dict(color=TEXT, width=1.5, opacity=0.9), dict(color=TEXT, width=1.1, dash="4 3", opacity=0.55))
foot = (3.0, -2.0, 0.0)
f.guide([M5, foot], TEXT, 0.7, 1.1)
f.guide([foot, (3, 0, 0)], TEXT, 0.6, 1.0)
f.guide([foot, (0, -2, 0)], TEXT, 0.6, 1.0)
top = (3.0, -2.0, 10.0)
f.line([M5, top], PRACTICE, 2.8)
f.point(M5, TEXT, 4.6)
f.point(top, PRACTICE, 3.8)
f.hollow(foot, TEXT, 3.6)
f.place(O3, it("O"), NAME, prefs=[250, 235, 265, 215])
f.place(M5, it("M") + triple(3, -2, 4), NAME, prefs=["r", "dr", "ur"], d=8)
f.place(top, triple(3, -2, 10), NAME, PRACTICE, prefs=["ur", "r", "ul"])
f.place(vscale(0.5, vadd(M5, top)), it("r") + " = 6", NAME, PRACTICE, prefs=["l", "ul", "dl"], d=7)
f.render(
    "kure-merkez-yaricap",
    "Merkezi <em>M</em>(3, −2, 4) ve yarıçapı 6 olan küre. Kürenin en üst noktası (3, −2, 10)&#8217;dur; "
    "küre <em>z</em> = −2&#8217;ye kadar indiğinden <em>XY</em>-düzlemini, merkezi (3, −2, 0) ve "
    "yarıçapı √20 olan çember boyunca keser (siyah çember).",
    "Sphere with center M(3, -2, 4) and radius 6, the vertical radius to the top point "
    "(3, -2, 10), the foot (3, -2, 0) of the center on the XY plane and the circle of radius "
    "root 20 where the sphere cuts the XY plane")

# ============================================================ iki-kat-uzaklik
M6 = (-2.0, 11 / 3, -4.0)
R6 = 2 * math.sqrt(70) / 3
P1a, P2a = (2.0, -3.0, 4.0), (-1.0, 2.0, -2.0)
K6, L6 = (0.0, 1 / 3, 0.0), (-4.0, 7.0, -8.0)
Mf = (Fraction(-2), Fraction(11, 3), Fraction(-4))
for Q in ((0, Fraction(1, 3), 0), (-4, 7, -8)):
    assert dist2(Q, Mf) == Fraction(280, 9)
    assert dist2(Q, P1a) == 4 * dist2(Q, P2a)
f = Fig(35, 16, [(4, 0, 0), (-8, 0, 0), (0, 10, 0), (0, -4, 0), (0, 0, 5), (0, 0, -10)], width=610)
f.axes(((-8, 4), (-4, 10), (-10, 5)), neg="solid", width=1.3, opacity=0.7)
f.ticks("x", (-8, -6, -4, -2, 2))
f.ticks("y", (-2, 2, 4, 6, 8))
f.ticks("z", (-10, -8, -6, -4, -2, 2, 4))
f.sphere(M6, R6, THEORY, fill=0.11)
# a point P on the upper front of the sphere: then |PP1| = 2|PP2| holds automatically
e6 = vunit(vadd(vadd(vscale(0.62, f.cam.r), vscale(0.62, f.cam.u)), vscale(0.45, f.d)))
P6 = vadd(M6, vscale(R6, e6))
assert abs(vnorm(vsub(P6, P1a)) - 2 * vnorm(vsub(P6, P2a))) < 1e-9
f.guide([P1a, L6], TEXT, 0.65, 1.3, "6 4")
f.line([P6, P1a], PRACTICE, 1.6, None, 0.9)
f.line([P6, P2a], PRACTICE, 1.6, None, 0.9)
f.point(M6, TEXT, 4.6)
f.point(P1a, PRACTICE, 4.8)
f.point(P2a, BASE, 4.8)
f.point(K6, THEORY, 4.6)
f.point(L6, THEORY, 4.6)
f.point(P6, TEXT, 4.4)
f.place(O3, it("O"), NAME, prefs=[250, 235, 265, 215, 300])
f.place(P1a, pt_name("P", "1") + triple(2, -3, 4), NAME, PRACTICE, prefs=["ul", "l", "u"], leader=True)
f.place(P2a, pt_name("P", "2") + triple(-1, 2, -2), NAME, BASE, prefs=["dl", "l", "d"], leader=True)
f.place(M6, it("M") + "(−2, 11/3, −4)", NAME, prefs=["dr", "r", "d"], leader=True)
f.place(K6, it("K") + "(0, 1/3, 0)", NAME, THEORY, prefs=[12, 22, 2, 32], leader=True,
        far=(0, 7, 15, 26, 40, 56))
f.place(L6, it("L") + triple(-4, 7, -8), NAME, THEORY, prefs=["r", "dr", "ur"], leader=True)
f.place(P6, it("P"), NAME + 0.5, prefs=["ur", "u", "r"])
f.place(vscale(0.5, vadd(P6, P1a)), "|" + it("PP") + sub("1") + "|", DESC + 0.5, PRACTICE, prefs=["u", "ur", "ul"], d=5)
f.place(vscale(0.5, vadd(P6, P2a)), "|" + it("PP") + sub("2") + "|", DESC + 0.5, PRACTICE, prefs=["dr", "d", "r"], d=5)
f.render(
    "iki-kat-uzaklik",
    "<em>P</em><sub>1</sub>&#8217;e uzaklığı <em>P</em><sub>2</sub>&#8217;ye uzaklığının 2 katı olan "
    "noktalar, merkezi <em>M</em>(−2, 11/3, −4) ve yarıçapı 2√70/3 ≈ 5,58 olan küreyi oluşturur. "
    "<em>P</em><sub>1</sub><em>P</em><sub>2</sub> doğrusu <em>M</em>&#8217;den geçer ve küreyi "
    "<em>K</em> ile <em>L</em> noktalarında keser; küre üzerindeki her <em>P</em> için "
    "|<em>PP</em><sub>1</sub>| = 2|<em>PP</em><sub>2</sub>|.",
    "Sphere with center M(-2, 11/3, -4) and radius 2 root 70 over 3; P1(2, -3, 4) outside, "
    "P2(-1, 2, -2) inside, the dashed line through P1, P2 and M meeting the sphere at K(0, 1/3, 0) "
    "and L(-4, 7, -8), and a point P on the sphere joined to P1 and P2")

# ============================================================ eskenar-ucgen
Ae, Be, Ce = (4.0, 2.0, 4.0), (10.0, 2.0, -2.0), (2.0, 0.0, -4.0)
assert dist2(Ae, Be) == dist2(Be, Ce) == dist2(Ce, Ae) == 72
f = Fig(-62, 16, [(11, 0, 0), (0, 4, 0), (0, 0, 5), (0, 0, -5), O3], width=600)
f.axes(((0, 11), (0, 4), (-5, 5)), neg="solid", width=1.4)
f.ticks("x", (2, 4, 6, 8, 10))
f.ticks("z", (-4, -2, 2, 4))
for Q in (Ae, Be):
    f.guide([Q, (Q[0], 0, Q[2])], TEXT, 0.6, 1.1)
    f.hollow((Q[0], 0, Q[2]), TEXT, 3.2)
f.polygon([Ae, Be, Ce], THEORY, 0.18)
f.line([Ae, Be, Ce, Ae], THEORY, 2.4)
for U, V in ((Ae, Be), (Be, Ce), (Ce, Ae)):
    mU, mV = f.px(U), f.px(V)
    mx, my = (mU[0] + mV[0]) / 2, (mU[1] + mV[1]) / 2
    L = math.hypot(mV[0] - mU[0], mV[1] - mU[1])
    nx, ny = -(mV[1] - mU[1]) / L, (mV[0] - mU[0]) / L
    f.p.add(f'<line x1="{mx - nx * 6:.1f}" y1="{my - ny * 6:.1f}" x2="{mx + nx * 6:.1f}" '
            f'y2="{my + ny * 6:.1f}" stroke="{THEORY}" stroke-width="2"/>')
for Q in (Ae, Be, Ce):
    f.point(Q, TEXT, 4.4)
f.place(O3, it("O"), NAME, prefs=[250, 235, 265, 215, 300])
f.place(Ae, it("A") + triple(4, 2, 4), NAME, prefs=["ul", "u", "l"])
f.place(Be, it("B") + triple(10, 2, -2), NAME, prefs=["r", "ur", "dr"])
f.place(Ce, it("C") + triple(2, 0, -4), NAME, prefs=["dl", "l", "d"])
G = vscale(1 / 3, vadd(vadd(Ae, Be), Ce))
for U, V in ((Ae, Be), (Be, Ce), (Ce, Ae)):
    m = vscale(0.5, vadd(U, V))
    gx, gy = f.px(G)
    mx, my = f.px(m)
    ang = math.degrees(math.atan2(-(my - gy), mx - gx))
    f.place(m, "6" + SQRT + "2", NAME, THEORY, prefs=[ang, ang + 20, ang - 20], d=9)
f.render(
    "eskenar-ucgen",
    "<em>A</em>(4, 2, 4), <em>B</em>(10, 2, −2), <em>C</em>(2, 0, −4) üçgeninin üç kenarı da "
    "6√2 uzunluğundadır; kenarlardaki çentikler bu eşitliği gösterir. Kesikli çizgiler "
    "<em>A</em> ve <em>B</em>&#8217;den <em>XZ</em>-düzlemine inen dikmelerdir (<em>C</em> bu düzlemdedir).",
    "Equilateral triangle A(4, 2, 4), B(10, 2, -2), C(2, 0, -4) seen nearly face on, each side "
    "labelled 6 root 2 with an equality tick, dashed drops from A and B to the XZ plane")

# ============================================================ dikdortgen
Ar, Br, Cr, Dr = (2.0, -1.0, 0.0), (0.0, -1.0, -1.0), (1.0, 1.0, -3.0), (3.0, 1.0, -2.0)
Nr = (1.5, 0.0, -1.5)
assert dist2(Ar, Br) == 5 and dist2(Br, Cr) == 9 and dist2(Cr, Dr) == 5 and dist2(Dr, Ar) == 9
assert dist2(Ar, Cr) == dist2(Br, Dr) == 14
assert all(dist2(Nr, Q) == Fraction(7, 2) for Q in (Ar, Br, Cr, Dr))
f = Fig(68, 27, [(4, 0, 0), (-1, 0, 0), (0, 2, 0), (0, -2, 0), (0, 0, 1), (0, 0, -4)], width=560)
f.axes(((-1, 4), (-2, 2), (-4, 1)), neg="solid", width=1.4)
f.ticks("x", (-1, 1, 2, 3))
f.ticks("y", (-2, -1, 1))
f.ticks("z", (-4, -3, -2, -1))
for Q in (Br, Cr, Dr):
    f.guide([Q, (Q[0], Q[1], 0)], TEXT, 0.45, 1.0)
    f.hollow((Q[0], Q[1], 0), TEXT, 3.0)
f.polygon([Ar, Br, Cr, Dr], BASE, 0.2)
f.guide([Ar, Cr], BASE, 0.8, 1.2, "5 4")
f.guide([Br, Dr], BASE, 0.8, 1.2, "5 4")
f.line([Ar, Br, Cr, Dr, Ar], BASE, 2.4)
for Q, U, V in ((Ar, Dr, Br), (Br, Ar, Cr), (Cr, Br, Dr), (Dr, Cr, Ar)):
    f.right_angle(Q, vsub(U, Q), vsub(V, Q), 10)
for Q in (Ar, Br, Cr, Dr):
    f.point(Q, TEXT, 4.4)
f.point(Nr, BASE, 3.6)
f.place(O3, it("O"), NAME, prefs=[250, 235, 265, 215, 300])
f.place(Ar, it("A") + triple(2, -1, 0), NAME, prefs=["ul", "u", "l"])
f.place(Br, it("B") + triple(0, -1, -1), NAME, prefs=["r", "ur", "dr"])
f.place(Cr, it("C") + triple(1, 1, -3), NAME, prefs=["dr", "r", "d"])
f.place(Dr, it("D") + triple(3, 1, -2), NAME, prefs=["l", "dl", "ul"])
f.place(Nr, it("N"), NAME, BASE, prefs=[90, 270, 0, 180], d=6)
Gr = Nr
for U, V, s in ((Ar, Br, SQRT + "5"), (Cr, Dr, SQRT + "5"), (Br, Cr, "3"), (Dr, Ar, "3")):
    m = vscale(0.5, vadd(U, V))
    gx, gy = f.px(Gr)
    mx, my = f.px(m)
    ang = math.degrees(math.atan2(-(my - gy), mx - gx))
    f.place(m, s, NAME, BASE, prefs=[ang, ang + 20, ang - 20], d=7)
f.render(
    "dikdortgen",
    "<em>A</em>(2, −1, 0), <em>B</em>(0, −1, −1), <em>C</em>(1, 1, −3), <em>D</em>(3, 1, −2) "
    "dikdörtgeni: karşılıklı kenarlar √5 ve 3, köşegenler √14 uzunluğundadır ve ortak orta "
    "noktaları <em>N</em>(3/2, 0, −3/2)&#8217;dir. Kesikli dikey çizgiler köşelerden "
    "<em>XY</em>-düzlemine iner.",
    "Rectangle A(2, -1, 0), B(0, -1, -1), C(1, 1, -3), D(3, 1, -2) shaded green with side "
    "lengths root 5 and 3, right angle marks, dashed diagonals meeting at N and drops to the XY plane")

# ============================================================ ayni-vektor
Av, Bv, Cv, Dv = (1.0, -2.0, 3.0), (1.0, 7.0, 4.0), (-2.0, 3.0, 0.0), (-2.0, 12.0, 1.0)
assert vsub(Bv, Av) == vsub(Dv, Cv) == (0.0, 9.0, 1.0)
f = Fig(32, 16, [(2, 0, 0), (-3, 0, 0), (0, 13, 0), (0, -3, 0), (0, 0, 5), O3], width=640)
f.axes(((-3, 2), (-3, 13), (0, 5)), neg="solid", width=1.4)
f.ticks("x", (-2, -1, 1))
f.ticks("y", (-2, 2, 4, 6, 8, 10, 12))
f.ticks("z", (1, 2, 3, 4))
for Q in (Av, Bv, Dv):
    f.guide([Q, (Q[0], Q[1], 0)], TEXT, 0.45, 1.0)
    f.hollow((Q[0], Q[1], 0), TEXT, 3.0)
f.polygon([Av, Bv, Dv, Cv], TEXT, 0.07)
f.guide([Av, Cv], TEXT, 0.7, 1.2, "5 4")
f.guide([Bv, Dv], TEXT, 0.7, 1.2, "5 4")
f.arrow(Av, Bv, THEORY, 3.0, 13)
f.arrow(Cv, Dv, THEORY, 3.0, 13)
for Q in (Av, Bv, Cv, Dv):
    f.point(Q, TEXT, 4.2)
f.place(O3, it("O"), NAME, prefs=[250, 235, 265, 215, 300])
f.place(Av, it("A") + triple(1, -2, 3), NAME, prefs=["ul", "u", "l"])
f.place(Bv, it("B") + triple(1, 7, 4), NAME, prefs=["u", "ur", "ul"])
f.place(Cv, it("C") + triple(-2, 3, 0), NAME, prefs=["dl", "d", "l"])
f.place(Dv, it("D") + triple(-2, 12, 1), NAME, prefs=["r", "dr", "ur"])
f.place(vscale(0.5, vadd(Av, Bv)), it("AB"), NAME + 0.5, THEORY, prefs=["u", "ul", "ur"], d=5, vec=True)
f.place(vscale(0.5, vadd(Cv, Dv)), it("CD"), NAME + 0.5, THEORY, prefs=["d", "dr", "dl"], d=5, vec=True)
f.render(
    "ayni-vektor",
    "<em>A</em>&#8217;dan <em>B</em>&#8217;ye ve <em>C</em>&#8217;den <em>D</em>&#8217;ye giden oklar "
    "aynı (0, 9, 1) koordinat değişimini taşır: paraleldir ve uzunlukları √82&#8217;dir. "
    "<em>ABDC</em> bir paralelkenardır.",
    "Arrows from A(1, -2, 3) to B(1, 7, 4) and from C(-2, 3, 0) to D(-2, 12, 1), parallel and of "
    "equal length, with the faint parallelogram ABDC and dashed drops to the XY plane")


# ---------------------------------------------------------------------------
for name, content in OUT.items():
    path = OUT_DIR / f"analytic-udk-{name}.md"
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(content)
    print("wrote", path.name)
