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

Order matters: rendering the root project wipes _site, so the course books
are rendered and copied AFTER the root project.

Usage:
    python scripts/build.py              # build everything
    python scripts/build.py kriptografi  # build a single course only
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COURSES = ROOT / "dersler"
SITE = ROOT / "_site"

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


def render(target: Path, label: str) -> float:
    """Render the Quarto project in `target`; return the elapsed seconds."""
    print(f"\n\033[1m>> {label}\033[0m")
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
        print(result.stdout)
        print(result.stderr, file=sys.stderr)
        sys.exit(f"ERROR: '{label}' failed to render (exit code {result.returncode}).")

    # Surface Quarto warnings so they are not missed
    for line in (result.stdout + result.stderr).splitlines():
        if "WARN" in line or "ERROR" in line:
            print(f"   ! {line.strip()}")

    print(f"   done ({elapsed:.1f} s)")
    return elapsed


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


def publish(book: Path) -> None:
    """Move the rendered book from dersler/<course>/_book/ under _site."""
    built = book / "_book"
    if not built.is_dir():
        sys.exit(f"ERROR: no _book directory was produced for '{book.name}'.")

    target = SITE / "dersler" / book.name
    if target.exists():
        shutil.rmtree(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(built, target)


def main() -> None:
    only = sys.argv[1] if len(sys.argv) > 1 else None
    started = time.time()

    if only:
        target = COURSES / only
        if not (target / "_quarto.yml").exists():
            sys.exit(f"ERROR: there is no course project named '{only}'.")
        render(target, f"course: {only}")
        publish(target)
        sync_shared_assets()
    else:
        # 1) Portal pages — this step wipes the _site directory
        render(ROOT, "portal (home page + course catalog)")

        # 2) Course books — output goes under _site/dersler/<course>/
        found = books()
        if not found:
            print("   ! no book projects found under dersler/")
        for book in found:
            render(book, f"course: {book.name}")
            publish(book)

    pages = len(list(SITE.rglob("*.html"))) if SITE.exists() else 0
    print(f"\n\033[1mDone.\033[0m {pages} HTML pages, {time.time() - started:.1f} s -> {SITE}")


if __name__ == "__main__":
    main()
