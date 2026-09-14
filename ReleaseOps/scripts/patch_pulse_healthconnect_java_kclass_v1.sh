#!/usr/bin/env bash
set -Eeuo pipefail

TARGET="${1:-/tmp/build_pulse_phone_baseline_v2.sh}"
test -s "$TARGET"

python3 - "$TARGET" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8")

import_anchor = "import java.util.Set;\n"
import_line = "import kotlin.jvm.JvmClassMappingKt;\n"
if import_line not in text:
    if import_anchor not in text:
        raise SystemExit("Pulse MainActivity import anchor missing")
    text = text.replace(import_anchor, import_anchor + import_line, 1)

records = [
    "ExerciseSessionRecord",
    "StepsRecord",
    "DistanceRecord",
    "TotalCaloriesBurnedRecord",
    "ActiveCaloriesBurnedRecord",
    "HeartRateRecord",
    "SleepSessionRecord",
    "WeightRecord",
    "BodyFatRecord",
]

for record in records:
    old = f"HealthPermission.getReadPermission({record}.class)"
    new = f"HealthPermission.getReadPermission(JvmClassMappingKt.getKotlinClass({record}.class))"
    if new in text:
        continue
    if old not in text:
        raise SystemExit(f"Expected Health Connect permission call missing for {record}")
    text = text.replace(old, new)

path.write_text(text, encoding="utf-8")
PY

grep -q 'import kotlin.jvm.JvmClassMappingKt;' "$TARGET"
for record in ExerciseSessionRecord StepsRecord DistanceRecord TotalCaloriesBurnedRecord ActiveCaloriesBurnedRecord HeartRateRecord SleepSessionRecord WeightRecord BodyFatRecord; do
  grep -q "HealthPermission.getReadPermission(JvmClassMappingKt.getKotlinClass(${record}.class))" "$TARGET"
done

echo 'THF_PULSE_HEALTHCONNECT_JAVA_KCLASS_PATCH=PASS'
