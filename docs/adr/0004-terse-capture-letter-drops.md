# 0004 — Terse capture + letter-coded drops

**Date:** 2026-05-13
**Status:** Accepted

## Context

Dogfood feedback from `slack-agent`: mid-feature, the `/debt-ops:add` flow surfaced as a wall of text per entry — a `Bash(date)` call, a `Write` tool invocation with full frontmatter + body, an analysis paragraph framing the deferral, and a closing recap of all entries created. The capture itself was useful (the registry filled with real entries), but the noise broke flow because the developer wasn't ready to stop and triage debt — they were trying to ship the feature. Two suggestions emerged: (1) make registration "more behind the scenes," (2) let the developer drop entries with a short shorthand like `drop A` instead of typing the full slug.

The Stop hook reminder compounded the same problem: when no entries were registered on a code-change turn, stage 2 emitted a 15-line bullet list re-teaching Discipline 1 — content the agent already had loaded via the `add` skill.

## Decision

Three moves, all converging on the same shape: capture stays loud enough to course-correct, quiet enough to ignore.

- **Silent helper, one-line output.** Introduce `claude-code/scripts/register.py`. The `add` skill no longer uses the `Write` tool or `Bash(date)` — it pipes the body via heredoc to the helper, which generates the timestamp, writes the file under `debt/registry/`, and emits exactly `+1 entry: <slug> (<letter>)` on stdout. The skill instructs the agent to add no commentary. The Bash tool's stdout IS the user-facing output.
- **Letter-coded drops.** Each register call assigns the next free letter (A → Z → AA → AB …) and records `LETTER\tslug\tfname` in `$CLAUDE_PLUGIN_DATA/cache/<repo-hash>/current-turn.txt`. A new `UserPromptSubmit` hook (`drop.py`) matches `drop A`, `drop A,B`, `drop A B`, or `drop all` against that file plus `last-batch.txt`, deletes the matching entries, removes them from the mapping, and blocks the prompt with a one-line `Dropped: <slugs>.` confirmation. No Claude turn consumed. `drop it` and `drop <slug>` continue to fall through to the agent.
- **Batch rotation on clean stop.** `stop.py` moves `current-turn.txt` → `last-batch.txt` only when neither stage 1 nor stage 2 fires. That way the just-completed turn is addressable by `drop A` on the next prompt, but a re-fire under a blocked stop can't clobber an earlier batch before Claude resolves it. The stage-1 and stage-2 reasons themselves are shortened to one line each — the skill carries the definition.

## What this means for you

- A mid-turn capture now reads as a single line per entry: `+1 entry: scraper-container-not-built (A)`. No paragraph of analysis, no visible Write tool block, no closing recap.
- After a turn, type `drop A`, `drop A,C`, or `drop all` to remove letter-labeled entries from the most recent batch. The plugin confirms with `Dropped: <slugs>.` and consumes no Claude turn. The full-slug form (`drop foo-slug`) still works through the agent.
- Stop-hook nudges are now one-liners. The agent has the discipline loaded via the skill; the hook is a tripwire, not a tutorial.
- `register.py` is the recommended path. The `Write`-tool fallback still produces a valid entry file but skips letter assignment, so the entry can only be dropped by slug.

## Alternatives we ruled out

- **Fully silent capture with a separate review file.** Modeled on the `un-punt` skill: register silently to disk and never announce. Loses the immediate course-correct signal — the developer wouldn't see "Claude flagged the stat-fallback as debt" until they explicitly reviewed the file, by which time the entry has hardened and the moment to say "no, that's intentional" has passed. One-line mid-turn keeps the signal without the wall of text.
- **End-of-turn batched recap, no mid-turn output.** Surfacing only at end of turn means the developer can't object until the whole batch lands. With mid-turn one-liners, they can interject after the first entry if Claude is mis-flagging — cheaper than rolling back three entries at end-of-turn.
- **Numeric labels instead of letters.** Numbers collide visually with line numbers, timestamps, and PR/issue references in agent output. Letters are visually distinct and short. The base-26 column-style fallback (`AA`, `AB`…) covers the rare turn that captures 27+ entries.
- **Have the agent track letters itself in chat context.** Fragile — long turns lose track, and the mapping vanishes across sessions. The cache file is durable and stateless from the agent's perspective.

## When to revisit

- If the helper's argument list grows beyond ~10 flags as the schema evolves, switch to a single `--json` flag taking the whole frontmatter as a JSON blob (cleaner for agents to construct).
- If `drop A` false-fires on real prose ("drop a couple of these"), tighten the regex — current pattern requires the whole prompt to match `drop <letter-tokens>`, so prose with extra words already passes through.
- If multiple captures within the same second collide and the `-2`/`-3` suffix becomes common, upgrade the ID to include microseconds.
- If the rotation-on-clean-stop rule causes confusion (entries from a blocked-then-resumed turn end up in a different batch than the user expects), explore a per-prompt rotation trigger in the `UserPromptSubmit` hook instead.
