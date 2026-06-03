# debt-ops — GitHub Copilot adapter

Brings debt-ops' **write-time feedback loop** to GitHub Copilot CLI via Copilot's
hooks. This is the differentiator the [portable skills](../skills/) can't carry: a
skill is model-invoked, but Copilot's `postToolUse` hook fires on every edit, so
quality checks run deterministically — same posture as the Claude Code and Codex
adapters.

> **Status: prototype** (packaging plan Phase C). The hook scripts are validated
> standalone against Copilot's documented JSON contract, and the adapter is now
> packaged as an installable Copilot plugin (`plugin.json` + marketplace). The
> remaining validation step is confirming `${PLUGIN_ROOT}` expansion and marketplace
> discovery on a real `copilot plugin install`.

## What ports, and what doesn't

Copilot's hook contract differs from Claude Code's in three ways that shape this
adapter:

| Capability | Claude Code | Copilot | Here |
|---|---|---|---|
| Write-time quality checks | `PostToolUse` (matched) | `postToolUse` (no matcher) | ✅ ported — `feedback.py` self-filters to edit tools by `toolName`/`toolArgs` |
| Disciplines at session start | `SessionStart` inject | command hooks **can't inject** | ➡️ moved to the **charter** (`debt-ops-init`); the `sessionStart` command hook only warms path caches + logs a metric |
| `drop A` intercept + confirm | `UserPromptSubmit` block | `userPromptSubmitted` output **not processed** | ⚠️ degraded — use the `debt-ops-add` skill's manual drop (read `current-turn.txt`, `rm` the entry) |
| Stop-time safety net | `Stop` `decision:block` | `agentStop` (different contract) | ⏭️ deferred (follow-up) |

So on Copilot you get the **full write-time loop** plus capture/review/metrics via
the [portable skills](../skills/); the disciplines come from the charter instead of
a per-session inject.

## Install

Needs a git repo and Python 3.10+.

### Option A — plugin install (recommended)

This adapter is a packaged Copilot CLI plugin (`plugin.json` bundling the hooks and
the four `debt-ops-*` skills). Install it from the repo's marketplace:

```bash
copilot plugin marketplace add bcanfield/agentic-tech-debt
copilot plugin install debt-ops@agentic-tech-debt
```

The marketplace lives at `.github/plugin/marketplace.json` and points at `./copilot`.
We go through a marketplace rather than a bare `copilot plugin install owner/repo`
because the bare form can't discover a plugin in a subdirectory yet
([copilot-cli#2390](https://github.com/github/copilot-cli/issues/2390)); marketplace
installs flatten the source dir so `plugin.json` is found. The plugin's hooks resolve
their scripts via `${PLUGIN_ROOT}` ([ADR 0015](../docs/adr/0015-copilot-plugin-and-marketplace.md)).

Then run the charter step below (still required — it's what gives the loop commands).

### Option B — manual copy (no plugin)

1. **Hooks** — copy this adapter's hook files into your repo's `.github/hooks/`:

   ```bash
   mkdir -p .github/hooks
   cp copilot/hooks/debt-ops.json copilot/hooks/feedback.py copilot/hooks/session-start.py .github/hooks/
   ```

   Copilot discovers `.github/hooks/*.json`; the `.py` files sit alongside and are
   referenced by the config (run with the repo root as cwd). User-level install
   works too — drop the same files under `~/.copilot/hooks/` and adjust the paths
   in `debt-ops.json`. (`hooks/debt-ops.json` is the manual-copy config;
   `hooks/hooks.json` is the `${PLUGIN_ROOT}` variant Option A uses.)

2. **Skills** — install the [portable skills](../skills/) into Copilot
   (`.github/skills/` in the repo, or `~/.copilot/skills/` personal).

### Charter (both options)

Run `debt-ops-init` once. It writes the disciplines and a
`<!-- debt-ops:feedback v1 -->` quality-commands block into
`.github/copilot-instructions.md` (or `AGENTS.md`). `feedback.py` reads that block to
know what to run on each edit — **without it, the write-time loop has no commands to
run.**

## How it works

- **`sessionStart` → `session-start.py`** — probes + caches the repo's ADR and
  registry directories and logs one `session` metric. Silent; injects nothing
  (Copilot command hooks can't).
- **`postToolUse` → `feedback.py`** — fires after every tool. Idles unless the tool
  was a file edit (matched via `toolName`/`toolArgs`). On an edit: reads the
  charter's quality-commands block, runs each command in parallel under a 3 s
  budget, warns if the edit dropped the repo's test-file count, and returns the
  pass/fail summary to Copilot as `additionalContext`.

Cache and metrics live under `~/.cache/debt-ops/` (override with `DEBT_OPS_CACHE`) —
the same base the skills and other adapters use, so `debt-ops-review` and
`debt-ops-metrics` see this adapter's data.

## Note on script duplication

`feedback.py` and `session-start.py` reuse the Claude adapter's logic almost
verbatim, on purpose — the core functions are kept identical so the planned
vendored `_common.py` (ADR 0011 / packaging plan Phase E) can replace all copies in
one lift. Don't "clean up" the duplication here; it's tracked debt with a scheduled
payoff.
