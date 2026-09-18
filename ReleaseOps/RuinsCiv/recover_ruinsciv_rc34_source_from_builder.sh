#!/usr/bin/env bash
set -Eeuo pipefail
# Read-only source recovery helper for the proven RC34 builder work tree.
# It creates an archive; it does not modify the source tree or WAVE_MAWJA.
SRC="${RUINSCIV_BUILDER_SOURCE:-$HOME/thf-terra-rift-staging-apk-v1/terra/work}"
OUT="${RUINSCIV_RECOVERY_OUT:-$HOME/ruinsciv-recovery}"
mkdir -p "$OUT"
test -f "$SRC/project.godot"
test -f "$SRC/native/world/WorldMain.gd"
test -f "$SRC/web/static/assets/avatars/stage16a/thf_mpfb_stage16a_ual12_animated.glb"
# Historical RC34 evidence values: verify the known key files before archiving.
WORLD_SHA=$(sha256sum "$SRC/native/world/WorldMain.gd" | awk '{print $1}')
PROJECT_SHA=$(sha256sum "$SRC/project.godot" | awk '{print $1}')
AVATAR_SHA=$(sha256sum "$SRC/web/static/assets/avatars/stage16a/thf_mpfb_stage16a_ual12_animated.glb" | awk '{print $1}')
test "$WORLD_SHA" = "19043caa07aa1470f586708b551bbe86249f0f612480657d8891458361e78372"
test "$PROJECT_SHA" = "ce3b4e4e2c08febcdb3d25591ee3163319af828d9c91e4691d3c2c47d02ff182"
test "$AVATAR_SHA" = "4f556086e1b7149f6c958f1f399f4368f6ad9b76afd3503d6f848eeeb7bea24f"
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
archive_sha256=$SHA
archive_size_bytes=$SIZE
source_mutated=FALSE
physical_device_status=PENDING
final_or_play_ready=FALSE
EOF
cat "$OUT/RUINSCIV_RC34_SOURCE_RECOVERY_EVIDENCE.txt"
