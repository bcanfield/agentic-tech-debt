---
id: 20260601000000
title: adapter-script-duplication
principal: ongoing
interest: every shared-logic change must be hand-applied to all script copies
hotspot: codex
business_capability: plugin-maintenance
payoff_trigger: AI-sync drift ships a real bug (fix lands in one copy, not the others)
quadrant: prudent-deliberate
category: code_quality
ai_authored: true
created: 2026-06-01
---

The helper scripts and skills are duplicated across four self-contained
implementations — `claude-code/`, `codex/`, `copilot/`, and the portable
`skills/` (register, review, drop, feedback, stop, session-start; add/review/
metrics/init skills). Accepted deliberately (ADR 0011): installed plugins are
isolated, so a shared runtime module can't travel without a build step, and a
runtime dependency violates the stdlib-only constraint.

Decision update (ADR 0014): we are **not** extracting a vendored `_common.py`.
Parity is maintained by hand/AI per-change instead — see CLAUDE.md "Adapter
parity" for the policy, the full duplicate map, and the per-adapter deltas not to
flatten. The cost stays real (a shared-logic change must land in every copy or
they drift); the payoff trigger is now the failure mode, not a copy count —
revisit the extraction only if AI-sync drift actually ships a bug.
