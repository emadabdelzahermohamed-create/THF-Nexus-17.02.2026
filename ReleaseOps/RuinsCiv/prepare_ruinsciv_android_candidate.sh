#!/usr/bin/env bash
set -Eeuo pipefail
# Build-only migration. Never mutates recovered RC34 or WAVE_MAWJA.
REC="${RUINSCIV_RECOVERY_OUT:-$HOME/ruinsciv-recovery}"
SRC="${RUINSCIV_SOURCE:-$HOME/thf-terra-rift-staging-apk-v1/terra/work}"
DST="${RUINSCIV_CANDIDATE:-$HOME/ruinsciv-candidate}"
OUT="${RUINSCIV_CANDIDATE_OUT:-$HOME/ruinsciv-candidate-evidence}"
EXPECTED_WORLD=19043caa07aa1470f586708b551bbe86249f0f612480657d8891458361e78372
EXPECTED_PROJECT=ce3b4e4e2c08febcdb3d25591ee3163319af828d9c91e4691d3c2c47d02ff182
EXPECTED_AVATAR=4f556086e1b7149f6c958f1f399f4368f6ad9b76afd3503d6f848eeeb7bea24f
QA_PACKAGE=com.topherofit.ruins.civ.phoneqa
mkdir -p "$OUT"; rm -rf "$DST"; mkdir -p "$DST"
sha(){ sha256sum "$1"|awk '{print $1}'; }
[[ -f "$SRC/project.godot" && "$(sha "$SRC/project.godot")" == "$EXPECTED_PROJECT" ]]
[[ -f "$SRC/web/static/assets/avatars/stage16a/thf_mpfb_stage16a_ual12_animated.glb" && "$(sha "$SRC/web/static/assets/avatars/stage16a/thf_mpfb_stage16a_ual12_animated.glb")" == "$EXPECTED_AVATAR" ]]
[[ -f "$REC/WorldMain.RC34.proven.gd" && "$(sha "$REC/WorldMain.RC34.proven.gd")" == "$EXPECTED_WORLD" ]]
rsync -a --delete --exclude='.git' --exclude='.godot' --exclude='*.apk' --exclude='*.aab' "$SRC/" "$DST/"
install -m 0644 "$REC/WorldMain.RC34.proven.gd" "$DST/native/world/WorldMain.gd"
# Remove forbidden legacy humanoid payloads from candidate only.
find "$DST" -type f \( -iname 'thf_humanoid_v1*' -o -iname 'thf_humanoid_v2*' -o -iname 'thf_humanoid_v3*' -o -iname 'thf_humanoid_v4*' -o -iname 'thf_humanoid_v5*' -o -iname 'thf_humanoid_v6*' \) -print -delete | sort > "$OUT/removed_forbidden_legacy.txt"
# Migrate public identity only in text/config/code surfaces; binaries are never rewritten.
mapfile -d '' TEXTS < <(find "$DST" -type f \( -name '*.godot' -o -name '*.cfg' -o -name '*.json' -o -name '*.gd' -o -name '*.tscn' -o -name '*.tres' -o -name '*.xml' -o -name '*.html' -o -name '*.js' -o -name '*.ts' -o -name '*.css' -o -name '*.md' -o -name '*.txt' -o -name '*.properties' \) -print0)
for f in "${TEXTS[@]}"; do
  sed -i \
    -e 's/com\.topherofit\.thf\.terra\.phoneqa/com.topherofit.ruins.civ.phoneqa/g' \
    -e 's/com\.topherofit\.thf\.terra/com.topherofit.ruins.civ/g' \
    -e 's/THF World/RuinsCiv/g' -e 's/THF WORLD/RuinsCiv/g' -e 's/Terra/RuinsCiv/g' "$f"
done
# Force QA package in Godot Android export presets when present.
if [[ -f "$DST/export_presets.cfg" ]]; then
  sed -Ei 's#^(package/unique_name|package/name)="[^"]*"#\1="'"$QA_PACKAGE"'"#' "$DST/export_presets.cfg"
fi
# Fail closed on active-export forbidden identity/payload references.
: > "$OUT/forbidden_identity_hits.txt"; : > "$OUT/forbidden_legacy_hits.txt"
grep -RInE --binary-files=without-match 'com\.topherofit\.thf\.terra|THF World|THF WORLD' "$DST" > "$OUT/forbidden_identity_hits.txt" || true
grep -RInE --binary-files=without-match 'thf_humanoid_v[1-6]([^0-9]|$)' "$DST" > "$OUT/forbidden_legacy_hits.txt" || true
[[ ! -s "$OUT/forbidden_identity_hits.txt" ]]
[[ ! -s "$OUT/forbidden_legacy_hits.txt" ]]
[[ "$(sha "$DST/native/world/WorldMain.gd")" == "$EXPECTED_WORLD" ]]
[[ "$(sha "$DST/web/static/assets/avatars/stage16a/thf_mpfb_stage16a_ual12_animated.glb")" == "$EXPECTED_AVATAR" ]]
# Asset/evidence inventory.
find "$DST" -type f | grep -Ei '(downtown|city|nature|house|interior|furniture|street|transport|ruin)' | sort > "$OUT/environment_assets.txt" || true
find "$DST" -type f | grep -Ei '(wardrobe|cloth|shoe|footwear|hair|viseme|face|avatar|animation|ik)' | sort > "$OUT/avatar_feature_assets.txt" || true
cat > "$OUT/RUINSCIV_CANDIDATE_PREP_EVIDENCE.txt" <<EOF
RUINSCIV_CANDIDATE_PREP=PASS
public_name=RuinsCiv
qa_package=$QA_PACKAGE
world_sha256=$(sha "$DST/native/world/WorldMain.gd")
avatar_sha256=$(sha "$DST/web/static/assets/avatars/stage16a/thf_mpfb_stage16a_ual12_animated.glb")
removed_forbidden_legacy_count=$(wc -l < "$OUT/removed_forbidden_legacy.txt" | tr -d ' ')
forbidden_identity_hits=0
forbidden_legacy_reference_hits=0
environment_asset_matches=$(wc -l < "$OUT/environment_assets.txt" | tr -d ' ')
avatar_feature_asset_matches=$(wc -l < "$OUT/avatar_feature_assets.txt" | tr -d ' ')
source_mutated=FALSE
physical_device_status=PENDING
final_or_play_ready=FALSE
EOF
cat "$OUT/RUINSCIV_CANDIDATE_PREP_EVIDENCE.txt"
