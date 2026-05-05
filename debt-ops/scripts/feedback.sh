#!/usr/bin/env bash
# debt-ops PostToolUse hook.
#
# Reads cached/charter quality commands, runs them in parallel under a 3 s
# wall-clock budget, and reports {command: pass|fail|timeout|skip} as
# additionalContext to the agent. Never blocks an edit; v1 is feedback-only.

set -u
umask 077

BUDGET_SECS="${DEBT_OPS_FEEDBACK_BUDGET:-3}"

# Resolve commands from charter marker first, then plugin-data cache.
CHARTER=""
for candidate in AGENTS.md CLAUDE.md; do
  if [[ -f "${candidate}" ]]; then
    CHARTER="${candidate}"
    break
  fi
done

read_charter() {
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
if [[ -n "${CHARTER}" ]] && grep -qE '<!--[[:space:]]*debt-ops:feedback[[:space:]]*-->' "${CHARTER}" 2>/dev/null; then
  CMDS="$(read_charter "${CHARTER}")"
fi
if [[ -z "${CMDS}" && -n "${CLAUDE_PLUGIN_DATA:-}" && -s "${CLAUDE_PLUGIN_DATA}/feedback.list" ]]; then
  CMDS="$(grep -Ev '^[[:space:]]*$|^[[:space:]]*#' "${CLAUDE_PLUGIN_DATA}/feedback.list")"
fi

# No commands known yet: stay silent. The SessionStart inject already asked
# Claude to detect them; spamming on every edit would be noise.
if [[ -z "${CMDS}" ]]; then
  exit 0
fi

WORK="$(mktemp -d 2>/dev/null || mktemp -d -t debt-ops)"
trap 'rm -rf "${WORK}"' EXIT

# Launch each command in the background. Per-command output captured for
# truncated tail on failure.
declare -a CMD_LIST=()
declare -a PIDS=()
i=0
while IFS= read -r cmd; do
  [[ -z "${cmd}" ]] && continue
  CMD_LIST+=("${cmd}")
  out="${WORK}/${i}.out"
  status="${WORK}/${i}.status"
  ( bash -c "${cmd}" >"${out}" 2>&1; echo $? >"${status}" ) &
  PIDS+=($!)
  i=$((i + 1))
done <<<"${CMDS}"

# Aggregate wall-clock budget: poll until all done or budget elapses.
deadline=$(( $(date +%s) + BUDGET_SECS ))
while :; do
  remaining=0
  for pid in "${PIDS[@]}"; do
    if kill -0 "${pid}" 2>/dev/null; then
      remaining=$((remaining + 1))
    fi
  done
  [[ ${remaining} -eq 0 ]] && break
  now=$(date +%s)
  [[ ${now} -ge ${deadline} ]] && break
  sleep 0.1
done

# Anything still running over budget: terminate (TERM, then KILL).
for pid in "${PIDS[@]}"; do
  if kill -0 "${pid}" 2>/dev/null; then
    kill -TERM "${pid}" 2>/dev/null || true
  fi
done
sleep 0.2
for pid in "${PIDS[@]}"; do
  if kill -0 "${pid}" 2>/dev/null; then
    kill -KILL "${pid}" 2>/dev/null || true
  fi
done

# Build the result JSON. python3 if available (safe escaping); else a
# best-effort hand-rolled fallback.
if command -v python3 >/dev/null 2>&1; then
  python3 - "${WORK}" "${BUDGET_SECS}" "${CMD_LIST[@]}" <<'PY'
import json, os, sys

work = sys.argv[1]
budget = sys.argv[2]
cmds = sys.argv[3:]

results = {}
any_fail = False
any_timeout = False

for i, cmd in enumerate(cmds):
    status_path = os.path.join(work, f"{i}.status")
    out_path = os.path.join(work, f"{i}.out")
    if not os.path.exists(status_path):
        results[cmd] = {"status": "timeout"}
        any_timeout = True
        continue
    try:
        rc = int(open(status_path).read().strip() or "1")
    except ValueError:
        rc = 1
    if rc == 0:
        results[cmd] = {"status": "pass"}
    else:
        any_fail = True
        tail = ""
        if os.path.exists(out_path):
            try:
                data = open(out_path, "rb").read().decode("utf-8", errors="replace")
            except Exception:
                data = ""
            lines = data.splitlines()
            tail = "\n".join(lines[-20:])
        results[cmd] = {"status": "fail", "exit_code": rc, "output_tail": tail}

if not any_fail and not any_timeout:
    # All-pass: stay silent so we don't pollute the model's context on the
    # happy path. Hooks are only useful when they say something actionable.
    sys.exit(0)

summary = {
    "source": "debt-ops:feedback",
    "budget_seconds": int(budget),
    "results": results,
}
context = (
    "debt-ops PostToolUse: one or more quality commands failed or timed out. "
    "Surface this to the user only if it's relevant to the change you just "
    "made; otherwise note it and continue.\n\n"
    "```json\n" + json.dumps(summary, indent=2) + "\n```"
)
print(json.dumps({
    "hookSpecificOutput": {
        "hookEventName": "PostToolUse",
        "additionalContext": context,
    }
}))
PY
  exit 0
fi

# Fallback (no python3): emit a minimal text-only summary.
any_fail=0
summary=""
for idx in "${!CMD_LIST[@]}"; do
  cmd="${CMD_LIST[$idx]}"
  status_path="${WORK}/${idx}.status"
  if [[ ! -f "${status_path}" ]]; then
    summary+="- timeout: ${cmd}"$'\n'
    any_fail=1
  else
    rc=$(cat "${status_path}" 2>/dev/null || echo 1)
    if [[ "${rc}" == "0" ]]; then
      :
    else
      summary+="- fail (exit ${rc}): ${cmd}"$'\n'
      any_fail=1
    fi
  fi
done

[[ ${any_fail} -eq 0 ]] && exit 0

esc=$(printf '%s' "debt-ops PostToolUse failures:
${summary}" | sed -e 's/\\/\\\\/g' -e 's/"/\\"/g' | awk 'BEGIN{ORS="\\n"}{print}')
printf '{"hookSpecificOutput":{"hookEventName":"PostToolUse","additionalContext":"%s"}}\n' "${esc}"
exit 0
