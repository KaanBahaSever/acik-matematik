# -*- coding: utf-8 -*-
"""
Figures of the chapter "Bölme Oranı, Eğim ve Açı"
(dersler/analitik-geometri/bolme-orani-egim-ve-aci.qmd), key `bea`.

The figures are NOT produced at build time. Run

    python scripts/analytic_figures/bea.py
    python scripts/center_figures.py "analytic-bea-*.md" --keep-width

and paste the markup from scripts/_figures/analytic-bea-<name>.md into the
.qmd file. Figures go INSIDE the box they explain (theorem, proof, example,
solution or exercise), never inside a definition box: a figure that
illustrates a definition sits directly below that box.

All panels use the same pixels per unit on both axes, so angles and right
angles look true. Labels are placed by a small collision search: every drawn
segment, arc, point and label is registered, and each new label takes the
first preferred position that touches none of them.

Captions are Turkish (they are shown on the site); aria labels are ASCII.
"""
import io
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, WIDE, TEXT, BG, THEORY, PRACTICE, BASE, REMARK  # noqa: E402
from check_figure_labels import text_width  # noqa: E402

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
OUT = {}

PI = math.pi
GRAY = TEXT

# ---------------------------------------------------------------------------
# tiny TeX-like label markup -> SVG text body
# ---------------------------------------------------------------------------
GREEK = {"theta": "&#952;", "alpha": "&#945;", "beta": "&#946;", "pi": "&#960;",
         "varphi": "&#966;", "cdot": "&#183;"}
ITALIC_GREEK = {"theta", "alpha", "beta", "varphi"}


def sub_size(size):
    return round(max(11.0, size * 0.78), 1)


def tex(s, size):
    """Render a label such as 'P_1(x_1, y_1)' or '\\theta = \\pi/4'.

    Letters are italic, digits upright, '_x' / '_{xy}' become subscripts,
    '-' becomes a true minus sign. Returns (svg_body, has_subscript)."""
    parts = []   # (kind, text) with kind in it / rm / sub
    i, n = 0, len(s)
    while i < n:
        c = s[i]
        if s.startswith("\\sqrt{", i):
            j = s.index("}", i)
            parts.append(("rm", "&#8730;" + s[i + 6:j]))
            i = j + 1
        elif c == "\\":
            m = re.match(r"\\([A-Za-z]+)", s[i:])
            name = m.group(1)
            parts.append(("it" if name in ITALIC_GREEK else "rm", GREEK[name]))
            i += len(m.group(0))
        elif c == "_":
            if s[i + 1] == "{":
                j = s.index("}", i)
                inner = s[i + 2:j]
                i = j + 1
            else:
                inner = s[i + 1]
                i += 2
            parts.append(("sub", inner))
        elif c.isalpha():
            j = i
            while j < n and s[j].isalpha():
                j += 1
            parts.append(("it", s[i:j]))
            i = j
        else:
            ch = {"-": "&#8722;", "<": "&lt;", ">": "&gt;", "&": "&amp;", "'": "&#8242;"}.get(c, c)
            parts.append(("rm", ch))
            i += 1
    out, has_sub = [], False
    ss = sub_size(size)
    for kind, t in parts:
        if kind == "rm":
            if out and out[-1][0] == "rm":
                out[-1] = ("rm", out[-1][1] + t)
            else:
                out.append(("rm", t))
        else:
            out.append((kind, t))
    body = []
    for kind, t in out:
        if kind == "rm":
            body.append(t)
        elif kind == "it":
            body.append(f'<tspan font-style="italic">{t}</tspan>')
        else:
            has_sub = True
            it = ' font-style="italic"' if t.isalpha() else ""
            body.append(f'<tspan font-size="{ss}" dy="4"{it}>{t}</tspan><tspan dy="-4">&#8203;</tspan>')
    return "".join(body), has_sub


# ---------------------------------------------------------------------------
# geometry helpers (pixel space)
# ---------------------------------------------------------------------------
def seg_hits_box(s, b):
    """Liang-Barsky: does segment s=(x1,y1,x2,y2) meet box b=(x0,y0,x1,y1)?"""
    x1, y1, x2, y2 = s[:4]
    bx0, by0, bx1, by1 = b
    dx, dy = x2 - x1, y2 - y1
    t0, t1 = 0.0, 1.0
    for p, q in ((-dx, x1 - bx0), (dx, bx1 - x1), (-dy, y1 - by0), (dy, by1 - y1)):
        if abs(p) < 1e-12:
            if q < 0:
                return False
        else:
            t = q / p
            if p < 0:
                if t > t1:
                    return False
                t0 = max(t0, t)
            else:
                if t < t0:
                    return False
                t1 = min(t1, t)
    return t0 <= t1


def boxes_meet(a, b):
    return min(a[2], b[2]) > max(a[0], b[0]) and min(a[3], b[3]) > max(a[1], b[1])


def circle_hits_box(c, b):
    cx, cy, r = c
    nx = min(max(cx, b[0]), b[2])
    ny = min(max(cy, b[1]), b[3])
    return math.hypot(cx - nx, cy - ny) < r


def unit(dx, dy):
    L = math.hypot(dx, dy) or 1.0
    return dx / L, dy / L


DIRS = {"r": (1, 0), "l": (-1, 0), "u": (0, -1), "d": (0, 1),
        "ur": (1, -1), "ul": (-1, -1), "dr": (1, 1), "dl": (-1, 1)}
ORDER = ("ur", "ul", "dr", "dl", "r", "l", "u", "d")


class Board:
    """One SVG canvas: panels plus the registry of everything drawn on it."""

    def __init__(self, W):
        self.W, self.H = W, 400
        self.segs, self.boxes, self.dots = [], [], []
        self.panes = []

    def pane(self, x0, y0, width, xr, yr):
        p = Pane(self, x0, y0, width, xr, yr)
        self.panes.append(p)
        return p

    def fit(self, bottom=44):
        self.H = int(max(p.p.y0 + p.p.h for p in self.panes) + bottom)

    def hits(self, box, pad=3.0, ignore=None):
        """Number of registered things a (padded) box touches; canvas exit counts too."""
        b = (box[0] - pad, box[1] - pad, box[2] + pad, box[3] + pad)
        k = 0
        if box[0] < 2 or box[1] < 2 or box[2] > self.W - 2 or box[3] > self.H - 2:
            k += 5
        for s in self.segs:
            if ignore is not None and s[4] in ignore:
                continue
            if seg_hits_box(s, b):
                k += 1
        for bb in self.boxes:
            if boxes_meet(b, bb):
                k += 2
        for c in self.dots:
            if circle_hits_box(c, b):
                k += 3
        return k

    def seg_free(self, s, ignore_box=None):
        for bb in self.boxes:
            if bb is not ignore_box and seg_hits_box(s, (bb[0] - 1, bb[1] - 1, bb[2] + 1, bb[3] + 1)):
                return False
        return True

    def finish(self):
        for p in self.panes:
            p.place_ticks()

    def figure(self, caption, aria, css="ders-grafik"):
        self.finish()
        return figure(self.W, self.H, [p.p for p in self.panes], caption, css, aria)


class Pane:
    """An equal-aspect Cartesian panel whose drawing calls also register obstacles."""

    def __init__(self, board, x0, y0, width, xr, yr):
        self.b = board
        self.ppu = width / (xr[1] - xr[0])
        self.p = Plot(x0, y0, width, (yr[1] - yr[0]) * self.ppu, xr, yr)
        self.xr, self.yr = xr, yr
        self.pending_ticks = []

    # -- mapping ------------------------------------------------------------
    def px(self, P):
        return (self.p.X(P[0]), self.p.Y(P[1]))

    def add(self, s):
        self.p.add(s)

    # -- low level pixel drawing -------------------------------------------
    def poly_px(self, pts, color=THEORY, width=2.0, dash=None, opacity=1.0, tag="line", register=True):
        d = " ".join(("M" if i == 0 else "L") + f"{x:.1f},{y:.1f}" for i, (x, y) in enumerate(pts))
        da = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}"{da} '
                 f'opacity="{opacity}" stroke-linejoin="round" stroke-linecap="round"/>')
        if register:
            for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
                self.b.segs.append((xa, ya, xb, yb, tag))

    def head_px(self, tip, ux, uy, color, size=8.0, opacity=1.0):
        """Filled arrowhead with its tip at `tip`, pointing along (ux, uy)."""
        x1, y1 = tip
        px_, py_ = -uy, ux
        hw = size * 0.42
        self.add(f'<polygon points="{x1:.1f},{y1:.1f} {x1 - ux * size + px_ * hw:.1f},{y1 - uy * size + py_ * hw:.1f} '
                 f'{x1 - ux * size - px_ * hw:.1f},{y1 - uy * size - py_ * hw:.1f}" fill="{color}" opacity="{opacity}"/>')
        self.b.segs.append((x1, y1, x1 - ux * size, y1 - uy * size, "head"))

    # -- data-space drawing -------------------------------------------------
    def seg(self, A, B, color=THEORY, width=2.2, dash=None, opacity=1.0, tag="line"):
        self.poly_px([self.px(A), self.px(B)], color, width, dash, opacity, tag)

    def dashed(self, A, B, color=GRAY, width=1.3, opacity=0.6, dash="5 4"):
        self.seg(A, B, color, width, dash, opacity, "guide")

    def arrow(self, A, B, color=THEORY, width=2.0, head=9.0, opacity=1.0):
        (xa, ya), (xb, yb) = self.px(A), self.px(B)
        ux, uy = unit(xb - xa, yb - ya)
        self.poly_px([(xa, ya), (xb - ux * head * 0.8, yb - uy * head * 0.8)], color, width, None, opacity)
        self.head_px((xb, yb), ux, uy, color, head, opacity)

    def clip(self, A, B, margin=0.0):
        """The part of the infinite line AB inside the data window (shrunk by margin)."""
        x0, x1 = self.xr[0] + margin, self.xr[1] - margin
        y0, y1 = self.yr[0] + margin, self.yr[1] - margin
        dx, dy = B[0] - A[0], B[1] - A[1]
        lo, hi = -1e9, 1e9
        for p, q0, q1 in ((dx, x0 - A[0], x1 - A[0]), (dy, y0 - A[1], y1 - A[1])):
            if abs(p) < 1e-12:
                continue
            ta, tb = sorted((q0 / p, q1 / p))
            lo, hi = max(lo, ta), min(hi, tb)
        return (A[0] + lo * dx, A[1] + lo * dy), (A[0] + hi * dx, A[1] + hi * dy)

    def dot(self, P, color=TEXT, r=4.2):
        X, Y = self.px(P)
        self.add(f'<circle cx="{X:.1f}" cy="{Y:.1f}" r="{r}" fill="{color}"/>')
        self.b.dots.append((X, Y, r + 1.5))

    def hollow(self, P, color=TEXT, r=4.2):
        X, Y = self.px(P)
        self.add(f'<circle cx="{X:.1f}" cy="{Y:.1f}" r="{r}" fill="{BG}" stroke="{color}" stroke-width="1.7"/>')
        self.b.dots.append((X, Y, r + 1.5))

    def right_angle(self, V, d1, d2, s=12.0, color=GRAY, opacity=0.8):
        X, Y = self.px(V)
        u1 = unit(d1[0], -d1[1])
        u2 = unit(d2[0], -d2[1])
        pts = [(X + s * u1[0], Y + s * u1[1]), (X + s * (u1[0] + u2[0]), Y + s * (u1[1] + u2[1])),
               (X + s * u2[0], Y + s * u2[1])]
        self.poly_px(pts, color, 1.3, None, opacity, "mark")

    def arc(self, V, a0, a1, r, color=BASE, width=1.7, arrow=False, opacity=1.0):
        """Arc of r pixels about V from angle a0 to a1 (radians, counter-clockwise)."""
        X, Y = self.px(V)
        n = max(12, int(abs(a1 - a0) * r / 3))
        pts = [(X + r * math.cos(a0 + (a1 - a0) * k / n), Y - r * math.sin(a0 + (a1 - a0) * k / n))
               for k in range(n + 1)]
        if arrow:
            head = 8.0
            # stop the curve where the head begins
            cut = head / r
            b1 = a1 - cut * (1 if a1 > a0 else -1)
            m = max(8, int(abs(b1 - a0) * r / 3))
            body = [(X + r * math.cos(a0 + (b1 - a0) * k / m), Y - r * math.sin(a0 + (b1 - a0) * k / m))
                    for k in range(m + 1)]
            self.poly_px(body, color, width, None, opacity, "arc")
            tip = pts[-1]
            # chord direction of the last piece of the arc
            ux, uy = unit(tip[0] - body[-1][0], tip[1] - body[-1][1])
            self.head_px(tip, ux, uy, color, head, opacity)
        else:
            self.poly_px(pts, color, width, None, opacity, "arc")

    def eqticks(self, A, B, n=1, color=THEORY, L=11.0, gap=4.5, t=0.5):
        """Equal-length marks: n short strokes across AB at fraction t (the middle by default)."""
        (xa, ya), (xb, yb) = self.px(A), self.px(B)
        ux, uy = unit(xb - xa, yb - ya)
        nx, ny = -uy, ux
        mx, my = xa + (xb - xa) * t, ya + (yb - ya) * t
        for k in range(n):
            o = (k - (n - 1) / 2) * gap
            cx, cy = mx + ux * o, my + uy * o
            self.poly_px([(cx - nx * L / 2, cy - ny * L / 2), (cx + nx * L / 2, cy + ny * L / 2)],
                         color, 1.6, None, 1.0, "mark")

    def chevrons(self, A, B, n=1, color=THEORY, s=6.0, gap=5.0):
        """Parallel marks: n arrow-like chevrons at the middle of AB pointing from A to B."""
        (xa, ya), (xb, yb) = self.px(A), self.px(B)
        ux, uy = unit(xb - xa, yb - ya)
        nx, ny = -uy, ux
        mx, my = (xa + xb) / 2, (ya + yb) / 2
        for k in range(n):
            o = (k - (n - 1) / 2) * gap + s / 2
            tx, ty = mx + ux * o, my + uy * o
            self.poly_px([(tx - ux * s + nx * s * 0.75, ty - uy * s + ny * s * 0.75), (tx, ty),
                          (tx - ux * s - nx * s * 0.75, ty - uy * s - ny * s * 0.75)],
                         color, 1.7, None, 1.0, "mark")

    # -- text ---------------------------------------------------------------
    def _measure(self, s, size):
        body, has_sub = tex(s, size)
        w = max(text_width(body, size), glyph_width(body, size))
        asc = 0.78 * size
        dsc = 6.6 if has_sub else 0.24 * size
        return body, w, asc, dsc

    def _emit(self, box, asc, body, size, color, bold=False, register=True):
        weight = ' font-weight="600"' if bold else ""
        self.add(f'<text x="{box[0]:.1f}" y="{box[1] + asc:.1f}" fill="{color}" font-size="{size}"{weight}>'
                 f'{body}</text>')
        if register:
            self.b.boxes.append(box)
        return box

    def text_px(self, x, y, s, size=13, color=TEXT, anchor="middle", bold=False):
        """Fixed text at pixel (x, baseline y); registered as an obstacle."""
        body, w, asc, dsc = self._measure(s, size)
        x0 = x - w / 2 if anchor == "middle" else x - w if anchor == "end" else x
        return self._emit((x0, y - asc, x0 + w, y + dsc), asc, body, size, color, bold)

    def _box_at(self, X, Y, d, w, asc, dsc, g):
        ux, uy = DIRS[d]
        h = asc + dsc
        if d in ("ur", "ul", "dr", "dl"):
            g *= 0.72
        if ux > 0:
            x0 = X + g
        elif ux < 0:
            x0 = X - g - w
        else:
            x0 = X - w / 2
        if uy < 0:
            y0 = Y - g - h
        elif uy > 0:
            y0 = Y + g
        else:
            y0 = Y - h / 2 - (asc - dsc) * 0.0
        return (x0, y0, x0 + w, y0 + h)

    def label(self, P, s, prefer=("ur",), size=14, color=TEXT, gap=10.0, bold=False, px=None):
        """Label for a point: the first preferred position that touches nothing."""
        X, Y = px if px else self.px(P)
        body, w, asc, dsc = self._measure(s, size)
        prefer = tuple(prefer)
        rest = [d for d in ORDER if d not in prefer]
        seq = ([(d, gap) for d in prefer] + [(d, gap + 5) for d in prefer] + [(d, gap) for d in rest]
               + [(d, g) for g in (gap + 5, gap + 10, gap + 16) for d in prefer + tuple(rest)])
        best = None
        for d, g in seq:
            box = self._box_at(X, Y, d, w, asc, dsc, g)
            k = self.b.hits(box)
            if k == 0:
                best = (box, g)
                break
            if best is None or k < best[2]:
                best = (box, g, k)
        box = best[0]
        if len(best) == 3:
            print(f"  ! label '{s}' placed with {best[2]} contacts")
        return self._emit(box, asc, body, size, color, bold)

    def _centered_box(self, cx, cy, w, asc, dsc):
        h = asc + dsc
        return (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)

    def edge_label(self, A, B, s, side=None, size=13, color=TEXT, gap=6.0,
                   ts=(0.5, 0.42, 0.58, 0.34, 0.66, 0.26, 0.74)):
        """Label beside segment AB, pushed off it perpendicularly toward `side`."""
        (xa, ya), (xb, yb) = self.px(A), self.px(B)
        ux, uy = unit(xb - xa, yb - ya)
        n1 = (-uy, ux)
        n2 = (uy, -ux)
        normals = [n1, n2]
        if side:
            sx, sy = unit(*DIRS[side])
            normals.sort(key=lambda n: -(n[0] * sx + n[1] * sy))
        body, w, asc, dsc = self._measure(s, size)
        h = asc + dsc
        best = None
        for nx, ny in normals:
            ext = abs(nx) * w / 2 + abs(ny) * h / 2
            for g in (gap, gap + 5, gap + 11):
                for t in ts:
                    cx = xa + (xb - xa) * t + nx * (g + ext)
                    cy = ya + (yb - ya) * t + ny * (g + ext)
                    box = self._centered_box(cx, cy, w, asc, dsc)
                    k = self.b.hits(box)
                    if k == 0:
                        return self._emit(box, asc, body, size, color)
                    if best is None or k < best[1]:
                        best = (box, k)
        print(f"  ! edge label '{s}' placed with {best[1]} contacts")
        return self._emit(best[0], asc, body, size, color)

    def angle_label(self, V, a0, a1, r, s, size=14, color=TEXT, inside=False, gap=5.0,
                    spread=(0, 0.2, -0.2, 0.4, -0.4), pad=3.0, far=26):
        """Label for an angle arc of radius r (pixels) at V; leader line as a last resort."""
        X, Y = self.px(V)
        body, w, asc, dsc = self._measure(s, size)
        h = asc + dsc
        half = (a1 - a0) / 2
        mid = (a0 + a1) / 2
        best = None
        for dr in [d for d in (0, 5, 11, 18, 26, 36, 48, 62, 78) if d <= far]:
            for f in spread:
                a = mid + f * half
                ux, uy = math.cos(a), -math.sin(a)
                ext = abs(ux) * w / 2 + abs(uy) * h / 2
                rr = (r - gap - ext - dr) if inside else (r + gap + ext + dr)
                if rr <= ext:
                    continue
                box = self._centered_box(X + ux * rr, Y + uy * rr, w, asc, dsc)
                k = self.b.hits(box, pad)
                if k == 0:
                    return self._emit(box, asc, body, size, color)
                if best is None or k < best[1]:
                    best = (box, k)
        # leader line from the middle of the arc
        ax, ay = X + r * math.cos(mid), Y - r * math.sin(mid)
        for dist in (22, 32, 44, 58, 74):
            for f in (0, 0.5, -0.5, 1.0, -1.0, 1.5, -1.5, 2.0, -2.0, 2.6, -2.6):
                a = mid + f * 0.5
                ux, uy = math.cos(a), -math.sin(a)
                ext = abs(ux) * w / 2 + abs(uy) * h / 2
                cx, cy = ax + ux * (dist + ext), ay + uy * (dist + ext)
                box = self._centered_box(cx, cy, w, asc, dsc)
                if self.b.hits(box) != 0:
                    continue
                ex, ey = ax + ux * (dist - 3), ay + uy * (dist - 3)
                lead = (ax + ux * 2, ay + uy * 2, ex, ey, "leader")
                if any(seg_hits_box(lead, (bb[0] - 1, bb[1] - 1, bb[2] + 1, bb[3] + 1)) for bb in self.b.boxes):
                    continue
                crossings = sum(1 for sg in self.b.segs if sg[4] not in ("arc",) and _segs_cross(lead, sg))
                if crossings:
                    continue
                self.poly_px([(lead[0], lead[1]), (lead[2], lead[3])], color, 0.9, None, 0.7, "leader")
                return self._emit(box, asc, body, size, color)
        if best is None:
            raise SystemExit(f"angle label '{s}': no room")
        print(f"  ! angle label '{s}' placed with {best[1]} contacts")
        return self._emit(best[0], asc, body, size, color)

    def note(self, lines, corners=("ur", "ul", "dr", "dl"), size=13, inset=10, color=TEXT):
        """A small framed note (e.g. 'r = 2') in a free corner of the panel."""
        meas = [self._measure(s, size) for s in lines]
        w = max(m[1] for m in meas) + 16
        lh = size * 1.45
        h = lh * len(lines) + 8
        P = self.p
        for c in corners:
            x0 = P.x0 + inset if "l" in c else P.x0 + P.w - inset - w
            y0 = P.y0 + inset if "u" in c else P.y0 + P.h - inset - h
            box = (x0, y0, x0 + w, y0 + h)
            if self.b.hits(box, pad=2) == 0:
                break
        else:
            print(f"  ! note {lines} placed over something")
        self.add(f'<rect x="{box[0]:.1f}" y="{box[1]:.1f}" width="{w:.1f}" height="{h:.1f}" rx="5" '
                 f'fill="{THEORY}" fill-opacity="0.07" stroke="{TEXT}" stroke-opacity="0.35" stroke-width="1"/>')
        self.b.boxes.append(box)
        for k, (body, bw, asc, dsc) in enumerate(meas):
            y = box[1] + 4 + lh * k + (lh + asc - dsc) / 2
            self.add(f'<text x="{box[0] + 8:.1f}" y="{y:.1f}" fill="{color}" font-size="{size}">{body}</text>')
        return box

    # -- axes ---------------------------------------------------------------
    def axes(self, xticks=(), yticks=(), xlabels=None, ylabels=None, origin=True, names=("X", "Y")):
        """Axes through the origin with arrowheads, tick marks, names and 'O'.

        Tick numbers are placed at the very end (Board.finish) and skipped
        where they would touch a drawn object."""
        P = self.p
        ox, oy = P.X(0), P.Y(0)
        left, right = P.x0, P.x0 + P.w
        top, bottom = P.y0, P.y0 + P.h
        op = 0.6
        self.poly_px([(left, oy), (right - 7, oy)], TEXT, 1.2, None, op, "axis")
        self.head_px((right, oy), 1, 0, TEXT, 9, op)
        self.poly_px([(ox, bottom), (ox, top + 7)], TEXT, 1.2, None, op, "axis")
        self.head_px((ox, top), 0, -1, TEXT, 9, op)
        for t in xticks:
            X = P.X(t)
            self.poly_px([(X, oy - 3.5), (X, oy + 3.5)], TEXT, 1.1, None, op, "tick")
        for t in yticks:
            Y = P.Y(t)
            self.poly_px([(ox - 3.5, Y), (ox + 3.5, Y)], TEXT, 1.1, None, op, "tick")
        if names[0]:
            self.text_px(right + 7, oy + 5, names[0], 14, TEXT, "start")
        if names[1]:
            self.text_px(ox, top - 8, names[1], 14, TEXT, "middle")
        self.origin = origin
        xl = xticks if xlabels is None else xlabels
        yl = yticks if ylabels is None else ylabels
        self.pending_ticks = [("x", t) for t in xl if t != 0] + [("y", t) for t in yl if t != 0]

    def place_ticks(self):
        P = self.p
        if getattr(self, "origin", False):
            self.label((0, 0), "O", ("dl", "ul", "dr"), 13, TEXT, gap=6)
        ox, oy = P.X(0), P.Y(0)
        for axis, t in self.pending_ticks:
            s = ("-" if t < 0 else "") + fmt_num(abs(t))
            body, w, asc, dsc = self._measure(s, 11)
            if axis == "x":
                X = P.X(t)
                box = (X - w / 2, oy + 16 - asc, X + w / 2, oy + 16 + dsc)
            else:
                Y = P.Y(t)
                box = (ox - 7 - w, Y + 4 - asc, ox - 7, Y + 4 + dsc)
            if self.b.hits(box, pad=1.5) == 0:
                self.add(f'<text x="{box[0]:.1f}" y="{box[1] + asc:.1f}" fill="{TEXT}" font-size="11" '
                         f'opacity="0.75">{body}</text>')
                self.b.boxes.append(box)


def _segs_cross(a, b):
    def orient(p, q, r):
        return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])
    p1, p2, p3, p4 = (a[0], a[1]), (a[2], a[3]), (b[0], b[1]), (b[2], b[3])
    d1, d2 = orient(p3, p4, p1), orient(p3, p4, p2)
    d3, d4 = orient(p1, p2, p3), orient(p1, p2, p4)
    return d1 * d2 < 0 and d3 * d4 < 0


_TSPAN = re.compile(r"<tspan\b([^>]*)>(.*?)</tspan>", re.S)
_ENT = re.compile(r"&#?\w+;")


def _chars_w(t):
    """Rough advance width (em) of plain text in a Georgia-like serif."""
    w = 0.0
    for m in re.finditer(r"&#?\w+;|.", t, re.S):
        c = m.group(0)
        if c == "&#8203;":
            continue
        if c.startswith("&"):
            w += 0.62
        elif c.isupper():
            w += 0.74
        elif c.islower():
            w += 0.52
        elif c.isdigit():
            w += 0.56
        elif c in " ,.()'":
            w += 0.32
        else:
            w += 0.62
    return w


def glyph_width(body, size):
    """Width of a text body with tspans at their own font size (a safer estimate than the checker's)."""
    w = 0.0
    for m in _TSPAN.finditer(body):
        fs = re.search(r'font-size="([\d.]+)"', m.group(1))
        w += _chars_w(m.group(2)) * (float(fs.group(1)) if fs else size)
    w += _chars_w(_TSPAN.sub("", body)) * size
    return w


def fmt_num(v):
    return str(int(v)) if float(v).is_integer() else f"{v}".replace(".", ",")


def ints(a, b, step=1):
    """Integer tick positions a..b (inclusive) in steps."""
    return [k for k in range(int(a), int(b) + 1) if k % step == 0]


def ang(A, B):
    return math.atan2(B[1] - A[1], B[0] - A[0])


def lerp(A, B, t):
    return (A[0] + (B[0] - A[0]) * t, A[1] + (B[1] - A[1]) * t)


def em(s):
    """Caption helper: italic math letter."""
    return f"<em>{s}</em>"


P1c, P2c, P3c = "<em>P</em><sub>1</sub>", "<em>P</em><sub>2</sub>", "<em>P</em><sub>3</sub>"
M1c, M2c, M3c = "<em>M</em><sub>1</sub>", "<em>M</em><sub>2</sub>", "<em>M</em><sub>3</sub>"
D1c, D2c = "<em>d</em><sub>1</sub>", "<em>d</em><sub>2</sub>"
TH, AL, BE, PIs, MIN = "<em>&#952;</em>", "<em>&#945;</em>", "<em>&#946;</em>", "&#960;", "&#8722;"
SQ3 = "&#8730;3"


def normal_board(xr, yr, width=480, W=560, x0=40, y0=36):
    b = Board(W)
    p = b.pane(x0, y0, width, xr, yr)
    b.fit()
    return b, p


def wide_board(xr, yr, width=620):
    return normal_board(xr, yr, width, 700, 40, 36)


# ============================================================ oran-bolgeleri
b = Board(700)
p = b.pane(40, 40, 620, (-4.7, 8.9), (-1.9, 0.75))
b.fit(16)
p.seg((-4.2, 0), (0, 0), PRACTICE, 2.6, "8 5")
p.seg((4, 0), (8.0, 0), BASE, 2.6, "8 5")
p.arrow((8.05, 0), (8.75, 0), TEXT, 1.6, 10, 0.8)
p.seg((0, 0), (4, 0), THEORY, 4.2)
X2 = p.px((2, 0))
p.poly_px([(X2[0], X2[1] - 7), (X2[0], X2[1] + 7)], TEXT, 1.6, None, 0.9, "mark")
p.dot((0, 0), TEXT, 5)
p.dot((4, 0), TEXT, 5)
p.label((0, 0), "P_1", ("u",), 15, gap=10)
p.label((4, 0), "P_2", ("u",), 15, gap=10)
p.label((0, 0), "r = 0", ("d",), 12.5, gap=11)
p.label((2, 0), "r = 1", ("d",), 12.5, gap=11)
for x, s, col in ((-2.1, "-1 < r < 0", PRACTICE), (2, "r > 0", THEORY), (6, "r < -1", BASE)):
    X, Y = p.px((x, 0))
    p.text_px(X, Y + 52, s, 14.5, col, "middle", True)
OUT["oran-bolgeleri"] = b.figure(
    f"Bölme oranının işareti, bölünme noktasının {P1c}{P2c} doğrusu üzerindeki yerine göre değişir: "
    f"parçanın içinde <em>r</em> &gt; 0, {P1c} tarafındaki uzantıda {MIN}1 &lt; <em>r</em> &lt; 0, "
    f"{P2c} tarafındaki uzantıda <em>r</em> &lt; {MIN}1. {P1c} noktasında <em>r</em> = 0, orta noktada "
    f"<em>r</em> = 1'dir; <em>r</em> = {MIN}1 değeri hiçbir noktaya karşılık gelmez.",
    "Number line with P1 and P2: ratio positive between them, between -1 and 0 beyond P1, below -1 beyond P2",
    WIDE)

# ============================================================ bolme-benzer-ucgenler
b, p = normal_board((-0.5, 8), (-0.5, 6))
p.axes()
P1, P, P2, M, N = (1, 1), (4, 3), (7, 5), (4, 1), (7, 3)
for A, B_ in ((P1, M), (M, P), (P, N), (N, P2)):
    p.dashed(A, B_, TEXT, 1.4, 0.65)
p.right_angle(M, (-1, 0), (0, 1))
p.right_angle(N, (-1, 0), (0, 1))
p.seg(P1, P2, THEORY, 2.4)
for Q in (P1, P, P2):
    p.dot(Q)
p.label(P1, "P_1(x_1, y_1)", ("l", "ul"))
p.label(P, "P(x, y)", ("ul",))
p.label(P2, "P_2(x_2, y_2)", ("ur", "u"))
p.label(M, "M", ("dr",), 14, gap=6)
p.label(N, "N", ("r",), 14, gap=7)
p.edge_label(P1, M, "x - x_1", "d")
p.edge_label(M, P, "y - y_1", "r")
p.edge_label(P, N, "x_2 - x", "d")
p.edge_label(N, P2, "y_2 - y", "r")
OUT["bolme-benzer-ucgenler"] = b.figure(
    f"{P1c}<em>MP</em> ve <em>PNP</em><sub>2</sub> dik üçgenleri benzerdir; yatay kenarlarının oranı da "
    f"düşey kenarlarının oranı da |{P1c}<em>P</em>| / |<em>PP</em><sub>2</sub>| = <em>r</em> oranına eşittir.",
    "Segment P1 P2 through P with the two similar right triangles P1 M P and P N P2 and their leg lengths")

# ============================================================ orta-nokta
b, p = normal_board((-4, 8), (-2, 6))
p.axes(ints(-4, 7), ints(-2, 5))
P1, P2, M = (-3, 5), (7, -1), (2, 2)
p.seg(P1, P2, THEORY, 2.4)
p.eqticks(P1, M, 2)
p.eqticks(M, P2, 2)
p.dot(P1)
p.dot(P2)
p.dot(M, PRACTICE, 4.6)
p.label(P1, "P_1(-3, 5)", ("ul", "u"))
p.label(P2, "P_2(7, -1)", ("dr", "d"))
p.label(M, "M(2, 2)", ("ur",), color=PRACTICE)
OUT["orta-nokta"] = b.figure(
    f"{P1c}(&#8722;3, 5) ve {P2c}(7, &#8722;1) uç noktalı parçanın orta noktası <em>M</em>(2, 2); "
    f"çift çentikler |{P1c}<em>M</em>| = |<em>MP</em><sub>2</sub>| eşitliğini gösterir.",
    "Segment from P1(-3,5) to P2(7,-1) with its midpoint M(2,2) and equal-length marks")

# ============================================================ agirlik-merkezi-genel
b, p = normal_board((-0.5, 7), (-0.5, 6))
p.axes()
P1, P2, P3 = (1, 1), (6, 2), (3, 5)
M1, M2, M3 = (4.5, 3.5), (2, 3), (3.5, 1.5)
G = (10 / 3, 8 / 3)
for V, Mm in ((P1, M1), (P2, M2), (P3, M3)):
    p.dashed(V, Mm, TEXT, 1.4, 0.6)
p.poly_px([p.px(P1), p.px(P2), p.px(P3), p.px(P1)], THEORY, 2.2)
for V in (P1, P2, P3):
    p.dot(V)
for Mm in (M1, M2, M3):
    p.hollow(Mm, TEXT)
p.dot(G, PRACTICE, 4.6)
p.label(P1, "P_1", ("dl",), 15)
p.label(P2, "P_2", ("r",), 15)
p.label(P3, "P_3", ("u",), 15)
p.label(M1, "M_1", ("ur",))
p.label(M2, "M_2", ("l",))
p.label(M3, "M_3", ("d",))
p.label(G, "G", ("dr",), 15, PRACTICE)
p.edge_label(P1, G, "2", "dr", 13.5, PRACTICE)
p.edge_label(G, M1, "1", "dr", 13.5, PRACTICE)
OUT["agirlik-merkezi-genel"] = b.figure(
    f"Üç kenarortay {P1c}{M1c}, {P2c}{M2c}, {P3c}{M3c} aynı <em>G</em> noktasından geçer; "
    f"<em>G</em> her kenarortayı köşeden itibaren 2 : 1 oranında böler.",
    "Triangle P1 P2 P3 with midpoints M1 M2 M3, its three medians and their common point G dividing them 2 to 1")

# ============================================================ agirlik-merkezi-ornek
b, p = normal_board((-1, 8), (-1, 9))
p.axes(ints(-1, 7), ints(-1, 8))
A, B_, C = (2, 1), (6, 3), (1, 8)
M = (3.5, 5.5)
G = (3, 4)
p.dashed(B_, (1.5, 4.5), TEXT, 1.1, 0.5, "4 4")
p.dashed(C, (4, 2), TEXT, 1.1, 0.5, "4 4")
p.seg(A, M, PRACTICE, 2.0, "7 5", 1.0, "guide")
p.poly_px([p.px(A), p.px(B_), p.px(C), p.px(A)], THEORY, 2.2)
for V in (A, B_, C):
    p.dot(V)
p.hollow(M, PRACTICE)
p.dot(G, PRACTICE, 4.6)
p.label(A, "A(2, 1)", ("dl", "d"))
p.label(B_, "B(6, 3)", ("r",))
p.label(C, "C(1, 8)", ("ul", "l"))
p.label(M, "M(7/2, 11/2)", ("ur",))
p.label(G, "G(3, 4)", ("r", "ur", "dr"), color=PRACTICE)
OUT["agirlik-merkezi-ornek"] = b.figure(
    "<em>A</em>(2, 1), <em>B</em>(6, 3), <em>C</em>(1, 8) üçgeninin ağırlık merkezi <em>G</em>(3, 4). "
    "Turuncu <em>AM</em> kenarortayı <em>G</em> tarafından 2 : 1 oranında bölünür; diğer iki kenarortay "
    "da <em>G</em>'den geçer.",
    "Triangle A(2,1) B(6,3) C(1,8) with the median AM to M(7/2, 11/2) and the centroid G(3,4)")

# ============================================================ bolme-ornek-i
b, p = normal_board((-1, 6), (-4, 5), width=440)
p.axes(ints(-1, 5), ints(-4, 4))
P1, P2, P = (4, -3), (1, 4), (2, 5 / 3)
p.seg(P1, P2, THEORY, 2.4)
p.dot(P1)
p.dot(P2)
p.dot(P, PRACTICE, 4.6)
p.label(P1, "P_1(4, -3)", ("r",))
p.label(P2, "P_2(1, 4)", ("l",))
p.label(P, "P(2, 5/3)", ("r",), color=PRACTICE)
p.edge_label(P1, P, "2k", "dl", 13.5)
p.edge_label(P, P2, "k", "dl", 13.5)
p.note(["r = 2"], ("ur", "ul", "dl"))
OUT["bolme-ornek-i"] = b.figure(
    f"{P1c}(4, &#8722;3) ve {P2c}(1, 4) uç noktalı parçayı <em>r</em> = 2 oranında bölen nokta "
    f"<em>P</em>(2, 5/3); |{P1c}<em>P</em>|, |<em>PP</em><sub>2</sub>| uzunluğunun iki katıdır.",
    "Segment from P1(4,-3) to P2(1,4) divided by P(2, 5/3) in the ratio 2")

# ============================================================ bolme-ornek-ii
b, p = wide_board((-4, 8), (-1, 5))
p.axes(ints(-4, 7), ints(-1, 4))
P1, P2, P = (0, 3), (7, 4), (-14 / 5, 13 / 5)
p.seg(P1, P, PRACTICE, 2.2, "7 5")
p.seg(P1, P2, THEORY, 2.4)
p.dot(P1)
p.dot(P2)
p.dot(P, PRACTICE, 4.6)
p.label(P1, "P_1(0, 3)", ("u", "ur"))
p.label(P2, "P_2(7, 4)", ("ur",))
p.label(P, "P(-14/5, 13/5)", ("d",), color=PRACTICE)
p.note(["r = -2/7"], ("dr", "ur"))
OUT["bolme-ornek-ii"] = b.figure(
    f"<em>r</em> = &#8722;2/7 için bölünme noktası <em>P</em>(&#8722;14/5, 13/5), parçanın {P1c} "
    "tarafındaki uzantısı (kesikli) üzerindedir.",
    "Segment from P1(0,3) to P2(7,4) and its extension beyond P1 to P(-14/5, 13/5)", WIDE)

# ============================================================ bolme-ornek-iii
b, p = normal_board((-4, 6), (-4, 4))
p.axes(ints(-4, 5), ints(-4, 3))
P1, P2, P = (5, 3), (-3, -3), (3, 1.5)
p.seg(P1, P2, THEORY, 2.4)
p.dot(P1)
p.dot(P2)
p.dot(P, PRACTICE, 4.6)
p.label(P1, "P_1(5, 3)", ("ur",))
p.label(P2, "P_2(-3, -3)", ("dl",))
p.label(P, "P(3, 3/2)", ("dr",), color=PRACTICE)
p.edge_label(P1, P, "k", "ul", 13.5)
p.edge_label(P, P2, "3k", "ul", 13.5, ts=(0.72, 0.8, 0.64, 0.86))
p.note(["r = 1/3"], ("ul", "dr"))
OUT["bolme-ornek-iii"] = b.figure(
    f"{P1c}(5, 3) ve {P2c}(&#8722;3, &#8722;3) uç noktalı parçayı <em>r</em> = 1/3 oranında bölen nokta "
    f"<em>P</em>(3, 3/2); <em>P</em>, {P2c}'ye {P1c}'e olduğundan üç kat uzaktır.",
    "Segment from P1(5,3) to P2(-3,-3) divided by P(3, 3/2) in the ratio 1/3")

# ============================================================ bolme-ornek-iv
b, p = wide_board((-6, 11), (-1, 8))
p.axes(ints(-6, 10), ints(-1, 7), ints(-6, 10, 2), ints(-1, 7, 2))
P1, P2, P = (-5, 2), (1, 4), (10, 7)
p.seg(P2, P, BASE, 2.2, "7 5")
p.seg(P1, P2, THEORY, 2.4)
p.dot(P1)
p.dot(P2)
p.dot(P, PRACTICE, 4.6)
p.label(P1, "P_1(-5, 2)", ("d",))
p.label(P2, "P_2(1, 4)", ("dr",))
p.label(P, "P(10, 7)", ("ul",), color=PRACTICE)
p.note(["r = -5/3"], ("ul", "dr"))
OUT["bolme-ornek-iv"] = b.figure(
    f"<em>r</em> = &#8722;5/3 için bölünme noktası <em>P</em>(10, 7), parçanın {P2c} tarafındaki "
    "uzantısı (kesikli) üzerindedir.",
    "Segment from P1(-5,2) to P2(1,4) and its extension beyond P2 to P(10,7)", WIDE)

# ============================================================ egim-acisi (two panels)
b = Board(700)
pl = b.pane(30, 36, 300, (-4, 4), (-3, 4))
pr = b.pane(380, 36, 300, (-4, 4), (-3, 4))
b.fit(56)
for q in (pl, pr):
    q.axes()
# left: y = x + 1
E0, E1 = pl.clip((-1, 0), (0, 1))
pl.seg(E0, E1, THEORY, 2.4)
pl.label(E1, "d", ("r", "ur"), 15, THEORY, gap=6)
pl.arc((-1, 0), 0, PI / 4, 46, BASE, 1.8, True)
pl.angle_label((-1, 0), 0, PI / 4, 46, "\\theta", 15, BASE, inside=True, pad=1.5)
# right: y = -2x + 2
F0, F1 = pr.clip((1, 0), (0, 2))
pr.seg(F0, F1, THEORY, 2.4)
top_end = F0 if F0[1] > F1[1] else F1
pr.label(top_end, "d", ("l", "ul"), 15, THEORY, gap=6)
th = PI - math.atan(2)
pr.arc((1, 0), 0, th, 34, BASE, 1.8, True)
pr.angle_label((1, 0), 0, th, 34, "\\theta", 15, BASE)
for q, s in ((pl, "0 < \\theta < \\pi/2"), (pr, "\\pi/2 < \\theta < \\pi")):
    q.text_px(q.p.x0 + q.p.w / 2, q.p.y0 + q.p.h + 34, s, 14.5)
OUT["egim-acisi"] = b.figure(
    f"Eğim açısı {TH}, <em>X</em>-ekseninin pozitif yönünden doğruya saat yönünün tersine ölçülür. "
    f"Solda sağa doğru yükselen doğru (0 &lt; {TH} &lt; {PIs}/2), sağda sağa doğru alçalan doğru "
    f"({PIs}/2 &lt; {TH} &lt; {PIs}).",
    "Two panels: the inclination angle of a rising line is acute, that of a falling line is obtuse", WIDE)

# ============================================================ egim-dar
b, p = normal_board((-3, 6), (-1, 6))
p.axes()
P1, P2, Q = (1, 2), (4, 5), (4, 2)
E0, E1 = p.clip((-1, 0), (0, 1))
p.dashed(P1, Q, TEXT, 1.4, 0.65)
p.dashed(Q, P2, TEXT, 1.4, 0.65)
p.right_angle(Q, (-1, 0), (0, 1))
p.seg(E0, E1, THEORY, 2.4)
p.arc(P1, 0, PI / 4, 38, BASE, 1.8)
p.arc((-1, 0), 0, PI / 4, 38, BASE, 1.8)
p.dot(P1)
p.dot(P2)
p.label(E1, "d", ("r", "ur"), 15, THEORY, gap=6)
p.label(P1, "P_1(x_1, y_1)", ("ul",))
p.label(P2, "P_2(x_2, y_2)", ("ul",))
p.label(Q, "Q", ("dr",), 14, gap=6)
p.angle_label(P1, 0, PI / 4, 38, "\\theta", 15, BASE)
p.angle_label((-1, 0), 0, PI / 4, 38, "\\theta", 15, BASE)
p.edge_label(P1, Q, "x_2 - x_1", "d")
p.edge_label(Q, P2, "y_2 - y_1", "r")
OUT["egim-dar"] = b.figure(
    f"Dar eğim açısında {P1c}<em>QP</em><sub>2</sub> dik üçgeninin {P1c} köşesindeki açı {TH}'dır "
    f"(yöndeş açı); bu yüzden tan {TH} = (<em>y</em><sub>2</sub> &#8722; <em>y</em><sub>1</sub>) / "
    "(<em>x</em><sub>2</sub> &#8722; <em>x</em><sub>1</sub>).",
    "Rising line through P1 and P2 with the right triangle P1 Q P2 and the inclination angle theta")

# ============================================================ egim-genis
b, p = normal_board((-1, 7), (-1, 6))
p.axes()
P1, P2, Q = (1, 5), (4, 2), (4, 5)
E0, E1 = p.clip((6, 0), (0, 6))
p.dashed(P1, Q, TEXT, 1.4, 0.65)
p.dashed(Q, P2, TEXT, 1.4, 0.65)
p.right_angle(Q, (-1, 0), (0, -1))
p.seg(E0, E1, THEORY, 2.4)
p.arc(P1, -PI / 4, 0, 40, REMARK, 1.8)
p.arc((6, 0), 0, 3 * PI / 4, 34, BASE, 1.8, True)
p.dot(P1)
p.dot(P2)
top_end = E0 if E0[1] > E1[1] else E1
p.label(top_end, "d", ("l", "ul"), 15, THEORY, gap=6)
p.label(P1, "P_1(x_1, y_1)", ("ur", "u"))
p.label(P2, "P_2(x_2, y_2)", ("r",))
p.label(Q, "Q", ("ur",), 14, gap=6)
p.edge_label(P1, Q, "x_2 - x_1", "u")
p.edge_label(Q, P2, "y_1 - y_2", "r")
p.angle_label(P1, -PI / 4, 0, 40, "\\pi - \\theta", 14, REMARK)
p.angle_label((6, 0), 0, 3 * PI / 4, 34, "\\theta", 15, BASE)
OUT["egim-genis"] = b.figure(
    f"Geniş eğim açısında {P1c}<em>QP</em><sub>2</sub> üçgeninin {P1c} köşesindeki iç açı {PIs} &#8722; {TH}'dır; "
    f"tan({PIs} &#8722; {TH}) = &#8722;tan {TH} olduğundan formül yine aynı çıkar.",
    "Falling line through P1 and P2 with the right triangle P1 Q P2; the angle at P1 is pi minus theta")

# ============================================================ egim-hesabi-a
b, p = normal_board((-4, 4), (-3, 4))
p.axes(ints(-4, 3), ints(-3, 3))
P1, P2, Q = (-2, -1), (1, 2), (1, -1)
E0, E1 = p.clip((-1, 0), (0, 1))
p.dashed(P1, Q, TEXT, 1.4, 0.65)
p.dashed(Q, P2, TEXT, 1.4, 0.65)
p.seg(E0, E1, THEORY, 2.4)
p.arc((-1, 0), 0, PI / 4, 36, BASE, 1.8)
p.dot(P1)
p.dot(P2)
p.label(P1, "P_1(-2, -1)", ("dr", "d"))
p.label(P2, "P_2(1, 2)", ("ul",))
p.edge_label(P1, Q, "3", "d", 14)
p.edge_label(Q, P2, "3", "r", 14)
p.angle_label((-1, 0), 0, PI / 4, 36, "\\theta = \\pi/4", 14, BASE)
OUT["egim-hesabi-a"] = b.figure(
    f"{P1c}(&#8722;2, &#8722;1) ve {P2c}(1, 2)'den geçen doğruda yatay ve düşey değişim 3'er birimdir; "
    f"eğim 1, eğim açısı {PIs}/4'tür.",
    "Line y = x + 1 through P1(-2,-1) and P2(1,2) with run 3, rise 3 and inclination pi/4")

# ============================================================ egim-hesabi-b
b, p = normal_board((-1, 4), (-1, 4), width=460)
p.axes(ints(-1, 3), ints(-1, 3))
r3 = math.sqrt(3)
P1, P2 = (0, 2 * r3), (2, 0)
E0, E1 = p.clip(P1, P2)
p.seg(E0, E1, THEORY, 2.4)
up = PI - PI / 3
p.arc(P2, 0, up, 40, BASE, 1.8, True)
p.arc(P2, up, PI, 26, REMARK, 1.8)
p.dot(P1)
p.dot(P2)
p.label(P1, "P_1(0, 2\\sqrt{3})", ("r",))
p.label(P2, "P_2(2, 0)", ("dl", "d"))
p.angle_label(P2, 0, up, 40, "\\theta = 2\\pi/3", 14, BASE)
p.angle_label(P2, up, PI, 26, "\\pi/3", 14, REMARK)
OUT["egim-hesabi-b"] = b.figure(
    f"{P1c}(0, 2{SQ3}) ve {P2c}(2, 0)'dan geçen doğrunun eğimi &#8722;{SQ3}'tür; doğru <em>X</em>-ekseninin "
    f"negatif yönüyle {PIs}/3'lük açı yapar, eğim açısı {TH} = 2{PIs}/3'tür.",
    "Falling line through P1(0, 2 sqrt 3) and P2(2,0) with inclination 2 pi/3 and the supplementary angle pi/3")

# ============================================================ egim-hesabi-c
b, p = normal_board((-1, 5), (-2, 5), width=450)
p.axes(ints(-1, 4), ints(-2, 4))
P1, P2 = (3, -1), (3, 4)
p.seg((3, -2), (3, 5), THEORY, 2.4)
p.right_angle((3, 0), (1, 0), (0, 1), 13, BASE, 1.0)
p.dot(P1)
p.dot(P2)
p.label(P1, "P_1(3, -1)", ("r",))
p.label(P2, "P_2(3, 4)", ("r",))
p.label((3, 0), "\\theta = \\pi/2", ("ur",), 14, BASE, gap=20)
OUT["egim-hesabi-c"] = b.figure(
    f"{P1c}(3, &#8722;1) ve {P2c}(3, 4)'ten geçen doğru düşeydir: eğim açısı {PIs}/2, eğimi tanımsızdır.",
    "Vertical line x = 3 through P1(3,-1) and P2(3,4) meeting the X axis at a right angle")

# ============================================================ esdogrusal
b, p = wide_board((-4, 10), (-1, 5))
p.axes(ints(-4, 9), ints(-1, 4), ints(-4, 9, 2), ints(-1, 4, 2))
A, B_, C = (-3, 4), (3, 2), (6, 1)
E0, E1 = p.clip(A, C)
# the two horizontal legs share A..(3,4): interleave their dashes so both colors show
p.seg(A, (6, 4), BASE, 2.0, "6 6", 1.0, "guide")
xa, ya = p.px(A)
xo, yo = p.px((3, 4))
p.add(f'<path d="M{xa:.1f},{ya:.1f} L{xo:.1f},{yo:.1f}" fill="none" stroke="{PRACTICE}" stroke-width="2.0" '
      f'stroke-dasharray="6 6" stroke-dashoffset="6" stroke-linecap="butt"/>')
p.seg((3, 4), B_, PRACTICE, 2.0, "6 6", 1.0, "guide")
p.seg((6, 4), C, BASE, 2.0, "6 6", 1.0, "guide")
p.seg(E0, E1, THEORY, 2.4)
# dimension line for the green horizontal leg, above the orange one
yd = 4 + 30 / p.ppu
p.arrow((1.5, yd), (6, yd), BASE, 1.1, 7)
p.arrow((1.5, yd), (-3, yd), BASE, 1.1, 7)
for x in (-3, 6):
    X, Y = p.px((x, yd))
    p.poly_px([(X, Y - 5), (X, Y + 5)], BASE, 1.0, None, 0.9, "mark")
for V in (A, B_, C):
    p.dot(V)
X9, Y9 = p.px((1.5, yd))
p.text_px(X9, Y9 - 7, "9", 14, BASE, "middle", True)
p.edge_label(A, (3, 4), "6", "u", 14, PRACTICE, 4, (0.5, 0.4, 0.6))
p.edge_label((3, 4), B_, "2", "r", 14, PRACTICE)
p.edge_label((6, 4), C, "3", "r", 14, BASE)
p.label(A, "A(-3, 4)", ("ul", "u", "l"))
p.label(B_, "B(3, 2)", ("u", "ur", "ul"))
p.label(C, "C(6, 1)", ("u", "ur", "ul"))
OUT["esdogrusal"] = b.figure(
    "<em>A</em>'dan başlayan iki eğim üçgeni: turuncu üçgende düşey değişim / yatay değişim = 2/6, yeşil "
    "üçgende 3/9. Eğimler eşit (&#8722;1/3) olduğundan <em>A</em>, <em>B</em>, <em>C</em> aynı doğru üzerindedir.",
    "Points A(-3,4), B(3,2), C(6,1) on one line with two slope triangles from A of legs 6, 2 and 9, 3", WIDE)

# ============================================================ paralel-dogrular
b, p = normal_board((-5, 5), (-2, 5))
p.axes()
d1a, d1b = p.clip((-4, 0), (0, 2))
d2a, d2b = p.clip((2, 0), (0, -1))
p.seg(d1a, d1b, THEORY, 2.4)
p.seg(d2a, d2b, PRACTICE, 2.4)
th = math.atan(0.5)
p.arc((-4, 0), 0, th, 62, BASE, 1.8)
p.arc((2, 0), 0, th, 62, BASE, 1.8)
p.label(max(d1a, d1b), "d_1", ("r", "ur"), 15, THEORY, gap=6)
p.label(max(d2a, d2b), "d_2", ("r", "ur"), 15, PRACTICE, gap=6)
p.angle_label((-4, 0), 0, th, 62, "\\theta", 15, BASE)
p.angle_label((2, 0), 0, th, 62, "\\theta", 15, BASE)
p.note(["m_1 = m_2"], ("ul", "ur", "dr"))
OUT["paralel-dogrular"] = b.figure(
    f"Paralel {D1c} ve {D2c} doğruları <em>X</em>-ekseniyle aynı {TH} açısını yapar; bu yüzden eğimleri eşittir.",
    "Two parallel lines with equal inclination angles theta at their X intercepts")

# ============================================================ dik-dogrular
b, p = normal_board((-3, 5), (-2, 5))
p.axes()
d1a, d1b = p.clip((0.5, 0), (2, 3))
d2a, d2b = p.clip((2, 3), (0, 4))
K = (2, 3)
p.seg(d1a, d1b, THEORY, 2.4)
p.seg(d2a, d2b, PRACTICE, 2.4)
p.right_angle(K, (1, 2), (-2, 1), 13)
th1 = math.atan(2)
p.arc((0.5, 0), 0, th1, 34, BASE, 1.8)
p.dot(K)
p.label(max(d1a, d1b, key=lambda q: q[1]), "d_1", ("ur", "r"), 15, THEORY, gap=6)
p.label(min(d2a, d2b), "d_2", ("ul", "l", "u"), 15, PRACTICE, gap=6)
p.angle_label((0.5, 0), 0, th1, 34, "\\theta_1", 15, BASE)
p.note(["m_1 m_2 = -1"], ("ur", "dr"))
OUT["dik-dogrular"] = b.figure(
    f"Dik {D1c} (eğim 2) ve {D2c} (eğim &#8722;1/2) doğruları (2, 3) noktasında dik açıyla kesişir; "
    "eğimlerinin çarpımı &#8722;1'dir.",
    "Perpendicular lines y = 2x - 1 and y = -x/2 + 4 meeting at (2,3) with a right angle mark")

# ============================================================ dik-ucgen-i
b, p = normal_board((-5, 5), (-2, 10), width=440)
p.axes(ints(-5, 4), ints(-2, 9), ints(-4, 4, 2), ints(-2, 9, 2))
A, B_, C = (-4, -1), (3, 2), (0, 9)
p.poly_px([p.px(A), p.px(B_), p.px(C), p.px(A)], THEORY, 2.2)
p.right_angle(B_, (A[0] - B_[0], A[1] - B_[1]), (C[0] - B_[0], C[1] - B_[1]), 13)
for V in (A, B_, C):
    p.dot(V)
p.label(A, "A(-4, -1)", ("dl", "d"))
p.label(B_, "B(3, 2)", ("r",))
p.label(C, "C(0, 9)", ("u", "ur"))
p.edge_label(B_, C, "m_{BC} = -7/3", "r", 13.5)
p.edge_label(A, B_, "m_{AB} = 3/7", "dr", 13.5)
OUT["dik-ucgen-i"] = b.figure(
    "<em>A</em>(&#8722;4, &#8722;1), <em>B</em>(3, 2), <em>C</em>(0, 9) üçgeninde <em>m<sub>AB</sub></em> · "
    "<em>m<sub>BC</sub></em> = &#8722;1; üçgen <em>B</em> köşesinde dik açılıdır.",
    "Right triangle A(-4,-1) B(3,2) C(0,9) with the right angle at B and the slopes of AB and BC")

# ============================================================ dik-ucgen-ii
b, p = normal_board((-3, 4), (-3, 5), width=440)
p.axes(ints(-3, 3), ints(-3, 4))
A, B_, C = (-2, 3), (0, 4), (3, -2)
p.poly_px([p.px(A), p.px(B_), p.px(C), p.px(A)], THEORY, 2.2)
p.right_angle(B_, (A[0] - B_[0], A[1] - B_[1]), (C[0] - B_[0], C[1] - B_[1]), 13)
for V in (A, B_, C):
    p.dot(V)
p.label(A, "A(-2, 3)", ("l",))
p.label(B_, "B(0, 4)", ("ur", "u"))
p.label(C, "C(3, -2)", ("dr",))
p.edge_label(A, B_, "m_{AB} = 1/2", "u", 13.5)
p.edge_label(B_, C, "m_{BC} = -2", "r", 13.5)
OUT["dik-ucgen-ii"] = b.figure(
    "<em>A</em>(&#8722;2, 3), <em>B</em>(0, 4), <em>C</em>(3, &#8722;2) üçgeninde <em>m<sub>AB</sub></em> · "
    "<em>m<sub>BC</sub></em> = (1/2)(&#8722;2) = &#8722;1; dik açı <em>B</em> köşesindedir.",
    "Right triangle A(-2,3) B(0,4) C(3,-2) with the right angle at B and the slopes of AB and BC")

# ============================================================ paralelkenar
b, p = normal_board((-1, 6), (-1, 5), width=460)
p.axes(ints(-1, 5), ints(-1, 4), origin=False)
A, B_, C, D = (0, 0), (4, 1), (5, 4), (1, 3)
p.poly_px([p.px(A), p.px(B_), p.px(C), p.px(D), p.px(A)], THEORY, 2.2)
p.chevrons(A, B_, 1)
p.chevrons(D, C, 1)
p.chevrons(B_, C, 2)
p.chevrons(A, D, 2)
for V in (A, B_, C, D):
    p.dot(V)
p.label(A, "A(0, 0)", ("dl",))
p.label(B_, "B(4, 1)", ("dr",))
p.label(C, "C(5, 4)", ("ur",))
p.label(D, "D(1, 3)", ("ul",))
OUT["paralelkenar"] = b.figure(
    "<em>ABCD</em> dörtgeninde karşılıklı kenarların eğimleri eşittir: <em>AB</em> ve <em>DC</em> için 1/4 "
    "(tek ok), <em>BC</em> ve <em>AD</em> için 3 (çift ok). Dörtgen bir paralelkenardır.",
    "Parallelogram A(0,0) B(4,1) C(5,4) D(1,3) with parallel marks on opposite sides")

# ============================================================ dik-parametre
b, p = normal_board((-2, 4), (-3, 3), width=460)
p.axes(ints(-2, 3), ints(-3, 2))
A, B_, C, D = (1, 2), (3, -2), (-1, 0), (3, 2)
K = (7 / 5, 6 / 5)
p.seg(lerp(C, D, -0.18), lerp(C, D, 1.18), PRACTICE, 2.4)
p.seg(lerp(A, B_, -0.16), lerp(A, B_, 1.16), THEORY, 2.4)
p.right_angle(K, (D[0] - C[0], D[1] - C[1]), (A[0] - B_[0], A[1] - B_[1]), 12)
for V in (A, B_, C, D):
    p.dot(V)
p.label(C, "C(-1, 0)", ("dl",))
p.label(D, "D(3, 2)", ("ur",))
p.label(A, "A(1, 2)", ("ul",))
p.label(B_, "B(3, -2)", ("dr",))
OUT["dik-parametre"] = b.figure(
    "<em>k</em> = &#8722;2 için <em>AB</em> doğrusu (eğim &#8722;2) <em>CD</em> doğrusuna (eğim 1/2) diktir; "
    "iki doğru (7/5, 6/5) noktasında kesişir.",
    "Line AB through A(1,2) and B(3,-2) perpendicular to line CD through C(-1,0) and D(3,2)")

# ============================================================ yonlu-aci
b = Board(560)
p = b.pane(40, 30, 480, (-2.7, 2.7), (-2.25, 2.25))
b.fit(40)
K = (0, 0)
a1, a2 = math.radians(50), math.radians(135)
L = 2.45
d1a, d1b = (-L * math.cos(a1), -L * math.sin(a1)), (L * math.cos(a1), L * math.sin(a1))
d2a, d2b = (-L * math.cos(a2), -L * math.sin(a2)), (L * math.cos(a2), L * math.sin(a2))
p.seg(d1a, d1b, THEORY, 2.4)
p.seg(d2a, d2b, PRACTICE, 2.4)
p.arc(K, a1, a2, 48, BASE, 1.9, True)
p.arc(K, a2, a1 + PI, 72, REMARK, 1.9, True)
p.dot(K)
p.label(d1b, "d_1", ("r", "ur"), 15, THEORY, gap=6)
p.label(d2b, "d_2", ("l", "ul"), 15, PRACTICE, gap=6)
p.label(K, "K", ("d",), 15, gap=10)
p.angle_label(K, a1, a2, 48, "\\alpha", 16, BASE)
p.angle_label(K, a2, a1 + PI, 72, "\\beta", 16, REMARK)
p.text_px(p.p.x0 + p.p.w / 2, p.p.y0 + p.p.h + 26, "\\alpha + \\beta = \\pi", 14.5)
OUT["yonlu-aci"] = b.figure(
    f"{D1c}'den {D2c}'ye yönlenmiş açı {AL}, {D2c}'den {D1c}'e yönlenmiş açı {BE}; ikisi de saat yönünün "
    f"tersine ölçülür ve {AL} + {BE} = {PIs}'dir.",
    "Two lines d1 and d2 meeting at K with the directed angles alpha from d1 to d2 and beta from d2 to d1")

# ============================================================ aci-ispat
b, p = wide_board((-4, 7), (-2, 6))
p.axes()
K = (2, 4)
d1a, d1b = p.clip((-2, 0), K)
d2a, d2b = p.clip((4, 0), K)
p.seg(d1a, d1b, THEORY, 2.4)
p.seg(d2a, d2b, PRACTICE, 2.4)
t1, t2 = PI / 4, PI - math.atan(2)
p.arc((-2, 0), 0, t1, 36, THEORY, 1.8)
p.arc((4, 0), 0, t2, 30, PRACTICE, 1.8)
p.arc(K, t1, t2, 34, BASE, 1.9, True)
p.arc(K, t2, t1 + PI, 54, REMARK, 1.9, True)
p.dot(K)
low1 = min(d1a, d1b, key=lambda q: q[1])
low2 = min(d2a, d2b, key=lambda q: q[1])
p.label(low1, "d_1", ("l", "dl", "ul"), 15, THEORY, gap=6)
p.label(low2, "d_2", ("r", "dr", "ur"), 15, PRACTICE, gap=6)
p.label(K, "K", ("r", "ur"), 15, gap=9)
p.angle_label((-2, 0), 0, t1, 36, "\\theta_1", 15, THEORY)
p.angle_label((4, 0), 0, t2, 30, "\\theta_2", 15, PRACTICE)
p.angle_label(K, t1, t2, 34, "\\alpha", 16, BASE)
p.angle_label(K, t2, t1 + PI, 54, "\\beta", 16, REMARK)
OUT["aci-ispat"] = b.figure(
    f"{D1c} ve {D2c} doğrularının eğim açıları {TH}<sub>1</sub>, {TH}<sub>2</sub>; kesişim noktasındaki "
    f"yönlenmiş açılar {AL} ve {BE}. Üçgenin dış açısı olarak {TH}<sub>2</sub> = {TH}<sub>1</sub> + {AL}'dır.",
    "Lines d1 and d2 with inclination angles theta1 and theta2 and the directed angles alpha and beta at K")

# ============================================================ aci-ornek
b, p = normal_board((-2, 3), (-1, 5), width=460)
p.axes(ints(-2, 2), ints(-1, 4))
K = (3 / 5, 11 / 5)
d1a, d1b = p.clip((0, 1), (1, 3))
d2a, d2b = p.clip((0, 4), (1, 1))
p.seg(d1a, d1b, THEORY, 2.4)
p.seg(d2a, d2b, PRACTICE, 2.4)
u1, u2 = math.atan(2), PI - math.atan(3)
p.arc(K, u1, u2, 40, BASE, 1.9, True)
p.arc(K, u2, u1 + PI, 62, REMARK, 1.9, True)
for V in ((0, 1), (1, 3), (0, 4), (1, 1)):
    p.dot(V, TEXT, 3.6)
p.dot(K, TEXT, 4.2)
p.label(max(d1a, d1b, key=lambda q: q[1]), "d_1", ("r", "ur"), 15, THEORY, gap=6)
p.label(max(d2a, d2b, key=lambda q: -q[1]), "d_2", ("r", "dr"), 15, PRACTICE, gap=6)
p.label((0, 1), "(0, 1)", ("r", "dr"), 13.5)
p.label((1, 3), "(1, 3)", ("r", "dr"), 13.5)
p.label((0, 4), "(0, 4)", ("r", "ur"), 13.5)
p.label((1, 1), "(1, 1)", ("r", "ur"), 13.5)
p.label(K, "K", ("r", "dr"), 15)
p.angle_label(K, u1, u2, 40, "\\alpha = \\pi/4", 14, BASE)
p.angle_label(K, u2, u1 + PI, 62, "\\beta = 3\\pi/4", 14, REMARK)
OUT["aci-ornek"] = b.figure(
    f"{D1c} (eğim 2) ve {D2c} (eğim &#8722;3) doğruları <em>K</em>(3/5, 11/5) noktasında kesişir; "
    f"{D1c}'den {D2c}'ye yönlenmiş açı {AL} = {PIs}/4, ters yöndeki açı {BE} = 3{PIs}/4'tür.",
    "Lines y = 2x + 1 and y = -3x + 4 meeting at K(3/5, 11/5) with directed angles pi/4 and 3 pi/4")

# ============================================================ dusey-aci
b, p = normal_board((-1, 4), (-1, 5), width=460)
p.axes(ints(-1, 3), ints(-1, 4))
K = (2, 2 * r3)
d2a, d2b = p.clip((0, 0), (1, r3))
p.seg((2, -1), (2, 5), THEORY, 2.4)
p.seg(d2a, d2b, PRACTICE, 2.4)
p.arc(K, PI / 2, PI + PI / 3, 44, BASE, 1.9, True)
p.arc(K, PI / 3, PI / 2, 60, REMARK, 1.9, True)
p.arc((0, 0), 0, PI / 3, 34, PRACTICE, 1.7)
p.dot(K)
p.label((2, 5), "d_1", ("r", "ur"), 15, THEORY, gap=6)
p.label(max(d2a, d2b, key=lambda q: q[1]), "d_2", ("r", "dr"), 15, PRACTICE, gap=6)
p.label(K, "K", ("r", "dr"), 15)
p.angle_label(K, PI / 2, PI + PI / 3, 44, "\\alpha = 5\\pi/6", 14, BASE)
# the 30-degree wedge is too narrow for its label: put it just outside, beside the arc's start on d2
KX, KY = p.px(K)
p.label(None, "\\beta = \\pi/6", ("r", "dr"), 14, REMARK, gap=8,
        px=(KX + 60 * math.cos(PI / 3), KY - 60 * math.sin(PI / 3)))
p.angle_label((0, 0), 0, PI / 3, 34, "\\pi/3", 14, PRACTICE)
OUT["dusey-aci"] = b.figure(
    f"Düşey {D1c} ile eğimi {SQ3} olan {D2c} doğrusu: {D1c}'den {D2c}'ye yönlenmiş açı {AL} = 5{PIs}/6, "
    f"{D2c}'den {D1c}'e yönlenmiş açı {BE} = {PIs}/6'dır.",
    "Vertical line x = 2 and the line y = sqrt(3) x meeting at K with directed angles 5 pi/6 and pi/6")

# ============================================================ ic-acilar
b, p = normal_board((-1, 6), (-5, 3), width=440)
p.axes(ints(-1, 5), ints(-5, 2))
A, B_, C = (5, -4), (1, -2), (3, 2)
p.poly_px([p.px(A), p.px(B_), p.px(C), p.px(A)], THEORY, 2.2)
p.eqticks(B_, A, 1, t=0.4)
p.eqticks(B_, C, 1, t=0.4)
p.right_angle(B_, (A[0] - B_[0], A[1] - B_[1]), (C[0] - B_[0], C[1] - B_[1]), 14, TEXT)
aA0, aA1 = ang(A, C), ang(A, B_)
aC0, aC1 = ang(C, B_) + 2 * PI, ang(C, A) + 2 * PI
p.arc(A, aA0, aA1, 34, BASE, 1.8)
p.arc(C, aC0, aC1, 34, BASE, 1.8)
Gc = ((5 + 1 + 3) / 3, (-4 - 2 + 2) / 3)
p.arc(Gc, math.radians(-40), math.radians(245), 20, REMARK, 1.6, True)
for V in (A, B_, C):
    p.dot(V)
p.label(A, "A(5, -4)", ("dr", "r", "d"))
p.label(B_, "B(1, -2)", ("l",))
p.label(C, "C(3, 2)", ("u", "ur"))
p.angle_label(A, aA0, aA1, 34, "\\pi/4", 14, BASE)
p.angle_label(C, aC0, aC1, 34, "\\pi/4", 14, BASE)
aB0, aB1 = ang(B_, A), ang(B_, C)
p.angle_label(B_, aB0, aB1, 20, "\\pi/2", 14, TEXT)
OUT["ic-acilar"] = b.figure(
    "<em>A</em>(5, &#8722;4), <em>B</em>(1, &#8722;2), <em>C</em>(3, 2) üçgeninin iç açıları: <em>B</em>'de "
    f"{PIs}/2, <em>A</em> ve <em>C</em>'de {PIs}/4. Köşeler saat yönünün tersine <em>A</em>, <em>C</em>, "
    "<em>B</em> sırasıyla dolaşılır; çentikler |<em>AB</em>| = |<em>BC</em>| eşitliğini gösterir.",
    "Isosceles right triangle A(5,-4) B(1,-2) C(3,2) with interior angles pi/4, pi/2, pi/4")

# ============================================================ exr-bolenden-uc
b, p = normal_board((-1, 18), (-13, 10), width=480)
p.axes(ints(-1, 17, 2), ints(-13, 9, 2))
P1, P, P2 = (6, 8), (9, 2), (16, -12)
p.seg(P1, P2, THEORY, 2.4)
p.dot(P1)
p.dot(P2)
p.dot(P, PRACTICE, 4.6)
p.label(P1, "P_1(6, 8)", ("r",))
p.label(P, "P(9, 2)", ("r",), color=PRACTICE)
p.label(P2, "P_2(16, -12)", ("l",))
p.edge_label(P1, P, "3\\sqrt{5}", "l", 13.5)
p.edge_label(P, P2, "7\\sqrt{5}", "l", 13.5)
OUT["exr-bolenden-uc"] = b.figure(
    f"{P1c}(6, 8) ile {P2c}(16, &#8722;12) arasındaki <em>P</em>(9, 2) noktası parçayı "
    f"|{P1c}<em>P</em>| : |<em>PP</em><sub>2</sub>| = 3&#8730;5 : 7&#8730;5 = 3 : 7 oranında böler.",
    "Segment from P1(6,8) to P2(16,-12) divided by P(9,2) into pieces 3 sqrt 5 and 7 sqrt 5")

# ============================================================ exr-yonlu-aci
b, p = wide_board((-6, 10), (-1, 10))
p.axes(ints(-6, 9, 2), ints(-1, 9, 2))
A, B_, C, D = (-4, 5), (3, 9), (-2, 4), (9, 1)
K = (-59 / 13, 61 / 13)
ab0, ab1 = p.clip(A, B_)
cd0, cd1 = p.clip(C, D)
p.seg(ab0, ab1, THEORY, 2.4)
p.seg(cd0, cd1, PRACTICE, 2.4)
k0, k1 = math.atan(4 / 7), PI - math.atan(3 / 11)
p.arc(K, k0, k1, 58, BASE, 1.9, True)
for V in (A, B_, C, D):
    p.dot(V)
p.dot(K, TEXT, 3.2)
p.label(max(ab0, ab1, key=lambda q: q[1]), "AB", ("ur", "r"), 15, THEORY, gap=6)
p.label(max(cd0, cd1), "CD", ("dr", "r", "d"), 15, PRACTICE, gap=6)
p.label(B_, "B(3, 9)", ("l",))
p.label(D, "D(9, 1)", ("d",))
p.label(C, "C(-2, 4)", ("d",))
p.label(A, "A(-4, 5)", ("u", "ur"))
p.angle_label(K, k0, k1, 58, "3\\pi/4", 14, BASE)
OUT["exr-yonlu-aci"] = b.figure(
    f"<em>A</em>(&#8722;4, 5) ve <em>B</em>(3, 9)'dan geçen doğrudan <em>C</em>(&#8722;2, 4) ve <em>D</em>(9, 1)'den "
    f"geçen doğruya yönlenmiş açı 3{PIs}/4'tür.",
    "Line AB through A(-4,5) and B(3,9) and line CD through C(-2,4) and D(9,1) with directed angle 3 pi/4", WIDE)

# ============================================================ exr-egimden-egim
b, p = normal_board((-3, 3), (-3, 4), width=450)
p.axes()
m2 = -(2 + r3)
d1a, d1b = p.clip((0, 0), (1, 1))
d2a, d2b = p.clip((0, 0), (1, m2))
p.seg(d1a, d1b, THEORY, 2.4)
p.seg(d2a, d2b, PRACTICE, 2.4)
up2 = PI + math.atan(m2)
p.arc((0, 0), 0, PI / 4, 34, REMARK, 1.8)
p.arc((0, 0), PI / 4, up2, 62, BASE, 1.9, True)
p.label(max(d1a, d1b), "d_1", ("ur", "r"), 15, THEORY, gap=6)
p.label(max(d2a, d2b, key=lambda q: q[1]), "d_2", ("ul", "l"), 15, PRACTICE, gap=6)
p.angle_label((0, 0), 0, PI / 4, 34, "\\pi/4", 14, REMARK)
p.angle_label((0, 0), PI / 4, up2, 62, "\\alpha = \\pi/3", 14, BASE)
p.note(["m_1 = 1", "m_2 = -2 - \\sqrt{3}"], ("dr", "ur", "dl"))
OUT["exr-egimden-egim"] = b.figure(
    f"Eğimi 1 olan {D1c} doğrusu {PIs}/3 döndürülünce eğim açısı {PIs}/4 + {PIs}/3 = 7{PIs}/12 olan {D2c} "
    f"doğrusuna paralel olur; {D2c}'nin eğimi &#8722;2 &#8722; {SQ3}'tür.",
    "Lines y = x and y = -(2 + sqrt 3) x through the origin with the directed angle pi/3 between them")

# ============================================================ exr-kirk-bes-derece
b, p = normal_board((-1, 7), (-4, 5))
p.axes(ints(-1, 6), ints(-4, 4))
A, B_ = (2, -1), (5, 3)
ab0, ab1 = p.clip(A, B_)
dd0, dd1 = p.clip(A, (3, -8))
dp0, dp1 = (-0.8, -1 - 2.8 / 7), (6.6, -1 + 4.6 / 7)
p.seg(ab0, ab1, THEORY, 2.4)
p.seg(dd0, dd1, PRACTICE, 2.4)
p.seg(dp0, dp1, BASE, 2.4)
aAB, aD, aDp = math.atan(4 / 3), PI - math.atan(7), math.atan(1 / 7)
p.arc(A, aAB, aD, 36, TEXT, 1.7)
p.arc(A, aDp, aAB, 68, TEXT, 1.7)
p.dot(A)
p.dot(B_)
p.label(max(ab0, ab1, key=lambda q: q[1]), "AB", ("ur", "r"), 15, THEORY, gap=6)
p.label(max(dd0, dd1, key=lambda q: q[1]), "m = -7", ("r", "ur", "u"), 14, PRACTICE, gap=6)
p.label(dp1, "m = 1/7", ("r", "ur"), 14, BASE, gap=6)
p.label(A, "A(2, -1)", ("dr",))
p.label(B_, "B(5, 3)", ("r",))
p.angle_label(A, aAB, aD, 36, "\\pi/4", 13.5, TEXT, pad=1.2)
p.angle_label(A, aDp, aAB, 68, "\\pi/4", 14, TEXT)
OUT["exr-kirk-bes-derece"] = b.figure(
    f"<em>AB</em> doğrusuyla {PIs}/4'lük açı yapan iki yön vardır: eğimi &#8722;7 ve eğimi 1/7 olan doğrular "
    "(burada <em>A</em>'dan geçecek biçimde çizildi). Bu iki doğru birbirine diktir.",
    "Line AB through A(2,-1) and B(5,3) with the two lines through A of slopes -7 and 1/7 making pi/4 with it")

# ============================================================ exr-kirk-bes-derece-dogru
b, p = wide_board((-7, 8), (-1, 8))
p.axes(ints(-7, 7), ints(-1, 7), ints(-6, 7, 2), ints(-1, 7, 2))
Q = (2, 5)
bl0, bl1 = p.clip((-6, 0), (3, 3))
or0, or1 = p.clip((0, 1), Q)
gr0, gr1 = p.clip((0, 6), Q)
p.seg(bl0, bl1, THEORY, 2.4)
p.seg(or0, or1, PRACTICE, 2.4)
p.seg(gr0, gr1, BASE, 2.4)
X1, X2 = (3 / 5, 11 / 5), (24 / 5, 18 / 5)
p.arc(X1, math.atan(1 / 3), math.atan(2), 36, TEXT, 1.7)
p.arc(X2, PI - math.atan(0.5), PI + math.atan(1 / 3), 36, TEXT, 1.7)
p.right_angle(Q, (-1, -2), (2, -1), 12)
p.dot(Q, PRACTICE, 4.6)
p.label(Q, "Q(2, 5)", ("ul",), color=PRACTICE)
p.label(max(bl0, bl1), "x - 3y + 6 = 0", ("dl", "d"), 14, THEORY, gap=8)
p.label(max(or0, or1, key=lambda q: q[1]), "2x - y + 1 = 0", ("r",), 14, PRACTICE, gap=8)
p.label(max(gr0, gr1), "x + 2y - 12 = 0", ("u", "ul"), 14, BASE, gap=8)
p.angle_label(X1, math.atan(1 / 3), math.atan(2), 36, "\\pi/4", 14, TEXT)
p.angle_label(X2, PI - math.atan(0.5), PI + math.atan(1 / 3), 36, "\\pi/4", 14, TEXT)
OUT["exr-kirk-bes-derece-dogru"] = b.figure(
    "<em>Q</em>(2, 5)'ten geçen ve <em>x</em> &#8722; 3<em>y</em> + 6 = 0 doğrusuyla " + PIs + "/4'lük açı yapan iki "
    "doğru: 2<em>x</em> &#8722; <em>y</em> + 1 = 0 ve <em>x</em> + 2<em>y</em> &#8722; 12 = 0. İki çözüm "
    "doğrusu <em>Q</em>'da dik kesişir.",
    "Line x - 3y + 6 = 0 and the two lines through Q(2,5) making pi/4 with it, perpendicular to each other", WIDE)


# ---------------------------------------------------------------------------
for name, content in OUT.items():
    with io.open(OUT_DIR / f"analytic-bea-{name}.md", "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
print("generated:", len(OUT), "figures")
