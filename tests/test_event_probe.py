import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "research" / "geometry-arbitration"))

from capture_hyprland_event_names import parse_event_name


class EventProbeTests(unittest.TestCase):
    def test_parser_keeps_event_name_only_and_drops_sensitive_payload(self):
        line = b"activewindow>>google-chrome-stable,private document title\n"
        self.assertEqual("activewindow", parse_event_name(line))

    def test_parser_rejects_malformed_event_line(self):
        self.assertIsNone(parse_event_name(b"private payload without delimiter"))
        self.assertIsNone(parse_event_name(b">>payload"))


if __name__ == "__main__":
    unittest.main()
