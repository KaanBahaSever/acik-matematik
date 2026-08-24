# -*- coding: utf-8 -*-
"""Dependency-free, theme-aware SVG plotting helper.

All colors are CSS custom properties defined in styles/global.css, so one
piece of markup renders correctly in both the light and the dark theme.

Figures are NOT generated at build time. A figure script (for example
stochastic_figures.py or complex_figures.py) imports this module, writes
the finished markup to scripts/_figures/, and the markup is pasted into the
.qmd sources by hand. Building the books therefore needs only Quarto.
"""
import math

TEXT     = "var(--academic-text)"
BG       = "var(--academic-bg)"      # page background — for "hollow" fills that must hide what is beneath
THEORY   = "var(--color-theory)"
PRACTICE = "var(--color-practice)"
BASE     = "var(--color-base)"
REMARK   = "var(--color-remark)"


def fmt(v):
    """Compact number formatting for tick labels: 2.50 -> '2.5', -0.0 -> '0'."""
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return s if s not in ("-0", "") else "0"


def _style(bold, italic):
    weight = ' font-weight="600"' if bold else ""
    slant = ' font-style="italic"' if italic else ""
    return weight + slant


class Plot:
    """A single Cartesian panel mapped onto a rectangle of the SVG canvas.

    (x0, y0) is the top-left corner of the panel in pixels, w/h its size,
    xrange/yrange the data intervals shown. Data y grows upward.
    """

    def __init__(self, x0, y0, w, h, xrange, yrange):
        self.x0, self.y0, self.w, self.h = x0, y0, w, h
        self.xmin, self.xmax = xrange
        self.ymin, self.ymax = yrange
        self.parts = []

    # -- coordinate mapping -------------------------------------------------
    def X(self, x):
        return self.x0 + (x - self.xmin) / (self.xmax - self.xmin) * self.w

    def Y(self, y):
        return self.y0 + self.h - (y - self.ymin) / (self.ymax - self.ymin) * self.h

    def P(self, x, y):
        """Data point -> 'px,py' string."""
        return f"{self.X(x):.1f},{self.Y(y):.1f}"

    def R(self, r):
        """Data length -> pixels along the x axis (use with equal aspect)."""
        return r / (self.xmax - self.xmin) * self.w

    def add(self, s):
        self.parts.append(s)

    # -- frames and axes ----------------------------------------------------
    def axes(self, xticks, yticks, xlabel="", ylabel="", xfmt=fmt, yfmt=fmt):
        """L-shaped axes along the bottom and left edges of the panel."""
        a = [f'<g stroke="{TEXT}" stroke-width="1.1" opacity="0.45">',
             f'<line x1="{self.x0:.1f}" y1="{self.y0+self.h:.1f}" x2="{self.x0+self.w+8:.1f}" y2="{self.y0+self.h:.1f}"/>',
             f'<line x1="{self.x0:.1f}" y1="{self.y0-8:.1f}" x2="{self.x0:.1f}" y2="{self.y0+self.h:.1f}"/>',
             '</g>']
        a.append(f'<g fill="{TEXT}" font-size="11" opacity="0.7">')
        for t in xticks:
            a.append(f'<text x="{self.X(t):.1f}" y="{self.y0+self.h+16:.1f}" text-anchor="middle">{xfmt(t)}</text>')
        for t in yticks:
            a.append(f'<text x="{self.x0-7:.1f}" y="{self.Y(t)+4:.1f}" text-anchor="end">{yfmt(t)}</text>')
        if xlabel:
            a.append(f'<text x="{self.x0+self.w+14:.1f}" y="{self.y0+self.h+4:.1f}" font-style="italic">{xlabel}</text>')
        if ylabel:
            a.append(f'<text x="{self.x0-4:.1f}" y="{self.y0-14:.1f}" text-anchor="middle" font-style="italic">{ylabel}</text>')
        a.append('</g>')
        self.add("\n  ".join(a))

    def origin_axes(self, xlabel="Re", ylabel="Im", xticks=(), yticks=(),
                    xfmt=fmt, yfmt=fmt, opacity=0.5):
        """Axes crossing at the data origin with arrowheads — the complex plane."""
        ox, oy = self.X(0), self.Y(0)
        left, right = self.x0 - 4, self.x0 + self.w + 4
        top, bottom = self.y0 - 4, self.y0 + self.h + 4
        a = [f'<g stroke="{TEXT}" stroke-width="1.1" opacity="{opacity}" fill="{TEXT}">',
             f'<line x1="{left:.1f}" y1="{oy:.1f}" x2="{right:.1f}" y2="{oy:.1f}"/>',
             f'<line x1="{ox:.1f}" y1="{bottom:.1f}" x2="{ox:.1f}" y2="{top:.1f}"/>',
             f'<polygon points="{right:.1f},{oy:.1f} {right-8:.1f},{oy-3.5:.1f} {right-8:.1f},{oy+3.5:.1f}" stroke="none"/>',
             f'<polygon points="{ox:.1f},{top:.1f} {ox-3.5:.1f},{top+8:.1f} {ox+3.5:.1f},{top+8:.1f}" stroke="none"/>',
             '</g>',
             f'<g fill="{TEXT}" font-size="11" opacity="0.7">']
        for t in xticks:
            a.append(f'<line x1="{self.X(t):.1f}" y1="{oy-3:.1f}" x2="{self.X(t):.1f}" y2="{oy+3:.1f}" stroke="{TEXT}" stroke-width="1"/>')
            a.append(f'<text x="{self.X(t):.1f}" y="{oy+15:.1f}" text-anchor="middle">{xfmt(t)}</text>')
        for t in yticks:
            a.append(f'<line x1="{ox-3:.1f}" y1="{self.Y(t):.1f}" x2="{ox+3:.1f}" y2="{self.Y(t):.1f}" stroke="{TEXT}" stroke-width="1"/>')
            a.append(f'<text x="{ox-7:.1f}" y="{self.Y(t)+4:.1f}" text-anchor="end">{yfmt(t)}</text>')
        a.append('</g>')
        a.append(f'<g fill="{TEXT}" font-size="11.5" font-style="italic" opacity="0.85">')
        if xlabel:
            a.append(f'<text x="{right-2:.1f}" y="{oy+15:.1f}" text-anchor="end">{xlabel}</text>')
        if ylabel:
            a.append(f'<text x="{ox+7:.1f}" y="{top+9:.1f}">{ylabel}</text>')
        a.append('</g>')
        self.add("\n  ".join(a))

    def grid(self, xs=(), ys=()):
        a = [f'<g stroke="{TEXT}" stroke-width="0.7" opacity="0.13">']
        for x in xs:
            a.append(f'<line x1="{self.X(x):.1f}" y1="{self.y0:.1f}" x2="{self.X(x):.1f}" y2="{self.y0+self.h:.1f}"/>')
        for y in ys:
            a.append(f'<line x1="{self.x0:.1f}" y1="{self.Y(y):.1f}" x2="{self.x0+self.w:.1f}" y2="{self.Y(y):.1f}"/>')
        a.append('</g>')
        self.add("".join(a))

    # -- marks --------------------------------------------------------------
    def line(self, pts, color=THEORY, width=1.9, dash=None, opacity=1.0):
        d = " ".join(("M" if i == 0 else "L") + self.P(x, y) for i, (x, y) in enumerate(pts))
        da = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}"{da} opacity="{opacity}" stroke-linejoin="round" stroke-linecap="round"/>')

    def points(self, pts, color=PRACTICE, r=4.0):
        for x, y in pts:
            self.add(f'<circle cx="{self.X(x):.1f}" cy="{self.Y(y):.1f}" r="{r}" fill="{color}"/>')

    def hollow_points(self, pts, color=PRACTICE, r=4.0):
        for x, y in pts:
            self.add(f'<circle cx="{self.X(x):.1f}" cy="{self.Y(y):.1f}" r="{r}" fill="none" stroke="{color}" stroke-width="1.8"/>')

    def bars(self, pts, color=THEORY, width=7, opacity=0.85):
        for x, y in pts:
            X, Y0, Y1 = self.X(x), self.Y(0), self.Y(y)
            self.add(f'<rect x="{X-width/2:.1f}" y="{Y1:.1f}" width="{width}" height="{Y0-Y1:.1f}" fill="{color}" opacity="{opacity}" rx="1.5"/>')

    def vline(self, x, y1, y2, color=TEXT, dash="4 3", opacity=0.5):
        self.add(f'<line x1="{self.X(x):.1f}" y1="{self.Y(y1):.1f}" x2="{self.X(x):.1f}" y2="{self.Y(y2):.1f}" stroke="{color}" stroke-width="1" stroke-dasharray="{dash}" opacity="{opacity}"/>')

    def circle(self, cx, cy, r, color=THEORY, width=1.6, dash=None, fill="none", opacity=1.0):
        """Circle with center (cx, cy) and radius r in data units (equal aspect)."""
        da = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<circle cx="{self.X(cx):.1f}" cy="{self.Y(cy):.1f}" r="{self.R(r):.1f}" fill="{fill}" stroke="{color}" stroke-width="{width}"{da} opacity="{opacity}"/>')

    def arc(self, cx, cy, r, a0, a1, color=THEORY, width=1.4, dash=None, opacity=1.0, samples=48):
        """Circular arc from angle a0 to a1 (radians, counter-clockwise)."""
        pts = [(cx + r * math.cos(a0 + (a1 - a0) * k / samples),
                cy + r * math.sin(a0 + (a1 - a0) * k / samples)) for k in range(samples + 1)]
        self.line(pts, color, width, dash, opacity)

    def sector(self, cx, cy, r, a0, a1, color=THEORY, opacity=0.16, samples=48):
        """Filled pie wedge — the usual way to shade an angle."""
        pts = [(cx, cy)] + [(cx + r * math.cos(a0 + (a1 - a0) * k / samples),
                            cy + r * math.sin(a0 + (a1 - a0) * k / samples)) for k in range(samples + 1)]
        self.polygon(pts, color, opacity, stroke="none")

    def polygon(self, pts, fill=THEORY, opacity=0.16, stroke="none", width=1.2, dash=None):
        d = " ".join(self.P(x, y) for x, y in pts)
        da = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<polygon points="{d}" fill="{fill}" fill-opacity="{opacity}" stroke="{stroke}" stroke-width="{width}"{da}/>')

    def arrow(self, p0, p1, color=THEORY, width=1.9, head=8.0, dash=None, opacity=1.0):
        """Straight arrow from data point p0 to p1 with a filled arrowhead."""
        x0, y0, x1, y1 = self.X(p0[0]), self.Y(p0[1]), self.X(p1[0]), self.Y(p1[1])
        dx, dy = x1 - x0, y1 - y0
        length = math.hypot(dx, dy) or 1.0
        ux, uy = dx / length, dy / length
        # shorten the shaft so it does not poke through the head
        sx, sy = x1 - ux * head * 0.8, y1 - uy * head * 0.8
        da = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{sx:.1f}" y2="{sy:.1f}" stroke="{color}" stroke-width="{width}"{da} opacity="{opacity}" stroke-linecap="round"/>')
        px, py = -uy, ux
        hw = head * 0.42
        self.add(f'<polygon points="{x1:.1f},{y1:.1f} {x1-ux*head+px*hw:.1f},{y1-uy*head+py*hw:.1f} {x1-ux*head-px*hw:.1f},{y1-uy*head-py*hw:.1f}" fill="{color}" opacity="{opacity}"/>')

    def text(self, x, y, s, color=TEXT, size=11.5, anchor="start", bold=False, italic=False):
        self.add(f'<text x="{self.X(x):.1f}" y="{self.Y(y):.1f}" fill="{color}" font-size="{size}" text-anchor="{anchor}"{_style(bold, italic)}>{s}</text>')

    def text_px(self, px, py, s, color=TEXT, size=11.5, anchor="start", bold=False, italic=False):
        self.add(f'<text x="{px:.1f}" y="{py:.1f}" fill="{color}" font-size="{size}" text-anchor="{anchor}"{_style(bold, italic)}>{s}</text>')

    def label(self, x, y, s, dx=0, dy=0, color=TEXT, size=11.5, anchor="start", bold=False, italic=False):
        """Text placed at a data point, nudged by (dx, dy) pixels."""
        self.text_px(self.X(x) + dx, self.Y(y) + dy, s, color, size, anchor, bold, italic)

    def svg(self):
        return "\n  ".join(self.parts)


WIDE = "ders-grafik ders-grafik-genis"   # css class for two-panel figures


def figure(W, H, panels, caption, css_class="ders-grafik", aria=""):
    """Wrap the panels in the <figure> markup the .qmd sources embed."""
    body = "\n  ".join(p.svg() for p in panels)
    return (f'```{{=html}}\n'
            f'<figure class="{css_class}">\n'
            f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="{aria}">\n  '
            f'{body}\n</svg>\n'
            f'<figcaption>{caption}</figcaption>\n</figure>\n```\n')


# ---------------------------------------------------------------------------
# Complex-plane conveniences
# ---------------------------------------------------------------------------
PI = math.pi

# HTML entities for symbols that appear inside <text> (plain UTF-8 works too)
PI_S, THETA, MINUS, TIMES, INFTY = "&#960;", "&#952;", "&#8722;", "&#183;", "&#8734;"
SUB0, SUB1, SUB2, SUB3 = "&#8320;", "&#8321;", "&#8322;", "&#8323;"
APPROX, LEQ, GEQ, NEQ, IN, BAR_Z = "&#8776;", "&#8804;", "&#8805;", "&#8800;", "&#8712;", "z&#773;"


def cplane(x0, y0, width, xrange, yrange):
    """A complex-plane panel with equal aspect (same pixels per unit on both axes)."""
    ppu = width / (xrange[1] - xrange[0])
    return Plot(x0, y0, width, (yrange[1] - yrange[0]) * ppu, xrange, yrange)


def polar(r, a):
    return (r * math.cos(a), r * math.sin(a))


def spiral(p, a0, a1, r0, r1, color, width=1.6, head=True, samples=90):
    """Arc whose radius grows linearly with the angle — lets multi-turn sweeps stay legible."""
    pts = [polar(r0 + (r1 - r0) * k / samples, a0 + (a1 - a0) * k / samples) for k in range(samples + 1)]
    p.line(pts[:-1], color, width)
    if head:
        p.arrow(pts[-3], pts[-1], color, width, head=7.0)


def angle_arc(p, a0, a1, r, color, width=1.6, head=True):
    """Angle marker: circular arc of radius r from angle a0 to a1 (radians) with an arrowhead."""
    spiral(p, a0, a1, r, r, color, width, head)


def dot(p, z, color=TEXT, r=3.6):
    p.points([z], color, r)


def cross(p, z, color=PRACTICE, size=4.0, width=1.6):
    """An × mark — the customary symbol for a singular point."""
    X, Y = p.X(z[0]), p.Y(z[1])
    p.add(f'<path d="M{X-size:.1f},{Y-size:.1f} L{X+size:.1f},{Y+size:.1f} M{X-size:.1f},{Y+size:.1f} L{X+size:.1f},{Y-size:.1f}" '
          f'stroke="{color}" stroke-width="{width}" stroke-linecap="round"/>')


def hollow(p, z, color=TEXT, r=3.6, width=1.6):
    """An open point filled with the page background — an excluded point such as a puncture."""
    p.add(f'<circle cx="{p.X(z[0]):.1f}" cy="{p.Y(z[1]):.1f}" r="{r}" fill="{BG}" stroke="{color}" stroke-width="{width}"/>')


def closed_curve(p, points, color=THEORY, width=1.8, dash=None, fill="none", opacity=0.14, arrow_at=None):
    """Closed polyline through data points; optional shading and an arrowhead placed at index arrow_at."""
    if fill != "none":
        p.polygon(points, fill, opacity, stroke="none")
    p.line(list(points) + [points[0]], color, width, dash)
    if arrow_at is not None:
        i = arrow_at % len(points)
        p.arrow(points[i - 1], points[i], color, width, head=8.0)


def blob(cx, cy, base_r, wobble=(), samples=120):
    """Points of a smooth 'potato' curve r(t) = base_r + sum(a*cos(k t + phase)); wobble = [(a, k, phase), ...]."""
    pts = []
    for s in range(samples):
        t = 2 * PI * s / samples
        r = base_r + sum(a * math.cos(k * t + ph) for a, k, ph in wobble)
        pts.append((cx + r * math.cos(t), cy + r * math.sin(t)))
    return pts


def circle_pts(cx, cy, r, a0=0.0, a1=2 * PI, samples=96):
    """Points along a circular arc (data coordinates)."""
    return [(cx + r * math.cos(a0 + (a1 - a0) * k / samples), cy + r * math.sin(a0 + (a1 - a0) * k / samples))
            for k in range(samples + 1)]


def annulus_fill(p, cx, cy, r_in, r_out, color=THEORY, opacity=0.10):
    """Shade the ring r_in < |z - c| < r_out (even-odd fill)."""
    def ring(r, sweep):
        return (f'M{p.X(cx + r):.1f},{p.Y(cy):.1f} A{p.R(r):.1f},{p.R(r):.1f} 0 1,{sweep} {p.X(cx - r):.1f},{p.Y(cy):.1f} '
                f'A{p.R(r):.1f},{p.R(r):.1f} 0 1,{sweep} {p.X(cx + r):.1f},{p.Y(cy):.1f} Z')
    p.add(f'<path d="{ring(r_out, 0)} {ring(r_in, 1)}" fill="{color}" fill-opacity="{opacity}" fill-rule="evenodd" stroke="none"/>')


def disk_fill(p, cx, cy, r, color=THEORY, opacity=0.10):
    p.add(f'<circle cx="{p.X(cx):.1f}" cy="{p.Y(cy):.1f}" r="{p.R(r):.1f}" fill="{color}" fill-opacity="{opacity}" stroke="none"/>')


def exterior_fill(p, cx, cy, r, color=THEORY, opacity=0.10):
    """Shade everything in the panel outside the circle |z - c| = r."""
    x0, y0, x1, y1 = p.x0 - 4, p.y0 - 4, p.x0 + p.w + 4, p.y0 + p.h + 4
    rr = p.R(r)
    p.add(f'<path d="M{x0:.1f},{y0:.1f} H{x1:.1f} V{y1:.1f} H{x0:.1f} Z '
          f'M{p.X(cx) + rr:.1f},{p.Y(cy):.1f} A{rr:.1f},{rr:.1f} 0 1,1 {p.X(cx) - rr:.1f},{p.Y(cy):.1f} '
          f'A{rr:.1f},{rr:.1f} 0 1,1 {p.X(cx) + rr:.1f},{p.Y(cy):.1f} Z" '
          f'fill="{color}" fill-opacity="{opacity}" fill-rule="evenodd" stroke="none"/>')


def sup(s, size=9):
    """Superscript inside an SVG <text>: 'e' + sup('i&#960;/6')."""
    # the zero-width space carries the baseline reset without eating the caller's own spaces
    return f'<tspan font-size="{size}" dy="-5">{s}</tspan><tspan dy="5">&#8203;</tspan>'


def panel_title(p, s, color=TEXT, size=11.5):
    """Bold title centred above a panel."""
    p.text_px(p.x0 + p.w / 2, p.y0 - 8, s, color, size, "middle", True)
