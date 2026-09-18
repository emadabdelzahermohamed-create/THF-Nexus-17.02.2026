#!/usr/bin/env bash
set -Eeuo pipefail
# Read-only source recovery helper for the proven RC34 builder work tree.
# It creates evidence/archive only; it does not modify source, WAVE_MAWJA, or release identities.
SRC="${RUINSCIV_BUILDER_SOURCE:-$HOME/thf-terra-rift-staging-apk-v1/terra/work}"
OUT="${RUINSCIV_RECOVERY_OUT:-$HOME/ruinsciv-recovery}"
mkdir -p "$OUT"
test -f "$SRC/project.godot"
test -f "$SRC/native/world/WorldMain.gd"
test -f "$SRC/web/static/assets/avatars/stage16a/thf_mpfb_stage16a_ual12_animated.glb"
WORLD_SHA=$(sha256sum "$SRC/native/world/WorldMain.gd" | awk '{print $1}')
PROJECT_SHA=$(sha256sum "$SRC/project.godot" | awk '{print $1}')
AVATAR_SHA=$(sha256sum "$SRC/web/static/assets/avatars/stage16a/thf_mpfb_stage16a_ual12_animated.glb" | awk '{print $1}')
test "$WORLD_SHA" = "19043caa07aa1470f586708b551bbe86249f0f612480657d8891458361e78372"
test "$PROJECT_SHA" = "ce3b4e4e2c08febcdb3d25591ee3163319af828d9c91e4691d3c2c47d02ff182"
test "$AVATAR_SHA" = "4f556086e1b7149f6c958f1f399f4368f6ad9b76afd3503d6f848eeeb7bea24f"
# Deterministic content manifest gives a reproducible fingerprint independent of tar/gzip metadata.
MANIFEST="$OUT/RUINSCIV_RC34_SOURCE_CONTENT_SHA256.txt"
(
  cd "$SRC"
  find . -type f \
    ! -path './.git/*' ! -path './.godot/*' \
    ! -name '*.apk' ! -name '*.aab' \
    -print0 | sort -z | xargs -0 sha256sum
) > "$MANIFEST"
MANIFEST_SHA=$(sha256sum "$MANIFEST" | awk '{print $1}')
FILE_COUNT=$(wc -l < "$MANIFEST" | tr -d ' ')
# Inventory forbidden legacy assets and required converted-environment evidence without mutating anything.
FORBIDDEN="$OUT/RUINSCIV_RC34_FORBIDDEN_LEGACY_INVENTORY.txt"
find "$SRC" -type f \( -iname 'thf_humanoid_v1*' -o -iname 'thf_humanoid_v2*' -o -iname 'thf_humanoid_v3*' -o -iname 'thf_humanoid_v4*' -o -iname 'thf_humanoid_v5*' -o -iname 'thf_humanoid_v6*' \) -print | sort > "$FORBIDDEN"
FORBIDDEN_COUNT=$(wc -l < "$FORBIDDEN" | tr -d ' ')
ENVINV="$OUT/RUINSCIV_RC34_ENVIRONMENT_ASSET_INVENTORY.txt"
find "$SRC" -type f | grep -Ei '(downtown|city|nature|house|interior|furniture|street|transport|ruin)' | sort > "$ENVINV" || true
ENV_COUNT=$(wc -l < "$ENVINV" | tr -d ' ')
ARCHIVE="$OUT/RUINSCIV_RC34_PROVEN_SOURCE_TREE.tar.gz"
tar --exclude='.godot' --exclude='*.apk' --exclude='*.aab' --exclude='.git' -C "$(dirname "$SRC")" -czf "$ARCHIVE" "$(basename "$SRC")"
SHA=$(sha256sum "$ARCHIVE" | awk '{print $1}')
SIZE=$(stat -c %s "$ARCHIVE")
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
cat "$OUT/RUINSCIV_RC34_SOURCE_RECOVERY_EVIDENCE.txt"
