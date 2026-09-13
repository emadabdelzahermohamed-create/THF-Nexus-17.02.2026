#!/usr/bin/env python3
"""Fail-closed static runtime-binding audit for Terra/Rift Godot sources.

This is stronger than asset/signal inventory: it looks for executable/player-scene
co-occurrence that binds locomotion, camera, animation/avatar and game interaction.
It remains source evidence only; device_status is always PENDING.
"""
from __future__ import annotations
import argparse,json,pathlib,re,sys
MAX=3_000_000

def texts(root,exts):
 out=[]
 for p in root.rglob('*'):
  if p.is_file() and p.suffix.lower() in exts and p.stat().st_size<=MAX:
   try: out.append((p.relative_to(root).as_posix(),p.read_text(errors='ignore')))
   except OSError: pass
 return out

def has(t,*ps):return all(re.search(p,t,re.I|re.M) for p in ps)
def any_file(items,*ps):return [n for n,t in items if has(t,*ps)]
def check(name,files,detail,required=True):return {'name':name,'status':'PASS' if files else ('FAIL' if required else 'INFO'),'required':required,'files':files[:20],'detail':detail}

def audit(root,kind):
 scenes=texts(root,{'.tscn','.tres'}); scripts=texts(root,{'.gd','.cs'}); configs=texts(root,{'.godot','.cfg','.ini'}); alltext=scenes+scripts+configs
 checks=[]
 checks.append(check('player_scene_runtime',any_file(scenes,r'CharacterBody3D|KinematicBody3D',r'Camera3D|SpringArm3D'), 'player body and camera co-bound in scene'))
 checks.append(check('locomotion_runtime',any_file(scripts,r'_physics_process|_process',r'move_and_slide|move_and_collide|velocity',r'Input\.|InputEvent'), 'frame/physics locomotion uses real input'))
 checks.append(check('camera_runtime',any_file(scripts,r'camera|Camera3D|SpringArm3D',r'look|rotate|yaw|pitch|drag'), 'camera has runtime look/follow control'))
 checks.append(check('avatar_scene_binding',any_file(scenes,r'avatar|player|character|humanoid',r'Skeleton3D|\.glb|\.gltf|\.fbx|MeshInstance3D'), 'player/avatar scene references rig or mesh'))
 anim_scene=any_file(scenes,r'AnimationTree|AnimationPlayer|AnimationNodeStateMachine')
 anim_script=any_file(scripts,r'AnimationTree|AnimationPlayer|playback|travel\(',r'walk|run|idle|jump|attack|locomotion')
 checks.append(check('animation_runtime_binding',sorted(set(anim_scene+anim_script)), 'animation tree/player exists and runtime code drives gameplay states'))
 checks.append(check('ik_runtime_binding',any_file(alltext,r'SkeletonIK3D|TwoBoneIK3D|LookAtModifier3D|IK|foot[_ -]?plant|inverse[_ -]?kinematic'), 'IK/foot/look runtime marker',False))
 checks.append(check('touch_runtime_binding',any_file(scripts,r'InputEventScreenTouch|InputEventScreenDrag|TouchScreenButton|virtual[_ -]?(joystick|stick)|touch'), 'touch reaches gameplay script'))
 checks.append(check('authority_runtime_binding',any_file(scripts,r'https://|wss://|WebSocket|HTTPClient|HTTPRequest|RPC|server[_ -]?author'), 'network/server authority runtime marker',False))
 checks.append(check('offline_truth_binding',any_file(alltext,r'offline|local[_ -]?(training|explore|practice)|practice[_ -]?mode|training[_ -]?mode'), 'explicit genuinely-local mode marker',False))
 if kind=='rift':checks.append(check('combat_runtime_binding',any_file(scripts,r'attack|fire|shoot|reload',r'damage|hit|ammo|weapon|projectile'), 'combat action and outcome/ammo co-bound'))
 if kind=='terra':checks.append(check('world_runtime_binding',any_file(scripts,r'interact|quest|pickup|inventory|npc',r'world|state|navigation|area|body'), 'world interaction and state/navigation co-bound'))
 failed=[x for x in checks if x['required'] and x['status']=='FAIL']
 return {'schema':'thf-game-runtime-binding-audit-v1','kind':kind,'source_contract_status':'PASS' if not failed else 'BLOCKED','required_failures':[x['name'] for x in failed],'checks':checks,'scene_files_scanned':len(scenes),'script_files_scanned':len(scripts),'device_status':'PENDING','final_status':'NOT_FINAL'}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('root');ap.add_argument('--kind',choices=['terra','rift'],required=True);ap.add_argument('--json-out',required=True);a=ap.parse_args();x=audit(pathlib.Path(a.root).resolve(),a.kind);pathlib.Path(a.json_out).write_text(json.dumps(x,indent=2,sort_keys=True)+'\n');print(json.dumps(x,indent=2,sort_keys=True));return 0 if x['source_contract_status']=='PASS' else 3
if __name__=='__main__':sys.exit(main())
