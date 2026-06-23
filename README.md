# debt-ops

**Catches AI-introduced tech debt at write-time**

*Works with [any coding agent](#install). Any stack.*

*Two decades of tech-debt research, distilled into a plugin and validated across dozens of codebases.*

<img src="./demo/debt-ops.gif" width="720" alt="debt-ops in Claude Code: the agent edits api/checkout.ts and casts a value to `as any` to clear a type error; debt-ops catches the loosened type at write-time and logs +1 entry: as-any-checkout-payload (A)" />

[![MIT License](https://img.shields.io/github/license/bcanfield/agentic-tech-debt?color=blue)](./LICENSE)
[![Claude Code plugin](https://img.shields.io/badge/Claude%20Code-plugin-d97757?logo=claude&logoColor=white)](#install)

## What it does

- **Tracks the debt** — every "I'll fix this later," shortcut, and punt your agent writes lands in a folder in your repo.
- **Records the decisions** — a short ADR when your agent makes an architectural call.
- **Works quietly in the loop** — reads what's already logged, ranks cleanup by hotspot, and surfaces failures before they hit your diff.

---

## Install

Just needs a git repo and Python 3.10+.

<a id="claude-code"></a>
<img src="./assets/agents/claude.svg" height="16" alt="" align="absmiddle" /> **Claude Code**

```bash
/plugin marketplace add bcanfield/agentic-tech-debt
/plugin install debt-ops@agentic-tech-debt
```

<details>
<summary><img src="./assets/agents/codex.svg" height="16" alt="" align="absmiddle" /> <b>Codex</b></summary>

```bash
codex plugin marketplace add bcanfield/agentic-tech-debt
# then, inside Codex: /plugins → install debt-ops
```

</details>

<details>
<summary><img src="./assets/agents/cursor.svg" height="16" alt="" align="absmiddle" /> <b>Cursor</b></summary>

One-click install via the plugin (hooks + skills bundled):

```text
/add-plugin     # then pick debt-ops, or browse cursor.com/marketplace
```

Prefer to install by hand? Copy `hooks.local.json` + the scripts into `.cursor/` and the skills into `.agents/skills/`:

```bash
mkdir -p .cursor/hooks .agents/skills
cp cursor/hooks/hooks.local.json .cursor/hooks.json
cp cursor/hooks/*.py .cursor/hooks/
cp -r cursor/skills/debt-ops-* .agents/skills/
```

See the [Cursor adapter README](./cursor/README.md) for details.

</details>

<details>
<summary><img src="./assets/agents/copilot.svg" height="16" alt="" align="absmiddle" /> <b>GitHub Copilot CLI</b></summary>

```bash
copilot plugin marketplace add bcanfield/agentic-tech-debt
copilot plugin install debt-ops@agentic-tech-debt
```

Then run `debt-ops-init` once — Copilot has no per-session inject, so this writes the
disciplines into your charter (`.github/copilot-instructions.md` or `AGENTS.md`). See the
[Copilot adapter README](./copilot/README.md) for the manual-install alternative and details.

</details>

<details>
<summary><img src="./assets/agents/gemini.svg" height="16" alt="" align="absmiddle" /> <b>Any other agent</b> (Gemini CLI, Windsurf, opencode…)</summary>

Via portable [Agent Skills](https://skills.sh):

```bash
npx skills add bcanfield/agentic-tech-debt
```

Then run `debt-ops-init` once to write the disciplines into your `AGENTS.md`.

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

