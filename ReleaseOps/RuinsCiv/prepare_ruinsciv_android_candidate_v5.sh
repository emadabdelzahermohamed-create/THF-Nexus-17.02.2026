#!/usr/bin/env bash
set -Eeuo pipefail
# V5: derive an isolated RC34 RuinsCiv candidate and gate only exportable/runtime surfaces.
REC="${RUINSCIV_RECOVERY_OUT:-$HOME/ruinsciv-recovery}"
SRC="${RUINSCIV_SOURCE:-$HOME/thf-terra-rift-staging-apk-v1/terra/work}"
DST="${RUINSCIV_CANDIDATE:-$HOME/ruinsciv-candidate}"
OUT="${RUINSCIV_CANDIDATE_OUT:-$HOME/ruinsciv-candidate-evidence-v5}"
QA_PACKAGE=com.topherofit.ruins.civ.phoneqa
MPFB=res://web/static/assets/avatars/stage16a/thf_mpfb_stage16a_ual12_animated.glb
EXPECTED_WORLD=19043caa07aa1470f586708b551bbe86249f0f612480657d8891458361e78372
EXPECTED_PROJECT=ce3b4e4e2c08febcdb3d25591ee3163319af828d9c91e4691d3c2c47d02ff182
EXPECTED_AVATAR=4f556086e1b7149f6c958f1f399f4368f6ad9b76afd3503d6f848eeeb7bea24f
mkdir -p "$OUT"
exec > >(tee "$OUT/v5_trace.log") 2>&1
trap 'rc=$?; printf "RUINSCIV_V5_FAIL rc=%s line=%s command=%q\n" "$rc" "$LINENO" "$BASH_COMMAND" | tee "$OUT/v5_failure.txt"; exit "$rc"' ERR
printf 'RUINSCIV_V5_START user=%s home=%s\n' "$(id -un)" "$HOME"
sha(){ sha256sum "$1"|awk '{print $1}'; }
require_file(){ local f="$1" label="$2"; if [[ ! -f "$f" ]]; then printf 'MISSING_%s=%s\n' "$label" "$f"; return 41; fi; }
sanitize_active_text(){
 local f="$1"
 sed -i -e 's/com\.topherofit\.thf\.terra\.phoneqa/com.topherofit.ruins.civ.phoneqa/g' -e 's/com\.topherofit\.thf\.terra/com.topherofit.ruins.civ/g' -e 's/THF World/RuinsCiv/g' -e 's/THF WORLD/RuinsCiv/g' -e 's/Terra/RuinsCiv/g' "$f"
 sed -Ei "s#(res://)?[^\"'[:space:]]*thf_humanoid_v[1-6][^\"'[:space:]]*\.(glb|gltf)#$MPFB#g" "$f" || true
}
require_file "$SRC/project.godot" SOURCE_PROJECT
require_file "$SRC/web/static/assets/avatars/stage16a/thf_mpfb_stage16a_ual12_animated.glb" SOURCE_AVATAR
require_file "$REC/WorldMain.RC34.proven.gd" RC34_WORLD
printf 'PREFLIGHT_FILES=PASS\n'
[[ "$(sha "$SRC/project.godot")" == "$EXPECTED_PROJECT" ]] || { echo PROJECT_SHA_MISMATCH; exit 42; }
[[ "$(sha "$SRC/web/static/assets/avatars/stage16a/thf_mpfb_stage16a_ual12_animated.glb")" == "$EXPECTED_AVATAR" ]] || { echo AVATAR_SHA_MISMATCH; exit 43; }
[[ "$(sha "$REC/WorldMain.RC34.proven.gd")" == "$EXPECTED_WORLD" ]] || { echo WORLD_SHA_MISMATCH; exit 44; }
printf 'PREFLIGHT_SHA=PASS\n'
rm -rf "$DST"; mkdir -p "$DST"
rsync -a --delete --exclude='.git' --exclude='.godot' --exclude='*.apk' --exclude='*.aab' "$SRC/" "$DST/"
install -m0644 "$REC/WorldMain.RC34.proven.gd" "$DST/native/world/WorldMain.gd"
find "$DST" -type f \( -iname 'thf_humanoid_v1*' -o -iname 'thf_humanoid_v2*' -o -iname 'thf_humanoid_v3*' -o -iname 'thf_humanoid_v4*' -o -iname 'thf_humanoid_v5*' -o -iname 'thf_humanoid_v6*' \) -print -delete | sort > "$OUT/removed_forbidden_legacy.txt"
PRUNES=( -path "$DST/tests" -o -path "$DST/scripts" -o -path "$DST/docs" -o -path "$DST/.github" -o -path "$DST/validation" -o -path "$DST/evidence" -o -path "$DST/ReleaseOps" )
mapfile -d '' TEXTS < <(find "$DST" \( "${PRUNES[@]}" \) -prune -o -type f \( -name '*.godot' -o -name '*.cfg' -o -name '*.json' -o -name '*.gd' -o -name '*.py' -o -name '*.tscn' -o -name '*.tres' -o -name '*.xml' -o -name '*.html' -o -name '*.js' -o -name '*.ts' -o -name '*.css' -o -name '*.properties' -o -name '*.java' -o -name '*.kt' -o -name '*.kts' -o -name '*.gradle' -o -name '*.toml' -o -name '*.ini' -o -name '*.env.example' -o -name '*.md' \) -print0)
for f in "${TEXTS[@]}"; do sanitize_active_text "$f"; done
if [[ -f "$DST/export_presets.cfg" ]]; then sed -Ei 's#^(package/unique_name|package/name)="[^"]*"#\1="'"$QA_PACKAGE"'"#' "$DST/export_presets.cfg"; fi
find "$DST" -type d \( -name build -o -name .gradle -o -name .cxx \) -prune -exec rm -rf {} + || true
# Historical validation/checksum/deployment notes are retained for provenance but are not exportable/runtime inputs.
EX=(--exclude-dir=.git --exclude-dir=tests --exclude-dir=scripts --exclude-dir=docs --exclude-dir=.github --exclude-dir=validation --exclude-dir=evidence --exclude-dir=ReleaseOps --exclude='*_VALIDATION.txt' --exclude='*MANIFEST_SHA256.txt' --exclude='DEPLOY_NOW*.md')
grep -RInE --binary-files=without-match "${EX[@]}" 'com\.topherofit\.thf\.terra|THF World|THF WORLD' "$DST" > "$OUT/forbidden_identity_hits.txt" || true
grep -RInE --binary-files=without-match "${EX[@]}" 'thf_humanoid_v[1-6]([^0-9]|$)' "$DST" > "$OUT/forbidden_legacy_hits.txt" || true
grep -RInE --binary-files=without-match "${EX[@]}" 'WAVE_[A-Z0-9_]*(SECRET|TOKEN|KEY|CLIENT)' "$DST" > "$OUT/wave_secret_hits.txt" || true
[[ ! -s "$OUT/forbidden_identity_hits.txt" && ! -s "$OUT/forbidden_legacy_hits.txt" && ! -s "$OUT/wave_secret_hits.txt" ]]
# Preserve exact RC34 lineage while allowing only the mandatory deterministic RuinsCiv identity/avatar-reference migration.
EXPECTED_SANITIZED_WORLD="$OUT/WorldMain.RC34.expected_sanitized.gd"
cp "$REC/WorldMain.RC34.proven.gd" "$EXPECTED_SANITIZED_WORLD"
sanitize_active_text "$EXPECTED_SANITIZED_WORLD"
[[ "$(sha "$DST/native/world/WorldMain.gd")" == "$(sha "$EXPECTED_SANITIZED_WORLD")" ]] || { echo RC34_POST_MIGRATION_LINEAGE_MISMATCH; exit 45; }
[[ "$(sha "$DST/web/static/assets/avatars/stage16a/thf_mpfb_stage16a_ual12_animated.glb")" == "$EXPECTED_AVATAR" ]]
find "$DST" -type f | grep -Ei '(downtown|city|nature|house|interior|furniture|street|transport|ruin)' | sort > "$OUT/environment_assets.txt" || true
find "$DST" -type f | grep -Ei '(wardrobe|cloth|shoe|footwear|hair|viseme|face|avatar|animation|ik|pbr|weather|day|night)' | sort > "$OUT/avatar_feature_assets.txt" || true
cat > "$OUT/RUINSCIV_CANDIDATE_PREP_EVIDENCE.txt" <<EOF
RUINSCIV_CANDIDATE_PREP=PASS
version=V5
public_name=RuinsCiv
qa_package=$QA_PACKAGE
rc34_source_sha256=$EXPECTED_WORLD
world_post_identity_migration_sha256=$(sha "$DST/native/world/WorldMain.gd")
avatar_sha256=$(sha "$DST/web/static/assets/avatars/stage16a/thf_mpfb_stage16a_ual12_animated.glb")
active_forbidden_identity_hits=0
active_forbidden_legacy_reference_hits=0
active_wave_secret_hits=0
rc34_lineage_preserved=TRUE
source_mutated=FALSE
physical_device_status=PENDING
final_or_play_ready=FALSE
EOF
cat "$OUT/RUINSCIV_CANDIDATE_PREP_EVIDENCE.txt"
