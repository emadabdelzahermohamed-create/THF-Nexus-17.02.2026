#!/usr/bin/env bash
set -Eeuo pipefail
BASE=/tmp/build_vault_signal_api36_candidates.sh
NATIVE=/tmp/nativeize_vault_signal_candidate.py
PATCHED=/tmp/build_vault_signal_native_candidates_v1.generated.sh
test -s "$BASE"
test -s "$NATIVE"
python3 - "$BASE" "$PATCHED" <<'PY'
from pathlib import Path
import sys
src=Path(sys.argv[1]).read_text(encoding='utf-8')
anchor='  cat "$overlay_map"\n  cd "$project"\n'
if src.count(anchor) != 1:
    raise SystemExit('builder anchor drift')
insert='''  cat "$overlay_map"\n  python3 /tmp/nativeize_vault_signal_candidate.py "$project" "$app" "$pkg" | tee "$out/native-overlay.txt"\n  test -s "$out/native-overlay.txt"\n  grep -q 'native_overlay=THF_NATIVE_REAL_FUNCTION_V1' "$out/native-overlay.txt"\n  cd "$project"\n'''
src=src.replace(anchor, insert)
src=src.replace('OVERLAY_ID="BUILD_CONFIG_URL_JSON_ESCAPE_V2"','OVERLAY_ID="BUILD_CONFIG_URL_JSON_ESCAPE_V2+THF_NATIVE_REAL_FUNCTION_V1"')
needle='build_overlay_map_sha256=$(sha256sum "$overlay_map" | awk \'{print $1}\')\n'
if src.count(needle) != 1:
    raise SystemExit('evidence anchor drift')
src=src.replace(needle, needle + 'native_overlay_id=THF_NATIVE_REAL_FUNCTION_V1\nnative_overlay_evidence_sha256=$(sha256sum "$out/native-overlay.txt" | awk \'{print $1}\')\n')
Path(sys.argv[2]).write_text(src, encoding='utf-8')
PY
chmod +x "$PATCHED"
bash -n "$PATCHED"
exec "$PATCHED"
