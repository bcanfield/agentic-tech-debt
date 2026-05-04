# Tech Debt — Claude Code Plugin v1 Spec

## Why this document exists

`tech-debt-pillars.md` is tool-agnostic on purpose. This document commits
those pillars to a concrete, buildable v1 plugin — and is honest about
what we are deliberately not building yet.

**What v1 is.** Three skills, three hooks, no subagents, no MCP. It does
three things:

1. Makes the agent's own quality reflexes work (Pillar 7 lite — runs
   the project's existing lint/type/test on every agent edit).
2. Makes "I'll come back to this" debt visible without taking the
   developer out of flow (Pillar 1 lite — registry + one-keystroke add).
3. Bootstraps the conventions (Pillar 6 — charter init + size budget).

**What v1 is not.** Ranking, ADR drafting, code-health analysis, fresh-
context reviewers, paydown automation, allocation reports, enforcement
rules, AI-touched longitudinal tracking. Each of those needs supporting
infrastructure (an MCP, months of PR history, multiple subagents) that
doesn't earn its weight on day 1. They arrive in v2–v4.

## The two non-negotiables

1. **Lean relaxed over strict.** v1 has zero blocking rules. Hooks
   surface and suggest; they never reject the agent's work. Strict gates
   arrive in v3 with their override skill, and even then they're
   individually disablable.
2. **Passive, plays well with others.** No `agent` override. Namespaced
   commands only (`/debt-ops:*`). Hooks call the project's existing
   tooling; we don't ship our own linters. The charter is the project's
   `CLAUDE.md` / `AGENTS.md`, not ours.

**Hard prerequisite.** A git repository. The TODO-sniff hook reads the
diff; a non-git repo gets a no-op plugin.

---

## Working name

`debt-ops` — namespaces to `/debt-ops:*`. Commands are written `/debt:*`
in this doc for brevity.

---

## The v1 commitment (at a glance)

| Pillar | v1 | Deferred |
|---|---|---|
| 1. Visibility | `/debt:add`, `/debt:list`, registry under `${registry_path}` | quadrant/category querying, stale aging, ADR auto-pairing |
| 2. Continuous Measurement | static layer (Pillar 7's lint/type) | behavioral, AI-touched windows, DORA, perception (v3) |
| 3. Hotspot Prioritization | — | full skill + `triage` subagent (v2) |
| 4. Continuous Paydown | — | `/debt:budget`, fix-it weeks, Boy Scout summary (v4) |
| 5. Deliberate Architecture | ADR template under `examples/adr/`; convention only | `/debt:adr` skill, index regen, architectural-touch nudge (v2) |
| 6. Curated Agent Context | `/debt:init` (auto-detects `AGENTS.md`/`CLAUDE.md`); `SessionStart` size check | (already complete in v1) |
| 7. In-Loop Deterministic Feedback | `PostToolUse` orchestrator: lint + type + test slice (parallel, 3 s budget; tests async) | test-integrity rule, AI-touched hotspot floor rule, `/debt:override` (v3) |
| 8. Spec → Test → Review → Comprehend | — | `/debt:spec`, `/debt:explain`, `reviewer`, `security-reviewer` (v2/v3) |
| 9. AI as Paydown Engine | — | `/debt:paydown`, GH Actions recipe (v3) |

Cross-cutting: `/debt:init` is the one-time setup; `Stop` hook does
todo-sniff.

---

## The registry schema

Every entry under `${registry_path}` is a markdown file with YAML
front-matter:

```yaml
---
id: 0042
title: cancelled-promotion-callback
principal: 2d                         # estimated effort to fix
interest: +30min/incident             # ongoing cost (free-form, quantified)
hotspot: pricing/engine.ts            # path or module
business_capability: checkout         # what this affects
payoff_trigger: when promotion engine v2 lands   # may be `unknown`
quadrant: reckless-inadvertent
category: code_quality
ai_authored: true
created: 2026-05-04
---

Free-form prose: the debt, recurrence, observed symptoms.
```

**Quadrant** (Fowler): `reckless-inadvertent`, `reckless-deliberate`,
`prudent-inadvertent`, `prudent-deliberate`. Triage order is the order
listed.

**Category** (Google / Jaspan-Green, closed enum): `migration`,
`documentation`, `testing`, `code_quality`, `dead_code`, `code_rot`,
`expertise`, `release`, `infrastructure`, `planning`.

**`payoff_trigger: unknown` is first-class.** Pillar 1 demands "register
debt under a minute"; demanding a trigger upfront is friction. `unknown`
ages into stale-review at v2 (when ranking lands).

ADRs use the Nygard format with one extension — a required
`payoff_trigger` field when the ADR introduces deliberate debt. v1 ships
the template only; the auto-pairing-with-registry behaviour arrives in
v2.

---

## Pillar-by-pillar v1 mapping

For each pillar: the v1 commitment (concrete) and what's deferred (with
the reason).

### Pillar 1 — Visibility

**v1 commitment.**

- `/debt:add` — the writer thread drafts a registry entry from current
  context, fills the schema, asks for any missing required field, writes
  to `${registry_path}/<id>-<slug>.md`. Allows
  `payoff_trigger: unknown`.
- `/debt:list` — chronological listing of registry entries with their
  quadrant and category. No ranking, no triage subagent.
- Soft nudge: the `Stop` hook detects new `TODO`/`FIXME`/"I'll come back
  to this" markers and surfaces "register this with `/debt:add`?".
  Never blocks.

**Deferred.**

- Ranking, filters (`--quadrant`, `--category`, `--stale`), the
  `triage` subagent → v2 (depends on having any meaningful population
  of entries first).
- ADR auto-pairing → v2 (depends on `/debt:adr` skill).
- Stale-aging of `unknown` triggers → v2 (depends on ranking).

---

### Pillar 2 — Continuous Measurement

**v1 commitment.**

- Static layer only, via Pillar 7's orchestrator (lint + type + test
  slice on touched files).

**Deferred.**

- Behavioral signal (hotspot, Code Health) → v3, via optional
  `code-health` MCP. We considered shipping a "lines × git frequency"
  fallback; on review it's a misleading complexity proxy and would
  actively harm trust. v1 has no behavioral signal; users who want one
  wire up an MCP at v3.
- AI-touched discriminator + 30/60/90/14-day windows → v3.
- DORA outcomes → v3 (file reader for `debt/dora.json`).
- Perception survey loop → out of plugin scope; teams put a markdown
  template under `debt/surveys/` if they want.

---

### Pillar 3 — Hotspot Prioritization

**v1 commitment.** None. `/debt:list` is chronological.

**Deferred to v2.** The skill grows to rank by churn (when there's no
MCP) or by Code Health × churn × business capability (when there is).
The `triage` subagent ships with the ranking.

The pillar fires *every* time a developer picks up the next task; v1
does not yet help with that. The cost is a known one — developers fall
back to their existing prioritization until v2.

---

### Pillar 4 — Continuous Paydown

**v1 commitment.** None.

**Deferred to v4.** `/debt:budget` (with `--fixit start|end`) needs
weeks of `Debt-Pays-Down`-tagged PR history before the number is
meaningful. The Boy Scout summary depends on a Code Health signal that
arrives with v3's MCP. Bug cap + DORA stay out of plugin scope.

What v1 *does* contribute to Pillar 4: the registry exists and entries
can be tagged, so the PR history that v4's accounting needs starts
accumulating from day 1.

---

### Pillar 5 — Deliberate Architecture

**v1 commitment.**

- `/debt:init` creates `${adr_path}/` (default `doc/adr/`) and drops a
  Nygard-format template (`0001-template.md`) with a `payoff_trigger`
  field.
- README documents the convention.

**Deferred to v2.** The `/debt:adr` skill (draft from context), the
`Stop`-hook ADR index regeneration, and the architectural-touch nudge
in the `PostToolUse` orchestrator. The nudge in particular is a
heuristic-and-likely-noisy thing; we'd rather ship it once we have
dogfood data on which paths actually matter.

---

### Pillar 6 — Curated Agent Context

**v1 commitment.**

- `/debt:init` auto-detects: if `AGENTS.md` exists, treat it as
  canonical (broader convention used by Cursor, Aider, others); else
  use `CLAUDE.md`. If neither exists, create `AGENTS.md` from a
  template that includes the section list mandated by Pillar 6 (stack,
  build/test/run, conventions, no-touch zones, ADR/registry pointers,
  escalation rules). Override via `charter_path`.
- `SessionStart` hook checks the charter is under `charter_line_budget`
  (default 200) and warns once if it isn't. Silent if all is well.

**Deferred.** None. Pillar 6 is fully covered by v1.

---

### Pillar 7 — In-Loop Deterministic Feedback

**v1 commitment.**

- One `PostToolUse` matcher (`Write|Edit|MultiEdit`) calls
  `feedback.sh`. The script:
  - Detects `lint_command`/`typecheck_command`/`test_command` from
    `userConfig`; if empty, auto-detects from project files
    (`package.json` scripts, `pyproject.toml`, `Makefile`,
    `.golangci.yml`, etc.). If no tooling is detected, the hook is a
    no-op rather than a noisy failure.
  - Runs lint and typecheck **in parallel** under a single 3 s
    wall-clock budget for the touched files.
  - Runs the test slice **async**; the result is delivered at the next
    `Stop`.
  - Returns structured JSON to the agent: `{lint, types, tests:
    pending|pass|fail}`.

**Deferred to v3.**

- Test-integrity rule (rejects diffs that delete or weaken tests in
  the same session as the production code those tests covered).
- AI-touched hotspot floor rule (rejects AI-touched diffs that worsen
  Code Health on a top-N hotspot or drop below `ai_touched_min_health`,
  default 9.4 — CodeScene's documented threshold).
- `/debt:override <reason>` skill — audit-trail escape for the two
  rules above.
- AI-touched tagging (under `debt/.ai-touched/<sha>`).
- Architectural-touch nudge.
- The optional `code-health` MCP wiring.

v1 is the relaxed-by-construction version of Pillar 7. No rejections.
Just feedback.

---

### Pillar 8 — Spec → Test → Review → Comprehend

**v1 commitment.** None.

**Deferred to v2/v3.** `/debt:spec`, `/debt:explain`, the `reviewer`
subagent (with comprehensibility mode), the `security-reviewer`
subagent, the `pre-commit.sh` comprehensibility prompt. Specs and
literate explanations are *disciplines* the team adopts via the charter;
v1's job is to make sure the charter exists and is read. The skills and
subagents formalize the disciplines once the team has settled on them.

---

### Pillar 9 — AI as a Paydown Engine

**v1 commitment.** None.

**Deferred to v3.** `/debt:paydown` skill and the documentation for
external scheduling (GH Actions cron). The pillar requires the in-loop
hooks (Pillar 7), the spec/review discipline (Pillar 8), and meaningful
hotspot ranking (Pillar 3) to all be live first. v1 has none of them
yet, so the paydown engine has nothing to operate on.

---

## Plugin layout (v1)

```
debt-ops/
├── .claude-plugin/
│   └── plugin.json
├── skills/
│   ├── init/SKILL.md            # /debt:init
│   ├── add/SKILL.md             # /debt:add
│   └── list/SKILL.md            # /debt:list
├── hooks/
│   └── hooks.json
├── scripts/
│   ├── feedback.sh              # PostToolUse: lint + type + test slice
│   ├── session-start.sh         # SessionStart: charter check
│   └── stop.sh                  # Stop: todo-sniff
├── examples/
│   ├── registry/
│   │   ├── README.md
│   │   └── 0001-example-debt.md
│   └── adr/
│       └── 0001-template.md
└── README.md
```

Three skills, zero subagents, three hook entries, three scripts. Anyone
can grok the plugin in fifteen minutes.

**`plugin.json`.**

```json
{
  "name": "debt-ops",
  "version": "0.1.0",
  "description": "Continuous, evidence-based tech debt management for Claude Code.",
  "userConfig": {
    "registry_path":       { "type": "string", "default": "debt/registry" },
    "adr_path":            { "type": "string", "default": "doc/adr" },
    "charter_path":        { "type": "string", "description": "Auto-detect AGENTS.md/CLAUDE.md if empty" },
    "charter_line_budget": { "type": "number", "default": 200 },
    "lint_command":        { "type": "string", "description": "Templated with ${file}; empty = auto-detect" },
    "typecheck_command":   { "type": "string", "description": "Templated with ${file}; empty = auto-detect" },
    "test_command":        { "type": "string", "description": "Templated with ${file}; empty = auto-detect" }
  },
  "dependencies": []
}
```

Seven config keys. Each one earns its slot.

---

## Hook layout (v1)

| Event | Matcher | Script | What it does |
|---|---|---|---|
| `PostToolUse` | `Write\|Edit\|MultiEdit` | `feedback.sh` | lint + type in parallel (3 s budget); test slice async; structured JSON result to agent |
| `SessionStart` | — | `session-start.sh` | charter size + freshness check; one-line warning if over budget |
| `Stop` | — | `stop.sh` | scan session diff for `TODO`/`FIXME`/"come back" markers; one-line "register this?" suggestion |

Outputs are structured JSON when the agent should react; one-line text
when it's a developer-facing nudge.

---

## What we skip in v1 (and when each could return)

Every cut is recoverable. The table records the trigger that would
bring each piece back; nothing is permanently off the table.

| Primitive | v1 decision | Why now | Could return when |
|---|---|---|---|
| `commands/` (legacy flat) | skip | Skills are the recommended replacement. | (we'd choose skills again, but the door isn't shut) |
| `themes/` | skip | Out of scope for tech debt. | If we ship a "code review" or "paydown session" mode that benefits from a visual cue. |
| `bin/` | skip | No script earns broader use yet. | Once a script earns standalone CLI use (e.g., a `debt-list` invokable from a non-Claude shell). |
| `.lsp.json` | skip | Anthropic ships LSP plugins for major languages. | If we target a niche language Anthropic doesn't cover. |
| `output-styles/` | skip | Heavyweight for what would just be reminders. | If a workflow needs a sustained tone shift (e.g., `tdd-mode` for a TDD-first session, `paydown-aware` during refactor runs, `security-review` tone). |
| `monitors/` | skip | Nothing in v1 needs background reactions. | v3+ for fix-it-week reactivity, CI status surfacing, or watching an external metrics endpoint. |
| `channels` | skip | No external messaging in core flow. | If we add Slack/Telegram/Discord bridges for paydown notifications or bug-cap alerts. |
| `settings.json` `agent` override | skip | Hostile to other plugins. | Only inside an explicit, time-boxed mode (e.g., a `/debt:focus` mode that takes the main thread for one paydown session and restores it). |
| Subagents (`agents/`) | skip | Skills handle drafting in v1. | v2 brings `debt-scribe` (multi-format), `triage` (ranking), `reviewer` (with comprehensibility mode); v3 adds `security-reviewer`. |
| `.mcp.json` | skip | No code-health MCP needed yet. | v3, when rules want a real Code Health signal (`code_health_mcp_endpoint`). |
| Local complexity scorer | skip in current form | "Lines × git frequency" is a misleading complexity proxy. | If replaced with a tree-sitter-based scoring (~20 lines per language) that's honest about what it measures. |
| GitHub Actions example | skip | Ships with `/debt:paydown`. | v3, alongside the paydown skill. |
| Skills folded in v1 | (see below) | Either covered by another skill or premature. | See "Future possibilities" — every folded skill is logged as a potential addition. |

---

## How we coexist with other plugins

1. **Namespace everything.** `/debt-ops:*` only. No short-alias
   land-grabs.
2. **No global `agent`.** We never set `settings.json` `agent`.
3. **Hooks call project tooling, don't replace it.** `feedback.sh` runs
   the project's eslint (or whatever); it doesn't shadow another
   plugin's hook.
4. **Charter respects ownership.** `CLAUDE.md` / `AGENTS.md` is the
   project's; we seed once on `/debt:init`; never overwrite on update.
5. **Soft hooks, structured outputs.** Hook results are structured
   JSON the agent reliably parses; other plugins/hooks can read or
   skip without ambiguous text-matching.

---

## Gaps in Claude Code primitives (honest list)

Most of these only matter for v2+; listed here so we know what's
coming.

1. **Cron / scheduling.** Pillar 9 needs an external scheduler (GH
   Actions). v3 ships the recipe.
2. **Cross-PR allocation accounting.** v4's `/debt:budget` is git-
   driven, survives plugin uninstall.
3. **Engineer-perception survey loop.** Out of plugin scope.
4. **DORA outcome telemetry.** Out of plugin scope; v3 reads
   `debt/dora.json` if produced externally.
5. **Bug cap.** Out of plugin scope; lives in the issue tracker.
6. **Hook ordering across plugins.** We assume hooks are commutative.
7. **Non-git repos.** Stated up front: most of the plugin is a no-op
   without git.

---

## A day in the life (v1)

A senior engineer, mid-sized TypeScript service, `debt-ops` v0.1.0
installed. The day is intentionally smaller than what the full plugin
will eventually deliver — that's the point.

**08:50 — Open editor.** `SessionStart` fires silently: charter under
budget. Developer sees nothing.

**09:10 — Start the work.** They open a callback chain in
`pricing/engine.ts` and tell Claude to refactor it.

**09:12 — First edit lands.** `feedback.sh` runs `pnpm lint` and `tsc
--noEmit` in parallel on `pricing/engine.ts`. Both pass within 1.4 s.
Test slice is queued. The agent sees `{lint: pass, types: pass, tests:
pending}` and continues.

**09:14 — Test slice returns at next `Stop`.** Two failing tests,
unrelated to the refactor; the agent sees the failures, fixes one,
flags the other for the developer with a one-line summary.

**09:35 — A subtle expediency.** Claude proposes `// TODO: handle the
cancelled-promotion case later`. The `Stop` hook's todo-sniff sees it
and surfaces "register this with `/debt:add`?". Developer says yes;
the writer thread drafts a registry entry, fills the schema, marks
`payoff_trigger: unknown` (because it genuinely is), files
`debt/registry/0042-cancelled-promotion-callback.md`. Total time: ~30
seconds.

**11:30 — Architectural fork.** Claude wants a new pricing-event
interface. The developer manually copies `examples/adr/0001-template
.md` to `doc/adr/0007-pricing-event-interface.md` and fills it in
during a chat with Claude. (v2 will have a skill for this.)

**16:00 — Open PR.** Two registry entries created during the day, one
ADR added. The developer mentions both in the PR description.

**End of week.** They run `/debt:list` to see what's accumulated. Three
entries this week. They click through, decide which to schedule for
next sprint. (v2 will rank them; v4 will report allocation.)

The throughline: the plugin is mostly silent, fast when it's not, and
small enough that a developer doesn't have to learn it.

---

## Beyond v1 — roadmap

Each phase is shippable on its own; each adds 2–4 components, not
twenty.

### v2 — ranking + ADR + reviewer

- `/debt:adr` skill (draft from context, paired registry entry if
  deliberate debt).
- `/debt:list` ranking + filters (`--quadrant`, `--category`,
  `--stale`).
- `/debt:spec` and `/debt:explain` skills.
- Subagents: `debt-scribe` (now that drafting is multi-format),
  `triage` (ranking), `reviewer` (with comprehensibility mode).
- `Stop` hook adds ADR index regeneration.
- `PreToolUse` on `git commit` for the comprehensibility prompt.

### v3 — enforcement + paydown engine

- `feedback.sh` adds: test-integrity rule, AI-touched hotspot floor
  rule, AI-touched tagging, architectural-touch nudge. All rules
  individually disablable in `userConfig`.
- `/debt:override <reason>` skill — audit-trail escape.
- `code-health` MCP wiring (`code_health_mcp_endpoint` userConfig).
- `/debt:health` skill with `--ai-only`, `--window=30d|60d|90d`,
  `--churn=14d` flags.
- `/debt:paydown` skill + GH Actions example.
- `security-reviewer` subagent.

### v4 — allocation + Boy Scout

- `/debt:budget` (with `--fixit start|end`).
- `Stop` hook adds Boy Scout one-line summary (now that there's a
  health signal).
- `debt/dora.json` and `debt/bug-cap.json` external file readers
  surfaced in `/debt:budget`.

**Validation gate between phases.** Dogfood the previous version on
the plugin's own repo for at least one full week before promoting.
The plugin is for tech debt; if it can't manage the debt of its own
development, the design is wrong.

---

## Future possibilities (beyond v1–v4)

Items that aren't pinned to a phase but were considered and cut.
Captured here so they're not lost. None of these are committed —
they're a backlog of plausible future additions, each gated on
evidence from dogfood that the cost is justified.

### Skills considered and cut

- **`/debt:next` (separate from `/debt:list`)** — folded into v2's
  `/debt:list` ranking. Could split back out if the ranked-pickup
  workflow diverges meaningfully from the registry-browsing
  workflow.
- **`/debt:fixit-week`** — folded into v4's `/debt:budget --fixit`.
  Could split back out if fix-it weeks become frequent enough to
  warrant a dedicated entry point.
- **`/debt:charter-check`** — folded into v1's `/debt:init --check`.
  Could split out if charter health needs more than the
  `SessionStart` hook surfaces.
- **`/debt:strict-mode`** — was a session flag forcing reviewer pass
  on every change. Cut entirely. Could return as a `userConfig`
  default (`always_strict: true`) or as part of a v3 `/debt:focus`
  mode for high-stakes work.
- **`/debt:tdd`** — was a TDD output-style toggle. Cut with the
  output styles. Could return alongside an `output-styles/tdd-mode`
  if a sustained TDD discipline session proves useful in dogfood.
- **`/debt:survey`** — opens a quarterly engineer-perception survey
  template. Cut because opening a markdown file doesn't need a
  skill. Could return if the survey loop justifies in-flow
  collection (e.g., timestamping responses, aggregating, exporting).
- **`/debt:focus`** — not in any phase yet. Hypothetical mode that
  takes over the main thread for a single paydown or audit session
  with a custom system prompt, then restores. Mentioned as the only
  context where a `settings.json agent` override might be defensible.

### Subagents considered and cut

- **`adr-author`** — folded into v2's `debt-scribe` (mode arg).
  Could split out if ADR drafting and registry-entry drafting
  diverge enough that one system prompt hurts both.
- **`comprehensibility-checker`** — folded into v2's `reviewer`
  (mode arg). Could split out if comprehensibility checks need a
  different model/effort than general review.
- **`paydown-runner`** — the writer thread is the runner in v3.
  Could split out if paydown sessions benefit from a fresh context
  rather than a writer-thread mode.

### Hooks / scripts considered and cut

- **Five-hook `PostToolUse` chain** — collapsed into one
  orchestrator (`feedback.sh`) for latency. Could split apart if a
  rule grows complex enough to warrant its own hook entry.
- **`Skip-Debt-Ops:` magic-string trailer** — replaced with v3's
  `/debt:override <reason>` skill. Trailer form could return as an
  alternative path for non-interactive contexts (CI scripts).
- **AI-touched marker file (`debt/.ai-touched/<sha>`)** — v3 uses
  the existing `Co-authored-by:` trailers from Claude Code, Cursor,
  Copilot, Aider rather than maintaining our own. The marker-file
  approach could return if trailer conventions fragment.

### Other primitives

- **Background monitor `fixit-mode-watch`** — replaced by a one-line
  read in `session-start.sh`. Could return as a real monitor if
  fix-it mode needs reactivity beyond session boundaries.
- **DORA dashboard pushers** — out of plugin scope. Could return as
  a writer for `debt/dora.json` if Claude Code gains background-
  task primitives.
- **Bug-cap enforcement** — out of plugin scope; lives in the
  issue tracker. Could return as a `PreToolUse` warning if a
  reliable cross-tracker integration emerges.
- **Engineer-perception survey aggregation** — out of plugin scope.
  Could return as a thin `/debt:survey` command if `channels`
  ships and a chat-based survey workflow is desired.
- **Local hotspot scoring with tree-sitter** — the previous "lines
  × git frequency" approach was cut as misleading. A real
  complexity scorer (~20 lines of tree-sitter per language) is on
  the table if no MCP is configured and a basic behavioral signal
  is wanted.

### userConfig keys cut from v1, returning later

| Key | Returns with |
|---|---|
| `code_health_mcp_endpoint` | v3 (MCP wiring) |
| `ai_touched_min_health` (default 9.4) | v3 (AI-touched hotspot floor rule) |
| `enforce_test_integrity` | v3 (test-integrity rule) |
| `enforce_ai_hotspot_floor` | v3 (hotspot floor rule) |
| `hotspot_top_n` | v2 (ranking) or v3 (rule scope) |
| `max_pr_diff_lines` | v3 (`/debt:paydown` size cap) |
| `paydown_target_pct` | v4 (`/debt:budget` target) |

---

## Anti-patterns we will actively watch for

1. **Hook latency creep.** v1's 3 s aggregate budget is the line; CI
   on the plugin's own repo measures it.
2. **Skill explosion.** Anything <1×/week in dogfood is a removal
   candidate, not a feature flag.
3. **Charter rot in our own dogfood.** Our `CLAUDE.md`/`AGENTS.md`
   obeys its own size budget.
4. **New non-bypassable rules without an ADR.** The plugin has its
   own ADRs.
5. **Optional becoming required.** Any v3 code path that *requires*
   the MCP is a regression.
6. **Output-style or default-agent overrides masquerading as
   "convenience."** Either is a passive-plugin failure.
7. **Registry bloat without payoff triggers.** Once v2 ranking lands,
   `/debt:list --stale` surfaces these; CI fails the plugin's own
   build past a threshold.

---

## Closing

Three skills, three hooks, three scripts, zero subagents, zero MCP, no
rules, no overrides, no automation. v1 fits in fifteen minutes of
reading and earns its install on the first agent edit.

The bet: a plugin that does three small things well on day 1, grows
along documented seams when each new piece earns its weight. Silent
in success, useful in failure, additive to whatever else the
developer has installed.

If the v1 plugin disappears into the developer's workflow and they
notice it only when it caught a real mistake or registered debt
they'd otherwise have lost, the design worked.
