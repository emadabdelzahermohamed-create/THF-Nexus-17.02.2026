#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="${1:-.}"
CANONICAL_REL="${THF_TERRA_CANONICAL_AVATAR:-web/static/assets/avatars/stage16a/thf_mpfb_stage16a_ual12_animated.glb}"
EXPECTED_SHA="${THF_TERRA_CANONICAL_AVATAR_SHA256:-}"
CANONICAL="$ROOT/$CANONICAL_REL"

fail() { printf 'TERRA_MODERN_HUMAN_ONLY=FAIL reason=%s\n' "$1" >&2; exit "${2:-1}"; }

[[ -f "$CANONICAL" ]] || fail "canonical_mpfb_missing:$CANONICAL_REL" 20
actual_sha="$(sha256sum "$CANONICAL" | awk '{print $1}')"
if [[ -n "$EXPECTED_SHA" && "$actual_sha" != "$EXPECTED_SHA" ]]; then
  fail "canonical_mpfb_sha_mismatch expected=$EXPECTED_SHA actual=$actual_sha" 21
fi

legacy_name_hits="$(find "$ROOT" -type f \( \
  -iname 'thf_humanoid_v1*' -o -iname 'thf_humanoid_v2*' -o \
  -iname 'thf_humanoid_v3*' -o -iname 'thf_humanoid_v4*' -o \
  -iname 'thf_humanoid_v5*' -o -iname 'thf_humanoid_v6*' \
\) -print 2>/dev/null || true)"
if [[ -n "$legacy_name_hits" ]]; then
  printf '%s\n' "$legacy_name_hits" >&2
  fail "legacy_humanoid_file_present" 22
fi

scan_paths=()
for p in project.godot export_presets.cfg native web android ReleaseOps/scripts; do
  [[ -e "$ROOT/$p" ]] && scan_paths+=("$ROOT/$p")
done
if ((${#scan_paths[@]})); then
  legacy_ref_hits="$(grep -RIE --exclude-dir=.git --exclude='TERRA_ACTIVE_ASSET_POLICY_V1_20260917.json' \
    'thf_humanoid_v[1-6]' "${scan_paths[@]}" 2>/dev/null || true)"
  if [[ -n "$legacy_ref_hits" ]]; then
    printf '%s\n' "$legacy_ref_hits" >&2
    fail "legacy_humanoid_runtime_or_export_reference" 23
  fi
fi

printf 'TERRA_MODERN_HUMAN_ONLY=PASS canonical=%s sha256=%s\n' "$CANONICAL_REL" "$actual_sha"
