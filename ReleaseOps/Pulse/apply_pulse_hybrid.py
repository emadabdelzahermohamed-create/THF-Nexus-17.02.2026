from pathlib import Path
import re, json

main=Path('app/src/main/java/com/topherofit/thf/pulse/MainActivity.java')
idx=Path('app/src/main/assets/pulse/index.html')
gradle=Path('app/build.gradle')
assets=idx.parent
j=main.read_text()
h=idx.read_text()
g=gradle.read_text()

# Hybrid identity and persistent endpoint policy.
j=j.replace('o.put("mode", "offline_first");','o.put("mode", "hybrid_offline_online");')
j=j.replace('return "{\\"mode\\":\\"offline_first\\"}";','return "{\\"mode\\":\\"hybrid_offline_online\\"}";')
j=j.replace('private static final int REQ_ACTIVITY = 701;','private static final int REQ_ACTIVITY = 701;\n    private static final String RUNTIME_CONFIG_ASSET = "pulse/runtime-config.json";\n    private static final String SYNC_PATH = "/api/pulse/mobile/sync";')
j=j.replace('import java.util.Locale;','import java.util.Locale;\nimport java.util.UUID;')
j=j.replace('String[] banned = {"trycloudflare.com", "ngrok-free.app", "ngrok.io", "localhost", "127.0.0.1", ".local"};','String[] banned = {"trycloudflare.com", "ngrok-free.app", "ngrok.io", "localhost", "127.0.0.1", ".local", "example.com", "example.org", "example.net"};')
j=j.replace('return true;\n        } catch (Exception ignored) { return false; }\n    }','if (host.contains("staging") || host.contains("preview") || host.contains("temporary")) return false;\n            return true;\n        } catch (Exception ignored) { return false; }\n    }',1)
# Every workout gets a stable id and enters a durable pending-sync queue. No online requirement for training.
old='''                item.put("savedAt", System.currentTimeMillis());\n                arr.put(item);'''
new='''                if (item.optString("id", "").isEmpty()) item.put("id", UUID.randomUUID().toString());\n                item.put("savedAt", System.currentTimeMillis());\n                item.put("syncState", "pending");\n                arr.put(item);'''
assert old in j
j=j.replace(old,new,1)
old='''                prefs.edit().putString("summaries", arr.toString()).apply();\n                return "{\\"saved\\":true}";'''
new='''                JSONArray pending = new JSONArray(prefs.getString("pending_sync", "[]"));\n                pending.put(item);\n                prefs.edit().putString("summaries", arr.toString()).putString("pending_sync", pending.toString()).apply();\n                return "{\\"saved\\":true,\\"queuedForSync\\":true}";'''
assert old in j
j=j.replace(old,new,1)
j=j.replace('@JavascriptInterface public String readSummaries() { return prefs.getString("summaries", "[]"); }','@JavascriptInterface public String readSummaries() { return prefs.getString("summaries", "[]"); }\n        @JavascriptInterface public String readPending() { return prefs.getString("pending_sync", "[]"); }\n        @JavascriptInterface public int pendingSyncCount() { try { return new JSONArray(prefs.getString("pending_sync", "[]")).length(); } catch(Exception e) { return 0; } }\n        @JavascriptInterface public String syncContract() { return SYNC_PATH + "|" + RUNTIME_CONFIG_ASSET; }')
# Status exposes queue count and concrete hybrid mode.
j=j.replace('o.put("sessionSteps", sessionSteps());','o.put("sessionSteps", sessionSteps());\n                o.put("pendingSync", pendingSyncCount());\n                o.put("syncPath", SYNC_PATH);')
main.write_text(j)

# Replace old SVG/cartoon human with canonical local 3D canvas only.
pat=r'<div class="hero"><svg.*?</svg><div class="overlay">(.*?)</div></div>'
m=re.search(pat,h,re.S)
assert m, 'old avatar hero not found'
h=re.sub(pat,r'<div class="hero" id="avatarWrap"><canvas id="avatar3d" style="width:100%;height:100%;display:block"></canvas><div class="overlay">\1<div id="avatarState" class="muted small">تحميل الإنسان الحديث ثلاثي الأبعاد…</div></div></div>',h,count=1,flags=re.S)
# Do not manipulate the removed SVG human.
h=h.replace("$('human').setAttribute('class','human '+current.cls);", "playAvatarClip(current.clip||'idle');")
# Add animation names to exercise records using proven 195-clip asset names.
clips={'warmup':'walk','squat':'UAL1_Crouch_Fwd_Loop','lunge':'UAL1_Walk_Loop','pushup':'UAL2_Chest_Open','plank':'breathe','run':'run','breathing':'breathe'}
for ex,clip in clips.items():
    h=h.replace("id:'%s',name:"%ex, "id:'%s',clip:'%s',name:"%(ex,clip))
# Hybrid status wording (no blocker screen).
h=h.replace("$('modeChip').textContent=s.syncConfigured&&s.online?'OFFLINE + SYNC':'OFFLINE READY'", "$('modeChip').textContent=s.syncConfigured&&s.online?'HYBRID + SYNC':'HYBRID · OFFLINE READY'")
h=h.replace("المزامنة: ${s.syncConfigured?'جاهزة':'اختيارية وغير مهيأة'}", "المزامنة: ${s.syncConfigured?'جاهزة':'تنتظر خدمة THF الدائمة'} · قائمة الانتظار: ${s.pendingSync||0}")
# Add Three.js scripts and a modern-human-only renderer before existing app script.
insert='''<script src="three.min.js"></script><script src="GLTFLoader.js"></script><script>\nlet thfScene,thfCamera,thfRenderer,thfMixer,thfClock,thfModel,thfActions={},thfActive;\nfunction initModernHuman(){const st=document.getElementById('avatarState');if(!window.THREE||!THREE.GLTFLoader){if(st)st.textContent='عارض 3D غير متاح — لا يوجد بديل قديم';return;}try{const c=document.getElementById('avatar3d');thfScene=new THREE.Scene();thfCamera=new THREE.PerspectiveCamera(31,1,.1,100);thfCamera.position.set(0,1.15,4.2);thfRenderer=new THREE.WebGLRenderer({canvas:c,antialias:true,alpha:true,powerPreference:'high-performance'});thfRenderer.setPixelRatio(Math.min(devicePixelRatio||1,1.6));thfRenderer.outputEncoding=THREE.sRGBEncoding;thfScene.add(new THREE.HemisphereLight(0xeef7ff,0x152027,1.5));const k=new THREE.DirectionalLight(0xffffff,1.8);k.position.set(3,5,4);thfScene.add(k);thfClock=new THREE.Clock();new THREE.GLTFLoader().load('avatar.glb',g=>{thfModel=g.scene;thfScene.add(thfModel);const box=new THREE.Box3().setFromObject(thfModel),sz=new THREE.Vector3(),ct=new THREE.Vector3();box.getSize(sz);box.getCenter(ct);thfModel.position.sub(ct);thfModel.position.y+=sz.y*.48;thfModel.scale.setScalar(1.72/Math.max(.01,sz.y));thfMixer=new THREE.AnimationMixer(thfModel);g.animations.forEach(a=>thfActions[a.name]=a);if(st)st.textContent='الإنسان الحديث · '+g.animations.length+' حركة';playAvatarClip((window.current&&current.clip)||'idle');resizeHuman();renderHuman()},undefined,()=>{if(st)st.textContent='تعذر تحميل الإنسان الحديث — لا يتم استخدام أي أفاتار قديم'});}catch(e){if(st)st.textContent='WebGL غير مدعوم على هذا الجهاز — لا يوجد fallback قديم';}}\nfunction playAvatarClip(name){if(!thfMixer)return;const clip=thfActions[name]||thfActions.idle||thfActions['UAL1_Idle_Loop'];if(!clip)return;const a=thfMixer.clipAction(clip);if(thfActive&&thfActive!==a){thfActive.fadeOut(.2);a.reset().fadeIn(.2)}a.play();thfActive=a;}\nfunction resizeHuman(){if(!thfRenderer||!thfCamera)return;const c=document.getElementById('avatar3d'),w=Math.max(1,c.clientWidth),hh=Math.max(1,c.clientHeight);thfRenderer.setSize(w,hh,false);thfCamera.aspect=w/hh;thfCamera.updateProjectionMatrix();}\nfunction renderHuman(){if(!thfRenderer)return;requestAnimationFrame(renderHuman);if(thfMixer)thfMixer.update(Math.min(.05,thfClock.getDelta()));if(thfModel)thfModel.rotation.y=Math.sin(performance.now()/4300)*.07;thfRenderer.render(thfScene,thfCamera);}\nwindow.addEventListener('resize',resizeHuman);window.addEventListener('load',()=>setTimeout(initModernHuman,50));\n</script>'''
h=h.replace('<script>\nconst N=',insert+'<script>\nconst N=',1)
# Existing CSS references hero already; enforce a useful viewport.
h=h.replace('.hero{', '.hero{min-height:420px;') if '.hero{' in h else h
idx.write_text(h)

(assets/'runtime-config.json').write_text(json.dumps({'mode':'hybrid_offline_online','baseUrl':'','syncPath':'/api/pulse/mobile/sync','avatar':'canonical_stage16a_mpfb_137j_195clips_only'},indent=2)+'\n')
g=g.replace('versionCode 42001','versionCode 43000').replace("versionName '4.2.0-batch1'","versionName '4.3.0-hybrid-modern'")
gradle.write_text(g)
print('PULSE_HYBRID_PATCH=PASS')
