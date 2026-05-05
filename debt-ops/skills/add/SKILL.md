---
name: add
description: Register a tech debt entry. Use when you write a TODO/FIXME/HACK/XXX marker that's real debt (a known shortcut, an incomplete case, a fragile assumption), or when the user explicitly asks to record debt. Skip for trivial style nits.
---

# /debt-ops:add — register a debt entry

You are drafting a tech-debt registry entry for the current repository. The
entry is a Markdown file with YAML front-matter under `debt/registry/`.
Entries are addressed **by content** in conversation ("the cancelled-promotion
entry"), never by ID. The numeric `id` exists only for tooling
cross-references (PR trailers like `Debt-Pays-Down: 0042`).

## What you do

1. **Determine the entry's content** from the current context:
   - If you just wrote a `TODO`/`FIXME`/`HACK`/`XXX` marker, use that
     marker's site as the basis.
   - If the user asked you to record something, use what they said.
   - Don't ask a clarifying question for fields you can guess; use
     `unknown` for the ones you can't.

2. **Choose the next id.** Look at existing files in `debt/registry/`
   (lazily create the directory if it doesn't exist). The id is the next
   zero-padded 4-digit number after the highest existing one (start at
   `0001`). Use `ls debt/registry/ 2>/dev/null` to enumerate.

3. **Compose the front-matter** using the schema below. Mark anything you
   can't determine as `unknown` — `payoff_trigger: unknown` is first-class.

4. **Write the file** at `debt/registry/<id>-<slug>.md`, where `<slug>` is
   a short kebab-case description (4–6 words). Create the
   `debt/registry/` directory if it does not exist.

5. **Announce briefly** in chat: one sentence, refer to the entry by content
   ("Registered the cancelled-promotion entry"), and remind the user they
   can tell you to drop it if it's not real debt.

Do not pause for confirmation before writing. The discipline is "write and
announce." If the user pushes back, delete the file.

## Schema

```yaml
---
id: 0042                                  # next zero-padded sequence
title: cancelled-promotion-callback       # kebab-case, matches filename slug
principal: 2d                             # estimated effort to fix (e.g., 2h, 2d, 1w, unknown)
interest: +30min/incident                 # ongoing cost (e.g., "+10%/feature", "unknown")
hotspot: pricing/engine.ts                # path or module the debt lives in
business_capability: checkout             # product area; "unknown" if unclear
payoff_trigger: when promotion engine v2 lands  # event/condition; "unknown" is fine
quadrant: reckless-inadvertent            # see Quadrants below
category: code_quality                    # see Categories below
ai_authored: true                         # true if Claude/Cursor/Copilot wrote it
created: 2026-05-04                       # YYYY-MM-DD, today's date
---

Free-form prose (1–4 short paragraphs):
- The debt: what shortcut was taken, what's incomplete, what assumption is
  fragile.
- Recurrence: how often it bites (or "not yet observed").
- Observed symptoms: bug reports, on-call incidents, slowdowns, surprises.
```

### Quadrants (Fowler)

- `reckless-inadvertent` — didn't know the better way, didn't slow down to
  find out.
- `reckless-deliberate` — knew it was wrong, shipped it anyway.
- `prudent-inadvertent` — only obvious in hindsight.
- `prudent-deliberate` — known shortcut, accepted with eyes open.

### Categories (Google / Jaspan-Green)

`migration`, `documentation`, `testing`, `code_quality`, `dead_code`,
`code_rot`, `expertise`, `release`, `infrastructure`, `planning`.

## Worked example

For a callback in `pricing/engine.ts` that doesn't handle the
cancelled-promotion case, after Claude wrote `// TODO: handle the cancelled-
promotion case later`:

File: `debt/registry/0001-cancelled-promotion-callback.md`

```markdown
---
id: 0001
title: cancelled-promotion-callback
principal: unknown
interest: unknown
hotspot: pricing/engine.ts
business_capability: checkout
payoff_trigger: when promotion engine v2 lands
quadrant: reckless-deliberate
category: code_quality
ai_authored: true
created: 2026-05-04
---

The pricing engine's promotion callback does not handle the cancelled-
promotion case. Today the upstream caller filters cancellations out, but the
filter is informal and could regress. When the promotion engine v2 lands the
callback will need to accept a `Cancelled(reason)` variant explicitly.
```

Announce: "Registered the cancelled-promotion entry. Tell me to drop it if
it's not real debt."

## Edge cases

- **Trivial markers.** A `TODO: rename this var` is a naming preference, not
  debt. Don't register it. If the discipline misfires and you registered one,
  the user will tell you to drop it.
- **Duplicate entries.** Before writing, glance at existing entries (filename
  slugs are descriptive). If one already covers the same shortcut, mention it
  in chat instead of creating a duplicate.
- **No git repo.** This plugin's hard prerequisite is a git repository. If
  there's no `.git/`, write the entry anyway but note in chat that the
  registry travels with the repo.
- **Dropping an entry.** When the user says "drop that one," delete the
  file. Don't archive it; the file's history is in git.
