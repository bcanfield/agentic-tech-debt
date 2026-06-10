# 0020 — Disable debt-ops per-repo via a cache sentinel, not a repo file

**Date:** 2026-06-10
**Status:** Accepted

## Context

There was no way to turn debt-ops off for a single repo. The hooks fire on
every session, edit, and stop, and the only escape was uninstalling the plugin
globally — too blunt when you want it on everywhere except one repo (a vendored
tree, a throwaway spike, a repo whose owner just doesn't want it).

We needed an on/off switch that is per-repo, easy to flip, and survives across
sessions. The open question was *where the off-state lives*.

## Decision

Store the disable flag as a sentinel file `disabled` inside the plugin's
existing per-repo cache dir (`<cache>/cache/<repo_hash>/disabled`) — the same
place `registry-dir`, `feedback.list`, and the turn batch already live. Every
hook already resolves `git_toplevel()` → `cache_dir`; we add one
`repo_disabled(cache_dir)` check right there and idle silently if the sentinel
exists (the same clean exit as "not a git repo").

Flipping it is the `/debt-ops:disable` skill (`$debt-ops-disable` on
non-Claude), backed by a small `toggle.py` that resolves the cache the same way
`register.py` does and creates or removes the sentinel, printing the resulting
state. Run it again to re-enable. The skill never auto-invokes — it only runs
on explicit request.

## What this means for you

- Disable a repo: run `/debt-ops:disable` (Claude) / `$debt-ops-disable`
  (Codex/Copilot/portable). Run it again to re-enable. The hooks go quiet
  immediately — no session inject, no write-time feedback, no stop nudge.
- Nothing is written to your working tree. The flag lives in the plugin's
  cache, so it never shows up in `git status` or a diff.
- Because the cache is per-machine, the off-state is **per developer machine**,
  not shared with the team. Each person who wants it off in a repo flips it
  themselves. (See the trade-off below.)
- The explicitly-invoked skills still work while disabled — disabling targets
  the automatic hook behaviors, which is what's intrusive.

## Alternatives we ruled out

- **A committed repo file** (`.debt-ops-disabled`, a config key). Would make the
  decision team-wide and version-controlled, but it puts a file in the user's
  tree — the one thing we were asked to avoid. The cache sentinel keeps the
  working tree clean at the cost of being per-machine.
- **An env var** (`DEBT_OPS_DISABLE=1`). Easy, but it's per-shell, not
  per-repo, and not persistent — you'd forget it's set. It doesn't answer "off
  for *this repo*."
- **Claude Code's native per-project plugin disable** (`.claude/settings.json`).
  Claude-only (not Codex/Copilot/portable) and still a committed repo file.

## When to revisit

If users ask for a *shared*, team-wide per-repo disable, add a committed-file
mechanism alongside this one (the hook check can honor either) — at that point
the working-tree-cleanliness trade-off is worth reopening.
