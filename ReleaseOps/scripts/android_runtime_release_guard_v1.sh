#!/usr/bin/env bash
set -Eeuo pipefail

: "${APK:?APK required}"
: "${EXPECTED_PACKAGE:?EXPECTED_PACKAGE required}"
: "${ANDROID_SDK_ROOT:?ANDROID_SDK_ROOT required}"
REQUIRE_GODOT_PAYLOAD="${REQUIRE_GODOT_PAYLOAD:-false}"
REQUIRE_HTTPS_LITERAL="${REQUIRE_HTTPS_LITERAL:-false}"

BT="$(find "$ANDROID_SDK_ROOT/build-tools" -mindepth 1 -maxdepth 1 -type d | sort -V | tail -1)"
AAPT="$BT/aapt"
APKSIGNER="$BT/apksigner"
ZIPALIGN="$BT/zipalign"
test -s "$APK"
test -x "$AAPT" && test -x "$APKSIGNER" && test -x "$ZIPALIGN"
unzip -tq "$APK" >/dev/null
"$APKSIGNER" verify --verbose "$APK" >/dev/null
"$ZIPALIGN" -c -p 4 "$APK" >/dev/null
BADGING="$($AAPT dump badging "$APK")"
grep -q "package: name='$EXPECTED_PACKAGE'" <<<"$BADGING"
grep -q "targetSdkVersion:'36'" <<<"$BADGING"

# Prevent Godot Android resource pollution seen in Rift RC37.
if unzip -Z1 "$APK" | grep -Eq '(^|/)res/.*\.import$'; then
  echo ANDROID_GODOT_IMPORT_SIDECAR_GATE=FAIL
  exit 71
fi
echo ANDROID_GODOT_IMPORT_SIDECAR_GATE=PASS

if [ "$REQUIRE_GODOT_PAYLOAD" = true ]; then
  # A Godot Android release must contain packaged project data under assets or a pck.
  if unzip -Z1 "$APK" | grep -Eq '(^|/)[^/]+\.pck$|^assets/.+'; then
    echo GODOT_PROJECT_PAYLOAD_GATE=PASS
  else
    echo GODOT_PROJECT_PAYLOAD_GATE=FAIL
    exit 72
  fi
fi

if [ "$REQUIRE_HTTPS_LITERAL" = true ]; then
  TMP="$(mktemp -d)"
  trap 'rm -rf "$TMP"' EXIT
  unzip -q "$APK" 'classes*.dex' -d "$TMP" 2>/dev/null || true
  if find "$TMP" -type f -name 'classes*.dex' -print0 | xargs -0 strings 2>/dev/null | grep -Eq 'https://[A-Za-z0-9.-]+'; then
    echo HTTPS_RUNTIME_ENDPOINT_GATE=PASS
  else
    echo HTTPS_RUNTIME_ENDPOINT_GATE=FAIL
    exit 73
  fi
fi

echo ANDROID_RUNTIME_RELEASE_GUARD=PASS
