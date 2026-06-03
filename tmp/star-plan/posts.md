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
