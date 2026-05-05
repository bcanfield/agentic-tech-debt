# Tech Debt: Claude Code Plugin v1 Spec

## Why this document exists

`tech-debt-pillars.md` is tool-agnostic. This document commits those pillars
to a concrete, buildable v1 plugin and names what we deliberately don't
build yet.

**The principle.** Claude Code is the agent doing the work. The plugin is a
thin helper. Anywhere the plugin is doing what Claude could do, we cut it.

**Enable-and-go.** Installing the plugin creates zero files in the user's
repo. The plugin works on the first agent edit. Setup ceremony, CLAUDE.md
modifications, and pre-creating directories are opt-in (`/debt:init`), not
required.

**What v1 ships.** Two skills (`/debt:init` opt-in, `/debt:add`), two hooks
(`SessionStart`, `PostToolUse`), two short scripts. No templates, no
examples, no `userConfig`, no required CLAUDE.md modifications.

**Hard prerequisite.** A git repository. **Targets Claude Code v2.1.121
or later** — the two CC features the version gate protects are
`hookSpecificOutput.additionalContext` (used by both hooks) and
`disable-model-invocation` on skills (used by `/debt:init`). Without
them v1's quiet-by-default posture and opt-in `/debt:init` behavior
both regress.

## The two non-negotiables

1. **Lean relaxed over strict.** v1 has zero blocking rules. The
   `PostToolUse` hook surfaces quality-check results to the agent; nothing
   is rejected. Strict gates arrive in v3.
2. **Passive, plays well with others.** No `agent` override. Namespaced
   commands only (`/debt-ops:*`). Hooks call the project's existing
   tooling. Nothing is created in the user's repo until the developer asks
   for it.

**On the apparent tension with the design tenets.** Two pillar tenets —
*deterministic over vibes* (§Pillar 7) and *evidence-based over opinion*
(§design tenets) — read at first as contradicting "zero blocking rules"
and "static layer only via Pillar 7." They don't, but the staging is
worth saying out loud: v1 honors *deterministic over vibes* by making
the feedback signal *exist* and reach the agent on every edit; v3
promotes the signal to a gate. v1 honors *evidence-based over opinion*
by deferring to the project's existing lint/type/test commands rather
than to the developer's gut — the project's quality stack is the v1
ground truth, the behavioral and DORA layers ship in v3. The two
non-negotiables describe v1's *posture*, not its endpoint.

---

## Working name

`debt-ops` namespaces to `/debt-ops:*`. Commands are written `/debt:*` in
this doc for brevity.

---

## Who v1 is for

Based on workflow research across five personas (vibe coder, solo
brownfield, small team, enterprise, OSS maintainer):

- **Bullseye: solo brownfield (Persona 2).** Senior IC adding agentic
  tooling to an established codebase. Install, then the first edit works.
  No setup ceremony.
- **Strong fit: small team, 2–10 devs (Persona 3).** Each dev gets
  enable-and-go individually. Optional `/debt:init` writes the config to
  CLAUDE.md so the team shares one source of truth.
- **Indifferent: vibe coder (Persona 1).** v1 is near-silent on projects
  with no detectable quality commands.
- **Out of scope: enterprise platform tier (Persona 4).** Spotify Honk /
  AWS Transform / internal platforms cover this.
- **Wrong layer: OSS maintainers (Persona 5).** Their pain is at PR
  triage; v1 lives in the contributor's editor.

---

## Why this and not the alternatives

Honest differentiation. v1 occupies a narrow seam, and a senior IC
should be able to read the install case in one paragraph.

- **vs. doing nothing (CLAUDE.md + a homemade `PostToolUse` hook
  running the project's linter).** A 30-line hand-rolled hook
  delivers most of Pillar 7. v1's incremental value over that is the
  *registry schema* (Fowler quadrant + Google categories + payoff
  trigger — a week of reading Kruchten/Fowler/Jaspan to invent), the
  manifest-mtime cache invalidation in implementation gate 2 (the
  cargo-cult-prone bit), and the disciplines packaged for team-share
  via `/debt:init`. If you don't intend to keep a registry, write the
  hook yourself.
- **vs. CodeScene CodeHealth MCP Server.** Different layer.
  CodeScene gives agents real Code Health metrics (Pillar 2
  behavioral); v1 gives lint/type/test pass-fail and a registry. v1
  is complementary; v3 wires the MCP.
- **vs. CodeRabbit / Cursor review modes / Sourcegraph Cody.**
  Different stage. Those tools review at PR or IDE-time; v1 operates
  pre-PR, in the agent's edit cycle.
- **vs. Claude Code's built-in `/init` + a generic review subagent.**
  No overlap. `/init` scaffolds CLAUDE.md (v1 deliberately doesn't
  duplicate); subagents arrive in v2.

The honest pitch is *the schema and the disciplines, packaged*. If
that combination earns its install, install. If not, the hand-rolled
hook is the right move.

---

## How it works (the whole plugin in one paragraph)

On every session, a `SessionStart` hook checks the plugin's per-repo
cache for this repo's quality commands (cache lives under
`${CLAUDE_PLUGIN_DATA}/cache/<repo-hash>/`, since
`${CLAUDE_PLUGIN_DATA}` itself is per-user-per-plugin and shared across
repos). On the first session it injects context asking Claude to scan
the repo and cache the result; on subsequent sessions it reads the
cache instantly. The same hook injects the disciplines (auto-register
debt, draft ADRs in Nygard format), emitted via the documented
`hookSpecificOutput.additionalContext` envelope (10,000-char cap).
After every agent edit, `PostToolUse → feedback.sh` runs the cached
commands in parallel under a self-imposed 3 s budget (Claude Code's
default hook timeout is 600 s; the plugin enforces 3 s itself via
`timeout 3 …` per command) and returns structured pass/fail. When
Claude writes an expedient marker during normal work, the discipline
tells it to invoke `/debt-ops:add` immediately; the skill loads the
schema, lazily creates `debt/registry/`, writes the entry, and
announces. The developer interacts with debt entries through chat
("drop that one") or the editor's file tree, referring to entries by
content rather than ID. `/debt:init` is an optional persistence step
that writes the disciplines and commands into CLAUDE.md so the team
shares one source of truth; solo users skip it.

---

## The disciplines (injected by `SessionStart`)

These three instructions live inside `session-start.sh`'s heredoc and
orient the model. The developer never reads them; the user-visible
surface is one-line announcements at registration time, the registry
directory, and ADR files. The script emits a JSON envelope
`{"hookSpecificOutput": {"hookEventName": "SessionStart",
"additionalContext": "<text>"}}`; there is no separate `disciplines.md`
file. If `CLAUDE.md` already has a `## Tech debt operations` section
(because `/debt:init` was run), those instructions take precedence; the
inject is the fallback. (Claude Code auto-loads `CLAUDE.md` and related
memory files; it does not auto-load `AGENTS.md` — see Pillar 6 mapping
below.)

The disciplines cover Pillars 1 and 5 (visibility, deliberate
architecture). Pillar 8 (spec / TDD / fresh-context review /
comprehensibility) is *not* covered by v1 disciplines; the
"What v1 accepts as residual risk" subsection below names the failure
mode v1 accepts there. v2 brings `/debt:spec`, `reviewer`, and
`security-reviewer` as a coherent set.

1. If you write a `TODO`, `FIXME`, `HACK`, or `XXX` marker, register it
   via `/debt-ops:add` immediately. No permission prompt; just do it.
   Use `payoff_trigger: unknown` if unsure. Announce as one line:
   `+1 entry: <slug> (drop?)`. The developer can reply "drop it" in
   one message and you'll delete the entry; treat over-registering as
   cheap.
2. When making an architecturally significant change — a data model,
   public interface, security boundary, release pipeline, or a
   dep-manifest change that is a major-version bump or a *new*
   top-level dependency — draft an ADR under `doc/adr/` in Nygard
   format (Context, Decision, Consequences, Alternatives, Payoff
   trigger). Create the directory if needed. Draft an ADR only when
   there were two credible alternatives; if you cannot list two, it is
   a comment, not an ADR. If the ADR introduces deliberate debt (a
   payoff trigger that fires later), also call `/debt-ops:add` so the
   registry entry mirrors the ADR.
3. Read entries under `debt/registry/` before changing files they
   reference.

---

## The registry schema

Each entry under `debt/registry/` is a Markdown file with YAML
front-matter. **Entries are addressed by content in conversation** ("the
cancelled-promotion entry"), not by ID. The numeric `id` is for tooling
cross-references (PR trailers like `Debt-Pays-Down: 0042`, future
ranking), like a commit SHA.

```yaml
---
id: 0042
title: cancelled-promotion-callback
principal: 2d                         # estimated effort to fix
interest: +30min/incident             # ongoing cost
hotspot: pricing/engine.ts            # path or module
business_capability: checkout
payoff_trigger: when promotion engine v2 lands   # may be `unknown`
quadrant: reckless-inadvertent
category: code_quality
ai_authored: true
created: 2026-05-04
---

Free-form prose: the debt, recurrence, observed symptoms.
```

**Quadrant** (Fowler): `reckless-inadvertent`, `reckless-deliberate`,
`prudent-inadvertent`, `prudent-deliberate`.

**Category** (Google / Jaspan-Green): `migration`, `documentation`,
`testing`, `code_quality`, `dead_code`, `code_rot`, `expertise`, `release`,
`infrastructure`, `planning`.

`payoff_trigger: unknown` is first-class; it ages into stale review at v2.

---

## The v1 commitment

| Pillar | v1 | Deferred |
|---|---|---|
| 1. Visibility | `/debt:add`; SessionStart inject auto-registers debt; lazy `debt/registry/` creation | `/debt:list` ranking, stale aging, ADR auto-pairing (v2) |
| 2. Continuous Measurement | static layer via Pillar 7's quality checks | behavioral signal, AI-touched windows, DORA, perception (v3) |
| 3. Hotspot Prioritization | — | `/debt:list` + `triage` (v2) |
| 4. Continuous Paydown | — | `/debt:budget`, fix-it weeks, Boy Scout summary (v4) |
| 5. Deliberate Architecture | SessionStart inject tells Claude to draft Nygard-format ADRs for significant changes; lazy `doc/adr/` creation | `/debt:adr` skill, index regen, template-ship (v2) |
| 6. Curated Agent Context | rely on Claude Code's native `CLAUDE.md` loading (CC does not auto-load `AGENTS.md`); `/debt:init` (opt-in) writes a debt-ops section into CLAUDE.md for team-share | enforced size budget, freshness checks (v2) |
| 7. In-Loop Deterministic Feedback | `PostToolUse → feedback.sh` runs commands cached by SessionStart (or read from CLAUDE.md if `/debt:init` ran) | test-integrity rule, AI-touched hotspot floor rule, `/debt:override` (v3) |
| 8. Spec → Test → Review → Comprehend | — (named as accepted residual risk; v1 disciplines do not cover Pillar 8) | `/debt:spec`, `/debt:explain`, `reviewer`, `security-reviewer` (v2/v3) |
| 9. AI as Paydown Engine | — | `/debt:paydown`, GH Actions recipe (v3) |

---

## What v1 accepts as residual risk

The v1 deferrals above leave specific failure modes from the pillars
running unimpeded in v1. Naming them is the honest companion to the
"What we skip" table further down, which lists *primitives*. This list
covers *failure modes*. Each line is a v1 acceptance, not a denial; v1
ships knowing this, with a dogfood detection plan.

1. **Behavioral measurement absent (Pillar 2 failure mode).** AI-induced
   hotspot regressions accumulate undetected until v3 wires the
   CodeScene MCP. v1 ships exactly the static-only configuration the
   pillars-doc anti-pattern #2 forbids; we accept this for v1 because
   the alternative is a misleading complexity proxy (see Pillar 2
   mapping below). **Mitigation:** the project's static layer catches
   the gross issues. **Detection:** registry growth rate and the share
   of `ai_authored: true` entries; if rising, v3 is needed sooner.
2. **No hotspot prioritization (Pillar 3 failure mode).** Cleanup may
   go to easy targets, not high-pay-off targets. **Mitigation:** v1
   expects the developer to choose targets; v2's `/debt:list` ranking
   arrives. **Detection:** ratio of registry entries closed in active
   modules vs. stable modules.
3. **No allocation defense (Pillar 4 failure mode).** Feature pressure
   may eat any informal paydown commitment. v1 ships nothing aimed at
   the cultural failure the research base most strongly warns about.
   **Mitigation:** `Debt-Pays-Down: <id>` PR trailers can accumulate
   from day one as raw material for v4's `/debt:budget`. **Detection:**
   the commit log itself.
4. **No test-integrity / Code Health gates (Pillar 7 failure mode).**
   The pillars doc marks two rules "non-bypassable"; v1 ships zero
   rejections. The implementation gate set below adds a non-blocking
   test-count *warning* in `feedback.sh` so Beck's "agents try to delete
   tests to make them pass" is at least visible — not enforced. The
   Code Health gate waits for v3's MCP. **Mitigation:** human at PR
   time. **Detection:** per-edit test-count delta in `feedback.sh`
   output.
5. **No spec / no fresh-context review / no comprehensibility gate
   (Pillar 8 failure mode).** v1 ships no Pillar 8 disciplines. The
   METR perception/reality gap, the most-cited piece of evidence in
   the synthesis, is uncovered at the v1 inject layer. **Mitigation:**
   human review at PR; v2 brings `/debt:spec`, `reviewer`, and
   `security-reviewer` as a coherent set. **Detection:** % of
   agent-authored diffs the developer rewrites materially; if high,
   v2 is needed sooner.
6. **No agentic paydown (Pillar 9 failure mode).** Asymmetry persists:
   agents accelerate creation, no one redirects to paydown. Pillar 9
   depends on 3, 7, 8 being live; v1 cannot ship it. **Detection:** v1
   surfaces nothing here; v3 owns the metric.

---

## Pillar-by-pillar v1 mapping

### Pillar 1: Visibility

**v1 commitment.**

- `/debt:add`: Claude drafts a registry entry from current context, fills
  the schema, marks `payoff_trigger: unknown` for any field it can't
  determine, lazily creates `debt/registry/` if needed, writes
  `<id>-<slug>.md`, and announces. The skill is a thin prompt that loads
  the schema; Claude does the work.
- SessionStart-injected discipline (item 1): when Claude writes an
  expedient marker during normal work, it auto-registers via
  `/debt-ops:add`. No permission prompt; just write and announce.
- The developer drops entries by asking Claude or by deleting the file in
  their editor.

**Deferred to v2.** Ranking, filters, the `triage` subagent, `/debt:list`
(chronological listing falls out of "ask Claude to read the dir" until the
skill earns its slot with ranking).

---

### Pillar 2: Continuous Measurement

**v1 commitment.** Static layer only, via Pillar 7 (quality commands run
on every edit).

**Deferred to v3.** Behavioral signal via optional `code-health` MCP;
AI-touched discriminator and 30/60/90/14-day windows; DORA file reader.
We considered a local "lines × git frequency" hotspot scorer; on review
it's a misleading complexity proxy. We commit to honest "behavioral signal
unavailable until you wire up an MCP" rather than fake it.

---

### Pillars 3, 4, 8, 9: deferred entirely from v1

- **Pillar 3 (Hotspot Prioritization).** Developers fall back to existing
  prioritization until v2 lands `/debt:list` ranking and the `triage`
  subagent.
- **Pillar 4 (Continuous Paydown).** No direct commitment. v1 *enables*
  future accounting because the registry exists; `Debt-Pays-Down: <id>`
  trailers can accumulate from day one.
- **Pillar 8 (Spec → Test → Review → Comprehend).** No commitment. v1's
  contribution is ensuring the disciplines exist in Claude's context;
  spec, test, review, and comprehend disciplines arrive in v2/v3.
- **Pillar 9 (AI as Paydown Engine).** No commitment. Pillar 9 needs
  Pillars 3, full 7, and 8 all live.

---

### Pillar 5: Deliberate Architecture

**v1 commitment.** The SessionStart-injected discipline (item 2) tells
Claude to draft a Nygard-format ADR for architecturally significant
changes. The ADR format is described in the inject; Claude writes the
file directly, lazily creating `doc/adr/` on first need.

**Deferred to v2.** `/debt:adr` skill (formal draft-from-context flow),
shipped ADR template file, ADR index regeneration, architectural-touch
heuristic detection.

---

### Pillar 6: Curated Agent Context

**v1 commitment.**

- We rely on Claude Code's native `CLAUDE.md` loading. CC reads
  `CLAUDE.md` (plus `CLAUDE.local.md`, `.claude/rules/*.md`, and
  managed-policy CLAUDE.md). It does **not** auto-load `AGENTS.md`; for
  AGENTS.md to participate, the user must add `@AGENTS.md` inside their
  CLAUDE.md.
- `/debt:init` (opt-in) writes a `## Tech debt operations` section into
  `./CLAUDE.md` (creating the file if absent) so the disciplines and
  commands persist with the repo. For teams that also want AGENTS.md
  parity (Cursor, Aider, Codex compatibility), the same content can be
  written to `AGENTS.md` and `@AGENTS.md` added to CLAUDE.md. It does
  **not** scaffold the rest of CLAUDE.md from scratch; Claude Code's
  built-in `/init` already produces a CLAUDE.md.
- The skill is marked `disable-model-invocation: true` so Claude cannot
  auto-invoke it without an explicit user request — `/debt:init` stays
  opt-in by construction.
- For solo users who skip `/debt:init`, the SessionStart inject covers
  the disciplines per-session. Nothing is written to the repo.

**Honest caveat.** Pillar 6 calls for an *enforced* size budget and
freshness checks. v1 has neither. The testable consequence: if your
CLAUDE.md exceeds ~10k tokens, expect discipline-firing rates to drop —
that is the dogfood signal that v2's size budget is needed. Until then
we trust Claude's reading of whatever charter exists.

---

### Pillar 7: In-Loop Deterministic Feedback

**v1 commitment.**

- `SessionStart` hook (`session-start.sh`) detects this repo's quality
  commands and caches them in
  `${CLAUDE_PLUGIN_DATA}/cache/<repo-hash>/feedback.list`. The
  `<repo-hash>` is a short hash of the git toplevel (e.g.,
  `git rev-parse --show-toplevel | shasum | cut -c1-12`); without it
  every repo on the user's machine would share one cache, since
  `${CLAUDE_PLUGIN_DATA}` is per-user-per-plugin, not per-repo. On
  first session: inject context asking Claude to scan project files and
  write the cache. On subsequent sessions: read the cache instantly. If
  `CLAUDE.md` has a `<!-- debt-ops:feedback v1 -->` marker block
  (because `/debt:init` ran), the cache is overridden by that; CLAUDE.md
  is the source of truth when present. `/debt:init` writes the marker
  block with a self-explaining first line so a teammate without the
  plugin can read it: `<!-- this section is auto-managed by the
  debt-ops Claude Code plugin; safe to edit, run /debt-ops:init to
  regenerate -->`. The marker is a self-imposed convention; CC has no
  cross-plugin marker contract, so `/debt:init` writes defensively and
  `feedback.sh` reads tolerantly.
- `PostToolUse` matcher (`Write|Edit|MultiEdit`, an exact-list match,
  not regex) calls `feedback.sh`. The script (~15 lines) reads commands
  from cache or charter, runs each in parallel under a self-imposed 3 s
  wall-clock budget per command (`timeout 3 …`), and returns structured
  JSON to the agent inside an `additionalContext` payload. CC's default
  hook timeout is 600 s; `hooks.json` sets `timeout: 5` as a CC-level
  guard so a stuck script can't hang the edit cycle. Other plugins'
  PostToolUse hooks are not bounded by this budget.

**Trust boundary.** The agent can *propose* commands by editing CLAUDE.md
(when present); it doesn't get to *skip* them at edit time, because the
hook runs deterministically.

**Deferred to v3.**

- Test-integrity rule (rejects diffs that delete or weaken tests in the
  same session as the production code those tests covered).
- AI-touched hotspot floor rule (`ai_touched_min_health`, default 9.4).
- `/debt:override <reason>` skill: audit-trail escape.
- AI-touched tagging.
- Optional `code-health` MCP wiring.
- Charter-tampering rule: extend test-integrity to also flag removal of
  the `<!-- debt-ops:feedback -->` block.

v1 is the relaxed-by-construction version. No rejections. Just feedback.

---

## Plugin layout (v1)

```
debt-ops/
├── .claude-plugin/
│   └── plugin.json              # name + description; version omitted while iterating
├── skills/
│   ├── add/SKILL.md             # /debt:add (registry schema embedded in prompt)
│   └── init/SKILL.md            # /debt:init (disable-model-invocation: true; writes section to CLAUDE.md)
├── hooks/
│   └── hooks.json               # SessionStart + PostToolUse; commands use ${CLAUDE_PLUGIN_ROOT}/scripts/...
├── scripts/
│   ├── session-start.sh         # detects + caches commands; injects disciplines via additionalContext
│   └── feedback.sh              # ~15 lines: read commands, run in parallel under timeout 3 each, return JSON
└── README.md
```

Two skills, two hooks, two scripts. No templates, no examples, no config
files. Anyone can grok the plugin in five minutes.

**`plugin.json`.**

```json
{
  "name": "debt-ops",
  "description": "Continuous, evidence-based tech debt management for Claude Code."
}
```

`name` is the only required field. `version` is omitted intentionally
during pre-1.0 iteration so the git SHA acts as the cache key; if we
pinned `0.1.0`, users would silently miss updates whenever the maintainer
forgot to bump. `userConfig` and `dependencies` are omitted because both
default to absent — including them as `{}` / `[]` is cargo-cult. Zero
install-time questions.

---

## Hook layout (v1)

| Event | Matcher | Script (under `${CLAUDE_PLUGIN_ROOT}/scripts/`) | What it does |
|---|---|---|---|
| `SessionStart` | — | `session-start.sh` | emit JSON envelope with `hookSpecificOutput.additionalContext` containing the disciplines; if `${CLAUDE_PLUGIN_DATA}/cache/<repo-hash>/feedback.list` exists, also include the command list; otherwise include a one-time prompt asking Claude to detect and write the cache |
| `PostToolUse` | `Write\|Edit\|MultiEdit` (exact-list match) | `feedback.sh` | read commands (CLAUDE.md marker block if present, else per-repo cache); run each in parallel (`timeout 3` each); return structured JSON via `additionalContext`. `hooks.json` sets `timeout: 5` so a stuck script can't hang the edit cycle. |

Two hooks, both small. Disciplines that don't need deterministic
enforcement live in the SessionStart inject; the one thing that does
(running quality commands) lives in PostToolUse.

---

## What we skip in v1 (and when each could return)

Every cut is recoverable. Nothing is permanently off the table.

| Primitive | v1 decision | Why now | Could return when |
|---|---|---|---|
| `userConfig` | empty | Charter (when present) is source of truth; cache covers the other case. | Per-user override of detected commands. |
| `Stop` hook | skip | Discipline asks Claude to suggest registration when it writes TODO/FIXME during work. | If charter discipline drifts in dogfood, a Stop-hook todo-sniff returns as safety net. |
| `/debt:list` skill | skip | Claude can `ls debt/registry/`; v2 brings it back with ranking. | v2 (with `triage` ranking). |
| Required `/debt:init` | skip | Plugin works on enable; `/debt:init` is opt-in for team-share. The skill carries `disable-model-invocation: true` so Claude can't auto-invoke it. | We would never make it required again. |
| `commands/` (legacy flat) | skip | Skills supersede. | We would choose skills again. |
| `themes/` | skip | Out of scope. | If we ship a visual mode (e.g., paydown-session). |
| `bin/` | skip | No standalone CLI use yet. | Once a script earns shell-level use. |
| `.lsp.json` | skip | Anthropic ships LSP plugins for major languages. | Niche language target. |
| `output-styles/` | skip | Heavyweight for nudges. | Sustained-tone modes (e.g., security review). |
| `monitors/` | skip | Nothing in v1 needs background reactions. | v3+ for fix-it-week reactivity, CI status. |
| `channels` | skip | No external messaging. | Slack/Telegram/Discord bridges. |
| `settings.json` `agent` override | skip | Hostile to other plugins. | Only inside an explicit time-boxed mode. |
| Subagents (`agents/`) | skip | Skills handle drafting; the hook handles enforcement. | v2 brings `debt-scribe`, `triage`, `reviewer`; v3 adds `security-reviewer`. |
| `.mcp.json` | skip | No code-health MCP needed yet. | v3 (Code Health signal). |
| Local hotspot scorer | skip | "Lines × git frequency" is a misleading complexity proxy. | Tree-sitter-based scoring as a no-MCP fallback. |
| Bash auto-detection table | skip | Claude detects via the SessionStart inject, smarter than bash globbing. | Non-interactive contexts. |
| `templates/` directory | skip | Disciplines live inline in `session-start.sh`; ADR format is in the inject text. | If a template grows complex enough to warrant a file. |
| `examples/` directory | skip | The schema example for registry entries lives inside `/debt:add`'s `SKILL.md`. | If users ask for human-readable example files in their repo. |
| Charter bootstrap (creating CLAUDE.md from scratch) | skip | Claude Code's built-in `/init` already scaffolds CLAUDE.md. | Never; overlap with native is the failure mode. |
| Pre-creating `debt/registry/` and `doc/adr/` on install | skip | Lazy creation on first use; install footprint is zero. | We would choose lazy again. |
| GitHub Actions example | skip | Ships with `/debt:paydown`. | v3. |

---

## How we coexist with other plugins

1. **Namespace everything.** `/debt-ops:*` only.
2. **No global `agent`.** We never set `settings.json` `agent`.
3. **Hooks call project tooling, not replace it.** The detected commands
   are the project's own.
4. **Charter respects ownership.** `CLAUDE.md` (and `AGENTS.md` if the
   project uses it) belongs to the project; we only modify it through
   opt-in `/debt:init`. The skill is gated by `disable-model-invocation:
   true` so it cannot be auto-invoked.
5. **Soft hooks, structured outputs.** Hook results are structured JSON
   inside the documented `hookSpecificOutput.additionalContext` envelope;
   other plugins can read or skip without text-matching. Multiple
   plugins' SessionStart/PostToolUse hooks run in parallel — we do not
   depend on ordering.
6. **Zero install footprint.** Files in the user's repo only appear when
   the developer asks for them (registry entries on `/debt:add`;
   CLAUDE.md edits on `/debt:init`).

---

## Gaps in Claude Code primitives

1. **Cron / scheduling.** Pillar 9 needs an external scheduler (GitHub
   Actions). v3 ships the recipe.
2. **Cross-PR allocation accounting.** v4's `/debt:budget` is git-driven
   and survives plugin uninstall.
3. **Engineer-perception survey loop.** Out of plugin scope.
4. **DORA outcome telemetry.** Out of plugin scope; v3 reads
   `debt/dora.json` if produced externally.
5. **Bug cap.** Out of plugin scope.
6. **Hook ordering across plugins.** Multiple plugins' SessionStart and PostToolUse hooks run in parallel; we depend on no ordering, and our outputs are independently consumable.
7. **Non-git repos.** Most of the plugin is a no-op without git.

---

## A day in the life (v1)

A senior engineer, mid-sized Rust service, `debt-ops` v0.1.0 installed
today.

**08:50, open editor.** First-ever session with the plugin. `SessionStart`
injects (via `additionalContext`): "Disciplines: [the four]. First
session for this repo: please detect quality commands by scanning
project files (`Cargo.toml`, etc.) and write them to
`${CLAUDE_PLUGIN_DATA}/cache/<repo-hash>/feedback.list`." Claude does so
silently: `cargo check`, `cargo clippy --no-deps -- -D warnings`. The
cache is now warm. Total: ~3 s. The developer sees nothing. (Note: the
3 s budget is per-command inside `feedback.sh`; the discovery prompt
itself runs once and is not bounded by it.)

**09:15, start the work.** They tell Claude to refactor a callback chain
in `pricing/engine.rs`.

**09:17, first edit lands.** `feedback.sh` reads the cache, runs `cargo
check` and `cargo clippy` in parallel under `timeout 3` each (1.4 s).
`cargo test` is *not* in the per-edit cache because the bare `cargo
test` exceeds the 3 s budget on this codebase; the discovery step
recorded only the fast-feedback commands (Pillar 7's "fast loop" intent).
The agent sees `{"cargo check": "pass", "cargo clippy": "pass"}` and
continues; the full test suite runs at PR time, not on every edit.

**09:35, a subtle expediency.** Claude proposes `// TODO: handle the
cancelled-promotion case later`. Discipline 1 fires. Claude invokes
`/debt-ops:add`, lazily creates `debt/registry/` (the first file ever in
this dir), writes the entry (timestamp-shaped id per impl-gate 4) with
`payoff_trigger: unknown`, and announces in one line:
`+1 entry: cancelled-promotion-callback (drop?)`.

**10:05, a false positive.** Claude writes `// TODO: maybe rename this
var` and announces `+1 entry: rename-this-var (drop?)`. Developer:
"drop." Claude deletes the entry. Done.

**11:30, an architectural fork.** Claude wants a new pricing-event trait.
Discipline 2 fires. Claude lazily creates `doc/adr/` (the first file in
this dir too), writes `0001-pricing-event-trait.md` in Nygard format with
a payoff trigger. The developer reviews and edits.

**16:00, end of day.** No Stop hook. Today's debt activity is visible
in `git diff`: one registry entry, one ADR, both under directories the
plugin lazily created.

**PR review (later that day).** The dev opens a PR; the diff includes
the new registry entry and ADR. They read each entry's `payoff_trigger`
field, glance at each ADR's "Decision" against ship reality, and decide
keep or `git rm`. Realistic cost: ~1 minute per registry entry, ~2
minutes per ADR. A typical day's debt artifacts add ~5 minutes to PR
review. v1 accepts this cost; v2's `/debt:list` and `triage` reduce it
by surfacing duplicates and stale entries before PR time.

**Tomorrow.** `SessionStart` reads the cache (instant), injects
disciplines and commands; the plugin runs.

**Some weeks later.** The team has grown to four developers. They want
everyone to share the same disciplines and commands, and a charter that
describes the project's debt-ops conventions for both Claude Code and
non-Claude tooling on the team. One dev runs `/debt-ops:init`. It writes
a `## Tech debt operations` section into `CLAUDE.md` with the
disciplines and a `<!-- debt-ops:feedback v1 -->` marker block containing
the cached commands. (If the team also keeps an `AGENTS.md` for Cursor /
Aider compatibility, the dev can mirror the section there and add
`@AGENTS.md` to CLAUDE.md so CC picks it up too.) They commit. CLAUDE.md
is now the source of truth (the SessionStart inject defers to it when
present). New team members get the config without configuring the
plugin.

The throughline: install, the first edit just works, footprint stays zero
until the developer asks for something.

---

## Beyond v1: roadmap

### v2: ranking + ADR + reviewer

- `/debt:list` (ranking + filters) and `triage` subagent.
- `/debt:adr` skill (formal draft-from-context flow), ADR index
  regeneration, shipped Nygard template.
- `/debt:spec`, `/debt:explain` skills.
- `reviewer` subagent (with comprehensibility mode).
- `debt-scribe` subagent (now that drafting is multi-format).
- Possibly a `Stop` hook returns as a safety net if discipline drifts in
  dogfood.
- `PreToolUse` on `git commit` for the comprehensibility prompt.
- Enforced charter size-budget check.

### v3: enforcement + paydown engine

- `feedback.sh` extends with: test-integrity rule, AI-touched hotspot
  floor rule, AI-touched tagging, charter-tampering rule.
- `/debt:override <reason>` skill.
- `code-health` MCP wiring (`code_health_mcp_endpoint` userConfig).
- `/debt:health` skill with `--ai-only`, `--window=…`, `--churn=…`.
- `/debt:paydown` skill + GH Actions example.
- `security-reviewer` subagent.

### v4: allocation + Boy Scout

- `/debt:budget` (with `--fixit start|end`).
- Boy Scout one-line summary at session end.
- `debt/dora.json` and `debt/bug-cap.json` external readers surfaced in
  `/debt:budget`.

**Validation gate.** Dogfood the previous version on the plugin's own
repo for at least one full week before promoting.

---

## Future possibilities (beyond v1–v4)

Items not pinned to a phase. Captured here so they're not lost.

### Skills considered and cut

- `/debt:next`: folded into v2's `/debt:list`.
- `/debt:fixit-week`: folded into v4's `/debt:budget --fixit`.
- `/debt:charter-check`: handled by SessionStart inject + v2 size-budget
  check.
- `/debt:strict-mode`, `/debt:tdd`, `/debt:survey`: speculative; only if
  dogfood shows a clear need.

### Subagents considered and cut

- `adr-author`: folded into v2's `debt-scribe`.
- `comprehensibility-checker`: folded into v2's `reviewer`.
- `paydown-runner`: v3's `/debt:paydown` uses the writer thread.

### Hooks / scripts considered and cut

- `Stop` hook: discipline 1 covers the same territory; returns as safety
  net if needed.
- `Skip-Debt-Ops:` magic-string trailer: replaced by v3's `/debt:override`.
- AI-touched marker file: v3 uses `Co-authored-by:` trailers from Claude
  Code, Cursor, Copilot, Aider.
- Bash auto-detection table: replaced by Claude's repo scan in the
  SessionStart inject.

### Other primitives

- Background monitor `fixit-mode-watch`: replaced by charter-driven
  reminders.
- DORA dashboard pushers: out of plugin scope.
- Bug-cap enforcement: out of plugin scope.
- Engineer-perception survey aggregation: out of plugin scope.
- Tree-sitter-based hotspot scoring: a possible no-MCP fallback at v3.

### userConfig keys considered and cut

All of them. v1 omits `userConfig` from the manifest entirely (since both
empty `{}` and absent are equivalent, the latter is the cleaner default).
Per-user overrides return in v2+ if needed.

---

## Anti-patterns we will actively watch for

1. **Hook latency creep.** The 3 s per-command budget inside `feedback.sh`
   (enforced via `timeout 3 …`, with `hooks.json` setting `timeout: 5`
   as a CC-level guard) is the line. Note: this budget is plugin-self-
   imposed, not CC-enforced; CC's default `command` hook timeout is 600 s.
2. **Skill explosion.** Any *recurring-use* skill <1×/week in dogfood is a
   removal candidate. (One-shot skills like `/debt:init` are exempt.)
3. **Reinventing detection.** If we add bash auto-detection logic
   anywhere, ask: could this be the SessionStart inject asking Claude to
   do it instead?
4. **Optional becoming required.** Any v3 code path that *requires* the
   MCP is a regression. Same for `/debt:init`: it must remain optional.
5. **Output-style or default-agent overrides masquerading as
   "convenience."** Either is a passive-plugin failure.
6. **Discipline drift.** If Claude consistently ignores the
   SessionStart-injected disciplines in dogfood, bring back safety-net
   hooks (Stop for TODO-sniff, etc.) and consider requiring `/debt:init`
   for the persistent-charter path.
7. **Footprint creep.** Every file the plugin creates in a user's repo
   without explicit ask is a regression to be justified.

---

## v1 implementation requirements

These are the script-level guarantees v1 must ship with. Each is a
specific failure mode the audit identified; each is a small fix
(~5–30 lines). None of them changes v1's architectural shape; all of
them prevent week-one bugs.

1. **Robust `session-start.sh` and `feedback.sh`.** Both scripts must
   open with `set -euo pipefail`. `session-start.sh` must check
   `git rev-parse --show-toplevel`'s exit code; on non-git repos, emit
   `additionalContext` "debt-ops: not a git repo, plugin idle this
   session" and exit clean (the audit found the naive
   `git rev-parse | shasum` collapses every non-git directory's cache
   to one shared key — silent corruption). On macOS, `timeout` is GNU
   coreutils and not present by default; both scripts must detect
   `timeout` vs. `gtimeout` and fall back to a portable
   `(cmd & PID=$!; sleep 3 && kill $PID 2>/dev/null) wait` shim.
   `${CLAUDE_PLUGIN_DATA}` may be read-only (containers); on first
   write failure, log "debt-ops: cache disabled, running in stateless
   mode" and skip cache logic. The README must state the plugin
   requires bash; on Windows, it expects WSL or Git Bash.
2. **Cache invalidation on manifest mtime.** SessionStart hashes the
   project's manifest files (`Cargo.toml`, `package.json`,
   `pyproject.toml`, `Makefile`, `go.mod`, `Gemfile`) and stores the
   hash beside `feedback.list`. On mismatch with the stored hash, it
   re-runs discovery. Without this, the cache silently serves stale
   commands when lockfiles change overnight.
3. **Test-integrity warning in `feedback.sh`.** SessionStart's
   discovery prompt asks Claude to count test-shaped filenames in the
   repo using a portable pattern (filenames matching `test_*`,
   `*_test.*`, `*.test.*`, or `*.spec.*`) and cache the count.
   `feedback.sh` recomputes on every invocation; if the count
   *dropped* in a single edit, it emits a `WARNING: this edit removed
   N test files` line in the structured `additionalContext`. File-name
   counting is intentionally coarse — a renamed file looks like
   delete + add and won't trigger; that's acceptable for v1 because
   the goal is catching the gross "agent removes the tests file"
   pattern Beck described. Block-level counting waits for v3. This is
   non-blocking — fully in the spirit of "lean relaxed over strict" —
   but it closes Beck's attack vector for the v1→v3 window. Without
   it, the team is exposed for months.
4. **Race-safe `/debt:add` IDs.** The skill must not pick the next id
   by globbing `debt/registry/[0-9]{4}-*.md` and incrementing — two
   concurrent sessions both pick `0001` and write conflicting files.
   Use a timestamp-shaped id (`YYYYMMDDhhmmss`) or a short content
   hash. The plan's framing ("the id is for tooling cross-references
   like commit SHAs") already supports this.
5. **Discovery prompt is load-bearing for fast-loop correctness.**
   SessionStart's discovery prompt is *the* mechanism that determines
   whether Pillar 7 actually delivers a fast loop. The prompt must
   explicitly tell Claude: (a) **prefer** commands that accept a
   changed-file or changed-package argument (`eslint $CHANGED_FILES`,
   `cargo clippy --no-deps -p $CHANGED_PACKAGE`, `pytest path/to/dir`)
   over project-wide ones; (b) **reject** any command whose typical
   wall-clock on this repo exceeds 3 s; (c) **record a wall-clock
   estimate** alongside each cached command. Project-wide commands
   exceed the budget on any non-trivial repo, return `timeout` on
   every edit, and train the agent to ignore feedback. This is the v1
   difference between "Pillar 7 works" and "Pillar 7 looks like it
   works." The cache file format is one command per line; comments
   (`#`) and empty lines are skipped; malformed lines are dropped
   silently. Robust to truncation by construction.

### Dogfood metrics (wire up from day one)

These five metrics determine whether v1 is succeeding, what v2 should
build, and whether any of the cuts (notably the `Stop` hook) need to
be reversed. Each is a single counter or rate, not a dashboard.

- **Discipline firing rate** — registrations per session and ADRs per
  session. If registrations drop after week one, the inject is being
  downweighted under long context (the `Stop` hook returns as a v2
  safety net).
- **Marker-without-registry rate** — TODO/FIXME/HACK/XXX markers
  Claude wrote in a session minus the count of registry entries it
  created the same session. Non-zero means Discipline 1 is not firing
  reliably; this is the explicit dogfood detection for the `Stop` hook
  cut.
- **ADR creation rate** — ADRs per week. Below ~0.1/week or above
  ~1/day means the architectural-significance heuristic in Discipline
  2 is broken; v2's `adr-author` subagent is the structural fix.
- **`feedback.sh` action rate** — fraction of edits where the agent
  visibly self-corrects after a non-pass result. If <50%, the
  `additionalContext`-acted-on-same-turn assumption (an open question
  since the audit) is false; escalate to v2.
- **Registry growth and AI-touched share** — total entries over time
  and the share with `ai_authored: true`. Rising AI-touched share is
  the leading indicator that v3's behavioral measurement (CodeScene
  MCP) is needed sooner than later.

These five are the minimum to ship v1 with credibility. Other edge
cases the design considered (monorepo single-command-set spray;
CLAUDE.md "no TODO" rule conflict; very large registries straining
Discipline 3) are acceptable v1 risk if these metrics are wired up
from week one.

---

## Closing

Two skills, two hooks, two short scripts, no `userConfig`, zero
required CLAUDE.md modifications, zero install-time footprint in the
user's repo. The plugin works on the first edit of the first session.
`/debt:init` is opt-in (and `disable-model-invocation: true` to prevent
auto-invocation), not setup; lazy creation handles everything else.

The bet: install the plugin, get value immediately. The charter, when
present, is the team-shared source of truth. When absent, the plugin's
own SessionStart inject covers the same ground per-session. Nothing in
the user's repo until the developer asks for it.

If the v1 plugin disappears into the developer's workflow and they
notice it only when the agent caught a quality issue or registered debt
they would otherwise have lost, the design worked.
