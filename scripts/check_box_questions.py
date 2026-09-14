# -*- coding: utf-8 -*-
"""List example/exercise boxes that hold more than one question.

Usage:  python scripts/check_box_questions.py <file.qmd> [...]

Every example and exercise box of the lecture notes must hold exactly one
question; a multi-part exercise is split into one box per part.

A "question" is a lettered or roman sub-part written as **(a)**, **(b)** ...,
- **(a)** ..., (a\\) ..., or a numbered 1\\. / 2\\. item inside an exm-/exr- box.
Exit status 1 when any box holds two or more questions.
"""
import io
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

OPEN = re.compile(r'^(:{3,})\s*\{#((?:exm|exr)-[a-z0-9-]+)([^}]*)\}\s*$')
NAME = re.compile(r'name="([^"]*)"')
PARTS = [
    re.compile(r"\*\*\((?:[a-h]|i|ii|iii|iv|v|vi)\)\*\*"),
    re.compile(r"\*\*\((?:[a-h])\\\)\*\*"),
    re.compile(r"^\s*[-*]\s+\*\*\(?[a-h]\\?\)", re.M),
    re.compile(r"^\(?[a-h]\\\)\s", re.M),
    re.compile(r"^\s*\*\*[a-h]\)\*\*", re.M),
]

bad = 0
for path in sys.argv[1:]:
    lines = io.open(path, encoding="utf-8").read().split("\n")
    total = multi = 0
    for i, line in enumerate(lines):
        m = OPEN.match(line)
        if not m:
            continue
        depth = len(m.group(1))
        close = re.compile(r"^:{%d}\s*$" % depth)
        j = i + 1
        while j < len(lines) and not close.match(lines[j]):
            j += 1
        body = "\n".join(lines[i + 1:j])
        # count the question parts before the solution block only
        head = body.split("::: {.cozum}")[0].split("::: {.ispat}")[0]
        n = max(len(p.findall(head)) for p in PARTS)
        total += 1
        if n >= 2:
            multi += 1
            nm = NAME.search(m.group(3))
            print("  %s:%d  %s  [%s]  soru=%d" % (path.split("\\")[-1].split("/")[-1], i + 1,
                                                 m.group(2), nm.group(1) if nm else "", n))
    print("%s: kutu=%d, birden cok soru iceren=%d" % (path, total, multi))
    bad += multi
sys.exit(1 if bad else 0)
