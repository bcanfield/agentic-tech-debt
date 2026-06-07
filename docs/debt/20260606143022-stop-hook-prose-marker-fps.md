---
id: 20260606143022
title: stop-hook-prose-marker-fps
principal: 2h
interest: blocking stop-hook nag every turn that writes eval/article markdown
hotspot: claude-code/hooks/stop.py
business_capability: debt-ops-plugin
payoff_trigger: next session that generates articles or eval artifacts under .claude/
quadrant: prudent-inadvertent
category: code_quality
ai_authored: false
created: 2026-06-06
---

The Stop hook's marker scan counts TODO/FIXME/HACK occurrences in prose markdown written under .claude/skills/ eval workspaces (articles that *teach* grepping for markers), despite the recent "ignore prose files in marker scan" fix. This session it escalated 8 -> 13 -> 20 phantom markers across three stops. Either the prose-ignore rule doesn't cover non-docs paths or the exact-line requirement isn't applied here.
