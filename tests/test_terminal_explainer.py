import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
SKILL = REPO / "skills/terminal-explainer"
CLI = ["uv", "run", "--script", str(SKILL / "scripts/explain.py")]


class TerminalExplainerTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.spec = self.root / "tour.json"
        self.env = dict(os.environ, XDG_CONFIG_HOME=str(self.root / "config"),
                        XDG_STATE_HOME=str(self.root / "state"))

    def cli(self, *args, check=True):
        return subprocess.run([*CLI, *args], cwd=self.root, env=self.env,
                              capture_output=True, text=True, check=check)

    def test_demo_freezes_real_code_and_picture_in_independent_runs(self):
        args = ("prepare", SKILL / "examples/walkthrough.json", "--root", SKILL)
        first, second = [Path(json.loads(self.cli(*args).stdout)["run"]) for _ in range(2)]
        self.assertNotEqual(first, second)
        self.assertEqual(first.stat().st_mode & 0o777, 0o700)
        pages = json.loads((first / "walkthrough.json").read_text())["pages"]
        self.assertTrue((first / pages[0]["image"]["file"]).is_file())
        self.assertIn("def save_response", pages[0]["evidence"]["code"])
        self.assertIn("temporary.replace", pages[0]["evidence"]["code"])
        self.assertIn("def wait_response", pages[1]["evidence"]["code"])
        self.assertIn("return json.loads", pages[1]["evidence"]["code"])
        self.assertEqual(self.cli("wait", first, "--timeout", "0", check=False).returncode, 3)
        self.assertNotEqual(self.cli("wait", self.root, "--timeout", "0", check=False).returncode, 0)

    def test_invalid_evidence_leaves_no_run(self):
        self.spec.write_text(json.dumps({"title": "Review", "pages": [{
            "heading": "Evidence", "body": "Source line",
            "evidence": {"file": "../escape", "start": 1, "end": 1}}]}))
        failure = self.cli("prepare", self.spec, check=False)
        self.assertNotEqual(failure.returncode, 0)
        self.assertIn("expected a relative file", failure.stderr)
        self.assertFalse(list((self.root / "state/terminal-explainer").iterdir()))

    def test_captures_tracked_diff_and_multi_evidence_at_creation(self):
        checkout = self.root / "checkout"
        subprocess.run(["git", "clone", "--quiet", "--local", "--no-hardlinks", str(REPO), str(checkout)], check=True)
        source = checkout / "README.md"
        lines = source.read_text().splitlines()
        with source.open("a") as f:
            f.write("\nA specific change to review.\n")
        self.spec.write_text(json.dumps({"title": "Diff", "pages": [
            {"heading": "Readme", "body": "New line",
             "evidence": {"file": "README.md", "base": "HEAD", "start": len(lines), "end": len(lines) + 2}},
            {"heading": "Combined", "body": "Diff and lines", "evidence": [
                {"file": "README.md", "base": "HEAD~1", "head": "HEAD"},
                {"file": "README.md", "start": 1, "end": 2},
            ]},
        ]}))
        run = Path(json.loads(self.cli("prepare", self.spec, "--root", checkout).stdout)["run"])
        self.spec.write_text(json.dumps({"title": "Miss", "pages": [{
            "heading": "Top", "body": "Unchanged",
            "evidence": {"file": "README.md", "base": "HEAD", "start": 1, "end": 2}}]}))
        self.assertNotEqual(self.cli("prepare", self.spec, "--root", checkout, check=False).returncode, 0)
        source.write_text("a later edit")
        pages = json.loads((run / "walkthrough.json").read_text())["pages"]
        ev = pages[0]["evidence"]
        self.assertIn("+A specific change to review.", ev["code"])
        self.assertNotIn("diff --git", ev["code"])
        self.assertNotIn("a later edit", ev["code"])
        self.assertEqual(len(pages[1]["evidence"]), 2)
        self.assertNotIn("working tree", pages[1]["evidence"][0]["label"])

    def test_generator_receives_one_literal_prompt_and_publishes_once(self):
        config = Path(json.loads(self.cli("config", "--init").stdout)["path"])
        helper = self.root / "worker.py"
        helper.write_text("from pathlib import Path\nimport sys, shutil\n"
                          "Path('received').write_text(sys.argv[1])\nshutil.copyfile(sys.argv[2], sys.argv[3])\n")
        command = [sys.executable, str(helper), "{prompt}", str(SKILL / "examples/handoff.png"), "{output}"]
        config.write_text(json.dumps({"image_command": command, "illustration_style": "Large silhouettes."}))
        (self.root / "brief.txt").write_text("One arrow with a '$' label.")
        self.cli("illustrate", "brief.txt", "out.png")
        self.assertEqual((self.root / "received").read_text(), "One arrow with a '$' label.\n\nLarge silhouettes.")
        self.assertEqual((self.root / "out.png").read_bytes(), (SKILL / "examples/handoff.png").read_bytes())
        self.assertNotEqual(self.cli("illustrate", "brief.txt", "out.png", check=False).returncode, 0)
        self.assertNotEqual(self.cli("illustrate", "brief.txt", "out.png", "--plane", check=False).returncode, 0)
        self.assertNotEqual(self.cli("config", "--init", check=False).returncode, 0)

    def test_viewer_keyboard_navigation_and_submission(self):
        (self.root / "handoff.png").write_bytes((SKILL / "examples/handoff.png").read_bytes())
        self.spec.write_text(json.dumps({"title": "Tour", "pages": [
            {"heading": "Scene 1", "body": "First body",
             "image": {"file": "handoff.png", "caption": "Caption"},
             "evidence": {"file": "scripts/explain.py", "start": 1, "end": 4},
             "question": {"id": "pick", "prompt": "Pick one", "choices": ["Alpha", "Beta"]}},
            {"heading": "Scene 2", "body": "Second body",
             "question": {"id": "note", "prompt": "Note"}},
        ]}))
        run = Path(json.loads(self.cli("prepare", self.spec, "--root", SKILL).stdout)["run"])
        header = "\n".join((SKILL / "scripts/explain.py").read_text().splitlines()[:4])
        driver = self.root / "driver.py"
        driver.write_text(f"""{header}
import asyncio, json, sys
from pathlib import Path
sys.path.insert(0, {str(SKILL / "scripts")!r})
from viewer import FigureView, Walkthrough

async def main():
    run = Path({str(run)!r})
    doc = json.loads((run / "walkthrough.json").read_text())
    app = Walkthrough(doc, run, 14, "cells")
    async with app.run_test(size=(100, 30)) as pilot:
        await pilot.pause()
        await pilot.press("f")
        await pilot.pause()
        assert isinstance(app.screen, FigureView)
        await pilot.press("f")
        await pilot.pause()
        assert not isinstance(app.screen, FigureView)
        await pilot.press("e")
        await pilot.pause()
        assert not app.query_one("#page-0 Collapsible").collapsed
        await pilot.press("2", "n")
        await pilot.pause()
        assert app.index == 1
        await pilot.press("a")
        await pilot.pause()
        ta = app.query_one("#answer-1")
        assert app.focused is ta
        await pilot.press("o", "k", "escape")
        await pilot.pause()
        assert app.is_running and ta.text == "ok" and app.focused is not ta
        await pilot.press("n")
        await pilot.pause()
    assert app.return_value == {{"pick": "Beta", "note": "ok"}}

asyncio.run(main())
""")
        subprocess.run(["uv", "run", "--script", str(driver)], cwd=self.root, env=self.env, check=True)
