# agentic-tech-debt

**Tech debt operations for AI coding agents** — a Claude Code plugin that surfaces the debt agents defer, drafts ADRs for the choices they make, and runs your project's own quality checks on every edit. Distilled from three decades of debt research (Cunningham, Fowler, Kruchten, DORA, Beck, GitClear) into a discipline an agent can hold without breaking flow.

Non-blocking. Evidence-based. Plays well with other plugins. Two skills, two hooks, two scripts, zero install footprint.

## Install

```bash
/plugin marketplace add bcanfield/agentic-tech-debt
/plugin install debt-ops
```

Requires Claude Code v2.1.121+ and a git repository.

## What's here

- **[`claude-code/`](./claude-code)** — the `debt-ops` plugin. See its [README](./claude-code/README.md) for what ships in v1 and what's deferred.
- **[`docs/`](./docs)** — research synthesis, the nine tool-agnostic pillars, and the v1 plugin spec.

Future adapters for other agents (Cursor, Aider) slot in as siblings to `claude-code/`.

## License

[MIT](./LICENSE).
