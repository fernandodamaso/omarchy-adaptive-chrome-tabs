#!/usr/bin/env python3
"""Deterministic read-only AT-SPI probe for FDM-821.

The probe matches an AT-SPI application to an already-validated browser PID,
walks only bounded native browser-chrome accessibility nodes, prunes web/document
subtrees, and serializes only role names plus boolean state/action predicates.
Accessible names are read only in memory to classify a possible state-specific
orientation menu item and are never emitted.
"""

import argparse
import json
import re
import sys
from typing import Any

ORIENTATION_LABEL = re.compile(
    r"(?:move|switch|mover|alterar).*(?:tab|tabs|aba|abas|guia|guias|separador|separadores).*(?:side|vertical|top|horizontal|lado|lateral|topo)",
    re.IGNORECASE,
)
PRUNED_ROLE_PARTS = ("document", "web", "embedded")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pid", type=int, required=True, help="validated focused browser PID")
    parser.add_argument("--browser-family", choices=("chrome", "chromium"), required=True)
    parser.add_argument("--max-depth", type=int, default=4)
    parser.add_argument("--max-nodes", type=int, default=256)
    return parser.parse_args()


def load_atspi():
    import gi  # type: ignore

    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi  # type: ignore

    return Atspi


def role_name(accessible: Any) -> str:
    try:
        value = accessible.get_role_name()
    except Exception:
        return "unknown"
    value = str(value or "unknown").strip().lower()
    return value or "unknown"


def state_contains(accessible: Any, state_type: Any) -> bool:
    try:
        return bool(accessible.get_state_set().contains(state_type))
    except Exception:
        return False


def action_count(accessible: Any) -> int:
    try:
        iface = accessible.get_action_iface()
        if iface is None:
            return 0
        return max(0, int(iface.get_n_actions()))
    except Exception:
        return 0


def orientation_action_candidate(accessible: Any, has_action: bool) -> bool:
    if not has_action:
        return False
    try:
        # Name is intentionally never returned or logged.
        name = str(accessible.get_name() or "")
    except Exception:
        return False
    return bool(ORIENTATION_LABEL.search(name))


def child_count(accessible: Any) -> int:
    try:
        return max(0, int(accessible.get_child_count()))
    except Exception:
        return 0


def child_at(accessible: Any, index: int) -> Any:
    try:
        return accessible.get_child_at_index(index)
    except Exception:
        return None


def main() -> int:
    args = parse_args()
    if args.pid <= 0 or args.max_depth < 0 or args.max_nodes <= 0:
        raise SystemExit("invalid probe bounds")

    try:
        Atspi = load_atspi()
        desktop = Atspi.get_desktop(0)
    except Exception as exc:
        json.dump(
            {
                "schemaVersion": 1,
                "browserFamily": args.browser_family,
                "probeAvailable": False,
                "applicationMatched": False,
                "error": type(exc).__name__,
            },
            sys.stdout,
            sort_keys=True,
        )
        sys.stdout.write("\n")
        return 1

    matches = []
    for index in range(child_count(desktop)):
        app = child_at(desktop, index)
        if app is None:
            continue
        try:
            process_id = int(app.get_process_id())
        except Exception:
            continue
        if process_id == args.pid:
            matches.append(app)

    nodes = []
    top_level_frame_count = 0

    def visit(accessible: Any, depth: int, top_level: bool) -> None:
        nonlocal top_level_frame_count
        if accessible is None or depth > args.max_depth or len(nodes) >= args.max_nodes:
            return

        role = role_name(accessible)
        if any(part in role for part in PRUNED_ROLE_PARTS):
            return

        has_action = action_count(accessible) > 0
        focused = state_contains(accessible, Atspi.StateType.FOCUSED)
        enabled = state_contains(accessible, Atspi.StateType.ENABLED)
        candidate = orientation_action_candidate(accessible, has_action)

        if top_level and "frame" in role:
            top_level_frame_count += 1

        nodes.append(
            {
                "role": role,
                "topLevel": bool(top_level),
                "focused": focused,
                "enabled": enabled,
                "hasAction": has_action,
                "orientationActionCandidate": candidate,
            }
        )

        for child_index in range(child_count(accessible)):
            visit(child_at(accessible, child_index), depth + 1, False)
            if len(nodes) >= args.max_nodes:
                break

    for app in matches:
        app_has_action = action_count(app) > 0
        nodes.append(
            {
                "role": role_name(app),
                "topLevel": False,
                "focused": state_contains(app, Atspi.StateType.FOCUSED),
                "enabled": state_contains(app, Atspi.StateType.ENABLED),
                "hasAction": app_has_action,
                "orientationActionCandidate": orientation_action_candidate(app, app_has_action),
            }
        )
        for index in range(child_count(app)):
            visit(child_at(app, index), 0, True)
            if len(nodes) >= args.max_nodes:
                break

    top_level_nodes = [node for node in nodes if node["topLevel"]]
    result = {
        "schemaVersion": 1,
        "browserFamily": args.browser_family,
        "probeAvailable": True,
        "applicationMatched": len(matches) == 1,
        "matchedApplicationCount": len(matches),
        "topLevelFrameCount": top_level_frame_count,
        "anyTopLevelFocused": any(node["focused"] for node in top_level_nodes),
        "anyActionCapability": any(node["hasAction"] for node in nodes),
        "stateSpecificOrientationActionObserved": any(
            node["orientationActionCandidate"] for node in nodes
        ),
        "menuOpenAttempted": False,
        "orientationMutationAttempted": False,
        "webDocumentSubtreesPruned": True,
        "truncated": len(nodes) >= args.max_nodes,
        "nodes": nodes,
    }
    json.dump(result, sys.stdout, sort_keys=True, separators=(",", ":"))
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
