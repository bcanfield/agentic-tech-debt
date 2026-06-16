#!/usr/bin/env python3
"""Build the human-prose baseline that fingerprint.py --vs-corpus compares against.

Pulls recent essays from the exemplar writers' feeds (the dry/concrete/first-person
set from docs/ai-writing-detection.md + the tone research), runs fingerprint.compute
on each, and writes per-metric p10/p50/p90 bands to human_baseline.json.

We store metrics and titles only — never the essay text — so this vendors nobody's
prose; the corpus is reproducible by re-running against the same feeds. Needs network
(feeds aren't in the sandbox allowlist), so run with the sandbox disabled.

Usage: python3 build_baseline.py
Extend FEEDS as the rotation grows. A feed that 403s or only ships excerpts just
contributes fewer docs; the run reports what it actually used.
"""
import html
import json
import os
import re
import statistics
import sys
import urllib.request

from fingerprint import compute

# (label, feed url). Full-text feeds preferred; excerpt-only feeds yield fewer docs.
FEEDS = [
    ("Dan Luu", "https://danluu.com/atom.xml"),
    ("Julia Evans", "https://jvns.ca/atom.xml"),
    ("Simon Willison", "https://simonwillison.net/atom/everything/"),
    ("Rachel by the Bay", "https://rachelbythebay.com/w/atom.xml"),
    ("Daniel Stenberg", "https://daniel.haxx.se/blog/feed/"),
    ("Joel Spolsky", "https://www.joelonsoftware.com/feed/"),
    # patio11/Matt Levine deliberately absent: their feeds ship excerpts or sit behind
    # a paywall, so we can't measure full essays. They stay rotation *reads* (the agent
    # WebFetches them live for the pairwise), not corpus sources.
]

MIN_WORDS = 250      # below this it's an excerpt/aside, not an essay
MAX_PER_FEED = 5     # cap so one prolific feed doesn't dominate the bands
UA = "Mozilla/5.0 (compatible; debt-ops-baseline/1.0; +https://github.com/bcanfield/agentic-tech-debt)"

ENTRY = re.compile(r"<(?:entry|item)\b.*?</(?:entry|item)>", re.S | re.I)
TITLE = re.compile(r"<title\b[^>]*>(.*?)</title>", re.S | re.I)
# content lives in different tags across Atom/RSS — grab them all, keep the longest
BODY = re.compile(r"<(?:content|summary|description|content:encoded)\b[^>]*>(.*?)</(?:content|summary|description|content:encoded)>", re.S | re.I)


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def untag(s):
    s = re.sub(r"<!\[CDATA\[(.*?)\]\]>", r"\1", s, flags=re.S)
    s = re.sub(r"(?is)<(script|style).*?</\1>", " ", s)
    s = html.unescape(s)                 # entities -> chars (handles double-escaped feeds)
    s = re.sub(r"(?is)<(script|style).*?</\1>", " ", s)  # again, in case unescape revealed tags
    s = re.sub(r"<[^>]+>", " ", s)        # strip remaining tags
    s = re.sub(r"\s+\n", "\n", s)
    return re.sub(r"[ \t]{2,}", " ", s).strip()


def entries(feed_xml):
    for block in ENTRY.findall(feed_xml):
        bodies = [untag(b) for b in BODY.findall(block)]
        body = max(bodies, key=len) if bodies else ""
        title_m = TITLE.search(block)
        title = untag(title_m.group(1)) if title_m else "(untitled)"
        yield title, body


def pct(values, p):
    if not values:
        return 0.0
    s = sorted(values)
    if len(s) == 1:
        return round(s[0], 2)
    k = (len(s) - 1) * p / 100
    lo = int(k)
    frac = k - lo
    hi = min(lo + 1, len(s) - 1)
    return round(s[lo] + (s[hi] - s[lo]) * frac, 2)


def main():
    docs = []
    used_sources = []
    for label, url in FEEDS:
        try:
            xml = fetch(url)
        except Exception as e:
            print(f"  skip {label}: {e}", file=sys.stderr)
            continue
        count = 0
        for title, body in entries(xml):
            if count >= MAX_PER_FEED:
                break
            if len(body.split()) < MIN_WORDS:
                continue
            m = compute(body)
            docs.append({"source": label, "title": title[:80], "metrics": m})
            count += 1
        print(f"  {label}: {count} essays", file=sys.stderr)
        if count:
            used_sources.append(label)

    if len(docs) < 8:
        sys.exit(f"only {len(docs)} essays gathered — too few for stable bands. "
                 "Check network / feed URLs and rerun.")

    keys = ["nominal_per_k", "participial_per_k", "passive_per_k", "hedge_per_k",
            "self_per_k", "punct_per_k", "sent_mean", "sent_stdev", "rhythm_stdev"]
    bands = {}
    for k in keys:
        vals = [d["metrics"][k] for d in docs]
        bands[k] = {"p10": pct(vals, 10), "p50": pct(vals, 50),
                    "p90": pct(vals, 90), "mean": round(statistics.mean(vals), 2)}

    out = {
        "_about": "Human-prose fingerprint bands. Built by build_baseline.py from real "
                  "essays. fingerprint.py --vs-corpus flags drafts outside p10-p90.",
        "n_docs": len(docs),
        "sources": used_sources,
        "metrics": bands,
        "docs": [{"source": d["source"], "title": d["title"],
                  "words": d["metrics"]["words"]} for d in docs],
    }
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "human_baseline.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nwrote {path}: {len(docs)} essays from {len(used_sources)} writers")


if __name__ == "__main__":
    main()
