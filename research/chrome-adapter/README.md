# Chrome orientation adapter research — FDM-821

This lane determines whether Chrome/Chromium's native tab-strip orientation can be read and set live through a production-safe Linux mechanism.

## Current state

**NO-GO — early hard-gate exit on the recorded local AT-SPI observation.** This is not a claim that the full mutation/profile matrix was executed.

The pre-existing sanitized Omarchy observation matched the Chrome AT-SPI application but exposed no focused top-level native frame and no state-specific orientation action in the read-only topology. Exact focused-target ownership is a mandatory prerequisite for both `get` and `set`, so the candidate fails closed before any orientation mutation is justified.

This remote review-fix change does **not** have access to the target Omarchy session and did not rerun or extend that local evidence. It adds a deterministic privacy-safe read-only probe and a structured transcription of the already-recorded observation. Under `local-qualification.md`'s explicit early-exit rule, feature/manual-switch and mutation-dependent rows are marked `SKIPPED — prerequisite hard gate failed` rather than being presented as completed tests.

Public Chrome/Chromium, extension, and CDP interfaces still do not provide the required exact live orientation adapter. Re-evaluate the AT-SPI candidate only when the capability fingerprint materially changes or the target machine reruns the probe and no longer reproduces the focused-target failure.

Do not treat the presence of a state-specific Chrome menu action as GO by itself. Profile-scope identity/token separation, policy/control classification, idempotent verification, collateral-state preservation, accessibility scope, stale-target handling, and deterministic cleanup are all hard gates.

## Artifacts

- `report.md` — pinned upstream findings, rejected mechanisms, recorded local early-exit evidence, and final decision rules.
- `adapter-contract.md` — proposed `probe/get/set` production boundary and failure semantics.
- `adapter-result.schema.json` — machine-readable result schema required by the contract.
- `contract-set-model.py` — pure reference model for consent/idempotence/postflight ordering; no browser side effects.
- `test-contract-set-model.py` — pure tests for no-op, consent, mismatch, managed-policy, and verification behavior.
- `probe-atspi.py` — deterministic read-only AT-SPI topology probe that prunes web/document content and never emits accessible names.
- `evidence/atspi-readonly-2026-09-02.json` — structured transcription of the pre-existing sanitized local observation; explicitly not rerun by this remote change.
- `capability-fingerprint.json` — source/target fingerprint and capability changes that warrant re-evaluation.
- `local-qualification.md` — deterministic target Omarchy matrix plus the normative early hard-gate exit rule.

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
