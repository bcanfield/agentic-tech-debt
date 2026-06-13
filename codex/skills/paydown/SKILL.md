---
name: paydown
description: Autonomously pay down the safe, mechanical tech-debt entries — fix, test, self-review, commit, drop, repeat — and escalate judgment calls instead of guessing. Use when the user says "pay down the debt," "keep going until the debt is paid," "clear what you safely can," or invokes $paydown. Runs interactively or headless (CI). Distinct from $review, which only audits.
---

# paydown — gated autonomous paydown

This is the verb that *acts*. `review` audits and stops; `paydown` walks the safe
class on its own — fix, test, self-review, commit, drop, next — and asks a human
only when it hits a real judgment call. (Why this is safe, in one line: autonomy and
gates are orthogonal — GitClear's data indicts *ungated* fast AI editing, not the
absence of a human keystroke between fixes. So the loop keeps every gate and moves the
human from per-entry approver to PR reviewer. Full rationale: ADR 0021 in the source repo.)

## Read the room first: are you reachable to a human?

- **Interactive** (a developer is in the session): when you hit a judgment call, stop
  and ask them — a concise question with the entry's real options as choices. Use your
  environment's structured-question affordance if it has one; otherwise ask inline.
- **Headless** (CI, `codex exec`, no human mid-run): you cannot block on a person.
  Do the safe class, and write escalations + the run summary into a **PR body and a
  markdown report**. The PR review is the human gate. Never invent an answer to a
  judgment call just because no one is watching.

If unsure, assume interactive and ask.

## Get the ranked list

Run the sibling `review` skill (`$review`) to produce the deterministic audit —
staleness flags + churn × quadrant ranking. You don't re-derive that. (You can also
read the registry under `docs/debt/` directly.) Propose `review`'s stale-flagged
entries for `drop` first — don't pay down dead code — then classify the survivors below.

## Classify each survivor: green, or escalate

**Green (auto-pay) — all of these must hold:**
- hotspot path still exists;
- small principal (≤ ~1h — read the `principal:` field);
- the fix is mechanical with one obvious primitive (the entry body usually names it:
  "the right primitive is `chat.getPermalink`");
- tests exist in that area to gate the change;
- it is **not** a deliberate tradeoff with an unmet `payoff_trigger`;
- the hotspot is **not** a security / auth / payments / migration / public-API boundary.

**Escalate (never guess) — any of:**
- principal is large or the fix is judgment-heavy;
- the body offers **multiple credible options** ("options at payoff time: …") —
  choosing among them is the human's call and per AGENTS.md becomes an ADR, not an
  autonomous edit;
- `prudent-deliberate` with the `payoff_trigger` not yet met — honor the trigger;
- a risky boundary (auth/payments/migration/public API);
- no tests in the area — you can't gate it, so don't autonomously change it.

When in doubt, escalate. The cost of a skipped fix is one line in a report; the cost
of a wrong autonomous edit is what GitClear measured.

## The loop (green entries only)

Work one entry at a time. For each:

1. **Read** the registry entry, the hotspot file, and the adjacent tests. Match the
   repo's framework and style — don't impose a new one.
2. **TDD.** Write a failing test that pins the deferral the entry describes, then make
   it pass. Never weaken or delete an existing test to get green.
3. **Smallest fix.** Improvement, not perfection. Resolve the entry; don't refactor
   the neighborhood.
4. **Run the gates.** The repo's cached feedback commands / test suite must be green.
   Red and not fixable in one more focused pass → revert this entry's changes, move it
   to the escalate list, continue.
5. **Fresh-context self-review.** Spawn a sub-agent to review the diff — *always*, not
   just for risky fixes. In supervised paydown a human reads each diff; here nobody
   does, so writer/reviewer separation is mandatory. If it flags a correctness problem,
   revert and escalate.
6. **Commit one entry per commit**, and **drop the registry entry in the same commit**
   so the ledger stays honest. Add the trailer `Debt-Pays-Down: <id>`. Use `drop <slug>`
   semantics — the entry file is removed in the same change that resolves it.
7. **Next entry.**

### Bounds (a runaway loop is the failure mode)

- **Scope cap.** Default to a handful per run (~5) unless the user gave a number or
  said "keep going / all you safely can" — then continue through the whole green class,
  still one at a time, still fully gated.
- **Stop after two consecutive failures** (test won't go green, or self-review rejects
  twice in a row). Something about the repo state is off; report and stop rather than
  thrash.
- **Never** force-push, auto-merge, touch entries outside the green set, or commit a
  diff you can't explain by citing the entry's body or `payoff_trigger`.

## Escalating a judgment call

**Interactive — ask, with options.** One question per escalated entry (or batch a few),
options drawn from the entry body's alternatives. Example: for `rate-limiting-and-cost-ceiling`
the options are "per-user token budget," "per-channel rate limit," "monthly cost ceiling,"
each a real choice from the entry. Let the human pick; if their pick implies an
architectural decision, draft the ADR (per Discipline 2) rather than silently coding it.

**Headless — write it down, don't block.** Collect escalations and emit:
- a markdown report at `docs/debt/paydown-report.md` (paid / escalated / failed), and
- the same summary in the PR body.

Don't ask a question into the void; a headless run has no one to answer it.

## Closing a run — always report

Whether you fixed 5 or 0, end with a plain-language summary:

- **Paid down (N):** entry → one-line fix → commit sha.
- **Escalated (N):** entry → why → the options a human needs to choose between.
- **Failed (N):** entry → what broke (test stayed red, self-review rejected).
- **Proposed drops (N):** stale entries `review` flagged — `drop A,B,C`.

Speak plainly. The frontmatter taxonomy (`quadrant`, `category`) is for ranking, not
for the user — say "a planned tradeoff" / "a shortcut" / "came up later," never
"prudent-deliberate."

## Don't

- Don't pay down anything outside the green class. Escalate-don't-guess holds even
  when no human is watching.
- Don't auto-merge or force-push. The PR review is the gate the whole design rests on.
- Don't skip the self-review sub-agent to save tokens — it's the writer/reviewer
  separation that makes unattended fixing safe.
- Don't leave a paid entry in the registry. Fix and drop land in the same commit.
- Don't run the supervised `review` rubric here — that one waits for the user. This
  one acts within its bounds.
