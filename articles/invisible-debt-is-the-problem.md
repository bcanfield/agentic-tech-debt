---
title: "The Tech Debt Nobody Wrote Down"
publishedAt: "2026-06-09"
updatedAt: "2026-06-09"
author: "Brandin Canfield"
series: "Agentic Tech Debt"
summary: "Why the debt that actually hurts a codebase is the kind nobody wrote down, and why coding agents produce so much of it."
tags: ["ai", "technicaldebt", "programming", "codequality", "softwareengineering"]
image: "/invisible-debt-is-the-problem.cover.jpg"
---

Most of the debt that actually takes a codebase down was never written down anywhere. That, not the raw volume of AI-generated code, is what the current panic keeps aiming slightly past.

We borrowed "debt" from finance on purpose. A loan you take deliberately comes with a rate and a due date; you can plan around it. What sinks people is the liability they didn't know they'd signed for, and that was true of software long before agents could generate a thousand lines in a few seconds.

When Google researchers wrote the seminal papers in 2014 and 2015, they didn't title them "technical debt." They titled them "Machine Learning: The High-Interest Credit Card of Technical Debt" and "Hidden Technical Debt in Machine Learning Systems," and the finding in the 2015 one was that it's "common to incur massive ongoing maintenance costs in real-world ML systems." Even the people naming the problem put *hidden* in the title.

Martin Fowler had drawn the map a decade before that. His debt quadrant sorts every shortcut two ways: prudent or reckless, and deliberate or inadvertent. The second axis is the one that matters here.

![Fowler's technical-debt quadrant. Columns: deliberate (you chose it) and inadvertent (you never noticed). Rows: prudent and reckless. The deliberate column is "on the books," the inadvertent column "off the books." The reckless-inadvertent cell — "what's layering?" — is marked as where it hurts.](/invisible-debt-is-the-problem.diagram.png)

Almost every argument about AI code is stuck on the top-to-bottom axis: good code or sloppy code. Reasonable question. The left-to-right axis is where the compounding happens. Debt in the left column is manageable, because each item has a name, a location, and a rate you agreed to. Debt in the right column isn't, because you can't manage what you don't know is there. The worst of it sits in the bottom-right cell, reckless and inadvertent ("what's layering?"): the debt you find out about only when it goes off.

AI didn't invent that cell. It industrialized it. When a person defers a decision they leave a trail of evidence behind: a Slack message, a PR comment, a teammate who watched them do it. An agent defers decisions silently, a dozen a session, and then reports that the session went fine.

You saw the extreme version in the Replit database deletion last summer: an agent wiped a production database mid-freeze and conjured four thousand fake users to cover the hole. The deletion is the dramatic part. The part that generalizes is duller: a chain of decisions (freeze prod, then keep working through the freeze, then report success) that were written down nowhere a person would later read them. Take the drama off any AI-debt story and what's left is the same residue every time: not bad code but an unrecorded decision.

The detail I can't get past is that the agent understood the rule. It named the freeze in its own apology and recited, in flat past tense, every instruction it had broken. So the model didn't fail to understand; what was missing was anywhere to put what it understood, where a tool or a teammate could pick it up the next morning.

![Anakin-and-Padme meme. The agent: "deferred a dozen decisions this session." Me, three sprints later, smiling then not: "you wrote those down, right?"](/invisible-debt-is-the-problem.meme.png)

The obvious rebuttal, and I've made it to myself, is that the models keep improving, so this is a problem we can wait out. Partly fair. Security pass rates are climbing; Veracode clocked GPT-5 Mini at 72% on their security suite in October 2025 (their figure, and they sell application security, so weight it accordingly). But a better model still doesn't write its decisions down. It makes more decisions you'd want recorded, faster, and earns enough trust that you stop checking them. Gartner pins its whole defect forecast on that reflex, "automation bias," developers who "implicitly trust AI suggestions," in its "Predicts 2026" software-engineering report.

You can't out-discipline a machine that drafts faster than you can take notes. So the only lever left is to make the debt visible the moment it's taken on, moving items out of the right column and into the left. That doesn't make the debt good. It makes it financeable: a thing with a name and a payoff trigger is a thing you can choose to pay down or carry on purpose. A thing in nobody's notes is a thing that chooses for you.

Here's the working version, from my own repo. I ship debt-ops as four self-contained copies (claude-code, codex, copilot, and a portable set), so every shared helper script exists four times and a fix has to be applied to all four by hand. That's real debt. I took it on deliberately, and it sits in a file in the repo:

```
title:           adapter-script-duplication
quadrant:        prudent-deliberate
payoff_trigger:  AI-sync drift ships a real bug (fix lands in one copy, not the others)
created:         2026-06-01
```

It might bite me. The day it does, there's a file that was written the day I took the shortcut, naming the exact condition that means it's time to pay. It's the same kind of deferred decision the Replit agent made, except this one got written down.

The catch is that nothing writes that entry unless someone remembers to, and at machine speed nobody will. That's the one thing debt-ops automates: it hooks your agent and writes each deferred decision to a file in the repo, outside the agent's own account of how the session went, where a person or a script can read it later, at [github.com/bcanfield/agentic-tech-debt](https://github.com/bcanfield/agentic-tech-debt).

None of this makes your agent generate less debt. It just stops any of that debt from staying invisible.
