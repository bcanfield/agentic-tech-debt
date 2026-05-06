# debt-ops

Continuous, evidence-based tech debt management for Claude Code. Two skills, two hooks, two scripts, zero install footprint.

## What it does

On every session, a hook injects three disciplines (auto-register deferrals, draft ADRs for architecturally significant changes, read the registry before changing referenced files) and detects the project's quality commands. After every agent edit, those commands run in parallel under a 3 s budget per command and return pass/fail to Claude. When Claude defers work — a `TODO`/`FIXME`/`HACK`/`XXX` marker, a stub, a loosened type, a "future"/"later" comment, or any decision left for later — it auto-invokes `/debt-ops:add` to register the entry under `debt/registry/`. Nothing is created in your repo until Claude has a reason to write it.

## Install

```bash
# from this marketplace:
/plugin marketplace add bcanfield/agentic-tech-debt
/plugin install debt-ops

# or for local development:
claude --plugin-dir /path/to/agentic-tech-debt/claude-code
```

## Prerequisites

- A git repository (the plugin idles outside one)
- Python 3.10 or later (used by both hooks; standard library only)
- Claude Code v2.1.121 or later

If a quality command in `feedback.list` needs shell features (pipes, `&&`, globs), wrap that line in `bash -c '...'` explicitly. By default the hook expands `$CHANGED_FILES` itself and runs the command without a shell, so bash is not required on PATH.

## Commands

- **`/debt-ops:add`** — register a debt entry. Auto-invoked by Discipline 1 when Claude defers work (marker, stub, loosened type, "future" comment, or any decision left for later). Drop entries by replying "drop it" or deleting the file.
- **`/debt-ops:init`** *(opt-in)* — persist the disciplines and quality commands into `./CLAUDE.md` so the team shares one source of truth. Re-run to regenerate.

## What appears in your repo

| Path                                             | When                               |
| ------------------------------------------------ | ---------------------------------- |
| `debt/registry/<id>-<slug>.md`                   | Claude calls `/debt-ops:add`       |
| `doc/adr/<n>-<title>.md`                         | Claude drafts an ADR               |
| `## Tech debt operations` section in `CLAUDE.md` | Only when you run `/debt-ops:init` |

The plugin never modifies anything else in your repo, never blocks an edit, and never adds files on install.

## Design rationale

See [`../docs/tech-debt-plugin-plan.md`](../docs/tech-debt-plugin-plan.md) for the v1 spec and [`../docs/tech-debt-pillars.md`](../docs/tech-debt-pillars.md) for the principles.
