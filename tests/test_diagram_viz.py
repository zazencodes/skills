import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "diagram-viz"
CHECK_PALETTE = SKILL / "scripts" / "check_palette.py"
RENDER = SKILL / "scripts" / "render.sh"
CHROME = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
SURFACES = ["--bg", "#1b2023", "--surface", "#262c2f"]


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(list(args), check=False, text=True, capture_output=True)


class CheckPaletteTests(unittest.TestCase):
    def test_documented_accents_pass(self) -> None:
        result = run(sys.executable, str(CHECK_PALETTE), *SURFACES, "#C6AEFF", "#FFA557", "#FF2E88")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertNotIn("FAIL", result.stdout)

    def test_purple_and_lifted_pink_fail_under_normal_vision(self) -> None:
        result = run(sys.executable, str(CHECK_PALETTE), *SURFACES, "#C6AEFF", "#FF80B5")
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("#C6AEFF+#FF80B5    14.8", result.stdout)

    def test_low_contrast_accent_fails(self) -> None:
        result = run(sys.executable, str(CHECK_PALETTE), *SURFACES, "#7C3AED")
        self.assertEqual(result.returncode, 1, result.stdout)

    def test_rejects_malformed_colour(self) -> None:
        result = run(sys.executable, str(CHECK_PALETTE), *SURFACES, "purple")
        self.assertNotEqual(result.returncode, 0)


@unittest.skipUnless(sys.platform == "darwin" and CHROME.exists(), "render.sh needs macOS and Google Chrome")
class RenderTests(unittest.TestCase):
    def test_examples_render_with_a_clean_layout(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            for name in ("harness", "timeline"):
                with self.subTest(example=name):
                    result = run(str(RENDER), str(SKILL / "examples" / f"{name}.html"), f"{tmp}/{name}.png")
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertIn("(2560x1440)", result.stdout)
                    self.assertIn("Layout check: OK", result.stdout)

    def test_layout_faults_are_reported(self) -> None:
        page = (SKILL / "examples" / "harness.html").read_text()
        broken = page.replace(
            'width:158px; text-align:center">reply or tool request',
            'width:100px; text-align:center">reply or tool request',
        ).replace("left:836px; top:219px; width:58px", "left:826px; top:219px; width:68px")
        self.assertNotEqual(page, broken)
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "broken.html"
            source.write_text(broken)
            result = run(str(RENDER), str(source), f"{tmp}/broken.png")
            self.assertEqual(result.returncode, 1, result.stdout)
            self.assertIn('wraps to 2 lines (max 1), widen it or shorten the words: cap "reply or tool request"', result.stderr)
            self.assertIn("arrow touches a box", result.stderr)
            self.assertTrue((Path(tmp) / "broken.png").exists())


if __name__ == "__main__":
    unittest.main()
