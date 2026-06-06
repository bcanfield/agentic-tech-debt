# 1 Star a Day: A Cold-Start Playbook for Getting (at Least) One GitHub Star Every Day on an AI Plugin/Skill Repo

## TL;DR
- **Yes, "one star a day" is realistically achievable for a cold-start solo dev building AI developer tooling — but only if you reframe it: the daily action is the goal, not the daily star.** You can guarantee the *input* (one concrete distribution action per day) and engineer a very high *probability* on the output (a star). What you cannot do is mechanically force a star on a given calendar day without cheating. Build a system where directory listings, SEO, and an ecosystem of cross-linked repos produce a passive "drip," then layer daily micro-actions (helpful comments, answering questions, posting tips) that each have a real shot at converting a star that day.
- **The highest-leverage long-term moves are: a README that works like a landing page (GIF demo + one-command install + feature table), getting listed in every relevant AI/MCP directory and awesome-list (the official MCP Registry, Glama, Smithery, PulseMCP, mcp.so, awesome-mcp-servers, Claude Code plugin marketplaces), and building or joining one small community.** These compound. A solo dev (Agrici Daniel) reportedly used exactly this playbook to reach 8,135 stars across 26 cross-linked Claude Code skill repos in 9 months with no funding and no prior audience.
- **Never buy, exchange, or bot stars.** The peer-reviewed StarScout study (He et al., CMU/NC State/Socket, ICSE 2026) identified ~6 million suspected fake stars across 18,617 repos from ~301,000 accounts; 90.42% of flagged repositories had been deleted by January 2025. AI/LLM repos are the single largest non-malicious category of fake-star recipients (~177,000 fake stars), so this niche is under active scrutiny. Fake stars don't convert to users and risk account suspension.

---

## Reality Check / Thesis

**The strict framing ("a day without a star is a failure") is motivationally useful but technically impossible to guarantee through legitimate means.** No honest tactic produces a star on command. So the plan rests on a deliberate reframe with two layers:

1. **Controllable input (guaranteed):** Take one concrete distribution/engagement action every single day. This you *can* do 365 days a year.
2. **Probabilistic output (engineered, not forced):** Stack enough passive drip (directories, SEO, awesome-lists) and active levers (comments, answers, posts) that the *probability* of ≥1 star per day climbs toward near-certainty over time.

Why this is achievable in *this specific niche*: AI developer tooling is riding a once-in-a-decade adoption wave. Per a 2026 developer survey cited in the Agrici Daniel case study, 73% of engineering teams now use AI coding tools daily (up from 41% in 2025). Claude Code, MCP servers, and agent skills are exactly where developer attention is concentrated right now, and the directory/registry ecosystem around them is young — meaning early listings carry outsized weight.

Why it's hard: GitHub hit 1 billion repositories on June 11, 2025, and the overwhelming majority sit at zero stars. The academic baseline (Borges & Valente, *Journal of Systems and Software*, 2018, studying the top-5,000 most-starred repos, where the median repo already had 2,866 stars) found that even among *already-popular* projects, **58.2% follow a "slow growth" pattern** (only ~19.8% new stars/year), 30.0% "moderate" (63.9%/yr), 9.3% "fast" (218.6%/yr), and just **2.3% "viral"** (1,317%/yr). Translation: viral is a rounding error; durable star growth is overwhelmingly a grind of slow, compounding effort. Your edge as a solo dev is not virality — it's consistency and ecosystem compounding.

**Honest expectation:** In the first 2–4 weeks you will likely have multiple zero-star days. That is normal and not failure — it's the cold-start phase before your foundational assets (listings, SEO, content) begin to drip. The daily streak you should actually hold yourself to is the *action* streak, which then makes the star streak emerge.

---

## Part A — The Long-Term Foundational Plan

These are the one-time and ongoing investments that make daily stars *possible* and compounding. Do these first; they convert a random visitor into a star and generate passive drip while you sleep.

### 1. What actually drives a star (build the repo around this)
The definitive data comes from Borges & Valente's survey of 791 developers. The reasons people star (multi-select, so totals exceed 100%):
- **To show appreciation / "I like this project" — 52.5%** ("More than half of the participants answered they starred the repositories because they liked the project." The dominant emotional driver; matters most in a project's earliest days as a feedback loop.)
- **Bookmarking for later retrieval — 51.1%** ("save for later" behavior — your README must make the project look worth returning to)
- **Because they use or used it — 36.7%**
- **Third-party recommendation — 4.6%**

Critically, **73% of developers ("three out of four") consider a repo's star count before using or contributing**, and stars were rated the single most useful popularity metric (83% scored them 3–4 of 4, above forks and watchers). This is the social-proof flywheel: stars beget trust beget stars. It also means the first ~10–50 stars are the hardest and most valuable — they move you out of "zero-star = looks abandoned" territory.

**Design implications:** Make the project (a) instantly likeable (a slick GIF of it working triggers the 52.5% appreciation reflex), (b) obviously worth bookmarking (clear "what this does for me" value prop), and (c) trivially easy to actually use (drives the 36.7%).

### 2. README as a landing page (single biggest conversion lever)
The 30-second test: a developer must understand *what it does, why they should care, and how to install it* within 30 seconds of scanning. Concretely:
- **Animated GIF/video demo at the very top** showing the tool working. The Agrici Daniel case study calls this "the single biggest conversion lever." For a Claude Code skill or MCP server, record a terminal session of it doing something useful.
- **One-command install** near the top (e.g., `claude plugin marketplace add you/your-repo` then `/plugin install`, or `npx -y your-mcp-server`). If install takes 20 steps, you lose ~90% of trial users.
- **Badge row** (stars, license, version, install) for at-a-glance social proof.
- **Scannable feature table**, not a wall of text.
- **A "Related projects" / ecosystem section** linking your other repos (see ecosystem strategy below).
- Add a live **star-history.com chart** embed to signal momentum once you have some.

### 3. GitHub-native SEO and discoverability
- **Topics/tags:** Add relevant topics (`mcp`, `mcp-server`, `claude`, `claude-code`, `ai-agent`, `llm`, `model-context-protocol`, plus your domain). Topics power GitHub's own search and "Explore" recommendations.
- **Repo description + the right keywords** so you surface on GitHub code/repo search for "mcp server [domain]."
- **Social preview image** (Settings → Social preview): a custom OG image makes every shared link look professional on X/LinkedIn/Slack and lifts click-through.
- **A README in the repo root/.github/docs** so GitHub auto-surfaces it.
- GitHub's discovery algorithm rewards **star velocity** (many stars in a short window) — when you launch, concentrate the push into a 24–48h window to try to trigger Trending → "Explore" → "Users also starred" cascade.

### 4. Get listed everywhere (the passive-drip engine)
This is the highest-leverage long-term move for "stars while you sleep." Real, currently-existing targets for an AI plugin/skill/MCP server:

**MCP registries & directories (if your repo is or includes an MCP server):**
- **Official MCP Registry** (`registry.modelcontextprotocol.io`) — the canonical source of truth, community-owned, backed by Anthropic, GitHub, PulseMCP, and Microsoft (launched in preview September 8, 2025). Publish via a `server.json` with GitHub namespace auth (`io.github.you/server`); your package needs validation metadata (e.g., an `mcpName` field in `package.json` for npm). This is the root of trust that downstream marketplaces sync from — list here first. (Note: still in preview, no data-durability guarantees.)
- **Glama** (`glama.ai/mcp/servers`) — ~21,000+ servers, auto-indexes open-source MCP servers from GitHub; **claim your listing** (unclaimed servers explicitly have "limited discoverability"). Indexes at the tool level, with an in-browser inspector.
- **Smithery** (`smithery.ai`) — clean app-store UX, ~7,000+ servers; publish via CLI: `smithery mcp publish "https://your-server.com" -n yourorg/your-server`.
- **PulseMCP** (`pulsemcp.com`) — ~11,840+ servers, hand-reviewed daily.
- **mcp.so** — ~19,700+ community servers; submit via their Submit button or GitHub issues.
- **awesome-mcp-servers** GitHub lists (punkpeye, wong2, appcypher) — submit via PR.

**Claude Code plugin/skill directories (if it's a Claude Code plugin/skill):**
- **Anthropic's official marketplace** (`claude-plugins-official`) — curated, no open application; a quality bar, auto-available in Claude Code.
- **Community marketplace** (`claude-community`) — submit via the plugin directory submission form (external plugins must meet quality/security standards).
- **claudemarketplaces.com** (cites 200,000+ monthly devs), **aitmpl.com**, **ClaudePluginHub** (auto-discovers valid manifests from GitHub; direct submission speeds indexing), **claudecodecommands.directory**.

**General:**
- **sindresorhus/awesome** ecosystem and any niche `awesome-*` list. Read contribution guidelines carefully — they're strict (the main awesome list requires you to comment the word "unicorn" to prove you read the rules, review 4 other open PRs, use a lowercase-slug repo name `awesome-name-of-list`, a title-case heading, and add `awesome`/`awesome-list` topics). A well-placed awesome-list entry can drive a steady drip of stars per month on autopilot — awesome lists themselves accumulate stars because they're treated as GitHub's de facto search engine for "best X."

**Listing cadence:** Don't dump all listings on day one — *space them out* as daily actions (see playbook). Each new listing is both a passive-drip asset AND a guaranteed "I did something today" action.

### 5. The ecosystem / "supply chain" strategy (the solo-dev superpower)
The single most important structural insight from the 8,135-star case study: **build a portfolio of small, cross-linked tools, not one monolith.** Each repo's README links to your others via a "Related Projects" table. A developer who finds one discovers five. Adding repo #N adds fractional discovery to repos #1…#N-1. This is the compounding advantage a solo dev has over a funded team pouring everything into one product. Even 3–5 small related skills cross-linked will outperform one big repo for total stars and for daily-drip reliability. (In that case study, the top 2 repos held ~80% of stars, but the smaller repos *fed* the larger ones via cross-links.)

### 6. Build/join one community from day one
The case study's biggest stated regret was not starting a community sooner. Community = launch velocity (the star-spike that triggers Trending) + evangelists + feedback. You don't need scale: "even a Discord with 50 active users will outperform a Twitter account with 5,000 followers for launch velocity." Options: the MCP community Discord (Frank Fiegel's, linked from awesome-mcp-servers), relevant Skool/Discord groups, or your own tiny Discord seeded from early users.

---

## Part B — 30/60/90-Day Phased Rollout

### Days 1–30: Foundation + first listings (expect lumpy, sometimes-zero days)
- **Week 1:** Ship the README-as-landing-page with GIF + one-command install + topics + social preview image. Publish to npm/PyPI/Docker if applicable (required for MCP Registry). Confirm you're solving a real, painful problem (the flopped repos in the case study "solved problems nobody had").
- **Week 2:** Publish to the **official MCP Registry** (if MCP) + claim **Glama** + publish to **Smithery**. Start the daily playbook. Open a tiny Discord or join the MCP Discord.
- **Week 3:** Submit PRs to 2–3 **awesome-lists** and **mcp.so / PulseMCP**. Submit to Claude Code plugin directories. Record a rough screen-recording demo and put it on YouTube.
- **Week 4:** Write your first "I built X" post for dev.to and cross-post. Begin answering questions in r/mcp, r/ClaudeAI, and relevant Discords daily.
- **Realistic target:** ~10–40 total stars. Goal is crossing the "looks alive" threshold (~10+) so the 73%-check-stars effect starts working for you.

### Days 31–60: First real launch + content engine
- Do your **first "big" launch**: a **Show HN** (mechanics below) timed Tue–Thu, US morning, AND a Reddit "journey" post in r/ClaudeAI or r/mcp. For open-source tools, one daily.dev analysis cites roughly **1.4 GitHub stars per HN upvote within 48h**; an arXiv study of AI-tool launches found the average repo gains ~121 stars in 24h, ~189 by 48h, ~289 in a week — but medians run far lower (most launches are modest; a few go viral and pull averages up).
- Ship a **second related repo** to start the ecosystem cross-link effect.
- Establish a weekly content rhythm (1 post/week: tutorial, comparison, or "I built").
- **Realistic target:** a launch spike (could be 50–500 stars in 48h if it lands; ~20 if it doesn't) plus a higher daily baseline.

### Days 61–90: Compound + repeat
- Ship repo #3; cross-link all of them.
- A second launch is fine **if there's a genuine significant update**. Product Hunt requires waiting ~6 months between launches of the *same* product plus a significant update; HN tolerates reposts only with fresh (non-greyed-out) links and real changes. **Launch *different* repos rather than re-launching the same one.**
- Double down on whatever channel drove the most referral traffic (Insights → Traffic).
- **Realistic target:** a self-sustaining daily drip from listings + SEO + ecosystem, supplemented by daily micro-actions, such that zero-star days become rare.

---

## Part C — The Daily Playbook (your guaranteed lever every day)

**Rule:** Every day, do **at least one** action from this menu. Rotate so you don't burn any single community. Each is sized for a solo dev with a day job.

| # | Daily action | Effort | Expected payoff | Notes |
|---|---|---|---|---|
| 1 | **Answer a real question** in r/mcp, r/ClaudeAI, r/LocalLLaMA, a Discord, or Stack Overflow where your tool genuinely helps; link it only when it's the actual answer | 15–30 min | Medium (0–3 stars, occasional spike) | Highest-trust lever. Value first, link last. Never drop naked links. |
| 2 | **Submit to one new directory/awesome-list** | 10–20 min | Low–medium immediate; high cumulative passive drip | You have dozens of targets; one per day = weeks of guaranteed actions |
| 3 | **Post a small, genuinely useful tip** (a Claude Code/MCP trick) on X/LinkedIn/dev.to with a soft mention of your repo | 15 min | Low–medium | Build-in-public; LinkedIn long-form gets strong algorithmic push for devs |
| 4 | **Ship a small visible improvement** and announce it (changelog, new feature, fix) | 30–60 min | Medium | Repos get a star bump right after releases (Borges & Valente: "acceleration in stars gained after releases"); gives you something to post |
| 5 | **Engage with an adjacent creator** — thoughtful reply/comment on someone bigger in the AI-tooling space | 10 min | Low–medium | Borrowed reach; a high-follower dev's endorsement can drive a sizable spike |
| 6 | **Cross-post** existing content to a new platform (dev.to → Hashnode → Medium → a relevant subreddit) | 10 min | Low–medium | Syndication compounds; same asset, new audience |
| 7 | **Comment helpfully on a relevant GitHub issue/discussion** in a bigger repo where your tool is relevant | 15 min | Low | Devs there are already in "tool evaluation" mindset |
| 8 | **Thank a new stargazer / engage an issue-opener** personally | 5 min | Low (retention/word-of-mouth) | Converts drive-by users into evangelists |

**The "I have 5 minutes" fallback:** If a day is completely swamped, do action #2 (submit to one directory) or #8 (thank a stargazer). Both are near-zero effort and keep the action-streak alive.

**Why these work daily:** They each put your repo in front of *new* people in a context where they're already curious or evaluating tools — the exact conditions that trigger the 52.5% "appreciation" star and the 51.1% "bookmark" star.

---

## Part D — Weekly Cadence (layered on top of dailies)

- **1× per week:** Publish one substantial piece of content — a tutorial, an "I built X because Y" story (personal-story framing reportedly gets ~3× the upvotes of a dry technical description), a comparison post ("X has N stars; here's a free/open alternative" — a documented dev.to format that earns stars), or a demo video. Video converts better than text because people see it working.
- **1× per week:** Ship a meaningful release/update (feeds action #4 and gives the algorithm a velocity bump).
- **1× per week:** Review GitHub **Insights → Traffic** (referrers, popular content) and double down on the best-performing channel.
- **Monthly:** Submit to any newly-discovered directory; consider a bigger launch only when you have a genuinely new repo or major update.

---

## Part E — Launch Mechanics (the periodic big pushes)

### Show HN (Hacker News)
- **Title:** `Show HN: [Name] – [precise, non-marketing description]`. No marketing-speak; HN punishes it instantly. The "I built X to do Y" framing resonates. Good: *"Show HN: A local agent for reviewing pull requests."* Bad: *"We built the best AI agent for developers."*
- **Timing:** Weekday (Tue–Thu) US morning, ~9am–12pm ET / 14:00–17:00 UTC. Treat timing as "be available to reply," not a magic ranking trick. The first 30–60 minutes are critical; a front-page shot typically needs ~30+ upvotes in the first hour.
- **Mechanics:** Use the `Show HN:` prefix (less-competitive /show queue, downvotes disabled during a grace period). Post a detailed first comment ("why I built this, what it solves, the tech, the limitations"). Reply to *every* comment for the first 2–4 hours. Make sure the repo loads fast and install works (a front-page post can drive 5,000–30,000 visitors in 24h). Point HN at your **repo**, not a glossy landing page — for technical products the repo *is* the landing page, and it converts to stars.
- **Never ask for upvotes** or send the direct link for people to vote — HN's voting-ring detection is excellent and will bury or shadowban you. Votes from new/zero-karma accounts are discounted. Only ~2.3% of submissions reach the front page; the median Show HN scores ~2 points.
- **Payoff:** ~1.4 stars/upvote for OSS within 48h; if your first attempt dies, you can email hn@ycombinator.com to request the second-chance pool.

### Reddit
- Best subreddits for this niche: **r/mcp, r/ClaudeAI, r/LocalLLaMA, r/AI_Agents, r/LLMDevs, r/selfhosted** (very tool-friendly; favors open-source), and cautiously **r/programming / r/webdev** (strict, no naked self-promo — substantive technical content only).
- Frame as a **"journey" post** ("I built X because Y — here's what I learned"), GitHub link in the body, not the title. Reddit is hit-or-miss: a well-timed r/ClaudeAI post can drive hundreds of stars; the same post in r/programming can get downvoted into oblivion.

### Product Hunt
- Self-hunt (no real advantage to third-party hunters; **paying hunters is against the rules and can get you banned**, though a recognized hunter can add momentum). First 4 hours of upvotes are crucial (rankings hidden/randomized). You can't ask for upvotes directly — ask people to "check it out / comment." Wait ~6 months + a significant update before re-launching the same product. PH gets ~2.7M monthly visitors (DR 91) and works for dev tools (Cursor, Kilo Code, Supabase have launched there), but skews B2C — good for awareness more than direct conversions.

### Other launch surfaces
- **Lobsters** (invite-only, tech-focused), **dev.to / DEV** (great for dev tools), **Dev Hunt** (OSS-friendly PH alternative), **BetaList, Indie Hackers, r/SideProject**.

---

## Part F — Tracking & Metrics

**Tools (all real, currently-existing):**
- **GitHub Insights → Traffic tab:** unique visitors, page views, clones, and — most importantly — **referring sites** and **popular content**. This tells you which channel actually drives stars. (Only ~14 days of data retained, so check weekly.)
- **star-history.com:** the de-facto star-growth chart; embed it in your README (`[![Star History](https://api.star-history.com/svg?repos=you/repo&type=Date)](...)`) and use it to correlate spikes with specific actions/launches.
- **GitHub CLI** (`gh api repos/OWNER/REPO --jq '{stars, forks, open_issues, fork_ratio, last_push}'`) for quick scripted checks.
- **GitHub API stargazers endpoint** (`GET /repos/{owner}/{repo}/stargazers`) for custom dashboards/alerts; ClawHub/skill download trackers exist for skill ecosystems.

**What to track:**
- **Daily star count** (the headline metric / streak).
- **Star velocity** (stars/week) and whether spikes line up with launches/posts — what GitHub's Trending algorithm rewards.
- **Referrer mix** — concentrate effort on the top 1–2 referrers.
- **Leading indicators that predict next-day stars:** traffic spikes (visitors today → stars tomorrow), content gaining traction, a launch hitting a front page, a new directory listing going live. The case study's rough channel attribution: ~35% organic GitHub discovery, ~25% YouTube demos, ~20% community, ~15% blog, ~5% Reddit/LinkedIn/X (treat as one informed estimate, not validated data).

---

## Part G — Dry Spells & the "or die" Failure Condition (honest handling)

**Reframe the failure condition.** Holding yourself to "a literal star every calendar day or I failed" will, on the inevitable zero-star days, push you toward the one thing that destroys the project: buying stars. So redefine the streak:
- **Primary streak (must hold): the daily ACTION.** One concrete distribution/engagement action every day. 100% in your control.
- **Secondary metric (trend, not daily binary): stars.** Judge it on a **7-day rolling basis**. A week with 5 stars over 7 days is a healthy 1/day average even if two days were zeros.

**When you hit a dry spell:**
1. Check **Insights → Traffic**: is it a *traffic* problem (nobody's visiting → do more top-of-funnel: launches, comments, content) or a *conversion* problem (people visit but don't star → fix the README/GIF/install)?
2. Pull a **higher-leverage lever**: ship a visible release, do a Reddit journey post, or submit to a fresh directory.
3. Lean on the **passive-drip assets** you built — this is exactly why the directory/awesome-list/SEO foundation matters: it produces stars on days you do nothing flashy.
4. Accept that **slow growth is the statistical norm** (58.2% of even top-5,000 repos grow slowly). Dry spells are not failure; they're the baseline you're engineering against.

**Burnout warning:** Posting the same launch repeatedly burns goodwill fast (HN greys out repeat links; subreddits ban repeat self-promo; PH requires 6-month gaps). The *sustainable* daily engine is helpful comments + answering questions + small tips + directory submissions — not repeated launches. Launches are periodic accelerants, not the daily fuel.

---

## Part H — Do NOT Do This (fake/bought/exchanged stars)

**Hard rule: never buy stars, join star-for-star exchange rings/schemes, or use bots.** Non-negotiable, and built into the entire plan's logic.

**Why it's both risky and self-defeating:**
- **GitHub detects and removes them.** The peer-reviewed StarScout study (He et al., CMU/NC State/Socket, ICSE 2026) analyzed 20TB of GitHub data (6.7 billion events, 326 million stars, July 2019–Dec 2024) and found ~6 million suspected fake stars across 18,617 repos from ~301,000 accounts. **90.42% of flagged repositories and 57.07% of flagged accounts had been deleted by January 2025** — a deletion rate ~16× higher than for random repos/accounts. Buying stars can get **your account suspended** under GitHub's Acceptable Use Policies. Detection uses "low-activity" signatures (accounts that star one repo and do nothing else) and "lockstep" clustering (accounts acting in coordination); even Dagster's open-source `star-gazer` tool reproduces this.
- **This niche is a red-flag zone.** AI/LLM repositories are the single largest *non-malicious* category of fake-star recipients (~177,000 fake stars), and by July 2024, 16.66% of *all* repos with ≥50 stars showed fake-star campaigns (up from near-zero before 2022). AI tooling is exactly where detection and community skepticism are highest. Sudden spikes from no-activity accounts, and fork-to-star ratios far below the organic 10–30% baseline, are obvious and documented giveaways.
- **They don't work.** A field experiment ("Social Proof is in the Pudding") bought stars for new Python-package repos and found *no discernible impact* on downloads, forks, PRs, issues, or any real engagement. Fake stars are pure vanity — they don't convert to users, contributors, or the 73%-trust effect (savvy devs now click through stargazer profiles).
- **Reputational and legal exposure.** Public exposure (as in the Dagster investigation, where fake profiles were deleted within 48h of publication) is humiliating in a trust-based community; the FTC's 2024 rule on fake social-influence metrics adds legal risk for commercial actors.
- **It undermines the actual goal.** The goal isn't a number — it's real adoption and credibility. Fake stars give you neither and put the real thing at risk.

**Also avoid the soft-gray-area versions:** don't gate your free tool behind "star to unlock" engagement-farming (explicitly discouraged by community tool authors like n8n-mcp's maintainer), and don't run upvote-rings on HN/Reddit/PH — all are detectable and against platform rules.

---

## Recommendations (staged, concrete next steps)

**This week (do in order):**
1. Rewrite the README as a landing page: GIF demo at top, one-command install, feature table, badge row, related-projects section.
2. Add topics/tags and a custom social-preview image.
3. Publish to the official MCP Registry (if MCP) and/or submit to the relevant Claude Code plugin directory; claim your Glama listing; publish to Smithery.
4. Start the daily-action streak today (begin with action #1 or #2).

**This month:**
5. Submit to one new directory/awesome-list per day until exhausted (this alone is ~2–4 weeks of guaranteed daily actions + passive drip).
6. Ship one related repo and cross-link.
7. Record a screen-recording demo for YouTube.
8. Open/join one small community.

**Days 30–90:**
9. Run a Show HN (Tue–Thu AM ET) and a Reddit journey post.
10. Establish 1 content piece + 1 release per week.
11. Ship repos #2–#3; cross-link the ecosystem.

**Benchmarks that should change your strategy:**
- **<10 total stars after 30 days of daily action:** your *product/problem* may be the issue (solving a non-problem) or your README isn't converting — revisit positioning and the GIF/install, not your distribution volume.
- **Good traffic but low stars** (Insights shows visitors, few stars): conversion problem → fix README/demo/install friction.
- **Low traffic** (Insights shows few visitors): top-of-funnel problem → more launches, comments, content, listings.
- **A channel drives a disproportionate share of referral stars:** double down on it; drop the dead channels.
- **7-day rolling average ≥1 star/day, self-sustaining from passive sources:** you've "won" the cold start — shift effort from daily grinding toward building repo #N and bigger content.

---

## Caveats
- **"One literal star every single day forever" cannot be *guaranteed* by any legitimate tactic** — the honest, sustainable version guarantees the daily *action* and engineers high *probability* on the star, measured on a rolling basis.
- The **8,135-stars-in-9-months case study is a single self-reported example** from a blog (Agrici Daniel) with an obvious incentive to look successful; treat its channel-attribution percentages (35/25/20/15/5) as one informed estimate, not validated data. Its core lessons (README, ecosystem cross-linking, riding the AI wave) are corroborated by the academic literature and other practitioner accounts.
- **Star-per-upvote and "stars per post" figures vary widely** and several come from marketing/DevRel sources with selection bias (successful launches get written up; failures don't). Medians are far below averages — most launches are modest. Some sources quoting high "stars per endorsement" numbers (e.g., 300–800 stars per influencer post) are from vendors that also sell growth services — discount them accordingly.
- The **AI-tooling wave is time-sensitive.** Much of this plan's leverage comes from MCP/Claude Code being hot *right now* and the directory ecosystem being young. If the niche cools or saturates, passive-drip channels weaken and you'll need to re-find a rising wave.
- **MCP Registry is in preview** (no durability guarantees) and the directory landscape changes monthly — re-verify submission URLs/processes when you act.
- **Borges & Valente's growth-pattern and motivation percentages are drawn from the top-5,000 most-starred repos** (median 2,866 stars) — i.e., already-successful projects. A true cold-start repo's odds are harder still, which is *why* the foundational drip-engine and daily-action discipline matter so much. (Motivation percentages are multi-select and sum to >100%; the 73% figure is computed on the 777 of 791 who answered that question.)