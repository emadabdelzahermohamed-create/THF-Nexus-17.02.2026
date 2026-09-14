#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$HOME/thf-pulse-phone-baseline-v2"
OUT="$ROOT/out"
RUN_LOG="/tmp/thf-pulse-phone-baseline-v2-run.log"
BUILD_SCRIPT="/tmp/build_pulse_phone_baseline_v2.sh"

mkdir -p "$OUT"
: > "$RUN_LOG"

emit_diagnostics() {
  local rc="$1"
  mkdir -p "$OUT"
  {
    echo "THF_PULSE_PHONE_BASELINE_QA2_DIAGNOSTIC=1"
    echo "exit_code=$rc"
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
  echo "utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
} > "$OUT/DIAGNOSTIC.txt"
cp "$RUN_LOG" "$OUT/builder-run.log"
