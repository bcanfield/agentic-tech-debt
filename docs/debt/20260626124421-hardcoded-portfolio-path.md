---
id: 20260626124421
title: hardcoded-portfolio-path
principal: 1h
interest: unknown
hotspot: .claude/skills/publish-to-portfolio/scripts/stage.py
business_capability: content-publishing
payoff_trigger: portfolio repo moves or the brandincanfield.com domain changes
quadrant: prudent-deliberate
category: code_quality
ai_authored: true
created: 2026-06-26
---

The portfolio repo path (/Users/bcanfield/Documents/Git/portfolio-2) and SITE_URL (https://brandincanfield.com) are hardcoded as defaults in publish-to-portfolio/scripts/stage.py and publish-to-devto/scripts/prepare.py. Fine for a single-user personal skill — stage.py exposes --portfolio and prepare.py --image-base as overrides — but the canonical/site URL is baked in. A future reader would ask why these aren't env/config. Cheap to externalize if the repo location or domain ever changes.
