#!/usr/bin/env python3
"""debt-ops disable toggle: flip the per-repo disable sentinel (ADR 0020).

Writes (or removes) a `disabled` marker in this repo's plugin cache dir. While
the marker is present every hook idles silently — no session inject, no
write-time feedback, no stop nudge. Nothing is written to the working tree.

With no argument it toggles; pass `disable` or `enable` to force a direction.
"""

import argparse
import hashlib
import os
import subprocess
import sys
from pathlib import Path


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


# Single deterministic cache base, shared with the hooks (override DEBT_OPS_CACHE).
def cache_base():
    override = os.environ.get("DEBT_OPS_CACHE")
    return Path(override) if override else (Path.home() / ".cache" / "debt-ops")


def parse_args():
    p = argparse.ArgumentParser(description="Toggle debt-ops for this repo.")
    p.add_argument("action", nargs="?", choices=["disable", "enable"],
                   help="force a direction; omit to toggle")
    return p.parse_args()


def main():
    args = parse_args()

    toplevel = git_toplevel()
    if toplevel is None:
        sys.stderr.write("debt-ops: not in a git repo\n")
        return 2

    cache_dir = cache_base() / "cache" / repo_hash(toplevel)
    sentinel = cache_dir / "disabled"
    currently_disabled = sentinel.is_file()

    if args.action == "disable":
        want_disabled = True
    elif args.action == "enable":
        want_disabled = False
    else:
        want_disabled = not currently_disabled

    if want_disabled:
        try:
            cache_dir.mkdir(parents=True, exist_ok=True)
            sentinel.write_text("", encoding="utf-8")
        except OSError as e:
            sys.stderr.write(f"debt-ops: could not disable: {e}\n")
            return 1
        sys.stdout.write("debt-ops disabled for this repo (run again to re-enable).\n")
    else:
        try:
            sentinel.unlink(missing_ok=True)
        except OSError as e:
            sys.stderr.write(f"debt-ops: could not re-enable: {e}\n")
            return 1
        sys.stdout.write("debt-ops re-enabled for this repo.\n")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        sys.stderr.write(f"debt-ops disable: {e}\n")
        sys.exit(1)
