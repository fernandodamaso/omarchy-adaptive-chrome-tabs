# FDM-821 — Chrome orientation adapter feasibility report

**Status:** REMOTE PHASE COMPLETE — FINAL VERDICT REQUIRES TARGET-MACHINE QUALIFICATION  
**Research branch:** `research/fdm-821-chrome-orientation-adapter`  
**Pinned branch base:** `444b31be1d12ea25729c4948a0428c5ebb72179a`  
**Remote research date:** 2026-09-02

## Decision state

No **GO — production adapter** decision is justified by remote source inspection alone.

The required investigation order leaves exactly one production candidate that still warrants local qualification: semantic Linux accessibility automation against Chrome's native browser UI. Public browser/extension/automation interfaces do not provide an exact read/set vertical-tab API for the user's existing profile, and the rejected fallback mechanisms in FDM-821 are not reconsidered here.

This branch therefore records a **pending feasibility decision**, not a soft GO. The target Omarchy machine must execute `local-qualification.md`. If the accessibility candidate fails any hard gate—especially exact focused-window/profile scoping, privacy-preserving scope-token separation, state readback, policy/control classification, idempotent set/verify, collateral-state preservation, or deterministic cleanup—the final FDM-821 result is **NO-GO**. Do not proceed to remote debugging, live preference-file editing, input injection, internal commands, or restarts as fallback work.

## Pinned public baseline

Google announced Chrome Stable `152.0.7977.75` for Linux on 2026-09-01. The matching Chromium source tag is `152.0.7977.75`, commit `4999cc1efed37c4d91dc4ce6ec4b0a50e2a9a8cb`, branched from Chromium main revision `1669021`.

The actual Omarchy machine must still record its installed browser version, package owner/source, wrapper chain, resolved executable, executable hash, sandbox/package form, and Wayland/XWayland mode. The public baseline is not permission to assume that the target machine already runs this exact build.

### Chrome 152 vertical-tab state

At tag `152.0.7977.75`:

- `kVerticalTabs` is disabled by default.
- `kVerticalTabsLaunch` is enabled by default on non-ChromeOS builds.
- `IsVerticalTabsFeatureEnabled()` returns true when either feature is enabled.
- `vertical_tabs.enabled` is a profile preference read by each window's `VerticalTabStripStateController`.
- collapsed state and uncollapsed width are tracked separately from orientation and are updated from the active window/session state.
- enabling vertical tabs for the first time also sets `vertical_tabs.enabled_first_time=true` for metrics.
- the Chrome 152 syncable-prefs database explicitly marks the former `VerticalTabsEnabled` sync entry as **no longer synced**.

The sync classification is therefore `local-only` for the pinned upstream Chrome 152 source. The local matrix still checks the installed Google Chrome package and any available Chromium package rather than assuming downstream packaging matches upstream exactly.

## Investigation results, in required order

### 1. Supported Chrome/Chromium command, policy, public extension API, or public automation API

**Result: rejected as a production mechanism.**

#### Public Chrome DevTools Protocol

Chrome 152's `Browser` protocol exposes `executeBrowserCommand`, but its `BrowserCommandId` enum contains only:

- `openTabSearch`
- `closeTabSearch`
- `openGlic`

There is no vertical-tab orientation command, preference getter/setter, or equivalent public Browser-domain operation in the pinned protocol.

Even if a future CDP command appeared, FDM-821 separately rejects exposing a persistent remote-debugging port or pipe for this feature. Chrome's remote-debugging security model also requires a non-default user data directory for the default-profile debugging switches in modern Chrome, which is incompatible with the target contract.

#### Ordinary extension APIs

`chrome.settingsPrivate` is not a normal user-installed extension API in the pinned build. `_api_features.json` makes it dependent on `permission:settingsPrivate`; `_permission_features.json` restricts that permission to component/allowlisted contexts. A regular marketplace or unpacked user extension cannot be the production adapter by requesting that private API.

No public extension API found in the pinned surface reads or writes `vertical_tabs.enabled` as Chrome's native tab-strip orientation.

#### Internal Chromium command

Chromium implements internal vertical-tab commands and state controllers. Chrome's browser UI can ultimately toggle the preference through internal code. That does not create a supported external interface. FDM-821 explicitly rejects calling an internal Chromium command that has no supported external interface, and a toggle-only operation would fail idempotence without independent current-state readback.

#### Feature switches and rollout controls

Chromium still contains a vertical-tabs enable switch/feature plumbing. Using flags, command-line switches, field-trial overrides, alternate browser channels, or a replacement user-data directory to manufacture support is explicitly out of scope and rejected by FDM-821.

#### Enterprise policy

No dedicated supported vertical-tab orientation policy or public policy setter was discovered in the pinned interface review. This is not used to assume `preferenceControl=user`: the local candidate must still distinguish an effective managed/supervised control state from a transient mismatch and return `policy-controlled` when appropriate. If semantic accessibility cannot make that distinction safely, it fails the GO contract.

### 2. Documented browser or desktop integration for the existing profile

**Result: no qualifying mechanism found.**

No documented Linux integration was found that exposes an existing Chrome profile's native orientation as an exact readable/writable state while also providing focused-window-to-profile identity, management metadata, verification, and the privacy-preserving scope token required by FDM-821.

Linux desktop launchers, `.desktop` actions, D-Bus surfaces discovered during the public-interface review, and browser command-line switches do not provide the required `probe/get/set` contract for the already-running normal browsing profile.

### 3. Semantic Linux accessibility automation

**Result: only remaining candidate; local qualification required.**

The pinned Chrome UI has a promising semantic property: the app menu renders a different menu item according to the actual controller state. When vertical tabs are displayed it presents the state-specific action corresponding to switching back to horizontal tabs; otherwise it presents the action corresponding to switching to vertical tabs. Chromium's own UI tests also exercise state-specific menu behavior.

Chrome's Views accessibility stack has a Linux platform bridge, so a local AT-SPI client may be able to identify the focused native browser window, open the browser menu semantically, read the state-specific menu item, invoke the desired action, verify the opposite state-specific action, and close the menu without coordinates or global input injection.

Remote source inspection cannot prove that the installed Chrome build actually exposes those objects/actions over AT-SPI with the required identity and cleanup semantics. It also cannot prove that an AT-SPI connection avoids enabling an unacceptable breadth of accessibility data. Those are target-machine measurements.

## Hard gates for the AT-SPI candidate

### Exact focused-window and process identity

Before any read or mutation, the adapter must fail closed unless all of the following still hold:

1. the compositor target is still the focused eligible normal browser window;
2. PID and process start time still match;
3. the process belongs to the current user;
4. the supplied PID is the approved browser process rather than a renderer/helper;
5. resolved executable/package/wrapper/sandbox identity matches an explicitly qualified fingerprint;
6. app ID/class and accessibility application identity are consistent with that browser family;
7. the request generation token is current.

A stale, replaced, spoofed, helper, or unqualified target must have no UI side effect.

### Profile scope and `scopeToken`

This is the largest structural risk.

Orientation is profile-scoped, while multiple Chrome windows—including windows from different profiles—may be hosted by one browser process. PID is therefore not an acceptable preference-scope identity.

The production adapter must demonstrate a deterministic mapping from the **focused top-level window** to exactly one profile preference scope and return an opaque equality-only token such that:

- two windows from the same profile return the same token during the declared lifetime;
- two simultaneously addressable different profiles return different tokens;
- no token reveals a profile name, profile path, account, title, or URL;
- process and adapter restarts obey the declared token lifetime without stale collisions.

No supported public profile identity primitive satisfying this contract was found remotely. If AT-SPI exposes only a display/profile name, a window-local object ID, or process identity, that is insufficient. A hash of a non-unique profile display name is also insufficient. If exact identity would require exporting an identifying profile path or a persistent secret, follow FDM-821 and record NO-GO or redesign the adapter boundary before implementation.

### Actual state readback, not last-applied state

`get(target)` must derive the browser's current effective orientation from semantic browser UI/controller state. It cannot trust a service cache, a previous requested value, a raw preference whose feature gate may make it ineffective, or a toggle history.

For the accessibility candidate, the preferred proof is mutually exclusive state-specific semantic actions (switch-to-horizontal vs switch-to-vertical) on the correctly focused window, followed by post-action semantic verification.

If the candidate exposes only a generic toggle without trustworthy current-state semantics, record NO-GO.

### Idempotent exact set

`set(target, desired)` must:

1. preflight identity and current state;
2. return `ok` without invoking the orientation action when current state already equals desired;
3. otherwise invoke exactly one state-specific semantic action;
4. revalidate target identity;
5. read the final effective state;
6. return `ok` only when verified;
7. return `conflict` with the observed final orientation when a user/sync/concurrent change is detected;
8. never perform a compensating second write in the same operation.

### Collateral mutation: first-enable metadata

Chrome 152's `VerticalTabStripStateController::OnModeChanged()` writes `vertical_tabs.enabled_first_time=true` the first time vertical tabs are enabled. This is separate from `vertical_tabs.enabled` and is documented in source as metrics-only state.

FDM-821's GO criterion says the adapter must change only tab-strip orientation and preserve unrelated/recent-use state. The local matrix must therefore include a never-enabled test profile and snapshot this field. If the acceptance contract treats this first-enable metrics write as forbidden collateral mutation, Chrome's own supported UI action cannot satisfy GO on a fresh profile and the result is NO-GO unless the product contract is deliberately revised in Linear before implementation. Do not silently waive this difference.

### Per-window collapse/width/recent-use state

A successful orientation switch must prove no unintended changes to:

- current window collapsed/expanded state;
- uncollapsed vertical-strip width;
- most-recent collapse/width fallback state;
- tabs, groups, window count/order, or focused tab;
- unrelated user preferences.

Chrome source keeps these states separate, but source separation is not a substitute for the required before/after local measurements.

### Preference control and sync impact

For upstream Chrome `152.0.7977.75`, source classifies `vertical_tabs.enabled` as no longer syncable. The adapter fingerprint may therefore report `syncImpact=local-only` only for the exact qualified build/package whose behavior matches that source.

Other Chromium builds/versions must be measured independently. If syncability is `profile-syncable` or `unknown`, mutation is default-deny and returns `consent-required` without explicit service opt-in.

The accessibility candidate must also distinguish policy/supervision control. If it cannot distinguish `policy-controlled` from a normal verification mismatch without opening privileged/settings pages, scraping sensitive data, or using unsupported internals, it fails the contract.

### Accessibility scope and visible interaction

A production candidate may inspect only Chrome's native browser chrome required for the operation. It must not traverse webpage accessibility content.

Local qualification must record whether connecting to AT-SPI:

- works with the machine's existing accessibility state;
- causes Chrome to enable broader native/renderer accessibility;
- requires a setting to be enabled;
- exposes webpage content that the probe must explicitly prune and never log.

Any required accessibility enablement must be represented by `accessibilityRequirement`. Broad enablement is not silently acceptable.

Transient browser-menu interaction is allowed for research but is GO only if production behavior is bounded and clean: no pointer movement, typing, global input, new tabs/settings pages, persistent focus loss, or menu left open after success/error/timeout/cancellation.

## Rejected production mechanisms

The following are closed by the issue contract and were not treated as fallback candidates:

- editing `Preferences` or `Local State` while Chrome runs;
- killing/restarting Chrome for a switch;
- replacing the user's normal data directory to obtain debugging access;
- remote-debugging port/pipe exposure;
- normal-extension use of `chrome.settingsPrivate`;
- private/internal Chromium commands without supported external API;
- flags, field trials, or alternate channels used to manufacture support;
- blind toggles;
- mouse-coordinate automation;
- `ydotool`, `/dev/input`, `input` group membership, or global key injection;
- `sudo`, root, setuid helpers, or a long-running helper daemon.

## Required local evidence before final decision

`local-qualification.md` is normative for the remaining work. At minimum, the final report must append sanitized evidence for:

- exact Google Chrome Stable package/version/executable/wrapper/sandbox/native window mode;
- Chromium package when available;
- actual vertical-tabs feature availability;
- accessibility semantics for horizontal/vertical state in English and Portuguese UI where practical;
- one window, two same-profile windows, and two different profiles;
- same-process multi-profile targeting if Chrome hosts that topology;
- scope-token equality/separation/lifetime/restart behavior;
- unmanaged, managed, supervised, guest, normal, and incognito behavior when available;
- fullscreen/immersive, maximized, tiled, and floating windows;
- startup/shutdown/crash/update/modal/first-run interference;
- focus loss/close between `get` and `set`;
- concurrent manual change and second in-flight request;
- PID reuse/process replacement/executable change/app-ID spoof/helper PID;
- timeout/cancellation and full owned-process/accessibility/menu cleanup;
- before/after collateral-state snapshots, including `enabled_first_time`, collapse, width, recent-use state, tabs/groups/windows/focus, and unrelated preference sentinels;
- latency and visible UI disturbance.

Raw captures stay under ignored local paths and must never be committed. Commit only sanitized aggregate evidence that contains no titles, URLs, profile names/paths, account identifiers, command lines, or preference-file contents.

## Final decision rule

After the local matrix is complete, FDM-821 must end with exactly one of:

- **GO — production adapter**: every GO criterion is demonstrated on the explicitly pinned package/executable/accessibility form, with a finalized adapter protocol and capability fingerprint.
- **NO-GO**: any required property cannot be demonstrated without using a rejected mechanism or weakening the acceptance contract.

A partial accessibility success is not GO. In particular, being able to click a state-specific menu item is insufficient if profile scope, policy classification, target identity, cleanup, or collateral preservation remains ambiguous.

## Capability re-evaluation triggers

Re-open public-interface research only if one of these changes:

- Chrome/Chromium publishes a supported exact vertical-tab read/set command or public automation API;
- CDP adds a vertical-tab browser command usable without violating the default-profile debugging constraints;
- a normal extension API gains supported access to native tab-strip orientation;
- Chrome publishes a stable Linux desktop/DBus interface that identifies the focused window's owning profile scope without disclosing profile identity;
- AT-SPI exposes a stable non-localized profile-scope identifier plus state-specific orientation actions with verified policy/control semantics;
- Chrome changes orientation from profile scope to window/process scope;
- Chrome changes the sync or first-enable collateral semantics relevant to the acceptance contract.

The machine-readable source-side fingerprint is in `capability-fingerprint.json`.

## Primary upstream evidence

- Chrome Stable release: <https://chromereleases.googleblog.com/2026/09/stable-channel-update-for-desktop.html>
- Chromium source tag: <https://chromium.googlesource.com/chromium/src/+/refs/tags/152.0.7977.75>
- Chrome 152 vertical-tab feature defaults: <https://github.com/chromium/chromium/blob/152.0.7977.75/chrome/browser/ui/tabs/features.cc>
- Chrome 152 state controller: <https://github.com/chromium/chromium/blob/152.0.7977.75/chrome/browser/ui/tabs/vertical_tab_strip_state_controller.cc>
- Chrome 152 syncable-prefs database: <https://github.com/chromium/chromium/blob/152.0.7977.75/chrome/browser/sync/prefs/chrome_syncable_prefs_database.cc>
- Chrome 152 app menu model: <https://github.com/chromium/chromium/blob/152.0.7977.75/chrome/browser/ui/toolbar/app_menu_model.cc>
- Chrome 152 extension API availability: <https://github.com/chromium/chromium/blob/152.0.7977.75/chrome/common/extensions/api/_api_features.json>
- Chrome 152 extension permission availability: <https://github.com/chromium/chromium/blob/152.0.7977.75/chrome/common/extensions/api/_permission_features.json>
- Chrome 152 CDP Browser domain: <https://github.com/chromium/chromium/blob/152.0.7977.75/third_party/blink/public/devtools_protocol/domains/Browser.pdl>
- Chrome remote-debugging security change: <https://developer.chrome.com/blog/remote-debugging-port>
