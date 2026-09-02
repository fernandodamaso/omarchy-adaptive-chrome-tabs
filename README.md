# Adaptive Chrome Tabs

Adaptive Chrome Tabs is a feasibility-gated Omarchy Quattro plugin project for selecting Chrome/Chromium's native horizontal or vertical tab strip from the focused eligible browser window's width.

## Status

**Research only — not installable yet.** Production implementation is blocked until both feasibility lanes return explicit GO decisions and their contracts are reconciled.

- **FDM-821:** prove a safe, idempotent, live Chrome/Chromium orientation adapter.
- **FDM-822:** prove Hyprland/Quickshell geometry freshness, eligible-window classification, and arbitration.
- **FDM-826:** reconcile both GO contracts and pin the implementation base before production code starts.

A NO-GO in either feasibility lane is a valid research outcome and blocks production implementation rather than authorizing a weaker workaround.

## Product constraints

Current research assumes:

- decisions are based on the focused eligible browser window's outer width in Hyprland logical compositor pixels, not monitor resolution;
- Chrome tab orientation is profile-scoped, while collapsed/expanded state and strip width may be window-scoped;
- the orientation preference may be profile-syncable/cross-device and therefore requires measurement and explicit opt-in before any production write;
- incognito, guest, managed, PWA/app-mode, DevTools, dialogs, PiP, fullscreen/immersive/kiosk, and other ambiguous surfaces are unsupported until explicitly qualified;
- local Omarchy validation is mandatory before release.

## Rejected production mechanisms

The project will not ship an implementation based on:

- cron or a second Quickshell process;
- persistent Chrome remote-debugging exposure or a replacement browsing profile;
- live edits to Chrome `Preferences` or `Local State`;
- blind toggle-only automation;
- global keyboard/mouse injection, pixel-coordinate automation, `ydotool`, raw input devices, or `input`-group access;
- sudo, root, setuid helpers, or an additional privileged daemon;
- unsupported Chromium internals disguised as a stable external API.

## Repository lanes

After the neutral bootstrap is pinned, research runs from sibling branches created from the exact same base:

```text
main @ BOOTSTRAP_SHA
├── research/fdm-821-chrome-orientation-adapter
└── research/fdm-822-geometry-arbitration
```

Neither research branch may declare itself the implementation base. FDM-826 owns convergence, the final ADR, protocol compatibility, merge order, and `IMPLEMENTATION_BASE_SHA`.

## Remote and local ownership

Remote GitHub workers may inspect public upstream source, add safe probes, pure tests, sanitized fixtures, documentation, and deterministic local runbooks.

Only the actual Omarchy/Hyprland/Chrome machine may claim live browser control, accessibility behavior, geometry freshness, multi-profile behavior, security/performance measurements, or a GO verdict.

## Privacy

Browser titles, URLs, profile names/paths, account identifiers, unrelated command-line arguments, tokens, secrets, and raw browser captures must not be committed or logged. Raw captures stay local and gitignored. Committed fixtures use deterministic placeholders and retain only fields required for classification, geometry, lifecycle, or preference-scope tests.

See `SECURITY.md`, `CONTRIBUTING.md`, and `tests/fixtures/README.md` before adding research artifacts.
