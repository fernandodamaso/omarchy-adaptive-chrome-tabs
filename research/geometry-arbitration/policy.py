"""Pure deterministic arbitration prototype for FDM-822 research.

This module has no browser or compositor side effects. Time is injected by callers as
monotonic elapsed milliseconds. Preference scope tokens are opaque and are combined
with an explicit lifetime/epoch so recycled tokens cannot collide with stale state.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any, Mapping, Optional


class ConfigError(ValueError):
    pass


@dataclass(frozen=True)
class PolicyConfig:
    horizontal_threshold: int = 1200
    vertical_threshold: int = 1400
    decision_dwell_ms: int = 750
    min_switch_interval_ms: int = 2000
    minimum_threshold_gap: int = 100
    apply_on_startup: bool = False
    manual_override_policy: str = "until-next-region-transition"
    revision: str = "default"

    @classmethod
    def from_mapping(cls, mapping: Mapping[str, Any]) -> "PolicyConfig":
        if not isinstance(mapping, Mapping):
            raise ConfigError("configuration must be a mapping")

        allowed = {
            "horizontalThreshold",
            "verticalThreshold",
            "decisionDwellMs",
            "minSwitchIntervalMs",
            "minimumThresholdGap",
            "applyOnStartup",
            "manualOverridePolicy",
            "revision",
        }
        unknown = sorted(set(mapping) - allowed)
        if unknown:
            raise ConfigError(f"unknown configuration fields: {', '.join(unknown)}")

        defaults = cls()

        def integer(name: str, default: int, *, minimum: int, maximum: int) -> int:
            value = mapping.get(name, default)
            if isinstance(value, bool) or not isinstance(value, int):
                raise ConfigError(f"{name} must be an integer")
            if value < minimum or value > maximum:
                raise ConfigError(f"{name} must be in range {minimum}..{maximum}")
            return value

        horizontal = integer("horizontalThreshold", defaults.horizontal_threshold, minimum=400, maximum=10000)
        vertical = integer("verticalThreshold", defaults.vertical_threshold, minimum=400, maximum=10000)
        gap = integer("minimumThresholdGap", defaults.minimum_threshold_gap, minimum=1, maximum=9600)
        dwell = integer("decisionDwellMs", defaults.decision_dwell_ms, minimum=0, maximum=60000)
        cooldown = integer("minSwitchIntervalMs", defaults.min_switch_interval_ms, minimum=0, maximum=60000)

        if horizontal + gap > vertical:
            raise ConfigError("minimum threshold gap is not satisfied")

        apply = mapping.get("applyOnStartup", defaults.apply_on_startup)
        if not isinstance(apply, bool):
            raise ConfigError("applyOnStartup must be boolean")

        manual = mapping.get("manualOverridePolicy", defaults.manual_override_policy)
        if manual != "until-next-region-transition":
            raise ConfigError("manualOverridePolicy is unsupported")

        revision = mapping.get("revision", defaults.revision)
        if not isinstance(revision, str) or not revision.strip():
            raise ConfigError("revision must be a non-empty string")

        return cls(
            horizontal_threshold=horizontal,
            vertical_threshold=vertical,
            decision_dwell_ms=dwell,
            min_switch_interval_ms=cooldown,
            minimum_threshold_gap=gap,
            apply_on_startup=apply,
            manual_override_policy=manual,
            revision=revision.strip(),
        )


@dataclass(frozen=True)
class Observation:
    window_key: str
    scope_token: str
    scope_epoch: str
    width: float
    orientation: str
    eligible: bool
    focused: bool
    locked: bool = False


@dataclass(frozen=True)
class SwitchRequest:
    window_key: str
    scope_token: str
    scope_epoch: str
    orientation: str
    region: str
    reason: str
    generation: int


@dataclass
class _ScopeState:
    region: str
    known_orientation: str
    last_width: float
    current_window_key: str
    manual_override_region: Optional[str] = None
    expected_orientation: Optional[str] = None
    inflight_generation: Optional[int] = None
    inflight_window_key: Optional[str] = None
    inflight_region: Optional[str] = None
    requalification_required: bool = False
    stale_completion_orientation: Optional[str] = None


@dataclass
class _Pending:
    scope_token: str
    scope_epoch: str
    window_key: str
    region: str
    desired_orientation: str
    started_ms: int
    reason: str


VALID_ORIENTATIONS = frozenset({"horizontal", "vertical"})


def _valid_width(width: Any) -> bool:
    if isinstance(width, bool) or not isinstance(width, (int, float)):
        return False
    return math.isfinite(float(width)) and float(width) > 0


def region_for_width(width: float, config: PolicyConfig) -> str:
    if not _valid_width(width):
        raise ValueError("width must be finite and positive")
    value = float(width)
    if value <= config.horizontal_threshold:
        return "narrow"
    if value >= config.vertical_threshold:
        return "wide"
    return "band"


def desired_orientation(region: str) -> Optional[str]:
    if region == "narrow":
        return "horizontal"
    if region == "wide":
        return "vertical"
    return None


def resolve_config(candidate: Mapping[str, Any], prior: Optional[PolicyConfig]):
    try:
        return PolicyConfig.from_mapping(candidate), True, ""
    except ConfigError as exc:
        return prior, False, str(exc)


class ArbitrationPolicy:
    """State machine prototype that returns requests instead of invoking an adapter.

    The first observation after construction is the enable/reload snapshot. With
    ``apply_on_startup=False`` only an eligible target in that snapshot is baselined.
    If the snapshot contains no eligible target, the next eligible target is evaluated
    normally and must satisfy the full dwell.
    """

    def __init__(self, config: PolicyConfig):
        self.config = config
        self._scopes: dict[tuple[str, str], _ScopeState] = {}
        self._pending: Optional[_Pending] = None
        self._startup_snapshot_consumed = False
        self._last_emit_ms: Optional[int] = None
        self._last_now_ms: Optional[int] = None
        self._suspended = False
        self._next_generation = 1

    def _check_time(self, now_ms: int) -> None:
        if isinstance(now_ms, bool) or not isinstance(now_ms, int) or now_ms < 0:
            raise ValueError("now_ms must be a non-negative monotonic integer")
        if self._last_now_ms is not None and now_ms < self._last_now_ms:
            raise ValueError("monotonic time moved backwards")
        self._last_now_ms = now_ms

    @staticmethod
    def _scope_key(observation: Observation) -> Optional[tuple[str, str]]:
        token = str(observation.scope_token or "").strip()
        epoch = str(observation.scope_epoch or "").strip()
        if not token or not epoch:
            return None
        return token, epoch

    def _cancel_pending(self) -> None:
        self._pending = None

    @staticmethod
    def _clear_inflight(state: _ScopeState) -> None:
        state.expected_orientation = None
        state.inflight_generation = None
        state.inflight_window_key = None
        state.inflight_region = None

    def _pending_scope_key(self) -> Optional[tuple[str, str]]:
        if self._pending is None:
            return None
        return self._pending.scope_token, self._pending.scope_epoch

    def _invalidate_active_work_for_recovery(self) -> None:
        """Cancel active candidate/request work while preserving a fresh-dwell obligation."""
        pending_key = self._pending_scope_key()
        if pending_key is not None:
            state = self._scopes.get(pending_key)
            if state is not None:
                state.requalification_required = True
        self._cancel_pending()

        for state in self._scopes.values():
            if state.inflight_generation is not None:
                state.requalification_required = True
                self._clear_inflight(state)

    def _start_pending(
        self,
        *,
        key: tuple[str, str],
        window_key: str,
        region: str,
        desired: str,
        now_ms: int,
        reason: str,
    ) -> None:
        self._pending = _Pending(
            scope_token=key[0],
            scope_epoch=key[1],
            window_key=window_key,
            region=region,
            desired_orientation=desired,
            started_ms=now_ms,
            reason=reason,
        )

    def observe(self, observation: Observation, now_ms: int) -> Optional[SwitchRequest]:
        self._check_time(now_ms)

        startup_snapshot = not self._startup_snapshot_consumed
        self._startup_snapshot_consumed = True

        if self._suspended:
            self._invalidate_active_work_for_recovery()
            return None

        key = self._scope_key(observation)
        valid = (
            not observation.locked
            and observation.focused
            and observation.eligible
            and key is not None
            and _valid_width(observation.width)
            and observation.orientation in VALID_ORIENTATIONS
            and bool(str(observation.window_key or "").strip())
        )
        if not valid:
            self._invalidate_active_work_for_recovery()
            return None

        assert key is not None
        region = region_for_width(observation.width, self.config)
        desired = desired_orientation(region)
        state = self._scopes.get(key)

        if state is None:
            state = _ScopeState(
                region=region,
                known_orientation=observation.orientation,
                last_width=float(observation.width),
                current_window_key=observation.window_key,
            )
            self._scopes[key] = state

            if startup_snapshot and not self.config.apply_on_startup:
                self._cancel_pending()
                return None

            if desired is not None and desired != observation.orientation:
                self._start_pending(
                    key=key,
                    window_key=observation.window_key,
                    region=region,
                    desired=desired,
                    now_ms=now_ms,
                    reason="initial-scope-evaluation",
                )
            return self._maybe_emit(observation, now_ms)

        previous_region = state.region
        manual_changed_now = False

        # A request stops being current as soon as its scope/window/region binding no
        # longer matches the live eligible target. Its completion must verify as stale.
        invalidated_expected_orientation: Optional[str] = None
        if state.inflight_generation is not None and (
            state.inflight_window_key != observation.window_key
            or state.inflight_region != region
        ):
            invalidated_expected_orientation = state.expected_orientation
            state.requalification_required = True
            self._clear_inflight(state)

        state.current_window_key = observation.window_key

        # A stale request may have applied before or after its binding was invalidated.
        # Treat that owned orientation as a recovery signal, not a manual override.
        if state.expected_orientation is None and observation.orientation != state.known_orientation:
            if (
                state.stale_completion_orientation == observation.orientation
                or invalidated_expected_orientation == observation.orientation
            ):
                state.known_orientation = observation.orientation
                if state.stale_completion_orientation == observation.orientation:
                    state.stale_completion_orientation = None
            else:
                state.known_orientation = observation.orientation
                state.manual_override_region = region
                manual_changed_now = True
                self._cancel_pending()
        elif state.stale_completion_orientation == observation.orientation:
            state.stale_completion_orientation = None

        region_changed = region != previous_region
        state.last_width = float(observation.width)

        if state.requalification_required:
            state.requalification_required = False
            state.region = region

            if region == "band":
                self._cancel_pending()
                return None

            if state.manual_override_region is not None and state.manual_override_region != region and not manual_changed_now:
                state.manual_override_region = None

            if manual_changed_now or state.manual_override_region == region:
                self._cancel_pending()
                return None

            if desired is not None and desired != observation.orientation:
                self._start_pending(
                    key=key,
                    window_key=observation.window_key,
                    region=region,
                    desired=desired,
                    now_ms=now_ms,
                    reason="recovery-requalification",
                )
            else:
                self._cancel_pending()
                state.known_orientation = observation.orientation
            return self._maybe_emit(observation, now_ms)

        if region_changed:
            state.region = region

            if region == "band":
                self._cancel_pending()
                return None

            if state.manual_override_region is not None and not manual_changed_now:
                state.manual_override_region = None

            if manual_changed_now:
                return None

            if desired is not None and desired != observation.orientation and state.manual_override_region != region:
                self._start_pending(
                    key=key,
                    window_key=observation.window_key,
                    region=region,
                    desired=desired,
                    now_ms=now_ms,
                    reason="effective-region-transition",
                )
            else:
                self._cancel_pending()
                state.known_orientation = observation.orientation
                return None

        elif self._pending is not None:
            pending_key = (self._pending.scope_token, self._pending.scope_epoch)
            if pending_key != key or self._pending.region != region:
                self._cancel_pending()
                return None
            if self._pending.window_key != observation.window_key:
                self._start_pending(
                    key=key,
                    window_key=observation.window_key,
                    region=region,
                    desired=self._pending.desired_orientation,
                    now_ms=now_ms,
                    reason="candidate-window-changed",
                )

        state.last_width = float(observation.width)
        return self._maybe_emit(observation, now_ms)

    def _maybe_emit(self, observation: Observation, now_ms: int) -> Optional[SwitchRequest]:
        pending = self._pending
        if pending is None:
            return None
        key = self._scope_key(observation)
        if key != (pending.scope_token, pending.scope_epoch):
            self._cancel_pending()
            return None
        if observation.window_key != pending.window_key:
            return None
        if region_for_width(observation.width, self.config) != pending.region:
            self._cancel_pending()
            return None
        if now_ms - pending.started_ms < self.config.decision_dwell_ms:
            return None
        if self._last_emit_ms is not None and now_ms - self._last_emit_ms < self.config.min_switch_interval_ms:
            return None

        state = self._scopes[key]
        if state.manual_override_region == pending.region:
            self._cancel_pending()
            return None

        generation = self._next_generation
        self._next_generation += 1
        request = SwitchRequest(
            window_key=pending.window_key,
            scope_token=pending.scope_token,
            scope_epoch=pending.scope_epoch,
            orientation=pending.desired_orientation,
            region=pending.region,
            reason=pending.reason,
            generation=generation,
        )
        state.expected_orientation = pending.desired_orientation
        state.inflight_generation = generation
        state.inflight_window_key = pending.window_key
        state.inflight_region = pending.region
        self._last_emit_ms = now_ms
        self._cancel_pending()
        return request

    def verify(self, request: SwitchRequest, actual_orientation: str, now_ms: int) -> bool:
        """Accept verification only for the request still current for its binding.

        Returns ``True`` when the completion belongs to the current request. Stale
        completions return ``False`` and cannot update known/manual state. A stale
        completion does force conservative requalification so any late side effect is
        observed afresh and must satisfy a full dwell before a correcting request.
        """

        self._check_time(now_ms)
        if actual_orientation not in VALID_ORIENTATIONS:
            raise ValueError("actual_orientation must be horizontal or vertical")
        key = (request.scope_token, request.scope_epoch)
        state = self._scopes.get(key)
        if state is None:
            return False

        current = (
            state.inflight_generation == request.generation
            and state.inflight_window_key == request.window_key
            and state.inflight_region == request.region
            and state.expected_orientation == request.orientation
            and state.current_window_key == request.window_key
            and state.region == request.region
        )
        if not current:
            state.stale_completion_orientation = actual_orientation
            state.requalification_required = True

            pending_key = self._pending_scope_key()
            if pending_key == key:
                self._cancel_pending()

            # If a newer request exists for this scope, the stale completion may race
            # with it too; invalidate that request rather than accepting either result.
            if state.inflight_generation is not None:
                self._clear_inflight(state)
            return False

        state.known_orientation = actual_orientation
        self._clear_inflight(state)
        if actual_orientation != request.orientation:
            state.manual_override_region = request.region
        return True

    def expire_scope(self, token: str, epoch: str) -> None:
        key = (token, epoch)
        self._scopes.pop(key, None)
        if self._pending and (self._pending.scope_token, self._pending.scope_epoch) == key:
            self._cancel_pending()

    def apply_config(self, candidate: Mapping[str, Any], now_ms: int):
        self._check_time(now_ms)
        resolved, accepted, error = resolve_config(candidate, self.config)
        if not accepted or resolved is None:
            return False, error

        if resolved == self.config:
            return True, ""

        self.config = resolved
        self._cancel_pending()

        # Safe choice required by FDM-822: baseline all currently known scopes on a
        # valid config revision. No request is created by the revision itself. Any old
        # in-flight request is no longer current under the new revision.
        for state in self._scopes.values():
            self._clear_inflight(state)
            state.requalification_required = False
            state.stale_completion_orientation = None
            if _valid_width(state.last_width):
                state.region = region_for_width(state.last_width, self.config)
        return True, ""

    def suspend(self, now_ms: int) -> None:
        self._check_time(now_ms)
        self._suspended = True
        self._invalidate_active_work_for_recovery()

    def resume(self, now_ms: int) -> None:
        self._check_time(now_ms)
        self._suspended = False
        # The recovery obligation established by suspend is intentionally retained.
