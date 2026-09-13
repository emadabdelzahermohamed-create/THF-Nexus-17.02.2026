#!/usr/bin/env bash
set -Eeuo pipefail

: "${APK:?APK required}"
: "${EXPECTED_PACKAGE:?EXPECTED_PACKAGE required}"
: "${ANDROID_SDK_ROOT:?ANDROID_SDK_ROOT required}"
RUNTIME_CLASS="${RUNTIME_CLASS:-}"
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

# Prevent Godot editor sidecars from leaking into Android resources.
if unzip -Z1 "$APK" | grep -Eq '(^|/)res/.*\.import$'; then
  echo ANDROID_GODOT_IMPORT_SIDECAR_GATE=FAIL
  exit 71
fi
echo ANDROID_GODOT_IMPORT_SIDECAR_GATE=PASS

if [ -z "$RUNTIME_CLASS" ]; then
  if [ "$REQUIRE_GODOT_PAYLOAD" = true ]; then RUNTIME_CLASS=GODOT_RUNTIME;
  elif [ "$REQUIRE_HTTPS_LITERAL" = true ]; then RUNTIME_CLASS=SERVICE_NATIVE;
  else RUNTIME_CLASS=OFFLINE_NATIVE;
  fi
fi

case "$RUNTIME_CLASS" in
  GODOT_RUNTIME)
    ASSET_COUNT="$(unzip -Z1 "$APK" | grep -c '^assets/' || true)"
    test "$ASSET_COUNT" -gt 0 || { echo GODOT_PROJECT_PAYLOAD_GATE=FAIL; exit 72; }
    if unzip -Z1 "$APK" | grep -Eq '(^|/)[^/]+\.pck$|^assets/.+'; then
      echo GODOT_PROJECT_PAYLOAD_GATE=PASS
      echo GODOT_ASSET_COUNT="$ASSET_COUNT"
    else
      echo GODOT_PROJECT_PAYLOAD_GATE=FAIL
      exit 72
    fi
    ;;
  SERVICE_NATIVE)
    : "${EXPECTED_HTTPS_ENDPOINT:?EXPECTED_HTTPS_ENDPOINT required for SERVICE_NATIVE}"
    case "$EXPECTED_HTTPS_ENDPOINT" in https://*) ;; *) echo HTTPS_RUNTIME_ENDPOINT_GATE=FAIL_NON_HTTPS; exit 73;; esac
    if [[ "$EXPECTED_HTTPS_ENDPOINT" =~ (localhost|127\.0\.0\.1|0\.0\.0\.0|example\.|placeholder|unset) ]]; then
      echo HTTPS_RUNTIME_ENDPOINT_GATE=FAIL_PLACEHOLDER_OR_LOOPBACK
      exit 74
    fi
    TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
    unzip -q "$APK" 'classes*.dex' -d "$TMP" 2>/dev/null || true
    test -n "$(find "$TMP" -type f -name 'classes*.dex' -print -quit)" || { echo HTTPS_RUNTIME_ENDPOINT_GATE=FAIL_NO_DEX; exit 75; }
    if ! find "$TMP" -type f -name 'classes*.dex' -print0 | xargs -0 strings | grep -F "$EXPECTED_HTTPS_ENDPOINT" >/dev/null; then
      echo HTTPS_RUNTIME_ENDPOINT_GATE=FAIL_NOT_EMBEDDED
      exit 76
    fi
    python3 - "$EXPECTED_HTTPS_ENDPOINT" <<'PY'
import json,sys,urllib.request
base=sys.argv[1].rstrip('/')
req=urllib.request.Request(base+'/health',headers={'User-Agent':'THF-Android-ReleaseGuard'})
d=json.load(urllib.request.urlopen(req,timeout=8))
assert d.get('ok') is True
PY
    echo HTTPS_RUNTIME_ENDPOINT_GATE=PASS
    ;;
  OFFLINE_NATIVE)
    [ "${REQUIRES_NETWORK_AT_STARTUP:-false}" != true ] || { echo OFFLINE_RUNTIME_GATE=FAIL_REQUIRES_NETWORK; exit 77; }
    echo OFFLINE_RUNTIME_GATE=PASS
    ;;
  *)
    echo "ANDROID_RUNTIME_CLASS_GATE=FAIL_UNKNOWN:$RUNTIME_CLASS"
    exit 78
    ;;
esac

echo PACKAGE="$EXPECTED_PACKAGE"
echo TARGET_SDK=36
echo RUNTIME_CLASS="$RUNTIME_CLASS"
echo ANDROID_RUNTIME_RELEASE_GUARD=PASS
