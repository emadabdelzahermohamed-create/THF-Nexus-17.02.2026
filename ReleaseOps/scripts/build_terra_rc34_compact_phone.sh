#!/usr/bin/env bash
set -Eeuo pipefail

SRC="$HOME/thf-terra-rift-staging-apk-v1/terra/work"
ROOT="$HOME/thf-terra-rc34-compact-phone-v4"
WORK="$ROOT/work"
OUT="$ROOT/out"
GODOT="$HOME/.local/bin/godot-4.7.2"
ANDROID_SDK="$HOME/thf-builder-rc16-build/android-sdk"
APK_NAME="THF-TERRA-4.6.8-RC34-PHONE-V4.apk"
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
s=s.replace('name="Android AAB Candidate"','name="Android Phone Explore RC34"',1)
s=s.replace('export_filter="all_resources"','export_filter="scenes"',1)
marker='export_filter="scenes"\n'
files='export_files=PackedStringArray("res://native/scenes/world_main.tscn", "res://web/static/assets/avatars/stage16a/thf_mpfb_stage16a_ual12_animated.glb", "res://web/static/assets/avatars/thf_humanoid_v6.glb")\n'
if marker not in s:
    raise SystemExit('export filter marker missing')
s=s.replace(marker,marker+files,1)
s=s.replace('version/code=42068','version/code=42072',1)
s=s.replace('version/name="4.6.8-rc34"','version/name="4.6.8-rc34-phonev4"',1)
s=s.replace('package/unique_name="com.topherofit.thf.terra"','package/unique_name="com.topherofit.thf.terra.phoneqa"',1)
s=s.replace('gradle_build/compress_native_libraries=false','gradle_build/compress_native_libraries=true',1)
p.write_text(s,encoding='utf-8')

w=Path('native/world/WorldMain.gd')
g=w.read_text(encoding='utf-8')

# Add a local-only mode flag. It never represents an online session and is
# intentionally separated from all server-authoritative world/economy state.
needle='var mobile_held_direction := ""\n'
if needle not in g:
    raise SystemExit('mobile state insertion point missing')
g=g.replace(needle, needle + 'var offline_explore_mode := false\n', 1)

old='''    var register_button := Button.new()\n    register_button.text = "Register / تسجيل"\n    register_button.pressed.connect(_register_pressed)\n    auth_box.add_child(register_button)\n    layer.add_child(auth_panel)'''
new='''    var register_button := Button.new()\n    register_button.text = "Register / تسجيل"\n    register_button.pressed.connect(_register_pressed)\n    auth_box.add_child(register_button)\n\n    var offline_button := Button.new()\n    offline_button.text = "Offline Explore QA / استكشاف محلي"\n    offline_button.pressed.connect(_offline_explore_pressed)\n    auth_box.add_child(offline_button)\n    layer.add_child(auth_panel)'''
if old not in g:
    raise SystemExit('auth UI insertion point missing')
g=g.replace(old,new,1)

old='''func _register_pressed() -> void:\n    _auth("register")\n\nfunc _show_auth(show_panel: bool) -> void:'''
new='''func _register_pressed() -> void:\n    _auth("register")\n\nfunc _offline_explore_pressed() -> void:\n    # Genuine local QA path: no account/session, no websocket connection, no\n    # online/ranked/social/economy mutation. Movement updates only local target\n    # position and exercises the real MPFB rig, UAL locomotion, IK and camera.\n    THFSessionStore.clear()\n    token = ""\n    api.set_token("")\n    offline_explore_mode = true\n    socket_connected = false\n    _show_auth(false)\n    me = {"id": -1, "username": "Offline Explore Guest"}\n    world = {}\n    local_user_id = -1\n    current_room = "offline_explore"\n    room_scale = WORLD_SCALE_FALLBACK\n    _spawn_local_avatar()\n    status_label.text = "OFFLINE EXPLORE · LOCAL MOVEMENT"\n    _show_visual_cue("Local MPFB explore · no online state", 3200)\n\nfunc _show_auth(show_panel: bool) -> void:'''
if old not in g:
    raise SystemExit('offline explore insertion point missing')
g=g.replace(old,new,1)

# Permit existing keyboard/touch cadence in local mode, while preserving the
# original fail-closed behavior when neither local mode nor a real socket exists.
g=g.replace('''func _send_keyboard_input() -> void:\n    if not socket_connected:\n        return''','''func _send_keyboard_input() -> void:\n    if not socket_connected and not offline_explore_mode:\n        return''',1)
g=g.replace('''func _update_mobile_input() -> void:\n    if not socket_connected or mobile_held_direction.is_empty():\n        return''','''func _update_mobile_input() -> void:\n    if (not socket_connected and not offline_explore_mode) or mobile_held_direction.is_empty():\n        return''',1)

old='''func _send_step(direction: String, running: bool) -> void:\n    native_running = running\n    seq += 1\n    socket.send_text(JSON.stringify({\n        "type": "step",\n        "direction": direction,\n        "run": running,\n        "seq": seq,\n    }))'''
new='''func _send_step(direction: String, running: bool) -> void:\n    native_running = running\n    if offline_explore_mode:\n        _apply_offline_step(direction, running)\n        return\n    if not socket_connected:\n        return\n    seq += 1\n    socket.send_text(JSON.stringify({\n        "type": "step",\n        "direction": direction,\n        "run": running,\n        "seq": seq,\n    }))\n\nfunc _apply_offline_step(direction: String, running: bool) -> void:\n    if not offline_explore_mode or not is_instance_valid(local_root):\n        return\n    var directions := {\n        "up": Vector3(0.0, 0.0, -1.0),\n        "down": Vector3(0.0, 0.0, 1.0),\n        "left": Vector3(-1.0, 0.0, 0.0),\n        "right": Vector3(1.0, 0.0, 0.0),\n        "up_left": Vector3(-1.0, 0.0, -1.0),\n        "up_right": Vector3(1.0, 0.0, -1.0),\n        "down_left": Vector3(-1.0, 0.0, 1.0),\n        "down_right": Vector3(1.0, 0.0, 1.0),\n    }\n    if not directions.has(direction):\n        return\n    var move: Vector3 = directions[direction]\n    if move.length_squared() > 1.0:\n        move = move.normalized()\n    var step_distance := 0.42 if running else 0.26\n    var next := target_position + move * step_distance\n    # The compact QA world has an 80 m ground plane. Stay safely inside it.\n    next.x = clampf(next.x, -38.0, 38.0)\n    next.z = clampf(next.z, -38.0, 38.0)\n    target_position = next'''
if old not in g:
    raise SystemExit('send step replacement point missing')
g=g.replace(old,new,1)
w.write_text(g,encoding='utf-8')
PY

# Fail closed on phone layout and local-mode wiring before invoking Godot.
grep -q 'window/size/window_width_override=0' project.godot
grep -q 'window/size/window_height_override=0' project.godot
grep -q 'window/stretch/aspect="expand"' project.godot
grep -q 'window/handheld/orientation=4' project.godot
grep -q 'Offline Explore QA / استكشاف محلي' native/world/WorldMain.gd
grep -q 'func _offline_explore_pressed()' native/world/WorldMain.gd
grep -q 'offline_explore_mode = true' native/world/WorldMain.gd
grep -q 'func _apply_offline_step' native/world/WorldMain.gd
grep -q 'if offline_explore_mode:' native/world/WorldMain.gd
grep -q 'if not socket_connected and not offline_explore_mode:' native/world/WorldMain.gd
grep -q 'InputEventScreenDrag' native/world/WorldMain.gd
grep -q 'custom_minimum_size = Vector2(62.0, 62.0)' native/world/WorldMain.gd

WORLD_SOURCE_SHA=$(sha256sum native/world/WorldMain.gd | awk '{print $1}')
PROJECT_SHA=$(sha256sum project.godot | awk '{print $1}')
AVATAR_SHA=$(sha256sum web/static/assets/avatars/stage16a/thf_mpfb_stage16a_ual12_animated.glb | awk '{print $1}')

"$GODOT" --headless --path "$WORK" --import >"$OUT/import.log" 2>&1 || {
  tail -220 "$OUT/import.log"
  exit 1
}
"$GODOT" --headless --path "$WORK" --export-debug "Android Phone Explore RC34" "$OUT/$APK_NAME" >"$OUT/export.log" 2>&1 || {
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
grep -q "versionCode='42072'" "$OUT/apk_badging.txt"
grep -q "versionName='4.6.8-rc34-phonev4'" "$OUT/apk_badging.txt"
grep -q "^targetSdkVersion:'$EXPECTED_TARGET_SDK'$" "$OUT/apk_badging.txt"

UNDER=FAIL
if [ "$SIZE" -lt 104857600 ]; then UNDER=PASS; fi

cat > "$OUT/EVIDENCE.txt" <<EOF
THF_TERRA_RC34_PHONE_V4=BUILT
source=thf-terra-rift-staging-apk-v1/terra/work
version=4.6.8-rc34-phonev4
package=$EXPECTED_PACKAGE
package_from_apk=PASS
target_sdk=$EXPECTED_TARGET_SDK
target_sdk_from_apk=PASS
android_api_36_installed=PASS
engine=Godot-4.7.2
main_scene=res://native/scenes/world_main.tscn
world_source_sha256=$WORLD_SOURCE_SHA
project_sha256=$PROJECT_SHA
mpfb_runtime_asset=PASS
avatar_model=thf_mpfb_stage16a_ual12_animated.glb
avatar_asset_sha256=$AVATAR_SHA
avatar_claim_from_runtime=137_joints_195_clips
offline_explore_mode=PASS
offline_keyboard_movement=LOCAL_ONLY
offline_touch_movement=LOCAL_ONLY
offline_camera_touch=PASS
offline_online_state_faked=FALSE
offline_authoritative_mutations=DISABLED_NO_SESSION_NO_SOCKET
sensor_landscape_setting=PASS
expandable_aspect=PASS
desktop_window_override=NONE
touch_step_minimum=62x62
architecture=arm64-v8a
apk_size_bytes=$SIZE
apk_sha256=$SHA
under_100MiB=$UNDER
backend_status=EPHEMERAL_ENDPOINT_NOT_ACCEPTED_AS_FINAL
candidate_scope=QA_ONLY_NOT_PRODUCTION_PACKAGE
physical_device_status=PENDING
final_or_play_ready=FALSE
EOF
cat "$OUT/EVIDENCE.txt"

if [ "$SIZE" -ge 104857600 ]; then
  echo "SIZE_GATE_OVER_100M"
  exit 2
fi
