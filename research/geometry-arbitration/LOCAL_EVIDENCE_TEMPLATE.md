# FDM-822 local evidence report

## Decision status

```text
NO-GO
```

This is a successful feasibility result, not a production implementation. The
target machine did not provide enough evidence to qualify a fresh, bounded,
logical-pixel geometry contract for every required resize/lifecycle path.

## Capture boundary and safety

Captured 2026-09-02 on the target Omarchy desktop using only read-only,
one-shot `hyprctl` snapshots, a bounded socket2 event probe, pure policy tests,
and an AT-SPI topology read. No Chrome preference/profile write, orientation
action, remote-debugging endpoint, alternate data directory, global input,
privileged helper, or production service was used. Raw snapshots remain under
the ignored `research/geometry-arbitration/raw/` directory and are not evidence
artifacts.

## Pinned stack

| Component | Exact version/build | Reproducible command | Notes |
| --- | --- | --- | --- |
| Omarchy Quattro | `4.0.2-1` | `omarchy version` | stable channel |
| Omarchy channel | `stable` | `omarchy version channel` | |
| Hyprland | `0.56.2-1`, commit `efb50993780079460b0cbed1363e2166a2de1d9f` | `hyprctl version` | Wayland session |
| Quickshell | `0.3.1-1` | `qs --version` | Arch package |
| Chrome Stable | `152.0.7977.64-1` | `google-chrome-stable --version` | native package; executable SHA-256 `04e973a4c359a87ef63871ec8726e08fabe9919c60f972d5ca6f56f80a2939ed` |
| Chromium | `151.0.7922.173-1` | `chromium --version` | installed, not observed as a target window; executable SHA-256 `78f94ee05d5d6fd1bd8239b9700d3cf54d540911febad4c7cea01080273943f9` |
| Session | Wayland (`XDG_SESSION_TYPE=wayland`) | environment capture | native Wayland browser window observed; XWayland variant not tested |
| Monitors | two `1920x1080`, scale `1.0`, transform `0` | `hyprctl monitors -j` | fractional scale/rotation/hotplug not available in this run |

### FDM-816 reuse check

```text
FDM-816 exact Omarchy match: YES (4.0.2-1)
FDM-816 exact Hyprland match: YES (0.56.2-1, commit efb5099…)
FDM-816 exact Quickshell match: YES (0.3.1-1)
Reuse permitted: YES, aggregate reference only
```

The matching FDM-816 run recorded no dedicated pixel-level geometry event and
used a research-only 12-sample, 250 ms bounded sampler. Its command durations
were 3.873–4.236 ms. That result is not treated as proof that FDM-822 can
detect every crossing or meet an end-to-end latency budget.

## Browser/package identity qualification

| Variant | Package source | Native Wayland/XWayland | Stable compositor identity | Normal-tabbed distinguishable | Controlling? |
| --- | --- | --- | --- | --- | --- |
| Chrome Stable | native pacman package | Wayland observed | `google-chrome` | NO; local semantic/focus proof incomplete | NO |
| Chromium | native pacman package | not observed | not observed | NO | NO |
| Chrome Beta/Dev/Canary | not installed/observed | unsupported | unavailable | NO | NO |
| Flatpak/Snap/wrapper | not installed | unsupported | unavailable | NO | NO; fail closed |
| Incognito | not provisioned for this run | unsupported by default | unavailable | NO | NO; requires FDM-821 scope proof |
| Guest | not provisioned for this run | unsupported by default | unavailable | NO | NO; requires FDM-821 scope proof |
| Managed | no managed test profile available | unsupported | unavailable | NO | NO; policy state unproven |
| PWA / `--app` | not exercised | unsupported | fail-closed fixture only | NO | NO |
| DevTools / popup / dialog / PiP | not exercised | unsupported | fail-closed fixture only | NO | NO |

The sanitized active checkpoint contained one allowlisted `google-chrome`
surface with outer snapshot size `1896x951`, but its package qualification,
normal-tabbed identity, and logical geometry unit were deliberately left
unqualified.

## Accessibility topology (read-only)

AT-SPI prerequisites were already installed (`at-spi2-core 2.60.6-1`,
`python-gobject 3.56.3-1`) and the user accessibility bus was present. The
matching Chrome application exposed three frame objects and menu-capable
actions, but no application or frame carried the focused state. No
state-specific orientation action was exposed in the inspected topology.
This is insufficient to map the focused compositor window to a safe controlling
surface; no menu was opened and no orientation action was invoked.

## Geometry field qualification

```text
Selected outer-width field: hyprctl activewindow/clients size[0] (observed only)
Reported unit: UNVERIFIED
Finite-positive normalization: implemented by the pure prototype; not promoted to a live contract
Fractional handling: NOT MEASURED (only scale 1.0 available)
Border inclusion: UNKNOWN (border option observed as 2; inclusion not proven)
Gap inclusion: UNKNOWN
Shadow/decoration inclusion: UNKNOWN (rounding observed as 0)
Rounding behavior: UNKNOWN
```

At scale `1.0`, a `1920`-logical-width monitor contained a `1896`-wide tiled
Chrome snapshot at an inset position. This single checkpoint cannot distinguish
logical pixels from a coincident physical value or prove border/gap/decorative
semantics. Zero, negative, non-finite, and transient values remain unknown as
required.

### Scale/transform matrix

| Scale/transform | Reported client width | Physical comparison | Logical/physical conclusion |
| --- | ---: | ---: | --- |
| 1.0 / transform 0 | 1896 (single checkpoint) | monitor width 1920 | unverified |
| 1.25 | not available | not measured | unsupported in this run |
| 1.5 | not available | not measured | unsupported in this run |
| 2.0 | not available | not measured | unsupported in this run |
| rotated monitor | not available | not measured | unsupported in this run |

## Geometry freshness matrix

No manual or programmatic resize was performed; global input and compositor
state mutation were out of scope. Rows marked `not measured` are explicit
unsupported cases, not successful observations.

| Case | Source/trigger | Crossing-to-detection ms | Stale/missed? | Notes |
| --- | --- | ---: | --- | --- |
| slow tiled resize | not measured | N/A | UNKNOWN | requires manual matrix run |
| rapid tiled resize | not measured | N/A | UNKNOWN | requires manual matrix run |
| slow floating resize | not measured | N/A | UNKNOWN | requires manual matrix run |
| rapid floating resize | not measured | N/A | UNKNOWN | requires manual matrix run |
| mouse resize after 60s stable focus | not measured | N/A | UNKNOWN | long-focus crossing unavailable |
| keyboard resize after 60s stable focus | not measured | N/A | UNKNOWN | global input forbidden |
| unrelated tiled-window reflow | not measured | N/A | UNKNOWN | requires controlled layout change |
| floating movement without resize | not measured | N/A | UNKNOWN | requires controlled movement |
| maximize / restore | not measured | N/A | UNKNOWN | raw fullscreen-like fields not mapped here |
| fullscreen / immersive / kiosk enter | fail-closed classifier | N/A | N/A | no controlling request |
| fullscreen / immersive / kiosk exit | fail-closed classifier | N/A | N/A | fresh dwell required but unmeasured |
| split/master layout change | not measured | N/A | UNKNOWN | requires controlled layout change |
| move between monitors | not measured | N/A | UNKNOWN | requires controlled move |
| workspace/special workspace | socket2 names only | N/A | UNKNOWN | no geometry proof |
| monitor scale/transform | not measured | N/A | UNKNOWN | fractional/rotation unavailable |
| rearrange/hotplug/unplug | not measured | N/A | UNKNOWN | unavailable |
| suspend/resume | not measured | N/A | UNKNOWN | unavailable |
| shell/compositor reload | not measured | N/A | UNKNOWN | unavailable |
| lock/unlock | fail-closed policy only | N/A | N/A | no sampling/action while locked |

## Bounded event observations

The reviewed socket2 helper ran for 2 seconds while idle and again for 30
seconds. The idle run produced no events. The 30-second run produced only
`focusedmon`, `focusedmonv2`, `activewindow`, `activewindowv2`, `windowtitle`,
and `windowtitlev2`; it produced no resize or geometry event. Event payloads
were discarded. Therefore no direct event strategy was qualified, and the
required threshold-crossing latency cannot be claimed.

## Observation strategy decision

1. Dedicated fresh toplevel geometry property/event: **NOT QUALIFIED**; the
   selected `size[0]` field is not proven logical or fresh.
2. Supported begin/end resize signal plus coalesced refresh: **NOT PROVEN**;
   bounded socket2 observation showed no resize/geometry event.
3. Lifecycle/layout events plus one coalesced refresh: **NOT PROVEN**;
   matching FDM-816 evidence found no dedicated pixel-level event and this run
   did not establish coverage of every resize path.
4. Focused-browser sentinel plus adaptive burst: **NOT QUALIFIED**; no
   measured crossing, latency, or resource budget exists for this target.
5. **NO-GO** under the issue contract: a safe, fully measured observation
   strategy is not available from the evidence gathered without further
   controlled local instrumentation.

## Latency metrics

```text
crossing-to-detection latency: NOT MEASURED (no controlled crossing)
crossing-to-verified-orientation latency: NOT APPLICABLE; FDM-821 adapter is not locally qualified
```

## Policy/arbitration qualification

The remote pure policy and classifier passed all 39 deterministic tests on this
machine. Real adapter scope evidence was unavailable, so these remain
prototype-only:

```text
same-profile windows share opaque scope token: NOT PROVEN
scope token lifetime/expiry contract: NOT PROVEN
startup baseline behavior: PURE-POLICY TESTED; LIVE SCOPE UNPROVEN
same-region refocus no-op: PURE-POLICY TESTED; LIVE FOCUS UNPROVEN
same-scope wide↔narrow focus transition: PURE-POLICY TESTED; LIVE GEOMETRY UNPROVEN
manual/external change ownership: PURE-POLICY TESTED; LIVE ORIENTATION UNPROVEN
config-change behavior: baseline-on-config-change (pure-policy tested)
lock/unlock cancellation/recovery: PURE-POLICY TESTED; LIVE LOCK UNPROVEN
```

## Resource observations

```text
Quickshell CPU baseline: NOT MEASURED for an FDM-822 strategy
Quickshell CPU during observation: NOT MEASURED for an FDM-822 strategy
Hyprland CPU/log baseline: NOT MEASURED for an FDM-822 strategy
Hyprland CPU/log during observation: NOT MEASURED for an FDM-822 strategy
command/process rate: no continuous subprocess poller; only bounded one-shot helpers
measurement method and duration: 2 s and 30 s socket2 probes; no selected production strategy
```

## Final NO-GO rationale

**NO-GO — observation contract.** On the pinned Omarchy 4.0.2 / Hyprland
0.56.2 / Quickshell 0.3.1 stack, `hyprctl ... size[0]` was observable but its
logical-unit and border/gap/decoration semantics were not proven. The 30-second
bounded socket2 probe produced focus/title notifications but no resize-geometry
event, and the exact-version FDM-816 aggregate likewise found no dedicated
pixel-level geometry event. AT-SPI exposed Chrome application/frame objects but
not a focused state or state-specific orientation surface. The full resize,
fractional-scale, lifecycle, and resource matrix therefore cannot support a
bounded GO contract. The classifier and policy remain safe fail-closed research
artifacts; no production service or Chrome orientation action is authorized.
