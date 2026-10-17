#!/usr/bin/env bash
set -Eeuo pipefail

usage() {
  cat <<'EOF'
Usage: fitness_phone_qa.sh --apk PATH [--serial SERIAL] [--expected-sha256 HEX]
       [--adb-connect PRIVATE_IP:PORT] [--record-seconds N] [--monkey-events N]
       [--instrumentation PACKAGE/RUNNER] [--require-health-connect]

Runs a fail-closed physical-phone QA evidence pass for Top Hero Fit Fitness V2.
The phone must already be authorized in `adb devices`; this script never pairs a device.
EOF
}

APK=""
SERIAL=""
ADB_CONNECT=""
EXPECTED_SHA=""
RECORD_SECONDS=30
MONKEY_EVENTS=50
INSTRUMENTATION=""
REQUIRE_HEALTH_CONNECT=false
PACKAGE="com.topherofit.thf.pulse"
REQUIRED_TARGET_SDK=36
REQUIRED_ABI="arm64-v8a"

while (($#)); do
  case "$1" in
    --apk) APK="${2:?missing --apk value}"; shift 2 ;;
    --serial) SERIAL="${2:?missing --serial value}"; shift 2 ;;
    --adb-connect) ADB_CONNECT="${2:?missing --adb-connect value}"; shift 2 ;;
    --expected-sha256) EXPECTED_SHA="${2:?missing --expected-sha256 value}"; shift 2 ;;
    --record-seconds) RECORD_SECONDS="${2:?missing --record-seconds value}"; shift 2 ;;
    --monkey-events) MONKEY_EVENTS="${2:?missing --monkey-events value}"; shift 2 ;;
    --instrumentation) INSTRUMENTATION="${2:?missing --instrumentation value}"; shift 2 ;;
    --require-health-connect) REQUIRE_HEALTH_CONNECT=true; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
done

[[ -f "$APK" ]] || { echo "APK not found: $APK" >&2; exit 3; }
[[ "$RECORD_SECONDS" =~ ^[0-9]+$ ]] && (( RECORD_SECONDS >= 5 && RECORD_SECONDS <= 180 )) || {
  echo "--record-seconds must be 5..180" >&2; exit 4;
}
[[ "$MONKEY_EVENTS" =~ ^[0-9]+$ ]] && (( MONKEY_EVENTS >= 0 && MONKEY_EVENTS <= 500 )) || {
  echo "--monkey-events must be 0..500" >&2; exit 4;
}
for cmd in adb sha256sum unzip awk sed grep date; do
  command -v "$cmd" >/dev/null || { echo "Missing command: $cmd" >&2; exit 5; }
done

if [[ -n "$ADB_CONNECT" ]]; then
  [[ "$ADB_CONNECT" =~ ^(10\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}|192\.168\.[0-9]{1,3}\.[0-9]{1,3}|172\.(1[6-9]|2[0-9]|3[01])\.[0-9]{1,3}\.[0-9]{1,3}):([0-9]{1,5})$ ]] || {
    echo "--adb-connect accepts a private LAN IPv4 address and port only" >&2; exit 5
  }
  ADB_PORT="${BASH_REMATCH[3]}"
  (( ADB_PORT >= 1 && ADB_PORT <= 65535 )) || {
    echo "--adb-connect port must be 1..65535" >&2; exit 5
  }
  adb connect "$ADB_CONNECT" >/dev/null || {
    echo "Authorized ADB Wireless connection failed" >&2; exit 6
  }
  SERIAL="$ADB_CONNECT"
fi

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
DEVICE_API="$("${ADB[@]}" shell getprop ro.build.version.sdk | tr -d '\r')"
DEVICE_ABIS="$("${ADB[@]}" shell getprop ro.product.cpu.abilist | tr -d '\r')"
printf '%s\n' "$DEVICE_API" | tee "$OUT/device_api.txt"
printf '%s\n' "$DEVICE_ABIS" | tee "$OUT/device_abis.txt"
grep -Eq "(^|,)${REQUIRED_ABI}(,|$)" "$OUT/device_abis.txt" || {
  echo "FAIL: connected device does not advertise ${REQUIRED_ABI}" >&2; exit 9
}
"${ADB[@]}" shell getprop ro.product.manufacturer | tee "$OUT/device_manufacturer.txt"
"${ADB[@]}" shell getprop ro.product.model | tee "$OUT/device_model.txt"

unzip -l "$APK" > "$OUT/apk_entries.txt"
if unzip -l "$APK" | grep -Eq 'lib/[^/]+/'; then
  unzip -l "$APK" | awk '/lib\/[[:alnum:]_-]+\// {print $4}' | sort -u > "$OUT/apk_native_libs.txt"
  grep -q "lib/${REQUIRED_ABI}/" "$OUT/apk_native_libs.txt" || {
    echo "FAIL: APK has native libraries but no ${REQUIRED_ABI} payload" >&2; exit 10
  }
else
  echo "bytecode_only=true" > "$OUT/apk_native_libs.txt"
fi

"${ADB[@]}" logcat -c
"${ADB[@]}" install -r "$APK" | tee "$OUT/install.txt"
"${ADB[@]}" shell pm path "$PACKAGE" | tee "$OUT/installed_path.txt"
grep -q '^package:' "$OUT/installed_path.txt" || {
  echo "FAIL: expected package was not installed: $PACKAGE" >&2; exit 11
}
"${ADB[@]}" shell dumpsys package "$PACKAGE" > "$OUT/package.txt"
grep -E 'versionCode=|versionName=|targetSdk=' "$OUT/package.txt" > "$OUT/package_identity.txt" || true
TARGET_SDK="$(grep -Eo 'targetSdk=[0-9]+' "$OUT/package.txt" | head -n1 | cut -d= -f2 || true)"
[[ "$TARGET_SDK" == "$REQUIRED_TARGET_SDK" ]] || {
  echo "FAIL: targetSdk=$TARGET_SDK; required $REQUIRED_TARGET_SDK" >&2; exit 12
}
grep -Eq 'versionCode=[0-9]+' "$OUT/package.txt" || {
  echo "FAIL: installed package has no readable versionCode" >&2; exit 13
}

"${ADB[@]}" shell am force-stop "$PACKAGE"
"${ADB[@]}" shell monkey -p "$PACKAGE" -c android.intent.category.LAUNCHER 1 | tee "$OUT/launch.txt"
sleep 5
"${ADB[@]}" exec-out screencap -p > "$OUT/01_boot.png"
"${ADB[@]}" shell uiautomator dump /sdcard/thf-fitness-boot.xml >/dev/null
"${ADB[@]}" pull /sdcard/thf-fitness-boot.xml "$OUT/01_boot_ui.xml" >/dev/null
"${ADB[@]}" shell rm -f /sdcard/thf-fitness-boot.xml
"${ADB[@]}" shell dumpsys window windows > "$OUT/window_boot.txt"
"${ADB[@]}" shell dumpsys activity activities > "$OUT/activity_boot.txt"
[[ -s "$OUT/01_boot.png" ]] || {
  echo "FAIL: boot screenshot is empty" >&2; exit 17
}
grep -q "$PACKAGE" "$OUT/window_boot.txt" || {
  echo "FAIL: Fitness is not the visible window after launch" >&2; exit 17
}

if [[ -n "$INSTRUMENTATION" ]]; then
  "${ADB[@]}" shell am instrument -w "$INSTRUMENTATION" | tee "$OUT/instrumentation.txt"
  grep -Eq 'OK \([0-9]+ test[s]?\)' "$OUT/instrumentation.txt" || {
    echo "FAIL: instrumentation did not report an OK result" >&2; exit 14
  }
fi

if (( MONKEY_EVENTS > 0 )); then
  "${ADB[@]}" shell monkey -p "$PACKAGE" --throttle 150 --pct-syskeys 0 "$MONKEY_EVENTS" \
    | tee "$OUT/monkey.txt"
  grep -q "Events injected: $MONKEY_EVENTS" "$OUT/monkey.txt" || {
    echo "FAIL: package-scoped UI smoke test did not complete" >&2; exit 15
  }
  "${ADB[@]}" exec-out screencap -p > "$OUT/02_after_ui_smoke.png"
  "${ADB[@]}" shell uiautomator dump /sdcard/thf-fitness-after-ui.xml >/dev/null
  "${ADB[@]}" pull /sdcard/thf-fitness-after-ui.xml "$OUT/02_after_ui_smoke.xml" >/dev/null
  "${ADB[@]}" shell rm -f /sdcard/thf-fitness-after-ui.xml
fi

"${ADB[@]}" shell input keyevent KEYCODE_HOME
sleep 2
"${ADB[@]}" shell monkey -p "$PACKAGE" -c android.intent.category.LAUNCHER 1 >/dev/null
sleep 3
"${ADB[@]}" exec-out screencap -p > "$OUT/03_resume.png"
"${ADB[@]}" shell dumpsys window windows > "$OUT/window_resume.txt"
[[ -s "$OUT/03_resume.png" ]] || {
  echo "FAIL: resume screenshot is empty" >&2; exit 18
}
grep -q "$PACKAGE" "$OUT/window_resume.txt" || {
  echo "FAIL: Fitness is not the visible window after resume" >&2; exit 18
}

echo "Interact with Fitness now; recording ${RECORD_SECONDS}s for motion/navigation evidence."
"${ADB[@]}" shell dumpsys gfxinfo "$PACKAGE" reset >/dev/null 2>&1 || true
"${ADB[@]}" shell screenrecord --time-limit "$RECORD_SECONDS" /sdcard/thf-fitness-qa.mp4 &
REC_PID=$!
wait "$REC_PID" || true
"${ADB[@]}" pull /sdcard/thf-fitness-qa.mp4 "$OUT/04_interaction.mp4" >/dev/null
"${ADB[@]}" shell rm -f /sdcard/thf-fitness-qa.mp4
[[ -s "$OUT/04_interaction.mp4" ]] || {
  echo "FAIL: motion/navigation screen recording is empty" >&2; exit 19
}
"${ADB[@]}" shell dumpsys gfxinfo "$PACKAGE" framestats > "$OUT/motion_framestats.txt" || true

"${ADB[@]}" shell pm list packages | grep -Ei 'healthconnect|healthdata' > "$OUT/health_connect_packages.txt" || true
"${ADB[@]}" shell dumpsys -l | grep -i health > "$OUT/health_connect_services.txt" || true
"${ADB[@]}" shell cmd package resolve-activity --brief \
  -a android.health.connect.action.HEALTH_HOME_SETTINGS \
  > "$OUT/health_connect_settings_activity.txt" 2>&1 || true
"${ADB[@]}" shell dumpsys package "$PACKAGE" \
  | sed -n '/runtime permissions:/,/^[^ ]/p' \
  > "$OUT/runtime_permissions.txt" || true
"${ADB[@]}" shell appops get "$PACKAGE" > "$OUT/appops.txt" 2>&1 || true

HEALTH_CONNECT_PRESENT=false
if [[ -s "$OUT/health_connect_packages.txt" || -s "$OUT/health_connect_services.txt" ]]; then
  HEALTH_CONNECT_PRESENT=true
fi
if $REQUIRE_HEALTH_CONNECT && ! $HEALTH_CONNECT_PRESENT; then
  echo "FAIL: Health Connect provider/service is unavailable on the connected phone" >&2
  exit 16
fi
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
echo "PASS_PACKAGE=$PACKAGE"
echo "PASS_TARGET_SDK=$TARGET_SDK"
echo "PASS_DEVICE_ABI=$REQUIRED_ABI"
echo "PASS_UI_SMOKE_EVENTS=$MONKEY_EVENTS"
echo "HEALTH_CONNECT_PROVIDER_PRESENT=$HEALTH_CONNECT_PRESENT"
echo "Evidence: $OUT"
echo "Manual acceptance still required for login, Health Connect grant/data flow, exercise anatomy/motion, and purchase/restore."
