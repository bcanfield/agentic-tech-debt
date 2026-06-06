"""Shared helpers for the debt-ops hook/manifest test suite.

The hooks are pure I/O contracts: a JSON payload on stdin -> a JSON envelope on
stdout + filesystem side effects under DEBT_OPS_CACHE. We exercise them by
spawning the real script (faithful to how each host runs it), not by import.

Stdlib only (json/subprocess/tempfile) so this runs on the same Pythons the
hooks target, including Windows without extra deps.
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Adapters that ship hooks. (portable skills/ has no hooks.)
HOOK_ADAPTERS = ("claude-code", "codex", "copilot")

# Copilot runs hooks with cwd = the plugin dir and passes the project as the
# payload's `cwd`; claude/codex run hooks in the project dir (ADR 0019). So the
# copilot hooks must be exercised from a non-repo cwd to be meaningful.
RUNS_IN_PROJECT_CWD = {"claude-code": True, "codex": True, "copilot": False}


def hook_path(adapter, name):
    return REPO_ROOT / adapter / "hooks" / f"{name}.py"


def has_hook(adapter, name):
    return hook_path(adapter, name).is_file()


def make_git_repo(tmp):
    """Init a throwaway git repo under tmp and return its path."""
    repo = Path(tempfile.mkdtemp(dir=tmp, prefix="repo-"))
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "t@t.t")
    _git(repo, "config", "user.name", "t")
    return repo


def _git(repo, *args):
    subprocess.run(["git", *args], cwd=str(repo), check=True,
                   capture_output=True, text=True)


def write_charter(repo, commands="echo CANARY_OK"):
    """Write the feedback marker block into every charter file an adapter reads,
    so each finds its commands regardless of which file it prefers."""
    block = (
        "# Test project\n\n## Tech debt operations\n\n"
        f"<!-- debt-ops:feedback v1 -->\n{commands}\n<!-- /debt-ops:feedback -->\n"
    )
    for rel in ("CLAUDE.md", "AGENTS.md", ".github/copilot-instructions.md"):
        p = repo / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(block, encoding="utf-8")


def write_prose_charter(repo):
    """Charter files that only MENTION the feedback marker inline in prose —
    no real block. Regression fixture for the prose-as-commands bug."""
    block = (
        "# Test project\n\n## Conventions\n\n"
        "- Feedback marker `<!-- debt-ops:feedback v1 -->` — appears in every adapter\n"
        "- prose lines that must never run as shell commands\n"
    )
    for rel in ("CLAUDE.md", "AGENTS.md", ".github/copilot-instructions.md"):
        p = repo / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(block, encoding="utf-8")


def run_hook(adapter, name, payload, *, repo, cache, run_cwd=None, env=None):
    """Spawn a hook script with `payload` on stdin. Returns CompletedProcess.

    run_cwd defaults to the project for claude/codex and a non-repo dir for
    copilot (mirroring how each host invokes hooks). DEBT_OPS_CACHE/_DEBUG are
    set so side effects land in an isolated, inspectable cache.
    """
    if run_cwd is None:
        run_cwd = repo if RUNS_IN_PROJECT_CWD[adapter] else cache  # cache dir is not a git repo
    e = dict(os.environ)
    # Adapters differ on cache base: claude-code reads CLAUDE_PLUGIN_DATA,
    # codex/copilot read DEBT_OPS_CACHE (ADR 0012). Point both at the isolated
    # dir so each picks up whichever it uses.
    e["DEBT_OPS_CACHE"] = str(cache)
    e["CLAUDE_PLUGIN_DATA"] = str(cache)
    e["DEBT_OPS_DEBUG"] = "1"
    if env:
        e.update(env)
    return subprocess.run(
        [sys.executable, str(hook_path(adapter, name))],
        input=json.dumps(payload), text=True, capture_output=True,
        cwd=str(run_cwd), env=e, timeout=30,
    )


def feedback_payload(adapter, repo, filename="note.txt"):
    """A postToolUse/edit payload in each host's envelope shape (validated live)."""
    if adapter == "claude-code":
        return {"tool_name": "Edit", "tool_input": {"file_path": filename},
                "tool_response": {"success": True}}
    if adapter == "codex":
        # Codex edits via apply_patch; the path lives in the V4A patch body.
        patch = (f"*** Begin Patch\n*** Update File: {filename}\n@@\n"
                 f"-old\n+new\n*** End Patch")
        return {"tool_name": "apply_patch", "tool_input": {"command": patch}}
    if adapter == "copilot":
        return {"toolName": "create",
                "toolArgs": json.dumps({"path": str(repo / filename)}),
                "toolResult": {"resultType": "success",
                               "textResultForLlm": "created"},
                "cwd": str(repo)}
    raise ValueError(adapter)


def session_start_payload(adapter, repo):
    # Only copilot reads stdin (for cwd); claude/codex ignore it but it's harmless.
    return {"sessionId": "test", "cwd": str(repo), "source": "startup"}


def stop_payload(adapter, repo):
    if adapter == "copilot":
        return {"sessionId": "test", "stopReason": "end_turn", "cwd": str(repo)}
    return {"session_id": "test", "cwd": str(repo)}


def read_metrics(cache):
    """Parse every metrics.jsonl event written under the cache. [] if none."""
    base = Path(cache) / "cache"
    if not base.is_dir():
        return []
    events = []
    for m in base.glob("*/metrics.jsonl"):
        for line in m.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                events.append(json.loads(line))
    return events
