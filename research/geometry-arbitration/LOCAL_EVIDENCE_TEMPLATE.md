# FDM-822 local evidence report

## Decision status

```text
LOCAL EVIDENCE PENDING
```

Local qualification is incomplete. The read-only checkpoint previously recorded on the target Omarchy machine is retained below only as partial, non-decisive evidence. It did not execute the required controlled resize/freshness, fractional-scale, lifecycle, latency, or resource matrix, so neither GO nor NO-GO is justified from this record.

## Capture boundary and safety

The recorded checkpoint used read-only one-shot `hyprctl` snapshots, a bounded socket2 event-name probe, pure policy tests, and a read-only accessibility topology observation. No Chrome preference/profile write, orientation action, remote-debugging endpoint, alternate data directory, global input injection, privileged helper, production service, or committed raw browser capture was used.

Raw local captures remain outside tracked evidence. Any future update to this report must contain only sanitized facts that pass the repository privacy gate.

## Previously recorded pinned stack

These values were recorded by the earlier local checkpoint and are not newly measured by this remediation:

| Component | Recorded version/build | Reproducible command | Qualification use |
| --- | --- | --- | --- |
| Omarchy Quattro | `4.0.2-1` | `omarchy version` | version pin only |
| Omarchy channel | `stable` | `omarchy version channel` | version pin only |
| Hyprland | `0.56.2-1`, commit `efb50993780079460b0cbed1363e2166a2de1d9f` | `hyprctl version` | version pin only |
| Quickshell | `0.3.1-1` | `qs --version` | version pin only |
| Chrome Stable | `152.0.7977.64-1` | `google-chrome-stable --version` | package/version checkpoint only |
| Chromium | `151.0.7922.173-1` | `chromium --version` | installed; target-window behavior not qualified |
| Session | Wayland | environment checkpoint | native Wayland target observed; XWayland untested |
| Monitors | two `1920x1080`, scale `1.0`, transform `0` | `hyprctl monitors -j` | fractional scale/rotation/hotplug untested |

### FDM-816 reuse check

The earlier record noted exact Omarchy/Hyprland/Quickshell version matches with FDM-816 and treated that evidence as aggregate reference only. That does not replace any FDM-822 matrix row. No FDM-816 observation may be used as proof of a resize/freshness case unless it directly measures the same required path under the pinned stack.

## Browser/package identity qualification

| Variant | Recorded evidence | Current qualification |
| --- | --- | --- |
| Chrome Stable | allowlisted compositor app ID observed on native Wayland | PENDING: package-to-window binding and normal-tabbed identity semantics not fully proven |
| Chromium | installed; no target-window checkpoint recorded | PENDING |
| Chrome Beta/Dev/Canary | not installed/observed in recorded checkpoint | UNSUPPORTED by default; explicit opt-in plus separate qualification required |
| Flatpak/Snap/wrapper | not exercised | PENDING; fail closed |
| Incognito/Guest | not exercised | PENDING; non-controlling until FDM-821 scope proof |
| Managed | no qualified managed test state | PENDING |
| PWA / app mode | synthetic fail-closed fixtures only | LIVE CASE PENDING |
| DevTools / popup / dialog / PiP | synthetic fail-closed fixtures only | LIVE CASE PENDING |
| first-run/recovery/update surfaces | not exercised | PENDING |

The classifier now enforces Stable by default. An allowlisted app ID and qualified package cannot make Beta/Dev/Canary eligible unless that channel is explicitly opted in and separately marked locally qualified.

## Accessibility topology checkpoint

The earlier record noted that the matching Chrome application exposed application/frame topology but did not provide enough focused-state evidence to map the compositor target to a safe controlling surface. No accessibility action was invoked. This is partial context only and does not qualify FDM-822 geometry or FDM-821 adapter control.

## Geometry field qualification

```text
candidate field observed: hyprctl activewindow/clients size[0]
reported unit: UNVERIFIED
finite-positive normalization: pure prototype only
fractional handling: NOT MEASURED
border inclusion: UNKNOWN
gap inclusion: UNKNOWN
shadow/decoration inclusion: UNKNOWN
rounding behavior: UNKNOWN
```

The earlier scale-1.0 checkpoint contained a tiled browser width numerically below the monitor width. A single scale-1.0 observation cannot distinguish logical from coincident physical units or prove border/gap/decoration semantics.

### Scale/transform matrix

| Scale/transform | Status | Conclusion |
| --- | --- | --- |
| 1.0 / transform 0 | single checkpoint only | unit semantics UNVERIFIED |
| 1.25 | NOT MEASURED | PENDING |
| 1.5 | NOT MEASURED | PENDING |
| 2.0 | NOT MEASURED | PENDING |
| rotated monitor | NOT MEASURED | PENDING |

## Geometry freshness matrix

No resize interaction was performed during the recorded 30-second socket2 probe. Therefore the absence of a resize/geometry event in that interval is **not** evidence that resize events are absent during resize, and it cannot reject an event-based observation strategy.

| Case | Status | Required local evidence |
| --- | --- | --- |
| slow tiled resize | NOT MEASURED | event/source trigger plus crossing-to-detection timing |
| rapid tiled resize | NOT MEASURED | event/source trigger plus crossing-to-detection timing |
| slow floating resize | NOT MEASURED | event/source trigger plus crossing-to-detection timing |
| rapid floating resize | NOT MEASURED | event/source trigger plus crossing-to-detection timing |
| mouse resize after 60s stable focus | NOT MEASURED | long-focus crossing timing |
| keyboard resize after 60s stable focus | NOT MEASURED | controlled local keyboard interaction timing |
| unrelated tiled-window reflow | NOT MEASURED | browser focus unchanged; geometry freshness proof |
| floating movement without resize | NOT MEASURED | prove no false transition/action |
| maximize / restore | NOT MEASURED | eligibility and fresh geometry proof |
| fullscreen / immersive / kiosk enter | PURE POLICY ONLY | live invalidation/cancellation still pending |
| fullscreen / immersive / kiosk exit | PURE POLICY ONLY | fresh eligible observation plus full dwell still pending live |
| split/master layout change | NOT MEASURED | fresh geometry proof |
| move between monitors | NOT MEASURED | fresh geometry and scope/window binding proof |
| workspace/special workspace | NOT MEASURED | lifecycle freshness proof |
| monitor scale/transform | NOT MEASURED | logical-unit proof |
| rearrange/hotplug/unplug | NOT MEASURED | invalidation/recovery proof |
| suspend/resume | PURE POLICY ONLY | live timing invalidation/recovery still pending |
| shell/compositor reload | NOT MEASURED | startup snapshot/recovery proof |
| lock/unlock | PURE POLICY ONLY | live no-sampling/no-action and fresh-dwell recovery pending |

## Bounded event-name checkpoint

The earlier helper ran for bounded idle/focus observation intervals and retained event names only; payloads were discarded. In the 30-second interval it recorded focus/window metadata event names but no resize was intentionally performed.

**Permitted conclusion:** the no-resize interval did not independently qualify a geometry event source.

**Not permitted conclusion:** that Hyprland emits no usable resize/geometry event while a controlled resize is occurring. The required interactive matrix must be run before making that claim.

## Observation-strategy status

Evaluate locally in the mandated order:

1. dedicated fresh toplevel geometry property/event — **PENDING**;
2. supported resize signal plus coalesced refresh — **PENDING**;
3. lifecycle/layout events plus coalesced refresh with complete resize-path proof — **PENDING**;
4. centralized focused-browser sentinel plus bounded adaptive burst, only if required and measured — **PENDING**;
5. NO-GO only if a required safety/freshness distinction is actually shown to fail, such as a supported stable-focus threshold crossing that remains undetected or an acceptable latency bound requiring unsafe/unbounded polling.

The current evidence does not satisfy step 5.

## Latency and resource metrics

```text
crossing-to-detection latency: NOT MEASURED
crossing-to-verified-orientation latency: NOT APPLICABLE in this lane
Quickshell CPU baseline/delta: NOT MEASURED for a selected strategy
Hyprland CPU/log baseline/delta: NOT MEASURED for a selected strategy
command/process rate: no production observation strategy selected
```

## Pure policy/classifier qualification

Remote deterministic tests cover:

```text
stable-only browser channel default: TESTED
explicit separately-qualified non-stable opt-in: TESTED
startup eligible target present at enable/reload baseline: TESTED
no browser at startup -> first eligible focus normal dwell: TESTED
same-region settled refocus no-op: TESTED
region transition dwell/hysteresis/cooldown: TESTED
request generation + scope/window/region binding: TESTED
stale verification rejection: TESTED
stale mismatch does not assign override to a new region: TESTED
candidate invalidation -> fresh recovery dwell: TESTED
lock/focus/fullscreen-mode/suspend recovery model: TESTED
closed fixture schema and negative validation cases: TESTED
```

These tests do not substitute for live Omarchy geometry, timing, lifecycle, or resource evidence.

## Remaining local-only work

A local operator must still execute and record the complete controlled matrix from `LOCAL_RUNBOOK.md`, including resize interactions, scale/transform cases available on the machine, long-focus crossings, lifecycle/lock/reload cases, observation latency, and resource/log measurements for the selected bounded strategy. Manual local interaction is allowed for qualification; programmatic/global input injection remains forbidden.

Only after every required acceptance row is measured may this section be replaced with exactly one supported outcome:

```text
GO — observation contract
```

or

```text
NO-GO
```

Until then, the FDM-822 local qualification remains incomplete and production implementation is not authorized.
