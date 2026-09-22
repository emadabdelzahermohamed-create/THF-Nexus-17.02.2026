#!/usr/bin/env bash
set -Eeuo pipefail

: "${WAVE_LIVE_URL:?WAVE_LIVE_URL is required}"

attempts="${WAVE_ALIAS_ATTEMPTS:-12}"
retry_seconds="${WAVE_ALIAS_RETRY_SECONDS:-5}"
curl_bin="${CURL_BIN:-curl}"
tmp_root="${RUNNER_TEMP:-/tmp}"

case "$attempts" in
  ''|*[!0-9]*) echo "WAVE_ALIAS_ATTEMPTS must be a positive integer" >&2; exit 64 ;;
esac
case "$retry_seconds" in
  ''|*[!0-9]*) echo "WAVE_ALIAS_RETRY_SECONDS must be a non-negative integer" >&2; exit 64 ;;
esac
if (( attempts < 1 )); then
  echo "WAVE_ALIAS_ATTEMPTS must be at least 1" >&2
  exit 64
fi

mkdir -p "$tmp_root"

for path in /admin /publisher; do
  alias_name="${path#/}"
  body="$tmp_root/wave-alias-${alias_name}.html"
  passed=0

  for ((attempt = 1; attempt <= attempts; attempt++)); do
    code="$("$curl_bin" --connect-timeout 10 --max-time 30 -sS -o /dev/null -w '%{http_code}' "$WAVE_LIVE_URL$path" || true)"
    target="$("$curl_bin" --connect-timeout 10 --max-time 30 -sS -o /dev/null -w '%{redirect_url}' "$WAVE_LIVE_URL$path" || true)"
    final="$("$curl_bin" --connect-timeout 10 --max-time 30 -L -sS -o "$body" -w '%{http_code} %{url_effective}' "$WAVE_LIVE_URL$path" || true)"

    if { [[ "$code" == "307" ]] || [[ "$code" == "308" ]]; } \
      && [[ "$target" == "$WAVE_LIVE_URL/control" ]] \
      && [[ "$final" == "200 $WAVE_LIVE_URL/admin-login?return_to=%2Fcontrol" ]] \
      && grep -q 'دخول لوحة التحكم' "$body"; then
      echo "WAVE_CONTROL_ALIAS=PASS path=$path attempt=$attempt"
      passed=1
      break
    fi

    echo "WAVE_CONTROL_ALIAS_RETRY path=$path attempt=$attempt/$attempts code=${code:-none} target=${target:-none} final=${final:-none}" >&2
    if (( attempt < attempts )); then
      sleep "$retry_seconds"
    fi
  done

  if (( passed != 1 )); then
    echo "WAVE_CONTROL_ALIAS=FAIL path=$path attempts=$attempts" >&2
    exit 33
  fi
done
