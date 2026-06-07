#!/usr/bin/env python3
"""Count the instruction-tuning fingerprint features in a markdown article.

Approximations of the PNAS 2025 (Reinhart et al.) Biber features plus rhythm and
stance proxies from docs/ai-writing-detection.md. Counts only — interpretation is
the reviewer's job. Each metric is tagged with the direction AI text skews.

Usage: python3 fingerprint.py <article.md> [more.md ...]
"""
import re
import statistics
import sys

# nominalization suffixes (len>6 filters "nation", "city"-class false positives)
NOMINAL = re.compile(r"\b\w{4,}(?:tion|sion|ment|ness|ity|ance|ence)s?\b", re.I)
# mid-sentence participial attachment: ", making it easier" / ", leading to"
PARTICIPIAL = re.compile(r",\s+(?:\w+ly\s+)?\w+ing\b")
# passive: be-verb + past participle; "agentless" = no "by" within the next few words
PASSIVE = re.compile(r"\b(?:is|are|was|were|been|being|be)\s+(?:\w+ly\s+)?(\w+(?:ed|en))\b", re.I)
HEDGES = re.compile(r"\b(?:maybe|probably|perhaps|seems?|roughly|i think|i suspect|i'm not sure|might|sort of|kind of)\b", re.I)
SELF = re.compile(r"\b(?:i|i'm|i've|i'd|my|me)\b", re.I)
STOP = set("the a an and or but of to in on for with as at by from is are was were be been it this that these those its it's".split())


def strip_markdown(text):
    # drop code blocks/inline code so tool output doesn't pollute prose stats
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    text = re.sub(r"`[^`]*`", "", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)  # keep link text
    text = re.sub(r"^#+ .*$", "", text, flags=re.M)        # drop headings
    return text


def sentences(text):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if len(s.split()) >= 3]


def analyze(path):
    text = strip_markdown(open(path, encoding="utf-8").read())
    words = re.findall(r"\b[\w']+\b", text)
    n = len(words)
    per_k = lambda c: round(c * 1000 / n, 1) if n else 0.0

    sents = sentences(text)
    lens = [len(s.split()) for s in sents]
    # second-order rhythm proxy: how much consecutive sentence-length *changes* vary
    deltas = [abs(a - b) for a, b in zip(lens, lens[1:])]

    passives = PASSIVE.findall(text)
    agentless = len(re.findall(PASSIVE.pattern + r"(?!\s+(?:\w+\s+){0,3}by\b)", text, re.I))

    paras = [p for p in text.split("\n\n") if len(p.split()) > 30]
    # worst within-paragraph content-word repetition
    rep = 0
    for p in paras:
        counts = {}
        for w in re.findall(r"\b\w{5,}\b", p.lower()):
            if w not in STOP:
                counts[w] = counts.get(w, 0) + 1
        if counts:
            rep = max(rep, max(counts.values()))

    print(f"\n== {path}  ({n} words, {len(sents)} sentences, {len(paras)} paragraphs)")
    rows = [
        ("nominalizations /1k        (AI-high, 2.1x)", per_k(len(NOMINAL.findall(text)))),
        ("participial clauses /1k    (AI-high, 5.3x)", per_k(len(PARTICIPIAL.findall(text)))),
        ("agentless passives /1k     (AI-LOW, ~0.5x)", per_k(agentless)),
        ("hedges /1k                 (AI-low)", per_k(len(HEDGES.findall(text)))),
        ("self-mention /1k           (AI-low)", per_k(len(SELF.findall(text)))),
        ("expressive punct (!?) /1k  (AI-low)", per_k(text.count("!") + text.count("?"))),
        ("sentence len mean/stdev    (AI: low stdev)", f"{statistics.mean(lens):.1f} / {statistics.stdev(lens):.1f}" if len(lens) > 1 else "n/a"),
        ("rhythm: stdev of deltas    (AI: low)", f"{statistics.stdev(deltas):.1f}" if len(deltas) > 1 else "n/a"),
        ("paragraph words stdev      (AI: uniform)", f"{statistics.stdev([len(p.split()) for p in paras]):.0f}" if len(paras) > 1 else "n/a"),
        ("max in-para word repeats   (AI-high)", rep),
    ]
    for label, val in rows:
        print(f"  {label:<46} {val}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    for f in sys.argv[1:]:
        analyze(f)
