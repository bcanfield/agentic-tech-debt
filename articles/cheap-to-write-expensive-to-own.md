---
title: "Writing Code Got Cheap. Owning It Didn't."
publishedAt: "2026-06-12"
updatedAt: "2026-06-12"
author: "Brandin Canfield"
series: "Agentic Tech Debt"
summary: "Generation cost fell to near zero while the cost of reviewing, testing, and maintaining code held, which is most of what the AI-debt data is measuring."
tags: ["ai", "technicaldebt", "softwareengineering", "codequality", "programming"]
image: "/cheap-to-write-expensive-to-own.cover.jpg"
---

The price of producing a line of code fell to about zero in the last two years. The price of living with that line did not move. Most of the AI-debt argument is people standing on one side of that split or the other without naming it.

Gauge, a dev-tools consultancy, put the consequence plainly: "AI has significantly increased the real cost of carrying tech debt... the penalty for having a 'high-debt' codebase is now larger than ever." That's stranger than it sounds — AI is supposed to be the thing that *helps* you with a messy codebase. Gauge is saying the messy codebase got more expensive to own in the same window the tooling meant to fix it arrived.

It costs something to write code and something else to live with it, and people keep treating the two as one number they call "productivity." Writing is what it takes to get code to exist: you type it, or now you prompt for it. Living with it is everything after that. You read it, you review it, you test it, you debug it at 2am, you explain it to whoever inherits it, you decide whether the shortcut buried in it is safe. The first cost collapsed. The second one is made of human attention, and human attention costs exactly what it cost in 2022.

When writing was expensive, that expense was also a throttle. A human typing the code was, by the same motion, the human who'd read every line, held the design in their head, and felt the friction of each shortcut as they took it. Slow production *was* the review. You couldn't generate faster than you understood, because the generating and the understanding were the same act. That coupling is what broke. Now the code can exist without anyone going through the act that used to produce understanding for free, so the understanding gets bought separately, after the fact, usually by someone who wasn't in the room.

![Two cost curves on a 2022 to 2026 timeline. The "cost to generate code" line drops steeply toward zero as coding agents arrive. The "cost to own it" line, covering read, review, test, debug, and hand off, stays flat or drifts up. The two lines cross, and the shaded gap after the crossing is labeled "the debt." A caption notes that before AI the two were the same line, because the person who wrote it was the person who read it.](/cheap-to-write-expensive-to-own.diagram.png)

The data shows it once you read it as two costs and not as a quality score. GitClear looked at 211 million changed lines and found that during 2024, for the first time they'd ever measured, copy-pasted code beat refactored code: duplicated blocks rose eightfold in that one year, while "moved" lines (someone reorganizing rather than re-pasting) dropped by about 40 percent. Pasting a block is cheap; every copy is a place a future fix has to land again.

The study people cite to argue the opposite is the one I find most convincing here. METR ran a randomized trial: sixteen experienced developers on their own repos, with early-2025 models, so don't carry it further than that. They came out 19 percent slower with AI, and didn't notice. They'd predicted a 24 percent speedup going in, and after finishing the tasks, slower, they still believed they'd gone 20 percent faster. The prompting got fast, and prompting is the part you feel, so the work feels fast. What got slower was the reading and the re-prompting and the checking of output you didn't write, and almost nobody counts that as work. I don't, in the moment. I notice the slowness later, when I'm three commits deep trying to remember why the agent did a thing.

![Drake meme. Top panel, Drake waving it off: "being 19% slower with the ai." Bottom panel, Drake nodding in approval: "feeling 20% faster with the ai." Both describe the same METR developers in the same trial.](/cheap-to-write-expensive-to-own.meme.png)

The asymmetry might just be a property of *current* models, and the models keep getting better. Veracode clocked GPT-5 Mini at a 72 percent pass rate on their security suite in late 2025, up sharply from the 45 percent that made headlines. If generated code keeps getting more correct, the ownership tax on each line falls, and the asymmetry closes on its own without anyone building anything. That's a real argument, and I don't have a clean rebuttal, only a partial one.

Better models close the wrong half. A more correct model does lower the cost of any *single* line you own: fewer bugs per line, fewer findings to chase. But a lot of that cost is per-*decision*, not per-line, and a better model makes more decisions, faster, none of them written down, and you check fewer of them because it's earned the benefit of the doubt. Gartner hangs its whole defect forecast on exactly that reflex, "automation bias," developers who "implicitly trust AI suggestions," in its Predicts 2026 report. So the lines get cleaner while the decisions behind them get more numerous and harder to see, which is the part the better-model argument doesn't price in.

I maintain a small plugin, and a few weeks ago I had a decision to make about how it's put together. It ships as four self-contained copies, which means every shared script is duplicated four times and a fix has to be applied to all four. The DRY instinct says extract a shared module. I'd even written that plan down earlier; there's an ADR in the repo, 0011, that scheduled the extraction for when a third adapter landed. A third adapter landed. A fourth landed. And the decision I actually made, recorded in ADR 0014, was to *reverse* the plan: keep all four copies and sync them by hand, on purpose. The line from that file:

```
Status: Accepted (supersedes ADR 0011's extraction trigger and packaging-plan Phase E)
```

I chose the higher cost to write (four copies, more lines, more typing) to buy a lower cost to own: each adapter stays a thing one person can read top to bottom, with nothing hidden behind an abstraction. That only worked because the decision got written down where I'd find it. Most of the decisions a coding agent makes for you don't get an ADR. They get a clean line that compiles, and the reasoning behind it is gone by the next session.

That evaporation is the expensive part, and it's the gap I built [debt-ops](https://github.com/bcanfield/agentic-tech-debt) to close: it makes an agent record the decisions it defers, so the ownership cost lands somewhere a person can see it instead of accruing in silence.

None of this is an argument against generating code with AI. I do it daily; the generation really is nearly free, and that's genuinely good. It's an argument against reading the free generation as a free *lunch*. The two costs came apart, and the one that's left is the one nobody put on a curve.

*Cover photo by mediha ekici on Unsplash.*
