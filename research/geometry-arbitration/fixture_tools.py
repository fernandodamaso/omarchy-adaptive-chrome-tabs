"""Sanitization helpers for FDM-822 local-only Hyprland captures."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any, Mapping


BROWSER_CHANNELS = frozenset({"stable", "beta", "dev", "canary", "unknown"})
PACKAGE_SOURCES = frozenset({"native", "flatpak", "snap", "wrapper", "unknown"})
DISPLAY_MODES = frozenset({"native-wayland", "xwayland", "unknown"})


def _positive_number(value: Any) -> bool:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    return math.isfinite(float(value)) and float(value) > 0


def _choice(value: str, *, field: str, allowed: frozenset[str]) -> str:
    normalized = str(value or "").strip().lower()
    if normalized not in allowed:
        raise ValueError(f"{field} must be one of: {', '.join(sorted(allowed))}")
    return normalized


def sanitize_hyprland_client(
    raw: Mapping[str, Any],
    *,
    fixture_id: str,
    surface_kind: str = "unknown",
    package_source: str = "unknown",
    package_qualified: bool = False,
    browser_channel: str = "unknown",
    browser_channel_qualified: bool = False,
    display_mode: str = "unknown",
) -> dict[str, Any]:
    """Retain only non-sensitive fields needed for geometry/classification research.

    Titles, URLs, workspace names, addresses, PIDs, command lines, profile data, and
    other transient identifiers are deliberately omitted. Geometry units remain
    ``unverified`` until the local qualification run proves logical compositor pixels.
    Browser channel is never inferred from an app ID; the local operator must supply
    and separately qualify it.
    """

    if not isinstance(raw, Mapping):
        raise ValueError("raw client must be a mapping")
    if not isinstance(fixture_id, str) or not fixture_id.strip():
        raise ValueError("fixture_id must be non-empty")

    size = raw.get("size")
    if not isinstance(size, (list, tuple)) or len(size) < 2:
        raise ValueError("raw client requires size[width,height]")
    width, height = size[0], size[1]
    if not _positive_number(width) or not _positive_number(height):
        raise ValueError("raw client size must be finite and positive")

    channel = _choice(browser_channel, field="browser_channel", allowed=BROWSER_CHANNELS)
    source = _choice(package_source, field="package_source", allowed=PACKAGE_SOURCES)
    mode = _choice(display_mode, field="display_mode", allowed=DISPLAY_MODES)

    app_id = str(raw.get("class") or "").strip()
    initial_app_id = str(raw.get("initialClass") or app_id).strip()

    return {
        "schemaVersion": 1,
        "fixtureId": fixture_id.strip(),
        "issue": "FDM-822",
        "provenance": {
            "kind": "local-sanitized",
            "stackFingerprint": "LOCAL_EVIDENCE_PENDING",
            "capture": "single-shot-hyprctl-client",
        },
        "observation": {
            "active": True,
            "sessionLocked": False,
            "surfaceRole": "application-toplevel",
            "appId": app_id,
            "initialAppId": initial_app_id,
            "browserChannel": channel,
            "browserChannelQualified": bool(browser_channel_qualified),
            "surfaceKind": str(surface_kind or "unknown").strip().lower(),
            "normalIdentityProven": False,
            "privacyScopeProven": False,
            "package": {
                "source": source,
                "qualified": bool(package_qualified),
            },
            "displayMode": mode,
            "geometry": {
                "width": float(width),
                "height": float(height),
                "unit": "unverified",
                "sourceField": "hyprctl.clients.size[0]",
            },
            "mapped": bool(raw.get("mapped", True)),
            "hidden": bool(raw.get("hidden", False)),
            "floating": bool(raw.get("floating", False)),
            "xwayland": bool(raw.get("xwayland", False)),
            "pinned": bool(raw.get("pinned", False)),
            "fullscreen": bool(raw.get("fullscreen", False)),
            "immersive": False,
            "kiosk": False,
            "maximized": False,
        },
        "expectedClassification": "ambiguous",
        "notes": [
            "Local operator must prove channel, surface identity, package identity, geometry field, and logical-unit semantics before promotion.",
        ],
    }


def _cli() -> int:
    parser = argparse.ArgumentParser(description="Sanitize one local Hyprland client JSON object for FDM-822 review.")
    parser.add_argument("input", type=Path, help="Ignored local JSON file containing one client object")
    parser.add_argument("output", type=Path, help="Ignored local output path; do not commit without manual qualification")
    parser.add_argument("--fixture-id", required=True)
    parser.add_argument("--surface-kind", default="unknown")
    parser.add_argument("--package-source", choices=sorted(PACKAGE_SOURCES), default="unknown")
    parser.add_argument("--package-qualified", action="store_true")
    parser.add_argument("--browser-channel", choices=sorted(BROWSER_CHANNELS), default="unknown")
    parser.add_argument("--browser-channel-qualified", action="store_true")
    parser.add_argument("--display-mode", choices=sorted(DISPLAY_MODES), default="unknown")
    args = parser.parse_args()

    raw = json.loads(args.input.read_text(encoding="utf-8"))
    fixture = sanitize_hyprland_client(
        raw,
        fixture_id=args.fixture_id,
        surface_kind=args.surface_kind,
        package_source=args.package_source,
        package_qualified=args.package_qualified,
        browser_channel=args.browser_channel,
        browser_channel_qualified=args.browser_channel_qualified,
        display_mode=args.display_mode,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(fixture, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(_cli())
