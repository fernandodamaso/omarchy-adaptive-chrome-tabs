import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures" / "fdm-822"
sys.path.insert(0, str(ROOT / "research" / "geometry-arbitration"))

from classifier import classify_window


class FixtureContractTests(unittest.TestCase):
    def test_schema_and_synthetic_fixtures_are_present(self):
        self.assertTrue((FIXTURES / "fixture-schema.json").is_file())
        fixtures = sorted(p for p in FIXTURES.glob("*.json") if p.name != "fixture-schema.json")
        self.assertGreaterEqual(len(fixtures), 6)

    def test_every_fixture_matches_minimal_contract_and_expected_classifier_result(self):
        schema = json.loads((FIXTURES / "fixture-schema.json").read_text(encoding="utf-8"))
        required_top = set(schema["required"])
        required_observation = set(schema["properties"]["observation"]["required"])
        for path in sorted(FIXTURES.glob("*.json")):
            if path.name == "fixture-schema.json":
                continue
            with self.subTest(path=path.name):
                data = json.loads(path.read_text(encoding="utf-8"))
                self.assertTrue(required_top.issubset(data))
                self.assertTrue(required_observation.issubset(data["observation"]))
                self.assertEqual("FDM-822", data["issue"])
                self.assertEqual("synthetic", data["provenance"]["kind"])
                result = classify_window(data["observation"])
                self.assertEqual(data["expectedClassification"], result.status)

    def test_fixtures_contain_no_forbidden_personal_browser_fields_or_url_like_data(self):
        forbidden_keys = {"title", "initialTitle", "url", "profile", "profilePath", "pid", "address", "commandLine", "token"}
        url_like = re.compile(r"(?:https?://|chrome-extension://)", re.I)

        def walk(value):
            if isinstance(value, dict):
                for key, nested in value.items():
                    self.assertNotIn(key, forbidden_keys)
                    yield from walk(nested)
            elif isinstance(value, list):
                for nested in value:
                    yield from walk(nested)
            elif isinstance(value, str):
                yield value

        for path in sorted(FIXTURES.glob("*.json")):
            data = json.loads(path.read_text(encoding="utf-8"))
            for text in walk(data):
                self.assertIsNone(url_like.search(text), f"URL-like data in {path.name}")


if __name__ == "__main__":
    unittest.main()
