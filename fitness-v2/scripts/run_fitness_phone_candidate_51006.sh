#!/usr/bin/env bash
set -Eeuo pipefail

REPOSITORY="emadabdelzahermohamed-create/THF-Nexus-17.02.2026"
RUN_ID="${THF_FITNESS_51006_RUN_ID:-${1:-}}"
ARTIFACT="fitness-v2-51006-package-gate"
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

if [[ -z "$RUN_ID" ]]; then
  echo "Pass the exact successful GitHub Actions run id as arg1 or THF_FITNESS_51006_RUN_ID" >&2
  exit 2
fi
if [[ $# -gt 0 ]]; then shift; fi
for command_name in gh adb sha256sum mktemp; do
  command -v "$command_name" >/dev/null || { echo "Missing command: $command_name" >&2; exit 2; }
done
WORK_DIR="$(mktemp -d)"
cleanup() { rm -rf -- "$WORK_DIR"; }
trap cleanup EXIT

echo "Downloading exact Fitness candidate: run=$RUN_ID artifact=$ARTIFACT"
gh run download "$RUN_ID" --repo "$REPOSITORY" --name "$ARTIFACT" --dir "$WORK_DIR"
APK="$WORK_DIR/android/app/build/outputs/apk/debug/app-debug.apk"
BADGING="$WORK_DIR/evidence/badging.txt"
[[ -s "$APK" && -s "$BADGING" ]] || { echo "Candidate APK/evidence missing" >&2; exit 3; }
grep -F "versionCode='51006'" "$BADGING" >/dev/null || { echo "Artifact is not versionCode 51006" >&2; exit 4; }
APK_SHA256="$(sha256sum "$APK" | awk '{print $1}')"
exec "$SCRIPT_DIR/fitness_phone_qa.sh" \
  --apk "$APK" \
  --expected-sha256 "$APK_SHA256" \
  --require-motion-sensors \
  --require-health-connect \
  "$@"
