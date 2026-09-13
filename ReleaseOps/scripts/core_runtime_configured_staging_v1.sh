#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$HOME/thf-core-rc6-runtime-configured-v1"
SRC="$HOME/thf-builder/inputs-rc17/THF_Core_RC6_ANDROID_NATIVE_I18N_RELEASE_CUMULATIVE_SOURCE.zip"
EXPECTED="6dab85e19f17e9d9c712cc1e588759bf826aa2ddd291fa361bbadaee014a045a"
SDK="$HOME/thf-builder-rc16-build/android-sdk"
CACHE="$HOME/thf-builder-rc16-build/cache"
RUNTIME="$HOME/thf-runtime-s1/runtime/THF_NEXUS_6_FINAL"
WORK="$ROOT/work"
OUT="$ROOT/out"

rm -rf "$WORK" "$OUT"
mkdir -p "$WORK" "$OUT" "$ROOT/gradle-home"
test -f "$SRC"
test "$(sha256sum "$SRC" | awk '{print $1}')" = "$EXPECTED"

python3 - <<'PY'
import json, urllib.request
d=json.load(urllib.request.urlopen('http://127.0.0.1:18080/health',timeout=5))
assert d.get('ok') is True
print('LOCAL_RUNTIME_HEALTH=PASS')
PY

CF="$HOME/bin/cloudflared"
test -x "$CF"
PUB=""
[ -f "$RUNTIME/runtime/public-url.txt" ] && PUB="$(cat "$RUNTIME/runtime/public-url.txt" 2>/dev/null || true)"
check_pub() {
  python3 - "$1" <<'PY'
import json, sys, urllib.request
u=sys.argv[1]
if not u.startswith('https://'):
    raise SystemExit(2)
d=json.load(urllib.request.urlopen(u.rstrip('/')+'/health',timeout=6))
assert d.get('ok') is True
PY
}

if [ -z "$PUB" ] || ! check_pub "$PUB" >/dev/null 2>&1; then
  mkdir -p "$RUNTIME/runtime/pids" "$RUNTIME/runtime/logs"
  if [ -f "$RUNTIME/runtime/pids/cloudflared-quick.pid" ]; then
    old="$(cat "$RUNTIME/runtime/pids/cloudflared-quick.pid" || true)"
    [[ "$old" =~ ^[0-9]+$ ]] && kill "$old" 2>/dev/null || true
  fi
  : > "$RUNTIME/runtime/logs/cloudflared-quick.log"
  nohup "$CF" tunnel --no-autoupdate --url http://127.0.0.1:18080 >"$RUNTIME/runtime/logs/cloudflared-quick.log" 2>&1 &
  cpid=$!
  echo "$cpid" > "$RUNTIME/runtime/pids/cloudflared-quick.pid"
  PUB=""
  for _ in $(seq 1 50); do
    PUB="$(grep -Eo 'https://[a-z0-9-]+\.trycloudflare\.com' "$RUNTIME/runtime/logs/cloudflared-quick.log" | head -1 || true)"
    [ -n "$PUB" ] && break
    sleep .5
  done
  test -n "$PUB"
  check_pub "$PUB"
  printf '%s\n' "$PUB" > "$RUNTIME/runtime/public-url.txt"
  chmod 600 "$RUNTIME/runtime/public-url.txt"
else
  check_pub "$PUB"
fi

echo HTTPS_STAGING_ENDPOINT_HEALTH=PASS
unzip -q "$SRC" -d "$WORK"
PROJ="$WORK/android"
test -f "$PROJ/app/build.gradle"
export ANDROID_HOME="$SDK" ANDROID_SDK_ROOT="$SDK" GRADLE_USER_HOME="$ROOT/gradle-home"
printf 'sdk.dir=%s\n' "$SDK" > "$PROJ/local.properties"
unset THF_KEYSTORE_PATH THF_KEY_ALIAS THF_KEYSTORE_PASSWORD THF_KEY_PASSWORD
DIST="$CACHE/gradle-dist-8.11.1/gradle-8.11.1/bin/gradle"
test -x "$DIST"
cd "$PROJ"
"$DIST" --no-daemon wrapper --gradle-version 8.11.1 --distribution-type bin >/dev/null
chmod +x gradlew
./gradlew --no-daemon --stacktrace -PTHF_BASE_URL="$PUB" -PTHF_PASS_URL="$PUB" :app:assembleRelease

APK="$(find app/build/outputs/apk -type f -name '*.apk' | head -1)"
test -n "$APK"
BT="$(find "$SDK/build-tools" -mindepth 1 -maxdepth 1 -type d | sort -V | tail -1)"
AAPT="$BT/aapt"
APKSIGNER="$BT/apksigner"
ZIPALIGN="$BT/zipalign"
TMP="$OUT/aligned-unsigned.apk"
"$ZIPALIGN" -f -p 4 "$APK" "$TMP"
KS="$ROOT/qa-debug.keystore"
if [ ! -f "$KS" ]; then
  keytool -genkeypair -noprompt -keystore "$KS" -storepass android -alias androiddebugkey -keypass android \
    -dname 'CN=Android Debug,O=THF Runtime QA,C=US' -keyalg RSA -keysize 2048 -validity 3650 >/dev/null 2>&1
fi
FINAL="$OUT/THF-Core-RC6-RUNTIME-CONFIGURED-STAGING.apk"
"$APKSIGNER" sign --ks "$KS" --ks-key-alias androiddebugkey --ks-pass pass:android --key-pass pass:android --out "$FINAL" "$TMP"
"$APKSIGNER" verify --verbose "$FINAL" >"$OUT/apksigner.txt" 2>&1
"$ZIPALIGN" -c -p 4 "$FINAL"
BADGING="$($AAPT dump badging "$FINAL")"
printf '%s\n' "$BADGING" > "$OUT/badging.txt"
grep -q "package: name='com.topherofit.thf.core'" <<<"$BADGING"
grep -q "targetSdkVersion:'36'" <<<"$BADGING"
unzip -p "$FINAL" classes.dex | strings | grep -F "$PUB" >/dev/null
APK_SHA="$(sha256sum "$FINAL" | awk '{print $1}')"
test "$(sha256sum "$SRC" | awk '{print $1}')" = "$EXPECTED"
printf 'status=PASS\ncanonical_sha256=%s\napk_sha256=%s\nservice_url_embedded=true\nservice_url_scheme=https\nservice_health=PASS\nendpoint_class=cloudflare_quick_staging\npackage=com.topherofit.thf.core\ntarget_sdk=36\nproduction_signing=false\nproduction_cutover=false\ncanonical_archive_mutated=false\nwave_untouched=true\n' "$EXPECTED" "$APK_SHA" | tee "$OUT/TRUTH.txt"
