#!/usr/bin/env python3
"""Pure tests for FDM-821 set consent/idempotence/verification ordering."""

import importlib.util
from pathlib import Path
import unittest

MODULE_PATH = Path(__file__).with_name("contract-set-model.py")
spec = importlib.util.spec_from_file_location("contract_set_model", MODULE_PATH)
model = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(model)


class ContractSetModelTests(unittest.TestCase):
    def test_already_desired_is_verified_noop_without_consent(self):
        result = model.decide_before_mutation(
            current_orientation="vertical",
            desired_orientation="vertical",
            preference_control="user",
            sync_impact="unknown",
            consent=False,
        )
        self.assertEqual(result.status, "ok")
        self.assertEqual(result.reason_code, "already-desired")
        self.assertFalse(result.changed)
        self.assertTrue(result.verified)
        self.assertFalse(result.mutation_allowed)

    def test_syncable_mismatch_requires_consent(self):
        result = model.decide_before_mutation(
            current_orientation="horizontal",
            desired_orientation="vertical",
            preference_control="user",
            sync_impact="profile-syncable",
            consent=False,
        )
        self.assertEqual(result.status, "consent-required")
        self.assertEqual(result.reason_code, "sync-consent-required")
        self.assertFalse(result.mutation_allowed)

    def test_unknown_impact_mismatch_with_consent_reaches_mutation_gate(self):
        result = model.decide_before_mutation(
            current_orientation="horizontal",
            desired_orientation="vertical",
            preference_control="user",
            sync_impact="unknown",
            consent=True,
        )
        self.assertEqual(result.status, "ready-to-mutate")
        self.assertTrue(result.mutation_allowed)

    def test_managed_mismatch_fails_before_mutation(self):
        result = model.decide_before_mutation(
            current_orientation="horizontal",
            desired_orientation="vertical",
            preference_control="managed",
            sync_impact="local-only",
            consent=True,
        )
        self.assertEqual(result.status, "policy-controlled")
        self.assertFalse(result.mutation_allowed)

    def test_postflight_mismatch_is_conflict_and_never_verified(self):
        result = model.verify_after_mutation(
            desired_orientation="vertical",
            final_orientation="horizontal",
        )
        self.assertEqual(result.status, "conflict")
        self.assertEqual(result.reason_code, "postflight-orientation-mismatch")
        self.assertIsNone(result.changed)
        self.assertFalse(result.verified)

    def test_postflight_match_is_verified_changed_success(self):
        result = model.verify_after_mutation(
            desired_orientation="vertical",
            final_orientation="vertical",
        )
        self.assertEqual(result.status, "ok")
        self.assertEqual(result.reason_code, "verified")
        self.assertTrue(result.changed)
        self.assertTrue(result.verified)


if __name__ == "__main__":
    unittest.main()
