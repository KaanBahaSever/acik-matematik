---
paths:
  - "styles/**"
  - "scripts/**"
  - "assets/**"
  - "_quarto.yml"
  - "_kitap-ortak.yml"
---

# Infrastructure rules (CSS, scripts, deployment)

## CSS

- Write colors as `:root` tokens and also give their dark-theme counterparts. Tokens: `--academic-bg`, `--academic-text`, `--color-theory`, `--color-base`, `--color-practice`, `--color-remark`.
  - The same palette also lives in `scripts/export_figures.lua` and `scripts/center_figures.py`. If you change one, update all three together.
- Mobile overflow:
  - The scroll container (`overflow-x: auto`) sits on: `p`, `dd`, `blockquote`, `figcaption`, `ol/ul`, `table`.
  - It never goes on `li`, because the bullet gets clipped. It never goes on `body`/`html` either, because the sticky sidebar breaks.
  - The padding and the visible thin scrollbar on `mjx-container[display]` are never removed. Without the padding the top of the formula is cut off; without the scrollbar the overflow is invisible.
- The class names produced by the Lua filters are a contract with the CSS: `.collapsible*`, `.downloads*`, `.curriculum`, `.landing*`, `.course-list`, `.catalog-back`, `.calculator`, `.calc-*`.
- Never deliver a CSS or layout change without measuring it.
  - Widths: phone (390), tablet (768), desktop (1280, 1920) and ultra-wide (2560). Check both the light and the dark theme.
  - Command: `python scripts/check_layout.py dersler/<course>/<page>.html --widths 390,768,1280,1920,2560`. The script returns 0 even when there is overflow; read the `RESULT` line.
  - For a visual complaint, find the root cause by measuring first.

## Build and export

- A change to a Lua filter or to `_kitap-ortak.yml` rebuilds every book; try it on a single book first.
- `build.py` calls `scripts/seo.py` at the end of every run. The script rewrites `_site/sitemap.xml` with all pages and adds `rel="canonical"` to every page. URLs use the form Cloudflare serves: no `.html`, and `/` instead of `index.html`. This step is never removed, because Quarto's own sitemap covers only the portal. The same script puts an "İçeriğe geç" (skip to content) link at the top of every page, turns Quarto's `href=""` toolbar links into `href="#" role="button"` and generates `_site/llms.txt` from the course list.
- `build.py` copies the root `_headers` (HSTS) and `_redirects` files into `_site/`; Cloudflare Pages reads both.
- The downloadable files are PDF (Typst) and EPUB; there is no DOCX.
  - The bottom of every PDF page carries the site URL and the CC BY-NC-SA 4.0 license (`scripts/export-assets/footer.typ`). The EPUB defines `dc:rights`. Keep these when changing the export.
  - The "Bu sürüm" (this version) date in the files comes from the last commit.
- If you served `_site` with `python -m http.server`, stop it when you are done; if it stays open, the build fails with `WinError 32`.

## Deployment

- There is no CI and no GitHub Actions. `scripts/deploy.py` builds the site on this machine and publishes it with `wrangler pages deploy`.
  - The `pre-push` hook starts it in the background after every push to main. It is installed once with `python scripts/deploy.py --install-hook` and shared by every worktree. A manual run is `python scripts/deploy.py`.
  - It builds in its own clone (`~/.acik-matematik/checkout`), never in a working tree, so only what is on main goes live. The clone keeps `_site`, the `_book` directories and `.build-cache.json`, so only the changed courses are rendered.
  - State and logs live in `~/.acik-matematik/` (`state.json`, `logs/`), not in `%LOCALAPPDATA%`: the desktop app's MSIX virtualization redirects AppData writes into its private folder.
  - `--status` shows what is live and whether a run is going on; `--wait` blocks until the run ends. The deployment shares the machine's memory with agents and local builds, so after a push that rebuilds many books, wait for it before heavy work.
  - A push that touches only README, LICENCE, `docs/`, `.gitignore`, `CLAUDE.md` or `.claude/` is marked live without a deployment.
  - The outcome arrives as a Windows notification; a failed run's log path appears in `--status`.
- The script uses only the standard library. The Cloudflare token comes from the `CLOUDFLARE_API_TOKEN` user environment variable and is never printed or written to a file.
- Wrangler is pinned (`WRANGLER_VERSION`); bump it deliberately.
- Nothing that executes code during the build is added.

## Repository layout

- Only permanent, documented tools enter the repository; one-off scripts stay in the scratchpad.
- If you add a new infrastructure file (Lua filter, script), explain the reason to the user.
