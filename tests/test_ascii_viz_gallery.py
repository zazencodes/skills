import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "ascii-viz" / "SKILL.md"
GALLERY = SKILL.parent / "references" / "pattern-gallery.md"


class AsciiVizGalleryTests(unittest.TestCase):
    def test_skill_links_to_bundled_gallery(self) -> None:
        links = re.findall(r"\[[^\]]+\]\(([^)]+)\)", SKILL.read_text())
        self.assertIn("references/pattern-gallery.md", links)
        self.assertTrue(GALLERY.is_file())


    def test_each_pattern_has_guidance_and_a_terminal_sized_example(self) -> None:
        text = GALLERY.read_text()
        expected = {
            "Usage and quota", "Progress", "Timeline", "System flow",
            "Before and after", "Option menu", "Architecture", "Status card",
        }
        sections = dict(re.findall(
            r"^## ([^\n]+)\n(.*?)(?=^## |\Z)", text, re.MULTILINE | re.DOTALL
        ))
        self.assertTrue(expected.issubset(sections), expected - sections.keys())
        for title in expected:
            with self.subTest(pattern=title):
                section = sections[title]
                guidance = section.split("```", 1)[0].strip()
                self.assertTrue(guidance, "Explain when to use the pattern")
                examples = re.findall(r"^```text\n(.+?)^```$", section,
                                      re.MULTILINE | re.DOTALL)
                self.assertEqual(len(examples), 1)
                self.assertEqual(section.count("```"), 2)
                for line in examples[0].splitlines():
                    self.assertLessEqual(len(line), 72, line)


if __name__ == "__main__":
    unittest.main()
