# Go/No-Go: pre-v1 audit synthesis

Date: 2026-05-05
Inputs: `audit/01-citation-verification.md`, `audit/02-plugin-fit.md`,
`audit/03-traceability.md`, `audit/04-redteam.md`.

## Verdict

**Don't implement v1 yet.** The research foundation is solid (every
load-bearing claim verifies), the architectural shape is sound (CC
primitives are used correctly after Pass 2 fixes), and the pillars trace
cleanly to research. The cracks are all in the seam between pillars and
v1 commitments: a few load-bearing claims about what v1 *delivers* don't
match what v1 actually does, and the implementation has four small
robustness blockers that will bite in week one.

The fix is small: ~80 lines of doc edits + ~50 lines of script
robustness when implementation begins. With those landed, v1 is shippable
to Persona 2 (solo brownfield) — the bullseye — without a credibility
risk.

---

## Required pre-v1 doc edits

These are the items that have to settle before v1 implementation starts.
None require scope changes; all are language/framing fixes.

### A. Reconcile claim-vs-actual on the v1 inject

**Problem (Pass 1b crack #1).** The plan says "v1's contribution is
ensuring the disciplines exist in Claude's context; spec, test, review,
and comprehend disciplines arrive in v2/v3." But the four injected
disciplines (register debt, draft ADR, read registry, refer by content)
cover only Pillars 1 and 5. Pillar 8 disciplines — the ones that close
the METR 19% slowdown — are nowhere in v1.

**Fix (one of two).**
- **Option A (preferred):** Add 1–2 inject items aimed at Pillar 8.
  Concretely: "If your task is non-trivial, write a brief spec (2–3
  sentences: input, output, edge cases) before editing" and
  "Registering debt is not a substitute for fixing it; if a shortcut
  would fail an obvious test, write the test first." Both are cheap,
  text-only, and turn v1 from a Pillar-1/5 plugin into a Pillar-1/5/(half-)8
  plugin.
- **Option B:** Strike the "v1 puts the disciplines in context" claim
  and explicitly say "v1 covers the visibility and ADR disciplines; spec,
  TDD, review, and comprehensibility arrive in v2/v3." Honest deferral.

Option A captures the highest-leverage piece of evidence in the entire
synthesis (METR) for ~40 words of inject text. Recommend it.

### B. Add a "What v1 accepts as residual risk" subsection to plan.md

**Problem (Pass 1b cracks #3, anti-pattern coverage).** Of 10 anti-patterns
the pillars doc names, four are unprevented in v1 *and* unnamed as accepted
scope cuts: static-only dashboard, vanity refactors, unprotected
allocation, vibe-coding without TDD/spec/comprehensibility. The plan's
"What we skip in v1" table covers *primitives*, not *anti-patterns*. The
honest companion is a parallel subsection.

**Fix.** Add a subsection (~12 lines) listing each pillar's failure mode
that v1 leaves running, with one sentence on how dogfood will detect it
or when v2/v3 closes it. This single edit eliminates most of Pass 1b's
"deferred-without-naming-the-failure-mode" findings.

### C. Reconcile the tenet-vs-staging tension

**Problem (Pass 1b crack #5).** Two design tenets — "evidence-based over
opinion" and "deterministic over vibes" — are in honest tension with
v1's relaxed/static staging. The plan resolves the tension by deferring
to v3 but never *defends* the staging in tenet language. A reviewer
reads "deterministic over vibes" and "v1 has zero blocking rules"
side-by-side and sees apparent contradiction.

**Fix.** One short paragraph in plan.md's "The two non-negotiables"
section, in tenet language: "v1 honors *deterministic over vibes* by
making the feedback signal exist; v3 promotes the signal to a gate. v1
honors *evidence-based over opinion* by deferring to the project's
existing quality commands until the behavioral and DORA layers ship in
v3 — the v1 dependency is the project's lint/type/test, not the
developer's gut." Closes the crack.

### D. Hedge inheritance from research → pillars

**Problem (Pass 1b §5).** Three load-bearing numbers — METR (single RCT),
GitClear (observational), CodeScene 9.4 / 2–5× MCP (vendor whitepaper) —
have explicit caveats in `tech-debt-management.md` that don't propagate
to pillar foundations or failure modes. Pillar 2, Pillar 7, and Pillar 8
read as if these were peer-reviewed and causal.

**Fix.** Add a one-clause inline hedge at each invocation in
`tech-debt-pillars.md`:
- Pillar 7 foundation: change "Benchmarks on a 25,000-file dataset
  showed 2–5× more code-health improvements vs. raw Claude Code" →
  "...showed 2–5× more code-health improvements vs. raw Claude Code
  (vendor benchmark, not peer-reviewed)."
- Pillar 7 foundation: drop the IBM CAST "2–5×" line, or note that it
  is *the same vendor pattern, not an independent corroboration* (Pass
  1b §1 verdict).
- Pillar 8 failure mode: change "the METR study's 19% slowdown..." →
  "the METR study's 19% slowdown (one RCT, n=16, early-2025 tools)..."
- Pillar 2 / Pillar 7 failure modes: change "GitClear's 4× clone rate,
  doubled 14-day churn" → "GitClear's observed correlations (4× clones,
  ~doubled 14-day churn; observational, not causal)..."
- Pillar 9 foundation: change "McKinsey 2025... 40–50% faster and cheaper"
  → "McKinsey 2025... 40–50% faster and cheaper (a strategic projection,
  not a settled outcome)."

### E. Smaller doc fixes

- **Pillar 5 ↔ registry link.** Discipline 2 currently tells Claude to
  draft an ADR for architecturally significant changes but doesn't say
  "if the ADR introduces deliberate debt, also call `/debt-ops:add`."
  One-line addition in the SessionStart inject text closes Pillar 5's
  "bidirectional link" required-functionality bullet for v1, no v2 wait
  needed.
- **Discipline 4 disclosure.** Note that "refer by content, not ID" is
  a UX choice not derived from any pillar (Pass 1b §B finding). Defensible
  as-is, but flag in the plan to pre-empt a hostile-reviewer question.
- **Tighten Discipline 1 wording (Pass 3 §3).** Drop "use judgment;
  trivial markers (style nits) don't earn an entry" — that is the
  loophole that re-introduces Pillar 1's failure mode. Replace with: "If
  you write a marker, register it. The developer can drop entries in one
  message; you cannot recover an unregistered shortcut."
- **Tighten Discipline 2 wording (Pass 3 §3).** Add: "Draft an ADR only
  when there were two credible alternatives. If you can't list two, it's
  a comment, not an ADR."

---

## Implementation-time gates (when v1 is actually built)

These are the script-level robustness fixes from Pass 3 §1, §2, §5. They
don't require doc changes now, but they *must* be on the v1 implementation
checklist or v1 will break in week one.

| # | Gate | Lines | Why it can't ship without |
|---|---|---|---|
| 1 | `set -euo pipefail` in both scripts; non-git repo path emits `additionalContext` "debt-ops idle this session" and exits clean (not silent corruption); `gtimeout` fallback for BSD/macOS; readonly `${CLAUDE_PLUGIN_DATA}` falls back to stateless mode; Windows requirement noted in README | ~30 | macOS users without Homebrew coreutils crash on first edit. Non-git repos collapse all caches to one. Container/sandbox users can't write the cache. |
| 2 | Cache invalidation on manifest mtime: SessionStart hashes `Cargo.toml` / `package.json` / `pyproject.toml` / `Makefile` / `go.mod` / `Gemfile` and stores the hash beside `feedback.list`; mismatch triggers re-discovery | ~5 | Without it, the cache silently serves stale commands for days when lockfiles change. |
| 3 | Test-integrity warning: SessionStart caches a test-file count; `feedback.sh` recomputes and emits a non-blocking `WARNING: this edit removed N tests/blocks` line in `additionalContext` | ~10 | Beck's "agents will try to delete tests to make them pass" is the single biggest evidence-base risk; deferring full test-integrity to v3 is fine, but the v1→v3 window leaves the team unprotected unless this 10-line warning ships. |
| 4 | Race-safe `/debt:add` IDs: switch from `0001` glob-and-increment to timestamp- or hash-based (`YYYYMMDDhhmmss-<slug>` or short content hash) | ~3 | Two concurrent sessions both pick id 0001 and write conflicting files. The plan's "id is like a commit SHA" framing already supports this. |
| 5 | Discovery prompt asks for **changed-file-scoped** lint/typecheck commands, not project-wide; cache format defined as one-command-per-line, comments allowed, malformed lines silently skipped | ~5 | Project-wide `npm run lint` exceeds 3 s on any non-trivial repo; the agent sees lint failing always and either ignores it or chases ghost errors. Cache format prevents corruption-on-truncation. |

**Total implementation cost above the plan baseline: ~50 lines of bash.**

---

## Accepted residual risk list (to copy into plan.md as the new subsection)

For each, dogfood will detect it; v2/v3 closes it. v1 ships knowing this.

1. **Behavioral measurement absent (Pillar 2 failure mode).** AI-induced
   hotspot regressions accumulate undetected until v3 wires the
   CodeScene MCP. Mitigation: project's existing static layer catches the
   gross issues. Detection: `git log` size of `debt/registry/` and the
   ratio of `ai_authored: true` entries — if rising, v3 needed sooner.
2. **No hotspot prioritization (Pillar 3 failure mode).** Cleanup may go
   to easy targets, not high-pay-off targets. Mitigation: v1 expects the
   developer to choose targets; v2's `/debt:list` ranking arrives.
   Detection: ratio of registry entries closed in active modules vs.
   stable modules.
3. **No allocation defense (Pillar 4 failure mode).** Feature pressure
   may eat any informal paydown commitment. v1 ships nothing aimed at
   this. Mitigation: `Debt-Pays-Down: <id>` PR trailers can accumulate
   from day one as raw material for v4's `/debt:budget`. Detection: the
   commit log itself.
4. **No test-integrity / Code Health gates (Pillar 7 failure modes).**
   v1 ships the warning signal in implementation gate #3 but not the
   hard rejection. Mitigation: human at PR time. Detection: per-edit
   test-count delta in `feedback.sh` output.
5. **No spec / fresh-context review / comprehensibility (Pillar 8
   failure mode).** Cognitive debt accrues. v1 inject (after fix A
   above) covers the spec and TDD-shaped lines but not the writer/reviewer
   separation. Mitigation: human review at PR. Detection: % of agent-
   authored diffs the developer rewrites materially.
6. **No agentic paydown (Pillar 9 failure mode).** Asymmetry persists —
   agents accelerate creation, no one redirects to paydown. Pillar 9
   depends on 3, 7, 8 being live; v1 cannot ship it.

---

## v2 / v3 backlog adds (from this audit)

- **v2:** architectural-significance heuristic detection (Pillar 5
  required-functionality (b); deferral acknowledged but the "no heuristic"
  point from Pass 3 §1.5 makes the v2 timing more pressing).
- **v2:** dedup logic for `/debt:add` (Pass 3 §3 attack vector — agent
  registers throwaway entries under different slugs).
- **v2:** Discipline 3 must scale beyond ~50 registry entries (Pass 3 §2
  edge case #4 — directory walk on every relevant edit).
- **v3:** verify `additionalContext` from `PostToolUse` is acted on by
  the agent in the *same turn* the edit completed (Pass 3 §1 failure
  mode #3). Currently an unverified plan assumption; if false, v1's
  Pillar-7 feedback loop is one user-prompt slower than the plan claims.
  Plumb a metric in v1 dogfood; if action rate < 50%, escalate.
- **v3:** ADR-as-rationalization detection (Pass 3 §3 — one form of the
  test-integrity / Code Health-regression class).

---

## Minimum viable fix list (mechanical)

If you say "go," I would:

1. **`tech-debt-pillars.md`** — apply hedges from §D (3 inline edits),
   reconcile Pillar 7's 2–5× double-count (§D bullet 2). ~10 lines
   touched.
2. **`tech-debt-plugin-plan.md`** — apply §A (the inject claim
   reconciliation, preferred Option A), §B (the "What v1 accepts as
   residual risk" subsection, ~12 lines), §C (the tenet-vs-staging
   paragraph), and §E (Pillar 5 inject line, Discipline 1 / 2 wording,
   Discipline 4 disclosure). ~50–60 lines touched.
3. **No code yet** — implementation gates 1–5 are notes for the v1
   implementation checklist. They live in the plan as a "v1
   implementation requirements" appendix, ~20 lines.

Total ~80 lines across two files. After this, the chain holds end-to-end
and v1 is implementation-ready for Persona 2.

---

## What this audit does *not* settle

- Whether `additionalContext` from `PostToolUse` is actually acted on
  in-turn by the agent (Pass 3 §1 #3). v1 dogfood metric.
- Whether discipline drift exceeds tolerable rate under long sessions
  (Pass 3 §1 #2). v1 dogfood metric.
- Whether v1's differentiation vs. a homemade SessionStart hook is
  worth the install for Persona 2 specifically (Pass 3 §4). The honest
  answer is "yes if you intend to keep a registry; no if you'll wing it
  on TODOs." v1 release messaging should say so.

These three are unknowns the audit cannot resolve without running v1.
The point of v1 is to find out.
