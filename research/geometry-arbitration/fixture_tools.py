"""Sanitization helpers for FDM-822 local-only Hyprland captures."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any, Mapping


def _positive_number(value: Any) -> bool:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    return math.isfinite(float(value)) and float(value) > 0


def sanitize_hyprland_client(
    raw: Mapping[str, Any],
    *,
    fixture_id: str,
    surface_kind: str = "unknown",
    package_source: str = "unknown",
    package_qualified: bool = False,
    display_mode: str = "unknown",
) -> dict[str, Any]:
    """Retain only non-sensitive fields needed for geometry/classification research.

    Titles, URLs, workspace names, addresses, PIDs, command lines, profile data, and
    other transient identifiers are deliberately omitted. Geometry units remain
    ``unverified`` until the local qualification run proves logical compositor pixels.
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
            "browserChannel": "stable" if app_id in {"google-chrome", "google-chrome-stable", "chromium"} else "unknown",
            "surfaceKind": surface_kind,
            "normalIdentityProven": False,
            "privacyScopeProven": False,
            "package": {
                "source": package_source,
                "qualified": bool(package_qualified),
            },
            "displayMode": display_mode,
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
        "qualificationNotes": [
            "Local operator must prove surface identity, package identity, geometry field, and logical-unit semantics before promotion.",
        ],
    }


def _cli() -> int:
    parser = argparse.ArgumentParser(description="Sanitize one local Hyprland client JSON object for FDM-822 review.")
    parser.add_argument("input", type=Path, help="Ignored local JSON file containing one client object")
    parser.add_argument("output", type=Path, help="Ignored local output path; do not commit without manual qualification")
    parser.add_argument("--fixture-id", required=True)
    parser.add_argument("--surface-kind", default="unknown")
    parser.add_argument("--package-source", default="unknown")
    parser.add_argument("--package-qualified", action="store_true")
    parser.add_argument("--display-mode", default="unknown")
    args = parser.parse_args()

    raw = json.loads(args.input.read_text(encoding="utf-8"))
    fixture = sanitize_hyprland_client(
        raw,
        fixture_id=args.fixture_id,
        surface_kind=args.surface_kind,
        package_source=args.package_source,
        package_qualified=args.package_qualified,
        display_mode=args.display_mode,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(fixture, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(_cli())
