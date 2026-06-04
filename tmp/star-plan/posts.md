# The posts (ready to send)

All grounded in the real product (root README + docs/) and `angles.md`. Plain
voice, no slop. Swap `https://github.com/bcanfield/agentic-tech-debt` for the repo/demo URL before posting. Use the real
validation count wherever it says "dozens."

---

## HN — Show HN

**URL field:** `https://github.com/bcanfield/agentic-tech-debt`

**Titles (pick one):**
- `Show HN: Debt-Ops – catch AI-written tech debt as the agent writes it`
- `Show HN: Debt-Ops – 20 years of tech-debt research, distilled into an agent plugin`

**Body (first comment / text; repo is in the URL field, so no link here):**

AI writes code faster than you can review it, and the shortcuts pile up
off-screen. GitClear's study of 211M lines shows it: refactoring fell from about
25% of changes to under 10%, and duplicated code kept climbing.

I read about 20 years of tech-debt research (Fowler's quadrants, the Dagstuhl
definition, ADRs, behavioral hotspots), distilled what held up into nine pillars,
and wired them into the agent loop. That's debt-ops.

It works at write-time. When your agent casts something to `as any`, leaves a
TODO, or punts on a decision, debt-ops logs it to a folder in your repo as it
happens. `review` ranks what to clean up by how active each file is, so you fix
hotspots, not vanity nits. It's passive, not a gate, and it doesn't block you.

Works in Claude Code, Codex, and Copilot, plus a portable skill for other agents.
One command to install, needs a git repo and Python. I've run it across dozens of
codebases.

Happy to get into the hook design or the ranking.

---

## HN — pre-written comment replies

**"How is this different from SonarQube / Sourcery / CodeRabbit?"**

Those run at PR time or on a schedule, after the code exists. debt-ops runs
inside the agent loop, so the shortcut gets logged the moment it's written, with
the reasoning still fresh. It's also not a linter, it's a registry: entries live
in your repo, travel with it, and get ranked by file activity so you pay down
hotspots first. And it's passive, it won't block your PR. You can run it
alongside SonarQube, they catch different things at different times.

**"Won't the agent just bypass it?"**

It can. debt-ops isn't a sandbox. The PostToolUse hook fires deterministically
on edits the agent makes through normal tools, and a Stop hook sweeps the end of
each turn as a safety net, but an agent determined to route around it could. The
goal is to make the honest path the easy path, not to be tamper-proof. I'm
clear-eyed about the threat model, it's in an ADR: https://github.com/bcanfield/agentic-tech-debt.

**"Why a plugin instead of a sandbox or standalone tool?"**

Because the debt is created inside the agent loop, so that's where it should be
caught, with the file and the reasoning still in context. A plugin installs in
one command, runs no daemon, and the registry is just files in your repo,
nothing to host. It's also why the same small hook contract ports across Claude
Code, Codex, and Copilot.

---

## Reddit

### r/ClaudeAI (show-and-tell, post the GIF)

**Title:** I built a Claude Code plugin that catches tech debt the moment the agent writes it

Claude is great, but it leaves shortcuts behind faster than I can review them, an
`as any` here, a TODO there, a swallowed exception. debt-ops watches at
write-time: the second the agent loosens a type or punts, it logs an entry to a
folder in your repo [screenshot/GIF]. `review` ranks what to clean up by how
active the file is. It's passive, it doesn't block you.

It's distilled from about 20 years of tech-debt research and I've run it across
dozens of repos. Works in Claude Code, Codex, and Copilot.

Install + demo: https://github.com/bcanfield/agentic-tech-debt. Would genuinely like feedback.

### r/LocalLLaMA (technical, text post)

**Title:** debt-ops: a write-time tech-debt registry wired into the agent loop (Claude Code / Codex / Copilot)

Sharing a thing I built. A PostToolUse hook fires on every edit the agent makes.
When it sees a deferral (an `as any`, a TODO, a `.skip`, a swallowed catch, a
punted decision) it writes a structured entry to a registry folder in the repo.
A Stop hook sweeps the end of the turn as a safety net so nothing slips through.

`review` ranks paydown by behavioral hotspots (how active a file is) rather than
static rules alone, which the research says is the stronger signal. Hooks are
stdlib Python, no daemon, no MCP. The same contract ports across the three CLIs,
plus a portable Agent Skill for other agents.

It's graceful by design, it surfaces and suggests, it doesn't gate. Built on
about 20 years of tech-debt research (Fowler quadrants, ADRs, hotspots).

Repo: https://github.com/bcanfield/agentic-tech-debt. Happy to answer anything about the hook design.

### r/ExperiencedDevs (war story, repo link in a comment)

**Title:** After months of AI-written PRs, I wrote a tool to catch the debt I kept missing in review

Reviewing agent PRs, I kept rubber-stamping small shortcuts, an `as any` to clear
a type error, a TODO that never came back, a swallowed exception. Each one fine,
all of them together a mess. GitClear's data matched the feeling: refactoring
down from ~25% of changes to under 10%, copy-paste overtaking moved code.

So I read up on a few decades of tech-debt research (Fowler, ADRs, behavioral
hotspots) and built something that catches these at write-time instead of review
time, logs them to a registry in the repo, and ranks paydown by file activity.
Passive, doesn't block. I've run it across dozens of codebases.

Curious how others handle this, are you catching it in review, or letting it
ride and hoping? (Tool link in a comment.)

---

## Product Hunt

**Tagline:** Catch AI-written tech debt the moment your agent writes it

**First comment:**

Hi PH 👋 AI writes code faster than we can review it, and the shortcuts (an
`as any`, a TODO, a punted decision) pile up off-screen. debt-ops catches them at
write-time and logs them to a registry in your repo, then ranks paydown by how
active each file is, so you fix hotspots first.

It's distilled from about 20 years of tech-debt research and validated across
dozens of codebases. Passive, no daemon. Works in Claude Code, Codex, and
Copilot, plus a portable skill for other agents. Would love your feedback.

---

## Lobsters (tag: show)

A write-time tech-debt registry wired into the coding-agent loop. A PostToolUse
hook logs deferrals (`as any`, TODO, swallowed catch, punted decisions) to a
folder in your repo; `review` ranks paydown by behavioral hotspots. Stdlib
Python, no daemon. Distilled from ~20 years of tech-debt research (Fowler
quadrants, ADRs, hotspots). Claude Code / Codex / Copilot + a portable skill.
https://github.com/bcanfield/agentic-tech-debt

---

## Bluesky (short thread)

1/ AI writes code faster than you can review it. The shortcuts, an `as any`, a
TODO, a swallowed catch, pile up off-screen.

2/ I built debt-ops: it catches them at write-time and logs each one to a
registry in your repo, the moment your agent writes it.

3/ It's about 20 years of tech-debt research distilled into a plugin, then run
across dozens of repos. Passive, doesn't block you. Claude Code / Codex /
Copilot. https://github.com/bcanfield/agentic-tech-debt

---

## LinkedIn (eng-leader angle)

Developers lose roughly 42% of their week to tech debt (Stripe). With AI in the
loop it compounds: GitClear's study of 211M lines found refactoring fell from
~25% of changes to under 10%, and copy-pasted code overtook moved code for the
first time.

The fix isn't new. Decades of research say the same three things: make debt
visible, pay it down continuously, document the decisions.

We distilled that into debt-ops, a plugin that catches AI-written debt at
write-time and ranks paydown by where your code is actually changing. Validated
across dozens of codebases. Works in Claude Code, Codex, and Copilot. https://github.com/bcanfield/agentic-tech-debt

---

## Direct outreach (DMs / email)

**Hamel Husain** — your `claude-review-loop` was the closest thing to what I
wanted: a check wired into the agent loop instead of bolted on at PR time. I
built debt-ops in a similar shape, a PostToolUse hook that logs tech debt
(`as any`, TODOs, punted decisions) to an in-repo registry as the agent writes
it, ranked by hotspots. Grounded it in ~20 years of tech-debt research and ran
it across dozens of repos. I cite your pattern in the README. Would value your
take if you have a minute: https://github.com/bcanfield/agentic-tech-debt.

**Boris Cherny** — built a Claude Code plugin (debt-ops) around a small
PostToolUse + Stop hook contract that logs AI-written tech debt to an in-repo
registry at write-time, then ranks paydown by behavioral hotspots. Stdlib
Python, no daemon, and the same contract ports to Codex and Copilot. Kept the
hook footprint deliberately tiny. If you ever look at plugin perf, I'd welcome a
critique of the hook design: https://github.com/bcanfield/agentic-tech-debt.

**Simon Willison** — made something you might find interesting: a coding-agent
plugin that catches tech debt at write-time (when the agent casts to `any` or
leaves a TODO) and logs it to a registry in the repo, ranked by file activity.
Distilled from ~20 years of tech-debt research. Show HN is here if it's up your
street: https://github.com/bcanfield/agentic-tech-debt.

**Alex Albert (Anthropic DevRel)** — debt-ops is a Claude Code / Codex / Copilot
plugin that catches AI-written tech debt at write-time and logs it to an in-repo
registry, built on cited tech-debt research and validated across dozens of repos.
I've got a 20-second demo gif if it ever fits a plugin spotlight. No worries
either way: https://github.com/bcanfield/agentic-tech-debt.

---

## Newsletter pitch (template, customize the [section])

**Subject:** Submission: debt-ops, catches AI-written tech debt at write-time

Hi [name], quick one for [section]. debt-ops is a coding-agent plugin that
catches tech debt the moment the AI writes it (an `as any`, a TODO, a punted
decision), logs it to a registry in your repo, and ranks paydown by how active
each file is. It's distilled from about 20 years of tech-debt research and
validated across dozens of codebases. Works in Claude Code, Codex, and Copilot.
https://github.com/bcanfield/agentic-tech-debt. Happy to share the GitClear data behind it if that's useful.

---

## Awesome-list entry

`**[debt-ops](https://github.com/bcanfield/agentic-tech-debt)** — Catches AI-introduced tech debt at write-time and logs it to a registry in your repo, ranked by hotspots. Claude Code, Codex, and Copilot.`

---

## General post (X / longer-form)

GitClear's study of 211M lines shows the pattern: **refactoring is dropping and duplicated code keeps climbing**.

And if you've spent enough time coding with agents, you've felt this pain.

So I ran a study on ~20 years of tech-debt research, distilled the findings into a few commandments, and wired them into my agent loop as a plugin.

How it works: as your agent writes code, **every deferral**, a loose type, a punted decision **gets logged to a folder in your repo as debt**. Every **key decision** gets logged as an **ADR**.

It's a **passive tracker** until **YOU decide to pay the debt down**. Then the plugin walks you through it the research-backed way.

Works in **Claude Code**, **Codex**, **Copilot**, or anything you can drop an Agent Skill into.

Source: https://github.com/bcanfield/agentic-tech-debt


https://www.brandincanfield.com/blog/debt-ops

---

## Launch-day Reddit (final — tiered, post spaced across the day)

> Don't blast all at once. Tailor each title, never reuse verbatim. Engage in the first hour on every one. Re-read each sub's live sidebar before posting (self-promo gates change). Counts/rules sourced from aggregators, not live sidebars.
>
> **Suggested order:** Tier 1 first (r/ChatGPTCoding → r/typescript → r/coolgithubprojects → r/ClaudeAI → r/AI_Agents), then Tier 2 over the following days (r/opensource, r/SideProject, r/cursor, and the Saturday-only r/webdev + r/javascript showcase threads). Tier 3 (r/ExperiencedDevs, r/programming) only via discussion/writeup.

---

### TIER 1 — warmest fit, easiest rules

#### r/ChatGPTCoding (~94k) — lenient, link in post. Best single fit.

**Title:** My coding agent buried an `as any` in an auth file and I didn't notice for three weeks

Found it last week sitting right next to a `// TODO: validate this properly` that I'd clearly scrolled past in the diff when I approved it. That's the pattern that bugs me: the agent leaves a shortcut, you skim the diff, you hit approve, and it's gone from your head by the next prompt. So I built debt-ops, an open-source plugin that hooks into your agent's edits and logs every deferral the moment it lands (`as any`, `@ts-ignore`, TODO, `.skip`, swallowed catch, a punted decision) to a folder in your repo. A Stop hook sweeps the end of each turn so nothing slips through. There's a `review` command that ranks the backlog by how active each file is, so you deal with the stuff you're actually editing instead of a flat 200-item list. It's passive, no daemon, no blocking, stdlib Python, one command to install if you've got git and Python, and it works across Claude Code, Codex, Copilot, plus a portable skill so it's not locked to one tool. [GIF]

Repo's here if you want to poke at it: github.com/bcanfield/agentic-tech-debt. Mostly curious whether other people hit this or if I'm just sloppy with my diffs. Would take any feedback on what it's missing.

#### r/typescript (~169k) — lenient main post, link in post. Highest message-market fit. Lead on type safety.

**Title:** I kept grepping `as any` and finding casts I never agreed to, so I built something to catch them at write-time

`as any` to silence a compiler error, then it ships and nobody ever circles back. With AI agents writing more of the code now, this got worse for me. The agent hits a type error, casts to `any` or drops a `@ts-ignore`, the build goes green, and three weeks later I'm grepping for `as any` and finding 40 of them I never agreed to.

I built debt-ops to catch these at write-time. It's a hook for AI coding agents (Claude Code, Codex, Copilot, plus a portable skill) that fires on every edit. When it sees an escape hatch or deferral, an `as any`, a `@ts-ignore`, a TODO, a `.skip`, a swallowed catch, it logs a structured entry to a folder in your repo the moment it's written. A `review` command then ranks what's worth cleaning up by how active each file is, so the casts buried in code you actually touch float to the top instead of every static-rule hit screaming equally. It's passive, no daemon, stdlib Python, installs with one command (needs git and Python). Repo's here: github.com/bcanfield/agentic-tech-debt.

How do you currently keep `any` from creeping into your codebase? Lint rules like `no-explicit-any`, review discipline, something else?

#### r/coolgithubprojects (~50k) — encouraged, repo link + language tag. Free, zero-risk.

**Title:** [Python] debt-ops: catch tech debt at write-time in your AI coding agent

A plugin for Claude Code, Codex, and Copilot that logs deferrals (`as any`, `@ts-ignore`, TODO, `.skip`, swallowed catch) to a registry folder in your repo as the agent writes them, then a `review` command ranks paydown by how active each file is. Passive, stdlib Python, no daemon.

github.com/bcanfield/agentic-tech-debt

#### r/ClaudeAI (~890k) — strict-ish, link in a COMMENT or projects megathread. Biggest Claude Code audience.

**Title:** Made a plugin that catches the tech debt Claude leaves while it codes

Last week I found three `as any` casts and a swallowed catch block in code Claude wrote, and I'd approved all of it in review. I never see those at the moment they happen, so I built debt-ops. There's a hook that fires on every edit, and when the agent loosens a type, drops a TODO, skips a test, or punts on something, it writes a structured entry to a folder in your repo right then (a Stop hook sweeps the end of each turn so nothing slips). A `review` command sorts what to clean up by how active each file is, so the stuff you actually touch floats up instead of some giant flat list. It doesn't block you or nag, it just keeps the record until you feel like dealing with it.

[GIF]

It's one command to install, needs git and Python (stdlib only, no daemon). Hero is Claude Code but it also runs in Codex and Copilot, plus a portable skill. github.com/bcanfield/agentic-tech-debt

Honestly not sure if this is a real problem for other people or just a me thing, so I'd take any feedback.

#### r/AI_Agents (~296k) — moderate (use the promo thread if there is one), reliability angle.

**Title:** I built a write-time capture layer for the small deferrals agents leave behind

Something I noticed building with coding agents: they ship edits faster than I can actually review them, so the little stuff slips through. An `as any` here, a `@ts-ignore` there, a TODO, a `.skip` on a flaky test, a swallowed catch. None of it is a big deal on its own, but it accumulates silently and you only find it weeks later when something breaks. The usual debt tools scan after the fact, which means you're reconstructing intent long after the agent moved on. So I wired a PostToolUse hook into the agent loop that fires on every edit and, when it spots a deferral, writes a structured entry to a registry folder in the repo right as it happens (a Stop hook sweeps the end of the turn to catch stragglers). Then a `review` command ranks what to pay down by how active the file is, since debt in a hot file matters more than debt in something nobody touches. It's passive, no daemon, stdlib Python, and works across Claude Code, Codex, Copilot, plus a portable skill. Repo's here if you want to poke at it: github.com/bcanfield/agentic-tech-debt. I'm curious whether other people treat this as an observability problem or just trust review to catch it later. How are you handling the deferrals your agents leave behind?

---

### TIER 2 — worth it, with constraints

#### r/opensource (~210k) — moderate, link in post. Lead on the OSS / no-lock-in story.

**Title:** debt-ops: a hook that logs your AI agent's deferrals to files in your own repo

When my coding agent writes `as any` or drops a `// TODO` to get something passing, that decision usually vanishes from memory by the next session. debt-ops is a plugin that catches those the moment they're written (`as any`, `@ts-ignore`, `.skip`, swallowed catches, punted TODOs) and logs each one to a registry folder inside your repo. The registry is just markdown files committed alongside your code, so there's no external service, no account, and no telemetry. The hooks are stdlib Python only, so there's no daemon to run and nothing to host. A `review` command ranks what to pay down first by how active each file is in git history. It runs across Claude Code, Codex, and Copilot, plus a portable skill, so you're not tied to one agent vendor.

Honest limitation: it's not a sandbox. It logs deferrals after the agent writes them, and a determined agent could route around the hook or just not trigger it, so treat it as a record-keeping aid, not enforcement. Install is one command and the whole thing is on GitHub: github.com/bcanfield/agentic-tech-debt. I'd like feedback on the registry file format and which deferral patterns are worth catching, and PRs are welcome.

#### r/SideProject (~622k) — lenient, link in post. Maker crowd (stars/feedback more than users).

**Title:** I built a thing that catches the tiny shortcuts my AI agent sneaks into PRs

The itch: I kept reviewing agent-generated PRs and rubber-stamping the small stuff. An `as any` here, a TODO there, a "we'll decide later" comment. Each one felt too minor to block the PR, and then six months later they're everywhere. So I built debt-ops. It's a hook for AI coding agents (Claude Code, Codex, Copilot, plus a portable skill) that logs each shortcut to a folder in your repo the moment the agent writes it, then a `review` command ranks what to actually fix by how active each file is, so you start with the stuff you keep touching. It's passive, no daemon, and installs with one command. I also spent a while reading through about 20 years of tech-debt research to figure out what's worth tracking and what's noise, since I didn't want it to just be another linter yelling at you. [GIF] Repo's here if you want to poke at it: github.com/bcanfield/agentic-tech-debt. Would love feedback on whether the file-activity ranking actually surfaces the right things for you, or if it misses stuff you'd want flagged.

#### r/cursor (large) — moderate, APPLY THE SELF-PROMOTION FLAIR. Be upfront: no native Cursor support yet.

**Title:** Catching shortcuts your agent writes before they hit review

Something I keep running into with AI coding: the agent writes a quick `as any` or drops a TODO to keep moving, and I don't notice until weeks later when that file is on fire. Code review doesn't catch it because the diff looked fine in the moment.

Upfront: this doesn't have native Cursor support yet. I built an open-source thing called debt-ops that works in Claude Code, Codex, and Copilot, plus a portable Agent Skill you can adapt to other setups. The idea is a hook logs each deferral the agent writes (an `as any`, a TODO, a punted decision) to a folder in your repo as it happens, then a `review` command ranks what to actually fix by how active each file is. It's passive, no daemon.

I'm posting here partly as market research. The pain feels universal even though the tool isn't Cursor-native, and I genuinely don't know if it's worth wiring up Cursor support or if the portable Skill is good enough. Repo's here if you want to poke at it: github.com/bcanfield/agentic-tech-debt

Cursor users, would you want this hooked into Cursor directly, or do you already have a way you catch this stuff? (Applying the Self-Promotion flair.)

#### r/webdev (~2.1M) — Showoff Saturday thread ONLY. Post as a comment in the megathread, GIF-first.

[GIF]

Your AI agent writes code faster than you can review it. debt-ops catches the shortcuts as they land.

It's a plugin for AI coding agents. As your agent codes, a hook logs each shortcut it takes (an `as any`, a TODO, a punted decision) to a folder in your repo. Then a `review` command ranks what to actually fix by how active each file is, so you start with the stuff you're touching anyway. No daemon, nothing running in the background, one command to install. The GIF shows it catching an `as any` in about 8 seconds. Works in Claude Code, Codex, and Copilot.

Repo's here if you want a look: github.com/bcanfield/agentic-tech-debt

#### r/javascript (~2.5M) — Showoff Saturday thread ONLY. Comment in the megathread, code-quality angle.

Caught the agent reaching for `as any` again, so I wrote a thing to keep score.

debt-ops is a plugin for AI coding agents (Claude Code, Codex, Copilot) that hooks into edits and logs every deferral the agent writes as it happens: `as any`, `@ts-ignore`, a bare TODO, a swallowed catch. They land as files in your repo, and a `review` command ranks them by how active each file is so you fix the stuff you actually touch. It's passive, no daemon, one command to install. [GIF] shows it catching an `as any` in under 8 seconds.

github.com/bcanfield/agentic-tech-debt

---

### TIER 3 — high reward, high removal risk. Discussion/writeup only, never a direct pitch.

#### r/ExperiencedDevs (~250k+) — war story. NO link in post; drop it in your own top comment a minute later.

**Title:** Months of reviewing AI agent PRs and I realized I'd been rubber-stamping the small stuff

Every agent PR came with one or two tiny shortcuts. An `as any` to clear a type error, a TODO where a real decision should've been, a catch block that quietly swallowed the error. Each one looked harmless in isolation so I'd approve and move on. Six months later half the codebase is held together with that stuff and I'm the one who signed off on all of it. There's a GitClear study that lines up with what I felt watching it happen: across 211M changed lines, refactoring dropped from around 25% of changes to under 10%, and copy-pasted code is now overtaking moved code. The review gate clearly isn't enough on its own anymore, at least not the way I was running it. How's everyone else dealing with this, are you catching it in review, leaning on some tooling, or just accepting it as the cost of moving faster?

**First comment (post yourself a minute later):** For what it's worth, I got tired of catching these one at a time in review so I ended up building a little thing that logs them at write-time instead and ranks paydown by how active each file is. It's open source if anyone wants to poke at it: github.com/bcanfield/agentic-tech-debt

#### r/programming (~6M) — link the blog writeup, data-led title. Brutal on self-promo; the post must stand alone as a read.

**Title:** Refactoring fell from ~25% of code changes to under 10% since AI coding tools took off (GitClear, 211M lines)

GitClear analyzed 211M changed lines and found refactoring dropped from around 25% of changes to under 10%, while duplicated/copy-pasted code passed moved code for the first time on record. That tracks with what I've seen reviewing agent-generated PRs: lots of small additions, almost no cleanup. I went through about 20 years of tech-debt research to figure out what actually helps manage this, and wrote up the findings plus the tool I built to catch AI-written shortcuts at write-time. https://www.brandincanfield.com/blog/debt-ops

---

### Skip (don't waste a post)

r/LocalLLaMA (local/open-weight models, not coding tooling) · r/devtools + r/programmingtools (quarantined/dead) · r/OpenAI · r/artificial · r/ArtificialInteligence · r/singularity (general AI, not devs) · r/SaaS · r/EntrepreneurRideAlong · r/IndieDev (indie *game* devs) · r/InternetIsBeautiful · r/madewithai · r/github (wrong audience — founders / non-devs / not a discovery channel)

---

## Product Hunt (final — dedicated launch day, post at 12:01am PT)

**Tagline (50 chars):** Catch AI tech debt the second your agent writes it

**Description (~260):** debt-ops logs tech debt the moment your AI agent creates it. When it casts to `as any`, drops a TODO, or punts a decision, it goes into a registry in your repo. A `review` command ranks paydown by file activity, so you fix the hot spots first. For Claude Code, Codex, and Copilot.

**First maker comment (pin this):**

I kept finding `as any` casts and stale TODOs in my repo months after my agent wrote them, with no idea which ones actually mattered. The problem is AI writes faster than I can review, so the small shortcuts slip by and pile up where I can't see them. So I built debt-ops. It watches your agent and logs each shortcut to a registry folder in your repo the moment it happens, then the `review` command ranks what to pay down by how active each file is, so you start with the hot spots instead of guessing. It's passive on purpose: no daemon, no blocking, just a running record until you decide to deal with it. A lot of the ranking logic comes from digging through about 20 years of tech-debt research. It runs in Claude Code, Codex, and Copilot, plus a portable skill, and installs in one command (you just need git and Python). How do you currently keep track of the shortcuts your agent leaves behind, if at all?

**Topics/tags:** Developer Tools · Artificial Intelligence · Open Source · GitHub