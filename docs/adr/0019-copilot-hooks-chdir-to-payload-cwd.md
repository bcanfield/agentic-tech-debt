# 0019 — Copilot hooks must chdir to the payload `cwd`, not trust process cwd

**Date:** 2026-06-03
**Status:** Accepted

## Context

The Copilot adapter's three hooks (`session-start.py`, `feedback.py`, `stop.py`)
located the repo with `git rev-parse --show-toplevel` in the **process cwd**. That
works on Claude Code and Codex — both invoke hooks with cwd = the user's project —
but it is silently broken on GitHub Copilot CLI.

Empirically (Copilot CLI v1.0.59, probe inserted into the installed hook), Copilot
runs plugin hooks with **cwd = the plugin install dir**
(`~/.copilot/installed-plugins/.../debt-ops`), which is not a git repo. So
`git_toplevel()` returned `None` and every hook idled — no cache, no `metrics.jsonl`,
no write-time feedback. It failed invisibly because the hooks swallow exceptions and
`exit 0`. The whole Copilot write-time loop was dead, even though skills installed
fine and `${PLUGIN_ROOT}` expanded correctly (both confirmed — the token resolves and
env vars propagate; only cwd was wrong).

Captured payloads show every Copilot hook **does** receive the real project path as a
top-level `cwd` field (camelCase, absolute):

- `sessionStart`: `{sessionId, timestamp, cwd, source, initialPrompt}`
- `postToolUse`: `{sessionId, timestamp, cwd, toolName, toolArgs, toolResult}`
- `agentStop`: `{sessionId, timestamp, cwd, stopReason, transcriptPath}`

## Decision

Each Copilot hook reads its stdin payload first and `os.chdir(data["cwd"])` before any
git call. A small `chdir_to_payload_cwd` helper does this (no-op if `cwd` is missing or
unusable, so we degrade to the old process-cwd behavior rather than crash).

- `feedback.py`: moved `read_stdin()` above the `git_toplevel()` check, then chdir.
- `stop.py`: already parsed the payload first; just added the chdir.
- `session-start.py`: previously ignored stdin entirely; now reads it solely to get
  `cwd`, then chdirs.

This is a **Copilot-only delta** — Claude/Codex hooks are left untouched because they
already run in the project dir (Claude verified live; Codex verified writing its cache).
Do **not** propagate the helper to the claude/codex/portable copies.

## Consequences

- The Copilot write-time loop works: a real `copilot -p` edit now writes the
  `session` / `edit` / `feedback` metrics and runs the charter's quality commands
  (verified end-to-end, not just unit-tested).
- New per-adapter delta to preserve when syncing these three scripts (recorded in
  CLAUDE.md): the `chdir_to_payload_cwd` helper + the payload-first ordering live only
  in `copilot/hooks/`.
- `session-start.py` now reads stdin on Copilot. The payload is always present in
  practice; the read is guarded and the hook has a `timeoutSec` bound.

## Alternatives we ruled out

- **Set `cwd` in the `hooks.json` entry.** Copilot's hook schema has a `cwd` field, but
  it's a static string written at package time — it cannot be the user's project dir,
  which is only known at runtime. Useless here.
- **`git -C <cwd>` on every subprocess call instead of `os.chdir`.** More surgical, but
  it would touch every git invocation in `stop.py` (which already threads `cwd=toplevel`
  through its helpers). A single chdir at the top of `main()` is smaller and the
  downstream `cwd=toplevel` calls keep working unchanged. chdir is safe in a
  short-lived, single-purpose hook process.
- **Apply the chdir to all four adapters for uniformity.** Rejected: Claude and Codex
  work today; changing their reference hooks adds regression risk for no gain and
  violates "stay in scope." Kept as a documented Copilot delta instead.

## Payoff trigger

Revisit if Copilot CLI changes to invoke plugin hooks with cwd = the project (making
the chdir a harmless no-op we could drop), or if the `_common.py` extraction (ADR 0011)
ever lands — at which point the cwd shim becomes the per-adapter I/O boundary.
