# Chrome orientation adapter research — FDM-821

This lane determines whether Chrome/Chromium's native tab-strip orientation can be read and set live through a production-safe Linux mechanism.

## Current state

**Remote research is complete; the final GO/NO-GO verdict is intentionally pending target-machine qualification.**

Public Chrome/Chromium, extension, and CDP interfaces do not provide the required exact live orientation adapter. The only remaining candidate is semantic Linux accessibility automation against Chrome's native state-specific orientation UI, and FDM-821 requires that behavior to be measured on the real Omarchy machine before a production decision.

Do not treat the presence of a state-specific Chrome menu action as GO by itself. Profile-scope identity/token separation, policy/control classification, idempotent verification, collateral-state preservation, accessibility scope, stale-target handling, and deterministic cleanup are all hard gates.

## Artifacts

- `report.md` — pinned upstream findings, rejected mechanisms, remaining candidate, and final decision rules.
- `adapter-contract.md` — proposed `probe/get/set` production boundary and failure semantics.
- `adapter-result.schema.json` — machine-readable result schema required by the contract.
- `capability-fingerprint.json` — source-side fingerprint and upstream changes that warrant re-evaluation.
- `local-qualification.md` — deterministic target Omarchy matrix that must be executed before the verdict.

## Branch contract

This branch was created directly from FDM-825's canonical bootstrap SHA:

```text
444b31be1d12ea25729c4948a0428c5ebb72179a
```

Do not rebase this research lane onto FDM-822 or any implementation branch. FDM-826 owns convergence after both feasibility lanes are reviewed.

## Privacy/security

Remote work may inspect upstream source, prepare safe probes, pure tests, schemas, and a deterministic local runbook. Only the target Omarchy machine may claim live browser/accessibility behavior or a GO verdict.

Do not commit raw browser/profile data. Raw local evidence belongs under ignored `research/chrome-adapter/raw/`. Sanitized evidence must not contain browser titles, URLs, profile names/paths, account data, command lines, raw accessibility trees, webpage content, or preference-file contents.

Rejected production fallbacks remain rejected: remote debugging exposure, live profile-file edits, alternate user-data directories created for debugging, global input injection, pixel automation, privileged helpers, browser restarts per switch, and unsupported internal Chromium commands.
