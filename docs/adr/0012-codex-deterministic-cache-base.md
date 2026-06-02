# 0012 — Codex adapter uses one deterministic cache base

**Date:** 2026-06-01
**Status:** Accepted

## Context

The hooks and the skills must agree on one per-repo cache dir — it holds the registry-dir pointer, the turn-batch letter file `drop` reads, the metrics log, and the feedback command list. In the Claude adapter the hook subprocess gets `CLAUDE_PLUGIN_DATA` but the skill Bash env does not, so the skills *glob* the known plugin-data dir to rediscover it (ADR 0006/0009). Codex sets a `PLUGIN_DATA` for hooks too, but its on-disk location for a given repo isn't a stable, documented contract the skill side can reliably reconstruct — and the install path (`~/.codex/plugins/cache/$MARKETPLACE/$PLUGIN/$VERSION/`) is version-scoped, so it moves on every upgrade.

## Decision

Resolve the cache from one deterministic base in **both** contexts: `~/.cache/debt-ops/cache/<repo-hash>`, overridable with a single `DEBT_OPS_CACHE` env var. `<repo-hash>` is `sha1(repo-toplevel)[:12]`, computed identically in Python (`hashlib`) and skill Bash (`shasum`). The hook subprocess and the skill Bash env compute the same path with no globbing and no dependence on `PLUGIN_DATA`.

## What this means for you

- State survives plugin upgrades — the cache isn't under the version-scoped install dir.
- One override knob: set `DEBT_OPS_CACHE` to relocate it (CI, sandboxes, read-only homes).
- The cache lives outside the plugin install tree, so uninstalling the plugin leaves the per-repo cache behind; it's cheap throwaway state (regenerated next session).

## Alternatives we ruled out

- **Honor `PLUGIN_DATA` like the Claude adapter does.** Hooks would write where Codex points, but the skills can't see that env var and can't reliably glob a version-scoped, undocumented path — so hooks and skills would silently diverge (entries land in one dir, `drop` reads another). Determinism beats using the managed dir.
- **Glob `~/.codex/plugins/cache/*/debt-ops/*/`.** Brittle: matches multiple installed versions, breaks on the next upgrade, and still guesses at a path Codex doesn't promise.

## When to revisit

- Codex documents a stable, skill-reachable per-repo data dir (an env var both hooks and skills receive). Then prefer the managed dir and drop the dotfile base.
- Users report cache collisions across repos that share a toplevel path — revisit the hash input.
