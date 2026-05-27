# 0001 — Dogfood metrics are tripwires, not precise instruments

**Date:** 2026-05-07
**Status:** Accepted

## Context

We're adding the v1 dogfood instrumentation (Phase A). The question came up: should the metrics try to detect *specifically what slipped through* — e.g., regex-match TODO/FIXME/HACK/XXX markers Claude wrote without registering — or just count coarse signals like "edits per session" and "registry growth"?

## Decision

Coarse signals only. Each metric is a **tripwire**: a binary "is something off over a week" check, not a precise per-incident detector. The `metrics.jsonl` log holds a few simple facts per edit (file, registry count, pass/fail) — that's it.

## What this means for you

- The plugin writes 1–2 short lines to a hidden log file per edit. Nothing in your repo, no chat noise, no slowdown.
- A future `/debt-ops:metrics` command will report trends ("registrations are keeping pace with edits — looks healthy") rather than specific events ("at 3:42pm Claude wrote a TODO without registering").
- If a tripwire trips after the dogfood week, we add precision *then*. Not before.

## Alternatives we ruled out

- **Regex-based marker detection** (`TODO|FIXME|HACK|XXX` in diffs). Narrow: catches only one of the five deferral types Discipline 1 covers (markers), misses loosened types, stubs, "later" comments, and unmade decisions. Gives false confidence — a clean number that quietly excludes most of the actual risk.
- **Agent self-reporting** (Claude scans its own session at SessionStart and logs deferrals). If the agent could reliably detect its own drift, it would just register the entry. Self-reporting biases the metric exactly the wrong direction.

## When to revisit

After the v1 dogfood week (≥2026-05-14):
- If any tripwire trips reliably (e.g., FAIL→PASS rate <50%, or registry growth ≪ edit volume), we add the precise detection v2 needs.
- If everything looks healthy, this decision stays — coarse is enough, precision is unearned complexity.
