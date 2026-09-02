# Fixture privacy and schema contract

Committed fixtures must be sanitized, minimal, deterministic, and attributable to a documented capture method.

## Required metadata

Each fixture records its schema version, owning research issue, provenance, non-sensitive stack fingerprint status, and the retained fields required by its test.

FDM-822 fixtures live under `tests/fixtures/fdm-822/`. `fixture-schema.json` is the checked contract. Current committed examples are explicitly synthetic and must not be described as live Hyprland/Chrome evidence.

## Sanitization

Before commit:

- omit browser titles, URLs, document names, profile names/paths, account identifiers, tokens, secrets, PIDs, window addresses, and unrelated command lines;
- omit workspace names and monitor serial/description data unless an approved future test proves a non-sensitive need;
- preserve only fields required to test classification, geometry, lifecycle, or preference-scope behavior;
- keep live/local captures under ignored `research/**/raw/` or `tests/fixtures/raw/` paths;
- manually inspect any fixture promoted from local evidence.

FDM-822's local sanitizer deliberately emits `geometry.unit=unverified` until the pinned-stack run proves the exact logical-width contract. Passing CI does not replace manual privacy review or local qualification.
