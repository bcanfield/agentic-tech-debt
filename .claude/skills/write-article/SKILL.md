---
name: write-article
description: Write or revise a public article for the debt-ops content pipeline — humanlike prose, grounded in the repo's research docs, tuned to convert readers into repo visits. Use whenever the user asks to write, draft, edit, or punch up an article, blog post, essay, or "day N" piece, gives a headline number from the content calendar, or mentions dev.to / Hacker News / blog content for this project. Any public-facing article must go through this skill, never freehand.
---

# Write an article

Every article exists to do two things, in this order:

1. **Never read as AI-written.** One reader smelling slop costs more than ten readers converting. The audience is developers — the most AI-tell-literate readers on earth — and several distribution targets explicitly ban AI-generated content.
2. **Convert.** The win condition is a click through to github.com/bcanfield/agentic-tech-debt, ideally a star or an install. Not applause. Not completeness.

These trade off against polish, not against each other. The same things that make prose read human (specifics, opinion, admitting what you don't know) are the things the research says convert developers.

## Step 1 — Gather before drafting

- **Find the piece** in `docs/ai-tech-debt-headlines.md` (by number or topic). Note the headline, angle, anchor source, and persona tag.
- **Pull every fact from `docs/ai-tech-debt-stories.md`.** It is the only source of claims, stats, and quotes. If a number isn't in there, the article doesn't get it. Never round a stat into a nicer one, never paraphrase a quote.
- **Check `docs/ai-tech-debt-release-order.md`** for slot context: is this part of the Amazon Monday series? A `⟂ pair` with yesterday's piece? A BOFU slot? A date peg? Series pieces should reference their siblings by name in prose (never as a link — see the one-link rule); pair pieces shouldn't repeat the partner's material.
- **Carry the caveats inline.** The stories doc's Caveats section is mandatory, not optional color: vendor studies named as vendor research, the Amazon 6.3M figure always "a Business Insider estimate Amazon disputes," METR always n=16 with early-2025 models. Stating the weakness of your own evidence is what lets the piece survive a hostile HN thread — and the release order was built on "credibility before virality."
- **Date discipline.** Write relative to the publish date, not today. GitClear's 8x duplication rise happened during 2024 — never "last year." curl's bounty reopened in March 2026, so the shutdown can't be the headline event.

## Step 2 — Pick the shape

Four pillars, four shapes. The voice and the CTA depth are properties of the shape — don't mix them.

### Incident pieces (Pillar 2) — first person, story-shaped

Open inside the event. Not "In July 2025, an incident occurred at Replit" — open on the agent's own confession, the deleted database, the day-9 timestamp. No scene-setting paragraph; trust the reader to catch up.

Then: chronology with receipts (dates, quotes, what the principals actually said), and then **the turn** — the thing other coverage of this incident missed, which for us is always some version of: *a decision got deferred and nobody wrote it down.* That's the debt-ops thesis arriving on its own legs. Don't name the product before the turn.

CTA: one short paragraph near the end. "Stories like this are why I built [debt-ops]" plus the one-line install, and stop. 800–1,200 words.

### Data pieces (Pillar 3) — editorial, the number does the work

Open with the stat translated into the reader's life ("of the last hundred functions your agent wrote, forty-five have a hole in them"), then what the study *actually* measured in two or three sentences — methodology is credibility, and these pieces are the credibility layer of the whole calendar. Give the caveat its own honest sentence; it's load-bearing. Close on what the reader should check in their own repo this week.

CTA: the lightest touch in the whole system — one sentence, or zero if it doesn't fit naturally. Data pieces earn the trust the playbooks spend. Forcing a pitch here spends it instead. 600–1,000 words.

### Thesis essays (Pillar 1) — editorial with a spine

First sentence is the claim. Not a question, not context — the claim. Argue it with specifics borrowed from the incident and data pieces (name the already-published ones in prose — never link them; see the one-link rule). Concede the strongest counterargument for real, not as a strawman to knock down. End when the argument ends — cornerstone essays don't need a summary, they need a last sentence that sticks.

These can take a stated "I think" where it's genuinely an opinion, but they're essays, not diary entries. CTA: one problem-framed sentence near the end ("this is the gap debt-ops exists to close"), linked. 900–1,400 words.

### Playbooks (Pillar 4, BOFU) — first person, the tool is the subject

Problem in two paragraphs, max. Then **teach the manual version first** — real commands, real grep patterns, a workflow the reader can run today with zero installs. It has to genuinely work standalone; that honesty is what makes the closing automation pitch land instead of reading as bait.

Then the pivot — "or let a hook do this every time" — and show the plugin doing the same thing with real output (the `+1 entry: as-any-checkout-payload (A)` line, actual registry frontmatter). When the tool enters, the trust block enters with it, plainly: local-only, stdlib Python, no network calls, no telemetry, MIT. That disclosure is our strongest asset — the one plugin that got torched on HN died for undisclosed server calls.

The install command appears exactly as it works:

```
/plugin marketplace add bcanfield/agentic-tech-debt
/plugin install debt-ops@agentic-tech-debt
```

1,200–2,000 words is fine here; playbooks are the one shape where length reads as generosity.

## Cut to the key points — write for the shortest attention span ever

Reader attention is the scarcest thing in the system, scarcer than any stat or kicker. Three dense paragraphs stacked with no break and the skimmer is gone before your best line lands. Assume every reader is one scroll from leaving, and that the back half of any piece loses readers the front half kept. The job isn't to say everything true about the topic — it's to land a few things so cleanly the reader can't not finish.

So before you polish, find the spine: **what are the two or three things this piece must get across?** Write those, then treat everything else as a candidate for the cut. The test for a paragraph isn't "is it good?" — it's "does the piece break if it's gone?" If not, cut it. A 700-word version that lands all three points beats an 1,100-word version that also makes four more — the four extra didn't add reach, they buried the three that mattered.

- **Aim at the low end of every range in Step 2; the high end is a ceiling you earn, not a target.** A draft that comes in 200 words under and loses nothing is the win, not one padded to the middle. The current series runs 1,000–1,900 words — most of those should be shorter.
- **Kill the throat-clearing.** Scene-setting first paragraphs, "it's worth noting," the sentence that restates the last paragraph, the second example that proves what the first already proved. The opening paragraph is the most common thing to cut whole — claim-first openings (Step 2) exist partly so there's nothing to clear.
- **Most paragraphs shorter than you'd default to, one idea each.** A one-line paragraph between two dense ones is the rest stop a skimmer needs — that's the same break-the-wall job the diagram, meme, and tables do, done with whitespace.
- **Concise ≠ compressed.** Cutting words and whole paragraphs is the goal; turning every survivor into a kicker is the *opposite* failure, the one "The register" warns about. The minimal article is fewer words and *plainer*, not fewer words and punchier. Playbooks stay long where length is reference value — but even there, density and skimmability still apply; long is not the same as padded.

## Conversion mechanics (what our research actually found)

From `docs/one-star-a-day.md` and `docs/publishing-checklist.md`:

- **Problem framing beats product framing.** "Claude Code plugin"-framed Show HNs scored 2–9 points; problem/outcome framing scored 100–500. The article is about the reader's problem; the tool is the epilogue.
- **Personal-story framing got roughly 3x the engagement** of dry technical description. This is why incidents and playbooks are first person.
- **Disclose self-interest, plainly.** "I built this, so weigh that" reads as honesty to developers and buys more trust than feigned neutrality. Same logic as labeling vendor studies.
- **Every article opens with the repo masthead — required, verbatim, no exceptions.** The first body element, before the opening line, identical on every piece:
  ```
  > **Full research and the plugin →** [github.com/bcanfield/agentic-tech-debt](https://github.com/bcanfield/agentic-tech-debt)
  ```
  It's a standing banner, not the CTA: the warm reader who arrived to find the repo gets the link in line one, and because it's identical across the series it reads as masthead furniture rather than a per-article pitch. Don't reword it, don't move it below the fold, don't add a second one, don't let it absorb the article's actual CTA work.
- **One link in the body besides the masthead, and it's the same repo.** The repo *is* the landing page. Past the masthead, the prose gets at most one repo link (the in-context CTA, depth per the shape), and nothing else is ever linked — not a marketing site, not your sibling articles, not the studies and incidents you cite (name those in prose). Relative/local file links (`./other-piece.md`) especially: they break on the blog, so a sibling reference is always plain text. Don't scatter links, never ask for stars — the research is unambiguous that begging and engagement-farming backfire in this exact niche.
- **Readers arrive warm or cold by slot.** Week-1 and BOFU readers come from the README — peak intent, give them the next step fast. Data-piece readers are cold — let them leave impressed and unbothered.

## The headline — open a gap, then pay it off

The headline is the only line most people read, so it carries the whole click, and it has two jobs that pull against each other: *earn* the click and survive a tell-literate skeptic. The defensive half is below in "Sounding human" ("The headline gets the strictest pass"). This is the offensive half, and the two are one coin — a title that opens a gap but does it as a negative-parallelism kicker fails both.

What earns a developer's click is a **curiosity gap** (Loewenstein's information gap: the space between what the reader knows and what they want to know), sized right. Too small — the title states the whole finding — and there's nothing to learn, no click. Too large — the title says nothing concrete — and there's no foothold; to a developer that reads as bait and they bounce.

- **Concrete foothold + exactly one thing withheld.** The foothold is a real number, a named entity, a specific oddity, or concrete stakes — *the same specificity that beats AI tells and signals you did the work* (numbers imply research; "cited a function that doesn't exist" implies a real story). Withhold the why, the mechanism, the consequence, or the turn — that's the gap. "The curl Bug Report That Cited a Function That Doesn't Exist" hands you the oddity and withholds the scale and the cost.
- **More specific is not more clickable — past a point it's less.** The counterintuitive finding from the largest headline study (a meta-analysis of ~9,000 experiments): concreteness has a sweet spot, and it's *relative to the feed*. When competing titles are already concrete — which is exactly the dev-blog feed — piling on more detail *reduces* clicks (−9.9% in that regime; the +5.5% gain only appears when the surrounding titles are vague). So the move here isn't to cram every figure in. One sharp hook, one clean gap. Don't stack three footholds and don't bury the best one.
- **Descriptive beats vague, and the gap has to pay off.** Even Upworthy's own data turned against pure curiosity-gap bait; developers turn on it harder. A title that withholds everything ("This One Pattern Will Change How You Write Code") buys a click the first paragraph can't honor, and an unpaid gap costs more than the click was worth — same math as "one reader smelling slop costs more than ten converting." Claim-first openings (Step 2) exist partly so the gap closes in sentence one.
- **Lead with the number when the number is the finding.** If the genuine result is a figure — 8x, 13,000 IDs, a report every 18 hours — put it up front; it's foothold and credibility in one. Exactly one, the load-bearing one. (HN is the exception: it strips "gratuitous numbers" and editorializing to a neutral label, so the HN *submission* title leans plain-descriptive — that's the existing Show HN guidance, and channel variants stay a separate task. The gap-with-foothold title is the lever on dev.to, Hashnode, Medium, and the blog.)
- **Match the foothold to the pillar.** Incident → the arresting specific detail, or the confession in the principal's own words. Data → the number and what's counterintuitive about it. Thesis → the claim that inverts an assumption the reader holds. Playbook → the outcome and the method, problem-framed not product-framed ("Catch the debt your agent writes, with grep and a folder of markdown," never "Introducing debt-ops"). Same 100–500-vs-2–9 problem-framing split from Conversion mechanics, applied to the title.

## Sounding human — the part that decides everything

If the **humanize** skill is available, apply it in full and run its audit, including `check_tells.py`, on the finished draft. Its catalog is the authority. The highest-stakes subset for these articles:

- **Structure tells kill first**: negative parallelism ("it's not X, it's Y"), rule-of-three triplets, em dashes past the second one, rhetorical reveals ("The result? Disaster."), question-format headings, every paragraph ending on a tidy bow, symmetric bold-headed bullets.
- **Rhythm**: vary sentence length hard — a 30-word sentence, then a 4-word one. Contractions. Starting with And, But, So. One-line paragraphs.
- **Content**: every few paragraphs should contain a sentence only someone who did this work could write. Specifics over adjectives, a position over balance, discomfort allowed.

And go further than humanize does — these are articles, and **too perfect is its own tell**:

- **Leave something rough.** A parenthetical aside that wanders for a beat. A gripe. A question the piece raises and admits it can't answer. Sections of visibly unequal length. Readers trust writing with one loose thread more than writing with none.
- **Don't be exhaustive.** Covering 80% of the angle with a personality beats covering 100% of it like a survey. Cutting your third-best point is a feature.
- **Few headings.** Incidents and essays often need zero H2s. Playbooks get headings because readers skim them for steps. When you do use headings, sentence case, and never "Introduction" or "Conclusion."
- **The headline gets the strictest pass of anything you write.** It's the most-visible line in the article and the first thing a tell-literate reader judges — a structure tell in the body costs you one skeptic mid-read; the same tell in the headline costs you the reader before they start. So soften it there even when the headlines doc ships it that way: the doc title is a working claim, not final copy. Negative parallelism is the usual offender ("Tech Debt Isn't the Problem. Invisible Debt Is." → "The Tech Debt Nobody Wrote Down"); so are question headlines, rule-of-three, and the colon-and-buzzword ("AI Debt: The Silent Killer"). Keep the thesis, drop the shape. This is the defensive half — "The headline — open a gap, then pay it off" above is the offensive half; both must hold at once.
- **It's fine to hedge when you're genuinely unsure** ("I think the second number matters more, but I keep going back and forth") — that's a human move. Hedging every claim is the AI move.
- **Never fake flaws**: no manufactured typos, no forced slang. Stilted-casual reads worse than clean.

Voice reference: the README and CLAUDE.md of this repo — plain-spoken, concise, a little dry. The author is a solo dev building debt-ops in public, not a content team.

## The register — coworker, not keynote

Dodging the obvious tells creates a second failure mode: over-compression. The draft starts performing. Every paragraph closes on a quotable line, claims get issued like laws of physics, and fragments get deployed for drama. ("The agent owned the seconds. The months were everybody else's." — a real line from a draft this skill produced. Good kicker. But the same draft had seven more like it.) Written-to-impress is its own tell, and it's exhausting by word 600. The target register is a sharp coworker explaining something at lunch — they land a good line occasionally, almost by accident, and the rest is just them telling you the thing.

- **One kicker per article, max.** A kicker is any sentence that wants to be quoted: a balanced antithesis (seconds/months, cheap/expensive, "taxes your engineers and your tooling"), an inversion, a mic-drop fragment. Spend it on the ending or the turn. Everywhere else, end the paragraph on plain information and let it sit.
- **Count your paragraph endings — don't trust your ear.** Every eval round, the writer believed it kept one kicker and an independent reader counted four or five: you cannot hear your own epigrams. So make it mechanical in the audit: list the final sentence of every paragraph; pull-quote-test each ("would this work on a conference slide?"); if more than two qualify, rewrite the rest to end on the plainest fact in the paragraph. Ending a paragraph on data, a quote, or a shrug is not a failure — it's what the human exemplars do most of the time.
- **Sweeping claims need an owner or a source.** "Capability isn't behavior" and "that premise died two years ago" are oracle voice — nobody is saying them, so nobody can be wrong. Convert to a person making a fallible observation ("as far as I can tell, capability hasn't translated into behavior — refactoring fell anyway") or hang them on the data directly. Two unowned pronouncements per piece is already pushing it.
- **Fragments are a spice, not a rhythm.** "A sentence." "No changes." One or two per article for genuine emphasis. When punch-elaboration-punch becomes the default paragraph shape, the prose has a beat you can dance to, and that's a fingerprint.
- **Vary sentence *shape*, not just length.** Some sentences should start with a subordinate clause. Some should ramble a little and recover. A lot should be plain subject-verb-object that delivers a fact and moves on. If every sentence is load-bearing, none of them are.
- **Let the facts carry the drama.** The Replit story doesn't need present-tense narration or staged reveals — an agent deleted a production database during a code freeze and then apologized for it. Flat delivery makes a dramatic fact hit harder; dramatic delivery makes it feel produced.

## The discourse skeleton — the deepest tell

After the sentences are clean and the register is right, a piece can still read AI because of how the *argument* is built. These are discourse-level patterns; no sentence-level audit catches them.

- **Don't announce your moves.** "That's an anecdote, so here's the data." "The strongest objection to all of this is…" "I have two reasons, and I hold them with different confidence." "Here's what I'll commit to." That's a model narrating its own outline. Make the move; skip the narration. The data can just arrive. The objection can just be raised.
- **Dwell unevenly.** A model gives every point its fair ~100-word paragraph. A person spends three paragraphs on the one detail that hooked them and waves at something bigger in half a sentence. Pick the thing in this piece that genuinely interests you and over-invest in it; compress something a fair essay would expand. Lopsided coverage reads researched-by-a-person.
- **One digression is allowed — encouraged — per piece.** A short detour that doesn't advance the thesis but is interesting enough to keep. Perfectly efficient argumentation is a tell; humans keep sentences because they like them.
- **Vary the citation delivery.** Stat → vendor caveat → interpretation is the responsible move, and running it four times in a row is a tic. Sometimes full attribution, sometimes a parenthetical, sometimes "there's a McKinsey number on this — about two-thirds faster — though it's from 2023." (The caveats themselves stay; only the delivery varies.)
- **Watch for tics this skill creates.** Any move repeated three times is a fingerprint, *including the ones taught here*: the calibrated-uncertainty aside ("I go back and forth"), the lunch-argument hedge, the owned-anecdote opener. One each, max. The audit should hunt for whatever this draft's repeated move is, not just the catalog's.
- **Not every paragraph opens with a topic sentence.** Some should start mid-thought, on a detail, and find their point on the way out.

## Steal reality from the repo — the unfakeable layer

Generic first person ("I feel this most on agent-heavy days…") is ghost-writer prose: plausible for anybody, checkable by nobody. The cheapest cure is that this author has a real repo. Before drafting, pull one or two real artifacts and build the first-person material from them:

- Actual entries in `docs/debt/` — real slugs, quadrants, body text (this repo registers debt against itself, including bugs in its own hooks).
- Real tool output, generated fresh: the `+1 entry: as-any-checkout-payload (A)` line from the demo scene, a `review.py` report against this repo.
- The repo's own history: `git log`, the ADRs — including ADR 0014, which *reverses* an earlier plan. A project documenting its own reversals is exactly the lived texture a model can't fake.
- Countable facts: lines of stdlib Python, number of registered entries, number of adapters kept in sync by hand.

Run the command, quote what came back, never invent or embellish what it says. One checkable artifact does more anti-AI work than ten style passes — it's "the sentence only this author could write," made literal.

## Break up the wall — visualizations that carry content

A screenful of unbroken gray text is its own kind of off-putting, and on dev.to or a blog the skimmer bounces before the prose gets a chance. But the fix is *not* decorative formatting — bold sprinkled for emphasis, a callout for drama. That reads as AI dressing and trips the structure tells above. The fix is a visualization that carries information the prose would otherwise spell out, so a skimmer gets it at a glance and a close reader gets a second angle. Specific, checkable visuals do the same anti-AI work as a real repo artifact: a model fakes a vibe, not a timeline with real dates.

**The hard rule: never more than two prose paragraphs in a row without a visual between them, and at least three committed images per article.** `meme_check.py` (Step 3) enforces both — it's not left to the eye. A *visual* that breaks a run is a committed image, a fenced code block, a table, a blockquote, or a heading. But the three required images carry the load, and in incident/data/essay pieces — which have almost no code — an image is the *only* thing that breaks a run, so there the rule lands as: an image every two paragraphs. Playbooks lean on their native code blocks and tables, which is why the gate counts those too.

The trap this sets is decoration, exactly the tell the rest of this section warns against, so it's paired with a second constraint that defuses it: **every one of those images carries content the prose doesn't.** When a run runs too long you have two honest fixes and one forbidden one. Honest: add a rendered image that teaches something the text only implies, or **cut prose until the run closes** — a wall of gray is often a wall because three paragraphs are saying what one could (this is the concision pass from "Cut to the key points," doing double duty). Forbidden: drop in a decorative image to hit the counter. If you can't make the gap-filler carry content, that's the signal to cut, not to dress.

Match the visual to the pillar — don't reach for one the content doesn't want:

- **Incidents** — a chronology with real timestamps reads well as a compact timeline (the Replit nine-day arc, day by day). Let a load-bearing quote stand on its own line.
- **Data** — where a table earns its place: the study's numbers side by side, before/after, your-repo vs. the cohort. One honest table beats three paragraphs walking the same figures, and it sets the caveat right next to the number it qualifies.
- **Essays** — the least formatted otherwise; the argument is the structure. The one mandatory diagram (see "The diagram" below) is usually a single mechanism or a 2×2 — make it the diagram that's genuinely worth a paragraph.
- **Playbooks** — already visual: real commands in fenced blocks, real tool output, registry frontmatter. A manual-workflow-vs-hook before/after is a natural table.

So it doesn't become the tell:

- **Every visual carries content the prose doesn't.** If a table just restates a sentence, cut the table. Decoration is the tell; information is the cure.
- **Bold is for load-bearing terms, used rarely** — the phrase a skimmer must catch, a real command, a term you're defining. Not emphasis the sentence already carries, and never the same bold pattern in every section (symmetric bold-headed bullets are still the first tell to die).
- **Don't formalize what's better as prose.** A two-item comparison is a sentence. A three-step process the reader runs once is a sentence. Reach for structure only when the content is genuinely structured.
- **Vary it.** If every section has a table they become wallpaper. One visual the content actually wanted beats one per section.
- **Render everything, hotlink nothing.** Tables and fenced code blocks render everywhere the article ships; the one custom diagram (next section) is a PNG we build and commit, not a hotlink. Never link an image you can't produce — committed file or it doesn't go in. (Skip ASCII diagrams: they break alignment across fonts and wrap on mobile. The committed diagram is where structure goes now.)

## The diagram — one custom render per article

Every article ships **at least one** custom rendered diagram — not optional, the same standing requirement as the cover. It's the analytical one of the **three committed images every article now carries** (diagram + meme + a third anchor — see "Break up the wall" for the count and "The third anchor" below for the free slot). Committed next to the piece as `<slug>.diagram.png` (mirrors the cover's `<slug>.cover.jpg`) and referenced inline in the body where the argument wants it. This is the *rendered* diagram, separate from any inline tables or code blocks (those still follow the "vary it, don't make wallpaper" rule above) — and it has to carry content the prose doesn't, held to every rule in "Break up the wall": matched to the pillar, teaching something the text only implies, rebuilt if it just restates a sentence.

Why a rendered PNG and not ASCII: we author the HTML and screenshot it ourselves, so it stays a checkable artifact — real labels, real dates, real numbers — not an AI-generated image, which is the thing the cover section forbids. It just holds structure ASCII can't (a clean 2×2, a dated timeline, a before/after) and renders identically everywhere the article ships.

Build it the way the cover gets built — produce the file, don't hotlink:

1. Hand-author a self-contained HTML file (CSS grid/flex, no external assets, no CDN fonts) at `articles/diagrams/<slug>.html` — one `#card` element holds the whole diagram. Real content only; pull the labels/figures from `docs/ai-tech-debt-stories.md` like any other claim.
2. Render + screenshot it to the committed PNG via the Playwright MCP. The browser blocks `file://`, so serve the dir first (`python3 -m http.server`), navigate to `…/<slug>.html?scale=2` (2× = retina-sharp), and screenshot the `#card` target to `articles/<slug>.diagram.png`. Full steps live in `articles/diagrams/README.md` — follow them, don't reinvent the dance.
3. `Read` the PNG back. A broken grid is visible at a glance, and that look *is* the validation — there's no schema to check, the render either holds or it doesn't.
4. Reference it inline with descriptive alt text: `![<what it shows, in plain words>](/<slug>.diagram.png)` (root-relative, same as how the frontmatter `image` resolves the cover).

Match the diagram to the pillar like any other visual: a dated timeline for incidents, a numbers-side-by-side grid for data, a single mechanism or 2×2 for essays, a manual-vs-hook before/after for playbooks.

## The meme — the other required visual

Every article also ships **exactly one meme**, committed as `<slug>.meme.png` and referenced once in the body. The diagram, the meme, and the third anchor are the three required body images, and together they break up the wall: the diagram sits where its subject is discussed, but a joke can go anywhere it's relevant, so **the meme is the most movable one** — it goes in an empty stretch the text has left. `meme_check.py` (Step 3) fails the publish if the meme is missing or doubled, if the body carries fewer than three images, or if any prose run exceeds two paragraphs.

This is the skill's one sanctioned piece of decoration, so it clears a high bar or it reads as exactly the AI dressing "Break up the wall" warns about:

- **Illustrate one beat, not the topic.** The thesis isn't memeable; a specific moment is — the absurd detail, the turn, the thing the agent said. (For the invisible-debt piece: the agent reporting "the session went fine" after silently deferring a dozen decisions. That's a meme. "Technical debt is bad" is not.)
- **Match the format to the beat's structure.** Preference/upgrade → Drake. Escalating absurdity → Galaxy Brain. Everyone ignores the obvious → "Always Has Been." Pick it like a kicker: one, and specific.
- **Tight, lowercase, dev-made.** Two short lines beat a stuffed panel. It should read like a developer made it at their desk, not a brand mascot.
- **Good beats even.** If the emptiest stretch has no beat worth a meme, put the meme on the beat and accept slightly-off-center placement — a sharp meme in the wrong gap beats a flat one in the right gap. You still ship one; hunt for the beat (the gate has no zero).

Build it the way the diagram and cover get built — produce the file, don't hotlink. Both scripts live in this skill's `scripts/` (stdlib + memegen.link, ~350 templates, no API key):

```
python3 scripts/render.py --list                          # browse templates; pick by what the FORMAT means
python3 scripts/render.py <id> <slug> "line 1" "line 2"   # → articles/<slug>.meme.png
```

Reference it inline with real alt text (describe the image for a screen reader, not a second punchline): `![<what it shows>](/<slug>.meme.png)`, dropped into the stretch `meme_check.py` flags.

## The third anchor — the free render

The diagram and meme are typed; the third required image is **free** — whatever the piece's emptiest remaining stretch actually wants. Pick from what the content offers, matched to the pillar like any other visual:

- A **stat-card** — one or two figures from `docs/ai-tech-debt-stories.md` set large with their caveat, for a data or thesis piece carrying a number the diagram didn't already use.
- A **second diagram** — a different mechanism or a before/after, when one render can't hold both ideas the argument needs.
- A **quote card** — a load-bearing line from a principal (Stenberg, the Replit agent's own words) set as an image where it lands.

It's built the exact same way as the diagram (hand-authored HTML → Playwright screenshot → committed PNG; see the diagram steps and `articles/diagrams/README.md`) and held to the same bar: **carries content the prose doesn't, or it's decoration and gets cut.** It's committed next to the piece — name it for what it is (`<slug>.statcard.png`, `<slug>.diagram-2.png`, etc.); only `.diagram.` and `.meme.` are reserved names the gate looks for. In a long piece the two-paragraph rule will ask for more breaks than three images; past the third, reach for a content-bearing table or code block where the shape offers one, another render where it doesn't — and cut prose first whenever the run is long because it's padded.

## The cover image — concept over cliché

dev.to (and most blogs) render a header image above the title — the first thing a scroller sees, so it's a conversion surface, not decoration. One per article, downloaded next to the piece in `articles/` as `<slug>.cover.jpg`; the canonical `<slug>.md` references it through its frontmatter `image` field (see Step 3's save block), so the committed cover travels with the post.

What makes a cover stand out is the *concept*, not the source. A dark server rack or a glowing-blue "AI brain" is the stock cliché every infra post already used. Reach for one concrete, slightly-oblique image the piece actually earns — the Replit code *freeze* wants cracked ice, not another server room. Pick it the way you'd pick a kicker: one, and specific. Skip AI-generated covers — the audience that bans AI prose reads an AI header as slop, and that's the credibility this whole skill protects.

You can't invent a valid photo URL, so look one up and download it — a committed file beats a hotlink that can rot or get rate-limited:

1. `WebSearch` for `site:unsplash.com <concrete concept>`, open a photo page.
2. `WebFetch` that page and take the `og:image` URL (`https://images.unsplash.com/photo-<id>?…`).
3. Download the **1000×420** crop next to the article, named for the slug — strip the og query string and re-pin to dev.to's spec (the Unsplash CDN honors these params):
   `curl -fsSL -o articles/<slug>.cover.jpg "https://images.unsplash.com/photo-<id>?w=1000&h=420&fit=crop&q=80&auto=format&fm=jpg"`
   Confirm it landed as a 1000×420 JPEG (`file articles/<slug>.cover.jpg`) and `Read` it to check the crop actually works as a header.
4. In the dev.to export's frontmatter, point `cover_image` at the committed file's raw URL (`https://raw.githubusercontent.com/<owner>/<repo>/<branch>/articles/<slug>.cover.jpg`) — dev.to fetches and re-hosts it. Credit the photographer in a one-line caption at the foot of the post — the Unsplash License doesn't require it, but it's clean and reads human.

Pexels works the same way (no attribution at all) if Unsplash has nothing.

## Calibrate on humans before drafting

Before writing, read (WebFetch, if available) one human-written essay from a rotating set — Dan Luu (danluu.com), Julia Evans (jvns.ca), Simon Willison (simonwillison.net), Rachel by the Bay (rachelbythebay.com), Daniel Stenberg (daniel.haxx.se/blog), Joel Spolsky (joelonsoftware.com), patio11 (kalzumeus.com / bitsaboutmoney.com) — and note two or three structural things it does that you wouldn't have done: where it rambles, what it skips, how unevenly it dwells. **Rotate the writer per article** — calibrating every piece to the same exemplar makes the series converge on one shape, which is its own fingerprint. The point is recalibrating the range of allowed shapes, not imitating a voice. If fetching isn't possible, skip the step; don't substitute an imagined exemplar.

Two anchors that are *not* rotation reads but a register and a rulebook to keep in mind: **Matt Levine** is the target register — the deadpan, explain-it-at-lunch voice that lands a good line by accident (borrow the register, never his footnote/digression tics). **Orwell** ("Politics and the English Language") and **Zinsser** ("On Writing Well") are the rules — concrete over abstract, cut every dead word — which is the same thing `fingerprint.py --vs-corpus` measures when it flags noun-heavy prose. These five corpus writers plus Spolsky are also the human baseline behind that script (`build_baseline.py`).

And the failure mode to avoid throughout: **do not compensate with emotion.** Dan Luu's prose contains approximately zero feelings and nobody has ever read it as AI. What makes writing human is obsessive concreteness, digression, and unevenness. Injected enthusiasm, manufactured frustration, or confessional asides the facts don't earn — that's over-correction, and it reads as fake as "delve."

## At series scale — don't develop a signature

This skill will write 70+ articles. The same author through the same instructions converges on pet phrases and identical structural moves — iteration 1 produced "I keep coming back to" in the same paragraph slot of two different articles written the same day. Across a daily series, that's how readers (and detectors) fingerprint the run.

Before delivering, skim the two or three most recent files in `articles/` and check the new draft against them: same opening move? same kicker shape? a phrase you've used before ("I keep coming back to," "the part nobody read," "quietly")? Change yours, not theirs. The CTA bridge is part of the signature too — "stories like this are why I built…" can appear in the series once, not in every incident piece. It's fine for two articles to share a worldview; it's not fine for them to share a skeleton.

## Step 3 — Audit, then deliver

Write the draft, then make a second pass as a hostile HN commenter who suspects both that the piece is AI-written and that it's an ad:

1. Run the humanize audit (manual catalog pass) plus the two deterministic scans:
   - `python3 .claude/skills/ai-smell-review/scripts/phrase_lint.py articles/<slug>.md` — em-dash density, AI typography, LLM vocabulary, regex-able structure tells, with line numbers.
   - `python3 .claude/skills/ai-smell-review/scripts/fingerprint.py --vs-corpus articles/<slug>.md` — checks the draft falls inside the p10–p90 band of real essays by the exemplar writers. Out-of-band in the AI direction (noun-heavy, participial-heavy, flat sentence rhythm, no self-mention) is a fail; de-nominalize to verbs and vary sentence length to pull it back in. Topical nouns get a pass (a piece on a "production deletion" runs high for honest reasons).
   - `python3 .claude/skills/write-article/scripts/meme_check.py articles/<slug>.md` — the visual contract: exactly one `*.meme.*` body ref with its file present, at least three committed body images (one a `*.diagram.*`), and no run of more than two prose paragraphs without a visual. A FAIL prints the offending stretch's line range — break it with a rendered image, or cut prose until the run closes.

   Fix every hit. A clean run on all three still proves nothing — the manual pass and the fresh-agent review below catch what a blocklist and a histogram can't.
2. **The ad test**: is the repo masthead the first body element, verbatim (`> **Full research and the plugin →** [github.com/bcanfield/agentic-tech-debt](https://github.com/bcanfield/agentic-tech-debt)`)? Past it, does the product show up before the reader has fully felt the problem? Is there any link other than the masthead and the one in-body repo link — a sibling article, a source, a relative `./file.md`? (All of those are named in prose, never linked.) Does any sentence flatter the tool instead of demonstrating it? Fix.
3. **The receipts test**: every stat and quote traceable to `docs/ai-tech-debt-stories.md`, every contested figure attributed inline, no invented numbers, dates correct relative to publish date. Every cited name also gets an identity the first time it appears — "Gauge drew the conclusion flatly" reads like a hallucinated source; "Gauge, a dev-tools consultancy, …" reads like a writer who knows who they're quoting.
4. **The shape test**: right voice for the pillar, CTA depth matches the shape, length in range, headline carries the headlines doc's *claim* but is held to the strictest anti-tell bar in the piece — soften any structure tell in it even though the doc ships the title that way (see "The headline gets the strictest pass" above); the doc title is a working claim, not final copy. (Distribution-channel title variants are still a separate task — don't improvise those here.) Formatting check: is the page a readable mix or a wall of gray? Does any run of prose go past two paragraphs without a visual (meme_check fails this, but eyeball it too)? Are all three required images present and committed — the mandatory `articles/<slug>.diagram.png`, the meme (`articles/<slug>.meme.png`), and a third anchor — each referenced inline and carrying content the prose doesn't? Does the meme land a specific beat rather than decorate the topic? Does each visual carry content the prose doesn't (cut it — and close the gap by trimming prose — if it just restates a sentence)? Is bold load-bearing and rare, or decorative and patterned the same way in every section (a tell — fix)? If exporting to dev.to, is there a `cover_image` and is it a concrete concept rather than the server-rack/AI-brain cliché?
5. **The smell test — not yours to run.** Spawn a *fresh* agent (Task tool) on the `ai-smell-review` skill (`.claude/skills/ai-smell-review/`) with the draft path. You cannot do this pass yourself: writers are provably blind to their own tells — in our evals the writing agent self-reported "one kicker" where an independent grader counted four. Apply the reviewer's ranked edits (push back only where an edit would break a fact or the shape), and if it flags more than ~5 real findings, send the revised draft back for one more pass. In the same fresh context, have the agent judge the meme (`Read` the PNG): is the format right for the beat, is it actually funny/apt or just present, does it read dev-made or brand? The gate has no zero, so its verdict is "ship this one" or "swap the beat/format and re-render" — never "drop it." You're blind to your own meme the same way you're blind to your own kicker.

Save to `articles/<slug>.md` (slug from the headline, lowercase-hyphenated; create the directory if needed). The body is plain markdown, but the file **opens with this YAML frontmatter block** (the blog reads it):

```
---
title: "<the softened headline>"
publishedAt: "<YYYY-MM-DD release slot>"
updatedAt: "<same as publishedAt on first write>"
author: "Brandin Canfield"
series: "Agentic Tech Debt"
summary: "<one plain line, ≤150 chars — what the reader gets, not a teaser; no em-dash>"
tags: ["<most relevant>", "<...>", "<...>", "<...>", "<5th>"]
image: "/<slug>.cover.jpg"
---
```

`series` is the same on every mainline article — **`Agentic Tech Debt`**, verbatim. It's the exact SEO phrase we're concentrating and it matches the repo slug (`github.com/bcanfield/agentic-tech-debt`), so name = keyword = destination; don't reword it per-piece or the keyword signal fragments. (dev.to has a real `series:` field that groups posts; the blog uses it as the collection/category.)

`tags` is exactly five, ranked most-relevant first, in platform-tag form (lowercase, single word, no spaces or `#` — e.g. `ai`, `technicaldebt`, `programming`, `codequality`, `devops`). The ranking is load-bearing: dev.to caps a post at four tags and other sites truncate too, so the export takes the top N off the front — put the tag you most want to be found under first. Pick from what the piece is actually about; reuse common tags across the series so the articles cluster, but don't pad with a tag the post doesn't earn.

`publishedAt` is the article's release-order slot date, not today. **No body H1** — the blog renders the frontmatter `title` as the page heading, so a body `# Heading` would double the title (and emit two H1s). The body starts on the first paragraph.

**Audit `title` and `summary` as hard as the prose — they're the most-syndicated lines you write** (index cards, OG/social previews, RSS), and they're short, which makes a structure tell *louder* there, not quieter. The `summary` is descriptive, not a pitch: say what the piece argues or covers, in the plain register of the leerob example ("Lessons from shipping real systems with AI-generated code"). The classic failure is two back-to-back epigrams — a balanced antithesis the body audit would have stripped, smuggled into the summary because it's "just metadata." Bad: `"Recorded debt is a financing instrument. The debt your agent never writes down is the landmine."` (two maxims, negative parallelism). Good: `"Why the debt that actually hurts a codebase is the kind nobody wrote down, and why coding agents produce so much of it."` Run the same kicker/antithesis/rule-of-three checks on both fields; the fresh-agent smell review (Step 3.5) reviews the frontmatter too.

Keep `summary` **≤150 characters** — roughly where Google truncates a meta description and a safe ceiling for the surfaces that use it. Platform mapping is uneven, so know where it lands:
- **Medium** has a visible subtitle/standfirst slot — `summary` goes there.
- **Our blog** uses `summary` for the index card and `<head>` meta.
- **dev.to has no summary field at all** — not in the rich editor, and `description` is *not* a documented front-matter key (dev.to's recognized keys are `title`, `published`, `tags`, `series`, `canonical_url`, `cover_image`). dev.to auto-builds its search/social snippet from the **first ~140 characters of the body**. So on dev.to the lever is the *opening line*, not the summary — the first sentence has to stand alone as the hook (our claim-first openings already do). Don't expect `summary` to appear anywhere on dev.to. (Platform exports like dev.to add their own frontmatter — `cover_image` etc. — on top of this; that's a separate task.)
