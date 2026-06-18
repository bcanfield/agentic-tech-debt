#!/usr/bin/env python3
"""Gate the article's meme: exactly one, and the visuals break up the wall evenly.

Two deterministic contracts the prose audit can't enforce by eye:

  1. COUNT — the body references exactly one `*.meme.*` image and the file exists.
     (Cover lives in frontmatter, not the body, so it never counts here.)
  2. PLACEMENT — the meme is the one movable visual, so it should land in the
     biggest empty stretch, not clumped against the diagram or a code block.
     We flag the longest unbroken prose run and any two visuals sitting too close.

This is the floor, not the verdict — "is the meme any good" is the fresh-agent
review's job. A clean run here just means it's present and well-spaced.

Usage: python3 meme_check.py <article.md>
Exit status: 1 if any contract fails (so it can gate a publish step), else 0.
"""
import re
import sys

# Longest unbroken prose run, as a fraction of total body prose. Over this and the
# wall isn't broken — move the meme into that stretch.
MAX_GAP_FRAC = 0.40
# Two visuals closer than this (prose words between them) read as clumped.
MIN_ADJ_WORDS = 80

FENCE = re.compile(r"```.*?```", re.S)
IMAGE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")


def split_frontmatter(raw):
    # returns (body_start_char) — body is everything after the closing --- fence
    if raw.startswith("---"):
        end = raw.find("\n---", 3)
        if end != -1:
            return raw.find("\n", end + 1) + 1
    return 0


def words(text):
    return len(re.findall(r"\S+", text))


def lineno(raw, offset):
    return raw[:offset].count("\n") + 1


def check(path):
    raw = open(path, encoding="utf-8").read()
    body_start = split_frontmatter(raw)
    body = raw[body_start:]
    fails = []
    print(f"\n== {path}")

    # 1. COUNT — exactly one meme ref, file present
    meme_refs = [m for m in IMAGE.finditer(body) if ".meme." in m.group(1)]
    if len(meme_refs) != 1:
        fails.append(f"found {len(meme_refs)} `*.meme.*` refs in body; need exactly 1")
    else:
        ref = meme_refs[0].group(1).lstrip("/").split("/")[-1]
        from os.path import join, dirname, exists
        if not exists(join(dirname(path) or ".", ref)):
            fails.append(f"meme ref `{ref}` has no file next to the article")

    # 2. PLACEMENT — collect visual spans (fences + body images) as (start, end, is_meme)
    spans = [(body_start + m.start(), body_start + m.end(), False) for m in FENCE.finditer(body)]
    for m in IMAGE.finditer(body):
        s = body_start + m.start()
        if not any(lo <= s < hi for lo, hi, _ in spans):  # skip images inside a fence
            spans.append((s, body_start + m.end(), ".meme." in m.group(1)))
    spans.sort()

    if spans:
        # prose gaps between visuals (and head/tail), each tagged with its borders
        gaps = [(body_start, spans[0][0], False)]
        for (_, prev_end, pm), (next_start, _, nm) in zip(spans, spans[1:]):
            gaps.append((prev_end, next_start, pm or nm))  # 3rd field: meme borders this gap
        gaps.append((spans[-1][1], len(raw), False))

        prose_total = sum(words(raw[a:b]) for a, b, _ in gaps) or 1
        biggest = max(gaps, key=lambda g: words(raw[g[0]:g[1]]))
        big_w = words(raw[biggest[0]:biggest[1]])
        if big_w / prose_total > MAX_GAP_FRAC:
            fails.append(
                f"longest prose run is {big_w}w ({big_w/prose_total:.0%} of body), "
                f"L{lineno(raw, biggest[0])}–L{lineno(raw, biggest[1])} — "
                f"move the meme into it"
            )
        # adjacency only matters for the MOVABLE visual — don't police content-anchored
        # code blocks (e.g. a registry example next to the install-command CTA).
        for a, b, meme_borders in gaps[1:-1]:
            if meme_borders and words(raw[a:b]) < MIN_ADJ_WORDS:
                fails.append(
                    f"meme is only {words(raw[a:b])}w from the next visual near "
                    f"L{lineno(raw, a)} — move it into open prose"
                )

    if not fails:
        print("  ok — exactly one meme, visuals evenly spaced.")
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
