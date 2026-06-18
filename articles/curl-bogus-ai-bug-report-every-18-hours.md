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

Somewhere in curl's bug-bounty queue last year sat a confident, well-formatted report about an HTTP/3 vulnerability. It walked through the flaw, named the affected function, suggested a fix. The only problem was the function. It does not exist in curl. It never has. An AI had written a plausible security report about code that was never in the project, and a human being had to read far enough to figure that out before he could throw it away.

That report is one of thousands, and by this month it's barely even notable. As I write this in June 2026, curl receives a bug report roughly every eighteen hours. Most of them are not real. Daniel Stenberg, who has maintained curl for going on three decades and personally triages a lot of that queue, has been keeping count. Around one in five submissions now carries the telltale signatures of AI slop. Around one in twenty is a genuine vulnerability. The rest is the wide middle: reports that look real enough to demand a human's time and turn out to be nothing.

Here is how it got to eighteen hours.

For years the queue was a trickle a careful person could keep up with. Then in 2025 the volume more than doubled, to about one report every forty-eight hours. The HTTP/3 report with the imaginary function lands in that stretch. By the end of January 2026 Stenberg had had enough and shut the bounty down. His phrasing, which got passed around a lot, was blunt: "We are effectively being DDoSed. If we could, we would charge them for this waste of our time."

He didn't say spammed or trolled. He reached for DDoSed, the term for a system knocked over not by any single malicious request but by the sheer arithmetic of too many requests, each cheap to send and expensive to absorb. No individual AI report is an attack. The aggregate is.

Then it got stranger. The bounty reopened in March 2026, once the slop tide pulled back a little. So this isn't a clean obituary, "AI killed the curl bug bounty," and I want to be careful not to write it as one. It's worse in a quieter way. The program came back, the volume climbed again, and by June it had doubled a second time, to the eighteen-hour cadence we're at now. The shutdown wasn't the disaster. The shutdown was a maintainer pulling a fire alarm, getting a few months of relief, and then watching the water rise to a new high-water mark. curl wasn't alone, either. Mitchell Hashimoto banned AI-written code from Ghostty around the same period; Steve Ruiz set tldraw to auto-close external pull requests; RedMonk's Kate Holterhoff started calling the whole thing "AI Slopageddon," which is funny until you're the one reading the queue.

![A dated timeline of curl's bug-bounty volume: a reviewable trickle through 2024, doubling to one report every 48 hours in 2025, the late-January 2026 shutdown, the March 2026 reopening, and a second doubling to one every 18 hours by June 2026; alongside the ratio of ~20% AI-slop submissions to ~5% genuine vulnerabilities.](/curl-bogus-ai-bug-report-every-18-hours.diagram.png)

Now, the obvious counter, and I think it's a fair one: bad bug reports are not new. Maintainers have eaten low-effort, wrong, copy-pasted reports forever. The bounty even creates an incentive to send them, because there's money at the end. So what changed, really, beyond the count going up?

What changed is who's holding the cost of being wrong.

A human submitting a junk report at least had to write it. They spent their own minutes producing the thing, which capped the rate and, more to the point, meant a person had at some point looked at the words. The AI report severs that. The cost of generating a confident, plausible, fully-formatted vulnerability write-up dropped to roughly zero. The cost of checking whether it's true did not drop at all, and that's the load-bearing detail. Verifying that an HTTP/3 function exists still takes a human who knows curl, opening the source, and confirming a negative. That work didn't get cheaper. It got moved. It moved from the person filing the report, who used to bear at least the writing of it, onto Stenberg, who now bears all of it.

It has a name we already use elsewhere: this is an externality. The submitter gets the upside, maybe a payout, maybe just the dopamine of having "contributed," and the maintainer absorbs the cost. Nobody decided this. Nobody filed a ticket that said "we will now route the verification burden for all generated security research onto unpaid open-source maintainers." It just became true, one cheap report at a time, the way a road fills with traffic.

And you can't triage your way out of it cheaply. The whole reason a slop report costs an hour is that you can't know it's slop until you've spent most of the hour. The good ones and the fabricated ones arrive looking identical; the imaginary HTTP/3 function was buried inside a report that was written to read, on its surface, exactly like a real one. So you can't skim and discard. Discarding *is* the work. Stenberg is paying full triage price to learn that the report was worth nothing, which is the same price he'd pay if it were worth everything.

![The "they're the same picture" meme: panels labeled "a real vuln report" and "an AI report citing a function that doesn't exist," with the punchline that they trigger the same triage hour.](/curl-bogus-ai-bug-report-every-18-hours.meme.png)

My own project handed me a miniature version of the same thing, and it embarrassed me enough to stick. I build a tech-debt plugin that hooks coding agents, and one of its hooks scans for the markers people leave when they cut a corner: `TODO`, `FIXME`, that family. Sounds reasonable. Except when I'm writing articles *about* tech debt, the prose is full of the literal strings "TODO" and "FIXME," and my own hook started counting them as real debt and nagging me to register it. One session it escalated across three stops, eight phantom markers, then thirteen, then twenty, none of them real, every one demanding a moment of my attention to confirm it was nothing. A tool I wrote was generating false reports and handing them to me to disprove. I filed the bug against my own repo (the irony of registering "my debt tracker invents debt" was not lost on me) and added a rule to skip prose files. Trivial fix. But the feeling was instructive: there is something uniquely deflating about being made to adjudicate noise a machine produced for free. Now multiply that by a real bounty, real money, real CVEs hiding somewhere in the pile, and a queue that doubles every few months. That's Stenberg's Tuesday.

Here's the frame, and it's the through-line of everything I've been writing about agentic code. We keep measuring AI by how fast it produces output. The number that actually matters is what it costs someone downstream to verify that output is real, and AI is very good at producing things that are expensive to verify and cheap to make. A bug report. A pull request. A function cast to `any` to make the type checker quiet. In every case the generation got cheap and the checking didn't, and the gap between those two costs has to land on a human somewhere. curl's queue is just the most legible version, because the bill arrives addressed to one named person every eighteen hours.

I write a plugin called debt-ops for the in-the-codebase version of this problem — it makes an agent record the decisions it defers, so the cost of those deferrals lands somewhere a person can see it instead of silently accruing. It would do exactly nothing for Stenberg's inbox; a bounty queue is a different surface than a repo. I'm not going to pretend otherwise. But it comes from staring at the same asymmetry he's describing, just from inside the source tree instead of the issue tracker. If that asymmetry is the thing nagging at you too, the code's at [github.com/bcanfield/agentic-tech-debt](https://github.com/bcanfield/agentic-tech-debt).

The HTTP/3 report is still my favorite artifact from this whole mess, in a bleak way. An AI invented a vulnerability in a function that was never written, and the system worked exactly as designed: the report was read by a person, checked against the source, confirmed bogus, and closed. Everything functioned. It just cost a curl maintainer an hour to establish that nothing had happened. Do that every eighteen hours, forever, and tell me who's being served.

*Cover photo by Christa Dodoo on Unsplash.*
