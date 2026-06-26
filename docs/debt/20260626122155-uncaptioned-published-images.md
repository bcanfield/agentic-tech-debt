---
id: 20260626122155
title: uncaptioned-published-images
principal: 1d
interest: +manual caption edit per image per post
hotspot: .claude/skills/publish-to-medium, .claude/skills/publish-to-hashnode
business_capability: content-publishing
payoff_trigger: when captions are wanted for accessibility/context on published posts
quadrant: prudent-deliberate
category: code_quality
ai_authored: true
created: 2026-06-26
---

Both publish skills (Medium + Hashnode) drop image captions: the markdown alt text is used only to locate/inject images, never written into the platform's caption field, so published images appear uncaptioned. Deliberate scope cut "for now", flagged to the user both times. prepare.py already parses the alt text so the data is available, and both editors expose a caption input under each inserted image — paying this down means typing the alt into that field after each image injection.
