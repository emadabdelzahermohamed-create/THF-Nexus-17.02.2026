#!/usr/bin/env bash
set -Eeuo pipefail

SDK="$HOME/thf-builder-rc16-build/android-sdk"
CACHE="$HOME/thf-builder-rc16-build/cache"
GVER=8.13
GRADLE_SHA256=dccb1612e69e36aa7f52082be0d820a27f90c1c7c58c7ab4e9df2eed1f3f7f65
GDIST="$CACHE/gradle-dist-${GVER}"
GBIN="$GDIST/gradle-${GVER}/bin/gradle"
AAPT="$SDK/build-tools/36.0.0/aapt"
APKSIGNER="$SDK/build-tools/36.0.0/apksigner"
ZIPALIGN="$SDK/build-tools/36.0.0/zipalign"
ROOT="$HOME/thf-vault-signal-api36-candidates-v1"
OVERLAY_ID="BUILD_CONFIG_URL_JSON_ESCAPE_V2"
mkdir -p "$ROOT" "$CACHE"
test -x "$AAPT"
test -x "$ZIPALIGN"

ensure_gradle() {
  if [ -x "$GBIN" ]; then
    test "$("$GBIN" --version | sed -n 's/^Gradle \([0-9.]*\)$/\1/p' | sed -n '1p')" = "$GVER"
    return
  fi
  local zip="$CACHE/gradle-${GVER}-bin.zip"
  rm -f "$zip"
  curl --fail --location --silent --show-error --proto '=https' --tlsv1.2 \
    "https://services.gradle.org/distributions/gradle-${GVER}-bin.zip" -o "$zip"
  test "$(sha256sum "$zip" | awk '{print $1}')" = "$GRADLE_SHA256"
  rm -rf "$GDIST"
  mkdir -p "$GDIST"
  unzip -q "$zip" -d "$GDIST"
  rm -f "$zip"
  test -x "$GBIN"
  test "$("$GBIN" --version | sed -n 's/^Gradle \([0-9.]*\)$/\1/p' | sed -n '1p')" = "$GVER"
}
ensure_gradle

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
    find "$ROOT/$CURRENT_APP/work" -maxdepth 4 -type f | sort | sed -n '1,240p' >&2 || true
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

  local settings project gradle_file gradle_before_sha gradle_after_sha overlay_map
  settings="$(find "$work" -maxdepth 6 -type f \( -name settings.gradle -o -name settings.gradle.kts \) -print -quit)"
  test -n "$settings"
  project="$(dirname "$settings")"
  gradle_file="$project/app/build.gradle"
  overlay_map="$out/build-overlay-map.txt"
  test -s "$gradle_file"
  gradle_before_sha="$(sha256sum "$gradle_file" | awk '{print $1}')"

  # Repair only malformed URL buildConfigField expressions generated with the
  # repeated <variable>.replace('\\', ...) quoting pattern. Each repaired field
  # preserves its original field name and source variable. The authoritative ZIP
  # is never modified; before/after Gradle hashes and the repair map are evidence.
  python3 - "$gradle_file" "$overlay_map" <<'PY'
from pathlib import Path
import re, sys
p = Path(sys.argv[1])
map_path = Path(sys.argv[2])
lines = p.read_text(encoding="utf-8").splitlines(keepends=True)
repairs = []
field_re = re.compile(r"buildConfigField\s+['\"]String['\"]\s*,\s*['\"]([^'\"]+)['\"]")
var_re = re.compile(r"\+\s*([A-Za-z_][A-Za-z0-9_]*)\.replace\(")
for i, line in enumerate(lines):
    if "buildConfigField" not in line or ".replace(" not in line:
        continue
    fm = field_re.search(line)
    vm = var_re.search(line)
    if not fm or not vm:
        continue
    field, var = fm.group(1), vm.group(1)
    indent = line[:len(line) - len(line.lstrip())]
    newline = "\n" if line.endswith("\n") else ""
    lines[i] = indent + f'buildConfigField "String", "{field}", groovy.json.JsonOutput.toJson({var})' + newline
    repairs.append((i + 1, field, var))
if not repairs:
    print("=== build.gradle first 80 lines ===", file=sys.stderr)
    for n, line in enumerate(lines[:80], 1):
        print(f"{n:03d}: {line.rstrip()}", file=sys.stderr)
    raise SystemExit("overlay repair count must be >= 1")
p.write_text("".join(lines), encoding="utf-8")
map_path.write_text("".join(f"line={n} field={field} variable={var}\n" for n, field, var in repairs), encoding="utf-8")
print(f"overlay_repairs={len(repairs)}")
for n, field, var in repairs:
    print(f"overlay_line={n} field={field} variable={var}")
PY
  gradle_after_sha="$(sha256sum "$gradle_file" | awk '{print $1}')"
  test "$gradle_before_sha" != "$gradle_after_sha"
  test -s "$overlay_map"
  ! grep -Eq "buildConfigField.*\.replace\(" "$gradle_file"
  echo "BUILD_APP=$app PROJECT=$project SOURCE_SHA=$actual_src_sha OVERLAY=$OVERLAY_ID BEFORE=$gradle_before_sha AFTER=$gradle_after_sha GRADLE=$GVER"
  cat "$overlay_map"
  cd "$project"

  export ANDROID_SDK_ROOT="$SDK" ANDROID_HOME="$SDK" GRADLE_USER_HOME="$ROOT/$app/gradle-home"
  export PATH="$SDK/platform-tools:$SDK/build-tools/36.0.0:$SDK/cmdline-tools/latest/bin:$PATH"
  mkdir -p "$GRADLE_USER_HOME"

  "$GBIN" --no-daemon --stacktrace :app:assembleDebug >"$out/gradle-debug.log" 2>&1
  local apk
  apk="$(find "$project/app/build/outputs/apk" -type f -name '*.apk' -print -quit)"
  test -s "$apk"
  "$AAPT" dump badging "$apk" >"$out/badging.txt"

  local found_pkg target
  found_pkg="$(sed -n "s/^package: name='\([^']*\)'.*/\1/p" "$out/badging.txt" | sed -n '1p')"
  target="$(sed -n "s/^targetSdkVersion:'\([^']*\)'.*/\1/p" "$out/badging.txt" | sed -n '1p')"

  local variant="debug"
  if [ "$found_pkg" != "$pkg" ] || [ "$target" != "36" ]; then
    "$GBIN" --no-daemon --stacktrace :app:assembleRelease >"$out/gradle-release.log" 2>&1
    apk="$(find "$project/app/build/outputs/apk/release" -type f -name '*.apk' -print -quit)"
    test -s "$apk"
    "$AAPT" dump badging "$apk" >"$out/badging.txt"
    found_pkg="$(sed -n "s/^package: name='\([^']*\)'.*/\1/p" "$out/badging.txt" | sed -n '1p')"
    target="$(sed -n "s/^targetSdkVersion:'\([^']*\)'.*/\1/p" "$out/badging.txt" | sed -n '1p')"
    variant="release"
  fi

  test "$found_pkg" = "$pkg"
  test "$target" = "36"

  local final="$out/THF-${app^^}-API36-EXACT-QA.apk"
  cp "$apk" "$final"
  "$AAPT" dump badging "$final" >"$out/badging.txt"
  "$AAPT" list "$final" >"$out/apk-files.txt"
  "$ZIPALIGN" -c -P 16 -v 4 "$final" >"$out/zipalign.txt"

  local size apk_sha signed="FALSE" version_code version_name app_label app_icon launcher abi_payload
  size="$(stat -c %s "$final")"
  apk_sha="$(sha256sum "$final" | awk '{print $1}')"
  version_code="$(sed -n "s/^package: name='[^']*' versionCode='\([^']*\)'.*/\1/p" "$out/badging.txt" | sed -n '1p')"
  version_name="$(sed -n "s/^package:.* versionName='\([^']*\)'.*/\1/p" "$out/badging.txt" | sed -n '1p')"
  app_label="$(sed -n "s/^application-label:'\([^']*\)'.*/\1/p" "$out/badging.txt" | sed -n '1p')"
  app_icon="$(sed -n "s/^application:.* icon='\([^']*\)'.*/\1/p" "$out/badging.txt" | sed -n '1p')"
  launcher="$(sed -n "s/^launchable-activity: name='\([^']*\)'.*/\1/p" "$out/badging.txt" | sed -n '1p')"
  test -n "$version_code"
  test -n "$version_name"
  test -n "$app_label"
  test -n "$app_icon"
  test -n "$launcher"
  grep -Fq 'res/drawable/ic_thf_launcher.xml' "$out/apk-files.txt"

  abi_payload="JAVA_ONLY_NO_NATIVE_LIBS"
  if grep -q '^lib/' "$out/apk-files.txt"; then
    abi_payload="$(sed -n 's#^lib/\([^/]*\)/.*#\1#p' "$out/apk-files.txt" | sort -u | paste -sd, -)"
    case ",$abi_payload," in
      *,arm64-v8a,*) : ;;
      *) echo "Unexpected native ABI payload: $abi_payload" >&2; return 71 ;;
    esac
  fi

  if [ -x "$APKSIGNER" ] && "$APKSIGNER" verify --verbose "$final" >"$out/apksigner.txt" 2>&1; then signed="TRUE"; fi
  test "$signed" = TRUE

  local expected_label
  if [ "$app" = vault ]; then expected_label="THF Wallet"; else expected_label="THF Publisher"; fi
  test "$app_label" = "$expected_label"

  cat >"$out/EVIDENCE.txt" <<EOF
THF_${app^^}_API36_EXACT_QA=BUILT
source_path=$src
source_sha256=$actual_src_sha
build_tool=gradle-$GVER
build_tool_distribution_sha256=$GRADLE_SHA256
build_overlay_id=$OVERLAY_ID
build_overlay_repairs=$(wc -l < "$overlay_map")
build_overlay_map_sha256=$(sha256sum "$overlay_map" | awk '{print $1}')
build_gradle_sha256_before=$gradle_before_sha
build_gradle_sha256_after=$gradle_after_sha
source_zip_mutated=FALSE
package=$found_pkg
versionCode=$version_code
versionName=$version_name
targetSdk=$target
variant=$variant
application_label=$app_label
application_icon=$app_icon
launcher_activity=$launcher
abi_payload=$abi_payload
apk_sha256=$apk_sha
apk_size_bytes=$size
artifact_size_policy=TELEMETRY_ONLY_NO_ARBITRARY_CAP
apk_signature_verifies=$signed
production_signing_performed=FALSE
zipalign_4byte_and_16k_native_alignment=PASS
apk_archive_integrity=PASS
installability_preflight=PASS_PACKAGE_PARSE_SIGNATURE_ZIPALIGN_ONLY
physical_install_status=PENDING_REAL_PHONE
physical_device_status=PENDING
network_release_ready=FALSE
final_or_play_ready=FALSE
EOF
  cat "$out/EVIDENCE.txt"
}

build_one vault com.topherofit.thf.vault \
  "$HOME/thf-apps-rc3-exact-candidate-v2/source/vault.zip" \
  7a2ba4236a0c42d2521fa2eb2c2d7108ceba0d2929ebdf68959a6eacbce4a793

build_one signal com.topherofit.thf.signal \
  "$HOME/thf-apps-rc3-exact-candidate-v2/source/signal.zip" \
  51d7ce44fed24f7490973bcc7e019a8430157c4d5bfa1541e7cb590b0b7957c0

trap - ERR
