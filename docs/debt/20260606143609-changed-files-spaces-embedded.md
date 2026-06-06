---
id: 20260606143609
title: changed-files-spaces-embedded
principal: small
interest: feedback commands silently fail on filenames with spaces when $CHANGED_FILES is embedded in a larger token
hotspot: */hooks/feedback.py run_one
business_capability: write-time quality feedback
payoff_trigger: a user reports feedback commands failing on paths with spaces
quadrant: prudent-deliberate
category: code_quality
ai_authored: true
created: 2026-06-06
---

A bare `$CHANGED_FILES` token now expands to one argv entry per file, which
handles spaces correctly. The embedded form (`--files=$CHANGED_FILES`) still
substitutes the space-joined string, so a filename with a space splits into
two values inside that single argument. Fixing it would need a delimiter
convention (e.g. comma) that varies per tool, so we left the joined string
and documented it in the run_one comment. Applies to all three feedback.py
copies (claude-code, codex, copilot).
