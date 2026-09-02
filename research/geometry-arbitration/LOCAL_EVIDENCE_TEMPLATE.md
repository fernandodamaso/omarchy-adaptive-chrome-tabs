# FDM-822 local evidence template

Fill this file only on the target Omarchy machine. Do not commit raw captures, browser titles/URLs, profile names/paths, account identifiers, command lines, tokens, or secrets.

## Decision status

```text
LOCAL EVIDENCE PENDING
```

Replace the line above with exactly one final result only after every required section is complete:

```text
GO — observation contract
```

or

```text
NO-GO
```

## Pinned stack

| Component | Exact version/build | Reproducible command | Notes |
| --- | --- | --- | --- |
| Omarchy Quattro | PENDING | `omarchy version` | |
| Omarchy channel | PENDING | `omarchy version channel` | |
| Hyprland | PENDING | `hyprctl version` | |
| Quickshell | PENDING | `qs --version` | |
| Chrome Stable | PENDING | browser `--version` only | package source + executable identity |
| Chromium | PENDING / absent | browser `--version` only | package source + executable identity |

### FDM-816 reuse check

```text
FDM-816 exact Omarchy match: PENDING
FDM-816 exact Hyprland match: PENDING
FDM-816 exact Quickshell match: PENDING
Reuse permitted: PENDING
```

If any version/build differs, set `Reuse permitted: NO` and do not copy numeric/event semantics.

## Browser/package identity qualification

| Variant | Package source | Native Wayland/XWayland | Stable compositor identity | Normal-tabbed distinguishable | Controlling? |
| --- | --- | --- | --- | --- | --- |
| Chrome Stable | PENDING | PENDING | PENDING | PENDING | PENDING |
| Chromium | PENDING | PENDING | PENDING | PENDING | PENDING |
| Chrome Beta/Dev/Canary | PENDING/absent | PENDING | PENDING | PENDING | opt-in only |
| Flatpak/Snap/wrapper | PENDING/absent | PENDING | PENDING | PENDING | fail closed until qualified |
| Incognito | PENDING | PENDING | PENDING | PENDING | fail closed until FDM-821 scope proof |
| Guest | PENDING | PENDING | PENDING | PENDING | fail closed until FDM-821 scope proof |
| Managed | PENDING | PENDING | PENDING | PENDING | fail closed until separately qualified |
| PWA / `--app` | PENDING | PENDING | PENDING | PENDING | no |
| DevTools / popup / dialog / PiP | PENDING | PENDING | PENDING | PENDING | no/ambiguous |

## Geometry field qualification

```text
Selected outer-width field: PENDING
Reported unit: PENDING
Finite-positive normalization: PENDING
Fractional handling: PENDING
Border inclusion: PENDING
Gap inclusion: PENDING
Shadow/decoration inclusion: PENDING
Rounding behavior: PENDING
```

### Scale/transform matrix

| Scale/transform | Reported client width | Physical comparison | Logical/physical conclusion |
| --- | ---: | ---: | --- |
| 1.0 | PENDING | PENDING | PENDING |
| 1.25 | PENDING / unsupported | PENDING | PENDING |
| 1.5 | PENDING / unsupported | PENDING | PENDING |
| 2.0 | PENDING / unsupported | PENDING | PENDING |
| rotated monitor | PENDING | PENDING | PENDING |

## Geometry freshness matrix

For every row record the observation source, trigger, stale interval, and whether the path remains detectable after the browser has been focused and unchanged for at least 60 seconds.

| Case | Source/trigger | Crossing-to-detection ms | Stale/missed? | Notes |
| --- | --- | ---: | --- | --- |
| slow tiled resize | PENDING | PENDING | PENDING | |
| rapid tiled resize | PENDING | PENDING | PENDING | |
| slow floating resize | PENDING | PENDING | PENDING | |
| rapid floating resize | PENDING | PENDING | PENDING | |
| mouse resize after 60s stable focus | PENDING | PENDING | PENDING | |
| keyboard resize after 60s stable focus | PENDING | PENDING | PENDING | |
| unrelated tiled-window reflow | PENDING | PENDING | PENDING | Chrome focus unchanged |
| floating movement without resize | PENDING | PENDING | PENDING | |
| maximize / restore | PENDING | PENDING | PENDING | remains eligible if normal |
| fullscreen / immersive / kiosk enter | PENDING | PENDING | PENDING | must cancel candidate/control |
| fullscreen / immersive / kiosk exit | PENDING | PENDING | PENDING | fresh geometry + full dwell |
| split/master layout change | PENDING | PENDING | PENDING | |
| move between monitors | PENDING | PENDING | PENDING | |
| workspace/special workspace | PENDING | PENDING | PENDING | |
| monitor scale/transform | PENDING | PENDING | PENDING | |
| rearrange/hotplug/unplug | PENDING | PENDING | PENDING | |
| suspend/resume | PENDING | PENDING | PENDING | invalidate deadlines |
| shell/compositor reload | PENDING | PENDING | PENDING | |
| lock/unlock | PENDING | PENDING | PENDING | no sampling/action while locked |

## Observation strategy

Evaluate in the required order and stop at the first fully qualified strategy:

1. Dedicated fresh toplevel geometry property/event.
2. Supported begin/end resize signal plus coalesced refresh.
3. Lifecycle/layout event coverage plus one coalesced refresh, only if no supported resize path is missed.
4. One centralized focused-browser sentinel plus bounded adaptive burst, preferably through Quickshell/direct IPC and never a repeated external `hyprctl` subprocess loop.
5. NO-GO if acceptable freshness requires unsafe/unbounded polling or any supported stable-focus resize path is undetectable.

If strategy 4 is required, fill all fields:

```text
sentinel interval ms: PENDING
adaptive burst interval ms: PENDING
burst trigger(s): PENDING
burst stop condition: PENDING
maximum burst duration ms: PENDING
coalescing rule: PENDING
no-eligible-focus stop rule: PENDING
lock stop rule: PENDING
maximum stable crossing detection latency ms: PENDING
maximum signal-triggered detection latency ms: PENDING
```

## Latency metrics

Report separately:

```text
crossing-to-detection latency: PENDING
crossing-to-verified-orientation latency: PENDING (requires FDM-821 adapter evidence; do not substitute detection latency)
```

## Policy/arbitration qualification

Confirm or amend the remote pure-policy contract with local adapter scope evidence:

```text
same-profile windows share opaque scope token: PENDING
scope token lifetime/expiry contract: PENDING
startup baseline behavior: PENDING
same-region refocus no-op: PENDING
same-scope wide↔narrow focus transition: PENDING
manual/external change ownership: PENDING
config-change behavior: baseline-on-config-change (remote safe default; local review PENDING)
lock/unlock cancellation/recovery: PENDING
```

## Resource observations

Record measured shell/compositor behavior for the selected strategy only. Do not infer this from CI or mocks.

```text
Quickshell CPU baseline: PENDING
Quickshell CPU during observation: PENDING
Hyprland CPU/log baseline: PENDING
Hyprland CPU/log during observation: PENDING
command/process rate: PENDING
measurement method and duration: PENDING
```

## Final contract or NO-GO rationale

PENDING.
