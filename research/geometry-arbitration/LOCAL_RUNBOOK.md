# FDM-822 deterministic local Omarchy runbook

Use this only after pulling `research/fdm-822-geometry-arbitration`. The remote branch intentionally contains no live result and no Chrome orientation adapter.

## 1. Freeze the lane and run remote-safe checks

```bash
git switch research/fdm-822-geometry-arbitration
git status --short
git rev-parse HEAD
python -m unittest discover -s tests -p 'test_*.py'
python -m compileall -q research/geometry-arbitration tests
bash -n research/geometry-arbitration/capture_versions.sh
```

Do not continue with an unclean tree unless the local-only files are under ignored `research/geometry-arbitration/raw/` paths.

## 2. Pin the exact stack before reusing any prior evidence

Capture the local stack:

```bash
research/geometry-arbitration/capture_versions.sh
cat research/geometry-arbitration/raw/stack.local.txt
```

Copy only non-sensitive version/package facts into `LOCAL_EVIDENCE_TEMPLATE.md`.

Before reusing any FDM-816 geometry result, compare its recorded Omarchy, Hyprland, and Quickshell versions/build identifiers to this capture. All three must match exactly. If one differs—or FDM-816 has no pinned result yet—mark FDM-816 reuse as `NO` and execute the full FDM-822 matrix independently.

Do not treat current documentation or historical fullscreen numeric meanings as pinned runtime evidence.

## 3. Qualify sanitized browser identities

For each browser/package/display-mode variant in the issue, focus exactly one target surface and capture a one-shot sanitized active-window snapshot:

```bash
python research/geometry-arbitration/capture_geometry_snapshot.py \
  --section active \
  --output research/geometry-arbitration/raw/<case>.local.json
```

For a controlled checkpoint of all current clients, use `--section clients`. The helper strips titles, initial titles, PIDs, addresses, workspace names, and command lines before writing. Never redirect raw `hyprctl clients -j` output into a tracked file.

Run this sequence for normal Chrome/Chromium, available channel variants, incognito/guest/managed, PWA/`--app`, DevTools, extension popup, browser-owned dialogs/file pickers/auth dialogs, PiP, first-run/recovery/update surfaces when observable, native Wayland/XWayland, and installed native/Flatpak/Snap/wrapper forms.

Classify a surface as `normal-tabbed` only when stable compositor metadata on the pinned stack proves it. If the distinction requires a title, URL, profile path, or guess, mark it ambiguous and fail closed. Beta/Dev/Canary remain opt-in. Incognito/guest remain non-controlling until FDM-821 proves adapter scope/side effects.

## 4. Prove the selected geometry field and unit

At each supported scale (`1.0`, `1.25`, `1.5`, `2.0` when hardware permits), monitor transform, and border/gap configuration:

1. capture `--section monitors`;
2. capture `--section active` for the focused normal browser;
3. record the compositor-reported outer width without rounding;
4. compare against the known logical monitor/layout geometry;
5. repeat after changing border size, gaps, rounding, maximize/restore, and monitor transform.

Capture Hyprland option values at the same checkpoint:

```bash
python research/geometry-arbitration/capture_geometry_snapshot.py --section options
```

Do not promote `geometry.unit` from `unverified` to `logical` in a committed fixture until the chosen field's scale/fraction/border/gap semantics are proven. Zero, negative, non-finite, or transient geometry is unknown and must produce no action.

## 5. Measure freshness and event coverage

Use the bounded socket2 helper during each interaction to learn which documented Hyprland event names occur without storing their payloads:

```bash
python research/geometry-arbitration/capture_hyprland_event_names.py \
  --duration-ms 30000 \
  --output research/geometry-arbitration/raw/<case>-events.local.json
```

In parallel, observe the exact candidate Quickshell geometry source required by FDM-822: `activeToplevel`, `lastIpcObject`, explicit `refreshToplevels()`, and any dedicated fresh geometry property/event available on the pinned Quickshell build. Use a monotonic elapsed-time source for all measurements.

For each matrix case, perform the interaction only after the browser has first remained focused and geometrically unchanged for at least 60 seconds where the issue requires it. Record **crossing-to-detection latency** separately from any later adapter/orientation verification latency.

Required cases include slow/rapid tiled resize, slow/rapid floating resize, mouse and keyboard resize after long stable focus, unrelated tiled-window reflow with Chrome focus unchanged, floating move without resize, maximize/restore, fullscreen/immersive/kiosk enter/exit, split/master layout changes, monitor moves, workspace/special-workspace changes, scale/transform/rearrangement/hotplug/unplug, suspend/resume, shell reload, lock/unlock, and monitor unplug during a candidate.

Do not put `hyprctl clients -j` in a loop. One-shot checkpoint captures are allowed; a continuous subprocess poller is not.

## 6. Select the bounded observation contract in the mandated order

Evaluate only in this order:

1. dedicated fresh toplevel geometry property/event;
2. supported signal covering every qualified resize start/end path, then one coalesced refresh;
3. lifecycle/layout events plus one coalesced refresh, only after proving no supported resize path is missed;
4. one centralized focused-browser sentinel plus bounded adaptive burst, preferably through Quickshell/direct IPC, if events alone are insufficient;
5. NO-GO if a stable focused browser can cross a threshold without detection or acceptable latency requires unbounded/high-frequency synchronous compositor polling.

If option 4 is necessary, start from the issue's hypothesis only as a measurement seed: 1000–2000 ms sentinel, 150–250 ms burst, N unchanged samples or 2 seconds max. Replace every number with measured parameters or record NO-GO. Sampling must stop completely with no eligible focused browser and while the session is locked.

Measure CPU/log behavior for the selected strategy on the actual shell/compositor. Do not infer resource cost from test timing, GitHub Actions, or source inspection.

## 7. Re-run arbitration with locally qualified scope evidence

The remote tests use synthetic opaque `(scopeToken, scopeEpoch)` values and a fake sink. Once FDM-821 has a locally proven adapter scope contract, map that evidence into the test cases without calling the real adapter from this research lane.

Re-run or extend deterministic tests for same-scope narrow/wide windows, different scopes, token expiry/restart, rapid focus flips, unrelated-app interruptions, candidate close/mutation, lock/null/layer focus, fullscreen/immersive/kiosk cancellation, threshold return-to-band, fractional boundaries, startup/reload baseline, new scope after startup, same-region refocus, manual/external changes, config revisions, suspend/resume, monitor unplug, and manual change before/after crossing.

The safe config-change choice in the remote prototype is **baseline-on-config-change**. Change it only with an explicit FDM-822 decision and tests.

## 8. Fill evidence and decide exactly once

Copy only sanitized, minimal evidence into `LOCAL_EVIDENCE_TEMPLATE.md`. Keep local captures ignored and inspect `git status --ignored --short` before committing anything.

Only after every acceptance criterion is answered, replace `LOCAL EVIDENCE PENDING` with exactly one outcome:

```text
GO — observation contract
```

or

```text
NO-GO
```

A GO must define the exact stack, geometry field/unit/normalization, eligible-window contract, package formats, scope-token lifetime, observation triggers/sampling bounds, maximum detection latency, dwell/hysteresis/cooldown/startup/manual-override semantics, lifecycle/lock cleanup, and measured CPU/log behavior. A NO-GO must state which required safety/freshness distinction failed.

Do not implement production `Service.qml` or invoke Chrome orientation from this issue. FDM-826 owns convergence with FDM-821 after both feasibility results exist.
