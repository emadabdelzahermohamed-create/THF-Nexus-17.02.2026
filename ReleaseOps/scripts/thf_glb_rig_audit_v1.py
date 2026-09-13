#!/usr/bin/env python3
"""Read-only GLB rig/animation integrity audit for THF game candidates."""
from __future__ import annotations
import argparse, json, pathlib, struct, sys

MAGIC = 0x46546C67
JSON_CHUNK = 0x4E4F534A

def inspect_glb(path: pathlib.Path) -> dict:
    size = path.stat().st_size
    with path.open('rb') as f:
        header = f.read(12)
        if len(header) != 12:
            raise ValueError('truncated GLB header')
        magic, version, declared = struct.unpack('<III', header)
        if magic != MAGIC: raise ValueError('bad GLB magic')
        if version != 2: raise ValueError(f'unsupported GLB version {version}')
        if declared != size: raise ValueError(f'length mismatch declared={declared} actual={size}')
        chunk_header = f.read(8)
        if len(chunk_header) != 8: raise ValueError('missing JSON chunk')
        length, kind = struct.unpack('<II', chunk_header)
        if kind != JSON_CHUNK: raise ValueError('first GLB chunk is not JSON')
        raw = f.read(length)
        if len(raw) != length: raise ValueError('truncated JSON chunk')
    doc = json.loads(raw.rstrip(b'\x00 \t\r\n').decode('utf-8'))
    return {
        'file': path.as_posix(), 'size': size, 'glb_version': version,
        'scenes': len(doc.get('scenes', [])), 'nodes': len(doc.get('nodes', [])),
        'meshes': len(doc.get('meshes', [])), 'skins': len(doc.get('skins', [])),
        'animations': len(doc.get('animations', [])),
        'materials': len(doc.get('materials', [])),
        'accessors': len(doc.get('accessors', [])),
        'has_rig': len(doc.get('skins', [])) > 0,
        'has_animation': len(doc.get('animations', [])) > 0,
    }

def main() -> int:
    ap=argparse.ArgumentParser(); ap.add_argument('root'); ap.add_argument('--json-out',required=True); a=ap.parse_args()
    root=pathlib.Path(a.root).resolve(); assert root.is_dir()
    tokens=('avatar','character','makehuman','mpfb','ual','animated','player')
    rows=[]; errors=[]
    for p in sorted(root.rglob('*.glb')):
        rel=p.relative_to(root).as_posix()
        if not any(t in rel.lower() for t in tokens): continue
        try:
            r=inspect_glb(p); r['file']=rel; rows.append(r)
        except Exception as e: errors.append({'file':rel,'error':type(e).__name__+': '+str(e)})
    result={
      'schema':'thf-glb-rig-audit-v1','candidate_count':len(rows),'error_count':len(errors),
      'rigged_count':sum(1 for r in rows if r['has_rig']),
      'animated_count':sum(1 for r in rows if r['has_animation']),
      'candidates':rows,'errors':errors,'read_only':True,'device_status':'PENDING','final_status':'NOT_FINAL'
    }
    pathlib.Path(a.json_out).write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(result,indent=2,sort_keys=True))
    return 0 if not errors else 2

if __name__=='__main__': sys.exit(main())
