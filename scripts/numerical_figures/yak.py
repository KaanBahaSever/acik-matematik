# -*- coding: utf-8 -*-
"""
Figures of the chapter "Algoritmalar ve Yakınsama Hızı"
(dersler/numerik-analiz/algoritmalar-ve-yakinsama.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box and never directly under a heading.
The figures are NOT produced at build time. Run

    python scripts/numerical_figures/yak.py
    python scripts/center_figures.py "numerical-yak-*.md"
    python scripts/check_figure_labels.py "scripts/_figures/numerical-yak-*.md"

and paste the markup of scripts/_figures/numerical-yak-<name>.md into the .qmd.
Captions are Turkish on purpose; aria labels are plain ASCII.

The 3-D graph is a translucent surface with a sparse wire net. Curves and
wires are split into the parts the viewer sees and the parts hidden by the
surface (a ray is cast from each sample toward the camera): hidden parts are
painted faintly before the surface, visible parts after it.
"""
import html
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, TEXT, THEORY, PRACTICE, BG  # noqa: E402
from svg_plot3 import Camera, Space  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "numerical-yak-"

MINUS = "&#8722;"


def save(name, markup):
    (OUT_DIR / f"{PREFIX}{name}.md").write_text(markup, encoding="utf-8", newline="\n")
    print(f"{PREFIX}{name}.md")


def it(s):
    """Italic run inside an SVG <text>."""
    return f'<tspan font-style="italic">{s}</tspan>'


def sup(s, size=8.5):
    """Superscript inside an SVG <text>."""
    return f'<tspan font-size="{size}" dy="-5">{s}</tspan><tspan dy="5">&#8203;</tspan>'


def sub(s, size=8.5):
    """Subscript inside an SVG <text>."""
    return f'<tspan font-size="{size}" dy="3.5">{s}</tspan><tspan dy="-3.5">&#8203;</tspan>'


def dec(v, digits=2):
    """Decimal comma and a true minus sign: -0.5 -> '−0,5'."""
    s = f"{v:.{digits}f}".rstrip("0").rstrip(".")
    return s.replace(".", ",").replace("-", MINUS)


def text_w(s, size):
    """Rough advance width of a label (0.56 em per visible character)."""
    plain = html.unescape(re.sub(r"<[^>]+>", "", s)).replace("​", "")
    return len(plain) * 0.56 * size


def plate(p, x, y, s, dx=0, dy=0, size=11.5, anchor="start", opacity=0.9):
    """Page-coloured rounded plate under a label that has to sit on lines."""
    px, py = p.X(x) + dx, p.Y(y) + dy
    w = text_w(s, size)
    x0 = px - (w / 2 if anchor == "middle" else w if anchor == "end" else 0)
    p.add(f'<rect x="{x0 - 2.5:.1f}" y="{py - 0.8 * size - 1:.1f}" width="{w + 5:.1f}" '
          f'height="{size + 3:.1f}" rx="3" fill="{BG}" opacity="{opacity}"/>')


def plabel(p, x, y, s, dx=0, dy=0, color=TEXT, size=11.5, anchor="start", bold=False):
    plate(p, x, y, s, dx, dy, size, anchor)
    p.label(x, y, s, dx, dy, color, size, anchor, bold)


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


def square(p, x, y, color, half=3.6):
    """Filled square marker (the second data series)."""
    X, Y = p.X(x), p.Y(y)
    p.add(f'<rect x="{X - half:.1f}" y="{Y - half:.1f}" width="{2 * half:.1f}" height="{2 * half:.1f}" '
          f'fill="{color}"/>')


# ---------------------------------------------------------------------------
# hidden-line handling for the graph z = h(x, y) of a function on a convex domain
# ---------------------------------------------------------------------------
class GraphScene:
    """Collects strokes, sorts them into hidden (painted before the surface)
    and visible parts (painted after it)."""

    def __init__(self, S, height, inside, reach=8.0):
        self.S = S
        self.h = height
        self.inside = inside
        self.reach = reach
        self.back, self.front = [], []

    def hidden(self, P, eps=0.01, n=500):
        """Does the surface lie between P and the viewer?"""
        d = self.S.cam.d
        prev = None
        for k in range(n + 1):
            t = eps + (self.reach - eps) * k / n
            x, y, z = P[0] + t * d[0], P[1] + t * d[1], P[2] + t * d[2]
            if not self.inside(x, y):
                prev = None
                continue
            g = z - self.h(x, y)
            if prev is not None and g * prev < 0:
                return True
            prev = g
        return False

    def polyline(self, pts, color, width, opacity=1.0, hidden_opacity=0.3, dash=None):
        """Split a sampled space curve at the changes of visibility."""
        flags = [self.hidden(tuple((a + b) / 2 for a, b in zip(P, Q))) for P, Q in zip(pts, pts[1:])]
        start = 0
        for k in range(1, len(flags) + 1):
            if k == len(flags) or flags[k] != flags[start]:
                run = pts[start:k + 1]
                if flags[start]:
                    self.back.append(lambda run=run: self.S.line(run, color, width, dash,
                                                                 opacity * hidden_opacity))
                else:
                    self.front.append(lambda run=run: self.S.line(run, color, width, dash, opacity))
                start = k

    def curve(self, f, t0, t1, color, width, samples=160, **kw):
        self.polyline([f(t0 + (t1 - t0) * k / samples) for k in range(samples + 1)], color, width, **kw)

    def render(self, draw_surface):
        for f in self.back:
            f()
        draw_surface()
        for f in self.front:
            f()


# ============================================================
# hata-yuzeyi: z = log10(E_n / E_0) = n log10(C), 0 <= n <= 10, 0.5 <= C <= 3
# ============================================================
# World coordinates: n runs along +y (to the right on the page), C grows along -x
# (away from the viewer), so the surface rises toward the back and faces the camera.
N0, N1, C0, C1 = 0.0, 10.0, 0.5, 3.0
SN, SC, SZ = 0.34, 1.0, 0.36


def growth(n, C):
    return n * math.log10(C)


def W(n, C, z):
    """(n, C, z) -> world point."""
    return ((1.75 - C) * SC, (n - 5.0) * SN, z * SZ)


def to_nc(x, y):
    return y / SN + 5.0, 1.75 - x / SC


def height(x, y):
    n, C = to_nc(x, y)
    return SZ * growth(n, C)


def in_domain(x, y):
    n, C = to_nc(x, y)
    return N0 <= n <= N1 and C0 <= C <= C1


cam = Camera(azimuth=-28.0, elevation=20.0)
ZTOP, ZBOT = 5.6, -3.4
NEND, CEND = 11.6, 3.55
box = [W(n, C, growth(n, C)) for n in (N0, N1) for C in (C0, 1.0, C1)]
box += [W(0, C0, ZTOP), W(0, C0, ZBOT), W(NEND, C0, 0), W(0, CEND, 0)]
pl, S = fit_space(cam, box, 110, 40, 92, 0.15)
G = GraphScene(S, height, in_domain)

# sparse wire net: n = 2, 4, ..., 10 and C = 0.5, 1.5, 2, 2.5 (C = 1 and C = 3 are drawn heavy below)
for k in range(1, 6):
    n = 2.0 * k
    G.curve(lambda C, n=n: W(n, C, growth(n, C)), C0, C1, TEXT, 0.7, 80, opacity=0.4, hidden_opacity=0.35)
for C in (0.5, 1.5, 2.0, 2.5):
    G.curve(lambda n, C=C: W(n, C, growth(n, C)), N0, N1, TEXT, 0.7, 40, opacity=0.4, hidden_opacity=0.35)
# the flat section C = 1, the exponential section C = 3 and the linear comparison curve z = log10(n)
G.curve(lambda n: W(n, 1.0, 0.0), N0, N1, TEXT, 2.6, 60, hidden_opacity=0.4)
G.curve(lambda n: W(n, C1, growth(n, C1)), N0, N1, PRACTICE, 2.8, 120, hidden_opacity=0.4)
G.curve(lambda n: W(n, 1.0, math.log10(n)), 1.0, N1, THEORY, 2.4, 120, hidden_opacity=0.4, dash="6 4")

def draw_growth_surface():
    """Faces painted back to front; blue where the error decays (z below 0),
    red where it grows, more opaque the farther z is from 0."""
    cs = [C0 + (1.0 - C0) * k / 5 for k in range(5)] + [1.0 + (C1 - 1.0) * k / 16 for k in range(17)]
    ns = [N0 + (N1 - N0) * k / 20 for k in range(21)]
    faces = []
    for i in range(len(ns) - 1):
        for j in range(len(cs) - 1):
            quad = [W(ns[a], cs[b], growth(ns[a], cs[b])) for a, b in ((i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1))]
            zc = growth((ns[i] + ns[i + 1]) / 2, (cs[j] + cs[j + 1]) / 2)
            dep = sum(S.depth(q) for q in quad) / 4
            faces.append((dep, quad, zc))
    faces.sort(key=lambda t: t[0])
    for _, quad, zc in faces:
        color = PRACTICE if zc > 0 else THEORY
        op = 0.07 + 0.31 * min(1.0, abs(zc) / 3.0)
        pts = " ".join(pl.P(*S.pt(q)) for q in quad)
        pl.add(f'<polygon points="{pts}" fill="{color}" fill-opacity="{op:.3f}" stroke="{color}" '
               f'stroke-width="0.3" stroke-opacity="0.06" stroke-linejoin="round"/>')


G.render(draw_growth_surface)

# axes: n along the front edge C = 0.5, C along the back edge n = 0 (where z = 0), z through (0, 0.5)
O = W(0, C0, 0)
AX_OP = 0.6
S.line([O, W(NEND - 0.5, C0, 0)], TEXT, 1.1, None, AX_OP)
S.arrow(W(NEND - 0.6, C0, 0), W(NEND, C0, 0), TEXT, 1.1, 7.0, None, AX_OP)
S.line([O, W(0, CEND - 0.1, 0)], TEXT, 1.1, None, AX_OP)
S.arrow(W(0, CEND - 0.15, 0), W(0, CEND, 0), TEXT, 1.1, 7.0, None, AX_OP)
S.line([W(0, C0, ZBOT), W(0, C0, ZTOP - 0.3)], TEXT, 1.1, None, AX_OP)
S.arrow(W(0, C0, ZTOP - 0.4), W(0, C0, ZTOP), TEXT, 1.1, 7.0, None, AX_OP)
S.label(W(NEND, C0, 0), it("n"), 6, 12, TEXT, 12.5, "middle")
S.label(W(0, CEND, 0), it("C"), -4, -7, TEXT, 12.5, "middle")
S.label(W(0, C0, ZTOP), "log" + sub("10") + "(" + it("E") + sub(it("n")) + "/" + it("E") + sub("0") + ")",
        0, -9, TEXT, 12, "middle")
# ticks
TK = 0.09
for n in (5, 10):
    S.line([W(n, C0 + TK, 0), W(n, C0 - TK, 0)], TEXT, 1.0, None, 0.7)
    S.label(W(n, C0, 0), str(n), -2, 15, TEXT, 10.5, "middle")
for C in (1, 2, 3):
    S.line([W(0, C, 0), W(-0.35, C, 0)], TEXT, 1.0, None, 0.7)
    S.label(W(-0.35, C, 0), dec(C), -4, 3, TEXT, 10.5, "end")
S.label(W(-0.35, C0, 0), "0,5", -4, 6, TEXT, 10.5, "end")
for z in (-3, 3):
    S.line([W(-0.3, C0, z), W(0, C0, z)], TEXT, 1.0, None, 0.7)
    S.label(W(-0.3, C0, z), dec(z), -4, 4, TEXT, 10.5, "end")
# section labels at the right end
S.label(W(N1, C1, growth(N1, C1)), it("C") + " = 3 (üstel)", 8, 4, PRACTICE, 12, "start", True)
S.label(W(N1, 1.0, 0), it("C") + " = 1", 8, -5, TEXT, 12, "start", True)
S.label(W(N1, 1.0, 1.0), "lineer: " + it("E") + sub(it("n")) + " = " + it("n") + "·" + it("E") + sub("0"),
        8, 0, THEORY, 12, "start", True)
save("hata-yuzeyi", figure(
    int(pl.x0 + pl.w + 150), int(pl.y0 + pl.h + 20), [pl],
    "<em>z</em> = log<sub>10</sub>(<em>E<sub>n</sub></em>/<em>E</em><sub>0</sub>) = <em>n</em>&#8201;log<sub>10</sub> "
    "<em>C</em> yüzeyi (0 &#8804; <em>n</em> &#8804; 10, 0,5 &#8804; <em>C</em> &#8804; 3). Mavi bölgede "
    "(<em>C</em> &lt; 1) hata söner, kırmızı bölgede (<em>C</em> &gt; 1) üstel olarak büyür; <em>C</em> = 1 "
    "kesitinde yüzey düzdür. Kırmızı kalın eğri <em>C</em> = 3 kesitidir, kesikli mavi eğri ise lineer büyüme "
    "<em>E<sub>n</sub></em> = <em>n</em>&#8201;<em>E</em><sub>0</sub> için log<sub>10</sub> <em>n</em> değeridir. "
    "Yüzeyin arkasında kalan çizgiler soluk çizilmiştir.",
    aria="Surface z = n log10(C) for n from 0 to 10 and C from 0.5 to 3: below zero for C under 1, flat along "
         "C = 1, rising for C over 1, with the section C = 3 in red and the linear growth curve log10(n) dashed"))

# ============================================================
# lineer-ustel: exponential against linear error growth, logarithmic error axis
# ============================================================
E0_EXP = 0.125e-5
E0_LIN = 0.33333e-5
TABLE = {2: 0.10000e-4, 3: 0.37000e-4, 4: 0.11600e-3, 5: 0.34920e-3, 6: 0.10487e-2, 7: 0.31466e-2,
         8: 0.94396e-2}
lg = math.log10
p = Plot(80, 30, 400, 300, (0, 8.6), (-6, -1))
p.grid(range(0, 9), range(-6, 0))
p.axes(range(0, 9), [], "n", "", str, str)
for k in range(-6, 0):
    p.label(0, k, "10" + sup(MINUS + str(-k)), -8, 4, TEXT, 11, "end")
p.text_px(p.x0 - 4, p.y0 - 14, "mutlak hata " + it("E") + sub(it("n")), TEXT, 11.5, "middle")
exp_pts = [(n, lg(E0_EXP * 3 ** n)) for n in range(9)]
lin_pts = [(n, lg(E0_LIN * n)) for n in range(1, 9)]
p.line(exp_pts, PRACTICE, 2.0)
p.points(exp_pts, PRACTICE, 3.4)
p.hollow_points([(n, lg(v)) for n, v in TABLE.items()], PRACTICE, 6.0)
p.line([(n, lg(E0_LIN * n)) for n in [1 + 7 * k / 140 for k in range(141)]], THEORY, 2.0, "6 4")
p.points(lin_pts, THEORY, 3.4)
# the factor between the two errors at n = 8 (table value against the linear error)
ya, yb = lg(E0_LIN * 8), lg(TABLE[8])
xa = 8.25
p.arrow((xa, (ya + yb) / 2), (xa, yb - 0.04), TEXT, 1.2, 7.0)
p.arrow((xa, (ya + yb) / 2), (xa, ya + 0.04), TEXT, 1.2, 7.0)
p.line([(8.08, yb), (8.32, yb)], TEXT, 0.8, None, 0.6)
p.line([(8.08, ya), (8.32, ya)], TEXT, 0.8, None, 0.6)
plabel(p, xa, (ya + yb) / 2, "&#8776; 350 kat", 6, 4, TEXT, 11.5, "start", True)
# curve labels
p.label(4.6, lg(E0_EXP * 3 ** 4.6), "üstel: 0,125·10" + sup(MINUS + "5") + "·3" + sup(it("n")), -6, -8,
        PRACTICE, 12, "end", True)
p.label(5, lg(E0_LIN * 5), "lineer: 0,33333·10" + sup(MINUS + "5") + "·" + it("n"), 4, 22, THEORY, 12,
        "middle", True)
p.label(0.25, -1.45, "log ölçekte üstel büyüme = doğru", 0, 0, TEXT, 11.5, "start", False, True)
p.hollow_points([(0.35, -1.85)], PRACTICE, 6.0)
p.label(0.35, -1.85, "tablodaki gerçek mutlak hata", 12, 4, PRACTICE, 11.5)
save("lineer-ustel", figure(
    int(p.x0 + p.w + 90), int(p.y0 + p.h + 30), [p],
    "Logaritmik eksende iki hata büyümesi. Kırmızı doğru üstel büyüme <em>E<sub>n</sub></em> = "
    "0,125·10<sup>&#8722;5</sup>·3<sup><em>n</em></sup>, içi boş daireler tablodaki beş-basamak hesabın gerçek "
    "mutlak hatalarıdır; kesikli mavi eğri lineer büyüme <em>E<sub>n</sub></em> = 0,33333·10<sup>&#8722;5</sup>·"
    "<em>n</em>'dir. <em>n</em> = 8'de tablodaki hata lineer hatanın yaklaşık 350 katıdır.",
    aria="Absolute error against n from 0 to 8 on a logarithmic axis from 10^-6 to 10^-1: the exponential "
         "growth 0.125e-5 times 3^n is a straight red line with the table errors as open circles, the linear "
         "growth 0.33333e-5 times n is a dashed blue curve, about 350 times smaller at n = 8"))

# ============================================================
# dizi-hizlari: a_n = (n + 1)/n^2 and b_n = (n + 3)/n^3 with the bounds 2/n and 4/n^2
# ============================================================
p = Plot(60, 30, 420, 300, (0, 10.5), (0, 4.2))
p.grid(range(1, 11), [0.5 * k for k in range(1, 9)])
p.axes(range(1, 11), [0, 1, 2, 3, 4], "n", it("a") + sub(it("n")) + ", " + it("b") + sub(it("n")), str, str)
xs = [1 + 9 * k / 360 for k in range(361)]
p.line([(x, 2 / x) for x in xs], THEORY, 1.6, "6 4", 0.9)
p.line([(x, 4 / x ** 2) for x in xs], PRACTICE, 1.6, "6 4", 0.9)
a = [(n, (n + 1) / n ** 2) for n in range(1, 11)]
b = [(n, (n + 3) / n ** 3) for n in range(1, 11)]
p.points(a, THEORY, 4.0)
for x, y in b:
    square(p, x, y, PRACTICE, 3.6)
p.label(1, 4, it("b") + sub(it("n")), 10, 4, PRACTICE, 13, "start", True)
p.label(1, 2, it("a") + sub(it("n")), -10, 5, THEORY, 13, "end", True)
p.label(4.2, 2 / 4.2, "2/" + it("n"), 4, -10, THEORY, 12, "start", True)
p.label(1.75, 4 / 1.75 ** 2, "4/" + it("n") + sup("2"), 7, -3, PRACTICE, 12, "start", True)
save("dizi-hizlari", figure(
    int(p.x0 + p.w + 40), int(p.y0 + p.h + 30), [p],
    "<em>a<sub>n</sub></em> = (<em>n</em> + 1)/<em>n</em>² (mavi daireler) ve <em>b<sub>n</sub></em> = "
    "(<em>n</em> + 3)/<em>n</em>³ (kırmızı kareler) dizilerinin ilk on terimi ile üst sınırları 2/<em>n</em> ve "
    "4/<em>n</em>² (kesikli). <em>n</em> = 1'de iki dizi de sınırına eşittir; <em>n</em> &#8805; 3 için "
    "<em>b<sub>n</sub></em> sıfıra <em>a<sub>n</sub></em>'den çok daha hızlı iner.",
    aria="The sequences a_n = (n+1)/n^2 as blue dots and b_n = (n+3)/n^3 as red squares for n from 1 to 10, "
         "under their dashed bounds 2/n and 4/n^2"))
