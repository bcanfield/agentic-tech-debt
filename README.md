# debt-ops

**Catches AI-introduced tech debt at write-time**

*Works with [any coding agent](#install). Any stack.*

*Two decades of tech-debt research, distilled into a plugin and validated across dozens of codebases.*

<img src="./demo/debt-ops.gif" width="720" alt="debt-ops in Claude Code: the agent edits api/checkout.ts and casts a value to `as any` to clear a type error; debt-ops catches the loosened type at write-time and logs +1 entry: as-any-checkout-payload (A)" />

[![MIT License](https://img.shields.io/github/license/bcanfield/agentic-tech-debt?color=blue)](./LICENSE)
[![Claude Code plugin](https://img.shields.io/badge/Claude%20Code-plugin-d97757?logo=claude&logoColor=white)](#install)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)

## What it does

- **Tracks the debt** — every "I'll fix this later," shortcut, and punt your agent writes lands in a folder in your repo.
- **Records the decisions** — a short ADR when your agent makes an architectural call.
- **Works quietly in the loop** — reads what's already logged, ranks cleanup by hotspot, and surfaces failures before they hit your diff.

---

## Install

Just needs a git repo and Python 3.10+.

<img src="https://cdn.simpleicons.org/claude/d97757" height="16" alt="" align="absmiddle" /> **Claude Code** (v2.1.121+)

```bash
/plugin marketplace add bcanfield/agentic-tech-debt
/plugin install debt-ops@agentic-tech-debt
```

<details>
<summary>Codex, Copilot, and other agents</summary>

**Codex**

```bash
codex plugin marketplace add bcanfield/agentic-tech-debt
# then, inside Codex: /plugins → install debt-ops
```

<img src="https://cdn.simpleicons.org/githubcopilot" height="16" alt="" align="absmiddle" /> **GitHub Copilot CLI**

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

</details>

---

<details>
<summary>Commands</summary>

## Commands

Claude Code `/debt-ops:<name>` · Codex `$<name>`:

- **add**: register a debt entry (auto-fires when your agent defers work). Drop with `drop A`, `drop A,C`, or `drop all`.
- **review**: audit and rank the registry, then walk paydown.
- **init** *(opt-in)*: write the disciplines into `CLAUDE.md`/`AGENTS.md` so the team shares them.
- **metrics**: read-only health summary of the registry.

</details>

---

## Why it exists

AI writes more code and cleans up less of it: across 211M lines, one study saw refactoring more than halve while duplicated code kept climbing. So debt piles up faster than you can review it. The fixes are well understood: keep it visible, pay it down over time, record the decisions. debt-ops wires those into the agent loop as [nine cited pillars](./docs/tech-debt-pillars.md). Full [research synthesis](./docs/tech-debt-management.md).

<img src="./demo/concept/debt-ops-concept.gif" width="720" alt="A `as any` cast in api/checkout.ts is caught at write-time and files itself as a registry entry `+1 entry: as-any-checkout-payload (A)`; a `// TODO` nit is caught the same way; the nit is pruned and the kept entry is paid down (strikethrough + green check); the registry empties to zero; debt-ops wordmark." />

