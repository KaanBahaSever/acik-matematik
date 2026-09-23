# -*- coding: utf-8 -*-
"""Figures for dersler/analitik-geometri/silindirik-ve-kuresel-koordinatlar.qmd (chapter key: skk).

Every drawing here is three-dimensional and goes through scripts/svg_plot3.py
(orthographic Camera on an equal-aspect svg_plot.Plot panel). The figures go
INSIDE the box they explain (example, solution, proof), never inside a
definition box.

Curved surfaces (cylinder, cone, sphere) are translucent. Where a line runs
behind such a surface it is drawn thin and dashed: `Fig.hidden` walks from
the point toward the viewer and looks for a sign change of the surface's
implicit equation inside the drawn patch.

Labels are placed after the projection, in page pixels: `Fig.place` tries a
ring of candidate positions around the anchor and keeps the one that touches
no drawn line, point or earlier label.

Usage:   python scripts/analytic_figures/skk.py
         python scripts/center_figures.py "analytic-skk-*.md" --keep-width
Output:  scripts/_figures/analytic-skk-<name>.md
"""
import html
import io
import math
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, WIDE, TEXT, BG, THEORY, PRACTICE, BASE, REMARK  # noqa: E402
from svg_plot3 import Camera, Space, vadd, vsub, vscale, vdot, vcross, vnorm, vunit  # noqa: E402

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
OUT = {}

MINUS, SQRT, PI = "−", "√", "π"
RHO, THETA, PHI = "ρ", "θ", "φ"
ALPHA, BETA, GAMMA = "α", "β", "γ"
NAME, DESC, ANG, AXIS = 14.5, 13.0, 16.0, 15.0      # font sizes (px)
O3 = (0.0, 0.0, 0.0)
EX, EY, EZ = (1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)

# Tall scenes stay in the standard column: at the wide width they would be too tall on screen.
TALL_SCENES = set()

# ---------------------------------------------------------------------------
# text helpers
# ---------------------------------------------------------------------------


def it(s):
    return f'<tspan font-style="italic">{s}</tspan>'


def sq(s):
    return f"{s}²"


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


def close(a, b, tol=1e-9):
    return all(abs(p - q) < tol for p, q in zip(a, b))


def lerp(A, B, t):
    return vadd(A, vscale(t, vsub(B, A)))


def seg_pts(A, B, n=160):
    return [lerp(A, B, k / n) for k in range(n + 1)]


def hcircle(r, z, t0=0.0, t1=2 * math.pi, n=240):
    """Points of the horizontal circle x^2 + y^2 = r^2 at height z, angle t0 -> t1."""
    return [(r * math.cos(t0 + (t1 - t0) * k / n), r * math.sin(t0 + (t1 - t0) * k / n), z)
            for k in range(n + 1)]


def gcircle(C, e1, e2, r, t0=0.0, t1=2 * math.pi, n=240):
    return [vadd(C, vadd(vscale(r * math.cos(t0 + (t1 - t0) * k / n), e1),
                         vscale(r * math.sin(t0 + (t1 - t0) * k / n), e2))) for k in range(n + 1)]


def hull(pts):
    """Convex hull (monotone chain) of page points."""
    P = sorted(set((round(x, 3), round(y, 3)) for x, y in pts))
    if len(P) < 3:
        return P

    def cr(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, up = [], []
    for p in P:
        while len(lo) >= 2 and cr(lo[-2], lo[-1], p) <= 0:
            lo.pop()
        lo.append(p)
    for p in reversed(P):
        while len(up) >= 2 and cr(up[-2], up[-1], p) <= 0:
            up.pop()
        up.append(p)
    return lo[:-1] + up[:-1]


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
        self.sid = 0
        self.surfaces = []    # (F, inpatch): implicit equation and patch test, for hidden()

    # -- projection ---------------------------------------------------------
    def px(self, P):
        X, Y = self.S.pt(P)
        return (self.p.X(X), self.p.Y(Y))

    def u(self, pixels):
        """Pixels -> space units."""
        return pixels / self.ppu

    def sang(self, vec):
        """Page angle (degrees, 0 = right, 90 = up) of the space direction vec."""
        a = self.px(O3)
        b = self.px(vec)
        return math.degrees(math.atan2(-(b[1] - a[1]), b[0] - a[0]))

    def _reg(self, Ps, w=1.0):
        self._reg_px([self.px(P) for P in Ps], w)

    def _reg_px(self, q, w=1.0):
        self.sid += 1
        for a, b in zip(q, q[1:]):
            self.segs.append((a, b, w, self.sid))

    # -- occlusion by translucent curved surfaces -----------------------------
    def hidden(self, Q, T=12.0, n=480, eps=0.04):
        for F, inpatch in self.surfaces:
            prev = None
            for k in range(n + 1):
                t = eps + (T - eps) * k / n
                R = vadd(Q, vscale(t, self.d))
                v = F(R)
                if prev is not None and (v > 0) != (prev[1] > 0):
                    M = vadd(Q, vscale(0.5 * (t + prev[0]), self.d))
                    if inpatch(M):
                        return True
                prev = (t, v)
        return False

    # -- drawing ------------------------------------------------------------
    def line(self, Ps, color=TEXT, width=1.6, dash=None, opacity=1.0, w=1.0):
        self.S.line(Ps, color, width, dash, opacity)
        if w:
            self._reg(Ps, w)

    def guide(self, Ps, color=TEXT, opacity=0.75, width=1.3, dash="5 4", w=0.7):
        self.line(Ps, color, width, dash, opacity, w)

    def arrow(self, P0, P1, color=THEORY, width=2.2, head=10.0, dash=None, opacity=1.0, w=1.0):
        self.S.arrow(P0, P1, color, width, head, dash, opacity)
        self._reg([P0, P1], w)

    def fill(self, Ps, color, opacity):
        self.S.polygon(Ps, color, opacity)

    def fill_px(self, q, color, opacity):
        pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in q)
        self.p.add(f'<polygon points="{pts}" fill="{color}" fill-opacity="{opacity}" stroke="none"/>')

    def fill_hull(self, Ps, color, opacity):
        self.fill_px(hull([self.px(P) for P in Ps]), color, opacity)

    def point(self, P, color=TEXT, r=4.2):
        self.S.point(P, color, r)
        x, y = self.px(P)
        self.dots.append((x, y, r))

    def hollow(self, P, color=TEXT, r=3.6):
        self.S.hollow(P, color, r)
        x, y = self.px(P)
        self.dots.append((x, y, r))

    def split(self, Ps, flag):
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
        for state, run in self.split(Ps, flag):
            st = on if state else off
            if st is not None and len(run) > 1:
                self.line(run, **st)

    def vis_line(self, Ps, color=TEXT, width=1.6, opacity=1.0, w=1.0, dash=None):
        """Polyline: as given where visible, thin and dashed where a surface hides it."""
        self.styled(Ps, lambda P: not self.hidden(P),
                    dict(color=color, width=width, opacity=opacity, w=w, dash=dash),
                    dict(color=color, width=max(1.0, 0.6 * width), dash="4 3",
                         opacity=0.55 * opacity, w=0.4 * w))

    def right_angle(self, Q, a, b, size=13, color=TEXT, width=1.3, opacity=0.9):
        s = self.u(size)
        a, b = vunit(a), vunit(b)
        pts = [vadd(Q, vscale(s, a)), vadd(Q, vadd(vscale(s, a), vscale(s, b))), vadd(Q, vscale(s, b))]
        self.line(pts, color, width, None, opacity, w=0.5)

    def arc(self, Q, a, b, r, color=TEXT, width=2.0, opacity=1.0, head=9.0, n=60):
        """Arc of radius r (space units) at Q from direction a to direction b (the smaller
        angle), with an arrowhead at b; returns the page point where its label goes."""
        e1 = vunit(a)
        bb = vunit(b)
        e2 = vunit(vsub(bb, vscale(vdot(bb, e1), e1)))
        th = math.acos(max(-1.0, min(1.0, vdot(e1, bb))))
        pts = [vadd(Q, vadd(vscale(r * math.cos(th * k / n), e1), vscale(r * math.sin(th * k / n), e2)))
               for k in range(n + 1)]
        if head:
            # stop the shaft where the head begins
            L = 0.0
            j = n
            while j > 0 and L < self.u(head * 0.8):
                L += vnorm(vsub(pts[j], pts[j - 1]))
                j -= 1
            self.line(pts[:j + 1], color, width, None, opacity, 0.8)
            self.S.arrow(pts[max(0, j - 2)], pts[-1], color, width, head, None, opacity)
            self._reg(pts[j:], 0.8)
        else:
            self.line(pts, color, width, None, opacity, 0.8)
        return pts

    # -- axes -------------------------------------------------------------
    def axes(self, rng, labels=("X", "Y", "Z"), width=1.4, opacity=0.85, colors=None, head=10.0,
             neg_opacity=0.5, hidden=True):
        """Axes over (lo, hi) ranges; negative parts fainter; stretches behind a surface dashed."""
        E = (EX, EY, EZ)
        for k, (lo, hi) in enumerate(rng):
            e = E[k]
            col = colors[k] if colors else TEXT
            flag = (lambda P: not self.hidden(P)) if (hidden and self.surfaces) else (lambda P: True)
            hid = dict(color=col, width=1.0, dash="4 3", opacity=0.45, w=0.4)
            if lo < 0:
                pts = [vscale(lo * (1 - j / 120), e) for j in range(121)]
                self.styled(pts, flag, dict(color=col, width=width * 0.85, opacity=neg_opacity, w=0.8), hid)
            n = 240
            tip = vscale(hi, e)
            pts = [vscale(hi * j / n, e) for j in range(n + 1)]
            cut = int(n * max(0.0, 1 - self.u(head * 1.3) / hi))
            self.styled(pts[:cut + 1], flag, dict(color=col, width=width, opacity=opacity, w=1.0), hid)
            self.arrow(pts[cut], tip, col, width, head, None, opacity, w=1.0)
            if labels and labels[k]:
                self.axis_label(e, tip, labels[k], col)

    def axis_label(self, e, tip, s, color=TEXT, size=AXIS, gap=7):
        x0, y0 = self.px(O3)
        x1, y1 = self.px(tip)
        L = math.hypot(x1 - x0, y1 - y0) or 1.0
        ax, ay = (x1 - x0) / L, (y1 - y0) / L
        w, h = text_width(s, size), size
        ext = min(w / 2 / abs(ax) if ax else 1e9, h / 2 / abs(ay) if ay else 1e9)
        cx, cy = x1 + ax * (gap + ext), y1 + ay * (gap + ext)
        self._text(cx, cy, it(s), size, color, w, h)

    def tick(self, P, along, length=7.0, color=TEXT):
        """Short tick across the axis direction `along` at P."""
        x, y = self.px(P)
        a = self.px(O3)
        b = self.px(along)
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        nx, ny = -(b[1] - a[1]) / L, (b[0] - a[0]) / L
        p0 = (x - nx * length / 2, y - ny * length / 2)
        p1 = (x + nx * length / 2, y + ny * length / 2)
        self.p.add(f'<line x1="{p0[0]:.1f}" y1="{p0[1]:.1f}" x2="{p1[0]:.1f}" y2="{p1[1]:.1f}" '
                   f'stroke="{color}" stroke-width="1.3" opacity="0.85"/>')
        self._reg_px([p0, p1], 0.5)

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
              opacity=1.0, only=False, far=(0, 7, 15, 26, 40)):
        """Put text s next to anchor (a space point, or ('px', x, y)); the cheapest ring
        candidate wins, earlier prefs winning ties. 'c' means centred on the anchor."""
        if isinstance(anchor, tuple) and anchor and anchor[0] == "px":
            x, y = anchor[1], anchor[2]
        else:
            x, y = self.px(anchor)
        w, h = text_width(s, size), size
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

    def side_label(self, A, B, s, size=NAME, color=TEXT, side=+1, t=0.5, d=6, extra=()):
        """Label beside segment AB at parameter t, pushed perpendicular (side +1 = left of A->B on the page)."""
        a = self.sang(vsub(B, A)) if vnorm(vsub(B, A)) > 0 else 0
        prefs = [a + 90 * side, a + 90 * side + 20, a + 90 * side - 20, *extra]
        return self.place(lerp(A, B, t), s, size, color, prefs=prefs, d=d)

    def angle_label(self, pts, s, size=ANG, color=TEXT, d=6):
        """Label just outside the middle of an arc (away from its centre)."""
        mid = pts[len(pts) // 2]
        C = self.px(pts[0])
        E = self.px(pts[-1])
        M = self.px(mid)
        # the centre on the page: the arc's end chords meet there; use the outward page direction
        cx, cy = (C[0] + E[0]) / 2, (C[1] + E[1]) / 2
        ang = math.degrees(math.atan2(-(M[1] - cy), M[0] - cx))
        return self.place(mid, s, size, color, prefs=[ang, ang + 20, ang - 20, ang + 40, ang - 40], d=d)

    # -- output -------------------------------------------------------------
    def render(self, name, caption, aria):
        print(f"-- {name} (warnings above belong to it)")
        for t in self.texts:
            self.p.add(t)
        css = "ders-grafik" if name in TALL_SCENES else WIDE
        OUT[name] = figure(round(self.W), round(self.H), [self.p], caption, css, aria)


def cyl_surface(R, z0, z1, t0=None, t1=None):
    def F(P):
        return P[0] ** 2 + P[1] ** 2 - R * R

    def ok(P):
        if not (z0 - 1e-9 <= P[2] <= z1 + 1e-9):
            return False
        if t0 is None:
            return True
        t = math.atan2(P[1], P[0]) % (2 * math.pi)
        return t0 - 1e-9 <= t <= t1 + 1e-9
    return F, ok


def cone_surface(sgn, zmax):
    """z = sgn * sqrt(x^2 + y^2), 0 <= sgn * z <= zmax."""
    def F(P):
        return sgn * P[2] - math.hypot(P[0], P[1])

    def ok(P):
        return -1e-9 <= sgn * P[2] <= zmax + 1e-9
    return F, ok


def sphere_surface(C, R):
    def F(P):
        return vnorm(vsub(P, C)) - R
    return F, (lambda P: True)


# ===========================================================================
# 1. skk-silindirik-kurulum: r = 3, theta = pi/3, z = 2.5
# ===========================================================================
r1, t1, z1 = 3.0, math.pi / 3, 2.5
P1f = (r1 * math.cos(t1), r1 * math.sin(t1), 0.0)
P1 = (P1f[0], P1f[1], z1)
assert close(P1f, (1.5, 3 * math.sqrt(3) / 2, 0.0))
f = Fig(30, 24, [O3, (3.6, 0, 0), (0, 3.6, 0), (0, 0, 3.4), (3, 0, 2.5), (0, 3, 2.5)], width=580)
bot, top = hcircle(r1, 0.0, 0, math.pi / 2, 90), hcircle(r1, z1, 0, math.pi / 2, 90)
f.fill(bot + list(reversed(top)), BASE, 0.09)
f.axes(((0, 3.6), (0, 3.6), (0, 3.4)))
for arc_ in (bot, top):
    f.line(arc_, BASE, 1.4, None, 0.7, 0.6)
for P in ((3, 0, 0), (0, 3, 0)):
    f.line([P, vadd(P, (0, 0, z1))], BASE, 1.2, None, 0.6, 0.6)
Xf, Yf = (P1f[0], 0, 0), (0, P1f[1], 0)
f.guide([P1f, Xf])
f.guide([P1f, Yf])
f.guide([O3, P1], TEXT, 0.45, 1.1, None, 0.5)
f.line([P1f, P1], THEORY, 2.6, "7 4", 1.0)
f.line([O3, P1f], PRACTICE, 3.0)
f.right_angle(P1f, vsub(O3, P1f), EZ, 17, TEXT, 1.5)
th_pts = f.arc(O3, EX, P1f, 0.95, REMARK, 2.2)
for P in (Xf, Yf):
    f.hollow(P, TEXT, 3.4)
f.point(O3, TEXT, 3.6)
f.point(P1f, TEXT, 4.4)
f.point(P1, THEORY, 4.8)
f.place(O3, it("O"), NAME, prefs=["l", "dl", "d"])
f.place(P1f, it("P") + "′", NAME, prefs=["dr", "r", "d"])
f.place(P1, it("P") + "(" + it("r") + ", " + it(THETA) + ", " + it("z") + ")", NAME, THEORY,
        prefs=["ur", "u", "r", "ul"])
f.side_label(O3, P1f, it("r"), NAME + 2, PRACTICE, side=+1, d=6)
f.side_label(P1f, P1, it("z"), NAME + 2, THEORY, side=-1, d=7)
f.place(Xf, it("x"), NAME + 1, prefs=["dl", "d", "l"])
f.place(Yf, it("y"), NAME + 1, prefs=["d", "dr", "dl"])
f.angle_label(th_pts, it(THETA), ANG, REMARK)
f.render(
    "silindirik-kurulum",
    "Silindirik koordinatlar: <em>P</em>&#8242;, <em>P</em>&#8217;nin <em>XY</em>-düzlemindeki "
    "izdüşümüdür; (<em>r</em>, <em>&#952;</em>) onun kutupsal koordinatları, <em>z</em> de "
    "<em>P</em>&#8217;nin kotudur. Soluk yüzey, <em>P</em>&#8217;nin üzerinde bulunduğu "
    "<em>r</em> = 3 silindirinin bir parçasıdır (şekilde <em>&#952;</em> = &#960;/3, "
    "<em>z</em> = 2,5).",
    "Point P with its foot P' in the XY plane, the segment OP' of length r, the angle theta from "
    "the positive X axis to OP', the vertical segment P'P of length z, dashed guides from P' to "
    "the X and Y axes, and a faint quarter of the cylinder r = 3 through P")


# ===========================================================================
# 2. skk-silindir-r-a: the cylinder x^2 + y^2 = 4
# ===========================================================================
a2, h0, h1 = 2.0, -2.0, 2.5
f = Fig(35, 20, [(4.2, 0, 0), (-3.2, 0, 0), (0, 3.2, 0), (0, -3.2, 0), (0, 0, 3.2), (0, 0, -2.6)],
        width=560)
f.surfaces.append(cyl_surface(a2, h0, h1))
dxy = (f.d[0], f.d[1])
phs = [math.atan2(-dxy[0], dxy[1]), math.atan2(dxy[0], -dxy[1])]       # silhouette angles


def cyl2(ph, z):
    return (a2 * math.cos(ph), a2 * math.sin(ph), z)


fr = [phs[0] + math.pi * k / 120 for k in range(121)]
if vdot(cyl2(fr[60], 0), (dxy[0], dxy[1], 0)) < 0:
    fr = [phs[0] - math.pi * k / 120 for k in range(121)]
side = [cyl2(t, h1) for t in fr] + [cyl2(t, h0) for t in reversed(fr)]
f.fill(hcircle(a2, h1, n=120), BASE, 0.07)
f.fill(side, BASE, 0.12)
f.axes(((-3.2, 4.2), (-3.2, 3.2), (-2.6, 3.2)))
f.line(hcircle(a2, h1), BASE, 1.8, None, 0.95)
f.vis_line(hcircle(a2, h0), BASE, 1.8, 0.95)
for ph in phs:
    f.line([cyl2(ph, h0), cyl2(ph, h1)], BASE, 1.8, None, 0.95)
f.vis_line(hcircle(a2, 0.0), PRACTICE, 2.8, 1.0)
Ra = (math.sqrt(3), -1.0, 0.0)
assert abs(vnorm(Ra) - a2) < 1e-12
f.arrow(O3, Ra, THEORY, 2.4, 11.0)
f.point(O3, TEXT, 3.6)
f.place(O3, it("O"), NAME, prefs=["ul", "u", "l"])
f.side_label(O3, Ra, it("a"), NAME + 2, THEORY, side=+1, d=6)
pr = sorted(phs, key=lambda ph: f.px(cyl2(ph, 0))[0])
f.place(cyl2(pr[1], 0.0), it("x") + "² + " + it("y") + "² = " + it("a") + "²", NAME, PRACTICE,
        prefs=["dr", "r", "d"], d=10)
f.place(cyl2(pr[1], h1), it("r") + " = " + it("a"), NAME + 1, BASE, prefs=["r", "ur", "dr"], d=10)
f.render(
    "silindir-r-a",
    "<em>r</em> = <em>a</em> denkleminin grafiği: ekseni <em>Z</em>-ekseni, yarıçapı <em>a</em> olan "
    "dik dairesel silindir (şekilde <em>a</em> = 2 ve &#8722;2 &#8804; <em>z</em> &#8804; 2,5 parçası). "
    "Kalın çember <em>XY</em>-düzlemindeki <em>x</em>² + <em>y</em>² = <em>a</em>² çemberidir; "
    "silindirin arkasında kalan çizgiler kesiklidir.",
    "Translucent circular cylinder of radius a = 2 around the Z axis, its top and bottom rims, "
    "the bold circle x^2 + y^2 = a^2 in the XY plane and a radius a from O; lines behind the "
    "surface are dashed")


# ===========================================================================
# 3. skk-yarim-duzlem: theta = pi/4
# ===========================================================================
c45 = 3 / math.sqrt(2)
assert abs(c45 - 2.1213) < 1e-3
HP = [(0, 0, -2.0), (c45, c45, -2.0), (c45, c45, 2.0), (0, 0, 2.0)]
f = Fig(20, 22, [(3.2, 0, 0), (-2.5, 0, 0), (0, 3.2, 0), (0, -2.5, 0), (0, 0, 2.8), (0, 0, -2.5)] + HP,
        width=560)
n_hp = vunit((1, -1, 0))


def behind_hp(P):
    """Behind the half-plane patch on the page (the patch is opaque enough to dash what it hides)."""
    s = vdot(P, n_hp)
    front_side = vdot(n_hp, f.d) > 0
    if (s > 1e-9) == front_side or abs(s) < 1e-9:
        return False
    # project along d onto the plane x = y
    t = -s / vdot(n_hp, f.d)
    Q = vadd(P, vscale(t, f.d))
    r = (Q[0] + Q[1]) / math.sqrt(2)
    return 0 <= r <= 3.0 and -2.0 <= Q[2] <= 2.0


f.surfaces.append((lambda P: vdot(P, n_hp),
                   lambda P: 0 <= (P[0] + P[1]) / math.sqrt(2) <= 3.0 and -2.0 <= P[2] <= 2.0))
f.fill(HP, PRACTICE, 0.16)
f.axes(((-2.5, 3.2), (-2.5, 3.2), (-2.5, 2.8)))
f.vis_line([HP[1], HP[2], HP[3]], PRACTICE, 1.2, 0.7, 0.6)
f.vis_line([HP[0], HP[1]], PRACTICE, 1.2, 0.7, 0.6)
f.line([(0, 0, -2.0), (0, 0, 2.0)], PRACTICE, 3.2)
f.guide([O3, (-1.8, -1.8, 0)], PRACTICE, 0.6, 1.5, "6 4", 0.5)
f.line([O3, (c45, c45, 0)], PRACTICE, 3.0)
ang_pts = f.arc(O3, EX, (1, 1, 0), 1.0, REMARK, 2.2)
f.point(O3, TEXT, 3.6)
f.place(O3, it("O"), NAME, prefs=["dl", "l", "d"])
f.place(ang_pts[len(ang_pts) // 2], PI + "/4", ANG - 1, REMARK, prefs=[300, 285, 315, 270], d=7)
f.place((c45, c45, 0), it("y") + " = " + it("x") + ", " + it("x") + " ≥ 0", NAME, PRACTICE,
        prefs=["r", "dr", "ur"], d=10)
f.place((0, 0, -1.65), "sınır: " + it("Z") + "-ekseni", DESC, PRACTICE, prefs=["l", "ul", "dl"], d=10,
        only=True)
f.place(lerp(HP[2], HP[3], 0.35), it(THETA) + " = " + PI + "/4", NAME + 1, PRACTICE,
        prefs=["d", "dl", "dr"], d=12)
f.render(
    "yarim-duzlem",
    "<em>&#952;</em> = &#960;/4 denkleminin grafiği: <em>Z</em>-ekseniyle sınırlanan yarım düzlem "
    "(&#8722;2 &#8804; <em>z</em> &#8804; 2 parçası). <em>XY</em>-düzlemindeki izi "
    "<em>y</em> = <em>x</em>, <em>x</em> &#8805; 0 yarı doğrusudur; kesikli yarı doğru "
    "<em>y</em> = <em>x</em> doğrusunun öbür yarısıdır ve <em>&#952;</em> = 5&#960;/4 yarım "
    "düzlemine aittir.",
    "Half-plane theta = pi/4 bounded by the Z axis, its trace y = x, x at least 0 in the XY plane, "
    "the other half of the line y = x dashed, and the angle pi/4 from the X axis")


# ===========================================================================
# 4. skk-silindirik-yuzeyler: r = 2, theta = pi/4, z = 1 meet at P(2, pi/4, 1)
# ===========================================================================
Pq = (math.sqrt(2), math.sqrt(2), 1.0)
assert abs(math.hypot(Pq[0], Pq[1]) - 2) < 1e-12
f = Fig(18, 26, [(3.2, 0, 0), (0, 3.2, 0), (0, 0, 2.6), O3, (2.6, 2.6, 1)], width=560)
Zp = [(0, 0, 1), (2.6, 0, 1), (2.6, 2.6, 1), (0, 2.6, 1)]
Hq = [O3, (c45, c45, 0), (c45, c45, 2), (0, 0, 2)]
cb, ct = hcircle(2, 0, 0, math.pi / 2, 90), hcircle(2, 2, 0, math.pi / 2, 90)
f.axes(((0, 3.2), (0, 3.2), (0, 2.6)), hidden=False)
f.fill(Zp, THEORY, 0.10)
f.fill(Hq, PRACTICE, 0.13)
f.fill(cb + list(reversed(ct)), BASE, 0.13)
f.line(Zp + [Zp[0]], THEORY, 1.2, None, 0.65, 0.6)
f.line(Hq + [Hq[0]], PRACTICE, 1.2, None, 0.65, 0.6)
for c_ in (cb, ct):
    f.line(c_, BASE, 1.4, None, 0.75, 0.6)
for P in ((2, 0, 0), (0, 2, 0)):
    f.line([P, vadd(P, (0, 0, 2))], BASE, 1.2, None, 0.65, 0.6)
f.line(hcircle(2, 1, 0, math.pi / 2, 90), TEXT, 2.0, None, 0.9)
f.line([(math.sqrt(2), math.sqrt(2), 0), (math.sqrt(2), math.sqrt(2), 2)], TEXT, 2.0, None, 0.9)
f.line([(0, 0, 1), (c45, c45, 1)], TEXT, 2.0, None, 0.9)
f.point(Pq, TEXT, 5.0)
f.place(O3, it("O"), NAME, prefs=["dl", "l", "d"])
f.place(Pq, it("P") + "(2, " + PI + "/4, 1)", NAME, prefs=["ur", "ul", "r", "u"], d=8)
f.place(ct[70], it("r") + " = 2", NAME + 1, BASE, prefs=["u", "ur", "r"], d=8)
f.place((c45, c45, 2), it(THETA) + " = " + PI + "/4", NAME + 1, PRACTICE, prefs=["u", "ur", "ul"], d=8)
f.place((2.6, 2.6, 1), it("z") + " = 1", NAME + 1, THEORY, prefs=["r", "dr", "ur"], d=8)
f.render(
    "silindirik-yuzeyler",
    "Silindirik koordinat yüzeyleri: <em>r</em> = 2 silindiri, <em>&#952;</em> = &#960;/4 yarım "
    "düzlemi ve <em>z</em> = 1 düzlemi (birinci bölgedeki parçaları). Koyu çizgiler ikişer ikişer "
    "kesişimlerdir; üçü birden yalnız silindirik koordinatları (2, &#960;/4, 1) olan "
    "<em>P</em>(&#8730;2, &#8730;2, 1) noktasında buluşur.",
    "Quarter of the cylinder r = 2, the half-plane theta = pi/4 and the plane z = 1 in the first "
    "octant, their pairwise intersection curves, and their common point P(sqrt2, sqrt2, 1)")


# ===========================================================================
# 5. skk-kuresel-kurulum: rho = 3, theta = pi/3, phi = pi/4
# ===========================================================================
rho, th5, ph5 = 3.0, math.pi / 3, math.pi / 4
P5 = (rho * math.sin(ph5) * math.cos(th5), rho * math.sin(ph5) * math.sin(th5), rho * math.cos(ph5))
P5f, Q5 = (P5[0], P5[1], 0.0), (0.0, 0.0, P5[2])
assert close(P5, (1.0607, 1.8371, 2.1213), 1e-4)
f = Fig(30, 20, [O3, (3.2, 0, 0), (0, 3.2, 0), (0, 0, 3.4)], width=580)
q1 = gcircle(O3, EX, EY, rho, 0, math.pi / 2, 90)
q2 = gcircle(O3, EY, EZ, rho, 0, math.pi / 2, 90)
q3 = gcircle(O3, EZ, EX, rho, 0, math.pi / 2, 90)
f.fill(q1 + q2 + q3, THEORY, 0.07)
f.axes(((0, 3.2), (0, 3.2), (0, 3.4)))
for q in (q1, q2, q3):
    f.line(q, THEORY, 1.3, None, 0.55, 0.5)
f.guide([P5f, P5], TEXT, 0.8, 1.5)
f.guide([P5, Q5], TEXT, 0.8, 1.5)
f.line([O3, P5f], THEORY, 2.4, "7 4", 1.0)
f.line([O3, Q5], BASE, 3.6, None, 1.0)
f.line([O3, P5], PRACTICE, 3.0)
f.right_angle(P5f, vsub(O3, P5f), EZ, 17, TEXT, 1.5)
f.right_angle(Q5, vsub(O3, Q5), vsub(P5, Q5), 12)
ph_pts = f.arc(O3, EZ, P5, 0.95, PRACTICE, 2.2)
th_pts = f.arc(O3, EX, P5f, 0.72, REMARK, 2.2)
f.point(O3, TEXT, 3.6)
f.point(P5f, TEXT, 4.4)
f.point(Q5, BASE, 4.0)
f.point(P5, PRACTICE, 4.8)
f.place(O3, it("O"), NAME, prefs=["l", "ul", "dl"])
f.place(P5f, it("P") + "′", NAME, prefs=["dr", "r", "d"])
f.place(P5, it("P") + "(" + it(RHO) + ", " + it(THETA) + ", " + it(PHI) + ")", NAME, PRACTICE,
        prefs=["ur", "r", "u"])
f.angle_label(ph_pts, it(PHI), ANG, PRACTICE)
f.angle_label(th_pts, it(THETA), ANG, REMARK)
f.side_label(O3, P5, it(RHO), NAME + 2, PRACTICE, side=-1, t=0.62, d=6)
f.side_label(O3, P5f, it(RHO) + " sin " + it(PHI), NAME, THEORY, side=-1, t=0.62, d=6)
f.side_label(O3, Q5, it(RHO) + " cos " + it(PHI), NAME, BASE, side=+1, t=0.5, d=8)
f.render(
    "kuresel-kurulum",
    "Küresel koordinatlar: <em>&#961;</em> = |<em>OP</em>|, <em>&#966;</em> pozitif <em>Z</em>-ekseni "
    "ile <em>OP</em> arasındaki açı, <em>&#952;</em> silindirik koordinatlardaki açıdır. <em>OP</em>&#8242;"
    "<em>P</em> dik üçgeninden |<em>OP</em>&#8242;| = <em>&#961;</em> sin <em>&#966;</em> ve "
    "<em>z</em> = <em>&#961;</em> cos <em>&#966;</em> okunur. Soluk yüzey, <em>&#961;</em> = 3 "
    "küresinin birinci bölgedeki parçasıdır (şekilde <em>&#952;</em> = &#960;/3, "
    "<em>&#966;</em> = &#960;/4).",
    "Point P on the sphere rho = 3 with OP of length rho, the angle phi from the positive Z axis "
    "to OP, the foot P' in the XY plane with OP' = rho sin phi, the Z-axis segment rho cos phi, "
    "and the angle theta from the X axis to OP'")


# ===========================================================================
# 6. skk-kuresel-ornek: P(sqrt3, 3, 2) = (4, pi/3, pi/3)
# ===========================================================================
s3 = math.sqrt(3)
P6 = (s3, 3.0, 2.0)
P6f, Q6 = (s3, 3.0, 0.0), (0.0, 0.0, 2.0)
assert abs(vnorm(P6) - 4) < 1e-12
assert abs(math.acos(P6[2] / 4) - math.pi / 3) < 1e-12 and abs(math.atan2(3, s3) - math.pi / 3) < 1e-12
f = Fig(30, 20, [O3, (2.6, 0, 0), (0, 3.8, 0), (0, 0, 3.2)], width=580)
f.axes(((0, 2.6), (0, 3.8), (0, 3.2)))
for k in (1, 2):
    f.tick((k, 0, 0), EX)
for k in (1, 2, 3):
    f.tick((0, k, 0), EY)
for k in (1, 2, 3):
    f.tick((0, 0, k), EZ)
f.guide([P6f, (s3, 0, 0)], TEXT, 0.6, 1.2)
f.guide([P6f, (0, 3, 0)], TEXT, 0.6, 1.2)
f.guide([P6f, P6], TEXT, 0.8, 1.5)
f.guide([P6, Q6], TEXT, 0.8, 1.5)
f.line([O3, P6f], THEORY, 2.2, "7 4", 0.95)
f.line([O3, P6], PRACTICE, 3.0)
f.right_angle(P6f, vsub(O3, P6f), EZ, 17, TEXT, 1.5)
ph_pts = f.arc(O3, EZ, P6, 0.9, PRACTICE, 2.2)
th_pts = f.arc(O3, EX, P6f, 0.7, REMARK, 2.2)
f.point(O3, TEXT, 3.6)
f.point(P6f, TEXT, 4.4)
f.point(Q6, TEXT, 3.6)
f.point(P6, PRACTICE, 4.8)
f.hollow((s3, 0, 0), TEXT, 3.2)
f.hollow((0, 3, 0), TEXT, 3.2)
f.place(O3, it("O"), NAME, prefs=["dl", "l", "d"])
f.place(P6f, it("P") + "′", NAME, prefs=["dr", "r", "d"])
f.place(P6, it("P") + "(" + SQRT + "3, 3, 2)", NAME, PRACTICE, prefs=["ur", "r", "u"])
f.place(Q6, "2", NAME, prefs=["l", "ul", "dl"])
f.place((s3, 0, 0), SQRT + "3", NAME, prefs=["dl", "d", "l"])
f.place((0, 3, 0), "3", NAME, prefs=["d", "dr", "dl"])
f.angle_label(ph_pts, it(PHI) + " = " + PI + "/3", ANG - 1, PRACTICE)
f.angle_label(th_pts, it(THETA) + " = " + PI + "/3", ANG - 1, REMARK)
f.side_label(O3, P6, it(RHO) + " = 4", NAME + 1, PRACTICE, side=-1, t=0.62, d=6)
f.render(
    "kuresel-ornek",
    "<em>P</em>(&#8730;3, 3, 2) noktası: <em>&#961;</em> = |<em>OP</em>| = 4, <em>XY</em>-düzlemindeki "
    "<em>P</em>&#8242; izdüşümü birinci bölgede olduğundan <em>&#952;</em> = &#960;/3, "
    "cos <em>&#966;</em> = 2/4 olduğundan <em>&#966;</em> = &#960;/3. Eksenlerdeki çentikler "
    "birer birim aralıklıdır.",
    "Point P(sqrt3, 3, 2) with OP of length 4, its foot P'(sqrt3, 3, 0) with dashed guides to "
    "sqrt3 on the X axis and 3 on the Y axis, the height 2 on the Z axis, and the angles "
    "phi = pi/3 and theta = pi/3")


# ===========================================================================
# 7. skk-koni: phi = pi/4, z = sqrt(x^2 + y^2)
# ===========================================================================
H7 = 2.5
f = Fig(35, 18, [(2.8, 0, 0), (-2.8, 0, 0), (0, 2.8, 0), (0, -2.8, 0), (0, 0, 3.9), O3,
                 (2.5, 0, 2.5), (-2.5, 0, 2.5), (0, 2.5, 2.5), (0, -2.5, 2.5)], width=560)
f.surfaces.append(cone_surface(+1, H7))
rim = hcircle(H7, H7)
f.fill_hull([O3] + rim, PRACTICE, 0.13)
f.fill(rim, PRACTICE, 0.05)
f.axes(((-2.8, 2.8), (-2.8, 2.8), (0, 3.9)))
f.line(rim, PRACTICE, 1.9, None, 0.95)
az = math.radians(35)
tsil = math.acos(math.tan(math.radians(18)))
for sg in (+1, -1):
    t = az + sg * tsil
    f.line([O3, (H7 * math.cos(t), H7 * math.sin(t), H7)], PRACTICE, 1.8, None, 0.95)
tg = az - math.radians(38)
G = (H7 * math.cos(tg), H7 * math.sin(tg), H7)
assert not f.hidden(lerp(O3, G, 0.5))
f.line([O3, G], THEORY, 3.0)
ph_pts = f.arc(O3, EZ, G, 0.9, THEORY, 2.2)
f.point(O3, TEXT, 3.6)
f.place(O3, it("O"), NAME, prefs=["dl", "l", "d"])
f.angle_label(ph_pts, it(PHI) + " = " + PI + "/4", ANG - 1, THEORY)
right_rim = max(rim, key=lambda P: f.px(P)[0])
f.place(right_rim, it("z") + " = " + SQRT + "(" + it("x") + "² + " + it("y") + "²)", NAME, PRACTICE,
        prefs=["r", "ur", "dr"], d=10)
f.render(
    "koni",
    "<em>&#966;</em> = &#960;/4 denkleminin grafiği: tepesi <em>O</em>&#8217;da, ekseni "
    "<em>Z</em>-ekseni olan ve <em>XY</em>-düzleminin üstünde kalan <em>z</em> = "
    "&#8730;(<em>x</em>² + <em>y</em>²) konisi (0 &#8804; <em>z</em> &#8804; 2,5 parçası). "
    "Mavi ana doğru <em>Z</em>-ekseniyle &#960;/4 açı yapar; koninin arkasında kalan çizgiler kesiklidir.",
    "Translucent cone z = sqrt(x^2 + y^2) with apex O and axis Z up to z = 2.5, its top rim, its "
    "outline, and one generator making the angle phi = pi/4 with the positive Z axis")


# ===========================================================================
# 8. skk-kuresel-yuzeyler: rho = 2, phi = pi/4, theta = pi/4 meet at P(1, 1, sqrt2)
# ===========================================================================
P8 = (1.0, 1.0, math.sqrt(2))
assert abs(vnorm(P8) - 2) < 1e-12 and abs(math.acos(P8[2] / 2) - math.pi / 4) < 1e-12
f = Fig(18, 24, [O3, (2.8, 0, 0), (0, 2.8, 0), (0, 0, 2.8)], width=560)
b26 = 2.6 / math.sqrt(2)
H8 = [O3, (b26, b26, 0), (b26, b26, 2.6), (0, 0, 2.6)]
s1 = gcircle(O3, EX, EY, 2, 0, math.pi / 2, 90)
s2 = gcircle(O3, EY, EZ, 2, 0, math.pi / 2, 90)
s3_ = gcircle(O3, EZ, EX, 2, 0, math.pi / 2, 90)
crim = hcircle(2.2, 2.2, 0, math.pi / 2, 90)
f.axes(((0, 2.8), (0, 2.8), (0, 2.8)), hidden=False)
f.fill(s1 + s2 + s3_, BASE, 0.12)
f.fill([O3] + crim, PRACTICE, 0.14)
f.fill(H8, THEORY, 0.12)
for q in (s1, s2, s3_):
    f.line(q, BASE, 1.3, None, 0.7, 0.5)
f.line(crim, PRACTICE, 1.3, None, 0.75, 0.5)
f.line([O3, (2.2, 0, 2.2)], PRACTICE, 1.2, None, 0.6, 0.5)
f.line([O3, (0, 2.2, 2.2)], PRACTICE, 1.2, None, 0.6, 0.5)
f.line(H8 + [H8[0]], THEORY, 1.2, None, 0.65, 0.5)
u45 = vunit((1, 1, 0))
f.line(hcircle(math.sqrt(2), math.sqrt(2), 0, math.pi / 2, 90), TEXT, 2.0, None, 0.9)
f.line(gcircle(O3, u45, EZ, 2, 0, math.pi / 2, 90), TEXT, 2.0, None, 0.9)
Gc = (2.2 / math.sqrt(2), 2.2 / math.sqrt(2), 2.2)
f.line([O3, Gc], TEXT, 2.0, None, 0.9)
f.point(P8, TEXT, 5.0)
f.place(O3, it("O"), NAME, prefs=["dl", "l", "d"])
f.place(P8, it("P") + "(2, " + PI + "/4, " + PI + "/4)", NAME, prefs=["r", "dr", "ur"], d=9)
f.place(gcircle(O3, EX, EY, 2, 0, math.pi / 2, 90)[20], it(RHO) + " = 2", NAME + 1, BASE,
        prefs=["dl", "d", "l"], d=8)
f.place(crim[70], it(PHI) + " = " + PI + "/4", NAME + 1, PRACTICE, prefs=["u", "ur", "ul"], d=8)
f.place(H8[2], it(THETA) + " = " + PI + "/4", NAME + 1, THEORY, prefs=["u", "ur", "r"], d=8)
f.render(
    "kuresel-yuzeyler",
    "Küresel koordinat yüzeyleri: <em>&#961;</em> = 2 küresi, <em>&#966;</em> = &#960;/4 konisi ve "
    "<em>&#952;</em> = &#960;/4 yarım düzlemi (birinci bölgedeki parçaları). Koyu çizgiler ikişer "
    "ikişer kesişimlerdir; üçü birden yalnız <em>P</em>(1, 1, &#8730;2) noktasında, yani küresel "
    "koordinatları (2, &#960;/4, &#960;/4) olan noktada buluşur.",
    "One eighth of the sphere rho = 2, the part of the cone phi = pi/4 and of the half-plane "
    "theta = pi/4 in the first octant, their pairwise intersection curves, and their common point "
    "P(1, 1, sqrt2)")


# ===========================================================================
# 9. skk-uzayda-kutupsal: direction angles alpha, beta, gamma of OP
# ===========================================================================
P9 = (2.6, 1.4, 2.6)
f = Fig(50, 16, [O3, (3.2, 0, 0), (0, 3.2, 0), (0, 0, 3.2), P9], width=560)
f.axes(((0, 3.2), (0, 3.2), (0, 3.2)), colors=(THEORY, BASE, PRACTICE), width=1.8, opacity=0.95)
f.guide([P9, (P9[0], P9[1], 0)], TEXT, 0.45, 1.1)
f.point((P9[0], P9[1], 0), TEXT, 2.6)
f.arrow(O3, P9, TEXT, 3.0, 13.0)
a_pts = f.arc(O3, EX, P9, 1.0, THEORY, 2.2, head=None)
b_pts = f.arc(O3, EY, P9, 1.45, BASE, 2.2, head=None)
g_pts = f.arc(O3, EZ, P9, 0.68, PRACTICE, 2.2, head=None)
f.point(O3, TEXT, 3.6)
f.place(O3, it("O"), NAME, prefs=["dl", "l", "d"])
f.place(P9, it("P") + "(" + it("x") + ", " + it("y") + ", " + it("z") + ")", NAME, prefs=["ur", "r", "u"])
f.side_label(O3, P9, it(RHO), NAME + 2, TEXT, side=-1, t=0.72, d=6)
f.angle_label(a_pts, it(ALPHA), ANG, THEORY)
f.angle_label(b_pts, it(BETA), ANG, BASE)
f.angle_label(g_pts, it(GAMMA), ANG, PRACTICE)
f.render(
    "uzayda-kutupsal",
    "Uzayda kutupsal koordinatlar: <em>&#961;</em> = |<em>OP</em>| ve <em>OP</em> vektörünün "
    "<em>X</em>-, <em>Y</em>-, <em>Z</em>-eksenlerinin pozitif yönleriyle yaptığı <em>&#945;</em>, "
    "<em>&#946;</em>, <em>&#947;</em> doğrultu açıları. Her açı yayı, açının ölçüldüğü eksenin rengindedir.",
    "Vector OP from the origin to P(x, y, z) of length rho and three arcs at O for its direction "
    "angles alpha, beta, gamma with the positive X, Y and Z axes, each in the colour of its axis")


# ===========================================================================
# 10. skk-eyer: z = x^2 - y^2
# ===========================================================================
E10 = 1.5
f = Fig(28, 32, [(2.4, 0, 0), (-2.4, 0, 0), (0, 2.4, 0), (0, -2.4, 0), (0, 0, 3.0), (0, 0, -2.9),
                 (E10, E10, 0), (-E10, -E10, 0), (E10, -E10, 0), (-E10, E10, 0),
                 (E10, 0, E10 ** 2), (0, E10, -E10 ** 2)], width=560)


def saddle(x, y):
    return (x, y, x * x - y * y)


def sgrid(n):
    return [-E10 + 2 * E10 * k / n for k in range(n + 1)]


f.axes(((-2.4, 2.4), (-2.4, 2.4), (-2.9, 3.0)), hidden=False)
f.S.surface(saddle, (-E10, E10), (-E10, E10), nu=24, nv=24, fill=THEORY, stroke="none",
            opacity=(0.05, 0.17), stroke_width=0.0, stroke_opacity=0.0)
for c in sgrid(6)[1:-1]:
    if abs(c) > 1e-9:
        f.line([saddle(c, v) for v in sgrid(60)], THEORY, 0.8, None, 0.45, 0.2)
        f.line([saddle(v, c) for v in sgrid(60)], THEORY, 0.8, None, 0.45, 0.2)
for c in (-E10, E10):
    f.line([saddle(c, v) for v in sgrid(80)], THEORY, 1.4, None, 0.85, 0.6)
    f.line([saddle(v, c) for v in sgrid(80)], THEORY, 1.4, None, 0.85, 0.6)
f.line([saddle(v, 0) for v in sgrid(120)], PRACTICE, 3.0)
f.line([saddle(0, v) for v in sgrid(120)], BASE, 3.0)
f.point(O3, TEXT, 4.4)
f.place(O3, it("O"), NAME, prefs=["dr", "dl", "r"], d=8)
f.place(saddle(E10, 0), it("z") + " = " + it("x") + "²", NAME + 1, PRACTICE, prefs=["l", "ul", "u", "r"], d=9)
f.place(saddle(0, E10), it("z") + " = " + MINUS + it("y") + "²", NAME + 1, BASE, prefs=["r", "dr", "d"], d=9)
f.place(saddle(-E10, E10), it("z") + " = " + it("x") + "² " + MINUS + " " + it("y") + "²", NAME, THEORY,
        prefs=["d", "dr", "dl", "r"], d=10)
f.render(
    "eyer",
    "<em>z</em> = <em>x</em>² &#8722; <em>y</em>² eyer yüzeyinin &#8722;1,5 &#8804; <em>x</em>, "
    "<em>y</em> &#8804; 1,5 parçası. <em>XZ</em>-düzlemiyle kesiti yukarı açılan <em>z</em> = "
    "<em>x</em>² parabolü, <em>YZ</em>-düzlemiyle kesiti aşağı açılan <em>z</em> = "
    "&#8722;<em>y</em>² parabolüdür; ikisi <em>O</em> eyer noktasında buluşur.",
    "Saddle surface z = x^2 - y^2 over the square from -1.5 to 1.5 with a wire grid, the upward "
    "parabola z = x^2 in the XZ plane and the downward parabola z = -y^2 in the YZ plane, "
    "meeting at the saddle point O")


# ===========================================================================
# 11. skk-kure-kosinus: rho = 4 cos(phi), the sphere x^2 + y^2 + (z - 2)^2 = 4
# ===========================================================================
M11, N11, P11 = (0.0, 0.0, 2.0), (0.0, 0.0, 4.0), (0.0, 2.0, 2.0)
assert abs(vnorm(vsub(P11, M11)) - 2) < 1e-12
assert abs(vdot(vsub(O3, P11), vsub(N11, P11))) < 1e-12
assert abs(vnorm(P11) - 4 * math.cos(math.pi / 4)) < 1e-12
f = Fig(30, 15, [(2.6, 0, 0), (-2.6, 0, 0), (0, 2.6, 0), (0, -2.6, 0), (0, 0, 4.8), O3,
                 (0, 2, 2), (0, -2, 2)], width=560)
f.surfaces.append(sphere_surface(M11, 2.0))
sq_ = 0.7
f.fill([(-sq_, -sq_, 0), (sq_, -sq_, 0), (sq_, sq_, 0), (-sq_, sq_, 0)], TEXT, 0.08)
cx, cy = f.px(M11)
Rpx = 2.0 * f.ppu
f.p.add(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{Rpx:.1f}" fill="{THEORY}" fill-opacity="0.10" stroke="none"/>')
for rr, ww, op in ((0.95, 0.10, 0.05), (0.87, 0.16, 0.04), (0.77, 0.2, 0.03)):
    f.p.add(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{rr * Rpx:.1f}" fill="none" stroke="{THEORY}" '
            f'stroke-width="{ww * Rpx:.1f}" stroke-opacity="{op}"/>')
f.axes(((-2.6, 2.6), (-2.6, 2.6), (0, 4.8)))
f.p.add(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{Rpx:.1f}" fill="none" stroke="{THEORY}" '
        f'stroke-width="1.6" opacity="0.85"/>')
f._reg_px([(cx + Rpx * math.cos(2 * math.pi * k / 96), cy + Rpx * math.sin(2 * math.pi * k / 96))
           for k in range(97)], 1.0)
f.vis_line(gcircle(M11, EX, EY, 2.0), THEORY, 1.6, 0.9, 0.8)
f.vis_line(gcircle(M11, EY, EZ, 2.0), THEORY, 1.6, 0.9, 0.8)
f.line([O3, N11], REMARK, 2.0, None, 0.95)
f.line([P11, N11], BASE, 2.2)
f.line([O3, P11], PRACTICE, 3.0)
f.right_angle(P11, vsub(O3, P11), vsub(N11, P11), 13)
ph_pts = f.arc(O3, EZ, P11, 0.8, PRACTICE, 2.2)
f.point(O3, TEXT, 4.2)
f.point(M11, TEXT, 3.6)
f.point(N11, TEXT, 4.2)
f.point(P11, PRACTICE, 4.8)
f.place(O3, it("O"), NAME, prefs=["dl", "l", "d"])
f.place(N11, it("N") + "(0, 0, 4)", NAME, prefs=["ul", "l", "ur"], d=8)
f.place(M11, it("M") + "(0, 0, 2)", NAME, prefs=["l", "dl", "ul"], d=8)
f.place(P11, it("P"), NAME + 1, PRACTICE, prefs=["r", "ur", "dr"], d=8)
f.angle_label(ph_pts, it(PHI), ANG, PRACTICE)
f.side_label(O3, P11, it(RHO) + " = 4 cos " + it(PHI), NAME, PRACTICE, side=-1, t=0.55, d=6)
f.render(
    "kure-kosinus",
    "<em>&#961;</em> = 4 cos <em>&#966;</em> küresi: merkezi <em>M</em>(0, 0, 2), yarıçapı 2, "
    "<em>XY</em>-düzlemine <em>O</em>&#8217;da teğet. <em>ON</em> bir çap olduğundan <em>OPN</em> "
    "üçgeni <em>P</em>&#8217;de diktir ve |<em>OP</em>| = 4 cos <em>&#966;</em> olur (şekilde "
    "<em>P</em>(0, 2, 2), <em>&#966;</em> = &#960;/4).",
    "Translucent sphere with center M(0, 0, 2) and radius 2 tangent to the XY plane at O, the "
    "top point N(0, 0, 4), a point P on the sphere with OP = 4 cos phi, the right angle at P in "
    "triangle OPN, and the angle phi at O")


# ===========================================================================
# 12. skk-cift-koni: x^2 + y^2 = z^2
# ===========================================================================
H12 = 2.2
f = Fig(35, 15, [(2.8, 0, 0), (-2.8, 0, 0), (0, 2.8, 0), (0, -2.8, 0), (0, 0, 3.5), (0, 0, -2.8),
                 (2.2, 0, 2.2), (-2.2, 0, 2.2), (0, 2.2, -2.2), (0, -2.2, -2.2)], width=560)
f.surfaces.append(cone_surface(+1, H12))
f.surfaces.append(cone_surface(-1, H12))
rim_u, rim_d = hcircle(H12, H12), hcircle(H12, -H12)
f.fill_hull([O3] + rim_d, THEORY, 0.13)
f.fill_hull([O3] + rim_u, PRACTICE, 0.13)
f.fill(rim_u, PRACTICE, 0.05)
f.axes(((-2.8, 2.8), (-2.8, 2.8), (-2.8, 3.5)))
f.line(rim_u, PRACTICE, 1.9, None, 0.95)
f.vis_line(rim_d, THEORY, 1.9, 0.95)
az = math.radians(35)
tsil = math.acos(math.tan(math.radians(15)))
# silhouettes: upper nappe where cos(t - az) = tan(el), lower nappe where cos(t - az) = -tan(el)
for sg in (+1, -1):
    t = az + sg * tsil
    f.line([O3, (H12 * math.cos(t), H12 * math.sin(t), H12)], PRACTICE, 1.8, None, 0.95)
    t = az + sg * (math.pi - tsil)
    f.line([O3, (H12 * math.cos(t), H12 * math.sin(t), -H12)], THEORY, 1.8, None, 0.95)
tg, tgd = az - math.radians(40), az + math.radians(40)
Gu = (H12 * math.cos(tg), H12 * math.sin(tg), H12)
Gd = (H12 * math.cos(tgd), H12 * math.sin(tgd), -H12)
assert not f.hidden(lerp(O3, Gu, 0.5)) and not f.hidden(lerp(O3, Gd, 0.5))
f.line([O3, Gu], PRACTICE, 3.0)
f.line([O3, Gd], THEORY, 3.0)
pu = f.arc(O3, EZ, Gu, 0.75, PRACTICE, 2.2)
pd = f.arc(O3, EZ, Gd, 1.15, THEORY, 2.2)
f.point(O3, TEXT, 3.6)
f.place(O3, it("O"), NAME, prefs=["l", "dl", "ul"])
f.angle_label(pu, it(PHI) + " = " + PI + "/4", ANG - 1, PRACTICE)
f.angle_label(pd, it(PHI) + " = 3" + PI + "/4", ANG - 1, THEORY)
ru = max(rim_u, key=lambda P: f.px(P)[0])
rd = max(rim_d, key=lambda P: f.px(P)[0])
f.place(ru, it("z") + " = " + SQRT + "(" + it("x") + "² + " + it("y") + "²)", NAME, PRACTICE,
        prefs=["r", "ur", "dr"], d=10)
f.place(rd, it("z") + " = " + MINUS + SQRT + "(" + it("x") + "² + " + it("y") + "²)", NAME, THEORY,
        prefs=["dr", "d", "r"], d=14, only=True)
f.render(
    "cift-koni",
    "<em>x</em>² + <em>y</em>² = <em>z</em>² çift konisi (|<em>z</em>| &#8804; 2,2 parçası): üstteki "
    "<em>&#966;</em> = &#960;/4 konisi ile alttaki <em>&#966;</em> = 3&#960;/4 konisinin birleşimi. "
    "İki açı da pozitif <em>Z</em>-ekseninden ölçülür; koninin arkasında kalan çizgiler kesiklidir.",
    "Double cone x^2 + y^2 = z^2 for |z| up to 2.2: the upper nappe phi = pi/4 and the lower nappe "
    "phi = 3pi/4 in two colours, each with a generator and its angle measured from the positive Z axis")


# ---------------------------------------------------------------------------
for name, content in OUT.items():
    path = OUT_DIR / f"analytic-skk-{name}.md"
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(content)
    print("wrote", path.name)
