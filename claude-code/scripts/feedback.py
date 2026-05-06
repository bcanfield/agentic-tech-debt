#!/usr/bin/env python3
"""debt-ops PostToolUse hook: run quality commands in parallel under a 3s budget."""

import concurrent.futures
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

MARKER_OPEN = "<!-- debt-ops:feedback v1 -->"
MARKER_CLOSE = "<!-- /debt-ops:feedback -->"
PER_COMMAND_TIMEOUT = 3
SNIPPET_LEN = 200
SKIP_DIRS = {".git", "node_modules", "target", "dist", "build"}
TEST_PATTERNS = (
    re.compile(r"^test_"),
    re.compile(r"_test\."),
    re.compile(r"\.test\."),
    re.compile(r"\.spec\."),
)
HEADING_RE = re.compile(r"^##\s")


def emit(context):
    payload = {
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": context,
        }
    }
    sys.stdout.write(json.dumps(payload) + "\n")


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


def repo_hash(toplevel):
    return hashlib.sha1(str(toplevel).encode()).hexdigest()[:12]


def changed_file_from_stdin():
    try:
        raw = sys.stdin.read()
    except OSError:
        return ""
    if not raw:
        return ""
    try:
        data = json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        return ""
    return (data.get("tool_input") or {}).get("file_path") or ""


def read_commands(toplevel, cache_dir):
    claude_md = toplevel / "CLAUDE.md"
    if claude_md.is_file():
        try:
            text = claude_md.read_text(encoding="utf-8", errors="replace")
        except OSError:
            text = ""
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


def run_one(line, env):
    if "$CHANGED_FILES" in line and not env.get("CHANGED_FILES"):
        return line, "SKIP_NO_FILE", ""
    try:
        result = subprocess.run(
            ["bash", "-c", line],
            capture_output=True, text=True,
            timeout=PER_COMMAND_TIMEOUT, env=env,
        )
    except subprocess.TimeoutExpired:
        return line, "TIMEOUT", ""
    except (OSError, FileNotFoundError):
        return line, "FAIL", "could not invoke bash"
    if result.returncode == 0:
        return line, "PASS", ""
    snippet = ((result.stdout or "") + (result.stderr or ""))[:SNIPPET_LEN]
    return line, "FAIL", snippet


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
    toplevel = git_toplevel()
    if toplevel is None:
        return 0

    cache_base = Path(os.environ.get("CLAUDE_PLUGIN_DATA") or (Path.home() / ".cache" / "debt-ops"))
    cache_dir = cache_base / "cache" / repo_hash(toplevel)

    env = os.environ.copy()
    env["CHANGED_FILES"] = changed_file_from_stdin()

    raw = read_commands(toplevel, cache_dir)
    commands = [
        line.rstrip()
        for line in raw.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    if not commands:
        return 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=len(commands)) as pool:
        results = list(pool.map(lambda c: run_one(c, env), commands))

    summary_lines = []
    for cmd, status, snippet in results:
        if status == "FAIL" and snippet:
            summary_lines.append(f"{cmd}\tFAIL\t{snippet}")
        else:
            summary_lines.append(f"{cmd}\t{status}")
    summary = "\n".join(summary_lines)

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
