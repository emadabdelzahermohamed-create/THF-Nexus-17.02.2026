#!/usr/bin/env bash
set -Eeuo pipefail

TARGET="${1:-/tmp/build_vault_signal_api36_candidates.sh}"
test -s "$TARGET"

python3 - "$TARGET" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8")
old = "  grep -Fq 'res/drawable/ic_thf_launcher.xml' \"$out/apk-files.txt\"\n"
new = "  # aapt2 may flatten/rename compiled resource entry paths (for example res/MD.xml).\n  # Validate the launcher path reported by aapt badging against the APK archive, while\n  # separately requiring the canonical source vector before compilation.\n  test -s \"$project/app/src/main/res/drawable/ic_thf_launcher.xml\"\n  grep -Fxq \"$app_icon\" \"$out/apk-files.txt\"\n"
if new in text:
    print("compiled icon gate already patched")
elif old in text:
    text = text.replace(old, new, 1)
    path.write_text(text, encoding="utf-8")
else:
    raise SystemExit("expected stale compiled launcher icon gate not found")
PY

grep -Fq 'grep -Fxq "$app_icon" "$out/apk-files.txt"' "$TARGET"
grep -Fq 'test -s "$project/app/src/main/res/drawable/ic_thf_launcher.xml"' "$TARGET"
! grep -Fq "grep -Fq 'res/drawable/ic_thf_launcher.xml' \"\$out/apk-files.txt\"" "$TARGET"
echo 'THF_VAULT_SIGNAL_COMPILED_ICON_GATE_PATCH=PASS'
