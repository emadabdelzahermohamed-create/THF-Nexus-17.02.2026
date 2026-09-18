#!/usr/bin/env bash
set -Eeuo pipefail
# Read-only source recovery helper for the proven RC34 builder work tree.
# Creates evidence/archive only; never mutates source or WAVE_MAWJA.
SRC="${RUINSCIV_BUILDER_SOURCE:-$HOME/thf-terra-rift-staging-apk-v1/terra/work}"
OUT="${RUINSCIV_RECOVERY_OUT:-$HOME/ruinsciv-recovery}"
EXPECTED_WORLD="19043caa07aa1470f586708b551bbe86249f0f612480657d8891458361e78372"
EXPECTED_PROJECT="ce3b4e4e2c08febcdb3d25591ee3163319af828d9c91e4691d3c2c47d02ff182"
EXPECTED_AVATAR="4f556086e1b7149f6c958f1f399f4368f6ad9b76afd3503d6f848eeeb7bea24f"
mkdir -p "$OUT"
FAIL="$OUT/RUINSCIV_RC34_RECOVERY_FAILURE.txt"
trap 'rc=$?; printf "RUINSCIV_RC34_SOURCE_RECOVERY=FAIL\nexit_code=%s\nsource_path=%s\nsource_mutated=FALSE\n" "$rc" "$SRC" > "$FAIL"; echo "[RuinsCiv recovery] FAIL rc=$rc source=$SRC" >&2' ERR

require_file() { if [[ ! -f "$1" ]]; then echo "[RuinsCiv recovery] MISSING: $1" >&2; return 41; fi; }
verify_sha() { local f="$1" expected="$2" label="$3" actual; actual=$(sha256sum "$f" | awk '{print $1}'); echo "[RuinsCiv recovery] $label sha256=$actual"; if [[ "$actual" != "$expected" ]]; then echo "[RuinsCiv recovery] HASH_MISMATCH $label expected=$expected actual=$actual" >&2; return 42; fi; }

# If the historical HOME differs for the SSH principal, locate only plausible RC34 work trees.
if [[ ! -f "$SRC/project.godot" ]]; then
  echo "[RuinsCiv recovery] default source absent: $SRC" >&2
  mapfile -t candidates < <(find /home /root -maxdepth 6 -type f -path '*/thf-terra-rift-staging-apk-v1/terra/work/project.godot' 2>/dev/null | sort || true)
  printf '%s\n' "${candidates[@]:-}" > "$OUT/RUINSCIV_RC34_SOURCE_PATH_CANDIDATES.txt"
  if [[ ${#candidates[@]} -eq 1 ]]; then SRC="${candidates[0]%/project.godot}"; echo "[RuinsCiv recovery] resolved source=$SRC"; else echo "[RuinsCiv recovery] candidate_count=${#candidates[@]}" >&2; return 43 2>/dev/null || exit 43; fi
fi

WORLD="$SRC/native/world/WorldMain.gd"
PROJECT="$SRC/project.godot"
AVATAR="$SRC/web/static/assets/avatars/stage16a/thf_mpfb_stage16a_ual12_animated.glb"
require_file "$PROJECT"; require_file "$WORLD"; require_file "$AVATAR"
verify_sha "$WORLD" "$EXPECTED_WORLD" world_source
verify_sha "$PROJECT" "$EXPECTED_PROJECT" project
verify_sha "$AVATAR" "$EXPECTED_AVATAR" avatar_asset
WORLD_SHA="$EXPECTED_WORLD"; PROJECT_SHA="$EXPECTED_PROJECT"; AVATAR_SHA="$EXPECTED_AVATAR"

MANIFEST="$OUT/RUINSCIV_RC34_SOURCE_CONTENT_SHA256.txt"
(cd "$SRC"; find . -type f ! -path './.git/*' ! -path './.godot/*' ! -name '*.apk' ! -name '*.aab' -print0 | sort -z | xargs -0 sha256sum) > "$MANIFEST"
MANIFEST_SHA=$(sha256sum "$MANIFEST" | awk '{print $1}')
FILE_COUNT=$(wc -l < "$MANIFEST" | tr -d ' ')
FORBIDDEN="$OUT/RUINSCIV_RC34_FORBIDDEN_LEGACY_INVENTORY.txt"
find "$SRC" -type f \( -iname 'thf_humanoid_v1*' -o -iname 'thf_humanoid_v2*' -o -iname 'thf_humanoid_v3*' -o -iname 'thf_humanoid_v4*' -o -iname 'thf_humanoid_v5*' -o -iname 'thf_humanoid_v6*' \) -print | sort > "$FORBIDDEN"
FORBIDDEN_COUNT=$(wc -l < "$FORBIDDEN" | tr -d ' ')
ENVINV="$OUT/RUINSCIV_RC34_ENVIRONMENT_ASSET_INVENTORY.txt"
find "$SRC" -type f | grep -Ei '(downtown|city|nature|house|interior|furniture|street|transport|ruin)' | sort > "$ENVINV" || true
ENV_COUNT=$(wc -l < "$ENVINV" | tr -d ' ')
ARCHIVE="$OUT/RUINSCIV_RC34_PROVEN_SOURCE_TREE.tar.gz"
tar --exclude='.godot' --exclude='*.apk' --exclude='*.aab' --exclude='.git' -C "$(dirname "$SRC")" -czf "$ARCHIVE" "$(basename "$SRC")"
SHA=$(sha256sum "$ARCHIVE" | awk '{print $1}'); SIZE=$(stat -c %s "$ARCHIVE")
cat > "$OUT/RUINSCIV_RC34_SOURCE_RECOVERY_EVIDENCE.txt" <<EOF
RUINSCIV_RC34_SOURCE_RECOVERY=PASS
source_path=$SRC
world_source_sha256=$WORLD_SHA
project_sha256=$PROJECT_SHA
avatar_asset_sha256=$AVATAR_SHA
content_manifest_sha256=$MANIFEST_SHA
content_file_count=$FILE_COUNT
forbidden_legacy_inventory_count=$FORBIDDEN_COUNT
converted_environment_inventory_matches=$ENV_COUNT
archive_sha256=$SHA
archive_size_bytes=$SIZE
source_mutated=FALSE
migration_performed=FALSE
physical_device_status=PENDING
final_or_play_ready=FALSE
EOF
rm -f "$FAIL"
cat "$OUT/RUINSCIV_RC34_SOURCE_RECOVERY_EVIDENCE.txt"
