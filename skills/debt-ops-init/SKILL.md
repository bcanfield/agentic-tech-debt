---
name: debt-ops-init
description: Write or refresh a "Tech debt operations" section in the project's AGENTS.md so the team shares one source of truth for debt-ops disciplines. Run ONLY when the user explicitly asks to set up, install, or initialize debt-ops disciplines — never auto-invoke. Idempotent; only the managed section changes, other sections are untouched.
---

# debt-ops-init

Write or update a `## Tech debt operations` section in the project's agent charter.
Idempotent — only the managed section changes.

**Run only on explicit user request** ("set up debt-ops", "init debt-ops",
"write the disciplines"). Do not invoke this as part of normal work. (Tools with a
debt-ops hook adapter inject these disciplines per-session automatically; this skill
is the persistence step for everyone else.)

## Why this matters more on skills-only tools

Without a hook adapter there is no per-edit enforcement and no automatic capture.
The charter is the *only* place the disciplines live, so the agent self-applies them.
That's "vibes," not a tripwire — be honest with the user that the persistent charter
is the substitute for, not the equal of, the hook-driven write-time loop.

## 1. Pick the charter file

Use `AGENTS.md` at the repo root — the cross-tool charter most agents read. If the
project clearly standardizes on a different file your agent auto-loads
(`GEMINI.md`, `.github/copilot-instructions.md`, `CLAUDE.md`), use that instead and
tell the user which you picked.

## 2. Read any cached quality commands (optional)

If a hook adapter previously ran in this repo, it cached the project's quality
commands. Include them if present; otherwise leave the placeholder.

```bash
REPO_HASH=$(python3 -c "import hashlib,subprocess;t=subprocess.run(['git','rev-parse','--show-toplevel'],capture_output=True,text=True).stdout.strip();print(hashlib.sha1(t.encode()).hexdigest()[:12] if t else '')")
CACHE_DIR="${DEBT_OPS_CACHE:-$HOME/.cache/debt-ops}/cache/$REPO_HASH"
[ -f "$CACHE_DIR/feedback.list" ] && cat "$CACHE_DIR/feedback.list"
ADR_DIR=$( [ -s "$CACHE_DIR/adr-dir" ] && cat "$CACHE_DIR/adr-dir" || echo "docs/adr" )
REGISTRY_DIR=$( [ -s "$CACHE_DIR/registry-dir" ] && cat "$CACHE_DIR/registry-dir" || echo "docs/debt" )
echo "adr-dir: $ADR_DIR"
echo "registry-dir: $REGISTRY_DIR"
```

If no commands are cached, detect the project's lint/type/test commands by scanning
its manifests (`package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, `Makefile`,
…). Prefer commands that take a changed-file argument and run in a few seconds.

## 3. Compose the section (template)

Substitute `{{ADR_DIR}}`, `{{REGISTRY_DIR}}`, and `{{COMMANDS}}` (the cached or
detected commands, one per line; leave a `# add your lint/type/test commands here`
placeholder if none found).

```markdown
## Tech debt operations

<!-- this section is auto-managed by the debt-ops agent skill; safe to edit, run debt-ops-init to regenerate -->

### Disciplines

1. The test for debt: would a future reader ask "why this way?" If yes, register via the `debt-ops-add` skill immediately — no prompt. This is judgment, not a marker scan: a `TODO`/`FIXME`/`HACK`/`XXX` is the obvious case, but an unmade decision, a stub, a loosened type, or a default picked "for now" all count even with no marker in the diff. Use `payoff_trigger: unknown` if unsure. Announce: `+1 entry: <slug> (drop?)`. Over-register freely; the developer drops with "drop it".

2. When making an architecturally significant change — a data model, public interface, security boundary, release pipeline, or a dep-manifest change that is a major-version bump or a *new* top-level dependency — draft an ADR under `{{ADR_DIR}}/` in Nygard format: a `# NNNN — Title` heading, `**Date:**` and `**Status:**` lines, then Context, Decision, Consequences, Alternatives, Payoff trigger. Create the directory if needed. Only draft an ADR when there are two credible alternatives; if you cannot list two, it is a comment, not an ADR. An ADR with a payoff trigger *is* deliberate debt — when you write one, also use `debt-ops-add` so the registry entry mirrors the ADR.

3. Read entries under `{{REGISTRY_DIR}}/` before changing files they reference.

### Quality checks (self-applied)

After editing code, run these and fix failures before moving on. Without a debt-ops hook adapter these are not enforced automatically — you, the agent, run them.

{{COMMANDS}}
```

## 4. Apply

- **If the charter file doesn't exist:** create it with the section above as the
  entire file.
- **If it has a `## Tech debt operations` section:** replace exactly that section —
  from the heading through (but not including) the next `## ` heading, or EOF if
  none. Leave every other byte unchanged.
- **If it exists without the section:** append the section after the last line, with
  one blank line between.

## 5. Announce

`charter updated: <file> — disciplines + N quality commands` (N = non-comment,
non-blank lines in the quality-checks block; 0 if placeholder).

## Don't

- Don't auto-invoke. Only on explicit user request.
- Don't touch any byte outside the `## Tech debt operations` section.
- Don't claim the charter gives deterministic enforcement — it doesn't without a
  hook adapter. Say so.
