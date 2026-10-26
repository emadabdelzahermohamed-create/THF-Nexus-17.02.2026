#!/usr/bin/env bash
set -Eeuo pipefail

PACKAGE="com.topherofit.thf.pulse"
ADB_BIN="${ADB_BIN:-adb}"
LABEL=""
OUT=""
REQUESTED_SERIAL=""

usage() {
  cat <<'EOF'
Usage: fitness_phone_p0_snapshot.sh --label LABEL --out DIRECTORY [--serial SERIAL]

Captures one read-only evidence snapshot during an explicitly controlled P0
phone test. Run the safety preflight first. This tool never connects, pairs,
wakes, unlocks, launches, stops, taps, changes settings/permissions, installs,
or clears data.

Labels: stationary-start, true-movement, navigation, background, screen-off,
screen-on, reopened, process-death, explicit-stop, daily-steps, notification,
health-source.
EOF
}

while (($#)); do
  case "$1" in
    --label) LABEL="${2:?missing --label value}"; shift 2 ;;
    --out) OUT="${2:?missing --out value}"; shift 2 ;;
    --serial) REQUESTED_SERIAL="${2:?missing --serial value}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
done

[[ -n "$LABEL" ]] || { echo "--label is required" >&2; exit 2; }
[[ -n "$OUT" ]] || { echo "--out is required" >&2; exit 2; }
case "$LABEL" in
  stationary-start|true-movement|navigation|background|screen-off|screen-on|reopened|process-death|explicit-stop|daily-steps|notification|health-source) ;;
  *) echo "unknown --label: $LABEL" >&2; exit 2 ;;
esac
[[ ! -e "$OUT" ]] || { echo "--out already exists: $OUT" >&2; exit 3; }

state() {
  printf 'snapshot_state=%s\n' "$1"
  exit "$2"
}

for command_name in "$ADB_BIN" sha256sum awk grep sed date; do
  command -v "$command_name" >/dev/null || state "TOOL_UNAVAILABLE" 20
done

DEVICE_OUTPUT="$($ADB_BIN devices -l 2>/dev/null)" || state "ADB_OFFLINE" 21
mapfile -t DEVICES < <(printf '%s\n' "$DEVICE_OUTPUT" | awk 'NR > 1 && $2 == "device" {print $1}')
if [[ -n "$REQUESTED_SERIAL" ]]; then
  printf '%s\n' "${DEVICES[@]:-}" | grep -Fxq "$REQUESTED_SERIAL" || state "REQUESTED_DEVICE_UNAVAILABLE" 22
  SERIAL="$REQUESTED_SERIAL"
else
  case "${#DEVICES[@]}" in
    0) state "ADB_OFFLINE" 21 ;;
    1) SERIAL="${DEVICES[0]}" ;;
    *) state "MULTIPLE_DEVICES" 23 ;;
  esac
fi

ADB=("$ADB_BIN" -s "$SERIAL")
"${ADB[@]}" get-state | grep -Fxq device || state "ADB_OFFLINE" 21

mkdir -p "$OUT"
printf 'label=%s\nhost_timestamp_utc=%s\ndevice_serial=%s\npackage=%s\n' \
  "$LABEL" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$SERIAL" "$PACKAGE" > "$OUT/checkpoint.txt"

"${ADB[@]}" shell date -u +%Y-%m-%dT%H:%M:%SZ > "$OUT/device_timestamp.txt" 2>&1 || true
"${ADB[@]}" shell getprop ro.product.manufacturer > "$OUT/device_manufacturer.txt" 2>&1 || true
"${ADB[@]}" shell getprop ro.product.model > "$OUT/device_model.txt" 2>&1 || true
"${ADB[@]}" shell getprop ro.build.version.sdk > "$OUT/device_api.txt" 2>&1 || true
"${ADB[@]}" shell pm path "$PACKAGE" > "$OUT/package_path.txt" 2>&1 || true
"${ADB[@]}" shell dumpsys package "$PACKAGE" > "$OUT/package.txt" 2>&1 || true
"${ADB[@]}" shell pm list packages -i "$PACKAGE" > "$OUT/installer.txt" 2>&1 || true
"${ADB[@]}" shell dumpsys activity services "$PACKAGE/.ActivityTrackingService" > "$OUT/service.txt" 2>&1 || true
"${ADB[@]}" shell dumpsys activity activities > "$OUT/activity.txt" 2>&1 || true
"${ADB[@]}" shell dumpsys activity processes > "$OUT/processes.txt" 2>&1 || true
"${ADB[@]}" shell dumpsys activity exit-info "$PACKAGE" > "$OUT/exit_info.txt" 2>&1 || true
"${ADB[@]}" shell dumpsys location > "$OUT/location.txt" 2>&1 || true
"${ADB[@]}" shell dumpsys notification --noredact > "$OUT/notification.txt" 2>&1 || true
"${ADB[@]}" shell dumpsys power > "$OUT/power.txt" 2>&1 || true
"${ADB[@]}" shell dumpsys window > "$OUT/window.txt" 2>&1 || true
"${ADB[@]}" shell dumpsys sensorservice > "$OUT/sensorservice.txt" 2>&1 || true
"${ADB[@]}" shell dumpsys meminfo "$PACKAGE" > "$OUT/meminfo.txt" 2>&1 || true
"${ADB[@]}" shell dumpsys package "$PACKAGE" \
  | sed -n '/runtime permissions:/,/^[^ ]/p' > "$OUT/runtime_permissions.txt" 2>&1 || true
[[ -s "$OUT/runtime_permissions.txt" ]] || printf 'runtime_permissions_section=NOT_REPORTED\n' > "$OUT/runtime_permissions.txt"
"${ADB[@]}" shell appops get "$PACKAGE" > "$OUT/appops.txt" 2>&1 || true
"${ADB[@]}" logcat -d -v threadtime > "$OUT/logcat.txt" 2>&1 || true
"${ADB[@]}" exec-out screencap -p > "$OUT/screen.png" 2>/dev/null || true

for evidence in package.txt installer.txt service.txt activity.txt exit_info.txt location.txt notification.txt power.txt window.txt logcat.txt screen.png; do
  [[ -s "$OUT/$evidence" ]] || printf 'capture_status=EMPTY_OR_UNAVAILABLE\n' > "$OUT/$evidence"
done

(
  cd "$OUT"
  for file in *; do
    [[ "$file" == "SHA256SUMS" ]] || sha256sum "$file"
  done > SHA256SUMS
)

printf 'snapshot_state=CAPTURED\nlabel=%s\nevidence=%s\n' "$LABEL" "$OUT"
