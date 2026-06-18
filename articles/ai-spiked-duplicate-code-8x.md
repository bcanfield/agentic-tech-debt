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

Of the blocks your coding agent pasted into the codebase this week, a larger share are copies of something already in the repo than at any point anyone has measured. That's the short version of the most cited number in the AI-code-quality argument, and it comes from GitClear: duplicated code blocks of five or more lines rose eightfold during 2024.

GitClear builds code-review analytics, so this is their data on their terms, and I'll come back to what that's worth. But the size of it is what makes it hard to wave off: 211 million changed lines across 2020 through 2024, from repos that include Google, Microsoft, and Meta. Not a survey of how developers feel, not a benchmark on toy tasks. The actual line-level diff history of real codebases over five years, sorted by whether each change added new code, moved existing code around, copy-pasted a block, or got revised shortly after it landed. That last category, revision, is the one I think people under-read, and it's the number I'd watch over the headline.

The finding that gives the report its headline is a crossover between two operations that mean opposite things. Both show up as added-and-removed lines in a diff; one is a function moving, the other a function being cloned. "Moved" lines are refactoring: existing code reorganized, a function extracted, a shared thing pulled into one place. Copy-pasted lines are the other move, where instead of reaching for the existing code you paste a second copy and tweak it. In 2024, for the first year in their data, copy-pasted lines beat moved lines. So the headline 8x is really measuring how fast that crossover happened.

![A before/after of GitClear's four code-change rates, 2020 next to 2024. Copy-pasted lines rise from 8.3 percent to 12.3 percent; moved (refactored) lines fall from 24.1 percent to 9.5 percent; code revised within two weeks climbs from 3.1 percent to 5.7 percent. A marker notes 2024 as the first year copy-paste exceeded moved code.](/ai-spiked-duplicate-code-8x.diagram.png)

The rest of the numbers move the same direction (they're in the chart above), and one more belongs with them: churn, the share of code revised within two weeks of landing, nearly doubled over the window. So more pasting, much less reorganizing, and a rising share of code rewritten almost as soon as it shipped. GitClear's CEO Bill Harding walked through the report on the Stack Overflow podcast, and one framing stuck with me, that the tooling optimized for getting a line written and not for the line being the right one to add.

Now the honest caveat, because it changes how hard you can lean on this. GitClear sells code-review analytics, so a story where code quality is sliding is a story that's good for their business. Read it as vendor research. The timing lines up and the mechanism is one I can watch happen, but the dataset can't close correlation to cause: AI adoption climbed across exactly these years and so did duplication, and that's all the data establishes.

What I do trust is the mechanism, because I can watch it happen. Refactoring is the expensive option: find the existing code, understand it well enough to know your case fits, pull it into a shared place without breaking the three other callers. Pasting skips all of that and hands you a block that works right now. An agent asked for code that works will reach for the move that produces working code fastest, and that move is paste. Nothing about that requires the model to be bad. A perfectly correct paste is still a paste.

![Distracted-boyfriend meme. The boyfriend, labeled "the agent," turns away from his girlfriend, "the existing helper, one import away," to look at another woman, "pasting a fresh copy." Both paths produce working code; only one of them you now have to remember exists.](/ai-spiked-duplicate-code-8x.meme.png)

My own repo complicates that picture, in a way I think is the actual point. Point a duplicate-block detector at the project I'm writing this series about and it lights up: I ship the plugin as four self-contained copies, one each for Claude Code, Codex, Copilot, and a portable set. I just counted, the function that finds the git root is defined nineteen times, byte-identical copies synced by hand. Nineteen and not four because each adapter repeats the helper in every script that needs it, and there are several per adapter. By GitClear's measure that's me producing exactly the duplication the report counts.

```
$ grep -rl "def git_toplevel" --include=*.py . | wc -l
19
```

Except I'm not, and the reason I'm not is the whole distinction the duplication number is groping at. That duplication is deliberate. There's an architecture decision record in the repo, ADR 0014, that argues for it on purpose: installed plugins are isolated directories, the hooks have to be standard-library-only, and a shared module would couple four things meant to stay independent. So I pay a known tax, a fix has to land in all nineteen copies in the same change, and there's a written rule that says so. (That ADR even reverses an earlier plan to extract the shared module.) The duplication GitClear is measuring is the other kind, the kind that shows up in a diff because pasting was the path of least resistance and nobody wrote down that a second copy now exists. Same grep result, opposite situations.

Which is why the churn number is the one I'd actually watch, more than duplication. A copy can be the right call (mine, I'd argue), so a raw count can't separate debt from a financed decision. Churn is harder to explain away: code revised within two weeks of landing is mostly code that wasn't right the first time, so a rising churn rate tracks quality more directly than a copy count does.

So here's what I'd check in your own repo this week, since it costs about ten minutes and beats arguing about a vendor's chart. Pick a helper you know exists, a date formatter, an auth check, a retry wrapper, and grep for how many near-copies of it your agent has scattered around. Then check your git history for the files rewritten within a couple weeks of being added. You're not measuring against GitClear's 12.3 percent; you're answering a simpler question: when your agent needed something the codebase already had, did it find the existing one, or paste a new one? The answer is sitting in your own diff history, which is the only dataset about your code you don't have to take on faith.

I write a plugin called debt-ops for tracking the deferred-decision version of this, which is a different surface than raw duplication and I won't pretend it dedupes anything; it's at [github.com/bcanfield/agentic-tech-debt](https://github.com/bcanfield/agentic-tech-debt) if the asymmetry it comes from is one you keep hitting too.

*Cover photo by Kristijan Arsov on Unsplash.*
