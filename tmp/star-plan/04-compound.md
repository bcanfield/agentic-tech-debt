# Compound — what keeps earning stars

The launch fades in a week. These steps keep earning stars for months because
they show up in search and get cited. Framing still comes from `angles.md`.

---

## Step 13 — Publish the data essay (your best long-term asset)

**"The GitClear numbers, a year later."** Re-run GitClear's method on your own
repo + 5–10 volunteer OSS repos using debt-ops registry data. Real numbers
nobody else has.

**Do this:**
- Publish on your own domain first.
- 48 hours later, cross-post to dev.to and Hashnode with `canonical_url` set
  back to the original (so you don't split SEO). Skip Medium.
- Submit to HN as a **blog post** (a different URL than the launch).

Timing bonus: GitClear's next annual report isn't due until ~Q1 2027, so the
back half of 2026 is your window to be the source journalists cite.

> **Hand to an agent:**
> "Help me design the study in tmp/star-plan/04-compound.md Step 13: what
> registry data to collect, how to mirror GitClear's methodology, and what
> charts to produce. Then draft the essay outline, framed per angles.md."

---

## Step 14 — Get into the "awesome" lists

Open PRs adding debt-ops to:
- `hesreallyhim/awesome-claude-code` (the big one)
- `ComposioHQ/awesome-claude-plugins`
- `Chat2AnyLLM/awesome-claude-plugins`
- plus `awesome-ai-coding-tools`, `awesome-devtools`, `awesome-code-review`, and
  (for the Copilot surface) `github/awesome-copilot`-type lists.

Passive, permanent star drip. Do it early; it compounds.

> **Hand to an agent:**
> "Open PRs adding debt-ops to the awesome-lists in tmp/star-plan/04-compound.md
> Step 14. Match each list's existing entry format; description per angles.md."

---

## Step 15 — Roundups & press

- Email the people who publish "Best Claude Code Plugins 2026" roundups
  (buildtolaunch.substack.com, firecrawl's blog) for next-edition inclusion.
- **Press:** pitch **The New Stack** and **InfoQ** — both cover AI-meets-tech-debt.
  Pitch the data essay (Step 13), not the launch.

---

## Step 16 — Anthropic cookbook + conferences (long lead)

- **Cookbook:** Submit a recipe to `anthropics/claude-cookbooks` titled
  something like "Catching AI-introduced tech debt with PostToolUse hooks."
  Anthropic links cookbook recipes from their docs.
- **CFPs:** AI Engineer World's Fair (Wave 2 open), QCon SF, GOTO Chicago all
  take solo-maintainer talks. TechDebt 2026 (academic, ICSE-co-located) is the
  most durable citation.

> **Hand to an agent:**
> "Draft a cookbook recipe outline for anthropics/claude-cookbooks per
> tmp/star-plan/04-compound.md Step 16, and list every open CFP with deadlines."

---

## Step 17 — Weekly metric posts (ongoing)

Post a weekly one-liner: "debt-ops registry intake this week across N repos: X
TODOs, Y `as any`, Z swallowed catches." Turns your own usage into quotable data
and keeps the project visible between big beats. Post it on your social home
(Step 12).

---

## Step 18 — Agent Skill + native distribution surfaces (reach play)

Beyond the Claude Code marketplace (Step 3), you ship to surfaces a single
plugin can't reach. Claim each native shelf:

- **Agent Skill** for **claude.ai and the Claude API** — both support custom
  skills. Package the **portable core** (disciplines, registry schema, ADR
  format, and the `add`/`review`/`metrics` scripts — essentially what's already
  in `claude-code/skills/` + scripts). The **enforcement** (PostToolUse loop,
  SessionStart inject, Stop nag) stays a hook; a skill can't replace it.
  - Market it honestly: "disciplines + registry, on demand" — and point power
    users to the plugin for the deterministic write-time enforcement. Don't let
    the skill weaken the "catches debt as the agent writes it" promise.
  - Format to copy: `anthropics/skills/tree/main/skills/skill-creator`.
- **Skill directories** — get the skill listed wherever the `npx skills` CLI and
  other skills registries pull from. Its own distribution channel.
- **Codex / Copilot native listings** — confirm whether each CLI has any
  plugin/extension directory you can claim. A native shelf beats social.

**Two facts that shape this:**
1. **Codex is NOT a skills surface** (docs list only claude.ai, Claude API,
   Claude Code). A skill buys nothing toward Codex — that stays a Codex-native
   hook layer. Don't conflate them.
2. This is a **follow-on**, not a launch-blocker. Ship the plugin + HN launch
   first; the skill is the "also works on claude.ai / in the API" extension.

> **Hand to an agent:**
> "Following tmp/star-plan/04-compound.md Step 18, scaffold an Agent Skill that
> packages debt-ops's portable core, using anthropics/skills skill-creator as
> the format reference. Reuse the existing claude-code/skills/*/SKILL.md and
> scripts/*.py — don't rewrite them. Leave hook-based enforcement out. Then list
> the skill directories and any Codex/Copilot listings we can submit to. Show me
> the proposed structure before creating files."

---

The single most important thing: **the HN launch is the center of gravity** —
Steps 7–12 reference it, Step 13 references the numbers it produces. Step 18 is
the reach extension once that's landed. But the thing to get right *first* is
`angles.md` — every step above only works if the angle is correct.
