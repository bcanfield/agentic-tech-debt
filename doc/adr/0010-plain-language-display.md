# 0010 — Plain language at the display layer

**Date:** 2026-05-27
**Status:** Accepted

## Context

The registry schema uses a research taxonomy — Fowler's debt quadrant (`reckless-inadvertent`, `prudent-deliberate`, …) and the Google/Jaspan categories (`code_rot`, `code_quality`, …). These earn their place behind the scenes: the quadrant drives `review.py`'s ranking weights and the categories ground the schema in published work. But the terms are academic — a developer reading `… · prudent-deliberate · churn=4` in the review output has no idea what it means, and neither do their teammates. The ADR-0009 default change made this obvious when `/debt-ops:review` started surfacing the raw quadrant prominently.

## Decision

Store the canonical taxonomy; translate to plain language at every surface the developer reads. `review.py` keeps `quadrant`/`category` in the frontmatter and in its scoring, but its printed output maps the quadrant through a `QUADRANT_PLAIN` table (`prudent-deliberate` → "planned tradeoff", `reckless-deliberate` → "knowing shortcut", etc.) and renders `churn=N` as "N edits since logged". The `review` skill instructs Claude to describe entries in plain words and never voice the raw taxonomy to the user. Docs describe the ranking as "change frequency and risk" rather than "churn × Fowler quadrant".

## What this means for you

- The review output reads in plain English; you never need to learn the 2×2.
- The frontmatter still says `quadrant: prudent-deliberate` — that's the machine field powering the ranking and keeping the schema research-grounded. If you open a raw entry file you'll see it; the body prose explains the debt plainly.
- Ranking is unchanged — only the labels did.

## Alternatives we ruled out

- **Rename the schema fields to plain values.** Breaks the ranking weights' canonical keys, severs the research grounding, and churns every existing entry. The split (canonical storage, plain display) costs one small map.
- **Collapse the quadrant to a single risk word (high/medium/low).** Loses the deliberate-vs-accidental nuance and conflates with priority — which is already the rank order, so a "low risk" item can sit at #1 by churn and read oddly.
- **Show both (plain + canonical in parens).** Still puts the jargon on screen, which is the thing we're removing.

## When to revisit

- If we add a user-facing surface that shows `category`, give it the same treatment (a `CATEGORY_PLAIN` map).
- If users ask to see the canonical term, add an opt-in `--raw` flag to `review.py` rather than putting jargon back in the default output.
