"""
Açık Matematik — search engine metadata for the whole published site.

Every course is its own Quarto book, so Quarto's sitemap only covers the
portal (a handful of pages) and no page carries a canonical URL. On top of
that, Cloudflare Pages answers `/x.html` and `/x/index.html` with a 308 to
`/x` and `/x/`, so the `.html` addresses Quarto writes are redirects.

This script runs at the end of scripts/build.py, over the finished _site:

    * writes _site/sitemap.xml with every real page, using the addresses
      Cloudflare actually serves (no `.html`, `index.html` -> `/`);
    * adds <link rel="canonical"> with that same address to every page.

Redirect stubs (Quarto `aliases:` pages with a meta refresh) and 404.html are
left out of the sitemap and get no canonical link. Running it again is safe.

Usage
    python scripts/seo.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "_site"
BASE = "https://acik-matematik.com"

SKIP_NAMES = {"404.html"}
SKIP_DIRS = {"site_libs"}
REFRESH = re.compile(r'http-equiv=["\']refresh["\']', re.I)
CANONICAL = re.compile(r'<link[^>]+rel=["\']canonical["\'][^>]*>', re.I)


def public_url(page: Path) -> str:
    rel = page.relative_to(SITE).as_posix()
    if rel == "index.html":
        return BASE + "/"
    if rel.endswith("/index.html"):
        return f"{BASE}/{rel[:-len('index.html')]}"
    return f"{BASE}/{rel[:-len('.html')]}"


def pages() -> list[Path]:
    found = []
    for page in sorted(SITE.rglob("*.html")):
        parts = page.relative_to(SITE).parts
        if page.name in SKIP_NAMES or SKIP_DIRS.intersection(parts):
            continue
        found.append(page)
    return found


def add_canonical(page: Path, url: str) -> bool:
    """Insert or refresh the canonical link. Returns False for redirect stubs."""
    html = page.read_text(encoding="utf-8")
    if REFRESH.search(html[:4000]):
        return False
    link = f'<link rel="canonical" href="{escape(url)}">'
    if CANONICAL.search(html):
        new = CANONICAL.sub(link, html, count=1)
    else:
        new = html.replace("</head>", f"{link}\n</head>", 1)
    if new != html:
        page.write_text(new, encoding="utf-8", newline="")
    return True


def main() -> str:
    if not SITE.exists():
        return "seo: _site does not exist, nothing to do"
    urls = []
    for page in pages():
        url = public_url(page)
        if add_canonical(page, url):
            urls.append(url)
    body = "\n".join(f"  <url><loc>{escape(u)}</loc></url>" for u in urls)
    (SITE / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{body}\n</urlset>\n",
        encoding="utf-8", newline="\n")
    robots = SITE / "robots.txt"
    if not robots.exists():
        robots.write_text(f"Sitemap: {BASE}/sitemap.xml\n", encoding="utf-8", newline="\n")
    return f"sitemap.xml: {len(urls)} pages, canonical links added"


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    print(main())
