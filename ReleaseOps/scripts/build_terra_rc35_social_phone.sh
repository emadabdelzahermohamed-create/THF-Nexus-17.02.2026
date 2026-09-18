#!/usr/bin/env bash
set -Eeuo pipefail

# RuinsCiv RC35 independent social-game Android candidate.
# Source authority: current RC34 builder source, patched forward only.
# Adds approved modern human/world lineage + standalone social auth + account deletion.
# Never touches WAVE_MAWJA source/runtime/state.

SRC="${THF_TERRA_SOURCE:-$HOME/thf-terra-rift-staging-apk-v1/terra/work}"
ROOT="${THF_TERRA_BUILD_ROOT:-$HOME/thf-terra-rc35-social-phone-v1}"
WORK="$ROOT/work"
OUT="$ROOT/out"
GODOT="${THF_GODOT:-$HOME/.local/bin/godot-4.7.2}"
ANDROID_SDK="${ANDROID_SDK_ROOT:-$HOME/thf-builder-rc16-build/android-sdk}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

PATCH_IDENTITY="$SCRIPT_DIR/patch_ruinsciv_identity_v1.py"
PATCH_HUMAN="$SCRIPT_DIR/patch_terra_modern_human_current_source.py"
VERIFY_HUMAN="$SCRIPT_DIR/verify_terra_modern_human_only.sh"
VERIFY_ASSETS="$SCRIPT_DIR/verify_terra_uploaded_asset_lineage.sh"
PATCH_SOCIAL="$SCRIPT_DIR/patch_terra_social_auth_v1.py"
PATCH_DELETE="$SCRIPT_DIR/patch_terra_account_deletion_v1.py"
SOCIAL_OVERLAY="${THF_TERRA_SOCIAL_AUTH_OVERLAY:-$SCRIPT_DIR/overlay}"
DELETE_OVERLAY="${THF_TERRA_ACCOUNT_DELETE_OVERLAY:-$SCRIPT_DIR/delete-overlay}"

APK_NAME="RuinsCiv-4.7.0-RC35-SOCIAL-MODERN-HUMAN-TEST.apk"
EXPECTED_PACKAGE="com.topherofit.ruins.civ"
EXPECTED_TARGET_SDK="36"
CANONICAL_AVATAR="web/static/assets/avatars/stage16a/thf_mpfb_stage16a_ual12_animated.glb"
CANONICAL_AVATAR_SHA256="4f556086e1b7149f6c958f1f399f4368f6ad9b76afd3503d6f848eeeb7bea24f"

fail(){ printf 'RUINSCIV_RC35_SOCIAL_BUILD=FAIL reason=%s\n' "$1" >&2; exit "${2:-1}"; }

[[ -d "$SRC" ]] || fail "terra_source_missing:$SRC" 10
[[ -x "$GODOT" ]] || fail "godot_4_7_2_missing:$GODOT" 11
[[ -f "$PATCH_IDENTITY" ]] || fail "ruinsciv_identity_patch_missing" 12
[[ -f "$PATCH_HUMAN" ]] || fail "modern_human_patch_missing" 13
[[ -x "$VERIFY_HUMAN" ]] || fail "modern_human_verifier_missing" 14
[[ -x "$VERIFY_ASSETS" ]] || fail "uploaded_asset_verifier_missing" 15
[[ -f "$PATCH_SOCIAL" ]] || fail "social_auth_patch_missing" 15
[[ -f "$PATCH_DELETE" ]] || fail "account_delete_patch_missing" 16
[[ -f "$SOCIAL_OVERLAY/app/auth_social.py" ]] || fail "social_auth_overlay_missing" 17
[[ -f "$DELETE_OVERLAY/web/templates/account_delete.html" ]] || fail "account_delete_overlay_missing" 18
[[ -d "$ANDROID_SDK/platforms/android-$EXPECTED_TARGET_SDK" ]] || fail "android_api_36_missing" 19
[[ -x "$ANDROID_SDK/platform-tools/adb" ]] || fail "adb_missing" 20

rm -rf "$ROOT"
mkdir -p "$ROOT" "$OUT"
cp -a "$SRC" "$WORK"
cd "$WORK"

# Forward-only cumulative patch sequence.
python3 "$PATCH_IDENTITY" | tee "$OUT/00-ruinsciv-identity-patch.log"
cp RUINSCIV_IDENTITY_PATCH_RESULT.json "$OUT/"
python3 "$PATCH_HUMAN" | tee "$OUT/01-modern-human-patch.log"
cp TERRA_MODERN_HUMAN_PATCH_RESULT.json "$OUT/"
THF_TERRA_SOCIAL_AUTH_OVERLAY="$SOCIAL_OVERLAY" python3 "$PATCH_SOCIAL" | tee "$OUT/02-social-auth-patch.log"
cp TERRA_SOCIAL_AUTH_V1_PATCH_RESULT.json "$OUT/"
THF_TERRA_ACCOUNT_DELETE_OVERLAY="$DELETE_OVERLAY" python3 "$PATCH_DELETE" | tee "$OUT/03-account-delete-patch.log"
cp TERRA_ACCOUNT_DELETION_V1_PATCH_RESULT.json "$OUT/"
# Re-apply final identity after feature overlays so no legacy package/branding can be reintroduced.
python3 "$PATCH_IDENTITY" | tee "$OUT/03b-ruinsciv-identity-post-overlays.log"
cp RUINSCIV_IDENTITY_PATCH_RESULT.json "$OUT/RUINSCIV_IDENTITY_PATCH_RESULT_POST_OVERLAYS.json"

THF_TERRA_CANONICAL_AVATAR="$CANONICAL_AVATAR" \
THF_TERRA_CANONICAL_AVATAR_SHA256="$CANONICAL_AVATAR_SHA256" \
"$VERIFY_HUMAN" "$WORK" | tee "$OUT/04-modern-human-gate.log"
"$VERIFY_ASSETS" "$WORK" | tee "$OUT/05-uploaded-asset-lineage-gate.log"

# Static source gates for the exact source that will be exported.
python3 -m compileall -q app
grep -q '/api/auth/oauth/start' app/main.py || fail "social_auth_route_missing" 21
LEGACY_PACKAGE_HITS="$(grep -RIl --exclude-dir=.godot --exclude-dir=build 'com.topherofit.thf.terra' project.godot export_presets.cfg native web config android app 2>/dev/null || true)"
[[ -z "$LEGACY_PACKAGE_HITS" ]] || { printf '%s\n' "$LEGACY_PACKAGE_HITS" | tee "$OUT/legacy-package-hits.txt"; fail "legacy_package_reference_active" 211; }
LEGACY_BRAND_HITS="$(grep -RIl --exclude-dir=.godot --exclude-dir=build -E 'THF Terra|THF World' project.godot export_presets.cfg native web config android app 2>/dev/null || true)"
[[ -z "$LEGACY_BRAND_HITS" ]] || { printf '%s\n' "$LEGACY_BRAND_HITS" | tee "$OUT/legacy-brand-hits.txt"; fail "legacy_public_brand_active" 212; }
grep -q '/api/account/delete' app/main.py || fail "account_delete_api_missing" 22
grep -q '/account-delete' app/main.py || fail "account_delete_web_route_missing" 23
grep -q 'func _social_auth_pressed(provider: String)' native/world/WorldMain.gd || fail "native_social_auth_missing" 24
grep -q 'func _open_account_delete_page()' native/world/WorldMain.gd || fail "native_delete_entry_missing" 25
grep -q 'socialProviders' web/templates/index.html || fail "web_social_buttons_missing" 26
test -s web/templates/account_delete.html || fail "external_delete_resource_missing" 27
if command -v node >/dev/null 2>&1; then
  node --check web/static/game2d.js
  node --check web/static/game3d.js
fi

# Standalone Android identity/version metadata. Gameplay/world content is preserved.
python3 - <<'PY'
from pathlib import Path
import re
p=Path('export_presets.cfg')
if not p.exists(): raise SystemExit('export_presets.cfg missing')
s=p.read_text(encoding='utf-8')
sections=re.split(r'(?=\[preset\.\d+\]\n)',s)
found=False;out=[]
for sec in sections:
    if 'platform="Android"' not in sec or found:
        out.append(sec);continue
    found=True
    sec=re.sub(r'package/unique_name="[^"]*"','package/unique_name="com.topherofit.ruins.civ"',sec,count=1)
    sec=re.sub(r'version/name="[^"]*"','version/name="4.7.0-rc35-ruinsciv-v1"',sec,count=1)
    m=re.search(r'version/code=(\d+)',sec)
    if m:
        new=max(int(m.group(1)),42075)
        sec=sec[:m.start()]+f'version/code={new}'+sec[m.end():]
    out.append(sec)
if not found: raise SystemExit('Android export preset missing')
p.write_text(''.join(out),encoding='utf-8')
PY

THF_TERRA_CANONICAL_AVATAR="$CANONICAL_AVATAR" \
THF_TERRA_CANONICAL_AVATAR_SHA256="$CANONICAL_AVATAR_SHA256" \
"$VERIFY_HUMAN" "$WORK" | tee "$OUT/06-modern-human-post-metadata-gate.log"
"$VERIFY_ASSETS" "$WORK" | tee "$OUT/07-uploaded-assets-post-metadata-gate.log"

JAVA_BIN="$(readlink -f "$(command -v java)")"
JAVA_HOME_DETECTED="$(dirname "$(dirname "$JAVA_BIN")")"
BUILD_TOOLS_DIR="$(find "$ANDROID_SDK/build-tools" -mindepth 1 -maxdepth 1 -type d | sort -V | tail -n 1)"
AAPT="$BUILD_TOOLS_DIR/aapt"
[[ -x "$AAPT" ]] || fail "aapt_missing" 28

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
for sec in re.split(r'(?=\[preset\.\d+\]\n)',s):
    if 'platform="Android"' in sec:
        m=re.search(r'^name="([^"]+)"',sec,re.M)
        if m:
            print(m.group(1));break
PY
)"
[[ -n "$PRESET" ]] || fail "android_preset_name_missing" 29

"$GODOT" --headless --path "$WORK" --import >"$OUT/godot-import.log" 2>&1 || {
  tail -220 "$OUT/godot-import.log" >&2; fail "godot_clean_import_failed" 30;
}
if grep -Eiq 'SCRIPT ERROR|Parse Error|Failed to load script' "$OUT/godot-import.log"; then
  tail -260 "$OUT/godot-import.log" >&2
  fail "godot_import_contains_script_error" 301
fi

set +e
timeout 45s "$GODOT" --headless --path "$WORK" --editor --quit-after 30 >"$OUT/godot-headless-30.log" 2>&1
headless_rc=$?
set -e
if [[ "$headless_rc" -ne 0 && "$headless_rc" -ne 124 ]]; then
  tail -220 "$OUT/godot-headless-30.log" >&2; fail "godot_headless_failed_rc_$headless_rc" 31
fi
if grep -Eiq 'SCRIPT ERROR|Parse Error|Failed to load script' "$OUT/godot-headless-30.log"; then
  tail -260 "$OUT/godot-headless-30.log" >&2
  fail "godot_headless_contains_script_error" 311
fi

"$GODOT" --headless --path "$WORK" --export-debug "$PRESET" "$OUT/$APK_NAME" >"$OUT/godot-android-export.log" 2>&1 || {
  tail -260 "$OUT/godot-android-export.log" >&2; fail "android_debug_export_failed" 32;
}
if grep -Eiq 'SCRIPT ERROR|Parse Error|Failed to load script' "$OUT/godot-android-export.log"; then
  tail -300 "$OUT/godot-android-export.log" >&2
  fail "android_export_contains_script_error" 321
fi

APK="$OUT/$APK_NAME"
[[ -s "$APK" ]] || fail "apk_missing_after_export" 33
unzip -t "$APK" > "$OUT/apk-zip-test.txt"
unzip -l "$APK" > "$OUT/apk-files.txt"
"$AAPT" dump badging "$APK" > "$OUT/apk-badging.txt"

grep -q "^package: name='$EXPECTED_PACKAGE'" "$OUT/apk-badging.txt" || fail "apk_package_mismatch" 34
grep -q "^targetSdkVersion:'$EXPECTED_TARGET_SDK'$" "$OUT/apk-badging.txt" || fail "apk_target_sdk_mismatch" 35
grep -q 'lib/arm64-v8a/libgodot_android.so' "$OUT/apk-files.txt" || fail "arm64_runtime_missing" 36
grep -q 'thf_mpfb_stage16a_ual12_animated' "$OUT/apk-files.txt" || fail "modern_avatar_missing_from_apk" 37
if grep -Eiq 'thf_humanoid_v[1-6]' "$OUT/apk-files.txt"; then fail "legacy_humanoid_present_in_apk" 38; fi
for family in downtown street transport interior nature furniture ruins; do
  grep -q "visual16a/$family/" "$OUT/apk-files.txt" || fail "uploaded_asset_family_missing_from_apk:$family" 39
done

APK_SHA="$(sha256sum "$APK" | awk '{print $1}')"
APK_SIZE="$(stat -c %s "$APK")"
AVATAR_SHA="$(sha256sum "$CANONICAL_AVATAR" | awk '{print $1}')"

cat > "$OUT/EVIDENCE.json" <<EOF
{
  "gate": "RUINSCIV_RC35_INDEPENDENT_SOCIAL_ANDROID_TEST",
  "status": "PASS_BUILD_AND_ENGINE_GATES",
  "source_authority": "current_RC34_gameplay_avatar_world_baseline_plus_RuinsCiv_identity_and_RC35_social_integrations",
  "version_name": "4.7.0-rc35-ruinsciv-v1",
  "engine": "Godot 4.7.2",
  "application_id": "$EXPECTED_PACKAGE",
  "target_sdk": 36,
  "architecture": "arm64-v8a",
  "avatar": "$CANONICAL_AVATAR",
  "avatar_sha256": "$AVATAR_SHA",
  "legacy_package_in_active_runtime": false,
  "legacy_public_brand_in_active_runtime": false,
  "legacy_humanoid_in_active_runtime": false,
  "legacy_humanoid_in_apk": false,
  "uploaded_visual16a_lineage_gate": "PASS",
  "uploaded_visual16a_families_in_apk": ["downtown","street","transport","interior","nature","furniture","ruins"],
  "standalone_local_auth": "PATCHED_AND_STATIC_GATED",
  "social_auth_google_discord_facebook": "PATCHED_AND_STATIC_GATED_LIVE_CREDENTIALS_PENDING",
  "google_play_games_identity": "NOT_YET_IMPLEMENTED_SEPARATE_NATIVE_LINK",
  "account_deletion_api_and_external_web_resource": "PATCHED_AND_STATIC_GATED",
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
