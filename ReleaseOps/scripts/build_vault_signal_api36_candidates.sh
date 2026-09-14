#!/usr/bin/env bash
set -Eeuo pipefail

SDK="$HOME/thf-builder-rc16-build/android-sdk"
CACHE="$HOME/thf-builder-rc16-build/cache"
GVER=8.11.1
GBIN="$CACHE/gradle-dist-${GVER}/gradle-${GVER}/bin/gradle"
AAPT="$SDK/build-tools/36.0.0/aapt"
APKSIGNER="$SDK/build-tools/36.0.0/apksigner"
ROOT="$HOME/thf-vault-signal-api36-candidates-v1"
OVERLAY_ID="API_BASE_URL_JSON_ESCAPE_V1"
mkdir -p "$ROOT"
test -x "$GBIN"
test -x "$AAPT"

CURRENT_APP="bootstrap"
diagnose() {
  local rc=$?
  echo "THF_VAULT_SIGNAL_BUILD_FAILURE app=$CURRENT_APP rc=$rc" >&2
  if [ -d "$ROOT/$CURRENT_APP/out" ]; then
    for f in "$ROOT/$CURRENT_APP/out"/gradle-*.log; do
      [ -f "$f" ] || continue
      echo "===== $f (tail 220) =====" >&2
      tail -n 220 "$f" >&2 || true
    done
  fi
  if [ -d "$ROOT/$CURRENT_APP/work" ]; then
    echo "===== source layout (depth 4) =====" >&2
    find "$ROOT/$CURRENT_APP/work" -maxdepth 4 -type f | sort | head -n 240 >&2 || true
  fi
  exit "$rc"
}
trap diagnose ERR

build_one() {
  local app="$1" pkg="$2" src="$3" src_sha="$4"
  CURRENT_APP="$app"
  local work="$ROOT/$app/work" out="$ROOT/$app/out"
  rm -rf "$ROOT/$app"
  mkdir -p "$work" "$out"
  test -s "$src"
  local actual_src_sha
  actual_src_sha="$(sha256sum "$src" | awk '{print $1}')"
  test "$actual_src_sha" = "$src_sha"
  unzip -q "$src" -d "$work"

  local settings project gradle_file gradle_before_sha gradle_after_sha
  settings="$(find "$work" -maxdepth 6 -type f \( -name settings.gradle -o -name settings.gradle.kts \) | head -n1)"
  test -n "$settings"
  project="$(dirname "$settings")"
  gradle_file="$project/app/build.gradle"
  test -s "$gradle_file"
  gradle_before_sha="$(sha256sum "$gradle_file" | awk '{print $1}')"

  # The authoritative RC2 sources contain one malformed Groovy escaping expression
  # for API_BASE_URL. Repair only that exact semantic line in the extracted build
  # workspace. JsonOutput supplies a valid quoted Java String literal without
  # changing runtime URL semantics. The source ZIP itself remains untouched.
  python3 - "$gradle_file" <<'PY'
from pathlib import Path
import sys
p = Path(sys.argv[1])
lines = p.read_text(encoding="utf-8").splitlines(keepends=True)
idx = [i for i, line in enumerate(lines) if "buildConfigField" in line and "API_BASE_URL" in line and "baseUrl.replace" in line]
if len(idx) != 1:
    raise SystemExit(f"overlay target count must be exactly 1, got {len(idx)}")
i = idx[0]
indent = lines[i][:len(lines[i]) - len(lines[i].lstrip())]
newline = "\n" if lines[i].endswith("\n") else ""
lines[i] = indent + 'buildConfigField "String", "API_BASE_URL", groovy.json.JsonOutput.toJson(baseUrl)' + newline
p.write_text("".join(lines), encoding="utf-8")
PY
  gradle_after_sha="$(sha256sum "$gradle_file" | awk '{print $1}')"
  test "$gradle_before_sha" != "$gradle_after_sha"
  grep -Fq 'buildConfigField "String", "API_BASE_URL", groovy.json.JsonOutput.toJson(baseUrl)' "$gradle_file"
  echo "BUILD_APP=$app PROJECT=$project SOURCE_SHA=$actual_src_sha OVERLAY=$OVERLAY_ID BEFORE=$gradle_before_sha AFTER=$gradle_after_sha"
  cd "$project"

  export ANDROID_SDK_ROOT="$SDK" ANDROID_HOME="$SDK" GRADLE_USER_HOME="$ROOT/$app/gradle-home"
  export PATH="$SDK/platform-tools:$SDK/build-tools/36.0.0:$SDK/cmdline-tools/latest/bin:$PATH"
  mkdir -p "$GRADLE_USER_HOME"

  "$GBIN" --no-daemon --stacktrace :app:assembleDebug >"$out/gradle-debug.log" 2>&1
  local apk
  apk="$(find "$project/app/build/outputs/apk" -type f -name '*.apk' | sort | head -n1)"
  test -s "$apk"
  "$AAPT" dump badging "$apk" >"$out/badging.txt"

  local found_pkg target
  found_pkg="$(sed -n "s/^package: name='\([^']*\)'.*/\1/p" "$out/badging.txt" | head -n1)"
  target="$(sed -n "s/^targetSdkVersion:'\([^']*\)'.*/\1/p" "$out/badging.txt" | head -n1)"

  local variant="debug"
  if [ "$found_pkg" != "$pkg" ] || [ "$target" != "36" ]; then
    "$GBIN" --no-daemon --stacktrace :app:assembleRelease >"$out/gradle-release.log" 2>&1
    apk="$(find "$project/app/build/outputs/apk/release" -type f -name '*.apk' | sort | head -n1)"
    test -s "$apk"
    "$AAPT" dump badging "$apk" >"$out/badging.txt"
    found_pkg="$(sed -n "s/^package: name='\([^']*\)'.*/\1/p" "$out/badging.txt" | head -n1)"
    target="$(sed -n "s/^targetSdkVersion:'\([^']*\)'.*/\1/p" "$out/badging.txt" | head -n1)"
    variant="release"
  fi

  test "$found_pkg" = "$pkg"
  test "$target" = "36"

  local final="$out/THF-${app^^}-API36-EXACT-QA.apk"
  cp "$apk" "$final"
  local size apk_sha signed="FALSE" under="FAIL"
  size="$(stat -c %s "$final")"
  apk_sha="$(sha256sum "$final" | awk '{print $1}')"
  if [ "$size" -lt 104857600 ]; then under="PASS"; fi
  if [ -x "$APKSIGNER" ] && "$APKSIGNER" verify "$final" >/dev/null 2>&1; then signed="TRUE"; fi

  cat >"$out/EVIDENCE.txt" <<EOF
THF_${app^^}_API36_EXACT_QA=BUILT
source_path=$src
source_sha256=$actual_src_sha
build_overlay_id=$OVERLAY_ID
build_gradle_sha256_before=$gradle_before_sha
build_gradle_sha256_after=$gradle_after_sha
source_zip_mutated=FALSE
package=$found_pkg
targetSdk=$target
variant=$variant
apk_sha256=$apk_sha
apk_size_bytes=$size
under_100MiB=$under
apk_signature_verifies=$signed
physical_device_status=PENDING
network_release_ready=FALSE
final_or_play_ready=FALSE
production_signing_performed=FALSE
EOF
  cat "$out/EVIDENCE.txt"
  test "$under" = PASS
}

build_one vault com.topherofit.thf.vault \
  "$HOME/thf-apps-rc3-exact-candidate-v2/source/vault.zip" \
  7a2ba4236a0c42d2521fa2eb2c2d7108ceba0d2929ebdf68959a6eacbce4a793

build_one signal com.topherofit.thf.signal \
  "$HOME/thf-apps-rc3-exact-candidate-v2/source/signal.zip" \
  51d7ce44fed24f7490973bcc7e019a8430157c4d5bfa1541e7cb590b0b7957c0

trap - ERR
