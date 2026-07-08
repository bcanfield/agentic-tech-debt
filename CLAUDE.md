# Project Rules

- **Stay in scope.** Do exactly what was asked. No drive-by refactors or "while I'm here" cleanups. Flag them and wait for confirmation.
- **Don't over-engineer.** Simplest thing that works. No speculative abstractions, defensive code for impossible cases, or new dependencies without a concrete reason.
- **Use current docs.** For any library, framework, or API, fetch docs via the context7 MCP server before answering. Even for things you "know." Match the version in this project, not the latest release. Also - try to fetch examples from github frequently (e.g. an Anthropic-published Claude Code plugin, or an OpenAI Codex plugin, to use as an example).
- **Confront our research.** Try to see if you can ground decisions in our extensive research.
- **Ask when unsure.** One focused question beats guessing or expanding scope.
- **Be refreshingly concise.** Nobody likes overly wordy AI slop. Speak and comment like a co-worker.
- **Guide the agent with markdown, not orchestration.** Claude Code and Codex are smart and have the keys to the user's repo. Skills should load research-backed principles and trust the agent's judgment, not script its every step. Reach for Python only when determinism demands it (timestamps, audits, atomic file ops, hook contracts), never to make decisions a smart agent reading the repo can make better.
- **Python over Bash for plugin scripts.** Stdlib `json`, `re`, and `subprocess.run(..., timeout=...)` beat hand-rolled JSON escaping, a `jq` dependency, and the BSD/GNU `timeout` portability dance. And run on Windows without WSL.
- **Conventional commits.** All four adapters' plugin versions auto-bump in lockstep via release-please (config in `.github/`; mirrors `claude-code/.claude-plugin/plugin.json`, `codex/.codex-plugin/plugin.json`, `copilot/plugin.json`, and `cursor/.cursor-plugin/plugin.json`); use `feat:` / `fix:` / `feat!:` prefixes. Anything else is ignored by the bumper. Don't hand-edit `version` in any `plugin.json`.
- **We like humanlike, concise inline comments** For example, a single line above a function or code block very simply and concisely saying what the code is doing so that the code is easy for a human to understand
- **Record decisions as ADRs.** When we make a choice with two credible alternatives (a new convention, a tradeoff worth remembering), drop a short note in [`docs/adr/`](./docs/adr/) using the format in its [README](./docs/adr/README.md).

## Adapter parity — duplicated on purpose

debt-ops is one product shipped as several **self-contained** implementations
(`claude-code/`, `codex/`, `copilot/`, and the portable `skills/`). The helper
scripts and skills are **deliberately duplicated** across them — there is no shared
or vendored module, and we are not extracting one ([ADR 0014](./docs/adr/0014-keep-adapters-duplicated.md),
reversing the `_common.py` plan). Installed plugins are isolated dirs and the hooks
are stdlib-only, so self-containment beats DRY here. **We keep the copies in sync by
hand/AI, in the same change — not by abstraction.**

**The rule.** A shared-logic change isn't done until it lands in *every* copy in the
same PR. Treat the copies of a given script as one unit: diff against `claude-code/`
(the reference — it has all six scripts) and propagate, **preserving each adapter's
deltas below** (don't flatten them).

### What's duplicated (keep in sync)

- **Helper scripts** — every adapter co-locates each script with its invoker: hook
  scripts in `hooks/` (next to `hooks.json`), skill scripts in the skill's own
  `scripts/`. `claude-code` is the reference (it has all six). Copies:
  - `register.py` (add skill) → `claude-code/skills/add/scripts/`, `codex/skills/add/scripts/`, `copilot/skills/debt-ops-add/scripts/`, `cursor/skills/debt-ops-add/scripts/`, `skills/debt-ops-add/scripts/`
  - `review.py` (review skill) → `claude-code/skills/review/scripts/`, `codex/skills/review/scripts/`, `copilot/skills/debt-ops-review/scripts/`, `cursor/skills/debt-ops-review/scripts/`, `skills/debt-ops-review/scripts/`
  - `feedback.py`, `session-start.py` (hooks) → `claude-code/hooks/`, `codex/hooks/`, `copilot/hooks/`, `cursor/hooks/`
  - `stop.py` (hook) → `claude-code/hooks/`, `codex/hooks/`, `copilot/hooks/`, `cursor/hooks/` (copilot on `agentStop`, cursor on `stop`)
  - `drop.py` (hook) → `claude-code/hooks/`, `codex/hooks/`, `cursor/hooks/` (cursor on `beforeSubmitPrompt`; no copilot — `userPromptSubmitted` output isn't processed)
- **Within-script helpers** repeated across most of the above — change one, change
  all: `git_toplevel`, `repo_hash`, `cache_base`, `read_registry_dir`, `log_metric`,
  `letter_for`, `parse_frontmatter`, `days_since`.
- **Skills (`SKILL.md`)** — `add`, `review`, `metrics`, `init` each live in
  `claude-code/skills/`, `codex/skills/`, `copilot/skills/`, `cursor/skills/`, and
  top-level `skills/`. Dir names differ by namespace (see deltas): bare (`add`)
  under the namespaced plugins, `debt-ops-`-prefixed under copilot + cursor + portable.
- **Cross-cutting contracts** (must match everywhere they appear):
  - Registry schema (frontmatter fields + quadrant/category enums) — every
    `register.py`, `review.py`, and `add` skill. Canonical: `docs/tech-debt-plugin-plan.md`.
  - Disciplines wording — `session-start.py` (claude, codex, cursor) + every `init` skill.
  - Feedback marker `<!-- debt-ops:feedback v1 -->` — every `feedback.py`,
    `session-start.py`, and the `init` skills that write it.
  - Cache layout + `metrics.jsonl` event shapes — the scripts + the `metrics` skill.
  - Product copy across the eight manifests (keep in lockstep, but mind the
    per-schema shape):
    - **Plugin tagline** — `"Every shortcut your coding agent takes, saved to
      your repo as it happens. Fix them when you're ready."` is byte-identical
      in all four `plugin.json` (`claude-code/.claude-plugin/`,
      `codex/.codex-plugin/`, `copilot/`, `cursor/.cursor-plugin/`) **and** the
      `plugins[].description` of the `.claude-plugin/`, `.github/plugin/`, and
      `.cursor-plugin/` marketplaces. The codex `.agents/plugins/marketplace.json`
      has **no** per-plugin description (that schema uses `interface.displayName`).
    - **Marketplace blurb** — one template, `"debt-ops for <Tool>: write-time
      tech-debt capture, review, and metrics."`, carried as top-level `description`
      (`.claude-plugin/`) or `metadata.description` (`.github/plugin/` → Copilot,
      `.cursor-plugin/` → Cursor). The codex `.agents/plugins/` marketplace shows
      only `interface.displayName` (no blurb field).

### Per-adapter deltas (do NOT sync away)

These differ on purpose; preserve them when propagating a shared change:

- **Cache base.** `claude-code` uses `CLAUDE_PLUGIN_DATA`; `codex`/`copilot`/`cursor`/portable
  use `DEBT_OPS_CACHE` → `~/.cache/debt-ops`.
- **Script-reference style.** Layout is now uniform (hook scripts in `hooks/`, skill
  scripts in the skill's `scripts/`); only the *reference* differs. `claude-code`
  addresses scripts via the `${CLAUDE_PLUGIN_ROOT}/…` token (Claude provides it);
  `codex`/`copilot`/portable call the bundled script by relative path (`scripts/…`),
  since the open SKILL.md standard has no plugin-root token. `cursor` ships **two**
  hooks configs: `hooks/hooks.json` (plugin/marketplace mode, scripts via the
  `${CURSOR_PLUGIN_ROOT}/hooks/…` token — Cursor's analog of `${CLAUDE_PLUGIN_ROOT}`)
  and `hooks/hooks.local.json` (manual copy → `.cursor/hooks.json`, project-relative
  `.cursor/hooks/…` paths). They differ only in that prefix — keep in sync
  ([ADR 0021](./docs/adr/0021-cursor-marketplace-plugin.md), mirroring Copilot's
  dual config in ADR 0015).
- **Hook I/O envelope.** `claude-code`/`codex` emit
  `hookSpecificOutput.additionalContext`; `copilot` emits a bare object and
  self-filters edit tools (its `postToolUse` has no matcher). `copilot`'s
  `feedback.py` prefers `modifiedResult` over `additionalContext` to work around
  [copilot-cli#2980](https://github.com/github/copilot-cli/issues/2980); its
  `stop.py` runs on `agentStop` (camelCase `sessionId`) and skips the batch
  rotation (no `drop` hook to consume it). `cursor` emits Cursor's snake_case
  envelopes: `additional_context` (sessionStart + postToolUse — both injected, no
  copilot-style workaround), `followup_message` (stop), and `continue:false` +
  `user_message` (drop, on `beforeSubmitPrompt`). Its `postToolUse` has no matcher
  so `feedback.py` self-filters edits by `tool_name`/`tool_input`; its `stop.py`
  keys the per-session cap on `conversation_id` (no `session_id` in the payload)
  and keeps batch rotation (it *does* have a `drop` hook) ([ADR 0020](./docs/adr/0020-cursor-full-hook-adapter.md)).
- **Hook cwd.** Copilot runs plugin hooks with cwd = the *plugin install dir*, not
  the project, so `copilot`'s three hooks read the payload's `cwd` and `os.chdir`
  into it (via `chdir_to_payload_cwd`) before any git call. Claude/Codex run hooks
  in the project dir, so their copies do **not** have a chdir helper — do not
  propagate one ([ADR 0019](./docs/adr/0019-copilot-hooks-chdir-to-payload-cwd.md)).
  `cursor` has its own variant — `chdir_to_workspace`, keyed on the payload's
  `workspace_roots[0]` (present in *every* Cursor hook payload), in all four hooks —
  so one script set works whether the marketplace plugin runs hooks from the plugin
  dir or the project ([ADR 0021](./docs/adr/0021-cursor-marketplace-plugin.md)). It's
  a no-op in the project-local install. Distinct from Copilot's (payload `cwd`); do
  not cross-propagate.
- **Charter file + invocation.** `CLAUDE.md` + `/debt-ops:add` (claude) vs
  `AGENTS.md`/copilot-instructions + `$add` / bare skill name (codex, copilot, cursor, portable).
- **Frontmatter.** `claude-code` skills use `allowed-tools` /
  `disable-model-invocation`; portable skills are `name` + `description` only.
  `claude-code` skills also carry `metadata.internal: true` to hide them from the
  `npx skills` CLI (it reads the root `marketplace.json` → `./claude-code` and would
  otherwise offer broken `${CLAUDE_PLUGIN_ROOT}` copies alongside the portable set).
  Do **not** propagate that flag to codex/copilot/portable ([ADR 0018](./docs/adr/0018-hide-claude-code-skills-from-skills-cli.md)).
  `cursor` skills are `name` + `description` like portable, except `debt-ops-init`
  adds `disable-model-invocation: true` (Cursor supports the field natively, making
  init explicit-only — `/debt-ops-init`). Do not propagate that field to the portable set.

## Demo GIFs

- `demo/debt-ops.gif`: README hero, [VHS](https://github.com/charmbracelet/vhs). One `as any` catch in under 8s. Scene: [`demo/scene.bash`](./demo/scene.bash). Tape: [`demo/debt-ops.tape`](./demo/debt-ops.tape). Regenerate: `vhs demo/debt-ops.tape` (needs `vhs`, `ttyd`, `ffmpeg`, JetBrains Mono).
- `demo/concept/debt-ops-concept.gif`: README "Why it exists" lifecycle animation (catch → manage → pay down), [Motion Canvas](https://motioncanvas.io/). Source + regen steps in [`demo/concept/`](./demo/concept/).

## Debugging

Set `DEBT_OPS_DEBUG=1` before launching the agent to log every PostToolUse fire and command result:

```bash
DEBT_OPS_DEBUG=1 claude   # Claude Code
DEBT_OPS_DEBUG=1 codex    # Codex
```

Each fire appends tab-separated lines to `<cache>/debug.log`. The exact path is printed in the SessionStart context block. Format:

```
2026-05-06T16:00:34Z	FIRE	changed=src/foo.ts	cmds=3
2026-05-06T16:00:34Z	PASS	0.01s	tsc --noEmit
2026-05-06T16:00:37Z	TIMEOUT	3.00s	pytest tests/
2026-05-06T16:00:37Z	FAIL	0.42s	eslint $CHANGED_FILES
```

Tail it in a separate terminal pane (the exact path is printed in the SessionStart context block):

- **Claude Code:** `tail -f ~/.claude/plugins/data/debt-ops-agentic-tech-debt/cache/<repo-hash>/debug.log`
- **Codex:** `tail -f ~/.cache/debt-ops/cache/<repo-hash>/debug.log` (override the base with `DEBT_OPS_CACHE`; see ADR 0012)

With the env var unset (default), nothing is written.
