# Geometry and arbitration research — FDM-822

This lane prepares the remote-safe part of FDM-822: a fail-closed eligible-window classifier, pure arbitration policy, synthetic sanitized fixtures, bounded capture helpers, deterministic tests, and the local Omarchy qualification procedure.

**Status: local qualification complete — NO-GO.** See
`LOCAL_EVIDENCE_TEMPLATE.md` for the sanitized evidence report. This result
blocks production implementation; the pure classifier/policy and bounded
capture helpers remain safe research artifacts.

## Hard boundary

This branch does not:

- invoke a real Chrome orientation adapter;
- implement production `Service.qml` or production plugin runtime wiring;
- claim live Hyprland/Quickshell geometry freshness, width units, browser arbitration, latency, or CPU/log behavior;
- run continuous `hyprctl` polling;
- use remote debugging, global input injection, profile files, titles, URLs, account data, tokens, or raw committed browser captures;
- import FDM-816 measurements without an exact Omarchy/Hyprland/Quickshell version match.

## Remote research artifacts

- `classifier.py` — pure fail-closed eligibility classifier. Titles are ignored. The default app-ID allowlist is `google-chrome`, `google-chrome-stable`, and `chromium`. Unqualified package identity, unknown normal-tabbed identity, invalid/unverified geometry, and unqualified privacy modes fail closed.
- `policy.py` — pure arbitration state machine using injected monotonic elapsed milliseconds and opaque `(scopeToken, scopeEpoch)` lifetime keys. It implements inclusive narrow/wide thresholds, band hysteresis, dwell, global cooldown, startup baseline, manual/external override suspension, safe baseline-on-config-change, and scope expiry without calling any adapter.
- `fixture_tools.py` — strips titles, URLs, PIDs, addresses, workspace names, and other transient/private fields from a single local Hyprland client object before review.
- `capture_geometry_snapshot.py` — one-shot sanitized `hyprctl` capture helper. It never loops and retains only geometry/state fields required by FDM-822.
- `capture_hyprland_event_names.py` — bounded Hyprland socket2 probe that persists only event names plus relative monotonic milliseconds; event payloads are discarded.
- `capture_versions.sh` — local stack/package/version fingerprint helper. Output goes to ignored `raw/` storage by default.
- `LOCAL_RUNBOOK.md` — deterministic local qualification sequence.
- `LOCAL_EVIDENCE_TEMPLATE.md` — result structure to fill only after the target Omarchy machine is tested.

Synthetic fixtures live under `tests/fixtures/fdm-822/`. They are policy/classifier examples only and deliberately use `SYNTHETIC-NO-LIVE-VERSIONS`; they are not evidence about current Hyprland or browser behavior.

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
```

Widths are compared as finite positive numbers without rounding. `<= horizontalThreshold` is narrow, `>= verticalThreshold` is wide, and values strictly between the thresholds are band. The remote prototype treats geometry marked `unit=unverified` as ambiguous; only the local run may qualify the exact production field as logical compositor pixels.

## FDM-816 reuse gate

No FDM-816 measurement is copied into this branch. During local continuation, reuse is allowed only when the FDM-816 evidence records the exact same Omarchy, Hyprland, and Quickshell versions/build identifiers as FDM-822. Any mismatch means the result is reference material only and FDM-822 must execute its own matrix.

## Remote checks

Run:

```bash
python -m unittest discover -s tests -p 'test_*.py'
python -m compileall -q research/geometry-arbitration tests
bash -n research/geometry-arbitration/capture_versions.sh
```

These checks prove only deterministic research code/fixtures. They cannot satisfy the live acceptance criteria.
