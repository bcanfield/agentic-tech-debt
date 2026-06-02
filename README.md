# debt-ops

**Catches tech debt and architectural decisions as your AI codes. Then stays out of your way until you're ready.**

Any stack. Backed by decades of research.

*Works with [Claude Code](./claude-code) and [Codex](./codex).*

[![MIT License](https://img.shields.io/github/license/bcanfield/agentic-tech-debt?color=blue)](./LICENSE)
[![Claude Code plugin](https://img.shields.io/badge/Claude%20Code-plugin-d97757)](./claude-code)
[![Codex plugin](https://img.shields.io/badge/Codex-plugin-000000)](./codex)

<img src="./demo/concept/debt-ops-concept.gif" width="720" alt="A real `# TODO` deferral in the code detaches and files itself as a registry entry `+1 entry: retry-swallows-error (A)`; a second nit is caught the same way; the nit slides off and the kept entry is paid down (strikethrough + green ✓); the registry empties to zero; debt-ops wordmark." />

## What it does

- **Logs every shortcut** to a debt registry: a TODO, a stub, a loosened type, a "fix it later."
- **Writes a short decision record** when your agent makes an architectural call.
- **Reads what's already logged** before changing a file, so your agent stops re-litigating settled decisions.
- **Runs your linter, type-checker, and tests** on each agentic edit, fixing failures before they reach your diff.
- **Ranks what to clean up first** by how active each file is, so effort goes to the hotspots.

## Install

A self-contained plugin per agent. Both need a git repo and Python 3.10+.

**Claude Code** (v2.1.121+)

```bash
/plugin marketplace add bcanfield/agentic-tech-debt
/plugin install debt-ops
```

**Codex**

```bash
codex plugin marketplace add bcanfield/agentic-tech-debt
# then, inside Codex: /plugins → install debt-ops
```

Nothing's written until there's a reason. Entries land in `docs/debt/`, decisions in `docs/adr/`.

## Commands

Claude Code `/debt-ops:<name>` · Codex `$<name>`:

- **add**: register a debt entry (auto-fires when your agent defers work). Drop with `drop A`, `drop A,C`, or `drop all`.
- **review**: audit and rank the registry, then walk paydown.
- **init** *(opt-in)*: write the disciplines into `CLAUDE.md`/`AGENTS.md` so the team shares them.
- **metrics**: read-only health summary of the registry.

<img src="./demo/debt-ops.gif" width="720" alt="debt-ops in Claude Code: adding retry logic logs two entries as ruff, mypy and pytest pass, logging two entries: the swallowed error (A) and a logging nit (B); drop B prunes the nit; then /debt-ops:review ranks the churn hotspots" />

## Why it exists

AI accrues debt faster than you can review it. The fix is decades old: make it visible, pay it down continuously, document the decisions. Distilled here into [nine cited pillars](./docs/tech-debt-pillars.md) wired into the agent loop. Full [research synthesis](./docs/tech-debt-management.md).

## License

MIT. See [LICENSE](./LICENSE).
