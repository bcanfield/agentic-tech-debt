---
id: 20260714122037
title: renovate-out-of-repo-settings
principal: unknown
interest: unknown
hotspot: .github/renovate.json
business_capability: release
payoff_trigger: Mend app pricing/limit change, real tests added (extend required checks), or major-update PRs piling up unmerged
quadrant: prudent-deliberate
category: infrastructure
ai_authored: true
created: 2026-07-14
---

Renovate automerge depends on state that lives outside the repo: the Mend-hosted app installation, the allow-auto-merge repo setting, and branch protection requiring the `scan` check — none of it visible or restorable from a clone. The only merge gate is the HOL scanner (no real tests), and majors queue for manual review. Mirrors docs/adr/0022-renovate-automerge-replaces-dependabot.md.
