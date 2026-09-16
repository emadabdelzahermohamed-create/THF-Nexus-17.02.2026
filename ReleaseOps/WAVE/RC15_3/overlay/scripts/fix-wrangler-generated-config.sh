#!/usr/bin/env bash
set -euo pipefail
CONFIG="${1:-dist/server/wrangler.json}"
[ -f "$CONFIG" ] || exit 0
TMP="${CONFIG}.tmp"
jq 'del(.legacy_env) | (.d1_databases[]? |= (. + {migrations_dir:"../../drizzle"}))' "$CONFIG" > "$TMP"
jq empty "$TMP" >/dev/null
mv "$TMP" "$CONFIG"
echo "WRANGLER GENERATED CONFIG: COMPATIBILITY PATCHED"
