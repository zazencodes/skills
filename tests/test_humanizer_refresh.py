"""Refresh lifecycle tests use temporary skills and mocked Wikipedia responses."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "skills/humanizer-tryhard/scripts/refresh_source.py"
spec = importlib.util.spec_from_file_location("humanizer_refresh", SCRIPT)
refresh = importlib.util.module_from_spec(spec)
spec.loader.exec_module(refresh)
NOW = datetime(2026, 11, 14, tzinfo=timezone.utc)


def response(extra=""):
    sections = "".join(
        f'<h2>Section {i}</h2><p>' + ("Concrete source prose. " * 100) + "</p>"
        for i in range(12)
    )
    html = '<div class="mw-parser-output"><p>Introduction.</p>' + sections + extra + "</div>"
    return {"parse": {"title": refresh.TITLE, "revid": 123, "text": html}}


class RefreshTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.root.joinpath("SKILL.md").write_text(
            '<!-- refresh-config:start -->\n```json\n'
            '{"refresh_interval_days": 7, "request_timeout_seconds": 30}\n'
            '```\n<!-- refresh-config:end -->\n'
        )

    def run_refresh(self, at=NOW, **kwargs):
        return refresh.run(self.root, now=at, **kwargs)

    def seed(self):
        with patch.object(refresh, "fetch_page", return_value=response()) as fetch:
            self.assertEqual(self.run_refresh(), "refreshed")
            fetch.assert_called_once()

    def test_initial_fetch_and_fresh_cache_do_not_refetch(self):
        self.seed()
        with patch.object(refresh, "fetch_page") as fetch:
            self.assertEqual(self.run_refresh(at=NOW + timedelta(days=6, hours=23)), "fresh")
            fetch.assert_not_called()
        metadata, body = refresh.read_snapshot(self.root)
        self.assertEqual(metadata["last_successful_fetch_utc"], "2026-11-14T00:00:00Z")
        self.assertIn("Concrete source prose.", body)

    def test_seven_day_boundary_fetches_and_includes_new_sections(self):
        self.seed()
        with patch.object(refresh, "fetch_page", return_value=response('<h2>New pattern</h2><p>New advice.</p>')):
            self.assertEqual(self.run_refresh(at=NOW + timedelta(days=7)), "refreshed")
        self.assertIn("## New pattern", refresh.read_snapshot(self.root)[1])

    def test_failed_fetch_keeps_good_snapshot_and_does_not_reset_clock(self):
        self.seed()
        original = self.root.joinpath("references/wikipedia.md").read_bytes()
        with patch.object(refresh, "fetch_page", side_effect=OSError("offline")):
            with self.assertRaisesRegex(refresh.RefreshError, "offline"):
                self.run_refresh(at=NOW + timedelta(days=8))
        self.assertEqual(original, self.root.joinpath("references/wikipedia.md").read_bytes())
        log = json.loads(self.root.joinpath("references/refresh-status.json").read_text())
        self.assertEqual(log["status"], "failed")
        self.assertEqual(log["last_successful_fetch_utc"], "2026-11-14T00:00:00Z")
        self.assertTrue(log["cached_copy_usable"])

    def test_short_or_wrong_page_cannot_replace_good_copy(self):
        self.seed()
        before = self.root.joinpath("references/wikipedia.md").read_bytes()
        for bad in ({"error": {"info": "blocked"}}, {"parse": {"title": "Other", "revid": 123, "text": "x"}}, response() | {"parse": {"title": refresh.TITLE, "revid": 123, "text": "<p>Access denied</p>"}}):
            with self.subTest(bad=str(bad)[:50]), patch.object(refresh, "fetch_page", return_value=bad):
                with self.assertRaises(refresh.RefreshError):
                    self.run_refresh(at=NOW + timedelta(days=8))
                self.assertEqual(before, self.root.joinpath("references/wikipedia.md").read_bytes())

    def test_force_refresh_inside_window(self):
        self.seed()
        with patch.object(refresh, "fetch_page", return_value=response()) as fetch:
            self.run_refresh(force=True)
            fetch.assert_called_once()

    def test_missing_cache_offline_fails_explicitly(self):
        with patch.object(refresh, "fetch_page", side_effect=OSError("offline")):
            with self.assertRaises(refresh.RefreshError):
                self.run_refresh()
        log = json.loads(self.root.joinpath("references/refresh-status.json").read_text())
        self.assertFalse(log["cached_copy_usable"])
        self.assertFalse(self.root.joinpath("references/wikipedia.md").exists())

    def test_corrupt_cache_is_repaired_even_inside_window(self):
        self.seed()
        path = self.root.joinpath("references/wikipedia.md")
        path.write_text(path.read_text().replace("Concrete source prose.", "Corrupted prose.", 1))
        with patch.object(refresh, "fetch_page", return_value=response()) as fetch:
            self.assertEqual(self.run_refresh(), "refreshed")
            fetch.assert_called_once()
        refresh.read_snapshot(self.root)

    def test_config_window_is_read_from_skill(self):
        self.seed()
        path = self.root.joinpath("SKILL.md")
        path.write_text(path.read_text().replace('"refresh_interval_days": 7', '"refresh_interval_days": 2'))
        with patch.object(refresh, "fetch_page", return_value=response()) as fetch:
            self.run_refresh(at=NOW + timedelta(days=2))
            fetch.assert_called_once()

    def test_future_timestamp_and_invalid_config_fail_loudly(self):
        self.seed()
        with self.assertRaisesRegex(refresh.RefreshError, "future"):
            self.run_refresh(at=NOW - timedelta(days=1))
        path = self.root.joinpath("SKILL.md")
        path.write_text(path.read_text().replace('"refresh_interval_days": 7', '"refresh_interval_days": 0'))
        with self.assertRaisesRegex(refresh.RefreshError, "refresh_interval_days"):
            self.run_refresh()

    def test_converter_preserves_examples_links_and_section_text(self):
        html = '<h2>Advice</h2><p>Keep <b>specific</b> facts <a href="/wiki/Facts">here</a>.</p><blockquote><p>Bad example.</p></blockquote><pre>x = 1\ny = 2</pre><style>noise</style><span class="mw-editsection">edit source</span>'
        body = refresh.article_markdown(html)
        self.assertIn("## Advice", body)
        self.assertIn("Keep **specific** facts [here](https://en.wikipedia.org/wiki/Facts).", body)
        self.assertIn("> Bad example.", body)
        self.assertIn("x = 1\ny = 2", body)
        self.assertNotIn("noise", body)
        self.assertNotIn("edit source", body)


if __name__ == "__main__":
    unittest.main()
