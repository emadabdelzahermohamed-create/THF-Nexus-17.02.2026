#!/usr/bin/env bash
set -Eeuo pipefail

TARGET="${1:-/tmp/build_vault_signal_canonical_native_v2.sh}"
test -s "$TARGET"

python3 - "$TARGET" <<'PY'
from pathlib import Path
import sys

p=Path(sys.argv[1])
s=p.read_text(encoding='utf-8')
old="""icon_anchor='  test -n \"$app_icon\"\\n  test -n \"$launcher\"\\n  grep -Fq \\\'res/drawable/ic_thf_launcher.xml\\\' \"$out/apk-files.txt\"\\n'\nif src.count(icon_anchor) != 1:\n    raise SystemExit('icon validation anchor drift')\nicon_new='''  test -n \"$launcher\"\\n  grep -Fq 'res/drawable/ic_thf_launcher.xml' \"$out/apk-files.txt\"\\n  if [ -z \"$app_icon\" ]; then\\n    app_icon='res/drawable/ic_thf_launcher.xml'\\n  fi\\n  test -n \"$app_icon\"\\n  echo \"APK_METADATA app=$app package=$found_pkg targetSdk=$target versionCode=$version_code versionName=$version_name label=$app_label icon=$app_icon launcher=$launcher\"\\n'''\nsrc=src.replace(icon_anchor, icon_new)\n"""
new="""# The base builder validates the canonical source vector and then verifies the\n# actual compiled icon path reported by aapt badging. aapt2 is free to rename\n# compiled XML resources (for example res/MD.xml), so never require the source\n# pathname to survive inside the APK.\nicon_anchor_new='  test -n \"$app_icon\"\\n  test -n \"$launcher\"\\n  # aapt2 may flatten/rename compiled resource entry paths (for example res/MD.xml).\\n  # Validate the launcher path reported by aapt badging against the APK archive, while\\n  # separately requiring the canonical source vector before compilation.\\n  test -s \"$project/app/src/main/res/drawable/ic_thf_launcher.xml\"\\n  grep -Fxq \"$app_icon\" \"$out/apk-files.txt\"\\n'\nicon_anchor_old='  test -n \"$app_icon\"\\n  test -n \"$launcher\"\\n  grep -Fq \\\'res/drawable/ic_thf_launcher.xml\\\' \"$out/apk-files.txt\"\\n'\nif src.count(icon_anchor_new) == 1:\n    icon_anchor=icon_anchor_new\nelif src.count(icon_anchor_old) == 1:\n    icon_anchor=icon_anchor_old\nelse:\n    raise SystemExit('icon validation anchor drift')\nicon_new='''  test -n \"$app_icon\"\\n  test -n \"$launcher\"\\n  test -s \"$project/app/src/main/res/drawable/ic_thf_launcher.xml\"\\n  if ! grep -Fxq \"$app_icon\" \"$out/apk-files.txt\"; then\\n    echo \"APK_ICON_FAIL app=$app aapt_icon=$app_icon\" >&2\\n    return 75\\n  fi\\n  echo \"APK_METADATA app=$app package=$found_pkg targetSdk=$target versionCode=$version_code versionName=$version_name label=$app_label icon=$app_icon launcher=$launcher\"\\n'''\nsrc=src.replace(icon_anchor, icon_new)\n"""
if new in s:
    print('canonical icon anchor already patched')
elif old in s:
    p.write_text(s.replace(old,new,1),encoding='utf-8')
else:
    raise SystemExit('canonical icon generator block not found')
PY

grep -Fq 'icon_anchor_new=' "$TARGET"
grep -Fq 'APK_ICON_FAIL app=$app aapt_icon=$app_icon' "$TARGET"
echo 'THF_VAULT_SIGNAL_CANONICAL_ICON_ANCHOR_PATCH=PASS'
