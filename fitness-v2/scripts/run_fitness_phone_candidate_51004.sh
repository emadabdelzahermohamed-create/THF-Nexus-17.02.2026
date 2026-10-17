#!/usr/bin/env bash
set -Eeuo pipefail

REPOSITORY="emadabdelzahermohamed-create/THF-Nexus-17.02.2026"
RUN_ID="39031680067"
ARTIFACT="fitness-v2-51004-package-gate"
APK_SHA256="0c5c76361106ae5564b2136b3c3b6b654cc827377484f3b684260afaba8fb2f1"
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

for command_name in gh adb sha256sum mktemp; do
  command -v "$command_name" >/dev/null || {
    echo "Missing command: $command_name" >&2
    exit 2
  }
done

WORK_DIR="$(mktemp -d)"
cleanup() { rm -rf -- "$WORK_DIR"; }
trap cleanup EXIT

echo "Downloading exact Fitness candidate: run=$RUN_ID artifact=$ARTIFACT"
gh run download "$RUN_ID" \
  --repo "$REPOSITORY" \
  --name "$ARTIFACT" \
  --dir "$WORK_DIR"

APK="$WORK_DIR/android/app/build/outputs/apk/debug/app-debug.apk"
[[ -f "$APK" ]] || {
  echo "Candidate APK is missing from artifact $ARTIFACT" >&2
  exit 3
}

ACTUAL_SHA="$(sha256sum "$APK" | awk '{print $1}')"
[[ "$ACTUAL_SHA" == "$APK_SHA256" ]] || {
  echo "Candidate APK SHA-256 mismatch: got $ACTUAL_SHA" >&2
  exit 4
}

exec "$SCRIPT_DIR/fitness_phone_qa.sh" \
  --apk "$APK" \
  --expected-sha256 "$APK_SHA256" \
  "$@"
