import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "research" / "geometry-arbitration"))

from fixture_tools import sanitize_hyprland_client


class FixtureSanitizerTests(unittest.TestCase):
    def test_sanitizer_drops_personal_and_transient_browser_fields(self):
        raw = {
            "address": "0xdeadbeef",
            "mapped": True,
            "hidden": False,
            "at": [10, 20],
            "size": [1200.5, 900.25],
            "workspace": {"id": 3, "name": "secret-workspace"},
            "floating": False,
            "pseudo": False,
            "monitor": 1,
            "class": "google-chrome-stable",
            "title": "private document title",
            "initialClass": "google-chrome-stable",
            "initialTitle": "private initial title",
            "pid": 4242,
            "xwayland": False,
            "pinned": False,
            "fullscreen": 0,
            "fullscreenClient": 0,
            "grouped": [],
            "tags": ["example"],
            "swallowing": "none",
            "focusHistoryID": 0,
        }
        fixture = sanitize_hyprland_client(
            raw,
            fixture_id="local-sanitized-example",
            surface_kind="unknown",
            package_source="native",
            package_qualified=False,
            display_mode="native-wayland",
        )
        encoded = json.dumps(fixture, sort_keys=True)
        self.assertNotIn("private document title", encoded)
        self.assertNotIn("secret-workspace", encoded)
        self.assertNotIn("0xdeadbeef", encoded)
        self.assertNotIn("4242", encoded)
        self.assertEqual("google-chrome-stable", fixture["observation"]["appId"])
        self.assertEqual(1200.5, fixture["observation"]["geometry"]["width"])
        self.assertEqual("unverified", fixture["observation"]["geometry"]["unit"])
        self.assertFalse(fixture["observation"]["normalIdentityProven"])
        self.assertFalse(fixture["observation"]["package"]["qualified"])
        self.assertEqual("unknown", fixture["observation"]["browserChannel"])
        self.assertFalse(fixture["observation"]["browserChannelQualified"])
        self.assertIn("notes", fixture)
        self.assertNotIn("qualificationNotes", fixture)

    def test_browser_channel_is_explicit_and_never_inferred_from_app_id(self):
        raw = {
            "size": [1500, 900],
            "class": "google-chrome",
            "initialClass": "google-chrome",
        }
        default_fixture = sanitize_hyprland_client(raw, fixture_id="default-channel")
        self.assertEqual("unknown", default_fixture["observation"]["browserChannel"])

        beta_fixture = sanitize_hyprland_client(
            raw,
            fixture_id="beta-channel",
            browser_channel="beta",
            browser_channel_qualified=True,
        )
        self.assertEqual("beta", beta_fixture["observation"]["browserChannel"])
        self.assertTrue(beta_fixture["observation"]["browserChannelQualified"])

    def test_sanitizer_refuses_missing_invalid_size_or_unknown_enumerated_metadata(self):
        with self.assertRaises(ValueError):
            sanitize_hyprland_client({}, fixture_id="missing-size")
        with self.assertRaises(ValueError):
            sanitize_hyprland_client({"size": [0, 900]}, fixture_id="bad-size")
        with self.assertRaises(ValueError):
            sanitize_hyprland_client({"size": [1200, 900]}, fixture_id="bad-channel", browser_channel="nightly")
        with self.assertRaises(ValueError):
            sanitize_hyprland_client({"size": [1200, 900]}, fixture_id="bad-package", package_source="custom")


if __name__ == "__main__":
    unittest.main()
