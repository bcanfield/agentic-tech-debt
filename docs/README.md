# debt

Working notes for an evidence-based, agentic tech debt management
system, delivered as a Claude Code plugin.

## Documents

- **[`tech-debt-management.md`](./tech-debt-management.md)**: research
  synthesis. Three decades of debt research and 2024–2026 practitioner
  data. Definitions, frameworks, costs, the impact of agentic coding,
  and the recommended Continuous Tech Debt Operations loop.
- **[`tech-debt-pillars.md`](./tech-debt-pillars.md)**: nine
  tool-agnostic pillars derived from that research. Each pillar names
  what it does, what the system must expose, when it fires, who it
  affects, and the failure mode without it.
- **[`tech-debt-plugin-plan.md`](./tech-debt-plugin-plan.md)**:
  `debt-ops` v1 spec. Maps the pillars to a concrete Claude Code
  plugin: two skills, two hooks, two scripts, zero install footprint.
- **[`claude-code-plugins.md`](./claude-code-plugins.md)**: reference
  guide for Claude Code plugin internals: manifest, skills, agents,
  hooks, MCP, LSP, monitors, marketplaces. Used while designing the
  plugin.

## Reading order

Start with `tech-debt-management.md` for grounding, read
`tech-debt-pillars.md` for the principles the plugin must satisfy,
then `tech-debt-plugin-plan.md` for what v1 builds.
