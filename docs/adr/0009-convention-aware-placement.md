# 0009 — Convention-aware, co-located placement for new ADR/registry dirs

**Date:** 2026-05-27
**Status:** Accepted

## Context

ADR 0006 made the plugin *detect* where ADRs and the registry already live, but its probes only fire on directories that already exist *with content*. On a greenfield repo — the common first-use case — both probes miss and the code falls to hardcoded defaults `doc/adr` and `debt/registry`. Two problems follow: the plugin ignores an existing documentation convention (a repo with `docs/` still gets a brand-new singular `doc/`), and ADRs and debt land in two separate top-level folders. This repo is the evidence — it carries both `docs/` and `doc/adr/`.

## Decision

Treat ADRs and the registry as two artifacts under one **documentation home**, and decide greenfield placement the same two-tier way ADR 0006 established for detection:

- **Existing-content probe (Python, unchanged).** If a populated ADR or registry dir exists, use it. Finding existing files is determinism, so it stays in Python.
- **Greenfield → Claude decides (SessionStart inject).** When either dir is absent, the inject states the convention as fact — co-locate both under one home, reuse an existing `docs/`/`documentation/`/`doc/` home when present, default to `docs/adr` + `docs/debt` — and Claude writes the resolved repo-relative path(s) to `<cache>/adr-dir` / `<cache>/registry-dir`. If one dir is already detected, the inject tells Claude to place the other beside it.

Choosing a home that fits an arbitrary repo is judgment a fixed probe does worse than the agent reading the repo, so it stays out of Python. The default changes from `doc/adr` + `debt/registry` (two top-level dirs) to `docs/adr` + `docs/debt` (one home). The cache contract (two hand-editable files) and the chokepoint (`session-start.py`) are unchanged; every consumer keeps reading the cache, so their hardcoded fallback constants move to the new defaults too.

## What this means for you

- A repo with an existing `docs/` gets `docs/adr` + `docs/debt`, not a new `doc/`. Nothing is created until Claude first writes an ADR or registry entry.
- Repos that already have a populated `doc/adr` or `debt/registry` keep them — the existing-content probe wins, so nothing relocates. (This repo keeps `doc/adr`.)
- For new repos the split default is gone: ADRs and debt share one home.
- Override as before by hand-editing `<cache>/adr-dir` or `<cache>/registry-dir`.

## Alternatives we ruled out

- **Extend the Python probe with a docs-home detector + co-location derivation ladder.** A candidate-list walk plus a most-markdown tiebreak re-implements judgment the agent does better, and the project rule is to guide Claude with markdown, not script decisions a smart agent can make. The inject handles arbitrary layouts for free.
- **A config file / `userConfig` key for the paths.** Already rejected in ADR 0006 — the plugin adapts, not asks. The current Claude Code docs confirm there is no path-config primitive and that the data-dir cache (hand-editable) is the intended override.
- **Keep the split default, only co-locate when a docs home exists.** Contradicts the goal — the ask is that the two share a home *by default*, diverging only when conventions say otherwise.
- **Migrate existing split layouts into the new home.** Relocating established dirs surprises users and breaks links; the probe deliberately leaves them in place.

## When to revisit

- If Claude routinely picks odd homes on greenfield repos, tighten the inject wording or add a verification round-trip (next SessionStart checks the cached path is co-located and re-injects if not).
- If users keep hand-editing the cache to undo co-location, the default is wrong — reconsider.
- If a third detected resource appears, generalize the cache read/write + placement inject rather than copy-pasting.
