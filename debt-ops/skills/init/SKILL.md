---
name: init
description: Writes the debt-ops disciplines and the project's detected quality commands into AGENTS.md or CLAUDE.md so the team and other AI tools share one source of truth. Opt-in; only runs when the user explicitly asks.
disable-model-invocation: true
allowed-tools: Read, Edit, Write, Glob, Bash(ls:*)
---

# /debt-ops:init — write disciplines and commands into the charter

This skill is **opt-in**. Run it only when the user explicitly asks (e.g.,
"set up debt-ops for the team", "/debt-ops:init"). Do not run it
proactively — solo users are happy with the SessionStart inject.

The plugin works fully on enable without this step. `/debt-ops:init` exists
so a team can commit the conventions to the repo, where they survive plugin
updates and travel to other AI tools (Cursor, Aider, Codex) that read
`AGENTS.md`.

## What you do

1. **Find or pick the charter.** Look for `AGENTS.md`, then `CLAUDE.md` in
   the repo root.
   - If both exist: prefer `AGENTS.md`.
   - If neither exists: tell the user that Claude Code's built-in `/init`
     creates the charter and they should run that first. Do **not** create
     a charter from scratch yourself; that overlaps with `/init`.

2. **Detect the project's quality commands** if not already cached. Check
   `${CLAUDE_PLUGIN_DATA}/feedback.list` first — if it has commands, reuse
   them. Otherwise scan project files (`package.json`, `Cargo.toml`,
   `pyproject.toml`, `Makefile`, `go.mod`, etc.) and propose a small set:
   typically type-check + lint + a fast test pass. Each must be
   non-interactive, self-contained, idempotent, and quiet on success.

3. **Append a `## Tech debt operations` section** to the charter. If the
   section already exists, replace it (preserve everything else in the
   file). The section must contain:

   - The four disciplines (verbatim from the template below).
   - A `<!-- debt-ops:feedback -->` marker block listing the quality
     commands, one per line, as a bulleted list inside a fenced block. The
     PostToolUse hook reads commands from this block when present, so the
     marker comments must stay intact.

4. **Write the cache too.** Mirror the commands to
   `${CLAUDE_PLUGIN_DATA}/feedback.list`, one per line, so the hook still
   has a source even if the marker block is later edited or deleted.

5. **Announce.** One sentence: "Wrote the debt-ops section to `AGENTS.md`.
   Commit it to share with the team." Do not commit the change yourself.

## Section template

Insert this section verbatim, substituting the detected commands into the
marker block. The outer fence uses **four backticks** so the inner
triple-backtick commands block nests correctly — preserve that when
copying.

````markdown
## Tech debt operations

This section is managed by the `debt-ops` Claude Code plugin. The marker
block below is read by the plugin's PostToolUse hook; keep the
`<!-- debt-ops:feedback -->` comments intact.

### Disciplines

1. **Auto-register debt.** When you take an expedient choice — a known
   shortcut, an incomplete case, a fragile assumption, a deferred
   refactor — register it via `/debt-ops:add` immediately. This includes
   any `TODO`, `FIXME`, `HACK`, or `XXX` marker you write that represents
   real debt, but is not limited to markers: a silent shortcut still
   earns an entry. No permission prompt; just register and announce
   briefly. Use `payoff_trigger: unknown` if unsure. Trivial nits (style,
   naming preferences) don't earn an entry; use judgment.

2. **Draft ADRs for architectural changes.** When making an
   architecturally significant change (data model, public interface,
   dependency manifest, security boundary, release pipeline), draft an
   ADR under `doc/adr/` in Nygard format (Context, Decision,
   Consequences, Alternatives, Payoff trigger). Create the directory if
   needed.

3. **Read the registry and ADR index first.** Before changing files in
   an area covered by entries under `debt/registry/` or ADRs under
   `doc/adr/`, read the relevant entries.

4. **Refer by content, not ID.** In conversation, refer to debt entries
   and ADRs by what they're about, not by numeric ID. IDs are for tooling
   cross-references like commit SHAs.

### Quality commands (read by the PostToolUse hook)

<!-- debt-ops:feedback -->
```
<DETECTED-COMMAND-1>
<DETECTED-COMMAND-2>
<DETECTED-COMMAND-3>
```
<!-- /debt-ops:feedback -->
````

## Edge cases

- **Existing `## Tech debt operations` section.** Replace it wholesale.
  Preserve everything before and after. Don't try to merge.
- **Charter has been customized.** Append the section at the end of the
  file with a single blank line separator; never reorder existing content.
- **No detected commands.** Write the section anyway with an empty marker
  block (`<!-- debt-ops:feedback -->` immediately followed by
  `<!-- /debt-ops:feedback -->`) and tell the user to add commands manually.
- **`AGENTS.md` is large.** Don't bloat it. The disciplines block is
  ~30 lines; the marker block is short. If the charter is already heavy,
  point that out — Pillar 6 cares about charter size budgets — but still
  append the section.
- **The user runs `/debt-ops:init` again later.** Treat it as idempotent:
  re-run safely overwrites the section in place.
