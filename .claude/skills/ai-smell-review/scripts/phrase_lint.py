#!/usr/bin/env python3
"""Flag the cheap, deterministic surface tells in a markdown article.

The literal layer that fingerprint.py (stats) and the smell-review agent (judgment)
don't cover: em-dash density, AI typography, the documented LLM vocabulary, and a
few regex-able structure tells (negative parallelism, rhetorical-reveal fragments).

Per docs/ai-writing-detection.md, surface vocabulary is the single largest expert
cue (53.1%) — but it's also the first thing a humanize pass scrubs. So this is a
pre-filter, not a verdict: a HIT is worth fixing, a clean run means nothing on its
own. Still run fingerprint.py and the agent review.

Lists are data at the top — extend them as new tells get through.

Usage: python3 phrase_lint.py <article.md> [more.md ...]
Exit status: 1 if any hit fires (so it can gate a publish step), else 0.
"""
import re
import sys

# Words that read AI on sight. Kept tight on purpose — a 200-word dragnet trains
# people to ignore the output. Grounded in the documented instruct-model lexicon.
AI_WORDS = [
    "delve", "delves", "delving", "tapestry", "realm", "boasts", "boast",
    "seamless", "seamlessly", "robust", "leverage", "leverages", "leveraging",
    "underscore", "underscores", "underscoring", "pivotal", "intricate",
    "intricacies", "meticulous", "meticulously", "multifaceted", "holistic",
    "plethora", "myriad", "garner", "garners", "showcase", "showcases",
    "spearhead", "facilitate", "utilize", "utilizes", "utilizing", "commendable",
    "noteworthy", "vibrant", "bustling", "embark", "foster", "fostering",
    "harness", "harnessing", "unlock", "unlocks", "elevate", "elevates",
    "paradigm", "synergy", "testament",
]

# Connective adverbs models over-deploy. Softer signal (legit in moderation),
# so reported as low severity and only flagged when piled up.
AI_CONNECTIVES = [
    "moreover", "furthermore", "additionally", "consequently", "notably",
    "importantly", "ultimately", "essentially", "fundamentally",
]

# (regex, why) — multi-word phrases and structure tells.
PHRASES = [
    (r"\bit'?s not (just )?\w[\w ]{0,30}?,?\s+it'?s\b", "negative parallelism ('it's not X, it's Y')"),
    (r"\bnot only\b[\w ,]{0,40}?\bbut also\b", "'not only ... but also' parallelism"),
    (r"\bit'?s (important|worth) (to note|noting)\b", "filler hedge ('it's worth noting')"),
    (r"\bneedless to say\b", "filler phrase"),
    (r"\bwhen it comes to\b", "filler transition"),
    (r"\bat the end of the day\b", "cliché"),
    (r"\bin today'?s\b[\w ]{0,20}?\b(world|landscape|era|age)\b", "'in today's ... world' opener"),
    (r"\bin the (world|realm|landscape) of\b", "'in the realm of' framing"),
    (r"\ba testament to\b", "'a testament to'"),
    (r"\bplays? a (key|crucial|vital|pivotal|critical|significant) role\b", "'plays a key role'"),
    (r"\bstands? as a\b", "'stands as a'"),
    (r"\bnavigat(e|ing) the (complex|complexit|landscape|world|challeng)", "figurative 'navigate the complexities'"),
    (r"\bthe (result|catch|problem|kicker|twist|reality|truth)\?\s", "rhetorical-reveal fragment ('The result?')"),
    (r"\bever-(evolving|changing|growing|increasing)\b", "'ever-evolving' intensifier"),
    (r"\bgame[- ]chang(er|ing)\b", "'game-changer'"),
    (r"\bcutting[- ]edge\b", "'cutting-edge'"),
    (r"\bdeep dive\b", "'deep dive' (verify it's not the literal Amazon-memo quote)"),
]

# Always-block typography: a keyboard doesn't produce these, a word processor or
# model does. (Em-dashes are handled separately — they're threshold-based, not
# always-block, since the humanize rule allows up to 2 per piece.)
TYPO = [
    ("–", "en-dash"),
    ("“", "curly double quote"),
    ("”", "curly double quote"),
    ("‘", "curly single quote"),
    ("’", "curly apostrophe"),
    ("…", "ellipsis character (…) instead of ..."),
]

CODE_BLOCK = re.compile(r"```.*?```", re.S)


def code_spans(text):
    # line ranges inside fenced blocks — tool output / install commands aren't prose
    spans = []
    for m in CODE_BLOCK.finditer(text):
        spans.append((text[: m.start()].count("\n"), text[: m.end()].count("\n")))
    return spans


def in_code(lineno, spans):
    return any(lo <= lineno <= hi for lo, hi in spans)


def lint(path):
    raw = open(path, encoding="utf-8").read()
    spans = code_spans(raw)
    lines = raw.splitlines()
    hits = []          # (severity, lineno, label, snippet)
    emdash = 0

    for i, line in enumerate(lines, 1):
        # Typography is scanned everywhere — a reader sees an em-dash in an ASCII
        # diagram too, so fenced blocks don't get a pass here. (Word/phrase tells
        # below are prose-only; they'd misfire on code.)
        emdash += line.count("—")  # threshold-based, reported in summary only
        for ch, why in TYPO:
            for _ in range(line.count(ch)):
                hits.append(("typo", i, why, line.strip()[:90]))

        if in_code(i, spans):
            continue
        low = line.lower()

        for w in AI_WORDS:
            if re.search(rf"\b{re.escape(w)}\b", low):
                hits.append(("word", i, f"AI word: '{w}'", line.strip()[:90]))
        for w in AI_CONNECTIVES:
            if re.search(rf"\b{re.escape(w)}\b", low):
                hits.append(("soft", i, f"connective: '{w}'", line.strip()[:90]))

        for pat, why in PHRASES:
            if re.search(pat, low):
                hits.append(("phrase", i, why, line.strip()[:90]))

    # report
    print(f"\n== {path}")
    if not hits and emdash <= 2:
        print("  clean (no surface tells) — but a clean pass proves nothing; run the agent review.")
        return 0

    order = {"phrase": 0, "word": 1, "typo": 2, "soft": 3}
    for sev, lineno, label, snippet in sorted(hits, key=lambda h: (order[h[0]], h[1])):
        print(f"  L{lineno:<4} [{sev:6}] {label}")
        print(f"         | {snippet}")

    if emdash:
        verdict = "TELL" if emdash > 2 else "ok-ish"
        print(f"\n  em-dashes: {emdash} ({verdict}; humanize rule is 2 max per piece)")

    blocking = [h for h in hits if h[0] != "soft"] or emdash > 2
    print(f"  {len(hits)} hit(s); {'FAIL — fix before publishing' if blocking else 'soft only'}")
    return 1 if blocking else 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    rc = 0
    for f in sys.argv[1:]:
        rc |= lint(f)
    sys.exit(rc)
