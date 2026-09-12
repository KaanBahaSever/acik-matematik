# -*- coding: utf-8 -*-
"""Orthographic 3-D drawing on top of svg_plot.Plot.

A Camera maps space points (x, y, z) to the 2-D data coordinates of a Plot
panel; the panel must have the same pixels-per-unit on both axes (build it
with space_panel()) or the projection is distorted. Depth along the viewing
direction is kept so that the faces of a surface can be painted back to front.

Conventions: right-handed axes, z points up on the page. With the default
camera the x axis comes toward the viewer (down-left), y goes to the right,
z goes up — the usual textbook view of R^3.

Everything is theme-aware because the colors are the CSS custom properties
of svg_plot; the output is plain SVG paths, polygons, circles and text, which
the PDF export (export_figures.lua + Typst) renders as well.
"""
import math

from svg_plot import Plot, TEXT, THEORY, PRACTICE, BASE, BG, fmt, hollow as _hollow

# ---------------------------------------------------------------------------
# small vector algebra on 3-tuples
# ---------------------------------------------------------------------------


def vadd(a, b):
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def vsub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def vscale(c, a):
    return (c * a[0], c * a[1], c * a[2])


def vdot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def vcross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def vnorm(a):
    return math.sqrt(vdot(a, a))


def vunit(a):
    n = vnorm(a)
    return a if n == 0 else vscale(1.0 / n, a)


def space_panel(x0, y0, w, xrange, yrange):
    """A panel with equal aspect: same pixels per unit horizontally and vertically."""
    ppu = w / (xrange[1] - xrange[0])
    return Plot(x0, y0, w, (yrange[1] - yrange[0]) * ppu, xrange, yrange)


class Camera:
    """Orthographic camera looking at `center` from the given azimuth and
    elevation (degrees). Azimuth is measured in the xy plane from the +x axis
    toward +y; elevation is the angle above the xy plane."""

    def __init__(self, azimuth=35.0, elevation=22.0, scale=1.0, center=(0.0, 0.0, 0.0)):
        az, el = math.radians(azimuth), math.radians(elevation)
        # unit vector from the scene toward the viewer
        self.d = (math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el))
        # page-right and page-up directions (both orthogonal to d)
        self.r = (-math.sin(az), math.cos(az), 0.0)
        self.u = (-math.sin(el) * math.cos(az), -math.sin(el) * math.sin(az), math.cos(el))
        self.scale = scale
        self.center = center

    def project(self, P):
        """Space point -> (X, Y, depth); larger depth is closer to the viewer."""
        q = vsub(P, self.center)
        return (vdot(q, self.r) * self.scale, vdot(q, self.u) * self.scale, vdot(q, self.d))


class Space:
    """Draw 3-D objects on a Plot panel through a Camera.

    Objects are emitted in call order (painter's algorithm by the author);
    surface() sorts its own faces back to front.
    """

    def __init__(self, plot, camera=None):
        self.p = plot
        self.cam = camera or Camera()

    # -- projection ---------------------------------------------------------
    def pt(self, P):
        X, Y, _ = self.cam.project(P)
        return (X, Y)

    def pts(self, Ps):
        return [self.pt(P) for P in Ps]

    def depth(self, P):
        return self.cam.project(P)[2]

    # -- curves and lines ---------------------------------------------------
    def line(self, Ps, color=THEORY, width=1.9, dash=None, opacity=1.0):
        self.p.line(self.pts(Ps), color, width, dash, opacity)

    def guide(self, Ps, color=TEXT, opacity=0.5, width=1.0, dash="4 3"):
        """Thin dashed helper line through space points."""
        self.p.line(self.pts(Ps), color, width, dash, opacity)

    def curve(self, f, t0, t1, color=THEORY, width=1.9, samples=200, dash=None, opacity=1.0):
        """Parametric space curve t -> f(t) = (x, y, z) on [t0, t1]."""
        pts = [f(t0 + (t1 - t0) * k / samples) for k in range(samples + 1)]
        self.line(pts, color, width, dash, opacity)

    def segment_arrow(self, f, t0, t1, color=THEORY, width=1.9, head=8.0, samples=200):
        """Parametric curve with an arrowhead at its end (direction of travel)."""
        pts = [f(t0 + (t1 - t0) * k / samples) for k in range(samples + 1)]
        self.line(pts[:-2], color, width)
        self.arrow(pts[-3], pts[-1], color, width, head)

    def arrow(self, P0, P1, color=THEORY, width=1.9, head=8.0, dash=None, opacity=1.0):
        self.p.arrow(self.pt(P0), self.pt(P1), color, width, head, dash, opacity)

    def circle(self, C, e1, e2, r, color=THEORY, width=1.6, dash=None, samples=96, opacity=1.0):
        """Circle of radius r about C in the plane spanned by the orthonormal pair e1, e2."""
        def f(t):
            return vadd(C, vadd(vscale(r * math.cos(t), e1), vscale(r * math.sin(t), e2)))
        self.curve(f, 0.0, 2 * math.pi, color, width, samples, dash, opacity)

    # -- points and text ----------------------------------------------------
    def point(self, P, color=TEXT, r=3.6):
        self.p.points([self.pt(P)], color, r)

    def hollow(self, P, color=TEXT, r=3.6, width=1.6):
        _hollow(self.p, self.pt(P), color, r, width)

    def label(self, P, s, dx=0, dy=0, color=TEXT, size=11.5, anchor="start", bold=False, italic=False):
        X, Y = self.pt(P)
        self.p.label(X, Y, s, dx, dy, color, size, anchor, bold, italic)

    # -- regions ------------------------------------------------------------
    def polygon(self, Ps, fill=THEORY, opacity=0.16, stroke="none", width=1.2, dash=None):
        self.p.polygon(self.pts(Ps), fill, opacity, stroke, width, dash)

    def parallelogram(self, P, e1, e2, s1=(-1.0, 1.0), s2=(-1.0, 1.0), fill=THEORY, opacity=0.14,
                      stroke="none", width=1.2, dash=None):
        """The patch {P + a e1 + b e2 : a in s1, b in s2} — a piece of a plane."""
        a0, a1 = s1
        b0, b1 = s2
        corners = [vadd(P, vadd(vscale(a, e1), vscale(b, e2)))
                   for a, b in ((a0, b0), (a1, b0), (a1, b1), (a0, b1))]
        self.polygon(corners, fill, opacity, stroke, width, dash)

    def surface(self, f, urange, vrange, nu=16, nv=16, fill=THEORY, stroke=THEORY,
                opacity=(0.05, 0.26), stroke_width=0.6, stroke_opacity=0.5,
                light=(-0.35, -0.55, 0.76)):
        """Shaded, wire-framed parametric surface (u, v) -> f(u, v).

        Each quad is filled with `fill`; its fill-opacity is interpolated in
        `opacity` by the angle between the face normal and `light`, which
        gives a soft relief without hard-coding colors. Faces are painted
        back to front.
        """
        u0, u1 = urange
        v0, v1 = vrange
        grid = [[f(u0 + (u1 - u0) * i / nu, v0 + (v1 - v0) * j / nv) for j in range(nv + 1)]
                for i in range(nu + 1)]
        L = vunit(light)
        faces = []
        for i in range(nu):
            for j in range(nv):
                a, b, c, d = grid[i][j], grid[i + 1][j], grid[i + 1][j + 1], grid[i][j + 1]
                n = vunit(vcross(vsub(c, a), vsub(d, b)))
                shade = 0.5 * (1.0 + abs(vdot(n, L)))
                dep = sum(self.depth(q) for q in (a, b, c, d)) / 4.0
                faces.append((dep, (a, b, c, d), shade))
        faces.sort(key=lambda t: t[0])
        lo, hi = opacity
        for _, quad, shade in faces:
            op = lo + (hi - lo) * shade
            pts = " ".join(self.p.P(*self.pt(q)) for q in quad)
            self.p.add(f'<polygon points="{pts}" fill="{fill}" fill-opacity="{op:.3f}" '
                       f'stroke="{stroke}" stroke-width="{stroke_width}" stroke-opacity="{stroke_opacity}" '
                       f'stroke-linejoin="round"/>')

    def wire(self, f, urange, vrange, nu=8, nv=8, color=THEORY, width=0.8, opacity=0.6, samples=24):
        """Only the coordinate lines of a parametric surface (no shading)."""
        u0, u1 = urange
        v0, v1 = vrange
        for i in range(nu + 1):
            u = u0 + (u1 - u0) * i / nu
            self.curve(lambda v, u=u: f(u, v), v0, v1, color, width, samples, None, opacity)
        for j in range(nv + 1):
            v = v0 + (v1 - v0) * j / nv
            self.curve(lambda u, v=v: f(u, v), u0, u1, color, width, samples, None, opacity)

    def floor_grid(self, xrange, yrange, n=6, z=0.0, color=TEXT, opacity=0.12, width=0.7):
        """Faint grid on the plane z = const, for spatial reference."""
        x0, x1 = xrange
        y0, y1 = yrange
        for i in range(n + 1):
            x = x0 + (x1 - x0) * i / n
            self.line([(x, y0, z), (x, y1, z)], color, width, None, opacity)
            y = y0 + (y1 - y0) * i / n
            self.line([(x0, y, z), (x1, y, z)], color, width, None, opacity)

    # -- axes and coordinate guides ----------------------------------------
    def axes(self, xmax, ymax, zmax, xmin=0.0, ymin=0.0, zmin=0.0, labels=("x", "y", "z"),
             color=TEXT, opacity=0.55, width=1.1, head=7.0, size=11.5, offsets=None):
        """Coordinate axes as arrows through the origin, labelled past their tips."""
        O = (0.0, 0.0, 0.0)
        ends = [((xmin, 0, 0), (xmax, 0, 0)), ((0, ymin, 0), (0, ymax, 0)), ((0, 0, zmin), (0, 0, zmax))]
        offs = offsets or ((-4, 13), (10, 4), (-10, -4))
        for k, (a, b) in enumerate(ends):
            if a != O:
                self.line([a, O], color, width, None, opacity)
            self.arrow(O, b, color, width, head, None, opacity)
            if labels and labels[k]:
                dx, dy = offs[k]
                self.label(b, labels[k], dx, dy, color, size, "middle", False, True)

    def ticks(self, axis, values, fmt_=fmt, size=10, color=TEXT, opacity=0.7, length=0.08,
              offset=None):
        """Small tick marks on a coordinate axis ('x', 'y' or 'z') with labels."""
        k = "xyz".index(axis)
        # tick direction: y-ward for the x axis, x-ward for the y axis, x-ward for the z axis
        tdir = {"x": (0, 1, 0), "y": (1, 0, 0), "z": (1, 0, 0)}[axis]
        dx, dy = offset or {"x": (-8, 10), "y": (0, 13), "z": (-9, 4)}[axis]
        for v in values:
            P = [0.0, 0.0, 0.0]
            P[k] = v
            P = tuple(P)
            a = vadd(P, vscale(-length / 2, tdir))
            b = vadd(P, vscale(length / 2, tdir))
            self.line([a, b], color, 1.0, None, opacity)
            self.label(P, fmt_(v), dx, dy, color, size, "middle" if axis != "z" else "end")

    def coordinate_box(self, P, color=TEXT, opacity=0.45, width=1.0, dash="4 3", to_z_axis=True):
        """Dashed guides that read off the coordinates of P: the L on the floor
        and the vertical riser; optionally the horizontal guide to the z axis."""
        x, y, z = P
        self.guide([(x, 0, 0), (x, y, 0), (0, y, 0)], color, opacity, width, dash)
        self.guide([(x, y, 0), P], color, opacity, width, dash)
        if to_z_axis:
            self.guide([P, (0, 0, z)], color, opacity, width, dash)

    def drop(self, P, z0=0.0, color=TEXT, opacity=0.45, width=1.0, dash="4 3", mark=True):
        """Dashed vertical from P down to the plane z = z0, with a small foot mark."""
        x, y, z = P
        self.guide([P, (x, y, z0)], color, opacity, width, dash)
        if mark:
            self.point((x, y, z0), color, 2.2)


__all__ = ["Camera", "Space", "space_panel", "vadd", "vsub", "vscale", "vdot", "vcross",
           "vnorm", "vunit"]
