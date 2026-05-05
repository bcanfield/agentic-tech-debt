#!/usr/bin/env bash
# debt-ops SessionStart hook.
#
# Injects the four debt-ops disciplines plus the repo's quality commands.
#
# Charter precedence (per tech-debt-plugin-plan.md):
#   - If the project's AGENTS.md or CLAUDE.md already has a
#     "## Tech debt operations" section (because /debt-ops:init has been run),
#     skip the disciplines inject. Claude Code loads the charter natively;
#     re-injecting would be noise.
#   - Same for the commands list: if the charter has a `<!-- debt-ops:feedback -->`
#     marker block, skip the commands inject.
#
# Command-source precedence (used by feedback.sh too):
#   1. Charter marker block.
#   2. ${CLAUDE_PLUGIN_DATA}/feedback.list (warm cache).
#   3. Neither: inject a one-time prompt asking Claude to detect and write
#      the cache.
#
# Output: SessionStart hookSpecificOutput.additionalContext on stdout.
# Diagnostics go to stderr so they don't pollute the model's context.

set -u -o pipefail
umask 077

DATA_DIR="${CLAUDE_PLUGIN_DATA:-}"
CACHE_FILE=""
if [[ -n "${DATA_DIR}" ]]; then
  mkdir -p "${DATA_DIR}" 2>/dev/null || true
  CACHE_FILE="${DATA_DIR}/feedback.list"
fi

# Locate the charter (AGENTS.md or CLAUDE.md) in the working directory.
CHARTER=""
for candidate in AGENTS.md CLAUDE.md; do
  if [[ -f "${candidate}" ]]; then
    CHARTER="${candidate}"
    break
  fi
done

# Charter has the disciplines section? Then skip the inject — Claude already
# sees it via native AGENTS.md/CLAUDE.md loading.
CHARTER_HAS_DISCIPLINES=0
if [[ -n "${CHARTER}" ]] && grep -qE '^##[[:space:]]+Tech[[:space:]]+debt[[:space:]]+operations\b' "${CHARTER}" 2>/dev/null; then
  CHARTER_HAS_DISCIPLINES=1
fi

# Pull commands from the charter's <!-- debt-ops:feedback --> block, if any.
charter_commands() {
  local file="$1"
  # The trailing grep can legitimately match nothing (empty marker block);
  # || true keeps pipefail from failing the caller in that case.
  awk '
    /<!--[[:space:]]*debt-ops:feedback[[:space:]]*-->/ { in_block = 1; next }
    /<!--[[:space:]]*\/debt-ops:feedback[[:space:]]*-->/ { in_block = 0; next }
    in_block { print }
  ' "${file}" | sed -E 's/^[[:space:]]*[-*][[:space:]]+//' \
              | sed -E 's/^[[:space:]]*```.*$//' \
              | sed -E 's/^[[:space:]]+|[[:space:]]+$//g' \
              | { grep -Ev '^$|^#' || true; }
}

CMDS=""
SOURCE=""
CMDS_FROM_CHARTER=0

if [[ -n "${CHARTER}" ]] && grep -qE '<!--[[:space:]]*debt-ops:feedback[[:space:]]*-->' "${CHARTER}" 2>/dev/null; then
  CMDS="$(charter_commands "${CHARTER}")"
  if [[ -n "${CMDS}" ]]; then
    SOURCE="charter:${CHARTER}"
    CMDS_FROM_CHARTER=1
  fi
fi

if [[ -z "${CMDS}" && -n "${CACHE_FILE}" && -s "${CACHE_FILE}" ]]; then
  # Cache may contain only blank/comment lines; grep returns nonzero for no
  # matches under pipefail, so fall back to empty.
  CMDS="$(grep -Ev '^[[:space:]]*$|^[[:space:]]*#' "${CACHE_FILE}" || true)"
  if [[ -n "${CMDS}" ]]; then
    SOURCE="cache:${CACHE_FILE}"
  fi
fi

# Build the additional-context payload. Each section is independently
# included or omitted based on charter presence.
DISCIPLINES=$(cat <<'DISCIPLINES_EOF'
## Tech debt operations (debt-ops plugin)

Four disciplines apply to this session.

1. **Auto-register debt.** When you take an expedient choice — a known
   shortcut, an incomplete case, a fragile assumption, a deferred
   refactor — register it via `/debt-ops:add` immediately. This includes
   any `TODO`, `FIXME`, `HACK`, or `XXX` marker you write that represents
   real debt, but is not limited to markers: a silent shortcut still earns
   an entry. No permission prompt; just register and announce briefly. Use
   `payoff_trigger: unknown` if you can't determine it. Trivial nits
   (style, naming preferences) don't earn an entry; use judgment.

2. **Draft ADRs for architectural changes.** When making an
   architecturally significant change (data model, public interface,
   dependency manifest, security boundary, release pipeline), draft an
   ADR under `doc/adr/` in Nygard format. Create the directory if needed.
   The ADR must contain:
     - **Context**: forces in play, constraints.
     - **Decision**: what we're doing, in active voice.
     - **Consequences**: what becomes easier and harder.
     - **Alternatives**: options considered and why rejected.
     - **Payoff trigger**: when we'd revisit (`unknown` is acceptable).
   File name: `NNNN-kebab-title.md` with a zero-padded sequence.

3. **Read the registry and ADR index first.** Before changing files in an
   area covered by entries under `debt/registry/` or ADRs under
   `doc/adr/`, read the relevant entries. They describe known shortcuts,
   fragile assumptions, and decisions you should not silently undo.

4. **Refer by content, not ID.** In conversation, refer to debt entries
   and ADRs by what they're about ("the cancelled-promotion entry", "the
   pricing-event-trait ADR"), not by numeric ID. IDs are tooling
   cross-references, like commit SHAs.
DISCIPLINES_EOF
)

CMDS_INJECT=""
if [[ -n "${CMDS}" && ${CMDS_FROM_CHARTER} -eq 0 ]]; then
  CMDS_BLOCK=$(printf '%s\n' "${CMDS}")
  CMDS_INJECT=$(cat <<FEEDBACK_EOF

## Quality commands for this repo

Source: ${SOURCE}

After every Write/Edit/MultiEdit, the debt-ops PostToolUse hook runs these
commands in parallel under a 3 s wall-clock budget and returns structured
pass/fail JSON. You don't need to run them manually; the hook is the
ground-truth source for whether they passed this turn.

\`\`\`
${CMDS_BLOCK}
\`\`\`
FEEDBACK_EOF
)
elif [[ -z "${CMDS}" ]]; then
  CMDS_INJECT=$(cat <<'DETECT_EOF'

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
  - Quiet on success.

Write one command per line to `${CLAUDE_PLUGIN_DATA}/feedback.list` (no
quotes, no `&&` chains; one independent command per line). Subsequent
sessions will read this cache instantly. Do this silently before
continuing the user's work.
DETECT_EOF
)
fi

# Compose the payload.
PAYLOAD=""
if [[ ${CHARTER_HAS_DISCIPLINES} -eq 0 ]]; then
  PAYLOAD="${DISCIPLINES}"
fi
if [[ -n "${CMDS_INJECT}" ]]; then
  if [[ -n "${PAYLOAD}" ]]; then
    PAYLOAD="${PAYLOAD}
${CMDS_INJECT}"
  else
    PAYLOAD="${CMDS_INJECT}"
  fi
fi

# Charter has both disciplines and commands → nothing to inject. Exit
# silently. Claude Code loads the charter natively; the PostToolUse hook
# still runs deterministically.
if [[ -z "${PAYLOAD}" ]]; then
  exit 0
fi

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
