#!/usr/bin/env python3
"""Read-only audit for THF game shared systems on a clean-extracted candidate tree.

Never mutates source. Reports implementation signals for avatar/animation/IK, touch,
world/combat, rendering/performance, local/offline and network/server-authority contracts.
Signals are evidence, not a FINAL/device verdict.
"""
from __future__ import annotations
import argparse, json, pathlib, re, sys

TEXT_EXT={'.gd','.tscn','.tres','.godot','.cfg','.ini','.json','.md','.txt','.kt','.java','.xml','.js','.ts','.tsx'}
PATTERNS={
 'avatar': r'avatar|makehuman|mpfb|humanoid|skeleton3d|bone',
 'animation': r'animationtree|animationplayer|blend[_ -]?tree|ual|retarget',
 'ik': r'\bik\b|two[_ -]?bone|lookatmodifier|skeletonik|foot[_ -]?plant',
 'locomotion': r'characterbody3d|move_and_slide|velocity|locomotion|sprint|jump|crouch',
 'camera': r'camera3d|springarm3d|camera[_ -]?(?:rig|controller)|look[_ -]?(?:input|delta)',
 'touch': r'touchscreenbutton|inputeventscreen|virtual[_ -]?(?:stick|joystick)|touch[_ -]?(?:hud|control)',
 'combat': r'attack|damage|hitbox|hurtbox|weapon|reload|projectile|melee|combat',
 'npc_ai': r'navigationagent3d|npc|state[_ -]?machine|behavior[_ -]?tree|pathfind',
 'world': r'worldenvironment|terrain|weather|day[_ -]?night|rain|snow|time[_ -]?of[_ -]?day',
 'pbr_lighting': r'standardmaterial3d|orm|normal[_ -]?map|light3d|directionallight3d|gi|ssao|ssil',
 'audio_vfx': r'audiostreamplayer|particles3d|gpuparticles3d|vfx|sfx|reverb',
 'lod_occlusion': r'visibility[_ -]?range|lod|occluder|occlusion|multimesh|impostor',
 'performance': r'performance\.|profiler|fps|frame[_ -]?time|object[_ -]?pool|pooling|quality[_ -]?preset',
 'anti_cheat': r'anti[_ -]?cheat|integrity|tamper|speedhack|teleport[_ -]?check|server[_ -]?validate',
 'server_authority': r'server[_ -]?authorit|authoritative|rpc|multiplayerapi|websocket|wss://|https://',
 'offline_local': r'offline|local[_ -]?(?:mode|training|explore)|single[_ -]?player|practice',
 'economy_guard': r'no[_ -]?pay[_ -]?to[_ -]?win|pay[_ -]?to[_ -]?win|ranked|economy|wallet|token',
 'accessibility': r'reduce[_ -]?motion|high[_ -]?contrast|accessibility|data[_ -]?saver|rtl|safe[_ -]?area',
}
COMPILED={k:re.compile(v,re.I) for k,v in PATTERNS.items()}

def scan(root:pathlib.Path):
 out={k:{'files':[], 'matches':0} for k in PATTERNS}
 scanned=0
 for p in root.rglob('*'):
  if not p.is_file() or p.suffix.lower() not in TEXT_EXT:
   continue
  try:
   if p.stat().st_size>3_000_000: continue
   text=p.read_text(errors='ignore')
  except OSError: continue
  scanned+=1
  rel=p.relative_to(root).as_posix()
  for k,rx in COMPILED.items():
   n=len(rx.findall(text))
   if n:
    out[k]['matches']+=n
    if len(out[k]['files'])<25: out[k]['files'].append(rel)
 for v in out.values(): v['files']=sorted(set(v['files']))
 return scanned,out

def main():
 ap=argparse.ArgumentParser();ap.add_argument('root');ap.add_argument('--kind',required=True);ap.add_argument('--json-out',required=True)
 a=ap.parse_args();root=pathlib.Path(a.root).resolve()
 if not root.is_dir(): raise SystemExit('root missing')
 scanned,signals=scan(root)
 required_base=['locomotion','camera','touch']
 if a.kind in {'terra','rift'}: required_base += ['avatar','animation']
 if a.kind=='terra': required_base += ['world']
 if a.kind=='rift': required_base += ['combat']
 missing=[k for k in required_base if signals[k]['matches']==0]
 result={
  'schema':'thf-game-shared-systems-audit-v1','kind':a.kind,'read_only':True,'files_scanned':scanned,
  'signals':signals,'required_signal_set':required_base,'required_missing':missing,
  'shared_systems_status':'PASS' if not missing else 'BLOCKED',
  'device_status':'PENDING','final_status':'NOT_FINAL'
 }
 pathlib.Path(a.json_out).write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
 print(json.dumps(result,indent=2,sort_keys=True)); return 0 if not missing else 3
if __name__=='__main__': sys.exit(main())
