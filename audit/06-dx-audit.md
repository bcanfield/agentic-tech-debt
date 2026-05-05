# DX audit (Pass 6): the Persona-2 daily-use lens

Date: 2026-05-05
Scope: stress-test v1's "enable-and-go," "near-silent on first session,"
"lean relaxed over strict," and "the plugin disappears into the
developer's workflow" claims from the perspective of a senior IC adding
the plugin to an established codebase. Bullseye is Persona 2; Persona
3 (small team) checked where it diverges. Out of scope: the failure
modes the plan's "v1 implementation requirements" appendix already
addresses (cache staleness, macOS `timeout`, /debt:add ID race, etc.).

---

## A. First-run experience

### Step 1 — install

A senior IC installs `debt-ops` from a marketplace or local link.
There is no install-time prompt, no `userConfig`, no `/debt:init`
required. The §Plugin layout (v1) section confirms zero working-tree
footprint. **Score: friction-free.** This is the strongest part of
the experience.

### Step 2 — first `claude` in the repo

`SessionStart` fires `session-start.sh`. Per §How it works and §Hook
layout, the script emits an `additionalContext` payload containing
the six disciplines and, on the first session, a discovery prompt.

The plan's day-in-the-life asserts "the developer sees nothing"
(§A day in the life, 08:50). This is the load-bearing claim and
worth pressing. `additionalContext` lands in model context, not
transcript — spec-correct. But Claude's *response* to a freshly-
injected "scan the repo and write `feedback.list`" is not guaranteed
to be silent. Two outcomes:

1. **Silent and correct.** Claude treats the inject as a system
   instruction, performs scan tool calls (collapsed in CC's UI),
   writes the cache, emits no chat text.
2. **A "hello, I scanned your repo" preamble.** Claude treats the
   inject conversationally and announces: "Detected `cargo check`,
   `cargo clippy`. Cached. Ready when you are."

The plan asserts (1) by stipulation; the protocol does not guarantee
it. Persona 2 tolerates (1), mildly resents (2), abandons the plugin
if (2) recurs every session. Mitigation in §F.

The six-item inject (~1500 chars) is invisible to the dev and visible
to the model — the correct trade. **Score: minor friction,
conditional on inject not generating chat noise.**

### Step 3 — first edit

`PostToolUse` fires `feedback.sh` returning `{"cargo check": "pass"}`
via `additionalContext` → next model turn, not transcript. Dev sees
nothing. Good.

But the dev's *first 30 minutes* may show no plugin behavior at all:
they ask a question (no edit), edit a `.md` (`feedback.sh` runs but
returns trivial pass), edit without writing a TODO (Discipline 1
dormant), no architectural change (Discipline 2 dormant). The plan
promises "the plugin works on the first agent edit" — true, silently.
The first user-visible artifact may not appear for hours.

Latent risk: the dev concludes "this thing isn't doing anything" and
uninstalls before seeing value. The plan does not commit to surfacing
first-edit feedback in any form the dev can see. **Score:
friction-free with latent abandonment risk.**

### Lazy-creation surprise

When `/debt:add` first creates `debt/registry/`, `git status` shows
`?? debt/`. §How we coexist claims "Files in the user's repo only
appear when the developer asks for them." Technically false: the
*agent* asked, prompted by the invisible inject. The dev's mental
model is "I didn't ask for this."

This is install-recency-dependent: a dev who installed three days ago
reads it as "mine"; a dev who installed an hour ago and saw no setup
reads it as "what is this." **Score: minor friction, mitigation in
§F.**

---

## B. Daily flow

A plausible Tuesday: feature with three placeholder TODOs; a
refactor; a dep bump; two bug fixes; tests. Six edit waves, ~5 hours.

### B.1 — TODO registration cadence

Three placeholders → three Discipline 1 fires → three files in
`debt/registry/` → three announcements: "Registered the X entry.
Tell me to drop it if it's not real debt." Persona 2 reads each on
day one, skims by Friday, banner-blinds by week two. Useful-to-
annoying tip is around **5-7 entries per session.**

Compounding: the inject (§Disciplines, item 1) was hardened to drop
the "trivial markers don't earn an entry" loophole, with rationale
"err toward registering." Right *recall* call (audit-04 §3) but
guarantees a higher per-session rate than the day-in-the-life shows
(one TODO + one false positive). Feature-heavy days are 2-3x.

**At risk of trained-to-ignore.** Announcement *text* matters more
than the plan acknowledges. Mitigation in §F.

### B.2 — ADR drafts

Discipline 2's "two credible alternatives or it's a comment" gate
(audit-04 §3 hardening) helps. But the trigger surface — "data model,
public interface, dep manifest, security boundary, release pipeline"
— is broad. Strict reading: every PR on a Tuesday touches one.

Realistic over-fire: dev bumps `serde` 1.0.197 → 1.0.198. Discipline
2 fires. Claude lazily creates `doc/adr/`, writes `0001-bump-serde.md`
with manufactured "Alternatives" ("stay on 1.0.197" vs "upgrade").
The two-alternatives gate doesn't catch this; both are technically
credible.

Cost: ~30s reviewing the ADR, ~15s deleting it, then mentally tagging
Discipline 2 as over-eager. Escape hatch is *only* deleting the file
or telling Claude in chat (session-scoped). No `/debt:adr-skip`, no
project-local toggle.

**High false-positive risk on dep manifests.** Mitigation in §F.

### B.3 — `feedback.sh` JSON visibility

Per §Pillar 7 + day-in-the-life, JSON lands in `additionalContext`
→ model context, not chat. Dev does not see it. Good.

Risk: if a future CC version surfaces hook output in transcripts (for
debug or "thinking" mode), the silence claim breaks. v1 has no
defense — the JSON is the protocol. **Low risk in v2.1.121, watch
in dogfood.** Acceptable.

### B.4 — the prioritization gap

By Friday: 18 registry entries. Dev wants to spend 30 minutes paying
down. They open `debt/registry/`. Files are sorted by id
(chronological). No ranking, no `/debt:list`, no filter. §Pillar 3
explicitly defers this: "Developers fall back to existing
prioritization until v2."

The dev opens each `.md`, eyeballs `principal` and `hotspot`, picks.
For 18 entries: 5-10 minutes of chooser-overhead. The plan says "ask
Claude to read the dir," but that's session-scoped — the dev cannot
bookmark the result.

This is the moment "enable-and-go" collides with the deferral table.
Both halves are honest; the second half lands hard the moment the
dev wants to *use* the registry. **Medium friction at end of week
one; significant by month one without v2.** Mitigation in §F.

### B.5 — PR-time cleanup

`git diff` shows new entries (1-3) and possibly new ADRs (0-1). Per
audit-04 §1.4, some entries may be stale (underlying code rewritten
mid-session). PR review tasks: read each entry's `payoff_trigger`
(~30s), read each ADR's "Decision" vs ship reality (~60s), decide
keep/`git rm` (~10s).

**Quantification: ~1 minute per entry, ~2 minutes per ADR.** Tuesday
with 3 entries + 1 ADR: ~5 minutes. Feature week with 12 entries +
3 ADRs: ~15 minutes. The plan's §Closing implies the dev "interacts
through chat," but PR review is the file tree (`gh pr view`, GitHub).
Chat is not in the loop. PR-time interaction is by file edit, not
by chat. **The plan should name this tax.**

---

## C. The "trained to ignore" risk

| Surface | Severity v1 | Cheapest mitigation |
|---|---|---|
| `feedback.sh` returns `timeout` repeatedly | **Med** (impl-req #5 already asks for changed-file-scoped commands; residual: Claude picks project-wide anyway) | If a command times out 2 of last 3 runs, emit `WARNING: <cmd> timing out; consider scoping`. Self-correcting in 4 lines. |
| `feedback.sh` always returns `pass` (commands too narrow) | **Med** | If session detected `<2` commands, inject "consider `/debt:init` — only one quality command found." 1 line. |
| ADR creation rate too high | **High** (B.2) | Tighten Discipline 2's "dep manifest" → "dep manifest with major-version change or new top-level dependency." 8 words. |
| Registry entries proliferate without ranking | **High** by week 4 (B.4) | Ship a 10-line `/debt:list` skill in v1: `cat debt/registry/*.md` + grep title/hotspot/principal. Unranked is fine. |
| Disciplines downweighted under long context | **Med** (audit-04 §1.2 covered) | v1 accepts; v2's Stop hook is the right insurance. No v1 fix. |

The two **High** entries train the dev to ignore within a month.
Both are ~10-line fixes.

---

## D. The "annoying" surfaces (senior-IC eye-roll inventory)

**D.1 — The 6-item inject as ceremony.** Six bullets in the plan
read paternalistic in document form even if invisible at runtime.
*Smallest fix:* lead §The disciplines with one sentence: "These six
instructions live in `session-start.sh`'s heredoc; the developer
never sees them. They orient the model, not the user." Reframes
ceremony as plumbing.

**D.2 — Discipline 1's "err toward registering."** Right recall
call, paternalistic wording. *Smallest fix:* soften the rationale
from "you cannot recover an unregistered shortcut" to "drop in one
message: 'that's not real debt.' I'll delete the entry." Frames
over-fire as cheap (true) rather than as a moral imperative.

**D.3 — Discipline 5's "spec before edit."** Reads as homework. The
saving grace — "the spec lives in chat, not a file" — is buried.
*Smallest fix:* append "the spec is a single chat message before
editing; the developer reads it, not writes it." Reframes from
homework to early warning.

**D.4 — The CLAUDE.md marker block.** Audit-04 §8 named this. Plan's
"markdown comments are conventionally ignored" is correct but cold
for a teammate without the plugin. *Smallest fix:* the marker's
inner first line is a human-readable explainer: `<!-- this section
is auto-managed by the debt-ops Claude Code plugin; safe to edit,
run /debt-ops:init to regenerate -->`. Eliminates the "what is this"
reaction.

**D.5 — The Pillar 6 honesty paragraph.** §Pillar 6 ends with "we
trust Claude's reading of whatever charter exists." Honesty-coded-
as-hand-wave. *Smallest fix:* "v1 has no charter-size defense. If
your CLAUDE.md exceeds ~10k tokens, expect discipline-firing rates
to drop; that's the dogfood signal that v2's size budget is needed."
Testable claim replaces hand-wave.

---

## E. The Persona-2 install-or-skip decision

I'm a senior IC. I read the plan. I decide.

**Case for installing.** Zero install ceremony (verified). Six
disciplines I'd otherwise write into my own CLAUDE.md (saved time).
The registry schema (Fowler quadrant + Google categories + payoff
trigger) is genuinely good — a week of reading
Kruchten/Fowler/Jaspan to invent. The cache-with-manifest-mtime
detection (impl-req #2) is exactly the kind of thing I'd cargo-cult
wrong.

**Case for skipping.** I can write the inject myself in 30 lines. I
can `mkdir debt/registry` myself. The registry has no ranking until
v2; I'm taking on the ceremony for the schema only. Audit-04 §4 said
as much: v1 does not strongly differentiate from a homemade hook +
a manual registry convention.

**What flips it:** the schema and the cache invalidation logic
together justify install — but the plan buries the schema in §The
registry schema between "How it works" and "The v1 commitment." Move
it higher and lead with it.

**What pushes toward skip:** announcement spam after every TODO
(B.1) and no `/debt:list` (B.4). If the plan's day-in-the-life had
said "the announcement is one line; you can suppress it with
`/debt:quiet`" I'd be more receptive.

**Smallest single change to flip skip → install:** add a 10-line
`/debt:list` skill to v1 (unranked, just `cat` the entries with
title/hotspot/principal). Costs nothing, removes the biggest
week-two friction. Combined with leading the plan's introduction
with the schema, the install case becomes solid.

---

## F. Top 5 DX changes (ranked)

1. **Add a 10-line `/debt:list` skill to v1.** §The v1 commitment
   defers this to v2. Reverse it. Skill is ~5 lines: cat the
   registry, grep title/hotspot/principal. Removes the biggest
   week-two friction (B.4). **Effort: 30 minutes. Win: high.**

2. **Tighten Discipline 1's announcement text.** Replace `"Registered
   the X entry. Tell me to drop it if it's not real debt."` with
   `"+1 entry: X (drop?)"`. Reduces visible noise on feature-heavy
   days (B.1) without changing recall. **Effort: 1 line of inject
   text. Win: high.**

3. **Narrow Discipline 2's dep-manifest trigger.** Change "dep
   manifest" to "dep manifest with a major-version change or new
   top-level dependency." Cuts the dep-bump ADR over-fire (B.2).
   **Effort: 8 words. Win: medium-high.**

4. **One-time first-edit confirmation.** On the *very first*
   successful `feedback.sh` per repo, prefix the model's
   `additionalContext` with `"debt-ops: first edit ran X commands.
   Future edits run silently."` Single user-visible signal that the
   plugin works (§A.3 latent risk). After the first edit silence
   resumes. **Effort: 5 lines + a state file in
   `${CLAUDE_PLUGIN_DATA}/cache/<repo-hash>/first_edit_announced`.
   Win: medium-high.**

5. **Reframe the disciplines section in the plan.** Add one
   sentence above §The disciplines: "These six instructions live in
   `session-start.sh`'s heredoc and orient the model. The developer
   never reads them; the user-visible surface is announcements,
   chat-message specs, and the registry." Converts the page from
   "list of corporate rules" to "plumbing description" for the
   senior IC reading the plan (D.1, D.3). **Effort: 1 sentence.
   Win: medium (decision-time only, but that's the bottleneck).**

Honorable mentions: the human-readable marker explainer (D.4);
softer "err toward registering" rationale (D.2); the rewritten
Pillar 6 honesty paragraph (D.5).

---

## G. Verdict

Will Persona 2 like v1 today? Mixed. They will love install (§A) and
the schema. They will tolerate the first session. They will push back
at week two when (a) the registry has 15+ unranked entries, (b)
`doc/adr/` accumulates ADRs from dep bumps, (c) TODO-heavy days lose
announcement signal. By month one a non-trivial fraction of installs
abandon — not because the plugin is bad, but because *announcement
text* and *missing /debt:list* convert into ignored ceremony.

After the top 5? Yes. Items 1 and 2 fix the two high-severity
trained-to-ignore risks (§C). Item 3 cuts the highest false-positive
surface. Items 4-5 fix the perception layer that determines whether
the dev evaluates v1 fairly in week one. None touch v1's architectural
shape; all are surface text or tiny skills. Total effort: under a day.

Residual risk: discipline drift under long context (§C row 5) and
the PR-time cleanup tax (§B.5). Both are plan-named v2 territory and
acceptable v1 risk *if* dogfood metrics ship — same conclusion as
audit-04. The DX layer is tighter than the architectural layer; the
top 5 are cosmetic from the spec's view but load-bearing from the
dev's. v1 is one announcement-text edit and one 10-line skill away
from disappearing into the workflow. Do those two and Persona 2
keeps the install.
