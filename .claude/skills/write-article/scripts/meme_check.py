#!/usr/bin/env python3
"""Gate the article's visuals: enough of them, well-spaced, exactly one meme.

Three deterministic contracts the prose audit can't enforce by eye:

  1. MEME — the body references exactly one `*.meme.*` image and the file exists.
     (Cover lives in frontmatter, not the body, so it never counts here.)
  2. ANCHORS — at least three committed body images total, one of them a diagram
     (`*.diagram.*`) and one the meme. The third is a free anchor (stat-card, a
     second diagram, a before/after) — the article just has to carry three.
  3. SPACING — no more than two consecutive prose paragraphs without a visual
     break between them. A break is a committed image, a fenced code block, a
     table, a blockquote, or a heading. Prose-heavy shapes (incident/data/essay)
     have nothing but images to break a run, so the rule lands as "an image every
     two paragraphs" there; playbooks lean on their native code/tables.

The fix for a too-long prose run is a rendered image that carries content the
prose doesn't — or cutting the prose until the run closes. Never decoration.

This is the floor, not the verdict — "is the meme any good", "does this image
earn its place" is the fresh-agent review's job.

Usage: python3 meme_check.py <article.md>
Exit status: 1 if any contract fails (so it can gate a publish step), else 0.
"""
import re
import sys
from os.path import join, dirname, exists

# Longest allowed run of consecutive prose paragraphs with no visual between them.
MAX_PROSE_RUN = 2
# Minimum committed body images (diagram + meme + one more).
MIN_IMAGES = 3

IMAGE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
IMAGE_ONLY = re.compile(r"^!\[[^\]]*\]\([^)]*\)$")
HEADING = re.compile(r"^#{1,6}\s")
TABLE_SEP = re.compile(r"^\s*\|?[\s:|-]*-[\s:|-]*$")


def split_frontmatter(raw):
    # returns body_start_char — body is everything after the closing --- fence
    if raw.startswith("---"):
        end = raw.find("\n---", 3)
        if end != -1:
            return raw.find("\n", end + 1) + 1
    return 0


def classify(body):
    """Walk the body into blocks tagged 'prose' or 'break', with body line numbers."""
    lines = body.split("\n")
    blocks = []  # (kind, start_line_idx)  kind in {'prose','break'}
    i, n = 0, len(lines)
    while i < n:
        s = lines[i].strip()
        if s == "":
            i += 1
            continue
        if s.startswith("```"):  # fenced code block — one break
            j = i + 1
            while j < n and not lines[j].strip().startswith("```"):
                j += 1
            blocks.append(("break", i))
            i = j + 1
            continue
        if HEADING.match(s) or IMAGE_ONLY.match(s):  # heading / standalone image — break
            blocks.append(("break", i))
            i += 1
            continue
        if s.startswith(">"):  # blockquote — break
            blocks.append(("break", i))
            while i < n and lines[i].strip().startswith(">"):
                i += 1
            continue
        if "|" in s and i + 1 < n and TABLE_SEP.match(lines[i + 1]):  # table — break
            blocks.append(("break", i))
            i += 2
            while i < n and "|" in lines[i]:
                i += 1
            continue
        # otherwise a prose paragraph: consume to the next blank/special line
        blocks.append(("prose", i))
        i += 1
        while i < n and lines[i].strip() != "" and not lines[i].strip().startswith(("```", ">")) \
                and not HEADING.match(lines[i].strip()) and not IMAGE_ONLY.match(lines[i].strip()):
            i += 1
    return blocks


def check(path):
    raw = open(path, encoding="utf-8").read()
    body_start = split_frontmatter(raw)
    body = raw[body_start:]
    base_line = raw[:body_start].count("\n")  # body line k → raw line base_line + k + 1
    fails = []
    print(f"\n== {path}")

    # 1. MEME — exactly one meme ref, file present
    refs = [m.group(1) for m in IMAGE.finditer(body)]
    meme_refs = [r for r in refs if ".meme." in r]
    if len(meme_refs) != 1:
        fails.append(f"found {len(meme_refs)} `*.meme.*` refs in body; need exactly 1")
    else:
        name = meme_refs[0].lstrip("/").split("/")[-1]
        if not exists(join(dirname(path) or ".", name)):
            fails.append(f"meme ref `{name}` has no file next to the article")

    # 2. ANCHORS — >=3 committed images, at least one diagram
    if len(refs) < MIN_IMAGES:
        fails.append(f"{len(refs)} committed body image(s); need >= {MIN_IMAGES} "
                     f"(diagram + meme + one more)")
    if not any(".diagram." in r for r in refs):
        fails.append("no `*.diagram.*` ref in body; the mandatory diagram is missing")

    # 3. SPACING — no run of more than MAX_PROSE_RUN consecutive prose paragraphs
    run, run_start = 0, None
    for kind, ln in classify(body):
        if kind == "prose":
            if run == 0:
                run_start = ln
            run += 1
            if run > MAX_PROSE_RUN:
                fails.append(
                    f"{run} prose paragraphs in a row with no visual, "
                    f"starting L{base_line + run_start + 1} — break it with a rendered "
                    f"image (or cut prose until the run closes)"
                )
                run = 0  # report each over-long run once
        else:
            run = 0

    if not fails:
        print("  ok — one meme, >=3 images, no prose run over two paragraphs.")
        return 0
    for f in fails:
        print(f"  FAIL  {f}")
    return 1


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    rc = 0
    for f in sys.argv[1:]:
        rc |= check(f)
    sys.exit(rc)
