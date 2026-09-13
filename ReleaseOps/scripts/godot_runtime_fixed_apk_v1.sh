#!/usr/bin/env bash
set -Eeuo pipefail

: "${FULL_NAME:?FULL_NAME required}"
: "${FULL_SHA:?FULL_SHA required}"
: "${INPUT_REL:?INPUT_REL required}"
: "${ROOT_REL:?ROOT_REL required}"
: "${EXPECTED_PACKAGE:?EXPECTED_PACKAGE required}"
: "${OUTPUT_BASENAME:?OUTPUT_BASENAME required}"

BASE="$HOME"
SRC="$BASE/$INPUT_REL/$FULL_NAME"
ROOT="$BASE/$ROOT_REL"
WORK="$ROOT/work"
OUT="$ROOT/out"
GODOT="$BASE/thf-tools/godot/4.7.2-stable/godot"
SDK="$BASE/thf-builder-rc16-build/android-sdk"
TEMPLATE_ROOT="$BASE/.local/share/godot/export_templates/4.7.2.stable"
PHASE=init

on_err() {
  rc=$?
  echo "GODOT_RUNTIME_FIXED_GATE=FAIL phase=$PHASE rc=$rc" >&2
  for f in "$OUT/import.log" "$OUT/boot.log" "$OUT/template.log" "$OUT/export.log"; do
    if [ -f "$f" ]; then
      echo "===== $(basename "$f") tail =====" >&2
      tail -n 120 "$f" >&2 || true
    fi
  done
  exit "$rc"
}
trap on_err ERR

rm -rf "$ROOT"
mkdir -p "$WORK" "$OUT"
test -f "$SRC"
PHASE=canonical_sha_before
echo "$FULL_SHA  $SRC" | sha256sum -c -

PHASE=safe_extract
python3 - "$SRC" "$WORK" <<'PY'
import pathlib, shutil, sys, zipfile
src, dst = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]).resolve()
with zipfile.ZipFile(src) as z:
    for info in z.infolist():
        rel = pathlib.PurePosixPath(info.filename)
        if rel.is_absolute() or '..' in rel.parts:
            raise SystemExit(f'unsafe zip member: {info.filename}')
        target = (dst / pathlib.Path(*rel.parts)).resolve()
        if target != dst and dst not in target.parents:
            raise SystemExit(f'zip escape: {info.filename}')
        if info.is_dir():
            target.mkdir(parents=True, exist_ok=True)
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        with z.open(info) as r, open(target, 'wb') as w:
            shutil.copyfileobj(r, w)
PY

PHASE=project_discovery
PG="$(find "$WORK" -maxdepth 4 -type f -name project.godot -print -quit)"
test -n "$PG"
PROJECT="$(dirname "$PG")"
test -f "$PROJECT/export_presets.cfg"
PRESET="$(sed -n 's/^name="\([^"]*\)"/\1/p' "$PROJECT/export_presets.cfg" | head -1)"
test -n "$PRESET"
echo "PROJECT=$PROJECT PRESET=$PRESET"

PHASE=ephemeral_export_format
python3 - "$PROJECT/export_presets.cfg" <<'PY'
import pathlib, sys
p = pathlib.Path(sys.argv[1])
s = p.read_text()
if 'gradle_build/export_format=1' in s:
    s = s.replace('gradle_build/export_format=1', 'gradle_build/export_format=0', 1)
elif 'gradle_build/export_format=0' not in s:
    raise SystemExit('missing Android export format marker')
p.write_text(s)
PY

PHASE=toolchain_preflight
test -x "$GODOT"
test -x "$SDK/build-tools/36.0.0/aapt2"
test -f "$SDK/platforms/android-36/android.jar"
test -f "$TEMPLATE_ROOT/android_source.zip"
JAVA_HOME_REAL="$(dirname "$(dirname "$(readlink -f "$(command -v javac)")")")"
ISO="$ROOT/godot-home"
mkdir -p "$ISO/.config/godot" "$ISO/.local/share/godot"
ln -s "$BASE/.local/share/godot/export_templates" "$ISO/.local/share/godot/export_templates"
printf '%s\n' '[gd_resource format=3]' '' '[resource]' \
  "export/android/android_sdk_path = \"$SDK\"" \
  "export/android/java_sdk_path = \"$JAVA_HOME_REAL\"" \
  > "$ISO/.config/godot/editor_settings-4.7.tres"
export HOME="$ISO" ANDROID_HOME="$SDK" ANDROID_SDK_ROOT="$SDK" JAVA_HOME="$JAVA_HOME_REAL"
export PATH="$JAVA_HOME_REAL/bin:$SDK/platform-tools:$SDK/build-tools/36.0.0:$PATH"

PHASE=godot_import
timeout 15m "$GODOT" --headless --editor --path "$PROJECT" --quit --verbose >"$OUT/import.log" 2>&1
PHASE=godot_boot
timeout 5m "$GODOT" --headless --path "$PROJECT" --quit-after 30 --verbose >"$OUT/boot.log" 2>&1
PHASE=android_template_install
set +e
timeout 5m "$GODOT" --headless --editor --path "$PROJECT" --install-android-build-template --quit >"$OUT/template.log" 2>&1
template_rc=$?
set -e
echo "ANDROID_TEMPLATE_INSTALL_RC=$template_rc"

PHASE=android_template_fallback
if [ ! -f "$PROJECT/android/build/gradlew" ]; then
  python3 - "$TEMPLATE_ROOT/android_source.zip" "$PROJECT/android/build" <<'PY'
import pathlib, shutil, sys, zipfile
src, dst = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]).resolve()
dst.mkdir(parents=True, exist_ok=True)
with zipfile.ZipFile(src) as z:
    for info in z.infolist():
        rel = pathlib.PurePosixPath(info.filename)
        if rel.is_absolute() or '..' in rel.parts:
            raise SystemExit(f'unsafe template member: {info.filename}')
        target = (dst / pathlib.Path(*rel.parts)).resolve()
        if target != dst and dst not in target.parents:
            raise SystemExit(f'template escape: {info.filename}')
        if info.is_dir():
            target.mkdir(parents=True, exist_ok=True)
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        with z.open(info) as r, open(target, 'wb') as w:
            shutil.copyfileobj(r, w)
PY
  chmod +x "$PROJECT/android/build/gradlew"
  printf '%s\n' '4.7.2.stable' > "$PROJECT/android/.build_version"
fi

PHASE=godot_android_export
APK="$OUT/$OUTPUT_BASENAME"
timeout 20m "$GODOT" --headless --path "$PROJECT" --export-debug "$PRESET" "$APK" >"$OUT/export.log" 2>&1
test -s "$APK"

PHASE=apk_verification
APKSIGNER="$SDK/build-tools/36.0.0/apksigner"
ZIPALIGN="$SDK/build-tools/36.0.0/zipalign"
AAPT2="$SDK/build-tools/36.0.0/aapt2"
"$APKSIGNER" verify --verbose "$APK" >"$OUT/apksigner.txt" 2>&1
"$ZIPALIGN" -c -v 4 "$APK" >"$OUT/zipalign.txt" 2>&1
"$AAPT2" dump badging "$APK" >"$OUT/badging.txt"
grep -q "package: name='$EXPECTED_PACKAGE'" "$OUT/badging.txt"
grep -q "targetSdkVersion:'36'" "$OUT/badging.txt"

PHASE=godot_payload_guard
ASSET_COUNT="$(unzip -Z1 "$APK" | grep -c '^assets/' || true)"
test "$ASSET_COUNT" -gt 0
if unzip -Z1 "$APK" | grep -Eq '(^|/)[^/]+\.pck$|^assets/'; then
  PAYLOAD=PASS
else
  PAYLOAD=FAIL
fi
test "$PAYLOAD" = PASS

PHASE=canonical_sha_after
APK_SHA="$(sha256sum "$APK" | awk '{print $1}')"
test "$(sha256sum "$SRC" | awk '{print $1}')" = "$FULL_SHA"
printf 'status=PASS\ncanonical_sha256=%s\napk_sha256=%s\nasset_count=%s\ngodot_payload=%s\npackage=%s\ntarget_sdk=36\nproduction_signing=false\ncanonical_archive_mutated=false\nwave_untouched=true\n' \
  "$FULL_SHA" "$APK_SHA" "$ASSET_COUNT" "$PAYLOAD" "$EXPECTED_PACKAGE" | tee "$OUT/TRUTH.txt"
PHASE=complete
echo GODOT_RUNTIME_FIXED_GATE=PASS
