# -*- coding: utf-8 -*-
"""
Figures of the chapter "Cauchy–Euler Denklemi"
(dersler/diferansiyel-denklemler/cauchy-euler-denklemi.qmd).

Figures go INSIDE the box they explain (theorem, proof, example, solution,
exercise or callout), never inside a definition box and never directly under
a heading. The figures are NOT produced at build time. Run

    python scripts/diffeq_figures/euler.py
    python scripts/center_figures.py "diffeq-euler-*.md"
    python scripts/check_figure_labels.py "scripts/_figures/diffeq-euler-*.md"

and paste the markup of scripts/_figures/diffeq-euler-<name>.md into the .qmd.
The captions are Turkish on purpose; the aria labels are plain ASCII.
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import save, clip_runs, linspace  # noqa: E402
from svg_plot import Plot, figure, sup, panel_title, hollow, BASE, PRACTICE, TEXT, THEORY, WIDE  # noqa: E402

PREFIX = "diffeq-euler-"
MINUS = "&#8722;"


def it(s):
    """Italic math letter inside an SVG <text>."""
    return f'<tspan font-style="italic">{s}</tspan>'


def power(exp):
    """The label x^exp with a raised exponent."""
    return it("x") + sup(exp, size=10)


# ============================================================
# Power functions x^r near x = 0 (callout after the root-case theorem)
# ============================================================
def fig_powers():
    p = Plot(50, 30, 300, 220, (0, 2.6), (0, 3.2))
    p.grid(xs=(1, 2), ys=(1, 2, 3))
    p.axes(xticks=(0, 1, 2), yticks=(0, 1, 2, 3), xlabel="x", ylabel="y")

    curves = [  # exponent, colour, dash, label, label y-nudge (px)
        (2.0, THEORY, None, power("2"), 0),
        (1.0, THEORY, "6 4", power("1"), 0),
        (0.5, BASE, None, power("1/2"), 0),
        (0.0, TEXT, "3 3", power("0"), 0),
        (-0.5, PRACTICE, "6 4", power(f"{MINUS}1/2"), -2),
        (-1.0, PRACTICE, None, power(f"{MINUS}1"), 6),
    ]
    # geometric sampling near 0 (steep branches), uniform further right
    xs = [0.005 * (0.6 / 0.005) ** (i / 150) for i in range(150)] + linspace(0.6, 2.5, 60)
    eps = 1e-9   # exact exits through the top edge y = 3.2
    xs = sorted(xs + [1 / 3.2 ** 2 + eps, 1 / 3.2 + eps, math.sqrt(3.2) - eps])
    for r, color, dash, _, _ in curves:
        pts = [(x, x ** r) for x in xs]
        for run in clip_runs(pts, p):
            p.line(run, color=color, width=1.9, dash=dash, opacity=0.85 if r == 0 else 1.0)
    for r, color, _, label, nudge in curves:
        if r == 2.0:
            xe = math.sqrt(3.2)
            p.label(xe, 3.2, label, dx=7, dy=12, color=color)
        else:
            p.label(2.5, 2.5 ** r, label, dx=7, dy=4 + nudge, color=color)
    p.points([(1, 1)], color=TEXT, r=3.6)

    svg = figure(400, 290, [p],
                 "Birinci durumdaki kuvvet fonksiyonları: üs pozitifken çözüm x sıfıra yaklaşırken "
                 "sıfıra gider, negatifken sınırsız büyür; bütün eğriler (1, 1) noktasından geçer.",
                 aria="Graphs of x to the powers 2, 1, 1/2, 0, -1/2 and -1 for x between 0 and 2.5; "
                      "positive powers tend to 0 and negative powers blow up as x tends to 0, "
                      "all curves pass through the point (1, 1).")
    save(PREFIX, "kuvvetler", svg)


# ============================================================
# Logarithmic oscillation: y = sqrt(x) cos(3 ln x) in x and in t = ln x
# (example 4x^2 y'' + 37 y = 0, y(1) = 1, y'(1) = 1/2)
# ============================================================
def fig_log_oscillation():
    zeros_t = [math.pi / 6 + k * math.pi / 3 for k in range(-3, 1)]   # -2.618 ... 0.524
    # left panel: the x variable
    px = Plot(52, 46, 240, 200, (0, 2.4), (-1.7, 1.7))
    px.origin_axes(xlabel="x", ylabel="y", xticks=(1, 2), yticks=(-1, 1))
    ts = linspace(-8.0, math.log(2.4), 600)
    env = [(math.exp(t), math.exp(t / 2)) for t in linspace(-8.0, math.log(2.4), 120)]
    px.line(env, color=TEXT, width=1.1, dash="4 3", opacity=0.55)
    px.line([(a, -b) for a, b in env], color=TEXT, width=1.1, dash="4 3", opacity=0.55)
    px.line([(math.exp(t), math.exp(t / 2) * math.cos(3 * t)) for t in ts], color=THEORY, width=1.9)
    for z in zeros_t:
        hollow(px, (math.exp(z), 0.0), color=PRACTICE, r=3.2, width=1.5)
    px.points([(1, 1)], color=BASE, r=3.8)
    px.label(1, 1, "(1, 1)", dx=-6, dy=-9, anchor="end", size=11)
    px.label(2.4, math.sqrt(2.4), it("y") + " = " + f"&#8730;{it('x')}", dx=-4, dy=-8, anchor="end",
             color=TEXT, size=11)
    panel_title(px, "x değişkeninde")

    # right panel: the t variable
    pt = Plot(352, 46, 240, 200, (-4.6, 1.0), (-1.7, 1.7))
    pt.origin_axes(xlabel="t", ylabel="y", xticks=(-4, -3, -2, -1), yticks=(-1, 1))
    tt = linspace(-4.6, 1.0, 400)
    te = linspace(-4.6, 1.0, 60)
    pt.line([(t, math.exp(t / 2)) for t in te], color=TEXT, width=1.1, dash="4 3", opacity=0.55)
    pt.line([(t, -math.exp(t / 2)) for t in te], color=TEXT, width=1.1, dash="4 3", opacity=0.55)
    pt.line([(t, math.exp(t / 2) * math.cos(3 * t)) for t in tt], color=THEORY, width=1.9)
    for z in zeros_t:
        hollow(pt, (z, 0.0), color=PRACTICE, r=3.2, width=1.5)
    pt.points([(0, 1)], color=BASE, r=3.8)
    pt.label(0, 1, "(0, 1)", dx=10, dy=4, size=11)
    panel_title(pt, "t = ln x değişkeninde")

    svg = figure(620, 290, [px, pt],
                 "Solda 4x²y″ + 37y = 0, y(1) = 1, y′(1) = 1/2 probleminin çözümü olan "
                 "y = √x cos(3 ln x) eğrisi ve kesikli çizgiyle ±√x zarfı; sağda aynı çözüm "
                 "t = ln x değişkeninde. Sağda eşit aralıklı olan sıfırlar (halkalar), solda "
                 "x = 0 noktasına doğru giderek sıkışır.",
                 css_class=WIDE,
                 aria="Two panels. Left: y = sqrt(x) cos(3 ln x) for x between 0 and 2.4 with the "
                      "dashed envelope plus and minus sqrt(x); its zeros crowd towards x = 0. "
                      "Right: the same solution in the variable t = ln x, y = exp(t/2) cos(3t), whose "
                      "zeros are equally spaced. The initial point is (1, 1) on the left and (0, 1) "
                      "on the right.")
    save(PREFIX, "log-salinim", svg)


if __name__ == "__main__":
    fig_powers()
    fig_log_oscillation()
