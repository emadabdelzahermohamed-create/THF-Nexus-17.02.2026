#!/usr/bin/env bash
set -Eeuo pipefail
# Read-only recovery of the proven RC34 source. Never mutates source or WAVE_MAWJA.
SRC="${RUINSCIV_BUILDER_SOURCE:-$HOME/thf-terra-rift-staging-apk-v1/terra/work}"
OUT="${RUINSCIV_RECOVERY_OUT:-$HOME/ruinsciv-recovery}"
EXPECTED_WORLD="19043caa07aa1470f586708b551bbe86249f0f612480657d8891458361e78372"
EXPECTED_PROJECT="ce3b4e4e2c08febcdb3d25591ee3163319af828d9c91e4691d3c2c47d02ff182"
EXPECTED_AVATAR="4f556086e1b7149f6c958f1f399f4368f6ad9b76afd3503d6f848eeeb7bea24f"
mkdir -p "$OUT"
FAIL="$OUT/RUINSCIV_RC34_RECOVERY_FAILURE.txt"
DISC="$OUT/RUINSCIV_RC34_WORLD_DISCOVERY.txt"
: > "$DISC"
trap 'rc=$?; printf "RUINSCIV_RC34_SOURCE_RECOVERY=FAIL\nexit_code=%s\nsource_path=%s\nsource_mutated=FALSE\n" "$rc" "$SRC" > "$FAIL"; echo "[RuinsCiv recovery] FAIL rc=$rc source=$SRC" >&2' ERR
require_file(){ [[ -f "$1" ]] || { echo "MISSING $1" >&2; return 41; }; }
sha(){ sha256sum "$1"|awk '{print $1}'; }
verify(){ local a; a=$(sha "$1"); echo "[RuinsCiv recovery] $3 sha256=$a"; [[ "$a" == "$2" ]] || { echo "HASH_MISMATCH $3 expected=$2 actual=$a" >&2; return 42; }; }
if [[ ! -f "$SRC/project.godot" ]]; then
 mapfile -t c < <(find /home /root -maxdepth 7 -type f -path '*/thf-terra-rift-staging-apk-v1/terra/work/project.godot' 2>/dev/null|sort||true)
 printf '%s\n' "${c[@]:-}" > "$OUT/RUINSCIV_RC34_SOURCE_PATH_CANDIDATES.txt"
 [[ ${#c[@]} -eq 1 ]] || exit 43; SRC="${c[0]%/project.godot}"
fi
PROJECT="$SRC/project.godot"; AVATAR="$SRC/web/static/assets/avatars/stage16a/thf_mpfb_stage16a_ual12_animated.glb"; WORLD="$SRC/native/world/WorldMain.gd"
require_file "$PROJECT"; require_file "$AVATAR"; require_file "$WORLD"
verify "$PROJECT" "$EXPECTED_PROJECT" project
verify "$AVATAR" "$EXPECTED_AVATAR" avatar_asset
# Current worktree may have advanced after the proven RC34 build. Search read-only for the exact historical WorldMain bytes.
if [[ "$(sha "$WORLD")" != "$EXPECTED_WORLD" ]]; then
 echo "current_world=$WORLD sha256=$(sha "$WORLD")" >> "$DISC"
 while IFS= read -r -d '' f; do
   a=$(sha "$f" 2>/dev/null || true); printf '%s\t%s\n' "$a" "$f" >> "$DISC"
   if [[ "$a" == "$EXPECTED_WORLD" ]]; then WORLD="$f"; break; fi
 done < <(find /home /root /tmp -xdev -type f \( -name 'WorldMain.gd' -o -name '*.tar' -o -name '*.tgz' -o -name '*.tar.gz' \) -print0 2>/dev/null || true)
fi
# Also inspect git objects/history in the source repository without checkout/reset.
if [[ "$(sha "$WORLD")" != "$EXPECTED_WORLD" && -d "$SRC/.git" ]]; then
 while read -r commit; do
   git -C "$SRC" show "$commit:native/world/WorldMain.gd" > "$OUT/.candidate_world" 2>/dev/null || continue
   a=$(sha "$OUT/.candidate_world"); printf '%s\tgit:%s\n' "$a" "$commit" >> "$DISC"
   if [[ "$a" == "$EXPECTED_WORLD" ]]; then WORLD="$OUT/.candidate_world"; echo "matched_git_commit=$commit" >> "$DISC"; break; fi
 done < <(git -C "$SRC" rev-list --all 2>/dev/null || true)
fi
verify "$WORLD" "$EXPECTED_WORLD" world_source
# Preserve exact recovered WorldMain separately if current worktree advanced; archive remains the untouched current tree for provenance.
cp "$WORLD" "$OUT/WorldMain.RC34.proven.gd"
MANIFEST="$OUT/RUINSCIV_RC34_SOURCE_CONTENT_SHA256.txt"
(cd "$SRC"; find . -type f ! -path './.git/*' ! -path './.godot/*' ! -name '*.apk' ! -name '*.aab' -print0|sort -z|xargs -0 sha256sum) > "$MANIFEST"
FORBIDDEN="$OUT/RUINSCIV_RC34_FORBIDDEN_LEGACY_INVENTORY.txt"; find "$SRC" -type f \( -iname 'thf_humanoid_v1*' -o -iname 'thf_humanoid_v2*' -o -iname 'thf_humanoid_v3*' -o -iname 'thf_humanoid_v4*' -o -iname 'thf_humanoid_v5*' -o -iname 'thf_humanoid_v6*' \) -print|sort > "$FORBIDDEN"
ENVINV="$OUT/RUINSCIV_RC34_ENVIRONMENT_ASSET_INVENTORY.txt"; find "$SRC" -type f|grep -Ei '(downtown|city|nature|house|interior|furniture|street|transport|ruin)'|sort > "$ENVINV" || true
ARCHIVE="$OUT/RUINSCIV_RC34_PROVEN_SOURCE_TREE.tar.gz"; tar --exclude='.godot' --exclude='*.apk' --exclude='*.aab' --exclude='.git' -C "$(dirname "$SRC")" -czf "$ARCHIVE" "$(basename "$SRC")"
cat > "$OUT/RUINSCIV_RC34_SOURCE_RECOVERY_EVIDENCE.txt" <<EOF
RUINSCIV_RC34_SOURCE_RECOVERY=PASS
source_path=$SRC
world_source_sha256=$EXPECTED_WORLD
project_sha256=$EXPECTED_PROJECT
avatar_asset_sha256=$EXPECTED_AVATAR
current_worktree_world_sha256=$(sha "$SRC/native/world/WorldMain.gd")
archive_sha256=$(sha "$ARCHIVE")
archive_size_bytes=$(stat -c %s "$ARCHIVE")
forbidden_legacy_inventory_count=$(wc -l < "$FORBIDDEN"|tr -d ' ')
converted_environment_inventory_matches=$(wc -l < "$ENVINV"|tr -d ' ')
source_mutated=FALSE
migration_performed=FALSE
physical_device_status=PENDING
final_or_play_ready=FALSE
EOF
rm -f "$FAIL"; cat "$OUT/RUINSCIV_RC34_SOURCE_RECOVERY_EVIDENCE.txt"
