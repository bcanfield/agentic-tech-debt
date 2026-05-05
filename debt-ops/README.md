# debt-ops

Continuous, evidence-based tech debt management for Claude Code. Two skills, two hooks, two scripts, zero install footprint.

## What it does

On every session start, a hook injects three disciplines into Claude's context — auto-register expedient markers as debt, draft Nygard-format ADRs for architecturally significant changes, read the registry before changing referenced files. The same hook detects (or recalls from cache) the project's quality commands. After every agent edit, a `PostToolUse` hook runs those commands in parallel under a 3 s budget per command and returns structured pass/fail to Claude. When Claude writes a `TODO` / `FIXME` / `HACK` / `XXX` during normal work, it invokes `/debt-ops:add` to register the debt under `debt/registry/`. Nothing is created in your repo until Claude has a reason to write it.

## Install

Add the plugin via Claude Code's `/plugin` command from a marketplace, or point your `.claude/settings.json` at this directory.

## Prerequisites

- A git repository. The plugin idles on non-git directories.
- Bash. macOS and Linux out of the box; on Windows, use WSL or Git Bash.
- macOS bonus: install GNU coreutils (`brew install coreutils`) to get `gtimeout`. The plugin works without it via a portable shim, but `gtimeout` is more accurate.
- Optional: `jq` for `$CHANGED_FILES` substitution in PostToolUse. Without it, commands containing `$CHANGED_FILES` are skipped.

Targets Claude Code v2.1.121 or later.

## What appears in your repo, and when

| Path | When it appears |
|---|---|
| `debt/registry/<id>-<slug>.md` | Claude calls `/debt-ops:add` (auto, on a TODO/FIXME, or on user request). The directory is lazily created. |
| `doc/adr/<n>-<title>.md` | Claude drafts an ADR for an architecturally significant change. The directory is lazily created. |
| `## Tech debt operations` section in `./CLAUDE.md` | Only when you run `/debt-ops:init`. |

The plugin never modifies anything else in your repo.

## Commands

### `/debt-ops:add`

Register a debt entry. Auto-invoked by Discipline 1 when Claude writes an expedient marker. Use `payoff_trigger: unknown` if unsure. Drop entries by replying "drop it" or by deleting the file.

### `/debt-ops:init` (opt-in)

Persist the disciplines and quality commands into `./CLAUDE.md` so the team shares one source of truth. The skill is gated by `disable-model-invocation: true` — Claude cannot auto-invoke it. Re-running regenerates only the managed section.

Solo developers can skip `/debt-ops:init`; the SessionStart inject covers the same ground per-session.

## Cache location

Per-repo cache lives under `${CLAUDE_PLUGIN_DATA}/cache/<repo-hash>/`, where `<repo-hash>` is a short hash of `git rev-parse --show-toplevel`. The cache holds:

- `feedback.list` — quality commands detected by Claude on first session.
- `manifest.hash` — mtime hash of `Cargo.toml` / `package.json` / `pyproject.toml` / `Makefile` / `go.mod` / `Gemfile`. On mismatch, discovery re-runs.
- `test-count` — count of test-shaped filenames; `feedback.sh` warns when it drops.

When `${CLAUDE_PLUGIN_DATA}` is read-only, the plugin runs in stateless mode (no cache, discovery prompt fires every session). That's a degraded but functional posture.

## What it deliberately doesn't do

- No blocking rules. `feedback.sh` surfaces pass/fail; it never rejects an edit. Strict gates arrive in v3.
- No `agent` override, no `output-styles`, no global side effects on your `settings.json`.
- No CLAUDE.md scaffolding. Claude Code's built-in `/init` already does that.
- No charter creation without `/debt-ops:init`. Zero-footprint by default.

## Design rationale

See [`../docs/tech-debt-plugin-plan.md`](../docs/tech-debt-plugin-plan.md) for the v1 spec, and [`../docs/tech-debt-pillars.md`](../docs/tech-debt-pillars.md) for the principles each piece satisfies.
