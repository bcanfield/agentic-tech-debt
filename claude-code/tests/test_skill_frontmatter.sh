#!/usr/bin/env bash
# SKILL.md frontmatter checks. Mirrors what
# anthropics/claude-plugins-official's validate-frontmatter workflow asserts:
# every skill has a non-empty `name` and `description`.

set -uo pipefail

TESTS_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
# shellcheck source=lib.sh
source "$TESTS_DIR/lib.sh"

PLUGIN_DIR=$(cd "$TESTS_DIR/.." && pwd)

# Print only the frontmatter block (between the first two `---` delimiters).
extract_frontmatter() {
  awk '
    /^---[[:space:]]*$/ { c++; if (c == 2) exit; next }
    c == 1 { print }
  ' "$1"
}

frontmatter_field() {
  local file=$1 key=$2
  extract_frontmatter "$file" | awk -v k="$key" '
    BEGIN { FS = ":" }
    $1 == k {
      sub(/^[^:]*:[[:space:]]*/, "")
      print
      exit
    }
  '
}

shopt -s nullglob
skills=("$PLUGIN_DIR"/skills/*/SKILL.md)
if [[ ${#skills[@]} -eq 0 ]]; then
  fail "skills" "no SKILL.md files found under $PLUGIN_DIR/skills/"
  summary
  exit
fi

for skill in "${skills[@]}"; do
  rel=${skill#"$PLUGIN_DIR"/}
  for key in name description; do
    value=$(frontmatter_field "$skill" "$key")
    if [[ -n "$value" ]]; then
      pass "$rel: frontmatter '$key' is non-empty"
    else
      fail "$rel: frontmatter '$key'" "missing or empty"
    fi
  done
done

summary
