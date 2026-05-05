#!/usr/bin/env bash
set -euo pipefail

# debt-ops SessionStart hook.
# Resolves: disciplines + (CLAUDE.md charter > per-repo cache > discovery prompt)
# and emits a hookSpecificOutput.additionalContext envelope.
# Spec: docs/tech-debt-plugin-plan.md §Pillar 7, §"v1 implementation requirements".

to_json_string() {
  local s=$1
  s=${s//\\/\\\\}
  s=${s//\"/\\\"}
  s=${s//$'\n'/\\n}
  s=${s//$'\r'/\\r}
  s=${s//$'\t'/\\t}
  printf '%s' "$s"
}

emit_envelope() {
  printf '{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"%s"}}\n' \
    "$(to_json_string "$1")"
}

if ! TOPLEVEL=$(git rev-parse --show-toplevel 2>/dev/null); then
  # Without a git toplevel, the naive "$cwd | shasum" key collides across every
  # non-git dir. Idle out instead of corrupting the shared cache.
  emit_envelope "debt-ops: not a git repo, plugin idle this session"
  exit 0
fi

REPO_HASH=$(printf '%s' "$TOPLEVEL" | shasum | cut -c1-12)
CACHE_BASE=${CLAUDE_PLUGIN_DATA:-$HOME/.cache/debt-ops}
CACHE_DIR="$CACHE_BASE/cache/$REPO_HASH"
STATELESS=0
mkdir -p "$CACHE_DIR" 2>/dev/null || STATELESS=1

manifest_hash() {
  local files=() out=''
  for f in Cargo.toml package.json pyproject.toml Makefile go.mod Gemfile; do
    [[ -f "$TOPLEVEL/$f" ]] && files+=("$TOPLEVEL/$f")
  done
  if [[ ${#files[@]} -eq 0 ]]; then
    printf 'no-manifest'
    return
  fi
  if out=$(stat -f '%m %N' "${files[@]}" 2>/dev/null) && [[ -n "$out" ]]; then
    printf '%s' "$out" | shasum | cut -c1-12
  elif out=$(stat -c '%Y %n' "${files[@]}" 2>/dev/null) && [[ -n "$out" ]]; then
    printf '%s' "$out" | shasum | cut -c1-12
  else
    printf 'stat-failed'
  fi
}
MANIFEST_HASH=$(manifest_hash)

CHARTER_MARKER='<!-- debt-ops:feedback v1 -->'
HAS_CHARTER=0
if [[ -f "$TOPLEVEL/CLAUDE.md" ]] && grep -qF "$CHARTER_MARKER" "$TOPLEVEL/CLAUDE.md"; then
  HAS_CHARTER=1
fi

DISCIPLINES=$(cat <<'EOF'
1. If you write a `TODO`, `FIXME`, `HACK`, or `XXX` marker, register it via /debt-ops:add immediately. No permission prompt; just do it. Use `payoff_trigger: unknown` if unsure. Announce as one line: `+1 entry: <slug> (drop?)`. Treat over-registering as cheap; the developer can reply "drop it" and you'll delete the entry.

2. When making an architecturally significant change — a data model, public interface, security boundary, release pipeline, or a dep-manifest change that is a major-version bump or a *new* top-level dependency — draft an ADR under doc/adr/ in Nygard format (Context, Decision, Consequences, Alternatives, Payoff trigger). Create the directory if needed. Only draft an ADR when there are two credible alternatives; if you cannot list two, it is a comment, not an ADR. If the ADR introduces deliberate debt, also call /debt-ops:add so the registry entry mirrors the ADR.

3. Read entries under debt/registry/ before changing files they reference.
EOF
)

build_commands_block() {
  if [[ $HAS_CHARTER -eq 1 ]]; then
    printf 'Quality commands: read the CLAUDE.md section marked `%s`. CLAUDE.md is the source of truth when present.' "$CHARTER_MARKER"
    return
  fi
  if [[ $STATELESS -eq 1 ]]; then
    printf 'debt-ops: cache disabled (read-only %s). For this session, detect quality commands once and run them yourself under timeout 3.' "$CACHE_BASE"
    return
  fi
  local list_file="$CACHE_DIR/feedback.list"
  local hash_file="$CACHE_DIR/manifest.hash"
  local cached_hash=''
  [[ -f "$hash_file" ]] && cached_hash=$(cat "$hash_file")
  if [[ -f "$list_file" && "$cached_hash" == "$MANIFEST_HASH" ]]; then
    printf 'Cached quality commands (one per line; comment lines are estimates):\n%s' "$(cat "$list_file")"
    return
  fi
  cat <<EOF
First session for this repo (or manifest changed). Please do the following silently — no need to announce:

1. Detect this project's quality commands by scanning manifest files (Cargo.toml, package.json, pyproject.toml, Makefile, go.mod, Gemfile) and tool-specific config (eslint, biome, ruff, mypy, tsconfig, etc.).
2. Prefer commands that accept a changed-file or changed-package argument (e.g., \`eslint \$CHANGED_FILES\`, \`cargo clippy --no-deps -p \$CHANGED_PACKAGE\`, \`pytest path/to/dir\`) over project-wide ones.
3. Reject any command whose typical wall-clock on this repo exceeds 3 seconds. Project-wide commands almost always exceed this on non-trivial repos.
4. Write to ${CACHE_DIR}/feedback.list. Format: one command per line, with the wall-clock estimate as a preceding comment, e.g.:
   # est ~0.8s — fast type check
   tsc --noEmit -p tsconfig.json
   Comments (#) and empty lines are skipped when feedback.sh reads the file.
5. Write the manifest hash to ${CACHE_DIR}/manifest.hash with this exact value: ${MANIFEST_HASH}
6. Count test-shaped filenames in the repo (filenames matching test_*, *_test.*, *.test.*, or *.spec.*) and write the integer count to ${CACHE_DIR}/test-count. feedback.sh recomputes this on every edit and warns when it drops.
EOF
}

CONTEXT="Tech-debt-operations disciplines (debt-ops plugin):

${DISCIPLINES}

$(build_commands_block)"

emit_envelope "$CONTEXT"
