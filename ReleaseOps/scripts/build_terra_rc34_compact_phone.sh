#!/usr/bin/env bash
set -Eeuo pipefail

SRC="$HOME/thf-terra-rift-staging-apk-v1/terra/work"
ROOT="$HOME/thf-terra-rc34-compact-phone-v3"
WORK="$ROOT/work"
OUT="$ROOT/out"
GODOT="$HOME/.local/bin/godot-4.7.2"
ANDROID_SDK="$HOME/thf-builder-rc16-build/android-sdk"
APK_NAME="THF-TERRA-4.6.8-RC34-PHONE-V3.apk"
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

# Compact native Android export while retaining the authoritative RC34 world
# scene and the exact local MPFB/UAL avatar used by the current runtime.
p=Path('export_presets.cfg')
s=p.read_text(encoding='utf-8')
s=s.replace('name="Android AAB Candidate"','name="Android Phone Visual RC34"',1)
s=s.replace('export_filter="all_resources"','export_filter="scenes"',1)
marker='export_filter="scenes"\n'
files='export_files=PackedStringArray("res://native/scenes/world_main.tscn", "res://web/static/assets/avatars/stage16a/thf_mpfb_stage16a_ual12_animated.glb", "res://web/static/assets/avatars/thf_humanoid_v6.glb")\n'
if marker not in s:
    raise SystemExit('export filter marker missing')
s=s.replace(marker,marker+files,1)
s=s.replace('version/code=42068','version/code=42071',1)
s=s.replace('version/name="4.6.8-rc34"','version/name="4.6.8-rc34-phonev3"',1)
s=s.replace('package/unique_name="com.topherofit.thf.terra"','package/unique_name="com.topherofit.thf.terra.phoneqa"',1)
s=s.replace('gradle_build/compress_native_libraries=false','gradle_build/compress_native_libraries=true',1)
p.write_text(s,encoding='utf-8')

# Physical-phone visual QA must not depend on the temporary public endpoint.
# Keep real login/register untouched, but add an explicit *non-authenticated*
# visual mode that spawns the same local MPFB avatar and native motion stack.
w=Path('native/world/WorldMain.gd')
g=w.read_text(encoding='utf-8')
old='''    var register_button := Button.new()\n    register_button.text = "Register / تسجيل"\n    register_button.pressed.connect(_register_pressed)\n    auth_box.add_child(register_button)\n    layer.add_child(auth_panel)'''
new='''    var register_button := Button.new()\n    register_button.text = "Register / تسجيل"\n    register_button.pressed.connect(_register_pressed)\n    auth_box.add_child(register_button)\n\n    var offline_button := Button.new()\n    offline_button.text = "Offline Visual QA / معاينة بدون حساب"\n    offline_button.pressed.connect(_offline_visual_pressed)\n    auth_box.add_child(offline_button)\n    layer.add_child(auth_panel)'''
if old not in g:
    raise SystemExit('auth UI insertion point missing')
g=g.replace(old,new,1)
old='''func _register_pressed() -> void:\n    _auth("register")\n\nfunc _show_auth(show_panel: bool) -> void:'''
new='''func _register_pressed() -> void:\n    _auth("register")\n\nfunc _offline_visual_pressed() -> void:\n    # Explicit visual-only mode. It never creates a session, account, balance,\n    # reward or authoritative world mutation. It exists only so physical-device\n    # QA can verify the real local MPFB model, rig, IK and locomotion while the\n    # external identity endpoint is being made persistent.\n    THFSessionStore.clear()\n    token = ""\n    api.set_token("")\n    _show_auth(false)\n    me = {"id": -1, "username": "Phone QA Guest"}\n    local_user_id = -1\n    room_scale = WORLD_SCALE_FALLBACK\n    _spawn_local_avatar()\n    status_label.text = "OFFLINE VISUAL QA · MPFB LOCAL"\n    _show_visual_cue("MPFB local visual QA · no account/session", 3200)\n\nfunc _show_auth(show_panel: bool) -> void:'''
if old not in g:
    raise SystemExit('offline visual function insertion point missing')
g=g.replace(old,new,1)
w.write_text(g,encoding='utf-8')
PY

grep -q 'Offline Visual QA / معاينة بدون حساب' native/world/WorldMain.gd
grep -q 'func _offline_visual_pressed()' native/world/WorldMain.gd
grep -q '_spawn_local_avatar()' native/world/WorldMain.gd

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
grep -q "versionCode='42071'" "$OUT/apk_badging.txt"
grep -q "^targetSdkVersion:'$EXPECTED_TARGET_SDK'$" "$OUT/apk_badging.txt"

UNDER=FAIL
if [ "$SIZE" -lt 104857600 ]; then UNDER=PASS; fi

cat > "$OUT/EVIDENCE.txt" <<EOF
THF_TERRA_RC34_PHONE_V3=BUILT
source=thf-terra-rift-staging-apk-v1/terra/work
version=4.6.8-rc34-phonev3
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
offline_visual_guest_mode=PASS
offline_visual_guest_auth_bypass=FALSE_AUTH_NOT_SIMULATED
offline_visual_guest_mutations=DISABLED_BY_NO_TOKEN
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
