# -*- coding: utf-8 -*-
"""Figures for dersler/analitik-geometri/uzayda-duzlem-denklemleri.qmd (chapter key: udz).

All drawings are three-dimensional and go through scripts/svg_plot3.py (an
orthographic Camera on an equal-aspect svg_plot.Plot panel). Planes are drawn
as translucent parallelogram patches that also act as occluders, so the parts
of lines and axes behind them turn thin and dashed. The figures go INSIDE the
box they explain (example, solution, proof), never inside a definition box.

Labels are placed after the projection, in page pixels: `Canvas.place` tries
a ring of candidate positions around the anchor and keeps the cheapest one,
i.e. the one that touches no registered line, point or earlier label.

Usage:   python scripts/analytic_figures/udz.py
         python scripts/center_figures.py "analytic-udz-*.md" --keep-width
Output:  scripts/_figures/analytic-udz-<name>.md
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

TALL_SCENES = set()
from svg_plot3 import (Camera, Space, vadd, vsub, vscale, vdot, vcross, vnorm,  # noqa: E402
                       vunit)

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
OUT = {}

MINUS, TIMES, SQRT, NORM, THETA, PI = "−", "×", "√", "‖", "θ", "π"
NAME, DESC, AXIS = 14.0, 12.5, 14.5          # font sizes (px)
O = (0.0, 0.0, 0.0)

# ---------------------------------------------------------------------------
# text helpers
# ---------------------------------------------------------------------------


def it(s):
    return f'<tspan font-style="italic">{s}</tspan>'


def sub(s, size=NAME):
    return (f'<tspan font-size="{0.74 * size:.1f}" dy="4">{s}</tspan>'
            f'<tspan dy="-4">&#8203;</tspan>')


def num(v):
    """Integer with a real minus sign."""
    return (MINUS + str(-v)) if v < 0 else str(v)


def triple(*vs):
    return "(" + ", ".join(v if isinstance(v, str) else num(v) for v in vs) + ")"


def x_(a, b):
    """'a × b' with the operands already marked up."""
    return f"{a} {TIMES} {b}"


U_, V_, W_ = it("u"), it("v"), it("w")
UxV = x_(U_, V_)


def e_(k, size=NAME):
    return it("e") + sub(str(k), size)


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


def lay_width(s, size):
    """Rough advance width of plain text in a book serif, for placing over-arrows."""
    w = 0.0
    for ch in html.unescape(s):
        if ch.isupper():
            w += 0.64
        elif ch.islower():
            w += 0.47
        elif ch.isdigit():
            w += 0.52
        elif ch == " ":
            w += 0.25
        elif ch in "(),.":
            w += 0.33
        else:
            w += 0.58
    return w * size


def inside(poly, x, y):
    """Even-odd point-in-polygon test in page pixels."""
    c = False
    n = len(poly)
    for i in range(n):
        (x1, y1), (x2, y2) = poly[i], poly[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
            c = not c
    return c


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


RING = [a * 22.5 for a in range(16)]


def close(a, b, tol=1e-9):
    return all(abs(p - q) < tol for p, q in zip(a, b))


# ---------------------------------------------------------------------------
# a drawing surface that remembers what it drew (in pixels) for label placement
# ---------------------------------------------------------------------------


class Canvas:
    def __init__(self):
        self.segs, self.dots, self.boxes, self.texts = [], [], [], []

    def reg_px(self, q, w=1.0):
        for a, b in zip(q, q[1:]):
            self.segs.append((a, b, w))

    def cost(self, box, pad=2.5):
        b = (box[0] - pad, box[1] - pad, box[2] + pad, box[3] + pad)
        c = 0.0
        for o in self.boxes:
            ov = box_overlap(b, o)
            if ov > 0:
                c += 60 + ov / 5
        for x, y, r in self.dots:
            if b[0] - r < x < b[2] + r and b[1] - r < y < b[3] + r:
                c += 45
        for p, q, w in self.segs:
            if w and seg_hits_box(p, q, b):
                c += 10 * w
        return c

    def text_px(self, cx, cy, s, size, color=TEXT, opacity=1.0, halo=True, register=True):
        """Text whose (estimated) box is centred on (cx, cy)."""
        w, h = text_width(s, size), size
        if register:
            self.boxes.append((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2))
        self.texts.append(dict(cx=cx, base=cy + 0.30 * h, w=w, s=s, size=size, color=color,
                               opacity=opacity, halo=halo))

    def emit_texts(self):
        """Markup of the labels. A label that sticks out past the drawing on the left or
        right is anchored at its outer edge: the real glyphs are narrower than the width
        estimate, so the estimated box then stays on the canvas that center_figures trims."""
        xs = [x for p, q, _ in self.segs for x in (p[0], q[0])] + [x for x, _, _ in self.dots]
        gx0, gx1 = (min(xs), max(xs)) if xs else (-1e9, 1e9)
        out = []
        for t in self.texts:
            if isinstance(t, str):
                out.append(t)
                continue
            x, anchor = t["cx"], "middle"
            if t["cx"] + t["w"] / 2 > gx1:
                x, anchor = t["cx"] + t["w"] / 2, "end"
            elif t["cx"] - t["w"] / 2 < gx0:
                x, anchor = t["cx"] - t["w"] / 2, "start"
            op = f' opacity="{t["opacity"]}"' if t["opacity"] < 1 else ""
            stroke = (f' stroke="{BG}" stroke-width="3.6" stroke-linejoin="round" paint-order="stroke"'
                      if t["halo"] else "")
            out.append(f'<text x="{x:.1f}" y="{t["base"]:.1f}" fill="{t["color"]}" font-size="{t["size"]}" '
                       f'text-anchor="{anchor}"{op}{stroke}>{t["s"]}</text>')
        return out

    def over_arrow(self, cx, ytop, w, color, width=1.1):
        """Small right arrow over a name (the vector AB with an arrow on top)."""
        x0, x1 = cx - w / 2, cx + w / 2
        self.texts.append(f'<line x1="{x0:.1f}" y1="{ytop:.1f}" x2="{x1 - 3:.1f}" y2="{ytop:.1f}" '
                          f'stroke="{color}" stroke-width="{width}"/>')
        self.texts.append(f'<polygon points="{x1 + 1:.1f},{ytop:.1f} {x1 - 4.5:.1f},{ytop - 2.6:.1f} '
                          f'{x1 - 4.5:.1f},{ytop + 2.6:.1f}" fill="{color}"/>')

    def anchor_px(self, anchor):
        raise NotImplementedError

    def place(self, anchor, s, size=NAME, color=TEXT, prefs=None, d=7.0, only=False,
              far=(0, 6, 13, 22, 34), leader=False, opacity=1.0, tall=0.0):
        """Put text s next to anchor; prefs are page angles in degrees (0 = right,
        90 = up) tried first, earlier ones winning ties. The cheapest candidate
        (no line, point or label under it) is used. `tall` adds room above the
        text (for an arrow drawn over a name)."""
        x, y = self.anchor_px(anchor)
        w, h = text_width(s, size), size + tall
        order = list(prefs) if prefs is not None else []
        if not only:
            order += [a for a in RING
                      if all(o == "c" or abs(((a - o + 180) % 360) - 180) > 11 for o in order)]
        best = None
        for k, ang in enumerate(order):
            if ang == "c":
                cands = [(x, y, 0)]
            else:
                th = math.radians(ang)
                c_, s_ = math.cos(th), -math.sin(th)
                ext = min(w / 2 / abs(c_) if abs(c_) > 1e-9 else 1e9,
                          h / 2 / abs(s_) if abs(s_) > 1e-9 else 1e9)
                cands = [(x + c_ * (d + e + ext), y + s_ * (d + e + ext), e) for e in far]
            for cx, cy, e in cands:
                box = (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)
                c = self.cost(box) + k * 0.9 + e * 0.35
                if best is None or c < best[0]:
                    best = (c, cx, cy, e)
        c, cx, cy, e = best
        if c > 12:
            print(f"   label '{html.unescape(_TAG.sub('', s))}': cost {c:.1f}")
        if leader and e >= 13:
            bx = min(max(x, cx - w / 2), cx + w / 2)
            by = min(max(y, cy - h / 2), cy + h / 2)
            L = math.hypot(bx - x, by - y)
            if L > 8:
                ux, uy = (bx - x) / L, (by - y) / L
                self.texts.insert(0, f'<line x1="{x + ux * 5:.1f}" y1="{y + uy * 5:.1f}" '
                                     f'x2="{bx - ux * 3:.1f}" y2="{by - uy * 3:.1f}" stroke="{color}" '
                                     f'stroke-width="0.9" opacity="0.75"/>')
        ty = cy + tall / 2
        self.text_px(cx, ty, s, size, color, opacity)
        self.boxes[-1] = (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)
        return cx, ty

    def vec_name(self, anchor, runs, size=NAME, color=TEXT, prefs=None, d=7.0, only=False,
                 far=(0, 6, 13, 22, 34)):
        """One label made of runs (text, arrow?); runs with arrow=True are italic point
        names with a small arrow over them, e.g. [("AB", True), (" = (1, 2)", False)].
        The label is a single <text>; only the arrows use the glyph-width estimate."""
        s = "".join(it(r) if a else r for r, a in runs)
        est = text_width(s, size)
        lay = sum(lay_width(r, size) for r, _ in runs)
        cx, cy = self.place(anchor, s, size, color, prefs, d, only, far, tall=5)
        self.texts.pop()                          # redraw it left-anchored; keep its box
        x0 = cx - (est + lay) / 4                 # between the estimate and the layout width
        base = cy + 0.30 * size
        self.texts.append(f'<text x="{x0:.1f}" y="{base:.1f}" fill="{color}" font-size="{size}" '
                          f'stroke="{BG}" stroke-width="3.6" stroke-linejoin="round" '
                          f'paint-order="stroke">{s}</text>')
        x = x0
        for r, a in runs:
            w = lay_width(r, size)
            if a:
                self.over_arrow(x + w / 2 + 0.06 * size, base - 0.92 * size, w - 1, color)
            x += w


class Fig(Canvas):
    """A 3-D scene: camera, equal-aspect panel fitted to `extent`, label registry."""

    def __init__(self, az, el, extent, width=600, pad=70, max_h=None):
        super().__init__()
        self.cam = Camera(az, el)
        pr = [self.cam.project(P) for P in extent]
        xs, ys = [a for a, _, _ in pr], [b for _, b, _ in pr]
        dx, dy = max(xs) - min(xs), max(ys) - min(ys)
        self.ppu = width / dx
        if max_h and dy * self.ppu > max_h:
            self.ppu = max_h / dy
        w, h = dx * self.ppu, dy * self.ppu
        self.p = Plot(pad, pad, w, h, (min(xs), max(xs)), (min(ys), max(ys)))
        self.S = Space(self.p, self.cam)
        self.W, self.H = w + 2 * pad, h + 2 * pad
        self.d = self.cam.d
        self.occ = []

    # -- occlusion by flat pieces (planes, faces) -----------------------------
    def add_occluder(self, Ps):
        """A planar polygon that hides whatever lies behind it on the page."""
        n = vcross(vsub(Ps[1], Ps[0]), vsub(Ps[2], Ps[0]))
        if vdot(n, self.d) < 0:
            n = vscale(-1.0, n)
        self.occ.append((Ps[0], vunit(n), [self.px(P) for P in Ps]))

    def hidden(self, P):
        x, y = self.px(P)
        return any(vdot(vsub(P, A), n) < -1e-6 and inside(poly, x, y) for A, n, poly in self.occ)

    def oline(self, P0, P1, color=TEXT, width=1.3, opacity=0.75, w=1.0, n=240):
        """Straight segment drawn solid where visible and thin-dashed where an occluder hides it."""
        pts = [vadd(P0, vscale(k / n, vsub(P1, P0))) for k in range(n + 1)]
        runs, cur, state = [], [pts[0]], self.hidden(pts[0])
        for P in pts[1:]:
            h = self.hidden(P)
            if h != state:
                runs.append((state, cur + [P]))
                cur, state = [P], h
            else:
                cur.append(P)
        runs.append((state, cur))
        for h, run in runs:
            if len(run) < 2:
                continue
            if h:
                self.line([run[0], run[-1]], color, 1.0, "4 3", 0.5, w * 0.4)
            else:
                self.line([run[0], run[-1]], color, width, None, opacity, w)

    # -- projection ---------------------------------------------------------
    def px(self, P):
        X, Y = self.S.pt(P)
        return (self.p.X(X), self.p.Y(Y))

    def anchor_px(self, anchor):
        if isinstance(anchor, tuple) and anchor and anchor[0] == "px":
            return anchor[1], anchor[2]
        return self.px(anchor)

    def sang(self, vec):
        """Page angle (degrees, 0 = right, 90 = up) of the space direction vec."""
        X, Y, _ = self.cam.project(vadd(self.cam.center, vec))
        return math.degrees(math.atan2(Y, X))

    def u(self, pixels):
        return pixels / self.ppu

    def px_len(self, vec):
        """Page length (in page units) of the projection of vec."""
        X, Y, _ = self.cam.project(vadd(self.cam.center, vec))
        return math.hypot(X, Y)

    def front(self, n):
        return vdot(n, self.d) > 0

    def _reg(self, Ps, w=1.0):
        self.reg_px([self.px(P) for P in Ps], w)

    # -- drawing ------------------------------------------------------------
    def line(self, Ps, color=TEXT, width=1.6, dash=None, opacity=1.0, w=1.0):
        self.S.line(Ps, color, width, dash, opacity)
        if w:
            self._reg(Ps, w)

    def arrow(self, P0, P1, color=THEORY, width=2.6, head=12.0, dash=None, opacity=1.0, w=1.0,
              halo=False):
        if halo:
            self.S.line([P0, P1], BG, width + 3.4, None, 1.0)
        self.S.arrow(P0, P1, color, width, head, dash, opacity)
        if w:
            self._reg([P0, P1], w)

    def polygon(self, Ps, fill=THEORY, opacity=0.14, stroke=None, width=1.0, s_opacity=0.7,
                dash=None, w=0.6):
        self.S.polygon(Ps, fill, opacity)
        if stroke:
            self.line(list(Ps) + [Ps[0]], stroke, width, dash, s_opacity, w)

    def point(self, P, color=TEXT, r=3.8):
        self.S.point(P, color, r)
        x, y = self.px(P)
        self.dots.append((x, y, r))

    def right_angle(self, Q, a, b, size=13, color=TEXT, width=1.2, opacity=0.9):
        s = self.u(size)
        a, b = vunit(a), vunit(b)
        pts = [vadd(Q, vscale(s, a)), vadd(Q, vadd(vscale(s, a), vscale(s, b))), vadd(Q, vscale(s, b))]
        self.line(pts, color, width, None, opacity, w=0.5)

    def arc(self, Q, a, b, r_px, color=TEXT, width=1.3, opacity=0.9, head=None, n=40, w=0.6):
        """Circular arc at Q from direction a to direction b (the smaller angle)."""
        e1 = vunit(a)
        bb = vunit(b)
        e2 = vunit(vsub(bb, vscale(vdot(bb, e1), e1)))
        th = math.acos(max(-1.0, min(1.0, vdot(e1, bb))))
        r = self.u(r_px)
        pts = [vadd(Q, vadd(vscale(r * math.cos(th * k / n), e1), vscale(r * math.sin(th * k / n), e2)))
               for k in range(n + 1)]
        if head:
            self.line(pts[:-2], color, width, None, opacity, w)
            self.S.arrow(pts[-4], pts[-1], color, width, head, None, opacity)
        else:
            self.line(pts, color, width, None, opacity, w)
        return pts

    def axes(self, rng, labels=("X", "Y", "Z"), width=1.3, opacity=0.75, color=TEXT, head=10.0,
             label_prefs=None):
        E = ((1, 0, 0), (0, 1, 0), (0, 0, 1))
        for k, (lo, hi) in enumerate(rng):
            e = E[k]
            if lo < 0:
                self.oline(vscale(lo, e), O, color, width, opacity)
            tip = vscale(hi, e)
            neck = vscale(hi - self.u(head * 1.2) / max(1e-9, self.px_len(e)), e)
            self.oline(O, neck, color, width, opacity)
            self.S.arrow(neck, tip, color, width, head, None, opacity)
            self._reg([neck, tip], 1.0)
            if labels and labels[k]:
                a = self.sang(e)
                prefs = (label_prefs or {}).get(k, [a, a + 25, a - 25])
                self.place(tip, it(labels[k]), AXIS, TEXT, prefs=prefs, d=5)

    # -- output -------------------------------------------------------------
    def render(self, name, caption, aria):
        print(f"-- {name} (warnings above belong to it)")
        for t in self.emit_texts():
            self.p.add(t)
        # Tall scenes (height/width above ~1.15) stay in the standard column:
        # at the wide width they would be 800-900 px tall on screen.
        css = "ders-grafik" if name in TALL_SCENES or self.H > 1.15 * self.W else WIDE
        OUT[name] = figure(round(self.W), round(self.H), [self.p], caption, css, aria)


# ---------------------------------------------------------------------------
# chapter helpers
# ---------------------------------------------------------------------------
SUBW = 0.74 * 0.52        # advance of a subscript digit, in em of the base size


def nm(letter, k=None, size=NAME):
    """Italic point or vector name with an optional subscript: P_0, v_1, ..."""
    return it(letter) + (sub(str(k), size) if k is not None else "")


def at(letter, k, *vs, size=NAME):
    """'P_0(1, -3, 2)'."""
    return nm(letter, k, size) + triple(*vs)


PLANE = it("D")           # the plane (Fraktur D in the text; the figure font has no Fraktur)


def lin(A, B, C, D, size=NAME):
    """'5x - 2y + 3z - 17 = 0' with italic variables and real minus signs."""
    out = []
    for c, v in ((A, "x"), (B, "y"), (C, "z"), (D, None)):
        if c == 0:
            continue
        sign = MINUS if c < 0 else "+"
        mag = abs(c)
        body = (str(mag) if v is None else ("" if mag == 1 else str(mag)) + it(v))
        if not out:
            out.append((MINUS if c < 0 else "") + body)
        else:
            out.append(f"{sign} {body}")
    return " ".join(out) + " = 0"


def plane_eq(A, B, C, D, name=True, size=NAME):
    return (PLANE + ": " if name else "") + lin(A, B, C, D, size)


def basis(n):
    """Orthonormal pair spanning the plane with normal n."""
    k = min(range(3), key=lambda i: abs(n[i]))
    e = [0.0, 0.0, 0.0]
    e[k] = 1.0
    a = vunit(vcross(n, tuple(e)))
    b = vunit(vcross(n, a))
    return a, b


def vbasis(az, el, n):
    """Orthonormal pair of the plane with normal n whose first vector looks horizontal
    on the page for the camera (az, el): patches then have level top and bottom edges."""
    cam = Camera(az, el)
    a = vunit(vcross(n, cam.u))
    if vdot(a, cam.r) < 0:
        a = vscale(-1.0, a)
    b = vunit(vcross(n, a))
    if vdot(b, cam.u) < 0:
        b = vscale(-1.0, b)
    return a, b


def fit(n, pts, margin=0.6, a=None, b=None):
    """Centre and ranges of a patch of the plane with normal n that holds pts."""
    if a is None:
        a, b = basis(n)
    C0 = vscale(1.0 / len(pts), (sum(p[0] for p in pts), sum(p[1] for p in pts), sum(p[2] for p in pts)))
    us = [vdot(vsub(p, C0), a) for p in pts]
    ws = [vdot(vsub(p, C0), b) for p in pts]
    return C0, a, b, (min(us) - margin, max(us) + margin), (min(ws) - margin, max(ws) + margin)


def ahead(f, vec, spread=(0, 30, -30, 60, -60, 90, -90)):
    """Label angles around the page direction of vec: first straight past the tip."""
    a = f.sang(vec)
    return [a + s for s in spread]


def guide(f, Ps, color=TEXT, opacity=0.5, width=1.0, dash="4 3"):
    """Thin dashed helper line, registered so that labels keep off it."""
    f.S.guide(Ps, color, opacity, width, dash)
    f._reg(Ps, 0.8)


def coord_box(f, P, opacity=0.4):
    """Dashed guides reading off the coordinates of P (floor L, riser, level to the z-axis)."""
    x, y, z = P
    guide(f, [(x, 0, 0), (x, y, 0), (0, y, 0)], TEXT, opacity)
    guide(f, [(x, y, 0), P], TEXT, opacity)
    guide(f, [P, (0, 0, z)], TEXT, opacity)


def corners_of(P, a, b, s1, s2):
    return [vadd(P, vadd(vscale(u, a), vscale(w, b))) for u in s1 for w in s2]


def patch(f, P, a, b, s1=(-1.0, 1.0), s2=(-1.0, 1.0), color=THEORY, op=0.13, occlude=True,
          s_op=0.6):
    """Translucent parallelogram {P + s a + t b}; it hides what lies behind it."""
    corners = [vadd(P, vadd(vscale(u, a), vscale(w, b)))
               for u, w in ((s1[0], s2[0]), (s1[1], s2[0]), (s1[1], s2[1]), (s1[0], s2[1]))]
    if occlude:
        f.add_occluder(corners)
    f.polygon(corners, color, op, stroke=color, width=1.0, s_opacity=s_op, w=1.0)
    return corners


def inset(corners, k, t=0.16):
    """A point inside the patch, near its corner k."""
    Cc = vscale(0.25, vadd(vadd(corners[0], corners[1]), vadd(corners[2], corners[3])))
    return vadd(corners[k], vscale(t, vsub(Cc, corners[k])))


def on_plane(n, D, P, tol=1e-9):
    return abs(vdot(n, P) + D) < tol


def run_width(s, size):
    """Layout width of a label run: base-size glyphs plus shrunken subscript digits."""
    w = 0.0
    for m in re.finditer(r'<tspan font-size="[\d.]+" dy="4">(.*?)</tspan>', s):
        w += len(m.group(1)) * SUBW * size
    rest = re.sub(r'<tspan font-size="[\d.]+" dy="4">.*?</tspan>', "", s)
    return w + lay_width(html.unescape(_TAG.sub("", rest)).replace("​", ""), size)


def vlabel(f, anchor, runs, size=NAME, color=TEXT, prefs=None, d=7.0, only=False,
           far=(0, 6, 13, 22, 34)):
    """Label made of runs (markup, arrow?); arrowed runs get a small arrow over them
    (the vector P0P). Drawn start-anchored so the arrows sit over their names."""
    s = "".join(r for r, _ in runs)
    cx, cy = f.place(anchor, s, size, color, prefs, d, only, far, tall=5)
    f.texts.pop()
    total = sum(run_width(r, size) for r, _ in runs)
    x0 = cx - total / 2
    base = cy + 0.30 * size
    f.texts.append(f'<text x="{x0:.1f}" y="{base:.1f}" fill="{color}" font-size="{size}" '
                   f'stroke="{BG}" stroke-width="3.6" stroke-linejoin="round" '
                   f'paint-order="stroke">{s}</text>')
    x = x0
    for r, a in runs:
        w = run_width(r, size)
        if a:
            f.over_arrow(x + w / 2 + 0.05 * size, base - 0.95 * size, w - 1, color)
        x += w


def crossing_gap(f, A0, A1, B0, B1):
    """If the page images of segments A and B cross, return which one is behind there
    ('A' or 'B') so the caller can draw that one first and the other with a halo."""
    p, q, r, s = f.px(A0), f.px(A1), f.px(B0), f.px(B1)
    den = (q[0] - p[0]) * (s[1] - r[1]) - (q[1] - p[1]) * (s[0] - r[0])
    if abs(den) < 1e-9:
        return None
    t = ((r[0] - p[0]) * (s[1] - r[1]) - (r[1] - p[1]) * (s[0] - r[0])) / den
    u = ((r[0] - p[0]) * (q[1] - p[1]) - (r[1] - p[1]) * (q[0] - p[0])) / den
    if not (0 <= t <= 1 and 0 <= u <= 1):
        return None
    da = f.S.depth(vadd(A0, vscale(t, vsub(A1, A0))))
    db = f.S.depth(vadd(B0, vscale(u, vsub(B1, B0))))
    return ("A" if da < db else "B", t, u)


def line_over(f, A0, A1, color, width, others, other_color=TEXT, other_width=1.3, gap_px=26):
    """Draw segment A; where it crosses one of the segments in `others` on the page, the one
    behind is interrupted by a short background-coloured gap (drawn again with a casing)."""
    f.line([A0, A1], color, width)
    la = math.hypot(*[p - q for p, q in zip(f.px(A1), f.px(A0))])
    for B0, B1 in others:
        hit = crossing_gap(f, A0, A1, B0, B1)
        if not hit:
            continue
        who, t, u = hit
        if who == "B":                           # the other one is behind: case A over it
            dt = gap_px / 2 / la
            halo_line(f, vadd(A0, vscale(max(0, t - dt), vsub(A1, A0))),
                      vadd(A0, vscale(min(1, t + dt), vsub(A1, A0))), color, width)
        else:                                    # A is behind: case the other one over A
            lb = math.hypot(*[p - q for p, q in zip(f.px(B1), f.px(B0))])
            du = gap_px / 2 / lb
            halo_line(f, vadd(B0, vscale(max(0, u - du), vsub(B1, B0))),
                      vadd(B0, vscale(min(1, u + du), vsub(B1, B0))), other_color, other_width,
                      opacity=0.75)


def halo_line(f, P0, P1, color, width=2.0, gap=5.0, opacity=1.0):
    """A line with a background-coloured casing: whatever it crosses gets a small gap."""
    f.S.line([P0, P1], BG, width + gap, None, 1.0)
    f.line([P0, P1], color, width, None, opacity)


def hollow(f, P, color=TEXT, r=3.4):
    f.S.hollow(P, color, r, 1.5)
    x, y = f.px(P)
    f.dots.append((x, y, r))


LINE_W = 2.2


def plane_label(f, corners, s, size=NAME, color=THEORY, ks=(0, 1, 2, 3), ts=(0.12, 0.2, 0.3)):
    """Put the plane's name or equation inside its patch, near the emptiest corner."""
    poly = [f.px(P) for P in corners]
    w, h = text_width(s, size), size
    best = None
    A, B, D = corners[0], corners[1], corners[3]
    for i in range(1, 20):
        for j in range(1, 20):
            fu, fw = i / 20, j / 20
            Q = vadd(A, vadd(vscale(fu, vsub(B, A)), vscale(fw, vsub(D, A))))
            x, y = f.px(Q)
            box = (x - w / 2 - 4, y - h / 2 - 3, x + w / 2 + 4, y + h / 2 + 3)
            if not all(inside(poly, bx, by) for bx in (box[0], box[2]) for by in (box[1], box[3])):
                continue
            # prefer the corner ks[0]: distance (in patch fractions) to it
            cu, cw = [(0, 0), (1, 0), (1, 1), (0, 1)][ks[0]]
            c = f.cost(box) + 6 * math.hypot(fu - cu, fw - cw)
            c += 15 * sum(1 for p, q, _ in f.segs if seg_hits_box(p, q, box))
            if best is None or c < best[0]:
                best = (c, x, y)
    if best is None:
        # too narrow on the page: put it just outside a corner, with a thin leader
        mx = sum(x for x, _ in poly) / 4
        my = sum(y for _, y in poly) / 4
        for i, (x, y) in enumerate(poly):
            a0 = math.atan2(y - my, x - mx)
            for da in (0, 0.4, -0.4, 0.8, -0.8):
                for r in (10, 18, 28, 40):
                    ux, uy = math.cos(a0 + da), math.sin(a0 + da)
                    ext = min(w / 2 / abs(ux) if abs(ux) > 1e-9 else 1e9,
                              h / 2 / abs(uy) if abs(uy) > 1e-9 else 1e9)
                    bx, by = x + ux * (r + ext), y + uy * (r + ext)
                    box = (bx - w / 2, by - h / 2, bx + w / 2, by + h / 2)
                    c = f.cost(box) + 0.15 * r + (0 if i in ks else 3)
                    if best is None or c < best[0]:
                        best = (c, bx, by, x, y)
        _, bx, by, x, y = best
        qx = min(max(x, bx - w / 2), bx + w / 2)
        qy = min(max(y, by - h / 2), by + h / 2)
        L = math.hypot(qx - x, qy - y)
        if L > 8:
            ux, uy = (qx - x) / L, (qy - y) / L
            f.texts.insert(0, f'<line x1="{x + ux * 2:.1f}" y1="{y + uy * 2:.1f}" '
                              f'x2="{qx - ux * 3:.1f}" y2="{qy - uy * 3:.1f}" stroke="{color}" '
                              f'stroke-width="0.9" opacity="0.75"/>')
        return f.place(("px", bx, by), s, size, color, prefs=["c"], only=True)
    return f.place(("px", best[1], best[2]), s, size, color, prefs=["c"], only=True)


def perp_in_plane(f, n, pixels=60):
    """Unit vector in the plane with normal n whose page image makes the clearest right
    angle with the page image of n (long, and far from n's page direction)."""
    a, b = basis(n)
    an = math.radians(f.sang(n))
    best = None
    for k in range(72):
        t = 2 * math.pi * k / 72
        e = vadd(vscale(math.cos(t), a), vscale(math.sin(t), b))
        L = f.px_len(e)
        ae = math.radians(f.sang(e))
        score = L * abs(math.sin(ae - an))
        if best is None or score > best[0]:
            best = (score, e)
    return best[1]


# Colors: plane patches THEORY, normals PRACTICE, in-plane vectors BASE, lines REMARK/THEORY.
NORMAL, INPLANE, LINE = PRACTICE, BASE, THEORY
ONLY = set(sys.argv[1:])


def want(name):
    return not ONLY or name in ONLY


# ===========================================================================
# 1. nokta-ve-normal: P0, P in the plane, P0P perpendicular to n (schematic)
# ===========================================================================
if want("nokta-ve-normal"):
    A_, B_ = (1.0, 0, 0), (0, 1.0, 0)
    P0, P = (0.25, -0.8, 0.0), (-0.35, 1.05, 0.0)
    Nv = (0, 0, 1.7)
    ext = [(1.3, -2.3, 0), (-1.3, 2.3, 0), (1.3, 2.3, 0), (-1.3, -2.3, 0), vadd(P0, Nv)]
    f = Fig(32, 24, ext, width=540, pad=70)
    C = patch(f, O, A_, B_, (-1.3, 1.3), (-2.3, 2.3))
    f.arrow(P0, P, INPLANE, 2.6, 12.0)
    f.right_angle(P0, Nv, vsub(P, P0), 14)
    f.arrow(P0, vadd(P0, Nv), NORMAL, 3.0, 13.0)
    f.point(P0)
    f.point(P)
    f.place(inset(C, 2, 0.13), PLANE, NAME + 2, THEORY, prefs=["c"], only=True)
    f.place(P0, nm("P", 0), NAME, prefs=[225, 200, 250])
    f.place(P, it("P"), NAME, prefs=[0, 20, 340])
    vlabel(f, vscale(0.5, vadd(P0, P)), [(nm("P", 0) + it("P"), True)], NAME, INPLANE,
           prefs=[270, 290, 250], d=6)
    f.place(vadd(P0, Nv), it("n") + " = " + triple(it("A"), it("B"), it("C")), NAME, NORMAL,
            prefs=[0, 20, 340], d=9)
    f.render(
        "nokta-ve-normal",
        "Düzlemin bir <em>P</em><sub>0</sub> noktası ve normali <em>n</em>. Düzlemin her <em>P</em> "
        "noktası için <em>P</em><sub>0</sub><em>P</em> vektörü düzlemin içindedir ve <em>n</em>&#8217;ye diktir.",
        "A horizontal plane patch D with two points P0 and P in it, the vector P0P inside the plane, "
        "and the normal vector n = (A, B, C) standing on P0 at a right angle to P0P")


# ===========================================================================
# 2. ornek-nokta-normal: 5x - 2y + 3z - 17 = 0 through P0(1, -3, 2)
# ===========================================================================
if want("ornek-nokta-normal"):
    Nn, Dc = (5, -2, 3), -17
    P0 = (1, -3, 2)
    assert on_plane(Nn, Dc, P0)
    AZ, EL = 35, 22
    a, b = vbasis(AZ, EL, Nn)
    Nv = vscale(0.4, Nn)
    s1, s2 = (-2.4, 2.4), (-1.5, 1.5)
    ext = [(0, -5.2, 0), (3.2, 0, 0), (0, 1.5, 0), (0, 0, 4.6), vadd(P0, Nv)]
    ext += corners_of(P0, a, b, s1, s2)
    f = Fig(AZ, EL, ext, width=560, pad=70)
    C = patch(f, P0, a, b, s1, s2)
    f.axes(((0, 3.2), (-5.2, 1.5), (0, 4.6)))
    coord_box(f, P0, 0.4)
    f.right_angle(P0, Nv, perp_in_plane(f, Nn), 15)
    f.arrow(P0, vadd(P0, Nv), NORMAL, 3.0, 13.0, halo=True)
    f.point(O, TEXT, 3.0)
    f.place(O, it("O"), NAME, prefs=[250, 230, 280])
    f.point(P0)
    f.place(P0, at("P", 0, 1, -3, 2), NAME, prefs=[200, 180, 220, 160])
    f.place(vadd(P0, Nv), it("n") + " = " + triple(5, -2, 3), NAME, NORMAL,
            prefs=[20, 0, 40], d=9)
    plane_label(f, C, plane_eq(5, -2, 3, -17))
    f.render(
        "ornek-nokta-normal",
        "5<em>x</em> &#8722; 2<em>y</em> + 3<em>z</em> &#8722; 17 = 0 düzleminin <em>P</em><sub>0</sub>(1, "
        "&#8722;3, 2) çevresindeki parçası ve normali <em>n</em> = (5, &#8722;2, 3) (0,4 katı çizildi).",
        "Coordinate axes, a patch of the plane 5x - 2y + 3z - 17 = 0 around P0(1, -3, 2) with dashed "
        "coordinate guides, and the normal n = (5, -2, 3) standing on P0")


# ===========================================================================
# 3. ornek-dogruya-dik: 7x + 2y - 3z - 21 = 0 through P0(4, -2, 1), line along v
# ===========================================================================
if want("ornek-dogruya-dik"):
    Nn, Dc = (7, 2, -3), -21
    P0 = (4, -2, 1)
    assert on_plane(Nn, Dc, P0)
    AZ, EL = 35, 22
    a, b = vbasis(AZ, EL, Nn)
    Vs = vscale(0.3, Nn)
    s1, s2 = (-2.6, 2.6), (-1.8, 1.8)
    L0, L1 = vadd(P0, vscale(-0.42, Nn)), vadd(P0, vscale(0.55, Nn))
    ext = [(0, -4, 0), (0, 3, 0), (5, 0, 0), (0, 0, 4), L0, L1] + corners_of(P0, a, b, s1, s2)
    f = Fig(AZ, EL, ext, width=560, pad=70)
    C = patch(f, P0, a, b, s1, s2)
    f.axes(((0, 5), (-4, 3), (0, 4)))
    f.oline(L0, L1, LINE, LINE_W, 0.95)
    f.right_angle(P0, Nn, perp_in_plane(f, Nn), 15)
    f.arrow(P0, vadd(P0, Vs), NORMAL, 3.0, 13.0, halo=True)
    f.point(O, TEXT, 3.0)
    f.place(O, it("O"), NAME, prefs=[250, 230, 280])
    f.point(P0)
    f.place(P0, at("P", 0, 4, -2, 1), NAME, prefs=[160, 180, 140, 200])
    f.place(vadd(P0, Vs), it("v") + " = " + it("n") + " = " + triple(7, 2, -3), NAME, NORMAL,
            prefs=[90, 60, 120, 30], d=9)
    f.place(L1, it("d"), NAME + 1, LINE, prefs=[0, 330, 30])
    plane_label(f, C, plane_eq(7, 2, -3, -21))
    f.render(
        "ornek-dogruya-dik",
        "<em>P</em><sub>0</sub>(4, &#8722;2, 1) noktasından geçen ve doğrultmanı <em>v</em> = (7, 2, "
        "&#8722;3) olan <em>d</em> doğrusuna dik düzlem. Doğrunun düzlemin arkasında kalan kısmı kesiklidir.",
        "Coordinate axes, a patch of the plane 7x + 2y - 3z - 21 = 0 around P0(4, -2, 1) and the line d "
        "through P0 along v = (7, 2, -3) meeting the plane at a right angle; v = n drawn as an arrow")


# ===========================================================================
# 4. ornek-kartezyen-dogruya-dik: 2x + y + z - 1 = 0, P0(0, 0, 1), H(1/3, -1/3, 2/3)
# ===========================================================================
if want("ornek-kartezyen-dogruya-dik"):
    Nn, Dc = (2, 1, 1), -1
    P0, H = (0, 0, 1), (1 / 3, -1 / 3, 2 / 3)
    V = (2, 1, 1)
    assert on_plane(Nn, Dc, P0) and on_plane(Nn, Dc, H)
    assert close(vadd((1, 0, 1), vscale(-1 / 3, V)), H)
    AZ, EL = -35, 22
    a, b = vbasis(AZ, EL, Nn)
    C0, a, b, s1, s2 = fit(Nn, [P0, H], 0.75, a, b)
    s1 = (s1[0] - 0.5, s1[1] + 0.5)
    L0, L1 = vadd((1, 0, 1), vscale(-1.05, V)), vadd((1, 0, 1), vscale(0.45, V))
    ext = [(2.2, 0, 0), (0, -1.6, 0), (0, 1.8, 0), (0, 0, 2.2), L0, L1]
    ext += corners_of(C0, a, b, s1, s2)
    f = Fig(AZ, EL, ext, width=560, pad=70)
    C = patch(f, C0, a, b, s1, s2)
    f.axes(((0, 2.2), (-1.6, 1.8), (0, 2.2)))
    f.oline(L0, L1, LINE, LINE_W, 0.95)
    f.right_angle(H, V, perp_in_plane(f, Nn), 14)
    f.arrow(H, vadd(H, vscale(0.28, V)), NORMAL, 2.8, 12.0, halo=True)
    hollow(f, (1, 0, 1), LINE)
    f.point(O, TEXT, 3.0)
    f.place(O, it("O"), NAME, prefs=[250, 230, 280])
    f.point(P0)
    f.point(H)
    f.place(P0, at("P", 0, 0, 0, 1), NAME, prefs=[160, 180, 140])
    f.place(H, it("H"), NAME, prefs=[200, 220, 180, 250])
    f.place(vadd(H, vscale(0.28, V)), it("v") + " = " + triple(2, 1, 1), NAME, NORMAL,
            prefs=[300, 330, 270], d=8)
    f.place(L1, it("d"), NAME + 1, LINE, prefs=[30, 0, 60])
    plane_label(f, C, plane_eq(2, 1, 1, -1))
    f.render(
        "ornek-kartezyen-dogruya-dik",
        "2<em>x</em> + <em>y</em> + <em>z</em> &#8722; 1 = 0 düzlemi ve ona dik <em>d</em> doğrusu. "
        "<em>d</em> düzlemi <em>H</em>(1/3, &#8722;1/3, 2/3) noktasında dik keser; boş daire "
        "<em>d</em>&#8217;nin (1, 0, 1) noktasıdır.",
        "Coordinate axes, a patch of the plane 2x + y + z - 1 = 0 containing P0(0, 0, 1) and H, and the "
        "line d = (1, 0, 1) + t(2, 1, 1) piercing the plane at H at a right angle, with v = (2, 1, 1) at H")




# Direction vectors v1, v2 of the two-direction examples keep their colors across figures.
C1, C2 = BASE, REMARK


def skew_pair(f, A0, A1, B0, B1, ca, cb, width=2.0):
    """Two lines; where their page images cross, the one behind gets a gap."""
    hit = crossing_gap(f, A0, A1, B0, B1)
    if hit and hit[0] == "A":
        f.line([A0, A1], ca, width)
        halo_line(f, B0, B1, cb, width)
    else:
        f.line([B0, B1], cb, width)
        halo_line(f, A0, A1, ca, width)


# ===========================================================================
# 5. iki-dogrultu: plane through P0 parallel to v1, v2; two skew lines below (schematic)
# ===========================================================================
if want("iki-dogrultu"):
    V1, V2 = (0.8, 1.0, 0.0), (-0.6, 1.0, 0.0)
    assert vcross(V1, V2)[2] > 0
    P0, P = (0.15, -1.0, 0.0), (-0.35, 1.45, 0.0)
    Nv = (0, 0, 1.6)
    ZL1, ZL2 = -1.7, -2.5
    A1, B1 = (0.0, -1.0, ZL1), (0.0, 0.6, ZL2)
    t1, t2 = (-1.2, 1.3), (-1.3, 1.4)
    D10, D11 = vadd(A1, vscale(t1[0], V1)), vadd(A1, vscale(t1[1], V1))
    D20, D21 = vadd(B1, vscale(t2[0], V2)), vadd(B1, vscale(t2[1], V2))
    s1, s2 = (-1.3, 1.3), (-2.5, 2.5)
    ext = corners_of(O, (1, 0, 0), (0, 1, 0), s1, s2) + [vadd(P0, Nv), D10, D11, D20, D21]
    f = Fig(32, 22, ext, width=520, pad=70)
    C = patch(f, O, (1.0, 0, 0), (0, 1.0, 0), s1, s2)
    f.arrow(P0, vadd(P0, vscale(0.95, V1)), C1, 2.2, 11.0, dash="6 4")
    f.arrow(P0, vadd(P0, vscale(0.95, V2)), C2, 2.2, 11.0, dash="6 4")
    f.arrow(P0, P, TEXT, 1.4, 9.0, opacity=0.8)
    f.right_angle(P0, Nv, perp_in_plane(f, (0, 0, 1)), 14)
    f.arrow(P0, vadd(P0, Nv), NORMAL, 3.0, 13.0)
    f.point(P0)
    f.point(P)
    skew_pair(f, D10, D11, D20, D21, C1, C2)
    a1, a2 = vadd(A1, vscale(-0.45, V1)), vadd(B1, vscale(-0.35, V2))
    f.arrow(a1, vadd(a1, vscale(0.95, V1)), C1, 3.4, 12.0)
    f.arrow(a2, vadd(a2, vscale(0.95, V2)), C2, 3.4, 12.0)
    plane_label(f, C, PLANE, NAME + 2, ks=(2,))
    f.place(P0, nm("P", 0), NAME, prefs=[315, 290, 340])
    f.place(P, it("P"), NAME, prefs=[90, 60, 120])
    f.place(vadd(P0, Nv), it("n") + " = " + x_(nm("v", 1), nm("v", 2)), NAME, NORMAL,
            prefs=[0, 20, 340], d=9)
    f.place(vadd(P0, vscale(0.95, V1)), nm("v", 1), NAME, C1, prefs=ahead(f, V1, (-40, 40, 0)))
    f.place(vadd(P0, vscale(0.95, V2)), nm("v", 2), NAME, C2, prefs=ahead(f, V2, (40, -40, 0)))
    f.place(D11, nm("d", 1), NAME + 1, C1, prefs=[0, 330, 30])
    f.place(D21, nm("d", 2), NAME + 1, C2, prefs=[0, 30, 330])
    f.place(vadd(a1, vscale(0.95, V1)), nm("v", 1), NAME, C1, prefs=ahead(f, V1, (-70, 70, -45)))
    f.place(vadd(a2, vscale(0.95, V2)), nm("v", 2), NAME, C2, prefs=ahead(f, V2, (70, -70, 45)))
    f.render(
        "iki-dogrultu",
        "Altta doğrultmanları <em>v</em><sub>1</sub> ve <em>v</em><sub>2</sub> olan aykırı "
        "<em>d</em><sub>1</sub>, <em>d</em><sub>2</sub> doğruları; üstte <em>P</em><sub>0</sub>&#8217;dan "
        "geçip ikisine de paralel olan düzlem. Kesikli oklar <em>v</em><sub>1</sub> ve "
        "<em>v</em><sub>2</sub>&#8217;nin <em>P</em><sub>0</sub>&#8217;a taşınmış temsilcileridir; normal "
        "<em>n</em> = <em>v</em><sub>1</sub> &#215; <em>v</em><sub>2</sub> ikisine de diktir.",
        "A horizontal plane patch D through P0 with dashed copies of v1 and v2 inside it, a point P, "
        "and the normal n = v1 x v2; below it two skew lines d1 and d2 with direction arrows v1 and v2")


# ===========================================================================
# 6. ornek-iki-dogru: d1 = (0,1,2) + t(2,1,3), d2 = (1,0,3) + s(5,1,1), P0(1, 1, 3)
# ===========================================================================
if want("ornek-iki-dogru"):
    V1, V2 = (2, 1, 3), (5, 1, 1)
    Q1, Q2, P0 = (0, 1, 2), (1, 0, 3), (1, 1, 3)
    # skew: no common point (the mixed product of Q2 - Q1, v1, v2 is non-zero)
    assert vdot(vsub(Q2, Q1), vcross(V1, V2)) != 0
    D10, D11 = vadd(Q1, vscale(-0.6, V1)), vadd(Q1, vscale(0.75, V1))
    D20, D21 = vadd(Q2, vscale(-0.5, V2)), vadd(Q2, vscale(0.5, V2))
    ext = [O, (2.5, 0, 0), (0, 2.5, 0), (0, 0, 4.8), D10, D11, D20, D21]
    f = Fig(35, 24, ext, width=560, pad=70)
    f.axes(((0, 2.5), (0, 2.5), (0, 4.8)))
    coord_box(f, P0, 0.4)
    skew_pair(f, D10, D11, D20, D21, C1, C2)
    f.arrow(Q1, vadd(Q1, vscale(0.5, V1)), C1, 3.4, 12.0)
    f.arrow(Q2, vadd(Q2, vscale(0.33, V2)), C2, 3.4, 12.0)
    f.point(Q1, C1, 3.2)
    f.point(Q2, C2, 3.2)
    f.point(O, TEXT, 3.0)
    f.place(O, it("O"), NAME, prefs=[250, 230, 280])
    f.point(P0)
    f.place(P0, at("P", 0, 1, 1, 3), NAME, prefs=[90, 60, 120, 30])
    f.place(vadd(Q1, vscale(0.5, V1)), nm("v", 1) + " = " + triple(2, 1, 3), NAME, C1,
            prefs=ahead(f, V1, (-90, 90, -60, 60)))
    f.place(vadd(Q2, vscale(0.33, V2)), nm("v", 2) + " = " + triple(5, 1, 1), NAME, C2,
            prefs=ahead(f, V2, (-90, 90, -60, 60)))
    f.place(D11, nm("d", 1), NAME + 1, C1, prefs=ahead(f, V1, (0, 30, -30)))
    f.place(D21, nm("d", 2), NAME + 1, C2, prefs=ahead(f, V2, (0, 30, -30)))
    f.render(
        "ornek-iki-dogru",
        "Aykırı <em>d</em><sub>1</sub> ve <em>d</em><sub>2</sub> doğruları, doğrultmanları ve "
        "<em>P</em><sub>0</sub>(1, 1, 3) noktası. Doğrular kesişmez; şekilde çakışır gibi göründükleri yerde "
        "arkadaki doğru kesintilidir.",
        "Coordinate axes, the skew lines d1 = (0, 1, 2) + t(2, 1, 3) and d2 = (1, 0, 3) + s(5, 1, 1) with "
        "direction arrows v1 and v2, and the point P0(1, 1, 3) with dashed coordinate guides")


# ===========================================================================
# 7. ornek-iki-dogru-duzlem: -2x + 13y - 3z - 2 = 0 through P0(1, 1, 3), sides along v1, v2
# ===========================================================================
if want("ornek-iki-dogru-duzlem"):
    V1, V2 = (2, 1, 3), (5, 1, 1)
    Nn, Dc = vcross(V1, V2), -2
    assert Nn == (-2, 13, -3)
    P0 = (1, 1, 3)
    assert on_plane(Nn, Dc, P0)
    s1, s2 = (-0.6, 0.6), (-0.4, 0.4)
    Nv = vscale(0.15, Nn)
    AZ, EL = 35, 15
    ext = corners_of(P0, V1, V2, s1, s2) + [O, (4, 0, 0), (0, 3.2, 0), (0, 0, 5.4), vadd(P0, Nv)]
    f = Fig(AZ, EL, ext, width=560, pad=70)
    C = patch(f, P0, V1, V2, s1, s2)
    f.axes(((0, 4), (0, 3.2), (0, 5.4)))
    f.arrow(P0, vadd(P0, vscale(0.5, V1)), C1, 3.0, 12.0)
    f.arrow(P0, vadd(P0, vscale(0.33, V2)), C2, 3.0, 12.0)
    f.right_angle(P0, Nv, perp_in_plane(f, Nn), 15)
    f.arrow(P0, vadd(P0, Nv), NORMAL, 3.0, 13.0, halo=True)
    f.point(O, TEXT, 3.0)
    f.place(O, it("O"), NAME, prefs=[250, 230, 280])
    f.point(P0)
    f.place(P0, nm("P", 0), NAME, prefs=[225, 200, 250, 315])
    f.place(vadd(P0, vscale(0.5, V1)), nm("v", 1), NAME, C1, prefs=ahead(f, V1, (0, 40, -40)))
    f.place(vadd(P0, vscale(0.33, V2)), nm("v", 2), NAME, C2, prefs=ahead(f, V2, (0, 40, -40)))
    f.place(vadd(P0, Nv), it("n") + " = " + x_(nm("v", 1), nm("v", 2)) + " = " + triple(-2, 13, -3),
            NAME, NORMAL, prefs=ahead(f, Nn, (0, 60, -60, 90, -90)), d=9)
    plane_label(f, C, plane_eq(-2, 13, -3, -2))
    f.render(
        "ornek-iki-dogru-duzlem",
        "&#8722;2<em>x</em> + 13<em>y</em> &#8722; 3<em>z</em> &#8722; 2 = 0 düzleminin kenarları "
        "<em>v</em><sub>1</sub> ve <em>v</em><sub>2</sub> doğrultusunda olan bir parçası ve normali "
        "<em>n</em> = <em>v</em><sub>1</sub> &#215; <em>v</em><sub>2</sub> (0,15 katı çizildi).",
        "Coordinate axes, a patch of the plane -2x + 13y - 3z - 2 = 0 with sides along v1 = (2, 1, 3) "
        "and v2 = (5, 1, 1) around P0(1, 1, 3), the arrows v1 and v2 from P0, and the normal n = v1 x v2")


# ===========================================================================
# 8. ornek-eksenlere-paralel: z = 3 through P0(1, 2, 3), parallel to the XY-plane
# ===========================================================================
if want("ornek-eksenlere-paralel"):
    P0 = (1, 2, 3)
    E1, E2, E3 = (1.0, 0, 0), (0, 1.0, 0), (0, 0, 1.0)
    s1, s2 = (0, 3), (0, 4)
    ext = [O, (4, 0, 0), (0, 5, 0), (0, 0, 4.8)] + corners_of(O, E1, E2, s1, s2)
    f = Fig(35, 24, ext, width=560, pad=70)
    f.S.polygon([(0, 0, 0), (3, 0, 0), (3, 4, 0), (0, 4, 0)], TEXT, 0.06)
    f.line([(3, 0, 0), (3, 4, 0), (0, 4, 0)], TEXT, 0.9, "3 3", 0.45, 0.3)
    C = patch(f, (0, 0, 3), E1, E2, s1, s2)
    f.axes(((0, 4), (0, 5), (0, 4.8)))
    guide(f, [P0, (1, 2, 0)], TEXT, 0.5)
    hollow(f, (1, 2, 0), TEXT, 3.0)
    f.arrow(P0, vadd(P0, E1), INPLANE, 2.8, 12.0)
    f.arrow(P0, vadd(P0, E2), INPLANE, 2.8, 12.0)
    f.right_angle(P0, E3, E2, 13)
    f.arrow(P0, vadd(P0, vscale(1.3, E3)), NORMAL, 3.0, 13.0)
    f.point((0, 0, 3), TEXT, 3.2)
    f.place((0, 0, 3), "3", NAME, prefs=[180, 200, 160])
    f.point(O, TEXT, 3.0)
    f.place(O, it("O"), NAME, prefs=[200, 180, 225])
    f.point(P0)
    f.place(P0, at("P", 0, 1, 2, 3), NAME, prefs=[250, 225, 200, 270])
    f.place(vadd(P0, E1), e_(1), NAME, INPLANE, prefs=ahead(f, E1, (0, 40, -40)))
    f.place(vadd(P0, E2), e_(2), NAME, INPLANE, prefs=ahead(f, E2, (0, 40, -40)))
    f.place(vadd(P0, vscale(1.3, E3)), it("n") + " = " + e_(3), NAME, NORMAL, prefs=[0, 20, 340], d=8)
    plane_label(f, C, PLANE + ": " + it("z") + " = 3", ks=(2,))
    f.render(
        "ornek-eksenlere-paralel",
        "<em>X</em>- ve <em>Y</em>-eksenine paralel olup <em>P</em><sub>0</sub>(1, 2, 3)&#8217;ten geçen "
        "<em>z</em> = 3 düzlemi: <em>XY</em>-düzlemine (soluk) paraleldir, normali <em>e</em><sub>3</sub>&#8217;tür.",
        "Coordinate axes, the horizontal plane z = 3 above the faint XY-plane, the point P0(1, 2, 3) with "
        "a dashed drop to (1, 2, 0), the arrows e1 and e2 inside the plane and the normal n = e3")


# ===========================================================================
# 9. uc-nokta: P1, P2, P3, Q in a plane; n = P1P2 x P1P3 (schematic)
# ===========================================================================
if want("uc-nokta"):
    P1, P2, P3, Q = (0.1, -1.9, 0.0), (1.0, 0.4, 0.0), (-0.1, 1.2, 0.0), (-0.95, 0.25, 0.0)
    Nv = (0, 0, 1.6)
    s1, s2 = (-1.3, 1.3), (-2.6, 2.1)
    ext = corners_of(O, (1, 0, 0), (0, 1, 0), s1, s2) + [vadd(P1, Nv)]
    f = Fig(32, 24, ext, width=540, pad=70)
    C = patch(f, O, (1.0, 0, 0), (0, 1.0, 0), s1, s2)
    f.arrow(P1, Q, REMARK, 1.6, 10.0)
    f.arrow(P1, P2, INPLANE, 2.6, 12.0)
    f.arrow(P1, P3, INPLANE, 2.6, 12.0)
    f.right_angle(P1, Nv, perp_in_plane(f, (0, 0, 1)), 14)
    f.arrow(P1, vadd(P1, Nv), NORMAL, 3.0, 13.0)
    for X in (P1, P2, P3, Q):
        f.point(X)
    plane_label(f, C, PLANE, NAME + 2, ks=(2,))
    f.place(P1, nm("P", 1), NAME, prefs=[180, 200, 160])
    f.place(P2, nm("P", 2), NAME, prefs=[315, 290, 340])
    f.place(P3, nm("P", 3), NAME, prefs=[0, 20, 340])
    f.place(Q, it("Q"), NAME, prefs=[90, 60, 120])
    P12, P13 = nm("P", 1) + nm("P", 2), nm("P", 1) + nm("P", 3)
    vlabel(f, vadd(P1, Nv), [(it("n") + " = ", False), (P12, True), (" " + TIMES + " ", False),
                            (P13, True)], NAME, NORMAL, prefs=[0, 20, 340], d=9)
    f.render(
        "uc-nokta",
        "Doğrudaş olmayan <em>P</em><sub>1</sub>, <em>P</em><sub>2</sub>, <em>P</em><sub>3</sub> noktaları "
        "ve düzlemin herhangi bir <em>Q</em> noktası. <em>P</em><sub>1</sub>&#8217;den çıkan üç vektör de "
        "düzlemin içindedir; normal, ilk ikisinin vektörel çarpımıdır.",
        "A horizontal plane patch D with points P1, P2, P3 and Q, arrows from P1 to P2, P3 and Q inside "
        "the plane, and the normal n = P1P2 x P1P3 standing on P1")


def triangle(f, Ps, color=THEORY, op=0.2):
    """A darker triangle on a plane patch (no occlusion of its own)."""
    f.S.polygon(Ps, color, op)
    f.line(list(Ps) + [Ps[0]], color, 1.0, None, 0.5, 0.6)


def plane_axes_scene(name, Nn, Dc, pts, az, el, axes, margin=0.7, width=560, extra=()):
    """Figure with coordinate axes and a translucent patch of the plane Nn.x + Dc = 0 that
    holds pts; returns (fig, corners)."""
    for P in pts:
        assert on_plane(Nn, Dc, P), (name, P)
    a, b = vbasis(az, el, Nn)
    C0, a, b, s1, s2 = fit(Nn, pts, margin, a, b)
    ext = corners_of(C0, a, b, s1, s2) + [O] + list(extra)
    for k, (lo, hi) in enumerate(axes):
        e = [0.0, 0.0, 0.0]
        e[k] = hi
        ext.append(tuple(e))
        e[k] = lo
        ext.append(tuple(e))
    f = Fig(az, el, ext, width=width, pad=70)
    C = patch(f, C0, a, b, s1, s2)
    f.axes(axes)
    return f, C


# ===========================================================================
# 10. ornek-uc-nokta: x - 3y - 2z = 0 through P1(1,1,-1), P2(-2,-2,2), P3(1,-1,2) and O
# ===========================================================================
UC_AZ, UC_EL = -50, 20
if want("ornek-uc-nokta"):
    P1, P2, P3 = (1, 1, -1), (-2, -2, 2), (1, -1, 2)
    Nn = (1, -3, -2)
    assert vcross(vsub(P2, P1), vsub(P3, P1)) == (-3, 9, 6)        # = -3 (1, -3, -2)
    G = (0, -2 / 3, 1)
    assert close(vscale(1 / 3, vadd(vadd(P1, P2), P3)), G)
    Nv = vscale(0.55, Nn)
    f, C = plane_axes_scene("ornek-uc-nokta", Nn, 0, [P1, P2, P3, O], UC_AZ, UC_EL,
                            ((-3, 3), (-3, 3), (-3, 3)), margin=0.6, extra=[vadd(G, Nv)])
    triangle(f, [P1, P2, P3])
    f.arrow(P1, P2, INPLANE, 2.6, 12.0)
    f.arrow(P1, P3, INPLANE, 2.6, 12.0)
    f.right_angle(G, Nv, perp_in_plane(f, Nn), 13)
    f.arrow(G, vadd(G, Nv), NORMAL, 3.0, 13.0, halo=True)
    f.point(G, NORMAL, 2.6)
    f.point(O, TEXT, 4.4)
    f.place(O, it("O"), NAME, prefs=[315, 290, 250, 200])
    for X, k in ((P1, 1), (P2, 2), (P3, 3)):
        f.point(X)
    f.place(P1, nm("P", 1), NAME, prefs=[270, 300, 240, 0])
    f.place(P2, nm("P", 2), NAME, prefs=[180, 150, 210, 90])
    f.place(P3, nm("P", 3), NAME, prefs=[90, 60, 120, 0])
    f.place(vadd(G, Nv), it("n") + " = " + triple(1, -3, -2), NAME, NORMAL,
            prefs=ahead(f, Nn, (0, 45, -45, 90, -90)), d=8)
    plane_label(f, C, plane_eq(1, -3, -2, 0))
    f.render(
        "ornek-uc-nokta",
        "<em>P</em><sub>1</sub>(1, 1, &#8722;1), <em>P</em><sub>2</sub>(&#8722;2, &#8722;2, 2), "
        "<em>P</em><sub>3</sub>(1, &#8722;1, 2) noktalarından geçen <em>x</em> &#8722; 3<em>y</em> &#8722; "
        "2<em>z</em> = 0 düzlemi; düzlem orijinden de geçer. Normal, üçgenin ağırlık merkezinden çizildi.",
        "Coordinate axes and a patch of the plane x - 3y - 2z = 0 through the origin, the triangle "
        "P1 P2 P3 shaded, arrows from P1 to P2 and P3, and the normal n = (1, -3, -2) from the centroid")


# ===========================================================================
# 11. ornek-dogrudas: collinear P1, P2, P3 on d; two of the many planes through d
# ===========================================================================
# The camera looks partly along d, so the two planes through d fan out like an X.
DG_AZ, DG_EL, DG_W = 55, 15, 2.6
if want("ornek-dogrudas"):
    P1, P2, P3 = (1, 0, 2), (3, 1, 5), (5, 2, 8)
    U = (2, 1, 3)
    assert vsub(P2, P1) == U and vsub(P3, P1) == vscale(2, U)
    N1, D1c, N2, D2c = (1, -2, 0), -1, (3, 0, -2), 1
    for P in (P1, P2, P3):
        assert on_plane(N1, D1c, P) and on_plane(N2, D2c, P)
    AZ, EL = DG_AZ, DG_EL
    t0, t1 = -0.45, 2.45                     # the line runs a little past the patches
    L0, L1 = vadd(P1, vscale(t0, U)), vadd(P1, vscale(t1, U))
    Mid = vadd(P1, vscale(1.0, U))
    uu = vunit(U)
    lu = vnorm(U)
    SU, SW = (-1.2 * lu, 1.2 * lu), (-DG_W, DG_W)
    strips = [vunit(vcross(Nk, U)) for Nk in (N1, N2)]
    ext = [O, (3, 0, 0), (0, 3.5, 0), (0, 0, 9), L0, L1]
    for w in strips:
        ext += corners_of(Mid, uu, w, SU, SW)
    f = Fig(AZ, EL, ext, width=560, pad=70)
    Cs = [patch(f, Mid, uu, w, SU, SW, col, 0.12) for w, col in zip(strips, (THEORY, BASE))]
    f.axes(((0, 3), (0, 3.5), (0, 9)))
    f.line([L0, L1], LINE, 2.6)
    for X in (P1, P2, P3):
        f.point(X)
    side = f.sang(U) + 90
    for X, k in ((P1, 1), (P2, 2), (P3, 3)):
        f.place(X, nm("P", k), NAME, prefs=[side, side + 20, side - 20], d=8)
    f.place(L1, it("d"), NAME + 1, LINE, prefs=ahead(f, U, (0, -30, 30)))
    plane_label(f, Cs[0], nm("D", 1), NAME + 1, THEORY, ks=(1, 2))
    plane_label(f, Cs[1], nm("D", 2), NAME + 1, BASE, ks=(3, 0))
    f.render(
        "ornek-dogrudas",
        "Doğrudaş <em>P</em><sub>1</sub>, <em>P</em><sub>2</sub>, <em>P</em><sub>3</sub> noktalarından "
        "geçen <em>d</em> doğrusu ve <em>d</em>&#8217;yi içeren iki düzlem: <em>x</em> &#8722; 2<em>y</em> "
        "&#8722; 1 = 0 ve 3<em>x</em> &#8722; 2<em>z</em> + 1 = 0. Üç nokta tek bir düzlem belirtmez.",
        "Coordinate axes, the line d through the collinear points P1(1, 0, 2), P2(3, 1, 5), P3(5, 2, 8), "
        "and two translucent plane strips D1: x - 2y - 1 = 0 and D2: 3x - 2z + 1 = 0 both containing d")


# ===========================================================================
# 12-13. ornek-dort-nokta-ayni / -farkli: 3x + 5y + 4z - 13 = 0 with A, B, C and D or E
# ===========================================================================
DN = (3, 5, 4)
DA, DB, DC_, DD, DE = (1, 2, 0), (3, 0, 1), (0, 1, 2), (-1, 4, -1), (2, 3, 1)
DN_AZ, DN_EL = -20, 20       # the plane seen obliquely, so E visibly leaves it
DN_AXES = ((0, 3.6), (0, 5), (0, 3))
assert vdot(vcross(vsub(DB, DA), vsub(DC_, DA)), vsub(DD, DA)) == 0
assert vdot(vcross(vsub(DB, DA), vsub(DC_, DA)), vsub(DE, DA)) == -12
EF = vsub(DE, vscale((vdot(DN, DE) - 13) / vdot(DN, DN), DN))        # foot of E on the plane
assert abs(vdot(DN, EF) - 13) < 1e-12

for name in ("ornek-dort-nokta-ayni", "ornek-dort-nokta-farkli"):
    if not want(name):
        continue
    same = name.endswith("ayni")
    f, C = plane_axes_scene(name, DN, -13, [DA, DB, DC_, DD], DN_AZ, DN_EL, DN_AXES,
                            margin=0.6, extra=[DE])
    f.arrow(DA, DB, INPLANE, 2.6, 12.0)
    f.arrow(DA, DC_, INPLANE, 2.6, 12.0)
    if same:
        f.arrow(DA, DD, REMARK, 2.6, 12.0)
    else:
        guide(f, [DE, EF], PRACTICE, 0.8, 1.2, "4 3")
        hollow(f, EF, PRACTICE, 3.0)
        f.arrow(DA, DE, PRACTICE, 2.6, 12.0, halo=True)
    f.point(O, TEXT, 3.0)
    f.place(O, it("O"), NAME, prefs=[250, 230, 280])
    pts = [(DA, "A"), (DB, "B"), (DC_, "C")] + ([(DD, "D")] if same else [(DE, "E")])
    for X, s in pts:
        f.point(X, PRACTICE if s == "E" else TEXT)
    for X, s in pts:
        f.place(X, it(s), NAME, PRACTICE if s == "E" else TEXT,
                prefs={"A": [225, 250, 200], "B": [270, 300, 0], "C": [90, 120, 60],
                       "D": [90, 60, 120], "E": [45, 20, 70]}[s])
    # equation only: the italic D of the plane would clash with the point D
    plane_label(f, C, lin(3, 5, 4, -13), ks=(3,))
    if same:
        f.render(
            name,
            "<em>A</em>, <em>B</em>, <em>C</em>, <em>D</em> noktaları aynı düzlemdedir: "
            "<em>AB</em>, <em>AC</em> ve <em>AD</em> vektörleri düzlemin içinde kalır.",
            "Coordinate axes and a patch of the plane 3x + 5y + 4z - 13 = 0 holding the points A, B, C, D, "
            "with arrows from A to B, C and D all lying in the plane")
    else:
        f.render(
            name,
            "<em>E</em>(2, 3, 1) noktası <em>A</em>, <em>B</em>, <em>C</em>&#8217;den geçen düzlemin "
            "dışındadır: <em>AE</em> vektörü düzlemden çıkar. Kesikli çizgi <em>E</em>&#8217;den düzleme "
            "inen dikmedir.",
            "The same view: the plane 3x + 5y + 4z - 13 = 0 through A, B, C, and the point E(2, 3, 1) off "
            "the plane with a dashed perpendicular to its foot; arrows from A to B and C in the plane and "
            "from A to E leaving it")


# ===========================================================================
# 14. exr-dogru-i: d = (-2, -1, 4) + l(5, -3, 2)
# ===========================================================================
if want("exr-dogru-i"):
    P0, V = (-2, -1, 4), (5, -3, 2)
    L0, L1 = vadd(P0, vscale(-0.6, V)), vadd(P0, vscale(0.8, V))
    Vs = vscale(0.5, V)
    ext = [O, (3, 0, 0), (-5.5, 0, 0), (0, 2, 0), (0, -3.8, 0), (0, 0, 6.2), L0, L1, (-2, -1, 0)]
    f = Fig(35, 22, ext, width=560, pad=70)
    f.axes(((-5.5, 3), (-3.8, 2), (0, 6.2)))
    guide(f, [P0, (-2, -1, 0)], TEXT, 0.5)
    guide(f, [(-2, 0, 0), (-2, -1, 0), (0, -1, 0)], TEXT, 0.4)
    f.point((-2, -1, 0), TEXT, 2.4)
    line_over(f, L0, L1, LINE, 2.0, [(O, (0, 0, 6.2))])
    f.arrow(P0, vadd(P0, Vs), NORMAL, 3.4, 13.0)
    f.point(O, TEXT, 3.0)
    f.place(O, it("O"), NAME, prefs=[250, 230, 280])
    f.point(P0)
    f.place(P0, at("P", 0, -2, -1, 4), NAME, prefs=[90, 120, 60, 150])
    f.place(vadd(P0, Vs), it("v") + " = " + triple(5, -3, 2), NAME, NORMAL,
            prefs=ahead(f, V, (-90, 90, -60, 60)), d=9)
    f.place(L1, it("d"), NAME + 1, LINE, prefs=ahead(f, V, (0, 30, -30)))
    f.render(
        "exr-dogru-i",
        "<em>P</em><sub>0</sub>(&#8722;2, &#8722;1, 4) noktasından geçen ve <em>v</em> = (5, &#8722;3, 2) "
        "vektörüne paralel olan <em>d</em> doğrusu; kesikli çizgi <em>P</em><sub>0</sub>&#8217;ın "
        "<em>XY</em>-düzlemine dikmesidir.",
        "Coordinate axes, the point P0(-2, -1, 4) with a dashed drop to the XY-plane, the line d through "
        "P0 and the direction arrow v = (5, -3, 2) drawn from P0")


# ===========================================================================
# 15. exr-dogru-v: d = (-2, 3, 2) + l(0, 2, 1) inside the plane x = -2
# ===========================================================================
if want("exr-dogru-v"):
    P0, V = (-2, 3, 2), (0, 2, 1)
    L0, L1 = vadd(P0, vscale(-1.4, V)), vadd(P0, vscale(1.4, V))
    Ey, Ez = (0, 1.0, 0), (0, 0, 1.0)
    SY, SZ = (-1, 6), (-0.8, 4)            # the X-axis pierces the patch at (-2, 0, 0)
    ext = [O, (3, 0, 0), (-3.4, 0, 0), (0, 7, 0), (0, 0, 5)] + corners_of((-2, 0, 0), Ey, Ez, SY, SZ)
    f = Fig(35, 20, ext, width=560, pad=70)
    Cpl = patch(f, (-2, 0, 0), Ey, Ez, SY, SZ)
    # the YZ-plane is in front of x = -2 for this camera: paint it afterwards, very faint
    f.S.polygon([O, (0, 6, 0), (0, 6, 4), (0, 0, 4)], TEXT, 0.05)
    f.line([(0, 6, 0), (0, 6, 4), (0, 0, 4)], TEXT, 0.9, "3 3", 0.45, 0.3)
    f.axes(((-3.4, 3), (0, 7), (0, 5)))
    f.line([L0, L1], LINE, 2.2)
    f.arrow(P0, vadd(P0, V), NORMAL, 3.4, 13.0)
    tk = (-2, 0, 0)
    f.line([vadd(tk, (0, -0.12, 0)), vadd(tk, (0, 0.12, 0))], TEXT, 1.4, None, 0.9)
    f.place(tk, MINUS + "2", NAME - 1, prefs=[270, 300, 240])
    f.point(O, TEXT, 3.0)
    f.place(O, it("O"), NAME, prefs=[250, 230, 280])
    f.point(P0)
    f.place(P0, at("P", 0, -2, 3, 2), NAME, prefs=[270, 250, 290, 90])
    f.place(vadd(P0, V), it("v") + " = " + triple(0, 2, 1), NAME, NORMAL,
            prefs=ahead(f, V, (-90, 90, -60, 60)), d=9)
    f.place(L1, it("d"), NAME + 1, LINE, prefs=ahead(f, V, (0, 30, -30)))
    plane_label(f, Cpl, it("x") + " = " + MINUS + "2", ks=(3,))
    f.render(
        "exr-dogru-v",
        "<em>v</em> = (0, 2, 1) vektörüne paralel olan <em>d</em> doğrusu <em>x</em> = &#8722;2 düzleminin "
        "içinde kalır; bu düzlem <em>YZ</em>-düzlemine (soluk) paraleldir.",
        "Coordinate axes, the plane x = -2 as a translucent rectangle parallel to the faint YZ-plane, and "
        "inside it the line d through P0(-2, 3, 2) with the direction arrow v = (0, 2, 1)")


# ===========================================================================
# 16-18. exr-eksene-paralel-x / -y / -z: lines through P0(2, -1, 3) parallel to an axis
# ===========================================================================
EP_P0 = (2, -1, 3)
EP_AXES = ((-1.5, 5.5), (-3.5, 4.5), (-1.5, 5.5))
EP_CASES = {
    "x": ((1, 0, 0), (-1, 5), it("y") + " = " + MINUS + "1, " + it("z") + " = 3", "X"),
    "y": ((0, 1, 0), (-3, 4), it("x") + " = 2, " + it("z") + " = 3", "Y"),
    "z": ((0, 0, 1), (-1, 5), it("x") + " = 2, " + it("y") + " = " + MINUS + "1", "Z"),
}
for key, (E, (lo, hi), eq, AX) in EP_CASES.items():
    name = "exr-eksene-paralel-" + key
    if not want(name):
        continue
    k = "xyz".index(key)
    L0 = list(EP_P0)
    L1 = list(EP_P0)
    L0[k], L1[k] = lo, hi
    L0, L1 = tuple(L0), tuple(L1)
    ext = [O, L0, L1] + [tuple(v if i == j else 0 for i in range(3)) for j in range(3)
                         for v in EP_AXES[j]]
    f = Fig(35, 22, ext, width=560, pad=70)
    f.axes(EP_AXES)
    foot = (2, -1, 0)
    if key == "z":
        guide(f, [(2, 0, 0), foot, (0, -1, 0)], TEXT, 0.45)
    else:
        coord_box(f, EP_P0, 0.4)
    axes_segs = [tuple(tuple(EP_AXES[j][s] if i == j else 0 for i in range(3)) for s in (0, 1))
                 for j in range(3)]
    line_over(f, L0, L1, LINE, 2.2, [s for j, s in enumerate(axes_segs) if j != k])
    f.arrow(EP_P0, vadd(EP_P0, vscale(1.3, E)), NORMAL, 3.4, 12.0)
    if key == "z":
        hollow(f, foot, LINE, 3.4)
        f.place(foot, triple(2, -1, 0), NAME, prefs=[0, 330, 30, 180])
    f.point(O, TEXT, 3.0)
    f.place(O, it("O"), NAME, prefs=[250, 230, 280])
    f.point(EP_P0)
    a = f.sang(E)
    f.place(EP_P0, at("P", 0, 2, -1, 3), NAME, prefs=[a + 180 + 40, a + 180 - 40, a - 90, a + 90])
    f.place(vadd(EP_P0, vscale(1.3, E)), e_(k + 1), NAME, NORMAL, prefs=ahead(f, E, (70, -70, 45, -45)))
    f.place(L1, eq, NAME, LINE, prefs=ahead(f, E, (0, 35, -35, 60, -60)), d=8)
    f.render(
        name,
        f"<em>P</em><sub>0</sub>(2, &#8722;1, 3) noktasından geçen ve <em>{AX}</em>-eksenine paralel olan "
        f"doğru; doğrultmanı <em>e</em><sub>{k + 1}</sub>&#8217;dir."
        + (" Doğru <em>XY</em>-düzlemini (2, &#8722;1, 0) noktasında dik keser." if key == "z" else ""),
        f"Coordinate axes, the point P0(2, -1, 3) and the line through it parallel to the {AX}-axis, "
        f"with the direction arrow e{k + 1}")


# ===========================================================================
# 19. exr-iki-dogruya-dik: d through P0(3, -1, 4) perpendicular to v1 = (2,-1,3), v2 = (-1,2,0)
# ===========================================================================
if want("exr-iki-dogruya-dik"):
    P0 = (3, -1, 4)
    V1, V2 = (2, -1, 3), (-1, 2, 0)
    W = vcross(V1, V2)
    assert W == (-6, -3, 3) and vscale(-3, (2, 1, -1)) == W
    a1, a2 = vscale(0.6, V1), vscale(0.6, V2)
    Ws = vscale(0.3, W)
    Dd = (2, 1, -1)
    L0, L1 = vadd(P0, vscale(-1.25, Dd)), vadd(P0, vscale(1.25, Dd))
    PG = [P0, vadd(P0, a1), vadd(vadd(P0, a1), a2), vadd(P0, a2)]
    AZ, EL = 130, 25         # seen from the side v1 x v2 points to, so its arrow stays in front
    assert vdot(W, Camera(AZ, EL).d) > 0
    AXR = ((0, 4), (-2, 2), (0, 3))
    ext = [O, (4, 0, 0), (0, -2, 0), (0, 2, 0), (0, 0, 3), L0, L1, vadd(P0, Ws)] + PG
    f = Fig(AZ, EL, ext, width=560, pad=70)
    f.add_occluder(PG)
    f.axes(AXR)
    guide(f, [P0, (3, -1, 0)], TEXT, 0.45)
    guide(f, [(3, 0, 0), (3, -1, 0), (0, -1, 0)], TEXT, 0.35)
    f.point((3, -1, 0), TEXT, 2.4)
    f.polygon(PG, INPLANE, 0.16, stroke=INPLANE, width=1.0, s_opacity=0.5, w=0.8)
    f.oline(L0, L1, LINE, 2.2, 0.95)
    f.arrow(P0, vadd(P0, a1), C1, 3.0, 12.0)
    f.arrow(P0, vadd(P0, a2), C2, 3.0, 12.0)
    f.right_angle(P0, W, a1, 12)
    f.right_angle(P0, W, a2, 12)
    f.arrow(P0, vadd(P0, Ws), NORMAL, 3.2, 13.0, halo=True)
    f.point(O, TEXT, 3.0)
    f.place(O, it("O"), NAME, prefs=[250, 230, 280])
    f.point(P0)
    f.place(P0, at("P", 0, 3, -1, 4), NAME, prefs=[200, 160, 180, 225])
    f.place(vadd(P0, a1), nm("v", 1), NAME, C1, prefs=ahead(f, V1, (0, 40, -40)))
    f.place(vadd(P0, a2), nm("v", 2), NAME, C2, prefs=ahead(f, V2, (0, 40, -40)))
    f.place(vadd(P0, Ws), x_(nm("v", 1), nm("v", 2)) + " = " + triple(-6, -3, 3), NAME, NORMAL,
            prefs=ahead(f, W, (60, -60, 90, -90, 0)), d=9)
    far_end = L1 if f.S.depth(L1) > f.S.depth(L0) else L0
    f.place(far_end, it("d"), NAME + 1, LINE, prefs=ahead(f, vsub(far_end, P0), (0, 30, -30)))
    f.render(
        "exr-iki-dogruya-dik",
        "<em>v</em><sub>1</sub> ve <em>v</em><sub>2</sub>&#8217;nin gerdiği paralelkenar (0,6 katı) ve "
        "<em>P</em><sub>0</sub>(3, &#8722;1, 4)&#8217;ten geçip ikisine de dik olan <em>d</em> doğrusu; "
        "doğrultmanı <em>v</em><sub>1</sub> &#215; <em>v</em><sub>2</sub> = (&#8722;6, &#8722;3, 3) "
        "(0,3 katı çizildi).",
        "Coordinate axes, the point P0(3, -1, 4) with arrows v1 = (2, -1, 3) and v2 = (-1, 2, 0) and the "
        "parallelogram they span, and the line d through P0 along v1 x v2 = (-6, -3, 3) perpendicular to both")


# ===========================================================================
# 20. exr-dogruya-dik-duzlem: 7x + 2y - 3z - 46 = 0 through P0(3, 14, 1)
# ===========================================================================
if want("exr-dogruya-dik-duzlem"):
    Nn, Dc = (7, 2, -3), -46
    P0 = (3, 14, 1)
    assert on_plane(Nn, Dc, P0)
    AZ, EL = 35, 22
    a, b = vbasis(AZ, EL, Nn)
    Vs = vscale(0.4, Nn)
    s1, s2 = (-4.2, 4.2), (-2.8, 2.8)
    L0, L1 = vadd(P0, vscale(-0.6, Nn)), vadd(P0, vscale(0.75, Nn))
    ext = [O, (6, 0, 0), (0, 16.5, 0), (0, 0, 4.5), L0, L1, (3, 14, 0)] + corners_of(P0, a, b, s1, s2)
    f = Fig(AZ, EL, ext, width=580, pad=70)
    C = patch(f, P0, a, b, s1, s2)
    f.axes(((0, 6), (0, 16.5), (0, 4.5)))
    guide(f, [P0, (3, 14, 0)], TEXT, 0.45)
    guide(f, [(3, 0, 0), (3, 14, 0), (0, 14, 0)], TEXT, 0.35)
    f.point((3, 14, 0), TEXT, 2.4)
    f.oline(L0, L1, LINE, LINE_W, 0.95)
    f.right_angle(P0, Nn, perp_in_plane(f, Nn), 15)
    f.arrow(P0, vadd(P0, Vs), NORMAL, 3.0, 13.0, halo=True)
    f.point(O, TEXT, 3.0)
    f.place(O, it("O"), NAME, prefs=[250, 230, 280])
    f.point(P0)
    f.place(P0, at("P", 0, 3, 14, 1), NAME, prefs=[135, 150, 120, 160])
    f.place(vadd(P0, Vs), it("n") + " = " + it("v") + " = " + triple(7, 2, -3), NAME, NORMAL,
            prefs=ahead(f, Nn, (90, -90, 60, -60)), d=9)
    f.place(L1, it("d"), NAME + 1, LINE, prefs=ahead(f, Nn, (0, 30, -30)))
    plane_label(f, C, lin(7, 2, -3, -46))
    f.render(
        "exr-dogruya-dik-duzlem",
        "<em>P</em><sub>0</sub>(3, 14, 1) noktasından geçen ve doğrultmanı (7, 2, &#8722;3) olan "
        "<em>d</em> doğrusuna dik düzlem: 7<em>x</em> + 2<em>y</em> &#8722; 3<em>z</em> &#8722; 46 = 0. "
        "Doğrunun düzlemin arkasında kalan kısmı kesiklidir.",
        "Coordinate axes with a long Y-axis, a patch of the plane 7x + 2y - 3z - 46 = 0 around "
        "P0(3, 14, 1), the line d through P0 along (7, 2, -3) meeting it at a right angle, and n = v")


# ===========================================================================
# 21. exr-uc-nokta-iki-yol: x - 3y - 2z = 0 through P1(1,1,-1), P2(-3,-3,3), P3(1,-1,2)
# ===========================================================================
if want("exr-uc-nokta-iki-yol"):
    P1, P2, P3, Q = (1, 1, -1), (-3, -3, 3), (1, -1, 2), (-2, -2, 2)
    Nn = (1, -3, -2)
    assert vcross(vsub(P2, P1), vsub(P3, P1)) == vscale(-4, Nn)
    assert vcross(vsub(Q, P1), vsub(P2, P1)) == (0, 0, 0)          # Q lies on P1P2
    f, C = plane_axes_scene("exr-uc-nokta-iki-yol", Nn, 0, [P1, P2, P3], UC_AZ, UC_EL,
                            ((-4, 4), (-4, 4), (-2.5, 4)), margin=0.6)
    triangle(f, [P1, P2, P3])
    f.line([P1, P2], INPLANE, 2.6)
    f.arrow(P1, P3, INPLANE, 2.6, 12.0)
    hollow(f, Q, TEXT, 3.6)
    f.point(O, TEXT, 3.0)
    f.place(O, it("O"), NAME, prefs=[315, 290, 250, 200])
    for X in (P1, P2, P3):
        f.point(X)
    f.place(P1, nm("P", 1), NAME, prefs=[270, 300, 240, 0])
    f.place(P2, nm("P", 2), NAME, prefs=[180, 150, 210, 90])
    f.place(P3, nm("P", 3), NAME, prefs=[90, 60, 120, 0])
    side = f.sang(vsub(P2, P1)) - 90
    f.place(Q, triple(-2, -2, 2), NAME - 1, prefs=[side, side + 25, side - 25, side + 180])
    plane_label(f, C, plane_eq(1, -3, -2, 0), ks=(3, 2))
    f.render(
        "exr-uc-nokta-iki-yol",
        "<em>P</em><sub>1</sub>(1, 1, &#8722;1), <em>P</em><sub>2</sub>(&#8722;3, &#8722;3, 3), "
        "<em>P</em><sub>3</sub>(1, &#8722;1, 2) noktalarından geçen <em>x</em> &#8722; 3<em>y</em> &#8722; "
        "2<em>z</em> = 0 düzlemi. Önceki örneğin (&#8722;2, &#8722;2, 2) noktası (boş daire) "
        "<em>P</em><sub>1</sub><em>P</em><sub>2</sub> doğrusu üzerindedir.",
        "Coordinate axes and a patch of the plane x - 3y - 2z = 0 with the shaded triangle P1 P2 P3, the "
        "segment P1 P2 passing through the hollow point (-2, -2, 2), and an arrow from P1 to P3")


# ===========================================================================
# 22. exr-uc-nokta-determinant: 6x - y + 5z - 6 = 0 through P1(2,1,-1), P2(-2,2,4), P3(3,2,-2)
# ===========================================================================
if want("exr-uc-nokta-determinant"):
    P1, P2, P3 = (2, 1, -1), (-2, 2, 4), (3, 2, -2)
    Nn = (6, -1, 5)
    assert vcross(vsub(P2, P1), vsub(P3, P1)) == vscale(-1, Nn)
    G = (1, 5 / 3, 1 / 3)
    assert close(vscale(1 / 3, vadd(vadd(P1, P2), P3)), G)
    Nv = vscale(0.3, Nn)
    # az 80, el 40: the long side P2P3 runs diagonally, so the scene is not tall
    f, C = plane_axes_scene("exr-uc-nokta-determinant", Nn, -6, [P1, P2, P3], 80, 40,
                            ((-2.5, 4), (0, 3.5), (-2.5, 5)), margin=0.6, extra=[vadd(G, Nv)])
    triangle(f, [P1, P2, P3])
    f.arrow(P1, P2, INPLANE, 2.6, 12.0)
    f.arrow(P1, P3, INPLANE, 2.6, 12.0)
    f.right_angle(G, Nv, perp_in_plane(f, Nn), 13)
    f.arrow(G, vadd(G, Nv), NORMAL, 3.0, 13.0, halo=True)
    f.point(G, NORMAL, 2.6)
    f.point(O, TEXT, 3.0)
    f.place(O, it("O"), NAME, prefs=[250, 230, 280])
    for X in (P1, P2, P3):
        f.point(X)
    f.place(P1, nm("P", 1), NAME, prefs=[180, 200, 160, 270])
    f.place(P2, nm("P", 2), NAME, prefs=[90, 60, 120, 180])
    f.place(P3, nm("P", 3), NAME, prefs=[0, 330, 30, 270])
    f.place(vadd(G, Nv), it("n") + " = " + triple(6, -1, 5), NAME, NORMAL,
            prefs=ahead(f, Nn, (0, 45, -45, 90, -90)), d=8)
    plane_label(f, C, plane_eq(6, -1, 5, -6))
    f.render(
        "exr-uc-nokta-determinant",
        "<em>P</em><sub>1</sub>(2, 1, &#8722;1), <em>P</em><sub>2</sub>(&#8722;2, 2, 4), "
        "<em>P</em><sub>3</sub>(3, 2, &#8722;2) noktalarından geçen 6<em>x</em> &#8722; <em>y</em> + "
        "5<em>z</em> &#8722; 6 = 0 düzlemi ve normali (0,3 katı, üçgenin ağırlık merkezinden).",
        "Coordinate axes and a patch of the plane 6x - y + 5z - 6 = 0 with the shaded triangle P1 P2 P3, "
        "arrows from P1 to P2 and P3, and the normal n = (6, -1, 5) from the centroid")


# ---------------------------------------------------------------------------
for name, content in OUT.items():
    path = OUT_DIR / f"analytic-udz-{name}.md"
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(content)
    print("wrote", path.name)
