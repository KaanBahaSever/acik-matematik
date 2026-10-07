---
name: write-chapters
description: Writes course chapters from a source PDF or a curriculum heading, and adds chapters, exercises or questions to an existing book. Covers reading the source, planning, writing, numerical verification, figures, wiring into the book, proof checking, the build and the report. Use when the user says "şu dersi/bölümü yaz" (write this course/chapter), "masaüstündeki PDF'ten notları çıkar" (extract the notes from the PDF on the desktop), "müfredattaki eksik başlıkları tamamla" (fill in the missing curriculum topics) or "bu soruları kitaba ekle" (add these questions to the book). Do not use it for a one-sentence fix or for a figure-only or CSS-only job.
---

# Chapter writing procedure

The binding rules are in `CLAUDE.md` and `.claude/rules/qmd-yazim.md`. Read both before starting.

## 1. Fix the scope

- Pin down exactly which parts of which course are to be written. If the user said "sadece 3 kısım" (only 3 parts), only those parts are written.
- Check whether `dersler/<course>/` already exists. There are 30 books and 14 of them are only skeletons; fill the existing book instead of opening a new course.
- If Claude's memory has a `<course>-kaynak-ve-uretim` note, read it first. The note holds the source path, the label keys, silently fixed errors and the user's decisions.
- Follow the user's session budget rule (in memory). Split a big job into chapters; finish and deliver each chapter.

## 2. Read the source

- First try `page.get_text()` with `import pymupdf`.
- If the text is empty or the formulas are garbled:
  - Render the pages to the scratchpad as 110–125 DPI PNGs.
  - Read at most 4 images per message with Read.
  - Right after each batch, write a summary into the notes file in the scratchpad.
  - Do not count an image that came back empty as read; read it again.
- Read files with equal md5 in the same folder only once.
- If there are several candidate files, read their first pages and ask which one to use.

## 3. Plan

Prepare `scratchpad/PLAN.md`:

- Write down which source pages each chapter corresponds to.
- Split into chapters following the principle in `CLAUDE.md`. Mark proofs and solutions left blank in the source as "ADD".
- Search whether the same topic already exists in this book or in a sibling book (ST1/ST2, Analiz 1/2, LC1/LC2). Look at the labels first (`grep -rn '{#def-' dersler/<course> --include=*.qmd`), then search by topic names. If the topic exists, do not redefine it; link to it.
- If the structure is unclear, show the plan to the user.

## 4. Style contract (for large jobs)

Prepare `scratchpad/STYLE.md`:

- For an English source, a Turkish terminology table.
- The existing notation, scanned from the book's `.qmd` files.
- The book's box depth (see the table in qmd-yazim).
- A short, unique label key for each chapter (`<prefix>-<key>-<name>`).
- Figure placeholder: `<!-- FIGURE: name | description -->` (name matches `[a-z0-9-]+`).

If the job spans several sessions, put a copy of the contract in a persistent folder outside the scratchpad, because the scratchpad is lost with the session.

## 5. Write

- Write with the Write tool (UTF-8, LF, no heredoc).
- Chapter order:
  1. Frontmatter
  2. 1–3 motivation paragraphs
  3. `##` headings
  4. Definition box, followed by "Yani …"
  5. Theorem box with `.ispat` inside
  6. Exactly one question and a `.cozum` in each example or exercise box
  7. `## Alıştırmalar`: all with solutions
  8. A closing that links to the next chapter
- Do not rewrite the parts the user wrote; only verify their math.
- Re-read a file before editing it, because the user makes changes between turns.

## 6. Verify the numbers

- Recompute every number in the source and in your text, and every intermediate step shown, with independent Python in the scratchpad. This includes Gauss-Jordan steps, inverses, intermediate factors and probabilities.
- Tools: `fractions.Fraction`, sympy, numpy (`np.trapezoid`).
- Fix whatever does not match. Record source errors in the course memory note, not in the text.

## 7. Figures

Turn the placeholders into figures and place them with the `make-figures` skill. No placeholder may remain when the job is done.

## 8. Wire into the book

- Add the chapter to the `chapters`/`part:` list in `dersler/<course>/_quarto.yml`.
- Put its link under the correct `##` heading in `index.qmd`.
- Update the curriculum page's `description` if needed.

## 9. Consistency scan (new or changed text only)

- `\emptyset` → `\varnothing`, "rasgele" → "rastgele", "keyfî" → "keyfi".
- `grep -rniE 'sınav|vize|final|hoca|ödev|kaynakta|cevap anahtar' <files>` must return nothing. Weed out innocent, topic-related uses by hand.
- After moving or splitting, fix relative transitions such as "bir sonraki bölümde" (in the next chapter) and references to deleted boxes.

## 10. Proof check (once per chapter)

- Hand the finished chapter to the `proof-checker` subagent. Include the file paths and a short note on the book's notation.
- Evaluate the returned findings yourself: fix the correct ones and skip false alarms with a stated reason.
- Do not run a second review round.

## 11. Check and build

Apply the `run-checks` skill.

## 12. Update memory

Write the following into the `<course>-kaynak-ve-uretim` memory note:

- source path and type (whether it has a text layer)
- chapter structure and label keys
- figure script and prefix
- silently fixed source errors
- topics deliberately left out
- the user's course-specific decisions

Add a one-line pointer to MEMORY.md.

## 13. Report (in Turkish)

- Answer the user's points one by one.
- State clearly any decisions you made beyond the request, so the user can veto them.
- List the silent fixes; the chapter, box and figure counts; the check and build results.
- List the uncommitted files. Suggest a commit message if asked. No push.

## Multi-agent work

Used only in a session mode (e.g. ultracode) or at the user's explicit request:

- One writer per chapter; writers work in disjoint files.
- Only the merger touches `_quarto.yml` and the build.
- One review round.
- When agents drop, restart only the ones that failed.
- Agents cannot find figure errors; check the figures yourself by looking at the PNGs.
