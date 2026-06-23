# 0021 — Package the Cursor adapter as a marketplace plugin

**Date:** 2026-06-18
**Status:** Accepted (supersedes the "no marketplace" call in [ADR 0020](./0020-cursor-full-hook-adapter.md))

## Context

[ADR 0020](./0020-cursor-full-hook-adapter.md) shipped `cursor/` as a full hook
adapter but concluded we'd distribute it by **manual file copy** because "Cursor
has no documented plugin/marketplace install for bundled skills+hooks yet (only a
nascent `workspaceOpen` → `pluginPaths`)." That conclusion was already out of date
when written.

Cursor shipped a real **plugin marketplace** (Cursor 2.5, Feb 2026; expanded
through May 2026 with team-distribution controls). Plugins bundle exactly our two
primitives — **hooks and skills** — into one reviewed, one-click install
(`/add-plugin`, or browse `cursor.com/marketplace`). The format is documented and
the spec repo is public ([`cursor/plugins`](https://github.com/cursor/plugins)):

- A plugin is a dir with `.cursor-plugin/plugin.json` (manifest; only `name` is
  required, components auto-discovered or pathed). Multi-plugin repos add a
  `.cursor-plugin/marketplace.json` listing each plugin by `source` subdir.
- **Hooks are a first-class bundled component.** The manifest's `hooks` field
  points at `./hooks/hooks.json`, and hook commands can reference the bundled
  script via the **`${CURSOR_PLUGIN_ROOT}`** token — the direct analog of
  `${CLAUDE_PLUGIN_ROOT}`. Confirmed against the official `continual-learning`
  plugin (`bun run ${CURSOR_PLUGIN_ROOT}/hooks/...`).
- Skills are referenced via the `skills` field (path to the skills dir).
- "All plugins must be open source" — we're MIT.

So the exact "when to revisit" trigger ADR 0020 named ("If Cursor ships a real
plugin/marketplace install, add a packaged path") is already met. Our adapter sat
at the *manual-copy* tier, which on every other adapter is the fallback, not the
primary — the gap between "works on Cursor" and first-class.

This also exposed a latent bug: plugin hooks may run with cwd = the plugin install
dir, not the project (the Copilot failure [ADR 0019](./0019-copilot-hooks-chdir-to-payload-cwd.md)
fixed). The committed Cursor hooks assumed project-root cwd and would silently
no-op in a marketplace install.

## Decision

Package `cursor/` as a Cursor marketplace plugin, mirroring the Copilot work in
[ADR 0015](./0015-copilot-plugin-and-marketplace.md):

- **`cursor/.cursor-plugin/plugin.json`** — manifest declaring `skills: "./skills/"`
  and `hooks: "./hooks/hooks.json"`, `version` wired into release-please lockstep
  (added to `.github/release-please-config.json` `extra-files`, like the other three).
- **`cursor/hooks/hooks.json`** is now the **plugin-mode** config: commands use
  `python3 ${CURSOR_PLUGIN_ROOT}/hooks/<script>.py`. This matches the official
  `./hooks/hooks.json` auto-discovery convention, so the manifest loads it
  correctly.
- **`cursor/hooks/hooks.local.json`** — the **manual-copy** config (project-relative
  `.cursor/hooks/<script>.py` paths), copied to `.cursor/hooks.json`. Same dual-config
  shape (and sync trap) as Copilot's `hooks.json` + `debt-ops.json`.
- **`.cursor-plugin/marketplace.json`** (repo root) — Cursor-native marketplace
  manifest listing `debt-ops` with `source: "cursor"`. Peer to
  `.claude-plugin/marketplace.json` (→ `./claude-code`), `.github/plugin/marketplace.json`
  (→ `./copilot`), and `.agents/plugins/marketplace.json` (→ `./codex`).
- **`chdir_to_workspace(data)`** added to all four Cursor hooks: re-anchor cwd to
  the payload's `workspace_roots[0]` before any git call. No-op for the project-local
  install (cwd is already the project root); corrects cwd under a plugin-dir install.
  One script set serves both modes — cleaner than Copilot's payload-`cwd` split
  because Cursor puts `workspace_roots` in *every* hook payload.

Install/test route: `/add-plugin` from a marketplace, or local-test by symlinking
`cursor/` into `~/.cursor/plugins/local/`.

## Consequences

- A first-class, one-click Cursor install — the marketplace tier, not manual copy.
  Unlocks the visibility play (official marketplace submission, cursor.directory,
  the `awesome-cursor-*` lists).
- Two hooks-config files in `cursor/hooks/` (`hooks.json` plugin-mode vs
  `hooks.local.json` manual-mode). They differ only in the script-path prefix
  (`${CURSOR_PLUGIN_ROOT}/hooks/` vs `.cursor/hooks/`) and must stay in sync on any
  hook-wiring change — same drift trap ADR 0015 called out for Copilot.
- New per-adapter delta: Cursor hooks carry `chdir_to_workspace` (keyed on
  `workspace_roots`), distinct from Copilot's `chdir_to_payload_cwd` (keyed on
  payload `cwd`) and absent from Claude/Codex. Recorded in CLAUDE.md.
- **Unverified on a live Cursor 2.5 install:** the `${CURSOR_PLUGIN_ROOT}` expansion,
  the plugin-hook cwd (hence whether `chdir_to_workspace` actually fires non-trivially),
  and `marketplace.json`/`plugin.json` discovery. The live install is what confirms
  these — same posture as ADR 0015's Copilot caveats.

## Alternatives we ruled out

- **Stay manual-copy only (ADR 0020's call).** Leaves us at the fallback tier on a
  tool that now has a real marketplace; forfeits the discovery surfaces. Reversed.
- **One shared `marketplace.json` listing every adapter.** Can't — a marketplace
  can't have two plugins named `debt-ops`, and the per-tool native marketplace dirs
  (`.cursor-plugin/`, `.claude-plugin/`, `.github/plugin/`, `.agents/plugins/`) each
  point at the right adapter without a name clash.
- **Reuse the manual `hooks.json` as the plugin config.** Its `.cursor/hooks/` paths
  don't resolve from the plugin install dir, so the write-time loop would silently
  no-op — the adapter's whole reason to exist.
- **Fork the hook scripts (plugin copy with chdir, manual copy without).** More
  drift surface; `chdir_to_workspace` is a safe no-op in project mode, so one set
  serves both.

## Payoff trigger

Revisit when: a live Cursor install contradicts the `${CURSOR_PLUGIN_ROOT}` / cwd /
discovery assumptions above (fix the wiring); or the two hooks-config files drift
(collapse to one install mode); or Cursor adds a plugin-root cwd guarantee that
makes `chdir_to_workspace` unnecessary.
