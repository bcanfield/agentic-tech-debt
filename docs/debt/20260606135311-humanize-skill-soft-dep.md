---
id: 20260606135311
title: humanize-skill-soft-dep
principal: 2h
interest: weaker tell-audit on machines without humanize
hotspot: .claude/skills/write-article/SKILL.md
business_capability: content-pipeline
payoff_trigger: articles written from a machine without the humanize skill installed
quadrant: prudent-deliberate
category: documentation
ai_authored: true
created: 2026-06-06
---

The write-article skill defers its full AI-tell catalog and deterministic audit to the user-level humanize skill (~/.claude/skills/humanize) and its check_tells.py, neither of which is checked into this repo. SKILL.md inlines only a high-signal subset as fallback, so on a machine without humanize the audit step silently degrades. Bundling or vendoring the checker was skipped to avoid duplicating an actively-maintained skill.
