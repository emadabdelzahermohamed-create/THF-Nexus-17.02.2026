#!/usr/bin/env bash
set -Eeuo pipefail

EXPECTED_SHA="e0ac997e1cdb0145b765884d8a59a70403821d1d1e19fbf6a05adcc4640cfbec"
EXPECTED_PACKAGE="com.topherofit.thf.terra.phoneqa"
EXPECTED_TARGET="36"
APK="$(find "$HOME" -type f -name 'THF-TERRA-4.6.8-RC34-PHONE-V4.apk' -print -quit 2>/dev/null)"
test -n "$APK"
ACTUAL_SHA="$(sha256sum "$APK" | awk '{print $1}')"
test "$ACTUAL_SHA" = "$EXPECTED_SHA"
SDK="$HOME/thf-builder-rc16-build/android-sdk"
BT="$(find "$SDK/build-tools" -mindepth 1 -maxdepth 1 -type d | sort -V | tail -1)"
test -x "$BT/apksigner"
test -x "$BT/aapt2"
test -x "$BT/zipalign"

echo "APK=$APK"
echo "SHA256=$ACTUAL_SHA"
"$BT/zipalign" -c -v 4 "$APK" >/tmp/terra_v4_zipalign.txt
"$BT/apksigner" verify --verbose --print-certs "$APK" | tee /tmp/terra_v4_apksigner.txt
"$BT/aapt2" dump badging "$APK" | tee /tmp/terra_v4_badging.txt
grep -Fq "package: name='$EXPECTED_PACKAGE'" /tmp/terra_v4_badging.txt
grep -Fq "targetSdkVersion:'$EXPECTED_TARGET'" /tmp/terra_v4_badging.txt
unzip -l "$APK" | grep -Fq 'lib/arm64-v8a/'

echo 'TERRA_V4_ZIPALIGN=PASS'
echo 'TERRA_V4_APKSIGNER=PASS'
echo 'TERRA_V4_PACKAGE_ID=PASS'
echo 'TERRA_V4_TARGET_SDK_36=PASS'
echo 'TERRA_V4_ARM64=PASS'
echo 'PHYSICAL_DEVICE_INSTALL=STILL_REQUIRED'
echo 'FINAL_OR_PLAY_READY=FALSE'
