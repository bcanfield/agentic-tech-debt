# Traceability audit (Pass 1b)
Date: 2026-05-05

Scope: internal coherence of `tech-debt-management.md` (research) → `tech-debt-pillars.md` (principles) → `tech-debt-plugin-plan.md` (v1 spec). No web work; structural read only. Citation correctness covered in `audit/01-citation-verification.md`; primitive-fit in `audit/02-plugin-fit.md`. This pass tests whether each upstream claim survives downstream and whether each downstream commitment can defend its pedigree.

---

## A. Pillar to v1 traceability

| # | Pillar | Research grounding (in `tech-debt-management.md`) | v1 commitment (in `tech-debt-plugin-plan.md`) | Verdict |
|---|---|---|---|---|
| 1 | Visibility | Findings 1–2; Layer 1; Kruchten/Nord/Ozkaya; Dagstuhl 16162 | `/debt:add`; SessionStart discipline 1; lazy `debt/registry/`; five-field schema | well-grounded |
| 2 | Continuous Measurement | Findings 7–8; §3 Measurement (4 layers); KPI 30/60/90-day + 14-day churn | "static layer via Pillar 7's quality checks"; behavioral, AI-touched, DORA, perception deferred to v3 | partial — gap named ("behavioral signal unavailable rather than fake it") |
| 3 | Hotspot Prioritization | Finding 4 (Pareto); §4 Prioritization | em-dash; deferred to v2 | partial — fully deferred, said plainly |
| 4 | Continuous Paydown | Finding 5 (15–25%); Layer 3; bug cap; Boy Scout | em-dash; "v1 *enables* future accounting"; deferred to v4 | partial — registry-as-foundation thin, deferral explicit |
| 5 | Deliberate Architecture | Finding 6 (ADRs/Nygard); SEI architectural primacy | SessionStart discipline 2; lazy `doc/adr/`; architectural-touch heuristic deferred to v2 | partial — heuristic deferred; deferral acknowledged |
| 6 | Curated Agent Context | Finding 10; Layer 4 §3 ("~150–200 instructions") | Native `CLAUDE.md` loading; opt-in `/debt:init`; SessionStart inject as fallback | partial — §Pillar 6 "Honest caveat" admits no size budget or freshness check |
| 7 | In-Loop Deterministic Feedback | Finding 10 (CodeHealth MCP); Layer 4 §3; Beck/Anthropic; DORA 2024 | `SessionStart` caches quality commands; `PostToolUse → feedback.sh` parallel under `timeout 3`; deferred: test-integrity rule, AI-touched hotspot floor, `/debt:override`, code-health MCP | weak link — pillar names two **non-bypassable** rules; v1 has zero blocking rules. See E.1. |
| 8 | Spec → Test → Review → Comprehend | Finding 9 (Willison, Beck, Karpathy); Layer 4 §3; cognitive debt | em-dash; "No commitment. v1's contribution is ensuring the disciplines exist in Claude's context" | weak link — that claim is **factually wrong**: injected disciplines cover Pillars 1, 5, 6, not 8. See E.3. |
| 9 | AI as Paydown Engine | Finding 8/10 + Layer 4 §3; AWS Transform; Spotify background agent (1,500+ PRs); McKinsey 2025 | em-dash; deferred to v3 with stated dependency chain (needs 3, full 7, 8) | partial — fully deferred and honest about it |

Net: only Pillar 1 is well-grounded. Five are partial-with-honest-deferral (2, 3, 4, 6, 9). Two are weak links (7, 8) — see E.1 and E.3. No outright orphans (every pillar has a v1 cell or a deferred-with-reason cell).

---

## B. v1 to Pillar (orphan check)

Walking every v1 surface in `tech-debt-plugin-plan.md` and confirming each lands on at least one pillar.

**Skills.**

1. `/debt:add` → Pillar 1 (registry entry creation). Grounded.
2. `/debt:init` (`disable-model-invocation: true`) → Pillar 6 (writes `## Tech debt operations` into `CLAUDE.md`). Grounded.

**Hooks.**

3. `SessionStart` (`session-start.sh`). Multi-pillar:
   - discipline 1 (TODO/FIXME/HACK/XXX → register) → Pillar 1
   - discipline 2 (architecturally significant change → Nygard ADR) → Pillar 5
   - discipline 3 (read `debt/registry/` before changing files) → Pillars 1, 6
   - discipline 4 (refer by content, not ID) → **orphan** — no pillar required this; UX convention only. Plan justifies it in passing ("IDs are for tooling cross-references like commit SHAs"). Harmless.
   - detects + caches quality commands → Pillar 7
   - per-repo cache under `${CLAUDE_PLUGIN_DATA}/cache/<repo-hash>/` → Pillar 7 infrastructure
4. `PostToolUse → feedback.sh` → Pillar 7. Grounded.

**Schema fields.**

5. Five-field YAML (principal, interest, hotspot, business_capability, payoff_trigger) → Pillar 1, mirrors Kruchten/Nord/Ozkaya.
6. `quadrant` enum (Fowler) → Pillar 1.
7. `category` enum (Google/Jaspan-Green ten) → Pillar 1.
8. `ai_authored: true|false` → Pillar 2's "discriminator for AI-touched code." **Schema-orphan in v1**: field exists, but Pillar 2's discriminator + 30/60/90-day windows are deferred to v3. Plan ships the *field* without the *machinery* — inconsistent with the "if v1 doesn't do it, v1 doesn't ship the surface" cut applied elsewhere (e.g., `userConfig` removed because empty ≡ absent). See E.6.
9. `payoff_trigger: unknown` → Pillars 1, 5. Grounded.

**Plumbing decisions.** All grounded — `disable-model-invocation: true` on `/debt:init` and `/debt-ops:*` namespacing trace to design tenets ("Graceful over punitive," "Passive, plays well with others"); 3s budget in `feedback.sh`, the `<!-- debt-ops:feedback v1 -->` marker, the `Write|Edit|MultiEdit` matcher, and `${CLAUDE_PLUGIN_DATA}/cache/<repo-hash>/` per-repo isolation all serve Pillar 7's "fast, deterministic, post-edit" intent.

**Orphans summary.**

- **Discipline 4** (refer-by-content, not ID). UX convention; no pillar required it; harmless.
- **`ai_authored` schema field.** Pedigree is Pillar 2, but Pillar 2's v1 cell defers the discriminator. Schema over-shipped relative to v1 functionality (see E.6).

**Commitments whose justification rests on a failure mode the pillars didn't name.** None found. Every primitive maps to a pillar-listed failure mode. No scope creep.

**Backward verdict.** Two minor orphans. v1 surface is, if anything, *narrower* than the pillars warrant — this is the explicit "lean relaxed over strict" stance. The asymmetry is the right direction (under-promise > over-promise); the orphans deserve a one-line note flagging them as forward-compatibility hooks, not v1 functionality.

---

## C. Caveat propagation

| Caveat | Load-bearing downstream? | Uncertainty visible? | Verdict |
|---|---|---|---|
| Big-dollar figures ($1.52T, 20–40%, 42%) are top-down estimates | Lightly. Pillars and plan do not quantify cost. | N/A | clean |
| Tool disagreement (Lefever 2021): static tools agree poorly | **Yes** — Pillar 2 explicitly cites Lefever as the justification for requiring 4 layers. Plan v1 ships only the static layer. | Plan never names Lefever; commitment-table cell reads as a positive ("static layer via Pillar 7's quality checks"). | flag — see E.4 |
| METR single RCT (n≈16, early 2025) | Lightly — Pillar 8 failure-mode prose ("the perception-reality gap *this pillar closes*"). Plan does not cite METR. | Pillar 8 treats a single small RCT as a settled finding; research caveat (METR couldn't reproduce in 2026) not carried forward. | partial — pillar overconfident; plan clean |
| GitClear is observational | **Yes** — Pillar 2 failure mode ("4× clones, doubled 14-day churn"); Pillar 9 counterweight. | Both pillars cite causally; observational caveat not carried. | flag — correlational read as causal in pillars; plan inherits indirectly |
| Vibe-coding debt projections (vendor-blog) | Not load-bearing anywhere. | N/A | clean |
| MCP / agent-driven refactoring tooling is brand new | **Yes** — Pillar 7 cites CodeScene CodeHealth MCP "2–5× improvements"; Pillar 9 cites Spotify 1,500+ PRs, AWS Transform 80%. v1 defers MCP wiring entirely to v3. | Pillars drop the "vendor whitepaper, not peer-reviewed" qualifier the research carries. Plan side-steps via deferral. | partial — pillars overclaim; v1 plan clean by deferral |
| Cultural / incentive issues dominate | **Yes** — Pillar 4 cites this as the failure mode the system must defend against. v1 defers Pillar 4 entirely. | Plan acknowledges Pillar 4 deferral but does not acknowledge that v1 is therefore exposed to the dominant failure mode the research names. | flag — see E.5 |
| Trade-off curve may be shifting | Lightly — Pillar 9 strategic implication. | Pillar softens "strategic bet, not settled" to "strategic implication." | clean enough |

---

## D. Anti-pattern coverage

| # | Anti-pattern | v1 mechanism / accepted gap | Verdict |
|---|---|---|---|
| 1 | Separate, ignored tech-debt backlog | `/debt:add` writes to `debt/registry/` in-repo; discipline 3 reads it before changes | prevented |
| 2 | Static-analysis-only dashboard | v1 Pillar 2 cell *is* "static layer via Pillar 7's quality checks" — exactly the configuration the pillar names as this anti-pattern | **gap, unflagged** — see E.4 |
| 3 | Vanity refactors of healthy code | Pillar 3 deferred to v2 entirely | accepted gap (deferral explicit) |
| 4 | Paydown allocation no one protects | Pillar 4 deferred to v4 entirely; registry enables future accounting only | accepted gap, but tension with caveat C — see E.5 |
| 5 | Tribal architecture | SessionStart discipline 2 nudges Nygard ADRs; lazy `doc/adr/` | prevented weakly (no architectural-touch heuristic; relies on agent judgment — see E.2) |
| 6 | Ever-growing CLAUDE.md / AGENTS.md | "Honest caveat" admits no size budget or freshness check in v1 | accepted gap (flagged) |
| 7 | Agent output reviewed only at PR time | `PostToolUse → feedback.sh` runs commands after every Write/Edit/MultiEdit | prevented |
| 8 | Vibe coding in production (no spec, no TDD, no comprehensibility check) | Pillar 8 deferred entirely; plan claims v1 contributes "by ensuring the disciplines exist in Claude's context" — but the inject contains no Pillar 8 disciplines | **gap, mis-flagged** — see E.3 |
| 9 | Using agents only to accrue debt | Pillar 9 deferred to v3 entirely | accepted gap (deferral explicit) |
| 10 | Punitive, blocking, opinion-based gates | "Lean relaxed over strict. v1 has zero blocking rules… nothing is rejected." | prevented (most strongly prevented in v1) |

Net: 4 prevented (1, 5, 7, 10), 4 accepted-and-flagged (3, 4, 6, 9), 2 unflagged-or-mis-flagged (2, 8).

---

## E. Internal contradictions

### E.1. Pillar 7 says non-bypassable; plan v1 says zero blocking rules

Pillar 7 names two **non-bypassable** rules: *"diffs that delete or weaken tests in order to make them pass are rejected"* and *"diffs that worsen Code Health on touched hotspots are rejected unless paired with a debt registry entry and ADR (Pillars 1 and 5)."* Plan §"The two non-negotiables" #1: *"Lean relaxed over strict. v1 has zero blocking rules. … nothing is rejected. Strict gates arrive in v3."*

These are direct opposites. The deferral is named ("strict gates arrive in v3"), but the commitment table lists Pillar 7 with a populated v1 cell *without* flagging that "non-bypassable" is the literal opposite of "zero blocking rules." The honest-caveat treatment used in §Pillar 6 is not applied here in the same shape; the deferral is buried in the v3 bullet list. **Severity:** medium. Recommend one line in §Pillar 7: "Pillar 7 calls these rules non-bypassable; v1 implements only the surfacing half, deferring the rejection half to v3 per the 'lean relaxed' non-negotiable. Anti-pattern 10 is the binding constraint."

### E.2. Pillar 5 requires architectural-touch detection; v1 ships nudge only

Pillar 5 required functionality, third bullet: *"A way to detect when a change is 'architecturally significant', even a rough heuristic (touching a public interface, a data model, a build pipeline, an auth surface), and prompt for an ADR."* Plan §Pillar 5 relies entirely on Claude's adherence to discipline 2; the heuristic is in the v2-deferred list. The agent decides whether the change is architecturally significant — i.e. one agent's judgment in place of the searchable, non-tribal record the research (Finding 6) says ADRs exist to produce. **Severity:** low. Deferral disclosed; framing implies more coverage than v1 actually provides.

### E.3. Pillar 8 declared "covered by context inject" but inject does not include Pillar 8 disciplines

Plan §"Pillars 3, 4, 8, 9", Pillar 8 line: *"No commitment. v1's contribution is ensuring the disciplines exist in Claude's context; spec, test, review, and comprehend disciplines arrive in v2/v3."* The four disciplines actually injected by `session-start.sh`:

1. TODO/FIXME/HACK/XXX → register debt (Pillar 1)
2. Architecturally significant change → Nygard ADR (Pillar 5)
3. Read `debt/registry/` before changes (Pillars 1, 6)
4. Refer by content, not ID (orphan)

None covers spec, TDD, writer/reviewer separation, or comprehensibility. The plan's claim is **factually wrong as written**; Pillar 8's disciplines are not in the v1 inject. **Severity:** high — strongest contradiction in the chain. Anti-pattern 8 is the one v1 is *most* exposed to given the Pillar 8 deferral, and the plan's prose implies partial coverage that does not exist. Recommend either (a) correct the prose ("Pillar 8 disciplines are not injected in v1; anti-pattern 8 is not prevented"), or (b) inject a fifth discipline encoding Willison's comprehensibility rule (two sentences, zero implementation cost, partially closes the gap and makes the prose true).

### E.4. Pillar 2 ships the configuration anti-pattern 2 forbids, without naming the connection

Pillar 2 cites Lefever 2021 ("static tools disagree heavily. No single tool is sufficient"). Anti-pattern 2: *"A static-analysis-only dashboard. Pillar 2 forbids it; behavioral and perception layers are required."* Plan v1 ships only the static layer. Plan §Pillar 2 admits behavioral signal is unavailable, but never connects this to anti-pattern 2. A reader of the commitment table sees Pillar 2 with a non-empty v1 cell and plausibly concludes Pillar 2 is "covered"; the principles file says that exact configuration is the forbidden anti-pattern. **Severity:** medium. Prose hedges; commitment-table cell oversells.

### E.5. Pillar 4 deferral collides with the dominant cultural caveat

Pillar 4 names the failure mode: "the persistent failure is leadership pressure that lets feature work eat the allocation." Research §Caveats names this as the *dominant* failure mode: "Without executive-level commitment to protect debt time, no framework holds." v1 defers Pillar 4 entirely and ships no measurement or reporting surface that would defend the allocation. Plan does not flag the tension. **Severity:** low–medium. v1 is small by design, but a one-line acknowledgement in §"Closing" or §"Who v1 is for" — "v1 does not address the leadership-pressure failure mode the research names as dominant; that arrives in v4" — would close the gap.

### E.6. `ai_authored` schema field shipped without v1 round-trip

§"The registry schema" includes `ai_authored: true|false`; commitment table defers Pillar 2's AI-touched discriminator entirely to v3. No v1 mechanism populates, reads, or consumes the field. This is the only schema field with no v1 round-trip, and the plan's general philosophy elsewhere ("if v1 doesn't do it, v1 doesn't ship the surface for it" — e.g., `userConfig` removed because both empty and absent are equivalent) is not applied here. **Severity:** low. Forward-compatibility is normal, but a one-line note in the schema section ("`ai_authored` is forward-compatibility for v3's AI-touched discriminator; v1 does not populate or consume it") would close the inconsistency.

### E.7. "Lean relaxed over strict" is stricter than the design tenets require

Design tenet 2: "Graceful over punitive. The system surfaces, suggests, and **gates only where evidence justifies blocking**." Pillars do *not* say "never gate"; they say "gate only where evidence justifies," and Pillar 7 names the evidence (test deletion, hotspot Code Health regression). Plan reframes as "v1 has zero blocking rules" — a stronger commitment than the principles assert, used to justify deferring blocking the principles say is justified. **Severity:** low. Phasing can be defended; "blocking deferred until dogfood evidence justifies it" would match pillar language better than "zero blocking rules."

---

## Story cracks

If the audit's findings hold, three v1 edits are needed before implementation locks in. None require architectural rework; all are prose / scope statements.

1. **Pillar 8 prose is false** (highest severity). §"Pillars 3, 4, 8, 9: deferred entirely from v1" claims v1 contributes to Pillar 8 "by ensuring the disciplines exist in Claude's context." The four injected disciplines don't include spec, TDD, reviewer, or comprehensibility. Either correct the prose or inject a fifth discipline encoding Willison's comprehensibility rule (zero implementation cost, partially closes anti-pattern 8).

2. **Pillar 7 contradiction needs reconciliation.** "Non-bypassable" (pillar) vs "zero blocking rules" (plan) is the loudest literal contradiction. A single line in §Pillar 7 acknowledging that v1 implements the surfacing half and defers the rejection half — anchored to anti-pattern 10 as the binding constraint — resolves it.

3. **Pillar 2 / anti-pattern 2 collision.** v1's "static layer only" is exactly the configuration the pillars name as anti-pattern 2. One line in §Pillar 2 ("v1 deliberately ships only the static layer the pillars name as insufficient on its own; behavioral, perception, and outcome layers arrive in v3") closes the gap.

Two smaller items (`ai_authored` schema field shipping without consumer; cultural caveat unaddressed by deferred Pillar 4) are worth a sentence but not blocking.

The chain holds. Deferrals are mostly honest; the v1 surface is narrow-by-design and the narrowness is principled. The cracks concentrate at Pillars 7 and 8 — the two pillars closest to the agent-loop discipline the research says matters most — and they are mostly *prose* cracks, not architecture cracks. Fixable in a small edit pass.
