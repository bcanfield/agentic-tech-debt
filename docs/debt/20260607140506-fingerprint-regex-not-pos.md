---
id: 20260607140506
title: fingerprint-regex-not-pos
principal: 1d
interest: false positives/negatives vs true Biber features; counts are directional only
hotspot: .claude/skills/ai-smell-review/scripts/fingerprint.py
business_capability: content-pipeline
payoff_trigger: reviewer edits driven by a miscount, or a real POS tagger becomes worth the dependency
quadrant: prudent-deliberate
category: code_quality
ai_authored: true
created: 2026-06-07
---

fingerprint.py approximates the PNAS instruction-tuning fingerprint (participial clauses, nominalizations, agentless passives) with regexes instead of POS tagging, to stay stdlib-only per project rules. The passive and participial patterns have known false-positive classes (adjectival -ed forms, gerund nouns). Counts are labeled directional and the LLM reviewer interprets them, which bounds the damage, but the numbers are not comparable to the paper's rates.
