# Research Notes

The evidence behind every step. Six research streams, consolidated. Hand any
section to an agent to dig deeper.

---

## A. Claude Code plugin landscape

What separates breakout plugins from stuck ones:

1. **Tagline names the visible artifact, not the mechanism.** Winners say what
   you'll see (a HUD, a memory store); losers explain hooks.
2. **One launch moment with a visible host.** Every organic breakout traces to
   one human with an audience (an X thread, a shoutout), not README quality.
3. **Multi-tool framing in the description** ("Claude Code, Codex, Cursor…").
4. **A hero visual before any prose.**
5. **Install is `/plugin marketplace add <user>/<repo>`** in the first screen.

**Closest competitor:** `ksimback/tech-debt-skill` (~500★) — same vocabulary,
but it's a one-shot audit with no hook, no GIF, no registry. Plateaued. Your
real-time / write-time angle is the clean differentiator.

**Closest format match:** `hamelsmu/claude-review-loop` (~680★) — same shape
(hook intercepts agent, runs a check). Study its README; Hamel is a friendly
outreach target.

**Biggest threat:** Anthropic's own first-party `code-review` plugin in the
official marketplace. Differentiate on timing (write-time vs review-time) and
the durable registry artifact.

Sources: GitHub `topic:claude-code` search, star-history.com, the official
`anthropics/claude-plugins-official` repo.

---

## B. How adjacent AI dev tools got their first 1,000+ stars

8 comparables (Aider, Continue, Cline, OpenHands, Sweep, Tabby, Plandex, goose).
Patterns:

1. **A front-page Show HN reliably yields ~3–10k stars in ~60 days.**
2. **Riding a bigger wave beats starting one** (OpenHands hit ~19.5k in 30 days
   as "open-source Devin"; Cline launched 10 days after Claude 3.5 Sonnet).
3. **A built-in distribution surface beats Twitter** (Cline grew via the VS Code
   marketplace with no viral thread).
4. **Founder fame is sufficient but not necessary** (goose flat until Jack
   Dorsey tweeted; but non-famous founders still hit 5k+ on artifact quality).
5. **Sustained re-posting > one-shot launch** (Aider re-posted benchmark results
   to HN for a year).
6. **"It builds itself" / dogfood stories go viral.**

Surprises:
- A polished video is NOT the breakout asset for 6 of 8 — text artifacts were.
- First-30-day stars poorly predict 180-day stars. A slow month doesn't kill you.
- Sweep's "AI handles your tech debt" framing (closest to debt-ops) stalled at
  ~7.7k because the delivery surface (PR bot) had high friction. The narrative
  is good; the surface decides retention.

Key source: arXiv 2511.04453 (138 AI-tool HN posts) — ~121 stars at 24h, ~189
at 48h, ~289 at 7 days; posting hour 12–17 UTC is a top predictor; the "Show HN"
tag itself is not significant.

---

## C. The "AI tech debt" conversation

**Vocabulary (use the ones with existing search gravity):**
- "vibe coding" — dominant; the SEO funnel.
- "AI slop" — high volume; good for headlines, not product copy.
- "AI-induced / AI-generated technical debt" — the serious framing; primary.
- "comprehension debt" (Addy Osmani) — rising; cite, don't try to own.
- "the 70%/80% problem" — meme status; reference.
- **Don't coin a new umbrella term.** Own a sub-term like "pre-merge debt
  capture" or "agentic debt registry."

**People with an audience on this exact topic (collaborate, don't cold-pitch):**
- Bill Harding (GitClear) — data partnership / blurb.
- Addy Osmani — guest essay on comprehension debt.
- Simon Willison — gets on his TIL feed via a sharp Show HN.
- Birgitta Böckeler (ThoughtWorks) — Tech Radar "harness" example.
- Kent Beck — podcast angle.
- Gergely Orosz (Pragmatic Engineer) — case-study mention.
- Adam Tornhill (CodeScene) — joint hotspot × registry piece; possible interop.
- Steve Yegge + Gene Kim — authors of the *Vibe Coding* book.

**Timing beats:** GitClear's next annual report ~Q1 2027 (you own the quiet
window until then); TechDebt 2026 + ICSE 2026 "Technical Debt in the AI Era"
panel; QCon AI Boston (June); GitHub Universe (Oct).

**Content angles that fit the discourse:**
1. "The Fowler quadrants, re-drawn for agents."
2. "What we found auditing N AI-generated PRs" (data essay — Step 13).
3. "Comprehension debt has an inverse: an externalized debt registry."

---

## D. What actually causes GitHub stars (peer-reviewed)

- **Org-owned > user-owned**, large effect (Borges et al., ICSME 2016 /
  arXiv:1606.04984). → the org-move decision.
- **Stars are bookmarks, not endorsements**; 73% of devs check star count before
  using; 52% star because they "like" it, 51% to bookmark (Borges & Valente,
  JSS 2018 / arXiv:1811.07643). → make it scannable and obviously useful-now.
- **HN diffusion dominates organic growth** (arXiv:2511.04453).
- **READMEs with lists + images + external links correlate with popularity**
  (Prana et al., 2022 / arXiv:2206.10772).
- **Forks correlate with stars; commit count and contributor count barely do.**
- **Releases trigger star spikes** — each release-please bump is a free promo.
- **Trending = velocity, not totals** — coordinated multi-channel launch days
  are how small repos hit Trending (GitHub community discussion #3083).
- **Top of GitHub is opinionated docs**, not software — only ~9 of top-25 are
  software (Livable Software analysis).

Weak signals people overrate: badge walls (Trockman et al., ICSE 2018),
contributor count for indie projects, repo age / commit volume.

**Opinionated-docs mechanics** (trunk-based-development, Conventional Commits,
microservices.io): a short brandable thesis at a memorable URL; a tool-agnostic
spec + a reference implementation; authority signals (cite research) over
feature lists. debt-ops has all three ingredients but buries them.

---

## E. Distribution channels (the calendar in 02/03/04)

- **HN Show HN** is the center of gravity. Tue 12:00 UTC. Comparable Claude Code
  plugin Show HNs that hit: a destructive-commands plugin (~61 pts), an
  agents-observe dashboard (~77 pts) — both won by answering every comment fast
  with technical detail.
- **X amplifiers (confirmed handles):** @simonw, @bcherny, @MaheshMurag, @swyx,
  @alexalbert__, @HamelHusain. Engage substantively for 2 weeks before pitching.
- **Newsletters:** Pragmatic Engineer (reply to Pulse), TLDR AI, Latent Space
  (guest post), Bytes.dev, JavaScript Weekly (peter@cooperpress.com),
  AlphaSignal, Ben's Bites.
- **Reddit:** r/ClaudeAI, r/LocalLLaMA, r/ExperiencedDevs — staggered, each a
  different format. Skip r/MachineLearning.
- **Cross-posting:** own domain first → dev.to + Hashnode 48h later with
  canonical_url → skip Medium.

---

## F. Anthropic-specific amplification

Ranked paths to official visibility:
1. **Official marketplace** via `clau.de/plugin-directory-submission` — ships
   with every install. Highest lever. Note: do NOT open PRs against
   `anthropics/claude-plugins-community` (auto-closed); use the form.
2. **A recipe in `anthropics/claude-cookbooks`** — Anthropic links these.
3. **A plugin spotlight on the Anthropic news blog** — via DevRel (Alex Albert),
   with a 20-second demo gif.
4. **Featured in Claude Code release notes** — ship a feature that pairs with
   whatever the team shipped that week.

Anthropic humans (one thoughtful public @mention beats five DMs):
- Boris Cherny (@bcherny) — Claude Code creator; lead with hook mechanism.
- Cat Wu (@_catwu) — Head of Product; show metrics + the trust contract.
- Alex Albert (@alexalbert__) — DevRel; DRI for blog spotlights.
- Sid Bidasaria — founding engineer; engage via a substantive GitHub issue.

Orbit boosters: Hamel Husain (highest-yield), Simon Willison, swyx/Latent Space,
Dan Ávila & Seth Hobson (marketplace curators already in the Anthropic blog).

Calendar: Code with Claude Tokyo (~June 10); lablab.ai Anthropic hackathon
(~June 12, ~3,000 people — the prize-sponsor option); biweekly Claude Code
releases (ship a compatibility release within 48h to land in the changelog).

**Anti-patterns:** don't PR the community mirror (auto-closed); don't cold-DM
multiple Anthropic employees the same week (they compare notes); don't spam the
Discord.

---

## What only you can do (not researched — needs you)

1. **Validate the persona.** Interview 5–10 "solo brownfield senior IC" devs.
   Does the GitClear stat resonate or feel academic? Where do they hang out?
2. **Survey your existing stargazers** — how did they find debt-ops, what made
   them star.

These determine whether the whole plan aims at the right people. If the persona
is wrong, revisit before executing.
