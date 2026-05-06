#!/usr/bin/env bash
# Manifest validation: jq syntax + required-field checks for the three JSON
# files Claude Code reads at install/load time. Mirrors the structural checks
# in https://github.com/ivan-magda/claude-code-plugin-template's CI.

set -uo pipefail

TESTS_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
# shellcheck source=lib.sh
source "$TESTS_DIR/lib.sh"

REPO_DIR=$(cd "$TESTS_DIR/../.." && pwd)
PLUGIN_DIR="$REPO_DIR/claude-code"

assert_json_file() {
  local file=$1 msg=$2
  if jq -e . <"$file" >/dev/null 2>&1; then
    pass "$msg"
  else
    fail "$msg" "invalid JSON: $file"
  fi
}

assert_jq() {
  local file=$1 expr=$2 msg=$3
  if jq -e "$expr" <"$file" >/dev/null 2>&1; then
    pass "$msg"
  else
    fail "$msg" "$file: $expr was null/false/missing"
  fi
}

MARKET="$REPO_DIR/.claude-plugin/marketplace.json"
assert_json_file "$MARKET" "marketplace.json: valid JSON"
assert_jq "$MARKET" '.name' "marketplace.json: name present"
assert_jq "$MARKET" '.owner.name' "marketplace.json: owner.name present"
assert_jq "$MARKET" '.plugins | type == "array" and length > 0' "marketplace.json: plugins[] non-empty"

PLUGIN_JSON="$PLUGIN_DIR/.claude-plugin/plugin.json"
assert_json_file "$PLUGIN_JSON" "plugin.json: valid JSON"
assert_jq "$PLUGIN_JSON" '.name' "plugin.json: name present"

HOOKS_JSON="$PLUGIN_DIR/hooks/hooks.json"
assert_json_file "$HOOKS_JSON" "hooks.json: valid JSON"
assert_jq "$HOOKS_JSON" '.hooks' "hooks.json: hooks block present"

# Each marketplace entry must point at a directory with a real plugin.json.
plugin_count=$(jq -r '.plugins | length' <"$MARKET")
for i in $(seq 0 $((plugin_count - 1))); do
  src=$(jq -r ".plugins[$i].source" <"$MARKET")
  name=$(jq -r ".plugins[$i].name" <"$MARKET")
  abs="$REPO_DIR/$src/.claude-plugin/plugin.json"
  if [[ -f "$abs" ]]; then
    pass "marketplace plugin '$name' source resolves to plugin.json"
  else
    fail "marketplace plugin '$name'" "no plugin.json at $abs"
  fi
done

# Each command in hooks.json must reference a script that actually exists,
# resolved against ${CLAUDE_PLUGIN_ROOT} = the plugin dir.
mapfile -t commands < <(jq -r '.. | objects | select(.command) | .command' <"$HOOKS_JSON")
for cmd in "${commands[@]}"; do
  resolved=${cmd//\$\{CLAUDE_PLUGIN_ROOT\}/$PLUGIN_DIR}
  script=${resolved%% *}
  if [[ -f "$script" ]]; then
    pass "hooks.json command resolves: $(basename "$script")"
  else
    fail "hooks.json command unresolved" "$cmd -> $script"
  fi
done

summary
