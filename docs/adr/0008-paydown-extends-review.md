# 0008 — Paydown extends review (one skill, not two)

**Date:** 2026-05-27
**Status:** Accepted

## Context

ADR 0007 closed the audit + triage gap with `/debt-ops:review` and committed to "paydown happens through normal work, not a `resolve` verb." That assumed the dev already knows which entry to fix and how. Dogfood at 30+ entries surfaces the real gap: the report identifies the top items, but the dev still has to copy a slug, frame the fix, pick a test approach, and remember to drop the entry afterward — friction that pushes paydown into "later" until later never comes. The research is unanimous on the shape (continuous over stop-the-world, TDD as guardrail per Beck, writer/reviewer separation per Anthropic, comprehensibility per Willison, improvement-not-perfection per Google, Pareto/hotspot focus per CodeScene, `docs/tech-debt-management.md:25,78,115,156,162`). Closing the loop needs guidance, not a new command.

## Decision

Paydown is the third beat of the review rhythm, not a second skill. `/debt-ops:review`'s body gains a short rubric — Fowler triage, TDD where tests exist, comprehensibility, code-review sub-agent for high-risk or AI-authored fixes, no auto-commit, `drop` as the close — that Claude applies when the user follows up with "fix the top one" / "let's pay these down" / "do A." The first turn still prints the report verbatim and stops (today's UX); the rubric only fires on a follow-up paydown intent. No new Python: `review.py` already produces letter codes and audit signals; `drop.py` already closes entries. The added surface is markdown in the skill body and one ADR — nothing more.

## What this means for you

One command stays one command. `/debt-ops:review`, then if you want to keep going, say "fix the top one" or "walk through them with me" — Claude reads the entries, proposes the smallest fix per entry, writes a failing test first when tests exist nearby, surfaces a diff, and waits for your call. Risky fixes (auth, payments, migrations, `ai_authored: true`) get a fresh-context review pass via the existing `code-review` skill. Close each entry with `drop A` — same UX as today. Never auto-commit; the user runs the gates and commits.

## Alternatives we ruled out

- **Separate `/debt-ops:paydown` skill.** ADR 0007 already rejected splitting audit from triage on the "same act" grounds (`doc/adr/0007-registry-review-skill.md:37`); paydown is the next beat of the same act. Two commands doubles friction and re-creates the "tech-debt backlog" anti-pattern the research is unanimous against (`docs/tech-debt-management.md:78`).
- **A `paydown.py` orchestrator that scripts per-entry decisions.** Violates `CLAUDE.md`'s "guide Claude with markdown, not orchestration." Claude reading the registry entry, the hotspot file, and adjacent tests adapts to the repo better than any state machine; Python is for what Claude shouldn't redo (timestamps, audits, atomic I/O).
- **`/debt-ops:resolve <slug>` verb.** ADR 0007 ruled this out; `drop` after a fix is the close, no new ceremony.
- **Unsupervised `--auto` batch mode.** GitClear's 211M-LOC data (`docs/tech-debt-management.md:32-36`) — 4× duplicate blocks, doubled short-term churn under fast AI — is what unsupervised cleanup produces. User-in-the-loop, one entry at a time.
- **PostToolUse hook that proposes paydown after every edit.** Breaks the dev's rhythm; ADR 0007's "paydown is a rhythm the developer owns" applies.

## When to revisit

- If `review/SKILL.md` exceeds ~80 lines under the added rubric, split paydown into its own skill that the review skill references.
- If Claude over-acts on the first-turn report (treats the rubric as "now go fix" instead of waiting for the user's intent), harden the boundary in the skill body or split.
- If the code-review sub-agent invocation cost dominates per-fix tokens, downgrade to user-only review for low-risk fixes and reserve the sub-agent for the high-risk list.
- If 90%+ of paydown sessions only drop entries (no fixes attempted), the rubric is too lenient on "looks already fixed" and needs a stricter signal — re-enable a marker-grep check in `review.py`'s audit phase.
