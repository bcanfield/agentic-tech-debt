# 0020 — Telemetry stays local by default; sharing is opt-in donation

**Date:** 2026-06-05
**Status:** Proposed

## Context

We want to learn from real usage — to steer the roadmap and to make content
(a "debt of the week", a "State of AI Tech Debt" report). But
[`PRIVACY.md`](../../PRIVACY.md) publicly promises debt-ops "collects nothing…
no network connection of any kind", and the privacy-first posture is a brand
asset. The 2026 norm for developer tools has hardened toward opt-in (the
GitHub CLI opt-out launch drew a public backlash; Next.js and Claude Code's
own OpenTelemetry are opt-in/auditable). Full plan in
[`telemetry-collection-plan.md`](../telemetry-collection-plan.md).

## Decision

Telemetry stays **local by default** — we enrich the existing
`metrics.jsonl` and the `/debt-ops:metrics` skill with no network. Anything
leaving the machine happens only through an **explicit, user-reviewed
donation** (`/debt-ops:donate`, preferring a pre-filled GitHub issue over a
collector endpoint). No background phone-home, never any emission in
CI/non-interactive runs, payload inspectable before it sends (a
`DEBT_OPS_TELEMETRY_DEBUG`-style print mode), and pseudonymous via a random
install-UUID — not the path-derived `repo_hash`.

## What this means for you

- **Nothing changes by default.** debt-ops still writes only local files; the
  richer metrics are read by `/debt-ops:metrics` on your machine.
- **Donation is a deliberate act.** You run a command, *see* the exact
  anonymized aggregate, and choose to share it. Project content (debt bodies,
  file paths, prompts) is excluded by construction and by test.
- **PRIVACY.md updates only when the donation path ships** (the doc's
  Phase 2), describing the opt-in honestly and bumping its date.

## Alternatives we ruled out

- **Opt-out networked telemetry (GitHub CLI model).** Maximum data, but
  contradicts our stated values and invites the exact backlash GitHub CLI got;
  GDPR makes opt-out legally shaky in the EU.
- **Background opt-in telemetry (env-var collector, on but silent).** Cleaner
  analytics, but adds infra to run and a standing `PRIVACY.md` liability, and a
  collector SDK (PostHog/OTEL) violates "no new dependencies / stdlib-only
  hooks". Kept only as a fallback transport, not the default.
- **No network ever.** Simplest, but "debt of the week" would draw solely from
  our own dogfooding repos — too thin to ground content or cross-repo
  benchmarks.

## When to revisit

- If local Phase-0 signals raise a roadmap question we can't answer without
  cross-repo data, promote the donation path.
- If donation uptake is near-zero, the GitHub-issue UX is too heavy — revisit
  transport.
- If a GDPR/partner requirement lands, revisit pseudonymity and consent wording.
