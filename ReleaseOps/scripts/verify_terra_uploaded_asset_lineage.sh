#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="${1:-.}"
fail(){ printf 'TERRA_UPLOADED_ASSET_LINEAGE=FAIL reason=%s\n' "$1" >&2; exit "${2:-1}"; }

vault="$ROOT/config/asset_vault.json"
renderer="$ROOT/config/renderer3d.json"
provenance="$ROOT/STAGE16A_VISUAL_PROVENANCE.json"
visual_root="$ROOT/web/static/assets/visual16a"
anim="$ROOT/config/animations.json"

[[ -s "$vault" ]] || fail "asset_vault_missing" 40
[[ -s "$renderer" ]] || fail "renderer_config_missing" 41
[[ -s "$provenance" ]] || fail "stage16a_visual_provenance_missing" 42
[[ -d "$visual_root" ]] || fail "visual16a_runtime_root_missing" 43
[[ -s "$anim" ]] || fail "animation_config_missing" 44

required_archives=(
  "Downtown City MegaKit[Standard].zip"
  "Furniture Pack - March 2019-20260903T032829Z-1-001.zip"
  "Public Transport Pack - Feb 2017-20260903T033040Z-1-001.zip"
  "Street Pack by @Quaternius-20260903T032033Z-1-001.zip"
  "Ultimate House Interior Pack - June 2020-20260903T032601Z-1-001.zip"
  "Ultimate Nature Pack - Jun 2019-20260903T032653Z-1-001.zip"
  "Universal Animation Library 2[Standard].zip"
  "Universal Animation Library[Standard].zip"
)
for name in "${required_archives[@]}"; do
  grep -Fq "$name" "$vault" || fail "uploaded_archive_not_registered:$name" 45
done

# Exact minimum file counts measured from the accepted RC34/Stage16A runtime on
# 2026-09-17. These are regression floors, not arbitrary quality estimates.
declare -A min_files=(
  [downtown]=20
  [street]=6
  [transport]=6
  [interior]=10
  [nature]=8
  [furniture]=2
  [ruins]=10
)
for d in downtown street transport interior nature furniture ruins; do
  [[ -d "$visual_root/$d" ]] || fail "runtime_asset_family_missing:$d" 46
  count="$(find "$visual_root/$d" -type f | wc -l | tr -d ' ')"
  [[ "$count" -ge "${min_files[$d]}" ]] || fail "runtime_asset_family_regressed:$d:$count<${min_files[$d]}" 47
  printf 'TERRA_ASSET_FAMILY=%s files=%s baseline=%s\n' "$d" "$count" "${min_files[$d]}"
done

required_sources=(
  "Downtown City MegaKit Standard"
  "Street Pack"
  "Public Transport Pack"
  "Ultimate House Interior Pack"
  "Ultimate Nature Pack"
  "Furniture Pack"
  "Ultimate Modular Ruins Pack"
)
for source in "${required_sources[@]}"; do
  grep -Fq "$source" "$provenance" || fail "visual_provenance_source_missing:$source" 48
done

grep -Fq '"visual_asset_root": "/static/assets/visual16a"' "$renderer" || fail "renderer_visual16a_not_active" 49
grep -Fq 'thf_mpfb_stage16a_ual12_animated.glb' "$renderer" || fail "renderer_modern_avatar_not_active" 50
grep -Fq 'thf_mpfb_stage16a_ual12_animated.glb' "$anim" || fail "animation_modern_avatar_not_active" 51
grep -Fq 'THF-MPFB-137-UAL1-UAL2-v3' "$anim" || fail "ual12_retarget_profile_missing" 52

# Accepted current runtime baseline is 66 files total. New work may add assets,
# but any future candidate with fewer files is considered a visual-lineage regression.
files="$(find "$visual_root" -type f | wc -l | tr -d ' ')"
bytes="$(find "$visual_root" -type f -printf '%s\n' | awk '{s+=$1} END{printf "%.0f",s+0}')"
[[ "$files" -ge 66 ]] || fail "visual16a_runtime_file_count_regressed:$files<66" 53
[[ "$bytes" -ge 1000000 ]] || fail "visual16a_runtime_bytes_too_low:$bytes" 54

printf 'TERRA_UPLOADED_ASSET_LINEAGE=PASS files=%s baseline_files=66 bytes=%s\n' "$files" "$bytes"
