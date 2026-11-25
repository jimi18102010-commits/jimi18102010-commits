import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import generate_cards as gc


class ProfileStatsTests(unittest.TestCase):
    def test_collect_stats_pagination_and_filtering(self):
        calls = []

        def fake_api(path: str):
            calls.append(path)
            if path.startswith("users/") and "&page=1" in path:
                return [
                    {"owner": {"login": "jimmiy"}, "stargazers_count": 2, "fork": False, "private": False}
                ] * 100
            if path.startswith("users/") and "&page=2" in path:
                return [
                    {"owner": {"login": "jimmiy"}, "stargazers_count": 3, "fork": True, "private": False},
                    {"owner": {"login": "jimmiy"}, "stargazers_count": 99, "fork": False, "private": True},
                    {"owner": {"login": "someone-else"}, "stargazers_count": 50, "fork": False, "private": False},
                ]
            if "is%3Amerged" in path:
                return {"total_count": 2, "incomplete_results": False}
            if "is%3Aopen" in path:
                return {"total_count": 1, "incomplete_results": False}
            raise AssertionError(f"Unexpected path: {path}")

        data = gc.collect_stats("jimmiy", api=fake_api)
        self.assertEqual(data["public_repos"], 101)
        self.assertEqual(data["original_repos"], 100)
        self.assertEqual(data["fork_repos"], 1)
        self.assertEqual(data["total_stars"], 203)
        self.assertEqual(data["original_stars"], 200)
        self.assertEqual(data["upstream_merged_prs"], 2)
        self.assertEqual(data["upstream_open_prs"], 1)
        self.assertTrue(any("&page=2" in c for c in calls))

    def test_incomplete_search_raises(self):
        def fake_api(path: str):
            if path.startswith("users/"):
                return []
            return {"total_count": 0, "incomplete_results": True}

        with self.assertRaises(RuntimeError):
            gc.collect_stats("jimmiy", api=fake_api)

    def test_invalid_username_rejected(self):
        with self.assertRaises(ValueError):
            gc.collect_stats("../evil")

    def test_render_dark_and_light_svgs_valid_xml(self):
        sample = {
            "username": "jimmiy",
            "public_repos": 9,
            "original_repos": 5,
            "fork_repos": 4,
            "total_stars": 11,
            "original_stars": 6,
            "upstream_merged_prs": 2,
            "upstream_open_prs": 1,
            "updated_utc": "2026-11-25T07:20:00+00:00",
        }
        for theme in ("dark", "light"):
            svg = gc.render_stats_svg(sample, theme=theme)
            root = ET.fromstring(svg)
            self.assertTrue(root.tag.endswith("svg"))
            self.assertIn("5 original · 4 forks", svg)
            self.assertIn("synced 2026-11-25", svg)
            self.assertNotIn("A++", svg)
            self.assertNotIn("142", svg)


if __name__ == "__main__":
    unittest.main()
