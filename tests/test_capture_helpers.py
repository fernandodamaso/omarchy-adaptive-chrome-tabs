import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "research" / "geometry-arbitration"))

from capture_geometry_snapshot import sanitize_client_record, sanitize_monitor_record


class CaptureHelperTests(unittest.TestCase):
    def test_client_snapshot_keeps_geometry_and_fullscreen_fields_but_drops_titles_and_transient_ids(self):
        raw = {
            "address": "0xabc",
            "class": "google-chrome-stable",
            "initialClass": "google-chrome-stable",
            "title": "private",
            "initialTitle": "private initial",
            "pid": 1234,
            "size": [1400.5, 900.25],
            "at": [100, 200],
            "fullscreen": 2,
            "fullscreenClient": 3,
            "floating": False,
            "xwayland": False,
            "mapped": True,
            "hidden": False,
            "monitor": 1,
            "workspace": {"id": 4, "name": "secret"},
        }
        clean = sanitize_client_record(raw)
        encoded = json.dumps(clean, sort_keys=True)
        self.assertNotIn("private", encoded)
        self.assertNotIn("0xabc", encoded)
        self.assertNotIn("1234", encoded)
        self.assertNotIn("secret", encoded)
        self.assertEqual([1400.5, 900.25], clean["size"])
        self.assertEqual(2, clean["fullscreenRaw"])
        self.assertEqual(3, clean["fullscreenClientRaw"])
        self.assertEqual(4, clean["workspaceId"])

    def test_monitor_snapshot_drops_make_model_description_and_serial(self):
        raw = {
            "id": 1,
            "name": "DP-1",
            "description": "private monitor description",
            "make": "Vendor",
            "model": "Model",
            "serial": "SERIAL-SECRET",
            "x": 1920,
            "y": 0,
            "width": 2560,
            "height": 1440,
            "refreshRate": 144.0,
            "scale": 1.25,
            "transform": 0,
            "activeWorkspace": {"id": 2, "name": "secret workspace"},
            "specialWorkspace": {"id": -99, "name": "special"},
        }
        clean = sanitize_monitor_record(raw)
        encoded = json.dumps(clean, sort_keys=True)
        self.assertNotIn("SERIAL-SECRET", encoded)
        self.assertNotIn("private monitor", encoded)
        self.assertNotIn("Vendor", encoded)
        self.assertEqual(1.25, clean["scale"])
        self.assertEqual(0, clean["transform"])
        self.assertEqual(2, clean["activeWorkspaceId"])


if __name__ == "__main__":
    unittest.main()
