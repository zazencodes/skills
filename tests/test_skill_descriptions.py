import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class SkillDescriptionTests(unittest.TestCase):
    def test_discovery_descriptions_stay_concise(self) -> None:
        skills = sorted((ROOT / "skills").glob("*/SKILL.md"))
        self.assertTrue(skills, "No skill metadata found")
        for skill in skills:
            with self.subTest(skill=skill.parent.name):
                frontmatter = skill.read_text().split("---", 2)[1]
                match = re.search(
                    r"^description:([^\n]*(?:\n[ \t]+[^\n]+)*)",
                    frontmatter,
                    re.MULTILINE,
                )
                self.assertIsNotNone(match, "Missing discovery description")
                assert match is not None
                description = " ".join(match[1].strip().lstrip(">|").split())
                self.assertTrue(description)
                self.assertLessEqual(len(description), 180, description)

    def test_codex_descriptions_stay_within_ui_budget(self) -> None:
        skills = sorted((ROOT / "skills").glob("*/SKILL.md"))
        self.assertTrue(skills, "No skill metadata found")
        for skill in skills:
            with self.subTest(skill=skill.parent.name):
                metadata = (skill.parent / "agents" / "openai.yaml").read_text()
                match = re.search(
                    r'^  short_description: "([^"\n]+)"$',
                    metadata,
                    re.MULTILINE,
                )
                self.assertIsNotNone(match, "Missing Codex short description")
                assert match is not None
                self.assertGreaterEqual(len(match[1]), 25)
                self.assertLessEqual(len(match[1]), 50, match[1])


if __name__ == "__main__":
    unittest.main()
