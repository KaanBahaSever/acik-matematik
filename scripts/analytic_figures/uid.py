# -*- coding: utf-8 -*-
"""Figures for dersler/analitik-geometri/uzayda-iki-dogru.qmd (chapter key: uid).

All drawings are three-dimensional and go through scripts/svg_plot3.py (an
orthographic Camera on an equal-aspect svg_plot.Plot panel). Two lines that
cross on the page but not in space are drawn with a gap: the nearer one gets
a background-colored halo, so it reads as passing in front. The figures go
INSIDE the box they explain (example, solution, proof), never inside a
definition box.

Labels are placed after the projection, in page pixels: `Canvas.place` tries
a ring of candidate positions around the anchor and keeps the cheapest one,
i.e. the one that touches no registered line, point or earlier label.

Usage:   python scripts/analytic_figures/uid.py
         python scripts/center_figures.py "analytic-uid-*.md" --keep-width
Output:  scripts/_figures/analytic-uid-<name>.md
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

TALL_SCENES = {"aci-dik-ornek"}
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


def nm(letter, idx=None, size=NAME):
    """Italic name with an optional subscript, e.g. nm('d', '1') for d_1."""
    return it(letter) + (sub(idx, size) if idx else "")


D1, D2 = nm("d", "1"), nm("d", "2")
V1, V2 = nm("v", "1"), nm("v", "2")
N1_, N2_ = nm("N", "1"), nm("N", "2")
P0_, P1_, P2_ = nm("P", "0"), nm("P", "1"), nm("P", "2")


def along(P, v, t):
    return vadd(P, vscale(t, v))


def seg(P, v, t0, t1):
    return [along(P, v, t0), along(P, v, t1)]


def ahead(f, vec, spread=(0, 30, -30, 60, -60, 90, -90)):
    """Label angles around the page direction of vec: first straight past the tip."""
    a = f.sang(vec)
    return [a + s for s in spread]


def side(f, vec, sign=1, spread=(0, 20, -20, 40, -40)):
    """Label angles perpendicular to the page direction of vec (sign picks the side)."""
    a = f.sang(vec) + 90 * sign
    return [a + s for s in spread]


def sline(f, A, B, color, width=2.2, opacity=1.0, halo=False, dash=None, w=1.0):
    """A straight piece of a line; with halo it is drawn over a background stroke,
    so any line it crosses on the page shows a gap (it passes in front)."""
    if halo:
        f.S.line([A, B], BG, width + 5.0, None, 1.0)
    f.line([A, B], color, width, dash, opacity, w)


def hollow(f, P, color=TEXT, r=4.2, width=1.6):
    f.S.hollow(P, color, r, width)
    x, y = f.px(P)
    f.dots.append((x, y, r))


def angle_mark(f, Q, a, b, r_px=30, gap=13, s=None, color=TEXT):
    """Arc between the directions a and b at Q, with the angle name just past the
    middle of the arc (measured on the page, so foreshortening is taken into account)."""
    pts = f.arc(Q, a, b, r_px, color, 1.4)
    x, y = f.px(Q)
    X, Y = f.px(pts[len(pts) // 2])
    L = math.hypot(X - x, Y - y)
    anchor = ("px", x + (X - x) / L * (L + gap), y + (Y - y) / L * (L + gap))
    f.place(anchor, s or it(THETA), NAME, color, prefs=["c"], far=(0, 4, 8))


def shift(f, dx, dy):
    """Move a panel on the shared canvas; call before anything is drawn on it."""
    f.p.x0 += dx
    f.p.y0 += dy


def title(f, s, dy=-50):
    f.place(("px", f.p.x0 + f.p.w / 2, f.p.y0 + dy), s, DESC + 0.5, TEXT, prefs=["c"], only=True)


def render_multi(figs, name, caption, aria, margin=40):
    print(f"-- {name} (warnings above belong to it)")
    for f in figs:
        for t in f.emit_texts():
            f.p.add(t)
    W = max(f.p.x0 + f.p.w for f in figs) + margin
    H = max(f.p.y0 + f.p.h for f in figs) + margin
    OUT[name] = figure(round(W), round(H), [f.p for f in figs], caption, WIDE, aria)


def vec_label(f, anchor, s, color, prefs=None, size=NAME, d=7.0):
    """A vector name with a small arrow over it (the whole name is covered)."""
    cx, ty = f.place(anchor, s, size, color, prefs=prefs, d=d, tall=6)
    w = text_width(s, size) * 0.82
    f.over_arrow(cx, ty + 0.30 * size - 0.98 * size - 1.5, w, color)


# ===========================================================================
# 1. uid-aci-tanimi: the angle of two lines, intersecting and not intersecting
# ===========================================================================
AZ1, EL1 = 30, 20
K1, U1, U2 = (2, 2, 1), (1, 2, 0), (0, 1, 1)
assert close(along((1, 0, 1), U1, 1), K1)
ext = [O, (4, 0, 0), (0, 4.3, 0), (0, 0, 3.2), (2, 0.4, -0.6), (3.2, 4.4, 1)]
fa = Fig(AZ1, EL1, ext, width=300, pad=56)
fa.axes(((0, 4), (0, 4.3), (0, 3.2)), opacity=0.45, width=1.1)
A, B = seg((1, 0, 1), U1, -0.3, 2.2)
C, D = seg(K1, U2, -1.6, 1.9)
sline(fa, C, D, PRACTICE, 2.0)
sline(fa, A, B, THEORY, 2.0, halo=True)
fa.arrow(K1, along(K1, U1, 0.6), THEORY, 3.2, 12.0)
fa.arrow(K1, along(K1, U2, 1.0), PRACTICE, 3.2, 12.0)
angle_mark(fa, K1, U1, U2, 30)
fa.point(K1, TEXT, 3.8)
fa.place(K1, it("K"), NAME, prefs=[fa.sang(U1) + 180 + 30, fa.sang(U1) + 180 - 30, 270])
fa.place(along(K1, U1, 0.6), V1, NAME, THEORY, prefs=side(fa, U1, -1), d=6)
fa.place(along(K1, U2, 1.0), V2, NAME, PRACTICE, prefs=side(fa, U2, 1), d=6)
fa.place(B, D1, NAME, THEORY, prefs=ahead(fa, U1))
fa.place(D, D2, NAME, PRACTICE, prefs=ahead(fa, U2))

Q2, W1, W2 = (2, 1, 0), (1, 0, 0), (1, 2, 0)
ext = [O, (4.3, 0, 0), (0, 4, 0), (0, 0, 3.6), (1, -2, 3), (3, 2, 3), (1.2, -0.6, 0), (3.2, 3.4, 0)]
fb = Fig(AZ1, 36, ext, width=300, pad=56)
shift(fb, fa.p.w + 90, 0)
fb.axes(((0, 4.3), (0, 4), (0, 3.6)), opacity=0.45, width=1.1)
A, B = seg((0, 1, 0), W1, -0.5, 4.3)
C, D = seg((2, 0, 3), W2, -0.5, 1.0)
E, F = seg(Q2, W2, -0.8, 1.25)
sline(fb, E, F, PRACTICE, 1.5, 0.75, dash="6 4")
sline(fb, A, B, THEORY, 2.0, halo=True)
sline(fb, C, D, PRACTICE, 2.0, halo=True)
S0, S1 = along((2, 0, 3), W2, 1.0), along(Q2, W2, 1.0)
fb.arrow(vadd(S0, (0, 0.12, -0.36)), vsub(S1, (0, 0.12, -0.36)), REMARK, 1.2, 9.0, "4 3", 0.9)
fb.arrow(Q2, along(Q2, W1, 1.0), THEORY, 3.2, 12.0)
fb.arrow(Q2, along(Q2, W2, 0.55), PRACTICE, 3.2, 12.0)
angle_mark(fb, Q2, W1, W2, 34)
fb.point(Q2, TEXT, 3.8)
fb.place(B, D1, NAME, THEORY, prefs=ahead(fb, W1))
fb.place(D, D2, NAME, PRACTICE, prefs=ahead(fb, W2))
fb.place(F, D2 + "&#8242;", NAME, PRACTICE, prefs=ahead(fb, W2))
fb.place(along(Q2, W1, 1.0), V1, NAME, THEORY, prefs=side(fb, W1, -1), d=6)
fb.place(along(Q2, W2, 0.55), V2, NAME, PRACTICE, prefs=side(fb, W2, 1), d=6)
title(fa, "Kesişen doğrular")
title(fb, "Kesişmeyen doğrular")
render_multi(
    [fa, fb], "aci-tanimi",
    "Solda <em>d</em><sub>1</sub> ile <em>d</em><sub>2</sub> <em>K</em> noktasında kesişir; aralarındaki "
    "açı, <em>K</em>&#8217;dan çizilen doğrultman vektörleri <em>v</em><sub>1</sub>, <em>v</em><sub>2</sub> "
    "arasındaki <em>&#952;</em> açısıdır. Sağda doğrular kesişmez: <em>d</em><sub>2</sub> kendine paralel "
    "kaydırılarak <em>d</em><sub>1</sub>&#8217;i kesen <em>d</em><sub>2</sub>&#8242; konumuna getirilir; "
    "doğrultman vektörü, dolayısıyla açı değişmez.",
    "Left: lines d1 and d2 meeting at K with direction vectors v1 = (1, 2, 0) and v2 = (0, 1, 1) drawn "
    "from K and the angle theta between them. Right: d1 on the floor and d2 at height 3, not meeting; "
    "a dashed copy d2' of d2 slid down to meet d1, with v1, v2 and theta at the meeting point")


# ===========================================================================
# 2. uid-aci-dik-ornek: d1, d2 meet at right angles at K(28/9, -17/27, 17/9)
# ===========================================================================
P1v, U1 = (2, -1, 3), (3, 1, -3)
P2v, U2 = (0, -80 / 27, -2), (4, 3, 5)
K = (28 / 9, -17 / 27, 17 / 9)
assert vdot(U1, U2) == 0
assert close(along(P1v, U1, 10 / 27), K) and close(along(P2v, U2, 7 / 9), K)
A, B = seg(P1v, U1, -0.35, 1.0)
C, D = seg(P2v, U2, -0.2, 1.25)
ext = [O, (5.4, 0, 0), (-1, 0, 0), (0, 2.5, 0), (0, -4, 0), (0, 0, 5), (0, 0, -3), A, B, C, D]
f = Fig(-60, 20, ext, width=560, pad=70)
f.axes(((-1, 5.4), (-4, 2.5), (-3, 5)), opacity=0.45, width=1.1)
sline(f, A, B, THEORY, 2.4)
sline(f, C, D, PRACTICE, 2.4, halo=True)
f.right_angle(K, U1, U2, 15)
for P in (P1v, P2v, K):
    f.point(P, TEXT, 3.8)
f.place(O, it("O"), NAME, prefs=[200, 225, 180])
f.place(P1v, P1_, NAME, prefs=side(f, U1, 1))
f.place(P2v, P2_, NAME, prefs=side(f, U2, -1))
f.place(K, it("K"), NAME, prefs=[f.sang(vadd(vunit(U1), vunit(U2))) + 180])
f.place(B, D1, NAME, THEORY, prefs=ahead(f, U1))
f.place(D, D2, NAME, PRACTICE, prefs=ahead(f, U2))
f.render(
    "aci-dik-ornek",
    "<em>d</em><sub>1</sub> ile <em>d</em><sub>2</sub> doğruları <em>K</em>(28/9, &#8722;17/27, 17/9) "
    "noktasında dik kesişir: &#10216;<em>v</em><sub>1</sub>, <em>v</em><sub>2</sub>&#10217; = 0, "
    "<em>&#952;</em> = &#960;/2.",
    "Lines d1 through P1(2, -1, 3) with direction (3, 1, -3) and d2 through P2(0, -80/27, -2) with "
    "direction (4, 3, 5) meeting at K with a right-angle mark")


# ===========================================================================
# 3. uid-nokta-dogru: the distance of a point Q from a line d
# ===========================================================================
P0v, Vd = (1, 0, 1), (1, 1.5, 0)
H = along(P0v, Vd, 1.3)
Qv = vadd(H, (0, 0, 2.2))
assert abs(vdot(vsub(Qv, H), Vd)) < 1e-12
A, B = seg(P0v, Vd, -0.8, 2.5)
ext = [O, (3.4, 0, 0), (0, 4.4, 0), (0, 0, 3.6), A, B, Qv]
f = Fig(25, 20, ext, width=560, pad=70)
f.axes(((0, 3.4), (0, 4.4), (0, 3.6)), opacity=0.4, width=1.1)
sline(f, A, B, THEORY, 2.2)
f.line([P0v, Qv], TEXT, 1.6, None, 0.85)
f.line([Qv, H], BASE, 2.0, "6 4", 1.0)
f.arrow(P0v, along(P0v, Vd, 0.75), THEORY, 3.4, 13.0)
f.right_angle(H, vscale(-1, Vd), vsub(Qv, H), 14)
angle_mark(f, P0v, Vd, vsub(Qv, P0v), 34)
for P in (P0v, H, Qv):
    f.point(P, TEXT, 3.8)
f.place(P0v, P0_, NAME, prefs=side(f, Vd, -1))
f.place(H, it("H"), NAME, prefs=side(f, Vd, -1))
f.place(Qv, it("Q"), NAME, prefs=[90, 60, 120])
f.place(along(P0v, Vd, 0.75), it("v"), NAME + 1, THEORY, prefs=side(f, Vd, -1), d=6)
f.place(vscale(0.5, vadd(Qv, H)), it("&#8467;"), NAME + 1, BASE, prefs=[0, 20, -20, 180])
f.place(B, it("d"), NAME + 1, THEORY, prefs=ahead(f, Vd))
f.render(
    "nokta-dogru",
    "<em>Q</em> noktasından <em>d</em> doğrusuna inilen dikme <em>QH</em>; uzunluğu <em>&#8467;</em> = "
    "|<em>QH</em>|, <em>Q</em>&#8217;nun <em>d</em>&#8217;ye uzaklığıdır. <em>&#952;</em>, <em>d</em>&#8217;nin "
    "doğrultman vektörü <em>v</em> ile <em>P</em><sub>0</sub><em>Q</em> arasındaki açıdır.",
    "A line d through P0 with direction v, a point Q off the line, the dashed perpendicular QH with a "
    "right-angle mark at H and length l, the segment P0Q and the angle theta at P0")


# ===========================================================================
# 4. uid-paralelkenar-yukseklik: area |v x P0Q| = |v| l
# ===========================================================================
P0v, Vd = (1, 0, 1), (1.3, 1.95, 0)
H = along(P0v, Vd, 0.55)
Qv = vadd(H, (0, 0, 2.0))
Av = vadd(P0v, Vd)
Cv = vadd(Av, vsub(Qv, P0v))
A, B = seg(P0v, Vd, -0.45, 1.7)
ext = [O, (3.6, 0, 0), (0, 4.4, 0), (0, 0, 3.6), A, B, Cv]
f = Fig(25, 20, ext, width=560, pad=70)
PL = [P0v, Av, Cv, Qv]
f.add_occluder(PL)
f.axes(((0, 3.6), (0, 4.4), (0, 3.6)), opacity=0.4, width=1.1)
f.polygon(PL, THEORY, 0.13, stroke=THEORY, width=1.0, s_opacity=0.5, dash="5 4")
sline(f, A, B, THEORY, 2.0)
f.line([Qv, H], BASE, 2.0, "6 4", 1.0)
f.right_angle(H, Vd, vsub(Qv, H), 14)
f.arrow(P0v, Av, THEORY, 3.2, 13.0)
f.arrow(P0v, Qv, PRACTICE, 3.2, 13.0, halo=True)
for P in (P0v, H, Qv):
    f.point(P, TEXT, 3.8)
f.place(P0v, P0_, NAME, prefs=side(f, Vd, -1))
f.place(H, it("H"), NAME, prefs=side(f, Vd, -1))
f.place(Qv, it("Q"), NAME, prefs=[135, 90, 180])
f.place(Av, it("v"), NAME + 1, THEORY, prefs=side(f, Vd, -1, (0, 30, -30)), d=6)
vec_label(f, vscale(0.5, vadd(P0v, Qv)), it("P") + sub("0") + it("Q"), PRACTICE,
          prefs=side(f, vsub(Qv, P0v), 1))
f.place(vscale(0.5, vadd(Qv, H)), it("&#8467;"), NAME + 1, BASE, prefs=[0, 20, -20, 180])
f.place(vscale(0.5, vadd(vadd(Av, Qv), (0, 0, 0))), "alan = " + NORM + "&#8201;" + it("v") + " " + TIMES + " "
        + it("P") + sub("0") + it("Q") + "&#8201;" + NORM, DESC, TEXT, prefs=["c", 0, 180])
f.place(B, it("d"), NAME + 1, THEORY, prefs=ahead(f, Vd))
f.render(
    "paralelkenar-yukseklik",
    "<em>v</em> ile <em>P</em><sub>0</sub><em>Q</em> vektörlerinin gerdiği paralelkenarın alanı "
    "&#8214;<em>v</em> &#215; <em>P</em><sub>0</sub><em>Q</em>&#8214;, tabanı &#8214;<em>v</em>&#8214;, "
    "yüksekliği <em>&#8467;</em> = |<em>QH</em>|&#8217;dir; bu yüzden <em>&#8467;</em> = "
    "&#8214;<em>v</em> &#215; <em>P</em><sub>0</sub><em>Q</em>&#8214; / &#8214;<em>v</em>&#8214;.",
    "The parallelogram spanned by v along the line d and the vector P0Q, shaded, with the dashed "
    "height QH of length l and a right-angle mark at H")


# ===========================================================================
# 5. uid-dikme-ayagi-ornek: foot of the perpendicular from Q(0, -1, -2) to d
# ===========================================================================
P0v, Wd = (0, 1, -2), (2, 4, 1)
Qv = (0, -1, -2)
H = (-16 / 21, -11 / 21, -50 / 21)
assert close(along(P0v, Wd, -8 / 21), H) and abs(vdot(vsub(Qv, H), Wd)) < 1e-12
A, B = seg(P0v, Wd, -0.8, 0.6)
ext = [O, (1.2, 0, 0), (-2, 0, 0), (0, 3.6, 0), (0, -2.4, 0), (0, 0, 1.2), (0, 0, -3), A, B]
f = Fig(-165, 50, ext, width=560, pad=70)
f.axes(((-2, 1.2), (-2.4, 3.6), (-3, 1.2)), opacity=0.45, width=1.1)
sline(f, A, B, THEORY, 2.2, halo=True)
f.line([P0v, Qv], TEXT, 1.4, None, 0.7)
f.line([Qv, H], BASE, 2.2, "6 4", 1.0)
f.right_angle(H, Wd, vsub(Qv, H), 13)
for P in (P0v, H, Qv):
    f.point(P, TEXT, 3.8)
f.place(O, it("O"), NAME, prefs=[200, 225, 180])
f.place(P0v, P0_, NAME, prefs=side(f, Wd, -1))
f.place(H, it("H"), NAME, prefs=side(f, Wd, 1))
f.place(Qv, it("Q"), NAME, prefs=side(f, Wd, -1))
f.place(vscale(0.5, vadd(Qv, H)), it("&#8467;") + " = 2" + SQRT + "105/21", DESC, BASE,
        prefs=side(f, vsub(Qv, H), 1) + side(f, vsub(Qv, H), -1))
f.place(B, it("d"), NAME + 1, THEORY, prefs=ahead(f, Wd))
f.render(
    "dikme-ayagi-ornek",
    "<em>Q</em>(0, &#8722;1, &#8722;2) noktasından <em>d</em> : 2<em>x</em> = <em>y</em> &#8722; 1 = "
    "4<em>z</em> + 8 doğrusuna inilen dikmenin ayağı <em>H</em>(&#8722;16/21, &#8722;11/21, &#8722;50/21); "
    "|<em>QH</em>| = 2&#8730;105/21.",
    "Line d through P0(0, 1, -2) with direction (2, 4, 1), the point Q(0, -1, -2), the foot "
    "H(-16/21, -11/21, -50/21) and the dashed perpendicular QH with a right-angle mark")


def crossing_front(f, A, B, C, D):
    """Where the page images of AB and CD cross: True if AB is nearer the viewer there,
    False if CD is, None if the two pieces do not cross on the page."""
    a, b, c, d = (f.cam.project(P) for P in (A, B, C, D))
    r = (b[0] - a[0], b[1] - a[1])
    q = (d[0] - c[0], d[1] - c[1])
    den = r[0] * q[1] - r[1] * q[0]
    if abs(den) < 1e-12:
        return None
    t = ((c[0] - a[0]) * q[1] - (c[1] - a[1]) * q[0]) / den
    u = ((c[0] - a[0]) * r[1] - (c[1] - a[1]) * r[0]) / den
    if not (0 <= t <= 1 and 0 <= u <= 1):
        return None
    return a[2] + t * (b[2] - a[2]) > c[2] + u * (d[2] - c[2])


def two_lines(f, A, B, C, D, c1=THEORY, c2=PRACTICE, width=2.2):
    """Draw two lines; the one in front where they cross on the page gets the gap-making halo."""
    fr = crossing_front(f, A, B, C, D)
    if fr:
        sline(f, C, D, c2, width)
        sline(f, A, B, c1, width, halo=True)
    else:
        sline(f, A, B, c1, width)
        sline(f, C, D, c2, width, halo=True)


AZ7, EL7 = 40, 55
AZ8, EL8 = -135, 30
AZ9, EL9 = 35, 20
AZ10, EL10 = -100, 28
AZ11, EL11 = 30, 20
AZ12, EL12 = 50, 20
AZ13, EL13 = -135, 28
AZ14, EL14 = -135, 28
AZ15, EL15 = 150, 20
AZ16, EL16 = 130, 58
AZ17, EL17 = -40, 44


# ===========================================================================
# 6. uid-dort-durum: intersecting, parallel, coincident and skew lines (2 x 2)
# ===========================================================================
AZ6, EL6, PW6 = 32, 22, 270
panels = []


def small_panel(col, row, ext):
    g = Fig(AZ6, EL6, ext + [O, (2.6, 0, 0), (0, 2.6, 0), (0, 0, 2.6)], width=PW6, pad=50)
    shift(g, col * (PW6 + 80), row * 330)
    g.axes(((0, 2.6), (0, 2.6), (0, 2.6)), opacity=0.4, width=1.0, head=8.0)
    panels.append(g)
    return g


# (1) intersecting
K6 = (1.2, 1.2, 1.1)
A, B = seg(K6, (0, 1, 0.75), -1.3, 1.3)
C, D = seg(K6, (0.4, 1, -0.7), -1.2, 1.3)
g = small_panel(0, 0, [A, B, C, D])
two_lines(g, A, B, C, D)
g.point(K6, TEXT, 3.8)
g.place(K6, it("K"), NAME, prefs=[270, 250, 290, 90])
g.place(B, D1, NAME, THEORY, prefs=ahead(g, (0, 1, 0.75)))
g.place(D, D2, NAME, PRACTICE, prefs=ahead(g, (0.4, 1, -0.7)))
title(g, "Kesişen", -40)
# (2) parallel and distinct
A, B = seg((1.2, 0, 0.3), (0, 1, 0.45), -0.2, 2.5)
C, D = seg((1.2, 0, 1.5), (0, 1, 0.45), -0.2, 2.5)
g = small_panel(1, 0, [A, B, C, D])
sline(g, A, B, THEORY, 2.2)
sline(g, C, D, PRACTICE, 2.2, halo=True)
g.place(B, D1, NAME, THEORY, prefs=ahead(g, (0, 1, 0.45)))
g.place(D, D2, NAME, PRACTICE, prefs=ahead(g, (0, 1, 0.45)))
title(g, "Paralel", -40)
# (3) coincident
A, B = seg((1.2, 0, 0.5), (0, 1, 0.6), -0.2, 2.5)
g = small_panel(0, 1, [A, B])
sline(g, A, B, THEORY, 4.2, halo=True)
g.line([A, B], PRACTICE, 1.6, "7 5", 1.0)
g.place(B, D1 + " = " + D2, NAME, TEXT, prefs=ahead(g, (0, 1, 0.6)))
title(g, "Çakışık", -40)
# (4) skew
F1, F2 = (1.5, 1.2, 0.3), (1.5, 1.2, 1.8)
A, B = seg(F1, (0, 1, 0), -1.5, 1.4)
C, D = seg(F2, (1, 0, 0), -1.8, 1.4)
g = small_panel(1, 1, [A, B, C, D])
two_lines(g, A, B, C, D)
g.line([F1, F2], BASE, 1.6, "5 4", 1.0)
g.place(B, D1, NAME, THEORY, prefs=ahead(g, (0, 1, 0)))
g.place(D, D2, NAME, PRACTICE, prefs=ahead(g, (1, 0, 0)))
title(g, "Aykırı", -40)
render_multi(
    panels, "dort-durum",
    "Uzayda iki doğrunun dört durumu: kesişen doğrular (tek ortak nokta <em>K</em>), paralel ve farklı "
    "doğrular, çakışık doğrular ve aykırı doğrular. Aykırı doğrular ne kesişir ne de paraleldir; kesikli "
    "parça ikisine birden diktir.",
    "Four small panels with axes: two lines meeting at K; two parallel lines one above the other; one "
    "line drawn twice, solid and dashed, labelled d1 = d2; two skew lines, one along Y low and one "
    "along X high, with a dashed vertical common perpendicular")


# ===========================================================================
# 7. uid-kesisen-ornek: d1, d2 meet far away at K(-17, -21, -32)
# ===========================================================================
P1v, U1 = (-1, 3, 0), (2, 3, 4)
P2v, U2 = (1, 0, -5), (6, 7, 9)
K = (-17, -21, -32)
assert along(P1v, U1, -8) == K and along(P2v, U2, -3) == K
A, B = seg(P1v, U1, -9, 1)
C, D = seg(P2v, U2, -3.4, 0.3)
ext = [A, B, C, D, (5, 0, 0), (0, 6, 0), (0, 0, 5)]
f = Fig(AZ7, EL7, ext, width=560, pad=70)
f.axes(((0, 5), (0, 6), (0, 5)), opacity=0.45, width=1.1)
sline(f, A, B, THEORY, 2.2)
sline(f, C, D, PRACTICE, 2.2, halo=True)
for P in (P1v, P2v, K):
    f.point(P, TEXT, 3.8)
f.place(O, it("O"), NAME, prefs=[200, 225, 180, 250])
f.place(P1v, P1_, NAME, prefs=side(f, U1, 1))
f.place(P2v, P2_, NAME, prefs=side(f, U2, -1))
f.place(K, it("K") + triple(-17, -21, -32), NAME, prefs=ahead(f, vscale(-1, U1), (0, 20, -20, 40, -40)))
f.place(B, D1, NAME, THEORY, prefs=ahead(f, U1))
f.place(D, D2, NAME, PRACTICE, prefs=ahead(f, U2))
f.render(
    "kesisen-ornek",
    "<em>d</em><sub>1</sub> ile <em>d</em><sub>2</sub> <em>K</em>(&#8722;17, &#8722;21, &#8722;32) "
    "noktasında kesişir. Doğrultman vektörleri arasındaki açı küçük olduğundan doğrular kesişim noktasına "
    "doğru yavaşça yaklaşır; eksenler başlangıç noktası çevresinde, ölçek için çizilmiştir.",
    "Two lines through P1(-1, 3, 0) with direction (2, 3, 4) and P2(1, 0, -5) with direction "
    "(6, 7, 9) converging to their common point K(-17, -21, -32), with short axes at the origin")


# ===========================================================================
# 8. uid-kesisme-parametresi: for m = 0 the lines meet at (0, 0, 1)
# ===========================================================================
U1, U2 = (2, 1, 1), (1, 2, 1)
M0 = (0, 0, 1)
A, B = seg(M0, U1, -0.9, 1.25)
C, D = seg(M0, U2, -0.9, 1.25)
A1, B1 = seg((0, 2, 1), U1, -0.6, 1.1)
C1, D1p = seg((1, 0, 1), U2, -0.6, 1.1)
ext = [A, B, C, D, A1, B1, C1, D1p, (3, 0, 0), (0, 3.2, 0), (0, 0, 3), (-1.5, 0, 0), (0, -1.5, 0)]
f = Fig(AZ8, EL8, ext, width=560, pad=70)
f.axes(((-1.5, 3), (-1.5, 3.2), (0, 3)), opacity=0.45, width=1.1)
fr = crossing_front(f, A1, B1, C1, D1p)
for (X0, X1, col), h in (((A1, B1, THEORY), fr is True), ((C1, D1p, PRACTICE), fr is False)):
    if not h:
        sline(f, X0, X1, col, 1.5, 0.65, dash="6 4")
for (X0, X1, col), h in (((A1, B1, THEORY), fr is True), ((C1, D1p, PRACTICE), fr is False)):
    if h:
        sline(f, X0, X1, col, 1.5, 0.65, halo=True, dash="6 4")
sline(f, A, B, THEORY, 2.4, halo=True)
sline(f, C, D, PRACTICE, 2.4, halo=True)
f.point(M0, TEXT, 3.8)
f.place(M0, P1_ + " = " + P2_ + " = (0, 0, 1)", NAME, prefs=[180, 160, 200, 135, 225])
f.place(B, D1, NAME, THEORY, prefs=ahead(f, U1))
f.place(D, D2, NAME, PRACTICE, prefs=ahead(f, U2))
f.place(B1, D1 + "&#8242; (" + it("m") + " = 1)", DESC, THEORY, prefs=ahead(f, U1), opacity=0.85)
f.place(D1p, D2 + "&#8242; (" + it("m") + " = 1)", DESC, PRACTICE, prefs=ahead(f, U2), opacity=0.85)
f.render(
    "kesisme-parametresi",
    "<em>m</em> = 0 için <em>d</em><sub>1</sub> ile <em>d</em><sub>2</sub> (0, 0, 1) noktasında kesişir. "
    "Kesikli çizilen <em>d</em><sub>1</sub>&#8242; ve <em>d</em><sub>2</sub>&#8242; ise <em>m</em> = 1 "
    "için aynı doğrulardır; bunlar kesişmez, aykırıdır.",
    "For m = 0 the lines through (0, 0, 1) with directions (2, 1, 1) and (1, 2, 1) meet there; dashed, "
    "the lines for m = 1 through (0, 2, 1) and (1, 0, 1) with the same directions, which do not meet")


# ===========================================================================
# 9. uid-paralel-ornek: parallel distinct lines at distance 3
# ===========================================================================
P1v, P2v, U1 = (1, 0, -1), (4, 0, 2), (1, 2, 2)
H = (2, 2, 1)
assert along(P1v, U1, 1) == H and vdot(vsub(P2v, H), U1) == 0 and vnorm(vsub(P2v, H)) == 3
A, B = seg(P1v, U1, -0.55, 1.6)
C, D = seg(P2v, U1, -0.9, 1.25)
ext = [A, B, C, D, O, (5.4, 0, 0), (0, 4.6, 0), (0, 0, 5), (0, 0, -2)]
f = Fig(AZ9, EL9, ext, width=560, pad=70)
f.axes(((0, 5.4), (0, 4.6), (-2, 5)), opacity=0.45, width=1.1)
sline(f, A, B, THEORY, 2.2)
sline(f, C, D, PRACTICE, 2.2, halo=True)
f.line([P2v, H], BASE, 1.6, "5 4", 0.95)
f.right_angle(H, U1, vsub(P2v, H), 12)
f.arrow(P1v, along(P1v, U1, 0.45), THEORY, 3.4, 12.0)
f.arrow(along(P2v, U1, 1.2), along(P2v, U1, 0.3), PRACTICE, 3.4, 12.0)
for P in (P1v, P2v, H):
    f.point(P, TEXT, 3.8)
f.place(P1v, P1_, NAME, prefs=side(f, U1, -1))
f.place(P2v, P2_, NAME, prefs=side(f, U1, 1))
f.place(H, it("H"), NAME, prefs=side(f, U1, -1))
f.place(vscale(0.5, vadd(P2v, H)), "3", NAME, BASE, prefs=side(f, vsub(P2v, H), 1) + side(f, vsub(P2v, H), -1))
f.place(along(P1v, U1, 0.45), V1, NAME, THEORY, prefs=side(f, U1, -1), d=6)
f.place(along(P2v, U1, 0.75), V2 + " = " + MINUS + "2" + V1, NAME, PRACTICE, prefs=side(f, U1, 1), d=8)
f.place(B, D1, NAME, THEORY, prefs=ahead(f, U1))
f.place(D, D2, NAME, PRACTICE, prefs=ahead(f, U1))
f.render(
    "paralel-ornek",
    "Paralel ve farklı iki doğru: <em>v</em><sub>2</sub> = &#8722;2<em>v</em><sub>1</sub> ters yönde ve iki "
    "kat uzundur, <em>P</em><sub>2</sub>(4, 0, 2) ise <em>d</em><sub>1</sub> üzerinde değildir. "
    "<em>P</em><sub>2</sub>&#8217;den <em>d</em><sub>1</sub>&#8217;e inilen dikmenin ayağı <em>H</em>(2, 2, 1), "
    "uzunluğu 3&#8217;tür.",
    "Two parallel lines d1 through P1(1, 0, -1) and d2 through P2(4, 0, 2), both along (1, 2, 2); an "
    "arrow v1 on d1 and a twice as long opposite arrow v2 = -2 v1 on d2; the dashed perpendicular P2H "
    "of length 3 with a right-angle mark at H(2, 2, 1)")


# ===========================================================================
# 10. uid-aykiri-ornek: skew lines and their common perpendicular
# ===========================================================================
P1v, U1 = (1, 2, 0), (1, -1, 2)
P2v, U2 = (0, -1, 3), (2, 1, -1)
N1 = (15 / 7, 6 / 7, 16 / 7)
N2 = (16 / 7, 1 / 7, 13 / 7)
assert close(along(P1v, U1, 8 / 7), N1) and close(along(P2v, U2, 8 / 7), N2)
assert abs(vdot(vsub(N2, N1), U1)) < 1e-12 and abs(vdot(vsub(N2, N1), U2)) < 1e-12
A, B = seg(P1v, U1, -0.6, 2)
C, D = seg(P2v, U2, -0.5, 2)
ext = [A, B, C, D, O, (4, 0, 0), (-1, 0, 0), (0, 3.5, 0), (0, -1.5, 0), (0, 0, 4.2), (0, 0, -1.2)]
f = Fig(AZ10, EL10, ext, width=560, pad=70)
f.axes(((-1, 4), (-1.5, 3.5), (-1.2, 4.2)), opacity=0.4, width=1.1)
assert crossing_front(f, A, B, C, D) is not None
two_lines(f, A, B, C, D)
f.line([N1, N2], BASE, 2.0, "4 3", 1.0)
for P in (P1v, P2v):
    f.point(P, TEXT, 3.8)
hollow(f, N1, BASE, 3.6)
hollow(f, N2, BASE, 3.6)
f.place(P1v, P1_, NAME, prefs=side(f, U1, 1) + side(f, U1, -1))
f.place(P2v, P2_, NAME, prefs=side(f, U2, 1) + side(f, U2, -1))
f.place(N1, N1_, NAME, BASE, prefs=ahead(f, vsub(N1, N2), (0, 30, -30, 60, -60)))
f.place(N2, N2_, NAME, BASE, prefs=ahead(f, vsub(N2, N1), (0, 30, -30, 60, -60)))
f.place(B, D1, NAME, THEORY, prefs=ahead(f, U1))
f.place(D, D2, NAME, PRACTICE, prefs=ahead(f, U2))
f.render(
    "aykiri-ornek",
    "Aykırı iki doğru: sayfada kesişiyormuş gibi görünseler de önde kalan doğru arkadakinin üzerinden "
    "geçer. En yakın noktaları <em>N</em><sub>1</sub>(15/7, 6/7, 16/7) ile "
    "<em>N</em><sub>2</sub>(16/7, 1/7, 13/7) arasındaki kesikli parça iki doğruya da diktir; uzunluğu "
    "&#8730;35/7&#8217;dir.",
    "Skew lines d1 through P1(1, 2, 0) with direction (1, -1, 2) and d2 through P2(0, -1, 3) with "
    "direction (2, 1, -1); the front one is drawn with a gap where they cross on the page; the dashed "
    "common perpendicular joins N1 and N2")


# ===========================================================================
# 11. uid-ortak-dikme: the common perpendicular and the position vectors
# ===========================================================================
# a clean generic scene: d1 low and parallel to Y, d2 high and horizontal,
# so the common perpendicular N1N2 is vertical and seen at full length
N1, N2 = (1.6, 2.2, 0.9), (1.6, 2.2, 3.0)
U1, U2 = (0, 1, 0), (1, -0.6, 0)
P1v, P2v = along(N1, U1, -2.2), along(N2, U2, -1.3)
A, B = seg(N1, U1, -2.9, 1.6)
C, D = seg(N2, U2, -2.0, 1.5)
ext = [O, A, B, C, D, (3.4, 0, 0), (0, 4.2, 0), (0, 0, 3.6)]
f = Fig(AZ11, EL11, ext, width=580, pad=70)
f.axes(((0, 3.4), (0, 4.2), (0, 3.6)), opacity=0.4, width=1.1)
f.arrow(O, N1, TEXT, 1.4, 10.0, "5 4", 0.75)
f.arrow(O, N2, TEXT, 1.4, 10.0, "5 4", 0.75)
f.arrow(O, P1v, REMARK, 2.0, 11.0)
f.arrow(O, P2v, REMARK, 2.0, 11.0)
two_lines(f, A, B, C, D)
f.line([N1, N2], BASE, 3.0)
f.right_angle(N1, U1, (0, 0, 1), 13)
f.right_angle(N2, vscale(-1, U2), (0, 0, -1), 13)
f.arrow(along(N1, U1, 0.35), along(N1, U1, 1.15), THEORY, 3.2, 12.0)
f.arrow(along(N2, U2, 0.3), along(N2, U2, 1.05), PRACTICE, 3.2, 12.0)
for P in (O, P1v, P2v, N1, N2):
    f.point(P, TEXT, 3.8)
f.place(O, it("O"), NAME, prefs=[200, 225, 250, 180])
f.place(P1v, P1_, NAME, prefs=side(f, U1, 1) + side(f, U1, -1))
f.place(P2v, P2_, NAME, prefs=side(f, U2, 1) + side(f, U2, -1))
f.place(N1, N1_, NAME, BASE, prefs=[315, 290, 340, 250])
f.place(N2, N2_, NAME, BASE, prefs=[45, 20, 70, 135])
for P, s_ in ((P1v, nm("u", "1")), (P2v, nm("u", "2")), (N1, nm("n", "1")), (N2, nm("n", "2"))):
    col = REMARK if P in (P1v, P2v) else TEXT
    f.place(vscale(0.62, P), s_, NAME, col, prefs=side(f, P, 1) + side(f, P, -1), d=5)
f.place(along(N1, U1, 1.15), V1, NAME, THEORY, prefs=side(f, U1, 1) + side(f, U1, -1), d=6)
f.place(along(N2, U2, 1.05), V2, NAME, PRACTICE, prefs=side(f, U2, 1) + side(f, U2, -1), d=6)
f.place(B, D1, NAME, THEORY, prefs=ahead(f, U1))
f.place(D, D2, NAME, PRACTICE, prefs=ahead(f, U2))
f.render(
    "ortak-dikme",
    "<em>N</em><sub>1</sub><em>N</em><sub>2</sub> ortak dikmesi <em>d</em><sub>1</sub>&#8217;e ve "
    "<em>d</em><sub>2</sub>&#8217;ye diktir. <em>u</em><sub>1</sub>, <em>u</em><sub>2</sub> doğrulardaki "
    "<em>P</em><sub>1</sub>, <em>P</em><sub>2</sub> noktalarının, <em>n</em><sub>1</sub>, "
    "<em>n</em><sub>2</sub> ise ayakların konum vektörleridir.",
    "Two skew lines d1 and d2 with direction arrows v1, v2, the common perpendicular N1N2 with "
    "right-angle marks, and position vectors u1, u2 to P1, P2 (solid) and n1, n2 to N1, N2 (dashed) "
    "drawn from the origin O")


# ===========================================================================
# 12. uid-en-kisa-pisagor: |XY|^2 = |N1N2|^2 + |w|^2
# ===========================================================================
N1, N2 = O, (0, 0, 2)
Xp, Yp, Xq = (2, 0, 0), (0, 1.5, 2), (2, 0, 2)
Wv = vsub(Yp, Xq)
assert vdot(Wv, (0, 0, 2)) == 0
A, B = seg(N1, (1, 0, 0), -0.9, 2.9)
C, D = seg(N2, (0, 1, 0), -1.0, 2.6)
ext = [A, B, C, D, (2.9, 2.6, 2), (-0.9, -1, 2)]
f = Fig(AZ12, EL12, ext, width=560, pad=70)
PL = [(-0.9, -1.0, 2), (2.9, -1.0, 2), (2.9, 2.6, 2), (-0.9, 2.6, 2)]
f.polygon(PL, BASE, 0.07, stroke=BASE, width=0.8, s_opacity=0.35, w=0.3)
two_lines(f, A, B, C, D)
f.line([N1, N2], BASE, 3.0)
f.line([Xp, Xq], TEXT, 1.4, None, 0.8)
f.line([Xq, Yp], REMARK, 1.8, None, 0.95)
f.line([Xp, Yp], TEXT, 1.8, "6 4", 0.95)
f.right_angle(Xq, (0, 0, -1), Wv, 12)
f.right_angle(N1, (1, 0, 0), (0, 0, 1), 11)
f.right_angle(N2, (0, 1, 0), (0, 0, -1), 11)
for P in (N1, N2, Xp, Yp):
    f.point(P, TEXT, 3.8)
hollow(f, Xq, TEXT, 3.8)
f.place(N1, N1_, NAME, BASE, prefs=[200, 225, 180, 250])
f.place(N2, N2_, NAME, BASE, prefs=[160, 135, 180, 110])
f.place(Xp, it("X"), NAME, prefs=[270, 250, 290, 225])
f.place(Yp, it("Y"), NAME, prefs=[90, 70, 110, 45])
f.place(Xq, it("X") + "&#8242;", NAME, prefs=[160, 135, 180, 110, 200])
f.place(vscale(0.5, vadd(Xp, Xq)), "|&#8201;" + N1_ + N2_ + "|", DESC, TEXT,
        prefs=side(f, (0, 0, 1), -1) + side(f, (0, 0, 1), 1))
f.place(vscale(0.5, vadd(Xq, Yp)), it("w"), NAME + 1, REMARK, prefs=side(f, Wv, 1) + side(f, Wv, -1))
f.place(B, D1, NAME, THEORY, prefs=ahead(f, (1, 0, 0)))
f.place(D, D2, NAME, PRACTICE, prefs=ahead(f, (0, 1, 0)))
f.render(
    "en-kisa-pisagor",
    "<em>X</em> &#8712; <em>d</em><sub>1</sub>, <em>Y</em> &#8712; <em>d</em><sub>2</sub> için "
    "<em>XY</em> vektörü, ortak dikmeye eşit <em>XX</em>&#8242; ile ona dik <em>w</em> = <em>X</em>&#8242;<em>Y</em> "
    "vektörlerinin toplamıdır. Pisagor bağıntısından |<em>XY</em>|&#178; = "
    "|<em>N</em><sub>1</sub><em>N</em><sub>2</sub>|&#178; + &#8214;<em>w</em>&#8214;&#178; "
    "&#8805; |<em>N</em><sub>1</sub><em>N</em><sub>2</sub>|&#178;.",
    "Skew lines d1 along X at height 0 and d2 along Y at height 2 with the common perpendicular N1N2; "
    "points X on d1 and Y on d2, the dashed segment XY, the segment XX' equal to N1N2 and the vector "
    "w from X' to Y in the faint plane z = 2, with a right angle at X'")


# ===========================================================================
# 13. uid-en-kisa-izdusum: projecting P1P2 onto v1 x v2 gives the distance 3
# ===========================================================================
P1v, U1 = (0, 2, -5), (2, -1, -2)
P2v, U2 = (-1, 2, 0), (4, -3, -5)
Nn = vcross(U1, U2)
N1, N2 = (2, 1, -7), (3, -1, -5)
F = vsub(P1v, Nn)
assert Nn == (-1, 2, -2) and F == (1, 0, -3)
assert vdot(vsub(P2v, F), Nn) == 0 and vnorm(vsub(F, P1v)) == 3
A, B = seg(P1v, U1, -0.5, 1.8)
C, D = seg(P2v, U2, -0.5, 1.8)
ext = [A, B, C, D, along(P1v, Nn, 0.7)]
f = Fig(AZ13, EL13, ext, width=560, pad=70)
two_lines(f, A, B, C, D, width=2.0)
f.line(seg(P1v, Nn, -1.3, 0.75), TEXT, 1.0, "2 3", 0.6)
f.line([N1, N2], BASE, 1.3, "5 4", 0.6)
f.line([P2v, F], TEXT, 1.3, "5 4", 0.85)
f.right_angle(F, Nn, vsub(P2v, F), 11)
f.line([P1v, F], BASE, 4.0)
f.arrow(P1v, along(P1v, Nn, 0.6), REMARK, 2.2, 11.0)
f.arrow(P1v, P2v, TEXT, 2.6, 12.0, halo=True)
for P in (P1v, P2v):
    f.point(P, TEXT, 3.8)
f.point(F, BASE, 3.4)
hollow(f, N1, BASE, 3.4)
hollow(f, N2, BASE, 3.4)
f.place(P1v, P1_, NAME, prefs=side(f, U1, 1) + side(f, U1, -1))
f.place(P2v, P2_, NAME, prefs=ahead(f, vsub(P2v, P1v)))
f.place(N1, N1_, NAME, BASE, prefs=ahead(f, vsub(N1, N2)), opacity=0.8)
f.place(N2, N2_, NAME, BASE, prefs=ahead(f, vsub(N2, N1)), opacity=0.8)
vec_label(f, vscale(0.5, vadd(P1v, P2v)), P1_ + P2_, TEXT, prefs=side(f, vsub(P2v, P1v), 1) + side(f, vsub(P2v, P1v), -1))
f.place(along(P1v, Nn, 0.6), V1 + " " + TIMES + " " + V2, NAME, REMARK, prefs=ahead(f, Nn))
f.place(vscale(0.5, vadd(P1v, F)), "3", NAME + 1, BASE, prefs=side(f, Nn, 1) + side(f, Nn, -1))
f.place(B, D1, NAME, THEORY, prefs=ahead(f, U1))
f.place(D, D2, NAME, PRACTICE, prefs=ahead(f, U2))
f.render(
    "en-kisa-izdusum",
    "<em>P</em><sub>1</sub><em>P</em><sub>2</sub> vektörünün <em>v</em><sub>1</sub> &#215; "
    "<em>v</em><sub>2</sub> doğrultusu üzerindeki izdüşümünün uzunluğu (kalın parça) 3&#8217;tür. "
    "Soluk kesikli <em>N</em><sub>1</sub><em>N</em><sub>2</sub> ortak dikmesi bu parçaya paraleldir ve "
    "onunla aynı uzunluktadır.",
    "Skew lines d1 through P1(0, 2, -5) and d2 through P2(-1, 2, 0), the vector P1P2, the direction "
    "v1 x v2 = (-1, 2, -2) at P1, the dashed drop from P2 onto that direction and the thick "
    "projection segment of length 3, with the faint common perpendicular N1N2")


# ===========================================================================
# 14. uid-ortak-dikme-ornek: the feet N1(2, 1, -7), N2(3, -1, -5)
# ===========================================================================
A, B = seg(P1v, U1, -0.5, 2)
C, D = seg(P2v, U2, -0.5, 2)
assert along(P1v, U1, 1) == N1 and along(P2v, U2, 1) == N2
ext = [A, B, C, D]
f = Fig(AZ14, EL14, ext, width=560, pad=80)
two_lines(f, A, B, C, D)
f.line([N1, N2], BASE, 3.4)
f.right_angle(N1, U1, vsub(N2, N1), 13)
f.right_angle(N2, U2, vsub(N1, N2), 13)
for P in (P1v, P2v):
    f.point(P, TEXT, 3.2)
for P in (N1, N2):
    f.point(P, BASE, 4.2)
f.place(P1v, P1_, NAME, prefs=side(f, U1, 1) + side(f, U1, -1), opacity=0.85)
f.place(P2v, P2_, NAME, prefs=side(f, U2, 1) + side(f, U2, -1), opacity=0.85)
f.place(N1, N1_ + triple(2, 1, -7), NAME, BASE, prefs=ahead(f, vsub(N1, N2), (0, 30, -30, 60, -60)))
f.place(N2, N2_ + triple(3, -1, -5), NAME, BASE, prefs=ahead(f, vsub(N2, N1), (0, 30, -30, 60, -60)))
f.place(vscale(0.5, vadd(N1, N2)), "|&#8201;" + N1_ + N2_ + "| = 3", NAME, BASE,
        prefs=side(f, vsub(N2, N1), 1) + side(f, vsub(N2, N1), -1), d=9)
f.place(B, D1, NAME, THEORY, prefs=ahead(f, U1))
f.place(D, D2, NAME, PRACTICE, prefs=ahead(f, U2))
f.render(
    "ortak-dikme-ornek",
    "Aykırı <em>d</em><sub>1</sub> ve <em>d</em><sub>2</sub> doğrularının ortak dikmesi "
    "<em>N</em><sub>1</sub>(2, 1, &#8722;7) ile <em>N</em><sub>2</sub>(3, &#8722;1, &#8722;5) arasındadır; "
    "iki doğruya da diktir ve uzunluğu 3&#8217;tür.",
    "Skew lines d1 through P1(0, 2, -5) with direction (2, -1, -2) and d2 through P2(-1, 2, 0) with "
    "direction (4, -3, -5); the thick common perpendicular from N1(2, 1, -7) to N2(3, -1, -5) with "
    "right-angle marks at both feet")


# ===========================================================================
# 15. uid-paralellik-parametresi: m = 4, n = 8 give parallel distinct lines
# ===========================================================================
P1v, U1 = (1, -2, 3), (3, 4, 4)
P2v, U2 = (2, 3, -1), (6, 8, 8)
assert vcross(U1, U2) == (0, 0, 0) and vcross(vsub(P2v, P1v), U1) != (0, 0, 0)
A, B = seg(P1v, U1, -0.7, 0.8)
C, D = seg(P2v, U2, -0.35, 0.45)
ext = [A, B, C, D, O, (4, 0, 0), (0, 5, 0), (0, -3, 0), (0, 0, 6), (0, 0, -3)]
f = Fig(AZ15, EL15, ext, width=560, pad=70)
f.axes(((0, 4), (-3, 5), (-3, 6)), opacity=0.4, width=1.1)
two_lines(f, A, B, C, D)
k = 0.25
f.arrow(along(P1v, U1, -0.35), along(P1v, U1, -0.35 + k), THEORY, 3.4, 12.0)
f.arrow(along(P2v, U2, -0.3), along(P2v, U2, -0.3 + k), PRACTICE, 3.4, 12.0)
for P in (P1v, P2v):
    f.point(P, TEXT, 3.8)
f.place(O, it("O"), NAME, prefs=[200, 225, 180, 250])
f.place(P1v, P1_, NAME, prefs=side(f, U1, -1) + side(f, U1, 1))
f.place(P2v, P2_, NAME, prefs=side(f, U1, 1) + side(f, U1, -1))
f.place(along(P1v, U1, -0.35 + k / 2), V1 + " = " + triple(3, 4, 4), DESC + 0.5, THEORY,
        prefs=side(f, U1, -1) + side(f, U1, 1), d=8)
f.place(along(P2v, U2, -0.3 + k / 2), V2 + " = " + triple(6, 8, 8), DESC + 0.5, PRACTICE,
        prefs=side(f, U1, 1) + side(f, U1, -1), d=8)
f.place(B, D1, NAME, THEORY, prefs=ahead(f, U1))
f.place(D, D2, NAME, PRACTICE, prefs=ahead(f, U1))
f.render(
    "paralellik-parametresi",
    "<em>m</em> = 4, <em>n</em> = 8 için <em>d</em><sub>1</sub> ile <em>d</em><sub>2</sub> paralel ve "
    "farklıdır: <em>v</em><sub>2</sub> = 2<em>v</em><sub>1</sub>, ama <em>P</em><sub>2</sub> "
    "<em>d</em><sub>1</sub> üzerinde değildir. Oklar, doğrultman vektörlerinin aynı oranda kısaltılmış "
    "hâlleridir.",
    "Two parallel lines d1 through P1(1, -2, 3) and d2 through P2(2, 3, -1) with arrows along v1 = "
    "(3, 4, 4) and v2 = (6, 8, 8), the second twice as long")


# ===========================================================================
# 16. uid-kesisim-alistirma: the lines meet far away at K(-19, 12, 44)
# ===========================================================================
P1v, U1 = (3, 1, 0), (-2, 1, 4)
P2v, U2 = (1, 0, -4), (5, -3, -12)
K = (-19, 12, 44)
assert along(P1v, U1, 11) == K and along(P2v, U2, -4) == K
A, B = seg(P1v, U1, -1, 12)
C, D = seg(P2v, U2, -4.5, 0.5)
ext = [A, B, C, D, O, (5, 0, 0), (0, 5, 0), (0, 0, 5)]
f = Fig(AZ16, EL16, ext, width=560, pad=70)
f.axes(((0, 5), (0, 5), (0, 5)), opacity=0.45, width=1.1)
two_lines(f, A, B, C, D)
for P in (P1v, P2v, K):
    f.point(P, TEXT, 3.8)
f.place(O, it("O"), NAME, prefs=[200, 225, 180, 250, 160])
f.place(P1v, P1_, NAME, prefs=side(f, U1, 1) + side(f, U1, -1))
f.place(P2v, P2_, NAME, prefs=side(f, U2, -1) + side(f, U2, 1))
f.place(K, it("K") + triple(-19, 12, 44), NAME, prefs=side(f, U1, 1) + side(f, U1, -1))
f.place(A, D1, NAME, THEORY, prefs=ahead(f, vscale(-1, U1)))
f.place(D, D2, NAME, PRACTICE, prefs=ahead(f, U2))
f.render(
    "kesisim-alistirma",
    "<em>d</em><sub>1</sub> ile <em>d</em><sub>2</sub> <em>K</em>(&#8722;19, 12, 44) noktasında kesişir. "
    "Doğrultman vektörleri neredeyse paralel olduğundan doğrular kesişim noktasına çok yavaş yaklaşır; "
    "eksenler başlangıç noktası çevresinde, ölçek için çizilmiştir.",
    "Two lines through P1(3, 1, 0) with direction (-2, 1, 4) and P2(1, 0, -4) with direction "
    "(5, -3, -12) converging to their common point K(-19, 12, 44), with short axes at the origin")


# ===========================================================================
# 17. uid-en-kisa-alistirma: feet N1(1/7, 2/7, 1), N2(19/21, -2/21, 17/21)
# ===========================================================================
P1v, U1 = (0, 0, 1), (2, 4, 0)
P2v, U2 = (3, 2, 5), (2, 2, 4)
N1 = (1 / 7, 2 / 7, 1)
N2 = (19 / 21, -2 / 21, 17 / 21)
assert close(along(P1v, U1, 1 / 14), N1) and close(along(P2v, U2, -22 / 21), N2)
assert abs(vdot(vsub(N2, N1), U1)) < 1e-12 and abs(vdot(vsub(N2, N1), U2)) < 1e-12
A17, B17 = seg(P1v, U1, -0.4, 0.8)
C17, D17 = seg(P2v, U2, -1.6, 0.2)
EXT17 = [A17, B17, C17, D17, O, (3.6, 0, 0), (0, 3.6, 0), (0, 0, 3.4), (-1, 0, 0), (0, -1.6, 0)]


def skew17(f, fade=1.0):
    f.axes(((-1, 3.6), (-1.6, 3.6), (0, 3.4)), opacity=0.35 * fade + 0.05, width=1.0)
    two_lines(f, A17, B17, C17, D17, width=2.2)
    f.right_angle(N1, U1, vsub(N2, N1), 11)
    f.right_angle(N2, U2, vsub(N1, N2), 11)


f = Fig(AZ17, EL17, EXT17, width=560, pad=70)
skew17(f)
f.line([N1, N2], BASE, 3.4)
for P in (P1v, P2v):
    f.point(P, TEXT, 3.2)
for P in (N1, N2):
    f.point(P, BASE, 4.0)
f.place(P1v, P1_, NAME, prefs=side(f, U1, 1) + side(f, U1, -1), opacity=0.85)
f.place(P2v, P2_, NAME, prefs=side(f, U2, 1) + side(f, U2, -1), opacity=0.85)
f.place(N1, N1_, NAME, BASE, prefs=ahead(f, vsub(N1, N2), (0, 30, -30, 60, -60, 90, -90)))
f.place(N2, N2_, NAME, BASE, prefs=ahead(f, vsub(N2, N1), (0, 30, -30, 60, -60, 90, -90)))
f.place(vscale(0.5, vadd(N1, N2)), "4" + SQRT + "21/21", DESC + 0.5, BASE,
        prefs=[200, 215, 185, 230, 170], d=9, far=(6, 13, 22, 34, 48), leader=True)
f.place(B17, D1, NAME, THEORY, prefs=ahead(f, U1))
f.place(C17, D2, NAME, PRACTICE, prefs=ahead(f, vscale(-1, U2)))
f.render(
    "en-kisa-alistirma",
    "Aykırı <em>d</em><sub>1</sub> ve <em>d</em><sub>2</sub> doğrularının ortak dikmesinin ayakları "
    "<em>N</em><sub>1</sub>(1/7, 2/7, 1) ve <em>N</em><sub>2</sub>(19/21, &#8722;2/21, 17/21); "
    "aralarındaki uzaklık 4&#8730;21/21 &#8776; 0,87&#8217;dir.",
    "Skew lines d1 in the plane z = 1 through P1(0, 0, 1) with direction (2, 4, 0) and d2 through "
    "P2(3, 2, 5) with direction (2, 2, 4); the thick common perpendicular N1N2 with right-angle marks")


# ===========================================================================
# 18. uid-ortak-dikme-dogrusu: the line through N1 and N2
# ===========================================================================
Wd = (4, -2, -1)
assert close(along(N1, Wd, 4 / 21), N2)
f = Fig(AZ17, EL17, EXT17 + seg(N1, Wd, -0.45, 0.65), width=560, pad=70)
f.axes(((-1, 3.6), (-1.6, 3.6), (0, 3.4)), opacity=0.25, width=1.0)
E, G = seg(N1, Wd, -0.45, 0.65)
fr = crossing_front(f, A17, B17, C17, D17)
order = [(A17, B17, THEORY), (C17, D17, PRACTICE)]
if fr:
    order.reverse()
for k_, (X0, X1, col) in enumerate(order):
    sline(f, X0, X1, col, 1.8, 0.55, halo=k_ == 1)
sline(f, E, G, BASE, 3.0, halo=True)
f.right_angle(N1, U1, Wd, 11)
f.right_angle(N2, U2, vscale(-1, Wd), 11)
for P in (N1, N2):
    f.point(P, BASE, 4.0)
f.place(N1, N1_, NAME, BASE, prefs=side(f, Wd, 1) + side(f, Wd, -1))
f.place(N2, N2_, NAME, BASE, prefs=side(f, Wd, -1) + side(f, Wd, 1))
f.place(G, "ortak dikme", DESC + 0.5, BASE, prefs=ahead(f, Wd))
f.place(B17, D1, NAME, THEORY, prefs=ahead(f, U1), opacity=0.8)
f.place(C17, D2, NAME, PRACTICE, prefs=ahead(f, vscale(-1, U2)), opacity=0.8)
f.render(
    "ortak-dikme-dogrusu",
    "<em>N</em><sub>1</sub> ve <em>N</em><sub>2</sub>&#8217;den geçen ortak dikme doğrusu; doğrultman "
    "vektörü (4, &#8722;2, &#8722;1), <em>v</em><sub>1</sub> &#215; <em>v</em><sub>2</sub>&#8217;ye paraleldir "
    "ve doğru iki doğruyu da dik keser.",
    "The faint skew lines d1 and d2 of the previous exercise and, in color, the common perpendicular "
    "line through N1 and N2 with direction (4, -2, -1), with right-angle marks at both feet")


# ---------------------------------------------------------------------------
for name, content in OUT.items():
    path = OUT_DIR / f"analytic-uid-{name}.md"
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(content)
    print("wrote", path.name)
