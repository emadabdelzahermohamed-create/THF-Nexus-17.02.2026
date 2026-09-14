#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$HOME/thf-pulse-phone-baseline-v2"
OUT="$ROOT/out"
RUN_LOG="/tmp/thf-pulse-phone-baseline-v2-run.log"
BUILD_SCRIPT="/tmp/build_pulse_phone_baseline_v2.sh"

mkdir -p "$OUT"
: > "$RUN_LOG"

# Apply compile-compatibility fixes only to the isolated generated QA2 builder.
# The authoritative Pulse/Fitness source tree remains byte-for-byte immutable.
python3 - "$BUILD_SCRIPT" <<'PY'
from pathlib import Path
import sys
p=Path(sys.argv[1])
s=p.read_text(encoding='utf-8')

# AndroidX Health Connect is Kotlin-first: Java callers must provide KClass<Record>.
needle='import java.util.Set;'
if 'import kotlin.jvm.JvmClassMappingKt;' not in s:
    if needle not in s:
        raise SystemExit('Pulse QA2 Java import anchor missing')
    s=s.replace(needle, needle+'\nimport kotlin.jvm.JvmClassMappingKt;', 1)
records=[
'ExerciseSessionRecord','StepsRecord','DistanceRecord','TotalCaloriesBurnedRecord',
'ActiveCaloriesBurnedRecord','HeartRateRecord','SleepSessionRecord','WeightRecord','BodyFatRecord'
]
for record in records:
    old=f'HealthPermission.getReadPermission({record}.class)'
    new=f'HealthPermission.getReadPermission(JvmClassMappingKt.getKotlinClass({record}.class))'
    if old not in s and new not in s:
        raise SystemExit(f'Pulse QA2 Health Connect anchor missing: {record}')
    s=s.replace(old,new)

# JSONObject.put throws checked JSONException in Java. Route bridge serialization through
# a local fail-safe helper so JavascriptInterface/callback methods never leak it.
bridge_anchor='  final class PulseBridge {'
helper='''  private String safeJson(Object... kv){try{JSONObject o=new JSONObject();for(int i=0;i+1<kv.length;i+=2)o.put(String.valueOf(kv[i]),kv[i+1]);return o.toString();}catch(Exception ignored){return "{}";}}\n\n'''
if 'private String safeJson(Object... kv)' not in s:
    if bridge_anchor not in s:
        raise SystemExit('Pulse QA2 bridge anchor missing')
    s=s.replace(bridge_anchor, helper+bridge_anchor, 1)
repls={
'String payload=new JSONObject().put("granted_count",granted.size()).put("requested_count",healthPermissions.size()).toString();':
'String payload=safeJson("granted_count",granted.size(),"requested_count",healthPermissions.size());',
'return new JSONObject().put("status","ERROR").put("message",e.getClass().getSimpleName()).toString();':
'return safeJson("status","ERROR","message",e.getClass().getSimpleName());',
'return new JSONObject().put("status","UNAVAILABLE").put("message",e.getClass().getSimpleName()).toString();':
'return safeJson("status","UNAVAILABLE","message",e.getClass().getSimpleName());',
'if(end<start||!allowedMetric(metric))return new JSONObject().put("status","INVALID").toString();':
'if(end<start||!allowedMetric(metric))return safeJson("status","INVALID");',
'return new JSONObject().put("status",duplicate?"DUPLICATE":"ACCEPTED").put("dedupe_sha256",key).put("reward_authorized",false).toString();':
'return safeJson("status",duplicate?"DUPLICATE":"ACCEPTED","dedupe_sha256",key,"reward_authorized",false);',
'return new JSONObject().put("status","INVALID").put("error",e.getClass().getSimpleName()).toString();':
'return safeJson("status","INVALID","error",e.getClass().getSimpleName());'
}
for old,new in repls.items():
    if old not in s and new not in s:
        raise SystemExit('Pulse QA2 JSON bridge anchor missing: '+old[:72])
    s=s.replace(old,new)

# Fail closed if known unchecked serialization sites survive in the generated builder text.
for forbidden in [
    'String payload=new JSONObject().put("granted_count"',
    'catch(Exception e){return new JSONObject().put("status","ERROR")',
    'catch(Exception e){return new JSONObject().put("status","UNAVAILABLE")',
    'return new JSONObject().put("status",duplicate?"DUPLICATE":"ACCEPTED")',
    'return new JSONObject().put("status","INVALID").put("error"'
]:
    if forbidden in s:
        raise SystemExit('Pulse QA2 unchecked JSONObject serialization remains: '+forbidden)
p.write_text(s,encoding='utf-8')
PY

emit_diagnostics() {
  local rc="$1"
  mkdir -p "$OUT"
  {
    echo "THF_PULSE_PHONE_BASELINE_QA2_DIAGNOSTIC=1"
    echo "exit_code=$rc"
    echo "health_connect_java_kclass_bridge=APPLIED"
    echo "bridge_json_checked_exception_fix=APPLIED_FAIL_CLOSED"
    echo "utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "host=$(hostname)"
    echo "java_version_begin"
    java -version 2>&1 || true
    echo "java_version_end"
    echo "disk_begin"
    df -h "$HOME" 2>&1 || true
    echo "disk_end"
    echo "root_listing_begin"
    find "$ROOT" -maxdepth 3 -type f -printf '%p %s bytes\n' 2>/dev/null | sort || true
    echo "root_listing_end"
    echo "gradle_log_tail_begin"
    tail -n 240 "$OUT/gradle.log" 2>/dev/null || true
    echo "gradle_log_tail_end"
    echo "pytest_log_tail_begin"
    tail -n 120 "$OUT/pytest.log" 2>/dev/null || true
    echo "pytest_log_tail_end"
    echo "runner_log_tail_begin"
    tail -n 300 "$RUN_LOG" 2>/dev/null || true
    echo "runner_log_tail_end"
  } | tee "$OUT/DIAGNOSTIC.txt"
  cp "$RUN_LOG" "$OUT/builder-run.log" 2>/dev/null || true
}

set +e
bash -x "$BUILD_SCRIPT" > >(tee -a "$RUN_LOG") 2> >(tee -a "$RUN_LOG" >&2)
rc=$?
set -e

if (( rc != 0 )); then
  emit_diagnostics "$rc"
  exit "$rc"
fi

{
  echo "THF_PULSE_PHONE_BASELINE_QA2_DIAGNOSTIC=0"
  echo "exit_code=0"
  echo "health_connect_java_kclass_bridge=APPLIED"
  echo "bridge_json_checked_exception_fix=APPLIED_FAIL_CLOSED"
  echo "utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
} > "$OUT/DIAGNOSTIC.txt"
cp "$RUN_LOG" "$OUT/builder-run.log"
