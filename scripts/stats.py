# -*- coding: utf-8 -*-
"""Count what a Quarto lecture-notes project contains and print it as a table.

Usage:
    python scripts/stats.py                 # scan the project this script lives in
    python scripts/stats.py <path>          # scan another directory
    python scripts/stats.py --per-book      # add a per-book breakdown
    python scripts/stats.py --csv           # machine-readable, one row per book

What it counts
--------------
book          a directory holding its own _quarto.yml
chapter       a .qmd file (a book's index.qmd is its curriculum page and is
              reported separately, so "chapter" means real content)
theorem,      crossref divs written as {#thm-...} / {#lem-...} / {#exm-...} /
lemma,        {#exr-...}, and also the class form used by other projects
example       (::: {.theorem}, ::: {.lemma}, ::: {.example}, ::: {.exercise})
proof         ::: {.proof} / ::: {.ispat} (this project's collapsible proof
              block), {#prf-...} and LaTeX \\begin{proof}
word, char    prose only: the YAML header, fenced code blocks and raw HTML
              blocks (which carry the inline SVG figures) are stripped first,
              because a drawing is thousands of characters of path data that
              nobody reads. The raw totals are printed as well.
disk          bytes on disk: the .qmd sources, the project without build
              output, and — when present — the rendered site.

Every file is read defensively: unreadable files are skipped and reported
rather than stopping the scan.
"""
import io
import os
import pathlib
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Directories that hold generated output, not content.
SKIP_DIRS = {"_site", "_book", "_freeze", "_export", "_export-src", "_export-figs",
             ".quarto", ".git", "node_modules", "__pycache__", ".venv", "venv"}

FRONT_MATTER = re.compile(r"\A---\r?\n.*?\r?\n---\r?\n", re.S)
FENCED_BLOCK = re.compile(r"^[ \t]*```.*?^[ \t]*```", re.S | re.M)

PATTERNS = {
    "teorem": [r"\{#thm-", r":::+\s*\{\s*\.theorem\b"],
    "lemma": [r"\{#lem-", r":::+\s*\{\s*\.lemma\b"],
    "ispat": [r"\{#prf-", r":::+\s*\{\s*\.(?:proof|ispat)\b", r"\\begin\{proof\}"],
    "ornek": [r"\{#exm-", r"\{#exr-", r":::+\s*\{\s*\.(?:example|exercise|problem)\b"],
    "tanim": [r"\{#def-", r":::+\s*\{\s*\.definition\b"],
    "onerme": [r"\{#prp-", r"\{#cor-", r":::+\s*\{\s*\.(?:proposition|corollary)\b"],
    "cozum": [r":::+\s*\{\s*\.(?:solution|cozum)\b"],
    "sekil": [r'<figure\b', r"^!\[.*\]\(.*\)"],
}
PATTERNS = {k: [re.compile(p, re.M) for p in v] for k, v in PATTERNS.items()}
METRIC_KEYS = list(PATTERNS)


def walk_qmd(root):
    """Every .qmd under root, build output left out."""
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        for name in filenames:
            if name.lower().endswith(".qmd"):
                yield pathlib.Path(dirpath) / name


def read_text(path):
    """File contents, or None when the file cannot be read."""
    try:
        with io.open(path, encoding="utf-8", errors="replace") as fh:
            return fh.read()
    except (OSError, ValueError):
        return None


def prose(text):
    return FENCED_BLOCK.sub("", FRONT_MATTER.sub("", text))


def scan_file(path):
    text = read_text(path)
    if text is None:
        return None
    body = prose(text)
    row = {k: sum(len(p.findall(text)) for p in pats) for k, pats in PATTERNS.items()}
    row["kelime"] = len(body.split())
    row["karakter"] = len(body)
    row["ham_karakter"] = len(text)
    try:
        row["bayt"] = path.stat().st_size
    except OSError:
        row["bayt"] = 0
    return row


def dir_size(root, skip=SKIP_DIRS):
    total = 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in skip]
        for name in filenames:
            try:
                total += (pathlib.Path(dirpath) / name).stat().st_size
            except OSError:
                pass
    return total


def mb(n):
    return "%.1f MB" % (n / (1024 * 1024))


def add(into, row):
    for k, v in row.items():
        into[k] = into.get(k, 0) + v
    return into


def collect(root):
    """(per-book rows, totals, files outside any book, unreadable files)"""
    books = sorted({p.parent for p in root.rglob("_quarto.yml")
                    if not any(d in SKIP_DIRS for d in p.parts)})
    # The project root often holds a _quarto.yml of its own (the portal); it is
    # not a book unless it has chapters of its own.
    rows, totals, unreadable = [], {}, []
    claimed = set()
    # Deepest first: a book nested inside another project (or inside the root
    # project) owns its own files, so nothing is counted twice.
    for book in sorted(books, key=lambda b: len(b.parts), reverse=True):
        files = [f for f in sorted(walk_qmd(book)) if f not in claimed]
        if not files:
            continue
        index = [f for f in files if f.name == "index.qmd" and f.parent == book]
        chapters = [f for f in files if f not in index]
        if not chapters and book == root:
            continue                      # portal project, no chapters of its own
        stats = {}
        for f in files:
            row = scan_file(f)
            if row is None:
                unreadable.append(f)
                continue
            add(stats, row)
            claimed.add(f)
        rows.append(dict(kitap=book.name if book != root else "(portal)",
                         portal=1 if book == root else 0,
                         bolum=len(chapters), mufredat=len(index), **stats))
        add(totals, {k: v for k, v in rows[-1].items() if k != "kitap"})
    loose = [f for f in walk_qmd(root) if f not in claimed]
    for f in loose:
        row = scan_file(f)
        if row is None:
            unreadable.append(f)
            continue
        add(totals, row)
        totals["bolum"] = totals.get("bolum", 0) + 1
    return rows, totals, loose, unreadable


def print_table(pairs, title):
    width = max(len(k) for k, _ in pairs)
    line = "+" + "-" * (width + 2) + "+" + "-" * 18 + "+"
    print(line)
    print("| %-*s | %16s |" % (width, title, ""))
    print(line)
    for key, value in pairs:
        print("| %-*s | %16s |" % (width, key, value))
    print(line)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = {a for a in sys.argv[1:] if a.startswith("--")}
    here = pathlib.Path(__file__).resolve().parent
    default = here.parent if (here.parent / "dersler").is_dir() else pathlib.Path.cwd()
    root = pathlib.Path(args[0]).resolve() if args else default
    if not root.is_dir():
        sys.exit("Dizin bulunamadi: %s" % root)

    rows, totals, loose, unreadable = collect(root)
    if not rows and not totals:
        sys.exit("Bu dizinde .qmd dosyasi yok: %s" % root)

    if "--csv" in flags:
        keys = ["kitap", "bolum", "mufredat"] + METRIC_KEYS + ["kelime", "karakter", "bayt"]
        print(",".join(keys))
        for r in rows:
            print(",".join(str(r.get(k, 0)) for k in keys))
        return

    # The root project holds the portal pages (home page, catalogue); it is not
    # a book, so it is reported on its own line.
    books_only = [r for r in rows if not r.get("portal")]
    portal_pages = sum(r.get("bolum", 0) + r.get("mufredat", 0) for r in rows if r.get("portal")) + len(loose)
    print("\nProje: %s\n" % root)
    print_table([
        ("Kitap sayısı", len(books_only)),
        ("Konu/Bölüm sayısı", sum(r.get("bolum", 0) for r in books_only)),
        ("Müfredat sayfası", sum(r.get("mufredat", 0) for r in books_only)),
        ("Portal sayfası", portal_pages),
        ("Teorem sayısı", totals.get("teorem", 0)),
        ("Lemma sayısı", totals.get("lemma", 0)),
        ("İspat sayısı", totals.get("ispat", 0)),
        ("Örnek/Soru sayısı", totals.get("ornek", 0)),
        ("Çözüm sayısı", totals.get("cozum", 0)),
        ("Tanım sayısı", totals.get("tanim", 0)),
        ("Önerme/Sonuç sayısı", totals.get("onerme", 0)),
        ("Şekil sayısı", totals.get("sekil", 0)),
        ("Toplam kelime", "{:,}".format(totals.get("kelime", 0))),
        ("Toplam karakter", "{:,}".format(totals.get("karakter", 0))),
        ("Ham karakter (kod dahil)", "{:,}".format(totals.get("ham_karakter", 0))),
        (".qmd kaynak boyutu", mb(totals.get("bayt", 0))),
        ("Proje boyutu (çıktısız)", mb(dir_size(root))),
        ("Toplam disk (her şey)", mb(dir_size(root, skip={".git"}))),
    ], "METRİK")

    if "--per-book" in flags:
        head = "%-30s %6s %7s %6s %6s %7s %10s" % ("kitap", "bölüm", "teorem", "lemma", "ispat", "örnek", "kelime")
        print("\n" + head)
        print("-" * len(head))
        for r in sorted(rows, key=lambda x: -x.get("kelime", 0)):
            print("%-30s %6d %7d %6d %6d %7d %10s"
                  % (r["kitap"][:30], r.get("bolum", 0), r.get("teorem", 0), r.get("lemma", 0),
                     r.get("ispat", 0), r.get("ornek", 0), "{:,}".format(r.get("kelime", 0))))

    if loose:
        print("\nHiçbir kitaba ait olmayan %d .qmd dosyası da sayıldı." % len(loose))
    if unreadable:
        print("\nOkunamayan %d dosya atlandı:" % len(unreadable))
        for f in unreadable[:10]:
            print("   ", f)


if __name__ == "__main__":
    main()
