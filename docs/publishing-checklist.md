# Publishing checklist

Where to list debt-ops for visibility. Distilled from [ai-plugin-visibility.md](./ai-plugin-visibility.md)
plus fresh verification (June 2026) of each surface. debt-ops has **no MCP server**
(hooks are the product; MCP can't intercept at write-time), so the entire MCP-registry
track from the research doc is intentionally skipped.

## Now — repo polish + zero-gate submissions

- [x] **GitHub metadata**: homepage set to the skills.sh listing; topics `codex`,
      `copilot-cli`, `codex-plugins`, `agent-skills`, `claude-skills`, `ai-agents` added
      (crawlers like ClaudePluginHub, claudemarketplaces.com, and GuildSkills index by
      topic/manifest). *(done 2026-06-06)*
- [x] **Validate**: `claude plugin validate ./claude-code --strict` — passes. Anthropic's
      review pipeline runs the same check. *(done 2026-06-06)*
- [x] **SKILL.md descriptions**: audited — no changes. All four already carry the
      high-value terms ("tech-debt registry", "TODO/FIXME/HACK", "debt health",
      "paydown"), and the wording doubles as agent-trigger logic + the disciplines
      contract, so keyword tweaks would risk trigger precision for marginal search gain.
      *(done 2026-06-06)*
- [ ] **Anthropic community marketplace**: submit at <https://claude.ai/settings/plugins/submit>.
      Lands in `@claude-community` (default-registered in every Claude Code install,
      browsable at <https://claude.com/plugins>). SHA-pinned; pin auto-bumps on push.
      Note: the *official* directory has no application path — don't chase it.
- [ ] **github/awesome-copilot external plugin**: open an issue with the external-plugin
      form at <https://github.com/github/awesome-copilot>. 34.5k★ and a **default-registered
      Copilot CLI marketplace** (`copilot plugin install debt-ops@awesome-copilot`).
      Needs an immutable source locator — use the latest release-please tag (e.g. `debt-ops-v0.8.1`).
- [ ] **ClaudePluginHub**: submit the repo URL at <https://www.claudepluginhub.com/tools/submit-plugin>,
      then claim the listing (verified badge + install-count README badge).
- [ ] **Codex community lists** (only Codex discovery surfaces that exist; OpenAI's
      directory is "coming soon" with no open submission):
  - [ ] PR to <https://github.com/hashgraph-online/awesome-codex-plugins>
  - [ ] PR to <https://github.com/RoggeOhta/awesome-codex-cli>
- [ ] **jqueryscript/awesome-claude-code**: PR to its "Claude Plugins" section
      (<https://github.com/jqueryscript/awesome-claude-code>, active, no gates).

Skipped on purpose: `github/copilot-plugins` (staff-gated, no community merges ever) and
the ComposioHQ awesome lists (they require *vendoring a copy* of the skills into their
repo — conflicts with our single-source-repo model, see ADR 0014's spirit).

## Later — launch wave (one Tue–Thu, after the listings above exist)

HN data is unambiguous: "Claude Code plugin"-framed Show HNs flop (2–9 pts);
problem/outcome framing wins (100–500 pts). Our trust asset: stdlib-only, fully local,
no network calls — the one plugin that got torched on HN (Peek, Mar 2026) died for
undisclosed server calls. Disclose data flow up front.

- [ ] **Show HN** — title around the problem (e.g. "Catch the tech debt your AI agent
      writes, at write-time"), link the repo, first comment explains the hook mechanism
      and states: local-only, stdlib Python, MIT, no telemetry.
- [ ] **Reddit, same day**:
  - r/ClaudeAI — promo explicitly *encouraged* for free tools: say it's free, pick a
    flair, no referral links.
  - r/codex — lead with the Codex adapter specifically (relevance rule).
  - r/ChatGPTCoding — frame as "sharing work," flair required.
- [ ] **Dev.to article** + **X/LinkedIn demo clip** (reuse `demo/debt-ops.gif`).
- [ ] **Product Hunt**: deprioritized — 2026 PH is saturated; for free OSS it's a
      backlink, not traction. Optional follow-on.

## Later — traction-gated lists (after ~10–50 stars)

These reject brand-new/low-star repos, so they come after the launch wave.
**Human-submitted only** — two of them explicitly ban AI-generated/AI-submitted
contributions:

- [ ] **VoltAgent/awesome-agent-skills** (24.4k★) — PR, one line, ≤10-word description;
      requires "real community usage."
- [ ] **travisvn/awesome-claude-skills** (13.2k★) — PR; requires ~10+ repo stars;
      **bans AI-generated/AI-submitted PRs**.
- [ ] **hesreallyhim/awesome-claude-code** (45.8k★) — issue form, **must be submitted by
      a human via the github.com UI**; repo must be >1 week public (✓). ~400-issue
      backlog and mid-reorg — file and forget.

## Ongoing

- skills.sh and claude.com/plugins rank by installs — every post/listing leads with the
  one-line install command. Already auto-indexed at
  <https://www.skills.sh/bcanfield/agentic-tech-debt>; nothing to submit.
- awesome-copilot tracks release tags; community-marketplace pin auto-bumps. No manual
  re-publishing needed.
- Watch for OpenAI's self-serve Codex Plugin Directory submission opening
  (<https://developers.openai.com/codex/plugins> — "coming soon" as of June 2026).
