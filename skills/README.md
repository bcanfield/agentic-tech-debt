# debt-ops portable Agent Skills

Runtime-agnostic [Agent Skills](https://agentskills.io) for debt-ops. One folder,
works in any of the ~40 tools that read the open `SKILL.md` standard — Copilot,
Gemini CLI, Cursor, Continue, Windsurf, and the rest — **without** the Claude Code
or Codex plugins.

> **Status: prototype** (packaging plan Phase B). Validated by running the bundled
> helpers directly; per-tool install is documented below but not yet
> machine-tested in every tool.

## What's here

| Skill | What it does | Backed by |
|---|---|---|
| `debt-ops-add` | register a tech-debt entry | bundled `scripts/register.py` |
| `debt-ops-review` | audit + rank the registry, walk paydown | bundled `scripts/review.py` |
| `debt-ops-metrics` | read-only health summary | inline (portable `python3 -c` cache lookup) |
| `debt-ops-init` | write the disciplines to `AGENTS.md` | inline |

Each is a self-contained folder: `SKILL.md` (`name` + `description` only, strict to
the open standard) plus any `scripts/`. Helpers are referenced by relative path and
resolved against the skill root — the one form every compatible tool supports.

## The one thing these skills can't do (and why)

Agent Skills are **model-invoked** — the agent runs them when it judges them
relevant. They have no event/hook mechanism. So the part of debt-ops that fires on
*every edit* — the write-time lint/type/test feedback loop, auto-capture, and the
test-deletion warning — **is not in this folder.** That's hook-driven, and a skill
can't fire deterministically on each edit by design.

**What you get on a skills-only tool (degraded mode):** capture (`debt-ops-add`),
review (`debt-ops-review`), metrics, and a charter (`debt-ops-init`) the agent
self-applies. The disciplines run on the model's judgment, not as a tripwire.

**What you give up:** deterministic write-time enforcement. For that you need a
hook adapter — shipped today for [Claude Code](../claude-code/) and
[Codex](../codex/); Copilot CLI and Gemini CLI adapters are planned (both now expose
a `postToolUse` hook). See [the packaging plan](../docs/agent-skill-packaging-plan.md).

## Install

Drop each `debt-ops-*` folder into your tool's skills directory. Exact paths differ
per tool — check the tool's skills docs:

- **Claude Code** — `.claude/skills/` (project) or `~/.claude/skills/` (personal). [docs](https://code.claude.com/docs/en/skills)
- **GitHub Copilot / VS Code** — [agent skills docs](https://code.visualstudio.com/docs/copilot/customization/agent-skills)
- **Gemini CLI** — [skills docs](https://geminicli.com/docs/cli/skills/)
- **Cursor** — [skills docs](https://cursor.com/docs/context/skills)
- **Codex** — [skills docs](https://developers.openai.com/codex/skills/)
- Others: see the [client list](https://agentskills.io/clients).

Example (Claude Code, project-local):

```bash
mkdir -p .claude/skills
cp -r skills/debt-ops-* .claude/skills/
```

## Requirements

- Git repository (entries are addressed to repo paths).
- Python 3.10+ on PATH (the helpers are stdlib-only — no install step).

## Try it

From inside a git repo, the helpers run standalone — no agent needed — which is how
this prototype is validated:

```bash
# register an entry
printf 'Stubbed the retry path to ship the happy path first.\n' \
  | python3 skills/debt-ops-add/scripts/register.py \
      --slug stubbed-retry --principal 1d --interest unknown \
      --hotspot src/client.py --business-capability sync \
      --payoff-trigger "when flaky-sync tickets recur" \
      --quadrant prudent-deliberate --category code_quality --ai-authored true
# → +1 entry: stubbed-retry (A)

# audit + rank
python3 skills/debt-ops-review/scripts/review.py
```

Cache (letter mappings, metrics) lives under `~/.cache/debt-ops/`; override the base
with `DEBT_OPS_CACHE`.
