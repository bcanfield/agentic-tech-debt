# agentic-tech-debt

**Tech-debt discipline for AI coding agents. Runs in Claude Code, never blocks an edit.**

As your agent codes, debt-ops catches tech debt as it's written.

## What it does

- **Logs every shortcut** to a debt registry: a TODO, a stub, a loosened type, a "fix it later."
- **Writes a short decision record** when your agent makes an architectural call.
- **Runs your linter, type-checker, and tests** on each agentic edit, fixing failures before they reach your diff.
- **Ranks what to clean up first** by how active each file is, so effort goes to the hotspots.

Watch it run — an edit logs the shortcuts it took while your gates fire in the loop, `drop B` prunes the over-capture in one word, and `/debt-ops:review` ranks what's left by churn:

<img src="./demo/debt-ops.gif" width="720" alt="debt-ops in Claude Code: adding retry logic logs two entries as ruff, mypy and pytest pass — the swallowed error (A) and a logging nit (B); drop B prunes the nit; then /debt-ops:review ranks the churn hotspots" />

## Install

```bash
/plugin marketplace add bcanfield/agentic-tech-debt
/plugin install debt-ops
```

Needs a git repo, Python 3.10+ (stdlib only), and Claude Code v2.1.121+. Full setup in the [plugin README](./claude-code/README.md).

Nothing is written on install. Files appear only when there's a reason, and it follows your existing convention (`doc/adr`, `docs/`) if you have one:

| Path                                     | When                             |
| ---------------------------------------- | -------------------------------- |
| `docs/debt/<id>-<slug>.md`               | Claude registers a debt entry    |
| `docs/adr/<n>-<title>.md`                | Claude drafts an ADR             |
| `## Tech debt operations` in `CLAUDE.md` | Only if you run `/debt-ops:init` |

## Why it exists

AI writes code fast and accrues debt just as fast. Across 211M lines (GitClear, 2020–2024), refactoring fell from ~25% of changed code to under 10% and code reverted within two weeks nearly doubled. The fix is decades old: make debt visible, pay it down continuously, document the decisions. It just rarely survives an agent moving faster than you can review.

debt-ops distills that research into [nine tool-agnostic pillars](./docs/tech-debt-pillars.md) and wires it into the agent loop. Every claim is cited, the weak ones flagged.

- [`docs/tech-debt-management.md`](./docs/tech-debt-management.md) — the research synthesis
- [`docs/tech-debt-pillars.md`](./docs/tech-debt-pillars.md) — the nine pillars
- [`docs/tech-debt-plugin-plan.md`](./docs/tech-debt-plugin-plan.md) — how they map to the plugin

## License

MIT — see [LICENSE](./LICENSE).
