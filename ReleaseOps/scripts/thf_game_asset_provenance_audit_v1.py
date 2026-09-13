#!/usr/bin/env python3
"""Read-only asset/provenance audit for canonical THF game source ZIPs.

The archive is never extracted or modified. The audit detects unsafe members,
case-insensitive collisions, symlink-like entries, oversized assets, and inventories
3D/avatar/animation/provenance signals relevant to MakeHuman/MPFB/UAL integration.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import PurePosixPath, Path
import re
import stat
import zipfile

ASSET_EXTS={'.glb','.gltf','.fbx','.blend','.obj','.dae','.vrm','.anim','.tres','.tscn','.png','.jpg','.jpeg','.webp','.exr','.hdr','.ogg','.wav','.mp3'}
MODEL_EXTS={'.glb','.gltf','.fbx','.blend','.obj','.dae','.vrm'}
ANIM_EXTS={'.anim','.fbx','.glb','.gltf','.tres','.tscn'}
PROVENANCE_NAMES=('license','licence','copying','copyright','credits','attribution','authors','notice','readme')
AVATAR_MARKERS=('avatar','character','human','makehuman','mpfb','skin','face','hair','viseme','rig','skeleton')
ANIMATION_MARKERS=('animation','anim','motion','locomotion','ual','retarget','ik','inverse_kinematic')

def sha256_file(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):
            h.update(chunk)
    return h.hexdigest()

def unsafe_name(name: str) -> bool:
    p=PurePosixPath(name)
    return name.startswith('/') or '..' in p.parts or bool(re.match(r'^[A-Za-z]:',name))

def is_symlink(info: zipfile.ZipInfo) -> bool:
    mode=(info.external_attr >> 16) & 0xFFFF
    return stat.S_ISLNK(mode)

def audit(path: Path, expected_sha: str|None=None) -> dict:
    actual=sha256_file(path)
    if expected_sha and actual.lower()!=expected_sha.lower():
        raise ValueError(f'archive SHA mismatch expected={expected_sha.lower()} actual={actual.lower()}')
    if not zipfile.is_zipfile(path):
        raise ValueError('not a valid ZIP archive')
    unsafe=[]; symlinks=[]; collisions=[]; oversized=[]
    assets=[]; models=[]; anim=[]; provenance=[]; avatar=[]; animation_markers=[]
    seen={}
    total_uncompressed=0
    with zipfile.ZipFile(path) as z:
        for i in z.infolist():
            if i.is_dir(): continue
            name=i.filename.replace('\\','/')
            low=name.casefold()
            if unsafe_name(name): unsafe.append(name)
            if is_symlink(i): symlinks.append(name)
            prior=seen.get(low)
            if prior and prior!=name: collisions.append([prior,name])
            else: seen[low]=name
            total_uncompressed += i.file_size
            if i.file_size > 512*1024*1024: oversized.append({'path':name,'bytes':i.file_size})
            suffix=PurePosixPath(low).suffix
            if suffix in ASSET_EXTS: assets.append(name)
            if suffix in MODEL_EXTS: models.append(name)
            if suffix in ANIM_EXTS: anim.append(name)
            base=PurePosixPath(low).name
            if any(m in base for m in PROVENANCE_NAMES): provenance.append(name)
            if any(m in low for m in AVATAR_MARKERS): avatar.append(name)
            if any(m in low for m in ANIMATION_MARKERS): animation_markers.append(name)
    safety_pass=not unsafe and not symlinks and not collisions
    return {
        'schema':'thf-game-asset-provenance-audit-v1',
        'archive':path.name,
        'archive_sha256':actual,
        'safety_status':'PASS' if safety_pass else 'FAIL',
        'unsafe_member_count':len(unsafe),
        'symlink_member_count':len(symlinks),
        'casefold_collision_count':len(collisions),
        'oversized_asset_count':len(oversized),
        'file_count':len(seen),
        'total_uncompressed_bytes':total_uncompressed,
        'asset_file_count':len(assets),
        'model_file_count':len(models),
        'animation_capable_file_count':len(anim),
        'avatar_character_marker_count':len(set(avatar)),
        'animation_motion_marker_count':len(set(animation_markers)),
        'provenance_document_count':len(set(provenance)),
        'integration_signals':{
            'makehuman_or_mpfb_named':any(('makehuman' in x.casefold() or 'mpfb' in x.casefold()) for x in avatar),
            'ual_named':any('ual' in x.casefold() for x in animation_markers),
            'avatar_or_character_assets_present':bool(avatar),
            'animation_or_motion_assets_present':bool(animation_markers),
            'provenance_documents_present':bool(provenance),
        },
        'samples':{
            'models':models[:25],
            'avatar_character':sorted(set(avatar))[:25],
            'animation_motion':sorted(set(animation_markers))[:25],
            'provenance':sorted(set(provenance))[:25],
            'unsafe':unsafe[:25],
            'symlinks':symlinks[:25],
            'casefold_collisions':collisions[:25],
            'oversized':oversized[:25],
        },
        'canonical_archive_mutated':False,
    }

def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('archive')
    ap.add_argument('--expected-sha256')
    ap.add_argument('--json-out')
    a=ap.parse_args()
    if a.expected_sha256 and not re.fullmatch(r'[0-9a-fA-F]{64}',a.expected_sha256):
        raise SystemExit('expected SHA must be 64 hex characters')
    try:
        result=audit(Path(a.archive),a.expected_sha256)
    except Exception as e:
        print(json.dumps({'status':'FAIL','error':str(e)},indent=2))
        return 2
    text=json.dumps(result,indent=2,sort_keys=True)+'\n'
    if a.json_out: Path(a.json_out).write_text(text,encoding='utf-8')
    print(text,end='')
    return 0 if result['safety_status']=='PASS' else 2

if __name__=='__main__':
    raise SystemExit(main())
