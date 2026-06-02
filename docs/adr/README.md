# Architecture Decision Records

Short notes on decisions that shape how this plugin behaves. Each one is written for a future reader who's about to change the same area and wants to know "wait — why was it done this way?"

## Format

Every ADR has five short sections, written in plain language:

- **Context** — what came up, what prompted the decision.
- **Decision** — what we picked.
- **What this means for you** — the user-facing impact (what changes, what doesn't, what to expect).
- **Alternatives we ruled out** — and why each was worse.
- **When to revisit** — the trigger that should pull this decision back open.

These are this repo's friendlier aliases for classic [Nygard](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions) sections. The plugin *ships* the classic names to user repos — Context, Decision, **Consequences** (≈ what this means for you), Alternatives, **Payoff trigger** (≈ when to revisit) — so an ADR generated in any repo is recognizable. Same five sections, same intent; only the two labels differ.

## House style

Keep it tight. 2–3 sentences per section is plenty. If a section is longer than a paragraph, you're probably writing the implementation, not the decision.

Numbered sequentially: `0001-short-title.md`, `0002-short-title.md`, etc.
