# 0014 — Keep adapters duplicated; sync by AI, don't extract `_common.py`

**Date:** 2026-06-02
**Status:** Accepted (supersedes ADR 0011's extraction trigger and packaging-plan Phase E)

## Context

[ADR 0011](./0011-codex-adapter-self-contained.md) accepted the adapter script
duplication and scheduled a vendored `_common.py` extraction *when a third adapter
lands*. We now have four implementations — `claude-code/`, `codex/`, `copilot/`, and
the portable `skills/` — so that trigger has fired, and the packaging plan named the
extraction as Phase E. The maintainer's call: keep full duplication and maintain
parity by hand/AI instead of building the extraction.

## Decision

No shared or vendored runtime module. Each adapter stays self-contained with its own
copy of the helper scripts and skills. Parity is maintained per-change: a
shared-logic edit is propagated to every copy in the same PR, preserving each
adapter's documented deltas. The policy and the full map of duplicated areas live in
CLAUDE.md under "Adapter parity — duplicated on purpose."

## What this means for you

- Installing any adapter standalone is unchanged — self-containment was already the
  shipped behavior.
- Contributing a shared-logic change means editing *every* copy in one PR.
  CLAUDE.md's "Adapter parity" section is the checklist of what's duplicated and
  what's intentionally different. There is no build or vendoring step to run.

## Alternatives we ruled out

- **Extract a vendored `_common.py` copied into each plugin at release time** (ADR
  0011's plan / Phase E). It adds a release-time copy mechanism and a build step for
  ~6 small stdlib scripts. The maintainer prefers AI-assisted sync over carrying
  that tooling.
- **A runtime pip/npm dependency.** Still violates the stdlib-only, zero-dependency
  constraint the hooks rely on.

## When to revisit

- If AI-sync drift ships a **real bug** more than rarely — a fix landing in one copy
  and not the others, reaching users — reconsider the extraction. That's the same
  failure signal ADR 0011 named; we've simply chosen the lighter mitigation first.
- If the per-adapter deltas grow to the point that "diff against `claude-code/` and
  propagate" stops being a reliable mental model, the duplication has outgrown
  hand-sync.
