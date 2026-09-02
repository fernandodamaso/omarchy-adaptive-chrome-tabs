# FDM-821 — target Omarchy qualification runbook

This runbook completes the part of FDM-821 that a remote GitHub worker cannot truthfully perform. It tests the only remaining candidate: semantic Linux accessibility automation against the installed Chrome/Chromium native browser UI.

A **GO** requires the complete applicable matrix. A **NO-GO** may stop early only when a deterministic, safe hard gate independently fails and no allowed mechanism can repair that prerequisite. Early exit is normative, not an excuse to relabel unexecuted work as passing.

When an early hard-gate exit is used:

1. record the smallest reproducible sanitized failure;
2. record the exact package/version/executable/accessibility fingerprint already known at the failure point;
3. mark every unexecuted dependent row as `SKIPPED — prerequisite hard gate failed` rather than `UNKNOWN`, `NOT TESTED`, or `PASS`;
4. do not perform a manual orientation switch or any mutation merely to fill the remaining matrix;
5. record the capability change that would require re-evaluation.

A remote worker may add source research, probes, fixtures, pure tests, and runbook improvements, but may not claim that the target Omarchy session was rerun. Any committed historical local observation must say whether the current change reproduced it.

Do not write a GO verdict until the full applicable matrix is complete. A NO-GO is valid either after the full matrix or after a documented independent early hard-gate failure under the rule above.

## Safety rules

1. Run only as the normal desktop user. No `sudo`, root service, setuid helper, `/dev/input`, `input` group changes, `ydotool`, or global input injector.
2. Do not add a remote-debugging port/pipe and do not launch the normal browsing session with an alternate `--user-data-dir`.
3. Never write Chrome `Preferences` or `Local State` to control orientation.
4. Do not commit raw captures. Use `research/chrome-adapter/raw/` for local-only evidence; it is gitignored.
5. Never record titles, URLs, profile names/paths, account identifiers, full command lines, raw accessibility trees, or preference-file contents in committed evidence.
6. Accessibility probes must prune webpage/document subtrees and inspect only native browser chrome needed for the orientation operation.
7. Use non-sensitive tabs/test data while qualifying the candidate.
8. If any step would require a forbidden mechanism, stop that lane and record the smallest sanitized failure. Do not improvise a fallback.

## Phase 1 — pin the target environment

Record a sanitized environment object with these fields:

```json
{
  "capturedAt": "ISO-8601",
  "os": "Omarchy",
  "kernel": "...",
  "hyprlandVersion": "...",
  "browserFamily": "chrome",
  "browserVersion": "...",
  "packageManager": "pacman",
  "packageName": "...",
  "packageVersion": "...",
  "launcherKind": "binary-or-wrapper",
  "resolvedExecutableFingerprint": "sha256:...",
  "sandboxForm": "native-package",
  "windowBackend": "wayland-or-xwayland",
  "verticalTabsAvailable": true,
  "locale": "en-US-or-pt-BR"
}
```

Useful read-only commands on an Arch/Omarchy host include:

```bash
command -v google-chrome-stable || command -v google-chrome || true
command -v chromium || true

google-chrome-stable --version 2>/dev/null || google-chrome --version 2>/dev/null || true
chromium --version 2>/dev/null || true

pacman -Q google-chrome 2>/dev/null || true
pacman -Q chromium 2>/dev/null || true

hyprctl version
uname -sr
```

Resolve wrapper/executable ownership locally, then store only the approved package form and executable hash in committed evidence. A local raw note may contain the path for reproducibility but must remain ignored.

For Google Chrome, compare the installed build with the public research baseline `152.0.7977.75`. Do not silently substitute current source `main` for the installed version.

For Chromium, pin its exact package/version/source revision independently if installed. If it is unavailable, record `not-installed` rather than installing an unreviewed package solely to make the matrix green.

### Pass condition

The exact package/wrapper/executable/sandbox/window-backend form is known well enough that production can allowlist it. Any alternate Flatpak, Snap, custom wrapper, or changed executable fingerprint is `unsupported` until separately qualified.

## Phase 2 — confirm native feature state

Normally, without enabling flags or field trials, confirm that the installed normal browser offers native vertical tabs and can manually switch between horizontal and vertical layouts.

Record only:

- feature available: yes/no;
- initial orientation: horizontal/vertical/unknown;
- manual switch live without browser restart: yes/no;
- feature unavailable due rollout/build: reason if known.

If the native feature is unavailable in the target package, record **NO-GO for that package/version**. Do not enable experimental flags to continue.

### Early-exit exception before manual switching

To minimize browser mutations, Phase 3's deterministic read-only focused-target probe may be run before the manual switch portion of this phase. If that probe independently proves that the compositor-focused browser window cannot be bound to one focused top-level native AT-SPI target, the production candidate already fails a mandatory security/correctness prerequisite.

In that case:

```text
feature availability: SKIPPED — independent focused-target hard gate failed first
initial orientation: SKIPPED — prerequisite hard gate failed
manual live switch: SKIPPED — no mutation required after decisive read-only failure
```

Do not perform a manual switch merely to convert those rows into measurements. If a future capability change makes the focused-target probe pass, return here and complete Phase 2 before any orientation action probe.

## Phase 3 — establish accessibility prerequisites

Inventory existing accessibility packages/services without changing configuration first:

```bash
pacman -Q at-spi2-core 2>/dev/null || true
pacman -Q python-gobject 2>/dev/null || true
busctl --user status org.a11y.Bus 2>/dev/null || true
```

The local probe may use AT-SPI through the platform's supported bindings. It must not use coordinates, synthesize global keyboard/pointer input, or walk webpage content.

### Deterministic read-only focused-target probe

Focus the intended normal Chrome/Chromium window. Extract only its compositor PID in memory and run the checked-in probe:

```bash
mkdir -p research/chrome-adapter/raw
active_pid="$(hyprctl activewindow -j | jq -er '.pid | select(type == "number" and . > 0)')"
python3 research/chrome-adapter/probe-atspi.py \
  --pid "$active_pid" \
  --browser-family chrome \
  > research/chrome-adapter/raw/atspi-probe.json
python3 -m json.tool research/chrome-adapter/raw/atspi-probe.json >/dev/null
```

For Chromium use `--browser-family chromium` after separately validating the package/executable identity.

The `hyprctl` JSON is piped directly through `jq`; do not redirect or commit the full active-window object because it can contain a title. The probe receives only the numeric PID. Its committed code:

- matches AT-SPI applications by that already-validated PID;
- prunes roles containing `document`, `web`, or `embedded` before recursion;
- bounds traversal depth/node count;
- never serializes accessible names/text;
- reads a native accessible name only in memory to classify a possible orientation-action candidate;
- emits only safe role strings, boolean focused/enabled/action predicates, counts, and probe-behavior booleans;
- never opens a menu and never invokes an orientation action.

The sanitized shape includes these decisive fields:

```json
{
  "applicationMatched": true,
  "topLevelFrameCount": 3,
  "anyTopLevelFocused": false,
  "anyActionCapability": true,
  "stateSpecificOrientationActionObserved": false,
  "menuOpenAttempted": false,
  "orientationMutationAttempted": false,
  "webDocumentSubtreesPruned": true
}
```

That block is a **shape/example**, not target evidence. Commit a real rerun only after reviewing it for privacy. Never copy raw accessibility names or a full accessibility dump into evidence.

The current branch also contains `evidence/atspi-readonly-2026-09-02.json`, a structured transcription of the pre-existing sanitized local observation. It explicitly says `reproducedByCurrentRemoteChange=false`; a remote review fix must not change that flag to true.

### Read-only topology pass/stop condition

The native browser UI must expose enough semantic structure to identify:

- the Chrome/Chromium application;
- the currently focused top-level normal browser window;
- the browser-menu button or equivalent semantic entry point;
- menu/menu-item roles and supported semantic actions.

If exactly one validated application is matched but **no top-level native frame is focused**, stop the AT-SPI candidate immediately with an early hard-gate NO-GO. Exact focused-window ownership cannot be proven, so opening a menu or attempting orientation read/set would target ambiguously. Mark Phases 2 manual-switch remainder and 4-12 mutation/profile-dependent rows `SKIPPED — prerequisite hard gate failed` as applicable.

If focused-target identity passes, continue. The probe output must still contain only role names, boolean focused/enabled/action capability, and safe aggregate predicates. Do **not** output accessible names/text because they can contain profile names, titles, URLs, or account data.

### Accessibility requirement classification

Record one of:

- `none`: candidate does not need accessibility;
- `existing`: required AT-SPI semantics are available without changing accessibility configuration;
- `must-enable`: Chrome/system accessibility must be enabled or materially broadened;
- `unknown`: cannot determine safely.

If a production implementation would require enabling broad accessibility without clear disclosure, the candidate does not meet FDM-821 as written.

## Phase 4 — prove state-specific semantic orientation readback

Only run this phase if focused-target identity passed.

Open the browser app/system/tab menu **semantically**, not by coordinates or global shortcut injection.

For an eligible focused normal window, prove that exactly one orientation action is exposed and that it corresponds to current effective state:

| Browser state | Expected semantic action meaning |
| --- | --- |
| Horizontal | switch/move tabs to vertical/side |
| Vertical | switch/move tabs to horizontal/top |

The local harness may compare localized accessible strings in memory against a versioned allowlist during research, but committed evidence must store only which semantic state was matched, not the raw labels. Prefer stable roles/action identities over text wherever AT-SPI exposes them.

Test at least:

- English UI;
- Portuguese UI when practical;
- already horizontal;
- already vertical;
- feature unavailable/unknown;
- maximized;
- tiled;
- floating;
- fullscreen/immersive.

Record whether opening/closing the semantic menu changes focus, creates UI residue, or fails in immersive mode.

### Pass condition

`get(target)` can determine the **actual effective orientation** without toggling, caching, reading live preference files, opening a settings tab, or guessing from prior service state.

If only a generic toggle is exposed and state cannot be read independently, final result is NO-GO.

## Phase 5 — prove exact idempotent `set`

For each desired state:

1. capture sanitized target identity and current effective orientation;
2. call `set(desired)`;
3. if already desired, prove no orientation action was invoked;
4. if different, prove exactly one state-specific semantic action was invoked;
5. immediately revalidate focus/PID/start-time/executable/generation;
6. read the effective final orientation independently;
7. close any transient menu/session;
8. record latency and focus/UI disturbance.

Expected results:

| Pre-state | Desired | Mutation count | Result |
| --- | --- | ---: | --- |
| horizontal | horizontal | 0 | `ok`, `changed=false`, verified horizontal |
| vertical | vertical | 0 | `ok`, `changed=false`, verified vertical |
| horizontal | vertical | 1 | `ok`, `changed=true`, verified vertical |
| vertical | horizontal | 1 | `ok`, `changed=true`, verified horizontal |

Consent ordering is part of this proof:

1. read the effective current orientation first;
2. if already desired, return the verified no-op with zero mutation even when `syncImpact` is `profile-syncable` or `unknown` and consent is absent;
3. if the state differs and the preference is managed, return `policy-controlled` with zero mutation;
4. if the state differs and `syncImpact` is `profile-syncable` or `unknown`, require consent immediately before the actual mutation;
5. after one mutation, independently verify the final state.

Run the pure reference tests before local mutation work:

```bash
python3 research/chrome-adapter/test-contract-set-model.py
```

A mismatch is never followed by a compensating second write in the same operation.

## Phase 6 — profile scope and opaque token

This phase is a hard gate and should be attempted before investing heavily in UX polish.

Prepare, when practical, all of these topologies using Chrome's normal profile system—not an alternate user-data directory created for remote debugging:

1. one normal window in profile A;
2. two normal windows in profile A;
3. one window in profile A plus one in profile B;
4. two profile windows hosted by the same browser process, if Chrome uses that topology.

The candidate must derive an opaque scope token from the **focused window's owning preference scope**.

Assert:

```text
A-window-1 token == A-window-2 token
A-window token != B-window token
```

Also test:

- switching focus A -> B -> A;
- browser-process restart;
- adapter restart;
- profile window close/reopen;
- simultaneous availability of both profiles;
- duplicate/similar profile display names if practical.

Document the token lifetime (`browser-process`, `adapter-session`, `persistent`, or `unknown`).

### Immediate NO-GO conditions

Record NO-GO if exact profile scope requires any of these:

- PID used as a proxy for profile when multiple profiles can share the process;
- profile display name as identity;
- profile path/account identifier crossing the service boundary;
- a non-unique hash of profile display data;
- persistent secret/profile identifying material without an approved boundary redesign;
- guessing that the focused window belongs to the process's "default" profile.

If the accessibility tree has no deterministic privacy-safe profile-scope primitive, stop here. Being able to toggle the right *window* is not enough because orientation affects the owning profile.

## Phase 7 — preference control and sync impact

### Sync impact

Pinned upstream Chrome `152.0.7977.75` marks the former `VerticalTabsEnabled` sync preference entry as no longer synced. For the installed exact package:

- record source-side classification;
- if a signed-in test profile and second device/profile instance are safely available, verify that a controlled orientation change does not propagate unexpectedly;
- do not expose account identifiers in evidence.

For any different Chromium/Chrome version where syncability is uncertain, return `syncImpact=unknown`. That uncertainty does not block readback or an already-desired verified no-op; it requires consent only immediately before a real mutation.

### Managed/supervised control

When an organization-managed or supervised test profile is available, determine whether orientation is user-controlled.

The production mechanism must return `policy-controlled` for an effective managed value when a mutation would be required rather than repeatedly treating it as a transient verification mismatch.

If the accessibility candidate cannot distinguish policy/supervision control without opening settings/policy pages, scraping sensitive profile data, or using unsupported internals, it fails this contract even if basic toggling works.

Guest/incognito remain unsupported by default unless exact scope and side effects are independently proven.

## Phase 8 — collateral-state proof

FDM-821 requires more than visible orientation success.

For a controlled non-sensitive test profile, capture only the specific known sentinels needed to compare state. Reading selected values for research evidence is allowed locally; it is **not** a candidate production control mechanism. Never commit the profile path, full preference file, or unrelated keys.

Track before/after values for:

- `vertical_tabs.enabled`;
- `vertical_tabs.enabled_first_time`;
- `vertical_tabs.collapsed_state`;
- `vertical_tabs.uncollapsed_width`;
- current window collapse state;
- current vertical-strip width;
- tab count/order/group count;
- window count;
- active/focused window and tab identity represented only by local ephemeral IDs;
- a small fixed set of unrelated preference sentinel hashes/values chosen in advance.

### Fresh-profile first-enable test

On a test profile where vertical tabs have never been enabled, switch horizontal -> vertical through the semantic candidate.

Chrome 152 source predicts `vertical_tabs.enabled_first_time` will change to true. Record the actual result.

If FDM-821's "change only orientation" rule rejects that metrics mutation, the final result is NO-GO for a fresh profile. Do not hide or normalize it away.

### Collapse/width preservation

Test at least:

- expanded vertical strip with a custom width;
- collapsed vertical strip;
- switch vertical -> horizontal -> vertical;
- same-profile second window with a different per-window collapse/width state when Chrome permits it.

No automation action may silently reset width/collapse/recent-use state beyond behavior explicitly accepted by FDM-821.

## Phase 9 — stale targets, spoofing, races, and conflicts

Build tests around the target descriptor rather than trusting app ID/class alone.

Required cases:

- target loses focus between `get` and `set`;
- target closes before action;
- process exits/restarts;
- PID start time mismatches (PID reuse simulation is acceptable if real reuse is impractical);
- executable path/hash changes;
- non-browser process presents a Chrome-like app ID/class;
- renderer/helper PID supplied instead of browser PID;
- generation token changes;
- second request arrives while one operation is in flight;
- user manually changes orientation after preflight but before/during verification.

Expected behavior:

- stale/spoof/helper cases -> `stale-target` or `unsupported`, zero mutation;
- second in-flight request -> `conflict`, `reasonCode=operation-in-flight`;
- manual/concurrent final-state mismatch -> `conflict` with observed final orientation, no immediate retry.

## Phase 10 — lifecycle, timeout, and cleanup

Exercise:

- browser startup;
- normal shutdown;
- crash/restart;
- browser update/relaunch;
- modal dialogs;
- first-run/update bubbles when available;
- adapter cancellation;
- deterministic timeout;
- plugin/adapter restart during an operation.

If the research harness spawns descendants, launch them in one owned process group/session. On timeout/cancel/invalidation terminate the full group and wait for exit.

After every failure path assert:

- no descendant survives;
- no accessibility session/task remains owned by the adapter;
- no menu remains open;
- no pointer movement or typed input occurred;
- focus is not persistently disrupted;
- no new tab/settings page was created.

A cleanup failure is a hard production failure, not a warning.

## Phase 11 — sanitized evidence format

Commit one aggregate result per qualified browser/package form. Example:

```json
{
  "schemaVersion": 1,
  "browserFamily": "chrome",
  "browserVersion": "152.0.7977.75",
  "packageForm": "native-arch-package",
  "executableFingerprint": "sha256:REDACTED-EXAMPLE",
  "windowBackend": "wayland",
  "accessibilityRequirement": "existing",
  "orientationRead": "pass",
  "idempotentSet": "pass",
  "sameProfileTokenEquality": "pass",
  "differentProfileTokenSeparation": "pass",
  "sameProcessMultiProfileTargeting": "pass",
  "preferenceControlClassification": "pass",
  "syncImpact": "local-only",
  "collateralState": "pass-or-fail",
  "cleanup": "pass",
  "finalCandidateResult": "pass-or-fail",
  "failureReasonCodes": []
}
```

Do not use the literal example fingerprint in real evidence. Store the actual SHA-256 fingerprint, which identifies an executable build rather than user data.

For an early hard-gate NO-GO, a smaller structured evidence object is sufficient if it includes the exact safe predicate that failed, the package/executable fingerprint already known at that point, the probe identity/version, `reproducedByCurrentRemoteChange`, and an explicit list/reason for skipped dependent phases. Do not invent booleans that were not retained by a historical observation; rerun the deterministic probe instead.

For each executed matrix row also record:

- operation/result status;
- reason code;
- initial/final orientation;
- mutation count;
- latency bucket or milliseconds;
- focus changed yes/no;
- visible transient UI yes/no;
- cleanup pass/fail;
- collateral-state pass/fail.

## Phase 12 — final verdict

Append the sanitized results to `report.md` and record exactly one final decision.

### GO — production adapter

Use only if every FDM-821 GO criterion is proven for an explicit package/executable/accessibility fingerprint and the final adapter boundary can implement `adapter-contract.md` without exceptions.

Record:

- qualified package/version/fingerprint list;
- final scope-token derivation and lifetime without sensitive material;
- exact accessibility requirement;
- preference-control behavior;
- measured sync impact;
- timeout/cancellation limits;
- accepted visible interaction;
- no-collateral proof;
- stable reason codes.

### NO-GO

Use if any hard requirement cannot be met safely. The candidate may end here either after the full matrix or through the early-exit rule when the failing prerequisite is independent of the skipped mutation/profile rows.

Record:

- pinned versions and all feature state actually measured before the stop;
- `SKIPPED — prerequisite hard gate failed` for unexecuted dependent feature/manual/mutation rows;
- smallest reproducible failure for the best candidate;
- why the failure is security/UX/correctness relevant;
- why rejected mechanisms remain rejected;
- upstream/target capability needed before re-evaluation;
- updated `capability-fingerprint.json`.

A NO-GO is successful completion of FDM-821 and blocks production implementation until the capability fingerprint materially changes.
