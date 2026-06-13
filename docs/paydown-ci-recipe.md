# Autonomous paydown in CI — a recipe, not a shipped Action

`/debt-ops:paydown` ([ADR 0021](./adr/0021-autonomous-paydown.md)) runs the same gated
loop headless. We give the recipe here rather than ship a GitHub Action inside the
plugin — same call ADR 0007 made for scheduled review: the natural shape is a job in
*your* repo, not new surface in *ours*. Copy this, pin the versions you trust, own it.

## What the job does

One scheduled run → one PR. The agent fixes only the **green class** (small, mechanical,
tested, non-boundary), one entry per commit, each diff self-reviewed by a fresh-context
sub-agent and gated on your test suite. Judgment calls are **not attempted** — they land
in the PR body for a human to decide. Nothing auto-merges; the PR review is the gate.

## Claude Code (headless)

```yaml
# .github/workflows/debt-paydown.yml
name: debt-paydown
on:
  schedule: [{ cron: "0 13 * * 1" }]   # Mondays 13:00 UTC
  workflow_dispatch:
permissions:
  contents: write
  pull-requests: write
jobs:
  paydown:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }       # churn ranking needs full history
      - name: Pay down the safe class
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          git switch -c "debt-paydown/$(date +%Y%m%d)"
          claude -p "Run /debt-ops:paydown. You are headless — no human is reachable.
            Pay down only the green class, fully gated. Write escalations and the run
            summary to docs/debt/paydown-report.md. Do not merge, do not force-push."
      - name: Open the PR
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          git push -u origin HEAD
          gh pr create --fill --body-file docs/debt/paydown-report.md || \
            echo "Nothing to pay down this run."
```

## Codex (headless)

Swap the agent step for `codex exec "Run the paydown skill. You are headless …"` with
the same instructions, and provide `OPENAI_API_KEY`. The skill body is identical; only
the launcher and the credential change.

## Why these guardrails are non-negotiable

- **Green class only.** The loop never autonomously edits a security/auth/payments/
  migration/public-API boundary, a large-principal entry, or anything with no tests to
  gate it. Those escalate. This is what keeps the run on the safe side of GitClear's
  ungated-AI-cleanup data ([ADR 0021](./adr/0021-autonomous-paydown.md),
  `tech-debt-management.md:32-36`).
- **No auto-merge.** The whole design rests on the PR being a real human checkpoint.
  Green gates make it a *fast* review, not an absent one. Don't add `gh pr merge`.
- **Fresh-context self-review.** Every diff is reviewed by a separate sub-agent before
  commit — writer/reviewer separation (Anthropic) is mandatory when no human watches
  each fix, not risk-gated as in supervised paydown.
- **Bounded loop.** Scope cap + stop-after-two-consecutive-failures keep a bad repo
  state from turning into a thrashing PR.

## Tuning

- **Cadence.** Weekly is a sane default. Daily only once you trust the accept rate.
- **Scope.** The skill defaults to a handful of entries; tell it a number in the prompt
  to widen or narrow per run.
- **Accept-rate is the signal.** If humans keep rejecting green-class PRs, the green
  boundary is too loose — tighten the skill's criteria before widening anything. That's
  the ADR 0021 revisit trigger.
