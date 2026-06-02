# Privacy Policy

_Last updated: June 2, 2026_

debt-ops is a local plugin for [Claude Code](https://code.claude.com/docs) and [Codex](https://developers.openai.com/codex). It runs entirely on your machine. This policy explains what it does and does not do with your data.

## The short version

debt-ops collects nothing. There is no telemetry, no analytics, no crash reporting, no account, and no network connection of any kind. Nothing is sent to the author or any third party. Every file it writes stays on your machine.

## What debt-ops writes, and where

debt-ops only reads and writes local files:

- **Debt entries** as Markdown in your repository's registry directory (default `docs/debt/`).
- **Architecture decision records** as Markdown in `docs/adr/`.
- **Operational data** in a local cache directory on your machine (a `metrics.jsonl` counting registrations and hook outcomes, a cached list of your quality commands, and the detected registry path). On Claude Code this lives under the plugin's data directory; on Codex it lives under `~/.cache/debt-ops` (override with `DEBT_OPS_CACHE`).
- **A debug log** (`debug.log`) in that cache directory, but only when you explicitly set `DEBT_OPS_DEBUG=1`. It is never written otherwise.

The debt entries and ADRs are yours: they are normal files in your repository, committed and shared only if and when you choose.

## Quality commands

debt-ops can run the linters, type-checkers, and tests you configure. These run locally as subprocesses, the same as if you ran them yourself. debt-ops does not transmit their output anywhere; it only reads the exit status to report pass or fail back to your agent.

## What debt-ops does not control

debt-ops runs inside a coding agent (Claude Code or Codex). That agent is what sends your code and prompts to a large language model. debt-ops does not make those calls and has no access to them. How your code is handled by the model is governed by the privacy policy of the agent you use:

- Anthropic (Claude Code): https://www.anthropic.com/legal/privacy
- OpenAI (Codex): https://openai.com/policies/privacy-policy

## Changes

If this policy ever changes, the update will be committed to this file in the repository, with a new "last updated" date.

## Contact

Questions: open an issue at https://github.com/bcanfield/agentic-tech-debt/issues or email brandincanfield@gmail.com.
