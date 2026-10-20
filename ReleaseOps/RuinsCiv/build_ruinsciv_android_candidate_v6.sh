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

# Keep this toolchain user-local so Wave/Fitness projects are not mutated.
GODOT="${GODOT_BIN:-}"
if [[ -z "$GODOT" ]]; then
  for x in godot4.7.2 godot-4.7.2 godot4 godot; do command -v "$x" >/dev/null 2>&1 && { GODOT="$(command -v "$x")"; break; }; done
fi
if [[ -z "$GODOT" ]]; then
  ZIP="$TOOLS/godot.zip"
  BIN="$TOOLS/Godot_v${GODOT_TAG}_linux.x86_64"
  if [[ ! -x "$BIN" ]]; then
    command -v curl >/dev/null 2>&1 || { echo BLOCKER_CURL_NOT_FOUND; exit 64; }
    command -v unzip >/dev/null 2>&1 || { echo BLOCKER_UNZIP_NOT_FOUND; exit 65; }
    curl -fL --retry 3 --connect-timeout 20 -o "$ZIP" "https://github.com/godotengine/godot/releases/download/$GODOT_TAG/Godot_v${GODOT_TAG}_linux.x86_64.zip"
    unzip -o "$ZIP" -d "$TOOLS"
    chmod +x "$BIN"
  fi
  GODOT="$BIN"
fi
"$GODOT" --version | tee "$OUT/godot_version.txt"
grep -q '^4\.7\.2' "$OUT/godot_version.txt" || { echo BLOCKER_GODOT_VERSION_NOT_4_7_2; exit 62; }

# Exact matching official export templates.
if [[ ! -f "$TEMPLATES/android_debug.apk" || ! -f "$TEMPLATES/android_release.apk" ]]; then
  TPZ="$TOOLS/export_templates.tpz"
  TMP="$TOOLS/templates-unpack"
  rm -rf "$TMP"; mkdir -p "$TMP" "$TEMPLATES"
  curl -fL --retry 3 --connect-timeout 20 -o "$TPZ" "https://github.com/godotengine/godot/releases/download/$GODOT_TAG/Godot_v${GODOT_TAG}_export_templates.tpz"
  unzip -o "$TPZ" -d "$TMP"
  cp -a "$TMP/templates/." "$TEMPLATES/"
fi
[[ -f "$TEMPLATES/android_debug.apk" ]] || { echo BLOCKER_ANDROID_EXPORT_TEMPLATE_MISSING; exit 66; }

# Verify Android/JDK prerequisites without mutating system packages.
JAVA_BIN="${JAVA_HOME:+$JAVA_HOME/bin/java}"
if [[ -z "$JAVA_BIN" || ! -x "$JAVA_BIN" ]]; then JAVA_BIN="$(command -v java || true)"; fi
[[ -n "$JAVA_BIN" ]] || { echo BLOCKER_JAVA_NOT_FOUND; exit 67; }
"$JAVA_BIN" -version 2>&1 | tee "$OUT/java_version.txt"
SDK="${ANDROID_HOME:-${ANDROID_SDK_ROOT:-$HOME/Android/Sdk}}"
[[ -d "$SDK/platforms/android-36" ]] || { echo "BLOCKER_ANDROID_API36_NOT_FOUND sdk=$SDK"; exit 68; }
[[ -d "$SDK/platform-tools" ]] || { echo "BLOCKER_ANDROID_PLATFORM_TOOLS_NOT_FOUND sdk=$SDK"; exit 69; }
printf 'android_sdk=%s\n' "$SDK" | tee "$OUT/android_toolchain.txt"

PRESET="${RUINSCIV_ANDROID_PRESET:-Android}"
"$GODOT" --headless --path "$DST" --editor --quit-after 2
"$GODOT" --headless --path "$DST" --export-debug "$PRESET" "$APK"
[[ -s "$APK" ]] || { echo BLOCKER_APK_NOT_CREATED; exit 63; }
sha256sum "$APK" | tee "$OUT/SHA256SUMS.txt"
SIZE=$(stat -c %s "$APK")
VC=$(grep -E '^version/code=' "$DST/export_presets.cfg" | head -1 | cut -d= -f2- | tr -d '"' || true)
VN=$(grep -E '^version/name=' "$DST/export_presets.cfg" | head -1 | cut -d= -f2- | tr -d '"' || true)
SRC=$(git -C "$DST" rev-parse HEAD 2>/dev/null || printf UNKNOWN)
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
