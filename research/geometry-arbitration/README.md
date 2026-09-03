# Geometry and arbitration research — FDM-822

This lane prepares the remote-safe part of FDM-822: a fail-closed eligible-window classifier, pure arbitration policy, synthetic sanitized fixtures, bounded capture helpers, deterministic tests, and the local Omarchy qualification procedure.

**Status: local qualification incomplete — LOCAL EVIDENCE PENDING.** The previously recorded read-only checkpoint did not execute the required resize/freshness, fractional-scale, lifecycle, latency, or resource matrix. In particular, a bounded socket2 probe performed without a resize interaction is not negative evidence about resize-time event coverage and does not support a final NO-GO verdict.

## Hard boundary

This branch does not:

- invoke a real Chrome orientation adapter;
- implement production `Service.qml` or production plugin runtime wiring;
- claim live Hyprland/Quickshell geometry freshness, width units, browser arbitration, latency, or CPU/log behavior;
- run continuous `hyprctl` polling;
- use remote debugging, global input injection, profile files, browser titles, browser URLs, account data, tokens, or raw committed browser captures;
- import FDM-816 measurements without an exact Omarchy/Hyprland/Quickshell version match.

## Remote research artifacts

- `classifier.py` — pure fail-closed eligibility classifier. Stable is the only browser channel allowed by default. Beta/Dev/Canary require both explicit opt-in and separate local channel qualification; app-ID and package allowlisting alone are insufficient.
- `policy.py` — pure arbitration state machine using injected monotonic elapsed milliseconds and opaque `(scopeToken, scopeEpoch)` lifetime keys. It implements inclusive narrow/wide thresholds, band hysteresis, dwell, global cooldown, enable/reload startup snapshot semantics, manual/external override handling, request generations bound to scope/window/region, stale-completion rejection, lifecycle requalification, config validation, and scope expiry without calling an adapter.
- `fixture_tools.py` — strips transient/private fields from a single local Hyprland client object. Browser channel is explicit and is never inferred from compositor app ID.
- `capture_geometry_snapshot.py` — one-shot sanitized `hyprctl` capture helper. It never loops and retains only geometry/state fields required by FDM-822.
- `capture_hyprland_event_names.py` — bounded Hyprland socket2 probe that persists only event names plus relative monotonic milliseconds; event payloads are discarded.
- `capture_versions.sh` — local stack/package/version fingerprint helper. Output goes to ignored `raw/` storage by default.
- `LOCAL_RUNBOOK.md` — deterministic local qualification sequence.
- `LOCAL_EVIDENCE_TEMPLATE.md` — partial evidence record plus the still-required local matrix. It must remain pending until the acceptance criteria are actually measured.

Synthetic fixtures live under `tests/fixtures/fdm-822/`. `fixture-schema.json` is an authoritative closed contract: nested objects reject undeclared properties, and the deterministic test validator enforces types, enums, constants, required fields, numeric bounds, and additional-property rules. The committed examples deliberately use `SYNTHETIC-NO-LIVE-VERSIONS`; they are not evidence about current Hyprland or browser behavior.

## Policy defaults represented by the prototype

```text
horizontalThreshold = 1200 logical px
verticalThreshold = 1400 logical px
decisionDwellMs = 750
minSwitchIntervalMs = 2000
minimumThresholdGap = 100 logical px
applyOnStartup = false
manualOverridePolicy = until-next-region-transition
configChangePolicy = baseline-on-config-change
browserChannelPolicy = stable-only by default
```

Widths are compared as finite positive numbers without rounding. `<= horizontalThreshold` is narrow, `>= verticalThreshold` is wide, and values strictly between the thresholds are band. The first observation after service enable/reload is the startup snapshot: with `applyOnStartup=false`, only an eligible target present in that snapshot is baselined. If no eligible browser is active then, the first later eligible focus follows normal eligibility, dwell, and policy evaluation.

Lock, focus loss during an active candidate/request, fullscreen/immersive/kiosk ineligibility, suspend, and equivalent invalidations cancel active work but retain a requalification obligation. The next eligible observation starts a fresh full dwell when correction is still needed. An ordinary settled same-region focus-away/refocus remains a no-op.

Each emitted request has a monotonically increasing generation and is bound to its scope token/epoch, window, and region. Verification can update known orientation or manual-override state only while that exact request remains current; delayed completions are rejected and force conservative fresh requalification.

## FDM-816 reuse gate

No FDM-816 measurement is promoted into a FDM-822 decision without an exact Omarchy, Hyprland, and Quickshell version/build match. Even with a match, aggregate observations are reference material unless they directly measure the FDM-822 acceptance case in question.

## Remote checks

Run:

```bash
python -m unittest discover -s tests -p 'test_*.py'
python -m compileall -q research/geometry-arbitration tests
bash -n research/geometry-arbitration/capture_versions.sh
```

These checks prove only deterministic research code, fixture/schema enforcement, and privacy gates. They cannot satisfy the remaining target-machine acceptance criteria or produce a GO/NO-GO verdict.
