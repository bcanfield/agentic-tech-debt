# Pillars of an Agentic Tech Debt Management System

## Why this document exists

This document defines the load-bearing pillars any **agentic tech debt
management system** built in this repository must follow. It bridges the
research in `tech-debt-management.md` and any concrete tool implementation.
Every pillar is grounded in that research; nothing here is opinion only.

**In scope.** The principles the system must obey, the functionality each
principle requires, when each pillar fires in a developer's day, the impact
on humans and agents, and the failure mode if the pillar is missing.

**Out of scope (next task).** Mapping pillars onto specific Claude Code
primitives (hooks, slash commands, sub-agents, MCP servers, output styles,
settings). Choosing third-party tools (SonarQube vs. CodeScene vs. CAST).
Implementation order or roadmap.

The pillars are tool-agnostic by design. The next document maps them to
Claude Code.

---

## Design tenets

The research converges on a small set of cross-cutting properties the system
must have. These are not pillars; they are the *style* in which every pillar
is implemented.

1. **Continuous over heroic.** Tech debt is steady-state, not project-shaped.
   Stop-the-world rewrites lose; continuous payment wins (Justin Grant's
   "tech budget" case study; Shopify's 25% rule; Microsoft Windows XP SP2 as
   the cautionary tale). The system runs all the time, not on a quarterly
   cleanup schedule.
2. **Graceful over punitive.** The system surfaces, suggests, and gates only
   where evidence justifies blocking. It treats the developer as a
   collaborator, not a defendant. Google's internal guidance: "improvement,
   not perfection."
3. **Evidence-based over opinion.** Behavioral hotspots are a stronger
   signal than static rules alone (one comparative University of Victoria
   study supports this; the field has not converged). DORA + rework rate
   is the outcome layer. Engineer-perception surveys catch what tools
   cannot. The system leans on this stack, not on individual taste.
4. **Visible over hidden.** Debt lives in the same backlog as features,
   tagged but not segregated. Separate backlogs reliably lose
   (Scrum.org / leadership.garden / volpis consensus). ADRs make
   architectural trade-offs searchable rather than tribal.
5. **Deterministic over vibes.** Agents are fast but careless contributors
   (Karpathy's "over-eager junior intern savant"). Their output is wrapped
   in deterministic feedback (tests, linters, type checks, code-health
   metrics), not in human vigilance alone.
6. **Pay down with the same tool that accrues debt.** GitClear shows AI
   creates more clones, more churn, less refactoring. The same agentic
   capability that creates that debt is turned around to pay it down
   (AWS Transform Custom; Spotify's background agent merging 1,500+ PRs;
   CodeScene ACE; Moderne).

A pillar that feels punitive, episodic, opinion-based, hidden, or vibes-based
is being implemented wrong.

---

## The Pillars

There are nine. Pillars 1–5 govern debt itself. Pillars 6–8 govern how agents
operate inside the system. Pillar 9 governs how the system uses agents as a
force multiplier for paydown.

### Pillar 1: Visibility

Every debt item is registered, classified, and discoverable.

**Statement.** No debt exists only in someone's head. Every debt item lives
in a single backlog with a structured record. Architectural debt gets an ADR.

**Research foundation.**
- Dagstuhl 16162 definition: debt is a *collection of design or
  implementation constructs*; you cannot manage what you have not named.
- One-backlog rule: separate tech-debt backlogs reliably lose to the
  feature backlog.
- Five-field debt entry (Kruchten/Nord/Ozkaya): principal, interest,
  affected hotspot/module, business capability impacted, payoff trigger.
- Fowler's quadrant + Google's 10 Jaspan/Green categories (migration, docs,
  testing, code quality, dead code, code rot, expertise, release,
  infrastructure, planning) for classification.
- ADRs (Nygard format) on Thoughtworks Adopt: Context / Decision /
  Consequences, checked into the repo.

**Required functionality.**
- A canonical debt registry any agent or human can read and write, living
  next to the code so it travels with the repo.
- A schema that enforces the five fields plus quadrant cell and category.
- An ADR collection (`doc/adr/`) with an enforced template.
- A way to create a debt entry or ADR in under a minute, ideally from the
  place the debt is observed: a code review, a failing test, an agent's own
  reasoning.

**When it activates.**
- A developer or agent makes an expedient choice ("I'll come back to this").
- Code review surfaces a smell that is not being fixed in the same PR.
- An architecturally significant decision is made by a human or an agent.
- An agent is about to take a shortcut it cannot justify.

**Developer impact.**
- The developer always knows where to put the thing they couldn't fix now.
- They can browse a coherent picture of what's outstanding instead of
  rediscovering it on call.
- Architectural decisions stop being tribal knowledge.

**Agent impact.**
- Agents read existing ADRs and debt entries before proposing changes that
  touch the affected modules. This prevents re-litigating settled
  trade-offs.
- Agents register the debt they are about to incur, with the same five
  fields, before completing a task that creates it. No silent expedience.

**Failure mode without it.** Reckless–inadvertent debt accumulates
invisibly, the most dangerous quadrant cell. New engineers and new agent
contexts re-discover and re-decide the same trade-offs. Debt grows faster
than it is found.

---

### Pillar 2: Continuous Measurement

Detect debt where it actually slows you down.

**Statement.** The system continuously measures debt at four layers
(static, behavioral, outcome, perception) and never relies on a single
signal.

**Research foundation.**
- The 2021 *Lack of Consensus Among Technical Debt Detection Tools* paper:
  static tools disagree heavily. No single tool is sufficient.
- Behavioral / hotspot analysis (CodeScene, Adam Tornhill): a comparative
  study at the University of Victoria suggests it surfaces more debt than
  pure static analysis, because it weights complexity by *change frequency*
  (an Ottawa-based paper cites CodeScene more peripherally; the field has
  not converged).
- DORA's metrics (lead time, deployment frequency, change failure rate,
  MTTR, plus **rework rate** added in 2024 and popularly called the "fifth
  metric") are the outcome layer; only ~7% of teams achieve rework rate
  <2% across recent reporting cycles.
- Google's quarterly engineer-hindrance survey catches debt no tool can see
  (docs, expertise, planning).
- CodeScene benchmarks (vendor whitepaper, not peer-reviewed): average
  industry hotspot Code Health is 5.15/10; AI-touched code needs ≥9.4/10
  to keep AI-induced bugs in check.

**Required functionality.**
- A static-analysis layer in CI (rule-based quality, e.g., the SQALE model).
- A behavioral / hotspot layer that ingests Git history and ranks files by
  the intersection of complexity and churn.
- An outcome dashboard tracking the five DORA metrics, with rework rate
  highlighted, broken out by team and module.
- A periodic engineer-perception survey (quarterly minimum) feeding the same
  registry as the tooling layers.
- A discriminator for **AI-touched code**: the system marks diffs an agent
  authored or co-authored and tracks their 30/60/90-day incident rate and
  14-day churn separately from human-only code.

**When it activates.**
- Every commit and every PR (static + hotspot delta).
- Continuously, in the background (DORA telemetry from CI/CD).
- Quarterly, prompted (perception survey).
- At every agent edit cycle (in-loop telemetry; see Pillar 7).

**Developer impact.**
- The developer gets early warning instead of post-incident shock.
- They see whether their changes are improving or worsening hotspot health
  *before* merging.
- They can point at numbers when arguing for paydown time.

**Agent impact.**
- Agents consult the same telemetry humans see; the code-health signal is
  part of their input, not an afterthought.
- Agents do not "succeed" at a task that worsens hotspot Code Health on
  files they touched without explicitly registering the new debt
  (Pillar 1) and obtaining a payoff trigger.

**Failure mode without it.** Debt grows silently. AI-induced regressions
(GitClear's observed correlations — 4× clones, ~doubled 14-day churn;
observational, not causal) accumulate as undetected maintenance cost.
The team relies on lagging incidents to discover what should have been a
leading indicator.

---

### Pillar 3: Hotspot-Targeted Prioritization

80/20, not vanity refactors.

**Statement.** Cleanup energy is directed at the small subset of code that
intersects active development and high complexity. Reckless–inadvertent
debt in those hotspots is paid down first; prudent–deliberate debt
elsewhere waits for its trigger.

**Research foundation.**
- Pareto pattern: McKinsey case studies report a small number of asset
  types (in one published case, around 20) drive the majority of an
  enterprise's debt; CodeScene shows ~20% of files generate ~80% of
  debt-related rework.
- Fowler's quadrant for triage: reckless–inadvertent first;
  prudent–deliberate only with an ADR-documented payoff trigger.
- Single backlog, prioritized against features, not segregated.
- Scoring frameworks: RICE, WSJF (Cost of Delay / job size), SQALE
  remediation cost, Tracy business-driven framework.

**Required functionality.**
- A ranking that combines hotspot score (complexity × churn) with business
  capability impact and Fowler quadrant cell.
- A way to see the ranking when planning a sprint, when picking the next
  task, and when an agent decides what to tackle in a refactor session.
- A guard against vanity refactors: code that is healthy or rarely changed
  is explicitly deprioritized.

**When it activates.**
- Backlog grooming and sprint planning.
- A developer or agent picks up "the next thing" to work on.
- The 15–20% paydown allocation is being scheduled (Pillar 4).
- An agent-driven refactor run is planned (Pillar 9).

**Developer impact.**
- The developer stops feeling cleanup work is arbitrary or political.
- They get a defensible answer to "why this and not that": the data, not a
  preference.
- They are protected from reviewers who would prefer to repaint a corner of
  a stable file rather than tackle the actual hotspot.

**Agent impact.**
- An agent told "fix tech debt" defaults to the top hotspots, not the file
  it just read.
- An agent considering an opportunistic refactor outside a hotspot is
  redirected, or required to justify it.

**Failure mode without it.** Cleanup work happens where it is *easy*
rather than where it pays off. Paydown allocation is consumed by satisfying
refactors that don't move DORA, while the actual hotspots continue to bleed.

---

### Pillar 4: Continuous Paydown

A protected allocation, every cycle.

**Statement.** A fixed 15–20% of every cycle is spent on prioritized debt
work, taken off the top before feature commitments. The Boy Scout Rule is
the always-on baseline. Fix-it weeks supplement, never replace, the steady
allocation. A bug cap acts as a forcing function when paydown lapses.

**Research foundation.**
- 15–25% per-sprint allocation is the convergent recommendation across
  Cagan, Microsoft Azure Boards, SAFe, Scrum.org, Shopify's 25% Rule, and
  Justin Grant's "tech budget" case study.
- Boy Scout Rule (Robert C. Martin): every PR leaves touched files
  measurably better. Baseline practice.
- Fix-it weeks (Spotify Hack Week, Atlassian ShipIt, Google fix-its) handle
  cross-cutting items that don't fit a sprint.
- Microsoft's bug cap (a small per-engineer cap, e.g., 4 bugs/engineer per
  Aaron Bjork's account; new feature work pauses if exceeded) is the
  forcing function.
- Stop-the-world rewrites are last resort and historically expensive
  (Windows XP SP2).
- Cultural reality: McKinsey, Google, and Scrum.org all warn that the
  technical solutions are well understood; the persistent failure is
  leadership pressure that lets feature work eat the allocation.

**Required functionality.**
- The system can count how much capacity is actually being spent on
  debt-tagged items per cycle and surface the gap.
- It produces reports an engineering leader can take to a CFO/CIO to defend
  the allocation.
- It supports a Boy Scout signal at PR time: "this PR touched files X, Y,
  Z; their Code Health went from A to B."
- It supports a fix-it-week mode (a temporary shift in capacity weights
  toward cross-cutting items) without becoming the only mode.
- It supports a bug-cap rule that can pause feature work programmatically
  when exceeded.

**When it activates.**
- Sprint planning (allocation).
- Every PR (Boy Scout rule check).
- Quarterly (fix-it week scheduling).
- Continuously (bug-cap monitoring).

**Developer impact.**
- The developer is given paid time to do the work they already know is
  needed, instead of stealing it from features at personal cost.
- They cannot accumulate a hidden rewrite burden that ambushes them later.
- They have explicit air cover from the system when feature pressure
  threatens the allocation.

**Agent impact.**
- Agents have a defined fraction of their working time allocated to
  paydown tasks (Pillar 9), drawn from the prioritized list (Pillar 3).
- Agents performing feature work still leave touched files measurably
  better (Boy Scout). Diffs that worsen Code Health on touched files
  trigger a deterministic gate (Pillar 7).

**Failure mode without it.** The allocation is the part everyone agrees to
and no one protects. Without explicit, measured, defended capacity, the
research is unanimous: feature work consumes it, debt compounds, and DORA
metrics decay.

---

### Pillar 5: Deliberate Architecture

ADRs convert inadvertent debt into deliberate debt.

**Statement.** Every architecturally significant decision, by a human or
agent, is captured as an ADR. The ADR makes the trade-off, the alternatives
considered, and the payoff trigger explicit and searchable.

**Research foundation.**
- ADRs (Nygard 2011, Thoughtworks Radar Adopt, AWS Prescriptive Guidance,
  Azure Well-Architected Framework, GDS Way, Red Hat).
- SEI / Kruchten-Nord-Ozkaya: architectural choices are the leading source
  of impactful debt, not micro-level smells.
- Fowler quadrant: ADRs are the canonical mechanism for moving debt from
  reckless–inadvertent to prudent–deliberate.
- ADRs as agent context: agents read ADRs to avoid re-litigating prior
  decisions (see Pillar 6).

**Required functionality.**
- An ADR template enforced in `doc/adr/`: title, status, context, decision,
  consequences, and (added by this system) a payoff trigger if the decision
  introduces deliberate debt.
- A way to detect when a change is "architecturally significant", even a
  rough heuristic (touching a public interface, a data model, a build
  pipeline, an auth surface), and prompt for an ADR.
- A bidirectional link between ADRs and the debt registry: if an ADR
  introduces deliberate debt, a registry entry is auto-created with the
  same payoff trigger.
- An index agents can read efficiently when given a task in an
  affected area.

**When it activates.**
- A public interface, data model, dependency, build/release pipeline,
  security boundary, or cross-team contract is touched.
- An agent is about to make a choice with multiple credible alternatives in
  a hotspot.
- Code review of any of the above.

**Developer impact.**
- New team members can read why something is the way it is, not just
  *that* it is.
- Architectural arguments can be settled by reference rather than by
  re-litigation in standup.
- Deliberate debt is no longer secret debt.

**Agent impact.**
- Agents read the ADR index before proposing changes in the affected area
  (mandatory context-loading).
- Agents draft ADRs when they are the ones making an architecturally
  significant decision; a human reviews and accepts the status.
- Agents do not silently override a prior ADR; doing so requires a new ADR
  superseding the old one.

**Failure mode without it.** Architectural decisions become tribal. The
same trade-off is re-debated every six months. Deliberate debt slides back
into reckless–inadvertent debt as institutional memory fades, the
"cognitive debt" gap Willison and Thoughtworks describe.

---

### Pillar 6: Persistent, Curated Agent Context

The project charter agents read every time.

**Statement.** A short, curated, persistent file (the agent charter)
encodes the project's stack, conventions, build/test commands, no-touch
zones, and pointers to ADRs. Agents read it on every task.

**Research foundation.**
- Persistent project rules (`CLAUDE.md`, `AGENTS.md`, `.cursorrules`,
  `copilot-instructions.md`, `GEMINI.md`) are now standard across Anthropic,
  Cursor, GitHub, and Google. Thoughtworks Radar Adopt: "curated AI
  instructions for software teams."
- HumanLayer / Anthropic best practice: keep these files *short*. Frontier
  models reliably attend to roughly 150–200 instructions; rely on linters,
  formatters, and hooks for the rest.
- Distinct from ADRs: ADRs answer "why is this thing the way it is"; the
  charter answers "how do we work here."

**Required functionality.**
- A canonical charter file (or small set of files) at a known location.
- An enforced size budget so the file does not bloat into uselessness.
- Sections covering stack, build/test/run commands, coding conventions,
  testing conventions, commit conventions, "do not touch" zones, links to
  the ADR index and debt registry, escalation rules ("when in doubt, ask").
- A mechanism for keeping it current. Stale charters are worse than none.

**When it activates.**
- Every agent invocation.
- Conventions change (a new linter, a new test runner, a new no-touch
  zone).
- An ADR is added that should be globally surfaced.

**Developer impact.**
- The developer stops re-prompting the same fundamentals on every task.
- Onboarding a new agent (or human) is reading one file, not crawling a
  wiki.
- The team has a single artifact to debate when conventions change.

**Agent impact.**
- The agent loads the charter on every task and treats it as authoritative.
- The agent flags charter conflicts (e.g., the charter says "no `any` in
  TypeScript" but the task asks for it) rather than silently complying.

**Failure mode without it.** Agents make different choices on different
days. Conventions drift. Engineers spend their attention re-stating the
basics instead of reviewing real work. The charter does not fix the
*cognitive debt* problem on its own, but its absence guarantees one.

---

### Pillar 7: In-Loop Deterministic Feedback

The gates wired into every agent edit.

**Statement.** After every agent edit, deterministic checks (linter, type
checker, test runner, code-health analyzer) run automatically. The agent
sees the result. The agent fixes the regression before the human sees the
diff. Quality gates the human enforces are also enforced on the agent,
in-loop.

**Research foundation.**
- Beck's *augmented coding*: TDD as a guardrail because agents will try to
  delete tests to make them pass. Deterministic gates make that impossible.
- Anthropic, Cursor, Thoughtworks: linters, type checkers, test runners,
  and code-health analyzers wired into post-tool-use hooks. Thoughtworks
  calls these "feedback sensors for coding agents."
- CodeScene CodeHealth MCP Server: deterministic Code Health exposure to
  agents. Benchmarks on a 25,000-file dataset showed 2–5× more code-health
  improvements vs. raw Claude Code (vendor benchmark, not peer-reviewed).
- DORA 2024: AI adoption increased throughput modestly but reduced delivery
  stability by 7.2% per 25% adoption increase, the regression these gates
  are designed to recover.
- IBM CAST + agentic AI work reports a similar 2–5× refactoring uplift
  with deterministic code-health feedback. Treat as the same vendor
  pattern as the CodeScene benchmark, not an independent corroboration.

**Required functionality.**
- A hook layer that fires after every meaningful agent edit (file write,
  multi-file refactor, dependency change).
- The hook layer runs at minimum: formatter, linter, type checker, the
  affected test slice, and a code-health probe on the touched files.
- Failures are returned to the agent in a structured form so it can act on
  them, not as opaque tracebacks.
- Auto-fix is applied where safe (formatter, simple lint rules); other
  failures block the agent until addressed.
- A non-bypassable rule: diffs that delete or weaken tests in order to make
  them pass are rejected.
- A non-bypassable rule: diffs that worsen Code Health on touched hotspots
  are rejected unless paired with a debt registry entry and ADR (Pillars 1
  and 5).

**When it activates.**
- After every agent file write.
- Before any agent claims a task is complete.
- Before any agent commit.
- At PR time (the human-visible enforcement layer is the same set of
  rules).

**Developer impact.**
- The developer can trust agent output enough to *review* it without
  *redoing* it.
- They are not the one catching the trivial mistakes a linter would catch.
  The agent already did.
- Their reviewer attention is reserved for design and intent.

**Agent impact.**
- The agent operates inside a tight, fast feedback loop and self-corrects
  against ground truth, not against its own narration.
- The agent's self-reported "done" cannot diverge from reality, because the
  gates have already run.
- The agent cannot achieve a green test suite by deleting tests.

**Failure mode without it.** The 2024 DORA stability regression and
GitClear's observed churn doubling (correlational evidence, not causal)
are the symptoms. Without deterministic in-loop feedback, agents ship
code that compiles in their head but breaks in the build. Humans become
unpaid reviewers of trivia. Stability decays.

---

### Pillar 8: Spec → Test → Review → Comprehend

Agent engineering discipline.

**Statement.** Non-trivial agent work begins with a written spec, proceeds
under TDD, is reviewed by an independent agent context (and a human), and
ends only when the human author can explain the resulting code.

**Research foundation.**
- Spec-driven development (GitHub Spec Kit, September 2025; AWS-Augment
  Code; JetBrains Junie patterns): specs replace prompts as the durable
  artifact.
- Beck (June 2025): augmented coding requires traditional engineering
  values (tidy code, complexity discipline, full test coverage) and TDD as
  a non-negotiable guardrail.
- Willison (October 2025 onward): "I won't commit any code to my repository
  if I couldn't explain exactly what it does to somebody else." The
  comprehensibility rule.
- Thoughtworks Radar v34: **Hold** on replacing pair programming with AI;
  Hold on complacency with AI-generated code.
- Anthropic best practices: writer/reviewer separation; a fresh agent
  context reviews diffs; a dedicated security sub-agent checks credentials,
  injection, and auth.
- *Cognitive debt* is what this pillar prevents: the code may be fine, but
  the team has lost the mental model. Distinct from technical debt; equally
  corrosive.

**Required functionality.**
- A lightweight spec format (a few hundred words is fine) that lives next
  to the work and is what the agent operates from.
- A TDD-first task mode: the agent (or human) writes the failing test
  first; the implementation pass is gated on having one.
- A reviewer pass with a *fresh* agent context, with no shared memory with
  the writer.
- A specialized security review for changes to auth, secrets, input
  handling, and dependencies.
- A comprehensibility gate at commit time: the human author signs off that
  they can explain the diff. For agent-authored changes that exceed a
  complexity-or-churn threshold, the agent produces a literate-program
  explanation and the human signs off on *that*.
- A pre-merge prompt for any module that has crossed a complexity-or-churn
  threshold: pause, have humans walk through it, or have the agent produce
  the explanation and the human verify.

**When it activates.**
- Task initiation (spec).
- During implementation (TDD loop, with Pillar 7 enforcing test integrity).
- Pre-commit (review and comprehensibility gate).
- Periodically (cognitive-debt walkthroughs at threshold crossings).

**Developer impact.**
- The developer never commits code they cannot explain, so they can
  support it on call.
- The developer's mental model keeps pace with the code, even when the
  code is being written faster than they would write it themselves.
- Reviews are shorter and sharper because the agent has already been
  reviewed by another agent.

**Agent impact.**
- The agent operates against a written spec, not a chat transcript.
- The agent writes a failing test before making it pass and cannot weaken
  or delete tests to fake success (Pillar 7 enforces this).
- The reviewer agent has no incentive to defend the writer's choices and
  is more likely to flag problems.

**Failure mode without it.** This is the cognitive-debt scenario Willison
and Thoughtworks named: code accumulates faster than understanding. The
team can ship and cannot debug. The METR study's 19% slowdown (one RCT,
n=16, early-2025 tools), *while developers believed they were 20% faster*,
is the perception-reality gap this pillar is designed to close — read it
as evidence the productivity claims are noisier than vendor reports
suggest, not as a settled measurement.

---

### Pillar 9: AI as a Paydown Engine

The same agents pay down what they help create.

**Statement.** Agentic capability is turned around to pay down debt.
Scheduled agent-driven refactor runs target the top hotspots, are guided by
code-health feedback (Pillar 7), and count toward the 15–20% paydown
allocation (Pillar 4).

**Research foundation.**
- AWS Transform Custom: claimed 80% time reduction for Java/Python/Node
  upgrades.
- IBM CAST + agentic AI hybrid for legacy modernization at portfolio scale.
- Spotify's background coding agent: 1,500+ merged PRs, half fully
  automated.
- CodeScene ACE; Moderne's Moddy; Refact.ai: an emerging category of
  agent-driven debt paydown.
- McKinsey 2025: AI is changing the economics of debt; legacy modernization
  that took years can be 40–50% faster and cheaper (a strategic projection,
  not a settled outcome). The strategic implication is to pay down more
  aggressively now, funded by the productivity gains, rather than the
  historical "manage indefinitely" posture.
- Counterweight: GitClear shows naive AI usage increases debt. This pillar
  is what turns AI from a debt accelerant into a debt amortizer.

**Required functionality.**
- A scheduling mechanism for agent refactor runs (cron-like or
  trigger-based on hotspot threshold crossings).
- A way for the run to draw its targets from the prioritized hotspot list
  (Pillar 3).
- The run executes under all of Pillars 6–8: it reads the charter, it is
  gated by deterministic feedback, it produces specs, it is reviewed by an
  independent agent context.
- The run's output is a normal PR, not a privileged direct commit. Humans
  remain in the merge loop.
- A budget: refactor runs consume a known share of the 15–20% allocation
  and are reported as such.

**When it activates.**
- On a scheduled cadence (e.g., weekly refactor runs).
- On a trigger (a hotspot crosses a Code Health threshold; rework rate for
  a module spikes; a fix-it-week mode is engaged).
- On an explicit human ask ("clean up module X").

**Developer impact.**
- The developer's paydown allocation produces visible, frequent wins
  rather than backlog churn.
- The boring work (dependency upgrades, dead code removal, test backfill,
  duplicate consolidation) is largely off their plate.
- Their reviewer attention is spent on agent-produced refactor PRs they
  can read and approve, not on writing them by hand.

**Agent impact.**
- Agents have a defined "second job": paying down debt, not just shipping
  features. Both jobs use the same discipline (Pillars 6–8).
- Refactor agents have access to the same telemetry humans use (Pillar 2)
  so they can choose targets the team would also choose.

**Failure mode without it.** The asymmetry GitClear documented persists:
agents accelerate debt creation but no one redirects them to paydown.
Allocation (Pillar 4) is funded but underused, because the human cost of
a manual cleanup PR is still higher than the human cost of a feature PR.
The system collects metrics it does not act on.

---

## How the pillars compose into an operating loop

The pillars form a loop, not a checklist. Mapped to the
Kruchten/Nord/Ozkaya **Identify → Measure → Decide → Resolve → Prevent**
cycle:

| Phase | Pillars | What happens |
|---|---|---|
| Identify | 1, 5 | Debt and decisions are registered. Nothing is invisible. |
| Measure | 2 | Static + behavioral + outcome + perception. AI-touched code tracked separately. |
| Decide | 3 | Hotspot ranking + Fowler triage drives what gets attention. |
| Resolve | 4, 9 | Protected allocation + Boy Scout + AI paydown engine. |
| Prevent | 6, 7, 8 | Charter + deterministic in-loop gates + spec/test/review/comprehend discipline. |

The loop runs continuously. The system's job is to keep it running with
the lowest possible friction for the developer, while making the
discipline non-negotiable for the agent.

---

## Anti-patterns the pillars are designed to prevent

These are the failure modes the research warns about. The pillars are
designed to prevent them. Naming them helps reviewers check the design.

- **A separate, ignored tech-debt backlog.** Pillar 1 forbids it.
- **A static-analysis-only dashboard.** Pillar 2 forbids it; behavioral
  and perception layers are required.
- **Vanity refactors of healthy code.** Pillar 3 forbids it; hotspot focus
  is mandatory.
- **A paydown allocation everyone agrees to and no one protects.**
  Pillar 4 requires the allocation be measured and defensible at executive
  level.
- **Tribal architecture.** Pillar 5 forbids it; ADRs are non-optional for
  significant decisions.
- **An ever-growing `CLAUDE.md` / `AGENTS.md`.** Pillar 6 imposes a size
  budget; the research is explicit that bloated charters lose effectiveness.
- **Agent output reviewed only by humans, only at PR time.** Pillar 7
  forbids it; gates run in-loop.
- **Vibe coding in production: free-form prompts, no spec, no TDD, no
  comprehensibility check.** Pillar 8 forbids it. Karpathy's own framing
  limits vibe coding to throwaways.
- **Using agents only to accrue debt, not to pay it down.** Pillar 9
  forbids it.
- **Punitive, blocking, opinion-based gates.** The design tenets forbid
  it. The system must be graceful, evidence-based, and continuous, or
  developers will route around it.

---

## Out of scope (next task)

The next task maps each pillar to specific Claude Code primitives (hooks,
slash commands, sub-agents, MCP servers, settings, output styles, the agent
SDK) and identifies gaps where Claude Code does not yet provide what a
pillar requires. This document stays tool-agnostic so the mapping can be
honest about gaps.

The research backing every pillar above is in `tech-debt-management.md`.
The mapping document references these pillars by number.
