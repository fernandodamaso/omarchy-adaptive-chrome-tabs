import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "research" / "geometry-arbitration"))

from policy import ArbitrationPolicy, Observation, PolicyConfig
from tests.fakes import FakeAdapterSink, FakeClock


def obs(window, width, orientation, scope="scope-a", epoch="epoch-1"):
    return Observation(
        window_key=window,
        scope_token=scope,
        scope_epoch=epoch,
        width=width,
        orientation=orientation,
        eligible=True,
        focused=True,
        locked=False,
    )


class FakeAdapterTimingTests(unittest.TestCase):
    def test_same_scope_focus_flips_do_not_ping_pong_before_full_dwell(self):
        clock = FakeClock()
        sink = FakeAdapterSink()
        policy = ArbitrationPolicy(PolicyConfig(apply_on_startup=True, decision_dwell_ms=750, min_switch_interval_ms=0))

        policy.observe(obs("wide-window", 1500, "horizontal"), clock.now_ms)
        clock.advance(750)
        first = policy.observe(obs("wide-window", 1500, "horizontal"), clock.now_ms)
        sink.apply_and_verify(policy, first, clock)
        self.assertEqual(["vertical"], [request.orientation for request in sink.requests])

        clock.advance(100)
        policy.observe(obs("narrow-window", 1000, "vertical"), clock.now_ms)
        clock.advance(300)
        self.assertIsNone(policy.observe(obs("wide-window", 1500, "vertical"), clock.now_ms))
        clock.advance(100)
        policy.observe(obs("narrow-window", 1000, "vertical"), clock.now_ms)
        clock.advance(749)
        self.assertIsNone(policy.observe(obs("narrow-window", 1000, "vertical"), clock.now_ms))
        clock.advance(1)
        second = policy.observe(obs("narrow-window", 1000, "vertical"), clock.now_ms)
        sink.apply_and_verify(policy, second, clock)

        self.assertEqual(["vertical", "horizontal"], [request.orientation for request in sink.requests])

    def test_fake_clock_and_global_cooldown_are_deterministic_without_sleep(self):
        clock = FakeClock(1000)
        sink = FakeAdapterSink()
        policy = ArbitrationPolicy(PolicyConfig(apply_on_startup=True, decision_dwell_ms=100, min_switch_interval_ms=2000))

        policy.observe(obs("a", 1500, "horizontal", scope="a", epoch="ea"), clock.now_ms)
        clock.advance(100)
        first = policy.observe(obs("a", 1500, "horizontal", scope="a", epoch="ea"), clock.now_ms)
        sink.apply_and_verify(policy, first, clock)

        clock.advance(100)
        policy.observe(obs("b", 1000, "vertical", scope="b", epoch="eb"), clock.now_ms)
        clock.advance(1000)
        self.assertIsNone(policy.observe(obs("b", 1000, "vertical", scope="b", epoch="eb"), clock.now_ms))
        clock.advance(900)
        second = policy.observe(obs("b", 1000, "vertical", scope="b", epoch="eb"), clock.now_ms)
        sink.apply_and_verify(policy, second, clock)

        self.assertEqual(2, len(sink.requests))
        self.assertEqual("horizontal", sink.requests[-1].orientation)

    def test_delayed_completion_from_old_region_cannot_suppress_fresh_dwell(self):
        clock = FakeClock()
        policy = ArbitrationPolicy(PolicyConfig(apply_on_startup=True, decision_dwell_ms=100, min_switch_interval_ms=0))

        policy.observe(obs("browser", 1500, "horizontal"), clock.now_ms)
        clock.advance(100)
        old_request = policy.observe(obs("browser", 1500, "horizontal"), clock.now_ms)

        clock.advance(10)
        self.assertIsNone(policy.observe(obs("browser", 1000, "horizontal"), clock.now_ms))

        clock.advance(90)
        policy.verify(old_request, "vertical", clock.now_ms)

        clock.advance(1)
        self.assertIsNone(policy.observe(obs("browser", 1000, "vertical"), clock.now_ms))
        clock.advance(100)
        correction = policy.observe(obs("browser", 1000, "vertical"), clock.now_ms)
        self.assertIsNotNone(correction)
        self.assertEqual("horizontal", correction.orientation)

    def test_stale_verification_mismatch_does_not_assign_override_to_new_region(self):
        clock = FakeClock()
        policy = ArbitrationPolicy(PolicyConfig(apply_on_startup=True, decision_dwell_ms=100, min_switch_interval_ms=0))

        policy.observe(obs("browser", 1500, "horizontal"), clock.now_ms)
        clock.advance(100)
        old_request = policy.observe(obs("browser", 1500, "horizontal"), clock.now_ms)

        clock.advance(10)
        policy.observe(obs("browser", 1000, "horizontal"), clock.now_ms)
        clock.advance(10)
        policy.verify(old_request, "horizontal", clock.now_ms)

        state = policy._scopes[("scope-a", "epoch-1")]
        self.assertIsNone(state.manual_override_region)


if __name__ == "__main__":
    unittest.main()
