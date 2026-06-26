---
id: 20260626124430
title: devto-no-update-path
principal: 2h
interest: +1 stale duplicate post per re-publish
hotspot: .claude/skills/publish-to-devto/SKILL.md
business_capability: content-publishing
payoff_trigger: first time an already-published dev.to article needs editing via the skill
quadrant: prudent-deliberate
category: code_quality
ai_authored: true
created: 2026-06-26
---

publish-to-devto only does POST /api/articles, which creates a NEW post every run (dev.to 422s on a duplicate title). Updating an existing post needs PUT /api/articles/{id} with the id captured from the create response — explicitly left out of scope. Until then, re-running on an already-published article either fails or makes a duplicate. Add an --update <id> path (or persist the returned id) when editing becomes a real need.
