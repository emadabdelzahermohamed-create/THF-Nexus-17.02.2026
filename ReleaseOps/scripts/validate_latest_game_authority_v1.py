#!/usr/bin/env python3
from __future__ import annotations
import json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
REG = ROOT / 'ReleaseOps/games/LATEST_GAME_AUTHORITY_V1.json'
MATRIX = ROOT / 'ReleaseOps/ANDROID_QA_MATRIX_V1_20260913.md'

def die(msg: str) -> None:
    print(f'LATEST_GAME_AUTHORITY=FAIL {msg}', file=sys.stderr)
    raise SystemExit(2)

def non_game_history(p: pathlib.Path) -> bool:
    # Apps-lineage workflows are read-only historical discovery for the non-game factory.
    # They may contain old Spark/Rush observations but cannot promote game candidates.
    return p.parent.name == 'workflows' and p.name.startswith('thf-apps-authoritative-lineage-v')

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

if games['rift']['eligible_candidate_apk_sha256'] is not None:
    die('rift_candidate_must_remain_none_until_rc41_build')
if games['rush']['eligible_candidate_apk_sha256'] is not None:
    die('rush_candidate_must_remain_none_until_verified_motion_v2_build')
if games['rush'].get('verified_motion_required') is not True:
    die('rush_verified_motion_not_required')
if games['rush'].get('reward_bearing_health_evidence_required') is not True:
    die('rush_reward_health_evidence_not_required')

matrix=MATRIX.read_text(encoding='utf-8')
for marker in [
 'RC41 `4.7.5-rc41`',
 '29edaa0eb594a25d0960cb176765663f9bab3d91a60fd98016474ff5695cb95d',
 'Verified-Motion V2',
 'NONE — RC37 APK superseded',
 'NONE — previous game APK superseded by Verified-Motion V2',
 'FINAL/PLAY_READY'
]:
    if marker not in matrix: die('matrix_missing:'+marker)

scan_roots=[ROOT/'.github/workflows', ROOT/'ReleaseOps/scripts', ROOT/'ReleaseOps/mobile', ROOT/'ReleaseOps/validators']
for key,g in games.items():
    for bad in g.get('superseded_apk_sha256',[]):
        if len(bad) != 64:
            continue
        for base in scan_roots:
            if not base.exists(): continue
            for p in base.rglob('*'):
                if non_game_history(p): continue
                if not p.is_file() or p.suffix not in {'.yml','.yaml','.py','.sh','.json','.md'}: continue
                try: text=p.read_text(encoding='utf-8')
                except UnicodeDecodeError: continue
                if bad in text:
                    die(f'{key}:superseded_hash_in_operational_file:{p.relative_to(ROOT)}')

for p in (ROOT/'.github/workflows').glob('*rift*.yml'):
    text=p.read_text(encoding='utf-8')
    if 'RC37' in text and ('FINAL' in text or 'PLAY_READY' in text or 'promot' in text.lower()):
        die(f'rift:stale_rc37_promotion_workflow:{p.name}')

print('LATEST_GAME_AUTHORITY=PASS')
for k in ('terra','rift','spark','rush'):
    g=games[k]
    print(f'{k}_version={g["authoritative_version"]}')
    print(f'{k}_source_sha256={g["authoritative_source_sha256"]}')
    print(f'{k}_candidate_apk_sha256={g.get("eligible_candidate_apk_sha256") or "NONE"}')
print('FINAL_OR_PLAY_READY=FALSE')
