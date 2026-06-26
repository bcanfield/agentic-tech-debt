---
title: "Your Agent Is Pasting More Than It's Refactoring"
publishedAt: "2026-06-14"
updatedAt: "2026-06-14"
author: "Brandin Canfield"
series: "Agentic Tech Debt"
summary: "GitClear measured copy-pasted code passing refactored code for the first time in 2024, with duplicated blocks up 8x. What that means for your repo."
tags: ["ai", "technicaldebt", "codequality", "programming", "softwareengineering"]
image: "/ai-spiked-duplicate-code-8x.cover.jpg"
---

Of the blocks your coding agent pasted into the codebase this week, a larger share are copies of something already in the repo than at any point anyone has measured. That's the most cited number in the AI-code-quality argument, and it comes from GitClear: duplicated code blocks of five or more lines rose eightfold during 2024.

GitClear builds code-review analytics, so this is their data on their terms, and I'll come back to what that's worth. But the size of it is hard to wave off: 211 million changed lines across 2020 through 2024, from repos that include Google, Microsoft, and Meta. Not a survey of how developers feel, not a benchmark on toy tasks, but the actual line-level diff history of real codebases over five years.

![GitClear's dataset at a glance: 211 million changed lines of real line-level diff history from 2020 to 2024, across repos including Google, Microsoft, and Meta, not a developer survey.](/ai-spiked-duplicate-code-8x.anchor.png)

The headline finding is a crossover. Refactoring and cloning both show up in a diff as added-and-removed lines, but they mean opposite things: "moved" lines are existing code reorganized into one place, copy-pasted lines are a second copy you tweak instead. In 2024, for the first year in their data, copy-pasted lines beat moved ones.

![A before/after of GitClear's three code-change rates, 2020 next to 2024. Copy-pasted lines rise from 8.3 percent to 12.3 percent; moved (refactored) lines fall from 24.1 percent to 9.5 percent; code revised within two weeks climbs from 3.1 percent to 5.7 percent. A marker notes 2024 as the first year copy-paste exceeded moved code.](/ai-spiked-duplicate-code-8x.diagram.png)

Now the honest caveat. GitClear sells code-review analytics, so a story where code quality is sliding is good for their business. Read it as vendor research. The timing lines up, but the dataset can't close correlation to cause: AI adoption climbed across exactly these years and so did duplication, and that's all the data establishes.

What I trust is that mechanism, because I can watch it happen. Refactoring is the expensive option: find the existing code, understand it well enough to know your case fits, pull it into a shared place without breaking the three other callers. Pasting skips all of that and hands you a block that works right now. An agent asked for code that works will reach for whatever produces working code fastest, and that's paste. Nothing about it requires the model to be bad. A perfectly correct paste is still a paste. My own repo complicates that picture, which I think is the actual point. Point a duplicate-block detector at the project I'm writing this series about and it lights up: I ship the plugin as four self-contained copies, one each for Claude Code, Codex, Copilot, and a portable set. The function that finds the git root is defined nineteen times, byte-identical copies synced by hand. It's nineteen and not four because each adapter repeats the helper in every script that needs it. By GitClear's measure that's me producing exactly the duplication the report counts.

```
$ grep -rl "def git_toplevel" --include=*.py . | wc -l
19
```

Except the duplication is deliberate. An architecture decision record in the repo, ADR 0014, argues for it: installed plugins are isolated directories, the hooks have to be standard-library-only, and a shared module would couple four things meant to stay independent. So I pay a known tax (a fix has to land in all nineteen copies in the same change), and there's a written rule that says so. The duplication GitClear is measuring is the other kind, the kind that shows up in a diff because pasting was the path of least resistance and nobody wrote down that a second copy now exists. Same grep result, opposite situations.

Which is why churn is the number I'd actually watch, more than duplication. A copy can be the right call, so a raw count can't separate debt from a financed decision; code revised within two weeks of landing is mostly code that wasn't right the first time, which tracks quality more directly. So here's what I'd check in your own repo this week. Pick a helper you know exists, like a date formatter or an auth check or a retry wrapper, and grep for how many near-copies of it your agent has scattered around. Then check your git history for the files rewritten within a couple weeks of being added. You're not measuring against GitClear's 12.3 percent; you're answering a simpler question: when your agent needed something the codebase already had, did it find it, or paste a new one? The answer is in your own diff history, the only dataset about your code you don't have to take on faith.

![Distracted-boyfriend meme. The boyfriend, labeled "the agent," turns away from his girlfriend, "the existing helper, one import away," to look at another woman, "pasting a fresh copy." Both paths produce working code; only one of them you now have to remember exists.](/ai-spiked-duplicate-code-8x.meme.png)

I write a plugin called debt-ops for tracking the deferred-decision version of this, a different surface than raw duplication, and I won't pretend it dedupes anything; it's at [github.com/bcanfield/agentic-tech-debt](https://github.com/bcanfield/agentic-tech-debt) if the asymmetry it comes from is one you keep hitting too.

*Cover photo by Kristijan Arsov on Unsplash.*
