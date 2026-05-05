# Tech Debt — Claude Code Plugin v1 Spec

## Why this document exists

`tech-debt-pillars.md` is tool-agnostic on purpose. This document commits
those pillars to a concrete, buildable v1 plugin — and is honest about
what we are deliberately not building yet.

**The principle.** Claude Code is the agent doing the work. The plugin
is a thin helper. Anywhere the plugin is doing what Claude could do, we
cut it. Disciplines live in the charter (`AGENTS.md` / `CLAUDE.md`)
where Claude already reads them. The plugin contributes only what
genuinely needs deterministic enforcement — which in v1 is one thing:
running the project's quality commands after every agent edit.

**What v1 ships.** Two skills (`/debt:init`, `/debt:add`), one hook
(`PostToolUse → feedback.sh`), one tiny script, three templates. That's
it.

**Hard prerequisite.** A git repository.

## The two non-negotiables

1. **Lean relaxed over strict.** v1 has zero blocking rules. The hook
   surfaces quality-check results to the agent; nothing is rejected.
   Strict gates arrive in v3 with `/debt:override`.
2. **Passive, plays well with others.** No `agent` override. Namespaced
   commands only (`/debt-ops:*`). Hooks call the project's existing
   tooling. The charter is the project's `AGENTS.md` / `CLAUDE.md`,
   not ours.

---

## Working name

`debt-ops` — namespaces to `/debt-ops:*`. Commands are written `/debt:*`
in this doc for brevity.

---

## Who v1 is for

Based on workflow research across five personas (vibe coder, solo
brownfield, small team, enterprise, OSS maintainer):

- **Bullseye: solo brownfield (Persona 2).** A senior IC adding agentic
  tooling to an established codebase that already has lint, types,
  tests, and conventions. v1 maps directly to their day.
- **Strong foundation: small team, 2–10 devs (Persona 3).** Team-
  shareable markdown registry + AGENTS.md detection + quality-check
  enforcement land cleanly. Their hottest pains (charter ownership
  drift, prompt sprawl, cognitive debt) are v2/v3 concerns; v1 is
  table stakes.
- **Indifferent: solo greenfield / vibe coder (Persona 1).** v1 is
  near-silent on these projects (no quality commands declared = hook
  no-ops). They neither benefit nor suffer.
- **Out of scope: enterprise platform tier (Persona 4).** Spotify Honk,
  AWS Transform, internal platforms cover this surface area. May
  re-evaluate at v3 with audit trails.
- **Wrong layer: OSS maintainers (Persona 5).** Their pain is at PR
  triage; v1 lives in the contributor's editor. The one tangential
  win is AGENTS.md primacy.

---

## How it works (the whole plugin in one paragraph)

`/debt:init` adds a `## Tech debt operations` section to the existing
`AGENTS.md` (or `CLAUDE.md`) and creates the registry and ADR
directories. It does **not** create a charter from scratch — Claude
Code's built-in `/init` already does that, and we don't compete with
it. The section it adds contains short discipline instructions (when
to register debt, when to draft an ADR, the size reminder) and a
marker-bracketed bash block listing the project's quality commands.
After every agent edit, `feedback.sh` greps that block from the
charter, runs each command in parallel under a 3 s budget (tests
async; reports at next stop), and returns structured pass/fail to
the agent. `/debt:add` lets the developer (or the agent, when
prompted by the charter discipline) write a registry entry from
current context. That's the plugin.

---

## The charter section that `/debt:init` writes

This section lives inside `AGENTS.md` / `CLAUDE.md`. It is the **only**
configuration the plugin has — and it lives where Claude already reads
it.

````markdown
## Tech debt operations

This project uses debt-ops for continuous tech-debt management.

**Discipline.** Follow these on every session:

1. When writing a `TODO`, `FIXME`, or "I'll fix later" marker, suggest
   the developer register it via `/debt-ops:add`. Don't ship debt
   silently.
2. When making an architecturally significant change (data model,
   public interface, dep manifest, security boundary, build/release
   pipeline), draft an ADR under `doc/adr/` using the template.
3. Keep this section under 200 lines. If it grows past that, suggest
   tightening.
4. The registry lives at `debt/registry/`. Read it before proposing
   changes that touch a flagged hotspot.

**Registry entry schema.** Five required fields plus quadrant and
category. See `doc/adr/` and `debt/registry/0001-example-debt.md` for
shape.

**Quality checks.** These run automatically after every file edit.
Keep them current as the project evolves.

<!-- debt-ops:feedback start -->
```bash
cargo check
cargo clippy --no-deps -- -D warnings
cargo test
```
<!-- debt-ops:feedback end -->
````

The discipline lives where Claude reads it. The plugin enforces only
what's inside the marker block — that's the trust boundary.

---

## The registry schema

Each entry under `debt/registry/` is a markdown file with YAML front-
matter:

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

**Category** (Google / Jaspan-Green, closed enum): `migration`,
`documentation`, `testing`, `code_quality`, `dead_code`, `code_rot`,
`expertise`, `release`, `infrastructure`, `planning`.

`payoff_trigger: unknown` is first-class; ages into stale review at v2.

ADRs use Nygard format with one extension — a required `payoff_trigger`
field when the ADR introduces deliberate debt.

---

## The v1 commitment

| Pillar | v1 | Deferred |
|---|---|---|
| 1. Visibility | `/debt:add`; registry under `debt/registry/`; charter discipline tells Claude when to suggest registration | `/debt:list` ranking, stale aging, ADR auto-pairing (v2) |
| 2. Continuous Measurement | static layer via Pillar 7's quality checks | behavioral signal, AI-touched windows, DORA, perception (v3) |
| 3. Hotspot Prioritization | — | `/debt:list` + `triage` subagent (v2) |
| 4. Continuous Paydown | — | `/debt:budget`, fix-it weeks, Boy Scout summary (v4) |
| 5. Deliberate Architecture | ADR template + charter discipline that nudges Claude to draft when needed | `/debt:adr` skill, index regen (v2) |
| 6. Curated Agent Context | `/debt:init` writes into `AGENTS.md`/`CLAUDE.md`; charter discipline includes its own size-budget reminder | richer freshness checks (v2 if charter discipline proves unreliable) |
| 7. In-Loop Deterministic Feedback | `PostToolUse → feedback.sh` runs the marker-bracketed block from the charter | test-integrity rule, AI-touched hotspot floor rule, `/debt:override` (v3) |
| 8. Spec → Test → Review → Comprehend | — | `/debt:spec`, `/debt:explain`, `reviewer`, `security-reviewer` (v2/v3) |
| 9. AI as Paydown Engine | — | `/debt:paydown`, GH Actions recipe (v3) |

---

## Pillar-by-pillar v1 mapping

### Pillar 1 — Visibility

**v1 commitment.**

- `/debt:add` — Claude drafts a registry entry from current context,
  fills the schema, asks for any missing required field, writes to
  `debt/registry/<id>-<slug>.md`. `payoff_trigger: unknown` is
  allowed. The skill is a thin prompt that loads the schema; Claude
  does the work.
- Charter discipline (item 1): when Claude writes a TODO/FIXME, it
  suggests `/debt:add`. No hook needed — Claude self-monitors because
  it just read the charter.

**Deferred to v2.** Ranking, filters, the `triage` subagent,
`/debt:list` (chronological listing falls out of "ask Claude to read
the dir" until the skill earns its slot with ranking).

---

### Pillar 2 — Continuous Measurement

**v1 commitment.** Static layer only, via Pillar 7 (quality commands
run on every edit).

**Deferred to v3.** Behavioral signal via optional `code-health` MCP;
AI-touched discriminator and 30/60/90/14-day windows; DORA file
reader. We considered a local "lines × git frequency" hotspot scorer;
on review it's a misleading complexity proxy. We commit to honest
"behavioral signal unavailable until you wire up an MCP" rather than
fake it.

---

### Pillars 3, 4, 8, 9 — deferred entirely from v1

- **Pillar 3 (Hotspot Prioritization).** Developers fall back to
  existing prioritization until v2 lands `/debt:list` ranking + the
  `triage` subagent.
- **Pillar 4 (Continuous Paydown).** No direct commitment. v1 *enables*
  future accounting because the registry exists — `Debt-Pays-Down:
  <id>` trailers can accumulate from day one. `/debt:budget`, fix-it
  weeks, and Boy Scout summary arrive in v4 (needs v3's Code Health
  signal first).
- **Pillar 8 (Spec → Test → Review → Comprehend).** No commitment.
  `/debt:spec`, `/debt:explain`, `reviewer`, `security-reviewer`,
  comprehensibility prompt all arrive in v2/v3. v1's contribution is
  ensuring the charter exists and is read; the disciplines are taught
  through charter content.
- **Pillar 9 (AI as Paydown Engine).** No commitment. Pillar 9 needs
  Pillars 3, 7-full, and 8 to all be live. `/debt:paydown` skill +
  external scheduling recipe arrive in v3.

---

### Pillar 5 — Deliberate Architecture

**v1 commitment.**

- `/debt:init` creates `doc/adr/` and seeds it with a Nygard-format
  template (`0001-template.md`) including a `payoff_trigger` field.
  The template content lives inside `/debt:init`'s SKILL.md prompt,
  not as a separate `templates/` file — Claude writes it from the
  prompt.
- Charter discipline (item 2) tells Claude when to draft an ADR.

**Deferred to v2.** `/debt:adr` skill (draft from context), ADR index
regeneration, architectural-touch heuristic detection.

---

### Pillar 6 — Curated Agent Context

**v1 commitment.**

- `/debt:init` auto-detects `AGENTS.md` (preferred — multi-tool
  convention used by Cursor, Aider, Codex, Claude Code) or
  `CLAUDE.md`. **If neither exists, the skill tells the user to run
  Claude Code's built-in `/init` first.** We don't reinvent charter
  bootstrapping; we add one section to a charter someone else already
  put there.
- Charter discipline (item 3) is the size-budget reminder. Claude
  reads it on every session and flags growth.

**Honest caveat on enforcement.** Pillar 6 calls for an *enforced*
size budget. v1 has self-monitoring (Claude flags growth as part of
the charter discipline), not enforcement. If dogfood shows the
discipline drifts — Claude doesn't reliably notice growth — a
deterministic `SessionStart` size check returns in v2 as a safety
net.

**Deferred.** Automated freshness/staleness checks. v1 trusts
Claude's read; v2 brings deterministic backstops if needed.

---

### Pillar 7 — In-Loop Deterministic Feedback

**v1 commitment.**

- One `PostToolUse` matcher (`Write|Edit|MultiEdit`) calls
  `feedback.sh`. The script (~15 lines):
  1. `sed` the marker-bracketed bash block from the charter.
  2. Run each non-comment line in parallel under a 3 s wall-clock
     budget for fast checks.
  3. The test slice (any line containing `test`) runs async; the
     result is delivered at the next `Stop`.
  4. Return structured JSON: `{<command>: pass|fail|pending, ...}`.

The trust boundary: the agent can *propose* commands by editing
`AGENTS.md`; it doesn't get to *skip* them at edit time because the
hook runs deterministically from the file.

**Deferred to v3.**

- Test-integrity rule (rejects diffs that delete or weaken tests in
  the same session as the production code those tests covered).
- AI-touched hotspot floor rule (`ai_touched_min_health`, default
  9.4).
- `/debt:override <reason>` skill — audit-trail escape.
- AI-touched tagging.
- The optional `code-health` MCP wiring.
- **Charter-tampering rule**: extend the test-integrity rule to also
  flag removal or weakening of the `<!-- debt-ops:feedback -->` block
  in the same session as code changes. Same shape as test deletion.

v1 is the relaxed-by-construction version. No rejections. Just
feedback.

---

### Pillar 8 — Spec → Test → Review → Comprehend

**v1 commitment.** None.

**Deferred to v2/v3.** `/debt:spec`, `/debt:explain`, the `reviewer`
subagent (with comprehensibility mode), the `security-reviewer`
subagent, the `pre-commit.sh` comprehensibility prompt. v1's
contribution is making sure the charter exists and is read; the
disciplines themselves are taught via charter content.

---

### Pillar 9 — AI as a Paydown Engine

**v1 commitment.** None. Pillar 9 needs Pillars 3, 7-full, and 8 to
all be live.

**Deferred to v3.** `/debt:paydown` skill + GH Actions example for
external scheduling.

---

## Plugin layout (v1)

```
debt-ops/
├── .claude-plugin/
│   └── plugin.json              # name, version, description; empty userConfig
├── skills/
│   ├── init/SKILL.md            # /debt:init (charter section + ADR template embedded in prompt)
│   └── add/SKILL.md             # /debt:add (registry schema embedded in prompt)
├── hooks/
│   └── hooks.json               # one entry: PostToolUse → feedback.sh
├── scripts/
│   └── feedback.sh              # ~15 lines: sed + parallel run + JSON
└── README.md
```

Two skills, one hook, one tiny script. The charter section, the ADR
template, and the registry schema all live inside the SKILL.md
prompts — Claude writes the files from those prompts. We don't ship
them as separate static files because that would be duplicating
content Claude can produce from instructions. Anyone can grok the
plugin in five minutes.

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

Zero `userConfig` keys. Zero install-time questions. The plugin
configures itself when `/debt:init` runs.

---

## Hook layout (v1)

| Event | Matcher | Script | What it does |
|---|---|---|---|
| `PostToolUse` | `Write\|Edit\|MultiEdit` | `feedback.sh` | sed the marker-bracketed bash block from `AGENTS.md`/`CLAUDE.md`; run each line in parallel (3 s budget for fast checks; tests async); structured JSON to agent |

One hook. The other lifecycle disciplines live in the charter where
Claude reads them.

---

## What we skip in v1 (and when each could return)

Every cut is recoverable. Nothing is permanently off the table.

| Primitive | v1 decision | Why now | Could return when |
|---|---|---|---|
| `userConfig` | empty | Charter is the source of truth; install-time questions add friction. | If a per-user override (e.g., one dev's `cargo check --all-features`) is needed without changing the shared charter. |
| `SessionStart` hook | skip | Charter discipline asks Claude to verify charter health; Claude reads charter every session anyway. | If dogfood shows charter discipline isn't reliable enough — fast bash check is the safety net. |
| `Stop` hook | skip | Charter discipline tells Claude to suggest `/debt:add` when it writes TODO/FIXME; the agent self-monitors. | Same as above — if reliability fails, a Stop-hook todo-sniff returns. |
| `/debt:list` skill | skip | Claude can `ls debt/registry/`; v2 brings the skill back with ranking. | v2 (with `triage` ranking). |
| `commands/` (legacy flat) | skip | Skills supersede. | (we'd choose skills again) |
| `themes/` | skip | Out of scope. | If we ship a visual mode (e.g., paydown-session theme). |
| `bin/` | skip | No standalone CLI use yet. | Once a script earns shell-level use. |
| `.lsp.json` | skip | Anthropic ships LSP plugins for major languages. | Niche language target. |
| `output-styles/` | skip | Heavyweight for nudges. | Sustained-tone modes (e.g., security review). |
| `monitors/` | skip | Nothing in v1 needs background reactions. | v3+ for fix-it-week reactivity, CI status. |
| `channels` | skip | No external messaging. | Slack/Telegram/Discord bridges. |
| `settings.json` `agent` override | skip | Hostile to other plugins. | Only inside an explicit time-boxed mode (hypothetical `/debt:focus`). |
| Subagents (`agents/`) | skip | Skills handle drafting; the hook handles enforcement. | v2 brings `debt-scribe`, `triage`, `reviewer`; v3 adds `security-reviewer`. |
| `.mcp.json` | skip | No code-health MCP needed yet. | v3 (Code Health signal). |
| Local hotspot scorer | skip | "Lines × git frequency" is a misleading complexity proxy. | Tree-sitter-based scoring (~20 lines per language) if we want a no-MCP fallback. |
| Auto-detection bash table | skip | `/debt:init` is a Claude prompt — Claude reads the repo and detects directly. | If we ever need detection in a non-interactive context. |
| `templates/` directory | skip | Charter section and ADR template content live inside `/debt:init`'s SKILL.md prompt; Claude writes them from instructions. | If a template grows complex enough that embedding it in a prompt is unwieldy. |
| `examples/` directory | skip | Schema/example for registry entries lives inside `/debt:add`'s SKILL.md. | If users ask for human-readable example files in their repo. |
| Charter bootstrap (creating AGENTS.md from scratch) | skip | Claude Code's built-in `/init` already does this. We only add a section to an existing charter. | Never — overlap with native is the failure mode. |
| GitHub Actions example | skip | Ships with `/debt:paydown`. | v3. |

---

## How we coexist with other plugins

1. **Namespace everything.** `/debt-ops:*` only.
2. **No global `agent`.** We never set `settings.json` `agent`.
3. **Hooks call project tooling, don't replace it.** The marker block
   contains the project's own commands.
4. **Charter respects ownership.** `AGENTS.md` / `CLAUDE.md` is the
   project's; `/debt:init` adds *one* section; never overwrites.
5. **Soft hooks, structured outputs.** Hook results are structured
   JSON; other plugins/hooks can read or skip without text-matching.

---

## Gaps in Claude Code primitives

1. **Cron / scheduling.** Pillar 9 needs an external scheduler (GH
   Actions). v3 ships the recipe.
2. **Cross-PR allocation accounting.** v4's `/debt:budget` is git-
   driven, survives plugin uninstall.
3. **Engineer-perception survey loop.** Out of plugin scope.
4. **DORA outcome telemetry.** Out of plugin scope; v3 reads
   `debt/dora.json` if produced externally.
5. **Bug cap.** Out of plugin scope.
6. **Hook ordering across plugins.** We assume hooks are commutative.
7. **Non-git repos.** Most of the plugin is a no-op without git.

---

## A day in the life (v1)

A senior engineer, mid-sized Rust service, `debt-ops` v0.1.0
installed.

**08:50 — Open editor.** No SessionStart hook fires; Claude loads
`AGENTS.md` natively, reads the debt-ops section, knows the
disciplines.

**09:10 — First-ever invocation.** They already have an `AGENTS.md`
(set up earlier by Claude Code's built-in `/init`). They run
`/debt-ops:init`. Claude reads the repo, sees `Cargo.toml` and a
`tests/` directory, appends a `## Tech debt operations` section to
`AGENTS.md` with the disciplines and a marker block containing
`cargo check`, `cargo clippy --no-deps -- -D warnings`, and `cargo
test`. It creates `debt/registry/` and `doc/adr/`, dropping a
Nygard-format template into `doc/adr/0001-template.md`. Total time:
about a minute.

**09:15 — Start the work.** They open a callback chain in
`pricing/engine.rs` and tell Claude to refactor.

**09:17 — First edit lands.** `feedback.sh` greps the marker block,
runs `cargo check` and `cargo clippy` in parallel (1.4 s); test slice
queued. Both pass. The agent sees `{"cargo check": "pass", "cargo
clippy": "pass", "cargo test": "pending"}` and continues.

**09:19 — Test slice returns at next Stop.** Two failing tests; the
agent sees them, fixes one, flags the other.

**09:35 — A subtle expediency.** Claude proposes `// TODO: handle the
cancelled-promotion case later`. Because the charter discipline tells
Claude to suggest registering TODOs, Claude says: "Want me to register
this with `/debt-ops:add`?" Developer: "yes." Claude runs `/debt:add`,
fills the schema from context, marks `payoff_trigger: unknown`, files
`debt/registry/0042-cancelled-promotion-callback.md`. Total: ~20
seconds.

**11:30 — Architectural fork.** Claude wants a new pricing-event
trait. The charter discipline says to draft an ADR for that. Claude
proposes one inline; the developer accepts; it lands at
`doc/adr/0007-pricing-event-trait.md`.

**16:00 — End of day.** No Stop summary fires. The developer's
session-tracking is the conversation itself plus the registry diff.

The throughline: the plugin is mostly silent; Claude does the
reading-and-noticing; the hook only fires when there's a quality
result to report.

---

## Beyond v1 — roadmap

### v2 — ranking + ADR + reviewer

- `/debt:list` (with ranking + filters) and `triage` subagent.
- `/debt:adr` skill, ADR index regeneration.
- `/debt:spec`, `/debt:explain` skills.
- `reviewer` subagent (with comprehensibility mode).
- `debt-scribe` subagent (now that drafting is multi-format).
- Possibly: `SessionStart` and `Stop` hooks return as safety nets if
  charter discipline proves unreliable in dogfood.
- `PreToolUse` on `git commit` for the comprehensibility prompt.

### v3 — enforcement + paydown engine

- `feedback.sh` extends with: test-integrity rule, AI-touched hotspot
  floor rule, AI-touched tagging, charter-tampering rule (block
  removal in same session as code changes).
- `/debt:override <reason>` skill.
- `code-health` MCP wiring (`code_health_mcp_endpoint` userConfig
  returns).
- `/debt:health` skill with `--ai-only`, `--window=…`, `--churn=…`.
- `/debt:paydown` skill + GH Actions example.
- `security-reviewer` subagent.

### v4 — allocation + Boy Scout

- `/debt:budget` (with `--fixit start|end`).
- Boy Scout one-line summary at session end.
- `debt/dora.json` and `debt/bug-cap.json` external readers surfaced
  in `/debt:budget`.

**Validation gate.** Dogfood the previous version on the plugin's own
repo for at least one full week before promoting.

---

## Future possibilities (beyond v1–v4)

Items not pinned to a phase. Captured here so they're not lost.

### Skills considered and cut

- `/debt:next` — folded into v2's `/debt:list`.
- `/debt:fixit-week` — folded into v4's `/debt:budget --fixit`.
- `/debt:charter-check` — handled by charter discipline; could split
  out as an explicit skill if needed.
- `/debt:strict-mode` — could return as a `userConfig` flag or as
  part of a hypothetical `/debt:focus` mode.
- `/debt:tdd`, `/debt:survey` — speculative; only if dogfood shows a
  clear need.

### Subagents considered and cut

- `adr-author` — folded into v2's `debt-scribe`.
- `comprehensibility-checker` — folded into v2's `reviewer` (mode
  arg).
- `paydown-runner` — v3's `/debt:paydown` uses the writer thread.

### Hooks / scripts considered and cut

- **`SessionStart` and `Stop` hooks** — replaced by charter
  discipline. Could return as safety nets if Claude doesn't reliably
  follow the charter (test in v2 dogfood).
- `Skip-Debt-Ops:` magic-string trailer — replaced by v3's
  `/debt:override <reason>` skill.
- AI-touched marker file — v3 uses `Co-authored-by:` trailers from
  Claude Code, Cursor, Copilot, Aider.
- Bash auto-detection table — replaced by Claude doing detection in
  `/debt:init`.

### Other primitives

- Background monitor `fixit-mode-watch` — replaced by charter-driven
  reminders.
- DORA dashboard pushers — out of plugin scope.
- Bug-cap enforcement — out of plugin scope.
- Engineer-perception survey aggregation — out of plugin scope.
- Tree-sitter-based hotspot scoring — possible no-MCP fallback at v3.

### userConfig keys considered and cut

All of them. v1 has an empty `userConfig` block. Configuration lives
in the charter section (AGENTS.md/CLAUDE.md); per-team paths are
hard-coded defaults; per-user overrides are a v2+ feature if needed.

---

## Anti-patterns we will actively watch for

1. **Hook latency creep.** The 3 s aggregate budget is the line.
2. **Skill explosion.** Anything <1×/week in dogfood is a removal
   candidate.
3. **Charter rot in our own dogfood.** Our `AGENTS.md`'s debt-ops
   section obeys its own size budget.
4. **Reinventing detection.** If we add bash auto-detection logic
   anywhere, we should ask "could `/debt:init` do this in a Claude
   prompt instead?"
5. **Optional becoming required.** Any v3 code path that *requires*
   the MCP is a regression.
6. **Output-style or default-agent overrides masquerading as
   "convenience."** Either is a passive-plugin failure.
7. **Charter discipline drift.** If Claude consistently ignores
   charter instructions in dogfood, that's a model problem we can't
   fix — but it's also data that says we should bring back the
   `SessionStart`/`Stop` safety-net hooks.

---

## Closing

Two skills. One hook. One ~15-line script. Empty `userConfig`. Zero
install-time questions. No bundled templates or examples — Claude
writes them from the SKILL.md prompts. No bootstrap of files Claude
Code already bootstraps (we layer onto `/init`'s output). The
charter is the source of truth; the plugin enforces only what
genuinely needs determinism.

The bet: Claude Code is the agent doing the work. The plugin is a
helper that runs the project's quality commands deterministically
after every edit and gives Claude a structured place to register
debt. Everything else lives in the charter, where Claude reads it
anyway.

If the v1 plugin disappears into the developer's workflow and they
notice it only when the agent caught a quality issue or registered
debt they'd otherwise have lost, the design worked.
