---
id: 20260607142310
title: skill-triggers-unoptimized
principal: 2h
interest: possible mis/under-triggering of write-article and ai-smell-review
hotspot: .claude/skills/write-article/SKILL.md
business_capability: content-pipeline
payoff_trigger: either skill fails to auto-trigger on a natural request, or triggers when it shouldn't
quadrant: prudent-deliberate
category: testing
ai_authored: true
created: 2026-06-07
---

Both content-pipeline skills shipped with hand-written descriptions; the skill-creator trigger-optimization loop (20-query eval set, train/test split, 5 iterations) was deliberately skipped to make the June 8 launch. Descriptions were written pushy-by-convention but never measured against should/should-not-trigger queries.
