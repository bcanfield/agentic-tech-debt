---
name: debt-ops-disable
description: Turn debt-ops off (or back on) for the current repo. Run ONLY when the user explicitly asks to disable, turn off, silence, or re-enable debt-ops here — never auto-invoke. Flips a per-repo marker in the plugin cache; nothing is written to the working tree.
---

# debt-ops-disable — turn debt-ops off for this repo

**Run only on explicit user request** ("disable debt-ops here", "turn debt-ops
off", "re-enable debt-ops"). Do not invoke this as part of normal work.

Call `toggle.py` via Bash. It flips a `disabled` marker in this repo's plugin
cache dir (ADR 0020). While the marker is present, every hook idles silently —
no write-time feedback, no agentStop nudge. Nothing lands in the working tree,
so it never shows up in `git status`.

The marker is per-machine, not committed — it disables debt-ops for *you* in
*this* repo. The script's stdout IS the confirmation; add no commentary.

## The call

```bash
# Toggle (or pass `disable` / `enable` to force a direction):
python3 scripts/toggle.py disable
python3 scripts/toggle.py enable
```

Match the user's intent: pass `disable` when they ask to turn it off, `enable`
when they ask to turn it back on. Omit the argument only when they say "toggle."
