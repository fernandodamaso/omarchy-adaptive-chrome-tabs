#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT="${1:-$ROOT_DIR/raw/stack.local.txt}"
mkdir -p "$(dirname "$OUTPUT")"
umask 077

redact_home() {
  local value="$1"
  if [[ -n "${HOME:-}" && "$value" == "$HOME"* ]]; then
    printf '<home>%s\n' "${value#"$HOME"}"
  else
    printf '%s\n' "$value"
  fi
}

section() {
  printf '\n[%s]\n' "$1"
}

capture_optional() {
  local label="$1"
  shift
  printf '%s: ' "$label"
  if command -v "$1" >/dev/null 2>&1; then
    "$@" 2>&1 || printf '<command-failed>\n'
  else
    printf '<not-installed>\n'
  fi
}

binary_identity() {
  local binary="$1"
  printf '%s: ' "$binary"
  local resolved
  resolved="$(command -v "$binary" 2>/dev/null || true)"
  if [[ -z "$resolved" ]]; then
    printf '<not-installed>\n'
    return
  fi
  resolved="$(readlink -f "$resolved" 2>/dev/null || printf '%s' "$resolved")"
  redact_home "$resolved"
}

{
  printf 'FDM-822 stack capture\n'
  printf 'status: LOCAL_ONLY_UNQUALIFIED\n'
  printf 'privacy: no browser profiles, titles, URLs, accounts, or command lines are queried\n'

  section 'Omarchy'
  capture_optional 'version' omarchy version
  capture_optional 'channel' omarchy version channel

  section 'Hyprland and Quickshell'
  capture_optional 'hyprland' hyprctl version
  capture_optional 'quickshell' qs --version

  section 'Browser versions'
  capture_optional 'google-chrome-stable' google-chrome-stable --version
  capture_optional 'google-chrome' google-chrome --version
  capture_optional 'chromium' chromium --version

  section 'Resolved executable identity'
  binary_identity google-chrome-stable
  binary_identity google-chrome
  binary_identity chromium
  binary_identity hyprctl
  binary_identity qs

  section 'Native package fingerprints'
  if command -v pacman >/dev/null 2>&1; then
    for package in omarchy hyprland quickshell google-chrome chromium; do
      printf '%s: ' "$package"
      pacman -Q "$package" 2>/dev/null || printf '<not-installed-as-native-package>\n'
    done
  else
    printf 'pacman: <not-installed>\n'
  fi

  section 'Qualified sandbox/package candidates'
  if command -v flatpak >/dev/null 2>&1; then
    for app in com.google.Chrome org.chromium.Chromium; do
      printf 'flatpak %s: ' "$app"
      flatpak info --show-version "$app" 2>/dev/null || printf '<not-installed>\n'
    done
  else
    printf 'flatpak: <not-installed>\n'
  fi

  if command -v snap >/dev/null 2>&1; then
    printf 'snap chromium: '
    snap list chromium 2>/dev/null | tail -n +2 || printf '<not-installed>\n'
  else
    printf 'snap: <not-installed>\n'
  fi

  section 'Session mode hints'
  printf 'XDG_SESSION_TYPE: %s\n' "${XDG_SESSION_TYPE:-<unset>}"
  printf 'WAYLAND_DISPLAY: %s\n' "${WAYLAND_DISPLAY:+<set>}"
  printf 'DISPLAY: %s\n' "${DISPLAY:+<set>}"

  printf '\nNo GO/NO-GO decision is implied by this capture.\n'
} >"$OUTPUT"

printf '%s\n' "$OUTPUT"
