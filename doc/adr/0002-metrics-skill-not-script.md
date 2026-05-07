# 0002 — `/debt-ops:metrics` is a skill, not a Python script

**Date:** 2026-05-07
**Status:** Accepted

## Context

The dogfood metrics need an aggregator: something that reads `metrics.jsonl`, filters to the last 7 days, computes the four tripwires, and prints a verdict. The fork: should Claude do the parsing and math (a thin skill prompt), or should we ship a Python script that aggregates on disk and the skill just runs it?

## Decision

The skill does the work itself. `claude-code/skills/metrics/SKILL.md` tells Claude where the file is, what the JSON shape means, what to compute, and how to format the output — and trusts Claude to handle the JSON parsing, date filtering, and arithmetic. No Python aggregator script.

## What this means for you

- Running `/debt-ops:metrics` costs a small amount of LLM tokens (Claude reads ~500 lines and reasons about them). For a once-a-day glance during dogfood, that's pennies.
- You can ask follow-up questions in chat — "what about just the last 2 days?" — and Claude will redo the math from the same data. A script would have required new flags.
- If we ever want this metric on a CI cron (no LLM involved), we'd add the script later. Today it's not needed.

## Alternatives we ruled out

- **Python aggregator script** (`scripts/metrics.py` + a thin skill that calls it). ~200 lines vs ~50, deterministic and fast, but rigid: no follow-up questions, no flexible time windows without flags, more code to maintain. Token cost saved doesn't pay for the rigidity at this scale.

## When to revisit

- If the metric runs frequently enough (e.g., on a cron, in CI, hundreds of times a day) that token cost matters, write the script.
- If `metrics.jsonl` grows past ~10k lines and `tail -n 500` starts losing useful data, write the script (it can stream the whole file efficiently).
- If Claude's arithmetic on the JSON ever produces visibly wrong numbers in dogfood, write the script.
