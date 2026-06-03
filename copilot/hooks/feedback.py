#!/usr/bin/env python3
"""debt-ops Copilot postToolUse hook: run quality commands on each agent edit.

Copilot adapter. Copilot's postToolUse fires after EVERY tool (no matcher), so
this self-filters to file-edit tools by toolName/toolArgs and idles on the rest.
The core run loop is kept byte-identical to the Claude adapter's feedback.py so
the planned _common.py extraction (ADR 0011 / packaging plan Phase E) is a clean
lift; only the I/O shim differs:

- stdin: Copilot delivers {toolName, toolArgs, toolResult} (camelCase), not
  Claude's {tool_name, tool_input.file_path}.
- stdout: Copilot expects a bare {"additionalContext": "..."} object; Claude
  wraps it in {"hookSpecificOutput": {...}}.
- commands source: the Copilot charter files (.github/copilot-instructions.md /
  AGENTS.md) carry the `<!-- debt-ops:feedback v1 -->` marker block; there is no
  SessionStart model-detection step on Copilot (command hooks can't inject), so
  the charter — written by debt-ops-init — is the source of truth.
"""

import concurrent.futures
import hashlib
import json
import os
import re
import shlex
import subprocess
import sys
import time
from pathlib import Path

MARKER_OPEN = "<!-- debt-ops:feedback v1 -->"
MARKER_CLOSE = "<!-- /debt-ops:feedback -->"
PER_COMMAND_TIMEOUT = 3
SNIPPET_LEN = 200
DEBUG_ENV = "DEBT_OPS_DEBUG"
SKIP_DIRS = {".git", "node_modules", "target", "dist", "build"}
TEST_PATTERNS = (
    re.compile(r"^test_"),
    re.compile(r"_test\."),
    re.compile(r"\.test\."),
    re.compile(r"\.spec\."),
)
HEADING_RE = re.compile(r"^##\s")

# Copilot has no PostToolUse matcher, so we filter here. Edit-ish tool names
# across agents: write/edit/create/apply_patch/str_replace/insert/update/modify.
EDIT_TOOL_RE = re.compile(r"(edit|write|create|apply.?patch|str.?replace|insert|update.?file|modify)", re.I)
# Keys an edit tool's args might carry the target path under.
PATH_KEYS = ("path", "file_path", "filePath", "file", "target_file", "filename")
# Charter files Copilot auto-loads; first marker block wins.
CHARTER_FILES = (".github/copilot-instructions.md", "AGENTS.md", "CLAUDE.md")


# Copilot postToolUse output envelope: a bare object with additionalContext.
def emit(context):
    sys.stdout.write(json.dumps({"additionalContext": context}) + "\n")


# Repo root, or None if we're not in a git repo.
def git_toplevel():
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, check=True,
        )
        s = out.stdout.strip()
        return Path(s) if s else None
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


# Short stable hash of the repo path — used as the cache subdirectory name.
def repo_hash(toplevel):
    return hashlib.sha1(str(toplevel).encode()).hexdigest()[:12]


# Single deterministic cache base, shared with the skills (override DEBT_OPS_CACHE).
def cache_base():
    override = os.environ.get("DEBT_OPS_CACHE")
    return Path(override) if override else (Path.home() / ".cache" / "debt-ops")


# Pull (tool_name, file_path) out of Copilot's postToolUse stdin payload.
# Returns ("", "") on anything that isn't a file edit so the caller can idle.
def changed_file_from_stdin():
    try:
        raw = sys.stdin.read()
    except OSError:
        return "", ""
    if not raw:
        return "", ""
    try:
        data = json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        return "", ""

    tool_name = data.get("toolName") or ""
    if not EDIT_TOOL_RE.search(tool_name):
        return tool_name, ""

    args = data.get("toolArgs")
    if isinstance(args, str):
        try:
            args = json.loads(args)
        except (json.JSONDecodeError, ValueError):
            args = {}
    if not isinstance(args, dict):
        return tool_name, ""
    for k in PATH_KEYS:
        v = args.get(k)
        if isinstance(v, str) and v.strip():
            return tool_name, v.strip()
    return tool_name, ""


# Loads quality commands. Charter marker block wins if present; else cached list.
def read_commands(toplevel, cache_dir):
    for rel in CHARTER_FILES:
        f = toplevel / rel
        if not f.is_file():
            continue
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if MARKER_OPEN in text:
            block = []
            collecting = False
            for line in text.splitlines():
                if not collecting:
                    if MARKER_OPEN in line:
                        collecting = True
                    continue
                if MARKER_CLOSE in line or HEADING_RE.match(line):
                    break
                block.append(line)
            return "\n".join(block)
    list_file = cache_dir / "feedback.list"
    if list_file.is_file():
        try:
            return list_file.read_text(encoding="utf-8")
        except OSError:
            return ""
    return ""


# Debug log path — only when DEBT_OPS_DEBUG=1 is set in the environment.
def debug_path(cache_dir):
    if not os.environ.get(DEBUG_ENV):
        return None
    return cache_dir / "debug.log"


# Appends one tab-separated line to the debug log; silently no-ops on failure.
def dlog(path, *fields):
    if path is None:
        return
    ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    try:
        with path.open("a", encoding="utf-8") as f:
            f.write("\t".join((ts, *fields)) + "\n")
    except OSError:
        pass


# Runs one quality command under a 3s timeout. Returns (cmd, status, snippet).
def run_one(line, changed_files, env):
    has_var = "$CHANGED_FILES" in line or "${CHANGED_FILES}" in line
    if has_var and not changed_files:
        return line, "SKIP_NO_FILE", ""

    try:
        args = shlex.split(line)
    except ValueError as e:
        return line, "FAIL", f"parse error: {e}"
    if not args:
        return line, "SKIP_NO_FILE", ""

    # Only $CHANGED_FILES is expanded; other shell features (pipes, &&, globs)
    # are not, so we don't need bash on PATH. Wrap in `bash -c '...'` to opt in.
    if changed_files:
        args = [
            tok.replace("${CHANGED_FILES}", changed_files).replace("$CHANGED_FILES", changed_files)
            for tok in args
        ]
    try:
        result = subprocess.run(
            args,
            capture_output=True, text=True,
            timeout=PER_COMMAND_TIMEOUT, env=env,
        )
    except subprocess.TimeoutExpired:
        return line, "TIMEOUT", ""
    except FileNotFoundError:
        return line, "FAIL", f"command not found: {args[0]}"
    except OSError as e:
        return line, "FAIL", str(e)[:SNIPPET_LEN]
    if result.returncode == 0:
        return line, "PASS", ""
    snippet = ((result.stdout or "") + (result.stderr or ""))[:SNIPPET_LEN]
    return line, "FAIL", snippet


# How many .md entries currently live in the (cached or default) registry dir.
def registry_count(toplevel, registry_dir):
    reg = toplevel / registry_dir
    if not reg.is_dir():
        return 0
    try:
        return sum(1 for p in reg.iterdir() if p.is_file() and p.suffix == ".md")
    except OSError:
        return 0


DEFAULT_REGISTRY_DIR = "docs/debt"


# Read the cached registry-dir path; default if missing/empty.
def read_registry_dir(cache_dir):
    f = cache_dir / "registry-dir"
    if f.is_file():
        try:
            val = f.read_text(encoding="utf-8").strip()
            if val:
                return val
        except OSError:
            pass
    return DEFAULT_REGISTRY_DIR


# Appends one JSON line to metrics.jsonl in the cache dir; silent no-op on failure.
def log_metric(cache_dir, payload):
    if not cache_dir.is_dir():
        return
    payload["ts"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    try:
        with (cache_dir / "metrics.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(payload, separators=(",", ":")) + "\n")
    except OSError:
        pass


# Counts test-shaped filenames anywhere in the repo (test_*, *_test.*, *.test.*, *.spec.*).
def test_count(toplevel):
    try:
        n = 0
        for root, dirs, files in os.walk(toplevel):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            for f in files:
                if any(p.search(f) for p in TEST_PATTERNS):
                    n += 1
        return n
    except OSError:
        return None


def main():
    # Idle out cleanly if we're not in a git repo.
    toplevel = git_toplevel()
    if toplevel is None:
        return 0

    cache_dir = cache_base() / "cache" / repo_hash(toplevel)

    tool_name, changed = changed_file_from_stdin()
    # Copilot fires postToolUse on every tool; only edits concern us.
    if not changed:
        return 0

    env = os.environ.copy()
    env["CHANGED_FILES"] = changed

    registry_dir = read_registry_dir(cache_dir)

    # One line per edit — the dogfood tripwire signal (edits vs registry growth).
    log_metric(cache_dir, {
        "event": "edit",
        "file": changed,
        "registry_count": registry_count(toplevel, registry_dir),
    })

    # Nothing to run? Done.
    raw = read_commands(toplevel, cache_dir)
    commands = [
        line.rstrip()
        for line in raw.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    if not commands:
        return 0

    dpath = debug_path(cache_dir)
    dlog(dpath, "FIRE", f"changed={changed or '<none>'}", f"cmds={len(commands)}")

    def run_and_log(c):
        start = time.monotonic()
        cmd, status, snippet = run_one(c, changed, env)
        dlog(dpath, status, f"{time.monotonic() - start:.2f}s", cmd)
        return cmd, status, snippet

    # Run all commands in parallel; per-command 3s timeout enforces the budget.
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(commands)) as pool:
        results = list(pool.map(run_and_log, commands))

    # Log overall result so metrics can detect FAIL → PASS self-corrections.
    agg = "fail" if any(s in ("FAIL", "TIMEOUT") for _, s, _ in results) else "pass"
    log_metric(cache_dir, {"event": "feedback", "file": changed, "result": agg})

    # Format pass/fail/snippet per command for the agent-facing summary.
    summary_lines = []
    for cmd, status, snippet in results:
        if status == "FAIL" and snippet:
            summary_lines.append(f"{cmd}\tFAIL\t{snippet}")
        else:
            summary_lines.append(f"{cmd}\t{status}")
    summary = "\n".join(summary_lines)

    # Warn if this edit dropped the test-file count (Beck's "agent deletes tests" anti-pattern).
    warn = ""
    test_count_file = cache_dir / "test-count"
    now = test_count(toplevel)
    if now is not None and test_count_file.is_file():
        prev = None
        try:
            prev = int(test_count_file.read_text(encoding="utf-8").strip())
        except (OSError, ValueError):
            pass
        if prev is not None and now != prev:
            if now < prev:
                warn = f"WARNING: this edit removed {prev - now} test file(s) (was {prev}, now {now})."
            try:
                test_count_file.write_text(str(now), encoding="utf-8")
            except OSError:
                pass

    if not summary and not warn:
        return 0

    parts = []
    if summary:
        parts.append(f"debt-ops feedback (3s budget per command):\n{summary}")
    if warn:
        parts.append(warn)
    emit("\n\n".join(parts))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        # A bug here must never block the tool cycle.
        sys.exit(0)
