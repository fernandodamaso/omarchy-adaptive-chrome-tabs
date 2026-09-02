#!/usr/bin/env python3
"""Pure FDM-821 set-decision reference model.

This is research/test code only. It has no browser, accessibility, compositor,
profile, or process side effects.
"""

from dataclasses import dataclass
from typing import Optional

ORIENTATIONS = {"horizontal", "vertical", "unknown"}
SYNC_IMPACTS = {"local-only", "profile-syncable", "unknown"}
PREFERENCE_CONTROLS = {"user", "managed", "unknown"}


@dataclass(frozen=True)
class Decision:
    status: str
    reason_code: str
    orientation: str
    changed: Optional[bool]
    verified: bool
    mutation_allowed: bool = False


def decide_before_mutation(
    *,
    current_orientation: str,
    desired_orientation: str,
    preference_control: str,
    sync_impact: str,
    consent: bool,
) -> Decision:
    """Return the contract outcome before any orientation mutation.

    Ordering is normative for FDM-821:
    1. a trustworthy readback is required;
    2. an already-correct target returns a verified no-op without consent;
    3. managed mismatch fails closed;
    4. consent gates only a real syncable/unknown-impact mutation.
    """

    if current_orientation not in ORIENTATIONS:
        raise ValueError("invalid current orientation")
    if desired_orientation not in {"horizontal", "vertical"}:
        raise ValueError("invalid desired orientation")
    if preference_control not in PREFERENCE_CONTROLS:
        raise ValueError("invalid preference control")
    if sync_impact not in SYNC_IMPACTS:
        raise ValueError("invalid sync impact")

    if current_orientation == "unknown":
        return Decision(
            status="unsupported",
            reason_code="orientation-unreadable",
            orientation="unknown",
            changed=None,
            verified=False,
        )

    if current_orientation == desired_orientation:
        return Decision(
            status="ok",
            reason_code="already-desired",
            orientation=current_orientation,
            changed=False,
            verified=True,
        )

    if preference_control == "managed":
        return Decision(
            status="policy-controlled",
            reason_code="managed-preference",
            orientation=current_orientation,
            changed=False,
            verified=False,
        )

    if sync_impact in {"profile-syncable", "unknown"} and not consent:
        return Decision(
            status="consent-required",
            reason_code="sync-consent-required",
            orientation=current_orientation,
            changed=False,
            verified=False,
        )

    return Decision(
        status="ready-to-mutate",
        reason_code="verified",
        orientation=current_orientation,
        changed=False,
        verified=False,
        mutation_allowed=True,
    )


def verify_after_mutation(
    *,
    desired_orientation: str,
    final_orientation: str,
    target_still_valid: bool = True,
    concurrent_change: bool = False,
) -> Decision:
    """Model the single-write postflight verification outcome."""

    if desired_orientation not in {"horizontal", "vertical"}:
        raise ValueError("invalid desired orientation")
    if final_orientation not in ORIENTATIONS:
        raise ValueError("invalid final orientation")

    if not target_still_valid:
        return Decision(
            status="stale-target",
            reason_code="postflight-target-changed",
            orientation=final_orientation,
            changed=None,
            verified=False,
        )

    if concurrent_change:
        return Decision(
            status="conflict",
            reason_code="concurrent-user-change",
            orientation=final_orientation,
            changed=None,
            verified=False,
        )

    if final_orientation != desired_orientation:
        return Decision(
            status="conflict",
            reason_code="postflight-orientation-mismatch",
            orientation=final_orientation,
            changed=None,
            verified=False,
        )

    return Decision(
        status="ok",
        reason_code="verified",
        orientation=final_orientation,
        changed=True,
        verified=True,
    )
