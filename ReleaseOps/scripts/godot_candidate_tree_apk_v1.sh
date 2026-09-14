#!/usr/bin/env bash
set -Eeuo pipefail

: "${PROJECT_ROOT:?PROJECT_ROOT required}"
: "${EXPECTED_PACKAGE:?EXPECTED_PACKAGE required}"
: "${OUTPUT_APK:?OUTPUT_APK required}"
: "${ANDROID_SDK_ROOT:?ANDROID_SDK_ROOT required}"
: "${GODOT_BIN:?GODOT_BIN required}"
: "${TEMPLATE_ROOT:?TEMPLATE_ROOT required}"

PROJECT_ROOT="$(cd "$PROJECT_ROOT" && pwd)"
OUT_DIR="$(dirname "$OUTPUT_APK")"; mkdir -p "$OUT_DIR"
PROJECT_FILE="$PROJECT_ROOT/project.godot"
PRESETS="$PROJECT_ROOT/export_presets.cfg"
test -f "$PROJECT_FILE"; test -f "$PRESETS"; test -x "$GODOT_BIN"
PRESET="$(sed -n 's/^name="\([^"]*\)"/\1/p' "$PRESETS" | head -1)"; test -n "$PRESET"

# Disposable candidate only: force installable APK format without modifying canonical archive.
python3 - "$PRESETS" <<'PY'
import pathlib,sys
p=pathlib.Path(sys.argv[1]);s=p.read_text()
if 'gradle_build/export_format=1' in s:s=s.replace('gradle_build/export_format=1','gradle_build/export_format=0',1)
elif 'gradle_build/export_format=0' not in s: raise SystemExit('missing Android export format marker')
p.write_text(s)
PY

BT="$(find "$ANDROID_SDK_ROOT/build-tools" -mindepth 1 -maxdepth 1 -type d | sort -V | tail -1)"
AAPT="$BT/aapt"; APKSIGNER="$BT/apksigner"; ZIPALIGN="$BT/zipalign"
test -x "$AAPT"; test -x "$APKSIGNER"; test -x "$ZIPALIGN"
JAVA_HOME_REAL="$(dirname "$(dirname "$(readlink -f "$(command -v javac)")")")"
ISO="$(mktemp -d)"; trap 'rm -rf "$ISO"' EXIT
mkdir -p "$ISO/.config/godot" "$ISO/.local/share/godot"
ln -s "$(dirname "$TEMPLATE_ROOT")" "$ISO/.local/share/godot/export_templates"
printf '%s\n' '[gd_resource type="EditorSettings" format=3]' '' '[resource]' \
  "export/android/android_sdk_path = \"$ANDROID_SDK_ROOT\"" \
  "export/android/java_sdk_path = \"$JAVA_HOME_REAL\"" > "$ISO/.config/godot/editor_settings-4.7.tres"
export HOME="$ISO" JAVA_HOME="$JAVA_HOME_REAL" ANDROID_HOME="$ANDROID_SDK_ROOT" ANDROID_SDK_ROOT
export PATH="$JAVA_HOME_REAL/bin:$ANDROID_SDK_ROOT/platform-tools:$BT:$PATH"

timeout 15m "$GODOT_BIN" --headless --editor --path "$PROJECT_ROOT" --quit --verbose > "$OUT_DIR/import.log" 2>&1
timeout 5m "$GODOT_BIN" --headless --path "$PROJECT_ROOT" --quit-after 30 --verbose > "$OUT_DIR/boot.log" 2>&1
set +e
timeout 5m "$GODOT_BIN" --headless --editor --path "$PROJECT_ROOT" --install-android-build-template --quit > "$OUT_DIR/template.log" 2>&1
set -e
if [ ! -f "$PROJECT_ROOT/android/build/gradlew" ]; then
  test -f "$TEMPLATE_ROOT/android_source.zip"
  python3 - "$TEMPLATE_ROOT/android_source.zip" "$PROJECT_ROOT/android/build" <<'PY'
import pathlib,shutil,sys,zipfile
src,dst=pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]).resolve();dst.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(src) as z:
 for i in z.infolist():
  r=pathlib.PurePosixPath(i.filename)
  if r.is_absolute() or '..' in r.parts: raise SystemExit('unsafe template member')
  t=(dst/pathlib.Path(*r.parts)).resolve()
  if t!=dst and dst not in t.parents: raise SystemExit('template escape')
  if i.is_dir(): t.mkdir(parents=True,exist_ok=True);continue
  t.parent.mkdir(parents=True,exist_ok=True)
  with z.open(i) as a,open(t,'wb') as b:shutil.copyfileobj(a,b)
PY
  chmod +x "$PROJECT_ROOT/android/build/gradlew"; printf '%s\n' '4.7.2.stable' > "$PROJECT_ROOT/android/.build_version"
fi

timeout 20m "$GODOT_BIN" --headless --path "$PROJECT_ROOT" --export-debug "$PRESET" "$OUTPUT_APK" > "$OUT_DIR/export.log" 2>&1
test -s "$OUTPUT_APK"; unzip -tq "$OUTPUT_APK" >/dev/null

if ! "$APKSIGNER" verify --verbose "$OUTPUT_APK" > "$OUT_DIR/apksigner-initial.txt" 2>&1; then
  ALIGNED="$OUT_DIR/aligned-unsigned.apk"; "$ZIPALIGN" -f -p 4 "$OUTPUT_APK" "$ALIGNED"
  KS="$ISO/qa-only.keystore"
  keytool -genkeypair -noprompt -keystore "$KS" -storepass android -alias qa -keypass android -dname 'CN=THF QA,O=TopHeroFit,C=EG' -keyalg RSA -keysize 2048 -validity 30 >/dev/null 2>&1
  "$APKSIGNER" sign --ks "$KS" --ks-key-alias qa --ks-pass pass:android --key-pass pass:android --out "$OUTPUT_APK.signed" "$ALIGNED"
  mv "$OUTPUT_APK.signed" "$OUTPUT_APK"; rm -f "$ALIGNED" "$KS"
fi
"$APKSIGNER" verify --verbose "$OUTPUT_APK" > "$OUT_DIR/apksigner.txt" 2>&1
"$ZIPALIGN" -c -p 4 "$OUTPUT_APK" > "$OUT_DIR/zipalign.txt" 2>&1
BADGING="$($AAPT dump badging "$OUTPUT_APK")"; printf '%s\n' "$BADGING" > "$OUT_DIR/badging.txt"
grep -q "package: name='$EXPECTED_PACKAGE'" <<<"$BADGING"
grep -q "targetSdkVersion:'36'" <<<"$BADGING"

python3 - "$OUTPUT_APK" <<'PY'
import sys,zipfile
with zipfile.ZipFile(sys.argv[1]) as z:
 names=z.namelist()
 if any(n.startswith('res/') and n.endswith('.import') for n in names): raise SystemExit('Godot import sidecars leaked into Android resources')
 if not any(n.startswith('assets/') or n.endswith('.pck') or n.endswith('project.binary') for n in names): raise SystemExit('missing Godot project payload')
PY
APK_SHA="$(sha256sum "$OUTPUT_APK"|awk '{print $1}')"
printf 'status=PASS\napk_sha256=%s\npackage=%s\ntarget_sdk=36\npayload=PASS\nqa_signing_only=true\nproduction_signing=false\ndevice_status=PENDING\nfinal_status=NOT_FINAL\n' "$APK_SHA" "$EXPECTED_PACKAGE" | tee "$OUT_DIR/TRUTH.txt"
