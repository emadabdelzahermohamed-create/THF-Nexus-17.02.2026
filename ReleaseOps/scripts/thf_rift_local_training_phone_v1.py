#!/usr/bin/env python3
"""Disposable Rift RC37 phone/local-training overlay.

Applies only to a clean-extracted candidate tree. The canonical archive is never modified.
Local training is deliberately separated from the online `session` dictionary and `_act()`
path so ranked/social/economy/world authority stays on the backend.
"""
from __future__ import annotations
import argparse, hashlib, json, pathlib, re

EXPECTED_ARENA_SHA = "884243a61d9bb39b276e77ba14579e290c25cec184d24a948e6cd4f45935bdae"


def sha256(p: pathlib.Path) -> str:
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()


def unique(root: pathlib.Path, suffix: str) -> pathlib.Path:
    xs=[p for p in root.rglob('*') if p.is_file() and p.as_posix().endswith(suffix)]
    if len(xs)!=1: raise SystemExit(f'expected one {suffix}, found {len(xs)}')
    return xs[0]


def function_span(lines: list[str], name: str) -> tuple[int,int]:
    rx=re.compile(r'^func\s+'+re.escape(name)+r'\s*\(')
    start=next((i for i,l in enumerate(lines) if rx.match(l)),None)
    if start is None: raise SystemExit(f'missing func {name}')
    end=len(lines)
    for i in range(start+1,len(lines)):
        if re.match(r'^func\s+[A-Za-z0-9_]+\s*\(',lines[i]): end=i; break
    return start,end


def replace_func(lines: list[str], name: str, body: str) -> list[str]:
    a,b=function_span(lines,name)
    return lines[:a]+body.strip('\n').splitlines()+['']+lines[b:]


def patch_arena(p: pathlib.Path) -> dict:
    before=sha256(p)
    if before!=EXPECTED_ARENA_SHA: raise SystemExit(f'ArenaMain SHA drift: {before}')
    s=p.read_text(encoding='utf-8')
    state_needle='var session: Dictionary = {}\n'
    if state_needle not in s: raise SystemExit('session state marker missing')
    state='''var session: Dictionary = {}\n# Phone V1 genuine local training state. This is intentionally NOT an online session.\nvar local_training_mode := false\nvar local_training_player: Dictionary = {"hp": 100, "stance": "stand", "weapon": {"ammo": 30, "magazine": 30}}\nvar local_training_ammo := 30\nvar local_training_bot_hp := 100\nvar local_training_hits := 0\nvar local_training_kills := 0\nvar local_training_target: Node3D\n'''
    s=s.replace(state_needle,state,1)
    lines=s.splitlines()

    lines=replace_func(lines,'_start_training',r'''
func _start_training() -> void:
    # Genuine local mode: no /api/session, no WebSocket, no online/ranked/economy mutation.
    local_training_mode = true
    socket = WebSocketPeer.new()
    socket_connected = false
    session.clear()
    local_training_player = {"hp": 100, "stance": "stand", "weapon": {"ammo": 30, "magazine": 30}}
    local_training_ammo = 30
    local_training_bot_hp = 100
    local_training_hits = 0
    local_training_kills = 0
    lobby_panel.visible = false
    _spawn_local_avatar()
    _spawn_local_training_target()
    target_position = local_actor.position if is_instance_valid(local_actor) else Vector3.ZERO
    safe_position = target_position
    status.text = "LOCAL TRAINING · OFFLINE · NO ONLINE STATE"
    hp_label.text = "HP 100 · LOCAL"
    ammo_label.text = "AMMO 30 · TARGET 100"
''')

    # Keep the existing online movement body byte-for-byte after a local-only branch.
    a,b=function_span(lines,'_movement_tick')
    old=lines[a:b]
    if len(old)<3 or 'if session.is_empty():' not in '\n'.join(old[:5]):
        raise SystemExit('movement guard drift')
    local_branch=r'''
func _movement_tick() -> void:
    if local_training_mode:
        if tactical_action.locomotion_locked():
            return
        var lx := 0.0
        var ly := 0.0
        if Input.is_physical_key_pressed(KEY_A) or Input.is_key_pressed(KEY_LEFT):
            lx -= 1.0
        if Input.is_physical_key_pressed(KEY_D) or Input.is_key_pressed(KEY_RIGHT):
            lx += 1.0
        if Input.is_physical_key_pressed(KEY_W) or Input.is_key_pressed(KEY_UP):
            ly -= 1.0
        if Input.is_physical_key_pressed(KEY_S) or Input.is_key_pressed(KEY_DOWN):
            ly += 1.0
        var local_move := Vector2(lx, ly)
        if touch_move.length() >= 0.16:
            local_move = touch_move
        if local_move.length() < 0.16:
            sprinting_native = false
            return
        var local_now := Time.get_ticks_msec()
        var local_period_ms := performance_budget.movement_period_ms(player_settings.data_saver)
        if local_now - last_move_ms < local_period_ms:
            return
        last_move_ms = local_now
        local_move = local_move.normalized()
        sprinting_native = Input.is_key_pressed(KEY_SHIFT)
        var step_distance := 0.34 if sprinting_native else 0.22
        target_position.x = clampf(target_position.x + local_move.x * step_distance, -38.0, 38.0)
        target_position.z = clampf(target_position.z + local_move.y * step_distance, -38.0, 38.0)
        return
'''.strip('\n').splitlines()
    lines=lines[:a]+local_branch+old[1:]+lines[b:]

    # Exact RC37 _process has no session guard. Only swap its presentation source
    # to local state while in local training; the existing avatar/UAL/IK/camera loop continues.
    pa,pb=function_span(lines,'_process')
    proc='\n'.join(lines[pa:pb])
    marker='        var player: Dictionary = session.get("player", {})'
    if marker not in proc: raise SystemExit('_process player marker drift')
    proc=proc.replace(marker,'        var player: Dictionary = local_training_player if local_training_mode else session.get("player", {})',1)
    lines=lines[:pa]+proc.splitlines()+lines[pb:]

    # Camera cover state also reads the online session; local mode must use only local state.
    ua,ub=function_span(lines,'_update_camera')
    cam='\n'.join(lines[ua:ub])
    camera_marker='    var player_state: Dictionary = session.get("player", {})'
    if camera_marker not in cam: raise SystemExit('_update_camera player marker drift')
    cam=cam.replace(camera_marker,'    var player_state: Dictionary = local_training_player if local_training_mode else session.get("player", {})',1)
    lines=lines[:ua]+cam.splitlines()+lines[ub:]

    # Route only local-training controls to local state; online controls remain request-only/server-authoritative.
    ca,cb=function_span(lines,'_combat_action')
    combat='\n'.join(lines[ca:cb])
    sig='func _combat_action(kind: String) -> void:\n'
    if not combat.startswith(sig): raise SystemExit('combat signature drift')
    combat=combat.replace(sig,sig+'    if local_training_mode:\n        _local_training_combat_action(kind)\n        return\n',1)
    lines=lines[:ca]+combat.splitlines()+lines[cb:]

    aa,ab=function_span(lines,'_act')
    helpers=r'''
func _spawn_local_training_target() -> void:
    if is_instance_valid(local_training_target):
        return
    local_training_target = Node3D.new()
    local_training_target.name = "LocalTrainingTarget"
    add_child(local_training_target)
    var mesh := MeshInstance3D.new()
    var capsule := CapsuleMesh.new()
    capsule.radius = 0.55
    capsule.height = 1.9
    mesh.mesh = capsule
    mesh.position.y = 0.95
    local_training_target.add_child(mesh)
    local_training_target.position = Vector3(0.0, 0.0, -8.0)

func _local_training_combat_action(kind: String) -> void:
    if not local_training_mode:
        return
    if kind == "fire":
        if local_training_ammo <= 0:
            status.text = "LOCAL TRAINING · RELOAD"
            return
        local_training_ammo -= 1
        local_training_player["weapon"] = {"ammo": local_training_ammo, "magazine": 30}
        last_action = "fire"
        var hit := false
        if is_instance_valid(camera) and is_instance_valid(local_training_target):
            var to_target := local_training_target.global_position + Vector3.UP - camera.global_position
            if to_target.length() <= 30.0 and to_target.length_squared() > 0.001:
                var aim_dir := -camera.global_transform.basis.z.normalized()
                hit = aim_dir.dot(to_target.normalized()) >= 0.88
        if hit:
            local_training_hits += 1
            local_training_bot_hp = maxi(0, local_training_bot_hp - 25)
            if local_training_bot_hp <= 0:
                local_training_kills += 1
                local_training_bot_hp = 100
                if is_instance_valid(local_training_target):
                    var lane := float((local_training_kills % 5) - 2) * 2.5
                    local_training_target.position = Vector3(lane, 0.0, -8.0 - float(local_training_kills % 3) * 2.0)
        ammo_label.text = "AMMO %d · TARGET %d" % [local_training_ammo, local_training_bot_hp]
        status.text = "LOCAL FIRE · HIT %d · KILLS %d" % [local_training_hits, local_training_kills]
    elif kind == "reload":
        local_training_ammo = 30
        local_training_player["weapon"] = {"ammo": local_training_ammo, "magazine": 30}
        last_action = "reload"
        ammo_label.text = "AMMO 30 · TARGET %d" % local_training_bot_hp
        status.text = "LOCAL TRAINING · RELOADED"
    elif kind == "aim":
        aim_enabled = not aim_enabled
        status.text = "LOCAL AIM · " + ("ON" if aim_enabled else "OFF")
    elif kind == "crouch":
        local_training_player["stance"] = "stand" if str(local_training_player.get("stance", "stand")) == "crouch" else "crouch"
        status.text = "LOCAL STANCE · " + str(local_training_player["stance"]).to_upper()
    elif kind == "settings":
        settings_panel.visible = not settings_panel.visible
    else:
        status.text = "LOCAL TRAINING · ACTION LOCAL-ONLY/UNRANKED"
'''.strip('\n').splitlines()+['']
    lines=lines[:aa]+helpers+lines[aa:]

    out='\n'.join(lines)+'\n'
    out=out.replace('button.custom_minimum_size = Vector2(66.0, 54.0)','button.custom_minimum_size = Vector2(66.0, 62.0)',1)
    out=out.replace('func _add_combat_button(parent: Control, label: String, action_name: String, minimum_size := Vector2(76.0, 58.0)) -> void:',
                    'func _add_combat_button(parent: Control, label: String, action_name: String, minimum_size := Vector2(76.0, 62.0)) -> void:',1)
    out=out.replace('    button.custom_minimum_size = minimum_size\n    button.pressed.connect(_combat_action.bind(action_name))',
                    '    button.custom_minimum_size = Vector2(maxf(minimum_size.x, 62.0), maxf(minimum_size.y, 62.0))\n    button.pressed.connect(_combat_action.bind(action_name))',1)
    p.write_text(out,encoding='utf-8')
    return {'before_sha256':before,'after_sha256':sha256(p)}


def patch_package(root: pathlib.Path) -> dict:
    p=unique(root,'export_presets.cfg')
    before=sha256(p); s=p.read_text(encoding='utf-8')
    old='package/unique_name="com.topherofit.thf.rift"'
    new='package/unique_name="com.topherofit.thf.rift.phoneqa"'
    if old in s: s=s.replace(old,new,1)
    elif new not in s: raise SystemExit('Rift package marker missing')
    p.write_text(s,encoding='utf-8')
    return {'before_sha256':before,'after_sha256':sha256(p),'package':'com.topherofit.thf.rift.phoneqa'}


def main() -> int:
    ap=argparse.ArgumentParser(); ap.add_argument('root'); ap.add_argument('--json-out',required=True); a=ap.parse_args()
    root=pathlib.Path(a.root).resolve()
    arena=unique(root,'native/arena/ArenaMain.gd')
    result={'schema':'thf-rift-local-training-phone-v1','candidate_only':True,'canonical_archive_mutated':False,
            'arena':patch_arena(arena),'package':patch_package(root),'final_status':'NOT_FINAL','physical_device_status':'PENDING'}
    text=arena.read_text(encoding='utf-8')
    required=['local_training_mode = true','socket = WebSocketPeer.new()','session.clear()','_spawn_local_training_target()','func _local_training_combat_action','local_training_bot_hp = maxi(0, local_training_bot_hp - 25)','target_position.x = clampf','target_position.z = clampf','local_training_player if local_training_mode else session.get("player", {})']
    for x in required:
        if x not in text: raise SystemExit(f'missing local-training marker: {x}')
    lines=text.splitlines(); a0,b0=function_span(lines,'_start_training'); start='\n'.join(lines[a0:b0])
    for forbidden in ('api.request_json','_connect_realtime','socket.send','_sync_session'):
        if forbidden in start: raise SystemExit(f'local start leaked online path: {forbidden}')
    la,lb=function_span(lines,'_local_training_combat_action'); local_combat='\n'.join(lines[la:lb])
    for forbidden in ('api.request_json','socket.send','_act('):
        if forbidden in local_combat: raise SystemExit(f'local combat leaked online path: {forbidden}')
    aa,bb=function_span(lines,'_act'); act='\n'.join(lines[aa:bb])
    for marker in ('socket.send_text','api.request_json','/api/session/'):
        if marker not in act: raise SystemExit(f'online authority marker lost: {marker}')
    pathlib.Path(a.json_out).write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(result,indent=2,sort_keys=True))
    return 0

if __name__=='__main__': raise SystemExit(main())
