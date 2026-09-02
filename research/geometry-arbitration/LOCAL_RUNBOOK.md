# FDM-822 deterministic local Omarchy runbook

Use this only after pulling `research/fdm-822-geometry-arbitration`. The branch contains no production watcher and no live Chrome orientation adapter.

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

Before reusing any FDM-816 result, compare its recorded Omarchy, Hyprland, and Quickshell versions/build identifiers to this capture. All three must match exactly. Even with an exact match, reuse only a measurement that directly covers the FDM-822 acceptance case being evaluated; aggregate evidence does not fill an unmeasured matrix row.

Do not treat documentation, historical compositor meanings, or a no-interaction probe as pinned runtime proof.

## 3. Qualify sanitized browser identities and channels

For each browser/package/display-mode variant in the issue, focus exactly one target surface and capture a one-shot sanitized active-window snapshot:

```bash
python research/geometry-arbitration/capture_geometry_snapshot.py \
  --section active \
  --output research/geometry-arbitration/raw/<case>.local.json
```

For a controlled checkpoint of all current clients, use `--section clients`. Never redirect raw `hyprctl clients -j` output into a tracked file.

Run this sequence for normal Chrome/Chromium, available channel variants, incognito/guest/managed, PWA/app mode, DevTools, extension popup, browser-owned dialogs/file pickers/auth dialogs, PiP, first-run/recovery/update surfaces when observable, native Wayland/XWayland, and installed native/Flatpak/Snap/wrapper forms.

Classify a surface as `normal-tabbed` only when stable compositor metadata on the pinned stack proves it. If the distinction requires a browser title, browser URL, profile path, account data, or guess, mark it ambiguous and fail closed.

Stable is the only controlling channel by default. Beta/Dev/Canary require an explicit configuration opt-in **and** separate local channel qualification. An allowlisted app ID or package does not prove the channel. When promoting a sanitized local fixture with `fixture_tools.py`, pass `--browser-channel` explicitly; do not infer it from the compositor app ID.

Incognito/guest remain non-controlling until FDM-821 proves adapter scope/side effects.

## 4. Prove the selected geometry field and unit

At each supported scale (`1.0`, `1.25`, `1.5`, `2.0` when the machine permits), monitor transform, and border/gap configuration:

1. capture `--section monitors`;
2. capture `--section active` for the focused normal browser;
3. record the compositor-reported outer width without rounding;
4. compare against the known logical monitor/layout geometry;
5. repeat after changing border size, gaps, rounding, maximize/restore, and monitor transform.

Capture Hyprland option values at the same checkpoint:

```bash
python research/geometry-arbitration/capture_geometry_snapshot.py --section options
```

Do not promote `geometry.unit` from `unverified` to `logical` until the chosen field's scale/fraction/border/gap semantics are proven. Zero, negative, non-finite, or transient geometry is unknown and must produce no action.

## 5. Measure freshness with controlled local interaction

Manual interaction by the local operator is **required and allowed** for this qualification. This includes resizing or moving windows with the mouse/keyboard, changing layouts, entering/exiting fullscreen-like modes, moving windows across monitors/workspaces, locking/unlocking, and other acceptance-matrix interactions. The hard boundary forbids programmatic/global input injection; it does not forbid a human operator from performing the controlled test case.

Run the bounded socket2 helper while the relevant interaction is actually performed:

```bash
python research/geometry-arbitration/capture_hyprland_event_names.py \
  --duration-ms 30000 \
  --output research/geometry-arbitration/raw/<case>-events.local.json
```

A socket2 interval in which no resize/layout interaction occurred may describe only that idle/focus interval. It **must not** be used to claim that resize/geometry events are absent during resize or to reject an event-based strategy.

In parallel, observe the exact candidate Quickshell geometry source required by FDM-822: `activeToplevel`, `lastIpcObject`, explicit `refreshToplevels()`, and any dedicated fresh geometry property/event available on the pinned Quickshell build. Use a monotonic elapsed-time source for all measurements.

For each matrix case, perform the interaction only after the browser has first remained focused and geometrically unchanged for at least 60 seconds where required. Record **crossing-to-detection latency** separately from any later adapter/orientation verification latency.

Required cases include slow/rapid tiled resize, slow/rapid floating resize, mouse and keyboard resize after long stable focus, unrelated tiled-window reflow with Chrome focus unchanged, floating move without resize, maximize/restore, fullscreen/immersive/kiosk enter/exit, split/master layout changes, monitor moves, workspace/special-workspace changes, scale/transform/rearrangement/hotplug/unplug, suspend/resume, shell/compositor reload, lock/unlock, and monitor unplug during a candidate.

Do not put `hyprctl clients -j` in a loop. One-shot checkpoint captures are allowed; a continuous subprocess poller is not.

## 6. Select the bounded observation contract in the mandated order

Evaluate only in this order:

1. dedicated fresh toplevel geometry property/event;
2. supported signal covering every qualified resize start/end path, then one coalesced refresh;
3. lifecycle/layout events plus one coalesced refresh, only after proving no supported resize path is missed;
4. one centralized focused-browser sentinel plus bounded adaptive burst, preferably through Quickshell/direct IPC, if events alone are insufficient;
5. NO-GO only when a required safety/freshness distinction is actually demonstrated to fail, such as a supported stable-focus threshold crossing that remains undetected or an acceptable latency bound requiring unsafe/unbounded high-frequency synchronous compositor polling.

If option 4 is necessary, start from the issue hypothesis only as a measurement seed: 1000–2000 ms sentinel, 150–250 ms burst, N unchanged samples or 2 seconds max. Replace every number with measured parameters or leave the case pending. Sampling must stop completely with no eligible focused browser and while the session is locked.

Measure CPU/log behavior for the selected strategy on the actual shell/compositor. Do not infer resource cost from unit-test timing, GitHub Actions, or source inspection.

## 7. Re-run arbitration with locally qualified scope evidence

The remote tests use synthetic opaque `(scopeToken, scopeEpoch)` values and a fake sink. Once FDM-821 has a locally proven adapter scope contract, map that evidence into the test cases without calling the real adapter from this research lane.

Re-run or extend deterministic tests for same-scope narrow/wide windows, different scopes, token expiry/restart, rapid focus flips, unrelated-app interruptions, candidate close/mutation, lock/null/layer focus, fullscreen/immersive/kiosk cancellation/recovery, threshold return-to-band, fractional boundaries, startup/reload snapshot semantics, no-browser-at-startup first focus, new scope after startup, same-region settled refocus, manual/external changes, config revisions, delayed adapter completions, suspend/resume, monitor unplug, and manual change before/after crossing.

Every delayed completion must remain bound to its emitted request generation, scope token/epoch, window, and region. A stale success or mismatch must not update current known orientation or assign `manual_override_region` to a newer region.

The safe config-change choice in the remote prototype is **baseline-on-config-change**. Change it only with an explicit FDM-822 decision and tests.

## 8. Fill evidence and decide exactly once

Copy only sanitized, minimal evidence into `LOCAL_EVIDENCE_TEMPLATE.md`. Keep local captures ignored and inspect `git status --ignored --short` before committing anything.

Leave the report as:

```text
LOCAL EVIDENCE PENDING
```

until every required acceptance row has measured evidence. Missing evidence, an unproven unit, or an idle no-resize event probe is not by itself a final NO-GO.

Only after the matrix is complete, replace the pending line with exactly one outcome:

```text
GO — observation contract
```

or

```text
NO-GO
```

A GO must define the exact stack, geometry field/unit/normalization, eligible-window/channel contract, package formats, scope-token lifetime, observation triggers/sampling bounds, maximum detection latency, dwell/hysteresis/cooldown/startup/manual-override semantics, lifecycle/lock cleanup, and measured CPU/log behavior. A NO-GO must identify a concrete reproduced safety/freshness failure and the exact controlled case that demonstrates it.

Do not implement production `Service.qml` or invoke Chrome orientation from this issue. FDM-826 owns convergence with FDM-821 after both feasibility results exist.
