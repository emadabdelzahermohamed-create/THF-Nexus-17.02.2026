#!/usr/bin/env bash
set -Eeuo pipefail
DST="${RUINSCIV_CANDIDATE:-$HOME/ruinsciv-candidate}"
OUT="${RUINSCIV_BUILD_OUT:-$HOME/ruinsciv-build-evidence-v6}"
APK="$OUT/RuinsCiv-v6-arm64.apk"
PACKAGE=com.topherofit.ruins.civ
mkdir -p "$OUT"
exec > >(tee "$OUT/build_trace.log") 2>&1
trap 'rc=$?; printf "RUINSCIV_V6_FAIL rc=%s line=%s command=%q\n" "$rc" "$LINENO" "$BASH_COMMAND" | tee "$OUT/build_failure.txt"; exit "$rc"' ERR
[[ -f "$DST/project.godot" ]]
[[ -f "$DST/export_presets.cfg" ]]
# Public candidate identity; never ship the phoneqa suffix.
sed -Ei 's#^(package/unique_name|package/name)="[^"]*"#\1="'"$PACKAGE"'"#' "$DST/export_presets.cfg"
# Prefer installed Godot 4.7.2 binary; deterministic failure if unavailable.
GODOT="${GODOT_BIN:-}"
if [[ -z "$GODOT" ]]; then
  for x in godot4.7.2 godot-4.7.2 godot4 godot; do command -v "$x" >/dev/null 2>&1 && { GODOT="$(command -v "$x")"; break; }; done
fi
[[ -n "$GODOT" ]] || { echo 'BLOCKER_GODOT_4_7_2_BINARY_NOT_FOUND'; exit 61; }
"$GODOT" --version | tee "$OUT/godot_version.txt"
grep -q '^4\.7\.2' "$OUT/godot_version.txt" || { echo 'BLOCKER_GODOT_VERSION_NOT_4_7_2'; exit 62; }
PRESET="${RUINSCIV_ANDROID_PRESET:-Android}"
"$GODOT" --headless --path "$DST" --editor --quit-after 2
"$GODOT" --headless --path "$DST" --export-debug "$PRESET" "$APK"
[[ -s "$APK" ]] || { echo 'BLOCKER_APK_NOT_CREATED'; exit 63; }
sha256sum "$APK" | tee "$OUT/SHA256SUMS.txt"
SIZE=$(stat -c %s "$APK")
VC=$(grep -E '^version/code=' "$DST/export_presets.cfg" | head -1 | cut -d= -f2- | tr -d '"' || true)
VN=$(grep -E '^version/name=' "$DST/export_presets.cfg" | head -1 | cut -d= -f2- | tr -d '"' || true)
cat > "$OUT/CANDIDATE.txt" <<EOF
candidate=RuinsCiv-v6-arm64.apk
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
