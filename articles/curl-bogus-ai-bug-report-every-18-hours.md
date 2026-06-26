---
title: "The curl Bug Report That Cited a Function That Doesn't Exist"
publishedAt: "2026-06-11"
updatedAt: "2026-06-11"
author: "Brandin Canfield"
series: "Agentic Tech Debt"
summary: "How AI-generated bug reports turned curl's bounty into a denial-of-service attack, and who actually pays for code an agent never had to understand."
tags: ["ai", "opensource", "technicaldebt", "security", "programming"]
image: "/curl-bogus-ai-bug-report-every-18-hours.cover.jpg"
---

Somewhere in curl's bug-bounty queue last year sat a confident, well-formatted report about an HTTP/3 vulnerability. It walked through the flaw, named the affected function, suggested a fix. The only problem was the function. It does not exist in curl. It never has. An AI had written a plausible security report about code that was never in the project, and a human had to read far enough to figure that out before it could be thrown away.

That report is one of thousands, and by this month it's barely notable. As I write this in June 2026, curl receives a bug report roughly every eighteen hours. Most are not real. Daniel Stenberg, who has maintained curl for going on three decades and personally triages a lot of that queue, has been keeping count. Around one in five submissions now carries the telltale signatures of AI slop. Around one in twenty is a genuine vulnerability. The rest is the wide middle: reports that look real enough to demand a human's time and turn out to be nothing.

For years the queue was a trickle a careful person could keep up with. Then in 2025 the volume more than doubled, to about one report every forty-eight hours, and the HTTP/3 report with the imaginary function lands somewhere in that stretch. By the end of January 2026 Stenberg had had enough and shut the bounty down. His phrasing got passed around a lot: "We are effectively being DDoSed. If we could, we would charge them for this waste of our time."

The bounty reopened in March 2026 once the slop tide pulled back. So this isn't a clean "AI killed the curl bug bounty" obituary. It's worse in a quieter way: the program came back, the volume climbed again, and by June it had doubled a second time, to the eighteen-hour cadence we're at now. The shutdown bought a few months of relief, then the water rose to a new high-water mark.

![A dated timeline of curl's bug-bounty volume: a reviewable trickle through 2024, doubling to one report every 48 hours in 2025, the late-January 2026 shutdown, the March 2026 reopening, and a second doubling to one every 18 hours by June 2026; alongside the ratio of ~20% AI-slop submissions to ~5% genuine vulnerabilities.](/curl-bogus-ai-bug-report-every-18-hours.diagram.png)

The obvious counter, and it's a fair one: bad bug reports are not new. Maintainers have eaten low-effort, wrong, copy-pasted reports forever, and the bounty even pays people to send them. So what changed, beyond the count going up?

What changed is who's holding the cost of being wrong.

A human submitting a junk report at least had to write it. They spent their own minutes producing the thing, which capped the rate and meant a person had at some point looked at the words. The AI report severs that. Generating a confident, fully-formatted vulnerability write-up dropped to roughly zero. Checking whether it's true did not. Verifying that an HTTP/3 function exists still takes a human who knows curl, opening the source and confirming a negative. That work didn't get cheaper. It got moved — off the submitter, onto Stenberg, who now bears all of it.

We have a name for this: an externality. The submitter gets the upside, a payout or just the dopamine of having "contributed," and the maintainer absorbs the cost. Nobody decided it. The cost was simply shifted, one cheap report at a time, the way a road fills with traffic.

My own project handed me a miniature version, and it embarrassed me enough to stick. I build a tech-debt plugin that hooks coding agents, and one of its hooks scans for the markers people leave when they cut a corner: `TODO`, `FIXME`, that family. Except when I'm writing articles *about* tech debt, the prose is full of the literal strings "TODO" and "FIXME," and my own hook started counting them as real debt and nagging me to register it. One session it escalated across three stops — eight phantom markers, then thirteen, then twenty, none of them real, each demanding a moment of my attention to confirm it was nothing. A tool I wrote was generating false reports and handing them to me to disprove. I filed the bug against my own repo and added a rule to skip prose files. Trivial fix. But the feeling stuck: there is something uniquely deflating about being made to adjudicate noise a machine produced for free. Now multiply that by real money and real CVEs hiding somewhere in the pile, on a queue that doubles every few months.

![The "they're the same picture" meme: panels labeled "a real vuln report" and "an AI report citing a function that doesn't exist," with the punchline that they trigger the same triage hour.](/curl-bogus-ai-bug-report-every-18-hours.meme.png)

We keep measuring AI by how fast it produces output. The number that actually matters is what it costs someone downstream to verify that output is real, and AI is very good at producing things that are expensive to verify and cheap to make. A bug report. A pull request. A function cast to `any` to quiet the type checker. The generation got cheap and the checking didn't, and the gap has to land on a human somewhere. curl's queue is just the most legible version, because the bill arrives addressed to one named person every eighteen hours.

I write a plugin called debt-ops for the in-the-codebase version of this, and it makes an agent record the decisions it defers, so the cost lands somewhere a person can see it instead of silently accruing. It would do nothing for Stenberg's inbox; a bounty queue is a different surface than a repo, and I'm not going to pretend otherwise. But it comes from staring at the same asymmetry he's describing, from inside the source tree instead of the issue tracker. If that asymmetry nags at you too, the code's at [github.com/bcanfield/agentic-tech-debt](https://github.com/bcanfield/agentic-tech-debt).

The HTTP/3 report is still my favorite artifact from this mess, in a bleak way. An AI invented a vulnerability in a function that was never written, and the system worked exactly as designed: the report was read by a person, checked against the source, confirmed bogus, and closed. Everything functioned. It just cost a curl maintainer an hour to establish that nothing had happened. Do that every eighteen hours, forever, and tell me who's being served.

*Cover photo by Christa Dodoo on Unsplash.*
