#!/usr/bin/env bash
# Hook-contract tests for scripts/feedback.sh.

set -uo pipefail

TESTS_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
# shellcheck source=lib.sh
source "$TESTS_DIR/lib.sh"

PLUGIN_DIR=$(cd "$TESTS_DIR/.." && pwd)
SCRIPT="$PLUGIN_DIR/scripts/feedback.sh"
FIXTURE="$TESTS_DIR/fixtures/post_tool_use.json"

# No charter, no cache: hook must exit cleanly with empty stdout (PostToolUse
# stdout is only consumed when an envelope is emitted; silence is correct).
test_no_commands_silent() {
  local tmp out rc
  tmp=$(setup_temp_repo)
  out=$(cd "$tmp" && CLAUDE_PLUGIN_DATA="$tmp/data" "$SCRIPT" <"$FIXTURE")
  rc=$?
  assert_eq "$rc" "0" "no-commands: exit 0"
  assert_eq "$out" "" "no-commands: empty stdout"
  cleanup_temp_repo "$tmp"
}

# Charter with a fast command: must emit envelope tagged PASS.
test_charter_command_passes() {
  local tmp out
  tmp=$(setup_temp_repo)
  cat >"$tmp/CLAUDE.md" <<'EOF'
## Tech debt operations

<!-- debt-ops:feedback v1 -->
echo hello
<!-- /debt-ops:feedback -->
EOF
  out=$(cd "$tmp" && CLAUDE_PLUGIN_DATA="$tmp/data" "$SCRIPT" <"$FIXTURE")
  assert_json "$out" "charter-pass: stdout is valid JSON"
  assert_contains "$out" '"hookEventName":"PostToolUse"' "charter-pass: PostToolUse envelope"
  assert_contains "$out" "echo hello" "charter-pass: command echoed in summary"
  assert_contains "$out" "PASS" "charter-pass: PASS marker present"
  cleanup_temp_repo "$tmp"
}

# Charter with a failing command: must emit envelope tagged FAIL.
test_charter_command_fails() {
  local tmp out
  tmp=$(setup_temp_repo)
  cat >"$tmp/CLAUDE.md" <<'EOF'
## Tech debt operations

<!-- debt-ops:feedback v1 -->
false
<!-- /debt-ops:feedback -->
EOF
  out=$(cd "$tmp" && CLAUDE_PLUGIN_DATA="$tmp/data" "$SCRIPT" <"$FIXTURE")
  assert_json "$out" "charter-fail: stdout is valid JSON"
  assert_contains "$out" "FAIL" "charter-fail: FAIL marker present"
  cleanup_temp_repo "$tmp"
}

test_no_commands_silent
test_charter_command_passes
test_charter_command_fails
summary
