# Tech Debt — Claude Code Plugin Mapping & Plan

## Why this document exists

`tech-debt-pillars.md` is tool-agnostic on purpose. This document is the
opposite: it commits each pillar to one or more concrete Claude Code plugin
primitives, weighs the options, and recommends a default. The end state is
one plugin — installed once, namespaced cleanly, mostly passive — that
delivers most of the pillars' value with minimal developer effort.

**The two non-negotiables, set up front:**

1. **Lean relaxed over strict.** The system surfaces, suggests, and
   reports. It blocks only where the research demands it (test-integrity;
   AI-touched code that worsens hotspot health below a floor without an
   ADR/registry entry — Pillars 7 and 1). Everything else is a nudge or a
   skill.
2. **Passive, plays well with others.** No default `agent` override. No
   global hooks that double-up another plugin's lint or test runs. We
   detect existing project tooling and call it; we don't ship our own.
   Namespaced commands only (`/debt:*`), so naming doesn't collide.

If a design choice anywhere in this document conflicts with these two
rules, the rule wins.

**Hard prerequisite.** A git repository. Pillar 2's behavioral signal is
git history; the AI-touched discriminator is a git trailer convention.
Without git, the plugin installs but most of it is a no-op.

---

## Working name

`debt-ops` — namespaces to `/debt-ops:*`. Commands are written `/debt:*` in
this doc for brevity; the ship name is the project's call.

---

## At-a-glance mapping

| Pillar | Primary plugin pieces | Posture |
|---|---|---|
| 1. Visibility (registry + ADRs) | Skills (`/debt:add`, `/debt:adr`, `/debt:list`) · subagent (`debt-scribe`) · markdown in repo | suggest |
| 2. Continuous Measurement | Hook orchestrator (`PostToolUse`) · MCP server (code-health, optional) · skill (`/debt:health`) | observe |
| 3. Hotspot Prioritization | Skill (`/debt:list` ranks by default) · subagent (`triage`) | on-demand |
| 4. Continuous Paydown | Hook (`Stop` Boy Scout summary) · skill (`/debt:budget`, with `--fixit`) | report |
| 5. Deliberate Architecture (ADRs) | Skill (`/debt:adr`) · subagent (`debt-scribe`) · soft `PreToolUse` nudge in orchestrator | suggest |
| 6. Curated Agent Context (charter) | Skill (`/debt:init`, with `--check`) · `SessionStart` size-budget check · defers to native `CLAUDE.md` / `AGENTS.md` | augment |
| 7. In-Loop Deterministic Feedback | Hook orchestrator (`PostToolUse`, Write\|Edit) · MCP (code-health) · the **only** non-bypassable rules live here | enforce (narrow) |
| 8. Spec → Test → Review → Comprehend | Skills (`/debt:spec`, `/debt:explain`) · subagents (`reviewer`, `security-reviewer`) | opt-in mode |
| 9. AI as Paydown Engine | Skill (`/debt:paydown`) · scheduling lives **outside** the plugin (GitHub Actions / cron) | invoked |

Plus one cross-cutting skill: `/debt:override` — the audit-trail escape
hatch for the two non-bypassable rules.

The full menu of plugin primitives in the field guide is intentionally not
all used. Each one we skip is justified in §"What we don't ship."

---

## How the cross-cutting tenets become plugin choices

| Tenet | Plugin default |
|---|---|
| Continuous | One `PostToolUse` orchestrator + one `SessionStart` + one `Stop` + one `PreToolUse` (commit). Mostly silent unless something is wrong. |
| Graceful | Hooks log/comment by default. Only two rules block, both with `/debt:override <reason>` audit-trail escapes, both individually disablable via `userConfig`. |
| Evidence-based | Code-health signal comes from an MCP server (CodeScene MCP if available). If absent, the plugin uses **churn-only** ranking from `git log` — no fake complexity score. |
| Visible | Registry and ADRs are markdown in the repo. Paths configurable. |
| Deterministic | The in-loop gate runs project tooling — auto-detected, or explicit `lint_command`/`typecheck_command`/`test_command` from `userConfig`. We don't reinvent the wheel. |
| Pay down with same tool | `/debt:paydown` is first-class. Same disciplines (charter, hooks, reviewer subagent) apply to paydown runs. |

---

## The registry schema (Pillar 1, made concrete)

A registry entry is a markdown file under `${registry_path}` with YAML
front-matter. Required fields:

```yaml
---
id: 0042                              # filename prefix
title: cancelled-promotion-callback
principal: 2d                         # estimated effort to fix
interest: +30min/incident             # ongoing cost (free-form, but quantified)
hotspot: pricing/engine.ts            # path or module
business_capability: checkout         # what this affects
payoff_trigger: when promotion engine v2 lands   # may be `unknown`
quadrant: reckless-inadvertent        # one of four
category: code_quality                # one of ten (below)
ai_authored: true                     # was this debt introduced by an agent?
created: 2026-05-04
---

Free-form prose describing the debt, recurrence, and observed symptoms.
```

**The four quadrant cells (Fowler).** `reckless-inadvertent`,
`reckless-deliberate`, `prudent-inadvertent`, `prudent-deliberate`. Triage
order is the order listed.

**The ten categories (Google / Jaspan-Green).** `migration`,
`documentation`, `testing`, `code_quality`, `dead_code`, `code_rot`,
`expertise`, `release`, `infrastructure`, `planning`. Closed enum.

**`payoff_trigger: unknown` is first-class.** The pillar requires "register
debt under a minute"; demanding a trigger upfront is friction. `unknown`
ages into `/debt:list --stale` after 30 days for review.

**ADRs** live under `${adr_path}` in Nygard format with one extension —
a required `payoff_trigger` field when the ADR introduces deliberate debt.
A registry entry is auto-paired in that case (same `payoff_trigger`).

---

## Pillar-by-pillar mapping

For each pillar: requirement, two or three plausible plugin shapes, the
recommendation, and the failure mode to avoid.

### Pillar 1 — Visibility

**Requirement.** A canonical, in-repo debt registry (5-field schema) and
ADR collection that humans and agents can read/write in under a minute.

**Options.**

- **A. Markdown-in-repo registry + ADR collection.** Per-file, front-matter
  schema. Humans `git diff` it; agents read it as plain text.
- **B. Single `debt.yaml` + `adr-index.yaml`.** Compact, easier to query,
  harder to merge, requires a parser.
- **C. GitHub Issues with debt/adr labels.** Zero in-repo footprint;
  ties paydown to one forge; loses offline use.

**Recommendation: A.** Lowest friction; plays nicely with PR review;
travels with the repo (Pillar 1 explicitly says "next to the code"). B is
a fine future migration if the registry grows past a few hundred items —
the front-matter schema makes the migration mechanical.

**Plugin pieces.**

- Skills: `/debt:add`, `/debt:adr`, `/debt:list` (defaults to ranked top
  N — replaces a separate `/debt:next`).
- Subagent: `debt-scribe` — fresh-context drafter for entries, ADRs,
  specs, and explanations. Same subagent, mode-switched by argument.
- Soft nudges: the `PostToolUse` orchestrator and the `Stop` hook detect
  new `TODO`/`FIXME`/"come back to this" markers and surface
  "register this with `/debt:add`?". Never blocks.

**Failure mode.** Bloating the registry. Mitigation: `/debt:list --stale`
ages out unknown-trigger entries after 30 days for review.

---

### Pillar 2 — Continuous Measurement

**Requirement.** Static + behavioral + outcome + perception layers, with a
discriminator for AI-touched code (incident rate at 30/60/90 days; 14-day
churn).

**Options for the in-loop layer.**

- **A. Detect & delegate for static; MCP-or-nothing for behavioral.** On
  `PostToolUse`, run the repo's tooling on touched files. For hotspot /
  Code Health, if `code_health_mcp_endpoint` is set, query the MCP;
  otherwise rank by **churn only** (file change count over 90 days from
  `git log`) and tell the user the behavioral signal is unavailable until
  they wire one up.
- **B. Bundle our own static analyzers.** Heavy; reinvents the wheel;
  bound to drift.
- **C. Defer to CI.** Defeats Pillar 7 — the agent ships first, learns
  later.

**Recommendation: A.** The previous draft proposed a local "complexity ×
churn" heuristic; on second look, "lines of code × git frequency" is a
famously bad complexity proxy and would actively mislead. We commit to
honest churn-only fallback and let the team add a real MCP when they want
the better signal.

**AI-touched discriminator.** A diff is AI-touched if any of these
trailers appear in the commit: `Co-authored-by: claude-code`, `... cursor`,
`... copilot`, `... aider`, or any line matching `Co-authored-by:.*\
[bot\]`. We do not maintain our own marker; we read the conventions
already in use.

**Surfacing.** `/debt:health` accepts:

- `--ai-only` — restrict to AI-touched files.
- `--window=30d|60d|90d` — incident rate (commits whose body contains
  `fix:`, `revert:`, or that touch a file flagged in an `incidents/`
  log) on AI-touched files in the window.
- `--churn=14d` — short-term churn (lines reverted or rewritten within
  the window). Direct from GitClear's framing.

**DORA outcome layer + perception survey.** Out of plugin scope. Plugin
reads `debt/dora.json` if present and surfaces in `/debt:health`. Survey
template lives under `debt/surveys/` for teams that want it; no skill
required to open a markdown file.

**Plugin pieces.**

- Hook: `PostToolUse` orchestrator (see Pillar 7 for the full picture).
- MCP server: optional `code-health` (configured via `userConfig`).
- Skill: `/debt:health [path] [--ai-only] [--window=…] [--churn=…]`.

**Failure mode.** Hook latency. The orchestrator's aggregate budget is
3 seconds wall-clock for the lint/type slice (parallel); test slice runs
async and reports at `Stop`.

---

### Pillar 3 — Hotspot Prioritization

**Requirement.** Hotspot × business capability × Fowler quadrant ranking,
available at task pickup and refactor planning.

**Options.**

- **A. Skill-only.** `/debt:list` (no args) returns the ranked top N.
- **B. Auto-injection on `UserPromptSubmit`.** Inject hotspots whenever
  the prompt mentions "what next." Gets noisy; collides with other
  plugins.
- **C. Default agent override to a "tech-debt-pm" thread.** Hostile to
  passivity.

**Recommendation: A.** No auto-injection. Ranking is a request, not an
ambient.

**Plugin pieces.**

- Skill: `/debt:list [count]` — default behaviour returns the ranked top
  N; `--all`, `--stale`, `--quadrant=…`, `--category=…` filter the
  view. Subsumes the `/debt:next` from the previous draft.
- Subagent: `triage` — fresh-context ranker invoked by `/debt:list`;
  callable directly when the developer wants reasoning behind the rank.

**Failure mode.** The team disagreeing with the rank. Mitigation:
`/debt:list` prints the scoring formula; entries can carry `pin: true`
or `exclude: true` in front-matter.

---

### Pillar 4 — Continuous Paydown

**Requirement.** Defensible 15–20% allocation; Boy Scout baseline; fix-it
weeks; bug cap.

**Boy Scout signal.** A `Stop` hook posts a one-line summary of Code Health
delta on touched files when the session has touched any. No block.

**Allocation accounting.** `/debt:budget` walks the last N PRs, counts
those tagged `Debt-Pays-Down: <id>` in commit metadata, prints percent
vs target. The percent comes from git, not a plugin store, so it survives
plugin uninstall.

**Fix-it weeks.** `/debt:budget --fixit start` and `--fixit end` flip
`debt/.fixit-week`. Other parts of the plugin read it: `/debt:list`
weights cross-cutting items higher; `/debt:paydown` runs more
aggressively. (Folded from the previous draft's separate
`/debt:fixit-week` skill.)

**Bug cap.** Out of plugin scope; lives in the issue tracker. The plugin
reads `debt/bug-cap.json` if produced externally and warns in
`/debt:budget`.

**Plugin pieces.**

- Hook: `Stop` Boy Scout summary (one of three things the `Stop` hook
  does; see "Hook layout").
- Skill: `/debt:budget [--since=…] [--fixit start|end]`.

**Failure mode.** Allocation theater. Mitigation: `/debt:budget --since`
is the one number worth putting on a slide; the rest is for the team.

---

### Pillar 5 — Deliberate Architecture (ADRs)

**Requirement.** Architecturally significant decisions land as ADRs with
payoff triggers; agents read the ADR index before working in affected
areas.

**"Significance" detection.**

- **A. Heuristic `PreToolUse` nudge** in the orchestrator: matches on
  touches to public interface files, data models, dep manifests
  (`package.json`, `pyproject.toml`, `go.mod`), auth/crypto paths, build
  scripts, `Dockerfile`, infra (`*.tf`). Surfaces "this looks
  ADR-shaped — draft one with `/debt:adr`?". Never blocks.
- **B. Subagent-only** (no detection).
- **C. Hard pre-commit gate.** Wrong call for a relaxed system.

**Recommendation: A + skill.** Heuristic catches the obvious; the skill
is always available.

**Agent reading.** `${adr_path}/INDEX.md` is regenerated by the `Stop`
hook when an ADR changes. The charter (Pillar 6) points to it.

**Plugin pieces.**

- Skill: `/debt:adr [topic]` — scaffolds an ADR; the `debt-scribe`
  subagent fills Context from recent conversation; if the ADR introduces
  deliberate debt, a paired registry entry is auto-created with the same
  `payoff_trigger`.
- Subagent: `debt-scribe` (mode: adr).
- Heuristic nudge: lives inside the `PostToolUse` orchestrator; one rule
  among several.
- ADR index regen: lives inside the `Stop` hook.

**Failure mode.** ADRs becoming a tickbox. Mitigation: required
`payoff_trigger` field; missing or `unknown` triggers age into
`/debt:list --stale`.

---

### Pillar 6 — Curated Agent Context

**Requirement.** A short, persistent charter file agents read on every
task, with a size budget.

**Critical observation.** Claude Code already reads `CLAUDE.md` (and
`AGENTS.md`) natively. The plugin's job is bootstrap, size enforcement,
and keeping the pointer to the live ADR index fresh — nothing more.

**Charter location.** Auto-detect: if `AGENTS.md` exists, use it (broader
convention used by Cursor, Aider, others); else `CLAUDE.md`. Both can
coexist — the plugin writes one canonical file and leaves the other as a
one-line pointer if the team uses both. Override via `charter_path` in
`userConfig`.

**Plugin pieces.**

- Skill: `/debt:init` — one-time setup. Bootstraps the charter, creates
  the registry and ADR directories, drops example seeds. The `--check`
  flag re-runs the size/freshness/link checks on demand. (Subsumes the
  previous draft's separate `charter-check` skill.)
- Hook: `SessionStart` — same checks, silent unless something is wrong.

**Failure mode.** Bloated charter. Mitigation: the size warning is the
mitigation; `charter_line_budget` in `userConfig` (default 200).

---

### Pillar 7 — In-Loop Deterministic Feedback

**This is the pillar where strictness is justified.** Two non-bypassable
rules live here, both individually toggleable.

**Requirement.** Lint + type + test slice + code-health probe fired after
every meaningful agent edit, with structured results piped back.

**Approach.** One `PostToolUse` orchestrator (`feedback.sh`) on
Write|Edit|MultiEdit that runs all checks in parallel under a single 3 s
wall-clock budget for the lint/type slice; the test slice runs async and
the result is delivered at the next `Stop`. Aggregating into one
orchestrator (rather than five separate hooks) is the single most
important latency decision.

The orchestrator runs:

1. **Lint / type / test slice** — auto-detect or use explicit
   `lint_command`/`typecheck_command`/`test_command` from `userConfig`.
   Templated with `${file}`. Empty config → auto-detect; auto-detect
   failure → no-op (don't fail the agent's work for a missing tool).
2. **Test-integrity check** (rule 1; toggle:
   `enforce_test_integrity`, default true). Flags diffs that delete or
   weaken tests in the same session that added or modified production
   code those tests covered. On flag: structured rejection, with the
   suggestion to run `/debt:override <reason>` if intentional.
3. **AI-touched hotspot floor check** (rule 2; toggle:
   `enforce_ai_hotspot_floor`, default true). Flags AI-touched diffs
   that worsen Code Health on a top-N hotspot **or** drop it below
   `ai_touched_min_health` (default 9.4 — CodeScene's documented
   threshold for AI-touched code). On flag: structured rejection,
   asking for `/debt:adr` + paired registry entry, or
   `/debt:override <reason>`.
4. **AI-touched tag** — record the file path under
   `debt/.ai-touched/<commit-sha>` for later windowed analysis. Pure
   side-effect; no decision.
5. **Architectural-touch nudge** — heuristic from Pillar 5. Soft.

The previous draft separated these into five hooks; in practice that
serializes the developer experience. One orchestrator, run in parallel,
with a strict budget, is faster and easier to reason about.

**The override skill.** `/debt:override <reason>` writes an entry to
`debt/.overrides/<date>.log` and sets a one-message-scoped flag the next
hook invocation respects. Audit trail without typing magic strings.

**Plugin pieces.**

- Hook: `PostToolUse` matcher `Write|Edit|MultiEdit` → `feedback.sh`
  (the orchestrator).
- Skill: `/debt:override <reason>`.
- MCP server: optional `code-health` (Pillar 2).

**Failure mode.** Hook latency. Mitigated by the parallel-with-budget
design and the async test slice.

---

### Pillar 8 — Spec → Test → Review → Comprehend

**Requirement.** Spec for non-trivial work; TDD; fresh-context reviewer;
security reviewer; comprehensibility gate at commit time.

**Approach.** Skills + subagents only. No mandatory mode flips, no output
styles. The "TDD-first" framing is a writer-thread discipline, not a
plugin feature; if a team wants to enforce it, they add an instruction
to the charter.

**Comprehensibility gate.** `PreToolUse` hook on `Bash` matching `git
commit` checks whether AI-touched files in the staged diff exceed a
complexity-or-churn threshold; if so, surfaces "explain this in plain
English in the commit body — try `/debt:explain`." Soft.

**Reviewer pass.** `/debt:explain` and the explicit invocation of the
`reviewer` and `security-reviewer` subagents. The previous draft proposed
a `comprehensibility-checker` subagent; on second look, that role is
just a mode of `reviewer`. Folded.

**Plugin pieces.**

- Skills: `/debt:spec` (drafts a short spec, saves under
  `debt/specs/<date>-<slug>.md`), `/debt:explain` (literate
  explanation; offered to be inserted into the commit body).
- Subagents: `reviewer` (fresh-context, model: opus, effort: high,
  disallowedTools: Write|Edit; modes include comprehensibility check),
  `security-reviewer` (security-focused).
- Hook: `PreToolUse` (`Bash` matching `git commit`) — comprehensibility
  prompt. Lives inside `pre-commit.sh`.

**Failure mode.** Comprehensibility theatre. Mitigation: when invoked,
`/debt:explain` runs `reviewer` in comprehensibility mode against the
diff to flag drift.

---

### Pillar 9 — AI as a Paydown Engine

**Requirement.** Scheduled agent-driven refactor runs targeting the
prioritized hotspot list; output is a normal PR; budgeted as part of the
15–20% allocation.

**Critical observation.** Claude Code does not schedule background work.
Scheduling lives outside the plugin (GH Actions cron, external cron).
The plugin provides the *workflow*, not the *scheduler*.

**Plugin pieces.**

- Skill: `/debt:paydown [target]` — orchestrates the run: read charter,
  pick a hotspot via `/debt:list` (or the explicit target), draft a spec
  via `/debt:spec`, run the work under the in-loop hooks, hand the diff
  to `reviewer`, open a draft PR with registry/ADR cross-references.
  No new subagent — the writer thread is the runner.
- Documentation: `examples/github-actions/paydown.yml` for weekly cron.

**Failure mode.** Refactor PRs too large to review. Mitigation: soft size
budget `max_pr_diff_lines` (default 300).

---

## Plugin layout

A single repository, single plugin.

```
debt-ops/
├── .claude-plugin/
│   └── plugin.json
├── skills/
│   ├── init/SKILL.md            # /debt:init [--check]
│   ├── add/SKILL.md             # /debt:add
│   ├── adr/SKILL.md             # /debt:adr
│   ├── list/SKILL.md            # /debt:list (default: ranked top N)
│   ├── health/SKILL.md          # /debt:health
│   ├── budget/SKILL.md          # /debt:budget [--fixit start|end]
│   ├── spec/SKILL.md            # /debt:spec
│   ├── explain/SKILL.md         # /debt:explain
│   ├── paydown/SKILL.md         # /debt:paydown
│   └── override/SKILL.md        # /debt:override <reason>
├── agents/
│   ├── debt-scribe.md           # drafts entries, ADRs, specs, explanations
│   ├── triage.md                # ranks
│   ├── reviewer.md              # fresh-context review (modes: general, comprehensibility)
│   └── security-reviewer.md     # security-focused review
├── hooks/
│   └── hooks.json
├── scripts/
│   ├── feedback.sh              # PostToolUse orchestrator (Pillars 5, 7)
│   ├── session-start.sh         # SessionStart (charter check + fixit reminder)
│   ├── stop.sh                  # Stop (todo-sniff + boy-scout + adr-index)
│   └── pre-commit.sh            # PreToolUse on git commit (comprehensibility prompt)
├── .mcp.json                    # optional: code-health MCP
├── examples/
│   ├── github-actions/paydown.yml
│   └── registry/
│       ├── README.md
│       └── 0001-example-debt.md
└── README.md
```

Ten skills, four subagents, four scripts, one hooks file, optional MCP.
Down from fifteen / seven / nine in the previous draft.

**`plugin.json` highlights.**

```json
{
  "name": "debt-ops",
  "version": "0.1.0",
  "description": "Continuous, evidence-based tech debt management for Claude Code.",
  "userConfig": {
    "registry_path":         { "type": "string",  "default": "debt/registry" },
    "adr_path":              { "type": "string",  "default": "doc/adr" },
    "charter_path":          { "type": "string",  "description": "Auto-detect AGENTS.md/CLAUDE.md if empty" },
    "code_health_mcp_endpoint": { "type": "string", "required": false },
    "paydown_target_pct":    { "type": "number",  "default": 20 },
    "hotspot_top_n":         { "type": "number",  "default": 20 },
    "max_pr_diff_lines":     { "type": "number",  "default": 300 },
    "charter_line_budget":   { "type": "number",  "default": 200 },
    "ai_touched_min_health": { "type": "number",  "default": 9.4 },
    "enforce_test_integrity":  { "type": "boolean", "default": true },
    "enforce_ai_hotspot_floor": { "type": "boolean", "default": true },
    "lint_command":      { "type": "string", "description": "Templated with ${file}; empty = auto-detect" },
    "typecheck_command": { "type": "string", "description": "Templated with ${file}; empty = auto-detect" },
    "test_command":      { "type": "string", "description": "Templated with ${file}; empty = auto-detect" }
  },
  "dependencies": []
}
```

`dependencies` stays empty. The MCP is configured by URL, not declared
as a hard dep.

---

## Hook layout

Four hook entries total — fewer means clearer reasoning about latency
and ordering.

| Event | Matcher | Script | Purpose |
|---|---|---|---|
| `PostToolUse` | `Write|Edit|MultiEdit` | `feedback.sh` | lint/type/test slice (parallel, 3 s budget; tests async) · test-integrity rule · AI-touched hotspot floor rule · AI-touched tag · architectural-touch nudge |
| `SessionStart` | — | `session-start.sh` | charter size + freshness check · fix-it-week reminder |
| `Stop` | — | `stop.sh` | todo-sniff (suggest `/debt:add`) · Boy Scout one-line summary · regenerate ADR index if changed |
| `PreToolUse` | `Bash` matching `git commit` | `pre-commit.sh` | comprehensibility prompt for AI-touched + complex diffs |

Outputs are structured JSON tool results when the hook needs the agent
to respond; one-line text when it's a developer-facing nudge.

---

## What we don't ship (and why)

| Primitive | Decision | Reason |
|---|---|---|
| `commands/` (legacy flat) | skip | Skills are the recommended replacement. |
| `themes/` | skip | Out of scope. |
| `bin/` | skip | No script earns broader use at v0.1. |
| `.lsp.json` | skip | Anthropic ships LSP plugins for the major languages. |
| `output-styles/` | skip | The previous draft included `tdd-mode` and `paydown-aware`; both were nudges dressed as styles. Removed. |
| `monitors/` | skip | Previous draft had `fixit-mode-watch`. The same job is one line in `session-start.sh`. |
| `channels` | skip | No external messaging in core flow. |
| `settings.json` `agent` override | skip | Hostile to other plugins. |
| Subagent `hooks`/`mcpServers`/`permissionMode` | n/a | Disallowed for plugin-shipped agents. |
| Local complexity scorer | skip | "LoC × git frequency" is a misleading complexity proxy. Use churn-only honestly; require an MCP for real Code Health. |

---

## How we coexist with other plugins

1. **Namespace everything.** All commands `/debt-ops:*`. No short-alias
   land-grabs.
2. **No global `agent`.** We never set `settings.json` `agent`.
3. **Hooks call project tooling, don't replace it.** `feedback.sh` runs
   the project's eslint (or whatever); doesn't shadow another plugin's
   hook.
4. **MCP is optional.** Teams without a code-health MCP are first-class.
5. **Charter respects ownership.** `CLAUDE.md` / `AGENTS.md` is the
   project's; we seed once on `/debt:init`; never overwrite on update.
6. **Multi-tool AI-touched detection.** We read existing
   `Co-authored-by:` trailers from Claude Code, Cursor, Copilot, Aider
   rather than maintaining our own marker.
7. **Per-rule disable.** `enforce_test_integrity` and
   `enforce_ai_hotspot_floor` toggle independently in `userConfig`.
8. **Override skill, not magic strings.** `/debt:override <reason>`.

---

## Gaps in Claude Code primitives (honest list)

1. **Cron / scheduling.** Pillar 9 needs an external scheduler. GH
   Actions recipe shipped in `examples/`.
2. **Cross-PR allocation accounting.** `/debt:budget` is git-driven, not
   session-driven. Fine — survives plugin uninstall.
3. **Engineer-perception survey loop.** Out of plugin scope; teams put a
   markdown template under `debt/surveys/` if they want.
4. **DORA outcome telemetry.** Out of plugin scope; reads
   `debt/dora.json` if produced externally.
5. **Bug cap.** Out of plugin scope; lives in the issue tracker.
6. **Hook ordering across plugins.** We assume hooks are commutative.
7. **Non-git repos.** Stated up-front: most of the plugin is a no-op
   without git. We don't pretend otherwise.

---

## A day in the life

A senior engineer, mid-sized TypeScript service, `debt-ops` installed.

**08:50 — Open editor.** `SessionStart` fires silently: charter under
budget, ADR index up to date, no fix-it-week. Developer sees nothing.

**09:10 — "What should I look at today?"** They type `/debt:list 5`. The
`triage` subagent returns five ranked items with the scoring formula
printed at the bottom.

**09:20 — Start the work.** They pick the top item — callback hell in
`pricing/engine.ts`.

**09:22 — First edit lands.** `feedback.sh` orchestrator runs in parallel:
- lint/types pass (within the 3 s budget; tests slice queued async).
- test-integrity: no test deletions. ✓
- AI-touched hotspot floor: 7.6, above 7.4 prior, above floor. ✓ (no
  rejection)
- AI-touched tag recorded.
- Architectural-touch nudge: file isn't an interface; no nudge.
The agent sees `{lint: pass, types: pass, integrity: pass, health: +0.2}`
and continues. Async test result lands at the next `Stop`.

**09:35 — A subtle expediency.** Claude proposes `// TODO: handle the
cancelled-promotion case later`. The `Stop` hook's todo-sniff sees it
and surfaces "register this with `/debt:add`?". Developer says yes;
`debt-scribe` drafts the entry from context. Payoff trigger isn't
obvious; the scribe writes `payoff_trigger: unknown` and notes the
entry will age into `--stale` review.

**10:00 — Architectural fork.** Claude wants a new pricing-event
interface. The orchestrator's architectural nudge fires on
`interfaces/pricing-events.ts`. Developer runs `/debt:adr "pricing
event interface"`. `debt-scribe` (mode: adr) drafts Context / Decision /
Consequences / Alternatives / Payoff trigger from the conversation;
developer edits and commits the ADR alongside the code.

**10:30 — A near-miss.** Claude tries to delete a test that was failing
because of the new interface signature. `feedback.sh` rule 1 fires: the
tool result is a structured rejection. The agent reads it, rewrites the
test to match the new signature instead of deleting it, and continues.
The developer never sees the diff.

**11:30 — Commit time.** AI-touched, complexity bumped. `pre-commit.sh`
surfaces a soft prompt: "explain this — try `/debt:explain`." Skill
runs, writes an explanation; developer edits one sentence; commits.

**13:00 — Auth code.** Developer explicitly invokes `/debt:explain` and
asks for `security-reviewer` on the next change. The reviewer flags an
unsanitized header read; the agent fixes it.

**15:30 — Boy Scout.** `Stop` posts: "Files touched: pricing/engine.ts
(7.4→7.6), pricing/types.ts (8.1→8.1), interfaces/pricing-events.ts
(new, 9.0). Net Code Health: +0.2."

**16:00 — Open PR.** PR description includes registry entries created,
ADRs added, Code Health delta. Trailer: `Debt-Pays-Down: 0042`.

**Friday — Allocation review.** `/debt:budget --since=monday`:
allocation 16% vs target 20%; top three uncovered hotspots.

**Sunday 02:00 — No human.** GH Actions cron runs `claude … -p
"/debt:paydown"`. The skill picks the top hotspot, drafts a spec, runs
the work under the same hooks (rule 2 forces the AI-touched code to
stay above 9.4 or pair an ADR), hands to `reviewer`, opens a draft PR.
Monday morning the developer reviews it like any other PR.

The throughline: silent in the success case, useful in the failure
case.

---

## Roadmap (lean)

Smaller phases than the previous draft. Each is shippable and
dogfoodable on its own.

### Phase 1 — Visibility + minimal in-loop feedback

Absolute minimum.

- `/debt:init`, `/debt:add`, `/debt:list`.
- Subagent: `debt-scribe`.
- Hook: `PostToolUse` orchestrator with **only** lint/type/test slice +
  AI-touched tag (no rules enforced yet).
- Hook: `SessionStart` charter check.
- Hook: `Stop` todo-sniff.

Pillars partially live: 1, 2 (static), 6, 7 (lite). Ships in days, not
weeks. Validates the hook-orchestrator latency claim before we add more
to it.

### Phase 2 — ADRs, ranking, comprehensibility

- `/debt:adr`, `/debt:explain`, `/debt:spec`, `/debt:list` ranking via
  `triage` subagent.
- Subagents: `triage`, `reviewer`.
- Add to orchestrator: architectural-touch nudge.
- Add `Stop` hook: ADR index regen, Boy Scout summary.
- Add `PreToolUse` hook: `pre-commit.sh` comprehensibility prompt.

Pillars now substantially live: 1, 3, 5, 6, 8.

### Phase 3 — Enforcement + paydown

- `/debt:override`.
- Add to orchestrator: rules 1 and 2 (test-integrity, AI-touched
  hotspot floor) — both togglable, default on.
- `/debt:paydown` skill.
- `security-reviewer` subagent.
- Optional MCP wiring.

Pillars 4, 7 (full), 9 live.

### Phase 4 — Allocation

- `/debt:budget` (with `--fixit`).
- Boy Scout summary already wired in Phase 2.
- DORA / bug-cap external file readers if any team produces them.

Validation gate between phases: dogfood for one week on the plugin's
own repo before promoting.

---

## Anti-patterns we will actively watch for

1. **Hook latency creep.** Aggregate budget is 3 s for lint/type. CI on
   the plugin's repo measures it.
2. **Skill explosion.** Anything <1×/week in dogfood is a removal
   candidate.
3. **Charter rot in the plugin's own dogfood.** The plugin's
   `CLAUDE.md` must obey its own size budget.
4. **New non-bypassable rules without an ADR.** The plugin has its own
   ADRs.
5. **External-dep drift.** `code-health` MCP is optional; any code path
   that requires it is a regression.
6. **Output-style or default-agent overrides masquerading as
   "convenience."** Either is a passive-plugin failure.
7. **Registry bloat without payoff triggers.** `/debt:list --stale`
   surfaces these; CI fails its own build past a threshold of stale
   entries.

---

## Closing

Nine pillars, one plugin, ten skills, four subagents, four hooks, one
optional MCP, two non-bypassable rules with audit-trail overrides,
zero overrides of the user's main agent.

The bet: most days, a developer shouldn't notice the plugin is
running. They should notice when (a) they ask it something, or (b) a
deterministic gate catches a real mistake the agent was about to make.
Silent in success, useful in failure.

If, six months in, developers describe it as "the thing that keeps our
debt visible without getting in our way," the design worked. If they
describe it as "another wall," it didn't.
