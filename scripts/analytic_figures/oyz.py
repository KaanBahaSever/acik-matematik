# -*- coding: utf-8 -*-
"""Figures for dersler/analitik-geometri/ozel-yuzeyler.qmd (chapter key: oyz).

Every drawing here is three-dimensional and goes through scripts/svg_plot3.py
(orthographic Camera on an equal-aspect svg_plot.Plot panel). The figures go
INSIDE the box they explain (example, solution, proof), never inside a
definition box.

Surfaces are drawn translucent: their faces are grouped into a few paths by
orientation and shade, a sparse net of parameter lines and the silhouette are
added, and every curve (traces, axes, net, silhouette) is split into visible
and hidden runs by casting a ray toward the viewer against a triangle mesh of
the surfaces (numpy). Hidden runs are drawn dashed and faint.

Labels are placed after the projection, in page pixels: `Fig.place` tries a
ring of candidate positions around the anchor and keeps the one that touches
no drawn line, point or earlier label, so labels never sit on the geometry.

Usage:   python scripts/analytic_figures/oyz.py
         python scripts/center_figures.py "analytic-oyz-*.md" --keep-width
Output:  scripts/_figures/analytic-oyz-<name>.md
"""
import html
import math
import re
import sys
from pathlib import Path

import numpy as np

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, WIDE, TEXT, BG, THEORY, PRACTICE, BASE, REMARK  # noqa: E402
from svg_plot3 import Camera, Space, vadd, vsub, vscale, vdot, vcross, vnorm, vunit  # noqa: E402

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
OUT = {}
ONLY = set(sys.argv[1:])          # optional: build only the named figures

MINUS, SQRT = "−", "√"
NAME, DESC, TICK, AXIS = 13.5, 12.5, 11, 14.5      # font sizes (px)
TAU = 2 * math.pi

# ---------------------------------------------------------------------------
# text helpers
# ---------------------------------------------------------------------------


def it(s):
    return f'<tspan font-style="italic">{s}</tspan>'


def sub(s, size=NAME):
    return (f'<tspan font-size="{0.76 * size:.1f}" dy="4">{s}</tspan>'
            f'<tspan dy="-4">&#8203;</tspan>')


def num(v):
    """Number with a real minus sign and a decimal comma."""
    s = str(int(v)) if float(v).is_integer() else str(v).replace(".", ",")
    return s.replace("-", MINUS)


def triple(*vs):
    return "(" + ", ".join(v if isinstance(v, str) else num(v) for v in vs) + ")"


def eq(s):
    """Italicise single latin letters of a short formula: 'x² + y² = 4'."""
    return re.sub(r"(?<![A-Za-z&#;])([a-z])(?![A-Za-z;])", lambda m: it(m.group(1)), s)


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

# up="y" draws the math y axis vertically (a cyclic permutation keeps the axes right-handed)
PERM = {"z": (lambda P: P, lambda W: W),
        "y": (lambda P: (P[2], P[0], P[1]), lambda W: (W[1], W[2], W[0]))}


class PermCamera(Camera):
    def __init__(self, az, el, T):
        super().__init__(az, el)
        self.T = T

    def project(self, P):
        return super().project(self.T(P))


# styles of visible / hidden runs
VIS_TRACE = dict(width=2.4, opacity=1.0)
HID_TRACE = dict(width=1.5, dash="5 4", opacity=0.7)


# ---------------------------------------------------------------------------
# the figure object: a Space plus a registry of what is drawn, in pixels
# ---------------------------------------------------------------------------


class Fig:
    def __init__(self, az, el, extent, width=600, pad=80, up="z"):
        T, Tinv = PERM[up]
        self.cam = PermCamera(az, el, T)
        pr = [self.cam.project(P) for P in extent]
        xs, ys = [a for a, _, _ in pr], [b for _, b, _ in pr]
        self.ppu = width / (max(xs) - min(xs))
        h = (max(ys) - min(ys)) * self.ppu
        self.p = Plot(pad, pad, width, h, (min(xs), max(xs)), (min(ys), max(ys)))
        self.S = Space(self.p, self.cam)
        self.W, self.H = width + 2 * pad, h + 2 * pad
        self.d = Tinv(self.cam.d)            # toward the viewer, in math coordinates
        self.segs, self.dots, self.boxes, self.texts = [], [], [], []
        self.sid = 0
        self.pending = []
        self.meshes = []                     # occluders: (V0, E1, E2, eps)
        self.extra = []                      # pixel points of filled areas (for the size estimate)

    # -- projection ---------------------------------------------------------
    def px(self, P):
        X, Y = self.S.pt(P)
        return (self.p.X(X), self.p.Y(Y))

    def depth(self, P):
        return vdot(P, self.d)

    def u(self, pixels):
        return pixels / self.ppu

    def _reg(self, Ps, w=1.0):
        self._reg_px([self.px(P) for P in Ps], w)

    def _reg_px(self, q, w=1.0):
        self.sid += 1
        for a, b in zip(q, q[1:]):
            self.segs.append((a, b, w, self.sid))

    # -- visibility ---------------------------------------------------------
    def add_mesh(self, grid):
        """Register a quad grid (list of rows of space points) as an occluder."""
        G = np.array(grid, dtype=float)
        A, B, C, D = G[:-1, :-1], G[1:, :-1], G[1:, 1:], G[:-1, 1:]
        V0 = np.concatenate([A.reshape(-1, 3), A.reshape(-1, 3)])
        E1 = np.concatenate([(B - A).reshape(-1, 3), (C - A).reshape(-1, 3)])
        E2 = np.concatenate([(C - A).reshape(-1, 3), (D - A).reshape(-1, 3)])
        size = float(np.linalg.norm(G.reshape(-1, 3).max(0) - G.reshape(-1, 3).min(0)))
        self.meshes.append((V0, E1, E2, 0.012 * size))

    def hidden_many(self, Ps, eps_scale=1.0):
        Ps = np.array(Ps, dtype=float).reshape(-1, 3)
        out = np.zeros(len(Ps), dtype=bool)
        D = np.array(self.d, dtype=float)
        for V0, E1, E2, eps in self.meshes:
            pvec = np.cross(D, E2)
            det = np.einsum("ij,ij->i", E1, pvec)
            ok = np.abs(det) > 1e-12
            inv = np.where(ok, 1.0 / np.where(ok, det, 1.0), 0.0)
            for s in range(0, len(Ps), 64):
                P = Ps[s:s + 64]
                tv = P[:, None, :] - V0[None, :, :]
                uu = np.einsum("nmk,mk->nm", tv, pvec) * inv
                qv = np.cross(tv, E1[None, :, :])
                vv = np.einsum("nmk,k->nm", qv, D) * inv
                tt = np.einsum("nmk,mk->nm", qv, E2) * inv
                hit = ok & (uu >= -1e-9) & (vv >= -1e-9) & (uu + vv <= 1 + 1e-9) & (tt > eps * eps_scale)
                out[s:s + 64] |= hit.any(1)
        return out

    def hidden(self, P):
        return bool(self.hidden_many([P])[0])

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
        self.extra += [self.px(P) for P in Ps]

    def point(self, P, color=TEXT, r=4.0, opacity=1.0):
        if opacity < 1:
            self.p.add(f'<g opacity="{opacity}">')
        self.S.point(P, color, r)
        if opacity < 1:
            self.p.add('</g>')
        x, y = self.px(P)
        self.dots.append((x, y, r))

    def hollow(self, P, color=TEXT, r=3.6):
        self.S.hollow(P, color, r)
        x, y = self.px(P)
        self.dots.append((x, y, r))

    @staticmethod
    def split(Ps, flags):
        runs, cur, state = [], [Ps[0]], flags[0]
        for P, f in zip(Ps[1:], flags[1:]):
            if f != state:
                # cut in the middle of the step so both runs meet
                mid = vscale(0.5, vadd(cur[-1], P))
                runs.append((state, cur + [mid]))
                cur, state = [mid, P], f
            else:
                cur.append(P)
        runs.append((state, cur))
        return runs

    def styled(self, Ps, flags, on, off):
        """Polyline with style `on` where flags hold and `off` elsewhere (None skips)."""
        for state, run in self.split(list(Ps), list(flags)):
            st = on if state else off
            if st is not None and len(run) > 1:
                self.line(run, **st)

    def vis(self, Ps, color, on=None, off=None, w=1.0, eps_scale=1.0):
        """Draw a space polyline, visible runs with `on`, hidden runs with `off`."""
        Ps = list(Ps)
        hid = self.hidden_many(Ps, eps_scale)
        on = dict(VIS_TRACE if on is None else on)
        off = dict(HID_TRACE if off is None else off) if off is not False else None
        on.setdefault("color", color)
        on.setdefault("w", w)
        if off is not None:
            off.setdefault("color", color)
            off.setdefault("w", w * 0.5)
        self.styled(Ps, [not h for h in hid], on, off)

    def trace(self, f, t0, t1, color, n=240, **kw):
        self.vis([f(t0 + (t1 - t0) * k / n) for k in range(n + 1)], color, **kw)

    # -- surfaces -------------------------------------------------------------
    def surface(self, f, ur, vr, color=THEORY, nu=36, nv=18, fill=(0.08, 0.1), net=(12, 6),
                net_op=(0.4, 0.14), sil=True, occ=(96, 48), levels=1, occlude=True,
                light=(-0.35, -0.55, 0.76), sil_op=0.85):
        """Translucent parametric surface (u, v) -> f(u, v) over ur x vr."""
        u0, u1 = ur
        v0, v1 = vr
        grid = [[f(u0 + (u1 - u0) * i / nu, v0 + (v1 - v0) * j / nv) for j in range(nv + 1)]
                for i in range(nu + 1)]
        L = vunit(light)
        buckets = {}
        for i in range(nu):
            for j in range(nv):
                quad = (grid[i][j], grid[i + 1][j], grid[i + 1][j + 1], grid[i][j + 1])
                q = [self.px(P) for P in quad]
                area = 0.0
                for k in range(4):
                    area += q[k][0] * q[(k + 1) % 4][1] - q[(k + 1) % 4][0] * q[k][1]
                if abs(area) < 1e-6:
                    continue
                n = vcross(vsub(quad[2], quad[0]), vsub(quad[3], quad[1]))
                if vnorm(n) < 1e-12:
                    continue
                shade = 0.5 * (1.0 + abs(vdot(vunit(n), L)))
                lev = min(levels - 1, int(shade * levels))
                key = (area > 0, lev)
                buckets.setdefault(key, []).append(q)
                self.extra += q
        lo, hi = fill
        for (side, lev), quads in sorted(buckets.items()):
            op = lo + (hi - lo) * (lev + 0.5) / levels
            d = " ".join("M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in q) + " Z" for q in quads)
            self.p.add(f'<path d="{d}" fill="{color}" fill-opacity="{op:.3f}" stroke="none"/>')
        if occlude:
            ou, ov = occ
            og = [[f(u0 + (u1 - u0) * i / ou, v0 + (v1 - v0) * j / ov) for j in range(ov + 1)]
                  for i in range(ou + 1)]
            self.add_mesh(og)
        # sparse net of parameter lines
        ku, kv = net
        on = dict(width=0.75, opacity=net_op[0], w=0.15)
        off = dict(width=0.6, opacity=net_op[1], w=0.0)
        for a in range(ku + 1 if ku else 0):
            uu = u0 + (u1 - u0) * a / ku
            self.vis([f(uu, v0 + (v1 - v0) * k / 80) for k in range(81)], color, on, off)
        for b in range(kv + 1 if kv else 0):
            vv = v0 + (v1 - v0) * b / kv
            self.vis([f(u0 + (u1 - u0) * k / 120, vv) for k in range(121)], color, on, off)
        if sil:
            flat = [P for row in grid for P in row]
            size = vnorm(vsub(tuple(max(P[k] for P in flat) for k in range(3)),
                              tuple(min(P[k] for P in flat) for k in range(3))))
            self.silhouette(f, ur, vr, color, sil_op, size=size)

    def silhouette(self, f, ur, vr, color, opacity=0.85, res=(144, 72), size=1.0):
        """Contour n . d = 0 of the surface, found by marching squares in parameter space."""
        u0, u1 = ur
        v0, v1 = vr
        nu, nv = res
        hu, hv = (u1 - u0) * 1e-4, (v1 - v0) * 1e-4

        def g(u, v):
            fu = vsub(f(u + hu, v), f(u - hu, v))
            fv = vsub(f(u, v + hv), f(u, v - hv))
            n = vcross(fu, fv)
            m = vnorm(n)
            return None if m < 1e-14 else vdot(n, self.d) / m

        U = [u0 + (u1 - u0) * i / nu for i in range(nu + 1)]
        V = [v0 + (v1 - v0) * j / nv for j in range(nv + 1)]
        G = [[g(u, v) for v in V] for u in U]
        pts, adj = {}, {}

        def cross_pt(key):
            if key in pts:
                return
            kind, i, j = key
            if kind == "u":
                a, b = G[i][j], G[i + 1][j]
                t = a / (a - b)
                pts[key] = (U[i] + t * (U[i + 1] - U[i]), V[j])
            else:
                a, b = G[i][j], G[i][j + 1]
                t = a / (a - b)
                pts[key] = (U[i], V[j] + t * (V[j + 1] - V[j]))

        def link(k1, k2):
            adj.setdefault(k1, []).append(k2)
            adj.setdefault(k2, []).append(k1)

        for i in range(nu):
            for j in range(nv):
                c = (G[i][j], G[i + 1][j], G[i + 1][j + 1], G[i][j + 1])
                if any(x is None for x in c):
                    continue
                edges = [("u", i, j), ("v", i + 1, j), ("u", i, j + 1), ("v", i, j)]
                ends = [(c[0], c[1]), (c[1], c[2]), (c[3], c[2]), (c[0], c[3])]
                hits = [e for e, (a, b) in zip(edges, ends) if (a > 0) != (b > 0)]
                for e in hits:
                    cross_pt(e)
                if len(hits) == 2:
                    link(*hits)
                elif len(hits) == 4:
                    link(hits[0], hits[1])
                    link(hits[2], hits[3])
        seen = set()
        chains = []
        # open chains start at their ends, closed ones anywhere
        starts = [k for k in adj if len(adj[k]) == 1] + list(adj)
        for start in starts:
            if start in seen:
                continue
            chain, cur = [start], start
            seen.add(start)
            while True:
                nxt = [k for k in adj[cur] if k not in seen]
                if not nxt:
                    if len(chain) > 2 and start in adj[cur]:
                        chain.append(start)
                    break
                cur = nxt[0]
                seen.add(cur)
                chain.append(cur)
            if len(chain) >= 2:
                chains.append(chain)
        for chain in chains:
            P3 = [f(*pts[k]) for k in chain]
            # a rim point is visible when a ray from just beside the surface escapes
            hs = []
            for k in chain:
                u, v = pts[k]
                fu = vsub(f(u + hu, v), f(u - hu, v))
                fv = vsub(f(u, v + hv), f(u, v - hv))
                n = vunit(vcross(fu, fv))
                hs.append(n)
            dl = 0.012 * size
            plus = self.hidden_many([vadd(P, vscale(dl, n)) for P, n in zip(P3, hs)], 0.5)
            minus = self.hidden_many([vadd(P, vscale(-dl, n)) for P, n in zip(P3, hs)], 0.5)
            flags = [not (a and b) for a, b in zip(plus, minus)]
            self.styled(P3, flags, dict(color=color, width=1.3, opacity=opacity, w=1.0),
                        dict(color=color, width=1.0, dash="4 3", opacity=0.4, w=0.3))

    # -- axes -------------------------------------------------------------
    def axes(self, rng, labels=("x", "y", "z"), width=1.3, opacity=0.8, color=TEXT, head=9.0,
             neg="solid"):
        """Coordinate axes over the given (lo, hi) ranges, arrowheads at the positive ends;
        stretches behind a surface are dashed and faint."""
        E = ((1, 0, 0), (0, 1, 0), (0, 0, 1))
        vis = dict(color=color, width=width, opacity=opacity, w=1.0)
        hid = dict(color=color, width=1.0, dash="4 3", opacity=0.45, w=0.5)
        for k, (lo, hi) in enumerate(rng):
            e = E[k]
            n = 240
            if lo < 0:
                pts = [vscale(lo * (1 - j / 120), e) for j in range(121)]
                flags = [not h for h in self.hidden_many(pts)] if self.meshes else [True] * len(pts)
                self.styled(pts, flags, vis if neg == "solid" else hid, hid)
            tip = vscale(hi, e)
            pts = [vscale(hi * j / n, e) for j in range(n + 1)]
            cut = int(n * max(0.0, 1 - self.u(head * 1.4) / hi))
            flags = [not h for h in self.hidden_many(pts[:cut + 1])] if self.meshes else [True] * (cut + 1)
            self.styled(pts[:cut + 1], flags, vis, hid)
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
        """Put text s next to anchor (a space point, or ('px', x, y)); the cheapest
        candidate on a ring around it wins (earlier prefs win ties)."""
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

    # -- helpers ------------------------------------------------------------
    def rot_arrow(self, C, axis, r, a0, a1, color=TEXT, width=1.6, e1=None):
        """Circular arrow of radius r about the line through C along `axis` (angles in degrees)."""
        a = vunit(axis)
        if e1 is None:
            t = (1, 0, 0) if abs(a[0]) < 0.9 else (0, 1, 0)
            e1 = vunit(vcross(a, t))
        e2 = vcross(a, e1)
        pts = [vadd(C, vadd(vscale(r * math.cos(math.radians(a0 + (a1 - a0) * k / 60)), e1),
                            vscale(r * math.sin(math.radians(a0 + (a1 - a0) * k / 60)), e2)))
               for k in range(61)]
        self.line(pts[:-4], color, width, None, 0.95)
        self.arrow(pts[-6], pts[-1], color, width, 9.0)

    # -- output -------------------------------------------------------------
    def render(self, name, caption, aria, css=None):
        print(f"-- {name} (warnings above belong to it)")
        for t in self.texts:
            self.p.add(t)
        xs = [p[0] for s in self.segs for p in s[:2]] + [b[0] for b in self.boxes] + \
             [b[2] for b in self.boxes] + [x for x, _ in self.extra]
        ys = [p[1] for s in self.segs for p in s[:2]] + [b[1] for b in self.boxes] + \
             [b[3] for b in self.boxes] + [y for _, y in self.extra]
        ratio = (max(ys) - min(ys) + 28) / (max(xs) - min(xs) + 28)
        if css is None:
            css = WIDE if 690 * ratio <= 800 else "ders-grafik"
        OUT[name] = figure(round(self.W), round(self.H), [self.p], caption, css, aria)


def want(name):
    return not ONLY or name in ONLY


O3 = (0.0, 0.0, 0.0)


def ring(C, r, e1, e2, n=240):
    return [vadd(C, vadd(vscale(r * math.cos(TAU * k / n), e1), vscale(r * math.sin(TAU * k / n), e2)))
            for k in range(n + 1)]


EX, EY, EZ = (1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)


def sphere_f(C, r):
    e = 1e-3
    return lambda u, v: (C[0] + r * math.cos(v) * math.cos(u), C[1] + r * math.cos(v) * math.sin(u),
                         C[2] + r * math.sin(v)), (0.0, TAU), (-math.pi / 2 + e, math.pi / 2 - e)


# ============================================================ kure-merkez-yaricap
if want("kure-merkez-yaricap"):
    M, R = (-1.0, -8.0, 4.0), 9.0
    assert (M[0] ** 2 + M[1] ** 2 + M[2] ** 2) == R ** 2          # O lies on the sphere
    f = Fig(32, 18, [(-11, 0, 0), (9, 0, 0), (0, -18, 0), (0, 3, 0), (0, 0, -6), (0, 0, 14),
                     (-1, -17, 4), (-1, 1, 4), (-1, -8, 13), (-1, -8, -5)], width=560)
    sf, ur, vr = sphere_f(M, R)
    f.surface(sf, ur, vr, PRACTICE, nu=40, nv=20, net=(8, 6), net_op=(0.28, 0.1))
    f.trace(lambda t: (M[0] + R * math.cos(t), M[1] + R * math.sin(t), M[2]), 0, TAU, PRACTICE,
            on=dict(width=1.5, opacity=0.8), off=dict(width=1.1, dash="5 4", opacity=0.45))
    f.axes(((-11, 9), (-18, 3), (-6, 14)))
    top = (M[0], M[1], M[2] + R)
    f.line([M, top], PRACTICE, 2.6)
    f.guide([M, O3], TEXT, 0.75, 1.3, "5 4")
    f.point(M, TEXT, 4.4)
    f.point(top, PRACTICE, 3.8)
    f.point(O3, TEXT, 4.4)
    f.place(M, it("M") + triple(-1, -8, 4), NAME, prefs=["r", "dr", "ur"], d=8)
    f.place(vscale(0.5, vadd(M, top)), it("r") + " = 9", NAME, PRACTICE, prefs=["l", "ul", "dl"], d=7)
    f.place(O3, it("O"), NAME, prefs=["dr", "r", "d"])
    f.render(
        "kure-merkez-yaricap",
        "Merkezi <em>M</em>(−1, −8, 4) ve yarıçapı 9 olan küre. Kırmızı doğru parçası yarıçaptır; "
        "|<em>OM</em>| = 9 olduğundan başlangıç noktası <em>O</em> küre üzerindedir (kesikli <em>MO</em> "
        "parçası). Eksenlerin kürenin arkasında ya da içinde kalan kısımları kesiklidir.",
        "Translucent sphere with center M(-1, -8, 4) and radius 9, the radius from M to the top point, "
        "the origin O on the sphere joined to M by a dashed segment")

# ============================================================ helis
if want("helis"):
    f = Fig(35, 18, [(2.8, 0, 0), (-2.8, 0, 0), (0, 2.8, 0), (0, -2.8, 0), (0, 0, 7), (0, 0, -0.4)],
            width=460)
    H = 2 * math.pi
    cf = lambda u, v: (2 * math.cos(u), 2 * math.sin(u), v)          # noqa: E731
    f.surface(cf, (0, TAU), (0, H), THEORY, nu=48, nv=6, net=(12, 0), net_op=(0.22, 0.08))
    for z in (0, H):
        f.trace(lambda t, z=z: cf(t, z), 0, TAU, THEORY, on=dict(width=1.1, opacity=0.6),
                off=dict(width=0.9, dash="4 3", opacity=0.35))
    f.axes(((-2.8, 2.8), (-2.8, 2.8), (0, 7)))
    alpha = lambda t: (2 * math.cos(t), 2 * math.sin(t), t / 2)       # noqa: E731
    f.trace(alpha, 0, 4 * math.pi, PRACTICE, n=600, on=dict(width=2.6, opacity=1.0),
            off=dict(width=1.5, dash="5 4", opacity=0.6))
    ta, tb = 2 * math.pi + 0.25, 2 * math.pi + 0.55
    f.arrow(alpha(ta), alpha(tb), PRACTICE, 2.6, 11)
    for t in (0, 2 * math.pi, 4 * math.pi):
        f.point(alpha(t), TEXT, 4.2)
    f.place(alpha(0), it("α") + "(0)", NAME, prefs=["l", "dl", "ul"])
    f.place(alpha(2 * math.pi), it("α") + "(2π)", NAME, prefs=["l", "dl", "ul"])
    f.place(alpha(4 * math.pi), it("α") + "(4π)", NAME, prefs=["l", "ul", "dl"])
    f.place(alpha(math.pi * 2.9), it("α"), NAME + 1, PRACTICE, prefs=["r", "ur", "dr"], d=8)
    f.render(
        "helis",
        "Helis <em>α</em>(<em>t</em>) = (2 cos <em>t</em>, 2 sin <em>t</em>, <em>t</em>/2), "
        "<em>t</em> ∈ [0, 4π], <em>x</em>² + <em>y</em>² = 4 silindirinin üzerinde iki tur atarak "
        "yükselir; ok, <em>t</em> artarken hareket yönünü gösterir. <em>α</em>(0), <em>α</em>(2π) ve "
        "<em>α</em>(4π) aynı düşey doğru üzerindedir; eğrinin silindirin arkasında kalan kısımları "
        "kesiklidir.",
        "Helix alpha(t) = (2 cos t, 2 sin t, t/2) for t from 0 to 4 pi winding twice around the faint "
        "cylinder x^2 + y^2 = 4, with the points alpha(0), alpha(2 pi), alpha(4 pi) on one vertical line")

# ============================================================ dairesel-silindir
if want("dairesel-silindir"):
    f = Fig(35, 20, [(3, 0, 0), (-3, 0, 0), (0, 3, 0), (0, -3, 0), (0, 0, 4), (0, 0, -1)], width=520)
    cf = lambda u, v: (2 * math.cos(u), 2 * math.sin(u), v)          # noqa: E731
    f.surface(cf, (0, TAU), (0, 3), THEORY, nu=48, nv=6, net=(8, 0), net_op=(0.4, 0.14))
    f.trace(lambda t: cf(t, 3), 0, TAU, THEORY, on=dict(width=1.3, opacity=0.75),
            off=dict(width=1.0, dash="4 3", opacity=0.4))
    f.axes(((-3, 3), (-3, 3), (-1, 4)))
    f.trace(lambda t: cf(t, 0), 0, TAU, PRACTICE)
    ug = math.radians(80)
    f.vis([cf(ug, 0), cf(ug, 3)], THEORY, on=dict(width=2.4, opacity=1.0))
    R0, P0 = (2.0, 0.0, 0.0), (2.0, 0.0, 2.0)
    f.arrow(R0, P0, BASE, 2.6, 11)
    f.point(R0, TEXT, 4.2)
    f.point(P0, TEXT, 4.2)
    V0 = (-1.2, 3.1, 1.0)
    f.arrow(V0, vadd(V0, (0, 0, 1.2)), TEXT, 2.0, 10)
    f.place(R0, it("R"), NAME, prefs=["dl", "l", "d"])
    f.place(P0, it("P"), NAME, prefs=["l", "ul", "dl"])
    f.place(vscale(0.5, vadd(R0, P0)), "λ" + it("v"), NAME, BASE, prefs=["l", "dl", "ul"], d=6)
    f.place(cf(ug, 2.2), "üreteç", DESC, THEORY, prefs=["r", "ur", "dr"], d=8)
    f.place(vadd(V0, (0, 0, 0.6)), it("v") + " = (0, 0, 1)", DESC, TEXT, prefs=["r", "l"], d=8)
    f.place(cf(math.radians(10), 0), "Γ: " + eq("x² + y² = 4, z = 0"), DESC, PRACTICE,
            prefs=["d", "dr", "dl"], d=8, leader=True)
    f.render(
        "dairesel-silindir",
        "Dayanak eğrisi <em>xy</em>-düzlemindeki Γ: <em>x</em>² + <em>y</em>² = 4 çemberi (kırmızı) olan "
        "ve üreteçleri <em>v</em> = (0, 0, 1) doğrultusunda olan dik dairesel silindir "
        "(0 ≤ <em>z</em> ≤ 3 parçası). <em>P</em> = <em>R</em> + λ<em>v</em> noktası, Γ üzerindeki "
        "<em>R</em>(2, 0, 0) noktasından geçen üreteçtedir.",
        "Right circular cylinder x^2 + y^2 = 4 between z = 0 and z = 3 with the base circle Gamma in "
        "the xy plane, vertical generators, one of them bold, and the arrow from R(2, 0, 0) to "
        "P(2, 0, 2) labelled lambda v")

# ============================================================ silindir-tanimi
if want("silindir-tanimi"):
    gam = lambda t: (1.9 * math.cos(t) + 0.25 * math.cos(2 * t),               # noqa: E731
                     1.25 * math.sin(t) - 0.35 * math.cos(2 * t) + 0.2, 0.0)
    v = (-0.3, 1.2, 2.2)
    f = Fig(35, 24, [(-3, -2.6, 0), (3, 2.6, 0), (-3, 2.6, 0), (3, -2.6, 0), (2.5, 1.6, 2.6),
                     (0, 4.4, 2.9), (-1, 4.4, 0)], width=560)
    f.polygon([(-2.8, -2.4, 0), (2.9, -2.4, 0), (2.9, 2.4, 0), (-2.8, 2.4, 0)], TEXT, 0.05)
    f.line([(-2.8, -2.4, 0), (2.9, -2.4, 0), (2.9, 2.4, 0), (-2.8, 2.4, 0), (-2.8, -2.4, 0)],
           TEXT, 0.9, None, 0.3, w=0.3)
    sf = lambda t, lam: vadd(gam(t), vscale(lam, v))                           # noqa: E731
    f.surface(sf, (0, TAU), (0, 1), THEORY, nu=64, nv=6, net=(10, 0), net_op=(0.55, 0.2))
    f.trace(lambda t: sf(t, 1), 0, TAU, THEORY, on=dict(width=1.2, opacity=0.6),
            off=dict(width=1.0, dash="4 3", opacity=0.35))
    f.trace(gam, 0, TAU, PRACTICE)
    tb = math.radians(-20)
    f.vis([sf(tb, 0), sf(tb, 1)], THEORY, on=dict(width=2.6, opacity=1.0))
    tr = math.radians(-110)
    R0, P0 = gam(tr), sf(tr, 0.62)
    f.arrow(R0, P0, BASE, 2.6, 11)
    f.point(R0, TEXT, 4.2)
    f.point(P0, TEXT, 4.2)
    Q0 = (-0.6, 3.7, 0.2)
    f.line([vadd(Q0, vscale(-0.08, v)), vadd(Q0, vscale(1.12, v))], TEXT, 1.4, None, 0.85)
    f.arrow(vadd(Q0, vscale(0.3, v)), vadd(Q0, vscale(0.72, v)), TEXT, 2.6, 11)
    f.place(vadd(Q0, vscale(1.08, v)), "Δ", NAME + 1, prefs=["r", "ur", "l"], d=7)
    f.place(vadd(Q0, vscale(0.5, v)), it("v") + " = (" + it("a") + ", " + it("b") + ", " + it("c") + ")",
            DESC, prefs=["r", "dr", "ur"], d=8)
    f.place(gam(math.radians(60)), "Γ", NAME + 1, PRACTICE, prefs=["u", "ur", "ul"], d=7)
    f.place(sf(tb, 0.55), "üreteç", DESC, THEORY, prefs=["r", "dr", "ur"], d=8)
    f.place(R0, it("R"), NAME, prefs=["d", "dl", "dr"])
    f.place(P0, it("P"), NAME, prefs=["l", "ul", "u"])
    f.place(vscale(0.5, vadd(R0, P0)), "λ" + it("v"), NAME, BASE, prefs=["l", "dl", "ul"], d=6)
    f.render(
        "silindir-tanimi",
        "Silindir: dayanak eğrisi Γ (kırmızı) boyunca kayan ve Δ doğrusuna (doğrultman vektörü "
        "<em>v</em>) paralel kalan doğrular, yani üreteçler yüzeyi örer. Γ üzerindeki <em>R</em> "
        "noktasının üretecindeki her <em>P</em> noktası için <em>RP</em> = λ<em>v</em> olur.",
        "A cylinder over a closed bean shaped curve Gamma in a horizontal plane: parallel generators "
        "in the direction of the line Delta with direction vector v, one generator bold, a point R on "
        "Gamma and a point P on its generator with the arrow lambda v")

# ============================================================ egik-silindir
if want("egik-silindir"):
    f = Fig(35, 20, [(-1.5, 0, 0), (4, 0, 0), (0, -1.8, 0), (0, 1.8, 0), (0, 0, -0.5), (0, 0, 2.8),
                     (3, 1, 2), (3, -1, 2)], width=560)
    ef = lambda u, z: (math.cos(u) + z, math.sin(u), z)                        # noqa: E731
    f.surface(ef, (0, TAU), (0, 2), THEORY, nu=48, nv=6, net=(8, 0), net_op=(0.45, 0.16))
    for z, st in ((1, dict(width=1.1, opacity=0.55)), (2, dict(width=1.4, opacity=0.8))):
        f.trace(lambda t, z=z: ef(t, z), 0, TAU, THEORY, on=st, off=dict(width=1.0, dash="4 3", opacity=0.35))
    f.axes(((-1.5, 4), (-1.8, 1.8), (-0.5, 2.8)))
    f.guide([(0, 0, 0), (2, 0, 2)], TEXT, 0.6, 1.1, "6 4")
    f.trace(lambda t: ef(t, 0), 0, TAU, PRACTICE)
    f.vis([ef(0, 0), ef(0, 2)], THEORY, on=dict(width=2.6, opacity=1.0))
    Pk = (2.0, 0.0, 1.0)
    f.point((1.0, 0.0, 0.0), TEXT, 3.8)
    f.point(Pk, TEXT, 4.4)
    for c in ((1, 0, 1), (2, 0, 2)):
        f.point(c, TEXT, 2.8, opacity=0.7)
    V0 = (-0.6, 2.5, 0.8)
    f.arrow(V0, vadd(V0, (0.9, 0, 0.9)), TEXT, 2.2, 10)
    f.place(Pk, triple(2, 0, 1), NAME, prefs=["dr", "r", "ur"], d=8)
    f.place((1.0, 0.0, 0.0), triple(1, 0, 0), DESC, prefs=["dl", "d", "l"], d=6)
    f.place(ef(math.radians(-60), 0), "Γ", NAME + 1, PRACTICE, prefs=["d", "dl", "dr"], d=7)
    f.place(vadd(V0, (0.45, 0, 0.45)), it("v") + " = (1, 0, 1)", DESC, prefs=["r", "l", "dr"], d=9)
    f.render(
        "egik-silindir",
        "Eğik silindir (<em>x</em> − <em>z</em>)² + <em>y</em>² = 1, 0 ≤ <em>z</em> ≤ 2. Dayanak "
        "çemberi Γ (kırmızı) <em>xy</em>-düzlemindedir; <em>z</em> = 1 ve <em>z</em> = 2 kesitleri "
        "merkezleri (1, 0, 1) ve (2, 0, 2) olan birim çemberlerdir. Kalın üreteç (1, 0, 0)&#8217;dan "
        "<em>v</em> = (1, 0, 1) doğrultusunda çıkar ve (2, 0, 1) noktasından geçer.",
        "Oblique cylinder (x - z)^2 + y^2 = 1 for z from 0 to 2 with its base circle Gamma, the "
        "circles at z = 1 and z = 2, the dashed line of centers and the bold generator from (1, 0, 0) "
        "through (2, 0, 1)")

# ============================================================ eliptik-silindir
if want("eliptik-silindir"):
    f = Fig(35, 20, [(-3, 0, 0), (3, 0, 0), (0, -1.8, 0), (0, 1.8, 0), (0, 0, -1.5), (0, 0, 2.5),
                     (0, 0, -1), (2, 1, 2)], width=560)
    lf = lambda u, z: (2 * math.cos(u), math.sin(u), z)                        # noqa: E731
    f.surface(lf, (0, TAU), (-1, 2), THEORY, nu=48, nv=6, net=(8, 0), net_op=(0.45, 0.16))
    for z in (-1, 2):
        f.trace(lambda t, z=z: lf(t, z), 0, TAU, THEORY, on=dict(width=1.3, opacity=0.75),
                off=dict(width=1.0, dash="4 3", opacity=0.4))
    f.axes(((-3, 3), (-1.8, 1.8), (-1.5, 2.5)))
    f.trace(lambda t: lf(t, 0), 0, TAU, PRACTICE)
    for Q in ((2, 0, 0), (-2, 0, 0), (0, 1, 0), (0, -1, 0)):
        f.point(Q, TEXT, 3.8, opacity=0.6 if f.hidden(Q) else 1.0)
    f.place((2, 0, 0), triple(2, 0, 0), DESC, prefs=["dl", "l", "d"], d=6)
    f.place((0, 1, 0), triple(0, 1, 0), DESC, prefs=["dr", "r", "d"], d=6)
    f.place(lf(math.radians(-100), 0), eq("x²/4 + y² = 1"), DESC, PRACTICE, prefs=["r", "dr", "ur"],
            d=10, leader=True)
    f.render(
        "eliptik-silindir",
        "Eliptik silindir <em>x</em>²/4 + <em>y</em>² = 1 (−1 ≤ <em>z</em> ≤ 2 parçası). Her "
        "<em>z</em> = <em>k</em> düzlemi yüzeyi aynı elips boyunca keser; kırmızı elips "
        "<em>xy</em>-düzlemindeki dayanak eğrisidir ve eksenleri (±2, 0, 0) ile (0, ±1, 0) "
        "noktalarında keser.",
        "Elliptic cylinder x^2/4 + y^2 = 1 for z from -1 to 2 with vertical generators, the ellipse in "
        "the xy plane bold and its axis points (2, 0, 0) and (0, 1, 0) labelled")

# ============================================================ parabolik-silindir
if want("parabolik-silindir"):
    f = Fig(24, 18, [(-2.5, 0, 0), (2.5, 0, 0), (0, -2, 0), (0, 2, 0), (0, 0, -0.5), (0, 0, 4),
                     (2, 1.8, 3.24), (-2, -1.8, 3.24)], width=560)
    pf = lambda x, y: (x, y, y * y)                                            # noqa: E731
    f.surface(pf, (-2, 2), (-1.8, 1.8), THEORY, nu=16, nv=36, net=(0, 8), net_op=(0.45, 0.16))
    for x in (-2, 2):
        f.trace(lambda t, x=x: pf(x, t), -1.8, 1.8, THEORY, on=dict(width=1.3, opacity=0.75),
                off=dict(width=1.0, dash="4 3", opacity=0.4))
    f.axes(((-2.5, 2.5), (-2, 2), (-0.5, 4)))
    f.trace(lambda t: pf(0, t), -1.8, 1.8, PRACTICE)
    yb = 1.35
    f.vis([pf(-2, yb), pf(2, yb)], THEORY, on=dict(width=2.6, opacity=1.0))
    V0 = (-1.0, 2.2, 3.2)
    f.arrow(V0, vadd(V0, (1.2, 0, 0)), TEXT, 2.2, 10)
    f.place(pf(0, -1.55), "Γ: " + eq("z = y², x = 0"), DESC, PRACTICE, prefs=["l", "ul", "dl"], d=10,
            leader=True)
    f.place(pf(1.2, yb), "üreteç", DESC, THEORY, prefs=["dr", "d", "r"], d=7)
    f.place(vadd(V0, (0.6, 0, 0)), it("v") + " = (1, 0, 0)", DESC, prefs=["u", "d"], d=8)
    f.render(
        "parabolik-silindir",
        "Parabolik silindir <em>z</em> = <em>y</em>² (−2 ≤ <em>x</em> ≤ 2 parçası): <em>yz</em>-düzlemindeki "
        "Γ parabolü (kırmızı) <em>x</em>-ekseni doğrultusunda kaydırılır; üreteçler "
        "<em>v</em> = (1, 0, 0)&#8217;a paraleldir.",
        "Parabolic cylinder z = y^2 for x from -2 to 2 shaped like a trough: the parabola Gamma in the "
        "yz plane bold, its copies at x = -2 and x = 2, generators parallel to the x axis, one bold")

# ============================================================ koni-tanimi
if want("koni-tanimi"):
    gam = lambda t: (1.8 * math.cos(t) + 0.3 * math.cos(2 * t),               # noqa: E731
                     1.3 * math.sin(t) + 0.15 * math.sin(2 * t), 0.0)
    T = (0.35, 0.25, 2.7)
    f = Fig(35, 22, [(-2.8, -2.4, 0), (2.9, 2.4, 0), (-2.8, 2.4, 0), (2.9, -2.4, 0), (0.6, 0.4, 3.8)],
            width=540)
    f.polygon([(-2.8, -2.4, 0), (2.9, -2.4, 0), (2.9, 2.4, 0), (-2.8, 2.4, 0)], TEXT, 0.05)
    f.line([(-2.8, -2.4, 0), (2.9, -2.4, 0), (2.9, 2.4, 0), (-2.8, 2.4, 0), (-2.8, -2.4, 0)],
           TEXT, 0.9, None, 0.3, w=0.3)
    kf = lambda t, lam: vadd(vscale(1 - lam, gam(t)), vscale(lam, T))          # noqa: E731
    f.surface(kf, (0, TAU), (0, 0.999), THEORY, nu=64, nv=8, net=(0, 0), net_op=(0.5, 0.18))
    f.surface(kf, (0, TAU), (1.001, 1.4), THEORY, nu=64, nv=3, net=(0, 0), fill=(0.04, 0.04),
              sil_op=0.4)
    for k in range(10):
        t = TAU * k / 10
        f.vis([kf(t, j / 40 * 1.4) for j in range(41)], THEORY, on=dict(width=0.8, opacity=0.5, w=0.15),
              off=dict(width=0.6, opacity=0.18, w=0.0))
    f.trace(gam, 0, TAU, PRACTICE)
    tr = math.radians(-75)
    R0 = gam(tr)
    P0 = kf(tr, 0.5)
    f.vis([kf(tr, j / 40 * 1.4) for j in range(41)], THEORY, on=dict(width=2.4, opacity=1.0))
    f.arrow(R0, vadd(R0, vscale(0.97, vsub(T, R0))), TEXT, 1.3, 8)
    f.arrow(R0, P0, BASE, 3.0, 12)
    for Q in (R0, P0, T):
        f.point(Q, TEXT, 4.2)
    f.place(T, it("T") + "(" + it("x") + sub("0") + ", " + it("y") + sub("0") + ", " + it("z") + sub("0") + ")",
            NAME, prefs=["l", "ul", "r"], d=10)
    f.place(gam(math.radians(55)), "Γ", NAME + 1, PRACTICE, prefs=["ur", "u", "r"], d=7)
    f.place(kf(math.radians(-150), 0.72), "üreteç", DESC, THEORY, prefs=["l", "ul", "dl"], d=8)
    f.place(R0, it("R"), NAME, prefs=["d", "dl", "dr"])
    f.place(P0, it("P"), NAME, prefs=["r", "ur", "dr"], d=8)
    f.place(kf(tr, 0.25), it("RP"), NAME, BASE, prefs=["r", "dr", "ur"], d=8, vec=True)
    f.place(kf(tr, 0.75), it("RT"), NAME, TEXT, prefs=["r", "ur", "dr"], d=8, vec=True)
    f.render(
        "koni-tanimi",
        "Koni: dayanak eğrisi Γ (kırmızı) üzerindeki her noktayı <em>T</em> tepe noktasına birleştiren "
        "doğrular (üreteçler) yüzeyi örer; üreteçler <em>T</em>&#8217;nin ötesine uzanarak öbür kanadı "
        "(soluk) oluşturur. <em>R</em> ∈ Γ ve <em>P</em>, <em>RT</em> üreteci üzerindeyken "
        "<em>RP</em> = λ<em>RT</em> olur.",
        "A cone over a closed egg shaped curve Gamma in a horizontal plane with vertex T above the "
        "plane: generators through T extended a little beyond it, one bold with the points R on Gamma "
        "and P between R and T, the vectors RP and RT")

# ============================================================ dik-dairesel-koni
if want("dik-dairesel-koni"):
    f = Fig(35, 18, [(-1.8, 0, 0), (1.8, 0, 0), (0, -1.8, 0), (0, 1.8, 0), (0, 0, -0.5), (0, 0, 4.5),
                     (1, 1, 4), (-1, -1, 4), (1, -1, 0), (-1, 1, 0)], width=500)
    cf = lambda u, z: ((2 - z) / 2 * math.cos(u), (2 - z) / 2 * math.sin(u), z)   # noqa: E731
    f.surface(cf, (0, TAU), (0, 1.995), THEORY, nu=48, nv=8, net=(0, 0))
    f.surface(cf, (0, TAU), (2.005, 4), THEORY, nu=48, nv=8, net=(0, 0), fill=(0.05, 0.05), sil_op=0.6)
    for k in range(8):
        u = TAU * k / 8 + 0.2
        f.vis([cf(u, 4 * j / 80) for j in range(81)], THEORY, on=dict(width=0.8, opacity=0.5, w=0.15),
              off=dict(width=0.6, opacity=0.18, w=0.0))
    f.trace(lambda t: cf(t, 4), 0, TAU, THEORY, on=dict(width=1.2, opacity=0.7),
            off=dict(width=1.0, dash="4 3", opacity=0.4))
    f.trace(lambda t: cf(t, 1), 0, TAU, THEORY, on=dict(width=1.1, dash="4 3", opacity=0.6),
            off=dict(width=0.9, dash="3 3", opacity=0.3))
    f.axes(((-1.8, 1.8), (-1.8, 1.8), (-0.5, 4.5)))
    f.trace(lambda t: cf(t, 0), 0, TAU, PRACTICE)
    ub = math.radians(70)
    f.vis([cf(ub, 4 * j / 80) for j in range(81)], THEORY, on=dict(width=2.4, opacity=1.0))
    T = (0.0, 0.0, 2.0)
    f.point(T, TEXT, 4.4)
    f.place(T, it("T") + triple(0, 0, 2), NAME, prefs=["l", "ul", "dl"], d=10)
    f.place(cf(math.radians(-60), 0), "Γ: " + eq("x² + y² = 1"), DESC, PRACTICE, prefs=["d", "dl", "dr"],
            d=9, leader=True)
    f.render(
        "dik-dairesel-koni",
        "Dik dairesel koni 4<em>x</em>² + 4<em>y</em>² = (2 − <em>z</em>)², 0 ≤ <em>z</em> ≤ 4. "
        "Üreteçler dayanak çemberi Γ&#8217;dan (kırmızı) <em>T</em>(0, 0, 2) tepe noktasından geçerek "
        "üst kanada uzanır; kesikli ara çember <em>z</em> = 1 kesitidir (yarıçap 1/2).",
        "Double right circular cone 4x^2 + 4y^2 = (2 - z)^2 for z from 0 to 4 with vertex T(0, 0, 2), "
        "base circle Gamma of radius 1 in the xy plane, the top circle at z = 4 and the dashed circle "
        "of radius 1/2 at z = 1")

# ============================================================ koni-elips
if want("koni-elips"):
    f = Fig(58, 18, [(-3, 0, 0), (3.2, 0, 0), (0, -1.8, 0), (0, 1.8, 0), (0, 0, -2.6), (0, 0, 3.1),
                     (2.3, 1.15, 2.3), (-2, -1, -2)], width=600)
    kf = lambda u, t: (2 * t * math.cos(u), t * math.sin(u), 2 * t)           # noqa: E731
    f.surface(kf, (0, TAU), (0.004, 1.15), THEORY, nu=48, nv=6, net=(0, 0))
    f.surface(kf, (0, TAU), (-1.0, -0.004), THEORY, nu=48, nv=6, net=(0, 0))
    for k in range(8):
        u = TAU * k / 8 + 0.3
        f.vis([kf(u, -1.0 + 2.15 * j / 80) for j in range(81)], THEORY,
              on=dict(width=0.8, opacity=0.5, w=0.15), off=dict(width=0.6, opacity=0.18, w=0.0))
    f.trace(lambda s: kf(s, 1.15), 0, TAU, THEORY, on=dict(width=1.1, opacity=0.6),
            off=dict(width=0.9, dash="4 3", opacity=0.35))
    f.trace(lambda s: kf(s, -1), 0, TAU, THEORY, on=dict(width=1.3, opacity=0.8),
            off=dict(width=1.0, dash="4 3", opacity=0.4))
    f.axes(((-3, 3.2), (-1.8, 1.8), (-2.6, 3.1)))
    f.trace(lambda s: kf(s, 1), 0, TAU, PRACTICE)
    ub = math.radians(75)
    f.vis([kf(ub, -1.0 + 2.15 * j / 80) for j in range(81)], THEORY, on=dict(width=2.4, opacity=1.0))
    f.point(O3, TEXT, 4.4)
    f.point((0, 0, 2), TEXT, 3.0, opacity=0.7)
    f.place(O3, it("T") + " = " + it("O"), NAME, prefs=["r", "dr", "l"], d=9)
    f.place(kf(math.radians(-40), 1), "Γ", NAME + 1, PRACTICE, prefs=["dl", "l", "d"], d=7)
    f.place((0, 0, 2), it("z") + " = " + it("c"), DESC, prefs=["l", "ul"], d=10)
    f.render(
        "koni-elips",
        "<em>a</em> = 2, <em>b</em> = 1, <em>c</em> = 2 için tepe noktası başlangıç noktası olan eliptik "
        "koni <em>x</em>²/4 + <em>y</em>² = <em>z</em>²/4. Dayanak elipsi Γ (kırmızı) <em>z</em> = "
        "<em>c</em> düzlemindedir; üreteçler <em>O</em>&#8217;dan geçip alt kanada uzanır, alt "
        "kanattaki elips <em>z</em> = −2 kesitidir.",
        "Elliptic cone x^2/4 + y^2 = z^2/4 with vertex at the origin for z from -2.5 to 2.5: the ellipse "
        "Gamma in the plane z = 2, generators through O, one bold, and the section at z = -2")

# ============================================================ donel-yuzey-tanimi
if want("donel-yuzey-tanimi"):
    g = lambda x: 1 + 0.4 * math.sin(1.5 * x)                                  # noqa: E731
    f = Fig(62, 22, [(-2.8, 0, 0), (3.4, 0, 0), (0, -2, 0), (0, 2, 0), (0, 0, -2), (0, 0, 2)],
            width=580)
    rf = lambda x, th: (x, g(x) * math.cos(th), g(x) * math.sin(th))          # noqa: E731
    f.surface(rf, (-2, 2), (0, TAU), THEORY, nu=40, nv=48, net=(0, 6), net_op=(0.35, 0.12))
    for x in (-2, 2):
        f.trace(lambda t, x=x: rf(x, t), 0, TAU, THEORY, on=dict(width=1.1, opacity=0.6),
                off=dict(width=0.9, dash="4 3", opacity=0.35))
    f.axes(((-2.8, 3.4), (-2, 2), (-2, 2)))
    f.trace(lambda x: rf(x, 0), -2, 2, PRACTICE)
    x0 = 0.8
    y0 = g(x0)
    f.trace(lambda t: rf(x0, t), 0, TAU, BASE, on=dict(width=2.0, opacity=1.0),
            off=dict(width=1.4, dash="5 4", opacity=0.7))
    Cq, Q, P = (x0, 0.0, 0.0), rf(x0, 0), rf(x0, math.radians(62))
    f.line([Cq, Q], BASE, 1.4, "4 3", 0.9)
    f.line([Cq, P], BASE, 1.4, "4 3", 0.9)
    f.rot_arrow((2.75, 0, 0), EX, 0.45, 200, 470, TEXT, 1.6, e1=EY)
    f.point(Cq, TEXT, 3.0)
    f.point(Q, TEXT, 4.2)
    f.point(P, TEXT, 4.2)
    f.place(Q, it("Q"), NAME, prefs=["dr", "r", "d"], d=6)
    f.place(P, it("P"), NAME, prefs=["ul", "u", "l"], d=6)
    f.place(rf(-1.3, 0), "Γ", NAME + 1, PRACTICE, prefs=["d", "dl", "dr"], d=7)
    f.place((3.0, 0, 0), "Δ", NAME + 1, TEXT, prefs=["d", "u", "dl"], d=8)
    f.render(
        "donel-yuzey-tanimi",
        "Dönel yüzey: <em>xy</em>-düzlemindeki Γ eğrisi (kırmızı) Δ = <em>x</em>-ekseni etrafında "
        "döndürülür. Γ&#8217;nın her <em>Q</em> noktası, merkezi eksen üzerinde olan ve eksene dik bir "
        "düzlemde kalan bir çember (yeşil) çizer; bu çemberin <em>P</em> noktalarının eksene uzaklığı "
        "<em>Q</em>&#8217;nunkine eşittir.",
        "Surface of revolution of a wavy curve Gamma in the xy plane about the x axis Delta: the circle "
        "traced by a point Q of Gamma in the plane x = x0, a point P on it and a curved arrow showing "
        "the rotation")

# ============================================================ elips-x-ekseni
if want("elips-x-ekseni"):
    f = Fig(-62, 20, [(-2.5, 0, 0), (3.1, 0, 0), (0, -1.6, 0), (0, 1.8, 0), (0, 0, -1.6), (0, 0, 1.8)],
            width=580)
    e = 1e-3
    ef = lambda t, th: (2 * math.cos(t), math.sin(t) * math.cos(th), math.sin(t) * math.sin(th))  # noqa: E731
    f.surface(ef, (e, math.pi - e), (0, TAU), THEORY, nu=36, nv=48, net=(0, 0))
    for xx in (-1, 1):
        f.trace(lambda s, xx=xx: (xx, math.sqrt(3) / 2 * math.cos(s), math.sqrt(3) / 2 * math.sin(s)),
                0, TAU, THEORY, on=dict(width=1.0, opacity=0.55), off=dict(width=0.9, dash="4 3", opacity=0.3))
    f.axes(((-2.5, 3.1), (-1.6, 1.8), (-1.6, 1.8)))
    f.trace(lambda s: (0, math.cos(s), math.sin(s)), 0, TAU, BASE, on=dict(width=2.0, opacity=1.0))
    f.trace(lambda s: (2 * math.cos(s), math.sin(s), 0), 0, TAU, PRACTICE)
    f.rot_arrow((2.6, 0, 0), EX, 0.4, 200, 470, TEXT, 1.6, e1=EY)
    for Q in ((2, 0, 0), (-2, 0, 0), (0, 1, 0), (0, 0, 1)):
        f.point(Q, TEXT, 3.8)
    f.place((2, 0, 0), "(" + it("a") + ", 0, 0)", DESC, prefs=["dr", "d", "ur"], d=7)
    f.place((-2, 0, 0), "(−" + it("a") + ", 0, 0)", DESC, prefs=["dl", "ul", "d"], d=7, leader=True)
    f.place((0, 1, 0), "(0, " + it("b") + ", 0)", DESC, prefs=["ur", "r", "u"], d=7)
    f.place((0, 0, 1), "(0, 0, " + it("b") + ")", DESC, prefs=["ur", "ul", "u"], d=7, leader=True)
    f.place((2 * math.cos(2.3), math.sin(2.3), 0), "Γ", NAME + 1, PRACTICE, prefs=["dl", "d", "l"], d=7)
    f.render(
        "elips-x-ekseni",
        "<em>a</em> = 2, <em>b</em> = 1 için <em>x</em>²/4 + <em>y</em>² = 1 elipsi Γ&#8217;nın (kırmızı) "
        "<em>x</em>-ekseni etrafında döndürülmesiyle oluşan dönel elipsoid <em>x</em>²/4 + <em>y</em>² + "
        "<em>z</em>² = 1. Yeşil çember <em>x</em> = 0 kesitidir; <em>x</em> = ±1 kesitleri yarıçapı "
        "√3/2 olan çemberlerdir.",
        "Prolate spheroid x^2/4 + y^2 + z^2 = 1 obtained by rotating the ellipse Gamma in the xy plane "
        "about the x axis: the unit circle at x = 0, smaller circles at x = 1 and x = -1, the points "
        "(a, 0, 0), (-a, 0, 0), (0, b, 0), (0, 0, b) and a curved arrow around the x axis")

# ============================================================ donel-elipsoid
if want("donel-elipsoid"):
    a, b = 1 / math.sqrt(2), 0.5
    f = Fig(-62, 20, [(-1, 0, 0), (1.15, 0, 0), (0, -0.8, 0), (0, 0.95, 0), (0, 0, -0.8), (0, 0, 0.95)],
            width=580)
    e = 1e-3
    ef = lambda t, th: (a * math.cos(t), b * math.sin(t) * math.cos(th), b * math.sin(t) * math.sin(th))  # noqa: E731
    f.surface(ef, (e, math.pi - e), (0, TAU), THEORY, nu=36, nv=48, net=(0, 0))
    f.axes(((-1, 1.15), (-0.8, 0.95), (-0.8, 0.95)))
    f.trace(lambda s: (0, b * math.cos(s), b * math.sin(s)), 0, TAU, THEORY, on=dict(width=2.2, opacity=1.0))
    f.trace(lambda s: (a * math.cos(s), 0, b * math.sin(s)), 0, TAU, BASE)
    f.trace(lambda s: (a * math.cos(s), b * math.sin(s), 0), 0, TAU, PRACTICE)
    for Q in ((a, 0, 0), (-a, 0, 0), (0, b, 0), (0, 0, b)):
        f.point(Q, TEXT, 3.8)
    f.place((a, 0, 0), "1/√2", DESC, prefs=["dr", "d", "ur"], d=7)
    f.place((-a, 0, 0), "−1/√2", DESC, prefs=["dl", "ul", "l"], d=7, leader=True)
    f.place((0, b, 0), "1/2", DESC, prefs=["ur", "u", "r"], d=6)
    f.place((0, 0, b), "1/2", DESC, prefs=["ul", "ur", "u"], d=6, leader=True)
    f.place((a * math.cos(2.2), b * math.sin(2.2), 0), eq("2x² + 4y² = 1"), DESC, PRACTICE,
            prefs=["ul", "u", "l"], d=12, leader=True)
    f.render(
        "donel-elipsoid",
        "Dönel elipsoid 2<em>x</em>² + 4<em>y</em>² + 4<em>z</em>² = 1: <em>xy</em>-düzlemindeki iz "
        "2<em>x</em>² + 4<em>y</em>² = 1 elipsi (kırmızı, üreteç), <em>xz</em>-düzlemindeki iz "
        "2<em>x</em>² + 4<em>z</em>² = 1 elipsi (yeşil), <em>yz</em>-düzlemindeki iz yarıçapı 1/2 olan "
        "çember (mavi). Yüzey <em>x</em>-ekseni boyunca ±1/√2&#8217;ye uzanır.",
        "Spheroid 2x^2 + 4y^2 + 4z^2 = 1 elongated along the x axis with its traces in the three "
        "coordinate planes and the axis points 1/root 2, -1/root 2 and 1/2")

# ============================================================ hiperbol-y-ekseni
if want("hiperbol-y-ekseni"):
    S = math.asinh(2)
    f = Fig(35, 18, [(-2.8, 0, 0), (2.8, 0, 0), (0, -2.4, 0), (0, 2.9, 0), (0, 0, -2.8), (0, 0, 2.8),
                     (2.3, 2, 0), (-2.3, -2, 0), (0, 2, 2.3), (0, -2, -2.3)], width=560, up="y")
    hf = lambda th, s: (math.cosh(s) * math.cos(th), math.sinh(s), math.cosh(s) * math.sin(th))   # noqa: E731
    f.surface(hf, (0, TAU), (-S, S), THEORY, nu=48, nv=24, net=(8, 0))
    for s in (-S, S):
        f.trace(lambda t, s=s: hf(t, s), 0, TAU, THEORY, on=dict(width=1.2, opacity=0.7),
                off=dict(width=1.0, dash="4 3", opacity=0.4))
    f.axes(((-2.8, 2.8), (-2.4, 2.9), (-2.8, 2.8)))
    f.trace(lambda t: hf(0, t), -S, S, PRACTICE)
    f.trace(lambda t: hf(math.pi, t), -S, S, PRACTICE)
    f.trace(lambda t: hf(t, 0), 0, TAU, BASE, on=dict(width=2.2, opacity=1.0))
    f.rot_arrow((0, 2.45, 0), EY, 0.5, 200, 470, TEXT, 1.6, e1=EZ)
    f.place(hf(0, -1.05), "Γ", NAME + 1, PRACTICE, prefs=["r", "dr", "ur"], d=8)
    f.place(hf(math.radians(-60), 0), "bel çemberi", DESC, BASE, prefs=["dr", "r", "d"], d=10, leader=True)
    f.render(
        "hiperbol-y-ekseni",
        "<em>a</em> = <em>b</em> = 1 için <em>x</em>² − <em>y</em>² = 1 hiperbolünün (kırmızı, Γ) "
        "<em>y</em>-ekseni etrafında döndürülmesiyle oluşan tek kanatlı hiperboloid "
        "<em>x</em>² − <em>y</em>² + <em>z</em>² = 1, −2 ≤ <em>y</em> ≤ 2. Yeşil çember <em>y</em> = 0&#8217;daki "
        "bel çemberidir; uçlardaki çemberlerin yarıçapı √5&#8217;tir.",
        "One sheeted hyperboloid of revolution x^2 - y^2 + z^2 = 1 with the y axis drawn vertically: "
        "the two branches of the hyperbola Gamma in the xy plane, the waist circle at y = 0, the end "
        "circles at y = 2 and y = -2 and a curved arrow around the y axis")

# ============================================================ tek-kanatli-donel
if want("tek-kanatli-donel"):
    S = math.asinh(2.4)                      # y = sinh(s)/2 reaches 1.2
    f = Fig(35, 18, [(-2.2, 0, 0), (2.2, 0, 0), (0, -1.5, 0), (0, 1.65, 0), (0, 0, -2.2), (0, 0, 2.2),
                     (1.85, 1.2, 0), (-1.85, -1.2, 0), (0, 1.2, 1.85), (0, -1.2, -1.85)], width=560, up="y")
    r2 = 1 / math.sqrt(2)
    hf = lambda th, s: (r2 * math.cosh(s) * math.cos(th), 0.5 * math.sinh(s), r2 * math.cosh(s) * math.sin(th))  # noqa: E731
    f.surface(hf, (0, TAU), (-S, S), THEORY, nu=48, nv=24, net=(8, 0))
    for s in (-S, S):
        f.trace(lambda t, s=s: hf(t, s), 0, TAU, THEORY, on=dict(width=1.2, opacity=0.7),
                off=dict(width=1.0, dash="4 3", opacity=0.4))
    f.axes(((-2.2, 2.2), (-1.5, 1.65), (-2.2, 2.2)))
    for th in (0, math.pi):
        f.trace(lambda t, th=th: hf(th, t), -S, S, PRACTICE)
    for th in (math.pi / 2, -math.pi / 2):
        f.trace(lambda t, th=th: hf(th, t), -S, S, REMARK)
    f.trace(lambda t: hf(t, 0), 0, TAU, BASE, on=dict(width=2.2, opacity=1.0))
    f.place(hf(0, 1.1), eq("2x² − 4y² = 1"), DESC, PRACTICE, prefs=["r", "ur", "dr"], d=10, leader=True)
    f.place(hf(math.pi / 2, -1.2), eq("2z² − 4y² = 1"), DESC, REMARK, prefs=["dl", "l", "d"], d=10, leader=True)
    f.place(hf(math.radians(-70), 0), eq("x² + z² = 1/2"), DESC, BASE, prefs=["dr", "r", "d"], d=12, leader=True)
    f.render(
        "tek-kanatli-donel",
        "Tek kanatlı dönel hiperboloid 2<em>x</em>² − 4<em>y</em>² + 2<em>z</em>² = 1, "
        "−1,2 ≤ <em>y</em> ≤ 1,2 (<em>y</em>-ekseni dikey). Bel çemberi <em>x</em>² + <em>z</em>² = 1/2 "
        "(yeşil); <em>xy</em>-düzlemindeki 2<em>x</em>² − 4<em>y</em>² = 1 hiperbolü (kırmızı) üreteçtir, "
        "<em>yz</em>-düzlemindeki iz 2<em>z</em>² − 4<em>y</em>² = 1 hiperbolüdür.",
        "One sheeted hyperboloid 2x^2 - 4y^2 + 2z^2 = 1 around the vertical y axis with the waist "
        "circle, the hyperbola in the xy plane and the hyperbola in the yz plane")

# ============================================================ hiperbol-x-ekseni
if want("hiperbol-x-ekseni"):
    S = math.acosh(2.5)
    f = Fig(-76, 16, [(-3.3, 0, 0), (3.6, 0, 0), (0, -2.5, 0), (0, 2.6, 0), (0, 0, -2.5), (0, 0, 2.6),
                      (2.5, 2.3, 0), (-2.5, -2.3, 0), (2.5, 0, 2.3), (-2.5, 0, -2.3)], width=600)
    for sg in (1, -1):
        hf = lambda s, th, sg=sg: (sg * math.cosh(s), math.sinh(s) * math.cos(th), math.sinh(s) * math.sin(th))  # noqa: E731
        f.surface(hf, (0.002, S), (0, TAU), THEORY, nu=24, nv=48, net=(0, 8))
    for xx in (2.5, -2.5, 1.6, -1.6):
        rr = math.sqrt(xx * xx - 1)
        strong = abs(xx) == 2.5
        f.trace(lambda t, xx=xx, rr=rr: (xx, rr * math.cos(t), rr * math.sin(t)), 0, TAU, THEORY,
                on=dict(width=1.2 if strong else 1.0, opacity=0.75 if strong else 0.5),
                off=dict(width=0.9, dash="4 3", opacity=0.35))
    f.axes(((-3.3, 3.6), (-2.5, 2.6), (-2.5, 2.6)))
    for sg in (1, -1):
        f.trace(lambda t, sg=sg: (sg * math.cosh(t), math.sinh(t), 0), -S, S, PRACTICE)
    f.rot_arrow((3.15, 0, 0), EX, 0.4, 200, 470, TEXT, 1.6, e1=EY)
    for Q in ((1, 0, 0), (-1, 0, 0)):
        f.point(Q, TEXT, 4.0)
    f.place((1, 0, 0), "(" + it("a") + ", 0, 0)", DESC, prefs=["d", "dr", "dl"], d=8, leader=True)
    f.place((-1, 0, 0), "(−" + it("a") + ", 0, 0)", DESC, prefs=["u", "ul", "ur"], d=8, leader=True)
    f.place((math.cosh(1.1), math.sinh(1.1), 0), "Γ", NAME + 1, PRACTICE, prefs=["u", "ur", "ul"], d=7)
    f.render(
        "hiperbol-x-ekseni",
        "<em>a</em> = <em>b</em> = 1 için <em>x</em>² − <em>y</em>² = 1 hiperbolünün (kırmızı, Γ) "
        "<em>x</em>-ekseni etrafında döndürülmesiyle oluşan iki kanatlı hiperboloid "
        "<em>x</em>² − <em>y</em>² − <em>z</em>² = 1, |<em>x</em>| ≤ 2,5. Kanatlar köşelerde başlar; "
        "−1 &lt; <em>x</em> &lt; 1 bölgesinde yüzey yoktur.",
        "Two sheeted hyperboloid of revolution x^2 - y^2 - z^2 = 1 around the horizontal x axis with "
        "the hyperbola Gamma in the xy plane, circles at x = 1.6 and x = 2.5 on each sheet, the "
        "vertices (a, 0, 0) and (-a, 0, 0) and a curved arrow around the x axis")

# ============================================================ iki-kanatli-donel
if want("iki-kanatli-donel"):
    a, b = 1 / math.sqrt(2), 0.5
    S = math.acosh(2 / a)
    f = Fig(-76, 16, [(-2.6, 0, 0), (2.9, 0, 0), (0, -1.6, 0), (0, 1.7, 0), (0, 0, -1.6), (0, 0, 1.7),
                      (2, 1.33, 0), (-2, -1.33, 0), (2, 0, 1.33), (-2, 0, -1.33)], width=600)
    for sg in (1, -1):
        hf = lambda s, th, sg=sg: (sg * a * math.cosh(s), b * math.sinh(s) * math.cos(th), b * math.sinh(s) * math.sin(th))  # noqa: E731
        f.surface(hf, (0.002, S), (0, TAU), THEORY, nu=24, nv=48, net=(0, 8))
        f.trace(lambda t, sg=sg: (sg * 2, math.sqrt(7) / 2 * math.cos(t), math.sqrt(7) / 2 * math.sin(t)),
                0, TAU, THEORY, on=dict(width=1.2, opacity=0.75), off=dict(width=0.9, dash="4 3", opacity=0.35))
    f.axes(((-2.6, 2.9), (-1.6, 1.7), (-1.6, 1.7)))
    for sg in (1, -1):
        f.trace(lambda t, sg=sg: (sg * a * math.cosh(t), 0, b * math.sinh(t)), -S, S, BASE)
        f.trace(lambda t, sg=sg: (sg * a * math.cosh(t), b * math.sinh(t), 0), -S, S, PRACTICE)
    for Q in ((a, 0, 0), (-a, 0, 0)):
        f.point(Q, TEXT, 4.0)
    f.place((a, 0, 0), "1/√2", DESC, prefs=["d", "dr", "dl"], d=8, leader=True)
    f.place((-a, 0, 0), "−1/√2", DESC, prefs=["u", "ul", "ur"], d=8, leader=True)
    f.place((a * math.cosh(1.2), b * math.sinh(1.2), 0), eq("2x² − 4y² = 1"), DESC, PRACTICE,
            prefs=["u", "ur", "ul"], d=10, leader=True, far=(0, 7, 15))
    f.place((-a * math.cosh(1.3), 0, b * math.sinh(1.3)), eq("2x² − 4z² = 1"), DESC, BASE,
            prefs=["ur", "u", "r"], d=10, leader=True, far=(0, 7, 15))
    f.render(
        "iki-kanatli-donel",
        "İki kanatlı dönel hiperboloid 2<em>x</em>² − 4<em>y</em>² − 4<em>z</em>² = 1, |<em>x</em>| ≤ 2: "
        "<em>xy</em>-düzlemindeki iz 2<em>x</em>² − 4<em>y</em>² = 1 (kırmızı), <em>xz</em>-düzlemindeki "
        "iz 2<em>x</em>² − 4<em>z</em>² = 1 (yeşil); <em>x</em> = ±2&#8217;deki uç çemberlerin yarıçapı "
        "√7/2&#8217;dir. Köşeler (±1/√2, 0, 0) noktalarıdır.",
        "Two sheeted hyperboloid 2x^2 - 4y^2 - 4z^2 = 1 for |x| up to 2 with its hyperbolic traces in the "
        "xy and xz planes, the end circles and the vertices 1/root 2 and -1/root 2")

# ============================================================ elipsoid
if want("elipsoid"):
    a, b, c = 1 / math.sqrt(2), 1 / math.sqrt(3), 1 / 3
    f = Fig(35, 20, [(-1, 0, 0), (1.05, 0, 0), (0, -1, 0), (0, 1.05, 0), (0, 0, -0.8), (0, 0, 0.9)],
            width=560)
    e = 1e-3
    ef = lambda u, v: (a * math.cos(v) * math.cos(u), b * math.cos(v) * math.sin(u), c * math.sin(v))  # noqa: E731
    f.surface(ef, (0, TAU), (-math.pi / 2 + e, math.pi / 2 - e), THEORY, nu=48, nv=24, net=(8, 0))
    f.axes(((-1, 1.05), (-1, 1.05), (-0.8, 0.9)))
    f.trace(lambda s: (0, b * math.cos(s), c * math.sin(s)), 0, TAU, THEORY, on=dict(width=2.2, opacity=1.0))
    f.trace(lambda s: (a * math.cos(s), 0, c * math.sin(s)), 0, TAU, BASE)
    f.trace(lambda s: (a * math.cos(s), b * math.sin(s), 0), 0, TAU, PRACTICE)
    for Q in ((a, 0, 0), (0, b, 0), (0, 0, c)):
        f.point(Q, TEXT, 3.8)
    f.place((a, 0, 0), "1/√2", DESC, prefs=["dl", "l", "d"], d=6)
    f.place((0, b, 0), "1/√3", DESC, prefs=["dr", "d", "r"], d=6)
    f.place((0, 0, c), "1/3", DESC, prefs=["ur", "ul", "u"], d=6, leader=True)
    f.render(
        "elipsoid",
        "Elipsoid 2<em>x</em>² + 3<em>y</em>² + 9<em>z</em>² = 1 ve koordinat düzlemlerindeki izleri: "
        "2<em>x</em>² + 3<em>y</em>² = 1 (kırmızı, <em>z</em> = 0), 2<em>x</em>² + 9<em>z</em>² = 1 "
        "(yeşil, <em>y</em> = 0), 3<em>y</em>² + 9<em>z</em>² = 1 (mavi, <em>x</em> = 0). "
        "<em>c</em> = 1/3 küçük olduğundan yüzey <em>z</em> doğrultusunda basıktır.",
        "Flat ellipsoid 2x^2 + 3y^2 + 9z^2 = 1 with its three traces in the coordinate planes in three "
        "colours and the semi axes 1/root 2, 1/root 3, 1/3 marked on the positive axes")

# ============================================================ eliptik-paraboloid
if want("eliptik-paraboloid"):
    f = Fig(35, 30, [(-1.8, 0, 0), (1.8, 0, 0), (0, -1.6, 0), (0, 1.6, 0), (0, 0, 0), (0, 0, 5.3),
                     (1.41, 1.15, 4), (-1.41, -1.15, 4)], width=540)
    pf = lambda s, u: (s * math.cos(u) / math.sqrt(2), s * math.sin(u) / math.sqrt(3), s * s)   # noqa: E731
    f.surface(pf, (0.002, 2), (0, TAU), THEORY, nu=16, nv=48, net=(4, 12))
    f.axes(((-1.8, 1.8), (-1.6, 1.6), (0, 5.3)))
    f.trace(lambda t: (t, 0, 2 * t * t), -math.sqrt(2), math.sqrt(2), PRACTICE)
    f.trace(lambda t: (0, t, 3 * t * t), -2 / math.sqrt(3), 2 / math.sqrt(3), BASE)
    for zz in (1, 4):
        f.trace(lambda u, zz=zz: pf(math.sqrt(zz), u), 0, TAU, THEORY, on=dict(width=2.2, opacity=1.0))
    f.point(O3, TEXT, 4.0)
    f.place(O3, it("O"), NAME, prefs=["dl", "l", "d"], d=6)
    f.place((1.25, 0, 3.125), eq("z = 2x²"), DESC, PRACTICE, prefs=["l", "dl", "ul"], d=10, leader=True)
    f.place((0, 1.0, 3.0), eq("z = 3y²"), DESC, BASE, prefs=["r", "dr", "ur"], d=10, leader=True)
    f.place(pf(1, math.radians(-40)), eq("z = 1"), DESC, THEORY, prefs=["r", "dr", "ur"], d=10)
    f.place(pf(2, math.radians(-40)), eq("z = 4"), DESC, THEORY, prefs=["r", "dr", "ur"], d=10)
    f.render(
        "eliptik-paraboloid",
        "Eliptik paraboloid 2<em>x</em>² + 3<em>y</em>² = <em>z</em>, 0 ≤ <em>z</em> ≤ 4. "
        "<em>xz</em>- ve <em>yz</em>-düzlemlerindeki izler <em>z</em> = 2<em>x</em>² (kırmızı) ve "
        "<em>z</em> = 3<em>y</em>² (yeşil) parabolleridir; <em>z</em> = 1 ve <em>z</em> = 4 "
        "düzlemlerindeki izler elipstir. Köşe <em>O</em>&#8217;dur.",
        "Elliptic paraboloid 2x^2 + 3y^2 = z for z from 0 to 4 shaped like a bowl with the parabolas "
        "z = 2x^2 and z = 3y^2 and the ellipses at z = 1 and z = 4")

# ============================================================ eliptik-koni
if want("eliptik-koni"):
    f = Fig(35, 22, [(-3.2, 0, 0), (3.2, 0, 0), (0, -2.6, 0), (0, 2.6, 0), (0, 0, -1.6), (0, 0, 1.7),
                     (2.76, 2.25, 1.3), (-2.76, -2.25, -1.3)], width=600)
    kf = lambda u, t: (3 * t / math.sqrt(2) * math.cos(u), math.sqrt(3) * t * math.sin(u), t)   # noqa: E731
    f.surface(kf, (0, TAU), (0.003, 1.3), THEORY, nu=48, nv=6, net=(0, 0))
    f.surface(kf, (0, TAU), (-1.3, -0.003), THEORY, nu=48, nv=6, net=(0, 0))
    for t in (-1.3, 1.3):
        f.trace(lambda s, t=t: kf(s, t), 0, TAU, THEORY, on=dict(width=1.0, opacity=0.55),
                off=dict(width=0.9, dash="4 3", opacity=0.3))
    f.axes(((-3.2, 3.2), (-2.6, 2.6), (-1.6, 1.7)))
    for sg in (1, -1):
        f.trace(lambda t, sg=sg: (sg * 3 / math.sqrt(2) * t, 0, t), -1.3, 1.3, BASE)
        f.trace(lambda t, sg=sg: (0, sg * math.sqrt(3) * t, t), -1.3, 1.3, REMARK)
    for zz in (1, -1):
        f.trace(lambda s, zz=zz: kf(s, zz), 0, TAU, PRACTICE)
    f.point(O3, TEXT, 4.0)
    f.place(O3, it("O"), NAME, prefs=["l", "dl", "ul"], d=8)
    f.place(kf(math.radians(-20), 1), eq("z = 1"), DESC, PRACTICE, prefs=["r", "dr", "ur"], d=10)
    f.place(kf(math.radians(-20), -1), eq("z = −1"), DESC, PRACTICE, prefs=["r", "dr", "ur"], d=10)
    f.place((3 / math.sqrt(2) * 1.2, 0, 1.2), it("x") + " = ±(3/√2) " + it("z"), DESC, BASE,
            prefs=["l", "dl", "ul"], d=10, leader=True)
    f.place((0, math.sqrt(3) * 1.2, 1.2), it("y") + " = ±√3 " + it("z"), DESC, REMARK,
            prefs=["r", "ur", "dr"], d=10, leader=True)
    f.render(
        "eliptik-koni",
        "Eliptik koni 2<em>x</em>² + 3<em>y</em>² = 9<em>z</em>², |<em>z</em>| ≤ 1,3. <em>z</em> = ±1 "
        "düzlemlerindeki izler aynı 2<em>x</em>² + 3<em>y</em>² = 9 elipsidir (kırmızı); "
        "<em>xz</em>-düzlemindeki iz <em>x</em> = ±(3/√2)<em>z</em> (yeşil), <em>yz</em>-düzlemindeki iz "
        "<em>y</em> = ±√3 <em>z</em> doğru çiftidir. İki kanat <em>O</em>&#8217;da birleşir.",
        "Double elliptic cone 2x^2 + 3y^2 = 9z^2 with the ellipses at z = 1 and z = -1 and the two "
        "pairs of lines in the xz and yz planes through the vertex O")

# ============================================================ tek-kanatli-hiperboloid
if want("tek-kanatli-hiperboloid"):
    S = math.asinh(3)
    f = Fig(35, 18, [(-2.8, 0, 0), (2.8, 0, 0), (0, -2.3, 0), (0, 2.3, 0), (0, 0, -1.4), (0, 0, 1.55),
                     (2.24, 1.83, 1), (-2.24, -1.83, -1)], width=600)
    hf = lambda u, s: (math.cosh(s) * math.cos(u) / math.sqrt(2), math.cosh(s) * math.sin(u) / math.sqrt(3),  # noqa: E731
                       math.sinh(s) / 3)
    f.surface(hf, (0, TAU), (-S, S), THEORY, nu=48, nv=24, net=(12, 0))
    for s in (-S, S):
        f.trace(lambda t, s=s: hf(t, s), 0, TAU, THEORY, on=dict(width=1.3, opacity=0.8),
                off=dict(width=1.0, dash="4 3", opacity=0.4))
    f.axes(((-2.8, 2.8), (-2.3, 2.3), (-1.4, 1.55)))
    for u in (0, math.pi):
        f.trace(lambda t, u=u: hf(u, t), -S, S, PRACTICE)
    for u in (math.pi / 2, -math.pi / 2):
        f.trace(lambda t, u=u: hf(u, t), -S, S, REMARK)
    f.trace(lambda t: hf(t, 0), 0, TAU, BASE)
    f.place(hf(math.radians(-15), S), eq("z = 1"), DESC, THEORY, prefs=["r", "ur", "dr"], d=10)
    f.place(hf(math.radians(-15), -S), eq("z = −1"), DESC, THEORY, prefs=["r", "dr", "ur"], d=10)
    f.place(hf(math.radians(-100), 0), "bel elipsi", DESC, BASE, prefs=["d", "dr", "dl"], d=12, leader=True)
    f.place(hf(0, -1.2), eq("2x² − 9z² = 1"), DESC, PRACTICE, prefs=["l", "dl", "ul"], d=12, leader=True)
    f.place(hf(math.pi / 2, 1.2), eq("3y² − 9z² = 1"), DESC, REMARK, prefs=["r", "ur", "dr"], d=12, leader=True)
    f.render(
        "tek-kanatli-hiperboloid",
        "Tek kanatlı hiperboloid 2<em>x</em>² + 3<em>y</em>² − 9<em>z</em>² = 1, |<em>z</em>| ≤ 1. "
        "<em>z</em> = 0&#8217;daki bel elipsi 2<em>x</em>² + 3<em>y</em>² = 1 (yeşil), <em>z</em> = ±1&#8217;deki "
        "uç elipsler 2<em>x</em>² + 3<em>y</em>² = 10&#8217;dur; <em>xz</em>- ve <em>yz</em>-düzlemlerindeki "
        "izler 2<em>x</em>² − 9<em>z</em>² = 1 (kırmızı) ve 3<em>y</em>² − 9<em>z</em>² = 1 hiperbolleridir.",
        "One sheeted hyperboloid 2x^2 + 3y^2 - 9z^2 = 1 for |z| up to 1 with the waist ellipse, the end "
        "ellipses at z = 1 and z = -1 and the hyperbolas in the xz and yz planes")

# ============================================================ iki-kanatli-hiperboloid
if want("iki-kanatli-hiperboloid"):
    S = math.acosh(2 * math.sqrt(2))
    f = Fig(-76, 16, [(-2.8, 0, 0), (3.0, 0, 0), (0, -2, 0), (0, 2, 0), (0, 0, -1.3), (0, 0, 1.3),
                      (2, 1.53, 0), (-2, -1.53, 0), (2, 0, 0.88), (-2, 0, -0.88)], width=600)
    for sg in (1, -1):
        hf = lambda s, u, sg=sg: (sg * math.cosh(s) / math.sqrt(2), math.sinh(s) * math.cos(u) / math.sqrt(3),  # noqa: E731
                                  math.sinh(s) * math.sin(u) / 3)
        f.surface(hf, (0.002, S), (0, TAU), THEORY, nu=24, nv=48, net=(0, 8))
        f.trace(lambda t, sg=sg: hf(S, t), 0, TAU, THEORY, on=dict(width=1.3, opacity=0.8),
                off=dict(width=0.9, dash="4 3", opacity=0.35))
    f.axes(((-2.8, 3.0), (-2, 2), (-1.3, 1.3)))
    for sg in (1, -1):
        f.trace(lambda t, sg=sg: (sg * math.cosh(t) / math.sqrt(2), math.sinh(t) / math.sqrt(3), 0), -S, S, PRACTICE)
        f.trace(lambda t, sg=sg: (sg * math.cosh(t) / math.sqrt(2), 0, math.sinh(t) / 3), -S, S, BASE)
    r2 = 1 / math.sqrt(2)
    for Q in ((r2, 0, 0), (-r2, 0, 0)):
        f.point(Q, TEXT, 4.0)
    f.place((r2, 0, 0), "1/√2", DESC, prefs=["d", "dr", "dl"], d=8, leader=True)
    f.place((-r2, 0, 0), "−1/√2", DESC, prefs=["u", "ul", "ur"], d=8, leader=True)
    f.place((2, 0, -0.95), eq("x = 2"), DESC, THEORY, prefs=["d", "dr", "dl"], d=8)
    f.place((-2, 0, 0.95), eq("x = −2"), DESC, THEORY, prefs=["u", "ul", "ur"], d=8)
    f.place((math.cosh(1.5) / math.sqrt(2), math.sinh(1.5) / math.sqrt(3), 0), eq("2x² − 3y² = 1"), DESC,
            PRACTICE, prefs=["ur", "r", "u"], d=10, leader=True)
    f.place((-math.cosh(1.5) / math.sqrt(2), 0, math.sinh(1.5) / 3), eq("2x² − 9z² = 1"), DESC, BASE,
            prefs=["ul", "u", "l"], d=10, leader=True)
    f.render(
        "iki-kanatli-hiperboloid",
        "İki kanatlı hiperboloid 2<em>x</em>² − 3<em>y</em>² − 9<em>z</em>² = 1, |<em>x</em>| ≤ 2: "
        "<em>xy</em>-düzlemindeki iz 2<em>x</em>² − 3<em>y</em>² = 1 (kırmızı), <em>xz</em>-düzlemindeki "
        "iz 2<em>x</em>² − 9<em>z</em>² = 1 (yeşil); <em>x</em> = ±2 düzlemlerindeki uç elipsler "
        "3<em>y</em>² + 9<em>z</em>² = 7&#8217;dir. Yüzey <em>yz</em>-düzlemini kesmez.",
        "Two sheeted hyperboloid 2x^2 - 3y^2 - 9z^2 = 1 opening along the x axis with its hyperbolic "
        "traces in the xy and xz planes, the end ellipses at x = 2 and x = -2 and the vertices")

# ============================================================ hiperbolik-paraboloid
if want("hiperbolik-paraboloid"):
    X, Y = 1.0, 0.8
    f = Fig(58, 30, [(-1.6, 0, 0), (1.6, 0, 0), (0, -1.5, 0), (0, 1.5, 0), (0, 0, -2.4), (0, 0, 2.5),
                     (X, Y, 3 * Y * Y - 2 * X * X), (-X, -Y, 3 * Y * Y - 2 * X * X)], width=560)
    hp = lambda x, y: (x, y, -2 * x * x + 3 * y * y)                           # noqa: E731
    f.surface(hp, (-X, X), (-Y, Y), THEORY, nu=32, nv=32, net=(8, 8))
    for x in (-X, X):
        f.trace(lambda t, x=x: hp(x, t), -Y, Y, THEORY, on=dict(width=1.2, opacity=0.75),
                off=dict(width=0.9, dash="4 3", opacity=0.35))
    for y in (-Y, Y):
        f.trace(lambda t, y=y: hp(t, y), -X, X, THEORY, on=dict(width=1.2, opacity=0.75),
                off=dict(width=0.9, dash="4 3", opacity=0.35))
    f.axes(((-1.6, 1.6), (-1.5, 1.5), (-2.4, 2.5)))
    k = math.sqrt(2 / 3)
    for sg in (1, -1):
        f.trace(lambda t, sg=sg: hp(t, sg * k * t), -X, X, TEXT,
                on=dict(width=1.2, dash="5 4", opacity=0.7), off=dict(width=1.0, dash="3 3", opacity=0.35))
    ym = math.sqrt((X * X - 0.5) / 1.5)
    for sg in (1, -1):
        f.trace(lambda t, sg=sg: (sg * math.sqrt(0.5 + 1.5 * t * t), t, -1.0), -ym, ym, REMARK, n=80)
    f.trace(lambda t: hp(0, t), -Y, Y, PRACTICE)
    f.trace(lambda t: hp(t, 0), -X, X, BASE)
    f.point(O3, TEXT, 4.0)
    f.place(O3, it("O"), NAME, prefs=["dl", "l", "d"], d=6)
    f.place(hp(0, 0.7), eq("z = 3y²"), DESC, PRACTICE, prefs=["r", "ur", "dr"], d=10, leader=True)
    f.place(hp(0.75, 0), eq("z = −2x²"), DESC, BASE, prefs=["l", "dl", "ul"], d=10, leader=True)
    f.place((math.sqrt(0.5 + 1.5 * 0.09), 0.3, -1.0), eq("z = −1"), DESC, REMARK, prefs=["dr", "d", "r"], d=8,
            leader=True)
    f.render(
        "hiperbolik-paraboloid",
        "Hiperbolik paraboloid (eyer) −2<em>x</em>² + 3<em>y</em>² = <em>z</em>, |<em>x</em>| ≤ 1, "
        "|<em>y</em>| ≤ 0,8. <em>yz</em>-düzlemindeki iz yukarı açılan <em>z</em> = 3<em>y</em>² "
        "(kırmızı), <em>xz</em>-düzlemindeki iz aşağı açılan <em>z</em> = −2<em>x</em>² (yeşil) "
        "parabolüdür; <em>z</em> = 0 izi kesikli doğru çiftidir, <em>z</em> = −1 izi köşeleri "
        "(±1/√2, 0, −1) olan bir hiperboldür (kahverengi). <em>O</em> eyer noktasıdır.",
        "Saddle surface z = -2x^2 + 3y^2 over a rectangle with the upward parabola z = 3y^2, the "
        "downward parabola z = -2x^2, the dashed line pair at z = 0, part of the hyperbola at z = -1 "
        "and the saddle point O")

# ============================================================ otelenmis-koni
if want("otelenmis-koni"):
    f = Fig(35, 18, [(-1.5, 0, 0), (3.5, 0, 0), (0, -2.6, 0), (0, 1, 0), (0, 0, -2.5), (0, 0, 2.6),
                     (3, 0, 2), (-1, -2, -2), (3, -2, 2), (-1, 0, -2)], width=560)
    kf = lambda u, t: (1 + t * math.cos(u), -1 + t / 2 * math.sin(u), t)        # noqa: E731
    f.surface(kf, (0, TAU), (0.003, 2), THEORY, nu=48, nv=6, net=(0, 0))
    f.surface(kf, (0, TAU), (-2, -0.003), THEORY, nu=48, nv=6, net=(0, 0))
    for k in range(8):
        u = TAU * k / 8 + 0.25
        f.vis([kf(u, -2 + 4 * j / 80) for j in range(81)], THEORY, on=dict(width=0.8, opacity=0.5, w=0.15),
              off=dict(width=0.6, opacity=0.18, w=0.0))
    f.axes(((-1.5, 3.5), (-2.6, 1), (-2.5, 2.6)))
    Tt = (1.0, -1.0, 0.0)
    f.vis([(1, -1, -2.4), (1, -1, 2.4)], TEXT, on=dict(width=1.1, dash="6 4", opacity=0.75),
          off=dict(width=1.0, dash="3 3", opacity=0.4))
    f.guide([O3, Tt], TEXT, 0.6, 1.0, "3 3")
    for zz in (2, -2):
        f.trace(lambda s, zz=zz: kf(s, zz), 0, TAU, PRACTICE)
    f.point(Tt, TEXT, 4.4)
    f.place(Tt, it("T") + triple(1, -1, 0), NAME, prefs=["r", "dr", "ur"], d=10, leader=True)
    f.place(kf(math.radians(-30), 2), eq("z = 2"), DESC, PRACTICE, prefs=["r", "ur", "dr"], d=10)
    f.place(kf(math.radians(-30), -2), eq("z = −2"), DESC, PRACTICE, prefs=["r", "dr", "ur"], d=10)
    f.render(
        "otelenmis-koni",
        "Eliptik koni (<em>x</em> − 1)² + 4(<em>y</em> + 1)² = <em>z</em>², |<em>z</em>| ≤ 2. Tepe "
        "noktası <em>T</em>(1, −1, 0), ekseni <em>T</em>&#8217;den geçen ve <em>z</em>-eksenine paralel "
        "kesikli doğrudur; <em>z</em> = ±2&#8217;deki izler merkezi (1, −1, ±2), yarı eksenleri 2 ve 1 "
        "olan elipslerdir.",
        "Double elliptic cone (x - 1)^2 + 4(y + 1)^2 = z^2 with vertex T(1, -1, 0), its dashed vertical "
        "axis and the ellipses at z = 2 and z = -2")

# ============================================================ otelenmis-paraboloid
if want("otelenmis-paraboloid"):
    f = Fig(35, 18, [(-0.5, 0, 0), (4.5, 0, 0), (0, -2.5, 0), (0, 2.5, 0), (0, 0, -1.5), (0, 0, 3.8),
                     (4, 2, 3), (0, -2, 3), (4, -2, 3), (0, 2, 3)], width=540)
    pf = lambda s, u: (2 + s * math.cos(u), s * math.sin(u), s * s - 1)          # noqa: E731
    f.surface(pf, (0.002, 2), (0, TAU), THEORY, nu=16, nv=48, net=(4, 12))
    f.axes(((-0.5, 4.5), (-2.5, 2.5), (-1.5, 3.8)))
    V = (2.0, 0.0, -1.0)
    f.vis([V, (2, 0, 3.4)], TEXT, on=dict(width=1.1, dash="6 4", opacity=0.75),
          off=dict(width=1.0, dash="3 3", opacity=0.4))
    f.trace(lambda t: (t, 0, (t - 2) ** 2 - 1), 0, 4, BASE)
    f.trace(lambda u: pf(1, u), 0, TAU, PRACTICE)
    f.trace(lambda u: pf(2, u), 0, TAU, THEORY, on=dict(width=2.2, opacity=1.0))
    f.point(V, TEXT, 4.4)
    f.place(V, it("V") + triple(2, 0, -1), NAME, prefs=["r", "dr", "d"], d=10)
    f.place(pf(2, math.radians(-40)), eq("z = 3"), DESC, THEORY, prefs=["r", "dr", "ur"], d=10)
    f.place(pf(1, math.radians(-60)), eq("z = 0"), DESC, PRACTICE, prefs=["r", "dr", "d"], d=10, leader=True)
    f.render(
        "otelenmis-paraboloid",
        "Dönel paraboloid (<em>x</em> − 2)² + <em>y</em>² = <em>z</em> + 1, −1 ≤ <em>z</em> ≤ 3. Köşe "
        "<em>V</em>(2, 0, −1), eksen köşeden geçen düşey kesikli doğrudur. <em>z</em> = 3 izi yarıçapı 2, "
        "<em>z</em> = 0 izi (kırmızı) yarıçapı 1 olan çemberdir; yeşil eğri <em>y</em> = 0 düzlemindeki "
        "<em>z</em> = (<em>x</em> − 2)² − 1 parabolüdür.",
        "Paraboloid of revolution (x - 2)^2 + y^2 = z + 1 with vertex V(2, 0, -1), its vertical axis, "
        "the circles at z = 3 and z = 0 and the parabola in the plane y = 0")

# ============================================================ exr-elipsoid
if want("exr-elipsoid"):
    a, b, c = 2.0, 2.5, 5.0
    f = Fig(35, 20, [(-2.8, 0, 0), (2.8, 0, 0), (0, -3.3, 0), (0, 3.4, 0), (0, 0, -5.8), (0, 0, 6.2)],
            width=480)
    e = 1e-3
    ef = lambda u, v: (a * math.cos(v) * math.cos(u), b * math.cos(v) * math.sin(u), c * math.sin(v))  # noqa: E731
    f.surface(ef, (0, TAU), (-math.pi / 2 + e, math.pi / 2 - e), THEORY, nu=48, nv=24, net=(8, 0))
    f.axes(((-2.8, 2.8), (-3.3, 3.4), (-5.8, 6.2)))
    f.trace(lambda s: (0, b * math.cos(s), c * math.sin(s)), 0, TAU, THEORY, on=dict(width=2.2, opacity=1.0))
    f.trace(lambda s: (a * math.cos(s), 0, c * math.sin(s)), 0, TAU, BASE)
    f.trace(lambda s: (a * math.cos(s), b * math.sin(s), 0), 0, TAU, PRACTICE)
    for Q in ((a, 0, 0), (0, b, 0), (0, 0, c)):
        f.point(Q, TEXT, 3.8)
    f.place((a, 0, 0), "2", NAME, prefs=["dr", "d", "r"], d=6)
    f.place((0, b, 0), "5/2", NAME, prefs=["dr", "d", "ur"], d=6)
    f.place((0, 0, c), "5", NAME, prefs=["ur", "ul", "r"], d=6)
    f.render(
        "exr-elipsoid",
        "Elipsoid <em>x</em>²/4 + <em>y</em>²/(25/4) + <em>z</em>²/25 = 1 (yarı eksenler 2, 5/2, 5) ve "
        "koordinat düzlemlerindeki izleri: <em>z</em> = 0 (kırmızı), <em>y</em> = 0 (yeşil), "
        "<em>x</em> = 0 (mavi). Yüzey <em>z</em> doğrultusunda uzamıştır.",
        "Ellipsoid x^2/4 + y^2/(25/4) + z^2/25 = 1 elongated along the vertical z axis with its three "
        "traces in the coordinate planes and the semi axes 2, 5/2, 5 marked")

# ============================================================ exr-tek-kanatli-z
if want("exr-tek-kanatli-z"):
    S = math.asinh(1)
    f = Fig(35, 18, [(-7, 0, 0), (7, 0, 0), (0, -5.5, 0), (0, 5.5, 0), (0, 0, -7.2), (0, 0, 7.8),
                     (5.66, 4.24, 6), (-5.66, -4.24, -6)], width=600)
    hf = lambda u, s: (4 * math.cosh(s) * math.cos(u), 3 * math.cosh(s) * math.sin(u), 6 * math.sinh(s))  # noqa: E731
    f.surface(hf, (0, TAU), (-S, S), THEORY, nu=48, nv=24, net=(12, 0))
    for s in (-S, S):
        f.trace(lambda t, s=s: hf(t, s), 0, TAU, THEORY, on=dict(width=1.3, opacity=0.8),
                off=dict(width=1.0, dash="4 3", opacity=0.4))
    f.axes(((-7, 7), (-5.5, 5.5), (-7.2, 7.8)))
    for u in (0, math.pi):
        f.trace(lambda t, u=u: hf(u, t), -S, S, PRACTICE)
    for u in (math.pi / 2, -math.pi / 2):
        f.trace(lambda t, u=u: hf(u, t), -S, S, REMARK)
    f.trace(lambda t: hf(t, 0), 0, TAU, BASE)
    for Q in ((4, 0, 0), (0, 3, 0)):
        f.point(Q, TEXT, 3.8)
    f.place((4, 0, 0), "4", NAME, prefs=["dl", "l", "d"], d=6)
    f.place((0, 3, 0), "3", NAME, prefs=["dr", "r", "d"], d=6)
    f.place(hf(math.radians(-15), S), eq("z = 6"), DESC, THEORY, prefs=["r", "ur", "dr"], d=10)
    f.place(hf(math.radians(-15), -S), eq("z = −6"), DESC, THEORY, prefs=["r", "dr", "ur"], d=10)
    f.place(hf(math.radians(-100), 0), "bel elipsi", DESC, BASE, prefs=["d", "dr", "dl"], d=12, leader=True)
    f.render(
        "exr-tek-kanatli-z",
        "Tek kanatlı hiperboloid <em>x</em>²/16 + <em>y</em>²/9 − <em>z</em>²/36 = 1, |<em>z</em>| ≤ 6. "
        "Bel elipsi (yeşil) eksenleri 4 ve 3&#8217;te keser; <em>z</em> = ±6&#8217;daki uç elipslerin yarı "
        "eksenleri 4√2 ve 3√2&#8217;dir. <em>y</em> = 0 ve <em>x</em> = 0 düzlemlerindeki izler "
        "hiperboldür (kırmızı ve kahverengi).",
        "One sheeted hyperboloid x^2/16 + y^2/9 - z^2/36 = 1 for |z| up to 6 with the waist ellipse "
        "through (4, 0, 0) and (0, 3, 0), the end ellipses at z = 6 and z = -6 and the hyperbolic traces")

# ============================================================ exr-tek-kanatli-x
if want("exr-tek-kanatli-x"):
    S = math.asinh(1)
    f = Fig(-68, 14, [(-3, 0, 0), (3.3, 0, 0), (0, -5, 0), (0, 5, 0), (0, 0, -6.4), (0, 0, 6.8),
                      (2, 4.24, 5.66), (-2, -4.24, -5.66), (2, -4.24, 5.66), (-2, 4.24, -5.66)], width=560)
    hf = lambda s, u: (2 * math.sinh(s), 3 * math.cosh(s) * math.cos(u), 4 * math.cosh(s) * math.sin(u))  # noqa: E731
    f.surface(hf, (-S, S), (0, TAU), THEORY, nu=24, nv=48, net=(0, 12))
    for s in (-S, S):
        f.trace(lambda t, s=s: hf(s, t), 0, TAU, THEORY, on=dict(width=1.3, opacity=0.8),
                off=dict(width=1.0, dash="4 3", opacity=0.4))
    f.axes(((-3, 3.3), (-5, 5), (-6.4, 6.8)))
    for u in (0, math.pi):
        f.trace(lambda t, u=u: hf(t, u), -S, S, PRACTICE)
    for u in (math.pi / 2, -math.pi / 2):
        f.trace(lambda t, u=u: hf(t, u), -S, S, REMARK)
    f.trace(lambda t: hf(0, t), 0, TAU, BASE)
    for Q in ((0, 3, 0), (0, 0, 4)):
        f.point(Q, TEXT, 3.8)
    f.place((0, 3, 0), "3", NAME, prefs=["dr", "ur", "r"], d=6)
    f.place((0, 0, 4), "4", NAME, prefs=["ul", "ur", "l"], d=6)
    f.place(hf(S, math.radians(-110)), eq("x = 2"), DESC, THEORY, prefs=["d", "dr", "r"], d=8)
    f.place(hf(-S, math.radians(-110)), eq("x = −2"), DESC, THEORY, prefs=["d", "dl", "l"], d=8)
    f.place(hf(0, math.radians(-120)), "bel elipsi", DESC, BASE, prefs=["d", "dr", "dl"], d=12, leader=True)
    f.render(
        "exr-tek-kanatli-x",
        "Ekseni <em>x</em>-ekseni olan tek kanatlı hiperboloid −<em>x</em>²/4 + <em>y</em>²/9 + "
        "<em>z</em>²/16 = 1, |<em>x</em>| ≤ 2. Bel elipsi <em>x</em> = 0 düzlemindedir (yeşil; yarı "
        "eksenler 3 ve 4); <em>x</em> = ±2&#8217;deki uç elipslerin yarı eksenleri 3√2 ve 4√2&#8217;dir. "
        "<em>z</em> = 0 ve <em>y</em> = 0 düzlemlerindeki izler hiperboldür (kırmızı ve kahverengi).",
        "One sheeted hyperboloid -x^2/4 + y^2/9 + z^2/16 = 1 lying along the horizontal x axis like an "
        "hourglass on its side, with the waist ellipse in the plane x = 0, the end ellipses at x = 2 and "
        "x = -2 and the hyperbolic traces")

# ============================================================ exr-tek-kanatli-otelenmis
if want("exr-tek-kanatli-otelenmis"):
    S = math.asinh(1)
    f = Fig(35, 18, [(-7, 0, 0), (7, 0, 0), (0, -3.8, 0), (0, 3.8, 0), (0, 0, -5), (0, 0, 7.6),
                     (5.66, 2.83, 6), (-5.66, -2.83, -4)], width=600)
    hf = lambda u, s: (4 * math.cosh(s) * math.cos(u), 2 * math.cosh(s) * math.sin(u), 1 + 5 * math.sinh(s))  # noqa: E731
    f.surface(hf, (0, TAU), (-S, S), THEORY, nu=48, nv=24, net=(12, 0))
    f.trace(lambda t: hf(t, S), 0, TAU, THEORY, on=dict(width=1.3, opacity=0.8),
            off=dict(width=1.0, dash="4 3", opacity=0.4))
    f.trace(lambda t: hf(t, -S), 0, TAU, THEORY, on=dict(width=1.3, opacity=0.8),
            off=dict(width=1.0, dash="4 3", opacity=0.4))
    rz = math.sqrt(1 + 1 / 25)
    f.trace(lambda t: (4 * rz * math.cos(t), 2 * rz * math.sin(t), 0), 0, TAU, TEXT,
            on=dict(width=1.0, dash="4 3", opacity=0.55), off=dict(width=0.9, dash="3 3", opacity=0.3))
    f.axes(((-7, 7), (-3.8, 3.8), (-5, 7.6)))
    for u in (0, math.pi):
        f.trace(lambda t, u=u: hf(u, t), -S, S, BASE)
    f.trace(lambda t: hf(t, 0), 0, TAU, PRACTICE)
    C = (0.0, 0.0, 1.0)
    f.point(C, TEXT, 4.2)
    f.place(C, it("C") + triple(0, 0, 1), NAME, prefs=["l", "ul", "dl"], d=9, leader=True)
    f.place(hf(math.radians(-60), 0), eq("z = 1"), DESC, PRACTICE, prefs=["dr", "r", "d"], d=10, leader=True)
    f.place(hf(math.radians(-15), S), eq("z = 6"), DESC, THEORY, prefs=["r", "ur", "dr"], d=10)
    f.place(hf(math.radians(-15), -S), eq("z = −4"), DESC, THEORY, prefs=["r", "dr", "ur"], d=10)
    f.render(
        "exr-tek-kanatli-otelenmis",
        "Merkezi <em>C</em>(0, 0, 1) olan tek kanatlı hiperboloid <em>x</em>²/16 + <em>y</em>²/4 − "
        "(<em>z</em> − 1)²/25 = 1, −4 ≤ <em>z</em> ≤ 6. Bel elipsi (kırmızı) <em>z</em> = 1 "
        "düzlemindedir, yani <em>xy</em>-düzleminin bir birim üstündedir (soluk kesikli elips yüzeyin "
        "<em>z</em> = 0 izidir); yeşil eğriler <em>y</em> = 0 düzlemindeki hiperbolün kollarıdır.",
        "One sheeted hyperboloid x^2/16 + y^2/4 - (z - 1)^2/25 = 1 with center C(0, 0, 1), the waist "
        "ellipse at z = 1, the end ellipses at z = 6 and z = -4, the faint trace at z = 0 and the "
        "hyperbola in the plane y = 0")

# ============================================================ exr-iki-kanatli-z
if want("exr-iki-kanatli-z"):
    S = math.acosh(2)
    f = Fig(35, 16, [(-4.5, 0, 0), (4.5, 0, 0), (0, -6.5, 0), (0, 6.5, 0), (0, 0, -9.4), (0, 0, 10),
                     (3.46, 5.2, 8), (-3.46, -5.2, -8)], width=560)
    for sg in (1, -1):
        hf = lambda s, u, sg=sg: (2 * math.sinh(s) * math.cos(u), 3 * math.sinh(s) * math.sin(u),  # noqa: E731
                                  sg * 4 * math.cosh(s))
        f.surface(hf, (0.002, S), (0, TAU), THEORY, nu=24, nv=48, net=(0, 12))
    f.axes(((-4.5, 4.5), (-6.5, 6.5), (-9.4, 10)))
    for sg in (1, -1):
        f.trace(lambda t, sg=sg: (0, 3 * math.sinh(t), sg * 4 * math.cosh(t)), -S, S, BASE)
        f.trace(lambda t, sg=sg: (2 * math.sinh(t), 0, sg * 4 * math.cosh(t)), -S, S, REMARK)
        f.trace(lambda t, sg=sg: (2 * math.sqrt(3) * math.cos(t), 3 * math.sqrt(3) * math.sin(t), sg * 8),
                0, TAU, PRACTICE)
    for Q in ((0, 0, 4), (0, 0, -4)):
        f.point(Q, TEXT, 4.0)
    f.place((0, 0, 4), triple(0, 0, 4), DESC, prefs=["dl", "l", "dr"], d=8, leader=True)
    f.place((0, 0, -4), triple(0, 0, -4), DESC, prefs=["ul", "l", "ur"], d=8, leader=True)
    f.place((2 * math.sqrt(3) * math.cos(-0.3), 3 * math.sqrt(3) * math.sin(-0.3), 8), eq("z = 8"), DESC,
            PRACTICE, prefs=["r", "ur", "dr"], d=10)
    f.place((2 * math.sqrt(3) * math.cos(-0.3), 3 * math.sqrt(3) * math.sin(-0.3), -8), eq("z = −8"), DESC,
            PRACTICE, prefs=["r", "dr", "ur"], d=10)
    f.render(
        "exr-iki-kanatli-z",
        "Ekseni <em>z</em>-ekseni olan iki kanatlı hiperboloid −<em>x</em>²/4 − <em>y</em>²/9 + "
        "<em>z</em>²/16 = 1, 4 ≤ |<em>z</em>| ≤ 8. Köşeler (0, 0, ±4); <em>z</em> = ±8&#8217;deki uç "
        "elipsler <em>x</em>²/4 + <em>y</em>²/9 = 3&#8217;tür (kırmızı). <em>x</em> = 0 ve <em>y</em> = 0 "
        "düzlemlerindeki izler hiperboldür (yeşil ve kahverengi); −4 &lt; <em>z</em> &lt; 4 şeridinde "
        "yüzey yoktur.",
        "Two sheeted hyperboloid -x^2/4 - y^2/9 + z^2/16 = 1 with an upper and a lower bowl, the "
        "vertices (0, 0, 4) and (0, 0, -4), the end ellipses at z = 8 and z = -8 and the hyperbolic "
        "traces in the planes x = 0 and y = 0")

# ============================================================ exr-paraboloid
if want("exr-paraboloid"):
    f = Fig(35, 24, [(-2.6, 0, 0), (2.6, 0, 0), (0, -2.8, 0), (0, 2.8, 0), (0, 0, 0), (0, 0, 3.9),
                     (2, 2.31, 3), (-2, -2.31, 3)], width=560)
    q = 4 / math.sqrt(3)
    pf = lambda s, u: (2 * s * math.cos(u), q * s * math.sin(u), 3 * s * s)     # noqa: E731
    f.surface(pf, (0.002, 1), (0, TAU), THEORY, nu=16, nv=48, net=(4, 12))
    f.axes(((-2.6, 2.6), (-2.8, 2.8), (0, 3.9)))
    f.trace(lambda t: (t, 0, 0.75 * t * t), -2, 2, BASE, on=dict(width=1.6, opacity=0.9),
            off=dict(width=1.2, dash="4 3", opacity=0.5))
    f.trace(lambda u: pf(1, u), 0, TAU, PRACTICE)
    A, B = (2.0, 0.0, 3.0), (1.0, 2.0, 3.0)
    assert abs(12 * 4 - 16 * 3) < 1e-12 and abs(12 + 9 * 4 - 16 * 3) < 1e-12
    for Q in (A, B):
        f.point(Q, TEXT, 4.6)
    f.point(O3, TEXT, 4.0)
    f.place(O3, it("O"), NAME, prefs=["dl", "l", "d"], d=6)
    f.place(A, triple(2, 0, 3), NAME, prefs=["dl", "l", "d"], d=8)
    f.place(B, triple(1, 2, 3), NAME, prefs=["dr", "r", "ur"], d=8)
    f.render(
        "exr-paraboloid",
        "Eliptik paraboloid 12<em>x</em>² + 9<em>y</em>² = 16<em>z</em>, 0 ≤ <em>z</em> ≤ 3. Verilen "
        "(2, 0, 3) ve (1, 2, 3) noktaları <em>z</em> = 3 izi olan <em>x</em>²/4 + <em>y</em>²/(16/3) = 1 "
        "elipsinin (kırmızı) üzerindedir; yeşil eğri <em>xz</em>-düzlemindeki <em>z</em> = (3/4)<em>x</em>² "
        "parabolüdür.",
        "Elliptic paraboloid 12x^2 + 9y^2 = 16z for z from 0 to 3 with the ellipse at z = 3 through the "
        "points (2, 0, 3) and (1, 2, 3), the parabola z = 3x^2/4 in the xz plane and the vertex O")

# ============================================================ exr-tamkare-hiperboloid
if want("exr-tamkare-hiperboloid"):
    S = math.asinh(1)
    a, b = 2 * math.sqrt(3), math.sqrt(6)
    C = (-2.0, 1.0, -1.0)
    f = Fig(35, 18, [(-8, 0, 0), (3, 0, 0), (0, -3.5, 0), (0, 5, 0), (0, 0, -4.5), (0, 0, 2.7),
                     (-6.9, 4.46, 1), (2.9, -2.46, -3), (-6.9, -2.46, 1), (2.9, 4.46, -3)], width=600)
    hf = lambda u, s: (C[0] + a * math.cosh(s) * math.cos(u), C[1] + b * math.cosh(s) * math.sin(u),  # noqa: E731
                       C[2] + 2 * math.sinh(s))
    f.surface(hf, (0, TAU), (-S, S), THEORY, nu=48, nv=24, net=(12, 0))
    for s in (-S, S):
        f.trace(lambda t, s=s: hf(t, s), 0, TAU, THEORY, on=dict(width=1.3, opacity=0.8),
                off=dict(width=1.0, dash="4 3", opacity=0.4))
    f.axes(((-8, 3), (-3.5, 5), (-4.5, 2.7)))
    f.vis([(C[0], C[1], -3.6), (C[0], C[1], 1.6)], TEXT, on=dict(width=1.1, dash="6 4", opacity=0.75),
          off=dict(width=1.0, dash="3 3", opacity=0.4))
    f.trace(lambda t: hf(t, 0), 0, TAU, PRACTICE)
    f.point(C, TEXT, 4.2)
    f.place(C, it("C") + triple(-2, 1, -1), NAME, prefs=["r", "ur", "dr"], d=9, leader=True)
    f.place(hf(math.radians(-60), 0), eq("z = −1"), DESC, PRACTICE, prefs=["dr", "d", "r"], d=10, leader=True)
    f.place(hf(math.radians(-15), S), eq("z = 1"), DESC, THEORY, prefs=["r", "ur", "dr"], d=10)
    f.place(hf(math.radians(-15), -S), eq("z = −3"), DESC, THEORY, prefs=["r", "dr", "ur"], d=10)
    f.render(
        "exr-tamkare-hiperboloid",
        "Tek kanatlı hiperboloid (<em>x</em> + 2)²/12 + (<em>y</em> − 1)²/6 − (<em>z</em> + 1)²/4 = 1, "
        "−3 ≤ <em>z</em> ≤ 1. Merkez <em>C</em>(−2, 1, −1); eksen <em>C</em>&#8217;den geçen düşey kesikli "
        "doğrudur. Bel elipsi (kırmızı) <em>z</em> = −1 düzlemindedir, yarı eksenleri 2√3 ve √6&#8217;dır.",
        "One sheeted hyperboloid (x + 2)^2/12 + (y - 1)^2/6 - (z + 1)^2/4 = 1 with center C(-2, 1, -1), "
        "its dashed vertical axis, the waist ellipse at z = -1 and the end ellipses at z = 1 and z = -3")

# ============================================================ exr-tamkare-iki-kanatli
if want("exr-tamkare-iki-kanatli"):
    a, b, c = 3 * math.sqrt(2), 2 * math.sqrt(3), 3.0
    S = math.acosh(7 / a)
    C = (3.0, -1.0, 0.0)
    f = Fig(-76, 16, [(-5, 0, 0), (11.2, 0, 0), (0, -6, 0), (0, 4, 0), (0, 0, -4.5), (0, 0, 4.7),
                      (10, 3.55, 3.94), (-4, -5.55, -3.94), (10, -5.55, 3.94), (-4, 3.55, -3.94)], width=620)
    for sg in (1, -1):
        hf = lambda s, u, sg=sg: (C[0] + sg * a * math.cosh(s), C[1] + b * math.sinh(s) * math.cos(u),  # noqa: E731
                                  c * math.sinh(s) * math.sin(u))
        f.surface(hf, (0.002, S), (0, TAU), THEORY, nu=24, nv=48, net=(0, 12))
        f.trace(lambda t, hf=hf: hf(S, t), 0, TAU, THEORY, on=dict(width=1.2, opacity=0.75),
                off=dict(width=0.9, dash="4 3", opacity=0.35))
    f.axes(((-5, 11.2), (-6, 4), (-4.5, 4.7)))
    f.vis([(-4.8, C[1], 0), (10.8, C[1], 0)], TEXT, on=dict(width=1.1, dash="6 4", opacity=0.75),
          off=dict(width=1.0, dash="3 3", opacity=0.4))
    for sg in (1, -1):
        f.trace(lambda t, sg=sg: (C[0] + sg * a * math.cosh(t), C[1] + b * math.sinh(t), 0), -S, S, PRACTICE)
    V1, V2 = (C[0] + a, C[1], 0.0), (C[0] - a, C[1], 0.0)
    f.hollow(C, TEXT, 4.0)
    for Q in (V1, V2):
        f.point(Q, TEXT, 4.2)
    f.place(C, it("C") + triple(3, -1, 0), NAME, prefs=["u", "ur", "ul"], d=10, leader=True)
    f.place(V1, it("V") + sub("1"), NAME, prefs=["dl", "d", "ul"], d=7)
    f.place(V2, it("V") + sub("2"), NAME, prefs=["dr", "d", "ur"], d=7)
    f.render(
        "exr-tamkare-iki-kanatli",
        "İki kanatlı hiperboloid (<em>x</em> − 3)²/18 − (<em>y</em> + 1)²/12 − <em>z</em>²/9 = 1, "
        "−4 ≤ <em>x</em> ≤ 10. Merkez <em>C</em>(3, −1, 0) (içi boş nokta; yüzeyde değildir), eksen "
        "<em>C</em>&#8217;den geçen ve <em>x</em>-eksenine paralel kesikli doğrudur. Köşeler "
        "<em>V</em><sub>1</sub>(3 + 3√2, −1, 0) ve <em>V</em><sub>2</sub>(3 − 3√2, −1, 0); kırmızı eğri "
        "<em>z</em> = 0 düzlemindeki hiperbolün kollarıdır.",
        "Two sheeted hyperboloid (x - 3)^2/18 - (y + 1)^2/12 - z^2/9 = 1 with center C(3, -1, 0) drawn "
        "hollow, its axis parallel to the x axis, the vertices V1 and V2, the end ellipses at x = 10 and "
        "x = -4 and the hyperbola in the plane z = 0")

# ============================================================ exr-donel-parabol
if want("exr-donel-parabol"):
    f = Fig(35, 22, [(-2.3, 0, 0), (2.3, 0, 0), (0, -2.3, 0), (0, 2.3, 0), (0, 0, 0), (0, 0, 4.8),
                     (2, 2, 4), (-2, -2, 4)], width=520)
    pf = lambda s, u: (s * math.cos(u), s * math.sin(u), s * s)                 # noqa: E731
    f.surface(pf, (0.002, 2), (0, TAU), THEORY, nu=16, nv=48, net=(0, 8))
    f.axes(((-2.3, 2.3), (-2.3, 2.3), (0, 4.8)))
    for s in (1, 2):
        f.trace(lambda u, s=s: pf(s, u), 0, TAU, BASE)
    f.trace(lambda t: (0, t, t * t), -2, 2, PRACTICE)
    arc = [(1.18 * math.cos(math.radians(a)), 1.18 * math.sin(math.radians(a)), 1.0) for a in range(90, 181, 3)]
    f.line(arc[:-3], TEXT, 1.8, None, 0.95)
    f.arrow(arc[-4], arc[-1], TEXT, 1.8, 9)
    f.point((0, 1, 1), TEXT, 3.8)
    f.point(O3, TEXT, 4.0)
    f.place(O3, it("O"), NAME, prefs=["dl", "l", "d"], d=6)
    f.place((0, 1.75, 1.75 ** 2), eq("z = y²"), DESC, PRACTICE, prefs=["r", "dr", "ur"], d=10, leader=True)
    f.place(pf(1, math.radians(-40)), eq("z = 1"), DESC, BASE, prefs=["r", "dr", "d"], d=10, leader=True)
    f.place(pf(2, math.radians(-40)), eq("z = 4"), DESC, BASE, prefs=["r", "dr", "ur"], d=10)
    f.render(
        "exr-donel-parabol",
        "<em>yz</em>-düzlemindeki <em>z</em> = <em>y</em>² parabolünün (kırmızı) <em>z</em>-ekseni "
        "etrafında döndürülmesiyle oluşan dönel paraboloid <em>z</em> = <em>x</em>² + <em>y</em>², "
        "0 ≤ <em>z</em> ≤ 4. <em>z</em> = 1 ve <em>z</em> = 4 izleri yarıçapları 1 ve 2 olan çemberlerdir "
        "(yeşil); ok, (0, 1, 1) noktasının dönerken izlediği yolu gösterir.",
        "Paraboloid of revolution z = x^2 + y^2 for z from 0 to 4 with the generating parabola z = y^2 "
        "in the yz plane, the circles at z = 1 and z = 4 and a curved arrow along the circle z = 1 "
        "starting at (0, 1, 1)")

# ============================================================ exr-egik-parabolik-silindir
if want("exr-egik-parabolik-silindir"):
    X = 1.6
    f = Fig(35, 20, [(-2.2, 0, 0), (2.2, 0, 0), (0, -0.5, 0), (0, 6.6, 0), (0, 0, -0.5), (0, 0, 2.8),
                     (X, X * X + 2, 2), (-X, X * X + 2, 2)], width=600)
    ps = lambda x, z: (x, x * x + z, z)                                          # noqa: E731
    f.surface(ps, (-X, X), (0, 2), THEORY, nu=32, nv=8, net=(8, 0))
    for zz in (1, 2):
        f.trace(lambda t, zz=zz: ps(t, zz), -X, X, THEORY, on=dict(width=1.3, opacity=0.8),
                off=dict(width=1.0, dash="4 3", opacity=0.4))
    f.axes(((-2.2, 2.2), (-0.5, 6.6), (-0.5, 2.8)))
    f.trace(lambda t: ps(t, 0), -X, X, PRACTICE)
    P0, P1 = (1.0, 1.0, 0.0), (1.0, 3.0, 2.0)
    f.vis([P0, P1], THEORY, on=dict(width=2.6, opacity=1.0))
    f.point(P0, TEXT, 3.6)
    f.point(P1, TEXT, 4.4)
    V0 = (-1.2, 4.6, 0.6)
    f.arrow(V0, vadd(V0, (0, 1.0, 1.0)), TEXT, 2.2, 10)
    f.place(P1, triple(1, 3, 2), NAME, prefs=["ur", "u", "r"], d=8)
    f.place(ps(-1.35, 0), "Γ: " + eq("y = x²"), DESC, PRACTICE, prefs=["dl", "l", "d"], d=10, leader=True)
    f.place(vadd(V0, (0, 0.5, 0.5)), it("v") + " = (0, 1, 1)", DESC, prefs=["r", "dr", "ur"], d=9)
    f.render(
        "exr-egik-parabolik-silindir",
        "Eğik parabolik silindir <em>y</em> − <em>z</em> = <em>x</em>², |<em>x</em>| ≤ 1,6, "
        "0 ≤ <em>z</em> ≤ 2. Dayanak parabolü Γ (kırmızı) <em>xy</em>-düzlemindedir; <em>z</em> = 1 ve "
        "<em>z</em> = 2 kesitleri <em>y</em> doğrultusunda kaymış <em>y</em> = <em>x</em>² + 1 ve "
        "<em>y</em> = <em>x</em>² + 2 parabolleridir. Kalın üreteç (1, 1, 0)&#8217;dan "
        "<em>v</em> = (0, 1, 1) doğrultusunda (1, 3, 2)&#8217;ye gider.",
        "Oblique parabolic cylinder y - z = x^2 for |x| up to 1.6 and z from 0 to 2 with the base "
        "parabola Gamma in the xy plane, the shifted parabolas at z = 1 and z = 2, generators in the "
        "direction (0, 1, 1) and the bold generator from (1, 1, 0) to (1, 3, 2)")

# ============================================================ (end of figures)
for name, body in OUT.items():
    (OUT_DIR / f"analytic-oyz-{name}.md").write_text(body, encoding="utf-8", newline="\n")
print(f"{len(OUT)} figures written")
