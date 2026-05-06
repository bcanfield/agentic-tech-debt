---
name: Register tech-debt entry
description: Use when the user invokes /debt-ops:add OR you just deferred work — a TODO/FIXME/HACK/XXX marker, a stub, a loosened type, a bypassed check, a "future"/"later"/"someday" comment, or any decision the code leaves for later. Register the deferral; over-register freely (developer drops with "drop it").
allowed-tools: Write, Bash(date *)
---

# /debt-ops:add — register a tech-debt entry

Write a Markdown file with YAML frontmatter under `debt/registry/`. Lazily create the directory if it doesn't exist (the Write tool creates parent dirs).

## Step 1 — generate a timestamp ID

Run `date +%Y%m%d%H%M%S` in Bash. Use the output verbatim as the entry's `id`. Do NOT scan the directory and pick the next integer — concurrent sessions collide on `0001`. Timestamp IDs are intentionally sortable, globally unique, and treated like commit SHAs (see plan §"v1 implementation requirements" #4).

## Step 2 — pick a slug

A 1–4 word kebab-case label of what the debt is. Examples: `cancelled-promotion-callback`, `legacy-auth-shim`, `unfinished-rate-limiter`. Keep it short — the body carries the context.

## Step 3 — fill the schema

Front-matter, all fields required (use `unknown` if you cannot determine a field):

```yaml
---
id: <YYYYMMDDhhmmss from step 1>
title: <slug from step 2>
principal: <effort to fix, e.g., 2d, 1w, unknown>
interest: <ongoing cost, e.g., +30min/incident, unknown>
hotspot: <path or module, e.g., pricing/engine.ts, unknown>
business_capability: <e.g., checkout, billing, unknown>
payoff_trigger: <concrete trigger, or `unknown`>
quadrant: <one of: reckless-inadvertent, reckless-deliberate, prudent-inadvertent, prudent-deliberate>
category: <one of: migration, documentation, testing, code_quality, dead_code, code_rot, expertise, release, infrastructure, planning>
ai_authored: <true if you (an AI) introduced this, false otherwise>
created: <today's date YYYY-MM-DD>
---
```

Body: free-form prose — what the debt is, why it exists, observed symptoms. Two to five sentences is plenty.

## Step 4 — write the file

Write to `debt/registry/<id>-<slug>.md`.

## Step 5 — announce, one line

`+1 entry: <slug> (drop?)`

If the developer replies "drop it" or "drop", delete the file. Treat dropping as cheap — over-registering is the intended posture.

## Schema notes

- **Quadrant** (Fowler): `reckless-inadvertent` (didn't know better), `reckless-deliberate` (knew, did it anyway), `prudent-inadvertent` (learned afterward), `prudent-deliberate` (deliberate, with a payoff plan).
- **Category** (Google / Jaspan-Green): pick the closest match.
- **payoff_trigger: unknown** is first-class. Don't manufacture a trigger to fill the field — `unknown` ages into stale review at v2 and that's the point.
- **ai_authored: true** is the leading signal for v3's behavioral measurement — be honest.

## Don't

- Don't ask the developer for confirmation before writing. Discipline 1 says "no permission prompt; just do it."
- Don't pick the next integer ID — use the timestamp.
- Don't fill `payoff_trigger` with a guess to seem certain.
