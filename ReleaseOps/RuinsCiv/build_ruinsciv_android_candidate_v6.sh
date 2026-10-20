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
GODOT="${GODOT_BIN:-}"
if [[ -z "$GODOT" ]]; then for x in godot4.7.2 godot-4.7.2 godot4 godot; do command -v "$x" >/dev/null 2>&1 && { GODOT="$(command -v "$x")"; break; }; done; fi
if [[ -z "$GODOT" ]]; then
 ZIP="$TOOLS/godot.zip"; BIN="$TOOLS/Godot_v${GODOT_TAG}_linux.x86_64"
 if [[ ! -x "$BIN" ]]; then curl -fL --retry 3 --connect-timeout 20 -o "$ZIP" "https://github.com/godotengine/godot/releases/download/$GODOT_TAG/Godot_v${GODOT_TAG}_linux.x86_64.zip"; unzip -o "$ZIP" -d "$TOOLS"; chmod +x "$BIN"; fi
 GODOT="$BIN"
fi
"$GODOT" --version | tee "$OUT/godot_version.txt"; grep -q '^4\.7\.2' "$OUT/godot_version.txt" || exit 62
if [[ ! -f "$TEMPLATES/android_debug.apk" || ! -f "$TEMPLATES/android_release.apk" ]]; then TPZ="$TOOLS/export_templates.tpz"; TMP="$TOOLS/templates-unpack"; rm -rf "$TMP"; mkdir -p "$TMP" "$TEMPLATES"; curl -fL --retry 3 --connect-timeout 20 -o "$TPZ" "https://github.com/godotengine/godot/releases/download/$GODOT_TAG/Godot_v${GODOT_TAG}_export_templates.tpz"; unzip -o "$TPZ" -d "$TMP"; cp -a "$TMP/templates/." "$TEMPLATES/"; fi
[[ -f "$TEMPLATES/android_debug.apk" ]] || exit 66
JAVA_BIN="${JAVA_HOME:+$JAVA_HOME/bin/java}"; [[ -x "$JAVA_BIN" ]] || JAVA_BIN="$(command -v java || true)"; [[ -n "$JAVA_BIN" ]] || exit 67; "$JAVA_BIN" -version 2>&1 | tee "$OUT/java_version.txt"
SDK="${ANDROID_HOME:-${ANDROID_SDK_ROOT:-$HOME/Android/Sdk}}"; SDKMANAGER=""
for s in "$SDK/cmdline-tools/latest/bin/sdkmanager" "$SDK/cmdline-tools/bin/sdkmanager"; do [[ -x "$s" ]] && { SDKMANAGER="$s"; break; }; done
if [[ -z "$SDKMANAGER" ]]; then CMDROOT="$HOME/.cache/thf-android-cmdline-tools"; mkdir -p "$CMDROOT" "$SDK/cmdline-tools"; CTZIP="$CMDROOT/commandlinetools-linux.zip"; curl -fL --retry 3 --connect-timeout 20 -o "$CTZIP" "https://dl.google.com/android/repository/commandlinetools-linux-13114758_latest.zip"; rm -rf "$CMDROOT/unpack" "$SDK/cmdline-tools/latest"; mkdir -p "$CMDROOT/unpack" "$SDK/cmdline-tools/latest"; unzip -q -o "$CTZIP" -d "$CMDROOT/unpack"; cp -a "$CMDROOT/unpack/cmdline-tools/." "$SDK/cmdline-tools/latest/"; SDKMANAGER="$SDK/cmdline-tools/latest/bin/sdkmanager"; fi
export ANDROID_HOME="$SDK" ANDROID_SDK_ROOT="$SDK"; export PATH="$SDK/platform-tools:$SDK/cmdline-tools/latest/bin:$PATH"; yes | "$SDKMANAGER" --sdk_root="$SDK" --licenses >/dev/null || true
"$SDKMANAGER" --sdk_root="$SDK" platform-tools 'platforms;android-36' 'build-tools;36.0.0'
[[ -f "$SDK/platforms/android-36/android.jar" && -x "$SDK/platform-tools/adb" && -d "$SDK/build-tools/36.0.0" ]] || exit 68
printf 'android_sdk=%s\nandroid_jar=%s\nbuild_tools=36.0.0\n' "$SDK" "$SDK/platforms/android-36/android.jar" | tee "$OUT/android_toolchain.txt"
# Use the canonical preset name already present in RC34. Allow an explicit override, but never assume a generic "Android" preset.
PRESET="${RUINSCIV_ANDROID_PRESET:-}"
if [[ -z "$PRESET" ]]; then PRESET="$(awk -F'=' '/^name=/{gsub(/^"|"$/, "", $2); print $2; exit}' "$DST/export_presets.cfg")"; fi
[[ -n "$PRESET" ]] || { echo BLOCKER_ANDROID_EXPORT_PRESET_NOT_FOUND; exit 72; }
printf 'preset=%s\n' "$PRESET" | tee "$OUT/export_preset.txt"
"$GODOT" --headless --path "$DST" --editor --quit-after 2
"$GODOT" --headless --path "$DST" --export-debug "$PRESET" "$APK"
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
EOF
cat "$OUT/CANDIDATE.txt"
