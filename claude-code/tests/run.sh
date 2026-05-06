#!/usr/bin/env bash
# Test runner for the debt-ops plugin.
# Usage: claude-code/tests/run.sh [test_file...]
# Each test_*.sh runs in its own bash subprocess so a failure in one file
# does not abort the rest of the suite.

set -uo pipefail

TESTS_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)

if [[ $# -gt 0 ]]; then
  files=("$@")
else
  shopt -s nullglob
  files=("$TESTS_DIR"/test_*.sh)
fi

if [[ ${#files[@]} -eq 0 ]]; then
  printf 'no test files found under %s\n' "$TESTS_DIR" >&2
  exit 1
fi

failed_files=0
for f in "${files[@]}"; do
  printf '\n=== %s ===\n' "$(basename "$f")"
  if ! bash "$f"; then
    failed_files=$((failed_files + 1))
  fi
done

printf '\n'
if [[ $failed_files -eq 0 ]]; then
  printf 'all %d test file(s) passed\n' "${#files[@]}"
  exit 0
fi
printf '%d of %d test file(s) failed\n' "$failed_files" "${#files[@]}"
exit 1
