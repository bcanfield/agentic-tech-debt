---
id: 20260606143022
title: feedback-hook-runs-prose
principal: 4h
interest: wall of FAIL noise in every PostToolUse on Write/Edit in this repo
hotspot: claude-code/hooks/feedback.py
business_capability: debt-ops-plugin
payoff_trigger: first session debugging quality-command output in this repo
quadrant: prudent-inadvertent
category: code_quality
ai_authored: false
created: 2026-06-06
---

The PostToolUse feedback hook is executing lines of CLAUDE.md prose (the adapter-parity section) as shell commands, emitting ~30 "command not found" FAIL lines per Write/Edit. Likely the quality-command extraction reads past the debt-ops:feedback marker block or a stale cached command list survived the marker-scan fix. Observed on every file write this session.
