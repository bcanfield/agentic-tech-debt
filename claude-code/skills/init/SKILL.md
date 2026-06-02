---
name: init
description: Write or refresh the `## Tech debt operations` section in CLAUDE.md so a team shares one source of truth for debt-ops disciplines and cached quality commands. Idempotent. Only the managed section changes; other sections are untouched. Invoked explicitly via /debt-ops:init (solo users get the same content from the SessionStart inject).
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

# Detected ADR/registry dirs (ADR 0006/0009). Fall back to the co-located
# defaults if the cache files aren't written yet.
ADR_DIR=$( [ -s "$CACHE_DIR/adr-dir" ] && cat "$CACHE_DIR/adr-dir" || echo "docs/adr" )
REGISTRY_DIR=$( [ -s "$CACHE_DIR/registry-dir" ] && cat "$CACHE_DIR/registry-dir" || echo "docs/debt" )
echo "adr-dir: $ADR_DIR"
echo "registry-dir: $REGISTRY_DIR"
```

If the file doesn't exist, the SessionStart discovery prompt hasn't run yet. Tell the developer:

> No cached quality commands yet. Start a new session so I can detect them, then re-run /debt-ops:init.

…and stop.

## 2. Compose the section (template)

Substitute `{{COMMANDS}}` with the cache contents verbatim, `{{ADR_DIR}}` with the detected `adr-dir`, and `{{REGISTRY_DIR}}` with the detected `registry-dir` (from step 1).

```markdown
## Tech debt operations

<!-- this section is auto-managed by the debt-ops Claude Code plugin; safe to edit, run /debt-ops:init to regenerate -->

### Disciplines

1. The test for debt: would a future reader ask "why this way?" If yes, register via `/debt-ops:add` immediately — no prompt. This is judgment, not a marker scan: a `TODO`/`FIXME`/`HACK`/`XXX` is the obvious case, but an unmade decision, a stub, a loosened type, or a default picked "for now" all count even with no marker in the diff. Use `payoff_trigger: unknown` if unsure. Announce: `+1 entry: <slug> (drop?)`. Over-register freely; the developer drops with "drop it".

2. When making an architecturally significant change — a data model, public interface, security boundary, release pipeline, or a dep-manifest change that is a major-version bump or a *new* top-level dependency — draft an ADR under `{{ADR_DIR}}/` in Nygard format: a `# NNNN — Title` heading, `**Date:**` and `**Status:**` lines, then Context, Decision, Consequences, Alternatives, Payoff trigger. Create the directory if needed. Only draft an ADR when there are two credible alternatives; if you cannot list two, it is a comment, not an ADR. An ADR with a payoff trigger *is* deliberate debt — when you write one, also call `/debt-ops:add` so the registry entry mirrors the ADR (don't conclude "no markers, no debt").

3. Read entries under `{{REGISTRY_DIR}}/` before changing files they reference.

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
