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
# Build each CI run in a fresh, caller-selected root. A shared fixed root can race
# with a previous Gradle process while rm -rf traverses gradle-home, which is not
# release evidence and must never make build truth nondeterministic.
root_old='ROOT="$HOME/thf-vault-signal-api36-candidates-v1"'
root_new='ROOT="${THF_NATIVE_RUN_ROOT:-$HOME/thf-vault-signal-native-candidates-v2}"'
if src.count(root_old) != 1:
    raise SystemExit('builder root anchor drift')
src=src.replace(root_old, root_new)
anchor='  cat "$overlay_map"\n  cd "$project"\n'
if src.count(anchor) != 1:
    raise SystemExit('builder anchor drift')
insert='''  cat "$overlay_map"\n  python3 /tmp/nativeize_vault_signal_candidate.py "$project" "$app" "$pkg" | tee "$out/native-overlay.txt"\n  test -s "$out/native-overlay.txt"\n  grep -q 'native_overlay=THF_NATIVE_REAL_FUNCTION_V2' "$out/native-overlay.txt"\n  test -s "$project/NATIVE_SOURCE_PROVENANCE_V2.json"\n  python3 - "$project/NATIVE_SOURCE_PROVENANCE_V2.json" "$pkg" "$app" <<'PROV'\nimport json,sys\np=json.load(open(sys.argv[1],encoding='utf-8'))\nassert p['schema']=='THF_NATIVE_REAL_FUNCTION_SOURCE_PROVENANCE_V2'\nassert p['overlay_id']=='THF_NATIVE_REAL_FUNCTION_V2'\nassert p['package']==sys.argv[2] and p['app']==sys.argv[3]\nassert p['pass_handoff_contract']=='thfpass://handoff/v1'\nassert p['remote_truth_policy']=='FAIL_CLOSED_NO_FAKE_REMOTE_STATE'\nassert p['production_authority'] is False\nassert p['physical_device_pass'] is False\nassert p['final_or_play_ready'] is False\nfor k in ('generated_manifest_sha256','generated_main_activity_sha256'):\n    assert len(p[k])==64 and all(c in '0123456789abcdef' for c in p[k])\nPROV\n  cp "$project/NATIVE_SOURCE_PROVENANCE_V2.json" "$out/native-source-provenance-v2.json"\n  cd "$project"\n'''
src=src.replace(anchor, insert)
src=src.replace('OVERLAY_ID="BUILD_CONFIG_URL_JSON_ESCAPE_V2"','OVERLAY_ID="BUILD_CONFIG_URL_JSON_ESCAPE_V2+THF_NATIVE_REAL_FUNCTION_V2"')
needle='build_overlay_map_sha256=$(sha256sum "$overlay_map" | awk \'{print $1}\')\n'
if src.count(needle) != 1:
    raise SystemExit('evidence anchor drift')
src=src.replace(needle, needle + 'native_overlay_id=THF_NATIVE_REAL_FUNCTION_V2\nnative_overlay_evidence_sha256=$(sha256sum "$out/native-overlay.txt" | awk \'{print $1}\')\nnative_source_provenance_sha256=$(sha256sum "$out/native-source-provenance-v2.json" | awk \'{print $1}\')\n')
Path(sys.argv[2]).write_text(src, encoding='utf-8')
PY
chmod +x "$PATCHED"
bash -n "$PATCHED"
exec "$PATCHED"
