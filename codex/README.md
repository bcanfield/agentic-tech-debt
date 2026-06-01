# debt-ops — Codex adapter

The [debt-ops](../README.md) disciplines, packaged as a [Codex](https://developers.openai.com/codex) plugin. Behavior matches the [Claude Code adapter](../claude-code); this README covers only what's Codex-specific.

## Install

```bash
/plugins marketplace add bcanfield/agentic-tech-debt
/plugins install debt-ops
```

For local development, point Codex at this repo's marketplace (`.agents/plugins/marketplace.json`) and install `debt-ops` from it. Needs a git repo and Python 3.10+ (stdlib only).

## What's wired

| Codex primitive | File | Role |
| --- | --- | --- |
| `SessionStart` hook | `scripts/session-start.py` | Injects the disciplines + detects/caches quality commands and ADR/registry dirs |
| `PostToolUse` hook (`apply_patch\|Edit\|Write`) | `scripts/feedback.py` | Runs quality commands on edited files under a 3s/command budget |
| `Stop` hook | `scripts/stop.py` | TODO-sniff safety net — nudges when deferrals went unregistered |
| `UserPromptSubmit` hook | `scripts/drop.py` | Handles `drop A` / `drop A,C` / `drop all` shorthand |
| Skills | `skills/{add,review,init,metrics}` | `$add`, `$review`, `$init`, `$metrics` |

## Codex-specific notes

- **Charter file is `AGENTS.md`**, not `CLAUDE.md` — `$init` writes the managed `## Tech debt operations` section there, and the hooks read quality commands from it.
- **Edits are `apply_patch`.** The feedback hook parses the V4A patch envelope (`*** Add/Update File:`, `*** Move to:`) to learn which files changed, since there's no `tool_input.file_path`.
- **Cache** lives at `~/.cache/debt-ops/cache/<repo-hash>/` (override with `DEBT_OPS_CACHE`) so the hooks and skill Bash always agree on one path ([ADR 0012](../docs/adr/0012-codex-deterministic-cache-base.md)).
- **Skill invocation** is `$add` / `$review` / `$init` / `$metrics` (or the `/skills` picker). `$init` is explicit-only (`skills/init/agents/openai.yaml`).
- **Debug:** set `DEBT_OPS_DEBUG=1` to log every hook fire to `<cache>/debug.log`.

## Research

Disciplines map to the [nine tool-agnostic pillars](../docs/tech-debt-pillars.md); the [Claude Code mapping](../docs/tech-debt-plugin-plan.md) explains why each hook exists. Same evidence base, different agent.
