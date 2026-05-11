---
name: init
description: This skill should be used ONLY when the user explicitly invokes /debt-ops:init. It writes the debt-ops disciplines + cached quality commands into CLAUDE.md as a `## Tech debt operations` section so a team shares one source of truth. Opt-in by design; solo users skip it (the SessionStart inject covers the same ground per-session). Re-running regenerates only the managed section, never touches other sections.
disable-model-invocation: true
allowed-tools: Read, Write, Edit, Bash
---

# /debt-ops:init

Write or update a `## Tech debt operations` section in `./CLAUDE.md`. Idempotent — only the managed section changes.

## 1. Read the cached commands

```bash
TOPLEVEL=$(git rev-parse --show-toplevel)
REPO_HASH=$(printf '%s' "$TOPLEVEL" | shasum | cut -c1-12)

# Locate this repo's plugin cache. CLAUDE_PLUGIN_DATA is set in hook
# subprocesses but NOT in the skill's bash env, so glob the standard
# Claude Code plugin-data dirs and fall back to the legacy cache path.
CACHE_DIR=""
for D in \
    ${CLAUDE_PLUGIN_DATA:+"$CLAUDE_PLUGIN_DATA/cache/$REPO_HASH"} \
    "$HOME/.claude/plugins/data"/debt-ops*/cache/"$REPO_HASH" \
    "$HOME/.cache/debt-ops/cache/$REPO_HASH"; do
  [ -d "$D" ] && { CACHE_DIR="$D"; break; }
done

LIST="$CACHE_DIR/feedback.list"
[ -n "$CACHE_DIR" ] && [ -f "$LIST" ] && cat "$LIST"
```

If the file doesn't exist, the SessionStart discovery prompt hasn't run yet. Tell the developer:

> No cached quality commands yet. Start a new session so I can detect them, then re-run /debt-ops:init.

…and stop.

## 2. Compose the section (template)

Substitute `{{COMMANDS}}` with the cache contents verbatim.

```markdown
## Tech debt operations

<!-- this section is auto-managed by the debt-ops Claude Code plugin; safe to edit, run /debt-ops:init to regenerate -->

### Disciplines

1. If you defer work — decision unmade, stub, loosened type, "future"/"later" comment, or `TODO`/`FIXME`/`HACK`/`XXX` marker — register via `/debt-ops:add` immediately. Test: would a future reader ask "why this way?" If yes, register. No prompt. Use `payoff_trigger: unknown` if unsure. Announce: `+1 entry: <slug> (drop?)`. Over-register freely; the developer drops with "drop it".

2. When making an architecturally significant change — a data model, public interface, security boundary, release pipeline, or a dep-manifest change that is a major-version bump or a *new* top-level dependency — draft an ADR under `doc/adr/` in Nygard format (Context, Decision, Consequences, Alternatives, Payoff trigger). Create the directory if needed. Only draft an ADR when there are two credible alternatives; if you cannot list two, it is a comment, not an ADR. If the ADR introduces deliberate debt, also call `/debt-ops:add` so the registry entry mirrors the ADR.

3. Read entries under `debt/registry/` before changing files they reference.

### Quality commands

These run after every edit under a 3 s budget per command. Edit freely; the plugin reads tolerantly. Lines starting with `#` are estimates/comments and are skipped at run time.

<!-- debt-ops:feedback v1 -->
{{COMMANDS}}
<!-- /debt-ops:feedback -->
```

## 3. Apply

- **If `./CLAUDE.md` doesn't exist:** `Write` it with the section above as the entire file.
- **If `./CLAUDE.md` has a `## Tech debt operations` section:** `Edit` to replace exactly that section — from the heading through (but not including) the next `## ` heading, or through EOF if no next heading. Leave every other byte unchanged.
- **If `./CLAUDE.md` exists without the section:** `Edit` to append the section after the last existing line, with a single blank line between.

## 4. Announce

`charter updated: ./CLAUDE.md — disciplines + N quality commands`

(N = count of non-comment, non-blank lines inside the marker block.)

## Marker contract — do not deviate

- `<!-- debt-ops:feedback v1 -->` is the open marker `feedback.py` keys on. Exact string; the `v1` is part of the marker.
- `<!-- /debt-ops:feedback -->` is the close marker.
- The self-explaining `<!-- this section is auto-managed by … -->` line is mandatory — a teammate without the plugin reads that to understand what they're seeing.
- Never touch any byte outside the `## Tech debt operations` section.
