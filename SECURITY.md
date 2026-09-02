# Security Policy

## Trust model

Omarchy plugins run unsandboxed with the user's permissions inside the shared long-running Quickshell environment. A blocking process, unsafe helper, leaked browser data, or unbounded compositor query can affect the user's shell session. Treat every external command and runtime dependency as security-sensitive.

## Non-negotiable production restrictions

Do not introduce:

- sudo, root, setuid helpers, or privileged background services;
- raw input-device access, `input`-group membership, `ydotool`, global keyboard/mouse injection, or coordinate automation;
- persistent Chrome remote-debugging ports/pipes or a replacement user-data directory used solely for this feature;
- writes to Chrome `Preferences` or `Local State` while Chrome is running;
- shell interpolation of user-controlled data or `sh -c` command construction;
- browser titles, URLs, profile names/paths, account identifiers, preference contents, or unrelated command lines in logs or committed fixtures;
- hidden fallback mechanisms that bypass the approved feasibility contract.

Any candidate browser adapter must be idempotent, exact-state based, target-verified, timeout-bounded, cancellable, and able to clean up its complete owned process tree. If the only workable mechanism violates these constraints, the correct result is NO-GO.

## Research data

Raw captures remain local under ignored paths. Before committing a fixture:

1. replace titles and URLs with deterministic placeholders;
2. remove usernames, home paths, profile names/paths, accounts, tokens, secrets, unrelated command-line arguments, and unnecessary extension identifiers;
3. retain only fields required by the test;
4. record fixture schema/version and the non-sensitive capture command;
5. review the diff manually before push.

Never paste sensitive browser state into GitHub issues, pull requests, CI logs, or Linear.

## Dependency review

Document every runtime dependency, why it is required, how it is invoked, what permissions it needs, and how it is removed. Omarchy plugin validation is not a substitute for security review.

The baseline CI includes heuristic secret/privacy checks. Repository-level GitHub secret scanning should also be enabled when available, but CI heuristics must not be treated as proof that a commit contains no secrets.

## Reporting

Report suspected security or privacy problems without attaching raw browser captures or secrets. Provide the smallest sanitized reproduction possible.
