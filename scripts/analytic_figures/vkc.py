# -*- coding: utf-8 -*-
"""Figures for dersler/analitik-geometri/vektorel-ve-karma-carpim.qmd (chapter key: vkc).

Three-dimensional drawings go through scripts/svg_plot3.py (an orthographic
Camera on an equal-aspect svg_plot.Plot panel); the three plane drawings use
svg_plot.Plot directly. The figures go INSIDE the box they explain (example,
solution, proof), never inside a definition box.

Labels are placed after the projection, in page pixels: `Canvas.place` tries
a ring of candidate positions around the anchor and keeps the cheapest one,
i.e. the one that touches no registered line, point or earlier label.

Usage:   python scripts/analytic_figures/vkc.py
         python scripts/center_figures.py "analytic-vkc-*.md" --keep-width
Output:  scripts/_figures/analytic-vkc-<name>.md
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

TALL_SCENES = {"sag-el-kurali", "ucgen-ornek", "duzlemde-alan"}
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


class Flat(Canvas):
    """A plane drawing on an equal-aspect Plot panel, with the same label registry."""

    def __init__(self, xr, yr, width=520, pad=40):
        super().__init__()
        self.ppu = width / (xr[1] - xr[0])
        h = (yr[1] - yr[0]) * self.ppu
        self.p = Plot(pad, pad, width, h, xr, yr)
        self.W, self.H = width + 2 * pad, h + 2 * pad

    def px(self, P):
        return (self.p.X(P[0]), self.p.Y(P[1]))

    def anchor_px(self, anchor):
        if isinstance(anchor, tuple) and anchor and anchor[0] == "px":
            return anchor[1], anchor[2]
        return self.px(anchor)

    def u(self, pixels):
        return pixels / self.ppu

    def line(self, pts, color=TEXT, width=1.6, dash=None, opacity=1.0, w=1.0):
        self.p.line(pts, color, width, dash, opacity)
        if w:
            self.reg_px([self.px(P) for P in pts], w)

    def arrow(self, P0, P1, color=THEORY, width=2.6, head=12.0, dash=None, opacity=1.0, w=1.0):
        self.p.arrow(P0, P1, color, width, head, dash, opacity)
        if w:
            self.reg_px([self.px(P0), self.px(P1)], w)

    def point(self, P, color=TEXT, r=3.8):
        self.p.points([P], color, r)
        x, y = self.px(P)
        self.dots.append((x, y, r))

    def arc(self, C, a0, a1, r_px, color=TEXT, width=1.3, opacity=0.9, n=40, w=0.6):
        r = self.u(r_px)
        pts = [(C[0] + r * math.cos(a0 + (a1 - a0) * k / n), C[1] + r * math.sin(a0 + (a1 - a0) * k / n))
               for k in range(n + 1)]
        self.line(pts, color, width, None, opacity, w)
        return pts

    def render(self, name, caption, aria, css="ders-grafik"):
        print(f"-- {name} (warnings above belong to it)")
        for t in self.emit_texts():
            self.p.add(t)
        OUT[name] = figure(round(self.W), round(self.H), [self.p], caption, css, aria)


def ahead(f, vec, spread=(0, 30, -30, 60, -60, 90, -90)):
    """Label angles around the page direction of vec: first straight past the tip."""
    a = f.sang(vec)
    return [a + s for s in spread]


def box_edges(f, P0, a, b, c):
    """Edges of the parallelepiped P0 + [0,1]a + [0,1]b + [0,1]c, each with a visibility
    flag: an edge is hidden when both faces meeting at it turn away from the viewer."""
    vecs = (a, b, c)
    vol = vdot(vcross(a, b), c)

    def corner(ijk):
        P = P0
        for t, v in zip(ijk, vecs):
            if t:
                P = vadd(P, v)
        return P

    def face_front(axis, side):
        p, q = [vecs[t] for t in range(3) if t != axis]
        n = vcross(p, q)
        if vdot(n, vecs[axis]) < 0:
            n = vscale(-1.0, n)                   # n now points to the side 1 face's outside
        if not side:
            n = vscale(-1.0, n)
        return vdot(n, f.d) > 0

    out = []
    for ax in range(3):
        o1, o2 = [t for t in range(3) if t != ax]
        for s1 in (0, 1):
            for s2 in (0, 1):
                i0, i1 = [0, 0, 0], [0, 0, 0]
                i0[o1] = i1[o1] = s1
                i0[o2] = i1[o2] = s2
                i1[ax] = 1
                vis = face_front(o1, s1) or face_front(o2, s2)
                out.append((corner(i0), corner(i1), vis, (tuple(i0), tuple(i1))))
    assert abs(vol) > 1e-9
    return out


# ===========================================================================
# 1. vkc-standart-baz: e1 x e2 = e3 and its cyclic shifts
# ===========================================================================
E1, E2, E3 = (1.0, 0, 0), (0, 1.0, 0), (0, 0, 1.0)
assert close(vcross(E1, E2), E3) and close(vcross(E2, E3), E1) and close(vcross(E3, E1), E2)

C0 = (1 / 3, 1 / 3, 1 / 3)
RC = math.sqrt(2 / 3)
A1 = vunit(vsub(E1, C0))
A2 = vcross(vunit((1, 1, 1)), A1)


def loop(t):
    return vadd(C0, vadd(vscale(RC * math.cos(t), A1), vscale(RC * math.sin(t), A2)))


assert close(loop(2 * math.pi / 3), E2, 1e-9) and close(loop(4 * math.pi / 3), E3, 1e-9)

ext = [O, (1.4, 0, 0), (0, 1.4, 0), (0, 0, 1.4)] + [loop(2 * math.pi * k / 60) for k in range(60)]
f = Fig(45, 20, ext, width=470, pad=90)
f.axes(((0, 1.4), (0, 1.4), (0, 1.4)))
gap = 17 / (RC * f.ppu)
for k in range(3):
    t0, t1 = 2 * math.pi * k / 3 + gap, 2 * math.pi * (k + 1) / 3 - gap
    pts = [loop(t0 + (t1 - t0) * j / 60) for j in range(61)]
    f.line(pts[:-2], REMARK, 1.6, None, 0.95)
    f.S.arrow(pts[-5], pts[-1], REMARK, 1.6, 10.0, None, 0.95)
    f._reg(pts[-5:], 1.0)
for e, col in ((E1, THEORY), (E2, BASE), (E3, PRACTICE)):
    f.arrow(O, e, col, 3.2, 13.0)
f.point(O, TEXT, 3.4)
f.place(O, it("O"), NAME, prefs=[270, 250, 290])
for k, (e, col) in enumerate(((E1, THEORY), (E2, BASE), (E3, PRACTICE))):
    a = f.sang(e)
    name_side = {0: a - 50, 1: a + 50, 2: a + 50}[k]
    prod_side = {0: a + 55, 1: a - 55, 2: a - 50}[k]
    f.place(e, e_(k + 1, NAME + 1), NAME + 1, col, prefs=[name_side, name_side + 15, name_side - 15], d=9)
    i, j = [(2, 3), (3, 1), (1, 2)][k]
    f.place(e, x_(e_(i, DESC), e_(j, DESC)) + " = " + e_(k + 1, DESC), DESC, TEXT,
            prefs=[prod_side, prod_side - 15, prod_side + 15], d=12)
f.render(
    "standart-baz",
    "Standart baz vektörleri ve döngü: <em>e</em><sub>1</sub> &#8594; <em>e</em><sub>2</sub> &#8594; "
    "<em>e</em><sub>3</sub> &#8594; <em>e</em><sub>1</sub> sırasında ardışık iki vektörün vektörel "
    "çarpımı döngüdeki bir sonraki vektördür; her yazı, sonucu olan vektörün ucunun yanındadır.",
    "Unit vectors e1, e2, e3 along the X, Y, Z axes with a circular arrow through their tips "
    "e1 to e2 to e3 to e1, and the products e1 x e2 = e3, e2 x e3 = e1, e3 x e1 = e2")


# ===========================================================================
# 2. vkc-ilk-ornek: u = (1, 2, 3), v = (4, 5, 6), u x v = (-3, 6, -3)
# ===========================================================================
Uv, Vv = (1, 2, 3), (4, 5, 6)
N = vcross(Uv, Vv)
assert N == (-3, 6, -3) and vdot(N, Uv) == 0 and vdot(N, Vv) == 0
UpV = vadd(Uv, Vv)
ext = [O, (5, 0, 0), (-4, 0, 0), (0, 7, 0), (0, -1, 0), (0, 0, 7), (0, 0, -4), UpV, N]
f = Fig(20, 18, ext, width=540, pad=80)
PL = [O, Uv, UpV, Vv]
f.add_occluder(PL)
f.axes(((-4, 5), (-1, 7), (-4, 7)))
f.polygon(PL, THEORY, 0.13, stroke=THEORY, width=1.0, s_opacity=0.55)
f.arrow(O, Vv, BASE, 2.8, 13.0)
f.arrow(O, Uv, THEORY, 2.8, 13.0)
f.arrow(O, N, PRACTICE, 3.4, 14.0, halo=True)
f.right_angle(O, N, Uv, 15, TEXT)
f.right_angle(O, N, Vv, 26, TEXT)
f.point(O, TEXT, 3.4)
f.place(O, it("O"), NAME, prefs=[200, 180, 225])
f.place(Uv, U_ + " = " + triple(1, 2, 3), NAME, THEORY, prefs=ahead(f, Uv, (90, 60, 120, 30)))
f.place(Vv, V_ + " = " + triple(4, 5, 6), NAME, BASE, prefs=ahead(f, Vv, (-90, -60, -30, 0)))
f.place(N, UxV + " = " + triple(-3, 6, -3), NAME, PRACTICE, prefs=ahead(f, N, (-120, -100, -140, 90)))
f.render(
    "ilk-ornek",
    "<em>u</em> = (1, 2, 3) ve <em>v</em> = (4, 5, 6) vektörlerinin gerdiği paralelkenar ve "
    "<em>u</em> &#215; <em>v</em> = (&#8722;3, 6, &#8722;3). Vektörel çarpım hem <em>u</em>&#8217;ya "
    "hem <em>v</em>&#8217;ye diktir, yani iki vektörün düzlemine diktir.",
    "Vectors u = (1, 2, 3) and v = (4, 5, 6) from the origin, the parallelogram they span, and "
    "u x v = (-3, 6, -3) perpendicular to both, with right-angle marks")


# ===========================================================================
# 3. vkc-uclu-ozdeslik: u x (v x w) = 3v - 2w for u = (1,1,2), v = (2,0,0), w = (1,2,0)
# ===========================================================================
Uv, Vv, Wv = (1, 1, 2), (2, 0, 0), (1, 2, 0)
VxW = vcross(Vv, Wv)
R = vcross(Uv, VxW)
assert VxW == (0, 0, 4) and R == (4, -4, 0)
assert vdot(Uv, Wv) == 3 and vdot(Uv, Vv) == 2
V3, W2 = vscale(3, Vv), vscale(-2, Wv)
assert close(vadd(V3, W2), R)
ext = [(-1, -5, 0), (7, -5, 0), (7, 3, 0), (-1, 3, 0), (0, 0, 4.8)]
f = Fig(22, 30, ext, width=560, pad=80)
f.polygon([(-1, -5, 0), (6, -5, 0), (6, 3, 0), (-1, 3, 0)], TEXT, 0.05, stroke=TEXT, width=0.8,
          s_opacity=0.3, w=0.3)
f.axes(((-1, 7), (-5, 3), (0, 4.8)))
f.polygon([O, V3, R, W2], PRACTICE, 0.06)
f.line([V3, R], PRACTICE, 1.2, "5 4", 0.8)
f.line([W2, R], PRACTICE, 1.2, "5 4", 0.8)
f.arrow(O, V3, THEORY, 1.5, 10.0, "6 4", 0.9)
f.arrow(O, W2, BASE, 1.5, 10.0, "6 4", 0.9)
f.arrow(O, R, PRACTICE, 3.4, 14.0)
f.arrow(O, Wv, BASE, 2.8, 13.0)
f.arrow(O, Vv, THEORY, 2.8, 13.0)
f.arrow(O, VxW, REMARK, 2.8, 13.0)
f.line([Uv, (1, 1, 0)], TEXT, 1.0, "4 3", 0.5, w=0.5)
f.arrow(O, Uv, TEXT, 2.8, 13.0, halo=True)
f.point(O, TEXT, 3.4)
f.place(O, it("O"), NAME, prefs=[285, 300, 270])
f.place(Vv, V_, NAME + 1, THEORY, prefs=[f.sang(Vv) + 90, f.sang(Vv) - 90])
f.place(V3, "3" + V_, NAME, THEORY, prefs=[f.sang(Vv) - 90, f.sang(Vv) + 90])
f.place(Wv, W_, NAME + 1, BASE, prefs=ahead(f, Wv))
f.place(W2, MINUS + "2" + W_, NAME, BASE, prefs=ahead(f, W2))
f.place(VxW, x_(V_, W_) + " = " + triple(0, 0, 4), NAME, REMARK, prefs=[0, 20, -20])
f.place(Uv, U_ + " = " + triple(1, 1, 2), NAME, TEXT, prefs=ahead(f, Uv))
f.place(R, x_(U_, "(" + x_(V_, W_) + ")") + " = 3" + V_ + " " + MINUS + " 2" + W_, NAME, PRACTICE,
        prefs=ahead(f, R, (-90, 90, 0)))
f.place((6, 3, 0), it("XY") + " düzlemi", DESC, TEXT, prefs=[0, 45, 315], opacity=0.8)
f.render(
    "uclu-ozdeslik",
    "<em>u</em> &#215; (<em>v</em> &#215; <em>w</em>) = (4, &#8722;4, 0), <em>XY</em> düzleminde kalır: "
    "3<em>v</em> ile &#8722;2<em>w</em> üzerine kurulan kesikli paralelkenarın köşegenidir, yani "
    "3<em>v</em> &#8722; 2<em>w</em>&#8217;ye eşittir. <em>v</em> &#215; <em>w</em> = (0, 0, 4) ise "
    "düzleme diktir.",
    "The XY plane with v = (2, 0, 0), w = (1, 2, 0), v x w = (0, 0, 4) along Z, u = (1, 1, 2), and "
    "u x (v x w) = (4, -4, 0) as the diagonal of the dashed parallelogram on 3v and -2w")


# ===========================================================================
# 4. vkc-dik-birim: unit vectors perpendicular to u = (2,-1,1) and v = (1,1,-1)
# ===========================================================================
Uv, Vv = (2, -1, 1), (1, 1, -1)
N = vcross(Uv, Vv)
assert N == (0, 3, 3) and vadd(Uv, Vv) == (3, 0, 0) and vdot(Uv, Vv) == 0
N1 = vunit(N)
N2 = vscale(-1, N1)
ext = [O, (3.7, 0, 0), (-1, 0, 0), (0, 3, 0), (0, -2, 0), (0, 0, 3.5), (0, 0, -2), Uv, Vv, N]
f = Fig(50, 17, ext, width=540, pad=80)
assert f.front(N)
PL = [O, Uv, vadd(Uv, Vv), Vv]
f.add_occluder(PL)
f.axes(((-1, 3.7), (-2, 3), (-2, 3.5)))
f.arrow(O, N2, TEXT, 2.4, 12.0, "5 3", 0.85)
f.polygon(PL, THEORY, 0.14, stroke=THEORY, width=1.0, s_opacity=0.55)
f.arrow(O, Uv, THEORY, 2.8, 13.0)
f.arrow(O, Vv, BASE, 2.8, 13.0)
f.arrow(O, N, PRACTICE, 3.0, 14.0, halo=True)
f.arrow(O, N1, TEXT, 3.8, 13.0)
f.right_angle(O, N, Uv, 16, TEXT)
f.point(O, TEXT, 3.4)
f.place(O, it("O"), NAME, prefs=[120, 135, 100])
f.place(Uv, U_ + " = " + triple(2, -1, 1), NAME, THEORY, prefs=ahead(f, Uv))
f.place(Vv, V_ + " = " + triple(1, 1, -1), NAME, BASE, prefs=ahead(f, Vv))
f.place(N, UxV + " = " + triple(0, 3, 3), NAME, PRACTICE, prefs=ahead(f, N, (-60, -90, 0, 60, 90)))
h2 = SQRT + "2/2"
f.place(N1, triple(0, h2, h2), DESC, TEXT, prefs=[f.sang(N) - 90, f.sang(N) - 60, f.sang(N) + 90],
        d=9, far=(10, 18, 26, 36), leader=True)
f.place(N2, triple(0, MINUS + h2, MINUS + h2), DESC, TEXT,
        prefs=[f.sang(N) + 90, f.sang(N) + 120, f.sang(N) - 90], d=9, far=(10, 18, 26, 36), leader=True)
f.render(
    "dik-birim",
    "<em>u</em> = (2, &#8722;1, 1) ile <em>v</em> = (1, 1, &#8722;1) vektörlerinin düzlemi ve ona dik "
    "<em>u</em> &#215; <em>v</em> = (0, 3, 3). Bu doğrultudaki iki birim vektör "
    "(0, &#8730;2/2, &#8730;2/2) ve düzlemin arkasına düşen, kesikli çizilen "
    "(0, &#8722;&#8730;2/2, &#8722;&#8730;2/2)&#8217;dir.",
    "Vectors u = (2, -1, 1) and v = (1, 1, -1), the rectangle they span, u x v = (0, 3, 3) with a "
    "right-angle mark, and the two unit normals (0, r, r) and (0, -r, -r) with r = sqrt(2)/2")


# ===========================================================================
# 5. vkc-sag-el-kurali: u = (2,1,0), v = (0,2,0), u x v = (0,0,4), v x u = (0,0,-4)
# ===========================================================================
Uv, Vv = (2, 1, 0), (0, 2, 0)
N = vcross(Uv, Vv)
assert N == (0, 0, 4) and vcross(Vv, Uv) == (0, 0, -4)
AZ5, EL5 = 35, 30
cam5 = Camera(AZ5, EL5)
KR = vadd(vscale(3.9, cam5.r), (0, 0, 0.6))          # foot of the right-hand sign
RF, ZF, TH = 0.75, 0.55, 2.3                        # finger ring radius and height, thumb length
ext = [O, (3, 0, 0), (0, 3, 0), (0, 0, 4.5), (0, 0, -4.5), (2, 3, 0), vadd(KR, (0, 0, TH)),
       vadd(KR, vscale(RF, cam5.r)), vadd(KR, vscale(-RF, cam5.r))]
f = Fig(AZ5, EL5, ext, width=520, pad=80)
PL = [O, Uv, (2, 3, 0), Vv]
f.add_occluder(PL)
f.axes(((0, 3), (0, 3), (-4.5, 4.5)))
f.arrow(O, (0, 0, -4), PRACTICE, 2.2, 12.0, "7 5", 0.9, halo=True)
f.polygon(PL, THEORY, 0.14, stroke=THEORY, width=1.0, s_opacity=0.55)
f.arrow(O, Uv, THEORY, 2.8, 13.0)
f.arrow(O, Vv, BASE, 2.8, 13.0)
a0, a1 = math.atan2(1, 2), math.pi / 2
rr = 1.0
turn = [(rr * math.cos(a0 + (a1 - a0) * k / 40), rr * math.sin(a0 + (a1 - a0) * k / 40), 0) for k in range(41)]
f.line(turn[3:-3], REMARK, 1.8, None, 1.0)
f.S.arrow(turn[-8], turn[-2], REMARK, 1.8, 10.0)
f._reg(turn[-8:], 1.0)
f.arrow(O, N, PRACTICE, 3.4, 14.0, halo=True)
f.point(O, TEXT, 3.4)
f.place(O, it("O"), NAME, prefs=[180, 200, 160])
f.place(Uv, U_, NAME + 1, THEORY, prefs=ahead(f, Uv))
f.place(Vv, V_, NAME + 1, BASE, prefs=ahead(f, Vv))
f.place((1.25, 2.05, 0), U_ + "&#8217;dan " + V_ + "&#8217;ye dönüş", DESC, REMARK, prefs=["c"])
f.place((0, 0, 4), UxV + " = " + triple(0, 0, 4), NAME, PRACTICE, prefs=[0, 10, 350], d=10)
f.place((0, 0, -4), x_(V_, U_) + " = " + MINUS + "(" + UxV + ")", NAME, PRACTICE, prefs=[0, 10, 350],
        d=10)
# the right-hand sign: thumb along u x v, the four fingers curling the way u turns toward v
# (counterclockwise seen from above, i.e. to the page right on the side facing us)
ring = [vadd(KR, (RF * math.cos(t), RF * math.sin(t), ZF))
        for t in (math.radians(AZ5 + 120 + 300 * j / 150) for j in range(151))]
back = [P for P in ring if vdot(vsub(P, KR), f.d) < 0]
front = [P for P in ring if vdot(vsub(P, KR), f.d) >= 0]
assert ring.index(front[0]) > ring.index(back[-1])      # one back run, then one front run
f.line(back, REMARK, 2.4, None, 0.45)
f.arrow(vadd(KR, (0, 0, 0.3)), vadd(KR, (0, 0, TH)), PRACTICE, 6.0, 17.0, halo=True)
f.S.line(front[:-5], BG, 6.4)
f.line(front[:-5], REMARK, 2.4, None, 1.0)
f.S.arrow(front[-9], front[-1], REMARK, 2.4, 12.0)
f._reg(front[-9:], 1.0)
f.place(vadd(KR, (0, 0, TH)), "başparmak", DESC, PRACTICE, prefs=[0, 20, 340], d=8)
f.place(front[len(front) // 3], "dört parmak", DESC, REMARK, prefs=[225, 250, 200], d=8)
f.render(
    "sag-el-kurali",
    "Sağ el kuralı: sağ elin dört parmağı <em>u</em>&#8217;dan <em>v</em>&#8217;ye doğru kıvrıldığında "
    "başparmak <em>u</em> &#215; <em>v</em> = (0, 0, 4)&#8217;ün yönünü gösterir (sağdaki şema). "
    "Çarpanların sırası değişince sonuç ters yöne döner: <em>v</em> &#215; <em>u</em> = (0, 0, &#8722;4).",
    "Vectors u = (2, 1, 0) and v = (0, 2, 0) in the XY plane with their parallelogram, a curved arrow "
    "turning u toward v, u x v = (0, 0, 4) up, v x u = (0, 0, -4) dashed down, and a right-hand "
    "sign: thumb up, the four fingers curling the same way")


# ===========================================================================
# 6. vkc-paralelkenar-alani (plane): area = |u| h, h = |v| sin(theta)
# ===========================================================================
A, B, D, C, H = (0, 0), (5, 0), (1.6, 2.8), (6.6, 2.8), (1.6, 0)
f = Flat((-0.9, 7.5), (-0.75, 3.4), width=520)
f.p.polygon([A, B, C, D], THEORY, 0.12)
f.line([B, C], TEXT, 1.2, "5 4", 0.7)
f.line([D, C], TEXT, 1.2, "5 4", 0.7)
f.line([D, H], TEXT, 1.2, "5 4", 0.8)
s = f.u(12)
f.line([(H[0] + s, 0), (H[0] + s, s), (H[0], s)], TEXT, 1.1, None, 0.85, w=0.5)
tv = math.atan2(D[1], D[0])
f.arc(A, 0, tv, 34, TEXT, 1.3)
f.arrow(A, B, THEORY, 2.8, 13.0)
f.arrow(A, D, BASE, 2.8, 13.0)
for P in (A, B, C, D, H):
    f.point(P, TEXT, 3.4)
rt = f.u(50)
f.place((rt * math.cos(tv / 2), rt * math.sin(tv / 2)), it(THETA), NAME, prefs=["c"], only=True)
f.place(A, it("A"), NAME, prefs=[225, 200, 250], only=True)
f.place(B, it("B"), NAME, prefs=[315, 340, 290], only=True)
f.place(C, it("C"), NAME, prefs=[45, 20, 70], only=True)
f.place(D, it("D"), NAME, prefs=[135, 160, 110], only=True)
f.place(H, it("H"), NAME, prefs=[270, 250], only=True)
f.place((3.4, 0), U_, NAME + 1, THEORY, prefs=[270], only=True)
f.place((0.8, 1.4), V_, NAME + 1, BASE, prefs=[150, 180, 120], only=True)
f.place((1.6, 1.4), it("h"), NAME, prefs=[0], d=6, only=True)
f.place((3.85, 1.35), "Alan = " + NORM + UxV + NORM, NAME, TEXT, prefs=["c"], only=True)
f.render(
    "paralelkenar-alani",
    "<em>ABCD</em> paralelkenarında taban |<em>AB</em>| = &#8214;<em>u</em>&#8214;, yükseklik "
    "<em>h</em> = |<em>DH</em>| = &#8214;<em>v</em>&#8214; sin <em>&#952;</em>&#8217;dır; alan "
    "&#8214;<em>u</em>&#8214; <em>h</em> = &#8214;<em>u</em> &#215; <em>v</em>&#8214; olur.",
    "Parallelogram ABCD with AB = u and AD = v as arrows, the angle theta at A, the dashed height "
    "DH with a right angle at H, and the area |u x v| written inside")


# ===========================================================================
# 7. vkc-paralelkenar-ornek: A(1,1,0), B(3,2,1), C(2,4,3), D(0,3,2)
# ===========================================================================
A, B, C, D = (1, 1, 0), (3, 2, 1), (2, 4, 3), (0, 3, 2)
Uv, Vv = vsub(B, A), vsub(D, A)
N = vcross(Uv, Vv)
assert Uv == (2, 1, 1) and Vv == (-1, 2, 2) and close(vadd(B, Vv), C) and N == (0, -5, 5)
NT = vadd(A, vscale(0.4, N))
assert close(NT, (1, -1, 2))
ext = [O, (4, 0, 0), (0, 5, 0), (0, 0, 4), A, B, C, D, NT]
f = Fig(-20, 35, ext, width=520, pad=80)
assert f.front(N)
PL = [A, B, C, D]
f.add_occluder(PL)
f.axes(((0, 4), (0, 5), (0, 4)))
f.polygon(PL, THEORY, 0.15, stroke=THEORY, width=1.1, s_opacity=0.6)
f.arrow(A, B, THEORY, 2.8, 13.0)
f.arrow(A, D, BASE, 2.8, 13.0)
f.arrow(A, NT, PRACTICE, 3.2, 13.0, halo=True)
f.right_angle(A, N, Uv, 20, TEXT)
for P in (A, B, C, D):
    f.point(P, TEXT, 3.6)
cen = vscale(0.5, vadd(A, C))
f.place(cen, "Alan = 5" + SQRT + "2", NAME, TEXT, prefs=["c"], only=True)
f.place(A, it("A") + triple(1, 1, 0), NAME, prefs=[270, 300, 240])
f.place(B, it("B") + triple(3, 2, 1), NAME, prefs=[0, 330, 30])
f.place(C, it("C") + triple(2, 4, 3), NAME, prefs=[45, 0, 90])
f.place(D, it("D") + triple(0, 3, 2), NAME, prefs=[135, 180, 90])
f.place(vscale(0.5, vadd(A, B)), U_ + " = " + triple(2, 1, 1), NAME, THEORY,
        prefs=[f.sang(Uv) - 90, f.sang(Uv) + 90])
f.place(vscale(0.5, vadd(A, D)), V_ + " = " + triple(-1, 2, 2), NAME, BASE,
        prefs=[f.sang(Vv) + 90, f.sang(Vv) - 90])
f.place(NT, UxV + " = " + triple(0, -5, 5), NAME, PRACTICE, prefs=ahead(f, N, (0, 30, -30, 90)))
f.render(
    "paralelkenar-ornek",
    "<em>A</em>(1, 1, 0), <em>B</em>(3, 2, 1), <em>C</em>(2, 4, 3), <em>D</em>(0, 3, 2) köşeli "
    "paralelkenar. <em>A</em>&#8217;dan çıkan kısa ok <em>u</em> &#215; <em>v</em> = (0, &#8722;5, 5) "
    "vektörünün 0,4 katıdır; paralelkenarın düzlemine diktir ve uzunluğu alanı, 5&#8730;2&#8217;yi verir.",
    "Parallelogram with corners A(1, 1, 0), B(3, 2, 1), C(2, 4, 3), D(0, 3, 2), edge arrows "
    "u = (2, 1, 1) and v = (-1, 2, 2) from A, and u x v = (0, -5, 5) drawn at 0.4 scale from A")


# ===========================================================================
# 8. vkc-ucgen-ornek: A(1,0,0), B(0,2,0), C(0,0,3), area 7/2
# ===========================================================================
A, B, C = (1, 0, 0), (0, 2, 0), (0, 0, 3)
AB, AC = vsub(B, A), vsub(C, A)
N = vcross(AB, AC)
assert AB == (-1, 2, 0) and AC == (-1, 0, 3) and N == (6, 3, 2) and vnorm(N) == 7
G = vscale(1 / 3, vadd(A, vadd(B, C)))
GT = vadd(G, vscale(0.2, N))
assert close(G, (1 / 3, 2 / 3, 1)) and close(GT, (1 / 3 + 1.2, 2 / 3 + 0.6, 1.4))
ext = [O, (2, 0, 0), (0, 3, 0), (0, 0, 3.6), GT]
f = Fig(-20, 20, ext, width=500, pad=90)
assert f.front(N)
PL = [A, B, C]
f.add_occluder(PL)
f.axes(((0, 2), (0, 3), (0, 3.6)))
f.polygon(PL, THEORY, 0.14, stroke=THEORY, width=1.0, s_opacity=0.5)
f.arrow(A, B, THEORY, 2.6, 12.0)
f.arrow(A, C, BASE, 2.6, 12.0)
f.point(G, PRACTICE, 3.0)
f.arrow(G, GT, PRACTICE, 3.0, 12.0, halo=True)
f.right_angle(G, N, vsub(A, G), 14, TEXT)
for P in (A, B, C):
    f.point(P, TEXT, 3.8)
f.place(A, it("A") + triple(1, 0, 0), NAME, prefs=[225, 250, 200])
f.place(B, it("B") + triple(0, 2, 0), NAME, prefs=[300, 270, 330])
f.place(C, it("C") + triple(0, 0, 3), NAME, prefs=[180, 150, 210])
f.place(vadd(G, (0.0, 0.1, -0.45)), "Alan = 7/2", NAME, TEXT, prefs=["c"])
f.vec_name(vscale(0.5, vadd(A, B)), [("AB", True), (" = " + triple(-1, 2, 0), False)], NAME, THEORY,
           prefs=[f.sang(AB) - 90, f.sang(AB) - 60, f.sang(AB) + 90])
f.vec_name(vscale(0.5, vadd(A, C)), [("AC", True), (" = " + triple(-1, 0, 3), False)], NAME, BASE,
           prefs=[f.sang(AC) + 90, f.sang(AC) + 60, f.sang(AC) - 90])
f.vec_name(GT, [("AB", True), (" " + TIMES + " ", False), ("AC", True), (" = " + triple(6, 3, 2), False)],
           NAME, PRACTICE, prefs=ahead(f, N, (0, 30, -30, 60, -60)))
f.render(
    "ucgen-ornek",
    "<em>A</em>(1, 0, 0), <em>B</em>(0, 2, 0), <em>C</em>(0, 0, 3) köşeli üçgen. Ağırlık merkezinden "
    "çıkan kısa ok, üçgenin düzlemine dik olan (6, 3, 2) vektörünün 0,2 katıdır; bu vektörün uzunluğu "
    "7 olduğundan alan 7/2&#8217;dir.",
    "Triangle with corners A(1, 0, 0), B(0, 2, 0), C(0, 0, 3) on the axes, edge arrows AB = (-1, 2, 0) "
    "and AC = (-1, 0, 3), and the normal AB x AC = (6, 3, 2) at 0.2 scale from the centroid")


# ===========================================================================
# 9. vkc-paralelyuz-hacmi: volume = base area * height (u = (3,0,0), v = (1,2,0), w = (1,1,3))
# ===========================================================================


def box_frame(f, Uv, Vv, Wv, base_col=THEORY):
    """Faint fill on the faces turned toward us, solid visible edges, dashed hidden ones;
    the three edges at O are left to the caller (they are the vector arrows)."""
    corners = {}
    for i in (0, 1):
        for j in (0, 1):
            for k in (0, 1):
                corners[(i, j, k)] = vadd(vadd(vscale(i, Uv), vscale(j, Vv)), vscale(k, Wv))
    vecs = (Uv, Vv, Wv)
    for ax in range(3):
        p, q = [t for t in range(3) if t != ax]
        n = vcross(vecs[p], vecs[q])
        if vdot(n, vecs[ax]) < 0:
            n = vscale(-1.0, n)
        for side in (0, 1):
            nn = n if side else vscale(-1.0, n)
            if vdot(nn, f.d) > 0:
                quad = []
                for a_, b_ in ((0, 0), (1, 0), (1, 1), (0, 1)):
                    idx = [0, 0, 0]
                    idx[ax], idx[p], idx[q] = side, a_, b_
                    quad.append(corners[tuple(idx)])
                f.S.polygon(quad, TEXT, 0.035)
                f.add_occluder(quad)
    for P, Q, vis, (i0, i1) in box_edges(f, O, Uv, Vv, Wv):
        if i0 == (0, 0, 0) and i1 in ((1, 0, 0), (0, 1, 0), (0, 0, 1)):
            continue
        base = i0[2] == 0 and i1[2] == 0
        col = base_col if base else TEXT
        if vis:
            f.line([P, Q], col, 1.3 if base else 1.2, None, 0.8 if base else 0.65)
        else:
            f.line([P, Q], col, 1.1, "5 4", 0.6 if base else 0.5)


Uv, Vv, Wv = (3, 0, 0), (1, 2, 0), (1, 1, 3)
N = vcross(Uv, Vv)
assert N == (0, 0, 6) and vdot(N, Wv) == 18
Av, Bv, Cv, Dv, Hv = Uv, vadd(Uv, Vv), Vv, Wv, (1, 1, 0)
NT = vscale(1 / 3, N)
tops = [vadd(Wv, P) for P in (O, Uv, Bv, Vv)]
assert tops == [(1, 1, 3), (4, 1, 3), (5, 3, 3), (2, 3, 3)]
ext = [O, Av, Bv, Cv] + tops + [NT]
f = Fig(-30, 26, ext, width=520, pad=90)
f.polygon([O, Av, Bv, Cv], THEORY, 0.15)
box_frame(f, Uv, Vv, Wv)
f.line([Dv, Hv], TEXT, 1.3, "5 4", 0.85)
f.arrow(O, NT, PRACTICE, 3.0, 12.0, halo=True)
f.arrow(O, Uv, THEORY, 2.8, 13.0)
f.arrow(O, Vv, BASE, 2.8, 13.0)
f.arrow(O, Wv, TEXT, 2.8, 13.0, halo=True)
f.right_angle(Hv, (0, 0, 1), f.cam.r, 13, TEXT)
f.arc(Dv, vscale(-1, Wv), (0, 0, -1), 32, REMARK, 1.4)
for P in (O, Av, Bv, Cv, Dv, Hv):
    f.point(P, TEXT, 3.4)
f.place(O, it("O"), NAME, prefs=[180, 200, 225])
f.place(Av, it("A"), NAME, prefs=[300, 270, 330])
f.place(Bv, it("B"), NAME, prefs=[315, 0, 290])
f.place(Cv, it("C"), NAME, prefs=[135, 160, 110])
f.place(Dv, it("D"), NAME, prefs=[110, 135, 90])
f.place(Hv, it("H"), NAME, prefs=[250, 270, 225])
f.place(vscale(0.5, Uv), U_, NAME + 1, THEORY, prefs=[f.sang(Uv) - 90, f.sang(Uv) + 90])
f.place(vscale(0.55, Vv), V_, NAME + 1, BASE, prefs=[f.sang(Vv) + 90, f.sang(Vv) - 90])
f.place(vscale(0.5, Wv), W_, NAME + 1, TEXT, prefs=[f.sang(Wv) + 90, f.sang(Wv) - 90])
f.place(NT, UxV, NAME, PRACTICE, prefs=[180, 160, 200])
f.place(vscale(0.5, vadd(Dv, Hv)), it("h"), NAME, TEXT, prefs=[0, 180])
bis = vunit(vadd(vunit(vscale(-1, Wv)), (0, 0, -1)))
f.place(vadd(Dv, vscale(f.u(48) / f.px_len(bis), bis)), it(THETA), NAME, REMARK, prefs=["c"], only=True)
f.place((3.1, 1.0, 0), "Taban alanı = " + NORM + UxV + NORM, DESC, TEXT, prefs=["c"])
f.render(
    "paralelyuz-hacmi",
    "<em>u</em>, <em>v</em>, <em>w</em> üzerine kurulan paralelyüz. Taban <em>OABC</em>&#8217;nin alanı "
    "&#8214;<em>u</em> &#215; <em>v</em>&#8214;, yükseklik <em>h</em> = |<em>HD</em>| = "
    "&#8214;<em>w</em>&#8214; |cos <em>&#952;</em>|&#8217;dır; <em>&#952;</em>, <em>w</em> ile tabana "
    "dik <em>u</em> &#215; <em>v</em> arasındaki açıdır. Arkada kalan ayrıtlar kesiklidir.",
    "Parallelepiped on u = (3, 0, 0), v = (1, 2, 0), w = (1, 1, 3) with base OABC shaded, u x v "
    "drawn short from O, the dashed height DH with a right angle at H and the angle theta at D")


# ===========================================================================
# 10. vkc-hacim-ornek: [u, v, w] = 24 for u = (2,0,0), v = (1,3,0), w = (1,1,4)
# ===========================================================================
Uv, Vv, Wv = (2, 0, 0), (1, 3, 0), (1, 1, 4)
assert vdot(vcross(Uv, Vv), Wv) == 24 and vcross(Uv, Vv) == (0, 0, 6)
Bv = vadd(Uv, Vv)
tops = [vadd(Wv, P) for P in (O, Uv, Bv, Vv)]
assert Bv == (3, 3, 0) and tops == [(1, 1, 4), (3, 1, 4), (4, 4, 4), (2, 4, 4)]
Hv = (1, 1, 0)
ext = [O, (4.5, 0, 0), (0, 4.5, 0), (0, 0, 5)] + tops + [Bv]
f = Fig(-22, 24, ext, width=500, pad=90)
f.polygon([O, Uv, Bv, Vv], THEORY, 0.15)
box_frame(f, Uv, Vv, Wv)
f.axes(((0, 4.5), (0, 4.5), (0, 5)))
f.line([Wv, Hv], PRACTICE, 1.4, "5 4", 0.9)
f.arrow(O, Uv, THEORY, 2.8, 13.0)
f.arrow(O, Vv, BASE, 2.8, 13.0)
f.arrow(O, Wv, TEXT, 2.8, 13.0, halo=True)
f.right_angle(Hv, (0, 0, 1), f.cam.r, 13, TEXT)
for P in (O, Wv, Hv):
    f.point(P, TEXT, 3.4)
f.place(O, it("O"), NAME, prefs=[180, 200, 160])
f.place(Uv, U_ + " = " + triple(2, 0, 0), NAME, THEORY, prefs=[200, 180, 225, 250])
f.place(vscale(0.55, Vv), V_ + " = " + triple(1, 3, 0), NAME, BASE, prefs=[90, 80, 100], d=5)
f.place(Wv, W_ + " = " + triple(1, 1, 4), NAME, TEXT, prefs=[150, 180, 120])
f.place(vadd(Hv, (0, 0, 2)), it("h") + " = 4", NAME, PRACTICE, prefs=[0, 180])
f.place((2.1, 1.9, 0), "Taban alanı = 6", DESC, TEXT, prefs=["c"])
f.place(vadd(tops[3], (0, 0, 0.9)), it("V") + " = [" + U_ + ", " + V_ + ", " + W_ + "] = 24", NAME, TEXT,
        prefs=["c"])
f.render(
    "hacim-ornek",
    "<em>u</em> = (2, 0, 0), <em>v</em> = (1, 3, 0), <em>w</em> = (1, 1, 4) üzerine kurulan "
    "paralelyüz. Taban <em>XY</em> düzlemindedir ve alanı 6&#8217;dır; <em>w</em>&#8217;nin ucu "
    "düzlemden 4 birim yukarıdadır. Hacim 6 &#183; 4 = 24 = [<em>u</em>, <em>v</em>, <em>w</em>].",
    "Parallelepiped on u = (2, 0, 0), v = (1, 3, 0), w = (1, 1, 4) with the base in the XY plane "
    "shaded, the dashed height h = 4 from the tip of w, and V = [u, v, w] = 24")


# ===========================================================================
# 11. vkc-es-duzlemli-ornek: w = 2v - u, [u, v, w] = 0
# ===========================================================================
Uv, Vv, Wv = (1, 2, 3), (4, 5, 6), (7, 8, 9)
assert vdot(vcross(Uv, Vv), Wv) == 0 and vsub(vscale(2, Vv), Uv) == Wv
mU, V2 = vscale(-1, Uv), vscale(2, Vv)
ext = [O, (9, 0, 0), (-2, 0, 0), (0, 11, 0), (0, -3, 0), (0, 0, 13), (0, 0, -4), V2, Wv, mU]
f = Fig(-20, 20, ext, width=560, pad=90)
PL = [O, mU, Wv, V2]
f.add_occluder(PL)
f.axes(((-2, 9), (-3, 11), (-4, 13)))
f.polygon(PL, THEORY, 0.14, stroke=THEORY, width=1.0, s_opacity=0.45)
f.arrow(O, V2, BASE, 1.5, 10.0, "6 4", 0.9)
f.arrow(O, mU, THEORY, 1.5, 10.0, "6 4", 0.9)
f.arrow(O, Wv, PRACTICE, 3.0, 13.0)
f.arrow(O, Vv, BASE, 3.0, 13.0, halo=True)
f.arrow(O, Uv, THEORY, 3.0, 13.0)
f.point(O, TEXT, 3.4)
f.place(O, it("O"), NAME, prefs=[315, 300, 330])
f.place(Uv, U_ + " = " + triple(1, 2, 3), NAME, THEORY, prefs=ahead(f, Uv, (90, 60, 120)))
f.place(Vv, V_ + " = " + triple(4, 5, 6), NAME, BASE, prefs=ahead(f, Vv, (90, 60, 120)))
f.place(Wv, W_ + " = " + triple(7, 8, 9), NAME, PRACTICE, prefs=ahead(f, Wv, (-90, -60, -120)))
f.place(V2, "2" + V_, NAME, BASE, prefs=ahead(f, V2))
f.place(mU, MINUS + U_, NAME, THEORY, prefs=ahead(f, mU))
f.place(vadd(V2, (0, 0, -9.5)), "[" + U_ + ", " + V_ + ", " + W_ + "] = 0", NAME, TEXT, prefs=["c"])
f.render(
    "es-duzlemli-ornek",
    "<em>u</em> = (1, 2, 3), <em>v</em> = (4, 5, 6), <em>w</em> = (7, 8, 9) aynı düzlemdedir: "
    "<em>w</em>, &#8722;<em>u</em> ile 2<em>v</em> üzerine kurulan paralelkenarın köşegenidir, yani "
    "<em>w</em> = 2<em>v</em> &#8722; <em>u</em>.",
    "Vectors u = (1, 2, 3), v = (4, 5, 6), w = (7, 8, 9) from the origin lying in one plane: the "
    "shaded parallelogram on -u and 2v has w as its diagonal; [u, v, w] = 0")


# ===========================================================================
# 12. vkc-duzlemde-aci (plane): theta = pi/4 between u = (1,2) and v = (3,1)
# ===========================================================================
f = Flat((-0.5, 3.5), (-0.5, 2.5), width=500)
p = f.p
p.grid(xs=[0.5 * k for k in range(-1, 8)], ys=[0.5 * k for k in range(-1, 6)])
p.origin_axes("", "", xticks=(1, 2, 3), yticks=(1, 2), opacity=0.6)
f.reg_px([f.px((-0.5, 0)), f.px((3.5, 0))], 0.8)
f.reg_px([f.px((0, -0.5)), f.px((0, 2.5))], 0.8)
for t in (1, 2, 3):
    f.boxes.append((f.px((t, 0))[0] - 5, f.px((t, 0))[1] + 5, f.px((t, 0))[0] + 5, f.px((t, 0))[1] + 17))
for t in (1, 2):
    f.boxes.append((f.px((0, t))[0] - 17, f.px((0, t))[1] - 6, f.px((0, t))[0] - 4, f.px((0, t))[1] + 6))
f.place(("px", p.x0 + p.w + 4, f.px((0, 0))[1]), it("X"), AXIS, prefs=[315, 270], d=4)
f.place(("px", f.px((0, 0))[0], p.y0 - 4), it("Y"), AXIS, prefs=[45, 0], d=4)
au, av = math.atan2(2, 1), math.atan2(1, 3)
assert abs(au - av - math.pi / 4) < 1e-12
f.arc((0, 0), av, au, 56, TEXT, 1.4)
f.arrow((0, 0), (3, 1), BASE, 2.8, 13.0)
f.arrow((0, 0), (1, 2), THEORY, 2.8, 13.0)
f.point((0, 0), TEXT, 3.4)
f.place((1, 2), U_ + " = (1, 2)", NAME, THEORY, prefs=[180, 160, 200], only=True)
f.place((3, 1), V_ + " = (3, 1)", NAME, BASE, prefs=[0, 20, 340, 90], only=True)
mid = (au + av) / 2
f.place((0.60 * math.cos(mid), 0.60 * math.sin(mid)), it(THETA) + " = " + PI + "/4", NAME, TEXT,
        prefs=[math.degrees(mid)], d=4)
f.render(
    "duzlemde-aci",
    "<em>u</em> = (1, 2) ile <em>v</em> = (3, 1) arasındaki açı: cos <em>&#952;</em> = &#8730;2/2, "
    "yani <em>&#952;</em> = <em>&#960;</em>/4.",
    "Plane vectors u = (1, 2) and v = (3, 1) from the origin on a light grid, with the angle "
    "theta = pi/4 between them marked by an arc")


# ===========================================================================
# 13. vkc-duzlemde-alan: (3,1,0) x (1,2,0) = (0,0,5), area 5
# ===========================================================================
Uv, Vv = (3, 1, 0), (1, 2, 0)
N = vcross(Uv, Vv)
assert N == (0, 0, 5)
Bv = vadd(Uv, Vv)
ext = [O, (4.5, 0, 0), (0, 3.5, 0), (0, 0, 5.8), Bv]
f = Fig(35, 24, ext, width=540, pad=90)
PL = [O, Uv, Bv, Vv]
f.add_occluder(PL)
f.axes(((0, 4.5), (0, 3.5), (0, 5.8)))
f.polygon(PL, THEORY, 0.15, stroke=THEORY, width=1.0, s_opacity=0.55)
f.arrow(O, Uv, THEORY, 2.8, 13.0)
f.arrow(O, Vv, BASE, 2.8, 13.0)
f.arrow(O, N, PRACTICE, 3.4, 14.0, halo=True)
f.right_angle(O, N, Vv, 16, TEXT)
f.point(O, TEXT, 3.4)
f.place(O, it("O"), NAME, prefs=[180, 200, 160])
f.place(Uv, U_ + " = " + triple(3, 1, 0), NAME, THEORY, prefs=[200, 190, 210], only=True, d=9)
f.place(Vv, V_ + " = " + triple(1, 2, 0), NAME, BASE, prefs=[0, 340, 20])
f.place(N, UxV + " = " + triple(0, 0, 5), NAME, PRACTICE, prefs=[0, 340, 20], d=10)
f.place(vscale(0.5, Bv), "Alan = 5", NAME, TEXT, prefs=["c"], only=True)
f.render(
    "duzlemde-alan",
    "<em>XY</em> düzlemindeki <em>u</em> = (3, 1, 0) ve <em>v</em> = (1, 2, 0) üzerine kurulan "
    "paralelkenar. <em>u</em> &#215; <em>v</em> = (0, 0, 5) <em>Z</em> ekseni üzerindedir ve uzunluğu "
    "alana, 5&#8217;e eşittir.",
    "Parallelogram on u = (3, 1, 0) and v = (1, 2, 0) in the XY plane, area 5, with u x v = (0, 0, 5) "
    "along the Z axis and a right-angle mark at the origin")


# ===========================================================================
# 14. vkc-es-duzlemlilik-m: m = 0, w = 2u + v
# ===========================================================================
Uv, Vv, Wv = (1, -1, 1), (1, 2, -1), (3, 0, 1)
assert vdot(vcross(Uv, Vv), Wv) == 0 and vadd(vscale(2, Uv), Vv) == Wv
U2 = vscale(2, Uv)
ext = [O, (4, 0, 0), (0, -2.5, 0), (0, 2.5, 0), (0, 0, 2), (0, 0, -1.5), U2, Wv, Vv]
f = Fig(-70, 14, ext, width=540, pad=90)
PL = [O, U2, Wv, Vv]
f.add_occluder(PL)
f.axes(((0, 4), (-2.5, 2.5), (-1.5, 2)))
f.polygon(PL, THEORY, 0.14, stroke=THEORY, width=1.0, s_opacity=0.45)
f.arrow(O, U2, THEORY, 1.5, 10.0, "6 4", 0.9)
f.arrow(U2, Wv, BASE, 1.5, 10.0, "6 4", 0.9)
f.arrow(O, Wv, PRACTICE, 3.0, 13.0)
f.arrow(O, Vv, BASE, 3.0, 13.0)
f.arrow(O, Uv, THEORY, 3.0, 13.0, halo=True)
f.point(O, TEXT, 3.4)
f.place(O, it("O"), NAME, prefs=[180, 200, 160])
# the u label goes into the free wedge between the Z axis and the dashed 2u, above the tip of u
(tx, ty), (zx, _), (ux2, uy2) = f.px(Uv), f.px(O), f.px(U2)
ly = ty - 64
lx = (zx + tx + (ty - ly) * (ux2 - tx) / (ty - uy2)) / 2
f.place(("px", lx, ly), U_ + " = " + triple(1, -1, 1), NAME, THEORY, prefs=["c"], only=True)
f.place(Vv, V_ + " = " + triple(1, 2, -1), NAME, BASE, prefs=ahead(f, Vv, (-90, -60, -120, 0)))
f.place(Wv, W_ + " = " + triple(3, 0, 1), NAME, PRACTICE, prefs=ahead(f, Wv))
f.place(U2, "2" + U_, NAME, THEORY, prefs=ahead(f, U2, (60, 90, 30)))
f.place(vscale(0.5, vadd(U2, Wv)), V_, NAME, BASE, prefs=[f.sang(Vv) + 90, f.sang(Vv) - 90])
f.place(vadd(U2, (0, 0, 1.4)), it("m") + " = 0 için [" + U_ + ", " + V_ + ", " + W_ + "] = 0", NAME,
        TEXT, prefs=["c"])
f.render(
    "es-duzlemlilik-m",
    "<em>m</em> = 0 için <em>u</em> = (1, &#8722;1, 1), <em>v</em> = (1, 2, &#8722;1), "
    "<em>w</em> = (3, 0, 1) aynı düzlemdedir: paralelkenar kuralıyla <em>w</em> = 2<em>u</em> + "
    "<em>v</em>.",
    "Vectors u = (1, -1, 1), v = (1, 2, -1) and w = (3, 0, 1) from the origin in one plane: the "
    "shaded parallelogram on 2u and v has w as its diagonal")


# ===========================================================================
# 15. vkc-sinus-teoremi (plane): position vectors a, b, c and the side vectors
# ===========================================================================
Op, Ap, Bp, Cp = (0, 0), (0.3, 4.2), (-3, 2.3), (3.5, 2.2)
f = Flat((-3.8, 4.3), (-0.55, 4.85), width=520)
f.p.polygon([Ap, Bp, Cp], THEORY, 0.07)
for P, Q in ((Op, Ap), (Op, Bp), (Op, Cp)):
    f.arrow(P, Q, REMARK, 1.4, 10.0, None, 0.75, w=0.8)
f.arrow(Bp, Ap, THEORY, 2.6, 12.0)
f.arrow(Cp, Bp, BASE, 2.6, 12.0)
f.arrow(Ap, Cp, PRACTICE, 2.6, 12.0)


def ang2(P, Q):
    return math.atan2(Q[1] - P[1], Q[0] - P[0])


for P, Q1, Q2 in ((Ap, Bp, Cp), (Bp, Cp, Ap), (Cp, Ap, Bp)):
    a1, a2 = ang2(P, Q1), ang2(P, Q2)
    if (a2 - a1) % (2 * math.pi) > math.pi:
        a1, a2 = a2, a1
    a2 = a1 + (a2 - a1) % (2 * math.pi)
    f.arc(P, a1, a2, 26, TEXT, 1.2)
for P in (Op, Ap, Bp, Cp):
    f.point(P, TEXT, 3.6)
f.place(Op, it("O"), NAME, prefs=[270, 250, 290], only=True)
f.place(Ap, it("A"), NAME + 1, prefs=[90, 60, 120], only=True)
f.place(Bp, it("B"), NAME + 1, prefs=[180, 200, 160], only=True)
f.place(Cp, it("C"), NAME + 1, prefs=[0, 340, 20], only=True)
# angle names inside the triangle, off the O->A arrow
for P, Q1, Q2, s_, rot in ((Ap, Bp, Cp, "A", -22), (Bp, Cp, Ap, "B", 0), (Cp, Ap, Bp, "C", 0)):
    a1, a2 = ang2(P, Q1), ang2(P, Q2)
    mid = math.atan2(math.sin(a1) + math.sin(a2), math.cos(a1) + math.cos(a2)) + math.radians(rot)
    r = f.u(44)
    f.place((P[0] + r * math.cos(mid), P[1] + r * math.sin(mid)), it(s_), 12, PRACTICE,
            prefs=["c"], only=True)
f.place((0.3 * 0.28, 4.2 * 0.28), it("a"), NAME, REMARK, prefs=[0, 180])
f.place((-3 * 0.45, 2.3 * 0.45), it("b"), NAME, REMARK, prefs=[225, 45])
f.place((3.5 * 0.45, 2.2 * 0.45), it("c"), NAME, REMARK, prefs=[315, 135])
f.place(((Ap[0] + Bp[0]) / 2, (Ap[1] + Bp[1]) / 2), it("a") + " " + MINUS + " " + it("b"), NAME,
        THEORY, prefs=[135, 120, 150])
f.place((-1.4, (2.3 + 2.2) / 2 + 0.01), it("b") + " " + MINUS + " " + it("c"), NAME, BASE,
        prefs=[90, 70, 110])
f.place(((Ap[0] + Cp[0]) / 2, (Ap[1] + Cp[1]) / 2), it("c") + " " + MINUS + " " + it("a"), NAME,
        PRACTICE, prefs=[45, 30, 60])
f.render(
    "sinus-teoremi",
    "<em>A</em>, <em>B</em>, <em>C</em> noktalarının yer vektörleri <em>a</em>, <em>b</em>, <em>c</em> "
    "ve kenar vektörleri <em>a</em> &#8722; <em>b</em>, <em>b</em> &#8722; <em>c</em>, "
    "<em>c</em> &#8722; <em>a</em>. Üçünün toplamı sıfırdır; köşelerdeki yaylar iç açıları gösterir.",
    "Triangle ABC with position vectors a, b, c drawn faintly from O, side vectors a - b from B to A, "
    "b - c from C to B, c - a from A to C, and the interior angles A, B, C marked by arcs")


# ---------------------------------------------------------------------------
for name, content in OUT.items():
    path = OUT_DIR / f"analytic-vkc-{name}.md"
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(content)
    print("wrote", path.name)
