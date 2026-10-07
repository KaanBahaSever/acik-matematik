---
name: site-infra
description: Used for site design and infrastructure changes. Covers styles/global.css, the Lua filters (collapsible, downloads, export_*), the build.py and export.py pipeline, _kitap-ortak.yml and deploy.yml; includes the known pitfalls, the design language and verification at every width. Use when the user asks for or complains about something visual ("içerik çok geniş" (the content is too wide), "mobilde kayıyor" (it scrolls sideways on mobile), "formülün üstü kesik" (the top of the formula is cut off), "kutular tasarıma uymuyor" (the boxes do not fit the design)), or when a Lua filter, a build/export script or CI is about to be touched.
---

# Design and infrastructure procedure

The binding rules are in `.claude/rules/altyapi.md`.

## 1. Read first

- Sections of `styles/global.css`:
  - PAGE GRID
  - 1 theme variables
  - 2–3 box styles
  - 3b collapsible blocks
  - 3c links
  - 3d callouts
  - 10 mobile layout, 10b mobile table of contents
  - 11–13 multi-part courses and curriculum
  - 15 equation spacing
  - 17 in-course drawings
  - 3D scenes, download panel
- Also read the header comment of the relevant Lua filter.

## 2. CSS pitfalls

- The content link rule `#quarto-document-content a:not(...)` has high specificity. To override it, use the same prefix and the same `:not` guards.
- `:has()` inside `:has()` is invalid. `:is()` silently swallows an invalid argument.
- Put a selector containing `:has()` into a rule of its own and add an `@supports not selector(:has(*))` fallback.
- Do not give `.theorem-title` and `.remark-title` `display:inline-flex`. Create the gap with `margin-right` on `::before`.
- A figure inside a box is centered: `.theorem/.collapsible-body/.callout-body figure.ders-grafik { margin-left/right: auto }`.

## 3. Keep the design language

General principle: plain and without animation. The catalog changes color only on hover.

- **Callouts:** drawn as siblings of the theorem boxes. The Bootstrap icon is hidden; they use a glyph in the title, an `--academic-bg` background, a left stripe and `0 8px 8px 0` corners.
- **Callout glyphs:**

  | Type | Glyph and style |
  |---|---|
  | note | ✎, gray dotted |
  | tip | ✦, turquoise |
  | important | !, brick red |
  | warning | △, amber dashed |
  | caution | ◇, amber |

- **Box glyphs:** all the same visual size.
  - Theorem ▲. The proof strip is also ▲ and rotates 180° when opened.
  - Definition ≡.
  - Example and exercise ▷. The solution strip is also ▷ and rotates 90° when opened.
- **Links:** content links are neither blue nor underlined. Curriculum links use `--color-theory`, headings use `--color-base`.
- **Curriculum page:** the content sits in a single outer box with no small boxes inside it. Sub-course `##` headings stay outside the box. The gap sits right below the large heading (h1).
- **Mobile:** lists do not shift inward. A display formula that comes right after a box title does not stick to the title.

## 4. Page grid

- Variables:
  - `--am-page-max: 1880px`
  - `--am-edge: 1.25rem`
  - `--am-side: clamp(10.5rem,15vw,16rem)`
  - `--am-gap: 1.5em`
  - `--am-slack: clamp(1.5rem,3vw,4rem)`
  - `--am-content: 48rem`
- 1rem = 17.6px, because the root font size is 1.1em.
- The grid is built on `body.floating #quarto-content.page-layout-article`. There is a separate grid for 768–991 px.
- Portal pages (`/`, `/dersler/`) stay on Quarto's article grid. The book layout must not affect them.
- The mobile table of contents appears at ≤ 767.98px via `scripts/mobile-toc.html`.
- The back-to-catalog link stays `href="/../"` in `_kitap-ortak.yml`. Course links in the catalog have the form `<course>/`.

## 5. Lua filters

- Quarto turns callouts into a custom node before user filters run. So use the `Callout` handler, not `Div`; `el.title` is a single Block.
- Use `quarto.doc.input_file` for the source path. In the combined export render this value returns `index.qmd`.
- The filter list is in `_kitap-ortak.yml`. A filter change rebuilds every book.

## 6. Build and export pipeline

- Units are built from a disposable copy at `_export-src/<course>/`, exactly two levels below the root.
- Do not run two exports of the same course in parallel; `.quarto` gets locked.
- Required settings:
  - `book.author` is mandatory.
  - Dates use an ISO `date` together with `date-format`.
  - The PDF has a 25 MiB limit.
- Debugging: `python scripts/export.py <course> --keep`, then `cd _export-src/<course> && quarto render --to typst`.
- Known bug: `export_links.lua` also redirects in-book `../<subfolder>/x.qmd` links to the site. When fixing it, rewrite only links to sibling books, i.e. those that have a `dersler/<x>/_quarto.yml`.

## 7. CI

- Changes to `CLAUDE.md`, `.claude/**`, README and LICENCE do not trigger CI (`paths-ignore`).
- See `altyapi.md` for the rules.

## 8. Verify

- For CSS, `python scripts/build.py <course> --no-export` is enough.
- Try a Lua or `_kitap-ortak.yml` change on a single book first.
- Measure the five widths with `check_layout.py`. Also look at the light and dark themes and at the catalog and portal pages.
- Prove the root cause by measurement.

## 9. Report

In the report, state clearly the site-wide impact and any changes you made beyond what was asked.
