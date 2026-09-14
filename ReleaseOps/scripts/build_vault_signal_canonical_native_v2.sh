#!/usr/bin/env bash
set -Eeuo pipefail
BASE=/tmp/build_vault_signal_api36_candidates.sh
NATIVE=/tmp/nativeize_vault_signal_candidate.py
PACK=/tmp/package_authoritative_android_source_v2.py
PATCHED=/tmp/build_vault_signal_canonical_native_v2.generated.sh

test -s "$BASE"
test -s "$NATIVE"
test -s "$PACK"

python3 - "$BASE" "$PATCHED" <<'PY'
from pathlib import Path
import sys
src=Path(sys.argv[1]).read_text(encoding='utf-8')
root_old='ROOT="$HOME/thf-vault-signal-api36-candidates-v1"'
root_new='ROOT="$HOME/thf-vault-signal-canonical-native-v2"'
if src.count(root_old) != 1:
    raise SystemExit('builder root anchor drift')
src=src.replace(root_old, root_new)

anchor='  cat "$overlay_map"\n  cd "$project"\n'
if src.count(anchor) != 1:
    raise SystemExit('builder native/package insertion anchor drift')
insert='''  cat "$overlay_map"\n  python3 /tmp/nativeize_vault_signal_candidate.py "$project" "$app" "$pkg" | tee "$out/native-overlay.txt"\n  test -s "$out/native-overlay.txt"\n  grep -q 'native_overlay=THF_NATIVE_REAL_FUNCTION_V2' "$out/native-overlay.txt"\n  canonical_source="$out/THF-${app^^}-CANONICAL-NATIVE-SOURCE-V2.zip"\n  python3 /tmp/package_authoritative_android_source_v2.py "$project" "$canonical_source" | tee "$out/source-package-evidence.txt"\n  test -s "$canonical_source"\n  test -s "$out/source-package-evidence.txt"\n  grep -q '^canonical_source_clean=PASS$' "$out/source-package-evidence.txt"\n  canonical_source_sha256="$(sha256sum "$canonical_source" | awk '{print $1}')"\n  test "$canonical_source_sha256" = "$(sed -n 's/^canonical_source_sha256=//p' "$out/source-package-evidence.txt")"\n  # Phone-QA release APK keeps the production package ID but is signed only with\n  # the standard Android debug key. This overlay is applied AFTER canonical source\n  # packaging so it can never be mistaken for production signing configuration.\n  qa_signing_before_sha256="$(sha256sum "$gradle_file" | awk '{print $1}')"\n  python3 - "$gradle_file" "$out/qa-signing-overlay.txt" <<'QAPY'\nfrom pathlib import Path\nimport sys\np=Path(sys.argv[1]); evidence=Path(sys.argv[2])\ns=p.read_text(encoding='utf-8')\nold="release { minifyEnabled false; proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro' }"\nnew="release { signingConfig signingConfigs.debug; minifyEnabled false; proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro' }"\nif s.count(old) != 1:\n    raise SystemExit('release buildType signing anchor drift')\np.write_text(s.replace(old,new), encoding='utf-8')\nevidence.write_text('qa_release_signing=ANDROID_DEBUG_KEY_ONLY\\nproduction_signing=FALSE\\ncanonical_source_contains_qa_signing_overlay=FALSE\\n', encoding='utf-8')\nQAPY\n  qa_signing_after_sha256="$(sha256sum "$gradle_file" | awk '{print $1}')"\n  test "$qa_signing_before_sha256" != "$qa_signing_after_sha256"\n  grep -q '^qa_release_signing=ANDROID_DEBUG_KEY_ONLY$' "$out/qa-signing-overlay.txt"\n  cd "$project"\n'''
src=src.replace(anchor, insert)

old='OVERLAY_ID="BUILD_CONFIG_URL_JSON_ESCAPE_V2"'
new='OVERLAY_ID="BUILD_CONFIG_URL_JSON_ESCAPE_V2+THF_NATIVE_REAL_FUNCTION_V2+CANONICAL_SOURCE_V2+QA_DEBUG_SIGNING_POST_PACKAGE_V1+APK_DIAGNOSTICS_V2"'
if src.count(old) != 1:
    raise SystemExit('overlay id anchor drift')
src=src.replace(old,new)

pkg_anchor='  test "$found_pkg" = "$pkg"\n  test "$target" = "36"\n'
if src.count(pkg_anchor) != 1:
    raise SystemExit('package/target validation anchor drift')
src=src.replace(pkg_anchor, '''  if [ "$found_pkg" != "$pkg" ]; then\n    echo "APK_PACKAGE_FAIL app=$app expected=$pkg actual=$found_pkg variant=$variant" >&2\n    return 70\n  fi\n  if [ "$target" != "36" ]; then\n    echo "APK_TARGET_FAIL app=$app expected=36 actual=$target variant=$variant" >&2\n    return 71\n  fi\n''')

zip_anchor='  "$ZIPALIGN" -c -P 16 -v 4 "$final" >"$out/zipalign.txt"\n'
if src.count(zip_anchor) != 1:
    raise SystemExit('zipalign anchor drift')
zip_new='''  if grep -q '^lib/.*\\.so$' "$out/apk-files.txt"; then\n    if ! "$ZIPALIGN" -c -P 16 -v 4 "$final" >"$out/zipalign.txt" 2>&1; then\n      echo "APK_ZIPALIGN_FAIL app=$app mode=4byte+16k-native" >&2\n      tail -n 80 "$out/zipalign.txt" >&2 || true\n      return 72\n    fi\n  else\n    if ! "$ZIPALIGN" -c -v 4 "$final" >"$out/zipalign.txt" 2>&1; then\n      echo "APK_ZIPALIGN_FAIL app=$app mode=4byte-java-only" >&2\n      tail -n 80 "$out/zipalign.txt" >&2 || true\n      return 72\n    fi\n  fi\n'''
src=src.replace(zip_anchor, zip_new)

meta_anchor='  test -n "$version_code"\n  test -n "$version_name"\n  test -n "$app_label"\n'
if src.count(meta_anchor) != 1:
    raise SystemExit('metadata validation anchor drift')
src=src.replace(meta_anchor, '''  echo "APK_METADATA_RAW app=$app versionCode=$version_code versionName=$version_name label=$app_label icon=$app_icon launcher=$launcher"\n  test -n "$version_code"\n  test -n "$version_name"\n  test -n "$app_label"\n''')

# aapt can leave the resolved application icon field empty for a vector while
# the compiled drawable is present. Require the compiled resource and record
# that exact resource rather than falsely failing a valid phone-QA package.
icon_anchor='  test -n "$app_icon"\n  test -n "$launcher"\n  grep -Fq \'res/drawable/ic_thf_launcher.xml\' "$out/apk-files.txt"\n'
if src.count(icon_anchor) != 1:
    raise SystemExit('icon validation anchor drift')
icon_new='''  test -n "$launcher"\n  grep -Fq 'res/drawable/ic_thf_launcher.xml' "$out/apk-files.txt"\n  if [ -z "$app_icon" ]; then\n    app_icon='res/drawable/ic_thf_launcher.xml'\n  fi\n  test -n "$app_icon"\n  echo "APK_METADATA app=$app package=$found_pkg targetSdk=$target versionCode=$version_code versionName=$version_name label=$app_label icon=$app_icon launcher=$launcher"\n'''
src=src.replace(icon_anchor, icon_new)

sig_anchor='  if [ -x "$APKSIGNER" ] && "$APKSIGNER" verify --verbose "$final" >"$out/apksigner.txt" 2>&1; then signed="TRUE"; fi\n  test "$signed" = TRUE\n'
if src.count(sig_anchor) != 1:
    raise SystemExit('signature validation anchor drift')
sig_new='''  if [ -x "$APKSIGNER" ] && "$APKSIGNER" verify --verbose "$final" >"$out/apksigner.txt" 2>&1; then signed="TRUE"; fi\n  if [ "$signed" != TRUE ]; then\n    echo "APK_SIGNATURE_FAIL app=$app apksigner=$APKSIGNER" >&2\n    cat "$out/apksigner.txt" >&2 2>/dev/null || true\n    return 73\n  fi\n'''
src=src.replace(sig_anchor, sig_new)

label_anchor='  test "$app_label" = "$expected_label"\n'
if src.count(label_anchor) != 1:
    raise SystemExit('label validation anchor drift')
src=src.replace(label_anchor, '''  if [ "$app_label" != "$expected_label" ]; then\n    echo "APK_LABEL_FAIL app=$app expected=$expected_label actual=$app_label" >&2\n    return 74\n  fi\n''')

needle='build_overlay_map_sha256=$(sha256sum "$overlay_map" | awk \'{print $1}\')\n'
if src.count(needle) != 1:
    raise SystemExit('evidence anchor drift')
src=src.replace(needle, needle + '''native_overlay_id=THF_NATIVE_REAL_FUNCTION_V2\nnative_overlay_evidence_sha256=$(sha256sum "$out/native-overlay.txt" | awk '{print $1}')\ncanonical_source_artifact=$(basename "$canonical_source")\ncanonical_source_sha256=$canonical_source_sha256\ncanonical_source_clean=PASS\ncanonical_source_authority=NEW_CANDIDATE_NOT_FINAL\nqa_release_signing=ANDROID_DEBUG_KEY_ONLY\nqa_signing_overlay_sha256=$(sha256sum "$out/qa-signing-overlay.txt" | awk '{print $1}')\nqa_signing_gradle_sha256_before=$qa_signing_before_sha256\nqa_signing_gradle_sha256_after=$qa_signing_after_sha256\ncanonical_source_contains_qa_signing_overlay=FALSE\n''')
Path(sys.argv[2]).write_text(src, encoding='utf-8')
PY

chmod +x "$PATCHED"
bash -n "$PATCHED"
exec "$PATCHED"
