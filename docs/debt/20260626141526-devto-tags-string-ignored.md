---
id: 20260626141526
title: devto-tags-string-ignored
principal: 30min
interest: +manual PUT per dev.to post
hotspot: .claude/skills/publish-to-devto/scripts/prepare.py
business_capability: article publishing
payoff_trigger: next dev.to publish run
quadrant: prudent-deliberate
category: code_quality
ai_authored: true
created: 2026-06-26
---

publish-to-devto's prepare.py writes `tags` as a comma-separated string in article.json; dev.to's POST /api/articles silently ignores that format, so posts publish with zero tags. Worked around for the curl article via a manual PUT sending tags as a JSON array. Root cause unfixed: prepare.py should emit `tags` as a JSON array. Adapter parity — the fix must propagate to every duplicated copy of prepare.py per CLAUDE.md.
