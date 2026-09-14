#!/usr/bin/env bash
set -Eeuo pipefail

SRC="$HOME/thf-builder/inputs-rc17/THF_Core_RC6_ANDROID_NATIVE_I18N_RELEASE_CUMULATIVE_SOURCE.zip"
EXPECTED="6dab85e19f17e9d9c712cc1e588759bf826aa2ddd291fa361bbadaee014a045a"
ROOT="$HOME/thf-core-phone-ui1-local"
APP="$ROOT/app"
OUT="$ROOT/out"
RC16="$HOME/thf-builder-rc16-build"
SDK="$RC16/android-sdk"
CACHE="$RC16/cache"
APK_NAME="THF-CORE-RC6-PHONE-UI1-LOCAL-QA.apk"

rm -rf "$ROOT"
mkdir -p "$APP" "$OUT"
echo "$EXPECTED  $SRC" | sha256sum -c -
unzip -q "$SRC" -d "$APP"
cd "$APP"

mkdir -p android/app/src/main/assets/web
cp -a clients/web/. android/app/src/main/assets/web/

python3 - <<'PY'
from pathlib import Path

idx=Path('android/app/src/main/assets/web/index.html')
s=idx.read_text(encoding='utf-8')
for a,b in {
    'href="/styles.css"':'href="styles.css"',
    'src="/core-i18n.js"':'src="core-i18n.js"',
    'src="/world3d.js"':'src="world3d.js"',
    'src="/app.js"':'src="app.js"',
    'href="/admin.html"':'href="admin.html"',
}.items():
    s=s.replace(a,b)
idx.write_text(s,encoding='utf-8')

gradle=Path('android/app/build.gradle')
g=gradle.read_text(encoding='utf-8')
g=g.replace('versionCode 62200','versionCode 62203',1)
g=g.replace("versionName '6.2.2-rc6'","versionName '6.2.2-rc6-phoneui1'",1)
gradle.write_text(g,encoding='utf-8')

java=Path('android/app/src/main/java/com/topherofit/thf/core/MainActivity.java')
j=java.read_text(encoding='utf-8')
old='s.setJavaScriptEnabled(true); s.setDomStorageEnabled(true); s.setAllowFileAccess(false); s.setAllowContentAccess(false);'
new='s.setJavaScriptEnabled(true); s.setDomStorageEnabled(true); s.setAllowFileAccess(true); s.setAllowContentAccess(false); s.setAllowFileAccessFromFileURLs(true); s.setAllowUniversalAccessFromFileURLs(false);'
if old not in j:
    raise SystemExit('expected WebSettings line not found')
j=j.replace(old,new,1)
old='''                if ("topherofit".equals(scheme)) { handleDeepLink(u); return true; }
                return !"https".equals(scheme);'''
new='''                if ("topherofit".equals(scheme)) { handleDeepLink(u); return true; }
                if ("file".equals(scheme)) return !u.toString().startsWith("file:///android_asset/web/");
                return !"https".equals(scheme);'''
if old not in j:
    raise SystemExit('expected URL policy block not found')
j=j.replace(old,new,1)
old='''    private void loadProduct() {
        String base=BuildConfig.THF_BASE_URL==null?"":BuildConfig.THF_BASE_URL.trim();
        if (!isSafeHttps(base)) { showConfigError(getString(R.string.config_base_missing)); return; }
        if (!isOnline()) { showOffline(); return; }
        loadUrl(base);
    }'''
new='''    private void loadProduct() {
        // Physical PHONE-UI QA: render the real bundled Core UI even without a backend.
        loadUrl("file:///android_asset/web/index.html");
    }'''
if old not in j:
    raise SystemExit('expected loadProduct block not found')
j=j.replace(old,new,1)
java.write_text(j,encoding='utf-8')
PY

test -s android/app/src/main/assets/web/index.html
test -s android/app/src/main/assets/web/styles.css
test -s android/app/src/main/assets/web/app.js
test -s android/app/src/main/assets/web/core-i18n.js
test -s android/app/src/main/assets/web/world3d.js
! grep -q 'src="/app.js"' android/app/src/main/assets/web/index.html
! grep -q 'href="/styles.css"' android/app/src/main/assets/web/index.html
grep -q 'file:///android_asset/web/index.html' android/app/src/main/java/com/topherofit/thf/core/MainActivity.java

export ANDROID_SDK_ROOT="$SDK" ANDROID_HOME="$SDK" GRADLE_USER_HOME="$ROOT/gradle-home"
export PATH="$SDK/platform-tools:$SDK/build-tools/36.0.0:$SDK/cmdline-tools/latest/bin:$PATH"
mkdir -p "$GRADLE_USER_HOME"
GVER=8.11.1
GDIST="$CACHE/gradle-${GVER}-bin.zip"
GBIN="$CACHE/gradle-dist-${GVER}/gradle-${GVER}/bin/gradle"
test -x "$GBIN"
echo "f397b287023acdba1e9f6fc5ea72d22dd63669d59ed4a289a29b1a76eee151c6  $GDIST" | sha256sum -c -

cd android
"$GBIN" --no-daemon wrapper --gradle-version "$GVER" --distribution-type bin >/dev/null
chmod +x gradlew
./gradlew --no-daemon --stacktrace clean :app:assembleDebug >"$OUT/gradle.log" 2>&1
cp app/build/outputs/apk/debug/app-debug.apk "$OUT/$APK_NAME"

AAPT2="$SDK/build-tools/36.0.0/aapt2"
APKSIGNER="$SDK/build-tools/36.0.0/apksigner"
APK="$OUT/$APK_NAME"
"$AAPT2" dump badging "$APK" > "$OUT/badging.txt"
"$APKSIGNER" verify --verbose --print-certs "$APK" > "$OUT/apksigner.txt"
grep -q "package: name='com.topherofit.thf.core.debug'" "$OUT/badging.txt"
grep -q "versionCode='62203'" "$OUT/badging.txt"
grep -q "targetSdkVersion:'36'" "$OUT/badging.txt"
grep -q 'CN=Android Debug' "$OUT/apksigner.txt"

# Avoid SIGPIPE false failures under `set -o pipefail`: materialize inspection
# output first, then run grep against regular files.
zipinfo -1 "$APK" > "$OUT/apk_entries.txt"
for f in index.html styles.css app.js core-i18n.js world3d.js; do
  grep -Fxq "assets/web/$f" "$OUT/apk_entries.txt"
done
unzip -p "$APK" assets/web/index.html > "$OUT/bundled_index.html"
grep -q 'THF CORE' "$OUT/bundled_index.html"
grep -q 'href="styles.css"' "$OUT/bundled_index.html"

SHA=$(sha256sum "$APK" | awk '{print $1}')
SIZE=$(stat -c %s "$APK")
cat > "$OUT/EVIDENCE.txt" <<EOF
THF_CORE_PHONE_UI1=PASS
purpose=physical_phone_design_compatibility_qa
source_sha256=$EXPECTED
package=com.topherofit.thf.core.debug
versionCode=62203
versionName=6.2.2-rc6-phoneui1-debug
targetSdk=36
bundled_real_core_ui=PASS
bundled_i18n=PASS
bundled_world3d=PASS
temporary_external_endpoint_required=false
backend_dependent_features=NOT_ACCEPTED_IN_THIS_CANDIDATE
apk_sha256=$SHA
apk_size_bytes=$SIZE
production_signing=false
play_upload=false
EOF
cat "$OUT/EVIDENCE.txt"
