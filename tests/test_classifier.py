import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "research" / "geometry-arbitration"))

from classifier import classify_window


def observation(**overrides):
    base = {
        "active": True,
        "sessionLocked": False,
        "surfaceRole": "application-toplevel",
        "appId": "google-chrome-stable",
        "initialAppId": "google-chrome-stable",
        "browserChannel": "stable",
        "surfaceKind": "normal-tabbed",
        "normalIdentityProven": True,
        "privacyScopeProven": False,
        "package": {"source": "native", "qualified": True},
        "geometry": {
            "width": 1199.5,
            "height": 900.0,
            "unit": "logical",
            "sourceField": "hyprctl.clients.size[0]",
        },
        "fullscreen": False,
        "immersive": False,
        "kiosk": False,
        "maximized": False,
    }
    base.update(overrides)
    return base


class EligibleWindowClassifierTests(unittest.TestCase):
    def test_allows_proven_normal_stable_native_browser(self):
        result = classify_window(observation())
        self.assertEqual("eligible", result.status)

    def test_unrelated_app_is_ineligible_even_if_title_mentions_chrome(self):
        result = classify_window(observation(appId="com.example.editor", title="Chrome - synthetic"))
        self.assertEqual("ineligible", result.status)
        self.assertEqual("app-id-not-allowlisted", result.reason)

    def test_non_stable_metadata_fails_default_channel_boundary_even_with_allowlisted_app_and_package(self):
        for channel in ("beta", "dev", "canary"):
            with self.subTest(channel=channel):
                result = classify_window(observation(
                    appId="google-chrome",
                    initialAppId="google-chrome",
                    browserChannel=channel,
                    browserChannelQualified=True,
                    package={"source": "native", "qualified": True},
                ))
                self.assertEqual("ineligible", result.status)
                self.assertEqual("browser-channel-not-allowlisted", result.reason)

    def test_non_stable_channel_requires_both_explicit_opt_in_and_separate_qualification(self):
        unqualified = classify_window(
            observation(browserChannel="beta", browserChannelQualified=False),
            allowed_browser_channels={"stable", "beta"},
        )
        self.assertEqual("ambiguous", unqualified.status)
        self.assertEqual("browser-channel-unqualified", unqualified.reason)

        qualified = classify_window(
            observation(browserChannel="beta", browserChannelQualified=True),
            allowed_browser_channels={"stable", "beta"},
        )
        self.assertEqual("eligible", qualified.status)

    def test_unknown_channel_is_ambiguous_even_when_app_and_package_are_allowlisted(self):
        result = classify_window(observation(browserChannel="unknown"))
        self.assertEqual("ambiguous", result.status)
        self.assertEqual("browser-channel-unqualified", result.reason)

    def test_explicit_non_controlling_surface_is_ineligible(self):
        for surface_kind in (
            "pwa",
            "devtools",
            "extension-popup",
            "dialog",
            "file-picker",
            "auth-dialog",
            "pip",
            "first-run",
            "crash-recovery",
            "update-bubble",
        ):
            with self.subTest(surface_kind=surface_kind):
                result = classify_window(observation(surfaceKind=surface_kind))
                self.assertEqual("ineligible", result.status)

    def test_unknown_surface_identity_fails_closed_as_ambiguous(self):
        result = classify_window(observation(surfaceKind="unknown", normalIdentityProven=False))
        self.assertEqual("ambiguous", result.status)
        self.assertEqual("normal-tabbed-identity-unproven", result.reason)

    def test_incognito_guest_and_managed_require_scope_proof(self):
        for surface_kind in ("incognito", "guest", "managed"):
            with self.subTest(surface_kind=surface_kind):
                result = classify_window(observation(surfaceKind=surface_kind))
                self.assertEqual("ambiguous", result.status)
                self.assertEqual("privacy-scope-unqualified", result.reason)

    def test_fullscreen_immersive_and_kiosk_are_non_controlling_but_maximized_is_allowed(self):
        for field in ("fullscreen", "immersive", "kiosk"):
            with self.subTest(field=field):
                result = classify_window(observation(**{field: True}))
                self.assertEqual("ineligible", result.status)
                self.assertEqual("non-controlling-mode", result.reason)
        self.assertEqual("eligible", classify_window(observation(maximized=True)).status)

    def test_unqualified_package_or_wrapper_is_ambiguous(self):
        result = classify_window(observation(package={"source": "wrapper", "qualified": False}))
        self.assertEqual("ambiguous", result.status)
        self.assertEqual("package-identity-unqualified", result.reason)

    def test_geometry_must_be_finite_positive_and_logical(self):
        bad_geometries = [
            {"width": 0, "height": 900, "unit": "logical", "sourceField": "hyprctl.clients.size[0]"},
            {"width": -1, "height": 900, "unit": "logical", "sourceField": "hyprctl.clients.size[0]"},
            {"width": math.nan, "height": 900, "unit": "logical", "sourceField": "hyprctl.clients.size[0]"},
            {"width": 1200, "height": 900, "unit": "unverified", "sourceField": "hyprctl.clients.size[0]"},
        ]
        for geometry in bad_geometries:
            with self.subTest(geometry=geometry):
                result = classify_window(observation(geometry=geometry))
                self.assertEqual("ambiguous", result.status)

    def test_non_allowlisted_channel_specific_app_ids_remain_ineligible(self):
        for app_id in ("google-chrome-beta", "google-chrome-unstable", "chromium-dev"):
            with self.subTest(app_id=app_id):
                result = classify_window(observation(appId=app_id, initialAppId=app_id))
                self.assertEqual("ineligible", result.status)


if __name__ == "__main__":
    unittest.main()
