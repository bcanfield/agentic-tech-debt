# debt-ops

Continuous, evidence-based tech debt management for Claude Code. A few skills, a few hooks, zero install footprint.

## What it does

On every session, a hook injects three disciplines (auto-register deferrals, draft ADRs for architecturally significant changes, read the registry before changing referenced files) and detects the project's quality commands. After every agent edit, those commands run in parallel under a 3 s budget per command and return pass/fail to Claude. When Claude defers work — a `TODO`/`FIXME`/`HACK`/`XXX` marker, a stub, a loosened type, a "future"/"later" comment, or any decision left for later — it auto-invokes `/debt-ops:add` to register the entry under your debt registry (default `docs/debt/`, or an existing convention it detects). Nothing is created in your repo until Claude has a reason to write it.

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

- **`/debt-ops:add`** — register a debt entry. Auto-invoked by Discipline 1 when Claude defers work (marker, stub, loosened type, "future" comment, or any decision left for later). Each capture surfaces as a one-liner with a batch letter: `+1 entry: <slug> (A)`. Drop the just-captured batch with `drop A`, `drop A,C`, or `drop all`; drop older entries by slug (`drop foo-slug`) or by deleting the file.
- **`/debt-ops:init`** *(opt-in)* — persist the disciplines and quality commands into `./CLAUDE.md` so the team shares one source of truth. Re-run to regenerate.
- **`/debt-ops:review`** — audit and triage the registry in one pass. Flags entries whose hotspot file no longer exists as `stale` (droppable with `drop A,B,…`), deprioritizes files unchanged in 90+ days as `cold`, and ranks the rest by churn × Fowler quadrant to surface the top 3 to pay down next. Run when the registry feels heavy. See [ADR 0007](../doc/adr/0007-registry-review-skill.md).
- **`/debt-ops:metrics`** — print a short health summary of the plugin's own dogfood log: edits per session, registry growth, ADR rate, hook fail→pass rate. Read-only. Reads `${CLAUDE_PLUGIN_DATA}/cache/<repo-hash>/metrics.jsonl` (typically `~/.claude/plugins/data/debt-ops-agentic-tech-debt/cache/<repo-hash>/metrics.jsonl`; the exact path is printed in the SessionStart context block). The skill auto-locates it; you only need the path if tailing it yourself.

## What appears in your repo

| Path                                             | When                               |
| ------------------------------------------------ | ---------------------------------- |
| `docs/debt/<id>-<slug>.md`                       | Claude calls `/debt-ops:add`       |
| `docs/adr/<n>-<title>.md`                        | Claude drafts an ADR               |
| `## Tech debt operations` section in `CLAUDE.md` | Only when you run `/debt-ops:init` |

ADRs and the registry are co-located under one home: `docs/` by default, or an existing convention the plugin detects (`docs/adr` + `docs/debt`, an existing `doc/adr`, etc.) — see [ADR 0009](../doc/adr/0009-convention-aware-placement.md). The plugin never modifies anything else in your repo, never blocks an edit, and never adds files on install.

## Design rationale

See [`../docs/tech-debt-plugin-plan.md`](../docs/tech-debt-plugin-plan.md) for the v1 spec and [`../docs/tech-debt-pillars.md`](../docs/tech-debt-pillars.md) for the principles.
