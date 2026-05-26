# 0007 — Periodic registry review skill (audit + triage in one pass)

**Date:** 2026-05-26
**Status:** Accepted

## Context

The capture loop works: across three dogfood repos the registries are filling (slack-agent 83 entries, diab 14, cage/ui 9). The loop that *closes* entries doesn't exist yet. Two failure modes have already surfaced:

- **Stale entries from reverted code.** When the dev backs out a change, the registry entry hangs on. The deferral the entry describes is no longer in the code, but nothing tells the registry that.
- **No prioritization.** With 83 entries, "what should I work on next?" has no answer the plugin can defend with data.

The v1 plan flagged exactly this gap. Pillar 1 stale-aging and Pillar 3 hotspot ranking were both deferred to v2 (`docs/tech-debt-plugin-plan.md:222, 298`), and the day-in-the-life note predicted it: "v2's `/debt:list` and `triage` reduce [review cost] by surfacing duplicates and stale entries" (`docs/tech-debt-plugin-plan.md:595`). The research base is unambiguous on the shape: one ranked backlog, not two (`docs/tech-debt-management.md:78`); ~20% of files generate ~80% of debt-related rework, so prioritization is mandatory (`docs/tech-debt-pillars.md:199-202`); Google's standard is "improvement, not perfection" (`docs/tech-debt-management.md:155`).

## Decision

Add one user-invoked skill — `/debt-ops:review` — that does audit and triage in a single pass and produces a short actionable list, not a dashboard.

- **Audit phase, deterministic, Git-as-oracle.** For each entry: (a) does the `hotspot:` path still exist? (b) does the marker the entry was created for (TODO/FIXME/the loosened type/the swallowed error referenced in the body) still appear in that file? (c) has the file been substantially rewritten since the entry's `created:` date? Any of (a)–(c) failing marks the entry as **likely-stale**. The signal is a suggestion to drop, not an auto-delete — same posture as `/debt-ops:add`: over-flag, let the human confirm.
- **Triage phase, evidence-based ranking.** Surviving entries are ranked by a small explicit formula: `git log --follow` change-count on the hotspot file (the churn half of the Pareto signal, `docs/tech-debt-pillars.md:209-212`), crossed with the Fowler quadrant (reckless-inadvertent first, `docs/tech-debt-pillars.md:202-204`), with `ai_authored: true` and entry age as tiebreakers (rising AI-authored share is the v1 leading-indicator wired in `docs/tech-debt-plugin-plan.md:815`).
- **Output: three buckets, one screen.** "Likely stale (N) — `drop A,B,…` to remove"; "Top 3 to pay down next — with hotspot and quadrant shown"; "Everything else kept (N)". Letters reuse the existing `drop A` UX (ADR 0004) so the audit's stale-flags are droppable with the same shorthand.
- **Paydown happens through normal work, not a `resolve` verb.** When the dev fixes one of the top 3, normal editing removes the marker; the next `/debt-ops:review` re-audits and the entry shows up under "likely stale" → drop. The PR trailer `Debt-Pays-Down: <id>` (`docs/tech-debt-plugin-plan.md:257`) is the audit trail. No special closing flow.

The skill is user-invoked, not on a hook — paydown is a rhythm the developer owns. The Stop-hook nudge ADR 0005 already handles the "registry growing fast" tripwire; adding a second nudge for "review is overdue" stays out of v1 to avoid the punitive posture (`docs/tech-debt-pillars.md:36-39`).

## What this means for you

- When the registry feels heavy (start of week, before a fix-it block, mid-sprint planning), run `/debt-ops:review`. You get one screen back: a small stale list, your top 3, a count of the rest.
- Reverted code stops haunting you. If the TODO that spawned the entry no longer exists in the file, the review flags it; one `drop A,B,C` and it's gone.
- "What should I work on next?" has a defensible answer that points at the code that's actually changing — not the entry at the top of the list because it was registered first.
- Paydown doesn't introduce new ceremony. You fix the thing, the marker disappears, next review the entry shows as stale and you drop it. No "close this debt item" button.
- It's invoked by you, not by a hook. The plugin still stays passive in the edit loop; the review is a rhythm, not an ambush.

## Alternatives we ruled out

- **Auto-close hook on every edit.** A PostToolUse hook that deletes registry entries when their marker disappears from the touched file. Too aggressive for v1's "lean relaxed over strict" non-negotiable (`docs/tech-debt-plugin-plan.md:30`) — false deletes are unrecoverable (the entry is gone), false flags are cheap (one `drop` away). Reconsider in v3 once the gate posture changes.
- **Separate `/debt-ops:audit` and `/debt-ops:list` skills.** Two commands re-creates the "tech-debt backlog" anti-pattern the research is unanimous against (`docs/tech-debt-management.md:78`, `docs/tech-debt-pillars.md:654`). Audit and triage are the same act — "what's still real" and "what's important now" answered together — and splitting them doubles the friction of the review rhythm.
- **`/debt-ops:resolve <id>`.** An imperative close-ticket verb. Adds ceremony around paydown that "Boy Scout + remove the marker + next review drops it" already handles without a verb. Conflicts with the Google "improvement, not perfection" stance (`docs/tech-debt-management.md:155`) by treating each item as a ticket to close rather than a signal that fades as the code improves.
- **Local behavioral hotspot scorer.** The v1 plan already debated this and cut it: "lines × git frequency is a misleading complexity proxy" (`docs/tech-debt-plugin-plan.md:310-313`). The review skill uses *churn count* only — change frequency without pretending it's complexity — which honestly represents Pareto without faking the complexity half. The real Code Health signal waits for v3's CodeScene MCP.
- **Run on a `Stop` hook tripwire.** A second tripwire alongside ADR 0005's per-session block cap (e.g., "review overdue by 7 days"). Pushes the dev into review when they're trying to ship — exactly the flow-break ADR 0004 was designed to remove. Manual invocation respects the dev's rhythm; the metrics skill already exposes the "you might want to review" signal.

## When to revisit

- If the Git-based staleness check produces too many false positives (entries flagged stale that are still real because the marker moved files), tighten the audit: also grep neighboring files in the same module, or store the marker text itself in the entry frontmatter at register time so the audit has an anchor.
- If the churn-based ranking consistently surfaces low-value entries (vanity refactors of healthy code, the Pillar 3 anti-pattern, `docs/tech-debt-pillars.md:236-239`), promote to a real behavioral signal — this is the trigger to wire v3's CodeScene MCP.
- If the dev wants to run review automatically (e.g., every Monday morning), the natural shape is a scheduled remote agent, not a new hook. Document the recipe; don't grow the plugin.
- If 90%+ of entries are dropped as stale on first review, the capture rule is too aggressive — revisit Discipline 1 wording before revisiting the audit logic.
