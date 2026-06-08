# Security Policy

## Reporting a vulnerability

Please report security issues privately via GitHub's
[private vulnerability reporting](https://github.com/bcanfield/agentic-tech-debt/security/advisories/new)
rather than opening a public issue. We aim to acknowledge reports within 5 business days.

## Scope

debt-ops is a local-only tool. Its hooks and skills are stdlib-Python only, make no
network calls, and run entirely in your repo. The most relevant security surfaces are:

- **Hook scripts** (`hooks/`) — invoked by the agent on each edit; they read the repo
  and write to a local cache, nothing else.
- **GitHub Actions** (`.github/workflows/`) — third-party actions are pinned to commit
  SHAs and run with least-privilege permissions.

If you find anything that lets the plugin reach the network, escalate privileges, or
execute untrusted code, that's in scope — please report it.
