# -*- coding: utf-8 -*-
"""
Figures of the chapter "Parametrelerin Değişimi Yöntemi"
(dersler/diferansiyel-denklemler/parametrelerin-degisimi-yontemi.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box and never directly under a heading.
The figures are NOT produced at build time. Run

    python scripts/diffeq_figures/parametre.py
    python scripts/center_figures.py "diffeq-parametre-*.md"
    python scripts/check_figure_labels.py "scripts/_figures/diffeq-parametre-*.md"

and paste the markup of scripts/_figures/diffeq-parametre-<name>.md into the .qmd.
The captions are Turkish on purpose; the aria labels are plain ASCII.
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import save, graph  # noqa: E402
from svg_plot import Plot, figure, BASE, PRACTICE, TEXT, THEORY  # noqa: E402

PREFIX = "diffeq-parametre-"
PI_S = "&#960;"


def it(s):
    """Italic math letter inside an SVG <text>."""
    return f'<tspan font-style="italic">{s}</tspan>'


# ============================================================
# csc-ivp: y'' + y = csc x, y(pi/2) = 1, y'(pi/2) = 0 on (0, pi);
# solution y = sin x + (pi/2 - x) cos x + sin x ln(sin x), homogeneous part sin x
# ============================================================
def y_ivp(x):
    s = math.sin(x)
    return s + (math.pi / 2 - x) * math.cos(x) + s * math.log(s)


TICKS = {0.0: "0", math.pi / 2: f"{PI_S}/2", math.pi: PI_S, 1.0: "1"}


def tick(v):
    for k, s in TICKS.items():
        if abs(v - k) < 1e-9:
            return s
    return f"{v:g}"


p = Plot(52, 26, 380, 230, (0.0, 3.45), (0.0, 1.85))
p.axes([0.0, math.pi / 2, math.pi], [0.0, 1.0, math.pi / 2], xlabel="x", ylabel="y", xfmt=tick, yfmt=tick)
# the right end of the interval, where csc x is undefined
p.vline(math.pi, 0.0, 1.85, TEXT, "5 4", 0.55)
p.label(math.pi, 1.85, f"{it('x')} = {PI_S}", 6, 10, TEXT, 11, "start")
# homogeneous part sin x (dashed) and the solution (solid)
graph(p, math.sin, 0.0, math.pi, n=300, color=BASE, width=1.8, dash="6 4")
graph(p, y_ivp, 0.004, math.pi - 0.004, n=600, color=THEORY, width=2.3)
# limits pi/2 at both ends are not attained: hollow dots
p.hollow_points([(0.0, math.pi / 2), (math.pi, math.pi / 2)], THEORY, 4.0)
# initial point
p.points([(math.pi / 2, 1.0)], PRACTICE, 4.5)
p.label(math.pi / 2, 1.0, f"({PI_S}/2, 1)", 0, -14, PRACTICE, 11.5, "middle")
# curve labels
p.label(2.62, y_ivp(2.62), it("y"), 2, -10, THEORY, 12.5, "start")
p.label(2.55, math.sin(2.55), f"sin {it('x')}", 13, 4, BASE, 12, "start")

save(PREFIX, "csc-ivp", figure(
    470, 290, [p],
    "<em>y</em>'' + <em>y</em> = csc <em>x</em>, <em>y</em>(&#960;/2) = 1, <em>y</em>'(&#960;/2) = 0 "
    "başlangıç değer probleminin çözümü (düz eğri) ile homojen kısmı sin <em>x</em> (kesikli eğri). "
    "Çözüm, csc <em>x</em>'in sürekli olduğu (0, &#960;) aralığının tamamında tanımlıdır. Uçlara yaklaşırken "
    "sağ taraf sınırsız büyür, çözüm sin <em>x</em>'ten ayrılır ve &#960;/2 değerine yaklaşır "
    "(boş noktalar; uç noktalar aralığa ait değildir).",
    aria="Solution of y'' + y = csc x with y(pi/2) = 1 and y'(pi/2) = 0 on the interval (0, pi), "
         "drawn with its homogeneous part sin x; the solution tends to pi/2 at both ends"))
