# 0006 — Adaptive ADR and registry path detection

**Date:** 2026-05-14
**Status:** Accepted

## Context

The plugin hardcoded `doc/adr/` and `debt/registry/` in five places: `session-start.py` (metrics counting + Discipline 2 prose), `stop.py` (marker-scan exclusion + entries count), `feedback.py` (registry growth metric), `register.py` (write target), and `drop.py` (delete target). A real dogfood signal exposed the cost: in `slack-agent`, the user kept ADRs under `docs/adr/` (plural). The metrics reported 0 ADRs (looking in the wrong dir), and any TODO/FIXME mentions inside those ADR files would have been counted as fresh deferrals (the exclusion missed them). The same fragility applied to any non-default registry layout.

A config file was the obvious fix and the user explicitly rejected it — they want the plugin to *adapt*, not to ask. The plugin already has the right pattern for adaptive detection: `session-start.py` asks Claude to detect quality commands silently on first session and write the result to a cache file the other hooks read. Same shape works for paths.

## Decision

Two-tier detection in `session-start.py`, with results cached per-repo under `$CLAUDE_PLUGIN_DATA/cache/<repo-hash>/`:

- **Tier 1 — cheap Python probe.** Walk a small list of known conventions (`doc/adr`, `docs/adr`, `adr`, `architecture/decisions`, etc. for ADRs; `debt/registry`, `tech-debt/registry`, `registry` for the registry). A directory counts as a hit when it contains at least one markdown file whose name matches `^\d+[-_].*\.md` (Nygard numbered-prefix convention) for ADRs, or any `.md` file for the registry. On a hit, write the repo-relative path to `<cache>/adr-dir` or `<cache>/registry-dir`.
- **Tier 2 — Claude semantic fallback.** If the ADR probe finds nothing, the SessionStart inject appends a silent instruction asking Claude to scan the repo for ADR-shaped markdown (numbered filenames or Nygard sections — `## Status`, `## Context`, `## Decision`, `## Consequences`) and write the path itself. Same pattern as the existing quality-commands first-session detection. Defaults to `doc/adr` if Claude finds nothing.
- **Cache invalidation.** `read_cached_dir` re-checks that the cached path still resolves to a real directory; if not, the tier-1 probe runs again. The cache is automatically refreshed when the directory is moved.

The detected paths feed five places: metrics counting (correct ADR/registry counts in `metrics.jsonl`), the disciplines text injected into Claude's context (Discipline 2 names the right destination for new ADRs; Discipline 3 names the right registry to consult), the marker-scan exclusion in `stop.py` (no false positives from TODO mentions inside ADR prose), entry registration in `register.py`, and entry deletion in `drop.py`.

## What this means for you

- `docs/adr/` works without any config change. So does `architecture/decisions/`, `adrs/`, or `tech-debt/registry/`.
- If you keep ADRs somewhere truly novel (`/poop/my-adrs`), first session asks Claude to find it silently; subsequent sessions read the cached path with no overhead.
- The Discipline 2 reminder injected at SessionStart now names the *actual* path for your repo, so new ADRs land in the right place.
- Metrics finally count what's there — the "0 ADRs alongside +60 registry entries" anomaly in `/debt-ops:metrics` was an artifact of the hardcoded path, not a genuine Discipline 2 failure.
- If you ever need to override, you can hand-edit `<cache>/adr-dir` or `<cache>/registry-dir` — the cache file is the source of truth, no plugin re-release needed.

## Alternatives we ruled out

- **Config file (`.debt-ops` or `plugin.json` user-config).** User-facing dial that turns the plugin into a thing-to-tweak rather than a thing-that-just-works. Explicitly rejected — the value of debt-ops is that it's auto-pilot; a config file moves it back toward manual.
- **Regex-and-filesystem-walk only (my first plan).** Brittle in two directions: the regex misses ADR shapes the convention doesn't anticipate (`A001-...md`, `RFC-001-...md`), and a deep filesystem walk on large monorepos costs real time on every SessionStart. The tier-2 Claude fallback handles arbitrary shapes for free and only runs when the cheap probe misses — best of both.
- **Glob-only autodiscovery (no Claude in the loop).** Equivalent to tier-1 only with a more permissive pattern. Same failure mode for non-standard layouts — and the existing first-session pattern for quality commands already proved the Claude-fallback shape works, so reusing it costs us nothing in complexity.
- **Per-hook re-detection.** Skip the cache; let every hook fire run the probe. Adds repeated filesystem cost to every PostToolUse and Stop. The cache write at SessionStart is the natural amortization point.

## When to revisit

- If the tier-1 probe routinely misses common cases that *aren't* in the candidate list, expand the list — the cost of a longer probe is bounded (each candidate is one `is_dir()` call).
- If Claude's tier-2 detection routinely writes wrong paths, tighten the instruction wording or add a verification round-trip on the next SessionStart (check that the cached path actually contains ADR-shaped files; if not, re-detect).
- If we add a third detected resource (e.g., a tests directory), generalize the cache read/write into a shared helper rather than copy-pasting the `read_cached_dir` pattern in every script.
- If we ever ship a `userConfig` block for unrelated reasons, reconsider whether `adr_dir` / `registry_dir` belong there as opt-in overrides — but only after the adaptive path proves insufficient for at least one real user.
