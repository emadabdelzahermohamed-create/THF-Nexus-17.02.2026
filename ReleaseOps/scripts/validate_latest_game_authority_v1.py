#!/usr/bin/env python3
from __future__ import annotations
import json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
REG = ROOT / 'ReleaseOps/games/LATEST_GAME_AUTHORITY_V1.json'
MATRIX = ROOT / 'ReleaseOps/ANDROID_QA_MATRIX_V1_20260913.md'

def die(msg: str) -> None:
    print(f'LATEST_GAME_AUTHORITY=FAIL {msg}', file=sys.stderr)
    raise SystemExit(2)

r = json.loads(REG.read_text(encoding='utf-8'))
if r.get('schema') != 1 or r.get('final_or_play_ready') is not False:
    die('registry_schema_or_final_flag')

games = r.get('games') or {}
required = {'terra','rift','spark','rush'}
if set(games) != required:
    die(f'game_set={sorted(games)}')

expected = {
 'terra': ('THF World','com.topherofit.thf.terra','eaa2ae79b4f85781903e7c7909910758344422209baa650cf7cf9fd397bdbd68'),
 'rift': ('THF Arena','com.topherofit.thf.rift','29edaa0eb594a25d0960cb176765663f9bab3d91a60fd98016474ff5695cb95d'),
 'spark': ('THF Learn Games','com.topherofit.thf.spark','58a32690ea69b6fd62a977145079e0ad6e75061724a786d5db9276b95ec48d43'),
 'rush': ('THF Motion Games','com.topherofit.thf.rush','766936c25700643bcf813d4e754b287f79810eebe859bd45388391bf57bf771c'),
}
sha64 = re.compile(r'^[0-9a-f]{64}$')
for key,(name,pkg,srcsha) in expected.items():
    g=games[key]
    if g.get('user_facing_name') != name: die(f'{key}:name')
    if g.get('canonical_package_id') != pkg: die(f'{key}:package')
    if g.get('authoritative_source_sha256') != srcsha: die(f'{key}:source_sha')
    if not sha64.fullmatch(srcsha): die(f'{key}:source_sha_format')
    if g.get('target_sdk') != 36 or g.get('arm64_required') is not True: die(f'{key}:android_contract')
    if g.get('physical_device_status') != 'PENDING': die(f'{key}:device_status')
    cand=g.get('eligible_candidate_apk_sha256')
    if cand is not None and not sha64.fullmatch(cand): die(f'{key}:candidate_sha_format')
    if cand is not None and cand in g.get('superseded_apk_sha256',[]): die(f'{key}:candidate_is_superseded')

# Current promotion truth is fail-closed. Historical references may remain as audit evidence,
# but no superseded APK may be the registry's eligible candidate.
if games['rift']['eligible_candidate_apk_sha256'] is not None:
    die('rift_candidate_must_remain_none_until_rc41_build')
if games['rush']['eligible_candidate_apk_sha256'] is not None:
    die('rush_candidate_must_remain_none_until_product_icon_rebuild')
if games['rush'].get('authoritative_version') != 'APPS RC4 + Native Verified-Motion V2 + product identity fix':
    die('rush_version_not_product_identity_fixed')
if games['rush'].get('candidate_status') != 'REBUILD_REQUIRED_AFTER_PRODUCT_ICON_FIX':
    die('rush_candidate_status_not_rebuild_required')
if games['rush'].get('verified_motion_required') is not True:
    die('rush_verified_motion_not_required')
if games['rush'].get('reward_bearing_health_evidence_required') is not True:
    die('rush_reward_health_evidence_not_required')
if games['rush'].get('product_specific_icon_required') is not True:
    die('rush_product_icon_not_required')

matrix=MATRIX.read_text(encoding='utf-8')
for marker in [
 'RC41 `4.7.5-rc41`',
 '29edaa0eb594a25d0960cb176765663f9bab3d91a60fd98016474ff5695cb95d',
 'Native Verified-Motion V2',
 'REJECTED — iconless candidate',
 'NONE — rebuild required after product icon fix',
 'NONE — RC37 APK superseded',
 'FINAL/PLAY_READY'
]:
    if marker not in matrix: die('matrix_missing:'+marker)

# Historical RC37 audit artifacts are allowed. Positive release operations are not.
for p in (ROOT/'.github/workflows').glob('*rift*.yml'):
    text=p.read_text(encoding='utf-8')
    if 'RC37' not in text:
        continue
    positive = re.search(r'(FINAL_OR_PLAY_READY|PLAY_READY|FINAL_STATUS)\s*[=:]\s*(TRUE|PASS|READY)', text, re.I)
    release_op = re.search(
        r'\b(promote|promotion|production[-_ ]?sign(?:ing)?|play[-_ ]?(?:upload|publish)|store[-_ ]?publish|production[-_ ]?(?:deploy|cutover))\b',
        text,
        re.I,
    )
    if positive or release_op:
        die(f'rift:stale_rc37_promotion_workflow:{p.name}')

print('LATEST_GAME_AUTHORITY=PASS')
for k in ('terra','rift','spark','rush'):
    g=games[k]
    print(f'{k}_version={g["authoritative_version"]}')
    print(f'{k}_source_sha256={g["authoritative_source_sha256"]}')
    print(f'{k}_candidate_apk_sha256={g.get("eligible_candidate_apk_sha256") or "NONE"}')
print('FINAL_OR_PLAY_READY=FALSE')
