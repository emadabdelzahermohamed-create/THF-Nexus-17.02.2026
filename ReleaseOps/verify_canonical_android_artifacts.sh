#!/usr/bin/env bash
set -Eeuo pipefail

OUT_DIR="${1:-canonical-out}"
EVIDENCE="${2:-evidence/package-verification.txt}"
AAPT="${ANDROID_HOME:?ANDROID_HOME required}/build-tools/36.0.0/aapt"
mkdir -p "$(dirname "$EVIDENCE")"
: > "$EVIDENCE"

outputs=0
apks=0
aabs=0

while IFS= read -r -d '' file; do
  outputs=$((outputs+1))
  sha=$(sha256sum "$file" | awk '{print $1}')
  if [[ "$file" == *.apk ]]; then
    apks=$((apks+1))
    badging=$("$AAPT" dump badging "$file")
    package=$(sed -n "s/^package: name='\([^']*\)'.*/\1/p" <<<"$badging" | head -n1)
    launcher=$(sed -n "s/^launchable-activity: name='\([^']*\)'.*/\1/p" <<<"$badging" | head -n1)
    test -n "$package"
    mode=LAUNCHER
    if [[ -z "$launcher" ]]; then
      xml=$("$AAPT" dump xmltree "$file" AndroidManifest.xml)
      case "$package" in
        com.topherofit.thf.command.debug)
          grep -q 'com.topherofit.thf.permission.COMMAND_PRIVATE' <<<"$xml"
          grep -q 'android.intent.action.VIEW' <<<"$xml"
          grep -q 'android.intent.category.BROWSABLE' <<<"$xml"
          mode=PRIVATE_DEEPLINK
          ;;
        com.topherofit.thf.signal.debug)
          grep -q 'com.topherofit.thf.permission.SIGNAL_PRIVATE' <<<"$xml"
          grep -q 'android.intent.action.VIEW' <<<"$xml"
          grep -q 'android.intent.category.BROWSABLE' <<<"$xml"
          mode=PRIVATE_DEEPLINK
          ;;
        *)
          echo "Missing launcher for non-private APK: $package" >&2
          exit 51
          ;;
      esac
    fi
    echo "APK file=$file package=$package mode=$mode launcher=${launcher:-PRIVATE} sha256=$sha" | tee -a "$EVIDENCE"
  elif [[ "$file" == *.aab ]]; then
    aabs=$((aabs+1))
    unzip -tq "$file" >/dev/null
    if jarsigner -verify "$file" >/dev/null 2>&1; then signed=true; else signed=false; fi
    echo "AAB file=$file signed=$signed sha256=$sha" | tee -a "$EVIDENCE"
  fi
done < <(find "$OUT_DIR" -type f \( -name '*.apk' -o -name '*.aab' \) -print0 | sort -z)

echo "TOTAL_OUTPUTS=$outputs APK_COUNT=$apks AAB_COUNT=$aabs" | tee -a "$EVIDENCE"
test "$apks" -eq 6
test "$aabs" -eq 6
test "$outputs" -eq 12
