# debt-ops

**Catches tech debt and architectural decisions as your AI codes. Then stays out of your way until you're ready.**

Any stack. Backed by decades of research.

[![MIT License](https://img.shields.io/github/license/bcanfield/agentic-tech-debt?color=blue)](./LICENSE)
[![Claude Code plugin](https://img.shields.io/badge/Claude%20Code-plugin-d97757)](./claude-code)

<img src="./demo/concept/debt-ops-concept.gif" width="720" alt="A real `# TODO` deferral in the code detaches and files itself as a registry entry `+1 entry: retry-swallows-error (A)`; a second nit is caught the same way; the nit slides off and the kept entry is paid down (strikethrough + green ✓); the registry empties to zero; debt-ops wordmark." />

## What it does

- **Logs every shortcut** to a debt registry: a TODO, a stub, a loosened type, a "fix it later."
- **Writes a short decision record** when your agent makes an architectural call.
- **Reads what's already logged** before changing a file, so your agent stops re-litigating settled decisions.
- **Runs your linter, type-checker, and tests** on each agentic edit, fixing failures before they reach your diff.
- **Ranks what to clean up first** by how active each file is, so effort goes to the hotspots.

## Install

```bash
/plugin marketplace add bcanfield/agentic-tech-debt
/plugin install debt-ops
```

Needs a git repo, Python 3.10+ (stdlib only), and Claude Code v2.1.121+. For local development, point Claude at the plugin dir instead: `claude --plugin-dir /path/to/agentic-tech-debt/claude-code`.

Nothing is written on install. Files appear only when there's a reason, and it follows your existing convention (`doc/adr`, `docs/`) if you have one:

| Path                                     | When                             |
| ---------------------------------------- | -------------------------------- |
| `docs/debt/<id>-<slug>.md`               | Claude registers a debt entry    |
| `docs/adr/<n>-<title>.md`                | Claude drafts an ADR             |
| `## Tech debt operations` in `CLAUDE.md` | Only if you run `/debt-ops:init` |

## Commands

- **`/debt-ops:add`** - register a debt entry. Auto-invoked when your agent defers work; each capture is a one-liner with a batch letter (`+1 entry: <slug> (A)`). Drop with `drop A`, `drop A,C`, or `drop all`.
- **`/debt-ops:review`** - audit and triage the registry: flags stale entries, deprioritizes cold files, ranks the rest by change frequency and risk. Run when it feels heavy.
- **`/debt-ops:init`** *(opt-in)* - write the disciplines and your quality commands into `CLAUDE.md` so the team shares one source of truth.
- **`/debt-ops:metrics`** - a read-only health summary of the plugin's own log: edits per session, registry growth, ADR rate, hook fail→pass rate.

<img src="./demo/debt-ops.gif" width="720" alt="debt-ops in Claude Code: adding retry logic logs two entries as ruff, mypy and pytest pass: the swallowed error (A) and a logging nit (B); drop B prunes the nit; then /debt-ops:review ranks the churn hotspots" />

## Why it exists

AI writes code fast and accrues debt just as fast. Across 211M lines (GitClear, 2020–2024), refactoring fell from ~25% of changed code to under 10% and code reverted within two weeks nearly doubled. The fix is decades old: make debt visible, pay it down continuously, document the decisions. It just rarely survives an agent moving faster than you can review.

debt-ops distills that research into [nine tool-agnostic pillars](./docs/tech-debt-pillars.md) and wires it into the agent loop. Every claim is cited, the weak ones flagged.

- [`docs/tech-debt-management.md`](./docs/tech-debt-management.md): the research synthesis
- [`docs/tech-debt-pillars.md`](./docs/tech-debt-pillars.md): the nine pillars
- [`docs/tech-debt-plugin-plan.md`](./docs/tech-debt-plugin-plan.md): how they map to the plugin

## License

MIT. See [LICENSE](./LICENSE).
