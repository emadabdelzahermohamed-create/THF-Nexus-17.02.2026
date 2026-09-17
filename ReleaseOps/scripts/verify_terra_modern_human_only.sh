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

# No deprecated humanoid asset or import sidecar may remain in the active avatar directory.
legacy_name_hits=""
if [[ -d "$ROOT/web/static/assets/avatars" ]]; then
  legacy_name_hits="$(find "$ROOT/web/static/assets/avatars" -maxdepth 1 -type f \( \
    -iname 'thf_humanoid_v1*' -o -iname 'thf_humanoid_v2*' -o \
    -iname 'thf_humanoid_v3*' -o -iname 'thf_humanoid_v4*' -o \
    -iname 'thf_humanoid_v5*' -o -iname 'thf_humanoid_v6*' \
  \) -print 2>/dev/null || true)"
fi
if [[ -n "$legacy_name_hits" ]]; then
  printf '%s\n' "$legacy_name_hits" >&2
  fail "legacy_humanoid_file_present" 22
fi

# Only active runtime/config source is authoritative. Historical release evidence is
# preserved for audit but may not drive runtime fallback or export behavior.
scan_paths=()
for p in project.godot export_presets.cfg native config web/static android/app; do
  [[ -e "$ROOT/$p" ]] && scan_paths+=("$ROOT/$p")
done
if ((${#scan_paths[@]})); then
  legacy_ref_hits="$(grep -RIE \
    --exclude-dir=.git --exclude-dir=.godot --exclude-dir=build \
    --exclude='*RELEASE_MANIFEST*' --exclude='*PROVENANCE*' --exclude='*PACKAGE_SHA*' \
    --exclude='README_AR.md' --exclude='*.sha256' \
    'thf_humanoid_v[1-6]' "${scan_paths[@]}" 2>/dev/null || true)"
  if [[ -n "$legacy_ref_hits" ]]; then
    printf '%s\n' "$legacy_ref_hits" >&2
    fail "legacy_humanoid_runtime_or_export_reference" 23
  fi
fi

# The actual native runtime must name the approved human path when it exposes a lite/remote fallback.
if [[ -f "$ROOT/native/world/WorldMain.gd" ]] && grep -q 'REMOTE_LITE_PATH' "$ROOT/native/world/WorldMain.gd"; then
  grep -q 'REMOTE_LITE_PATH.*thf_mpfb_stage16a_ual12_animated\.glb' "$ROOT/native/world/WorldMain.gd" \
    || fail "remote_lite_path_not_canonical_mpfb" 24
fi

printf 'TERRA_MODERN_HUMAN_ONLY=PASS canonical=%s sha256=%s\n' "$CANONICAL_REL" "$actual_sha"
