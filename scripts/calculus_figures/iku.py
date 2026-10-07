# -*- coding: utf-8 -*-
"""
Figures of the chapter "İki Katlı İntegralin Uygulamaları"
(dersler/integral-calculus/iki-katli-integralin-uygulamalari.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise); a concept figure sits in plain text right under the paragraph or
the definition box it illustrates, never inside a definition box and never
directly under a heading. The figures are NOT produced at build time. Run

    python scripts/calculus_figures/iku.py
    python scripts/center_figures.py "calculus-iku-*.md"
    python scripts/check_figure_labels.py "scripts/_figures/calculus-iku-*.md"

and paste the markup of scripts/_figures/calculus-iku-<name>.md into the .qmd.
Captions are Turkish on purpose; aria labels are plain ASCII.

Densities are drawn as tints: a region is cut into small cells and every
cell is filled with a translucent color whose opacity grows with the density
at its center (no color scale, no clip paths).
"""
import html
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, dot, hollow, TEXT, THEORY, PRACTICE, BASE, BG  # noqa: E402
from svg_plot3 import Camera, Space  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "calculus-iku-"

MINUS = "&#8722;"
PI = "&#960;"
RHO = "&#961;"
DELTA = "&#916;"
BARX = "<tspan font-style=\"italic\">x</tspan>&#773;"
BARY = "<tspan font-style=\"italic\">y</tspan>&#773;"
ZWSP = chr(0x200B)


def save(name, markup):
    (OUT_DIR / f"{PREFIX}{name}.md").write_text(markup, encoding="utf-8", newline="\n")
    print(f"{PREFIX}{name}.md")


def it(s):
    """Italic run inside an SVG <text>."""
    return f'<tspan font-style="italic">{s}</tspan>'


def sub(s, size=8.5):
    """Subscript inside an SVG <text>."""
    return f'<tspan font-size="{size}" dy="3.5">{s}</tspan><tspan dy="-3.5">&#8203;</tspan>'


def sup(s, size=8.5):
    """Superscript inside an SVG <text>."""
    return f'<tspan font-size="{size}" dy="-5">{s}</tspan><tspan dy="5">&#8203;</tspan>'


def eq_plot(x0, y0, ppu, xr, yr):
    """Panel with the same number of pixels per unit on both axes."""
    return Plot(x0, y0, (xr[1] - xr[0]) * ppu, (yr[1] - yr[0]) * ppu, xr, yr)


def fit_space(cam, pts, x0, y0, ppu, pad=0.12):
    """Equal-aspect panel just large enough for the projections of pts."""
    q = [cam.project(P)[:2] for P in pts]
    xr = (min(a for a, _ in q) - pad, max(a for a, _ in q) + pad)
    yr = (min(b for _, b in q) - pad, max(b for _, b in q) + pad)
    plot = eq_plot(x0, y0, ppu, xr, yr)
    return plot, Space(plot, cam)


def text_w(s, size):
    """Rough advance width of a label (0.43 em per visible character, tspans at their own size)."""
    def count(t):
        return len(html.unescape(re.sub(r"<[^>]+>", "", t)).replace(ZWSP, "").replace("̅", ""))
    width = 0.0
    for m in re.finditer(r'<tspan font-size="([\d.]+)"[^>]*>(.*?)</tspan>', s):
        width += count(m.group(2)) * 0.43 * float(m.group(1))
    rest = re.sub(r'<tspan font-size="[\d.]+"[^>]*>.*?</tspan>', "", s)
    return width + count(rest) * 0.43 * size


def plabel(p, x, y, s, dx=0, dy=0, color=TEXT, size=11.5, anchor="start", bold=False):
    """Label on a page-coloured plate, for text that must sit on a tinted region or a mesh."""
    px, py = p.X(x) + dx, p.Y(y) + dy
    w = text_w(s, size)
    x0 = px - (w / 2 if anchor == "middle" else w if anchor == "end" else 0)
    p.add(f'<rect x="{x0 - 2.5:.1f}" y="{py - 0.8 * size - 1:.1f}" width="{w + 5:.1f}" '
          f'height="{size + 3:.1f}" rx="3" fill="{BG}" opacity="0.85"/>')
    p.label(x, y, s, dx, dy, color, size, anchor, bold)


def splabel(S, P, s, dx=0, dy=0, color=TEXT, size=11.5, anchor="start", bold=False):
    """plabel() at a space point."""
    X, Y = S.pt(P)
    plabel(S.p, X, Y, s, dx, dy, color, size, anchor, bold)


def clip_convex(poly, window):
    """Sutherland-Hodgman: clip any simple polygon against a convex, counter-clockwise window."""
    out = list(poly)
    n = len(window)
    for k in range(n):
        ax, ay = window[k]
        bx, by = window[(k + 1) % n]

        def inside(p):
            return (bx - ax) * (p[1] - ay) - (by - ay) * (p[0] - ax) >= 0

        def cut(p, q):
            # intersection of segment pq with the line ab
            dx1, dy1 = q[0] - p[0], q[1] - p[1]
            dx2, dy2 = bx - ax, by - ay
            den = dx1 * dy2 - dy1 * dx2
            s = ((ax - p[0]) * dy2 - (ay - p[1]) * dx2) / den
            return (p[0] + s * dx1, p[1] + s * dy1)

        src, out = out, []
        if not src:
            break
        prev = src[-1]
        for cur in src:
            if inside(cur):
                if not inside(prev):
                    out.append(cut(prev, cur))
                out.append(cur)
            elif inside(prev):
                out.append(cut(prev, cur))
            prev = cur
    return out


def halfplane(a, b, c, M=200.0):
    """Large counter-clockwise quad standing for the half-plane a x + b y >= c."""
    n = math.hypot(a, b)
    nx_, ny_ = a / n, b / n
    qx, qy = nx_ * c / n, ny_ * c / n          # a point of the line a x + b y = c
    tx, ty = -ny_, nx_
    quad = [(qx - M * tx, qy - M * ty), (qx + M * tx, qy + M * ty),
            (qx + M * tx + M * nx_, qy + M * ty + M * ny_), (qx - M * tx + M * nx_, qy - M * ty + M * ny_)]
    area = sum(quad[k][0] * quad[(k + 1) % 4][1] - quad[(k + 1) % 4][0] * quad[k][1] for k in range(4))
    return quad if area > 0 else quad[::-1]


def tint_layers(add_poly, layers, color=THEORY, base=0.05, alpha=0.05):
    """Density as stacked translucent superlevel sets: one single polygon per level, so no seams.

    layers[0] is the whole region (opacity base), the others are nested superlevel sets.
    add_poly(points, opacity) draws one polygon.
    """
    for k, poly in enumerate(layers):
        if len(poly) >= 3:
            add_poly(poly, base if k == 0 else alpha)


def plot_poly(p, color=THEORY):
    def add(poly, op):
        d = " ".join(p.P(x, y) for x, y in poly)
        p.add(f'<polygon points="{d}" fill="{color}" fill-opacity="{op:.3f}" stroke="none"/>')
    return add


def linear_layers(region, a, b, lo, hi, n=16):
    """region and its pieces where a x + b y >= level, levels spread over (lo, hi)."""
    return [region] + [clip_convex(region, halfplane(a, b, lo + (hi - lo) * k / (n + 1)))
                       for k in range(1, n + 1)]


def inside_poly(pt, poly):
    """Ray casting point-in-polygon test."""
    x, y = pt
    c = False
    n = len(poly)
    for k in range(n):
        x1, y1 = poly[k]
        x2, y2 = poly[(k + 1) % n]
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
            c = not c
    return c


def blob_pts(cx, cy, rx, ry, wobble, samples=160):
    """Smooth closed curve (counter-clockwise) for a lamina."""
    pts = []
    for s in range(samples):
        t = 2 * math.pi * s / samples
        f = 1 + sum(a * math.cos(k * t + ph) for a, k, ph in wobble)
        pts.append((cx + rx * f * math.cos(t), cy + ry * f * math.sin(t)))
    return pts


def frac_label(num, den):
    """Inline 'num/den' with a thin slash, for point coordinates."""
    return f"{num}/{den}"


# ============================================================
# izgara: Riemann-sum grid over a lamina, the mass of one cell
# ============================================================
D1 = blob_pts(5.1, 3.5, 3.5, 2.15, [(0.10, 2, 0.6), (0.06, 3, 2.2)])
GX, GY, NX, NY = (1.0, 9.4), (0.8, 6.2), 14, 9


p = eq_plot(40, 30, 36, (-0.3, 10.0), (-0.3, 7.0))
# illustrative density growing with 0.25 x + 0.18 y (toward the upper right)
L1 = [0.25 * x + 0.18 * y for x, y in D1]
tint_layers(plot_poly(p), linear_layers(D1, 0.25, 0.18, min(L1), max(L1), 16), THEORY, 0.06, 0.045)
# the grid over the enclosing rectangle R
hx, hy = (GX[1] - GX[0]) / NX, (GY[1] - GY[0]) / NY
grid = [f'<g stroke="{TEXT}" stroke-width="0.7" opacity="0.28">']
for i in range(NX + 1):
    X = p.X(GX[0] + i * hx)
    grid.append(f'<line x1="{X:.1f}" y1="{p.Y(GY[0]):.1f}" x2="{X:.1f}" y2="{p.Y(GY[1]):.1f}"/>')
for j in range(NY + 1):
    Y = p.Y(GY[0] + j * hy)
    grid.append(f'<line x1="{p.X(GX[0]):.1f}" y1="{Y:.1f}" x2="{p.X(GX[1]):.1f}" y2="{Y:.1f}"/>')
grid.append("</g>")
p.add("".join(grid))
p.line(D1 + [D1[0]], THEORY, 2.0)
# the chosen cell R_ij and its sample point
ci, cj = 9, 6
ca, cb = GX[0] + ci * hx, GY[0] + cj * hy
assert all(inside_poly(q, D1) for q in [(ca, cb), (ca + hx, cb), (ca + hx, cb + hy), (ca, cb + hy)])
p.polygon([(ca, cb), (ca + hx, cb), (ca + hx, cb + hy), (ca, cb + hy)], PRACTICE, 0.30, PRACTICE, 2.0)
SP = (ca + 0.36 * hx, cb + 0.58 * hy)
dot(p, SP, PRACTICE, 3.4)
# leader lines to the labels in the free band above the rectangle
p.line([(ca + hx, cb + hy), (8.6, 6.65)], PRACTICE, 1.0, None, 0.8)
p.label(8.6, 6.65, it("R") + sub("ij", 9), 4, -2, PRACTICE, 13, "start", True)
p.line([SP, (5.0, 6.65)], PRACTICE, 1.0, None, 0.8)
p.label(5.0, 6.65, "(" + it("x") + sub("ij", 9) + sup("*", 9) + ", " + it("y") + sub("ij", 9) + sup("*", 9) + ")",
        0, -5, PRACTICE, 12.5, "middle")
plabel(p, 3.0, 3.2, it("D"), 0, 0, THEORY, 14, "middle", True)
p.label(GX[0], GY[0], it("R"), 6, 16, TEXT, 13, "start")
# axes
p.arrow((-0.2, 0), (9.95, 0), TEXT, 1.1, 7.0, None, 0.55)
p.arrow((0, -0.2), (0, 6.95), TEXT, 1.1, 7.0, None, 0.55)
p.label(9.95, 0, it("x"), -2, 16, TEXT, 12, "end")
p.label(0, 6.95, it("y"), 9, 6, TEXT, 12)
p.label(0, 0, "0", -6, 14, TEXT, 11, "end")
save("izgara", figure(
    int(p.x0 + p.w + 30), int(p.y0 + p.h + 30), [p],
    "<em>D</em> bölgesini içeren <em>R</em> dikdörtgeni eşit alt dikdörtgenlere bölünür ve <em>D</em> "
    "dışında <em>&#961;</em> = 0 alınır; renk koyulaştıkça yoğunluk büyür. Turuncu <em>R<sub>ij</sub></em> "
    "parçasının kütlesi yaklaşık <em>&#961;</em>(<em>x</em><sub><em>ij</em></sub><sup>*</sup>, "
    "<em>y</em><sub><em>ij</em></sub><sup>*</sup>)&#8201;&#916;<em>A</em>'dır.",
    aria="A lamina D inside a rectangle R cut into a grid of equal subrectangles, the lamina tinted darker "
         "toward the upper right where the density is larger, one subrectangle Rij highlighted with its "
         "sample point"))

# ============================================================
# denge: the lamina balances on a needle under its center of mass
# ============================================================
H = 1.7
SHAPE = blob_pts(0.0, 0.0, 2.0, 1.35, [(0.12, 2, 0.4), (0.07, 3, 1.9)])


def rho2(x, y):
    """Illustrative density: heavier toward +x and +y."""
    return 1.0 + 0.45 * x + 0.25 * y


# center of mass of the drawn shape for this density (midpoint rule on a fine grid)
N2 = 240
xs = [-2.6 + 5.2 * (k + 0.5) / N2 for k in range(N2)]
ys = [-1.9 + 3.8 * (k + 0.5) / N2 for k in range(N2)]
m2 = mx2 = my2 = 0.0
for xv in xs:
    for yv in ys:
        if inside_poly((xv, yv), SHAPE):
            w = rho2(xv, yv)
            m2 += w
            mx2 += xv * w
            my2 += yv * w
XB, YB = mx2 / m2, my2 / m2

cam = Camera(azimuth=35.0, elevation=24.0)
box = [(x, y, H) for x, y in SHAPE] + [(x, y, 0.0) for x, y in SHAPE] + [(XB, YB, -0.3)]
pl, S = fit_space(cam, box, 30, 30, 105, 0.25)
# the stand on the floor and the needle
S.circle((XB, YB, 0.0), (1, 0, 0), (0, 1, 0), 0.42, TEXT, 1.0, None, 72, 0.55)
S.polygon([(XB + 0.42 * math.cos(2 * math.pi * k / 48), YB + 0.42 * math.sin(2 * math.pi * k / 48), 0.0)
           for k in range(48)], TEXT, 0.10)
needle = [S.pt((XB, YB, 0.0)), S.pt((XB, YB, H - 0.09))]
(nx0, ny0), (nx1, ny1) = needle
pl.add(f'<polygon points="{pl.P(nx0 - 0.09, ny0)} {pl.P(nx0 + 0.09, ny0)} {pl.P(nx1, ny1)}" '
       f'fill="{TEXT}" fill-opacity="0.55" stroke="{TEXT}" stroke-width="0.8" stroke-opacity="0.7"/>')
# the plate: bottom face, tinted top face (density as stacked layers mapped through the camera), rim
bottom = [(x, y, H - 0.09) for x, y in SHAPE]
S.polygon(bottom, THEORY, 0.10, THEORY, 0.8)
L2 = [0.45 * x + 0.25 * y for x, y in SHAPE]
tint_layers(lambda poly, op: S.polygon([(x, y, H) for x, y in poly], THEORY, op),
            linear_layers(SHAPE, 0.45, 0.25, min(L2), max(L2), 16), THEORY, 0.06, 0.045)
S.line([(x, y, H) for x, y in SHAPE] + [(SHAPE[0][0], SHAPE[0][1], H)], THEORY, 1.8)
# rim lines that join top and bottom at the left and right silhouette points
sil = sorted(SHAPE, key=lambda q: S.pt((q[0], q[1], H))[0])
for q in (sil[0], sil[-1]):
    S.line([(q[0], q[1], H), (q[0], q[1], H - 0.09)], THEORY, 1.2)
S.point((XB, YB, H), PRACTICE, 4.2)
splabel(S, (XB, YB, H), "kütle merkezi", 9, -7, PRACTICE, 12, "start", True)
splabel(S, (-1.3, -0.55, H), it("D"), 0, 5, THEORY, 13.5, "middle", True)
save("denge", figure(
    int(pl.x0 + pl.w + 30), int(pl.y0 + pl.h + 30), [pl],
    "Levha, bütün kütlesi kütle merkezinde toplanmış gibi davranır: kütle merkezinin altından bir iğne "
    "ucuyla desteklenen levha yatay olarak dengede kalır. Koyu bölgeler daha yoğundur ve kütle merkezi "
    "o yana kayar.",
    aria="A thin plate D held horizontally on the tip of a needle placed under its center of mass "
         "(xbar, ybar); the plate is tinted darker on the denser side"))

# ============================================================
# ucgen: the triangle of the worked example, rho = 1 + 3x + y
# ============================================================
TRI = [(0.0, 0.0), (1.0, 0.0), (0.0, 2.0)]
# the x range runs past the triangle so that the tall triangle does not make a tall figure
p = eq_plot(70, 30, 185, (-0.12, 1.7), (-0.12, 2.2))
tint_layers(plot_poly(p), linear_layers(TRI, 3.0, 1.0, 0.0, 3.0, 16), THEORY, 0.05, 0.045)
p.line(TRI + [TRI[0]], THEORY, 2.0)
p.arrow((-0.1, 0), (1.67, 0), TEXT, 1.1, 7.0, None, 0.55)
p.arrow((0, -0.1), (0, 2.17), TEXT, 1.1, 7.0, None, 0.55)
p.label(1.67, 0, it("x"), -2, 16, TEXT, 12, "end")
p.label(0, 2.17, it("y"), 9, 6, TEXT, 12)
p.label(0, 0, "0", -6, 14, TEXT, 11, "end")
dot(p, (1, 0), TEXT, 3.2)
dot(p, (0, 2), TEXT, 3.2)
p.label(1, 0, "(1, 0)", 0, 17, TEXT, 11.5, "middle")
p.label(0, 2, "(0, 2)", -8, 4, TEXT, 11.5, "end")
p.label(0.55, 0.9, it("y") + " = 2 " + MINUS + " 2" + it("x"), 12, -2, THEORY, 12, "start", True)
plabel(p, 0.22, 0.55, it("D"), 0, 0, THEORY, 13.5, "middle", True)
p.label(1.67, 2.17, it("&#961;") + " = 1 + 3" + it("x") + " + " + it("y"), 0, 6, TEXT, 12, "end")
save("ucgen", figure(
    int(p.x0 + p.w + 30), int(p.y0 + p.h + 30), [p],
    "Köşeleri (0, 0), (1, 0) ve (0, 2) olan üçgen levha. Renk koyulaştıkça yoğunluk "
    "<em>&#961;</em>(<em>x</em>, <em>y</em>) = 1 + 3<em>x</em> + <em>y</em> büyür: en hafif köşe orijin "
    "(<em>&#961;</em> = 1), en ağır köşeler (1, 0) ve (0, 2)'dir (<em>&#961;</em> = 4 ve 3).",
    aria="Triangle with vertices (0, 0), (1, 0) and (0, 2), upper side y = 2 - 2x, tinted darker where the "
         "density 1 + 3x + y is larger"))

# ============================================================
# yarimdisk: center of mass of the half disk, rho = K r versus constant rho
# ============================================================
p = eq_plot(40, 30, 190, (-1.25, 1.25), (-0.12, 1.22))
NR = 16


def half_ring(r0, r1, n=72):
    """The half annulus r0 <= r <= r1, 0 <= theta <= pi (a half disk when r0 = 0)."""
    outer = [(r1 * math.cos(math.pi * s / n), r1 * math.sin(math.pi * s / n)) for s in range(n + 1)]
    inner = [(r0 * math.cos(math.pi * s / n), r0 * math.sin(math.pi * s / n)) for s in range(n, -1, -1)]
    return outer + inner


# density K r: superlevel sets are the half annuli c <= r <= 1
tint_layers(plot_poly(p), [half_ring(0.0, 1.0)] + [half_ring(k / (NR + 1), 1.0) for k in range(1, NR + 1)],
            THEORY, 0.04, 0.045)
p.arc(0, 0, 1, 0, math.pi, THEORY, 2.0)
p.line([(-1, 0), (1, 0)], THEORY, 2.0)
p.arrow((-1.22, 0), (1.22, 0), TEXT, 1.1, 7.0, None, 0.55)
p.arrow((0, -0.08), (0, 1.2), TEXT, 1.1, 7.0, None, 0.55)
p.label(1.22, 0, it("x"), -2, 16, TEXT, 12, "end")
p.label(0, 1.2, it("y"), 9, 6, TEXT, 12)
p.label(-1, 0, MINUS + it("a"), 0, 16, TEXT, 11.5, "middle")
p.label(1, 0, it("a"), 0, 16, TEXT, 11.5, "middle")
p.label(0, 0, "0", -6, 16, TEXT, 11, "end")
p.label(0, 1, it("a"), -7, -6, TEXT, 11.5, "end")
p.label(math.cos(0.8), math.sin(0.8), it("x") + "² + " + it("y") + "² = " + it("a") + "²", 8, -4, THEORY, 12)
YC, YU = 3 / (2 * math.pi), 4 / (3 * math.pi)
dot(p, (0, YC), PRACTICE, 4.4)
hollow(p, (0, YU), TEXT, 4.0, 1.6)
plabel(p, 0, YC, "(0, 3" + it("a") + "/(2" + PI + "))", 10, -1, PRACTICE, 12.5, "start", True)
plabel(p, 0, YU, "sabit yoğunlukta (0, 4" + it("a") + "/(3" + PI + "))", -10, 8, TEXT, 12, "end")
save("yarimdisk", figure(
    int(p.x0 + p.w + 30), int(p.y0 + p.h + 30), [p],
    "Yoğunluk merkeze uzaklıkla orantılı olduğunda (koyu renk büyük yoğunluk) kütle merkezi "
    "(0, 3<em>a</em>/(2&#960;)) &#8776; (0; 0,477<em>a</em>) noktasıdır. Yoğunluk sabit olsaydı kütle "
    "merkezi (0, 4<em>a</em>/(3&#960;)) &#8776; (0; 0,424<em>a</em>) olurdu (içi boş nokta): ağırlık "
    "dışa doğru arttığı için kütle merkezi yukarı kayar.",
    aria="Upper half disk of radius a tinted darker toward the rim, with the center of mass (0, 3a/(2 pi)) "
         "marked as a solid point just above the hollow point (0, 4a/(3 pi)) of the constant density case"))

# ============================================================
# uzaklik: the three distances behind Ix, Iy and I0
# ============================================================
D5 = blob_pts(2.75, 2.0, 1.75, 1.25, [(0.09, 2, 1.1), (0.05, 3, 0.3)])
PX, PY = 3.3, 2.35
assert inside_poly((PX, PY), D5)
p = eq_plot(50, 30, 82, (-0.35, 5.0), (-0.35, 3.75))
p.polygon(D5, THEORY, 0.12, THEORY, 1.8)
p.line([(PX, PY), (PX, 0)], PRACTICE, 1.6, "5 3")
p.line([(PX, PY), (0, PY)], BASE, 1.6, "5 3")
p.line([(0, 0), (PX, PY)], TEXT, 1.6)
h = 0.13
p.polygon([(PX - h, PY - h), (PX + h, PY - h), (PX + h, PY + h), (PX - h, PY + h)], PRACTICE, 0.35, PRACTICE, 1.2)
dot(p, (PX, PY), PRACTICE, 3.0)
p.arrow((-0.25, 0), (4.95, 0), TEXT, 1.1, 7.0, None, 0.55)
p.arrow((0, -0.25), (0, 3.7), TEXT, 1.1, 7.0, None, 0.55)
p.label(4.95, 0, it("x"), -2, 16, TEXT, 12, "end")
p.label(0, 3.7, it("y"), 9, 6, TEXT, 12)
p.label(0, 0, "0", -6, 14, TEXT, 11, "end")
plabel(p, PX, 0.4, "|" + it("y") + "|", 8, 4, PRACTICE, 13, "start", True)
plabel(p, 0.5, PY, "|" + it("x") + "|", 0, -8, BASE, 13, "middle", True)
plabel(p, PX * 0.36, PY * 0.36, it("r"), 9, 12, TEXT, 13, "start", True)
plabel(p, PX, PY, it("P") + "(" + it("x") + ", " + it("y") + ")", 12, -10, PRACTICE, 12.5, "start", True)
plabel(p, 1.75, 2.95, it("D"), 0, 0, THEORY, 14, "middle", True)
save("uzaklik", figure(
    int(p.x0 + p.w + 30), int(p.y0 + p.h + 30), [p],
    "Levhanın <em>P</em>(<em>x</em>, <em>y</em>) noktasındaki küçük parçasının kütlesi yaklaşık "
    "<em>&#961;</em>(<em>x</em>, <em>y</em>)&#8201;&#916;<em>A</em>'dır. Bu parça <em>x</em> ekseninden "
    "|<em>y</em>|, <em>y</em> ekseninden |<em>x</em>|, orijinden <em>r</em> = &#8730;(<em>x</em>² + "
    "<em>y</em>²) uzaklıktadır; <em>I<sub>x</sub></em>, <em>I<sub>y</sub></em> ve "
    "<em>I</em><sub>0</sub> bu uzaklıkların kareleriyle kurulur.",
    aria="A lamina D in the first quadrant with a small square at the point P(x, y), the dashed distance "
         "|y| down to the x axis, the dashed distance |x| across to the y axis and the segment r from the "
         "origin to P"))

# ============================================================
# hacim: a probability is the volume under the joint density over D
# ============================================================


def fj(x, y):
    return 1.75 * math.exp(-((x - 2.1) ** 2) / 2.4 - ((y - 2.5) ** 2) / 3.2) + 0.12


A_, B_, C_, D_ = 1.3, 2.9, 1.6, 3.5
XM, YM = 4.4, 5.2
cam = Camera(azimuth=35.0, elevation=22.0)
pts = [(0, 0, 0), (5.0, 0, 0), (0, 5.9, 0), (0, 0, 2.55), (XM, YM, 0), (XM, 0, 0), (0, YM, 0),
       (XM, YM, fj(XM, YM)), (2.1, 2.5, fj(2.1, 2.5))]
pl, S = fit_space(cam, pts, 30, 30, 70, 0.35)
S.axes(5.0, 5.9, 2.55)
# the rectangle D on the floor with its guides to the axes
S.polygon([(A_, C_, 0), (B_, C_, 0), (B_, D_, 0), (A_, D_, 0)], PRACTICE, 0.22, PRACTICE, 1.4)
S.guide([(A_, C_, 0), (A_, 0, 0)])
S.guide([(B_, C_, 0), (B_, 0, 0)])
S.guide([(A_, C_, 0), (0, C_, 0)])
S.guide([(A_, D_, 0), (0, D_, 0)])


def wall(p0, p1, n=24):
    """Vertical wall from the floor segment p0-p1 up to the graph."""
    bot = [(p0[0] + (p1[0] - p0[0]) * k / n, p0[1] + (p1[1] - p0[1]) * k / n, 0.0) for k in range(n + 1)]
    top = [(q[0], q[1], fj(q[0], q[1])) for q in reversed(bot)]
    return bot + top


# back walls first (x = a and y = c face away from the viewer)
S.polygon(wall((A_, C_), (A_, D_)), PRACTICE, 0.10, PRACTICE, 0.8)
S.polygon(wall((A_, C_), (B_, C_)), PRACTICE, 0.10, PRACTICE, 0.8)
# the graph of the joint density over the whole drawn square
S.surface(lambda u, v: (u, v, fj(u, v)), (0, XM), (0, YM), nu=11, nv=13, fill=THEORY, stroke=THEORY,
          opacity=(0.03, 0.12), stroke_width=0.5, stroke_opacity=0.3)
# front walls and the top patch of the solid
S.polygon(wall((B_, C_), (B_, D_)), PRACTICE, 0.16, PRACTICE, 1.0)
S.polygon(wall((A_, D_), (B_, D_)), PRACTICE, 0.16, PRACTICE, 1.0)
for P0, P1 in (((A_, C_), (B_, C_)), ((B_, C_), (B_, D_)), ((B_, D_), (A_, D_)), ((A_, D_), (A_, C_))):
    S.curve(lambda s, P0=P0, P1=P1: (P0[0] + (P1[0] - P0[0]) * s, P0[1] + (P1[1] - P0[1]) * s,
                                     fj(P0[0] + (P1[0] - P0[0]) * s, P0[1] + (P1[1] - P0[1]) * s)),
            0, 1, PRACTICE, 1.8, 40)
S.label((A_, 0, 0), it("a"), -6, 14, TEXT, 12.5, "middle")
S.label((B_, 0, 0), it("b"), -6, 14, TEXT, 12.5, "middle")
S.label((0, C_, 0), it("c"), 0, -7, TEXT, 12.5, "middle")
S.label((0, D_, 0), it("d"), 0, -7, TEXT, 12.5, "middle")
splabel(S, ((A_ + B_) / 2, (C_ + D_) / 2, 0), it("D"), 4, 16, PRACTICE, 13.5, "middle", True)
S.label((1.2, 4.4, fj(1.2, 4.4)), it("z") + " = " + it("f") + "(" + it("x") + ", " + it("y") + ")",
        6, -40, THEORY, 12.5, "start", True)
save("hacim", figure(
    int(pl.x0 + pl.w + 30), int(pl.y0 + pl.h + 30), [pl],
    "<em>P</em>(<em>a</em> &#8804; <em>X</em> &#8804; <em>b</em>, <em>c</em> &#8804; <em>Y</em> &#8804; "
    "<em>d</em>) olasılığı, <em>D</em> = [<em>a</em>, <em>b</em>] &#215; [<em>c</em>, <em>d</em>] "
    "dikdörtgeninin üstünde ve ortak yoğunluk fonksiyonunun grafiğinin altında kalan cismin hacmidir. "
    "Bütün grafiğin altındaki hacim 1'dir.",
    aria="Graph of a joint density z = f(x, y) over the first quadrant; above the rectangle D = [a, b] x "
         "[c, d] on the floor the solid under the graph is outlined with walls"))

# ============================================================
# normal: the bivariate normal density of the roller example
# ============================================================
PEAK = 5000 / math.pi          # 1591.55
HZ = 4.2                        # drawn height of the peak
SC = HZ / PEAK                  # drawn units per unit of density


def gauss(u, v):
    """u = (x - 4)/0.01, v = (y - 6)/0.01; the density in drawn units."""
    return HZ * math.exp(-(u * u + v * v) / 2)


cam = Camera(azimuth=35.0, elevation=24.0)
L5 = 5.0
pts = [(L5, L5, 0), (-L5, -L5, 0), (L5, -L5, 0), (-L5, L5, 0), (L5, -L5, HZ + 0.4), (0, 0, HZ)]
pl, S = fit_space(cam, pts, 70, 30, 30, 0.6)
# floor frame and the square |u|, |v| <= 2 of the event
S.polygon([(-L5, -L5, 0), (L5, -L5, 0), (L5, L5, 0), (-L5, L5, 0)], TEXT, 0.04, TEXT, 0.9)
S.floor_grid((-L5, L5), (-L5, L5), 10, 0.0, TEXT, 0.12, 0.6)
S.polygon([(-2, -2, 0), (2, -2, 0), (2, 2, 0), (-2, 2, 0)], PRACTICE, 0.25, PRACTICE, 1.6)
# the bell in polar parameters (beyond r = 3.2 the density is below 0.6 % of the peak)
S.surface(lambda r, th: (r * math.cos(th), r * math.sin(th), gauss(r * math.cos(th), r * math.sin(th))),
          (0, 3.2), (0, 2 * math.pi), nu=12, nv=40, fill=THEORY, stroke=THEORY,
          opacity=(0.02, 0.24), stroke_width=0.45, stroke_opacity=0.45)
# vertical z axis at the left corner (x = 4.05, y = 5.95) with ticks in density units
ZC = (L5, -L5)
S.line([(ZC[0], ZC[1], 0), (ZC[0], ZC[1], HZ + 0.35)], TEXT, 1.0, None, 0.6)
for val in (500, 1000, 1500):
    zz = val * SC
    S.line([(ZC[0], ZC[1], zz), (ZC[0] + 0.35, ZC[1] - 0.35, zz)], TEXT, 1.0, None, 0.6)
    S.label((ZC[0] + 0.35, ZC[1] - 0.35, zz), str(val), -4, 4, TEXT, 11.5, "end")
S.label((ZC[0], ZC[1], HZ + 0.35), it("z"), 0, -6, TEXT, 13, "middle")
# x ticks along the front-right edge v = 5 (that is y = 6.05), y ticks along the front-left edge u = 5
for u, s in ((-L5, "3,95"), (0.0, "4"), (L5, "4,05")):
    S.line([(u, L5, 0), (u, L5 + 0.35, 0)], TEXT, 1.0, None, 0.6)
    S.label((u, L5, 0), s, 12, 14, TEXT, 11.5, "start")
for v, s in ((-L5, "5,95"), (0.0, "6"), (L5, "6,05")):
    S.line([(L5, v, 0), (L5 + 0.35, v, 0)], TEXT, 1.0, None, 0.6)
    S.label((L5, v, 0), s, -8, 16, TEXT, 11.5, "end")
S.label((0.0, L5, 0), it("x"), 30, 34, TEXT, 13, "middle")
S.label((L5, 0.0, 0), it("y"), -30, 36, TEXT, 13, "middle")
splabel(S, (2.0, 2.0, 0), "|" + it("x") + " " + MINUS + " 4| &lt; 0,02 ve |" + it("y") + " " + MINUS
        + " 6| &lt; 0,02", 0, 24, PRACTICE, 12, "middle")
save("normal", figure(
    int(pl.x0 + pl.w + 30), int(pl.y0 + pl.h + 30), [pl],
    "Ortak yoğunluk <em>f</em>(<em>x</em>, <em>y</em>) = (5000/&#960;)&#8201;<em>e</em><sup>&#8722;5000"
    "[(<em>x</em> &#8722; 4)² + (<em>y</em> &#8722; 6)²]</sup>, (4, 6) noktası üzerinde dik bir tepedir; "
    "en büyük değeri 5000/&#960; &#8776; 1592'dir. Tabandaki turuncu kare |<em>x</em> &#8722; 4| &lt; 0,02, "
    "|<em>y</em> &#8722; 6| &lt; 0,02 bölgesidir; bu karenin üstünde ve grafiğin altında kalan hacim "
    "yaklaşık 0,91'dir.",
    aria="Bell shaped surface of the bivariate normal density over the square 3.95 to 4.05 by 5.95 to 6.05 "
         "with peak about 1592 at (4, 6); the central square |x - 4| and |y - 6| below 0.02 is marked on "
         "the floor"))

# ============================================================
# tahmin: exercise lamina, the unit square with rho = xy
# ============================================================
SQ = [(0, 0), (1, 0), (1, 1), (0, 1)]
p = eq_plot(50, 30, 230, (-0.1, 1.2), (-0.1, 1.15))
# density xy: the superlevel set xy >= c is bounded by the hyperbola y = c/x and the corner (1, 1)
LAY = [SQ]
for k in range(1, 19):
    c = k / 19
    LAY.append([(c + (1 - c) * s / 48, c / (c + (1 - c) * s / 48)) for s in range(49)] + [(1, 1)])
tint_layers(plot_poly(p), LAY, THEORY, 0.03, 0.04)
p.line(SQ + [SQ[0]], THEORY, 1.6)
p.arrow((-0.08, 0), (1.18, 0), TEXT, 1.1, 7.0, None, 0.55)
p.arrow((0, -0.08), (0, 1.13), TEXT, 1.1, 7.0, None, 0.55)
p.label(1.18, 0, it("x"), -2, 16, TEXT, 12, "end")
p.label(0, 1.13, it("y"), 9, 6, TEXT, 12)
p.label(0, 0, "0", -6, 14, TEXT, 11, "end")
p.label(1, 0, "1", 0, 15, TEXT, 11.5, "middle")
p.label(0, 1, "1", -7, 4, TEXT, 11.5, "end")
p.label(1.18, 1.13, it("&#961;") + "(" + it("x") + ", " + it("y") + ") = " + it("x") + it("y"),
        0, 6, TEXT, 12, "end")
save("tahmin", figure(
    int(p.x0 + p.w + 30), int(p.y0 + p.h + 30), [p],
    "Yoğunluğu <em>&#961;</em>(<em>x</em>, <em>y</em>) = <em>xy</em> olan kare levha; renk koyulaştıkça "
    "yoğunluk büyür. Sol ve alt kenarlarda yoğunluk 0'dır.",
    aria="Unit square tinted from white at the left and bottom edges to dark at the corner (1, 1), "
         "showing the density xy"))
