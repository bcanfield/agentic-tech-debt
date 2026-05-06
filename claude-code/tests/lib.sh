#!/usr/bin/env bash
# Shared helpers for debt-ops test files. Sourced by each test_*.sh.

[[ -n "${_DEBT_OPS_TESTS_LIB:-}" ]] && return 0
_DEBT_OPS_TESTS_LIB=1

PASSED=0
FAILED=0

pass() {
  printf '  ok   %s\n' "$1"
  PASSED=$((PASSED + 1))
}

fail() {
  printf '  FAIL %s\n' "$1"
  [[ -n "${2:-}" ]] && printf '       %s\n' "$2"
  FAILED=$((FAILED + 1))
}

assert_eq() {
  local actual=$1 expected=$2 msg=$3
  if [[ "$actual" == "$expected" ]]; then
    pass "$msg"
  else
    fail "$msg" "expected: ${expected@Q} | got: ${actual@Q}"
  fi
}

assert_contains() {
  local haystack=$1 needle=$2 msg=$3
  if [[ "$haystack" == *"$needle"* ]]; then
    pass "$msg"
  else
    fail "$msg" "missing substring: ${needle@Q}"
  fi
}

assert_json() {
  local input=$1 msg=$2
  if printf '%s' "$input" | jq -e . >/dev/null 2>&1; then
    pass "$msg"
  else
    fail "$msg" "not valid JSON: ${input:0:200}"
  fi
}

# Creates a fresh /tmp git repo and prints its absolute path.
setup_temp_repo() {
  local dir
  dir=$(mktemp -d)
  (cd "$dir" && git init -q)
  printf '%s' "$dir"
}

cleanup_temp_repo() {
  [[ -d "${1:-}" && "$1" == /tmp/* ]] && rm -rf "$1"
}

summary() {
  printf '  -- %d ok, %d fail\n' "$PASSED" "$FAILED"
  [[ $FAILED -eq 0 ]]
}
