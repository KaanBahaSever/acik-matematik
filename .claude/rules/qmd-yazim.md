---
paths:
  - "dersler/**/*.qmd"
  - "dersler/**/_quarto.yml"
---

# .qmd authoring rules

## Files and frontmatter

- A file name is a lowercase, hyphenated slug without Turkish characters (`cekirdek-ve-goruntu.qmd`). Use `git mv` when moving a file.
- The frontmatter order is `title` → `pagetitle` → `description`.
  - `pagetitle` has no number and does not contain the book name; it shows as the tab title.
  - `description` is a single original, SEO-friendly sentence that summarizes the content.
- Add a new chapter both to the `chapters`/`part:` list in `_quarto.yml` and to the curriculum list in `index.qmd`; an unlinked chapter does not get into the PDF and EPUB. No chapter is titled "Giriş" (Introduction).

## Boxes

- Prefixes: `def`, `thm`, `lem`, `cor`, `prp`, `exm`, `exr`. Axioms are given in a `def-` box. `rem`, `cnj` and `alg` are not used.
- Labels:
  - Contain only `[a-z0-9-]`, never start with a digit and are unique across the book. Sayılar Teorisi 1 and 2 share one namespace.
  - In new books the form is `<prefix>-<chapter-key>-<name>`. Search the book before assigning a new label.
  - `{#sec-…}` identifiers are entirely lowercase.
- A box name (`name="…"`) never starts with a digit and a period; a "24. …" prefix is silently swallowed.
- Never write numbers into headings or box names by hand; Quarto numbers them. Exception: the `## 1. Bölüm — …` sub-course headings on the curriculum page, because the export unit names are generated from them.
- A proof or a solution sits INSIDE the box it belongs to, as `::: {.ispat}` or `::: {.cozum}`.
  - These blocks are collapsed by default. `baslik="…"` gives a custom title, `acik="true"` starts the block expanded.
  - Do not use the old `callout collapse="true"` pattern in new writing.
- The colon depth varies by book. Never re-indent an existing book:

  | Depth (outer / inner) | Books |
  |---|---|
  | 4 / 3 | analiz-1, analiz-2, diferansiyel-geometri, olasilik-teorisi, sayilar-teorisi, topoloji, diferansiyel-denklemler, finans-matematigi |
  | 3 / 3 | kompleks-analiz, lineer-cebir, soyut-cebir-1, matematigin-temelleri, kismi-diferansiyel-denklemler |
  | definition 4; box with a proof 5 / 4 | konveks-analiz |
  | box with no proof or solution inside 3; box with one 4 / 3 | new books |

- Every proof and solution ends with a `{.qed}` mark. In new writing use `[$\blacksquare$]{.qed}`. Do not touch the existing `\boxtimes` marks or the unmarked solutions of konveks-analiz.
- **Every `exm-` or `exr-` box contains a single question.**
  - Parts (a)(b)(c) are split into separate boxes. The labels take suffixes such as `-a`, `-b`, the `name` values are distinct and descriptive, and the shared setup is briefly repeated in each box.
  - Every exercise has a step-by-step `.cozum` block; never write a one-line "Yanıt:" (Answer:).
  - Check: `python scripts/check_box_questions.py <files>`.
- A definition box holds a single concept; complementary pairs are the exception.
  - A concept that is cited or used in exercises does not stay in plain text; it goes into a `def-` box.
  - In a classification, each type gets its own box.
  - A definition is followed by a plain explanation that starts with "Yani …".
- Use callouts sparingly (note, tip, warning, important).
  - Never put a callout inside `.cozum`/`.ispat` blocks or example boxes.
  - When a method is taught, a short `callout-tip` recipe titled "X adımda …" (in X steps) comes first, immediately followed by a worked example that applies it.

## Text and notation

- In new writing, a `##` heading is immediately followed by a connecting sentence. In no book is a figure placed right below a heading. Do not rewrite existing chapters for this rule.
- A chapter ends with a short closing that links to the next chapter with `[Name](file.qmd)`.
- Sequences such as `19.`, `II.`, `(f)` at the start of a line accidentally open a list. Escape the closing delimiter: `19\.`, `II\.`, `(f\)`. Never escape the opening parenthesis, because `\(` is LaTeX.
- Cross-references:
  - Within a book, use `@label`.
  - lineer-cebir and soyut-cebir-1 do not use `@`, only file links. Topoloji uses `@` within a chapter and file links between chapters.
  - `@` does not work across books; the form is `bkz. [Analiz 1](../analiz-1/<chapter>.html#label)`.
  - In new writing, never attach a suffix to a reference, as in `@sec-…'ndeki`. Do not bulk-fix existing ones.
- Notation:
  - The decimal separator is a comma: `$0{,}6$`.
  - The empty set is `\varnothing`.
  - In a piecewise function: `\text{diğer durumlarda}`.
  - The spellings are "rastgele" and "keyfi".
  - `\tag{n}` numbers increase sequentially from 1 within a chapter.
- Technical pitfalls:
  - Not available in MathJax: `\centernot`, `psmallmatrix`.
  - Lower and upper integrals are written `\underline{I}(f)`, `\overline{I}(f)`; `\underline{\int}` breaks Typst.
  - A new macro that Pandoc does not recognize halts the PDF. Add its equivalent to the `MACROS` table in `scripts/export_math.lua`.
- In books based on English sources, the English term is given in parentheses at its first occurrence. In books based on Turkish sources, follow the book's existing habit.
- Mobile width budget:
  - An inline formula is at most 16.5em, 14.5em inside a box.
  - A display formula is at most 34em.
  - Split a long calculation with `$$ … $$` and `aligned`: line end `\\[1mm]`, continuation line `&\quad`. Do not delete steps when splitting.
  - Check: `python scripts/check_math_width.py <course>`.
- Solutions use the method the course teaches at that point; a more advanced method may be given only as an additional route. Complicated expressions containing Σ are expanded term by term. Before a hard problem, solve 2–3 warm-up questions from easy to hard if needed.

## Figures

- A figure sits INSIDE the theorem, proof, example, solution or callout box it explains: right below the relevant paragraph, centered. It is never placed inside a definition box, but right below it. Different steps of a solution get separate figures.
  - In lineer-programlama, the figure of a single-figure solution sits at the very start of the solution (the reader sees the picture first). Figures that follow subproblems or iterations step by step stay next to the relevant step.
- There are no code cells executed at build time (python, r, Jupyter). Figures are produced by `scripts/*_figures.py` and embedded in the `.qmd`; the details are in the `make-figures` skill. The only exception is the browser-run OJS scenes in diferansiyel-geometri and integral-calculus.
- An embedded SVG is never fixed by hand: fix the generator script and regenerate the figure.

## Curriculum page (`index.qmd`)

- YAML:
  - `title: "# Müfredat ve Giriş {.unnumbered}"`
  - `pagetitle: "Müfredat ve Giriş"`
  - `description`
  - `number-sections: false`
- The page holds a short introduction and a list made only of links.
- `scripts/export.py` treats every `##` heading as a sub-course (a separate PDF/EPUB).
  - "Ders İçeriği", "İçindekiler", "Müfredat" and "Konular" are generic headings and mean a single unit.
  - Do not open a `##` for content that is not a sub-course; use a callout.
- The one-line `callout-note appearance="simple"` status note at the top of the page is a tradition, not a requirement.
- Never added: a "Notların kullanımı" (how to use the notes) section, exam or grading information, a "yazım aşamasındaki başlıklar" (topics being written) group.
- Curriculum topics not covered by the source were left unlinked in some courses and deleted in others. Do not touch the existing ones; in a new course, ask the user.
- `downloads.lua` appends the download panel to the end of the page by itself. Do not add an explanatory sentence to the panel.
