# Contributing

This repository is feasibility-gated. Do not skip directly to production automation.

## Issue ownership

Work only within the owning Linear issue's contract:

- FDM-821 owns Chrome orientation-adapter feasibility.
- FDM-822 owns geometry, eligible-window classification, and arbitration feasibility.
- FDM-826 owns convergence of two GO contracts and the pinned implementation base.
- FDM-823 owns production implementation only after FDM-826.
- FDM-824 owns local release qualification.

Research workers must not claim a live GO result from source inspection, mocks, or CI alone.

## Branch discipline

Research branches are created from the exact recorded `BOOTSTRAP_SHA`. Do not rebase one feasibility lane onto the other. FDM-826 owns the merge/reconciliation order after both lanes are reviewed.

Production work must start only from the exact `IMPLEMENTATION_BASE_SHA` recorded by FDM-826.

## Scope discipline

Keep probes, fixtures, tests, and documentation narrowly tied to the owning issue. Do not add production `Service.qml`, a working production `manifest.json`, or a browser-control fallback during the repository bootstrap or research-only work unless the owning issue explicitly calls for it.

## Privacy checklist

Before committing any captured data:

- remove browser titles and URLs;
- remove usernames, home directories, profile names/paths, account data, tokens, secrets, and unrelated command-line arguments;
- replace sensitive values with deterministic placeholders;
- keep raw captures only in ignored local paths;
- inspect the staged diff manually.

See `tests/fixtures/README.md` for the fixture contract.

## Executable files

Executable files are allowed only under `bin/` or `research/` and must be intentional, reviewable source scripts/helpers. Generated binaries and opaque executables must not be committed.

## Validation

The baseline workflow checks repository hygiene, Markdown whitespace, shell syntax when scripts exist, fixture privacy heuristics, common secret patterns, symlinks, and executable placement. Later implementation issues may extend CI with `qmllint`, QML tests, adapter tests, and `omarchy plugin validate`.
