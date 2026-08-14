# Telemetry Collection Plan

## Why this document exists

We want to learn from how debt-ops is actually used — to steer the roadmap
(what to build, what to cut) and to fuel content (a "debt of the week", an
annual "State of AI Tech Debt" report). This document names **what data is
worth collecting, why, and how** to collect it without breaking the
privacy-first promise the tool was built on.

**The gating constraint.** [`PRIVACY.md`](../PRIVACY.md) publicly states
debt-ops "collects nothing… no network connection of any kind." That promise
is an asset, not an obstacle. The plan keeps **local-by-default** and adds a
single **explicit opt-in donation** path the user reviews before anything
leaves the machine. No background phone-home, ever.

This plan inherits the project's house rules: **tripwires over precision**
([ADR 0001](./adr/0001-metrics-are-tripwires.md)), **skill over script when a
smart agent can reason** ([ADR 0002](./adr/0002-metrics-skill-not-script.md)),
**stdlib-only hooks, no new dependencies**, and **adapter parity** (anything
shared lands in every copy in the same change).

## What we already collect (local, today)

Six event types append to `<cache>/<repo-hash>/metrics.jsonl`, read by the
`/debt-ops:metrics` skill:

| Event | Emitter | Fields |
|---|---|---|
| `session` | `session-start.py` | `registry_count`, `adr_count`, `ai_authored_count`, `adr_dir`, `registry_dir` |
| `edit` | `feedback.py` | `file`, `registry_count` |
| `feedback` | `feedback.py` | `file`, `result` (pass/fail) |
| `register` | `register.py` | `slug`, `ai_authored`, `letter` |
| `review` | `review.py` | `total`, `stale`, `cold`, `active` |
| `drop` | `drop.py` | `slugs`, `missed` |

Plus the registry frontmatter itself — `quadrant`, `category`, `principal`,
`interest`, `hotspot`, `business_capability`, `payoff_trigger`, `ai_authored`,
`created` — which is the richest part of the dataset and already on disk.

## Two purposes, two very different data shapes

The data splits cleanly by intent. Keeping them separate is what lets most of
the value stay zero-network.

### Purpose A — Shape the tool (product signals)

Quantitative, structural, **no project content**. Almost all of it can be
collected and surfaced **locally** with no privacy change — it just improves
the `/debt-ops:metrics` skill. We donate it only in aggregate (Purpose B's
transport), never per-event.

- **Activation funnel / time-to-value** — install → first edit → first
  registration. Tests the core bet ("value on the first edit"). *New.*
- **Discipline firing rate** — registrations/session, ADRs/session. *Have it.*
- **Feedback-loop health** — pass rate, fail→pass rate (*have it*) **plus
  command timeout rate and per-fire latency** (*new*). Directly measures the
  3 s budget and the project's #1 anti-pattern, hook-latency creep.
- **Skill-usage frequency** — which skills fire, how often. Feeds the explicit
  "remove any skill used <1×/week" rule, which currently has no data. *New.*
- **Drop friction** — `missed` letters, drop frequency. *Partly have it.*
- **Adapter & environment shape** — claude/codex/copilot; detected language/
  ecosystem, repo-size bucket, test presence. *New, derived from existing
  manifest detection.*
- **Errors** — hook failures, malformed `feedback.list`. *New.*

### Purpose B — Content & research ("debt of the week")

Qualitative and aggregate. This is the differentiated angle, and it is
fundamentally more sensitive because the interesting parts include debt
**titles and bodies**. It therefore lives entirely behind explicit opt-in
donation, and the headline stories come from the registry, not the counters:

- **"What kind of debt does AI create?"** — category (Jaspan 10) and quadrant
  (Fowler) distributions across repos. Headline metric: **AI-authored share
  and its trend** — extends the GitClear/DORA findings the project already
  cites in [`tech-debt-management.md`](./tech-debt-management.md).
- **Lifecycle stories** — register → dropped / still-active / paid-down, with
  time-to-paydown distributions. "How long does AI debt survive?"
- **Self-correction evidence** — fail→pass rate as proof the deterministic
  Pillar-7 loop works. Strong, research-grounded blog material.
- **"Debt of the week"** — a single anonymized entry (biggest `principal`,
  most `reckless-deliberate`, best title). Needs body text → only ever via a
  deliberate per-item share action, never background telemetry.
- **Benchmarks as a feature** — "your AI-authored debt share vs the median"
  closes the perception/benchmark layer deferred from v1, and gives users a
  concrete reason to *want* to opt in.

## How — phased, so privacy only gates the later phases

### Phase 0 — Enrich local metrics (zero network, do regardless)

Add fields/events to the existing `metrics.jsonl` and teach `/debt-ops:metrics`
to report them. No privacy change, no `PRIVACY.md` edit. Stdlib only; propagate
across all adapters in the same change per the parity rule.

- `feedback` event gains `latency_ms` and a `timeout` count.
- New `skill_used` event (skill name, ts) emitted by each skill's script.
- `session` event gains `adapter` and `language`/`ecosystem` tags.
- An activation marker (first-edit, first-register timestamps) in cache.
- `/debt-ops:metrics` report gains funnel, latency, and skill-usage lines.

### Phase 1 — Local export / inspect (zero network)

A `/debt-ops:export` skill (and/or a `DEBT_OPS_TELEMETRY_DEBUG=1` print mode,
mirroring Next.js's `NEXT_TELEMETRY_DEBUG`) that prints the **exact anonymized
aggregate** a donation would send. This builds the schema and the trust
artifact *before any network exists* — the user can read the payload byte for
byte.

### Phase 2 — Opt-in donation (requires PRIVACY.md rewrite + ADR 0020)

The user, on demand, shares the reviewed aggregate. Transport — we pick the
GitHub-native option as primary because it fits the zero-infra, stdlib,
GitHub-centric ethos and shows the payload before it's sent:

- **Primary — `/debt-ops:donate` opens a pre-filled GitHub issue/PR** with the
  aggregate. No server to run, no PII pipeline, user reviews and submits
  manually. Maximally on-brand.
- **Fallback — stdlib `urllib` POST** behind `DEBT_OPS_TELEMETRY=1`, off by
  default, **never prompts or emits in CI/non-interactive runs**, one-time
  interactive consent. More standard, but adds infra + ongoing
  `PRIVACY.md` liability. Avoid PostHog/OTEL SDKs — they violate "no new deps"
  and "stdlib-only hooks".

Consent hygiene either way (grounded in the CLI-telemetry best practices and
GDPR notes in the research): pseudonymous random install-UUID in cache (**not**
the path-derived `repo_hash`, which is guessable), a documented + minimal
schema, **PII-exclusion tests as guardrails**, and best-effort/fire-and-forget
so donation can never break a command.

### Phase 3 — Content pipeline

Aggregate donated data → "debt of the week" and a periodic "State of AI Tech
Debt" report. The aggregation can itself be a skill, consistent with ADR 0002.

## What changes in PRIVACY.md (Phase 2 only)

Phases 0–1 need no change. Phase 2 replaces the absolute "no network of any
kind" with an honest description of the **opt-in, user-reviewed donation**:
what it can include, that it is off by default and never fires in CI, how to
inspect the payload (Phase 1), and how to opt back out. The "last updated" date
bumps. ADR 0020 records the decision and its trigger to revisit.

## Anti-patterns to avoid (from the project's own rules)

- **No background phone-home.** Donation is always an explicit user act.
- **No catch-all "collect everything".** Every field answers a named question;
  sensitive classes (file contents, paths, env vars, prompts) are excluded by
  construction and by test — the same line Next.js and Claude Code's OTEL draw.
- **No new dependencies.** Transport is stdlib `urllib` or a GitHub issue.
- **No footprint in the user's repo.** Cache only, same as today.
- **Stay coarse where coarse is enough** (ADR 0001) — add precision when a
  tripwire actually trips, not before.

## When to revisit

- If Phase 0 local signals show a clear roadmap question we can't answer
  without cross-repo data, prioritize Phase 2.
- If donation uptake is near-zero, the GitHub-issue UX is too heavy — revisit
  transport.
- If the EU/GDPR posture or a partner requires it, revisit pseudonymity and the
  consent prompt wording.
