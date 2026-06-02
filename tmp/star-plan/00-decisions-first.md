# Step 0 — Three decisions to make first

These three calls change everything downstream. Make them before you touch the
README. Each is yours alone — no agent can decide them for you.

---

## Decision 1: Will you claim multi-tool support?

Every top plugin says "works with Claude Code, Cursor, Codex, Gemini CLI…"
even when it mostly runs on one. It multiplies your audience 3–5x.

- **Yes** → you must roadmap Cursor/Codex support for real. Claiming it and
  having it break for Cursor users costs more trust than it earns.
- **No** → stay "Claude Code plugin." Honest, smaller pond.

**Note:** the repo already has a `codex/` adapter path in the plan, so "yes" may
be closer than it looks. Check what actually works before claiming it.

---

## Decision 2: Move the repo to a GitHub org?

Research is clear: org-owned repos (`debt-ops/debt-ops`) get more stars than
personal ones (`bcanfield/agentic-tech-debt`) — a real, free effect.

- **Yes** → create a `debt-ops` org, transfer the repo, keep the old URL as a
  redirect. One afternoon of work.
- **No** → stay put. You lose a free boost but skip the migration.

---

## Decision 3: Spend money on a hackathon prize?

There's an Anthropic hackathon (~3,000 people) around June 12. You could
sponsor a "least debt accrued" prize so debt-ops becomes a recommended tool.

- **Yes** → budget needed, big visibility with the exact right crowd.
- **No** → skip; everything else still works.

---

## When you've decided

Write your answers at the top of `01-foundation.md` so the agents you hand
steps to know the constraints. Then start Step 1.
