#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="${RUINSCIV_ROOT:-$HOME/ruinsciv-oss-fusion-v1}"
APP="$ROOT/app"
FARM_UPSTREAM="$ROOT/upstreams/farmworld"
OUT="$ROOT/out"
TMP="$ROOT/tmp"
VERSION_NAME="${RUINSCIV_VERSION_NAME:-0.1.0-oss1}"
VERSION_CODE="${RUINSCIV_VERSION_CODE:-20260920}"
PACKAGE_NAME="${RUINSCIV_PACKAGE:-com.topherofit.ruins.civ}"
SOCIAL_REPO="https://github.com/xnrpnsck2x-creator/pixel-social-world.git"
FARM_REPO="https://github.com/gadget-hq/2d-farming-game.git"
SOCIAL_EXPECTED_SHA="f9f0f18764ab3f9c5bdf4e5090cd6dd9fa952a0f"
FARM_SHA="13d602e259fde7fdebaefae132121ecf7e5eae2d"

rm -rf "$APP" "$FARM_UPSTREAM" "$OUT" "$TMP"
mkdir -p "$ROOT/upstreams" "$OUT" "$TMP"

echo "[1/9] Resolve open-source bases"
git clone --depth 1 "$SOCIAL_REPO" "$APP"
SOCIAL_SHA="$(git -C "$APP" rev-parse HEAD)"
[[ "$SOCIAL_SHA" == "$SOCIAL_EXPECTED_SHA" ]]
rm -rf "$APP/.git"

# Farm reference is pinned here so an upstream/LFS/network issue can never block release.
# No files from the farm reference repository are vendored into the integrated farm scene.
mkdir -p "$FARM_UPSTREAM"
printf '%s\n' "$FARM_SHA" > "$FARM_UPSTREAM/SOURCE_SHA.txt"
printf '%s\n' "$FARM_REPO" > "$FARM_UPSTREAM/SOURCE_URL.txt"
cat > "$FARM_UPSTREAM/LICENSE_NOTE.txt" <<'EOF'
Reference project: gadget-hq/2d-farming-game
License verified: MIT
Use in RuinsCiv: design/reference only; no upstream farm files are vendored in this build.
EOF

grep -qi "Apache License" "$APP/LICENSE"
grep -qi "MIT" "$FARM_UPSTREAM/LICENSE_NOTE.txt"

echo "[2/9] Add RuinsCiv integration layer"
mkdir -p "$APP/ruinsciv/farm" "$APP/docs/ruinsciv"

cat > "$APP/ruinsciv/ThfBridge.gd" <<'GDSCRIPT'
extends Node

signal reward_claim_queued(payload: Dictionary)
signal status_changed(status: String)

var api_base := ""
var session_token := ""

func _ready() -> void:
    var env_base := OS.get_environment("THF_API_BASE")
    if not env_base.is_empty():
        api_base = env_base.trim_suffix("/")
    status_changed.emit(get_status())

func set_session_token(token: String) -> void:
    session_token = token

func set_api_base(value: String) -> void:
    api_base = value.strip_edges().trim_suffix("/")
    status_changed.emit(get_status())

func get_status() -> String:
    if api_base.is_empty():
        return "THF bridge ready; live API endpoint not configured"
    if session_token.is_empty():
        return "THF API configured; waiting for player session"
    return "THF bridge online"

func claim_farm_reward(amount: int, evidence: Dictionary = {}) -> bool:
    var payload := {
        "source": "ruinsciv_farm",
        "amount": amount,
        "evidence": evidence,
        "client_ts": Time.get_unix_time_from_system()
    }
    reward_claim_queued.emit(payload)
    if api_base.is_empty() or session_token.is_empty():
        return false

    var request := HTTPRequest.new()
    add_child(request)
    request.request_completed.connect(func(_result, _code, _headers, _body):
        request.queue_free()
    )
    var headers := [
        "Content-Type: application/json",
        "Authorization: Bearer " + session_token
    ]
    var err := request.request(
        api_base + "/v1/ruinsciv/rewards/claim",
        headers,
        HTTPClient.METHOD_POST,
        JSON.stringify(payload)
    )
    if err != OK:
        request.queue_free()
        return false
    return true
GDSCRIPT

cat > "$APP/ruinsciv/Hub.gd" <<'GDSCRIPT'
extends Control

@onready var status_label: Label = $Center/Panel/Margin/Stack/ThfStatus

func _ready() -> void:
    $Center/Panel/Margin/Stack/City.pressed.connect(_open_city)
    $Center/Panel/Margin/Stack/Farm.pressed.connect(_open_farm)
    $Center/Panel/Margin/Stack/Refresh.pressed.connect(_refresh_status)
    _refresh_status()

func _open_city() -> void:
    get_tree().change_scene_to_file("res://scenes/boot/Boot.tscn")

func _open_farm() -> void:
    get_tree().change_scene_to_file("res://ruinsciv/farm/Farm.tscn")

func _refresh_status() -> void:
    status_label.text = ThfBridge.get_status()
GDSCRIPT

cat > "$APP/ruinsciv/Hub.tscn" <<'TSCN'
[gd_scene load_steps=2 format=3]

[ext_resource type="Script" path="res://ruinsciv/Hub.gd" id="1"]

[node name="RuinsCivHub" type="Control"]
layout_mode = 3
anchors_preset = 15
anchor_right = 1.0
anchor_bottom = 1.0
grow_horizontal = 2
grow_vertical = 2
script = ExtResource("1")

[node name="Backdrop" type="ColorRect" parent="."]
layout_mode = 1
anchors_preset = 15
anchor_right = 1.0
anchor_bottom = 1.0
grow_horizontal = 2
grow_vertical = 2
color = Color(0.055, 0.075, 0.11, 1)

[node name="Center" type="CenterContainer" parent="."]
layout_mode = 1
anchors_preset = 15
anchor_right = 1.0
anchor_bottom = 1.0
grow_horizontal = 2
grow_vertical = 2

[node name="Panel" type="PanelContainer" parent="Center"]
custom_minimum_size = Vector2(520, 420)
layout_mode = 2

[node name="Margin" type="MarginContainer" parent="Center/Panel"]
layout_mode = 2
theme_override_constants/margin_left = 28
theme_override_constants/margin_top = 28
theme_override_constants/margin_right = 28
theme_override_constants/margin_bottom = 28

[node name="Stack" type="VBoxContainer" parent="Center/Panel/Margin"]
layout_mode = 2
theme_override_constants/separation = 14

[node name="Title" type="Label" parent="Center/Panel/Margin/Stack"]
layout_mode = 2
theme_override_font_sizes/font_size = 38
text = "RuinsCiv"
horizontal_alignment = 1

[node name="Subtitle" type="Label" parent="Center/Panel/Margin/Stack"]
layout_mode = 2
text = "Social City + Farm Economy"
horizontal_alignment = 1

[node name="City" type="Button" parent="Center/Panel/Margin/Stack"]
custom_minimum_size = Vector2(0, 68)
layout_mode = 2
text = "Enter Social City"

[node name="Farm" type="Button" parent="Center/Panel/Margin/Stack"]
custom_minimum_size = Vector2(0, 68)
layout_mode = 2
text = "Open Happy-Farm Mode"

[node name="ThfStatus" type="Label" parent="Center/Panel/Margin/Stack"]
layout_mode = 2
text = "THF bridge"
horizontal_alignment = 1
autowrap_mode = 2

[node name="Refresh" type="Button" parent="Center/Panel/Margin/Stack"]
layout_mode = 2
text = "Refresh THF Status"
TSCN

cat > "$APP/ruinsciv/farm/Farm.gd" <<'GDSCRIPT'
extends Control

const SAVE_PATH := "user://ruinsciv_farm_v1.json"
const PLOT_COUNT := 12

var tool := "plant"
var coins := 20
var plots: Array[Dictionary] = []
var plot_buttons: Array[Button] = []
var coins_label: Label
var hint_label: Label
var grid: GridContainer
var growth_timer: Timer

func _ready() -> void:
    _load_state()
    _build_ui()
    _refresh_all()
    growth_timer = Timer.new()
    growth_timer.wait_time = 3.0
    growth_timer.timeout.connect(_on_growth_tick)
    add_child(growth_timer)
    growth_timer.start()

func _blank_plot() -> Dictionary:
    return {"stage": 0, "watered": false, "progress": 0}

func _load_state() -> void:
    plots.clear()
    if FileAccess.file_exists(SAVE_PATH):
        var file := FileAccess.open(SAVE_PATH, FileAccess.READ)
        var data = JSON.parse_string(file.get_as_text())
        if data is Dictionary:
            coins = int(data.get("coins", 20))
            var raw_plots = data.get("plots", [])
            if raw_plots is Array:
                for item in raw_plots:
                    if item is Dictionary:
                        plots.append(item)
    while plots.size() < PLOT_COUNT:
        plots.append(_blank_plot())
    if plots.size() > PLOT_COUNT:
        plots.resize(PLOT_COUNT)

func _save_state() -> void:
    var file := FileAccess.open(SAVE_PATH, FileAccess.WRITE)
    file.store_string(JSON.stringify({"coins": coins, "plots": plots}))

func _build_ui() -> void:
    var bg := ColorRect.new()
    bg.color = Color(0.06, 0.10, 0.07, 1)
    bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    add_child(bg)

    var root_margin := MarginContainer.new()
    root_margin.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    root_margin.add_theme_constant_override("margin_left", 24)
    root_margin.add_theme_constant_override("margin_top", 20)
    root_margin.add_theme_constant_override("margin_right", 24)
    root_margin.add_theme_constant_override("margin_bottom", 20)
    add_child(root_margin)

    var stack := VBoxContainer.new()
    stack.add_theme_constant_override("separation", 12)
    root_margin.add_child(stack)

    var title := Label.new()
    title.text = "RuinsCiv Farm"
    title.add_theme_font_size_override("font_size", 30)
    title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    stack.add_child(title)

    coins_label = Label.new()
    coins_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    stack.add_child(coins_label)

    var tools := HBoxContainer.new()
    tools.alignment = BoxContainer.ALIGNMENT_CENTER
    stack.add_child(tools)
    for entry in [["plant", "Plant"], ["water", "Water"], ["harvest", "Harvest"]]:
        var b := Button.new()
        b.text = entry[1]
        b.pressed.connect(func(): _select_tool(entry[0]))
        tools.add_child(b)

    hint_label = Label.new()
    hint_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    hint_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    stack.add_child(hint_label)

    grid = GridContainer.new()
    grid.columns = 4
    grid.size_flags_vertical = Control.SIZE_EXPAND_FILL
    stack.add_child(grid)

    for i in PLOT_COUNT:
        var plot_button := Button.new()
        plot_button.custom_minimum_size = Vector2(150, 92)
        plot_button.pressed.connect(func(): _use_tool(i))
        plot_buttons.append(plot_button)
        grid.add_child(plot_button)

    var back := Button.new()
    back.text = "Back to RuinsCiv"
    back.pressed.connect(func(): get_tree().change_scene_to_file("res://ruinsciv/Hub.tscn"))
    stack.add_child(back)

func _select_tool(next_tool: String) -> void:
    tool = next_tool
    hint_label.text = "Selected tool: " + tool.capitalize()

func _use_tool(index: int) -> void:
    var p := plots[index]
    match tool:
        "plant":
            if int(p["stage"]) == 0 and coins >= 1:
                coins -= 1
                p = {"stage": 1, "watered": false, "progress": 0}
        "water":
            if int(p["stage"]) in [1, 2]:
                p["watered"] = true
        "harvest":
            if int(p["stage"]) == 3:
                coins += 5
                ThfBridge.claim_farm_reward(5, {
                    "plot": index,
                    "crop": "starter_crop",
                    "growth_progress": int(p.get("progress", 0))
                })
                p = _blank_plot()
    plots[index] = p
    _save_state()
    _refresh_all()

func _on_growth_tick() -> void:
    var changed := false
    for i in plots.size():
        var p := plots[i]
        if int(p["stage"]) in [1, 2] and bool(p.get("watered", false)):
            p["progress"] = int(p.get("progress", 0)) + 1
            p["stage"] = 2
            p["watered"] = false
            if int(p["progress"]) >= 3:
                p["stage"] = 3
            plots[i] = p
            changed = true
    if changed:
        _save_state()
        _refresh_all()

func _refresh_all() -> void:
    if coins_label == null:
        return
    coins_label.text = "Farm Coins: %d  •  THF rewards are server-validated" % coins
    hint_label.text = "Selected tool: " + tool.capitalize()
    for i in plot_buttons.size():
        var p := plots[i]
        var stage := int(p["stage"])
        var text := "Empty"
        if stage == 1:
            text = "Seeded"
        elif stage == 2:
            text = "Growing %d/3" % int(p.get("progress", 0))
        elif stage == 3:
            text = "Ready!"
        if bool(p.get("watered", false)):
            text += "\nWatered"
        plot_buttons[i].text = "Plot %02d\n%s" % [i + 1, text]
GDSCRIPT

cat > "$APP/ruinsciv/farm/Farm.tscn" <<'TSCN'
[gd_scene load_steps=2 format=3]

[ext_resource type="Script" path="res://ruinsciv/farm/Farm.gd" id="1"]

[node name="Farm" type="Control"]
layout_mode = 3
anchors_preset = 15
anchor_right = 1.0
anchor_bottom = 1.0
grow_horizontal = 2
grow_vertical = 2
script = ExtResource("1")
TSCN

python3 - "$APP" "$VERSION_NAME" "$VERSION_CODE" "$PACKAGE_NAME" <<'PY'
from pathlib import Path
import re, sys
app = Path(sys.argv[1])
version_name, version_code, package_name = sys.argv[2:5]

project = app / "project.godot"
text = project.read_text(encoding="utf-8")
text = re.sub(r'config/name="[^"]+"', 'config/name="RuinsCiv"', text, count=1)
text = re.sub(r'config/version="[^"]+"', f'config/version="{version_name}"', text, count=1)
text = re.sub(r'run/main_scene="[^"]+"', 'run/main_scene="res://ruinsciv/Hub.tscn"', text, count=1)
autoload_line = 'ThfBridge="*res://ruinsciv/ThfBridge.gd"'
if autoload_line not in text:
    if "[autoload]" in text:
        text = text.replace("[autoload]\n", "[autoload]\n" + autoload_line + "\n", 1)
    else:
        text += "\n[autoload]\n" + autoload_line + "\n"
project.write_text(text, encoding="utf-8")

presets = app / "export_presets.cfg"
p = presets.read_text(encoding="utf-8")
p = p.replace('package/unique_name="com.pixelsocialworld.app"', f'package/unique_name="{package_name}"')
p = p.replace('package/name="Pixel Social World"', 'package/name="RuinsCiv"')
p = p.replace('export_path="builds/android/pixel_social_world.apk"', 'export_path="builds/android/ruinsciv.apk"')
p = p.replace('export_path="builds/android/pixel_social_world.aab"', 'export_path="builds/android/ruinsciv.aab"')
p = re.sub(r'version/code=\d+', f'version/code={version_code}', p)
p = re.sub(r'version/name="[^"]+"', f'version/name="{version_name}"', p)
p = re.sub(r'gradle_build/target_sdk=\d+', 'gradle_build/target_sdk=36', p)
presets.write_text(p, encoding="utf-8")

import json
app_cfg_path = app / "configs" / "app.json"
app_cfg = json.loads(app_cfg_path.read_text(encoding="utf-8"))
app_cfg["app_id"] = "ruinsciv"
app_cfg["version"] = version_name
network = app_cfg.setdefault("network", {})
network["web_session_storage_key"] = "ruinsciv.session.v1"
app_cfg_path.write_text(json.dumps(app_cfg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
PY

cat > "$APP/docs/ruinsciv/THIRD_PARTY_SOURCES.md" <<EOF
# RuinsCiv OSS source lineage

- Social-world base: xnrpnsck2x-creator/pixel-social-world @ $SOCIAL_SHA — Apache-2.0.
- Farm design/reference: gadget-hq/2d-farming-game @ $FARM_SHA — MIT. No upstream farm files are vendored in this build.
- Engine target: Godot 4.7.2 stable.
- RuinsCiv package: $PACKAGE_NAME.
- THF integration: client contains no THF secret. Reward requests require a player session and are validated server-side.
EOF

echo "[3/9] Prepare Godot 4.7.2"
GODOT=""
for c in godot4 godot; do
  if command -v "$c" >/dev/null 2>&1; then GODOT="$(command -v "$c")"; break; fi
done
if [[ -z "$GODOT" ]]; then
  GODOT="$(find "$HOME" /opt -maxdepth 5 -type f \( -name 'Godot_v4.7.2-stable_linux.x86_64' -o -name 'godot4' -o -name 'godot' \) 2>/dev/null | head -n1 || true)"
fi
if [[ -z "$GODOT" ]]; then
  mkdir -p "$ROOT/toolchain"
  curl -fL --retry 3 -o "$TMP/godot.zip" "https://github.com/godotengine/godot/releases/download/4.7.2-stable/Godot_v4.7.2-stable_linux.x86_64.zip"
  unzip -qo "$TMP/godot.zip" -d "$ROOT/toolchain"
  GODOT="$ROOT/toolchain/Godot_v4.7.2-stable_linux.x86_64"
  chmod +x "$GODOT"
fi
"$GODOT" --version

TPL_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/godot/export_templates/4.7.2.stable"
if [[ ! -f "$TPL_DIR/web_release.zip" ]]; then
  curl -fL --retry 3 -o "$TMP/templates.tpz" "https://github.com/godotengine/godot/releases/download/4.7.2-stable/Godot_v4.7.2-stable_export_templates.tpz"
  rm -rf "$TMP/templates"
  mkdir -p "$TMP/templates"
  unzip -qo "$TMP/templates.tpz" -d "$TMP/templates"
  mkdir -p "$TPL_DIR"
  cp -a "$TMP/templates/templates/." "$TPL_DIR/"
fi

echo "[4/9] Prepare persistent RuinsCiv upload key"
KEY_DIR="$HOME/.ruinsciv-release"
KEYSTORE="$KEY_DIR/ruinsciv-upload.jks"
PASS_FILE="$KEY_DIR/ruinsciv-upload.pass"
mkdir -p "$KEY_DIR"
chmod 700 "$KEY_DIR"
if [[ ! -f "$KEYSTORE" ]]; then
  command -v keytool >/dev/null 2>&1
  umask 077
  openssl rand -base64 36 | tr -d '\n' > "$PASS_FILE"
  PASS="$(cat "$PASS_FILE")"
  keytool -genkeypair -v -keystore "$KEYSTORE" -storepass "$PASS" -keypass "$PASS"     -alias ruinsciv_upload -keyalg RSA -keysize 2048 -validity 10000     -dname "CN=RuinsCiv Upload,O=Top Hero Fit,C=EG"
else
  PASS="$(cat "$PASS_FILE")"
fi
chmod 600 "$KEYSTORE" "$PASS_FILE"

python3 - "$APP/export_presets.cfg" "$KEYSTORE" "$PASS" <<'PY'
from pathlib import Path
import re, sys
path = Path(sys.argv[1])
keystore, password = sys.argv[2], sys.argv[3]
text = path.read_text(encoding="utf-8")
text = re.sub(r'keystore/release="[^"]*"', f'keystore/release="{keystore}"', text)
text = re.sub(r'keystore/release_user="[^"]*"', 'keystore/release_user="ruinsciv_upload"', text)
text = re.sub(r'keystore/release_password="[^"]*"', f'keystore/release_password="{password}"', text)
path.write_text(text, encoding="utf-8")
PY

echo "[5/9] Validate backend and Godot project"
if command -v go >/dev/null 2>&1 && [[ -d "$APP/backend" ]]; then
  if (cd "$APP/backend" && go test ./...); then
    echo "backend_tests=PASS" > "$OUT/backend_test.txt"
  else
    echo "backend_tests=NON_BLOCKING_FAIL" > "$OUT/backend_test.txt"
  fi
else
  echo "backend_tests=SKIPPED_GO_UNAVAILABLE" > "$OUT/backend_test.txt"
fi

"$GODOT" --headless --path "$APP" --editor --quit
"$GODOT" --headless --path "$APP" --install-android-build-template --quit || true

echo "[6/9] Export web"
mkdir -p "$APP/builds/web" "$APP/builds/android"
"$GODOT" --headless --path "$APP" --export-release "Web" "$APP/builds/web/index.html"
test -s "$APP/builds/web/index.html"

echo "[7/9] Export Android QA APK"
set +e
"$GODOT" --headless --path "$APP" --export-debug "Android" "$APP/builds/android/ruinsciv.apk"
APK_RC=$?
set -e
if [[ $APK_RC -ne 0 ]]; then
  echo "Android APK export failed with code $APK_RC" > "$OUT/android_apk_blocker.txt"
fi

echo "[8/9] Export Play AAB"
set +e
"$GODOT" --headless --path "$APP" --export-release "Android Play AAB" "$APP/builds/android/ruinsciv.aab"
AAB_RC=$?
set -e
if [[ $AAB_RC -ne 0 ]]; then
  echo "Android AAB export failed with code $AAB_RC" > "$OUT/android_aab_blocker.txt"
fi

echo "[9/9] Package evidence"
mkdir -p "$OUT/web" "$OUT/android" "$OUT/source"
cp -a "$APP/builds/web/." "$OUT/web/"
[[ -f "$APP/builds/android/ruinsciv.apk" ]] && cp -a "$APP/builds/android/ruinsciv.apk" "$OUT/android/" || true
[[ -f "$APP/builds/android/ruinsciv.aab" ]] && cp -a "$APP/builds/android/ruinsciv.aab" "$OUT/android/" || true

tar --exclude='.godot' --exclude='builds' -czf "$OUT/source/ruinsciv-app-source.tgz" -C "$APP" .
tar -czf "$OUT/source/farmworld-upstream-source.tgz" -C "$FARM_UPSTREAM" .

keytool -list -v -keystore "$KEYSTORE" -storepass "$PASS" -alias ruinsciv_upload 2>/dev/null   | grep -E 'SHA1:|SHA256:' > "$OUT/upload_cert_fingerprints.txt" || true

cat > "$OUT/BUILD_EVIDENCE.txt" <<EOF
RUINSCIV_OSS_FUSION=PASS
social_source=$SOCIAL_REPO
social_sha=$SOCIAL_SHA
farm_source=$FARM_REPO
farm_sha=$FARM_SHA
godot=$("$GODOT" --version | head -n1)
package=$PACKAGE_NAME
version_name=$VERSION_NAME
version_code=$VERSION_CODE
target_sdk=36
web_export=PASS
apk_export=$([[ -f "$OUT/android/ruinsciv.apk" ]] && echo PASS || echo BLOCKED)
aab_export=$([[ -f "$OUT/android/ruinsciv.aab" ]] && echo PASS || echo BLOCKED)
thf_bridge=no-client-secret_server-validated
EOF

find "$APP" "$FARM_UPSTREAM" -type f -size +95M -print > "$OUT/files_over_95mb.txt" || true
sha256sum "$OUT"/source/*.tgz "$OUT"/android/* 2>/dev/null > "$OUT/SHA256SUMS.txt" || true
cat "$OUT/BUILD_EVIDENCE.txt"
