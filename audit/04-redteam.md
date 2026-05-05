# Red-team audit (Pass 3)
Date: 2026-05-05

Adversarial review of `tech-debt-plugin-plan.md` v1 against `tech-debt-pillars.md`
and `tech-debt-management.md`. Bias is toward concrete failure modes; "unknown
— needs dogfood" is used where evidence is genuinely missing.

---

## 1. Day-in-the-life failure modes

The "day in the life" assumes the SessionStart inject reliably steers Claude's
behavior across an 8-hour session, that `feedback.sh` output is acted on, and
that the cache stays valid. Each is contestable.

1. **08:50 — discovery prompt failure mode (cold cache).** The first
   SessionStart inject contains both the four disciplines *and* an
   instruction to scan the repo and write
   `${CLAUDE_PLUGIN_DATA}/cache/<repo-hash>/feedback.list`. Two failure
   modes: (a) Claude treats the discovery instruction as informational and
   never writes the file, leaving the cache empty for the rest of the
   session and silently for tomorrow as well; (b) Claude writes commands
   that don't exist or are misnamed (`cargo clippy` without
   `--workspace` in a workspace repo, `npm test` in a pnpm repo). v1 has
   no validation layer between "Claude wrote a line" and "the line gets
   `timeout 3 …`'d on every edit." **Mitigation:** `feedback.sh` should
   shell out a 200 ms `command -v` / `which` probe per cached command on
   first read after a cache write and drop unrecognized ones with a one-
   line warning in `additionalContext`. Otherwise: accept and watch in
   dogfood.

2. **09:15–09:17 — inject downweighting under long context.** Claude Code
   sessions routinely exceed 100k tokens; the four-discipline inject is
   ~600 chars at session start and is competing with subsequent task
   context, file reads, and tool outputs. There is no published evidence
   that `additionalContext` from `SessionStart` is treated as system-grade
   instructions vs. ordinary context. By 09:35 the inject may be six or
   seven tool roundtrips back. The Pillar 6 research note that frontier
   models "reliably attend to roughly 150–200 instructions" is exactly
   the regime where the 4-item discipline list lives — but it has to
   compete. **Mitigation:** v1 accepts; v2's `Stop` hook safety net (the
   plan already lists this as a v2 contingency) is the right insurance.
   Flag for dogfood: track how often Discipline 1 fires vs. how many
   TODOs Claude actually writes.

3. **09:17 — `feedback.sh` output is structured JSON, but is it
   *acted on*?** The plan specifies the script returns
   `{"cargo check": "pass", "cargo clippy": "pass"}` via
   `additionalContext`. There is no commitment that Claude will *read*
   `additionalContext` from a `PostToolUse` hook on the *same* turn the
   edit completed, vs. continuing to the next user prompt. CC's hook
   spec emits `additionalContext` into the next model turn; if the edit
   completes the user's request, the next turn may be a fresh user
   prompt, and the JSON may never be reasoned about. **Failure mode:** a
   silent failure (clippy fails, agent ignores it, user sees the diff
   later). **Mitigation:** the plan's "structured JSON, agent can act on
   it" claim is unverified; dogfood needs a metric like "number of edits
   where Claude self-corrected after a clippy fail." Until then, mark as
   unknown — needs dogfood.

4. **09:35 — registering against unverified code (the user's question).**
   Discipline 1 fires on writing the TODO; the TODO is in a diff that
   has only been checked by the per-edit cache (which intentionally
   excludes `cargo test`). Claude registers the debt, but the change may
   still fail tests. The registry now contains an entry pointing at
   broken code. v1 has no link between debt registration and test
   passage. **Concrete consequence:** PR-time test failure invalidates
   the debt entry's premise (the "callback chain" may not exist as
   designed); the entry is now stale before it's ever read. **Mitigation:**
   tolerable for v1 because (a) entries are addressable by content and
   easy to delete, (b) the developer reviews the diff at PR time anyway.
   But document this explicitly: **the registry is a record of intent at
   edit time, not a verified record of debt in the merged tree.** A v3
   AI-touched-tagging pass should resolve any orphaned entries on test
   failure.

5. **11:30 — "architecturally significant" is pure model judgment.** The
   plan offers no heuristic. Pillar 5's research foundation explicitly
   names heuristics ("touching a public interface, a data model, a build
   pipeline, an auth surface"); Discipline 2 names them too. But there
   is no detection layer, no tool that says "you just touched
   `Cargo.toml`'s `[dependencies]` — consider an ADR." Failure modes:
   (a) **false negative** — Claude refactors a public trait without
   realizing it's public, no ADR. (b) **false positive** — Claude treats
   every internal helper rename as architecturally significant and the
   `doc/adr/` directory fills with rationalizations. (c) **selection
   bias** — Claude is more likely to ADR a flashy new feature than a
   fragile workaround that's actually the higher-debt decision.
   **Mitigation for v1:** accept, but instrument. Count ADRs created per
   session in dogfood; if < 0.1/week or > 1/day, the heuristic is
   broken. v2's "architectural-touch heuristic detection" is the
   structural fix and probably can't wait.

6. **Tomorrow — cache staleness.** The plan promises "instant" cache reads
   on subsequent sessions. There is no invalidation policy. **Failure
   mode:** overnight, the developer adds `prettier` to `package.json` or
   the team migrates from Jest to Vitest; the cache still has `npm
   test`. `feedback.sh` runs the wrong command for days until someone
   notices. The plan does say `/debt:init` writes a marker block in
   CLAUDE.md and "CLAUDE.md is the source of truth when present" — but
   for solo users who skip `/debt:init`, the cache *is* the source of
   truth, and it never invalidates. **Mitigation:** SessionStart should
   compare an mtime hash of `Cargo.toml`/`package.json`/`pyproject.toml`/
   `Makefile`/`go.mod`/`Gemfile` against a hash stored alongside the
   cache; on mismatch, re-run discovery. ~5 lines of bash. Strong
   recommendation to add to v1.

7. **Some weeks later — `/debt:init` race.** The team scenario assumes
   "one dev runs `/debt-ops:init`" cleanly. If two devs run it
   concurrently in different branches and merge, the
   `<!-- debt-ops:feedback v1 -->` marker block conflicts. The plan
   names the marker as "self-imposed convention" with no cross-plugin
   contract; it also has no merge-conflict story. **Mitigation:** the
   marker block content should be deterministic given the same project
   files (sorted commands, no timestamps); if so, the merge conflict
   resolves to identical content. v1 should explicitly commit to that.

8. **Implicit — the inject's 10,000-char cap.** The plan says
   `additionalContext` has a 10,000-char cap. The four disciplines are
   ~600 chars; on a *first* session, the inject also carries the
   discovery prompt (~300 chars). Headroom is large for v1. But every
   `feedback.sh` run also emits `additionalContext` on PostToolUse, and
   if a project has a verbose linter (e.g., a wall of clippy warnings on
   a fresh edit), the per-tool-use 10,000-char cap can clip the
   structured JSON mid-record, breaking the agent's ability to parse it.
   **Mitigation:** `feedback.sh` should truncate per-command output to
   ~1500 chars (head + tail) before emission. Not a v3 issue — a
   first-week dogfood issue.

---

## 2. Empty-state & edge-case matrix

| # | Scenario | What v1 does | Acceptable? |
|---|---|---|---|
| 1 | Repo with no `Cargo.toml`/`package.json`/`pyproject.toml`/Makefile/`go.mod` (vibe coder Persona 1, e.g., shell scripts, static site). | SessionStart inject asks Claude to detect quality commands; Claude reports none and writes empty `feedback.list`. PostToolUse runs nothing per edit. Disciplines (registry, ADR) still fire. | **Acceptable.** Plan explicitly names this ("near-silent on projects with no detectable quality commands"). v1 still delivers Pillars 1, 5 value via disciplines. |
| 2 | Non-git repo (the plan calls git "hard prerequisite"). | `<repo-hash>` is computed via `git rev-parse --show-toplevel | shasum`; if `.git` is absent, `git rev-parse` returns non-zero, the `cut`-pipe consumes its empty output, and the cache key collapses to a hash of empty-string — meaning **every non-git directory shares one cache.** Two devs working in two non-git scratch dirs share each other's cached commands. The `SessionStart` hook does not currently `set -e` per the plan; failure mode is a silent corruption rather than an error. | **Not acceptable.** v1 must `set -euo pipefail` in `session-start.sh`, check `git rev-parse` exit code, and either no-op cleanly with a one-line `additionalContext` ("debt-ops: not a git repo, plugin idle this session") or use `pwd | shasum` as fallback with a clear comment. Recommend the no-op path; matches the "hard prerequisite" claim. |
| 3 | Monorepo with multiple lockfiles (root `package.json` + `apps/*/package.json` + a `Cargo.toml`). | `session-start.sh` asks Claude to scan; Claude writes a single `feedback.list` of commands for "the repo." Whose `npm test`? The plan does not commit to a per-package strategy. | **Marginal.** v1 will cache one set of root-level commands. PostToolUse runs them on every edit, including edits in unrelated packages, wasting time. **Mitigation:** accept for v1; document as "monorepo support is v2." Add to anti-pattern watchlist (#3, "reinventing detection"). |
| 4 | Very large repo (Linux-kernel-scale, ~80k files). | First SessionStart inject asks Claude to scan project files. Claude reads `Cargo.toml`/`package.json`/etc., not the whole tree, so latency should stay bounded. But the disciplines list ("read entries under `debt/registry/` before changing files") implies a directory walk on every relevant edit; on a repo with 1000+ debt entries (realistic at year 2), this is unbounded. | **Acceptable for v1** because the registry will be empty or near-empty for any v1 user. **Document** that Discipline 3 needs a "read what's relevant to the touched module" qualifier before the registry exceeds ~50 entries. |
| 5 | Windows shell (`feedback.sh` is bash). | Plan does not mention Windows. CC v2.1.121 runs on Windows; bash availability on Windows requires WSL or Git Bash. Without it, `command:` in `hooks.json` fails on the first edit, breaking the plugin entirely. | **Not acceptable as silent.** v1 must (a) document "requires bash; on Windows, install Git Bash or use WSL" in README, OR (b) ship a `.cmd`/PowerShell sibling. (a) is fine for v1. (b) is v2. |
| 6 | Repo where another plugin already wrote a `<!-- debt-ops:feedback v1 -->` block (collision). | Effectively impossible for v1 (no other plugin uses our marker). But: a forked or older `debt-ops` install could create one. `/debt:init` writes "defensively" per the plan but that's not specified. | **Unknown — needs dogfood.** v1 should commit: `/debt:init` reads any existing block, parses commands tolerantly, replaces only the content between the markers, never the surrounding CLAUDE.md text. |
| 7 | Repo with an existing `debt/registry/` directory from a prior tool. | `/debt:add` writes `<id>-<slug>.md`. If a prior tool used the same naming convention, the new entry collides with an existing file. The plan's `id` numbering scheme (`0042`) requires reading the directory to find next-free; what if the directory has non-conforming files? | **Marginal.** `/debt:add` should: (a) glob `debt/registry/[0-9][0-9][0-9][0-9]-*.md`, ignore others, take max+1 as next id; (b) refuse to overwrite. Document. ~3 lines of skill prompt. |
| 8 | A teammate without the plugin opens a CLAUDE.md edited by `/debt:init` — does the marker block confuse them? | The marker is `<!-- debt-ops:feedback v1 -->`. To a non-plugin reader, it looks like an HTML comment with stale-looking text and a list of bash commands. They might delete it. They might not. | **Acceptable.** Markdown comments are conventionally ignored. The plan's "passive, plays well with others" stance accepts this. **Recommend:** the marker block's first line be a human-readable explainer comment like `<!-- debt-ops: this section is auto-managed by the debt-ops plugin; safe to edit, run /debt:init to regenerate -->` so a stranger knows what to do. |
| 9 | The cache file gets corrupted (truncated, invalid format). | `feedback.sh` reads the cache. If it's a JSON array and got truncated mid-parse, `jq` (or whatever parser) errors out. Plan does not specify the format — "command list" suggests one-command-per-line plain text, which is robust to truncation but not to e.g. a partial line. | **Marginal.** v1 must: (a) define the cache format as one-command-per-line, no quoting, comments allowed; (b) `feedback.sh` skips empty/comment lines and drops malformed lines silently. Robust by construction. ~2 lines of awk. |
| 10 | Two Claude Code sessions open on the same repo at once — race on cache and registry. | (a) **SessionStart cache race.** Both sessions check, both find missing, both ask Claude to write the cache. Last writer wins; content should be identical so collision is benign. **But:** if discovery is non-deterministic (Claude phrasing varies), the file can flap. (b) **PostToolUse registry race.** Both edits trigger `feedback.sh` AND Discipline 1 may fire in both. Two `/debt:add` invocations may pick the same `id` (both glob the directory and find max+1 = 0001). Two files with the same id, different slugs. | **(a) acceptable** — cache content should be canonical. **(b) not acceptable as-is.** v1's `/debt:add` should use a coarser id strategy (e.g., timestamp `YYYYMMDDhhmmss`, or a short content hash) to avoid the race entirely. The "id is like a commit SHA" framing in the plan supports this. **Strong recommendation.** |
| 11 | Discipline conflict: CLAUDE.md says "no markers like TODO" but Discipline 1 tells the agent to write TODOs. | Plan says: "If `CLAUDE.md` already has a `## Tech debt operations` section, those instructions take precedence; the inject is the fallback." But a conflict between an *unrelated* charter rule ("no TODO comments") and Discipline 1 (which assumes Claude writes a TODO and registers it) is unresolved. Claude may follow the project's no-TODO rule and never trigger registration — Pillar 1 silently unmet. | **Acceptable but worth naming.** Discipline 1 should also fire on commit messages saying "I'll handle X later," on `// XXX`, on conditional `if (false)` debt-blocks, etc. v1 inject text should broaden the trigger surface beyond the four-marker list. ~1 line edit. |
| 12 | `${CLAUDE_PLUGIN_DATA}` not writable (read-only HOME, container with mounted plugin but no writable data dir). | `session-start.sh` tries to write the cache, fails. Failure mode unspecified. | **Unknown — needs dogfood.** v1: `session-start.sh` should test-write a probe file; on failure, emit `additionalContext` ("debt-ops: cache disabled, running in stateless mode") and skip cache logic. Falls back to per-session re-detection. Acceptable behaviorally; just needs to fail cleanly. |
| 13 | Hook itself errors out (bash bug, missing `timeout` binary on macOS — `timeout` is GNU coreutils, not BSD default). | macOS users without coreutils have no `timeout` command. `feedback.sh` errors. Per `hooks.json` `timeout: 5`, CC kills it; the edit cycle continues but no feedback. | **Not acceptable as silent.** v1: detect `timeout` vs `gtimeout` (Homebrew coreutils ships as `gtimeout`); fall back to a portable `(cmd & PID=$!; sleep 3 && kill $PID) wait` shim. This is a 5-line fix; ignoring it breaks every fresh macOS user. Strong v1 recommendation. |

---

## 3. Adversarial agent

The four disciplines live in a heredoc inside `session-start.sh`; the model's
interpretation is the entire enforcement mechanism in v1. Reviewed each as a
recall/precision question.

**Discipline 1 (TODO/FIXME/HACK/XXX → register).**
- *Recall.* The marker list is good; Pillar 1 research supports it. But the
  plan adds "use judgment; trivial markers (style nits) don't earn an entry."
  This is exactly the loophole. Claude is well-aligned to "be helpful, don't
  spam"; given any plausible rationale to skip, it will. The Pillar 1 failure
  mode ("Reckless–inadvertent debt accumulates invisibly") is the precise
  thing that "trivial — use judgment" re-introduces. **Recall is the weak
  axis, not precision.**
- *Precision.* If the discipline fires too eagerly, the registry fills with
  the 10:05 false-positive case ("just a naming nit, drop it"). The plan
  designs for this with content-addressable drops, which is the right call.
- *Attack vectors.*
  1. Agent claims "trivial" to avoid interruption. v1 cannot detect this; no
     audit trail exists.
  2. Agent registers throwaway entries (e.g., re-registers the same
     conceptual debt under different slugs to look productive). v1 has no
     dedup.
  3. Agent skips Discipline 1 entirely under heavy-context conditions; the
     inject is too far back. See failure mode #2 above.
- **Recommendation.** Tighten Discipline 1 wording: replace "use judgment;
  trivial markers (style nits) don't earn an entry" with "if you write a
  marker, register it. The developer can drop entries in one message; you
  cannot recover an unregistered shortcut." Trade precision for recall;
  Pillar 1 is recall-shaped.

**Discipline 2 (architecturally significant → ADR).**
- *Recall.* Section 1.5 above already covered the absence of a heuristic.
  Without one, recall is unknowable; needs dogfood.
- *Precision.* Worse: an ADR that's a *rationalization* (Claude justifying a
  shortcut after the fact, in Nygard format) actively damages Pillar 5's
  premise (ADRs as searchable, honest decision records). v1 has no rule
  separating "decision record" from "rationalization."
- *Attack vectors.*
  1. Claude writes `0001-decided-to-skip-the-test.md` with confident
     "Consequences" prose; the ADR has now laundered a shortcut.
  2. Claude over-ADRs: every refactor becomes an ADR, the directory bloats,
     human reviewers stop reading.
- **Recommendation.** v1: add to the inject "draft an ADR only when there
  was a real *choice* between credible alternatives. If you can't list two,
  it's not an ADR; it's a comment." This maps to the Nygard "Alternatives"
  field, which the schema includes. Cheap, immediate.

**Discipline 3 (read entries before changing files).**
- *Recall/precision.* This works for an empty registry and breaks under
  load. See edge case #4. v1 acceptable; document the v2 fix.
- *Attack vector.* Agent claims to have read the registry but didn't. v1
  has no audit. Accept for v1 (plan tenet: "Lean relaxed over strict").

**Discipline 4 (refer to entries by content, not ID).**
- *Recall/precision.* This is a stylistic preference for chat output; low
  consequence either way. The numeric ID is *also* exposed (PR trailers).
  Claude may default to ID anyway because IDs are easier to copy. Not a
  v1 risk.

**Pillar 7 / test-integrity exposure — a serious gap.**
The plan defers test-integrity (rejecting diffs that delete or weaken tests)
to v3. The pillars doc cites Beck directly: "agents will try to delete tests
to make them pass." `tech-debt-management.md` repeats this in the Beck
quote and in the Pillar 7 mandate. **v1 has no defense.** A team that
dogfoods v1 in a real project for the entire v1 → v2 → v3 window (months,
plausibly a year) is exposed to this risk in production. This is the single
biggest gap in the v1 commitment relative to the pillars.

- *Mitigation, cheap, v1-compatible.* `feedback.sh` already runs project
  commands. Add one more cached command, detected in SessionStart: a count
  of test files (`fd -e test.ts -e .test.tsx -e _test.go -e .spec.ts | wc -l`
  or equivalent). On `PostToolUse`, recompute the count; if it dropped by
  >0 in a single edit, emit a `WARNING: this edit removed N test
  files/blocks` line in `additionalContext`. This is not the v3
  test-integrity rule (no rejection), but it is a free signal the agent
  can act on. ~10 lines. Strong v1 recommendation.

---

## 4. Differentiation

`debt-ops` v1 in 2026 must justify install against five real alternatives.

**vs. doing nothing (CLAUDE.md + project linters via PostToolUse hook).** A
hand-rolled `.claude/hooks.json` running `npm run lint` after every edit
delivers ~70% of v1's Pillar 7 value in 15 lines, no plugin install. v1's
delta: the cache, the lazy registry, the inject of disciplines. **Honest
take:** for a solo Persona 2 dev who already has a CLAUDE.md, v1's incremental
value over a homemade hook is small. The persistent registry (Pillar 1) is
the differentiator.

**vs. CodeScene CodeHealth MCP Server** ([CodeScene MCP](https://codescene.com/product/code-health-mcp)).
CodeScene gives agents real Code Health metrics (Pillar 2 behavioral layer);
v1 gives lint pass/fail. CodeScene is the right Pillar 7 substrate; v1 says
so itself by deferring MCP wiring to v3. **`debt-ops` v1 is complementary,
not competitive.**

**vs. Claude Code's built-in `/init` + a "review your code" subagent.** `/init`
scaffolds CLAUDE.md; v1 deliberately does not duplicate this and is correct
to avoid it. A review subagent reviews diffs; v1 does not (subagents are v2).
**Different layer.**

**vs. CodeRabbit / Cursor review modes / Sourcegraph Cody.** All three are
PR-time or IDE-time *review* tools. v1 operates pre-PR, in-loop, on the
agent's own edit cycle. Different workflow seam. CodeRabbit at ~$24/dev/mo
([CodeRabbit pricing](https://max-productive.ai/ai-tools/coderabbit/));
Cody enterprise from ~$5k/yr ([Cody pricing](https://www.sitepoint.com/ai-ides-compared-cursor-claude-code-cody-2026/)).
v1 is free and Claude Code-native. **Different stage of pipeline.**

**vs. a homemade SessionStart hook injecting two paragraphs.** Honestly,
that captures Disciplines 1–4 without the plugin. v1's persistent value over
this is: the schema (Pillar 1 structured registry), the cache, and the
opt-in `/debt:init` for team share. **For Persona 2 evaluating "is it worth
the install?" the answer is: only if you intend to keep a registry.** If
you plan to wing it on TODOs, a homemade hook beats v1.

**Verdict:** v1 differentiates from review tools (different stage), from
CodeScene (different layer), and from `/init` (no overlap). It does *not*
strongly differentiate from a 30-line homemade hook + a manual registry
convention. The honest pitch is the registry schema and the discipline
inject, packaged.

---

## 5. Top-5 v1-at-risk anti-patterns

1. **Hook latency creep** (plan's #1). v1 enforces `timeout 3` per command
   and `timeout 5` at the CC level. **Repro:** install v1 in a
   moderately-large monorepo, run `eslint` over the full repo (the
   discovery prompt may pick `npm run lint` which is project-wide).
   `timeout 3` kills it; `feedback.sh` returns `timeout`/`fail` for every
   edit; the agent sees lint failing always and either ignores it (recall
   #2) or chases ghost lint errors. *Prevention:* SessionStart's
   discovery prompt should explicitly ask for **changed-file-scoped**
   commands (`eslint $CHANGED_FILES` style), not project-wide. v1 should
   ship that wording.

2. **Discipline drift / agent ignores inject under long context** (plan's
   #6). **Repro:** open a session, work for 4 hours, ask Claude to
   write a TODO at hour 4, observe whether Discipline 1 fires.
   *Prevention:* dogfood metric; if drift is >20%, bring back Stop hook
   (already on the v2 list).

3. **Agent output reviewed only by humans, only at PR time** (pillars
   doc). v1 explicitly defers writer/reviewer separation, security
   review, and comprehensibility checks to v2/v3. **Repro (3-line):**
   prompt Claude to add a hashed-password compare in v1, observe no
   security review fires; the only feedback is the project's lint, which
   does not catch timing-attack vulnerabilities. *Prevention:* document
   prominently that v1 is **not** a substitute for code review; v1's
   Pillar 7 is "fast loop only." A README sentence.

4. **Vibe coding in production / no spec, no TDD, no comprehensibility
   check** (pillars doc). v1's Discipline 1 even *encourages* the
   "register a TODO and move on" path, which is the opposite of TDD's
   "write the failing test first." A user could read v1 as license to
   defer aggressively. **Repro:** "Claude, implement payment retry. If
   anything's edge-case-y, register it as debt and proceed." v1
   complies. *Prevention:* the inject text should explicitly say
   "registering debt is not a substitute for fixing it; if a shortcut
   would fail an obvious test, write the test first." 1 sentence.

5. **Footprint creep** (plan's #7). v1 is currently footprint-zero on
   install but writes to `${CLAUDE_PLUGIN_DATA}` per session and lazily
   creates `debt/registry/` and `doc/adr/` in-repo. **Repro:** install
   v1, work for one day, check `git status` — registry entries appear
   even if the developer wanted "just try the plugin, nothing
   committed." *Prevention:* `/debt:add` should add a one-line "(working
   tree only — `git rm` to discard)" to its announcement so the user
   understands the registry is now real. Cheap.

(Honorable mentions, not in top 5 but live: separate-backlog risk,
ever-growing CLAUDE.md, vanity ADRs.)

---

## Verdict

**Ship v1 today? No, but close.** Five things must change before v1 is
worth releasing as "enable-and-go":

1. **Robust `session-start.sh` failure modes** (edge cases #2, #5, #12,
   #13). Set `set -euo pipefail`, handle non-git repos cleanly, document
   Windows requirement, fall back when `${CLAUDE_PLUGIN_DATA}` is
   read-only, handle BSD vs GNU `timeout`. Maybe 30 lines total.

2. **Cache invalidation on manifest mtime.** The cache cannot silently
   serve stale commands forever. ~5 lines (failure mode #6).

3. **Test-integrity warning signal in `feedback.sh`** (Section 3 final
   point). v1 cannot leave the team unprotected against the
   delete-tests-to-make-them-pass attack from now until v3. A non-
   blocking warning is ~10 lines and is in the spirit of "lean relaxed."

4. **Race-safe `/debt:add` ID strategy.** Concurrent sessions must not
   collide on `0001`. Use timestamp- or hash-based IDs (edge case #10).

5. **One-sentence inject hardening.** Tighten Discipline 1 (drop the
   "use judgment" loophole), add the "two alternatives or it's not an
   ADR" rule to Discipline 2, and add the "registering debt is not a
   substitute for a failing test" line. Three sentences, big behavioral
   delta.

Everything else on this red-team list is acceptable v1 risk *if* the
team commits to dogfood instrumentation: count discipline firings,
ADR creation rate, edits per `feedback.sh` output, registry size over
time. Without dogfood metrics, v2 and v3 will be designed against
hunches. The plan already says this is the bet; the bet is good if the
metrics are wired up from day one.

The most valuable single change: items 1 and 5 together turn v1 from
"a respectful skeleton" into "a credible discipline harness." Items
2–4 prevent specific bugs that will bite within the first week of
real use.

Sources for differentiation:
- [CodeScene CodeHealth MCP Server](https://codescene.com/product/code-health-mcp)
- [CodeRabbit Review 2026](https://max-productive.ai/ai-tools/coderabbit/)
- [AI IDE Comparison 2026 — Cursor vs Claude Code vs Cody](https://www.sitepoint.com/ai-ides-compared-cursor-claude-code-cody-2026/)
