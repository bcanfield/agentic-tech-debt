# Docs Index

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
  plugin with zero install footprint. Shipped as two self-contained
  adapters — [`claude-code/`](../claude-code) and [`codex/`](../codex)
  (the Codex adapter mirrors the Claude mapping onto Codex primitives;
  see ADRs 0011–0012).
- **[`claude-code-plugins.md`](./claude-code-plugins.md)**: reference
  guide for Claude Code plugin internals: manifest, skills, agents,
  hooks, MCP, LSP, monitors, marketplaces. Used while designing the
  plugin.
- **[`telemetry-collection-plan.md`](./telemetry-collection-plan.md)**:
  what usage data is worth collecting (to steer the roadmap and fuel
  content like a "debt of the week") and how to collect it without
  breaking the privacy promise — local by default, sharing via explicit
  opt-in donation. See [ADR 0020](./adr/0020-local-only-opt-in-telemetry.md).
- **[`adr/`](./adr/)**: Architecture Decision Records — short notes on
  the choices that shape how the plugin behaves. See
  [`adr/README.md`](./adr/README.md) for the format.

## Reading order

Start with `tech-debt-management.md` for grounding, read
`tech-debt-pillars.md` for the principles the plugin must satisfy,
then `tech-debt-plugin-plan.md` for what v1 builds.
