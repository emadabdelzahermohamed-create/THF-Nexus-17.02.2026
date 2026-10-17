#!/usr/bin/env bash
set -Eeuo pipefail

usage() {
  cat <<'EOF'
Usage: fitness_phone_qa.sh --apk PATH [--serial SERIAL] [--expected-sha256 HEX] [--record-seconds N]

Runs a fail-closed physical-phone QA evidence pass for Top Hero Fit Fitness V2.
The phone must already be authorized in `adb devices`; this script never pairs a device.
EOF
}

APK=""
SERIAL=""
EXPECTED_SHA=""
RECORD_SECONDS=30
PACKAGE="com.topherofit.thf.pulse"

while (($#)); do
  case "$1" in
    --apk) APK="${2:?missing --apk value}"; shift 2 ;;
    --serial) SERIAL="${2:?missing --serial value}"; shift 2 ;;
    --expected-sha256) EXPECTED_SHA="${2:?missing --expected-sha256 value}"; shift 2 ;;
    --record-seconds) RECORD_SECONDS="${2:?missing --record-seconds value}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
done

[[ -f "$APK" ]] || { echo "APK not found: $APK" >&2; exit 3; }
[[ "$RECORD_SECONDS" =~ ^[0-9]+$ ]] && (( RECORD_SECONDS >= 5 && RECORD_SECONDS <= 180 )) || {
  echo "--record-seconds must be 5..180" >&2; exit 4;
}
for cmd in adb sha256sum unzip awk sed grep date; do
  command -v "$cmd" >/dev/null || { echo "Missing command: $cmd" >&2; exit 5; }
done

ADB=(adb)
[[ -n "$SERIAL" ]] && ADB+=( -s "$SERIAL" )
mapfile -t DEVICES < <(adb devices | awk 'NR>1 && $2=="device" {print $1}')
if [[ -n "$SERIAL" ]]; then
  printf '%s\n' "${DEVICES[@]:-}" | grep -Fxq "$SERIAL" || {
    echo "Requested device is not connected and authorized: $SERIAL" >&2; exit 6;
  }
elif ((${#DEVICES[@]} != 1)); then
  echo "Expected exactly one authorized device; found ${#DEVICES[@]}. Pass --serial when needed." >&2
  exit 7
fi

APK_SHA="$(sha256sum "$APK" | awk '{print $1}')"
if [[ -n "$EXPECTED_SHA" && "${APK_SHA,,}" != "${EXPECTED_SHA,,}" ]]; then
  echo "APK SHA-256 mismatch: got $APK_SHA" >&2; exit 8
fi

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
OUT="fitness-phone-evidence-${STAMP}"
mkdir -p "$OUT"
exec > >(tee "$OUT/harness.log") 2>&1

echo "candidate_sha256=$APK_SHA"
echo "package=$PACKAGE"
"${ADB[@]}" get-state | grep -Fxq device
"${ADB[@]}" shell getprop ro.build.version.sdk | tee "$OUT/device_api.txt"
"${ADB[@]}" shell getprop ro.product.cpu.abilist | tee "$OUT/device_abis.txt"
"${ADB[@]}" shell getprop ro.product.manufacturer | tee "$OUT/device_manufacturer.txt"
"${ADB[@]}" shell getprop ro.product.model | tee "$OUT/device_model.txt"

unzip -l "$APK" > "$OUT/apk_entries.txt"
if unzip -l "$APK" | grep -Eq 'lib/[^/]+/'; then
  unzip -l "$APK" | awk '/lib\/[[:alnum:]_-]+\// {print $4}' | sort -u > "$OUT/apk_native_libs.txt"
else
  echo "bytecode_only=true" > "$OUT/apk_native_libs.txt"
fi

"${ADB[@]}" logcat -c
"${ADB[@]}" install -r "$APK" | tee "$OUT/install.txt"
"${ADB[@]}" shell pm path "$PACKAGE" | tee "$OUT/installed_path.txt"
"${ADB[@]}" shell dumpsys package "$PACKAGE" > "$OUT/package.txt"
grep -E 'versionCode=|versionName=|targetSdk=' "$OUT/package.txt" > "$OUT/package_identity.txt" || true

"${ADB[@]}" shell am force-stop "$PACKAGE"
"${ADB[@]}" shell monkey -p "$PACKAGE" -c android.intent.category.LAUNCHER 1 | tee "$OUT/launch.txt"
sleep 5
"${ADB[@]}" exec-out screencap -p > "$OUT/01_boot.png"
"${ADB[@]}" shell dumpsys window windows > "$OUT/window_boot.txt"
"${ADB[@]}" shell dumpsys activity activities > "$OUT/activity_boot.txt"

"${ADB[@]}" shell input keyevent KEYCODE_HOME
sleep 2
"${ADB[@]}" shell monkey -p "$PACKAGE" -c android.intent.category.LAUNCHER 1 >/dev/null
sleep 3
"${ADB[@]}" exec-out screencap -p > "$OUT/02_resume.png"

echo "Interact with Fitness now; recording ${RECORD_SECONDS}s for motion/navigation evidence."
"${ADB[@]}" shell screenrecord --time-limit "$RECORD_SECONDS" /sdcard/thf-fitness-qa.mp4 &
REC_PID=$!
wait "$REC_PID" || true
"${ADB[@]}" pull /sdcard/thf-fitness-qa.mp4 "$OUT/03_interaction.mp4" >/dev/null
"${ADB[@]}" shell rm -f /sdcard/thf-fitness-qa.mp4

"${ADB[@]}" shell pm list packages | grep -E 'healthconnect|com.google.android.apps.healthdata' > "$OUT/health_connect_packages.txt" || true
"${ADB[@]}" shell dumpsys meminfo "$PACKAGE" > "$OUT/meminfo.txt" || true
"${ADB[@]}" shell dumpsys gfxinfo "$PACKAGE" > "$OUT/gfxinfo.txt" || true
"${ADB[@]}" shell dumpsys thermalservice > "$OUT/thermal.txt" || true
"${ADB[@]}" shell dumpsys battery > "$OUT/battery.txt" || true
"${ADB[@]}" logcat -d -v threadtime > "$OUT/logcat.txt"
grep -Ei 'FATAL EXCEPTION|ANR in|AndroidRuntime|am_crash|am_anr' "$OUT/logcat.txt" > "$OUT/crash_anr.txt" || true

if [[ -s "$OUT/crash_anr.txt" ]]; then
  echo "FAIL: crash/ANR signals found in $OUT/crash_anr.txt" >&2
  exit 20
fi

(cd "$OUT" && sha256sum ./* > SHA256SUMS)
echo "PASS_NO_CRASH_ANR=true"
echo "Evidence: $OUT"
echo "Manual acceptance still required for login, Health Connect grant/data, exercise anatomy/motion, and purchase/restore."
