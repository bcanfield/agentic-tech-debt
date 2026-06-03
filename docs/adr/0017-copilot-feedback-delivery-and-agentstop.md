# 0017 — Copilot write-time feedback delivery (#2980 workaround) + agentStop safety net

**Date:** 2026-06-02
**Status:** Accepted

## Context

Two Copilot-CLI hook-contract facts surfaced after the adapter was packaged
([ADR 0015](./0015-copilot-plugin-and-marketplace.md)), both verified against GitHub's
current hooks reference:

1. **`postToolUse` `additionalContext` is broken upstream.**
   [copilot-cli#2980](https://github.com/github/copilot-cli/issues/2980) (open, no
   workaround offered): the CLI captures a `postToolUse` hook's `additionalContext`
   but never injects it into the agent. The write-time feedback loop — the adapter's
   whole differentiator — would run but its output would never reach the model.
2. **`agentStop` is a real block channel.** Its output contract is
   `decision: "block" | "allow"` + `reason` (the next-turn prompt) — the same shape as
   Claude/Codex's `Stop`. We had earlier written it off as "different contract,
   deferred"; that was wrong.

## Decision

**Feedback delivery — prefer `modifiedResult`.** `feedback.py` emits
`{"modifiedResult": {"resultType": "success", "textResultForLlm": <original> + "\n\n" + <summary>}}`
instead of `{"additionalContext": <summary>}` when (and only when) the tool succeeded
and exposes the documented `{resultType, textResultForLlm}` shape — `modifiedResult`
*is* forwarded to the model. It is an **append, never a replace**: the original result
text is copied through verbatim. If the tool errored or the result shape is
unrecognized, it falls back to `additionalContext` (never clobbering output) — that
path also goes live automatically once #2980 is fixed.

**Stop-time safety net — port to `agentStop`.** `stop.py` (the codex copy) runs on
Copilot's `agentStop` with two copilot deltas: read camelCase `sessionId`, and drop
the `current-turn.txt → last-batch.txt` rotation (there is no `userPromptSubmitted`
`drop` hook to consume it; manual drops read `current-turn.txt` directly). Same
two-stage marker-vs-registry block and per-session cap as the other adapters.

## Consequences

- On current Copilot CLI the safety-net nudge works (separate channel); the write-time
  summary reaches the model on edits where `modifiedResult` applies, and may not on the
  `additionalContext` fallback path until #2980 lands. The debug log + metrics record
  the run either way. Documented in `copilot/README.md`.
- `feedback.py`'s output shim now diverges further from claude/codex — tracked in
  CLAUDE.md's "Hook I/O envelope" delta.
- The `modifiedResult` preference is deliberate debt to revert once #2980 is fixed;
  mirrored by a registry entry.

## Alternatives we ruled out

- **Emit `additionalContext` only and just document #2980.** Honest but ships a
  silently-ineffective loop — the feature looks present but the model never sees it.
- **Always replace the tool result with our summary.** Simpler, but destroys the
  tool's own output (the edit confirmation). The append-or-fall-back rule avoids that.
- **Emit both `additionalContext` and `modifiedResult` every time.** Doubles the
  feedback once #2980 is fixed. Preferring one channel avoids the duplicate.

## Payoff trigger

When copilot-cli#2980 is fixed: drop the `modifiedResult` preference and emit
`additionalContext` (the clean channel that doesn't touch tool output).
