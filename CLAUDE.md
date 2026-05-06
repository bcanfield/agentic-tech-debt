# Project Rules

- **Stay in scope.** Do exactly what was asked. No drive-by refactors or "while I'm here" cleanups — flag them and wait for confirmation.
- **Don't over-engineer.** Simplest thing that works. No speculative abstractions, defensive code for impossible cases, or new dependencies without a concrete reason.
- **Use current docs.** For any library, framework, or API, fetch docs via the context7 MCP server before answering — even for things you "know." Match the version in this project, not the latest release. Also - try to fetch examples from github requently (i.e. an Anthropic-published Claude Code plugin to use as an example)
- **Ask when unsure.** One focused question beats guessing or expanding scope.
- **Be refreshingly concise.** Nobody likes overly wordy AI slop. Speak and comment like a co-worker.
- **Python over Bash for plugin scripts.** Stdlib `json`, `re`, and `subprocess.run(..., timeout=...)` beat hand-rolled JSON escaping, a `jq` dependency, and the BSD/GNU `timeout` portability dance — and run on Windows without WSL.
