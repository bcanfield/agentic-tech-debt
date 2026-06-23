# 0020 — Cursor is a full hook adapter, not skills-only

**Date:** 2026-06-18
**Status:** Accepted

## Context

The packaging plan ([ADR 0013](./0013-portable-agent-skills-layer.md), and the
per-tool table in `docs/agent-skill-packaging-plan.md`) put Cursor in the
**skills + degraded mode** bucket — "weak/none or non-portable" hooks — so the
write-time differentiator couldn't port and Cursor only got the model-invoked
skills. The early launch plan even locked "Multi-tool: YES … **Not Cursor**."

That's now out of date. Cursor 1.7 (Oct 2025) shipped a full agent-hooks system
(`.cursor/hooks.json`) and Cursor natively reads the open Agent Skills standard
(`.agents/skills/`, `.cursor/skills/`). Checking the current hook contract, every
mechanism debt-ops needs is present — and the envelopes Cursor exposes make it a
*fuller* target than Copilot:

| debt-ops mechanism | Claude | Cursor hook | Cursor output channel |
|---|---|---|---|
| Disciplines at session start | `SessionStart` inject | `sessionStart` | `additional_context` (injected into initial context) |
| Write-time quality checks | `PostToolUse(Edit)` | `postToolUse` (no matcher → self-filter to edits) | `additional_context` (injected) |
| Stop-time safety net | `Stop` `decision:block` | `stop` | `followup_message` (auto-submitted to continue) |
| `drop A` intercept + confirm | `UserPromptSubmit` block | `beforeSubmitPrompt` | `continue:false` + `user_message` |

So Cursor gets the **full write-time loop, the stop safety net, the drop
intercept, and session-start injection** — the Claude/Codex tier. The one thing
Copilot couldn't carry (drops; its `userPromptSubmitted` output isn't processed)
works on Cursor.

## Decision

Ship a self-contained `cursor/` adapter as a first-class peer to
`claude-code/`, `codex/`, and `copilot/`: four hooks (`session-start.py`,
`feedback.py`, `stop.py`, `drop.py`) + a `hooks.json`, plus bundled copies of the
four `debt-ops-*` skills. Codex is the structural base (shared
`DEBT_OPS_CACHE` → `~/.cache/debt-ops`, `AGENTS.md` charter, skill-name
invocation); only the hook I/O envelopes differ, and they're Cursor's snake_case
(`additional_context`, `followup_message`, `continue`/`user_message`).

We reject `afterFileEdit` for write-time feedback: it's **informational-only**
(no output is injected back to the agent). `postToolUse` fires on every tool and
*does* inject `additional_context`, so `feedback.py` self-filters to edit tools
by `tool_name`/`tool_input` — the same posture as the Copilot adapter.

## What this means for you

- On Cursor you now get the same deterministic write-time loop as Claude Code and
  Codex, not the degraded skills-only experience. Install commits `.cursor/hooks.json`
  + `.cursor/hooks/*.py` and drops the `debt-ops-*` skills into `.agents/skills/`
  (or `.cursor/skills/`). See [`cursor/README.md`](../../cursor/README.md).
- The cache, registry, and `metrics.jsonl` are the shared `~/.cache/debt-ops`
  base, so `debt-ops-review` and `debt-ops-metrics` see Cursor's data exactly as
  they see the other adapters'.
- This is a **fifth duplicated copy** of the shared hook/skill logic. Per
  [ADR 0014](./0014-keep-adapters-duplicated.md) the copies stay in sync by
  hand/AI in the same change — `cursor/` is now part of "every copy."

## Alternatives we ruled out

- **Skills-only degraded mode** (the old plan). Leaves the differentiator on the
  table when Cursor can run it deterministically. Reversed.
- **`afterFileEdit` for feedback.** Cleaner payload (`file_path` + `edits`) but
  the hook can't return anything to the agent — feedback would be invisible.
  `postToolUse` + self-filter is the working channel.
- **A Cursor "plugin"/marketplace package.** Cursor has no documented
  plugin/marketplace install for bundled skills+hooks yet (only a nascent
  `workspaceOpen` → `pluginPaths`). So we ship via the committed `.cursor/` +
  skills dirs, the same self-contained shape as the manual-copy path on other
  adapters.

## When to revisit

- If Cursor ships a real plugin/marketplace install, add a packaged path (mirror
  ADR 0015's Copilot plugin work) instead of manual file copies.
- If `afterFileEdit` gains an inject channel, reconsider it for cleaner edit
  metadata.
- If hand/AI sync across five copies actually ships a drift bug, revisit the
  extraction question ([ADR 0014](./0014-keep-adapters-duplicated.md)).
