"""Static structure checks — cheap guards for the class of bug that ships a
broken install: malformed manifests, hook commands pointing at missing scripts,
skills missing required frontmatter, or the dedup `internal` flag drifting.
"""

import json
import re
import unittest
from pathlib import Path

import helpers as h

ROOT = h.REPO_ROOT

# (manifest path, plugin-root dir the ${...} token resolves to)
PLUGIN_MANIFESTS = [
    ROOT / "claude-code" / ".claude-plugin" / "plugin.json",
    ROOT / "codex" / ".codex-plugin" / "plugin.json",
    ROOT / "copilot" / "plugin.json",
]
# hooks.json wired via each plugin manifest, and the dir its root token maps to.
HOOK_MANIFESTS = [
    (ROOT / "claude-code" / "hooks" / "hooks.json", ROOT / "claude-code"),
    (ROOT / "codex" / "hooks" / "hooks.json", ROOT / "codex"),
    (ROOT / "copilot" / "hooks" / "hooks.json", ROOT / "copilot"),
]
ROOT_TOKEN_RE = re.compile(r"\$\{(?:CLAUDE_)?PLUGIN_ROOT\}/(\S+\.py)")


def frontmatter(skill_md):
    """Return the text between the first two `---` fences, or '' if absent."""
    text = skill_md.read_text(encoding="utf-8")
    parts = text.split("---", 2)
    return parts[1] if len(parts) >= 3 and text.lstrip().startswith("---") else ""


def all_skill_files():
    out = []
    for parent in ("claude-code/skills", "codex/skills", "copilot/skills", "skills"):
        out.extend(sorted((ROOT / parent).glob("*/SKILL.md")))
    return out


class TestManifests(unittest.TestCase):
    def test_root_marketplace_resolves_to_a_plugin(self):
        mk = ROOT / ".claude-plugin" / "marketplace.json"
        data = json.loads(mk.read_text(encoding="utf-8"))
        self.assertTrue(data.get("name"))
        self.assertTrue(data.get("plugins"), "marketplace has no plugins")
        for plugin in data["plugins"]:
            src = plugin.get("source")
            self.assertIsInstance(src, str, "expected a local string source")
            target = (ROOT / src / ".claude-plugin" / "plugin.json")
            self.assertTrue(target.is_file(),
                            f"marketplace source {src} has no plugin.json")

    def test_plugin_manifests_valid(self):
        for mani in PLUGIN_MANIFESTS:
            with self.subTest(manifest=str(mani.relative_to(ROOT))):
                self.assertTrue(mani.is_file(), f"missing {mani}")
                data = json.loads(mani.read_text(encoding="utf-8"))
                self.assertTrue(data.get("name"), "plugin.json missing name")

    def test_hook_commands_point_at_real_scripts(self):
        for mani, root_dir in HOOK_MANIFESTS:
            with self.subTest(manifest=str(mani.relative_to(ROOT))):
                text = mani.read_text(encoding="utf-8")
                json.loads(text)  # must be valid JSON
                refs = ROOT_TOKEN_RE.findall(text)
                self.assertTrue(refs, f"{mani} references no hook scripts")
                for rel in refs:
                    self.assertTrue((root_dir / rel).is_file(),
                                    f"{mani}: {rel} does not exist under {root_dir.name}/")


class TestSkillFrontmatter(unittest.TestCase):
    def test_every_skill_has_name_and_description(self):
        skills = all_skill_files()
        self.assertGreaterEqual(len(skills), 16, "expected >=16 SKILL.md files")
        for sk in skills:
            with self.subTest(skill=str(sk.relative_to(ROOT))):
                fm = frontmatter(sk)
                self.assertRegex(fm, r"(?m)^\s*name:\s*\S+", "missing name")
                self.assertRegex(fm, r"(?m)^\s*description:\s*\S+", "missing description")

    def test_internal_flag_only_on_claude_code_skills(self):
        # ADR 0018: the claude-code copies are hidden from `npx skills`; the
        # other three sets must NOT carry the flag or they'd vanish too.
        for sk in all_skill_files():
            rel = str(sk.relative_to(ROOT))
            is_internal = bool(re.search(r"(?m)^\s*internal:\s*true\s*$", frontmatter(sk)))
            with self.subTest(skill=rel):
                if rel.startswith("claude-code/skills/"):
                    self.assertTrue(is_internal, f"{rel} should be metadata.internal: true")
                else:
                    self.assertFalse(is_internal, f"{rel} must NOT be internal")


if __name__ == "__main__":
    unittest.main()
