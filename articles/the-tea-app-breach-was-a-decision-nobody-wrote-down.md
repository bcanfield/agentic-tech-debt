---
title: "The Tea App Breach Came From an Open Database Nobody Decided to Leave Open"
publishedAt: "2026-06-13"
updatedAt: "2026-06-13"
author: "Brandin Canfield"
series: "Agentic Tech Debt"
summary: "A women's safety app leaked 13,000 government IDs from an open database, and the access check that would have caught it was a choice nobody recorded."
tags: ["ai", "security", "technicaldebt", "vibecoding", "programming"]
image: "/the-tea-app-breach-was-a-decision-nobody-wrote-down.cover.jpg"
---

The Firebase database behind Tea was sitting open on the internet last July, and anyone who found the URL could read all of it. Roughly 72,000 images. Around 13,000 of them government IDs: driver's licenses, selfies people had uploaded to prove they were women, because Tea is a women-only app for vetting men before a date. Past that, 1.1 million-plus private messages. No password, no auth check, no token. Just a bucket you could point a script at and pull down.

That's the part worth sitting with before any of the analysis. The IDs existed because the app asked for proof of identity to keep men out. Then it stored that proof somewhere a man on 4chan could grab the lot in an afternoon. The thing built to protect the users is the thing that doxxed them.

Now the caveat, because it matters to how you read the rest. The widely-repeated attribution (that this was "vibe coding," AI-generated code shipped without a security review) comes from the original 4chan poster and got picked up across the coverage. I haven't seen Tea confirm how the code was written, so don't take "an AI did it" as established. What *is* established is the shape of the failure, and that shape doesn't need an AI to explain it. An open database with no access control is one of the oldest mistakes there is. AI is relevant because it makes this particular mistake faster and quieter to commit, not because it's the only way to commit it.

So set the attribution aside and look at the mechanism. A Firebase database has rules, the layer that says who can read what. Spin a Firestore database up in test mode and it literally writes `allow read, write: if true;` for you, with a banner saying that rule expires in 30 days. It's permissive on purpose, so you can build without fighting the auth layer first, and tightening it is a separate, deliberate step you take before you ship. Somewhere between "let's get this working" and "this is live with real users' driver's licenses in it," that step didn't happen.

![A trace of the read path for a Tea user record. Left: the request a logged-in user makes. Center: the access-control check that should sit between the request and the data, asking "is this caller allowed to read this?", drawn as a gate that was never installed, grayed out and labeled "deferred 'for now,' never recorded." Right: the open Firebase bucket returning 72,000 images and 1.1M messages to any caller. A side note marks the one place the decision to skip the gate could have been written down, and was not.](/the-tea-app-breach-was-a-decision-nobody-wrote-down.diagram.png)

I want to be precise about what kind of failure this is, because "they forgot to secure the database" makes it sound like an oversight, a slip. It's more specific than that. Locking the database down is real work. You write the rules, you test that an unauthenticated request actually bounces, you confirm a logged-in user can't read another user's record. Call it an afternoon, maybe more. Under deadline, with the app already working in the demo, that afternoon is the easiest thing in the world to push to "before launch" and then to "right after launch" and then off the edge of anyone's memory. So I don't read the open database as an accident. I read it as a decision, *we'll lock it down later*, that got made by default and then never got revisited because nothing pointed back at it.

I've made the smaller version of that exact call. Spin up a dev backend with the rules wide open so you can iterate, tell yourself you'll tighten them before anyone real touches it, and then the only record of "open on purpose, fix later" is a thought you had on a Tuesday. I tightened mine before it mattered, but I won't pretend that was discipline. It's the same lapse Tea had, except I never had 13,000 driver's licenses sitting behind the open rule, so the stretch where I forgot about it didn't cost me anything.

That's the through-line I keep finding under these stories, and Tea is the cleanest case of it. The damage doesn't trace to a line of bad code. It traces to a deferral that left no trace. Nobody wrote "shipping with open Firebase rules, must fix before we have real IDs in here" anywhere a person would later trip over it. If they had, the breach is a five-minute conversation in a standup three days before launch instead of 13,000 leaked IDs.

Guillermo Rauch, who runs Vercel, made the dark joke that wrote itself: "On Tea Dating, AI and Vibe Coding security TL;DR: the antidote for mistakes AIs make is... more AI." That's the actual reflex, though: ship faster with the tool, then bolt on a second tool to catch what the first missed. But the gap that sank Tea isn't a gap a smarter model closes. A better code generator still doesn't surface the decision it just made on your behalf. It writes the permissive default, the app works, and the choice to leave the gate off never becomes a thing anyone looked at and signed.

![Two-astronaut "Always Has Been" meme. The front astronaut, looking back at Earth: "wait, nobody wrote the auth check down?" The astronaut behind him, holding a gun: "always has been."](/the-tea-app-breach-was-a-decision-nobody-wrote-down.meme.png)

Here's where I think AI actually changes the math, and it's narrower than the headlines make it. When a human stands up that database, friction works in their favor. They had to go read the Firebase docs. They saw the warning about test-mode rules. The act planted a memory that a security step was still owed. An agent stands up the same database in one motion, default rules and all, tells you it's provisioned, and moves on. The friction that used to leave a mental sticky note is gone. The deferral now happens at the same speed as the success message, and the success message is the only artifact left behind.

Which means the cheapest control that would have caught Tea isn't a scanner or a pen test or another model reviewing the first one's output. It's a note. A line, written at the moment someone chose the permissive default, that says: this is open on purpose for now, here's the condition that ends that (real user data lands in it), here's where it lives. One sentence in a file checked into the repo, where the next person would see it, or the same person a month later, the night before launch. Tea never had that sentence anywhere, which is the whole reason the rule stayed open into production.

That's the thing I've been building toward with debt-ops. It hooks a coding agent and writes each deferred decision to a markdown file the agent's "database provisioned" summary never mentions, so a choice like *leaving auth off for now* lands somewhere a person can find it before launch instead of evaporating into a green checkmark.

The repo is [github.com/bcanfield/agentic-tech-debt](https://github.com/bcanfield/agentic-tech-debt). To be clear about its limits: it doesn't write secure rules, and it can't tell a permissive default from a deliberate one. All it does is turn the silent choice into a line of text on the way to launch, the kind of line you have to read and dismiss on purpose rather than never see at all. For Tea, that line would have been sitting in the repo the whole time, next to a database holding 13,000 driver's licenses, waiting for anyone to walk past it.

*Cover photo by Michael Chacon on Unsplash.*
