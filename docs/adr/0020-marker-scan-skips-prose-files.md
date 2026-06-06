# 0020 — Stop-hook marker scan skips prose files

**Date:** 2026-06-06
**Status:** Accepted

## Context

The Stop hook counts newly-added `TODO|FIXME|HACK|XXX` lines as a Discipline-1 tripwire. It scanned
every changed file, including prose markdown — so docs that *discuss* tech debt (article drafts,
research notes, a headline like "Registry vs TODO comments vs Jira") tripped repeated false blocks.
Reproduced live in this repo on 2026-06-06: three prose mentions, three demands to register. The
same root class hit `feedback.py`/`session-start.py`, which matched the `<!-- debt-ops:feedback v1 -->`
marker as a substring — a prose *mention* of the marker string opened the command block and executed
CLAUDE.md bullets as shell commands.

## Decision

1. `is_excluded()` in every `stop.py` also excludes prose suffixes (`.md`, `.markdown`, `.rst`,
   `.txt`, `.adoc`) from marker counting and from the stage-2 "code changed" gate (which already
   documented doc-only edits as out of scope).
2. The feedback marker only opens/closes a block when the stripped line **equals** the marker string
   (`feedback.py` × 3, `session-start.py` charter check × 2). A prose-only mention falls through to
   the cached command list instead of returning an empty block.

## Consequences

- Docs-heavy repos stop getting false Stop blocks; debt noted in prose is still caught by
  judgment-based registration (Discipline 1 is explicit that markers are only the obvious case).
- A genuine `TODO` in a README is no longer counted — accepted; the scan is a tripwire, not an audit.
- Charter authors must keep the feedback markers on their own lines (the init skills already write
  them that way).

## Alternatives

- **Scan only fenced code blocks inside markdown.** Keeps real code-snippet TODOs countable, but adds
  a markdown parser to a stdlib tripwire for marginal recall — rejected.
- **Anchor markers with a stricter regex (e.g. `(?i)^\s*#?\s*TODO:`).** Cuts some prose hits but not
  titles like "Registry vs TODO vs Jira"; suffix exclusion is simpler and complete for the observed
  failure.

## Payoff trigger

Users report missed marker debt in docs/prose files (revisit fenced-block scanning then).
