# Where to Submit an AI Coding-Agent Plugin/Extension for Maximum Visibility (2025–2026)

## TL;DR
- **The single highest-leverage move is to package your tool as an MCP server and publish it once to the official MCP Registry (registry.modelcontextprotocol.io via the `mcp-publisher` CLI), because that one publish auto-propagates to the largest downstream consumers** — GitHub's MCP Registry (github.com/mcp), PulseMCP, Glama, and others. The registry's own promise is "Unified Discovery: Server creators publish once, all consumers reference the same canonical data." Then list natively where your tool actually runs (Anthropic's Claude plugins/Connectors directory, Cline, Cursor, VS Code), and do one coordinated launch wave (Show HN + Product Hunt + relevant subreddits + the awesome-lists).
- **Old GitHub Copilot Extensions (GitHub App-based) are dead:** Per GitHub's Changelog (Sept 24, 2025), "We are deprecating GitHub Copilot Extensions (built as GitHub Apps) on November 10, 2025, in favor of Model Context Protocol (MCP) servers." Do NOT spend time on the legacy "List in Marketplace" flow — build an MCP server instead.
- **Treat distribution as one-time registry publishing (set up CI/CD so every release re-publishes) plus ongoing community presence** (newsletters, Discords, content). The registries are where adoption compounds; the launch platforms are a one-day spike.

## Key Findings
1. **MCP is now the universal distribution substrate.** Whether your tool is a Claude Code plugin, a slash-command extension, or a standalone server, exposing it (or part of it) as an MCP server unlocks the broadest set of clients (Claude, Copilot, Cursor, Windsurf, Cline, Codex, VS Code) and the richest registry ecosystem. The official registry is a "metaregistry" — it hosts metadata only and is designed to be consumed by downstream marketplaces.
2. **Publish once, appear everywhere.** The official MCP Registry (modelcontextprotocol.io/registry/about) is "the official centralized metadata repository for publicly accessible MCP servers, backed by major trusted contributors… such as Anthropic, GitHub, PulseMCP, and Microsoft." GitHub's registry, PulseMCP, and others ingest from it. This makes the official registry the highest-ROI single action.
3. **First-party native marketplaces matter most for your specific runtime.** If you ship a Claude Code plugin, Anthropic's `claude-plugins-official` marketplace and the in-product Connectors/Plugins directory are the canonical homes; Cline's marketplace reaches a large installed base (cline.bot advertises "Trusted by 8M+ developers," with ~3.85M recorded in the VS Code Marketplace as of May 2026 and 62.8k GitHub stars); Cursor/Windsurf each have in-app MCP marketplaces.
4. **"Awesome" lists and third-party directories are still high-signal** but increasingly gated on quality (e.g., punkpeye/awesome-mcp-servers now effectively expects a Glama listing; Cline reviews for community adoption and security).
5. **GitHub Copilot's path changed fundamentally in late 2025** — build an MCP server, not a Copilot Extension.
6. **Launch platforms (Show HN, Product Hunt, Reddit) are spiky and norm-sensitive;** they reward authentic, story-driven posts and punish overt self-promotion.

## Details

### 1. Official / first-party marketplaces and plugin registries

**Anthropic — Claude Code plugin marketplace system**
- What it is: Claude Code plugins bundle slash commands, subagents, skills, hooks, MCP servers, and LSP servers. A "marketplace" is just a Git repo containing `.claude-plugin/marketplace.json` that points at plugins. Users run `/plugin marketplace add owner/repo` then `/plugin install name@marketplace`.
- How to list (your own marketplace): create `.claude-plugin/marketplace.json` at your repo root with `name`, `owner`, and a `plugins[]` array (each entry needs at minimum a `name` and `source`). Each plugin needs `.claude-plugin/plugin.json`. This is automated/self-serve — anyone can host a marketplace; discovery happens when you share the repo or get listed elsewhere.
- URL: https://code.claude.com/docs/en/plugin-marketplaces

**Anthropic-maintained official marketplace — `anthropics/claude-plugins-official`**
- What it is: "Official, Anthropic-managed directory of high quality Claude Code Plugins." Curated; includes partner plugins (42Crunch, Box, Bright Data, Microsoft docs, etc.).
- How to list: curated/reviewed. "Third-party partners can submit plugins for inclusion… External plugins must meet quality and security standards for approval. To submit a new plugin, use the plugin directory submission form."
- URL: https://github.com/anthropics/claude-plugins-official
- Tip: This is the highest-prestige Claude Code listing; run `claude plugin validate` before submitting.

**Anthropic Connectors Directory (Claude.ai / Claude Desktop)**
- What it is: Anthropic's vetted directory of MCP servers/connectors and MCP Apps surfaced across Claude products. Also covers Desktop Extensions (`.mcpb` packages).
- How to list: form-based + Anthropic review. Requirements include public documentation by publish date, a complete privacy policy (missing/incomplete = immediate rejection), OAuth/HTTPS/Origin-header validation, tool annotations, and (for MCP Apps) promotional screenshots. Separate submission forms for Desktop extensions (MCPB) vs remote connectors.
- URL: https://claude.com/docs/connectors/building/submission
- In-product: Claude's "Customize" menu → Plugins / Connectors tabs; the "Knowledge Work" marketplace is added by default, plus Financial Services, Legal, Life Sciences.

**Official MCP Registry (the canonical metaregistry)**
- What it is: The official centralized metadata repository for publicly accessible MCP servers. Per the registry repo README: "2025-09-08 update: The registry has launched in preview" and "2025-10-24 update: The Registry API has entered an API freeze (v0.1)… the API will remain stable with no breaking changes." It was driven to launch by David Soria Parra (Lead Maintainer), Adam Jones (Anthropic), Tadas Antanavicius (PulseMCP), and Toby Padilla (GitHub's Head of MCP).
- How to publish: use the `mcp-publisher` CLI. Steps: (1) publish your package to npm/PyPI/NuGet/Docker/GHCR first (the registry hosts metadata only); (2) add an ownership marker — `mcpName` in package.json for npm, `mcp-name:` in README for PyPI, an `io.modelcontextprotocol.server.name` label for Docker; (3) run `mcp-publisher init` to generate `server.json`; (4) authenticate via GitHub OAuth or DNS/HTTP for company namespaces; (5) `mcp-publisher publish`. Namespaces use reverse-DNS (`io.github.you/server` or `com.yourco/server`).
- URLs: https://registry.modelcontextprotocol.io/ • https://github.com/modelcontextprotocol/registry • Quickstart: https://github.com/modelcontextprotocol/registry/blob/main/docs/modelcontextprotocol-io/quickstart.mdx
- Tip: Wire publishing into CI/CD (GitHub OIDC auth, `continue-on-error: true`) so each tagged release re-publishes — otherwise your listing goes stale at v1.0.0 while users install old versions.

**MCP reference servers repo — `modelcontextprotocol/servers`**
- What it is: Official reference implementations + a community showcase. Very selective.
- How to list: PR to the repo following strict guidelines; best reserved for genuinely reference-quality servers.
- URL: https://github.com/modelcontextprotocol/servers

**GitHub Copilot — the path changed (read carefully)**
- **Legacy Copilot Extensions (GitHub App-based) were sunset November 10, 2025.** Per the GitHub Changelog (Sept 24, 2025): creation of new ones was blocked after Sept 24, 2025 8:00 AM PST; a brownout testing period ran Nov 3–7; full sunset was Nov 10, 2025 11:59 PM PST; the Marketplace "Copilot Extensions" category was removed. Do not pursue this path.
- **Current path #1 — GitHub MCP Registry (github.com/mcp):** GitHub's discovery home for MCP servers, public preview since Sept 2025, launched with 40+ verified partner servers (Figma, HashiCorp, Stripe, Microsoft, etc.) while the OSS community registry already listed 1,000+ self-published entries (per the Sept 16, 2025 GitHub Changelog "GitHub MCP Registry: The fastest way to discover AI tools"). Each entry shows the repo README, stars, and a one-click VS Code install button. To get listed: self-publish to the OSS MCP Community Registry (the official registry above) — GitHub's model is that published servers automatically appear in the GitHub MCP Registry. (Caveat: auto-propagation was still maturing in late 2025; the OSS registry grew to nearly 2,000 entries by Nov 2025, a 407% increase from its Sept launch batch, far ahead of GitHub's curated set.)
- **Current path #2 — Copilot CLI plugins:** distributed via git-repo "plugin marketplaces" using a `marketplace.json` in `.github/plugin/` (also reads `.claude-plugin/`). Default marketplaces include `copilot-plugins` and `awesome-copilot`. Decentralized; no central review. Docs: https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/plugins-marketplace
- **Official GitHub plugins collection:** https://github.com/github/copilot-plugins (accepts contributions via PR).
- Reach: Satya Nadella on Microsoft's July 30, 2025 FY25 Q4 earnings call confirmed Copilot "surpassed 20 million all-time users" (up from 15M in April 2025); a GitHub spokesperson told TechCrunch the figure is total ever-used, and Microsoft reported "90% of Fortune 100 companies now use GitHub Copilot."

**OpenAI Codex CLI**
- What it is: Codex CLI supports Skills (`SKILL.md` + optional `agents/openai.yaml`), MCP servers (configured in `~/.codex/config.toml` or via `codex mcp`), and — newer — Plugins with marketplace CLI commands (`codex plugin marketplace add` from Git/local sources; added ~v0.131, May 2026). Codex can also read `.claude-plugin/` layouts, so a single repo can serve both Claude Code and Codex.
- Distribution: no central OpenAI-run marketplace; distribution is via Git repos (your own plugin marketplace) and via MCP (config-based) + cross-agent skill installers (`npx skills add`). AGENTS.md is the cross-tool instruction standard.
- URLs: https://developers.openai.com/codex/skills • https://developers.openai.com/codex/cli/reference

**Cursor**
- In-app MCP marketplace/directory (cursor.directory/mcp). One-click install via `~/.cursor/mcp.json`. Submit via their GitHub/website.
- URL: https://cursor.directory/mcp

**Windsurf (Cascade)**
- In-app MCP Marketplace (accessible from the Cascade panel's MCP icon). Official servers show a blue checkmark. Supports one-click install deeplinks (`windsurf://windsurf-mcp-registry?serverName=…`).
- URL: https://docs.windsurf.com/windsurf/cascade/mcp

**Cline MCP Marketplace**
- What it is: Official curated, one-click-install marketplace for Cline (cline.bot advertises "Trusted by 8M+ developers"; 62.8k GitHub stars).
- How to submit: open an issue in `cline/mcp-marketplace` with a GitHub repo URL, a 400×400 PNG logo, and a reason for addition; confirm you tested that Cline can set it up from your README/`llms-install.md`. Per the repo README, review "evaluates: Community Adoption… through GitHub engagement metrics" and "Developer Credibility," with extra scrutiny for finance/crypto; the team aims to review submissions within a couple of days.
- URL: https://github.com/cline/mcp-marketplace

**Continue.dev Hub**
- Hub of models, rules, prompts, docs, MCP servers and other "building blocks." MCP via `.continue/mcpServers/`.
- URL: https://hub.continue.dev (docs: https://docs.continue.dev/customize/deep-dives/mcp)

**VS Code Marketplace & Open VSX**
- If you ship an editor extension (or an extension that bundles/installs an MCP server), publish to both: `vsce publish` (VS Code Marketplace) and `ovsx publish` (Open VSX, required for VS Code forks like Cursor, Windsurf, VSCodium, Gitpod). VS Code also has a native MCP gallery (search `@mcp`) and one-click `mcp.json` install.
- URLs: https://marketplace.visualstudio.com • https://open-vsx.org • MCP dev guide: https://code.visualstudio.com/api/extension-guides/ai/mcp

### 2. Third-party MCP & AI-tool marketplaces/directories

**Highest-leverage four (the consensus 2026 set): mcp.so, Smithery, Glama, and punkpeye/awesome-mcp-servers.** Beyond these, returns diminish because smaller directories share indexes.

- **mcp.so** — Largest aggregator (~21,800+ servers). Submit via the "Submit" button / their GitHub issues. URL: https://mcp.so
- **Smithery (smithery.ai)** — Distribution channel that runs/hosts servers with managed OAuth; install is `smithery mcp add`. Publish via CLI: `smithery mcp publish <url|bundle.mcpb> -n <org/server>`, or submit a manifest (name, description, tools, auth method, working URL/npm package). Also runs a Skills Registry. URL: https://smithery.ai (CLI: https://github.com/smithery-ai/cli)
- **Glama (glama.ai/mcp)** — 31,000+ servers; auto-indexes open-source MCP servers from GitHub (submit a repo; claim your listing for the admin panel). Provides quality scores, security audits, in-browser inspector, tool-level indexing. URL: https://glama.ai/mcp/servers
- **PulseMCP (pulsemcp.com)** — 16,800+ servers; run by MCP Steering Committee members; tracks weekly visitor estimates; publishes the influential "Agentic Loop" newsletter. Submit via the "Submit" button in the nav bar. Auto-ingests from the official registry within ~a week. URL: https://www.pulsemcp.com
- **mcpservers.org** — The web front-end for punkpeye/awesome-mcp-servers; has a submit page. URL: https://mcpservers.org/submit
- **MCP Market / MCP Server Finder / MCP Hunt / MCP Server Hub / mcp.directory / mcpserverdirectory.org** — Secondary directories; mostly form-based submissions. MCP Hunt is "Product Hunt meets Reddit for MCP" (upvotes/momentum). MCP Server Finder targets enterprise.
- **Composio** — 500+/1000+ app integrations exposed to agents; relevant if you want your tool reachable via Composio's tool-router. URL: https://composio.dev
- **Pipedream / Zapier MCP** — generate MCP servers across thousands of apps; relevant for integration-style tools.

**How to submit (universal prep):** prepare one metadata block — name, one-line capability description, transport type (stdio / Streamable HTTP), auth method (none / API key / OAuth), tool list, homepage, repository, license, and an example config snippet — then paste it into each form/PR.

### 3. "Awesome" lists / curated GitHub repos

- **punkpeye/awesome-mcp-servers** — The canonical MCP awesome list (88.6k stars, 11.1k forks as of mid-2026; 7,235 commits). Its README links directly to glama.ai/mcp/servers. Contribute via PR (fork → branch → edit README.md, one server per line, correct category, alphabetical) or via an Issue using their submission template. Note the automated "Check Glama Link" workflow — a Glama listing materially helps your PR merge. URL: https://github.com/punkpeye/awesome-mcp-servers
- **hesreallyhim/awesome-claude-code** — The leading Claude Code awesome list (skills, hooks, slash-commands, agents, plugins). Submit via an Issue using the "[Resource]" template (it auto-validates), or use `make add-resource` / `python scripts/add_resource.py` to add to `THE_RESOURCES_TABLE.csv` (never edit README directly). Requirements: repo public >1 week, working links, no other open issues. URL: https://github.com/hesreallyhim/awesome-claude-code
- **Other Claude/skills lists worth a PR:** travisvn/awesome-claude-skills, ComposioHQ/awesome-claude-skills, ComposioHQ/awesome-claude-plugins, BehiSecc/awesome-claude-skills, jqueryscript/awesome-claude-code, rohitg00/awesome-claude-code-toolkit, GetBindu/awesome-claude-code-and-skills. Most accept PRs or Issues.
- **General:** the canonical "awesome" ecosystem (sindresorhus/awesome) and language-specific lists if relevant.
- Process norm: follow each repo's CONTRIBUTING.md exactly (format, alphabetical order, emoji index); these are curated and sloppy PRs get rejected.

### 4. General developer discovery / launch platforms

- **Hacker News "Show HN"** — Highest-ROI single launch for technical/dev tools. Front-page can drive thousands of qualified visitors in a day; unpredictable and the audience is brutally honest. Post with a clear "Show HN:" title, a real description, and be present in the comments. One-time.
- **Product Hunt** — Still valuable; diversify. Launch Tue–Thu; line up a maker comment, demo GIF, and supporters. AI-coding-agents is an active category.
- **Reddit** — r/ClaudeAI, r/ChatGPTCoding, r/LocalLLaMA, r/programming, r/commandline, r/SideProject, r/mcp. Frame as a story ("I built this to solve X"), not an ad; participate first; avoid bare links in 1M+ subs (auto-removed).
- **Dev.to / Hashnode** — Publish a launch/how-it-works article (Dev.to is developer-native and indexes well).
- **Lobsters** — Smaller, high-signal technical community (invite-based; tag appropriately).
- **IndieHackers ("Show IH")** — Supportive bootstrapper audience.
- **Product Hunt alternatives** — Uneed, MicroLaunch, Peerlist Launch, BetaList (early-stage). Layer smaller launches first to gather proof, then hit HN/Reddit.

### 5. Package registries (discoverability layer)

- **npm** — For `npx`-distributed servers/CLIs. Add keywords `mcp`, `modelcontextprotocol`, `mcp-server`, `claude`, plus your domain; set `bin`/`main` correctly; add `mcpName` to package.json for registry linkage. URL: https://www.npmjs.com
- **PyPI** — For `uvx`/pip servers; add `mcp-name:` to README; use clear classifiers/keywords. URL: https://pypi.org
- **Docker Hub / GHCR** — Add the `io.modelcontextprotocol.server.name` image label so the registry can verify ownership.
- **crates.io** — For Rust transports/CLIs.
- **Homebrew** — A formula/cask or a custom tap for CLI distribution (`brew tap`).
- Discoverability tips: consistent naming (`yourtool-mcp`), the same keywords everywhere, and a README that front-loads what the tool does and a copy-paste install/config snippet.

### 6. Social / content channels

- **Newsletters (get featured by shipping something genuinely new and emailing / a warm intro):**
  - **PulseMCP / "The Agentic Loop"** — the highest-signal MCP-specific channel; auto-features registry additions.
  - **Latent Space** (swyx; AI engineering; 200k+ across channels) — covers dev tools; accepts pitches via warm intro only, ~1 month lead time, no cold emails; "Write for us" option.
  - **TLDR AI** (1.25M+), **The Rundown AI** (2M+), **Ben's Bites** (builder-focused), **Smol AI / AINews** (swyx, daily Discord/X recap).
- **Discord/Slack:** the MCP community Discord (linked from modelcontextprotocol.io/community), Anthropic's Discord, Glama's Discord (for directory support), and tool-specific communities (Cline, Cursor, Continue).
- **X/Twitter:** post a demo clip; tag relevant maintainers; use hashtags/terms like #MCP, #ClaudeCode, #buildinpublic. The AI-dev community is very active on X.
- **LinkedIn / YouTube:** a short demo video doubles as content for Dev.to, Reddit, and X.

### 7. GitHub-native discoverability

- **Apply GitHub topics:** `mcp`, `mcp-server`, `model-context-protocol`, `claude-code`, `claude-code-plugin`, `claude-code-skills`, `claude-skills`, `copilot`, `codex`, `cursor`, `windsurf`, `cline`, `ai-agents`, `agent-skills`, `llm-tools`, plus your domain. Topics feed GitHub Explore and search ranking.
- **README:** front-load the value proposition, an install/config snippet, and badges (build status, npm/PyPI version, license, stars). Repos with strong READMEs, topics, a homepage URL, license, releases/CHANGELOG, and recent activity rank higher and are more "AI-citable."
- **GitHub Code Search-based auto-discovery:** some Claude plugin indexers (e.g., ClaudePluginHub) auto-discover repos with `.claude-plugin/plugin.json` via GitHub Code Search every couple of hours — but indexing can take days, so direct submission is faster.
- **Trending strategy:** a coordinated launch-day spike (HN + Reddit + Product Hunt + newsletter) concentrates stars and can land you on GitHub Trending for your language/topic, which itself drives a secondary wave.

## Recommendations (prioritized, sequenced launch checklist)

**Phase 0 — Prep (before any announcement; 1–2 weeks lead time)**
1. Decide packaging: if at all possible, expose an **MCP server** (it's the universal substrate) in addition to your native format (Claude Code plugin, skill, slash command).
2. Publish the package to **npm and/or PyPI** (and Docker/GHCR if relevant) with proper keywords, `mcpName`/`mcp-name` markers, and a copy-paste config snippet in the README.
3. Polish the **GitHub repo**: topics, README with badges + install snippet, license, a demo GIF/video, CHANGELOG. Run `claude plugin validate` / `mcpb validate` as applicable.

**Phase 1 — Registries (one-time, but wire into CI/CD; do first — adoption compounds here)**
4. **Publish to the official MCP Registry** via `mcp-publisher` (GitHub OIDC in CI so every release re-publishes). This seeds GitHub's MCP Registry, PulseMCP, and others automatically.
5. Submit to your **native first-party home(s):** Anthropic `claude-plugins-official` + Connectors Directory (if Claude Code/Claude), Cline marketplace, Cursor directory, Windsurf marketplace, VS Code/Open VSX (if an editor extension).
6. Submit to the **third-party big four:** Smithery (publish via CLI), Glama (submit repo), mcp.so (submit), PulseMCP (submit).

**Phase 2 — Curated lists (one-time; do after you have a Glama listing)**
7. PR/Issue to **punkpeye/awesome-mcp-servers** (ensure the Glama link exists first), **hesreallyhim/awesome-claude-code** (Issue template), and the relevant Composio/skills awesome lists.

**Phase 3 — Coordinated launch wave (one day; Tue–Thu)**
8. Morning: **Show HN** + **Product Hunt** simultaneously.
9. Same day: post to **r/ClaudeAI / r/ChatGPTCoding / r/mcp / r/LocalLLaMA** (story framing), publish a **Dev.to** article, and post a demo on **X/LinkedIn**.
10. Notify **newsletters** (PulseMCP auto-picks up registry adds; pitch Latent Space/TLDR with ~1 month lead time for bigger features) and drop a note in the **MCP / Anthropic / tool-specific Discords**.

**Phase 4 — Ongoing**
11. Keep registries fresh via CI/CD on every release; respond to issues; periodically re-share new capabilities; pursue newsletter features as you ship notable updates.

**Benchmarks that change the plan:**
- If you're **only Claude Code** (no server), skip the MCP registry and prioritize `claude-plugins-official` + awesome-claude-code + the in-product Plugins directory.
- If you're **terminal/Codex/Copilot-CLI focused**, prioritize a git-repo plugin marketplace (`marketplace.json`) + MCP registry; the GitHub MCP Registry is your discovery surface.
- If early traction is low (e.g., <50 stars after launch), focus on one excellent directory + one strong Show HN/Reddit story rather than spraying low-signal directories (dead links there hurt trust).

## Caveats
- **Fast-moving ecosystem:** the MCP Registry was in preview (v0.1 API freeze Oct 2025) with no durability guarantees; GitHub's MCP Registry auto-propagation from the OSS registry was still maturing in late 2025 (the OSS registry's ~2,000 entries by Nov 2025 far outpaced GitHub's curated set). Verify current behavior before relying on auto-propagation.
- **Copilot Extensions deprecation is confirmed** (Nov 10, 2025) — any older guide telling you to "list a Copilot Extension in the GitHub Marketplace" is obsolete.
- **Server counts and audience figures vary by source and date** (e.g., mcp.so ~20k–22k, Glama ~31k, PulseMCP ~16k); treat them as directional. Copilot's "20M all-time users" (July 2025 earnings call) is the officially-sourced figure; larger paid-subscriber numbers from SEO blogs are unverified.
- **Curated venues can reject** for quality/security (Cline, Anthropic Connectors, awesome-lists). Have docs, a privacy policy (for connectors), and a working install path ready.
- **Launch-platform norms are strict** — overt self-promotion gets removed/downvoted on Reddit and HN; lead with value and authenticity.