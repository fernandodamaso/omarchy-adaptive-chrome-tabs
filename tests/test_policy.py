import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "research" / "geometry-arbitration"))

from policy import (
    ArbitrationPolicy,
    Observation,
    PolicyConfig,
    ConfigError,
    region_for_width,
    resolve_config,
)


def obs(
    *,
    window="window-a",
    scope="scope-a",
    epoch="epoch-1",
    width=1300.0,
    orientation="horizontal",
    eligible=True,
    focused=True,
    locked=False,
):
    return Observation(
        window_key=window,
        scope_token=scope,
        scope_epoch=epoch,
        width=width,
        orientation=orientation,
        eligible=eligible,
        focused=focused,
        locked=locked,
    )


class PolicyConfigTests(unittest.TestCase):
    def test_region_boundaries_are_inclusive_without_rounding_fractional_values(self):
        config = PolicyConfig()
        self.assertEqual("narrow", region_for_width(1200.0, config))
        self.assertEqual("band", region_for_width(1200.1, config))
        self.assertEqual("band", region_for_width(1399.9, config))
        self.assertEqual("wide", region_for_width(1400.0, config))

    def test_invalid_revision_preserves_prior_valid_runtime_config(self):
        prior = PolicyConfig(horizontal_threshold=1100, vertical_threshold=1400, revision="prior")
        resolved, accepted, error = resolve_config(
            {"horizontalThreshold": 1390, "verticalThreshold": 1400, "minimumThresholdGap": 100, "revision": "bad"},
            prior,
        )
        self.assertFalse(accepted)
        self.assertEqual(prior, resolved)
        self.assertIn("minimum threshold gap", error)

    def test_invalid_config_without_prior_disables_automation(self):
        resolved, accepted, error = resolve_config({"horizontalThreshold": 399, "revision": "bad"}, None)
        self.assertFalse(accepted)
        self.assertIsNone(resolved)
        self.assertTrue(error)

    def test_present_non_integer_threshold_rejects_entire_revision(self):
        with self.assertRaises(ConfigError):
            PolicyConfig.from_mapping({"horizontalThreshold": 1200.5, "revision": "fractional"})


class ArbitrationPolicyTests(unittest.TestCase):
    def test_startup_baselines_only_eligible_target_in_enable_snapshot_when_apply_on_startup_is_false(self):
        policy = ArbitrationPolicy(PolicyConfig(apply_on_startup=False))
        self.assertIsNone(policy.observe(obs(width=1500, orientation="horizontal"), 0))
        self.assertIsNone(policy.observe(obs(width=1500, orientation="horizontal"), 1000))

    def test_no_browser_at_startup_then_first_eligible_focus_uses_normal_dwell_evaluation(self):
        policy = ArbitrationPolicy(PolicyConfig(apply_on_startup=False, decision_dwell_ms=100, min_switch_interval_ms=0))
        self.assertIsNone(policy.observe(obs(eligible=False, focused=False), 0))
        self.assertIsNone(policy.observe(obs(width=1500, orientation="horizontal"), 10))
        self.assertIsNone(policy.observe(obs(width=1500, orientation="horizontal"), 109))
        request = policy.observe(obs(width=1500, orientation="horizontal"), 110)
        self.assertIsNotNone(request)
        self.assertEqual("vertical", request.orientation)
        self.assertEqual("initial-scope-evaluation", request.reason)

    def test_transition_requires_full_dwell_then_emits_exact_state_request(self):
        policy = ArbitrationPolicy(PolicyConfig(apply_on_startup=False, decision_dwell_ms=750))
        policy.observe(obs(width=1300, orientation="horizontal"), 0)
        self.assertIsNone(policy.observe(obs(width=1500, orientation="horizontal"), 100))
        self.assertIsNone(policy.observe(obs(width=1500, orientation="horizontal"), 849))
        request = policy.observe(obs(width=1500, orientation="horizontal"), 850)
        self.assertIsNotNone(request)
        self.assertEqual("vertical", request.orientation)
        self.assertEqual("scope-a", request.scope_token)
        self.assertEqual("epoch-1", request.scope_epoch)

    def test_apply_on_startup_true_evaluates_initial_scope_after_dwell(self):
        policy = ArbitrationPolicy(PolicyConfig(apply_on_startup=True, decision_dwell_ms=750))
        self.assertIsNone(policy.observe(obs(width=1000, orientation="vertical"), 0))
        request = policy.observe(obs(width=1000, orientation="vertical"), 750)
        self.assertEqual("horizontal", request.orientation)

    def test_focus_loss_during_pending_requires_fresh_full_dwell_after_recovery(self):
        policy = ArbitrationPolicy(PolicyConfig(decision_dwell_ms=100, min_switch_interval_ms=0))
        policy.observe(obs(width=1300), 0)
        policy.observe(obs(width=1500), 10)
        self.assertIsNone(policy.observe(obs(width=1500, focused=False, eligible=False), 50))
        self.assertIsNone(policy.observe(obs(width=1500), 200))
        self.assertIsNone(policy.observe(obs(width=1500), 299))
        request = policy.observe(obs(width=1500), 300)
        self.assertEqual("vertical", request.orientation)
        self.assertEqual("recovery-requalification", request.reason)

    def test_lock_during_pending_requires_fresh_full_dwell_after_unlock(self):
        policy = ArbitrationPolicy(PolicyConfig(decision_dwell_ms=100, min_switch_interval_ms=0))
        policy.observe(obs(width=1300), 0)
        policy.observe(obs(width=1500), 10)
        self.assertIsNone(policy.observe(obs(width=1500, locked=True), 50))
        self.assertIsNone(policy.observe(obs(width=1500), 500))
        self.assertIsNone(policy.observe(obs(width=1500), 599))
        request = policy.observe(obs(width=1500), 600)
        self.assertEqual("vertical", request.orientation)

    def test_ineligible_fullscreen_immersive_or_kiosk_interruption_requalifies_candidate(self):
        for mode in ("fullscreen", "immersive", "kiosk"):
            with self.subTest(mode=mode):
                policy = ArbitrationPolicy(PolicyConfig(decision_dwell_ms=100, min_switch_interval_ms=0))
                policy.observe(obs(width=1300), 0)
                policy.observe(obs(width=1500), 10)
                self.assertIsNone(policy.observe(obs(width=1500, eligible=False), 50))
                self.assertIsNone(policy.observe(obs(width=1500), 200))
                request = policy.observe(obs(width=1500), 300)
                self.assertEqual("vertical", request.orientation)

    def test_recovery_into_band_clears_interrupted_candidate_then_future_transition_gets_full_dwell(self):
        policy = ArbitrationPolicy(PolicyConfig(decision_dwell_ms=100, min_switch_interval_ms=0))
        policy.observe(obs(width=1300), 0)
        policy.observe(obs(width=1500), 10)
        policy.observe(obs(width=1500, focused=False, eligible=False), 50)

        self.assertIsNone(policy.observe(obs(width=1300), 200))
        self.assertIsNone(policy.observe(obs(width=1500), 300))
        self.assertIsNone(policy.observe(obs(width=1500), 399))
        request = policy.observe(obs(width=1500), 400)
        self.assertEqual("vertical", request.orientation)

    def test_narrow_candidate_recovery_also_requires_full_dwell(self):
        policy = ArbitrationPolicy(PolicyConfig(decision_dwell_ms=100, min_switch_interval_ms=0))
        policy.observe(obs(width=1300, orientation="vertical"), 0)
        policy.observe(obs(width=1000, orientation="vertical"), 10)
        policy.observe(obs(width=1000, eligible=False, focused=False, orientation="vertical"), 50)

        self.assertIsNone(policy.observe(obs(width=1000, orientation="vertical"), 200))
        self.assertIsNone(policy.observe(obs(width=1000, orientation="vertical"), 299))
        request = policy.observe(obs(width=1000, orientation="vertical"), 300)
        self.assertEqual("horizontal", request.orientation)

    def test_ordinary_settled_same_region_focus_away_and_refocus_is_noop(self):
        policy = ArbitrationPolicy(PolicyConfig(apply_on_startup=True, decision_dwell_ms=0, min_switch_interval_ms=0))
        request = policy.observe(obs(width=1500, orientation="horizontal"), 0)
        policy.verify(request, "vertical", 0)

        self.assertIsNone(policy.observe(obs(width=1500, orientation="vertical", focused=False, eligible=False), 10))
        self.assertIsNone(policy.observe(obs(width=1500, orientation="vertical"), 20))
        self.assertIsNone(policy.observe(obs(width=1500, orientation="vertical"), 1000))

    def test_same_scope_window_change_during_pending_resets_dwell(self):
        policy = ArbitrationPolicy(PolicyConfig(decision_dwell_ms=750))
        policy.observe(obs(width=1300), 0)
        policy.observe(obs(window="window-a", width=1500), 100)
        policy.observe(obs(window="window-b", width=1500), 700)
        self.assertIsNone(policy.observe(obs(window="window-b", width=1500), 1400))
        request = policy.observe(obs(window="window-b", width=1500), 1450)
        self.assertEqual("vertical", request.orientation)

    def test_global_min_switch_interval_delays_second_scope_request(self):
        config = PolicyConfig(apply_on_startup=True, decision_dwell_ms=100, min_switch_interval_ms=2000)
        policy = ArbitrationPolicy(config)
        policy.observe(obs(scope="scope-a", width=1500, orientation="horizontal"), 0)
        first = policy.observe(obs(scope="scope-a", width=1500, orientation="horizontal"), 100)
        self.assertEqual("vertical", first.orientation)
        policy.verify(first, "vertical", 100)

        policy.observe(obs(scope="scope-b", epoch="epoch-b", width=1000, orientation="vertical"), 200)
        self.assertIsNone(policy.observe(obs(scope="scope-b", epoch="epoch-b", width=1000, orientation="vertical"), 1000))
        second = policy.observe(obs(scope="scope-b", epoch="epoch-b", width=1000, orientation="vertical"), 2100)
        self.assertEqual("horizontal", second.orientation)

    def test_manual_external_change_suspends_same_region_until_later_effective_transition(self):
        policy = ArbitrationPolicy(PolicyConfig(decision_dwell_ms=100))
        policy.observe(obs(width=1000, orientation="horizontal"), 0)
        self.assertIsNone(policy.observe(obs(width=1000, orientation="vertical"), 10))
        policy.observe(obs(width=1000, orientation="vertical", focused=False, eligible=False), 20)
        self.assertIsNone(policy.observe(obs(width=1000, orientation="vertical"), 30))
        self.assertIsNone(policy.observe(obs(width=1300, orientation="vertical"), 40))
        self.assertIsNone(policy.observe(obs(width=1500, orientation="vertical"), 50))
        self.assertIsNone(policy.observe(obs(width=1300, orientation="vertical"), 60))
        self.assertIsNone(policy.observe(obs(width=1000, orientation="vertical"), 70))
        request = policy.observe(obs(width=1000, orientation="vertical"), 170)
        self.assertEqual("horizontal", request.orientation)

    def test_external_change_after_threshold_crossing_cancels_pending_as_manual(self):
        policy = ArbitrationPolicy(PolicyConfig(decision_dwell_ms=100))
        policy.observe(obs(width=1300, orientation="horizontal"), 0)
        policy.observe(obs(width=1500, orientation="horizontal"), 10)
        self.assertIsNone(policy.observe(obs(width=1500, orientation="vertical"), 50))
        self.assertIsNone(policy.observe(obs(width=1500, orientation="vertical"), 500))

    def test_current_verification_mismatch_owns_manual_override_only_for_request_region(self):
        policy = ArbitrationPolicy(PolicyConfig(apply_on_startup=True, decision_dwell_ms=0, min_switch_interval_ms=0))
        request = policy.observe(obs(width=1500, orientation="horizontal"), 0)
        policy.verify(request, "horizontal", 10)
        self.assertIsNone(policy.observe(obs(width=1500, orientation="horizontal"), 20))
        self.assertIsNone(policy.observe(obs(width=1500, orientation="horizontal"), 500))

    def test_same_token_with_new_epoch_is_new_scope_lifetime(self):
        policy = ArbitrationPolicy(PolicyConfig(apply_on_startup=False, decision_dwell_ms=100))
        policy.observe(obs(scope="shared", epoch="process-a", width=1000, orientation="horizontal"), 0)
        self.assertIsNone(policy.observe(obs(scope="shared", epoch="process-b", width=1500, orientation="horizontal"), 10))
        request = policy.observe(obs(scope="shared", epoch="process-b", width=1500, orientation="horizontal"), 110)
        self.assertEqual("vertical", request.orientation)

    def test_expiring_scope_discards_saved_state_and_pending(self):
        policy = ArbitrationPolicy(PolicyConfig(decision_dwell_ms=100))
        policy.observe(obs(width=1300), 0)
        policy.observe(obs(width=1500), 10)
        policy.expire_scope("scope-a", "epoch-1")
        self.assertIsNone(policy.observe(obs(width=1500), 200))

    def test_valid_config_change_uses_safe_baseline_and_cancels_pending(self):
        policy = ArbitrationPolicy(PolicyConfig(decision_dwell_ms=500, revision="one"))
        policy.observe(obs(width=1300), 0)
        policy.observe(obs(width=1500), 10)
        accepted, error = policy.apply_config({
            "horizontalThreshold": 1100,
            "verticalThreshold": 1300,
            "minimumThresholdGap": 100,
            "decisionDwellMs": 500,
            "minSwitchIntervalMs": 2000,
            "applyOnStartup": False,
            "manualOverridePolicy": "until-next-region-transition",
            "revision": "two",
        }, 100)
        self.assertTrue(accepted, error)
        self.assertIsNone(policy.observe(obs(width=1500), 1000))

    def test_invalid_or_unknown_observation_without_active_candidate_is_noop(self):
        policy = ArbitrationPolicy(PolicyConfig(decision_dwell_ms=100))
        policy.observe(obs(width=1300), 0)
        self.assertIsNone(policy.observe(obs(width=math.nan), 20))
        self.assertIsNone(policy.observe(obs(width=1300), 200))
        self.assertIsNone(policy.observe(obs(width=1300), 1000))

    def test_monotonic_time_rejects_clock_reversal(self):
        policy = ArbitrationPolicy(PolicyConfig())
        policy.observe(obs(), 100)
        with self.assertRaises(ValueError):
            policy.observe(obs(), 99)

    def test_suspend_resume_interrupted_candidate_requires_fresh_full_dwell(self):
        policy = ArbitrationPolicy(PolicyConfig(decision_dwell_ms=100, min_switch_interval_ms=0))
        policy.observe(obs(width=1300), 0)
        policy.observe(obs(width=1500), 10)
        policy.suspend(50)
        policy.resume(1000)
        self.assertIsNone(policy.observe(obs(width=1500), 1010))
        self.assertIsNone(policy.observe(obs(width=1500), 1109))
        request = policy.observe(obs(width=1500), 1110)
        self.assertEqual("vertical", request.orientation)


if __name__ == "__main__":
    unittest.main()
