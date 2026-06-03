# 0015 — Package the Copilot adapter as an installable plugin + Copilot marketplace

**Date:** 2026-06-02
**Status:** Accepted

## Context

The `copilot/` adapter shipped as loose files: a `hooks/` dir the user hand-copies
into `.github/hooks/` plus the portable `skills/` installed separately. To test the
write-time loop *live* inside Copilot CLI — and to give users a one-command install —
it needs to be a real Copilot CLI plugin (`plugin.json` manifest) reachable through a
plugin marketplace.

Copilot CLI's plugin format overlaps Claude Code's but differs in three ways that
shaped this:

- The plugin-root token in hook commands is `${PLUGIN_ROOT}`, **not** Claude's
  `${CLAUDE_PLUGIN_ROOT}` (invalid in Copilot-format plugins).
- A bare `copilot plugin install owner/repo` is **broken for subdirectory plugins** —
  it caches the repo and looks for `plugin.json` at the repo *root*
  ([copilot-cli#2390](https://github.com/github/copilot-cli/issues/2390)). Marketplace
  installs use a flattened source dir with `plugin.json` at its root, so they work.
- Copilot reads `marketplace.json` from `.github/plugin/` (native) **and**
  `.claude-plugin/` (fallback); precedence when both exist is undocumented. Claude
  Code reads only `.claude-plugin/`.

## Decision

Package `copilot/` as a self-contained Copilot plugin and register it in a
Copilot-native marketplace:

- `copilot/plugin.json` — manifest declaring `skills: "./skills/"` and
  `hooks: "./hooks/hooks.json"`, seeded with `version: "0.7.2"` and wired into
  release-please (see below). Lives at the plugin-dir root, not a `.copilot-plugin/`
  subdir — Copilot has no such convention, and root `plugin.json` is GitHub's
  documented discovery default (unlike Claude/Codex, which *require* `.X-plugin/`).
- `copilot/hooks/hooks.json` — plugin-mode hooks config invoking
  `${PLUGIN_ROOT}/hooks/{session-start,feedback}.py` (filename matches the sibling
  adapters' `hooks/hooks.json`). The separate `hooks/debt-ops.json` (relative
  `.github/hooks/…` paths) is kept for the manual-copy install path documented in
  the adapter README.
- `.github/release-please-config.json` — `copilot/plugin.json` added to `extra-files`
  so its `version` lockstep-bumps with `claude-code` and `codex`.
- `copilot/skills/` — the four portable `debt-ops-*` skills bundled in, consistent
  with the self-contained-adapter rule ([ADR 0014](./0014-keep-adapters-duplicated.md)).
- `.github/plugin/marketplace.json` — Copilot marketplace listing `debt-ops` with
  `source: "./copilot"`. Distinct from `.claude-plugin/marketplace.json`
  (→ `./claude-code`), so each tool's native marketplace dir points at that tool's
  adapter.

Install/test route: `copilot plugin marketplace add bcanfield/agentic-tech-debt`
then `copilot plugin install debt-ops@agentic-tech-debt`.

## Consequences

- Live, one-command install inside Copilot CLI; the write-time loop is testable
  end-to-end for the first time.
- Two hooks-config files in `copilot/hooks/` (`hooks.json` plugin-mode vs
  `debt-ops.json` manual-mode). They differ only in the script path prefix
  (`${PLUGIN_ROOT}` vs `.github/hooks/`) and must stay in sync on any hook-wiring
  change — added surface area, called out here so it isn't a silent drift trap.
- The `.github/plugin/` vs `.claude-plugin/` precedence is unverified; the live
  install is what confirms `${PLUGIN_ROOT}` expansion and marketplace discovery.

## Alternatives we ruled out

- **Single shared `marketplace.json` in `.claude-plugin/` listing both adapters.**
  Can't — a marketplace can't have two plugins named `debt-ops`, and renaming would
  break the charter/skill identity. Tool-native marketplace dirs keep each pointing
  at the right adapter without a name clash.
- **Reuse `claude-code/` as the Copilot plugin.** Its hooks are Claude-format and
  wouldn't fire under Copilot's contract — the write-time loop (the adapter's whole
  reason to exist) would silently no-op.
- **Bare `copilot plugin install owner/repo:copilot` only, no marketplace.** Hits
  the subdirectory-discovery bug (#2390); marketplace install is the reliable route.

## Payoff trigger

Revisit when Copilot CLI fixes #2390 (bare subdir installs become reliable — the
marketplace indirection may no longer be needed), or if the two hooks-config files
drift, at which point collapsing to a single install mode is worth it.
