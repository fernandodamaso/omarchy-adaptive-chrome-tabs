"""Pure fail-closed browser-window eligibility classifier for FDM-822 research."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any, Mapping

DEFAULT_APP_ID_ALLOWLIST = frozenset({
    "google-chrome",
    "google-chrome-stable",
    "chromium",
})

EXPLICIT_NON_CONTROLLING_SURFACES = frozenset({
    "pwa",
    "app",
    "devtools",
    "extension-popup",
    "dialog",
    "file-picker",
    "auth-dialog",
    "pip",
    "first-run",
    "crash-recovery",
    "update-bubble",
})

PRIVACY_SCOPED_SURFACES = frozenset({"incognito", "guest", "managed"})


@dataclass(frozen=True)
class Classification:
    status: str
    reason: str

    @property
    def eligible(self) -> bool:
        return self.status == "eligible"


def _finite_positive_number(value: Any) -> bool:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    return math.isfinite(float(value)) and float(value) > 0


def classify_window(observation: Mapping[str, Any]) -> Classification:
    """Classify normalized compositor evidence without consulting titles or URLs.

    This prototype intentionally requires local qualification to normalize a surface as
    ``normal-tabbed`` and to mark its package identity as qualified. Unknown evidence
    is ambiguous rather than guessed.
    """

    if observation.get("sessionLocked"):
        return Classification("ineligible", "session-locked")

    if not observation.get("active", False):
        return Classification("ineligible", "not-active-toplevel")

    if observation.get("surfaceRole") != "application-toplevel":
        return Classification("ineligible", "not-application-toplevel")

    app_id = str(observation.get("appId") or "").strip().lower()
    if app_id not in DEFAULT_APP_ID_ALLOWLIST:
        return Classification("ineligible", "app-id-not-allowlisted")

    package = observation.get("package")
    if not isinstance(package, Mapping) or package.get("qualified") is not True:
        return Classification("ambiguous", "package-identity-unqualified")

    geometry = observation.get("geometry")
    if not isinstance(geometry, Mapping):
        return Classification("ambiguous", "geometry-missing")
    if geometry.get("unit") != "logical":
        return Classification("ambiguous", "geometry-unit-unverified")
    if not _finite_positive_number(geometry.get("width")) or not _finite_positive_number(geometry.get("height")):
        return Classification("ambiguous", "geometry-invalid")
    if not str(geometry.get("sourceField") or "").strip():
        return Classification("ambiguous", "geometry-source-unqualified")

    if observation.get("fullscreen") or observation.get("immersive") or observation.get("kiosk"):
        return Classification("ineligible", "non-controlling-mode")

    surface_kind = str(observation.get("surfaceKind") or "unknown").strip().lower()
    if surface_kind in EXPLICIT_NON_CONTROLLING_SURFACES:
        return Classification("ineligible", f"surface-{surface_kind}")

    if surface_kind in PRIVACY_SCOPED_SURFACES:
        if observation.get("privacyScopeProven") is not True:
            return Classification("ambiguous", "privacy-scope-unqualified")
        if observation.get("normalIdentityProven") is not True:
            return Classification("ambiguous", "normal-tabbed-identity-unproven")
        return Classification("eligible", "qualified-privacy-surface")

    if surface_kind != "normal-tabbed" or observation.get("normalIdentityProven") is not True:
        return Classification("ambiguous", "normal-tabbed-identity-unproven")

    return Classification("eligible", "qualified-normal-tabbed-browser")
