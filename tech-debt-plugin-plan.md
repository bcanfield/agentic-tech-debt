# Tech Debt: Claude Code Plugin v1 Spec

## Why this document exists

`tech-debt-pillars.md` is tool-agnostic. This document commits those pillars
to a concrete, buildable v1 plugin and names what we deliberately don't
build yet.

**The principle.** Claude Code is the agent doing the work. The plugin is a
thin helper. Anywhere the plugin is doing what Claude could do, we cut it.

**Enable-and-go.** Installing the plugin creates zero files in the user's
repo. The plugin works on the first agent edit. Setup ceremony, AGENTS.md
modifications, and pre-creating directories are opt-in (`/debt:init`), not
required.

**What v1 ships.** Two skills (`/debt:init` opt-in, `/debt:add`), two hooks
(`SessionStart`, `PostToolUse`), two short scripts. No templates, no
examples, no `userConfig`, no required AGENTS.md modifications.

**Hard prerequisite.** A git repository.

## The two non-negotiables

1. **Lean relaxed over strict.** v1 has zero blocking rules. The
   `PostToolUse` hook surfaces quality-check results to the agent; nothing
   is rejected. Strict gates arrive in v3.
2. **Passive, plays well with others.** No `agent` override. Namespaced
   commands only (`/debt-ops:*`). Hooks call the project's existing
   tooling. Nothing is created in the user's repo until the developer asks
   for it.

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
  AGENTS.md so the team shares one source of truth.
- **Indifferent: vibe coder (Persona 1).** v1 is near-silent on projects
  with no detectable quality commands.
- **Out of scope: enterprise platform tier (Persona 4).** Spotify Honk /
  AWS Transform / internal platforms cover this.
- **Wrong layer: OSS maintainers (Persona 5).** Their pain is at PR
  triage; v1 lives in the contributor's editor.

---

## How it works (the whole plugin in one paragraph)

On every session, a `SessionStart` hook checks plugin-data cache for this
repo's quality commands. On the first session it injects context asking
Claude to scan the repo and cache the result; on subsequent sessions it
reads the cache instantly. The same hook injects the disciplines
(auto-register debt, draft ADRs in Nygard format). After every agent edit,
`PostToolUse → feedback.sh` runs the cached commands in parallel under a
3 s budget and returns structured pass/fail. When Claude writes an
expedient marker during normal work, the discipline tells it to invoke
`/debt-ops:add` immediately; the skill loads the schema, lazily creates
`debt/registry/`, writes the entry, and announces. The developer interacts
with debt entries through chat ("drop that one") or the editor's file
tree, referring to entries by content rather than ID. `/debt:init` is an
optional persistence step that writes the disciplines and commands into
AGENTS.md so the team shares one source of truth; solo users skip it.

---

## The disciplines (injected by `SessionStart`)

These four short instructions are what `SessionStart` injects into Claude's
context every session. They live inside `session-start.sh` as a heredoc;
there is no separate `disciplines.md` file. If `AGENTS.md` or `CLAUDE.md`
already has a `## Tech debt operations` section (because `/debt:init` was
run), those instructions take precedence; the inject is the fallback.

1. When you write a `TODO`, `FIXME`, `HACK`, or `XXX` marker that's real
   debt (a known shortcut, an incomplete case, a fragile assumption),
   register it via `/debt-ops:add` immediately. No permission prompt; just
   do it and announce. Use `payoff_trigger: unknown` if unsure. Trivial
   markers (style nits) don't earn an entry; use judgment.
2. When making an architecturally significant change (data model, public
   interface, dep manifest, security boundary, release pipeline), draft an
   ADR under `doc/adr/` in Nygard format (Context, Decision, Consequences,
   Alternatives, Payoff trigger). Create the directory if needed.
3. Read entries under `debt/registry/` before changing files they
   reference.
4. Refer to debt entries and ADRs by content in conversation, not by ID.
   IDs are for tooling cross-references like commit SHAs.

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
| 6. Curated Agent Context | rely on Claude Code's native `AGENTS.md`/`CLAUDE.md` loading; `/debt:init` (opt-in) writes a debt-ops section for team-share | enforced size budget, freshness checks (v2) |
| 7. In-Loop Deterministic Feedback | `PostToolUse → feedback.sh` runs commands cached by SessionStart (or read from AGENTS.md if `/debt:init` ran) | test-integrity rule, AI-touched hotspot floor rule, `/debt:override` (v3) |
| 8. Spec → Test → Review → Comprehend | — | `/debt:spec`, `/debt:explain`, `reviewer`, `security-reviewer` (v2/v3) |
| 9. AI as Paydown Engine | — | `/debt:paydown`, GH Actions recipe (v3) |

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

- We rely on Claude Code's native `AGENTS.md` / `CLAUDE.md` loading. We
  don't reinvent it.
- `/debt:init` (opt-in) writes a `## Tech debt operations` section into
  the existing charter so the disciplines and commands persist with the
  repo and travel to other team members and other AI tools (Cursor, Aider,
  Codex). It does **not** create a charter from scratch; Claude Code's
  built-in `/init` already does that.
- For solo users who skip `/debt:init`, the SessionStart inject covers the
  disciplines per-session. Nothing is written to the repo.

**Honest caveat.** Pillar 6 calls for an *enforced* size budget and
freshness checks. v1 has neither; we trust Claude's reading of whatever
charter exists. Size-budget enforcement returns in v2 if dogfood shows
charter bloat is a real problem.

---

### Pillar 7: In-Loop Deterministic Feedback

**v1 commitment.**

- `SessionStart` hook (`session-start.sh`) detects this repo's quality
  commands and caches them in `${CLAUDE_PLUGIN_DATA}/feedback.list`. On
  first session: inject context asking Claude to scan project files and
  write the cache. On subsequent sessions: read the cache instantly. If
  `AGENTS.md` or `CLAUDE.md` has a `<!-- debt-ops:feedback -->` marker
  block (because `/debt:init` ran), the cache is overridden by that;
  charter is the source of truth when present.
- `PostToolUse` matcher (`Write|Edit|MultiEdit`) calls `feedback.sh`. The
  script (~15 lines) reads commands from cache or charter, runs each in
  parallel under a 3 s wall-clock budget, and returns structured JSON
  `{<command>: pass|fail, ...}` to the agent.

**Trust boundary.** The agent can *propose* commands by editing AGENTS.md
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
│   └── plugin.json              # name, version, description; empty userConfig
├── skills/
│   ├── add/SKILL.md             # /debt:add (registry schema embedded in prompt)
│   └── init/SKILL.md            # /debt:init (opt-in: writes section to AGENTS.md)
├── hooks/
│   └── hooks.json
├── scripts/
│   ├── session-start.sh         # detects + caches commands; injects disciplines
│   └── feedback.sh              # ~15 lines: read commands, run in parallel, return JSON
└── README.md
```

Two skills, two hooks, two scripts. No templates, no examples, no config
files. Anyone can grok the plugin in five minutes.

**`plugin.json`.**

```json
{
  "name": "debt-ops",
  "version": "0.1.0",
  "description": "Continuous, evidence-based tech debt management for Claude Code.",
  "userConfig": {},
  "dependencies": []
}
```

Zero `userConfig` keys. Zero install-time questions.

---

## Hook layout (v1)

| Event | Matcher | Script | What it does |
|---|---|---|---|
| `SessionStart` | — | `session-start.sh` | inject disciplines; if `${CLAUDE_PLUGIN_DATA}/feedback.list` exists, also inject the command list; otherwise inject a one-time prompt asking Claude to detect and write the cache |
| `PostToolUse` | `Write\|Edit\|MultiEdit` | `feedback.sh` | read commands (charter marker block if present, else cache); run each in parallel (3 s budget); return structured JSON to the agent |

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
| Required `/debt:init` | skip | Plugin works on enable; `/debt:init` is opt-in for team-share. | We would never make it required again. |
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
| Charter bootstrap (creating AGENTS.md from scratch) | skip | Claude Code's built-in `/init` already does this. | Never; overlap with native is the failure mode. |
| Pre-creating `debt/registry/` and `doc/adr/` on install | skip | Lazy creation on first use; install footprint is zero. | We would choose lazy again. |
| GitHub Actions example | skip | Ships with `/debt:paydown`. | v3. |

---

## How we coexist with other plugins

1. **Namespace everything.** `/debt-ops:*` only.
2. **No global `agent`.** We never set `settings.json` `agent`.
3. **Hooks call project tooling, not replace it.** The detected commands
   are the project's own.
4. **Charter respects ownership.** `AGENTS.md` and `CLAUDE.md` belong to
   the project; we only modify them through opt-in `/debt:init`.
5. **Soft hooks, structured outputs.** Hook results are structured JSON;
   other plugins can read or skip without text-matching.
6. **Zero install footprint.** Files in the user's repo only appear when
   the developer asks for them (registry entries on `/debt:add`;
   AGENTS.md edits on `/debt:init`).

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
6. **Hook ordering across plugins.** We assume hooks are commutative.
7. **Non-git repos.** Most of the plugin is a no-op without git.

---

## A day in the life (v1)

A senior engineer, mid-sized Rust service, `debt-ops` v0.1.0 installed
today.

**08:50, open editor.** First-ever session with the plugin. `SessionStart`
injects: "Disciplines: [the four]. First session for this repo: please
detect quality commands by scanning project files (`Cargo.toml`, etc.) and
write them to `${CLAUDE_PLUGIN_DATA}/feedback.list`." Claude does so
silently: `cargo check`, `cargo clippy --no-deps -- -D warnings`, `cargo
test`. The cache is now warm. Total: ~3 s. The developer sees nothing.

**09:15, start the work.** They tell Claude to refactor a callback chain
in `pricing/engine.rs`.

**09:17, first edit lands.** `feedback.sh` reads the cache, runs `cargo
check` and `cargo clippy` in parallel (1.4 s), then `cargo test` (5.8 s).
The agent sees `{"cargo check": "pass", "cargo clippy": "pass", "cargo
test": "pass"}` and continues.

**09:35, a subtle expediency.** Claude proposes `// TODO: handle the
cancelled-promotion case later`. Discipline 1 fires. Claude invokes
`/debt-ops:add`, lazily creates `debt/registry/` (the first file ever in
this dir), writes `0001-cancelled-promotion-callback.md` with
`payoff_trigger: unknown`, and announces: "Registered the
cancelled-promotion entry. Tell me to drop it if it's not real debt."

**10:05, a false positive.** Claude flags `// TODO: maybe rename this var`
and registers it. Developer: "that's just a naming nit, drop it." Claude
deletes the entry. Done.

**11:30, an architectural fork.** Claude wants a new pricing-event trait.
Discipline 2 fires. Claude lazily creates `doc/adr/` (the first file in
this dir too), writes `0001-pricing-event-trait.md` in Nygard format with
a payoff trigger. The developer reviews and edits.

**16:00, end of day.** No Stop hook. Today's debt activity is visible in
`git diff`: one registry entry, one ADR, both under directories the
plugin lazily created.

**Tomorrow.** `SessionStart` reads the cache (instant), injects
disciplines and commands; the plugin runs.

**Some weeks later.** The team has grown to four developers. They want
everyone to share the same disciplines and commands, and the AGENTS.md to
describe the project's debt-ops conventions for Cursor users on the team.
One dev runs `/debt-ops:init`. It writes a `## Tech debt operations`
section into AGENTS.md with the disciplines and a marker block containing
the cached commands. They commit. The charter is now the source of truth
(the SessionStart inject defers to it when present). New team members get
the config without installing the plugin.

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

All of them. v1 has empty `userConfig`. Per-user overrides return in v2+
if needed.

---

## Anti-patterns we will actively watch for

1. **Hook latency creep.** The 3 s aggregate budget for `feedback.sh` is
   the line.
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

## Closing

Two skills, two hooks, two short scripts, empty `userConfig`, zero
required AGENTS.md modifications, zero install-time footprint in the
user's repo. The plugin works on the first edit of the first session.
`/debt:init` is opt-in, not setup; lazy creation handles everything else.

The bet: install the plugin, get value immediately. The charter, when
present, is the team-shared source of truth. When absent, the plugin's
own SessionStart inject covers the same ground per-session. Nothing in
the user's repo until the developer asks for it.

If the v1 plugin disappears into the developer's workflow and they
notice it only when the agent caught a quality issue or registered debt
they would otherwise have lost, the design worked.
