---
name: run-checks
description: The check chain run after a .qmd, figure, CSS or infrastructure change, before delivery and before a commit. It covers structural checks, box and formula checks, the build, a scan of the built HTML and PDF, and layout measurement. Use when the user says "kontrol et" (check it), "derle" (build it) or "commit öncesi bak" (take a look before the commit), when verifying a bug fix, or as the last step of the write-chapters, make-figures and site-infra skills.
---

# Pre-delivery checks

The goal: every check reports 0 problems on new or changed content. Known blemishes in older books (listed below) are outside the scope of the job; do not bulk-fix them.

## 1. Structural check on changed files

The repo has no structural checker. Check the following in the changed `.qmd` files; write a small script in the scratchpad if needed:

- **Fence balance:** Opening and closing colon counts must match. The opening regex must be greedy: `^(:{3,})\s*\{(.*)\}\s*$`. The pattern `[^}]*` misses names like `name="$5^{2n}$"`. ``` blocks are skipped.
- **Labels:**
  - No label may be duplicated across the book.
  - No label may contain characters outside `[a-z0-9-]`.
  - No `@label` may be unresolved.
- **Proof and solution blocks:**
  - Every `.ispat`/`.cozum` block must be inside a box.
  - Every block must end with a `]{.qed}` mark. konveks-analiz solutions are exempt.
- **Frontmatter:** `pagetitle:` must not be missing.
- **Figures:**
  - No `FIGURE:` placeholder may be left over.
  - A `<!--FIG:name-->` comment is a persistent anchor. It is an error only if no ```` ```{=html} ```` `<figure>` block follows it.
  - No `<figure` may sit inside a definition box.
  - No figure may sit right below a `##` heading.
- **File:** No CRLF, no BOM and no unbalanced `$`.

Known old label violations; they are not renamed without also updating their `@` references:

- `sec-nEx`, `def-nEx` (finans-matematigi)
- `thm-koprü`, `thm-uA`, `thm-P-us-n` (raslanti-surecleri)
- `cor-a-uzeri-N` (soyut-cebir-1)

## 2. One question per box

`python scripts/check_box_questions.py <files.qmd>` must exit with code 0.

The script has real blind spots, so also read suspicious boxes by hand:

- It does not count numbered `1.` items.
- It does not split `.cozum baslik=…` and `.ispat baslik=…` blocks.
- It does not split old `callout collapse="true"` solutions.
- It skips a box whose name contains `}`.
- It counts `**a)** … **b)**` parts written on a single line as one piece.

## 3. Formula width

`python scripts/check_math_width.py <course> [--limit N]`

- New or changed formulas must stay within budget: inline 16.5em, inside a box 14.5em, display formula 34em.
- The script always returns 0, so read its output.
- Split overflowing formulas with `$$…$$` and `aligned`.

## 4. Quick greps

Run all of them with `--include=*.qmd`, on the changed files only:

- `grep -nE 'name="[0-9]+\.'` must return nothing.
- `grep -niE 'sınav|vize|final|hoca|ödev|kaynakta|cevap anahtar'` must return nothing. Weed out innocent uses by hand.
- Spelling: `\emptyset`, `rasgele`, `keyfî` must not appear in new text.

## 5. Build

Run `python scripts/build.py <course>`. If it takes long, start it in the background and wait for the notification. Add `--no-export` if only HTML is needed.

- Exit 1 means a render error; 2 means an export error or a file over 25 MiB.
- If the PDF is needed too and the book was previously built with `--no-export`, or if `scripts/export.py` or `export-assets` changed, add `--force`. Otherwise the unchanged book is skipped and no PDF is produced at all.
- If you see `WinError 32`, close the `http.server` that holds `_site` and run again.
- The occasional "failed to render" error in the portal step usually goes away on a rerun.

## 6. Scan the built HTML

Scan under `_site/dersler/<course>/`, not under `_book`. Expected counts:

| Check | Expected |
|---|---|
| Unresolved `?@` or `?sec-` reference | 0 |
| `<ol start=` and `<ol>` with a single `<li>` (accidental list) | 0 |
| Raw `:::` leftover | 0 |
| Broken relative link | 0 |

Tab titles must be unnumbered.

## 7. PDF and EPUB

- `_export/<course>/*.pdf` must exist and stay under 25 MiB.
- In multi-unit courses every unit must be listed in `dersler/<course>/_downloads.json`.
- Render the relevant pages to PNG with `pymupdf` and look at them.
- Two search traps:
  - In the PDF the figure label uses a no-break space (`Şekil\xa0N.M`).
  - Typst's "fi" ligature can mislead a text search.

## 8. Layout (if CSS, figures or placement changed)

Run `python scripts/check_layout.py dersler/<course>/<page>.html --widths 390,768,1280,1920,2560` and read the `RESULT` line. The script returns 0 even on overflow.

For your own measurements:

- Write the probe or copied HTML into the page's own folder; otherwise the relative CSS does not load and overflow falsely comes out as 0. Delete the file in a `finally`.
- Use `<details open` in the copy to see inside `<details>`.
- Headless Chrome does not shrink the window below ~485 px; measure narrow widths inside an iframe.

## 9. Report

- Give the count for every check: files, boxes, labels, references, problems, overflows, PDF page count.
- Do not call anything "clean" without measuring it. A probe written to the wrong place and a silently failing sed/regex have produced fake 0 results before.
