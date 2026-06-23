---
name: debt-ops-metrics
description: Print a debt-ops health summary from the metrics log, covering registration rate, feedback action rate, ADR creation, and AI-authored share. Use when the user asks for "debt-ops metrics", "debt health", "registry stats", or a tech-debt health summary. Read-only, never writes the log.
---

# debt-ops-metrics

Read the hidden metrics log and tell the user whether the tripwires are tripping.

## 1. Find the log

The repo-hash is computed in Python (not `shasum`) so this is identical across
macOS, Linux, and Windows — no BSD/GNU coreutils dependency.

```bash
REPO_HASH=$(python3 -c "import hashlib,subprocess;t=subprocess.run(['git','rev-parse','--show-toplevel'],capture_output=True,text=True).stdout.strip();print(hashlib.sha1(t.encode()).hexdigest()[:12] if t else '')")

# Hooks and skills share one deterministic cache base. Override with
# DEBT_OPS_CACHE; default is ~/.cache/debt-ops.
CACHE_DIR="${DEBT_OPS_CACHE:-$HOME/.cache/debt-ops}/cache/$REPO_HASH"

LOG="$CACHE_DIR/metrics.jsonl"
if [ -n "$REPO_HASH" ] && [ -f "$LOG" ]; then
  tail -n 500 "$LOG"
else
  echo "MISSING: no metrics.jsonl found for repo hash ${REPO_HASH:-<not-a-git-repo>}"
fi
```

If the file is missing or empty, tell the user no debt-ops activity has been logged
for this repo yet and stop. On a skills-only tool (no hook adapter), only
`register` and `review` events are logged — the per-edit `edit`/`feedback`/`session`
events come from the hook adapter, so feedback metrics will be absent. Say so rather
than reporting them as zero.

## 2. The log format

One JSON object per line. Event shapes:

- `{"event":"register","slug":"...","ai_authored":bool,"letter":"...","ts":"..."}` — each capture
- `{"event":"review","total":N,"stale":N,"cold":N,"active":N,"ts":"..."}` — each review
- `{"event":"edit","file":"...","registry_count":N,"ts":"..."}` — every agent edit *(hook adapter only)*
- `{"event":"feedback","file":"...","result":"pass|fail","ts":"..."}` — every quality-check fire *(hook adapter only)*
- `{"event":"session","registry_count":N,"adr_count":M,"ai_authored_count":K,"ts":"..."}` — start of each session *(hook adapter only)*

Timestamps are ISO-8601 UTC.

## 3. Compute the tripwires

Filter to the last 7 days. Then compute what the available events support:

- **Captures / reviews** — counts of `event:register` and `event:review`.
- **AI-authored share** — share of `register` events with `ai_authored:true`.
- **Edits / sessions** *(hook adapter only)* — counts of `event:edit` and `event:session`.
- **Registry growth** *(hook adapter only)* — last `registry_count` minus first.
- **Feedback pass rate** *(hook adapter only)* — `count(result:pass) / count(event:feedback)`.
- **FAIL → PASS rate** *(hook adapter only)* — for each `feedback` with `result:fail`,
  look at the *next* feedback for the *same* file; count those that flipped to
  `pass`; divide by total fails. Below 50% means the agent isn't reliably acting on
  hook output — the architectural alarm bell.

If there are fewer than 5 data points in the window, say "need more data" and skip
the verdict.

## 4. Report

One screen. No padding. Use `→` and `↑/↓` for trends. Mark adapter-only rows as
`n/a (skills-only)` when those events are absent. Example shape:

```
debt-ops metrics — last 7 days
─────────────────────────────────
captures        : 7
reviews         : 2
ai-authored     : 57%

edits           : n/a (skills-only)
feedback ran    : n/a (skills-only)

verdict: ok
```

End with one judgment line:
- **ok** — captures >0 (and, when available, fail→pass rate ≥50%).
- **investigate: <reason>** — name the specific tripwire that tripped.

## Don't

- Don't write to the log.
- Don't compute metrics not listed above.
- Don't report adapter-only metrics as `0` on a skills-only tool — mark them `n/a`.
- Don't guess at health when data is thin — say "need more data" instead.
