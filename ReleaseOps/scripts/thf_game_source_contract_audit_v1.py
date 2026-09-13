#!/usr/bin/env python3
"""Static source-contract audit for THF Godot game candidates.

This is deliberately NOT a runtime/device acceptance test. It proves only source
contracts that can be established from a clean extracted tree. Device status is
always PENDING and must be satisfied separately for the exact APK SHA.
"""
from __future__ import annotations
import argparse, json, pathlib, re, sys

TEXT_EXT={'.gd','.tscn','.tres','.godot','.cfg','.ini','.json','.md','.txt','.cs','.java','.kt','.xml','.gradle','.properties','.shader','.gdshader'}
MAX_FILE=2_000_000

def texts(root: pathlib.Path):
    out=[]
    for p in root.rglob('*'):
        if not p.is_file() or p.stat().st_size>MAX_FILE: continue
        if p.suffix.lower() not in TEXT_EXT and p.name not in {'project.godot','export_presets.cfg'}: continue
        try: out.append((p.relative_to(root).as_posix(),p.read_text(errors='ignore')))
        except OSError: pass
    return out

def has(blob:str,*patterns:str)->bool:
    return any(re.search(x,blob,re.I|re.M) for x in patterns)

def check(name,ok,detail,required=True):
    return {'name':name,'status':'PASS' if ok else ('FAIL' if required else 'INFO'),'required':required,'detail':detail}

def audit(root:pathlib.Path, game:str):
    projects=list(root.rglob('project.godot'))
    checks=[check('unique_project_root',len(projects)==1,f'project.godot count={len(projects)}')]
    if len(projects)!=1:
        return checks, None
    pr=projects[0].parent
    items=texts(pr); blob='\n'.join(f'### {n}\n{t}' for n,t in items)
    pg=projects[0].read_text(errors='ignore')
    exp=pr/'export_presets.cfg'
    checks += [
      check('export_preset',exp.is_file(),'export_presets.cfg present'),
      check('sensor_landscape',has(pg,r'display/window/handheld/orientation\s*=\s*3\b',r'handheld/orientation.*sensor.*landscape',r'orientation.*sensor.*landscape'),'sensor-landscape mobile orientation contract'),
      check('expandable_aspect',has(pg,r'display/window/stretch/aspect\s*=\s*"?expand"?',r'stretch/aspect.*expand'),'expandable aspect contract'),
      check('no_desktop_window_override',not has(pg,r'display/window/size/window_width_override\s*=\s*[1-9]',r'display/window/size/window_height_override\s*=\s*[1-9]'),'no non-zero desktop window override'),
      check('touch_input_contract',has(blob,r'InputEventScreenTouch',r'InputEventScreenDrag',r'TouchScreenButton',r'virtual[_ -]?joystick',r'touch[_ -]?(hud|control|input|stick)'),'touch input/HUD source marker'),
      check('player_avatar_load',has(blob,r'avatar',r'player(_|\s)?scene',r'characterbody3d',r'load\([^\n]*(player|avatar)',r'preload\([^\n]*(player|avatar)'),'player/avatar load marker'),
      check('locomotion',has(blob,r'velocity',r'move_and_slide',r'move_and_collide',r'locomotion',r'walk_speed',r'run_speed'),'locomotion source marker'),
      check('camera_gameplay',has(blob,r'Camera3D',r'camera(_|\s)?controller',r'look_at',r'mouse_sensitivity',r'camera.*follow'),'gameplay camera marker'),
      check('offline_local_mode',has(blob,r'offline',r'local[_ -]?(mode|training|explore|practice)',r'training[_ -]?mode',r'explore[_ -]?mode'),'genuine local/offline-mode marker',False),
      check('backend_authority',has(blob,r'authoritative',r'server[_ -]?author',r'validate.*server',r'wss://',r'https://',r'rpc'),'backend authority/network marker',False),
      check('no_placeholder_endpoint',not has(blob,r'https?://(example\.com|localhost|127\.0\.0\.1|0\.0\.0\.0)(?::\d+)?',r'REPLACE[_ -]?ME',r'YOUR[_ -]?(API|URL|HOST)',r'placeholder[_ -]?(url|endpoint)'),'no obvious placeholder endpoint'),
      check('avatar_pipeline_refs',has(blob,r'MakeHuman',r'MPFB',r'Universal Animation Library',r'UAL\b',r'avatar[_ -]?(rig|skeleton|animation)',r'humanoid'),'avatar/animation pipeline marker',False),
      check('ik_animation',has(blob,r'SkeletonIK3D',r'TwoBoneIK3D',r'AnimationTree',r'blend_tree',r'IK\b'),'IK/animation-tree marker',False),
      check('world_npc_system',has(blob,r'NPC',r'NavigationAgent3D',r'world[_ -]?(manager|system|state)',r'navmesh'),'NPC/world-system marker',False),
      check('render_environment',has(blob,r'WorldEnvironment',r'Environment',r'weather',r'day[_ -]?night',r'PBR',r'occlusion',r'LOD'),'environment/weather/PBR/LOD marker',False),
      check('audio_vfx',has(blob,r'AudioStreamPlayer',r'GPUParticles3D',r'CPUParticles3D',r'VFX',r'particle'),'audio/VFX marker',False),
      check('localization',has(blob,r'TranslationServer',r'locale',r'localization',r'\.translation',r'i18n'),'localization contract marker',False),
      check('accessibility',has(blob,r'reduce[_ -]?motion',r'high[_ -]?contrast',r'accessibility',r'data[_ -]?saver'),'accessibility/data-saver marker',False),
    ]
    if game=='rift':
      checks += [
        check('combat_wiring',has(blob,r'attack',r'weapon',r'damage',r'hitbox',r'hurtbox',r'reload'),'combat interaction marker'),
        check('anti_cheat',has(blob,r'anti[_ -]?cheat',r'validate.*(hit|shot|move|position)',r'proof[_ -]?of[_ -]?human'),'anti-cheat/validation marker',False),
      ]
    if game=='terra':
      checks += [
        check('world_interaction',has(blob,r'interact',r'quest',r'inventory',r'NPC',r'world[_ -]?state'),'world/explore interaction marker'),
      ]
    return checks, pr

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root'); ap.add_argument('--game',choices=['terra','rift','generic'],required=True); ap.add_argument('--json-out')
    a=ap.parse_args(); root=pathlib.Path(a.root).resolve(); checks,pr=audit(root,a.game)
    failed=[c for c in checks if c['required'] and c['status']=='FAIL']
    result={'schema':'thf-game-source-contract-v1','game':a.game,'project_root':str(pr) if pr else None,'source_contract_status':'PASS' if not failed else 'FAIL','device_status':'PENDING','checks':checks}
    data=json.dumps(result,indent=2,sort_keys=True)
    print(data)
    if a.json_out: pathlib.Path(a.json_out).write_text(data+'\n')
    return 1 if failed else 0
if __name__=='__main__': sys.exit(main())
