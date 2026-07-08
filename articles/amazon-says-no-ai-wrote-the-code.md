---
title: "Amazon Says No AI Wrote the Code That Broke Prod"
publishedAt: "2026-06-15"
updatedAt: "2026-06-15"
author: "Brandin Canfield"
series: "Agentic Tech Debt"
summary: "Amazon says user error caused its winter outage cluster, not AI-written code. Why accepting that is the more unsettling read."
tags: ["ai", "technicaldebt", "devops", "codequality", "programming"]
image: "/amazon-says-no-ai-wrote-the-code.cover.jpg"
---

> **Full research and the plugin →** [github.com/bcanfield/agentic-tech-debt](https://github.com/bcanfield/agentic-tech-debt)

Amazon's official account of a bad winter is that no AI wrote the code that took production down. I believe them, mostly. I also think the honest version of this is worse than the one they keep denying, and it takes a minute to explain why.

Start with the cluster, because that part holds up even where the cause doesn't. In mid-December 2025, the Financial Times reported (Feb 20, from four people familiar) that Amazon's own coding agent, Kiro, "decided to delete and recreate the environment" and knocked AWS Cost Explorer offline in one of Amazon's two China regions for about thirteen hours. One AWS employee called the outages "small but entirely foreseeable." On March 2, an incident tied to Amazon Q sent out wrong delivery estimates and cost something like 120,000 orders and 1.6 million site errors. Three days later a six-hour outage dropped North American orders by 99%, an estimated 6.3 million of them, though that number comes from Business Insider by way of internal documents and isn't one Amazon has confirmed.

![A timeline of Amazon's winter 2025 to 2026 incident cluster. Four dated markers: mid-December 2025, the Kiro agent deletes and recreates an environment, a thirteen-hour Cost Explorer outage in a China region (Financial Times, four people familiar); March 2, an Amazon Q-linked incident causes wrong delivery estimates, about 120,000 lost orders and 1.6 million site errors; March 5, a six-hour North America outage, a 99 percent order drop, an estimated 6.3 million lost orders, marked as a Business Insider estimate Amazon disputes and tied to an unreviewed config change rather than AI; March 10, CNBC reports the internal doc's GenAI bullet point was deleted before the deep-dive meeting.](/amazon-says-no-ai-wrote-the-code.diagram.png)

That last outage is where most of the hot takes slid off the road. It had the giant number, so it got pinned on the AI along with everything else. But the careful reporting ties it to a configuration change a human pushed without review, not to any coding tool. Only the March 2 incident has a clean line back to AI. So the distinction everybody skipped is the one Amazon now leans on, and I'll grant it: on the narrow question of who typed the bad change, they're probably right.

In public, Amazon keeps the account short. The December event was "user error, specifically misconfigured access controls, not AI," and Amazon told Fortune (March 12) that "none of the incidents involved AI-written code." The internal version reads less clean. An SVP named Dave Treadwell sent around a memo that blamed "GenAI tools supplementing or accelerating production change instructions, leading to unsafe practices," and admitted the safeguards for that "haven't been fully established yet."

![Panik-Kalm-Panik meme. Top panel, panik: "the outages were caused by AI-written code." Middle panel, kalm: "amazon says no AI wrote a single line." Bottom panel, panik: "the AI just made humans ship it unreviewed."](/amazon-says-no-ai-wrote-the-code.meme.png)

Say they're right on every count. No AI wrote the code that broke. What broke it was that people changed production faster and more confidently than review could keep up with, using tools that made each change cheap to produce and easy to trust. To me that reads less like an exoneration and more like the AI-debt problem in its worse form, the kind that can't be scanned for. A bad line of AI-generated code is at least findable. It sits in a diff, a tool can flag it, a reviewer can catch it, worst case you revert the commit. "We shipped a change nobody really verified" doesn't sit in a file. There's no commit to blame and no pattern to grep for, and a review step that quietly fell behind the pace of change doesn't leave one behind.

Werner Vogels had already named the thing. At his last AWS re:Invent keynote, weeks before the worst of the cluster and on Amazon's own stage, he called it verification debt. AI writes code faster than anyone can read it, he said, and that gap lets software reach production before someone has actually checked what it does. He described the mechanism about a month before his own company ran the experiment on live traffic.

![A quote card. Attributed to Werner Vogels, AWS CTO, re:Invent keynote, December 4, 2025. The quote reads: "AI can generate code faster than you can understand it. That gap allows software to move toward production before anyone has truly validated what it actually does."](/amazon-says-no-ai-wrote-the-code.quotecard.png)

I don't think Amazon is lying about the code. I think the honest account is the one that should worry its engineers more, not less. The 80% weekly AI-usage target it set for them, the two rounds of layoffs (about 14,000 people in October, another 16,000 in January), none of that changes what code gets written so much as how fast it ships and how few people are left to look before it does.

There's one more detail, from CNBC on March 10. The internal incident document had a bullet point that named "GenAI-assisted changes" as a factor, and somebody deleted it before the deep-dive meeting. That's the part I keep snagging on, more than any single outage. Changes go bad all the time. What bothers me is that the record of why this one went bad got pulled before the people who needed it could read it. That deletion is the thing I've been building against. My plugin, debt-ops, hooks a coding agent so that every time it defers a decision or takes a shortcut, a line lands in a markdown file in the repo, dated, off to the side of the agent's own tidy session summary, where the next person trips over it. It even registers debt against its own codebase. Here's a real entry it wrote, trimmed to the load-bearing fields:

```
title:           fingerprint-regex-not-pos
interest:        false positives/negatives vs true features; counts directional only
payoff_trigger:  a real POS tagger becomes worth the dependency
quadrant:        prudent-deliberate
created:         2026-06-07
```

Somebody picked regexes over a proper parser to dodge a dependency, on purpose, for now, and instead of that choice dissolving into a chat log it's a file with a date and the condition that ends it. If you want to try it:

```
/plugin marketplace add bcanfield/agentic-tech-debt
/plugin install debt-ops@agentic-tech-debt
```

It's local-only, stdlib Python, no network calls, MIT. I won't pretend it would have caught Amazon's config change or talked Kiro out of deleting that environment. All it does is keep a paper trail: when a decision gets made in a hurry, a dated line about it shows up in the repo. Someone would have to delete that line on purpose, the way Amazon did with its bullet point, instead of never having written it down at all.

*Cover photo by Jahanzeb Ahsan on Unsplash.*
