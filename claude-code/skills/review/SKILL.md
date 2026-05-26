---
name: review
description: Use when the user invokes /debt-ops:review. Audit the debt registry — drop hotspot files that no longer exist as stale, deprioritize files unchanged in 90+ days, rank the rest by churn × Fowler quadrant — and surface a top-3 paydown list. Stale entries get letter codes so the user can drop them with `drop A,B,C` (ADR 0007).
allowed-tools: Bash(python3 *)
---

# /debt-ops:review — audit + triage the registry

Call `review.py` via Bash. The helper does all the deterministic work: it reads every entry under the cached `registry-dir`, audits each one against Git, ranks the survivors, writes letter codes for stale entries to `current-turn.txt` (so the existing `drop A,B` UX from ADR 0004 keeps working), and prints a three-bucket report.

**Then re-emit the helper's stdout verbatim as your response text, inside a fenced code block.** Claude Code collapses long bash outputs behind a `+N lines, ctrl+o to expand` placeholder, so if you don't print the report yourself, the user never sees it. Copy the stdout exactly — no preamble, no summary, no follow-up suggestions. The fenced code block preserves the monospace alignment of the columns.

## The call

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/review.py
```

Optional: `--top N` to surface more than the default 3 paydown candidates.

## What the helper does

For each registry entry it reads:

- **Audit (deterministic, Git-as-oracle).** Does the `hotspot:` path still exist in the working tree? How many commits have touched it since the entry's `created:` date?
- **Classify.** File missing → `stale`. File exists but unchanged in 90+ days → `cold`. Otherwise → `active`.
- **Rank active entries.** Score = churn × quadrant weight (reckless-inadvertent 3, reckless-deliberate / prudent-inadvertent 2, prudent-deliberate 1) + 2 if `ai_authored: true` + 1 if older than 30 days. Top N are surfaced; the rest are summarized as a count.
- **Wire the drop UX.** Stale entries get letters appended to `current-turn.txt` so the user's next prompt can be `drop A,B,C` and the existing `drop.py` hook handles it without a Claude turn.

## Why this shape

The marker-presence check ("does this file still have TODO/FIXME?") was deliberately cut — most registry entries describe architectural deferrals, not in-code markers, and dogfood on slack-agent showed 100% false-stale flagging with that signal in. The honest staleness signal is hotspot-file-missing; everything else stays active and the user decides.

## Don't

- Don't ask the user to confirm before running. The helper is read-only on the registry except for the letter mapping; nothing is deleted until the user types `drop`.
- Don't paraphrase, reformat, or summarize the helper's stdout. Copy it exactly into the fenced code block. The report's column alignment and letter codes only work if reproduced verbatim.
- Don't suggest follow-ups inline ("want me to fix the top one?"). The user picks the next move; your job ends when the report is on screen.
