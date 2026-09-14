#!/usr/bin/env bash
set -Eeuo pipefail

SDK="$HOME/thf-builder-rc16-build/android-sdk"
CACHE="$HOME/thf-builder-rc16-build/cache"
GVER=8.11.1
GBIN="$CACHE/gradle-dist-${GVER}/gradle-${GVER}/bin/gradle"
AAPT="$SDK/build-tools/36.0.0/aapt"
APKSIGNER="$SDK/build-tools/36.0.0/apksigner"
ROOT="$HOME/thf-vault-signal-api36-candidates-v1"
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

  local settings project
  settings="$(find "$work" -maxdepth 6 -type f \( -name settings.gradle -o -name settings.gradle.kts \) | head -n1)"
  test -n "$settings"
  project="$(dirname "$settings")"
  echo "BUILD_APP=$app PROJECT=$project SOURCE_SHA=$actual_src_sha"
  cd "$project"

  export ANDROID_SDK_ROOT="$SDK" ANDROID_HOME="$SDK" GRADLE_USER_HOME="$ROOT/$app/gradle-home"
  export PATH="$SDK/platform-tools:$SDK/build-tools/36.0.0:$SDK/cmdline-tools/latest/bin:$PATH"
  mkdir -p "$GRADLE_USER_HOME"

  # The exact sources use Android Gradle Plugin 8.13.0. Permit repository resolution
  # here; the resulting APK is still accepted only after exact package/API/SHA checks.
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
