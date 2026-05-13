# 0005 — Stop hook: one block per session

**Date:** 2026-05-13
**Status:** Accepted

## Context

ADR-0003 chose to let the Stop hook fire every turn (gated by a state fingerprint cache from `20679ee`) so Discipline 1 wouldn't get crowded out under long-context pressure. Dogfood feedback exposed two holes in that bet. First, the fingerprint includes the full `git diff HEAD`, so any incidental edit between Stop fires — a whitespace tweak, a reformat — produces a new fingerprint and re-fires the block. Active development thus surfaces a nudge on essentially every code-change turn. Second, the state file holds only one fingerprint at a time, so a state cycle (fp_A → fp_B → fp_A) can re-fire because the inner fingerprint was overwritten. In a live `slack-agent` session this manifested as the same Stage 1 block repeating turn after turn without making progress — the exact "wall of text" friction ADR-0004 was trying to soften, just through a different vector.

## Decision

Add `SESSION_BLOCK_CAP = 1` and gate every Stage 1 / Stage 2 emit on it. Stop hook parses `session_id` from its stdin payload, reads `<cache>/session-blocks` (format: `<session_id>\t<count>`), and refuses to emit a block when the count for the current session has reached the cap — even if the fingerprint check would have allowed it. A mismatched stored session_id implicitly resets the count, so SessionStart needs no new logic. The fingerprint cache remains as the inner gate (suppresses re-fires for unchanged state, which don't count against the cap).

## What this means for you

- A given session sees at most one Stop-hook block, period. After it fires once, the rest of the session is silent regardless of what you (or Claude) do.
- The SessionStart inject still surfaces Discipline 1 at session start. Combined with one mid-session block ceiling, the discipline gets two reminder windows per session instead of one-per-turn.
- The `add` skill remains loaded throughout, so Claude can still auto-invoke `/debt-ops:add` proactively — the cap only limits the hook's reactive nudge, not voluntary registration.
- Same caveat as ADR-0003 applies: in pure-refactor turns where you registered nothing, you may see exactly one "review your diff for deferrals" line — and only one.

## Alternatives we ruled out

- **Cap at 2 or 3.** More forgiving, but the dogfood signal was strong: any repetition feels like spam mid-feature. One nudge is the smallest unit that still surfaces the discipline; anything above one re-introduces the friction we're trying to fix.
- **Fingerprint-set instead of cap.** Store all fingerprints seen this session (capped at last ~50) so any cycle suppresses. Doesn't help the active-dev case where every turn legitimately changes state — you'd still see a nudge every turn. The session cap addresses both failure modes at once.
- **Per-stage caps (stage 1 = 1, stage 2 = 1, total = 2).** Cleaner in principle, but in practice the stages address the same goal (surface a missed deferral). Letting both fire in one session doubles the interruption with no qualitative gain.
- **Move the fingerprint cache to include staged changes, ignore whitespace, etc.** Doesn't bound the loop in the worst case — only narrows the trigger surface. The cap is a hard ceiling that works regardless of how the fingerprint is computed.

## When to revisit

- If the cap proves too tight — registrations drop noticeably because Claude misses cues that the second-or-third nudge would have caught — raise to 2 and re-measure via `/debt-ops:metrics`.
- If false positives become routine (stage 2 nudging on legitimate pure-refactor turns), pair the cap with a path-based diff filter so formatter-only changes don't trip it.
- If a future Stop-hook stage 3 is added (e.g., recommending an ADR), reconsider whether the cap should be per-stage or shared.
