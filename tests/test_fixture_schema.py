import copy
import json
import math
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures" / "fdm-822"
sys.path.insert(0, str(ROOT / "research" / "geometry-arbitration"))

from classifier import classify_window


SUPPORTED_SCHEMA_KEYWORDS = frozenset({
    "additionalProperties",
    "const",
    "enum",
    "exclusiveMinimum",
    "items",
    "minLength",
    "properties",
    "required",
    "type",
    "schemaVersion",
})


class SchemaValidationError(ValueError):
    pass


def _instance_matches_type(instance, expected):
    if expected == "object":
        return isinstance(instance, dict)
    if expected == "array":
        return isinstance(instance, list)
    if expected == "string":
        return isinstance(instance, str)
    if expected == "boolean":
        return isinstance(instance, bool)
    if expected == "integer":
        return isinstance(instance, int) and not isinstance(instance, bool)
    if expected == "number":
        return (
            isinstance(instance, (int, float))
            and not isinstance(instance, bool)
            and math.isfinite(float(instance))
        )
    raise SchemaValidationError(f"unsupported schema type: {expected!r}")


def validate_schema_definition(schema, path="$schema"):
    if not isinstance(schema, dict):
        raise SchemaValidationError(f"{path}: schema node must be an object")

    unknown = sorted(set(schema) - SUPPORTED_SCHEMA_KEYWORDS)
    if unknown:
        raise SchemaValidationError(f"{path}: unsupported schema keyword(s): {', '.join(unknown)}")

    if "schemaVersion" in schema and schema["schemaVersion"] != 1:
        raise SchemaValidationError(f"{path}.schemaVersion must be 1")

    if "properties" in schema:
        properties = schema["properties"]
        if not isinstance(properties, dict):
            raise SchemaValidationError(f"{path}.properties must be an object")
        for name, nested in properties.items():
            validate_schema_definition(nested, f"{path}.properties.{name}")

    if "items" in schema:
        validate_schema_definition(schema["items"], f"{path}.items")

    if "additionalProperties" in schema and not isinstance(schema["additionalProperties"], bool):
        raise SchemaValidationError(f"{path}.additionalProperties must be boolean")

    if "required" in schema:
        required = schema["required"]
        if not isinstance(required, list) or any(not isinstance(item, str) for item in required):
            raise SchemaValidationError(f"{path}.required must be an array of strings")


def validate_instance(instance, schema, path="$"):
    expected_type = schema.get("type")
    if expected_type is not None and not _instance_matches_type(instance, expected_type):
        raise SchemaValidationError(f"{path}: expected {expected_type}")

    if "const" in schema and instance != schema["const"]:
        raise SchemaValidationError(f"{path}: expected const {schema['const']!r}")

    if "enum" in schema and instance not in schema["enum"]:
        raise SchemaValidationError(f"{path}: value {instance!r} is not in enum")

    if "minLength" in schema:
        if not isinstance(instance, str) or len(instance) < schema["minLength"]:
            raise SchemaValidationError(f"{path}: string is shorter than minLength")

    if "exclusiveMinimum" in schema:
        if (
            not isinstance(instance, (int, float))
            or isinstance(instance, bool)
            or not math.isfinite(float(instance))
            or not float(instance) > float(schema["exclusiveMinimum"])
        ):
            raise SchemaValidationError(f"{path}: value must exceed exclusiveMinimum")

    if expected_type == "object":
        required = schema.get("required", [])
        missing = [name for name in required if name not in instance]
        if missing:
            raise SchemaValidationError(f"{path}: missing required field(s): {', '.join(missing)}")

        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            extras = sorted(set(instance) - set(properties))
            if extras:
                raise SchemaValidationError(f"{path}: additional field(s): {', '.join(extras)}")

        for name, value in instance.items():
            nested = properties.get(name)
            if nested is not None:
                validate_instance(value, nested, f"{path}.{name}")

    if expected_type == "array":
        item_schema = schema.get("items")
        if item_schema is not None:
            for index, value in enumerate(instance):
                validate_instance(value, item_schema, f"{path}[{index}]")


class FixtureContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = json.loads((FIXTURES / "fixture-schema.json").read_text(encoding="utf-8"))
        cls.fixture_paths = sorted(path for path in FIXTURES.glob("*.json") if path.name != "fixture-schema.json")
        cls.valid_fixture = json.loads(cls.fixture_paths[0].read_text(encoding="utf-8"))

    def test_schema_and_synthetic_fixtures_are_present(self):
        self.assertTrue((FIXTURES / "fixture-schema.json").is_file())
        self.assertGreaterEqual(len(self.fixture_paths), 6)

    def test_schema_uses_only_the_deterministically_supported_vocabulary(self):
        validate_schema_definition(self.schema)

    def test_every_fixture_validates_against_schema_and_expected_classifier_result(self):
        for path in self.fixture_paths:
            with self.subTest(path=path.name):
                data = json.loads(path.read_text(encoding="utf-8"))
                validate_instance(data, self.schema)
                self.assertEqual("FDM-822", data["issue"])
                self.assertEqual("synthetic", data["provenance"]["kind"])
                result = classify_window(data["observation"])
                self.assertEqual(data["expectedClassification"], result.status)

    def test_validator_rejects_invalid_enum_type_and_additional_properties(self):
        cases = []

        invalid_enum = copy.deepcopy(self.valid_fixture)
        invalid_enum["observation"]["browserChannel"] = "nightly"
        cases.append(("enum", invalid_enum))

        invalid_type = copy.deepcopy(self.valid_fixture)
        invalid_type["observation"]["active"] = "true"
        cases.append(("type", invalid_type))

        extra_top = copy.deepcopy(self.valid_fixture)
        extra_top["documentName"] = "synthetic"
        cases.append(("top-extra", extra_top))

        extra_observation = copy.deepcopy(self.valid_fixture)
        extra_observation["observation"]["workspaceName"] = "synthetic"
        cases.append(("observation-extra", extra_observation))

        extra_package = copy.deepcopy(self.valid_fixture)
        extra_package["observation"]["package"]["accountId"] = "synthetic"
        cases.append(("package-extra", extra_package))

        extra_geometry = copy.deepcopy(self.valid_fixture)
        extra_geometry["observation"]["geometry"]["rawWidth"] = 1234
        cases.append(("geometry-extra", extra_geometry))

        extra_provenance = copy.deepcopy(self.valid_fixture)
        extra_provenance["provenance"]["profileName"] = "synthetic"
        cases.append(("provenance-extra", extra_provenance))

        for label, candidate in cases:
            with self.subTest(case=label):
                with self.assertRaises(SchemaValidationError):
                    validate_instance(candidate, self.schema)

    def test_fixtures_contain_no_forbidden_personal_browser_fields_or_url_like_data(self):
        forbidden_keys = {
            "account",
            "accountId",
            "address",
            "commandLine",
            "documentName",
            "email",
            "initialTitle",
            "pid",
            "profile",
            "profileName",
            "profilePath",
            "title",
            "token",
            "url",
            "workspaceName",
        }
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

        for path in [FIXTURES / "fixture-schema.json", *self.fixture_paths]:
            data = json.loads(path.read_text(encoding="utf-8"))
            for text in walk(data):
                self.assertIsNone(url_like.search(text), f"URL-like data in {path.name}")


if __name__ == "__main__":
    unittest.main()
