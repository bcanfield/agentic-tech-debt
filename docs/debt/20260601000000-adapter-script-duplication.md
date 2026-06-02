---
id: 20260601000000
title: adapter-script-duplication
principal: 1d
interest: every shared-logic change must be hand-applied to two script sets
hotspot: codex
business_capability: plugin-maintenance
payoff_trigger: a third agent adapter is added
quadrant: prudent-deliberate
category: code_quality
ai_authored: true
created: 2026-06-01
---

The Codex adapter duplicates ~90% of the Claude adapter
(`claude-code/scripts/`) — register, review, drop, feedback, stop, session-start.
On the Codex side these live split per Codex convention: hook scripts under
`codex/hooks/`, skill helpers under `codex/skills/<skill>/scripts/`.
Accepted deliberately (ADR 0011): installed plugins are isolated, so a shared
runtime module can't travel with either without a build step, and a runtime
dependency violates the stdlib-only constraint. The cost is real: a change to
shared logic (registry schema, letter assignment, metrics format) must land in
both copies or they drift. Pay down when a third adapter lands by extracting a
vendored `_common.py` copied into each plugin at release time.
