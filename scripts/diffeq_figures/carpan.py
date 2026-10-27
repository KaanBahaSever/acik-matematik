# -*- coding: utf-8 -*-
"""
Figures of the chapter "İntegrasyon Çarpanı"
(dersler/diferansiyel-denklemler/integrasyon-carpani.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution or
exercise), never inside a definition box and never directly under a heading.
The figures are NOT produced at build time. Run

    python scripts/diffeq_figures/carpan.py
    python scripts/center_figures.py "diffeq-carpan-*.md"
    python scripts/check_figure_labels.py "scripts/_figures/diffeq-carpan-*.md"

and paste the markup of scripts/_figures/diffeq-carpan-<name>.md into the .qmd.
The captions are Turkish on purpose; the aria labels are plain ASCII.
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import save, clip_runs, linspace  # noqa: E402
from svg_plot import Plot, figure, BG, PRACTICE, TEXT, THEORY  # noqa: E402

PREFIX = "diffeq-carpan-"
MINUS = "&#8722;"


def it(s):
    """Italic math letter inside an SVG <text>."""
    return f'<tspan font-style="italic">{s}</tspan>'


def num(v):
    """Tick label with a typographic minus sign and a decimal comma."""
    return f"{v:g}".replace(".", ",").replace("-", MINUS)


def plate_label(p, x, y, s, width_chars, dx=0, dy=0, color=TEXT, size=11.5, anchor="start"):
    """Label on a page-coloured plate, so curves running behind it stay readable."""
    w = width_chars * 0.55 * size
    px, py = p.X(x) + dx, p.Y(y) + dy
    x0 = px - (w / 2 if anchor == "middle" else w if anchor == "end" else 0)
    p.add(f'<rect x="{x0 - 2.5:.1f}" y="{py - 0.8 * size - 1:.1f}" width="{w + 5:.1f}" '
          f'height="{size + 3:.1f}" rx="3" fill="{BG}" opacity="0.9"/>')
    p.label(x, y, s, dx, dy, color, size, anchor)


# ============================================================
# spiral: solution curves r = K e^theta of (x + y) dx + (y - x) dy = 0 (exr-carpan-oben)
# ============================================================
R = 3.0
p = Plot(30, 24, 330, 330, (-R, R), (-R, R))          # equal scales: true spirals
p.polygon([(-R, 0), (R, 0), (R, R), (-R, R)], THEORY, 0.07)
p.origin_axes(xlabel=it("x"), ylabel=it("y"), xticks=(-2, -1, 1, 2), yticks=(-2, -1, 1, 2),
              xfmt=num, yfmt=num)

RMAX = 2.8                                              # every spiral ends on this circle
for n in range(8):
    K = math.exp(-n * math.pi / 4)                      # rotated copies, 45 degrees apart
    th0, th1 = math.log(0.02 / K), math.log(RMAX / K)
    pts = [(K * math.exp(t) * math.cos(t), K * math.exp(t) * math.sin(t)) for t in linspace(th0, th1, 900)]
    # split into the parts above and below the x axis
    runs, cur, sign = [], [], None
    for q in pts:
        s = q[1] > 0
        if sign is None or s == sign:
            cur.append(q)
        else:
            runs.append((sign, cur + [q]))
            cur = [q]
        sign = s
    runs.append((sign, cur))
    for upper, run in runs:
        for part in clip_runs(run, p):
            if upper:
                p.line(part, THEORY, 2.0)
            else:
                p.line(part, THEORY, 1.3, dash="5 4", opacity=0.5)

p.points([(0, 0)], TEXT, 3.2)
plate_label(p, -R, R, f"{it('y')} &gt; 0", 4.2, dx=8, dy=18, color=THEORY, size=12)

svg = figure(400, 390, [p],
             "Denklemin çözüm eğrileri: orijin çevresinde dolanan logaritmik spiraller. Kesiksiz çizilen "
             "parçalar üst yarı düzlemde kalır; bulduğumuz kapalı çözüm bu parçaları verir. Kesikli "
             "parçalar aynı spirallerin alt yarı düzlemdeki devamıdır.",
             aria="Logarithmic spirals r = K e^theta for eight values of K; the parts in the upper half plane "
                  "are solid, the parts below the x axis are dashed.")
save(PREFIX, "spiraller", svg)
