#!/usr/bin/env bash
set -Eeuo pipefail

TARGET="${1:-/tmp/build_pulse_phone_baseline_v2.sh}"
test -s "$TARGET"

python3 - "$TARGET" <<'PY'
from pathlib import Path
import sys

p = Path(sys.argv[1])
s = p.read_text(encoding='utf-8')

replacements = {
'''String payload=new JSONObject().put("granted_count",granted.size()).put("requested_count",healthPermissions.size()).toString();''':
'''String payload;try{payload=new JSONObject().put("granted_count",granted.size()).put("requested_count",healthPermissions.size()).toString();}catch(Exception ignored){payload="{\\\"granted_count\\\":0,\\\"requested_count\\\":0}";}''',
'''return new JSONObject().put("status","ERROR").put("message",e.getClass().getSimpleName()).toString();''':
'''return "{\\\"status\\\":\\\"ERROR\\\",\\\"message\\\":\\\""+e.getClass().getSimpleName()+"\\\"}";''',
'''return new JSONObject().put("status","UNAVAILABLE").put("message",e.getClass().getSimpleName()).toString();''':
'''return "{\\\"status\\\":\\\"UNAVAILABLE\\\",\\\"message\\\":\\\""+e.getClass().getSimpleName()+"\\\"}";''',
'''return new JSONObject().put("status","INVALID").put("error",e.getClass().getSimpleName()).toString();''':
'''return "{\\\"status\\\":\\\"INVALID\\\",\\\"error\\\":\\\""+e.getClass().getSimpleName()+"\\\"}";''',
}

changed = 0
for old, new in replacements.items():
    if new in s:
        continue
    if old not in s:
        raise SystemExit('Expected generated JSONObject checked-exception anchor missing: ' + old[:80])
    s = s.replace(old, new)
    changed += 1

p.write_text(s, encoding='utf-8')
print(f'patched_groups={changed}')
PY

grep -Fq 'String payload;try{payload=new JSONObject().put("granted_count",granted.size())' "$TARGET"
grep -Fq 'return "{\"status\":\"ERROR\",\"message\":\""+e.getClass().getSimpleName()+"\"}";' "$TARGET"
grep -Fq 'return "{\"status\":\"UNAVAILABLE\",\"message\":\""+e.getClass().getSimpleName()+"\"}";' "$TARGET"
grep -Fq 'return "{\"status\":\"INVALID\",\"error\":\""+e.getClass().getSimpleName()+"\"}";' "$TARGET"
echo 'THF_PULSE_GENERATED_JSON_EXCEPTION_PATCH=PASS'
