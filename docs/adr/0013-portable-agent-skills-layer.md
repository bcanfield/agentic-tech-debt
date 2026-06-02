# 0013 — Portable Agent Skills layer for cross-tool reach

**Date:** 2026-06-02
**Status:** Accepted

> **Note (superseded in part):** this ADR's references to paying down the
> duplication via a vendored `_common.py` are reversed by
> [ADR 0014](./0014-keep-adapters-duplicated.md) — we keep the duplication and sync
> by AI instead. The cross-tool packaging decision below still stands.

## Context

We ship two self-contained plugin adapters: `claude-code/` and `codex/`. That
reaches Claude Code and Codex users and no one else. The larger market —
Copilot, Gemini CLI, Cursor, Continue, Windsurf, and ~35 more — runs other
agents. Since Anthropic released **Agent Skills** as an open standard (Dec 2025),
those tools all read the *same* `SKILL.md` format: a folder with `name` +
`description` frontmatter, optional bundled `scripts/`, loaded by progressive
disclosure. One skills folder now works across ~40 agents.

But debt-ops is two mechanisms, not one:

- **Model-invoked** (`add`, `review`, `metrics`, `init`) — the agent *chooses* to
  run them. These map 1:1 onto the Agent Skills standard.
- **Hook-driven** (`feedback.py` write-time lint/type/test, the SessionStart
  inject, `drop`, the Stop safety-net) — the *runtime* fires them deterministically,
  every edit. This is the differentiator, and the Agent Skills standard has **no
  event/hook mechanism**. A skill only runs when the model decides it's relevant.

So "package the hooks as a skill" is a category error: it would convert
deterministic write-time enforcement into a model's discretionary choice,
violating Pillar 7 (*deterministic over vibes*) and the whole reason
`feedback.py` is a `PostToolUse` hook and not a slash command.

## Decision

Add a runtime-agnostic **`skills/`** set at the repo root as a *third distribution
channel*, alongside the two plugin adapters. It carries only the model-invoked
surface and follows the open standard strictly so it drops into any compatible
tool:

- Frontmatter is `name` + `description` **only** — no `allowed-tools`, no
  `disable-model-invocation` (both are Claude Code extensions, ignored or
  rejected elsewhere). User-only intent (the old `init`) is enforced by wording
  in the description and body, not a frontmatter flag.
- Helper scripts are **bundled** in each skill's `scripts/` and referenced by
  relative path (`python3 scripts/register.py`), resolved against the skill root —
  the one path form every compatible tool supports.
- Skill names are prefixed (`debt-ops-add`, not `add`) so they don't collide
  with a user's other skills in tools that key on the bare name.
- Any bash in the markdown uses Python (`python3 -c …`) for the repo-hash, not
  `shasum`/`sha1sum` — honoring the project's "Python over Bash" rule and the
  BSD/GNU portability dance it exists to avoid.

The hook-driven layer is explicitly **out of this channel**. It stays a
per-runtime hook adapter and is extended to the tools that now expose hooks
(Copilot CLI and Gemini CLI both ship a `postToolUse`/`sessionStart` contract
nearly identical to Claude Code's) in a later phase — see
`docs/agent-skill-packaging-plan.md`. The released `claude-code/` and `codex/`
adapters are untouched in this phase (in scope: add a channel, not refactor
shipped plugins).

## What this means for you

- **Any Agent-Skills tool can use debt-ops' capture/review/metrics today.** Drop
  the `skills/` folder into the tool's skills directory (paths in
  `skills/README.md`).
- **Skills-only tools get a degraded mode, and we say so.** Without a hook
  adapter, there is no deterministic write-time feedback and no auto-capture on
  every edit — the agent self-applies the disciplines from the charter
  (`debt-ops-init` writes them to `AGENTS.md`). That's "vibes," not a tripwire.
  The full experience needs a hook adapter (Claude Code, Codex today; Copilot and
  Gemini next).
- **One more copy of the helper scripts.** `register.py`/`review.py` now exist in
  three places. This trips the payoff trigger on the
  `adapter-script-duplication` debt entry ("a third agent adapter is added");
  the plan schedules the `_common.py` vendoring as the payoff.

## Alternatives we ruled out

- **Cram `feedback.py` into a skill.** The point of the product is that quality
  checks fire on *every* edit, not when the model feels like it. A skill can't do
  that — it's model-invoked by definition. Ships the degraded version as if it
  were the product.
- **Collapse all three skill copies (claude-code, codex, portable) into one set
  now.** The portable set *could* eventually be the single source both adapters
  symlink/vendor from. But that edits the already-released plugins, which is out
  of scope here and couples this channel to a bigger refactor. Sequence it behind
  the `_common.py` extraction instead.
- **AGENTS.md-only, skip skills.** Writing disciplines into `AGENTS.md` reaches
  every tool but loses the invokable `add`/`review`/`metrics` UX and progressive
  disclosure. Since skills are now universal, there's no reason to give that up —
  `AGENTS.md` is the *degraded* fallback, not the strategy.

## When to revisit

- **A hook-bearing tool gets its adapter.** When the Copilot or Gemini hook
  adapter lands, this channel stops being that tool's only option and becomes its
  skills half — revisit the README's per-tool guidance.
- **The third-copy duplication bites.** The moment a shared-logic fix lands in one
  copy and not the others (a real bug, not just drift), extract the vendored
  `_common.py` copied into each plugin/skill at release time. That's the
  registered debt entry's payoff.
- **The standard adds an event mechanism.** If Agent Skills ever grows a portable
  hook/trigger primitive, the model-invoked vs hook-driven split this ADR is built
  on collapses, and the whole packaging story should be reconsidered.
