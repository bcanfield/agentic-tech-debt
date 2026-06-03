# 0018 — Hide the claude-code skill copies from the `npx skills` CLI

**Date:** 2026-06-02
**Status:** Accepted

## Context

Running `npx skills add bcanfield/agentic-tech-debt` (Vercel's skills CLI, the
skills.sh installer) offered **eight** skills: the four portable `debt-ops-*`
skills *and* a bare `add`/`init`/`metrics`/`review` set — the same four commands
twice.

Reading the CLI source ([`vercel-labs/skills`](https://github.com/vercel-labs/skills),
`src/skills.ts` + `src/plugin-manifest.ts`): after scanning the portable `skills/`
dir it also calls `getPluginSkillPaths`, which reads the **root
`.claude-plugin/marketplace.json`**, follows its one plugin's `source: "./claude-code"`,
and surfaces `claude-code/skills/`. (It only reads `.claude-plugin/*` — codex/copilot
manifests are never read, and the recursive fallback is skipped once skills are found,
so only the claude-code copies leak.)

This isn't cosmetic: the claude-code copies address their scripts via
`${CLAUDE_PLUGIN_ROOT}`, a token only Claude Code provides. Installed via `npx skills`
into Cursor/Gemini/etc. they'd be **broken**. Only the portable copies (relative
`scripts/` paths) work cross-agent.

## Decision

Add `metadata.internal: true` to the four `claude-code/skills/*/SKILL.md` files. The
skills CLI's `parseSkillMd` skips internal skills in the discovery/picker flow, so
`npx skills add <repo>` now offers exactly the four portable skills. An explicit
`npx skills add <repo> --skill add` still resolves (the CLI passes `includeInternal`
for by-name requests) — opt-in, never accidental.

`metadata` is a recognized passthrough field in the Agent Skills standard and in
Claude Code; only `disable-model-invocation: true` hides a skill *from Claude Code
itself*, so this flag is inert there. `claude plugin validate` passes. This is a new
per-adapter frontmatter delta (claude-code only) — recorded in CLAUDE.md.

## What this means for you

- `npx skills add bcanfield/agentic-tech-debt` shows one clean set of four skills; no
  duplicate installs on anyone's machine.
- Claude Code plugin install (`/plugin install debt-ops@…`) is unchanged.
- New rule when syncing skills: don't propagate `metadata.internal` to the codex,
  copilot, or portable copies — it belongs only on claude-code.

## Alternatives we ruled out

- **Switch the marketplace plugin `source` to a remote/github object form** so the CLI
  skips it (it ignores non-string sources). Rejected: it degrades the *primary* Claude
  Code install path (relative `./claude-code` is the documented clean self-contained
  layout) to fix the secondary npx path.
- **Mark all twelve non-portable copies internal** (codex + copilot too). Rejected:
  only claude-code is ever discovered by the CLI; flagging the others is dead config.
- **Leave it and document "pick the `debt-ops-*` set."** Rejected: the picker still
  lets users install broken `${CLAUDE_PLUGIN_ROOT}` copies — the user called duplicate
  installs "not ok."

## Payoff trigger

Revisit if the skills CLI adds a real ignore mechanism (`.skillsignore`/config), starts
reading codex/copilot manifests, or changes how `metadata.internal` behaves — any would
let us drop or relocate the flag.
