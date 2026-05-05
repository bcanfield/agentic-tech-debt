# Managing Technical Debt in Agentic Codebases

A research-grounded reference. Every claim cites a source.

## Summary

Three decades of debt research and 2024–2026 practitioner data point to one operating model: a continuous, hotspot-targeted loop. Debt items live in a single backlog, classified by Fowler's quadrant and the Dagstuhl 16162 definition. Prioritization follows behavioral hotspots (CodeScene, Google). Paydown takes 15–20% of every sprint, reinforced by the Boy Scout Rule. Architecture Decision Records make trade-offs explicit. DORA plus rework rate is the outcome layer. For agentic coding, the loop is wrapped in deterministic feedback gates: tests, linters, type checks, code-health MCP servers running inside the agent's edit cycle.

The cost is well-quantified. Stripe found developers lose ~42% of their week to debt. McKinsey CIOs put debt at 20–40% of IT estate value. CISQ (2022) priced US accumulated debt at ~$1.52T. DORA 2024 found a 25% increase in AI adoption tracked with a 7.2% drop in delivery stability, the symptoms GitClear confirms in 211M lines: 4× more clones, doubled short-term churn, refactoring rates falling from 25% to under 10% of changes.

The consensus among Karpathy, Willison, Beck, Anthropic, and Thoughtworks: AI requires more engineering discipline than human-written code, not less. Spec-driven prompts. TDD around every agent loop. Persistent project rules in `CLAUDE.md` / `AGENTS.md`. MCP-based code-health feedback. Willison's rule: do not commit code you cannot explain.

---

## Findings

1. **A community-consensus academic definition exists.** Cunningham's 1992 OOPSLA framing ("shipping first-time code is like going into debt") was extended at Dagstuhl 16162 (Avgeriou, Kruchten, Ozkaya, Seaman, 2016) into the working definition adopted across SEI, IEEE Software, and the TechDebt conference series: *"a collection of design or implementation constructs that are expedient in the short term, but set up a technical context that can make future changes more costly or impossible."* Kruchten/Nord/Ozkaya operationalize it in *Managing Technical Debt* (Addison-Wesley/SEI Series, 2019).

2. **Fowler's quadrant remains the most useful triage tool** (deliberate vs. inadvertent × prudent vs. reckless). Google's empirical work (Jaspan & Green, IEEE Software 2023, *Defining, Measuring, and Managing Technical Debt*) extended it to 10 measured categories. Migrations, documentation gaps, testing gaps, and code quality were the top hindrances Google engineers reported.

3. **The cost is large and well-quantified.** Stripe's *Developer Coefficient* recorded 13.5 hr/week on tech debt + 3.8 hr/week on bad code (~42% of a 41.1-hour week). McKinsey's CIO survey put debt at 20–40% of IT estate value before depreciation; 60% of CIOs said debt had grown perceptibly in the last three years. CISQ (2022) estimated US accumulated debt at $1.52T of a $2.41T total cost of poor software quality. Gartner has projected that organizations actively managing debt achieve 50%+ faster service delivery.

4. **Working frameworks converge on a small set of practices.** SQALE (the open ISO 25010 method behind SonarQube) computes principal and interest in remediation hours. CodeScene's behavioral analysis, validated as more predictive than static analysis at the University of Ottawa and University of Victoria, prioritizes by *hotspot*: the intersection of complexity and change frequency. CAST and SIG handle portfolio scoring. All converge on the same loop: identify, quantify, prioritize by carrying cost, pay down at hotspots.

5. **Continuous payment beats heroic rewrites.** Shopify Engineering's "25 percent rule," Microsoft's bug-cap policy, and Scrum.org / SAFe guidance all allocate **15–25% of every sprint** to debt, with the Boy Scout Rule covering incidental cleanup. Periodic fix-it weeks and Spotify-style hack weeks complement the steady allocation; they don't replace it. Justin Grant's case study contrasting Microsoft's year-long Windows XP SP2 stop-the-world effort with a continuous "tech budget" model shows the latter consistently outperforms.

6. **Architecture Decision Records (ADRs)** convert *inadvertent* debt into *deliberate, documented* debt. Michael Nygard's 2011 format, now in the Thoughtworks Radar's Adopt ring, captures each architecturally significant decision as a short Markdown record (Context / Decision / Consequences) checked into the repo.

7. **DORA is the right outcome layer**, especially after rework rate was added as a fifth metric in 2024. The 2024 report found AI adoption raised throughput modestly but cut delivery stability by 7.2% per 25% adoption increase. The 2026 research notes only 6.9% of teams achieve a rework rate below 2%. Thoughtworks now recommends DORA as the early-warning signal for AI-induced debt.

8. **AI-generated code creates a new debt class.** GitClear's 2024 and 2025 longitudinal studies (211M LOC, 2020–2024) found:
   - Refactoring/"moved" code dropped from ~25% of changed lines (2021) to <10% (2024).
   - Copy/paste lines exceeded moved lines for the first time in two decades.
   - Duplicate blocks rose ~4×; short-term churn (lines reverted within 2 weeks) ~doubled.
   - These are the symptoms classical software-engineering literature uses to predict future maintenance burden.

   The METR randomized controlled trial (arXiv:2507.09089, July 2025) further found experienced open-source developers were on average 19% *slower* with early-2025 AI tools while believing they were 20% faster.

9. **Practitioner thought leaders converge on "vibe engineering" / "augmented coding."** Karpathy coined "vibe coding" in February 2025; by mid-2025 Willison, Beck, Andrew Ng, and Thoughtworks had repositioned the responsible practice. Willison's rule: *"I won't commit any code to my repository if I couldn't explain exactly what it does to somebody else."* Beck's *augmented coding*, demonstrated in BPlusTree3, treats AI agents as "unpredictable genies" requiring TDD as a non-negotiable guardrail. Willison and Thoughtworks now use *cognitive debt*, distinct from technical debt, for the loss of human mental model when agents write faster than reviewers can comprehend.

10. **Tooling has caught up.** Anthropic, Cursor, GitHub, and Google ship persistent project-instruction files (`CLAUDE.md`, `AGENTS.md`, `.cursorrules`, `copilot-instructions.md`). CodeScene's CodeHealth MCP Server (2025) and IBM's CAST + agentic AI work show AI agents perform 2–5× better refactoring when given deterministic code-health feedback in their loop. AWS Transform Custom and Spotify's background coding agent (1,500+ PRs, half fully automated) demonstrate enterprises now use AI to *pay down* debt at scale.

---

## Details

### 1. Foundations: Cunningham to Dagstuhl

Ward Cunningham introduced the metaphor in the 1992 OOPSLA WyCash experience report: *"Shipping first-time code is like going into debt. A little debt speeds development so long as it is paid back promptly with a rewrite… Every minute spent on not-quite-right code counts as interest on that debt."* McConnell (Construx, 2007) added the *intentional vs. unintentional* axis. Fowler's 2009 *Technical Debt Quadrant* added *prudent vs. reckless*; the most dangerous cell is reckless–inadvertent.

Dagstuhl 16162 (Avgeriou, Kruchten, Ozkaya, Seaman, 2016) produced the consensus definition above and a research roadmap that defined the modern field. The 2019 Kruchten/Nord/Ozkaya book is the most cited practitioner reference. SEI's field studies find that practitioners broadly accept the "expedient short term" framing, and that *architectural choices*, not micro-level code smells, are the leading source of impactful debt.

### 2. Empirical evidence on impact

- **Stripe Developer Coefficient (2018):** 13.5 hr/week on tech debt + 3.8 hr/week on bad code = 17.3 hr (~42%) of a 41.1-hour week, self-reported.
- **McKinsey "Tech debt: Reclaiming tech equity" (2020) and "Breaking technical debt's vicious cycle" (2023):** 20–40% of technology estate value is tech debt; 30% of CIOs say >20% of new-product budget is diverted to debt; managing debt frees up to 50% more engineer time for value-creating work.
- **CISQ "Cost of Poor Software Quality in the US: A 2022 Report":** US tech debt principal estimated at $1.52T; total cost of poor software quality at $2.41T. Read these as orders of magnitude, not precise figures, since they are top-down estimates.
- **Google internal survey (Jaspan & Green, 2023):** A substantial percentage of Google engineers report being hindered by unnecessary complexity each quarter; 10 categories of debt identified, with migrations, docs, testing, and code quality dominating.
- **DORA 2024:** A 25% increase in AI adoption was associated with a 1.5% throughput drop and a 7.2% stability drop; rework rate added as the fifth DORA metric.

### 3. Measurement frameworks

|Layer|Tools / Methods|Strengths|Weaknesses|
|---|---|---|---|
|**Static rule-based**|SonarQube (SQALE), Checkstyle, PMD|Cheap, language-agnostic, CI-integrable; produces remediation-hour estimates|Snapshot only; flags many low-impact issues; the 2021 arXiv "Lack of Consensus" study showed major tools disagree heavily|
|**Behavioral / hotspot**|CodeScene (CodeHealth + Hotspots), Adam Tornhill's *Your Code as a Crime Scene* approach|Combines complexity with change frequency to surface what actually costs you; peer-reviewed accuracy edge over SonarQube|Requires Git history; needs licensing for full enterprise use|
|**Portfolio / architecture**|CAST Highlight, SIG, Structure 101, NDepend|Cross-application, executive dashboards|Heavyweight; expensive; less actionable for individual devs|
|**Outcome metrics**|DORA (lead time, deployment frequency, change failure rate, MTTR, **rework rate**) plus team-survey instruments|Connects engineering to business outcomes|Lagging indicators|
|**Engineer-perception survey**|Google's quarterly hindrance survey; SPACE framework|Catches debt that tools cannot (docs, expertise, team)|Subjective; quarterly cadence is lagging|

The pragmatic recommendation in Kruchten/Nord/Ozkaya, Tornhill, and Jaspan/Green: combine at least one structural metric with DORA outcomes and a quarterly engineer-hindrance survey. No single tool is enough.

### 4. Prioritization

- **Fowler's quadrant for triage.** Address reckless–inadvertent debt aggressively. Leave prudent–deliberate debt only with an explicit pay-back trigger documented in an ADR.
- **Hotspot rule (Pareto).** McKinsey reports 10–15 assets typically drive the majority of an enterprise's debt. CodeScene research shows ~20% of files generate ~80% of debt-related rework. Prioritize debt that intersects active development.
- **Scoring frameworks.** RICE, WSJF (Cost of Delay / job size), and SQALE remediation cost vs. business impact matrices are most commonly cited. The *Tracy* framework (arXiv:1908.00150) maps debt items to business processes for explicit ROI.
- **One backlog, not two.** The leadership.garden / volpis / Scrum.org consensus: a separate "tech debt backlog" reliably loses to the feature backlog. Debt items belong in the same prioritized list, simply tagged.

### 5. Pay-down strategies

|Strategy|When it works|Source|
|---|---|---|
|**Boy Scout Rule** ("leave the campground cleaner")|Always; baseline practice|Robert C. Martin, *Clean Code*; *97 Things Every Programmer Should Know*|
|**15–25% per-sprint allocation**|Default for most teams|Marty Cagan; Microsoft Azure Boards guidance; SAFe; Scrum.org; Justin Grant's "tech budget" case study; Shopify's 25 Percent Rule|
|**Periodic refactor sprints / fix-it weeks**|Larger refactors, dependency upgrades, rare interventions|Spotify Hack Week; Atlassian ShipIt; Google fix-its|
|**Bug cap** (e.g., 3 bugs/engineer max; new features pause until under cap)|Production-quality regulated systems|Microsoft Azure DevOps team practice|
|**Tech-debt or platform team**|Very large enterprises|McKinsey app-modernization factories|
|**Stop-the-world rewrite**|Last resort; high risk|Microsoft Windows XP SP2 (lost an estimated billions of upgrade revenue)|

The empirical pattern: continuous + Boy Scout + the occasional fix-it week, all measured, beats every other approach.

### 6. Architecture Decision Records

Michael Nygard's 2011 format (Title / Status / Context / Decision / Consequences) is a Markdown file checked into the repo (`doc/adr/0001-…md`). Adopted by Thoughtworks (Adopt ring), AWS Prescriptive Guidance, the Azure Well-Architected Framework, GDS Way, and Red Hat. ADRs convert reckless–inadvertent debt into prudent–deliberate debt by making each trade-off explicit and searchable. They double as agent context: AI agents read ADRs from the repo to understand prior decisions and avoid re-litigating them.

### 7. Tech debt in agentic / "vibe coding" contexts

Karpathy coined *vibe coding* on February 6, 2025 ("fully give in to the vibes, embrace exponentials, and forget that the code even exists"). Collins named it Word of the Year 2025. The empirical record is now substantial.

**Quality regression evidence (2024–2026):**

- **GitClear 2024 & 2025 (211M lines):** refactoring share fell from ~25% (2021) to <10% (2024); copy/paste exceeded moved code for the first time; duplicate-block prevalence ~4×; lines reverted within two weeks ~doubled.
- **DORA 2024:** AI adoption raises individual productivity but cuts stability by 7.2% per 25% adoption increase.
- **METR (arXiv 2507.09089, July 2025):** experienced OSS developers using Cursor Pro + Claude 3.5/3.7 were 19% *slower* (95% CI [+2%, +39%]) than without AI, while *believing* they were 20% faster. METR has since redesigned the experiment because so many developers refused to work without AI in 2026, biasing the population.
- **Ahmad et al. (arXiv 2512.11922, prepared for IEEE Software):** the first peer-style empirical experience report on the flow–debt trade-off in vibe coding, attributing accumulated debt to architectural inconsistencies, security vulnerabilities, and process-level weaknesses. Manuscript "prepared for IEEE Software," not yet peer-reviewed; cite with that caveat.
- **CodeScene benchmarks (2025):** average industry hotspot Code Health is 5.15/10; AI agents need ≥9.4/10 to keep AI-induced bugs in check; agent-driven refactoring fixes fewer smells the healthier the code already is.

**Cognitive debt.** Distinct from technical debt: the code may be fine, but the team has lost the mental model. Articulated by Willison (February 2026) and adopted in Thoughtworks Technology Radar v34, which calls AI "introducing a wider gap between humans and software systems."

**Practitioner-leader frameworks:**

- **Karpathy.** Vibe coding is fine for throwaways; in production, "keep a very tight leash on this new over-eager junior intern savant."
- **Willison ("vibe engineering," October 2025; "agentic engineering patterns," 2026).** Review every line; spec-driven; TDD; commit early and often; run multiple agents in parallel only after fundamentals are in place.
- **Beck ("Augmented Coding: Beyond the Vibes," September 2025).** Maintain traditional engineering values (tidy code, complexity discipline, full test coverage); use TDD as a guardrail because "agents keep trying to delete tests to make them pass."
- **Anthropic (How Anthropic Teams Use Claude Code, 2025; Best Practices docs).** Start from clean git state, commit often, use `CLAUDE.md` for persistent project context, use sub-agents for security and code review, run multiple Claude instances with writer/reviewer separation.
- **Thoughtworks Radar v34 (2026).** Adopt: DORA metrics, ADRs, continuous compliance, curated AI instructions for software teams (`AGENTS.md`). Hold: replacing pair programming with AI; complacency with AI-generated code.

**Tooling for AI-debt mitigation:**

- **Persistent project rules.** `CLAUDE.md`, `AGENTS.md`, `.cursorrules`, `.github/copilot-instructions.md`, `GEMINI.md`. Best practice (HumanLayer, Anthropic): keep these short (a few hundred lines max); encode coding standards, build/test commands, architectural conventions; rely on linters and formatters via hooks for the rest.
- **Spec-driven development.** GitHub Spec Kit (September 2025), AWS-Augment Code, JetBrains Junie patterns. Specs replace prompts as the durable artifact agents work from.
- **In-loop deterministic feedback.** Linters, type checkers, test suites, mutation testing (cargo-mutants), fuzz testing (WuppieFuzz), and code-health analyzers wired into agent post-tool-use hooks. Thoughtworks calls these "feedback sensors for coding agents."
- **MCP-based code health.** CodeScene's CodeHealth MCP Server exposes Code Health metrics deterministically to agents; benchmarks on a 25,000-file dataset showed 2–5× more code-health improvements vs. raw Claude Code.
- **AI-driven paydown of legacy debt.** AWS Transform Custom (Java/Python/Node upgrades, claimed 80% time reduction), IBM CAST + agentic AI hybrid, Spotify's background coding agent (1,500+ merged PRs, half fully automated), CodeScene ACE, Moderne's Moddy, Refact.ai.

---

## Recommended approach: Continuous Tech Debt Operations (CTDO)

One approach scales from solo developer to Fortune 500: a four-layer loop following Kruchten/Nord/Ozkaya's Identify–Measure–Decide–Resolve–Prevent cycle, with hotspot prioritization (CodeScene/Google), DORA outcomes, and AI guardrails (Beck/Willison/Anthropic/Thoughtworks).

### Layer 1: Make all debt visible (Register)

1. **One backlog.** All debt items live in the same product backlog, tagged `tech-debt`, classified by one of the 10 Google–Jaspan categories (migration, docs, testing, code quality, dead code, code rot, expertise, release, infrastructure, planning) and a Fowler quadrant cell.
2. **ADRs for every architecturally significant decision** (Nygard format, in `doc/adr/`). Reckless–inadvertent debt that code review surfaces becomes a prudent–deliberate ADR with a payoff trigger.
3. **A debt entry has 5 fields:** principal (estimated hours), interest (qualitative cost-of-delay or quantitative slowdown if measurable), affected hotspot/module, business capability impacted, payoff trigger.

### Layer 2: Measure (Detect)

1. **Static + behavioral analysis in CI.** SonarQube (SQALE) for rule-based gates; CodeScene (or equivalent) for hotspot + Code Health. Quality gates block merges that worsen hotspot health.
2. **DORA + rework rate** as the outcome dashboard, tracked per team and per module.
3. **Quarterly hindrance survey** (Google-style) for the debt no tool can see (docs, expertise, planning).

### Layer 3: Pay down (Resolve)

1. **15–20% per-sprint capacity allocation** for prioritized debt items, taken off the top before feature commitments (Cagan / Justin Grant / Shopify pattern). Treat as inviolable; report exceptions explicitly.
2. **Boy Scout Rule** as the daily baseline. Every PR leaves touched files measurably better. This is the always-on layer.
3. **80/20 hotspot focus.** Direct the per-sprint allocation at the top 10–20 hotspots from behavioral analysis. Skip vanity refactors.
4. **Quarterly fix-it week** for cross-cutting items (dependency upgrades, migration completions) that don't fit a sprint.
5. **Bug cap** (Microsoft pattern): ≤3 open bugs/engineer; exceeding it pauses new feature work.

### Layer 4: Prevent (Definition of Done + agent guardrails)

1. **Definition of Done** includes test coverage threshold, lint/type clean, ADR if architecturally significant, no Code Health regression on touched files.
2. **Code review for code health, not perfection.** Google's "improvement, not perfection" standard.
3. **For AI/agentic work, the non-negotiables:**
   - **Persistent project context** in `AGENTS.md` (preferred for cross-tool) and/or `CLAUDE.md`: stack, conventions, build/test commands, "do not touch" zones, links to ADRs. Keep it focused; research suggests frontier models attend reliably to ~150–200 instructions.
   - **Spec-driven prompts.** Every non-trivial task starts from a written spec (GitHub Spec Kit pattern), not a free-form chat.
   - **Tests-first / TDD with the agent** (Beck's augmented coding). Write the failing test, then let the agent make it pass. Reject diffs that delete or weaken tests.
   - **Deterministic feedback gates inside the agent loop.** PostToolUse hooks running linter, typechecker, test runner, and code-health MCP after every edit, with auto-fix where safe.
   - **Writer/reviewer separation.** A fresh agent context reviews diffs; a security sub-agent (Anthropic's pattern) checks credentials, injection, and auth.
   - **Mandatory comprehensibility rule** (Willison). No commit of code the human author cannot explain to a teammate.
   - **Cognitive-debt countermeasure.** When a module crosses a complexity-or-churn threshold, pause. Have humans walk through it, or have the agent produce a literate-program explanation for human review.
   - **Use AI to pay down debt, not just accrue it.** Schedule agent-driven refactoring runs targeting hotspot files, guided by code-health MCP feedback, as part of the 15–20% allocation.

### KPIs

|KPI|Target / Direction|Source|
|---|---|---|
|DORA Lead Time for Changes|Down|DORA|
|DORA Change Failure Rate|Down|DORA|
|DORA Rework Rate (5th metric, 2024)|<2% (only top 6.9% of teams achieve this)|DORA 2026|
|Time-to-restore (MTTR)|Down|DORA|
|% engineers reporting "hindered by debt"|Down quarter-over-quarter|Google Jaspan/Green pattern|
|Hotspot Code Health (CodeScene scale 0–10)|≥9.0 for human-touched code; ≥9.4 for AI-touched code|CodeScene research|
|SQALE technical debt ratio|<5%|SonarQube standard|
|% sprint capacity actually spent on debt|15–25%|Cagan / Shopify / SAFe|
|AI-touched code: 30/60/90-day incident rate|Equal to or better than human-only|Faros AI / Exceeds AI 2026 guidance|
|AI-touched code: 30-day churn (lines reverted within 14 days)|Trending toward pre-AI baseline (~3% in 2020 per GitClear)|GitClear|
|ADR coverage of architecturally significant decisions|100%|Thoughtworks Adopt|

### Scaling

- **Solo or small team.** GitHub repo with `doc/adr/`, an `AGENTS.md`, SonarCloud or CodeScene Community on PRs, a single tagged backlog, a personal Boy Scout commitment, two days every ten-day sprint on debt, and Claude Code or Cursor with TDD-first prompts and a PostToolUse lint hook.
- **Mid-size enterprise (50–500 engineers).** Add a platform team owning the Code Health MCP, an internal ADR template, the quarterly hindrance survey, DORA dashboards per team, a quarterly fix-it week, and a debt-portfolio review at engineering-leadership level.
- **Fortune 500.** Add CAST or SIG portfolio-level scoring (the McKinsey debt-balance-sheet pattern), an application-modernization factory for the 10–15 assets driving the majority of debt, agent-based modernization tooling (AWS Transform Custom, IBM Code Transporter, Moderne, a Spotify-style background coding agent), and CFO/CIO trade-off conversations using SQALE-derived dollar figures.

---

## Caveats and open questions

- **The big-dollar figures (Stripe $3T, CISQ $1.52T, McKinsey 20–40%) are top-down economic estimates**, not audited measurements. Useful for executive framing, not for budgeting any specific decision.
- **Tool disagreement is real.** The 2021 arXiv paper *On the Lack of Consensus Among Technical Debt Detection Tools* (Lefever et al.) found commercial tools agree poorly on what code is "debt." Behavioral approaches (CodeScene) appear to outperform pure static analysis in the Ottawa and Victoria studies, but the field has not converged.
- **The METR study (19% slowdown) is a single RCT on 16 experienced OSS developers in early 2025.** Newer agents (Claude Sonnet 4+ / Opus 4.5+, Cursor Composer 2, Codex CLI, Gemini CLI) post-date the study. METR has been unable to reproduce the design in 2026 because of selection bias from refusal to work without AI. Read it as evidence that AI productivity claims are noisier than vendor reports suggest, not as a settled finding.
- **GitClear's data is observational.** It correlates AI-tool adoption with quality regressions but cannot fully isolate the AI effect from confounders (more junior developers, higher delivery pressure, etc.).
- **Vibe-coding debt projections** circulating in 2026 trade press ("$1.5T by 2027," "vibe-coded projects accumulate debt 3× faster") are vendor-blog projections, not peer-reviewed; treat them as illustrative. The peer-reviewed evidence base on agentic-coding debt is still thin. The most credible items are the GitClear longitudinal studies, the METR RCT, the DORA 2024 report, and the Ahmad et al. IEEE Software experience report.
- **MCP-based and agent-driven refactoring tooling is brand new.** CodeScene's CodeHealth MCP, AWS Transform Custom, IBM's CAST + agent fusion, and Spotify's background coding agent are all 2025–2026 products. Long-run effectiveness is not yet independently validated.
- **Cultural and incentive issues dominate.** McKinsey, Google, and Scrum.org all stress that the technical solutions are well understood; the persistent failure mode is leadership pressure that lets feature work eat the 15–20% allocation. Without executive-level commitment to protect debt time, no framework holds.
- **The trade-off curve may be shifting.** McKinsey (2025) and Anthropic argue AI is changing the economics of debt: legacy modernization that previously took years can be 40–50% faster and cheaper with agentic AI. If that holds, the right strategic move for some enterprises is more aggressive paydown now, funded by AI productivity gains, rather than the historical "manage it indefinitely" posture. This is a strategic bet, not a settled fact.

---

The bottom line, supported across thirty years of literature and 2024–2026 practitioner evidence: make debt visible, measure it where it actually slows you, pay it down continuously at hotspots, document deliberate trade-offs in ADRs, and when AI agents are in the loop treat them as fast but careless contributors who must be wrapped in tests, specs, persistent rules, and deterministic feedback gates.
