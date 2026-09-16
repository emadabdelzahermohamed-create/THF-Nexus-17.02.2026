#!/usr/bin/env bash
set -uo pipefail
PROJECT="${WAVE_PROJECT:-/root/workspace/wave-mawja}"
STAMP="$(date +%Y%m%d-%H%M%S)"
OUT="${WAVE_RC15_3_OUT:-/root/logs/wave-rc15-3/$STAMP}"
mkdir -p "$OUT"
RESULT="$OUT/RESULT.txt"
: > "$RESULT"
log(){ printf '%s\n' "$*" | tee -a "$RESULT"; }
fail(){ log "FAIL: $*"; exit 1; }
step(){ log "== $* =="; }

[ -d "$PROJECT" ] || fail "project missing: $PROJECT"
[ ! -L "$PROJECT" ] || fail "project root must not be symlink"
REAL_PROJECT="$(readlink -f "$PROJECT")"
case "$REAL_PROJECT" in *THF*|*thf*) fail "THF path rejected: $REAL_PROJECT" ;; esac
cd "$PROJECT"
for d in app components media-server tests android android-twa; do [ -d "$d" ] || fail "missing $d"; done
[ -f package.json ] || fail "package.json missing"
NAME="$(node -p "require('./package.json').name")"
VERSION="$(node -p "require('./package.json').version")"
case "$NAME" in wave-stream|wave-mawja|wave*) ;; *) fail "unexpected package identity: $NAME" ;; esac
[ "$VERSION" = "1.0.0-rc.15.3+auth-abr-evidence" ] || fail "unexpected package version: $VERSION"
log "PASS: WAVE identity $NAME@$VERSION"

step "RC15.3 critical source SHA"
sha256sum -c RC15_3_CRITICAL_SHA256SUMS.txt | tee "$OUT/CRITICAL_SHA.log" || fail "critical source SHA mismatch"

step "dependency-free gates"
python3 -m compileall -q media-server tests scripts || fail "python compile"
python3 -m unittest discover -s tests -p '*_test.py' 2>&1 | tee "$OUT/PYTHON_TESTS.txt" || fail "python tests"
node --test tests/multi-ingest-source.test.mjs tests/service-worker.test.mjs 2>&1 | tee "$OUT/NODE_STANDALONE_TESTS.txt" || fail "node standalone tests"

step "Node dependencies"
if [ ! -d node_modules ]; then
  npm ci --no-audit --no-fund 2>&1 | tee "$OUT/NPM_CI.log" || fail "npm ci (network/registry or dependency issue)"
fi

step "typecheck/build"
npm run typecheck 2>&1 | tee "$OUT/TYPECHECK.log" || fail "typecheck"
npm run build 2>&1 | tee "$OUT/BUILD.log" || fail "web/worker build"

step "Android phone-test APK"
APK_STATE="NOT_EXECUTED_TOOLCHAIN_UNAVAILABLE"
if command -v gradle >/dev/null && [ -n "${ANDROID_HOME:-${ANDROID_SDK_ROOT:-}}" ]; then
  (cd android && DEBUG_BASE_URL="${WAVE_LIVE_URL:-https://wave-mawja.p-my.workers.dev}" bash ./BUILD_PHONE_TEST.sh) 2>&1 | tee "$OUT/ANDROID_BUILD.log" || fail "Android debug build"
  APK="$(find android/app/build/outputs/apk -type f -name '*debug*.apk' | head -n1 || true)"
  [ -n "$APK" ] && [ -f "$APK" ] || fail "debug APK missing after build"
  sha256sum "$APK" | tee "$OUT/APK_SHA256.txt"
  cp -f "$APK" "$OUT/WAVE_MAWJA_RC15_3_PHONE_TEST.apk"
  APK_STATE="DEBUG_APK_BUILD_PASS"
fi
log "ANDROID_BUILD_STATE=$APK_STATE"

python3 - "$OUT" <<'PY'
from pathlib import Path
import json,sys
out=Path(sys.argv[1])
state={
 "checkpoint":"RC15.3-FIRST-PARTY-AUTH-ABR-EVIDENCE",
 "source_tests":"PASS",
 "debug_apk_present":(out/'WAVE_MAWJA_RC15_3_PHONE_TEST.apk').is_file(),
 "production_signed_aab":False,
 "play_approval":False,
 "physical_phone_acceptance":False,
 "cloudflare_deploy_by_rc15_3":False,
 "media_transcode_claim_by_rc15_3":False
}
(out/'RC15_3_EXECUTION_SUMMARY.json').write_text(json.dumps(state,indent=2),encoding='utf-8')
PY
sha256sum "$RESULT" "$OUT/RC15_3_EXECUTION_SUMMARY.json" > "$OUT/SHA256SUMS.txt"
log "PASS: RC15.3 executable gate complete; evidence=$OUT"
