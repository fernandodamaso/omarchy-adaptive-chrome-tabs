#!/usr/bin/env python3
"""One-shot, sanitized Hyprland geometry capture helper for FDM-822.

The helper never loops and never records titles, URLs, PIDs, window addresses,
workspace names, monitor descriptions, make/model, or serial numbers. Its output is
local evidence only and remains under a gitignored raw/ directory by default.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
from typing import Any, Mapping, Sequence


OPTION_NAMES = (
    "general:border_size",
    "general:gaps_in",
    "general:gaps_out",
    "decoration:rounding",
)


def _workspace_id(value: Any) -> Any:
    if isinstance(value, Mapping):
        return value.get("id")
    return None


def sanitize_client_record(raw: Mapping[str, Any]) -> dict[str, Any]:
    size = raw.get("size")
    at = raw.get("at")
    return {
        "appId": str(raw.get("class") or ""),
        "initialAppId": str(raw.get("initialClass") or raw.get("class") or ""),
        "size": list(size[:2]) if isinstance(size, (list, tuple)) and len(size) >= 2 else None,
        "position": list(at[:2]) if isinstance(at, (list, tuple)) and len(at) >= 2 else None,
        "fullscreenRaw": raw.get("fullscreen"),
        "fullscreenClientRaw": raw.get("fullscreenClient"),
        "floating": bool(raw.get("floating", False)),
        "xwayland": bool(raw.get("xwayland", False)),
        "mapped": bool(raw.get("mapped", False)),
        "hidden": bool(raw.get("hidden", False)),
        "monitorId": raw.get("monitor"),
        "workspaceId": _workspace_id(raw.get("workspace")),
    }


def sanitize_monitor_record(raw: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "id": raw.get("id"),
        "name": str(raw.get("name") or ""),
        "x": raw.get("x"),
        "y": raw.get("y"),
        "width": raw.get("width"),
        "height": raw.get("height"),
        "refreshRate": raw.get("refreshRate"),
        "scale": raw.get("scale"),
        "transform": raw.get("transform"),
        "activeWorkspaceId": _workspace_id(raw.get("activeWorkspace")),
        "specialWorkspaceId": _workspace_id(raw.get("specialWorkspace")),
        "disabled": bool(raw.get("disabled", False)),
    }


def _run_json(command: Sequence[str]) -> Any:
    completed = subprocess.run(
        list(command),
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=5,
    )
    return json.loads(completed.stdout or "null")


def _option_value(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, Mapping):
        return {"available": False}
    clean = {"available": True}
    for key in ("int", "float", "str", "set"):
        value = raw.get(key)
        if isinstance(value, (bool, int, float, str)) or value is None:
            clean[key] = value
    return clean


def capture(section: str) -> dict[str, Any]:
    result: dict[str, Any] = {
        "schemaVersion": 1,
        "issue": "FDM-822",
        "evidenceStatus": "LOCAL_ONLY_UNQUALIFIED",
        "warning": "Do not infer GO/NO-GO or logical-unit semantics from this snapshot alone.",
    }

    if section in {"active", "all"}:
        active = _run_json(("hyprctl", "activewindow", "-j"))
        result["activeWindow"] = sanitize_client_record(active) if isinstance(active, Mapping) and active else None

    if section in {"clients", "all"}:
        clients = _run_json(("hyprctl", "clients", "-j"))
        result["clients"] = [sanitize_client_record(item) for item in clients] if isinstance(clients, list) else []

    if section in {"monitors", "all"}:
        monitors = _run_json(("hyprctl", "monitors", "-j"))
        result["monitors"] = [sanitize_monitor_record(item) for item in monitors] if isinstance(monitors, list) else []

    if section in {"options", "all"}:
        options = {}
        for name in OPTION_NAMES:
            options[name] = _option_value(_run_json(("hyprctl", "getoption", name, "-j")))
        result["options"] = options

    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Capture one sanitized Hyprland snapshot for FDM-822 local research.")
    parser.add_argument("--section", choices=("active", "clients", "monitors", "options", "all"), default="all")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).with_name("raw") / "geometry-snapshot.local.json",
        help="Local output path. The default raw/ path is gitignored.",
    )
    args = parser.parse_args()

    data = capture(args.section)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
