# Tests

A deterministic harness that proves the product works across every surface we
ship. Stdlib `unittest` only (Python 3.9+, the version the hooks target) — no
extra deps, runs on Windows.

```bash
python3 -m unittest discover -s tests -v      # everything
python3 -m unittest discover -s tests -p "test_hooks.py" -v   # one file
SKIP_SKILLS_CLI=1 python3 -m unittest discover -s tests       # skip the npx test
```

## What it covers

| File | Layer | What it guards |
|---|---|---|
| `test_hooks.py` | hook I/O contract | Spawns the real `feedback`/`session-start`/`stop` scripts for **all three adapters** with host-shaped payloads; asserts the output envelope (`hookSpecificOutput` for claude/codex, `modifiedResult` for copilot; `{"decision":"block"}` for stop) and the `session`/`edit`/`feedback` cache metrics. Includes a named regression for the ADR 0019 Copilot cwd fix. |
| `test_static.py` | structure | Manifests parse; every hook command resolves to a real script under its plugin root; every `SKILL.md` has `name`+`description`; the `metadata.internal` dedup flag is on **exactly** the four claude-code skills (ADR 0018), nowhere else. |
| `test_skills_cli.py` | live registry | `npx skills@1.5.10 add . --list` offers **4** portable skills by default and **8** with `INSTALL_INTERNAL_SKILLS=1` — proving the dedup flag is load-bearing. Self-skips without `npx`. |

`helpers.py` holds the per-adapter payload builders and the spawn helper. The
adapter deltas it encodes (cache env var, which hooks read stdin, copilot's
non-repo cwd) mirror the parity map in the root `CLAUDE.md`.

## What it deliberately does NOT cover

Live, host-driven runs (does Copilot/Codex/Claude actually *invoke* the hooks)
need the real CLIs, auth, and model calls — unsuitable for CI. Those are the
manual P0 smoke checks; the harness instead spawns the same scripts with the
exact payloads each host was observed to send, so a contract break is caught
without a host. When a host changes its payload shape, update `helpers.py`.
