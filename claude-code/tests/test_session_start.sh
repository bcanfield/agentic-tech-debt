#!/usr/bin/env bash
# Hook-contract tests for scripts/session-start.sh.
# Each case sets up an isolated git repo + cache dir, runs the hook, and
# asserts the JSON envelope against the contract documented in
# https://code.claude.com/docs/en/hooks.

set -uo pipefail

TESTS_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
# shellcheck source=lib.sh
source "$TESTS_DIR/lib.sh"

PLUGIN_DIR=$(cd "$TESTS_DIR/.." && pwd)
SCRIPT="$PLUGIN_DIR/scripts/session-start.sh"

# Outside a git repo, the plugin must idle (Pillar 7: never corrupt the
# cross-repo cache when there is no toplevel to key on).
test_outside_git_repo() {
  local tmp out
  tmp=$(mktemp -d)
  out=$(cd "$tmp" && CLAUDE_PLUGIN_DATA="$tmp/data" "$SCRIPT")
  assert_json "$out" "outside-git: stdout is valid JSON"
  assert_contains "$out" '"hookEventName":"SessionStart"' "outside-git: SessionStart envelope"
  assert_contains "$out" "not a git repo" "outside-git: idle message"
  cleanup_temp_repo "$tmp"
}

# Fresh repo, no charter, empty cache: must emit disciplines plus the
# first-session discovery prompt for quality commands.
test_fresh_repo_first_session() {
  local tmp out
  tmp=$(setup_temp_repo)
  out=$(cd "$tmp" && CLAUDE_PLUGIN_DATA="$tmp/data" "$SCRIPT")
  assert_json "$out" "fresh-repo: stdout is valid JSON"
  assert_contains "$out" "Tech-debt-operations disciplines" "fresh-repo: disciplines header present"
  assert_contains "$out" "/debt-ops:add" "fresh-repo: discipline 1 references /debt-ops:add"
  assert_contains "$out" "First session for this repo" "fresh-repo: discovery prompt present"
  cleanup_temp_repo "$tmp"
}

# CLAUDE.md with the v1 charter marker: hook should defer to CLAUDE.md
# instead of emitting the discovery prompt or the cached-list path.
test_charter_present() {
  local tmp out
  tmp=$(setup_temp_repo)
  cat >"$tmp/CLAUDE.md" <<'EOF'
# Project

## Tech debt operations

<!-- debt-ops:feedback v1 -->
echo hello
<!-- /debt-ops:feedback -->
EOF
  out=$(cd "$tmp" && CLAUDE_PLUGIN_DATA="$tmp/data" "$SCRIPT")
  assert_json "$out" "charter: stdout is valid JSON"
  assert_contains "$out" "CLAUDE.md is the source of truth" "charter: defers to CLAUDE.md"
  if [[ "$out" != *"First session for this repo"* ]]; then
    pass "charter: suppresses first-session discovery prompt"
  else
    fail "charter: suppresses first-session discovery prompt" "discovery prompt leaked"
  fi
  cleanup_temp_repo "$tmp"
}

test_outside_git_repo
test_fresh_repo_first_session
test_charter_present
summary
