#!/usr/bin/env python3
"""debt-ops Stop hook: TODO-sniff safety net for Discipline 1.

Fires at the end of every turn. Counts newly-added marker lines
(TODO/FIXME/HACK/XXX) in the working tree vs newly-added entries
under `debt/registry/`. If markers > registrations, nudges Claude
on the next turn via additionalContext.

Tripwire, not precision: false positives are cheap (the dev drops
spurious entries with "drop it"); false negatives defeat the point.
"""

import hashlib
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

DEBUG_ENV = "DEBT_OPS_DEBUG"
MARKER_RE = re.compile(r"\b(TODO|FIXME|HACK|XXX)\b")
# Excluded paths: plugin artifacts (registry, ADRs) and the plugin's own
# source — `claude-code/` mentions the markers as documentation prose, not
# as code deferrals, and would tripwire on every plugin-dev edit.
EXCLUDED_PREFIXES = ("debt/registry/", "doc/adr/", "claude-code/")
MAX_UNTRACKED_BYTES = 1_000_000


# Emit a block decision. Claude Code's Stop-hook schema doesn't support
# additionalContext; `decision: "block"` + `reason` is the documented way
# to make Claude continue working on the supplied message before stopping.
def emit(reason):
    payload = {
        "decision": "block",
        "reason": reason,
    }
    sys.stdout.write(json.dumps(payload) + "\n")


# Resolve repo root; returns None outside a git repo so we idle cleanly.
def git_toplevel():
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, check=True, timeout=2,
        )
        s = out.stdout.strip()
        return Path(s) if s else None
    except (subprocess.SubprocessError, FileNotFoundError):
        return None


def repo_hash(toplevel):
    return hashlib.sha1(str(toplevel).encode()).hexdigest()[:12]


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
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as f:
            f.write("\t".join((ts,) + fields) + "\n")
    except OSError:
        pass


# True if the file path is excluded from marker counting.
def is_excluded(path):
    return any(path.startswith(p) for p in EXCLUDED_PREFIXES)


# Counts marker hits in `+` lines from `git diff HEAD` (modified-tracked files).
def markers_in_diff(toplevel):
    try:
        out = subprocess.run(
            ["git", "diff", "HEAD", "--", "."],
            cwd=toplevel,
            capture_output=True, text=True, timeout=2,
        )
    except (subprocess.SubprocessError, FileNotFoundError):
        return 0
    # rc 0 = no diff or success; rc 1 from git diff also signals "differences found" in some contexts.
    if out.returncode not in (0, 1):
        return 0
    n = 0
    current_path = None
    for line in out.stdout.splitlines():
        if line.startswith("+++ b/"):
            p = line[6:]
            current_path = None if p == "/dev/null" else p
            continue
        if line.startswith("+++"):
            current_path = None
            continue
        if not line.startswith("+"):
            continue
        if current_path is None or is_excluded(current_path):
            continue
        if MARKER_RE.search(line):
            n += 1
    return n


# Counts marker hits in untracked files (whole file = new lines).
def markers_in_untracked(toplevel):
    try:
        out = subprocess.run(
            ["git", "ls-files", "-o", "--exclude-standard"],
            cwd=toplevel,
            capture_output=True, text=True, timeout=2,
        )
    except (subprocess.SubprocessError, FileNotFoundError):
        return 0
    if out.returncode != 0:
        return 0
    n = 0
    for path in out.stdout.splitlines():
        if is_excluded(path):
            continue
        full = toplevel / path
        try:
            if not full.is_file() or full.stat().st_size > MAX_UNTRACKED_BYTES:
                continue
            text = full.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for line in text.splitlines():
            if MARKER_RE.search(line):
                n += 1
    return n


# True if this turn produced any tracked-or-untracked file change outside
# the excluded paths (registry/ADR). Used to gate stage-2 broad-judgment
# blocks so we don't fire on no-op turns or doc-only edits.
def has_code_changes(toplevel):
    try:
        out = subprocess.run(
            ["git", "diff", "--name-only", "HEAD"],
            cwd=toplevel,
            capture_output=True, text=True, timeout=2,
        )
    except (subprocess.SubprocessError, FileNotFoundError):
        out = None
    if out and out.returncode in (0, 1):
        for path in out.stdout.splitlines():
            if path.strip() and not is_excluded(path):
                return True
    try:
        out2 = subprocess.run(
            ["git", "ls-files", "-o", "--exclude-standard"],
            cwd=toplevel,
            capture_output=True, text=True, timeout=2,
        )
    except (subprocess.SubprocessError, FileNotFoundError):
        return False
    if out2.returncode == 0:
        for path in out2.stdout.splitlines():
            if path.strip() and not is_excluded(path):
                return True
    return False


# Fingerprint of the current decidable state. The Stop hook re-runs at the
# end of every assistant turn; without this, stages 1 and 2 would re-fire
# every turn on an unchanged pending diff and trap the agent in an
# "Acknowledged, no changes" loop until the user commits.
def state_fingerprint(toplevel, stage, markers, entries):
    h = hashlib.sha1()
    h.update(f"{stage}|{markers}|{entries}|".encode())
    try:
        out = subprocess.run(
            ["git", "diff", "HEAD"],
            cwd=toplevel, capture_output=True, text=True, timeout=2,
        )
        h.update(out.stdout.encode("utf-8", errors="replace"))
    except (subprocess.SubprocessError, FileNotFoundError):
        pass
    h.update(b"\x00")
    try:
        out = subprocess.run(
            ["git", "ls-files", "-o", "--exclude-standard"],
            cwd=toplevel, capture_output=True, text=True, timeout=2,
        )
        h.update(out.stdout.encode("utf-8", errors="replace"))
    except (subprocess.SubprocessError, FileNotFoundError):
        pass
    return h.hexdigest()


def already_nudged(state_path, fingerprint):
    try:
        return state_path.read_text(encoding="utf-8").strip() == fingerprint
    except OSError:
        return False


def record_nudge(state_path, fingerprint):
    try:
        state_path.parent.mkdir(parents=True, exist_ok=True)
        state_path.write_text(fingerprint, encoding="utf-8")
    except OSError:
        pass


# Counts new (untracked or staged-add) .md files under debt/registry/.
# Pathspec scopes the call so `--untracked-files=all` (needed to walk into
# fully-untracked debt/registry/ dirs) doesn't expand work over the whole repo.
def new_registry_entries(toplevel):
    try:
        out = subprocess.run(
            ["git", "status", "--porcelain", "--untracked-files=all", "--", "debt/registry/"],
            cwd=toplevel,
            capture_output=True, text=True, timeout=2,
        )
    except (subprocess.SubprocessError, FileNotFoundError):
        return 0
    if out.returncode != 0:
        return 0
    n = 0
    for line in out.stdout.splitlines():
        if len(line) < 4:
            continue
        status = line[:2]
        path = line[3:].strip()
        # Renames look like "R  oldname -> newname"; we want the new name.
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        # Strip git's quoting around paths with special chars.
        if path.startswith('"') and path.endswith('"'):
            path = path[1:-1]
        if not path.startswith("debt/registry/") or not path.endswith(".md"):
            continue
        # New = untracked (??) or any add in either status column.
        if status == "??" or "A" in status:
            n += 1
    return n


def main():
    # Drain stdin so the hook process exits cleanly even if the caller pipes a payload.
    try:
        sys.stdin.read()
    except OSError:
        pass

    toplevel = git_toplevel()
    if toplevel is None:
        return 0

    cache_base = Path(os.environ.get("CLAUDE_PLUGIN_DATA") or (Path.home() / ".cache" / "debt-ops"))
    cache_dir = cache_base / "cache" / repo_hash(toplevel)
    dpath = debug_path(cache_dir)
    state_path = cache_dir / "stop-state"

    markers = markers_in_diff(toplevel) + markers_in_untracked(toplevel)
    entries = new_registry_entries(toplevel)

    if markers > entries:
        # Stage 1: specific marker-count block.
        fp = state_fingerprint(toplevel, "stage1", markers, entries)
        if already_nudged(state_path, fp):
            dlog(dpath, "STOP", f"markers={markers}", f"new_registry={entries}", "stage=1", "skipped=dup")
            return 0
        record_nudge(state_path, fp)
        dlog(dpath, "STOP", f"markers={markers}", f"new_registry={entries}", "stage=1")
        delta = markers - entries
        reason = (
            f"debt-ops: this turn added {markers} new TODO/FIXME/HACK/XXX marker "
            f"line(s) but only {entries} new entry/entries under debt/registry/. "
            f"Before stopping, register the {delta} unregistered deferral(s) via "
            f"/debt-ops:add — one entry per marker. No prompt, no confirmation; "
            f"over-register freely (the developer drops spurious entries with "
            f"\"drop it\")."
        )
        emit(reason)
        return 0

    # Stage 2: no markers and no registrations, but code changed — let Claude
    # judge whether the diff contains broader Discipline 1 deferrals (stubs,
    # loosened types, swallowed errors, deferred-via-prose, mocked calls).
    if markers == 0 and entries == 0 and has_code_changes(toplevel):
        fp = state_fingerprint(toplevel, "stage2", markers, entries)
        if already_nudged(state_path, fp):
            dlog(dpath, "STOP", f"markers={markers}", f"new_registry={entries}", "stage=2", "skipped=dup")
            return 0
        record_nudge(state_path, fp)
        dlog(dpath, "STOP", f"markers={markers}", f"new_registry={entries}", "stage=2")
        reason = (
            "debt-ops: this turn changed code but registered no new entries under "
            "debt/registry/. Before stopping, review your diff and apply "
            "Discipline 1's full scope — register every deferral you introduced "
            "via /debt-ops:add. Discipline 1 is broader than explicit markers; "
            "common shapes (whatever syntax your language uses):\n"
            "  - Stubs and partial implementations (placeholder values, empty "
            "bodies, \"not implemented\" handlers)\n"
            "  - Loosened types or suppressed checks (untyped escapes, "
            "ignore/suppress directives)\n"
            "  - Skipped or disabled tests, guards, or validations\n"
            "  - Swallowed errors (empty exception handlers, ignored return "
            "codes, unhandled promises/futures)\n"
            "  - Decisions deferred via prose comments (\"for now\", "
            "\"later\", \"follow-up\", \"figure out\")\n"
            "  - Any other \"I'll come back to this\"\n"
            "Test: would a future reader ask \"why this "
            "way?\" If yes, register. Run /debt-ops:add for each — one entry "
            "per deferral. If you genuinely introduced no deferrals (pure "
            "refactor, rename, formatting), acknowledge that and continue. "
            "Over-register freely — the developer drops spurious entries "
            "with \"drop it\"."
        )
        emit(reason)
        return 0

    dlog(dpath, "STOP", f"markers={markers}", f"new_registry={entries}", "silent")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        # A hook bug must never block the tool cycle — exit clean.
        sys.exit(0)
