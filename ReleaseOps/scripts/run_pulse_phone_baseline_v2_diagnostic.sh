#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$HOME/thf-pulse-phone-baseline-v2"
OUT="$ROOT/out"
RUN_LOG="/tmp/thf-pulse-phone-baseline-v2-run.log"
BUILD_SCRIPT="/tmp/build_pulse_phone_baseline_v2.sh"

mkdir -p "$OUT"
: > "$RUN_LOG"

# androidx.health.connect HealthPermission is Kotlin-first and its Java signature
# expects KClass<? extends Record>. Keep the authoritative Pulse source immutable;
# patch only this isolated generated QA2 builder before it emits MainActivity.java.
python3 - "$BUILD_SCRIPT" <<'PY'
from pathlib import Path
import sys
p=Path(sys.argv[1])
s=p.read_text(encoding='utf-8')
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
p.write_text(s,encoding='utf-8')
PY

emit_diagnostics() {
  local rc="$1"
  mkdir -p "$OUT"
  {
    echo "THF_PULSE_PHONE_BASELINE_QA2_DIAGNOSTIC=1"
    echo "exit_code=$rc"
    echo "health_connect_java_kclass_bridge=APPLIED"
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
  echo "utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
} > "$OUT/DIAGNOSTIC.txt"
cp "$RUN_LOG" "$OUT/builder-run.log"
