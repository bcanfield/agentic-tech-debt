---
id: 20260702084117
title: per-session-browser-profiles
principal: 4h
interest: re-login per multi-target publish run
hotspot: .claude/skills/publish-to-medium/SKILL.md
business_capability: content-publishing
payoff_trigger: unknown
quadrant: prudent-deliberate
category: infrastructure
ai_authored: true
created: 2026-07-02
---

agent-browser runs one shared daemon that shows a single window, so two headed sign-in sessions (Medium + Hashnode) can't stay open at once — opening the second replaces the first, and closing before cookies flush drops the login. The publish-to-medium and publish-to-hashnode skills now document a sequential-login workaround (sign in, verify persistence, close --all, next) instead of the real fix: give each session its own persistent browser profile so multiple headed windows coexist and logins are truly frontloaded in one pass. Deferred because per-profile isolation needs agent-browser flag research and wasn't blocking this run.
