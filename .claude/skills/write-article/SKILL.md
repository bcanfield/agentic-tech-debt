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
- **Check `docs/ai-tech-debt-release-order.md`** for slot context: is this part of the Amazon Monday series? A `⟂ pair` with yesterday's piece? A BOFU slot? A date peg? Series pieces should reference their siblings; pair pieces shouldn't repeat the partner's material.
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

First sentence is the claim. Not a question, not context — the claim. Argue it with specifics borrowed from the incident and data pieces (link the ones already published per the release calendar; internal links keep readers in the funnel). Concede the strongest counterargument for real, not as a strawman to knock down. End when the argument ends — cornerstone essays don't need a summary, they need a last sentence that sticks.

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

## Conversion mechanics (what our research actually found)

From `docs/one-star-a-day.md` and `docs/publishing-checklist.md`:

- **Problem framing beats product framing.** "Claude Code plugin"-framed Show HNs scored 2–9 points; problem/outcome framing scored 100–500. The article is about the reader's problem; the tool is the epilogue.
- **Personal-story framing got roughly 3x the engagement** of dry technical description. This is why incidents and playbooks are first person.
- **Disclose self-interest, plainly.** "I built this, so weigh that" reads as honesty to developers and buys more trust than feigned neutrality. Same logic as labeling vendor studies.
- **One repo link.** The repo *is* the landing page. Don't link a marketing site, don't scatter five links, never ask for stars — the research is unambiguous that begging and engagement-farming backfire in this exact niche.
- **Readers arrive warm or cold by slot.** Week-1 and BOFU readers come from the README — peak intent, give them the next step fast. Data-piece readers are cold — let them leave impressed and unbothered.

## Sounding human — the part that decides everything

If the **humanize** skill is available, apply it in full and run its audit, including `check_tells.py`, on the finished draft. Its catalog is the authority. The highest-stakes subset for these articles:

- **Structure tells kill first**: negative parallelism ("it's not X, it's Y"), rule-of-three triplets, em dashes past the second one, rhetorical reveals ("The result? Disaster."), question-format headings, every paragraph ending on a tidy bow, symmetric bold-headed bullets.
- **Rhythm**: vary sentence length hard — a 30-word sentence, then a 4-word one. Contractions. Starting with And, But, So. One-line paragraphs.
- **Content**: every few paragraphs should contain a sentence only someone who did this work could write. Specifics over adjectives, a position over balance, discomfort allowed.

And go further than humanize does — these are articles, and **too perfect is its own tell**:

- **Leave something rough.** A parenthetical aside that wanders for a beat. A gripe. A question the piece raises and admits it can't answer. Sections of visibly unequal length. Readers trust writing with one loose thread more than writing with none.
- **Don't be exhaustive.** Covering 80% of the angle with a personality beats covering 100% of it like a survey. Cutting your third-best point is a feature.
- **Few headings.** Incidents and essays often need zero H2s. Playbooks get headings because readers skim them for steps. When you do use headings, sentence case, and never "Introduction" or "Conclusion."
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

Match the visual to the pillar — don't reach for one the content doesn't want:

- **Incidents** — a chronology with real timestamps reads well as a compact timeline (the Replit nine-day arc, day by day). Let a load-bearing quote stand on its own line.
- **Data** — where a table earns its place: the study's numbers side by side, before/after, your-repo vs. the cohort. One honest table beats three paragraphs walking the same figures, and it sets the caveat right next to the number it qualifies.
- **Essays** — usually the least formatted; the argument is the structure. One diagram of a mechanism can be worth a paragraph, but the default is no.
- **Playbooks** — already visual: real commands in fenced blocks, real tool output, registry frontmatter. A manual-workflow-vs-hook before/after is a natural table.

So it doesn't become the tell:

- **Every visual carries content the prose doesn't.** If a table just restates a sentence, cut the table. Decoration is the tell; information is the cure.
- **Bold is for load-bearing terms, used rarely** — the phrase a skimmer must catch, a real command, a term you're defining. Not emphasis the sentence already carries, and never the same bold pattern in every section (symmetric bold-headed bullets are still the first tell to die).
- **Don't formalize what's better as prose.** A two-item comparison is a sentence. A three-step process the reader runs once is a sentence. Reach for structure only when the content is genuinely structured.
- **Vary it.** If every section has a table they become wallpaper. One visual the content actually wanted beats one per section.
- **ASCII and fenced blocks only** — a table, a code block, a hand-drawn ASCII diagram render everywhere the article ships. Never link an image you can't produce.

## The cover image — concept over cliché

dev.to (and most blogs) render a header image above the title — the first thing a scroller sees, so it's a conversion surface, not decoration. One per article, downloaded next to the piece in `articles/`; the canonical `<slug>.md` stays plain (the cover is a separate file).

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

   Fix every hit. A clean run on both still proves nothing — the manual pass and the fresh-agent review below catch what a blocklist and a histogram can't.
2. **The ad test**: does the product show up before the reader has fully felt the problem? Is there more than one repo link? Does any sentence flatter the tool instead of demonstrating it? Fix.
3. **The receipts test**: every stat and quote traceable to `docs/ai-tech-debt-stories.md`, every contested figure attributed inline, no invented numbers, dates correct relative to publish date. Every cited name also gets an identity the first time it appears — "Gauge drew the conclusion flatly" reads like a hallucinated source; "Gauge, a dev-tools consultancy, …" reads like a writer who knows who they're quoting.
4. **The shape test**: right voice for the pillar, CTA depth matches the shape, length in range, headline matches the headlines doc (distribution-channel title variants are a separate task — don't improvise them here). Formatting check: is the page a readable mix or a wall of gray? Does each visual carry content the prose doesn't (cut it if it just restates a sentence)? Is bold load-bearing and rare, or decorative and patterned the same way in every section (a tell — fix)? If exporting to dev.to, is there a `cover_image` and is it a concrete concept rather than the server-rack/AI-brain cliché?
5. **The smell test — not yours to run.** Spawn a *fresh* agent (Task tool) on the `ai-smell-review` skill (`.claude/skills/ai-smell-review/`) with the draft path. You cannot do this pass yourself: writers are provably blind to their own tells — in our evals the writing agent self-reported "one kicker" where an independent grader counted four. Apply the reviewer's ranked edits (push back only where an edit would break a fact or the shape), and if it flags more than ~5 real findings, send the revised draft back for one more pass.

Save to `articles/<slug>.md` (slug from the headline, lowercase-hyphenated; create the directory if needed) with the headline as the H1. Plain markdown, no frontmatter, unless the user asks for a specific platform format.
