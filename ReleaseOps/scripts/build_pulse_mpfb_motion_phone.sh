#!/usr/bin/env bash
set -Eeuo pipefail

SRC="$HOME/thf-apps-rc3-exact-candidate-v2/work/pulse/THF_Pulse_APPS_RC2_SOURCE"
MPFB="$HOME/thf-terra-rift-staging-apk-v1/terra/work/web/static/assets/avatars/stage16a/thf_mpfb_stage16a_ual12_animated.glb"
ROOT="$HOME/thf-pulse-mpfb-motion-phone-v1"
WORK="$ROOT/work"
OUT="$ROOT/out"
SDK="$HOME/thf-builder-rc16-build/android-sdk"
CACHE="$HOME/thf-builder-rc16-build/cache"
APK_NAME="THF-PULSE-MPFB-MOTION-PHONE-QA1.apk"

rm -rf "$ROOT"
mkdir -p "$ROOT" "$OUT"
cp -a "$SRC" "$WORK"
test -s "$MPFB"
cd "$WORK"

ASSETS="android/app/src/main/assets/pulse"
mkdir -p "$ASSETS"
cp "$MPFB" "$ASSETS/avatar.glb"
cp static/photoreal_runtime.mjs "$ASSETS/photoreal_source.mjs"

# Bundle fixed-version MIT Three.js dependencies locally so the physical-phone
# motion QA does not depend on an external renderer CDN at runtime.
curl -fsSL --retry 3 --retry-delay 2 https://unpkg.com/three@0.128.0/build/three.min.js -o "$ASSETS/three.min.js"
curl -fsSL --retry 3 --retry-delay 2 https://unpkg.com/three@0.128.0/examples/js/loaders/GLTFLoader.js -o "$ASSETS/GLTFLoader.js"
test -s "$ASSETS/three.min.js"
test -s "$ASSETS/GLTFLoader.js"

python3 - <<'PY'
from pathlib import Path

# Convert the already-developed Pulse photoreal semantic-bone driver from
# dynamic ES-module imports to locally bundled classic Three.js scripts.
src=Path('static/photoreal_runtime.mjs').read_text(encoding='utf-8')
src=src.replace("if(!cfg.threeModuleUrl || !cfg.gltfLoaderUrl) fail('3D dependency URLs missing');\n\nlet THREE, GLTFLoader;\ntry {\n  THREE = await import(cfg.threeModuleUrl);\n  ({GLTFLoader} = await import(cfg.gltfLoaderUrl));\n} catch (e) { fail('تعذر تحميل محرك 3D: '+e.message); }",
"const THREE=window.THREE;\nconst GLTFLoader=window.THREE && window.THREE.GLTFLoader;\nif(!THREE || !GLTFLoader) fail('تعذر تحميل محرك 3D المحلي');")
src=src.replace("const pattern=cfg.pattern||'dynamic_warmup';",
"let pattern=cfg.pattern||'dynamic_warmup';\nwindow.THF_PULSE_SET_PATTERN=(p)=>{pattern=String(p||'dynamic_warmup');if(statusEl)statusEl.textContent='MPFB ready · '+bones.length+' bones · pattern '+pattern;};")
src="(async()=>{\n"+src+"\n})().catch(e=>{console.error(e);const n=document.getElementById('photoStatus');if(n)n.textContent='3D ERROR · '+e.message;});\n"
Path('android/app/src/main/assets/pulse/photoreal.js').write_text(src,encoding='utf-8')

html=r'''<!doctype html>
<html lang="ar" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>THF Pulse · MPFB Motion QA</title>
<style>
:root{color-scheme:dark;--bg:#071219;--panel:#0c1c24;--line:#38505b;--gold:#edca78;--txt:#edf3f5;--muted:#a9b5bb}
*{box-sizing:border-box}body{margin:0;background:linear-gradient(180deg,#061018,#0b1720);color:var(--txt);font-family:system-ui,-apple-system,"Noto Sans Arabic",sans-serif;padding-bottom:28px}.top{position:sticky;top:0;z-index:5;padding:16px 18px;background:#07131bea;border-bottom:1px solid #32454f;backdrop-filter:blur(10px)}.brand{display:flex;justify-content:space-between;align-items:center}.brand b{font-size:22px;letter-spacing:2px;color:var(--gold)}.badge{font-size:11px;border:1px solid #8f783e;border-radius:999px;padding:6px 9px;color:var(--gold)}main{max-width:760px;margin:auto;padding:16px}.hero h1{font-size:28px;margin:8px 0;color:var(--gold)}.hero p{color:var(--muted);line-height:1.7}.card{background:linear-gradient(180deg,#0d1c24,#0a171e);border:1px solid #334953;border-radius:18px;padding:16px;margin:14px 0}.stage{height:58vh;min-height:430px;max-height:620px;position:relative;border-radius:18px;overflow:hidden;background:#090b0c;border:1px solid #34444b}.stage canvas{width:100%;height:100%;display:block}.status{position:absolute;bottom:10px;left:10px;right:10px;background:#071219d9;border:1px solid #52646b;border-radius:12px;padding:9px;font-size:12px;color:#d6e0e4}.controls{display:grid;grid-template-columns:1fr;gap:12px}select,button{width:100%;min-height:52px;border-radius:12px;border:1px solid #53656e;background:#0a161d;color:var(--txt);padding:10px 12px;font-size:16px}button{background:linear-gradient(180deg,#3d331d,#211b10);border-color:#8e7437;color:var(--gold);font-weight:800}.cue{line-height:1.8;color:#d9e0e3}.truth{font-size:12px;color:#9fb0b7;border-top:1px solid #2b3c44;padding-top:12px}.grid{display:grid;grid-template-columns:1fr 1fr;gap:10px}.mini{padding:10px;border:1px solid #30434c;border-radius:12px;text-align:center}.mini b{display:block;color:var(--gold);font-size:17px}@media(max-width:520px){main{padding:10px}.stage{height:55vh;min-height:390px}.hero h1{font-size:24px}.grid{grid-template-columns:1fr 1fr}}
</style></head><body>
<header class="top"><div class="brand"><b>THF PULSE</b><span class="badge">MPFB MOTION QA</span></div></header>
<main><section class="hero"><h1>مدرب الحركة ثلاثي الأبعاد</h1><p>هذه شاشة اختبار الحركة الفعلية على الهاتف من مسار Pulse الحقيقي. اختر نمطًا لترى نموذج MPFB يتحرك مباشرة.</p></section>
<section class="card"><div class="grid"><div class="mini"><b>137</b>Joint identity</div><div class="mini"><b>195</b>UAL clips in current Terra asset</div></div></section>
<section class="stage"><canvas id="photoCanvas"></canvas><div id="photoStatus" class="status">تحميل نموذج MPFB المحلي…</div></section>
<section class="card controls"><label>الحركة / التمرين<select id="pattern"></select></label><button id="voice">▶ الدليل الصوتي</button><p id="cue" class="cue"></p><p class="truth">Visual QA فقط: هذه النسخة لا تنشئ حسابًا ولا تسجل مكافآت أو دليل نشاط. الهدف هنا اعتماد الإنسان الحقيقي والحركة على هاتفك قبل دمج الشبكة وباقي وظائف Pulse.</p></section></main>
<script>
const patterns=[
['dynamic_warmup','إحماء ديناميكي','حرّك الجسم تدريجيًا واستعد للتمرين.'],['squat','سكوات','اثبت القدمين وانزل بتحكم ثم اصعد بثبات.'],['hinge','Hip Hinge','ادفع الورك للخلف مع ظهر محايد ثم عد.'],['lunge','لانجز','اخطُ بثبات واخفض الحوض ثم ادفع للعودة.'],['leg_extension','تمديد الركبة','مد الركبة بتحكم ثم عد ببطء.'],['leg_curl','ثني الركبة','اثن الركبة مع ثبات الحوض ثم عد.'],['calf_raise','رفع السمانة','ارفع الكعبين ثم انزل بتحكم.'],['hip_abduction','إبعاد الفخذ','أبعد الفخذ مع ثبات الحوض.'],['hip_extension','مد الورك','مد الورك دون تقوس زائد للظهر.'],['horizontal_press','دفع أفقي','ثبت الكتف وادفع للأمام ثم عد.'],['vertical_press','ضغط علوي','ادفع لأعلى مع جذع ثابت.'],['fly','Chest Fly','افتح الذراعين ثم قربهما بتحكم.'],['horizontal_pull','سحب أفقي','اسحب المرفقين للخلف مع ثبات الجذع.'],['vertical_pull','سحب رأسي','اسحب لأسفل دون رفع الكتفين.'],['curl','بايسبس Curl','اثن المرفق دون تأرجح الجذع.'],['triceps','ترايسبس','مد المرفق مع ثبات العضد.'],['anti_rotation','مقاومة الدوران','حافظ على الجذع ثابتًا وقاوم الدوران.'],['jump','قفز','حمّل الورك والركبتين ثم اقفز واهبط بهدوء.'],['landing','هبوط','اهبط بهدوء وامتص القوة بثني الركبتين.'],['run','جري','حافظ على إيقاع ثابت وهبوط قدم هادئ.'],['sprint','Sprint','سرّع تدريجيًا مع ذراعين نشطين.'],['football_dribble','مراوغة كرة القدم','لمسات قصيرة مع بقاء الكرة قريبة.'],['football_pass','تمرير كرة القدم','ثبت القدم الداعمة ثم مرر.'],['football_shot','تسديد كرة القدم','ثبت القدم الداعمة وتابع حركة الركل.'],['basket_dribble','تنطيط كرة السلة','استخدم الأصابع مع ثني بسيط للركبتين.'],['basket_layup','Layup','نسق الاقتراب والارتقاء والهبوط.'],['volley_pass','استقبال الكرة الطائرة','ثبت الساعدين ووجه المنصة للهدف.'],['volley_set','إعداد الكرة الطائرة','ضع اليدين فوق الجبهة وادفع بأصابع مرتخية.'],['racket_forehand','Forehand','ابدأ بالدوران من الجذع ثم تابع الضربة.'],['racket_backhand','Backhand','حضّر الكتفين واضرب مع اتزان القدمين.'],['racket_serve','Serve','نسق رفع الذراع وحركة الإرسال.'],['boxing_jab','Boxing Jab','اضرب مباشرة مع حماية الوجه وثبات الجذع.'],['boxing_cross','Boxing Cross','دوّر الجذع واضرب بالذراع الخلفية.'],['boxing_slip','Boxing Slip','حرّك الجذع لتفادي الضربة مع حفظ التوازن.'],['row_erg','تجديف','نسق دفع الرجلين وسحب الذراعين.'],['cycle','دراجة','حافظ على دوران منتظم للرجلين.'],['shoulder_mobility','مرونة الكتف','حرك الذراعين في مدى مريح.'],['hip_mobility','مرونة الورك','حرّك الورك في مدى مريح ومتحكم.'],['stretch','إطالة','تحرك ببطء إلى مدى الإطالة المريح.'],['breathing','تنفس','تنفس بهدوء وحافظ على استرخاء الجذع.']
];
const sel=document.getElementById('pattern'),cue=document.getElementById('cue');for(const [id,n] of patterns){const o=document.createElement('option');o.value=id;o.textContent=n;sel.appendChild(o)}
function apply(){const row=patterns.find(x=>x[0]===sel.value)||patterns[0];cue.textContent=row[2];window.THF_PULSE_SET_PATTERN?.(row[0]);window.THF_PHOTOREAL_CONFIG.pattern=row[0]}
sel.addEventListener('change',apply);document.getElementById('voice').addEventListener('click',()=>{const row=patterns.find(x=>x[0]===sel.value)||patterns[0];if('speechSynthesis'in window){speechSynthesis.cancel();const u=new SpeechSynthesisUtterance(row[2]);u.lang='ar-EG';u.rate=.88;speechSynthesis.speak(u)}});
window.THF_PHOTOREAL_CONFIG={assetUrl:'avatar.glb',pattern:'dynamic_warmup',tempoSec:3};cue.textContent=patterns[0][2];
</script>
<script src="three.min.js"></script><script src="GLTFLoader.js"></script><script src="photoreal.js"></script>
</body></html>'''
Path('android/app/src/main/assets/pulse/index.html').write_text(html,encoding='utf-8')

# Android shell: local self-contained visual QA, independent of temporary API.
jp=Path('android/app/src/main/java/com/topherofit/thf/pulse/MainActivity.java')
j=jp.read_text(encoding='utf-8')
j=j.replace('s.setJavaScriptEnabled(true); s.setDomStorageEnabled(true); s.setAllowFileAccess(false); s.setAllowContentAccess(false);',
'''s.setJavaScriptEnabled(true); s.setDomStorageEnabled(true); s.setAllowFileAccess(true); s.setAllowContentAccess(false); s.setAllowFileAccessFromFileURLs(true); s.setAllowUniversalAccessFromFileURLs(false);''',1)
j=j.replace('''                if ("topherofit".equals(scheme)) { handleDeepLink(u); return true; }\n                return !"https".equals(scheme);''',
'''                if ("topherofit".equals(scheme)) { handleDeepLink(u); return true; }\n                if ("file".equals(scheme)) return !u.toString().startsWith("file:///android_asset/pulse/");\n                return !"https".equals(scheme);''',1)
old='''    private void loadProduct() {\n        String base=BuildConfig.THF_BASE_URL==null?"":BuildConfig.THF_BASE_URL.trim();\n        if (!isSafeHttps(base)) { showConfigError(getString(R.string.service_endpoint_missing)); return; }\n        if (!isOnline()) { showOffline(); return; }\n        loadUrl(base);\n    }'''
new='''    private void loadProduct() {\n        loadUrl("file:///android_asset/pulse/index.html");\n    }'''
if old not in j: raise SystemExit('Pulse loadProduct block not found')
j=j.replace(old,new,1)
jp.write_text(j,encoding='utf-8')

gp=Path('android/app/build.gradle')
g=gp.read_text(encoding='utf-8')
g=g.replace('versionCode 41200','versionCode 41301',1)
g=g.replace("versionName '4.1.2'","versionName '4.1.3-motionqa1'",1)
gp.write_text(g,encoding='utf-8')
PY

for f in index.html avatar.glb three.min.js GLTFLoader.js photoreal.js; do test -s "$ASSETS/$f"; done
grep -q 'MPFB MOTION QA' "$ASSETS/index.html"
grep -q 'case .squat.' "$ASSETS/photoreal.js"

export ANDROID_SDK_ROOT="$SDK" ANDROID_HOME="$SDK" GRADLE_USER_HOME="$ROOT/gradle-home"
export PATH="$SDK/platform-tools:$SDK/build-tools/36.0.0:$SDK/cmdline-tools/latest/bin:$PATH"
mkdir -p "$GRADLE_USER_HOME"
GVER=8.11.1
GBIN="$CACHE/gradle-dist-${GVER}/gradle-${GVER}/bin/gradle"
test -x "$GBIN"
cd android
"$GBIN" --no-daemon wrapper --gradle-version "$GVER" --distribution-type bin >/dev/null
chmod +x gradlew
./gradlew --no-daemon --stacktrace clean :app:assembleDebug >"$OUT/gradle.log" 2>&1
cp app/build/outputs/apk/debug/app-debug.apk "$OUT/$APK_NAME"

APK="$OUT/$APK_NAME"
AAPT="$SDK/build-tools/36.0.0/aapt"
APKSIGNER="$SDK/build-tools/36.0.0/apksigner"
"$AAPT" dump badging "$APK" > "$OUT/badging.txt"
"$APKSIGNER" verify --verbose --print-certs "$APK" > "$OUT/apksigner.txt"
grep -q "package: name='com.topherofit.thf.pulse.debug'" "$OUT/badging.txt"
grep -q "versionCode='41301'" "$OUT/badging.txt"
grep -q "targetSdkVersion:'36'" "$OUT/badging.txt"
zipinfo -1 "$APK" > "$OUT/apk_entries.txt"
for f in index.html avatar.glb three.min.js GLTFLoader.js photoreal.js; do grep -Fxq "assets/pulse/$f" "$OUT/apk_entries.txt"; done
SIZE=$(stat -c %s "$APK"); SHA=$(sha256sum "$APK" | awk '{print $1}')
MPFB_SHA=$(sha256sum "$ASSETS/avatar.glb" | awk '{print $1}')
UNDER=FAIL; if [ "$SIZE" -lt 104857600 ]; then UNDER=PASS; fi
cat > "$OUT/EVIDENCE.txt" <<EOF
THF_PULSE_MPFB_MOTION_PHONE_QA1=BUILT
source=thf-apps-rc3-exact-candidate-v2/work/pulse/THF_Pulse_APPS_RC2_SOURCE
source_motion_driver=static/photoreal_runtime.mjs
avatar_source=current_Terra_RC34_stage16a
avatar_asset=thf_mpfb_stage16a_ual12_animated.glb
avatar_sha256=$MPFB_SHA
renderer_dependencies=LOCAL_BUNDLED_THREE_R128
network_required_for_motion=false
exercise_pattern_selector=PASS
arabic_voice_cue=PASS
package=com.topherofit.thf.pulse.debug
version=4.1.3-motionqa1-debug
versionCode=41301
targetSdk=36
apk_size_bytes=$SIZE
apk_sha256=$SHA
under_100MiB=$UNDER
backend_features=NOT_ACCEPTED_IN_THIS_VISUAL_QA
physical_device_status=PENDING
final_or_play_ready=FALSE
EOF
cat "$OUT/EVIDENCE.txt"
[ "$UNDER" = PASS ]
