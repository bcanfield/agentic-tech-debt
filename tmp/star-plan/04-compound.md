# Days 60–90 — Compound

The launch fades in a week. These steps keep earning stars for months because
they show up in search and get cited.

---

## Step 12 — Publish the data essay (your best long-term asset)

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
> "Help me design the study in tmp/star-plan/04-compound.md Step 12: what
> registry data to collect, how to mirror GitClear's methodology, and what
> charts to produce. Then draft the essay outline."

---

## Step 13 — Get into the "awesome" lists

Open PRs adding debt-ops to:
- `ComposioHQ/awesome-claude-plugins`
- `Chat2AnyLLM/awesome-claude-plugins`

Passive, permanent star drip. Do it early (~Day 30); it compounds.

> **Hand to an agent:**
> "Open PRs adding debt-ops to the two awesome-lists in
> tmp/star-plan/04-compound.md Step 13. Match each list's existing entry format."

---

## Step 14 — Get into "best plugins" roundups

Email the people who publish "Best Claude Code Plugins 2026" roundups
(buildtolaunch.substack.com, firecrawl's blog) for next-edition inclusion.

---

## Step 15 — Anthropic cookbook + conferences (long lead)

- **Cookbook:** Submit a recipe to `anthropics/claude-cookbooks` titled
  something like "Catching AI-introduced tech debt with PostToolUse hooks."
  Anthropic links cookbook recipes from their docs.
- **CFPs:** AI Engineer World's Fair (Wave 2 open), QCon SF, GOTO Chicago all
  take solo-maintainer talks. TechDebt 2026 (academic, ICSE-co-located) is the
  most durable citation.

> **Hand to an agent:**
> "Draft a cookbook recipe outline for anthropics/claude-cookbooks per
> tmp/star-plan/04-compound.md Step 15, and list every open CFP with deadlines."

---

## Step 16 — Weekly metric tweets (ongoing)

Post a weekly one-liner: "debt-ops registry intake this week across N repos: X
TODOs, Y `as any`, Z swallowed catches." Turns your own usage into quotable
data and keeps the project visible between big beats.

---

## Step 17 — Package the portable core as an Agent Skill (reach play)

A second way to ship debt-ops, aimed at surfaces a Claude Code plugin can't
reach: **claude.ai and the Claude API** both support custom Agent Skills.
Getting a skill into a known skills directory is its own distribution channel,
same logic as the plugin marketplace.

**The key fact that shapes this:** Agent Skills are *model-invoked* — they load
only when Claude decides they're relevant. They have **no hooks**, so they can't
fire deterministically on every edit. That means debt-ops splits in two:

- **Portable core (skill-able):** the disciplines, the registry schema, the ADR
  format, and the `add` / `review` / `metrics` scripts. This is essentially what
  already lives in `claude-code/skills/` plus the scripts.
- **Enforcement (not skill-able):** the always-on PostToolUse feedback loop, the
  SessionStart inject, the Stop nag. These stay hooks; a skill can't replace them.

So the skill is a **complementary SKU, not a replacement.** Market it honestly:
"disciplines + registry, on demand" — and point power users to the plugin for
the deterministic enforcement. Don't let the skill version quietly weaken the
"catches debt *as the agent writes it*" promise.

**Format to copy:** `anthropics/skills/tree/main/skills/skill-creator` — a
`SKILL.md` (name + description frontmatter) plus `scripts/`, `references/`,
`assets/`. Your existing Python scripts drop into `scripts/` and run via bash.

**Two things to confirm first:**
1. **Codex is NOT a skills surface** (docs list only claude.ai, Claude API,
   Claude Code). A skill buys you nothing toward Codex — that still needs a
   Codex-native hook layer. Don't conflate the two.
2. This is a **Phase 2 move.** Ship the plugin and the HN launch first; the skill
   is an "also works on claude.ai / in the API" follow-on, not a launch-blocker.

> **Hand to an agent:**
> "Following tmp/star-plan/04-compound.md Step 17, scaffold an Agent Skill that
> packages debt-ops's portable core (disciplines + registry schema + the add/
> review/metrics scripts), using anthropics/skills skill-creator as the format
> reference. Reuse the existing claude-code/skills/*/SKILL.md and scripts/*.py —
> don't rewrite them. Leave the hook-based enforcement out; it can't be a skill.
> Show me the proposed structure before creating files."

---

That's the full 90 days. The single most important thing: **the HN launch is
the center of gravity** — Steps 8–11 reference it, Step 12 references the
numbers it produces. Step 17 is the reach extension once that's landed.
