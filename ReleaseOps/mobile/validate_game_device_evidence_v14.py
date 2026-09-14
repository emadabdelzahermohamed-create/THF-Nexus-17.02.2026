#!/usr/bin/env python3
"""V14: bind gameplay capability PASS claims to semantic, SHA-bound evidence bytes."""
from __future__ import annotations
import argparse, importlib.util, re, sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
S=importlib.util.spec_from_file_location('v13',HERE/'validate_game_device_evidence_v13.py'); V13=importlib.util.module_from_spec(S); assert S and S.loader; sys.modules[S.name]=V13; S.loader.exec_module(V13)
V3,V4=V13.V3,V13.V4
INT=re.compile(r'^\d+$')
BASE={
 'touch':('THF_TOUCH_EVENTS_OBSERVED',),
 'orientation_layout':('THF_LAYOUT_SAFE_AREA_OK','THF_ORIENTATION_OK'),
 'core_user_journey':('THF_CORE_JOURNEY_COMPLETED',),
 'gameplay_interaction':('THF_GAMEPLAY_INTERACTION',),
}
PRODUCT={
 'terra':{'avatar_or_player_load':('THF_AVATAR_LOADED',),'movement_camera':('THF_PLAYER_MOVED','THF_CAMERA_MOVED'),'world_npc_interaction':('THF_WORLD_INTERACTION',)},
 'rift':{'avatar_or_player_load':('THF_AVATAR_LOADED',),'movement_camera':('THF_PLAYER_MOVED','THF_CAMERA_MOVED'),'world_npc_interaction':('THF_WORLD_INTERACTION',),'combat':('THF_COMBAT_ACTION','THF_COMBAT_STATE_CHANGED')},
 'spark':{'learning_progression':('THF_LEARNING_PROGRESS_BEFORE','THF_LEARNING_PROGRESS_AFTER')},
 'learn_games':{'learning_progression':('THF_LEARNING_PROGRESS_BEFORE','THF_LEARNING_PROGRESS_AFTER')},
 'rush':{'sensor_motion':('THF_SENSOR_EVENTS_OBSERVED',),'repetition_counting':('THF_REPS_BEFORE','THF_REPS_AFTER')},
 'fitness_games':{'sensor_motion':('THF_SENSOR_EVENTS_OBSERVED',),'repetition_counting':('THF_REPS_BEFORE','THF_REPS_AFTER')},
}
def one(text,key):
 p=key+'='; v=[x[len(p):].strip() for x in text.splitlines() if x.startswith(p)]; return v[0] if len(v)==1 else None
def validate_bundle(registry,registry_sha,evidence,root):
 errors=list(V13.validate_bundle(registry,registry_sha,evidence,root)); product=evidence.get('product'); obs=evidence.get('manual_observations') if isinstance(evidence.get('manual_observations'),dict) else {}; session=evidence.get('session') if isinstance(evidence.get('session'),dict) else {}; sid=session.get('session_id'); package=evidence.get('package')
 req=dict(BASE); req.update(PRODUCT.get(product,{}))
 for key,markers in req.items():
  row=obs.get(key); p=V4._safe_evidence_path(root,row.get('evidence_ref') if isinstance(row,dict) else None)
  if p is None or not p.is_file(): errors.append(f'V14 {key}: semantic evidence file required'); continue
  text=p.read_text(encoding='utf-8',errors='replace')
  if one(text,'THF_SESSION_ID')!=sid: errors.append(f'V14 {key}: session identity mismatch')
  if one(text,'THF_PACKAGE')!=package: errors.append(f'V14 {key}: package identity mismatch')
  if one(text,'THF_CAPABILITY')!=key: errors.append(f'V14 {key}: capability marker mismatch')
  if one(text,'THF_RESULT')!='PASS': errors.append(f'V14 {key}: PASS marker required')
  vals={m:one(text,m) for m in markers}
  if key in {'learning_progression','repetition_counting'}:
   a,b=list(vals.values());
   if not(a and b and INT.fullmatch(a) and INT.fullmatch(b) and int(b)>int(a)): errors.append(f'V14 {key}: strictly increasing before/after counters required')
  elif key in {'touch','sensor_motion'}:
   v=next(iter(vals.values()));
   if not(v and INT.fullmatch(v) and int(v)>0): errors.append(f'V14 {key}: positive observed event count required')
  else:
   for m,v in vals.items():
    if v!='TRUE': errors.append(f'V14 {key}: {m}=TRUE required')
 if product in {'terra','rift'}:
  row=obs.get('orientation_layout'); p=V4._safe_evidence_path(root,row.get('evidence_ref') if isinstance(row,dict) else None)
  if p and p.is_file() and one(p.read_text(errors='replace'),'THF_SENSOR_LANDSCAPE')!='TRUE': errors.append('V14 Terra/Rift require THF_SENSOR_LANDSCAPE=TRUE')
 if evidence.get('final_or_play_ready') is not False: errors.append('V14 cannot self-promote FINAL/PLAY_READY')
 return errors
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('registry',type=Path); ap.add_argument('evidence',type=Path); ap.add_argument('evidence_root',type=Path); n=ap.parse_args(); r,rs=V3.load_json(n.registry); e,_=V3.load_json(n.evidence); x=validate_bundle(r,rs,e,n.evidence_root)
 if x:
  [print('ERROR: '+i,file=sys.stderr) for i in x]; print('THF_GAME_PHYSICAL_DEVICE_EVIDENCE_V14=FAIL\nFINAL_OR_PLAY_READY=FALSE'); return 1
 print('THF_GAME_PHYSICAL_DEVICE_EVIDENCE_V14=PASS\nGAMEPLAY_SEMANTIC_EVIDENCE_BOUND=TRUE\nFINAL_OR_PLAY_READY=FALSE'); return 0
if __name__=='__main__': raise SystemExit(main())
