# debt-ops — Cursor adapter

Brings debt-ops' **write-time feedback loop** to Cursor via Cursor's agent hooks
(`.cursor/hooks.json`, Cursor 1.7+). Unlike a skills-only install, Cursor's hooks
fire deterministically on the agent loop, so quality checks, the stop-time safety
net, and `drop` shorthand all run on their own — the same posture as the Claude
Code and Codex adapters ([ADR 0020](../docs/adr/0020-cursor-full-hook-adapter.md)).

## Why Cursor is full-experience, not degraded

The [portable skills](../skills/) already run on Cursor (it reads the open
`SKILL.md` standard), but skills are model-invoked — they can't fire on every
edit. Cursor's hook contract closes that gap, and it exposes every channel the
loop needs:

| Capability | Claude Code | Cursor | Here |
|---|---|---|---|
| Disciplines at session start | `SessionStart` inject | `sessionStart` → `additional_context` | ✅ injected, same as Claude/Codex |
| Write-time quality checks | `PostToolUse(Edit)` | `postToolUse` (no matcher) → `additional_context` | ✅ ported — `feedback.py` self-filters to edit tools by `tool_name`/`tool_input` |
| Stop-time safety net | `Stop` `decision:block` | `stop` → `followup_message` | ✅ ported — `stop.py` returns a continuation message |
| `drop A` intercept + confirm | `UserPromptSubmit` block | `beforeSubmitPrompt` → `continue:false` + `user_message` | ✅ ported — the channel Copilot lacks |

So on Cursor you get the **full write-time loop, the stop safety net, the drop
intercept, and the session-start inject** — capture/review/metrics via the
bundled skills, disciplines injected per session *and* persistable to the charter.

> **Why not `afterFileEdit`?** Cursor's `afterFileEdit` has the cleanest payload
> (`file_path` + `edits`) but is **informational-only** — it can't return anything
> to the agent. `postToolUse` *does* inject `additional_context`, so that's what
> `feedback.py` uses, self-filtering to edit tools.

## Install

Needs a git repo and Python 3.10+ (stdlib only).

### 1. Hooks

Copy this adapter's hooks into your repo's `.cursor/` directory:

```bash
mkdir -p .cursor/hooks
cp cursor/hooks/hooks.json .cursor/hooks.json
cp cursor/hooks/session-start.py cursor/hooks/feedback.py cursor/hooks/stop.py cursor/hooks/drop.py .cursor/hooks/
```

`hooks.json` must live at `.cursor/hooks.json` (Cursor's config location); the
scripts sit under `.cursor/hooks/` and are referenced by relative path from the
project root. Cursor watches the config and reloads it automatically. A
user-level install works too — drop the same files under `~/.cursor/` and adjust
the paths in `hooks.json`.

### 2. Skills

Drop the four `debt-ops-*` skills into a Cursor skills directory
(`.agents/skills/` or `.cursor/skills/`, project-local; or `~/.agents/skills/`
personal):

```bash
mkdir -p .agents/skills
cp -r cursor/skills/debt-ops-* .agents/skills/
```

`debt-ops-init` ships with `disable-model-invocation: true`, so it's
explicit-only — run it as `/debt-ops-init` when you want to write the disciplines
into `AGENTS.md` for the team. The other three are model-invoked.

### 3. (Optional) charter

The `sessionStart` hook injects the disciplines and detects quality commands
every session, so you don't *need* the charter. Run `debt-ops-init` if you want
the disciplines and the `<!-- debt-ops:feedback v1 -->` quality-commands block
persisted in `AGENTS.md` so the whole team shares them; `feedback.py` reads that
block when present (else the session-detected `feedback.list` cache).

## How it works

- **`sessionStart` → `session-start.py`** — injects the disciplines via
  `additional_context`, probes + caches the repo's ADR and registry dirs, detects
  quality commands (or reads them from the `AGENTS.md` charter), and logs one
  `session` metric.
- **`postToolUse` → `feedback.py`** — fires after every tool; idles unless the
  tool was a file edit (matched via `tool_name`/`tool_input`). On an edit: runs
  each quality command in parallel under a 3 s budget, warns if the edit dropped
  the repo's test-file count, and returns the pass/fail summary as
  `additional_context`.
- **`stop` → `stop.py`** — fires when the agent loop ends. Counts new
  TODO/FIXME/HACK/XXX markers vs new registry entries; if markers outpace
  registrations it returns a `followup_message` nudge, capped once per
  conversation so it can't loop.
- **`beforeSubmitPrompt` → `drop.py`** — intercepts `drop A` / `drop A,C` /
  `drop all` typed as the whole prompt: deletes the matching entries and blocks
  the submission (`continue:false`) with a one-line confirmation — no agent turn
  consumed.

Cache and metrics live under `~/.cache/debt-ops/` (override with
`DEBT_OPS_CACHE`) — the same base the skills and other adapters use, so
`debt-ops-review` and `debt-ops-metrics` see this adapter's data.

## Cloud agents

Cursor's cloud agents run `postToolUse` but not `sessionStart`, `stop`, or
`beforeSubmitPrompt` (those aren't wired in cloud yet). So in a cloud agent you
get the write-time feedback loop; the session inject, stop net, and drop
shorthand are local/IDE only. Persist the disciplines with `debt-ops-init` so
cloud runs still see them via the charter.

## Note on script duplication

These hooks and skills are near-verbatim copies of the Codex adapter's, on
purpose — the copies are kept in sync by hand/AI per change rather than extracted
into a shared module ([ADR 0014](../docs/adr/0014-keep-adapters-duplicated.md)).
Don't "clean up" the duplication here.
