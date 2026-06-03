# Step 0 — Three decisions to make first

These three calls change everything downstream. Make them before you touch the
README. Each is yours alone — no agent can decide them for you.

---

## Decision 1: Will you claim multi-tool support? → RESOLVED: YES

Every top plugin says "works with Claude Code, Codex, Cursor…" even when it
mostly runs on one. It multiplies your audience 3–5x.

**Decided:** claim **Claude Code, Codex, and Copilot** (all three adapters
already ship in the repo) plus a **portable Agent Skill** for claude.ai and the
Claude API. **Not Cursor** — we don't ship it; claiming it would cost more trust
than it earns. This claim is honest because every surface actually exists.

---

## Decision 2: Move the repo to a GitHub org? → RESOLVED: NO

Research is clear: org-owned repos get more stars than personal ones — a real,
free effect we're choosing to forgo.

**Decided:** stay on `bcanfield/agentic-tech-debt`. Skip the migration; every
link in the README, HN post, and awesome-list PRs uses the current URL.

---

## Decision 3: Spend money on a hackathon prize? → RESOLVED: NO

There was an Anthropic hackathon (~3,000 people) you could have sponsored a
"least debt accrued" prize at.

**Decided:** no hackathon spend. Everything else in the plan still works.

---

## When you've decided

Write your answers at the top of `01-foundation.md` so the agents you hand
steps to know the constraints. Then start Step 1.
