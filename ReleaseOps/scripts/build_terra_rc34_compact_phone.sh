#!/usr/bin/env bash
set -Eeuo pipefail

# THF Terra RC34 modern-human Android verification build.
# Operates only on a disposable copy of the current Terra staging source.
# It never touches WAVE_MAWJA and fails closed if a deprecated humanoid or the
# approved uploaded-world lineage disappears.

SRC="${THF_TERRA_SOURCE:-$HOME/thf-terra-rift-staging-apk-v1/terra/work}"
ROOT="${THF_TERRA_BUILD_ROOT:-$HOME/thf-terra-rc34-modern-phone-v1}"
WORK="$ROOT/work"
OUT="$ROOT/out"
GODOT="${THF_GODOT:-$HOME/.local/bin/godot-4.7.2}"
ANDROID_SDK="${ANDROID_SDK_ROOT:-$HOME/thf-builder-rc16-build/android-sdk}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VERIFY="$SCRIPT_DIR/verify_terra_modern_human_only.sh"
VERIFY_ASSETS="$SCRIPT_DIR/verify_terra_uploaded_asset_lineage.sh"
PATCH="$SCRIPT_DIR/patch_terra_modern_human_current_source.py"
APK_NAME="THF-TERRA-4.6.8-RC34-MODERN-HUMAN-TEST.apk"
EXPECTED_PACKAGE="com.topherofit.thf.terra"
EXPECTED_TARGET_SDK="36"
CANONICAL_AVATAR="web/static/assets/avatars/stage16a/thf_mpfb_stage16a_ual12_animated.glb"
CANONICAL_AVATAR_SHA256="4f556086e1b7149f6c958f1f399f4368f6ad9b76afd3503d6f848eeeb7bea24f"

fail() { printf 'TERRA_RC34_MODERN_BUILD=FAIL reason=%s\n' "$1" >&2; exit "${2:-1}"; }

[[ -d "$SRC" ]] || fail "terra_source_missing:$SRC" 10
[[ -x "$GODOT" ]] || fail "godot_4_7_2_missing:$GODOT" 11
[[ -x "$VERIFY" ]] || fail "modern_human_verifier_missing:$VERIFY" 12
[[ -x "$VERIFY_ASSETS" ]] || fail "uploaded_asset_lineage_verifier_missing:$VERIFY_ASSETS" 18
[[ -f "$PATCH" ]] || fail "modern_human_patch_missing:$PATCH" 17
[[ -d "$ANDROID_SDK/platforms/android-$EXPECTED_TARGET_SDK" ]] || fail "android_api_36_missing" 13
[[ -x "$ANDROID_SDK/platform-tools/adb" ]] || fail "adb_missing" 14

rm -rf "$ROOT"
mkdir -p "$ROOT" "$OUT"
cp -a "$SRC" "$WORK"
cd "$WORK"

# Merge the approved 2026-09-16 modern-human cleanup forward onto the current
# RC34 source copy. Historical evidence is preserved, while active runtime
# fallbacks/caches are removed or redirected to the canonical MPFB human.
python3 "$PATCH" | tee "$OUT/modern_human_patch.txt"
cp TERRA_MODERN_HUMAN_PATCH_RESULT.json "$OUT/"

THF_TERRA_CANONICAL_AVATAR="$CANONICAL_AVATAR" \
THF_TERRA_CANONICAL_AVATAR_SHA256="$CANONICAL_AVATAR_SHA256" \
"$VERIFY" "$WORK" | tee "$OUT/modern_human_gate.txt"

# Prove the later user-supplied environment/animation asset lineage is retained.
"$VERIFY_ASSETS" "$WORK" | tee "$OUT/uploaded_asset_lineage_gate.txt"

# Preserve current RC34 gameplay/world content. Normalize only standalone Android
# identity/version metadata on the first Android export preset.
python3 - <<'PY'
from pathlib import Path
import re
p=Path('export_presets.cfg')
if not p.exists():
    raise SystemExit('export_presets.cfg missing')
s=p.read_text(encoding='utf-8')
sections=re.split(r'(?=\[preset\.\d+\]\n)', s)
found=False
out=[]
for sec in sections:
    if 'platform="Android"' not in sec:
        out.append(sec); continue
    if found:
        out.append(sec); continue
    found=True
    sec=re.sub(r'package/unique_name="[^"]*"', 'package/unique_name="com.topherofit.thf.terra"', sec, count=1)
    sec=re.sub(r'version/name="[^"]*"', 'version/name="4.6.8-rc34-modern-human-v1"', sec, count=1)
    m=re.search(r'version/code=(\d+)', sec)
    if m:
        current=int(m.group(1)); new=max(current, 42073)
        sec=sec[:m.start()] + f'version/code={new}' + sec[m.end():]
    out.append(sec)
if not found:
    raise SystemExit('Android export preset missing')
p.write_text(''.join(out), encoding='utf-8')
PY

THF_TERRA_CANONICAL_AVATAR="$CANONICAL_AVATAR" \
THF_TERRA_CANONICAL_AVATAR_SHA256="$CANONICAL_AVATAR_SHA256" \
"$VERIFY" "$WORK" | tee "$OUT/modern_human_gate_after_export_patch.txt"
"$VERIFY_ASSETS" "$WORK" | tee "$OUT/uploaded_asset_lineage_gate_after_export_patch.txt"

JAVA_BIN="$(readlink -f "$(command -v java)")"
JAVA_HOME_DETECTED="$(dirname "$(dirname "$JAVA_BIN")")"
BUILD_TOOLS_DIR="$(find "$ANDROID_SDK/build-tools" -mindepth 1 -maxdepth 1 -type d | sort -V | tail -n 1)"
AAPT="$BUILD_TOOLS_DIR/aapt"
[[ -x "$AAPT" ]] || fail "aapt_missing" 15

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

PRESET="$(python3 - <<'PY'
from pathlib import Path
import re
s=Path('export_presets.cfg').read_text(encoding='utf-8')
for sec in re.split(r'(?=\[preset\.\d+\]\n)', s):
    if 'platform="Android"' in sec:
        m=re.search(r'^name="([^"]+)"', sec, re.M)
        if m:
            print(m.group(1)); break
PY
)"
[[ -n "$PRESET" ]] || fail "android_preset_name_missing" 16

"$GODOT" --headless --path "$WORK" --import >"$OUT/godot-import.log" 2>&1 || {
  tail -220 "$OUT/godot-import.log" >&2
  fail "godot_clean_import_failed" 30
}

set +e
timeout 45s "$GODOT" --headless --path "$WORK" --editor --quit-after 30 >"$OUT/godot-headless-30.log" 2>&1
headless_rc=$?
set -e
if [[ "$headless_rc" -ne 0 && "$headless_rc" -ne 124 ]]; then
  tail -220 "$OUT/godot-headless-30.log" >&2
  fail "godot_headless_30_failed_rc_$headless_rc" 31
fi

"$GODOT" --headless --path "$WORK" --export-debug "$PRESET" "$OUT/$APK_NAME" >"$OUT/godot-android-export.log" 2>&1 || {
  tail -260 "$OUT/godot-android-export.log" >&2
  fail "android_debug_export_failed" 32
}

APK="$OUT/$APK_NAME"
[[ -s "$APK" ]] || fail "apk_missing_after_export" 33
unzip -t "$APK" > "$OUT/apk-zip-test.txt"
unzip -l "$APK" > "$OUT/apk-files.txt"
"$AAPT" dump badging "$APK" > "$OUT/apk-badging.txt"

grep -q "^package: name='$EXPECTED_PACKAGE'" "$OUT/apk-badging.txt" || fail "apk_package_mismatch" 34
grep -q "^targetSdkVersion:'$EXPECTED_TARGET_SDK'$" "$OUT/apk-badging.txt" || fail "apk_target_sdk_mismatch" 35
grep -q 'lib/arm64-v8a/libgodot_android.so' "$OUT/apk-files.txt" || fail "arm64_runtime_missing" 36
grep -q 'thf_mpfb_stage16a_ual12_animated' "$OUT/apk-files.txt" || fail "modern_avatar_missing_from_apk" 37
if grep -Eiq 'thf_humanoid_v[1-6]' "$OUT/apk-files.txt"; then
  fail "legacy_humanoid_present_in_apk" 38
fi
# At least representative visual16a families must actually be packaged in the APK.
for family in downtown street transport interior nature furniture ruins; do
  grep -q "visual16a/$family/" "$OUT/apk-files.txt" || fail "uploaded_asset_family_missing_from_apk:$family" 39
done

APK_SHA="$(sha256sum "$APK" | awk '{print $1}')"
APK_SIZE="$(stat -c %s "$APK")"
AVATAR_SHA="$(sha256sum "$CANONICAL_AVATAR" | awk '{print $1}')"

cat > "$OUT/EVIDENCE.json" <<EOF
{
  "gate": "THF_TERRA_RC34_MODERN_HUMAN_ANDROID_TEST",
  "status": "PASS_BUILD_AND_ENGINE_GATES",
  "source_authority": "current_builder_RC34_copy_plus_2026_09_16_modern_human_cleanup",
  "engine": "Godot 4.7.2",
  "application_id": "$EXPECTED_PACKAGE",
  "target_sdk": 36,
  "architecture": "arm64-v8a",
  "avatar": "$CANONICAL_AVATAR",
  "avatar_sha256": "$AVATAR_SHA",
  "legacy_humanoid_in_active_runtime": false,
  "legacy_humanoid_in_apk": false,
  "uploaded_visual16a_lineage_gate": "PASS",
  "uploaded_visual16a_families_in_apk": ["downtown","street","transport","interior","nature","furniture","ruins"],
  "apk": "$APK_NAME",
  "apk_sha256": "$APK_SHA",
  "apk_size_bytes": $APK_SIZE,
  "physical_device_test": "PENDING",
  "production_signing": "NOT_CLAIMED",
  "google_play_upload": "NOT_CLAIMED",
  "production_web_deployment": "NOT_CLAIMED"
}
EOF
sha256sum "$OUT/EVIDENCE.json" > "$OUT/EVIDENCE.json.sha256"
cat "$OUT/EVIDENCE.json"
