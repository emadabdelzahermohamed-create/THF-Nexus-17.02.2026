#!/usr/bin/env bash
set -euo pipefail

APK="${GITHUB_WORKSPACE}/build/fitness/android/app/build/outputs/apk/debug/app-debug.apk"
PKG="com.topherofit.thf.pulse.debug"
ACTIVITY="com.topherofit.thf.pulse.MainActivity"
OUT="${GITHUB_WORKSPACE}/artifacts/emulator"
mkdir -p "$OUT"

test -f "$APK"
adb wait-for-device
adb install -r "$APK"
adb shell am force-stop "$PKG" || true
adb logcat -c

# Exercise RTL/localization path on the emulator.
adb shell settings put system system_locales ar-EG || true
adb shell am start -W -n "$PKG/$ACTIVITY" | tee "$OUT/am-start.txt"
sleep 10

adb shell pidof "$PKG" | tee "$OUT/pid.txt"
adb shell dumpsys activity activities | grep -E 'mResumedActivity|topResumedActivity' | tee "$OUT/resumed-activity.txt" || true

adb shell uiautomator dump /sdcard/thf-window.xml >/dev/null 2>&1 || true
adb pull /sdcard/thf-window.xml "$OUT/window.xml" >/dev/null 2>&1 || true
adb exec-out screencap -p > "$OUT/screenshot.png"
adb logcat -d -v threadtime > "$OUT/logcat.txt"

if grep -nE 'FATAL EXCEPTION|AndroidRuntime: Process: com\.topherofit\.thf\.pulse\.debug' "$OUT/logcat.txt"; then
  echo "Android runtime crash detected" >&2
  exit 1
fi

if [[ -f "$OUT/window.xml" ]]; then
  grep -E 'THF|Pulse|تسجيل|اللياقة|تمرين|خطط|التمارين|اليوم' "$OUT/window.xml" > "$OUT/ui-evidence.txt" || true
fi

cat > "$OUT/RESULT.txt" <<EOF
package=$PKG
activity=$ACTIVITY
base_url=https://thf-fitness-pulse-ul26f1.v2.appdeploy.ai/
locale_test=ar-EG
install=PASS
launch=PASS
no_fatal_crash=PASS
ui_dump=$([[ -s "$OUT/window.xml" ]] && echo PASS || echo WARN)
screenshot=$([[ -s "$OUT/screenshot.png" ]] && echo PASS || echo FAIL)
EOF

test -s "$OUT/screenshot.png"
