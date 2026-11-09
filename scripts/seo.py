"""
Açık Matematik — search engine and AI agent metadata for the published site.

Every course is its own Quarto book, so Quarto's sitemap only covers the
portal (a handful of pages) and no page carries a canonical URL. On top of
that, Cloudflare Pages answers `/x.html` and `/x/index.html` with a 308 to
`/x` and `/x/`, so the `.html` addresses Quarto writes are redirects.

This script runs at the end of scripts/build.py, over the finished _site:

    * writes _site/sitemap.xml with every real page, using the addresses
      Cloudflare actually serves (no `.html`, `index.html` -> `/`), each with
      the date of the last commit that touched its source file;
    * adds <link rel="canonical"> with that same address to every page;
    * gives a course's landing page the title "<Course> Ders Notları", which
      is what people search for, instead of the book's "Müfredat ve Giriş";
    * adds Open Graph / Twitter card tags, a <link rel="alternate"> to the
      page's Markdown copy and, on course pages, JSON-LD structured data
      (BreadcrumbList + LearningResource);
    * adds a "skip to content" link as the first focusable element of every
      page, and turns Quarto's toolbar actions (dark mode, reader mode), which
      are links with an empty href, into role="button" links with href="#";
    * hands over to scripts/agent_files.py, which writes the Markdown copies,
      llms.txt, robots.txt and the agent skill.

Redirect stubs (Quarto `aliases:` pages with a meta refresh) and 404.html are
left out of the sitemap and are not touched. Running it again is safe: the
injected block sits between <!-- seo:start --> and <!-- seo:end --> markers
and is replaced on every run.

Usage
    python scripts/seo.py
"""
from __future__ import annotations

import html as htmllib
import json
import re
import subprocess
import sys
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "_site"
BASE = "https://acik-matematik.com"
SITE_NAME = "Açık Matematik"
LOGO = f"{BASE}/assets/logo-512.png"
LICENSE = "https://creativecommons.org/licenses/by-nc-sa/4.0/"
AUTHOR = {"@type": "Person", "name": "Kaan Baha Sever",
          "url": "https://github.com/KaanBahaSever"}

SKIP_NAMES = {"404.html"}
SKIP_DIRS = {"site_libs"}
REFRESH = re.compile(r'http-equiv=["\']refresh["\']', re.I)
CANONICAL = re.compile(r'<link[^>]+rel=["\']canonical["\'][^>]*>', re.I)
BODY = re.compile(r"<body[^>]*>", re.I)
TITLE = re.compile(r"<title>(.*?)</title>", re.S)
DESCRIPTION = re.compile(r'<meta name="description" content="([^"]*)"')
BLOCK = re.compile(r"\n?<!-- seo:start -->.*?<!-- seo:end -->", re.S)
# Quarto writes its toolbar actions as <a href="" onclick="...; return false;">
ACTION_LINK = re.compile(r'<a href=""(?=[^>]*\bonclick=)')
SKIP_LINK = '<a class="skip-link" href="#quarto-document-content">İçeriğe geç</a>'
# Quarto joins a book page's title and the book's title with an en dash.
TITLE_SEP = " – "


def public_url(page: Path) -> str:
    rel = page.relative_to(SITE).as_posix()
    if rel == "index.html":
        return BASE + "/"
    if rel.endswith("/index.html"):
        return f"{BASE}/{rel[:-len('index.html')]}"
    return f"{BASE}/{rel[:-len('.html')]}"


def markdown_url(page: Path) -> str:
    """Address of the page's Markdown copy (see agent_files.py)."""
    return f"{BASE}/{page.relative_to(SITE).with_suffix('.md').as_posix()}"


def pages() -> list[Path]:
    found = []
    for page in sorted(SITE.rglob("*.html")):
        parts = page.relative_to(SITE).parts
        if page.name in SKIP_NAMES or SKIP_DIRS.intersection(parts):
            continue
        found.append(page)
    return found


def book_of(page: Path) -> tuple[str, str] | None:
    """(directory, title) of the course book a page belongs to, if any."""
    from stats import book_title

    parts = page.relative_to(SITE).parts
    if len(parts) < 3 or parts[0] != "dersler":
        return None
    book = ROOT / "dersler" / parts[1]
    if not (book / "_quarto.yml").is_file():
        return None
    return parts[1], book_title(book)


def is_landing(page: Path) -> bool:
    """A course's front page: dersler/<course>/index.html (books and hubs)."""
    parts = page.relative_to(SITE).parts
    return len(parts) == 3 and parts[0] == "dersler" and parts[2] == "index.html"


def last_modified() -> dict[str, str]:
    """Repository path -> date (YYYY-MM-DD) of the last commit that touched it."""
    try:
        out = subprocess.run(
            ["git", "log", "--format=%x00%cs", "--name-only", "--", "dersler", "index.qmd"],
            cwd=ROOT, capture_output=True, text=True, encoding="utf-8", check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        return {}
    dates: dict[str, str] = {}
    date = ""
    for line in out.splitlines():
        if line.startswith("\x00"):
            date = line[1:].strip()
        elif line.strip() and date:
            dates.setdefault(line.strip(), date)
    return dates


def source_of(page: Path) -> str:
    """The repository path of the .qmd a page was rendered from."""
    return page.relative_to(SITE).with_suffix(".qmd").as_posix()


def json_ld(data: dict) -> str:
    text = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    return '<script type="application/ld+json">' + text.replace("</", "<\\/") + "</script>"


def structured_data(page: Path, url: str, name: str, description: str,
                    book: tuple[str, str] | None) -> str:
    if book is None:
        return ""
    book_dir, book_title = book
    book_url = f"{BASE}/dersler/{book_dir}/"
    crumbs = [(SITE_NAME, f"{BASE}/"), ("Dersler", f"{BASE}/dersler/"), (book_title, book_url)]
    if url != book_url:
        crumbs.append((name, url))
    graph = [
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": i, "name": n, "item": u}
            for i, (n, u) in enumerate(crumbs, 1)]},
        {"@type": "LearningResource", "name": name, "url": url,
         "description": description, "inLanguage": "tr",
         "learningResourceType": "Ders notu", "educationalLevel": "Lisans",
         "isAccessibleForFree": True, "license": LICENSE,
         "isPartOf": {"@type": "Book", "name": book_title, "url": book_url},
         "author": AUTHOR, "publisher": AUTHOR},
    ]
    return json_ld({"@context": "https://schema.org", "@graph": graph})


def postprocess(page: Path, url: str) -> dict | None:
    """Rewrite one page; returns what llms.txt needs, or None for stubs."""
    html = page.read_text(encoding="utf-8")
    if REFRESH.search(html[:4000]):
        return None
    book = book_of(page)
    m = TITLE.search(html)
    title = htmllib.unescape(m.group(1).strip()) if m else SITE_NAME
    if is_landing(page):
        course = book[1] if book else title.split(TITLE_SEP)[0].removesuffix(" Ders Notları")
        title = f"{course} Ders Notları{TITLE_SEP}{SITE_NAME}"
        html = TITLE.sub(lambda _: f"<title>{escape(title)}</title>", html, count=1)
    name = title.split(TITLE_SEP)[0].strip()
    d = DESCRIPTION.search(html)
    description = htmllib.unescape(d.group(1)) if d else ""

    attr = lambda s: escape(s, {'"': "&quot;"})  # noqa: E731
    block = [
        "<!-- seo:start -->",
        f'<meta property="og:type" content="{"article" if book and not is_landing(page) else "website"}">',
        f'<meta property="og:site_name" content="{SITE_NAME}">',
        '<meta property="og:locale" content="tr_TR">',
        f'<meta property="og:title" content="{attr(title)}">',
        f'<meta property="og:url" content="{attr(url)}">',
        f'<meta property="og:image" content="{LOGO}">',
        '<meta name="twitter:card" content="summary">',
        f'<link rel="alternate" type="text/markdown" href="{attr(markdown_url(page))}">',
    ]
    if description:
        block.insert(5, f'<meta property="og:description" content="{attr(description)}">')
    ld = structured_data(page, url, name, description, book)
    if ld:
        block.append(ld)
    block.append("<!-- seo:end -->")

    link = f'<link rel="canonical" href="{escape(url)}">'
    new = BLOCK.sub("", html)
    if CANONICAL.search(new):
        new = CANONICAL.sub(link, new, count=1)
    else:
        new = new.replace("</head>", f"{link}\n</head>", 1)
    new = new.replace("</head>", "\n".join(block) + "\n</head>", 1)
    if 'class="skip-link"' not in new and 'id="quarto-document-content"' in new:
        new = BODY.sub(lambda m: f"{m.group(0)}\n{SKIP_LINK}", new, count=1)
    new = ACTION_LINK.sub('<a href="#" role="button"', new)
    if new != page.read_text(encoding="utf-8"):
        page.write_text(new, encoding="utf-8", newline="")
    return {"page": page, "url": url, "title": name, "description": description,
            "book": book}


def main() -> str:
    if not SITE.exists():
        return "seo: _site does not exist, nothing to do"
    from agent_files import write_agent_files

    dates = last_modified()
    entries, infos = [], []
    for page in pages():
        url = public_url(page)
        info = postprocess(page, url)
        if info is None:
            continue
        infos.append(info)
        lastmod = dates.get(source_of(page))
        entries.append(f"  <url><loc>{escape(url)}</loc>"
                       + (f"<lastmod>{lastmod}</lastmod>" if lastmod else "") + "</url>")
    (SITE / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(entries) + "\n</urlset>\n",
        encoding="utf-8", newline="\n")
    return (f"sitemap.xml: {len(entries)} pages, canonical and metadata added; "
            + write_agent_files(infos))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    print(main())
