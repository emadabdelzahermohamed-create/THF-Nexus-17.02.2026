#!/usr/bin/env bash
set -Eeuo pipefail

PACKAGE="com.topherofit.thf.pulse"
ADB_BIN="${ADB_BIN:-adb}"
REQUESTED_SERIAL=""

usage() {
  cat <<'EOF'
Usage: fitness_phone_preflight.sh [--serial SERIAL]

Runs one read-only, fail-closed safety check before physical Fitness QA.
It never connects, pairs, wakes, unlocks, installs, launches, stops, taps,
changes permissions, or clears data. A READY result only permits a separate,
deliberate manual QA action; it does not perform that action.
EOF
}

while (($#)); do
  case "$1" in
    --serial) REQUESTED_SERIAL="${2:?missing --serial value}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
done

state() {
  printf 'qa_state=%s\n' "$1"
  exit "$2"
}

command -v "$ADB_BIN" >/dev/null || state "ADB_UNAVAILABLE" 20

DEVICE_OUTPUT="$($ADB_BIN devices -l 2>/dev/null)" || state "ADB_OFFLINE" 21
mapfile -t DEVICES < <(printf '%s\n' "$DEVICE_OUTPUT" | awk 'NR > 1 && $2 == "device" {print $1}')

if [[ -n "$REQUESTED_SERIAL" ]]; then
  if ! printf '%s\n' "${DEVICES[@]:-}" | grep -Fxq "$REQUESTED_SERIAL"; then
    state "REQUESTED_DEVICE_UNAVAILABLE" 22
  fi
  SERIAL="$REQUESTED_SERIAL"
else
  case "${#DEVICES[@]}" in
    0) state "ADB_OFFLINE" 21 ;;
    1) SERIAL="${DEVICES[0]}" ;;
    *) state "MULTIPLE_DEVICES" 23 ;;
  esac
fi

printf 'device_serial=%s\n' "$SERIAL"
ADB=("$ADB_BIN" -s "$SERIAL")

POWER="$("${ADB[@]}" shell dumpsys power 2>/dev/null)" || state "DEVICE_NOT_INTERACTIVE" 24
if ! grep -q 'mInteractive=true' <<<"$POWER"; then
  state "DEVICE_NOT_INTERACTIVE" 24
fi

WINDOW="$("${ADB[@]}" shell dumpsys window 2>/dev/null)" || state "DEVICE_LOCKED" 25
if grep -Eq 'mShowingLockscreen=true|mDreamingLockscreen=true|isStatusBarKeyguard=true' <<<"$WINDOW"; then
  state "DEVICE_LOCKED" 25
fi

PACKAGE_PATH="$("${ADB[@]}" shell pm path "$PACKAGE" 2>/dev/null)" || state "PACKAGE_NOT_INSTALLED" 26
if ! grep -q '^package:' <<<"$PACKAGE_PATH"; then
  state "PACKAGE_NOT_INSTALLED" 26
fi

PACKAGE_INFO="$("${ADB[@]}" shell dumpsys package "$PACKAGE" 2>/dev/null)" || state "PACKAGE_NOT_INSTALLED" 26
VERSION_CODE="$(grep -Eo 'versionCode=[0-9]+' <<<"$PACKAGE_INFO" | head -n1 | cut -d= -f2 || true)"
VERSION_NAME="$(grep -Eo 'versionName=[^[:space:]]+' <<<"$PACKAGE_INFO" | head -n1 | cut -d= -f2- || true)"
[[ -n "$VERSION_CODE" ]] && printf 'installed_version_code=%s\n' "$VERSION_CODE"
[[ -n "$VERSION_NAME" ]] && printf 'installed_version_name=%s\n' "$VERSION_NAME"

INSTALLER_INFO="$("${ADB[@]}" shell pm list packages -i "$PACKAGE" 2>/dev/null || true)"
INSTALLER="$(sed -n 's/.*installer=\([^[:space:]]*\).*/\1/p' <<<"$INSTALLER_INFO" | head -n1)"
[[ -n "$INSTALLER" ]] && printf 'installer=%s\n' "$INSTALLER"

SERVICE="$("${ADB[@]}" shell dumpsys activity services "$PACKAGE/.ActivityTrackingService" 2>/dev/null)" || state "SERVICE_STATE_UNKNOWN" 27
if grep -Eq 'isForeground=true|startRequested=true' <<<"$SERVICE"; then
  state "ACTIVE_TRACKING_SESSION" 28
fi

state "READY_FOR_MANUAL_QA" 0
