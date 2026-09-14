#!/usr/bin/env bash
set -Eeuo pipefail

: "${PROJECT_ROOT:?PROJECT_ROOT required}"
: "${EXPECTED_PACKAGE:?EXPECTED_PACKAGE required}"
: "${OUTPUT_AAB:?OUTPUT_AAB required}"
: "${ANDROID_SDK_ROOT:?ANDROID_SDK_ROOT required}"
: "${GODOT_BIN:?GODOT_BIN required}"
: "${TEMPLATE_ROOT:?TEMPLATE_ROOT required}"

PROJECT_ROOT="$(cd "$PROJECT_ROOT" && pwd)"
OUT_DIR="$(dirname "$OUTPUT_AAB")"; mkdir -p "$OUT_DIR"
PROJECT_FILE="$PROJECT_ROOT/project.godot"
PRESETS="$PROJECT_ROOT/export_presets.cfg"
test -f "$PROJECT_FILE"; test -f "$PRESETS"; test -x "$GODOT_BIN"
PRESET="$(sed -n 's/^name="\([^"]*\)"/\1/p' "$PRESETS" | head -1)"; test -n "$PRESET"

# Disposable candidate only. Canonical source archive is never modified.
python3 - "$PRESETS" <<'PY'
import pathlib,sys
p=pathlib.Path(sys.argv[1]); s=p.read_text()
if 'gradle_build/export_format=0' in s:
    s=s.replace('gradle_build/export_format=0','gradle_build/export_format=1',1)
elif 'gradle_build/export_format=1' not in s:
    raise SystemExit('missing Android export format marker')
p.write_text(s)
PY

BT="$(find "$ANDROID_SDK_ROOT/build-tools" -mindepth 1 -maxdepth 1 -type d | sort -V | tail -1)"
JAVA_HOME_REAL="$(dirname "$(dirname "$(readlink -f "$(command -v javac)")")")"
ISO="$(mktemp -d)"; trap 'rm -rf "$ISO"' EXIT
mkdir -p "$ISO/.config/godot" "$ISO/.local/share/godot"
ln -s "$(dirname "$TEMPLATE_ROOT")" "$ISO/.local/share/godot/export_templates"
printf '%s\n' '[gd_resource type="EditorSettings" format=3]' '' '[resource]' \
  "export/android/android_sdk_path = \"$ANDROID_SDK_ROOT\"" \
  "export/android/java_sdk_path = \"$JAVA_HOME_REAL\"" > "$ISO/.config/godot/editor_settings-4.7.tres"
export HOME="$ISO" JAVA_HOME="$JAVA_HOME_REAL" ANDROID_HOME="$ANDROID_SDK_ROOT" ANDROID_SDK_ROOT
export PATH="$JAVA_HOME_REAL/bin:$ANDROID_SDK_ROOT/platform-tools:$BT:$PATH"

timeout 15m "$GODOT_BIN" --headless --editor --path "$PROJECT_ROOT" --quit --verbose > "$OUT_DIR/aab-import.log" 2>&1
timeout 5m "$GODOT_BIN" --headless --path "$PROJECT_ROOT" --quit-after 30 --verbose > "$OUT_DIR/aab-boot.log" 2>&1
set +e
timeout 5m "$GODOT_BIN" --headless --editor --path "$PROJECT_ROOT" --install-android-build-template --quit > "$OUT_DIR/aab-template.log" 2>&1
set -e
if [ ! -f "$PROJECT_ROOT/android/build/gradlew" ]; then
  test -f "$TEMPLATE_ROOT/android_source.zip"
  python3 - "$TEMPLATE_ROOT/android_source.zip" "$PROJECT_ROOT/android/build" <<'PY'
import pathlib,shutil,sys,zipfile
src,dst=pathlib.Path(sys.argv[1]),pathlib.Path(sys.argv[2]).resolve(); dst.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(src) as z:
    for i in z.infolist():
        r=pathlib.PurePosixPath(i.filename)
        if r.is_absolute() or '..' in r.parts: raise SystemExit('unsafe template member')
        t=(dst/pathlib.Path(*r.parts)).resolve()
        if t!=dst and dst not in t.parents: raise SystemExit('template escape')
        if i.is_dir(): t.mkdir(parents=True,exist_ok=True); continue
        t.parent.mkdir(parents=True,exist_ok=True)
        with z.open(i) as a,open(t,'wb') as b: shutil.copyfileobj(a,b)
PY
  chmod +x "$PROJECT_ROOT/android/build/gradlew"; printf '%s\n' '4.7.2.stable' > "$PROJECT_ROOT/android/.build_version"
fi

timeout 25m "$GODOT_BIN" --headless --path "$PROJECT_ROOT" --export-debug "$PRESET" "$OUTPUT_AAB" > "$OUT_DIR/aab-export.log" 2>&1
test -s "$OUTPUT_AAB"; unzip -tq "$OUTPUT_AAB" >/dev/null

if grep -Eqi 'SCRIPT ERROR|Parse Error|Parser Error|Failed to load script|Invalid call|Invalid get index|Invalid set index' "$OUT_DIR/aab-import.log" "$OUT_DIR/aab-boot.log" "$OUT_DIR/aab-export.log"; then
  grep -Ein 'SCRIPT ERROR|Parse Error|Parser Error|Failed to load script|Invalid call|Invalid get index|Invalid set index' "$OUT_DIR/aab-import.log" "$OUT_DIR/aab-boot.log" "$OUT_DIR/aab-export.log" | head -100 >&2
  exit 93
fi

python3 - "$OUTPUT_AAB" "$EXPECTED_PACKAGE" <<'PY'
import sys,zipfile
p,pkg=sys.argv[1:]
with zipfile.ZipFile(p) as z:
    names=z.namelist()
    if not any(n.endswith('BundleConfig.pb') for n in names): raise SystemExit('missing BundleConfig.pb')
    if not any(n.endswith('manifest/AndroidManifest.xml') for n in names): raise SystemExit('missing base manifest')
    if not any('lib/arm64-v8a/libgodot_android.so' in n for n in names): raise SystemExit('missing arm64 Godot runtime')
    if not any('/assets/' in n or n.startswith('base/assets/') for n in names): raise SystemExit('missing packaged game assets')
    if any(n.endswith('.import') and '/res/' in n for n in names): raise SystemExit('Godot import sidecars leaked into Android resources')
print('bundle_structure=PASS')
PY
AAB_SHA="$(sha256sum "$OUTPUT_AAB"|awk '{print $1}')"
SIZE="$(stat -c %s "$OUTPUT_AAB")"
printf 'status=PASS\naab_sha256=%s\naab_size_bytes=%s\npackage=%s\ntarget_sdk_expected=36\npayload=PASS\nqa_signing_only=true\nproduction_signing=false\ndevice_status=PENDING\nfinal_status=NOT_FINAL\n' "$AAB_SHA" "$SIZE" "$EXPECTED_PACKAGE" | tee "$OUT_DIR/AAB_TRUTH.txt"
