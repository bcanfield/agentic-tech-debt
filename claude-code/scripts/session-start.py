#!/usr/bin/env python3
"""debt-ops SessionStart hook: emit disciplines + (charter | cache | discovery prompt).

Path adaptivity: cheap Python probe of common ADR/registry conventions on first
session, cached at <cache>/adr-dir and <cache>/registry-dir. If the probe finds
no existing ADR directory, the inject asks Claude to detect it semantically and
write the path itself — same pattern as the quality-commands detection below.
"""

import hashlib
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

CHARTER_MARKER = "<!-- debt-ops:feedback v1 -->"
MANIFEST_FILES = ("Cargo.toml", "package.json", "pyproject.toml", "Makefile", "go.mod", "Gemfile")

ADR_CANDIDATE_PATHS = (
    "doc/adr", "docs/adr", "doc/adrs", "docs/adrs",
    "adr", "adrs",
    "architecture/decisions", "docs/architecture/decisions", "doc/architecture/decisions",
)

REGISTRY_CANDIDATE_PATHS = (
    "debt/registry", "tech-debt/registry", "debt-registry", "registry",
)

ADR_FILENAME_RE = re.compile(r"^\d+[-_].*\.md$", re.IGNORECASE)
DEFAULT_ADR_DIR = "doc/adr"
DEFAULT_REGISTRY_DIR = "debt/registry"


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


def md_count(dir_path):
    if not dir_path.is_dir():
        return 0
    try:
        return sum(1 for p in dir_path.iterdir() if p.is_file() and p.suffix == ".md")
    except OSError:
        return 0


def ai_authored_count(registry_dir):
    if not registry_dir.is_dir():
        return 0
    n = 0
    try:
        for p in registry_dir.iterdir():
            if p.is_file() and p.suffix == ".md":
                try:
                    if "ai_authored: true" in p.read_text(encoding="utf-8", errors="replace"):
                        n += 1
                except OSError:
                    pass
    except OSError:
        return 0
    return n


def log_metric(cache_dir, payload):
    if not cache_dir.is_dir():
        return
    payload["ts"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    try:
        with (cache_dir / "metrics.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(payload, separators=(",", ":")) + "\n")
    except OSError:
        pass


def has_charter(toplevel):
    claude_md = toplevel / "CLAUDE.md"
    if not claude_md.is_file():
        return False
    try:
        return CHARTER_MARKER in claude_md.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False


# Read a cached relative path. Returns the string if the cache file exists,
# its content is non-empty, AND the path still resolves to a real directory
# under toplevel. Otherwise None — triggers re-detection.
def read_cached_dir(cache_file, toplevel):
    if not cache_file.is_file():
        return None
    try:
        rel = cache_file.read_text(encoding="utf-8").strip()
    except OSError:
        return None
    if not rel:
        return None
    if not (toplevel / rel).is_dir():
        return None
    return rel


def write_cached_dir(cache_file, rel_path):
    try:
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        cache_file.write_text(rel_path, encoding="utf-8")
    except OSError:
        pass


# Look for any ADR-shaped file (numbered-prefix .md) in known convention dirs.
# Returns the relative path or None if no convention matches with content.
def probe_adr_dir(toplevel):
    for rel in ADR_CANDIDATE_PATHS:
        p = toplevel / rel
        if not p.is_dir():
            continue
        try:
            for f in p.iterdir():
                if f.is_file() and ADR_FILENAME_RE.match(f.name):
                    return rel
        except OSError:
            pass
    return None


# Look for an existing registry dir with any .md content. Less variable than
# ADRs (plugin owns the convention), so we just check known shapes and fall
# back to the default.
def probe_registry_dir(toplevel):
    for rel in REGISTRY_CANDIDATE_PATHS:
        p = toplevel / rel
        if not p.is_dir():
            continue
        try:
            if any(f.is_file() and f.suffix == ".md" for f in p.iterdir()):
                return rel
        except OSError:
            pass
    return None


# Asks Claude to find the ADR directory semantically. Same pattern as the
# quality-commands first-session detection — silent, writes the result to a
# cache file the other hooks read.
def adr_detection_instruction(cache_dir):
    return (
        "ADR directory: not detected by quick probe. Please find it silently — no announcement:\n"
        "1. Scan this repo for any directory containing markdown files that look like ADRs: "
        "filenames matching `NNNN-title.md` / `NNN-title.md`, or bodies with Nygard sections "
        "(`## Status`, `## Context`, `## Decision`, `## Consequences`).\n"
        "2. Common conventions include `doc/adr`, `docs/adr`, `adr`, `architecture/decisions`, "
        "but accept any directory that matches the shape — including non-standard ones.\n"
        f"3. If found, write the repo-relative path to {cache_dir}/adr-dir on a single line.\n"
        f"4. If genuinely no ADRs exist yet, write `{DEFAULT_ADR_DIR}` to {cache_dir}/adr-dir — "
        "Discipline 2 will create it on first use."
    )


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


# Substitutes the detected paths into the disciplines text. Discipline 2 names
# the ADR dir Claude should write new ADRs into; Discipline 3 names the
# registry to read before editing referenced files.
def disciplines_text(adr_dir, registry_dir):
    return (
        '1. If you defer work — decision unmade, stub, loosened type, "future"/"later" comment, or '
        '`TODO`/`FIXME`/`HACK`/`XXX` marker — register via /debt-ops:add immediately. Test: would a '
        'future reader ask "why this way?" If yes, register. No prompt. Use `payoff_trigger: unknown` '
        'if unsure. The helper prints one line: `+1 entry: <slug> (<letter>)` — don\'t paraphrase or '
        'add commentary. Over-register freely; the developer drops with `drop A`, `drop A,C`, '
        '`drop all`, or `drop <slug>`.\n\n'
        '2. When making an architecturally significant change — a data model, public interface, '
        'security boundary, release pipeline, or a dep-manifest change that is a major-version bump '
        f'or a *new* top-level dependency — draft an ADR under {adr_dir}/ in Nygard format (Context, '
        'Decision, Consequences, Alternatives, Payoff trigger). Create the directory if needed. Only '
        'draft an ADR when there are two credible alternatives; if you cannot list two, it is a '
        'comment, not an ADR. If the ADR introduces deliberate debt, also call /debt-ops:add so the '
        'registry entry mirrors the ADR.\n\n'
        f'3. Read entries under {registry_dir}/ before changing files they reference.'
    )


def main():
    toplevel = git_toplevel()
    if toplevel is None:
        emit("debt-ops: not a git repo, plugin idle this session")
        return 0

    cache_base = Path(os.environ.get("CLAUDE_PLUGIN_DATA") or (Path.home() / ".cache" / "debt-ops"))
    cache_dir = cache_base / "cache" / repo_hash(toplevel)
    stateless = False
    try:
        cache_dir.mkdir(parents=True, exist_ok=True)
    except OSError:
        stateless = True

    # Resolve ADR and registry paths: cached → probe → default. ADR may end
    # up unresolved here (None) — in that case the inject below asks Claude
    # to fill in <cache>/adr-dir semantically.
    adr_cache = cache_dir / "adr-dir"
    registry_cache = cache_dir / "registry-dir"

    adr_dir = read_cached_dir(adr_cache, toplevel)
    if adr_dir is None:
        probed = probe_adr_dir(toplevel)
        if probed:
            adr_dir = probed
            if not stateless:
                write_cached_dir(adr_cache, probed)

    registry_dir = read_cached_dir(registry_cache, toplevel)
    if registry_dir is None:
        probed = probe_registry_dir(toplevel) or DEFAULT_REGISTRY_DIR
        registry_dir = probed
        if not stateless:
            write_cached_dir(registry_cache, probed)

    effective_adr_dir = adr_dir or DEFAULT_ADR_DIR

    log_metric(cache_dir, {
        "event": "session",
        "registry_count": md_count(toplevel / registry_dir),
        "adr_count": md_count(toplevel / effective_adr_dir),
        "ai_authored_count": ai_authored_count(toplevel / registry_dir),
        "adr_dir": effective_adr_dir,
        "registry_dir": registry_dir,
    })

    context = (
        "Tech-debt-operations disciplines (debt-ops plugin):\n\n"
        f"{disciplines_text(effective_adr_dir, registry_dir)}\n\n"
        f"{commands_block(cache_dir, cache_base, manifest_hash(toplevel), has_charter(toplevel), stateless)}"
    )
    if adr_dir is None and not stateless:
        context += "\n\n" + adr_detection_instruction(cache_dir)
    if not stateless:
        context += (
            f"\n\nDebug: set DEBT_OPS_DEBUG=1 in the environment to log every hook fire "
            f"and command result to {cache_dir}/debug.log (tab-separated; tail -f to watch)."
        )
    emit(context)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
