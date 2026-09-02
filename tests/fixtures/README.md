# Fixture privacy and schema contract

Committed fixtures must be sanitized, minimal, deterministic, and attributable to a documented capture method.

## Required metadata

Each future fixture should document:

- fixture schema/version;
- owning research issue;
- sanitized browser/compositor version fingerprint when required;
- capture command or procedure without secrets or personal paths;
- which fields were retained and why.

## Sanitization

Before commit:

- replace browser titles and URLs with placeholders such as `<redacted-title>` and `<redacted-url>`;
- remove usernames, home directories, profile names/paths, account identifiers, tokens, secrets, and unrelated command-line arguments;
- remove extension IDs unless a test explicitly requires a synthetic placeholder;
- preserve only fields required to test classification, geometry, lifecycle, or preference-scope behavior.

Raw captures belong in ignored `raw/` directories and must never be committed.

The baseline CI intentionally rejects obvious URL/home-path/profile leakage in fixture files. Passing CI does not replace manual review.
