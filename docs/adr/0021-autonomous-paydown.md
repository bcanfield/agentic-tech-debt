# 0021 — Autonomous paydown (gated loop, not unsupervised batch)

**Date:** 2026-06-12
**Status:** Accepted (supersedes the `--auto` and separate-skill rejections in [ADR 0008](./0008-paydown-extends-review.md))

## Context

ADR 0008 made paydown the third beat of the *review* rhythm: user-in-the-loop, one entry at a time, no auto-commit. It explicitly ruled out an unsupervised `--auto` batch mode, citing GitClear's 211M-LOC finding that fast, ungated AI cleanup produces ~4× duplicate blocks and doubled short-term churn (`docs/tech-debt-management.md:32-36`).

Dogfood across repos surfaced the gap that prediction didn't cover: registries grow to 80–100 entries (slack-agent hit 98), and the long tail is mechanical — 30-minute, single-primitive fixes like "use `chat.getPermalink` instead of the hand-built URL." A human walking those one at a time is the bottleneck, not the safeguard. Two concrete asks: a developer who wants to say "just keep going until you've paid off what you safely can," and a CI job that opens a paydown PR on a schedule with no human present mid-run.

The thing to get right is *what GitClear's data actually indicts*. It indicts **ungated** fast AI editing — no tests in the loop, no fresh-context review, no scope limit. It does **not** indict the absence of a human keystroke between each fix. The research line that matters is the deterministic wrapper: tests/linters/type-checks/code-health feedback inside the agent's edit cycle, where agents refactor 2–5× better (`docs/tech-debt-management.md:7,41`), plus writer/reviewer separation (Anthropic) and improvement-not-perfection (Google). Autonomy and gates are orthogonal. The mistake ADR 0008 conflated was treating "unsupervised" and "ungated" as the same word.

## Decision

Add a fourth skill, `/debt-ops:paydown`, that runs a **gated autonomous loop**. It is not a second backlog (ADR 0007's anti-pattern) — it's an execution surface over the one registry that `review` already audits and ranks. `review` stays audit-first (prints and stops); `paydown` is the verb that acts, kept on a deliberately distinct invocation so the "this one actually changes code on its own" surface never fires from a passive report.

**Selection — only the green class auto-pays.** Per entry, all must hold: hotspot path still exists; small principal (≤ ~1h); the fix is mechanical with one obvious primitive; tests exist in that area to gate against; the entry is not a deliberate tradeoff with an unmet `payoff_trigger`; the hotspot is not a security/auth/payments/migration/public-API boundary. Anything failing these is **escalated, not guessed**. Entries with multiple credible options in their body (the `rate-limiting-and-cost-ceiling` shape — "options at payoff time: …") are escalations by definition: choosing among credible alternatives is the human's call, and per CLAUDE.md becomes an ADR, not an autonomous edit.

**Gates — per entry, every entry.** TDD where tests exist (failing test that pins the deferral, then make it pass; never weaken an existing test to pass). Run the repo's cached feedback commands / suite — must be green. Fresh-context `code-review` sub-agent on the diff (always in autonomous mode — there is no human watching each one, so writer/reviewer separation is mandatory, not risk-gated as in supervised paydown). One commit per entry, dropping the registry entry in the same commit, with the `Debt-Pays-Down: <id>` trailer. A scope cap (default a handful of entries) and a stop-after-two-consecutive-failures backstop bound a runaway loop. Never force-push, never touch entries outside the green set.

**Human input — dependency-free, two sinks by reachability.** When a human is reachable (a developer running it interactively), escalations use the native `AskUserQuestion` tool — structured choices, no browser, no server, no `feedback.json` round-trip. When headless (CI, `claude -p`, `codex exec`), the agent cannot block on a human, so escalations and the run summary are written as a **structured artifact**: a markdown report and the PR body listing paid / escalated (with the options) / failed. The PR review *is* the human gate. This is deliberately not skill-creator's local HTML viewer — that pattern needs a browser/display and a file round-trip; `AskUserQuestion` + a PR comment cover both reachability cases with zero new dependency. (skill-creator's own headless fallback already concedes the point: "skip the browser reviewer entirely; present results in the conversation.")

## What this means for you

- Interactive: run `/debt-ops:paydown` and say "keep going." It walks the green class on its own — fix, test, self-review, commit, drop, next — and only stops to ask you when it hits a real judgment call, via a clean multiple-choice prompt, not a wall of prose or a browser tab.
- CI: a scheduled headless run opens one PR — green-class fixes already tested and self-reviewed, each its own commit, the registry entries dropped alongside. Judgment calls aren't attempted; they're listed in the PR body for you to decide. You review one PR instead of babysitting a loop.
- Nothing auto-merges and nothing force-pushes. The safety budget that protected supervised paydown (tests green, fresh-context review, small scope) is exactly what gates the autonomous loop — the human moved from per-entry keystroke to PR reviewer, the gates did not move.
- `review` is unchanged: still audit-first, still yours to drive. `paydown` is the opt-in that acts.

## Alternatives we ruled out

- **Keep ADR 0008's user-in-the-loop-only stance.** It was right that *ungated* batch is harmful and right for the supervised path, but it left no answer for the 98-entry long tail or for CI. Gated autonomy is the missing mode, not a reversal of the safety argument — the gates are inherited wholesale.
- **An `--auto` flag on `review`.** ADR 0008's own revisit trigger ("if the rubric pushes `review/SKILL.md` past ~80 lines, split paydown into its own skill") fires here: autonomous mode is substantial and behaviorally distinct, and folding it into `review` risks the exact "over-acts on the first-turn report" failure ADR 0008 worried about. A separate invocation keeps the audit surface passive.
- **A `paydown.py` orchestrator that scripts per-entry fix decisions.** Still ruled out, same as ADR 0008: framing the fix, picking the test approach, and judging comprehensibility are what the agent reading the repo does better than a state machine (CLAUDE.md). Python stays for determinism only. *Deterministic selection* of the green set (an auditable "here's exactly what CI will touch and why") is worth having for the CI story, but it's deferred as a registered debt entry — extend `review.py` with a `--plan` bucket emitter — not built speculatively now.
- **skill-creator's HTML viewer for human input.** Needs a browser/display and a `feedback.json` download round-trip — an unnecessary dependency for what `AskUserQuestion` (interactive) and a PR comment (headless) already do natively.
- **Best-effort autonomous fixes for judgment entries in CI, flagged for extra scrutiny.** Tempting (more gets done unattended), but it's precisely the ungated-fast-edit shape GitClear indicts, and it puts the agent in the position of silently choosing among credible alternatives that should be an ADR. Escalate-don't-guess holds even when no human is watching.
- **Auto-merge the CI PR when all gates pass.** Removes the one human checkpoint the whole design rests on. The PR review is the gate; green gates make it a fast review, not an absent one.

## When to revisit

- If autonomous PRs come back with a low accept rate (humans rejecting green-class fixes), the green boundary is too loose — tighten principal/mechanical criteria or shrink the scope cap before widening anything.
- If the green class is reliably accepted and CI demand grows, build the deferred `review.py --plan` deterministic selector so "what the loop will touch" is auditable pre-run, and consider raising the scope cap.
- If escalation artifacts pile up unread, the registry is over-weighted toward judgment entries — that's a capture-discipline signal (Discipline 1/2), not a paydown one.
- If a self-review sub-agent miss ships a bad fix, harden the gate (second reviewer, or require the entry's `payoff_trigger` be cited in the fix rationale) before loosening anything else.

## Payoff trigger

This ADR introduces a new autonomous code-modifying surface with conservative defaults (green-class only, deferred deterministic selection). Revisit when autonomous-PR accept-rate data exists, or when CI usage justifies building the `review.py --plan` selector and raising the scope cap.
