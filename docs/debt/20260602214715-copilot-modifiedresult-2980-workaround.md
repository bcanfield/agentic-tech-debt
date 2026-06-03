---
id: 20260602214715
title: copilot-modifiedresult-2980-workaround
principal: 2h
interest: feedback.py mutates tool output instead of using the clean additionalContext channel
hotspot: copilot/hooks/feedback.py (build_payload)
business_capability: copilot write-time loop
payoff_trigger: when copilot-cli#2980 is fixed (postToolUse additionalContext injected)
quadrant: prudent-deliberate
category: code_quality
ai_authored: true
created: 2026-06-02
---

copilot feedback.py prefers modifiedResult over additionalContext to dodge copilot-cli#2980 (postToolUse additionalContext not injected into the agent). It appends the pass/fail summary to the tool's own textResultForLlm rather than using the clean side-channel. Deliberate workaround per ADR 0017; revert to additionalContext-only once the upstream bug is fixed.
