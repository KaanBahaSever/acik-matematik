# -*- coding: utf-8 -*-
"""Center and trim the generated SVG figures.

The plotting helpers cannot measure text, so a figure's drawn content often
sits off-center inside its viewBox (or leaves large empty margins). This
script fixes that after generation: each figure in scripts/_figures/ is
rasterized (light and dark palette), the bounding box of the actual content
is measured, and the viewBox is rewritten so the content sits centered with
a uniform margin.

The measured box also decides how wide a column the figure gets: an SVG fills
its <figure>, so a nearly square drawing would be twice as tall on screen as a
two-panel strip. Those get the .ders-grafik-dar class (see set_width_class).

Authoring flow:  python scripts/complex_figures.py
                 python scripts/center_figures.py            # this script
                 ...then paste/refresh the markup into the .qmd files.

Needs `rsvg-convert` on PATH and Pillow — author-side only; CI never runs it.

Usage:  python scripts/center_figures.py [glob]     (default: complex-*.md)
"""
import pathlib
import re
import subprocess
import sys
import tempfile

from PIL import Image, ImageChops

sys.stdout.reconfigure(encoding="utf-8")

FIG_DIR = pathlib.Path(__file__).resolve().parent / "_figures"
PAD = 14          # margin around the content, in viewBox units
PROBE = 80        # extra room added around the old viewBox to catch overflow
TOL = 7           # per-channel background tolerance
SCALE = 2
TALL = 0.72       # height/width above which a drawing gets the narrow column

PALETTES = (
    ({"--academic-text": "#2C2A27", "--academic-bg": "#FAF6EE", "--color-theory": "#2B4C7E",
      "--color-base": "#0D6E6A", "--color-practice": "#9C3F1E", "--color-remark": "#5C5346"}, "#FAF6EE"),
    ({"--academic-text": "#E6E1DA", "--academic-bg": "#1E1D1B", "--color-theory": "#8AB4F8",
      "--color-base": "#4DB6AC", "--color-practice": "#E8A088", "--color-remark": "#A89F91"}, "#1E1D1B"),
)

VIEWBOX = re.compile(r'viewBox="([-\d. ]+)"')
FIGCLASS = re.compile(r'<figure class="([^"]+)">')


def content_bbox(svg, vb, colors, bg):
    """Bounding box of non-background pixels, in viewBox coordinates."""
    x, y, w, h = vb
    probe = (x - PROBE, y - PROBE, w + 2 * PROBE, h + 2 * PROBE)
    s = svg
    for k, v in colors.items():
        s = s.replace(f"var({k})", v)
    s = VIEWBOX.sub(f'viewBox="{probe[0]} {probe[1]} {probe[2]} {probe[3]}"', s, count=1)
    s = ('<?xml version="1.0" encoding="UTF-8"?>\n'
         + s.replace("<svg ", '<svg xmlns="http://www.w3.org/2000/svg" font-family="Georgia, serif" ', 1))
    with tempfile.TemporaryDirectory() as td:
        sp, pp = pathlib.Path(td) / "f.svg", pathlib.Path(td) / "f.png"
        sp.write_text(s, encoding="utf-8")
        subprocess.run(["rsvg-convert", "-w", str(int(probe[2] * SCALE)), "-b", bg,
                        "-o", str(pp), str(sp)], check=True)
        im = Image.open(pp).convert("RGB")
    bgc = tuple(int(bg[i:i + 2], 16) for i in (1, 3, 5))
    diff = ImageChops.difference(im, Image.new("RGB", im.size, bgc)).convert("L")
    box = diff.point(lambda v: 255 if v > TOL else 0).getbbox()
    if box is None:
        return None
    sc = probe[2] / im.size[0]
    return (probe[0] + box[0] * sc, probe[1] + box[1] * sc,
            probe[0] + box[2] * sc, probe[1] + box[3] * sc)


def set_width_class(body, ratio):
    """Give nearly square drawings the narrow column, wide strips the wide one.

    The SVG fills its figure's width, so the rendered height is that width
    times the aspect ratio; without this a square panel is twice as tall on
    screen as a two-panel strip. Idempotent: the class is recomputed, never
    appended twice.
    """
    m = FIGCLASS.search(body)
    if not m:
        return body
    names = [c for c in m.group(1).split() if c != "ders-grafik-dar"]
    if "ders-grafik-genis" not in names and ratio >= TALL:
        names.append("ders-grafik-dar")
    return body.replace(m.group(0), '<figure class="%s">' % " ".join(names), 1)


def main():
    pattern = sys.argv[1] if len(sys.argv) > 1 else "complex-*.md"
    changed = 0
    for f in sorted(FIG_DIR.glob(pattern)):
        body = f.read_text(encoding="utf-8")
        m = VIEWBOX.search(body)
        vb = tuple(float(v) for v in m.group(1).split())
        if len(vb) == 2:
            vb = (0.0, 0.0) + vb
        svg = body[body.index("<svg"):body.index("</svg>") + 6]
        boxes = [content_bbox(svg, vb, colors, bg) for colors, bg in PALETTES]
        boxes = [b for b in boxes if b]
        if not boxes:
            print(f"  !! no content: {f.name}")
            continue
        x0 = min(b[0] for b in boxes) - PAD
        y0 = min(b[1] for b in boxes) - PAD
        x1 = max(b[2] for b in boxes) + PAD
        y1 = max(b[3] for b in boxes) + PAD
        new = f'viewBox="{x0:.1f} {y0:.1f} {x1 - x0:.1f} {y1 - y0:.1f}"'
        old = m.group(0)
        out = body.replace(old, new, 1) if new != old else body
        out = set_width_class(out, (y1 - y0) / (x1 - x0))
        if out != body:
            f.write_text(out, encoding="utf-8")
            changed += 1
            print(f"  {f.name}: {old[9:-1]} -> {new[9:-1]}")
    print(f"centered {changed} figures")


if __name__ == "__main__":
    main()
