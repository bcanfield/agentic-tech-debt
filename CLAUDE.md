# Project Rules

- **Stay in scope.** Do exactly what was asked. No drive-by refactors or "while I'm here" cleanups — flag them and wait for confirmation.
- **Don't over-engineer.** Simplest thing that works. No speculative abstractions, defensive code for impossible cases, or new dependencies without a concrete reason.
- **Use current docs.** For any library, framework, or API, fetch docs via the context7 MCP server before answering — even for things you "know." Match the version in this project, not the latest release. Also - try to fetch examples from github requently (i.e. an Anthropic-published Claude Code plugin to use as an example)
- **Confront our research.** Try to see if you can ground decisions in our extensive research.
- **Ask when unsure.** One focused question beats guessing or expanding scope.
- **Be refreshingly concise.** Nobody likes overly wordy AI slop. Speak and comment like a co-worker.
- **Guide Claude with markdown, not orchestration.** Claude Code is smart and has the keys to the user's repo — skills should load research-backed principles and trust Claude's judgment, not script its every step. Reach for Python only when determinism demands it (timestamps, audits, atomic file ops, hook contracts) — never to make decisions a smart agent reading the repo can make better.
- **Python over Bash for plugin scripts.** Stdlib `json`, `re`, and `subprocess.run(..., timeout=...)` beat hand-rolled JSON escaping, a `jq` dependency, and the BSD/GNU `timeout` portability dance — and run on Windows without WSL.
- **Conventional commits.** Plugin version auto-bumps via release-please (config in `.github/`); use `feat:` / `fix:` / `feat!:` prefixes — anything else is ignored by the bumper. Don't hand-edit `version` in `plugin.json`.
- **We like humanlike, concise inline comments** For example, a single line above a function or code block very simply and concisely saying what the code is doing so that the code is easy for a human to understand
- **Record decisions as ADRs.** When we make a choice with two credible alternatives — a new convention, a tradeoff worth remembering — drop a short note in [`doc/adr/`](./doc/adr/) using the format in its [README](./doc/adr/README.md).
## Debugging

Set `DEBT_OPS_DEBUG=1` before launching Claude Code to log every PostToolUse fire and command result:

```bash
DEBT_OPS_DEBUG=1 claude
```

Each fire appends tab-separated lines to `<cache>/debug.log` — the exact path is printed in the SessionStart context block. Format:

```
2026-05-06T16:00:34Z	FIRE	changed=src/foo.ts	cmds=3
2026-05-06T16:00:34Z	PASS	0.01s	tsc --noEmit
2026-05-06T16:00:37Z	TIMEOUT	3.00s	pytest tests/
2026-05-06T16:00:37Z	FAIL	0.42s	eslint $CHANGED_FILES
```

Tail it in a separate terminal pane: `tail -f ~/.claude/plugins/data/debt-ops-agentic-tech-debt/cache/<repo-hash>/debug.log` (the exact path is printed in the SessionStart context block). With the env var unset (default), nothing is written.