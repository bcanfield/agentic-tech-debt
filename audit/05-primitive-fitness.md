# Audit 05 — Primitive Fitness

**Question.** Is every v1 commitment grounded in a specific pillar/research finding, and is the chosen Claude Code primitive the *optimal* primitive for that need?

**Scope.** This pass assumes citation correctness, primitive-correctness (CLAUDE.md vs AGENTS.md, per-repo cache, `additionalContext` envelope, `disable-model-invocation`), and major story cracks have already been resolved by audits 01–04. The audit examines whether the v1 primitive *selection* is the best fit available in the Claude Code toolbox.

---

## A. Roundtrip groundedness

| Commitment | Pillar(s) | Research finding(s) | Verdict | Notes |
|---|---|---|---|---|
| `/debt:add` skill | P1 (Visibility) | Dagstuhl 16162 definition; Kruchten/Nord/Ozkaya five-field entry; Jaspan/Green 10 categories; Fowler quadrant | Well-grounded | Schema embeds the five fields plus quadrant + category. Direct map. |
| `/debt:init` skill (opt-in) | P6 (Curated Agent Context) | Persistent project rules pattern (CLAUDE.md, AGENTS.md, Thoughtworks Adopt: "curated AI instructions"); HumanLayer/Anthropic "keep these short" | Well-grounded | Opt-in is correct posture: charter is project-owned. `disable-model-invocation` is the right guard. |
| `SessionStart` hook | P6 (charter substitute when absent) + P7 (cache for fast loop) + P1/P5 (disciplines) | "Persistent project rules read every session"; CodeScene/CAST "deterministic feedback in the loop"; Nygard ADR | Well-grounded | One hook serves three pillars. Defensible because the per-session inject is the natural CC affordance for "context every session." |
| `PostToolUse` hook (`Write\|Edit\|MultiEdit`) | P7 (In-Loop Deterministic Feedback) | Beck augmented coding (TDD as guardrail); Anthropic/Cursor/Thoughtworks PostToolUse hook pattern; CodeScene 2–5× refactor uplift; DORA 2024 7.2% stability drop | Well-grounded | This is the canonical Pillar 7 mechanism in CC. Exact-list matcher is correct. |
| `session-start.sh` | P6 + P7 + P1 + P5 (carrier for the inject) | — (delivery mechanism) | Well-grounded | Carrier; not pillar-bearing on its own. |
| `feedback.sh` | P7 + (test-integrity warning) | Beck "agents try to delete tests"; CodeScene fast-feedback pattern | Well-grounded | Carrier for P7 plus the v3-preview test-integrity warning. |
| Discipline 1 (auto-register markers) | P1 | Reckless–inadvertent quadrant ("most dangerous cell") + Cunningham "expedient" framing | Well-grounded | Marker → register is the explicit Pillar 1 entry point. |
| Discipline 2 (Nygard ADR for arch-significant changes; "two credible alternatives" rule) | P5 | Nygard 2011; Thoughtworks Adopt; SEI/Kruchten-Nord-Ozkaya "architectural choices are leading source of impactful debt" | Well-grounded | The "two credible alternatives" rule is judgment-bound; see §B6. |
| Discipline 3 (read registry before changing referenced files) | P1 + P5 | Kruchten-Nord-Ozkaya "read existing ADRs before proposing changes"; Pillar 5 "mandatory context-loading" | Well-grounded | Direct map to Pillar 5's "agents read the ADR index before proposing changes." |
| Discipline 4 (refer by content, not ID) | — (UX, not pillar-derived) | None | Acceptable orphan | Plan flags it explicitly: "UX choice; not derived from a pillar." Honest disclosure; not a real orphan. |
| Discipline 5 (spec before edit on non-trivial work) | P8 (Spec → Test → Review → Comprehend) | GitHub Spec Kit; Beck/Willison; METR perception/reality gap | Well-grounded | The lightest possible coverage of Pillar 8 stated as such. |
| Discipline 6 ("registering ≠ fixing"; write the failing test first) | P8 + P7 | Beck's "agents try to delete tests"; Willison comprehensibility framing | Well-grounded | Closes the failure mode where the registry becomes a bypass for missing tests. |
| Registry schema (11-field YAML) | P1 | Five-field core (Kruchten-Nord-Ozkaya) + Fowler quadrant + Jaspan/Green category + AI-touched discriminator (P2 prep) + ADR linkage | Well-grounded | `ai_authored` is the v1 hook for Pillar 2's AI-touched discriminator. `id` carrying timestamp shape (per impl gate 4) is justified in §B4. |
| Lazy creation of `debt/registry/` and `doc/adr/` | "Enable-and-go" non-negotiable + design tenet "graceful over punitive" | Design tenet 2 (graceful) | Well-grounded | Footprint creep is named anti-pattern #7 in the plan. |
| Per-repo cache `${CLAUDE_PLUGIN_DATA}/cache/<repo-hash>/feedback.list` | P7 (fast loop) | "Deterministic feedback inside the agent loop" | Well-grounded | The `<repo-hash>` partition fixes a real defect (one shared cache across all repos for one user). Correct use of the documented `${CLAUDE_PLUGIN_DATA}` per Plugins Field Guide §17. |
| `<!-- debt-ops:feedback v1 -->` marker block | P6 (charter as source of truth when present) | "Charter respects ownership"; persistent project rules best practice | Well-grounded | Self-imposed convention; plan correctly flags CC has no cross-plugin marker contract. |
| 3 s per-command timeout | P7 ("fast loop") + design tenet 5 (deterministic) | Anthropic best practice on hook latency; "the developer is not the one catching trivial mistakes" | Well-grounded | The plan owns that 3 s is plugin-self-imposed; CC default is 600 s. Hook-level `timeout: 5` is the right CC-side guard. |
| Residual-risk #1 (behavioral measurement absent) | P2 deferral | "Static-only is anti-pattern #2 in pillars doc" | Honest deferral | Detection plan named (`ai_authored: true` rate). |
| Residual-risk #2 (no hotspot prioritization) | P3 deferral | Pareto / hotspot rule | Honest deferral | |
| Residual-risk #3 (no allocation defense) | P4 deferral | Cagan/Shopify/Justin Grant | Honest deferral | `Debt-Pays-Down:` PR trailers as raw material is a small but real v1 contribution. |
| Residual-risk #4 (no test-integrity / Code Health gates) | P7 deferral (partial; warning ships) | Beck's "agents try to delete tests"; CodeScene 9.4/10 | Honest deferral | Partially mitigated by impl gate 3 (test-count warning). |
| Residual-risk #5 (partial spec / no fresh-context review / no comprehensibility gate) | P8 deferral | Willison comprehensibility; Anthropic writer/reviewer separation | Honest deferral | Disciplines 5–6 cover spec floor only. |
| Residual-risk #6 (no agentic paydown) | P9 deferral | GitClear asymmetry | Honest deferral | Correctly noted as dependent on 3, 7, 8. |
| Impl-gate 1 (`set -euo pipefail`; non-git handling; macOS `timeout`/`gtimeout`; read-only `${CLAUDE_PLUGIN_DATA}`) | Cross-cutting (script credibility) | — | Well-grounded | Each sub-item maps to a specific failure observed by audit 04. |
| Impl-gate 2 (manifest mtime / hash for cache invalidation) | P7 (correctness of fast loop) | "Stale charter is worse than none" (Pillar 6) by analogy | Well-grounded | Without it, Cargo.lock changes silently serve stale commands. |
| Impl-gate 3 (test-integrity warning in `feedback.sh`) | P7 (partial coverage of test-integrity rule) | Beck "agents try to delete tests" | Well-grounded | See §B7 for primitive choice. |
| Impl-gate 4 (race-safe IDs; timestamp or content-hash) | P1 (correctness of registry) | — | Well-grounded | Two concurrent `0001` writes is a real failure mode for any monorepo with parallel sessions. |
| Impl-gate 5 (changed-file-scoped commands; line-per-command cache) | P7 (the 3 s budget is meaningful only if commands are scoped) | "Fast loop" intent | Well-grounded | Without scoping, every edit returns `timeout`, training the agent to ignore feedback. This is the most important impl gate. |
| Non-negotiable 1 (lean relaxed over strict) | Design tenet 2 (graceful over punitive); P7 deferred-enforcement story | Google "improvement, not perfection" | Well-grounded | Plan reconciles tension with deterministic-over-vibes explicitly. |
| Non-negotiable 2 (passive, plays well with others) | Design tenet 4 (visible, not hidden) + cross-plugin coexistence (Plugins Field Guide §11 settings warning) | — (CC ecosystem hygiene) | Well-grounded | "No `agent` override" is the single most important coexistence move. |
| CC version anchor (v2.1.121+) | — (versioning hygiene) | — | Well-grounded but lightly grounded | The 121 number is presumably tied to features used: `additionalContext` envelope, `monitors/` (which we cut, so not v1-relevant), `disable-model-invocation`. The plan does not explain *why* 121. **Sub-recommendation:** in the README, name the two CC features the version anchor protects (`hookSpecificOutput.additionalContext`; `disable-model-invocation` on skills). Otherwise dogfood will silently drift to a lower minimum and the gate will be cargo-cult. |

**Pillars not commitment-mapped that are *not* in the residual-risk list:**

- **Design tenet 1 (continuous over heroic)** — implicitly satisfied (the plugin is always-on once enabled). No commitment, no risk entry. Acceptable; design tenets are style, not behavior. Not flagged.
- **Design tenet 6 (pay down with the same tool that accrues debt)** — Pillar 9 is in residual-risk #6, so this design tenet is correctly accounted for as deferred.

**No orphans found in either direction.** Every v1 commitment traces; every pillar requirement is either committed or named in residual-risk. Discipline 4 is a labeled non-pillar UX choice and is honestly flagged as such.

---

## B. Primitive fitness

### B1. Detect repo's quality commands and persist them

| Need | Currently chosen | Alternatives considered | Optimal? | Recommendation |
|---|---|---|---|---|
| Detect + persist commands | `SessionStart` hook + `session-start.sh` + `${CLAUDE_PLUGIN_DATA}` cache | `/debt:detect` slash command; MCP server; native CC project detection | **Optimal** | Keep. |

A slash command would force the user to type `/debt:detect` once (and on every Cargo.lock change). Pillar 7 demands the fast loop "every commit and every PR"; SessionStart is the only primitive in CC that fires automatically without user action and has access to `additionalContext` to inject the discovery prompt to Claude. CC has no native project-detection facility (per the Plugins Field Guide; nothing in `/docs/en/` exposes one either). An MCP server would be wrong here because (a) MCPs are for systems that aren't CLIs (Plugins Field Guide §6), and (b) command detection is a one-shot question to Claude, not an ongoing tool surface. Native LSP would not help because LSPs answer language-level questions, not project-shape questions. **Verdict:** SessionStart + script is the only correctly-shaped primitive.

### B2. Run quality commands after every agent edit

| Need | Currently chosen | Alternatives considered | Optimal? | Recommendation |
|---|---|---|---|---|
| Per-edit feedback | `PostToolUse` hook + `feedback.sh` | `monitors/`; `bin/` CLI; subagent verifier; MCP code-runner | **Optimal** | Keep. |

This is the textbook example in the Plugins Field Guide §5 (auto-format on `PostToolUse`). A `monitors/` background watcher would be wrong: monitors react to *external* state changes (log lines, deploy status — Field Guide §8); they do not gate the agent's edit cycle. An MCP "code-runner" server would be wrong: MCPs expose tools the model *chooses* to call; Pillar 7 demands deterministic invocation that the model cannot skip. The `agent` hook type (verifier subagent) is overkill and wastes a context window per edit; `command` is correct. **Verdict:** the only Pillar 7-shaped primitive in CC is `PostToolUse → command`.

### B3. Inject disciplines on every session

| Need | Currently chosen | Alternatives considered | Optimal? | Recommendation |
|---|---|---|---|---|
| Per-session disciplines | `SessionStart` → `additionalContext` JSON envelope | `CLAUDE.md`-only (no plugin); skill that Claude is told to load; `output-styles/` | **Optimal for v1's enable-and-go bet** | Keep. |

A CLAUDE.md-only approach (no plugin) would force the user to edit their repo on install — direct violation of "Enable-and-go" and footprint-creep anti-pattern #7. A skill that Claude is told to load assumes Claude knows to invoke it without the inject telling it to — circular. `output-styles/` was explicitly cut (Plugins Field Guide §10): it changes formatting tone, not standing instructions; and the plan's anti-pattern #5 explicitly forbids using output-styles for "convenience." The SessionStart-inject is the only primitive that delivers standing instructions without modifying user files. **Verdict:** keep, but be aware this is the load-bearing primitive — if the inject fails (no git, read-only data dir, malformed JSON), discipline coverage drops to zero. Impl-gate 1 covers the failure modes.

### B4. Provide the registry schema and act on it

| Need | Currently chosen | Alternatives considered | Optimal? | Recommendation |
|---|---|---|---|---|
| Registry schema + write | `/debt:add` skill (schema embedded in `SKILL.md`) | `agents/debt-scribe`; bash script via slash command; MCP "registry" server | **Optimal for v1**; `debt-scribe` is right for v2 | Keep. |

A subagent (`debt-scribe`) would be wrong for v1 because v1 has *only* the `/debt:add` flow; subagents earn their slot when drafting becomes multi-format (entries + ADRs + specs in v2). The plan correctly defers `debt-scribe` to v2. A bash script would be wrong because the registry entry's fields (especially `interest`, `business_capability`, `payoff_trigger`) require model judgment over current chat context — exactly what skills exist for. An MCP "registry" server would be wrong because the registry *is the filesystem*; an MCP wrapper adds a process, a protocol, and a startup tax for filesystem ops the model already does natively. **Verdict:** skill is correct; the timestamp-shaped ID per impl-gate 4 is critical and should not be optional.

### B5. Bootstrap shared team config

| Need | Currently chosen | Alternatives considered | Optimal? | Recommendation |
|---|---|---|---|---|
| Team-shared persistence | `/debt:init` skill (with `disable-model-invocation: true`) writing to CLAUDE.md | Marketplace-managed config; `userConfig`; bundled `bin/` CLI | **Optimal** | Keep. |

A marketplace-managed configuration would be wrong: marketplaces (Plugins Field Guide §16) catalog plugins, not project files; they cannot write to a user's repo. `userConfig` (Field Guide §13) prompts at *plugin enable time*, persists per-user in `~/.claude/`, and never touches the project repo — wrong for team-share, which by definition needs the config to live in version control. A bundled `bin/` CLI (`debt-ops init`) would force the user to remember a shell command instead of a slash command and would lose access to chat context. The `disable-model-invocation: true` guard is the correct way to prevent Claude from auto-invoking it (Plugins Field Guide §2; native skill frontmatter). **Verdict:** the only correctly-shaped primitive.

### B6. Architectural-significance heuristic for ADR drafting

| Need | Currently chosen | Alternatives considered | Optimal? | Recommendation |
|---|---|---|---|---|
| Detect arch-significant changes | Pure model judgment from inject text + "two credible alternatives" rule | `agents/adr-author` subagent; `PreToolUse` on git commits; LSP-driven heuristic | **Optimal for v1**; subagent is right for v2 | Keep for v1. Move to subagent in v2. |

The "two credible alternatives" rule is the cleanest possible v1 heuristic — it filters bikeshedding from architecture by demanding the agent name two real alternatives before invoking the format. A subagent (`adr-author`) is the correct primitive eventually because ADR drafting benefits from a fresh context window (Pillars 8 writer/reviewer separation), but in v1 there is no writer/reviewer separation anywhere; adding one only here would be inconsistent. A `PreToolUse` on git commits would fire too late (commit time, not decision time) and would block the developer's flow — a non-negotiable violation. LSP heuristics cannot detect "data model" or "public interface" semantically across languages. **Verdict for v1:** model judgment is the only primitive that scales across languages and decision types. **Recommendation for v2:** an `adr-author` subagent invoked when discipline 2 fires (already in the v2 roadmap as part of `debt-scribe`); the audit confirms this is the right primitive then.

### B7. Test-integrity warning signal in v1

| Need | Currently chosen | Alternatives considered | Optimal? | Recommendation |
|---|---|---|---|---|
| Test-count drop warning | Folded into `feedback.sh` (PostToolUse) | Subagent; separate `Write\|Edit` hook for test-count diff only; PreToolUse on test files | **Optimal** | Keep, with one refinement. |

Adding it to `feedback.sh` keeps v1 at two hooks. A separate hook would double the per-edit overhead and force two `additionalContext` packets back into the model — diminishing returns at v1 cost. A subagent would be a category error: subagents are for fresh-context analysis, not deterministic counting. PreToolUse on test files is wrong because it requires *predicting* whether a planned edit is a test-deletion before it lands; PostToolUse with diff is the only signal that catches actual deletions. **One refinement:** the impl-gate 3 description ("approximate test-file count") should be clarified — file count is fragile (a renamed file counts as a delete + an add). The plan's mention of "blocks" is the safer signal but harder to implement. For v1, a count of `test_` / `_test.` / `.test.` / `.spec.` filenames is good enough to catch the gross "agent deletes the tests file" pattern Beck described; refine to block-level in v3.

### B8. Cross-tool team config (Cursor / Aider / Codex)

| Need | Currently chosen | Alternatives considered | Optimal? | Recommendation |
|---|---|---|---|---|
| AGENTS.md interop | `@AGENTS.md` import inside CLAUDE.md (instruction in `/debt:init`) | Bundled AGENTS.md template; marketplace `init.json` pattern | **Optimal** | Keep. |

Shipping an AGENTS.md template would *create* the file in the user's repo on install, a footprint-creep regression. Marketplace `init.json` (the doc claims this exists, but it is *not* documented in the official Plugins Field Guide §16 nor on `code.claude.com/docs/en/plugin-marketplaces`; it appears to be a community pattern, not a CC primitive). The `@AGENTS.md` import is exactly the documented CC pattern: CLAUDE.md is auto-loaded; `@`-imports inside it pull in additional files. The team can choose whether they want AGENTS.md parity by writing it themselves; the plugin merely makes the import discoverable in the section it writes. **Verdict:** keep.

---

## C. The cuts: defended or risky?

| Cut | Verdict | Reasoning |
|---|---|---|
| `userConfig` empty | **Defended** | Charter (when present) is source of truth; cache covers other case. Pillar 6's freshness check is a *behavioral* requirement (size budget, staleness detection), not a *configurable threshold* in v1 — there is nothing to override in v1. v2's freshness checks may need a `charter_max_lines` user override; until then, `userConfig` is correctly empty. |
| `Stop` hook | **Risky → recoverable** | Anti-pattern #6 ("discipline drift") names the exact failure mode where Stop returns. The risk is real: if discipline 1 fires inconsistently in dogfood, the marker-sniff at session end is the obvious safety net. *But* shipping it in v1 would couple "lean relaxed" to two different mechanisms (inject + stop-time scan) and double the surface area. Acceptable v1 cut **iff** the dogfood metric "marker-without-registry rate" is wired up from week one. **Recommendation:** add this metric explicitly to the impl-gate-5 dogfood list. |
| `/debt:list` (skill) | **Defended** | "Claude can `ls debt/registry/`" is correct; v1 lists chronologically without effort. v2's reason for re-introducing it is *ranking*, not listing — earned slot. |
| Required `/debt:init` (now opt-in) | **Defended** | Hard-required would have killed enable-and-go; the `disable-model-invocation` guard prevents auto-invocation. Correct as cut. |
| `commands/` flat layout | **Defended; but worth interrogating** | The user asked: could `/debt:add` just be a `commands/` flat-file? Verdict: **no.** The registry schema is ~30 lines and the skill needs progressive disclosure (the schema is loaded once, the example is loaded only when needed). `commands/` is for "one-shot commands that don't need scripts or reference material" (Field Guide §3). `/debt:add` will grow supporting files in v2 (the example file users keep asking for); shipping as a skill avoids a v2 migration. |
| `themes/` | **Defended** | Out of scope. |
| `bin/` | **Defended** | No standalone CLI use yet. Field Guide §12 says `bin/` shines when scripts earn shell-level use; v1's two scripts are hook-only. |
| `.lsp.json` | **Defended** | Anthropic ships LSP plugins for major languages; competing would be cargo-cult. |
| `output-styles/` | **Defended** | Anti-pattern #5 forbids using output-styles for "convenience." Right cut. |
| `monitors/` | **Defended for v1; correct return point flagged** | v3's paydown engine could use one (Pillar 9 needs scheduling triggers — log-tail or threshold-cross); plan correctly flags v3+ return. |
| `channels` | **Defended** | No external messaging in v1. |
| `settings.json` `agent` override | **Defended** | This is the single most important *no* in the plan. Setting it would replace the user's main loop on plugin enable — the canonical "hostile to other plugins" posture. The plan's "passes well with others" non-negotiable hangs on this cut. |
| Subagents (`agents/`) | **Defended for v1; v2 plan is correct** | The user explicitly asked: should `adr-author` move into v1? **No.** v1 has no other subagent and no writer/reviewer separation; adding one subagent would be inconsistent. v2 introduces `debt-scribe`, `triage`, `reviewer` as a coherent set — that is when subagents earn their slot. The audit's §B6 confirms model judgment is the only v1-coherent primitive for the "two credible alternatives" rule. |
| `.mcp.json` | **Defended** | No code-health MCP needed in v1; v3 wires CodeScene. |
| Local hotspot scorer | **Defended** | Plan's reasoning is correct: "lines × git frequency" is a misleading complexity proxy. Honest "behavioral signal unavailable" beats a fake one. |
| Bash auto-detection table | **Defended** | Replaced by Claude's repo scan in inject; correct. |
| `templates/` | **Defended** | Disciplines live inline; ADR format is in inject text. Correct. |
| `examples/` | **Defended** | Schema example lives in `SKILL.md`. Correct. |
| Charter bootstrap | **Defended** | CC's built-in `/init` already scaffolds CLAUDE.md; overlap is the failure. |
| Pre-creating `debt/registry/` and `doc/adr/` on install | **Defended** | Lazy creation is the enable-and-go non-negotiable. |
| GitHub Actions example | **Defended** | Ships with v3's `/debt:paydown`; nothing for it to do in v1. |

**Net.** One risky cut (`Stop` hook), and the mitigation is a single line added to the dogfood metrics. No wrong cuts.

---

## D. Net recommendation

**(1) Is the v1 primitive selection optimal? Yes.** Eight functional needs map to four primitives (skills × 2, hooks × 2 with scripts × 2, manifest). For each need, the chosen primitive is the only or clearly best CC primitive. The cuts are defended, with one risky-but-recoverable exception (`Stop`).

**(2) Single most important primitive change.** *None to the primitive selection itself.* The single most important *non-primitive* change is to make impl-gate 5 (changed-file-scoped commands; line-per-command cache) **load-bearing for the SessionStart discovery prompt**, not just guidance to Claude. Without changed-file-scoped commands, every edit returns `timeout`, the agent learns to ignore the feedback, and Pillar 7 (the load-bearing pillar of v1) silently degrades. Specifically, the SessionStart inject must (a) tell Claude to *prefer* commands that accept file/package arguments, (b) tell Claude to *reject* commands whose typical wall-clock exceeds 3 s, and (c) ask Claude to record the wall-clock estimate alongside each command in the cache. This is a script-level change, not a primitive change — but it is the v1 difference between "Pillar 7 works" and "Pillar 7 looks like it works."

A secondary refinement: the README must name the two CC features that justify the v2.1.121+ version anchor (`hookSpecificOutput.additionalContext` and `disable-model-invocation` on skills). Otherwise the gate becomes a cargo-cult number.

**(3) Single most important non-change — primitive that looks suboptimal but is right.** The `SessionStart` hook used as a *triple-purpose* primitive (cache discovery + cache hit injection + disciplines inject). It looks like a violation of single-responsibility. It is the right call. Three things share one trigger ("session begins"), one delivery channel (`additionalContext`), and one timing window (before first user prompt). Splitting them across primitives would mean the disciplines inject competes for ordering with the cache inject (CC runs SessionStart hooks in parallel; ordering is not guaranteed — Plugins Field Guide §5). A second hook would offer no behavioral guarantee that the cache populates before the disciplines arrive. One `session-start.sh` that emits one consolidated `additionalContext` envelope is the only design that survives the parallel-hook semantics.

**Bottom line.** Two skills, two hooks, two scripts. The toolbox has fifteen primitives. v1 uses three. Each cut is defended; the three retained are the only ones that match the load-bearing pillars (1, 5, 6, 7, 8). Ship it.
