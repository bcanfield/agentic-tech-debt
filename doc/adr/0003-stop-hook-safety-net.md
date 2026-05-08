# 0003 — Stop hook as Discipline 1 safety net

**Date:** 2026-05-08
**Status:** Accepted

## Context

v1 deliberately cut the Stop hook on the bet that the SessionStart "additionalContext" inject (Discipline 1) would be enough to get Claude to register deferrals. Four days of dogfood in `mediamtx-connect` produced **0 registry entries across 69 edits** including architecturally interesting changes (`instrumentation.ts`, a new API route, `env.ts` ×4). The pattern: Claude reads the inject once at session start, then under context pressure on long turns in repos with dense in-repo `CLAUDE.md` rules, the discipline gets crowded out and forgotten.

## Decision

Add a `Stop` hook (`claude-code/scripts/stop.py`) that fires at the end of every turn. It scans `git diff HEAD` plus untracked files for newly-added `TODO`/`FIXME`/`HACK`/`XXX` marker lines, compares to new entries under `debt/registry/`, and emits an `additionalContext` nudge on Claude's next turn if there's a delta. Tripwire, not precision instrument: paths under `debt/registry/` and `doc/adr/` are excluded; false positives cost a "drop it" reply, false negatives defeat the point.

## What this means for you

- The plugin now nudges Claude **every turn**, not just at session start. Long sessions in dense-rules repos no longer lose the discipline.
- You don't need to run `/debt-ops:init` per-repo to make Discipline 1 fire reliably — the safety net works without modifying any `CLAUDE.md`.
- Expect occasional false-positive nudges (e.g., literal `TODO` strings in test fixtures, in plugin source code that mentions the regex itself, in docs that list marker names). Reply "drop it" to clear spurious registry entries.

## Alternatives we ruled out

- **Strengthen the SessionStart inject only.** Tighter wording would help marginally but wouldn't fix the root issue: any one-shot inject loses weight under long-context pressure. Same failure mode we just observed.
- **Write disciplines into `~/.claude/CLAUDE.md` globally.** Research across Anthropic's official plugins showed only two write to `CLAUDE.md` and both require explicit user invocation. Plugin-driven `CLAUDE.md` modification is against the grain of the platform's conventions.
- **Make the Stop hook blocking** (`decision: "block"`). More forceful but interrupts Claude mid-flow on what may be a false positive. Start observational; promote to blocking only if dogfood shows the nudge is routinely ignored.

## When to revisit

- If false-positive rate is annoying (>1 spurious nudge per session in normal use), narrow the marker regex or add path-based exclusions for `tests/`, `docs/`, generated files, etc.
- If the nudge fires but Claude routinely ignores it (visible as a new "markers stayed unregistered turn-over-turn" tripwire in `metrics.jsonl`), promote to `decision: "block"` so Claude must register before the turn ends.
- If broader deferral patterns (`as any`, `@ts-ignore`, `// later`, swallowed exceptions) start showing up in dogfood as common un-registered debt, extend the sniff beyond markers — or accept that those rely on Discipline 1's session-start inject only.
