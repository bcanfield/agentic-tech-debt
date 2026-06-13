---
id: 20260612222441
title: paydown-plan-deterministic-selection
principal: 3h
interest: autonomous paydown selects the green set by agent judgment, so a CI run's 'what will it touch' isn't auditable pre-run or reproducible; reviewers trust the model's selection instead of inspecting a deterministic plan
hotspot: claude-code/skills/review/scripts/review.py (+3 duplicated copies), skills/*/paydown
business_capability: paydown-automation
payoff_trigger: autonomous-PR accept-rate data exists and CI usage justifies it (ADR 0021), OR a reviewer asks 'why did the loop touch these entries?' and it isn't reconstructable
quadrant: prudent-deliberate
category: infrastructure
ai_authored: true
created: 2026-06-12
---

ADR 0021 ships autonomous paydown with the green/escalate selection left to agent
judgment, and explicitly defers the deterministic selector as registered debt rather
than building it speculatively.

The deferred work: extend `review.py` with a `--plan` mode that emits the
green / escalate / skip buckets as JSON with a reason per entry, using signals it
already computes (hotspot existence, churn, quadrant) plus a principal parse and a
boundary-keyword check. That makes "exactly what the CI loop will touch, and why"
auditable before the run and reproducible across runs — the CI safety story ADR 0021
leans on. Must land in all four review.py copies (parity).

Also deferred here: a `paydown` event shape in metrics.jsonl (entries paid / escalated /
failed per run) so the metrics skill can report autonomous-paydown health and the
accept-rate signal ADR 0021's revisit trigger needs.

Not built now per "don't over-engineer / markdown not orchestration" — the loop works
on judgment today; this is the determinism upgrade for when CI usage justifies it.
