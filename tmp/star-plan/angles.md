# Angles & Positioning — how we propose debt-ops to devs

The single source of truth for how we describe the product. Every README line,
HN post, Reddit thread, and pitch pulls its framing from here. Vary the *format*
per channel; never vary the *angle*. Grounded in `research-notes.md`.

---

## The pitch (the honest spine)

> We read two decades of tech-debt research, distilled it into one opinionated
> AI plugin, and validated it across dozens of real codebases.

That's the whole story. It's true, it's plain, and it's credibility no
competitor has. Lead with it everywhere.

**What it does, in one line:**
Catches AI-introduced tech debt at write-time — the moment your agent writes it,
not at PR review.

Lead with the spine (credibility), land on the one-liner (the differentiator).
Everything below just supports these two sentences. Keep it plain — no hype, no
slop, no wall of adjectives.

---

## Rule 1 — Sell the artifact, not the mechanism

Research is blunt: people star what they can screenshot. Winners name the
*visible thing*; losers explain their hooks.

- **Lead with:** the debt registry / paydown queue ranked by churn. That's the
  artifact. Show it.
- **Don't lead with:** PostToolUse hooks, SessionStart inject, the Stop nag.
  Mechanism is the answer to "how does it work?", saved for the engineering
  crowd (HN replies, Boris, Latent Space) — not the opening pitch.

---

## Rule 2 — The four moats (why us, not the alternatives)

1. **Write-time, not review-time.** SonarQube, Sourcery, CodeRabbit, Sweep all
   act at or after the PR. debt-ops runs *inside the agent loop, as the code is
   written.* This is the one claim none of them can structurally make. It is the
   headline differentiator.
2. **A durable registry, not a one-shot audit.** The closest competitor
   (`ksimback/tech-debt-skill`) audits once and forgets. We turn every deferral
   into a persistent, ranked paydown queue. The registry is the asset that keeps
   paying off.
3. **Graceful, not punitive.** debt-ops surfaces and suggests; it doesn't block
   your PR or nag. The registry lives in your repo and travels with it, and
   `review` ranks paydown by behavioral hotspots (how active a file is) so you
   fix what matters, not vanity nits. Straight from the research's "improvement,
   not perfection" tenet.
4. **Multi-surface, one schema.** Claude Code, Codex, and Copilot CLIs, plus a
   portable Agent Skill for claude.ai and the Claude API. Most rivals are
   single-surface.
   - **Honesty guardrail:** write-time *enforcement* is CLI-only. The Agent
     Skill is "disciplines + registry on demand" — it can't fire on every edit
     (skills have no hooks). Never let "works everywhere" dilute the
     "catches debt as the agent writes it" promise.

---

## Rule 3 — Vocabulary (search gravity + credibility)

**Use** (terms that already have an audience):
- *"AI-induced / AI-generated technical debt"* — primary, serious framing.
- *"vibe coding"* — the SEO funnel; use in titles/tags where it reads naturally.
- *Cite* "comprehension debt" (Addy Osmani) and "the 70% problem" — reference
  them, don't try to own them.

**Own a narrow sub-term** (don't coin a new umbrella term — that fails):
- *"write-time debt capture"* / *"agentic debt registry"* / *"pre-merge debt
  capture."*

**Avoid in product copy:**
- *"AI slop"* — fine for a headline, wrong for the pitch.
- Any invented umbrella term, and any claim of Cursor support (we don't ship it).

---

## Rule 4 — Proof points (use the same three everywhere)

- **GitClear** (211M lines): refactoring fell from ~25% of changes to under
  10%, and copy-pasted code overtook moved code for the first time. The pain,
  quantified. Recurring hook. (Skip the "$1.5T by 2027 / 3× faster" figures —
  our own docs flag them as un-credible vendor projections.)
- **The in-repo registry** — entries you can open, diff, and screenshot.
- **One real catch** — the GIF of an `as any` getting registered at write-time.

---

## Rule 5 — Same product, different door (per-audience angle)

- **Solo brownfield senior IC** (primary persona): *"Every `TODO`, `as any`, and
  `.skip` your agent writes, turned into a queue you'll actually pay down."*
  War-story framing. → README, r/ExperiencedDevs.
- **Eng leaders / the GitClear crowd:** the org-level debt trend + the data. →
  LinkedIn, the data essay, Pragmatic Engineer.
- **Claude / agent-tooling crowd:** the hook architecture + the multi-surface
  schema. → HN engineering replies, Latent Space, Boris/Anthropic outreach.
- **AI-skeptics ("AI makes a mess"):** *"it catches the mess as it's made."*
  Write-time. → r/programming (with the data essay), InfoQ/The New Stack.

---

## Rule 6 — Objection handling (pre-baked, see Step 5)

- *"How is this different from SonarQube / Sourcery / CodeRabbit?"* →
  write-time, inside the agent loop, not PR-time.
- *"Won't the agent just bypass it with `bash tmp.sh`?"* → be honest about the
  threat model; link the ADR.
- *"Why a plugin instead of a sandbox?"* → the debt is created in the loop, so
  catch it there; one-command install, no daemon, the registry is just files in
  your repo.

---

## What NOT to claim

- We **capture and rank** debt; we don't claim to **stop** it. Overclaiming
  kills trust (Sweep's narrative was right, the surface friction stalled it).
- The Agent Skill does **not** enforce at write-time — only the CLI plugins do.
- Cursor/Gemini/Windsurf/opencode are supported **via the portable Agent Skill**,
  not a native plugin. Say that, don't imply a deeper integration than ships.
- debt-ops is **graceful/passive** — don't describe it as a blocker, gate, or a
  "Refuse > Flag > Fix" tool. That's a different product.
- Use the **real** validation number. If it's ~30 repos, say "dozens" or the
  actual count — never round up to "hundreds." The honesty is the point.
