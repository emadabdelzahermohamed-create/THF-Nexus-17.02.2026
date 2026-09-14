#!/usr/bin/env bash
set -Eeuo pipefail

SRC="$HOME/thf-terra-rift-staging-apk-v1/terra/work"
ROOT="$HOME/thf-terra-rc34-compact-phone-v2"
WORK="$ROOT/work"
OUT="$ROOT/out"
GODOT="$HOME/.local/bin/godot-4.7.2"
ANDROID_SDK="$HOME/thf-builder-rc16-build/android-sdk"
APK_NAME="THF-TERRA-4.6.8-RC34-PHONE-V2.apk"
EXPECTED_PACKAGE="com.topherofit.thf.terra.phoneqa"
EXPECTED_TARGET_SDK="36"

rm -rf "$ROOT"
mkdir -p "$ROOT" "$OUT"
cp -a "$SRC" "$WORK"
cd "$WORK"

JAVA_BIN=$(readlink -f "$(command -v java)")
JAVA_HOME_DETECTED=$(dirname "$(dirname "$JAVA_BIN")")
test -x "$ANDROID_SDK/platform-tools/adb"
test -d "$ANDROID_SDK/build-tools"
test -d "$ANDROID_SDK/platforms/android-$EXPECTED_TARGET_SDK"
test -x "$JAVA_HOME_DETECTED/bin/java"

BUILD_TOOLS_DIR=$(find "$ANDROID_SDK/build-tools" -mindepth 1 -maxdepth 1 -type d | sort -V | tail -n 1)
AAPT="$BUILD_TOOLS_DIR/aapt"
test -x "$AAPT"

# Godot stores Android toolchain paths in per-user editor settings. Use an
# isolated config root so this QA build cannot change the builder's shared UI
# settings or interfere with other THF jobs.
export XDG_CONFIG_HOME="$ROOT/config"
mkdir -p "$XDG_CONFIG_HOME/godot"
cat > "$XDG_CONFIG_HOME/godot/editor_settings-4.7.tres" <<EOF
[gd_resource type="EditorSettings" format=3]

[resource]
export/android/android_sdk_path = "$ANDROID_SDK"
export/android/java_sdk_path = "$JAVA_HOME_DETECTED"
EOF
export ANDROID_HOME="$ANDROID_SDK"
export ANDROID_SDK_ROOT="$ANDROID_SDK"
export JAVA_HOME="$JAVA_HOME_DETECTED"
export PATH="$JAVA_HOME/bin:$ANDROID_SDK/platform-tools:$PATH"

python3 - <<'PY'
from pathlib import Path
p=Path('export_presets.cfg')
s=p.read_text(encoding='utf-8')
s=s.replace('name="Android AAB Candidate"','name="Android Phone Visual RC34"',1)
s=s.replace('export_filter="all_resources"','export_filter="scenes"',1)
marker='export_filter="scenes"\n'
files='export_files=PackedStringArray("res://native/scenes/world_main.tscn", "res://web/static/assets/avatars/stage16a/thf_mpfb_stage16a_ual12_animated.glb", "res://web/static/assets/avatars/thf_humanoid_v6.glb")\n'
if marker not in s:
    raise SystemExit('export filter marker missing')
s=s.replace(marker,marker+files,1)
s=s.replace('version/code=42068','version/code=42070',1)
s=s.replace('version/name="4.6.8-rc34"','version/name="4.6.8-rc34-phonev2"',1)
s=s.replace('package/unique_name="com.topherofit.thf.terra"','package/unique_name="com.topherofit.thf.terra.phoneqa"',1)
s=s.replace('gradle_build/compress_native_libraries=false','gradle_build/compress_native_libraries=true',1)
p.write_text(s,encoding='utf-8')
PY

"$GODOT" --headless --path "$WORK" --import >"$OUT/import.log" 2>&1 || {
  tail -220 "$OUT/import.log"
  exit 1
}
"$GODOT" --headless --path "$WORK" --export-debug "Android Phone Visual RC34" "$OUT/$APK_NAME" >"$OUT/export.log" 2>&1 || {
  tail -260 "$OUT/export.log"
  exit 1
}

APK="$OUT/$APK_NAME"
test -s "$APK"
SIZE=$(stat -c %s "$APK")
SHA=$(sha256sum "$APK" | awk '{print $1}')
unzip -l "$APK" > "$OUT/apk_entries.txt"
grep -q 'thf_mpfb_stage16a_ual12_animated' "$OUT/apk_entries.txt"
grep -q 'world_main' "$OUT/apk_entries.txt"
grep -q 'lib/arm64-v8a/libgodot_android.so' "$OUT/apk_entries.txt"

"$AAPT" dump badging "$APK" > "$OUT/apk_badging.txt"
grep -q "^package: name='$EXPECTED_PACKAGE'" "$OUT/apk_badging.txt"
grep -q "^targetSdkVersion:'$EXPECTED_TARGET_SDK'$" "$OUT/apk_badging.txt"

UNDER=FAIL
if [ "$SIZE" -lt 104857600 ]; then UNDER=PASS; fi

cat > "$OUT/EVIDENCE.txt" <<EOF
THF_TERRA_RC34_PHONE_V2=BUILT
source=thf-terra-rift-staging-apk-v1/terra/work
version=4.6.8-rc34-phonev2
package=$EXPECTED_PACKAGE
package_from_apk=PASS
target_sdk=$EXPECTED_TARGET_SDK
target_sdk_from_apk=PASS
android_api_36_installed=PASS
engine=Godot-4.7.2
main_scene=res://native/scenes/world_main.tscn
mpfb_runtime_asset=PASS
avatar_model=thf_mpfb_stage16a_ual12_animated.glb
avatar_claim_from_runtime=137_joints_195_clips
architecture=arm64-v8a
apk_size_bytes=$SIZE
apk_sha256=$SHA
under_100MiB=$UNDER
backend_status=EPHEMERAL_ENDPOINT_NOT_ACCEPTED_AS_FINAL
physical_device_status=PENDING
final_or_play_ready=FALSE
EOF
cat "$OUT/EVIDENCE.txt"

if [ "$SIZE" -ge 104857600 ]; then
  echo "SIZE_GATE_OVER_100M"
  exit 2
fi
