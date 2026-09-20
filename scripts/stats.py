# -*- coding: utf-8 -*-
"""Count what a Quarto lecture-notes project contains and print it as a table.

Usage:
    python scripts/stats.py                 # scan the project this script lives in
    python scripts/stats.py <path>          # scan another directory
    python scripts/stats.py --per-book      # add a per-book breakdown
    python scripts/stats.py --csv           # machine-readable, one row per book
    python scripts/stats.py --write-readme  # refresh the numbers in README.md

The README carries two generated sections, each between a pair of HTML comment
markers (see MARKERS below): the table of contents of the archive and the
figures of the archive. --write-readme rewrites what is between the markers and
leaves the rest of the file alone; scripts/build.py calls it after a build that
actually rendered something. Nothing outside the markers is ever touched, and
the file is only written when the text really changed, so a build that changes
no numbers leaves the working tree clean.

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


# ------------------------------------------------------- generated README bits

# Section name -> (opening marker, closing marker). The markers stay in the
# README; everything between them is replaced.
MARKERS = {
    "books": ("<!-- BOOKS-START -->", "<!-- BOOKS-END -->"),
    "metrics": ("<!-- METRICS-START -->", "<!-- METRICS-END -->"),
}

SITE = "https://acik-matematik.com/dersler"


def book_title(book):
    """The book's title from its _quarto.yml, or its directory name."""
    text = read_text(book / "_quarto.yml") or ""
    m = re.search(r'^\s*title:\s*"?([^"\n]+)"?\s*$', text, re.M)
    return m.group(1).strip() if m else book.name


def books_markdown(rows, root):
    """A collapsible list of every book, with its size and its state."""
    listed = [(book_title(root / "dersler" / r["kitap"]), r)
              for r in rows if not r.get("portal")]
    # The books whose chapters are online come first, each group by title --
    # the directory name is not what a reader sees.
    listed.sort(key=lambda item: (0 if item[1].get("bolum") else 1, item[0].lower()))
    entries = []
    for title, r in listed:
        if r.get("bolum"):
            entries.append("- [%s](%s/%s/) — %d bölüm, %s örnek ve alıştırma"
                           % (title, SITE, r["kitap"], r["bolum"],
                              "{:,}".format(r.get("ornek", 0)).replace(",", ".")))
        else:
            entries.append("- %s — müfredatı hazır, bölümleri yazılıyor" % title)
    written = sum(1 for r in rows if not r.get("portal") and r.get("bolum"))
    return "\n".join([
        "<details>",
        "<summary><strong>Arşivdeki %d ders</strong> — %d tanesinin bölümleri yayında (listeyi açmak için tıklayın)</summary>"
        % (len([r for r in rows if not r.get("portal")]), written),
        "",
        "\n".join(entries),
        "",
        "</details>",
    ])


def metrics_markdown(totals, rows):
    """The figures of the archive as a Markdown table."""
    def n(value):
        return "{:,}".format(value).replace(",", ".")

    books_only = [r for r in rows if not r.get("portal")]
    pairs = [
        ("📚 Kitap", n(len(books_only))),
        ("📖 Konu/Bölüm", n(sum(r.get("bolum", 0) for r in books_only))),
        ("📐 Teorem", n(totals.get("teorem", 0))),
        ("🔹 Lemma", n(totals.get("lemma", 0))),
        ("📝 Tanım", n(totals.get("tanim", 0))),
        ("✅ İspat", n(totals.get("ispat", 0))),
        ("🧮 Örnek ve alıştırma", n(totals.get("ornek", 0))),
        ("💡 Çözüm", n(totals.get("cozum", 0))),
        ("📊 Şekil", n(totals.get("sekil", 0))),
        ("✍️ Kelime", n(totals.get("kelime", 0))),
        ("🔤 Karakter", n(totals.get("karakter", 0))),
        ("💾 Kaynak metin", mb(totals.get("bayt", 0)).replace(".", ",")),
    ]
    lines = ["| | |", "|---|---:|"]
    lines += ["| %s | **%s** |" % (label, value) for label, value in pairs]
    lines.append("")
    lines.append("<sub>Bu tablo her derlemede `scripts/stats.py` tarafından güncellenir.</sub>")
    return "\n".join(lines)


def replace_marked(text, name, body):
    """Put `body` between the markers of `name`; return (text, changed?)."""
    start, end = MARKERS[name]
    i, j = text.find(start), text.find(end)
    if i < 0 or j < 0 or j < i:
        return text, None                      # markers missing: nothing to do
    new = "%s\n\n%s\n\n%s" % (start, body.strip("\n"), end)
    old = text[i:j + len(end)]
    if old == new:
        return text, False
    return text[:i] + new + text[j + len(end):], True


def write_readme(root, rows, totals):
    """Refresh the generated sections of README.md; return a status line."""
    readme = root / "README.md"
    text = read_text(readme)
    if text is None:
        return "README.md okunamadı, atlandı"
    updated, changes, missing = text, [], []
    for name, body in (("books", books_markdown(rows, root)),
                       ("metrics", metrics_markdown(totals, rows))):
        updated, changed = replace_marked(updated, name, body)
        if changed is None:
            missing.append(MARKERS[name][0])
        elif changed:
            changes.append(name)
    if missing:
        return "README.md güncellenmedi: %s işareti yok" % ", ".join(missing)
    if not changes:
        return "README.md zaten güncel"
    try:
        io.open(readme, "w", encoding="utf-8", newline="\n").write(updated)
    except OSError as exc:
        return "README.md yazılamadı: %s" % exc
    return "README.md güncellendi (%s)" % ", ".join(changes)


def update_readme(root=None):
    """Entry point for scripts/build.py: scan and refresh README.md."""
    root = pathlib.Path(root) if root else pathlib.Path(__file__).resolve().parent.parent
    rows, totals, _, _ = collect(root)
    return write_readme(root, rows, totals)


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

    if "--write-readme" in flags:
        print(write_readme(root, rows, totals))

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
