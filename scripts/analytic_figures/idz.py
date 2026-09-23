# -*- coding: utf-8 -*-
"""Figures for dersler/analitik-geometri/iki-duzlem-ve-duzlemin-irdelenmesi.qmd (chapter key: idz).

Three-dimensional drawings go through scripts/svg_plot3.py (an orthographic
Camera on an equal-aspect svg_plot.Plot panel); the two cross-section drawings
are flat svg_plot.Plot panels. The figures go INSIDE the box
they explain (example, solution, proof), never inside a definition box.

Planes are translucent parallelogram patches. Every patch is registered as an
occluder, so a line or an edge that passes behind it is drawn thin and dashed
(`Fig.oline`). Labels are placed after the projection, in page pixels:
`Canvas.place` tries a ring of candidate positions around the anchor and keeps
the cheapest one, i.e. the one that touches no registered line, point or
earlier label.

The plane name is the fraktur letter D. Book fonts and rsvg have no glyph for
U+1D507, so it is drawn as an outline path (from TeX Gyre DejaVu Math, GUST
Font License) followed by an ordinary <text> tail such as a subscript or the
equation.

Usage:   python scripts/analytic_figures/idz.py
         python scripts/center_figures.py "analytic-idz-*.md" --keep-width
Output:  scripts/_figures/analytic-idz-<name>.md
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
from svg_plot3 import (Camera, Space, vadd, vsub, vscale, vdot, vcross, vnorm,  # noqa: E402
                       vunit)

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
OUT = {}

MINUS, PHI, THETA, ELL, LAMBDA, PI = "−", "φ", "θ", "ℓ", "λ", "π"
NAME, DESC, AXIS = 14.0, 12.5, 14.5          # font sizes (px)
O = (0.0, 0.0, 0.0)

# Fraktur D (U+1D507) outline in em units, baseline at y = 0, y pointing down.
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

# ---------------------------------------------------------------------------
# text helpers
# ---------------------------------------------------------------------------


def it(s):
    return f'<tspan font-style="italic">{s}</tspan>'


def sub(s, size=NAME):
    return (f'<tspan font-size="{0.74 * size:.1f}" dy="4">{s}</tspan>'
            f'<tspan dy="-4">&#8203;</tspan>')


def num(v):
    """Number with a real minus sign and a decimal comma."""
    s = str(v).replace(".", ",")
    return (MINUS + s[1:]) if s.startswith("-") else s


def triple(*vs):
    return "(" + ", ".join(v if isinstance(v, str) else num(v) for v in vs) + ")"


def frac(a, b):
    return f"{num(a)}/{b}"


N_, V_, D_ = it("n"), it("v"), it("d")


def pname(s, idx=None, size=NAME):
    """Italic point name with an optional subscript, e.g. P0."""
    return it(s) + (sub(str(idx), size) if idx is not None else "")


P0_ = pname("P", 0)


def eq(s):
    """Plane equation tail ': 2x - y + 2z + 9 = 0' with italic variables and real minus signs."""
    s = re.sub(r"[xyz]", lambda m: it(m.group()), s.replace("-", MINUS))
    return ": " + s + " = 0"


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

    def anchor_px(self, anchor):
        raise NotImplementedError

    def place(self, anchor, s, size=NAME, color=TEXT, prefs=None, d=7.0, only=False,
              far=(0, 6, 13, 22, 34), leader=False, opacity=1.0, tall=0.0, w_px=None):
        """Put text s next to anchor; prefs are page angles in degrees (0 = right,
        90 = up) tried first, earlier ones winning ties. The cheapest candidate
        (no line, point or label under it) is used. `tall` adds room above the
        text (for an arrow drawn over a name)."""
        x, y = self.anchor_px(anchor)
        w, h = (w_px if w_px is not None else text_width(s, size)), size + tall
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

    def plane_name(self, anchor, tail="", size=NAME, color=TEXT, prefs=None, d=7.0, only=False,
                   far=(0, 6, 13, 22, 34), leader=False):
        """The fraktur D (an outline path) followed by the text `tail`, placed like a label."""
        gw = FRAK_ADV * size
        w = gw + (text_width(tail, size) if tail else 0.0)
        cx, cy = self.place(anchor, tail or "D", size, color, prefs, d, only, far, leader, w_px=w)
        self.texts.pop()
        x0, base = cx - w / 2, cy + 0.30 * size
        k = size
        self.texts.append(f'<path d="{FRAK_D}" transform="translate({x0:.1f} {base:.1f}) scale({k:.2f})" '
                          f'fill="{color}" stroke="{BG}" stroke-width="{3.6 / k:.3f}" '
                          f'stroke-linejoin="round" paint-order="stroke"/>')
        if tail:
            self.texts.append(f'<text x="{x0 + gw:.1f}" y="{base:.1f}" fill="{color}" font-size="{size}" '
                              f'text-anchor="start" stroke="{BG}" stroke-width="3.6" '
                              f'stroke-linejoin="round" paint-order="stroke">{tail}</text>')
        return cx, cy


class Fig(Canvas):
    """A 3-D scene: camera, equal-aspect panel fitted to `extent`, label registry."""

    def __init__(self, az, el, extent, width=600, pad=70, max_h=None, x0=0.0, y0=0.0, ppu=None):
        super().__init__()
        self.cam = Camera(az, el)
        pr = [self.cam.project(P) for P in extent]
        xs, ys = [a for a, _, _ in pr], [b for _, b, _ in pr]
        dx, dy = max(xs) - min(xs), max(ys) - min(ys)
        self.ppu = ppu or width / dx
        if max_h and dy * self.ppu > max_h:
            self.ppu = max_h / dy
        w, h = dx * self.ppu, dy * self.ppu
        self.p = Plot(x0 + pad, y0 + pad, w, h, (min(xs), max(xs)), (min(ys), max(ys)))
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

    def oline(self, P0, P1, color=TEXT, width=1.3, opacity=0.75, w=1.0, n=240, hw=1.0, ho=0.5,
              hdash="4 3"):
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
                self.line([run[0], run[-1]], color, hw, hdash, ho, w * 0.4)
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

    # -- planes -------------------------------------------------------------
    def patch(self, P, e1, e2, s1=(-1.0, 1.0), s2=(-1.0, 1.0), fill=THEORY, opacity=0.13):
        """Translucent plane piece {P + a e1 + b e2}; registered as an occluder. Its edges
        are drawn later with edges(), once every occluder of the scene is known."""
        (a0, a1), (b0, b1) = s1, s2
        C = [vadd(P, vadd(vscale(a, e1), vscale(b, e2))) for a, b in ((a0, b0), (a1, b0), (a1, b1), (a0, b1))]
        self.S.polygon(C, fill, opacity)
        self.add_occluder(C)
        return C

    def edges(self, C, color=THEORY, width=1.1, opacity=0.7):
        for A, B in zip(C, C[1:] + C[:1]):
            self.oline(A, B, color, width, opacity, w=0.6, hw=0.9, ho=0.45)

    def dline(self, P0, P1, color=THEORY, width=2.4, opacity=1.0, w=1.0):
        """A main line: solid where seen, dashed in the same colour where a plane hides it."""
        self.oline(P0, P1, color, width, opacity, w, hw=1.5, ho=0.8, hdash="6 4")

    # -- output -------------------------------------------------------------
    def emit(self):
        for t in self.emit_texts():
            self.p.add(t)

    def render(self, name, caption, aria, css=None):
        print(f"-- {name} (warnings above belong to it)")
        self.emit()
        # Tall scenes stay in the standard column: at the wide width they would be too tall.
        css = css or ("ders-grafik" if self.H / self.W > 1.1 else WIDE)
        OUT[name] = figure(round(self.W), round(self.H), [self.p], caption, css, aria)


def ahead(f, vec, spread=(0, 30, -30, 60, -60, 90, -90)):
    """Label angles around the page direction of vec: first straight past the tip."""
    a = f.sang(vec)
    return [a + s for s in spread]


def normal_arrow(f, Q, n, length_px=None, color=BASE, width=2.6, head=12.0, label=True, prefs=None,
                 name=None):
    """Normal vector drawn from Q (the vector n itself, or scaled to a page length)."""
    T = vadd(Q, n) if length_px is None else vadd(Q, vscale(f.u(length_px) / f.px_len(n), n))
    f.arrow(Q, T, color, width, head, halo=True)
    if label:
        f.place(T, name or N_, NAME + 1, color, prefs=prefs or ahead(f, n, (0, -40, 40, -80, 80)))
    return T


def mid(A, B, t=0.5):
    return vadd(A, vscale(t, vsub(B, A)))



def clip_poly(Ps, n, c):
    """The part of the planar polygon Ps where <n, P> <= c (Sutherland-Hodgman, one plane)."""
    out = []
    for i, A in enumerate(Ps):
        B = Ps[(i + 1) % len(Ps)]
        fa, fb = vdot(n, A) - c, vdot(n, B) - c
        if fa <= 0:
            out.append(A)
        if (fa < 0 < fb) or (fb < 0 < fa):
            out.append(vadd(A, vscale(fa / (fa - fb), vsub(B, A))))
    return out


def corners(P, e1, e2, s1, s2):
    (a0, a1), (b0, b1) = s1, s2
    return [vadd(P, vadd(vscale(a, e1), vscale(b, e2))) for a, b in ((a0, b0), (a1, b0), (a1, b1), (a0, b1))]


def cut_patch(f, C, m, c, fill, opacity, back=0.45):
    """Fill the patch C in two parts split by the plane <m, P> = c: the part on the far side
    from the viewer is lighter. C is registered as one occluder."""
    if vdot(m, f.d) < 0:
        m, c = vscale(-1.0, m), -c
    far_part, near_part = clip_poly(C, m, c), clip_poly(C, vscale(-1.0, m), -c)
    if len(far_part) >= 3:
        f.S.polygon(far_part, fill, opacity * back)
    if len(near_part) >= 3:
        f.S.polygon(near_part, fill, opacity)
    f.add_occluder(C)


def page_perp(cam, w, l):
    """Signed page distance of the projected w from the projected line direction l
    (positive on the left of l, i.e. the counter-clockwise side)."""
    X, Y, _ = cam.project(vadd(cam.center, w))
    lx, ly, _ = cam.project(vadd(cam.center, l))
    return (-X * ly + Y * lx) / math.hypot(lx, ly)


def book_wings(cam, W1, W2, l):
    """Signs for the in-plane directions so that the two half-planes bounded by the line
    open like a book: the first wing on the left of the line on the page, the second on the right."""
    W1 = W1 if page_perp(cam, W1, l) > 0 else vscale(-1.0, W1)
    W2 = W2 if page_perp(cam, W2, l) < 0 else vscale(-1.0, W2)
    return W1, W2


def n_(k, size=NAME + 1):
    return it("n") + sub(str(k), size)


def D_sub(k, size=NAME + 2):
    return sub(str(k), size)


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


E_X, E_Y, E_Z = (1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)


# ===========================================================================
# 1. idz-paralel-duzlemler: two parallel horizontal patches and their normals
# ===========================================================================
TOP, BOT = (0.45, 0.0, 1.3), (-0.45, 0.0, 0.0)
SX, SY = (-1.5, 1.5), (-2.2, 2.2)
FOOT = (0.95, 0.65, 0.0)                     # both normals start at the same spot of their patch
ext = corners(TOP, E_X, E_Y, SX, SY) + corners(BOT, E_X, E_Y, SX, SY) + [vadd(TOP, (0.9, 1.1, 0.8))]
f = Fig(35, 22, ext, width=560, pad=60)
C2 = f.patch(BOT, E_X, E_Y, SX, SY, BASE, 0.15)
C1 = f.patch(TOP, E_X, E_Y, SX, SY, THEORY, 0.15)
f.edges(C2, BASE, 1.3, 0.8)
f.edges(C1, THEORY, 1.3, 0.8)
F2, F1 = vadd(BOT, FOOT), vadd(TOP, FOOT)
normal_arrow(f, F2, (0, 0, 0.5), color=BASE, name=n_(2), prefs=[0, 345, 15, 330])
normal_arrow(f, F1, (0, 0, 0.5), color=THEORY, name=n_(1), prefs=[0, 20, 340])
f.point(F2, BASE, 3.4)
f.point(F1, THEORY, 3.4)
f.plane_name(C1[1], D_sub(1), NAME + 2, THEORY, prefs=[200, 225, 180, 250])
f.plane_name(C2[1], D_sub(2), NAME + 2, BASE, prefs=[200, 225, 180, 250])
f.render(
    "paralel-duzlemler",
    "Paralel iki düzlem: normal vektörleri <em>n</em><sub>1</sub> ile <em>n</em><sub>2</sub> aynı "
    "doğrultudadır. Alttaki düzlemin üsttekinin arkasında kalan kenarları kesiklidir.",
    "Two parallel horizontal plane patches D1 above and D2 below, each with an upward normal arrow "
    "n1 and n2 pointing the same way")


# ===========================================================================
# 2. idz-dik-duzlemler: a floor and a wall, their normals at a right angle
# ===========================================================================
ext = corners(O, E_X, E_Y, (-2.0, 2.0), (-2.4, 2.4)) + corners(O, E_Y, E_Z, (-2.4, 2.4), (-1.6, 2.1))
f = Fig(35, 24, ext, width=540, pad=60)
CH = corners(O, E_X, E_Y, (-2.0, 2.0), (-2.4, 2.4))
CV = corners(O, E_Y, E_Z, (-2.4, 2.4), (-1.6, 2.1))
f.S.polygon(CH, THEORY, 0.14)
f.add_occluder(CH)
cut_patch(f, CV, E_Z, 0.0, BASE, 0.16, back=0.4)
f.edges(CH, THEORY, 1.3, 0.8)
f.edges(CV, BASE, 1.3, 0.8)
f.line([(0, -2.4, 0), (0, 2.4, 0)], TEXT, 2.8)
Q = (0.0, 0.9, 0.0)
f.right_angle(Q, E_X, E_Z, 15, TEXT)
normal_arrow(f, Q, (0, 0, 1.25), color=THEORY, name=n_(1), prefs=[0, 20, 340])
normal_arrow(f, Q, (1.35, 0, 0), color=BASE, name=n_(2), prefs=ahead(f, E_X, (0, -40, 40, -80, 80)))
f.point(Q, TEXT, 3.6)
f.plane_name(CH[1], D_sub(1), NAME + 2, THEORY, prefs=[200, 225, 180, 250])
f.plane_name(CV[2], D_sub(2), NAME + 2, BASE, prefs=[20, 0, 45, 340])
f.render(
    "dik-duzlemler",
    "Dik iki düzlem: yatay zemin ile düşey duvar. Normalleri "
    "<em>n</em><sub>1</sub> ile <em>n</em><sub>2</sub> arasındaki açı diktir; düşey düzlemin yatay "
    "düzlemin altında kalan kısmı soluk, kenarları kesiklidir.",
    "A horizontal plane patch D1 and a vertical plane patch D2 crossing along a thick line, with the "
    "normal n1 pointing up and the normal n2 lying in the horizontal plane, and a right-angle mark")


# ===========================================================================
# 3. idz-arakesit-genel: two planes at 60 degrees, the line d and u = n1 x n2
# ===========================================================================
N1 = E_Z
N2 = (-math.sin(math.pi / 3), 0.0, math.cos(math.pi / 3))
assert abs(vdot(N1, N2) - 0.5) < 1e-12                  # the normals meet at 60 degrees
LU = vunit(vcross(N1, N2))
assert close(LU, vscale(-1.0, E_Y))
W1, W2 = E_X, vunit(vcross(N2, LU))
SL = (-2.4, 2.4)
C1 = corners(O, W1, LU, (-2.0, 2.0), SL)
C2 = corners(O, LU, W2, SL, (-1.6, 2.5))
f = Fig(35, 24, C1 + C2, width=540, pad=70)
f.S.polygon(C1, THEORY, 0.14)
f.add_occluder(C1)
cut_patch(f, C2, E_Z, 0.0, BASE, 0.16, back=0.4)
f.edges(C1, THEORY, 1.3, 0.8)
f.edges(C2, BASE, 1.3, 0.8)
f.dline(vscale(-2.8, LU), vscale(2.8, LU), TEXT, 2.8)
normal_arrow(f, O, N1, length_px=80, color=THEORY, name=n_(1), prefs=[180, 160, 200, 90])
normal_arrow(f, O, N2, length_px=80, color=BASE, name=n_(2), prefs=ahead(f, N2, (-60, -40, 0, -90)))
T = normal_arrow(f, O, LU, length_px=100, color=PRACTICE, label=False)
f.point(O, TEXT, 3.8)
f.place(O, P0_, NAME, prefs=[f.sang(LU) + 180 + 40, f.sang(LU) + 180 - 40, 270])
f.place(T, it("u") + " = " + n_(1, NAME) + " " + "×" + " " + n_(2, NAME), NAME, PRACTICE,
        prefs=ahead(f, LU, (-90, 90, -60, 60, 0)))
f.place(vscale(2.8, LU), D_, NAME + 2, TEXT, prefs=ahead(f, LU, (0, 40, -40, 80, -80)))
f.plane_name(C1[1], D_sub(1), NAME + 2, THEORY, prefs=[200, 225, 180, 250])
f.plane_name(C2[2], D_sub(2), NAME + 2, BASE, prefs=[20, 0, 45, 340])
f.render(
    "arakesit-genel",
    "Kesişen iki düzlem ortak bir <em>d</em> doğrusu boyunca buluşur. <em>d</em>, iki düzlemde de "
    "yattığı için iki normale de diktir; doğrultusu <em>u</em> = <em>n</em><sub>1</sub> &#215; "
    "<em>n</em><sub>2</sub>'dir. Düzlemlerin birbirinin arkasında kalan kenarları kesiklidir.",
    "Two plane patches D1 and D2 meeting at about 60 degrees along a thick line d, a point P0 on d, "
    "the normals n1 and n2 from P0 and the arrow u = n1 x n2 along d")


def eqlabel(k, s):
    """Tail ' _k: equation = 0' after the fraktur D."""
    return (D_sub(k, NAME) if k else "") + eq(s)


# ===========================================================================
# 4. idz-arakesit-ornek: D1: 2x - 3y + z - 5 = 0, D2: 3x + 4y - z + 1 = 0 (Z drawn at 1/4)
# ===========================================================================
ZS = 0.25


def zs(P):
    """Drawing coordinates: the Z axis is shortened to a quarter."""
    return (P[0], P[1], P[2] * ZS)


n1, n2 = (2, -3, 1), (3, 4, -1)
P1, P2 = (1, -1, 0), (0, 4, 17)
for P in (P1, P2):
    assert vdot(n1, P) - 5 == 0 and vdot(n2, P) + 1 == 0
UD = vsub(P2, P1)
assert UD == (-1, 5, 17) and vcross(n1, n2) == UD
W1, W2 = vunit(vcross(n1, UD)), vunit(vcross(n2, UD))



T0, T1, SW4 = -0.22, 1.22, 1.7
CAM4 = Camera(25, 20)
W1, W2 = book_wings(CAM4, zs(W1), zs(W2), zs(UD))


def on_d(t, s=0.0, w=W1):
    return vadd(zs(vadd(P1, vscale(t, UD))), vscale(s, w))


S1 = [on_d(T0), on_d(T1), on_d(T1, SW4, W1), on_d(T0, SW4, W1)]
S2 = [on_d(T0), on_d(T1), on_d(T1, SW4, W2), on_d(T0, SW4, W2)]
ext = S1 + S2 + [(3.0, 0, 0), (0, 6.3, 0), (0, 0, 5.4), (-1.2, 0, 0), (0, -2.6, 0), (0, 0, -1.3)]
f = Fig(25, 20, ext, width=600, pad=70)
f.S.polygon(S1, THEORY, 0.16)
f.S.polygon(S2, BASE, 0.17)
f.add_occluder(S1)
f.add_occluder(S2)
f.axes(((-1.2, 3.0), (-2.6, 6.3), (-1.3, 5.4)))
f.edges(S1, THEORY, 1.2, 0.8)
f.edges(S2, BASE, 1.2, 0.8)
f.dline(on_d(T0 - 0.08), on_d(T1 + 0.08), TEXT, 2.8)
Z17 = zs((0, 0, 17))
f.line([zs(P2), zs((0, 0, 17))], TEXT, 1.0, "4 3", 0.55, w=0.4)
f.line([vadd(Z17, (-0.12, 0, 0)), vadd(Z17, (0.12, 0, 0))], TEXT, 1.2, None, 0.8, w=0.4)
f.place(Z17, "17", 12.0, TEXT, prefs=[180, 200, 160], d=6)
for P in (P1, P2):
    f.point(zs(P), TEXT, 4.0)
f.place(zs(P1), pname("P", 1), NAME, prefs=[330, 300, 0, 270])
f.place(zs(P2), pname("P", 2), NAME, prefs=[330, 300, 0, 270])
f.place(on_d(T1 + 0.08), D_, NAME + 2, TEXT, prefs=ahead(f, zs(UD), (0, 30, -30)))
f.plane_name(mid(S1[2], S1[3], 0.35), eqlabel(1, "2x - 3y + z - 5"), 13.0, THEORY,
             prefs=[135, 110, 160, 90], leader=True)
f.plane_name(mid(S2[2], S2[3], 0.3), eqlabel(2, "3x + 4y - z + 1"), 13.0, BASE,
             prefs=[300, 285, 315], only=True, far=(34, 44, 54), leader=True)
f.render(
    "arakesit-ornek",
    "İki düzlemin arakesit doğrusu <em>d</em>, ortak noktalar <em>P</em><sub>1</sub>(1, &#8722;1, 0) "
    "ve <em>P</em><sub>2</sub>(0, 4, 17)&#8217;den geçer; iki şerit, düzlemlerin <em>d</em>&#8217;yi "
    "içeren parçalarıdır. Şekil sığsın diye <em>Z</em>-ekseni dörtte bir ölçekle çizilmiştir.",
    "Axes X, Y, Z with the Z axis at quarter scale; the line d through P1 (1, -1, 0) and P2 (0, 4, 17) "
    "and two strips of the planes 2x - 3y + z - 5 = 0 and 3x + 4y - z + 1 = 0 that contain it")


# ===========================================================================
# 5. idz-arakesit-orijin: x + y + 2z = 0 and 2x - y + z = 0 through O, d along (-1, -1, 1)
# ===========================================================================
n1, n2 = (1, 1, 2), (2, -1, 1)
UD = (-1, -1, 1)
assert vcross(n1, n2) == vscale(-3, UD) and vdot(n1, UD) == 0 and vdot(n2, UD) == 0
LU = vunit(UD)
W1, W2 = book_wings(Camera(35, 22), vunit(vcross(n1, LU)), vunit(vcross(n2, LU)), LU)
LAM = 1.5                                   # d is drawn for lambda in [-LAM, LAM]
SL, SW = (-LAM * math.sqrt(3) + 0.3, LAM * math.sqrt(3) - 0.3), (0.0, 2.3)
C1 = corners(O, LU, W1, SL, SW)
C2 = corners(O, LU, W2, SL, SW)
AX = ((-2.0, 3.0), (-2.0, 3.0), (-2.2, 2.9))
ext = C1 + C2 + [(3.0, 0, 0), (0, 3.0, 0), (0, 0, 2.9), (-2.0, 0, 0), (0, -2.0, 0), (0, 0, -2.2)]
f = Fig(35, 22, ext, width=560, pad=70)
f.S.polygon(C1, THEORY, 0.15)
f.S.polygon(C2, BASE, 0.16)
f.add_occluder(C1)
f.add_occluder(C2)
f.axes(AX)
f.edges(C1, THEORY, 1.2, 0.8)
f.edges(C2, BASE, 1.2, 0.8)
DA, DB = vscale(-LAM, UD), vscale(LAM, UD)
f.dline(DA, DB, TEXT, 2.8)
f.point(O, TEXT, 3.8)
f.place(O, it("O"), NAME, prefs=[340, 20, 200, 160])
f.place(DB, D_, NAME + 2, TEXT, prefs=ahead(f, UD, (0, 30, -30, 60, -60)))
f.plane_name(mid(C1[1], C1[2], 0.55), eqlabel(1, "x + y + 2z"), 13.0, THEORY, prefs=[90, 105, 75])
f.plane_name(mid(C2[2], C2[3], 0.5), eqlabel(2, "2x - y + z"), 13.0, BASE, prefs=[0, 340, 20, 315],
             leader=True)
f.render(
    "arakesit-orijin",
    "Orijinden geçen iki düzlemin arakesiti de orijinden geçer: <em>d</em>, <em>O</em>&#8217;dan "
    "geçen ve (&#8722;1, &#8722;1, 1) doğrultusundaki doğrudur. Her düzlemin yalnız <em>d</em>&#8217;nin bir yanında kalan yarısı çizilmiştir.",
    "Axes X, Y, Z and two plane patches through the origin, x + y + 2z = 0 and 2x - y + z = 0, meeting "
    "along the thick line d through O with direction (-1, -1, 1)")


# ===========================================================================
# 6. idz-arakesit-yatay: x + y + z - 4 = 0 and x + y - z = 0 meet in the level line z = 2
# ===========================================================================
n1, n2 = (1, 1, 1), (1, 1, -1)
UD = (1, -1, 0)
Q = (1, 1, 2)
assert vdot(n1, Q) == 4 and vdot(n2, Q) == 0 and vcross(n1, n2) == vscale(-2, UD)
LU = vunit(UD)
# a tent over the floor: D1 runs down toward the viewer, D2 down away from him
W1, W2 = (1.0, 1.0, -2.0), (-1.0, -1.0, -2.0)
assert vdot(W1, n1) == 0 and vdot(W2, n2) == 0 and vdot(W1, UD) == 0 and vdot(W2, UD) == 0


def lam(l):
    return (l, 2 - l, 2)


L0, L1 = -0.6, 2.6
SW6 = 0.65
S1 = [lam(L0), lam(L1), vadd(lam(L1), vscale(SW6, W1)), vadd(lam(L0), vscale(SW6, W1))]
S2 = [lam(L0), lam(L1), vadd(lam(L1), vscale(SW6, W2)), vadd(lam(L0), vscale(SW6, W2))]
ext = S1 + S2 + [(4.2, 0, 0), (0, 4.2, 0), (0, 0, 3.1), (-1.3, 0, 0), (0, -1.3, 0), (-1, 3, 0), (3, -1, 0)]
f = Fig(35, 22, ext, width=600, pad=70)
f.S.polygon(S1, THEORY, 0.15)
f.S.polygon(S2, BASE, 0.16)
f.add_occluder(S1)
f.add_occluder(S2)
f.axes(((-1.3, 4.2), (-1.3, 4.2), (0, 3.1)))
f.edges(S1, THEORY, 1.2, 0.8)
f.edges(S2, BASE, 1.2, 0.8)
f.line([(-1, 3, 0), (3, -1, 0)], TEXT, 1.2, "5 4", 0.55, w=0.5)
f.line([Q, (1, 1, 0)], TEXT, 1.1, "4 3", 0.55, w=0.5)
f.point((1, 1, 0), TEXT, 2.4)
f.dline(lam(L0 - 0.15), lam(L1 + 0.15), TEXT, 2.8)
f.point(Q, TEXT, 4.0)
f.place(Q, triple(1, 1, 2), NAME, prefs=[70, 110, 45, 135])
f.place(lam(L0 - 0.15), D_ + ": " + it("z") + " = 2", NAME, TEXT, prefs=[0, 20, 340, 45, 315])
f.place((3, -1, 0), it("x") + " + " + it("y") + " = 2", 12.5, TEXT, prefs=[330, 300, 0], opacity=0.8)
f.plane_name(mid(S1[0], S1[3], 0.5), D_sub(1), NAME + 2, THEORY, prefs=[0, 340, 20])
f.plane_name(mid(S2[1], S2[2], 0.35), D_sub(2), NAME + 2, BASE, prefs=[180, 200, 160])
f.render(
    "arakesit-yatay",
    "Arakesit doğrusu <em>d</em> her noktasında <em>z</em> = 2 olan yatay bir doğrudur; bu yüzden "
    "<em>z</em> parametre olarak seçilemez. Kesikli doğru, <em>d</em>&#8217;nin <em>XY</em>-düzlemindeki "
    "izdüşümü <em>x</em> + <em>y</em> = 2&#8217;dir.",
    "Axes X, Y, Z; the horizontal line d at height z = 2 through (1, 1, 2), its shadow x + y = 2 in the "
    "XY plane, a dashed drop from (1, 1, 2), and strips of the two planes that contain d")


def flat_right_angle(f, Q, a_deg, b_deg, size=12, color=TEXT):
    a, b = math.radians(a_deg), math.radians(b_deg)
    s = f.u(size)
    P1 = (Q[0] + s * math.cos(a), Q[1] + s * math.sin(a))
    P3 = (Q[0] + s * math.cos(b), Q[1] + s * math.sin(b))
    P2 = (P1[0] + s * math.cos(b), P1[1] + s * math.sin(b))
    f.line([P1, P2, P3], color, 1.2, None, 0.9, w=0.5)


def polar2(r, deg):
    return (r * math.cos(math.radians(deg)), r * math.sin(math.radians(deg)))


def eqn(s):
    """An equation with italic variables and real minus signs."""
    return re.sub(r"[xyz]", lambda m: it(m.group()), s.replace("-", MINUS))


# ===========================================================================
# 7. idz-aci-kesit (plane): a cross-section perpendicular to the line of intersection
# ===========================================================================
TH = 60.0
f = Flat((-3.3, 3.3), (-1.55, 2.75), width=480, pad=40)
f.line([(-3.1, 0), (3.1, 0)], THEORY, 2.4)
G0, G1 = polar2(-1.75, TH), polar2(3.05, TH)
f.line([G0, G1], BASE, 2.4)
N1T, N2T = polar2(1.55, 90), polar2(1.55, 90 + TH)
f.arrow((0, 0), N1T, THEORY, 2.4, 12.0)
f.arrow((0, 0), N2T, BASE, 2.4, 12.0)
flat_right_angle(f, (0, 0), 0, 90, 12)
flat_right_angle(f, (0, 0), 90 + TH, 180 + TH, 12)
f.arc((0, 0), math.radians(90), math.radians(90 + TH), 44, PRACTICE, 1.6, 1.0)
f.arc((0, 0), 0.0, math.radians(TH), 74, PRACTICE, 1.6, 1.0)
f.place(polar2(f.u(60), 90 + TH / 2), THETA, NAME + 1, PRACTICE, prefs=["c"], only=True)
f.place(polar2(f.u(90), TH / 2), THETA, NAME + 1, PRACTICE, prefs=["c"], only=True)
f.point((0, 0), TEXT, 4.2)
f.place((0, 0), D_, NAME + 1, TEXT, prefs=[270, 250, 290, 225])
f.place(N1T, n_(1), NAME + 1, THEORY, prefs=[0, 20, 340])
f.place(N2T, n_(2), NAME + 1, BASE, prefs=[180, 200, 160, 135])
f.plane_name((3.1, 0), D_sub(1), NAME + 2, THEORY, prefs=[90, 70, 270])
f.plane_name(G1, D_sub(2), NAME + 2, BASE, prefs=[0, 340, 20])
f.render(
    "aci-kesit",
    "Arakesit doğrusuna dik bir kesit: <em>d</em> bir nokta, düzlemler iki doğru, normaller bu "
    "doğrulara dik iki ok olarak görünür. Normaller arasındaki açı ile doğrular arasındaki açı aynı "
    "<em>&#952;</em> açısıdır.",
    "A cross-section: two lines through the point d, the horizontal trace of D1 and the trace of D2 at "
    "60 degrees; the normals n1 and n2 drawn from d; the angle theta marked between the normals and "
    "again between the two lines")


# ===========================================================================
# 8. idz-aci-orijin: the normals n1 = (1, 1, 2) and n2 = (2, -1, 1) meet at pi/3
# ===========================================================================
n1, n2 = (1, 1, 2), (2, -1, 1)
assert vdot(n1, n2) == 3 and vdot(n1, n1) == 6 and vdot(n2, n2) == 6        # cos = 1/2
UD = (-1, -1, 1)
LU = vunit(UD)
W1, W2 = book_wings(Camera(35, 22), vunit(vcross(n1, LU)), vunit(vcross(n2, LU)), LU)
SL, SW = (-2.0, 2.0), (0.0, 1.9)
C1 = corners(O, LU, W1, SL, SW)
C2 = corners(O, LU, W2, SL, SW)
ext = C1 + C2 + [n1, n2, (3.0, 0, 0), (0, 2.6, 0), (0, 0, 2.9), (-1.6, 0, 0), (0, -1.6, 0), (0, 0, -1.6)]
f = Fig(35, 22, ext, width=560, pad=70)
f.S.polygon(C1, THEORY, 0.07)
f.S.polygon(C2, BASE, 0.08)
f.add_occluder(C1)
f.add_occluder(C2)
f.axes(((-1.6, 3.0), (-1.6, 2.6), (-1.6, 2.9)))
f.edges(C1, THEORY, 1.0, 0.45)
f.edges(C2, BASE, 1.0, 0.45)
f.line([vscale(-1.15, UD), vscale(1.15, UD)], TEXT, 1.3, "6 4", 0.55, w=0.5)
f.arc(O, n1, n2, 62, PRACTICE, 1.7, 1.0)
f.arrow(O, n1, THEORY, 2.8, 13.0, halo=True)
f.arrow(O, n2, BASE, 2.8, 13.0, halo=True)
f.point(O, TEXT, 3.8)
f.place(O, it("O"), NAME, prefs=[250, 290, 200])
f.place(n1, n_(1) + " = " + triple(1, 1, 2), NAME, THEORY, prefs=ahead(f, n1, (0, -40, 40, 80)))
f.place(n2, n_(2) + " = " + triple(2, -1, 1), NAME, BASE, prefs=ahead(f, n2, (0, 40, -40, -80)))
bis = vunit(vadd(vunit(n1), vunit(n2)))
f.place(vscale(f.u(84) / f.px_len(bis), bis), PI + "/3", NAME, PRACTICE, prefs=["c"], only=True)
f.place(vscale(1.15, UD), D_, NAME, TEXT, prefs=ahead(f, UD, (0, 30, -30)), opacity=0.8)
f.plane_name(C1[2], D_sub(1, NAME), NAME, THEORY, prefs=[180, 160, 200, 135])
f.plane_name(C2[2], D_sub(2, NAME), NAME, BASE, prefs=[0, 20, 340, 45])
f.render(
    "aci-orijin",
    "<em>n</em><sub>1</sub> = (1, 1, 2) ile <em>n</em><sub>2</sub> = (2, &#8722;1, 1) arasındaki açı "
    "<em>&#960;</em>/3 olup düzlemler arasındaki açı da budur. Soluk yarım düzlemler "
    "<em>x</em> + <em>y</em> + 2<em>z</em> = 0 ile 2<em>x</em> &#8722; <em>y</em> + <em>z</em> = 0 "
    "düzlemlerinin parçaları, kesikli doğru da onların arakesiti <em>d</em>&#8217;dir.",
    "Axes X, Y, Z; the normals n1 = (1, 1, 2) and n2 = (2, -1, 1) from the origin with the angle pi/3 "
    "between them, faint half-planes of x + y + 2z = 0 and 2x - y + z = 0 and their dashed line d")


# ===========================================================================
# 9. idz-eksen-parcalari-genel: intercepts a, b, c and the triangle they span
# ===========================================================================
A_, B_, C_ = (4.0, 0, 0), (0, 5.0, 0), (0, 0, 3.0)
TRI = [A_, B_, C_]
ext = TRI + [(5.4, 0, 0), (0, 6.4, 0), (0, 0, 4.2)]
f = Fig(35, 22, ext, width=560, pad=70)
f.S.polygon(TRI, THEORY, 0.16)
f.add_occluder(TRI)
f.axes(((0, 5.4), (0, 6.4), (0, 4.2)))
for P in TRI:
    f.oline(O, P, PRACTICE, 3.2, 1.0, hw=2.4, ho=0.9, hdash="7 4")     # behind the triangle: dashed
f.line(TRI + [A_], THEORY, 1.8)
for P in TRI:
    f.point(P, TEXT, 4.0)
f.point(O, TEXT, 3.4)
f.place(O, it("O"), NAME, prefs=[200, 225, 180])
f.place(A_, triple(it("a"), 0, 0), NAME, prefs=[300, 315, 285])
f.place(B_, triple(0, it("b"), 0), NAME, prefs=[270, 300, 250])
f.place(C_, triple(0, 0, it("c")), NAME, prefs=[180, 160, 200])
f.place(mid(O, A_), it("a"), NAME + 1, PRACTICE, prefs=[f.sang(A_) - 90, f.sang(A_) + 90])
f.place(mid(O, B_), it("b"), NAME + 1, PRACTICE, prefs=[f.sang(B_) - 90, f.sang(B_) + 90])
f.place(mid(O, C_), it("c"), NAME + 1, PRACTICE, prefs=[180, 0])
f.plane_name(mid(B_, C_), ": " + it("x") + "/" + it("a") + " + " + it("y") + "/" + it("b") + " + "
             + it("z") + "/" + it("c") + " = 1", NAME, THEORY, prefs=[45, 30, 60, 0])
f.render(
    "eksen-parcalari-genel",
    "Düzlem eksenleri (<em>a</em>, 0, 0), (0, <em>b</em>, 0), (0, 0, <em>c</em>) noktalarında keser; "
    "kalın parçalar eksen parçalarıdır. Bu üç noktanın üçgeni düzlemin bir parçasıdır.",
    "Axes X, Y, Z; the plane x/a + y/b + z/c = 1 as the translucent triangle with vertices (a, 0, 0), "
    "(0, b, 0), (0, 0, c), and the intercepts a, b, c as thick segments on the axes")


# ===========================================================================
# 10. idz-resim-pozitif: 2x + 3y + 4z - 12 = 0 through (6,0,0), (0,4,0), (0,0,3)
# ===========================================================================
A_, B_, C_ = (6, 0, 0), (0, 4, 0), (0, 0, 3)
for P in (A_, B_, C_):
    assert 2 * P[0] + 3 * P[1] + 4 * P[2] == 12
TRI = [A_, B_, C_]
ext = TRI + [(7.3, 0, 0), (0, 5.3, 0), (0, 0, 4.1)]
f = Fig(35, 22, ext, width=580, pad=70)
f.S.polygon(TRI, THEORY, 0.15)
f.add_occluder(TRI)
f.axes(((0, 7.3), (0, 5.3), (0, 4.1)))
f.line([A_, B_], BASE, 2.6)
f.line([A_, C_], PRACTICE, 2.6)
f.line([B_, C_], REMARK, 2.6)
for P in TRI:
    f.point(P, TEXT, 4.0)
f.point(O, TEXT, 3.4)
f.place(O, it("O"), NAME, prefs=[200, 225, 180])
f.place(A_, triple(6, 0, 0), NAME, prefs=[180, 200, 160])
f.place(B_, triple(0, 4, 0), NAME, prefs=[90, 60, 120])
f.place(C_, triple(0, 0, 3), NAME, prefs=[180, 160, 200])
f.place(mid(A_, B_, 0.55), eqn("2x + 3y = 12"), 13.0, BASE, prefs=[f.sang(vsub(B_, A_)) - 90, 300, 270])
f.place(mid(A_, C_, 0.5), eqn("x + 2z = 6"), 13.0, PRACTICE, prefs=[f.sang(vsub(C_, A_)) + 90, 150, 180])
f.place(mid(B_, C_, 0.45), eqn("3y + 4z = 12"), 13.0, REMARK, prefs=[f.sang(vsub(C_, B_)) - 90, 45, 30])
f.plane_name(vadd(vscale(0.22, A_), vadd(vscale(0.5, B_), vscale(0.28, C_))), "", NAME + 4, THEORY,
             prefs=["c"], only=True)
f.render(
    "resim-pozitif",
    "2<em>x</em> + 3<em>y</em> + 4<em>z</em> &#8722; 12 = 0 düzleminin birinci bölgedeki parçası. "
    "Üçgenin kenarları düzlemin izleri üzerindedir: <em>XY</em>-düzleminde 2<em>x</em> + 3<em>y</em> = 12, "
    "<em>XZ</em>-düzleminde <em>x</em> + 2<em>z</em> = 6, <em>YZ</em>-düzleminde 3<em>y</em> + 4<em>z</em> = 12.",
    "Axes X, Y, Z; the triangle with vertices (6, 0, 0), (0, 4, 0), (0, 0, 3) and its three sides "
    "labelled with the traces 2x + 3y = 12, x + 2z = 6 and 3y + 4z = 12")


# ===========================================================================
# 11. idz-resim-negatif: x - 2y + 3z + 6 = 0 through (-6,0,0), (0,3,0), (0,0,-2)
# ===========================================================================
A_, B_, C_ = (-6, 0, 0), (0, 3, 0), (0, 0, -2)
for P in (A_, B_, C_):
    assert P[0] - 2 * P[1] + 3 * P[2] + 6 == 0
TRI = [A_, B_, C_]
NEG = ((-7.0, 0, 0), (0, -2.0, 0), (0, 0, -3.0))
POS = ((3.0, 0, 0), (0, 4.2, 0), (0, 0, 3.0))
AZ11 = 35
f = Fig(AZ11, 22, TRI + list(NEG) + list(POS), width=580, pad=70)
f.S.polygon(TRI, PRACTICE, 0.15)
f.add_occluder(TRI)
for P in NEG:
    f.oline(P, O, TEXT, 1.2, 0.45)
f.axes(((0, 3.0), (0, 4.2), (0, 3.0)))
f.line(TRI + [A_], PRACTICE, 1.9)
for P in TRI:
    f.point(P, TEXT, 4.0)
f.point(O, TEXT, 3.4)
f.place(O, it("O"), NAME, prefs=[315, 290, 340])
f.place(A_, triple(-6, 0, 0), NAME, prefs=[90, 60, 120])
f.place(B_, triple(0, 3, 0), NAME, prefs=[20, 0, 35])
f.place(C_, triple(0, 0, -2), NAME, prefs=[180, 200, 160])
CX, CY = f.px(C_)
f.plane_name(("px", CX + 128, CY + 22), ": " + it("x") + "/(" + MINUS + "6) + " + it("y") + "/3 + " + it("z")
             + "/(" + MINUS + "2) = 1", NAME, PRACTICE, prefs=["c"], only=True)
f.render(
    "resim-negatif",
    "<em>x</em> &#8722; 2<em>y</em> + 3<em>z</em> + 6 = 0 düzlemi eksenleri (&#8722;6, 0, 0), (0, 3, 0) "
    "ve (0, 0, &#8722;2) noktalarında keser; üçgen <em>X</em> ve <em>Z</em> eksenlerinin negatif "
    "yanlarına uzanır. Eksenlerin negatif kısımları soluktur.",
    "Axes X, Y, Z with faint negative halves; the triangle with vertices (-6, 0, 0), (0, 3, 0), "
    "(0, 0, -2) of the plane x/(-6) + y/3 + z/(-2) = 1")


# ===========================================================================
# 12. idz-resim-orijin: x + y - z = 0 drawn with its three traces through O
# ===========================================================================
H = 1.2
PAT = [(-H, -H, -2 * H), (H, -H, 0.0), (H, H, 2 * H), (-H, H, 0.0)]
for P in PAT:
    assert abs(P[0] + P[1] - P[2]) < 1e-12
ext = PAT + [(2.4, 0, 0), (0, 2.4, 0), (0, 0, 2.9), (-1.8, 0, 0), (0, -1.8, 0), (0, 0, -2.7)]
f = Fig(35, 22, ext, width=560, pad=70)
f.S.polygon(PAT, THEORY, 0.14)
f.add_occluder(PAT)
f.axes(((-1.8, 2.4), (-1.8, 2.4), (-2.7, 2.9)))
f.edges(PAT, THEORY, 1.2, 0.8)
TXY = [(-H, H, 0.0), (H, -H, 0.0)]
TXZ = [(-H, 0.0, -H), (H, 0.0, H)]
TYZ = [(0.0, -H, -H), (0.0, H, H)]
f.line(TXY, BASE, 2.6)
f.line(TXZ, PRACTICE, 2.6)
f.line(TYZ, REMARK, 2.6)
for P in ((1, 0, 1), (0, 1, 1)):
    assert P[0] + P[1] - P[2] == 0
    f.point(P, TEXT, 4.0)
f.point(O, TEXT, 3.4)
f.place(O, it("O"), NAME, prefs=[250, 290, 225])
f.place((1, 0, 1), triple(1, 0, 1), NAME, prefs=[200, 180, 225])
f.place((0, 1, 1), triple(0, 1, 1), NAME, prefs=[20, 0, 45])
f.place(TXY[1], eqn("y = -x"), 13.0, BASE, prefs=ahead(f, vsub(TXY[1], TXY[0]), (0, -30, 30, -60)))
f.place(TXZ[1], eqn("z = x"), 13.0, PRACTICE, prefs=ahead(f, vsub(TXZ[1], TXZ[0]), (0, 30, -30, 60)))
f.place(TYZ[1], eqn("z = y"), 13.0, REMARK, prefs=ahead(f, vsub(TYZ[1], TYZ[0]), (0, -30, 30, -60)))
f.plane_name(PAT[2], eq("x + y - z"), NAME, THEORY, prefs=[0, 20, 340, 45])
f.render(
    "resim-orijin",
    "<em>x</em> + <em>y</em> &#8722; <em>z</em> = 0 düzlemi orijinden geçer; onu üç iziyle çizeriz: "
    "<em>XY</em>-düzleminde <em>y</em> = &#8722;<em>x</em>, <em>XZ</em>-düzleminde <em>z</em> = <em>x</em>, "
    "<em>YZ</em>-düzleminde <em>z</em> = <em>y</em>. Yama, |<em>x</em>|, |<em>y</em>| &#8804; 1,2 "
    "olan parçadır.",
    "Axes X, Y, Z; a parallelogram patch of the plane x + y - z = 0 over the square abs x, abs y at most "
    "1.2, its traces y = -x, z = x, z = y through O and the points (1, 0, 1), (0, 1, 1)")


# ===========================================================================
# 13. idz-x-ekseninden: y - 2z = 0 contains the X axis
# ===========================================================================
PAT = [(-1.0, 0, 0), (4.0, 0, 0), (4.0, 4.0, 2.0), (-1.0, 4.0, 2.0)]
for P in PAT:
    assert P[1] - 2 * P[2] == 0
EL13 = 38                                    # from higher up: the plane is steep and nearly edge-on at 22
ext = PAT + [(5.2, 0, 0), (-1.5, 0, 0), (0, 5.2, 0), (0, 0, 3.2)]
f = Fig(35, EL13, ext, width=560, pad=70)
f.S.polygon(PAT, THEORY, 0.15)
f.add_occluder(PAT)
f.axes(((-1.5, 5.2), (0, 5.2), (0, 3.2)))
f.edges(PAT, THEORY, 1.2, 0.8)
f.line([(-1.0, 0, 0), (4.0, 0, 0)], THEORY, 3.4)
f.line([O, (0, 4.0, 2.0)], BASE, 3.0)
A13, B13 = (0, 2, 1), (3, 2, 1)
f.arrow(A13, B13, PRACTICE, 1.8, 11.0, "6 4")
f.point(A13, TEXT, 4.0)
f.point(B13, TEXT, 4.0)
f.place(A13, triple(0, 2, 1), NAME, prefs=[45, 60, 30, 90])
f.place(B13, triple(3, 2, 1), NAME, prefs=[250, 270, 225, 290])
f.place((0, 4.0, 2.0), eqn("y = 2z") + " (" + eqn("x = 0") + ")", 13.0, BASE, prefs=[90, 60, 120, 45])
f.plane_name(PAT[2], eq("y - 2z"), NAME, THEORY, prefs=[0, 330, 30])
f.render(
    "x-ekseninden",
    "<em>y</em> &#8722; 2<em>z</em> = 0 düzlemi <em>X</em>-eksenini içerir (kalın mavi). "
    "<em>YZ</em>-düzlemindeki izi <em>y</em> = 2<em>z</em> doğrusudur; düzlem bu izin <em>X</em>-ekseni "
    "doğrultusunda kaydırılmasıyla oluşur: (0, 2, 1) düzlemdeyse (3, 2, 1) de düzlemdedir.",
    "Axes X, Y, Z; a patch of the plane y - 2z = 0 containing the X axis, its trace y = 2z in the YZ "
    "plane, and a dashed arrow from (0, 2, 1) to (3, 2, 1) parallel to the X axis")


# ===========================================================================
# 14. idz-z-eksenine-paralel: the wall 3x + 2y - 6 = 0
# ===========================================================================
W0, W1_ = (2.5, -0.75, 0.0), (-0.5, 3.75, 0.0)
for P in (W0, W1_, (2, 0, 0), (0, 3, 0)):
    assert abs(3 * P[0] + 2 * P[1] - 6) < 1e-12
WALL = [W0, W1_, (W1_[0], W1_[1], 3.0), (W0[0], W0[1], 3.0)]
ext = WALL + [(3.6, 0, 0), (0, 4.8, 0), (0, 0, 4.0)]
f = Fig(60, 22, ext, width=560, pad=70)            # at 35 degrees the wall would face the viewer squarely
f.S.polygon(WALL, THEORY, 0.15)
f.add_occluder(WALL)
f.axes(((0, 3.6), (0, 4.8), (0, 4.0)))
f.edges(WALL, THEORY, 1.2, 0.8)
f.line([W0, W1_], BASE, 3.0)
for P in ((2, 0, 0), (0, 3, 0)):
    f.point(P, TEXT, 4.0)
f.point(O, TEXT, 3.4)
f.place(O, it("O"), NAME, prefs=[200, 180, 225])
f.place((2, 0, 0), triple(2, 0, 0), NAME, prefs=[150, 170, 130])
f.place((0, 3, 0), triple(0, 3, 0), NAME, prefs=[300, 330, 270])
f.place(mid(W0, W1_, 0.35), eqn("3x + 2y = 6") + " (" + eqn("z = 0") + ")", 13.0, BASE,
        prefs=[f.sang(vsub(W1_, W0)) - 90, 270, 300], leader=True)
f.plane_name(mid(WALL[2], WALL[3], 0.3), eq("3x + 2y - 6"), NAME, THEORY, prefs=[80, 95, 65])
f.render(
    "z-eksenine-paralel",
    "3<em>x</em> + 2<em>y</em> &#8722; 6 = 0 düzlemi, <em>XY</em>-düzlemindeki izi 3<em>x</em> + 2<em>y</em> = 6 "
    "üzerinde dikilen bir duvardır. <em>Z</em>-eksenine paraleldir ama onu kesmez: eksen duvarın "
    "arkasında kalır (kesikli).",
    "Axes X, Y, Z; a vertical wall over the line 3x + 2y = 6 in the XY plane through (2, 0, 0) and "
    "(0, 3, 0); the Z axis stays behind the wall")


# ===========================================================================
# 15. idz-xz-paralel: the plane y = 4, parallel to the XZ plane
# ===========================================================================
S15 = 3.0
XZ = [(0, 0, 0), (S15, 0, 0), (S15, 0, S15), (0, 0, S15)]
PL = [(0, 4.0, 0), (S15, 4.0, 0), (S15, 4.0, S15), (0, 4.0, S15)]
ext = XZ + PL + [(4.0, 0, 0), (0, 5.6, 0), (0, 0, 4.0)]
f = Fig(35, 22, ext, width=560, pad=70)
f.S.polygon(XZ, TEXT, 0.05)
f.S.polygon(PL, THEORY, 0.15)
f.add_occluder(PL)
f.axes(((0, 4.0), (0, 5.6), (0, 4.0)))
for A, B in zip(XZ, XZ[1:] + XZ[:1]):
    f.line([A, B], TEXT, 1.0, "4 3", 0.45, w=0.3)
f.edges(PL, THEORY, 1.2, 0.8)
f.oline(O, (0, 4.0, 0), PRACTICE, 3.2, 1.0, hw=2.2, ho=0.9, hdash="7 4")
f.point((0, 4.0, 0), TEXT, 4.0)
f.place((0, 4.0, 0), triple(0, 4, 0), NAME, prefs=[300, 330, 270])
f.place((0, 2.0, 0), "4", NAME + 1, PRACTICE, prefs=[270, 300, 240])
f.plane_name(PL[2], ": " + it("y") + " = 4", NAME, THEORY, prefs=[160, 180, 135])
f.place(XZ[3], it("XZ") + "-düzlemi", 12.5, TEXT, prefs=[160, 180, 135, 90], opacity=0.8)
f.render(
    "xz-paralel",
    "<em>y</em> = 4 düzlemi <em>XZ</em>-düzlemine paraleldir: <em>XZ</em>-düzleminin <em>Y</em>-ekseni "
    "boyunca 4 birim kaydırılmışıdır ve <em>Y</em>-eksenini (0, 4, 0)&#8217;da dik keser.",
    "Axes X, Y, Z; a faint square of the XZ plane and the parallel square of the plane y = 4, which "
    "meets the Y axis at (0, 4, 0); the segment from O to (0, 4, 0) has length 4")


# ===========================================================================
# 16. idz-dogru-duzlemde: the line d lies in 6x - 2y + z - 1 = 0
# ===========================================================================
nD, vD, P16 = (6, -2, 1), (0, 2, 4), (-1, -2, 3)
assert vdot(nD, vD) == 0 and vdot(nD, P16) - 1 == 0
WD = vunit(vcross(nD, vD))


def d16(t, s=0.0):
    return vadd(vadd(P16, vscale(t, vD)), vscale(s, WD))


T16, S16 = 0.62, 1.25
PAT = [d16(-T16, -S16), d16(T16, -S16), d16(T16, S16), d16(-T16, S16)]
for P in PAT:
    assert abs(vdot(nD, P) - 1) < 1e-9
ext = PAT + [(2.0, 0, 0), (-2.2, 0, 0), (0, 1.6, 0), (0, -4.6, 0), (0, 0, 6.4)]
f = Fig(35, 22, ext, width=560, pad=70)
f.S.polygon(PAT, THEORY, 0.15)
f.add_occluder(PAT)
f.axes(((-2.2, 2.0), (-4.6, 1.6), (0, 6.4)))
f.edges(PAT, THEORY, 1.2, 0.8)
f.dline(d16(-T16 - 0.1), d16(T16 + 0.1), PRACTICE, 2.8)
V2, N3 = vscale(0.5, vD), vscale(1 / 3, nD)
f.right_angle(P16, V2, N3, 17)
f.arrow(P16, vadd(P16, V2), TEXT, 2.6, 12.0, halo=True)
f.arrow(P16, vadd(P16, N3), BASE, 2.6, 12.0, halo=True)
f.point(P16, TEXT, 4.0)
f.place(P16, triple(-1, -2, 3), NAME, prefs=[250, 225, 270, 200])
f.place(vadd(P16, V2), V_, NAME + 1, TEXT, prefs=ahead(f, vD, (-60, 60, -30, 30)))
f.place(vadd(P16, N3), N_, NAME + 1, BASE, prefs=ahead(f, nD, (0, -40, 40, 80)))
f.place(d16(T16 + 0.1), D_, NAME + 2, PRACTICE, prefs=ahead(f, vD, (0, 30, -30)))
f.plane_name(PAT[1], "", NAME + 2, THEORY, prefs=[0, 20, 340, 45])
f.render(
    "dogru-duzlemde",
    "<em>d</em> doğrusu 6<em>x</em> &#8722; 2<em>y</em> + <em>z</em> &#8722; 1 = 0 düzleminin içinde yatar: "
    "doğrultusu <em>v</em> = (0, 2, 4) normal <em>n</em> = (6, &#8722;2, 1)&#8217;e diktir ve "
    "(&#8722;1, &#8722;2, 3) noktası düzlemdedir. Oklar <em>v</em>/2 ve <em>n</em>/3 boyunda çizilmiştir.",
    "Axes X, Y, Z; a patch of the plane 6x - 2y + z - 1 = 0 with the line d inside it, the point "
    "(-1, -2, 3), the direction v and the normal n with a right-angle mark")


# ===========================================================================
# 17. idz-yz-paralel: the plane x = 4, parallel to the YZ plane
# ===========================================================================
LO, HI = -1.0, 3.0
PL = [(4.0, LO, LO), (4.0, HI, LO), (4.0, HI, HI), (4.0, LO, HI)]
YZ = [(0.0, LO, LO), (0.0, HI, LO), (0.0, HI, HI), (0.0, LO, HI)]
ext = PL + YZ + [(5.8, 0, 0), (0, 4.3, 0), (0, 0, 4.3), (0, -1.4, 0), (0, 0, -1.4)]
f = Fig(35, 22, ext, width=560, pad=70)
f.S.polygon(YZ, TEXT, 0.05)
f.S.polygon(PL, THEORY, 0.15)
f.add_occluder(PL)
f.axes(((0, 5.8), (-1.4, 4.3), (-1.4, 4.3)))
for A, B in zip(YZ, YZ[1:] + YZ[:1]):
    f.oline(A, B, TEXT, 1.0, 0.45, w=0.3, hw=0.9, ho=0.35)
f.edges(PL, THEORY, 1.2, 0.8)
f.point((4.0, 0, 0), TEXT, 4.0)
f.place((4.0, 0, 0), triple(4, 0, 0), NAME, prefs=[250, 225, 270])
f.plane_name(PL[2], ": " + it("x") + " = 4", NAME, THEORY, prefs=[20, 0, 45])
f.place(YZ[2], it("YZ") + "-düzlemi", 12.5, TEXT, prefs=[90, 60, 120], opacity=0.8)
f.render(
    "yz-paralel",
    "<em>x</em> = 4 düzlemi <em>YZ</em>-düzlemine paraleldir ve <em>X</em>-eksenini (4, 0, 0)&#8217;da "
    "dik keser; eksenin düzlemin arkasında kalan kısmı kesiklidir.",
    "Axes X, Y, Z; a square of the plane x = 4 crossing the X axis at (4, 0, 0) and a faint copy of "
    "the YZ plane behind it")


# ===========================================================================
# 18. idz-orta-dikme: the perpendicular bisector plane of QR
# ===========================================================================
Q18, R18 = (-2, 2, -3), (6, 4, 5)
M18 = vscale(0.5, vadd(Q18, R18))
n18 = (4, 1, 4)
assert M18 == (2, 3, 1) and vdot(n18, M18) == 15 and vscale(2, n18) == vsub(R18, Q18)
E1 = vunit(vcross(n18, E_Z))
E2 = vunit(vcross(n18, E1))
SQ = corners(M18, E1, E2, (-2.5, 2.5), (-2.5, 2.5))
ext = SQ + [Q18, R18, (7.0, 0, 0), (-3.0, 0, 0), (0, 5.4, 0), (0, 0, 6.0), (0, 0, -4.0)]
f = Fig(35, 22, ext, width=580, pad=70)
f.S.polygon(SQ, THEORY, 0.15)
f.add_occluder(SQ)
f.axes(((-3.0, 7.0), (0, 5.4), (-4.0, 6.0)))
f.edges(SQ, THEORY, 1.2, 0.8)
f.dline(Q18, R18, PRACTICE, 2.8)
f.right_angle(M18, vsub(R18, M18), E1, 18)
for A, B in ((Q18, M18), (M18, R18)):
    Cm = mid(A, B)
    tdir = vunit(vcross(vsub(B, A), f.d))
    f.line([vadd(Cm, vscale(-f.u(7), tdir)), vadd(Cm, vscale(f.u(7), tdir))], PRACTICE, 1.8, w=0.5)
for P in (Q18, R18, M18):
    f.point(P, TEXT, 4.0)
f.place(Q18, it("Q"), NAME + 1, prefs=[200, 180, 225])
f.place(R18, it("R"), NAME + 1, prefs=[20, 0, 45])
f.place(M18, P0_, NAME, prefs=[340, 320, 20])
f.plane_name(SQ[2], "", NAME + 2, THEORY, prefs=[20, 0, 45])
f.render(
    "orta-dikme",
    "[<em>QR</em>] doğru parçasının orta dikme düzlemi 4<em>x</em> + <em>y</em> + 4<em>z</em> &#8722; 15 = 0: "
    "orta nokta <em>P</em><sub>0</sub>(2, 3, 1)&#8217;den geçer ve <em>QR</em>&#8217;ye diktir. "
    "Doğru parçasının düzlemin arkasında kalan kısmı kesiklidir.",
    "Axes X, Y, Z; the points Q (-2, 2, -3) and R (6, 4, 5), the midpoint P0 (2, 3, 1), and a square "
    "of the plane 4x + y + 4z - 15 = 0 through P0 perpendicular to QR, with equal-length tick marks")


# ===========================================================================
# 19. idz-paralel-nokta: 2x - 3y - 5z + 6 = 0 and the parallel plane through P(-1, 2, 4)
# ===========================================================================
n19 = (2, -3, -5)
P19 = (-1, 2, 4)
assert vdot(n19, P19) + 28 == 0
C19 = vadd(P19, vscale(22 / 38, n19))                     # foot of P on the first plane
assert abs(vdot(n19, C19) + 6) < 1e-9
E1 = vunit(vcross(n19, E_Z))
E2 = vunit(vcross(n19, E1))
H19 = 1.9
PA = corners(C19, E1, E2, (-H19, H19), (-H19, H19))
PB = corners(P19, E1, E2, (-H19, H19), (-H19, H19))
AZ19, EL19 = 35, 22
ext = PA + PB + [(3.2, 0, 0), (0, 4.4, 0), (0, 0, 6.2)]
f = Fig(AZ19, EL19, ext, width=580, pad=70)
f.S.polygon(PA, BASE, 0.12)
f.S.polygon(PB, THEORY, 0.15)
f.add_occluder(PA)
f.add_occluder(PB)
f.axes(((0, 3.2), (0, 4.4), (0, 6.2)))
f.edges(PA, BASE, 1.1, 0.7)
f.edges(PB, THEORY, 1.2, 0.8)
for C, col in ((C19, BASE), (P19, THEORY)):
    normal_arrow(f, C, n19, length_px=80, color=col, prefs=ahead(f, n19, (-90, 90, 0)))
f.point(P19, TEXT, 4.0)
f.place(P19, it("P") + triple(-1, 2, 4), NAME, prefs=[160, 200, 135, 225])
f.place(PA[2], eqn("2x - 3y - 5z + 6 = 0"), 13.0, BASE, prefs=[0, 340, 20, 315], opacity=0.9)
f.plane_name(("px", 540, 480), eq("2x - 3y - 5z + 28"), 13.0, THEORY, prefs=["c"], only=True)
f.render(
    "paralel-nokta",
    "Aynı normale sahip iki paralel düzlem: soluk olanı verilen 2<em>x</em> &#8722; 3<em>y</em> &#8722; "
    "5<em>z</em> + 6 = 0 düzlemi, mavisi <em>P</em>(&#8722;1, 2, 4)&#8217;ten geçen "
    "2<em>x</em> &#8722; 3<em>y</em> &#8722; 5<em>z</em> + 28 = 0 düzlemidir.",
    "Axes X, Y, Z; two parallel plane patches 2x - 3y - 5z + 6 = 0 and 2x - 3y - 5z + 28 = 0 with the "
    "same normal n drawn from their centres, and the point P (-1, 2, 4) on the second one")


# ===========================================================================
# 20. idz-uzaklik-orijin (plane): a section along the normal of 6x - 6y + 7z = const
# ===========================================================================
assert vdot((6, -6, 7), (6, -6, 7)) == 121
f = Flat((-3.9, 5.9), (-2.35, 2.45), width=480, pad=40)
f.arrow((-3.7, 0), (5.7, 0), TEXT, 1.3, 10.0, None, 0.75)
f.place((5.7, 0), N_, NAME + 1, TEXT, prefs=[0, 20, 340], d=6)
f.line([(4, -1.9), (4, 1.9)], TEXT, 1.2, "5 4", 0.5)
f.line([(-2, -1.9), (-2, 1.9)], BASE, 2.6)
f.line([(2, -1.9), (2, 1.9)], THEORY, 2.6)
for x, s in ((2, 1), (-2, -1)):
    flat_right_angle(f, (x, 0), 90, 180 if s > 0 else 0, 11)


def dim(f, x0, x1, y, text, above=True, color=TEXT, at=0.5):
    """A dimension arrow between x0 and x1 at height y with its value (at a fraction `at`)."""
    xm = x0 + at * (x1 - x0)
    f.arrow((xm, y), (x1, y), color, 1.2, 8.0, None, 0.85, w=0.4)
    f.arrow((xm, y), (x0, y), color, 1.2, 8.0, None, 0.85, w=0.4)
    f.place((xm, y), text, NAME, color, prefs=[90 if above else 270], only=True, d=4)


dim(f, 0, 2, 0.42, "2")
dim(f, -2, 0, 0.42, "2")
dim(f, 0, 4, -1.25, "4", above=False, at=0.25)
f.line([(0, -0.1), (0, -1.4)], TEXT, 0.8, "2 2", 0.5, w=0.2)
f.line([(4, -1.1), (4, -1.4)], TEXT, 0.8, None, 0.5, w=0.2)
for P in ((0, 0), (2, 0), (-2, 0)):
    f.point(P, TEXT, 4.0)
f.place((0, 0), it("O"), NAME, prefs=[315, 300, 330], d=5)
f.place((2, 0), it("H"), NAME, prefs=[315, 300, 330], d=5)
f.place((-2, 0), it("H") + "′", NAME, prefs=[315, 300, 330], d=5)
f.place((2, -1.9), eqn("6x - 6y + 7z - 22 = 0"), 12.5, THEORY, prefs=[270], only=True)
f.place((-2, 1.9), eqn("6x - 6y + 7z + 22 = 0"), 12.5, BASE, prefs=[90], only=True)
f.place((4, 1.9), eqn("6x - 6y + 7z - 44 = 0"), 12.5, TEXT, prefs=[90], only=True, opacity=0.75)
f.render(
    "uzaklik-orijin",
    "Normal doğrultusundaki kesit: düzlemler <em>n</em>&#8217;ye dik doğrular olarak görünür. "
    "Orijinin iki yanında, ona 2 birim uzaklıkta iki paralel düzlem vardır; kesikli doğru, "
    "orijine uzaklığı 4 olan verilen düzlemdir.",
    "A section along the normal n: the origin O on a horizontal axis, the planes 6x - 6y + 7z - 22 = 0 "
    "and 6x - 6y + 7z + 22 = 0 as vertical lines at distance 2 on either side with feet H and H', and "
    "the given plane 6x - 6y + 7z - 44 = 0 dashed at distance 4")


# ===========================================================================
# 21. idz-iki-duzleme-dik: the plane through P0 perpendicular to D1 and D2
# ===========================================================================
nA, nB, nC = (2, -2, -4), (3, 1, 6), (1, 3, -1)
P21 = (1, 1, 2)
assert vcross(nA, nB) == vscale(-8, nC) and vdot(nC, P21) - 2 == 0
A21 = (1.75, -1.25, 0.0)                                   # a point of D1 and D2
assert abs(vdot(nA, A21) - 6) < 1e-12 and abs(vdot(nB, A21) - 4) < 1e-12
F21 = vadd(A21, vscale(4 / 11, nC))                       # where their line meets D
assert abs(vdot(nC, F21) - 2) < 1e-12
LU = vunit(nC)
M21 = mid(F21, P21)
E1 = vunit(vsub(P21, F21))
E2 = vunit(vcross(nC, E1))
PD = corners(M21, E1, E2, (-2.4, 2.4), (-2.2, 2.2))
WA, WB = vunit(vcross(nA, LU)), vunit(vcross(nB, LU))
SA = corners(F21, LU, WA, (-2.6, 2.6), (-1.5, 1.5))
SB = corners(F21, LU, WB, (-2.6, 2.6), (-1.5, 1.5))
AZ21, EL21 = 75, 35                         # no axes here: a view that opens all three planes
f = Fig(AZ21, EL21, PD + SA + SB, width=580, pad=70)
f.S.polygon(SA, THEORY, 0.08)
f.S.polygon(SB, BASE, 0.09)
f.S.polygon(PD, PRACTICE, 0.15)
for C in (SA, SB, PD):
    f.add_occluder(C)
f.edges(SA, THEORY, 1.0, 0.5)
f.edges(SB, BASE, 1.0, 0.5)
f.edges(PD, PRACTICE, 1.2, 0.85)
f.oline(vadd(F21, vscale(-2.9, LU)), vadd(F21, vscale(2.9, LU)), TEXT, 2.2, 0.9, hw=1.4, ho=0.7, hdash="6 4")
for W in (vunit(vcross(nC, nA)), vunit(vcross(nC, nB))):
    f.oline(vadd(F21, vscale(-2.2, W)), vadd(F21, vscale(2.2, W)), TEXT, 1.0, 0.7)
normal_arrow(f, P21, nC, length_px=70, color=PRACTICE, prefs=ahead(f, nC, (0, 40, -40)))
f.point(P21, TEXT, 4.0)
f.point(F21, TEXT, 3.0)
f.place(P21, P0_ + triple(1, 1, 2), NAME, prefs=[200, 225, 180, 250])
f.place(vadd(F21, vscale(2.9, LU)), D_ + sub("12", NAME), NAME + 1, TEXT, prefs=ahead(f, LU, (0, 30, -30)))
f.plane_name(SA[2], D_sub(1), NAME + 1, THEORY, prefs=[0, 30, 330])
f.plane_name(SB[2], D_sub(2), NAME + 1, BASE, prefs=[0, 30, 330])
f.plane_name(PD[3], "", NAME + 2, PRACTICE, prefs=[180, 200, 160])
f.render(
    "iki-duzleme-dik",
    "<em>P</em><sub>0</sub>(1, 1, 2)&#8217;den geçen ve iki düzleme birden dik olan düzlem: "
    "normali <em>n</em> = (1, 3, &#8722;1), <em>d</em><sub>12</sub> arakesit doğrusuna paraleldir; "
    "bu yüzden düzlem <em>d</em><sub>12</sub>&#8217;ye diktir ve iki düzlemi ince çizgiler boyunca keser.",
    "Two faint plane patches D1 and D2 meeting along the dashed line d12, and an orange patch D through "
    "P0 (1, 1, 2) perpendicular to d12, with its normal n = (1, 3, -1) parallel to d12")


# ---------------------------------------------------------------------------
for name, content in OUT.items():
    path = OUT_DIR / f"analytic-idz-{name}.md"
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(content)
    print("wrote", path.name)
