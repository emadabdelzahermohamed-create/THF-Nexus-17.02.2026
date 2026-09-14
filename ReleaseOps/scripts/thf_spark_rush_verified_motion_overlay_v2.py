#!/usr/bin/env python3
"""Install a genuine local-only practice game into Spark/Rush on a disposable QA tree.

V2 closes an important Rush trust-boundary gap: touch/manual values can never advance
motion repetitions. Rush reps are derived only from trusted device motion sensor events.
The local mode never writes ranked/social/economy/reward/fitness-evidence state and does
not claim server-verifiable health evidence. Any online reward path remains outside this
overlay and must be backend-authoritative.

Canonical source archives are never modified by this helper.
"""
from __future__ import annotations

import argparse
import hashlib
import pathlib
import re
import sys

HEAD = r'''<!doctype html><html lang="en" dir="auto"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover,user-scalable=no"><title>THF Local Practice</title><style>
:root{color-scheme:dark;--bg:#101418;--fg:#fff;--panel:#1d252c;--accent:#8fe3ff}*{box-sizing:border-box}html,body{margin:0;width:100%;height:100%;overflow:hidden;background:var(--bg);color:var(--fg);font-family:system-ui,sans-serif;touch-action:none}#app{position:fixed;inset:0;padding:max(10px,env(safe-area-inset-top)) max(10px,env(safe-area-inset-right)) max(10px,env(safe-area-inset-bottom)) max(10px,env(safe-area-inset-left));display:grid;grid-template-rows:auto 1fr auto;gap:8px}#hud{display:flex;flex-wrap:wrap;gap:8px;align-items:center;background:var(--panel);padding:8px 12px;border-radius:12px}#game{width:100%;height:100%;min-height:0;border:1px solid #52616b;border-radius:14px;background:#15202a;touch-action:none}#note{font-size:12px;text-align:center;opacity:.9}.btn{min-width:52px;min-height:52px;border:1px solid #6d8796;background:#21313c;color:#fff;border-radius:10px;padding:8px 12px;font-weight:700}@media(prefers-reduced-motion:reduce){*{scroll-behavior:auto!important}}@media(prefers-contrast:more){:root{--bg:#000;--fg:#fff;--panel:#000;--accent:#0ff}#game,.btn{border-width:3px}}</style></head><body><main id="app"><div id="hud"><strong id="title">THF Local Practice</strong><span id="status"></span><button class="btn" id="sensor" type="button" hidden>Enable motion</button><button class="btn" id="reset" type="button">Reset</button></div><canvas id="game" width="960" height="540" aria-label="Local practice game"></canvas><div id="note">Local offline practice only — no ranked, social, wallet, economy, rewards, or server fitness-evidence state is written.</div></main><script>'use strict';
const canvas=document.getElementById('game'),ctx=canvas.getContext('2d'),statusEl=document.getElementById('status'),sensorBtn=document.getElementById('sensor');const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;const rtl=(navigator.language||'').toLowerCase().startsWith('ar');const playerState={x:480,y:400,targetX:480,targetY:400,r:24,score:0,round:1,active:true};function loadLocalAvatar(){return{label:'THF',radius:playerState.r}}const avatar=loadLocalAvatar();function pointerPos(e){const r=canvas.getBoundingClientRect();return{x:(e.clientX-r.left)*canvas.width/r.width,y:(e.clientY-r.top)*canvas.height/r.height}}function movePlayerTowardTarget(dt){const dx=playerState.targetX-playerState.x,dy=playerState.targetY-playerState.y,d=Math.hypot(dx,dy);if(d>2){const speed=reduced?900:520,step=Math.min(d,speed*dt);playerState.x+=dx/d*step;playerState.y+=dy/d*step}}canvas.addEventListener('pointerdown',e=>{e.preventDefault();const p=pointerPos(e);playerState.targetX=p.x;playerState.targetY=p.y;onLocalTouch(p)},{passive:false});canvas.addEventListener('pointermove',e=>{if(e.buttons){e.preventDefault();const p=pointerPos(e);playerState.targetX=p.x;playerState.targetY=p.y}},{passive:false});document.getElementById('reset').addEventListener('click',()=>resetLocalGame());let last=performance.now();function gameLoop(now){const dt=Math.min(.05,(now-last)/1000);last=now;movePlayerTowardTarget(dt);updateLocalGame(dt);drawLocalGame();requestAnimationFrame(gameLoop)}requestAnimationFrame(gameLoop);
'''

SPARK = r'''document.getElementById('title').textContent='THF Learn Games';const spark={a:0,b:0,correct:0,choices:[],answered:false};function newLearningRound(){spark.a=1+Math.floor(Math.random()*9);spark.b=1+Math.floor(Math.random()*9);spark.correct=spark.a+spark.b;let wrong=spark.correct+(Math.random()<.5?-1:1)*(1+Math.floor(Math.random()*3));if(wrong<0)wrong+=5;spark.choices=Math.random()<.5?[spark.correct,wrong]:[wrong,spark.correct];spark.answered=false;playerState.targetX=480;playerState.targetY=400;statusEl.textContent=(rtl?'حل: ':'Solve: ')+spark.a+' + '+spark.b}function onLocalTouch(p){if(p.y>245||spark.answered)return;const i=p.x<480?0:1;spark.answered=true;if(spark.choices[i]===spark.correct){playerState.score++;statusEl.textContent=rtl?'صحيح — تقدم محلي فقط':'Correct — local progress only'}else statusEl.textContent=(rtl?'الإجابة الصحيحة: ':'Correct answer: ')+spark.correct;setTimeout(newLearningRound,reduced?50:650)}function updateLocalGame(dt){}function drawLocalGame(){ctx.clearRect(0,0,960,540);ctx.fillStyle='#243646';ctx.fillRect(24,28,432,190);ctx.fillRect(504,28,432,190);ctx.fillStyle='#fff';ctx.font='bold 72px system-ui';ctx.textAlign='center';ctx.fillText(String(spark.choices[0]??''),240,150);ctx.fillText(String(spark.choices[1]??''),720,150);drawAvatar();ctx.font='22px system-ui';ctx.fillText((rtl?'النقاط المحلية: ':'Local score: ')+playerState.score,480,505)}function resetLocalGame(){playerState.score=0;newLearningRound()}newLearningRound();'''

RUSH = r'''document.getElementById('title').textContent='THF Motion Games';const rush={reps:0,sensorEvents:0,trustedEvents:0,rejectedEvents:0,lastRepAt:0,phase:'LOW',lastMagnitude:0,permission:'pending'};const MOTION_HIGH=13.5,MOTION_LOW=10.7,REP_COOLDOWN_MS=450;
function setMotionStatus(extra=''){statusEl.textContent=(rtl?'تدريب حركة محلي — تكرارات: ':'Local motion drill — reps: ')+rush.reps+' · '+(rtl?'عينات موثوقة: ':'trusted samples: ')+rush.trustedEvents+(extra?' · '+extra:'')}
function finite3(a){return a&&Number.isFinite(a.x)&&Number.isFinite(a.y)&&Number.isFinite(a.z)}
function onVerifiedMotionEvent(e){rush.sensorEvents++;if(!e.isTrusted){rush.rejectedEvents++;return}const a=finite3(e.accelerationIncludingGravity)?e.accelerationIncludingGravity:(finite3(e.acceleration)?e.acceleration:null);if(!a){rush.rejectedEvents++;return}rush.trustedEvents++;const mag=Math.hypot(a.x,a.y,a.z);rush.lastMagnitude=mag;const now=performance.now();if(rush.phase==='LOW'&&mag>=MOTION_HIGH&&now-rush.lastRepAt>=REP_COOLDOWN_MS){rush.phase='HIGH'}else if(rush.phase==='HIGH'&&mag<=MOTION_LOW){rush.phase='LOW';rush.reps++;playerState.score=rush.reps;rush.lastRepAt=now}setMotionStatus()}
function installMotionListener(){window.addEventListener('devicemotion',onVerifiedMotionEvent,{passive:true});rush.permission='granted';sensorBtn.hidden=true;setMotionStatus(rtl?'الحساس مفعل':'sensor active')}
async function requestMotionPermission(){try{if(typeof DeviceMotionEvent==='undefined'){rush.permission='unavailable';setMotionStatus(rtl?'الحساس غير متاح':'motion sensor unavailable');return}if(typeof DeviceMotionEvent.requestPermission==='function'){const p=await DeviceMotionEvent.requestPermission();if(p!=='granted'){rush.permission='denied';setMotionStatus(rtl?'تم رفض إذن الحركة':'motion permission denied');return}}installMotionListener()}catch(_){rush.permission='error';setMotionStatus(rtl?'تعذر تشغيل الحساس':'motion sensor error')}}
function startMotion(){if(typeof DeviceMotionEvent!=='undefined'&&typeof DeviceMotionEvent.requestPermission==='function'){sensorBtn.hidden=false;sensorBtn.addEventListener('click',requestMotionPermission,{once:true});setMotionStatus(rtl?'فعّل الحساس':'enable sensor')}else requestMotionPermission()}
function onLocalTouch(p){/* Touch may move the local avatar for accessibility/camera practice, but MUST NOT increment reps or fabricate motion evidence. */}
function updateLocalGame(dt){}function drawLocalGame(){ctx.clearRect(0,0,960,540);ctx.fillStyle='#24495a';ctx.fillRect(80,70,800,280);ctx.fillStyle='#fff';ctx.font='bold 34px system-ui';ctx.textAlign='center';ctx.fillText(rtl?'حرّك الهاتف/الجسم لإكمال التكرار':'MOVE TO COMPLETE A REP',480,150);ctx.font='24px system-ui';ctx.fillText((rtl?'التكرارات من الحساس فقط: ':'sensor-only reps: ')+rush.reps,480,215);ctx.fillText((rtl?'مقدار الحركة: ':'motion magnitude: ')+rush.lastMagnitude.toFixed(2),480,260);drawAvatar();ctx.font='18px system-ui';ctx.fillText((rtl?'اللمس لا يحتسب تكرارات':'touch never counts repetitions'),480,505)}function resetLocalGame(){rush.reps=0;rush.sensorEvents=0;rush.trustedEvents=0;rush.rejectedEvents=0;rush.lastRepAt=0;rush.phase='LOW';playerState.score=0;setMotionStatus()}startMotion();'''

TAIL = r'''function drawAvatar(){ctx.fillStyle='#8fe3ff';ctx.beginPath();ctx.arc(playerState.x,playerState.y,avatar.radius,0,Math.PI*2);ctx.fill();ctx.fillStyle='#071018';ctx.font='bold 16px system-ui';ctx.textAlign='center';ctx.fillText(avatar.label,playerState.x,playerState.y+6)}</script></body></html>'''


def sha256(p: pathlib.Path) -> str:
    h = hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def preserve_canonical_package(root: pathlib.Path, kind: str) -> tuple[int, list[str]]:
    canonical = {'spark': 'com.topherofit.thf.spark', 'rush': 'com.topherofit.thf.rush'}[kind]
    changed: list[str] = []
    suffix_pat = re.compile(r'(?m)^[ \t]*(?:applicationIdSuffix|versionNameSuffix)\b[^\n]*$')
    appid_pat = re.compile(r'(?m)^(?P<i>[ \t]*)applicationId\b(?:\s*=)?\s*["\'][^"\']+["\'][^\n]*$')
    for name in ('build.gradle', 'build.gradle.kts'):
        for p in root.rglob(name):
            text = p.read_text(errors='ignore')
            if 'applicationId' not in text:
                continue
            new, n1 = suffix_pat.subn('', text)
            def repl(m: re.Match[str]) -> str:
                return f'{m.group("i")}applicationId "{canonical}"'
            new, n2 = appid_pat.subn(repl, new)
            if n1 or n2:
                p.write_text(new)
                changed.append(p.relative_to(root).as_posix())
    return len(changed), changed


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('root')
    ap.add_argument('--kind', choices=['spark', 'rush'], required=True)
    ap.add_argument('--evidence-out', required=True)
    a = ap.parse_args()
    root = pathlib.Path(a.root).resolve()
    candidates = sorted(root.rglob('android/app/src/main/assets/offline.html'))
    if len(candidates) != 1:
        raise SystemExit(f'expected one Android offline asset, found {len(candidates)}')
    out = candidates[0]
    before = sha256(out)
    payload = HEAD + (SPARK if a.kind == 'spark' else RUSH) + TAIL
    out.write_text(payload)
    after = sha256(out)
    package_files_changed, package_files = preserve_canonical_package(root, a.kind)
    common = [
        'schema=thf-spark-rush-verified-motion-overlay-v2',
        f'kind={a.kind}',
        f'offline_asset={out.relative_to(root).as_posix()}',
        f'offline_sha256_before={before}',
        f'offline_sha256_after={after}',
        f'qa_package_files_changed={package_files_changed}',
        f"qa_package_files={','.join(package_files)}",
        f"canonical_package_id={'com.topherofit.thf.spark' if a.kind == 'spark' else 'com.topherofit.thf.rush'}",
        'canonical_package_identity_required=true',
        'local_mode=true',
        'touch_input=true',
        'player_state=true',
        'game_loop=true',
        f"domain_loop={'learning' if a.kind == 'spark' else 'verified_motion_practice'}",
        'ranked_state_written=false',
        'social_state_written=false',
        'economy_state_written=false',
        'reward_state_written=false',
        'fitness_evidence_written=false',
        'network_required=false',
        'candidate_only=true',
        'canonical_archive_mutated=false',
        'device_status=PENDING',
        'final_status=NOT_FINAL',
    ]
    if a.kind == 'rush':
        common += [
            'verified_motion_required=true',
            'motion_source=DeviceMotionEvent',
            'trusted_event_required=true',
            'finite_sensor_vector_required=true',
            'manual_activity_values_accepted=false',
            'touch_repetition_increment=false',
            'sensor_repetition_state_machine=true',
            'online_motion_reward_authority=BACKEND_REQUIRED_NOT_IMPLEMENTED_HERE',
            'server_verifiable_health_evidence_claimed=false',
        ]
    ev = pathlib.Path(a.evidence_out)
    ev.parent.mkdir(parents=True, exist_ok=True)
    ev.write_text('\n'.join(common) + '\n')
    print(ev.read_text(), end='')
    return 0


if __name__ == '__main__':
    sys.exit(main())
