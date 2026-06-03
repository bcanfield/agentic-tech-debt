# Foundation — fix the repo first

Fix the repo before anyone looks at it. No external posting yet. When a launch
sends 1,000 people to your README, it needs to convert them in 10 seconds.

> **Before you write a word of copy, read `angles.md`.** It's the source of
> truth for how we propose debt-ops to devs — the README and every step below
> pull their framing from it.

> Decision-0 answers (locked):
> - Multi-tool: **YES** — Claude Code, Codex, Copilot CLIs + a portable Agent
>   Skill (claude.ai / Claude API). Not Cursor.
> - Org move: **NO** — staying on `bcanfield/agentic-tech-debt`; all links use it.
> - Hackathon: **NO**.

---

## Step 1 — Rewrite the README top

**Do this:**
- Put the demo GIF **above** the badges (right now badges come first).
- Add a stat block in the first screenful using the GitClear numbers:
  refactoring fell from ~25% to under 10%, copy-pasted code up 48%.
- Keep the install command in the first 5 lines.
- Cut to 2 badges max (license + plugin). Badge walls don't help.
- Add a short "Who this is for / who it's not for" section.
- Add a tiny table of contents.

**New tagline — pick one:**
- A (headline): *"Catches AI-introduced tech debt at write-time, not at PR review."*
- B (sub-line): *"Every `TODO`, `as any`, and `.skip` your AI agent writes — turned into a paydown queue ranked by churn."*
- C (marketplace description): *"A Claude Code, Cursor, and Codex plugin: turn agent shortcuts into a debt registry your team actually pays down."*

Recommended: A as headline, B under the GIF, C in `marketplace.json`.

> **Hand to an agent:**
> "Rewrite /Users/bcanfield/Documents/debt/README.md following
> tmp/star-plan/01-foundation.md Step 1. Keep our existing voice (concise, no
> em-dashes, no AI slop per CLAUDE.md). Show me a diff before saving."

---

## Step 2 — Rebuild the demo GIF

**Do this:** Make `demo/debt-ops.gif` show ONE real catch (e.g. Claude writing
`as any`, debt-ops registering it) within **8 seconds**. The current concept
GIF is abstract; people star what they can see happening.

> **Hand to an agent:**
> "Look at demo/scene.bash and demo/debt-ops.tape. Propose a tighter scene that
> shows one `as any` getting caught in under 8 seconds. Don't regenerate yet —
> show me the new tape first."

---

## Step 3 — Submit to Anthropic's plugin marketplace

**This is the single biggest lever. Do it on Day 1 — it's async.**

**Do this:**
- Go to the submission form: `clau.de/plugin-directory-submission`
- Pick a category where you'd be the only debt/quality tool.
- Make `marketplace.json` / `plugin.json` match the shape of an existing
  community entry (e.g. context7).

> **Hand to an agent:**
> "Research the current submission requirements at clau.de/plugin-directory-submission
> and the format of accepted entries in anthropics/claude-plugins-official.
> Tell me exactly what fields debt-ops needs and whether our manifest matches."

---

## Step 4 — Make the repo look alive

**Do this:**
- Ship 2 small releases (`feat:` / `fix:`) so the commit log isn't empty.
- Open 3 "good first issue" tickets.
- (If Decision 2 = yes) move to the org now.

---

## Step 5 — Pre-write your HN comment replies

You'll get the same 3 questions on launch day. Write answers now so you can
reply within minutes (fast replies are what separate hits from flops).

1. "How is this different from SonarQube / Sourcery / CodeRabbit?"
   → You run at **write-time**, inside the agent loop, not at PR time.
2. "Won't Claude just bypass it by running `bash tmp.sh`?"
   → Be honest about the threat model; link an ADR.
3. "Why a plugin instead of a sandbox?"
   → The Refuse > Flag > Fix contract; zero install footprint.

> **Hand to an agent:**
> "Draft 3 HN comment replies for the questions in tmp/star-plan/01-foundation.md
> Step 5. Ground them in our docs/ research. Keep each under 120 words, plain and
> non-defensive."

---

When all 5 steps are done, go to `02-launch.md`.
