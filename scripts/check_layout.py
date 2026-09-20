# -*- coding: utf-8 -*-
"""Measure the page layout of built pages at several viewport widths.

Usage:  python scripts/check_layout.py <page> [<page> ...] [--widths 390,768,1280,1920,2560]
        <page> is a path under _site, e.g. dersler/topoloji/baz-ve-alt-baz.html

Headless Chrome on Windows refuses to make its window narrower than ~485 CSS px,
so every width is measured inside an iframe of that width: media queries inside
an iframe follow the iframe's own viewport. One Chrome run covers all widths.

For each page and width it reports, in CSS pixels:
  viewport, page scrollWidth (horizontal overflow is a failure),
  left sidebar   left..right edge and width,
  content column left..right edge and width, plus the gap to each side,
  right TOC      left..right edge and width,
  TOC reachable  whether a table of contents is visible, or reachable through a
                 visible toggle/details element (the mobile case).
"""
import json
import os
import pathlib
import re
import socket
import subprocess
import sys
import tempfile
import time
import urllib.parse

sys.stdout.reconfigure(encoding="utf-8")

REPO = pathlib.Path(__file__).resolve().parent.parent
SITE = REPO / "_site"
CHROME = os.environ.get("CHROME", r"C:\Program Files\Google\Chrome\Application\chrome.exe")
FLAGS = ["--headless=new", "--no-sandbox", "--disable-gpu", "--force-device-scale-factor=1"]

WRAPPER = """<!doctype html><meta charset="utf-8"><title>layout probe</title>
<style>html,body{margin:0;padding:0}iframe{border:0;display:block}</style>
<body>
<script>
const PAGES = __PAGES__;
const WIDTHS = __WIDTHS__;
const jobs = [];
for (const page of PAGES) for (const w of WIDTHS) jobs.push([page, w]);

function box(el) {
  if (!el) return null;
  const r = el.getBoundingClientRect();
  const cs = getComputedStyle(el);
  return {l: Math.round(r.left), r: Math.round(r.right), w: Math.round(r.width),
          h: Math.round(r.height), display: cs.display, visible: r.width > 0 && r.height > 0 &&
          cs.visibility !== "hidden" && cs.display !== "none"};
}

function measure(doc, win, width) {
  const de = doc.documentElement;
  const q = (s) => doc.querySelector(s);
  // A table of contents counts as reachable when it is on screen, or when a
  // visible control (Quarto's secondary nav, a <details>, our own toggle) opens it.
  const toc = q("#TOC") || q("nav.toc-active") || q("#quarto-margin-sidebar nav");
  const tocBox = box(toc);
  let reach = tocBox && tocBox.visible ? "gorunur" : "yok";
  if (reach === "yok") {
    const toggles = [".quarto-btn-toggle", "#quarto-back-to-top", ".quarto-secondary-nav-title",
                     "[data-bs-target='#quarto-secondary-nav']", ".quarto-toc-toggle",
                     "details.quarto-toc summary", "#quarto-toc-toggle"];
    for (const sel of toggles) {
      const el = q(sel);
      const b = box(el);
      if (b && b.visible) { reach = "dugme:" + sel; break; }
    }
  }
  // The mobile panel built by scripts/mobile-toc.html: it must be visible,
  // carry links, open, and every link must point at a heading that exists.
  var mt = q("details.mobile-toc");
  var mtInfo = "yok";
  if (mt) {
    var mb = box(mt);
    if (!mb.visible) {
      mtInfo = "gizli";
    } else {
      // Quarto rewrites TOC hrefs to absolute URLs, so read the hash off the
      // end of whatever the link carries.
      var links = mt.getElementsByTagName("a");
      var closedH = mt.getBoundingClientRect().height;
      mt.open = true;
      var openH = mt.getBoundingClientRect().height;
      var broken = 0;
      Array.prototype.forEach.call(links, function (a) {
        var href = a.getAttribute("href") || "";
        var hash = href.slice(href.indexOf("#") + 1);
        var id = href.indexOf("#") < 0 ? "" : decodeURIComponent(hash);
        if (!id || !doc.getElementById(id)) broken++;
      });
      mt.open = false;
      mtInfo = "panel " + links.length + " baglanti, acilinca " + Math.round(closedH) +
               "->" + Math.round(openH) + "px" + (broken ? ", KIRIK " + broken : "");
    }
  }
  if (reach === "yok" || reach.indexOf("dugme") === 0) {
    if (mtInfo.indexOf("panel") === 0) reach = "mobil panel";
  }
  return {
    width, scrollW: de.scrollWidth, clientW: de.clientWidth, mobileToc: mtInfo,
    sidebar: box(q("#quarto-sidebar")),
    content: box(q("#quarto-document-content")),
    margin: box(q("#quarto-margin-sidebar")),
    toc: tocBox, tocReach: reach,
    columns: box(q(".page-columns")),
  };
}

async function run() {
  const out = [];
  for (const [page, w] of jobs) {
    const frame = document.createElement("iframe");
    frame.width = w; frame.height = 900; frame.src = "/" + page;
    document.body.appendChild(frame);
    await new Promise((res) => { frame.onload = res; setTimeout(res, 15000); });
    await new Promise((res) => setTimeout(res, 700));
    let m;
    try { m = measure(frame.contentDocument, frame.contentWindow, w); }
    catch (e) { m = {width: w, error: String(e).slice(0, 120)}; }
    m.page = page;
    out.push(m);
    frame.remove();
    new Image().src = "/__layout?d=" + encodeURIComponent(JSON.stringify(m));
    await new Promise((res) => setTimeout(res, 150));
  }
  new Image().src = "/__layout?done=" + out.length;
}
run();
</script>
"""


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def fmt_box(b):
    if not b:
        return "yok"
    if not b["visible"]:
        return "gizli(%s)" % b["display"]
    return "%d..%d (%d)" % (b["l"], b["r"], b["w"])


def main():
    argv = sys.argv[1:]
    widths = [390, 768, 1280, 1920, 2560]
    if "--widths" in argv:
        i = argv.index("--widths")
        widths = [int(x) for x in argv[i + 1].split(",")]
        del argv[i:i + 2]
    args = [a for a in argv if not a.startswith("--")]
    if not args:
        sys.exit(__doc__)

    port = free_port()
    log = tempfile.NamedTemporaryFile("w+", suffix=".log", delete=False, encoding="utf-8")
    server = subprocess.Popen([sys.executable, "-u", "-m", "http.server", str(port), "--bind", "127.0.0.1"],
                              cwd=SITE, stdout=log, stderr=subprocess.STDOUT)
    wrapper = SITE / "_layout-probe.html"
    try:
        time.sleep(1.2)
        wrapper.write_text(WRAPPER.replace("__PAGES__", json.dumps(args)).replace("__WIDTHS__", json.dumps(widths)),
                           encoding="utf-8")
        win = max(widths) + 60
        tmp = tempfile.mkdtemp()
        subprocess.run([CHROME, *FLAGS, "--window-size=%d,1200" % win,
                        "--virtual-time-budget=%d" % (20000 + 9000 * len(args) * len(widths)),
                        "--user-data-dir=" + tmp, "--screenshot=" + str(pathlib.Path(tmp) / "x.png"),
                        "http://127.0.0.1:%d/_layout-probe.html" % port],
                       capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=900)
        time.sleep(1.0)
        rows = []
        for line in pathlib.Path(log.name).read_text(encoding="utf-8", errors="replace").splitlines():
            m = re.search(r"GET /__layout\?d=(\S+) HTTP", line)
            if m:
                rows.append(json.loads(urllib.parse.unquote(m.group(1))))
    finally:
        server.kill()
        server.wait(timeout=10)
        log.close()
        wrapper.unlink(missing_ok=True)

    if not rows:
        print("OLCUM YOK (sayfa yuklenmedi mi?)")
        sys.exit(1)
    page = None
    bad = 0
    for r in rows:
        if r.get("page") != page:
            page = r["page"]
            print("\n== %s" % page)
            print("  %-6s %-11s %-18s %-22s %-18s %s" % ("genis", "tasma", "sol menu", "icerik (bosluk)", "sag icindekiler", "TOC"))
        if "error" in r:
            print("  %-6d HATA %s" % (r["width"], r["error"]))
            bad += 1
            continue
        overflow = r["scrollW"] - r["clientW"]
        gap_l = r["content"]["l"] if r["content"] else 0
        gap_r = (r["clientW"] - r["content"]["r"]) if r["content"] else 0
        print("  %-6d %-11s %-18s %-22s %-18s %s" % (
            r["width"],
            "yok" if overflow <= 1 else "VAR +%d" % overflow,
            fmt_box(r["sidebar"]),
            (fmt_box(r["content"]) + "  %d|%d" % (gap_l, gap_r)) if r["content"] else "yok",
            fmt_box(r["margin"]),
            r["tocReach"] + ("  [%s]" % r.get("mobileToc") if r.get("mobileToc", "yok") != "yok" else "")))
        if overflow > 1:
            bad += 1
    print("\nSONUC: %s" % ("SORUN VAR" if bad else "tasma yok"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
