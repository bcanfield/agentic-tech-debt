#!/usr/bin/env bash
# debt-ops SessionStart hook.
#
# Injects the four debt-ops disciplines into Claude's context, plus the
# repo's quality commands (for PostToolUse feedback).
#
# Command-source precedence:
#   1. <!-- debt-ops:feedback --> block in AGENTS.md or CLAUDE.md (charter
#      wins when /debt-ops:init has been run).
#   2. ${CLAUDE_PLUGIN_DATA}/feedback.list (warm cache from a prior session).
#   3. Neither: ask Claude to detect commands and write the cache. The first
#      session pays this cost once.
#
# Output: JSON on stdout via the SessionStart hookSpecificOutput.additionalContext
# field. Diagnostics go to stderr so they don't pollute the model's context.

set -u
umask 077

DATA_DIR="${CLAUDE_PLUGIN_DATA:-}"
CACHE_FILE=""
if [[ -n "${DATA_DIR}" ]]; then
  mkdir -p "${DATA_DIR}" 2>/dev/null || true
  CACHE_FILE="${DATA_DIR}/feedback.list"
fi

# Locate the charter (AGENTS.md or CLAUDE.md) in the current working directory.
CHARTER=""
for candidate in AGENTS.md CLAUDE.md; do
  if [[ -f "${candidate}" ]]; then
    CHARTER="${candidate}"
    break
  fi
done

# Pull commands out of the charter's <!-- debt-ops:feedback --> block, if any.
charter_commands() {
  local file="$1"
  awk '
    /<!--[[:space:]]*debt-ops:feedback[[:space:]]*-->/ { in_block = 1; next }
    /<!--[[:space:]]*\/debt-ops:feedback[[:space:]]*-->/ { in_block = 0; next }
    in_block { print }
  ' "${file}" | sed -E 's/^[[:space:]]*[-*][[:space:]]+//' \
              | sed -E 's/^[[:space:]]*```.*$//' \
              | sed -E 's/^[[:space:]]+|[[:space:]]+$//g' \
              | grep -Ev '^$|^#'
}

CMDS=""
SOURCE=""

if [[ -n "${CHARTER}" ]]; then
  if grep -qE '<!--[[:space:]]*debt-ops:feedback[[:space:]]*-->' "${CHARTER}" 2>/dev/null; then
    CMDS="$(charter_commands "${CHARTER}")"
    if [[ -n "${CMDS}" ]]; then
      SOURCE="charter:${CHARTER}"
    fi
  fi
fi

if [[ -z "${CMDS}" && -n "${CACHE_FILE}" && -s "${CACHE_FILE}" ]]; then
  CMDS="$(grep -Ev '^[[:space:]]*$|^[[:space:]]*#' "${CACHE_FILE}")"
  if [[ -n "${CMDS}" ]]; then
    SOURCE="cache:${CACHE_FILE}"
  fi
fi

# Build the additional-context payload.
DISCIPLINES=$(cat <<'DISCIPLINES_EOF'
## Tech debt operations (debt-ops plugin)

Four disciplines apply to this session. If the project's AGENTS.md or CLAUDE.md
already has a `## Tech debt operations` section, that section takes precedence.

1. **Auto-register debt.** When you write a `TODO`, `FIXME`, `HACK`, or `XXX`
   marker that's real debt (a known shortcut, an incomplete case, a fragile
   assumption), invoke `/debt-ops:add` immediately to register it. No
   permission prompt; just do it and announce briefly. Use
   `payoff_trigger: unknown` if you can't determine it. Trivial markers (style
   nits, naming preferences) don't earn an entry; use judgment.

2. **Draft ADRs for architectural changes.** When making an architecturally
   significant change (data model, public interface, dependency manifest,
   security boundary, release pipeline), draft an ADR under `doc/adr/` in
   Nygard format. Create the directory if needed. The ADR must contain:
     - **Context**: forces in play, constraints.
     - **Decision**: what we're doing, in active voice.
     - **Consequences**: what becomes easier and harder.
     - **Alternatives**: options considered and why rejected.
     - **Payoff trigger**: when we'd revisit (`unknown` is acceptable).
   File name: `NNNN-kebab-title.md` with a zero-padded sequence.

3. **Read the registry first.** Before changing files referenced by entries
   under `debt/registry/`, read those entries. They describe known shortcuts
   and fragile assumptions you should avoid stepping on.

4. **Refer by content, not ID.** In conversation, refer to debt entries and
   ADRs by what they're about ("the cancelled-promotion entry", "the
   pricing-event-trait ADR"), not by numeric ID. IDs are tooling
   cross-references, like commit SHAs.
DISCIPLINES_EOF
)

if [[ -n "${CMDS}" ]]; then
  CMDS_BLOCK=$(printf '%s\n' "${CMDS}")
  FEEDBACK_SECTION=$(cat <<FEEDBACK_EOF

## Quality commands for this repo

Source: ${SOURCE}

After every Write/Edit/MultiEdit, the debt-ops PostToolUse hook runs these
commands in parallel under a 3 s budget and returns structured pass/fail JSON.
You don't need to run them manually; surface failures only when the hook
reports them.

\`\`\`
${CMDS_BLOCK}
\`\`\`
FEEDBACK_EOF
)
else
  FEEDBACK_SECTION=$(cat <<'DETECT_EOF'

## Detect quality commands (one-time, this repo)

No quality commands are cached for this repo yet. Before the next edit, scan
the project for the commands developers run to type-check, lint, and test
this codebase. Look at:

  - `package.json` scripts (`build`, `lint`, `typecheck`, `test`)
  - `Cargo.toml` / `cargo` (`cargo check`, `cargo clippy --no-deps -- -D warnings`, `cargo test`)
  - `pyproject.toml` / `setup.cfg` / `tox.ini` (`ruff`, `mypy`, `pytest`)
  - `Makefile` targets (`make lint`, `make test`)
  - `go.mod` (`go vet ./...`, `go test ./...`)
  - `Gemfile`, `mix.exs`, `pom.xml`, `build.gradle`, etc.

Pick the small, fast set a developer would run before pushing — typically
type-check + lint + a fast test pass. Each command must be:

  - Non-interactive (no prompts).
  - Self-contained (no positional args).
  - Idempotent (safe to run repeatedly).
  - Quiet on success (we'll only surface failures).

Write one command per line to `${CLAUDE_PLUGIN_DATA}/feedback.list` (no
quotes, no `&&` chains; one independent command per line). Subsequent sessions
will read this cache instantly. Do this silently before continuing the user's
work.
DETECT_EOF
)
fi

PAYLOAD="${DISCIPLINES}
${FEEDBACK_SECTION}"

# Emit JSON. Use python3 for safe escaping if available; fall back to a
# minimal hand-rolled escaper.
emit_json() {
  local text="$1"
  if command -v python3 >/dev/null 2>&1; then
    python3 - <<'PY' "${text}"
import json, sys
print(json.dumps({
    "hookSpecificOutput": {
        "hookEventName": "SessionStart",
        "additionalContext": sys.argv[1],
    }
}))
PY
  else
    local escaped
    escaped=$(printf '%s' "${text}" \
      | sed -e 's/\\/\\\\/g' -e 's/"/\\"/g' \
      | awk 'BEGIN{ORS="\\n"}{print}')
    printf '{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"%s"}}\n' "${escaped}"
  fi
}

emit_json "${PAYLOAD}"
exit 0
