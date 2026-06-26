---
title: "Catch the Debt Your Agent Writes, with Grep and a Folder of Markdown"
publishedAt: "2026-06-10"
updatedAt: "2026-06-10"
author: "Brandin Canfield"
series: "Agentic Tech Debt"
summary: "A manual catch-register-review-paydown loop you can run by hand today, then the hook that runs the catch step for you."
tags: ["ai", "technicaldebt", "programming", "codequality", "devops"]
image: "/running-tech-debt-ops-with-an-ai-agent.cover.jpg"
---

> Full content, research, and plugins → **[debt-ops on GitHub](https://github.com/bcanfield/agentic-tech-debt)**

The problem with letting an agent write most of your code isn't that the code is bad. A lot of it is fine. The problem is the rate. An agent will defer a dozen small decisions in a session (cast a value to `any` to clear a type error, swallow an exception so a test goes green, pick a default "for now") and then tell you the session went well, because by its own account it did. OX Security, which sells code-security tooling so weigh it accordingly, put the mechanism plainly in their October 2025 "Army of Juniors" report: "vulnerable systems now reach production at unprecedented speed, and proper code review simply cannot scale to match the new output velocity."

That's the bind. You can't review at the speed the thing generates, and telling it to slow down defeats the point of using it. So you make the deferrals visible the moment they happen and deal with them on your own schedule. Four steps, all of them runnable by hand starting today: catch, register, review, pay down. No installs. I'll walk the manual version first, because it genuinely works and you should know what you're automating before you automate it.

## Catch: grep for the shortcuts the agent didn't mention

The catch step is finding the deferrals in code your agent already wrote. Most of them leave a fingerprint. Not all of them; the worst ones don't, and I'll get to that. But enough that a handful of greps clears the easy 80%.

The pattern that started this whole project for me is the escape-hatch type cast. In TypeScript that's `as any`; the agent reaches for it the instant the type checker complains, and the cast erases the very thing the checker was protecting:

```bash
# loosened types: the agent's favorite way to make tsc shut up
grep -rn "as any\|: any\b\|@ts-ignore\|@ts-expect-error" src/

# swallowed errors: the catch block that does nothing
grep -rn "except:\s*$\|except Exception:\s*pass\|catch\s*(.*)\s*{\s*}" .

# the markers people leave when they know but keep going
grep -rEn "TODO|FIXME|HACK|XXX" src/
```

The last grep is the weakest. A `TODO` is a deferral someone bothered to label, and most agent deferrals don't get one. They get a clean line that compiles. The cast is invisible to the test suite and to your eye on a 400-line diff; only a grep that knows what an `as any` looks like will find it.

Run those after a session and you'll get hits. Some are real debt, plenty are noise (a `: any` in a third-party `.d.ts` you can't touch). That's fine. The triage is the next step, and over-catching is the right failure mode here. A false positive costs you a glance; a missed deferral costs you a debugging afternoon three sprints out.

## Register: a folder of markdown, one file per decision

Here's where the manual loop earns its keep, and it's almost embarrassingly low-tech. For each real deferral, write a markdown file into a `docs/debt/` folder and commit it next to the code. One file, one decision. That's the registry.

The format matters less than the fields. I use frontmatter so a script can rank it later, but a teammate doing this with a plain sentence per file would get 90% of the value. The fields I won't skip: where the debt lives (so churn can be measured against it), why it exists, and the load-bearing one, the payoff trigger. Not a due date. The *condition* that means it's time to pay, like "the first time someone touches this auth path again" or "when we add a second payment provider." A due date is a guess; a condition is something you can actually wait for.

![A single debt-registry markdown file for the adapter-script-duplication entry, showing its fields: hotspot, why, Fowler quadrant, and the payoff trigger.](/running-tech-debt-ops-with-an-ai-agent.anchor.png)

Why not `TODO` comments? I assumed they were good enough for a while; they're not, for a reason specific to agents. A `TODO` travels with the code, which sounds fine until the agent rewrites that file next session and the comment goes with it, or gets "cleaned up." A Jira ticket dies in grooming three weeks later when nobody remembers the context. A markdown file checked into the repo survives both: version control tracks it, grep finds it, and because it isn't real code the agent doesn't touch it on its next pass. The decision and the code that prompted it are committed together, the one time all the context is in the same place.

What surprised me building this is how much of it is just *writing the decision down at the moment you make it*. Take the Replit database deletion last summer, the agent that wiped a production database mid-freeze and apologized in flat past tense, reciting every rule it broke. The agent understood the freeze fine. It named it in the apology. The miss was that "we're working through it anyway" was written down nowhere outside the chat log. A registry is that anywhere.

![Gru's-plan meme. Panel 1: "grep for the shortcuts after every session." Panel 2: "register each one to docs/debt/." Panel 3: "if I remember to run the grep." Panel 4: Gru does a double-take at the same line, realizing the plan's whole catch step depends on him remembering.](/running-tech-debt-ops-with-an-ai-agent.meme.png)

## Review: rank by where the code actually churns

Now you have a folder filling up with entries. Most of them you'll never need to act on. Debt in a file nobody touches is just a note, and paying it down is a vanity refactor. Roughly a fifth of your files generate most of the rework, so the review step is about finding which entries sit in that fifth.

The signal is churn. How often does the file an entry points at actually change? Git already knows:

```bash
# how many times each registered hotspot changed in the last 90 days
git log --since="90 days ago" --name-only --format= -- src/ \
  | sort | uniq -c | sort -rn | head -20
```

Cross that list against your `docs/debt/` entries. A debt entry on a file that shows up near the top is the interest payment you're making over and over; an entry on a file with zero changes since you logged it can wait, maybe forever. That ranking is the whole review heuristic: Fowler's intent quadrant for *what kind* of debt it is, churn for *how much it's costing you*. You don't need a tool for it. You need the git command above and ten minutes.

## Pay down: smallest change that resolves the entry, then drop it

Paying down is the least interesting step and I'll keep it short, which is also roughly how much attention it deserves relative to the other three. Take the top entry, make the smallest change that resolves it (make it less bad, don't make it perfect, and don't refactor the neighborhood), confirm a test pins the fix, delete the entry file. If the area has no tests, that absence is itself the finding; decide whether to add one before touching anything. Do three to ten per session, not a stop-the-world cleanup quarter. Unsupervised batch refactoring is one of the things the GitClear data caught making duplication *worse*, not better.

That's the loop. Catch, register, review, pay down, repeat. It works with grep, git, and a folder, and if you stopped reading here you'd already have something that works.

## Or let a hook run the catch step every time

The honest problem with the manual loop is the catch step. It only works if you remember to run it, and the entire premise of this series is that at agent speed you won't. The decisions go by faster than you take notes. Everything downstream (the registry, the churn ranking, the paydown) is durable once an entry exists. The fragile link is a human noticing the deferral in the first place.

So I wrote a hook to do that catching for me. debt-ops is a plugin that watches your coding agent and runs the catch step on every edit; each deferral is registered to a file in `docs/debt/`, the same folder and format as the manual version, just written without you having to catch it. The review step is a skill that runs the churn ranking for you. Here's that skill against this repo's own registry, real output, eight entries deep into building the thing in public:

```
debt-ops review — 8 entries
─────────────────────────────────
top 3 to pay down
  • adapter-script-duplication               codex · planned tradeoff · 11 edits since logged [ai]
    The helper scripts and skills are duplicated across four self-contained
  • humanize-skill-soft-dep                  .claude/skills/write-article/SKILL.md · planned tradeoff · 5 edits since logged [ai]
    The write-article skill defers its full AI-tell catalog and deterministic audit to t...
  • skill-triggers-unoptimized               .claude/skills/write-article/SKILL.md · planned tradeoff · 5 edits since logged [ai]
    Both content-pipeline skills shipped with hand-written descriptions; the skill-creat...
```

That top entry is the project documenting its own shortcut. I ship debt-ops as four self-contained copies, so every shared script exists four times and is synced by hand. That's a deliberate tradeoff, registered against itself, ranked top because that file churns. None of it is mocked up for the article. It's what the command prints when I run it just now.

![The catch, register, review, and pay-down loop in two columns: what you run by hand today, and which step the debt-ops hook takes over.](/running-tech-debt-ops-with-an-ai-agent.diagram.png)

Since the plugin watches your agent and reads your repo, here's exactly what it is and isn't, because the one plugin I watched get torched on Hacker News died for undisclosed server calls. debt-ops runs entirely on your machine. The hooks are stdlib Python, no dependencies to audit. It makes no network calls and sends no telemetry; the registry is plain markdown in your repo, the only state is a local cache, and it's MIT-licensed. You can read every line before you trust it with a single edit, which given what it's hooked into is the point.

It installs as a Claude Code plugin:

```
/plugin marketplace add bcanfield/agentic-tech-debt
/plugin install debt-ops@agentic-tech-debt
```

(It also runs on Codex, Copilot, and other agents through portable skills; that's in the repo readme.)

What it doesn't do is the part I'd want it to and can't make honest: it won't pay your debt down for you, not unattended, not in a way I'd trust against an auth path. The catch step is mechanical, so I automated it. The judgment steps (is this entry worth fixing, what's the smallest safe change) I still do by hand, one at a time, with the diff in front of me. If I'm honest that's also just how I like working, so take the recommendation with that grain of salt: I built the tool to do the part I'd forget, and kept the part I didn't want to give up.

> The repo is [github.com/bcanfield/agentic-tech-debt](https://github.com/bcanfield/agentic-tech-debt). Grep your own `src/` first, though — you'll find the hits whether or not you ever install anything.

*Cover photo by Lindsay Cotter on Unsplash.*
