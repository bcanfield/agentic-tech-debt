#!/usr/bin/env python3
"""Count the instruction-tuning fingerprint features in a markdown article.

Approximations of the PNAS 2025 (Reinhart et al.) Biber features plus rhythm and
stance proxies from docs/ai-writing-detection.md. Counts only — interpretation is
the reviewer's job. Each metric is tagged with the direction AI text skews.

Two modes:
  python3 fingerprint.py <article.md> [more.md ...]      # print raw rates
  python3 fingerprint.py --vs-corpus <article.md>        # compare to human bands

--vs-corpus loads human_baseline.json (built by build_baseline.py from real essays
by the writers in docs/ai-writing-detection.md's exemplar set) and flags every
metric where the draft falls outside the human p10–p90 band. Inside the band proves
nothing on its own; outside it — in the AI-risk direction — is a reliable fail.
"""
import json
import os
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

# metrics compared against the human corpus, with the direction AI text skews.
# "high" = AI runs hotter than humans (flag when draft > p90).
# "low"  = AI runs colder than humans (flag when draft < p10).
COMPARE = {
    "nominal_per_k": "high",
    "participial_per_k": "high",
    "passive_per_k": "low",
    "hedge_per_k": "low",
    "self_per_k": "low",
    "punct_per_k": "low",
    "sent_stdev": "low",
    "rhythm_stdev": "low",
    "sent_mean": "either",
}

BASELINE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "human_baseline.json")


def strip_markdown(text):
    # drop code blocks/inline code so tool output doesn't pollute prose stats
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    text = re.sub(r"`[^`]*`", "", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)  # keep link text
    text = re.sub(r"^#+ .*$", "", text, flags=re.M)        # drop headings
    return text


def sentences(text):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if len(s.split()) >= 3]


def compute(text):
    """Return the numeric fingerprint metrics for a block of plain text."""
    words = re.findall(r"\b[\w']+\b", text)
    n = len(words)
    per_k = lambda c: round(c * 1000 / n, 1) if n else 0.0

    sents = sentences(text)
    lens = [len(s.split()) for s in sents]
    deltas = [abs(a - b) for a, b in zip(lens, lens[1:])]
    agentless = len(re.findall(PASSIVE.pattern + r"(?!\s+(?:\w+\s+){0,3}by\b)", text, re.I))

    paras = [p for p in text.split("\n\n") if len(p.split()) > 30]
    rep = 0
    for p in paras:
        counts = {}
        for w in re.findall(r"\b\w{5,}\b", p.lower()):
            if w not in STOP:
                counts[w] = counts.get(w, 0) + 1
        if counts:
            rep = max(rep, max(counts.values()))

    return {
        "words": n,
        "sentences": len(sents),
        "paragraphs": len(paras),
        "nominal_per_k": per_k(len(NOMINAL.findall(text))),
        "participial_per_k": per_k(len(PARTICIPIAL.findall(text))),
        "passive_per_k": per_k(agentless),
        "hedge_per_k": per_k(len(HEDGES.findall(text))),
        "self_per_k": per_k(len(SELF.findall(text))),
        "punct_per_k": per_k(text.count("!") + text.count("?")),
        "sent_mean": round(statistics.mean(lens), 1) if lens else 0.0,
        "sent_stdev": round(statistics.stdev(lens), 1) if len(lens) > 1 else 0.0,
        "rhythm_stdev": round(statistics.stdev(deltas), 1) if len(deltas) > 1 else 0.0,
        "para_stdev": round(statistics.stdev([len(p.split()) for p in paras]), 0) if len(paras) > 1 else 0.0,
        "max_rep": rep,
    }


def print_report(path):
    m = compute(strip_markdown(open(path, encoding="utf-8").read()))
    print(f"\n== {path}  ({m['words']} words, {m['sentences']} sentences, {m['paragraphs']} paragraphs)")
    rows = [
        ("nominalizations /1k        (AI-high, 2.1x)", m["nominal_per_k"]),
        ("participial clauses /1k    (AI-high, 5.3x)", m["participial_per_k"]),
        ("agentless passives /1k     (AI-LOW, ~0.5x)", m["passive_per_k"]),
        ("hedges /1k                 (AI-low)", m["hedge_per_k"]),
        ("self-mention /1k           (AI-low)", m["self_per_k"]),
        ("expressive punct (!?) /1k  (AI-low)", m["punct_per_k"]),
        ("sentence len mean/stdev    (AI: low stdev)", f"{m['sent_mean']} / {m['sent_stdev']}"),
        ("rhythm: stdev of deltas    (AI: low)", m["rhythm_stdev"]),
        ("paragraph words stdev      (AI: uniform)", f"{m['para_stdev']:.0f}"),
        ("max in-para word repeats   (AI-high)", m["max_rep"]),
    ]
    for label, val in rows:
        print(f"  {label:<46} {val}")


def compare_corpus(path):
    if not os.path.exists(BASELINE):
        sys.exit(f"no baseline at {BASELINE} — run build_baseline.py first.")
    base = json.load(open(BASELINE))
    bands = base["metrics"]
    m = compute(strip_markdown(open(path, encoding="utf-8").read()))

    print(f"\n== {path}  vs human corpus ({base['n_docs']} docs, {len(base['sources'])} writers)")
    flags = 0
    for key, direction in COMPARE.items():
        if key not in bands:
            continue
        lo, hi = bands[key]["p10"], bands[key]["p90"]
        val = m[key]
        verdict = "ok"
        if val < lo:
            verdict = "LOW " + ("(AI-risk)" if direction in ("low", "either") else "")
        elif val > hi:
            verdict = "HIGH " + ("(AI-risk)" if direction in ("high", "either") else "")
        risky = "AI-risk" in verdict
        flags += risky
        mark = "  <-- " if risky else "      "
        print(f"{mark}{key:<20} draft {val:<7} human p10–p90 [{lo}, {hi}]  med {bands[key]['p50']}  {verdict.strip()}")

    print(f"\n  {flags} metric(s) outside the human band in the AI direction.")
    print("  In-band proves nothing; out-of-band (AI-risk) is a reliable fail. Still run the agent review.")
    return 1 if flags else 0


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    if args[0] == "--vs-corpus":
        targets = args[1:]
        if not targets:
            sys.exit(__doc__)
        rc = 0
        for f in targets:
            rc |= compare_corpus(f)
        sys.exit(rc)
    for f in args:
        print_report(f)
