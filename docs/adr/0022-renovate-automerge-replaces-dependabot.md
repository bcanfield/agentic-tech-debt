# 0022 — Renovate with automerge replaces Dependabot

**Date:** 2026-07-14
**Status:** Accepted

## Context

Dependabot (`.github/dependabot.yml`) watched only the pinned GitHub Actions and
opened PRs that sat until someone clicked merge. It never covered
`demo/concept/package.json` (the Motion Canvas demo), and it has no automerge of
its own — you'd wire up a separate workflow that approves/merges its PRs. The
goal is zero-touch: dependency PRs open *and* land on their own when CI passes.

## Decision

Replace Dependabot with the Mend-hosted Renovate GitHub App, configured in
`.github/renovate.json`:

- `config:recommended` as the base — auto-detects the `github-actions` manager
  (updates SHA pins plus their version comments) and the npm demo package.
- Automerge for `minor` / `patch` / `pin` / `digest`; majors still open a PR but
  wait for a human click.
- `minimumReleaseAge: 3 days` for npm — with nobody reviewing the diff, don't
  pull a package the hour it's published (supply-chain guard).

Renovate's default `platformAutomerge` uses GitHub's native auto-merge, which
needs two repo settings (applied via API, not in-repo): **allow auto-merge** on,
and branch protection on `main` requiring the HOL Plugin Scanner `scan` check —
without a required check, GitHub merges before CI finishes. `enforce_admins`
stays off so direct pushes to `main` keep working.

Commits stay `chore(deps): …` (Renovate detects the conventional-commit style),
so dep bumps never trigger a release-please plugin release — they're CI/demo
surface, not product.

## Consequences

- Non-major updates land unattended once `scan` is green; majors queue as PRs.
- The Renovate app must be installed on the repo (one-time, manual — a GitHub
  App install can't be committed). Until then the config is inert.
- Dependabot *version* PRs stop; GitHub's security alerts are unaffected.

## Alternatives

- **Keep Dependabot + an auto-approve/merge workflow.** Works, but it's a
  second workflow with `GITHUB_TOKEN` gymnastics, and Dependabot still can't
  group or age-gate npm packages. More moving parts for less control.
- **Self-host Renovate via `renovatebot/github-action` on a schedule.**
  Full control, but PRs opened with the default `GITHUB_TOKEN` don't trigger
  `pull_request` workflows — the `scan` check would never run and nothing would
  automerge. Fixing that means minting and rotating a PAT or GitHub App. The
  hosted app avoids all of it.

## Payoff trigger

Revisit if the Mend-hosted app changes pricing/limits for public repos, if the
repo grows real tests (add them to the required checks), or if majors pile up
unmerged (consider automerging majors for actions we pin by SHA anyway).
