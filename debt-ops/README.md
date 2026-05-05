# debt-ops

A Claude Code plugin for continuous, evidence-based tech debt management.

`debt-ops` adds two skills, two hooks, and two short scripts to your editor.
Install it and the first edit just works — no setup ceremony, no files
created in your repo until you ask for them.

## What it does

- **Auto-registers debt.** When Claude writes a `TODO`/`FIXME`/`HACK`/`XXX`
  that's real debt (a known shortcut, an incomplete case, a fragile
  assumption), it invokes `/debt-ops:add` and writes a structured entry
  under `debt/registry/`.
- **Drafts ADRs for architectural changes.** Data model, public interface,
  dependency manifest, security boundary, release pipeline → Claude drafts
  a Nygard-format ADR under `doc/adr/`.
- **Runs your quality commands after every edit.** A `PostToolUse` hook
  invokes the project's own type-checker, linter, and tests in parallel
  under a 3-second wall-clock budget and feeds the results back to Claude.
- **Surfaces nothing on the happy path.** If everything passes, the hook is
  silent. Failures and timeouts are reported as structured JSON the agent
  can act on.

## Install

From a marketplace that lists `debt-ops`:

```sh
/plugin install debt-ops@<marketplace>
```

Or load locally for a single session while developing:

```sh
claude --plugin-dir ./debt-ops
```

**Hard prerequisite:** the project is a git repository.

## How it works

1. **`SessionStart` hook** injects the four debt-ops disciplines into
   Claude's context every session. The first time you open a session in a
   given repo, the hook also asks Claude to detect the project's quality
   commands and write them to `${CLAUDE_PLUGIN_DATA}/feedback.list`.
   Subsequent sessions read the cache instantly.

2. **`PostToolUse` hook** (`Write|Edit|MultiEdit`) reads those commands and
   runs them in parallel under a 3-second budget. If something fails or
   times out, the hook returns structured JSON to the agent; on success it
   stays quiet.

3. **`/debt-ops:add`** — Claude drafts a registry entry from current
   context, lazily creates `debt/registry/`, and writes
   `<id>-<slug>.md`. Auto-invoked when Claude writes an expedient marker
   during normal work.

4. **`/debt-ops:init`** (opt-in) — writes a `## Tech debt operations`
   section into `AGENTS.md` (or `CLAUDE.md`) so the disciplines and
   commands persist with the repo and travel to other AI tools (Cursor,
   Aider, Codex). Solo users can skip it; the SessionStart inject covers
   the same ground per-session.

## Layout

```
debt-ops/
├── .claude-plugin/
│   └── plugin.json
├── hooks/
│   └── hooks.json
├── scripts/
│   ├── session-start.sh    # detects + caches commands; injects disciplines
│   └── feedback.sh         # runs commands in parallel, returns JSON
├── skills/
│   ├── add/SKILL.md        # /debt-ops:add
│   └── init/SKILL.md       # /debt-ops:init (opt-in)
└── README.md
```

## What v1 doesn't do

v1 is the relaxed-by-construction version. **No blocking rules.** The
PostToolUse hook surfaces failures; nothing is rejected. Strict gates,
test-integrity rules, AI-touched hotspot floors, ranking, paydown engines,
and reviewers arrive in v2/v3/v4.

See [`tech-debt-plugin-plan.md`](../tech-debt-plugin-plan.md) for the full
spec, the deferred-work table, and the roadmap.

## Coexistence

- **Namespaced everything** (`/debt-ops:*`).
- **No global `agent` override.**
- **Hooks call the project's own tooling.** Detected commands; no
  reinvented detection.
- **Charter respects ownership.** `AGENTS.md`/`CLAUDE.md` are only
  modified by opt-in `/debt-ops:init`.
- **Soft hooks, structured output.** Other plugins can read or skip
  without text-matching.
- **Zero install footprint.** Files in your repo only appear when you
  ask for them (registry entries on `/debt-ops:add`; charter edits on
  `/debt-ops:init`).

## Tuning

Two environment variables are honored:

| Variable | Default | What it controls |
|---|---|---|
| `DEBT_OPS_FEEDBACK_BUDGET` | `3` | Wall-clock seconds for `feedback.sh` |
| `CLAUDE_PLUGIN_DATA` | (set by Claude Code) | Cache directory; `feedback.list` lives here |

## License

See repository root.
