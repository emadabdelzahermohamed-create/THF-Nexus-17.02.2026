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
 'terra': {
   'name':'RuinsCiv', 'package':'com.topherofit.ruins.civ',
   'version':'RC34 baseline / RuinsCiv identity migration',
   'source':'eaa2ae79b4f85781903e7c7909910758344422209baa650cf7cf9fd397bdbd68',
   'candidate':None,
 },
 'rift': {
   'name':'THF Arena', 'package':'com.topherofit.thf.rift',
   'version':'4.7.5-rc41',
   'source':'29edaa0eb594a25d0960cb176765663f9bab3d91a60fd98016474ff5695cb95d',
   'candidate':None,
 },
 'spark': {
   'name':'THF Learn Games', 'package':'com.topherofit.thf.spark',
   'version':'APPS RC4 + real-game overlay',
   'source':'58a32690ea69b6fd62a977145079e0ad6e75061724a786d5db9276b95ec48d43',
   'candidate':'9fffc4d97e64faf1d92ec6900968902570e2739d6751d752377ebde2589165ea',
 },
 'rush': {
   'name':'THF Motion Games', 'package':'com.topherofit.thf.rush',
   'version':'APPS RC4 + Native Verified-Motion V2 + product identity fix',
   'source':'766936c25700643bcf813d4e754b287f79810eebe859bd45388391bf57bf771c',
   'candidate':'f81ecebd5017500ac6dd980d58ee2eca717f210f2ede18747b3a971a1779072f',
 },
}
sha64 = re.compile(r'^[0-9a-f]{64}$')
seen_candidates = set()
for key,e in expected.items():
    g=games[key]
    if g.get('user_facing_name') != e['name']: die(f'{key}:name')
    if g.get('canonical_package_id') != e['package']: die(f'{key}:package')
    if g.get('authoritative_version') != e['version']: die(f'{key}:version')
    if g.get('authoritative_source_sha256') != e['source']: die(f'{key}:source_sha')
    if not sha64.fullmatch(e['source']): die(f'{key}:source_sha_format')
    if g.get('target_sdk') != 36 or g.get('arm64_required') is not True: die(f'{key}:android_contract')
    if g.get('physical_device_status') != 'PENDING': die(f'{key}:device_status')
    cand=g.get('eligible_candidate_apk_sha256')
    if cand != e['candidate']: die(f'{key}:exact_candidate_sha')
    if cand is not None and not sha64.fullmatch(cand): die(f'{key}:candidate_sha_format')
    superseded=g.get('superseded_apk_sha256',[])
    if len(superseded) != len(set(superseded)): die(f'{key}:duplicate_superseded_sha')
    for old in superseded:
        if not sha64.fullmatch(old): die(f'{key}:superseded_sha_format')
    if cand is not None and cand in superseded: die(f'{key}:candidate_is_superseded')
    if cand is not None:
        if cand in seen_candidates: die(f'{key}:candidate_sha_reused_cross_product')
        seen_candidates.add(cand)

if games['terra'].get('qa_package_id') != 'com.topherofit.ruins.civ.phoneqa':
    die('terra:qa_package')
if games['rift']['eligible_candidate_apk_sha256'] is not None:
    die('rift_candidate_must_remain_none_until_rc41_build')

rush=games['rush']
if rush.get('candidate_status') != 'PACKAGE_PASS_PHYSICAL_DEVICE_PENDING':
    die('rush_candidate_status')
if rush.get('candidate_run_id') != 34904322777 or rush.get('candidate_artifact_id') != 10371807756:
    die('rush_candidate_provenance')
if rush.get('candidate_artifact_digest') != 'sha256:c158383f5b2183be0d677c65748376d44fc2f75a989f136ddfd62a126ab4f0d2':
    die('rush_artifact_digest')
for k in ('verified_motion_required','reward_bearing_health_evidence_required','product_specific_icon_required'):
    if rush.get(k) is not True: die('rush_missing_'+k)

matrix=MATRIX.read_text(encoding='utf-8')
for marker in [
 'RC34 Phone V4',
 'e0ac997e1cdb0145b765884d8a59a70403821d1d1e19fbf6a05adcc4640cfbec',
 'RC41 `4.7.5-rc41`',
 '29edaa0eb594a25d0960cb176765663f9bab3d91a60fd98016474ff5695cb95d',
 'APPS RC4 + real-game overlay',
 '9fffc4d97e64faf1d92ec6900968902570e2739d6751d752377ebde2589165ea',
 'Native Verified-Motion V2',
 'REJECTED — iconless candidate',
 'f81ecebd5017500ac6dd980d58ee2eca717f210f2ede18747b3a971a1779072f',
 'NONE — RC37 APK superseded',
 'FINAL/PLAY_READY'
]:
    if marker not in matrix: die('matrix_missing:'+marker)

for p in (ROOT/'.github/workflows').glob('*rift*.yml'):
    text=p.read_text(encoding='utf-8')
    if 'RC37' not in text: continue
    positive = re.search(r'(FINAL_OR_PLAY_READY|PLAY_READY|FINAL_STATUS)\s*[=:]\s*(TRUE|PASS|READY)', text, re.I)
    release_op = re.search(r'\b(promote|promotion|production[-_ ]?sign(?:ing)?|play[-_ ]?(?:upload|publish)|store[-_ ]?publish|production[-_ ]?(?:deploy|cutover))\b', text, re.I)
    if positive or release_op: die(f'rift:stale_rc37_promotion_workflow:{p.name}')

print('LATEST_GAME_AUTHORITY=PASS')
for k in ('terra','rift','spark','rush'):
    g=games[k]
    print(f'{k}_version={g["authoritative_version"]}')
    print(f'{k}_source_sha256={g["authoritative_source_sha256"]}')
    print(f'{k}_candidate_apk_sha256={g.get("eligible_candidate_apk_sha256") or "NONE"}')
print('FINAL_OR_PLAY_READY=FALSE')
