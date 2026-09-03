#!/usr/bin/env python3
"""Bounded Hyprland socket2 event-name probe for FDM-822 local research.

Only event names and relative monotonic milliseconds are written. Event payloads are
never persisted, so window titles/classes/workspace names from socket2 stay out of the
capture. This helper does not call hyprctl and is not a polling loop.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import selectors
import socket
import time
from typing import Optional


def parse_event_name(line: bytes) -> Optional[str]:
    if b">>" not in line:
        return None
    name, _payload = line.split(b">>", 1)
    decoded = name.decode("utf-8", errors="replace").strip()
    if not decoded:
        return None
    return decoded


def socket_path() -> Path:
    runtime = os.environ.get("XDG_RUNTIME_DIR")
    signature = os.environ.get("HYPRLAND_INSTANCE_SIGNATURE")
    if not runtime or not signature:
        raise RuntimeError("XDG_RUNTIME_DIR and HYPRLAND_INSTANCE_SIGNATURE are required")
    return Path(runtime) / "hypr" / signature / ".socket2.sock"


def capture_event_names(duration_ms: int) -> list[dict[str, int | str]]:
    if duration_ms <= 0 or duration_ms > 300000:
        raise ValueError("duration_ms must be in range 1..300000")

    path = socket_path()
    start_ns = time.monotonic_ns()
    deadline_ns = start_ns + duration_ms * 1_000_000
    records: list[dict[str, int | str]] = []
    buffer = b""

    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
        sock.setblocking(False)
        try:
            sock.connect(str(path))
        except BlockingIOError:
            pass

        selector = selectors.DefaultSelector()
        selector.register(sock, selectors.EVENT_READ)
        try:
            while True:
                remaining_ns = deadline_ns - time.monotonic_ns()
                if remaining_ns <= 0:
                    break
                events = selector.select(timeout=min(0.25, remaining_ns / 1_000_000_000))
                for key, _mask in events:
                    chunk = key.fileobj.recv(65536)
                    if not chunk:
                        return records
                    buffer += chunk
                    while b"\n" in buffer:
                        line, buffer = buffer.split(b"\n", 1)
                        name = parse_event_name(line)
                        if name is None:
                            continue
                        records.append({
                            "elapsedMs": (time.monotonic_ns() - start_ns) // 1_000_000,
                            "event": name,
                        })
        finally:
            selector.close()
    return records


def main() -> int:
    parser = argparse.ArgumentParser(description="Capture Hyprland socket2 event names only; payloads are discarded.")
    parser.add_argument("--duration-ms", type=int, default=30000)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).with_name("raw") / "event-names.local.json",
    )
    args = parser.parse_args()

    data = {
        "schemaVersion": 1,
        "issue": "FDM-822",
        "evidenceStatus": "LOCAL_ONLY_UNQUALIFIED",
        "durationMs": args.duration_ms,
        "events": capture_event_names(args.duration_ms),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
