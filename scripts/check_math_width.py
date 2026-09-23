# -*- coding: utf-8 -*-
"""Estimate how wide every formula renders and report the ones that overflow a phone.

MathJax typesets in the browser, so the rendered width of a formula cannot be
measured from the sources directly. This script approximates it: it walks the
LaTeX of each formula and adds up per-glyph widths in `em` units (the same unit
MathJax works in), handling fractions, scripts, roots, delimiters, spacing
commands and the alignment environments.

The budget is the width available to a formula on a 360 px phone, expressed in
em of the body text (1 em = 17.6 px at the site's font-size: 1.1em):

    plain paragraph        ~16.5 em
    inside a theorem box   ~14.5 em   (the box adds padding on both sides)

Display formulas are allowed to be wider: styles/global.css turns every
display formula into its own horizontal scroll container, so a wide one costs
the reader a swipe but never widens the page. Inline formulas cannot scroll on
their own -- an inline formula wider than the text column pushes the whole page
sideways, which is the defect this script exists to prevent.

Usage:
    python scripts/check_math_width.py                    # whole site
    python scripts/check_math_width.py olasilik-teorisi   # one course
    python scripts/check_math_width.py --all              # list every finding
    python scripts/check_math_width.py --json out.json
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

ROOT = pathlib.Path(__file__).resolve().parent.parent
COURSES = ROOT / "dersler"

# Width budgets in em (see the module docstring).
INLINE_BUDGET = 16.5
INLINE_BOX_BUDGET = 14.5
# A display formula scrolls, but past this width the swipe is long enough that
# the formula should be split over several lines with `aligned` instead.
DISPLAY_BUDGET = 34.0

# ---------------------------------------------------------------------------
# width model
# ---------------------------------------------------------------------------
# Average advance widths of the MathJax (TeX) fonts, in em. Italic math letters
# are narrower than upright text; digits are tabular at 0.5.
CHAR_W = {
    " ": 0.0, "\n": 0.0, "\t": 0.0,
    "i": 0.30, "j": 0.32, "l": 0.30, "f": 0.35, "t": 0.39, "r": 0.39,
    "I": 0.44, "J": 0.47,
    "m": 0.88, "w": 0.72, "M": 0.90, "W": 0.94,
    "(": 0.39, ")": 0.39, "[": 0.28, "]": 0.28, "|": 0.28, "/": 0.50,
    ",": 0.28, ".": 0.28, ";": 0.28, ":": 0.28, "!": 0.28,
    "'": 0.28, "?": 0.47,
}
DIGIT_W = 0.50
LETTER_W = 0.55
# Binary operators and relations carry MathJax's own spacing on both sides.
BINARY_W = {"+": 0.78 + 0.44, "-": 0.78 + 0.44, "*": 0.50 + 0.44}
RELATION_W = {"=": 0.78 + 0.56, "<": 0.78 + 0.56, ">": 0.78 + 0.56}

# Named commands: width of the symbol they produce, including its own spacing.
CMD_W = {
    # relations
    "le": 1.34, "leq": 1.34, "ge": 1.34, "geq": 1.34, "ne": 1.34, "neq": 1.34,
    "equiv": 1.34, "approx": 1.34, "sim": 1.34, "simeq": 1.34, "cong": 1.34,
    "subset": 1.34, "subseteq": 1.34, "supset": 1.34, "supseteq": 1.34,
    "in": 1.11, "notin": 1.11, "ni": 1.11, "mid": 0.28, "to": 1.44, "mapsto": 1.44,
    "Rightarrow": 1.56, "Leftarrow": 1.56, "Leftrightarrow": 1.83, "iff": 1.83,
    "rightarrow": 1.44, "leftarrow": 1.44, "longrightarrow": 1.94,
    # binary operators
    "pm": 1.22, "mp": 1.22, "times": 1.22, "div": 1.22, "cdot": 0.76,
    "cup": 1.22, "cap": 1.22, "setminus": 1.22, "wedge": 1.22, "vee": 1.22,
    "circ": 0.76, "oplus": 1.22, "otimes": 1.22, "ast": 0.94,
    # large operators (the operator glyph itself; limits are measured separately)
    "sum": 1.44, "prod": 1.44, "int": 0.94, "iint": 1.60, "oint": 1.06,
    "bigcup": 1.44, "bigcap": 1.44, "lim": 1.44, "max": 1.50, "min": 1.44,
    "sup": 1.33, "inf": 1.22, "log": 1.44, "ln": 1.06, "exp": 1.61,
    "sin": 1.33, "cos": 1.50, "tan": 1.50, "arctan": 2.61, "arcsin": 2.44,
    "det": 1.44, "dim": 1.61, "deg": 1.50, "gcd": 1.61, "operatorname": 0.0,
    # letters and symbols
    "alpha": 0.64, "beta": 0.56, "gamma": 0.58, "delta": 0.50, "epsilon": 0.47,
    "varepsilon": 0.47, "theta": 0.51, "lambda": 0.58, "mu": 0.61, "nu": 0.57,
    "pi": 0.57, "rho": 0.52, "sigma": 0.60, "tau": 0.52, "phi": 0.64,
    "varphi": 0.64, "chi": 0.61, "psi": 0.68, "omega": 0.69,
    "Gamma": 0.63, "Delta": 0.83, "Theta": 0.79, "Lambda": 0.69, "Sigma": 0.73,
    "Phi": 0.76, "Psi": 0.79, "Omega": 0.79,
    "infty": 0.98, "partial": 0.55, "nabla": 0.83, "emptyset": 0.78,
    "varnothing": 0.78, "ldots": 1.17, "cdots": 1.17, "dots": 1.17, "vdots": 0.28,
    "blacksquare": 0.72, "star": 0.78, "angle": 0.78, "perp": 0.78,
    "prime": 0.28, "circledast": 1.22,
    # spacing
    "quad": 1.0, "qquad": 2.0, ",": 0.17, ";": 0.28, ":": 0.22, "!": -0.17,
    " ": 0.33, "enspace": 0.5, "hspace": 0.0,
    # invisible / structural
    "left": 0.0, "right": 0.0, "big": 0.1, "Big": 0.15, "bigg": 0.2, "Bigg": 0.25,
    "displaystyle": 0.0, "textstyle": 0.0, "limits": 0.0, "nolimits": 0.0,
    "label": 0.0, "notag": 0.0, "\\": 0.0,
}
# One-argument wrappers whose argument keeps (roughly) its own width.
SAME_WIDTH = {"mathbf", "mathrm", "mathbb", "mathcal", "mathscr", "mathfrak",
              "boldsymbol", "bm", "hat", "bar", "tilde", "vec", "overline",
              "underline", "widehat", "widetilde", "left", "right", "phantom"}
DELIMS = {"(": 0.39, ")": 0.39, "[": 0.28, "]": 0.28, "\\{": 0.50, "\\}": 0.50,
          "|": 0.28, "\\|": 0.56, "\\langle": 0.39, "\\rangle": 0.39}


def _read_group(s: str, i: int):
    """If s[i] opens a brace group, return (content, index after it)."""
    if i >= len(s) or s[i] != "{":
        # a single token argument: \frac12 or \hat x
        if i < len(s) and s[i] == "\\":
            m = re.match(r"\\[A-Za-z]+", s[i:])
            if m:
                return m.group(0), i + m.end()
        if i < len(s):
            return s[i], i + 1
        return "", i
    depth, j = 0, i
    while j < len(s):
        if s[j] == "{" and (j == i or s[j - 1] != "\\"):
            depth += 1
        elif s[j] == "}" and s[j - 1] != "\\":
            depth -= 1
            if depth == 0:
                return s[i + 1:j], j + 1
        j += 1
    return s[i + 1:], len(s)


def width(tex: str, scale: float = 1.0) -> float:
    """Approximate rendered width of a LaTeX fragment, in em."""
    tex = tex.strip()
    if not tex:
        return 0.0
    # environments: aligned / cases / matrices -- width is the widest row
    m = re.search(r"\\begin\{(aligned|align|array|cases|[bpvV]?matrix|split|gathered)\*?\}(.*?)"
                  r"\\end\{\1\*?\}", tex, re.S)
    if m:
        before = tex[:m.start()]
        after = tex[m.end():]
        body = m.group(2)
        if m.group(1) == "array":
            body = re.sub(r"^\s*\{[^{}]*\}", "", body)
        rows = re.split(r"\\\\", body)
        inner = max((sum(width(c, scale) for c in row.split("&")) for row in rows), default=0.0)
        if m.group(1) in ("cases",):
            inner += 1.0
        elif m.group(1) in ("bmatrix", "pmatrix", "vmatrix", "Vmatrix", "matrix"):
            inner += 1.0
        return width(before, scale) + inner + width(after, scale)

    total = 0.0
    i = 0
    n = len(tex)
    while i < n:
        ch = tex[i]
        if ch == "\\":
            m = re.match(r"\\([A-Za-z]+|.)", tex[i:])
            if not m:
                i += 1
                continue
            name = m.group(1)
            i += m.end()
            if name == "frac" or name == "dfrac" or name == "tfrac" or name == "binom":
                a, i = _read_group(tex, i)
                b, i = _read_group(tex, i)
                sub = scale if name != "tfrac" else scale * 0.85
                total += max(width(a, sub), width(b, sub)) + 0.30 * scale
                continue
            if name == "sqrt":
                if i < n and tex[i] == "[":
                    j = tex.find("]", i)
                    i = j + 1 if j >= 0 else i
                a, i = _read_group(tex, i)
                total += width(a, scale) + 0.9 * scale
                continue
            if name in ("text", "textrm", "textbf", "textit", "operatorname", "mbox"):
                a, i = _read_group(tex, i)
                total += (0.5 * len(a) + 0.4) * scale
                continue
            if name in SAME_WIDTH:
                a, i = _read_group(tex, i)
                total += width(a, scale)
                continue
            if name in CMD_W:
                total += CMD_W[name] * scale
                continue
            # unknown command: assume a single medium glyph
            total += 0.6 * scale
            continue
        if ch in "^_":
            i += 1
            a, i = _read_group(tex, i)
            total += width(a, scale * 0.72)
            continue
        if ch == "{" or ch == "}":
            i += 1
            continue
        if ch.isdigit():
            total += DIGIT_W * scale
        elif ch in BINARY_W:
            total += BINARY_W[ch] * scale
        elif ch in RELATION_W:
            total += RELATION_W[ch] * scale
        elif ch in CHAR_W:
            total += CHAR_W[ch] * scale
        elif ch.isalpha():
            total += LETTER_W * scale
        else:
            total += 0.55 * scale
        i += 1
    return total


# ---------------------------------------------------------------------------
# source scanning
# ---------------------------------------------------------------------------
FENCE = re.compile(r"^(```|~~~)")
BOX_OPEN = re.compile(r"^(:{3,})\s*\{(.*)\}\s*$")
BOX_CLOSE = re.compile(r"^(:{3,})\s*$")
DISPLAY = re.compile(r"\$\$(.+?)\$\$", re.S)
INLINE = re.compile(r"(?<!\$)\$(?!\$)((?:[^$\\]|\\.)+?)\$(?!\$)", re.S)


ENVIRONMENT = re.compile(r"\\(?:begin|end)\{[a-zA-Z*]+\}(?:\{[^}]*\})?")
ROW_BREAK = re.compile(r"\\\\(?:\[[^\]]*\])?")


def display_width(tex: str) -> float:
    """Width of a display formula: its widest row, not the sum of its rows."""
    rows = ROW_BREAK.split(ENVIRONMENT.sub(" ", tex))
    return max((width(r.replace("&", " ")) for r in rows if r.strip()), default=0.0)


def scan_file(path: pathlib.Path):
    """Yield findings: (line, kind, width_em, budget, formula)."""
    text = path.read_text(encoding="utf-8")
    lines = text.split("\n")
    in_fence = False
    in_yaml = lines and lines[0].strip() == "---"
    depth = 0
    out = []
    buf = []          # display math spanning several lines
    buf_start = 0
    for n, line in enumerate(lines, 1):
        if in_yaml:
            if n > 1 and line.strip() == "---":
                in_yaml = False
            continue
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if BOX_OPEN.match(line):
            depth += 1
            continue
        if BOX_CLOSE.match(line):
            depth = max(0, depth - 1)
            continue
        stripped = line.strip()
        if buf:
            if stripped.endswith("$$") or stripped == "$$":
                buf.append(stripped[:-2] if stripped.endswith("$$") else "")
                out.append((buf_start, "display", display_width("\n".join(buf)), DISPLAY_BUDGET,
                            " ".join(x.strip() for x in buf if x.strip())))
                buf = []
            else:
                buf.append(line)
            continue
        # A block opens on a line that starts with $$ and does not close on
        # it; a bare "$$" line both starts and ends with $$, so test it first.
        if stripped == "$$" or (stripped.startswith("$$") and not stripped.endswith("$$")):
            buf = [stripped[2:]]
            buf_start = n
            continue
        for m in DISPLAY.finditer(line):
            out.append((n, "display", display_width(m.group(1)), DISPLAY_BUDGET, m.group(1).strip()))
        rest = DISPLAY.sub(" ", line)
        for m in INLINE.finditer(rest):
            budget = INLINE_BOX_BUDGET if depth else INLINE_BUDGET
            out.append((n, "inline", width(m.group(1)), budget, m.group(1).strip()))
    return out


def shown(path: pathlib.Path) -> str:
    """Repository-relative path when possible, the full path for drafts elsewhere."""
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("course", nargs="?", help="course directory under dersler/")
    ap.add_argument("--all", action="store_true", help="list every finding, not just the worst")
    ap.add_argument("--json", help="write the findings to a JSON file")
    ap.add_argument("--limit", type=int, default=25, help="how many findings to print per kind")
    args = ap.parse_args()

    # a course name under dersler/, or any directory or single .qmd file (drafts outside the repo)
    base = (COURSES / args.course) if args.course else COURSES
    files = [base] if base.is_file() else sorted(base.rglob("*.qmd"))
    findings = []
    counts = {"inline": 0, "display": 0}
    for f in files:
        for line, kind, w, budget, tex in scan_file(f):
            counts[kind] += 1
            if w > budget:
                findings.append({"file": shown(f), "line": line,
                                 "kind": kind, "em": round(w, 1), "budget": budget,
                                 "tex": tex[:200]})

    findings.sort(key=lambda d: d["em"] - d["budget"], reverse=True)
    inline = [d for d in findings if d["kind"] == "inline"]
    display = [d for d in findings if d["kind"] == "display"]
    print("dosya: %d  satir ici formul: %d  goruntu formulu: %d"
          % (len(files), counts["inline"], counts["display"]))
    print("butceyi asan: satir ici %d (sayfayi genisletir), goruntu %d (kaydirilir)"
          % (len(inline), len(display)))
    for kind, items in (("SATIR ICI", inline), ("GORUNTU", display)):
        if not items:
            continue
        print("\n== %s ==" % kind)
        for d in (items if args.all else items[:args.limit]):
            print("  %s:%d  %.1fem (butce %.1f)  %s"
                  % (d["file"], d["line"], d["em"], d["budget"], d["tex"][:90]))
        if not args.all and len(items) > args.limit:
            print("  ... %d tane daha" % (len(items) - args.limit))
    if args.json:
        pathlib.Path(args.json).write_text(json.dumps(findings, ensure_ascii=False, indent=1),
                                           encoding="utf-8")
        print("\njson:", args.json)
    return 0


if __name__ == "__main__":
    sys.exit(main())
