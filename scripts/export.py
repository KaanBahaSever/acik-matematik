#!/usr/bin/env python3
"""
Açık Matematik — exports every course (or the sub-courses it is split into)
as downloadable PDF / EPUB files.

Why a separate script instead of `quarto render --to pdf` on the book?

  * A book may be split into sub-courses (Cebir 1, Cebir 2, …). That split
    lives only on the curriculum page (index.qmd, "##" headings); _quarto.yml
    knows nothing about it. Every sub-course needs its own file, i.e. its
    own chapter list.
  * Quarto profiles APPEND to `book.chapters` instead of replacing it, so a
    profile cannot narrow a book down to one sub-course.

So every unit is rendered from a throw-away copy of the course placed under
<repo>/_export-src/<course>/ with a generated _quarto.yml. The copy sits at
the same depth as the original (two levels below the repo root), so the
shared ../../_kitap-ortak.yml, the Lua filters and the Typst includes
resolve unchanged. Quarto silently ignores a missing metadata file, so a
copy at the wrong depth would render without any of the shared setup.

PDFs are produced with Typst (bundled with Quarto — no TeX installation
needed, and it renders the inline SVG figures natively). EPUB comes straight
from Pandoc.

Outputs
    <repo>/_export/<course>/<unit>.{pdf,epub}
    dersler/<course>/_downloads.json   manifest read by scripts/downloads.lua,
                                        which draws the download panel on the
                                        course's curriculum page

Usage
    python scripts/export.py                       # every course
    python scripts/export.py kriptografi           # one course
    python scripts/export.py kriptografi --formats pdf
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COURSES = ROOT / "dersler"
# Disposable book copies (must stay exactly two levels below the repo root)
EXPORT_SRC = ROOT / "_export-src"
# Finished files, one directory per course
EXPORT_OUT = ROOT / "_export"
MANIFEST_NAME = "_downloads.json"
# Units whose chapters hold less text than this are skeletons (placeholder
# pages only) and get no download files; real chapters run to 100+ KB.
MIN_UNIT_BYTES = 8 * 1024
# Cloudflare Pages refuses single files above 25 MiB — catch it at build time
MAX_FILE_BYTES = 25 * 1024 * 1024

AUTHOR = "Açık Matematik"
# Colours, licence text and the site address of the PDF live in
# scripts/export-assets/{typst-show,footer,body}.typ
ALL_FORMATS = ("pdf", "epub")
QUARTO_FORMAT = {"pdf": "typst", "epub": "epub"}

# Headings on the curriculum page that do NOT start a sub-course (compared
# as slugs so that "İ" and other Turkish letters need no special casing)
GENERIC_HEADINGS = {"ders-icerigi", "icindekiler", "mufredat", "konular"}
# "1. Bölüm — Temeller": a short name that is only a number gets the course
# name in front of it so the file says which course it belongs to
_NUMERIC_SHORT = re.compile(r"^(\d+)\.?\s*(bölüm|kısım|ünite|kisim|bolum)?$", re.I)

for stream in (sys.stdout, sys.stderr):
    try:
        stream.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass


# ----------------------------------------------------------------- helpers

def quarto() -> str:
    exe = shutil.which("quarto")
    if not exe:
        sys.exit("ERROR: 'quarto' not found on PATH. https://quarto.org/docs/get-started/")
    return exe


_TR = str.maketrans("çğıöşüâîûÇĞİÖŞÜÂÎÛI", "cgiosuaiucgiosuaiui")


def slugify(text: str) -> str:
    text = text.translate(_TR).lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def short_name(title: str) -> str:
    """'Cebir 1 — Grup Teorisi' -> 'Cebir 1'; 'Lineer Cebir 2: …' -> 'Lineer Cebir 2'."""
    return re.split(r"\s+[—–-]\s+|:", title, maxsplit=1)[0].strip()


def yaml_str(text: str) -> str:
    """A YAML double-quoted scalar (JSON escaping is valid YAML)."""
    return json.dumps(text, ensure_ascii=False)


# ------------------------------------------------------------ book structure

def inspect_book(course: Path) -> dict:
    """Project configuration as Quarto itself resolves it (no YAML parser needed)."""
    result = subprocess.run(
        [quarto(), "inspect", str(course)],
        cwd=ROOT, text=True, capture_output=True, encoding="utf-8", errors="replace",
    )
    if result.returncode != 0:
        raise RuntimeError(f"quarto inspect failed for {course.name}:\n{result.stderr}")
    return json.loads(result.stdout)["config"]


def flatten_chapters(entries) -> list[str]:
    files: list[str] = []
    for entry in entries or []:
        if isinstance(entry, str):
            files.append(entry)
        elif "part" in entry:
            files.extend(flatten_chapters(entry.get("chapters")))
        elif "file" in entry:
            files.append(entry["file"])
    return [f.replace("\\", "/") for f in files]


_H2 = re.compile(r"^##\s+(.*?)\s*(\{[^}]*\})?\s*$")
_LINK = re.compile(r"\]\(([^)\s#]+\.qmd)(?:#[^)]*)?\)")


def parse_sub_courses(index_qmd: Path) -> list[tuple[str, list[str]]]:
    """(heading, [linked chapter files]) for every '##' heading of the
    curriculum page that names a sub-course."""
    units: list[tuple[str, list[str]]] = []
    current: list[str] | None = None
    in_code = False
    in_front_matter = False
    for i, line in enumerate(index_qmd.read_text(encoding="utf-8").splitlines()):
        if line.strip() == "---" and (i == 0 or in_front_matter):
            in_front_matter = not in_front_matter     # YAML header may hold "#" comments
            continue
        if in_front_matter:
            continue
        if line.startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        heading = _H2.match(line)
        if heading:
            title = heading.group(1).strip()
            if slugify(title) in GENERIC_HEADINGS:
                current = None
            else:
                current = []
                units.append((title, current))
            continue
        if current is not None:
            for target in _LINK.findall(line):
                current.append(target.replace("\\", "/"))
    return units


@dataclass
class Unit:
    stem: str                     # output file name without extension
    title: str                    # book title
    subtitle: str | None          # sub-course name (None for a whole book)
    chapters: list[str]
    kind: str                     # "sub" or "book"

    @property
    def label(self) -> str:
        return self.subtitle or self.title


def plan_units(course: Path, config: dict) -> list[Unit]:
    book = config.get("book", {})
    title = book.get("title") or course.name
    chapters = [c for c in flatten_chapters(book.get("chapters")) if c != "index.qmd"]

    sub_courses = parse_sub_courses(course / "index.qmd") if (course / "index.qmd").exists() else []
    units: list[Unit] = []
    covered: set[str] = set()
    used_stems: set[str] = set()
    for heading, links in sub_courses:
        members = [c for c in chapters if c in set(links)]
        if not members:
            continue                       # sub-course announced but not written yet
        short = short_name(heading)
        numeric = _NUMERIC_SHORT.match(short)
        stem = f"{course.name}-{numeric.group(1)}" if numeric else (slugify(short) or slugify(heading))
        base, n = stem, 2
        while not stem or stem in used_stems or stem == course.name:
            stem, n = f"{base}-{n}", n + 1
        used_stems.add(stem)
        units.append(Unit(stem, title, heading, members, "sub"))
        covered.update(members)

    if units:
        stray = [c for c in chapters if c not in covered]
        if stray:
            print(f"   ! {course.name}: {len(stray)} chapter(s) are not linked under any "
                  f"sub-course heading of index.qmd and only appear in the whole-book file: "
                  + ", ".join(stray))
        if len(units) >= 2 or stray:
            units.append(Unit(course.name, title, None, chapters, "book"))
    else:
        units.append(Unit(course.name, title, None, chapters, "book"))

    def content_bytes(unit: Unit) -> int:
        return sum((course / c).stat().st_size for c in unit.chapters if (course / c).exists())

    real = [u for u in units if content_bytes(u) >= MIN_UNIT_BYTES]
    for u in units:
        if u not in real:
            print(f"   - skipped {u.stem}: no written chapters yet")
    return real


# --------------------------------------------------------------- rendering

def export_config(unit: Unit, today: dt.date) -> str:
    lines = [
        "# Generated by scripts/export.py — do not edit, the copy is disposable.",
        "project:",
        "  type: book",
        "  output-dir: _out",
        "",
        "metadata-files:",
        "  - ../../_kitap-ortak.yml",
        "",
        "book:",
        f"  title: {yaml_str(unit.title)}",
    ]
    if unit.subtitle:
        lines.append(f"  subtitle: {yaml_str(unit.subtitle)}")
    lines += [
        f"  author: {yaml_str(AUTHOR)}",
        # ISO date + a format; Quarto localises the month name via `lang: tr`
        f"  date: {yaml_str(today.isoformat())}",
        '  date-format: "D MMMM YYYY"',
        f"  output-file: {yaml_str(unit.stem)}",
        "  chapters:",
        "    - index.qmd",
    ]
    lines += [f"    - {yaml_str(ch)}" for ch in unit.chapters]
    lines += [
        "",
        "format:",
        "  typst:",
        "    papersize: a4",
        "    toc-depth: 2",
        "    template-partials:",
        "      - ../../scripts/export-assets/typst-show.typ",
        "    include-in-header: ../../scripts/export-assets/footer.typ",
        "    include-before-body: ../../scripts/export-assets/body.typ",
        "  epub:",
        "    toc-depth: 2",
        # Pandoc resolves this one itself (not Quarto), so it must be absolute
        f"    epub-metadata: {yaml_str((ROOT / 'scripts' / 'export-assets' / 'epub-metadata.xml').as_posix())}",
        "",
    ]
    return "\n".join(lines)


def split_front_matter(text: str) -> tuple[str, str]:
    """(YAML header incl. its --- fences, body) — header may be empty."""
    if text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        if end != -1:
            return text[:end + 5], text[end + 5:]
    return "", text


def intro_only(text: str) -> str:
    """Turn a curriculum page into the intro chapter of an exported file.

    The page carries its title as '# Müfredat ve Giriş {.unnumbered}' — a
    trick that keeps the HTML chapter numbers starting at 1, but attributes
    on a YAML title are only honoured with that leading '#', which would
    then show up in print. The title is moved into the body as an
    unnumbered heading (so chapter numbers still match the website), and
    everything from the first '##' heading on — the link lists and the
    sub-course blurbs — is cut: the file has a real table of contents.
    """
    front, body = split_front_matter(text)
    front = re.sub(r"^title:.*\n", "", front, flags=re.M)
    body = body.split("\n## ", 1)[0].strip("\n")
    return front + "\n# Giriş {.unnumbered}\n\n" + body + "\n"


def version_date() -> dt.date:
    """Date shown as 'Bu sürüm' — the last commit's date, so that rebuilding
    the same commit yields identical files; today when git is unavailable."""
    try:
        result = subprocess.run(["git", "log", "-1", "--format=%cs"], cwd=ROOT,
                                capture_output=True, text=True, timeout=10)
        if result.returncode == 0 and result.stdout.strip():
            return dt.date.fromisoformat(result.stdout.strip())
    except (OSError, ValueError):
        pass
    return dt.date.today()


def remove_tree(path: Path) -> None:
    """rmtree that tolerates Windows file locks (Quarto's .quarto cache keeps
    a file open for a moment after a render); retries, then gives up quietly."""
    for attempt in range(5):
        try:
            shutil.rmtree(path)
        except OSError:
            if attempt == 4:
                shutil.rmtree(path, ignore_errors=True)
        if not path.exists():
            return
        time.sleep(0.5 * (attempt + 1))


def make_copy(course: Path) -> Path:
    copy = EXPORT_SRC / course.name
    if copy.exists():
        remove_tree(copy)
    shutil.copytree(
        course, copy, dirs_exist_ok=True,
        ignore=shutil.ignore_patterns("_book", ".quarto", "_export*", "_out", MANIFEST_NAME, "*.pdf", "*.epub", "*.docx"),
    )
    index = copy / "index.qmd"
    if index.exists():
        index.write_text(intro_only(index.read_text(encoding="utf-8")), encoding="utf-8")
    return copy


def render(copy: Path, fmt: str) -> tuple[bool, str]:
    result = subprocess.run(
        [quarto(), "render", "--to", QUARTO_FORMAT[fmt]],
        cwd=copy, text=True, capture_output=True, encoding="utf-8", errors="replace",
    )
    log = result.stdout + result.stderr
    return result.returncode == 0, log


def compact_pdf(path: Path) -> None:
    """Rewrite a Typst PDF with object streams (PDF 1.5).

    Typst emits a tagged PDF whose structure tree is tens of thousands of tiny
    objects (about 230 per page); stored one by one they dominate the file
    size — a 420-page book came out at 21 MB with only 4 MB of real content.
    Packing them into compressed object streams cuts the file to roughly a
    third without touching pages, fonts or the outline.

    Optional: needs PyMuPDF (`pip install pymupdf`). Without it the PDF is
    left as Typst wrote it.
    """
    try:
        import pymupdf
    except ImportError:
        return
    tmp = path.with_name(path.stem + ".compact.pdf")
    doc = pymupdf.open(path)
    doc.save(tmp, garbage=1, deflate=True, use_objstms=1)
    doc.close()
    tmp.replace(path)


def export_course(course: Path, formats: tuple[str, ...] = ALL_FORMATS, today: dt.date | None = None,
                  keep_copy: bool = False) -> dict:
    """Render every unit of `course` in every format; write and return the manifest.

    With keep_copy the disposable project under _export-src/<course>/ is left
    in place (configured for the last unit) so a failing render can be
    repeated by hand: `cd _export-src/<course> && quarto render --to typst`.
    """
    today = today or version_date()
    started = time.time()
    config = inspect_book(course)
    units = plan_units(course, config)
    out_dir = EXPORT_OUT / course.name
    if out_dir.exists():
        remove_tree(out_dir)          # no stale files from an earlier run
    if units:
        out_dir.mkdir(parents=True, exist_ok=True)

    manifest = {
        "course": course.name,
        "title": config.get("book", {}).get("title", course.name),
        "generated": today.isoformat(),
        "units": [],
    }
    failures: list[str] = []
    if not units:
        # Nothing to offer: make sure no stale manifest draws a panel
        (course / MANIFEST_NAME).unlink(missing_ok=True)
        manifest["failures"] = failures
        print(f"   nothing to export ({time.time() - started:.1f} s)")
        return manifest
    copy = make_copy(course)
    for unit in units:
        (copy / "_quarto.yml").write_text(export_config(unit, today), encoding="utf-8")
        entry = {"title": unit.label, "kind": unit.kind, "chapters": len(unit.chapters), "files": {}}
        for fmt in formats:
            ok, log = render(copy, fmt)
            produced = copy / "_out" / f"{unit.stem}.{fmt}"
            if ok and produced.exists():
                target = out_dir / produced.name
                shutil.move(str(produced), target)
                if fmt == "pdf":
                    compact_pdf(target)
                size = target.stat().st_size
                entry["files"][fmt] = {"name": target.name, "bytes": size}
                print(f"   {unit.stem}.{fmt}  ({size / 1048576:.1f} MB)")
                if size > MAX_FILE_BYTES:
                    failures.append(f"{course.name}/{target.name} (over the 25 MiB Cloudflare Pages limit)")
            else:
                failures.append(f"{course.name}/{unit.stem}.{fmt}")
                tail = "\n".join(log.strip().splitlines()[-12:])
                print(f"   ! FAILED {unit.stem}.{fmt}\n" + "\n".join("     " + l for l in tail.splitlines()))
        if entry["files"]:
            manifest["units"].append(entry)
    if not keep_copy:
        remove_tree(copy)

    (course / MANIFEST_NAME).write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
    manifest["failures"] = failures
    print(f"   exports done ({time.time() - started:.1f} s)")
    return manifest


def publish_exports(course: Path, site_dir: Path) -> int:
    """Copy the produced files next to the course's HTML under _site."""
    out_dir = EXPORT_OUT / course.name
    if not out_dir.is_dir():
        return 0
    site_dir.mkdir(parents=True, exist_ok=True)
    count = 0
    for file in out_dir.iterdir():
        if file.suffix.lstrip(".") in ALL_FORMATS:
            shutil.copy2(file, site_dir / file.name)
            count += 1
    return count


def books() -> list[Path]:
    return sorted(p.parent for p in COURSES.glob("*/_quarto.yml"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Export the courses as PDF/EPUB.")
    parser.add_argument("course", nargs="?", help="course directory name under dersler/ (default: all)")
    parser.add_argument("--formats", default=",".join(ALL_FORMATS), help="comma-separated subset of pdf,epub")
    parser.add_argument("--keep", action="store_true", help="keep the disposable copy under _export-src/ for debugging")
    args = parser.parse_args()

    formats = tuple(f.strip() for f in args.formats.split(",") if f.strip())
    unknown = [f for f in formats if f not in ALL_FORMATS]
    if unknown:
        sys.exit(f"ERROR: unknown format(s): {', '.join(unknown)}")

    targets = [COURSES / args.course] if args.course else books()
    if args.course and not (targets[0] / "_quarto.yml").exists():
        sys.exit(f"ERROR: there is no course project named '{args.course}'.")

    failures: list[str] = []
    for course in targets:
        print(f"\n\033[1m>> export: {course.name}\033[0m")
        failures += export_course(course, formats, keep_copy=args.keep)["failures"]

    if failures:
        print("\n\033[1mFailed exports:\033[0m " + ", ".join(failures))
        sys.exit(1)
    print("\n\033[1mAll exports done.\033[0m")


if __name__ == "__main__":
    main()
