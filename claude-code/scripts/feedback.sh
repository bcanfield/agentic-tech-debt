#!/usr/bin/env bash
set -euo pipefail

# debt-ops PostToolUse hook.
# Reads cached/charter quality commands, runs each in parallel under a 3s
# self-imposed budget, returns {pass|fail|timeout} JSON via additionalContext.
# Spec: docs/tech-debt-plugin-plan.md §Pillar 7, §"v1 implementation requirements" #1, #3.

# A bug here must never block the tool cycle.
exit_clean() { exit 0; }
trap exit_clean ERR

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
  printf '{"hookSpecificOutput":{"hookEventName":"PostToolUse","additionalContext":"%s"}}\n' \
    "$(to_json_string "$1")"
}

TOPLEVEL=$(git rev-parse --show-toplevel 2>/dev/null) || exit 0

REPO_HASH=$(printf '%s' "$TOPLEVEL" | shasum | cut -c1-12)
CACHE_BASE=${CLAUDE_PLUGIN_DATA:-$HOME/.cache/debt-ops}
CACHE_DIR="$CACHE_BASE/cache/$REPO_HASH"

# Extract the changed file from PostToolUse input so commands using
# $CHANGED_FILES can scope to it (Pillar 7 fast-loop intent).
INPUT=$(cat 2>/dev/null || true)
CHANGED_FILES=''
if command -v jq >/dev/null 2>&1 && [[ -n "$INPUT" ]]; then
  CHANGED_FILES=$(printf '%s' "$INPUT" | jq -r '.tool_input.file_path // empty' 2>/dev/null || true)
fi
export CHANGED_FILES

read_commands() {
  local claude_md="$TOPLEVEL/CLAUDE.md"
  if [[ -f "$claude_md" ]] && grep -qF '<!-- debt-ops:feedback v1 -->' "$claude_md"; then
    awk '
      /<!-- debt-ops:feedback v1 -->/ {found=1; next}
      found && /<!-- \/debt-ops:feedback -->/ {exit}
      found && /^##[[:space:]]/ {exit}
      found {print}
    ' "$claude_md"
    return
  fi
  [[ -f "$CACHE_DIR/feedback.list" ]] && cat "$CACHE_DIR/feedback.list"
}

run_with_timeout() {
  local secs=$1; shift
  if command -v timeout >/dev/null 2>&1; then
    timeout "$secs" bash -c "$*"
  elif command -v gtimeout >/dev/null 2>&1; then
    gtimeout "$secs" bash -c "$*"
  else
    bash -c "$*" &
    local pid=$!
    ( sleep "$secs"; kill "$pid" 2>/dev/null || true ) &
    local watcher=$!
    local rc=0
    wait "$pid" 2>/dev/null || rc=$?
    kill "$watcher" 2>/dev/null || true
    return "$rc"
  fi
}

test_count_now() {
  find "$TOPLEVEL" -type f \
    \( -name 'test_*' -o -name '*_test.*' -o -name '*.test.*' -o -name '*.spec.*' \) \
    -not -path '*/.git/*' -not -path '*/node_modules/*' \
    -not -path '*/target/*' -not -path '*/dist/*' -not -path '*/build/*' \
    2>/dev/null | wc -l | tr -d ' '
}

COMMANDS=$(read_commands || true)
[[ -z "$COMMANDS" ]] && exit 0

RESULTS_FILE=$(mktemp)
cleanup() { rm -f "$RESULTS_FILE"; exit 0; }
trap cleanup EXIT

declare -a PIDS=()
while IFS= read -r line; do
  line=${line%"${line##*[![:space:]]}"}
  [[ -z "$line" || "$line" == \#* ]] && continue
  if [[ "$line" == *'$CHANGED_FILES'* && -z "${CHANGED_FILES:-}" ]]; then
    printf '%s\tSKIP_NO_FILE\n' "$line" >> "$RESULTS_FILE"
    continue
  fi
  (
    if out=$(run_with_timeout 3 "$line" 2>&1); then
      printf '%s\tPASS\n' "$line" >> "$RESULTS_FILE"
    else
      rc=$?
      if [[ $rc -eq 124 || $rc -eq 137 || $rc -eq 143 ]]; then
        printf '%s\tTIMEOUT\n' "$line" >> "$RESULTS_FILE"
      else
        snippet=${out:0:200}
        printf '%s\tFAIL\t%s\n' "$line" "$snippet" >> "$RESULTS_FILE"
      fi
    fi
  ) &
  PIDS+=($!)
done <<< "$COMMANDS"

if [[ ${#PIDS[@]} -gt 0 ]]; then
  wait "${PIDS[@]}" 2>/dev/null || true
fi

WARN=''
if [[ -f "$CACHE_DIR/test-count" ]]; then
  prev=$(cat "$CACHE_DIR/test-count" 2>/dev/null || true)
  now=$(test_count_now || true)
  if [[ "$now" =~ ^[0-9]+$ && "$prev" =~ ^[0-9]+$ ]]; then
    if [[ "$now" -lt "$prev" ]]; then
      WARN="WARNING: this edit removed $(( prev - now )) test file(s) (was $prev, now $now)."
      printf '%s' "$now" > "$CACHE_DIR/test-count" 2>/dev/null || true
    elif [[ "$now" -gt "$prev" ]]; then
      printf '%s' "$now" > "$CACHE_DIR/test-count" 2>/dev/null || true
    fi
  fi
fi

SUMMARY=$(cat "$RESULTS_FILE" 2>/dev/null || true)
[[ -z "$SUMMARY" && -z "$WARN" ]] && exit 0

OUT=''
if [[ -n "$SUMMARY" ]]; then
  OUT="debt-ops feedback (3s budget per command):"$'\n'"$SUMMARY"
fi
if [[ -n "$WARN" ]]; then
  if [[ -n "$OUT" ]]; then
    OUT="$OUT"$'\n\n'"$WARN"
  else
    OUT="$WARN"
  fi
fi

emit_envelope "$OUT"
exit 0
