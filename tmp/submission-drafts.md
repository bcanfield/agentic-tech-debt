# Submission drafts: copy-paste material for the NOW checklist

Scratch file backing `docs/publishing-checklist.md`. Each section maps to one
submission. If a newer release ships before you submit, swap the tag (latest as
of writing: `debt-ops-v0.8.1`).

## 1. Anthropic community marketplace

Form: <https://claude.ai/settings/plugins/submit> (or <https://platform.claude.com/plugins/submit>)

- **Plugin name:** debt-ops
- **Repository:** https://github.com/bcanfield/agentic-tech-debt
- **Plugin path / source:** `./claude-code` (marketplace manifest: `.claude-plugin/marketplace.json`)
- **Description:** Hooks watch your agent's edits and log each deferral to a registry in your repo: the `as any` cast that clears a type error, the default picked "for now." A review skill ranks the backlog by file churn and Fowler quadrant so you pay down what actually hurts. Architectural calls get a short ADR.
- **Category:** productivity
- **License:** MIT
- **Privacy:** fully local. Stdlib Python, no network calls, no telemetry. Privacy policy: https://github.com/bcanfield/agentic-tech-debt/blob/main/PRIVACY.md
- **Pre-flight:** `claude plugin validate ./claude-code --strict` passes (2026-06-06).

## 2. github/awesome-copilot external plugin issue

Issue form: <https://github.com/github/awesome-copilot/issues/new/choose>, external plugin template.
Don't PR `plugins/external.json` directly.

- **name:** debt-ops
- **description** (must match plugin.json verbatim): Catches AI-introduced tech debt at write-time. Every "I'll fix this later," every shortcut, every punt your AI agent writes gets caught.
- **version:** 0.8.1
- **author.name:** Brandin Canfield
- **repository:** https://github.com/bcanfield/agentic-tech-debt
- **keywords:** tech-debt, code-health, hotspots, adr, productivity
- **license:** MIT
- **source.source:** github
- **source.repo:** bcanfield/agentic-tech-debt
- **source ref (immutable):** `debt-ops-v0.8.1` (release tag)
- Notes for the form: the plugin lives at `./copilot` per `.github/plugin/marketplace.json`.
  Hooks are stdlib Python with no network calls. Install smoke test:
  `copilot plugin marketplace add bcanfield/agentic-tech-debt && copilot plugin install debt-ops@agentic-tech-debt`.

## 3. ClaudePluginHub

Submit: <https://www.claudepluginhub.com/tools/submit-plugin>. Paste the repo URL,
then claim the listing for the verified badge and the install-count README badge.

## 4. Codex community lists (PRs)

One-line entries. Match each list's existing format and category before opening the PR.

**hashgraph-online/awesome-codex-plugins:**

```
- [debt-ops](https://github.com/bcanfield/agentic-tech-debt) - Logs the tech debt your agent writes as it writes it, then ranks paydown by file churn. `codex plugin marketplace add bcanfield/agentic-tech-debt`
```

**RoggeOhta/awesome-codex-cli:**

```
- [debt-ops](https://github.com/bcanfield/agentic-tech-debt) - Write-time tech-debt capture for Codex. Hooks log deferred decisions to a registry in your repo; a review skill ranks what to fix first.
```

## 5. jqueryscript/awesome-claude-code Plugins section (PR)

```
- [debt-ops](https://github.com/bcanfield/agentic-tech-debt) - Catches deferred decisions (loosened types, "for now" defaults) as your agent writes them and logs them to a registry in your repo.
```
