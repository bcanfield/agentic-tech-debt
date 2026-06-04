"""Live check that `npx skills` offers exactly the four portable skills, not the
eight that would appear if the claude-code copies leaked (ADR 0018).

Needs network + npx, so it self-skips when unavailable. Pin the CLI version:
discovery/internal-flag behavior has changed across minor releases.
"""

import os
import shutil
import subprocess
import unittest

import helpers as h

SKILLS_CLI = "skills@1.5.10"
PORTABLE = ("debt-ops-add", "debt-ops-init", "debt-ops-metrics", "debt-ops-review")


def _list(env_extra=None):
    env = dict(os.environ)
    if env_extra:
        env.update(env_extra)
    return subprocess.run(
        ["npx", "-y", SKILLS_CLI, "add", str(h.REPO_ROOT), "--list"],
        capture_output=True, text=True, timeout=240, env=env,
    )


@unittest.skipUnless(shutil.which("npx"), "npx not available")
@unittest.skipIf(os.environ.get("SKIP_SKILLS_CLI"), "SKIP_SKILLS_CLI set")
class TestSkillsCli(unittest.TestCase):
    def test_default_offers_only_the_four_portable_skills(self):
        p = _list()
        self.assertIn("Found 4 skills", p.stdout + p.stderr,
                      f"expected 4 skills.\nSTDOUT:\n{p.stdout}\nSTDERR:\n{p.stderr}")
        for name in PORTABLE:
            self.assertIn(name, p.stdout + p.stderr, f"missing {name}")

    def test_internal_flag_hides_the_claude_code_copies(self):
        # With internal skills forced on, the four hidden copies reappear -> 8.
        # Proves the flag (not luck) is what hides them in the default run.
        p = _list({"INSTALL_INTERNAL_SKILLS": "1"})
        self.assertIn("Found 8 skills", p.stdout + p.stderr,
                      f"expected 8 with internal on.\nSTDOUT:\n{p.stdout}\nSTDERR:\n{p.stderr}")


if __name__ == "__main__":
    unittest.main()
