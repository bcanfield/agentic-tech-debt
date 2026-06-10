---
name: disable
description: Turn debt-ops off (or back on) for the current repo. Run ONLY when the user explicitly asks to disable, turn off, silence, or re-enable debt-ops here — never auto-invoke. Flips a per-repo marker in the plugin cache; nothing is written to the working tree.
disable-model-invocation: true
allowed-tools: Bash(python3 *)
# Hidden from `npx skills` discovery — this copy ships in the Claude Code plugin (uses ${CLAUDE_PLUGIN_ROOT}); the portable skills/ copy is the one for the skills CLI.
metadata:
  internal: true
---

# /debt-ops:disable — turn debt-ops off for this repo

Call `toggle.py` via Bash. It flips a `disabled` marker in this repo's plugin
cache dir (ADR 0020). While the marker is present, every hook idles silently —
no session inject, no write-time feedback, no stop nudge. Nothing lands in the
working tree, so it never shows up in `git status`.

The marker is per-machine, not committed — it disables debt-ops for *you* in
*this* repo. The script's stdout IS the confirmation; add no commentary.

## The call

```bash
# Toggle (or pass `disable` / `enable` to force a direction):
python3 ${CLAUDE_PLUGIN_ROOT}/skills/disable/scripts/toggle.py disable
python3 ${CLAUDE_PLUGIN_ROOT}/skills/disable/scripts/toggle.py enable
```

Match the user's intent: pass `disable` when they ask to turn it off, `enable`
when they ask to turn it back on. Omit the argument only when they say "toggle."

## Don't

- Don't run this as part of normal work — only on an explicit request.
- Don't echo or paraphrase the script's output; the Bash result is already visible.
