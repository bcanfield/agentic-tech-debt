# 0016 — One adapter layout: organize scripts by their invoker

**Date:** 2026-06-02
**Status:** Accepted

## Context

The four implementations (`claude-code/`, `codex/`, `copilot/`, portable `skills/`)
had drifted into inconsistent folder layouts. Auditing them, the differences split
into two kinds:

- **One free inconsistency.** `claude-code` lumped all six helper scripts into a flat
  `scripts/` dir; the other three split hook scripts into `hooks/` and skill scripts
  into each skill's `scripts/`. Claude did this only because `${CLAUDE_PLUGIN_ROOT}`
  *let* it address a shared dir — not because anything required it.
- **Several forced divergences.** Manifest location, skill dir names, and
  script-reference style differ because each host tool mandates it.

## Decision

**Canonical layout rule: a script lives with whatever invokes it.**

- Hook scripts (`feedback`, `session-start`, `drop`, `stop`) live in `hooks/`, next to
  the `hooks.json` that names them — they are a unit with the hook config.
- Skill scripts (`register`, `review`) live in their skill's own `scripts/` dir — the
  `SKILL.md` that calls them is what they're coupled to.

A flat `scripts/` bin groups by file-type ("it's a `.py`"), the weakest organizing
principle. Grouping by invoker matches the actual coupling and is what three of four
adapters already did. `claude-code` is realigned to it: its hook scripts moved to
`hooks/`, its `register.py`/`review.py` into `skills/add/scripts/` and
`skills/review/scripts/`, and the flat `scripts/` dir is deleted. `hooks.json` and the
two `SKILL.md`s were repointed.

**Forced divergences are kept and documented** (they are not drift):

| Aspect | Why it can't be uniform |
|---|---|
| Manifest: `.claude-plugin/` / `.codex-plugin/` / root `plugin.json` | Each host requires its own location; Copilot's documented default is root. |
| Skill dir name: `add` vs `debt-ops-add` | Namespaced plugins (`/debt-ops:add`, `$add`) want a bare leaf; portable skills drop into a *shared* skills dir alongside other tools, so they need the `debt-ops-` prefix to stay collision-safe. Copilot bundles the portable skills verbatim ([ADR 0014](./0014-keep-adapters-duplicated.md)). |
| Script reference: `${CLAUDE_PLUGIN_ROOT}/…` vs relative `scripts/…` | Claude exposes a plugin-root token; the open SKILL.md standard does not, so codex/copilot/portable must call bundled scripts by relative path. (Layout is identical; only the *reference string* differs.) |

The full map lives in CLAUDE.md under "Adapter parity — duplicated on purpose."

## Consequences

- All four adapters now share one structure: `hooks/` for hook scripts + config,
  `skills/<skill>/scripts/` for skill scripts. `init`/`metrics` have no `scripts/`
  anywhere (they ship no helper).
- The duplication-sync map lines up 1:1 by path (modulo the skill-name prefix), so
  "diff against `claude-code/` and propagate" is now a literal path diff.
- Past ADRs and `docs/tech-debt-plugin-plan.md` still reference the old
  `claude-code/scripts/` path. They are point-in-time records and were left as-is;
  CLAUDE.md is the live convention.

## Alternatives we ruled out

- **Keep `claude-code`'s flat `scripts/` as the "reference" layout.** Rejected: it
  forces the sync map to cross-map mismatched paths and makes claude the lone
  outlier for no functional gain.
- **Force one skill dir name everywhere** (e.g. `debt-ops-add` in all four). Rejected:
  it makes the namespaced invocations redundant (`/debt-ops:debt-ops-add`) to fix a
  divergence that has a real reason.

## Payoff trigger

Revisit if a host tool changes its required manifest location or adds/removes a
plugin-root token — either would shift which divergences are still "forced."
