# debt-ops

**Catches AI-introduced tech debt at write-time**

*Works with [any coding agent](#install). Any stack. Backed by decades of research.*

<img src="./demo/debt-ops.gif" width="720" alt="debt-ops in Claude Code: the agent edits api/checkout.ts and casts a value to `as any` to clear a type error; debt-ops catches the loosened type at write-time and logs +1 entry: as-any-checkout-payload (A)" />

*Every "I'll fix this later," every shortcut, every punt your AI agent writes gets caught.*

[![MIT License](https://img.shields.io/github/license/bcanfield/agentic-tech-debt?color=blue)](./LICENSE)
[![Claude Code plugin](https://img.shields.io/badge/Claude%20Code-plugin-d97757)](#install)

> AI ships code fast and accrues debt faster. GitClear's 2024 analysis found refactored code fell from ~25% of changes to under 10%, while copy-pasted code rose 48%. The shortcuts pile up between PRs, where nobody's looking.

## Install

Just needs a git repo and Python 3.10+.

**Claude Code** (v2.1.121+)

```bash
/plugin marketplace add bcanfield/agentic-tech-debt
/plugin install debt-ops@agentic-tech-debt
```

**Codex**

```bash
codex plugin marketplace add bcanfield/agentic-tech-debt
# then, inside Codex: /plugins → install debt-ops
```

**GitHub Copilot CLI**

```bash
copilot plugin marketplace add bcanfield/agentic-tech-debt
copilot plugin install debt-ops@agentic-tech-debt
```

**Any other agent** (Cursor, Gemini CLI, Windsurf, opencode…) via portable [Agent Skills](https://skills.sh):

```bash
npx skills add bcanfield/agentic-tech-debt
```

Then run `debt-ops-init` once — on Copilot the disciplines live in your charter
(`.github/copilot-instructions.md` or `AGENTS.md`), not a per-session inject. See the
[Copilot adapter README](./copilot/README.md) for the manual-install alternative and details.

Nothing's written until there's a reason. Entries land in `docs/debt/`, decisions in `docs/adr/`.

## Contents

- [debt-ops](#debt-ops)
  - [Install](#install)
  - [Contents](#contents)
  - [What it does](#what-it-does)
  - [Who it's for](#who-its-for)
  - [Commands](#commands)
  - [Why it exists](#why-it-exists)
  - [License](#license)

## What it does

- **Logs every shortcut** to a debt registry: a TODO, a stub, a loosened type, a "fix it later."
- **Writes a short decision record** when your agent makes an architectural call.
- **Reads what's already logged** before changing a file, so your agent stops re-litigating settled decisions.
- **Runs your linter, type-checker, and tests** on each agentic edit, fixing failures before they reach your diff.
- **Ranks what to clean up first** by how active each file is, so effort goes to the hotspots.

## Who it's for

**For you if** you let AI agents write a lot of your code, you care about what they cut corners on, and you want that visible before it hits review instead of after.

**Not for you if** you're after a PR-time linter or a CI gate. debt-ops runs inside the agent loop at write-time, not on your pipeline, and it won't block a merge.

## Commands

Claude Code `/debt-ops:<name>` · Codex `$<name>`:

- **add**: register a debt entry (auto-fires when your agent defers work). Drop with `drop A`, `drop A,C`, or `drop all`.
- **review**: audit and rank the registry, then walk paydown.
- **init** *(opt-in)*: write the disciplines into `CLAUDE.md`/`AGENTS.md` so the team shares them.
- **metrics**: read-only health summary of the registry.

## Why it exists

AI accrues debt faster than you can review it. The fix is decades old: make it visible, pay it down continuously, document the decisions. Distilled here into [nine cited pillars](./docs/tech-debt-pillars.md) wired into the agent loop. Full [research synthesis](./docs/tech-debt-management.md).

<img src="./demo/concept/debt-ops-concept.gif" width="720" alt="A `as any` cast in api/checkout.ts is caught at write-time and files itself as a registry entry `+1 entry: as-any-checkout-payload (A)`; a `// TODO` nit is caught the same way; the nit is pruned and the kept entry is paid down (strikethrough + green check); the registry empties to zero; debt-ops wordmark." />

## License

MIT. See [LICENSE](./LICENSE).
