"""Hook I/O contract tests across every adapter that ships hooks.

Each test runs the real script with a host-shaped payload and asserts the output
envelope + cache side effects. The copilot cases run from a non-repo cwd, so
they double as the regression guard for the ADR 0019 cwd bug.
"""

import json
import tempfile
import unittest
from pathlib import Path

import helpers as h


def feedback_context(adapter, stdout):
    """Pull the feedback text out of whichever envelope the adapter emits."""
    obj = json.loads(stdout)
    if adapter == "copilot":
        if "modifiedResult" in obj:
            return obj["modifiedResult"]["textResultForLlm"]
        return obj.get("additionalContext", "")
    return obj["hookSpecificOutput"]["additionalContext"]


class HookTestBase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.mkdtemp(prefix="debtops-")
        self.tmp = Path(self._tmp)

    def tearDown(self):
        import shutil
        shutil.rmtree(self._tmp, ignore_errors=True)

    def fresh(self):
        """A fresh (repo, cache) pair under this test's temp dir."""
        repo = h.make_git_repo(self.tmp)
        cache = Path(tempfile.mkdtemp(dir=self.tmp, prefix="cache-"))
        return repo, cache


class TestFeedback(HookTestBase):
    def test_passing_command_reported_pass(self):
        for adapter in h.HOOK_ADAPTERS:
            with self.subTest(adapter=adapter):
                repo, cache = self.fresh()
                h.write_charter(repo, "echo CANARY_OK")
                (repo / "note.txt").write_text("x", encoding="utf-8")
                p = h.run_hook(adapter, "feedback",
                               h.feedback_payload(adapter, repo),
                               repo=repo, cache=cache)
                self.assertEqual(p.returncode, 0, p.stderr)
                ctx = feedback_context(adapter, p.stdout)
                self.assertIn("PASS", ctx)
                self.assertNotIn("FAIL", ctx)

    def test_failing_command_reported_fail(self):
        for adapter in h.HOOK_ADAPTERS:
            with self.subTest(adapter=adapter):
                repo, cache = self.fresh()
                h.write_charter(repo, "false")
                (repo / "note.txt").write_text("x", encoding="utf-8")
                p = h.run_hook(adapter, "feedback",
                               h.feedback_payload(adapter, repo),
                               repo=repo, cache=cache)
                self.assertEqual(p.returncode, 0, p.stderr)
                self.assertIn("FAIL", feedback_context(adapter, p.stdout))

    def test_prose_marker_mention_not_executed(self):
        # Regression: a charter that only MENTIONS the marker inline in prose
        # must not have the surrounding prose executed as shell commands.
        for adapter in h.HOOK_ADAPTERS:
            with self.subTest(adapter=adapter):
                repo, cache = self.fresh()
                h.write_prose_charter(repo)
                (repo / "note.txt").write_text("x", encoding="utf-8")
                p = h.run_hook(adapter, "feedback",
                               h.feedback_payload(adapter, repo),
                               repo=repo, cache=cache)
                self.assertEqual(p.returncode, 0, p.stderr)
                if p.stdout.strip():
                    ctx = feedback_context(adapter, p.stdout)
                    self.assertNotIn("FAIL", ctx)
                    self.assertNotIn("command not found", ctx)

    def test_prose_mention_falls_back_to_cached_list(self):
        # The prose mention must not short-circuit the cached-command fallback.
        for adapter in h.HOOK_ADAPTERS:
            with self.subTest(adapter=adapter):
                repo, cache = self.fresh()
                h.write_prose_charter(repo)
                (repo / "note.txt").write_text("x", encoding="utf-8")
                h.run_hook(adapter, "session-start",
                           h.session_start_payload(adapter, repo),
                           repo=repo, cache=cache)
                for d in (cache / "cache").iterdir():
                    (d / "feedback.list").write_text("echo CANARY_OK\n",
                                                     encoding="utf-8")
                p = h.run_hook(adapter, "feedback",
                               h.feedback_payload(adapter, repo),
                               repo=repo, cache=cache)
                self.assertEqual(p.returncode, 0, p.stderr)
                self.assertIn("PASS", feedback_context(adapter, p.stdout))

    def test_non_edit_tool_is_ignored(self):
        # Only copilot fires postToolUse on every tool, so it must self-filter.
        repo, cache = self.fresh()
        h.write_charter(repo)
        payload = {"toolName": "report_intent",
                   "toolArgs": json.dumps({"intent": "thinking"}),
                   "toolResult": {"resultType": "success",
                                  "textResultForLlm": "ok"},
                   "cwd": str(repo)}
        p = h.run_hook("copilot", "feedback", payload, repo=repo, cache=cache)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(p.stdout.strip(), "")  # idled, no envelope


class TestSessionStart(HookTestBase):
    def test_writes_cache_and_session_metric(self):
        for adapter in h.HOOK_ADAPTERS:
            with self.subTest(adapter=adapter):
                repo, cache = self.fresh()
                p = h.run_hook(adapter, "session-start",
                               h.session_start_payload(adapter, repo),
                               repo=repo, cache=cache)
                self.assertEqual(p.returncode, 0, p.stderr)
                events = h.read_metrics(cache)
                self.assertTrue(
                    any(e.get("event") == "session" for e in events),
                    f"{adapter}: no session metric written (cache={list((cache/'cache').glob('*')) if (cache/'cache').is_dir() else 'absent'})",
                )

    def test_prose_marker_mention_is_not_a_charter(self):
        # claude-code + codex check the charter file for the marker; an inline
        # prose mention must read as "no charter" (copilot has no charter check).
        for adapter in ("claude-code", "codex"):
            with self.subTest(adapter=adapter):
                repo, cache = self.fresh()
                h.write_prose_charter(repo)
                p = h.run_hook(adapter, "session-start",
                               h.session_start_payload(adapter, repo),
                               repo=repo, cache=cache)
                self.assertEqual(p.returncode, 0, p.stderr)
                self.assertNotIn("Quality commands: read the", p.stdout)


class TestStop(HookTestBase):
    def test_blocks_on_unregistered_change(self):
        # Code changed (untracked file) + empty registry -> nudge to register.
        for adapter in h.HOOK_ADAPTERS:
            with self.subTest(adapter=adapter):
                repo, cache = self.fresh()
                (repo / "feature.py").write_text("def f():\n    pass\n",
                                                 encoding="utf-8")
                p = h.run_hook(adapter, "stop",
                               h.stop_payload(adapter, repo),
                               repo=repo, cache=cache)
                self.assertEqual(p.returncode, 0, p.stderr)
                obj = json.loads(p.stdout)
                self.assertEqual(obj.get("decision"), "block")
                self.assertTrue(obj.get("reason"))


    def test_markdown_todo_prose_does_not_block(self):
        # Regression: marker words in prose docs are mentions, not debt (ADR 0020).
        for adapter in h.HOOK_ADAPTERS:
            with self.subTest(adapter=adapter):
                repo, cache = self.fresh()
                docs = repo / "docs"
                docs.mkdir()
                (docs / "notes.md").write_text(
                    "# Article ideas\n\n- Registry vs TODO comments vs Jira\n",
                    encoding="utf-8")
                p = h.run_hook(adapter, "stop",
                               h.stop_payload(adapter, repo),
                               repo=repo, cache=cache)
                self.assertEqual(p.returncode, 0, p.stderr)
                if p.stdout.strip():
                    obj = json.loads(p.stdout)
                    self.assertNotEqual(obj.get("decision"), "block")


class TestEndToEnd(HookTestBase):
    def test_session_then_feedback_logs_full_loop(self):
        # session-start primes the cache; a subsequent edit logs edit+feedback.
        # For copilot this is the full ADR-0019 cwd path, end to end.
        for adapter in h.HOOK_ADAPTERS:
            with self.subTest(adapter=adapter):
                repo, cache = self.fresh()
                h.write_charter(repo, "echo CANARY_OK")
                (repo / "note.txt").write_text("x", encoding="utf-8")
                h.run_hook(adapter, "session-start",
                           h.session_start_payload(adapter, repo),
                           repo=repo, cache=cache)
                h.run_hook(adapter, "feedback",
                           h.feedback_payload(adapter, repo),
                           repo=repo, cache=cache)
                kinds = {e.get("event") for e in h.read_metrics(cache)}
                self.assertIn("session", kinds)
                self.assertIn("edit", kinds)
                self.assertIn("feedback", kinds)


class TestCopilotCwdRegression(HookTestBase):
    """ADR 0019: Copilot runs hooks with cwd = the plugin dir and passes the
    project as the payload `cwd`. These run from an unrelated dir and must still
    find the repo — they fail if the chdir-to-payload-cwd shim is removed."""

    def test_hooks_use_payload_cwd_not_process_cwd(self):
        repo, cache = self.fresh()
        h.write_charter(repo, "echo CANARY_OK")
        (repo / "note.txt").write_text("x", encoding="utf-8")
        elsewhere = Path(tempfile.mkdtemp(dir=self.tmp, prefix="elsewhere-"))  # not a git repo

        ss = h.run_hook("copilot", "session-start",
                        h.session_start_payload("copilot", repo),
                        repo=repo, cache=cache, run_cwd=elsewhere)
        self.assertEqual(ss.returncode, 0, ss.stderr)

        fb = h.run_hook("copilot", "feedback",
                        h.feedback_payload("copilot", repo),
                        repo=repo, cache=cache, run_cwd=elsewhere)
        self.assertEqual(fb.returncode, 0, fb.stderr)
        self.assertIn("PASS", feedback_context("copilot", fb.stdout))

        kinds = {e.get("event") for e in h.read_metrics(cache)}
        self.assertIn("session", kinds)
        self.assertIn("feedback", kinds)


if __name__ == "__main__":
    unittest.main()
