#!/usr/bin/env python3
"""Install a genuine local-only touch game into Spark/Rush offline.html on a disposable tree.

The local mode never writes ranked/social/economy state and never claims fitness evidence.
Canonical source archives are never modified by this tool.
"""
from __future__ import annotations
import argparse, hashlib, pathlib, sys

COMMON_HEAD = r'''<!doctype html>
<html lang="en" dir="auto"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover,user-scalable=no">
<title>THF Local Practice</title>
<style>
:root{color-scheme:dark;--bg:#101418;--fg:#f7f7f7;--panel:#1d252c;--accent:#8fe3ff;--good:#aaf0b5;--warn:#ffd59a}
*{box-sizing:border-box}html,body{margin:0;width:100%;height:100%;overflow:hidden;background:var(--bg);color:var(--fg);font-family:system-ui,sans-serif;touch-action:none}
#app{position:fixed;inset:0;padding:max(10px,env(safe-area-inset-top)) max(10px,env(safe-area-inset-right)) max(10px,env(safe-area-inset-bottom)) max(10px,env(safe-area-inset-left));display:grid;grid-template-rows:auto 1fr auto;gap:8px}
#hud{display:flex;flex-wrap:wrap;gap:8px;align-items:center;background:var(--panel);padding:8px 12px;border-radius:12px}#hud strong{color:var(--accent)}
#game{width:100%;height:100%;min-height:0;border:1px solid #52616b;border-radius:14px;background:#15202a;touch-action:none}
#note{font-size:12px;opacity:.88;text-align:center}.btn{border:1px solid #6d8796;background:#21313c;color:var(--fg);border-radius:10px;padding:8px 12px;font-weight:700}
@media (prefers-reduced-motion:reduce){*{scroll-behavior:auto!important}}
@media (prefers-contrast:more){:root{--bg:#000;--fg:#fff;--panel:#000;--accent:#0ff;--good:#0f0;--warn:#ff0}#game,.btn{border-width:3px}}
</style></head><body><main id="app">
<div id="hud"><strong id="title">THF Local Practice</strong><span id="status"></span><button class="btn" id="reset" type="button">Reset</button></div>
<canvas id="game" width="960" height="540" aria-label="Local touch practice game"></canvas>
<div id="note">Local offline practice only — no ranked, social, wallet, economy, rewards, or fitness-evidence state is written.</div>
</main><script>
'use strict';
const canvas=document.getElementById('game'),ctx=canvas.getContext('2d'),statusEl=document.getElementById('status');
const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
const rtl=(document.documentElement.dir==='rtl')||(navigator.language||'').toLowerCase().startsWith('ar');
const playerState={x:480,y:400,targetX:480,targetY:400,r:24,score:0,round:1,active:true};
function loadLocalAvatar(){ return {label:'THF',radius:playerState.r}; }
const avatar=loadLocalAvatar();
function pointerPos(e){const r=canvas.getBoundingClientRect();return{x:(e.clientX-r.left)*canvas.width/r.width,y:(e.clientY-r.top)*canvas.height/r.height};}
function movePlayerTowardTarget(dt){const dx=playerState.targetX-playerState.x,dy=playerState.targetY-playerState.y,d=Math.hypot(dx,dy);if(d>2){const speed=reduced?900:520,step=Math.min(d,speed*dt);playerState.x += dx/d*step;playerState.y += dy/d*step;}}
canvas.addEventListener('pointerdown',e=>{e.preventDefault();const p=pointerPos(e);playerState.targetX=p.x;playerState.targetY=p.y;onLocalAction(p);},{passive:false});
canvas.addEventListener('pointermove',e=>{if(e.buttons){e.preventDefault();const p=pointerPos(e);playerState.targetX=p.x;playerState.targetY=p.y;}},{passive:false});
document.getElementById('reset').addEventListener('click',()=>resetLocalGame());
let last=performance.now();function gameLoop(now){const dt=Math.min(.05,(now-last)/1000);last=now;movePlayerTowardTarget(dt);updateLocalGame(dt);drawLocalGame();requestAnimationFrame(gameLoop);}requestAnimationFrame(gameLoop);
'''

SPARK = r'''
const spark={a:0,b:0,correct:0,choices:[],answered:false};
function newLearningRound(){spark.a=1+Math.floor(Math.random()*9);spark.b=1+Math.floor(Math.random()*9);spark.correct=spark.a+spark.b;let wrong=spark.correct+(Math.random()<.5?-1:1)*(1+Math.floor(Math.random()*3));if(wrong<0)wrong+=5;spark.choices=Math.random()<.5?[spark.correct,wrong]:[wrong,spark.correct];spark.answered=false;playerState.targetX=480;playerState.targetY=400;statusEl.textContent=(rtl?'حل: ':'Solve: ')+spark.a+' + '+spark.b;}
function choiceAt(p){if(p.y>245)return null;return p.x<480?0:1;}
function onLocalAction(p){const i=choiceAt(p);if(i===null||spark.answered)return;spark.answered=true;if(spark.choices[i]===spark.correct){playerState.score++;statusEl.textContent=rtl?'صحيح — تقدم محلي فقط':'Correct — local progress only';}else{statusEl.textContent=(rtl?'الإجابة الصحيحة: ':'Correct answer: ')+spark.correct;}setTimeout(newLearningRound,reduced?50:650);}
function updateLocalGame(dt){}
function drawLocalGame(){ctx.clearRect(0,0,960,540);ctx.fillStyle='#243646';ctx.fillRect(24,28,432,190);ctx.fillRect(504,28,432,190);ctx.fillStyle='#fff';ctx.font='bold 72px system-ui';ctx.textAlign='center';ctx.fillText(String(spark.choices[0]??''),240,150);ctx.fillText(String(spark.choices[1]??''),720,150);ctx.fillStyle='#8fe3ff';ctx.beginPath();ctx.arc(playerState.x,playerState.y,avatar.radius,0,Math.PI*2);ctx.fill();ctx.fillStyle='#071018';ctx.font='bold 16px system-ui';ctx.fillText(avatar.label,playerState.x,playerState.y+6);ctx.fillStyle='#fff';ctx.font='22px system-ui';ctx.fillText((rtl?'النقاط المحلية: ':'Local score: ')+playerState.score,480,505);}
function resetLocalGame(){playerState.score=0;playerState.round=1;newLearningRound();}
newLearningRound();
'''

RUSH = r'''
const rush={side:0,reps:0,streak:0,lastHit:performance.now(),target:{x:180,y:150,r:72}};
function nextFitnessTarget(){rush.side=1-rush.side;rush.target.x=rush.side?780:180;rush.target.y=120+Math.random()*250;statusEl.textContent=(rtl?'تدريب لمس محلي — تكرارات: ':'Local touch drill — reps: ')+rush.reps;}
function onLocalAction(p){const d=Math.hypot(p.x-rush.target.x,p.y-rush.target.y);if(d<=rush.target.r+28){rush.reps++;playerState.score=rush.reps;rush.streak++;rush.lastHit=performance.now();nextFitnessTarget();}}
function updateLocalGame(dt){if(performance.now()-rush.lastHit>5000)rush.streak=0;}
function drawLocalGame(){ctx.clearRect(0,0,960,540);ctx.fillStyle='#2d4860';ctx.beginPath();ctx.arc(rush.target.x,rush.target.y,rush.target.r,0,Math.PI*2);ctx.fill();ctx.fillStyle='#fff';ctx.font='bold 25px system-ui';ctx.textAlign='center';ctx.fillText(rtl?'المس الهدف':'TOUCH TARGET',rush.target.x,rush.target.y+8);ctx.fillStyle='#8fe3ff';ctx.beginPath();ctx.arc(playerState.x,playerState.y,avatar.radius,0,Math.PI*2);ctx.fill();ctx.fillStyle='#071018';ctx.font='bold 16px system-ui';ctx.fillText(avatar.label,playerState.x,playerState.y+6);ctx.fillStyle='#fff';ctx.font='22px system-ui';ctx.fillText((rtl?'التكرارات المحلية: ':'Local reps: ')+rush.reps+'  '+(rtl?'السلسلة: ':'streak: ')+rush.streak,480,505);}
function resetLocalGame(){rush.reps=0;rush.streak=0;playerState.score=0;nextFitnessTarget();}
nextFitnessTarget();
'''

TAIL = r'''
window.addEventListener('resize',()=>{});
</script></body></html>
'''

def sha256(p:pathlib.Path)->str:
    h=hashlib.sha256();
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()

def main()->int:
    ap=argparse.ArgumentParser();ap.add_argument('root');ap.add_argument('--kind',choices=['spark','rush'],required=True);ap.add_argument('--evidence-out',required=True);a=ap.parse_args()
    root=pathlib.Path(a.root).resolve();
    candidates=sorted(root.rglob('android/app/src/main/assets/offline.html'))
    if len(candidates)!=1: raise SystemExit(f'expected one Android offline asset, found {len(candidates)}')
    out=candidates[0]; before=sha256(out); html=COMMON_HEAD+(SPARK if a.kind=='spark' else RUSH)+TAIL; out.write_text(html)
    after=sha256(out)
    ev=pathlib.Path(a.evidence_out);ev.write_text('\n'.join([
      'schema=thf-spark-rush-local-practice-overlay-v1',f'kind={a.kind}',f'offline_asset={out.relative_to(root).as_posix()}',f'offline_sha256_before={before}',f'offline_sha256_after={after}',
      'local_mode=true','touch_input=true','player_state=true','game_loop=true',f"domain_loop={'learning' if a.kind=='spark' else 'fitness_practice'}",
      'ranked_state_written=false','social_state_written=false','economy_state_written=false','fitness_evidence_written=false','network_required=false','candidate_only=true','canonical_archive_mutated=false','device_status=PENDING','final_status=NOT_FINAL',''])
    print(ev.read_text(),end='');return 0
if __name__=='__main__':sys.exit(main())
