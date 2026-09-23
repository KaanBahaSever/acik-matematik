# -*- coding: utf-8 -*-
"""Figures for dersler/analitik-geometri/uzayda-dogru-denklemleri.qmd (chapter key: udd).

All drawings are three-dimensional and go through scripts/svg_plot3.py (an
orthographic Camera on an equal-aspect svg_plot.Plot panel). A line is drawn
in one color and its direction vector in another, shifted a few pixels to the
side of the line on the page so that the two never hide each other. Planes are
translucent parallelogram patches that also act as occluders, so the parts of
lines and axes behind them turn thin and dashed. The figures go INSIDE the box
they explain (example, solution, proof), never inside a definition box.

Labels are placed after the projection, in page pixels: `Canvas.place` tries
a ring of candidate positions around the anchor and keeps the cheapest one,
i.e. the one that touches no registered line, point or earlier label.

Usage:   python scripts/analytic_figures/udd.py
         python scripts/center_figures.py "analytic-udd-*.md" --keep-width
Output:  scripts/_figures/analytic-udd-<name>.md
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

TALL_SCENES = {"koordinat-duzlemleri", "iki-nokta-ornegi-i"}
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
        css = "ders-grafik" if name in TALL_SCENES else WIDE
        OUT[name] = figure(round(self.W), round(self.H), [self.p], caption, css, aria)



# ---------------------------------------------------------------------------
# chapter helpers
# ---------------------------------------------------------------------------
LAM = "λ"
P0_, P1_ = it("P") + sub("0"), it("P") + sub("1")
D_ = it("d")


def pname(base, k=None, size=NAME):
    return it(base) + (sub(str(k), size) if k is not None else "")


def at(P0, v, lam):
    return vadd(P0, vscale(lam, v))


def shift(f, v, px, side=1):
    """Space offset that moves a point px pixels on the page, perpendicular to the page
    direction of v (side=+1: to the left of v, side=-1: to the right)."""
    a = math.radians(f.sang(v) + 90 * side)
    s = f.u(px)
    return vadd(vscale(s * math.cos(a), f.cam.r), vscale(s * math.sin(a), f.cam.u))


def dline(f, P0, v, l0, l1, color=THEORY, width=2.1, occl=False):
    A, B = at(P0, v, l0), at(P0, v, l1)
    if occl:
        f.oline(A, B, color, width, 1.0)
    else:
        f.line([A, B], color, width)
    return A, B


def line_name(f, B, v, s, color, side=1, size=NAME + 1):
    a = f.sang(v)
    f.place(B, s, size, color, prefs=[a + 90 * side, a + 60 * side, a, a - 90 * side], d=8)


def beside(f, A, B, color=PRACTICE, px=9, side=1, width=3.0, head=13.0):
    """Vector from A to B drawn next to the line AB lies on, px pixels to one side."""
    s = shift(f, vsub(B, A), px, side)
    A2, B2 = vadd(A, s), vadd(B, s)
    f.arrow(A2, B2, color, width, head, halo=True)
    return A2, B2


def mid(A, B):
    return vscale(0.5, vadd(A, B))


def vlabel(f, A, B, s, color, side=1, t=0.5, size=NAME, d=7.0):
    """Name of the arrow AB beside the point A + t(B - A), on the given side."""
    a = f.sang(vsub(B, A))
    P = vadd(A, vscale(t, vsub(B, A)))
    f.place(P, s, size, color, prefs=[a + 90 * side, a + 70 * side, a + 110 * side, a - 90 * side], d=d)


def over_label(f, anchor, pieces, color, prefs, prefix="", prefix_w=0.0, size=NAME, d=7.0):
    """A name with an arrow over it, e.g. the vector P0P1: pieces = [("P", "0"), ("P", "1")].
    `prefix` (already marked up, estimated width prefix_w) stands before it without an arrow."""
    s = prefix + "&#8202;".join(pname(b, k, size) for b, k in pieces)
    wl = sum(lay_width(b, size) + (lay_width(str(k), 0.74 * size) if k is not None else 0)
             for b, k in pieces) + 0.1 * size * (len(pieces) - 1)
    cx, cy = f.place(anchor, s, size, color, prefs=prefs, d=d, tall=5)
    f.texts.pop()
    total = prefix_w + wl
    x0 = cx - total / 2
    base = cy + 0.30 * size
    f.texts.append(f'<text x="{x0:.1f}" y="{base:.1f}" fill="{color}" font-size="{size}" '
                   f'stroke="{BG}" stroke-width="3.6" stroke-linejoin="round" '
                   f'paint-order="stroke">{s}</text>')
    f.over_arrow(x0 + prefix_w + wl / 2 + 0.06 * size, base - 0.92 * size, wl - 1, color)


def drop(f, P, z0=0.0, opacity=0.5):
    x, y, _ = P
    f.line([P, (x, y, z0)], TEXT, 1.0, "4 3", opacity, w=0.4)


def ahead(f, vec, spread=(0, 30, -30, 60, -60, 90, -90)):
    """Label angles around the page direction of vec: first straight past the tip."""
    a = f.sang(vec)
    return [a + s for s in spread]


def small_dot(f, P, color=TEXT, r=2.4):
    f.point(P, color, r)


# ===========================================================================
# 1. vektorel-denklem: P0 = (3, 1, 2), v = (-1, 2, 1), P = P0 + 2v = (1, 5, 4)
# ===========================================================================
P0, V = (3, 1, 2), (-1, 2, 1)
P = at(P0, V, 2)
assert P == (1, 5, 4) and at(P0, V, 1) == (2, 3, 3)
L0, L1 = -0.4, 2.4
A, B = at(P0, V, L0), at(P0, V, L1)
assert all(0 <= c <= 6 for Q in (A, B) for c in Q)
ext = [O, (6, 0, 0), (0, 6, 0), (0, 0, 6), A, B]
f = Fig(30, 20, ext, width=560, pad=70)
f.axes(((0, 6), (0, 6), (0, 6)))
f.line([A, B], THEORY, 2.1)
f.arrow(O, P0, BASE, 2.2, 12.0)
f.arrow(O, P, BASE, 2.2, 12.0)
La, Lb = beside(f, P0, P, REMARK, 27, 1, 2.6)
Va, Vb = beside(f, P0, at(P0, V, 1), PRACTICE, 10, 1, 3.2)
f.point(O, TEXT, 3.4)
f.point(P0)
f.point(P)
f.place(O, it("O"), NAME, prefs=[225, 200, 250])
f.place(P0, P0_, NAME, prefs=[-30, 0, -60, 300])
f.place(P, it("P"), NAME, prefs=[-30, -60, 0, 300])
vlabel(f, O, P0, it("u") + sub("0"), BASE, side=-1, t=0.55)
vlabel(f, O, P, it("u"), BASE, side=-1, t=0.55)
f.place(Vb, it("v"), NAME, PRACTICE, prefs=[f.sang(V) + s_ for s_ in (0, 15, -15)], d=6)
vlabel(f, La, Lb, LAM + it("v"), REMARK, side=1, t=0.6, d=6)
line_name(f, B, V, D_, THEORY, side=1)
f.render(
    "vektorel-denklem",
    "<em>d</em> doğrusu <em>P</em><sub>0</sub>&#8217;dan geçer ve doğrultmanı <em>v</em>&#8217;dir. "
    "<em>P</em>&#8217;ye <em>O</em>&#8217;dan doğrudan (<em>u</em>) ya da önce <em>P</em><sub>0</sub>&#8217;a "
    "(<em>u</em><sub>0</sub>), sonra doğru boyunca &#955;<em>v</em> kadar giderek varılır: "
    "<em>u</em> = <em>u</em><sub>0</sub> + &#955;<em>v</em>.",
    "Line d through P0 with direction vector v; position vectors u0 of P0 and u of a point P on d; "
    "the vector lambda v from P0 to P drawn beside the line")


# ===========================================================================
# 2. nokta-vektor-ornegi: P0 = (4, -3, 1), v = (7, 2, -3)
# ===========================================================================
P0, V = (4, -3, 1), (7, 2, -3)
assert at(P0, V, 1) == (11, -1, -2)
L0, L1 = -0.4, 1.3
A, B = at(P0, V, L0), at(P0, V, L1)
ext = [O, (14, 0, 0), (-1, 0, 0), (0, -5, 0), (0, 1.5, 0), (0, 0, 4), (0, 0, -4), A, B]
f = Fig(-70, 22, ext, width=580, pad=70)
f.axes(((-1, 14), (-5, 1.5), (-4, 4)))
f.line([(4, 0, 0), (4, -3, 0), (0, -3, 0)], TEXT, 1.0, "4 3", 0.5, w=0.4)
drop(f, P0)
f.line([A, B], THEORY, 2.1)
Va, Vb = beside(f, P0, at(P0, V, 1), PRACTICE, 9, 1, 3.2)
small_dot(f, (4, -3, 0))
f.point(O, TEXT, 3.4)
f.point(P0)
f.place(O, it("O"), NAME, prefs=[250, 270, 225])
f.place(P0, P0_, NAME, prefs=[f.sang(V) - 90, f.sang(V) - 60, f.sang(V) - 120])
vlabel(f, Va, Vb, it("v"), PRACTICE, side=1, t=0.55, d=6)
line_name(f, B, V, D_, THEORY, side=1)
f.render(
    "nokta-vektor-ornegi",
    "<em>P</em><sub>0</sub> = (4, &#8722;3, 1) noktasından geçen ve <em>v</em> = (7, 2, &#8722;3) "
    "vektörüne paralel olan <em>d</em> doğrusu. Kesikli çizgiler <em>P</em><sub>0</sub>&#8217;ın "
    "<em>XY</em> düzlemindeki izdüşümünü gösterir.",
    "Line d through P0 = (4, -3, 1) with direction vector v = (7, 2, -3) drawn beside it, and the "
    "dashed projection of P0 to the XY plane")


# ===========================================================================
# 3. nokta-uzerinde: R = (-3, -5, 5) is one unit above S = (-3, -5, 4) on d
# ===========================================================================
P0, V = (4, -3, 1), (7, 2, -3)
S, R = at(P0, V, -1), (-3, -5, 5)
assert S == (-3, -5, 4)
L0, L1 = -1.25, 0.25
A, B = at(P0, V, L0), at(P0, V, L1)
assert -5 <= A[0] and B[0] <= 6 and -7 <= A[1] and A[2] <= 6 and B[2] >= 0
ext = [O, (6, 0, 0), (-5, 0, 0), (0, -7, 0), (0, 1, 0), (0, 0, 6), A, B, R]
f = Fig(40, 18, ext, width=560, pad=70)
f.axes(((-5, 6), (-7, 1), (0, 6)))
drop(f, S)
f.line([(-3, 0, 0), (-3, -5, 0), (0, -5, 0)], TEXT, 1.0, "4 3", 0.45, w=0.4)
small_dot(f, (-3, -5, 0))
f.line([A, B], THEORY, 2.1)
f.line([S, R], TEXT, 1.3, "3 3", 0.9, w=0.8)
f.point(O, TEXT, 3.4)
f.point(P0)
f.point(S)
f.S.hollow(R, TEXT, 4.2, 1.8)
f.dots.append((*f.px(R), 4.2))
f.place(O, it("O"), NAME, prefs=[315, 290, 340])
f.place(P0, P0_, NAME, prefs=[f.sang(V) + 90, 90, 60])
f.place(R, it("R"), NAME, prefs=[45, 30, 60, 90])
f.place(S, it("S"), NAME, prefs=[225, 200, 250, 270])
line_name(f, B, V, D_, THEORY, side=1)
f.render(
    "nokta-uzerinde",
    "<em>d</em> üzerindeki <em>S</em> = (&#8722;3, &#8722;5, 4) noktası ilk iki koordinatı "
    "<em>R</em> = (&#8722;3, &#8722;5, 5) ile aynı olan tek noktadır; <em>R</em> onun 1 birim "
    "üstündedir, yani <em>d</em> üzerinde değildir.",
    "Line d with points P0 and S = (-3, -5, 4) on it, and the hollow point R = (-3, -5, 5) one unit "
    "above S, off the line")


# ===========================================================================
# 4. koordinat-duzlemleri: d = (2, 1, 4) + t(1, 1, -2) meets the planes at A, B, C
# ===========================================================================
P0, V = (2, 1, 4), (1, 1, -2)
Aq, Bq, Cq = at(P0, V, 2), at(P0, V, -1), at(P0, V, -2)
assert Aq == (4, 3, 0) and Bq == (1, 0, 6) and Cq == (0, -1, 8)
L0, L1 = -2.12, 2.15
A, B = at(P0, V, L0), at(P0, V, L1)
ext = [O, (5, 0, 0), (-1, 0, 0), (0, 4, 0), (0, -2, 0), (0, 0, 9), (0, 0, -0.6), A, B]
f = Fig(55, 14, ext, width=520, pad=70)
XY = [(0, 0, 0), (5, 0, 0), (5, 4, 0), (0, 4, 0)]
XZ = [(0, 0, 0), (5, 0, 0), (5, 0, 8.6), (0, 0, 8.6)]
YZ = [(0, -2, 0), (0, 4, 0), (0, 4, 8.6), (0, -2, 8.6)]
for pl in (XY, XZ, YZ):
    f.add_occluder(pl)
f.polygon(YZ, TEXT, 0.05, stroke=TEXT, width=0.7, s_opacity=0.22, w=0.2)
f.polygon(XZ, TEXT, 0.05, stroke=TEXT, width=0.7, s_opacity=0.22, w=0.2)
f.polygon(XY, TEXT, 0.06, stroke=TEXT, width=0.7, s_opacity=0.22, w=0.2)
f.axes(((-1, 5), (-2, 4), (-1, 9)))
f.oline(A, B, THEORY, 2.1, 1.0)
f.point(O, TEXT, 3.4)
f.point(P0)
for Q in (Aq, Bq, Cq):
    f.point(Q, PRACTICE, 4.2)
f.place(O, it("O"), NAME, prefs=[225, 250, 200])
side = f.sang(V) - 90
for Q, s, col in ((Cq, it("C"), PRACTICE), (Bq, it("B"), PRACTICE), (P0, P0_, TEXT),
                  (Aq, it("A"), PRACTICE)):
    f.place(Q, s, NAME, col, prefs=[side, side + 25, side - 25], d=8)
line_name(f, B, V, D_, THEORY, side=1)
f.render(
    "koordinat-duzlemleri",
    "<em>d</em> doğrusu <em>YZ</em> düzlemini <em>C</em>&#8217;de, <em>XZ</em> düzlemini "
    "<em>B</em>&#8217;de, <em>XY</em> düzlemini <em>A</em>&#8217;da keser; parametre değerleri "
    "sırasıyla &#8722;2, &#8722;1, 2&#8217;dir, <em>P</em><sub>0</sub> ise &#955; = 0 noktasıdır.",
    "Line d through P0 = (2, 1, 4) crossing the three faint coordinate planes at C = (0, -1, 8), "
    "B = (1, 0, 6) and A = (4, 3, 0); parts behind a plane are dashed")


# ===========================================================================
# 5. iki-nokta: P0 = (4, 1, 1), P1 = (3, 3, 2), P = P0 + 2.2 (P1 - P0)
# ===========================================================================
P0, P1 = (4, 1, 3), (3, 3, 4)
V = vsub(P1, P0)
P = at(P0, V, 2.2)
assert V == (-1, 2, 1) and close(P, (1.8, 5.4, 5.2))
L0, L1 = -0.4, 2.4
A, B = at(P0, V, L0), at(P0, V, L1)
assert all(0 <= c <= 6 for Q in (A, B) for c in Q)
ext = [O, (6, 0, 0), (0, 6, 0), (0, 0, 6), A, B]
f = Fig(30, 20, ext, width=560, pad=70)
f.axes(((0, 6), (0, 6), (0, 6)))
f.line([A, B], THEORY, 2.1)
f.arrow(O, P0, BASE, 2.2, 12.0)
f.arrow(O, P, BASE, 2.2, 12.0)
La, Lb = beside(f, P0, P, REMARK, 10, -1, 2.6)
Va, Vb = beside(f, P0, P1, PRACTICE, 10, 1, 3.2)
f.point(O, TEXT, 3.4)
for Q in (P0, P1, P):
    f.point(Q)
f.place(O, it("O"), NAME, prefs=[225, 200, 250])
f.place(P0, P0_, NAME, prefs=[-30, 0, -60, 300])
f.place(P1, P1_, NAME, prefs=[f.sang(V) - 90, f.sang(V) - 60, 0])
f.place(P, it("P"), NAME, prefs=[90, 60, 120, 30])
vlabel(f, O, P0, it("u") + sub("0"), BASE, side=-1, t=0.55)
vlabel(f, O, P, it("u"), BASE, side=1, t=0.55)
a = f.sang(V)
over_label(f, mid(Va, Vb), [("P", 0), ("P", 1)], PRACTICE, prefs=[a + 90, a + 70, a + 110], d=6)
over_label(f, vadd(La, vscale(0.35, vsub(Lb, La))), [("P", 0), ("P", 1)], REMARK,
           prefs=[a - 90, a - 70, a - 110], prefix=LAM + " · ", prefix_w=lay_width("λ · ", NAME), d=6)
line_name(f, B, V, D_, THEORY, side=1)
f.render(
    "iki-nokta",
    "<em>P</em><sub>0</sub> ile <em>P</em><sub>1</sub>&#8217;den geçen <em>d</em> doğrusunun "
    "doğrultmanı olarak <em>P</em><sub>0</sub><em>P</em><sub>1</sub> vektörü alınır; <em>d</em>&#8217;nin "
    "her <em>P</em> noktası için <em>u</em> = <em>u</em><sub>0</sub> + &#955; "
    "<em>P</em><sub>0</sub><em>P</em><sub>1</sub> olur.",
    "Line d through P0 = (4, 1, 3) and P1 = (3, 3, 4); the vector P0P1 beside the line, the vector "
    "lambda P0P1 from P0 to a point P, and the position vectors u0 and u")


# ===========================================================================
# 6. iki-nokta-ornegi-i: P0 = (2, -3, 4), P1 = (5, 2, -1)
# ===========================================================================
P0, P1 = (2, -3, 4), (5, 2, -1)
V = vsub(P1, P0)
assert V == (3, 5, -5)
L0, L1 = -0.3, 1.3
A, B = at(P0, V, L0), at(P0, V, L1)
ext = [O, (7, 0, 0), (0, -5, 0), (0, 4, 0), (0, 0, 6), (0, 0, -3), A, B]
f = Fig(15, 20, ext, width=560, pad=70)
f.axes(((0, 7), (-5, 4), (-3, 6)))
drop(f, P0)
drop(f, P1)
f.line([(2, 0, 0), (2, -3, 0), (0, -3, 0)], TEXT, 1.0, "4 3", 0.4, w=0.3)
f.line([(5, 0, 0), (5, 2, 0), (0, 2, 0)], TEXT, 1.0, "4 3", 0.4, w=0.3)
small_dot(f, (2, -3, 0))
small_dot(f, (5, 2, 0))
f.line([A, B], THEORY, 2.1)
Va, Vb = beside(f, P0, P1, PRACTICE, 9, 1, 3.2)
f.point(O, TEXT, 3.4)
f.point(P0)
f.point(P1)
f.place(O, it("O"), NAME, prefs=[250, 225, 290])
a = f.sang(V)
f.place(P0, P0_, NAME, prefs=[a - 90, a + 180, a - 135])
f.place(P1, P1_, NAME, prefs=[a - 90, a - 60, a - 120])
vlabel(f, Va, Vb, it("v"), PRACTICE, side=1, t=0.4, d=6)
line_name(f, B, V, D_, THEORY, side=1)
f.render(
    "iki-nokta-ornegi-i",
    "<em>P</em><sub>0</sub> = (2, &#8722;3, 4) ile <em>P</em><sub>1</sub> = (5, 2, &#8722;1) "
    "noktalarından geçen doğru ve doğrultmanı <em>v</em> = (3, 5, &#8722;5). Kesikli çizgiler "
    "noktaları <em>XY</em> düzlemine bağlar.",
    "Line d through P0 = (2, -3, 4) and P1 = (5, 2, -1) with the vector v = P0P1 beside it and "
    "dashed verticals to the XY plane")


# ===========================================================================
# 7. iki-nokta-ornegi-ii: P0 = (1, 2, 3), P1 = (-2, 3, 3); d lies in z = 3
# ===========================================================================
P0, P1 = (1, 2, 3), (-2, 3, 3)
V = vsub(P1, P0)
assert V == (-3, 1, 0)
L0, L1 = -0.6, 1.6
A, B = at(P0, V, L0), at(P0, V, L1)
PL = [(-4, 0, 3), (3, 0, 3), (3, 5, 3), (-4, 5, 3)]
ext = [O, (3, 0, 0), (-4, 0, 0), (0, 5, 0), (0, 0, 4)] + PL
f = Fig(35, 22, ext, width=560, pad=70)
f.add_occluder(PL)
f.axes(((-4, 3), (0, 5), (0, 4)))
for Q in (P0, P1):
    drop(f, Q)
    small_dot(f, (Q[0], Q[1], 0))
f.polygon(PL, THEORY, 0.10, stroke=THEORY, width=0.9, s_opacity=0.45, w=0.3)
f.line([A, B], THEORY, 2.1)
Va, Vb = beside(f, P0, P1, PRACTICE, 9, 1, 3.2)
f.point(O, TEXT, 3.4)
f.point(P0)
f.point(P1)
f.place(O, it("O"), NAME, prefs=[250, 225, 290])
a = f.sang(V)
f.place(P0, P0_, NAME, prefs=[a - 90, a - 60, a + 180])
f.place(P1, P1_, NAME, prefs=[a - 90, a - 120, a - 60])
vlabel(f, Va, Vb, it("v"), PRACTICE, side=1, t=0.5, d=6)
line_name(f, B, V, D_, THEORY, side=1)
f.place((3, 5, 3), it("z") + " = 3", DESC + 1, THEORY, prefs=[0, 330, 30, 270])
f.render(
    "iki-nokta-ornegi-ii",
    "Doğrultmanı <em>v</em> = (&#8722;3, 1, 0) olan doğru, kotu 3 olan noktalardan oluşan "
    "<em>z</em> = 3 düzleminde yatar; <em>P</em><sub>0</sub> ve <em>P</em><sub>1</sub>&#8217;den "
    "<em>XY</em> düzlemine inen kesikli çizgilerin ikisi de 3 birimdir.",
    "The plane z = 3 as a translucent patch with the line through P0 = (1, 2, 3) and P1 = (-2, 3, 3) "
    "lying in it, the vector v = (-3, 1, 0), and dashed verticals of length 3 to the XY plane")


# ===========================================================================
# 8. paralel-dogrular: d1 = (2, 0, 1) + t(-1, 2, 1), d2 = (4, 1, 0) + t(-1, 2, 1)
# ===========================================================================
Q1, Q2, V = (2, 0, 1), (4, 1, 0), (-1, 2, 1)
V2a, V2b = at(Q2, V, 1.5), Q2
assert close(vsub(V2b, V2a), vscale(-1.5, V)) and close(V2a, (2.5, 4, 1.5))
A1, B1 = at(Q1, V, 0), at(Q1, V, 2)
A2, B2 = at(Q2, V, 0), at(Q2, V, 2.3)
assert all(0 <= c for Q in (A1, B1, A2, B2) for c in Q) and B2[1] <= 6
ext = [O, (5, 0, 0), (0, 6, 0), (0, 0, 4), A1, B1, A2, B2]
f = Fig(30, 22, ext, width=560, pad=70)
f.axes(((0, 5), (0, 6), (0, 4)))
f.line([A1, B1], THEORY, 2.1)
f.line([A2, B2], BASE, 2.1)
V1a, V1b = beside(f, Q1, at(Q1, V, 1), PRACTICE, 9, 1, 3.2)
W1a, W1b = beside(f, V2a, V2b, PRACTICE, 9, -1, 3.2)
f.point(O, TEXT, 3.4)
f.place(O, it("O"), NAME, prefs=[225, 200, 250])
vlabel(f, V1a, V1b, it("v") + sub("1"), PRACTICE, side=1, t=0.5, d=6)
vlabel(f, W1a, W1b, it("v") + sub("2"), PRACTICE, side=1, t=0.5, d=6)
line_name(f, B1, V, it("d") + sub("1"), THEORY, side=1)
line_name(f, B2, V, it("d") + sub("2"), BASE, side=-1)
f.render(
    "paralel-dogrular",
    "Doğrultmanları paralel olan <em>d</em><sub>1</sub> ve <em>d</em><sub>2</sub> doğruları. "
    "Burada <em>v</em><sub>2</sub> = &#8722;1,5 <em>v</em><sub>1</sub> olduğundan iki doğrultman "
    "zıt yönlüdür; doğrular yine paraleldir.",
    "Two parallel lines d1 and d2 with direction vectors v1 and v2 = -1.5 v1 drawn beside them, "
    "pointing in opposite directions")


# ===========================================================================
# 9. paralel-dogru-ornegi: d1 through P0 = (1, 3, 4), P1 = (-2, 2, 3); d through P = (-2, 4, 3)
# ===========================================================================
P0, P1, P = (1, 3, 4), (-2, 2, 3), (-2, 4, 3)
V = vsub(P1, P0)
assert V == (-3, -1, -1) and at(P, V, 1) == (-5, 3, 2)
A1, B1 = at(P0, V, -0.4), at(P0, V, 1.4)
A2, B2 = at(P, V, -0.3), at(P, V, 1.15)
for Q in (A1, B1, A2, B2):
    assert -5.5 <= Q[0] <= 3 and 0 <= Q[1] <= 5 and 0 <= Q[2] <= 5
ext = [O, (3, 0, 0), (-5.5, 0, 0), (0, 5, 0), (0, 0, 5), A1, B1, A2, B2]
f = Fig(-70, 20, ext, width=560, pad=70)
f.axes(((-5.5, 3), (0, 5), (0, 5)))
f.line([A1, B1], THEORY, 2.1)
f.line([A2, B2], BASE, 2.1)
Va, Vb = beside(f, P0, P1, PRACTICE, 9, 1, 3.2)
Wa, Wb = beside(f, P, at(P, V, 1), PRACTICE, 9, -1, 3.2)
f.point(O, TEXT, 3.4)
for Q in (P0, P1, P):
    f.point(Q)
f.place(O, it("O"), NAME, prefs=[315, 290, 340])
a = f.sang(V)
f.place(P0, P0_, NAME, prefs=[a + 180, a + 180 - 30, a + 180 + 30])
f.place(P1, P1_, NAME, prefs=[270, 250, 290, a - 90])
f.place(P, it("P"), NAME, prefs=[90, 70, 110, a + 90])
vlabel(f, Va, Vb, it("v"), PRACTICE, side=1, t=0.5, d=6)
vlabel(f, Wa, Wb, it("v"), PRACTICE, side=-1, t=0.5, d=6)
line_name(f, B1, V, it("d") + sub("1"), THEORY, side=-1)
line_name(f, B2, V, D_, BASE, side=1)
f.render(
    "paralel-dogru-ornegi",
    "<em>P</em><sub>0</sub> ile <em>P</em><sub>1</sub>&#8217;den geçen <em>d</em><sub>1</sub> ve "
    "<em>P</em>&#8217;den geçen, aynı <em>v</em> = (&#8722;3, &#8722;1, &#8722;1) doğrultmanlı "
    "<em>d</em> doğrusu. <em>P</em>, <em>d</em><sub>1</sub> üzerinde olmadığından iki doğru çakışmaz.",
    "Two parallel lines: d1 through P0 = (1, 3, 4) and P1 = (-2, 2, 3), and d through P = (-2, 4, 3), "
    "each with the direction vector v = (-3, -1, -1) beside it")


# ===========================================================================
# 10. dik-dogrular: d1 = (t, 2, 0), d2 = (2, t, 0), d3 = (0, t, 3)
# ===========================================================================
K = (2, 2, 0)
T0, T1 = -0.5, 4.5
ext = [O, (5, 0, 0), (-1, 0, 0), (0, 5, 0), (0, -1, 0), (0, 0, 5)]
f = Fig(35, 22, ext, width=560, pad=70)
f.axes(((-1, 5), (-1, 5), (0, 5)))
f.line([(0, 2, 0), (0, 2, 3)], TEXT, 1.0, "4 3", 0.6, w=0.4)
f.line([(T0, 2, 0), (T1, 2, 0)], THEORY, 2.1)
f.line([(2, T0, 0), (2, T1, 0)], BASE, 2.1)
f.line([(0, T0, 3), (0, T1, 3)], REMARK, 2.1)
f.right_angle(K, (1, 0, 0), (0, 1, 0), 14, TEXT)
B1 = beside(f, (3, 2, 0), (4, 2, 0), PRACTICE, 9, 1, 3.0)
B2 = beside(f, (2, 3, 0), (2, 4, 0), PRACTICE, 9, 1, 3.0)
B3 = beside(f, (0, 3, 3), (0, 4, 3), PRACTICE, 9, 1, 3.0)
f.point(O, TEXT, 3.4)
f.point(K)
small_dot(f, (0, 2, 0))
small_dot(f, (0, 2, 3))
f.place(O, it("O"), NAME, prefs=[225, 200, 250])
f.place(K, it("K"), NAME, prefs=[315, 290, 340, 270])
E1, E2 = (1, 0, 0), (0, 1, 0)
vlabel(f, *B1, it("v") + sub("1"), PRACTICE, side=1, d=6)
vlabel(f, *B2, it("v") + sub("2"), PRACTICE, side=1, d=6)
vlabel(f, *B3, it("v") + sub("3"), PRACTICE, side=1, d=6)
line_name(f, (T1, 2, 0), E1, it("d") + sub("1"), THEORY, side=-1)
line_name(f, (2, T1, 0), E2, it("d") + sub("2"), BASE, side=-1)
line_name(f, (0, T1, 3), E2, it("d") + sub("3"), REMARK, side=1)
f.render(
    "dik-dogrular",
    "<em>d</em><sub>1</sub> &#8869; <em>d</em><sub>2</sub> ve bu iki doğru <em>K</em>&#8217;da "
    "kesişir. <em>d</em><sub>3</sub>, <em>d</em><sub>1</sub>&#8217;in 3 birim üstünden geçer: "
    "<em>d</em><sub>1</sub> &#8869; <em>d</em><sub>3</sub> olduğu hâlde bu iki doğru kesişmez.",
    "Lines d1 = (t, 2, 0) and d2 = (2, t, 0) meeting at right angles at K = (2, 2, 0) in the XY "
    "plane, and d3 = (0, t, 3) three units above d1, perpendicular to it without meeting it")


# ===========================================================================
# 11. dik-durumlu: d1 = (4, -3, 1) + s(7, 2, -3), d2 = (1, -2, 0) + t(1, -2, 1)
# ===========================================================================
Q1, V1 = (4, -3, 1), (7, 2, -3)
Q2, V2 = (1, -2, 0), (1, -2, 1)
assert vdot(V1, V2) == 0
s0, t0 = -5 / 16, 13 / 16
S1, S2 = at(Q1, V1, s0), at(Q2, V2, t0)
assert close(S1, (29 / 16, -29 / 8, 31 / 16)) and close(S2, (29 / 16, -29 / 8, 13 / 16))
A1, B1 = at(Q1, V1, -0.75), at(Q1, V1, 0.15)
A2, B2 = at(Q2, V2, -0.5), at(Q2, V2, 1.9)
for Q in (A1, B1, A2, B2):
    assert -2 <= Q[0] <= 6 and -6 <= Q[1] <= 1 and -1 <= Q[2] <= 4
ext = [O, (6, 0, 0), (-2, 0, 0), (0, -6, 0), (0, 1, 0), (0, 0, 4), (0, 0, -1), A1, B1, A2, B2]
f = Fig(50, 18, ext, width=560, pad=70)
f.axes(((-2, 6), (-6, 1), (-1, 4)))
f.line([S1, S2], TEXT, 1.2, "4 3", 0.8, w=0.6)
f.line([A2, B2], BASE, 2.1)
f.line([A1, B1], THEORY, 2.1)
f.point(O, TEXT, 3.4)
f.point(S1)
f.point(S2)
f.place(O, it("O"), NAME, prefs=[300, 270, 330])
f.place(S1, it("S") + sub("1"), NAME, prefs=[90, 60, 120, 45, 135])
f.place(S2, it("S") + sub("2"), NAME, prefs=[270, 300, 240, 315, 225])
line_name(f, A1, V1, it("d") + sub("1"), THEORY, side=1)
line_name(f, B2, V2, it("d") + sub("2"), BASE, side=-1)
f.render(
    "dik-durumlu",
    "Dik fakat kesişmeyen <em>d</em><sub>1</sub> ve <em>d</em><sub>2</sub> doğruları. "
    "<em>S</em><sub>1</sub> ile <em>S</em><sub>2</sub> aynı dikey doğru üzerindedir; "
    "<em>d</em><sub>1</sub>, <em>d</em><sub>2</sub>&#8217;nin 9/8 birim üstünden geçer.",
    "Two perpendicular skew lines d1 and d2; S1 on d1 lies 9/8 units straight above S2 on d2, "
    "joined by a dashed vertical segment")


# ===========================================================================
# 12. iki-dogruya-dik: v = v1 x v2 = (-8, -14, -13) through P0 = (3, -1, 4)
# ===========================================================================
P0, V1, V2 = (3, -1, 4), (3, 2, -4), (2, -3, 2)
V = vcross(V1, V2)
assert V == (-8, -14, -13) and vdot(V, V1) == 0 and vdot(V, V2) == 0
E1_, E2_, EV = vadd(P0, V1), vadd(P0, V2), at(P0, V, 0.2)
assert E1_ == (6, 1, 0) and E2_ == (5, -4, 6) and close(EV, (1.4, -3.8, 1.4))
A, B = at(P0, V, -0.15), at(P0, V, 0.28)
for Q in (A, B, E1_, E2_, EV):
    assert 0 <= Q[0] <= 7 and -5 <= Q[1] <= 2 and 0 <= Q[2] <= 7
ext = [O, (7, 0, 0), (0, -5, 0), (0, 2, 0), (0, 0, 7), A, B, E1_, E2_]
f = Fig(20, 18, ext, width=560, pad=70)
f.axes(((0, 7), (-5, 2), (0, 7)))
f.line([A, B], TEXT, 1.4, None, 0.85)
f.arrow(P0, E1_, THEORY, 2.8, 13.0, halo=True)
f.arrow(P0, E2_, BASE, 2.8, 13.0, halo=True)
Va, EV = beside(f, at(P0, V, 0.015), EV, PRACTICE, 10, -1, 3.2)
f.right_angle(P0, V, V1, 20, TEXT)
f.right_angle(P0, V, V2, 20, TEXT)
f.point(O, TEXT, 3.4)
f.point(P0)
f.place(O, it("O"), NAME, prefs=[250, 225, 290])
f.place(P0, P0_, NAME, prefs=[90, 60, 120, 150])
f.place(E1_, it("v") + sub("1"), NAME, THEORY, prefs=ahead(f, V1))
f.place(E2_, it("v") + sub("2"), NAME, BASE, prefs=ahead(f, V2))
f.place(EV, it("v") + " = " + it("v") + sub("1", NAME) + " " + TIMES + " " + it("v") + sub("2", NAME),
        NAME, PRACTICE, prefs=ahead(f, V, (-90, 90, -60, 60, 0)))
line_name(f, A, vscale(-1, V), D_, TEXT, side=1)
f.render(
    "iki-dogruya-dik",
    "<em>P</em><sub>0</sub> = (3, &#8722;1, 4) noktasından çizilen <em>v</em><sub>1</sub>, "
    "<em>v</em><sub>2</sub> ve bunların vektörel çarpımı <em>v</em> = (&#8722;8, &#8722;14, &#8722;13); "
    "<em>v</em> kısaltılarak, yalnız yönü gösterilecek biçimde çizildi. <em>v</em> her ikisine de "
    "diktir ve aranan <em>d</em> doğrusunun doğrultmanıdır.",
    "From P0 = (3, -1, 4): arrows v1 = (3, 2, -4), v2 = (2, -3, 2) and a shortened v = v1 x v2 = "
    "(-8, -14, -13) with right-angle marks, and the line d through P0 along v")


# ===========================================================================
# 13. x-eksenine-dik: P0 = (3, 1, 2), v = (0, 2, -1); d lies in the plane x = 3
# ===========================================================================
P0, V = (3, 1, 2), (0, 2, -1)
A, B = at(P0, V, -1), at(P0, V, 2)
assert A == (3, -1, 3) and B == (3, 5, 0) and at(P0, V, 1) == (3, 3, 1)
PL = [(3, -1, 0), (3, 5, 0), (3, 5, 4), (3, -1, 4)]
ext = [O, (5, 0, 0), (0, 6, 0), (0, -1, 0), (0, 0, 4)] + PL
f = Fig(52, 22, ext, width=560, pad=70)
f.add_occluder(PL)
f.axes(((0, 5), (-1, 6), (0, 4)))
f.polygon(PL, THEORY, 0.10, stroke=THEORY, width=0.9, s_opacity=0.45, w=0.3)
f.line([A, B], THEORY, 2.1)
Va, Vb = beside(f, P0, at(P0, V, 1), PRACTICE, 9, 1, 3.2)
f.point(O, TEXT, 3.4)
f.point((3, 0, 0), TEXT, 3.0)
f.point(P0)
f.place(O, it("O"), NAME, prefs=[250, 225, 290])
f.place((3, 0, 0), "3", DESC, TEXT, prefs=[250, 225, 270, 200])
f.place(P0, P0_, NAME, prefs=[f.sang(V) - 90, f.sang(V) - 60, 180])
vlabel(f, Va, Vb, it("v"), PRACTICE, side=1, t=0.5, d=6)
line_name(f, B, V, D_, THEORY, side=1)
f.place((3, 5, 4), it("x") + " = 3", DESC + 0.5, THEORY, prefs=[0, 30, 330, 90])
f.render(
    "x-eksenine-dik",
    "Doğrultmanı <em>v</em> = (0, 2, &#8722;1) olan <em>d</em> doğrusu <em>x</em> = 3 düzleminde "
    "yatar. Bu düzlem <em>YZ</em> düzlemine paraleldir ve <em>X</em> eksenini 3&#8217;te dik keser.",
    "The plane x = 3 as a translucent patch with the line d through P0 = (3, 1, 2) lying in it, its "
    "direction vector v = (0, 2, -1), and the point 3 on the X axis")


# ===========================================================================
# 14. z-eksenine-paralel: d = {(2, 3, z)}, P0 = (2, 3, 2)
# ===========================================================================
F0, P0 = (2, 3, 0), (2, 3, 2)
V = (0, 0, 1)
A, B = (2, 3, -0.6), (2, 3, 4.6)
ext = [O, (5, 0, 0), (0, 5, 0), (0, 0, 5), (0, 0, -1), A, B]
f = Fig(35, 22, ext, width=520, pad=70)
f.axes(((0, 5), (0, 5), (-1, 5)))
f.line([(2, 0, 0), F0, (0, 3, 0)], TEXT, 1.0, "4 3", 0.55, w=0.4)
f.line([A, B], THEORY, 2.1)
Va, Vb = beside(f, P0, (2, 3, 3.5), PRACTICE, 9, -1, 3.2)
f.point(O, TEXT, 3.4)
f.point(F0)
f.point(P0)
f.place(O, it("O"), NAME, prefs=[225, 200, 250])
f.place(F0, "(" + it("x") + sub("0", DESC + 1) + ", " + it("y") + sub("0", DESC + 1) + ", 0)",
        DESC + 1, TEXT, prefs=[0, 330, 30, 300])
f.place(P0, P0_, NAME, prefs=[180, 200, 160])
vlabel(f, Va, Vb, it("v"), PRACTICE, side=-1, t=0.5, d=6)
line_name(f, B, V, D_, THEORY, side=-1)
f.render(
    "z-eksenine-paralel",
    "Doğrultmanı <em>Z</em> eksenine paralel olan <em>d</em> doğrusu, <em>XY</em> düzlemindeki "
    "(<em>x</em><sub>0</sub>, <em>y</em><sub>0</sub>, 0) noktasından dikey olarak geçer; "
    "üzerinde <em>x</em> = <em>x</em><sub>0</sub> ve <em>y</em> = <em>y</em><sub>0</sub> sabittir.",
    "A vertical line d through the point (x0, y0, 0) of the XY plane, with P0 on it and a direction "
    "vector v parallel to the Z axis drawn beside it")


# ===========================================================================
# 15. dogrusal-uc-nokta: A = (1, 2, -4), B = (3, 4, -1), C = (7, 8, 5); AC = 3 AB
# ===========================================================================
Ap, Bp, Cp = (1, 2, -4), (3, 4, -1), (7, 8, 5)
V = vsub(Bp, Ap)
assert V == (2, 2, 3) and vsub(Cp, Ap) == vscale(3, V)
A, B = at(Ap, V, -0.3), at(Ap, V, 3.3)
ext = [O, (8, 0, 0), (0, 9, 0), (0, 0, 6), (0, 0, -5), A, B]
f = Fig(12, 18, ext, width=560, pad=70)
f.axes(((0, 8), (0, 9), (-5, 6)))
f.line([A, B], THEORY, 2.1)
Ca, Cb = beside(f, Ap, Cp, REMARK, 10, -1, 2.6)
Ba, Bb = beside(f, Ap, Bp, PRACTICE, 10, 1, 3.2)
f.point(O, TEXT, 3.4)
for Q in (Ap, Bp, Cp):
    f.point(Q)
f.place(O, it("O"), NAME, prefs=[225, 200, 250])
a = f.sang(V)
f.place(Ap, it("A"), NAME, prefs=[a + 180, a + 150, a + 210])
f.place(Bp, it("B"), NAME, prefs=[a + 90, a + 60, a + 120])
f.place(Cp, it("C"), NAME, prefs=[a + 90, a + 60, a - 90])
over_label(f, mid(Ba, Bb), [("A", None), ("B", None)], PRACTICE, prefs=[a + 90, a + 70, a + 110],
           d=6)
over_label(f, vadd(Ca, vscale(0.6, vsub(Cb, Ca))), [("A", None), ("C", None)], REMARK,
           prefs=[a - 90, a - 70, a - 110], d=6)
line_name(f, B, V, D_, THEORY, side=1)
f.render(
    "dogrusal-uc-nokta",
    "<em>A</em>, <em>B</em>, <em>C</em> aynı <em>d</em> doğrusu üzerindedir: <em>AC</em> vektörü "
    "<em>AB</em> vektörünün 3 katıdır.",
    "Line d through A = (1, 2, -4), B = (3, 4, -1) and C = (7, 8, 5); the vector AB and the vector "
    "AC = 3 AB drawn on the two sides of the line")


# ---------------------------------------------------------------------------
for name, content in OUT.items():
    path = OUT_DIR / f"analytic-udd-{name}.md"
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(content)
    print("wrote", path.name)
