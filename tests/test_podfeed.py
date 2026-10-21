import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import podfeed


class TestFmtDuration(unittest.TestCase):
    def test_minutes(self):
        self.assertEqual(podfeed.fmt_duration(125), "2:05")

    def test_hours(self):
        self.assertEqual(podfeed.fmt_duration(3661), "1:01:01")


class TestBuildFeed(unittest.TestCase):
    def test_feed_contains_episode(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "2026-10-20_Morning_Show.m4a")
            with open(path, "wb") as f:
                f.write(b"\0" * 1234)
            xml = podfeed.build_feed(d, dict(podfeed.DEFAULT_CONFIG))
            self.assertIn("<rss version=\"2.0\"", xml)
            self.assertIn("2026 10 20 Morning Show", xml)
            self.assertIn('length="1234"', xml)
            self.assertIn('type="audio/x-m4a"', xml)

    def test_escapes_special_chars(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "Tom & Jerry.mp3")
            with open(path, "wb") as f:
                f.write(b"x")
            xml = podfeed.build_feed(d, dict(podfeed.DEFAULT_CONFIG))
            self.assertIn("Tom &amp; Jerry", xml)


if __name__ == "__main__":
    unittest.main()
