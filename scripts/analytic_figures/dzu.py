# -*- coding: utf-8 -*-
"""Figures for dersler/analitik-geometri/dogru-ile-duzlem-ve-uzakliklar.qmd (chapter key: dzu).

Three-dimensional drawings go through scripts/svg_plot3.py (an orthographic
Camera on an equal-aspect svg_plot.Plot panel). The figures go INSIDE the box
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

Usage:   python scripts/analytic_figures/dzu.py
         python scripts/center_figures.py "analytic-dzu-*.md" --keep-width
Output:  scripts/_figures/analytic-dzu-<name>.md
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

MINUS, PHI, THETA, ELL, LAMBDA = "−", "φ", "θ", "ℓ", "λ"
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
        lim = getattr(self, "bounds", None)
        if lim and (box[0] < lim[0] + 4 or box[1] < lim[1] + 4 or box[2] > lim[2] - 4 or box[3] > lim[3] - 4):
            c += 300
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

    def __init__(self, az, el, extent, width=600, pad=70, max_h=None, x0=0.0, y0=0.0, ppu=None,
                 level=None, up=None):
        super().__init__()
        self.cam = Camera(az, el)
        if level is not None:
            # roll the camera about its viewing axis so that the direction `level` runs
            # horizontally on the page (only for scenes drawn without coordinate axes)
            r, u = self.cam.r, self.cam.u
            a = math.atan2(vdot(level, u), vdot(level, r))
            if up is not None and vdot(up, vadd(vscale(-math.sin(a), r), vscale(math.cos(a), u))) < 0:
                a += math.pi                      # keep `up` pointing up on the page
            c, s_ = math.cos(a), math.sin(a)
            self.cam.r = vadd(vscale(c, r), vscale(s_, u))
            self.cam.u = vadd(vscale(-s_, r), vscale(c, u))
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
        self.bounds = (x0, y0, x0 + self.W, y0 + self.H)
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


def corner(f, C, key):
    """The patch corner that is extreme on the page: 'top', 'bottom', 'left' or 'right'."""
    k = {"top": lambda P: f.px(P)[1], "bottom": lambda P: -f.px(P)[1],
         "left": lambda P: f.px(P)[0], "right": lambda P: -f.px(P)[0]}[key]
    return min(C, key=k)


def mid(A, B, t=0.5):
    return vadd(A, vscale(t, vsub(B, A)))


# ===========================================================================
# 1. dzu-durumlar: a line meeting a plane, parallel to it, lying in it
# ===========================================================================
AZ1, EL1 = 30, 26
PS = 2.6                                          # half side of the plane patch
E_X, E_Y, E_Z = (1.0, 0, 0), (0, 1.0, 0), (0, 0, 1.0)
ext1 = [(x, y, z) for x in (-PS, PS) for y in (-PS, PS) for z in (-2.5, 2.5)]
cam1 = Camera(AZ1, EL1)
_pr = [cam1.project(P) for P in ext1]
PPU1 = 212 / (max(p[0] for p in _pr) - min(p[0] for p in _pr))
PANEL_W = 212 + 2 * 18
TITLES = ("kesişen", "yalnız paralel", "düzlemde yatan")
panels = []
for k in range(3):
    f = Fig(AZ1, EL1, ext1, pad=18, x0=k * PANEL_W, y0=18, ppu=PPU1)
    C = f.patch(O, E_X, E_Y, (-PS, PS), (-PS, PS))
    f.edges(C)
    NQ = (-1.5, 1.9, 0)
    if k == 0:
        A, B = (-1.2, 0, -2.4), (1.2, 0, 2.4)
        f.dline(A, B, TEXT, 2.4)
        f.point(O, TEXT, 4.0)
        f.place(O, it("K"), NAME, prefs=[200, 180, 160])
        f.place(B, D_, NAME + 1, prefs=[0, 20, 340])
    elif k == 1:
        A, B = (0.3, -2.1, 1.5), (0.3, 1.5, 1.5)
        f.line([(0.3, -2.1, 0), (0.3, 1.5, 0)], TEXT, 1.1, "4 3", 0.55, w=0.6)
        for P in (A, B):
            f.line([P, (P[0], P[1], 0)], TEXT, 1.0, "3 3", 0.45, w=0.5)
        f.line([A, B], TEXT, 2.4)
        f.place(A, D_, NAME + 1, prefs=[160, 180, 140])
    else:
        A, B = (-2.3, -2.3, 0), (2.3, 2.3, 0)
        f.line([A, B], TEXT, 2.6)
        f.place(B, D_, NAME + 1, prefs=[270, 300, 240])
    normal_arrow(f, NQ, (0, 0, 1.2), prefs=[0, 30, 330])
    f.plane_name(C[1], "", NAME + 3, THEORY, prefs=[200, 225, 180])
    f.text_px(k * PANEL_W + PANEL_W / 2, 20, TITLES[k], 13.5, TEXT, 1.0, halo=False)
    f.emit()
    panels.append(f)
W1 = 3 * PANEL_W
H1 = max(f.H for f in panels) + 18
OUT["durumlar"] = figure(round(W1), round(H1), [f.p for f in panels],
    "Bir doğru ile bir düzlem: solda doğru düzlemi tek bir <em>K</em> noktasında deler (düzlemin "
    "arkasında kalan parçası kesikli), ortada düzleme paraleldir ve onu hiç kesmez (kesikli çizgi, "
    "doğrunun düzlemdeki dik izdüşümüdür), sağda tamamen düzlemin içinde yatar.",
    WIDE,
    "Three panels with the same horizontal plane and its normal n: a line d piercing the plane at K, "
    "a line d parallel to the plane above it, and a line d lying in the plane")
print("-- durumlar")


# ===========================================================================
# 2. dzu-ortak-nokta: the points of d are P0 + lambda v; K is the one on the plane
# ===========================================================================
AZ, EL = 30, 20
P0 = (1.6, -2.3, 2.4)
Vv = (-0.45, 0.95, -1.2)
lamK = -P0[2] / Vv[2]
K = vadd(P0, vscale(lamK, Vv))
assert abs(K[2]) < 1e-12
A, B = vadd(P0, vscale(-0.55, Vv)), vadd(P0, vscale(3.1, Vv))
ext = [(x, y, 0) for x in (-3, 3) for y in (-3.4, 3.4)] + [A, B, (-1.8, 2.3, 1.5)]
f = Fig(AZ, EL, ext, width=520, pad=70)
C = f.patch(O, E_X, E_Y, (-3, 3), (-3.4, 3.4))
f.edges(C)
f.dline(A, B, TEXT, 2.2)
f.arrow(P0, vadd(P0, Vv), PRACTICE, 3.0, 13.0, halo=True)
normal_arrow(f, (-1.8, 2.3, 0), (0, 0, 1.5), prefs=[0, 30, 330])
f.point(P0, TEXT, 4.0)
f.point(K, TEXT, 4.0)
f.place(P0, P0_, NAME, prefs=[180, 150, 210])
f.place(vadd(P0, vscale(0.55, Vv)), V_, NAME + 1, PRACTICE, prefs=[f.sang(Vv) + 90, f.sang(Vv) - 90])
f.place(K, it("K") + " = " + P0_ + " + " + it(LAMBDA) + V_, NAME, prefs=[0, 340, 20, 315])
f.place(A, D_, NAME + 1, prefs=[180, 150, 210])
f.plane_name(C[1], "", NAME + 3, THEORY, prefs=[200, 225, 180])
f.render(
    "ortak-nokta",
    "<em>d</em> doğrusunun noktaları <em>P</em><sub>0</sub> + <em>&#955;v</em> biçimindedir. Bu noktalardan "
    "düzlemin denklemini sağlayan tek nokta <em>K</em>&#8217;dır; <em>&#955;</em> değeri (1)&#8217;den "
    "bulunur. Doğrunun düzlemin arkasında kalan parçası kesiklidir.",
    "A horizontal plane with normal n, a point P0 above it, the direction vector v from P0, and the line "
    "d = P0 + lambda v piercing the plane at K; the part of d below the plane is dashed")


# ===========================================================================
# 3. dzu-dik: d perpendicular to the plane, v parallel to n
# ===========================================================================
K = (0.4, -0.6, 0)
A, B = vadd(K, (0, 0, -2.0)), vadd(K, (0, 0, 3.0))
NQ = (-1.2, 2.4, 0)
ext = [(x, y, 0) for x in (-3, 3) for y in (-3.4, 3.4)] + [A, B]
f = Fig(AZ, EL, ext, width=520, pad=70)
C = f.patch(O, E_X, E_Y, (-3, 3), (-3.4, 3.4))
f.edges(C)
f.line([vadd(K, (-2.2, 0, 0)), vadd(K, (2.2, 0, 0))], TEXT, 1.2, None, 0.6, w=0.8)
f.line([vadd(K, (0, -2.4, 0)), vadd(K, (0, 2.4, 0))], TEXT, 1.2, None, 0.6, w=0.8)
f.dline(A, B, TEXT, 2.2)
f.arrow(vadd(K, (0, 0, 1.0)), vadd(K, (0, 0, 2.4)), PRACTICE, 3.2, 13.0, halo=True)
normal_arrow(f, NQ, (0, 0, 1.4), prefs=[0, 30, 330])
f.right_angle(K, (0, 0, 1), (1, 0, 0), 14)
f.right_angle(K, (0, 0, 1), (0, 1, 0), 14)
f.point(K, TEXT, 4.0)
f.place(K, it("K"), NAME, prefs=[305, 315, 295], d=10)
f.place(vadd(K, (0, 0, 1.7)), V_, NAME + 1, PRACTICE, prefs=[0, 180])
f.place(B, D_, NAME + 1, prefs=[0, 20, 340])
f.plane_name(C[1], "", NAME + 3, THEORY, prefs=[200, 225, 180])
f.render(
    "dik",
    "Düzleme dik doğru: <em>d</em>&#8217;nin doğrultman vektörü <em>v</em>, düzlemin normali <em>n</em> "
    "ile aynı doğrultudadır. Bu yüzden <em>d</em>, düzlemin <em>K</em>&#8217;dan geçen her doğrusuna "
    "diktir; şekilde bunlardan ikisi gösterilmiştir.",
    "A horizontal plane, a vertical line d through the point K of the plane with its direction vector v, "
    "a parallel normal n elsewhere on the plane, and right-angle marks between d and two lines of the "
    "plane through K")


# ===========================================================================
# 4. dzu-aci: the angle phi between d and its projection d' onto the plane
# ===========================================================================
PHI_DEG = 34.0
hdir = vunit((-0.3, 1.0, 0))
wdir = vadd(vscale(math.cos(math.radians(PHI_DEG)), hdir), (0, 0, math.sin(math.radians(PHI_DEG))))
K = (1.1, -1.9, 0)
P = vadd(K, vscale(3.4, wdir))
H = (P[0], P[1], 0)
A, B = vadd(K, vscale(-1.0, wdir)), vadd(K, vscale(4.6, wdir))
Dp = vadd(K, vscale(4.6 * math.cos(math.radians(PHI_DEG)), hdir))
NQ = (-2.0, 2.2, 0)
ext = [(x, y, 0) for x in (-3, 3) for y in (-3.4, 3.4)] + [A, B, vadd(NQ, (0, 0, 1.5))]
f = Fig(AZ, EL, ext, width=520, pad=70)
C = f.patch(O, E_X, E_Y, (-3, 3), (-3.4, 3.4))
f.edges(C)
f.line([K, Dp], BASE, 1.8, None, 0.95)
f.dline(A, B, TEXT, 2.2)
f.line([P, H], TEXT, 1.6, "5 4", 0.9)
normal_arrow(f, NQ, (0, 0, 1.5), prefs=[0, 30, 330])
f.right_angle(H, vsub(P, H), vsub(K, H), 13)
f.arc(K, vsub(H, K), vsub(P, K), 40, TEXT, 1.4)
f.arc(P, vsub(K, P), vsub(H, P), 30, TEXT, 1.4)
for Q in (K, P, H):
    f.point(Q, TEXT, 4.0)
bis = vunit(vadd(vunit(vsub(H, K)), vunit(vsub(P, K))))
f.place(vadd(K, vscale(f.u(56), bis)), it(PHI), NAME + 1, prefs=["c"], only=True)
bis = vunit(vadd(vunit(vsub(K, P)), vunit(vsub(H, P))))
f.place(vadd(P, vscale(f.u(44), bis)), it(THETA), NAME + 1, prefs=["c"], only=True)
f.place(K, it("K"), NAME, prefs=[225, 250, 200, 180])
f.place(P, it("P"), NAME, prefs=[135, 110, 160, 90])
f.place(H, it("H"), NAME, prefs=[0, 330, 300])
f.place(B, D_, NAME + 1, prefs=[0, 20, 340])
f.place(Dp, D_ + "&#8242;", NAME + 1, BASE, prefs=[0, 340, 20])
f.plane_name(C[1], "", NAME + 3, THEORY, prefs=[200, 225, 180])
f.render(
    "aci",
    "Doğru ile düzlem arasındaki açı: <em>P</em>&#8217;den inen dikmenin ayağı <em>H</em>&#8217;dir ve "
    "<em>d</em>&#8242; = <em>KH</em>, <em>d</em>&#8217;nin düzlemdeki izdüşümüdür. <em>&#966;</em>, "
    "<em>d</em> ile <em>d</em>&#8242; arasındaki açıdır; <em>PHK</em> dik üçgeninde "
    "<em>&#966;</em> + <em>&#952;</em> = <em>&#960;</em>/2 olur.",
    "A horizontal plane, a line d meeting it at K, a point P on d with the dashed perpendicular PH to "
    "the plane, the projection d' through K and H, the angle phi at K between d and d', the angle theta "
    "at P, and a normal n")


# ===========================================================================
# 5. dzu-nokta-duzlem: the perpendicular P0 S is shorter than any other P0 P
# ===========================================================================
P0 = (0.8, -1.2, 2.7)
S = (P0[0], P0[1], 0)
P = (1.4, 1.9, 0)
NQ = (-2.0, 2.4, 0)
ext = [(x, y, 0) for x in (-3, 3) for y in (-3.4, 3.4)] + [P0, vadd(NQ, (0, 0, 1.5))]
f = Fig(AZ, EL, ext, width=520, pad=70)
C = f.patch(O, E_X, E_Y, (-3, 3), (-3.4, 3.4))
f.edges(C)
f.line([S, P], TEXT, 1.4, None, 0.8)
f.line([P0, P], TEXT, 2.0)
f.line([P0, S], TEXT, 1.8, "5 4", 0.95)
normal_arrow(f, NQ, (0, 0, 1.5), prefs=[0, 30, 330])
f.right_angle(S, (0, 0, 1), vsub(P, S), 13)
f.arc(P0, vsub(S, P0), vsub(P, P0), 34, TEXT, 1.4)
for Q in (P0, S, P):
    f.point(Q, TEXT, 4.0)
bis = vunit(vadd(vunit(vsub(S, P0)), vunit(vsub(P, P0))))
f.place(vadd(P0, vscale(f.u(48), bis)), it(THETA), NAME + 1, prefs=["c"], only=True)
f.place(P0, P0_, NAME, prefs=[90, 120, 150])
f.place(S, it("S"), NAME, prefs=[225, 200, 250])
f.place(P, it("P"), NAME, prefs=[315, 0, 290])
f.place(mid(P0, S, 0.62), it(ELL), NAME + 1, prefs=[180, 160, 200])
f.plane_name(C[1], "", NAME + 3, THEORY, prefs=[200, 225, 180])
f.render(
    "nokta-duzlem",
    "<em>P</em><sub>0</sub>&#8217;dan düzleme inen dikmenin ayağı <em>S</em>, düzlemin başka bir noktası "
    "<em>P</em>&#8217;dir. <em>P</em><sub>0</sub><em>SP</em> üçgeni <em>S</em>&#8217;de dik açılıdır ve "
    "<em>&#8467;</em> = |<em>P</em><sub>0</sub><em>S</em>| = |<em>P</em><sub>0</sub><em>P</em>| "
    "|cos <em>&#952;</em>| olur.",
    "A horizontal plane with normal n, a point P0 above it, the dashed perpendicular P0S of length l with "
    "a right angle at S, another point P of the plane, the segment P0P and the angle theta at P0")


# ===========================================================================
# 6. dzu-paralel-duzlemler: two parallel planes with the common normal n
# ===========================================================================
HZ = 2.7
P0 = (0.6, -0.9, HZ)
P = (P0[0], P0[1], 0)
NQ = (-1.9, 2.3, HZ)
ext = [(x, y, z) for x in (-3, 3) for y in (-3.4, 3.4) for z in (0, HZ)] + [vadd(NQ, (0, 0, 1.5))]
f = Fig(AZ, EL, ext, width=520, pad=70)
C2 = f.patch(O, E_X, E_Y, (-3, 3), (-3.4, 3.4), BASE, 0.12)
C1 = f.patch((0, 0, HZ), E_X, E_Y, (-3, 3), (-3.4, 3.4), THEORY, 0.13)
f.edges(C2, BASE)
f.edges(C1, THEORY)
f.line([P0, P], TEXT, 1.8, "5 4", 0.95)
f.right_angle(P, (0, 0, 1), (1, 0, 0), 13)
normal_arrow(f, NQ, (0, 0, 1.5), prefs=[0, 30, 330])
f.point(P0, TEXT, 4.0)
f.point(P, TEXT, 4.0)
f.place(P0, P0_ + "(" + it("x") + sub(0) + ", " + it("y") + sub(0) + ", " + it("z") + sub(0) + ")",
        NAME, prefs=[165, 180, 150, 135])
f.place(P, it("P") + "(" + it("x") + ", " + it("y") + ", " + it("z") + ")", NAME, prefs=[195, 180, 210])
f.place(mid(P0, P, 0.45), it(ELL), NAME + 1, prefs=[0, 20, 340])
f.plane_name(C1[1], sub(1, NAME + 3), NAME + 3, THEORY, prefs=[200, 225, 180])
f.plane_name(C2[1], sub(2, NAME + 3), NAME + 3, BASE, prefs=[200, 225, 180])
f.render(
    "paralel-duzlemler",
    "Paralel iki düzlemin normali ortaktır: ikisi de aynı <em>n</em> vektörüne diktir. Üstteki "
    "düzlemin <em>P</em><sub>0</sub> noktasından alttaki düzleme inen dikmenin uzunluğu "
    "<em>&#8467;</em>, iki düzlem arasındaki uzaklıktır.",
    "Two parallel horizontal planes D1 above and D2 below with their common normal n, a point P0 on D1, "
    "the dashed perpendicular of length l down to its foot P on D2, and a right angle at P")


# ===========================================================================
# 7. dzu-duzlemde-yatan: d = (-1 + 3l, 2l, -3l) lies in x + z + 1 = 0
# ===========================================================================
AZ7, EL7 = 65, 15
P0 = (-1, 0, 0)
Vv, Nn = (3, 2, -3), (1, 0, 1)
assert vdot(Vv, Nn) == 0 and P0[0] + P0[2] + 1 == 0
A, B = vadd(P0, vscale(-1.2, Vv)), vadd(P0, vscale(1.2, Vv))
e1 = (1, 0, -1)
ext = [vadd(P0, vadd(vscale(a, e1), (0, b, 0))) for a in (-3.8, 3.8) for b in (-3, 3)] + \
      [(4, 0, 0), (0, 4, 0), (0, 0, 4.5), (0, -3.5, 0)]
f = Fig(AZ7, EL7, ext, width=540, pad=70)
C = f.patch(P0, e1, E_Y, (-3.8, 3.8), (-3, 3))
assert f.front(Nn)
f.axes(((-5, 4), (-3.5, 4), (-4, 4.5)))
f.edges(C)
f.line([A, B], TEXT, 2.4)
f.arrow(P0, vadd(P0, Vv), PRACTICE, 3.0, 13.0, halo=True)
f.arrow(P0, vadd(P0, Nn), BASE, 3.0, 13.0, halo=True)
f.point(P0, TEXT, 4.0)
f.place(P0, P0_, NAME, prefs=[160, 135, 180, 200])
f.place(vadd(P0, vscale(0.62, Vv)), V_, NAME + 1, PRACTICE, prefs=[f.sang(Vv) + 90, f.sang(Vv) - 90])
f.place(vadd(P0, Nn), N_, NAME + 1, BASE, prefs=ahead(f, Nn, (0, -45, 45, -90, 90)))
f.place(A, D_, NAME + 1, prefs=[f.sang(Vv) + 90, f.sang(Vv) + 180, f.sang(Vv) - 90])
f.plane_name(corner(f, C, "bottom"), eq("x + z + 1"), NAME, THEORY, prefs=[340, 0, 320])
f.render(
    "duzlemde-yatan",
    "<em>d</em> doğrusu düzlemin içinde yatar: doğrultman vektörü <em>v</em> = (3, 2, &#8722;3), "
    "düzlemin normali <em>n</em> = (1, 0, 1)&#8217;e diktir ve <em>P</em><sub>0</sub>(&#8722;1, 0, 0) "
    "düzlemin üzerindedir. Eksenlerin düzlemin arkasında kalan kısımları kesiklidir.",
    "Axes X, Y, Z and the plane x + z + 1 = 0 with the line d = (-1 + 3 lambda, 2 lambda, -3 lambda) "
    "inside it, the point P0(-1, 0, 0), the direction vector v = (3, 2, -3) along d and the normal "
    "n = (1, 0, 1) at P0")


# ===========================================================================
# 8. dzu-kesisen: d = (1 + 2l, -1 + l, 2 - l) meets x + 2y + z - 7 = 0 at K(5, 1, 0)
# ===========================================================================
P0, Vv, Nn = (1, -1, 2), (2, 1, -1), (1, 2, 1)
K = vadd(P0, vscale(2, Vv))
assert K == (5, 1, 0) and K[0] + 2 * K[1] + K[2] - 7 == 0 and vdot(Nn, Vv) == 3
e1, e2 = vunit((1, 0, -1)), vunit((-1, 1, -1))
assert abs(vdot(e1, Nn)) < 1e-12 and abs(vdot(e2, Nn)) < 1e-12
S1, S2 = (-1.6, 3.6), (-2.2, 2.2)
A, B = vadd(P0, vscale(-0.5, Vv)), vadd(P0, vscale(3, Vv))
ext = [vadd(K, vadd(vscale(a, e1), vscale(b, e2))) for a in S1 for b in S2] + \
      [A, B, (7.5, 0, 0), (0, 4.5, 0), (0, 0, 4.5), (0, -2, 0), (0, 0, -2)]
f = Fig(35, 22, ext, width=540, pad=70)
C = f.patch(K, e1, e2, S1, S2)
f.axes(((-1, 7.5), (-2, 4.5), (-2, 4.5)))
f.edges(C)
f.dline(A, B, TEXT, 2.4)
f.arrow(P0, vadd(P0, Vv), PRACTICE, 3.0, 13.0, halo=True)
f.arrow(K, vadd(K, Nn), BASE, 3.0, 13.0, halo=True)
f.point(P0, TEXT, 4.0)
f.point(K, TEXT, 4.0)
f.place(P0, P0_, NAME, prefs=[90, 120, 60, 150])
f.place(vadd(P0, vscale(0.55, Vv)), V_, NAME + 1, PRACTICE, prefs=[f.sang(Vv) - 90, f.sang(Vv) + 90])
f.place(vadd(K, Nn), N_, NAME + 1, BASE, prefs=ahead(f, Nn, (0, -45, 45, -90, 90)))
f.place(K, it("K") + triple(5, 1, 0), NAME, prefs=[315, 290, 340, 0, 270])
f.place(B, D_, NAME + 1, prefs=[f.sang(Vv) - 90, f.sang(Vv), f.sang(Vv) + 90])
f.plane_name(corner(f, C, "bottom"), eq("x + 2y + z - 7"), NAME, THEORY, prefs=[0, 340, 20])
f.render(
    "kesisen",
    "<em>d</em> doğrusu düzlemi <em>K</em>(5, 1, 0) noktasında keser: <em>&#10216;n</em>, "
    "<em>v&#10217;</em> = 3 &#8800; 0&#8217;dır. <em>v</em> = (2, 1, &#8722;1), <em>P</em><sub>0</sub>(1, "
    "&#8722;1, 2)&#8217;dan; <em>n</em> = (1, 2, 1), <em>K</em>&#8217;dan çizilmiştir. Doğrunun ve "
    "eksenlerin düzlemin arkasında kalan kısımları kesiklidir.",
    "Axes, the plane x + 2y + z - 7 = 0 around K(5, 1, 0), the line d through P0(1, -1, 2) with direction "
    "v = (2, 1, -1) crossing the plane at K, and the normal n = (1, 2, 1) at K; hidden parts are dashed")


# ===========================================================================
# 9. dzu-dik-kesisen: d through P0(3, 1, 2) with v = n = (2, -1, 2) meets the plane at H(-1, 3, -2)
# ===========================================================================
P0, Vv = (3, 1, 2), (2, -1, 2)
H = vadd(P0, vscale(-2, Vv))
assert H == (-1, 3, -2) and 2 * H[0] - H[1] + 2 * H[2] + 9 == 0
e1, e2 = (1, 2, 0), (1, 0, -1)
assert vdot(e1, Vv) == 0 and vdot(e2, Vv) == 0
S1, S2 = (-1.4, 1.4), (-2.0, 2.0)
A, B = vadd(P0, vscale(0.45, Vv)), vadd(P0, vscale(-2.8, Vv))
ext = [vadd(H, vadd(vscale(a, e1), vscale(b, e2))) for a in S1 for b in S2] + \
      [A, B, (5.5, 0, 0), (0, 5.5, 0), (0, 0, 4.5), (-3, 0, 0), (0, 0, -4)]
f = Fig(35, 20, ext, width=540, pad=70)
assert f.front(Vv)
C = f.patch(H, e1, e2, S1, S2)
f.axes(((-3, 5.5), (-1, 5.5), (-4, 4.5)))
f.edges(C)
f.dline(A, B, TEXT, 2.4)
def side_offset(f, P, vec, e1, e2, px, side=1):
    """In-plane offset (span of e1, e2) whose page image is farthest from the page line of vec,
    on its left (side=1) or right (side=-1) looking along vec on the page."""
    a = math.radians(f.sang(vec))
    best = None
    for k in range(72):
        t = 2 * math.pi * k / 72
        o = vadd(vscale(math.cos(t), vunit(e1)), vscale(math.sin(t), vunit(e2)))
        X, Y, _ = f.cam.project(vadd(f.cam.center, o))
        perp = side * (-math.sin(a) * X + math.cos(a) * Y)
        if best is None or perp > best[0]:
            best = (perp, o)
    return vscale(f.u(px) / best[0], best[1])


off = side_offset(f, P0, Vv, e1, vcross(e1, Vv), 30, -1)
f.arrow(vadd(P0, vadd(off, vscale(-0.2, Vv))), vadd(P0, vadd(off, vscale(0.35, Vv))), BASE, 3.0, 13.0,
        halo=True)
f.right_angle(H, Vv, e2, 14)
f.point(P0, TEXT, 4.0)
f.point(H, TEXT, 4.0)
f.place(P0, P0_ + triple(3, 1, 2), NAME, prefs=[180, 200, 160, 225])
f.place(H, it("H") + triple(-1, 3, -2), NAME, prefs=[0, 340, 20, 315])
f.place(vadd(P0, vadd(off, vscale(0.35, Vv))), N_, NAME + 1, BASE, prefs=ahead(f, Vv, (0, -40, 40, -80)))
f.place(A, D_, NAME + 1, prefs=[f.sang(Vv) + 90, f.sang(Vv), f.sang(Vv) - 90])
f.plane_name(C[0], eq("2x - y + 2z + 9"), NAME, THEORY, prefs=[270, 240, 300, 180])
f.render(
    "dik-kesisen",
    "<em>d</em>&#8217;nin doğrultman vektörü düzlemin normali <em>n</em> = (2, &#8722;1, 2)&#8217;dir; "
    "doğru düzleme diktir ve onu <em>H</em>(&#8722;1, 3, &#8722;2)&#8217;de keser. <em>H</em>, "
    "<em>P</em><sub>0</sub>(3, 1, 2)&#8217;dan düzleme inen dikmenin ayağıdır.",
    "Axes, the plane 2x - y + 2z + 9 = 0 around H(-1, 3, -2), the line d from P0(3, 1, 2) to H "
    "perpendicular to the plane with a right-angle mark at H, and a short normal n = (2, -1, 2) beside "
    "P0 parallel to d")


# ===========================================================================
# 10. dzu-yalniz-paralel: d = (2 + l, 1 - l, 3l) runs beside 2x - y - z + 4 = 0
# ===========================================================================
P0, Vv, Nn = (2, 1, 0), (1, -1, 3), (2, -1, -1)
assert vdot(Vv, Nn) == 0 and 2 * P0[0] - P0[1] - P0[2] + 4 == 7
F = vadd(P0, vscale(-7 / 6, Nn))
assert close(F, (-1 / 3, 13 / 6, 7 / 6)) and abs(2 * F[0] - F[1] - F[2] + 4) < 1e-12
Cc = (-1, 1, 1)
e1, e2 = vunit(Vv), vunit(vcross(Nn, Vv))
assert abs(vdot(e2, Nn)) < 1e-12 and 2 * Cc[0] - Cc[1] - Cc[2] + 4 == 0
S1, S2 = (-4.0, 4.0), (-1.8, 1.8)
A, B = vadd(P0, vscale(-1.2, Vv)), vadd(P0, vscale(1.2, Vv))
ext = [vadd(Cc, vadd(vscale(a, e1), vscale(b, e2))) for a in S1 for b in S2] + \
      [A, B, (3.5, 0, 0), (0, 3.5, 0), (0, 0, 5), (-3.5, 0, 0), (0, -1.5, 0), (0, 0, -2)]
f = Fig(85, 17, ext, width=540, pad=70)
C = f.patch(Cc, e1, e2, S1, S2)
f.axes(((-3.5, 3.5), (-1.5, 3.5), (-2, 5)))
f.edges(C)
f.dline(A, B, TEXT, 2.4)
f.line([P0, F], TEXT, 1.8, "5 4", 0.95)
f.right_angle(F, vsub(P0, F), e1, 13)
f.point(P0, TEXT, 4.0)
f.point(F, TEXT, 3.2)
f.place(P0, P0_, NAME, prefs=[0, 330, 30])
f.place(B, D_, NAME + 1, prefs=[f.sang(Vv) + 90, f.sang(Vv), f.sang(Vv) - 90])
f.plane_name(C[0], eq("2x - y - z + 4"), NAME, THEORY, prefs=[270, 240, 300, 180])
f.render(
    "yalniz-paralel",
    "<em>d</em> doğrusu düzleme paraleldir (<em>&#10216;n</em>, <em>v&#10217;</em> = 0) ama "
    "<em>P</em><sub>0</sub>(2, 1, 0) düzlemde değildir; doğru düzlemin yanından geçer ve onu hiç kesmez. "
    "Kesikli çizgi <em>P</em><sub>0</sub>&#8217;dan düzleme inen dikmedir.",
    "Axes, the plane 2x - y - z + 4 = 0 and the line d through P0(2, 1, 0) with direction (1, -1, 3) "
    "running beside it without meeting it, and the dashed perpendicular from P0 to the plane with a "
    "right-angle mark at its foot")


# ===========================================================================
# 11. dzu-nokta-duzlem-ornek: P0(2, -1, 1) is at distance 2 from 2x - y - 2z + 3 = 0
# ===========================================================================
P0, Nn = (2, -1, 1), (2, -1, -2)
S = (2 / 3, -1 / 3, 7 / 3)
assert abs(2 * S[0] - S[1] - 2 * S[2] + 3) < 1e-12 and close(vsub(P0, S), vscale(2 / 3, Nn))
assert abs(vnorm(vsub(P0, S)) - 2) < 1e-12
e1, e2 = (1, 2, 0), (1, 0, 1)
assert vdot(e1, Nn) == 0 and vdot(e2, Nn) == 0
S1, S2 = (-1.3, 1.3), (-1.6, 1.6)
ext = [vadd(S, vadd(vscale(a, e1), vscale(b, e2))) for a in S1 for b in S2] + \
      [P0, (3.5, 0, 0), (0, 2.5, 0), (0, 0, 4.5), (-1, 0, 0), (0, -2, 0), (0, 0, -1)]
f = Fig(35, 12, ext, width=520, pad=70)
assert f.front(Nn)
C = f.patch(S, e1, e2, S1, S2)
f.axes(((-1, 3.5), (-2, 2.5), (-1, 4.5)))
f.edges(C)
f.line([P0, S], TEXT, 1.8, "5 4", 0.95)
f.right_angle(S, Nn, e1, 13)
f.point(P0, TEXT, 4.0)
f.point(S, TEXT, 4.0)
f.place(P0, P0_ + triple(2, -1, 1), NAME, prefs=[0, 330, 30, 270])
f.place(S, it("S"), NAME, prefs=[90, 120, 60, 180])
f.place(mid(P0, S), it(ELL) + " = 2", NAME, prefs=[f.sang(Nn) + 90, f.sang(Nn) - 90])
f.plane_name(corner(f, C, "top"), eq("2x - y - 2z + 3"), NAME, THEORY, prefs=[90, 60, 120])
f.render(
    "nokta-duzlem-ornek",
    "<em>P</em><sub>0</sub>(2, &#8722;1, 1)&#8217;dan düzleme inen dikmenin ayağı "
    "<em>S</em>(2/3, &#8722;1/3, 7/3)&#8217;tür ve |<em>P</em><sub>0</sub><em>S</em>| = 2&#8217;dir. "
    "<em>P</em><sub>0</sub>, normal <em>n</em> = (2, &#8722;1, &#8722;2)&#8217;nin gösterdiği "
    "taraftadır.",
    "Axes, the plane 2x - y - 2z + 3 = 0 around S(2/3, -1/3, 7/3), the point P0(2, -1, 1) and the dashed "
    "perpendicular P0S of length 2 with a right-angle mark at S")


ALPHA12, BETA12 = -15, 55
AZ13, EL13 = 200, 30
AZ14, EL14 = -130, 20
CORNER12, PREFS12 = ("left", "right"), ([180, 200, 160], [0, 20, 340])
CORNER13, PREFS13 = ("left", "right"), ([180, 200, 160], [0, 20, 340])
CORNER14, PREFS14 = "bottom", [0, 340, 20, 270]


# ===========================================================================
# 12. dzu-duzlem-acisi: 2x - y + z - 7 = 0 and x + y + 2z - 11 = 0 meet at the angle pi/3
# ===========================================================================
N1, N2 = (2, -1, 1), (1, 1, 2)
Q = (6, 5, 0)
L = vcross(N1, N2)
assert L == (-3, -3, 3) and 2 * 6 - 5 - 7 == 0 and 6 + 5 - 11 == 0
assert abs(vdot(N1, N2) / (vnorm(N1) * vnorm(N2)) - 0.5) < 1e-12
Lu = vunit((1, 1, -1))
W1, W2 = vunit(vcross(N1, Lu)), vunit(vcross(N2, Lu))
SA, SB = (-3.4, 3.4), (-2.7, 2.7)
NL = 2.3                                           # page length of the drawn normals, in units
ext = [vadd(Q, vadd(vscale(a, Lu), vscale(b, W))) for a in SA for b in SB for W in (W1, W2)]
# look from the bisector of the two normals, tipped by BETA12 toward the line, so both normals
# face the viewer and the angle between them opens up; the line is then levelled on the page
BIS = vunit(vadd(vunit(N1), vunit(N2)))
_a, _b = math.radians(ALPHA12), math.radians(BETA12)
_side = vadd(vscale(math.cos(_a), BIS), vscale(math.sin(_a), vcross(Lu, BIS)))
view = vadd(vscale(math.cos(_b), _side), vscale(math.sin(_b), Lu))
AZ12, EL12 = math.degrees(math.atan2(view[1], view[0])), math.degrees(math.asin(view[2]))
f = Fig(AZ12, EL12, ext, width=560, pad=70, level=Lu, up=BIS)
C1 = f.patch(Q, Lu, W1, SA, SB, THEORY, 0.13)
C2 = f.patch(Q, Lu, W2, SA, SB, BASE, 0.12)
f.edges(C1, THEORY)
f.edges(C2, BASE)
f.line([vadd(Q, vscale(SA[0], Lu)), vadd(Q, vscale(SA[1], Lu))], TEXT, 2.6)
T1, T2 = vadd(Q, vscale(NL, vunit(N1))), vadd(Q, vscale(NL, vunit(N2)))
f.arc(Q, N1, N2, 46, TEXT, 1.4)
f.arrow(Q, T1, THEORY, 3.0, 13.0, halo=True)
f.arrow(Q, T2, BASE, 3.0, 13.0, halo=True)
f.point(Q, TEXT, 4.0)
f.place(Q, it("Q"), NAME, prefs=[270, 250, 290, 225, 315])
f.place(T1, N_ + sub(1), NAME + 1, THEORY, prefs=ahead(f, N1, (0, 40, -40, 80, -80)))
f.place(T2, N_ + sub(2), NAME + 1, BASE, prefs=ahead(f, N2, (0, 40, -40, 80, -80)))
bis = vunit(vadd(vunit(N1), vunit(N2)))
f.place(vadd(Q, vscale(f.u(66) / f.px_len(bis), bis)), it(THETA) + " = " + it("π") + "/3", NAME,
        prefs=["c", 90, 45, 135], d=2, far=(0, 6, 12, 20))
f.plane_name(corner(f, C1, CORNER12[0]), sub(1, NAME + 3), NAME + 3, THEORY, prefs=PREFS12[0])
f.plane_name(corner(f, C2, CORNER12[1]), sub(2, NAME + 3), NAME + 3, BASE, prefs=PREFS12[1])
f.render(
    "duzlem-acisi",
    "İki düzlem arakesit doğrusu boyunca kesişir. Arakesit üzerindeki <em>Q</em>(6, 5, 0) noktasından "
    "çizilen <em>n</em><sub>1</sub> = (2, &#8722;1, 1) ve <em>n</em><sub>2</sub> = (1, 1, 2) normalleri "
    "arasındaki açı <em>&#952;</em> = <em>&#960;</em>/3&#8217;tür; düzlemler arasındaki açı da budur.",
    "Two planes 2x - y + z - 7 = 0 and x + y + 2z - 11 = 0 crossing along the line (6, 5, 0) + t(1, 1, -1), "
    "the point Q(6, 5, 0) on it, the normals n1 = (2, -1, 1) and n2 = (1, 1, 2) from Q and the angle "
    "theta = pi/3 between them")


# ===========================================================================
# 13. dzu-arakesit-dogrusu: 2x - 7y + 4z - 3 = 0 and 3x - 5y + 4z + 11 = 0 meet along d
# ===========================================================================
N1, N2 = (2, -7, 4), (3, -5, 4)
Q = (-14, 0, 31 / 4)
V4 = (-8, 4, 11)
assert abs(vdot(N1, Q) - 3) < 1e-12 and abs(vdot(N2, Q) + 11) < 1e-12
assert vdot(N1, V4) == 0 and vdot(N2, V4) == 0
Vv = vscale(0.25, V4)
W1, W2 = vunit(vcross(N1, V4)), vunit(vcross(N2, V4))
if vdot(W1, W2) < 0:
    W2 = vscale(-1, W2)
TA, SB = (-0.5, 1.5), (-11.0, 11.0)
ext = [vadd(Q, vadd(vscale(a, V4), vscale(b, W))) for a in TA for b in SB for W in (W1, W2)]
f = Fig(AZ13, EL13, ext, width=560, pad=70, level=V4)
C1 = f.patch(Q, V4, W1, TA, SB, THEORY, 0.13)
C2 = f.patch(Q, V4, W2, TA, SB, BASE, 0.12)
f.edges(C1, THEORY)
f.edges(C2, BASE)
A, B = vadd(Q, vscale(TA[0], V4)), vadd(Q, vscale(TA[1], V4))
f.line([A, B], TEXT, 2.6)
f.arrow(Q, vadd(Q, Vv), PRACTICE, 3.2, 13.0, halo=True)
f.point(Q, TEXT, 4.0)
f.place(Q, it("Q"), NAME, prefs=[f.sang(V4) - 90, f.sang(V4) + 90, f.sang(V4) + 180])
f.place(vadd(Q, vscale(0.6, Vv)), V_, NAME + 1, PRACTICE, prefs=[f.sang(V4) + 90, f.sang(V4) - 90])
f.place(B, D_, NAME + 1, prefs=ahead(f, V4, (0, 30, -30, 60, -60)))
f.plane_name(corner(f, C1, CORNER13[0]), sub(1, NAME + 3), NAME + 3, THEORY, prefs=PREFS13[0])
f.plane_name(corner(f, C2, CORNER13[1]), sub(2, NAME + 3), NAME + 3, BASE, prefs=PREFS13[1])
f.render(
    "arakesit-dogrusu",
    "İki düzlem <em>d</em> doğrusu boyunca kesişir; <em>d</em>, <em>Q</em>(&#8722;14, 0, 31/4) noktasından "
    "geçer ve doğrultman vektörü <em>v</em> = (&#8722;2, 1, 11/4)&#8217;tür. Düzlemler arasındaki açı "
    "küçük olduğundan yamalar birbirine yakın durur.",
    "Two planes 2x - 7y + 4z - 3 = 0 and 3x - 5y + 4z + 11 = 0 meeting along the line d through "
    "Q(-14, 0, 31/4) with direction v = (-2, 1, 11/4)")


# ===========================================================================
# 14. dzu-arakesit-duzlemi: the plane 15x - 47y + 28z - 7 = 0 through d and P0(-2, 1, 3)
# ===========================================================================
Nn = (15, -47, 28)
P0 = (-2, 1, 3)
E2 = vsub(P0, Q)
assert close(E2, (12, 1, -19 / 4)) and abs(vdot(Nn, P0) - 7) < 1e-12 and abs(vdot(Nn, Q) - 7) < 1e-12
assert vdot(Nn, V4) == 0
TA, SB = (-0.5, 1.5), (-0.45, 1.45)
ext = [vadd(Q, vadd(vscale(a, V4), vscale(b, E2))) for a in TA for b in SB]
f = Fig(AZ14, EL14, ext, width=560, pad=70, level=V4, up=Nn)
C = f.patch(Q, V4, E2, TA, SB, THEORY, 0.13)
f.edges(C, THEORY)
A, B = vadd(Q, vscale(TA[0], V4)), vadd(Q, vscale(TA[1], V4))
f.line([A, B], TEXT, 2.6)
f.line([Q, P0], TEXT, 1.4, "5 4", 0.85)
assert f.front(Nn)
NT = normal_arrow(f, Q, Nn, 70, prefs=ahead(f, Nn, (0, -40, 40, -80, 80)))
f.right_angle(Q, Nn, V4, 14)
f.point(Q, TEXT, 4.0)
f.point(P0, TEXT, 4.0)
f.place(Q, it("Q"), NAME, prefs=[f.sang(V4) - 90, f.sang(V4) + 90, f.sang(V4) + 180])
f.place(P0, P0_, NAME, prefs=[f.sang(E2), f.sang(E2) + 40, f.sang(E2) - 40])
f.place(B, D_, NAME + 1, prefs=ahead(f, V4, (0, 30, -30, 60, -60)))
f.plane_name(corner(f, C, CORNER14), eq("15x - 47y + 28z - 7"), NAME, THEORY, prefs=PREFS14)
f.render(
    "arakesit-duzlemi",
    "Aranan düzlem <em>d</em> arakesit doğrusunu ve onun dışındaki <em>P</em><sub>0</sub>(&#8722;2, 1, 3) "
    "noktasını içerir; <em>Q</em>&#8217;dan geçen <em>d</em> ile <em>QP</em><sub>0</sub> doğrultusu "
    "düzlemi gerer. <em>Q</em>&#8217;dan çizilen ok, normal <em>n</em> = (15, &#8722;47, 28) "
    "doğrultusundadır ve <em>d</em>&#8217;ye diktir.",
    "The plane 15x - 47y + 28z - 7 = 0 containing the line d through Q(-14, 0, 31/4) with direction "
    "(-8, 4, 11) and the point P0(-2, 1, 3), with the dashed segment Q P0 and the normal n at Q")


# ---------------------------------------------------------------------------
for name, content in OUT.items():
    path = OUT_DIR / f"analytic-dzu-{name}.md"
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(content)
    print("wrote", path.name)
