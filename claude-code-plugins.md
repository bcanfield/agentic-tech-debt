# Claude Code Plugins: A Field Guide

A reference for every piece of a Claude Code plugin: what it is, when to reach for it, and a real GitHub example you can read or install today.

A **plugin** is a self-contained directory that extends Claude Code with custom functionality. Plugins are distributed through marketplaces, copied into a local cache on install (`~/.claude/plugins/cache`), and discovered by Claude Code automatically. Anything you can do with `.claude/` standalone configuration you can do inside a plugin. Plugins add versioning, namespacing, and shareability.

Use **standalone `.claude/`** for personal or project-only workflows where you want short skill names like `/deploy`. Use a **plugin** when you want versioning, namespaced commands like `/my-plugin:deploy`, or distribution to a team or community.

---

## Table of contents

1. [Plugin manifest (`plugin.json`)](#1-plugin-manifest-pluginjson)
2. [Skills (`skills/`)](#2-skills-skills)
3. [Commands (`commands/`)](#3-commands-commands)
4. [Subagents (`agents/`)](#4-subagents-agents)
5. [Hooks (`hooks/hooks.json`)](#5-hooks-hookshooksjson)
6. [MCP servers (`.mcp.json`)](#6-mcp-servers-mcpjson)
7. [LSP servers (`.lsp.json`)](#7-lsp-servers-lspjson)
8. [Background monitors (`monitors/monitors.json`)](#8-background-monitors-monitorsmonitorsjson)
9. [Themes (`themes/`)](#9-themes-themes)
10. [Output styles (`output-styles/`)](#10-output-styles-output-styles)
11. [Default plugin settings (`settings.json`)](#11-default-plugin-settings-settingsjson)
12. [Bundled executables (`bin/`)](#12-bundled-executables-bin)
13. [User configuration (`userConfig`)](#13-user-configuration-userconfig)
14. [Channels](#14-channels)
15. [Plugin dependencies](#15-plugin-dependencies)
16. [Marketplaces (`marketplace.json`)](#16-marketplaces-marketplacejson)
17. [Environment variables and persistent data](#17-environment-variables-and-persistent-data)
18. [CLI commands](#18-cli-commands)
19. [Worked example layout](#19-worked-example-layout)
20. [Sources](#sources)

---

## 1. Plugin manifest (`plugin.json`)

**What it is.** A JSON file at `.claude-plugin/plugin.json` that identifies the plugin, declares its version, and optionally overrides default component paths. It is the only file that belongs in `.claude-plugin/`. Every other directory (skills, agents, hooks) lives at the plugin root.

**When to use it.** Always when distributing. The manifest is technically optional (Claude Code can auto-discover components and use the directory name), but you need it as soon as you want a stable name, version pinning, marketplace metadata, or non-default component paths.

**Minimal manifest.**

```json
{
  "name": "my-first-plugin",
  "description": "A greeting plugin to learn the basics",
  "version": "1.0.0",
  "author": { "name": "Your Name" }
}
```

**Full schema fields.** `name` (required, kebab-case, becomes the namespace prefix), `version` (semver; omit to fall back to the git commit SHA), `description`, `author`, `homepage`, `repository`, `license`, `keywords`, plus path overrides: `skills`, `commands`, `agents`, `hooks`, `mcpServers`, `lspServers`, `monitors`, `outputStyles`, `themes`, plus `userConfig`, `channels`, `dependencies`.

**Versioning rule.** If `version` is set, you **must bump it** for users to receive updates. Pushing new commits without bumping is silently a no-op. Omit `version` while iterating; add it for stable releases.

**Live example.** [`anthropics/claude-plugins-official` — `plugins/example-plugin/.claude-plugin/plugin.json`](https://github.com/anthropics/claude-plugins-official) is the canonical reference implementation. The `plugin-dev` plugin in the same repo is the meta-plugin Anthropic uses to scaffold new plugins.

---

## 2. Skills (`skills/`)

**What it is.** A skill is a folder under `skills/` containing a `SKILL.md` with YAML frontmatter and instructions. Each folder name becomes a slash command, namespaced by the plugin: `skills/code-review/SKILL.md` in plugin `acme-tools` becomes `/acme-tools:code-review`. Skills can be **model-invoked** (Claude picks them based on the `description`) or **explicit** (`disable-model-invocation: true`).

**When to use it.** Skills are the workhorse: use them for any reusable workflow, prompt, or knowledge package. Prefer `skills/` over the older flat `commands/` layout because skills support supporting files (`reference.md`, `scripts/`) and progressive disclosure.

**Example `SKILL.md`.**

```markdown
---
description: Reviews code for bugs, security, and performance. Use when reviewing PRs or analyzing code quality.
---

When reviewing code, check for:
1. Code organization and structure
2. Error handling
3. Security concerns
4. Test coverage
```

Skills can take arguments via `$ARGUMENTS`. They can also restrict tools via frontmatter and load supporting files lazily.

**Live examples.**
- [`anthropics/claude-code/plugins`](https://github.com/anthropics/claude-code/tree/main/plugins): `plugin-dev` ships seven expert skills covering plugin scaffolding, hook development, MCP integration, and more.
- [`anthropics/skills`](https://github.com/anthropics/skills): Anthropic's public Agent Skills repository (PDF processing, document analysis).

---

## 3. Commands (`commands/`)

**What it is.** A flat-file alternative to `skills/`: any `.md` file under `commands/` becomes a slash command. Same invocation namespace (`/plugin-name:command-name`), but no folder, no supporting files.

**When to use it.** Quick one-shot commands that don't need scripts or reference material. Anthropic recommends new plugins prefer `skills/`. `commands/` is supported for backwards compatibility and the simplest cases.

**Live example.** [`wshobson/commands`](https://github.com/wshobson/commands): production-ready slash commands for Claude Code, organized as flat markdown files ready to drop into a plugin's `commands/` folder.

---

## 4. Subagents (`agents/`)

**What it is.** Markdown files under `agents/` that define specialized subagents Claude can spawn for focused tasks. Each agent has YAML frontmatter declaring its name, description, model, tool restrictions, and reasoning effort, plus a body that becomes its system prompt.

**When to use it.** For tasks that benefit from a fresh context window, a different model, or a tightly scoped toolset: code review, security audits, test generation, research that would pollute the main thread.

**Plugin agent frontmatter** supports: `name`, `description`, `model`, `effort`, `maxTurns`, `tools`, `disallowedTools`, `skills`, `memory`, `background`, and `isolation` (only `"worktree"` is valid). For security, plugin-shipped agents **cannot** define `hooks`, `mcpServers`, or `permissionMode`.

```markdown
---
name: security-reviewer
description: Audits code changes for OWASP top-10 vulnerabilities. Use after writes to auth, crypto, or input-handling code.
model: opus
effort: high
disallowedTools: Write, Edit
---

You are a senior application-security engineer. Review the diff for...
```

**Live examples.**
- [`wshobson/agents`](https://github.com/wshobson/agents): 80 plugins, 185 specialized agents (architect-review, security-auditor, kubernetes-architect) using a tiered Opus/Sonnet/Haiku model strategy.
- [`VoltAgent/awesome-claude-code-subagents`](https://github.com/VoltAgent/awesome-claude-code-subagents): 100+ curated subagents.
- [`anthropics/claude-plugins-official` — `pr-review-toolkit`](https://github.com/anthropics/claude-plugins-official): five specialized PR-review agents (comments, tests, error handling, type design, code quality).

---

## 5. Hooks (`hooks/hooks.json`)

**What it is.** Event-driven shell commands, HTTP calls, MCP tool calls, prompts, or sub-agents that fire on Claude Code lifecycle events. Hooks are the one feature that lets your plugin **enforce** behavior rather than suggest it.

**When to use it.** Auto-format on `PostToolUse`, block dangerous commands on `PreToolUse`, inject project context on `SessionStart`, run tests after edits, scan for secrets before commits, react to file changes with `FileChanged`.

**Available events** (selected): `SessionStart`, `UserPromptSubmit`, `PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `PostToolBatch`, `PermissionRequest`, `PermissionDenied`, `SubagentStart`, `SubagentStop`, `Stop`, `Notification`, `FileChanged`, `CwdChanged`, `PreCompact`, `PostCompact`, `WorktreeCreate`, `SessionEnd`, plus task and instruction events.

**Hook types:** `command` (shell), `http` (POST event JSON), `mcp_tool`, `prompt` (LLM evaluation), `agent` (verifier subagent).

**Example.**

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PLUGIN_ROOT}/scripts/format-code.sh"
          }
        ]
      }
    ]
  }
}
```

Hook scripts receive event JSON on stdin (use `jq -r '.tool_input.file_path'` to extract fields) and use `${CLAUDE_PLUGIN_ROOT}` to reference bundled scripts.

**Live examples.**
- [`disler/claude-code-hooks-mastery`](https://github.com/disler/claude-code-hooks-mastery): exhaustive hook patterns including sub-agent orchestration and team validation.
- [`disler/claude-code-hooks-multi-agent-observability`](https://github.com/disler/claude-code-hooks-multi-agent-observability): real-time monitoring built on hook events.
- [`anthropics/claude-plugins-official` — `security-guidance`](https://github.com/anthropics/claude-plugins-official): warns on command injection, XSS, eval usage during edits.
- [`anthropics/claude-plugins-official` — `hookify`](https://github.com/anthropics/claude-plugins-official): meta-plugin that generates new hooks from a transcript.

---

## 6. MCP servers (`.mcp.json`)

**What it is.** Bundled Model Context Protocol servers that auto-start when the plugin is enabled, exposing external systems (databases, APIs, internal services) as Claude tools. Configured in `.mcp.json` at the plugin root or inline under `mcpServers` in `plugin.json`.

**When to use it.** When your plugin needs to talk to a system that isn't a CLI: internal APIs, vector stores, ticketing systems, observability backends. Bundling the MCP server in a plugin means users get the integration automatically when they install.

**Example.**

```json
{
  "mcpServers": {
    "plugin-database": {
      "command": "${CLAUDE_PLUGIN_ROOT}/servers/db-server",
      "args": ["--config", "${CLAUDE_PLUGIN_ROOT}/config.json"],
      "env": { "DB_PATH": "${CLAUDE_PLUGIN_ROOT}/data" }
    }
  }
}
```

**Live examples.**
- [`github/github-mcp-server`](https://github.com/github/github-mcp-server): GitHub's official MCP server (issues, PRs, code search).
- [`zilliztech/claude-context`](https://github.com/zilliztech/claude-context): semantic codebase search MCP for Claude Code.
- [`steipete/claude-code-mcp`](https://github.com/steipete/claude-code-mcp): Claude Code as a one-shot MCP server (agent-in-an-agent).

---

## 7. LSP servers (`.lsp.json`)

**What it is.** Language Server Protocol configurations that give Claude real-time diagnostics, go-to-definition, find-references, and hover info while editing. Configured in `.lsp.json` or inline under `lspServers` in `plugin.json`.

**When to use it.** Mostly, don't roll your own. Anthropic ships official LSP plugins for the common languages (`pyright-lsp`, `typescript-lsp`, `rust-lsp`). Build a custom LSP plugin only when targeting a language Anthropic hasn't covered. The user must have the language-server binary installed; the plugin only configures the connection.

**Example.**

```json
{
  "go": {
    "command": "gopls",
    "args": ["serve"],
    "extensionToLanguage": { ".go": "go" }
  }
}
```

Optional fields include `transport` (stdio/socket), `env`, `initializationOptions`, `settings`, `startupTimeout`, `restartOnCrash`, `maxRestarts`.

**Live example.** Search the official `/plugin Discover` tab for `lsp`. `pyright-lsp`, `typescript-lsp`, and `rust-lsp` are all distributed via [`anthropics/claude-plugins-official`](https://github.com/anthropics/claude-plugins-official).

---

## 8. Background monitors (`monitors/monitors.json`)

**What it is.** Long-running shell commands started automatically when the plugin loads. Each stdout line is delivered to Claude as a notification, so Claude reacts to log entries, deploy status, or polled events without being asked to start the watch. Requires Claude Code v2.1.105+, interactive sessions only, runs unsandboxed at hook trust level.

**When to use it.** Tail an error log, poll a deploy status endpoint, watch a queue depth, surface CI events: anything where Claude should react to external state changes during the session.

**Example.**

```json
[
  {
    "name": "deploy-status",
    "command": "${CLAUDE_PLUGIN_ROOT}/scripts/poll-deploy.sh ${user_config.api_endpoint}",
    "description": "Deployment status changes"
  },
  {
    "name": "error-log",
    "command": "tail -F ./logs/error.log",
    "description": "Application error log",
    "when": "on-skill-invoke:debug"
  }
]
```

`when` defaults to `"always"` (start at session start). `"on-skill-invoke:<skill>"` defers startup until that skill is first invoked.

---

## 9. Themes (`themes/`)

**What it is.** JSON files under `themes/` that ship color themes selectable from `/theme`. Each theme declares a `base` preset (dark or light) and a sparse `overrides` map of color tokens.

**When to use it.** Distribute branded color schemes, accessibility-focused themes, or popular community palettes (Dracula, Solarized). Plugin themes are read-only; users press Ctrl+E in `/theme` to copy one to `~/.claude/themes/` for editing.

**Example.**

```json
{
  "name": "Dracula",
  "base": "dark",
  "overrides": {
    "claude": "#bd93f9",
    "error": "#ff5555",
    "success": "#50fa7b"
  }
}
```

---

## 10. Output styles (`output-styles/`)

**What it is.** Markdown files under `output-styles/` that change how Claude formats its responses (terse, verbose, educational tone).

**When to use it.** When the plugin wants to enforce a particular conversational style: security review tone, teaching tone, terminal-only output.

**Live examples.**
- [`anthropics/claude-plugins-official` — `explanatory-output-style`](https://github.com/anthropics/claude-plugins-official): adds educational insights about implementation choices via a `SessionStart` hook.
- [`anthropics/claude-plugins-official` — `learning-output-style`](https://github.com/anthropics/claude-plugins-official): interactive learning mode that pauses at decision points.

---

## 11. Default plugin settings (`settings.json`)

**What it is.** A `settings.json` at the plugin root that applies defaults when the plugin is enabled. Currently only the `agent` and `subagentStatusLine` keys are honored; unknown keys are silently ignored.

**When to use it.** When a plugin should change Claude Code's *default behavior* on enable, most commonly by activating one of the plugin's bundled subagents as the main thread.

```json
{ "agent": "security-reviewer" }
```

Setting `agent` swaps the main loop's system prompt, model, and tool restrictions for the named plugin agent. This is how a plugin can ship as "Claude Code, but specialized for X."

---

## 12. Bundled executables (`bin/`)

**What it is.** Anything dropped into `bin/` is added to `PATH` whenever the plugin is enabled, so the Bash tool can invoke it as a bare command.

**When to use it.** Ship CLI helpers your skills and hooks call: formatters, linters, custom wrappers, internal scripts. This avoids hard-coding `${CLAUDE_PLUGIN_ROOT}/bin/foo` everywhere.

---

## 13. User configuration (`userConfig`)

**What it is.** A schema declared in `plugin.json` for values Claude Code prompts the user for at enable time, replacing hand-edits to `settings.json`. Each option has a `type` (`string`, `number`, `boolean`, `directory`, `file`), `title`, `description`, and optional `sensitive`, `required`, `default`, `multiple`, `min`/`max`.

**When to use it.** API endpoints, tokens, paths to user-owned resources: anything that varies per user and must not be hard-coded.

```json
{
  "userConfig": {
    "api_endpoint": {
      "type": "string",
      "title": "API endpoint",
      "description": "Your team's API endpoint"
    },
    "api_token": {
      "type": "string",
      "title": "API token",
      "description": "API authentication token",
      "sensitive": true
    }
  }
}
```

Values are substituted as `${user_config.api_endpoint}` in MCP, LSP, hook, and monitor configs, and exported to subprocesses as `CLAUDE_PLUGIN_OPTION_API_ENDPOINT`. **`sensitive: true` values go to the system keychain** (or `~/.claude/.credentials.json`), not `settings.json`. Keep them under ~2 KB total since the keychain bucket is shared with OAuth tokens.

---

## 14. Channels

**What it is.** A `channels` array in `plugin.json` that declares message channels (Telegram, Slack, Discord-style) which inject content into the conversation. Each channel binds to one of the plugin's MCP servers and can prompt for its own credentials via per-channel `userConfig`.

**When to use it.** When the plugin enables Claude to receive messages from outside the terminal: chat-bridge plugins, on-call paging.

```json
{
  "channels": [
    {
      "server": "telegram",
      "userConfig": {
        "bot_token": { "type": "string", "title": "Bot token", "sensitive": true },
        "owner_id":  { "type": "string", "title": "Owner ID", "description": "Your Telegram user ID" }
      }
    }
  ]
}
```

---

## 15. Plugin dependencies

**What it is.** A `dependencies` array in `plugin.json` declaring other plugins this plugin requires, optionally with semver constraints. Cross-marketplace dependencies must be allow-listed in the marketplace's `allowCrossMarketplaceDependenciesOn` field.

```json
{
  "dependencies": [
    "helper-lib",
    { "name": "secrets-vault", "version": "~2.1.0" }
  ]
}
```

**When to use it.** Split a large plugin into reusable building blocks (a shared `secrets-vault` plugin that auth plugins depend on). `claude plugin prune` cleans up auto-installed dependencies no longer needed.

---

## 16. Marketplaces (`marketplace.json`)

**What it is.** A catalog at `.claude-plugin/marketplace.json` (in a *marketplace* repo, separate from individual plugin repos) listing plugins and where to fetch each one. Marketplaces **index** plugins; they don't have to host them. Plugin sources can point anywhere.

**When to use it.** As soon as you want users to `/plugin install foo@your-marketplace` instead of cloning a directory and pointing at it with `--plugin-dir`.

**Minimal example.**

```json
{
  "name": "my-plugins",
  "owner": { "name": "Your Name" },
  "plugins": [
    {
      "name": "quality-review-plugin",
      "source": "./plugins/quality-review-plugin",
      "description": "Adds a /quality-review skill for quick code reviews"
    }
  ]
}
```

**Plugin source types.**

| Source        | When to use                                                                  |
| ------------- | ---------------------------------------------------------------------------- |
| Relative path | Plugin lives in the same repo as the marketplace                             |
| `github`      | Plugin lives in another GitHub repo (`{repo, ref?, sha?}`)                   |
| `url`         | Any git URL (GitLab, Bitbucket, self-hosted, Azure DevOps, AWS CodeCommit)   |
| `git-subdir`  | Plugin lives in a subdirectory of a monorepo (uses sparse partial clone)     |
| `npm`         | Plugin published as an npm package (public or private registry)              |

**Strict mode.** Each plugin entry can set `strict: false` to make the marketplace entry, not the plugin's own `plugin.json`, the authority for component definitions. Useful when curating or restructuring third-party plugins.

**Reserved marketplace names** (cannot be used by third parties): `claude-code-marketplace`, `claude-code-plugins`, `claude-plugins-official`, `anthropic-marketplace`, `anthropic-plugins`, `agent-skills`, `knowledge-work-plugins`, `life-sciences`.

**Live examples.**
- [`anthropics/claude-plugins-official`](https://github.com/anthropics/claude-plugins-official): Anthropic's official marketplace (internal in `/plugins`, third-party in `/external_plugins`).
- [`anthropics/knowledge-work-plugins`](https://github.com/anthropics/knowledge-work-plugins): Anthropic's marketplace for non-engineering workflows.
- [`ivan-magda/claude-code-plugin-template`](https://github.com/ivan-magda/claude-code-plugin-template): GitHub template with marketplace scaffolding, validation commands, and CI/CD workflows.
- [`mrlm-xyz/demo-claude-marketplace`](https://github.com/mrlm-xyz/demo-claude-marketplace): minimal demonstration marketplace.

---

## 17. Environment variables and persistent data

Two variables are substituted everywhere and exported to all plugin subprocesses:

- **`${CLAUDE_PLUGIN_ROOT}`**: absolute path to the installed plugin directory in `~/.claude/plugins/cache`. **Changes when the plugin updates.** Anything written here does not survive an update.
- **`${CLAUDE_PLUGIN_DATA}`**: persistent directory at `~/.claude/plugins/data/{id}/` that survives updates. Use it for `node_modules`, virtualenvs, generated code, caches.

**Pattern: install dependencies on first run and after dependency changes.**

```json
{
  "hooks": {
    "SessionStart": [{
      "hooks": [{
        "type": "command",
        "command": "diff -q \"${CLAUDE_PLUGIN_ROOT}/package.json\" \"${CLAUDE_PLUGIN_DATA}/package.json\" >/dev/null 2>&1 || (cd \"${CLAUDE_PLUGIN_DATA}\" && cp \"${CLAUDE_PLUGIN_ROOT}/package.json\" . && npm install) || rm -f \"${CLAUDE_PLUGIN_DATA}/package.json\""
      }]
    }]
  }
}
```

The `diff` exits nonzero on first run or when the bundled manifest changes; the trailing `rm` lets the next session retry if `npm install` fails.

**Path-traversal limitation.** Installed plugins cannot reference files outside their directory (`../shared-utils` won't work after install; those files aren't copied to the cache). Use symlinks: `ln -s /path/to/shared-utils ./shared-utils` is preserved in the cache and resolved at runtime.

---

## 18. CLI commands

| Command                              | Purpose                                                                   |
| ------------------------------------ | ------------------------------------------------------------------------- |
| `claude --plugin-dir ./my-plugin`    | Load a local plugin for the current session (no install). Repeatable.     |
| `/reload-plugins`                    | Pick up plugin changes mid-session without restarting.                    |
| `/plugin marketplace add <source>`   | Register a marketplace (GitHub repo, git URL, local path).                |
| `/plugin marketplace update`         | Refresh marketplace catalogs.                                             |
| `/plugin install <name>@<market>`    | Install a plugin (`--scope user|project|local`).                          |
| `claude plugin uninstall <name>`     | Remove. `--keep-data` preserves `${CLAUDE_PLUGIN_DATA}`. `--prune` cleans deps. |
| `claude plugin prune`                | Remove orphaned auto-installed dependencies.                              |
| `claude plugin enable/disable`       | Toggle without uninstalling.                                              |
| `claude plugin update <name>`        | Pull a new version (respects pinned `version` field).                     |
| `claude plugin list [--json]`        | Show installed plugins, version, source, status.                          |
| `claude plugin tag [--push]`         | Create a release git tag from inside the plugin's folder.                 |
| `claude --debug`                     | Print plugin loading details (manifest errors, registration, MCP init).   |
| `claude plugin validate`             | Lint `plugin.json`, frontmatter, `hooks.json` for schema and syntax errors.|

**Installation scopes.** `user` (`~/.claude/settings.json`, default), `project` (`.claude/settings.json`, version-controlled), `local` (`.claude/settings.local.json`, gitignored), `managed` (read-only, admin-controlled).

---

## 19. Worked example layout

A plugin that uses every component looks like this:

```text
enterprise-plugin/
├── .claude-plugin/
│   └── plugin.json              # only file in here
├── skills/
│   ├── code-reviewer/SKILL.md
│   └── pdf-processor/
│       ├── SKILL.md
│       ├── reference.md
│       └── scripts/
├── commands/                    # legacy flat-file skills
│   └── status.md
├── agents/
│   ├── security-reviewer.md
│   └── compliance-checker.md
├── output-styles/terse.md
├── themes/dracula.json
├── monitors/monitors.json
├── hooks/
│   ├── hooks.json
│   └── security-hooks.json
├── bin/my-tool                  # added to PATH while enabled
├── settings.json                # default agent / status line
├── .mcp.json                    # MCP servers
├── .lsp.json                    # LSP servers
├── scripts/                     # called by hooks
│   ├── format-code.py
│   └── deploy.js
├── LICENSE
└── CHANGELOG.md
```

---

## Sources

### Official documentation
- [Create plugins — Claude Code Docs](https://code.claude.com/docs/en/plugins)
- [Plugins reference — Claude Code Docs](https://code.claude.com/docs/en/plugins-reference)
- [Create and distribute a plugin marketplace — Claude Code Docs](https://code.claude.com/docs/en/plugin-marketplaces)
- [Discover and install prebuilt plugins — Claude Code Docs](https://code.claude.com/docs/en/discover-plugins)
- [Slash Commands in the SDK — Claude Code Docs](https://code.claude.com/docs/en/agent-sdk/slash-commands)
- [Create custom subagents — Claude Code Docs](https://code.claude.com/docs/en/sub-agents)
- [Automate workflows with hooks — Claude Code Docs](https://code.claude.com/docs/en/hooks-guide)
- [Connect Claude Code to tools via MCP — Claude Code Docs](https://code.claude.com/docs/en/mcp)
- [Claude Code settings — Claude Code Docs](https://docs.anthropic.com/en/docs/claude-code/settings)

### Live GitHub examples
- [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official): official marketplace; reference `example-plugin`, `plugin-dev`, `code-review`, `pr-review-toolkit`, `security-guidance`, `hookify`, `feature-dev`, `commit-commands`, `frontend-design`, `ralph-wiggum`, `learning-output-style`, `explanatory-output-style`, `agent-sdk-dev`, `claude-opus-4-5-migration`.
- [anthropics/claude-code](https://github.com/anthropics/claude-code/tree/main/plugins): Claude Code source repo with bundled plugins.
- [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins): Anthropic's marketplace for non-engineering workflows.
- [anthropics/skills](https://github.com/anthropics/skills): public Agent Skills repository.
- [wshobson/agents](https://github.com/wshobson/agents): 80 plugins, 185 specialized subagents with tiered model strategy.
- [wshobson/commands](https://github.com/wshobson/commands): production-ready slash commands collection.
- [VoltAgent/awesome-claude-code-subagents](https://github.com/VoltAgent/awesome-claude-code-subagents): 100+ curated subagents.
- [disler/claude-code-hooks-mastery](https://github.com/disler/claude-code-hooks-mastery): exhaustive hook patterns.
- [disler/claude-code-hooks-multi-agent-observability](https://github.com/disler/claude-code-hooks-multi-agent-observability): real-time hook-event monitoring.
- [github/github-mcp-server](https://github.com/github/github-mcp-server): official GitHub MCP server.
- [zilliztech/claude-context](https://github.com/zilliztech/claude-context): semantic codebase search MCP.
- [steipete/claude-code-mcp](https://github.com/steipete/claude-code-mcp): Claude Code as a one-shot MCP server.
- [ivan-magda/claude-code-plugin-template](https://github.com/ivan-magda/claude-code-plugin-template): marketplace template with validation and CI.
- [mrlm-xyz/demo-claude-marketplace](https://github.com/mrlm-xyz/demo-claude-marketplace): minimal marketplace demo.

### Curated lists
- [ComposioHQ/awesome-claude-plugins](https://github.com/ComposioHQ/awesome-claude-plugins)
- [hesreallyhim/awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code)
- [ccplugins/awesome-claude-code-plugins](https://github.com/ccplugins/awesome-claude-code-plugins)
- [rohitg00/awesome-claude-code-toolkit](https://github.com/rohitg00/awesome-claude-code-toolkit)
- [jmanhype/awesome-claude-code](https://github.com/jmanhype/awesome-claude-code)
