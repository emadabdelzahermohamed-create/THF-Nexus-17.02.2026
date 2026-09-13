#!/usr/bin/env python3
"""Read-only real-function source audit for THF games.

Static/source evidence only. Never upgrades device_status beyond PENDING.
It intentionally rejects UI-only shells and placeholder network wiring.
"""
from __future__ import annotations
import argparse, hashlib, json, pathlib, re, sys

TEXT_EXT={'.gd','.tscn','.tres','.godot','.cfg','.ini','.json','.md','.txt','.cs','.java','.kt','.xml','.gradle','.properties','.shader','.gdshader','.js','.ts','.tsx','.html','.css','.py'}
MAX_FILE=2_000_000

def read_texts(root:pathlib.Path):
    out=[]
    for p in root.rglob('*'):
        if not p.is_file() or p.stat().st_size>MAX_FILE: continue
        if p.suffix.lower() not in TEXT_EXT and p.name not in {'project.godot','export_presets.cfg','package.json'}: continue
        try: out.append((p.relative_to(root).as_posix(),p.read_text(errors='ignore')))
        except OSError: pass
    return out

def m(blob,*patterns): return any(re.search(p,blob,re.I|re.M) for p in patterns)
def c(name,ok,detail,required=True): return {'name':name,'status':'PASS' if ok else ('FAIL' if required else 'INFO'),'required':required,'detail':detail}

def audit(root:pathlib.Path,kind:str):
    projects=list(root.rglob('project.godot'))
    project_root=projects[0].parent if len(projects)==1 else root
    items=read_texts(project_root); blob='\n'.join(f'### {n}\n{t}' for n,t in items)
    pg=(projects[0].read_text(errors='ignore') if len(projects)==1 else '')
    checks=[]
    engine='godot' if len(projects)==1 else ('web' if (project_root/'package.json').exists() or list(project_root.rglob('index.html')) else 'unknown')
    checks.append(c('source_tree_nonempty',len(items)>0,f'text_files={len(items)}'))
    checks.append(c('no_ui_only_shell',m(blob,r'_physics_process\(',r'_process\(',r'requestAnimationFrame\(',r'update\(',r'game[_ ]?loop',r'MotionEvent',r'InputEvent') and m(blob,r'player|avatar|character|score|level|quest|exercise|lesson'), 'game loop/input plus game-state markers'))
    checks.append(c('real_input_wiring',m(blob,r'InputEventScreenTouch',r'InputEventScreenDrag',r'TouchScreenButton',r'virtual[_ -]?joystick',r'MotionEvent',r'onTouch',r'touchstart',r'pointerdown'),'touch/input handler marker'))
    checks.append(c('real_state_progression',m(blob,r'score|points|xp\b|level|progress|quest|round|match|objective|streak|reps|exercise|lesson'),'progress/game-state marker'))
    checks.append(c('player_or_avatar_load',m(blob,r'avatar|player[_ -]?scene|CharacterBody3D|preload\([^\n]*(player|avatar)|load\([^\n]*(player|avatar)|character'),'player/avatar marker'))
    checks.append(c('locomotion_or_gameplay_action',m(blob,r'move_and_slide|move_and_collide|velocity|walk_speed|run_speed|jump|attack|shoot|reload|interact|exercise|rep_count|answer|submit'),'movement/gameplay action marker'))
    checks.append(c('camera_or_view_control',m(blob,r'Camera3D|camera[_ -]?(controller|follow)|look_at|mouse_sensitivity|drag.*camera|pinch|viewport'),'camera/view marker',kind not in {'learn','fitness','spark','rush'}))
    checks.append(c('offline_mode_truthful',m(blob,r'offline|local[_ -]?(mode|training|explore|practice)|training[_ -]?mode|practice[_ -]?mode|cached[_ -]?local'),'local/offline marker',False))
    checks.append(c('backend_authority_marker',m(blob,r'authoritative|server[_ -]?author|validate.*server|https://|wss://|WebSocket|RPC'),'server/network authority marker',False))
    checks.append(c('no_placeholder_endpoint',not m(blob,r'https?://(example\.com|localhost|127\.0\.0\.1|0\.0\.0\.0)(?::\d+)?',r'REPLACE[_ -]?ME',r'YOUR[_ -]?(API|URL|HOST)',r'placeholder[_ -]?(url|endpoint)'),'no obvious placeholder endpoint'))
    checks.append(c('anti_cheat_or_validation',m(blob,r'anti[_ -]?cheat|server.*validate|validate.*(hit|move|position|score|rep|answer)|proof[_ -]?of[_ -]?human|integrity'),'anti-cheat/validation marker',False))
    checks.append(c('avatar_animation_pipeline',m(blob,r'MakeHuman|MPFB|Universal Animation Library|\bUAL\b|AnimationTree|Skeleton3D|humanoid|avatar[_ -]?(rig|skeleton|animation)'),'avatar/animation integration marker',False))
    checks.append(c('ik_marker',m(blob,r'SkeletonIK3D|TwoBoneIK3D|IK\b|inverse[_ -]?kinematic'),'IK marker',False))
    checks.append(c('world_npc_marker',m(blob,r'NavigationAgent3D|NPC\b|navmesh|world[_ -]?(manager|system|state)|quest'),'NPC/world marker',False))
    checks.append(c('render_pipeline_marker',m(blob,r'WorldEnvironment|weather|day[_ -]?night|PBR|occlusion|\bLOD\b|lightmap'),'environment/performance rendering marker',False))
    checks.append(c('audio_vfx_marker',m(blob,r'AudioStreamPlayer|GPUParticles3D|CPUParticles3D|VFX|particle'),'audio/VFX marker',False))
    checks.append(c('performance_controls',m(blob,r'LOD|occlusion|visibility_range|quality[_ -]?preset|fps|frame[_ -]?budget|object[_ -]?pool|pooling|data[_ -]?saver'),'performance-control marker',False))
    checks.append(c('localization_marker',m(blob,r'TranslationServer|locale|localization|i18n|rtl|layout_direction'),'localization/RTL marker',False))
    checks.append(c('accessibility_marker',m(blob,r'reduce[_ -]?motion|high[_ -]?contrast|accessibility|data[_ -]?saver|safe[_ -]?area'),'accessibility marker',False))
    if engine=='godot':
        checks += [
          c('unique_godot_project',len(projects)==1,f'project_count={len(projects)}'),
          c('export_preset',(project_root/'export_presets.cfg').is_file(),'export_presets.cfg present'),
        ]
        if kind in {'terra','rift'}:
            checks += [
              c('sensor_landscape',m(pg,r'(display/window/)?handheld/orientation\s*=\s*3\b',r'orientation.*sensor.*landscape'),'sensor-landscape'),
              c('expandable_aspect',m(pg,r'(display/window/)?stretch/aspect\s*=\s*"?expand"?',r'stretch/aspect.*expand'),'expand stretch aspect'),
              c('no_desktop_window_override',not m(pg,r'window_(width|height)_override\s*=\s*[1-9]',r'size/window_(width|height)_override\s*=\s*[1-9]'),'no non-zero desktop override'),
            ]
    if kind=='rift': checks.append(c('combat_wiring',m(blob,r'attack|weapon|damage|hitbox|hurtbox|reload|ammo'),'combat marker'))
    if kind=='terra': checks.append(c('world_interaction',m(blob,r'interact|quest|inventory|NPC\b|world[_ -]?state|pickup'),'world interaction marker'))
    if kind in {'learn','spark'}: checks.append(c('learning_loop',m(blob,r'question|answer|lesson|quiz|correct|incorrect|mastery|learning'),'learning gameplay loop'))
    if kind in {'fitness','rush'}: checks.append(c('fitness_loop',m(blob,r'exercise|rep_count|repetition|workout|timer|heart|motion|sensor|calorie'),'fitness gameplay loop'))
    failed=[x for x in checks if x['required'] and x['status']=='FAIL']
    return {
      'schema':'thf-game-real-function-audit-v2','kind':kind,'engine':engine,
      'project_root':str(project_root),'source_contract_status':'PASS' if not failed else 'FAIL',
      'device_status':'PENDING','final_status':'NOT_FINAL','checks':checks,
      'summary':{'required_failures':[x['name'] for x in failed],'pass_count':sum(x['status']=='PASS' for x in checks),'info_count':sum(x['status']=='INFO' for x in checks)}
    }

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root'); ap.add_argument('--kind',choices=['terra','rift','learn','fitness','spark','rush','generic'],required=True); ap.add_argument('--json-out')
    a=ap.parse_args(); result=audit(pathlib.Path(a.root).resolve(),a.kind); data=json.dumps(result,indent=2,sort_keys=True); print(data)
    if a.json_out: pathlib.Path(a.json_out).write_text(data+'\n')
    return 1 if result['source_contract_status']=='FAIL' else 0
if __name__=='__main__': sys.exit(main())
