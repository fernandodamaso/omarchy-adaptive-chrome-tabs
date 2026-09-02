# FDM-821 — proposed production adapter contract

This document defines the boundary that a locally qualified Chrome/Chromium orientation mechanism must satisfy. It does **not** assert that a qualifying mechanism exists.

## Operations

```text
probe(target) -> AdapterResult
get(target) -> AdapterResult
set(target, desiredOrientation, consent) -> AdapterResult
```

`probe` answers whether the exact target/package/window/profile scope can be safely handled. `get` returns the current effective native tab-strip orientation. `set` applies one exact desired orientation and verifies the final effective state.

## Request boundary

The service must not send a profile name, profile path, browser title, URL, account identifier, command line, preference-file contents, or arbitrary shell text.

A target contains only:

```json
{
  "compositorAddress": "0xopaque-window-address",
  "pid": 1234,
  "processStartTime": "987654321",
  "appIdClass": "google-chrome",
  "browserFamily": "chrome",
  "executableFingerprint": "sha256:...",
  "generationToken": "opaque-service-generation"
}
```

Fields:

- `compositorAddress`: opaque compositor window identity; never shell-interpolated.
- `pid`: expected browser-process PID.
- `processStartTime`: exact process start-time token, encoded as a string so no integer precision is lost.
- `appIdClass`: normalized expected compositor app ID/class.
- `browserFamily`: `chrome` or `chromium`.
- `executableFingerprint`: approved executable/package fingerprint, preferably a SHA-256 identity plus an adapter-side allowlist entry for wrapper/package form.
- `generationToken`: service-owned token used to reject stale work after focus/region/reload transitions.

The adapter independently revalidates every security-sensitive property. Request fields are claims, not authority.

## Result shape

Every operation returns one machine-readable object matching `adapter-result.schema.json`.

Required fields:

```json
{
  "schemaVersion": 1,
  "status": "ok",
  "orientation": "vertical",
  "scope": "profile",
  "scopeToken": "opaque-equality-token",
  "scopeTokenLifetime": "adapter-session",
  "preferenceControl": "user",
  "syncImpact": "local-only",
  "accessibilityRequirement": "existing",
  "browserFamily": "chrome",
  "browserVersion": "152.0.7977.75",
  "reasonCode": "verified",
  "changed": false,
  "verified": true
}
```

### `status`

Allowed values are fixed by FDM-821:

- `ok`: operation completed and any requested mutation is verified.
- `unsupported`: target/package/window/profile/capability is not explicitly qualified. No mutation occurred.
- `stale-target`: target identity, process lifetime, focus, executable, or generation no longer matches. No mutation occurred after staleness was detected.
- `timeout`: deterministic deadline expired; owned descendants/session/UI were cleaned up.
- `conflict`: another request or observed user/browser change made the preflight state invalid, or post-set verification observed a conflicting final state. No compensating second write is made.
- `consent-required`: mutation may be profile-syncable or sync impact is unknown and explicit opt-in is absent.
- `policy-controlled`: effective preference is controlled by policy/supervision and is not retried as transient failure.
- `error`: bounded internal failure not represented by a more specific status.

### `orientation`

- `vertical`
- `horizontal`
- `unknown`

`unknown` is mandatory when the adapter cannot read the **effective current browser UI state**. It must not infer orientation from the service's last request.

### `scope`

- `profile`
- `browser-process`
- `window`
- `unknown`

For Chrome 152's native orientation, a qualifying adapter is expected to return `profile`; any other value must be justified by the exact browser build being probed.

### `scopeToken`

Opaque equality-only token for the effective preference scope, or `null` when scope cannot safely be identified.

Requirements:

- same-profile windows -> same token during declared lifetime;
- different simultaneously addressable profiles -> different tokens;
- token reveals no profile name/path/account/title/URL;
- consumers compare only equality;
- no token may be derived from PID alone when profile scope can contain multiple profiles in one process;
- no persistent identifying profile material crosses the service boundary.

If these properties cannot be proven, the production adapter is NO-GO rather than `scopeToken` being approximated.

### `scopeTokenLifetime`

- `browser-process`
- `adapter-session`
- `persistent`
- `unknown`

Prefer the shortest lifetime that still meets the product's same-profile association requirement. `persistent` requires an explicit privacy/security justification and must not depend on exporting an identifying profile path or account data.

### `preferenceControl`

- `user`
- `managed`
- `unknown`

A managed effective preference must produce `status=policy-controlled` for `set`. A mechanism that cannot distinguish management from ordinary verification failure cannot be promoted to production.

### `syncImpact`

- `local-only`
- `profile-syncable`
- `unknown`

For `profile-syncable` or `unknown`, `set` is default-deny and returns `consent-required` unless the request carries the documented explicit opt-in.

### `accessibilityRequirement`

- `none`: accessibility is not used.
- `existing`: adapter uses an already available semantic accessibility surface without changing browser/system accessibility configuration.
- `must-enable`: operation requires enabling accessibility capability; this must be disclosed and separately approved before production use.
- `unknown`: cannot determine requirement safely.

The adapter must never traverse/log webpage accessibility content for this feature.

### `changed` and `verified`

These two optional contract extensions make idempotence observable:

- `changed=false`, `verified=true` when `set` finds the desired orientation already active.
- `changed=true`, `verified=true` when exactly one desired-state mutation was required and postflight succeeded.
- `changed=null` and/or `verified=false` for unsupported/error states where no trustworthy conclusion is available.

## Reason codes

Reason codes are stable kebab-case machine identifiers. The initial reserved set is:

```text
verified
already-desired
capability-not-qualified
browser-version-not-qualified
package-form-not-qualified
executable-mismatch
wrong-user
helper-pid
pid-reused
focus-changed
generation-stale
app-identity-mismatch
profile-scope-ambiguous
scope-token-unavailable
orientation-unreadable
semantic-action-unavailable
accessibility-unavailable
accessibility-enablement-required
managed-preference
sync-consent-required
operation-in-flight
postflight-target-changed
postflight-orientation-mismatch
concurrent-user-change
collateral-state-changed
cleanup-failed
deadline-exceeded
internal-error
```

New reason codes may be added compatibly; existing meanings must not be silently repurposed.

## `probe(target)`

`probe` is side-effect free with respect to browser orientation and browser UI.

It must validate:

1. target shape and schema version;
2. current user ownership;
3. PID start time;
4. approved top-level browser executable rather than helper/renderer;
5. package/wrapper/sandbox fingerprint;
6. current focused eligible browser-window identity;
7. browser family/version/feature availability;
8. availability of the qualified semantic mechanism;
9. ability to resolve the preference scope and return a valid `scopeToken`;
10. preference-control and sync-impact classification when they can be known without mutation.

`probe` returns `unsupported` rather than optimistic capability when exact profile scoping or package identity is unresolved.

## `get(target)`

`get` repeats all mutable identity checks immediately before reading state.

A valid read is the effective native orientation displayed by Chrome, not merely a stored preference. For an accessibility implementation, mutually exclusive state-specific semantic actions are a candidate read signal only after local qualification proves they correspond exactly to effective orientation.

`get` must not:

- open settings/new tabs;
- read profile files;
- inspect page content;
- rely on last-applied state;
- invoke the orientation toggle;
- expose profile/title/URL data in diagnostics.

## `set(target, desired, consent)`

Pseudocode:

```text
validate request
serialize operation
preflight target identity + focus + generation
resolve exact preference scope
classify control + sync impact
if managed -> policy-controlled
if syncable/unknown and consent absent -> consent-required
read effective orientation
if unknown -> unsupported
if orientation == desired -> ok(changed=false, verified=true)
snapshot allowed collateral sentinels
revalidate target identity
invoke exactly one qualified state-specific semantic action
revalidate target identity
read effective final orientation
compare collateral sentinels
if concurrent/manual conflict -> conflict(final observed state), no retry
if final != desired -> conflict/error, no second write
if collateral changed beyond approved orientation effect -> error/conflict and candidate fails qualification
cleanup all transient UI/session/process state
return ok(changed=true, verified=true)
```

No second mutation is performed to "repair" a mismatch inside the same request.

## Concurrency

Until a trustworthy profile scope is resolved, serialize adapter operations at least per browser process; a stricter single-operation adapter-session lock is acceptable for v1.

If a second request arrives while one is in flight, it returns:

```text
status=conflict
reasonCode=operation-in-flight
```

It must not race the first operation or queue indefinitely. A later service region transition may retry normally.

## Target invalidation

At minimum, invalidate the operation when any of these changes:

- compositor focus leaves the target window;
- target window closes;
- PID exits or start time changes;
- executable fingerprint/resolution changes;
- app ID/class no longer matches;
- browser process is replaced during update/relaunch;
- service generation token changes;
- accessibility top-level target can no longer be proven to be the same focused browser window.

Target invalidation closes any adapter-opened menu/session and terminates owned descendants before returning.

## Deadlines and cancellation

Every operation has a deterministic bounded deadline chosen by implementation and documented in the final report.

Any subprocess must be created in an adapter-owned process group/session. On cancellation, timeout, plugin reload, or target invalidation, terminate the full owned process tree and wait for exit. No detached child, accessibility client/session, browser menu, or browser-side task may survive.

If cleanup cannot be proven, return `error` with `reasonCode=cleanup-failed`; repeated automation must be suppressed until a later safe transition.

## Logging/privacy

Allowed structured diagnostics:

- schema version;
- operation/status/reason code;
- browser family/version;
- approved package-form identifier;
- hashed executable fingerprint;
- orientation/scope/scope-token equality value;
- boolean identity checks;
- latency/deadline/cancellation outcome.

Never log:

- tab/window titles;
- URLs;
- profile names or paths;
- account identifiers;
- complete command lines;
- raw accessibility trees;
- webpage content;
- preference-file contents;
- raw captured browser/profile data.

## Promotion rule

This contract becomes a production interface only after `local-qualification.md` proves one mechanism satisfies every FDM-821 GO criterion. Otherwise the final implementation is intentionally absent and FDM-821 records NO-GO.
