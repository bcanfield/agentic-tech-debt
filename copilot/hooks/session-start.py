#!/usr/bin/env python3
"""debt-ops Copilot sessionStart hook: silent path detection + session metric.

Copilot adapter. Copilot's sessionStart *command* hooks cannot inject context
(only `prompt`-type hooks can), so — unlike the Claude adapter — this does NOT
inject the disciplines. On Copilot the disciplines live in the charter
(.github/copilot-instructions.md / AGENTS.md), written by debt-ops-init and
auto-loaded by Copilot. This hook only does the side-effects the other pieces
rely on: probe + cache the ADR/registry directories and log one session metric.

Path-probe logic is kept identical to the Claude adapter's session-start.py so
the planned _common.py extraction (packaging plan Phase E) is a clean lift.
"""

import hashlib
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

ADR_CANDIDATE_PATHS = (
    "doc/adr", "docs/adr", "doc/adrs", "docs/adrs",
    "adr", "adrs",
    "architecture/decisions", "docs/architecture/decisions", "doc/architecture/decisions",
)
REGISTRY_CANDIDATE_PATHS = (
    "docs/debt", "docs/registry", "doc/debt",
    "debt/registry", "tech-debt/registry", "debt-registry", "registry",
)
ADR_FILENAME_RE = re.compile(r"^\d+[-_].*\.md$", re.IGNORECASE)
DEFAULT_ADR_DIR = "docs/adr"
DEFAULT_REGISTRY_DIR = "docs/debt"


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


def cache_base():
    override = os.environ.get("DEBT_OPS_CACHE")
    return Path(override) if override else (Path.home() / ".cache" / "debt-ops")


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


def main():
    toplevel = git_toplevel()
    if toplevel is None:
        return 0

    cache_dir = cache_base() / "cache" / repo_hash(toplevel)
    try:
        cache_dir.mkdir(parents=True, exist_ok=True)
    except OSError:
        return 0  # read-only cache: nothing to warm, idle clean

    adr_cache = cache_dir / "adr-dir"
    registry_cache = cache_dir / "registry-dir"

    adr_dir = read_cached_dir(adr_cache, toplevel)
    if adr_dir is None:
        probed = probe_adr_dir(toplevel)
        if probed:
            adr_dir = probed
            write_cached_dir(adr_cache, probed)

    registry_dir = read_cached_dir(registry_cache, toplevel)
    if registry_dir is None:
        probed = probe_registry_dir(toplevel)
        if probed:
            registry_dir = probed
            write_cached_dir(registry_cache, probed)

    effective_adr_dir = adr_dir or DEFAULT_ADR_DIR
    effective_registry_dir = registry_dir or DEFAULT_REGISTRY_DIR

    log_metric(cache_dir, {
        "event": "session",
        "registry_count": md_count(toplevel / effective_registry_dir),
        "adr_count": md_count(toplevel / effective_adr_dir),
        "ai_authored_count": ai_authored_count(toplevel / effective_registry_dir),
        "adr_dir": effective_adr_dir,
        "registry_dir": effective_registry_dir,
    })
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
