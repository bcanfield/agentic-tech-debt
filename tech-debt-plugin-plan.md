# Tech Debt — Claude Code Plugin Mapping & Plan

## Why this document exists

`tech-debt-pillars.md` is tool-agnostic on purpose. This document is the
opposite: it commits each pillar to one or more concrete Claude Code plugin
primitives (skills, subagents, hooks, MCP, monitors, output styles,
settings, userConfig, marketplace), weighs the options, and recommends a
default. The end state is one plugin — installed once, namespaced cleanly,
mostly passive — that delivers most of the pillars' value with minimal
developer effort.

**The two non-negotiables, set up front:**

1. **Lean relaxed over strict.** The system surfaces, suggests, and
   reports. It blocks only where the research demands it (test-integrity;
   AI-touched code that worsens hotspot health without an ADR/registry
   entry — Pillars 7 and 1). Everything else is a nudge or a skill.
2. **Passive, plays well with others.** No default `agent` override. No
   global hooks that double-up another plugin's lint or test runs. We
   detect existing project tooling and call it; we don't ship our own.
   Namespaced commands only (`/debt:*`), so naming doesn't collide.

If a design choice anywhere in this document conflicts with these two
rules, the rule wins.

---

## Working name

`debt-ops` — short enough to type, long enough to be unambiguous, namespaces
to `/debt-ops:*`. Falls back to a shorter alias `/debt:*` only if Claude
Code gains alias support; otherwise we go with `/debt-ops:*` from day one
and avoid bikeshedding.

For the rest of this document, commands are written `/debt:*` for brevity.
The actual ship name is the project's call.

---

## At-a-glance mapping

| Pillar | Primary plugin pieces | Posture |
|---|---|---|
| 1. Visibility (registry + ADRs) | Skills (`/debt:add`, `/debt:adr`, `/debt:list`) · subagents (`debt-scribe`, `adr-author`) · markdown registry in repo | suggest |
| 2. Continuous Measurement | Hooks (`PostToolUse`) · MCP server (code-health, optional dep) · skill (`/debt:health`) | observe |
| 3. Hotspot Prioritization | Skill (`/debt:next`) · subagent (`triage`) · MCP query | on-demand |
| 4. Continuous Paydown | Hooks (Boy Scout delta on PR) · skill (`/debt:budget`) · output style ("paydown reminder") | report |
| 5. Deliberate Architecture (ADRs) | Skill (`/debt:adr`) · subagent (`adr-author`) · soft `PreToolUse` nudge | suggest |
| 6. Curated Agent Context (charter) | Skill (`/debt:charter-init`) · `SessionStart` size-budget check · doc-only — defer to native CLAUDE.md | augment |
| 7. In-Loop Deterministic Feedback | Hooks (`PostToolUse` matcher Write\|Edit) · MCP (code-health) · the **only** non-bypassable rules live here | enforce (narrow) |
| 8. Spec → Test → Review → Comprehend | Skills (`/debt:spec`, `/debt:tdd`, `/debt:explain`) · subagents (`reviewer`, `security-reviewer`, `comprehensibility-checker`) · output style | opt-in mode |
| 9. AI as Paydown Engine | Skill (`/debt:paydown`) · subagent (`paydown-runner`) · scheduling lives **outside** the plugin (GitHub Actions / cron) | invoked |

The full menu of plugin primitives in the field guide is intentionally not
all used. Each one we skip is justified in §"What we don't ship."

---

## How the cross-cutting tenets become plugin choices

The pillars doc lists six tenets (continuous, graceful, evidence-based,
visible, deterministic, paydown-with-same-tool). They translate to plugin
defaults as follows.

| Tenet | Plugin default |
|---|---|
| Continuous | Hooks fire on `PostToolUse` and `SessionStart`. Most output is asynchronous and silent unless something is wrong. |
| Graceful | Hooks log/comment by default. Only two hooks block: test-deletion guard and AI-touched-hotspot-health-regression guard. Everything else is a soft nudge or a skill. |
| Evidence-based | Code-health signal comes from an MCP server (CodeScene MCP if available; otherwise a small local hotspot scorer based on `git log` × cyclomatic-ish heuristic). Numbers, not vibes. |
| Visible | Registry and ADRs are markdown in the repo (`debt/` and `doc/adr/`). No DB, no external dashboard, no SaaS dependency for the core flow. |
| Deterministic | The in-loop gate runs project tooling (eslint, ruff, mypy, pytest, etc.) — whatever the repo already has — and reports structured results to the agent. We don't reinvent the wheel; we wire the existing wheel into the agent's loop. |
| Pay down with same tool | `/debt:paydown` and the `paydown-runner` subagent are first-class, not afterthoughts. The same disciplines (charter, hooks, reviewer subagent) apply to paydown runs. |

---

## Pillar-by-pillar mapping

For each pillar: the requirement, two or three plausible plugin shapes, the
recommendation, and the failure mode to avoid.

### Pillar 1 — Visibility

**Requirement.** A canonical, in-repo debt registry (5-field schema) and
ADR collection that humans and agents can read/write in under a minute,
ideally from the place the debt is observed.

**Options.**

- **A. Markdown-in-repo registry (`debt/registry/*.md`) + `doc/adr/*.md`.** One
  file per item. Front-matter holds the five fields plus quadrant cell and
  category. Humans `git diff` it; agents read it as plain text.
- **B. Single `debt.yaml` + `adr-index.yaml`.** One file, parsed by a small
  bundled binary. More compact, easier to query, harder to merge.
- **C. GitHub Issues with debt/adr labels.** Zero in-repo footprint;
  travels with GitHub, not the repo. Loses offline use; ties paydown to
  one forge.

**Recommendation: A.** Per-file markdown is the lowest-friction format for
both humans and agents, plays nicely with PR review, has no parser, and
travels with the repo (Pillar 1 explicitly says "next to the code").
Option B is a fine future migration if the registry grows past a few
hundred items; the schema (front-matter) makes that migration mechanical.

**Plugin pieces.**

- Skills: `/debt:add` (creates a registry entry from current context),
  `/debt:adr` (scaffolds an ADR), `/debt:list` (queries the registry by
  hotspot/quadrant/age).
- Subagents: `debt-scribe` (drafts the entry from a chat context, fills the
  five fields, asks for the missing one), `adr-author` (drafts an ADR with
  Context/Decision/Consequences/Payoff-trigger).
- Hook: `Stop` matcher detects new `TODO`, `FIXME`, `XXX`, "I'll come back
  to this," "expedient" in the assistant's last turn or in the diff;
  surfaces a one-line "register this?" suggestion. Never blocks.
- Hook: `PreToolUse` matcher on `Bash` for `git commit` scans the staged
  diff for the same markers; same one-line suggestion. Never blocks.

**Failure mode.** Bloating the registry. Mitigation: the `debt-scribe`
subagent must produce entries with payoff triggers; entries without one
are flagged in `/debt:list --stale`.

---

### Pillar 2 — Continuous Measurement

**Requirement.** Static + behavioral + outcome + perception layers, with a
discriminator for AI-touched code.

**Options for the in-loop measurement layer (static + behavioral).**

- **A. Detect & delegate.** On `PostToolUse` after Write/Edit, detect the
  repo's tooling (`package.json` scripts, `pyproject.toml`, `Makefile`,
  `.golangci.yml`, etc.) and run the matching `lint`/`typecheck`/`test`
  target on touched files. Hotspot signal comes from `git log --follow`
  on the touched files plus a small complexity heuristic (LoC × file
  churn over 90d).
- **B. Bundle our own.** Ship eslint/ruff/mypy/etc. wrappers in `bin/`.
  Heavy, redundant with project tooling, bound to drift.
- **C. Depend on CodeScene CodeHealth MCP.** Best signal. Adds a paid
  external dependency. Good for teams that already pay for CodeScene.

**Recommendation: A as default, C as optional dep.** `userConfig` exposes
a `code_health_mcp_endpoint` so a team that has CodeScene (or a similar
service) can wire it in; if absent, the plugin falls back to its local
hotspot scorer. The local scorer is intentionally small — `git log --since
=90.days --name-only` × a `wc -l` proxy is enough to be useful and won't
mislead anyone into thinking it's CodeScene.

**Outcome layer (DORA).** Out of plugin scope. The plugin reads a
`debt/dora.json` file if present (produced by an external pipeline) and
surfaces the numbers in `/debt:health`; we do not pretend to compute DORA
from inside Claude Code.

**Perception layer (quarterly survey).** Out of plugin scope. The plugin
ships a survey template under `debt/surveys/template.md` and a
`/debt:survey` skill that opens a new dated copy, but the actual sending
is the team's job.

**AI-touched code discriminator.** A `PostToolUse` hook tags every
agent-written diff with a marker file (`debt/.ai-touched/<commit-sha>`)
plus a git trailer (`Co-authored-by: claude-code <noreply@anthropic.com>`
already exists for many setups). `/debt:health --ai-only` filters to those
files. This is a thin convention, not a system.

**Plugin pieces.**

- Hooks: `PostToolUse` (Write|Edit) → run detected lint/type/test on touched
  paths; report inline. `PostToolUse` (Write|Edit) → tag AI-touched files.
- MCP server: optional `code-health` server (configured via `userConfig`).
- Skill: `/debt:health [path]` — show static + hotspot for the path or
  the touched set; honors `--ai-only`.

**Failure mode.** The hook becoming slow enough to annoy the developer.
Mitigation: only run on the touched file's affected slice (e.g., `eslint
$file`, `pytest -k <module>` rather than full suite); fall back to
"deferred" mode that reports at `Stop` if the slice isn't quick.

---

### Pillar 3 — Hotspot Prioritization

**Requirement.** A ranking that combines hotspot score × business
capability impact × Fowler quadrant cell, available at sprint planning,
task pickup, and refactor planning.

**Options.**

- **A. Skill-only.** `/debt:next` queries the registry + hotspot scorer
  and prints a ranked list.
- **B. Skill + auto-injection.** Inject the top-3 hotspots on
  `UserPromptSubmit` whenever the prompt contains "what next," "pick a
  task," "tech debt," etc.
- **C. Default agent override.** Make a `tech-debt-pm` subagent the main
  thread. Aggressive — violates "passive."

**Recommendation: A.** Auto-injection (B) sounds clever but quickly turns
into noise that other plugins also want to inject; the result is a
context window crowded with snippets nobody asked for. C is straightforwardly
wrong for a passive plugin.

**Plugin pieces.**

- Skill: `/debt:next [count]` — ranked list with the three signals.
- Subagent: `triage` — fresh-context ranker invoked by the skill; can
  also be called explicitly.

**Failure mode.** Picking favorites that the team disagrees with.
Mitigation: the skill prints its scoring formula at the bottom, and the
team can pin/exclude items via front-matter (`pin: true`, `exclude: true`)
in the registry entry.

---

### Pillar 4 — Continuous Paydown

**Requirement.** Defensible 15–20% allocation, Boy Scout baseline, fix-it
weeks, bug cap.

**Options for the Boy Scout signal.**

- **A. Soft report at PR / `Stop` time.** Post a comment summarizing the
  Code Health delta on touched files. Doesn't block.
- **B. Hard gate at commit time.** Block commit if Code Health worsens
  on hotspots. Strict; forces a registry entry / ADR.
- **C. PR-only, no in-session signal.** Defer entirely to CI.

**Recommendation: A by default, with B opt-in for hotspots only.** Pillar 7
already specifies a non-bypassable rule for *AI-touched* hotspot
regressions, which is the strict piece. For human-authored code, the
research is clear that punitive gating loses; A is the relaxed default.

**Allocation accounting.** A skill, not a hook. `/debt:budget` walks the
last N PRs, counts how many were `debt`-tagged in commit metadata
(trailer: `Debt-Pays-Down: <registry-id>`), and prints the percent vs the
configured target.

**Bug cap.** Out of plugin scope; lives in the team's issue tracker.
The plugin can read a `debt/bug-cap.json` if produced externally and warn
in `/debt:budget`.

**Plugin pieces.**

- Hook: `Stop` — if the session touched files, summarize Code Health
  delta in a single line.
- Skill: `/debt:budget` — paydown allocation report.
- Skill: `/debt:fixit-week start|end` — flips a flag file
  (`debt/.fixit-week`) that other parts of the plugin read (e.g.,
  `/debt:next` weights cross-cutting items higher; `paydown-runner` runs
  more aggressively).
- Output style: `paydown-aware` — terse reminder of touched-files Code
  Health on each turn. Optional; off by default.

**Failure mode.** Allocation theater — numbers reported, never acted on.
Mitigation: `/debt:budget --since` is the only thing the plugin asks the
plugin author to put on a slide; the rest is for the team.

---

### Pillar 5 — Deliberate Architecture (ADRs)

**Requirement.** Every architecturally significant decision (human or
agent) lands as an ADR with payoff trigger; agents read the ADR index
before working in affected areas.

**Options for "significance" detection.**

- **A. Heuristic `PreToolUse` nudge.** Match on touches to public
  interface files, data models, dep-manager files (`package.json`,
  `pyproject.toml`, `go.mod`), auth / crypto paths, build scripts,
  `Dockerfile`, infra (`*.tf`). On match, the assistant surfaces a soft
  "this looks ADR-shaped — draft one with `/debt:adr`?" message. Never
  blocks.
- **B. Subagent-only.** No detection; the developer or assistant invokes
  `/debt:adr` when they think they should.
- **C. Hard pre-commit gate.** Block commits to those paths without an
  ADR. Strict; exactly the kind of thing developers route around.

**Recommendation: A + B.** The heuristic matcher catches the obvious
cases; the skill is always available. Hard gating (C) is the wrong call
for a relaxed system.

**Agent reading.** The plugin maintains `doc/adr/INDEX.md` (auto-generated
by a `Stop` hook when an ADR is added/changed). The charter (Pillar 6)
points to it. Agents read the index, then drill into specific ADRs as
needed.

**Plugin pieces.**

- Skill: `/debt:adr [topic]` — scaffolds an ADR, populates Context from
  recent conversation, asks for Decision and Consequences, prompts for a
  Payoff trigger if the ADR introduces deliberate debt; auto-creates a
  paired registry entry if so.
- Subagent: `adr-author` — fresh-context drafter.
- Hook: `PreToolUse` (Write|Edit) — heuristic nudge on architectural paths.
- Hook: `Stop` — regenerate `doc/adr/INDEX.md` if any ADR changed in the
  session.

**Failure mode.** ADRs becoming a tickbox. Mitigation: the template's
Payoff trigger field is required; entries without it are surfaced by
`/debt:list --stale`.

---

### Pillar 6 — Curated Agent Context (charter)

**Requirement.** A short, persistent charter file agents read on every
task, with a size budget.

**Critical observation.** Claude Code already reads `CLAUDE.md` (and
`AGENTS.md`) natively. We do **not** want to ship a competing charter
mechanism. The plugin's job is to (a) bootstrap a good initial charter,
(b) enforce the size budget, (c) keep the charter pointing at the live
ADR index and registry.

**Options.**

- **A. Bootstrap + size-budget hook.** Skill seeds `CLAUDE.md` with a
  template; `SessionStart` hook warns (not blocks) if the charter exceeds
  the budget (default: 200 lines / ~4KB).
- **B. Plugin owns a separate `debt/CHARTER.md` it reads on session
  start.** Duplicates CLAUDE.md and confuses other plugins.
- **C. Replace CLAUDE.md.** Hostile to other plugins, breaks existing
  conventions. Wrong.

**Recommendation: A.** Smallest footprint; respects what Claude Code
already does; provides the missing piece (size enforcement, charter
freshness, charter→ADR-index link).

**Plugin pieces.**

- Skill: `/debt:charter-init` — write the template if `CLAUDE.md` doesn't
  exist; otherwise show a diff for review. Template includes the section
  list mandated by Pillar 6 (stack, build/test/run, conventions, no-touch
  zones, ADR/registry pointers, escalation rules).
- Skill: `/debt:charter-check` — explicit on-demand check for budget,
  staleness (mtime > N days), broken ADR index links.
- Hook: `SessionStart` — same checks, silent unless something is wrong;
  one-line warning if so.

**Failure mode.** Bloated charter. The size-budget warning is exactly
the mitigation; if developers ignore it, no plugin saves them.

---

### Pillar 7 — In-Loop Deterministic Feedback

**This is the pillar where strictness is justified.** Two non-bypassable
rules live here. Everything else gates softly.

**Requirement.** Formatter, linter, type checker, affected test slice,
code-health probe — fired after every meaningful agent edit, with results
piped back to the agent in a structured form.

**Options.**

- **A. One generic `PostToolUse` hook that detects project tooling and
  runs it on touched files.** Default and recommended.
- **B. Per-language hooks shipped in the plugin.** Heavy; reinvents
  detection.
- **C. Defer entirely to CI.** Defeats the pillar — the agent ships and
  *then* finds out.

**Recommendation: A.** A small bash script (`hooks/feedback.sh`) reads the
hook event JSON, finds the project's `lint`/`typecheck`/`test` targets,
runs the slice, returns structured JSON. If no project tooling is
configured, the hook is a no-op rather than a noisy failure.

**The two non-bypassable rules.**

1. **Test-integrity guard.** A `PostToolUse` hook on Write|Edit checks
   whether the diff *deletes or weakens* tests in the same session that
   added or modified production code those tests covered. If yes, the
   tool result is a structured rejection, surfaced to the agent. The
   developer can override by adding the trailer
   `Skip-Debt-Ops: tests-rewritten` to the next message — but the
   override leaves a paper trail.
2. **AI-touched hotspot regression guard.** A `PostToolUse` hook checks
   whether an AI-tagged diff worsened Code Health on a file in the top-N
   hotspot list. If yes and there is no paired registry entry / ADR, the
   tool result is a structured rejection asking for one. Same override
   trailer mechanism.

Both rules are derived directly from the pillars doc (Pillar 7 +
Pillar 1). Both have an explicit, auditable override. Both fail closed
in the agent's loop, not the developer's terminal — the developer is
never personally blocked.

**Plugin pieces.**

- Hook: `PostToolUse` matcher `Write|Edit|MultiEdit` → `feedback.sh`
  (lint + type + test slice).
- Hook: `PostToolUse` matcher `Write|Edit|MultiEdit` → `test-integrity.sh`
  (rule 1).
- Hook: `PostToolUse` matcher `Write|Edit|MultiEdit` → `hotspot-guard.sh`
  (rule 2).
- MCP server: `code-health` (optional dep; falls back to local scorer).
- Output: structured JSON in tool result, not free text, so the agent
  reliably acts on it.

**Failure mode.** Hook latency. Mitigation: each script has a hard
2-second budget for the lint/type slice, 10-second for the test slice;
overruns push the result to the next `Stop` rather than blocking the
edit.

---

### Pillar 8 — Spec → Test → Review → Comprehend

**Requirement.** Spec for non-trivial work, TDD, fresh-context reviewer,
security reviewer, comprehensibility gate at commit time.

**Options for the writer/reviewer split.**

- **A. Skills + subagents.** `/debt:spec`, `/debt:tdd`, `/debt:explain`
  are explicit; the reviewer agents are invoked at the end of a task by
  the writer or the developer.
- **B. Hook-driven mandatory review.** Every agent-written commit must
  pass through `reviewer` and `security-reviewer` subagents
  automatically. Strict; useful but slow.
- **C. Default agent override to a "spec-mode" agent.** Hostile to other
  plugins; locks the user in.

**Recommendation: A as default; B available as `/debt:strict-mode`.**
The pillars doc says "non-trivial agent work" — that judgment call should
live with the developer, not be coerced. The strict mode is one skill
invocation away when the work warrants it.

**Comprehensibility gate.** A `PreToolUse` matcher on `Bash` for
`git commit` (when AI-touched files are part of the commit and exceed
a complexity-or-churn threshold) appends a one-line prompt to the
assistant: "you wrote this; explain it in plain English in the commit
body." Soft; no block.

**Security review.** Specialized subagent triggered by file paths
(auth, secrets, input handling, dependency manifests). Same shape as
`reviewer`, different system prompt.

**Plugin pieces.**

- Skills: `/debt:spec` (drafts a short spec for the current task and
  saves it under `debt/specs/<date>-<slug>.md`), `/debt:tdd` (toggles a
  session-scoped output style biasing toward failing-test-first),
  `/debt:explain` (produces a literate explanation of the current diff
  and saves it in the commit body or a sibling `.md`).
- Subagents: `reviewer` (fresh context, model: opus, effort: high,
  disallowedTools: Write|Edit), `security-reviewer` (same shape,
  security-focused system prompt), `comprehensibility-checker`
  (checks the explanation matches the diff).
- Hook: `PreToolUse` (`Bash` matching `git commit`) — comprehensibility
  prompt. Soft.
- Output style: `tdd-mode` (toggled by `/debt:tdd`).

**Failure mode.** Comprehensibility theatre — the assistant writes a
plausible explanation that doesn't match the code. Mitigation: the
`comprehensibility-checker` subagent reviews the explanation against the
diff and flags drift; the human still signs off, but with assistance.

---

### Pillar 9 — AI as a Paydown Engine

**Requirement.** Scheduled agent-driven refactor runs; targets drawn from
the prioritized hotspot list; output is a normal PR; budgeted as part of
the 15–20% allocation.

**Critical observation.** Claude Code itself does not schedule
background work. Pillar 9's "scheduling mechanism" lives outside the
plugin — typically GitHub Actions calling `claude` in a workflow, or an
external cron. The plugin provides the *workflow*, not the *scheduler*.

**Options for the in-session paydown workflow.**

- **A. Skill + subagent.** `/debt:paydown [target]` runs a paydown
  session: read the charter, pick a hotspot from `/debt:next` (or
  the explicit target), draft a spec, run TDD, hand to `reviewer`,
  open a PR.
- **B. Always-on background monitor that auto-files refactor PRs.** Too
  aggressive for a passive plugin. Possible later, gated behind explicit
  config.
- **C. Manual orchestration only.** No new skill; just document.
  Underwhelming.

**Recommendation: A.** The skill is the unit of work. External
scheduling (GH Actions cron) calls `claude --plugin-dir … -p
"/debt:paydown"` as a oneshot. We document the Actions recipe; we don't
ship a custom orchestrator.

**Plugin pieces.**

- Skill: `/debt:paydown [target]` — orchestrates the run; honors strict
  mode; opens a draft PR with the registry/ADR cross-references in the
  body.
- Subagent: `paydown-runner` — fresh-context refactor agent, calls
  `reviewer` and `security-reviewer` before claiming done.
- Background monitor (optional, off by default): `fixit-mode-watch` —
  reads `debt/.fixit-week` and surfaces a once-per-session reminder.
- Documentation: `examples/github-actions/paydown.yml` — recipe for
  weekly cron.

**Failure mode.** Refactor PRs that are too large to review. Mitigation:
the `paydown-runner` system prompt enforces a soft size budget (≤300
lines diff per PR by default; configurable via `userConfig`).

---

## Plugin layout

A single repository, single plugin. We resist splitting into a
marketplace of micro-plugins because every pillar above expects the
others to be present.

```
debt-ops/
├── .claude-plugin/
│   └── plugin.json
├── skills/
│   ├── add/SKILL.md            # /debt:add
│   ├── adr/SKILL.md            # /debt:adr
│   ├── list/SKILL.md           # /debt:list
│   ├── next/SKILL.md           # /debt:next
│   ├── health/SKILL.md         # /debt:health
│   ├── budget/SKILL.md         # /debt:budget
│   ├── charter-init/SKILL.md
│   ├── charter-check/SKILL.md
│   ├── spec/SKILL.md
│   ├── tdd/SKILL.md
│   ├── explain/SKILL.md
│   ├── paydown/SKILL.md
│   ├── strict-mode/SKILL.md
│   ├── fixit-week/SKILL.md
│   └── survey/SKILL.md
├── agents/
│   ├── debt-scribe.md
│   ├── adr-author.md
│   ├── triage.md
│   ├── reviewer.md
│   ├── security-reviewer.md
│   ├── comprehensibility-checker.md
│   └── paydown-runner.md
├── hooks/
│   └── hooks.json
├── scripts/
│   ├── feedback.sh             # Pillar 7: lint/type/test slice
│   ├── test-integrity.sh       # Pillar 7: rule 1
│   ├── hotspot-guard.sh        # Pillar 7: rule 2
│   ├── todo-sniff.sh           # Pillar 1: detect "I'll come back"
│   ├── adr-detect.sh           # Pillar 5: architectural-touch heuristic
│   ├── adr-index.sh            # Pillar 5: regenerate doc/adr/INDEX.md
│   ├── charter-check.sh        # Pillar 6: size budget
│   ├── ai-touched-tag.sh       # Pillar 2: discriminator
│   └── hotspot-score.sh        # local fallback for Pillar 2
├── output-styles/
│   ├── tdd-mode.md
│   └── paydown-aware.md
├── monitors/
│   └── monitors.json           # fixit-mode-watch (optional)
├── .mcp.json                   # optional: code-health MCP
├── examples/
│   ├── github-actions/paydown.yml
│   └── registry/
│       ├── README.md
│       └── 0001-example-debt.md
└── README.md
```

**`plugin.json` highlights.**

```json
{
  "name": "debt-ops",
  "version": "0.1.0",
  "description": "Continuous, evidence-based tech debt management for Claude Code.",
  "userConfig": {
    "code_health_mcp_endpoint": {
      "type": "string",
      "title": "Code-health MCP endpoint",
      "description": "Optional. If unset, falls back to local hotspot scorer.",
      "required": false
    },
    "paydown_target_pct": {
      "type": "number",
      "title": "Paydown allocation target (%)",
      "default": 20
    },
    "hotspot_top_n": {
      "type": "number",
      "title": "Hotspot watch list size",
      "default": 20
    },
    "max_pr_diff_lines": {
      "type": "number",
      "title": "Soft size cap on paydown PRs",
      "default": 300
    },
    "charter_line_budget": {
      "type": "number",
      "title": "CLAUDE.md size budget (lines)",
      "default": 200
    }
  },
  "dependencies": []
}
```

We deliberately leave `dependencies` empty. The CodeScene MCP is
configured via `userConfig`, not declared as a hard dep, so the plugin
installs cleanly for teams that don't have it.

---

## What we don't ship (and why)

| Primitive | Decision | Reason |
|---|---|---|
| `commands/` (legacy flat) | skip | Skills are the recommended replacement and support supporting files. |
| `themes/` | skip | Out of scope for tech debt; would just dilute the plugin. |
| `bin/` | maybe | Not needed at v0.1; revisit if any script earns broader use. |
| `.lsp.json` | skip | Anthropic ships LSP plugins for the major languages. We rely on those, don't compete. |
| `channels` | skip | No external messaging in the core flow; on-call/Slack integration is out of scope. |
| `settings.json` `agent` override | skip | Hostile to other plugins; the user picks their main thread. |
| Subagent `hooks`/`mcpServers`/`permissionMode` | n/a | Not allowed for plugin-shipped agents anyway. |
| Background monitor (default-on) | skip | Monitors must be opt-in; the only one we ship is `fixit-mode-watch`, off by default. |
| Sandboxed subagent that bypasses checks | skip | All subagents run inside the same hooks. No privileged paths. |

---

## How we coexist with other plugins

1. **Namespace everything.** All commands are `/debt-ops:*`. We don't claim
   short aliases.
2. **No global `agent`.** We never set `settings.json` `agent`. Users keep
   their main thread.
3. **Hooks are additive, not replacement.** Our `PostToolUse` hooks call
   project tooling; they don't shadow another plugin's hook. If a project
   has eslint configured, we run eslint (the project's eslint), once.
4. **MCP is optional.** No hard MCP dependency; teams without
   CodeScene/equivalent are first-class.
5. **Charter respects ownership.** `CLAUDE.md` is the project's, not the
   plugin's. We seed it once on `/debt:charter-init`; we don't overwrite
   on update.
6. **Soft hooks, structured outputs.** Hook results are structured JSON
   the agent can reliably parse, so other hooks/plugins can read or skip
   them without ambiguous text-matching.
7. **Override trailers.** The two non-bypassable rules accept `Skip-
   Debt-Ops: <reason>` so the developer can always proceed; we leave a
   trail rather than a wall.

---

## Gaps in Claude Code primitives (honest list)

The pillars require a few things the primitives don't quite give us
out of the box.

1. **Cron / scheduling.** Pillar 9's scheduled refactor runs need an
   external scheduler. GitHub Actions is the obvious answer; we ship a
   recipe.
2. **Cross-PR allocation accounting.** `/debt:budget` works against the
   git log, not Claude Code's session model. Fine, but it means the data
   source is git, not a plugin-internal store.
3. **Engineer-perception survey loop.** No primitive handles surveying;
   we provide a template and a `/debt:survey` skill but the loop is
   manual.
4. **DORA outcome telemetry.** Out of plugin scope; the plugin reads
   `debt/dora.json` if a CI pipeline produces it.
5. **Bug cap.** Same — out of plugin scope; lives in the issue tracker.
6. **Hook ordering across plugins.** If two plugins both register
   `PostToolUse` for `Write`, ordering is whatever Claude Code chooses.
   We assume hooks are commutative; if a real conflict shows up, we
   document it and let the user disable the conflicting plugin.

These gaps are acceptable. The pillars doc explicitly anticipated some
of them ("the system collects metrics it does not act on" is the
Pillar 4 anti-pattern; our `/debt:budget` is the action).

---

## A day in the life

A senior engineer, mid-sized TypeScript service, `debt-ops` installed.

**08:50 — Open editor.** `SessionStart` hook fires silently:
- Charter under budget. ✓
- ADR index up to date. ✓
- No pending fix-it-week mode.
The developer sees nothing. That's the point.

**09:10 — Pick a task.** "What should I look at today?"
The developer types `/debt:next 5`. The `triage` subagent returns five
ranked items: two reckless–inadvertent in a hotspot module, one
prudent–deliberate ADR with a payoff trigger that's gone overdue, two
fresh registry entries from yesterday's PRs.

**09:20 — Start the work.** They pick the top item — a callback hell in
`pricing/engine.ts`. They tell Claude what they want. Claude proposes
a refactor.

**09:22 — First edit lands.** `PostToolUse` hook fires:
- `feedback.sh` runs `pnpm lint --filter pricing` and `pnpm test
  pricing/engine.test.ts` in parallel; both green.
- `hotspot-guard.sh` checks Code Health: 7.4 → 7.6. ✓ no rejection.
- `test-integrity.sh`: no test deletions. ✓
The agent sees structured `{lint: "pass", types: "pass", tests: "pass",
health: "+0.2"}` and continues.

**09:35 — A subtle expediency.** Claude proposes a `// TODO: handle
the cancelled-promotion case later` to ship the path narrower. The
`Stop` hook's `todo-sniff.sh` sees the marker. A one-liner appears:
"register this with `/debt:add`?" The developer says yes; the
`debt-scribe` subagent drafts a registry entry from context, asks for
the missing payoff trigger ("when promotion engine v2 lands"), files
it as `debt/registry/0042-cancelled-promotion-callback.md`. Total
time: ~30 seconds.

**10:00 — Architectural fork.** Claude wants to introduce a new
pricing-event interface that other services would consume. The
`PreToolUse` heuristic on `interfaces/pricing-events.ts` recognizes
this is interface-shaped and surfaces "this looks ADR-shaped." The
developer types `/debt:adr "pricing event interface"`. The `adr-author`
subagent drafts Context/Decision/Consequences/Alternatives/Payoff-
trigger from the conversation; the developer edits and commits the ADR
alongside the code.

**11:30 — Commit time.** The diff includes AI-touched changes plus a
non-trivial complexity bump in `engine.ts`. The `PreToolUse` hook on
`git commit` adds a soft prompt: "explain this in the commit body." The
`/debt:explain` skill runs, writes a plain-English summary into the
commit message. The developer reads it, edits one sentence, commits.
Comprehensibility gate satisfied — and the developer can actually
explain it on call.

**13:00 — Lunch return; reviewer pass.** The developer runs `/debt:strict
-mode` for the afternoon (they're touching auth). Subsequent edits go
through `reviewer` and `security-reviewer` automatically before the
agent claims a task is done. The security reviewer flags an unsanitized
header read; the agent fixes it before the developer ever sees the
diff.

**15:30 — Boy Scout.** They're done with the feature. `Stop` hook
posts: "Files touched: pricing/engine.ts (7.4→7.6), pricing/types.ts
(8.1→8.1), interfaces/pricing-events.ts (new, 9.0). Net Code Health:
+0.2."

**16:00 — Open PR.** PR description auto-includes a summary of the
registry entries created, ADRs added, and Code Health delta. The PR
body has a `Debt-Pays-Down: 0042-cancelled-promotion-callback`-style
trailer if applicable; `/debt:budget` will count it toward the
allocation.

**Friday — Paydown allocation.** End of week, the developer runs
`/debt:budget --since=monday`. Output:
- Allocation target: 20%.
- Actual: 16% (3 of 19 PRs were debt-tagged; one `paydown-runner` PR
  merged Wednesday).
- Top three uncovered hotspots heading into next week.
The developer talks it through with their lead. Numbers, not vibes.

**Sunday 02:00 (no human in the loop).** A GitHub Actions cron runs
`claude … -p "/debt:paydown"`. The `paydown-runner` subagent picks the
top hotspot, drafts a spec, runs TDD, opens a draft PR. The PR body
references the registry entry and the affected ADR. Monday morning the
developer reviews it like any other PR.

The throughline: the developer does feature work all day. The plugin
is mostly silent. When it speaks, it's structured, fast, and easy to
say yes/no to. The discipline gets enforced where it has to be (test
integrity, AI hotspot regressions); everywhere else it's available
when reached for.

---

## Roadmap (lean)

Three phases, each shippable on its own.

### Phase 1 — Visibility & in-loop feedback (the foundation)

The minimum that delivers real value.

- `plugin.json` + namespaces.
- Skills: `/debt:add`, `/debt:adr`, `/debt:list`, `/debt:health`,
  `/debt:charter-init`, `/debt:charter-check`.
- Subagents: `debt-scribe`, `adr-author`.
- Hooks: `PostToolUse` `feedback.sh` (lint+type+test slice),
  `PostToolUse` `test-integrity.sh`, `Stop` `todo-sniff.sh`,
  `SessionStart` charter check, `Stop` `adr-index.sh`.
- Local hotspot scorer (`hotspot-score.sh`).
- `examples/registry/` seeds.

This is what makes Pillar 7 real, Pillar 1 workable, and Pillar 6
honest about size.

### Phase 2 — Prioritization, paydown, and discipline

- Skills: `/debt:next`, `/debt:budget`, `/debt:spec`, `/debt:tdd`,
  `/debt:explain`, `/debt:fixit-week`, `/debt:strict-mode`.
- Subagents: `triage`, `reviewer`, `security-reviewer`,
  `comprehensibility-checker`.
- Hook: `PreToolUse` `adr-detect.sh` (architectural nudge).
- Hook: `PreToolUse` on `git commit` (comprehensibility prompt).
- Hook: `PostToolUse` `hotspot-guard.sh` (rule 2 of Pillar 7).
- Hook: `PostToolUse` `ai-touched-tag.sh`.
- Output styles: `tdd-mode`, `paydown-aware`.

This is what makes Pillars 3, 4, 5, and 8 first-class.

### Phase 3 — Paydown engine + integrations

- Skill: `/debt:paydown`, subagent `paydown-runner`.
- `examples/github-actions/paydown.yml`.
- Optional MCP wiring (`code-health` via `userConfig`).
- Optional monitor: `fixit-mode-watch`.
- `/debt:survey` skill + template.

This is Pillar 9 plus the optional integrations that make Pillar 2's
fancy metrics available to teams that already pay for them.

**Validation between phases.** After each phase, dogfood the plugin on
this very repo for one full week before promoting to the next phase.
The plugin is for tech debt; if it can't be used to manage the debt of
its own development, the design is wrong.

---

## Anti-patterns we will actively watch for

These mirror the pillars doc's anti-patterns, restated as plugin smells.

1. **Hook latency creep.** Any hook >2 seconds for the lint/type slice
   or >10 seconds for tests gets pushed to deferred mode. We track this
   in CI on the plugin's own repo.
2. **Skill explosion.** If a skill is invoked <1×/week by dogfood users,
   it's a candidate for removal, not feature flag.
3. **Charter rot in the plugin's own dogfood.** If the plugin's own
   `CLAUDE.md` exceeds the size budget, we fix the plugin (the rule
   binds us first).
4. **Strict gates that aren't in Pillar 7's two rules.** Any new
   non-bypassable rule needs an ADR justifying it. (Yes, the plugin
   has its own ADRs.)
5. **MCP / external dependency drift.** `code-health` MCP is optional;
   if any code path *requires* it, that's a regression.
6. **Output-style or default-agent overrides masquerading as
   "convenience."** Either is a passive-plugin failure.
7. **Registry bloat without payoff triggers.** `/debt:list --stale`
   surfaces these; CI on the plugin's repo fails its own build if
   stale entries exceed a threshold.

---

## Closing

The pillars are nine, but the plugin is one — built mostly out of
**skills + subagents + a small, focused hook layer**, with one optional
MCP, one optional monitor, two non-bypassable rules, and zero
overrides of the user's main agent. Every other primitive in the
field guide is consciously skipped.

The bet: most days, a developer shouldn't notice the plugin is
running. They should notice when (a) they ask it something, or (b) a
deterministic gate catches a real mistake the agent was about to make.
That asymmetry — silent in the success case, useful in the failure
case — is the mark of a passive plugin that delivers value with
minimal effort.

If, six months in, developers describe the plugin as "the thing that
keeps our debt visible without getting in our way," the design
worked. If they describe it as "another wall," it didn't.
