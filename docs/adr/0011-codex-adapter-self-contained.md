# 0011 — Codex adapter ships as a self-contained sibling plugin

**Date:** 2026-06-01
**Status:** Accepted

## Context

debt-ops now targets a second agent. Codex CLI exposes a deliberately Claude-Code-compatible plugin system — `.codex-plugin/plugin.json`, `hooks/hooks.json` with the same event names (`SessionStart`, `UserPromptSubmit`, `PostToolUse`, `Stop`), `skills/*/SKILL.md`, and even `CLAUDE_PLUGIN_ROOT`/`CLAUDE_PLUGIN_DATA` env aliases. The six Python helpers are ~90% identical to the Claude versions; only a handful of behaviors differ (charter file, the file-edit tool, skill-invocation syntax). The question was how to share the common logic.

## Decision

Ship the Codex adapter as a fully self-contained plugin under `codex/`, a sibling of `claude-code/`, with its own copy of the scripts and skills. Each adapter is independently installable and travels as one unit. The released `claude-code/` plugin is left untouched (in scope: add an adapter, not refactor the existing one).

## What this means for you

- Install either adapter on its own: `/plugin install` for Claude, the Codex marketplace at `.agents/plugins/marketplace.json` for Codex. Neither depends on files outside its own directory.
- A change to shared logic (e.g. the registry schema) must be applied to both adapters' copies (`claude-code/scripts/` and, on the Codex side, `codex/hooks/` + `codex/skills/<skill>/scripts/`). That duplication is logged as a debt entry with a payoff trigger (a third adapter).

## Alternatives we ruled out

- **Extract a shared `scripts/common/` both adapters import.** Codex installs each plugin into an isolated cache dir (`~/.codex/plugins/cache/.../$VERSION/`), and Claude does the same — a shared parent dir doesn't travel with an installed plugin without a build/vendoring step. It also means editing the already-released Claude plugin, which is out of scope. The coupling cost outweighs the ~900 saved lines at two adapters.
- **A runtime package dependency (pip/npm).** Violates the stdlib-only, zero-dependency constraint the hooks rely on to run anywhere Python 3.10+ exists.

## When to revisit

- A **third** adapter lands. At three copies the duplication tax crosses the line; extract a vendored `_common.py` copied into each plugin at build/release time (keeps install-time self-containment, kills the hand-sync). This is the registered debt entry's payoff trigger.
- The two script sets drift in a way that causes a real bug (e.g. a schema fix applied to one and not the other). That's the signal the manual sync has failed.
