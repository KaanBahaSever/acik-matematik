"""
Açık Matematik — files for AI assistants and agents, written into _site.

Called by scripts/seo.py (at the end of scripts/build.py) with the list of
published pages. It writes:

    * a Markdown copy next to every page (`x.html` -> `x.md`, served at
      `/x.md`, `/dersler/<course>/index.md` for a course's front page). The
      page's <main> is converted with Quarto's bundled pandoc; math comes out
      as `$...$` / `$$...$$` LaTeX, inline SVG figures are dropped. A copy is
      only rebuilt when its page's content changed;
    * llms.txt (https://llmstxt.org): what the site is, every course and every
      chapter in reading order, each linked to its Markdown copy;
    * robots.txt: every crawler, AI crawlers included, may read everything;
      Content-Signal (https://contentsignals.org) states the allowed uses;
    * an agent skill (/.well-known/agent-skills/index.json + SKILL.md, Agent
      Skills Discovery RFC v0.2.0) telling an agent how to find and cite notes.

_headers serves the .md files as text/markdown with noindex, so search engines
keep indexing the HTML pages only.

Usage
    python scripts/seo.py      (this module has no command of its own)
"""
from __future__ import annotations

import hashlib
import html as htmllib
import json
import re
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "_site"
BASE = "https://acik-matematik.com"
REPO = "https://github.com/KaanBahaSever/acik-matematik"
LICENSE_TR = "https://creativecommons.org/licenses/by-nc-sa/4.0/deed.tr"

# Bump when the conversion changes, so every copy is rebuilt once.
MD_FORMAT = "acik-matematik-md/2"
MAIN = re.compile(r'<main class="content"[^>]*>(.*?)</main>', re.S)
MATH = re.compile(r'<span class="math (inline|display)">(.*?)</span>', re.S)
DROP = re.compile(r"<(script|style|svg|nav)\b.*?</\1>", re.S | re.I)
RELATIVE_HTML = re.compile(r"\]\((?!https?:|/|#|mailto:)([^)\s]*?)\.html(#[^)\s]*)?\)")
SIDEBAR_LINK = re.compile(
    r'<a href="([^"]+)" class="sidebar-item-text sidebar-link[^"]*">\s*'
    r'<span class="menu-text">(.*?)</span>', re.S)
TAGS = re.compile(r"<[^>]+>")

AI_AGENTS = [
    "GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-SearchBot",
    "Claude-User", "PerplexityBot", "Perplexity-User", "Google-Extended",
    "Applebot-Extended", "CCBot", "meta-externalagent", "Bytespider",
    "Amazonbot", "DuckAssistBot", "MistralAI-User",
]
CONTENT_SIGNAL = "Content-Signal: search=yes, ai-input=yes, ai-train=yes"


# --------------------------------------------------------------------------
# Markdown copies
# --------------------------------------------------------------------------

def pandoc() -> str | None:
    found = shutil.which("pandoc")
    if found:
        return found
    q = shutil.which("quarto")
    if not q:
        return None
    tools = Path(q).resolve().parent / "tools"
    for cand in (tools / "pandoc.exe", tools / "pandoc",
                 tools / "x86_64" / "pandoc.exe", tools / "x86_64" / "pandoc"):
        if cand.is_file():
            return str(cand)
    return None


def to_markdown(exe: str, info: dict) -> bool:
    page: Path = info["page"]
    target = page.with_suffix(".md")
    text = page.read_text(encoding="utf-8")
    m = MAIN.search(text)
    body = m.group(1) if m else text
    # The build copies every book into _site again, so the page's date says
    # nothing; the hash of its content decides whether the copy is stale.
    digest = hashlib.sha1((MD_FORMAT + body).encode("utf-8")).hexdigest()
    if target.exists():
        with target.open(encoding="utf-8") as fh:
            if f"source: {digest}" in fh.read(600):
                return False
    body = DROP.sub("", body)
    # Quarto marks code blocks "sourceCode <lang>"; pandoc takes the first class.
    body = re.sub(r'class="sourceCode (\w+)', r'class="\1', body)
    maths: list[tuple[str, str]] = []

    def stash(mm: re.Match) -> str:
        tex = htmllib.unescape(mm.group(2)).strip()
        tex = re.sub(r"^\\[(\[]|\\[)\]]$", "", tex).strip()
        maths.append((mm.group(1), tex))
        return f"AMMATH{len(maths) - 1}X"

    body = MATH.sub(stash, body)
    out = subprocess.run([exe, "-f", "html", "-t", "gfm-raw_html", "--wrap=none"],
                         input=body, capture_output=True, text=True, encoding="utf-8")
    if out.returncode != 0:
        return False
    md = out.stdout

    def unstash(mm: re.Match) -> str:
        kind, tex = maths[int(mm.group(1))]
        return f"$${tex}$$" if kind == "display" else f"${tex}$"

    md = re.sub(r"AMMATH(\d+)X", unstash, md)
    md = RELATIVE_HTML.sub(lambda mm: f"]({mm.group(1)}.md{mm.group(2) or ''})", md)
    md = re.sub(r"\n{3,}", "\n\n", md).strip()
    head = [
        "---",
        f"title: {json.dumps(info['title'], ensure_ascii=False)}",
        f"url: {info['url']}",
    ]
    if info["book"]:
        head.append(f"course: {json.dumps(info['book'][1], ensure_ascii=False)}")
    head += [
        "language: tr",
        f"license: CC BY-NC-SA 4.0 ({LICENSE_TR})",
        f"format: {MD_FORMAT}",
        f"source: {digest}",
        "---",
        "",
    ]
    target.write_text("\n".join(head) + md + "\n", encoding="utf-8", newline="\n")
    return True


def prune_markdown() -> int:
    """Remove copies whose page no longer exists."""
    removed = 0
    for md in SITE.rglob("*.md"):
        if md.with_suffix(".html").exists() or "site_libs" in md.parts:
            continue
        try:
            with md.open(encoding="utf-8") as fh:
                ours = MD_FORMAT.split("/")[0] in fh.read(400)
        except OSError:
            continue
        if ours:
            md.unlink()
            removed += 1
    return removed


def write_markdown(infos: list[dict]) -> str:
    exe = pandoc()
    if exe is None:
        return "markdown copies skipped (pandoc not found)"
    with ThreadPoolExecutor(max_workers=8) as pool:
        made = sum(pool.map(lambda i: to_markdown(exe, i), infos))
    removed = prune_markdown()
    return f"markdown: {made} of {len(infos)} rebuilt" + (f", {removed} removed" if removed else "")


# --------------------------------------------------------------------------
# llms.txt
# --------------------------------------------------------------------------

def chapters(book_dir: str) -> list[tuple[str, str]]:
    """(title, page path under _site) of a book's pages in sidebar order."""
    index = SITE / "dersler" / book_dir / "index.html"
    if not index.is_file():
        return []
    seen, result = set(), []
    for href, label in SIDEBAR_LINK.findall(index.read_text(encoding="utf-8")):
        if href.startswith(("http", "/", "#")) or not href.endswith(".html"):
            continue
        rel = (index.parent / href).resolve().relative_to(SITE.resolve()).as_posix()
        if rel in seen:
            continue
        seen.add(rel)
        title = " ".join(htmllib.unescape(TAGS.sub(" ", label)).split())
        result.append((title, rel))
    return result


def write_llms_txt(infos: list[dict]) -> int:
    books = sorted({i["book"] for i in infos if i["book"]}, key=lambda b: b[1].lower())
    titles = {i["page"].relative_to(SITE).as_posix(): i["title"] for i in infos}
    lines = [
        "# Açık Matematik",
        "",
        "> Lisans matematik dersleri için açık kaynaklı ve reklamsız Türkçe ders "
        "notu arşivi. Notlar tanım, teorem, ispat ve çözümlü örneklerden oluşur; "
        "her ders ayrıca PDF ve EPUB olarak indirilebilir.",
        "",
        f"İçerik Türkçedir ve CC BY-NC-SA 4.0 lisansıyla yayımlanır ({LICENSE_TR}). "
        f"Kaynak kodu: {REPO}",
        "",
        "Her sayfanın bir Markdown kopyası vardır: adresin sonuna `.md` eklenir "
        "(bir dersin giriş sayfası için `/dersler/<ders>/index.md`). Formüller "
        "LaTeX olarak `$...$` içinde yazılıdır. Alıntı yaparken HTML sayfasının "
        "adresini verin.",
        "",
        "## Site",
        "",
        f"- [Ana sayfa]({BASE}/index.md): sitenin tanıtımı",
        f"- [Dersler]({BASE}/dersler/index.md): bütün derslerin kataloğu",
        f"- [Site haritası]({BASE}/sitemap.xml): yayımlanan her sayfa",
        "",
    ]
    listed = 0
    for book_dir, title in books:
        pages = chapters(book_dir)
        if len(pages) <= 1:          # a skeleton book: only its front page
            continue
        listed += 1
        lines += [f"## {title}", "",
                  f"Giriş ve müfredat: {BASE}/dersler/{book_dir}/ "
                  f"(PDF ve EPUB bağlantıları bu sayfadadır)", ""]
        for name, rel in pages:
            lines.append(f"- [{titles.get(rel, name)}]({BASE}/{rel[:-len('.html')]}.md)")
        lines.append("")
    (SITE / "llms.txt").write_text("\n".join(lines), encoding="utf-8", newline="\n")
    return listed


# --------------------------------------------------------------------------
# robots.txt and the agent skill
# --------------------------------------------------------------------------

def write_robots() -> None:
    lines = [
        "# Açık Matematik is an open archive: every crawler, AI crawlers",
        "# included, may read every page. Content-Signal states the allowed uses",
        "# (https://contentsignals.org); the licence is CC BY-NC-SA 4.0.",
        "",
        "User-agent: *",
        CONTENT_SIGNAL,
        "Allow: /",
        "",
        *[f"User-agent: {a}" for a in AI_AGENTS],
        CONTENT_SIGNAL,
        "Allow: /",
        "",
        f"Sitemap: {BASE}/sitemap.xml",
        "",
    ]
    (SITE / "robots.txt").write_text("\n".join(lines), encoding="utf-8", newline="\n")


SKILL_DESCRIPTION = (
    "Find, read and cite Turkish undergraduate mathematics lecture notes on "
    "acik-matematik.com (Açık Matematik): analysis, linear algebra, abstract "
    "algebra, topology, probability, differential equations and more. Use when "
    "a user asks about a university math topic in Turkish or wants Turkish "
    "course notes, proofs or solved examples.")

SKILL_BODY = """\
# Açık Matematik

Açık Matematik ({base}) is an open, ad-free archive of Turkish lecture notes
for undergraduate mathematics courses. Each course is a book of chapters with
definitions, theorems, full proofs and solved examples. Content language:
Turkish. Licence: CC BY-NC-SA 4.0.

## Finding a topic

1. Read {base}/llms.txt. It lists every course and every chapter in reading
   order, each linked to a Markdown copy of the page.
2. To search inside one course, fetch `{base}/dersler/<course>/search.json`:
   an array of sections with `title`, `section`, `href` and `text`.
3. Course directory names are Turkish slugs, e.g. `analiz-1`, `lineer-cebir`,
   `kompleks-analiz`, `topoloji`, `olasilik-teorisi`.

## Reading a page

- Append `.md` to a page address for clean Markdown:
  `{base}/dersler/topoloji/baz-ve-alt-baz` ->
  `{base}/dersler/topoloji/baz-ve-alt-baz.md`.
  A course's front page is `{base}/dersler/<course>/index.md`.
- Math is LaTeX inside `$...$` and `$$...$$`.
- Proofs and solutions are complete; "Çözüm" marks a solution, "İspat" a proof.
- Whole-course PDF and EPUB files are linked from each course's front page.

## Citing

Link the HTML page (the address without `.md`) and name the site
"Açık Matematik". Reuse must follow CC BY-NC-SA 4.0: attribution,
non-commercial, share-alike.
"""


def write_agent_skill() -> None:
    folder = SITE / ".well-known" / "agent-skills"
    skill = folder / "acik-matematik" / "SKILL.md"
    skill.parent.mkdir(parents=True, exist_ok=True)
    text = ("---\nname: acik-matematik\n"
            f"description: {json.dumps(SKILL_DESCRIPTION, ensure_ascii=False)}\n"
            "---\n\n" + SKILL_BODY.format(base=BASE))
    data = text.encode("utf-8")
    skill.write_bytes(data)
    index = {
        "$schema": "https://schemas.agentskills.io/discovery/0.2.0/schema.json",
        "skills": [{
            "name": "acik-matematik",
            "type": "skill-md",
            "description": SKILL_DESCRIPTION,
            "url": "/.well-known/agent-skills/acik-matematik/SKILL.md",
            "digest": "sha256:" + hashlib.sha256(data).hexdigest(),
        }],
    }
    (folder / "index.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def write_agent_files(infos: list[dict]) -> str:
    markdown = write_markdown(infos)
    courses = write_llms_txt(infos)
    write_robots()
    write_agent_skill()
    return f"{markdown}; llms.txt: {courses} courses; robots.txt and agent skill written"
