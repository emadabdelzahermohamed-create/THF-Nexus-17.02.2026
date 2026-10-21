#!/usr/bin/env bash
set -Eeuo pipefail
DST="${RUINSCIV_CANDIDATE:-$HOME/ruinsciv-candidate}"
OUT="${RUINSCIV_BUILD_OUT:-$HOME/ruinsciv-build-evidence-v6}"
APK="$OUT/RuinsCiv-v6-arm64.apk"
PACKAGE=com.topherofit.ruins.civ
GODOT_VERSION=4.7.2
GODOT_TAG=4.7.2-stable
TOOLS="$HOME/.cache/thf-godot-$GODOT_VERSION"
TEMPLATES="$HOME/.local/share/godot/export_templates/$GODOT_VERSION.stable"
mkdir -p "$OUT" "$TOOLS"
exec > >(tee "$OUT/build_trace.log") 2>&1
trap 'rc=$?; printf "RUINSCIV_V6_FAIL rc=%s line=%s command=%q\n" "$rc" "$LINENO" "$BASH_COMMAND" | tee "$OUT/build_failure.txt"; exit "$rc"' ERR
[[ -f "$DST/project.godot" ]]
[[ -f "$DST/export_presets.cfg" ]]
sed -Ei 's#^(package/unique_name|package/name)="[^"]*"#\1="'"$PACKAGE"'"#' "$DST/export_presets.cfg"
# RC35 product repair: explicit always-visible mobile movement + camera controls.
# Install as an autoload so Offline Explore receives controls without coupling to a scene path.
cat > "$DST/RuinsCivMobileControls.gd" <<'GDSCRIPT'
extends CanvasLayer

var held := {}

func _ready():
    layer = 100
    var root := Control.new()
    root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    root.mouse_filter = Control.MOUSE_FILTER_IGNORE
    add_child(root)
    _button(root, "▲", Vector2(92, -202), "move_forward")
    _button(root, "▼", Vector2(92, -92), "move_backward")
    _button(root, "◀", Vector2(18, -147), "move_left")
    _button(root, "▶", Vector2(166, -147), "move_right")
    _button(root, "CAM ◀", Vector2(-286, -147), "camera_left", true)
    _button(root, "CAM ▶", Vector2(-148, -147), "camera_right", true)
    var hint := Label.new()
    hint.text = "MOVE                         CAMERA"
    hint.add_theme_font_size_override("font_size", 15)
    hint.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
    hint.position = Vector2(20, -236)
    hint.mouse_filter = Control.MOUSE_FILTER_IGNORE
    root.add_child(hint)

func _button(parent: Control, text: String, pos: Vector2, action: String, right := false):
    var b := Button.new()
    b.text = text
    b.custom_minimum_size = Vector2(112, 82)
    b.add_theme_font_size_override("font_size", 22)
    b.set_anchor_and_offset(SIDE_BOTTOM, 1.0, pos.y)
    if right:
        b.set_anchor_and_offset(SIDE_RIGHT, 1.0, pos.x)
        b.set_anchor_and_offset(SIDE_LEFT, 1.0, pos.x - 112)
    else:
        b.set_anchor_and_offset(SIDE_LEFT, 0.0, pos.x)
        b.set_anchor_and_offset(SIDE_RIGHT, 0.0, pos.x + 112)
    b.button_down.connect(_press.bind(action))
    b.button_up.connect(_release.bind(action))
    parent.add_child(b)

func _press(action: String):
    held[action] = true
    for a in _aliases(action):
        if InputMap.has_action(a): Input.action_press(a)

func _release(action: String):
    held.erase(action)
    for a in _aliases(action):
        if InputMap.has_action(a): Input.action_release(a)

func _aliases(action: String) -> Array[String]:
    match action:
        "move_forward": return ["move_forward", "forward", "move_up", "ui_up"]
        "move_backward": return ["move_backward", "backward", "move_down", "ui_down"]
        "move_left": return ["move_left", "left", "ui_left"]
        "move_right": return ["move_right", "right", "ui_right"]
        "camera_left": return ["camera_left", "look_left", "turn_left"]
        "camera_right": return ["camera_right", "look_right", "turn_right"]
    return []
GDSCRIPT
python3 - "$DST/project.godot" <<'PY'
from pathlib import Path
import sys
p=Path(sys.argv[1]); s=p.read_text()
entry='RuinsCivMobileControls="*res://RuinsCivMobileControls.gd"'
if entry not in s:
    if '[autoload]' in s:
        s=s.replace('[autoload]', '[autoload]\n'+entry, 1)
    else:
        s += '\n[autoload]\n'+entry+'\n'
p.write_text(s)
PY
# New QA candidate identity; never overwrite RC34 identity.
sed -Ei 's#^version/code=.*#version/code=42069#; s#^version/name=.*#version/name="4.6.8-rc35"#' "$DST/export_presets.cfg"
grep -q 'RuinsCivMobileControls' "$DST/project.godot"
grep -q '^version/code=42069' "$DST/export_presets.cfg"
GODOT="${GODOT_BIN:-}"
if [[ -z "$GODOT" ]]; then for x in godot4.7.2 godot-4.7.2 godot4 godot; do command -v "$x" >/dev/null 2>&1 && { GODOT="$(command -v "$x")"; break; }; done; fi
if [[ -z "$GODOT" ]]; then
 ZIP="$TOOLS/godot.zip"; BIN="$TOOLS/Godot_v${GODOT_TAG}_linux.x86_64"
 if [[ ! -x "$BIN" ]]; then curl -fL --retry 3 --connect-timeout 20 -o "$ZIP" "https://github.com/godotengine/godot/releases/download/$GODOT_TAG/Godot_v${GODOT_TAG}_linux.x86_64.zip"; unzip -o "$ZIP" -d "$TOOLS"; chmod +x "$BIN"; fi
 GODOT="$BIN"
fi
"$GODOT" --version | tee "$OUT/godot_version.txt"; grep -q '^4\.7\.2' "$OUT/godot_version.txt" || exit 62
if [[ ! -f "$TEMPLATES/android_debug.apk" || ! -f "$TEMPLATES/android_release.apk" || ! -f "$TEMPLATES/android_source.zip" ]]; then TPZ="$TOOLS/export_templates.tpz"; TMP="$TOOLS/templates-unpack"; rm -rf "$TMP"; mkdir -p "$TMP" "$TEMPLATES"; curl -fL --retry 3 --connect-timeout 20 -o "$TPZ" "https://github.com/godotengine/godot/releases/download/$GODOT_TAG/Godot_v${GODOT_TAG}_export_templates.tpz"; unzip -o "$TPZ" -d "$TMP"; cp -a "$TMP/templates/." "$TEMPLATES/"; fi
[[ -f "$TEMPLATES/android_debug.apk" && -f "$TEMPLATES/android_source.zip" ]] || exit 66
JAVA_BIN="${JAVA_HOME:+$JAVA_HOME/bin/java}"; [[ -x "$JAVA_BIN" ]] || JAVA_BIN="$(command -v java || true)"; [[ -n "$JAVA_BIN" ]] || exit 67
JAVA_BIN="$(readlink -f "$JAVA_BIN")"; export JAVA_HOME="${JAVA_HOME:-$(dirname "$(dirname "$JAVA_BIN")")}"; export PATH="$JAVA_HOME/bin:$PATH"; "$JAVA_BIN" -version 2>&1 | tee "$OUT/java_version.txt"; printf 'java_home=%s\n' "$JAVA_HOME" | tee "$OUT/java_home.txt"
SDK="${ANDROID_HOME:-${ANDROID_SDK_ROOT:-$HOME/Android/Sdk}}"; SDKMANAGER=""
for s in "$SDK/cmdline-tools/latest/bin/sdkmanager" "$SDK/cmdline-tools/bin/sdkmanager"; do [[ -x "$s" ]] && { SDKMANAGER="$s"; break; }; done
if [[ -z "$SDKMANAGER" ]]; then CMDROOT="$HOME/.cache/thf-android-cmdline-tools"; mkdir -p "$CMDROOT" "$SDK/cmdline-tools"; CTZIP="$CMDROOT/commandlinetools-linux.zip"; curl -fL --retry 3 --connect-timeout 20 -o "$CTZIP" "https://dl.google.com/android/repository/commandlinetools-linux-13114758_latest.zip"; rm -rf "$CMDROOT/unpack" "$SDK/cmdline-tools/latest"; mkdir -p "$CMDROOT/unpack" "$SDK/cmdline-tools/latest"; unzip -q -o "$CTZIP" -d "$CMDROOT/unpack"; cp -a "$CMDROOT/unpack/cmdline-tools/." "$SDK/cmdline-tools/latest/"; SDKMANAGER="$SDK/cmdline-tools/latest/bin/sdkmanager"; fi
export ANDROID_HOME="$SDK" ANDROID_SDK_ROOT="$SDK"; export PATH="$SDK/platform-tools:$SDK/cmdline-tools/latest/bin:$PATH"; yes | "$SDKMANAGER" --sdk_root="$SDK" --licenses >/dev/null || true
"$SDKMANAGER" --sdk_root="$SDK" platform-tools 'platforms;android-36' 'build-tools;36.0.0'
[[ -f "$SDK/platforms/android-36/android.jar" && -x "$SDK/platform-tools/adb" && -d "$SDK/build-tools/36.0.0" ]] || exit 68
printf 'android_sdk=%s\nandroid_jar=%s\nbuild_tools=36.0.0\n' "$SDK" "$SDK/platforms/android-36/android.jar" | tee "$OUT/android_toolchain.txt"
GODOT_XDG_CONFIG="$TOOLS/xdg-config-v6"; rm -rf "$GODOT_XDG_CONFIG"; mkdir -p "$GODOT_XDG_CONFIG"; export XDG_CONFIG_HOME="$GODOT_XDG_CONFIG"
PRESET="${RUINSCIV_ANDROID_PRESET:-}"; if [[ -z "$PRESET" ]]; then PRESET="$(awk -F'=' '/^name=/{gsub(/^"|"$/, "", $2); print $2; exit}' "$DST/export_presets.cfg")"; fi
[[ -n "$PRESET" ]] || exit 72
"$GODOT" --headless --path "$DST" --editor --quit-after 2
INSTALL_BUILD_TEMPLATE=(); if [[ ! -f "$DST/android/build/gradlew" ]]; then INSTALL_BUILD_TEMPLATE=(--install-android-build-template); fi
"$GODOT" --headless --path "$DST" "${INSTALL_BUILD_TEMPLATE[@]}" --export-debug "$PRESET" "$APK"
[[ -s "$APK" ]] || exit 63
sha256sum "$APK" | tee "$OUT/SHA256SUMS.txt"; SIZE=$(stat -c %s "$APK"); VC=$(grep -E '^version/code=' "$DST/export_presets.cfg" | head -1 | cut -d= -f2- | tr -d '"' || true); VN=$(grep -E '^version/name=' "$DST/export_presets.cfg" | head -1 | cut -d= -f2- | tr -d '"' || true); SRC=$(git -C "$DST" rev-parse HEAD 2>/dev/null || printf UNKNOWN)
cat > "$OUT/CANDIDATE.txt" <<EOF
candidate=RuinsCiv-v6-arm64.apk
source_sha=$SRC
package=$PACKAGE
versionCode=${VC:-UNKNOWN}
versionName=${VN:-UNKNOWN}
api_target=36
abi=arm64
size_bytes=$SIZE
sha256=$(sha256sum "$APK" | awk '{print $1}')
phone_status=PENDING
product_change=explicit_mobile_movement_camera_controls
EOF
cat "$OUT/CANDIDATE.txt"
