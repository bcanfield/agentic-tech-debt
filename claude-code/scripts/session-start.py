#!/usr/bin/env python3
"""debt-ops SessionStart hook: emit disciplines + (charter | cache | discovery prompt)."""

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

CHARTER_MARKER = "<!-- debt-ops:feedback v1 -->"
MANIFEST_FILES = ("Cargo.toml", "package.json", "pyproject.toml", "Makefile", "go.mod", "Gemfile")

DISCIPLINES = """1. If you write a `TODO`, `FIXME`, `HACK`, or `XXX` marker, register it via /debt-ops:add immediately. No permission prompt; just do it. Use `payoff_trigger: unknown` if unsure. Announce as one line: `+1 entry: <slug> (drop?)`. Treat over-registering as cheap; the developer can reply "drop it" and you'll delete the entry.

2. When making an architecturally significant change — a data model, public interface, security boundary, release pipeline, or a dep-manifest change that is a major-version bump or a *new* top-level dependency — draft an ADR under doc/adr/ in Nygard format (Context, Decision, Consequences, Alternatives, Payoff trigger). Create the directory if needed. Only draft an ADR when there are two credible alternatives; if you cannot list two, it is a comment, not an ADR. If the ADR introduces deliberate debt, also call /debt-ops:add so the registry entry mirrors the ADR.

3. Read entries under debt/registry/ before changing files they reference."""


def emit(context):
    payload = {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
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


def manifest_hash(toplevel):
    paths = [toplevel / n for n in MANIFEST_FILES if (toplevel / n).is_file()]
    if not paths:
        return "no-manifest"
    try:
        joined = "\n".join(f"{int(p.stat().st_mtime)} {p}" for p in paths)
    except OSError:
        return "stat-failed"
    return hashlib.sha1(joined.encode()).hexdigest()[:12]


def has_charter(toplevel):
    claude_md = toplevel / "CLAUDE.md"
    if not claude_md.is_file():
        return False
    try:
        return CHARTER_MARKER in claude_md.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False


def commands_block(cache_dir, cache_base, manifest, charter, stateless):
    if charter:
        return (
            f"Quality commands: read the CLAUDE.md section marked `{CHARTER_MARKER}`. "
            "CLAUDE.md is the source of truth when present."
        )
    if stateless:
        return (
            f"debt-ops: cache disabled (read-only {cache_base}). "
            "For this session, detect quality commands once and run them yourself under timeout 3."
        )
    list_file = cache_dir / "feedback.list"
    hash_file = cache_dir / "manifest.hash"
    cached = ""
    if hash_file.is_file():
        try:
            cached = hash_file.read_text(encoding="utf-8").strip()
        except OSError:
            pass
    if list_file.is_file() and cached == manifest:
        try:
            return (
                "Cached quality commands (one per line; comment lines are estimates):\n"
                + list_file.read_text(encoding="utf-8")
            )
        except OSError:
            pass
    return (
        "First session for this repo (or manifest changed). Please do the following silently — no need to announce:\n\n"
        "1. Detect this project's quality commands by scanning manifest files (Cargo.toml, package.json, pyproject.toml, Makefile, go.mod, Gemfile) and tool-specific config (eslint, biome, ruff, mypy, tsconfig, etc.).\n"
        "2. Prefer commands that accept a changed-file or changed-package argument (e.g., `eslint $CHANGED_FILES`, `cargo clippy --no-deps -p $CHANGED_PACKAGE`, `pytest path/to/dir`) over project-wide ones.\n"
        "3. Reject any command whose typical wall-clock on this repo exceeds 3 seconds. Project-wide commands almost always exceed this on non-trivial repos.\n"
        f"4. Write to {cache_dir}/feedback.list. Format: one command per line, with the wall-clock estimate as a preceding comment, e.g.:\n"
        "   # est ~0.8s — fast type check\n"
        "   tsc --noEmit -p tsconfig.json\n"
        "   Comments (#) and empty lines are skipped when feedback.py reads the file.\n"
        f"5. Write the manifest hash to {cache_dir}/manifest.hash with this exact value: {manifest}\n"
        f"6. Count test-shaped filenames in the repo (filenames matching test_*, *_test.*, *.test.*, or *.spec.*) and write the integer count to {cache_dir}/test-count. feedback.py recomputes this on every edit and warns when it drops."
    )


def main():
    toplevel = git_toplevel()
    if toplevel is None:
        # The naive "$cwd | shasum" key would collide across every non-git dir; idle out instead.
        emit("debt-ops: not a git repo, plugin idle this session")
        return 0

    cache_base = Path(os.environ.get("CLAUDE_PLUGIN_DATA") or (Path.home() / ".cache" / "debt-ops"))
    cache_dir = cache_base / "cache" / repo_hash(toplevel)
    stateless = False
    try:
        cache_dir.mkdir(parents=True, exist_ok=True)
    except OSError:
        stateless = True

    context = (
        "Tech-debt-operations disciplines (debt-ops plugin):\n\n"
        f"{DISCIPLINES}\n\n"
        f"{commands_block(cache_dir, cache_base, manifest_hash(toplevel), has_charter(toplevel), stateless)}"
    )
    emit(context)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
