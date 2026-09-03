# Chrome orientation adapter research — FDM-821

This lane determines whether Chrome/Chromium's native tab-strip orientation can be read and set live through a production-safe Linux mechanism.

## Current state

**INCOMPLETE LOCAL QUALIFICATION — PRODUCTION ADAPTER NO-GO.**

The pre-existing sanitized Omarchy observation matched the Chrome AT-SPI application but exposed no focused top-level native frame. Exact focused-target ownership is a mandatory prerequisite for both `get` and `set`, so the candidate fails closed before any orientation mutation is justified.

This remote review-fix work does **not** have access to the target Omarchy session and did not rerun or extend that local evidence. It adds a deterministic privacy-safe read-only probe and a structured transcription of the already-recorded observation. Native feature availability, initial orientation, and the prescribed manual live switch remain `PENDING_LOCAL`; only phases that depend on the failed focused-target prerequisite are `SKIPPED_AFTER_HARD_GATE`.

Public Chrome/Chromium, extension, and CDP interfaces still do not provide the required exact live orientation adapter. The recorded hard-gate failure keeps production **NO-GO**, but the local qualification must not be described as complete until the required pending local evidence is actually measured.

Do not treat the presence of a state-specific Chrome menu action as GO by itself. Profile-scope identity/token separation, policy/control classification, idempotent verification, collateral-state preservation, accessibility scope, stale-target handling, and deterministic cleanup are all hard gates.

## Artifacts

- `report.md` — pinned upstream findings, rejected mechanisms, recorded local hard-gate evidence, pending/skipped matrix state, and decision rules.
- `adapter-contract.md` — proposed `probe/get/set` production boundary and failure semantics.
- `adapter-result.schema.json` — machine-readable result schema required by the contract.
- `contract-set-model.py` — pure reference model for consent/idempotence/postflight ordering; no browser side effects.
- `test-contract-set-model.py` — pure tests for no-op, consent, mismatch, managed-policy, and verification behavior.
- `probe-atspi.py` — deterministic read-only AT-SPI topology probe that prunes web/document content and never emits accessible names.
- `evidence/atspi-readonly-2026-09-02.json` — structured transcription of the pre-existing sanitized local observation; explicitly not rerun by this remote change.
- `capability-fingerprint.json` — source/target fingerprint and capability changes that warrant re-evaluation.
- `local-qualification.md` — deterministic target Omarchy matrix with explicit `PENDING_LOCAL` and `SKIPPED_AFTER_HARD_GATE` rules.

## Branch contract

This branch was created directly from FDM-825's canonical bootstrap SHA:

```text
444b31be1d12ea25729c4948a0428c5ebb72179a
```

Do not rebase this research lane onto FDM-822 or any implementation branch. FDM-826 owns convergence after both feasibility lanes are reviewed.

## Privacy/security

Remote work may inspect upstream source, prepare safe probes, pure tests, schemas, and a deterministic local runbook. Only the target Omarchy machine may claim new live browser/accessibility behavior or a GO verdict.

Do not commit raw browser/profile data. Raw local evidence belongs under ignored `research/chrome-adapter/raw/`. Sanitized evidence must not contain browser titles, URLs, profile names/paths, account data, command lines, raw accessibility trees, webpage content, or preference-file contents.

Rejected production fallbacks remain rejected: remote debugging exposure, live profile-file edits, alternate user-data directories created for debugging, global input injection, pixel automation, privileged helpers, browser restarts per switch, and unsupported internal Chromium commands.
