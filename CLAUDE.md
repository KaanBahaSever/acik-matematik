# Açık Matematik: working rules

An open-source, ad-free archive of Turkish notes for undergraduate mathematics courses. It is built with Quarto and published at https://acik-matematik.com. The repository is public: never write personal paths, source file names or secrets into this file or anywhere under `.claude/`.

## Where things are

- `dersler/<course>/`: each course is a standalone Quarto book. It consists of a `_quarto.yml`, an `index.qmd` that serves as the curriculum page, and the chapter `.qmd` files. Shared settings come from `_kitap-ortak.yml`. A book must sit exactly two levels below the root; otherwise the Lua filters and the Turkish labels are silently lost.
- Analiz and Soyut Cebir are four separate books each (`dersler/analiz-1` … `analiz-4`, `dersler/soyut-cebir-1` … `soyut-cebir-4`); `dersler/analiz/` and `dersler/soyut-cebir/` are only hub pages. The book title of such a split course is the number, a colon and a short name: `Analiz 1: Temeller`, `Soyut Cebir 1: Gruplar`. Other multi-semester courses (Lineer Cebir 1–2, Sayılar Teorisi 1–2, …) are split with `part:` inside a single book, and chapter numbers run continuously through the book.
- The root `_quarto.yml` renders only the portal (home page, catalog). All styling lives in `styles/global.css`.
- `scripts/`: build, export, check and figure scripts.

## Detailed rules and procedures

- The `.qmd` authoring rules are in `.claude/rules/qmd-yazim.md`. Read that file when working on course files.
- The CSS, script and CI rules are in `.claude/rules/altyapi.md`.
- Skills:
  - `write-chapters`: writing chapters from a source
  - `run-checks`: pre-delivery checks
  - `make-figures`: figures
  - `site-infra`: design and build infrastructure
- The `proof-checker` subagent checks proofs and calculations. It is called once when each chapter is finished; there is no second round.

## Language

- Turkish is used only for:
  - the course content: lecture text, headings, figure labels and everything else in the `.qmd` notes;
  - text visible on the site, including interface text;
  - messages and reports written to the user.
- Everything else is English: this file, the rules, skills and agent definitions under `.claude/`, internal notes, code (Python, Lua, Typst, CSS class and variable names, embedded JS, CI steps), comments, console output and commit messages.
- Exceptions: README.md, and the Turkish file and directory names kept for SEO (`dersler/`, chapter slugs).
- The `.qmd` authoring vocabulary stays Turkish and is never renamed (`.ispat`, `.cozum`, `baslik=`, `acik=`, `ders-grafik*`), because `scripts/collapsible.lua` reads these names.
- New text uses no emoji. The site brand is the logo image `assets/logo.svg`, not an emoji. The only exceptions are the catalog group headings and README.md.

## Content principles

1. **Re-explanation, not translation.** The source is read in person and the text is written by hand; source content is never translated or converted by a script. Bulk term changes or cross-reference conversions in existing text may be done by a script, but every generated form is reviewed one by one (vowel harmony, substring matches).
2. **Plain, clear, friendly Turkish.** The flow is: motivation, definition, a "Yani …" explanation, plenty of examples. If the source has few examples, add more. Every proof step is justified, and only the clean final version is written.
3. **Completeness.** Definitions, theorems, proofs and examples in the source are never skipped or summarized. Proofs and solutions the source left blank are written too; the text does not say they were added.
4. **Standalone course text.** The notes never refer to the instructor, the source file, an exam or homework. Errors in the source are silently corrected.
5. **Match the book's voice.** Before writing, scan the book's existing `.qmd` files. Notation, terminology, label scheme, box depth and difficulty level are taken from the book. The course never uses a tool it has not defined up to that point.
6. **No repetition.** A concept is never defined a second time in the same book or in a sibling book; link to the existing definition instead. Advanced courses do not re-explain basic prerequisites.
7. **Verify every number.** Every numerical result and intermediate step shown is recomputed independently in Python in the scratchpad (`fractions.Fraction`, sympy). Verification scripts never enter the repository.
8. **Chapter division.**
   - If the source has an explicit weekly schedule or exercise blocks, the chapters follow it; do not split into extra files.
   - If the source is scattered, order the topics by academic flow.
   - If you are unsure, show the plan first.

## Build and checks

- Always build with `python scripts/build.py <course>`, and build only the course you are working on (`--no-export` produces HTML only). Never run a bare `quarto render` at the root: it deletes `_site` and every book in it.
- Options: `python scripts/build.py [course...] [--no-export] [--force] [--jobs N] [--serial]`. There is no `--help`; an unknown flag is an error.
- Exit codes:
  - 1: render error
  - 2: export error, or a file larger than 25 MiB
- The cache is in `.build-cache.json`.
  - `styles/`, `assets/` and the figure scripts are not part of the fingerprint; when they change, the build only copies the files.
  - If `scripts/export.py` or `scripts/export-assets/` changed, or the book was previously built with `--no-export`, add `--force` to get the PDF.
- Visual checks are done in `_site/`, not in `_book/`.
- Apply the `run-checks` skill before delivery. CI runs no checks. `check_math_width.py` and `check_layout.py` return 0 even when they find problems, so read their output.
- `scripts/stats.py` rewrites the `BOOKS` and `METRICS` regions of the README on every build; do not edit them by hand. If the book count in the diff differs from what you expect, do not commit.

## Git

- Never run `git push`; the user publishes. Commit only when the user asks. When the work is done, report the uncommitted files.
- A commit message is a single plain line in English, in the imperative mood. Course work takes the Turkish course name as a prefix, e.g. `Diferansiyel Geometri: add the Frame Fields part (6 chapters)`. No body.
- Commit messages, code comments and notes never mention where the content was compiled from: no PDF, page, handwritten note, instructor, exam, reading or transcription process.
- If the URL of a published page is going to change, use `git mv` and add `aliases:` to the chapter or a book-level `_redirects`. Never delete existing redirects.
- A new worktree starts empty (no `_site`, `.build-cache.json` or `scripts/_figures`). Build only the relevant course; run the relevant `*_figures.py` script before editing figures.

## Windows environment

- Never write content containing backslashes (LaTeX, `.qmd`, CSS) with a Bash heredoc, because sequences such as `\b`, `\v`, `\r` get corrupted. Use the Write/Edit tools, and raw strings (`r"…"`) in Python.
- In Python scripts that print Turkish, call `sys.stdout.reconfigure(encoding="utf-8")`. Write files as UTF-8 (no BOM) with LF line endings (`newline="\n"`).
- Limit grep over `dersler/` with `--include=*.qmd`. When working from the main folder, exclude the `.claude/` folder, because it contains worktree copies.
