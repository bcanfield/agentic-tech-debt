# 0003 — Stop hook as Discipline 1 safety net

**Date:** 2026-05-08
**Status:** Accepted

## Context

v1 deliberately cut the Stop hook on the bet that the SessionStart "additionalContext" inject (Discipline 1) would be enough to get Claude to register deferrals. Four days of dogfood in `mediamtx-connect` produced **0 registry entries across 69 edits** including architecturally interesting changes (`instrumentation.ts`, a new API route, `env.ts` ×4). The pattern: Claude reads the inject once at session start, then under context pressure on long turns in repos with dense in-repo `CLAUDE.md` rules, the discipline gets crowded out and forgotten.

## Decision

Add a `Stop` hook (`claude-code/scripts/stop.py`) that fires at the end of every turn. It runs in two stages, only one of which can fire per turn:

- **Stage 1 — specific marker count.** Scan `git diff HEAD` plus untracked files for newly-added `TODO`/`FIXME`/`HACK`/`XXX` marker lines, compared to new entries under `debt/registry/`. If markers > registrations, block with the exact count: "register the N unregistered deferrals." Mechanical — Claude doesn't need judgment, just to act on the number.
- **Stage 2 — broad-judgment block.** Only fires when stage 1 is silent AND no new registry entries exist AND the turn produced any code change outside `debt/registry/` / `doc/adr/`. Block with a prompt that enumerates Discipline 1's full scope (stubs / 501 returns, `as any` / `@ts-ignore`, `.skip()` / bypassed checks, `catch {}` swallowed errors, "later" / "for now" prose comments, mocked integrations) and asks Claude to scan its own diff (which it already has in context) and register what fits — or explicitly acknowledge nothing fits and continue.

The two-stage shape lets the cheap regex catch the deterministic cases while Claude's judgment fills in the long tail of non-marker debt. Paths under `debt/registry/` and `doc/adr/` are excluded from both stages so registration activity itself never trips the hook.

**Schema note (discovered at first test):** Claude Code's Stop-hook output schema does *not* support `hookSpecificOutput.additionalContext` (that field is reserved for `PreToolUse`/`UserPromptSubmit`/`PostToolUse`/`PostToolBatch`). The first implementation emitted `additionalContext` and was rejected with a validation error. `decision: "block"` is the only documented mechanism for surfacing a nudge — which means *blocking* is the only available behavior, not an opt-in promotion path.

## What this means for you

- The plugin now nudges Claude **every turn**, not just at session start. Long sessions in dense-rules repos no longer lose the discipline.
- You don't need to run `/debt-ops:init` per-repo to make Discipline 1 fire reliably — the safety net works without modifying any `CLAUDE.md`.
- Coverage is broad on purpose: stage 2 catches non-marker debt (stubs, loosened types, swallowed errors, "later" comments, mocked integrations) that the regex sniff alone would miss.
- Stage 2 fires on *every* code-change turn that didn't register anything, which means pure refactors / renames / formatting will see a brief "no debt introduced, continuing" exchange before stopping. That's the cost of broader coverage. No-op turns and doc-only turns stay silent.
- Expect occasional false-positive nudges (e.g., literal `TODO` strings in test fixtures, in plugin source code that mentions the regex itself, in docs that list marker names). Reply "drop it" to clear spurious registry entries.

## Alternatives we ruled out

- **Strengthen the SessionStart inject only.** Tighter wording would help marginally but wouldn't fix the root issue: any one-shot inject loses weight under long-context pressure. Same failure mode we just observed.
- **Write disciplines into `~/.claude/CLAUDE.md` globally.** Research across Anthropic's official plugins showed only two write to `CLAUDE.md` and both require explicit user invocation. Plugin-driven `CLAUDE.md` modification is against the grain of the platform's conventions.
- **Observational nudge via `additionalContext`** (what we originally planned). Less forceful, doesn't interrupt mid-flow on false positives. **Not available**: the Stop-hook schema doesn't accept `additionalContext`. We'd have to invent our own out-of-band channel (e.g., write a file Claude reads later), which is more complexity than the false-positive cost is worth.
- **Pure regex sniff (markers only).** Cheap and deterministic but blind to non-marker debt — which is most of it. First mediamtx test (a 501-stub route handler) only got caught because it also happened to include a `TODO` comment; without that, the regex would have missed the actual deferral signal (the 501 status). Superseded by the stage-1 + stage-2 split.
- **Pure judgment on every turn** (drop the regex, always block on code-change turns asking Claude to scan its diff). Maximum coverage but pays the block cost on every code turn including ones with obvious markers where a specific count is more actionable. Hybrid wins by giving Claude a precise instruction when one exists and falling back to judgment only when needed.

## When to revisit

- If stage 2 over-blocks on legitimate refactors (e.g., the "no debt introduced, continuing" exchange shows up too often or annoys), tighten the gate: require a minimum diff size, exclude additional path patterns (e.g., `**/*.test.*`, `**/__tests__/**`, formatter-only changes), or require new lines (not just modified lines) before firing.
- If stage 1's regex starts producing many false positives (`TODO` in test fixtures, docs that enumerate marker names), add path-based exclusions or a per-file allowlist.
- If Claude routinely under-registers under stage 2 (registers fewer entries than the diff actually warrants), make the stage-2 prompt more specific — e.g., echo a snippet of the diff into the block reason so Claude reasons against concrete code rather than generic categories.
- If blocking proves too disruptive overall, explore an out-of-band channel: write the nudge to a file the SessionStart hook re-injects on the next session, or emit a `systemMessage` (semantics of that Stop-hook field are not yet verified).
