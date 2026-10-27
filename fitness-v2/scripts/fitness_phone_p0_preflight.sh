#!/usr/bin/env bash
set -Eeuo pipefail

PACKAGE="com.topherofit.thf.pulse"
ADB_BIN="${ADB_BIN:-adb}"
EXPECTED_VERSION_CODE=""
OUT=""
REQUESTED_SERIAL=""
OWNER_CONFIRMED_IDLE=0

usage() {
  cat <<'EOF'
Usage: fitness_phone_p0_preflight.sh --expected-version-code CODE --out DIRECTORY [--serial SERIAL] [--owner-confirmed-idle]

Read-only safety preflight. It never connects/pairs, wakes/unlocks, launches,
taps, stops, changes settings/permissions, installs, or clears app data.
The explicit owner-idle flag is an operator attestation, not inferred from ADB.
Proceed with interactive tests only when PREFLIGHT_READY is returned.

EOF
}

blocked() {
  printf 'preflight_state=%s\n' "$1"
  if [[ -n "$OUT" && ! -e "$OUT" ]]; then
    mkdir -p "$OUT" 2>/dev/null || true
    {
      printf 'preflight_state=%s\nhost_timestamp_utc=%s\npackage=%s\nexpected_version_code=%s\n' \
        "$1" "$(date -u +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || printf unavailable)" \
        "$PACKAGE" "${EXPECTED_VERSION_CODE:-unknown}"
      if [[ -n "${DEVICE_OUTPUT:-}" ]]; then
        printf 'device_list_capture=devices.txt\n'
        printf '%s\n' "$DEVICE_OUTPUT" > "$OUT/devices.txt"
      fi
    } > "$OUT/preflight.txt"
  fi
  exit 30
}

while (($#)); do
  case "$1" in
    --expected-version-code) EXPECTED_VERSION_CODE="${2:?missing version code}"; shift 2 ;;
    --out) OUT="${2:?missing output directory}"; shift 2 ;;
    --serial) REQUESTED_SERIAL="${2:?missing serial}"; shift 2 ;;
    --owner-confirmed-idle) OWNER_CONFIRMED_IDLE=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
done

[[ "$EXPECTED_VERSION_CODE" =~ ^[0-9]+$ ]] || { echo "--expected-version-code is required" >&2; exit 2; }
[[ -n "$OUT" ]] || { echo "--out is required" >&2; exit 2; }
[[ ! -e "$OUT" ]] || { echo "--out already exists: $OUT" >&2; exit 3; }

for command_name in "$ADB_BIN" awk grep sed date sha256sum; do
  command -v "$command_name" >/dev/null || blocked "TOOL_UNAVAILABLE"
done

DEVICE_OUTPUT="$("$ADB_BIN" devices -l 2>/dev/null)" || blocked "ADB_OFFLINE"
mapfile -t DEVICES < <(printf '%s\n' "$DEVICE_OUTPUT" | awk 'NR > 1 && $2 == "device" {print $1}')
if [[ -n "$REQUESTED_SERIAL" ]]; then
  printf '%s\n' "${DEVICES[@]:-}" | grep -Fxq "$REQUESTED_SERIAL" || blocked "REQUESTED_DEVICE_UNAVAILABLE"
  SERIAL="$REQUESTED_SERIAL"
else
  case "${#DEVICES[@]}" in
    0) blocked "ADB_OFFLINE" ;;
    1) SERIAL="${DEVICES[0]}" ;;
    *) blocked "MULTIPLE_DEVICES" ;;
  esac
fi

ADB=("$ADB_BIN" -s "$SERIAL")
"${ADB[@]}" get-state 2>/dev/null | grep -Fxq device || blocked "ADB_OFFLINE"

mkdir -p "$OUT"
printf 'host_timestamp_utc=%s\ndevice_serial=%s\npackage=%s\nexpected_version_code=%s\nowner_idle_confirmation=%s\n' \
  "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$SERIAL" "$PACKAGE" "$EXPECTED_VERSION_CODE" \
  "$([[ "$OWNER_CONFIRMED_IDLE" == 1 ]] && printf EXPLICIT || printf MISSING)" > "$OUT/preflight.txt"

capture() {
  local file="$1"; shift
  "${ADB[@]}" "$@" > "$OUT/$file" 2>&1 || printf 'capture_status=COMMAND_FAILED\n' > "$OUT/$file"
}

capture device_timestamp.txt shell date -u +%Y-%m-%dT%H:%M:%SZ
capture package.txt shell dumpsys package "$PACKAGE"
capture installer.txt shell pm list packages -i "$PACKAGE"
capture service.txt shell dumpsys activity services "$PACKAGE/.ActivityTrackingService"
capture activities.txt shell dumpsys activity activities
capture notification.txt shell dumpsys notification --noredact
capture power.txt shell dumpsys power
capture window.txt shell dumpsys window
capture keyguard.txt shell dumpsys keyguard

REPORT="$OUT/preflight.txt"
FAILURES=0
check() {
  local name="$1" result="$2" detail="$3"
  printf 'check_%s=%s\ndetail_%s=%s\n' "$name" "$result" "$name" "$detail" >> "$REPORT"
  [[ "$result" == PASS ]] || FAILURES=$((FAILURES + 1))
}

if grep -Eq "versionCode[= ]${EXPECTED_VERSION_CODE}([^0-9]|$)" "$OUT/package.txt"; then
  check installed_version PASS "$EXPECTED_VERSION_CODE"
else
  check installed_version FAIL "expected_${EXPECTED_VERSION_CODE}"
fi

if grep -Fq 'installer=com.android.vending' "$OUT/installer.txt"; then
  check google_play_installer PASS "com.android.vending"
else
  check google_play_installer FAIL "installer_not_confirmed"
fi

if grep -Eqi 'mShowingLockscreen=false|mKeyguardShowing=false|isKeyguardLocked=false' "$OUT/window.txt" "$OUT/keyguard.txt"; then
  check keyguard_unlocked PASS "explicit_unlocked_signal"
else
  check keyguard_unlocked FAIL "no_positive_unlocked_signal"
fi

if grep -Eq 'mWakefulness=Awake' "$OUT/power.txt"; then
  check device_awake PASS "mWakefulness_Awake"
else
  check device_awake FAIL "awake_not_confirmed"
fi

if grep -Eq 'mInteractive=true' "$OUT/power.txt"; then
  check device_interactive PASS "mInteractive_true"
else
  check device_interactive FAIL "interactive_not_confirmed"
fi

if grep -Eq 'ActivityTrackingService|isForeground=true|startRequested=true' "$OUT/service.txt"; then
  check tracking_service_absent FAIL "tracking_service_present_or_ambiguous"
else
  check tracking_service_absent PASS "no_tracking_service_reported"
fi

if grep -Eqi 'ActivityTrackingService|isOngoing=true|ongoing=true|FLAG_ONGOING_EVENT' "$OUT/notification.txt"; then
  check workout_notification_absent FAIL "ongoing_or_tracking_notification_present_or_ambiguous"
else
  check workout_notification_absent PASS "no_tracking_or_ongoing_notification_signal"
fi

if grep -E 'mResumedActivity|topResumedActivity|ResumedActivity' "$OUT/activities.txt" | grep -Fq "$PACKAGE"; then
  check app_not_resumed FAIL "TopHeroFit_is_resumed"
else
  check app_not_resumed PASS "TopHeroFit_not_reported_as_resumed"
fi

if [[ "$OWNER_CONFIRMED_IDLE" == 1 ]]; then
  check owner_idle_confirmation PASS "explicit_operator_attestation"
else
  check owner_idle_confirmation FAIL "explicit_owner_idle_confirmation_required"
fi

if [[ "$FAILURES" -eq 0 ]]; then
  printf 'preflight_state=PREFLIGHT_READY\n' | tee -a "$REPORT"
  EXIT_CODE=0
else
  printf 'preflight_state=PREFLIGHT_BLOCKED\nfailed_checks=%s\n' "$FAILURES" | tee -a "$REPORT"
  EXIT_CODE=30
fi

# Hash only after the report reaches its final state, so every listed digest
# validates the exact evidence files that are committed/shared.
(
  cd "$OUT"
  for file in *; do
    [[ "$file" == "SHA256SUMS" ]] || sha256sum "$file"
  done > SHA256SUMS
)
exit "$EXIT_CODE"
