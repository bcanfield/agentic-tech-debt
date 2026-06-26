# 0022 — Article visual density: an image every two paragraphs, three mandatory anchors

**Date:** 2026-06-26
**Status:** Accepted

## Context

The write-article skill required exactly two committed body images (one diagram, one meme) and
enforced spacing only as "no prose run exceeds ~40% of the body" (`meme_check.py`, `MAX_GAP_FRAC`).
On a 1,000–1,900-word article that still leaves long gray runs a skimmer bounces off before the
prose converts. The author asked for a harder floor: never more than two prose paragraphs in a row
without a visual, and one more mandatory render.

This collides with the skill's own anti-AI research, which treats visuals as *scarce on purpose* —
"decoration is the tell," "if every section has a table they become wallpaper," "every visual
carries content the prose doesn't." Forcing an image every two paragraphs, read naively, manufactures
exactly the decoration the rest of the skill spends pages avoiding. So the decision is as much about
*what defuses the decoration risk* as about the density number.

## Decision

1. **Density floor, deterministic.** `meme_check.py` now fails on any run of more than two
   consecutive prose paragraphs with no visual between them, and on fewer than three committed body
   images (one of which must be a `*.diagram.*`, one the meme). The old `MAX_GAP_FRAC` run-fraction
   check is replaced by the paragraph-run rule.
2. **A visual break is broad; the required images are narrow.** For the run rule, a break is a
   committed image, fenced code block, table, blockquote, or heading. But the article must carry
   three *images* regardless — in incident/data/essay pieces (almost no code) an image is the only
   thing that breaks a run, so the rule lands as "an image every two paragraphs" there; playbooks
   lean on their native code/tables, which is why those count.
3. **The third anchor is free** (stat-card / second diagram / quote card), same build pipeline as the
   diagram, same "carries content or it's cut" bar. Only `.diagram.` and `.meme.` are reserved names.
4. **Decoration is defused by a paired constraint, in prose:** every gap-filler carries content the
   prose doesn't, and the sanctioned fix for a too-long run is *either* a content-bearing render *or*
   cutting prose until the run closes — never a decorative image. This makes the density rule pull in
   the same direction as ADR's sibling concision guidance ("Cut to the key points").

## Consequences

- Skimmable pages by construction; the gate, not the eye, catches walls of gray.
- The seven existing articles fail the new gate (two anchors, long runs) — they need a retrofit pass
  to add a third anchor and break runs. Tracked as debt, not done in this change.
- A real risk we are accepting: heavier visual cadence *can* read as AI dressing, the exact tell the
  skill protects against. The content-bearing constraint and the fresh-agent review are the guard;
  the payoff trigger below is when to revisit if the guard proves insufficient.
- `meme_check.py` lives only in the write-article skill (not one of the duplicated adapter scripts),
  so no cross-adapter sync is owed.

## Alternatives

- **Any visual break counts (tables/code/quotes equal to images).** Easier to satisfy without new
  renders, but the author explicitly wanted *images* between paragraphs, and prose-heavy pieces would
  pass on tables alone — defeating the intent. Rejected as the gate's framing; kept only as the
  playbook carve-out (where code is the native visual).
- **Rendered-PNG-only gate, uniformly.** The strict literal reading, but with no machine-readable
  pillar in frontmatter the gate can't carve out playbooks, so it would false-fail the one shape
  legitimately broken by code blocks. Rejected; the broad-break gate plus a prose "prefer rendered
  images" default reaches the same outcome in prose pieces without the false failures.
- **Keep two anchors, just tighten the run fraction.** Less build work, but doesn't deliver the
  "one more render" the author asked for and leaves the gray-run problem on longer pieces.

## Payoff trigger

Articles start reading as over-decorated / AI-dressed, or engagement on image-dense pieces drops
versus the leaner earlier ones — revisit the density floor (relax to three paragraphs, or let
content-bearing tables fully substitute for the third image).
