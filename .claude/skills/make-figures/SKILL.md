---
name: make-figures
description: Adds, fixes, deletes or regenerates course figures (ders-grafik SVG). The steps are the generator script, center_figures, a visual check via PNG and placement inside the .qmd box; also covers the interactive 3D scenes for differential geometry. Use when the user says "grafik/şema ekle" (add a figure/diagram), "şu şekil yanlış/ortalı değil/çok büyük" (this figure is wrong/off-center/too big) or "diyagram az" (too few diagrams), or when a `<!-- FIGURE: … -->` placeholder is left in a draft.
---

# Figure procedure

## 1. Preparation

- `scripts/_figures/` is gitignored and does not exist in a new worktree; run the relevant generator script first.
- `center_figures.py` needs `rsvg-convert` on PATH and Pillow installed.

## 2. Pick the script

Prefixes:

| Script | Prefix |
|---|---|
| `analysis_figures.py` | `analysis-` |
| `analysis2_figures.py` | `analysis2-` |
| `complex_figures.py` | `complex-` |
| `convex_figures.py` | `convex-` |
| `crypto_figures.py` | `crypto-` |
| `diffgeo_figures.py` | `diffgeo-` |
| `finance_figures.py` | `finance-` |
| `probability_figures.py` | `probability-` |
| `topology_figures.py` | `topology-` |
| `stochastic_figures.py` | `figA`…`figG` (not centered) |
| `real_analysis_figures.py` | `real-` |
| `analytic_figures/<key>.py` | `analytic-<key>-` |
| `statistics_figures/<key>.py` | `statistics-<key>-` |
| `diffgeo_figures_extra/<key>.py` | `diffgeo-<key>-` (DG chapters after connection forms; no new figures go into `diffgeo_figures.py`) |

For a new course, write `scripts/<topic>_figures.py` in English:

- Build on `svg_plot.py` for 2D and `svg_plot3.py` for 3D (Camera/Space; azimuth 35°, elevation 22°).
- The docstring must state the correct `dersler/<course>` path and the "figures go INSIDE the box they explain" rule.
- The "always OUTSIDE boxes" sentence in the `complex_figures.py` and `crypto_figures.py` docstrings is outdated; ignore it.

## 3. Write the figure

- Each figure sits in its own section banded by `"# " + "="*60`: `figure(W, H, panels, caption, css_class="ders-grafik" | WIDE, aria="...")`.
- Use the constants `THEORY`, `BASE`, `PRACTICE`, `REMARK`, `TEXT`, `BG` for colors; do not hard-code hex values.
- `Plot.label(x, y, s, dx, dy, …)`: dx/dy are in pixels and positive dy means down.
- The `aria` text is ASCII only and contains no `<`/`>` (rsvg throws an XML error). The caption is Turkish.
- Function and distribution plots have labeled axes; `Plot.grid()` exists for grids.

## 4. Pitfalls

- **Clipping:** `Plot` does not clip. Clip unbounded objects (hyperplane, half-plane, cone, asymptote) to the panel. Ready-made helpers: `clipped()` in `analysis2_figures.py`, `clip_seg`/`clip_poly` in `convex_figures.py`.
- **Aspect ratio:** True circles and Venn diagrams need equal x and y scales (`YR = XR*PH/PW`).
- **Font glyphs:** In the rsvg font ∪ ∖ ∈ ⊂ ⊆ ⋯ ∅ ∧ ∨ ¬ ⇒ ∥ render as boxes; use a word, ASCII or an HTML entity. ∩ ≤ ≥ ≠ − ∞ → ℝ ℕ √ π are fine.
- **Font family:** Never write `font-family` (especially Georgia) into the generated SVG; it once hung the Typst build. `export_figures.lua` already handles the combining overline.
- **Fill:** An opaque fill covers the circle's content; use a semi-transparent fill.
- **Label position:** Do not put a horizontal label beside a slanted line; move the label to the other side or into an empty band.

## 5. Generate and center

1. `python scripts/<x>_figures.py`
2. Then, EVERY time, `python scripts/center_figures.py "<prefix>-*.md"`. Without a pattern only `complex-*.md` is processed. In books where square figures must not drop into the narrow column (24rem) (e.g. analitik-geometri), add `--keep-width`.
3. `python scripts/check_figure_labels.py "scripts/_figures/<prefix>-*.md"` must report `problems: 0`. It finds overlapping labels, labels covering a point, text overflowing the canvas and text smaller than 10 px. It does not see line–label overlaps; check those by eye.

center_figures crops the viewBox to the content with a 14-unit margin. It adds `ders-grafik-dar` to a non-wide figure whose aspect ratio is ≥ 0.72.

## 6. Check by eye

- Convert every new or changed figure to PNG with `rsvg-convert` in both light and dark theme and inspect it with Read.
- Look for: overlapping labels, clipping, a half-plane shaded on the wrong side, viewBox bloat.
- Numbers, intervals and parameters in the figure must match the text of its box exactly.
- If the user reports a wrong diagram, compare every figure of the same kind against its own solution.

## 7. Place

- Paste the contents of `scripts/_figures/<prefix>-<name>.md` (a ```` ```{=html} ```` block) INSIDE the box it explains in the .qmd, right below the relevant paragraph.
- Do not put it in a definition box; put it right below the box. Do not put it right below a `##` heading either.
- When updating, find the old block by its `aria-label` and replace the whole block.
- Do not hand-edit the embedded SVG.
- Normalize line endings when comparing: the generator scripts write CRLF on Windows, while .qmd files are LF.
- Deleting: remove the .qmd block, the banded section in the script and the `scripts/_figures` file together.

## 8. Selection and size

- Add a figure that visualizes a concept or carries the idea of a proof; do not add one that merely restates a theorem as a picture.
- Sizes:
  - `.ders-grafik`: 30rem
  - `.ders-grafik-genis` (WIDE, multi-panel): 39rem
  - `.ders-grafik-dar`: 24rem
- These CSS values affect every course; tell the user if you change them.

## 9. Interactive scenes (diferansiyel-geometri, integral-calculus)

- Each of these books has its own helper module: `dersler/diferansiyel-geometri/ojs/scene3d.js` and `dersler/integral-calculus/ojs/scene3d.js` (the latter adds graphs over regions, Riemann columns, slicing planes, 3D and 2D vector fields, curtains and grid curves; its header documents the API).
- A ```` ```{ojs} ```` cell uses `//| echo: false` and imports from the book's module (`../ojs/scene3d.js` from a chapter in a subfolder, `./ojs/scene3d.js` from the book root). Plotly is loaded as `plotly.js-dist-min@2.35.2`.
- The scene sits inside `:::: {.content-visible when-format="html:js"}`, not inside `.cozum`/`.ispat`; a short paragraph starting "**Etkileşimli sahne: …**" says what to drag or slide.
- OJS variables are page-global; each scene uses its own prefix (the chapter key in integral-calculus).
- For PDF and EPUB a static SVG is also placed at the same spot.
- The hidden browser pane does not run OJS cells; test scenes on a visible pane or a test copy of the page.

## 10. Verify

Run `python scripts/build.py <course>`. Then look at the figure in `_site` (inside the box and centered?) and in the PDF.
