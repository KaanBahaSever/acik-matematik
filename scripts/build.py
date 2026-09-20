#!/usr/bin/env python3
"""
Açık Matematik — builds the whole site.

Layout:
  * Root project (type: website)  -> home page + course catalog  ->  _site/
  * dersler/<course>/             -> each one an independent Quarto "book"
                                     -> dersler/<course>/_book/
                                     -> _site/dersler/<course>/

Every book is first rendered into its own _book/ directory and then copied
under _site. Rendering the books straight into _site made Quarto refuse to
clean directories outside the project and let stale files pile up.

Order matters: rendering the root project wipes _site, so the course books are
copied under _site AFTER the portal is rendered.

Before a course's HTML is rendered, scripts/export.py produces its downloadable
PDF / EPUB files (one per sub-course) and drops a manifest next to the course;
the download panel on the curriculum page is drawn from that manifest, and the
files are copied under _site with the HTML.

Two things keep the build short:

  * The books are independent projects, so they are rendered CONCURRENTLY.
    Quarto itself renders the documents of one project one after another and
    has no option to spread them over cores, so the parallelism has to happen
    here, one process per book.
  * A book is only rendered when something it is built from has changed. The
    fingerprint of every book (its .qmd files, its _quarto.yml, the shared
    _kitap-ortak.yml, the Lua filters and the Quarto version) is kept in
    .build-cache.json; an unchanged book is copied from its existing _book
    directory, or skipped entirely when the copy under _site is current.
    Editing README.md, a script or a style sheet therefore renders nothing.

Usage:
    python scripts/build.py                        # build what has changed
    python scripts/build.py kriptografi            # build a single course only
    python scripts/build.py --force                # ignore the cache, rebuild all
    python scripts/build.py --no-export            # HTML only, skip PDF/EPUB
    python scripts/build.py --jobs 6               # how many books at a time
    python scripts/build.py --serial               # one at a time (debugging)
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from export import export_course, publish_exports  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
COURSES = ROOT / "dersler"
SITE = ROOT / "_site"
CACHE_FILE = ROOT / ".build-cache.json"

# Files every book is built from. A change to one of them invalidates all of
# them. Style sheets and assets are deliberately NOT in this list: the books
# link to /styles/global.css instead of embedding it, so changing the design
# only means copying the file again (sync_shared_assets), never re-rendering.
SHARED_INPUTS = (
    ROOT / "_kitap-ortak.yml",
    ROOT / "scripts" / "collapsible.lua",
    ROOT / "scripts" / "export_figures.lua",
    ROOT / "scripts" / "export_math.lua",
    ROOT / "scripts" / "export_links.lua",
    ROOT / "scripts" / "downloads.lua",
    ROOT / "scripts" / "mobile-toc.html",
)

# The Windows console defaults to cp1252, which cannot print the Turkish
# characters that appear in course names.
for stream in (sys.stdout, sys.stderr):
    try:
        stream.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass


def quarto() -> str:
    exe = shutil.which("quarto")
    if not exe:
        sys.exit("ERROR: 'quarto' not found on PATH. https://quarto.org/docs/get-started/")
    return exe


def quarto_version() -> str:
    try:
        out = subprocess.run([quarto(), "--version"], text=True, capture_output=True,
                             encoding="utf-8", errors="replace", timeout=60)
        return out.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return "unknown"


def default_jobs() -> int:
    """How many books to render at once.

    Each worker is a quarto process (Deno + pandoc) that needs roughly half a
    gigabyte, so the count is bounded by cores and by memory, and capped at 8:
    beyond that the machine spends its time swapping between renders rather
    than finishing them.
    """
    env = os.environ.get("QUARTO_BUILD_JOBS")
    if env and env.isdigit() and int(env) > 0:
        return int(env)
    cores = os.cpu_count() or 4
    return max(2, min(8, cores - 4))


# --------------------------------------------------------------- fingerprints

def file_digest(path: Path, chunk: int = 1 << 20) -> str:
    h = hashlib.sha1()
    try:
        with open(path, "rb") as fh:
            while True:
                block = fh.read(chunk)
                if not block:
                    break
                h.update(block)
    except OSError:
        return "missing"
    return h.hexdigest()


def fingerprint(paths) -> str:
    """One hash over a set of files: their relative names and their contents."""
    h = hashlib.sha1()
    for path in sorted(paths, key=lambda p: str(p).lower()):
        try:
            rel = path.relative_to(ROOT).as_posix()
        except ValueError:
            rel = path.name
        h.update(rel.encode("utf-8"))
        h.update(file_digest(path).encode("ascii"))
    return h.hexdigest()


def book_inputs(book: Path) -> list[Path]:
    """Everything that decides what a book's HTML looks like."""
    own = [p for p in book.rglob("*")
           if p.is_file()
           and p.suffix.lower() in (".qmd", ".yml", ".yaml", ".js", ".css", ".bib", ".json")
           and not any(part.startswith(("_book", ".quarto", "_export")) for part in p.relative_to(book).parts)
           and p.name != "_downloads.json"]          # written by the export step itself
    return own + [p for p in SHARED_INPUTS if p.exists()]


def portal_inputs() -> list[Path]:
    """The files the root website project renders (see its `project: render:`)."""
    files = [ROOT / "_quarto.yml", ROOT / "index.qmd",
             COURSES / "index.qmd", COURSES / "analiz" / "index.qmd"]
    return [p for p in files if p.exists()]


def load_cache() -> dict:
    try:
        data = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def save_cache(cache: dict) -> None:
    try:
        CACHE_FILE.write_text(json.dumps(cache, indent=1, sort_keys=True), encoding="utf-8")
    except OSError as exc:
        print(f"   ! could not write {CACHE_FILE.name}: {exc}")


# ------------------------------------------------------------------ rendering

def render(target: Path, label: str, quiet: bool = False) -> tuple[float, str]:
    """Render the Quarto project in `target`; return (seconds, warnings)."""
    started = time.time()
    result = subprocess.run(
        [quarto(), "render"],
        cwd=target,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
    )
    elapsed = time.time() - started

    if result.returncode != 0:
        print(f"\n\033[1m>> {label}\033[0m")
        print(result.stdout)
        print(result.stderr, file=sys.stderr)
        raise RuntimeError(f"'{label}' failed to render (exit code {result.returncode}).")

    warnings = "\n".join(f"   ! {line.strip()}"
                         for line in (result.stdout + result.stderr).splitlines()
                         if "WARN" in line or "ERROR" in line)
    if not quiet:
        print(f"\n\033[1m>> {label}\033[0m")
        if warnings:
            print(warnings)
        print(f"   done ({elapsed:.1f} s)")
    return elapsed, warnings


def books() -> list[Path]:
    """All book projects under dersler/, in alphabetical order."""
    return sorted(p.parent for p in COURSES.glob("*/_quarto.yml"))


def sync_shared_assets() -> None:
    """Refresh the styles/ and assets/ directories under _site.

    The course books link to these files from the _site root
    (../../../styles/global.css and so on). Because the files live outside
    the book project directories, Quarto does not copy them into the book
    output. Normally the portal build takes care of it, but when a single
    course is built the portal is not rendered and the styles went stale.
    """
    for name in ("styles", "assets"):
        source = ROOT / name
        if not source.is_dir():
            continue
        target = SITE / name
        if target.exists():
            shutil.rmtree(target)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source, target)

    # Cloudflare Pages reads _site/_redirects, which keeps the addresses of
    # pages that have moved working. Quarto leaves files whose name starts with
    # "_" out of the build, so it is copied here.
    redirects = ROOT / "_redirects"
    if redirects.is_file():
        SITE.mkdir(parents=True, exist_ok=True)
        shutil.copy2(redirects, SITE / "_redirects")


def prune_site(found: list[Path]) -> list[str]:
    """Delete published courses that no longer exist in the repository.

    _site survives between builds now, so a course that was renamed or removed
    would otherwise stay online for ever. A directory is kept when a directory
    of the same name exists under dersler/ — that also covers dersler/analiz,
    which holds a hub page rendered by the portal rather than a book.
    """
    published = SITE / "dersler"
    if not published.is_dir():
        return []
    gone = []
    for entry in published.iterdir():
        if not entry.is_dir() or (COURSES / entry.name).is_dir():
            continue
        shutil.rmtree(entry, ignore_errors=True)
        gone.append(entry.name)
    return gone


def publish(book: Path) -> None:
    """Copy the rendered book from dersler/<course>/_book/ under _site."""
    built = book / "_book"
    if not built.is_dir():
        raise RuntimeError(f"no _book directory was produced for '{book.name}'.")

    target = SITE / "dersler" / book.name
    if target.exists():
        shutil.rmtree(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(built, target)


def build_book(book: Path, with_exports: bool, stale: bool, quiet: bool) -> dict:
    """Export (optional), render and publish one course.

    `stale` says whether anything the book is built from has changed. An
    unchanged book is not rendered and not re-exported; it is only copied under
    _site again, which is what a portal render (which wipes _site) needs.
    """
    result = {"book": book.name, "failures": [], "rendered": False, "seconds": 0.0}
    if stale:
        if with_exports:
            if not quiet:
                print(f"\n\033[1m>> export: {book.name}\033[0m")
            result["failures"] = export_course(book)["failures"]
        seconds, _ = render(book, f"course: {book.name}", quiet=quiet)
        result["rendered"] = True
        result["seconds"] = seconds
    publish(book)
    # Files from an earlier export run are still published with --no-export
    publish_exports(book, SITE / "dersler" / book.name)
    return result


def main() -> None:
    argv = sys.argv[1:]
    jobs = default_jobs()
    if "--jobs" in argv:
        i = argv.index("--jobs")
        if i + 1 >= len(argv) or not argv[i + 1].isdigit():
            sys.exit("ERROR: --jobs needs a number, e.g. --jobs 6")
        jobs = max(1, int(argv[i + 1]))
        del argv[i:i + 2]
    args = [a for a in argv if not a.startswith("--")]
    flags = {a for a in argv if a.startswith("--")}
    unknown = flags - {"--no-export", "--force", "--serial"}
    if unknown:
        sys.exit(f"ERROR: unknown option(s): {', '.join(sorted(unknown))}")
    with_exports = "--no-export" not in flags
    force = "--force" in flags
    if "--serial" in flags:
        jobs = 1
    only = args[0] if args else None

    started = time.time()
    cache = load_cache()
    version = quarto_version()
    if cache.get("quarto") != version:
        if cache:
            print(f"   Quarto {version} (cache was written by {cache.get('quarto')}); rebuilding everything")
        force = True
    cached_books = cache.get("books", {}) if isinstance(cache.get("books"), dict) else {}
    failures: list[str] = []
    rendered: list[str] = []
    skipped: list[str] = []

    if only:
        target = COURSES / only
        if not (target / "_quarto.yml").exists():
            sys.exit(f"ERROR: there is no course project named '{only}'.")
        found = [target]
        wiped = False
    else:
        found = books()
        if not found:
            print("   ! no book projects found under dersler/")
        # 1) Portal pages — this step wipes the _site directory, so every book
        #    has to be copied under _site again afterwards.
        portal_now = fingerprint(portal_inputs())
        portal_stale = force or cache.get("portal") != portal_now or not (SITE / "index.html").exists()
        if portal_stale:
            render(ROOT, "portal (home page + course catalog)")
            cache["portal"] = portal_now
            wiped = True
        else:
            print("\n\033[1m>> portal\033[0m\n   unchanged, skipped")
            wiped = False

    sync_shared_assets()
    if not only:
        removed = prune_site(found)
        if removed:
            print("   removed from _site: " + ", ".join(sorted(removed)))

    # 2) Course books. Each one is an independent Quarto project, so they are
    #    rendered concurrently; a book nothing has touched is only copied.
    plan = []
    for book in found:
        now = fingerprint(book_inputs(book))
        published = (SITE / "dersler" / book.name).is_dir()
        built = (book / "_book").is_dir()
        stale = force or cached_books.get(book.name) != now or not built
        if not stale and published and not wiped:
            skipped.append(book.name)
            continue
        plan.append((book, stale, now))

    if plan:
        workers = min(jobs, len(plan))
        to_render = [b.name for b, stale, _ in plan if stale]
        print(f"\n\033[1m>> {len(to_render)} course(s) to render, "
              f"{len(plan) - len(to_render)} to copy, {len(skipped)} unchanged"
              f" — {workers} at a time\033[0m")

        def run(item):
            book, stale, now = item
            try:
                outcome = build_book(book, with_exports, stale, quiet=workers > 1)
            except Exception as exc:                     # a failed render or copy
                return {"book": book.name, "error": str(exc), "failures": [], "rendered": False}
            outcome["fingerprint"] = now
            return outcome

        if workers > 1:
            with ThreadPoolExecutor(max_workers=workers) as pool:
                outcomes = list(pool.map(run, plan))
        else:
            outcomes = [run(item) for item in plan]

        errors = []
        for outcome in outcomes:
            if outcome.get("error"):
                errors.append(f"{outcome['book']}: {outcome['error']}")
                continue
            failures += outcome["failures"]
            if outcome["rendered"]:
                rendered.append(f"{outcome['book']} ({outcome['seconds']:.0f} s)")
            cached_books[outcome["book"]] = outcome["fingerprint"]
        if rendered:
            print("   rendered: " + ", ".join(sorted(rendered)))
        if errors:
            cache["books"] = cached_books
            save_cache(cache)
            for line in errors:
                print(f"::error::{line}")
            sys.exit("ERROR: " + "; ".join(errors))

    cache["quarto"] = version
    cache["books"] = cached_books
    save_cache(cache)

    pages = len(list(SITE.rglob("*.html"))) if SITE.exists() else 0
    downloads = sum(len(list(SITE.rglob(f"*.{ext}"))) for ext in ("pdf", "epub")) if SITE.exists() else 0
    print(f"\n\033[1mDone.\033[0m {pages} HTML pages, {downloads} downloadable files, "
          f"{time.time() - started:.1f} s -> {SITE}")
    if skipped:
        print(f"   {len(skipped)} course(s) unchanged and left alone")
    if failures:
        # Every course must stay downloadable: fail the build (after finishing
        # everything else) so CI shows the broken unit instead of deploying
        # a site that silently lacks its files.
        print("\033[1m! Failed exports:\033[0m " + ", ".join(failures))
        for item in failures:
            print(f"::error::export failed: {item}")
        sys.exit(2)


if __name__ == "__main__":
    main()
