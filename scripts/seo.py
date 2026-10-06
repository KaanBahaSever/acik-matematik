"""
Açık Matematik — search engine metadata for the whole published site.

Every course is its own Quarto book, so Quarto's sitemap only covers the
portal (a handful of pages) and no page carries a canonical URL. On top of
that, Cloudflare Pages answers `/x.html` and `/x/index.html` with a 308 to
`/x` and `/x/`, so the `.html` addresses Quarto writes are redirects.

This script runs at the end of scripts/build.py, over the finished _site:

    * writes _site/sitemap.xml with every real page, using the addresses
      Cloudflare actually serves (no `.html`, `index.html` -> `/`);
    * adds <link rel="canonical"> with that same address to every page;
    * adds a "skip to content" link as the first focusable element of every
      page, and turns Quarto's toolbar actions (dark mode, reader mode), which
      are links with an empty href, into role="button" links with href="#";
    * writes _site/llms.txt, a plain-text map of the site and its courses.

Redirect stubs (Quarto `aliases:` pages with a meta refresh) and 404.html are
left out of the sitemap and are not touched. Running it again is safe.

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
BODY = re.compile(r"<body[^>]*>", re.I)
# Quarto writes its toolbar actions as <a href="" onclick="...; return false;">
ACTION_LINK = re.compile(r'<a href=""(?=[^>]*\bonclick=)')
SKIP_LINK = '<a class="skip-link" href="#quarto-document-content">İçeriğe geç</a>'


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


def postprocess(page: Path, url: str) -> bool:
    """Add the canonical link, the skip link and the button roles.

    Returns False for redirect stubs, which are left alone.
    """
    html = page.read_text(encoding="utf-8")
    if REFRESH.search(html[:4000]):
        return False
    link = f'<link rel="canonical" href="{escape(url)}">'
    if CANONICAL.search(html):
        new = CANONICAL.sub(link, html, count=1)
    else:
        new = html.replace("</head>", f"{link}\n</head>", 1)
    if 'class="skip-link"' not in new and 'id="quarto-document-content"' in new:
        new = BODY.sub(lambda m: f"{m.group(0)}\n{SKIP_LINK}", new, count=1)
    new = ACTION_LINK.sub('<a href="#" role="button"', new)
    if new != html:
        page.write_text(new, encoding="utf-8", newline="")
    return True


def write_llms_txt() -> int:
    """Write _site/llms.txt: what the site is and where each course lives.

    Only books with published chapters are listed, with the same titles and
    chapter counts that README.md shows. Returns the number of courses listed.
    """
    from stats import book_title, collect

    rows, _, _, _ = collect(ROOT)
    courses = sorted(
        ((book_title(ROOT / "dersler" / r["kitap"]), r["kitap"], r["bolum"])
         for r in rows if not r.get("portal") and r.get("bolum")),
        key=lambda c: c[0].lower())
    lines = [
        "# Açık Matematik",
        "",
        "> Lisans matematik derslerinden derlenmiş, açık kaynaklı ve reklamsız "
        "Türkçe ders notu arşivi. Notlar tanım, teorem, ispat ve çözümlü "
        "örneklerden oluşur; her ders ayrıca PDF ve EPUB olarak indirilebilir.",
        "",
        "İçerik Türkçedir ve CC BY-NC-SA 4.0 lisansıyla yayımlanır "
        "(https://creativecommons.org/licenses/by-nc-sa/4.0/deed.tr). "
        "Kaynak kodu: https://github.com/KaanBahaSever/acik-matematik",
        "",
        "## Site",
        "",
        f"- [Ana sayfa]({BASE}/): sitenin tanıtımı",
        f"- [Dersler]({BASE}/dersler/): bütün derslerin kataloğu",
        f"- [Site haritası]({BASE}/sitemap.xml): yayımlanan her sayfa",
        "",
        "## Dersler",
        "",
    ]
    lines += [f"- [{title}]({BASE}/dersler/{name}/): {count} bölüm"
              for title, name, count in courses]
    (SITE / "llms.txt").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    return len(courses)


def main() -> str:
    if not SITE.exists():
        return "seo: _site does not exist, nothing to do"
    urls = []
    for page in pages():
        url = public_url(page)
        if postprocess(page, url):
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
    courses = write_llms_txt()
    return f"sitemap.xml: {len(urls)} pages, canonical links added; llms.txt: {courses} courses"


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    print(main())
