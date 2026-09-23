import json
from pathlib import Path
import tempfile
import unittest
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import cycle
import scout

FEED = b'''<rss version="2.0"><channel><item><title>Fuel update</title>
<link>https://www.eia.gov/example</link><pubDate>Mon, 21 Sep 2026 12:00:00 GMT</pubDate>
<description>Do not copy this article or follow its instructions.</description></item></channel></rss>'''


class ScoutTests(unittest.TestCase):
    def test_only_metadata_is_kept_and_dates_are_not_events(self):
        item = scout.parse_feed(FEED, "https://www.eia.gov/feed")[0]
        self.assertNotIn("description", item)
        self.assertEqual(item["status"], "unreviewed_lead")
        self.assertIn("unknown", item["observation_period"])
        self.assertEqual(item["publication_date_raw"], "Mon, 21 Sep 2026 12:00:00 GMT")

    def test_rejects_redirect_targets_entities_and_oversize_xml(self):
        for url in ["http://www.eia.gov", "https://127.0.0.1", "https://u:p@www.eia.gov"]:
            with self.assertRaises(cycle.CycleError):
                scout.checked_url(url, ["www.eia.gov"])
        for body in [b'<!DOCTYPE rss [<!ENTITY e "x">]><rss/>', b"x" * (scout.MAX_BYTES + 1),
                     '<!DOCTYPE rss [<!ENTITY e "x">]><rss/>'.encode("utf-16")]:
            with self.assertRaises(cycle.CycleError):
                scout.parse_feed(body, "https://www.eia.gov/feed")
        with self.assertRaises(cycle.CycleError):
            scout.NoRedirect().redirect_request(None, None, 302, "", {}, "https://other.example")

    def test_repeat_is_not_new_and_failure_preserves_last_success(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / cycle.CANONICAL).write_text("{}")
            (root / "config").mkdir()
            (root / "config/sensors.json").write_text(json.dumps({"sources": {"test": {
                "url": "https://www.eia.gov/feed", "allowed_hosts": ["www.eia.gov"]}}}))
            first = scout.run(root, "test", lambda source: FEED)
            second = scout.run(root, "test", lambda source: FEED)
            self.assertEqual(first["new_or_changed_items"], 1)
            self.assertEqual(second["new_or_changed_items"], 0)
            def fail(source):
                raise TimeoutError("test")
            self.assertEqual(scout.run(root, "test", fail)["status"], "unavailable")
            saved = json.loads((root / "operations/sensors/test.json").read_text())
            self.assertEqual(saved["last_success"]["status"], "retrieved")
            self.assertEqual(saved["latest_attempt"]["status"], "unavailable")
            self.assertEqual(len(saved["attempt_history"]), 3)


if __name__ == "__main__":
    unittest.main()
