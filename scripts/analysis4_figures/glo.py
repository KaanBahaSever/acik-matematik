# -*- coding: utf-8 -*-
"""
Figures of the chapter "Sürekli Fonksiyonların Global Özellikleri"
(dersler/analiz-4/surekli-fonksiyonlarin-global-ozellikleri.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box and never directly under a heading.
The figures are NOT produced at build time. Run

    python scripts/analysis4_figures/glo.py
    python scripts/center_figures.py "analysis4-glo-*.md"
    python scripts/check_figure_labels.py "scripts/_figures/analysis4-glo-*.md"

and paste the markup of scripts/_figures/analysis4-glo-<name>.md into the .qmd.
The captions are Turkish on purpose; the aria labels are plain ASCII.

Conventions: a boundary that belongs to the set is solid, one that does not is
dashed; a point of the set is filled, a point outside it is hollow.
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from svg_plot import Plot, figure, hollow, disk_fill, WIDE, TEXT, THEORY, PRACTICE  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT_DIR = Path(__file__).resolve().parents[1] / "_figures"
OUT_DIR.mkdir(exist_ok=True)
PREFIX = "analysis4-glo-"

MINUS, PI_S, DELTA, EPS, NORM, TO = "&#8722;", "&#960;", "&#948;", "&#949;", "&#8214;", "&#8594;"


def save(name, svg):
    (OUT_DIR / f"{PREFIX}{name}.md").write_text(svg, encoding="utf-8", newline="\n")
    print(f"{PREFIX}{name}.md")


def it(s):
    """Italic math letter inside an SVG <text>."""
    return f'<tspan font-style="italic">{s}</tspan>'


def subs(s, size=9):
    """Subscript inside an SVG <text>."""
    return f'<tspan font-size="{size}" dy="4">{s}</tspan><tspan dy="-4">&#8203;</tspan>'


def sups(s, size=9):
    """Superscript inside an SVG <text>."""
    return f'<tspan font-size="{size}" dy="-5">{s}</tspan><tspan dy="5">&#8203;</tspan>'


def num(v):
    """Tick label with a real minus sign."""
    return f"{v:g}".replace("-", MINUS)


def equal_panel(x0, y0, ppu, xrange, yrange):
    """A panel with the same pixels per unit on both axes."""
    return Plot(x0, y0, ppu * (xrange[1] - xrange[0]), ppu * (yrange[1] - yrange[0]), xrange, yrange)


def arc_pts(cx, cy, r, a0, a1, n=96):
    return [(cx + r * math.cos(a0 + (a1 - a0) * k / n), cy + r * math.sin(a0 + (a1 - a0) * k / n))
            for k in range(n + 1)]


def graph_pts(f, x0, x1, n=160):
    return [(x0 + (x1 - x0) * k / n, f(x0 + (x1 - x0) * k / n)) for k in range(n + 1)]


def arrowhead(p, tip, frm, color, head=8.0):
    """Filled arrowhead at pixel point tip, pointing away from pixel point frm."""
    dx, dy = tip[0] - frm[0], tip[1] - frm[1]
    L = math.hypot(dx, dy) or 1.0
    ux, uy = dx / L, dy / L
    hw = head * 0.42
    p.add(f'<polygon points="{tip[0]:.1f},{tip[1]:.1f} {tip[0] - ux * head - uy * hw:.1f},{tip[1] - uy * head + ux * hw:.1f} '
          f'{tip[0] - ux * head + uy * hw:.1f},{tip[1] - uy * head - ux * hw:.1f}" fill="{color}"/>')


def bezier_arrow(p, a, c, b, color=TEXT, width=1.4, dash=None, head=8.0):
    """Quadratic Bezier arrow in pixel coordinates from a to b with control point c."""
    tip = b
    # stop the shaft short of the tip so that it does not poke through the head
    L = math.hypot(b[0] - c[0], b[1] - c[1]) or 1.0
    end = (b[0] - (b[0] - c[0]) / L * head * 0.8, b[1] - (b[1] - c[1]) / L * head * 0.8)
    da = f' stroke-dasharray="{dash}"' if dash else ""
    p.add(f'<path d="M{a[0]:.1f},{a[1]:.1f} Q{c[0]:.1f},{c[1]:.1f} {end[0]:.1f},{end[1]:.1f}" fill="none" '
          f'stroke="{color}" stroke-width="{width}"{da} stroke-linecap="round"/>')
    arrowhead(p, tip, c, color, head)


def inv(s):
    """s with a superscript -1: f^-1."""
    return s + sups(MINUS + "1")


F = it("f")
FINV = inv(it("f"))

# ============================================================
# kare-ters: f(x) = x^2 on [-1, 1], f^-1([1/4, 3]) = [-1, -1/2] and [1/2, 1]
# ============================================================
# the y axis stops just below the x axis so that the bracket label under it stays clear
p = Plot(40, 30, 450, 228, (-1.5, 1.5), (-0.12, 1.4))
p.origin_axes(it("x"), it("y"), (), (), num, num, 0.45)
GUIDE = dict(color=TEXT, width=1.0, dash="4 3", opacity=0.6)
p.line([(-0.5, 0.25), (0.5, 0.25)], **GUIDE)
p.line([(-1.0, 1.0), (1.0, 1.0)], **GUIDE)
for v in (-1.0, -0.5, 0.5, 1.0):
    p.line([(v, 0.0), (v, v * v)], **GUIDE)
p.line(graph_pts(lambda x: x * x, -1.0, 1.0, 200), TEXT, 2.4)
# the bars: f^-1(B) on the x axis, f(f^-1(B)) on the y axis
p.line([(-1.0, 0.0), (-0.5, 0.0)], THEORY, 5.0)
p.line([(0.5, 0.0), (1.0, 0.0)], THEORY, 5.0)
p.line([(0.0, 0.25), (0.0, 1.0)], PRACTICE, 5.0)
p.points([(-0.5, 0.25), (0.5, 0.25), (-1.0, 1.0), (1.0, 1.0)], TEXT, 3.8)
for v, s in ((-1.0, MINUS + "1"), (-0.5, MINUS + "1/2"), (0.5, "1/2"), (1.0, "1")):
    p.label(v, 0.0, s, 0, 17, TEXT, 11, "middle")
p.label(0.0, 0.25, "1/4", -7, -5, TEXT, 11, "end")
p.label(0.0, 1.0, "1", -7, -5, TEXT, 11, "end")
p.label(0.0, 1.12, F + "(" + FINV + "(" + it("B") + ")) = [1/4, 1]", 7, 0, PRACTICE, 12)
# one bracket names both pieces of f^-1(B)
YB = -0.25
for s in (1, -1):
    p.line([(s * 0.21, YB), (s * 0.75, YB), (s * 0.75, -0.045)], THEORY, 1.1, None, 0.9)
p.label(0.0, YB, FINV + "(" + it("B") + ")", 0, 4, THEORY, 12, "middle")
save("kare-ters", figure(
    530, 320, [p],
    "<em>f</em>(<em>x</em>) = <em>x</em><sup>2</sup>, <em>f</em> : [&#8722;1, 1] &#8594; &#8477; ve "
    "<em>B</em> = [1/4, 3]. Ters görüntü <em>f</em><sup>&#8722;1</sup>(<em>B</em>) = [&#8722;1, &#8722;1/2] ile "
    "[1/2, 1] aralıklarından oluşur (mavi); bu noktaların görüntüleri <em>f</em>(<em>f</em><sup>&#8722;1</sup>(<em>B</em>)) "
    "= [1/4, 1] aralığını doldurur (turuncu). <em>B</em>'nin (1, 3] kısmına hiçbir nokta gitmez.",
    aria="Parabola y = x^2 over [-1, 1]; the intervals [-1, -1/2] and [1/2, 1] on the x axis map onto "
         "[1/4, 1] on the y axis, with dashed guides at heights 1/4 and 1"))

# ============================================================
# ters-goruntu: B(a, delta_a) and D lands inside B(f(a), eps_a), which lies in U
# ============================================================
PPU, GAP = 76, 70
XR, YR = (-0.5, 3.5), (-0.8, 2.5)
W1 = PPU * (XR[1] - XR[0])
left = equal_panel(24, 20, PPU, XR, YR)
right = equal_panel(24 + W1 + GAP, 20, PPU, XR, YR)
A, DA = (1.0, 0.0), 0.5
RU = 1.2
TU = math.acos(-1.0 / RU)                      # where the circle about a meets x = 0
pre = [(0.0, 0.0), (1.0 + RU, 0.0)] + arc_pts(1.0, 0.0, RU, 0.0, TU, 120)
half = arc_pts(1.0, 0.0, DA, 0.0, math.pi, 80)
left.polygon([(0, 0), (3, 0), (3, 2), (0, 2)], THEORY, 0.07)
left.polygon(pre, THEORY, 0.2)
left.polygon(half, PRACTICE, 0.34)
left.origin_axes("", "", (), (), num, num, 0.35)
left.line([(0, 0), (3, 0), (3, 2), (0, 2), (0, 0)], THEORY, 1.7)
left.line(arc_pts(1.0, 0.0, RU, 0.0, TU, 120), THEORY, 1.8, "6 4")
left.circle(A[0], A[1], DA, PRACTICE, 1.5, "5 3")
left.points([A], TEXT, 3.8)
left.label(A[0], A[1], it("a"), 0, 18, TEXT, 12.5, "middle")
left.label(3.0, 2.0, it("D"), -9, 17, THEORY, 14, "end", True)
left.label(1.0, 0.82, FINV + "(" + it("U") + ")", 0, 4, THEORY, 12.5, "middle")
# the dark half disc is named from below the edge of D, through a short leader
LB = (1.62, -0.42)
left.line([(1.25, 0.2), (LB[0] - 0.03, LB[1] + 0.12)], TEXT, 0.9, None, 0.7)
left.label(LB[0], LB[1], it("B") + "(" + it("a") + ", " + it(DELTA) + subs("a") + ") &#8745; " + it("D"),
           0, 6, PRACTICE, 12)
# right panel: U and the ball about f(a)
U = [(1.6 + 1.4 * math.cos(t), 1.0 + math.sin(t)) for t in (2 * math.pi * k / 180 for k in range(180))]
FA, EA = (1.2, 0.8), 0.45
# B(f(a), eps_a) must lie in U: every point of its circle satisfies the ellipse inequality
assert max(((FA[0] + EA * math.cos(t) - 1.6) / 1.4) ** 2 + (FA[1] + EA * math.sin(t) - 1.0) ** 2
           for t in (2 * math.pi * k / 360 for k in range(360))) < 1.0
right.polygon(U, THEORY, 0.14)
right.origin_axes("", "", (), (), num, num, 0.35)
right.line(U + [U[0]], THEORY, 1.8, "6 4")
disk_fill(right, FA[0], FA[1], EA, PRACTICE, 0.3)
right.circle(FA[0], FA[1], EA, PRACTICE, 1.5, "5 3")
right.points([FA], TEXT, 3.8)
right.label(FA[0], FA[1], F + "(" + it("a") + ")", 5, 16, TEXT, 12)
right.label(FA[0], FA[1] + EA, it("B") + "(" + F + "(" + it("a") + "), " + it(EPS) + subs("a") + ")", 0, -7,
            PRACTICE, 12, "middle")
right.label(2.75, 1.45, it("U"), 0, 0, THEORY, 14, "middle", True)
# f carries the dark half disc into the small ball
start = (left.X(1.0 + DA * math.cos(0.5)) + 3, left.Y(DA * math.sin(0.5)) + 2)
end = (right.X(FA[0] - EA * 0.94) - 3, right.Y(FA[1] - EA * 0.34) + 1)
ctrl = ((start[0] + end[0]) / 2, max(start[1], end[1]) + 62)
bezier_arrow(left, start, ctrl, end, TEXT, 1.4, None, 8.0)
# the label sits just above the curve, in the gap between the panels
tm = 0.62
mid = ((1 - tm) ** 2 * start[0] + 2 * tm * (1 - tm) * ctrl[0] + tm ** 2 * end[0],
       (1 - tm) ** 2 * start[1] + 2 * tm * (1 - tm) * ctrl[1] + tm ** 2 * end[1])
left.text_px(mid[0], mid[1] - 10, F, TEXT, 13.5, "middle")
save("ters-goruntu", figure(
    24 + 2 * W1 + GAP + 24, 20 + PPU * (YR[1] - YR[0]) + 12, [left, right],
    "<em>D</em> = [0, 3] &#215; [0, 2] ve <em>a</em> = (1, 0). <em>U</em> açık olduğundan <em>f</em>(<em>a</em>) "
    "merkezli <em>B</em>(<em>f</em>(<em>a</em>), <em>&#949;<sub>a</sub></em>) yuvarı <em>U</em>'nun içinde kalır; "
    "süreklilik, <em>D</em>'nin <em>B</em>(<em>a</em>, <em>&#948;<sub>a</sub></em>) içindeki parçasını (turuncu yarım "
    "disk) bu yuvara götürür. Dolayısıyla bu parça <em>f</em><sup>&#8722;1</sup>(<em>U</em>) içindedir; yuvarın "
    "<em>D</em> dışında kalan alt yarısı hakkında bir şey söylenmez.",
    css_class=WIDE,
    aria="Left: the rectangle D with the region f inverse of U around a = (1, 0) on its lower edge and the half disc "
         "of B(a, delta) inside D. Right: the ellipse U with a small ball about f(a) inside it; an arrow f joins "
         "the half disc to the small ball"))

# ============================================================
# ters-sureksiz: f(t) = (cos t, sin t) on [0, 2 pi); its inverse jumps at (1, 0)
# ============================================================
TP = 2 * math.pi
PY = 95
left = Plot(30, 24, 7.5 * 44, 2.8 * PY, (-0.5, 7.0), (-1.4, 1.4))
GAP = 104
right = equal_panel(30 + 7.5 * 44 + GAP, 24, PY, (-1.4, 1.4), (-1.4, 1.4))
TK = [TP - 1 / k for k in range(1, 6)]
PK = [(math.cos(1 / k), -math.sin(1 / k)) for k in range(1, 6)]
# the number line and [0, 2 pi)
left.arrow((-0.5, 0.0), (7.0, 0.0), TEXT, 1.1, 7.0, None, 0.45)
left.line([(0.0, 0.0), (TP, 0.0)], THEORY, 3.2)
for v, s in ((0.0, "0"), (math.pi, PI_S), (TP, "2" + PI_S)):
    left.line([(v, -0.06), (v, 0.06)], TEXT, 1.0, None, 0.6)
    left.label(v, 0.0, s, 0, 20, TEXT, 11.5, "middle")
left.points([(t, 0.0) for t in TK], PRACTICE, 2.8)
left.points([(0.0, 0.0)], THEORY, 4.4)
hollow(left, (TP, 0.0), THEORY, 4.4, 1.8)
left.label(1.6, 0.0, "[0, 2" + PI_S + ")", 0, -10, THEORY, 12.5, "middle")
left.arrow((4.75, 0.34), (6.15, 0.34), PRACTICE, 1.4, 7.0)
left.label(5.45, 0.34, it("t") + subs(it("k")) + " " + TO + " 2" + PI_S, 0, -8, PRACTICE, 12, "middle")
# the unit circle, f(0) = (1, 0) and the points p_k = f(t_k)
right.origin_axes("", "", (), (), num, num, 0.3)
right.circle(0, 0, 1, THEORY, 2.2)
right.points(PK, PRACTICE, 2.8)
right.points([(1.0, 0.0)], THEORY, 5.2)
# inside the circle: outside, the label would run into the axis arrow and off the canvas
right.label(1.0, 0.0, "(1, 0) = " + F + "(0)", -11, -9, TEXT, 12, "end")
arc = arc_pts(0, 0, 1.17, -1.18, -0.3, 60)
right.line(arc[:-1], PRACTICE, 1.4)
right.arrow(arc[-4], arc[-1], PRACTICE, 1.4, 7.0)
right.label(1.17 * math.cos(-1.18), 1.17 * math.sin(-1.18), it("p") + subs(it("k")) + " " + TO + " (1, 0)",
            6, 18, PRACTICE, 12)
right.label(0.0, -1.4, FINV + "(" + it("p") + subs(it("k")) + ") = " + it("t") + subs(it("k")) + " " + TO
            + " 2" + PI_S + ", ama " + FINV + "(1, 0) = 0", 0, 22, TEXT, 12, "middle")
# f to the right, f^-1 back to the left
ax0, ax1 = left.X(7.0) + 14, right.X(-1.4) - 4
ym = left.Y(0.0)
left.add(f'<line x1="{ax0:.1f}" y1="{ym - 16:.1f}" x2="{ax1 - 7:.1f}" y2="{ym - 16:.1f}" stroke="{TEXT}" stroke-width="1.5"/>')
arrowhead(left, (ax1, ym - 16), (ax0, ym - 16), TEXT, 8.0)
left.add(f'<line x1="{ax1:.1f}" y1="{ym + 16:.1f}" x2="{ax0 + 7:.1f}" y2="{ym + 16:.1f}" stroke="{TEXT}" '
         f'stroke-width="1.5" stroke-dasharray="5 3"/>')
arrowhead(left, (ax0, ym + 16), (ax1, ym + 16), TEXT, 8.0)
left.text_px((ax0 + ax1) / 2, ym - 24, F, TEXT, 13, "middle")
left.text_px((ax0 + ax1) / 2, ym + 36, FINV, TEXT, 13, "middle")
save("ters-sureksiz", figure(
    30 + 7.5 * 44 + GAP + 2.8 * PY + 90, 24 + 2.8 * PY + 36, [left, right],
    "<em>f</em>(<em>t</em>) = (cos <em>t</em>, sin <em>t</em>), <em>f</em> : [0, 2&#960;) &#8594; &#8477;<sup>2</sup>. "
    "<em>t<sub>k</sub></em> = 2&#960; &#8722; 1/<em>k</em> noktaları (<em>k</em> = 1, &#8230;, 5) 2&#960;'ye "
    "yaklaşır; görüntüleri <em>p<sub>k</sub></em> = (cos(1/<em>k</em>), &#8722;sin(1/<em>k</em>)) ise çember "
    "üzerinde alttan (1, 0) = <em>f</em>(0) noktasına yaklaşır. Ters fonksiyon <em>p<sub>k</sub></em>'yı "
    "<em>t<sub>k</sub></em>'ya götürdüğünden (1, 0)'da sürekli değildir.",
    css_class=WIDE,
    aria="Left: the interval from 0 to 2 pi on a number line with 0 filled, 2 pi hollow and points t_k "
         "approaching 2 pi. Right: the unit circle with f(0) = (1, 0) and the points p_k approaching it from "
         "below; arrows f and f inverse between the panels"))

# ============================================================
# heine-cantor: finitely many balls B(a_j, delta_j) cover K; delta = min delta_j works everywhere
# ============================================================
BALLS = [((1.0, 1.5), 0.8), ((1.9, 1.1), 0.7), ((2.8, 1.8), 0.8), ((3.6, 1.2), 0.7), ((4.3, 1.9), 0.7)]
AJ, DJ = BALLS[2]
XP, SP = (3.3, 1.45), (3.75, 1.6)
# the outline of K: a closed Catmull-Rom curve through these points, kept inside the union of the balls
CTRL = [(0.45, 1.5), (0.6, 1.12), (0.95, 0.9), (1.4, 0.8), (1.85, 0.6), (2.2, 0.7), (2.5, 1.03),
        (2.8, 1.2), (3.1, 0.96), (3.45, 0.7), (3.8, 0.76), (4.1, 1.06), (4.35, 1.34), (4.7, 1.52),
        (4.88, 1.85), (4.75, 2.25), (4.4, 2.46), (4.0, 2.33), (3.78, 2.0), (3.6, 1.78), (3.45, 2.1),
        (3.1, 2.4), (2.75, 2.5), (2.4, 2.35), (2.15, 1.95), (1.92, 1.6), (1.65, 1.78), (1.3, 2.08),
        (0.9, 2.15), (0.6, 1.95)]


def catmull(ctrl, per=16):
    n = len(ctrl)
    out = []
    for i in range(n):
        p0, p1, p2, p3 = ctrl[i - 1], ctrl[i], ctrl[(i + 1) % n], ctrl[(i + 2) % n]
        for s in range(per):
            t = s / per
            out.append(tuple(0.5 * (2 * p1[j] + (p2[j] - p0[j]) * t
                                    + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t * t
                                    + (3 * p1[j] - p0[j] - 3 * p2[j] + p3[j]) * t ** 3) for j in range(2)))
    return out


def depth(q):
    """How deep q lies inside the union of the balls (negative: outside)."""
    return max(r - math.hypot(q[0] - c[0], q[1] - c[1]) for c, r in BALLS)


K = catmull(CTRL)
# the drawing must tell the truth: K inside the cover, x in the thick ball, s outside it but within
# delta = min delta_j of x (so inside the thin circle), and s in another ball of the cover
assert min(depth(q) for q in K) > 0.03
assert math.dist(XP, AJ) < DJ < math.dist(SP, AJ) < 2 * DJ
assert math.dist(XP, SP) < min(r for _, r in BALLS)
assert depth(SP) > 0
p = equal_panel(24, 20, 105, (0.2, 5.1), (0.1, 3.5))
p.polygon(K, THEORY, 0.15)
p.line(K + [K[0]], THEORY, 1.8)
for j, (c, r) in enumerate(BALLS):
    if j != 2:
        p.circle(c[0], c[1], r, TEXT, 1.2, "5 4", opacity=0.55)
p.circle(AJ[0], AJ[1], 2 * DJ, PRACTICE, 1.3, "4 3", opacity=0.85)
p.circle(AJ[0], AJ[1], DJ, PRACTICE, 2.5, "7 4")
p.points([c for j, (c, _) in enumerate(BALLS) if j != 2], TEXT, 2.6)
p.points([AJ], PRACTICE, 3.4)
p.line([XP, SP], TEXT, 1.6)
p.points([XP, SP], TEXT, 3.6)
p.label(AJ[0], AJ[1], it("a") + subs(it("j")), -6, -7, PRACTICE, 12.5, "end")
p.label(XP[0], XP[1], it("x"), -8, 5, TEXT, 13, "end")
p.label(SP[0], SP[1], it("s"), 8, 5, TEXT, 13)
p.label(0.66, 1.5, it("K"), 0, 5, THEORY, 15, "middle", True)
p.label(AJ[0], AJ[1] + DJ, it("B") + "(" + it("a") + subs(it("j")) + ", " + it(DELTA) + subs(it("j")) + ")",
        0, -7, PRACTICE, 12, "middle")
p.label(AJ[0] + 2 * DJ * math.cos(math.radians(140)), AJ[1] + 2 * DJ * math.sin(math.radians(140)),
        it("B") + "(" + it("a") + subs(it("j")) + ", " + it(DELTA) + "(" + it("a") + subs(it("j")) + "))",
        -6, -4, PRACTICE, 12, "end")
# the length of the segment, named outside K through a short leader
LS = (4.32, 0.9)
p.line([((XP[0] + SP[0]) / 2, (XP[1] + SP[1]) / 2 - 0.03), (LS[0] - 0.03, LS[1] + 0.1)], TEXT, 0.9, None, 0.7)
p.label(LS[0], LS[1], NORM + it("x") + " " + MINUS + " " + it("s") + NORM + " &lt; " + it(DELTA), 0, 4, TEXT, 12)
save("heine-cantor", figure(
    24 + 105 * 4.9 + 24, 20 + 105 * 3.4 + 12, [p],
    "Kompakt <em>K</em> kümesi beş yuvarla örtülür: <em>B</em>(<em>a<sub>j</sub></em>, <em>&#948;<sub>j</sub></em>), "
    "<em>&#948;<sub>j</sub></em> = <em>&#948;</em>(<em>a<sub>j</sub></em>)/2. Kalın kesikli yuvarın içindeki "
    "<em>x</em> ile &#8214;<em>x</em> &#8722; <em>s</em>&#8214; &lt; <em>&#948;</em> = min <em>&#948;<sub>j</sub></em> "
    "koşulunu sağlayan <em>s</em> bu yuvarın dışına çıkabilir, ama ikisi de <em>a<sub>j</sub></em>'ye "
    "<em>&#948;</em>(<em>a<sub>j</sub></em>)'den yakındır: ince kesikli çemberin içindedir.",
    css_class=WIDE,
    aria="An irregular compact set K covered by five dashed balls; one ball about a_j is highlighted together "
         "with the concentric ball of twice its radius, and two close points x and s, x inside the highlighted "
         "ball and s just outside it but inside the larger one"))
