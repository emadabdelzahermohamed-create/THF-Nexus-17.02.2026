#!/usr/bin/env python3
"""V15: bind gameplay semantic evidence to the live foreground game process."""
from __future__ import annotations
import argparse, hashlib, importlib.util, re, sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
S=importlib.util.spec_from_file_location('v14',HERE/'validate_game_device_evidence_v14.py'); V14=importlib.util.module_from_spec(S); assert S and S.loader; sys.modules[S.name]=V14; S.loader.exec_module(V14)
V3,V4=V14.V3,V14.V4
PID=re.compile(r'^[1-9]\d*$')
METHOD='ADB_DUMPSYS_ACTIVITY_PIDOF'

def one(text,key):
 p=key+'='; v=[x[len(p):].strip() for x in text.splitlines() if x.startswith(p)]; return v[0] if len(v)==1 else None

def sha256(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def validate_bundle(registry,registry_sha,evidence,root):
 errors=list(V14.validate_bundle(registry,registry_sha,evidence,root))
 product=evidence.get('product'); obs=evidence.get('manual_observations') if isinstance(evidence.get('manual_observations'),dict) else {}
 proc=evidence.get('process_provenance') if isinstance(evidence.get('process_provenance'),dict) else {}
 session=evidence.get('session') if isinstance(evidence.get('session'),dict) else {}; sid=session.get('session_id'); package=evidence.get('package')
 req=dict(V14.BASE); req.update(V14.PRODUCT.get(product,{}))
 for key in req:
  gameplay=obs.get(key) if isinstance(obs.get(key),dict) else {}; gameplay_sha=gameplay.get('evidence_sha256')
  row=proc.get(key) if isinstance(proc.get(key),dict) else {}; p=V4._safe_evidence_path(root,row.get('evidence_ref'))
  if p is None or not p.is_file(): errors.append(f'V15 {key}: foreground process provenance file required'); continue
  expected=row.get('evidence_sha256')
  if not isinstance(expected,str) or expected!=sha256(p): errors.append(f'V15 {key}: process provenance SHA mismatch')
  text=p.read_text(encoding='utf-8',errors='replace')
  checks={
   'THF_SESSION_ID':sid,'THF_PACKAGE':package,'THF_CAPABILITY':key,
   'THF_FOREGROUND_PACKAGE':package,'THF_PROCESS_CAPTURE_METHOD':METHOD,
   'THF_PROCESS_ALIVE_AFTER':'TRUE','THF_GAMEPLAY_EVIDENCE_SHA256':gameplay_sha,
  }
  for marker,want in checks.items():
   if not isinstance(want,str) or one(text,marker)!=want: errors.append(f'V15 {key}: {marker} mismatch')
  pid=one(text,'THF_FOREGROUND_PID'); resumed=one(text,'THF_RESUMED_PID')
  if not(pid and PID.fullmatch(pid)): errors.append(f'V15 {key}: valid foreground PID required')
  if resumed!=pid: errors.append(f'V15 {key}: resumed PID must equal foreground PID')
  if one(text,'THF_ACTIVITY_RESUMED')!='TRUE': errors.append(f'V15 {key}: resumed activity proof required')
 if evidence.get('final_or_play_ready') is not False: errors.append('V15 cannot self-promote FINAL/PLAY_READY')
 return errors

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('registry',type=Path); ap.add_argument('evidence',type=Path); ap.add_argument('evidence_root',type=Path); n=ap.parse_args()
 r,rs=V3.load_json(n.registry); e,_=V3.load_json(n.evidence); x=validate_bundle(r,rs,e,n.evidence_root)
 if x:
  [print('ERROR: '+i,file=sys.stderr) for i in x]; print('THF_GAME_PHYSICAL_DEVICE_EVIDENCE_V15=FAIL\nFINAL_OR_PLAY_READY=FALSE'); return 1
 print('THF_GAME_PHYSICAL_DEVICE_EVIDENCE_V15=PASS\nFOREGROUND_PROCESS_PROVENANCE_BOUND=TRUE\nFINAL_OR_PLAY_READY=FALSE'); return 0
if __name__=='__main__': raise SystemExit(main())
